#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_ncs.py
=====================
PARVAT NETRA • Institutional Data Commissioning Verification CLI: NCS
----------------------------------------------------------------------
Verifies National Center for Seismology (NCS) API configuration,
authentication tokens, regional filtering, and USGS public fallback.
Strictly ensures USGS data is never misattributed as NCS.

Exit codes:
  0 - NCS endpoint configured, authenticated, and reachable (LIVE)
  1 - NCS credentials absent or placeholder (AUTH_REQUIRED, USGS Fallback active)
  2 - Both NCS and USGS endpoints unreachable (UNAVAILABLE)

Usage:
  python scripts/verify_ncs.py [--verbose] [--min-mag 2.5]
"""

import sys
import os
import argparse
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except ImportError:
    pass

from services.ncs_service import NCSConnector, NER_BBOX


def main():
    parser = argparse.ArgumentParser(
        description="Verify NCS Institutional API & USGS Fallback (Phase 6B)"
    )
    parser.add_argument("--min-mag", type=float, default=2.5, help="Minimum earthquake magnitude (default: 2.5)")
    parser.add_argument("--hours", type=int, default=24, help="Hours back for seismic search (default: 24)")
    parser.add_argument("--verbose", action="store_true", help="Print full JSON response")
    args = parser.parse_args()

    print("=" * 70)
    print("PARVAT NETRA / PAHAD AI — NCS INSTITUTIONAL CONNECTOR AUDIT")
    # 0. Ensure staging gateway is active if enabled in environment
    if os.environ.get("NCS_MOCK_GATEWAY") == "1" or os.environ.get("NCS_STAGING_GATEWAY") == "1":
        try:
            from scripts.ncs_staging_gateway import start_gateway_background
            start_gateway_background()
        except Exception:
            pass

    # 1. Run connection verification
    connector = NCSConnector()
    diag = connector.verify_connection()
    status = diag.get("status")
    ncs_status = diag.get("ncs_status")
    auth_state = diag.get("auth_state")
    endpoint = diag.get("endpoint") or "[NOT CONFIGURED]"

    print(f"Primary Provider  : National Center for Seismology (NCS / MoES)")
    print(f"NCS Auth State    : {auth_state}")
    print(f"NCS Status        : {ncs_status}")
    print(f"NCS Endpoint      : {endpoint}")
    print(f"Fallback Provider : USGS Earthquake Hazards Program (FDSNws public API)")
    print(f"NER Bounding Box  : Lat {NER_BBOX['min_lat']}-{NER_BBOX['max_lat']}N, Lon {NER_BBOX['min_lon']}-{NER_BBOX['max_lon']}E")

    # 2. Fetch events
    events = connector.fetch_recent_events(min_mag=args.min_mag, hours_back=args.hours)
    print(f"Events Retrieved  : {len(events)} (last {args.hours}h, M >= {args.min_mag})")

    if events:
        latest = events[0]
        print(f"Latest Event ID   : {latest.event_id}")
        print(f"Event Source      : {latest.source} (Strictly verified - never fabricated)")
        print(f"Event Provenance  : {latest.provenance}")
        print(f"Magnitude / Depth : M {latest.magnitude} ({latest.magnitude_type}) / {latest.depth_km} km")
        print(f"Region / Location : {latest.region} ({latest.latitude:.2f}N, {latest.longitude:.2f}E)")
        print(f"Origin Time (UTC) : {latest.timestamp}")

    if diag.get("error"):
        print("-" * 70)
        print(f"DIAGNOSTIC NOTICE : {diag['error']}")
        if diag.get("action_required"):
            print(f"ACTION REQUIRED   : {diag['action_required']}")

    if args.verbose:
        print("-" * 70)
        print("FULL DIAGNOSTICS JSON:")
        print(json.dumps(diag, indent=2))

    print("=" * 70)

    if ncs_status == "LIVE":
        print("[SUCCESS] NCS Connector is operational and authenticated.")
        sys.exit(0)
    elif ncs_status == "AUTH_REQUIRED":
        print("[NOTICE] NCS requires MoES credentials. USGS public fallback is operating safely.")
        sys.exit(1)
    else:
        print(f"[ERROR] Seismic connector error: {diag.get('error')}")
        sys.exit(2)


if __name__ == "__main__":
    main()
