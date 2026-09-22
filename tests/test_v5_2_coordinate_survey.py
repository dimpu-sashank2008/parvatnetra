# -*- coding: utf-8 -*-
"""
tests/test_v5_2_coordinate_survey.py
====================================
Phase V5.2 Test Suite: Coordinate Survey Provenance Gate
Verifies that estimated coordinates are never labelled as surveyed coordinates,
and requires GNSS/RTK ground-truth survey evidence before claiming surveyed coordinates.
"""

import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_coordinate_survey_status_pending():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    survey = engine.audit_coordinate_survey()
    assert survey["status"] == "COORDINATE_SURVEY_PENDING"
    assert survey["surveyed_coordinates_count"] == 0
    assert survey["design_coordinates_count"] == 5


def test_no_estimated_coordinates_labelled_surveyed():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    survey = engine.audit_coordinate_survey()
    for node in survey["nodes"].values():
        assert node["coordinate_classification"] == "DESIGN_ESTIMATED"
        assert node["rtk_survey_verified"] is False
        assert node["surveyor_signature"] is None


def test_survey_reference_station_identified():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    survey = engine.audit_coordinate_survey()
    # Survey of India benchmark identified for future field ties
    assert "SOI-GTS-RANGPO-BM14" in survey["soi_benchmark_station"]
    assert survey["rtk_horizontal_tolerance_m"] <= 0.02
