# -*- coding: utf-8 -*-
"""
tests/test_v5_0_raw_custody.py
==============================
Phase V5.0 Test Suite: Raw Telemetry Data Custody & Cryptographic Verification
"""

import os
from datetime import datetime, timezone
import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestRawDataCustody:
    """Verifies directory partitioning, SHA-256 manifest logging, and tamper detection."""

    def test_custody_directory_structure(self, deployment_engine):
        dt = datetime(2026, 9, 20, 12, 0, 0, tzinfo=timezone.utc)
        p = deployment_engine.get_custody_path(
            corridor_id="CORR-NH10-SIKKIM-KM48",
            site_id="KM48",
            sensor_id="PIEZO-NH10-KM48-01",
            dt=dt
        )
        expected_suffix = os.path.join(
            "field_telemetry",
            "CORR-NH10-SIKKIM-KM48",
            "KM48",
            "PIEZO-NH10-KM48-01",
            "2026",
            "09",
            "20"
        )
        assert expected_suffix in p

    def test_record_and_verify_custody_batch(self, deployment_engine, tmp_path):
        payload = b"TEST_RAW_LORA_PAYLOAD_BYTES_0xDEADBEEF"
        res = deployment_engine.record_raw_telemetry_batch(
            corridor_id="CORR-NH10-SIKKIM-KM48",
            site_id="KM48",
            sensor_id="PIEZO-NH10-KM48-01",
            raw_payload=payload,
            metadata={"source": "BENCH_FIXTURE", "operator": "CustodyTest"}
        )
        assert res["status"] == "CUSTODY_RECORDED"
        assert os.path.exists(res["payload_path"])
        assert os.path.exists(res["manifest_path"])

        # Verify integrity
        ok, msg = deployment_engine.verify_custody_integrity(res["manifest_path"])
        assert ok is True
        assert "bit-for-bit identical" in msg

    def test_custody_tamper_detection(self, deployment_engine):
        payload = b"ORIGINAL_DATA_123"
        res = deployment_engine.record_raw_telemetry_batch(
            corridor_id="CORR-NH10-SIKKIM-KM48",
            site_id="KM48",
            sensor_id="INCL-NH10-KM48-01",
            raw_payload=payload,
            metadata={"source": "BENCH_FIXTURE"}
        )

        # Alter payload file
        with open(res["payload_path"], "wb") as f:
            f.write(b"TAMPERED_DATA_456")

        ok, msg = deployment_engine.verify_custody_integrity(res["manifest_path"])
        assert ok is False
        assert "TAMPER_DETECTED" in msg
