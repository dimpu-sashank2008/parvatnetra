# -*- coding: utf-8 -*-
"""
tests/test_v5_0_calibration_forensics.py
========================================
Phase V5.0 Test Suite: Metrological Traceability & Calibration Forensics
"""

import os
import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    CAL_MISSING,
    CAL_VERIFIED,
    compute_sha256_bytes
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestCalibrationForensics:
    """Forensic audit of calibration certificates and laboratory traceability."""

    def test_all_five_corridor_nodes_cal_cert_missing(self, deployment_engine):
        audits = deployment_engine.audit_sensor_hardware_provenance()
        for s_id, record in audits.items():
            assert record.calibration_cert_found is False
            assert record.calibration_cert_hash is None
            assert record.calibration_status == CAL_MISSING

    def test_nabl_reference_string_does_not_infer_certification(self, deployment_engine):
        # Even if registry contains 'NABL-CAL-GK-2026-0812', cert is missing
        audits = deployment_engine.audit_sensor_hardware_provenance()
        piezo = audits["PIEZO-NH10-KM48-01"]
        assert piezo.calibration_status == CAL_MISSING
        assert "CALIBRATION_EVIDENCE_MISSING" in piezo.audit_notes

    def test_mock_cert_hash_verification(self, tmp_path, deployment_engine):
        # Test that an actual certificate PDF must match SHA-256
        cert_content = b"%PDF-1.4 Mock ISO/IEC 17025 Geokon Calibration Certificate"
        cert_hash = compute_sha256_bytes(cert_content)
        cert_file = tmp_path / "CAL_PIEZO_GK_2026.pdf"
        cert_file.write_bytes(cert_content)

        # Hash matches byte content
        assert cert_hash == compute_sha256_bytes(cert_file.read_bytes())
        assert len(cert_hash) == 64

    def test_unaccredited_self_declaration_rejected(self, deployment_engine):
        claims_audit = deployment_engine.audit_authority_and_claims()
        nabl_claim = next((c for c in claims_audit["claims"] if "NABL" in c["term"]), None)
        assert nabl_claim is not None
        assert nabl_claim["classification"] == "UNSUPPORTED"
        assert "CALIBRATION_EVIDENCE_MISSING" in nabl_claim["remedy"]
