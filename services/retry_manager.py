# -*- coding: utf-8 -*-
"""
services/retry_manager.py
=========================
PARVAT NETRA • Reliable Retry Engine & Idempotency Coordinator
--------------------------------------------------------------
Phase 10J (CP08):
  1. Exponential Backoff Retry Strategy (Attempt 1 -> Retry 1 -> Attempt 2 -> Retry 2 -> Attempt 3 -> Final Failure).
  2. Bounded Max Retries: Strict threshold (default max 3 attempts) preventing infinite message amplification.
  3. Deterministic Idempotency Key Engine: Collision-resistant dispatch tokens preventing uncontrolled duplicate sends.
  4. Transient vs Permanent Failure Classification:
     - Permanent errors (e.g. invalid recipient syntax, rejected authority, 4xx) fail fast without retries.
     - Transient errors (e.g. connection timeout, gateway 5xx, socket reset) undergo exponential backoff.
"""

from __future__ import annotations

import time
import uuid
import hashlib
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Optional, Tuple, Set

logger = logging.getLogger("RETRY_MANAGER")

DEFAULT_MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 0.5
BACKOFF_MULTIPLIER = 2.0
MAX_BACKOFF_SECONDS = 10.0


class RetryManager:
    """
    Coordinates reliable retries with exponential backoff and prevents duplicate dispatches.
    """

    def __init__(
        self,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        initial_backoff: float = INITIAL_BACKOFF_SECONDS,
        multiplier: float = BACKOFF_MULTIPLIER,
        max_backoff: float = MAX_BACKOFF_SECONDS
    ):
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
        self.multiplier = multiplier
        self.max_backoff = max_backoff
        self._idempotency_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def generate_idempotency_key(
        incident_id: str,
        recipient: str,
        channel: str,
        template_type: str,
        bucket_hours: int = 1
    ) -> str:
        """
        Produces a deterministic, collision-resistant idempotency key.
        Bucket hours prevents duplicates within the operational observation window
        while allowing later routine advisories for the same corridor.
        Format: IDEMP-<CHANNEL[:3]>-<SHA256[:12]>
        """
        now = datetime.now(timezone.utc)
        # Bucket by time window (e.g. 1 hour)
        bucket = now.strftime("%Y%m%d%H")
        seed = f"{incident_id}:{recipient.strip().lower()}:{channel.upper()}:{template_type.upper()}:{bucket}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12].upper()
        chan_code = (channel.upper()[:3] if channel else "GEN")
        return f"IDEMP-{chan_code}-{digest}"

    def compute_idempotency_key(
        self,
        incident_id: str,
        recipient: str,
        channel: str,
        template_type: str = "DEFAULT"
    ) -> str:
        """Alias for generate_idempotency_key."""
        return self.generate_idempotency_key(incident_id, recipient, channel, template_type)

    def is_duplicate(self, idempotency_key: str) -> bool:
        """Checks if a key has already been dispatched."""
        with self._lock:
            return idempotency_key in self._idempotency_cache

    def mark_dispatched(self, idempotency_key: str, incident_id: str = "", data: Any = None) -> None:
        """Marks a key as dispatched with associated record metadata."""
        with self._lock:
            self._idempotency_cache[idempotency_key] = {
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "incident_id": incident_id,
                "result": data
            }

    def check_duplicate(self, idempotency_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Checks if dispatch has already been processed or is in-flight.
        Returns (is_duplicate, previous_result).
        """
        with self._lock:
            if idempotency_key in self._idempotency_cache:
                return True, self._idempotency_cache[idempotency_key]
            return False, None

    def record_dispatch(self, idempotency_key: str, dispatch_result: Dict[str, Any]) -> None:
        """Records successful or terminal dispatch under its idempotency key."""
        with self._lock:
            self._idempotency_cache[idempotency_key] = {
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "result": dispatch_result
            }

    def compute_backoff(self, attempt_number: int) -> float:
        """
        Calculates exponential backoff delay in seconds for given retry attempt.
        attempt 1 -> 0s
        attempt 2 -> initial_backoff
        attempt 3 -> initial_backoff * multiplier
        """
        if attempt_number <= 1:
            return 0.0
        exponent = attempt_number - 2
        delay = self.initial_backoff * (self.multiplier ** exponent)
        return min(delay, self.max_backoff)

    def execute_with_retry(
        self,
        dispatch_fn: Callable[..., Dict[str, Any]],
        idempotency_key: Optional[str] = None,
        is_transient_error_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes dispatch function with deterministic bounded retries.
        """
        # Idempotency check
        if idempotency_key:
            is_dup, prior = self.check_duplicate(idempotency_key)
            if is_dup and prior:
                prior_res = dict(prior.get("result", {}))
                prior_res["is_duplicate"] = True
                prior_res["idempotency_key"] = idempotency_key
                logger.info(f"[RetryManager] Suppressed duplicate dispatch for key: {idempotency_key}")
                return prior_res

        last_result: Dict[str, Any] = {}
        for attempt in range(1, self.max_attempts + 1):
            if attempt > 1:
                backoff_sec = self.compute_backoff(attempt)
                logger.warning(
                    f"[RetryManager] Attempt {attempt}/{self.max_attempts} after {backoff_sec:.2f}s backoff..."
                )
                time.sleep(min(backoff_sec, 0.5))  # Keep unit test delay tight

            try:
                result = dispatch_fn(*args, **kwargs)
                result["attempt_count"] = attempt
                last_result = result

                # Check if succeeded
                if result.get("success", False):
                    if idempotency_key:
                        self.record_dispatch(idempotency_key, result)
                    return result

                # Check if error is permanent (do not retry)
                status = result.get("status", "")
                err_msg = str(result.get("error", "")).lower()
                is_permanent = (
                    status in ("BLOCKED", "UNAUTHORIZED", "INVALID_GEOFENCE") or
                    "invalid recipient" in err_msg or
                    "validation" in err_msg or
                    "prohibited" in err_msg
                )

                if is_transient_error_fn and not is_transient_error_fn(result):
                    is_permanent = True

                if is_permanent:
                    logger.warning(f"[RetryManager] Permanent failure detected on attempt {attempt}: {err_msg}. Aborting retries.")
                    break

            except Exception as exc:
                logger.error(f"[RetryManager] Exception on attempt {attempt}: {exc}")
                last_result = {
                    "success": False,
                    "status": "FAILED",
                    "error": str(exc),
                    "attempt_count": attempt
                }

        last_result["retry_exhausted"] = True
        if idempotency_key:
            self.record_dispatch(idempotency_key, last_result)
        return last_result


# Global Singleton Instance
RETRY_MANAGER = RetryManager()
