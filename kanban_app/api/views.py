from django.db.models import Q
from rest_framework import status  
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Board
from .serializers import BoardListSerializer, BoardCreateSerializer


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
    