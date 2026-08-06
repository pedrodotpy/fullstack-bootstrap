# CRUD pattern

Reference implementation: **User**. Follow this checklist for every new resource.

## Backend checklist

1. **Model** — preferably subclass `common.models.IndexedTimeStampedModel`.
2. **`makemigrations` / `migrate`** via `manage.py` (never hand-write migrations).
3. **Serializer(s)** — read serializer; write serializer with validation; write-only secrets (e.g. password).
4. **ViewSet** — `ModelViewSet` (or subset); `IsAuthenticated` + model permissions including `view`.
5. **`routes.py`** — register `{ regex, viewset, basename }`.
6. **Filters** — search / ordering / pagination (limit-offset) as needed.
7. **Schema** — `uv run python manage.py spectacular --file schema.yml`.
8. **Tests** — pytest API E2E under `apps/<app>/tests/` covering list/create/retrieve/update/destroy and permission denials; `make test` green.

## Frontend checklist

1. **Regenerate client** — `yarn openapi-ts` (reads sibling `schema.yml` or configured path).
2. **Feature API module** — React Query hooks wrapping generated SDK (`useUsersQuery`, `useUserQuery`, `useCreateUser`, …). Query keys per resource.
3. **List page** — table + limit/offset pagination; create button in `<Can perm="…add_…">`.
4. **Detail page** — fields; edit/delete gated by change/delete perms.
5. **Create / Edit pages** — shared form component; map DRF `{ field: ["msg"] }` errors to inputs.
6. **Mutations** — invalidate list/detail query keys on success.
7. **Routes** — under authenticated shell; perm guards for view/add/change.
8. **Tests** — Playwright under `e2e/` for list/create (and permissions when gated); `yarn test:e2e` green against live Django.

## User resource map

| Concern | Location |
|---------|----------|
| Model | `apps/users/models.py` |
| API | `apps/users/api/` |
| Routes | `apps/users/routes.py` |
| Schema | `schema.yml` |
| Generated client | `react-boilerplate/src/shared/api/` |
| Hooks | `features/users/api.ts` |
| Pages | `features/users/pages/` |

## Error contract

- Validation: HTTP 400 with field keys matching serializer fields.
- Auth: 401 → client refresh / login redirect.
- Forbidden: 403 → show forbidden state; do not treat as logout unless 401.

## What “easy CRUD” means here

No resource scaffold CLI in v1. Copy the User feature end-to-end and rename. The OpenAPI client removes hand-written URL/type drift; Query hooks + shadcn form/table remove page boilerplate.
