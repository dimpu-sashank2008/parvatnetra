# -*- coding: utf-8 -*-
"""
tests/test_phase10d_barge_in.py
===============================
PARVAT NETRA • PAHAD AI — Phase 10D Conversational Barge-In Verification
-----------------------------------------------------------------------
Validates:
1. Barge-in interruption contract: immediate cancellation of speech synthesis.
2. Stop button actuation and listener registration.
3. Zero audio overlap guarantee: new query dispatch aborts previous utterance.
4. Visual state transitions during barge-in (SPEAKING/LISTENING -> IDLE).
"""

import os
import sys
import re
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


class TestPhase10dBargeIn:

    @classmethod
    def setup_class(cls):
        js_path = os.path.join(REPO_ROOT, "static", "js", "pahad_voice_assistant.js")
        with open(js_path, "r", encoding="utf-8") as f:
            cls.js = f.read()

        html_path = os.path.join(REPO_ROOT, "templates", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            cls.html = f.read()

    def test_01_barge_in_stop_method_cancels_speech(self):
        """Verify bargeInStop explicitly invokes speechSynth.cancel() without delay."""
        assert "bargeInStop()" in self.js
        assert "this.speechSynth.cancel()" in self.js
        assert "AssistantState.IDLE" in self.js

    def test_02_mic_toggle_triggers_barge_in_if_speaking(self):
        """Verify toggling mic while assistant is speaking cancels voice before listening."""
        assert "this.state === AssistantState.SPEAKING" in self.js
        assert "this.bargeInStop()" in self.js

    def test_03_query_dispatch_enforces_barge_in_first(self):
        """Verify sendQuery enforces immediate bargeInStop() prior to dispatching new request."""
        assert "async sendQuery" in self.js
        barge_pos = self.js.find("this.bargeInStop();")
        fetch_pos = self.js.find("fetch('/api/pahad/assistant/chat'")
        assert barge_pos != -1, "bargeInStop() must be called in sendQuery"
        assert fetch_pos != -1, "fetch() must be called in sendQuery"
        assert barge_pos < fetch_pos, "bargeInStop() must precede fetch() to prevent overlapping audio"


    def test_04_stop_button_dom_and_aria(self):
        """Verify #pahad-assistant-stop-btn is present with clear barge-in label and accessible styling."""
        assert 'id="pahad-assistant-stop-btn"' in self.html
        assert "Stop (Barge-In)" in self.html
        assert "Click to interrupt" in self.html

    def test_05_stop_button_wiring_in_controller(self):
        """Verify stop button click listener triggers bargeInStop()."""
        assert "this.stopBtn.addEventListener('click', () => this.bargeInStop())" in self.js
