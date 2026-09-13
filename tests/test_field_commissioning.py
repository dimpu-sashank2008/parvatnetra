# -*- coding: utf-8 -*-
"""
tests/test_field_commissioning.py
=================================
Unit tests for the 7-step field commissioning workflow, GPS accuracy limits,
photo cryptographic hashing, and technician sign-off evidence.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.field_evidence_service import (
    FieldEvidenceService,
    FieldEvidenceRecord,
    FIELD_STAGES
)


@pytest.fixture
def temp_evidence_service(tmp_path):
    db_file = str(tmp_path / "test_evidence.db")
    return FieldEvidenceService(db_path=db_file)


def test_field_stages_authoritative_sequence():
    assert FIELD_STAGES == [
        "REGISTER",
        "LOCATE",
        "INSTALL",
        "CALIBRATE",
        "CONNECT",
        "TEST",
        "ACCEPT"
    ]


def test_record_locate_stage_with_valid_gps(temp_evidence_service):
    rec = FieldEvidenceRecord(
        evidence_id="EV-LOC-001",
        device_id="SN-PIEZ-TEST-01",
        stage="LOCATE",
        technician_name="T. Lepcha",
        gps_coords={"latitude": 27.3300, "longitude": 88.6100, "elevation_m": 680.0, "accuracy_m": 4.5},
        notes="GPS fix obtained with survey-grade DGPS"
    )
    saved = temp_evidence_service.record_stage_evidence(rec)
    assert saved.evidence_id == "EV-LOC-001"
    assert len(saved.signature_hash) == 64  # SHA-256


def test_reject_inaccurate_gps(temp_evidence_service):
    rec = FieldEvidenceRecord(
        evidence_id="EV-LOC-BAD",
        device_id="SN-PIEZ-TEST-01",
        stage="LOCATE",
        technician_name="T. Lepcha",
        gps_coords={"latitude": 27.3300, "longitude": 88.6100, "accuracy_m": 45.0},
        notes="Poor GPS lock in dense canopy"
    )
    with pytest.raises(ValueError) as excinfo:
        temp_evidence_service.record_stage_evidence(rec)
    assert "GPS accuracy too poor" in str(excinfo.value)


def test_install_stage_requires_photo_evidence(temp_evidence_service):
    rec = FieldEvidenceRecord(
        evidence_id="EV-INST-001",
        device_id="SN-PIEZ-TEST-01",
        stage="INSTALL",
        technician_name="T. Lepcha",
        gps_coords={"accuracy_m": 5.0},
        photo_hashes=[]  # Missing photo hashes
    )
    with pytest.raises(ValueError) as excinfo:
        temp_evidence_service.record_stage_evidence(rec)
    assert "INSTALL stage requires at least one photograph" in str(excinfo.value)


def test_calibrate_stage_requires_certificate(temp_evidence_service):
    rec = FieldEvidenceRecord(
        evidence_id="EV-CAL-001",
        device_id="SN-PIEZ-TEST-01",
        stage="CALIBRATE",
        technician_name="Metrology Eng",
        gps_coords={"accuracy_m": 5.0},
        photo_hashes=["sha256_mock_photo"],
        calibration_cert_id=None
    )
    with pytest.raises(ValueError) as excinfo:
        temp_evidence_service.record_stage_evidence(rec)
    assert "CALIBRATE stage requires valid calibration_cert_id" in str(excinfo.value)


def test_connect_stage_requires_rssi_and_gateway(temp_evidence_service):
    rec = FieldEvidenceRecord(
        evidence_id="EV-CONN-001",
        device_id="SN-PIEZ-TEST-01",
        stage="CONNECT",
        technician_name="Comms Eng",
        gps_coords={"accuracy_m": 5.0},
        gateway_id="GW-01",
        measured_rssi=None  # Missing RSSI
    )
    with pytest.raises(ValueError) as excinfo:
        temp_evidence_service.record_stage_evidence(rec)
    assert "CONNECT stage requires measured_rssi" in str(excinfo.value)


def test_complete_device_evidence_history(temp_evidence_service):
    # Step 1: Register
    temp_evidence_service.record_stage_evidence(FieldEvidenceRecord(
        evidence_id="EV-01", device_id="SN-PIEZ-99", stage="REGISTER", technician_name="Tech A",
        gps_coords={"accuracy_m": 5.0}
    ))
    # Step 2: Locate
    temp_evidence_service.record_stage_evidence(FieldEvidenceRecord(
        evidence_id="EV-02", device_id="SN-PIEZ-99", stage="LOCATE", technician_name="Tech A",
        gps_coords={"latitude": 27.33, "longitude": 88.61, "accuracy_m": 3.0}
    ))
    # Step 3: Install
    temp_evidence_service.record_stage_evidence(FieldEvidenceRecord(
        evidence_id="EV-03", device_id="SN-PIEZ-99", stage="INSTALL", technician_name="Tech A",
        gps_coords={"accuracy_m": 3.0}, photo_hashes=["c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2"]
    ))

    history = temp_evidence_service.get_device_evidence("SN-PIEZ-99")
    assert len(history) == 3
    assert [h.stage for h in history] == ["REGISTER", "LOCATE", "INSTALL"]
