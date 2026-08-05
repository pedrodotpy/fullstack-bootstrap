---
name: fullstack-crud
description: >-
  Implements full-stack CRUD resources for fullstack-bootstrap projects using
  Django DRF, OpenAPI, and React Query. Use when adding or changing a model,
  ViewSet, schema, typed API client, or CRUD pages/permissions.
---

# Fullstack CRUD

## When to use

Apply this skill whenever the user asks to add a resource, extend User-like CRUD,
change API shape, or wire a new authenticated page to Django model permissions.

## Source of truth

Read these specs before coding (paths are inside the current repo):

1. `SPECS/04-crud-pattern.md` — checklist and User resource map
2. `SPECS/03-auth-and-permissions.md` — JWT + model perms + `<Can>`
3. `SPECS/01-backend.md` / `SPECS/02-frontend.md` — layout and commands
4. `SPECS/05-agent-conventions.md` — tooling rules

Sibling repositories: `{{backend_repo}}` and `{{frontend_repo}}`.

## Backend workflow

```bash
uv run python manage.py startapp <name> apps/<name>
uv run python manage.py makemigrations
uv run python manage.py migrate
# implement model, serializers, viewset, routes.py
make schema
make test
```

Requirements:

- `IsAuthenticated` plus Django model permissions (`view` / `add` / `change` / `delete`)
- Register routes in `apps/<name>/routes.py`
- Never hand-write migrations or hand-edit generated OpenAPI consumers

Settings live under `{{python_id}}/` (never reintroduce a Django package named `config`).

## Frontend workflow

```bash
# after backend schema.yml changes
yarn openapi-ts
```

Then:

1. Add React Query hooks wrapping generated SDK calls
2. Build list/detail/create/edit pages under the authenticated shell
3. Gate UI with `<Can perm="app_label.codename">` and route guards
4. Extend Playwright E2E when auth/CRUD/permissions change — prefer E2E over new unit tests

OpenAPI input defaults to `../{{backend_repo}}/schema.yml`.

## Done checklist

- [ ] API private except JWT obtain/refresh
- [ ] Schema regenerated and client regenerated
- [ ] Permissions enforced server-side and reflected in UI
- [ ] Backend `make test` and/or frontend `yarn test:e2e` updated as needed
