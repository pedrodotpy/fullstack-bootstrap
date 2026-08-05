# Overview

Private, login-gated Django REST + React SPA boilerplate as **two sibling repos inside this folder**. The root (`django-react-boilerplate`) holds SPECS + both repos and is **not** itself a git repository (each subfolder has its own git repo).

## Repos

| Path | Role |
|------|------|
| `django-boilerplate/` | Django + DRF + JWT API |
| `react-boilerplate/` | Vite SPA (Yarn, shadcn, Biome, TanStack Query) |

## Goals

- Make CRUD pages easy: model → ViewSet → OpenAPI → typed client → React Query hooks → shadcn pages.
- Integrate the frontend with Django’s **model-level** permissions (`view` / `add` / `change` / `delete`).
- No public product UI — only `/login` and JWT token endpoints are anonymous.

## Decisions

- **Auth:** JWT (`djangorestframework-simplejwt` + refresh blacklist). No SSO.
- **User:** custom email-based `User` (`USERNAME_FIELD = "email"`).
- **API contract:** `drf-spectacular` → `schema.yml` → `@hey-api/openapi-ts` client in the React repo.
- **Example resource:** full User CRUD (list / detail / create / edit) gated by model perms.

## Inspired by Vinta (adopted vs not)

**Adopted:** email User, `IndexedTimeStampedModel`, settings split, `DATABASE_URL`, DRF `IsAuthenticated` + limit/offset pagination, app `routes.py` registry, spectacular + openapi-ts, 401 → login with `next`, Ruff/pre-commit, Makefiles.

**Not adopted:** monorepo/Webpack/django-webpack-loader, Poetry/pnpm, session+CSRF as primary SPA auth, admin-as-login, Celery/Redis/defender/CSP/Sentry/Render as v1 requirements, public Home page.

## Local run (summary)

```bash
# Backend
cd django-boilerplate
cp .env.example .env
cp config/settings/local.py.example config/settings/local.py
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver

# Frontend (separate terminal)
cd react-boilerplate
cp .env.example .env
yarn install
yarn dev
```

Open `http://localhost:5173/login`, sign in with the superuser email/password.

## Tests (summary)

```bash
# Backend API E2E
cd django-boilerplate && make test

# Frontend browser E2E (Django must be running + seeded)
cd django-boilerplate && make seed-e2e && make run   # terminal 1
cd react-boilerplate && yarn test:e2e               # terminal 2
```

## Out of scope

- Public landing/marketing pages and self-service signup
- Django admin as product UI
- SSO, object-level permissions, resource scaffold CLI
- Celery/Redis/Docker/Render as required defaults
