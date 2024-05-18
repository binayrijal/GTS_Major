from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterModelSerializer,LoginModelSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken



#generate token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



# Create your views here.
class RegisterModelView(APIView):
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