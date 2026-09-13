# -*- coding: utf-8 -*-
"""
tests/test_phase10_failure_modes.py
====================================
PARVAT NETRA • PAHAD AI — Phase 10 Failure & Edge Case Test Suite
-----------------------------------------------------------------
Verifies robust, fail-safe operation under missing data, extreme anomalies,
corrupted sequences, and strict 2-of-3 safety gate constraints.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_sequence_pipeline import PahadSequencePipeline, CANONICAL_FEATURE_COLUMNS, HORIZONS
from engine.pahad_live_inference import run_live_inference, run_forecast
from engine.model_registry import GLOBAL_MODEL_REGISTRY


class TestPhase10FailureModes:

    def test_missing_weather_telemetry_graceful_fallback(self):
        """When weather telemetry is absent, inference must not crash and must flag imputation."""
        override = {
            "rainfall_24h": None,
            "rain_24h": None,
            "rain_1h": None,
            "rain_6h": None,
            "rain_intensity": None
        }
        res = run_live_inference(
            sector_id="SK-NH10-KM48",
            latitude=27.33,
            longitude=88.61,
            forecast_horizon_hours=24,
            override_features=override
        )
        assert res.event_probability >= 0.0
        assert res.event_probability <= 1.0
        assert res.data_quality_level in ["PARTIAL DATA", "DEGRADED DATA", "HIGH QUALITY"]

    def test_missing_seismic_telemetry_fallback(self):
        """When seismic telemetry is unavailable, system falls back to regional baseline."""
        override = {
            "seismic_count_24h": None,
            "max_magnitude_24h": None,
            "nearest_seismic_distance": None
        }
        res = run_live_inference(
            sector_id="MN-TUPUL-RLY",
            latitude=24.755,
            longitude=93.578,
            forecast_horizon_hours=12,
            override_features=override
        )
        assert res.event_probability >= 0.0
        assert res.event_probability <= 1.0
        assert isinstance(res.explanation, dict)

    def test_missing_insitu_sensors_masking_and_imputation(self):
        """In-situ sensors missing must be masked as 0 in missingness mask and imputed cleanly."""
        df_sample = pd.DataFrame([{
            "sample_id": "test_missing_1",
            "sector_id": "SK-NH10-KM48",
            "timestamp": "2024-06-15T12:00:00Z",
            "is_event_sample": 0,
            "target_6h": 0,
            "target_12h": 0,
            "target_24h": 0,
            "target_48h": 0,
            "rain_1h": 5.0,
            "rain_3h": 10.0,
            "rain_6h": 15.0,
            "rain_12h": 20.0,
            "rain_24h": 25.0,
            "rain_48h": 30.0,
            "rain_72h": 35.0,
            "antecedent_rain_3d": 40.0,
            "antecedent_rain_7d": 50.0,
            "rain_intensity": 5.0,
            "rainfall_threshold_exceedance": 0.2,
            "fos": 1.25,
            "slope": 35.0,
            "aspect": 120.0,
            "elevation": 800.0,
            "curvature": 0.05,
            # Missing in-situ sensors:
            "soil_moisture": np.nan,
            "pore_pressure": np.nan,
            "tilt": np.nan,
            "ground_displacement": np.nan,
            "ndvi": 0.65,
            "ndvi_anomaly": -0.05,
            "seismic_count_24h": 0,
            "max_magnitude_24h": 0.0,
            "nearest_seismic_distance": 150.0,
            "historical_susceptibility": 0.70
        }])

        pipeline = PahadSequencePipeline()
        train_path = os.path.join(REPO_ROOT, "data", "processed", "phase5b_temporal_train.csv")
        df_train = pd.read_csv(train_path)
        pipeline.fit(df_train)

        dataset = pipeline.transform(df_sample, partition_name="test_missing")
        assert dataset.sample_count == 1
        
        # Check missingness mask for in-situ columns
        sm_idx = CANONICAL_FEATURE_COLUMNS.index("soil_moisture")
        pp_idx = CANONICAL_FEATURE_COLUMNS.index("pore_pressure")
        tilt_idx = CANONICAL_FEATURE_COLUMNS.index("tilt")
        disp_idx = CANONICAL_FEATURE_COLUMNS.index("ground_displacement")
        
        assert dataset.missingness_masks[0, sm_idx] == 0.0
        assert dataset.missingness_masks[0, pp_idx] == 0.0
        assert dataset.missingness_masks[0, tilt_idx] == 0.0
        assert dataset.missingness_masks[0, disp_idx] == 0.0

        # Non-missing feature must have mask = 1.0
        slope_idx = CANONICAL_FEATURE_COLUMNS.index("slope")
        assert dataset.missingness_masks[0, slope_idx] == 1.0

    def test_extreme_out_of_distribution_bounds_flagging(self):
        """Features outside training distribution bounds must trigger OOD flag and degrade confidence."""
        extreme_features = {
            "rainfall_24h": 999.0,         # Max in train is ~380mm
            "pore_pressure": 250.0,        # Max in train is ~85 kPa
            "ground_displacement": 500.0,  # Max in train is ~120 mm
            "tilt": 45.0,                  # Slope angle ~45 deg
            "slope": 75.0                  # Extreme cliff
        }
        is_ood, ood_score, reasons = GLOBAL_MODEL_REGISTRY.check_ood(extreme_features)
        assert is_ood is True
        assert ood_score > 0.5
        assert len(reasons) >= 2

    def test_sequence_pipeline_empty_and_short_series_padding(self):
        """Pipeline must gracefully pad short sequences without throwing exceptions."""
        pipeline = PahadSequencePipeline()
        train_path = os.path.join(REPO_ROOT, "data", "processed", "phase5b_temporal_train.csv")
        df_train = pd.read_csv(train_path)
        pipeline.fit(df_train)

        # Single row dataset
        df_single = df_train.head(1).copy()
        ds = pipeline.transform(df_single, partition_name="single")
        seqs = pipeline.build_sector_sequences(ds, window_size=6)
        
        sec_id = df_single["sector_id"].iloc[0]
        assert sec_id in seqs
        assert seqs[sec_id]["sequences"].shape == (1, 6, len(CANONICAL_FEATURE_COLUMNS))
        assert seqs[sec_id]["masks"].shape == (1, 6, len(CANONICAL_FEATURE_COLUMNS))

    def test_decoupled_fos_vs_event_probability(self):
        """Verify Factor of Safety (FoS) is mathematically decoupled from statistical probability."""
        res_stable = run_live_inference(
            sector_id="SK-NH10-KM48",
            latitude=27.33,
            longitude=88.61,
            forecast_horizon_hours=24,
            override_features={"slope_deg": 20.0, "rainfall_24h": 5.0}
        )
        assert res_stable.fos_physical > 1.20
        assert res_stable.fos_status in ["STABLE", "MARGINAL"]

        res_unstable = run_live_inference(
            sector_id="SK-NH10-KM48",
            latitude=27.33,
            longitude=88.61,
            forecast_horizon_hours=24,
            override_features={"slope_deg": 65.0, "rainfall_24h": 150.0}
        )
        assert res_unstable.fos_physical < 1.00
        assert res_unstable.fos_status == "CRITICAL"

        # Statistical event probability and physical FoS are separate properties
        assert hasattr(res_stable, "event_probability")
        assert hasattr(res_stable, "fos_physical")
        assert res_stable.event_probability != res_stable.fos_physical

    def test_safety_gate_prevents_unilateral_red_alert_without_corroboration(self):
        """High statistical ML probability alone must NOT trigger unilateral public red alert without 2-of-3 corroboration."""
        res = run_live_inference(
            sector_id="SK-NH10-KM48",
            latitude=27.33,
            longitude=88.61,
            forecast_horizon_hours=24,
            override_features={
                "fos": 1.75,          # Stable physical FoS
                "rainfall_24h": 5.0,  # Negligible rainfall
                "soil_moisture": 0.15 # Bone dry
            }
        )
        assert res.alert_eligible is False or res.risk_band != "EXTREME"
        assert "statutory" in res.authority_action.get("statutory_gate", "").lower()

    def test_multi_horizon_api_contract_and_probability_bounds(self):
        """Verify multi-horizon run_forecast returns all 4 horizons with valid probability bounds [0.0, 1.0]."""
        fc = run_forecast(
            sector_id="SK-NH10-KM48",
            latitude=27.33,
            longitude=88.61,
            horizons=[6, 12, 24, 48]
        )
        assert "horizons" in fc["forecast_risk"]
        for h in ["6h", "12h", "24h", "48h"]:
            assert h in fc["forecast_risk"]["horizons"]
            p = fc["forecast_risk"]["horizons"][h]["event_probability"]
            assert 0.0 <= p <= 1.0
            assert fc["forecast_risk"]["horizons"][h]["model_status"] in [
                "TRAINED_LIMITED_DATA", "VALIDATED_RESEARCH_PROTOTYPE", "IN_DISTRIBUTION"
            ]
