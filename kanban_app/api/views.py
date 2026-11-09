from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.models import Board, Comment, Task

from .permissions import (
    IsBoardOwnerOrMember,
    IsCommentAuthor,
    IsTaskActionAllowed,
    IsTaskBoardMember,
)
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    EmailCheckSerializer,
    TaskCreateSerializer,
    TaskSerializer,
    TaskUpdateResponseSerializer,
    TaskUpdateSerializer,
    UserSummarySerializer,
)


class BoardListCreateView(ListCreateAPIView):
    """Create boards and list boards owned by or shared with the user."""

    queryset = Board.objects.annotate(
        ticket_count=Count("tasks", distinct=True),
        tasks_to_do_count=Count(
            "tasks", filter=Q(tasks__status=Task.Status.TO_DO), distinct=True,
        ),
        tasks_high_prio_count=Count(
            "tasks",
            filter=Q(tasks__priority=Task.Priority.HIGH),
            distinct=True,
        ),
    )
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
        "members", "tasks__assignee", "tasks__reviewer", "tasks__comments",
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


class TaskCreateView(CreateAPIView):
    """Create a task for a board member and record its actual creator."""

    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Validate the input and return the newly created task's details."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(creator=request.user)
        return Response(
            TaskSerializer(task).data, status=status.HTTP_201_CREATED,
        )


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """Partially update or delete tasks according to the requested action."""

    queryset = Task.objects.select_related("board", "assignee", "reviewer")
    serializer_class = TaskUpdateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskActionAllowed]
    http_method_names = ["patch", "delete", "options"]

    def partial_update(self, request, *args, **kwargs):
        """Validate changed fields and return the updated task information."""
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskUpdateResponseSerializer(task).data)


class AssignedTaskListView(ListAPIView):
    """List only the tasks assigned to the authenticated user."""

    queryset = Task.objects.select_related(
        "assignee", "reviewer",
    ).prefetch_related("comments")
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Filter the list by its current assignee."""
        return super().get_queryset().filter(assignee=self.request.user)


class ReviewingTaskListView(ListAPIView):
    """List only the tasks reviewed by the authenticated user."""

    queryset = Task.objects.select_related(
        "assignee", "reviewer",
    ).prefetch_related("comments")
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Filter the list by its current reviewer."""
        return super().get_queryset().filter(reviewer=self.request.user)


class TaskCommentListView(ListCreateAPIView):
    """List and create comments for a task accessible to board members."""

    queryset = Comment.objects.select_related("author")
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskBoardMember]
    pagination_class = None

    def get_queryset(self):
        """Return only comments belonging to the task in the URL."""
        return super().get_queryset().filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        """Use the authenticated author and the task supplied by the URL."""
        serializer.save(
            author=self.request.user, task_id=self.kwargs["task_id"],
        )


class TaskCommentDetailView(DestroyAPIView):
    """Delete a nested task comment only when requested by its author."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        """Bind the comment lookup to its parent task to prevent mismatches."""
        return super().get_queryset().filter(task_id=self.kwargs["task_id"])
