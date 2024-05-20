from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterModelSerializer,LoginModelSerializer,ProfileModelSerializer,PasswordChangeSerializer,SendMailPasswordResetSerializer,DoPasswordResetSerializer,EventSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .renderer import UserRenderer
from .models import Event
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser, SAFE_METHODS




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
    
    
# class IsAdminOrReadOnly(permissions.BasePermission):
#     """
#     Custom permission to only allow admins to edit or delete objects.
#     """

#     def has_permission(self, request, view):
#         # Allow read-only permissions to authenticated users
#         if request.user.is_authenticated:
#             return request.method in SAFE_METHODS
#         return False
    
#     def has_object_permission(self, request, view, obj):
#         # Allow write permissions only to admin users
#         return request.user.is_staff
    

# class EventViewSet(viewsets.ModelViewSet):
#     queryset = Event.objects.all()
#     serializer_class = EventSerializer
#     permission_classes = [IsAdminOrReadOnly]

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