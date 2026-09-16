# PARVAT NETRA • PAHAD AI — PHASE 12D BASELINE AUDIT

**Audit Date**: 2026-09-16  
**Auditor**: PARVAT NETRA Autonomous Defense Swarm  
**Git Branch**: `main`  
**Git Commit**: `dd9e57dc6452e0a70ad98731de0c536af8e50cb0` (Ahead of origin by 3 commits)  
**Verification Baseline**: Phase 11F (`29/29`), Phase 12A (`24/24`), Phase 12B (`17/17`), Phase 12C (`12/12`)  

---

## 1. Commit & Working Tree Audit

### 1.1 Git Status & Diff Summary
- **Current Branch**: `main`
- **Current HEAD Revision**: `dd9e57dc6452e0a70ad98731de0c536af8e50cb0`
- **Total Modified Files**: 13
- **Total Untracked Files**: 10

### 1.2 Modified Files Inspection & Intentionality Audit

| File Path | Status | Change Description | Intentionality Determination |
| :--- | :---: | :--- | :--- |
| `app.py` | MODIFIED | Added `GET /api/pahad/explanation/<corridor_id>`, integrated `LiveDataStatusAuditor` in `/api/pahad/data-status`, fixed `load_env()` `setdefault` to preserve test environment, and added RBAC 400 validation on incident report status. | **INTENTIONAL**: Required by Phase 12C contract, data truth disclosures, and RBAC endpoint security. |
| `templates/index.html` | MODIFIED | Added `#pahad-evidence-matrix` UI panel, wired explanation fetch on corridor change, enforced `window.NER_BOUNDS` regional fit, added `window.pahadMapViewState` (`INITIAL_VIEW`, `NER_OVERVIEW`, `CORRIDOR_VIEW`), and prevented polling zoom via `onCorridorSelectionChanged(..., false)`. | **INTENTIONAL**: Required by Phase 12C explainability visualization and Phase 12 GIS default NER overview defense. |
| `services/pahad_voice_assistant.py` | MODIFIED | Grounded voice queries with `PahadExplanationEngine` & `LiveDataStatusAuditor`, added DMA 2005 read-only safety interlock rejecting emergency actuations with `status: "REJECTED_SAFETY"`. | **INTENTIONAL**: Required by Phase 12C statutory voice grounding. |
| `static/js/pahad_gis_animation.js` | MODIFIED | Added `shouldZoom` control to `onCorridorChanged` and `loadCorridorData` to suppress auto-panning during temporal playback. | **INTENTIONAL**: Preserves user map viewport stability. |
| `public/static/js/pahad_gis_animation.js` | MODIFIED | Synchronized with `static/js/pahad_gis_animation.js`. | **INTENTIONAL**: Asset distribution parity. |
| `templates/login_authority.html` | MODIFIED | Added role selection credentials helper for authority vs field operator vs citizen. | **INTENTIONAL**: EOC login demonstration clarity. |
| `tests/test_ner_gis_default_view.py` | MODIFIED | Added comprehensive tests for NER 8-state boundaries, bounding box, layer panes, view states, and reset button. | **INTENTIONAL**: GIS regression defense suite. |
| `data/cache/*` | MODIFIED | Updated timestamps for local weather and seismic caches from test executions. | **INTENTIONAL**: Dynamic cache freshening. |
| `data/realtime/*`, `reports/*` | MODIFIED | Realtime CRI dataset and audit generated during test execution. | **INTENTIONAL**: Pipeline verification artifacts. |

### 1.3 Untracked Files Inspection
- `data/manifests/phase12c_explainability_manifest.json`: Phase 12C cryptographic SHA-256 manifest.
- `docs/PHASE12C_*.md` (4 files): Comprehensive Phase 12C explainability, data truth, voice grounding, and judge matrix reports.
- `docs/PHASE12_GIS_HAZARD_ANIMATION_REPORT.md`: GIS hazard animation documentation.
- `engine/pahad_explanation_engine.py`: Phase 12C authoritative explanation engine, `RiskChangeEngine`, and `LiveDataStatusAuditor`.
- `tests/test_phase12c_*.py` (3 files): Phase 12C test suites.

