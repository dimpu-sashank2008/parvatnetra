# PARVAT NETRA / PAHAD AI — PHASE 11M
## FINAL EVIDENCE & TRACEABILITY INDEX
**SIH 2026 — TOP-500 → TOP-5 SUBMISSION READINESS**

---

### Purpose
This master index maps every core evaluation claim, mathematical formula, operational workflow, and safety invariant asserted in the SIH 2026 submission package to its exact primary source file, unit test, audit report, live runtime endpoint, and persisted artifact.

---

### Master Submission Evidence Traceability Matrix

| Evaluation Claim / System Dimension | Claim Boundary & Assertion | Primary Source Code | Unit / Regression Test | Authoritative Report | Runtime Endpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Deterministic Physical FoS** | Infinite-slope Mohr-Coulomb limit equilibrium ($\text{FoS} = \tau_f / \tau_d$); deterministic physics, NOT machine learning | `engine/pahad_geotechnical.py`<br/>`engine/pahad_engine.py` | `tests/test_pahad_engine.py`<br/>(11 passed) | `reports/PHASE11J_MODEL_ARTIFACT_PARITY.json` | `/api/pahad/evaluate-sector` |
| **2. Machine Learning Event Model** | Platt-calibrated Gradient Boosting Classifier predicting empirical likelihood across 6h/12h/24h/48h horizons | `engine/pahad_event_classifier.py`<br/>`models/pahad_event_model.pkl` | `tests/test_model_regression.py`<br/>(4 passed) | `models/pahad_event_metadata.json` | `/api/pahad/event-model/status` |
| **3. Ground-Truth Data Provenance** | 36 curated real records (17 events, 19 controls); synthetic samples quarantined in `demo_train.csv` | `data/labels/event_labels.csv`<br/>`data/features/real_train.csv` | `scripts/check_event_leakage.py`<br/>`scripts/verify_phase11m_data_hashes.py` | `reports/PHASE11M_FINAL_DATA_HASHES.json`<br/>`reports/pahad_data_quality_report.md` | `/api/pahad/event-model/data-quality` |
| **4. Temporal Model Honesty** | Recurrent LSTM is a mathematical surrogate; not claimed as a deep neural network | `engine/pahad_lstm.py`<br/>`models/pahad_event_metadata.json` | `tests/test_pahad_phase2.py`<br/>(12 passed) | `docs/PAHAD_MODEL_CARD.md` | `/api/pahad/event-model/status`<br/>(`deep_lstm_status`: `NOT_TRAINED...`) |
| **5. Multi-Signal Corroboration** | 2-of-3 agreement required across FoS, rainfall I-D, and ML; correlated via rain (NOT independent) | `engine/pahad_data_fusion.py`<br/>`services/ai_triage.py` | `tests/test_pahad_data_fusion.py`<br/>(7 passed) | `docs/PHASE11I_CLAIM_MATRIX.md` | `/api/pahad/corroborate-incidents` |
| **6. Composite Risk Index (CRI)** | $H = 0.40S + 0.35P + 0.25A$, $\text{CRI} = H \times V \times 100$; operational index, not calibrated probability | `engine/pahad_data_fusion.py`<br/>`backend/realtime_cri.py` | `tests/test_phase11j_smoke.py`<br/>(10 passed) | `reports/PHASE11M_FINAL_RUNTIME_SNAPSHOT.json` | `/api/pahad/highest-risk-corridor` |
| **7. Primary Corridor Runtime State** | `SK-NH10-KM48`: CRI 45.50 (HIGH), FoS 0.971 (CRITICAL), Rain 33.3mm, P(ev) 4.97% | `app.py`<br/>(line 2180) | `scripts/generate_phase11m_snapshot.py` | `reports/PHASE11M_FINAL_RUNTIME_SNAPSHOT.json` | `/api/pahad/highest-risk-corridor` |
| **8. 4-Tier Weather Failover** | IMD $\to$ Open-Meteo $\to$ Disk Cache ($900\text{s}$ TTL) $\to$ Himalayan Climatological Model | `services/weather_service.py`<br/>`data/cache/weather/` | `tests/test_weather_service.py`<br/>(8 passed) | `docs/PHASE11H_SCIENTIFIC_INTEGRITY_AUDIT.md` | `/api/weather/status` |
| **9. Live Seismic Feed & Fallback** | Live USGS global feed ($M \ge 2.5$) with automated fallback for unconfigured NCS | `services/seismic_service.py`<br/>`data/cache/seismic/` | `tests/test_seismic_service.py`<br/>(6 passed) | `docs/PHASE11L_DEFENSE_BASELINE.md` | `/api/pahad/data-status` |
| **10. Siren Dry-Run Safety Lock** | `SIREN_DRY_RUN=1` forces `DRY_RUN_EMULATOR`; zero physical output can sound | `backend/edge/siren_controller.py`<br/>`services/siren_controller.py` | `scratch/test_safety_gates.py`<br/>`tests/test_phase7g_rbac.py` | `reports/pahad_phase11h_forensic_audit_report.json`| `/api/siren/status` |
| **11. Voice Assistant Interlocks** | 7 forbidden actuation patterns (siren, evacuation dispatch, override) intercepted by regex | `services/pahad_voice_assistant.py`<br/>lines 33–44 | `tests/test_phase10d_voice_hardening.py`<br/>`scratch/test_safety_gates.py` | `docs/PHASE11I_CODE_CLAIM_REMEDIATION.md` | `/api/pahad/assistant/chat` |
| **12. Public Alert Gating** | `ENABLE_PUBLIC_DISPATCH=0`, `CAP_PRODUCTION_DISPATCH=0`; cell broadcast locked | `app.py`<br/>`services/eoc_service.py` | `scratch/test_safety_gates.py` | `docs/PHASE11J_DEPLOYMENT_HARDENING_REPORT.md` | `/api/eoc/incidents/<id>/dispatch` |
| **13. Role-Based Access Control** | Privilege separation across `PUBLIC`, `FIELD_OPERATOR`, `AUTHORITY`, and `ADMIN` | `services/authority_review_service.py`<br/>`engine/operational_state_machine.py` | `tests/test_phase7g_rbac.py`<br/>(7 passed) | `docs/PHASE7I_SECURITY_AUDIT_REPORT.md` | `/api/eoc/incidents` |
| **14. Offline BRO Bypass Routing** | Multi-profile Dijkstra routing (FASTEST, SHORTEST, SAFEST via NH-717A) on embedded graph | `services/offline_routing_service.py`<br/>`backend/tactical_router.py` | `tests/test_terrain_api.py`<br/>(12 passed) | `docs/PHASE11J_DEPLOYMENT_HARDENING_REPORT.md` | `/api/pahad/routing/calculate-bypass` |
| **15. 15 km Corridor Geofencing** | Haversine geodesic buffer calculating affected settlements (29th Mile, Singtam) | `services/eoc_service.py`<br/>lines 98–140 | `tests/test_phase11j_smoke.py` | `reports/PHASE11M_FINAL_RUNTIME_SNAPSHOT.json` | `/api/eoc/incidents/<id>/geofence` |
| **16. Statutory DMA 2005 Alignment** | AI produces recommendations; human statutory authority decides under Section 30 | `services/eoc_service.py`<br/>`templates/index.html` | `scratch/test_safety_gates.py` | `docs/PHASE11L_SIH_JUDGE_DEFENSE.md` | `/api/eoc/command-brief` |
| **17. OASIS CAP v1.2 Feed** | Standardized emergency alert XML generation for test feeds; production locked | `engine/pahad_cap.py`<br/>`services/public_warning_service.py` | `tests/test_phase11j_smoke.py` | `docs/PHASE11A_PUBLIC_DEPLOYMENT_REPORT.md` | `/api/pahad/generate-cap` |
| **18. Cryptographic Audit Trail** | HMAC-SHA256 signed authority commands with append-only SQLite incident logging | `data/observations/pahad_observations.db`<br/>`services/eoc_service.py` | `tests/test_phase7g_audit.py` | `docs/PHASE8_EOC_OPERATIONS_REPORT.md` | `/api/eoc/incidents/<id>/transition` |
| **19. Zero CDN / Offline Packaged** | Leaflet maps, CSS styles, and JavaScript assets packaged locally in `/static/` | `static/css/`, `static/js/`,<br/>`public/static/` | `scripts/audit_phase11j_assets_and_hosts.py` | `reports/PHASE11J_STATIC_AND_HOST_AUDIT.json` | `/static/` |
| **20. Model & Data Parity** | 10 model files and 6 datasets verified bit-for-bit against authoritative baseline hashes | `models/`, `data/features/`,<br/>`data/labels/` | `scripts/verify_phase11m_model_hashes.py`<br/>`scripts/verify_phase11m_data_hashes.py` | `reports/PHASE11M_FINAL_MODEL_HASHES.json`<br/>`reports/PHASE11M_FINAL_DATA_HASHES.json` | Local Artifact Inspection |

---
**Document Status:** COMPLETE & FROZEN (Phase 11M)  
**Verification Coverage:** 100% of major claims backed by code, tests, reports, and live endpoints
