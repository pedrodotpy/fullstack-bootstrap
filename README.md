# fullstack-bootstrap

Deterministic one-command bootstrap for sibling Django + React repositories.

Inspired by [Vinta's django-react-boilerplate](https://github.com/vintasoftware/django-react-boilerplate) template flow, adapted to a **three-repository** layout: pinned backend boilerplate, pinned frontend boilerplate, and this tooling repo (CLI + specs + agent support).

## Usage

Client name is the only runtime parameter:

```bash
uvx --from git+https://github.com/<org>/fullstack-bootstrap.git fullstack-bootstrap "Acme Corp"
```

From a local checkout:

```bash
cd fullstack-bootstrap
uv sync --group dev
uv run fullstack-bootstrap "Acme Corp"
```

### Derived names

| Input | Derived |
|-------|---------|
| Display | `Acme Corp` |
| Slug | `acme-corp` |
| Python package | `acme_corp` |
| Backend repo | `acme-corp-backend/` |
| Frontend repo | `acme-corp-frontend/` |
| API title | `Acme Corp API` |

Output (current working directory):

```text
acme-corp-backend/   # git init -b main, no commit
acme-corp-frontend/  # git init -b main, no commit
```

## What the command does

1. Downloads pinned backend/frontend zip archives from [`template-sources.toml`](template-sources.toml)
2. Verifies SHA-256 checksums
3. Extracts securely (rejects traversal/symlinks; strips GitHub root folder; omits `.venv`, `node_modules`, `.env`, etc.)
4. Brands both trees (repo/package names, Django settings package rename `config` → `<python_id>`, sibling OpenAPI paths, docs, API/UI titles)
5. Installs tailored `SPECS/`, `.cursor/rules/`, `.cursor/skills/fullstack-crud/`, and `AGENTS.md` into **both** repos
6. Initializes Git on `main` without commits or remotes

### Explicitly not done

Dependency install, `.env` creation, migrations, OpenAPI client regeneration, and first commit. Run those after bootstrap.

## Post-generation setup

```bash
# Backend
cd acme-corp-backend
cp .env.example .env
cp acme_corp/settings/local.py.example acme_corp/settings/local.py
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver

# Frontend (separate terminal)
cd ../acme-corp-frontend
cp .env.example .env
yarn install
yarn dev
```

## Pinning template sources

[`template-sources.toml`](template-sources.toml) currently uses `UNSET` placeholders. After the boilerplates are published, fill:

```toml
[backend]
url = "https://github.com/<org>/django-boilerplate/archive/<full-commit-sha>.zip"
commit = "<full-commit-sha>"
sha256 = "<sha256-of-zip-bytes>"

[frontend]
url = "https://github.com/<org>/react-boilerplate/archive/<full-commit-sha>.zip"
commit = "<full-commit-sha>"
sha256 = "<sha256-of-zip-bytes>"
```

Compute the checksum:

```bash
curl -L "$URL" | sha256sum
```

Until pins are set, the CLI exits with a configuration error. Unit tests use local fixture archives and do not need network access. The real-archive contract test activates automatically once URLs are no longer `UNSET`.

### Updating pins

1. Publish/tag new boilerplate commits
2. Update `url`, `commit`, and `sha256` in `template-sources.toml`
3. Run `uv run pytest`
4. Commit the pin bump in this repo

## Agent support

Canonical sources live in this repository:

- [`specs/`](specs/) — moved from the workspace `SPECS/` directory (unchanged content)
- [`support/agents/`](support/agents/) — per-repo `AGENTS.md` overlays
- [`support/cursor/rules/`](support/cursor/rules/) — Cursor rules
- [`support/cursor/skills/fullstack-crud/`](support/cursor/skills/fullstack-crud/) — CRUD workflow skill

Generated client repos receive tailored copies so either sibling is agent-ready.

## Development

```bash
uv sync --group dev
uv run pytest
```

## Layout

```text
fullstack-bootstrap/
  pyproject.toml
  template-sources.toml
  specs/
  support/
  src/fullstack_bootstrap/
  tests/
```
