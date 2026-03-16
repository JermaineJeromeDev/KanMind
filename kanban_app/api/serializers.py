from rest_framework import serializers

from auth_app.models import CustomUser
from ..models import Board, Task


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id"
        ]

    def get_member_count(self, obj):
        return obj.members.count() + 1

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="todo").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    

class BoardCreateSerializer(BoardListSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=CustomUser.objects.all(), 
        required=False
    )

    class Meta:
        model = Board  
        fields = [
            "id", "title", "member_count", "ticket_count", 
            "tasks_to_do_count", "tasks_high_prio_count", 
            "owner_id", "members"
        ]
        extra_kwargs = {'owner_id': {'read_only': True}}

    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        validated_data['owner'] = self.context['request'].user
        board = Board.objects.create(**validated_data)
        board.members.set(members_data)
        return board
    

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "fullname"]


class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserPublicSerializer(read_only=True)
    reviewer = UserPublicSerializer(read_only=True)
    comments_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", 
            "priority", "assignee", "reviewer", 
            "due_date", "comments_count"
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserPublicSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]