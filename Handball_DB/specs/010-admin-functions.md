# 010 - Admin Functions & Dev Tools

**Priority:** 10
**Status:** COMPLETE

## Description

Implement admin functionality and development tools as specified in projektplan.md sections 2.1 and 6.

## Acceptance Criteria

### Admin Dashboard
- [ ] Full system overview:
  - Total users by role
  - Total teams, players, coaches
  - Total measurements recorded
- [ ] Quick access to all management functions

### Admin User Management
- [ ] `GET /admin/users` - List all users with roles
- [ ] `POST /admin/users` - Create user with any role
- [ ] `PUT /admin/users/{id}` - Update user details/role
- [ ] `DELETE /admin/users/{id}` - Deactivate user
- [ ] Reset password functionality

### Admin Team Management
- [ ] Full CRUD on all teams (already in spec 004)
- [ ] Assign any player to any team
- [ ] Assign any coach to any team
- [ ] View all teams regardless of assignment

### Admin Exercise Management
- [ ] Edit/archive any exercise (not just own)
- [ ] Reassign exercise ownership

### Development Tools (DEV ONLY)

- [ ] `GET /docs` - Swagger UI (FastAPI default)
- [ ] `GET /redoc` - ReDoc documentation
- [ ] `DELETE /debug/reset` - Reset database
  - Drops and recreates all tables
  - Only available in development mode
  - Protected by admin auth in dev
  - Completely disabled in production
- [ ] Environment variable: `ENVIRONMENT=development|production`

### Hacker Mode UI (DEV ONLY)
- [ ] Dev page at `/dev/hacker-mode`
- [ ] Quick buttons to:
  - Create test admin user
  - Create test coach user
  - Create test player user
  - Generate sample data (teams, exercises, measurements)
- [ ] Only accessible in development mode
- [ ] Not included in production build

### Production Security
- [ ] `/debug/*` routes disabled entirely
- [ ] `/dev/*` routes disabled entirely
- [ ] Swagger/ReDoc optionally disabled
- [ ] HTTPS enforcement reminder in docs

### Verification
- [ ] Admin can create/edit/delete any user
- [ ] Admin can assign any user to any team
- [ ] /debug/reset works in development
- [ ] /debug/reset returns 404 in production mode
- [ ] /dev/hacker-mode not accessible in production

## Dependencies

- Spec 004 (Team Management)
- Spec 005 (Exercise Management)
- All previous specs for full testing

---

**Output when complete:** `<promise>DONE</promise>`
