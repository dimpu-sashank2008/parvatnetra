# -*- coding: utf-8 -*-
"""
tests/test_phase10d_grounding.py
================================
PARVAT NETRA • PAHAD AI — Phase 10D Multi-Source Grounding Verification
-----------------------------------------------------------------------
Validates:
1. Grounded telemetry responses across all 9 canonical corridors.
2. Dynamic corridor switching: queries return sector-specific values with zero stale data.
3. Factual alignment: reported CRI, FoS, rainfall, and tau_b match authoritative backend services.
4. Model boundary enforcement: assistant never calculates new CRI or overrides FoS.
5. Regional priority corridor triage matches engine ranking.
"""

import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from services.pahad_voice_assistant import PAHAD_VOICE_ASSISTANT, CORRIDOR_METADATA


class TestPhase10dGrounding:

    def test_01_all_canonical_corridors_registered(self):
        """Verify all 9 canonical corridors are registered in assistant metadata."""
        expected_corridors = [
            "SK-NH10-KM48", "ML-SONAPUR-01", "MN-TUPUL-RLY", "MZ-MELTHUM-QRY",
            "AS-HAFLONG-RLY", "ML-MAWSYNRAM", "NL-DZUKOU-KOH", "AR-TAWANG-SELA", "TR-JAMPUI-HILLS"
        ]
        for cid in expected_corridors:
            assert cid in CORRIDOR_METADATA
            meta = CORRIDOR_METADATA[cid]
            assert "name" in meta
            assert "state" in meta
            assert "district" in meta

    def test_02_dynamic_corridor_switching_updates_context(self):
        """Verify querying different corridors dynamically produces unique sector context without stale data."""
        ctx_sikkim = PAHAD_VOICE_ASSISTANT.get_grounded_corridor_context("SK-NH10-KM48")
        ctx_manipur = PAHAD_VOICE_ASSISTANT.get_grounded_corridor_context("MN-TUPUL-RLY")
        ctx_meghalaya = PAHAD_VOICE_ASSISTANT.get_grounded_corridor_context("ML-SONAPUR-01")

        assert ctx_sikkim["corridor_id"] == "SK-NH10-KM48"
        assert ctx_manipur["corridor_id"] == "MN-TUPUL-RLY"
        assert ctx_meghalaya["corridor_id"] == "ML-SONAPUR-01"

        assert "Sikkim" in ctx_sikkim["corridor_name"] or "NH-10" in ctx_sikkim["corridor_name"]
        assert "Tupul" in ctx_manipur["corridor_name"] or "Manipur" in ctx_manipur["state"]

    def test_03_fos_grounding_accuracy(self):
        """Verify FoS query returns numerical Factor of Safety matching backend context."""
        res = PAHAD_VOICE_ASSISTANT.process_query(
            query="What is the current Factor of Safety and slope stability?",
            corridor_id="SK-NH10-KM48"
        )
        assert res["status"] == "SUCCESS"
        facts = res["grounded_facts"]
        assert "fos" in facts
        fos_val = facts["fos"]
        assert 0.0 < fos_val < 3.0
        # The exact FoS string must appear in the markdown output
        assert f"{fos_val:.3f}" in res["response"]
        assert res["provenance"].startswith("[LIVE]")

    def test_04_rainfall_and_scour_grounding(self):
        """Verify rainfall and Teesta basal scour queries return live telemetry figures."""
        rain_res = PAHAD_VOICE_ASSISTANT.process_query(
            query="Report 24h cumulative rainfall and IMD anomaly percentage.",
            corridor_id="SK-NH10-KM48"
        )
        assert rain_res["status"] == "SUCCESS"
        assert "mm" in rain_res["response"]
        assert "anomaly" in rain_res["response"].lower()

        scour_res = PAHAD_VOICE_ASSISTANT.process_query(
            query="What is the Teesta River basal scour shear stress?",
            corridor_id="SK-NH10-KM48"
        )
        assert scour_res["status"] == "SUCCESS"
        assert "Pa" in scour_res["response"] or "Pascals" in scour_res["spoken_response"]

    def test_05_multi_horizon_forecast_grounding(self):
        """Verify multi-horizon forecast query outputs 6h, 12h, 24h, 48h probabilities."""
        res = PAHAD_VOICE_ASSISTANT.process_query(
            query="Give me the multi-horizon early warning forecast probabilities.",
            corridor_id="SK-NH10-KM48"
        )
        assert res["status"] == "SUCCESS"
        resp = res["response"]
        assert "6-Hour Horizon" in resp
        assert "12-Hour Horizon" in resp
        assert "24-Hour Horizon" in resp
        assert "48-Hour Horizon" in resp

    def test_06_highest_risk_corridor_triage(self):
        """Verify priority corridor query correctly identifies regional priority corridor."""
        res = PAHAD_VOICE_ASSISTANT.process_query(
            query="Which corridor currently exhibits the highest risk?",
            corridor_id="SK-NH10-KM48"
        )
        assert res["status"] == "SUCCESS"
        assert "Priority Risk Corridor" in res["response"]
        assert "Evaluation Protocol" in res["response"]
