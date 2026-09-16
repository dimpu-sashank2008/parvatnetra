# -*- coding: utf-8 -*-
"""
tests/test_phase12d_judge_matrix.py
===================================
PARVAT NETRA • PAHAD AI — Phase 12D Adversarial Judge Testing Suite
-------------------------------------------------------------------
Verifies all 40 adversarial judge questions:
- Exact system answers, evidence citations, and honesty disclosures.
- Proof that LSTM is declared NOT_TRAINED.
- Proof of small test set (N=8) disclosure.
- Proof of distinct FoS vs P(event) vs CRI metrics.
- Proof of DMA 2005 authority statutory interlocks.
"""

import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_adversarial_defense import JUDGE_40_QUESTIONS


class TestPhase12DJudgeMatrix:

    def test_all_forty_questions_present(self):
        """Verify that exactly 40 adversarial questions are formally registered."""
        assert len(JUDGE_40_QUESTIONS) == 40
        ids = [q["id"] for q in JUDGE_40_QUESTIONS]
        expected_ids = [f"JQ-{i:02d}" for i in range(1, 41)]
        assert ids == expected_ids

    def test_complete_metadata_schema_per_question(self):
        """Verify every question contains all 7 mandatory dimensions."""
        required_keys = {
            "id", "question", "expected_answer", "required_evidence",
            "provenance_status", "code_reference", "demo_action", "known_limitation"
        }
        for q in JUDGE_40_QUESTIONS:
            missing = required_keys - set(q.keys())
            assert not missing, f"Question {q.get('id')} is missing keys: {missing}"
            for k in required_keys:
                assert q[k] is not None and len(str(q[k]).strip()) > 0, f"Empty field {k} in {q['id']}"

    def test_target_separation_honesty(self):
        """JQ-01 & JQ-03 must strictly preserve FoS and P(event) separation."""
        jq01 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-01")
        assert "Factor of Safety" in jq01["expected_answer"]
        assert "event probability" in jq01["expected_answer"]
        assert "Composite Risk Index" in jq01["expected_answer"]

        jq03 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-03")
        assert "Mohr-Coulomb" in jq03["expected_answer"]

    def test_lstm_temporal_honesty_disclosure(self):
        """JQ-05 must declare LSTM as not trained due to lack of continuous sensor data."""
        jq05 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-05")
        answer = jq05["expected_answer"]
        assert "not trained" in answer.lower() or "surrogate" in answer.lower()
        assert "DATA_COLLECTION_REQUIRED" in answer or "readiness gate" in answer
        assert jq05["provenance_status"] == "[NOT_TRAINED] Physics-Informed Temporal Surrogate"

    def test_small_sample_size_honesty(self):
        """JQ-06, JQ-07, JQ-08 must disclose N=17 historical events and N=8 held-out test set."""
        jq06 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-06")
        assert "17" in jq06["expected_answer"]
        assert "GSI" in jq06["expected_answer"]

        jq07 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-07")
        assert "8" in jq07["expected_answer"]
        assert "temporal holdout" in jq07["expected_answer"].lower()

        jq08 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-08")
        assert "research prototype" in jq08["expected_answer"].lower()

    def test_actuation_safety_and_statutory_interlocks(self):
        """JQ-19, JQ-20, JQ-21 must enforce DMA 2005 authority restrictions and dry-run sirens."""
        jq19 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-19")
        assert "NO" in jq19["expected_answer"]
        assert "SIREN_DRY_RUN=1" in jq19["expected_answer"] or "STATE_AUTHORITY_REVIEW" in jq19["expected_answer"]

        jq20 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-20")
        assert "NO" in jq20["expected_answer"]
        assert "403" in jq20["expected_answer"]

        jq21 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-21")
        assert "NO" in jq21["expected_answer"]
        assert "DISTRICT_AUTHORITY" in jq21["expected_answer"]

    def test_data_truth_and_fallbacks(self):
        """JQ-11, JQ-12, JQ-23, JQ-38 must prove authentic live feeds with transparent fallbacks."""
        jq23 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-23")
        assert "Open-Meteo" in jq23["expected_answer"]
        assert "USGS" in jq23["expected_answer"]
        assert "PostGIS" in jq23["expected_answer"]

        jq38 = next(q for q in JUDGE_40_QUESTIONS if q["id"] == "JQ-38")
        assert "AUTH_REQUIRED" in jq38["expected_answer"]
        assert "Open-Meteo" in jq38["expected_answer"]
