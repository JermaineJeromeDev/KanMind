from django.db.models import Q
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Board, Task, Comment
from .serializers import BoardListSerializer, BoardCreateSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskDetailSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer, CommentCreateSerializer
from .permissions import IsOwnerOrMember, IsOwner, IsBoardMemberForTask, IsTaskAuthorOrBoardOwner, IsCommentAuthor


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BoardCreateSerializer
        if self.action == 'retrieve':
            return BoardDetailSerializer
        if self.action == 'partial_update':
            return BoardUpdateSerializer
        return BoardListSerializer
    
    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsOwnerOrMember()]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        return Response(BoardListSerializer(board).data, status=status.HTTP_201_CREATED)


class AssignedTasksListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(assignee=user) | Q(reviewer=user))


class ReviewTasksListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCreateSerializer
    queryset = Task.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskAuthorOrBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberForTask()]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CommentListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)

    def get_serializer_class(self):
        """Wählt Create-Serializer für POST."""
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        task = generics.get_object_or_404(Task, pk=task_id)
        self.check_object_permissions(self.request, task)
        serializer.save(task_id=task_id)
        

class CommentDetailView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    queryset = Comment.objects.all()
    lookup_url_kwarg = 'comment_id'

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if str(comment.task_id) != str(self.kwargs.get('task_id')):
            return Response({"error": "Comment/Task mismatch"}, status=status.HTTP_400_BAD_REQUEST)
        return self.destroy(request, *args, **kwargs)