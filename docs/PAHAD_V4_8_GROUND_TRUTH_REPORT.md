# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Ground-Truth Event Pipeline, Temporal Windows & Leakage Prevention Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Modules**: `services/field_evidence_manager.py`, `services/pahad_event_dataset.py`  
**Test Suite**: `tests/test_v4_8_ground_truth.py`  

---

## 1. Ground-Truth Data Architecture

A machine learning classifier or physical risk threshold is only as valid as its ground truth. PARVAT NETRA establishes an independent, authoritative ground-truth catalog containing:
- **17 Canonical Historical Landslide Events** (GSI / NDMA / BRO Swastik validated)
- **20 Verified Negative Controls** (IMD verified continuous dry periods with open highway logs)

### Strict Independence Invariant:
$$\text{Ground Truth} \ne f(\text{PAHAD AI Prediction}, \text{CRI Score}, \text{FoS Model})$$
A model output or high sensor reading can **never** serve as its own ground-truth label. Labels must originate exclusively from verified physical incident records, geological surveys, or emergency response logs.

---

## 2. Event Label Schema

```json
{
  "event_id": "EVT-2023-TEESTA-SURGE",
  "corridor_id": "CORR-NH10-SIKKIM-KM48",
  "site_id": "KM48-SLOPE-B1",
  "event_timestamp": "2023-10-04T06:00:00Z",
  "event_type": "DEBRIS_FLOW_GLOF_SURGE",
  "severity": "CRITICAL",
  "ground_truth_source": "GSI_OFFICIAL_DISASTER_BULLETIN",
  "ground_truth_reference": "GSI-NER-2023-TEESTA-04",
  "verification_status": "VERIFIED",
  "confidence": 1.0,
  "evidence_ids": ["EVID-GSI-SURVEY-2023", "EVID-BRO-CLOSURE-LOG-04"]
}
```

---

## 3. Temporal Window Generation & Zero-Leakage Guarantee

For every verified event with time $T_{\text{event}}$, observation feature windows are generated strictly backwards in time:
- **$168\text{h}$**: Antecedent synoptic saturation baseline
- **$72\text{h}$**: Intermediate storm buildup
- **$48\text{h}$**: Severe precipitation onset
- **$24\text{h}$**: Acute geotechnical pore-pressure response
- **$12\text{h}$**: Sub-daily acceleration window
- **$6\text{h}$**: Immediate nowcasting horizon

### The Zero-Leakage Invariant:
$$\forall t \in \text{FeatureWindow}, \quad t < T_{\text{event}}$$
Any feature containing post-event rainfall, post-event displacement, or future labels immediately fails the automated leakage auditor (`check_event_leakage.py`) and halts training.

---

## 4. Negative Control Selection Protocol

To avoid biased, easy negatives:
1. Negative controls are selected exclusively from high-risk mountain sectors during verified dry winter windows (December–February).
2. The monitoring period must have verified continuous telemetry and confirmed zero road closures by BRO Swastik.
3. Missing or dropped telemetry is classified as `UNKNOWN` and **strictly excluded** from negative training sets.
