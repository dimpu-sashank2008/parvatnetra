# PARVAT NETRA / PAHAD AI — PHASE V4.6
# In-Situ Telemetry Threat Model & Security Verification Report

**Document Version**: 1.0.0  
**Security Standard**: National Critical Infrastructure / SIH Defense Grade  
**Scope**: In-Situ Sensors, LoRaWAN Gateways, Edge Ingestion APIs, Machine Learning Artifacts  

---

## 1. Threat Model for Mountain Geotechnical Telemetry

In-situ slope monitoring stations operate in remote, physically unmonitored Himalayan terrain. The threat vectors considered include:

1. **RF Replay Attacks**: An adversary captures previously transmitted "safe" telemetry frames and replays them during active rainfall to mask slope failure.
2. **RF Packet Injection / Falsification**: Malicious nodes transmit fake high pore-pressure readings to trigger false highway closures.
3. **Data Counterfeiting**: Developers or rogue scripts post synthetic/simulated data tagged as `[LIVE]` to inflate system performance ratings.
4. **Clock Drift Manipulation**: Malicious packets with future timestamps injected to desynchronize sliding window derivative calculations.
5. **Model Artifact Tampering**: Unauthorized modification of production model weights to alter safety thresholds.

---

## 2. Security Controls & Defenses

| Threat Vector | Implemented Security Control | Enforcement Mechanism |
| :--- | :--- | :--- |
| **RF Replay Attacks** | Monotonic Sequence Numbering & Deduplication Hash Ring | Replays rejected with `REJECTED_DUPLICATE` or `REJECTED_DUPLICATE_SEQUENCE` |
| **Packet Falsification** | CRC-16-CCITT Verification & Sensor Registry Whitelist | Unregistered node IDs and corrupted checksums rejected at Layer 1/2 |
| **Data Counterfeiting** | Strict Zero-Counterfeit Enforcement Filter | Ingestion service rejects `source="BENCH_SIMULATOR"` claiming `provenance="LIVE"` |
| **Clock Manipulation** | Strict Future Timestamp Clamping | Timestamps $>30\text{ s}$ ahead of server UTC rejected (`REJECTED_FUTURE_TIMESTAMP`) |
| **REST Injection** | Parameterized SQL Queries via psycopg2 / SQLite | Zero dynamic string concatenations in ingestion path |
| **Model Weight Tampering** | Cryptographic SHA-256 Locking & Automated Test Assertions | CI/Pytest verifies locked SHA-256 hashes of production weights on every commit |

---

## 3. Production Weights Integrity Verification

Automated tests in `tests/test_v4_6_dual_stream.py` verify the exact cryptographic hashes of all model weights:
- **Production V3 (`models/pahad_lstm_v3_weights.pt`)**:
  `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` (**VERIFIED 100% UNTOUCHED**)
- **Offline Research V4.5 (`models/pahad_lstm_v4_5_research_weights.pt`)**:
  `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f` (**VERIFIED 100% UNTOUCHED**)
