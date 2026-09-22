# -*- coding: utf-8 -*-
"""
tests/test_v4_7_dataset_lineage.py
==================================
Phase V4.7 Test Suite: Immutable Database Lineage, Store-and-Forward Replay & Trust Scoring
"""

import os
import json
import time
from datetime import datetime, timezone
import pytest

from services.kinematic_telemetry_service import KinematicTelemetryService
from engine.telemetry_trust_engine import (
    TelemetryTrustEngine,
    TRUST_VERIFIED,
    TRUST_DEGRADED,
    TRUST_UNVERIFIED
)
from engine.sensor_acceptance_engine import SensorAcceptanceEngine


@pytest.fixture
def service_and_engine(tmp_path):
    ledger_file = str(tmp_path / "acceptance_ledger.json")
    acc_engine = SensorAcceptanceEngine(persistence_path=ledger_file)
    # Register verified identity
    acc_engine.verify_and_set_identity(
        sensor_id="PIEZO-LINEAGE-01",
        manufacturer="Geokon LLC",
        model="4500AL",
        serial_number="GK-2026-9011",
        hardware_revision="REV-B",
        firmware_version="v2.1",
        sensor_type="PIEZOMETER"
    )

    reg_file = str(tmp_path / "test_reg.json")
    with open(reg_file, "w", encoding="utf-8") as f:
        json.dump({
            "corridor_id": "CORR-TEST",
            "field_deployment_pending": False,
            "sensors": [
                {
                    "sensor_id": "PIEZO-LINEAGE-01",
                    "sensor_type": "PIEZOMETER",
                    "unit": "kPa",
                    "range_min": -50.0,
                    "range_max": 500.0,
                    "serial_number": "GK-2026-9011",
                    "manufacturer": "Geokon LLC",
                    "model": "4500AL"
                }
            ]
        }, f)

    svc = KinematicTelemetryService(registry_path=reg_file)
    trust_engine = TelemetryTrustEngine(acceptance_engine=acc_engine)
    return svc, trust_engine, acc_engine


class TestStoreAndForwardReplay:
    """Tests edge store-and-forward replay idempotency."""

    def test_store_and_forward_replay_idempotency(self, service_and_engine):
        svc, _, _ = service_and_engine
        now_iso = datetime.now(timezone.utc).isoformat()

        obs = {
            "observation_id": "obs-replay-001",
            "sensor_id": "PIEZO-LINEAGE-01",
            "corridor_id": "CORR-TEST",
            "site_id": "SITE-1",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 24.5,
            "unit": "kPa",
            "quality": "GOOD",
            "source": "BENCH_SIMULATOR",
            "provenance": "SIMULATED",
            "status": "SIMULATED",
            "sequence_number": 5,
            "transport": "EDGE_BUFFER_REPLAY"
        }

        # First ingestion
        res1 = svc.ingest_canonical_observation(obs)
        assert res1.is_valid is True

        # Second ingestion with transport="EDGE_BUFFER_REPLAY" should be handled gracefully without duplicate error
        res2 = svc.ingest_canonical_observation(obs)
        assert res2.is_valid is True
        assert res2.status == "ACCEPTED"


class TestTelemetryTrustScoring:
    """Tests transparent trust classification across 7 criteria."""

    def test_verified_trust_classification(self, service_and_engine):
        _, trust_engine, _ = service_and_engine
        now_iso = datetime.now(timezone.utc).isoformat()

        obs = {
            "observation_id": "obs-trust-01",
            "sensor_id": "PIEZO-LINEAGE-01",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "received_at": now_iso,
            "value": 22.0,
            "unit": "kPa",
            "quality": "GOOD",
            "sequence_number": 1,
            "battery_voltage": 12.8,
            "signal_strength": -75.0,
            "provenance": "SIMULATED",
            "source": "BENCH_SIMULATOR"
        }

        assessment = trust_engine.assess_observation(obs)
        # Identity is verified, value is in range, timestamps are valid
        assert assessment.identity_valid is True
        assert assessment.range_valid is True
        assert assessment.timestamp_valid is True
        assert assessment.score_pct >= 80.0

    def test_unverified_trust_on_unknown_identity(self, service_and_engine):
        _, trust_engine, _ = service_and_engine
        now_iso = datetime.now(timezone.utc).isoformat()

        obs = {
            "observation_id": "obs-trust-02",
            "sensor_id": "UNKNOWN-ROGUE-SENSOR",
            "sensor_type": "PIEZOMETER",
            "timestamp_utc": now_iso,
            "value": 15.0,
            "unit": "kPa",
            "sequence_number": 1
        }

        assessment = trust_engine.assess_observation(obs)
        assert assessment.telemetry_trust == TRUST_UNVERIFIED
        assert "IDENTITY_UNVERIFIED" in assessment.reasons
