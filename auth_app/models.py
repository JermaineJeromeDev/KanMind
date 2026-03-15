from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "fullname"]

    def __str__(self):
        return self.email
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
