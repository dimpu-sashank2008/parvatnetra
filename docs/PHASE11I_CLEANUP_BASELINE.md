# PARVAT NETRA / PAHAD AI — PHASE 11I CLEANUP & HARDENING BASELINE
**Baseline State Prior to Codebase Cleanup, Claim Remediation, and Production Hygiene**

- **Date:** September 15, 2026
- **Branch:** `main`
- **Baseline Git Commit:** `4c439afa16e7158b1657ea892e14d99d42285156`
- **Commit Message:** `feat(phase11b): complete responsive UI refinement report and verification across 18 viewports`
- **Python Runtime:** Python 3.11.0 (Windows x64)
- **Node Runtime:** v24.19.0
- **Prior Audit Phase Verdict:** `INTEGRITY_PASS_WITH_LIMITATIONS` (Phase 11H)

---

## 1. Safety Configuration Invariants

The following safety parameters are enforced across `.env`, `app.py`, `routes/siren.py`, and `backend/cap_handler.py`:

| Parameter | Baseline Value | Hard Enforcement Status |
|---|---|---|
| `ENABLE_PUBLIC_DISPATCH` | `0` | **FAIL-CLOSED** (Civilian SMS/CAP dispatch blocked) |
| `SIREN_DRY_RUN` | `1` | **FAIL-CLOSED** (Physical GPIO relay decoupled) |
| `CAP_PRODUCTION_DISPATCH` | `0` | **FAIL-CLOSED** (CAP feeds restricted to staging/demo) |
| `SACHET_PRODUCTION_DISPATCH` | `0` | **FAIL-CLOSED** (NDMA SACHET sandbox gated) |
| `CELL_BROADCAST_PRODUCTION` | `0` | **FAIL-CLOSED** (Emergency cell broadcast mock only) |
| `PAHAD_DEMO_MODE` | `0` (or `1` in evaluator demo) | **ISOLATED** (Demo uses synthetic overlay) |

---

## 2. Working-Tree Status

`git status` prior to cleanup:
- **Modified files:**
  - `services/pahad_voice_assistant.py`: Phase 11H CP25 safety interlock regex tightening (catching compound modifiers like `"emergency siren"`, `"emergency evacuation alert"`).
  - `data/cache/weather/`: Ephemeral meteorological cache updates from test suite and live Open-Meteo fetches.
  - `data/cache/seismic/latest_events.json`: Ephemeral seismic cache update.
- **Untracked files:**
  - `docs/PHASE11H_SCIENTIFIC_AUDIT_BASELINE.md`
  - `docs/PHASE11H_CLAIM_AUDIT.md`
  - `docs/PHASE11H_RISK_REGISTER.md`
  - `docs/PHASE11H_SCIENTIFIC_INTEGRITY_AUDIT.md`
  - `reports/pahad_phase11h_forensic_audit_report.json`
  - `scripts/run_phase11h_forensic_audit.py`

---

## 3. Model Artifact SHA-256 Hashes

| Model File | File Size (Bytes) | SHA-256 Prefix (First 16 chars) | Full SHA-256 Hash |
|---|---|---|---|
| `models/fos_predictor.pkl` | 288,589 | `21206e6f98ed77c1` | `21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c` |
| `models/pahad_event_calibrator.pkl` | 56,091 | `f3a72b9eb9340990` | `f3a72b9eb9340990a4b4585799f438d27158d09002b948728f5eae41dbc1b1f8` |
| `models/pahad_event_model.pkl` | 57,100 | `d2094eae9ee6906f` | `d2094eae9ee6906f5197af5b2fdeb671d6a571080c7f63985b92b95c82ede938` |
| `models/pahad_event_model_6h.pkl` | 61,657 | `e864b26edb1e708a` | `e864b26edb1e708aac4ec5c2d95d8c3088ba6310a3b9e79586a093c70e06270e` |
| `models/pahad_event_model_12h.pkl` | 88,702 | `04c2eb5469c4b8a1` | `04c2eb5469c4b8a14d0e99cb71380430c695f858cb7e349e78658f335ab24698` |
| `models/pahad_event_model_24h.pkl` | 84,094 | `84cd808a6196cdd5` | `84cd808a6196cdd5f330756a6b4007234bd9ae7a73d9505cd428ac7589545831` |
| `models/pahad_event_model_48h.pkl` | 62,245 | `61e1f8aff5f3f954` | `61e1f8aff5f3f954560bbeb88cd8ae94e27134ec2e9cfc18a5004bf419f86093` |
| `models/pahad_fos_model.pkl` | 295,094 | `d1b9e91db79d3292` | `d1b9e91db79d3292fd318c73aaba4b3d5caf0a1119e5a698b24f68a19e1de673` |
| `models/pahad_event_metadata.json` | 2,152 | `9f408b7acb5c77f1` | `9f408b7acb5c77f1a124fcad5e1898cdc42549f855ac4c45e44d89aebc62e77f` |
| `models/pahad_event_metrics.json` | 657 | `8bc174735d5362dd` | `8bc174735d5362dd1662b84b918b261a4da720c0be5a27847f5e161fe034d44d` |

---

## 4. Test Suite Baseline Inventory

Core Regression Test Command:
```bash
python -m pytest \
  tests/test_pahad_engine.py \
  tests/test_pahad_phase2.py \
  tests/test_pahad_phase3.py \
  tests/test_pahad_data_fusion.py \
  tests/test_weather_service.py \
  tests/test_seismic_service.py \
  tests/test_terrain_api.py \
  tests/test_i18n_localization.py \
  tests/test_model_regression.py
```
- **Test Result:** 80 passed in 292.22s (100% pass rate). Zero failures, zero errors, zero skips.

---

## 5. Deployment & Production Configuration Inventory

- **Vercel Manifest:** `vercel.json` routing WSGI via `api/index.py` with Python 3.9/3.11 builder.
- **Render Manifest:** `render.yaml` defining gunicorn WSGI service on port 10000.
- **Docker Manifest:** `Dockerfile` multi-stage build with non-root security context.
- **Environment Schema:** `.env.example` documenting 42 configuration variables across 8 security tiers.
