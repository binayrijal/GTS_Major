from django.urls import path,include
from . import views

urlpatterns = [
    path('register_user/',views.RegisterModelView.as_view(),name='register_user'),
    path('login_user/',views.LoginModelView.as_view(),name='login_user'),
    path('profile/',views.ProfileModelView.as_view(),name='profile'),
    path('changepassword/',views.PasswordChangeView.as_view(),name='changepassword'),
    path('send-mail-reset-password/',views.SendMailPasswordResetView.as_view(),name='send-mail-reset-password'),
    path('password-reset/<uid>/<token>/',views.DoPasswordResetView.as_view(),name='password-reset'),
    path('schedule/', views.EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedule'),
    path('schedule/<int:pk>/', views.EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='schedule'),
]
