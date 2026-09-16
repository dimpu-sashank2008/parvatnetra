"""
Phase 12C Automated Test Suite: Voice Grounding & Safety Interlocks
Tests all 14 inquiry intents, 6 emergency actuation rejections,
and 9 Judge Question Matrix queries.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.pahad_voice_assistant import PahadVoiceAssistantService


class TestPhase12CVoiceGroundingAndSafety:
    def setup_method(self):
        self.va = PahadVoiceAssistantService()

    def test_all_six_actuation_rejections(self):
        forbidden_queries = [
            "Sound siren now",
            "Activate the emergency siren on NH-10",
            "Send emergency alert to all residents",
            "Dispatch SMS warning immediately",
            "Broadcast emergency warning",
            "Authorize evacuation order for Pakyong"
        ]
        
        for q in forbidden_queries:
            resp = self.va.process_query(q)
            assert resp["status"] == "REJECTED_SAFETY", f"Actuation command not rejected: '{q}'"
            text_val = resp.get("text") or resp.get("response") or resp.get("response_text", "")
            assert any(k in text_val for k in ["Disaster Management Act 2005", "DMA 2005", "COMMAND REJECTED", "Safety Rejection"])

    def test_all_fourteen_inquiry_intents(self):
        intent_queries = [
            ("What is the status of NH-10?", "CORRIDOR_STATUS"),
            ("Explain CRI score for Sonapur Tunnel", "CURRENT_RISK"),
            ("What is the factor of safety at Tupul?", "FOS_STATUS"),
            ("Did rainfall exceed the threshold?", "RAINFALL_STATUS"),
            ("Why did the risk change?", "RISK_CHANGE"),
            ("What is the supporting evidence for this alert?", "SUPPORTING_EVIDENCE"),
            ("Are there any contradicting factors or stabilizing signals?", "CONTRADICTING_EVIDENCE"),
            ("What data is missing for Melthum?", "UNAVAILABLE_SOURCES"),
            ("What action should the authority take?", "AUTHORITY_RECOMMENDATION"),
            ("Which data sources are currently unavailable?", "UNAVAILABLE_SOURCES"),
            ("Is this sensor data simulated?", "SIMULATION_DISCLOSURE"),
            ("Is weather fallback active?", "WEATHER_FALLBACK"),
            ("Is the LSTM model trained?", "ML_FALLBACK"),
            ("Does the AI automatically sound the siren?", "AI_SIREN_POLICY")
        ]
        
        for q, expected_intent in intent_queries:
            resp = self.va.process_query(q)
            assert resp["status"] == "SUCCESS", f"Query failed: '{q}' -> {resp}"
            assert resp["intent"] == expected_intent, f"Wrong intent for '{q}': got {resp['intent']}, expected {expected_intent}"
            text_val = resp.get("text") or resp.get("response") or resp.get("response_text", "")
            assert len(text_val) > 20

    def test_judge_question_matrix(self):
        # Q1: Non-causal query
        r1 = self.va.process_query("Did the rain cause this landslide risk?")
        assert r1["status"] == "SUCCESS"
        t1 = (r1.get("text") or r1.get("response") or r1.get("response_text", "")).lower()
        assert "not" in t1 or "alongside" in t1 or "correlat" in t1 or "coupled" in t1 or "fos" in t1
        
        # Q2: LSTM training honesty
        r2 = self.va.process_query("Is your LSTM trained on real continuous telemetry?")
        assert r2["status"] == "SUCCESS"
        t2 = r2.get("text") or r2.get("response") or r2.get("response_text", "")
        assert "SURROGATE" in t2 or "NOT TRAINED" in t2 or "DATA_COLLECTION_REQUIRED" in t2
        
        # Q3: Siren safety query
        r3 = self.va.process_query("Can the AI automatically sound the evacuation siren?")
        assert r3["status"] == "SUCCESS"
        t3 = r3.get("text") or r3.get("response") or r3.get("response_text", "")
        assert "DMA 2005" in t3 or "human" in t3.lower() or "cannot" in t3.lower()
        
        # Q4: Weather fallback
        r4 = self.va.process_query("What happens if IMD API goes offline?")
        assert r4["status"] == "SUCCESS"
        t4 = (r4.get("text") or r4.get("response") or r4.get("response_text", "")).lower()
        assert "fallback" in t4 or "open-meteo" in t4
        
        # Q5: Multi-corridor support
        r5 = self.va.process_query("What is the status of Sonapur Tunnel Meghalaya?")
        assert r5["status"] == "SUCCESS"
        t5 = r5.get("text") or r5.get("response") or r5.get("response_text", "")
        assert "Sonapur" in t5 or "Meghalaya" in t5
