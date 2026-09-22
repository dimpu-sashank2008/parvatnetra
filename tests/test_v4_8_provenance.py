# -*- coding: utf-8 -*-
"""
tests/test_v4_8_provenance.py
=============================
Automated test suite for Phase V4.8 Provenance Lineage, Immutability & Corridor Isolation.
Tests:
  1. Corridor boundary isolation (rejecting foreign corridor IDs).
  2. Deduplication of replayed packets via hash tracking.
  3. Evidence file tamper detection via SHA-256 mismatch.
"""

import time
import pytest
from datetime import datetime, timezone
from services.kinematic_telemetry_service import (
    KinematicTelemetryService,
    CORRIDOR_ID_NH10
)
from firmware.packet_codec import BinaryPacketCodec


def test_corridor_boundary_isolation():
    """Confirms sensors registered to NH-10 cannot accept packets from foreign corridors."""
    service = KinematicTelemetryService()
    assert service.corridor_metadata["corridor_id"] == CORRIDOR_ID_NH10

    now_iso = datetime.now(timezone.utc).isoformat()
    foreign_obs = {
        "observation_id": "obs-foreign-001",
        "sensor_id": "PIEZO-NH10-KM48-01",
        "corridor_id": "CORR-FOREIGN-HIMALAYAS",  # Foreign corridor mismatch
        "site_id": "SITE-NH10-KM48",
        "sensor_type": "PIEZOMETER",
        "timestamp_utc": now_iso,
        "value": 25.0,
        "unit": "kPa",
        "quality": "GOOD",
        "source": "BENCH_SIMULATOR",
        "provenance": "SIMULATED",
        "status": "SIMULATED",
        "sequence_number": 1
    }
    res = service.ingest_canonical_observation(foreign_obs)
    assert res.is_valid is False
    assert "CORRIDOR_MISMATCH" in res.status


def test_packet_deduplication_via_hash():
    """Confirms identical binary payloads are identified and counted as duplicates."""
    service = KinematicTelemetryService()
    epoch = int(time.time())
    frame = BinaryPacketCodec.encode(
        device_short_id=101,
        sequence_number=1,
        timestamp_epoch=epoch,
        primary_val=24.5,
        secondary_val=1.2,
        tertiary_val=0.5,
        battery_pct=95.0,
        temperature_c=18.0
    )
    
    # Ingest first time
    res1 = service.ingest_binary_lora_frame(
        frame_bytes=frame,
        sensor_type="PIEZOMETER",
        sensor_id="PIEZO-NH10-KM48-01",
        provenance="BENCH"
    )
    assert res1.is_valid is True
    
    # Ingest second time (exact duplicate)
    res2 = service.ingest_binary_lora_frame(
        frame_bytes=frame,
        sensor_type="PIEZOMETER",
        sensor_id="PIEZO-NH10-KM48-01",
        provenance="BENCH"
    )
    assert res2.is_valid is False
    assert "DUPLICATE" in res2.status


def test_evidence_file_tamper_detection():
    """Confirms modifying an evidence file invalidates its SHA-256 and trips tamper detection."""
    import tempfile
    import os
    from engine.telemetry_evidence_audit_engine import compute_sha256_file
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(b"ORIGINAL_CALIBRATION_RECORD_V1")
        tmp_path = tmp.name
        
    try:
        orig_hash = compute_sha256_file(tmp_path)
        assert orig_hash is not None
        
        # Tamper with file
        with open(tmp_path, "wb") as f:
            f.write(b"TAMPERED_CALIBRATION_RECORD_V2")
            
        new_hash = compute_sha256_file(tmp_path)
        assert new_hash != orig_hash
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
