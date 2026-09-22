# PARVAT NETRA / PAHAD AI — PHASE V5.0
## FIELD COMMISSIONING & 7-STAGE SENSOR STATUS MATRIX REPORT

**Authoritative Status**: `BENCH_ACCEPTED`  
**Target Stage**: `PHYSICAL_VERIFIED` (Blocked due to missing physical hardware artifacts)  

---

### 1. The 7-Stage Sensor Status Matrix Architecture

Phase V5.0 streamlines and solidifies sensor lifecycle governance into an immutable, forward-only 7-stage matrix:

```
[1. PLANNED]
     │
     ▼
[2. BENCH_ACCEPTED]        <── CURRENT STATE (All 5 nodes 100% bench & HIL validated)
     │
     ▼ (Requires physical nameplate photo & delivery challan)
[3. PHYSICAL_VERIFIED]     <── LOCKED (Physical evidence pending)
     │
     ▼ (Requires borehole/mounting sign-off & GPS survey)
[4. INSTALLATION_VERIFIED]
     │
     ▼ (Requires wiring continuity, power, & RF link SNR)
[5. COMMISSIONING_PENDING]
     │
     ▼ (Requires end-to-end site commissioning sign-off)
[6. FIELD_COMMISSIONED]
     │
     ▼ (Requires continuous live field stream passing 10-criteria gate)
[7. LIVE_MONITORING]
```

---

### 2. Corridor Node Matrix Evaluation

| Sensor Node ID | Sensor Type | Current Stage | Next Allowed Stage | Transition Status | Reason for Hold |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PIEZO-NH10-KM48-01` | Piezometer | `BENCH_ACCEPTED` | `PHYSICAL_VERIFIED` | **HOLD** | Nameplate photo & delivery challan missing |
| `INCL-NH10-KM48-01` | Inclinometer | `BENCH_ACCEPTED` | `PHYSICAL_VERIFIED` | **HOLD** | Nameplate photo & delivery challan missing |
| `TILT-NH10-KM48-01` | Tiltmeter | `BENCH_ACCEPTED` | `PHYSICAL_VERIFIED` | **HOLD** | Nameplate photo & delivery challan missing |
| `RAIN-NH10-KM48-01` | Rain Gauge | `BENCH_ACCEPTED` | `PHYSICAL_VERIFIED` | **HOLD** | Nameplate photo & delivery challan missing |
| `GW-NH10-KM48-01` | LoRa Gateway | `BENCH_ACCEPTED` | `PHYSICAL_VERIFIED` | **HOLD** | Nameplate photo & delivery challan missing |

---

### 3. Lifecycle Transition Governance Rules

1. **Strict Forward Progression**: Stages must be traversed sequentially. Jumping directly from `BENCH_ACCEPTED` to `FIELD_COMMISSIONED` or `LIVE_MONITORING` is programmatically blocked and raises an immediate rejection.
2. **Evidence-Backed Promotion**: Every promotion requires cryptographic artifacts (SHA-256 hashes of physical files, operator credentials).
3. **Bench Isolation**: Running simulation tests, HIL frames, or synthetic replays can validate `BENCH_ACCEPTED`, but cannot alter physical commissioning state.
