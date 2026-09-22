# -*- coding: utf-8 -*-
"""
tests/test_v5_2_event_provenance.py
===================================
Phase V5.2 Test Suite: Event Source Provenance & Corroboration Traceability
"""

import pytest
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52EventProvenance:
    """Verifies that all canonical events trace to authoritative government sources."""

    def test_all_canonical_events_have_provenance_badge(self, manager):
        events = manager.list_canonical_events()
        for ev in events:
            assert ev["provenance"] == "[HISTORICAL]"
            assert ev["source"] is not None and len(ev["source"]) > 0
            assert ev["source_reference"] is not None and len(ev["source_reference"]) > 0

    def test_provenance_summary_no_synthetic_in_canonical(self, manager):
        prov = manager.get_provenance_summary()
        assert prov["synthetic_events_in_canonical"] == 0
        assert prov["physical_iot_in_situ_events"] == 0
        assert prov["total_canonical_events"] >= 42
        assert prov["canonical_negative_controls"] == 20

    def test_authoritative_sources_represented(self, manager):
        prov = manager.get_provenance_summary()
        sources = prov["source_breakdown"]
        # Must have GSI, BRO, and SDMA records represented
        has_gsi = any("GSI" in s or "Geological Survey" in s for s in sources)
        has_bro = any("BRO" in s or "Border Roads" in s for s in sources)
        has_sdma = any("SDMA" in s or "Disaster Management" in s for s in sources)
        assert has_gsi, "GSI source missing from canonical events"
        assert has_bro, "BRO source missing from canonical events"
        assert has_sdma, "SDMA source missing from canonical events"
