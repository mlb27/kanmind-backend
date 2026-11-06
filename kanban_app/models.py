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
