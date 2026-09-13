# -*- coding: utf-8 -*-
"""
backend/realtime_routes.py
==========================
PARVAT NETRA • Real-Time CRI Dataset & Dynamic Evaluation REST Blueprint
-------------------------------------------------------------------------
Endpoints:
  - GET  /api/pahad/realtime-cri             : Returns latest filed real-time CRI dataset and metadata
  - POST /api/pahad/realtime-cri/refresh     : Triggers live API ingestion, re-computes CRI, files to disk
  - GET  /api/pahad/realtime-cri/download    : Downloads filed realtime_cri_dataset.csv or .json
  - GET  /api/pahad/realtime-cri/sector/<id> : Returns live real-time CRI evaluation for a specific corridor

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import logging
from flask import Blueprint, jsonify, request, send_file
from services.realtime_cri_service import REALTIME_CRI_SERVICE

logger = logging.getLogger("REALTIME_ROUTES")

realtime_bp = Blueprint("realtime_cri", __name__)


@realtime_bp.route("/api/pahad/realtime-cri", methods=["GET"])
def get_realtime_cri():
    """
    Returns the current filed real-time CRI dataset across all monitored corridors,
    including provenance breakdown and SHA-256 data hash.
    """
    try:
        data = REALTIME_CRI_SERVICE.get_latest_dataset()
        return jsonify(data), 200
    except Exception as exc:
        logger.error(f"Error fetching realtime CRI dataset: {exc}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(exc)}), 500


@realtime_bp.route("/api/pahad/realtime-cri/refresh", methods=["POST"])
def refresh_realtime_cri():
    """
    Triggers an immediate on-demand real-time ingestion from Open-Meteo, USGS,
    and in-situ telemetry, re-computes CRI across all sectors, and files the
    updated datasets into CSV and JSON.
    """
    try:
        result = REALTIME_CRI_SERVICE.refresh_and_file_dataset()
        status_code = 200 if result.get("status") == "SUCCESS" else 500
        return jsonify(result), status_code
    except Exception as exc:
        logger.error(f"Error refreshing realtime CRI dataset: {exc}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(exc)}), 500


@realtime_bp.route("/api/pahad/realtime-cri/sector/<sector_id>", methods=["GET"])
def get_sector_realtime_cri(sector_id: str):
    """
    Returns the real-time multi-modal features and computed CRI for a specific sector.
    """
    try:
        rec = REALTIME_CRI_SERVICE.get_sector_record(sector_id)
        if not rec:
            return jsonify({"status": "NOT_FOUND", "message": f"Sector {sector_id} not found"}), 404
        return jsonify({"status": "SUCCESS", "record": rec}), 200
    except Exception as exc:
        logger.error(f"Error evaluating sector {sector_id}: {exc}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(exc)}), 500


@realtime_bp.route("/api/pahad/realtime-cri/download", methods=["GET"])
def download_realtime_cri():
    """
    Direct file download of the filed real-time dataset.
    Query param ?format=csv (default) or ?format=json
    """
    fmt = request.args.get("format", "csv").lower()
    if fmt == "json":
        target = REALTIME_CRI_SERVICE.json_path
        mime = "application/json"
        filename = "realtime_cri_dataset.json"
    else:
        target = REALTIME_CRI_SERVICE.csv_path
        mime = "text/csv"
        filename = "realtime_cri_dataset.csv"

    if not os.path.exists(target):
        # Generate if file does not exist yet
        REALTIME_CRI_SERVICE.refresh_and_file_dataset()

    if not os.path.exists(target):
        return jsonify({"status": "NOT_FOUND", "message": "Dataset file not generated"}), 404

    return send_file(
        target,
        mimetype=mime,
        as_attachment=True,
        download_name=filename
    )
