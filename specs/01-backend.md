# Backend

Repo: `django-boilerplate/` (inside this folder)  
Package manager: **uv**. Always `uv add` / `uv add --dev` — never hand-edit dependency manifests when the CLI works.

## Layout

```
django-boilerplate/
  pyproject.toml
  manage.py
  Makefile
  Dockerfile
  docker-compose.yml
  .env.example
  schema.yml
  config/
    celery.py            # Celery app (autodiscover)
    settings/
      base.py
      local.py.example   # copy → local.py (gitignored)
      production.py
      test.py            # CELERY_TASK_ALWAYS_EAGER
    urls.py
  apps/
    common/models.py     # IndexedTimeStampedModel
    email_server/        # SMTPServer + Celery send_mail_task
    users/
      models.py          # email User
      email_auth.py      # EmailAuthCode (OTP)
      auth_codes.py      # create + queue_mail helpers
      managers.py
      routes.py
      templates/users/email/
      api/
        serializers.py
        views.py
        permissions.py
```

## Settings

- Split: `base` / `local` / `production` / `test`.
- Env via `python-decouple` + `dj-database-url` (`DATABASE_URL`).
- Local/default: Postgres via Compose (`postgres://postgres:postgres@db:5432/app`).
- Driver: `psycopg` (binary).
- `DJANGO_SETTINGS_MODULE=config.settings.local` for development.
- `LOGIN_2FA_ENABLED` (env, default `False`) gates login-time email OTP.
- Celery:
  - Broker/result: `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` (default `redis://redis:6379/0`).
  - App: `config.celery` (`celery -A config worker`).
  - Compose services: `redis` + `worker` (same image as `backend`).
  - **test** / Playwright e2e backend: `CELERY_TASK_ALWAYS_EAGER=True` so mail runs in-process without a worker.
- Email:
  - **local**: `EMAIL_BACKEND = filebased.EmailBackend`, writes to `sent_emails/` (gitignored).
  - **production**: `EMAIL_BACKEND = smtp.EmailBackend`; host/user/password/`from_email` come from `email_server.SMTPServer` at send time (Django admin).
  - `SMTPServer.send_mail()` is the **sync** sender (used by the Celery task). Request handlers call `queue_mail()` → `send_mail_task.delay(...)`.
  - Auth OTP / password-reset emails are always queued asynchronously (eager under pytest/e2e).
## Stack

| Package | Purpose |
|---------|---------|
| django | Framework |
| djangorestframework | API |
| djangorestframework-simplejwt | JWT (+ token_blacklist) |
| django-cors-headers | SPA origin |
| drf-spectacular | OpenAPI schema |
| celery[redis] | Background tasks (email) |
| python-decouple, dj-database-url | Config |
| psycopg[binary] | Postgres driver |
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

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/auth/token/` | Anonymous | JWT, or 202 challenge when `LOGIN_2FA_ENABLED` |
| POST | `/api/v1/auth/token/refresh/` | Anonymous | |
| POST | `/api/v1/auth/verify-code/` | Anonymous | Completes login 2FA → JWT |
| POST | `/api/v1/auth/resend-code/` | Anonymous | New OTP for a `challenge_id` |
| POST | `/api/v1/auth/forgot-password/` | Anonymous | Always 204 |
| POST | `/api/v1/auth/reset-password/` | Anonymous | email + code + new passwords |
| POST | `/api/v1/auth/logout/` | Authenticated | |
| GET | `/api/v1/auth/me/` | Authenticated | |

Token obtain uses **email** + password.

`/me` returns `{ id, email, permissions: ["app_label.codename", ...] }`.

Django admin is mounted at `/admin/` for `SMTPServer` (and other models you register).
## User CRUD

- `UserViewSet` at `/api/v1/users/`
- `IsAuthenticated` + Django model permissions (`users.view_user`, etc.)
- Create/update serializers accept `password` (write-only)

## OpenAPI

```bash
make schema
```

Schema is consumed by the React repo’s `make openapi-ts`.

## CORS

`CORS_ALLOWED_ORIGINS` from env (default includes `http://localhost:5173` and Compose service `http://frontend:5173`).

## Testing

API E2E via **pytest** + **pytest-django** (full HTTP stack through DRF). Prefer these over model/serializer unit tests for the same behavior. **Required** for new or changed API behavior — leave `make test` green before considering work done.

```bash
make test          # docker compose run --rm backend uv run pytest
```

Tests use the Compose **Postgres** service (`DATABASE_URL`); pytest-django creates/destroys `test_<dbname>`. Do not use SQLite for tests.

Seed users for the React Playwright suite:

```bash
make seed-e2e
make run           # default LOGIN_2FA_ENABLED=False
# make run-2fa     # for frontend make test-e2e-2fa
```

Credentials: `e2e-admin@example.com` / `e2e-viewer@example.com` with password `e2epass123`.

## Useful commands

All via Docker Compose (Make wrappers):

```bash
make build
make migrate
make makemigrations
make createsuperuser
make schema
make seed-e2e
make test
make up              # db + redis + backend + worker
make run             # db + redis + backend (start worker separately for mail)
make worker
# Dependency adds (inside the backend container):
docker compose run --rm backend uv add <pkg>
docker compose run --rm backend uv add --dev <pkg>
docker compose run --rm backend uv run python manage.py startapp <name> apps/<name>
```
