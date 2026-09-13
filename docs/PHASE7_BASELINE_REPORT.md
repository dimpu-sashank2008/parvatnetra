# PARVAT NETRA • PAHAD AI — PHASE 7 BASELINE REPORT
**Checkpoint 0: Initial Technical Baseline & Verification State**

---

## 1. Repository & Architecture State
- **Project Root**: `c:\Users\dimpu\Downloads\PARVAT_NETRA_PAHAD_AI_FIRST\silly-fermi`
- **Platform**: PARVAT NETRA — NER Sentinel (Smart India Hackathon SIH Grade Platform)
- **AI Core**: PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)
- **Primary Pilot Corridor**: `CORR-NH10-SIKKIM-KM48` (Pakyong District, Sikkim / Project Swastik BRO)
- **Version Control**: Standalone local workspace.
- **Python Environment**: Python 3.11.0, pytest-9.1.1, scikit-learn, Flask 3.0, SQLite3.

---

## 2. Existing Phase Completion State
- **Phase 1 – Phase 4**: Core platform, 3D GIS visualization, geotechnical physics engine (Infinite Slope FoS), and CAP v1.2 alerting. (**COMPLETE**)
- **Phase 5 (5A – 5E)**:
  - 5A: Core live inference & baseline architecture (**COMPLETE**)
  - 5B: Multi-horizon temporal models (6h, 12h, 24h, 48h) (**COMPLETE**)
  - 5C: Real data connectors & observation store (**COMPLETE**)
  - 5D: Offline synchronization & data reality gate (**COMPLETE**)
  - 5E: Flutter mobile field client & offline SQLite (**COMPLETE**)
- **Phase 6 (6A – 6F)**:
  - 6A: Field infrastructure & corridor registry (**COMPLETE**)
  - 6B: Institutional data gateway & protocol adapters (**COMPLETE**)
  - 6C: Hardware specifications & telemetry schemas (**COMPLETE**)
  - 6D: Field validation & HIL testbenches (**COMPLETE**)
  - 6E: Supervised operational loop & authority review (**COMPLETE**)
  - 6E.1: Data consistency & reconciliation audit (**COMPLETE**)
  - 6F: Controlled pilot readiness audit & SOP (**COMPLETE**)

---

## 3. Reconciled Models & Datasets Baseline
- **Model A (Geotechnical Physics)**:
  - File: `models/pahad_fos_model.pkl` (295,094 bytes)
  - Target: Infinite-Slope Factor of Safety ($FoS$).
  - Status: `EXISTING / VERIFIED`.
- **Model B (Landslide Event Classifier)**:
  - File: `models/pahad_event_model.pkl` (57,293 bytes)
  - Calibrator: `models/pahad_event_calibrator.pkl` (56,284 bytes)
  - Target: Probability of landslide failure within forecast horizon.
  - Status: `TRAINED_LIMITED_DATA` (Research Prototype).
- **Multi-Horizon Horizon Models**:
  - `pahad_event_model_6h.pkl` (61,657 bytes)
  - `pahad_event_model_12h.pkl` (88,702 bytes)
  - `pahad_event_model_24h.pkl` (84,094 bytes)
  - `pahad_event_model_48h.pkl` (62,245 bytes)
- **Reconciled Event Quantities**:
  - Canonical Historical Landslide Events: **17** documented disasters across 8 NER states.
  - Baseline Model Observations: **36** (17 positive event records, 19 negative controls).
  - Antecedent Temporal Windows: **105** ($17 \times 5 = 85$ positive windows + 20 controls).
  - Held-out Test Split: **8** records (5 positive, 3 negative controls).
- **Dataset Cryptographic SHA-256 Hash**:
  - `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`

---

## 4. Current Operational Modes & Safety Interlocks
- **Operational Mode**: `SHADOW_MODE` (Live inference running in background observation mode).
- **Siren Hardware Subsystem**: `SIREN_DRY_RUN = 1` (Acoustic siren relay hardware locked in dry-run mode).
- **Public Alert Dispatch**: `ENABLE_PUBLIC_DISPATCH = 0` (Public CAP dissemination strictly disabled).
- **Corroboration Invariant**: 2-of-3 independent evidence confirmation rule active across physical mechanics, hydrologic threshold, and empirical ML.
- **Human Authority Sign-off**: Mandatory two-stage authority review required before warning authorization.

---

## 5. Connector Qualification Baseline (8 Connectors)
1. **Open-Meteo**: `CONNECTED` (`[LIVE_FALLBACK]`, zero-auth public weather API).
2. **USGS Earthquake Hazards API**: `CONNECTED` (`[LIVE_FALLBACK]`, zero-auth public FDSNws seismic API).
3. **IMD AWS/Nowcast**: `AUTH_REQUIRED` (`[HISTORICAL/SIMULATED]`, credentials pending MOU).
4. **NCS Seismology**: `AUTH_REQUIRED` (`[LIVE_FALLBACK]`, USGS acts as active zero-auth fallback).
5. **Copernicus CDSE / Sentinel-1 InSAR**: `AUTH_REQUIRED` (`[HISTORICAL]`, cached LOS velocity catalog active).
6. **ISRO Bhoonidhi**: `REGISTRATION_REQUIRED` (`[HISTORICAL]`, static Cartosat/GLO-30 DEM catalog active).
7. **Neon PostgreSQL / PostGIS**: `CONFIGURED` (`[DATABASE_BACKED]`, `DATABASE_URL` active).
8. **Edge IoT Device Gateway**: `STANDBY_READY_FOR_DEVICES` (`[SIMULATED_OR_STAGING]`, broker ready).

---

## 6. Known Controlled Pilot Blockers
1. **Physical Instrumentation**: Borehole drilling, casing anchoring, and on-slope transducer installation (piezometers, inclinometers, tiltmeters) pending at corridor `CORR-NH10-SIKKIM-KM48`.
2. **Institutional Credentials**: Direct authenticated access to MoES / IMD AWS feeds requires execution of formal inter-agency Data Sharing MOU.
3. **Historical Event Volume**: Empirical event model trained on $N=17$ canonical events requires governed expansion to $N \ge 150$ via GSI NLSM archives for unconstrained production generalization.

---

## 7. Checkpoint 0 Determination
- Baseline state is fully documented, reproducible, and verified against on-disk artifacts.
- **GATE RESULT**: **`CHECKPOINT_0 = PASS`**
