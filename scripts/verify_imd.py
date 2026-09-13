#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_imd.py
=====================
PARVAT NETRA • Institutional Data Commissioning Verification CLI: IMD
----------------------------------------------------------------------
Verifies IMD API endpoint configuration, authentication bearer tokens,
AWS/ARG station mapping, and connectivity without fabricating observations.

Exit codes:
  0 - IMD endpoint configured, authenticated, and reachable (LIVE)
  1 - IMD credentials absent or placeholder (AUTH_REQUIRED)
  2 - IMD endpoint unreachable or returned an unexpected server error (UNAVAILABLE)

Usage:
  python scripts/verify_imd.py [--verbose] [--station AWS-42299]
"""

import sys
import os
import argparse
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.imd_service import IMD_CONNECTOR, NER_IMD_STATIONS, get_station_for_coords


def main():
    parser = argparse.ArgumentParser(
        description="Verify IMD Institutional API Connectivity & Station Mapping (Phase 6B)"
    )
    parser.add_argument("--station", help="Specific IMD AWS/ARG station ID to test", default=None)
    parser.add_argument("--lat", type=float, default=27.33, help="Latitude for nowcast check (default: 27.33 Gangtok)")
    parser.add_argument("--lon", type=float, default=88.61, help="Longitude for nowcast check (default: 88.61 Gangtok)")
    parser.add_argument("--verbose", action="store_true", help="Print full JSON response")
    args = parser.parse_args()

    print("=" * 70)
    print("PARVAT NETRA / PAHAD AI — IMD INSTITUTIONAL CONNECTOR AUDIT")
    print("=" * 70)

    # 1. Run connection verification
    diag = IMD_CONNECTOR.verify_connection()
    status = diag.get("status")
    auth_state = diag.get("auth_state")
    endpoint = diag.get("endpoint") or "[NOT CONFIGURED]"
    latency = diag.get("latency_ms", 0.0)

    print(f"Provider          : India Meteorological Department (IMD / MoES)")
    print(f"Status            : {status}")
    print(f"Auth State        : {auth_state}")
    print(f"Endpoint URL      : {endpoint}")
    print(f"Latency           : {latency} ms")
    print(f"Stations Mapped   : {len(NER_IMD_STATIONS)} stations across NER Himalayan corridors")

    # 2. Station selection
    target_st_id = args.station
    if not target_st_id:
        target_st_id, st_info = get_station_for_coords(args.lat, args.lon)
        print(f"Nearest Station   : {target_st_id} ({st_info['name']}, {st_info['district']}, {st_info['state']})")
    elif target_st_id in NER_IMD_STATIONS:
        st_info = NER_IMD_STATIONS[target_st_id]
        print(f"Target Station    : {target_st_id} ({st_info['name']}, {st_info['district']}, {st_info['state']})")
    else:
        print(f"Target Station    : {target_st_id} [CUSTOM STATION ID]")

    # 3. Fetch test observation
    obs_list = IMD_CONNECTOR.fetch_observations(lat=args.lat, lon=args.lon, sector_id="COMMISSION-TEST")
    print(f"Observation Count : {len(obs_list)}")
    if obs_list:
        sample = obs_list[0]
        print(f"Sample Provenance : {sample.provenance}")
        print(f"Sample Quality    : {sample.quality}")
        print(f"Sample Value      : {sample.value} {sample.unit}")

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

    if status == "LIVE":
        print("[SUCCESS] IMD Connector is operational and authenticated.")
        sys.exit(0)
    elif status == "AUTH_REQUIRED":
        print("[NOTICE] IMD Connector requires official MoES credentials in .env.")
        sys.exit(1)
    else:
        print(f"[ERROR] IMD Connector encountered error: {diag.get('error')}")
        sys.exit(2)


if __name__ == "__main__":
    main()
