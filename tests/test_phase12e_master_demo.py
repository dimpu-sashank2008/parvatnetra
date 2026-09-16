# -*- coding: utf-8 -*-
"""
tests/test_phase12e_master_demo.py
==================================
PARVAT NETRA • PAHAD AI — Phase 12E Master SIH Top-1 Demo Test Suite
---------------------------------------------------------------------
Verifies:
1. Demo manifest schema, structure, and data integrity.
2. GET /api/pahad/demo/scenario endpoint contract.
3. GET /api/pahad/demo/top10-judge-qa endpoint & scientific honesty constraints.
4. Deterministic 12-stage timeline continuity (0:00 to 5:00).
5. Safe failure injection & recovery simulation endpoints.
6. Canonical corridor (SK-NH10-KM48) telemetry & 2-of-3 corroboration state.
7. Strict statutory safety interlocks (DMA 2005, NDMA).
8. Voice AI emergency actuation rejection (REJECTED_SAFETY).
9. UI Judge Defense Overlay components in templates/index.html.
"""

import os
import sys
import json
import pytest

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

os.environ["PARVAT_TESTING"] = "1"
os.environ["ENABLE_PUBLIC_DISPATCH"] = "0"
os.environ["SIREN_DRY_RUN"] = "1"
os.environ["PUBLIC_DEMO_TEST_ONLY"] = "1"

from app import app
from engine.pahad_master_demo import (
    PahadMasterDemoEngine,
    TOP_10_JUDGE_QUESTIONS,
    MASTER_DEMO_TIMELINE
)
from services.pahad_voice_assistant import PahadVoiceAssistantService



@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestPhase12EMasterDemoManifest:
    """Verifies manifest schema, structure, and completeness."""

    def test_demo_manifest_schema_and_integrity(self):
        manifest = PahadMasterDemoEngine.get_demo_manifest()
        assert manifest["manifest_version"] == "1.0.0"
        assert manifest["phase"] == "PHASE_12E"
        assert manifest["demo_id"] == "SIH_TOP1_EOC_MASTER_DEMO"
        assert "target_duration_minutes" in manifest

        # Regional coverage (all 8 NER states)
        states = manifest["regional_coverage"]["states"]
        assert len(states) == 8
        assert "Sikkim" in states
        assert "Arunachal Pradesh" in states
        assert "Assam" in states
        assert "Meghalaya" in states
        assert "Manipur" in states
        assert "Mizoram" in states
        assert "Nagaland" in states
        assert "Tripura" in states
        assert manifest["regional_coverage"]["zero_auto_zoom_enforced"] is True

        # Timeline has 12 stages
        timeline = manifest["timeline"]
        assert len(timeline) == 12

        # Top 10 Judge Q&A
        top_qa = manifest["top_10_judge_defense_qa"]
        assert len(top_qa) == 10

        # Safety assertions
        safety = manifest["safety_assertions"]
        assert safety["is_safe"] is True
        assert safety["invariants"]["ENABLE_PUBLIC_DISPATCH"] == 0
        assert safety["invariants"]["SIREN_DRY_RUN"] == 1
        assert safety["invariants"]["PUBLIC_DEMO_TEST_ONLY"] == 1

    def test_disk_manifest_file_exists_and_matches(self):
        manifest_path = os.path.join(REPO_ROOT, "data", "manifests", "phase12e_master_demo.json")
        assert os.path.exists(manifest_path), f"Manifest file missing: {manifest_path}"
        with open(manifest_path, "r", encoding="utf-8") as f:
            disk_manifest = json.load(f)
        assert disk_manifest["demo_id"] == "SIH_TOP1_EOC_MASTER_DEMO"
        assert len(disk_manifest["timeline"]) == 12
        assert len(disk_manifest["top_10_judge_defense_qa"]) == 10


class TestPhase12EApiEndpoints:
    """Verifies REST API endpoints exposed for master demo."""

    def test_demo_scenario_endpoint(self, client):
        res = client.get("/api/pahad/demo/scenario")
        assert res.status_code == 200
        data = res.get_json()
        assert data["demo_id"] == "SIH_TOP1_EOC_MASTER_DEMO"
        assert data["canonical_corridor"]["corridor_id"] == "SK-NH10-KM48"
        assert len(data["timeline"]) == 12
        assert len(data["top_10_judge_defense_qa"]) == 10

    def test_top10_judge_qa_endpoint(self, client):
        res = client.get("/api/pahad/demo/top10-judge-qa")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "SUCCESS"
        assert data["count"] == 10
        questions = data["questions"]
        assert len(questions) == 10

        # Verify JQ-01 through JQ-10 IDs are present
        q_ids = [q["id"] for q in questions]
        for i in range(1, 11):
            assert f"JQ-{i:02d}" in q_ids

    def test_simulate_failure_and_recovery_flow(self, client):
        # 1. Simulate NWP outage
        res1 = client.post("/api/pahad/demo/simulate-failure", json={
            "action": "simulate",
            "provider": "open-meteo"
        })
        assert res1.status_code == 200
        data1 = res1.get_json()
        assert data1["action"] == "SIMULATE_FAILURE"
        assert data1["simulation_active"] is True
        assert data1["degraded_state"]["status"] == "OUTAGE / FALLBACK_ENGAGED"
        assert data1["degraded_state"]["confidence_after"] == "LOW_CONFIDENCE"
        assert data1["degraded_state"]["crash_prevented"] is True

        # 2. Restore provider
        res2 = client.post("/api/pahad/demo/simulate-failure", json={
            "action": "restore"
        })
        assert res2.status_code == 200
        data2 = res2.get_json()
        assert data2["action"] == "RESTORE_FAILURE"
        assert data2["simulation_active"] is False
        assert data2["restored_state"]["status"] == "ONLINE"
        assert data2["restored_state"]["confidence"] == "MODERATE"


