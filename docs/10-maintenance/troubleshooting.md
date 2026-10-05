# Production Troubleshooting & Incident Response

This operational guide provides diagnostic procedures for handling production incidents.

---

## 🚨 Production Incident Playbook

### Incident 1: High CPU Utilization on Document Uploads
- **Symptom**: Server CPU spikes to 100% when users upload scanned PDF files.
- **Root Cause**: RapidOCR ONNX inference runs on CPU and utilizes multiple processing threads for heavy rasterized page images.
- **Remediation**:
  1. Verify uploads adhere to the `MAX_FILE_SIZE_MB = 3` limit.
  2. Scale the backend horizontally across multiple CPU cores or containers.
  3. Ensure Gunicorn workers have sufficient CPU reservations.

---

### Incident 2: Database Out of Connections: "FATAL: remaining connection slots are reserved"
- **Symptom**: API endpoints return HTTP 500 errors; `/health` returns `"degraded"`.
- **Root Cause**: FastAPI requests or background processes leaking database sessions without calling `session.close()`.
- **Remediation**:
  1. Inspect active PostgreSQL connection counts:
     ```sql
     SELECT count(*), state FROM pg_stat_activity GROUP BY state;
     ```
  2. Terminate idle connections:
     ```sql
     SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < current_timestamp - INTERVAL '5 minutes';
     ```
  3. Ensure all route handlers use the `get_session` dependency context manager.

---

### Incident 3: Documents Uploaded as "Others" Unintentionally
- **Symptom**: Standard invoices or medical reports are categorized as `Others`.
- **Root Cause**: The PDF text either lacks sufficient domain keywords in `category_keyword` or OCR produced low-confidence noisy text.
- **Remediation**:
  1. Inspect the document's `extracted_text` via `GET /documents/{document_id}`.
  2. If the text contains relevant industry terms not yet in the dictionary, insert them into `category_keyword`:
     ```sql
     INSERT INTO category_keyword (keyword, cat_id) VALUES ('new_domain_term', 1);
     ```
  3. Update the document category via `PATCH /documents/{document_id}`.
