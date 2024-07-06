from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.html import escape
from .utils import Util
from .models import Event,Trashdata,FeedBack


User=get_user_model()



class RegisterModelSerializer(serializers.ModelSerializer):
    password2=serializers.CharField()
    class Meta:
        model= User
        fields=['email','full_name','role','password','password2','mobile_number','citizenship','latitude','longitude']
        extra_kwargs={
            'password':{'write_only':True},
            'password2':{'write_only':True}
        }


    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.pop('password2')
        if password != password2:
           raise serializers.ValidationError('password and password2  need to match') 
       
        citizenship = attrs.get('citizenship')
        mobile_number = attrs.get('mobile_number')
        if citizenship and User.objects.filter(citizenship=citizenship).exists():
           
             raise serializers.ValidationError('citizenship already exist') 
        if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
            
             raise serializers.ValidationError('mobile_number already exist ')
        if mobile_number and len(mobile_number)!=10:
            raise serializers.ValidationError('mobile_number must be 10 digit')
        if citizenship and len(citizenship)!=16:
            raise serializers.ValidationError('citizenship must be 16 digit')
            
        
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
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Check if email exists
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Email does not exist.")

            # Check if password matches
            if password and not user.check_password(password):
                raise serializers.ValidationError("Password does not match.")

        return attrs
        
    
        
class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id','email','full_name','latitude','longitude','mobile_number','role','citizenship']
        
    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.citizenship = validated_data.get('citizenship', instance.citizenship)
        instance.mobile_number = validated_data.get('mobile_number', instance.mobile_number)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
        
class PasswordChangeSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']
    

    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        user=self.context.get('user')
        if password!=password2:
            raise serializers.ValidationError('password and password2 must match for change password')
        user.set_password(password) 
        user.save()  
        return attrs
    
class SendMailPasswordResetSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        fields=['email']

    def validate(self, attrs):
        email=attrs.get('email')
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            uid=urlsafe_base64_encode(force_bytes(user.id))
            print('UID',uid)
            token=PasswordResetTokenGenerator().make_token(user)
            print('Password Reset token',token)
            link='http://localhost:3000/password-reset/'+uid+'/'+token
            print('Reset password Send Mail  Link',link)
            link = escape(link)
            body = f'Click the following link to reset your password: {link}'
            # reset_url = reverse('password-reset', kwargs={'uid': uid, 'token': token})
            # link = self.context['request'].build_absolute_uri(reset_url)
            # body = f'Click the following link to reset your password: <a href="{link}">Reset Password</a>'
            #mail send 
            data={
                'subject':'This email is send for reset password',
                'body':body,
                'to_email':user.email
            }
            Util.send_mail(data)
        else:
            raise serializers.ValidationError('user doesnot exist with that email')

        return attrs


class DoPasswordResetSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']
    

    def validate(self, attrs):
        try:
         password=attrs.get('password')
         password2=attrs.get('password2')
         uid=self.context.get('uid')
         token=self.context.get('token')
         if password!=password2:
             raise serializers.ValidationError('password and password2 must match for change password')
         id=smart_str(urlsafe_base64_decode(uid))
         user=User.objects.get(id=id)
         if not PasswordResetTokenGenerator().check_token(user,token):
             raise serializers.ValidationError('token is expird or invalid token')

         user.set_password(password) 
         user.save()   
         return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise serializers.ValidationError('token is expired or invalid token')
        

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_time', 'end_time']       
           

class TrashDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trashdata
        fields = ['location', 'trash','timestamp']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['trash'] is not None:
            representation['trash'] = f"{representation['trash']}%"
        return representation


    
class LocationSerializer(serializers.Serializer):
    lati = serializers.FloatField()
    longi = serializers.FloatField()

    def validate_lati(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longi(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value
    


class FeedBackSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    feedback_msg = serializers.CharField(max_length=200)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    name=serializers.ReadOnlyField(source='user.full_name')
    
    class Meta:
        model = FeedBack
        fields = ['user', 'feedback_msg', 'rating','full_name']
        read_only_fields = ['user', 'full_name']

    def create(self, validated_data):
        return FeedBack.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.feedback_msg = validated_data.get('feedback_msg', instance.feedback_msg)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance
        
    