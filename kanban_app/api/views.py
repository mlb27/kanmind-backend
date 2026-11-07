from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from kanban_app.models import Board

from .permissions import IsBoardOwnerOrMember
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
)


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


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update or delete a board with object permissions."""

    queryset = Board.objects.select_related("owner").prefetch_related(
        "members",
    )
    serializer_class = BoardDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Use writable member IDs only for board updates."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return super().get_serializer_class()
