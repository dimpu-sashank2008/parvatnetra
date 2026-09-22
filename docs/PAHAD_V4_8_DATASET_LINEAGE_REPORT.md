# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Feature Lineage, Traceability & Kinematic ML Training Gate Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Modules**: `engine/telemetry_evidence_audit_engine.py`, `services/kinematic_telemetry_service.py`  
**Test Suite**: `tests/test_v4_8_dataset_lineage.py`  

---

## 1. Derived Feature Lineage Architecture

PARVAT NETRA enforces strict genealogical traceability for all derived geotechnical indicators:

$$\text{Raw Observations } \{o_1, o_2, \dots, o_k\} \xrightarrow[\text{Lineage Logged}]{\text{Deterministic Filter}} \text{Derived Feature } f_j$$

Every feature record in the feature store explicitly logs:
- `feature_id`: Unique identifier (e.g. `FEAT-PIEZO-VEL-1H-KM48`)
- `source_observation_ids`: Array of exact raw packet/observation UUIDs used in the calculation
- `window_start_utc` & `window_end_utc`: Exact temporal window bounds
- `derivation_method`: Mathematical algorithm (e.g., Savitzky-Golay derivative, central difference)
- `software_version`: Codebase version producing the derivation

Orphaned features lacking source observation links are purged from supervised datasets.

---

## 2. Prevention of Target/Feature Circularity

To ensure that machine learning evaluations remain scientifically valid, circular predictive dependencies are prohibited:
- **No Self-Prediction**: Downstream hazard indices (such as the Composite Risk Index - CRI or Alert Severity Level) cannot enter feature vectors.
- **Physical Exogeneity**: Feature vectors comprise solely physical measurements (rainfall, pore pressure, inclinometer displacement, tilt, ground temperature, seismic PGA).

---

## 3. The Future Kinematic ML Training Gate

In strict adherence to Phase V4.8 invariants, **no kinematic ML model is trained during this phase**. The system status is definitively:

$$\mathbf{KINEMATIC\_ML\_STATUS = NOT\_TRAINED\_DATA\_PENDING}$$

### Mandatory Gate Prerequisites for Future Training:
1. `REAL_FIELD_DATA == TRUE` (Verified live field telemetry from deployed transducers)
2. `MULTIPLE_SITES == TRUE` (Telemetry from at least 3 distinct geological corridors)
3. `VERIFIED_EVENTS >= 15` & `VERIFIED_CONTROLS >= 20`
4. `TEMPORAL_LEAKAGE == ZERO` & `EVENT_LEAKAGE == ZERO`
5. `SENSOR_QC == PASS` (Less than 2% packet corruption or missingness)
6. `72H_BURN_IN == COMPLETED`

If any prerequisite is unmet, kinematic ML training remains firmly **BLOCKED**.
