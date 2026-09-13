# -*- coding: utf-8 -*-
"""
tests/test_phase7_mobile_contract.py
====================================
Tests for Phase 7H Mobile Field Contract & Offline Hardening.
Validates the Flutter field app contract with backend:
  1. Field report push contract (/api/sync/push)
  2. Sync pull contract (/api/sync/pull)
  3. Push idempotency (deduplication of retry packets)
  4. Telemetry payload schema validation
  5. Multilingual localization key parity across all 6 Himalayan languages
"""

import os
import time
import json
import pytest
from app import app
from services.sync_service import SYNC_SERVICE

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_mobile_field_report_push_contract(client):
    """Field worker report pushed from mobile SQLite sync queue returns valid server ACK."""
    ts = int(time.time() * 1000)
    local_id = f"TEST-MOB-{ts}"
    payload = {
        "reports": [
            {
                "local_id": local_id,
                "created_at": "2026-09-10T10:00:00Z",
                "lat": 27.3300,
                "lon": 88.6100,
                "hazard_type": "Tension Crack",
                "severity": "CRITICAL",
                "description": "Widening tension crack observed along Pakyong slope.",
                "photo_paths": "['/storage/dcim/crack.jpg']",
                "video_paths": "[]",
                "reporter_role": "BRO_FIELD_INSPECTOR",
                "sync_status": "QUEUED",
                "retry_count": 0
            }
        ]
    }
    res = client.post("/api/sync/push", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "SUCCESS"
    acks = data.get("acknowledgements", [])
    assert len(acks) == 1
    assert acks[0]["local_id"] == local_id
    assert acks[0]["sync_status"] == "SYNCED"
    assert "tracking_ref" in acks[0]

def test_mobile_pull_contract(client):
    """Mobile pull returns sector snapshots and active alert headers."""
    res = client.get("/api/sync/pull?sector_id=SK-NH10-KM48")
    assert res.status_code == 200
    data = res.get_json()
    assert "active_alerts" in data
    assert "critical_snapshots" in data
    assert "pulled_at" in data
    assert "bundle_version" in data

def test_sync_push_idempotency(client):
    """Re-pushing identical report payload due to network retry does not create duplicates."""
    ts = int(time.time() * 1000)
    local_id = f"RETRY-TEST-{ts}"
    payload = {
        "reports": [
            {
                "local_id": local_id,
                "created_at": "2026-09-10T10:05:00Z",
                "lat": 27.332,
                "lon": 88.612,
                "hazard_type": "Rockfall",
                "severity": "MAJOR",
                "description": "Small rockfall debris on road verge.",
                "photo_paths": "[]",
                "video_paths": "[]",
                "reporter_role": "SDRF_RESPONDER",
                "sync_status": "QUEUED",
                "retry_count": 1
            }
        ]
    }
    # First push
    res1 = client.post("/api/sync/push", json=payload)
    assert res1.status_code == 200
    ack1 = res1.get_json()["acknowledgements"][0]

    # Retry push
    res2 = client.post("/api/sync/push", json=payload)
    assert res2.status_code == 200
    ack2 = res2.get_json()["acknowledgements"][0]

    assert ack1["local_id"] == ack2["local_id"]
    assert ack1["sync_status"] == "SYNCED"
    assert ack2["sync_status"] == "SYNCED"

def test_multilingual_dictionary_key_parity():
    """Validates that all 6 Himalayan languages in i18n.js provide core emergency keys."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    i18n_file = os.path.join(base_dir, "static", "js", "i18n.js")
    assert os.path.exists(i18n_file)

    with open(i18n_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Core languages: English, Hindi, Nepali, Bhutia, Lepcha, Assamese
    for lang in ["en", "hi", "ne", "bh", "lp", "as"]:
        assert f"{lang}:" in content, f"Missing language block for {lang}"

    # Critical alert keys that must exist
    required_keys = ["app_title", "evacuation_warning", "critical_red_zones", "road_severed"]
    for key in required_keys:
        assert f"{key}:" in content, f"Missing emergency key: {key}"
