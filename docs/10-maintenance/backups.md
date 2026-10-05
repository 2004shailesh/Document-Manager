# Backup & Disaster Recovery Procedures

Because PDF binary documents are stored directly inside the `documents` table (`BYTEA`), a standard PostgreSQL backup encapsulates all system data and files.

---

## 💾 Creating Backups with `pg_dump`

### 1. Compressed Binary Backup (Recommended)
```bash
# Set password in environment to avoid interactive prompt
export PGPASSWORD="your_secure_password"

# Execute pg_dump with custom format and compression
pg_dump -h localhost -p 5432 -U postgres -d Document -F c -b -v -f "document_backup_$(date +%Y%m%d_%H%M%S).dump"
```

### 2. Plain SQL Text Backup
```bash
pg_dump -h localhost -p 5432 -U postgres -d Document -F p -v -f "document_backup_$(date +%Y%m%d).sql"
```

---

## 🔄 Restoring from Backup with `pg_restore`

### 1. Restore into Fresh Database
```bash
# Create target database if needed
createdb -h localhost -p 5432 -U postgres Document_Restored

# Restore from compressed custom format dump
pg_restore -h localhost -p 5432 -U postgres -d Document_Restored -v "document_backup_20260925.dump"
```

### 2. Verification after Restore
```bash
psql -h localhost -U postgres -d Document_Restored -c "SELECT COUNT(*) FROM documents;"
```
