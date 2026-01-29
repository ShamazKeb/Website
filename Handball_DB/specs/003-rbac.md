# 003 - Role-Based Access Control (RBAC)

**Priority:** 3
**Status:** COMPLETE

## Description

Implement FastAPI dependencies for role-based access control as specified in projektplan.md section 5.2.

## Acceptance Criteria

### FastAPI Dependencies
- [ ] `get_current_user(token)` - Decode JWT and return current user
  - Raises 401 if token invalid or expired
- [ ] `get_current_admin(user)` - Verify user has admin role
  - Raises 403 if not admin
- [ ] `get_current_coach(user)` - Verify user has coach role
  - Raises 403 if not coach
- [ ] `get_current_coach_or_admin(user)` - Verify user is coach OR admin
  - Raises 403 if neither
- [ ] `get_current_player(user)` - Verify user has player role
  - Raises 403 if not player

### Coach Team Context
- [ ] Create `get_coach_teams(coach_user)` helper
  - Returns list of team IDs the coach is assigned to
- [ ] Create `verify_coach_has_team_access(coach, team_id)` helper
  - Raises 403 if coach not assigned to team

### Player Self-Access
- [ ] Create `verify_player_self_access(current_user, target_player_id)` helper
  - Raises 403 if player tries to access another player's data

### Error Responses
- [ ] 401 Unauthorized - Invalid/missing/expired token
- [ ] 403 Forbidden - Insufficient permissions
- [ ] Consistent error response schema: `{ detail: string }`

### Verification
- [ ] Admin can access admin-only endpoints
- [ ] Coach can access coach endpoints but not admin endpoints
- [ ] Player can only access own data
- [ ] Coach can only access data from assigned teams
- [ ] All protected endpoints return 401 without token
- [ ] All role-restricted endpoints return 403 with wrong role

## Dependencies

- Spec 002 (User Authentication)

---

**Output when complete:** `<promise>DONE</promise>`
