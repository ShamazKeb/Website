# 008 - Player Dashboard & UI

**Priority:** 8
**Status:** COMPLETE

## Description

Implement player-facing UI as specified in projektplan.md section 4.1. Mobile-first design.

## Acceptance Criteria

### Frontend Setup
- [ ] React or Vue.js frontend application
- [ ] Responsive, mobile-first design
- [ ] Connect to FastAPI backend via REST API
- [ ] JWT token stored securely (httpOnly cookie or secure storage)

### Player Login
- [ ] Login page with email/password
- [ ] Error messages for invalid credentials
- [ ] Redirect to dashboard after login
- [ ] Logout functionality

### Player Dashboard
- [ ] Welcome message with player name
- [ ] Quick stats overview:
  - Total measurements recorded
  - Last activity date
  - Recent improvements
- [ ] List of recent measurements (last 10)

### Measurement Entry
- [ ] Form to record new measurement
  - Select exercise from dropdown
  - Dynamic fields based on exercise's measurement types
  - Optional notes field
  - Submit button
- [ ] Success/error feedback
- [ ] Redirect to history or dashboard after submit

### Performance History
- [ ] List view of all measurements
- [ ] Filters:
  - By exercise
  - By date range (calendar picker)
  - By season
- [ ] Chart: Performance trend over time per exercise
  - Line chart showing improvement/decline
  - Toggle between measurement types

### UI/UX Requirements
- [ ] Mobile-optimized (touch-friendly buttons, readable fonts)
- [ ] Fast load times
- [ ] Clear navigation
- [ ] German language support (labels in German)

### Verification
- [ ] Player can log in and see dashboard
- [ ] Player can record a measurement
- [ ] Player can view history with filters
- [ ] Chart displays correctly
- [ ] Works well on mobile viewport (375px width)

## Dependencies

- Spec 002 (Authentication)
- Spec 006 (Player Measurements)

---

**Output when complete:** `<promise>DONE</promise>`
