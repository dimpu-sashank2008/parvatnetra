# -*- coding: utf-8 -*-
"""
tests/test_v5_1_kinematic_boundary.py
======================================
Tests the absolute boundary enforcement for the Kinematic IoT ML model.
In accordance with Phase V5.0 and V5.1 mandates:
- Kinematic ML model is strictly NOT_TRAINED_DATA_PENDING.
- Zero live field sensor telemetry exists.
- Zero borehole casing installations exist.
- No kinematic neural network weights file may be manufactured.
"""

import os
import glob
import pytest
from engine.scientific_truth_engine import GLOBAL_SCIENTIFIC_TRUTH_ENGINE


def test_kinematic_model_status_in_ledger():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    research_models = ledger.get("research_models", [])
    kinematic = next((m for m in research_models if m.get("model_id") == "PAHAD-Kinematic-IoT-ML-Model"), {})
    assert kinematic.get("status") == "NOT_TRAINED_DATA_PENDING"
    assert kinematic.get("weights_file") is None
    assert kinematic.get("field_data_available") is False


def test_no_manufactured_kinematic_weights():
    base_dir = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.base_dir
    models_dir = os.path.join(base_dir, "models")
    # Verify no trained kinematic weight files exist
    kinematic_weights = glob.glob(os.path.join(models_dir, "*kinematic*.*"))
    assert len(kinematic_weights) == 0, f"Found unexpected kinematic weights: {kinematic_weights}"


def test_physical_telemetry_state_zero():
    ledger = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_ledger()
    field_state = ledger.get("physical_field_telemetry_state", {})
    assert field_state.get("physical_sensors_verified") == 0
    assert field_state.get("borehole_casings_installed") == 0
    assert field_state.get("live_mountain_observations") == 0
    assert field_state.get("continuous_live_telemetry_hours") == 0.0


def test_engine_verdict_kinematic_boundary():
    verdict = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.evaluate_v5_1_verdict()
    assert verdict["kinematic_ml_status"] == "NOT_TRAINED_DATA_PENDING"


def test_model_inventory_kinematic_entry():
    inventory = GLOBAL_SCIENTIFIC_TRUTH_ENGINE.get_model_inventory()
    assert "kinematic_ml" in inventory
    assert inventory["kinematic_ml"]["status"] == "NOT_TRAINED_DATA_PENDING"
    assert inventory["kinematic_ml"]["weights"] is None
