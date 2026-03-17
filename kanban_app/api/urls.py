from django.urls import path
from .views import BoardListView, BoardDetailView, AssignedTasksListView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='tasks-assigned'),
]
