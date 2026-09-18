# -*- coding: utf-8 -*-
"""
backend/edge/routes.py
======================
PARVAT NETRA • Edge Network & Local Warning REST Endpoints
---------------------------------------------------------
Implements Sections 12, 18, 19, 21, 25:
  - GET  /api/edge/status
  - GET  /api/edge/nodes
  - GET  /api/edge/network
  - GET  /api/edge/readings
  - GET  /api/edge/alerts
  - GET  /api/edge/siren/status
  - POST /api/edge/siren/test
  - POST /api/edge/siren/arm
  - POST /api/edge/siren/disarm
  - POST /api/edge/demo/inject
  - POST /api/edge/toggle-cloud
  - POST /api/edge/sync/flush
  - GET  /edge-network (UI template)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Optional
from flask import Blueprint, request, jsonify, render_template

from backend.edge.gateway import EdgeGateway

logger = logging.getLogger("EDGE_ROUTES")

# Global singleton instance for runtime operations
_GLOBAL_EDGE_GATEWAY: Optional[EdgeGateway] = None


def get_edge_gateway() -> EdgeGateway:
    """Returns the singleton instance of the local edge gateway."""
    global _GLOBAL_EDGE_GATEWAY
    if _GLOBAL_EDGE_GATEWAY is None:
        _GLOBAL_EDGE_GATEWAY = EdgeGateway(
            gateway_id=os.environ.get("EDGE_GATEWAY_ID", "GW-01"),
            location=os.environ.get("EDGE_GATEWAY_LOC", "Singtam Staging Depo (NH-10 Corridor)")
        )
    return _GLOBAL_EDGE_GATEWAY


def set_edge_gateway(gateway: EdgeGateway) -> None:
    """Explicitly sets or overrides the global gateway instance (e.g., during tests)."""
    global _GLOBAL_EDGE_GATEWAY
    _GLOBAL_EDGE_GATEWAY = gateway


edge_bp = Blueprint("edge_bp", __name__)


# ==============================================================================
# SECTION 18: EDGE NETWORK STATUS & TELEMETRY APIS
# ==============================================================================

@edge_bp.route("/api/edge/status", methods=["GET"])
def api_edge_status():
    """Returns gateway status, cloud connectivity, buffer count, mesh, siren, and BLE health."""
    try:
        gw = get_edge_gateway()
        status_data = gw.get_gateway_status()
        return jsonify({
            "status": "SUCCESS",
            "data": status_data,
            "provenance": "[LIVE]" if status_data.get("is_cloud_connected") else "[OFFLINE]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_STATUS] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/nodes", methods=["GET"])
def api_edge_nodes():
    """Returns registered LoRa mesh sensor and relay nodes with RF & health telemetry."""
    try:
        gw = get_edge_gateway()
        mesh_status = gw.mesh.get_network_status()
        return jsonify({
            "status": "SUCCESS",
            "gateway_id": gw.gateway_id,
            "total_nodes": mesh_status["total_nodes_registered"],
            "active_nodes": mesh_status["active_nodes_count"],
            "nodes": mesh_status["nodes"],
            "relays": list(gw.mesh.relays),
            "provenance": "[LIVE / MESH]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_NODES] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/network", methods=["GET"])
def api_edge_network():
    """Returns LoRa wireless mesh RF parameters, topology, and packet statistics."""
    try:
        gw = get_edge_gateway()
        status = gw.mesh.get_network_status()
        return jsonify({
            "status": "SUCCESS",
            "network": {
                "frequency_mhz": status["frequency_mhz"],
                "gateway_id": gw.gateway_id,
                "topology_type": "STAR_OF_STARS_WITH_RIDGE_RELAYS",
                "total_packets_received": status["total_packets_received"],
                "total_packets_forwarded": status["total_packets_forwarded"],
                "total_duplicates_dropped": status["total_duplicates_dropped"],
                "active_nodes_count": status["active_nodes_count"],
                "registered_nodes_count": status["total_nodes_registered"],
            },
            "provenance": "[SIMULATED / MESH ADAPTER]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_NETWORK] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/readings", methods=["GET"])
def api_edge_readings():
    """Returns recent in-situ geotechnical sensor readings from the local SQLite store."""
    try:
        gw = get_edge_gateway()
        limit = int(request.args.get("limit", 50))
        node_id = request.args.get("node_id")
        readings = gw.store.query_readings(node_id=node_id, limit=limit)
        return jsonify({
            "status": "SUCCESS",
            "count": len(readings),
            "readings": readings,
            "provenance": "[LIVE / BUFFERED]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_READINGS] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/alerts", methods=["GET"])
def api_edge_alerts():
    """Returns local safety threshold alert records dispatched at the edge."""
    try:
        gw = get_edge_gateway()
        limit = int(request.args.get("limit", 50))
        alerts = gw.store.query_alerts(limit=limit)
        return jsonify({
            "status": "SUCCESS",
            "count": len(alerts),
            "alerts": alerts,
            "provenance": "[EDGE SAFETY STATE]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_ALERTS] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ==============================================================================
# SECTION 10, 11, 12: SIREN CONTROLLER APIS
# ==============================================================================

@edge_bp.route("/api/edge/siren/status", methods=["GET"])
def api_edge_siren_status():
    """Returns siren controller arm state, physical enablement, and recent event logs."""
    try:
        gw = get_edge_gateway()
        return jsonify({
            "status": "SUCCESS",
            "siren": gw.siren.status(),
            "provenance": "[EDGE HARDWARE ADAPTER]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_SIREN_STATUS] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/siren/test", methods=["POST"])
def api_edge_siren_test():
    """
    POST /api/edge/siren/test
    Triggers a dry-run siren test generating a SIREN_TEST_EVENT without physical sounder activation.
    """
    try:
        gw = get_edge_gateway()
        data = request.get_json(silent=True) or {}
        requested_by = data.get("requested_by", "FIELD_OPERATOR_CONSOLE")
        test_event = gw.siren.test(requested_by=requested_by)
        return jsonify({
            "status": "SUCCESS",
            "message": "Siren test executed in dry-run safety mode. No physical acoustic activation occurred.",
            "event": test_event,
            "provenance": "[DEMO / DRY RUN]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_SIREN_TEST] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/siren/arm", methods=["POST"])
def api_edge_siren_arm():
    """Arms the siren controller to respond to WARNING/CRITICAL triggers."""
    try:
        gw = get_edge_gateway()
        gw.siren.arm()
        return jsonify({
            "status": "SUCCESS",
            "message": "Siren controller ARMED.",
            "siren": gw.siren.status()
        }), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/siren/disarm", methods=["POST"])
def api_edge_siren_disarm():
    """Disarms the siren controller."""
    try:
        gw = get_edge_gateway()
        gw.siren.disarm()
        return jsonify({
            "status": "SUCCESS",
            "message": "Siren controller DISARMED.",
            "siren": gw.siren.status()
        }), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ==============================================================================
# SECTION 19: DEMONSTRATION & INJECTION APIS
# ==============================================================================

@edge_bp.route("/api/edge/demo/inject", methods=["POST"])
def api_edge_demo_inject():
    """
    POST /api/edge/demo/inject
    Injects synthetic geotechnical sensor readings for SIH evaluator walkthrough.
    Requires PAHAD_DEMO_MODE=1 or development environment.
    Always marks incoming telemetry with [DEMO].
    """
    try:
        # Enforce demo mode policy
        demo_env = os.environ.get("PAHAD_DEMO_MODE", "1")
        if demo_env not in ("1", "true", "True") and os.environ.get("PARVAT_ENV") == "production":
            return jsonify({
                "status": "FORBIDDEN",
                "message": "Demonstration injection is disabled in strict production mode. Set PAHAD_DEMO_MODE=1."
            }), 403

        data = request.get_json(silent=True) or {}
        node_id = data.get("node_id", "SN-DEMO-SLOPE-01")

        reading_payload = {
            "node_id": node_id,
            "soil_moisture": float(data.get("soil_moisture", 35.0)),
            "pore_pressure": float(data.get("pore_pressure", 15.0)),
            "tilt": float(data.get("tilt", 0.5)),
            "rainfall": float(data.get("rainfall", 2.0)),
            "temperature": float(data.get("temperature", 18.5)),
            "humidity": float(data.get("humidity", 70.0)),
            "battery": int(data.get("battery", 95)),
            "signal_strength": int(data.get("signal_strength", -75)),
            "displacement": float(data.get("displacement", 0.0)),
            "crack_aperture": float(data.get("crack_aperture", 0.0)),
            "vibration": float(data.get("vibration", 0.0)),
            "provenance": "[DEMO]",
            "source": "SIMULATED_DEMO_INJECTION"
        }

        gw = get_edge_gateway()
        result = gw.process_json_reading(reading_payload)

        return jsonify({
            "status": "SUCCESS",
            "message": "Demonstration telemetry ingested into edge pipeline.",
            "pipeline_result": result,
            "provenance": "[DEMO]"
        }), 200

    except Exception as e:
        logger.error(f"[API_EDGE_DEMO_INJECT] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ==============================================================================
# SECTION 21: OFFLINE DISCONNECT / SYNC APIS
# ==============================================================================

@edge_bp.route("/api/edge/toggle-cloud", methods=["POST"])
def api_edge_toggle_cloud():
    """
    POST /api/edge/toggle-cloud
    Simulates severing or restoring regional satellite/cellular backhaul.
    Enables evaluator to inspect Edge Autonomous vs Connected behaviour.
    """
    try:
        gw = get_edge_gateway()
        new_state = gw.sync.set_cloud_connectivity(not gw.sync.is_cloud_connected)
        
        # If restored, attempt immediate flush
        flush_result = None
        if new_state:
            flush_result = gw.sync.flush_sync_queue(batch_size=50)

        return jsonify({
            "status": "SUCCESS",
            "is_cloud_connected": new_state,
            "mode": "CLOUD_CONNECTED" if new_state else "EDGE_OFFLINE_AUTONOMOUS",
            "flush_result": flush_result,
            "buffered_count": gw.store.get_queue_stats()["buffered_count"],
            "provenance": "[SIMULATED]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_TOGGLE_CLOUD] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/sync/flush", methods=["POST"])
def api_edge_sync_flush():
    """Manually forces a sync flush of buffered readings to central cloud."""
    try:
        gw = get_edge_gateway()
        batch_size = int(request.args.get("batch_size", 50))
        result = gw.sync.flush_sync_queue(batch_size=batch_size)
        return jsonify({
            "status": "SUCCESS",
            "sync_result": result,
            "queue_stats": gw.store.get_queue_stats(),
            "provenance": "[BUFFERED / SYNC]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_SYNC_FLUSH] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ==============================================================================
# FIRST RESPONDER OFFLINE FIELD TRIAGE & LORA PACKET APIS
# ==============================================================================

@edge_bp.route("/api/edge/field-reports/sync", methods=["POST"])
def api_edge_field_reports_sync():
    """
    POST /api/edge/field-reports/sync
    Ingests batched offline field triage reports from first responders/citizens.
    Validates, deduplicates, logs into local edge_store, and buffers for cloud sync.
    """
    try:
        gw = get_edge_gateway()
        payload = request.get_json(silent=True) or {}
        reports = payload.get("reports", [])
        if not isinstance(reports, list):
            return jsonify({"status": "ERROR", "message": "reports field must be a list"}), 400

        inserted_ids = []
        for r in reports:
            if isinstance(r, dict):
                rid = gw.store.insert_field_report(r, buffer_for_cloud=True)
                inserted_ids.append(rid)

        return jsonify({
            "status": "SUCCESS",
            "synced_count": len(inserted_ids),
            "report_ids": inserted_ids,
            "provenance": "[EDGE_LORA_SYNC]",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_FIELD_REPORTS_SYNC] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/field-reports", methods=["GET"])
def api_edge_field_reports():
    """Returns recent locally buffered field triage reports."""
    try:
        gw = get_edge_gateway()
        limit = int(request.args.get("limit", 50))
        reports = gw.store.query_field_reports(limit=limit)
        return jsonify({
            "status": "SUCCESS",
            "count": len(reports),
            "reports": reports,
            "provenance": "[EDGE_LOCAL_STORE]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_FIELD_REPORTS] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/mesh/packets", methods=["GET"])
def api_edge_mesh_packets():
    """Returns recent LoRa sub-GHz radio packet frames for packet inspector."""
    try:
        gw = get_edge_gateway()
        limit = int(request.args.get("limit", 25))
        packets = gw.mesh.get_recent_packets(limit=limit)
        return jsonify({
            "status": "SUCCESS",
            "packets": packets,
            "frequency_mhz": gw.mesh.frequency_mhz,
            "modulation": "LoRa CSS (SF7, BW 125kHz, CR 4/5)",
            "total_packets": gw.mesh.total_packets_received,
            "provenance": "[LIVE / LORA_MESH]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_MESH_PACKETS] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@edge_bp.route("/api/edge/mesh/simulate-burst", methods=["POST"])
def api_edge_mesh_simulate_burst():
    """Simulates an emergency sub-GHz radio packet burst from deep gorge sensor nodes."""
    try:
        gw = get_edge_gateway()
        count = int(request.args.get("count", 3))
        results = gw.mesh.simulate_burst(count=count)
        return jsonify({
            "status": "SUCCESS",
            "message": f"Simulated {len(results)} emergency LoRa sub-GHz frames.",
            "packets": results,
            "mesh_status": gw.mesh.get_network_status(),
            "provenance": "[SIMULATED / LORA_BURST]"
        }), 200
    except Exception as e:
        logger.error(f"[API_EDGE_MESH_SIMULATE_BURST] Error: {e}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(e)}), 500


# ==============================================================================
# SECTION 25: SEPARATE MISSION-CONTROL WEB PAGE
# ==============================================================================

@edge_bp.route("/edge-network")
def page_edge_network():
    """Renders the dedicated Edge Network & LoRa Mesh Mission Control Dashboard."""
    gw = get_edge_gateway()
    status = gw.get_gateway_status()
    nodes = list(gw.mesh.nodes.values())
    recent_readings = gw.store.query_readings(limit=15)
    recent_alerts = gw.store.query_alerts(limit=10)

    return render_template(
        "edge_network.html",
        gateway=status,
        nodes=nodes,
        readings=recent_readings,
        alerts=recent_alerts,
        current_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )


def register_edge_routes(flask_app, gateway: Optional[EdgeGateway] = None) -> None:
    """Helper to register the edge blueprint on the Flask application."""
    if gateway is not None:
        set_edge_gateway(gateway)
    flask_app.register_blueprint(edge_bp)
    logger.info("Edge Network REST routes registered on Flask app.")
