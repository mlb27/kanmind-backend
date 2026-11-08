from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from kanban_app.models import Board, Task


class BoardSerializer(serializers.ModelSerializer):
    """Validate board creation and return board summaries."""

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )
    member_count = serializers.IntegerField(
        source="members.count", read_only=True,
    )
    ticket_count = serializers.IntegerField(read_only=True, default=0)
    tasks_to_do_count = serializers.IntegerField(read_only=True, default=0)
    tasks_high_prio_count = serializers.IntegerField(read_only=True, default=0)
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            "id", "title", "members", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count", "owner_id",
        ]


class UserSummarySerializer(serializers.ModelSerializer):
    """Return the public user fields used in API responses."""

    fullname = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskSerializer(serializers.ModelSerializer):
    """Return task information with nested assignee and reviewer details."""

    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    # New tasks have no comments until the comment model is added.
    comments_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "due_date", "comments_count",
        ]


class BoardTaskSerializer(TaskSerializer):
    """Omit the board ID when a task is already nested inside its board."""

    class Meta(TaskSerializer.Meta):
        fields = [
            "id", "title", "description", "status", "priority", "assignee",
            "reviewer", "due_date", "comments_count",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Return board details with members and their tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserSummarySerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Validate title and membership changes and return the updated users."""

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )
    owner_data = UserSummarySerializer(source="owner", read_only=True)
    members_data = UserSummarySerializer(
        source="members", many=True, read_only=True,
    )

    class Meta:
        model = Board
        fields = ["id", "title", "members", "owner_data", "members_data"]


class EmailCheckSerializer(serializers.Serializer):
    """Validate the email query parameter used to find a board member."""

    email = serializers.EmailField(max_length=254)


class TaskCreateSerializer(serializers.ModelSerializer):
    """Validate a new task and ensure its participants belong to the board."""

    board = serializers.IntegerField(write_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee", queryset=User.objects.all(),
        write_only=True, required=False, allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer", queryset=User.objects.all(),
        write_only=True, required=False, allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "board", "title", "description", "status", "priority",
            "assignee_id", "reviewer_id", "due_date",
        ]

    def validate_board(self, value):
        """Find the board and require membership before creating a task."""
        board = get_object_or_404(Board, pk=value)
        user = self.context["request"].user
        if not board.members.filter(pk=user.pk).exists():
            raise PermissionDenied("You must be a member of this board.")
        return board

    def validate(self, attrs):
        """Reject assignees and reviewers who are outside the task's board."""
        for field in ["assignee", "reviewer"]:
            user = attrs.get(field)
            if user and not attrs["board"].members.filter(pk=user.pk).exists():
                raise serializers.ValidationError({
                    f"{field}_id": "The user must be a board member.",
                })
        return attrs
