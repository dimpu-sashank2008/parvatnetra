# -*- coding: utf-8 -*-
"""
tests/test_v5_0_coordinate_survey.py
====================================
Phase V5.0 Test Suite: GNSS Coordinate Survey Provenance & Accuracy Audit
"""

import pytest
from engine.physical_deployment_engine import PhysicalDeploymentEngine


@pytest.fixture
def deployment_engine():
    return PhysicalDeploymentEngine()


class TestCoordinateSurvey:
    """Verifies GNSS survey benchmark, planned coordinates, and RTK accuracy standards."""

    def test_coordinate_survey_specification(self, deployment_engine):
        survey = deployment_engine.audit_coordinate_survey()
        assert survey["corridor_id"] == "CORR-NH10-SIKKIM-KM48"
        assert survey["benchmark_station"] == "SOI-GTS-RANGPO-BM14"
        assert survey["benchmark_elevation_msl"] == pytest.approx(612.45, rel=1e-2)
        assert survey["survey_status"] == "PENDING_FIELD_SURVEY"

    def test_planned_sensor_coordinates(self, deployment_engine):
        survey = deployment_engine.audit_coordinate_survey()
        coords = survey["planned_coordinates"]
        assert "BH-NH10-KM48-01" in coords
        bh = coords["BH-NH10-KM48-01"]
        assert bh["lat"] == pytest.approx(27.2023, rel=1e-3)
        assert bh["lon"] == pytest.approx(88.5147, rel=1e-3)
        assert bh["elevation_msl"] == pytest.approx(620.0, rel=1e-2)

    def test_rtk_accuracy_tolerances(self, deployment_engine):
        survey = deployment_engine.audit_coordinate_survey()
        tol = survey["accuracy_tolerance_m"]
        assert tol["horizontal_rtk_m"] <= 0.02
        assert tol["vertical_rtk_m"] <= 0.05
        assert tol["max_allowable_m"] == 0.05

    def test_physical_survey_evidence_missing(self, deployment_engine):
        survey = deployment_engine.audit_coordinate_survey()
        assert survey["survey_evidence_found"] is False
        assert survey["rinex_logs_present"] is False
        assert survey["surveyor_signoff"] is None
