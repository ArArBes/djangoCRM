from django.urls import path
from .views import RegisterUserView, CreateCompanyView, GetCompanyView, LoginView
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/',LoginView.as_view(), name='login'),
    path('create-company/', CreateCompanyView.as_view(), name='create_company'),
    path('show-company/', GetCompanyView.as_view(), name='get_company'),
]
