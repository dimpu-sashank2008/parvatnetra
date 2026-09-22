# -*- coding: utf-8 -*-
"""
tests/test_v5_1_dataset_reconciliation.py
==========================================
Phase V5.1 Test Suite: Dataset Lineage Reconciliation
Verifies canonical sample counts, hashes, and demotion of unsupported counts.
"""

import os
import pytest
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


class TestV51DatasetReconciliation:
    """Verifies dataset lineage and counts across historical records."""

    def test_canonical_counts_in_truth_engine(self, truth_engine):
        counts = truth_engine.get_dataset_counts()
        assert counts["canonical_events"] == CANONICAL_EVENTS_COUNT == 17
        assert counts["canonical_controls"] == CANONICAL_CONTROLS_COUNT == 20
        assert counts["canonical_sequences"] == CANONICAL_SEQUENCES_COUNT == 105
        assert counts["canonical_event_model_samples"] == CANONICAL_EVENT_SAMPLES_COUNT == 36

    def test_raw_historical_events_file_on_disk(self, truth_engine):
        raw_events_path = os.path.join(truth_engine.base_dir, "data", "raw", "historical_landslides_ner.csv")
        assert os.path.exists(raw_events_path), f"File missing: {raw_events_path}"
        with open(raw_events_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        # Header + 17 events = 18 lines
        assert len(lines) == 18, f"Expected 17 events (18 lines), found {len(lines)}"

    def test_historical_controls_file_on_disk(self, truth_engine):
        controls_path = os.path.join(truth_engine.base_dir, "data", "processed", "lstm_v4_historical_controls.csv")
        assert os.path.exists(controls_path), f"File missing: {controls_path}"
        with open(controls_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        # Header + 20 controls = 21 lines
        assert len(lines) == 21, f"Expected 20 controls (21 lines), found {len(lines)}"

    def test_features_all_event_samples_on_disk(self, truth_engine):
        features_path = os.path.join(truth_engine.base_dir, "data", "features", "features_all.csv")
        assert os.path.exists(features_path), f"File missing: {features_path}"
        with open(features_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        # Header + 36 samples = 37 lines
        assert len(lines) == 37, f"Expected 36 samples (37 lines), found {len(lines)}"

    def test_unsupported_counts_demoted(self, truth_engine):
        conflicts = truth_engine.get_conflict_matrix()
        c1 = next((c for c in conflicts if c["conflict_id"] == "CONF-01"), None)
        assert c1 is not None
        assert "52 Real Historical Events" in c1["later_claim"]
        assert "17" in c1["resolution"]
        assert "UNSUPPORTED" in c1["resolution"]

        c2 = next((c for c in conflicts if c["conflict_id"] == "CONF-02"), None)
        assert c2 is not None
        assert "41 Train, 11 Val, 11 Test" in c2["later_claim"]
        assert "16 Train, 12 Val, 8 Test" in c2["resolution"]
        assert "UNSUPPORTED" in c2["resolution"]
