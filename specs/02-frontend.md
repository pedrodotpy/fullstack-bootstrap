# Frontend

Repo: `react-boilerplate/` (inside this folder)  
Package manager: **yarn**. Always `yarn add` / `yarn add -D` — never hand-edit `package.json` when the CLI works.

## Stack

- Vite + React + TypeScript
- React Router (auth-first)
- TanStack Query
- shadcn/ui + Tailwind
- Biome (lint + format)
- `@hey-api/openapi-ts` generated client under `src/shared/api`

## Layout

```
react-boilerplate/
  package.json
  Makefile
  Dockerfile
  Dockerfile.playwright
  docker-compose.yml
  docker-compose.e2e.yml
  vite.config.ts
  biome.json
  openapi-ts.config.ts
  components.json
  .env.example
  e2e/
  src/
    main.tsx
    app/router.tsx
    app/providers.tsx
    shared/
      api/              # generated — do not hand-edit
      api/setup.ts      # JWT interceptors
      auth/
      permissions/
      components/ui/    # shadcn
    features/
      auth/pages/
        LoginPage.tsx          # password + optional OTP step
        ForgotPasswordPage.tsx
        ResetPasswordPage.tsx
      users/
        api.ts
        pages/
        components/
```

## Env

```
VITE_API_BASE_URL=http://localhost:8000
OPENAPI_SCHEMA_PATH=/django-boilerplate/schema.yml
```

Host browser uses `localhost` for the API. Playwright E2E Compose sets `VITE_API_BASE_URL=http://backend:8000`. Schema path is the sibling repo mounted at `/django-boilerplate` inside the frontend container.

Generated SDK paths already include `/api/v1/...`, so the base URL is the Django origin only.
## OpenAPI client workflow

1. Backend: `make schema`
2. Frontend: `make openapi-ts`
3. Restore `src/shared/api/setup.ts` if the generator wiped it (hand-maintained JWT interceptors live next to generated files)
4. Commit the generated `src/shared/api` so clones work without regenerating
5. Feature modules wrap generated SDK calls in React Query hooks

Do **not** hand-edit generated files. Change the backend, regenerate schema, regenerate client.

## Auth-first router

| Route | Access |
|-------|--------|
| `/login` | Public (inline OTP step when 2FA is on) |
| `/forgot-password` | Public |
| `/reset-password` | Public |
| everything else | Authenticated shell |

- Unauthenticated → `/login?next=...`
- Authenticated hitting `/login` → app home
- `/` → users list (post-login home)
- No public landing page / no self-registration

## Permissions UI

- `useMe()` loads `/auth/me/` permissions into Query cache
- `<Can perm="users.add_user">` for action visibility
- Route guards for page-level model perms

## Testing

Browser E2E via **Playwright** against a **live Django API** (preferred over Vitest/RTL for auth, CRUD, and permission UI). **Required** for new or changed auth/CRUD/permissions UI — leave `make test-e2e` green before considering work done.

```bash
make test-e2e       # Compose: Postgres + Django + Vite + Playwright
make test-e2e-2fa   # same stack with LOGIN_2FA_ENABLED=True
```

OTP helpers read codes from Postgres (`E2E_DATABASE_URL`) on the Compose network. Do **not** add unit tests for flows already covered by these E2E specs.

## Useful commands

All via Docker Compose (Make wrappers):

```bash
make build
make dev
make lint
make openapi-ts
make test-e2e
docker compose run --rm frontend yarn add <pkg>
docker compose run --rm frontend yarn add -D <pkg>
```
