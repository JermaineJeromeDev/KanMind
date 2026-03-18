from django.urls import path
from .views import BoardListView, BoardDetailView, AssignedTasksListView, ReviewTasksListView, TaskCreateView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', ReviewTasksListView.as_view(), name='tasks-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
]
