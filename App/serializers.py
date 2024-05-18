from rest_framework import serializers
from django.contrib.auth import get_user_model


User=get_user_model()



class RegisterModelSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    role = serializers.CharField(write_only=True, required=False)
    class Meta:
        model= User
        fields=['email','name','role','password','password2','mobile_number','citizenship','latitude','longitude']
        extra_kwargs={
            'password':{'write_only':True},
        }


    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.pop('password2')
        if password != password2:
           raise serializers.ValidationError('password and password2  need to match') 
       
        
        return attrs
    
    def create(self, validated_data):
        role = validated_data.pop('role', 'User')  # Get role from validated_data, default to 'User' if not provided
        validated_data['role'] = role  # Include role in the validated data
        return User.objects.create_user(**validated_data)
    
    
class LoginModelSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model= User
        fields= ['email','password']