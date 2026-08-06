# Auth and permissions

## Principles

1. The product is **private**. Anonymous access is limited to JWT auth endpoints and the SPA auth pages (`/login`, `/forgot-password`, `/reset-password`).
2. Frontend never invents permissions — it consumes `GET /api/v1/auth/me/`.
3. v1 is **model-level** Django permissions only.
4. There is **no self-registration**. Users are created by staff via the users CRUD / admin.

## JWT flow (LOGIN_2FA_ENABLED=false, default)

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

## Login 2FA (LOGIN_2FA_ENABLED=true)

Env toggle only. When **off**, never ask for a code. When **on**, ask on **every** login.

```
Login form (email + password)
  → POST /api/v1/auth/token/
  → 202 { challenge_id, destination }  (no JWT yet)
  → email 6-digit code (10 min expiry)
  → POST /api/v1/auth/verify-code/ { challenge_id, code }
  → store access + refresh → /me → redirect

Resend: POST /api/v1/auth/resend-code/ { challenge_id }
```

## Forgot / reset password

Always available (independent of `LOGIN_2FA_ENABLED`).

```
Forgot page
  → POST /api/v1/auth/forgot-password/ { email }
  → always 204 (anti-enumeration)
  → if user exists: email 6-digit code (purpose=password_reset, 10 min)

Reset page
  → POST /api/v1/auth/reset-password/
      { email, code, new_password, confirm_password }
  → 204 on success → /login
```

OTP rows live in `users.EmailAuthCode` (`challenge_id`, `code`, `purpose`, `expiration_date`, `validated_at`). Creating a new code invalidates prior open codes for the same user+purpose.

## Anonymous allowlist (API)

- `POST /api/v1/auth/token/`
- `POST /api/v1/auth/token/refresh/`
- `POST /api/v1/auth/verify-code/`
- `POST /api/v1/auth/resend-code/`
- `POST /api/v1/auth/forgot-password/`
- `POST /api/v1/auth/reset-password/`

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

**Must** keep Playwright (`react-boilerplate/e2e/`, especially `auth.spec.ts`, `auth.2fa.spec.ts`, `users.permissions.spec.ts`) and pytest API coverage (`django-boilerplate/apps/users/tests/`) in sync with auth/permission changes. Do not ask whether tests are wanted.

Seed with `make seed-e2e` in the Django repo: `e2e-viewer@example.com` has only `users.view_user`; `e2e-admin@example.com` is a superuser. Superuser is fine for smoke/CRUD paths; the viewer covers hide/deny UI and Forbidden routes. For login-2FA browser tests use `make run-2fa` + frontend `make test-e2e-2fa`.
