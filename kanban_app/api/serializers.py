from django.contrib.auth.models import User
from rest_framework import serializers

from kanban_app.models import Board


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
    # Boards have no tasks until the task model is added.
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


class BoardDetailSerializer(serializers.ModelSerializer):
    """Return board details with members and an initially empty task list."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserSummarySerializer(many=True, read_only=True)
    # Replace the empty list with task serialization when tasks are added.
    tasks = serializers.ListField(read_only=True, default=list)

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
