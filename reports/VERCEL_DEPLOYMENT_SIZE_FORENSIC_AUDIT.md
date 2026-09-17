# PARVAT NETRA / PAHAD AI
## VERCEL 100 MB DEPLOYMENT SIZE FORENSIC AUDIT & REMEDIATION REPORT
**Document Reference**: `reports/VERCEL_DEPLOYMENT_SIZE_FORENSIC_AUDIT.md`  
**Execution Timestamp**: `2026-09-17T09:23:00+05:30`  
**Git Baseline Commit**: `c5964d8a19e97af6bc96470014ed344bfd1b36f2`  
**Vercel Target Project**: `silly-fermi` (`prj_wDHY7Lm5diHUrN4hzZSPqfEsfIZz`, Org: `team_PIwfOBfSoof2F2Ou7YqruEp1`)  
**Deployment Readiness Verdict**: `DEPLOYMENT_SIZE_RESOLVED`

---

## 1. ERROR
```text
ERROR: File size limit exceeded (100 MB)
```
**Error Stage**: Source Upload Phase (Pre-build).  
**Vercel Platform Rule**: Vercel enforces a hard 100 MB individual file limit and request payload threshold during source asset upload before container packaging.

---

## 2. REPOSITORY SIZE

| Scope | Total Size | Total File Count | Notes |
|---|---|---|---|
| **Entire Physical Workspace** (`c:\...\PARVAT_NETRA_PAHAD_AI_FIRST`) | **733.20 MB** | 20,608 files | Includes `.venv` (517.67 MB), `.git` (37.37 MB), `parvat_netra_mobile` (68.12 MB), `data/observations` (53.66 MB). |
| **Git-Tracked Assets** (`git ls-files`) | **34.91 MB** | 1,369 files | Repository tracked content under version control. |
| **Pre-Remediation Parent Deployable Size** | **390.75 MB** | 1,942 files | Evaluated when invoking Vercel CLI from parent directory without root `.vercelignore`. |
| **Pre-Remediation `silly-fermi` Subdirectory Deployable Size** | **7.99 MB** | 1,073 files | Evaluated inside `silly-fermi` with initial baseline `.vercelignore`. |

---

## 3. DEPLOYMENT SIZE

| Directory Context | Initial Dry-Run Size | Post-Optimization Dry-Run Size | Headroom under 100 MB Limit |
|---|---|---|---|
| **Subdirectory** (`silly-fermi`) | 7.99 MB (8,377,914 B) | **6.04 MB** (6,335,389 B) | **93.96 MB (94.0% below limit)** |
| **Parent Root** (`PARVAT_NETRA_PAHAD_AI_FIRST`) | 390.75 MB (409,726,823 B) | **6.29 MB** (6,600,251 B) | **93.71 MB (93.7% below limit)** |

---

## 4. TOP LARGE FILES

### Across Physical Repository
| Rank | Size (MB) | File Path | Classification | Runtime Required? |
|---|---|---|---|---|
| 1 | **231.77 MB** | `PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi.zip` | Stale Archive (Parent) | **NO** (Audit bloat) |
| 2 | **88.25 MB** | `.venv/Lib/site-packages/playwright/driver/node.exe` | Local Dev Virtualenv | **NO** (Serverless installs clean) |
| 3 | **54.98 MB** | `silly-fermi/parvat_netra_mobile/build/test_cache/...dill` | Flutter Test Cache | **NO** (Mobile client artifact) |
| 4 | **53.66 MB** | `silly-fermi/data/observations/pahad_observations.db` | Local SQLite Database | **NO** (`/tmp` used on Vercel) |
| 5 | **19.47 MB** | `.venv/Lib/site-packages/numpy.libs/...` | Local Dev Virtualenv | **NO** (Installed on Vercel) |
| 6 | **19.32 MB** | `.venv/Lib/site-packages/scipy.libs/...` | Local Dev Virtualenv | **NO** (Installed on Vercel) |
| 7 | **11.85 MB** | `.git/objects/pack/...` | Git Internal Packfile | **NO** (Ignored by Vercel) |
| 8 | **10.64 MB** | `silly-fermi/parvat_netra_mobile/.dart_tool/...hook.dill` | Flutter Hook Runner | **NO** (Mobile client artifact) |
| 9 | **3.18 MB** | `silly-fermi/docs/screenshots/viewport_1024x768_tablet_landscape.png`| Documentation / Proof | **NO** (Documentation only) |
| 10 | **3.13 MB** | `silly-fermi/docs/PARVAT_NETRA_SIH_Winning_Deck.pptx` | Presentation Deck | **NO** (Documentation only) |

