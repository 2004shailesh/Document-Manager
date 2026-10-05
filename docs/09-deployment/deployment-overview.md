# Deployment Overview & Production Topologies

This document outlines deployment architectures, production build processes, and operational topologies for the **Document Management System**.

> **Audit Note**: Dockerfiles, Kubernetes manifests, and CI/CD pipelines are not currently present in the repository. The deployment strategies documented below are based on verified application build and runtime requirements.

---

## 🏗️ Production Deployment Topology

```mermaid
flowchart TB
    User[End User Web Traffic] --> Cloudflare[Reverse Proxy / CDN / SSL Termination]
    
    subgraph FrontendHosting["Frontend Static Hosting"]
        Cloudflare -- "Static Assets (HTML / JS / CSS)" --> NginxS3["Nginx / Cloudflare Pages / AWS S3 + CloudFront"]
    end

    subgraph BackendCluster["Application Cluster (FastAPI / Uvicorn)"]
        Cloudflare -- "API Traffic (/users, /documents, /categories)" --> Gunicorn["Gunicorn / Uvicorn ASGI Process Manager"]
        Gunicorn --> Worker1["Uvicorn Worker 1"]
        Gunicorn --> Worker2["Uvicorn Worker 2"]
        Gunicorn --> Worker3["Uvicorn Worker 3"]
        Gunicorn --> Worker4["Uvicorn Worker 4"]
    end

    subgraph DatabaseTier["Persistence Tier"]
        Worker1 & Worker2 & Worker3 & Worker4 --> PgPool["PostgreSQL Primary (Managed DB / RDS)"]
        PgPool --> Standby["Read / Standby Replica"]
    end
```

---

## 📦 Build Artifact Summary

| Component | Build Tool / Command | Output Artifact | Hosting Target |
| :--- | :--- | :--- | :--- |
| **Frontend** | `pnpm run build` (`tsc -b && vite build`) | `frontend/dist/` (HTML, JS bundles, CSS) | Nginx, AWS S3 / CloudFront, Vercel, Cloudflare Pages |
| **Backend** | Python Package / Wheel | Python 3.12 Virtual Environment | Linux VM (systemd), Docker Container, AWS ECS, GCP Cloud Run |
| **Database** | PostgreSQL 14+ | PostgreSQL Schema & Tables | Managed AWS RDS, GCP Cloud SQL, or self-hosted PostgreSQL |
