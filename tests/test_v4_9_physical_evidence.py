# -*- coding: utf-8 -*-
"""
tests/test_v4_9_physical_evidence.py
====================================
Phase V4.9 Test Suite: Physical Sensor Evidence Audit & Categorization
"""

import pytest
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    EVID_SOFTWARE_DECLARATION,
    EVID_MISSING,
    EVID_BENCH_ONLY,
    STATUS_NOT_INSTALLED
)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestPhysicalSensorEvidence:
    """Verifies unsparing audit of physical sensor evidence for the 5 corridor nodes."""

    def test_five_corridor_nodes_audited(self, commissioning_engine):
        audits = commissioning_engine.audit_physical_sensor_evidence()
        assert len(audits) == 5
        expected_ids = {
            "PIEZO-NH10-KM48-01",
            "INCL-NH10-KM48-01",
            "TILT-NH10-KM48-01",
            "RAIN-NH10-KM48-01",
            "GW-NH10-KM48-01"
        }
        assert set(audits.keys()) == expected_ids

    def test_registry_declarations_not_confused_with_physical_evidence(self, commissioning_engine):
        audits = commissioning_engine.audit_physical_sensor_evidence()
        for s_id, audit in audits.items():
            assert audit.physical_device_evidence == EVID_SOFTWARE_DECLARATION
            assert audit.serial_number_evidence == EVID_SOFTWARE_DECLARATION
            assert audit.manufacturer_evidence == EVID_SOFTWARE_DECLARATION
            assert audit.model_evidence == EVID_SOFTWARE_DECLARATION

    def test_missing_installation_and_calibration_evidence_flagged(self, commissioning_engine):
        audits = commissioning_engine.audit_physical_sensor_evidence()
        for s_id, audit in audits.items():
            assert audit.installation_evidence == EVID_MISSING
            assert audit.calibration_evidence == EVID_MISSING
            assert audit.installation_status == STATUS_NOT_INSTALLED

    def test_hardware_identity_unverified_without_external_proof(self, commissioning_engine):
        audits = commissioning_engine.audit_physical_sensor_evidence()
        for s_id, audit in audits.items():
            assert audit.hardware_identity_status == "UNVERIFIED_IDENTITY"
            assert "UNVERIFIED" in audit.hardware_identity_status

    def test_telemetry_classified_as_bench_only_not_live(self, commissioning_engine):
        audits = commissioning_engine.audit_physical_sensor_evidence()
        for s_id, audit in audits.items():
            assert audit.telemetry_evidence == EVID_BENCH_ONLY
            assert audit.telemetry_status == "PHYSICAL_TELEMETRY_PENDING"
