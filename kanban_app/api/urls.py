"""
URL configuration for the kanban_app.
Defines endpoints for boards, tasks, and comments using routers and generic views.
"""

# 1. Standard library
# (None required)

# 2. Third-party (Django & DRF)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# 3. Local
from .views import (
    AssignedTasksListView, BoardViewSet, CommentDetailView,
    CommentListView, ReviewTasksListView, TaskCreateView, TaskDetailView
)


router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    # Router-based board endpoints
    path('', include(router.urls)),

    # Task specialized list views
    path(
        'tasks/assigned-to-me/',
        AssignedTasksListView.as_view(),
        name='tasks-assigned'
    ),
    path(
        'tasks/reviewing/',
        ReviewTasksListView.as_view(),
        name='tasks-reviewing'
    ),

    # Task CRUD
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<str:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Comment CRUD
    path(
        'tasks/<int:task_id>/comments/',
        CommentListView.as_view(),
        name='task-comments'
    ),
    path(
        'tasks/<str:task_id>/comments/<str:comment_id>/',
        CommentDetailView.as_view(),
        name='comment-detail'
    ),
]
