# -*- coding: utf-8 -*-
"""
tests/test_phase7h_routing_resilience.py
========================================
PHASE 7H — CP 7H-05: Tactical Routing Resilience, Road & Bridge Blockage Injection,
Hazard Penalties, Multi-Profile Optimization (FASTEST, SHORTEST, SAFEST), and Unreachable Detection.
"""

import pytest
from services.offline_routing_service import OfflineRoutingService


@pytest.fixture
def router():
    # Fresh router instance for isolated test state
    r = OfflineRoutingService()
    r.blocked_corridors_set.clear()
    r.blocked_bridges_set.clear()
    r.clear_hazard_zones()
    return r


def test_routing_profiles_fastest_shortest_safest(router):
    """CP 7H-05: System computes valid routes for FASTEST, SHORTEST, and SAFEST profiles."""
    origin_lat, origin_lon = 27.3300, 88.6100  # Gangtok / Pakyong
    dest_lat, dest_lon = 26.8500, 88.3900      # Siliguri Plains

    plan_fast = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon, routing_preference="FASTEST")
    assert plan_fast["status"] == "SUCCESS"
    assert plan_fast["routing_preference"] == "FASTEST"
    assert plan_fast["route_mode"] in ["PRIMARY_CORRIDOR", "STRATEGIC_BYPASS", "BYPASS_AVOIDANCE", "DIRECT_LOCAL"]

    plan_short = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon, routing_preference="SHORTEST")
    assert plan_short["status"] == "SUCCESS"
    assert plan_short["routing_preference"] == "SHORTEST"

    plan_safe = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon, routing_preference="SAFEST")
    assert plan_safe["status"] == "SUCCESS"
    assert plan_safe["routing_preference"] == "SAFEST"
    assert plan_safe["safety_score"] >= 0.50


def test_dynamic_corridor_blockage_diverts_to_bypass(router):
    """CP 7H-05: Severing NH-10 at Km 48 triggers automatic strategic detour to NH-717A."""
    origin_lat, origin_lon = 27.3300, 88.6100
    dest_lat, dest_lon = 26.8500, 88.3900

    # Inject blockage on NH-10
    router.block_corridor("SK-NH10", reason="Severe Mudflow at KM 48")
    assert "SK-NH10" in router.blocked_corridors_set

    plan = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon, avoid_blockages=True)
    assert plan["status"] == "SUCCESS"
    assert plan["active_blockages_detected"] >= 1
    assert "SK-NH10" in plan["blocked_corridors"]
    assert plan["bypass_recommendation"] is not None
    assert plan["bypass_recommendation"]["status"] == "PASSABLE"
    assert plan["route_mode"] in ["STRATEGIC_BYPASS", "BYPASS_AVOIDANCE"]


def test_dynamic_hazard_zone_penalty(router):
    """CP 7H-05: Injected active hazard zone penalizes transit time and degrades safety score."""
    origin_lat, origin_lon = 27.3300, 88.6100
    dest_lat, dest_lon = 26.8500, 88.3900

    # Base route without hazard zone
    plan_base = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon)
    base_time = plan_base["estimated_time_minutes"]

    # Inject hazard zone near origin/corridor
    router.add_landslide_hazard_zone("HZ-NH10-KM48", lat=27.3000, lon=88.6000, radius_km=15.0, risk_penalty=3.0)
    plan_haz = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon)

    assert plan_haz["estimated_time_minutes"] > base_time
    assert plan_haz["safety_score"] < plan_base["safety_score"]


def test_unreachable_destination_when_all_corridors_severed(router):
    """CP 7H-05: If all routes and bridges are blocked, router fails safely with UNREACHABLE status."""
    origin_lat, origin_lon = 27.3300, 88.6100
    dest_lat, dest_lon = 26.8500, 88.3900

    # Block both primary lifeline and critical bridge
    router.block_corridor("SK-NH10", reason="Active Landslide")
    router.block_bridge("CORR-BR-TEESTA-01", reason="Teesta Flash Flood / Bridge Pier Scour")

    plan = router.plan_offline_route(origin_lat, origin_lon, dest_lat, dest_lon, avoid_blockages=True)
    assert plan["status"] == "UNREACHABLE"
    assert plan["route_mode"] == "NO_PASSABLE_ROUTE"
    assert plan["bypass_recommendation"] is None
    assert plan["nearest_shelter"] is not None  # Guides to closest local high-ground shelter
