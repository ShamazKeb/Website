# 006 - Player Measurements

**Priority:** 6
**Status:** COMPLETE

## Description

Implement player performance data recording as specified in projektplan.md section 3.4.

## Acceptance Criteria

### API Endpoints - Recording Measurements

- [x] `POST /measurements` (player/coach/admin)
  - Record measurement for a player on an exercise
  - Input: player_id, exercise_id, values (dict of measurement_type: value), notes (optional)
  - Player can only record for themselves
  - Coach can record for players in their teams
  - Admin can record for any player
  - Validates that all required measurement types have values
- [x] `GET /measurements` (coach/admin)
  - List measurements with filters
  - Filters: player_id, exercise_id, team_id, date_from, date_to
  - Coach can only see measurements from their team's players
- [x] `GET /measurements/{id}` (owner player/coach/admin)
  - Get single measurement details
- [x] `PUT /measurements/{id}` (coach/admin)
  - Update measurement values
  - Only coach (of player's team) or admin can edit
  - Players cannot edit after submission
- [x] `DELETE /measurements/{id}` (admin only)
  - Soft delete, historical data preserved

### API Endpoints - Player's Own Measurements

- [x] `GET /players/me/measurements` (player)
  - List own measurements
  - Filters: exercise_id, date_from, date_to
- [x] `POST /players/me/measurements` (player)
  - Shorthand for recording own measurement

### Business Rules
- [x] Multiple measurements per day allowed
- [x] Coach can correct/edit player measurements
- [x] Deactivating player does NOT delete measurements
- [x] Timestamps recorded automatically (recorded_at)
- [x] Track who created the measurement (created_by_user_id)

### Computed Statistics (on-the-fly)
- [x] `GET /measurements/stats` (coach/admin)
  - Returns: average, best, trend for given filters
  - Filters: player_id, exercise_id, measurement_type, date_range
- [x] `GET /players/{id}/stats` (player for self, coach for team players)
  - Player statistics across exercises

### Verification
- [x] Player records own measurement → saved correctly
- [x] Coach records for team player → saved with coach as creator
- [x] Coach cannot record for player outside their teams
- [x] Multiple measurements on same day → all saved separately
- [x] Statistics calculated correctly

## Dependencies

- Spec 004 (Team Management)
- Spec 005 (Exercise Management)

---

**Output when complete:** `<promise>DONE</promise>`
