# Task Management Project – Current Status

## Domain (clean, framework-free)

### Value Objects
- **Email**: normalizes (trim + lowercase) and validates format; raises `InvalidEmail`.
- **UserId**: wraps a `uuid.UUID` with `UserId.new()` factory.
- **PasswordHash**: opaque wrapper; rejects obviously invalid hashes.

### Entities
- **User**:  
  Fields: `id: UserId`, `email: Email`, `password_hash: PasswordHash`, `status: UserStatus`, `created_at`.  
  Behaviors: `change_email`, `change_password`, `ensure_can_authenticate` (raises `UserLocked`), `lock`, `issue_refresh_token(...)`.
- **RefreshToken**:  
  Fields: `id: UUID`, `user_id: UserId`, `issued_at`, `expires_at`, `revoked_at`.  
  Behaviors: `ensure_active()` (raises `TokenExpired`), `revoke()`.

### Errors (domain)
- `DomainError` base; specialized: `UserLocked`, `TokenExpired`, `InvalidEmail`.

### Invariants
- User blocked cannot authenticate.
- Email is always normalized and valid at creation.
- Refresh token only valid if not expired or revoked.

---

## Application (use cases + ports/contracts)

### Ports
- `UserRepository`: `add`, `save`, `get_by_id`, `get_by_email`, `exists_by_email`, `list`.
- `PasswordHasher`: `hash`, `verify`.
- (Planned) `RefreshTokenRepository`, `AccessTokenEncoder`.

### Use Cases (User CRUD)
- `CreateUser`: Creates user with validated email and hashed password, prevents duplicates.
- `GetUser`, `ListUsers`: Read by id and list with pagination.
- `UpdateUserEmail`: Changes email with validation and duplication prevention.
- `UpdateUserPassword`: Changes password via `PasswordHasher`.
- `SetUserStatus`: Locks/unlocks user.
- `DeleteUser`: Soft delete by locking user.

### Testability
- In-memory fake repositories and fakes for password hashing allow TDD without DB/framework.

---

## Key Decisions
- **DDD + Clean Architecture**: Bounded contexts, dependencies pointing inward.
- **Framework-free domain**: No Pydantic, ORM, or JWT in core.
- **Access token ≠ domain**: Will be implemented via `AccessTokenEncoder` in app/infra.
- **Refresh token = domain**: Modeled as entity with lifecycle.

---

## Remaining to Complete Auth End-to-End
- **Infrastructure**:
  - `MongoUserRepository`, `MongoRefreshTokenRepository`.
  - `Argon2PasswordHasher` (or bcrypt).
- **(Later)** `JWTAccessTokens` (`AccessTokenEncoder`).
- **Session Use Cases**:
  - `Login`: Verify password, issue refresh token, return short-lived access token.
  - `RefreshSession`: Validate/rotate refresh, issue new access token.
  - `Logout`: Revoke refresh token(s).
- **HTTP Interfaces**:
  - FastAPI routes calling use cases, mapping DTOs ↔ VOs/entities.
