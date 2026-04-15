# Community Operations Platform Frontend (Vue 3)

This is the frontend for the **Community Operations Platform**.

## What Is Integrated

The UI is now wired for real backend integration with:

- JWT auth flow (`/auth/login`, `/auth/register`, `/auth/logout`)
- Manager task management (`/tasks` CRUD + status)
- Staff assigned tasks (`/tasks/assigned`, `/tasks/:id/status`)
- Notifications (`/notifications`, `/notifications/:id/read`)
- Dashboard analytics (`/dashboard/manager`, `/dashboard/staff`)
- Manager user account management (`/users` + update/activate/deactivate/hard-delete)

## Tech

- Vue 3 (Composition API)
- Vue Router
- Pinia
- Plain CSS (scoped component styles + shared global stylesheet)
- Axios (with request/response interceptors)
- Chart.js (`vue-chartjs`)

## Setup

1. Install dependencies:

```bash
npm install
```

2. Configure backend base URL:

- Copy `.env.example` to `.env`
- Set:

```env
VUE_APP_API_BASE_URL=http://127.0.0.1:5000/api
```

3. Run dev server:

```bash
npm run dev
```

App runs at `http://localhost:8080/`.

## Auth and Routing Behavior

- JWT token is auto-attached in `Authorization` header.
- On `401`, token is cleared and user is redirected to `/login`.
- Role-aware route guards:
  - Manager/Admin -> `/manager/*`
  - Staff -> `/staff/*`

## Manager User Manage-ment

In **Manager Dashboard -> User Management**, manager can:

- Search users
- Create user accounts
- Edit user profile/role
- Activate/deactivate users
- Hard-delete users (if backend endpoint is available)

## Important Backend Endpoint Notes

This frontend expects these endpoints to exist:

- `GET /users`
- `POST /users`
- `PUT /users/:id`
- `PUT /users/:id/terminate` or fallback `PATCH /users/:id { is_active: false }`
- `PUT /users/:id/activate` or fallback `PATCH /users/:id { is_active: true }`
- `DELETE /users/:id/hard`

If your backend uses different paths/field names, adjust mappings in:

- `src/services/userService.js`
- `src/services/taskService.js`
- `src/services/dashboardService.js`
