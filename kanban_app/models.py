"""
Models for the kanban_app.
Defines the structure for Boards, Tasks, and Comments.
"""

# 1. Standard library
# (None required)

# 2. Third-party (Django)
from django.conf import settings
from django.db import models

# 3. Local
# (None required)


class Board(models.Model):
    """
    Represents a Kanban board containing tasks and members.
    """
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_boards",
        blank=True
    )

    class Meta:
        """
        Meta options for the Board model.
        """
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Returns the board title.
        """
        return str(self.title)


class Task(models.Model):
    """
    Represents a task within a board with status and priority.
    """
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done")
    ]

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    board = models.ForeignKey(
        'Board',
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_tasks"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks"
    )

    class Meta:
        """
        Meta options for the Task model.
        """
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["due_date"]

    def __str__(self):
        """
        Returns task title with status and priority.
        """
        return f"{self.title} ({self.status} - {self.priority})"


class Comment(models.Model):
    """
    Represents a comment on a specific task.
    """
    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta options for the Comment model.
        """
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]

    def __str__(self):
        """
        Returns a summary of the comment.
        """
        return f"Comment by {self.author} on {self.task.title}"