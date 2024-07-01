
from django.urls import path,include
from App.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/',include('App.urls'))
]
