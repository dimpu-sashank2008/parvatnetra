# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Real Telemetry Acquisition, Physical Deployment Boundary & Kinematic Model Status Report

**Document Version**: 1.0.0  
**Phase**: V4.7 Engineering Commissioning  
**System Status**: BENCH_READY_FIELD_EVIDENCE_PENDING  
**Operational Verdict**: `V4_7_BENCH_READY_FIELD_EVIDENCE_PENDING`  
**Target Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 Rangpo–Singtam Geological Corridor)  

---

## 1. Ground Truth & Deployment Boundary

A central tenet of PARVAT NETRA is the uncompromising distinction between **laboratory bench readiness** and **physical mountain deployment**:

$$\textbf{BENCH\_VALIDATED} \ne \textbf{FIELD\_COMMISSIONED}$$

1. **Hardware State**: Five physical geotechnical instrument nodes have been acquired, serialized, calibrated by NABL accredited laboratories, and tested via hardware-in-the-loop (HIL) LoRa bench verification at the Sikkim State EOC Integration Facility.
2. **Field State**: Mountain slope borehole drilling, casing grouting, downhole anchoring, and solar mast erection along the NH-10 KM48 corridor remain scheduled with Border Roads Organisation (BRO Project Swastik) and Sikkim State Disaster Management Authority (SSDMA).
3. **Verdict**: The current operational state of real-time telemetry acquisition is strictly:
   $$\textbf{PHYSICAL\_TELEMETRY\_PENDING}$$

---

## 2. In-Situ Instrumentation Status Table (`CORR-NH10-SIKKIM-KM48`)

| Sensor ID | Sensor Type | Hardware Serial | Calibration Cert | Bench Test | Downhole Installation | Field Telemetry Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PIEZO-NH10-KM48-01` | Vibrating Wire Piezometer | `GK-4500AL-9988` | `NABL-GEO-2026-P8821` | PASS (72h HIL) | Scheduled (12m borehole) | `BENCH_ACCEPTED (Field Pending)` |
| `INCL-NH10-KM48-01` | In-Place Inclinometer | `RST-MEMS-5521` | `NABL-GEO-2026-I4409` | PASS (72h HIL) | Scheduled (Shear plane) | `BENCH_ACCEPTED (Field Pending)` |
| `TILT-NH10-KM48-01` | Surface Tiltmeter | `ENC-92M-3312` | `NABL-GEO-2026-T1134` | PASS (72h HIL) | Scheduled (Crown bedrock) | `BENCH_ACCEPTED (Field Pending)` |
| `RAIN-NH10-KM48-01` | Tipping Bucket Rain Gauge | `DAV-AERO-7740` | `IMD-MET-2026-R0921` | PASS (72h HIL) | Scheduled (Corridor mast) | `BENCH_ACCEPTED (Field Pending)` |
| `GW-NH10-KM48-01` | LoRa Edge Gateway | `RAK-7289-4411` | Factory Tested | PASS (72h HIL) | Scheduled (Ridge solar mast)| `BENCH_ACCEPTED (Field Pending)` |

---

## 3. Dual-Stream Inference Architecture Boundary

The platform's dual-stream inference pipeline maintains strict physical separation:

```
[STREAM A: Synoptic Multi-Horizon Forecasting (24h - 168h)]
Status: AVAILABLE
Input Data: 25 real channels (IMD AWS, ERA5 reanalysis, Mohr-Coulomb FoS)
Target: Regional antecedent saturation & regional landslide probability
Model: Production V3 (models/pahad_lstm_v3_weights.pt) [ACTIVE & LOCKED]

[STREAM B: High-Frequency Kinematic Nowcasting (0h - 6h)]
Status: UNAVAILABLE (Reason: PHYSICAL_TELEMETRY_PENDING)
Input Data: In-situ piezometer pore pressure & inclinometer tilt rate
Target: Imminent slope collapse nowcasting
Model: Kinematic Classifier [STATUS: NOT_TRAINED_DATA_PENDING]
```

Under zero circumstances are Stream A and Stream B blended into an opaque single score that obscures the absence of physical field telemetry. The API explicitly returns:
```json
{
  "stream_a_synoptic": {
    "status": "AVAILABLE",
    "probability_24h": 0.42,
    "model_version": "v3"
  },
  "stream_b_kinematic": {
    "status": "UNAVAILABLE",
    "reason": "PHYSICAL_TELEMETRY_PENDING",
    "model_status": "NOT_TRAINED_DATA_PENDING"
  }
}
```

---

## 4. Machine Learning Model Training Boundary

In compliance with the Core Constitution and Phase V4.7 mandates:
1. **No ML Model Trained on Synthetic Kinematic Data**: The kinematic model remains officially classified as `NOT_TRAINED_DATA_PENDING`.
2. **Production V3 Immutability**: Production weights (`models/pahad_lstm_v3_weights.pt`) remain bit-for-bit unchanged (SHA-256: `7cb823888646ca2b...`).
3. **Research V4.5 Immutability**: Research weights (`models/pahad_lstm_v4_5_research_weights.pt`) remain bit-for-bit unchanged (SHA-256: `31e16ce003cdd2c5...`).
4. **Data Sufficiency Threshold**: Training of Stream B kinematic models will only commence after acquiring a minimum of 90 days of continuous, field-validated in-situ telemetry under monsoon conditions with verified slope stability baselines.

---

## 5. Real Telemetry Baseline Statistics Protocol

Once field telemetry acquisition initiates post-installation, `FieldEvidenceManager.compute_baseline_statistics()` will process the raw time series:
- Compute parametric metrics: Mean, standard deviation, minimum, maximum.
- Compute non-parametric quantiles: 5th, 25th, 50th (median), 75th, 95th percentiles.
- Calculate signal noise floors and baseline diurnal thermal cycles.
- **Strict Limitation**: Baseline descriptive statistics will NOT be extrapolated into unverified failure probabilities or premature stability certifications until corroborated by seasonal hydrological cycles.
