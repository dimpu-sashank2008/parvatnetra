# PARVAT NETRA / PAHAD AI — PHASE V5.0
## FIELD TELEMETRY CENSUS & RAW DATA CUSTODY LEDGER

**Authoritative Status**: `PHYSICAL_TELEMETRY_PENDING`  
**Verified Live Mountain Observations**: `0`  
**Bench / HIL Test Frames**: `8,640`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  

---

### 1. Telemetry Census by Provenance Badge

| Category | Dataset Description | Observation Count | Provenance Badge | Storage Path |
| :--- | :--- | :---: | :---: | :--- |
| **Live Mountain Telemetry** | Genuine in-situ mountain transmissions | **0** | `[LIVE]` | `data/raw/field_telemetry/` |
| **Bench HIL Loopback** | USB-serial & bench loopback test stream | 8,640 | `[BENCH]` | `data/processed/bench_telemetry/` |
| **Monte Carlo Physics** | Synthetic rainfall infiltration simulations | 120 | `[SIMULATED]`| `data/simulated/corridor_profiles/` |
| **Replayed Test Frames** | Historical packet replay sanity verification | 5 | `[REPLAY]` | `data/raw/field_telemetry/test/` |

---

### 2. Raw Telemetry Custody Architecture
Under Phase V5.0 rules, all raw field transmissions are permanently preserved in their original immutable byte format prior to parsing or database ingestion:

```
data/raw/field_telemetry/
└── CORR-NH10-SIKKIM-KM48/
    └── KM48/
        ├── PIEZO-NH10-KM48-01/
        │   └── 2026/09/21/
        │       ├── PIEZO-NH10-KM48-01_20260921T151011Z_cb900770.bin
        │       └── PIEZO-NH10-KM48-01_20260921T151011Z_cb900770.manifest.json
        └── INCL-NH10-KM48-01/
            └── 2026/09/21/
                ├── INCL-NH10-KM48-01_20260921T151011Z_b979e5e4.bin
                └── INCL-NH10-KM48-01_20260921T151011Z_b979e5e4.manifest.json
```

Each transmission writes:
- `.bin`: Exact raw byte payload received over RF or serial interface.
- `.manifest.json`: Metadata record containing SHA-256 hash, byte length, UTC arrival timestamp, receiver identity, and tamper detection signature.

Tamper verification re-reads the payload file, computes its SHA-256 digest, and confirms bit-for-bit equivalence.
