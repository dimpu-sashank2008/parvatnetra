# -*- coding: utf-8 -*-
"""
tests/test_v4_9_calibration.py
==============================
Phase V4.9 Test Suite: Calibration Evidence & Traceability Verification
"""

import os
import pytest
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    CAL_MISSING,
    CAL_VERIFIED,
    compute_file_sha256
)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestCalibrationTraceability:
    """Tests laboratory calibration certificate audit and traceability enforcement."""

    def test_missing_physical_certificates_flagged(self, commissioning_engine):
        res = commissioning_engine.audit_calibration_traceability()
        assert res["total_calibration_claims"] == 5
        assert res["verified_certificates_count"] == 0
        assert res["missing_certificates_count"] == 5
        assert res["overall_calibration_status"] == CAL_MISSING

    def test_calibration_ref_strings_do_not_infer_nabl_certification(self, commissioning_engine):
        res = commissioning_engine.audit_calibration_traceability()
        for record in res["traceability_ledger"]:
            assert record["verification_status"] == CAL_MISSING
            assert record["certificate_filename"] is None
            assert record["certificate_hash"] is None
            assert record["traceability_standard"] == "UNVERIFIED"

    def test_file_hash_computed_accurately_for_genuine_file(self, tmp_path):
        sample_cert = tmp_path / "iso17025_cert.pdf"
        sample_content = b"%PDF-1.4 ACCREDITED LABORATORY CERTIFICATE"
        sample_cert.write_bytes(sample_content)

        h = compute_file_sha256(str(sample_cert))
        assert h is not None
        assert len(h) == 64

    def test_nonexistent_file_returns_none_hash(self):
        h = compute_file_sha256("/nonexistent/path/to/cert.pdf")
        assert h is None
