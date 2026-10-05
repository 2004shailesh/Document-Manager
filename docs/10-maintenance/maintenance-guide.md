# System Maintenance & Database Operations

This guide covers routine operational maintenance tasks, including keyword dictionary tuning, database vacuuming, and category re-synchronization.

---

## 🔧 Routine Maintenance Procedures

### 1. Adding New Domain Keywords to Categorization Engine
To improve document classification accuracy for specific categories without restarting the server:

```sql
-- Example: Add 'proforma' and 'einvoice' to Category 1 (Invoice)
INSERT INTO category_keyword (keyword, cat_id)
VALUES 
    ('proforma', 1),
    ('einvoice', 1)
ON CONFLICT (keyword) DO NOTHING;
```
The categorization engine dynamically queries the `category_keyword` table, so changes take effect immediately on subsequent uploads.

---

### 2. Database Maintenance & VACUUM (BYTEA Optimization)
Because PDF documents are stored as `BYTEA` BLOBs, deleting or updating documents creates dead tuples in PostgreSQL. Run routine maintenance:

```sql
-- Analyze table statistics for query planner
ANALYZE documents;

-- Reclaim storage space from deleted document BLOBs
VACUUM (VERBOSE, ANALYZE) documents;
```

---

### 3. Re-running Document Backfill
To re-run text extraction and categorization across older documents:
Simply restart the backend service or invoke `backfill_uncategorized_documents()` from `backend/src/data/database.py` in a Python shell:

```python
from src.data.database import backfill_uncategorized_documents
backfill_uncategorized_documents()
```
