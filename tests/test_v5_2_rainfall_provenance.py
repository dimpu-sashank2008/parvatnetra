# -*- coding: utf-8 -*-
"""
tests/test_v5_2_rainfall_provenance.py
======================================
Phase V5.2 Test Suite: Precipitation Data Provenance & Anti-Relabeling Invariant
"""

import pytest
from engine.external_data_engine import ExternalDataEngine, STATUS_LIVE
from engine.dataset_expansion_manager import DatasetExpansionManager


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


@pytest.fixture
def manager():
    return DatasetExpansionManager.get_instance()


class TestV52RainfallProvenance:
    """Verifies that rainfall sources are never relabeled and maintain rigorous provenance."""

    def test_open_meteo_never_relabelled_as_imd(self, engine):
        source = engine.get_source_by_id("SRC-OPEN-METEO")
        assert source is not None
        assert "Open-Meteo" in source["organization"]
        assert "India Meteorological Department" not in source["organization"]

        imd_audit = engine._audit_imd_credentials()
        # Fallback must be explicitly declared as Open-Meteo
        assert "SRC-OPEN-METEO" in imd_audit["fallback_provider"]
        assert imd_audit["source_id"] != imd_audit["fallback_provider"]

    def test_historical_event_rainfall_context_provenance(self, manager):
        events = manager.list_canonical_events()
        for ev in events:
            rf = ev.get("rainfall_context")
            if rf:
                assert "rainfall_24h_mm" in rf
                assert rf["rainfall_24h_mm"] >= 0.0
                # If source is documented, verify it is realistic
                src = rf.get("source", "")
                if src:
                    assert any(valid in src for valid in ["Open-Meteo", "IMD", "Reanalysis", "Historical"])
