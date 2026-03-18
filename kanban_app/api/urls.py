from django.urls import path
from .views import BoardListView, BoardDetailView, AssignedTasksListView, ReviewTasksListView, TaskCreateView, TaskDetailView, CommentListView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', ReviewTasksListView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>//', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', CommentListView.as_view(), name='task-comments'),

]
