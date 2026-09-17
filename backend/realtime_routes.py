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


def dataset_to_geojson(data: dict) -> dict:
    """
    Converts real-time CRI records into standard WGS84 GeoJSON FeatureCollection
    with full authoritative data classes and provenance metadata.
    """
    records = data.get("records", [])
    features = []
    highest_cri = -1.0
    highest_band = "LOW"
    highest_sec = None

    band_order = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "VERY_HIGH": 4, "EXTREME": 5}

    for rec in records:
        lat = float(rec.get("latitude", 0.0))
        lon = float(rec.get("longitude", 0.0))
        cri = float(rec.get("final_cri", rec.get("raw_cri", 0.0)))
        band = str(rec.get("alert_band", "LOW")).upper()

        if cri > highest_cri:
            highest_cri = cri
            highest_sec = rec.get("sector_name")
            highest_band = band

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "sector_id": rec.get("sector_id"),
                "sector_name": rec.get("sector_name"),
                "corridor": rec.get("corridor"),
                "state": rec.get("state"),
                "district": rec.get("district"),
                "cri": round(cri, 2),
                "raw_cri": round(float(rec.get("raw_cri", cri)), 2),
                "risk_band": band,
                "alert_band": band,
                "physical_fos": round(float(rec.get("physical_fos", 1.0)), 3),
                "rainfall_24h_mm": round(float(rec.get("rainfall_24h_mm", 0.0)), 1),
                "rainfall_current_mmh": round(float(rec.get("rainfall_current_mmh", 0.0)), 2),
                "ecmwf_24h_mm": round(float(rec.get("ecmwf_24h_mm", 0.0)), 1),
                "gfs_24h_mm": round(float(rec.get("gfs_24h_mm", 0.0)), 1),
                "icon_24h_mm": round(float(rec.get("icon_24h_mm", 0.0)), 1),
                "ensemble_mean_24h_mm": round(float(rec.get("ensemble_mean_24h_mm", rec.get("rainfall_24h_mm", 0.0))), 1),
                "rainfall_source": rec.get("weather_source", "Open-Meteo Multi-Model Ensemble"),
                "rainfall_class": "LIVE_EXTERNAL",
                "seismic_magnitude": float(rec.get("seismic_magnitude", 0.0)),
                "seismic_distance_km": float(rec.get("seismic_distance_km", 0.0)),
                "seismic_source": "USGS Earthquake Hazards Program",
                "seismic_class": "LIVE_EXTERNAL",
                "ncs_status": "AUTH_REQUIRED",
                "insar_deformation_mm": float(rec.get("insar_deformation_mm", 0.0)),
                "insar_class": "HISTORICAL",
                "pore_water_pressure_kpa": float(rec.get("pore_water_pressure_kpa", 0.0)),
                "soil_moisture_vwc": float(rec.get("soil_moisture_vwc", 0.0)),
                "sensor_class": "SIMULATED",
                "sensor_note": "Physical deployment not verified",
                "event_probability": round(float(rec.get("event_probability_24h", 0.0)), 3),
                "model_class": "MODEL_PRETRAINED",
                "model_status": "TRAINED_LIMITED_DATA",
                "cri_class": "DERIVED",
                "live_contribution": "PARTIAL",
                "signals_triggered": rec.get("model_agreement", "2/3"),
                "evidence_confidence": float(rec.get("evidence_confidence", 0.81)),
                "data_quality": "HIGH",
                "timestamp": rec.get("timestamp"),
                "data_hash_sha256": rec.get("data_hash_sha256", "")
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "metadata": {
            "title": "PARVAT NETRA • Current Risk Zones (NER Sentinel)",
            "generated_at": data.get("generated_at"),
            "dataset_class": "CACHED_LIVE",
            "record_count": len(features),
            "live_sources_count": 2,
            "live_sources": ["Open-Meteo REST API (Weather)", "USGS GeoJSON (Seismic)"],
            "simulated_sources": ["van Genuchten SWCC Unsaturated In-Situ Telemetry"],
            "highest_risk_band": highest_band,
            "highest_risk_cri": round(highest_cri, 2),
            "highest_risk_corridor": highest_sec,
            "band_summary": data.get("band_summary", {}),
            "sha256_hash": data.get("data_hash_sha256", "")
        },
        "features": features
    }


@realtime_bp.route("/api/pahad/realtime-cri", methods=["GET"])
def get_realtime_cri():
    """
    Returns the current filed real-time CRI dataset across all monitored corridors,
    including provenance breakdown and SHA-256 data hash.
    Supports ?format=geojson for native GIS ingestion.
    """
    try:
        data = REALTIME_CRI_SERVICE.get_latest_dataset()
        fmt = request.args.get("format", "").lower()
        if fmt == "geojson":
            return jsonify(dataset_to_geojson(data)), 200
        return jsonify(data), 200
    except Exception as exc:
        logger.error(f"Error fetching realtime CRI dataset: {exc}", exc_info=True)
        return jsonify({"status": "ERROR", "message": str(exc)}), 500


@realtime_bp.route("/api/pahad/realtime-cri/geojson", methods=["GET"])
def get_realtime_cri_geojson():
    """
    Standard GeoJSON FeatureCollection endpoint serving current evaluated risk zones
    across all 8 North-Eastern Region states with full authoritative data classes.
    """
    try:
        data = REALTIME_CRI_SERVICE.get_latest_dataset()
        return jsonify(dataset_to_geojson(data)), 200
    except Exception as exc:
        logger.error(f"Error serving realtime CRI GeoJSON: {exc}", exc_info=True)
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
