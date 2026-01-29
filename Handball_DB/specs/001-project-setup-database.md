# 001 - Project Setup & Database Schema

**Priority:** 1 (Must be completed first)
**Status:** COMPLETE

## Description

Initialize the Handball Database project with the foundational structure, dependencies, and complete database schema based on the projektplan.md specification.

## Acceptance Criteria

### Project Structure
- [ ] Create Python project with FastAPI
- [ ] Set up virtual environment with requirements.txt
- [ ] Configure .env.example with required environment variables:
  - `SECRET_KEY`
  - `DATABASE_URL`
  - `ALGORITHM` (default: HS256)
- [ ] Create main.py with FastAPI app initialization
- [ ] Set up SQLAlchemy with async support

### Database Models (SQLAlchemy)
- [ ] `users` table:
  - id, email (unique), password_hash, role (enum: admin/coach/player), created_at, updated_at
- [ ] `players` table (1-1 with users where role=player):
  - id, user_id (FK), first_name, last_name, birth_year, is_active, created_at
- [ ] `coaches` table (1-1 with users where role=coach):
  - id, user_id (FK), first_name, last_name, created_at
- [ ] `teams` table:
  - id, name, season, created_at
- [ ] `team_players` (M2M):
  - team_id (FK), player_id (FK)
- [ ] `team_coaches` (M2M):
  - team_id (FK), coach_id (FK)
- [ ] `exercises` table:
  - id, owner_coach_id (FK), name, description, is_active, created_at
- [ ] `categories` enum: schnelligkeit, maximalkraft, ausdauer, koordination
- [ ] `exercise_categories` (M2M):
  - exercise_id (FK), category
- [ ] `measurement_types` enum: seconds, repetitions, kilograms, meters, centimeters
- [ ] `exercise_measurements` table:
  - exercise_id (FK), measurement_type, is_required
- [ ] `player_measurements` table:
  - id, player_id (FK), exercise_id (FK), recorded_at, notes, created_by_user_id (FK)
  - Dynamic value columns based on measurement types
- [ ] `activity_logs` table:
  - id, action_type, user_id (FK), target_player_id, target_exercise_id, target_team_id, description, created_at

### Verification
- [ ] Run `alembic init` and create initial migration
- [ ] Migration applies successfully to SQLite database
- [ ] All foreign key relationships work correctly
- [ ] Indexes created for frequently queried columns

## Technical Notes

- Use SQLite for development (DATABASE_URL=sqlite:///./handball.db)
- Use Alembic for migrations
- All models inherit from a Base class with common fields

## Dependencies

None - this is the first spec.

---

**Output when complete:** `<promise>DONE</promise>`
