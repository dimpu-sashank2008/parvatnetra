import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
from engine.pahad_alert_gateway import (
    PahadAlertOrchestrator,
    SirenGateway,
    MeshAlertNode,
    haversine_distance_km,
)


class TestAlertGeofence(unittest.TestCase):
    """Tests geofenced emergency notification orchestration, siren synthesis, and dry-run safety."""

    def setUp(self):
        self.orchestrator = PahadAlertOrchestrator(dry_run=True, default_radius_km=15.0)

    def test_haversine_geodesic_distance(self):
        """Verify haversine formula against known coordinates (Gangtok to Rangpo ~30 km)."""
        gangtok_lat, gangtok_lon = 27.3314, 88.6138
        rangpo_lat, rangpo_lon = 27.1767, 88.5322
        dist = haversine_distance_km(gangtok_lat, gangtok_lon, rangpo_lat, rangpo_lon)
        self.assertAlmostEqual(dist, 19.0, delta=4.0)

    def test_geofence_filtering_inside_and_outside(self):
        """Verify nodes inside radius are targeted and nodes outside are excluded."""
        # Epicenter: NH-10 Km 48 (27.200, 88.550)
        center_lat, center_lon = 27.200, 88.550

        # Close node (~4 km away)
        node_close = {"id": "N1", "lat": 27.220, "lon": 88.560, "name": "Rangpo Village"}
        # Far node (~65 km away in Siliguri)
        node_far = {"id": "N2", "lat": 26.720, "lon": 88.430, "name": "Siliguri Staging"}

        nodes = self.orchestrator.filter_geofence_recipients(
            epicenter_lat=center_lat,
            epicenter_lon=center_lon,
            candidate_recipients=[node_close, node_far],
            radius_km=15.0,
        )

        node_ids = [n["id"] for n in nodes]
        self.assertIn("N1", node_ids)
        self.assertNotIn("N2", node_ids)

    def test_dry_run_safety_guarantee(self):
        """Ensure dry-run mode returns success without calling real telecommunication backends."""
        alert = self.orchestrator.dispatch_geofenced_alert(
            sector_id="S14",
            epicenter_lat=27.200,
            epicenter_lon=88.550,
            risk_band="EXTREME",
            message_en="EXTREME Landslide Danger: Evacuate lower slopes immediately.",
            radius_km=15.0,
        )

        self.assertTrue(alert.get("dry_run"))
        self.assertEqual(alert.get("status"), "SIMULATED_DISPATCH")
        self.assertIn("channels", alert)

        # Check all channels dispatched safely
        channels = alert["channels"]
        self.assertIn("push", channels)
        self.assertIn("siren_gateway", channels)
        self.assertIn("mesh_nodes", channels)
        self.assertIn("cap_xml", alert)

    def test_siren_gateway_tone_generation(self):
        """Verify SirenGateway generates dual EAS acoustic tones (853 Hz / 960 Hz)."""
        siren = SirenGateway(dry_run=True)
        resp = siren.sound_siren("SIREN_RANGPO_01", duration_sec=10)
        self.assertEqual(resp.get("status"), "SOUNDING_SIMULATED")
        self.assertEqual(resp.get("primary_frequency_hz"), 853)
        self.assertEqual(resp.get("secondary_frequency_hz"), 960)

    def test_mesh_alert_packet_structure(self):
        """Verify LoRa 865 MHz mesh packet format conforms to payload size limits."""
        mesh = MeshAlertNode(node_id="LORA_GATEWAY_S14", frequency_mhz=865.0, dry_run=True)
        pkt = mesh.broadcast_mesh_alert(alert_code="RED_EVAC_NOW", sector_id="S14", ttl_hops=4)
        self.assertEqual(pkt.get("status"), "BROADCAST_SIMULATED")
        self.assertLessEqual(pkt.get("payload_bytes"), 64, "LoRa emergency packet exceeds 64-byte payload limit")


if __name__ == "__main__":
    unittest.main()