### Large File Search Breakdown:
- **Files > 100 MB**: `silly-fermi.zip` (**231.77 MB**)
- **Files 50 MB - 100 MB**: `node.exe` in `.venv` (88.25 MB), Flutter test cache (54.98 MB), `pahad_observations.db` (53.66 MB)
- **Files 25 MB - 50 MB**: None
- **Files 10 MB - 25 MB**: `.git` packfile (11.85 MB), `numpy/scipy` DLLs in `.venv` (~19.4 MB each), Flutter hook runner (10.64 MB)
- **Files 5 MB - 10 MB**: `ngrok.pyd` (7.81 MB), `_avif.pyd` (7.52 MB), `highspy` (6.14 MB) in `.venv`

---

## 5. VERCEL DRY RUN ANALYSIS

Executed via `Vercel CLI 59.20.0`:
`vercel deploy --dry --format=json`

### Subdirectory `silly-fermi` Dry-Run:
- **Included Files**: 620 files
- **Total Deployment Size**: **6.04 MB** (6,335,389 bytes)
- **Top 5 Largest Included Files**:
  1. `templates/index.html`: **0.92 MB**
  2. `app.py`: **0.31 MB**
  3. `static/images/parvat_netra_emblem.png`: **0.29 MB**
  4. `models/pahad_fos_model.pkl`: **0.28 MB**
  5. `models/fos_predictor.pkl`: **0.28 MB**
- **Size by Directory**:
  - `templates`: 1.40 MB
  - `models`: 0.97 MB
  - `engine`: 0.89 MB
  - `services`: 0.88 MB
  - `static`: 0.83 MB
  - `backend`: 0.39 MB
  - `[root]`: 0.39 MB
  - `data`: 0.28 MB

---

## 6. ROOT CAUSE

1. **Primary Offender**:
   The file `c:\Users\dimpu\Downloads\PARVAT_NETRA_PAHAD_AI_FIRST\silly-fermi.zip` (**231.77 MB**) located in the workspace parent root.
2. **Execution Context Mismatch**:
   At `09:14 AM`, Vercel project linkage was established in the parent directory (`PARVAT_NETRA_PAHAD_AI_FIRST/.vercel/project.json`), which pointed to `prj_wDHY7Lm5diHUrN4hzZSPqfEsfIZz`.
3. **Absence of Parent `.vercelignore`**:
   The parent directory lacked a `.vercelignore` file. When `vercel deploy` was executed in the parent directory, Vercel attempted to upload all root files, including `silly-fermi.zip` (231.77 MB).
4. **Vercel Hard Cap Trigger**:
   Because `231.77 MB > 100 MB`, Vercel CLI immediately terminated during the pre-flight source upload with:
   `ERROR: File size limit exceeded (100 MB)`.

---

## 7. RUNTIME DEPENDENCY MATRIX SUMMARY

Detailed matrix documented in [`reports/vercel_runtime_dependency_matrix.md`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/reports/vercel_runtime_dependency_matrix.md):
- **Models Required**: `fos_predictor.pkl` (281.8 KB), `pahad_fos_model.pkl` (288.2 KB), `pahad_event_model.pkl` (55.8 KB), `pahad_event_calibrator.pkl` (54.8 KB), multi-horizon models (296 KB). **Total model footprint: 0.97 MB**.
- **Datasets Required**: `data/realtime/realtime_cri_dataset.json` (50.3 KB), `data/realtime/realtime_cri_dataset.csv` (14.6 KB), `data/manifests/canonical_event_inventory.json` (36.0 KB). **Total runtime data: < 150 KB**.
- **Databases**: SQLite persistence redirected to `/tmp/pahad_observations.db` at runtime (`app.py:L31-41`). Cloud persistence provided by Neon PostgreSQL. Local `.db` files safely excluded.
- **Documentation & Tests**: `docs/`, `reports/`, `tests/`, `scripts/` are development/audit artifacts and not required by the Flask serverless handler.

---

## 8. SAFE OPTIMIZATION APPLIED

