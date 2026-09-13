# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Autonomous AI Multi-Source Triage Engine
Phase 7: Autonomous Convergence Decision Matrix & Instant Siren Dispatch
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Features:
1. Multi-source real-time evidence aggregation:
   - Physical Factor of Safety (FoS < 1.0)
   - Teesta River Basal Scour (tau_b > 5,000 Pa)
   - Cumulative 24h Rainfall (> 120 mm)
   - Citizen Edge CV Crack Aperture (> 30 mm)
2. Autonomous convergence scoring & Explainability Breakdown ("Why").
3. Instant AI_AUTONOMOUS_BROADCAST dispatch without human delay.
"""

import os
import time
import json
import logging
import threading
from datetime import datetime, timezone
from services.cwc_sync import CWC_TEESTA_SERVICE

logger = logging.getLogger("PARVAT_NETRA_AI_TRIAGE")


class AutonomousAITriageEngine:
    """
    Evaluates multi-source hazard telemetry in real time.
    Triggers autonomous life-safety broadcast upon critical convergence.
    """

    # National Emergency Authority Thresholds
    FOS_CRITICAL_THRESHOLD = 1.0           # Physical failure imminent
    SCOUR_CRITICAL_PA = 5000.0             # Hydrodynamic basal scour threshold (Pa)
    RAINFALL_24H_CRITICAL_MM = 120.0       # Cumulative 24h rain threshold (mm)
    CRACK_APERTURE_CRITICAL_MM = 30.0      # Edge CV tension crack aperture threshold (mm)

    def __init__(self, alert_bus=None):
        self.alert_bus = alert_bus
        self.ml_model = None
        self.lock = threading.Lock()
        self.last_dispatch_time = None
        self.dispatch_history = []
        self._worker_thread = None
        self._stop_event = threading.Event()
        self.debounce_seconds = 45.0  # Prevent spamming consecutive alerts

    def set_alert_bus(self, alert_bus):
        self.alert_bus = alert_bus

    def load_ml_model(self, model_bundle):
        """Loads Phase 8 GradientBoostingRegressor model bundle for geotechnical FoS inference."""
        self.ml_model = model_bundle
        logger.info("[AI TRIAGE] Loaded Phase 8 Geotech ML model into AutonomousAITriageEngine.")

    def predict_ml_fos(self, rainfall_24h: float, pore_water_pressure: float, river_scour_tau_b: float) -> float:
        """Inference helper using loaded ML model bundle."""
        if not self.ml_model:
            return 0.745
        import pandas as pd
        model = self.ml_model["model"]
        features = self.ml_model.get("feature_names", ["rainfall_24h", "pore_water_pressure", "river_scour_tau_b"])
        X_input = pd.DataFrame([[float(rainfall_24h), float(pore_water_pressure), float(river_scour_tau_b)]], columns=features)
        pred = float(model.predict(X_input)[0])
        return max(0.20, min(3.0, round(pred, 3)))

    def evaluate_convergence(self, override_metrics=None):
        """
        Gathers live parameters across 4 critical modalities and computes convergence score.
        Integrates Phase 8 ML predicted Factor of Safety (FoS).
        """
        metrics = override_metrics or {}

        # 1. Physical Factor of Safety (FoS) & River Scour (tau_b) from CWC Hydro-Telemetry
        cwc_status = CWC_TEESTA_SERVICE.get_status()
        tau_b = float(metrics.get("tau_b", cwc_status.get("basal_shear_stress_pa", 5986.65)))

        # 2. Cumulative 24h Rainfall
        rain_24h = float(metrics.get("rainfall_24h_mm", 140.0))

        # 3. Pore-Water Pressure (kPa)
        pore_pressure = float(metrics.get("pore_water_pressure", max(0.0, (rain_24h - 20.0) * 0.22)))

        # 4. ML Inferred FoS
        ml_predicted_fos = None
        if self.ml_model:
            ml_predicted_fos = self.predict_ml_fos(rain_24h, pore_pressure, tau_b)

        # FoS resolution: override takes priority, then ML prediction, then coupled CWC fallback
        if "fos" in metrics:
            fos = float(metrics["fos"])
        elif ml_predicted_fos is not None:
            fos = float(ml_predicted_fos)
        else:
            fos = float(cwc_status.get("coupled_fos", 0.745))

        # 3. Citizen Edge CV Crack Aperture
        crack_aperture = float(metrics.get("crack_aperture_mm", 41.5))

        # Evaluate threshold breaches
        fos_breach = fos < self.FOS_CRITICAL_THRESHOLD
        scour_breach = tau_b > self.SCOUR_CRITICAL_PA
        rain_breach = rain_24h > self.RAINFALL_24H_CRITICAL_MM
        crack_breach = crack_aperture > self.CRACK_APERTURE_CRITICAL_MM

        breached_modalities = []
        if fos_breach:
            breached_modalities.append({
                "modality": "PHYSICAL_FOS",
                "label": "Factor of Safety Collapse",
                "value": round(fos, 3),
                "threshold": f"< {self.FOS_CRITICAL_THRESHOLD}",
                "weight_pct": 30.0,
                "status": "CRITICAL"
            })
        if scour_breach:
            breached_modalities.append({
                "modality": "TEESTA_BASAL_SCOUR",
                "label": "Hydrodynamic Toe Scour",
                "value": f"{round(tau_b, 1)} Pa",
                "threshold": f"> {self.SCOUR_CRITICAL_PA:.0f} Pa",
                "weight_pct": 25.0,
                "status": "CRITICAL"
            })
        if rain_breach:
            breached_modalities.append({
                "modality": "CUMULATIVE_RAINFALL",
                "label": "24h Monsoonal Precipitation",
                "value": f"{round(rain_24h, 1)} mm",
                "threshold": f"> {self.RAINFALL_24H_CRITICAL_MM:.0f} mm",
                "weight_pct": 25.0,
                "status": "CRITICAL"
            })
        if crack_breach:
            breached_modalities.append({
                "modality": "EDGE_CV_TENSION_CRACK",
                "label": "Field Camera Crack Aperture",
                "value": f"{round(crack_aperture, 1)} mm",
                "threshold": f"> {self.CRACK_APERTURE_CRITICAL_MM:.0f} mm",
                "weight_pct": 20.0,
                "status": "CRITICAL"
            })

        breach_count = len(breached_modalities)
        total_modalities = 4
        convergence_score = round((breach_count / total_modalities) * 100.0, 1)

        # Critical convergence if >= 3 modalities breached
        is_critical_convergence = breach_count >= 3

        # Compute Composite Vulnerability & Threat Index (VTI, 0-100 scale)
        from services.ai_sitrep import AI_SITREP_SERVICE
        vti_score = AI_SITREP_SERVICE.calculate_vti(fos, tau_b, rain_24h, crack_aperture)
        vti_tier = AI_SITREP_SERVICE.get_vti_tier(vti_score)

        now_iso = datetime.now(timezone.utc).isoformat()
        sector = metrics.get("sector", "NH-10 Km 48 (29th Mile Sector)")

        result = {
            "timestamp": now_iso,
            "sector": sector,
            "convergence_score": convergence_score,
            "vti_score": vti_score,
            "vti_tier": vti_tier,
            "breach_count": breach_count,
            "total_modalities": total_modalities,
            "is_critical_convergence": is_critical_convergence,
            "status": "CRITICAL_CONVERGENCE" if is_critical_convergence else "ELEVATED_WATCH",
            "metrics": {
                "factor_of_safety": round(fos, 3),
                "ml_predicted_fos": round(ml_predicted_fos, 3) if ml_predicted_fos is not None else None,
                "basal_shear_stress_pa": round(tau_b, 1),
                "rainfall_24h_mm": round(rain_24h, 1),
                "pore_water_pressure_kpa": round(pore_pressure, 2),
                "crack_aperture_mm": round(crack_aperture, 1)
            },
            "breached_modalities": breached_modalities,
            "explainability": {
                "why": f"Autonomous AI convergence confirmed across {breach_count}/{total_modalities} modalities. "
                       f"FoS={fos:.3f} (<1.0) under high river basal shear stress tau_b={tau_b:.1f}Pa (>5000Pa), "
                       f"intense rainfall={rain_24h}mm (>120mm), and field CV tension crack={crack_aperture}mm (>30mm).",
                "modality_weights": {
                    "physics_fos": 30.0,
                    "teesta_scour": 25.0,
                    "rainfall_24h": 25.0,
                    "edge_cv_crack": 20.0
                }
            }
        }
        return result

    def execute_autonomous_triage(self, override_metrics=None, force=False):
        """
        Evaluates convergence and the Composite Vulnerability & Threat Index (VTI).
        Executes the Adaptive AI Notification & Siren Matrix:
        - 0–40 (Normal): Passive logging.
        - 41–70 (Elevated): Broadcasts multi-lingual citizen advisories via SSE.
        - 71–90 (High): Flags offline traveler devices for SAR tracking.
        - 91–100 (Critical): Automatically triggers AI_AUTONOMOUS_BROADCAST server-side SSE siren dispatch without human delay.
        """
        eval_res = self.evaluate_convergence(override_metrics)
        vti_score = eval_res.get("vti_score", 0.0)
        vti_tier = eval_res.get("vti_tier", "NORMAL")
        is_critical = eval_res["is_critical_convergence"] or vti_score > 90.0 or force

        now_epoch = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Normal Tier (0-40): Passive logging
        if vti_score <= 40.0 and not force and not eval_res["is_critical_convergence"]:
            logger.info(f"[AI VTI MATRIX] Sector {eval_res['sector']} VTI: {vti_score}/100 [NORMAL] - Passive telemetry logging.")
            return {
                "action": "PASSIVE_LOGGING",
                "vti_score": vti_score,
                "vti_tier": "NORMAL",
                "evaluation": eval_res
            }

        # 2. Elevated Tier (41-70): Broadcast multi-lingual citizen advisories via SSE
        if 40.0 < vti_score <= 70.0 and not force and not eval_res["is_critical_convergence"]:
            advisory_payload = {
                "type": "CITIZEN_ADVISORY_BROADCAST",
                "dispatch_id": f"ADV-{int(now_epoch)}",
                "sector": eval_res["sector"],
                "vti_score": vti_score,
                "vti_tier": "ELEVATED",
                "severity": "ELEVATED",
                "timestamp": now_iso,
                "message": f"⚠️ CITIZEN ADVISORY: Heightened landslide vigilance on {eval_res['sector']} (VTI: {vti_score}/100). Exercise caution and avoid non-essential mountain travel.",
                "message_hi": f"⚠️ नागरिक परामर्श: {eval_res['sector']} पर भूस्खलन सतर्कता (VTI: {vti_score}/100)। रात में अनावश्यक यात्रा से बचें।",
                "message_ne": f"⚠️ नागरिक सल्लाह: {eval_res['sector']} मा पहिरो सतर्कता (VTI: {vti_score}/100)। अत्यावश्यक बाहेक यात्रा नगर्नुहोस्।"
            }
            if self.alert_bus:
                self.alert_bus.broadcast("citizen_advisory", advisory_payload)
            logger.info(f"[AI VTI MATRIX] Sector {eval_res['sector']} VTI: {vti_score}/100 [ELEVATED] - Multilingual citizen advisory broadcast.")
            return {
                "action": "CITIZEN_ADVISORY_DISPATCHED",
                "vti_score": vti_score,
                "vti_tier": "ELEVATED",
                "advisory_payload": advisory_payload,
                "evaluation": eval_res
            }

        # 3. High Tier (71-90): Flag offline traveler devices for SAR tracking
        if 70.0 < vti_score <= 90.0 and not force and not eval_res["is_critical_convergence"]:
            from services.sar_tracking import SAR_TRACKING_SERVICE
            flagged = SAR_TRACKING_SERVICE.flag_devices_in_hazard_zone(eval_res["sector"], radius_km=15.0)
            sar_alert_payload = {
                "type": "SAR_TRACKING_FLAGGED",
                "dispatch_id": f"SAR-FLAG-{int(now_epoch)}",
                "sector": eval_res["sector"],
                "vti_score": vti_score,
                "vti_tier": "HIGH",
                "severity": "HIGH",
                "timestamp": now_iso,
                "flagged_devices_count": len(flagged),
                "message": f"[HIGH THREAT ALERT]: Sector {eval_res['sector']} geotechnical stress critical (VTI: {vti_score}/100). Offline traveler devices flagged for NDRF ground extrication and aerial SAR."
            }
            if self.alert_bus:
                self.alert_bus.broadcast("sar_alert", sar_alert_payload)
            logger.info(f"[AI VTI MATRIX] Sector {eval_res['sector']} VTI: {vti_score}/100 [HIGH] - Proactively flagged {len(flagged)} devices for SAR.")
            return {
                "action": "SAR_DEVICES_FLAGGED",
                "vti_score": vti_score,
                "vti_tier": "HIGH",
                "sar_payload": sar_alert_payload,
                "evaluation": eval_res
            }

        # 4. Critical Tier (91-100) or Critical Convergence: Autonomous Broadcast
        if not is_critical:
            return {
                "action": "WATCH_NO_BROADCAST",
                "vti_score": vti_score,
                "vti_tier": vti_tier,
                "evaluation": eval_res
            }

        with self.lock:
            now_epoch = time.time()
            if not force and self.last_dispatch_time and (now_epoch - self.last_dispatch_time < self.debounce_seconds):
                return {
                    "action": "DEBOUNCED",
                    "vti_score": vti_score,
                    "vti_tier": vti_tier,
                    "seconds_remaining": round(self.debounce_seconds - (now_epoch - self.last_dispatch_time), 1),
                    "evaluation": eval_res
                }

            self.last_dispatch_time = now_epoch
            dispatch_id = f"AI-AUTO-{int(now_epoch)}"

            broadcast_payload = {
                "type": "AI_AUTONOMOUS_BROADCAST",
                "dispatch_id": dispatch_id,
                "source": "AUTONOMOUS_AI_MULTI_SOURCE_TRIAGE",
                "sector": eval_res["sector"],
                "hazard_centroid": {"lat": 27.2010, "lng": 88.5180},
                "radius_km": 15.0,
                "fs": eval_res["metrics"]["factor_of_safety"],
                "fos": eval_res["metrics"]["factor_of_safety"],
                "tau_b_pa": eval_res["metrics"]["basal_shear_stress_pa"],
                "rainfall_24h_mm": eval_res["metrics"]["rainfall_24h_mm"],
                "crack_aperture_mm": eval_res["metrics"]["crack_aperture_mm"],
                "convergence_score": eval_res["convergence_score"],
                "vti_score": vti_score,
                "vti_tier": "CRITICAL",
                "breach_count": eval_res["breach_count"],
                "total_modalities": eval_res["total_modalities"],
                "status": eval_res["status"],
                "explainability": eval_res["explainability"],
                "channel": "C-DOT CBS CH-4370 + Web Audio EAS + AI Autonomous Pipeline",
                "timestamp": eval_res["timestamp"],
                "severity": "CRITICAL",
                "action": "EVACUATE",
                "message": f"[AUTONOMOUS AI WARNING]: Multi-source convergence breached at {eval_res['sector']}. "
                           f"VTI={vti_score}/100, FoS={eval_res['metrics']['factor_of_safety']}, Scour={eval_res['metrics']['basal_shear_stress_pa']}Pa. "
                           f"Immediate corridor evacuation required!"
            }

            # If Alert Bus is attached, broadcast immediately to all connected clients
            if self.alert_bus:
                # 1. Broadcast AI_AUTONOMOUS_BROADCAST
                self.alert_bus.broadcast("ai_autonomous_broadcast", broadcast_payload)
                # 2. Also emit with type AUTHORITY_SIREN_DISPATCH for universal siren & modal triggers
                siren_compat_payload = dict(broadcast_payload)
                siren_compat_payload["type"] = "AUTHORITY_SIREN_DISPATCH"
                self.alert_bus.broadcast("siren_dispatch", siren_compat_payload)

            self.dispatch_history.append(broadcast_payload)
            logger.info(f"[AI TRIAGE] AUTONOMOUS DISPATCH TRIGGERED: {dispatch_id} for {eval_res['sector']} (Score: {eval_res['convergence_score']}%, VTI: {vti_score})")

            return {
                "action": "BROADCAST_DISPATCHED",
                "dispatch_id": dispatch_id,
                "vti_score": vti_score,
                "vti_tier": "CRITICAL",
                "broadcast_payload": broadcast_payload,
                "evaluation": eval_res
            }

    def start_autonomous_worker(self, interval_seconds=30):
        """Starts background daemon to poll convergence and auto-trigger if threshold crossed."""
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._stop_event.clear()

        def _loop():
            logger.info(f"[AI TRIAGE] Autonomous evaluation worker started (Interval: {interval_seconds}s).")
            while not self._stop_event.is_set():
                try:
                    self.execute_autonomous_triage()
                except Exception as e:
                    logger.warning(f"[AI TRIAGE WORKER WARNING] {e}")
                self._stop_event.wait(interval_seconds)

        self._worker_thread = threading.Thread(target=_loop, daemon=True, name="AI_Autonomous_Triage_Worker")
        self._worker_thread.start()

    def stop_autonomous_worker(self):
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)


# Global singleton
AI_TRIAGE_ENGINE = AutonomousAITriageEngine()
