ï»¿# PARVAT NETRA / PAHAD AI ? PHASE 11A DEPLOYMENT BASELINE
**Problem Statement ID:** SIH 26001 | Ministry of Development of North Eastern Region (MDoNER)  
**Standard:** Smart India Hackathon Grade National Disaster-Intelligence Platform  
**Target Environment:** Public HTTPS Staging & Production Deployment Pipeline  
**Execution Timestamp:** 2026-09-13T12:15:00Z  

---

## 1. Git Repository & Working Tree Baseline
- **GitHub Remote:** `https://github.com/dimpu-sashank2008/parvatnetra`
- **Active Branch Strategy:**
  - `main`: Production release branch.
  - `staging`: Public staging deployment branch.
- **Head Commit:** `be382c7` ? *feat(phase11a): add /health deployment healthcheck and /demo 50m geofence evaluation portal*
- **Working Tree Cleanliness:** Verified. Build caches (`.venv/`, `.gradle/`, `.pytest_cache/`), SQLite caches (`*.db`), and private `.env` are strictly excluded by `.gitignore`.

---

## 2. Monolith & WSGI Architecture
- **Flask Monolith Entrypoint:** `app.py`
- **WSGI Object:** `app` (callable syntax: `app:app`)
- **Production Server Specification:** Gunicorn WSGI Server (`gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app`)
- **Port Dynamic Binding:** Conforms to `0.0.0.0:${PORT:-8080}` across Dockerfile, Procfile, and Railway/Render specifications.

---

## 3. Dependency Lock (CP03)
- **Manifest:** `requirements.txt`
- **Runtime Components:**
  - `Flask==3.0.3` (Core web framework & Jinja2 template engine)
  - `gunicorn==22.0.0` (Production multi-threaded WSGI runner)
  - `psycopg2-binary==2.9.9` (PostgreSQL / PostGIS geospatial interface)
  - `requests==2.32.3` (IMD / Open-Meteo & USGS API connectivity)
  - `shapely==2.0.4` (Hillslope vector geometries & spatial polygon operations)
  - `numpy>=1.26.0` (Geotechnical Mohr-Coulomb tensor array math)
  - `pandas>=2.0.0` (Ground-truth catalogues & historical telemetry reconciliation)
  - `scikit-learn>=1.4.0` (Gradient Boosting FoS predictor & calibrators)
  - `joblib>=1.3.0` (Binary serialized model bundle loading)
  - `scipy>=1.12.0` (Spatial distance matrices & statistical distributions)
  - `python-dotenv>=1.0.0` (Local isolation environment manager)

---

## 4. Endpoints & Public Health Architecture (CP04 & CP21)
- `GET /`: Unified tactical operations console (543 KB Jinja2 single-page workspace).
- `GET /health`: Safe public deployment health check returning HTTP 200 without exposing credentials or internal IP topologies.
- `GET /demo`: Public 50m geofence evaluation and life-safety scenario drill portal.
- `GET /api/health`: Legacy PostGIS connectivity probe.
- `GET /api/pahad/highest-risk-corridor`: Autonomous corridor risk evaluation ranking.
- `GET /api/eoc/command-brief`: Executive incident command summary.

---

## 5. Machine Learning & Model Artifact Baseline (CP09)
All 16 trained model artifacts are verified present and versioned in `models/`:
- `models/fos_predictor.pkl` (288 KB ? Geotechnical FoS GradientBoosting model)
- `models/pahad_event_model.pkl` (57 KB ? Landslide event classifier)
- `models/pahad_event_model_6h.pkl`, `12h.pkl`, `24h.pkl`, `48h.pkl` (Multi-horizon models)
- `models/pahad_feature_schema.json` (Strict schema validator)
- `models/pahad_ood_bounds.json` (Out-of-distribution physical safety bounds)
- **Model Status:** Preserved as `TRAINED_LIMITED_DATA` in accordance with scientific defensibility protocols.

---

## 6. Safety & Credential Isolation Audit (CP05 & CP06)
- `.env.example` verified with placeholders.
- `python mcp/scripts/validate_config.py` executed: **ALL CHECKS PASSED**.
- Mandatory Staging Safety Controls:
  - `ENABLE_PUBLIC_DISPATCH = 0`
  - `SIREN_DRY_RUN = 1`
  - `CAP_PRODUCTION_DISPATCH = 0`
  - `SACHET_PRODUCTION_DISPATCH = 0`
  - `CELL_BROADCAST_PRODUCTION = 0`
  - `PUBLIC_DEMO_TEST_ONLY = 1`

---

## 7. Test Baseline Record
- **Total Tests Executed:** 1,530 tests.
- **Passed:** 1,491 tests.
- **Skipped:** 9 tests.
- **Failures:** 30 tests (attributable solely to remote AWS PostgreSQL timeout at `44.206.211.72:5432` in offline development mode).
