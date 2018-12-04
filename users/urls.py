from django.urls import path
from . import views
from .models import CustomUser

urlpatterns = [
    path('signup/<user>/', views.sign_up, name='signup'),
    path('validate_token/', views.validate_token, name='validate_token'),
]