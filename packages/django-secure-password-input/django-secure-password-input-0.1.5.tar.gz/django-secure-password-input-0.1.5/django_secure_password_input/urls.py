from django.urls import path
from . import views

urlpatterns = [
    path('getPublicKey', views.getPublicKey, name="django_secure_password_input.getPublicKey"),
]
