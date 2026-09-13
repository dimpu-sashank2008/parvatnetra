# -*- coding: utf-8 -*-
"""
backend/iot_routes.py
=====================
PARVAT NETRA • In-Situ Geotechnical IoT & Edge Gateway REST API
---------------------------------------------------------------
Endpoints for:
  - Device registry and live status
  - Concentrator gateway management
  - Telemetry ingress with canonical validation
  - Field commissioning workflow (8-stage state machine)
  - Transducer calibration certificate uploads
  - Autonomous edge corridor alert policy test
  - Acoustic siren status and control

Problem Statement: SIH 26001 / Phase 6A
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from dataclasses import asdict
from flask import Blueprint, request, jsonify

from engine.sensor_registry import (
    GLOBAL_SENSOR_REGISTRY,
    SensorDevice,
    GatewayInfo,
    STATUS_REGISTERED,
    COMMISSIONING_STAGES
)
from engine.sensor_calibration import (
    GLOBAL_CALIBRATION_ENGINE,
    CalibrationRecord
)
from services.telemetry_contract import (
    GLOBAL_TELEMETRY_VALIDATOR,
    TelemetryPacket
)
from services.edge_gateway import (
    GLOBAL_EDGE_GATEWAY_SERVICE
)
from engine.edge_alert_policy import (
    GLOBAL_EDGE_ALERT_POLICY
)
from services.siren_controller import (
    GLOBAL_SIREN_CONTROLLER
)
from engine.observation_store import (
    GLOBAL_OBSERVATION_STORE
)

logger = logging.getLogger("IOT_ROUTES")

iot_bp = Blueprint("iot_routes", __name__)


# ─────────────────────────────────────────────────────────────────────────────
# DEVICE REGISTRY & SENSORS
# ─────────────────────────────────────────────────────────────────────────────

@iot_bp.route("/api/iot/devices", methods=["GET"])
def list_devices():
    """
    GET /api/iot/devices
    --------------------
    Returns registered sensor instrumentation with live operational states.
    Filters: ?sector_id=...&sensor_type=...&status=...
    """
    try:
        sector_id = request.args.get("sector_id")
        sensor_type = request.args.get("sensor_type")
        status = request.args.get("status")

        devices = GLOBAL_SENSOR_REGISTRY.list_devices(
            sector_id=sector_id,
            sensor_type=sensor_type,
            status=status
        )

        return jsonify({
            "status": "SUCCESS",
            "total_count": len(devices),
            "filters": {
                "sector_id": sector_id,
                "sensor_type": sensor_type,
                "status": status
            },
            "devices": [d.to_dict() for d in devices]
        }), 200
    except Exception as e:
        logger.error(f"Error listing IoT devices: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/iot/devices/<device_id>", methods=["GET"])
def get_device_detail(device_id: str):
    """
    GET /api/iot/devices/<device_id>
    --------------------------------
    Returns detailed configuration, calibration status, and latest telemetry for a sensor.
    """
    try:
        dev = GLOBAL_SENSOR_REGISTRY.get_device(device_id)
        if not dev:
            return jsonify({"status": "NOT_FOUND", "message": f"Device '{device_id}' not registered."}), 404

        # Query calibration
        cal = GLOBAL_CALIBRATION_ENGINE.get_calibration(dev.sensor_id)
        cal_dict = cal.to_dict() if cal else {"status": "UNKNOWN", "message": "No calibration record"}

        # Query latest observations
        latest_obs = GLOBAL_OBSERVATION_STORE.get_latest(
            sector_id=dev.sector_id, feature=dev.sensor_type, limit=5
        )

        return jsonify({
            "status": "SUCCESS",
            "device": dev.to_dict(),
            "calibration": cal_dict,
            "recent_observations": [
                {
                    "timestamp": obs.timestamp,
                    "value": obs.value,
                    "unit": obs.unit,
                    "quality": obs.quality,
                    "provenance": obs.provenance
                }
                for obs in latest_obs
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving device {device_id}: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# EDGE GATEWAYS & CONCENTRATORS
# ─────────────────────────────────────────────────────────────────────────────

@iot_bp.route("/api/iot/gateways", methods=["GET"])
def list_gateways():
    """
    GET /api/iot/gateways
    ---------------------
    Returns registered field edge concentrators and backhaul connectivity status.
    Filter: ?sector_id=...
    """
    try:
        sector_id = request.args.get("sector_id")
        gateways = GLOBAL_SENSOR_REGISTRY.list_gateways(sector_id=sector_id)
        edge_status = GLOBAL_EDGE_GATEWAY_SERVICE.get_status()

        return jsonify({
            "status": "SUCCESS",
            "total_gateways": len(gateways),
            "edge_concentrator_service": edge_status,
            "gateways": [asdict(gw) for gw in gateways]
        }), 200
    except Exception as e:
        logger.error(f"Error listing gateways: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/iot/gateways/<gateway_id>", methods=["GET"])
def get_gateway_detail(gateway_id: str):
    """
    GET /api/iot/gateways/<gateway_id>
    ----------------------------------
    Returns details for a specific edge concentrator.
    """
    try:
        gw = GLOBAL_SENSOR_REGISTRY.get_gateway(gateway_id)
        if not gw:
            # If requesting the active edge service gateway
            if gateway_id == GLOBAL_EDGE_GATEWAY_SERVICE.gateway_id:
                return jsonify({"status": "SUCCESS", "gateway": GLOBAL_EDGE_GATEWAY_SERVICE.get_status()}), 200
            return jsonify({"status": "NOT_FOUND", "message": f"Gateway '{gateway_id}' not found."}), 404

        return jsonify({"status": "SUCCESS", "gateway": asdict(gw)}), 200
    except Exception as e:
        logger.error(f"Error retrieving gateway {gateway_id}: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# NETWORK HEALTH & METRICS
# ─────────────────────────────────────────────────────────────────────────────

@iot_bp.route("/api/iot/health", methods=["GET"])
def iot_health_summary():
    """
    GET /api/iot/health
    -------------------
    Provides aggregate telemetry health, staleness detection, battery warnings,
    and weak signal monitoring.
    """
    try:
        summary = GLOBAL_SENSOR_REGISTRY.get_health_summary()
        summary["timestamp"] = datetime.now(timezone.utc).isoformat()
        return jsonify({"status": "SUCCESS", "health": summary}), 200
    except Exception as e:
        logger.error(f"Error fetching IoT health: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/iot/metrics", methods=["GET"])
def iot_metrics():
    """
    GET /api/iot/metrics
    --------------------
    Returns packet rates, drop rates, error rejection breakdowns, and ingest latency.
    """
    try:
        metrics = GLOBAL_TELEMETRY_VALIDATOR.get_metrics()
        edge_metrics = {
            "buffered_packets": GLOBAL_EDGE_GATEWAY_SERVICE.buffer.count_buffered(),
            "cloud_connected": GLOBAL_EDGE_GATEWAY_SERVICE.is_cloud_connected
        }
        return jsonify({
            "status": "SUCCESS",
            "telemetry_metrics": metrics,
            "edge_concentrator": edge_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching IoT metrics: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# TELEMETRY INGRESS & HISTORICAL QUERY
# ─────────────────────────────────────────────────────────────────────────────

@iot_bp.route("/api/iot/telemetry", methods=["GET"])
def query_telemetry():
    """
    GET /api/iot/telemetry
    ----------------------
    Query observations from persistent store.
    Parameters: ?sector_id=...&sensor_type=...&limit=50
    """
    try:
        sector_id = request.args.get("sector_id", "SK-NH10-KM48")
        sensor_type = request.args.get("sensor_type", "piezometer")
        limit = int(request.args.get("limit", 50))

        records = GLOBAL_OBSERVATION_STORE.get_latest(
            sector_id=sector_id, feature=sensor_type, limit=limit
        )

        return jsonify({
            "status": "SUCCESS",
            "sector_id": sector_id,
            "sensor_type": sensor_type,
            "count": len(records),
            "observations": [
                {
                    "timestamp": r.timestamp,
                    "feature": r.feature,
                    "value": r.value,
                    "unit": r.unit,
                    "quality": r.quality,
                    "provenance": r.provenance,
                    "source": r.source,
                    "ingested_at": r.ingested_at
                }
                for r in records
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error querying telemetry: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/iot/telemetry", methods=["POST"])
def ingest_telemetry():
    """
    POST /api/iot/telemetry
    -----------------------
    High-assurance telemetry ingress endpoint.
    Accepts raw JSON payload from LoRaWAN gateway, cellular RTU, or HTTP edge node.
    Validates canonical contract, applies calibration, checks bounds, and persists.
    """
    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({
                "status": "REJECTED_EMPTY_PAYLOAD",
                "message": "Request body must contain valid JSON."
            }), 400

        transport = request.headers.get("X-Transport-Type", "HTTP")

        # Route through Edge Gateway Concentrator Service
        result = GLOBAL_EDGE_GATEWAY_SERVICE.ingest_sensor_packet(payload, transport=transport)

        status_code = 200 if result.get("status") in ("ACCEPTED", "SUCCESS") else (
            202 if result.get("status") == "BUFFERED_OFFLINE" else 400
        )

        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Error ingesting telemetry: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# COMMISSIONING & CALIBRATION WORKFLOWS
# ─────────────────────────────────────────────────────────────────────────────

@iot_bp.route("/api/iot/commission", methods=["POST"])
def commission_device():
    """
    POST /api/iot/commission
    ------------------------
    Executes field commissioning workflow stages:
    REGISTER -> INSTALL -> CALIBRATE -> CONNECT -> HEARTBEAT -> TELEMETRY -> VALIDATE -> ACCEPT
    Body:
        {
            "device_id": str,
            "stage": str,
            "sensor_type": str (required for REGISTER),
            "sector_id": str,
            "latitude": float,
            "longitude": float,
            "gateway_id": str,
            "details": dict (optional)
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        device_id = data.get("device_id")
        stage = (data.get("stage") or "REGISTER").upper()

        if not device_id:
            return jsonify({"status": "ERROR", "message": "Missing required field 'device_id'"}), 400

        # Initial registration if stage is REGISTER
        if stage == "REGISTER":
            sensor_type = data.get("sensor_type", "piezometer")
            lat = float(data.get("latitude", 27.33))
            lon = float(data.get("longitude", 88.61))
            sec_id = data.get("sector_id", "SK-NH10-KM48")
            gw_id = data.get("gateway_id", "GW-01")

            dev = SensorDevice(
                device_id=device_id,
                sensor_id=data.get("sensor_id", device_id),
                sensor_type=sensor_type,
                latitude=lat,
                longitude=lon,
                sector_id=sec_id,
                gateway_id=gw_id,
                status=STATUS_REGISTERED,
                installation_status="PENDING_FIELD_INSTALL"
            )
            GLOBAL_SENSOR_REGISTRY.register_device(dev)

        # Advance commissioning stage
        res = GLOBAL_SENSOR_REGISTRY.advance_commissioning(
            device_id=device_id, stage=stage, details=data.get("details")
        )

        status_code = 200 if res.get("status") == "SUCCESS" else 400
        return jsonify(res), status_code

    except Exception as e:
        logger.error(f"Error in device commissioning: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/iot/calibration", methods=["POST"])
def upload_calibration():
    """
    POST /api/iot/calibration
    -------------------------
    Uploads or updates a certified sensor calibration record.
    Body:
        {
            "sensor_id": str,
            "calibration_id": str,
            "calibration_date": ISO str,
            "calibration_due": ISO str,
            "zero_offset": float,
            "scale_factor": float,
            "calibration_source": str
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        sensor_id = data.get("sensor_id")
        if not sensor_id:
            return jsonify({"status": "ERROR", "message": "Missing 'sensor_id'"}), 400

        now_iso = datetime.now(timezone.utc).isoformat()
        cal_id = data.get("calibration_id") or f"CAL-{sensor_id}-{int(datetime.now(timezone.utc).timestamp())}"
        cal_date = data.get("calibration_date") or now_iso
        cal_due = data.get("calibration_due") or "2027-12-31T23:59:59Z"

        record = CalibrationRecord(
            calibration_id=cal_id,
            sensor_id=sensor_id,
            calibration_date=cal_date,
            calibration_due=cal_due,
            zero_offset=float(data.get("zero_offset", 0.0)),
            scale_factor=float(data.get("scale_factor", 1.0)),
            calibration_source=data.get("calibration_source", "FIELD_MANUAL")
        )

        registered = GLOBAL_CALIBRATION_ENGINE.register_calibration(record)

        return jsonify({
            "status": "SUCCESS",
            "calibration": registered.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error uploading calibration: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# EDGE CORRIDOR ALERT POLICY & ACOUSTIC SIRENS
# ─────────────────────────────────────────────────────────────────────────────

@iot_bp.route("/api/edge/alert/test", methods=["POST"])
def test_edge_alert():
    """
    POST /api/edge/alert/test
    -------------------------
    Evaluates real or test sensor telemetry against localized corridor thresholds.
    Can also trigger simulated siren verification event.
    Body:
        {
            "measurements": { "pore_pressure": 48.0, "tilt_rate": 2.8 },
            "sector_id": "SK-NH10-KM48",
            "trigger_siren_test": bool
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        measurements = data.get("measurements", {"pore_pressure": 46.5})
        sector_id = data.get("sector_id", "SK-NH10-KM48")

        eval_result = GLOBAL_EDGE_ALERT_POLICY.evaluate_reading(
            measurements=measurements, sector_id=sector_id
        )

        siren_test_result = None
        if data.get("trigger_siren_test"):
            siren_test_result = GLOBAL_SIREN_CONTROLLER.test(
                duration_sec=3, operator="Edge Alert Test Diagnostic"
            )

        return jsonify({
            "status": "SUCCESS",
            "evaluation": eval_result,
            "siren_test": siren_test_result
        }), 200

    except Exception as e:
        logger.error(f"Error executing edge alert test: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/edge/health", methods=["GET"])
def edge_health():
    """
    GET /api/edge/health
    --------------------
    Returns edge gateway health, local buffer count, and power status.
    """
    try:
        status = GLOBAL_EDGE_GATEWAY_SERVICE.get_status()
        return jsonify({"status": "SUCCESS", "edge_gateway": status}), 200
    except Exception as e:
        logger.error(f"Error fetching edge health: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/siren/status", methods=["GET"])
def siren_status():
    """
    GET /api/siren/status
    ---------------------
    Returns acoustic siren controller status, safety dry-run state, and audit log.
    """
    try:
        status = GLOBAL_SIREN_CONTROLLER.status()
        recent_log = GLOBAL_SIREN_CONTROLLER.get_event_log(limit=10)
        return jsonify({
            "status": "SUCCESS",
            "siren": status,
            "recent_events": recent_log
        }), 200
    except Exception as e:
        logger.error(f"Error fetching siren status: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/siren/activate", methods=["POST"])
def siren_activate():
    """
    POST /api/siren/activate
    ------------------------
    Manual or automated siren trigger.
    Body:
        {
            "level": "WARNING" | "CRITICAL",
            "reason": str,
            "auth_token": str (required for physical output)
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        level = data.get("level", "WARNING")
        reason = data.get("reason", "Corridor Hazard Emergency")
        token = data.get("auth_token")

        res = GLOBAL_SIREN_CONTROLLER.activate(level=level, reason=reason, auth_token=token)
        return jsonify({"status": "SUCCESS", "event": res}), 200
    except Exception as e:
        logger.error(f"Error activating siren: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/siren/disarm", methods=["POST"])
def siren_disarm():
    """
    POST /api/siren/disarm
    ----------------------
    Silences active acoustic sirens and disarms controller.
    """
    try:
        operator = request.args.get("operator", "Safety Officer")
        res = GLOBAL_SIREN_CONTROLLER.disarm(operator=operator)
        return jsonify({"status": "SUCCESS", "siren": res}), 200
    except Exception as e:
        logger.error(f"Error disarming siren: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@iot_bp.route("/api/iot/bench/status", methods=["GET"])
def iot_bench_status():
    """
    GET /api/iot/bench/status
    -------------------------
    Reports hardware-in-the-loop and bench simulator status.
    Distinguishes physical serial/USB device presence vs bench simulator.
    """
    try:
        from services.hardware_interface import GLOBAL_HARDWARE_INTERFACE
        from services.bench_simulator import GLOBAL_BENCH_SIMULATOR

        hitl_status = GLOBAL_HARDWARE_INTERFACE.get_status()
        sim_status = GLOBAL_BENCH_SIMULATOR.get_status()

        return jsonify({
            "status": "SUCCESS",
            "physical_deployment_state": "PHYSICAL_DEPLOYMENT_PENDING" if hitl_status["hardware_state"] != "PHYSICAL_DEVICE_ACTIVE" else "ACTIVE",
            "hardware_state": hitl_status["hardware_state"],
            "provenance": hitl_status["provenance"],
            "has_physical_port": hitl_status["has_physical_port"],
            "ports": hitl_status["ports"],
            "is_bench_mode": hitl_status["is_bench_mode"],
            "simulator": sim_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching bench status: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500

