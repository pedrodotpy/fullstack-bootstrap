# Agent guidelines ({{backend_repo}})

- Development is **Docker-first**: use Make / `docker compose` for migrate, run, schema, and tests.
- Add dependencies with `docker compose run --rm backend uv add` / `uv add --dev` only.
- Schema and apps: `make migrate|makemigrations|schema|createsuperuser|seed_e2e` or `docker compose run --rm backend uv run python manage.py …`.
- Never hand-write migration files or hand-edit `uv.lock` when the CLI can do the job.
- After API changes, run `make schema` and regenerate the React OpenAPI client in `../{{frontend_repo}}`.
- Keep the API private: only JWT obtain/refresh (and auth OTP endpoints) are anonymous.
- **Must** add/update pytest API E2E under `apps/<app>/tests/` for new/changed API behavior; leave `make test` green. Do not ask whether tests are wanted.
- Prefer pytest API E2E over unit tests for the same behavior. Tests use Compose Postgres.
- Follow `./SPECS/` especially `04-crud-pattern.md` and `05-agent-conventions.md`.
- Django settings package is `{{python_id}}` (e.g. `DJANGO_SETTINGS_MODULE={{python_id}}.settings.local`).
