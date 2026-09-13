"""
engine/pahad_crowd.py
=====================
PAHAD Phase 2 — Crowd Corroboration & Trust Tiering
-----------------------------------------------------
Trust tiers:
  OFFICIAL (GSI, BRO, SDMA, PWD) : weight = 1.00
  CITIZEN  (Public, Spotter)      : weight = 0.50

Confidence thresholds:
  >= 1.0          -> CORROBORATED_CRITICAL
  0.5 <= x < 1.0  -> COMMUNITY_REPORTED
  < 0.5           -> UNVERIFIED

Data : [SIMULATED]
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

TRUST_WEIGHTS: Dict[str, float] = {
    "GSI": 1.00, "BRO": 1.00, "SDMA": 1.00, "PWD": 1.00, "OFFICIAL": 1.00,
    "CITIZEN": 0.50, "PUBLIC": 0.50, "LOCAL_SPOTTER": 0.50, "COMMUNITY": 0.50,
}
_DEFAULT_WEIGHT: float = 0.50
_CLUSTER_RADIUS_KM: float = 0.5
_CLUSTER_TIME_WINDOW_S: int = 7200


@dataclass
class IncidentReport:
    report_id: str
    lat: float
    lon: float
    timestamp_epoch: float
    source_type: str
    description: str = ""
    weight: float = field(init=False)

    def __post_init__(self) -> None:
        self.weight = TRUST_WEIGHTS.get(self.source_type.upper(), _DEFAULT_WEIGHT)


@dataclass
class IncidentCluster:
    cluster_id: str
    reports: List[IncidentReport]
    confidence: float
    status: str
    centroid_lat: float
    centroid_lon: float
    earliest_epoch: float
    latest_epoch: float

    def to_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id,
            "status": self.status,
            "confidence": round(self.confidence, 4),
            "report_count": len(self.reports),
            "centroid": {
                "lat": round(self.centroid_lat, 6),
                "lon": round(self.centroid_lon, 6),
            },
            "time_span_seconds": round(self.latest_epoch - self.earliest_epoch, 1),
            "report_ids": [r.report_id for r in self.reports],
            "source_types": list({r.source_type for r in self.reports}),
        }


class CrowdVerificationEngine:
    """Spatiotemporal incident clustering with trust-tiered confidence scoring."""

    def __init__(
        self,
        cluster_radius_km: float = _CLUSTER_RADIUS_KM,
        time_window_s: int = _CLUSTER_TIME_WINDOW_S,
    ) -> None:
        self._radius = cluster_radius_km
        self._tw = time_window_s

    def cluster_and_verify(self, reports: List[Dict[str, Any]]) -> List[dict]:
        """Cluster reports and return corroboration tags."""
        parsed: List[IncidentReport] = []
        for r in reports:
            # Tolerant parsing for lat/latitude and lon/longitude
            lat_val = r.get("lat") if "lat" in r else r.get("latitude")
            lon_val = r.get("lon") if "lon" in r else r.get("longitude")
            if lat_val is None or lon_val is None:
                continue
            try:
                lat_f = float(lat_val)
                lon_f = float(lon_val)
            except (ValueError, TypeError):
                continue

            ts_val = r.get("timestamp_epoch")
            if ts_val is None:
                ts_val = r.get("timestamp") or time.time()
            try:
                ts_f = float(ts_val)
            except (ValueError, TypeError):
                ts_f = time.time()

            parsed.append(IncidentReport(
                report_id=str(r.get("report_id", r.get("id", f"rpt-{len(parsed)}"))),
                lat=lat_f,
                lon=lon_f,
                timestamp_epoch=ts_f,
                source_type=str(r.get("source_type", r.get("source", "CITIZEN"))),
                description=str(r.get("description", "")),
            ))
        clusters = self._greedy_cluster(parsed)
        return [c.to_dict() for c in clusters]

    def _greedy_cluster(self, reports: List[IncidentReport]) -> List[IncidentCluster]:
        assigned = [False] * len(reports)
        clusters: List[IncidentCluster] = []
        cluster_idx = 0

        for i, anchor in enumerate(reports):
            if assigned[i]:
                continue
            members = [anchor]
            assigned[i] = True

            for j, candidate in enumerate(reports):
                if assigned[j] or i == j:
                    continue
                dist = self._haversine(anchor.lat, anchor.lon, candidate.lat, candidate.lon)
                dt = abs(anchor.timestamp_epoch - candidate.timestamp_epoch)
                if dist <= self._radius and dt <= self._tw:
                    members.append(candidate)
                    assigned[j] = True

            confidence = min(sum(m.weight for m in members), 1.0)
            status = self._classify_confidence(confidence)
            lats = [m.lat for m in members]
            lons = [m.lon for m in members]
            times = [m.timestamp_epoch for m in members]

            clusters.append(IncidentCluster(
                cluster_id=f"CLU-{cluster_idx:04d}",
                reports=members,
                confidence=confidence,
                status=status,
                centroid_lat=sum(lats) / len(lats),
                centroid_lon=sum(lons) / len(lons),
                earliest_epoch=min(times),
                latest_epoch=max(times),
            ))
            cluster_idx += 1

        return clusters

    @staticmethod
    def _classify_confidence(confidence: float) -> str:
        if confidence >= 1.0:
            return "CORROBORATED_CRITICAL"
        if confidence >= 0.5:
            return "COMMUNITY_REPORTED"
        return "UNVERIFIED"

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
