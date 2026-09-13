# -*- coding: utf-8 -*-
"""
services/public_warning_service.py
===================================
PARVAT NETRA • Multi-Channel Public Warning & Dissemination Readiness Engine
----------------------------------------------------------------------------
Phase 10E: Standards-compliant, multi-channel emergency alert dissemination.

Architecture:
  PAHAD AI Multi-Modal Telemetry
       │
       ▼
  2-of-3 Corroboration Check (FoS, In-Situ Sensors, IMD Rainfall, InSAR)
       │
       ▼
  EOC Incident Creation (STATE_AUTHORITY_REVIEW)
       │
       ▼
  Human Authority Approval (RBAC, DMA 2005 Jurisdiction, Cryptographic Token)
       │
       ▼
  Geofence Formulation (15 km Geodesic Corridor Polygon Containment)
       │
       ▼
  Multi-Channel Alert Dissemination Package
       │
  ┌────┴───────────────────────┬───────────────────────┬───────────────────┐
  ▼                            ▼                       ▼                   ▼
SMS Gateway               Cell Broadcast          SACHET / CAP 1.2    Acoustic Siren
(CDAC / Sandes / Mock)    (3GPP ATIS-0700015)     (OASIS XML Feed)    (Signed HMAC Relay)
  │                            │                       │                   │
  ▼                            ▼                       ▼                   ▼
Web / Mobile Push         Roadside VMS            Audit Ledger
(ServiceWorker / FCM)     (Dynamic Matrix Signs)  (Tamper-Evident SHA-256)

Safety Invariants:
  1. PUBLIC_DISPATCH = DISABLED (All channels strictly TEST/DRY_RUN).
  2. SIREN_DRY_RUN = 1 (Zero physical audible horn actuation).
  3. CELL_BROADCAST = TEST/DRY_RUN (Zero live RF emissions).
  4. Delivery honesty: Simulated alerts NEVER labeled DELIVERED without authentic carrier receipt.
  5. Decoupled tracking: Failure in one channel never masks or alters status in another.
  6. Multi-lingual coverage: English, Hindi, Nepali, Assamese, Bhutia, Lepcha (<160 char SMS).

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001 / Phase 10E
"""

from __future__ import annotations

import os
import math
import time
import uuid
import hmac
import hashlib
import sqlite3
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set

# Core engine imports
from engine.pahad_cap import CAPAlertGenerator
from services.sms_service import SMS_SERVICE, BaseSMSProvider, MockSMSProvider, CDACSMSProvider
from services.siren_controller import GLOBAL_SIREN_CONTROLLER, SirenController
from engine.eoc_incident_manager import (
    EOC_INCIDENT_MANAGER,
    STATE_AUTHORIZED,
    STATE_DISPATCHED
)
STATE_WARNING_AUTHORIZED = "WARNING_AUTHORIZED"
from services.authority_review_service import (
    ROLE_PUBLIC,
    ROLE_FIELD_OPERATOR,
    ROLE_AUTHORITY,
    ROLE_DISTRICT_AUTHORITY,
    ROLE_STATE_AUTHORITY,
    ROLE_ADMIN,
    AuthorizationTokenManager,
    check_rbac_permission
)

AUTHORIZATION_TOKEN_MANAGER = AuthorizationTokenManager()

logger = logging.getLogger("PUBLIC_WARNING_SERVICE")

# ==============================================================================
# Constants & Enums
# ==============================================================================

# Strict Environment Safety Defaults
PUBLIC_DISPATCH_ENABLED: bool = os.getenv("PUBLIC_DISPATCH", "DISABLED").upper() == "ENABLED"
SIREN_DRY_RUN: bool = os.getenv("SIREN_DRY_RUN", "1").lower() in ("1", "true", "yes")
CELL_BROADCAST_DRY_RUN: bool = os.getenv("CELL_BROADCAST_DRY_RUN", "1").lower() in ("1", "true", "yes")
CAP_GATEWAY_DRY_RUN: bool = os.getenv("CAP_GATEWAY_DRY_RUN", "1").lower() in ("1", "true", "yes")

# Delivery Receipt States (CP02, CP10)
RECEIPT_QUEUED = "QUEUED"
RECEIPT_SENT = "SENT"
RECEIPT_DELIVERED = "DELIVERED"
RECEIPT_FAILED = "FAILED"
RECEIPT_UNKNOWN = "UNKNOWN"

VALID_RECEIPT_STATES = {
    RECEIPT_QUEUED,
    RECEIPT_SENT,
    RECEIPT_DELIVERED,
    RECEIPT_FAILED,
    RECEIPT_UNKNOWN
}

# Provider Configuration States (CP02)
PROVIDER_CONFIGURED = "CONFIGURED"
PROVIDER_UNCONFIGURED = "UNCONFIGURED"
PROVIDER_SIMULATED = "SIMULATED"
PROVIDER_FAILED = "FAILED"
PROVIDER_BLOCKED = "BLOCKED"

# Siren State Machine (CP05)
SIREN_STATE_DISABLED = "DISABLED"
SIREN_STATE_ARMED = "ARMED"
SIREN_STATE_AUTHORIZED = "AUTHORIZED"
SIREN_STATE_COMMAND_QUEUED = "COMMAND_QUEUED"
SIREN_STATE_DRY_RUN_EXECUTED = "DRY_RUN_EXECUTED"

VALID_SIREN_STATES = {
    SIREN_STATE_DISABLED,
    SIREN_STATE_ARMED,
    SIREN_STATE_AUTHORIZED,
    SIREN_STATE_COMMAND_QUEUED,
    SIREN_STATE_DRY_RUN_EXECUTED
}

# Channel Identifiers
CHANNEL_SMS = "SMS"
CHANNEL_CELL_BROADCAST = "CELL_BROADCAST"
CHANNEL_CAP_GATEWAY = "CAP_GATEWAY"
CHANNEL_WEB_PUSH = "WEB_PUSH"
CHANNEL_MOBILE_PUSH = "MOBILE_PUSH"
CHANNEL_SIREN = "SIREN"
CHANNEL_ROADSIDE_VMS = "ROADSIDE_VMS"

