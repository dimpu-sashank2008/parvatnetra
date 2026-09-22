# -*- coding: utf-8 -*-
"""
tests/test_v5_0_commissioning.py
================================
Phase V5.0 Test Suite: 7-Stage Sensor Status Matrix Lifecycle Governance
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    CANONICAL_V5_STAGES,
    STAGE_PLANNED,
    STAGE_BENCH_ACCEPTED,
    STAGE_PHYSICAL_VERIFIED,
    STAGE_INSTALLATION_VERIFIED,
    STAGE_COMMISSIONING_PENDING,
    STAGE_FIELD_COMMISSIONED,
    STAGE_LIVE_MONITORING
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestSensorStatusMatrix:
    """Verifies the 7-stage Sensor Status Matrix and forward-only transition enforcement."""

    def test_canonical_matrix_stages_order(self):
        expected_stages = [
            "PLANNED",
            "BENCH_ACCEPTED",
            "PHYSICAL_VERIFIED",
            "INSTALLATION_VERIFIED",
            "COMMISSIONING_PENDING",
            "FIELD_COMMISSIONED",
            "LIVE_MONITORING"
        ]
        assert CANONICAL_V5_STAGES == expected_stages

    def test_all_sensors_currently_at_bench_accepted(self, deployment_engine):
        matrix = deployment_engine.get_sensor_status_matrix()
        assert matrix["overall_matrix_status"] == STAGE_BENCH_ACCEPTED
        for s_id, data in matrix["sensors"].items():
            assert data["current_stage"] == STAGE_BENCH_ACCEPTED
            assert data["allowed_next_stage"] == STAGE_PHYSICAL_VERIFIED
            assert data["physical_verified"] is False
            assert data["commissioned"] is False

    def test_skipping_stages_is_strictly_forbidden(self, deployment_engine):
        # Cannot jump from BENCH_ACCEPTED to FIELD_COMMISSIONED
        ok, msg = deployment_engine.validate_stage_transition(
            sensor_id="INCL-NH10-KM48-01",
            target_stage=STAGE_FIELD_COMMISSIONED,
            evidence={}
        )
        assert ok is False
        assert "skipping forbidden" in msg.lower()

    def test_transition_to_physical_verified_blocked_without_photo_and_challan(self, deployment_engine):
        ok, msg = deployment_engine.validate_stage_transition(
            sensor_id="INCL-NH10-KM48-01",
            target_stage=STAGE_PHYSICAL_VERIFIED,
            evidence={}
        )
        assert ok is False
        assert "rejected" in msg.lower()
        assert "nameplate photo" in msg.lower()

    def test_transition_to_physical_verified_succeeds_with_valid_evidence(self, deployment_engine):
        ok, msg = deployment_engine.validate_stage_transition(
            sensor_id="INCL-NH10-KM48-01",
            target_stage=STAGE_PHYSICAL_VERIFIED,
            evidence={
                "nameplate_photo_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "delivery_challan_ref": "CHALLAN-DGSI-2026-0441-SIGNED"
            }
        )
        assert ok is True
        assert "accepted" in msg.lower()
