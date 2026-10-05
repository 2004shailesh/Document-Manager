# Authentication & Credential Security

This document evaluates the cryptographic algorithms, credential storage, and session handling controls used in the application.

---

## 🔐 Cryptographic Password Hashing (Argon2)

Password hashing is implemented using `pwdlib[argon2]`:

- **Algorithm**: Argon2id (Version 19).
- **Salt Generation**: Automatically generates a unique, cryptographically secure 128-bit random salt per password entry.
- **Timing Attack Resistance**: The `password_hash.verify()` routine uses constant-time string comparisons to prevent timing attacks.
- **Hash Format Example**:
  ```text
  $argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ...$hashbytes...
  ```

---

## 🛡️ Response Sanitization & Data Exposure Prevention

To prevent accidental credential leaks:
1. **Public DTO Segregation**:
   The `UserPublic` schema strictly limits exposed fields:
   ```python
   class UserPublic(SQLModel):
       id: int
       name: str
       email: str
   ```
2. **Exclusion from Document Detail**:
   `DocumentDetailPublic` and `UserDocumentSummary` expose only the owner's numeric `id` or document summary without exposing password hashes.

---

## ⚠️ Identified Gaps & Hardening Recommendations

1. **Implement Stateless JWT Authentication**:
   - Currently, `POST /users/login` returns a user profile without a signed session token.
   - *Recommendation*: Issue signed JSON Web Tokens (JWT) with HMAC-SHA256 or RSA-256 and validate them via `Depends(oauth2_scheme)` on protected endpoints.
2. **Rate Limiting on Login**:
   - *Recommendation*: Add slowapi / Redis rate-limiting middleware to `POST /users/login` to thwart brute-force password guessing attacks.
