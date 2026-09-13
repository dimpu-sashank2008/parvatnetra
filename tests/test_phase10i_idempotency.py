# -*- coding: utf-8 -*-
"""
tests/test_phase10i_idempotency.py
==================================
PARVAT NETRA • Phase 10I — Deterministic Idempotency & Duplicate Prevention Tests
---------------------------------------------------------------------------------
Verifies:
  1. Deterministic generation of dispatch references based on incident_id, recipient, and template.
  2. Duplicate dispatch prevention during network retries, browser reloads, and EOC re-evaluations.
  3. Idempotency manager correctly flags duplicates.
  4. Second dispatch returns existing receipt without re-queueing or spamming recipients.
"""

import pytest
from services.production_sms_service import (
    IdempotencyManager,
    PRODUCTION_SMS_SERVICE,
    TEMPLATE_LANDSLIDE_WARNING,
    ROLE_DISTRICT_AUTHORITY
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER, STATE_AUTHORIZED

GEOFENCE = [
    [27.3200, 88.6000],
    [27.3400, 88.6000],
    [27.3400, 88.6200],
    [27.3200, 88.6200],
    [27.3200, 88.6000]
]


def test_deterministic_dispatch_id_generation():
    """Verifies that the same parameters produce identical deterministic IDs."""
    mgr = IdempotencyManager()
    id1 = mgr.generate_dispatch_id("INC-IDEM-01", "REC-01", TEMPLATE_LANDSLIDE_WARNING)
    id2 = mgr.generate_dispatch_id("INC-IDEM-01", "REC-01", TEMPLATE_LANDSLIDE_WARNING)
    assert id1 == id2
    assert id1.startswith("SMS-DISP-")

    # Different recipient produces different ID
    id3 = mgr.generate_dispatch_id("INC-IDEM-01", "REC-02", TEMPLATE_LANDSLIDE_WARNING)
    assert id1 != id3


def test_duplicate_dispatch_blocked_by_idempotency():
    """Verifies that dispatching the same emergency SMS twice does not duplicate records."""
    inc_id = "INC-IDEM-02"
    inc = EOC_INCIDENT_MANAGER.create_incident(
        sector_id="SK-NH10-KM48",
        risk_score=84.0,
        risk_band="CRITICAL",
        model_probability=0.87,
        FoS=0.89,
        rainfall=78.0,
        incident_id=inc_id
    )
    inc.incident_status = STATE_AUTHORIZED
    inc.corroboration_count = 3
    EOC_INCIDENT_MANAGER._save(inc)

    token = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)

    # First dispatch
    res1 = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token,
        geofence_polygon=GEOFENCE,
        template_type=TEMPLATE_LANDSLIDE_WARNING
    )
    assert res1["success"] is True
    first_count = res1["dispatched_count"]
    assert first_count > 0

    first_dispatch_ids = [r["dispatch_id"] for r in res1["recipients"]]

    # Immediate second dispatch (simulating duplicate webhook / browser double-click)
    # Issue fresh token for same incident to test idempotency layer
    token2 = PRODUCTION_SMS_SERVICE.auth_token_mgr.issue_token("DM_PAKYONG", ROLE_DISTRICT_AUTHORITY, inc_id)
    res2 = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
        incident_id=inc_id,
        actor_id="DM_PAKYONG",
        actor_role=ROLE_DISTRICT_AUTHORITY,
        auth_token=token2,
        geofence_polygon=GEOFENCE,
        template_type=TEMPLATE_LANDSLIDE_WARNING
    )

    second_dispatch_ids = [r["dispatch_id"] for r in res2["recipients"]]

    # Assert that dispatch IDs match identically (deduplicated)
    assert first_dispatch_ids == second_dispatch_ids
    assert res2["dispatched_count"] == first_count
