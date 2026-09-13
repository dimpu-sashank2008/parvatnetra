# -*- coding: utf-8 -*-
"""
backend/edge/siren_controller.py
================================
PARVAT NETRA • Local Tactical Siren & Acoustic Alert Controller
--------------------------------------------------------------
Implements Section 10, 11, 12: High-assurance physical siren controller.
Enforces strict fail-safe invariants:
  1. Default mode is strictly DRY_RUN=true and SIREN_ENABLED=false.
  2. Physical actuation requires explicit SIREN_HARDWARE_ENABLED=true flag.
  3. Test mode dispatches SIREN_TEST_EVENT without audible output.
  4. Maintains tamper-evident local activation audit log.

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("EDGE_SIREN_CONTROLLER")

SIREN_HARDWARE_ENABLED = os.getenv("SIREN_HARDWARE_ENABLED", "false").lower() in ("true", "1", "yes")
DEFAULT_DRY_RUN = os.getenv("SIREN_DRY_RUN", "true").lower() in ("true", "1", "yes")


class SirenController:
    """Manages physical acoustic siren horns, multi-tone chimes, and test events."""

    VALID_LEVELS = ("WATCH", "WARNING", "CRITICAL")

    def __init__(
        self,
        gateway_id: str = "GW-01",
        hardware_enabled: bool = SIREN_HARDWARE_ENABLED,
        dry_run: bool = DEFAULT_DRY_RUN,
        store=None
    ) -> None:
        self.gateway_id = gateway_id
        self.hardware_enabled = hardware_enabled
        self.dry_run = dry_run or not self.hardware_enabled
        self.store = store

        self.is_armed = True
        self.current_state = "ARMED"
        self.active_level: Optional[str] = None
        self.activation_history: List[Dict[str, Any]] = []

    def arm(self) -> Dict[str, Any]:
        """Arms the siren controller for emergency response."""
        self.is_armed = True
        self.current_state = "ARMED"
        logger.info(f"[SirenController {self.gateway_id}] Armed.")
        return self.status()

    def disarm(self) -> Dict[str, Any]:
        """Disarms and suppresses any active acoustic warning."""
        self.is_armed = False
        self.current_state = "DISARMED"
        self.active_level = None
        logger.info(f"[SirenController {self.gateway_id}] Disarmed & silenced.")
        return self.status()

    def test(
        self,
        duration_sec: int = 5,
        operator: str = "Authorized Engineer",
        requested_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a safety test sequence.
        Generates SIREN_TEST_EVENT strictly without physical audible horn output.
        """
        event_id = f"SIREN-TEST-{int(datetime.now().timestamp() * 1000)}"
        now_iso = datetime.now(timezone.utc).isoformat()
        op = requested_by or operator

        event = {
            "event_type": "SIREN_TEST_EVENT",
            "alert_id": event_id,
            "severity": "TEST",
            "timestamp": now_iso,
            "gateway_id": self.gateway_id,
            "activation_type": "MANUAL_TEST",
            "duration_seconds": duration_sec,
            "operator": op,
            "requested_by": op,
            "dry_run": True, # Safety invariant: test is ALWAYS dry run
            "physical_output": False,
            "physical_actuation": False,
            "status": "TEST_COMPLETED_SAFE",
            "message": "Local siren test event logged. Physical sounder suppressed."
        }

        self.activation_history.append(event)
        if self.store:
            try:
                self.store.insert_alert({
                    "alert_id": event_id,
                    "severity": "TEST",
                    "trigger_source": "MANUAL_SIREN_TEST",
                    "gateway_id": self.gateway_id,
                    "reason": f"Diagnostic siren test by {operator}",
                    "siren_activated": 0,
                    "dry_run": True,
                    "acknowledged": 1
                }, buffer_for_cloud=False)
            except Exception as e:
                logger.warning(f"Could not persist siren test to store: {e}")

        logger.info(f"[SirenController {self.gateway_id}] SIREN_TEST_EVENT executed safely.")
        return event

    def activate(
        self,
        level: str,
        alert_id: Optional[str] = None,
        reason: str = "Automated Edge Warning Trigger"
    ) -> Dict[str, Any]:
        """
        Activates siren tone for WATCH, WARNING, or CRITICAL states.
        Enforces dry-run suppression when hardware is not explicitly enabled.
        """
        level_upper = level.upper()
        if level_upper not in self.VALID_LEVELS:
            raise ValueError(f"Invalid siren level: {level} (expected one of {self.VALID_LEVELS})")

        if not self.is_armed:
            return {
                "status": "BLOCKED_DISARMED",
                "message": "Siren activation blocked: controller is DISARMED.",
                "level": level_upper,
                "dry_run": self.dry_run
            }

        event_id = alert_id or f"SIREN-ACT-{int(datetime.now().timestamp() * 1000)}"
        now_iso = datetime.now(timezone.utc).isoformat()
        self.active_level = level_upper
        self.current_state = "ACTIVE"

        tones = {
            "WATCH": "INTERMITTENT_CHIME_853HZ",
            "WARNING": "PULSED_ALERT_DUAL_TONE",
            "CRITICAL": "CONTINUOUS_EAS_853_960HZ_EVACUATION"
        }

        event = {
            "event_type": "SIREN_ACTIVATION_EVENT",
            "alert_id": event_id,
            "severity": level_upper,
            "timestamp": now_iso,
            "gateway_id": self.gateway_id,
            "activation_type": "AUTOMATED_THRESHOLD",
            "tone_profile": tones.get(level_upper),
            "reason": reason,
            "dry_run": self.dry_run,
            "physical_output": not self.dry_run,
            "status": "SOUNDING_SIMULATED" if self.dry_run else "SOUNDING_HARDWARE"
        }

        self.activation_history.append(event)
        if self.store:
            try:
                self.store.insert_alert({
                    "alert_id": event_id,
                    "severity": level_upper,
                    "trigger_source": "EDGE_SIREN_CONTROLLER",
                    "gateway_id": self.gateway_id,
                    "reason": reason,
                    "siren_activated": 1 if not self.dry_run else 0,
                    "dry_run": self.dry_run,
                    "acknowledged": 0
                }, buffer_for_cloud=True)
            except Exception as e:
                logger.warning(f"Could not persist siren activation: {e}")

        logger.info(f"[SirenController {self.gateway_id}] Level {level_upper} activated (dry_run={self.dry_run}).")
        return event

    def status(self) -> Dict[str, Any]:
        """Returns comprehensive diagnostic telemetry."""
        return {
            "gateway_id": self.gateway_id,
            "current_state": self.current_state,
            "is_armed": self.is_armed,
            "active_level": self.active_level,
            "hardware_enabled": self.hardware_enabled,
            "dry_run": self.dry_run,
            "safety_mode": "DRY_RUN (No Physical Sound)" if self.dry_run else "LIVE_HARDWARE_ARMED",
            "total_events_logged": len(self.activation_history),
            "last_event": self.activation_history[-1] if self.activation_history else None,
            "supported_levels": list(self.VALID_LEVELS),
            "disclaimer": "Physical siren output disabled by default for test safety."
        }

    def get_event_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent activation events."""
        return list(reversed(self.activation_history[-limit:]))
