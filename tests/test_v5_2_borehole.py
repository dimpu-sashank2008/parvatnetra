# -*- coding: utf-8 -*-
"""
tests/test_v5_2_borehole.py
===========================
Phase V5.2 Test Suite: Borehole & Inclinometer Casing Evidence
Verifies that borehole design specifications are strictly separated from
field verification, and that casing status remains NOT_INSTALLED.
"""

import pytest
from engine.physical_deployment_engine import (
    GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE,
    BOREHOLE_NOT_DRILLED,
    CASING_NOT_INSTALLED
)


def test_borehole_status_not_drilled():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    bh = engine.audit_borehole_and_casing()
    assert bh.borehole_id == "BH-NH10-KM48-01"
    assert bh.drilling_status == BOREHOLE_NOT_DRILLED
    assert bh.casing_status == CASING_NOT_INSTALLED


def test_design_spec_separated_from_field_verification():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    bh = engine.audit_borehole_and_casing()
    # Design specification exists: 25.0m depth, 70mm OD ABS casing with 4-keyway grooves
    assert bh.casing_depth_m == 25.0
    assert bh.casing_od_mm == 70.0
    assert "4-keyway" in bh.casing_type
    # But field drilling/installation is unverified
    assert bh.field_verified is False


def test_zero_borehole_core_photographs_on_disk():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    bh = engine.audit_borehole_and_casing()
    assert len(bh.core_box_photos) == 0
