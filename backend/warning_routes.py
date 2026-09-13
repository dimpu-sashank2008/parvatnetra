# -*- coding: utf-8 -*-
"""
backend/warning_routes.py
=========================
PARVAT NETRA • Multi-Channel Emergency Warning REST API Blueprint
-----------------------------------------------------------------
Phase 10E: Dissemination endpoints, delivery tracking, and CAP gateway feed.

Routes:
  POST /api/warning/disseminate           - Dispatches authorized warning package across channels
  GET  /api/warning/channels/status       - Operating status and dry-run safety modes of all 7 channels
  GET  /api/warning/delivery/<dissem_id>  - Independent delivery receipt tracking per channel
  GET  /api/warning/cap/<incident_id>     - OASIS CAP v1.2 XML / JSON test feed
  GET  /api/warning/audit                 - Cryptographic audit trail & integrity verification

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001 / Phase 10E
"""

from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify, Response

from services.public_warning_service import (
    PUBLIC_WARNING_SERVICE,
    CHANNEL_SMS,
    CHANNEL_CELL_BROADCAST,
    CHANNEL_CAP_GATEWAY,
    CHANNEL_SIREN,
    CHANNEL_WEB_PUSH,
    CHANNEL_MOBILE_PUSH,
    CHANNEL_ROADSIDE_VMS
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER

logger = logging.getLogger("WARNING_ROUTES")

warning_bp = Blueprint("warning_bp", __name__, url_prefix="/api/warning")


@warning_bp.route("/channels/status", methods=["GET"])
def get_channel_status():
    """Returns operational configuration and safety modes for all 7 channels."""
    try:
        status_data = PUBLIC_WARNING_SERVICE.get_channel_status()
        return jsonify({
            "status": "success",
            "data": status_data
        }), 200
    except Exception as exc:
        logger.error(f"[WarningRoutes] Error fetching channel status: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@warning_bp.route("/disseminate", methods=["POST"])
def disseminate_warning():
    """
    Dispatches an authorized emergency warning package.
    Requires statutory DMA 2005 authority credentials, valid token, and 2-of-3 corroboration.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
        incident_id = body.get("incident_id")
        actor_id = body.get("actor_id")
        actor_role = body.get("actor_role")
        auth_token = body.get("auth_token")
        geofence_polygon = body.get("geofence_polygon")
        target_channels = body.get("channels")
        jurisdiction = body.get("jurisdiction")

        if not incident_id:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter 'incident_id'"
            }), 400

        result = PUBLIC_WARNING_SERVICE.disseminate_emergency_warning(
            incident_id=incident_id,
            actor_id=actor_id or "ANONYMOUS",
            actor_role=actor_role or "PUBLIC",
            auth_token=auth_token or "",
            geofence_polygon=geofence_polygon or [],
            target_channels=target_channels,
            jurisdiction=jurisdiction
        )

        status_code = 200 if result.get("success", False) or result.get("status") == "DISSEMINATED_DRY_RUN" else 403
        if result.get("status") == "INVALID_GEOFENCE":
            status_code = 400

        return jsonify({
            "status": "success" if status_code == 200 else "rejected",
            "data": result
        }), status_code

    except Exception as exc:
        logger.error(f"[WarningRoutes] Dissemination execution failed: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@warning_bp.route("/delivery/<dissemination_id>", methods=["GET"])
def get_delivery_status(dissemination_id: str):
    """Returns unified independent delivery tracking records for a dissemination package."""
    try:
        record = PUBLIC_WARNING_SERVICE.get_dissemination_record(dissemination_id)
        if not record:
            return jsonify({
                "status": "not_found",
                "message": f"Dissemination ID '{dissemination_id}' not found"
            }), 404

        return jsonify({
            "status": "success",
            "dissemination_id": dissemination_id,
            "data": record
        }), 200
    except Exception as exc:
        logger.error(f"[WarningRoutes] Error retrieving delivery record {dissemination_id}: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@warning_bp.route("/cap/<incident_id>", methods=["GET"])
def get_cap_alert(incident_id: str):
    """Returns compliant OASIS CAP v1.2 XML or JSON feed for an incident."""
    try:
        format_type = request.args.get("format", "json").lower()
        inc = EOC_INCIDENT_MANAGER.get_incident(incident_id)

        sector_name = getattr(inc, "sector_id", "NH-10 Himalayan Corridor") if inc else "NH-10 Himalayan Corridor"
        severity = getattr(inc, "severity", "WARNING") if inc else "WARNING"

        multilingual = PUBLIC_WARNING_SERVICE.format_multilingual_package(
            sector=sector_name,
            alert_id=incident_id,
            severity=severity
        )

        cap_payload = {
            "identifier": f"CAP-{incident_id}",
            "sender": "pahad-ews@ner.gov.in",
            "sent": "2026-09-13T09:00:00Z",
            "status": "Actual",
            "msgType": "Alert",
            "scope": "Public",
            "severity": severity.capitalize(),
            "urgency": "Immediate",
            "certainty": "Observed",
            "headline": multilingual["en"]["push_title"],
            "description": multilingual["en"]["push_body"],
            "instruction": "Follow designated mountain evacuation detours.",
            "areaDesc": sector_name,
            "polygon": [[27.33, 88.61], [27.34, 88.61], [27.34, 88.62], [27.33, 88.62], [27.33, 88.61]],
            "expiry": "2026-12-31T23:59:59Z",
            "incident_id": incident_id
        }

        staged = PUBLIC_WARNING_SERVICE.cap_adapter.stage_cap_alert(cap_payload)

        if format_type == "xml":
            xml_str = staged.get("xml_payload", "")
            return Response(xml_str, mimetype="application/xml")

        return jsonify({
            "status": "success",
            "incident_id": incident_id,
            "cap_data": staged
        }), 200

    except Exception as exc:
        logger.error(f"[WarningRoutes] Error generating CAP feed for {incident_id}: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@warning_bp.route("/audit", methods=["GET"])
def get_audit_trail():
    """Returns cryptographic audit ledger records and validates chained hash integrity."""
    try:
        limit = int(request.args.get("limit", 50))
        entries = PUBLIC_WARNING_SERVICE.audit_ledger.get_entries(limit=limit)
        is_valid, checked_count = PUBLIC_WARNING_SERVICE.audit_ledger.verify_integrity()

        return jsonify({
            "status": "success",
            "ledger_integrity": "INTACT" if is_valid else "CORRUPTED",
            "total_blocks_verified": checked_count,
            "entries_count": len(entries),
            "entries": entries
        }), 200
    except Exception as exc:
        logger.error(f"[WarningRoutes] Error fetching audit ledger: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500
