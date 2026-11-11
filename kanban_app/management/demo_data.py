"""Reserved local demo accounts and sample content for the guest login."""

DEMO_USERS = {
    "guest": {
        "email": "guest@kanmind.local", "first_name": "Guest",
        "last_name": "User", "password": "Guest-KanMind-2026!",
    },
    "alex": {
        "email": "alex.demo@kanmind.local", "first_name": "Alex",
        "last_name": "Demo", "password": "Demo-KanMind-2026!",
    },
    "sam": {
        "email": "sam.demo@kanmind.local", "first_name": "Sam",
        "last_name": "Demo", "password": "Demo-KanMind-2026!",
    },
}

DEMO_BOARDS = {
    "personal": {"title": "KanMind Demo", "owner": "guest"},
    "team": {"title": "Team Workspace", "owner": "alex"},
}

DEMO_TASKS = [
    {
        "board": "personal", "creator": "guest",
        "title": "Plan the next sprint",
        "description": "Collect the next milestones and agree on priorities.",
        "status": "to-do", "priority": "high", "due_in_days": 3,
        "assignee": "guest", "reviewer": "sam",
        "comments": [
            ("sam", "Please include time for the final API checks."),
            ("alex", "The team is ready to review the next milestones."),
        ],
    },
    {
        "board": "personal", "creator": "guest",
        "title": "Connect the API",
        "description": "Connect the supplied frontend to the local API.",
        "status": "in-progress", "priority": "medium", "due_in_days": 7,
        "assignee": "guest", "reviewer": "alex",
        "comments": [("guest", "Login and the board list are connected.")],
    },
    {
        "board": "personal", "creator": "alex",
        "title": "Review the board workflow",
        "description": "Check board membership, task updates and comments.",
        "status": "review", "priority": "high", "due_in_days": 5,
        "assignee": "alex", "reviewer": "guest",
        "comments": [("sam", "The workflow is ready for your review.")],
    },
    {
        "board": "personal", "creator": "guest",
        "title": "Set up the project",
        "description": "Create the environment and apply the migrations.",
        "status": "done", "priority": "low", "due_in_days": -1,
        "assignee": "guest", "reviewer": "sam",
        "comments": [("sam", "The setup instructions worked correctly.")],
    },
    {
        "board": "team", "creator": "alex",
        "title": "Check the release notes",
        "description": "Review the release notes before the next handover.",
        "status": "to-do", "priority": "medium", "due_in_days": 10,
        "assignee": "sam", "reviewer": "guest",
        "comments": [("alex", "Please check the setup and API sections.")],
    },
    {
        "board": "team", "creator": "alex",
        "title": "Prepare demo content",
        "description": "Keep useful example tasks available for visitors.",
        "status": "in-progress", "priority": "low", "due_in_days": 12,
        "assignee": "guest", "reviewer": "sam", "comments": [],
    },
]
