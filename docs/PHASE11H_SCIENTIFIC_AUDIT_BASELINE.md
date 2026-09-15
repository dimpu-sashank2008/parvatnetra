# PARVAT NETRA / PAHAD AI -- PHASE 11H SCIENTIFIC & SAFETY AUDIT BASELINE

**Document ID**: PAHAD-AUDIT-BASELINE-PHASE11H  
**Classification**: Forensic Audit Protocol Baseline  
**Timestamp**: 2026-09-14T15:38:00Z  
**Auditor**: Autonomous AI Systems Engineering & Disaster Governance Team  
**Scope**: Reconciliation of claims vs code, data, models, APIs, and safety gates  

---

## 1. Repository & Commit Baseline

- **Current Git Commit**: 4c439af (feat(phase11b): complete responsive UI refinement report and verification across 18 viewports)
- **Active Git Branch**: main (Synchronized with staging and remote origin/main)
- **Working Tree State**: Clean (nothing to commit, working tree clean)
- **Remote URL**: https://github.com/dimpu-sashank2008/parvatnetra.git
- **Platform Runtime**: Python 3.11.0 (Windows / Linux containerized via Docker)

---

## 2. Existing Phase 11 Reports & Reference Claims

The following Phase 11 documentation artifacts exist in docs/:

1. docs/PHASE11A_DEPLOYMENT_BASELINE.md (4,158 bytes) -- Baseline for cloud staging deployment.
2. docs/PHASE11A_DEPLOYMENT_RUNBOOK.md (4,130 bytes) -- Runbook for Render, Railway, and Vercel hosting.
3. docs/PHASE11A_EXECUTION_LOG.md (3,431 bytes) -- Checkpoint execution log for Phase 11A.
4. docs/PHASE11A_PUBLIC_DEPLOYMENT_REPORT.md (3,799 bytes) -- Claims live URLs, 50m geofence demo, model status.
5. docs/PHASE11B_RESPONSIVE_BASELINE.md (11,584 bytes) -- Responsive baseline audit.
6. docs/PHASE11B_RESPONSIVE_REPORT.md (9,067 bytes) -- Viewport audit log.
7. docs/PHASE11B_RESPONSIVE_UI_REPORT.md (14,016 bytes) -- Comprehensive 18-breakpoint responsive validation report.

*Audit Note: All claims in these reports are treated strictly as unverified claims until cross-examined against actual source code and runtime telemetry.*

---

## 3. Current Model Artifacts Inventory (models/)

The models/ directory contains 16 files:

| Filename | File Size | Description / Target |
| :--- | :---: | :--- |
| pahad_fos_model.pkl | 295,094 bytes | Geotechnical Factor of Safety model bundle (Target: continuous FoS) |
| pahad_fos_model.metadata.json | 663 bytes | FoS model metadata, training parameters, features |
| os_predictor.pkl | 288,589 bytes | Secondary/legacy FoS estimator |
| pahad_event_model.pkl | 57,100 bytes | Primary Landslide Event Classifier (GradientBoostingClassifier) |
| pahad_event_model.metadata.json| 2,152 bytes | Metadata: SHA-256 dataset hash, features, performance |
| pahad_event_metadata.json | 2,152 bytes | Event model metadata duplicate |
| pahad_event_metrics.json | 657 bytes | Reported metrics summary (AUC, PR-AUC, Brier score) |
| pahad_event_calibrator.pkl | 56,091 bytes | Isotonic/Platt probability calibration wrapper |
| pahad_event_model_6h.pkl | 61,657 bytes | 6-hour antecedent forecast horizon classifier |
| pahad_event_model_12h.pkl | 88,702 bytes | 12-hour forecast horizon classifier |
| pahad_event_model_24h.pkl | 84,094 bytes | 24-hour forecast horizon classifier |
| pahad_event_model_48h.pkl | 62,245 bytes | 48-hour forecast horizon classifier |
| phase5b_multi_horizon_metrics.json| 6,816 bytes | Multi-horizon comparative metrics catalog |
| pahad_feature_schema.json | 9,384 bytes | Canonical feature definitions, units, bounds |
| pahad_ood_bounds.json | 5,460 bytes | Out-of-Distribution empirical envelope bounds |
| pahad_training_metrics.json | 657 bytes | Historical training loss & metric curves |

---

## 4. Current Datasets Inventory (data/)

Key datasets present in data/:

- data/raw/historical_landslides_ner.csv: 17 documented historical landslides across 8 NER states.
- data/processed/pahad_event_observations.csv: Reconciled event observation dataset.
- data/processed/phase5b_temporal_*.csv: Antecedent multi-horizon temporal windows (N=105).
- data/features/real_train.csv, 
eal_val.csv, 
eal_test.csv: Separated real event training partitions.
- data/features/demo_train.csv: Synthetic/demo dataset isolated from operational training.
- data/cache/weather/, data/cache/seismic/, data/cache/iot_telemetry/: Live telemetry caches with TTL expiration.
- data/splits/: Partition split manifests with temporal holdout index definitions.

---

## 5. Current Safety-Related Environment Variables

Environment variables checked at baseline:

| Variable | Current Baseline Value | Intended Fail-Safe Behavior |
| :--- | :---: | :--- |
| ENABLE_PUBLIC_DISPATCH | <UNSET> (Default: 0) | Public emergency broadcast disabled |
| SIREN_DRY_RUN | <UNSET> (Default: 1) | Acoustic sirens in simulation / dry-run mode |
| CAP_PRODUCTION_DISPATCH| <UNSET> (Default: 0) | National CAP XML dispatch suppressed |
| SACHET_PRODUCTION_DISPATCH| <UNSET> (Default: 0) | NDMA SACHET production dispatch suppressed |
| CELL_BROADCAST_PRODUCTION| <UNSET> (Default: 0) | Civilian cell broadcast disabled |
| PUBLIC_DEMO_TEST_ONLY | <UNSET> (Default: 1) | Evaluator drills isolated to session memory |
| PAHAD_DEMO_MODE | <UNSET> (Default: 0) | Operational models prioritize real physics/data |
| FLASK_ENV | <UNSET> (Default: production) | Production security defaults |
| DATABASE_URL | Configured | Neon Serverless PostgreSQL with SQLite fallback |

*All safety interlocks default to strict fail-closed state when variables are unset.*

---

## 6. Core Application Endpoints Under Audit

Over 85 endpoints mapped in pp.py:
- **Core Views**: /, /demo, /notifications, /pahad-ai, /climate-map, /seismic, /terrain-3d, /edge-network, /login, /health.
- **Inference & Risk**: /api/pahad/predict-event, /api/pahad/evaluate-sector, /api/pahad/highest-risk-corridor, /api/pahad/fused-risk, /api/ml/latest-risk.
- **Geotechnical & IoT**: /api/sensors/live, /api/telemetry/devices, /api/siren/activate, /api/siren/status.
- **Spatial & Warning**: /api/warning/cap/<incident_id>, /api/sms/queue-emergency, /api/routing/evacuation-plan, /api/reports/clustered.

---

## 7. Current Test Suite Status

- Mandated core regression test suite (	ests/test_pahad_engine.py, 	est_pahad_phase2.py, 	est_pahad_phase3.py, 	est_pahad_data_fusion.py, 	est_weather_service.py, 	est_seismic_service.py, 	est_terrain_api.py, 	est_i18n_localization.py, 	est_model_regression.py): **80/80 passed (100%)**.

---

## 8. Baseline Safety Invariant Lock

- Zero alterations to scientific prediction formulas during baseline.
- Zero modifications to safety gates, thresholds, or siren relay configurations.
- Working tree remains completely clean.
