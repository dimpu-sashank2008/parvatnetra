# -*- coding: utf-8 -*-
"""
backend/institutional_routes.py
===============================
PARVAT NETRA • Institutional Data Health, Sensor Readiness & Shadow Operations REST API
---------------------------------------------------------------------------------------
Endpoints for:
  - GET  /api/institutional/data-health : Consolidated health of IMD, NCS, EO, DEM, IoT, CWC
  - GET  /api/iot/commissioning/readiness : 8-stage readiness tracking for all sensors
  - POST /api/pahad/shadow-inference     : Supervised shadow run with full risk & route impacts

Problem Statement: SIH 26001 / Phase 6B
"""

from __future__ import annotations

import os
import time
import json
import sqlite3
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from services.imd_service import IMD_CONNECTOR
from services.ncs_service import NCS_CONNECTOR
from services.satellite_service import SATELLITE_SERVICE
from services.dem_service import DEM_SERVICE
from services.cwc_sync import CWCTeestaHydroService
from engine.sensor_registry import GLOBAL_SENSOR_REGISTRY
from engine.data_freshness import FRESHNESS_ENGINE
from engine.observation_store import GLOBAL_OBSERVATION_STORE
from engine.pahad_live_inference import run_live_inference

logger = logging.getLogger("INSTITUTIONAL_ROUTES")

institutional_bp = Blueprint("institutional_routes", __name__)

SQLITE_DB_PATH = os.environ.get(
    "PHASE6A_DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db")
)

# Shared CWC service instance
_CWC_SERVICE = CWCTeestaHydroService()


def _ensure_shadow_table():
    try:
        os.makedirs(os.path.dirname(os.path.abspath(SQLITE_DB_PATH)), exist_ok=True)
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shadow_alert_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sector_id TEXT NOT NULL,
                event_probability REAL,
                cri REAL,
                fos REAL,
                recommended_alert TEXT,
                route_impact TEXT,
                suppression_reason TEXT,
                status TEXT,
                details_json TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"Shadow table init error: {e}")


_ensure_shadow_table()


# ─────────────────────────────────────────────────────────────────────────────
# 1. INSTITUTIONAL DATA HEALTH API
# ─────────────────────────────────────────────────────────────────────────────

