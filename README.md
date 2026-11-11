# KanMind Backend

REST API for managing Kanban boards, tasks and comments.

## Features

- Registration and login with token authentication
- Boards with members and access permissions
- Tasks with status, priority, assignees and reviewers
- Task comments and personal task lists
- Guest login with demo boards and tasks

## Running locally

Requires Python 3.12 or newer. This setup runs the backend locally.

```bash
git clone https://github.com/mlb27/kanmind-backend.git
cd kanmind-backend
python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

On Windows, activate the environment with `env\Scripts\activate`.

API: `http://127.0.0.1:8000/api/`

For admin access, run `python manage.py createsuperuser` and open
`http://127.0.0.1:8000/admin/`.

## Guest login

- Email: `guest@kanmind.local`
- Password: `Guest-KanMind-2026!`

`seed_demo` creates three demo users, two boards, six tasks and six comments.
Running it again does not duplicate unchanged demo data or overwrite existing tasks.
Conflicting demo accounts stop the command without changing existing data.

## Frontend

Open the supplied frontend with Live Server at `http://127.0.0.1:5500`.
In `shared/js/config.js`, set:

- `API_BASE_URL` to `http://127.0.0.1:8000/api/`
- `GUEST_LOGIN` to the guest credentials above

Board owners must also add themselves as members to create tasks.

## Technologies

- Python
- Django and Django REST Framework
- SQLite

## API documentation

[KanMind endpoints](https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=kanmind)

Authenticated requests use `Authorization: Token <token>`.

## Project context

This project was created as part of the **Developer Akademie** program.

## Author

Moritz Böhm
