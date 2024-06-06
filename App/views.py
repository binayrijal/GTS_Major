import io
import matplotlib
matplotlib.use('agg')  # Set the backend to 'agg' before importing pyplot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterModelSerializer,LoginModelSerializer,ProfileModelSerializer,PasswordChangeSerializer,SendMailPasswordResetSerializer,DoPasswordResetSerializer,EventSerializer,TrashDataSerializer,LocationSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .renderer import UserRenderer
from .models import Event,Trashdata,Notification
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser, SAFE_METHODS
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table
from io import BytesIO
from .firebase_config import initialize_firebase
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from geopy.distance import geodesic
from django.contrib.auth import get_user_model
from django.conf import settings
import json
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter

User=get_user_model()








#generate token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



# Create your views here.
class RegisterModelView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer=RegisterModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Registration successfull'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        
class LoginModelView(APIView):
    def post(self,request,format=None):
        serializer=LoginModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
         email=serializer.data.get('email')
         password=serializer.data.get('password')
         
         user=authenticate(email=email,password=password)
         if user is not None:
            token=get_tokens_for_user(user)
            return Response({'token':token,'msg':'login successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ProfileModelView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def get(self,request,format=None):
        serializer=ProfileModelSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

class PasswordChangeView(APIView):
    renderer_classes=[UserRenderer]
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        serializer=PasswordChangeSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'password changed successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class SendMailPasswordResetView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer=SendMailPasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Email send successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class DoPasswordResetView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,uid,token,format=None):
        serializer=DoPasswordResetSerializer(data=request.data,context={
            'uid':uid,
            'token':token
        })
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'password reset successfully'})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit or delete objects.
    """

    def has_permission(self, request, view):
        # Allow read-only permissions to authenticated users
        if request.user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        # Allow write permissions only to admin users
        return request.user.is_staff

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            # Allow all authenticated users to list and retrieve events
            permission_classes = [permissions.IsAuthenticated]
        else:
            # For all other actions, use the IsAdminOrReadOnly permission
            permission_classes = [IsAdminOrReadOnly]
        return [permission() for permission in permission_classes]
    

class GeneratePDFAPIView(APIView):
    
    def get(self, request):
        # Fetch data for the schedule
        events = Event.objects.all()
        
        # Serialize the data
        serializer = EventSerializer(events, many=True)
        serialized_data = serializer.data

        # Create a buffer to hold the PDF content
        buffer = BytesIO()

        # Create a PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Create a table to display schedule data
        data = [['ID', 'Title', 'Description', 'Start Time', 'End Time']]
        for event in serialized_data:
            data.append([
                str(event['id']),
                event['title'],
                event['description'],
                str(event['start_time']),
                str(event['end_time'])
            ])

        # Create the table and style
        table = Table(data)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ])
        elements.append(table)

        # Build the PDF document
        doc.build(elements)

        # Close the buffer and get the PDF content
        pdf = buffer.getvalue()
        buffer.close()

        # Create an HTTP response with PDF content
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="schedule_report.pdf"'
        return response
    

def firebaseData(request):
    # Create a Firebase Realtime Database reference
    database = initialize_firebase() 
    location=database.child('TrashData').child('location').get().val()
    trash=database.child('TrashData').child('trash').get().val()
    
    trash_data = Trashdata(location=location, trash=trash)
    trash_data.save()

    # Serialize the saved data
    serializer = TrashDataSerializer(trash_data)
    
    return Response(serializer.data)

class TrashDataView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Ensure the request data is a dictionary
            if isinstance(request.data, bytes):
                data = json.loads(request.data.decode('utf-8'))
            else:
                data = request.data
            
            # Deserialize the data
            serializer = TrashDataSerializer(data=data)
            
            # Validate and save the data
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception or print it
            print(f"Exception occurred: {e}")
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#generate graph for trash data
class TrashDataGraphView(APIView):
    def get(self, request, *args, **kwargs):
        # try:
        #     # Retrieve all trash data from the database
        #     trash_data = Trashdata.objects.all().order_by('timestamp')
        #     if not trash_data:
        #         return Response({"error": "No data found"}, status=status.HTTP_404_NOT_FOUND)

        #     # Serialize the data
        #     serializer = TrashDataSerializer(trash_data, many=True)
        #     data = serializer.data

        #     # Extract timestamps and values
        #     timestamps = [item['timestamp'] for item in data]
        #     values = [item['trash'] for item in data]

        #     # Generate the graph
        #     fig, ax = plt.subplots()
        #     ax.plot(timestamps, values, label='Trash Data')
        #     ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        #     plt.xlabel('Time')
        #     plt.ylabel('Trash Data')
        #     plt.title('Trash Data Over Time')

        #     # Highlight peaks
        #     max_value = max(values)
        #     peak_indices = [i for i, value in enumerate(values) if value == max_value]
        #     for idx in peak_indices:
        #         plt.plot(timestamps[idx], values[idx], 'ro')

        #     # Format the x-axis to show date-time
        #     ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
        #     plt.gcf().autofmt_xdate()

        #     # Save the plot to a BytesIO object
        #     buf = io.BytesIO()
        #     plt.savefig(buf, format='png')
        #     plt.close(fig)
        #     buf.seek(0)

        #     # Return the graph as a response
        #     return HttpResponse(buf, content_type='image/png')
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            # Retrieve all trash data from the database
            trash_data = Trashdata.objects.all().order_by('timestamp')
            if not trash_data:
                return Response({"error": "No data found"}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the data
            
            serializer = TrashDataSerializer(trash_data, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_location(request):
    if request.data is None:
        return Response({'error': 'Request data is missing'}, status=400)
    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        lati = serializer.validated_data['lati']
        longi = serializer.validated_data['longi']

        notified_users = []
        for user in User.objects.exclude(latitude__isnull=True, longitude__isnull=True):
            user_location = (user.latitude, user.longitude)
            truck_location = (lati, longi)
            dis=geodesic(truck_location, user_location).km
            print(dis,user.email)
            if dis <= 1:
                if not Notification.objects.filter(user=user, sent_at__date=timezone.now().date()).exists():
                    send_mail(
                        'Truck Near You',
                        f'The truck is currently at latitude: {lati}, longitude: {longi}.',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    Notification.objects.create(user=user, lati=user.latitude, longi=user.longitude)
                    notified_users.append(user.email)

        return Response({'status': 'success', 'notified_users': notified_users})
    else:
        return Response(serializer.errors, status=400) 
    