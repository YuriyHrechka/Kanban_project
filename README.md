# Kanban Board API

A powerful RESTful API for task management using the Kanban methodology. Built with **Django** and **Django REST Framework**, fully dockerized and ready for deployment.


## Key Features

This API provides a full spectrum of features for creating and managing task boards:

  * **Authentication & Security**

      * User registration and login (JWT tokens: Access & Refresh).
      * **Data Isolation:** Users can only access and modify their own boards, columns, and cards.
      * Password validation and username uniqueness checks.

  * **Board Management**

      * Create personal workspaces (boards).
      * View lists of active boards.

  * **Columns**

      * Create columns (e.g., "To Do", "In Progress", "Done").
      * **Drag & Drop Logic:** Dedicated endpoint for changing column positions (`/move`), automatically reordering adjacent columns.

  * **Cards**

      * Create tasks with due dates (`due_date`) and descriptions.
      * **Priorities:** Supports `Low`, `Medium`, and `High` levels.
      * **Movement:** Move cards between columns and change their order within a column.

  * **Documentation**

      * Automatically generated Swagger UI and ReDoc documentation.


## Tech Stack

  * **Language:** Python 3.12
  * **Framework:** Django 5.2.6
  * **API:** Django REST Framework + `drf-spectacular` (OpenAPI 3.0)
  * **Database:** PostgreSQL 15
  * **Authentication:** `djangorestframework-simplejwt`
  * **Containerization:** Docker & Docker Compose


## Installation & Setup

The project is configured for quick startup using Docker.

### 1\. Clone the repository

```bash
git clone https://github.com/YuriyHrechka/Kanban_project/
cd Kanban_project
```

### 2\. Environment Configuration

A default `.env` file is already included in the project root containing the necessary database and Django settings. You can review or modify it if needed:

### 3\. Run via Docker Compose

This command will build the image, start the database, apply migrations, and launch the server:

```bash
docker-compose up --build
```

After startup, the API will be available at: `http://localhost:8000`

-----

## API Endpoints

### Auth (Users)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/token/` | Obtain JWT pair (Login) |
| `POST` | `/api/auth/refresh/` | Refresh Access Token |
| `GET` | `/api/auth/profile/` | Current user profile |

### Kanban (Requires Bearer Token)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET/POST` | `/api/boards/` | List boards / Create board |
| `GET/POST` | `/api/columns/` | List columns / Create column |
| `POST` | `/api/columns/{id}/move/` | **Move Column** (Body: `{"position": 2}`) |
| `GET/POST` | `/api/cards/` | List cards / Create card |
| `POST` | `/api/cards/{id}/move/` | **Move Card** (Body: `{"column": 1, "position": 3}`) |

## Testing

The project is covered by Unit tests. To run tests inside the container:

```bash
# Run all tests
docker exec -it kanban_backend python manage.py test

# Or run specific modules
docker exec -it kanban_backend python manage.py test users
docker exec -it kanban_backend python manage.py test kanban
```

-----

## Project Structure

```text
.
├── backend/
│   ├── common/
│   ├── config/
│   ├── kanban/
│   ├── users/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```
