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
    path('generate-pdf/',views.GeneratePDFAPIView.as_view(), name='generate_pdf'),
    path('trashdata/', views.TrashDataView.as_view(), name='trash-data'),
    path('update-location/', views.update_location, name='update_location'),
    path('trashdata/graph/', views.TrashDataGraphView.as_view(), name='trashdata-graph'), 
    path('feedback/', views.FeedBackListCreateView.as_view(), name='feedback-list-create'),
    path('feedback/<int:pk>/', views.FeedBackDetailView.as_view(), name='feedback-detail'),
    path('initiate/',views.initiatekhalti,name='initiate'),
    path('verifykhalti/',views.verifykhalti,name='verifykhalti'),
    path('send_email_to_all_users/',views.send_email_to_all_users,name='send_email_to_all_users'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('verify_payment/',views.verify_payment,name='verify_payment'),
    path('Verified/',views.Verified,name="Verified")
    
]
