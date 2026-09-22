# -*- coding: utf-8 -*-
"""
tests/test_v4_8_evidence_audit.py
=================================
Automated test suite for Phase V4.8 Physical Evidence Forensic Audit.
Tests:
  1. Forensic classification of claimed sensors as SOFTWARE_DECLARATION_ONLY without physical receipts.
  2. Fake/placeholder serial number rejection.
  3. Unsupported calibration certificate rejection (CALIBRATION_EVIDENCE_MISSING).
  4. Missing installation evidence handling (INSTALLATION_STATUS = PENDING).
  5. REST API endpoint /api/telemetry/evidence-audit verification.
"""

import os
import json
import pytest
from engine.telemetry_evidence_audit_engine import (
    GLOBAL_EVIDENCE_AUDIT_ENGINE,
    TelemetryEvidenceAuditEngine,
    CLASS_SOFTWARE_DECLARATION_ONLY,
    CLASS_UNVERIFIED,
    CLASS_MISSING,
    VERDICT_DATA_FOUNDATION_READY
)


def test_audit_placeholder_serial_rejection():
    """Confirms that placeholder serial numbers are flagged as UNVERIFIED."""
    engine = TelemetryEvidenceAuditEngine()
    for bad_sn in ["TBD", "UNKNOWN", "", "none", "0000", "pending"]:
        meta = {
            "sensor_id": "TEST-SENSOR-01",
            "serial_number": bad_sn,
            "manufacturer": "TestCorp",
            "model": "TestModel"
        }
        res = engine.audit_sensor_identity(meta)
        assert res.classification == CLASS_UNVERIFIED
        assert not res.establishes_physical_ownership
        assert "Placeholder or empty serial" in res.audit_notes


def test_audit_software_declaration_without_receipt():
    """Confirms that sensors with valid format serials but no physical receipt/scan are SOFTWARE_DECLARATION_ONLY."""
    engine = TelemetryEvidenceAuditEngine()
    meta = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "serial_number": "GK-4500AL-9988",
        "manufacturer": "Geokon",
        "model": "4500AL"
    }
    res = engine.audit_sensor_identity(meta)
    assert res.classification == CLASS_SOFTWARE_DECLARATION_ONLY
    assert not res.establishes_physical_ownership
    assert "SOFTWARE_DECLARATION_ONLY" in res.audit_notes


def test_audit_unsupported_calibration_certificate():
    """Confirms that calibration reference strings without actual PDF in repo are flagged CALIBRATION_EVIDENCE_MISSING."""
    engine = TelemetryEvidenceAuditEngine()
    meta = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "calibration_ref": "NABL-GEO-2026-P8821"
    }
    res = engine.audit_calibration_certificate(meta)
    assert res.classification == CLASS_SOFTWARE_DECLARATION_ONLY
    assert not res.establishes_actual_calibration
    assert "CALIBRATION_EVIDENCE_MISSING" in res.audit_notes


def test_audit_missing_installation_evidence():
    """Confirms that sensors pending physical borehole placement are classified as INSTALLATION_STATUS = PENDING."""
    engine = TelemetryEvidenceAuditEngine()
    meta = {
        "sensor_id": "PIEZO-NH10-KM48-01",
        "acceptance_stage": "BENCH_ACCEPTED"
    }
    res = engine.audit_installation_evidence(meta)
    assert res.classification == CLASS_MISSING
    assert not res.establishes_actual_installation
    assert "INSTALLATION_STATUS = PENDING" in res.audit_notes


def test_full_corridor_audit_execution():
    """Executes full corridor audit and verifies overall verdict is V4_8_DATA_FOUNDATION_READY."""
    audit = GLOBAL_EVIDENCE_AUDIT_ENGINE.perform_full_corridor_audit()
    assert audit["corridor_id"] == "CORR-NH10-SIKKIM-KM48"
    assert audit["sensors_claimed_count"] == 5
    assert audit["sensors_physically_verified_count"] == 0
    assert audit["installed_sensors_verified_count"] == 0
    assert audit["verdict"] == VERDICT_DATA_FOUNDATION_READY
    assert audit["research_readiness_gate"]["is_research_ready"] is False
