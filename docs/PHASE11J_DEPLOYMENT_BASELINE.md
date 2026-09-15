# PARVAT NETRA / PAHAD AI — PHASE 11J DEPLOYMENT BASELINE
**Standard: Smart India Hackathon (SIH) 2026 Pre-Submission Hardening**  
**Classification: Release Baseline, Build & Deployment Configuration Inventory**  
**Audit Baseline Verdict: `CODE_CLAIM_REMEDIATION_PASS_WITH_LIMITATIONS` (Phase 11I)**

---

## 1. Release Identification & Repository State

- **Baseline Date:** September 15, 2026
- **Current Branch:** `main`
- **Baseline Git Commit:** `4c439afa16e7158b1657ea892e14d99d42285156` (`feat(phase11b): complete responsive UI refinement report and verification across 18 viewports`)
- **Remote Origin:** `https://github.com/dimpu-sashank2008/parvatnetra.git` (fetch & push)
- **Deployment Platform:** Vercel Serverless WSGI (`@vercel/python` builder via `vercel.json` routing to `app.py`)
- **Staging / Fallback Target:** Render WSGI (`render.yaml` gunicorn deployment on port 10000)
- **Container Target:** Multi-stage `Dockerfile` (non-root unprivileged execution)

---

## 2. Execution Runtime & Toolchain Versions

| Component | Active Version | Verification Command | Status |
|---|---|---|:---:|
| **Python** | 3.11.0 (Windows x64) | `python --version` | COMPLIANT |
| **Node.js** | v24.19.0 | `node --version` | COMPLIANT |
| **npm** | 11.17.0 | `npm --version` | COMPLIANT |
| **Pytest** | 9.1.1 | `python -m pytest --version` | COMPLIANT |
| **Flask** | 3.0.x WSGI | `python -c "import flask; print(flask.__version__)"` | COMPLIANT |

---

## 3. Working Tree Status Prior to 11J

### 3.1 Staged Changes (`git status`):
- Deleted 4 obsolete HTML template backups (`templates/index.html.pre_ai_first_20260908.bak`, `templates/index.html.pre_gis_dashboard_bak`, `templates/index.html.pre_sih_uiux_20260908.bak2`, `templates/index.html.pre_uiux_20260908.bak`) and diagnostic log `temp_fail.txt`, reclaiming **2,230,500 bytes (~2.23 MB)**.

### 3.2 Unstaged Modifications:
- `.gitignore`: Added `*.bak` pattern.
- `app.py`:
  - `lines 5699`: Feature key lookup rectified from `rain_24h` to `rainfall_24h` in `/api/pahad/highest-risk-corridor`.
  - `lines 5898–5920` & `5955–5975`: Canonical coordinate resolution in `/api/pahad/live-inference` and `/api/pahad/forecast` to prevent spatial leakage when lat/lon omitted.
- `services/pahad_voice_assistant.py`:
  - `lines 485`: Reconciled lead time assertion to: `*Prototype evaluates multiple forecast horizons (6h / 12h / 24h / 48h outlooks)*`.
- `templates/index.html`:
  - `lines 2673–2676`: Added persistent academic research prototype disclaimer banner (`CLM-12`).
  - `lines 4618, 4642, 4669, 4693`: Updated horizon card labels from `Lead Time Estimate` to `Forecast Horizon: XXh`.

---

## 4. Operational Invariants Enforced

| Environmental Parameter | Value | Enforcement Mode |
|---|:---:|---|
| `ENABLE_PUBLIC_DISPATCH` | `0` | **FAIL-CLOSED** (Civilian mass SMS/CAP locked) |
| `SIREN_DRY_RUN` | `1` | **FAIL-CLOSED** (Hardware relay dry-run emulated) |
| `CAP_PRODUCTION_DISPATCH` | `0` | **FAIL-CLOSED** (CAP feeds restricted to staging/sandbox) |
| `SACHET_PRODUCTION_DISPATCH` | `0` | **FAIL-CLOSED** (NDMA SACHET sandbox gated) |
| `CELL_BROADCAST_PRODUCTION` | `0` | **FAIL-CLOSED** (Mock emergency cell broadcast) |
| `PAHAD_DEMO_MODE` | `0` | **ISOLATED** (Demo overlay active only when explicitly 1) |

---

## 5. Deployment Commands Inventory

- **Local Development / Test Start:**
  ```bash
  python app.py
  ```
- **WSGI Production Start (Render / Container):**
  ```bash
  gunicorn --workers=2 --bind 0.0.0.0:10000 --timeout 60 app:app
  ```
- **Serverless Production Start (Vercel):**
  ```json
  "builds": [{ "src": "app.py", "use": "@vercel/python", "config": { "maxDuration": 30 } }]
  ```
- **Regression Suite:**
  ```bash
  python -m pytest tests/test_pahad_engine.py tests/test_pahad_phase2.py tests/test_pahad_phase3.py tests/test_pahad_data_fusion.py tests/test_weather_service.py tests/test_seismic_service.py tests/test_terrain_api.py tests/test_i18n_localization.py tests/test_model_regression.py
  ```
