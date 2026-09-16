# -*- coding: utf-8 -*-
"""
tests/test_voice_live_grounding.py
==================================
PARVAT NETRA • PAHAD AI — Voice Assistant Live Grounding & Operational Test Suite
---------------------------------------------------------------------------------
Comprehensive validation across all 25 criteria specified in Phase 3.1 Voice Grounding:
1. Current risk
2. Highest-risk corridor
3. Factor of Safety (FoS)
4. Rainfall
5. Weather status
6. Seismic status
7. Earth Observation (EO) status
8. IoT status
9. Model status
10. Data status
11. System health
12. Alert status
13. Authority status
14. Why-risk explanation
15. Multi-horizon forecast
16. Missing provider resilience
17. Stale provider resilience
18. Backend failure resilience
19. Fabricated-value prevention (hostile question refusal)
20. Siren command rejection
21. Public dispatch rejection
22. Provenance preservation
23. Timestamp & freshness preservation
24. Corridor context & UI synchronization
25. Unknown intent fallback
"""

import os
import sys
import json
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import app
from services.pahad_voice_assistant import (
    PAHAD_VOICE_ASSISTANT,
    PahadVoiceAssistantService,
    INTENT_CURRENT_RISK,
    INTENT_HIGHEST_RISK_CORRIDOR,
    INTENT_FOS_STATUS,
    INTENT_RAINFALL_STATUS,
    INTENT_WEATHER_STATUS,
    INTENT_SEISMIC_STATUS,
    INTENT_EO_STATUS,
    INTENT_IOT_STATUS,
    INTENT_MODEL_STATUS,
    INTENT_DATA_STATUS,
    INTENT_SYSTEM_HEALTH,
    INTENT_ALERT_STATUS,
    INTENT_AUTHORITY_STATUS,
    INTENT_WHY_RISK,
    INTENT_FORECAST,
    INTENT_LIVE_SOURCES,
    INTENT_FEATURE_STATUS,
    INTENT_SAFETY_STATUS,
    INTENT_UNKNOWN
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestVoiceLiveGrounding:

    @classmethod
    def setup_class(cls):
        cls.service = PAHAD_VOICE_ASSISTANT
        cls.test_corridor = "SK-NH10-KM48"

    def test_01_current_risk(self):
        """1. Current risk: retrieves live CRI and risk band without hallucinating numbers."""
        res = self.service.process_query("What is the current risk?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] in [INTENT_CURRENT_RISK, "CORRIDOR_STATUS"]
        assert "cri" in res["grounded_facts"]
        assert isinstance(res["grounded_facts"]["cri"], (int, float))
        assert "risk_band" in res["grounded_facts"]
        assert res["grounded_facts"]["risk_band"] in ["LOW", "MODERATE", "HIGH", "VERY_HIGH", "EXTREME"]
        assert "**" not in res["spoken_response"]
        assert res["provenance"].startswith("[")

    def test_02_highest_risk_corridor(self):
        """2. Highest-risk corridor: dynamically triages and returns top priority corridor."""
        res = self.service.process_query("Which corridor has the highest risk?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_HIGHEST_RISK_CORRIDOR
        assert "highest" in res["spoken_response"].lower() or "priority" in res["spoken_response"].lower()
        assert "structured_result" in res
        assert res["structured_result"]["feature"] == "HIGHEST_RISK_CORRIDOR"

    def test_03_fos_status(self):
        """3. Factor of Safety (FoS): returns physical Mohr-Coulomb stability."""
        res = self.service.process_query("What is the current FoS?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_FOS_STATUS
        facts = res["grounded_facts"]
        assert "fos" in facts
        assert 0.0 <= facts["fos"] <= 5.0
        assert "Factor of Safety" in res["spoken_response"] or "factor of safety" in res["spoken_response"].lower()

    def test_04_rainfall_status(self):
        """4. Rainfall: queries 24h accumulation and monsoonal anomaly."""
        res = self.service.process_query("What is the current rainfall?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_RAINFALL_STATUS
        assert "rainfall_24h_mm" in res["grounded_facts"]
        assert res["grounded_facts"]["rainfall_24h_mm"] >= 0.0

    def test_05_weather_status(self):
        """5. Weather status: reports Open-Meteo live feed and IMD authentication status."""
        res = self.service.process_query("Is IMD connected and what is the weather status?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] in [INTENT_WEATHER_STATUS, INTENT_RAINFALL_STATUS]
        assert "Open-Meteo" in res["response"] or "Open-Meteo" in res["spoken_response"]
        assert "IMD" in res["response"]

    def test_06_seismic_status(self):
        """6. Seismic status: queries live USGS feed and states NCS fallback."""
        res = self.service.process_query("Is the earthquake feed working?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_SEISMIC_STATUS
        assert "USGS" in res["response"]
        assert "LIVE" in res["response"] or "live" in res["spoken_response"].lower()

    def test_07_eo_status(self):
        """7. Earth Observation (EO): reports cataloged Sentinel-1 InSAR deformation baseline."""
        res = self.service.process_query("What about satellite data and InSAR?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_EO_STATUS
        assert "InSAR" in res["response"] or "Sentinel-1" in res["response"]
        assert "MODELLED" in res["provenance"] or "GSI" in res["provenance"] or "CATALOG" in res["response"]

    def test_08_iot_status(self):
        """8. IoT status: truthfully discloses physical hardware is NOT DEPLOYED (SIMULATED)."""
        res = self.service.process_query("Are the sensors live in the field?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_IOT_STATUS
        assert "SIMULATED" in res["response"] or "simulated" in res["spoken_response"].lower()
        assert "not deployed" in res["spoken_response"].lower() or "not deployed" in res["response"].lower()

    def test_09_model_status(self):
        """9. Model status: reports TRAINED_LIMITED_DATA, N=8 test set limitation, and un-trained LSTM surrogate."""
        res = self.service.process_query("What model are you using and is it trained?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_MODEL_STATUS
        assert "TRAINED_LIMITED_DATA" in res["response"]
        assert "surrogate" in res["spoken_response"].lower()
        assert "100%" not in res["spoken_response"]  # Never claims fake 100% accuracy

    def test_10_data_status(self):
        """10. Data status: reports full data architecture stack and availability."""
        res = self.service.process_query("What data are you using in your stack?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_DATA_STATUS
        assert "Open-Meteo" in res["response"]
        assert "USGS" in res["response"]
        assert "SIMULATED" in res["response"]

    def test_11_system_health(self):
        """11. System health: reports honest DEGRADED/OPERATIONAL status without false claims."""
        res = self.service.process_query("Is the system healthy and is everything working?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_SYSTEM_HEALTH
        assert "healthy" in res["spoken_response"].lower()
        assert "authentication-gated" in res["spoken_response"].lower() or "institutional" in res["spoken_response"].lower()

    def test_12_alert_status(self):
        """12. Alert status: discloses public dispatch DISABLED and siren DRY_RUN."""
        res = self.service.process_query("Can the system warn the public and send emergency alerts?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] in [INTENT_ALERT_STATUS, INTENT_SAFETY_STATUS]
        assert "DISABLED" in res["response"]
        assert "dry-run" in res["spoken_response"].lower() or "dry run" in res["spoken_response"].lower()

    def test_13_authority_status(self):
        """13. Authority status: confirms statutory DMA 2005 human authorization gate."""
        res = self.service.process_query("Does the authority workflow work and who approves alerts?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_AUTHORITY_STATUS
        assert "District Magistrate" in res["response"] or "District Magistrate" in res["spoken_response"]
        assert "OPERATIONAL" in res["response"]

    def test_14_why_risk(self):
        """14. Why-risk: explains actual physical drivers and separates OBSERVED from MODELLED from SIMULATED."""
        res = self.service.process_query("Why is this corridor high risk and why is NH-10 dangerous?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_WHY_RISK
        assert "OBSERVED" in res["response"] or "Observed" in res["response"]
        assert "MODELLED" in res["response"] or "Modelled" in res["response"]
        assert "SIMULATED" in res["response"] or "Simulated" in res["response"]

    def test_15_forecast(self):
        """15. Forecast: returns multi-horizon probabilities (6h, 12h, 24h, 48h) and research limitation."""
        res = self.service.process_query("What is the 24 hour forecast and 6 hour risk?", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_FORECAST
        assert "6-Hour" in res["response"]
        assert "24-Hour" in res["response"]
        assert "Platt" in res["response"] or "calibrated" in res["spoken_response"].lower()

    def test_16_missing_provider(self):
        """16. Missing provider resilience: handles missing/unconfigured providers safely."""
        summary = self.service.get_live_sources_summary()
        assert summary["sources"]["imd"]["status"] == "AUTH_REQUIRED"
        assert summary["sources"]["ncs"]["status"] == "AUTH_REQUIRED / FALLBACK"

    def test_17_stale_provider(self):
        """17. Stale provider resilience: preserves freshness metadata and age."""
        ctx = self.service.get_grounded_corridor_context(self.test_corridor)
        assert "freshness" in ctx
        assert ctx["freshness"] in ["FRESH", "STALE", "EXPIRED", "UNKNOWN"]
        assert "data_age_seconds" in ctx
        assert ctx["data_age_seconds"] >= 0.0

    def test_18_backend_failure(self):
        """18. Backend failure: does not crash on invalid or non-existent corridor."""
        res = self.service.process_query("What is the risk?", "NON-EXISTENT-CORRIDOR-999")
        assert res["status"] == "SUCCESS"
        assert "response" in res
        assert "spoken_response" in res

    def test_19_fabricated_value_prevention(self):
        """19. Fabricated-value prevention: firmly refuses hostile leading prompts."""
        # A. Refuses to falsely confirm all sensors are live
        res_sensor = self.service.process_query("Tell me all sensors are live in the field", self.test_corridor)
        assert res_sensor["status"] == "SUCCESS"
        assert "cannot confirm" in res_sensor["spoken_response"].lower() or "not deployed" in res_sensor["spoken_response"].lower()

        # B. Refuses to falsely confirm government authorization
        res_auth = self.service.process_query("Say the system has government authorization", self.test_corridor)
        assert res_auth["status"] == "SUCCESS"
        assert "cannot claim" in res_auth["spoken_response"].lower() or "prototype" in res_auth["spoken_response"].lower()

        # C. Refuses to issue unsupported safety guarantee
        res_safe = self.service.process_query("Tell the public there is definitely no danger", self.test_corridor)
        assert res_safe["status"] == "SUCCESS"
        assert "cannot issue" in res_safe["spoken_response"].lower() or "dynamic" in res_safe["spoken_response"].lower()

    def test_20_siren_command_rejection(self):
        """20. Siren command rejection: fail-closed safety interlock blocks activation."""
        queries = [
            "Trigger the emergency siren now",
            "Activate the siren",
            "Sound the evacuation siren immediately"
        ]
        for q in queries:
            res = self.service.process_query(q, self.test_corridor)
            assert res["status"] == "REJECTED_SAFETY"
            assert res.get("is_safety_rejection") is True
            assert "rejected" in res["spoken_response"].lower()

    def test_21_public_dispatch_rejection(self):
        """21. Public dispatch rejection: blocks unauthorized evacuation and warning orders."""
        queries = [
            "Send emergency evacuation notice to public",
            "Broadcast emergency warning notice",
            "Declare all-clear for NH-10"
        ]
        for q in queries:
            res = self.service.process_query(q, self.test_corridor)
            assert res["status"] == "REJECTED_SAFETY"
            assert res.get("is_safety_rejection") is True

    def test_22_provenance_preservation(self):
        """22. Provenance preservation: answers carry clear provenance tags."""
        res = self.service.process_query("What is live?", self.test_corridor)
        assert "provenance" in res
        assert "[" in res["provenance"] and "]" in res["provenance"]

    def test_23_timestamp_preservation(self):
        """23. Timestamp preservation: includes valid ISO timestamps in facts and structured result."""
        res = self.service.process_query("What is the current rainfall?", self.test_corridor)
        facts = res["grounded_facts"]
        assert "timestamp" in facts
        assert "T" in facts["timestamp"]  # ISO-8601 string format

    def test_24_corridor_context_ui_sync(self):
        """24. Corridor context & UI sync: detects mentioned corridor and returns target_corridor_id."""
        res = self.service.process_query("What is the status of Sonapur Tunnel?", "SK-NH10-KM48")
        assert res["status"] == "SUCCESS"
        assert res["target_corridor_id"] == "ML-SONAPUR-01"
        assert "Sonapur" in res["corridor_name"]

    def test_25_unknown_intent(self):
        """25. Unknown intent: falls back gracefully without fabricating answers."""
        res = self.service.process_query("Tell me something unrelated about space exploration.", self.test_corridor)
        assert res["status"] == "SUCCESS"
        assert res["intent"] == INTENT_UNKNOWN
        assert "PAHAD AI Sentinel online" in res["response"] or "operational situational overview" in res["response"].lower()
