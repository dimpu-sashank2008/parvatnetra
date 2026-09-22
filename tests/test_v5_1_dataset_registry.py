# -*- coding: utf-8 -*-
"""
tests/test_v5_1_dataset_registry.py
===================================
Phase V5.1 Test Suite: Canonical Dataset Ledger & Sample Count Verification
"""

import os
import pytest
import pandas as pd
from engine.scientific_truth_engine import (
    ScientificTruthEngine,
    CANONICAL_EVENTS_COUNT,
    CANONICAL_CONTROLS_COUNT,
    CANONICAL_SEQUENCES_COUNT,
    CANONICAL_EVENT_SAMPLES_COUNT
)


@pytest.fixture
def truth_engine():
    return ScientificTruthEngine()


class TestDatasetRegistry:
    """Verifies that dataset counts on disk strictly match canonical ledger declarations."""

    def test_canonical_counts_declaration(self, truth_engine):
        counts = truth_engine.get_dataset_counts()
        assert counts["canonical_events"] == CANONICAL_EVENTS_COUNT == 17
        assert counts["canonical_controls"] == CANONICAL_CONTROLS_COUNT == 20
        assert counts["canonical_sequences"] == CANONICAL_SEQUENCES_COUNT == 105
        assert counts["canonical_event_model_samples"] == CANONICAL_EVENT_SAMPLES_COUNT == 36

    def test_raw_historical_events_file_on_disk(self, truth_engine):
        p = os.path.join(truth_engine.base_dir, "data", "raw", "historical_landslides_ner.csv")
        assert os.path.exists(p)
        df = pd.read_csv(p)
        assert len(df) == 17
        assert "EV-01" in df["event_id"].values
        assert "EV-17" in df["event_id"].values

    def test_historical_controls_file_on_disk(self, truth_engine):
        p = os.path.join(truth_engine.base_dir, "data", "processed", "lstm_v4_historical_controls.csv")
        assert os.path.exists(p)
        df = pd.read_csv(p)
        assert len(df) == 20

    def test_features_all_event_samples_on_disk(self, truth_engine):
        p = os.path.join(truth_engine.base_dir, "data", "features", "features_all.csv")
        assert os.path.exists(p)
        df = pd.read_csv(p)
        assert len(df) == 36

    def test_demo_dataset_strictly_quarantined(self, truth_engine):
        p = os.path.join(truth_engine.base_dir, "data", "features", "demo_train.csv")
        assert os.path.exists(p)
        df = pd.read_csv(p)
        assert len(df) == 25
