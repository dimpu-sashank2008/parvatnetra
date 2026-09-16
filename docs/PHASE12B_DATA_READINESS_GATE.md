# PARVAT NETRA • PAHAD AI — Phase 12B Data Readiness Gate Specification

**Standard**: SIH 26001 / Project Constitution Section 12 & 32  
**System**: PARVAT NETRA — Northeast Region Sentinel  
**Subsystem**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Document Version**: 12.0.0-phase12b  
**Status**: ACTIVE SYSTEM ENFORCEMENT SPECIFICATION  

---

## 1. Purpose & Authority

The **PAHAD Data Readiness Gate** (`engine/pahad_temporal_gate.py`) is an autonomous architectural safety mechanism. Its sole responsibility is to evaluate available temporal datasets against rigorous geotechnical and statistical criteria, strictly prohibiting deep sequence model training (LSTM / GRU / TCN) until statistically defensible thresholds are achieved.

---

## 2. Gate Status Taxonomy

| Status Code | Description | Operational Action |
| :--- | :--- | :--- |
| `KEEP_SURROGATE` | Insufficient continuous telemetry to satisfy statistical learning criteria. | Maintain existing Physics-Informed Geotechnical Surrogate (`engine/pahad_lstm.py`). |
| `DATA_COLLECTION_REQUIRED` | Formal gate evaluation confirming candidate sequences fall below project minimums. | Training is strictly blocked. Physical sensor deployment and data collection required. |
| `TRAINING_ELIGIBLE` | All volume, cadence, duration, and completeness targets met. | Research LSTM training authorized within isolated sandbox. |
| `VALIDATION_REQUIRED` | Research model trained; awaiting multi-basin spatiotemporal validation. | Model quarantined; operational dispatch blocked. |
| `PRODUCTION_ELIGIBLE` | Multi-monsoon validation passed with POD > 0.85 and FAR < 0.20. | Model certified for operational inference. |

---

## 3. Explicit Project Target Specification (Himalayan Corridor Standard)

| Target Criterion | Target Value | Unit | Scientific & Geotechnical Rationale |
| :--- | :---: | :--- | :--- |
| `event_sequence_volume` | **500** | Independent failure sequences | A 2-layer BiLSTM network with 26 features has ~25,000 trainable weights. Parameter optimization requires at least 500 distinct events across the 8 NER states to avoid extreme memorization. |
| `control_sequence_volume` | **2,000** | Independent non-event sequences | Slopes are stable during 99%+ of rain hours. Training on balanced sets creates false-alarm rates > 80%. A 1:4 event-to-control ratio is the minimum for reliable early-warning discrimination. |
| `minimum_sequence_duration_hours` | **48.0** | Contiguous hours per sequence | Regolith saturation and basal pore-water pressure respond to antecedent rainfall on a 24h to 72h lag. Sequences < 48h truncate the hydrological accumulation curve. |
| `cadence_in_situ_minutes` | **15.0** | Minutes between sensor packets | Tertiary shear acceleration and pore-pressure dissipation leading to catastrophic failure occur within 15–30 minutes. 24h snapshots fail to capture precursor velocity spikes. |
| `cadence_rainfall_hours` | **1.0** | Hour per rainfall accumulation | Convective cloudburst pulses trigger shallow debris flows within 1 to 3 hours. Hourly accumulation is required to resolve intensity thresholds. |
| `seasonal_coverage_monsoons` | **2** | Complete monsoon cycles (24 months) | Captures inter-annual Southwest monsoon variability (ENSO modulation) and prevents catastrophic distribution shift between wet and dry years. |
| `data_completeness_pct` | **95.0%** | Percentage observed without imputation | Synthetic imputation of missing sensor packets in temporal sequences distorts higher-order derivatives (acceleration, tilt rates). |
| `timestamp_confidence_seconds` | **15.0** | Seconds maximum uncertainty | Required to synchronize high-frequency seismic rumble with piezometric and displacement spikes during co-seismic or rain-induced mass wasting. |

---

## 4. Current Repository State Evaluation

The automated gate evaluation (`PahadTemporalGate.evaluate_current_repository()`) produces the following verified audit:

```
======================================================================
PAHAD AI TEMPORAL GATE: READINESS AUDIT
======================================================================
Gate Status              : DATA_COLLECTION_REQUIRED
Training Authorized      : FALSE
Active Operational Model : PAHAD LSTM (Physics-Informed Surrogate v2)
Operational Model Status : NOT_TRAINED
Recommended Action       : KEEP_SURROGATE_CONTINUE_TELEMETRY_DEPLOYMENT
----------------------------------------------------------------------
Prerequisite Check                  Actual       Target       Result
----------------------------------------------------------------------
event_sequences                     0            500          FAIL
control_sequences                   0            2000         FAIL
min_duration_hours                  0.0          48.0         FAIL
cadence_minutes                     720.0        15.0         FAIL
seasonal_monsoons                   0            2            FAIL
completeness_pct                    0.0          95.0         FAIL
real_telemetry                      ABSENT       PRESENT      FAIL
----------------------------------------------------------------------
```

---

## 5. Execution Hard Guard Behavior

When `enforce_training_guard()` is invoked (e.g. by `scripts/train_temporal_lstm.py`):
1. It verifies all 7 prerequisite checks.
2. If any check fails and `PAHAD_DEMO_MODE != 1`, it immediately raises `TemporalReadinessError`.
3. The process terminates with exit code `1`, refusing to write or modify model checkpoint files.
4. Under `--audit-only`, the script prints the audit matrix and exits with code `0`.

---

## 6. Live API Contract

The readiness gate is exposed via the REST endpoint:

`GET /api/pahad/temporal/readiness`  
(Alias: `GET /api/pahad/training-readiness`)

### Sample Response:
```json
{
  "gate_status": "DATA_COLLECTION_REQUIRED",
  "training_authorized": false,
  "recommended_action": "KEEP_SURROGATE_CONTINUE_TELEMETRY_DEPLOYMENT",
  "active_temporal_model": "PAHAD LSTM (Physics-Informed Surrogate v2)",
  "model_status": "NOT_TRAINED",
  "actual_vs_target": {
    "event_sequences": {"actual": 0, "target": 500, "status": "FAIL"},
    "control_sequences": {"actual": 0, "target": 2000, "status": "FAIL"},
    "min_duration_hours": {"actual": 0.0, "target": 48.0, "status": "FAIL"},
    "cadence_minutes": {"actual": 720.0, "target": 15.0, "status": "FAIL"},
    "seasonal_monsoons": {"actual": 0, "target": 2, "status": "FAIL"},
    "completeness_pct": {"actual": 0.0, "target": 95.0, "status": "FAIL"},
    "real_telemetry": {"actual": "ABSENT (Modelled Historical)", "target": "PRESENT", "status": "FAIL"}
  }
}
```
