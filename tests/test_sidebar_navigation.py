"""
tests/test_sidebar_navigation.py
SIH Top-1 Grade Validation:
Verifies the complete EOC master navigation drawer, accessible dialog semantics,
panel target integrity, modal triggers, DOM anchors, JS handlers, and CSS pulse effects.
"""
import os
import re
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, 'templates', 'index.html')
CSS_STATIC_PATH = os.path.join(BASE_DIR, 'static', 'css', 'parvat_theme.css')
CSS_PUBLIC_PATH = os.path.join(BASE_DIR, 'public', 'static', 'css', 'parvat_theme.css')


@pytest.fixture(scope="module")
def index_html_content():
    assert os.path.exists(INDEX_PATH), f"Missing index.html at {INDEX_PATH}"
    with open(INDEX_PATH, mode='r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope="module")
def theme_css_content():
    assert os.path.exists(CSS_STATIC_PATH), f"Missing theme CSS at {CSS_STATIC_PATH}"
    with open(CSS_STATIC_PATH, mode='r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope="module")
def public_theme_css_content():
    assert os.path.exists(CSS_PUBLIC_PATH), f"Missing public theme CSS at {CSS_PUBLIC_PATH}"
    with open(CSS_PUBLIC_PATH, mode='r', encoding='utf-8') as f:
        return f.read()


def test_sidebar_drawer_markup_and_accessibility(index_html_content):
    assert 'id="eoc-sidebar-drawer"' in index_html_content, "Drawer container #eoc-sidebar-drawer not found"
    assert 'id="eoc-sidebar-backdrop"' in index_html_content, "Drawer backdrop #eoc-sidebar-backdrop not found"
    drawer_match = re.search(r'<nav[^>]*id="eoc-sidebar-drawer"[^>]*>', index_html_content)
    assert drawer_match is not None, "Could not match <nav id='eoc-sidebar-drawer'>"
    drawer_tag = drawer_match.group(0)
    assert 'role="dialog"' in drawer_tag, "Drawer must have role='dialog'"
    assert 'aria-modal="true"' in drawer_tag, "Drawer must have aria-modal='true'"
    assert 'aria-label=' in drawer_tag, "Drawer must have an aria-label"


def test_sidebar_hamburger_button(index_html_content):
    btn_match = re.search(r'<button[^>]*id="btn-hamburger-menu"[^>]*>', index_html_content)
    assert btn_match is not None, "Hamburger button #btn-hamburger-menu not found"
    btn_tag = btn_match.group(0)
    assert 'toggleSidebarMenu()' in btn_tag, "Hamburger button must call toggleSidebarMenu()"
    assert 'aria-expanded=' in btn_tag, "Hamburger button must have aria-expanded attribute"
    assert 'aria-label=' in btn_tag, "Hamburger button must have aria-label"


def test_sidebar_all_seven_categories_present(index_html_content):
    expected_categories = [
        "0. SIH TOP-1 DEFENSE",
        "1. PAHAD PREDICTIVE AI",
        "2. GIS &amp; TERRAIN INTELLIGENCE",
        "3. FIELD OPERATIONS &amp; SENSORS",
        "4. EOC TACTICAL COMMAND",
        "5. PUBLIC WARNING &amp; SAFEGUARDS",
        "6. SYSTEM GOVERNANCE &amp; MLOPS",
    ]
    for cat in expected_categories:
        assert cat in index_html_content, f"Missing category section '{cat}' in index.html sidebar"


def test_sidebar_judge_defense_and_scientific_modals(index_html_content):
    assert "toggleJudgeDefenseOverlay(true)" in index_html_content
    assert "openDataTruthModal()" in index_html_content
    assert "openScientificExplModal('fos')" in index_html_content
    assert "open3DTerrainModel(" in index_html_content
    assert "openHistoricalMediaModal()" in index_html_content
    assert "openWeatherForecastModal()" in index_html_content
    assert "togglePahadRegionalDrawer()" in index_html_content
    assert "openCapModal()" in index_html_content
    assert "openCitizenReportModal()" in index_html_content


def test_all_workspace_views_exist_in_dom(index_html_content):
    workspace_views = [
        'view-prediction',
        'view-horizon-forecast',
        'view-response',
        'view-system',
    ]
    for view_id in workspace_views:
        assert f'id="{view_id}"' in index_html_content or f"id='{view_id}'" in index_html_content, (
            f"Target workspace view '{view_id}' missing in index.html"
        )


def test_all_subpanel_anchors_exist_in_dom(index_html_content):
    anchors = [
        'gis-map-card',
        'pahad-prediction-details-panel',
        'teesta-hydro-widget',
        'observation-queue-section',
        'ai-sitrep-card',
        'citizen-bypass-calculator-card',
        'pahad-autonomous-siren-card',
        'pahad-model-status-panel',
        'seismic-quick-status',
    ]
    for anchor in anchors:
        assert f'id="{anchor}"' in index_html_content or f"id='{anchor}'" in index_html_content, (
            f"Target anchor element '{anchor}' missing in index.html"
        )


def test_all_modals_exist_in_dom(index_html_content):
    modals = [
        'pahad-judge-overlay',
        'modal-data-truth-matrix',
        'modal-scientific-expl',
        'modal-historical-media',
        'weather-forecast-modal',
        'pahad-regional-drawer',
        'cap-modal',
        'citizen-report-modal',
        'modal-3d-terrain',
    ]
    for modal_id in modals:
        assert f'id="{modal_id}"' in index_html_content or f"id='{modal_id}'" in index_html_content, (
            f"Target modal container '{modal_id}' missing in index.html"
        )


def test_javascript_helpers_and_aliases(index_html_content):
    assert 'function toggleSidebarMenu' in index_html_content, "toggleSidebarMenu function missing"
    assert 'function navigateToPanel' in index_html_content, "navigateToPanel function missing"
    assert 'function eocHighlightPulse' in index_html_content, "eocHighlightPulse function missing"
    assert 'window.open3DTerrainModal =' in index_html_content, "open3DTerrainModal alias missing"
    assert "e.key === 'Escape'" in index_html_content or 'e.keyCode === 27' in index_html_content, (
        "Escape key handler for drawer closing missing"
    )


def test_css_pulse_and_active_classes_synchronized(theme_css_content, public_theme_css_content):
    for name, css in [('static', theme_css_content), ('public', public_theme_css_content)]:
        assert '.eoc-nav-item.active' in css, f".eoc-nav-item.active missing in {name} CSS"
        assert '.eoc-nav-highlighted' in css, f".eoc-nav-highlighted missing in {name} CSS"
        assert '@keyframes eocTargetPulse' in css, f"@keyframes eocTargetPulse missing in {name} CSS"
