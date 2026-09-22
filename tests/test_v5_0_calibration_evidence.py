# -*- coding: utf-8 -*-
"""
tests/test_v5_0_calibration_evidence.py
=======================================
Phase V5.0 Test Suite: Laboratory Calibration Evidence & Metrological Traceability
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    CAL_MISSING
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestCalibrationEvidence:
    """Verifies that calibration claims require external signed certificates."""

    def test_all_five_nodes_flag_missing_calibration_evidence(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.calibration_cert_found is False
            assert record.calibration_cert_hash is None
            assert record.calibration_status == CAL_MISSING

    def test_declared_strings_do_not_substitute_for_certificates(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        piezo = audits["PIEZO-NH10-KM48-01"]
        # Declared calibration string exists in registry metadata, but cert on disk is missing
        assert piezo.calibration_status == CAL_MISSING
        assert "CALIBRATION_EVIDENCE_MISSING" in piezo.audit_notes

    def test_calibration_status_in_overall_verdict(self, deployment_engine):
        v = deployment_engine.evaluate_v5_0_overall_verdict()
        assert v["calibration_status"] == CAL_MISSING
