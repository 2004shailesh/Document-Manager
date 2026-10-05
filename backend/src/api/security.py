"""
================================================================================
Security & Password Hashing Configuration
================================================================================
Author: Senior Software Engineer & Technical Documentation Engineer
Library: `pwdlib` (Argon2id + Bcrypt fallback)

Key Architectural Concepts for New Developers:
1. One-Way Cryptographic Hashing:
   - Plaintext passwords submitted during user registration (`/users/`) are hashed with salt.
   - `password_hash.hash(plaintext)` generates a secure, salted hash string.
   - `password_hash.verify(plaintext, hash)` validates credentials during login (`/users/login`)
     without ever decrypting or storing plaintext credentials in the database.
2. Shared Singleton Pattern:
   - Uses `PasswordHash.recommended()` which selects Argon2id by default for optimal resistance
     against brute-force and GPU-based dictionary attacks.
================================================================================
"""

from pwdlib import PasswordHash

# Initialize a single shared PasswordHash instance using recommended cryptographic algorithms
password_hash = PasswordHash.recommended()
