# Frontend Production Build & Deployment

This document explains how to build and deploy the React 19 Single Page Application for production environments.

---

## 🔨 Compiling Production Bundles

From the `frontend/` directory:

```bash
# 1. Install dependencies
pnpm install --frozen-lockfile

# 2. Compile TypeScript and build production bundle
pnpm run build
```

This command executes `tsc -b && vite build`:
- Type-checks all TypeScript source code.
- Minifies and bundles code into the `frontend/dist/` directory.
- Injects hashed asset filenames for cache busting.

---

## 🌐 Serving with Nginx

Sample Nginx server block for hosting `dist/` with client-side SPA routing:

```nginx
server {
    listen 80;
    server_name documents.example.com;

    root /var/www/document-manager/frontend/dist;
    index index.html;

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Static Assets with Long Cache Expiry
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA Client-Side Routing Fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API Requests to Backend
    location /users/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /categories/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /documents/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        client_max_body_size 5M; # Must exceed 3MB upload limit
    }
}
```
