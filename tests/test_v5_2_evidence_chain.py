# -*- coding: utf-8 -*-
"""
tests/test_v5_2_evidence_chain.py
=================================
Phase V5.2 Test Suite: Field Evidence Chain & Manifest Integrity
Verifies the cryptographic lineage, manifest schemas, and tamper-resistance
of the field commissioning evidence package.
"""

import os
import json
import pytest
from engine.physical_deployment_engine import GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE


def test_field_commissioning_manifest_exists_and_valid():
    base_dir = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE.base_dir
    manifest_path = os.path.join(base_dir, "data", "processed", "v5_2_field_commissioning_manifest.json")
    assert os.path.exists(manifest_path), f"Missing manifest: {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_version"] == "5.2.0"
    assert data["phase"] == "V5.2"
    assert data["overall_verdict"] == "V5_2_PHYSICAL_DEPLOYMENT_PENDING"
    assert data["registered_sensor_count"] == 5
    assert data["hardware_received_count"] == 0
    assert data["installed_sensor_count"] == 0
    assert data["calibration_status"] == "CALIBRATION_EVIDENCE_MISSING"
    assert data["borehole_status"] == "NOT_INSTALLED"


def test_live_telemetry_manifest_exists_and_valid():
    base_dir = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE.base_dir
    manifest_path = os.path.join(base_dir, "data", "processed", "v5_2_live_telemetry_manifest.json")
    assert os.path.exists(manifest_path), f"Missing manifest: {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_version"] == "5.2.0"
    assert data["phase"] == "PHASE_V5_2_CONTROLLED_PHYSICAL_PILOT_COMMISSIONING"
    assert data["telemetry_counts"]["live_mountain_observations"] == 0
    assert data["telemetry_counts"]["bench_observations"] == 8640
    assert data["continuity_and_burn_in"]["longest_continuous_live_hours"] == 0.0


def test_result_report_exists_and_matches_verdict():
    base_dir = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE.base_dir
    result_path = os.path.join(base_dir, "reports", "pahad_v5_2_result.json")
    assert os.path.exists(result_path), f"Missing result: {result_path}"

    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["phase"] == "V5.2"
    assert data["overall_verdict"] == "V5_2_PHYSICAL_DEPLOYMENT_PENDING"
    assert data["cryptographic_isolation"]["v3_hash_before"] == "7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183"
