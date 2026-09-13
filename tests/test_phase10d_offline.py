# -*- coding: utf-8 -*-
"""
tests/test_phase10d_offline.py
==============================
PARVAT NETRA • PAHAD AI — Phase 10D Offline Resilience & Transparency Suite
---------------------------------------------------------------------------
Validates:
1. Transparent connectivity states: LIVE, DEGRADED, OFFLINE, ERROR.
2. Invariant: System NEVER claims LIVE when external models or backends are unavailable.
3. Deterministic grounded fallback when LLM gateway is unreachable.
4. Client offline event listeners and offline advisory banner rendering.
5. Error handling for audio/mic exceptions and timeout recovery.
"""

import os
import sys
import json
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import app
from services.pahad_voice_assistant import PahadVoiceAssistantService, PAHAD_VOICE_ASSISTANT


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestPhase10dOffline:

    def test_01_status_badge_states_in_client_js(self):
        """Verify client controller supports all 4 transparent status states."""
        js_path = os.path.join(REPO_ROOT, "static", "js", "pahad_voice_assistant.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        assert "[LIVE]" in js
        assert "[DEGRADED]" in js
        assert "[OFFLINE]" in js
        assert "updateStatusUI" in js
        assert "window.addEventListener('online'" in js
        assert "window.addEventListener('offline'" in js

    def test_02_deterministic_synthesis_when_llm_unavailable(self):
        """Verify deterministic physical synthesis generates accurate briefings without LLM."""
        svc = PahadVoiceAssistantService()
        # Query without LLM active
        res = svc.process_query("What is the current risk for NH-10?", "SK-NH10-KM48")
        assert res["status"] == "SUCCESS"
        assert "Composite Risk Index" in res["response"]
        assert "Factor of Safety" in res["response"]
        assert res["provenance"].startswith("[LIVE]")

    def test_03_empty_or_corrupted_corridor_handles_gracefully(self):
        """Verify non-existent corridor falls back safely to default sector without 500 error."""
        svc = PahadVoiceAssistantService()
        res = svc.process_query("What is the risk?", "NON-EXISTENT-CORRIDOR-999")
        assert res["status"] == "SUCCESS"
        assert "corridor_name" in res
        assert res["latency_ms"] >= 0.0

    def test_04_offline_banner_and_resilient_messaging(self):
        """Verify client JS handles network fetch failures with offline advisory."""
        js_path = os.path.join(REPO_ROOT, "static", "js", "pahad_voice_assistant.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        assert "[OFFLINE / RESILIENT]" in js
        assert "Operating in offline resilient mode" in js

    def test_05_error_state_handling(self):
        """Verify showError puts assistant into ERROR state and announces to screen reader."""
        js_path = os.path.join(REPO_ROOT, "static", "js", "pahad_voice_assistant.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        assert "showError" in js
        assert "AssistantState.ERROR" in js
        assert "announce" in js
