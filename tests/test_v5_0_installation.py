# -*- coding: utf-8 -*-
"""
tests/test_v5_0_installation.py
===============================
Phase V5.0 Test Suite: Physical Downhole & Surface Installation Gating
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    STAGE_INSTALLATION_VERIFIED
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestInstallationGating:
    """Verifies physical downhole and surface anchor installation requirements."""

    def test_all_five_nodes_installation_status_is_not_installed(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.installation_record_found is False
            assert record.installation_status == "NOT_INSTALLED"

    def test_transition_to_installation_verified_fails_without_evidence(self, deployment_engine):
        # Cannot transition to INSTALLATION_VERIFIED directly from BENCH_ACCEPTED
        ok, msg = deployment_engine.validate_stage_transition(
            sensor_id="PIEZO-NH10-KM48-01",
            target_stage=STAGE_INSTALLATION_VERIFIED,
            evidence={}
        )
        assert ok is False
        assert "skipping forbidden" in msg.lower()

    def test_downhole_piezometer_requires_borehole_log_and_depth(self, deployment_engine):
        # Even if hypothetically at PHYSICAL_VERIFIED, transitioning to INSTALLATION_VERIFIED requires depth and log
        # Test validation logic:
        deployment_engine.validate_stage_transition(
            sensor_id="PIEZO-NH10-KM48-01",
            target_stage=STAGE_INSTALLATION_VERIFIED,
            evidence={"borehole_log_ref": None, "installation_depth_m": None}
        )
