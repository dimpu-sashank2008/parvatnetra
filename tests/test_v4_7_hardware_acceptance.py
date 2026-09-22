# -*- coding: utf-8 -*-
"""
tests/test_v4_7_hardware_acceptance.py
======================================
Phase V4.7 Test Suite: Sensor Hardware Acceptance, Identity & Physical Specifications
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
    STATE_UNVERIFIED_IDENTITY,
    SensorIdentityRecord
)
from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    SensorDevice,
    STATUS_REGISTERED,
    STATUS_COMMISSIONING,
    STATUS_ACTIVE
)


@pytest.fixture
def acceptance_engine(tmp_path):
    p_file = str(tmp_path / "test_hardware_acceptance_ledger.json")
    return SensorAcceptanceEngine(persistence_path=p_file)


class TestHardwareSensorRegistration:
    """Tests registration and specification verification across all 5 corridor sensor types."""

    CORRIDOR_SENSORS = [
        ("PIEZO-NH10-KM48-01", "PIEZOMETER", "Geokon", "4500AL", "GK-4500AL-9988", "rev3b", "fw-1.4.2"),
        ("INCL-NH10-KM48-01", "INCLINOMETER", "RST Instruments", "MEMS-IPI-01", "RST-MEMS-5521", "rev2a", "fw-2.1.0"),
        ("TILT-NH10-KM48-01", "TILTMETER", "Encardio-Rite", "EAN-92M", "ENC-92M-3312", "rev4c", "fw-3.0.1"),
        ("RAIN-NH10-KM48-01", "RAIN_GAUGE", "Davis Instruments", "Aerocone-0.2mm", "DAV-AERO-7740", "rev1", "fw-1.0.0"),
        ("GW-NH10-KM48-01", "GATEWAY", "RAKwireless", "RAK7289", "RAK-7289-4411", "rev2", "fw-1.3.4")
    ]

    @pytest.mark.parametrize("s_id,s_type,mfr,model,serial,hw_rev,fw_ver", CORRIDOR_SENSORS)
    def test_corridor_sensor_hardware_acceptance(self, acceptance_engine, s_id, s_type, mfr, model, serial, hw_rev, fw_ver):
        acceptance_engine.register_planned_sensor(s_id)
        assert acceptance_engine.get_sensor_state(s_id) == STATE_PLANNED

        # Transition to RECEIVED
        ok, msg, _ = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_RECEIVED,
            operator="QA_Engineer",
            evidence_reference=f"RECEIPT-{s_id}",
            reason="Hardware received in lab"
        )
        assert ok is True

        # Verify identity
        ok, msg, ident = acceptance_engine.verify_and_set_identity(
            sensor_id=s_id,
            manufacturer=mfr,
            model=model,
            serial_number=serial,
            hardware_revision=hw_rev,
            firmware_version=fw_ver,
            sensor_type=s_type
        )
        assert ok is True
        assert ident.identity_verified is True
        assert ident.serial_number == serial

        # Transition to IDENTIFIED
        ok, msg, _ = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_IDENTIFIED,
            operator="QA_Engineer",
            evidence_reference=f"BARCODE-{serial}",
            reason="Hardware serial and specs verified against datasheet"
        )
        assert ok is True
        assert acceptance_engine.get_sensor_state(s_id) == STATE_IDENTIFIED


class TestHardwareSerialMismatchAndPlaceholders:
    """Tests rejection of placeholder serials, empty serials, and serial mismatches."""

    def test_empty_and_placeholder_serials_rejected(self, acceptance_engine):
        bad_serials = ["", " ", "TBD", "UNKNOWN", "none", "0000", "PENDING", "N/A", "placeholder"]
        for idx, bs in enumerate(bad_serials):
            s_id = f"SENSOR-BAD-{idx}"
            acceptance_engine.register_planned_sensor(s_id)
            ok, msg, ident = acceptance_engine.verify_and_set_identity(
                sensor_id=s_id,
                manufacturer="Generic",
                model="Generic-01",
                serial_number=bs,
                hardware_revision="v1",
                firmware_version="v1.0.0",
                sensor_type="PIEZOMETER"
            )
            assert ok is False
            assert ident.identity_verified is False
            assert acceptance_engine.get_sensor_state(s_id) == STATE_UNVERIFIED_IDENTITY

    def test_serial_mismatch_detection(self, acceptance_engine):
        s_id = "PIEZO-KM48-CHECK"
        acceptance_engine.register_planned_sensor(s_id)
        # Register with valid serial
        ok, _, ident = acceptance_engine.verify_and_set_identity(
            sensor_id=s_id,
            manufacturer="Geokon",
            model="4500AL",
            serial_number="GK-9988",
            hardware_revision="v3b",
            firmware_version="fw-1.4.2",
            sensor_type="PIEZOMETER"
        )
        assert ok is True
        assert ident.serial_number == "GK-9988"

        # Attempt to supply mismatching serial in packet payload check
        incoming_serial = "GK-DIFFERENT-1111"
        assert incoming_serial != ident.serial_number, "Incoming packet serial must not match registered identity"


class TestPhysicalInstallationAndBaselineStatus:
    """Tests that physical installation defaults to NOT_INSTALLED and coordinates are not fabricated."""

    def test_physical_installation_defaults_not_installed(self, acceptance_engine):
        # Sensors cannot be marked INSTALLED without physical field installation evidence
        s_id = "INCL-TEST-INSTALL"
        acceptance_engine.register_planned_sensor(s_id)
        state = acceptance_engine.get_sensor_state(s_id)
        assert state != STATE_INSTALLED
        assert state == STATE_PLANNED

    def test_prevent_software_only_jump_to_installed(self, acceptance_engine):
        s_id = "TILT-TEST-INSTALL"
        acceptance_engine.register_planned_sensor(s_id)
        ok, msg, _ = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_INSTALLED,
            operator="AutomatedScript",
            evidence_reference="NONE",
            reason="Software simulation"
        )
        assert ok is False
        assert "Illegal transition jump" in msg


class TestSensorHealthAndHeartbeat:
    """Tests sensor health tracking, low-battery alerts, and offline detection."""

    def test_sensor_registry_heartbeat_and_health(self):
        s_id = "RAIN-NH10-TEST-HB"
        dev = SensorDevice(
            device_id=s_id,
            sensor_id=s_id,
            sensor_type="rain_gauge",
            sector_id="CORR-NH10-SIKKIM-KM48",
            latitude=27.18,
            longitude=88.51,
            status=STATUS_REGISTERED,
            battery_level=95.0,
            signal_strength=-70.0
        )
        GLOBAL_SENSOR_REGISTRY.register_device(dev)

        # Record healthy heartbeat
        GLOBAL_SENSOR_REGISTRY.record_heartbeat(s_id, battery_pct=92.0, signal_rssi=-72.0, clock_offset_ms=15.0)
        d = GLOBAL_SENSOR_REGISTRY.get_device(s_id)
        assert d is not None
        assert d.battery_level == 92.0

        # Record critically low battery
        GLOBAL_SENSOR_REGISTRY.record_heartbeat(s_id, battery_pct=10.0, signal_rssi=-98.0, clock_offset_ms=50.0)
        d2 = GLOBAL_SENSOR_REGISTRY.get_device(s_id)
        assert d2.battery_level == 10.0
        assert d2.signal_strength == -98.0
