# Agent guidelines ({{backend_repo}})

- Add dependencies with `uv add` / `uv add --dev` only.
- Schema and apps: `uv run python manage.py makemigrations|migrate|startapp|spectacular|createsuperuser|seed_e2e`.
- Never hand-write migration files or hand-edit `uv.lock` when the CLI can do the job.
- After API changes, run `make schema` and regenerate the React OpenAPI client in `../{{frontend_repo}}`.
- Keep the API private: only JWT obtain/refresh are anonymous.
- Prefer pytest API E2E (`make test`) over unit tests for the same behavior; update specs when auth/CRUD changes.
- Follow `./SPECS/` especially `04-crud-pattern.md` and `05-agent-conventions.md`.
- Django settings package is `{{python_id}}` (e.g. `DJANGO_SETTINGS_MODULE={{python_id}}.settings.local`).
