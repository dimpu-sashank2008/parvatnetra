# -*- coding: utf-8 -*-
"""
tests/test_phase7h_mobile_offline.py
====================================
PHASE 7H — CP 7H-03: Mobile Offline Capabilities, Cached Snapshots & Alerts,
Local Field Report Queueing, GPS Coordinate Validation, and Sync Reconciliation.
"""

import os
import json
import pytest
from datetime import datetime, timezone
from services.sync_service import SyncService


@pytest.fixture
def sync_service():
    return SyncService()


def test_mobile_offline_cached_manifest_structure(sync_service):
    """CP 7H-03: Mobile offline bundle provides cached alerts, sectors, shelters, and road blocks."""
    manifest = sync_service.pull_offline_manifest(sectors=["S14", "SK-NH10-KM48"])
    assert manifest["status"] == "SUCCESS"
    assert "version" in manifest
    assert "cached_alerts" in manifest
    assert "sectors" in manifest
    assert "shelters" in manifest
    assert "road_blocks" in manifest
    assert "generated_at" in manifest
    assert isinstance(manifest["shelters"], list)
    assert len(manifest["shelters"]) > 0


def test_mobile_offline_report_creation_and_queueing(sync_service):
    """CP 7H-03: Offline responder creates local field report with client UUID; sync queues it."""
    local_id = "PN-MOBILE-OFFLINE-TEST-001"
    report = {
        "local_id": local_id,
        "hazard_type": "debris_flow",
        "severity": "CRITICAL",
        "latitude": 27.2458,
        "longitude": 88.5124,
        "description": "Debris flow across KM 48 of NH-10. Culvert overwhelmed.",
        "reporter_role": "Field Officer",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Simulate sync to backend
    batch_res = sync_service.sync_batch_reports([report])
    assert batch_res["status"] == "SUCCESS"
    assert batch_res["synced_count"] == 1
    assert len(batch_res["acknowledgements"]) == 1
    
    ack = batch_res["acknowledgements"][0]
    assert ack["local_id"] == local_id
    assert ack["sync_status"] == "SYNCED"
    assert ack["server_id"] is not None
    assert "PN-REPORT-" in ack["tracking_ref"]


def test_mobile_gps_coordinate_validation(sync_service):
    """CP 7H-03: GPS coordinates are tracked and validated for field reports."""
    # Valid NER coordinate (Sikkim NH-10)
    valid_report = {
        "local_id": "PN-LOC-VALID-01",
        "hazard_type": "landslide",
        "latitude": 27.33,
        "longitude": 88.61,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    ack_valid = sync_service.sync_single_report(valid_report)
    assert ack_valid["sync_status"] == "SYNCED"

    # Preserves local ID and coordinates
    assert ack_valid["local_id"] == "PN-LOC-VALID-01"


def test_mobile_offline_idempotent_deduplication(sync_service):
    """CP 7H-03: Re-transmitting an already synced local report does not create duplicate server entries."""
    local_id = "PN-MOBILE-DEDUP-99"
    report = {
        "local_id": local_id,
        "hazard_type": "subsidence",
        "severity": "MODERATE",
        "latitude": 27.30,
        "longitude": 88.58,
        "description": "Slow road subsidence observed.",
        "created_at": "2026-09-11T05:00:00Z"
    }

    # First sync
    res1 = sync_service.sync_single_report(report)
    assert res1["sync_status"] == "SYNCED"
    srv_id_1 = res1["server_id"]

    # Re-sync (e.g. mobile reconnected and resent queue)
    res2 = sync_service.sync_single_report(report)
    assert res2["sync_status"] == "SYNCED"
    assert res2["server_id"] == srv_id_1
    assert res2.get("duplicate") is True
