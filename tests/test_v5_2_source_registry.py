# -*- coding: utf-8 -*-
"""
tests/test_v5_2_source_registry.py
==================================
Phase V5.2 Test Suite: External Source Registry Completeness & Metadata Audit
"""

import pytest
from engine.external_data_engine import ExternalDataEngine, ExternalSourceRecord


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


class TestV52SourceRegistry:
    """Verifies that all 12 authoritative external providers are properly cataloged."""

    EXPECTED_SOURCE_IDS = {
        "SRC-GSI-NLSM",
        "SRC-ISRO-NRSC-BHOONIDHI",
        "SRC-IMD-NOWCAST",
        "SRC-OPEN-METEO",
        "SRC-NCS-SEISMIC",
        "SRC-USGS-FDSNWS",
        "SRC-ESA-COPERNICUS-CDSE",
        "SRC-SDMA-NER",
        "SRC-BRO-PROJECTS",
        "SRC-CWC-TEESTA",
        "SRC-POSTGIS-NEON",
        "SRC-PHYSICAL-IOT-KM48"
    }

    def test_all_twelve_sources_registered(self, engine):
        sources = engine.get_source_registry()
        registered_ids = {s["source_id"] for s in sources}
        assert registered_ids == self.EXPECTED_SOURCE_IDS, (
            f"Expected exactly 12 authoritative sources. Missing: {self.EXPECTED_SOURCE_IDS - registered_ids}, "
            f"Extra: {registered_ids - self.EXPECTED_SOURCE_IDS}"
        )

    def test_source_record_metadata_completeness(self, engine):
        sources = engine.get_source_registry()
        required_fields = [
            "source_id", "organization", "source_type", "url_reference",
            "access_method", "authentication_state", "coverage",
            "temporal_range", "geographic_range", "license_notes",
            "retrieval_timestamp", "status", "description"
        ]
        for src in sources:
            for f in required_fields:
                assert f in src and src[f], f"Source {src.get('source_id')} missing required field: {f}"

    def test_get_source_by_id(self, engine):
        for sid in self.EXPECTED_SOURCE_IDS:
            rec = engine.get_source_by_id(sid)
            assert rec is not None
            assert rec["source_id"] == sid

    def test_nonexistent_source_returns_none(self, engine):
        assert engine.get_source_by_id("SRC-NONEXISTENT") is None