**Audit Finding**: Zero accidental or destructive uncommitted modifications exist. All files constitute legitimate, verified deliverables from Phase 12, Phase 12A, 12B, and 12C.

---

## 2. Frozen Architectural Invariants

The following invariants are strictly frozen for Phase 12D:

1. **Life Safety Gates**:
   - `ENABLE_PUBLIC_DISPATCH=0`
   - `SIREN_DRY_RUN=1`
   - `CAP_PRODUCTION_DISPATCH=0`
   - `SACHET_PRODUCTION_DISPATCH=0`
   - `CELL_BROADCAST_PRODUCTION=0`
   - `PUBLIC_DEMO_TEST_ONLY=1`
   - Voice assistant is **strictly read-only advisory**. Actuations are unconditionally rejected under DMA 2005.

2. **Model Status & Honesty**:
   - Recurrent Neural Network (LSTM / GRU): **`NOT_TRAINED / PHYSICS-INFORMED TEMPORAL SURROGATE`**.
   - Temporal Training Gate: **`DATA_COLLECTION_REQUIRED`** (Training hard-blocked).
   - Operational Classifier: **`TRAINED_LIMITED_DATA / RESEARCH PROTOTYPE`** ($N=17$ historical failure events, $N=8$ held-out test records).
   - FoS Model: Infinite slope Mohr-Coulomb limit equilibrium equation ($FoS = \frac{c' + (\gamma z \cos^2\beta - u)\tan\phi'}{\gamma z \sin\beta\cos\beta}$).

3. **GIS Navigation Integrity**:
   - Initial Map View: Full Northeast India (NER) bounding box spanning all 8 states ($[21.8^\circ\text{N}, 88.0^\circ\text{E}]$ to $[29.5^\circ\text{N}, 97.5^\circ\text{E}]$).
   - Zero auto-zoom to individual corridors or clusters on initial page load or during background polling.
   - `Risk Evolution` remains an on-map temporal animation layer.
   - `Risk Evaluation` remains a distinct analytical modal.

4. **Role Separation**:
   - Public/Citizen: Read-only risk maps, public alerts, citizen reporting. No authority review, approvals, dispatch, or sirens.
   - Field Operator: Telemetry collection, incident verification, offline sync. No dispatch authorization or sirens.
   - Authority / EOC: Two-man rule alert verification, SOP dispatch authorization (dry-run guarded).

---

## 3. Known System Risks & Defense Strategy

| Identified Risk | System Defense Mechanism | Judge Response Strategy |
| :--- | :--- | :--- |
| **Small Sample Size ($N=17$ events)** | Formal status `TRAINED_LIMITED_DATA`; explicit disclosure of held-out set ($N=8$). | State openly: *"The current model produces strong point metrics on a very small held-out test set, so we treat it as a research prototype rather than deployment-grade evidence."* |
| **Untrained Recurrent Model (LSTM)** | `pahad_temporal_gate.py` hard gate throwing `TemporalReadinessError`; CLI refuses execution. | Explain: *"LSTM is not trained because real continuous sensor sequences do not yet exist. We chose scientific integrity over fake temporal accuracy."* |
| **External API Outages (IMD / NCS)** | Automated graceful fallback to Open-Meteo and USGS with explicit provenance badging (`[LIVE / FALLBACK]`, `[AUTH_REQUIRED]`). | Demonstrate live fallback flags in `/api/pahad/data-status`. |
| **Unauthorized Emergency Actuation** | DMA 2005 Section 34(c) interlock rejecting non-authorized triggers; production dispatch flags set to `0`. | Attack voice assistant with *"Sound the siren"* to show instant rejection. |
| **GIS Viewport Drift** | Polling calls pass `shouldZoom=false`; view states strictly tracked. | Demonstrate continuous 10s polling with zero map jerking or unexpected zooms. |

---

**Baseline Audit Conclusion**: The repository is clean, verified, coherent, and ready for Adversarial Judge Testing and Demo Hardening.
