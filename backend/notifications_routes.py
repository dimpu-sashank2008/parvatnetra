# -*- coding: utf-8 -*-
"""
backend/notifications_routes.py
===============================
PARVAT NETRA • Phase 3.5 Intelligent Notification Center & Alert Policy Blueprint
---------------------------------------------------------------------------------
Implements Section 21, 22, 23, 32:
  - GET  /notifications (Mission-control Notification Center UI)
  - GET  /api/notifications (List alerts with lifecycle filtering)
  - GET  /api/notifications/<alert_id> (Full assessment, drivers & delivery status)
  - POST /api/notifications/<alert_id>/acknowledge (Operator acknowledgement)
  - POST /api/notifications/<alert_id>/authorize (Authority authorization sign-off)
  - POST /api/notifications/<alert_id>/dispatch (Multi-channel push/sms/cap dispatch)
  - GET  /api/notifications/<alert_id>/delivery-status (Per-channel delivery logs)
  - POST /api/push/subscribe (Browser/mobile push registration)
  - POST /api/push/unsubscribe (Revoke push subscription)
  - GET  /api/alert-policy/<sector_id> (Live alert policy evaluation)
  - GET  /api/geofence/<alert_id> (15 km impact geometry & recipient breakdown)
  - POST /api/notifications/demo/reset (Isolated demo reset)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import time
import logging
from typing import Optional
from flask import Blueprint, jsonify, request, render_template

from engine.pahad_notification_orchestrator import (
    NOTIFICATION_ORCHESTRATOR,
    PahadNotificationOrchestrator,
    DEDUP_INTERVAL_MINUTES
)
from engine.pahad_geofence import DEFAULT_RADIUS_KM
from engine.pahad_alert_policy import (
    PahadAlertPolicyEngine,
    ALERT_LEVEL_MAPPINGS
)
from services.push_service import PUSH_SERVICE
from services.sms_service import SMS_SERVICE

logger = logging.getLogger("NOTIFICATIONS_API")

notifications_bp = Blueprint("notifications_bp", __name__)


# ---------------------------------------------------------------------------
# 1. UI Route: Notification Center
# ---------------------------------------------------------------------------
@notifications_bp.route("/notifications", methods=["GET"])
def notification_center_view():
    """
    Renders the operational mission-control Notification Center.
    """
    state_filter = request.args.get("state", "ALL")
    active_alert_id = request.args.get("alert_id")
    alerts = NOTIFICATION_ORCHESTRATOR.list_alerts(filter_state=state_filter)
    recent_sms = SMS_SERVICE.list_recent_sms(limit=10)
    recent_push = PUSH_SERVICE.list_recent_deliveries(limit=10)
    audit_logs = NOTIFICATION_ORCHESTRATOR.list_audit_logs(limit=25)

    selected_alert = None
    if active_alert_id:
        selected_alert = NOTIFICATION_ORCHESTRATOR.get_alert(active_alert_id)
    elif alerts:
        selected_alert = alerts[0]

    return render_template(
        "notifications.html",
        alerts=alerts,
        selected_alert=selected_alert,
        recent_sms=recent_sms,
        recent_push=recent_push,
        audit_logs=audit_logs,
        filter_state=state_filter,
        dry_run=NOTIFICATION_ORCHESTRATOR.dry_run
    )


# ---------------------------------------------------------------------------
# 2. API Routes: Alert Lifecycle & Querying
# ---------------------------------------------------------------------------
@notifications_bp.route("/api/notifications", methods=["GET"])
def list_notifications():
    """
    GET /api/notifications?state=ALL|ACTIVE|ACKNOWLEDGED|FAILED|EXPIRED
    """
    state_filter = request.args.get("state", "ALL")
    alerts = NOTIFICATION_ORCHESTRATOR.list_alerts(filter_state=state_filter)
    return jsonify({
        "status": "SUCCESS",
        "count": len(alerts),
        "filter": state_filter,
        "alerts": alerts,
        "dry_run": NOTIFICATION_ORCHESTRATOR.dry_run
    }), 200


@notifications_bp.route("/api/notifications/status", methods=["GET"])
def get_notifications_status():
    """
    GET /api/notifications/status -> High-level status & operational parameters.
    """
    active_alerts = NOTIFICATION_ORCHESTRATOR.list_alerts(filter_state="ACTIVE")
    return jsonify({
        "success": True,
        "status": {
            "total_tracked": len(NOTIFICATION_ORCHESTRATOR._alerts),
            "active_count": len(active_alerts),
            "alert_radius_km": DEFAULT_RADIUS_KM,
            "push_dry_run": PUSH_SERVICE.dry_run,
            "sms_dry_run": SMS_SERVICE.dry_run,
            "dedup_window_minutes": DEDUP_INTERVAL_MINUTES,
            "dry_run": NOTIFICATION_ORCHESTRATOR.dry_run
        }
    }), 200


@notifications_bp.route("/api/notifications/active", methods=["GET"])
def get_active_notifications():
    """
    GET /api/notifications/active -> Convenient shorthand for active alerts.
    """
    active_alerts = NOTIFICATION_ORCHESTRATOR.list_alerts(filter_state="ACTIVE")
    return jsonify({
        "status": "SUCCESS",
        "count": len(active_alerts),
        "alerts": active_alerts,
        "dry_run": NOTIFICATION_ORCHESTRATOR.dry_run
    }), 200


@notifications_bp.route("/api/notifications/<alert_id>", methods=["GET"])
def get_notification_detail(alert_id: str):
    """
    GET /api/notifications/<alert_id> -> Comprehensive alert detail breakdown.
    """
    alert = NOTIFICATION_ORCHESTRATOR.get_alert(alert_id)
    if not alert:
        return jsonify({"status": "ERROR", "message": f"Alert {alert_id} not found."}), 404

    audit_logs = NOTIFICATION_ORCHESTRATOR.list_audit_logs(alert_id=alert_id, limit=20)
    return jsonify({
        "status": "SUCCESS",
        "alert": alert,
        "audit_logs": audit_logs
    }), 200


@notifications_bp.route("/api/notifications/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_notification(alert_id: str):
    """
    POST /api/notifications/<alert_id>/acknowledge
    Payload: {"actor": "Operator Name", "notes": "..."}
    """
    data = request.get_json(silent=True) or {}
    actor = data.get("actor", "Command Center Operator")
    notes = data.get("notes", "Acknowledged in operations center.")

    res = NOTIFICATION_ORCHESTRATOR.acknowledge_alert(alert_id, actor=actor, notes=notes)
    status_code = 200 if res.get("status") == "ACKNOWLEDGED" else 400
    return jsonify(res), status_code


@notifications_bp.route("/api/notifications/<alert_id>/authorize", methods=["POST"])
def authorize_notification(alert_id: str):
    """
    POST /api/notifications/<alert_id>/authorize
    Payload: {"actor": "District Magistrate", "notes": "..."}
    """
    data = request.get_json(silent=True) or {}
    actor = data.get("actor", "District Magistrate")
    notes = data.get("notes", "Authorized based on 3/3 signal agreement.")

    res = NOTIFICATION_ORCHESTRATOR.authorize_alert(alert_id, actor=actor, authorization_notes=notes)
    status_code = 200 if res.get("status") == "AUTHORIZED" else 400
    return jsonify(res), status_code


@notifications_bp.route("/api/notifications/<alert_id>/dispatch", methods=["POST"])
def dispatch_notification(alert_id: str):
    """
    POST /api/notifications/<alert_id>/dispatch
    Payload: {"actor": "Operations Officer", "channels": ["push", "sms", "cap", "edge"]}
    """
    data = request.get_json(silent=True) or {}
    actor = data.get("actor", "Disaster Operations Officer")
    channels = data.get("channels", ["push", "sms", "cap", "edge"])

    res = NOTIFICATION_ORCHESTRATOR.dispatch_alert(alert_id, actor=actor, selected_channels=channels)
    status_code = 200 if res.get("status") == "DISPATCHED" else 403
    return jsonify(res), status_code


@notifications_bp.route("/api/notifications/<alert_id>/delivery-status", methods=["GET"])
def get_notification_delivery_status(alert_id: str):
    """
    GET /api/notifications/<alert_id>/delivery-status
    """
    alert = NOTIFICATION_ORCHESTRATOR.get_alert(alert_id)
    if not alert:
        return jsonify({"status": "ERROR", "message": f"Alert {alert_id} not found."}), 404

    audit = NOTIFICATION_ORCHESTRATOR.list_audit_logs(alert_id=alert_id)
    return jsonify({
        "status": "SUCCESS",
        "alert_id": alert_id,
        "lifecycle_state": alert.get("lifecycle_state"),
        "channels_dispatched": alert.get("channels_dispatched", []),
        "zone_aggregates": alert.get("zone_aggregates", {}),
        "audit_trail": audit,
        "dry_run": NOTIFICATION_ORCHESTRATOR.dry_run
    }), 200


# ---------------------------------------------------------------------------
# 3. API Routes: Push Subscription
# ---------------------------------------------------------------------------
@notifications_bp.route("/api/push/subscribe", methods=["POST"])
def push_subscribe():
    """
    POST /api/push/subscribe
    Payload: {"recipient_id": "...", "endpoint": "...", "platform": "web"}
    """
    data = request.get_json(silent=True) or {}
    recipient_id = data.get("recipient_id", "REC-CITZ-WEB-USER")
    endpoint = data.get("endpoint", "")
    platform = data.get("platform", "web")

    if not endpoint:
        return jsonify({"status": "ERROR", "message": "Missing required push endpoint token."}), 400

    res = PUSH_SERVICE.subscribe(recipient_id=recipient_id, endpoint=endpoint, platform=platform)
    return jsonify(res), 200


@notifications_bp.route("/api/push/unsubscribe", methods=["POST"])
def push_unsubscribe():
    """
    POST /api/push/unsubscribe
    Payload: {"subscription_id": "..."}
    """
    data = request.get_json(silent=True) or {}
    sub_id = data.get("subscription_id", "")
    if not sub_id:
        return jsonify({"status": "ERROR", "message": "Missing subscription_id."}), 400

    res = PUSH_SERVICE.unsubscribe(sub_id)
    status_code = 200 if res.get("status") == "UNSUBSCRIBED" else 404
    return jsonify(res), status_code


# ---------------------------------------------------------------------------
# 4. API Routes: Policy Evaluation & Geofencing
# ---------------------------------------------------------------------------
@notifications_bp.route("/api/alert-policy/<sector_id>", methods=["GET"])
def evaluate_alert_policy_endpoint(sector_id: str):
    """
    GET /api/alert-policy/<sector_id> -> On-the-fly alert policy evaluation.
    """
    cri = float(request.args.get("cri", 78.0))
    prob = float(request.args.get("event_probability", 0.82))
    fos = float(request.args.get("fos", 0.96))
    rain_trig = request.args.get("rainfall_trigger", "EXCEEDED")
    sig_agree = request.args.get("signal_agreement", "3/3")

    dec = NOTIFICATION_ORCHESTRATOR.policy_engine.evaluate(
        cri=cri,
        event_probability=prob,
        factor_of_safety=fos,
        rainfall_trigger=rain_trig,
        signal_agreement=sig_agree,
        sector_id=sector_id
    )
    return jsonify({
        "status": "SUCCESS",
        "sector_id": sector_id,
        "policy_decision": dec.to_dict()
    }), 200


@notifications_bp.route("/api/geofence/<alert_id>", methods=["GET"])
def get_geofence_endpoint(alert_id: str):
    """
    GET /api/geofence/<alert_id> -> Impact geometry and eligible recipient aggregates.
    """
    alert = NOTIFICATION_ORCHESTRATOR.get_alert(alert_id)
    if not alert:
        return jsonify({"status": "ERROR", "message": f"Alert {alert_id} not found."}), 404

    return jsonify({
        "status": "SUCCESS",
        "alert_id": alert_id,
        "impact_geometry": alert.get("impact_geometry"),
        "zone_aggregates": alert.get("zone_aggregates")
    }), 200


# ---------------------------------------------------------------------------
# 5. API Routes: Demo Scenario & Reset
# ---------------------------------------------------------------------------
@notifications_bp.route("/api/notifications/demo/trigger", methods=["POST"])
def trigger_demo_scenario():
    """
    POST /api/notifications/demo/trigger
    Executes SIH deterministic demonstration sequence.
    """
    res = NOTIFICATION_ORCHESTRATOR.run_sih_demo_scenario()
    return jsonify(res), 200


@notifications_bp.route("/api/notifications/demo/reset", methods=["POST"])
def reset_demo_alerts():
    """
    POST /api/notifications/demo/reset -> Cleans only demo-generated alert states.
    """
    count = NOTIFICATION_ORCHESTRATOR.reset_demo_alerts()
    return jsonify({
        "status": "SUCCESS",
        "message": f"Cleared {count} demonstration alerts.",
        "remaining_alerts": len(NOTIFICATION_ORCHESTRATOR._alerts)
    }), 200


# ---------------------------------------------------------------------------
# 6. Phase 10J: Reliable Multi-Channel Demo & Email/SMS Verification APIs
# ---------------------------------------------------------------------------
# Simple In-Memory Rate Limiter (CP14)
DEMO_RATE_LIMITS: Dict[str, List[float]] = {}
RATE_LIMIT_MAX_PER_MINUTE = 20

def check_demo_rate_limit(client_ip: str) -> bool:
    now = time.time()
    timestamps = DEMO_RATE_LIMITS.setdefault(client_ip, [])
    # Filter out timestamps older than 60 seconds
    timestamps = [t for t in timestamps if now - t < 60.0]
    DEMO_RATE_LIMITS[client_ip] = timestamps
    if len(timestamps) >= RATE_LIMIT_MAX_PER_MINUTE:
        return False
    timestamps.append(now)
    return True


@notifications_bp.route("/api/notifications/demo/send-test", methods=["POST"])
def send_test_notification():
    """
    POST /api/notifications/demo/send-test
    Input:
      recipient: email address or telephone number
      email: optional explicit email
      phone: optional explicit phone
      channel: 'AUTO' | 'EMAIL' | 'SMS'
      recipient_name: optional
      language: 'en' | 'hi' | 'ne' | 'as' | 'bh' | 'lp'
      alert_type: 'TEST_ALERT' | ...
      corridor: optional corridor string
      scenario: optional scenario ID
    """
    client_ip = request.remote_addr or "127.0.0.1"
    if not check_demo_rate_limit(client_ip):
        return jsonify({
            "success": False,
            "status": "RATE_LIMITED",
            "error": "Rate limit exceeded. Maximum 20 demo dispatches per minute."
        }), 429

    try:
        from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE
        body = request.get_json(force=True, silent=True) or {}
        recipient = body.get("recipient")
        email = body.get("email") or (recipient if recipient and "@" in str(recipient) else None)
        phone = body.get("phone") or (recipient if recipient and "@" not in str(recipient) else None)
        channel = body.get("channel", "AUTO")
        recipient_name = body.get("recipient_name")
        language = body.get("language", "en")
        alert_type = body.get("alert_type", "TEST_ALERT")
        corridor = body.get("corridor") or body.get("scenario") or "NH-10 (Sikkim Lifeline KM 48)"

        # If both email and phone provided, run dual channel dispatch
        if email and phone:
            result = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
                email_address=email,
                phone_number=phone,
                recipient_name=recipient_name,
                language=language,
                scenario_id=corridor,
                actor="EOC_WEB_DEMO_OPERATOR"
            )
            return jsonify(result), 200 if result.get("success", False) else 400

        # Fallback to single channel auto-detection
        target_recip = recipient or email or phone
        if not target_recip:
            return jsonify({
                "success": False,
                "status": "FAILED",
                "error": "Missing recipient. Enter an email address, telephone number, or both."
            }), 400

        result = UNIFIED_NOTIFICATION_SERVICE.dispatch_test_notification(
            recipient=target_recip,
            channel=channel,
            recipient_name=recipient_name,
            language=language,
            alert_type=alert_type,
            corridor=corridor,
            actor="EOC_WEB_DEMO_OPERATOR"
        )

        status_code = 200 if result.get("success", False) else 400
        return jsonify(result), status_code

    except Exception as exc:
        logger.error(f"[Notifications] Error in send_test_notification: {exc}")
        return jsonify({
            "success": False,
            "status": "FAILED",
            "error": str(exc)
        }), 500


@notifications_bp.route("/api/notifications/demo/run-scenario-and-send", methods=["POST"])
def run_scenario_and_send():
    """
    POST /api/notifications/demo/run-scenario-and-send
    CP02 & CP03: Executes scenario and queues dispatches to BOTH Email and SMS independently.
    Input:
      email: email address
      phone: phone number
      recipient_name: optional
      language: 'en' | 'hi' | 'ne' | 'as' | 'bh' | 'lp'
      scenario: 'ML-SONAPUR-01' | 'SK-NH10-KM48' | 'MZ-HUNTHAR-01' | 'MN-TUPUL-01'
      idempotency_key: optional key
    """
    client_ip = request.remote_addr or "127.0.0.1"
    if not check_demo_rate_limit(client_ip):
        return jsonify({
            "success": False,
            "status": "RATE_LIMITED",
            "error": "Rate limit exceeded. Maximum 20 demo dispatches per minute."
        }), 429

    try:
        from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE
        body = request.get_json(force=True, silent=True) or {}
        email = body.get("email")
        phone = body.get("phone")
        recipient_name = body.get("recipient_name")
        language = body.get("language", "en")
        scenario = body.get("scenario", "ML-SONAPUR-01")
        idempotency_key = body.get("idempotency_key")
        force_real_email = bool(body.get("force_real_email", False))
        force_real_sms = bool(body.get("force_real_sms", False))

        if not email and not phone:
            return jsonify({
                "success": False,
                "status": "FAILED",
                "error": "At least one recipient (Email or Phone) is required to run scenario and send."
            }), 400

        result = UNIFIED_NOTIFICATION_SERVICE.dispatch_dual_test_notification(
            email_address=email,
            phone_number=phone,
            recipient_name=recipient_name,
            language=language,
            scenario_id=scenario,
            actor="EOC_JUDGE_DEMO_OPERATOR",
            is_test=True,
            idempotency_key=idempotency_key,
            force_real_email=force_real_email,
            force_real_sms=force_real_sms
        )

        status_code = 200 if result.get("success", False) else 400
        return jsonify(result), status_code

    except Exception as exc:
        logger.error(f"[Notifications] Error in run_scenario_and_send: {exc}")
        return jsonify({
            "success": False,
            "status": "FAILED",
            "error": str(exc)
        }), 500


@notifications_bp.route("/api/notifications/demo/journal", methods=["GET"])
def get_demo_journal():
    """
    GET /api/notifications/demo/journal
    Returns recent tamper-evident audit journal records.
    """
    try:
        from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE
        limit = int(request.args.get("limit", 25))
        incident_id = request.args.get("incident_id")
        entries = UNIFIED_NOTIFICATION_SERVICE.journal.list_entries(limit=limit, incident_id=incident_id)
        return jsonify({
            "status": "SUCCESS",
            "count": len(entries),
            "journal": entries
        }), 200
    except Exception as exc:
        logger.error(f"[Notifications] Error fetching journal: {exc}")
        return jsonify({
            "status": "ERROR",
            "message": str(exc)
        }), 500


@notifications_bp.route("/api/notifications/providers/status", methods=["GET"])
def get_providers_status():
    """
    GET /api/notifications/providers/status
    Reports status of all 7 alert channels: SMS, Email, Push, CAP, Cell Broadcast, Siren.
    """
    try:
        from services.unified_notification_service import UNIFIED_NOTIFICATION_SERVICE
        status_data = UNIFIED_NOTIFICATION_SERVICE.get_channels_status()
        return jsonify({
            "status": "SUCCESS",
            "data": status_data
        }), 200
    except Exception as exc:
        logger.error(f"[Notifications] Error fetching providers status: {exc}")
        return jsonify({
            "status": "ERROR",
            "message": str(exc)
        }), 500


def register_notification_routes(flask_app) -> None:
    """Registers notifications blueprint into main Flask application."""
    flask_app.register_blueprint(notifications_bp)
    logger.info("[Notifications] Registered Notification Center blueprint & APIs.")
