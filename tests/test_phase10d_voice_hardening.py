# -*- coding: utf-8 -*-
"""
tests/test_phase10d_voice_hardening.py
======================================
PARVAT NETRA • PAHAD AI — Phase 10D Voice Assistant Hardening Suite
-------------------------------------------------------------------
Validates:
1. Voice session lifecycle (session creation, token issuance, active corridor, capabilities).
2. Status endpoint contract (/api/pahad/assistant/status) reporting LIVE status and safety invariants.
3. Context endpoint contract (/api/pahad/assistant/context) for multi-source grounding.
4. Assistant chat processing with spoken response synthesis and latency reporting.
5. DOM elements presence in index.html (launcher, panel, mic, stop, transcript, announcer).
6. JavaScript controller contract in pahad_voice_assistant.js.
"""

import os
import sys
import json
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import app
from services.pahad_voice_assistant import PAHAD_VOICE_ASSISTANT, PahadVoiceAssistantService


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestPhase10dVoiceHardening:

    def test_01_assistant_status_endpoint(self, client):
        """Verify GET /api/pahad/assistant/status returns LIVE and safety invariants."""
        res = client.get("/api/pahad/assistant/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["assistant_status"] == "LIVE"
        assert data["version"] == "v10.4.0-phase10d"

        invariants = data["safety_invariants"]
        assert invariants["public_dispatch"] == "DISABLED"
        assert invariants["siren_dry_run"] == 1
        assert invariants["two_of_three_corroboration"] is True
        assert invariants["statutory_human_authorization"] is True
        assert invariants["conversational_actuation_permitted"] is False

        caps = data["capabilities"]
        assert caps["voice_recognition"] is True
        assert caps["barge_in_interruption"] is True
        assert caps["grounded_sitrep"] is True

    def test_02_session_creation_lifecycle(self, client):
        """Verify POST /api/pahad/assistant/session generates valid ephemeral token."""
        payload = {"user_id": "field_officer_1", "role": "authority"}
        res = client.post("/api/pahad/assistant/session",
                          data=json.dumps(payload), content_type="application/json")
        assert res.status_code == 200

        data = res.get_json()
        assert data["status"] == "SUCCESS"
        sinfo = data["data"]
        assert sinfo["token"].startswith("pva_tok_")
        assert sinfo["expires_in_seconds"] == 3600
        assert "SK-NH10-KM48" in sinfo["available_corridors"]

        # Validate token directly on service
        valid, sdata = PAHAD_VOICE_ASSISTANT.validate_session(sinfo["token"])
        assert valid is True
        assert sdata["user_id"] == "field_officer_1"

    def test_03_corridor_context_retrieval(self, client):
        """Verify GET /api/pahad/assistant/context returns grounded data for requested corridor."""
        res = client.get("/api/pahad/assistant/context?corridor_id=SK-NH10-KM48")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        ctx = data["context"]
        assert ctx["corridor_id"] == "SK-NH10-KM48"
        assert "fos" in ctx
        assert "cri" in ctx
        assert "rainfall_24h_mm" in ctx
        assert "basal_shear_stress_pa" in ctx
        assert ctx["provenance"].startswith("[LIVE]")

    def test_04_chat_processing_with_spoken_synthesis(self, client):
        """Verify POST /api/pahad/assistant/chat delivers both markdown and clean spoken output."""
        sess = PAHAD_VOICE_ASSISTANT.create_session(user_id="eoc_tester")
        token = sess["token"]

        payload = {
            "query": "Give me the operational situation overview for this corridor.",
            "corridor_id": "SK-NH10-KM48",
            "token": token,
            "channel": "voice"
        }
        res = client.post("/api/pahad/assistant/chat", data=json.dumps(payload), content_type="application/json")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert "response" in data
        assert "spoken_response" in data
        assert "grounded_facts" in data
        assert data["latency_ms"] >= 0.0
        # Spoken response must be clean of markdown asterisks
        assert "**" not in data["spoken_response"]
        assert "```" not in data["spoken_response"]

    def test_05_dom_elements_presence_in_template(self):
        """Verify all required assistant DOM elements exist in templates/index.html."""
        tmpl_path = os.path.join(REPO_ROOT, "templates", "index.html")
        with open(tmpl_path, "r", encoding="utf-8") as f:
            html = f.read()

        assert 'id="pahad-assistant-launcher"' in html
        assert 'id="pahad-assistant-panel"' in html
        assert 'id="pahad-assistant-transcript"' in html
        assert 'id="pahad-assistant-input"' in html
        assert 'id="pahad-assistant-mic-btn"' in html
        assert 'id="pahad-assistant-stop-btn"' in html
        assert 'id="pahad-assistant-mute-btn"' in html
        assert 'id="pahad-assistant-close-btn"' in html
        assert 'id="pahad-assistant-corridor-badge"' in html
        assert 'id="pahad-assistant-status-badge"' in html
        assert 'id="pahad-assistant-live-announcer"' in html
        assert 'src="/static/js/pahad_voice_assistant.js"' in html

    def test_06_js_controller_contract(self):
        """Verify required client-side methods and listeners exist in pahad_voice_assistant.js."""
        js_path = os.path.join(REPO_ROOT, "static", "js", "pahad_voice_assistant.js")
        assert os.path.exists(js_path)
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        assert "bargeInStop" in js
        assert "speechSynthesis.cancel" in js
        assert "toggleMic" in js
        assert "toggleMute" in js
        assert "sendQuery" in js
        assert "bindCorridorWatcher" in js
        assert "pahad-corridor-select" in js
        assert "Alt+A" in js or "altKey" in js