### Modified `silly-fermi/.vercelignore`:
Added explicit production exclusions without removing any runtime or scientific dependencies:
```gitignore
*.zip
*.tar*
*.gz
data/observations/
data/cache/
data/raw/
data/features/
data/labels/
data/processed/
scripts/
reports/
public/
```

### Created `PARVAT_NETRA_PAHAD_AI_FIRST/.vercelignore`:
Added root guard rules preventing `silly-fermi.zip` and mobile/test caches from being bundled if CLI is invoked from the parent workspace directory.

---

## 9. POST-OPTIMIZATION SIZE MEASUREMENTS

| Directory | Initial Size | Post-Optimization Size | Delta | Status |
|---|---|---|---|---|
| `silly-fermi` | 7.99 MB | **6.04 MB** | -1.95 MB (-24.4%) | **PASSED (6.04 MB / 100 MB)** |
| `PARVAT_NETRA_PAHAD_AI_FIRST` | 390.75 MB | **6.29 MB** | -384.46 MB (-98.4%) | **PASSED (6.29 MB / 100 MB)** |

---

## 10. TEST VERIFICATION

Command executed:
```bash
python -m pytest tests/test_live_risk_map.py tests/test_map_viewport.py tests/test_runtime_data_truth.py tests/test_authoritative_audit.py tests/test_pahad_engine.py tests/test_weather_service.py tests/test_seismic_service.py -q
```
**Results**:
- **56 passed in 13.00s (100% Pass Rate)**
- Zero test failures, zero regressions, zero skipped tests.

---

## 11. MODEL & DATASET SHA-256 HASH INTEGRITY

| File | Size (Bytes) | SHA-256 Hash | Integrity Check |
|---|---|---|---|
| `models/fos_predictor.pkl` | 288,589 | `21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c` | **UNMODIFIED** |
| `models/pahad_fos_model.pkl` | 295,094 | `d1b9e91db79d3292fd318c73aaba4b3d5caf0a1119e5a698b24f68a19e1de673` | **UNMODIFIED** |
| `models/pahad_event_model.pkl` | 57,100 | `46c1f2f8106074d1c8c9ef19880533fd0faa3ece3f2296fe47785a8ee7ffff35` | **UNMODIFIED** |
| `models/pahad_event_calibrator.pkl` | 56,091 | `f3a72b9eb9340990a4b4585799f438d27158d09002b948728f5eae41dbc1b1f8` | **UNMODIFIED** |
| `models/pahad_event_model_6h.pkl` | 61,657 | `e864b26edb1e708aac4ec5c2d95d8c3088ba6310a3b9e79586a093c70e06270e` | **UNMODIFIED** |
| `models/pahad_event_model_12h.pkl` | 88,702 | `04c2eb5469c4b8a14d0e99cb71380430c695f858cb7e349e78658f335ab24698` | **UNMODIFIED** |
| `models/pahad_event_model_24h.pkl` | 84,094 | `84cd808a6196cdd5f330756a6b4007234bd9ae7a73d9505cd428ac7589545831` | **UNMODIFIED** |
| `models/pahad_event_model_48h.pkl` | 62,245 | `61e1f8aff5f3f954560bbeb88cd8ae94e27134ec2e9cfc18a5004bf419f86093` | **UNMODIFIED** |
| `data/realtime/realtime_cri_dataset.json`| 51,546 | `e69eb72c2ff2d86f6872097531158879db83e83264e2f65accf670899483412a` | **UNMODIFIED** |
| `data/realtime/realtime_cri_dataset.csv` | 14,926 | `b10abf09f2c7d5fcfd289e4319419b59d5831a27f805d9f24a2436de662fc4a1` | **UNMODIFIED** |

---

## 12. DEPLOYMENT READINESS

```yaml
DEPLOYMENT_READINESS: DEPLOYMENT_SIZE_RESOLVED
VERCEL_DRY_RUN_SIZE: 6.04 MB (6,335,389 bytes)
MAX_PERMISSIBLE_SIZE: 100.00 MB
HEADROOM: 93.96 MB (94.0% safety margin)
EXTERNAL_STORAGE_REQUIRED: NO
SOURCE_INTEGRITY: 100% PRESERVED
REGRESSION_TEST_STATUS: 56/56 PASSED (100%)
```
