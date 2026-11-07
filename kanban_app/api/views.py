from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.models import Board

from .permissions import IsBoardOwnerOrMember
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    EmailCheckSerializer,
    UserSummarySerializer,
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


class EmailCheckView(GenericAPIView):
    """Find a registered user by email for authenticated board invitations."""

    queryset = User.objects.all()
    serializer_class = UserSummarySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Validate the query and return the matching user's public fields."""
        query = EmailCheckSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        user = get_object_or_404(
            self.get_queryset(),
            email__iexact=query.validated_data["email"],
        )
        return Response(self.get_serializer(user).data)
