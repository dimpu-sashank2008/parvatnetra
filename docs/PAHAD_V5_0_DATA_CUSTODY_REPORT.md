# PARVAT NETRA / PAHAD AI — PHASE V5.0
## RAW TELEMETRY DATA CUSTODY & INTEGRITY REPORT

**Storage Architecture**: Bit-for-Bit Immutable Ingestion Directory  
**Base Directory**: `data/raw/field_telemetry/<corridor>/<site>/<sensor>/<YYYY>/<MM>/<DD>/`  

---

### 1. Architectural Design

To support rigorous scientific publication and legal evidentiary standards for post-disaster inquiries, raw sensor transmissions must never be altered or overwritten during normalization.

```
data/raw/field_telemetry/
└── CORR-NH10-SIKKIM-KM48/
    └── KM48/
        ├── PIEZO-NH10-KM48-01/
        │   └── 2026/
        │       └── 09/
        │           └── 20/
        │               ├── PIEZO-NH10-KM48-01_20260920T120000Z_a1b2c3d4.bin
        │               └── PIEZO-NH10-KM48-01_20260920T120000Z_a1b2c3d4.manifest.json
        └── INCL-NH10-KM48-01/
            └── ...
```

---

### 2. Cryptographic Custody Manifest Format

Every raw binary or JSON payload is accompanied by an immutable manifest:

```json
{
  "corridor_id": "CORR-NH10-SIKKIM-KM48",
  "site_id": "KM48",
  "sensor_id": "PIEZO-NH10-KM48-01",
  "timestamp_utc": "2026-09-20T12:00:00Z",
  "byte_count": 38,
  "payload_file": "PIEZO-NH10-KM48-01_20260920T120000Z_a1b2c3d4.bin",
  "payload_sha256": "a1b2c3d4e5f6...32bytes",
  "custody_signer": "PARVAT_NETRA_CUSTODY_DAEMON",
  "provenance": "BENCH_SIMULATED",
  "metadata": {
    "source": "BENCH_FIXTURE",
    "crc_valid": true
  }
}
```

---

### 3. Tamper Detection Verification

During automated testing (`test_v5_0_raw_custody.py`), the custody engine demonstrated that:
1. Payloads re-hashed against stored manifests verify bit-for-bit identity.
2. If a raw file is modified by even one bit, the custody auditor immediately flags `TAMPER_DETECTED` and invalidates the record from entering the downstream analytics pipeline.
