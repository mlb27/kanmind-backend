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
