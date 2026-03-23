"""
Views for the kanban_app.
Handles CRUD operations for Boards, Tasks, and Comments using ViewSets and Generics.
"""

# 2. Third-party (Django & DRF)
from django.db.models import Q, Count
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
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
    ViewSet for Board operations. 
    Uses annotation to prevent N+1 issues in list views.
    """
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer

    def get_queryset(self):
        """
        Returns boards with pre-calculated counts for the list action.
        """
        user = self.request.user
        queryset = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

        if self.action == 'list':
            return queryset.annotate(
                ann_member_count=Count('members', distinct=True),
                ann_ticket_count=Count('tasks', distinct=True),
                ann_todo_count=Count(
                    'tasks', filter=Q(tasks__status='to-do'), distinct=True
                ),
                ann_high_prio_count=Count(
                    'tasks', filter=Q(tasks__priority='high'), distinct=True
                )
            )
        return queryset

    def get_serializer_class(self):
        """Selects serializer based on action."""
        serializer_map = {
            'create': BoardCreateSerializer,
            'retrieve': BoardDetailSerializer,
            'partial_update': BoardUpdateSerializer
        }
        return serializer_map.get(self.action, BoardListSerializer)

    def get_permissions(self):
        """Sets permissions based on action."""
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsOwnerOrMember()]

    def create(self, request, *args, **kwargs):
        """Creates board and returns list representation."""
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
    """
    Endpoint for deleting a specific comment.
    Ensures ID integrity and task-comment relationship.
    """
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    queryset = Comment.objects.all()
    lookup_url_kwarg = 'comment_id'

    def perform_destroy(self, instance):
        """
        Validates task relationship before final deletion.
        Ensures 400 status for ID mismatch as per documentation.
        """
        task_id = self.kwargs.get('task_id')
        
        if str(instance.task_id) != str(task_id):
            raise ValidationError("Ungültige Anfragedaten. Task-ID Mismatch.")
        instance.delete()

    def get_object(self):
        """
        Validates ID format before fetching the object to enforce 400 status.
        """
        c_id = self.kwargs.get('comment_id')
        t_id = self.kwargs.get('task_id')
        
        if not str(c_id).isdigit() or not str(t_id).isdigit():
            raise ValidationError("Ungültige Anfragedaten. ID fehlerhaft.")
            
        return super().get_object()