# PARVAT NETRA / PAHAD AI — PHASE 11J DEPLOYMENT ARCHITECTURE
**Standard: Smart India Hackathon (SIH) 2026 Pre-Submission Hardening**  
**Classification: Serverless & Containerized Production Deployment Specification**  
**Primary Target Platform: Vercel Serverless WSGI (`https://silly-fermi.vercel.app`)**

---

## 1. Primary Platform: Vercel Serverless WSGI

The primary public demonstration target for PARVAT NETRA is deployed on **Vercel** under the production URL:
`https://silly-fermi.vercel.app/`

### 1.1 Architecture Configuration (`vercel.json`)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python",
      "config": {
        "maxDuration": 30
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### 1.2 Entrypoint & Execution Model
- **WSGI Entrypoint:** `app.py` exposes the Flask application instance `app`.
- **Alternative Handler:** `api/index.py` also exists as an import bridge adding the root directory to `sys.path`.
- **Builder:** `@vercel/python` builder compiles `requirements.txt` into an AWS Lambda / Vercel Serverless execution container running Python 3.11.
- **Execution Timeout:** `maxDuration: 30` seconds per request (generous for sub-500ms model inference and 100ms API endpoints).

---

## 2. Platform Boundaries, Persistence & Caching Constraints

| Attribute | Vercel Serverless Environment | Application Resilience Design |
|---|---|---|
| **Filesystem State** | **Ephemeral / Read-Only** outside `/tmp` | SQLite DB (`data/observations/pahad_observations.db`) and weather/seismic caches fallback gracefully to in-memory dictionary caching if disk writes fail. |
| **Process Lifecycle** | **Stateless invocation** (container spun up on demand, frozen between calls) | No background daemon worker threads required for basic request fulfillment; all inference is computed synchronously or cached with TTL. |
| **Static Assets** | Served by Flask via `/static/` routing | Core libraries (Leaflet, Phosphor Icons, Tailwind CDN) load from verified CDNs or local bundles. |
| **Database Connectivity** | External PostgreSQL via `DATABASE_URL` (Neon / Supabase / Render) | Connection failures fallback automatically to static PostGIS and canonical corridor registries without crashing (`DATABASE_AVAILABLE=False`). |
| **In-Memory Caching** | Local process cache (`_HIGHEST_RISK_CACHE`, weather caches) | 60-second TTL prevents repeated external weather queries during high-concurrency traffic. |

---

## 3. Alternative / Fallback Targets

### 3.1 Render WSGI (`render.yaml`)
- **Service:** Web Service
- **Runtime:** Python 3.11
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --workers=2 --bind 0.0.0.0:10000 --timeout 60 app:app`
- **Port:** 10000

### 3.2 Docker Container (`Dockerfile`)
- **Base Image:** `python:3.11-slim`
- **Security:** Non-root unprivileged execution (`appuser`, UID 10001)
- **Healthcheck:** `curl -f http://localhost:10000/health || exit 1`
