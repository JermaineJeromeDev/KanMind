from django.db.models import Q
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
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


class CommentListView(APIView):
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]
    serializer_class = CommentSerializer

    def get(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id)
            self.check_object_permissions(request, task)

            comments = task.comments.all()
            serializer = self.serializer_class(comments, many=True)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id)
            self.check_object_permissions(request, task)
            serializer = CommentCreateSerializer(
                data=request.data, 
                context={'request': request, 'task_id': task_id}
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    queryset = Comment.objects.all()

    def delete(self, request, task_id, comment_id):
        try:
            comment = Comment.objects.het(pk=comment_id, task_id=task_id)
            self.check_object_permissions(request, comment)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)