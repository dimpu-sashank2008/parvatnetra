# -*- coding: utf-8 -*-
"""
tests/test_v4_8_live_boundary.py
================================
Phase V4.8 Test Suite: Real vs Bench vs Simulated Data Boundary & Localhost Safety
"""

import os
import pytest

from engine.telemetry_evidence_audit_engine import (
    LiveTelemetryBoundaryCheck,
    PROV_LIVE,
    PROV_BENCH,
    PROV_SIMULATED,
    PROV_UNAVAILABLE
)
from services.packet_replay_service import (
    SOURCE_CLASS_LIVE_PHYSICAL,
    SOURCE_CLASS_BENCH_HARDWARE,
    SOURCE_CLASS_SIMULATED,
    VALID_SOURCE_CLASSES
)


class TestDataBoundaryEnforcement:
    """Tests that bench hardware and simulations can never masquerade as live field telemetry."""

    def test_bench_hardware_rejected_by_live_gate(self):
        check = LiveTelemetryBoundaryCheck(
            sensor_id="PIEZO-NH10-KM48-01",
            verified_physical_sensor_identity=True,
            verified_installation_or_field_presence=False,  # Still in lab
            valid_telemetry_packet=True,
            valid_timestamp=True,
            valid_provenance=True,
            validated_sensor_gateway_path=True,
            no_simulation_marker=True,
            no_hil_marker=False,             # Failed: HIL bench fixture present
            no_benchmark_fixture=False,      # Failed: Bench fixture
            persistence_in_observation_store=True,
            rejection_reasons=["BENCH_HIL_MARKER_PRESENT", "NO_FIELD_PRESENCE"]
        )
        assert check.is_live_field_telemetry is False
        assert "BENCH_HIL_MARKER_PRESENT" in check.rejection_reasons

    def test_simulated_packet_rejected_by_live_gate(self):
        check = LiveTelemetryBoundaryCheck(
            sensor_id="INCL-NH10-KM48-01",
            verified_physical_sensor_identity=False,
            verified_installation_or_field_presence=False,
            valid_telemetry_packet=True,
            valid_timestamp=True,
            valid_provenance=False,
            validated_sensor_gateway_path=False,
            no_simulation_marker=False,      # Failed: simulation flag set
            no_hil_marker=True,
            no_benchmark_fixture=True,
            persistence_in_observation_store=True,
            rejection_reasons=["SIMULATION_MARKER_DETECTED"]
        )
        assert check.is_live_field_telemetry is False


class TestLocalhostAndPublicDispatchSafeguards:
    """Tests localhost-only rules, public dispatch disablement, and siren dry-run."""

    def test_public_dispatch_is_disabled(self):
        dispatch_val = os.environ.get("ENABLE_PUBLIC_DISPATCH", "0")
        assert dispatch_val in ["0", "false", "False"]

    def test_siren_is_in_dry_run_mode(self):
        siren_val = os.environ.get("SIREN_DRY_RUN", "1")
        assert siren_val in ["1", "true", "True"]

    def test_localhost_only_binding_configured(self):
        flask_host = os.environ.get("FLASK_HOST", "127.0.0.1")
        assert flask_host in ["127.0.0.1", "localhost"]
