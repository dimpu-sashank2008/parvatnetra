# PARVAT NETRA / PAHAD AI — PHASE V4.6
# In-Situ Telemetry Ingestion Pipeline Verification Report

**Document Version**: 1.0.0  
**Phase**: V4.6 Engineering  
**Service Implementation**: `services/kinematic_telemetry_service.py`  
**Test Suite**: `tests/test_v4_6_telemetry.py`  

---

## 1. Ingestion Pipeline Architecture

The ingestion pipeline handles both edge-concentrated binary frames (LoRaWAN IN865) and cloud/REST JSON observations. It enforces seven layers of integrity checks before accepting a measurement into the high-frequency sliding window buffer.

```
Incoming Stream (REST JSON / Binary LoRa)
                     |
                     v
       [Layer 1: Frame Format & Length] --------> REJECT (Invalid hex/length)
                     |
                     v
       [Layer 2: CRC-16-CCITT Checksum] -------> REJECT (Bit corruption)
                     |
                     v
       [Layer 3: Mandatory Fields Check] ------> REJECT (Missing schema keys)
                     |
                     v
       [Layer 4: Zero-Counterfeit Provenance] -> REJECT (SIMULATED claimed as LIVE)
                     |
                     v
       [Layer 5: Clock Drift & Monotonicity] --> REJECT (Future ts > 30s)
                     |
                     v
       [Layer 6: Deduplication & Replay] ------> REJECT (Seen hash / duplicate seq)
                     |
                     v
       [Layer 7: Physical Limits Clamping] ----> REJECT (Impossible reading)
                     |
                     v
        [ACCEPTED -> Buffered in Memory]
```

---

## 2. Validation Rule Execution Results

Automated tests in `tests/test_v4_6_telemetry.py` exercised every failure and success path:

| Test Case | Ingestion Payload Condition | Expected Behavior | Actual Test Result |
| :--- | :--- | :--- | :--- |
| `test_accept_valid_bench_observation` | Valid observation conforming to schema | Accepted, status 200, buffered | **PASSED** |
| `test_reject_counterfeit_live_provenance`| `source="BENCH_SIMULATOR"`, `provenance="LIVE"` | Rejected: `REJECTED_PROVENANCE_COUNTERFEIT` | **PASSED** |
| `test_reject_future_timestamp` | Timestamp $>30\text{ s}$ ahead of server clock | Rejected: `REJECTED_FUTURE_TIMESTAMP` | **PASSED** |
| `test_reject_duplicate_sequence` | Duplicate packet hash / sequence replay | Rejected: `REJECTED_DUPLICATE` | **PASSED** |
| `test_reject_out_of_physical_bounds` | Piezometer reading $999.0\text{ kPa}$ ($[-50, 500]$) | Rejected: `REJECTED_IMPOSSIBLE_VALUE` | **PASSED** |
| `test_valid_binary_lora_frame` | 18-byte packed binary frame with valid CRC | Decoded, normalized, accepted | **PASSED** |
| `test_corrupted_crc_rejected` | 1-bit corrupted payload byte | Rejected: `REJECTED_CRC_ERROR` | **PASSED** |
| `test_invalid_frame_length_rejected` | Truncated binary frame ($5\text{ bytes}$) | Rejected: `REJECTED_FRAME_LENGTH` | **PASSED** |

---

## 3. Observability & Event Journal

All ingestion activities emit structured machine-readable events into an in-memory ring buffer (up to 1,000 events) accessible via `/api/telemetry/status`:
- `TELEMETRY_RECEIVED`: Packet parsed, validated, and added to history.
- `TELEMETRY_REJECTED`: Packet failed schema, physical, or cryptographic checks.
- `TELEMETRY_DUPLICATE`: Replay attempt or duplicate sequence number detected.
- `TELEMETRY_OUT_OF_ORDER`: Non-monotonic sequence packet flagged.
- `TELEMETRY_STALE`: Sensor exceeded freshness threshold ($900\text{ s}$).
- `SENSOR_OFFLINE`: Sensor silent for $>2\times$ threshold ($1800\text{ s}$).
- `SENSOR_RECOVERED`: Offline sensor resumed transmitting valid observations.
