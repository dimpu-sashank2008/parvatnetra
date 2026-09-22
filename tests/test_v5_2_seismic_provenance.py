# -*- coding: utf-8 -*-
"""
tests/test_v5_2_seismic_provenance.py
=====================================
Phase V5.2 Test Suite: Seismological Data Provenance & Anti-Relabeling Invariant
"""

import pytest
from engine.external_data_engine import ExternalDataEngine


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


class TestV52SeismicProvenance:
    """Verifies that seismic feeds maintain rigorous provenance and truthful fallback labeling."""

    def test_usgs_never_relabelled_as_ncs(self, engine):
        source = engine.get_source_by_id("SRC-USGS-FDSNWS")
        assert source is not None
        assert "United States Geological Survey" in source["organization"]
        assert "National Center for Seismology" not in source["organization"]

        ncs_audit = engine._audit_ncs_credentials()
        # Fallback must be explicitly declared as USGS
        assert "SRC-USGS-FDSNWS" in ncs_audit["fallback_provider"]
        assert ncs_audit["source_id"] != ncs_audit["fallback_provider"]

    def test_usgs_seismic_audit_structure(self, engine):
        res = engine._audit_usgs_seismic()
        assert res["source_id"] == "SRC-USGS-FDSNWS"
        assert res["status"] in {"LIVE", "DEGRADED", "UNAVAILABLE"}
        if res["status"] == "LIVE":
            assert res["provenance"] == "[LIVE]"
            assert res["records_received"] >= 0
