from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from kanban_app.models import Task


class IsBoardOwnerOrMember(BasePermission):
    """Allow board access to participants and deletion only to the owner."""

    def has_object_permission(self, request, view, obj):
        """Check the requested action against the board's participants."""
        if request.method == "DELETE":
            return obj.owner_id == request.user.id
        return (
            obj.owner_id == request.user.id
            or obj.members.filter(pk=request.user.id).exists()
        )


class IsTaskActionAllowed(BasePermission):
    """Allow member creation/edits and creator or board owner deletion."""

    def has_object_permission(self, request, view, obj):
        """Apply the task's edit and deletion rules separately."""
        if request.method == "POST":
            return obj.members.filter(pk=request.user.id).exists()
        if request.method == "DELETE":
            return (
                obj.creator_id == request.user.id
                or obj.board.owner_id == request.user.id
            )
        return obj.board.members.filter(pk=request.user.id).exists()


class IsTaskBoardMember(BasePermission):
    """Allow comment listing and creation only to task board members."""

    def has_permission(self, request, view):
        """Resolve the parent task and check the user's board membership."""
        task = get_object_or_404(
            Task.objects.select_related("board"), pk=view.kwargs["task_id"],
        )
        return task.board.members.filter(pk=request.user.id).exists()


class IsCommentAuthor(BasePermission):
    """Allow deleting a comment only by the user who wrote it."""

    def has_object_permission(self, request, view, obj):
        """Compare the authenticated user with the stored comment author."""
        return obj.author_id == request.user.id
