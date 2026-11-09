from django.conf import settings
from django.db import models


class Board(models.Model):
    """Store a board with its owner and members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_boards",
        blank=True,
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    """Store a board task and the users involved in its completion."""

    class Status(models.TextChoices):
        TO_DO = "to-do", "To do"
        IN_PROGRESS = "in-progress", "In progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices)
    priority = models.CharField(max_length=10, choices=Priority.choices)
    due_date = models.DateField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        null=True,
        blank=True,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Store a task comment with its author and creation time."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.content[:50]