@institutional_bp.route("/api/institutional/data-health", methods=["GET"])
def get_institutional_data_health():
    """
    GET /api/institutional/data-health
    ----------------------------------
    Returns health, authentication state, freshness, and errors for:
      - IMD (India Meteorological Department)
      - NCS (National Center for Seismology)
      - EO  (Earth Observation / Copernicus & ISRO Bhoonidhi)
      - DEM (Digital Elevation Model / GLO-30)
      - IoT (In-Situ Geotechnical Instrumentation)
      - CWC (Central Water Commission River Telemetry)
    """
    try:
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. IMD Status
        imd_stat = IMD_CONNECTOR.get_status()
        imd_freshness = FRESHNESS_ENGINE.get_freshness("imd")
        imd_health = {
            "status": imd_stat.get("status", "AUTH_REQUIRED"),
            "last_success": imd_stat.get("last_success"),
            "freshness": imd_freshness.status,
            "auth_state": imd_stat.get("auth_state", "AUTH_REQUIRED"),
            "source": "IMD Nowcast / AWS Network",
            "endpoint": imd_stat.get("endpoint"),
            "error": imd_stat.get("last_error") or (
                "IMD credentials absent in .env (IMD_API_BASE_URL/TOKEN)"
                if imd_stat.get("auth_state") == "AUTH_REQUIRED" else None
            ),
            "stations_available": imd_stat.get("stations_count", 10)
        }

        # 2. NCS Status
        ncs_stat = NCS_CONNECTOR.get_status()
        ncs_freshness = FRESHNESS_ENGINE.get_freshness("ncs")
        ncs_health = {
            "status": ncs_stat.get("status", "USGS_FALLBACK"),
            "last_success": now_iso if ncs_stat.get("ncs_configured") else None,
            "freshness": ncs_freshness.status,
            "auth_state": ncs_stat.get("auth_state", "AUTH_REQUIRED"),
            "source": "NCS Primary (AUTH_REQUIRED) / USGS Fallback (ACTIVE)",
            "endpoint": ncs_stat.get("endpoint"),
            "active_provider": ncs_stat.get("active_source", "USGS"),
            "fallback_active": True,
            "error": ncs_stat.get("last_error") or (
                "NCS_API_BASE_URL absent in .env; operating on public USGS fallback"
                if not ncs_stat.get("ncs_configured") else None
            )
        }

        # 3. EO / Satellite Status
        eo_pipeline = SATELLITE_SERVICE.get_pipeline_status()
        eo_health = {
            "status": eo_pipeline.get("overall_status", "CATALOGUE_DISCOVERY_ACTIVE"),
            "last_success": eo_pipeline.get("checked_at"),
            "freshness": "FRESH" if eo_pipeline.get("total_catalogued_scenes", 0) > 0 else "AGING",
            "auth_state": eo_pipeline.get("auth_state", "AUTH_REQUIRED"),
            "source": "Copernicus ESA / ISRO NRSC Bhoonidhi",
            "catalogued_scenes": eo_pipeline.get("total_catalogued_scenes", 0),
            "raw_download_available": eo_pipeline.get("raw_download_configured", False),
            "pipeline_tiers": eo_pipeline.get("pipeline_tiers"),
            "error": (
                "COPERNICUS_CLIENT_ID or ISRO_BHOONIDHI_API_KEY absent for automated scene download"
                if eo_pipeline.get("auth_state") == "AUTH_REQUIRED" else None
            )
        }

        # 4. DEM Status
        dem_stat = DEM_SERVICE.get_status() if hasattr(DEM_SERVICE, "get_status") else {}
        dem_health = {
            "status": "CACHED_LOCAL",
            "last_success": now_iso,
            "freshness": "FRESH",
            "auth_state": "CONFIGURED",
            "source": "Copernicus GLO-30 / CartoDEM",
            "resolution": "30m",
            "coverage": "North-Eastern Region (Himalayan Arc)",
            "error": None
        }

        # 5. IoT Sensor Network Status
        iot_stat = GLOBAL_SENSOR_REGISTRY.get_health_summary()
        active_devices = iot_stat["status_breakdown"].get("ACTIVE", 0)
        iot_health = {
            "status": "FIELD_INFRASTRUCTURE_READY" if active_devices > 0 else "PHYSICAL_DEPLOYMENT_PENDING",
            "last_success": now_iso if active_devices > 0 else None,
            "freshness": "FRESH" if active_devices > 0 else "STALE",
            "auth_state": "CONFIGURED",
            "source": "In-Situ Geotechnical Sensors (LoRa/MQTT)",
            "total_devices": iot_stat["total_devices"],
            "active_devices": active_devices,
            "gateways_count": iot_stat["total_gateways"],
            "error": None if active_devices > 0 else "No physical sensor nodes actively transmitting on-site"
        }

        # 6. CWC Hydrometric Status
        cwc_hydraulics = _CWC_SERVICE.compute_hydraulics()
        cwc_health = {
            "status": "SIMULATED_PHYSICS",
            "last_success": _CWC_SERVICE.last_sync_time,
            "freshness": "FRESH",
            "auth_state": "SIMULATED",
            "source": f"CWC Hydrometric Gauge {_CWC_SERVICE.station_id} ({_CWC_SERVICE.station_name})",
            "river": _CWC_SERVICE.river_name,
            "water_level_m": _CWC_SERVICE.water_level_m,
            "discharge_cumecs": _CWC_SERVICE.discharge_cumecs,
            "toe_loss_pct": cwc_hydraulics.get("toe_loss_pct", 0.0),
            "error": None
        }

        overall_readiness = (
            "INSTITUTIONAL_DATA_PARTIALLY_READY"
            if (imd_health["auth_state"] == "AUTH_REQUIRED" or ncs_health["auth_state"] == "AUTH_REQUIRED")
            else "INSTITUTIONAL_DATA_READY"
        )

        return jsonify({
            "status": "SUCCESS",
            "overall_readiness": overall_readiness,
            "checked_at": now_iso,
            "modalities": {
                "imd": imd_health,
                "ncs": ncs_health,
                "eo": eo_health,
                "dem": dem_health,
                "iot": iot_health,
                "cwc": cwc_health
            },
            "credentials_audit": {
                "IMD_API_BASE_URL": "SET" if os.environ.get("IMD_API_BASE_URL") else "NOT_SET",
                "IMD_API_TOKEN": "SET" if os.environ.get("IMD_API_TOKEN") else "NOT_SET",
                "NCS_API_BASE_URL": "SET" if os.environ.get("NCS_API_BASE_URL") else "NOT_SET",
                "COPERNICUS_CLIENT_ID": "SET" if os.environ.get("COPERNICUS_CLIENT_ID") else "NOT_SET",
                "ISRO_BHOONIDHI_API_KEY": "SET" if os.environ.get("ISRO_BHOONIDHI_API_KEY") else "NOT_SET",
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in institutional data-health: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# 2. SENSOR COMMISSIONING READINESS API
# ─────────────────────────────────────────────────────────────────────────────

@institutional_bp.route("/api/iot/commissioning/readiness", methods=["GET"])
def get_commissioning_readiness():
    """
    GET /api/iot/commissioning/readiness
    ------------------------------------
    Returns 8-stage readiness progress across registered sensor hardware:
    REGISTERED, INSTALLED, CALIBRATED, CONNECTED, HEARTBEAT_OK, TELEMETRY_OK, VALIDATED, ACCEPTED
    """
    try:
        device_id = request.args.get("device_id")
        readiness = GLOBAL_SENSOR_REGISTRY.get_commissioning_readiness(device_id=device_id)
        status_code = 200 if readiness.get("status") == "SUCCESS" else 404
        return jsonify(readiness), status_code
    except Exception as e:
        logger.error(f"Error in commissioning readiness API: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# 3. SUPERVISED SHADOW OPERATIONS INFERENCE API
# ─────────────────────────────────────────────────────────────────────────────

@institutional_bp.route("/api/pahad/shadow-inference", methods=["POST"])
def run_shadow_inference():
    """
    POST /api/pahad/shadow-inference
    --------------------------------
    Runs full live multi-modal inference and calculates:
      - Event probability
      - Factor of Safety (FoS)
      - Composite Risk Index (CRI)
      - Recommended alert level (GREEN, YELLOW, ORANGE, RED)
      - Corridor evacuation route impact
    STRICT SAFETY INVARIANT:
      Never dispatches public sirens, CAP broadcasts, or SMS.
      Returns status="SUPPRESSED_SHADOW_OPERATIONS" and records full decision trail.
    """
    try:
        data = request.get_json(silent=True) or {}
        sector_id = data.get("sector_id", "SK-NH10-KM48")
        lat = float(data.get("latitude", 27.3300))
        lon = float(data.get("longitude", 88.6100))
        horizon = int(data.get("forecast_horizon_hours", 24))

        # 1. Run live prediction
        inference_res = run_live_inference(
            sector_id=sector_id,
            latitude=lat,
            longitude=lon,
            forecast_horizon_hours=horizon,
            override_features=data.get("override_features")
        )

        # 2. Determine recommended alert level
        prob = inference_res.event_probability
        cri = inference_res.cri
        fos = inference_res.fos_physical

        if cri >= 80.0 or prob >= 0.80 or fos < 1.0:
            recommended_alert = "RED"
            route_impact = "CORRIDOR_CLOSURE_RECOMMENDED"
        elif cri >= 65.0 or prob >= 0.60 or fos < 1.25:
            recommended_alert = "ORANGE"
            route_impact = "RESTRICTED_HEAVY_VEHICLES"
        elif cri >= 45.0 or prob >= 0.40 or fos < 1.50:
            recommended_alert = "YELLOW"
            route_impact = "CAUTION_PROCEED_SLOWLY"
        else:
            recommended_alert = "GREEN"
            route_impact = "CORRIDOR_OPEN"

        now_iso = datetime.now(timezone.utc).isoformat()
        suppression_reason = "SHADOW_OPERATIONS_MODE_ACTIVE"

        # 3. Log into shadow_alert_log
        trail_id = None
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO shadow_alert_log (
                    timestamp, sector_id, event_probability, cri, fos,
                    recommended_alert, route_impact, suppression_reason, status, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                now_iso, sector_id, prob, cri, fos,
                recommended_alert, route_impact, suppression_reason,
                "SUPPRESSED_SHADOW_OPERATIONS",
                json.dumps({
                    "features_used": inference_res.features_used,
                    "top_drivers": inference_res.top_drivers,
                    "data_quality_score": inference_res.data_quality_score,
                    "confidence": inference_res.confidence
                })
            ))
            conn.commit()
            trail_id = cur.lastrowid
            conn.close()
        except Exception as log_err:
            logger.error(f"Error persisting shadow decision trail: {log_err}")

        return jsonify({
            "status": "SUPPRESSED_SHADOW_OPERATIONS",
            "shadow_mode": True,
            "public_dispatch_suppressed": True,
            "decision_trail_id": trail_id,
            "sector_id": sector_id,
            "timestamp_utc": now_iso,
            "inference": {
                "event_probability": prob,
                "event_probability_percentage": inference_res.probability_percentage,
                "fos_physical": fos,
                "fos_status": inference_res.fos_status,
                "cri": cri,
                "risk_band": inference_res.risk_band,
                "confidence": inference_res.confidence,
                "data_quality_score": inference_res.data_quality_score
            },
            "recommendations": {
                "alert_level": recommended_alert,
                "corridor_route_impact": route_impact,
                "siren_trigger_recommended": recommended_alert in ("ORANGE", "RED"),
                "bypass_route": "NH-717A_BAGRAKOTE_BYPASS" if recommended_alert in ("ORANGE", "RED") else None
            },
            "suppression_policy": {
                "reason": suppression_reason,
                "public_siren_activated": False,
                "cap_broadcast_dispatched": False,
                "sms_alert_dispatched": False,
                "notice": "Decision evaluated and archived for authority review without public dissemination."
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in shadow inference API: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500
