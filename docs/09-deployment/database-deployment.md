# Database Production Deployment & Sizing

This document outlines configuration guidelines, sizing recommendations, and connection pooling best practices for deploying PostgreSQL in production.

---

## 🗄️ PostgreSQL Production Configuration

When provisioning PostgreSQL (e.g. AWS RDS PostgreSQL 16 or Azure Database for PostgreSQL):

| Setting | Recommended Value | Rationale |
| :--- | :--- | :--- |
| `max_connections` | `100 - 200` | Sufficient for multi-worker backend clusters |
| `shared_buffers` | `25% of total RAM` | Efficient in-memory caching of tables and indexes |
| `effective_cache_size` | `75% of total RAM` | Informs query planner of available filesystem cache |
| `work_mem` | `16 MB - 32 MB` | Accelerates sorting and junction table joins |
| `maintenance_work_mem` | `256 MB` | Speeds up index builds and `VACUUM` maintenance |

---

## 💾 Storage Sizing Calculations

Because document binary payloads are stored in the `documents.body` column (`BYTEA`):

$$\text{Estimated DB Storage} = N_{\text{documents}} \times (\text{Average PDF Size} + \text{Text Overhead}) \times 1.25$$

### Example Projections:
- **1,000 Documents** (Average 500 KB): $\approx 625 \text{ MB}$.
- **10,000 Documents** (Average 500 KB): $\approx 6.25 \text{ GB}$.
- **100,000 Documents** (Average 500 KB): $\approx 62.5 \text{ GB}$.

> **Architecture Recommendation**: For scale $> 50,000$ documents, migrate PDF binary storage to Object Storage (S3 / MinIO) as cataloged in [`docs/DOCUMENTATION_ISSUES.md`](file:///c:/Users/shail/OneDrive/Desktop/project/docs/DOCUMENTATION_ISSUES.md).
