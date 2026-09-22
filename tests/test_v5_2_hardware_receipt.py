# -*- coding: utf-8 -*-
"""
tests/test_v5_2_hardware_receipt.py
===================================
Phase V5.2 Test Suite: Physical Hardware Receipt Gate
Verifies that software registry entries are not treated as physical receipt evidence,
and that hardware possession requires physical inspection and serial verification.
"""

import pytest
from engine.physical_deployment_engine import (
    GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE,
    STAGE_PLANNED,
    STAGE_BENCH_ACCEPTED
)


def test_hardware_receipt_distinguishes_software_from_physical():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    audits = engine.audit_sensor_hardware_provenance()
    assert len(audits) == 5

    # Sensors in ground must be 0
    verified_phys = sum(1 for a in audits.values() if a.device_physically_verified)
    assert verified_phys == 0, f"Expected 0 physically verified sensors, found {verified_phys}"


def test_receipt_statuses_reflect_unverified_field_presence():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    audits = engine.audit_sensor_hardware_provenance()
    for sensor_id, a in audits.items():
        if a.sensor_type == "GATEWAY":
            # Gateway has bench prototype
            assert a.installation_status in ["CONFIGURED_ONLY", "NOT_INSTALLED"]
        else:
            assert a.installation_status in ["NOT_INSTALLED", "PLANNED"]
            assert a.device_physically_verified is False


def test_no_manufactured_delivery_challans_treated_as_verified():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    audits = engine.audit_sensor_hardware_provenance()
    for a in audits.values():
        assert a.delivery_challan_verified is False
        assert a.nameplate_photo_verified is False
