from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, AssignedTasksListView, ReviewTasksListView, TaskCreateView, TaskDetailView, CommentListView, CommentDetailView


router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', ReviewTasksListView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<str:pk>/', TaskDetailView.as_view(), name='task-detail'), 
    path('tasks/<int:task_id>/comments/', CommentListView.as_view(), name='task-comments'),
    path('tasks/<str:task_id>/comments/<str:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),
]