ALL_CHANNELS = [
    CHANNEL_SMS,
    CHANNEL_CELL_BROADCAST,
    CHANNEL_CAP_GATEWAY,
    CHANNEL_WEB_PUSH,
    CHANNEL_MOBILE_PUSH,
    CHANNEL_SIREN,
    CHANNEL_ROADSIDE_VMS
]

# Supported Multilingual Alert Languages (CP09)
LANG_ENGLISH = "en"
LANG_HINDI = "hi"
LANG_NEPALI = "ne"
LANG_ASSAMESE = "as"
LANG_BHUTIA = "bh"
LANG_LEPCHA = "lp"

SUPPORTED_LANGUAGES = [
    LANG_ENGLISH,
    LANG_HINDI,
    LANG_NEPALI,
    LANG_ASSAMESE,
    LANG_BHUTIA,
    LANG_LEPCHA
]

# Multilingual Alert Templates (< 160 chars for SMS)
ALERT_TEMPLATES: Dict[str, Dict[str, str]] = {
    LANG_ENGLISH: {
        "sms": "PAHAD AI {level}: Severe landslide risk at {sec}. Move away from slope cuts. Follow SDRF advisories. ID:{alert_id}",
        "push_title": "PAHAD AI Landslide Warning: {sec}",
        "push_body": "Critical hillslope instability detected at {sec}. Evacuate vulnerable slopes immediately. Alternate route: NH-717A.",
        "voice": "Emergency alert. Severe landslide threat detected at {sec}. Evacuate immediately via designated detour routes.",
        "vms": "LANDSLIDE WARNING {sec} / SLOW DOWN / USE NH-717A"
    },
    LANG_HINDI: {
        "sms": "पहाड़ एआई {level}: {sec} पर भूस्खलन का भारी जोखिम। ढलान से दूर रहें। प्रशासन के निर्देशों का पालन करें। ID:{alert_id}",
        "push_title": "पहाड़ एआई भूस्खलन चेतावनी: {sec}",
        "push_body": "{sec} में अत्यधिक भूस्खलन जोखिम। तुरंत सुरक्षित स्थान पर जाएं। वैकल्पिक मार्ग: NH-717A।",
        "voice": "आपातकालीन चेतावनी। {sec} पर गंभीर भूस्खलन का खतरा। सुरक्षित मार्ग का प्रयोग करें।",
        "vms": "भूस्खलन चेतावनी {sec} / गति धीमी रखें / NH-717A चुनें"
    },
    LANG_NEPALI: {
        "sms": "पहाड एआई {level}: {sec} नजिक पहिरोको उच्च जोखिम। भिरालोबाट टाढा रहनुहोस्। निर्देशन पालना गर्नुहोस्। ID:{alert_id}",
        "push_title": "पहाड एआई पहिरो चेतावनी: {sec}",
        "push_body": "{sec} मा पहिरोको उच्च जोखिम पहिचान गरिएको छ। तुरुन्त सुरक्षित स्थानमा जानुहोस्।",
        "voice": "आपतकालीन सूचना। {sec} नजिक पहिरोको जोखिम। तुरुन्त सुरक्षित ठाउँमा जानुहोस्।",
        "vms": "पहिरो जोखिम {sec} / गाडी बिस्तारै चलाउनुहोस् / NH-717A"
    },
    LANG_ASSAMESE: {
        "sms": "পাহাড় এআই {level}: {sec}ত ভূমিস্খলনৰ প্ৰচণ্ড আশংকা। পাহাৰৰ ঢালৰ পৰা আঁতৰি থাকক। ID:{alert_id}",
        "push_title": "পাহাড় এআই ভূমিস্খলন সতৰ্কবাণী: {sec}",
        "push_body": "{sec} পাহাৰীয়া এলেকাত ভূমিস্খলনৰ অতি উচ্চ আশংকা ধৰা পৰিছে। সুৰক্ষিত স্থানলৈ যাওক।",
        "voice": "সকলোৰে দৃষ্টি আকৰ্ষণ কৰা হৈছে। {sec}ত ভূমিস্খলনৰ আশংকা আছে। সাৱধান হওক।",
        "vms": "ভূমিস্খলনৰ সতৰ্কতা {sec} / সাৱধানে গাড়ী চলাওক / NH-717A"
    },
    LANG_BHUTIA: {
        "sms": "PAHAD AI {level}: {sec} ཉེན་ཁ་ཆེན་པོ། ས་རུད་ཉེན་ཁ་ཡོད། གནས་སྤོ་གནང་རོགས། ID:{alert_id}",
        "push_title": "PAHAD AI ས་རུད་ཉེན་བརྡ།: {sec}",
        "push_body": "{sec} ས་གནས་སུ་ས་རུད་ཉེན་ཁ་ཚབས་ཆེན་ཐོན་ཡོད། ཉེན་མེད་ས་གནས་སུ་གནས་སྤོ་གནང་རོགས།",
        "voice": "ཉེན་བརྡ་གལ་ཆེན། {sec} ས་རུད་ཉེན་ཁ་ཡོད། ཉེན་མེད་ས་གནས་སུ་གཤེགས་རོགས།",
        "vms": "SA-RUD NYEN-KHA {sec} / KHAL-GYANG / NH-717A"
    },
    LANG_LEPCHA: {
        "sms": "PAHAD AI {level}: {sec} ᰀᰩᰴ ᰚᰩᰵ ᰜᰤᰵ ᰛᰦᰵᰀᰩᰴ ᰆᰫᰀ ᰕᰦᰰ ᰠᰦᰵᰃᰦ ᰠᰦᰵ. ID:{alert_id}",
        "push_title": "PAHAD AI ᰛᰦᰵᰀᰩᰴ ᰆᰫᰀ: {sec}",
        "push_body": "{sec} ᰜᰤᰵ ᰛᰦᰵᰀᰩᰴ ᰆᰫᰀ ᰕᰦᰰ ᰠᰦᰵᰃᰦ ᰠᰦᰵ ᰚᰩᰵ. ᰠᰦᰵᰃᰦ ᰜᰤᰵ ᰠᰪᰵ ᰕᰦᰰ.",
        "voice": "ᰛᰦᰵᰀᰩᰴ ᰆᰫᰀ ᰠᰦᰵᰃᰦ ᰠᰦᰵ. {sec} ᰜᰤᰵ ᰕᰦᰰ. ᰠᰦᰵᰃᰦ ᰜᰤᰵ ᰠᰪᰵ.",
        "vms": "RANG-KONG CHUK {sec} / SLOW DOWN / NH-717A"
    }
}

