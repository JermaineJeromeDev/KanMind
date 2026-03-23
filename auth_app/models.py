"""
Models for the auth_app.
Defines the custom user model used for authentication.
"""

# 2. Third-party (Django)
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model that uses email as the unique identifier.
    Includes additional fields for full name.
    """

    fullname = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "fullname"]

    class Meta:
        """
        Meta options for the CustomUser model.
        """
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["email"]

    def __str__(self):
        """
        Returns the email representation of the user.
        """
        return str(self.email)
