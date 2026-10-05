# Monitoring, Health Checks & Observability

This document describes how to monitor application health, track server diagnostics, and inspect system logs.

---

## 🩺 System Health Check Endpoint (`/health`)

FastAPI exposes an active database health diagnostic endpoint at `GET /health` (`backend/src/api/api.py`):

```python
@app.get(
    "/health",
    tags=["System"],
    summary="System Health & Database Connectivity Check",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    try:
        with Session(engine) as session:
            session.exec(select(1)).first()
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as exc:
        return {
            "status": "degraded",
            "database": f"error: {str(exc)}",
        }
```

### Response States:
- **Healthy (`HTTP 200 OK`)**:
  ```json
  {
    "status": "healthy",
    "database": "connected"
  }
  ```
- **Degraded (`HTTP 200 / Error`)**:
  ```json
  {
    "status": "degraded",
    "database": "error: connection to server on socket failed"
  }
  ```

---

## 📊 Key Metrics to Monitor

| Metric | Target / Threshold | Alert Condition |
| :--- | :--- | :--- |
| **API Health Status** | `status: "healthy"` | Alert if endpoint returns degraded or fails 3 consecutive checks |
| **P95 Latency (`POST /documents/`)** | $< 3.0 \text{ seconds}$ | Alert if $> 6.0 \text{ seconds}$ (indicates OCR CPU bottlenecks) |
| **Database Connection Pool** | $< 80\%$ pool capacity | Alert if pool exhausts connections |
| **Server Memory (RAM)** | $< 80\%$ utilization | Alert if memory spikes during large PDF OCR processing |
