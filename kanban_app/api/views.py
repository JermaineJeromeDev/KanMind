from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Board
from .serializers import BoardListSerializer


class BoardListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardListSerializer 
    queryset = Board.objects.none()         

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
