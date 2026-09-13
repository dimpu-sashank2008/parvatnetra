# -*- coding: utf-8 -*-
"""
backend/operational_routes.py
=============================
PARVAT NETRA • PAHAD AI — Real-Time Supervised Operations REST API
------------------------------------------------------------------
REST API endpoints exposing operational state machines, PAHAD decision records,
authority review workflows, geofencing, notification delivery, incident management,
and append-only audit trails.
"""

from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify

from engine.operational_state_machine import OPERATIONAL_STATE_MACHINE
from engine.pahad_decision_store import PAHAD_DECISION_STORE
from engine.incident_manager import INCIDENT_MANAGER
from services.authority_review_service import AUTHORITY_REVIEW_SERVICE
from services.field_task_service import FIELD_TASK_SERVICE, FieldVerificationReport
from services.geofence_service import GEOFENCE_SERVICE
from services.notification_orchestrator import NOTIFICATION_ORCHESTRATOR
from services.escalation_engine import ESCALATION_ENGINE

logger = logging.getLogger("OPERATIONAL_ROUTES")

operations_bp = Blueprint("operations_bp", __name__, url_prefix="/api/operations")


@operations_bp.route("/active", methods=["GET"])
def get_active_operations():
    """Lists all active monitored hazard entities and their operational lifecycle states."""
    active = OPERATIONAL_STATE_MACHINE.list_active_entities()
    return jsonify({
        "status": "SUCCESS",
        "active_entities_count": len(active),
        "entities": active
    }), 200


@operations_bp.route("/decisions", methods=["GET"])
def get_decisions():
    """Retrieves recent multi-modal PAHAD AI risk decisions."""
    sector_id = request.args.get("sector_id")
    limit = min(100, int(request.args.get("limit", 50)))
    decisions = PAHAD_DECISION_STORE.list_decisions(sector_id=sector_id, limit=limit)
    return jsonify({
        "status": "SUCCESS",
        "count": len(decisions),
        "decisions": decisions
    }), 200


@operations_bp.route("/evaluate", methods=["POST"])
def evaluate_observations():
    """Evaluates telemetry observations, performs corroboration & OOD check, and records decision."""
    data = request.get_json(silent=True) or {}
    sector_id = data.get("sector_id", "SK-NH10-KM48")
    observations = data.get("observations", {})

    record = PAHAD_DECISION_STORE.evaluate_and_record(
        sector_id=sector_id,
        observations=observations
    )

    # Automatically advance state machine from MONITORING -> ANOMALY_DETECTED if hazard flagged
    if record["risk"] in ["CRITICAL", "HIGH"]:
        try:
            curr_state = OPERATIONAL_STATE_MACHINE.get_state(sector_id)
            if curr_state == "MONITORING":
                OPERATIONAL_STATE_MACHINE.transition(
                    entity_id=sector_id,
                    new_state="ANOMALY_DETECTED",
                    actor="PAHAD_INFERENCE_PIPELINE",
                    reason=f"Risk evaluated as {record['risk']} (FoS={record['fos']:.2f})"
                )
        except Exception as e:
            logger.warning(f"Could not auto-advance state for {sector_id}: {e}")

    return jsonify({
        "status": "SUCCESS",
        "decision": record
    }), 200


