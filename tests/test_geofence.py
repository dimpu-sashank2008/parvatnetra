"""
Test Suite: PAHAD AI Spatial Geofencing & 15 km Alert Zones (Phase 3.5)
Validates Haversine geodesic distance calculation, multi-geometry construction
(Point 15km, Road Corridor, Polygon Catchment), and recipient eligibility filtering.
"""
import os
import unittest

os.environ["PARVAT_TESTING"] = "1"

from engine.pahad_geofence import (
    PahadGeofenceEngine,
    haversine_distance_km,
    GeofenceEligibilityResult,
    DEFAULT_RADIUS_KM,
)


class TestPahadGeofence(unittest.TestCase):
    """Tests spatial geofence algorithms and privacy-preserving filtering."""

    def setUp(self):
        self.engine = PahadGeofenceEngine(default_radius_km=15.0)

    def test_haversine_distance_accuracy(self):
        """Test great-circle distance between known points in Sikkim (Gangtok to Rangpo ~19 km)."""
        gangtok = (27.3314, 88.6138)
        rangpo = (27.1767, 88.5322)
        dist = haversine_distance_km(gangtok[0], gangtok[1], rangpo[0], rangpo[1])
        self.assertAlmostEqual(dist, 19.2, delta=1.5)

        # Zero distance
        self.assertEqual(haversine_distance_km(27.0, 88.0, 27.0, 88.0), 0.0)

    def test_create_alert_geometry_point(self):
        """Verify Point geometry creation with default and custom radius."""
        geom = self.engine.create_alert_geometry("point", [27.200, 88.550], radius_km=15.0)
        self.assertEqual(geom["type"], "point")
        self.assertEqual(geom["center"], [27.200, 88.550])
        self.assertEqual(geom["radius_km"], 15.0)
        self.assertIn("15.0 km", geom["description"])

    def test_create_alert_geometry_corridor(self):
        """Verify road corridor buffer geometry."""
        waypoints = [[27.180, 88.530], [27.200, 88.550], [27.230, 88.580]]
        geom = self.engine.create_alert_geometry("corridor", waypoints, radius_km=10.0)
        self.assertEqual(geom["type"], "corridor")
        self.assertEqual(len(geom["waypoints"]), 3)
        self.assertEqual(geom["buffer_km"], 10.0)

    def test_create_alert_geometry_polygon(self):
        """Verify polygon catchment geometry."""
        ring = [[27.18, 88.53], [27.25, 88.53], [27.25, 88.60], [27.18, 88.60], [27.18, 88.53]]
        geom = self.engine.create_alert_geometry("polygon", ring, radius_km=5.0)
        self.assertEqual(geom["type"], "polygon")
        self.assertEqual(len(geom["vertices"]), 5)
        self.assertEqual(geom["buffer_km"], 5.0)

    def test_point_geofence_recipient_eligibility(self):
        """Recipients within 3 km -> IMPACT_DIRECT, 3-15 km -> BUFFER_ZONE, > 15 km -> OUTSIDE."""
        geom = self.engine.create_alert_geometry("point", [27.200, 88.550], radius_km=15.0)

        # 1. Close recipient (~1.5 km)
        res_direct = self.engine.is_recipient_in_alert_zone(27.210, 88.555, geom)
        self.assertTrue(res_direct.eligible)
        self.assertEqual(res_direct.zone_type, "IMPACT_DIRECT")
        self.assertLessEqual(res_direct.distance_km, 3.0)

        # 2. Intermediate recipient (~8 km away, inside 15 km radius)
        res_buffer = self.engine.is_recipient_in_alert_zone(27.260, 88.580, geom)
        self.assertTrue(res_buffer.eligible)
        self.assertEqual(res_buffer.zone_type, "BUFFER_ZONE")
        self.assertLessEqual(res_buffer.distance_km, 15.0)

        # 3. Far recipient (~35 km away, outside 15 km radius)
        res_outside = self.engine.is_recipient_in_alert_zone(27.500, 88.700, geom)
        self.assertFalse(res_outside.eligible)
        self.assertEqual(res_outside.zone_type, "OUTSIDE")
        self.assertGreater(res_outside.distance_km, 15.0)

    def test_corridor_recipient_eligibility(self):
        """Recipient close to a corridor segment is eligible."""
        waypoints = [[27.180, 88.530], [27.200, 88.550], [27.230, 88.580]]
        geom = self.engine.create_alert_geometry("corridor", waypoints, radius_km=5.0)

        # Close to second waypoint (~1 km away)
        res = self.engine.is_recipient_in_alert_zone(27.205, 88.552, geom)
        self.assertTrue(res.eligible)
        self.assertEqual(res.zone_type, "IMPACT_DIRECT")

        # Far away (~40 km)
        res_far = self.engine.is_recipient_in_alert_zone(27.500, 88.800, geom)
        self.assertFalse(res_far.eligible)
        self.assertEqual(res_far.zone_type, "OUTSIDE")

    def test_polygon_recipient_eligibility(self):
        """Polygon containment and buffer tests."""
        # Box between lat [27.20, 27.25] and lon [88.50, 88.55]
        ring = [[27.20, 88.50], [27.25, 88.50], [27.25, 88.55], [27.20, 88.55], [27.20, 88.50]]
        geom = self.engine.create_alert_geometry("polygon", ring, radius_km=5.0)

        # Center of the polygon
        res_inside = self.engine.is_recipient_in_alert_zone(27.225, 88.525, geom)
        self.assertTrue(res_inside.eligible)
        self.assertEqual(res_inside.zone_type, "IMPACT_DIRECT")

        # 3 km outside box
        res_buffer = self.engine.is_recipient_in_alert_zone(27.270, 88.525, geom)
        self.assertTrue(res_buffer.eligible)
        self.assertEqual(res_buffer.zone_type, "BUFFER_ZONE")

    def test_filter_eligible_recipients(self):
        """Test batch filtering of candidate recipients sorted by distance."""
        geom = self.engine.create_alert_geometry("point", [27.200, 88.550], radius_km=15.0)
        candidates = [
            {"id": "USER_FAR", "lat": 26.800, "lon": 88.400, "role": "citizen"},
            {"id": "USER_NEAR", "lat": 27.210, "lon": 88.555, "role": "sdrf_responder"},
            {"id": "USER_MID", "lat": 27.250, "lon": 88.570, "role": "citizen"},
        ]
        eligible = self.engine.filter_eligible_recipients(candidates, geom, alert_id="ALT-001")
        self.assertEqual(len(eligible), 2)
        # Should be ordered nearest first
        self.assertEqual(eligible[0]["id"], "USER_NEAR")
        self.assertEqual(eligible[1]["id"], "USER_MID")
        self.assertIn("distance_km", eligible[0])
        self.assertIn("zone_type", eligible[0])


if __name__ == "__main__":
    unittest.main()
