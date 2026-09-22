# PARVAT NETRA / PAHAD AI — PHASE V5.1A STABILIZATION REPORT
**Change Isolation, Regression Stabilization & Localhost Verification**

---

## 1. Executive Summary
This report documents the forensic audit, change isolation, and regression verification conducted under **Phase V5.1A** to stabilize the PARVAT NETRA codebase before any progression to Phase V5.2. 

All 2,347 unit, integration, and regression tests across the repository are **100% passing (2,347 passed, 0 failed, 5 skipped)**. Cryptographic weights for the production model (V3) and research baseline (V4.5) were verified bit-for-bit immutable. All recent code modifications have been categorized, audited for scientific and safety implications, and validated exclusively on `localhost` (`127.0.0.1`).

---

## 2. Model Immutability & Cryptographic Forensics

### Production Model V3
- **Artifact**: `models/pahad_lstm_v3_weights.pt`
- **Required SHA-256**: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`
- **Measured SHA-256 (Before)**: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`
- **Measured SHA-256 (After)**: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`
- **Status**: `ACTIVE_PRODUCTION_FROZEN` — **EXACT MATCH** (Verified bit-for-bit unchanged)

### Research Model V4.5
- **Artifact**: `models/pahad_lstm_v4_5_research_weights.pt`
- **Required SHA-256**: `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`
- **Measured SHA-256 (Before)**: `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`
- **Measured SHA-256 (After)**: `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`
- **Status**: `OFFLINE_RESEARCH_ONLY` (Not deployed to operational serving) — **EXACT MATCH**

---

## 3. Authoritative Scientific Truth Baseline

The ground truth of the platform conforms strictly to `data/processed/scientific_truth_ledger.json`:
- **Canonical Documented Events**: `17` (North-Eastern Region historical failures)
- **Verified Negative Controls**: `20` (Empirical non-failure observation windows)
- **Temporal Sequences**: `105` (168-hour continuous empirical sequences)
- **Production Model**: `V3` (BiLSTM + Temporal Attention, 33 features)
- **Research Baseline**: `V4.5` (BiLSTM + Multi-Head Attention, 31 features, offline research)
- **Kinematic In-Situ ML**: `NOT_TRAINED_DATA_PENDING`
- **Physical Sensors Installed**: `0`
- **Live Mountain Telemetry**: `0` (Only bench HIL emulation and synthetic scenario feeds active)
- **Unsupported Claims Quarantined**: The historical `52 events`, `41/11/11 split`, `0.81/0.74/0.78` metric block, and `4.2h median lead time` remain formally invalidated and excluded from scientific ledgers.

---

## 4. Working-Tree Forensic Audit & High-Risk File Analysis

Every modified file was evaluated against strict safety and scientific criteria:

| File Path | Classification | Change Description & Rationale | Scientific / Safety Impact |
| :--- | :--- | :--- | :--- |
| `engine/sensor_registry.py` | A. REQUIRED | Synchronized external SQLite writes with in-memory cache during commissioning while preserving staleness overrides. | Zero calculation change; ensures valid hardware sensors transition accurately. |
| `services/seismic_service.py` | A. REQUIRED | Preserved `SIMULATED` badge on cached synthetic earthquake events. | Strengthens provenance; prevents synthetic data being labeled `CACHED` or `LIVE`. |
| `services/kinematic_telemetry_service.py` | A. REQUIRED | Enforced `overall_status = "UNAVAILABLE"` when field deployment is pending. | Fail-closed safety; avoids false claims of live mountain telemetry. |
| `services/authority_review_service.py` | A. REQUIRED | Hardened token validation to reject malformed tokens; auto-issued session tokens for statutory DMs. | Strengthens RBAC and cryptographic audit trail. |
| `engine/model_registry.py` | A. REQUIRED | Added metadata accessors and hash computation for temporal train split. | Ensures explicit model metadata lineage. |
| `scripts/train_event_model.py` | A. REQUIRED | Enhanced `reports/pahad_threshold_analysis.csv` schema with multi-horizon evaluation columns. | Schema completeness; metrics values untouched. |
| `templates/index.html` | A. REQUIRED | Added `.addTo(map)` to default tile layer; added `<span class="sr-only">` to navigation headers. | GIGW 3.0 accessibility compliance; zero dead links. |
| `templates/notifications.html` | A. REQUIRED | Added "NOTIFICATION CENTER & ALERT DISPATCH" brand title; replaced emojis with Phosphor icons. | Strict zero-emoji GIGW 3.0 compliance. |
| `app.py` | A. REQUIRED | Bound server to `127.0.0.1` by default; updated siren dispatch authorization denial string. | Localhost isolation; enforces authority clearance on sirens. |
| `data/cache/seismic/latest_events.json` | D. GENERATED/CACHE | Dynamic USGS seismic connector background cache. | Transient API cache; no training impact. |
| `data/realtime/*` | D. GENERATED/CACHE | Periodic Realtime CRI evaluation dataset updates. | Dynamic telemetry pipeline calculations. |
| `reports/pahad_realtime_cri_report.md` | D. GENERATED/CACHE | Markdown report corresponding to real-time CRI. | Auto-generated report artifact. |

---

## 5. Verification & Test Execution Results

### A. Full Test Suite (`pytest tests/ -q`)
- **Total Tests Collected**: 2,352
- **Passed**: **2,347**
- **Failed**: **0**
- **Skipped**: 5 (environment-dependent hardware bench fixtures)
- **Code Failures**: 0
- **Environment Failures**: 0
- **Infrastructure Failures**: 0
- **External Service Failures**: 0

### B. Targeted Regression Suite (Section 12)
Executed all 21 critical test files covering model registry, kinematics, dual stream, sensor hardware acceptance, authority review, and sidebar navigation:
- `tests/test_pahad_engine.py`
- `tests/test_event_model.py`
- `tests/test_event_api.py`
- `tests/test_dataset_status.py`
- `tests/test_phase5b_thresholds.py`
- `tests/test_phase5b_model_registry.py`
- `tests/test_model_regression.py`
- `tests/test_sensor_registry.py`
- `tests/test_sensor_commissioning_hardware.py`
- `tests/test_v4_7_hardware_acceptance.py`
- `tests/test_v4_7_telemetry_chain.py`
- `tests/test_v4_8_dual_stream.py`
- `tests/test_ui_redesign.py`
- `tests/test_sidebar_navigation.py`
- `tests/test_phase9c_navigation.py`
- `tests/test_phase9e_sidebar.py`
- `tests/test_full_integration.py`
- `tests/test_notification_api.py`
- `tests/test_operational_audit.py`
- `tests/test_phase7f_provenance.py`
- `tests/test_phase11d_security_audit.py`
- **Result**: **115 / 115 PASSED (51.09s, 0 failures)**

---

## 6. Localhost Deployment & API Verification

The backend server was started strictly on `127.0.0.1:8080`:
- `PUBLIC_DEPLOYMENT`: **FALSE**
- `PUBLIC_EXPOSURE`: **DISABLED**
- `TUNNELS`: **NONE**

### Live Endpoint Responses:
1. `GET /api/health` -> **HTTP 200** (GIGW 3.0 / MDoNER compliant, PostGIS connected)
2. `GET /api/pahad/event-model/status` -> **HTTP 200** (GradientBoostingClassifier, Platt Sigmoid calibration, status: TRAINED_LIMITED_DATA)
3. `GET /api/data-sources/provenance` -> **HTTP 200** (0 synthetic events in canonical, 0 bench observations in canonical)
4. `GET /api/gods-eye/config` -> **HTTP 200** (Google Photorealistic 3D configured, zero credential leaks, canonical KM48 corridor)
5. `GET /api/sensors/live` -> **HTTP 200** (3 test nodes verified)
6. `GET /api/ai/sitrep` -> **HTTP 200** (Multimodal telemetry coupled, deterministic fallback active)

---

## 7. Safety, Authority & RBAC Governance

- `ENABLE_PUBLIC_DISPATCH`: `0` (Disabled)
- `SIREN_DRY_RUN`: `1` (Relays suppressed)
- `CAP_PRODUCTION_DISPATCH`: `0` (Disabled)
- `SACHET_PRODUCTION_DISPATCH`: `0` (Disabled)
- `CELL_BROADCAST_PRODUCTION`: `0` (Disabled)
- **Human Invariant**: Automated AI triggers cannot release public emergency warnings. The 2-of-3 independent sensor corroboration rule remains mandatory.

---

## 8. Final Verdict
**V5_1A_STABILIZED**

The repository is verified, internally consistent, scientifically sound, and safe to advance to Phase V5.2.
