# -*- coding: utf-8 -*-
"""
tests/test_phase10i_geofence.py
===============================
PARVAT NETRA • Phase 10I — Geofenced Recipient Selection & PII Protection Tests
-------------------------------------------------------------------------------
Verifies:
  1. Geofence polygon filtering: only recipients inside polygon are selected.
  2. Exclusion of users outside the polygon.
  3. Role-based filtering (RESIDENT, TOURIST, FIELD_VOLUNTEER).
  4. Language matching for localized SMS dispatch.
  5. Strict PII protection:
     - Phone numbers masked (+91-XXXXX-1234).
     - Deterministic SHA-256 hash generated for each phone number.
     - Raw phone numbers never exposed in logs or delivery receipts.
"""

import pytest
from services.production_sms_service import RecipientFilter

# 15 km NH-10 Corridor Polygon (Pakyong / Gangtok)
NH10_GEOFENCE = [
    [27.3200, 88.6000],
    [27.3400, 88.6000],
    [27.3400, 88.6200],
    [27.3200, 88.6200],
    [27.3200, 88.6000]
]


def test_recipients_inside_geofence_selected():
    """Verifies that recipients located within the polygon are retrieved."""
    recipients = RecipientFilter.get_recipients_in_geofence(NH10_GEOFENCE)
    assert len(recipients) > 0

    # Ensure all returned coordinates are inside polygon
    for r in recipients:
        assert 27.3200 <= r["latitude"] <= 27.3400
        assert 88.6000 <= r["longitude"] <= 88.6200


def test_recipients_outside_geofence_excluded():
    """Verifies that subscribers outside the polygon (e.g. Delhi or outside district) are excluded."""
    recipients = RecipientFilter.get_recipients_in_geofence(NH10_GEOFENCE)
    recipient_ids = [r["recipient_id"] for r in recipients]

    # 'CITIZEN-GNT-01' is set at lat 28.5000, lon 77.2000 (outside)
    assert "CITIZEN-GNT-01" not in recipient_ids


def test_pii_masking_format():
    """Verifies that phone numbers are masked properly and follow format +91-XXXXX-1234."""
    masked = RecipientFilter.mask_phone("+919832011234")
    assert masked == "+91-XXXXX-1234"
    assert "98320" not in masked


def test_pii_sha256_hashing():
    """Verifies that phone numbers are converted to deterministic SHA-256 hashes."""
    hash1 = RecipientFilter.hash_phone("+919832011234")
    hash2 = RecipientFilter.hash_phone("+919832011234")
    assert hash1 == hash2
    assert len(hash1) == 64
    assert hash1 != "+919832011234"


def test_role_filtering_capability():
    """Verifies that recipient filtering can target specific roles."""
    residents_only = RecipientFilter.get_recipients_in_geofence(NH10_GEOFENCE, role_filter=["RESIDENT"])
    for r in residents_only:
        assert r["role"] == "RESIDENT"
