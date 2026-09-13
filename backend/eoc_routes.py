# -*- coding: utf-8 -*-
"""
backend/eoc_routes.py
=====================
PARVAT NETRA — PAHAD AI — EOC Command & Operations REST API Blueprint
---------------------------------------------------------------------
Phase 8 EOC REST endpoints:
  - Incident queue & lifecycle state machine
  - 15 km geodesic safety geofencing & exposure
  - Subscription registry (Web, Mobile, SMS, Edge)
  - Multi-channel notification dispatch & [SIMULATED SMS]
  - Recipient safety acknowledgements
  - Operational SITREP & Executive Command Brief
  - Cryptographically signed siren commands & replay checks
  - E2E & Failure drill runners
"""

from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify

from engine.eoc_incident_manager import EOC_INCIDENT_MANAGER
from services.eoc_service import EOC_SERVICE

logger = logging.getLogger("EOC_ROUTES")
eoc_bp = Blueprint("eoc_bp", __name__, url_prefix="/api/eoc")


@eoc_bp.route("/incidents", methods=["GET"])
def list_incidents():
    """List prioritized EOC incidents."""
    status = request.args.get("status")
    sector_id = request.args.get("sector_id")
    limit = int(request.args.get("limit", 50))
    incidents = EOC_INCIDENT_MANAGER.list_incidents(status=status, sector_id=sector_id, limit=limit)
    return jsonify({
        "status": "SUCCESS",
        "total": len(incidents),
        "incidents": incidents
    })


@eoc_bp.route("/incidents", methods=["POST"])
def create_incident():
    """Create a persistent EOC incident."""
    data = request.get_json(force=True) or {}
    sector_id = data.get("sector_id", "SK-NH10-KM48")
    risk_score = float(data.get("risk_score", 75.0))
    risk_band = data.get("risk_band", "HIGH")
    model_probability = float(data.get("model_probability", 0.80))
    fos = float(data.get("FoS", 1.02))
    rainfall = float(data.get("rainfall", 160.0))

    incident = EOC_INCIDENT_MANAGER.create_incident(
        sector_id=sector_id,
        risk_score=risk_score,
        risk_band=risk_band,
        model_probability=model_probability,
        FoS=fos,
        rainfall=rainfall,
        seismic_state=data.get("seismic_state", "QUIET"),
        sensor_state=data.get("sensor_state", "HEALTHY"),
        signal_agreement=data.get("signal_agreement", "2-of-3 Corroborated"),
        data_quality=float(data.get("data_quality", 0.95)),
        provenance=data.get("provenance", "[SIMULATED]"),
        recommended_action=data.get("recommended_action", "INSPECT"),
        assigned_authority=data.get("assigned_authority", "DISTRICT_MAGISTRATE_PAKYONG"),
        assigned_field_team=data.get("assigned_field_team", "BRO_TASK_FORCE_KM48"),
        geofence_radius=float(data.get("geofence_radius", 15.0)),
        description=data.get("description", ""),
        latitude=float(data.get("latitude", 27.3300)),
        longitude=float(data.get("longitude", 88.6100)),
        population_at_risk=int(data.get("population_at_risk", 4200)),
        road_criticality=float(data.get("road_criticality", 95.0)),
        corridor_name=data.get("corridor_name", "NH-10 (Sikkim Lifeline KM 48)")
    )
    return jsonify({
        "status": "CREATED",
        "incident": incident.to_dict()
    }), 201


@eoc_bp.route("/incidents/<incident_id>", methods=["GET"])
def get_incident(incident_id: str):
    """Retrieve detailed incident entity with display projections."""
    incident = EOC_INCIDENT_MANAGER.get_incident(incident_id)
    if not incident:
        return jsonify({"status": "ERROR", "error": "Incident not found"}), 404
    return jsonify({
        "status": "SUCCESS",
        "incident": incident.to_dict()
    })


