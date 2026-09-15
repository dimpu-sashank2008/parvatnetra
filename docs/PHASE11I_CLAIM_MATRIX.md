# PARVAT NETRA / PAHAD AI — PHASE 11I SCIENTIFIC & OPERATIONAL CLAIM MATRIX
**Standard: Smart India Hackathon (SIH) 2026 Final Defensibility Hardening**  
**Audit Standard: Zero-Tolerance Technical Claim Verification & Remediation**  
**Baseline Audit: Phase 11H Forensic Audit (`INTEGRITY_PASS_WITH_LIMITATIONS`)**

---

## 1. Overview & Classification Schema

Every technical, scientific, operational, and architectural claim made across the PARVAT NETRA codebase, API documentation, public templates, and evaluation artifacts is categorized into one of four audit states:

1. **`SUPPORTED`**: Supported by verifiable, reproducible source code, physical models, mathematical limit-equilibrium derivations, or documented data sources.
2. **`PARTIALLY_SUPPORTED`**: Core scientific/architectural mechanism is implemented, but operational scope is bounded by documented constraints (e.g. limited training sample size, staged telecommunications gateway).
3. **`UNSUPPORTED`**: Claim cannot be mathematically or operationally verified from existing codebase and data; must be bounded or removed from judge-facing presentations.
4. **`FORBIDDEN / MISLEADING`**: Overstated capability, simulated hardware represented as live deployed field hardware, or claim of official government statutory authority. Strictly prohibited by the PARVAT NETRA constitution.

---

## 2. Authoritative Claim Matrix

