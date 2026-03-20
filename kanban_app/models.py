from django.db import models
from django.conf import settings


class Board(models.Model):
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
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["-created_at"] 

    def __str__(self):
        return self.title
    
    

class Task(models.Model):
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
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES
    )

    board = models.ForeignKey(
        'Board', 
        on_delete=models.CASCADE, 
        related_name="tasks"
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="assigned_tasks"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="reviewed_tasks"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks"
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.title} ({self.status} - {self.priority})"


class Comment(models.Model):
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
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.fullname} on {self.task.title}"