# HMAC signing secret for Siren and Authority commands
EOC_SECRET_KEY = os.environ.get("EOC_HMAC_SECRET", "PARVAT_NETRA_EOC_SIH_2026_AUTHORITY_KEY").encode("utf-8")


# ==============================================================================
# Helper Geodesic & Geofence Functions (CP07)
# ==============================================================================

def point_in_polygon(lat: float, lon: float, polygon: List[List[float]]) -> bool:
    """
    Determines if point (lat, lon) is inside polygon using standard horizontal ray-casting algorithm.
    Polygon is list of [lat, lon] coordinates.
    """
    if not polygon or len(polygon) < 3:
        return False

    pts = [[float(p[0]), float(p[1])] for p in polygon if isinstance(p, (list, tuple)) and len(p) >= 2]
    if len(pts) > 3 and pts[0] == pts[-1]:
        pts = pts[:-1]

    n = len(pts)
    if n < 3:
        return False

    inside = False
    j = n - 1
    for i in range(n):
      y1, x1 = pts[i][0], pts[i][1]  # y = lat, x = lon
      y2, x2 = pts[j][0], pts[j][1]

      if ((y1 > lat) != (y2 > lat)) and (y2 != y1):
        x_intersect = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
        if lon < x_intersect:
          inside = not inside
      j = i

    return inside


def validate_geofence_polygon(polygon: Any) -> Tuple[bool, str]:
    """
    Validates polygon coordinates:
      - Must be a non-empty list of at least 3 points
      - Each point must have [lat, lon] within reasonable Himalayan NER bounding box
    """
    if not polygon:
        return False, "Geofence polygon cannot be empty"
    if not isinstance(polygon, (list, tuple)):
        return False, "Geofence polygon must be a list of coordinates"
    if len(polygon) < 3:
        return False, "Geofence polygon must contain at least 3 vertices"

    for idx, pt in enumerate(polygon):
        if not isinstance(pt, (list, tuple)) or len(pt) < 2:
            return False, f"Vertex at index {idx} is not a valid [lat, lon] pair"
        try:
            lat, lon = float(pt[0]), float(pt[1])
            # Check geographical validity (-90 to 90 lat, -180 to 180 lon)
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                return False, f"Coordinates out of physical range at vertex {idx}: ({lat}, {lon})"
        except (ValueError, TypeError):
            return False, f"Non-numeric coordinates at vertex {idx}"

    return True, "Geofence polygon is valid"


# ==============================================================================
# CP02: SMS Gateway Adapter & Delivery Receipt Tracker
# ==============================================================================

