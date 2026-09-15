# PARVAT NETRA / PAHAD AI — PHASE 11K
## DEMO BASELINE & REPRODUCIBILITY MANIFEST
**SIH 2026 — TOP-500 → TOP-5 EVALUATION PREPARATION**

---

### 1. Git Repository Baseline

| Property | Recorded State | Status / Verification |
| :--- | :--- | :--- |
| **Active Branch** | `main` | Authoritative Release Branch |
| **Tracking Branch** | `origin/main` (Up to date) | Synchronized with origin |
| **Latest Commit Hash** | `4c439afa16e7158b1657ea892e14d99d42285156` | Verified via `git log -1` |
| **Commit Message** | `feat(phase11b): complete responsive UI refinement report and verification across 18 viewports` | Stable Evaluated Base |
| **Pre-Demo Working State** | Tracked Phase 11H/I/J claim mitigations in `templates/index.html`, `services/pahad_voice_assistant.py`, `render.yaml`, `app.py` | Audited and verified |
| **Git Diff Check (`git diff --check`)** | Clean (0 conflict markers, 0 trailing whitespace violations) | **PASS** |

#### Git Diff Stat Summary
```text
 .gitignore                            |  3 +++
 app.py                                | 38 ++++++++++++++++++++++++++++-------
 data/cache/seismic/latest_events.json |  4 ++--
 render.yaml                           |  4 ++--
 services/pahad_voice_assistant.py     | 10 ++++-----
 templates/index.html                  | 21 +++++++++++++------
 6 files changed, 58 insertions(+), 22 deletions(-)
```

---

### 2. Runtime Deployment Configuration

| Component | Target Parameter | Configured Value | Verification |
| :--- | :--- | :--- | :--- |
| **Platform Target** | Cloud Web Service | Render (`render.yaml`) / Docker | Dockerized Container |
| **Runtime Base** | Python 3.11 Base Image | `python:3.11-slim` | Confirmed |
| **Service Port** | HTTP Listening Port | `PORT=8080` / `FLASK_PORT=8080` | Confirmed |
| **Health Check Path** | Container Liveness Check | `/health` (HTTP 200) | Validated |
| **API Health Path** | Application Health Endpoint | `/api/health` (Reports subsystems) | Validated |
| **Static File Delivery** | Leaflet / CSS / JS Assets | Local Self-Contained (`/static/`) | Zero CDN Dependency |
| **Local LLM Gateway** | OmniRoute Router | `http://localhost:20128/v1` | Deterministic Fallback Active |

---

### 3. Machine Learning & Geotechnical Model Parity (SHA-256)

Every model artifact in `models/` is verified bit-for-bit against authoritative cryptographic hashes:

| Artifact Name | Size (Bytes) | SHA-256 Digest | Provenance & Role |
| :--- | :--- | :--- | :--- |
| `fos_predictor.pkl` | 288,589 | `21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c` | Geotechnical Factor of Safety ML Predictor |
| `pahad_fos_model.pkl` | 295,094 | `d1b9e91db79d3292fd318c73aaba4b3d5caf0a1119e5a698b24f68a19e1de673` | Infinite-Slope Geotechnical Model Bundle |
| `pahad_event_model.pkl` | 57,100 | `d2094eae9ee6906f5197af5b2fdeb671d6a571080c7f63985b92b95c82ede938` | Primary Landslide Event Classifier |
| `pahad_event_calibrator.pkl` | 56,091 | `f3a72b9eb9340990a4b4585799f438d27158d09002b948728f5eae41dbc1b1f8` | Platt Sigmoid Probability Calibrator |
| `pahad_event_model_6h.pkl` | 61,657 | `e864b26edb1e708aac4ec5c2d95d8c3088ba6310a3b9e79586a093c70e06270e` | 6-Hour Horizon Event Model |
| `pahad_event_model_12h.pkl` | 88,702 | `04c2eb5469c4b8a14d0e99cb71380430c695f858cb7e349e78658f335ab24698` | 12-Hour Horizon Event Model |
| `pahad_event_model_24h.pkl` | 84,094 | `84cd808a6196cdd5f330756a6b4007234bd9ae7a73d9505cd428ac7589545831` | 24-Hour Horizon Event Model |
| `pahad_event_model_48h.pkl` | 62,245 | `61e1f8aff5f3f954560bbeb88cd8ae94e27134ec2e9cfc18a5004bf419f86093` | 48-Hour Horizon Event Model |
| `pahad_event_metadata.json` | 2,152 | `9f408b7acb5c77f1a124fcad5e1898cdc42549f855ac4c45e44d89aebc62e77f` | Model Registry Metadata (vtest-v1.0) |
| `pahad_event_metrics.json` | 657 | `8bc174735d5362dd1662b84b918b261a4da720c0be5a27847f5e161fe034d44d` | Model Evaluation Metrics Record |

---

### 4. Ground-Truth Dataset Integrity (SHA-256)

| Dataset File | Rows | Size (Bytes) | SHA-256 Digest | Classification |
| :--- | :--- | :--- | :--- | :--- |
| `data/features/real_train.csv` | 16 | 4,172 | `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e` | Real Curated Training Partition |
| `data/features/real_val.csv` | 12 | 3,290 | `ed732e2054f1b028cab9380a35ad31affbbb5e93a3cb207fda1582665aa0bd81` | Real Curated Validation Partition |
| `data/features/real_test.csv` | 8 | 2,468 | `29f84cf974241844a16086736e1cab833484a9587519946dd24ee09ae09d28da` | Real Curated Test Partition |
| `data/labels/event_labels.csv` | 36 | 4,442 | `edcdb95b13a87208deb3aa20cf29f381bad8c9312c8879131bce38ad00455a4c` | Master Ground-Truth Labels (17 Ev / 19 Ctrl) |
| `data/features/features_all.csv` | 36 | 8,816 | `28688c13aba6b03b83d55a41f3f4028f910c16069eea12396a4695d579a56c2a` | All Curated Multimodal Features |
| `data/features/demo_train.csv` | 25 | 6,942 | `a5453fa55bc6cc330d92236f5c82444444f1034c3969de4eff0b3b5deb6c9cad` | Isolated Demo Dataset (`PAHAD_DEMO_MODE=1`) |

---

### 5. Production Safety Invariants & Policy Flags

All production actuation and public dispatch channels are verified **FAIL-CLOSED** for the demonstration:

| Safety Policy Flag | Enforced State | Fail-Closed Mechanism | Verification Status |
| :--- | :--- | :--- | :--- |
| `ENABLE_PUBLIC_DISPATCH` | `0` | Disables automated public alert broadcast | **LOCKED (DISABLED)** |
| `SIREN_DRY_RUN` | `1` | Forces relay driver to `DRY_RUN_EMULATOR` | **ENFORCED (DRY_RUN)** |
| `CAP_PRODUCTION_DISPATCH` | `0` | OASIS CAP XML output gated to test/preview feed | **LOCKED (DISABLED)** |
| `SACHET_PRODUCTION_DISPATCH` | `0` | NDMA SACHET gateway public dispatch blocked | **LOCKED (DISABLED)** |
| `CELL_BROADCAST_PRODUCTION` | `0` | Telecom cell broadcast production dispatches blocked | **LOCKED (DISABLED)** |
| `VOICE_ASSISTANT_ACTUATION` | Interlocks Active | Voice commands matching 7 forbidden patterns blocked | **VERIFIED (BLOCKED)** |

---
**Document Status:** FREEZE ENFORCED (Phase 11K)  
**Evaluation Standard:** Smart India Hackathon (SIH) 2026 — Disaster Management Theme
