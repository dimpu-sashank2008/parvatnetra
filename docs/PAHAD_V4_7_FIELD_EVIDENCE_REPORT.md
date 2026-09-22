# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Physical Field Evidence Packaging, Cryptographic Verification & Event Labeling Framework

**Document Version**: 1.0.0  
**Phase**: V4.7 Engineering Commissioning  
**System Status**: BENCH_READY_FIELD_EVIDENCE_PENDING  
**Module**: `services/field_evidence_manager.py`  
**Test Suite**: `tests/test_v4_7_field_evidence.py`  

---

## 1. Objective & The Evidence Packaging Mandate

In critical early-warning systems, claims of physical ground sensor instrumentation or landslide event detections must be anchored to verifiable, tamper-evident physical artifacts. PARVAT NETRA establishes an evidence packaging architecture where every sensor node possesses an isolated cryptographic dossier under:

$$\text{field\_evidence/}\langle \text{sensor\_id} \rangle\text{/}$$

This framework guarantees that no synthetic, simulated, or hypothetical sensor reading can ever masquerade as real-world field truth.

---

## 2. Directory Hierarchy & Artifact Manifest

For each registered node, the directory structure enforces strict separation of artifact types:

```
field_evidence/
├── PIEZO-NH10-KM48-01/
│   ├── evidence_manifest.json          <-- SHA-256 ledger of all artifacts
│   ├── calibration_cert.pdf            <-- NABL certified laboratory calibration
│   ├── bench_test_hil_log.csv          <-- 72-hour HIL hardware test log
│   ├── borehole_drilling_log.pdf       <-- Pending field drilling [STATUS: NOT_AVAILABLE]
│   └── installation_photos/            <-- Downhole installation photos [STATUS: NOT_AVAILABLE]
├── INCL-NH10-KM48-01/
│   ├── evidence_manifest.json
│   ├── calibration_cert.pdf
│   └── bench_test_hil_log.csv
├── TILT-NH10-KM48-01/
│   ├── evidence_manifest.json
│   └── bench_test_hil_log.csv
├── RAIN-NH10-KM48-01/
│   └── evidence_manifest.json
└── GW-NH10-KM48-01/
    └── evidence_manifest.json
```

---

## 3. Cryptographic Verification & Tamper Detection

Every evidence item registered through `FieldEvidenceManager.register_evidence()` undergoes mandatory cryptographic processing:
1. **SHA-256 Hash Computation**: The exact bitstream of the uploaded artifact is hashed using SHA-256.
2. **Immutable Ledger Entry**: The file hash, size, timestamp, operator identity, and artifact classification are recorded in `evidence_manifest.json`.
3. **Integrity Audit**: Automated background audit tasks re-hash all stored evidence files and verify bit-for-bit equality against the manifest. Any file alteration immediately trips `PROVENANCE_COUNTERFEIT` and downgrades telemetry trust to `UNVERIFIED`.

---

## 4. Handling Missing Physical Artifacts: The `NOT_AVAILABLE` Protocol

A core SIH-grade transparency invariant of PARVAT NETRA is that pending or missing physical evidence is never faked with placeholder files.

When an artifact category cannot be fulfilled because physical slope execution is pending:
- The system explicitly records `status: "NOT_AVAILABLE"` in the manifest.
- The reason code is logged (e.g., `PENDING_BRO_FIELD_INSTALLATION`).
- The sensor acceptance engine refuses transition past `BENCH_ACCEPTED`.

```json
{
  "evidence_id": "EVID-PIEZO-NH10-003",
  "sensor_id": "PIEZO-NH10-KM48-01",
  "evidence_type": "INSTALLATION_RECORD",
  "file_path": null,
  "file_hash": null,
  "status": "NOT_AVAILABLE",
  "description": "Downhole 12m borehole grouting and piezometer installation awaiting joint BRO Swastik deployment"
}
```

---

## 5. Event Label Linkage Foundation

Supervised training of landslide prediction classifiers requires rigorous ground-truth event labeling. In `FieldEvidenceManager`, event labeling operates under a 3-state protocol:

```
                      +-------------------+
                      |   Candidate Time  |
                      |      Window       |
                      +---------+---------+
                                |
             +------------------+------------------+
             |                                     |
    Visual / Survey                      Verified Absence of
    Movement Corroborated                 Deformation & Movement
             |                                     |
             v                                     v
       [LABEL: EVENT]                      [LABEL: NON_EVENT]
     (event_label = 1)                     (event_label = 0)
             |                                     |
             +------------------+------------------+
                                |
                     Uncertain / Insufficient
                           Field Data
                                |
                                v
                       [LABEL: UNKNOWN]
                 (Strictly excluded from ML)
```

1. **`EVENT` (Positive Ground Truth)**: Assigned only when a documented slope failure, crown scarp displacement, tension cracking, or debris flow is verified by GSI field reports, drone imagery, or high-confidence citizen corroboration.
2. **`NON_EVENT` (Negative Control Truth)**: Assigned only for time windows where instrumentation, satellite InSAR, and local authorities explicitly verify zero movement across the monitored hillslope.
3. **`UNKNOWN` (Uncertain Ground Truth)**: Assigned whenever sensor telemetry was offline, weather was unobserved, or post-event reconnaissance was absent. **Samples marked `UNKNOWN` are strictly forbidden from binary supervised training.**

---

## 6. Audit Verdict

All evidence packaging routines in `services/field_evidence_manager.py` have passed unit and integration verification in `tests/test_v4_7_field_evidence.py`. No synthetic field evidence exists in the repository.
