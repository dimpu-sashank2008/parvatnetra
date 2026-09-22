# -*- coding: utf-8 -*-
"""
tests/test_v4_9_installation.py
===============================
Phase V4.9 Test Suite: Physical Installation Verification & Downhole Gating
"""

import pytest
from engine.sensor_acceptance_engine import (
    SensorAcceptanceEngine,
    STATE_PLANNED,
    STATE_RECEIVED,
    STATE_IDENTITY_VERIFIED,
    STATE_CALIBRATION_VERIFIED,
    STATE_BENCH_ACCEPTED,
    STATE_FIELD_PRESENCE_VERIFIED,
    STATE_INSTALLED
)
from engine.field_commissioning_engine import (
    FieldCommissioningEngine,
    STATUS_NOT_INSTALLED
)


@pytest.fixture
def acceptance_engine(tmp_path):
    p_file = str(tmp_path / "test_install_ledger.json")
    return SensorAcceptanceEngine(persistence_path=p_file)


class TestInstallationVerification:
    """Verifies physical downhole drilling and mounting installation gating."""

    def test_planned_nodes_remain_not_installed_by_default(self):
        eng = FieldCommissioningEngine()
        audits = eng.audit_physical_sensor_evidence()
        for s_id, audit in audits.items():
            assert audit.installation_status == STATUS_NOT_INSTALLED

    def test_installation_requires_gps_and_casing_depth(self, acceptance_engine):
        s_id = "PIEZO-INSTALL-TEST"
        acceptance_engine.register_planned_sensor(s_id)
        acceptance_engine._states[s_id] = STATE_FIELD_PRESENCE_VERIFIED

        # Attempt to transition to INSTALLED without coordinates and depth
        success, msg, trans = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_INSTALLED,
            operator="FieldTech",
            evidence_reference="DOC-BOREHOLE-01",
            reason="Downhole casing completed",
            metadata={}  # Missing latitude, longitude, installation_depth
        )
        assert success is False
        assert "requires physical installation evidence" in msg

    def test_successful_installation_with_verified_physical_metadata(self, acceptance_engine):
        s_id = "INCL-INSTALL-TEST"
        acceptance_engine.register_planned_sensor(s_id)
        acceptance_engine._states[s_id] = STATE_FIELD_PRESENCE_VERIFIED

        success, msg, trans = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_INSTALLED,
            operator="BoreholeSurveyor",
            evidence_reference="DOC-BOREHOLE-LOG-KM48-BH02",
            reason="Grooved inclinometer casing installed and grouted to 15m depth",
            metadata={
                "latitude": 27.20231,
                "longitude": 88.51472,
                "installation_depth": 15.0,
                "casing_type": "ABS_GROOVED_70MM"
            }
        )
        assert success is True
        assert acceptance_engine.get_sensor_state(s_id) == STATE_INSTALLED
