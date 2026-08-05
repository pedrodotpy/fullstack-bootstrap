# Auth and permissions

## Principles

1. The product is **private**. Anonymous access is limited to JWT obtain/refresh and the SPA login page.
2. Frontend never invents permissions — it consumes `GET /api/v1/auth/me/`.
3. v1 is **model-level** Django permissions only.

## JWT flow

```
Login form (email + password)
  → POST /api/v1/auth/token/
  → store access (memory) + refresh (localStorage)
  → prefetch GET /api/v1/auth/me/
  → redirect to next or /

API request
  → Authorization: Bearer <access>

401
  → POST /api/v1/auth/token/refresh/ once
  → retry original request
  → if refresh fails → clear tokens → /login?next=...

Logout
  → POST /api/v1/auth/logout/ (blacklist refresh)
  → clear tokens + Query cache → /login
```

## Anonymous allowlist (API)

- `POST /api/v1/auth/token/`
- `POST /api/v1/auth/token/refresh/`

All other endpoints require authentication. DRF default permission: `IsAuthenticated`.

## `/me` payload

```json
{
  "id": 1,
  "email": "admin@example.com",
  "permissions": [
    "users.view_user",
    "users.add_user",
    "users.change_user",
    "users.delete_user"
  ]
}
```

`permissions` comes from `user.get_all_permissions()` (includes group-granted perms). Superusers receive all permissions Django would grant them.

## Model permissions on ViewSets

Use DRF permission classes that map HTTP actions to Django model perms, including **view**:

| Action | Permission |
|--------|------------|
| list, retrieve | `users.view_user` |
| create | `users.add_user` |
| update, partial_update | `users.change_user` |
| destroy | `users.delete_user` |

## Frontend gates

```tsx
<Can perm="users.add_user">
  <Link to="/users/new">Create user</Link>
</Can>
```

Route-level: wrap authenticated routes so missing `users.view_user` cannot open the list page (show forbidden / redirect).

## Testing tip

Prefer the Playwright E2E suite in `react-boilerplate/e2e/` (especially `users.permissions.spec.ts`) and the pytest API permission matrix in `django-boilerplate/apps/users/tests/`.

Seed with `make seed-e2e` in the Django repo: `e2e-viewer@example.com` has only `users.view_user`; `e2e-admin@example.com` is a superuser. Superuser is fine for smoke/CRUD paths; the viewer covers hide/deny UI and Forbidden routes.
