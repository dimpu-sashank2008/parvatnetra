# -*- coding: utf-8 -*-
"""
tests/test_phase8_field_dispatch.py
===================================
Tests for Checkpoint 8-16 & 8-17:
Field Task Dispatch, Multi-Profile Route Comparison (FASTEST, SHORTEST, SAFEST),
and Evidence Submission.
"""

import pytest
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_TRIAGED, STATE_FIELD_VERIFICATION, STATE_AUTHORITY_REVIEW
from services.eoc_service import EOC_SERVICE


def test_field_task_dispatch_and_routing_comparison():
    """Verify field task creation, routing comparison, and status assignment."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=78.0,
        risk_band="HIGH",
        model_probability=0.79,
        FoS=1.01,
        rainfall=165.0
    )
    # Triage first
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_TRIAGED, "EOC_OPERATOR", "OP_01")

    task_res = EOC_SERVICE.dispatch_field_task(
        incident_id=inc.incident_id,
        team="BRO_TASK_FORCE_KM48",
        priority="HIGH",
        target="NH-10 KM 48 29th Mile Chokepoint",
        coordinates=(27.3300, 88.6100),
        deadline_minutes=45,
        routing_profile="SAFEST"
    )

    assert task_res["status"] == "ASSIGNED"
    assert "task_id" in task_res
    assert "routing_comparison" in task_res
    routes = task_res["routing_comparison"]

    # Verify all 3 profiles exist
    assert "FASTEST" in routes
    assert "SHORTEST" in routes
    assert "SAFEST" in routes
    for prof in ("FASTEST", "SHORTEST", "SAFEST"):
        assert "distance_km" in routes[prof]
        assert "eta_minutes" in routes[prof]
        assert "hazard_exposure" in routes[prof]

    # Verify incident advanced to FIELD_VERIFICATION
    updated_inc = EOC_INCIDENT_MANAGER.get_incident(inc.incident_id)
    assert updated_inc.incident_status == STATE_FIELD_VERIFICATION


def test_field_evidence_submission_and_authority_review_transition():
    """Verify field evidence submission advances incident to AUTHORITY_REVIEW."""
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=80.0,
        risk_band="HIGH",
        model_probability=0.81,
        FoS=0.98,
        rainfall=170.0
    )
    EOC_INCIDENT_MANAGER.transition_state(inc.incident_id, STATE_TRIAGED, "EOC_OPERATOR", "OP_01")
    task_res = EOC_SERVICE.dispatch_field_task(
        incident_id=inc.incident_id,
        team="SDRF_UNIT_03",
        priority="EXTREME",
        target="NH-10 KM 48",
        coordinates=(27.3300, 88.6100)
    )

    ev_res = EOC_SERVICE.submit_field_evidence(
        task_id=task_res["task_id"],
        operator="SDRF_INSPECTOR_LEPCHA",
        observations="Significant active toe slumping and 15mm tension cracks.",
        observed_cracks=True,
        slope_movement=True,
        road_blocked=False,
        media_refs=["SDRF_EVIDENCE_PHOTO_1.JPG", "SDRF_EVIDENCE_VIDEO_1.MP4"]
    )

    assert ev_res["status"] == "VERIFIED"
    assert ev_res["evidence"]["verification_status"] == "GROUND_TRUTH_CONFIRMED"
    assert len(ev_res["evidence"]["media_refs"]) == 2

    # Verify incident transitioned to AUTHORITY_REVIEW
    updated_inc = EOC_INCIDENT_MANAGER.get_incident(inc.incident_id)
    assert updated_inc.incident_status == STATE_AUTHORITY_REVIEW
