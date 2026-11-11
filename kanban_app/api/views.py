from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
    TaskBoardSerializer,
    TaskCreateSerializer,
    TaskSerializer,
    TaskUpdateResponseSerializer,
    TaskUpdateSerializer,
    UserSummarySerializer,
)


class BoardViewSet(ModelViewSet):
    """Create, list and manage boards with action-specific responses."""

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
    ).select_related("owner").prefetch_related("members")
    serializer_class = BoardSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Filter personal lists and load task details only when needed."""
        queryset = super().get_queryset().order_by("id")
        if self.action == "list":
            user = self.request.user
            return queryset.filter(Q(owner=user) | Q(members=user)).distinct()
        return queryset.prefetch_related(
            "tasks__assignee", "tasks__reviewer", "tasks__comments",
        )

    def get_serializer_class(self):
        """Select the documented summary, detail or update response."""
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Always use the authenticated user as the new board's owner."""
        serializer.save(owner=self.request.user)


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


class TaskViewSet(ModelViewSet):
    """Create, partially update and delete tasks with action permissions."""

    queryset = Task.objects.select_related("board", "assignee", "reviewer")
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskActionAllowed]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Use dedicated input serializers for task creation and updates."""
        if self.action == "create":
            return TaskCreateSerializer
        if self.action == "partial_update":
            return TaskUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """Check board access before validating and saving task details."""
        board_data = TaskBoardSerializer(data=request.data)
        board_data.is_valid(raise_exception=True)
        self.check_object_permissions(
            request, board_data.validated_data["board"],
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(creator=request.user)
        return Response(
            TaskSerializer(task).data, status=status.HTTP_201_CREATED,
        )

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


class CommentViewSet(ModelViewSet):
    """List, create and delete nested task comments with author checks."""

    queryset = Comment.objects.select_related("author")
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTaskBoardMember]
    pagination_class = None
    lookup_url_kwarg = "comment_id"
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_permissions(self):
        """Require membership for reading/writing and authorship to delete."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsCommentAuthor()]
        return super().get_permissions()

    def get_queryset(self):
        """Bind every comment lookup to the task supplied by its URL."""
        return super().get_queryset().filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        """Use the authenticated author and the task supplied by the URL."""
        serializer.save(
            author=self.request.user, task_id=self.kwargs["task_id"],
        )
