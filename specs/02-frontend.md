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
  vite.config.ts
  biome.json
  openapi-ts.config.ts
  components.json
  .env.example
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
      auth/pages/LoginPage.tsx
      users/
        api.ts
        pages/
        components/
```

## Env

```
VITE_API_BASE_URL=http://localhost:8000
OPENAPI_SCHEMA_PATH=../django-boilerplate/schema.yml
```

Generated SDK paths already include `/api/v1/...`, so the base URL is the Django origin only.
## OpenAPI client workflow

1. Backend: `make schema` (or `manage.py spectacular --file schema.yml`)
2. Frontend: `yarn openapi-ts`
3. Commit the generated `src/shared/api` so clones work without regenerating
4. Feature modules wrap generated SDK calls in React Query hooks

Do **not** hand-edit generated files. Change the backend, regenerate schema, regenerate client.

## Auth-first router

| Route | Access |
|-------|--------|
| `/login` | Public only |
| everything else | Authenticated shell |

- Unauthenticated → `/login?next=...`
- Authenticated hitting `/login` → app home
- `/` → users list (post-login home)
- No public landing page

## Permissions UI

- `useMe()` loads `/auth/me/` permissions into Query cache
- `<Can perm="users.add_user">` for action visibility
- Route guards for page-level model perms

## Testing

Browser E2E via **Playwright** against a **live Django API** (preferred over Vitest/RTL for auth, CRUD, and permission UI).

Prerequisites:

1. Backend running on `:8000` with migrations applied
2. `make seed-e2e` in `django-boilerplate/` (admin + viewer + extra users)
3. `VITE_API_BASE_URL=http://localhost:8000` in `.env`
4. Browsers installed once: `yarn playwright install chromium`

```bash
yarn test:e2e       # or: make test-e2e
yarn test:e2e:ui
```

Playwright starts `yarn dev` on `:5173` (reuses an existing Vite server when not in CI). Specs live under `e2e/`.

Do **not** add unit tests for flows already covered by these E2E specs.

## Useful commands

```bash
yarn add <pkg>
yarn add -D <pkg>
yarn dev
yarn openapi-ts
yarn biome check --write .
yarn test:e2e
```
