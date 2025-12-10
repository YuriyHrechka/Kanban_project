Backend for Kanban_project

Quick start for frontend devs

Endpoints (JSON API):
- POST /api/auth/register/  -> {username, password, confirm_password}
  - returns {access, refresh, user_id, username}
- POST /api/auth/token/ -> {username, password}
  - returns {access, refresh}
- POST /api/auth/refresh/ -> {refresh}
  - returns new access (and new refresh if rotation enabled)
- GET /api/auth/profile/ (Bearer <access>) -> {id, username}

Kanban endpoints (authenticated):
- /api/boards/  (list, create)  -> board has fields id, title, description, owner (readonly), created_at, updated_at
- /api/columns/ (list, create)  -> column has id, title, board, position
- /api/cards/   (list, create)  -> card has id, title, description, column, position, due_date, priority

Notes / tips
- Authentication: use the Bearer access token in the Authorization header.
- When creating boards, owner is set automatically to the authenticated user; do not send `owner` in the create payload.
- You cannot create or modify Columns/Cards inside Boards you do not own. API returns 403 if attempted.
- Pagination: lists are paginated (page size = 10). Use `?page=n`.
- Priority choices: "low", "medium", "high".
- For local development use the Swagger UI at /api/schema/swagger-ui/ to explore endpoints.

Running tests

python3 manage.py test users
python3 manage.py test kanban