class TestPhase12ETop10JudgeDefense:
    """Verifies scientific honesty and defensive rigor across all 10 judge questions."""

    def test_jq01_pahad_ai_dual_engine(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-01")
        assert "PAHAD AI" in q["question"]
        assert "Mohr-Coulomb" in q["detailed_defense"]
        assert "FoS" in q["detailed_defense"]
        assert "GradientBoostingClassifier" in q["detailed_defense"]
        assert "TRAINED_LIMITED_DATA" in q["known_limitation"]

    def test_jq02_cri_multi_criteria(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-02")
        assert "CRI" in q["question"]
        assert "0.0 and 100.0" in q["detailed_defense"] or "[0, 100]" in q["short_answer"]
        assert "STABLE" in q["detailed_defense"]
        assert "CRITICAL" in q["detailed_defense"]

    def test_jq03_why_fos_limit_equilibrium(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-03")
        assert "FOS" in q["question"]
        assert "Mohr-Coulomb" in q["detailed_defense"]
        assert "tau_f" in q["detailed_defense"] or "shear strength" in q["detailed_defense"].lower()
        assert "1.5" in q["detailed_defense"]

    def test_jq05_why_not_lstm_honesty(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-05")
        assert "LSTM" in q["question"]
        assert "NOT_TRAINED / SURROGATE" in q["evidence_badge"]
        assert "DATA_COLLECTION_REQUIRED" in q["detailed_defense"]
        assert "timestamp" in q["detailed_defense"].lower()

    def test_jq06_jq07_data_truth_provenance(self):
        q_live = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-06")
        assert "LIVE" in q_live["evidence_badge"]
        assert "Open-Meteo" in q_live["detailed_defense"]
        assert "USGS" in q_live["detailed_defense"]

        q_sim = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-07")
        assert "SIMULATED" in q_sim["evidence_badge"]
        assert "NOT VERIFIED" in q_sim["detailed_defense"]

    def test_jq08_corroboration_false_alarm_defense(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-08")
        assert "FALSE ALERTS" in q["question"]
        assert "2-of-3" in q["detailed_defense"]
        assert "DMA 2005" in q["detailed_defense"]

    def test_jq09_siren_actuation_strictly_locked(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-09")
        assert "SIREN" in q["question"]
        assert "SAFETY LOCKED" in q["evidence_badge"]
        assert "ENABLE_PUBLIC_DISPATCH=0" in q["detailed_defense"]
        assert "SIREN_DRY_RUN=1" in q["detailed_defense"]
        assert "REJECTED_SAFETY" in q["detailed_defense"]

    def test_jq10_biggest_limitation_disclosure(self):
        q = next(item for item in TOP_10_JUDGE_QUESTIONS if item["id"] == "JQ-10")
        assert "LIMITATION" in q["question"]
        assert "NOT VERIFIED" in q["detailed_defense"]
        assert "TRAINED_LIMITED_DATA" in q["detailed_defense"]


class TestPhase12ETimelineAndSafety:
    """Verifies timeline progression, safety locks, and voice grounding."""

    def test_timeline_timing_continuity(self):
        total_seconds = 0
        for stage in MASTER_DEMO_TIMELINE:
            assert stage["seconds_start"] == total_seconds
            assert stage["seconds_end"] > stage["seconds_start"]
            total_seconds = stage["seconds_end"]
            assert "speaker_cue" in stage
            assert "expected_state" in stage
            assert "safety_check" in stage
        assert total_seconds == 300  # Exactly 5 minutes (5:00)

    def test_canonical_corridor_state(self):
        state = PahadMasterDemoEngine.get_canonical_corridor_state()
        assert state["corridor_id"] == "SK-NH10-KM48"
        assert state["cri"] == 72.4
        assert state["fos"] == 1.08
        assert state["event_probability"] == 0.68
        assert state["corroboration"]["corroboration_state"] == "CORROBORATED_MULTI_SIGNAL (A+B+C)"

    def test_safety_invariants_verification(self):
        safety = PahadMasterDemoEngine.verify_safety_invariants()
        assert safety["safety_status"] == "LOCKED_SAFE"
        assert safety["is_safe"] is True
        assert safety["invariants"]["ENABLE_PUBLIC_DISPATCH"] == 0
        assert safety["invariants"]["SIREN_DRY_RUN"] == 1
        assert safety["invariants"]["PUBLIC_DEMO_TEST_ONLY"] == 1
        assert safety["physical_actuation_blocked"] is True

    def test_voice_assistant_rejects_siren_actuation(self):
        pva = PahadVoiceAssistantService()
        res = pva.process_query("Sound the siren")
        assert res.get("status") == "REJECTED_SAFETY"
        assert res.get("is_safety_rejection") is True
        resp_text = res.get("response") or res.get("text", "")
        assert any(k in resp_text for k in ["Disaster Management Act", "DMA 2005", "COMMAND REJECTED", "Safety Rejection"])


    def test_ui_judge_overlay_elements(self):
        idx_path = os.path.join(REPO_ROOT, "templates", "index.html")
        with open(idx_path, "r", encoding="utf-8") as f:
            html = f.read()

        assert 'id="btn-judge-overlay-trigger"' in html
        assert 'id="pahad-judge-overlay"' in html
        assert 'function toggleJudgeDefenseOverlay' in html
        assert 'function setJudgeOverlayTab' in html
        assert 'function executeJudgeDemoStage' in html
        assert 'TOP 10 JUDGE DEFENSE' in html
        assert '5-MIN MASTER DEMO FLOW' in html
        assert 'SAFETY &amp; DATA TRUTH' in html
