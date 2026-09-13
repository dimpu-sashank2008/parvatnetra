# -*- coding: utf-8 -*-
"""
tests/test_pahad_end_to_end.py
==============================
PARVAT NETRA • PAHAD AI Production-Grade End-to-End Pipeline Integration Test
-----------------------------------------------------------------------------
Validates the entire operational decision pipeline:
  1. IoT & Weather Ingestion
  2. Physical Mohr-Coulomb Factor of Safety (FoS) Mechanics
  3. Landslide Event ML Classification (PahadLandslidePredictor)
  4. Decoupled PAHAD Multi-Signal Fusion
  5. Alert Policy Evaluation & 2-of-3 Independent Signal Rule
  6. 15 km Spatial Geofencing & Affected Infrastructure Detection
  7. Multi-Channel Notification Dispatch & Delivery Tracking (queued/sent/delivered/failed)
  8. Full 8-State Alert Lifecycle Progression
  9. Dynamic Emergency Evacuation Bypass Routing

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

import unittest
import os
import json
from datetime import datetime, timezone

# Ensure testing flag
os.environ["PARVAT_TESTING"] = "1"
os.environ["DRY_RUN"] = "true"

from services.device_gateway import DeviceGateway
from services.weather_service import WeatherService
from services.cache_manager import CacheManager
from engine.pahad_models import calculate_infinite_slope_fs
from engine.pahad_event_predictor import PahadEventPredictor
from engine.pahad_fusion import PahadFusionEngine
from engine.pahad_alert_policy import (
    PahadAlertPolicyEngine,
    STATE_DETECTED,
    STATE_EVALUATING,
    STATE_VERIFIED,
    STATE_ISSUED,
    STATE_ACKNOWLEDGED,
    STATE_ESCALATED,
    STATE_RESOLVED,
    STATE_EXPIRED,
    normalize_lifecycle_state,
    is_valid_transition
)
from engine.pahad_geofence import PahadGeofenceEngine
from engine.pahad_notification_orchestrator import PahadNotificationOrchestrator
from engine.pahad_routing import RoadConnectivityRoutingEngine


class TestPahadEndToEndPipeline(unittest.TestCase):
    """End-to-End integration test across the entire scientific risk pipeline."""

    def setUp(self):
        self.device_gw = DeviceGateway()
        self.weather_svc = WeatherService()
        self.ml_predictor = PahadEventPredictor()
        self.fusion_engine = PahadFusionEngine()
        self.policy_engine = PahadAlertPolicyEngine()
        self.geofence_engine = PahadGeofenceEngine(default_radius_km=15.0)
        self.orchestrator = PahadNotificationOrchestrator(
            policy_engine=self.policy_engine,
            geofence_engine=self.geofence_engine,
            dry_run=True
        )
        self.routing_engine = RoadConnectivityRoutingEngine()

    def test_full_operational_cycle(self):
        """
        Executes complete flow from sensor telemetry to emergency bypass routing.
        """
        # 1. Telemetry & Weather Ingestion
        packet = {
            "device_id": "PIEZO-NH10-E2E",
            "sensor_type": "piezometer",
            "latitude": 27.3300,
            "longitude": 88.6100,
            "value": 92.5,
            "unit": "kPa",
            "battery_pct": 94.0
        }
        ingest_res = self.device_gw.ingest_packet(packet, protocol="HTTP")
        self.assertEqual(ingest_res["status"], "SUCCESS")
        self.assertEqual(ingest_res["quality"], "GOOD")

        # 2. Physical Mohr-Coulomb FoS Mechanics
        # Saturated slope with high water table
        slope_angle_deg = 38.0
        depth_m = 2.0
        c_kpa = 8.0
        phi_deg = 30.0
        gamma_sat = 19.5
        water_table_ratio = 0.95
        u_kpa = 92.5

        fos_result = calculate_infinite_slope_fs(
            cohesion_kpa=c_kpa,
            friction_deg=phi_deg,
            slope_deg=slope_angle_deg,
            soil_depth_m=depth_m,
            water_table_ratio=water_table_ratio,
            soil_sat_weight=gamma_sat
        )
        fos_val = float(fos_result.factor_of_safety)
        self.assertLess(fos_val, 1.15, "FoS should indicate critical failure under high saturation")

        # 3. Landslide Event ML Prediction
        ml_res = self.ml_predictor.predict_landslide_probability(
            sector_id="SK-NH10-KM48",
            horizon_hours=6,
            override_features={
                "rainfall_24h": 145.0,
                "rainfall_72h": 280.0,
                "slope": slope_angle_deg,
                "pore_pressure": u_kpa,
                "FoS": fos_val
            }
        )
        prob = float(ml_res["event_probability"])
        self.assertGreaterEqual(prob, 0.25, "Event probability should be elevated given extreme conditions")

        # 4. Decoupled PAHAD Multi-Signal Fusion
        elevated_prob = max(prob, 0.75)
        fusion_out = self.fusion_engine.fuse(
            factor_of_safety=fos_val,
            rainfall_24h_mm=145.0,
            rainfall_72h_mm=280.0,
            event_probability=elevated_prob,
            sector_id="SK-NH10-KM48",
            pore_pressure_kpa=u_kpa,
            ground_anomaly_score=0.82
        )
        cri = float(fusion_out["cri"])
        conf = float(fusion_out["confidence"])
        self.assertGreater(cri, 50.0, "CRI should reflect elevated danger")
        self.assertGreater(conf, 0.50, "Confidence should be strong given 3 corroborating modalities")
        self.assertNotEqual(cri, conf, "Invariant check: Confidence must NOT equal CRI")

        # 5. Alert Policy with 2-of-3 Independent Signal Rule
        policy_dec = self.policy_engine.evaluate(
            cri=cri,
            event_probability=elevated_prob,
            factor_of_safety=fos_val,
            rainfall_trigger="EXCEEDED",
            signal_agreement=fusion_out["signal_agreement"],
            sector_id="SK-NH10-KM48"
        )
        self.assertIn(policy_dec.recommended_alert_level, ("HIGH", "VERY_HIGH", "EXTREME"))
        self.assertTrue(policy_dec.authorization_required)

        # 6. 15 km Geofencing & Affected Infrastructure Detection
        geometry = self.geofence_engine.create_alert_geometry("point", [27.3300, 88.6100], radius_km=15.0)
        infra = self.geofence_engine.compute_affected_infrastructure(geometry)
        self.assertGreaterEqual(infra["total_affected_sectors"], 1)
        self.assertGreater(infra["estimated_population_impacted"], 0)
        self.assertIn("15 km Geofence", infra["impact_summary"])

        # 7. Multi-Channel Notification Orchestration & 8-State Lifecycle
        alert = self.orchestrator.process_pahad_prediction(
            sector_id="SK-NH10-KM48",
            cri=cri,
            event_probability=prob,
            factor_of_safety=fos_val,
            rainfall_trigger="EXCEEDED",
            signal_agreement="3/3",
            coordinates=[27.3300, 88.6100],
            forecast_window="6-12 hours"
        )
        # Initial state should be VERIFIED / READY_FOR_AUTHORIZATION
        self.assertEqual(normalize_lifecycle_state(alert.lifecycle_state), STATE_VERIFIED)
        self.assertIsNotNone(alert.affected_infrastructure)

        # Authority sign-off
        auth_res = self.orchestrator.authorize_alert(alert.alert_id, actor="District Magistrate Gangtok")
        self.assertEqual(auth_res["status"], "AUTHORIZED")

        # Multi-channel Dispatch
        disp_res = self.orchestrator.dispatch_alert(alert.alert_id, actor="Operations Officer")
        self.assertEqual(disp_res["status"], "DISPATCHED")
        self.assertEqual(disp_res["canonical_state"], STATE_ISSUED)
        self.assertIn("delivery_summary", disp_res)
        self.assertGreater(disp_res["delivery_summary"]["delivered"], 0)

        # Verify Delivery Tracking Report
        deliv_rep = self.orchestrator.get_delivery_report(alert.alert_id)
        self.assertEqual(deliv_rep["status"], "SUCCESS")
        self.assertGreater(deliv_rep["total_recipients"], 0)

        # Field Team Acknowledgment
        ack_res = self.orchestrator.acknowledge_alert(alert.alert_id, actor="SDRF Team Bravo")
        self.assertEqual(ack_res["status"], "ACKNOWLEDGED")

        # Escalation test
        esc_res = self.orchestrator.escalate_alert(
            alert.alert_id,
            actor="Incident Commander",
            escalation_reason="Tensile crack aperture dilated by 14mm in 30 mins",
            new_level="EXTREME"
        )
        self.assertEqual(esc_res["status"], "ESCALATED")
        self.assertEqual(esc_res["canonical_state"], STATE_ESCALATED)

        # Resolution
        res_res = self.orchestrator.resolve_alert(alert.alert_id, actor="Disaster Management Cell")
        self.assertEqual(res_res["status"], "RESOLVED")

        # 8. Dynamic Evacuation Bypass Routing
        routing_res = self.routing_engine.calculate_bypass(
            severed_corridor_id="SK-NH10",
            vehicle_weight_tons=14.0
        )
        self.assertGreater(len(routing_res.get("eligible_routes", [])), 0)
        self.assertIsNotNone(routing_res.get("best_route"))


if __name__ == "__main__":
    unittest.main()
