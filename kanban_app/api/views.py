"""
Views for the kanban_app.
Handles CRUD operations for Boards, Tasks, and Comments using ViewSets and Generics.
"""

# 1. Standard library
# (None required)

# 2. Third-party (Django & DRF)
from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# 3. Local
from ..models import Board, Comment, Task
from .permissions import (
    IsBoardMemberForTask, IsCommentAuthor, IsOwner,
    IsOwnerOrMember, IsTaskAuthorOrBoardOwner
)
from .serializers import (
    BoardCreateSerializer, BoardDetailSerializer, BoardListSerializer,
    BoardUpdateSerializer, CommentCreateSerializer, CommentSerializer,
    TaskCreateSerializer, TaskDetailSerializer, TaskUpdateSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Board operations. Filters querysets based on user membership.
    """
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer

    def get_queryset(self):
        """Returns boards where the user is either owner or member."""
        user = self.request.user
        if self.action == 'list':
            return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return Board.objects.all()

    def get_serializer_class(self):
        """Selects serializer based on the current action."""
        serializer_map = {
            'create': BoardCreateSerializer,
            'retrieve': BoardDetailSerializer,
            'partial_update': BoardUpdateSerializer
        }
        return serializer_map.get(self.action, BoardListSerializer)

    def get_permissions(self):
        """Sets permissions: Owners only for deletion, members for others."""
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsOwnerOrMember()]

    def create(self, request, *args, **kwargs):
        """Creates a board and returns the detailed list representation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        return Response(
            BoardListSerializer(board).data,
            status=status.HTTP_201_CREATED
        )


class AssignedTasksListView(generics.ListAPIView):
    """Lists tasks where the user is assignee or reviewer."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        """Filters tasks for the authenticated user."""
        user = self.request.user
        return Task.objects.filter(Q(assignee=user) | Q(reviewer=user))


class ReviewTasksListView(generics.ListAPIView):
    """Lists tasks where the user is assigned as reviewer."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        """Filters tasks by reviewer status."""
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    """Endpoint for creating a new task."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCreateSerializer
    queryset = Task.objects.all()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint for retrieving, updating or deleting a specific task."""
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def get_permissions(self):
        """Authors or Board Owners can delete; members can view/update."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskAuthorOrBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberForTask()]

    def delete(self, request, *args, **kwargs):
        """Validates task ID format before deletion to ensure 400 status."""
        task_id = self.kwargs.get('pk')
        if task_id and not str(task_id).isdigit():
            raise ValidationError(
                "Ungültige Anfragedaten. Die übermittelte Task-ID ist fehlerhaft."
            )
        return self.destroy(request, *args, **kwargs)


class CommentListView(generics.ListCreateAPIView):
    """Lists and creates comments for a specific task."""
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]

    def get_queryset(self):
        """Checks board permissions and returns task comments."""
        task_id = self.kwargs.get('task_id')
        task = generics.get_object_or_404(Task, pk=task_id)
        self.check_object_permissions(self.request, task)
        return Comment.objects.filter(task_id=task_id)

    def get_serializer_class(self):
        """Returns specialized serializer for POST requests."""
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        """Validates permissions and saves comment with task link."""
        task_id = self.kwargs.get('task_id')
        task = generics.get_object_or_404(Task, pk=task_id)
        self.check_object_permissions(self.request, task)
        serializer.save(task_id=task_id)


class CommentDetailView(generics.DestroyAPIView):
    """Endpoint for deleting a specific comment."""
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    queryset = Comment.objects.all()
    lookup_url_kwarg = 'comment_id'

    def delete(self, request, *args, **kwargs):
        """Validates IDs and task-comment relation before deletion."""
        t_id = self.kwargs.get('task_id')
        c_id = self.kwargs.get('comment_id')
        if not str(t_id).isdigit() or not str(c_id).isdigit():
            raise ValidationError("Ungültige Anfragedaten. ID fehlerhaft.")
        
        comment = self.get_object()
        if str(comment.task_id) != str(t_id):
            return Response(
                {"error": "Ungültige Anfragedaten"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.destroy(request, *args, **kwargs)