@eoc_bp.route("/incidents/<incident_id>/transition", methods=["POST"])
def transition_incident(incident_id: str):
    """Advance or update lifecycle state of an incident."""
    data = request.get_json(force=True) or {}
    target_state = data.get("target_state")
    actor_role = data.get("actor_role", "EOC_OPERATOR")
    actor_id = data.get("actor_id", "OPERATOR_01")
    note = data.get("note", "")
    force = bool(data.get("force", False))

    if not target_state:
        return jsonify({"status": "ERROR", "error": "target_state is required"}), 400

    ok, msg, inc = EOC_INCIDENT_MANAGER.transition_state(
        incident_id=incident_id,
        target_state=target_state,
        actor_role=actor_role,
        actor_id=actor_id,
        note=note,
        force=force
    )
    if not ok:
        return jsonify({"status": "REJECTED", "error": msg}), 400

    return jsonify({
        "status": "TRANSITIONED",
        "message": msg,
        "incident": inc.to_dict() if inc else None
    })


@eoc_bp.route("/incidents/<incident_id>/geofence", methods=["GET"])
def get_incident_geofence(incident_id: str):
    """Calculate 15 km geodesic safety geofence and exposure."""
    incident = EOC_INCIDENT_MANAGER.get_incident(incident_id)
    if not incident:
        return jsonify({"status": "ERROR", "error": "Incident not found"}), 404

    geo_data = EOC_SERVICE.calculate_15km_geofence(
        center_lat=incident.latitude,
        center_lon=incident.longitude,
        radius_km=incident.geofence_radius
    )
    return jsonify({
        "status": "SUCCESS",
        "incident_id": incident_id,
        "geofence": geo_data
    })


@eoc_bp.route("/subscriptions", methods=["POST"])
def register_subscription():
    """Register device or user early-warning subscription."""
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    device_id = data.get("device_id")
    platform = data.get("platform", "WEB_PUSH")
    endpoint = data.get("notification_endpoint", "https://push.browser.example/sub1")
    language = data.get("language", "en")
    lat = float(data.get("latitude", 27.3300))
    lon = float(data.get("longitude", 88.6100))
    consent = data.get("consent_state", "CONSENTED")
    role = data.get("role", "PUBLIC")

    if not user_id or not device_id:
        return jsonify({"status": "ERROR", "error": "user_id and device_id are required"}), 400

    res = EOC_SERVICE.register_subscription(
        user_id=user_id,
        device_id=device_id,
        platform=platform,
        notification_endpoint=endpoint,
        language=language,
        latitude=lat,
        longitude=lon,
        consent_state=consent,
        role=role
    )
    return jsonify(res), 201


@eoc_bp.route("/incidents/<incident_id>/dispatch", methods=["POST"])
def dispatch_notifications(incident_id: str):
    """Dispatch multi-channel notifications for authorized incident."""
    data = request.get_json(force=True) or {}
    token = data.get("authorization_token", "")
    channels = data.get("channels")
    test_mode = bool(data.get("test_mode", True))

    res = EOC_SERVICE.dispatch_incident_notifications(
        incident_id=incident_id,
        authorization_token=token,
        channels=channels,
        test_mode=test_mode
    )
    if res.get("status") == "BLOCKED":
        return jsonify(res), 403
    return jsonify(res)


@eoc_bp.route("/acknowledge", methods=["POST"])
def record_acknowledgement():
    """Record citizen or responder safety acknowledgement."""
    data = request.get_json(force=True) or {}
    incident_id = data.get("incident_id")
    user_id = data.get("user_id")
    device_id = data.get("device_id")
    ack_type = data.get("ack_type", "SAFE")
    lat = data.get("latitude")
    lon = data.get("longitude")
    note = data.get("note", "")

    if not incident_id or not user_id or not device_id:
        return jsonify({"status": "ERROR", "error": "incident_id, user_id, device_id required"}), 400

    res = EOC_SERVICE.record_acknowledgement(
        incident_id=incident_id,
        user_id=user_id,
        device_id=device_id,
        ack_type=ack_type,
        latitude=lat,
        longitude=lon,
        note=note
    )
    return jsonify(res), 200


