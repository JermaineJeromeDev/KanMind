"""
Admin configuration for the kanban_app.
Registers Board, Task, and Comment models for the Django admin interface.
"""

# 2. Third-party (Django)
from django.contrib import admin

# 3. Local
from .models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Board model.
    """
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "owner__email")
    list_filter = ("created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Task model.
    """
    list_display = ("title", "board", "status", "priority", "due_date")
    search_fields = ("title", "board__title")
    list_filter = ("status", "priority", "due_date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Comment model.
    """
    list_display = ("author", "task", "created_at")
    search_fields = ("content", "author__email")
    list_filter = ("created_at",)
