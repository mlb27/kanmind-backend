# KanMind Backend

Django REST Framework API for the Developer Akademie KanMind project.
The supplied frontend is maintained separately.

## Requirements

- Python 3.12 or newer
- pip and a virtual environment
- The packages pinned in `requirements.txt`

SQLite is used for local development. The database and virtual environment
are excluded from Git.

## Installation and startup

Clone the backend and enter its directory:

```bash
git clone https://github.com/mlb27/kanmind-backend.git
cd kanmind-backend
python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

On Windows, activate the environment with `env\Scripts\activate` instead
of `source env/bin/activate`.

The API is available at `http://127.0.0.1:8000/api/`.
Keep the development server running while using the frontend.

## Guest login and demo content

After running `python manage.py seed_demo`, use:

- Email: `guest@kanmind.local`
- Password: `Guest-KanMind-2026!`

The command creates three regular users, two boards, six tasks covering all
four statuses and all three priorities, and six comments. The guest owns one
board and belongs to another. Both the assigned-task list and the reviewing
list contain examples.

The other demo users are `alex.demo@kanmind.local` and
`sam.demo@kanmind.local`, both with password `Demo-KanMind-2026!`.
All demo users are members of both boards. None has admin privileges.

Task dates are calculated relative to the day the data is first created.
Running the command again does not duplicate unchanged demo data or overwrite
existing task content. It can add missing demo records. Existing accounts
with conflicting details cause the complete command to stop without saving
partial changes.

The demo data is created by the management command; it does not need a
committed database file.

## Supplied frontend

Open the supplied frontend's root `index.html` with Live Server.
Use the origin `http://127.0.0.1:5500`, which is allowed by the local CORS
configuration.

The frontend's `shared/js/config.js` must contain:

```javascript
const GUEST_LOGIN = {
    "email": "guest@kanmind.local",
    "password": "Guest-KanMind-2026!"
}

const API_BASE_URL = 'http://127.0.0.1:8000/api/';
```

The frontend logic is supplied by the academy. Guest credentials and the API
base URL are its relevant configuration entries for this backend.

## Admin

Create a separate administrator if needed:

```bash
python manage.py createsuperuser
```

Open `http://127.0.0.1:8000/admin/` and use the administrator's username.
Boards, tasks and comments are registered in the admin.

Frontend users registered through the API and the seeded demo accounts use
their email address as their Django username.

## API and authentication

The endpoint contract is documented in the
[Developer Akademie KanMind API documentation](https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=kanmind).

Registration and login are public:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/registration/` | Create an account and return a token |
| POST | `/api/login/` | Authenticate and return a token |

All other endpoints require the returned token:

```http
Authorization: Token <token>
```

| Method | Path | Purpose |
| --- | --- | --- |
| GET, POST | `/api/boards/` | List accessible boards or create a board |
| GET, PATCH, DELETE | `/api/boards/{id}/` | Read, change or delete a board |
| GET | `/api/email-check/?email=...` | Look up a registered user |
| POST | `/api/tasks/` | Create a task |
| PATCH, DELETE | `/api/tasks/{id}/` | Change or delete a task |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | List tasks reviewed by the current user |
| GET, POST | `/api/tasks/{id}/comments/` | List or create comments |
| DELETE | `/api/tasks/{id}/comments/{comment_id}/` | Delete an author's own comment |

Board ownership and board membership are separate. Creating a board does
not automatically add its owner as a member. Task creation, task editing
and comment reading/writing require membership. Assignees and reviewers
must also be board members; both assignments may be empty.

Only the board owner can delete the board. The task creator or the board
owner may delete a task. Only the comment author may delete their comment.

Deleting a board removes its tasks and comments. Deleting a task removes
its comments. Partial task updates keep omitted fields and cannot move a
task to another board.

## Verification and dependency updates

Run Django's checks after setup or changes:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

Use Postman to check API responses, validation and permissions independently
of the supplied frontend. Browser testing additionally checks the integration.

The academy's original PM tests are not included in this repository.
Its required result of at least 95% must be checked with the academy's suite;
local API checks do not establish that result.

After intentionally changing installed dependencies, update the package list:

```bash
python -m pip freeze > requirements.txt
```

The included settings and `runserver` command are intended for local
development. Deployment requires environment-specific server settings.
