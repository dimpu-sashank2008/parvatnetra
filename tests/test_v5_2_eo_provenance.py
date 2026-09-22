# -*- coding: utf-8 -*-
"""
tests/test_v5_2_eo_provenance.py
================================
Phase V5.2 Test Suite: Earth Observation & Remote Sensing Data Provenance
"""

import pytest
from engine.external_data_engine import ExternalDataEngine


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


class TestV52EOProvenance:
    """Verifies that Earth Observation data (Copernicus, InSAR, Bhoonidhi) is strictly tracked."""

    def test_copernicus_cdse_registration(self, engine):
        src = engine.get_source_by_id("SRC-ESA-COPERNICUS-CDSE")
        assert src is not None
        assert "European Space Agency" in src["organization"]
        assert "Sentinel-1" in src["description"]

        cop_audit = engine._audit_copernicus_cdse()
        assert cop_audit["catalog_discovery"] == "METADATA_DISCOVERY_CAPABLE"
        assert "GLO-30" in cop_audit["local_raster_cache"]

    def test_bhoonidhi_mou_requirement_tracked(self, engine):
        src = engine.get_source_by_id("SRC-ISRO-NRSC-BHOONIDHI")
        assert src is not None
        assert "National Remote Sensing Centre" in src["organization"]

        bhoo_audit = engine._audit_bhoonidhi_credentials()
        assert "MOU Required" in bhoo_audit["mou_requirement"]
