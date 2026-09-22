# -*- coding: utf-8 -*-
"""
tests/test_v4_7_commissioning.py
================================
Phase V4.7 Test Suite: Sensor Acceptance Lifecycle & Commissioning Gating
"""

import os
import json
import pytest

from engine.sensor_acceptance_engine import (
    SensorAcceptanceEngine,
    STATE_PLANNED,
    STATE_RECEIVED,
    STATE_IDENTIFIED,
    STATE_CALIBRATED,
    STATE_BENCH_ACCEPTED,
    STATE_INSTALLED,
    STATE_CONNECTED,
    STATE_TELEMETRY_VALIDATED,
    STATE_FIELD_COMMISSIONED,
    STATE_MONITORING,
    STATE_UNVERIFIED_IDENTITY,
    STATE_DECOMMISSIONED
)


@pytest.fixture
def acceptance_engine(tmp_path):
    """Provides an isolated SensorAcceptanceEngine instance with temporary persistence."""
    p_file = str(tmp_path / "test_acceptance_ledger.json")
    engine = SensorAcceptanceEngine(persistence_path=p_file)
    return engine


class TestSensorIdentityGating:
    """Tests hardware identity verification and serial number enforcement."""

    def test_valid_serial_number_verification(self, acceptance_engine):
        success, msg, ident = acceptance_engine.verify_and_set_identity(
            sensor_id="PIEZO-TEST-01",
            manufacturer="Geokon LLC",
            model="4500AL",
            serial_number="GK-4500AL-9988",
            hardware_revision="REV-B",
            firmware_version="v2.1.0",
            sensor_type="PIEZOMETER"
        )
        assert success is True
        assert ident.identity_verified is True
        assert ident.serial_number == "GK-4500AL-9988"

    @pytest.mark.parametrize("bad_serial", ["", "TBD", "UNKNOWN", "none", "0000", "n/a", "pending"])
    def test_placeholder_serial_sets_unverified_identity(self, acceptance_engine, bad_serial):
        success, msg, ident = acceptance_engine.verify_and_set_identity(
            sensor_id="PIEZO-BAD-01",
            manufacturer="Generic",
            model="Model-X",
            serial_number=bad_serial,
            hardware_revision="REV-A",
            firmware_version="v1.0.0",
            sensor_type="PIEZOMETER"
        )
        assert success is False
        assert ident.identity_verified is False
        assert acceptance_engine.get_sensor_state("PIEZO-BAD-01") == STATE_UNVERIFIED_IDENTITY


class TestLifecycleTransitions:
    """Tests 10-stage lifecycle progression and evidence gating."""

    def test_initial_state_is_planned(self, acceptance_engine):
        state = acceptance_engine.register_planned_sensor("INCL-TEST-01")
        assert state == STATE_PLANNED

    def test_reject_illegal_stage_jump(self, acceptance_engine):
        acceptance_engine.register_planned_sensor("TILT-TEST-01")
        # Attempt to jump from PLANNED directly to FIELD_COMMISSIONED
        success, msg, trans = acceptance_engine.execute_transition(
            sensor_id="TILT-TEST-01",
            target_state=STATE_FIELD_COMMISSIONED,
            operator="RogueOperator",
            evidence_reference="NONE",
            reason="Shortcut attempt"
        )
        assert success is False
        assert "Illegal transition jump" in msg
        assert acceptance_engine.get_sensor_state("TILT-TEST-01") == STATE_PLANNED

    def test_progressive_acceptance_flow(self, acceptance_engine):
        s_id = "RAIN-TEST-01"
        acceptance_engine.register_planned_sensor(s_id)

        # 1. PLANNED -> RECEIVED
        s1, m1, t1 = acceptance_engine.execute_transition(
            sensor_id=s_id, target_state=STATE_RECEIVED, operator="LogisticsOfficer",
            evidence_reference="DOC-DELIVERY-RECEIPT-2026-01", reason="Physical unit received at Rangpo warehouse"
        )
        assert s1 is True
        assert acceptance_engine.get_sensor_state(s_id) == STATE_RECEIVED

        # 2. Set valid identity -> RECEIVED to IDENTIFIED
        acceptance_engine.verify_and_set_identity(
            sensor_id=s_id, manufacturer="Texas Electronics", model="TR-525M",
            serial_number="TE-9921", hardware_revision="REV-A", firmware_version="v1.0",
            sensor_type="RAIN_GAUGE"
        )
        s2, m2, t2 = acceptance_engine.execute_transition(
            sensor_id=s_id, target_state=STATE_IDENTIFIED, operator="QA_Tech",
            evidence_reference="BARCODE_SCAN_TE9921", reason="Serial number verified"
        )
        assert s2 is True

        # 3. IDENTIFIED -> CALIBRATED
        s3, m3, t3 = acceptance_engine.execute_transition(
            sensor_id=s_id, target_state=STATE_CALIBRATED, operator="MetrologyEng",
            evidence_reference="NABL_CERT_TE9921", reason="Factory cal valid",
            calibration_reference="CERT-NABL-2026-9921"
        )
        assert s3 is True

        # 4. CALIBRATED -> BENCH_ACCEPTED
        s4, m4, t4 = acceptance_engine.execute_transition(
            sensor_id=s_id, target_state=STATE_BENCH_ACCEPTED, operator="HIL_Tester",
            evidence_reference="BENCH_HIL_LOG_RUN48", reason="18-byte LoRa frame passed bench testing"
        )
        assert s4 is True
        assert acceptance_engine.get_sensor_state(s_id) == STATE_BENCH_ACCEPTED

    def test_software_only_commissioning_strictly_rejected(self, acceptance_engine):
        s_id = "PIEZO-FIELD-01"
        acceptance_engine.register_planned_sensor(s_id)
        # Advance to TELEMETRY_VALIDATED directly for test setup
        acceptance_engine._states[s_id] = STATE_TELEMETRY_VALIDATED

        # Try to commission without authorized human token
        success, msg, trans = acceptance_engine.execute_transition(
            sensor_id=s_id, target_state=STATE_FIELD_COMMISSIONED, operator="ScriptAgent",
            evidence_reference="HIL_RESULT", reason="Automated attempt",
            authorization_token="INVALID_OR_MISSING"
        )
        assert success is False
        assert "Software-only commissioning is prohibited" in msg


class TestCommissioningAPIs:
    """Tests Flask client commissioning endpoints."""

    @pytest.fixture
    def client(self):
        import app
        return app.app.test_client()

    def test_commissioning_detail_api(self, client):
        res = client.get("/api/telemetry/commissioning/PIEZO-NH10-KM48-01")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "acceptance_state" in data
        assert "identity" in data

    def test_commission_post_rejection_without_evidence(self, client):
        res = client.post("/api/telemetry/commission", json={
            "sensor_id": "PIEZO-NH10-KM48-01",
            "target_state": "FIELD_COMMISSIONED",
            "operator": "UNAUTHORIZED_BOT",
            "reason": "Test premature"
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["status"] == "REJECTED"
