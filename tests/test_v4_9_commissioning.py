# -*- coding: utf-8 -*-
"""
tests/test_v4_9_commissioning.py
================================
Phase V4.9 Test Suite: 11-Stage Field Commissioning State Machine & Lifecycle Governance
"""

import pytest
from engine.sensor_acceptance_engine import (
    SensorAcceptanceEngine,
    STATE_PLANNED,
    STATE_RECEIVED,
    STATE_IDENTITY_VERIFIED,
    STATE_IDENTIFIED,
    STATE_CALIBRATION_VERIFIED,
    STATE_CALIBRATED,
    STATE_BENCH_ACCEPTED,
    STATE_FIELD_PRESENCE_VERIFIED,
    STATE_INSTALLED,
    STATE_CONNECTED,
    STATE_TELEMETRY_VALIDATED,
    STATE_FIELD_COMMISSIONED,
    STATE_MONITORING,
    CANONICAL_LIFECYCLE_STAGES
)


@pytest.fixture
def acceptance_engine(tmp_path):
    p_file = str(tmp_path / "test_comm_ledger.json")
    return SensorAcceptanceEngine(persistence_path=p_file)


class Test11StageLifecycleProgression:
    """Tests complete 11-stage field commissioning progression."""

    def test_canonical_11_stages_declared(self):
        assert len(CANONICAL_LIFECYCLE_STAGES) == 11
        expected = [
            "PLANNED",
            "RECEIVED",
            "IDENTITY_VERIFIED",
            "CALIBRATION_VERIFIED",
            "BENCH_ACCEPTED",
            "FIELD_PRESENCE_VERIFIED",
            "INSTALLED",
            "CONNECTED",
            "TELEMETRY_VALIDATED",
            "FIELD_COMMISSIONED",
            "MONITORING"
        ]
        assert CANONICAL_LIFECYCLE_STAGES == expected

    def test_progressive_11_stage_lifecycle_flow(self, acceptance_engine):
        s_id = "TILT-TEST-11STAGE"
        acceptance_engine.register_planned_sensor(s_id)

        # 1. PLANNED -> RECEIVED
        s1, m1, t1 = acceptance_engine.execute_transition(
            s_id, STATE_RECEIVED, "LogisticsLead", "WAYBILL-2026-09", "Delivered to Singtam staging"
        )
        assert s1 is True

        # 2. RECEIVED -> IDENTITY_VERIFIED
        acceptance_engine.verify_and_set_identity(
            sensor_id=s_id, manufacturer="PARVAT Metrology", model="Tilt-200",
            serial_number="PN-TILT-2026-0991", hardware_revision="REV-B", firmware_version="v1.0",
            sensor_type="TILTMETER"
        )
        s2, m2, t2 = acceptance_engine.execute_transition(
            s_id, STATE_IDENTITY_VERIFIED, "QATech", "BARCODE-0991", "Serial confirmed"
        )
        assert s2 is True

        # 3. IDENTITY_VERIFIED -> CALIBRATION_VERIFIED
        s3, m3, t3 = acceptance_engine.execute_transition(
            s_id, STATE_CALIBRATION_VERIFIED, "MetrologyEng", "NABL-DOC-0991", "2-axis zero calibration certified",
            calibration_reference="CERT-NABL-TILT-0991"
        )
        assert s3 is True

        # 4. CALIBRATION_VERIFIED -> BENCH_ACCEPTED
        s4, m4, t4 = acceptance_engine.execute_transition(
            s_id, STATE_BENCH_ACCEPTED, "LabTech", "BENCH_HIL_LOG_RUN48", "Passed 72h continuous bench HIL test"
        )
        assert s4 is True

        # 5. BENCH_ACCEPTED -> FIELD_PRESENCE_VERIFIED
        s5, m5, t5 = acceptance_engine.execute_transition(
            s_id, STATE_FIELD_PRESENCE_VERIFIED, "FieldSurveyor", "FIELD_PRESENCE_GPS_SURVEY",
            "Physical device transported to NH-10 KM48 bedrock anchor site"
        )
        assert s5 is True

        # 6. FIELD_PRESENCE_VERIFIED -> INSTALLED
        s6, m6, t6 = acceptance_engine.execute_transition(
            s_id, STATE_INSTALLED, "CivilEngineer", "ANCHOR_INSTALL_REPORT", "Anchored to bedrock with epoxy studs",
            metadata={"latitude": 27.2023, "longitude": 88.5147, "mount": "Bedrock bracket"}
        )
        assert s6 is True

        # 7. INSTALLED -> CONNECTED
        s7, m7, t7 = acceptance_engine.execute_transition(
            s_id, STATE_CONNECTED, "RfEngineer", "RF_LORA_JOIN_ACCEPT", "LoRaWAN OTAA join confirmed",
            gateway_id="GW-NH10-KM48-01"
        )
        assert s7 is True

        # 8. CONNECTED -> TELEMETRY_VALIDATED
        for _ in range(12):
            acceptance_engine.record_telemetry_observation(s_id, True)

        s8, m8, t8 = acceptance_engine.execute_transition(
            s_id, STATE_TELEMETRY_VALIDATED, "SystemObserver", "CONSECUTIVE_OBSERVATIONS_LOG",
            "12 consecutive valid packets ingested"
        )
        assert s8 is True

    def test_legacy_aliases_identified_and_calibrated_compatible(self, acceptance_engine):
        s_id = "LEGACY-TEST-01"
        acceptance_engine.register_planned_sensor(s_id)
        acceptance_engine._states[s_id] = STATE_RECEIVED

        acceptance_engine.verify_and_set_identity(
            sensor_id=s_id, manufacturer="Geokon", model="4500", serial_number="GK-9911",
            hardware_revision="A", firmware_version="1", sensor_type="PIEZOMETER"
        )
        # Using legacy IDENTIFIED
        s_id_trans, _, _ = acceptance_engine.execute_transition(
            s_id, STATE_IDENTIFIED, "Op", "REF", "Reason"
        )
        assert s_id_trans is True

        # Using legacy CALIBRATED
        s_cal_trans, _, _ = acceptance_engine.execute_transition(
            s_id, STATE_CALIBRATED, "Op", "REF", "Reason", calibration_reference="CAL-1"
        )
        assert s_cal_trans is True
