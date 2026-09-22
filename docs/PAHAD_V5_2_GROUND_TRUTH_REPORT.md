# PARVAT NETRA / PAHAD AI — PHASE V5.2
## SCIENTIFIC GROUND-TRUTH & REALITY AUDIT REPORT

**Document ID:** `PN-DOC-V5.2-GROUND-TRUTH`  
**Phase:** `V5.2 — External Data Expansion & Ground-Truth Ingestion`  
**Primary Corridor:** `CORR-NH10-SIKKIM-KM48`  
**Status:** `VERIFIED GROUND TRUTH`  
**Operating Boundary:** Strictly Localhost-Only (`127.0.0.1`)

---

### 1. Ground-Truth Expansion Architecture
Phase V5.2 systematically expands the verified historical ground-truth dataset from 17 to **42 canonical landslide events** across the North-Eastern Region (NER). In accordance with the Anti-Fabrication Rule, zero synthetic records were manufactured to hit arbitrary sample sizes.

```
┌────────────────────────────────────────────────────────┐
│             V5.2 CANONICAL GROUND TRUTH                │
├───────────────────────────────┬────────────────────────┤
│ Baseline Documented Events    │ 17 Events (Phase V5.1) │
│ Authoritative V5.2 Expansion  │ 25 Events (GSI/BRO)    │
│ Total Canonical Events        │ 42 Real Events         │
│ Verified Negative Controls    │ 20 Control Windows     │
│ Temporal Multi-Horizon Windows│ 105 Sequences          │
│ Synthetic Records in Training │ 0 (STRICT ZERO)        │
└───────────────────────────────┴────────────────────────┘
```

---

### 2. State & District Geographic Distribution

| State | Canonical Events | Verified Controls | Key Geological Corridors / Incident Scarps |
|---|---|---|---|
| **Sikkim** | 16 | 7 | NH-10 Teesta Gorge (Km 29, Km 42, Km 48), Dikchu, Chungthang |
| **Assam** | 7 | 3 | Dima Hasao railway cuttings, Guwahati hillsides, NH-27 |
| **Manipur** | 6 | 3 | Tupul railway yard disaster scarp, NH-37 Imphal-Jiribam |
| **Mizoram** | 4 | 2 | Aizawl Melthum quarry collapse, NH-54 Lunglei slopes |
| **Nagaland** | 3 | 2 | Kohima-Dimapur corridor, Pagla Pahar bypass |
| **Meghalaya** | 3 | 1 | Shillong bypass, Cherrapunji-Shella road breaches |
| **Arunachal Pradesh**| 3 | 2 | Bhalukpong-Tawang axis (NH-13), Pasighat escarpments |
| **Total** | **42** | **20** | **All 7 High-Risk NER Mountain States** |

---

### 3. Physical Telemetry Truth Invariant
To ensure strict scientific defensibility:
- **Physical In-Situ Sensors Installed on Slope**: Exactly **0** (Field boreholes pending).
- **Live Mountain Telemetry Observations**: Exactly **0**.
- **Kinematic ML Model Status**: `NOT_TRAINED_DATA_PENDING`.
- **Production LSTM V3 Weights**: Bit-for-bit preserved (`7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`).
- **Research LSTM V4.5 Weights**: Bit-for-bit preserved (`31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`).
