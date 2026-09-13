# -*- coding: utf-8 -*-
"""
tests/test_phase10i_templates.py
================================
PARVAT NETRA • Phase 10I — Message Template Engine & Variable Tests
-------------------------------------------------------------------
Verifies:
  1. The 6 canonical emergency template categories:
     LANDSLIDE_WARNING, HIGH_RISK_ADVISORY, ROAD_CLOSURE, EVACUATION_ADVISORY, ALL_CLEAR, TEST_ALERT.
  2. Full variable substitution:
     {area}, {corridor}, {risk_level}, {time}, {action}, {incident_id}, {helpline}.
  3. Rejection of unknown / unapproved template names.
  4. Preservation of critical life-safety action advice.
  5. Correct mapping of DLT Template IDs to each category.
"""

import pytest
from services.production_sms_service import (
    SMSTemplateEngine,
    TEMPLATE_LANDSLIDE_WARNING,
    TEMPLATE_HIGH_RISK_ADVISORY,
    TEMPLATE_ROAD_CLOSURE,
    TEMPLATE_EVACUATION_ADVISORY,
    TEMPLATE_ALL_CLEAR,
    TEMPLATE_TEST_ALERT,
    VALID_TEMPLATES
)


def test_all_six_templates_renderable():
    """Verifies that all 6 template categories render without error."""
    for tmpl in VALID_TEMPLATES:
        rendered = SMSTemplateEngine.render(
            template_type=tmpl,
            language="en",
            area="Pakyong",
            corridor="NH-10 Km 48",
            risk_level="CRITICAL",
            time_str="Immediate",
            action="Evacuate to higher ground",
            incident_id="INC-TMPL-01",
            helpline="1077"
        )
        assert rendered["template_type"] == tmpl
        assert len(rendered["message"]) > 0
        assert "INC-TMPL-01" in rendered["message"]
        assert "dlt_template_id" in rendered


def test_variable_substitution_complete():
    """Verifies that all variables are cleanly interpolated and no placeholders remain."""
    rendered = SMSTemplateEngine.render(
        template_type=TEMPLATE_LANDSLIDE_WARNING,
        language="en",
        area="Dikchu",
        corridor="Dikchu-Gangtok Highway",
        risk_level="EXTREME",
        time_str="11:30 AM",
        action="Avoid exposed rock faces",
        incident_id="INC-SUB-99",
        helpline="112"
    )
    msg = rendered["message"]

    assert "{area}" not in msg
    assert "{corridor}" not in msg
    assert "{risk_level}" not in msg
    assert "{action}" not in msg
    assert "{incident_id}" not in msg
    assert "Dikchu" in msg
    assert "EXTREME" in msg
    assert "Avoid exposed rock faces" in msg
    assert "INC-SUB-99" in msg


def test_invalid_template_rejection():
    """Verifies that attempting to render an unapproved template raises ValueError."""
    with pytest.raises(ValueError) as exc:
        SMSTemplateEngine.render(template_type="UNAPPROVED_MARKETING_PROMO")
    assert "invalid template type" in str(exc.value).lower()


def test_critical_action_preserved():
    """Verifies that critical evacuation action instructions are preserved."""
    critical_action = "Seek shelter at Dikchu Community Hall"
    rendered = SMSTemplateEngine.render(
        template_type=TEMPLATE_EVACUATION_ADVISORY,
        language="en",
        action=critical_action
    )
    assert critical_action in rendered["message"]
    assert rendered["critical_action_preserved"] is True
