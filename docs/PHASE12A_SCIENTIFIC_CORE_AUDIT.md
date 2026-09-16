# PARVAT NETRA / PAHAD AI — PHASE 12A SCIENTIFIC CORE AUDIT
**Authoritative Mathematical Formulation, Pipeline Dataflow & Architecture Trace**
*Smart India Hackathon (SIH 2026) Grade National Disaster-Intelligence Platform*

---

## 1. Executive Summary

This document establishes the single authoritative reference for the mathematical, physical, and statistical formulations implemented within the **PARVAT NETRA** operational risk intelligence engine (**PAHAD AI** — Predictive AI for Hillslope Analysis & Disaster-response).

Every equation, variable, and coefficient in this document has been verified against the production codebase:
- `engine/pahad_models.py`
- `engine/pahad_fusion.py`
- `engine/pahad_live_inference.py`
- `engine/canonical_registry.py`
- `services/weather_service.py`
- `app.py`

---

## 2. End-to-End Pipeline Dataflow Trace

```
Raw Telemetry Sources (IMD/Open-Meteo, USGS/NCS, Sentinel-1 InSAR, Piezometer/Inclinometer)
       │
       ▼
[engine/pahad_live_inference.py: run_live_inference()]
       │
       ├─► 1. Feature Ingestion & Imputation (Data Quality Scoring & Provenance Tagging)
       │       Observed -> [LIVE] / [CACHED]
       │       Missing  -> [MISSING] with documented training-split median imputation
       │
       ├─► 2. Geotechnical Limit Equilibrium Model [engine/pahad_models.py: calculate_infinite_slope_fs()]
       │       Input: c' (15 kPa), phi' (28°), beta (slope°), z (depth), u (pore pressure)
       │       Output: Factor of Safety (FoS_physical) & Status (STABLE / MARGINAL / CRITICAL / FAILED)
       │
       ├─► 3. Regional Rainfall Trigger Threshold Model [engine/pahad_models.py: is_empirical_threshold_exceeded()]
       │       Input: 24h precipitation, effective hourly rainfall intensity
       │       Output: Mandal-Sarkar & Monga-Ganguli Threshold Exceedance Flag
       │
       ├─► 4. Machine Learning Event Classifier [engine/pahad_event_predictor.py: PAHAD_EVENT_PREDICTOR]
       │       Input: 11-feature vector (slope, elevation, rain_24h, pore_pressure, FoS, etc.)
       │       Output: Calibrated Landslide Probability P(event | features) across 6h/12h/24h/48h
       │
       ├─► 5. Multimodal Evidence Fusion (CRI) [engine/pahad_fusion.py: PahadFusionEngine.fuse()]
       │       Static Susceptibility S = min(1.0, (slope/45°) * (1 - c'/40))
       │       Precipitation Loading P = min(1.0, (R_24h/100) + (I/12))
       │       Ground Anomaly A = min(1.0, 0.45*(u/35) + 0.30*(disp/5) + 0.15*(insar/20) + 0.10*(seismic/0.15))
       │       Base Hazard H = 0.40*S + 0.35*P + 0.25*A
       │       Raw CRI = H * V * 100
       │
       ├─► 6. 2-of-3 Multi-Signal Corroboration Heuristic
       │       Signal A: FoS <= 1.0 (Physical critical equilibrium)
       │       Signal B: Rainfall threshold breached or R_24h >= 100mm
       │       Signal C: Calibrated ML P(event) > 0.80
       │       Rule: If tentative band == EXTREME and signals < 2:
       │             Auto-downgrade to VERY_HIGH (final CRI capped at 79.9)
       │
       └─► 7. Machine-Readable Explainability & Provenance Contract
               Exposes: why_risk_changed, top_risk_factors, supporting_evidence,
               contradicting_evidence, data_quality_level, authority_action
               │
               ▼
[REST APIs: /api/pahad/predict-event, /api/pahad/highest-risk-corridor, /api/pahad/evaluate-sector]
               │
               ▼
[Command Console UI / EOC Dashboard / Sound & Alert Safety Interlocks]
```

---

## 3. Core Mathematical Formulations

### 3.1 Geotechnical Stability: Infinite-Slope Limit Equilibrium Model
$$FoS = \frac{c' + (\gamma_{\text{sat}} - m \gamma_w) z \cos^2\beta \tan\phi'}{\gamma_{\text{sat}} z \sin\beta \cos\beta}$$

