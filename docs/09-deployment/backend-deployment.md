# Backend Production Deployment

This document describes how to deploy the FastAPI backend service using production ASGI process managers (Gunicorn + Uvicorn) and systemd services.

---

## 🚀 Running FastAPI in Production (Gunicorn + Uvicorn)

In production, run FastAPI behind **Gunicorn** managing a pool of **Uvicorn** worker processes:

```bash
# Install gunicorn in the virtual environment
pip install gunicorn

# Start Gunicorn with Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --timeout 120 \
  --access-logfile /var/log/doc-manager/access.log \
  --error-logfile /var/log/doc-manager/error.log
```

> **Worker Count Formula**: Recommended number of workers is $(2 \times \text{CPU Cores}) + 1$.

---

## ⚙️ Systemd Service Configuration

Create `/etc/systemd/system/document-manager.service`:

```ini
[Unit]
Description=Document Management API Backend Service
After=network.target postgresql.service

[Service]
Type=notify
User=appuser
Group=appuser
WorkingDirectory=/var/www/document-manager
EnvironmentFile=/var/www/document-manager/.env
ExecStart=/var/www/document-manager/.venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable document-manager
sudo systemctl start document-manager
```
