# -*- coding: utf-8 -*-
"""
services/packet_replay_service.py
=================================
PARVAT NETRA • In-Situ Telemetry Deterministic Packet Replay & Forensic Pipeline
---------------------------------------------------------------------------------
Phase V4.8 Mandatory Invariant:
Replays raw captured OTA packets for deterministic offline analysis and regression testing.
Enforces that all replayed data is permanently branded as:
    provenance = "[REPLAYED_REAL]"
    source_class = "REPLAYED_REAL"
and can NEVER be promoted to LIVE or LIVE_PHYSICAL.
"""

from __future__ import annotations

import os
import json
import time
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Iterator

from firmware.packet_codec import (
    BinaryPacketCodec,
    FRAME_LENGTH_BYTES
)
from services.telemetry_contract import (
    TelemetryPacket,
    MeasurementItem,
    QUALITY_GOOD,
    QUALITY_DEGRADED
)

logger = logging.getLogger("PACKET_REPLAY")

SOURCE_CLASS_LIVE_PHYSICAL = "LIVE_PHYSICAL"
SOURCE_CLASS_BENCH_HARDWARE = "BENCH_HARDWARE"
SOURCE_CLASS_SIMULATED = "SIMULATED"
SOURCE_CLASS_DERIVED = "DERIVED"
SOURCE_CLASS_CACHED = "CACHED"
SOURCE_CLASS_UNAVAILABLE = "UNAVAILABLE"
SOURCE_CLASS_REPLAYED_REAL = "REPLAYED_REAL"

VALID_SOURCE_CLASSES = {
    SOURCE_CLASS_LIVE_PHYSICAL,
    SOURCE_CLASS_BENCH_HARDWARE,
    SOURCE_CLASS_SIMULATED,
    SOURCE_CLASS_DERIVED,
    SOURCE_CLASS_CACHED,
    SOURCE_CLASS_UNAVAILABLE,
    SOURCE_CLASS_REPLAYED_REAL
}

MODE_NORMAL = "NORMAL"
MODE_OUT_OF_ORDER = "OUT_OF_ORDER"
MODE_DUPLICATE = "DUPLICATE"
MODE_PACKET_LOSS = "PACKET_LOSS"


@dataclass
class PacketForensicRecord:
    packet_id: str
    sensor_id: str
    gateway_id: str
    sequence_number: int
    sensor_timestamp: str
    received_timestamp: str
    payload_hash: str
    crc_result: str           # PASS | FAIL
    decoder_version: str = "v4.8-codec18"
    firmware_version: str = "fw-1.4.2"
    transport: str = "LORA"
    source: str = SOURCE_CLASS_REPLAYED_REAL

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PacketReplayEngine:
    """
    Deterministic playback engine for raw packet capture files.
    Ensures zero masquerading of replayed data as live operational feeds.
    """

    def __init__(self, capture_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.capture_dir = capture_dir or os.path.join(base_dir, "data", "raw", "telemetry")
        os.makedirs(self.capture_dir, exist_ok=True)
        self._replayed_history: List[PacketForensicRecord] = []

    def load_capture_file(self, file_name: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Loads a packet capture JSON or binary ledger from data/raw/telemetry/.
        Returns (packets_list, metadata).
        """
        path = os.path.join(self.capture_dir, file_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Packet capture file not found: {path}")

        file_size = os.path.getsize(path)
        with open(path, "rb") as f:
            raw_bytes = f.read()
            sha256 = hashlib.sha256(raw_bytes).hexdigest()

        try:
            data = json.loads(raw_bytes.decode("utf-8"))
            packets = data.get("packets", data) if isinstance(data, dict) else data
            meta = {
                "file_name": file_name,
                "file_path": path,
                "file_size_bytes": file_size,
                "sha256": sha256,
                "packet_count": len(packets),
                "loaded_at_utc": datetime.now(timezone.utc).isoformat()
            }
            return packets, meta
        except Exception as e:
            raise ValueError(f"Failed to parse packet capture {file_name}: {e}")

    def save_capture_file(self, file_name: str, packets: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Saves a list of raw captured packets with immutable SHA-256 metadata.
        """
        path = os.path.join(self.capture_dir, file_name)
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "metadata": metadata or {
                "corridor_id": "CORR-NH10-SIKKIM-KM48",
                "capture_timestamp_utc": now_iso,
                "format": "JSON_CANONICAL_PACKET_STREAM"
            },
            "packet_count": len(packets),
            "packets": packets
        }
        content = json.dumps(payload, indent=2)
        content_bytes = content.encode("utf-8")
        with open(path, "wb") as f:
            f.write(content_bytes)
        return hashlib.sha256(content_bytes).hexdigest()

    def replay_packets(
        self,
        packets: List[Dict[str, Any]],
        mode: str = MODE_NORMAL,
        loss_rate: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Transforms packets into REPLAYED_REAL format.
        Preserves original timestamp, sequence number, and sensor values.
        Applies playback modes (NORMAL, OUT_OF_ORDER, DUPLICATE, PACKET_LOSS).
        """
        if not packets:
            return []

        out = []
        for p in packets:
            # Deep-copy dictionary
            r = dict(p)
            # Enforce REPLAYED_REAL provenance
            r["provenance"] = "[REPLAYED_REAL]"
            r["source_class"] = SOURCE_CLASS_REPLAYED_REAL
            r["replayed_at_utc"] = datetime.now(timezone.utc).isoformat()
            
            # Record forensic record
            rec = PacketForensicRecord(
                packet_id=str(r.get("packet_id", f"PKT-REPLAY-{r.get('sequence_number', 0)}")),
                sensor_id=str(r.get("sensor_id", r.get("device_id", "UNKNOWN"))),
                gateway_id=str(r.get("gateway_id", "GW-NH10-KM48-01")),
                sequence_number=int(r.get("sequence_number", 0)),
                sensor_timestamp=str(r.get("timestamp", "")),
                received_timestamp=str(r["replayed_at_utc"]),
                payload_hash=hashlib.sha256(json.dumps(r.get("measurements", {})).encode("utf-8")).hexdigest(),
                crc_result="PASS" if r.get("crc_valid", True) else "FAIL",
                source=SOURCE_CLASS_REPLAYED_REAL
            )
            self._replayed_history.append(rec)
            out.append(r)

        if mode == MODE_OUT_OF_ORDER:
            # Reverse order of consecutive pairs
            for i in range(0, len(out) - 1, 2):
                out[i], out[i + 1] = out[i + 1], out[i]

        elif mode == MODE_DUPLICATE:
            # Duplicate the first packet
            if out:
                out.insert(1, dict(out[0]))

        elif mode == MODE_PACKET_LOSS:
            # Drop every nth packet according to loss_rate
            drop_interval = int(round(1.0 / max(0.01, min(0.99, loss_rate)))) if loss_rate > 0 else 0
            if drop_interval > 0:
                out = [pkt for idx, pkt in enumerate(out) if (idx + 1) % drop_interval != 0]

        return out

    def get_forensics_history(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._replayed_history]


GLOBAL_PACKET_REPLAY_ENGINE = PacketReplayEngine()
