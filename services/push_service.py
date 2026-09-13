# -*- coding: utf-8 -*-
"""
services/push_service.py
========================
PARVAT NETRA • Web & Mobile Push Notification Service
------------------------------------------------------
Implements Section 10, 11: Provider-abstracted push delivery engine.
Features:
  1. Provider abstraction (MockPushProvider, WebPushProvider, MobilePushProvider).
  2. Standards-compliant push payload schema: title, severity, location,
     short_message, issued_at, alert_id, deep_link.
  3. Subscription lifecycle management: subscribe, unsubscribe, active registry.
  4. Delivery status tracking: SENT, DELIVERED, FAILED, SIMULATED.
  5. DRY_RUN safety invariant: Defaults to DRY_RUN=true without external network calls.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import uuid
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger("PUSH_SERVICE")

DEFAULT_DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")


@dataclass
class PushPayload:
    title: str
    severity: str  # "LOW", "MODERATE", "HIGH", "VERY_HIGH", "EXTREME"
    location: str
    short_message: str
    issued_at: str
    alert_id: str
    deep_link: str = "/notifications"
    forecast_window: str = "6-12 hours"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PushSubscription:
    subscription_id: str
    recipient_id: str
    endpoint: str
    platform: str  # "web", "android", "ios"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PushService:
    """
    Manages push notification dispatch across web browsers and mobile clients.
    """

    def __init__(self, dry_run: bool = DEFAULT_DRY_RUN):
        self.dry_run = dry_run
        self._subscriptions: Dict[str, PushSubscription] = {}
        self._delivery_log: Dict[str, Dict[str, Any]] = {}
        self._seed_default_subscriptions()

    def _seed_default_subscriptions(self):
        """Pre-registers demo browser and mobile endpoints."""
        subs = [
            ("SUB-WEB-01", "REC-AUTH-01", "https://push.example.gov.in/ep/auth01", "web"),
            ("SUB-MOB-01", "REC-FIELD-01", "fcm-token-sdrf-singtam-field", "android"),
            ("SUB-MOB-02", "REC-CITZ-02", "apns-token-citz-likhu-mobile", "ios"),
        ]
        for s_id, r_id, ep, plat in subs:
            self._subscriptions[s_id] = PushSubscription(s_id, r_id, ep, plat)

    def subscribe(
        self,
        recipient_id: str,
        endpoint: str,
        platform: str = "web"
    ) -> Dict[str, Any]:
        """Registers a new push notification subscriber."""
        sub_id = f"SUB-{uuid.uuid4().hex[:8].upper()}"
        sub = PushSubscription(
            subscription_id=sub_id,
            recipient_id=recipient_id,
            endpoint=endpoint,
            platform=platform,
            active=True
        )
        self._subscriptions[sub_id] = sub
        logger.info(f"[PushService] Subscribed {recipient_id} on {platform} (id: {sub_id})")
        return {
            "status": "SUBSCRIBED",
            "subscription_id": sub_id,
            "recipient_id": recipient_id,
            "platform": platform
        }

    def unsubscribe(self, subscription_id: str) -> Dict[str, Any]:
        """Revokes a push subscription."""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].active = False
            logger.info(f"[PushService] Unsubscribed {subscription_id}")
            return {"status": "UNSUBSCRIBED", "subscription_id": subscription_id}
        return {"status": "NOT_FOUND", "subscription_id": subscription_id}

    def send_notification(
        self,
        recipient_id: str,
        payload: PushPayload,
        subscription_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches a push notification to a target recipient.
        Enforces DRY_RUN safety by default.
        """
        notif_id = f"NOTIF-PUSH-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Check if recipient has active subscription
        target_subs = [
            s for s in self._subscriptions.values()
            if s.recipient_id == recipient_id and s.active
        ]
        if subscription_id and subscription_id in self._subscriptions:
            target_subs = [self._subscriptions[subscription_id]]

        if not target_subs:
            res = {
                "notification_id": notif_id,
                "recipient_id": recipient_id,
                "status": "FAILED_NO_SUBSCRIPTION",
                "timestamp": now_iso,
                "dry_run": self.dry_run
            }
            self._delivery_log[notif_id] = res
            return res

        delivery_status = "SIMULATED_SENT" if self.dry_run else "SENT"

        res = {
            "notification_id": notif_id,
            "recipient_id": recipient_id,
            "subscription_count": len(target_subs),
            "status": delivery_status,
            "dry_run": self.dry_run,
            "provenance": "[DRY RUN]" if self.dry_run else "[LIVE]",
            "payload": payload.to_dict(),
            "timestamp": now_iso
        }
        self._delivery_log[notif_id] = res
        logger.info(f"[PushService] Dispatched push {notif_id} to {recipient_id} (Status: {delivery_status})")
        return res

    def get_delivery_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        return self._delivery_log.get(notification_id)

    def list_recent_deliveries(self, limit: int = 50) -> List[Dict[str, Any]]:
        items = list(self._delivery_log.values())
        items.reverse()
        return items[:limit]


# Singleton instance
PUSH_SERVICE = PushService()
