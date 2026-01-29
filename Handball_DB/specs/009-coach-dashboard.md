# 009 - Coach Dashboard & Analytics

**Priority:** 9
**Status:** COMPLETE

## Description

Implement coach-facing UI with analytics as specified in projektplan.md section 4.2. Mobile-first design.

## Acceptance Criteria

### Coach Dashboard
- [ ] Activity log feed of recent team actions
- [ ] Quick links to:
  - Team management
  - Exercise management
  - Player data
  - Analytics/charts

### Team Overview
- [ ] List of coach's teams
- [ ] For each team:
  - Player count
  - Recent activity summary
  - Quick link to team details

### Player Management (within teams)
- [ ] View all players in selected team
- [ ] Player details: name, birth year, active status
- [ ] View player's measurement history
- [ ] Add/edit measurements for players
- [ ] Create new player (linked to team)
- [ ] Deactivate player (not delete)

### Exercise Management
- [ ] List coach's exercises
- [ ] Create new exercise with categories and measurement types
- [ ] Edit exercise details
- [ ] Archive exercise

### Analytics & Charts
- [ ] Multi-player comparison charts
- [ ] Filters:
  - Team
  - Multiple players (multi-select)
  - Exercise
  - Category
  - Birth year (Jahrgang)
  - Season
  - Date range
- [ ] Chart types:
  - Line chart: Progress over time
  - Bar chart: Comparison across players
  - Leaderboard: Top 10 per exercise

### Leaderboards
- [ ] Top performers per exercise
- [ ] Filter by season, team, birth year
- [ ] Show best value and date achieved

### UI/UX Requirements
- [ ] Mobile-optimized
- [ ] Intuitive navigation for busy coaches
- [ ] Quick data entry (minimal clicks)
- [ ] German language labels

### Verification
- [ ] Coach logs in → sees dashboard with teams
- [ ] Coach can add measurement for player
- [ ] Coach can create/edit exercises
- [ ] Multi-player comparison chart works
- [ ] Leaderboard displays top performers
- [ ] All filters work correctly

## Dependencies

- Spec 008 (Player Dashboard - shared components)

---

**Output when complete:** `<promise>DONE</promise>`
