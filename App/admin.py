# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User,Event,Trashdata,Notification,FeedBack
from django import forms


class CustomUserCreationForm(UserCreationForm):
    mobile_number = forms.CharField(max_length=13)
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    citizenship = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mobile_number'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['citizenship'].required = True

class CustomUserChangeForm(UserChangeForm):
    mobile_number = forms.CharField(max_length=13)
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    citizenship = forms.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mobile_number'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['citizenship'].required = True

        
        
# Register your models here.
class UserModelAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'citizenship', 'role', 'latitude', 'longitude', 'mobile_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2','mobile_number','latitude','longitude','citizenship'),
        }),
    )
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    filter_horizontal = ()




# Now register the new UserAdmin...
admin.site.register(User, UserModelAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')
    
@admin.register(Trashdata)
class TrashAdmin(admin.ModelAdmin):
    list_display=('id','location','trash','timestamp')
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sent_at', 'lati', 'longi')
    
@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display=('id','user','feedback_msg','rating')
    
