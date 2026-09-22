# -*- coding: utf-8 -*-
"""
tests/test_v4_8_dual_stream.py
==============================
Phase V4.8 Test Suite: Dual-Stream Separation, Fail-Closed Degradation & V3 Immutability
"""

import os
import hashlib
import pytest

from services.kinematic_telemetry_service import GLOBAL_KINEMATIC_SERVICE


class TestDualStreamSeparationAndState:
    """Tests that Stream A (Synoptic) and Stream B (Kinematic) remain strictly decoupled."""

    def test_stream_a_available_stream_b_unavailable(self):
        status = GLOBAL_KINEMATIC_SERVICE.get_corridor_status()
        # Stream B status
        assert status["corridor"]["telemetry_status"] == "PHYSICAL_TELEMETRY_PENDING"
        assert status["freshness"]["overall_status"] == "UNAVAILABLE"
        assert status["corridor"]["field_deployment_pending"] is True

    def test_fail_closed_prevents_false_negative_safety_claims(self):
        # When Stream B is unavailable, platform must report DEGRADED/UNAVAILABLE, never "SAFE" or "NO RISK"
        status = GLOBAL_KINEMATIC_SERVICE.get_corridor_status()
        assert status["freshness"]["overall_status"] != "SAFE"
        assert status["freshness"]["overall_status"] != "NO_RISK"
        assert status["freshness"]["overall_status"] == "UNAVAILABLE"


class TestCryptographicIsolationAndImmutability:
    """Tests that Production Model V3 weights match exact expected SHA-256."""

    EXPECTED_V3_SHA = "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"

    def test_v3_weights_sha256_unmodified(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        v3_path = os.path.join(base_dir, "models", "pahad_lstm_v3_weights.pt")
        assert os.path.exists(v3_path), f"V3 weights missing: {v3_path}"

        h = hashlib.sha256()
        with open(v3_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        actual_sha = h.hexdigest()

        assert actual_sha == self.EXPECTED_V3_SHA, f"V3 weights tampered! Expected {self.EXPECTED_V3_SHA}, got {actual_sha}"
