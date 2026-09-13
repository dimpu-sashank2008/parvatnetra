# -*- coding: utf-8 -*-
"""
backend/sms_routes.py
=====================
PARVAT NETRA • Production Emergency SMS REST API Blueprint
----------------------------------------------------------
Phase 10I: Dissemination endpoints, DLR webhooks, DLT readiness, and delivery tracking.

Routes:
  POST /api/sms/queue-emergency          - Queues authorized geofenced emergency SMS package
  POST /api/sms/dlr                      - Ingests asynchronous carrier delivery receipts (DLR)
  GET  /api/sms/status                   - Reports provider configuration, DLT readiness, and safety modes
  GET  /api/sms/delivery/<dispatch_id>   - Retrieves delivery receipt and delivery status
  GET  /api/sms/sachet/<incident_id>     - SACHET/CAP handoff preview
  POST /api/sms/cell-broadcast           - Cell Broadcast PWS preview

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001 / Phase 10I
"""

from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify, Response

from services.production_sms_service import (
    PRODUCTION_SMS_SERVICE,
    STATE_DELIVERED,
    STATE_FAILED,
    STATE_BLOCKED,
    TEMPLATE_LANDSLIDE_WARNING
)
from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER

logger = logging.getLogger("SMS_ROUTES")

sms_bp = Blueprint("sms_bp", __name__, url_prefix="/api/sms")


@sms_bp.route("/status", methods=["GET"])
def get_sms_status():
    """Returns provider configuration state, India Government DLT readiness, and safety modes."""
    try:
        status_data = PRODUCTION_SMS_SERVICE.get_provider_configuration_status()
        return jsonify({
            "status": "success",
            "data": status_data
        }), 200
    except Exception as exc:
        logger.error(f"[SMSRoutes] Error fetching SMS status: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@sms_bp.route("/queue-emergency", methods=["POST"])
def queue_emergency_sms():
    """
    Queues geofenced emergency SMS package.
    Enforces DMA 2005 authority gate, 2-of-3 corroboration, geofence, and idempotency.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
        incident_id = body.get("incident_id")
        actor_id = body.get("actor_id")
        actor_role = body.get("actor_role")
        auth_token = body.get("auth_token")
        geofence_polygon = body.get("geofence_polygon")
        template_type = body.get("template_type", TEMPLATE_LANDSLIDE_WARNING)
        jurisdiction = body.get("jurisdiction")
        custom_action = body.get("custom_action")

        if not incident_id:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter 'incident_id'"
            }), 400

        result = PRODUCTION_SMS_SERVICE.dispatch_geofenced_sms(
            incident_id=incident_id,
            actor_id=actor_id or "ANONYMOUS",
            actor_role=actor_role or "PUBLIC",
            auth_token=auth_token or "",
            geofence_polygon=geofence_polygon or [],
            template_type=template_type,
            jurisdiction=jurisdiction,
            custom_action=custom_action
        )

        status_code = 200 if result.get("success", False) else 403
        if result.get("status") == "INVALID_GEOFENCE":
            status_code = 400

        return jsonify({
            "status": "success" if result.get("success") else "rejected",
            "data": result
        }), status_code

    except Exception as exc:
        logger.error(f"[SMSRoutes] SMS dispatch error: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@sms_bp.route("/dlr", methods=["POST"])
def handle_delivery_receipt_callback():
    """
    Asynchronous Webhook Callback for Telecom Gateway Delivery Receipts (DLR).
    Transitions record to DELIVERED only on authentic carrier delivery confirmation.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
        dispatch_id = body.get("dispatch_id")
        provider_reference = body.get("provider_reference") or body.get("msg_id") or "DLR-REF-UNKNOWN"
        carrier_status = body.get("carrier_status") or body.get("status") or "DELIVRD"
        failure_reason = body.get("failure_reason")

        if not dispatch_id:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter 'dispatch_id'"
            }), 400

        ok, msg = PRODUCTION_SMS_SERVICE.receipt_tracker.update_from_webhook(
            dispatch_id=dispatch_id,
            provider_reference=provider_reference,
            carrier_status=carrier_status,
            failure_reason=failure_reason
        )

        return jsonify({
            "status": "success" if ok else "error",
            "message": msg,
            "dispatch_id": dispatch_id
        }), 200

    except Exception as exc:
        logger.error(f"[SMSRoutes] Error processing DLR callback: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@sms_bp.route("/delivery/<dispatch_id>", methods=["GET"])
def get_sms_delivery_record(dispatch_id: str):
    """Retrieves delivery receipt and tracking information by dispatch ID."""
    try:
        receipt = PRODUCTION_SMS_SERVICE.receipt_tracker.get_receipt(dispatch_id)
        if not receipt:
            return jsonify({
                "status": "not_found",
                "message": f"Dispatch ID '{dispatch_id}' not found"
            }), 404

        return jsonify({
            "status": "success",
            "dispatch_id": dispatch_id,
            "data": receipt
        }), 200

    except Exception as exc:
        logger.error(f"[SMSRoutes] Error retrieving receipt {dispatch_id}: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@sms_bp.route("/sachet/<incident_id>", methods=["GET"])
def get_sachet_handoff(incident_id: str):
    """Returns SACHET / OASIS CAP v1.2 warning handoff package."""
    try:
        handoff = PRODUCTION_SMS_SERVICE.export_sachet_cap(incident_id)
        return jsonify({
            "status": "success",
            "data": handoff
        }), 200
    except Exception as exc:
        logger.error(f"[SMSRoutes] Error generating SACHET handoff for {incident_id}: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@sms_bp.route("/cell-broadcast", methods=["POST"])
def preview_cell_broadcast():
    """Generates provider-neutral Cell Broadcast package preview."""
    try:
        body = request.get_json(force=True, silent=True) or {}
        geofence = body.get("geofence_polygon", [])
        severity = body.get("severity", "Severe")
        urgency = body.get("urgency", "Immediate")
        language = body.get("language", "en")
        message = body.get("message", "PAHAD AI Landslide Hazard Warning")
        expiry = body.get("expiry", "2026-12-31T23:59:59Z")

        res = PRODUCTION_SMS_SERVICE.export_cell_broadcast_payload(
            geofence_polygon=geofence,
            severity=severity,
            urgency=urgency,
            language=language,
            message=message,
            expiry_iso=expiry
        )
        return jsonify({
            "status": "success",
            "data": res
        }), 200

    except Exception as exc:
        logger.error(f"[SMSRoutes] Error formulating Cell Broadcast payload: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500