| Claim ID | Claim Statement | Evidence in Codebase | Audit Status | Authoritative Wording & Remediation Guidance |
|---|---|---|:---:|---|
| **CLM-01** | Geotechnical Infinite Slope Factor of Safety ($FoS$) based on Mohr-Coulomb mechanics | `engine/pahad_models.py:175`, `calculate_infinite_slope_fs()` | **`SUPPORTED`** | **Deterministic Physical Model**: Exact closed-form infinite slope limit-equilibrium calculation based on planar Mohr-Coulomb shear strength criteria. Evaluated deterministically for all 26 canonical corridors. |
| **CLM-02** | Empirical Rainfall Threshold Model (Caine 1980 / Regional I-D thresholds) | `engine/pahad_models.py:270`, `is_empirical_threshold_exceeded()` | **`SUPPORTED`** | **Empirical Rainfall Threshold**: Computes power-law intensity-duration exceedance ($I = \alpha \cdot D^{-\beta}$) against regional Himalayan baseline thresholds. Corroborates physical saturation. |
| **CLM-03** | Machine Learning Landslide Event Classifier (GBDT with Platt probability calibration) | `engine/model_registry.py`, `models/pahad_event_model.pkl`, `data/features/real_train.csv` | **`PARTIALLY_SUPPORTED`**<br>*(Trained on Limited Data)* | **Research Prototype Classifier (`TRAINED_LIMITED_DATA`)**: Gradient Boosting classifier trained on 16 documented GSI events/controls ($\le 2023$), calibrated with Platt scaling. Test performance on held-out partition ($N=8$, H2 2024) reflects small sample size; not claimed as deployment-ready. |
| **CLM-04** | Deep Learning LSTM Temporal Sequence Model for rolling horizon prediction | `engine/pahad_lstm.py:9` | **`SUPPORTED AS SURROGATE`**<br>*(NOT TRAINED)* | **Mathematical Physics Surrogate**: `engine/pahad_lstm.py` is explicitly annotated: `Model Status: NOT_TRAINED (MATHEMATICAL SURROGATE)`. No fabricated LSTM weights or false neural claims are presented. Preserved as a mathematical surrogate until multi-year sequence archives exist. |
| **CLM-05** | Multimodal Composite Risk Index (CRI = $H \times V \times 100$) | `engine/pahad_fusion.py:235`, `backend/risk_engine.py` | **`SUPPORTED`** | **Multimodal CRI Formulation**: Hazard $H = 0.40 \cdot S + 0.35 \cdot P + 0.25 \cdot A$, Composite Risk $\text{CRI} = H \cdot V \cdot 100$. Dynamic rainfall dynamically modulates $P$ and triggers physical ground anomaly $A \ge 0.90$ when $FoS \le 1.0$. |
| **CLM-06** | 2-of-3 Triangulation Signal Confirmation Rule | `engine/pahad_alert_policy.py:261`, `engine/pahad_fusion.py:251`, `engine/pahad_models.py:369` | **`SUPPORTED`**<br>*(Multi-Signal Corroboration)* | **Multi-Signal Corroboration**: Mandatory safety interlock prevents single-signal false alarms from issuing Red alerts. Evaluates FoS ($\le 1.0$), empirical rainfall threshold, and ML probability ($> 0.80$). Clarified that signals are physically covariant (rainfall impacts FoS); terminology standardized to "multi-signal corroboration" rather than statistical independence. |
| **CLM-07** | Satellite InSAR Ground Deformation & Terrain Morphometry | `services/terrain_service.py`, `data/cache/terrain/` | **`SUPPORTED`**<br>*(Catalog & Baseline Integration)* | **Satellite Catalog & LOS Velocity Integration**: Incorporates Copernicus GLO-30 DEM slope/aspect and Sentinel-1 InSAR mean line-of-sight (LOS) deformation velocity as antecedent geomechanical priors. Orbit processing pipeline is off-board. |
| **CLM-08** | In-Situ IoT Borehole Sensor Telemetry (Piezometers, Inclinometers, Tiltmeters) | `services/iot_sensor_service.py`, `engine/sensor_simulator.py` | **`SUPPORTED`**<br>*(Simulated Telemetry Pipeline)* | **Bench-Validated Simulated Telemetry Pipeline**: Hardware architecture, LoRaWAN payload parsers, and edge gateway protocols are bench-tested. In-situ field deployment along active mountain corridors is pending capital works. Provenance tagged `[SIMULATED]`. |
| **CLM-09** | Autonomous Highest-Risk Corridor Prioritization | `/api/pahad/highest-risk-corridor`, `app.py:5655` | **`SUPPORTED`** | **Dynamic Multi-Corridor Hazard Triage**: Evaluates all 26 canonical corridors across the 8 NER states dynamically via live Open-Meteo telemetry. Ranks deterministically by CRI descending, FoS ascending, and alphabetical ID. Current highest-risk corridor: `SK-NH10-KM48` ($\text{CRI} = 45.50$, `HIGH`, $FoS = 0.9710$). |
| **CLM-10** | Warning Lead Time (Forecasting Horizon Capability) | `templates/index.html:4615`, `services/pahad_voice_assistant.py:485` | **`SUPPORTED`**<br>*(Multi-Horizon Horizons)* | **Multi-Horizon Exceedance Forecasting**: Evaluates multiple discrete predictive horizons ($6\text{h}$, $12\text{h}$, $24\text{h}$, $48\text{h}$). Numeric claims asserting fixed operational lead times (e.g., "36 hours ahead with 100% certainty") are remediated to transparent horizon evaluations. |
| **CLM-11** | OASIS CAP v1.2 & Civil Protection Mass Alerting | `backend/cap_handler.py`, `services/unified_notification_service.py` | **`SUPPORTED`**<br>*(Sandbox / Staging Gated)* | **OASIS CAP v1.2 Compliant Alert Feeds**: Synthesizes valid XML with WGS-84 polygonal geofences and CAP severity tiers. Mass civilian broadcast is strictly fail-closed (`ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`, `CAP_PRODUCTION_DISPATCH=0`). Statutory District Magistrate sign-off remains mandatory. |
| **CLM-12** | National Government Identity & Regulatory Authority | `templates/index.html:2673` | **`SUPPORTED`**<br>*(Disclaimer Banner Active)* | **SIH 2026 Academic Research Prototype**: Persistent prototype disclaimer banner displayed beneath the tricolor bar: *"PARVAT NETRA is an SIH 2026 AI-assisted research and decision-support prototype. Not an official Government of India emergency broadcast service."* |

---

## 3. Summary of Remediations Applied

1. **Warning Lead Time Terminology Reconciled**:
   - Replaced fixed performance claims (`"Estimated Early Warning Lead Time: 24.0 hours"`) in `services/pahad_voice_assistant.py` and `templates/index.html` with accurate multi-horizon terminology: *"Prototype evaluates multiple forecast horizons (6h / 12h / 24h / 48h outlooks)"*.
2. **2-of-3 Triangulation Independence Clarified**:
   - Clarified that geotechnical FoS, empirical rainfall, and ML classifier probabilities share underlying hydrometeorological covariance. Standardized terminology to *"multi-signal corroboration across physical, rainfall, and ML indicators"*.
3. **Research Prototype Disclaimer Enforced**:
   - Injected prominent top banner in `templates/index.html:2673` clarifying SIH 2026 academic research status, preventing any misrepresentation as an official NDMA/GSI statutory alerting authority.
4. **Rainfall Feature Lookup Rectified**:
   - Fixed feature key extraction in `app.py:5699` from `rain_24h` to `rainfall_24h`, restoring live Open-Meteo precipitation values in `/api/pahad/highest-risk-corridor` JSON payloads.
