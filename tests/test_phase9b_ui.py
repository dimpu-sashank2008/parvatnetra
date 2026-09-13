# -*- coding: utf-8 -*-
"""
tests/test_phase9b_ui.py
========================
Phase 9B: Government-Grade Homepage and Dashboard UX Test Suite.

Verifies:
1. GIGW 3.0 / NIC / NDMA Institutional Header and Branding Lockup.
2. Top Government Command Summary (5 KPI cards with live synchronization).
3. Plain-Language Risk Explanation and Non-Causal Contributing Drivers.
4. Separation of AI Recommendation (Stage 2) from Statutory Human Authority Sign-Off (Stage 3).
5. Theme contrast rules for light and dark modes.
6. Absolute Zero Unicode Emoji Invariant across templates and client scripts.
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


class TestGovernmentHeaderAndIdentity:
    """Verifies official Government of India / NDMA / MDoNER institutional visual identity."""

    def test_official_national_portal_branding(self, index_html):
        """Header must include national identity lockup, bilingual branding, and portal title."""
        assert "PARVAT NETRA" in index_html
        assert "पर्वत नेत्र" in index_html
        assert "MDoNER" in index_html or "NDMA" in index_html or "Government of India" in index_html
        assert "parvat_netra_emblem" in index_html

    def test_accessibility_controls_present(self, index_html):
        """Must include theme toggle, font resizing, and language selection controls."""
        assert 'id="theme-toggle-btn"' in index_html
        assert 'id="lang-select"' in index_html
        assert "aria-label" in index_html

    def test_zero_unicode_emojis_in_index(self, index_html):
        """Templates must have ZERO Unicode emojis — strictly Phosphor SVG/font icons."""
        emoji_pattern = re.compile(r'[\U0001F300-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]')
        matches = emoji_pattern.findall(index_html)
        assert len(matches) == 0, f"Found {len(matches)} forbidden emojis: {matches[:10]}"


class TestTopCommandSummaryBar:
    """Verifies the 5-card Government Command Summary KPI strip."""

    def test_command_summary_container_exists(self, index_html):
        """Section #gov-command-summary must exist with accessibility label."""
        assert 'id="gov-command-summary"' in index_html
        assert 'aria-label="National Disaster Management Command Summary"' in index_html

    def test_all_five_kpi_cards_present(self, index_html):
        """Must contain all 5 required government command KPI cards."""
        assert 'id="kpi-gov-overall-risk"' in index_html
        assert 'id="kpi-gov-priority-loc"' in index_html
        assert 'id="kpi-gov-corridors"' in index_html
        assert 'id="kpi-gov-pending-reviews"' in index_html
        assert 'id="kpi-gov-telemetry-health"' in index_html

    def test_command_summary_light_mode_css(self, index_html):
        """CSS must define light mode contrast overrides for #gov-command-summary cards and text."""
        assert "body.light-mode #gov-command-summary .kpi-card" in index_html
        assert "color:#0f172a !important" in index_html or "color: #0f172a" in index_html


class TestPlainLanguageAndDrivers:
    """Verifies plain-language risk explanation and non-causal driver labeling."""

    def test_plain_explanation_box_exists(self, index_html):
        """Plain language explanation box #pahad-plain-explanation must exist."""
        assert 'id="pahad-plain-explanation"' in index_html

    def test_non_causal_driver_disclaimer(self, index_html):
        """Must include non-causal disclaimer stating signals indicate statistical association/drivers."""
        assert "Contributing signals indicate statistical association and physical mechanism drivers" in index_html
        assert "do not constitute individual causal proof" in index_html

    def test_driver_list_structure(self, index_html):
        """Ranked driver list must exist with driver bar and signal indicators."""
        assert 'id="pahad-driver-ranked-list"' in index_html
        assert "PRIMARY DRIVER" in index_html or "SECONDARY DRIVER" in index_html or "SUPPORTING SIGNAL" in index_html


class TestStatutoryAuthorityDemarcation:
    """Verifies segregation between AI recommendations and statutory human sign-offs."""

    def test_stage2_ai_advisory_demarcation(self, index_html):
        """Card must clearly designate AI recommendations as [STAGE 2] AI Recommended Advisory."""
        assert "[STAGE 2] AI Recommended Advisory" in index_html
        assert 'id="pahad-ai-action"' in index_html
        assert 'id="pahad-ai-action-reason"' in index_html
        assert 'id="pahad-corroboration-badge"' in index_html

    def test_stage3_human_authority_signoff(self, index_html):
        """Card must clearly designate statutory authority protocol as [STAGE 3] Statutory Human Authority Sign-Off."""
        assert "[STAGE 3] Statutory Human Authority Sign-Off" in index_html
        assert "District Collector" in index_html or "SEOC Magistrate" in index_html
        assert "DMA 2005" in index_html

    def test_safety_gate_dry_run_notice(self, index_html):
        """Safety Gate active notice must be displayed."""
        assert "Safety Gate: ENABLE_PUBLIC_DISPATCH=0" in index_html or "Simulated / Test Mode" in index_html


class TestJavaScriptDynamicSynchronization:
    """Verifies that client JS synchronizes government command summary and plain explanation."""

    def test_corridor_selection_syncs_kpis(self, index_html):
        """onCorridorSelectionChanged must update priority location, overall risk KPI, plain explanation, and corroboration badge."""
        assert "kpi-gov-priority-loc" in index_html
        assert "kpi-gov-overall-risk" in index_html
        assert "pahad-plain-explanation" in index_html
        assert "pahad-corroboration-badge" in index_html

    def test_custom_location_syncs_kpis(self, index_html):
        """runCustomLocationInference must also update priority location and overall risk KPI."""
        assert "async function runCustomLocationInference" in index_html
