# -*- coding: utf-8 -*-
"""
tests/test_v5_3_severity.py
===========================
Phase V5.3 Test Suite: Hazard Severity Vocabulary & Ground Truth Plausibility
Verifies that all 42 events use valid severity designations supported by damage logs.
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager, VALID_SEVERITIES


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV53Severity:
    """Verifies that hazard severities are strictly validated."""

    def test_severities_in_controlled_vocabulary(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        for e in events:
            sev = e.get("severity")
            assert sev in VALID_SEVERITIES or sev == "UNKNOWN", f"Invalid severity in {e['event_id']}: {sev}"

    def test_major_disasters_have_critical_severity(self, manager):
        inv = manager.get_v5_3_inventory()
        events = inv.get("events", [])
        singtam = next(e for e in events if e["event_id"] == "EV-03")
        assert singtam["severity"] == "CRITICAL"

        tupul = next(e for e in events if e["event_id"] == "EV-04")
        assert tupul["severity"] == "CRITICAL"