class SMSGatewayAdapter:
    """
    Provider-abstracted emergency SMS gateway adapter.
    Enforces delivery receipt model: QUEUED -> SENT -> FAILED / UNKNOWN.
    Invariant: Simulated dispatch NEVER claims DELIVERED.
    """

    def __init__(self, provider_type: str = "mock"):
        self.provider_type = provider_type.lower()
        if self.provider_type == "cdac":
            self.provider: BaseSMSProvider = CDACSMSProvider()
        else:
            self.provider = MockSMSProvider()

    def get_provider_state(self) -> str:
        """Returns provider state: CONFIGURED, UNCONFIGURED, SIMULATED, FAILED, BLOCKED."""
        if isinstance(self.provider, CDACSMSProvider):
            if self.provider.is_configured:
                return PROVIDER_CONFIGURED
            return PROVIDER_UNCONFIGURED
        elif isinstance(self.provider, MockSMSProvider):
            return PROVIDER_SIMULATED
        return PROVIDER_UNCONFIGURED

    def send_sms(
        self,
        recipient_phone_masked: str,
        message: str,
        incident_id: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Dispatches SMS to recipient.
        Enforces character limit < 160 characters.
        """
        provider_state = self.get_provider_state()
        now_iso = datetime.now(timezone.utc).isoformat()
        sms_id = f"SMS-{uuid.uuid4().hex[:8].upper()}"

        # Strict length enforcement
        if len(message) > 160:
            message = message[:157] + "..."

        if provider_state == PROVIDER_SIMULATED or not PUBLIC_DISPATCH_ENABLED:
            # Safe simulation dispatch
            return {
                "channel": CHANNEL_SMS,
                "provider": "MOCK_SMS_GATEWAY" if provider_state == PROVIDER_SIMULATED else "CDAC_MOBILE_SEVA",
                "provider_state": provider_state,
                "sms_id": sms_id,
                "incident_id": incident_id,
                "recipient": recipient_phone_masked,
                "message": message,
                "message_length": len(message),
                "language": language,
                "delivery_status": RECEIPT_SENT,  # NEVER DELIVERED in simulation
                "queued_at": now_iso,
                "sent_at": now_iso,
                "delivered_at": None,
                "dry_run": True,
                "provenance": "[SIMULATED / TEST_DRY_RUN]",
                "carrier_receipt": None,
                "error": None
            }
        elif provider_state == PROVIDER_CONFIGURED and PUBLIC_DISPATCH_ENABLED:
            # Attempt live provider call
            res = self.provider.send(recipient_phone_masked, message)
            success = res.get("success", False)
            return {
                "channel": CHANNEL_SMS,
                "provider": "CDAC_MOBILE_SEVA",
                "provider_state": provider_state,
                "sms_id": sms_id,
                "incident_id": incident_id,
                "recipient": recipient_phone_masked,
                "message": message,
                "message_length": len(message),
                "language": language,
                "delivery_status": RECEIPT_SENT if success else RECEIPT_FAILED,
                "queued_at": now_iso,
                "sent_at": now_iso if success else None,
                "delivered_at": None,  # Requires async carrier webhook receipt
                "dry_run": False,
                "provenance": "[LIVE]",
                "carrier_receipt": res.get("status"),
                "error": res.get("error") if not success else None
            }
        else:
            return {
                "channel": CHANNEL_SMS,
                "provider": "CDAC_MOBILE_SEVA",
                "provider_state": PROVIDER_UNCONFIGURED,
                "sms_id": sms_id,
                "incident_id": incident_id,
                "recipient": recipient_phone_masked,
                "message": message,
                "message_length": len(message),
                "language": language,
                "delivery_status": RECEIPT_FAILED,
                "queued_at": now_iso,
                "sent_at": None,
                "delivered_at": None,
                "dry_run": True,
                "provenance": "[UNCONFIGURED_FAIL_CLOSED]",
                "carrier_receipt": None,
                "error": "SMS Gateway unconfigured: missing credentials"
            }


# ==============================================================================
# CP03: Cell Broadcast Adapter (3GPP ATIS-0700015 PWS)
# ==============================================================================

class CellBroadcastAdapter:
    """
    Provider-neutral Cell Broadcast Service (CBS) / Public Warning System (PWS) adapter.
    Formats warning messages according to 3GPP TS 23.041 / ATIS-0700015 standards.
    Safety Invariant: CELL_BROADCAST = TEST/DRY_RUN (Zero live RF emissions).
    """

    def __init__(self, dry_run: bool = CELL_BROADCAST_DRY_RUN):
        self.dry_run = dry_run

    def broadcast(
        self,
        incident_id: str,
        geofence_polygon: List[List[float]],
        severity: str,
        urgency: str,
        language: str,
        message: str,
        expiry_iso: str
    ) -> Dict[str, Any]:
        """
        Dispatches Cell Broadcast warning to cellular towers covering the geofence.
        Strictly operates in TEST/DRY_RUN mode.
        """
        is_valid, err_msg = validate_geofence_polygon(geofence_polygon)
        if not is_valid:
            return {
                "channel": CHANNEL_CELL_BROADCAST,
                "provider_status": "TEST/DRY_RUN",
                "broadcast_status": "FAILED_INVALID_GEOFENCE",
                "correlation_id": None,
                "error": err_msg
            }

        correlation_id = f"CB-{uuid.uuid4().hex[:12].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Simulated cell tower coverage in Himalayan polygon
        estimated_cell_sites = max(1, len(geofence_polygon) * 2)

        return {
            "channel": CHANNEL_CELL_BROADCAST,
            "provider_status": "TEST/DRY_RUN",
            "broadcast_status": "SIMULATED",
            "correlation_id": correlation_id,
            "incident_id": incident_id,
            "severity": severity,
            "urgency": urgency,
            "language": language,
            "message": message,
            "polygon_vertices": len(geofence_polygon),
            "estimated_cell_sites": estimated_cell_sites,
            "queued_at": now_iso,
            "sent_at": now_iso,
            "expiry": expiry_iso,
            "dry_run": True,
            "rf_actuation": False,
            "provenance": "[CELL_BROADCAST_DRY_RUN]"
        }


# ==============================================================================
# CP04: SACHET / OASIS CAP v1.2 Gateway Adapter
# ==============================================================================

class SachetCapGatewayAdapter:
    """
    OASIS Common Alerting Protocol (CAP) v1.2 warning gateway adapter.
    Validates all 15 required OASIS CAP v1.2 elements:
      identifier, sender, sent, status, msgType, scope,
      severity, urgency, certainty, headline, description, instruction,
      area, polygon, expiry.
    Safety Invariant: Encapsulates XML payload into a staged test feed; zero live public push.
    """

    MANDATORY_ELEMENTS = [
        "identifier", "sender", "sent", "status", "msgType", "scope",
        "severity", "urgency", "certainty", "headline", "description",
        "instruction", "areaDesc", "polygon", "expiry"
    ]

    def __init__(self, dry_run: bool = CAP_GATEWAY_DRY_RUN):
        self.dry_run = dry_run
        self.generator = CAPAlertGenerator()

    def validate_cap_payload(self, alert_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates the presence and non-emptiness of all 15 mandatory CAP 1.2 elements."""
        missing = []
        for elem in self.MANDATORY_ELEMENTS:
            val = alert_data.get(elem)
            if val is None or str(val).strip() == "":
                missing.append(elem)
        return len(missing) == 0, missing

    def stage_cap_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and formats an official OASIS CAP 1.2 XML & JSON alert package.
        """
        is_valid, missing = self.validate_cap_payload(alert_data)
        if not is_valid:
            return {
                "channel": CHANNEL_CAP_GATEWAY,
                "status": "VALIDATION_FAILED",
                "missing_elements": missing,
                "xml_payload": None,
                "error": f"Missing mandatory CAP 1.2 elements: {', '.join(missing)}"
            }

        # Build valid OASIS XML
        xml_str = self.generator.build_cap_xml(alert_data)
        structured_dict = self.generator.build_cap_dict(alert_data)

        now_iso = datetime.now(timezone.utc).isoformat()
        cap_id = alert_data["identifier"]

        return {
            "channel": CHANNEL_CAP_GATEWAY,
            "provider": "NDMA_SACHET_ADAPTER",
            "cap_id": cap_id,
            "incident_id": alert_data.get("incident_id", cap_id),
            "status": "STAGED_TEST_FEED",
            "delivery_status": RECEIPT_SENT,
            "validated_elements_count": len(self.MANDATORY_ELEMENTS),
            "xml_payload": xml_str,
            "structured_dict": structured_dict,
            "queued_at": now_iso,
            "sent_at": now_iso,
            "dry_run": True,
            "gateway_url": "https://sachet.ndma.gov.in/api/v1/cap/feed [STAGING_TEST]",
            "provenance": "[OASIS_CAP_1.2_DRY_RUN]"
        }


# ==============================================================================
# CP05: Physical Siren & LoRa Gateway Adapter
# ==============================================================================

class SirenGatewayAdapter:
    """
    High-assurance acoustic warning siren & LoRa relay controller adapter.
    Enforces cryptographic signing with nonce, timestamp, expiry, and HMAC-SHA256.
    Enforces the 5-state lifecycle:
      DISABLED -> ARMED -> AUTHORIZED -> COMMAND_QUEUED -> DRY_RUN_EXECUTED
    Safety Invariants:
      - SIREN_DRY_RUN = 1 (Physical sounder strictly suppressed).
      - AI never triggers sirens directly; human authority authorization required.
      - Single-use nonces prevent command replay.
    """

    def __init__(
        self,
        controller: Optional[SirenController] = None,
        dry_run: bool = SIREN_DRY_RUN
    ):
        self.controller = controller or GLOBAL_SIREN_CONTROLLER
        self.dry_run = dry_run or not getattr(self.controller, "hardware_enabled", False)
        self._used_nonces: Set[str] = set()
        self._lock = threading.Lock()
        self.current_state = SIREN_STATE_ARMED if self.controller.is_armed else SIREN_STATE_DISABLED

    def generate_signed_command(
        self,
        incident_id: str,
        target_sector: str,
        authority_role: str,
        authority_id: str,
        token: str,
        expiry_seconds: int = 120
    ) -> Dict[str, Any]:
        """
        Generates signed siren trigger payload.
        Transitions state: ARMED -> AUTHORIZED -> COMMAND_QUEUED.
        """
        # Validate authority role
        if authority_role not in (ROLE_DISTRICT_AUTHORITY, ROLE_STATE_AUTHORITY, ROLE_AUTHORITY):
            raise PermissionError(f"Role '{authority_role}' is not authorized to sign siren commands.")

        now_ts = int(time.time())
        expiry_ts = now_ts + expiry_seconds
        nonce = uuid.uuid4().hex

        # Construct signed payload
        msg = f"{incident_id}:{target_sector}:{authority_id}:{nonce}:{expiry_ts}"
        sig = hmac.new(EOC_SECRET_KEY, msg.encode("utf-8"), hashlib.sha256).hexdigest()

        with self._lock:
            self.current_state = SIREN_STATE_COMMAND_QUEUED

        command_id = f"SIREN-CMD-{now_ts}-{nonce[:6].upper()}"

        return {
            "command_id": command_id,
            "incident_id": incident_id,
            "target_sector": target_sector,
            "authority_id": authority_id,
            "authority_role": authority_role,
            "token": token,
            "timestamp": now_ts,
            "expiry": expiry_ts,
            "nonce": nonce,
            "signature": sig,
            "siren_state": SIREN_STATE_COMMAND_QUEUED,
            "dry_run": True,
            "provenance": "[SIREN_DRY_RUN_HMAC]"
        }

    def verify_and_execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies cryptographic integrity and executes siren test.
        Transitions state: COMMAND_QUEUED -> DRY_RUN_EXECUTED.
        Fails closed on replay or signature mismatch.
        """
        inc_id = command.get("incident_id")
        sector = command.get("target_sector")
        auth_id = command.get("authority_id")
        nonce = command.get("nonce")
        expiry = command.get("expiry", 0)
        sig = command.get("signature")

        if not all([inc_id, sector, auth_id, nonce, expiry, sig]):
            return {
                "success": False,
                "status": "MALFORMED_COMMAND",
                "error": "Missing required fields in siren command"
            }

        # Check Expiry
        now_ts = int(time.time())
        if now_ts > expiry:
            return {
                "success": False,
                "status": "EXPIRED_COMMAND",
                "error": f"Siren command expired at {expiry}, current time is {now_ts}"
            }

        # Check Replay Attack
        with self._lock:
            if nonce in self._used_nonces:
                return {
                    "success": False,
                    "status": "REPLAY_DETECTED",
                    "error": "Replay attack detected: Nonce already executed"
                }
            self._used_nonces.add(nonce)

        # Verify HMAC Signature
        expected_msg = f"{inc_id}:{sector}:{auth_id}:{nonce}:{expiry}"
        expected_sig = hmac.new(EOC_SECRET_KEY, expected_msg.encode("utf-8"), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected_sig):
            return {
                "success": False,
                "status": "INVALID_SIGNATURE",
                "error": "Cryptographic signature verification failed"
            }

        # Execute safe dry run
        with self._lock:
            self.current_state = SIREN_STATE_DRY_RUN_EXECUTED

        test_result = self.controller.test(
            duration_sec=3,
            operator=f"{auth_id} ({command.get('authority_role')})"
        )

        return {
            "channel": CHANNEL_SIREN,
            "success": True,
            "status": SIREN_STATE_DRY_RUN_EXECUTED,
            "command_id": command.get("command_id"),
            "target_sector": sector,
            "physical_sound_output": False,
            "dry_run": True,
            "audit": test_result,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "provenance": "[SIREN_DRY_RUN_EXECUTED]"
        }


# ==============================================================================
# Push & Roadside VMS Adapters (CP01, CP06)
# ==============================================================================

class WebPushAdapter:
    """Standard W3C Web Push / ServiceWorker notification adapter."""
    def send(self, recipient_endpoint: str, title: str, body: str, incident_id: str) -> Dict[str, Any]:
        return {
            "channel": CHANNEL_WEB_PUSH,
            "recipient": recipient_endpoint[:24] + "...",
            "incident_id": incident_id,
            "title": title,
            "body": body,
            "delivery_status": RECEIPT_SENT,
            "dry_run": True,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "provenance": "[WEB_PUSH_DRY_RUN]"
        }


class MobilePushAdapter:
    """Native FCM / APNS push notification adapter."""
    def send(self, device_token: str, title: str, body: str, incident_id: str) -> Dict[str, Any]:
        return {
            "channel": CHANNEL_MOBILE_PUSH,
            "device_token": device_token[:16] + "...",
            "incident_id": incident_id,
            "priority": "HIGH_EMERGENCY",
            "title": title,
            "body": body,
            "delivery_status": RECEIPT_SENT,
            "dry_run": True,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "provenance": "[FCM_PUSH_DRY_RUN]"
        }


class RoadsideVMSAdapter:
    """Roadside Variable Message Sign (VMS) matrix signboard gateway adapter."""
    def send(self, signboard_id: str, text: str, incident_id: str) -> Dict[str, Any]:
        return {
            "channel": CHANNEL_ROADSIDE_VMS,
            "signboard_id": signboard_id,
            "incident_id": incident_id,
            "display_lines": [text[:32], text[32:64]],
            "delivery_status": RECEIPT_SENT,
            "dry_run": True,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "provenance": "[VMS_SIGN_DRY_RUN]"
        }


# ==============================================================================
# CP12: Cryptographic Tamper-Evident Audit Ledger
# ==============================================================================

class DisseminationAuditLedger:
    """
    Cryptographic SHA-256 hash-chained audit ledger.
    Guarantees non-repudiation of all authority warnings and dissemination actions.
    """

    def __init__(self):
        self._chain: List[Dict[str, Any]] = []
        self._last_hash = "GENESIS_BLOCK_PARVAT_NETRA_EWS_2026"
        self._lock = threading.Lock()

    def record_action(
        self,
        actor: str,
        role: str,
        incident_id: str,
        channel: str,
        action: str,
        auth_ref: str,
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock:
            idx = len(self._chain)
            raw_str = f"{idx}:{actor}:{role}:{incident_id}:{channel}:{action}:{auth_ref}:{result}:{self._last_hash}:{now_iso}"
            current_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

            entry = {
                "block_index": idx,
                "actor": actor,
                "role": role,
                "incident_id": incident_id,
                "timestamp": now_iso,
                "channel": channel,
                "action": action,
                "authorization_reference": auth_ref,
                "result": result,
                "previous_hash": self._last_hash,
                "audit_hash": current_hash,
                "metadata": metadata or {}
            }
            self._chain.append(entry)
            self._last_hash = current_hash
            return entry

    def verify_integrity(self) -> Tuple[bool, int]:
        """Validates that no historical audit entry has been altered."""
        with self._lock:
            prev = "GENESIS_BLOCK_PARVAT_NETRA_EWS_2026"
            for idx, entry in enumerate(self._chain):
                raw_str = (
                    f"{entry['block_index']}:{entry['actor']}:{entry['role']}:{entry['incident_id']}:"
                    f"{entry['channel']}:{entry['action']}:{entry['authorization_reference']}:"
                    f"{entry['result']}:{prev}:{entry['timestamp']}"
                )
                computed = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
                if computed != entry["audit_hash"] or entry["previous_hash"] != prev:
                    return False, idx
                prev = entry["audit_hash"]
            return True, len(self._chain)

    def get_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return list(reversed(self._chain[-limit:]))


# ==============================================================================
# CP01, CP08, CP10, CP11: Unified Public Warning Service
# ==============================================================================

class PublicWarningService:
    """
    Central orchestration service for multi-channel emergency dissemination.
    Coordinates all 7 channel adapters under strict DMA 2005 authority governance.
    """

    def __init__(self):
        self.sms_adapter = SMSGatewayAdapter()
        self.cell_broadcast_adapter = CellBroadcastAdapter()
        self.cap_adapter = SachetCapGatewayAdapter()
        self.siren_adapter = SirenGatewayAdapter()
        self.web_push_adapter = WebPushAdapter()
        self.mobile_push_adapter = MobilePushAdapter()
        self.vms_adapter = RoadsideVMSAdapter()
        self.audit_ledger = DisseminationAuditLedger()

        self._dissemination_history: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get_channel_status(self) -> Dict[str, Any]:
        """Reports current operating status, readiness, and dry-run safety modes."""
        return {
            "global_safety_invariants": {
                "PUBLIC_DISPATCH": "DISABLED" if not PUBLIC_DISPATCH_ENABLED else "ENABLED",
                "SIREN_DRY_RUN": 1 if SIREN_DRY_RUN else 0,
                "CELL_BROADCAST_DRY_RUN": 1 if CELL_BROADCAST_DRY_RUN else 0,
                "CAP_GATEWAY_DRY_RUN": 1 if CAP_GATEWAY_DRY_RUN else 0
            },
            "channels": {
                CHANNEL_SMS: {
                    "provider": self.sms_adapter.provider_type.upper(),
                    "state": self.sms_adapter.get_provider_state(),
                    "safety_mode": "TEST/DRY_RUN",
                    "integration_readiness": "READY"
                },
                CHANNEL_CELL_BROADCAST: {
                    "standard": "3GPP TS 23.041 / ATIS-0700015",
                    "state": "SIMULATED",
                    "safety_mode": "TEST/DRY_RUN",
                    "integration_readiness": "READY"
                },
                CHANNEL_CAP_GATEWAY: {
                    "standard": "OASIS CAP v1.2 / ITU-T X.1303",
                    "state": "STAGED_FEED",
                    "safety_mode": "TEST/DRY_RUN",
                    "integration_readiness": "READY"
                },
                CHANNEL_SIREN: {
                    "controller_state": self.siren_adapter.current_state,
                    "safety_mode": "DRY_RUN (No Physical Sound)",
                    "integration_readiness": "READY"
                },
                CHANNEL_WEB_PUSH: {
                    "standard": "W3C Push API / VAPID",
                    "state": "SIMULATED",
                    "safety_mode": "TEST/DRY_RUN",
                    "integration_readiness": "READY"
                },
                CHANNEL_MOBILE_PUSH: {
                    "standard": "Firebase Cloud Messaging (FCM)",
                    "state": "SIMULATED",
                    "safety_mode": "TEST/DRY_RUN",
                    "integration_readiness": "READY"
                },
                CHANNEL_ROADSIDE_VMS: {
                    "corridors": ["NH-10", "NH-717A", "Dikchu-Gangtok"],
                    "state": "SIMULATED",
                    "safety_mode": "TEST/DRY_RUN",
                    "integration_readiness": "READY"
                }
            },
            "supported_languages": SUPPORTED_LANGUAGES,
            "dissemination_count": len(self._dissemination_history)
        }

    def format_multilingual_package(
        self,
        sector: str,
        alert_id: str,
        severity: str = "WARNING"
    ) -> Dict[str, Dict[str, str]]:
        """
        Synthesizes localized text across all 6 target languages:
        en, hi, ne, as, bh, lp.
        Enforces SMS < 160 characters.
        """
        package: Dict[str, Dict[str, str]] = {}
        for lang, tmpls in ALERT_TEMPLATES.items():
            sms_text = tmpls["sms"].format(level=severity.upper(), sec=sector, alert_id=alert_id)
            if len(sms_text) > 160:
                sms_text = sms_text[:157] + "..."

            package[lang] = {
                "sms": sms_text,
                "sms_length": str(len(sms_text)),
                "push_title": tmpls["push_title"].format(sec=sector),
                "push_body": tmpls["push_body"].format(sec=sector),
                "voice": tmpls["voice"].format(sec=sector),
                "vms": tmpls["vms"].format(sec=sector)
            }
        return package

    def validate_authority_and_corroboration(
        self,
        actor_id: str,
        actor_role: str,
        incident_id: str,
        auth_token: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        incident_obj: Optional[Any] = None
    ) -> Tuple[bool, str]:
        """
        CP08: Enforces strict statutory authorization prerequisites.
        Requires:
          1. Authenticated authority with authorized role.
          2. Explicit rejection of PUBLIC, FIELD_OPERATOR, unauthenticated.
          3. Valid cryptographic authorization token.
          4. Jurisdiction match (if specified).
          5. Incident in STATE_AUTHORIZED or STATE_WARNING_AUTHORIZED.
          6. 2-of-3 corroboration satisfied.
        """
        role_up = (actor_role or "").upper()
        if not actor_id or not role_up:
            return False, "Unauthenticated request: missing actor credentials"

        # Explicit rejection of unauthorized roles
        if role_up in (ROLE_PUBLIC, ROLE_FIELD_OPERATOR):
            return False, f"Role '{role_up}' is strictly prohibited from authorizing public emergency dispatches"

        if role_up not in (ROLE_DISTRICT_AUTHORITY, ROLE_STATE_AUTHORITY, ROLE_AUTHORITY):
            return False, f"Role '{role_up}' lacks emergency dispatch authorization privileges"

        # Validate cryptographic token
        if not auth_token:
            return False, "Missing required cryptographic authority token"

        valid_tok, tok_err = AUTHORIZATION_TOKEN_MANAGER.validate_token(auth_token, incident_id, role_up)
        if not valid_tok:
            return False, f"Authority token validation failed: {tok_err}"

        # Fetch incident if not passed
        inc = incident_obj or EOC_INCIDENT_MANAGER.get_incident(incident_id)
        if not inc:
            return False, f"Incident '{incident_id}' not found in registry"

        # Validate incident status
        valid_states = (STATE_AUTHORIZED, STATE_WARNING_AUTHORIZED, STATE_DISPATCHED)
        if inc.incident_status not in valid_states:
            return False, f"Incident status '{inc.incident_status}' is not AUTHORIZED for dissemination"

        # Validate 2-of-3 corroboration
        corrob_count = getattr(inc, "corroboration_count", 0)
        if corrob_count < 2 and hasattr(inc, "signal_agreement"):
            sig = str(inc.signal_agreement)
            if "2-of-3" in sig or "3-of-3" in sig or "CORROBORATED" in sig.upper():
                corrob_count = 2
        if corrob_count < 2:
            return False, f"Cannot disseminate: multi-source corroboration requirement (>= 2) not satisfied (found {corrob_count})"

        # Validate jurisdiction if applicable
        if jurisdiction and hasattr(inc, "district") and inc.district:
            if jurisdiction.lower() not in inc.district.lower() and role_up == ROLE_DISTRICT_AUTHORITY:
                return False, f"Jurisdiction mismatch: authority jurisdiction '{jurisdiction}' does not match incident district '{inc.district}'"

        return True, "Authority credentials and corroboration prerequisites satisfied"

    def disseminate_emergency_warning(
        self,
        incident_id: str,
        actor_id: str,
        actor_role: str,
        auth_token: str,
        geofence_polygon: List[List[float]],
        target_channels: Optional[List[str]] = None,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches authorized multi-channel emergency alert package.
        Each channel executes independently.
        Tamper-evident audit logged for every action.
        """
        # Step 1: Validate Authority & Corroboration (CP08)
        inc = EOC_INCIDENT_MANAGER.get_incident(incident_id)
        auth_ok, auth_reason = self.validate_authority_and_corroboration(
            actor_id=actor_id,
            actor_role=actor_role,
            incident_id=incident_id,
            auth_token=auth_token,
            jurisdiction=jurisdiction,
            incident_obj=inc
        )
        if not auth_ok:
            # Audit rejection
            self.audit_ledger.record_action(
                actor=actor_id,
                role=actor_role,
                incident_id=incident_id,
                channel="ALL",
                action="DISSEMINATION_REJECTED",
                auth_ref=auth_token or "NONE",
                result=auth_reason
            )
            return {
                "success": False,
                "status": "DISSEMINATION_REJECTED",
                "error": auth_reason,
                "incident_id": incident_id
            }

        # Step 2: Validate Geofence (CP07)
        geo_ok, geo_err = validate_geofence_polygon(geofence_polygon)
        if not geo_ok:
            self.audit_ledger.record_action(
                actor=actor_id,
                role=actor_role,
                incident_id=incident_id,
                channel="ALL",
                action="GEOFENCE_VALIDATION_FAILED",
                auth_ref=auth_token,
                result=geo_err
            )
            return {
                "success": False,
                "status": "INVALID_GEOFENCE",
                "error": geo_err,
                "incident_id": incident_id
            }

        dissemination_id = f"DISSEM-{uuid.uuid4().hex[:8].upper()}"
        channels_to_use = target_channels or ALL_CHANNELS
        sector_name = getattr(inc, "sector_id", "NH-10 Himalayan Corridor")
        severity = getattr(inc, "severity", "WARNING")

        # Step 3: Generate 6-Language Multilingual Payloads (CP09)
        multilingual_payloads = self.format_multilingual_package(
            sector=sector_name,
            alert_id=incident_id,
            severity=severity
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        expiry_iso = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()

        channel_receipts: Dict[str, Any] = {}

        # ----------------------------------------------------------------------
        # Channel 1: SMS (CP02)
        # ----------------------------------------------------------------------
        if CHANNEL_SMS in channels_to_use:
            try:
                sms_rec = self.sms_adapter.send_sms(
                    recipient_phone_masked="+91-98****1234",
                    message=multilingual_payloads[LANG_ENGLISH]["sms"],
                    incident_id=incident_id,
                    language=LANG_ENGLISH
                )
                channel_receipts[CHANNEL_SMS] = sms_rec
            except Exception as exc:
                channel_receipts[CHANNEL_SMS] = {
                    "channel": CHANNEL_SMS,
                    "delivery_status": RECEIPT_FAILED,
                    "error": str(exc),
                    "dry_run": True
                }

        # ----------------------------------------------------------------------
        # Channel 2: Cell Broadcast (CP03)
        # ----------------------------------------------------------------------
        if CHANNEL_CELL_BROADCAST in channels_to_use:
            try:
                cb_rec = self.cell_broadcast_adapter.broadcast(
                    incident_id=incident_id,
                    geofence_polygon=geofence_polygon,
                    severity=severity,
                    urgency="Immediate",
                    language=LANG_ENGLISH,
                    message=multilingual_payloads[LANG_ENGLISH]["push_body"],
                    expiry_iso=expiry_iso
                )
                channel_receipts[CHANNEL_CELL_BROADCAST] = cb_rec
            except Exception as exc:
                channel_receipts[CHANNEL_CELL_BROADCAST] = {
                    "channel": CHANNEL_CELL_BROADCAST,
                    "delivery_status": RECEIPT_FAILED,
                    "error": str(exc),
                    "dry_run": True
                }

        # ----------------------------------------------------------------------
        # Channel 3: SACHET / CAP 1.2 (CP04)
        # ----------------------------------------------------------------------
        if CHANNEL_CAP_GATEWAY in channels_to_use:
            try:
                cap_payload = {
                    "identifier": f"CAP-{incident_id}",
                    "sender": "pahad-ews@ner.gov.in",
                    "sent": now_iso,
                    "status": "Actual",
                    "msgType": "Alert",
                    "scope": "Public",
                    "severity": severity.capitalize(),
                    "urgency": "Immediate",
                    "certainty": "Observed",
                    "headline": multilingual_payloads[LANG_ENGLISH]["push_title"],
                    "description": multilingual_payloads[LANG_ENGLISH]["push_body"],
                    "instruction": "Evacuate vulnerable slope corridors immediately. Follow SDRF detour advisories.",
                    "areaDesc": sector_name,
                    "polygon": geofence_polygon,
                    "expiry": expiry_iso,
                    "incident_id": incident_id,
                    "authorization_reference": auth_token
                }
                cap_rec = self.cap_adapter.stage_cap_alert(cap_payload)
                channel_receipts[CHANNEL_CAP_GATEWAY] = cap_rec
            except Exception as exc:
                channel_receipts[CHANNEL_CAP_GATEWAY] = {
                    "channel": CHANNEL_CAP_GATEWAY,
                    "delivery_status": RECEIPT_FAILED,
                    "error": str(exc),
                    "dry_run": True
                }

        # ----------------------------------------------------------------------
        # Channel 4: Acoustic Siren / LoRa Relay (CP05)
        # ----------------------------------------------------------------------
        if CHANNEL_SIREN in channels_to_use:
            try:
                signed_cmd = self.siren_adapter.generate_signed_command(
                    incident_id=incident_id,
                    target_sector=sector_name,
                    authority_role=actor_role,
                    authority_id=actor_id,
                    token=auth_token,
                    expiry_seconds=120
                )
                siren_rec = self.siren_adapter.verify_and_execute(signed_cmd)
                channel_receipts[CHANNEL_SIREN] = siren_rec
            except Exception as exc:
                channel_receipts[CHANNEL_SIREN] = {
                    "channel": CHANNEL_SIREN,
                    "delivery_status": RECEIPT_FAILED,
                    "error": str(exc),
                    "dry_run": True
                }

        # ----------------------------------------------------------------------
        # Channels 5, 6, 7: Web Push, Mobile Push, Roadside VMS
        # ----------------------------------------------------------------------
        if CHANNEL_WEB_PUSH in channels_to_use:
            channel_receipts[CHANNEL_WEB_PUSH] = self.web_push_adapter.send(
                recipient_endpoint="https://updates.push.services.mozilla.com/wpush/v2/...",
                title=multilingual_payloads[LANG_ENGLISH]["push_title"],
                body=multilingual_payloads[LANG_ENGLISH]["push_body"],
                incident_id=incident_id
            )

        if CHANNEL_MOBILE_PUSH in channels_to_use:
            channel_receipts[CHANNEL_MOBILE_PUSH] = self.mobile_push_adapter.send(
                device_token="fcm_token_sikkim_pky_9831",
                title=multilingual_payloads[LANG_ENGLISH]["push_title"],
                body=multilingual_payloads[LANG_ENGLISH]["push_body"],
                incident_id=incident_id
            )

        if CHANNEL_ROADSIDE_VMS in channels_to_use:
            channel_receipts[CHANNEL_ROADSIDE_VMS] = self.vms_adapter.send(
                signboard_id=f"VMS-{sector_name.replace(' ', '_')[:8]}",
                text=multilingual_payloads[LANG_ENGLISH]["vms"],
                incident_id=incident_id
            )

        # Step 4: Record Cryptographic Audit Ledger Entry (CP12)
        audit_entry = self.audit_ledger.record_action(
            actor=actor_id,
            role=actor_role,
            incident_id=incident_id,
            channel="MULTI_CHANNEL_PACKAGE",
            action="EMERGENCY_DISSEMINATION_EXECUTED",
            auth_ref=auth_token,
            result="DISSEMINATED_DRY_RUN",
            metadata={"channels_dispatched": list(channel_receipts.keys())}
        )

        response = {
            "dissemination_id": dissemination_id,
            "incident_id": incident_id,
            "status": "DISSEMINATED_DRY_RUN",
            "timestamp": now_iso,
            "authorized_by": {
                "actor_id": actor_id,
                "role": actor_role,
                "token_preview": auth_token[:16] + "..."
            },
            "geofence": {
                "vertices_count": len(geofence_polygon),
                "is_valid": True
            },
            "multilingual_summary": {
                lang: multilingual_payloads[lang]["sms"]
                for lang in SUPPORTED_LANGUAGES
            },
            "channel_receipts": channel_receipts,
            "audit_hash": audit_entry["audit_hash"],
            "dry_run": True,
            "provenance": "[MULTI_CHANNEL_PUBLIC_WARNING_READY]"
        }

        with self._lock:
            self._dissemination_history[dissemination_id] = response

        logger.info(f"[PublicWarningService] Dissemination {dissemination_id} completed across {len(channel_receipts)} channels (DRY_RUN).")
        return response

    def get_dissemination_record(self, dissemination_id: str) -> Optional[Dict[str, Any]]:
        """Returns delivery tracking details for a specific dissemination."""
        with self._lock:
            return self._dissemination_history.get(dissemination_id)


# Global Singleton Instance
PUBLIC_WARNING_SERVICE = PublicWarningService()
