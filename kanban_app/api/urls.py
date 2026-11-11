from django.urls import path

from .views import (
    AssignedTaskListView,
    BoardViewSet,
    CommentViewSet,
    EmailCheckView,
    ReviewingTaskListView,
    TaskViewSet,
)

urlpatterns = [
    path(
        "boards/", BoardViewSet.as_view({"get": "list", "post": "create"}),
        name="board-list",
    ),
    path(
        "boards/<int:pk>/", BoardViewSet.as_view({
            "get": "retrieve", "patch": "partial_update", "delete": "destroy",
        }), name="board-detail",
    ),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path(
        "tasks/", TaskViewSet.as_view({"post": "create"}), name="task-create",
    ),
    path(
        "tasks/assigned-to-me/", AssignedTaskListView.as_view(),
        name="tasks-assigned-to-me",
    ),
    path(
        "tasks/reviewing/", ReviewingTaskListView.as_view(),
        name="tasks-reviewing",
    ),
    path(
        "tasks/<int:pk>/", TaskViewSet.as_view({
            "patch": "partial_update", "delete": "destroy",
        }), name="task-detail",
    ),
    path(
        "tasks/<int:task_id>/comments/", CommentViewSet.as_view({
            "get": "list", "post": "create",
        }), name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentViewSet.as_view({"delete": "destroy"}),
        name="task-comment-detail",
    ),
]
