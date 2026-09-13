# -*- coding: utf-8 -*-
"""
engine/observability.py
=======================
PARVAT NETRA • PAHAD AI — Observability, Telemetry & Heartbeat Monitoring
Provides operational metrics, health checks, Prometheus telemetry, and dead-man heartbeats.
"""

from __future__ import annotations

import os
import time
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("PAHAD_OBSERVABILITY")

class SystemObservabilityTracker:
    """
    Central operational observability collector for system health,
    Prometheus metrics, and edge gateway heartbeats.
    """
    _instance: Optional[SystemObservabilityTracker] = None
    _lock = threading.Lock()

    def __init__(self):
        self._start_time = time.time()
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = {
            "inference_requests_total": 0,
            "observations_ingested_total": 0,
            "alerts_evaluated_total": 0,
            "authority_reviews_total": 0,
            "failed_requests_total": 0
        }
        self._heartbeats: Dict[str, float] = {}
        self._latencies: List[float] = []

    @classmethod
    def get_instance(cls) -> SystemObservabilityTracker:
        with cls._lock:
            if cls._instance is None:
                cls._instance = SystemObservabilityTracker()
            return cls._instance

    def record_request(self, endpoint: str, latency_seconds: float, success: bool = True) -> None:
        with self._lock:
            self._counters["inference_requests_total"] += 1
            if not success:
                self._counters["failed_requests_total"] += 1
            self._latencies.append(latency_seconds)
            if len(self._latencies) > 1000:
                self._latencies.pop(0)

    def record_heartbeat(self, device_id: str) -> None:
        with self._lock:
            self._heartbeats[device_id] = time.time()

    def check_heartbeat(self, device_id: str, timeout_seconds: float = 300.0) -> Dict[str, Any]:
        with self._lock:
            last = self._heartbeats.get(device_id)
            if last is None:
                return {"device_id": device_id, "status": "UNKNOWN", "last_seen_seconds_ago": None}
            elapsed = time.time() - last
            is_alive = elapsed <= timeout_seconds
            return {
                "device_id": device_id,
                "status": "ALIVE" if is_alive else "DEAD_MAN_TRIGGERED",
                "last_seen_seconds_ago": round(elapsed, 2),
                "timeout_threshold_s": timeout_seconds
            }

    def get_system_health(self) -> Dict[str, Any]:
        with self._lock:
            uptime = time.time() - self._start_time
            avg_lat = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
            p95_lat = sorted(self._latencies)[int(0.95 * len(self._latencies))] if len(self._latencies) >= 20 else avg_lat

            components = {
                "core_api": "HEALTHY",
                "physics_engine": "HEALTHY",
                "decision_store": "HEALTHY",
                "observation_store": "HEALTHY",
                "external_connectors": "PARTIAL_CREDENTIALS_REQUIRED",
                "siren_subsystem": "DRY_RUN_ARMED"
            }

            return {
                "status": "OPERATIONAL",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": round(uptime, 2),
                "components": components,
                "counters": dict(self._counters),
                "latency_metrics": {
                    "avg_latency_s": round(avg_lat, 4),
                    "p95_latency_s": round(p95_lat, 4)
                },
                "active_device_heartbeats": len(self._heartbeats)
            }

    def export_prometheus_metrics(self) -> str:
        """Exports metrics in standard Prometheus text format."""
        with self._lock:
            uptime = time.time() - self._start_time
            lines = [
                "# HELP pahad_uptime_seconds Total runtime of PAHAD AI engine in seconds",
                "# TYPE pahad_uptime_seconds gauge",
                f"pahad_uptime_seconds {uptime:.2f}",
                "# HELP pahad_inference_requests_total Total number of inference requests processed",
                "# TYPE pahad_inference_requests_total counter",
                f"pahad_inference_requests_total {self._counters['inference_requests_total']}",
                "# HELP pahad_failed_requests_total Total number of failed requests",
                "# TYPE pahad_failed_requests_total counter",
                f"pahad_failed_requests_total {self._counters['failed_requests_total']}"
            ]
            return "\n".join(lines) + "\n"

OBSERVABILITY = SystemObservabilityTracker.get_instance()