- **Effective cohesion ($c'$):** $12.0\text{--}20.0\text{ kPa}$ (lithology specific)
- **Effective friction angle ($\phi'$):** $25.0^\circ\text{--}34.0^\circ$
- **Slope inclination ($\beta$):** Measured in radians from DEM gradient ($0.1^\circ \le \beta \le 89.9^\circ$)
- **Slip surface depth ($z$):** $3.0\text{--}4.0\text{ m}$
- **Water table saturation ratio ($m$):** $m = \min(1.0, \max(0.0, \frac{u}{\gamma_w z}))$, where $u$ is pore-water pressure in $\text{kPa}$
- **Unit weights:** $\gamma_{\text{sat}} = 18.5\text{--}19.5\text{ kN/m}^3$, $\gamma_w = 9.81\text{ kN/m}^3$

### 3.2 Regional Empirical Rainfall Trigger Thresholds
1. **Mandal & Sarkar (2013/2021) Sikkim Himalayan I-D Curve:**
   $$I_{\text{critical}} = 4.045 \cdot D^{-0.25} \quad [\text{mm/hr}]$$
   At $D = 24.0\text{ h}$: $I_{\text{critical}} = 1.828\text{ mm/hr}$ (cumulative $43.88\text{ mm}$).
2. **Monga & Ganguli (2018) Regional North-East I-D Curve:**
   $$I_{\text{critical}} = 5.8294 \cdot D^{-0.4141} \quad [\text{mm/hr}]$$
   At $D = 24.0\text{ h}$: $I_{\text{critical}} = 1.563\text{ mm/hr}$ (cumulative $37.52\text{ mm}$).

### 3.3 Composite Risk Index (CRI) Fusion
$$\text{Hazard } H = (\alpha \cdot S) + (\beta \cdot P) + (\gamma \cdot A)$$
$$\text{Composite Risk Index (CRI)} = H \cdot V \cdot 100$$

Where:
- $\alpha = 0.40$ (Static Susceptibility weight)
- $\beta = 0.35$ (Dynamic Precipitation loading weight)
- $\gamma = 0.25$ (Ground Anomaly / In-Situ Telemetry weight)
- $V \in [0.1, 1.0]$: Vulnerability Factor (derived from highway corridor criticality and surrounding population density)

---

## 4. Risk Band Categorization

| Tier | Range | Classification | Protocol Actions | Public Dispatch Gated? |
|---|---|---|---|---|
| **LOW** | $[0.0, 20.0)$ | Routine Monitoring | Standard background telemetry polling | Gated (No dispatch) |
| **MODERATE** | $[20.0, 40.0)$ | Elevated Observation | 5-minute sensor polling; notify beat engineers | Gated (No dispatch) |
| **HIGH** | $[40.0, 60.0)$ | Advisory Watch | Issue Watch to DDMA; pre-position road dozers | Gated (No dispatch) |
| **VERY_HIGH** | $[60.0, 80.0)$ | Severe Warning | Issue Warning to SDMA/NDRF; field patrol dispatch | Gated (No dispatch) |
| **EXTREME** | $[80.0, 100.0]$ | Emergency Evacuation | CAP-XML warning broadcast; evacuation advisory | **GATED** (Mandatory Human Sign-off) |

---

## 5. Discrepancy Analysis: Documentation vs Implementation

| Dimension | Documented Standard | Production Implementation | Audit Finding |
|---|---|---|---|
| **FoS Equation** | Classical Infinite-Slope Mohr-Coulomb | `engine/pahad_models.py: calculate_infinite_slope_fs` | **EXACT MATCH**. Monotonicity verified across all parameters. |
| **CRI Weights** | $\alpha=0.40, \beta=0.35, \gamma=0.25$ | `engine/pahad_fusion.py: lines 89-95` | **EXACT MATCH**. Verified $\alpha+\beta+\gamma = 1.00$. |
| **I-D Sikkim Curve** | $I = 4.045 \cdot D^{-0.25}$ | `backend/risk_engine.py`, `services/weather_service.py` | **EXACT MATCH**. Correctly calibrated for Sikkim-Darjeeling. |
| **Regional NER Curve** | $I = 5.8294 \cdot D^{-0.4141}$ | `engine/pahad_models.py: calculate_id_threshold` | **EXACT MATCH**. Derived from Monga & Ganguli (2018). |
| **Monga ED Formula** | $E = 1.3728 \cdot D_{\text{days}}^{1.1083}$ | `engine/pahad_models.py: calculate_ed_threshold` | **DISCREPANCY (P1)**. Produces only $1.37\text{ mm}$ threshold at $D=1\text{ day}$, causing accidental trigger if checked via `or`. Resolved by primary gating on $I_{\text{thresh}}$ and $R_{24h} \ge 100\text{ mm}$. |
| **Corroboration Rule** | 2-of-3 signal confirmation | `engine/pahad_fusion.py: lines 251-308` | **EXACT MATCH**. Suppresses unconfirmed EXTREME alerts to VERY_HIGH. |
