# PARVAT NETRA / PAHAD AI
## Vercel Runtime Dependency & Deployment Exclusion Matrix
**Document Reference**: `reports/vercel_runtime_dependency_matrix.md`  
**Execution Timestamp**: `2026-09-17T09:25:00+05:30`  
**Project Directory**: `c:\Users\dimpu\Downloads\PARVAT_NETRA_PAHAD_AI_FIRST\silly-fermi`  
**Target Commit SHA**: `c5964d8a19e97af6bc96470014ed344bfd1b36f2`

---

## 1. Runtime Asset Audit & Dependency Classification

This matrix documents every major file, model artifact, database, and directory in the repository, certifying whether it is strictly required by the Flask WSGI / PAHAD AI runtime in Vercel Serverless environment (`@vercel/python`), or whether it is safe to exclude via `.vercelignore`.

| Path / Pattern | Size | Required at Runtime? | Required for Vercel? | Safe to Exclude? | Reason & Architectural Justification |
|---|---|---|---|---|---|
| `app.py` | 317 KB | **YES** | **YES** | **NO** | Core Flask WSGI application entrypoint, route handlers, middleware. |
| `vercel.json` | 248 bytes | **YES** | **YES** | **NO** | Vercel deployment specification (`@vercel/python`, maxDuration: 30s). |
| `requirements.txt` | 1.8 KB | **YES** | **YES** | **NO** | Python package dependencies installed during Vercel build. |
| `backend/` | 390 KB | **YES** | **YES** | **NO** | Flask Blueprint route controllers (realtime, edge, auth, telemetry). |
| `engine/` | 890 KB | **YES** | **YES** | **NO** | Core PAHAD physics, Mohr-Coulomb FoS formulas, adversarial defense. |
| `services/` | 880 KB | **YES** | **YES** | **NO** | Open-Meteo weather, USGS seismic, AI triage, voice assistant services. |
| `models/fos_predictor.pkl` | 288.6 KB | **YES** | **YES** | **NO** | Trained Geotechnical FoS scikit-learn model loaded by `AI_TRIAGE_ENGINE`. |
| `models/pahad_fos_model.pkl` | 295.1 KB | **YES** | **YES** | **NO** | Geotechnical FoS predictor loaded by `engine/pahad_live_inference.py`. |
| `models/pahad_event_model.pkl` | 57.1 KB | **YES** | **YES** | **NO** | Primary Landslide Event Classifier model (Phase 3.1 GBDT). |
| `models/pahad_event_calibrator.pkl` | 56.1 KB | **YES** | **YES** | **NO** | Isotonic probability calibrator for event classifier. |
| `models/pahad_event_model_*.pkl` | 296 KB | **YES** | **YES** | **NO** | Multi-horizon forecast models (6h, 12h, 24h, 48h). |
| `models/*.json` | 27 KB | **YES** | **YES** | **NO** | Feature schemas, metadata, and out-of-distribution (OOD) bounds. |
| `templates/` | 1.40 MB | **YES** | **YES** | **NO** | Jinja2 HTML templates (`index.html`, `pahad_ai.html`, `console.html`, etc.). |
| `static/` | 830 KB | **YES** | **YES** | **NO** | CSS stylesheets, Leaflet GIS map scripts, logos, emblems. |
| `public/` | 830 KB | **NO** | **NO** | **YES** | Duplicate mirror of `static/` assets; Flask serves `/static/` directly. |
| `data/realtime/realtime_cri_dataset.json` | 51.5 KB | **YES** | **YES** | **NO** | Real-time Corridor Risk Index baseline filed for 20 corridors. |
| `data/realtime/realtime_cri_dataset.csv` | 14.9 KB | **YES** | **YES** | **NO** | Real-time CRI CSV representation for data export routes. |
| `data/manifests/corridor_registry.json` | 10 KB | **YES** | **YES** | **NO** | Canonical GIS metadata and coordinate extents for corridors. |
| `data/manifests/canonical_event_inventory.json` | 36.9 KB | **YES** | **YES** | **NO** | Ground truth event catalog for model explanation and evaluation APIs. |
| `data/manifests/data_lineage_matrix.json` | 35.5 KB | **YES** | **YES** | **NO** | Authoritative data provenance matrix served by `/api/audit/data-lineage`. |
| `data/cache/` | < 1 KB | **NO** | **NO** | **YES** | Ephemeral API response cache. Regenerated dynamically in `/tmp`. |
| `data/observations/pahad_observations.db` | **53.66 MB** | **NO** | **NO** | **YES** | SQLite local database. `app.py` redirects to `/tmp/pahad_observations.db` on serverless. Primary cloud persistence is Neon PostgreSQL. |
| `data/edge/*.db` | 150 KB | **NO** | **NO** | **YES** | Edge gateway simulation buffer SQLite files. |
| `data/processed/` | 100 KB | **NO** | **NO** | **YES** | Historical training partitions used during model training. Not used at runtime. |
| `data/features/` | 30 KB | **NO** | **NO** | **YES** | Engineered feature tables used during model training. |
| `data/labels/` | < 5 KB | **NO** | **NO** | **YES** | Event labeling truth tables used during model training. |
| `data/raw/` | < 5 KB | **NO** | **NO** | **YES** | Raw historical landslide records. |
| `parvat_netra_mobile/` | **68.12 MB** | **NO** | **NO** | **YES** | Flutter/Dart mobile application source and build cache (`.dill` files). |
| `parvat_netra_mobile/build/test_cache/` | **54.98 MB** | **NO** | **NO** | **YES** | Flutter test cache compiler binary artifact (`.track.dill`). |
| `docs/` | **25.29 MB** | **NO** | **NO** | **YES** | Evaluation screenshots (20 MB), presentation deck (3.13 MB), markdown specs. |
| `tests/` | **8.12 MB** | **NO** | **NO** | **YES** | Pytest unit and integration test suite and fixtures. |
| `scripts/` | **982 KB** | **NO** | **NO** | **YES** | Developer training, benchmarking, and audit scripts. |
| `reports/` | **387 KB** | **NO** | **NO** | **YES** | Audit reports and evaluation markdown documents. |
| `scratch/` | 330 KB | **NO** | **NO** | **YES** | Developer scratchpad and temporary JSON logs. |
| `.git/` | **37.37 MB** | **NO** | **NO** | **YES** | Git version control metadata. |
| `.venv/` | **517.67 MB** | **NO** | **NO** | **YES** | Local Python virtual environment. Vercel installs dependencies in container. |
| `__pycache__/` | **11.18 MB** | **NO** | **NO** | **YES** | Python compiled bytecode cache. |
| `.pytest_cache/` | 170 KB | **NO** | **NO** | **YES** | Pytest test execution cache. |
| `silly-fermi.zip` (Parent Root) | **231.77 MB** | **NO** | **NO** | **YES** | **PRIMARY CAUSE OF 100 MB ERROR**. Stale archive in parent directory. |

