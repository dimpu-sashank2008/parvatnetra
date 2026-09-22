# -*- coding: utf-8 -*-
"""
tests/test_v4_9_field_installation.py
=====================================
Phase V4.9 Test Suite: Physical Field Installation & Hardware Identity Governance
Validates:
- Item 1: Installation state gating (planned vs installed, downhole casing)
- Item 2: Serial identity verification (nameplates and serial forensics)
- Item 3: Calibration linkage (NABL accredited certificate verification)
"""

import pytest
from engine.sensor_acceptance_engine import (
    SensorAcceptanceEngine,
    STATE_PLANNED,
    STATE_FIELD_PRESENCE_VERIFIED,
    STATE_INSTALLED,
    STATE_IDENTITY_VERIFIED,
    STATE_CALIBRATION_VERIFIED
)
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    STATUS_NOT_INSTALLED,
    STATUS_PLANNED,
    CAL_MISSING,
    EVID_UNVERIFIED
)


@pytest.fixture
def acceptance_engine(tmp_path):
    p_file = str(tmp_path / "test_field_install_ledger.json")
    return SensorAcceptanceEngine(persistence_path=p_file)


@pytest.fixture
def commissioning_engine():
    return FieldCommissioningEngine()


class TestFieldInstallation:
    """Verifies physical downhole and surface sensor installation requirements."""

    def test_item_1_installation_state_default_not_installed(self, commissioning_engine):
        """Item 1: Verify all planned corridor nodes remain NOT_INSTALLED by default."""
        audits = commissioning_engine.audit_physical_sensor_evidence()
        assert len(audits) == 5
        for sensor_id, audit in audits.items():
            assert audit.installation_status == STATUS_NOT_INSTALLED
            assert audit.physical_device_verified is False

    def test_item_1_downhole_installation_requires_casing_depth_and_coordinates(self, acceptance_engine):
        """Item 1: Downhole borehole sensors require ABS grooved casing depth, grouting and GPS."""
        piezo_id = "PIEZO-NH10-KM48-01"
        acceptance_engine.register_planned_sensor(piezo_id)
        acceptance_engine._states[piezo_id] = STATE_FIELD_PRESENCE_VERIFIED

        # Attempt to transition without casing depth metadata
        success, msg, _ = acceptance_engine.execute_transition(
            sensor_id=piezo_id,
            target_state=STATE_INSTALLED,
            operator="FieldTech",
            evidence_reference="BH-DRILL-REPORT-01",
            reason="Drilling completed",
            metadata={"latitude": 27.2023}  # Missing depth and longitude
        )
        assert success is False
        assert "requires physical installation evidence" in msg

        # Proper metadata transitions successfully
        success_ok, _, _ = acceptance_engine.execute_transition(
            sensor_id=piezo_id,
            target_state=STATE_INSTALLED,
            operator="BoreholeDriller",
            evidence_reference="DOC-BOREHOLE-LOG-KM48-BH01",
            reason="Piezometer placed in sand intake zone at 18.5m depth with bentonite seal",
            metadata={
                "latitude": 27.20231,
                "longitude": 88.51472,
                "installation_depth": 18.5,
                "casing_type": "PVC_SLOTTED_WITH_SAND_PACK"
            }
        )
        assert success_ok is True
        assert acceptance_engine.get_sensor_state(piezo_id) == STATE_INSTALLED

    def test_item_2_serial_identity_verification(self, commissioning_engine):
        """Item 2: Serial identity remains UNVERIFIED_IDENTITY without physical nameplate photos."""
        audits = commissioning_engine.audit_physical_sensor_evidence()
        for s_id, audit in audits.items():
            # In bench prototype phase, physical photo evidence is pending
            assert audit.hardware_identity_status == "UNVERIFIED_IDENTITY"
            assert audit.hardware_identity_evidence in [EVID_UNVERIFIED, "MISSING", "BENCH_ONLY", "SOFTWARE_DECLARATION"]

    def test_item_3_calibration_linkage(self, commissioning_engine):
        """Item 3: Missing physical accredited calibration certificates flagged as CALIBRATION_EVIDENCE_MISSING."""
        cal_audit = commissioning_engine.audit_calibration_traceability()
        assert cal_audit["overall_calibration_status"] == CAL_MISSING
        assert cal_audit["missing_count"] == 5
        assert cal_audit["verified_count"] == 0
        for rec in cal_audit["traceability_ledger"]:
            assert rec["verification_status"] == CAL_MISSING
            assert rec["certificate_hash"] is None
