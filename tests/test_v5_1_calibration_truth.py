# -*- coding: utf-8 -*-
"""
tests/test_v5_1_calibration_truth.py
====================================
Phase V5.1 Test Suite: Calibration Truth & Metrological Audit
Verifies that calibration evidence is honest and zero fake certificates exist.
"""

import os
import glob
import pytest
from engine.scientific_truth_engine import ScientificTruthEngine


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestV51CalibrationTruth:
    """Verifies calibration records and absent laboratory certificate reality."""

    def test_calibration_evidence_missing_status(self, truth_engine):
        cal = truth_engine.get_calibration_truth()
        assert cal.get("overall_calibration_status") == "CALIBRATION_EVIDENCE_MISSING"
        assert cal.get("calibration_verified_count") == 0
        assert cal.get("calibration_missing_count") >= 5

    def test_zero_signed_certificates_on_disk(self, truth_engine):
        base_dir = truth_engine.base_dir
        cert_pattern = os.path.join(base_dir, "field_evidence", "certificates", "*.pdf")
        certs = glob.glob(cert_pattern)
        assert len(certs) == 0, f"Found unexpected signed certificate files: {certs}"

    def test_calibration_note_discloses_limitations(self, truth_engine):
        cal = truth_engine.get_calibration_truth()
        note = cal.get("note", "")
        assert "NABL" in note or "ISO-17025" in note or "certificates" in note
