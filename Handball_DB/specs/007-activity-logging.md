# 007 - Activity Logging

**Priority:** 7
**Status:** COMPLETE

## Description

Implement activity logs for audit trail as specified in projektplan.md section 3.5.

## Acceptance Criteria

### Activity Log Model
- [ ] Action types enum:
  - `player_entry` - Player records own measurement
  - `coach_add_measurement` - Coach adds measurement for player
  - `coach_edit_measurement` - Coach edits measurement
  - `coach_create_player` - Coach creates new player
  - `coach_deactivate_player` - Coach deactivates player
  - `coach_edit_exercise` - Coach edits exercise
  - `admin_action` - Generic admin action

### Automatic Logging
- [ ] Log created when player records measurement
- [ ] Log created when coach adds/edits measurement
- [ ] Log created when coach creates/deactivates player
- [ ] Log created when coach edits exercise
- [ ] Log includes: user_id, timestamp, description, target IDs

### API Endpoints

- [ ] `GET /activity-logs` (coach/admin)
  - Coach sees logs from their teams only
  - Admin sees all logs
- [ ] Filters:
  - `user_id` - Who performed the action
  - `player_id` - Affected player
  - `team_id` - Affected team
  - `exercise_id` - Affected exercise
  - `action_type` - Type of action
  - `date_from`, `date_to` - Time range
- [ ] Pagination: limit, offset
- [ ] Sort by timestamp (newest first by default)

### Log Entry Format
- [ ] Timestamp (ISO 8601)
- [ ] Action type
- [ ] User who performed action (name + role)
- [ ] Short description (auto-generated or custom)
- [ ] Related entities (player name, exercise name, team name if applicable)

### Verification
- [ ] Player records measurement → log entry created
- [ ] Coach edits measurement → log entry with both user and player
- [ ] Coach creates player → log entry created
- [ ] Filters work correctly
- [ ] Coach cannot see logs from other teams

## Dependencies

- Spec 006 (Player Measurements)

---

**Output when complete:** `<promise>DONE</promise>`
