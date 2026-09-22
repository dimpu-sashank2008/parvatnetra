# -*- coding: utf-8 -*-
"""
tests/test_v5_2_calibration.py
==============================
Phase V5.2 Test Suite: Calibration Evidence Gate
Verifies that calibration references without underlying laboratory certificates
are treated as CALIBRATION_EVIDENCE_MISSING, rejecting certificate IDs alone.
"""

import os
import glob
import pytest
from engine.physical_deployment_engine import (
    GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE,
    CAL_MISSING
)


def test_calibration_evidence_gate_missing_status():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    audits = engine.audit_sensor_hardware_provenance()
    for sensor_id, a in audits.items():
        if a.sensor_type != "GATEWAY":
            assert a.calibration_status == CAL_MISSING, (
                f"Sensor {sensor_id} calibration status must be {CAL_MISSING}, got {a.calibration_status}"
            )
            assert a.calibration_cert_verified is False


def test_certificate_id_alone_insufficient():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    audits = engine.audit_sensor_hardware_provenance()
    piezo = audits.get("PIEZO-NH10-KM48-01") or audits.get("PIEZ-KM48-01")
    assert piezo is not None
    # Certificate reference string may be present in config/manifest, but physical certificate is unverified
    assert piezo.calibration_cert_verified is False


def test_zero_signed_pdf_certificates_on_disk():
    base_dir = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE.base_dir
    cert_pattern = os.path.join(base_dir, "field_evidence", "certificates", "*.pdf")
    certs = glob.glob(cert_pattern)
    assert len(certs) == 0, f"Found unexpected physical certificate files: {certs}"
