# -*- coding: utf-8 -*-
"""
services/isro_bhuvan_service.py
================================
PARVAT NETRA - ISRO/NRSC Bhuvan Earth Observation Service
Integrates real Indian satellite data from ISRO/NRSC Bhuvan portal.
Provenance: [ISRO/NRSC] live, [CACHED] offline fallback.
Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""
from __future__ import annotations
import os, time, logging, hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("PAHAD_ISRO_BHUVAN")

BHUVAN_WMS_BASE = "https://bhuvan-app3.nrsc.gov.in/bhuvan/wms"
BHUVAN_VEC2_BASE = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/wms"
BHUVAN_PROBE_URL = "https://bhuvan-app3.nrsc.gov.in/bhuvan/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities"
BHUVAN_TIMEOUT_S = 8

BHUVAN_LAYERS: Dict[str, Dict[str, Any]] = {
    "landslide_hazard": {
        "display_name": "Landslide Hazard Zones",
        "wms_layer": "bhuvan:India_Landslide_Hazard",
        "wms_base": BHUVAN_WMS_BASE,
        "format": "image/png",
        "transparent": True,
        "opacity": 0.65,
        "description": "NRSC Landslide Hazard Zonation - NDMS Programme",
        "provenance": "[ISRO/NRSC]",
        "source_url": "https://bhuvan.nrsc.gov.in/disaster/",
        "color_hint": "#dc2626",
        "srs": "EPSG:4326",
        "version": "1.1.1",
    },
    "landslide_susceptibility": {
        "display_name": "Landslide Susceptibility (NESAC)",
        "wms_layer": "nesac:NER_Landslide_Susceptibility",
        "wms_base": BHUVAN_WMS_BASE,
        "format": "image/png",
        "transparent": True,
        "opacity": 0.55,
        "description": "NESAC NER Landslide Susceptibility Mapping under NERDRR programme",
        "provenance": "[ISRO/NESAC]",
        "source_url": "https://nerdrr.gov.in/",
        "color_hint": "#f97316",
        "srs": "EPSG:4326",
        "version": "1.1.1",
    },
    "bhuvan_satellite": {
        "display_name": "Bhuvan Satellite Imagery",
        "wms_layer": "bhuvan:RESOURCESAT2_LISS3",
        "wms_base": BHUVAN_VEC2_BASE,
        "format": "image/jpeg",
        "transparent": False,
        "opacity": 1.0,
        "description": "RESOURCESAT-2/2A LISS-III 24m resolution Indian satellite imagery",
        "provenance": "[ISRO/NRSC]",
        "source_url": "https://bhuvan.nrsc.gov.in/",
        "color_hint": "#38bdf8",
        "srs": "EPSG:4326",
        "version": "1.1.1",
    },
}

_is_vercel = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
TILE_CACHE_DIR = "/tmp/bhuvan_cache" if _is_vercel else "data/bhuvan_cache"
try:
    os.makedirs(TILE_CACHE_DIR, exist_ok=True)
except OSError:
    TILE_CACHE_DIR = "/tmp/bhuvan_cache"
    try:
        os.makedirs(TILE_CACHE_DIR, exist_ok=True)
    except OSError:
        TILE_CACHE_DIR = None

_status_cache: Dict[str, Any] = {
    "online": None, "latency_ms": None, "last_checked": None,
    "error": None, "capabilities_snippet": None,
}
_STATUS_TTL_S = 120


def probe_bhuvan_wms(force: bool = False) -> Dict[str, Any]:
    """Check if ISRO Bhuvan WMS is reachable. Returns status dict."""
    global _status_cache
    now = time.time()
    if (not force and _status_cache["last_checked"] is not None
            and (now - _status_cache["last_checked"]) < _STATUS_TTL_S):
        return dict(_status_cache)
    try:
        import requests
        t0 = time.time()
        resp = requests.get(BHUVAN_PROBE_URL, timeout=BHUVAN_TIMEOUT_S,
                            headers={"User-Agent": "PARVAT-NETRA/SIH26001"},
                            allow_redirects=True)
        latency_ms = int((time.time() - t0) * 1000)
        if resp.status_code == 200:
            online = ("WMT_MS_Capabilities" in resp.text or "WMS_Capabilities" in resp.text
                      or "<Service>" in resp.text)
            _status_cache.update({
                "online": online, "latency_ms": latency_ms,
                "last_checked": now, "error": None,
                "capabilities_snippet": resp.text[:200],
            })
        else:
            _status_cache.update({
                "online": False, "latency_ms": latency_ms,
                "last_checked": now, "error": f"HTTP {resp.status_code}",
                "capabilities_snippet": None,
            })
    except Exception as exc:
        _status_cache.update({
            "online": False, "latency_ms": None, "last_checked": now,
            "error": str(exc)[:200], "capabilities_snippet": None,
        })
        logger.warning("Bhuvan WMS probe failed: %s", exc)
    return dict(_status_cache)


def get_service_status() -> Dict[str, Any]:
    """Return Bhuvan WMS service status for API endpoint."""
    status = probe_bhuvan_wms()
    return {
        "service": "ISRO/NRSC Bhuvan WMS",
        "online": status.get("online"),
        "latency_ms": status.get("latency_ms"),
        "last_checked_utc": (
            datetime.fromtimestamp(status["last_checked"], tz=timezone.utc).isoformat()
            if status.get("last_checked") else None
        ),
        "error": status.get("error"),
        "wms_base_url": BHUVAN_WMS_BASE,
        "provenance": "[ISRO/NRSC]",
        "layers_available": list(BHUVAN_LAYERS.keys()),
        "data_source": "bhuvan.nrsc.gov.in",
        "attribution": "Copyright ISRO/NRSC Bhuvan National Geoportal",
    }


def get_layers_metadata() -> list:
    """Return display metadata for all registered ISRO layers."""
    result = []
    for layer_id, cfg in BHUVAN_LAYERS.items():
        result.append({
            "layer_id": layer_id,
            "display_name": cfg["display_name"],
            "description": cfg["description"],
            "provenance": cfg["provenance"],
            "color_hint": cfg["color_hint"],
            "opacity": cfg["opacity"],
            "transparent": cfg["transparent"],
            "source_url": cfg["source_url"],
            "wms_proxy_url": f"/api/isro/wms-proxy?layer={layer_id}",
        })
    return result


def build_wms_request_url(layer_id: str, params: Dict[str, str]) -> Optional[str]:
    """Build the upstream Bhuvan WMS URL for a given layer and GetMap params."""
    cfg = BHUVAN_LAYERS.get(layer_id)
    if not cfg:
        return None
    import urllib.parse
    wms_params = {
        "SERVICE": "WMS",
        "VERSION": cfg.get("version", "1.1.1"),
        "REQUEST": "GetMap",
        "LAYERS": cfg["wms_layer"],
        "STYLES": "",
        "FORMAT": params.get("FORMAT", cfg["format"]),
        "TRANSPARENT": "TRUE" if cfg["transparent"] else "FALSE",
        "SRS": params.get("SRS", cfg.get("srs", "EPSG:4326")),
        "BBOX": params.get("BBOX", ""),
        "WIDTH": params.get("WIDTH", "256"),
        "HEIGHT": params.get("HEIGHT", "256"),
    }
    return f"{cfg['wms_base']}?{urllib.parse.urlencode(wms_params)}"


def fetch_wms_tile(layer_id: str, params: Dict[str, str]) -> Tuple[Optional[bytes], str, bool]:
    """Fetch a WMS tile from Bhuvan. Returns (bytes, content_type, from_cache)."""
    cfg = BHUVAN_LAYERS.get(layer_id)
    if not cfg:
        return _transparent_tile(), "image/png", False
    bbox = params.get("BBOX", "")
    width = params.get("WIDTH", "256")
    height = params.get("HEIGHT", "256")
    cache_key = hashlib.md5(f"{layer_id}:{bbox}{width}{height}".encode()).hexdigest()
    cache_path = os.path.join(TILE_CACHE_DIR, f"{cache_key}.tile") if TILE_CACHE_DIR else None
    if cache_path and os.path.exists(cache_path):
        age_s = time.time() - os.path.getmtime(cache_path)
        if age_s < 21600:
            try:
                with open(cache_path, "rb") as f:
                    data = f.read()
                if data:
                    ct = "image/jpeg" if layer_id == "bhuvan_satellite" else "image/png"
                    return data, ct, True
            except OSError:
                pass
    upstream_url = build_wms_request_url(layer_id, params)
    if not upstream_url:
        return _transparent_tile(), "image/png", False
    try:
        import requests
        resp = requests.get(upstream_url, timeout=BHUVAN_TIMEOUT_S,
                            headers={"User-Agent": "PARVAT-NETRA/SIH26001"})
        if resp.status_code == 200 and resp.content:
            if cache_path:
                try:
                    with open(cache_path, "wb") as f:
                        f.write(resp.content)
                except OSError:
                    pass
            ct = resp.headers.get("Content-Type", "image/png").split(";")[0]
            return resp.content, ct, False
        logger.warning("Bhuvan tile HTTP %s for layer %s", resp.status_code, layer_id)
        return _transparent_tile(), "image/png", False
    except Exception as exc:
        logger.warning("Bhuvan tile fetch error for %s: %s", layer_id, exc)
        return _transparent_tile(), "image/png", False


def _transparent_tile() -> bytes:
    """Return a minimal 1x1 transparent PNG as fallback tile."""
    return bytes([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
        0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4,
        0x89, 0x00, 0x00, 0x00, 0x0b, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9c, 0x62, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae,
        0x42, 0x60, 0x82,
    ])
