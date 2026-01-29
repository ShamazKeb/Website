# 002 - User Authentication

**Priority:** 2
**Status:** COMPLETE

## Description

Implement secure user authentication with Argon2 password hashing and JWT tokens as specified in projektplan.md section 5.

## Acceptance Criteria

### Password Security
- [ ] Implement Argon2 password hashing using `passlib[argon2]`
- [ ] Create utility functions: `hash_password(plain)` and `verify_password(plain, hashed)`
- [ ] No plaintext passwords stored anywhere

### JWT Authentication
- [ ] Implement JWT token creation using `python-jose`
- [ ] Token payload includes: `sub` (user email), `exp` (expiration), `role`
- [ ] Default token expiration: 24 hours (configurable via .env)
- [ ] Create `create_access_token(data: dict)` utility

### API Endpoints
- [ ] `POST /auth/register` - Create new user account
  - Input: email, password, role (optional, default: player)
  - Validates email format and password strength
  - Returns user info (no password)
- [ ] `POST /auth/login` - Authenticate and get token
  - Input: email, password
  - Returns: `{ access_token, token_type: "bearer" }`
- [ ] `GET /auth/me` - Get current user info
  - Requires valid JWT in `Authorization: Bearer <token>` header
  - Returns user profile based on role

### Pydantic Schemas
- [ ] `UserCreate` - registration input
- [ ] `UserLogin` - login input
- [ ] `UserResponse` - user output (no password)
- [ ] `Token` - JWT response

### Verification
- [ ] Register a new user → password stored as Argon2 hash
- [ ] Login with correct credentials → receive valid JWT
- [ ] Login with wrong password → 401 Unauthorized
- [ ] Access /auth/me with valid token → returns user info
- [ ] Access /auth/me without token → 401 Unauthorized

## Dependencies

- Spec 001 (Project Setup & Database Schema)

---

**Output when complete:** `<promise>DONE</promise>`
