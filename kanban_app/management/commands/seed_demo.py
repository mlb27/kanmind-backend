"""Create reusable local demo data without overwriting existing content."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from kanban_app.management.demo_data import DEMO_BOARDS, DEMO_TASKS, DEMO_USERS
from kanban_app.models import Board, Comment, Task


class Command(BaseCommand):
    help = "Create the local guest account, demo teammates, boards and tasks."

    @transaction.atomic
    def handle(self, *args, **options):
        """Create missing demo records as one complete transaction."""
        users = {
            role: self.get_demo_user(data) for role, data in DEMO_USERS.items()
        }
        boards = self.get_demo_boards(users)
        for data in DEMO_TASKS:
            self.get_demo_task(data, boards, users)
        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Guest login: guest@kanmind.local / "
            "Guest-KanMind-2026!",
        ))

    def get_demo_user(self, data):
        """Create a reserved demo user or verify the existing demo account."""
        email = data["email"]
        user = User.objects.filter(username=email).first()
        if user:
            self.validate_demo_user(user, data)
            return user
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("A reserved demo email is already in use.")
        return User.objects.create_user(
            username=email, email=email, password=data["password"],
            first_name=data["first_name"], last_name=data["last_name"],
        )

    def validate_demo_user(self, user, data):
        """Refuse to repurpose an existing account with different details."""
        if (
            user.email != data["email"]
            or user.first_name != data["first_name"]
            or user.last_name != data["last_name"]
            or user.is_staff or user.is_superuser or not user.is_active
            or not user.check_password(data["password"])
        ):
            raise CommandError(
                "An existing demo account has different details. "
                "No data was changed; existing accounts are kept intact.",
            )

    def get_demo_boards(self, users):
        """Create demo boards and give new boards their initial members."""
        boards = {}
        for key, data in DEMO_BOARDS.items():
            board, created = Board.objects.get_or_create(
                owner=users[data["owner"]], title=data["title"],
            )
            if created:
                board.members.add(*users.values())
            boards[key] = board
        return boards

    def get_task_defaults(self, data, users):
        """Build initial task values with dates relative to the setup day."""
        return {
            "description": data["description"], "status": data["status"],
            "priority": data["priority"],
            "due_date": timezone.localdate() + timedelta(
                days=data["due_in_days"],
            ),
            "assignee": users[data["assignee"]],
            "reviewer": users[data["reviewer"]],
        }

    def get_demo_task(self, data, boards, users):
        """Add a missing demo task and its example discussion."""
        task, _ = Task.objects.get_or_create(
            board=boards[data["board"]], creator=users[data["creator"]],
            title=data["title"], defaults=self.get_task_defaults(data, users),
        )
        for role, content in data["comments"]:
            Comment.objects.get_or_create(
                task=task, author=users[role], content=content,
            )
