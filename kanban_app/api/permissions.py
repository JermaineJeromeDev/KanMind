from rest_framework import permissions

class IsOwnerOrMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()

        return is_owner or is_member


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
    

class IsBoardMemberForTask(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return board.owner == request.user or board.members.filter(id=request.user.id).exists()