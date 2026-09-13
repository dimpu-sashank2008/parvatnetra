ï»¿# PARVAT NETRA / PAHAD AI ? PHASE 11A PUBLIC DEPLOYMENT REPORT
**Platform:** PARVAT NETRA ? NER Sentinel  
**Engine:** PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Deployment Pipeline:** Continuous Update Pipeline (GitHub Actions -> Railway / Render)  
**Prepared Date:** 2026-09-13  
**Status:** PHASE11A_STAGING_READY  

---

## Executive Summary
Phase 11A establishes the production deployment foundation for the PARVAT NETRA / PAHAD AI platform, enabling automated continuous deployment from the GitHub repository directly to hosted cloud container runtimes with zero UI redesign and complete preservation of scientific modeling cores.

---

## 1. Hosting Architecture & Multi-Cloud Redundancy

```
                       GitHub Repository: parvatnetra
                                    ?
           ???????????????????????????????????????????????????
           ?                                                 ?
      branch: main                                   branch: staging
    [Production Ring]                               [Public Staging Ring]
           ?                                                 ?
           ?                                                 ?
     GitHub Actions                                    GitHub Actions
  (CI, Smoke Tests,                                 (CI, Smoke Tests,
   Spatial Validation)                               Spatial Validation)
           ?                                                 ?
           ???????????????????????????????????????????????????
           ?                        ?                        ?
     RAILWAY APP              RENDER SERVICE            VERCEL EDGE
(Dockerfile Container)      (Docker Blueprint)      (Static & Serverless)
   `0.0.0.0:$PORT`             `0.0.0.0:$PORT`            `api/index.py`
           ?                        ?                        ?
           ???????????????????????????????????????????????????
                                    ?
                                    ?
                         PUBLIC HTTPS ACCESS
                     ? GET / (Tactical Console)
                     ? GET /health (Safe Probe)
                     ? GET /demo (50m Geofence)
```

---

## 2. Infrastructure as Code (IaC) Manifests

| Manifest | Target Platform | Specification Details |
|---|---|---|
| `railway.json` | Railway | Dockerfile builder, `/health` healthcheck probe, dynamic `$PORT` |
| `Procfile` | Railway / Heroku | `web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app` |
| `render.yaml` | Render | Docker runtime, healthCheckPath `/health`, zero-downtime rolling deploys |
| `vercel.json` | Vercel | Python WSGI runtime, static file caching, route redirection |
| `Dockerfile` | Multi-Cloud | Multi-stage builder with GDAL, GEOS, Proj, and Gunicorn WSGI |
| `.github/workflows/test.yml` | GitHub Actions | Automated lint, zero-leak check, WSGI boot verification, pytest smoke suite |

---

## 3. Public Verification Endpoints (CP04 & CP21)

### `GET /health` (Safe Healthcheck)
```json
{
  "application": "PARVAT NETRA",
  "database_status": "STANDALONE_FALLBACK",
  "environment": "staging",
  "model_status": "TRAINED_LIMITED_DATA",
  "status": "UP",
  "timestamp": "2026-09-13T12:05:11.934656+00:00",
  "version": "3.1.0"
}
```

### `GET /demo` (50-Meter Life-Safety Geofence Evaluator)
- **Real HTTPS Geolocation:** Queries device GPS with accuracy confidence.
- **Dynamic Haversine Proximity:** Computes distance to slip centroid (NH-10 Km 48).
- **50m Threshold Barrier:**
  - `INSIDE (<= 50m)`: Immediate Evacuation Order + Dry-Run Siren Trigger.
  - `OUTSIDE (> 50m)`: Standby & Monitoring Safe Standoff State.
- **Simulation Overrides:** 35m (Inside) vs 180m (Outside) evaluator presets for judges anywhere on Earth.
- **Isolated Multichannel Drill:** Submits safe test dispatches to `/api/notifications/demo/send-test` with zero public leak risk.

---

## 4. Staging Safety Invariants (CP19 & CP20)

In accordance with National Emergency Authority standards:
1. `ENABLE_PUBLIC_DISPATCH=0`: Blocks any external push or SMS broadcasts to the civilian population.
2. `SIREN_DRY_RUN=1`: Physical 130dB acoustic relays remain electronically locked in software emulation mode.
3. `PUBLIC_DEMO_TEST_ONLY=1`: Forces all drills into quarantined session scopes.
4. Cryptographic authority barriers protect all administrative routes (`/api/eoc/*`).
