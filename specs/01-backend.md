# Backend

Repo: `django-boilerplate/` (inside this folder)  
Package manager: **uv**. Always `uv add` / `uv add --dev` — never hand-edit dependency manifests when the CLI works.

## Layout

```
django-boilerplate/
  pyproject.toml
  manage.py
  Makefile
  .env.example
  schema.yml
  config/
    settings/
      base.py
      local.py.example   # copy → local.py (gitignored)
      production.py
      test.py
    urls.py
  apps/
    common/models.py     # IndexedTimeStampedModel
    users/
      models.py          # email User
      managers.py
      routes.py
      api/
        serializers.py
        views.py
        permissions.py
```

## Settings

- Split: `base` / `local` / `production` / `test`.
- Env via `python-decouple` + `dj-database-url` (`DATABASE_URL`).
- Local default: SQLite (`sqlite:///db.sqlite3`).
- `DJANGO_SETTINGS_MODULE=config.settings.local` for development.

## Stack

| Package | Purpose |
|---------|---------|
| django | Framework |
| djangorestframework | API |
| djangorestframework-simplejwt | JWT (+ token_blacklist) |
| django-cors-headers | SPA origin |
| drf-spectacular | OpenAPI schema |
| python-decouple, dj-database-url | Config |
| django-model-utils | Timestamp fields |

## Custom User

- `AbstractBaseUser` + `PermissionsMixin` + `IndexedTimeStampedModel`
- `USERNAME_FIELD = "email"`
- Custom `UserManager` with `create_user` / `create_superuser`
- `AUTH_USER_MODEL = "users.User"`
- Always create schema with `manage.py makemigrations` / `migrate`

## DRF defaults

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

## Routes registry

Each app exports:

```python
routes = [
    {"regex": r"users", "viewset": UserViewSet, "basename": "user"},
]
```

`config/urls.py` merges all `routes` into a `DefaultRouter` under `/api/v1/`.

## Auth endpoints

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/token/` | Anonymous |
| POST | `/api/v1/auth/token/refresh/` | Anonymous |
| POST | `/api/v1/auth/logout/` | Authenticated |
| GET | `/api/v1/auth/me/` | Authenticated |

Token obtain uses **email** + password.

`/me` returns `{ id, email, permissions: ["app_label.codename", ...] }`.

## User CRUD

- `UserViewSet` at `/api/v1/users/`
- `IsAuthenticated` + Django model permissions (`users.view_user`, etc.)
- Create/update serializers accept `password` (write-only)

## OpenAPI

```bash
uv run python manage.py spectacular --file schema.yml
# or: make schema
```

Schema is consumed by the React repo’s `yarn openapi-ts`.

## CORS

`CORS_ALLOWED_ORIGINS` from env (default `http://localhost:5173`).

## Testing

API E2E via **pytest** + **pytest-django** (full HTTP stack through DRF). Prefer these over model/serializer unit tests for the same behavior.

```bash
make test          # uv run pytest
```

`config/settings/test.py` forces an in-memory SQLite DB so tests do not depend on local Postgres.

Seed users for the React Playwright suite:

```bash
make seed-e2e      # uv run python manage.py seed_e2e --extra-users 15
```

Credentials: `e2e-admin@example.com` / `e2e-viewer@example.com` with password `e2epass123`.

## Useful commands

```bash
uv add <pkg>
uv add --dev <pkg>
uv run python manage.py startapp <name> apps/<name>
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py spectacular --file schema.yml
uv run python manage.py seed_e2e --extra-users 15
uv run pytest
```
