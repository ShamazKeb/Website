# 004 - Team Management

**Priority:** 4
**Status:** COMPLETE

## Description

Implement team CRUD operations and player/coach assignments as specified in projektplan.md section 3.2.

## Acceptance Criteria

### API Endpoints - Teams

- [ ] `POST /teams` (admin only)
  - Create new team with name and season
  - Returns created team
- [ ] `GET /teams` (coach/admin)
  - Admin: returns all teams
  - Coach: returns only assigned teams
- [ ] `GET /teams/{id}` (coach/admin)
  - Returns team details with player and coach lists
  - Coach can only access assigned teams
- [ ] `PUT /teams/{id}` (admin only)
  - Update team name/season
- [ ] `DELETE /teams/{id}` (admin only)
  - Soft delete or archive team

### API Endpoints - Team Assignments

- [ ] `POST /teams/{id}/players` (admin only)
  - Add player to team
  - Input: player_id
- [ ] `DELETE /teams/{id}/players/{player_id}` (admin only)
  - Remove player from team
- [ ] `POST /teams/{id}/coaches` (admin only)
  - Add coach to team
  - Input: coach_id
- [ ] `DELETE /teams/{id}/coaches/{coach_id}` (admin only)
  - Remove coach from team
- [ ] `GET /teams/{id}/players` (coach/admin)
  - List all players in team
  - Coach must be assigned to team
- [ ] `GET /teams/{id}/coaches` (coach/admin)
  - List all coaches in team

### Business Rules
- [ ] Players can belong to multiple teams
- [ ] Coaches can coach multiple teams
- [ ] Teams can have multiple coaches
- [ ] Removing player from team does NOT delete their measurement data

### Verification
- [ ] Admin can create/update/delete teams
- [ ] Admin can assign/remove players and coaches
- [ ] Coach can only view teams they're assigned to
- [ ] Coach cannot modify team assignments
- [ ] Player cannot access team endpoints

## Dependencies

- Spec 003 (RBAC)

---

**Output when complete:** `<promise>DONE</promise>`
