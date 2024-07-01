# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User,Event,Trashdata,Notification,FeedBack
from django import forms
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum


class MyAdminSite(admin.AdminSite):
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('trashdata_chart/', self.admin_view(self.trashdata_chart_view), name='trashdata_chart')
        ]
        return custom_urls + urls

    def trashdata_chart_view(self, request):
        if not request.user.is_superuser:
            self.message_user(request, "You do not have permission to view this page.", level="error")
            return TemplateResponse(request, "admin/permission_denied.html")
        
        data = Trashdata.objects.order_by('timestamp').values('timestamp').annotate(total_trash=Sum('trash'))
        
        timestamps = [item['timestamp'].strftime("%Y-%m-%d") for item in data]
        trash_values = [item['total_trash'] for item in data]
        
        location_data = Trashdata.objects.values('location').annotate(total_trash=Sum('trash'))
        locations = [item['location'] for item in location_data]
        trash_values_by_location = [item['total_trash'] for item in location_data]
        
        context = dict(
            self.each_context(request),
            data={
                'timestamps': timestamps,
                'trash_values': trash_values,
                'locations': locations,
                'trash_values_by_location': trash_values_by_location
            }
        )
        return TemplateResponse(request, "admin/trashdata_chart.html", context)

admin_site = MyAdminSite()
# class MyAdminSite(admin.AdminSite):
#     index_template='admin/base_site.html'
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('trashdata_chart/', self.admin_view(self.trashdata_chart_view), name='trashdata_chart')
#         ]
#         return custom_urls + urls

#     def trashdata_chart_view(self, request):
#         if not request.user.is_superuser:
#             self.message_user(request, "You do not have permission to view this page.", level="error")
#             return TemplateResponse(request, "admin/permission_denied.html")
        
#         data = Trashdata.objects.order_by('timestamp').values('timestamp').annotate(total_trash=Sum('trash'))
        
#         timestamps = [item['timestamp'].strftime("%Y-%m-%d") for item in data]
#         trash_values = [item['total_trash'] for item in data]
        
#         location_data = Trashdata.objects.values('location').annotate(total_trash=Sum('trash'))
#         locations = [item['location'] for item in location_data]
#         trash_values_by_location = [item['total_trash'] for item in location_data]
        
#         context = dict(
#             self.each_context(request),
#             data={
#                 'timestamps': timestamps,
#                 'trash_values': trash_values,
#                 'locations': locations,
#                 'trash_values_by_location': trash_values_by_location
#             }
#         )
#         return TemplateResponse(request, "admin/trashdata_chart.html", context)

# admin_site = MyAdminSite()

# @admin.register(Trashdata)
# class TrashdataAdmin(admin.ModelAdmin):
#     change_list_template = "admin/change_list.html"

#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         return super().changelist_view(request, extra_context=extra_context)
    







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
admin_site.register(User, UserModelAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)


    
@admin.register(Event, site=admin_site)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time')
    
@admin.register(Trashdata, site=admin_site)
class TrashAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'trash', 'timestamp')
    
@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sent_at', 'lati', 'longi')
    
@admin.register(FeedBack, site=admin_site)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'feedback_msg', 'rating')
