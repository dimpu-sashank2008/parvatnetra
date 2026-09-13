#!/usr/bin/env python3
"""
PARVAT NETRA -- Autonomous Background Scheduler Daemon (Phase 15)
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Features:
  1. Synchronizes in-situ geotechnical telemetry (VWC % & Inclinometer tilt) and node health.
  2. Re-evaluates 5-modality AI landslide risk with Teesta toe scour and hill-cut modifiers.
  3. Refreshes arterial highway clearance, bypass detours, and settlement isolation states.
  4. Emits regular ASCII-safe heartbeats for system health audits.
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime, timezone

# Reconfigure stdout/stderr to UTF-8 on Windows cp1252 safely
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PARVAT_NETRA_SCHEDULER")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.telemetry_streamer import GeotechnicalTelemetryStreamer
from backend.risk_engine import run_risk_fusion_pipeline
from backend.routing_engine import EmergencyRoutingEngine

_scheduler_thread = None
_stop_event = threading.Event()


def run_scheduler_cycle(max_retries=3):
    """
    Executes a complete single pass of the decision intelligence loop:
      Step 1: Ingest simulated/live geotechnical telemetry
      Step 2: Recalculate 5-modality risk scores + river scour + cut factors
      Step 3: Update emergency detour routes and settlement isolation matrix
    """
    start_time = time.time()
    results = {
        "status": "SUCCESS",
        "telemetry_readings": 0,
        "risk_evaluations": 0,
        "routes_evaluated": 0,
        "settlements_evaluated": 0,
        "primary_road_status": "UNKNOWN",
        "heartbeat": ""
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            # 1. Geotechnical Telemetry Streamer
            streamer = GeotechnicalTelemetryStreamer()
            readings = streamer.stream_cycle()
            results["telemetry_readings"] = len(readings) if readings else 0

            time.sleep(0.5)

            # 2. 5-Modality AI Risk Fusion Engine
            evals = run_risk_fusion_pipeline()
            results["risk_evaluations"] = len(evals) if evals else 0

            time.sleep(0.5)

            # 2b. Real-Time Multimodal CRI Dataset Harvester & Filer
            try:
                from services.realtime_cri_service import REALTIME_CRI_SERVICE
                rt_res = REALTIME_CRI_SERVICE.refresh_and_file_dataset()
                results["realtime_cri_records"] = rt_res.get("record_count", 0)
            except Exception as rt_err:
                logger.warning(f"Scheduler Realtime CRI update deferred: {rt_err}")

            # 3. Emergency Routing & Habitation Isolation Engine
            routing_engine = EmergencyRoutingEngine()
            cycle_res = routing_engine.run_routing_cycle()
            results["primary_road_status"] = cycle_res["primary_road"]["status"]
            results["routes_evaluated"] = len(cycle_res.get("bypass_routes", []))
            results["settlements_evaluated"] = len(cycle_res.get("habitations", []))

            elapsed = time.time() - start_time
            heartbeat = f"[HEARTBEAT] Telemetry synced ({results['telemetry_readings']} nodes) -> 5M Risk updated ({results['risk_evaluations']} sectors) -> RT CRI filed ({results.get('realtime_cri_records', 0)}) -> Evacuation routes refreshed (Primary: {results['primary_road_status']}, Elapsed: {elapsed:.2f}s)."
            results["heartbeat"] = heartbeat
            logger.info(heartbeat)
            return results

        except Exception as exc:
            last_error = exc
            logger.warning(f"Scheduler cycle attempt {attempt + 1}/{max_retries} encountered transient error: {exc}. Retrying...")
            time.sleep(1.5 * (attempt + 1))

    results["status"] = "ERROR"
    results["error"] = str(last_error)
    logger.error(f"Scheduler cycle failed after {max_retries} attempts: {last_error}", exc_info=True)
    return results


def _scheduler_loop(interval_seconds=60):
    """Internal daemon loop firing every interval_seconds until stopped."""
    logger.info(f"Autonomous background scheduler loop started (Interval: {interval_seconds}s).")
    # Initial sleep to allow webserver and connections to initialize cleanly
    _stop_event.wait(min(15, interval_seconds))
    while not _stop_event.is_set():
        run_scheduler_cycle()
        _stop_event.wait(interval_seconds)
    logger.info("Autonomous background scheduler loop stopped.")


def start_scheduler_daemon(interval_seconds=60):
    """Starts the background scheduler as a non-blocking daemon thread."""
    global _scheduler_thread
    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        logger.warning("Scheduler daemon thread is already running.")
        return _scheduler_thread

    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        args=(interval_seconds,),
        daemon=True,
        name="ParvatNetraScheduler"
    )
    _scheduler_thread.start()
    return _scheduler_thread


def stop_scheduler_daemon():
    """Signals the scheduler daemon to stop."""
    _stop_event.set()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PARVAT NETRA Background Scheduler")
    parser.add_argument("--once", action="store_true", help="Execute single cycle and exit")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds between cycles")
    args = parser.parse_args()

    print("=" * 80)
    print("PARVAT NETRA -- AUTONOMOUS BACKGROUND SCHEDULER DAEMON")
    print("Phase 15 (SIH Problem Statement ID: 26001)")
    print("=" * 80)

    if args.once:
        res = run_scheduler_cycle()
        print("\n" + res.get("heartbeat", "[HEARTBEAT] Cycle completed."))
        print(f"Status: {res['status']}")
    else:
        print(f"Starting continuous daemon loop every {args.interval} seconds... (Ctrl+C to stop)")
        try:
            while True:
                run_scheduler_cycle()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
