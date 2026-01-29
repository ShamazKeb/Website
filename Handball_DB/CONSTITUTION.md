# CONSTITUTION.md - Handball-Tracker Project

## 1. Project Vision & Goals

**Vision:** To provide a robust, intuitive, and mobile-optimized web application for handball clubs to effectively track, analyze, and visualize player performance and training progress. This system will empower coaches to make data-driven decisions, administer teams efficiently, and foster player development.

**Goals:**
- Enable comprehensive tracking of player performance data across various exercises.
- Visualize individual and group progress over time, identifying strengths, weaknesses, and potential.
- Streamline administrative tasks for coaches, including team and player management.
- Ensure data security, privacy, and role-based access control.
- Offer a seamless user experience across all devices, particularly smartphones.

## 2. Key Features

- **Role-Based Access Control (RBAC):** Distinct roles for `admin`, `coach`, and `player` with specific permissions.
  - `admin`: Full system access, team/coach/player assignments.
  - `coach`: Manage multiple teams, view/edit player data for their teams, create/edit own exercises, manage team composition.
  - `player`: View own data, input own performance data for exercises.
- **Player & Team Management:**
  - Create, edit, and deactivate players.
  - Assign players and coaches to multiple teams.
- **Exercise Management:**
  - Create and edit exercises with owner-coach association.
  - Categorize exercises (e.g., `schnelligkeit`, `maximalkraft`).
  - Define multiple measurement types per exercise (e.g., `seconds`, `repetitions`, `kilograms`).
- **Performance Data Entry & Tracking:**
  - Record performance data for players per exercise with date/time.
  - Allow coaches to correct historical data.
  - Support multiple entries per day.
- **Analytics & Visualizations:**
  - **Player View:** Dashboard with latest entries, performance development diagrams per exercise, filterable by exercise, period, season.
  - **Coach View:** Activity log for their teams, comprehensive diagrams for multiple players, filterable by team, player, exercise, category, birth year, season. Best lists (e.g., Top 10 per exercise/season).
- **Activity Log:** Track significant system actions (player data entry, coach edits, player creation/deactivation, exercise changes).
- **Security:** Argon2 for password hashing, JWT for authentication, environment variables for sensitive configurations.

## 3. Target Users

- **Handball Coaches:** Primary users for managing teams, tracking player progress, and analyzing training results.
- **Handball Players:** To view their individual performance data and input their own exercise results.
- **Club Administrators:** For overall system management and user assignment.

## 4. Technology Stack

- **Frontend:** React (Mobile-First UI, potentially with a responsive UI library).
- **Backend:** Python with FastAPI.
- **Database:** Relational Database (e.g., PostgreSQL, SQLite for development) managed via SQLAlchemy (ORM).
- **Authentication/Authorization:** Argon2 (password hashing), `python-jose` (JWT).
- **Data Validation:** Pydantic.

## 5. Development Principles (Ralph Wiggum Guidelines)

- **Fresh Context Each Loop:** Each iteration of the Ralph loop starts with a clean slate, preventing context overflow.
- **Shared State on Disk:** State persists between loops via files (specs/, ralph_history.txt, IMPLEMENTATION_PLAN.md).
- **Completion Signal:** The agent outputs `<promise>DONE</promise>` ONLY when all acceptance criteria are verified, tests pass, and changes are committed.
- **Backpressure via Tests:** Tests, lints, and builds act as guardrails; issues must be fixed before completion.
- **Let Ralph Ralph:** Trust the AI to self-identify, self-correct, and self-improve.
- **YOLO Mode (for development/sandboxed environment):** Enable full autonomy for effective operation. (This means Ralph will use `--dangerously-skip-permissions` or equivalent for relevant tools.)
- **Spec-Driven Development:** Focus on clear, testable acceptance criteria in `specs/` files to guide implementation.

## 6. Debug & Development Tools

- Swagger/ReDoc enabled in development (`/docs`, `/redoc`).
- `DELETE /debug/reset` endpoint for development (resets DB, disabled/protected in production).
- "Hacker Mode UI" for quick test user creation and RBAC testing in development.
- Configuration via `.env` files for secrets.

This constitution will serve as the guiding document for all subsequent development tasks performed by Ralph Wiggum.