@operations_bp.route("/authority-review", methods=["POST"])
def submit_authority_review():
    """Processes human-in-the-loop review actions (APPROVE, REJECT, REQUEST_FIELD_VERIFICATION, etc.)."""
    data = request.get_json(silent=True) or {}
    decision_id = data.get("decision_id")
    reviewer_id = data.get("reviewer_id", "OFFICER_01")
    role = data.get("role", "DISTRICT_AUTHORITY")
    action = data.get("action", "APPROVE")
    justification = data.get("justification", "Reviewed telemetry and corroborated slope failure risk")
    auth_token = data.get("authorization_token")

    if not decision_id:
        return jsonify({"error": "'decision_id' is required"}), 400

    try:
        review_result = AUTHORITY_REVIEW_SERVICE.submit_review_action(
            decision_id=decision_id,
            reviewer_id=reviewer_id,
            role=role,
            action=action,
            justification=justification,
            authorization_token=auth_token
        )
        return jsonify({
            "status": "SUCCESS",
            "review": review_result
        }), 200
    except (ValueError, PermissionError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


@operations_bp.route("/field-verification", methods=["POST"])
def handle_field_verification():
    """Dispatches a field verification task or submits on-site ground inspection report."""
    data = request.get_json(silent=True) or {}
    action_type = data.get("action_type", "SUBMIT_REPORT")

    if action_type == "DISPATCH_TASK":
        task = FIELD_TASK_SERVICE.dispatch_field_task(
            decision_id=data.get("decision_id", "DEC-UNKNOWN"),
            sector_id=data.get("sector_id", "SK-NH10-KM48"),
            assigned_team=data.get("assigned_team", "BRO Quick Reaction Team"),
            target_location=data.get("target_location")
        )
        return jsonify({"status": "SUCCESS", "task": task}), 200
    else:
        # Submit report
        report = FieldVerificationReport(
            report_id=data.get("report_id", "REP-UNKNOWN"),
            task_id=data.get("task_id", "TASK-UNKNOWN"),
            operator=data.get("operator", "On-Duty BRO Officer"),
            location=data.get("location", {"latitude": 27.33, "longitude": 88.61, "accuracy_m": 4.0}),
            timestamp=data.get("timestamp", ""),
            media_reference=data.get("media_reference", []),
            observation=data.get("observation", "Tension crack verified"),
            severity=data.get("severity", "CONFIRMED_HIGH"),
            verification_result=data.get("verification_result", "HAZARD_CONFIRMED")
        )
        try:
            saved = FIELD_TASK_SERVICE.submit_field_report(report)
            return jsonify({"status": "SUCCESS", "report": saved}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


@operations_bp.route("/alerts", methods=["GET"])
def get_alerts():
    """Lists all active operational notifications and generated CAP bulletins."""
    notifications = NOTIFICATION_ORCHESTRATOR.list_notifications(limit=50)
    return jsonify({
        "status": "SUCCESS",
        "alerts_count": len(notifications),
        "alerts": notifications
    }), 200


@operations_bp.route("/incidents", methods=["GET"])
def get_incidents():
    """Lists disaster incident entities and response statuses."""
    status = request.args.get("status")
    incidents = INCIDENT_MANAGER.list_incidents(status=status)
    return jsonify({
        "status": "SUCCESS",
        "incidents_count": len(incidents),
        "incidents": incidents
    }), 200


@operations_bp.route("/notifications", methods=["GET"])
def get_notifications():
    """Lists notifications across all delivery channels."""
    alert_id = request.args.get("alert_id")
    limit = min(100, int(request.args.get("limit", 50)))
    notifs = NOTIFICATION_ORCHESTRATOR.list_notifications(alert_id=alert_id, limit=limit)
    return jsonify({
        "status": "SUCCESS",
        "count": len(notifs),
        "notifications": notifs
    }), 200


@operations_bp.route("/acknowledge", methods=["POST"])
def acknowledge_notification():
    """Records human operator or field unit confirmation of received emergency alert."""
    data = request.get_json(silent=True) or {}
    notif_id = data.get("notification_id")
    ack_by = data.get("acknowledged_by", "Control Room Operator")

    if not notif_id:
        return jsonify({"error": "'notification_id' is required"}), 400

    try:
        ack_res = NOTIFICATION_ORCHESTRATOR.record_acknowledgement(
            notification_id=notif_id,
            acknowledged_by=ack_by
        )
        return jsonify({"status": "SUCCESS", "acknowledgement": ack_res}), 200
    except KeyError as e:
        return jsonify({"error": str(e)}), 404


@operations_bp.route("/response-priority", methods=["GET"])
def get_response_priority():
    """Returns disaster response targets sorted by priority score."""
    incidents = INCIDENT_MANAGER.list_incidents()
    return jsonify({
        "status": "SUCCESS",
        "total_targets": len(incidents),
        "ranked_targets": incidents
    }), 200


@operations_bp.route("/escalate", methods=["POST"])
def trigger_escalation():
    """Scans for unacknowledged alerts or manually escalates an alert."""
    data = request.get_json(silent=True) or {}
    manual = data.get("manual", False)

    if manual:
        alert_id = data.get("alert_id")
        current_role = data.get("current_role", "FIELD_OPERATOR")
        reason = data.get("reason", "Operator unreachable")
        if not alert_id:
            return jsonify({"error": "'alert_id' required for manual escalation"}), 400
        res = ESCALATION_ENGINE.manual_escalate(alert_id, current_role, reason)
        return jsonify({"status": "SUCCESS", "escalation": res}), 200
    else:
        timeout = data.get("timeout_seconds")
        escalated = ESCALATION_ENGINE.check_and_escalate_unacknowledged(timeout_seconds=timeout)
        return jsonify({
            "status": "SUCCESS",
            "escalated_count": len(escalated),
            "escalations": escalated
        }), 200


@operations_bp.route("/audit", methods=["GET"])
def get_audit_trail():
    """Retrieves append-only operational lifecycle transition history for an entity."""
    entity_id = request.args.get("entity_id", "SK-NH10-KM48")
    history = OPERATIONAL_STATE_MACHINE.get_history(entity_id)
    reviews = AUTHORITY_REVIEW_SERVICE.list_reviews()
    return jsonify({
        "status": "SUCCESS",
        "entity_id": entity_id,
        "state_transitions": history,
        "authority_reviews": reviews
    }), 200
