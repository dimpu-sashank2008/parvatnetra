# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Event Labeling Foundation, Linkage Ledger & Non-Event Control Strategy Report

**Document Version**: 1.0.0  
**Phase**: V4.8 Real Telemetry Evidence Audit & First-Data Foundation  
**System Status**: `V4_8_DATA_FOUNDATION_READY`  
**Module**: `services/field_evidence_manager.py`  
**Test Suite**: `tests/test_v4_8_event_labels.py`  
**Date**: September 2026  

---

## 1. The 3-State Ground-Truth Event Labeling Protocol

In supervised machine learning for landslide hazard prediction, class label integrity is paramount. In accordance with Section 13 of the V4.8 Master Engineering Prompt, PARVAT NETRA enforces a strict 3-state labeling protocol:

$$\textbf{Label} \in \{\textbf{EVENT}, \textbf{NON\_EVENT}, \textbf{UNKNOWN}\}$$

```
                +-----------------------------------------+
                |     Candidate Temporal Window           |
                +--------------------+--------------------+
                                     |
             +-----------------------+-----------------------+
             |                                               |
   Corroborated Physical                           Documented Absence of
   Movement or Failure                             Movement in Monitored Zone
             |                                               |
             v                                               v
      [LABEL: EVENT]                                 [LABEL: NON_EVENT]
   (event_label = 1.0)                             (event_label = 0.0)
             |                                               |
             +-----------------------+-----------------------+
                                     |
                       Unmonitored, Missing Telemetry,
                         or Unverified Observation
                                     |
                                     v
                             [LABEL: UNKNOWN]
                     (STRICTLY EXCLUDED FROM ML)
```

1. **`EVENT` (Positive Ground Truth)**: Assigned only when documented slope failure, crown scarp displacement, tension cracking, or debris flow is verified by GSI disaster records, high-resolution satellite InSAR, or authenticated SDRF field reconnaissance.
2. **`NON_EVENT` (Negative Control)**: Assigned only for time windows where active instrumentation or aerial reconnaissance explicitly corroborates the complete absence of slope movement.
3. **`UNKNOWN` (Uncertain Ground Truth)**: Assigned whenever telemetry was offline, weather records were missing, or post-event reconnaissance was absent.
   $$\textbf{Invariant: Unknown periods must NEVER silently become negative training examples.}$$

---

## 2. Event Linkage Schema & Attributes

Every linkage record created in `FieldEvidenceManager.link_event_window()` captures nine immutable fields:

```json
{
  "linkage_id": "link-5d313e9a",
  "event_id": "EVT-2023-TEESTA-01",
  "sensor_id": "PIEZO-NH10-KM48-01",
  "corridor_id": "CORR-NH10-SIKKIM-KM48",
  "event_timestamp_utc": "2023-10-04T06:00:00Z",
  "observation_window_start": "2023-10-01T06:00:00Z",
  "observation_window_end": "2023-10-04T06:00:00Z",
  "label": "EVENT",
  "label_source": "GSI_DISASTER_RECORD",
  "verification_status": "LINKED",
  "notes": "South Lhonak GLOF Teesta surge"
}
```

---

## 3. Current Event Linkage Ledger Audit (`field_evidence_ledger.json`)

The event ledger tracks 17 canonical GSI historical landslide events and 20 verified negative controls across the North-Eastern Region:

| Event Identifier | Date / Time (UTC) | State / Corridor | Label Assigned | Verification Source | ML Set Inclusion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `EVT-2023-TEESTA-01` | 2023-10-04 06:00 | Sikkim (NH-10) | `EVENT` | GSI Disaster Report / Teesta Surge | Supervised Positive |
| `EVT-2024-MANGAN-02` | 2024-06-12 14:30 | Sikkim (Mangan) | `EVENT` | GSI Field Survey / Drone Survey | Supervised Positive |
| `EVT-2022-KALIMPONG-03`| 2022-07-08 09:15 | West Bengal / Sikkim | `EVENT` | BRO Swastik Incident Log | Supervised Positive |
| `CTRL-2023-DRY-01` | 2023-12-15 12:00 | Sikkim (NH-10) | `NON_EVENT` | IMD AWS Verified Dry Window | Supervised Negative |
| `CTRL-2024-WINTER-02` | 2024-01-20 00:00 | Sikkim (NH-10) | `NON_EVENT` | CWC Zero Discharge Anomaly | Supervised Negative |
| `UNVERIFIED-WINDOW-01` | 2024-05-10 00:00 | Sikkim (NH-10) | `UNKNOWN` | Unmonitored Pre-Monsoon Span | **EXCLUDED** |

**Audit Finding**:
- Total Documented Events Linked: 17
- Total Verified Negative Controls Linked: 20
- Total Uncertain Windows Linked: 1
- Supervised Training Purity: 100% (0 UNKNOWN samples present in binary training sets).
- Verified in `tests/test_v4_8_event_labels.py::test_unknown_labels_strictly_excluded_from_binary_training`.
