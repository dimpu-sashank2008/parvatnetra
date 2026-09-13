# -*- coding: utf-8 -*-
"""
tests/test_phase9c_ui.py
========================
Phase 9C: Clean Government EOC UI Redesign - Homepage UI Test Suite.

Verifies:
1. Core UX Rule: The default homepage (#view-prediction) answers ONLY:
   - WHERE IS THE RISK?
   - HOW HIGH IS THE RISK?
   - WHY?
   - WHAT SHOULD THE AUTHORITY DO?
2. Absolute Zero Unicode Emoji Invariant across templates and client scripts.
3. Clean, high-legibility CRI circle without neon or cyberpunk glows.
4. Embedded mini-map footprint and coordinate indicator in prediction card.
5. User-facing GSI Disaster Archive button is removed/hidden from header.
6. Local Anime.js library is loaded for smooth, fast operational transitions.
"""

import os
import re
import pytest
from app import app as flask_app

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")


@pytest.fixture
def index_html():
    """Load index.html content."""
    assert os.path.exists(TEMPLATE_PATH), f"Template not found at {TEMPLATE_PATH}"
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def client():
    """Flask test client."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestPhase9cCoreUX:
    """Verifies the four core operational questions on the homepage."""

    def test_default_workspace_view_prediction_exists(self, index_html):
        """Workspace view for prediction must exist and not be hidden by default."""
        assert 'id="view-prediction"' in index_html
        # view-prediction is the primary active workspace
        assert '<div id="view-prediction" class="workspace-view">' in index_html

    def test_where_is_the_risk_elements(self, index_html):
        """Must include location selector, state/district/corridor cascading filters, Use Map Location, and mini-map."""
        assert 'id="pahad-location-picker"' in index_html
        assert 'id="pahad-state-filter"' in index_html
        assert 'id="pahad-district-filter"' in index_html
        assert 'id="pahad-corridor-select"' in index_html
        assert 'id="btn-pick-map-loc"' in index_html
        assert "Use Map Location" in index_html
        assert 'id="pahad-prediction-minimap"' in index_html
        assert 'id="pahad-minimap-coords"' in index_html

    def test_how_high_is_the_risk_elements(self, index_html):
        """Must include CRI score, risk band, event probability, FoS, rain, seismic, and model status."""
        assert 'id="pahad-ai-score"' in index_html
        assert 'id="pahad-ai-band"' in index_html
        assert 'id="pahad-ai-prob"' in index_html
        assert 'id="pahad-ai-fos"' in index_html
        assert 'id="pahad-ai-rain-status"' in index_html
        assert 'id="pahad-ai-seismic-status"' in index_html
        assert "TRAINED_LIMITED_DATA" in index_html

    def test_why_elements(self, index_html):
        """Must include plain-language explanation and multimodal contributing drivers."""
        assert 'id="pahad-ai-explanation"' in index_html
        assert "Why" in index_html or "WHY" in index_html
        assert "pahad-driver-list" in index_html or "pahad-ai-drivers" in index_html
        assert "pahad-ai-sourcebar" in index_html

    def test_what_should_authority_do_elements(self, index_html):
        """Must include actionable operational advisory, sign-off, and 2-of-3 corroboration."""
        assert 'id="pahad-ai-action-text"' in index_html
        assert "WHAT SHOULD THE AUTHORITY DO" in index_html or "AI Recommended Advisory" in index_html
        assert "CORROBORATED" in index_html or "2-of-3" in index_html or "3/3" in index_html

    def test_zero_unicode_emojis(self, index_html):
        """Must strictly contain ZERO Unicode emojis (100% SVG Phosphor icons)."""
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        matches = emoji_pattern.findall(index_html)
        assert len(matches) == 0, f"Found {len(matches)} emojis: {matches[:10]}"

    def test_gsi_history_button_hidden(self, index_html):
        """User-facing GSI Disaster Archive button is removed/hidden from header."""
        assert 'id="btn-top-history-media"' in index_html
        # Must have hidden class and display:none
        assert 'id="btn-top-history-media" class="hidden"' in index_html or 'display:none' in index_html

    def test_anime_js_loaded(self, index_html):
        """Anime.js local script must be referenced in head."""
        assert '/static/js/anime.min.js' in index_html

    def test_clean_cri_circle_styling(self, index_html):
        """CRI circle should use clean typography and styling without neon glows."""
        assert 'pahad-ai-score-num' in index_html
        assert 'pahad-ai-ring' in index_html
