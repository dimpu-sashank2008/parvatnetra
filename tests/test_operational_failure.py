# -*- coding: utf-8 -*-
"""
tests/test_operational_failure.py
=================================
Unit tests for operational failure modes, graceful degradation, stale telemetry
penalties, Out-Of-Distribution (OOD) envelope detection, and safety gate suppression.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pahad_decision_store import DecisionRecordStore
from services.notification_orchestrator import (
    NotificationOrchestrator,
    STATUS_SUPPRESSED,
    STATUS_DELIVERED
)


@pytest.fixture
def temp_store(tmp_path):
    db_file = str(tmp_path / "test_failure.db")
    return DecisionRecordStore(db_path=db_file)


def test_graceful_degradation_on_missing_observations(temp_store):
    """Empty or partial observations should gracefully fallback without crashing."""
    res = temp_store.evaluate_and_record(
        sector_id="SECTOR-SPARSE-01",
        observations={}
    )

    assert res["decision_id"] is not None
    assert res["risk"] in ["LOW", "MODERATE"]
    assert res["is_ood"] is False
    assert res["safety_gate_result"] == "PASSED_NOMINAL"
    assert res["recommended_action"] == "CONTINUE_MONITORING"
    assert res["confidence"] >= 0.50


def test_stale_telemetry_confidence_penalties(temp_store):
    """Telemetry age reduces confidence score according to freshness tiers."""
    # Fresh telemetry
    rec_fresh = temp_store.evaluate_and_record(
        sector_id="SECTOR-FRESH",
        observations={"freshness_status": "FRESH"}
    )
    assert rec_fresh["confidence"] == 0.90

    # Aging telemetry
    rec_aging = temp_store.evaluate_and_record(
        sector_id="SECTOR-AGING",
        observations={"freshness_status": "AGING"}
    )
    assert rec_aging["confidence"] == 0.75

    # Stale telemetry
    rec_stale = temp_store.evaluate_and_record(
        sector_id="SECTOR-STALE",
        observations={"freshness_status": "STALE"}
    )
    assert rec_stale["confidence"] == 0.50

    # Unavailable telemetry
    rec_unavail = temp_store.evaluate_and_record(
        sector_id="SECTOR-UNAVAIL",
        observations={"freshness_status": "UNAVAILABLE"}
    )
    assert rec_unavail["confidence"] == 0.50


def test_ood_envelope_detection_forces_human_review(temp_store):
    """Readings exceeding physical/historical boundaries force mandatory authority review."""
    # 1. Extreme rainfall (> 400 mm / 24h)
    rec_rain = temp_store.evaluate_and_record(
        sector_id="SECTOR-OOD-RAIN",
        observations={"rain_24h_mm": 520.0}
    )
    assert rec_rain["is_ood"] is True
    assert "exceeds extreme monsoon ceiling" in rec_rain["ood_reason"]
    assert rec_rain["safety_gate_result"] == "HOLD_MANDATORY_HUMAN_REVIEW"
    assert rec_rain["recommended_action"] == "ESCALATE_OOD_TO_AUTHORITY"
    assert rec_rain["confidence"] <= 0.40

    # 2. Extreme pore pressure (> 180 kPa)
    rec_pp = temp_store.evaluate_and_record(
        sector_id="SECTOR-OOD-PP",
        observations={"pore_pressure_kpa": 215.0}
    )
    assert rec_pp["is_ood"] is True
    assert "exceeds sensor saturation boundary" in rec_pp["ood_reason"]
    assert rec_pp["safety_gate_result"] == "HOLD_MANDATORY_HUMAN_REVIEW"

    # 3. Extreme tilt (> 15 deg)
    rec_tilt = temp_store.evaluate_and_record(
        sector_id="SECTOR-OOD-TILT",
        observations={"tilt_deg": 18.5}
    )
    assert rec_tilt["is_ood"] is True
    assert "indicates total structural dislocation" in rec_tilt["ood_reason"]
    assert rec_tilt["safety_gate_result"] == "HOLD_MANDATORY_HUMAN_REVIEW"


def test_public_dispatch_suppression_safety_gate(tmp_path):
    """Public dispatches remain suppressed unless explicitly authorized and enabled."""
    db_file = str(tmp_path / "test_notif.db")
    notif = NotificationOrchestrator(db_path=db_file)

    cap_payload = notif.generate_cap_alert(
        alert_id="ALERT-SAFETY-01",
        event="Debris Flow Warning",
        severity="Severe",
        urgency="Immediate",
        certainty="Observed",
        area_description="KM 48 NH-10",
        instruction="Evacuate"
    )

    # 1. Default dispatch without public enabled - public channels must be SUPPRESSED
    res1 = notif.dispatch_alert(
        alert_id="ALERT-SAFETY-01",
        cap_payload=cap_payload,
        channels=["SMS", "SIREN", "MOBILE"],
        public_dispatch_enabled=False
    )
    assert res1["channel_results"]["SMS"]["status"] == STATUS_SUPPRESSED
    assert res1["channel_results"]["SIREN"]["status"] == STATUS_SUPPRESSED
    assert "PUBLIC_DISPATCH is DISABLED" in res1["channel_results"]["SMS"]["note"]
    # Internal operational channels are delivered
    assert res1["channel_results"]["MOBILE"]["status"] == STATUS_DELIVERED

    # 2. Public enabled but without authorization token - must be SUPPRESSED
    res2 = notif.dispatch_alert(
        alert_id="ALERT-SAFETY-01",
        cap_payload=cap_payload,
        channels=["SMS", "SIREN"],
        public_dispatch_enabled=True,
        authorization_token=None
    )
    assert res2["channel_results"]["SMS"]["status"] == STATUS_SUPPRESSED
    assert "requires valid authorization_token" in res2["channel_results"]["SMS"]["note"]

    # 3. Public enabled WITH authorization token - DELIVERED
    res3 = notif.dispatch_alert(
        alert_id="ALERT-SAFETY-01",
        cap_payload=cap_payload,
        channels=["SMS", "SIREN"],
        public_dispatch_enabled=True,
        authorization_token="AUTH-DM-SIKKIM-998822"
    )
    assert res3["channel_results"]["SMS"]["status"] == STATUS_DELIVERED
    assert res3["channel_results"]["SIREN"]["status"] == STATUS_DELIVERED


def test_corroboration_failure_prevents_autonomous_high_alert(temp_store):
    """An isolated single-modality spike must NOT trigger an unverified high hazard alert."""
    # High pore pressure alone (no rainfall, no slope mechanics, no seismic)
    rec = temp_store.evaluate_and_record(
        sector_id="SECTOR-UNCONFIRMED-01",
        observations={
            "pore_pressure_kpa": 65.0,  # Abnormal in-situ
            "rain_24h_mm": 0.0,
            "fos": 1.45,
            "tilt_deg": 0.1
        }
    )

    assert rec["signals"]["is_corroborated"] is False
    # Must hold unconfirmed anomaly rather than raising public alarm
    assert rec["safety_gate_result"] == "HOLD_UNCONFIRMED_ANOMALY"
    assert rec["recommended_action"] == "REQUEST_FIELD_VERIFICATION"
