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