@eoc_bp.route("/incidents/<incident_id>/acknowledgements", methods=["GET"])
def get_acknowledgements(incident_id: str):
    """Get aggregated privacy-preserving acknowledgement stats."""
    stats = EOC_SERVICE.get_acknowledgement_stats(incident_id)
    return jsonify({
        "status": "SUCCESS",
        "incident_id": incident_id,
        "statistics": stats
    })


@eoc_bp.route("/sitrep/<incident_id>", methods=["GET"])
def get_sitrep(incident_id: str):
    """Generate 15-section structured operational SITREP."""
    sitrep = EOC_SERVICE.generate_sitrep(incident_id)
    if "error" in sitrep:
        return jsonify({"status": "ERROR", "error": sitrep["error"]}), 404
    return jsonify(sitrep)


@eoc_bp.route("/command-brief", methods=["GET"])
def get_command_brief():
    """One-screen executive briefing data."""
    incident_id = request.args.get("incident_id")
    brief = EOC_SERVICE.generate_command_brief(incident_id)
    return jsonify({
        "status": "SUCCESS",
        "brief": brief
    })


@eoc_bp.route("/all-clear", methods=["POST"])
def authorize_all_clear():
    """Execute multi-gate All-Clear protocol."""
    data = request.get_json(force=True) or {}
    incident_id = data.get("incident_id")
    role = data.get("approver_role", "DISTRICT_AUTHORITY")
    approver = data.get("approver_id", "DM_PAKYONG")
    field_confirmed = bool(data.get("field_clearance_confirmed", False))
    fos = float(data.get("current_fos", 1.35))
    rain = float(data.get("current_rain_mm", 10.0))
    justification = data.get("justification", "Slope stabilized")

    if not incident_id:
        return jsonify({"status": "ERROR", "error": "incident_id required"}), 400

    res = EOC_SERVICE.authorize_all_clear(
        incident_id=incident_id,
        approver_role=role,
        approver_id=approver,
        field_clearance_confirmed=field_confirmed,
        current_fos=fos,
        current_rain_mm=rain,
        justification=justification
    )
    if res.get("status") == "REJECTED":
        return jsonify(res), 400
    return jsonify(res)


@eoc_bp.route("/siren/sign-command", methods=["POST"])
def sign_siren_command():
    """Generate cryptographically signed siren command."""
    data = request.get_json(force=True) or {}
    incident_id = data.get("incident_id", "INC-TEST-001")
    target = data.get("target", "SIREN_NH10_KM48_RELAY")
    auth = data.get("authorization", "AUTH_TOKEN_TEST")
    res = EOC_SERVICE.generate_signed_siren_command(incident_id, target, auth)
    return jsonify(res)


@eoc_bp.route("/siren/verify-command", methods=["POST"])
def verify_siren_command():
    """Verify and simulate siren command with replay check."""
    payload = request.get_json(force=True) or {}
    ok, msg = EOC_SERVICE.verify_and_execute_siren_command(payload)
    if not ok:
        return jsonify({"status": "REJECTED", "error": msg}), 400
    return jsonify({"status": "VERIFIED_AND_SIMULATED", "message": msg})


@eoc_bp.route("/drill/e2e", methods=["POST"])
def run_e2e_drill():
    """Execute end-to-end 20-stage EOC drill."""
    res = EOC_SERVICE.run_end_to_end_drill()
    return jsonify(res)


@eoc_bp.route("/drill/failure", methods=["POST"])
def run_failure_drill():
    """Execute fail-closed resilience drill."""
    res = EOC_SERVICE.run_failure_drill()
    return jsonify(res)
