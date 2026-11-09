from rest_framework.permissions import BasePermission


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
    """Allow member edits and deletion by the creator or board owner."""

    def has_object_permission(self, request, view, obj):
        """Apply the task's edit and deletion rules separately."""
        if request.method == "DELETE":
            return (
                obj.creator_id == request.user.id
                or obj.board.owner_id == request.user.id
            )
        return obj.board.members.filter(pk=request.user.id).exists()
