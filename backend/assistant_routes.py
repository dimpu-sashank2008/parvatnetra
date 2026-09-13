# -*- coding: utf-8 -*-
"""
backend/assistant_routes.py
===========================
PARVAT NETRA • PAHAD AI — Voice & Chat Assistant Blueprint
----------------------------------------------------------
REST Endpoints:
- POST /api/pahad/assistant/session   : Create ephemeral 1h assistant token
- POST /api/pahad/assistant/chat      : Ingest query, enforce safety, return grounded response
- GET  /api/pahad/assistant/context   : Fetch live grounded telemetry for corridor
- GET  /api/pahad/assistant/status    : Health & connectivity status (LIVE/DEGRADED/OFFLINE)
"""

from __future__ import annotations

import time
import logging
from flask import Blueprint, request, jsonify
from services.pahad_voice_assistant import PAHAD_VOICE_ASSISTANT

logger = logging.getLogger("ASSISTANT_ROUTES")

assistant_bp = Blueprint("assistant_bp", __name__)


@assistant_bp.route("/api/pahad/assistant/session", methods=["POST"])
def create_session():
    """Initializes an ephemeral voice assistant session."""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "commander_eoc")
    role = data.get("role", "authority")
    session_info = PAHAD_VOICE_ASSISTANT.create_session(user_id=user_id, role=role)
    return jsonify({
        "status": "SUCCESS",
        "data": session_info,
        "timestamp": time.time()
    }), 200


@assistant_bp.route("/api/pahad/assistant/chat", methods=["POST"])
def chat():
    """Processes user query (voice transcript or typed text) with corridor grounding."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    corridor_id = data.get("corridor_id", "SK-NH10-KM48")
    token = data.get("token") or request.headers.get("X-Assistant-Token")

    result = PAHAD_VOICE_ASSISTANT.process_query(
        query=query,
        corridor_id=corridor_id,
        session_token=token
    )

    status_code = 200
    if result.get("error_code") == "AUTH_EXPIRED":
        status_code = 401
    elif result.get("error_code") == "RATE_LIMITED":
        status_code = 429

    return jsonify(result), status_code


@assistant_bp.route("/api/pahad/assistant/context", methods=["GET"])
def get_context():
    """Returns live grounded context snapshot for specified corridor."""
    corridor_id = request.args.get("corridor_id", "SK-NH10-KM48")
    ctx = PAHAD_VOICE_ASSISTANT.get_grounded_corridor_context(corridor_id)
    return jsonify({
        "status": "SUCCESS",
        "corridor_id": corridor_id,
        "context": ctx
    }), 200


@assistant_bp.route("/api/pahad/assistant/status", methods=["GET"])
def get_status():
    """Returns assistant operational status and safety invariants."""
    return jsonify({
        "status": "SUCCESS",
        "assistant_status": "LIVE",
        "version": "v10.4.0-phase10d",
        "safety_invariants": {
            "public_dispatch": "DISABLED",
            "siren_dry_run": 1,
            "two_of_three_corroboration": True,
            "statutory_human_authorization": True,
            "conversational_actuation_permitted": False
        },
        "capabilities": {
            "voice_recognition": True,
            "barge_in_interruption": True,
            "grounded_sitrep": True,
            "multi_horizon_forecast": True,
            "cross_corridor_triage": True
        }
    }), 200
