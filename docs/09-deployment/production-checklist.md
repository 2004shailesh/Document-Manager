# Production Launch Checklist

Before deploying the **Document Management System** to production, verify all items in this checklist.

---

## 📋 Pre-Flight Verification Checklist

### 🔒 1. Security & Configuration
- [ ] Ensure `.env` is populated with strong, unique credentials.
- [ ] Remove hardcoded password fallbacks from source code (`constant.py`).
- [ ] Restrict CORS `allow_origins` to production domain whitelists.
- [ ] Verify SSL/TLS HTTPS certificates are installed on reverse proxy / load balancer.
- [ ] Set Nginx `client_max_body_size` to at least `5M` to allow 3MB PDF uploads.

### 🗄️ 2. Database & Persistence
- [ ] Ensure target PostgreSQL database exists and is backed up regularly.
- [ ] Confirm `pool_pre_ping=True` is enabled in SQLAlchemy engine configuration.
- [ ] Verify database connection string uses SSL (`sslmode=require` in production).
- [ ] Confirm the 6 static categories (IDs 1..6) and keywords are seeded on startup.

### ⚡ 3. Processing Engines (OCR & ML)
- [ ] Verify host machine has at least 4 GB RAM to support RapidOCR ONNX model memory.
- [ ] Test sample vector PDF extraction to confirm PyMuPDF digital text extraction.
- [ ] Test sample scanned PDF extraction to confirm RapidOCR ONNX image fallback.

### 🌐 4. Frontend SPA
- [ ] Execute `pnpm run build` without TypeScript or bundle errors.
- [ ] Ensure API base URL in frontend points to production backend gateway.
- [ ] Verify SPA fallback routing is configured on the static web server (`try_files $uri $uri/ /index.html;`).
