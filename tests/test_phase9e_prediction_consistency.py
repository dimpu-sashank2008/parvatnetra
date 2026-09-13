# -*- coding: utf-8 -*-
"""
tests/test_phase9e_prediction_consistency.py
============================================
Phase 9E: Prediction Consistency, 2-of-3 Corroboration & Safety Governance
--------------------------------------------------------------------------
Validates:
  1. The clean 9-step government prediction hierarchy in #view-prediction.
  2. 2-of-3 sensor corroboration rule for hazard escalation.
  3. Non-causal scientific language disclaimer.
  4. Statutory authority sign-off requirement (DMA 2005 / District Magistrate).
  5. Public dispatch safety gate (ENABLE_PUBLIC_DISPATCH=0).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def index_html(client):
    res = client.get("/")
    assert res.status_code == 200
    return res.get_data(as_text=True)


class TestPhase9ePredictionConsistency:
    """Verifies scientific integrity, non-causal language, and statutory safety interlocks."""

    def test_nine_step_prediction_hierarchy_elements(self, index_html):
        """All 9 core steps must be present in the prediction view DOM."""
        # 1. Institutional identity
        assert "NATIONAL DISASTER MANAGEMENT AUTHORITY" in index_html
        # 2. Location assessment & cascading pickers
        assert 'id="pahad-location-picker"' in index_html
        assert 'id="pahad-state-filter"' in index_html
        assert 'id="pahad-district-filter"' in index_html
        assert 'id="pahad-corridor-select"' in index_html
        # 3. CRI centerpiece & 4. Risk level
        assert 'id="pahad-ai-ring"' in index_html
        assert 'id="pahad-ai-score"' in index_html
        assert 'id="pahad-ai-band"' in index_html
        # 5. Why explanation & non-causal drivers
        assert 'id="pahad-plain-explanation"' in index_html
        assert 'id="pahad-ai-explanation"' in index_html
        assert 'id="pahad-driver-ranked-list"' in index_html
        # 6. Key evidence
        assert 'id="pahad-ai-fos"' in index_html
        assert 'id="pahad-ai-rain-status"' in index_html
        assert 'id="pahad-ai-ml-status"' in index_html
        assert 'id="pahad-ai-seismic-status"' in index_html
        # 7. Recommended action & statutory protocol
        assert 'id="pahad-ai-action"' in index_html
        assert 'id="pahad-ai-action-text"' in index_html
        # 8. Location/map context
        assert 'id="pahad-prediction-minimap"' in index_html
        assert 'id="pahad-minimap-coords"' in index_html
        # 9. Provenance & timestamp
        assert 'id="pahad-evidence-provenance"' in index_html
        assert 'id="pahad-corridor-timestamp"' in index_html

    def test_two_of_three_sensor_corroboration_badge(self, index_html):
        """The 2-of-3 sensor corroboration badge must be present."""
        assert 'id="pahad-corroboration-badge"' in index_html
        assert "CORROBORATED" in index_html

    def test_non_causal_driver_disclaimer(self, index_html):
        """Disclaimers must clarify that model features represent association, not causal proof."""
        assert "Contributing signals indicate statistical association and physical mechanism drivers; they do not constitute individual causal proof." in index_html

    def test_statutory_magistrate_signoff_protocol(self, index_html):
        """Stage 2 AI recommendation and Stage 3 Magistrate sign-off must be clearly delineated."""
        assert "[STAGE 2] AI Recommended Advisory" in index_html
        assert "[STAGE 3] Statutory Human Authority Sign-Off" in index_html
        assert "District Collector / SEOC Magistrate" in index_html
        assert "Disaster Management Act 2005" in index_html or "DMA 2005" in index_html
        assert "ENABLE_PUBLIC_DISPATCH=0" in index_html
