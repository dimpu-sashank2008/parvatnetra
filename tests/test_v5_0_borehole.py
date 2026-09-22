# -*- coding: utf-8 -*-
"""
tests/test_v5_0_borehole.py
===========================
Phase V5.0 Test Suite: Geotechnical Borehole & ABS Casing Evidence Audit
"""

import pytest
from engine.physical_deployment_engine import (
    PhysicalDeploymentEngine,
    BoreholeRecord,
    BOREHOLE_NOT_DRILLED,
    CASING_NOT_INSTALLED,
    BOREHOLE_EVIDENCE_MISSING
)


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestBoreholeAndCasing:
    """Verifies that borehole and downhole casing records are strictly audited."""

    def test_borehole_record_specification(self, deployment_engine):
        bh = deployment_engine.audit_borehole_and_casing()
        assert isinstance(bh, BoreholeRecord)
        assert bh.borehole_id == "BH-NH10-KM48-01"
        assert bh.highway_km == 48.2
        assert bh.casing_depth_m == 25.0
        assert "ABS inclinometer casing" in bh.casing_type
        assert bh.casing_od_mm == 70.0
        assert bh.casing_id_mm == 60.0
        assert bh.slot_size_mm == 0.5
        assert "silica sand" in bh.filter_pack.lower()
        assert "bentonite-cement slurry" in bh.grouting_mix.lower()

    def test_borehole_lithology_strata(self, deployment_engine):
        bh = deployment_engine.audit_borehole_and_casing()
        assert len(bh.lithology) == 3
        # First layer: colluvium
        assert "colluvial" in bh.lithology[0]["stratum"].lower()
        # Second layer: phyllite
        assert "phyllite" in bh.lithology[1]["stratum"].lower()
        # Third layer: schist bedrock
        assert "schist" in bh.lithology[2]["stratum"].lower()

    def test_borehole_coordinates_and_water_table(self, deployment_engine):
        bh = deployment_engine.audit_borehole_and_casing()
        assert bh.coordinates["latitude"] == pytest.approx(27.2023, rel=1e-3)
        assert bh.coordinates["longitude"] == pytest.approx(88.5147, rel=1e-3)
        assert bh.coordinates["elevation_msl"] == pytest.approx(620.0, rel=1e-2)
        assert bh.water_table_depth_m == pytest.approx(8.5, rel=1e-2)

    def test_drilling_and_casing_status_not_installed(self, deployment_engine):
        bh = deployment_engine.audit_borehole_and_casing()
        assert bh.drilling_status == BOREHOLE_NOT_DRILLED
        assert bh.casing_status == CASING_NOT_INSTALLED
        assert bh.evidence_status == BOREHOLE_EVIDENCE_MISSING
        assert bh.completion_date is None
