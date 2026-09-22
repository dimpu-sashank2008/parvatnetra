# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Deterministic Packet Replay & REPLAYED_REAL Provenance Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Module**: `services/packet_replay_service.py`  
**Test Suite**: `tests/test_v4_8_replay.py`  

---

## 1. Deterministic Packet Replay Architecture

To enable reproducible regression testing and offline algorithm validation without fabricating live field sensors, PARVAT NETRA provides a deterministic replay engine (`PacketReplayEngine`):

$$\text{Raw Packet Capture } \xrightarrow[\text{Immutable Read}]{\text{SHA-256 Verified}} \text{Replay Engine} \xrightarrow[\text{Provenance Stamped}]{\text{Modes (Normal/Loss/Dupl)}} \text{Pipeline Ingestion}$$

---

## 2. Mandatory `REPLAYED_REAL` Provenance Stamping

To prevent evaluator confusion or fraudulent claims of live connectivity:
- Every replayed packet is explicitly stamped with:
  $$\text{provenance} = \text{"[REPLAYED\_REAL]"}$$
  $$\text{source\_class} = \text{"REPLAYED\_REAL"}$$
- **Anti-Promotion Invariant**: Under no circumstance can replayed data be converted into `LIVE`, `LIVE_PHYSICAL`, or operational nowcasts.
- The UI renders replayed packets with a distinct blue badge `[REPLAYED_REAL]` to differentiate them from simulated (`[SIMULATED]`) or historical (`[HISTORICAL]`) data.

---

## 3. Replay Test Modes

The engine supports four deterministic transmission modes for stress testing the backend pipeline:
1. **`NORMAL`**: Exact chronological replay in ascending sequence.
2. **`OUT_OF_ORDER`**: Inverts packet pairs to verify that the backend sequence buffer and timestamp orderings handle network jitter gracefully.
3. **`DUPLICATE`**: Injects duplicate frames to confirm that the deduplication gate (`REJECTED_DUPLICATE`) catches repeats without double-counting rainfall or displacement.
4. **`PACKET_LOSS`**: Drops a configured fraction (e.g. 20% or 50%) of frames to test interpolation and stale telemetry alerts.
