from django.urls import path

from .views import (
    AssignedTaskListView,
    BoardDetailView,
    BoardListCreateView,
    EmailCheckView,
    ReviewingTaskListView,
    TaskCommentDetailView,
    TaskCommentListView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/assigned-to-me/", AssignedTaskListView.as_view(),
        name="tasks-assigned-to-me",
    ),
    path(
        "tasks/reviewing/", ReviewingTaskListView.as_view(),
        name="tasks-reviewing",
    ),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<int:task_id>/comments/", TaskCommentListView.as_view(),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        TaskCommentDetailView.as_view(), name="task-comment-detail",
    ),
]
