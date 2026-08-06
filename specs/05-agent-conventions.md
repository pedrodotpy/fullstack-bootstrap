# Agent conventions

Rules for humans and coding agents working in these repos.

## Docker-first

Apps and tests run in Docker Compose. Prefer Make targets (`make test`, `make run`, `make dev`, `make test-e2e`) over host `uv` / `yarn`. Add dependencies inside containers:

```bash
docker compose run --rm backend uv add <package>
docker compose run --rm frontend yarn add <package>
```

## Dependencies

- **Backend:** `uv add <package>` / `uv add --dev <package>` only (via Compose as above).
- **Frontend:** `yarn add <package>` / `yarn add -D <package>` only (via Compose as above).
- Do not hand-edit lockfiles or dependency sections of `pyproject.toml` / `package.json` when the CLI can do the job.

## Django schema and apps

Always use manage.py via Make / Compose:

```bash
make makemigrations
make migrate
make createsuperuser
make schema
docker compose run --rm backend uv run python manage.py startapp <name> apps/<name>
```

Never hand-write or hand-edit migration files unless repairing a broken state **after** CLI use.

## OpenAPI client

After API shape changes:

1. `make schema` on the Django side.
2. `make openapi-ts` on the React side.
3. Do not hand-edit `src/shared/api` generated output.

## Permissions and privacy

- Do not add public feature routes or anonymous API endpoints outside the JWT allowlist.
- New ViewSets must require authentication and appropriate model permissions.
- Frontend pages for new resources must live under the authenticated shell and use `Can` / route guards.

## Prefer the User CRUD pattern

Extend `SPECS/04-crud-pattern.md` rather than inventing a one-off API or page structure.

## Testing

Tests are part of the Definition of Done. Do **not** ask whether the user wants tests — write them.

- Prefer **end-to-end** tests: pytest API tests on the backend, Playwright (live Django) on the frontend.
- Do **not** add unit tests for behavior already covered by an E2E test in the same project.
- **Backend:** every new or changed API endpoint / ViewSet behavior must extend `apps/<app>/tests/` and leave `make test` green. Tests use Compose Postgres (pytest-django test database).
- **Frontend:** every new or changed auth, CRUD, or permissions UI flow must extend `e2e/` and leave `make test-e2e` green (Compose stack).
- Backend: `make test` / `make seed-e2e`. Frontend: `make test-e2e` / `make test-e2e-2fa`.
