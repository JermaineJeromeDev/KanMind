from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from auth_app.models import CustomUser
from ..models import Board, Task, Comment
from auth_app.api.serializers import UserPublicSerializer



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
        return obj.tasks.filter(status="to-do").count()

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
    

class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserPublicSerializer(read_only=True)
    reviewer = UserPublicSerializer(read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    board = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Task
        fields = [
            "id", "board","title", "description", "status", 
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


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all())

    class Meta:
        model = Board
        fields = ["title", "members"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "owner_data": UserPublicSerializer(instance.owner).data,
            "members_data": UserPublicSerializer(instance.members.all(), many=True).data
        }
    

class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )
    board = serializers.IntegerField(write_only=True)

    class Meta:
        model = Task
        fields = ["board", "title", "description", "status", "priority", "assignee_id", "reviewer_id", "due_date"]

    def validate_board(self, value):
        user = self.context['request'].user
    
        try:
            board_instance = Board.objects.get(pk=value)
        except Board.DoesNotExist:
            raise exceptions.NotFound("Board nicht gefunden. Die angegebene Board-ID existiert nicht.")

        if not (board_instance.owner == user or board_instance.members.filter(id=user.id).exists()):
            raise exceptions.PermissionDenied("Verboten. Der Benutzer muss Mitglied des Boards sein, um eine Task zu erstellen.")       
        return board_instance
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        return TaskDetailSerializer(instance).data
    

class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='assignee', 
        write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='reviewer', 
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = ["title", "description", "status", "priority", "assignee_id", "reviewer_id", "due_date"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "status": instance.status,
            "priority": instance.priority,
            "assignee": UserPublicSerializer(instance.assignee).data if instance.assignee else None,
            "reviewer": UserPublicSerializer(instance.reviewer).data if instance.reviewer else None,
            "due_date": instance.due_date.isoformat() if instance.due_date else None
        }


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        if obj.author:
            return obj.author.fullname
        return "Deleted User"


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        return CommentSerializer(instance).data