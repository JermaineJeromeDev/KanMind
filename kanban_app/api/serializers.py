"""
Serializers for the kanban_app.
Handles data transformation and validation for Boards, Tasks, and Comments.
"""

# 2. Third-party (Django & DRF)
from rest_framework import exceptions, serializers

# 3. Local
from auth_app.api.serializers import UserPublicSerializer
from auth_app.models import CustomUser
from ..models import Board, Comment, Task


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for listing boards with optimized count retrieval."""
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.ReadOnlyField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count", "owner_id"
        ]

    def get_member_count(self, obj):
        """Uses annotated count or performs fallback query."""
        count = getattr(obj, 'ann_member_count', obj.members.count())
        return count + 1

    def get_ticket_count(self, obj):
        """Uses annotated ticket count or performs fallback query."""
        return getattr(obj, 'ann_ticket_count', obj.tasks.count())

    def get_tasks_to_do_count(self, obj):
        """Uses annotated to-do count or performs fallback query."""
        return getattr(obj, 'ann_todo_count', obj.tasks.filter(status="to-do").count())

    def get_tasks_high_prio_count(self, obj):
        """Uses annotated high priority count or performs fallback query."""
        return getattr(obj, 'ann_high_prio_count', obj.tasks.filter(priority="high").count())


class BoardCreateSerializer(BoardListSerializer):
    """Serializer for creating a new board with members."""
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all(), required=False
    )

    class Meta:
        model = Board
        fields = BoardListSerializer.Meta.fields + ["members"]
        extra_kwargs = {'owner_id': {'read_only': True}}

    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        validated_data['owner'] = self.context['request'].user
        board = Board.objects.create(**validated_data)
        board.members.set(members_data)
        return board


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed view for a single task."""
    assignee = UserPublicSerializer(read_only=True)
    reviewer = UserPublicSerializer(read_only=True)
    comments_count = serializers.IntegerField(
        source='comments.count', read_only=True
    )
    board = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status",
            "priority", "assignee", "reviewer", "due_date", "comments_count"
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Comprehensive view of a board including its tasks and members."""
    members = UserPublicSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating board members and title."""
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all()
    )

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
    """Handles task creation with existence and permission checks."""
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='assignee',
        write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='reviewer',
        write_only=True, required=False, allow_null=True
    )
    board = serializers.IntegerField(write_only=True)

    class Meta:
        model = Task
        fields = [
            "board", "title", "description", "status",
            "priority", "assignee_id", "reviewer_id", "due_date"
        ]

    def validate_board(self, value):
        user = self.context['request'].user
        try:
            board_instance = Board.objects.get(pk=value)
        except Board.DoesNotExist:
            raise exceptions.NotFound(
                "Board nicht gefunden. Die angegebene Board-ID existiert nicht."
            )
        if not (board_instance.owner == user or
                board_instance.members.filter(id=user.id).exists()):
            raise exceptions.PermissionDenied(
                "Verboten. Der Benutzer muss Mitglied des Boards sein."
            )
        return board_instance

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        return TaskDetailSerializer(instance).data


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Handles task updates while returning full nested user data."""
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
        fields = [
            "title", "description", "status", "priority",
            "assignee_id", "reviewer_id", "due_date"
        ]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "status": instance.status,
            "priority": instance.priority,
            "assignee": UserPublicSerializer(instance.assignee).data
            if instance.assignee else None,
            "reviewer": UserPublicSerializer(instance.reviewer).data
            if instance.reviewer else None,
            "due_date": instance.due_date.isoformat()
            if instance.due_date else None
        }


class CommentSerializer(serializers.ModelSerializer):
    """Summary view for comments."""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        return obj.author.fullname if obj.author else "Deleted User"


class CommentCreateSerializer(serializers.ModelSerializer):
    """Creation logic for comments."""
    class Meta:
        model = Comment
        fields = ["content"]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        return CommentSerializer(instance).data