from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, name, citizenship=None, role=None, latitude=None, longitude=None, mobile_number=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, name, citizenship, role, latitude, longitude, mobile number, and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        
        if not name:
            raise ValueError("Users must have a name")

        email = self.normalize_email(email)
        
        if role is None:
            role = 'User'
            
        user = self.model(
            email=email,
            name=name,
            citizenship=citizenship,
            role=role,
            latitude=latitude,
            longitude=longitude,
            mobile_number=mobile_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None,mobile_number=None, **extra_fields):
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
            name,
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
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    citizenship = models.CharField(max_length=10, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    mobile_number = models.CharField(max_length=13, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return self.is_superuser





class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title