---

## 2. Model Hash Verification & Production Integrity

The required production machine learning models and calibrators have verified SHA-256 integrity:

| Model File | Size (Bytes) | Size (MB) | SHA-256 Checksum | Runtime Loader | Status |
|---|---|---|---|---|---|
| `models/fos_predictor.pkl` | 288,589 | 0.275 MB | `21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c` | `AI_TRIAGE_ENGINE` | **VERIFIED** |
| `models/pahad_fos_model.pkl` | 295,094 | 0.281 MB | `d1b9e91db79d3292fd318c73aaba4b3d5caf0a1119e5a698b24f68a19e1de673` | `pahad_live_inference` | **VERIFIED** |
| `models/pahad_event_model.pkl` | 57,100 | 0.054 MB | `46c1f2f8106074d1c8c9ef19880533fd0faa3ece3f2296fe47785a8ee7ffff35` | `load_pahad_event_model` | **VERIFIED** |
| `models/pahad_event_calibrator.pkl` | 56,091 | 0.053 MB | `f3a72b9eb9340990a4b4585799f438d27158d09002b948728f5eae41dbc1b1f8` | `load_pahad_event_model` | **VERIFIED** |
| `models/pahad_event_model_6h.pkl` | 61,657 | 0.059 MB | `e864b26edb1e708aac4ec5c2d95d8c3088ba6310a3b9e79586a093c70e06270e` | Multi-horizon engine | **VERIFIED** |
| `models/pahad_event_model_12h.pkl` | 88,702 | 0.085 MB | `04c2eb5469c4b8a14d0e99cb71380430c695f858cb7e349e78658f335ab24698` | Multi-horizon engine | **VERIFIED** |
| `models/pahad_event_model_24h.pkl` | 84,094 | 0.080 MB | `84cd808a6196cdd5f330756a6b4007234bd9ae7a73d9505cd428ac7589545831` | Multi-horizon engine | **VERIFIED** |
| `models/pahad_event_model_48h.pkl` | 62,245 | 0.059 MB | `61e1f8aff5f3f954560bbeb88cd8ae94e27134ec2e9cfc18a5004bf419f86093` | Multi-horizon engine | **VERIFIED** |

**Summary**: The total footprint of all production ML models is **0.97 MB**. No external object storage or model compression is necessary.
