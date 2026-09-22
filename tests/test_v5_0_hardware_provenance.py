# -*- coding: utf-8 -*-
"""
tests/test_v5_0_hardware_provenance.py
======================================
Phase V5.0 Test Suite: Physical Hardware Provenance Acquisition & Device Identity Audit
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    STAGE_BENCH_ACCEPTED
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestHardwareProvenance:
    """Verifies that physical sensor evidence is audited across all 9 dimensions."""

    def test_five_corridor_nodes_present_in_audit(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        assert len(audits) == 5
        expected_ids = {
            "PIEZO-NH10-KM48-01",
            "INCL-NH10-KM48-01",
            "TILT-NH10-KM48-01",
            "RAIN-NH10-KM48-01",
            "GW-NH10-KM48-01"
        }
        assert set(audits.keys()) == expected_ids

    def test_nameplate_photos_missing_on_disk(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.nameplate_photo_found is False
            assert record.nameplate_photo_path is None
            assert record.nameplate_photo_hash is None

    def test_delivery_challans_and_invoices_missing(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.delivery_challan_found is False
            assert record.delivery_challan_ref is None

    def test_physical_device_verification_status_is_false(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.device_physically_verified is False
            assert record.hardware_identity_status == "UNVERIFIED_IDENTITY"

    def test_current_matrix_stage_is_bench_accepted(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.current_stage == STAGE_BENCH_ACCEPTED
            assert record.telemetry_status == "PHYSICAL_TELEMETRY_PENDING"
