# -*- coding: utf-8 -*-
"""
tests/test_sensor_commissioning_hardware.py
===========================================
Phase 6C Test Suite: Hardware Sensor Commissioning CLI & Calibration Enforcement
"""

import sys
import os
import subprocess
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.sensor_calibration import (
    GLOBAL_CALIBRATION_ENGINE,
    CalibrationRecord,
    STATUS_CALIBRATED,
    STATUS_CALIBRATION_DUE,
    STATUS_INVALID_CALIBRATION
)
from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    STATUS_ACTIVE
)

SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts",
    "commission_sensor.py"
)


class TestHardwareSensorCommissioning:

    def test_commissioning_happy_path_with_technician_and_cert(self):
        result = subprocess.run(
            [
                sys.executable, SCRIPT_PATH,
                "--device-id", "COMM-HW-PZ-01",
                "--sensor-type", "piezometer",
                "--technician", "Er. R. K. Thapa, SDRF Metrologist",
                "--cert-ref", "NABL-CAL-2026-PZ01",
                "--zero-offset", "0.0",
                "--scale-factor", "1.0",
                "--auto"
            ],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "ACCEPTED" in result.stdout
        assert "Digital Certificate" in result.stdout
        assert "Er. R. K. Thapa" in result.stdout

        dev = GLOBAL_SENSOR_REGISTRY.get_device("COMM-HW-PZ-01")
        assert dev is not None
        assert dev.status == STATUS_ACTIVE

    def test_commissioning_rejected_invalid_calibration(self):
        result = subprocess.run(
            [
                sys.executable, SCRIPT_PATH,
                "--device-id", "COMM-HW-FAIL-CAL",
                "--sensor-type", "piezometer",
                "--force-invalid-cal",
                "--auto"
            ],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "REJECTED" in result.stdout
        assert "Calibration validation failed" in result.stdout

    def test_commissioning_rejected_expired_calibration(self):
        result = subprocess.run(
            [
                sys.executable, SCRIPT_PATH,
                "--device-id", "COMM-HW-EXPIRED",
                "--sensor-type", "piezometer",
                "--force-expired-cal",
                "--auto"
            ],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "REJECTED" in result.stdout
        assert "Calibration validation failed" in result.stdout

    def test_commissioning_rejected_out_of_bounds_coords(self):
        result = subprocess.run(
            [
                sys.executable, SCRIPT_PATH,
                "--device-id", "COMM-HW-OOB",
                "--sensor-type", "piezometer",
                "--lat", "12.5000",  # South India, outside NER (20-30°N)
                "--lon", "77.5000",
                "--auto"
            ],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "REJECTED" in result.stdout
        assert "Out-of-bounds geographic location" in result.stdout

    def test_commissioning_rejected_invalid_sensor_type(self):
        result = subprocess.run(
            [
                sys.executable, SCRIPT_PATH,
                "--device-id", "COMM-HW-INVALID-TYPE",
                "--sensor-type", "unknown_gadget",
                "--auto"
            ],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0  # Argparse choices error or validation failure
