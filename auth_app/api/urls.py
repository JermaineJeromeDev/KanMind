from django.urls import path
from .views import LoginView, RegistrationView, EmailCheckView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]