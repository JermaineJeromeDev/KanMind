"""
Admin configuration for the auth_app.
Customizes the Django admin interface for the CustomUser model.
"""

# 2. Third-party (Django)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# 3. Local
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for managing CustomUser accounts.
    Includes additional fields like fullname and email in the fieldsets.
    """
    model = CustomUser
    list_display = ["email", "username", "fullname", "is_staff"]
    
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {"fields": ("fullname",)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Fields", {"fields": ("fullname", "email")}),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Optional: Customize the form if needed.
        Ensures a clean code structure under 14 lines.
        """
        return super().get_form(request, obj, **kwargs)
