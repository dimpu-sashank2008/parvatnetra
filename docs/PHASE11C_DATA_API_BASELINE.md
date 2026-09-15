# PARVAT NETRA / PAHAD AI — PHASE 11C BASELINE
**DATA, API & PREDICTION INTEGRITY FORENSIC AUDIT BASELINE**

- **Date:** September 15, 2026
- **Audit Phase:** Phase 11C
- **Current Branch:** `main`
- **Baseline Git Commit:** `4c439afa16e7158b1657ea892e14d99d42285156`
- **Commit Message:** `feat(phase11b): complete responsive UI refinement report and verification across 18 viewports`
- **Python Version:** Python 3.11.0 (Windows x64 [MSC v.1933 64 bit])
- **Node Runtime Version:** v24.19.0
- **Prior Phase Status:** Phase 11I completed (`CLEANUP_PASS_WITH_LIMITATIONS`)

---

## 1. Working Tree State

`git status` prior to Phase 11C audit execution:
- **Staged deletions (reclaimed obsolete backups ~2.23 MB from Phase 11I):**
  - `temp_fail.txt`
  - `templates/index.html.pre_ai_first_20260908.bak`
  - `templates/index.html.pre_gis_dashboard_bak`
  - `templates/index.html.pre_sih_uiux_20260908.bak2`
  - `templates/index.html.pre_uiux_20260908.bak`
- **Tracked modified files:**
  - `.gitignore`: Added `*.bak` rule.
  - `services/pahad_voice_assistant.py`: Hardened safety interlock regex patterns for voice actuation.
  - `templates/index.html`: Research prototype disclaimer banner added (`CLM-12`).
- **Untracked audit documentation:**
  - `docs/PHASE11H_*.md`
  - `docs/PHASE11I_*.md`
  - `reports/pahad_phase11h_forensic_audit_report.json`
  - `scripts/run_phase11h_forensic_audit.py`

`git diff --stat`:
```text
 .gitignore                        | 1 +
 services/pahad_voice_assistant.py | 8 ++++----
 templates/index.html              | 5 +++++
 3 files changed, 10 insertions(+), 4 deletions(-)
```

---

## 2. Deployment & Database Configuration

- **Deployment Manifests:**
  - `vercel.json`: WSGI configuration via `@vercel/python` pointing to `api/index.py` (`maxDuration: 30`).
  - `render.yaml`: gunicorn WSGI service on port 10000.
  - `Dockerfile`: Multi-stage non-root container configuration.
- **Database Configuration:**
  - `DATABASE_URL`: Active PostgreSQL instance (Neon cloud endpoint `ep-wild-wave-awpqskzf`) with PostGIS spatial extension support.
  - Fallback local observation store: `data/observations/pahad_observations.db` (SQLite3).

---

## 3. Important Safety & Environment Variables

| Variable | Configured / Default | Operational Gate State |
|---|---|---|
| `ENABLE_PUBLIC_DISPATCH` | `0` (Default: `0`) | **FAIL-CLOSED** (Civilian SMS/CAP dispatch blocked) |
| `SIREN_DRY_RUN` | `1` (Default: `1`) | **FAIL-CLOSED** (Physical GPIO relay suppressed) |
| `CAP_PRODUCTION_DISPATCH` | `0` (Default: `0`) | **FAIL-CLOSED** (Staging/demo sandbox feeds only) |
| `SACHET_PRODUCTION_DISPATCH` | `0` (Default: `0`) | **FAIL-CLOSED** (NDMA SACHET sandbox gated) |
| `CELL_BROADCAST_PRODUCTION` | `0` (Default: `0`) | **FAIL-CLOSED** (Cell broadcast mock adapter) |
| `PAHAD_DEMO_MODE` | `0` (Default: `0`) | **ISOLATED** (Demo records isolated in `demo_train.csv`) |

---

## 4. Model Artifact Paths & Hashes

| Model File | Size (Bytes) | SHA-256 Hash |
|---|---|---|
| `models/fos_predictor.pkl` | 288,589 | `21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c` |
| `models/pahad_event_calibrator.pkl` | 56,091 | `f3a72b9eb9340990a4b4585799f438d27158d09002b948728f5eae41dbc1b1f8` |
| `models/pahad_event_model.pkl` | 57,100 | `d2094eae9ee6906f5197af5b2fdeb671d6a571080c7f63985b92b95c82ede938` |
| `models/pahad_event_model_6h.pkl` | 61,657 | `e864b26edb1e708aac4ec5c2d95d8c3088ba6310a3b9e79586a093c70e06270e` |
| `models/pahad_event_model_12h.pkl` | 88,702 | `04c2eb5469c4b8a14d0e99cb71380430c695f858cb7e349e78658f335ab24698` |
| `models/pahad_event_model_24h.pkl` | 84,094 | `84cd808a6196cdd5f330756a6b4007234bd9ae7a73d9505cd428ac7589545831` |
| `models/pahad_event_model_48h.pkl` | 62,245 | `61e1f8aff5f3f954560bbeb88cd8ae94e27134ec2e9cfc18a5004bf419f86093` |
| `models/pahad_fos_model.pkl` | 295,094 | `d1b9e91db79d3292fd318c73aaba4b3d5caf0a1119e5a698b24f68a19e1de673` |
| `models/pahad_event_metadata.json` | 2,152 | `9f408b7acb5c77f1a124fcad5e1898cdc42549f855ac4c45e44d89aebc62e77f` |
| `models/pahad_event_metrics.json` | 657 | `8bc174735d5362dd1662b84b918b261a4da720c0be5a27847f5e161fe034d44d` |
