from django.urls import path

from .views import (
    BoardDetailView,
    BoardListCreateView,
    EmailCheckView,
    TaskCreateView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
]
