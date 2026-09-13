# -*- coding: utf-8 -*-
"""
backend/field_routes.py
=======================
PARVAT NETRA • PAHAD AI — Field Deployment & Corridor Validation REST API
-------------------------------------------------------------------------
Endpoints for mountain corridor management, physical asset inventories,
gateway propagation planning, mobile evidence synchronization, radio link
benchmarks, and supervised field shadow operations.
"""

from __future__ import annotations

import sqlite3
import logging
from flask import Blueprint, request, jsonify

from engine.corridor_registry import CORRIDOR_REGISTRY, SQLITE_DB_PATH
from engine.sensor_inventory import SENSOR_INVENTORY
from services.sensor_placement_planner import SENSOR_PLACEMENT_PLANNER
from services.gateway_planner import GATEWAY_PLANNER
from services.field_evidence_service import FIELD_EVIDENCE_SERVICE, FieldEvidenceRecord
from services.field_shadow_service import FIELD_SHADOW_SERVICE
from scripts.test_radio_link import run_radio_test

logger = logging.getLogger("FIELD_ROUTES")

field_bp = Blueprint("field_bp", __name__, url_prefix="/api/field")


@field_bp.route("/corridors", methods=["GET"])
def list_corridors():
    """Returns all registered Himalayan transport/settlement corridors."""
    status_filter = request.args.get("status")
    corridors = CORRIDOR_REGISTRY.list_corridors(status=status_filter)
    summary = CORRIDOR_REGISTRY.summary()
    return jsonify({
        "status": "SUCCESS",
        "total_corridors": len(corridors),
        "summary": summary,
        "corridors": [c.to_dict() for c in corridors]
    }), 200


@field_bp.route("/corridors/<corridor_id>", methods=["GET"])
def get_corridor(corridor_id: str):
    """Retrieves detailed corridor definition, sensor sites, and evacuation corridors."""
    corridor = CORRIDOR_REGISTRY.get_corridor(corridor_id)
    if not corridor:
        return jsonify({"error": f"Corridor '{corridor_id}' not found"}), 404
    return jsonify({
        "status": "SUCCESS",
        "corridor": corridor.to_dict()
    }), 200


@field_bp.route("/sensors", methods=["GET"])
def list_sensors():
    """Lists physical sensor hardware assets in the corridor inventory."""
    status = request.args.get("status")
    corridor_id = request.args.get("corridor_id")
    sensor_type = request.args.get("sensor_type")

    assets = SENSOR_INVENTORY.list_assets(
        status=status, corridor_id=corridor_id, sensor_type=sensor_type
    )
    summary = SENSOR_INVENTORY.summary()

    return jsonify({
        "status": "SUCCESS",
        "total_assets": len(assets),
        "summary": summary,
        "assets": [a.to_dict() for a in assets]
    }), 200


@field_bp.route("/gateways", methods=["GET"])
def list_gateways():
    """Evaluates estimated RF propagation and Fresnel clearance for corridor gateways."""
    corridor_id = request.args.get("corridor_id", "CORR-NH10-SIKKIM-KM48")
    try:
        plan = GATEWAY_PLANNER.plan_corridor_gateways(corridor_id)
        return jsonify({
            "status": "SUCCESS",
            "corridor_id": corridor_id,
            "planning": plan
        }), 200
    except KeyError as e:
        return jsonify({"error": str(e)}), 404


@field_bp.route("/commissioning", methods=["GET"])
def get_commissioning():
    """Retrieves 7-step field evidence and audit records for a sensor device."""
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "Query parameter 'device_id' is required"}), 400

    evidence = FIELD_EVIDENCE_SERVICE.get_device_evidence(device_id)
    return jsonify({
        "status": "SUCCESS",
        "device_id": device_id,
        "evidence_count": len(evidence),
        "evidence": [e.to_dict() for e in evidence]
    }), 200


