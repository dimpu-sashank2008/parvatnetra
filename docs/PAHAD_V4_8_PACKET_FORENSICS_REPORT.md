# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Raw Packet Forensics, SHA-256 Immutability & Audit Trail Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Modules**: `services/packet_replay_service.py`, `firmware/packet_codec.py`, `services/telemetry_contract.py`  
**Test Suite**: `tests/test_v4_8_packet_forensics.py`  

---

## 1. Objective: Immutable Telemetry Forensics

In mission-critical disaster early-warning engineering, raw incoming sensor telemetry frames must be forensically preserved in their exact bit-for-bit representation. PARVAT NETRA enforces an immutable raw evidence layer under:

$$\text{data/raw/telemetry/}$$

No backend ingestion service, quality filter, or analytics script is permitted to modify or overwrite raw packet records.

---

## 2. Canonical Packet Forensics Schema

For every captured frame, the `PacketForensicRecord` data structure captures complete transmission provenance:

| Forensic Field | Data Type | Scientific Purpose | Example Value |
| :--- | :--- | :--- | :--- |
| `packet_id` | `string` | Unique UUID/sequence identifier | `PKT-RAW-001` |
| `sensor_id` | `string` | Registered corridor instrument ID | `PIEZO-NH10-KM48-01` |
| `gateway_id` | `string` | Receiving edge concentrator gateway | `GW-NH10-KM48-01` |
| `sequence_number` | `uint16` | Monotonic frame sequence from device | `1` |
| `sensor_timestamp` | `ISO-8601` | Transducer Real-Time Clock timestamp | `2026-09-20T12:00:00Z` |
| `received_timestamp`| `ISO-8601` | Server arrival UTC timestamp | `2026-09-20T12:00:00.245Z` |
| `payload_hash` | `hex string`| SHA-256 hash of measurement payload | `09ff67858ed1...` |
| `crc_result` | `PASS/FAIL` | Hardware CRC16-CCITT evaluation | `PASS` |
| `decoder_version` | `string` | Codec parser implementation version | `v4.8-codec18` |
| `firmware_version`| `string` | Edge controller firmware release | `fw-1.4.2` |
| `transport` | `string` | Physical transmission layer | `LORA` |
| `source` | `string` | Provenance classification | `REPLAYED_REAL` / `LIVE_PHYSICAL` |

---

## 3. Cryptographic Tamper-Evidence

1. **Bitstream Invariant**: Captured raw files (`sample_corridor_packets.json`) are hashed upon creation using SHA-256.
2. **Audit Verification**: The replay service computes file hashes dynamically on ingestion. Any alteration of white space, delimiters, or values fails the integrity check and flags the stream with `PROVENANCE_COUNTERFEIT`.
3. **Reproducibility**: Raw byteframes permit byte-exact reproduction of decoding runs across independent metrology reviews.

---

## 4. Structured Observability Event Logging

The telemetry pipeline emits structured audit events for every operational anomaly:
- `REAL_PACKET_RECEIVED`: Valid packet verified against identity and CRC.
- `PACKET_REJECTED`: Packet rejected due to physical bounds or CRC corruption.
- `PACKET_DUPLICATE`: Replayed or re-transmitted sequence number detected.
- `PACKET_OUT_OF_ORDER`: Non-monotonic sequence or clock inversion observed.
- `SENSOR_ID_MISMATCH`: Incoming packet serial conflicts with registered identity.
- `TIMESTAMP_DRIFT`: Clock offset exceeds $30\text{s}$ future or $120\text{s}$ warning threshold.
