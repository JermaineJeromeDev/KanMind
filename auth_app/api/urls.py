"""
URL mapping for the auth_app.
Defines endpoints for registration, login, and email verification.
"""

# 2. Third-party (Django)
from django.urls import path

# 3. Local
from .views import EmailCheckView, LoginView, RegistrationView


urlpatterns = [
    path(
        'registration/', 
        RegistrationView.as_view(), 
        name='user-registration'
    ),
    path(
        'login/', 
        LoginView.as_view(), 
        name='user-login'
    ),
    path(
        'email-check/', 
        EmailCheckView.as_view(), 
        name='email-check'
    ),
]