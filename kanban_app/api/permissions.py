"""
Custom permissions for the kanban_app.
Defines access control for Boards, Tasks, and Comments.
"""

# 2. Third-party (DRF)
from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    """
    Allows access only to the board owner or assigned members.
    """
    def has_object_permission(self, request, view, obj):
        """Checks if user is owner or member of the board instance."""
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()
        return is_owner or is_member


class IsOwner(permissions.BasePermission):
    """
    Allows access only to the owner of the object.
    """
    def has_object_permission(self, request, view, obj):
        """Checks if user is the direct owner."""
        return obj.owner == request.user


class IsBoardMemberForTask(permissions.BasePermission):
    """
    Allows access to tasks if the user is owner or member of the parent board.
    """
    def has_object_permission(self, request, view, obj):
        """Checks membership in the board associated with the task."""
        board = obj.board
        is_owner = board.owner == request.user
        is_member = board.members.filter(id=request.user.id).exists()
        return is_owner or is_member


class IsTaskAuthorOrBoardOwner(permissions.BasePermission):
    """
    Allows deletion of tasks only for the task author or the board owner.
    """
    def has_object_permission(self, request, view, obj):
        """Checks if user created the task or owns the board it belongs to."""
        is_author = obj.author == request.user
        is_board_owner = obj.board.owner == request.user
        return is_author or is_board_owner


class IsCommentAuthor(permissions.BasePermission):
    """
    Allows access to comments only for the original author.
    """
    def has_object_permission(self, request, view, obj):
        """Checks if the user is the author of the comment."""
        return obj.author == request.user
