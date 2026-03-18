from django.db.models import Q
from rest_framework import status 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Board, Task
from .serializers import BoardListSerializer, BoardCreateSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskDetailSerializer, TaskCreateSerializer, TaskUpdateSerializer
from .permissions import IsOwnerOrMember, IsOwner, IsBoardMemberForTask


class BoardListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardListSerializer 
    queryset = Board.objects.none()      

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardListSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = self.get_serializer_class()(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            board = serializer.save()
            return Response(
                BoardListSerializer(board).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)).distinct()
    


class BoardDetailView(APIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsOwner]
        return [IsAuthenticated(), IsOwnerOrMember()]

    def get(self, request, pk):
        try:
            board = Board.objects.get(pk=pk)
            self.check_object_permissions(request, board)
            serializer = self.serializer_class(board)
            return Response(serializer.data)
        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, pk):
        try:
            board = Board.objects.get(pk=pk)
            self.check_object_permissions(request, board)

            serializer = BoardUpdateSerializer(board, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Board.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, pk):
        try:
            board = Board.objects.get(pk=pk)
            self.check_object_permissions(request, board)
            board.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=status.HTTP_404_NOT_FOUND)


class AssignedTasksListView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.none()
    serializer_class = TaskDetailSerializer
    
    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(assignee=user) | Q(reviewer=user))
    

class ReviewTasksListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.none()

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)
    

class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, 
                                        context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]
    serializer_class = TaskUpdateSerializer
    queryset = Task.objects.all()

    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            self.check_object_permissions(request, task)
            serializer = self.serializer_class(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)