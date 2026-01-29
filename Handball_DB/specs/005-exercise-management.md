# 005 - Exercise Management

**Priority:** 5
**Status:** COMPLETE

## Description

Implement exercise CRUD with categories and measurement types as specified in projektplan.md section 3.3.

## Acceptance Criteria

### API Endpoints - Exercises

- [ ] `POST /exercises` (coach/admin)
  - Create exercise with name, description, categories, measurement types
  - Owner is the creating coach (or admin)
  - At least one measurement type required
- [ ] `GET /exercises` (coach/admin/player)
  - Returns all active exercises
  - Include categories and measurement types
- [ ] `GET /exercises/{id}` (coach/admin/player)
  - Returns exercise details with categories and measurements
- [ ] `PUT /exercises/{id}` (owner coach or admin)
  - Update name, description, categories
  - Cannot remove measurement types that have data
- [ ] `DELETE /exercises/{id}` (owner coach or admin)
  - Soft delete (archive), not hard delete
  - Historical measurement data preserved

### API Endpoints - Measurement Types
- [ ] `POST /exercises/{id}/measurements` (owner coach or admin)
  - Add measurement type to exercise
  - Input: measurement_type (enum), is_required
- [ ] `DELETE /exercises/{id}/measurements/{type}` (owner coach or admin)
  - Only if no measurements recorded with this type

### Categories
- [ ] Fixed category enum: `schnelligkeit`, `maximalkraft`, `ausdauer`, `koordination`
- [ ] Exercises can have multiple categories
- [ ] `GET /categories` - List all available categories

### Measurement Types
- [ ] Fixed enum: `seconds`, `repetitions`, `kilograms`, `meters`, `centimeters`
- [ ] `GET /measurement-types` - List all available types

### Business Rules
- [ ] Coach can only edit/archive their own exercises
- [ ] Admin can edit/archive any exercise
- [ ] Exercise must have at least 1 measurement type
- [ ] Archived exercises still visible in historical data

### Verification
- [ ] Coach creates exercise → is owner
- [ ] Coach can edit own exercises
- [ ] Coach cannot edit other coach's exercises
- [ ] Admin can edit any exercise
- [ ] Exercise with 0 measurement types → validation error
- [ ] Archive exercise → historical data still accessible

## Dependencies

- Spec 003 (RBAC)

---

**Output when complete:** `<promise>DONE</promise>`
