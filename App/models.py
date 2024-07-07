from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid
from django.contrib.auth.models import BaseUserManager
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.urls import reverse
from django.conf import settings
from .tokens import account_activation_token


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, citizenship=None, role=None, latitude=None, longitude=None, mobile_number=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, name, citizenship, role, latitude, longitude, mobile number, and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        
        if not full_name:
            raise ValueError("Users must have a name")

        email = self.normalize_email(email)
        
        if role is None:
            role = 'User'
            
        user = self.model(
            email=email,
            full_name=full_name,
            citizenship=citizenship,
            role=role,
            latitude=latitude,
            longitude=longitude,
            mobile_number=mobile_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        
        # Generate and send confirmation email
        user.send_confirmation_email()
        return user

    def create_superuser(self, email, full_name, password=None,mobile_number=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, name, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            email,
            full_name,
            password=password,
            role='Officer',
            mobile_number=mobile_number,
            **extra_fields
        )

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    citizenship = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    mobile_number = models.CharField(max_length=13, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return self.is_superuser


    def send_confirmation_email(self):
            domain = '127.0.0.1:8000'
            uid = urlsafe_base64_encode(force_bytes(self.pk))
            token = account_activation_token.make_token(self)

            subject = 'Confirm Your Registration'
            confirmation_link = f'http://{domain}/api/confirm-registration/{uid}/{token}/'
            message = render_to_string('admin/confirmation_email.html',{
                'user': self,
                'domain': domain,
                'uid':uid,
                'token': token,
                'confirmation_link': confirmation_link,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [self.email])

    def generate_token(self):
            return get_random_string(length=32)


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title
    

class Trashdata(models.Model):
    location=models.CharField(max_length=150)
    trash=models.IntegerField(default=0)
    timestamp = models.DateField(auto_now_add=True)
    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    lati = models.FloatField()
    longi = models.FloatField()
    
class FeedBack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_msg=models.TextField()
    rating=models.IntegerField()
    



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_verified=models.BooleanField(default=False)
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_uuid = models.CharField(max_length=100, unique=True)
    product_code = models.CharField(max_length=100)
    product_service_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    success_url = models.URLField()
    failure_url = models.URLField()
    signed_field_names = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    ref_id = models.CharField(max_length=100, null=True, blank=True)  # Reference ID from eSewa
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
    