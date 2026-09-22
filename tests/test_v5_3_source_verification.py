# -*- coding: utf-8 -*-
"""
tests/test_v5_3_source_verification.py
======================================
Phase V5.3 Test Suite: External Source Verification & Provider Existence Audit
Verifies that institutional citations correspond to recognized agencies,
authentic citation references, and honest provider connectivity states.
"""

import os
import json
import pytest
from engine.external_data_engine import ExternalDataEngine, STATUS_LIVE, STATUS_AUTH_REQUIRED, STATUS_CACHED, STATUS_UNAVAILABLE


@pytest.fixture
def ext_engine():
    return ExternalDataEngine.get_instance()


class TestV53SourceVerification:
    """Verifies that all claimed data sources exist and maintain honest access states."""

    def test_total_sources_audited_and_classified(self, ext_engine):
        sources = ext_engine.list_sources()
        assert len(sources) == 12

    def test_institutional_agencies_registered(self, ext_engine):
        source_ids = {s["source_id"] for s in ext_engine.list_sources()}
        expected_agencies = {
            "SRC-GSI-NLSM", "SRC-BRO-PROJECTS", "SRC-SDMA-NER",
            "SRC-IMD-NOWCAST", "SRC-NCS-SEISMIC", "SRC-ISRO-NRSC-BHOONIDHI",
            "SRC-ESA-COPERNICUS-CDSE", "SRC-CWC-TEESTA", "SRC-POSTGIS-NEON",
            "SRC-OPEN-METEO", "SRC-USGS-FDSNWS", "SRC-PHYSICAL-IOT-KM48"
        }
        assert expected_agencies.issubset(source_ids)

    def test_zero_fabricated_credentials(self, ext_engine):
        # Auth-required sources must remain AUTH_REQUIRED unless legitimate token provided
        imd = ext_engine.get_source("SRC-IMD-NOWCAST")
        ncs = ext_engine.get_source("SRC-NCS-SEISMIC")
        bhoonidhi = ext_engine.get_source("SRC-ISRO-NRSC-BHOONIDHI")
        copernicus = ext_engine.get_source("SRC-ESA-COPERNICUS-CDSE")

        assert imd["status"] == STATUS_AUTH_REQUIRED
        assert ncs["status"] == STATUS_AUTH_REQUIRED
        assert bhoonidhi["status"] == STATUS_AUTH_REQUIRED
        assert copernicus["status"] == STATUS_AUTH_REQUIRED

    def test_source_conflicts_resolved_and_tracked(self, ext_engine):
        conflicts = ext_engine._conflicts
        assert len(conflicts) >= 4
        for c in conflicts:
            rec = c.to_dict()
            assert rec["status"] == "RESOLVED"
            assert rec["confidence"] >= 0.90
            assert rec["resolution_method"]
