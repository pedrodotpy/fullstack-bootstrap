# Agent conventions

Rules for humans and coding agents working in these repos.

## Dependencies

- **Backend:** `uv add <package>` / `uv add --dev <package>` only.
- **Frontend:** `yarn add <package>` / `yarn add -D <package>` only.
- Do not hand-edit lockfiles or dependency sections of `pyproject.toml` / `package.json` when the CLI can do the job.

## Django schema and apps

Always use manage.py:

```bash
uv run python manage.py startapp <name> apps/<name>
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py spectacular --file schema.yml
```

Never hand-write or hand-edit migration files unless repairing a broken state **after** CLI use.

## OpenAPI client

After API shape changes:

1. Regenerate `schema.yml` on the Django side.
2. Run `yarn openapi-ts` on the React side.
3. Do not hand-edit `src/shared/api` generated output.

## Permissions and privacy

- Do not add public feature routes or anonymous API endpoints outside the JWT allowlist.
- New ViewSets must require authentication and appropriate model permissions.
- Frontend pages for new resources must live under the authenticated shell and use `Can` / route guards.

## Prefer the User CRUD pattern

Extend `SPECS/04-crud-pattern.md` rather than inventing a one-off API or page structure.

## Testing

- Prefer **end-to-end** tests: pytest API tests on the backend, Playwright (live Django) on the frontend.
- Do **not** add unit tests for behavior already covered by an E2E test in the same project.
- After changing auth or CRUD flows, update the matching E2E specs.
- Backend: `make test` / `make seed-e2e`. Frontend: start Django, then `yarn test:e2e`.