@field_bp.route("/evidence/sync", methods=["POST"])
def sync_offline_evidence():
    """Batch-synchronizes offline mobile commissioning evidence from field technicians."""
    data = request.get_json(silent=True) or {}
    records = data.get("records") if isinstance(data, dict) and "records" in data else data

    if not isinstance(records, list):
        return jsonify({"error": "Payload must be a JSON array of evidence records or contain 'records' list"}), 400

    result = FIELD_EVIDENCE_SERVICE.batch_sync_offline_evidence(records)
    return jsonify({
        "status": result["status"],
        "result": result
    }), 200


@field_bp.route("/radio-tests", methods=["GET"])
def list_radio_tests():
    """Retrieves recent on-site LoRa radio link benchmarks."""
    device_id = request.args.get("device_id")
    limit = min(100, int(request.args.get("limit", 20)))

    conn = sqlite3.connect(SQLITE_DB_PATH)
    try:
        cur = conn.cursor()
        if device_id:
            cur.execute("""
                SELECT test_id, device_id, gateway_id, corridor_id,
                       rssi, snr, packet_delivery_ratio, latency_ms,
                       verdict, details, timestamp
                FROM field_radio_tests
                WHERE device_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (device_id, limit))
        else:
            cur.execute("""
                SELECT test_id, device_id, gateway_id, corridor_id,
                       rssi, snr, packet_delivery_ratio, latency_ms,
                       verdict, details, timestamp
                FROM field_radio_tests
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        rows = cur.fetchall()

        import json
        records = [
            {
                "test_id": r[0],
                "device_id": r[1],
                "gateway_id": r[2],
                "corridor_id": r[3],
                "rssi_dbm": r[4],
                "snr_db": r[5],
                "packet_delivery_ratio": r[6],
                "latency_ms": r[7],
                "verdict": r[8],
                "details": json.loads(r[9]),
                "timestamp": r[10]
            }
            for r in rows
        ]

        return jsonify({
            "status": "SUCCESS",
            "count": len(records),
            "tests": records
        }), 200
    finally:
        conn.close()


@field_bp.route("/radio-test", methods=["POST"])
def post_radio_test():
    """Executes or logs a real field LoRa RF link performance measurement."""
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id", "SN-PIEZ-NH10-01")
    gateway_id = data.get("gateway_id", "GW-NH10-SINGTAM-01")
    corridor_id = data.get("corridor_id", "CORR-NH10-SIKKIM-KM48")
    packets = int(data.get("packets", 10))
    rssi = float(data["rssi"]) if "rssi" in data else None
    snr = float(data["snr"]) if "snr" in data else None
    pdr = float(data["pdr"]) if "pdr" in data else None
    latency = float(data["latency"]) if "latency" in data else None

    result = run_radio_test(
        device_id=device_id,
        gateway_id=gateway_id,
        corridor_id=corridor_id,
        num_packets=packets,
        rssi_input=rssi,
        snr_input=snr,
        pdr_input=pdr,
        latency_input=latency
    )

    return jsonify({
        "status": "SUCCESS",
        "result": result
    }), 200


@field_bp.route("/shadow/evaluate", methods=["POST"])
def evaluate_shadow():
    """Executes supervised field shadow inference on a monitored corridor."""
    data = request.get_json(silent=True) or {}
    corridor_id = data.get("corridor_id", "CORR-NH10-SIKKIM-KM48")
    telemetry = data.get("telemetry", {})

    try:
        evaluation = FIELD_SHADOW_SERVICE.evaluate_corridor_risk(
            corridor_id=corridor_id, telemetry=telemetry
        )
        return jsonify({
            "status": "SUCCESS",
            "evaluation": evaluation
        }), 200
    except KeyError as e:
        return jsonify({"error": str(e)}), 404


@field_bp.route("/shadow/status", methods=["GET"])
def shadow_status():
    """Reports status of the supervised field shadow trial and recent audit logs."""
    status = FIELD_SHADOW_SERVICE.get_shadow_status()
    return jsonify({
        "status": "SUCCESS",
        "shadow_status": status
    }), 200
