from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Board

from .serializers import BoardSerializer


class BoardListCreateView(ListCreateAPIView):
    """Create boards and list boards owned by or shared with the user."""

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Restrict the list to boards accessible to the current user."""
        user = self.request.user
        return (
            super().get_queryset()
            .filter(Q(owner=user) | Q(members=user))
            .distinct()
            .prefetch_related("members")
            .order_by("id")
        )

    def perform_create(self, serializer):
        """Always use the authenticated user as the new board's owner."""
        serializer.save(owner=self.request.user)
