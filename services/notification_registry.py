# -*- coding: utf-8 -*-
"""
services/notification_registry.py
=================================
PARVAT NETRA • Emergency Notification Recipient Registry & Consent Manager
-------------------------------------------------------------------------
Implements Section 8, 9, 25: Privacy-preserving recipient registry.
Features:
  1. Role-based indexing: authority, field_officer, response_team, citizen.
  2. Cryptographic phone references (SHA-256 phone hash + masked reference).
  3. Explicit consent management: SMS_OPT_IN, PUSH_OPT_IN.
  4. Aggregate statistics generation for dashboard (zero personal PII disclosure).

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import hashlib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger("NOTIFICATION_REGISTRY")


def hash_phone(phone_str: str) -> Tuple[str, str]:
    """
    Returns (phone_hash, masked_reference) to preserve civilian privacy.
    Example: '+919876543210' -> ('e3b0c44298fc1...', '+91-XXXXX-3210')
    """
    clean = "".join(ch for ch in phone_str if ch.isdigit() or ch == "+")
    p_hash = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    if len(clean) >= 4:
        masked = f"+91-XXXXX-{clean[-4:]}"
    else:
        masked = "+91-XXXXX-0000"
    return p_hash, masked


@dataclass
class RegisteredRecipient:
    recipient_id: str
    role: str  # "authority", "field_officer", "response_team", "citizen"
    device_id: str
    phone_hash: str
    phone_masked: str
    lat: float
    lon: float
    preferred_language: str = "en"
    push_enabled: bool = True
    sms_enabled: bool = True
    consent_status: str = "OPT_IN"  # "OPT_IN", "SMS_OPT_IN", "PUSH_OPT_IN", "OPT_OUT"
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        d = asdict(self)
        if not include_sensitive:
            d.pop("phone_hash", None)
        return d


class NotificationRegistry:
    """
    In-memory and persistent registry for notification recipients.
    """

    def __init__(self):
        self._recipients: Dict[str, RegisteredRecipient] = {}
        self._seed_default_recipients()

    def _seed_default_recipients(self):
        """Seeds realistic demonstration recipients in the Sikkim NH-10 corridor."""
        demo_data = [
            # Authorities
            ("REC-AUTH-01", "authority", "DEV-MAGISTRATE-GTK", "+919800112233", 27.3314, 88.6138, "en", "OPT_IN"),
            ("REC-AUTH-02", "authority", "DEV-BRO-HQ-SEVOKE", "+919800112234", 26.8850, 88.4720, "en", "OPT_IN"),
            ("REC-AUTH-03", "authority", "DEV-DDMA-PAKYONG", "+919800112235", 27.2400, 88.5800, "en", "OPT_IN"),
            # Field Officers & SDRF Teams
            ("REC-FIELD-01", "field_officer", "DEV-SDRF-SINGTAM", "+919800223344", 27.2350, 88.4980, "ne", "OPT_IN"),
            ("REC-FIELD-02", "field_officer", "DEV-PWD-KM48", "+919800223345", 27.2000, 88.5500, "hi", "OPT_IN"),
            ("REC-RESP-01", "response_team", "DEV-NDRF-RANGPO", "+919800334455", 27.1767, 88.5322, "en", "OPT_IN"),
            # Local Citizens along NH-10 (Likhu Veer / 29th Mile / Rangpo / Singtam)
            ("REC-CITZ-01", "citizen", "MOB-CITZ-LIKHU-01", "+919811001101", 27.2100, 88.5450, "ne", "SMS_OPT_IN"),
            ("REC-CITZ-02", "citizen", "MOB-CITZ-LIKHU-02", "+919811001102", 27.2050, 88.5480, "bh", "PUSH_OPT_IN"),
            ("REC-CITZ-03", "citizen", "MOB-CITZ-RANGPO-01", "+919811001103", 27.1800, 88.5300, "lp", "OPT_IN"),
            ("REC-CITZ-04", "citizen", "MOB-CITZ-SINGTAM-01", "+919811001104", 27.2300, 88.5000, "as", "OPT_IN"),
            ("REC-CITZ-05", "citizen", "MOB-CITZ-MELLI-01", "+919811001105", 27.0900, 88.4500, "hi", "OPT_IN"),
            ("REC-CITZ-06", "citizen", "MOB-CITZ-SILIGURI-01", "+919811001106", 26.7200, 88.4300, "en", "OPT_IN"),
        ]

        for r_id, role, dev_id, phone, lat, lon, lang, consent in demo_data:
            p_hash, p_mask = hash_phone(phone)
            push = "PUSH" in consent or consent == "OPT_IN"
            sms = "SMS" in consent or consent == "OPT_IN"
            self._recipients[r_id] = RegisteredRecipient(
                recipient_id=r_id,
                role=role,
                device_id=dev_id,
                phone_hash=p_hash,
                phone_masked=p_mask,
                lat=lat,
                lon=lon,
                preferred_language=lang,
                push_enabled=push,
                sms_enabled=sms,
                consent_status=consent
            )

    def register_recipient(
        self,
        recipient_id: str,
        role: str,
        device_id: str,
        phone: str,
        lat: float,
        lon: float,
        preferred_language: str = "en",
        consent_status: str = "OPT_IN"
    ) -> RegisteredRecipient:
        """Registers or updates a recipient with explicit consent."""
        p_hash, p_mask = hash_phone(phone)
        push = "PUSH" in consent_status or consent_status == "OPT_IN"
        sms = "SMS" in consent_status or consent_status == "OPT_IN"

        r = RegisteredRecipient(
            recipient_id=recipient_id,
            role=role,
            device_id=device_id,
            phone_hash=p_hash,
            phone_masked=p_mask,
            lat=float(lat),
            lon=float(lon),
            preferred_language=preferred_language,
            push_enabled=push,
            sms_enabled=sms,
            consent_status=consent_status
        )
        self._recipients[recipient_id] = r
        logger.info(f"[Registry] Registered recipient {recipient_id} ({role}, consent: {consent_status})")
        return r

    def get_recipient(self, recipient_id: str) -> Optional[RegisteredRecipient]:
        return self._recipients.get(recipient_id)

    def list_all_candidates(self) -> List[Dict[str, Any]]:
        """Returns candidate dictionaries suitable for geofence filtering."""
        return [r.to_dict(include_sensitive=True) for r in self._recipients.values()]

    def compute_zone_aggregates(self, eligible_recipients: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Computes privacy-preserving aggregate statistics (Section 25).
        Discloses NO personal recipient names or phone numbers to the UI.
        """
        total = len(eligible_recipients)
        authorities = sum(1 for r in eligible_recipients if r.get("role") == "authority")
        field_teams = sum(1 for r in eligible_recipients if r.get("role") in ("field_officer", "response_team"))
        citizens = sum(1 for r in eligible_recipients if r.get("role") == "citizen")
        sms_eligible = sum(1 for r in eligible_recipients if r.get("sms_enabled") and r.get("consent_status") != "OPT_OUT")
        push_eligible = sum(1 for r in eligible_recipients if r.get("push_enabled") and r.get("consent_status") != "OPT_OUT")

        return {
            "total_in_zone": total,
            "authorities": authorities,
            "field_teams": field_teams,
            "citizens": citizens,
            "sms_eligible": sms_eligible,
            "push_eligible": push_eligible
        }


# Singleton instance
NOTIFICATION_REGISTRY = NotificationRegistry()
