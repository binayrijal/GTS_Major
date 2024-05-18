from django.urls import path,include
from . import views

urlpatterns = [
    path('register_user/',views.RegisterModelView.as_view(),name='register_user'),
    path('login_user/',views.LoginModelView.as_view(),name='login_user'),
    path('profile/',views.ProfileModelView.as_view(),name='profile'),
]
