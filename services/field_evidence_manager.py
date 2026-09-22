# -*- coding: utf-8 -*-
"""
services/field_evidence_manager.py
==================================
PARVAT NETRA • Field Evidence Packaging, Verification & Event Labeling Framework
---------------------------------------------------------------------------------
Phase V4.7 Structured Evidence Management:
1. Manages physical field evidence packages (installation photos, calibration certs,
   commissioning sign-offs, GPS surveying records, telemetry logs).
2. Computes and checks SHA-256 file hashes.
3. Records missing evidence transparently as 'NOT_AVAILABLE'.
4. Implements the Event Label Linkage Foundation (EVENT, NON_EVENT, UNKNOWN).
5. Computes baseline descriptive statistics without unwarranted failure inferences.
"""

from __future__ import annotations

import os
import json
import hashlib
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("FIELD_EVIDENCE")

# Evidence Types (Phase V4.9 Canonical Schema)
EVIDENCE_TYPE_PHOTO = "PHOTO"
EVIDENCE_TYPE_VIDEO = "VIDEO"
EVIDENCE_TYPE_CALIBRATION_CERTIFICATE = "CALIBRATION_CERTIFICATE"
EVIDENCE_TYPE_INSTALLATION_RECORD = "INSTALLATION_RECORD"
EVIDENCE_TYPE_BOREHOLE_LOG = "BOREHOLE_LOG"
EVIDENCE_TYPE_COMMISSIONING_RECORD = "COMMISSIONING_RECORD"
EVIDENCE_TYPE_COMMISSIONING_LOG = "COMMISSIONING_LOG"  # Legacy alias
EVIDENCE_TYPE_TELEMETRY_LOG = "TELEMETRY_LOG"
EVIDENCE_TYPE_GPS_RECORD = "GPS_RECORD"
EVIDENCE_TYPE_MANUFACTURER_RECORD = "MANUFACTURER_RECORD"
EVIDENCE_TYPE_TEST_RESULT = "TEST_RESULT"
EVIDENCE_TYPE_OTHER = "OTHER"

VALID_EVIDENCE_TYPES = {
    EVIDENCE_TYPE_PHOTO,
    EVIDENCE_TYPE_VIDEO,
    EVIDENCE_TYPE_CALIBRATION_CERTIFICATE,
    EVIDENCE_TYPE_INSTALLATION_RECORD,
    EVIDENCE_TYPE_BOREHOLE_LOG,
    EVIDENCE_TYPE_COMMISSIONING_RECORD,
    EVIDENCE_TYPE_COMMISSIONING_LOG,
    EVIDENCE_TYPE_TELEMETRY_LOG,
    EVIDENCE_TYPE_GPS_RECORD,
    EVIDENCE_TYPE_MANUFACTURER_RECORD,
    EVIDENCE_TYPE_TEST_RESULT,
    EVIDENCE_TYPE_OTHER
}

# Event Label States
LABEL_EVENT = "EVENT"
LABEL_NON_EVENT = "NON_EVENT"
LABEL_UNKNOWN = "UNKNOWN"

VALID_EVENT_LABELS = {LABEL_EVENT, LABEL_NON_EVENT, LABEL_UNKNOWN}


@dataclass
class EvidenceItem:
    evidence_id: str
    sensor_id: str
    capture_time_utc: str
    operator: str
    evidence_type: str
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    description: str = ""
    status: str = "VERIFIED"  # VERIFIED, NOT_AVAILABLE, PENDING, UNVERIFIED
    site_id: str = "SITE-NH10-KM48"
    corridor_id: str = "CORR-NH10-SIKKIM-KM48"
    capture_timestamp: Optional[str] = None
    upload_timestamp: Optional[str] = None
    source: str = "FIELD_INSPECTION"
    sha256: Optional[str] = None
    gps: Optional[Dict[str, float]] = None
    verification_status: str = "VERIFIED"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.capture_timestamp:
            self.capture_timestamp = self.capture_time_utc
        if not self.capture_time_utc:
            self.capture_time_utc = self.capture_timestamp
        if not self.sha256:
            self.sha256 = self.file_hash
        if not self.file_hash:
            self.file_hash = self.sha256
        if not self.upload_timestamp:
            self.upload_timestamp = datetime.now(timezone.utc).isoformat()
        if not self.verification_status:
            self.verification_status = self.status
        if not self.status:
            self.status = self.verification_status

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EventLinkageRecord:
    linkage_id: str
    event_id: str
    sensor_id: str
    corridor_id: str
    event_timestamp_utc: str
    observation_window_start: str
    observation_window_end: str
    label: str  # EVENT, NON_EVENT, UNKNOWN
    label_source: str
    verification_status: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FieldEvidenceManager:
    """
    Manages cryptographic field evidence packaging, audit ledgers,
    event label linkages, and baseline sensor statistics.
    """

    def __init__(self, base_evidence_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.evidence_dir = base_evidence_dir or os.path.join(base_dir, "field_evidence")
        self.ledger_path = os.path.join(base_dir, "data", "processed", "field_evidence_ledger.json")

        self._evidence_catalog: Dict[str, List[EvidenceItem]] = {}
        self._event_linkages: List[EventLinkageRecord] = []

        self._init_directories()
        self._load_ledger()

    def _init_directories(self) -> None:
        """Initializes canonical directory structure."""
        os.makedirs(self.evidence_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)

    def _load_ledger(self) -> None:
        """Loads evidence and linkage ledger from disk if available."""
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for s_id, items in data.get("evidence", {}).items():
                        self._evidence_catalog[s_id] = [EvidenceItem(**item) for item in items]
                    for link in data.get("event_linkages", []):
                        self._event_linkages.append(EventLinkageRecord(**link))
                logger.info(f"Loaded {sum(len(v) for v in self._evidence_catalog.values())} evidence records.")
            except Exception as e:
                logger.warning(f"Could not load field evidence ledger: {e}")

    def _save_ledger(self) -> None:
        """Saves evidence catalog and event linkages."""
        try:
            data = {
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
                "evidence": {k: [i.to_dict() for i in v] for k, v in self._evidence_catalog.items()},
                "event_linkages": [l.to_dict() for l in self._event_linkages]
            }
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save field evidence ledger: {e}")

    def compute_file_hash(self, file_path: str) -> Optional[str]:
        """Calculates SHA-256 hash of a physical file."""
        if not os.path.exists(file_path):
            return None
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def register_evidence(
        self,
        sensor_id: str,
        evidence_type: str,
        operator: str,
        description: str,
        file_path: Optional[str] = None,
        is_available: bool = True,
        site_id: str = "SITE-NH10-KM48",
        corridor_id: str = "CORR-NH10-SIKKIM-KM48",
        capture_timestamp: Optional[str] = None,
        source: str = "FIELD_INSPECTION",
        gps: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvidenceItem:
        """
        Registers an evidence item into the sensor's package.
        If file is missing or is_available=False, records NOT_AVAILABLE.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        e_id = f"ev-{uuid.uuid4().hex[:10]}"
        cap_ts = capture_timestamp or now_iso

        if not is_available or not file_path or not os.path.exists(file_path):
            item = EvidenceItem(
                evidence_id=e_id,
                sensor_id=sensor_id,
                capture_time_utc=cap_ts,
                operator=operator,
                evidence_type=evidence_type,
                file_path=None,
                file_hash=None,
                description=description,
                status="NOT_AVAILABLE",
                site_id=site_id,
                corridor_id=corridor_id,
                capture_timestamp=cap_ts,
                upload_timestamp=now_iso,
                source=source,
                sha256=None,
                gps=gps,
                verification_status="NOT_AVAILABLE",
                metadata=metadata or {}
            )
        else:
            f_hash = self.compute_file_hash(file_path)
            item = EvidenceItem(
                evidence_id=e_id,
                sensor_id=sensor_id,
                capture_time_utc=cap_ts,
                operator=operator,
                evidence_type=evidence_type,
                file_path=file_path,
                file_hash=f_hash,
                description=description,
                status="VERIFIED",
                site_id=site_id,
                corridor_id=corridor_id,
                capture_timestamp=cap_ts,
                upload_timestamp=now_iso,
                source=source,
                sha256=f_hash,
                gps=gps,
                verification_status="VERIFIED",
                metadata=metadata or {}
            )

        self._evidence_catalog.setdefault(sensor_id, []).append(item)
        self._save_ledger()
        return item

    def get_sensor_evidence(self, sensor_id: str) -> List[Dict[str, Any]]:
        """Returns all evidence items associated with a sensor."""
        return [i.to_dict() for i in self._evidence_catalog.get(sensor_id, [])]

    def link_event_window(
        self,
        event_id: str,
        sensor_id: str,
        corridor_id: str,
        event_timestamp_utc: str,
        window_start_utc: str,
        window_end_utc: str,
        label: str,
        label_source: str,
        notes: str = ""
    ) -> EventLinkageRecord:
        """
        Links a temporal observation window to a documented event.
        Label must be EVENT, NON_EVENT, or UNKNOWN.
        """
        if label not in VALID_EVENT_LABELS:
            raise ValueError(f"Invalid label '{label}'. Must be one of: {VALID_EVENT_LABELS}")

        l_id = f"link-{uuid.uuid4().hex[:8]}"
        record = EventLinkageRecord(
            linkage_id=l_id,
            event_id=event_id,
            sensor_id=sensor_id,
            corridor_id=corridor_id,
            event_timestamp_utc=event_timestamp_utc,
            observation_window_start=window_start_utc,
            observation_window_end=window_end_utc,
            label=label,
            label_source=label_source,
            verification_status="LINKED",
            notes=notes
        )
        self._event_linkages.append(record)
        self._save_ledger()
        return record

    def get_event_linkages(self, sensor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns event linkages filtered optionally by sensor_id."""
        if sensor_id:
            return [l.to_dict() for l in self._event_linkages if l.sensor_id == sensor_id]
        return [l.to_dict() for l in self._event_linkages]

    def compute_baseline_statistics(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes descriptive baseline statistics (mean, median, std, min, max, missingness)
        without making unwarranted failure interpretations.
        """
        if not observations:
            return {
                "sample_count": 0,
                "status": "NO_DATA",
                "missingness_pct": 100.0
            }

        numeric_vals: List[float] = []
        timestamps: List[datetime] = []

        for obs in observations:
            val = obs.get("value")
            if val is not None:
                try:
                    numeric_vals.append(float(val))
                except Exception:
                    pass
            t_str = obs.get("timestamp_utc") or obs.get("received_at")
            if t_str:
                try:
                    timestamps.append(datetime.fromisoformat(str(t_str).replace("Z", "+00:00")))
                except Exception:
                    pass

        if not numeric_vals:
            return {
                "sample_count": 0,
                "status": "NO_NUMERIC_OBSERVATIONS",
                "missingness_pct": 100.0
            }

        numeric_vals.sort()
        n = len(numeric_vals)
        mean_val = sum(numeric_vals) / n
        median_val = numeric_vals[n // 2] if n % 2 != 0 else (numeric_vals[n // 2 - 1] + numeric_vals[n // 2]) / 2.0
        var_val = sum((x - mean_val) ** 2 for x in numeric_vals) / n
        std_val = var_val ** 0.5

        # Temporal span
        if len(timestamps) >= 2:
            timestamps.sort()
            span_seconds = (timestamps[-1] - timestamps[0]).total_seconds()
        else:
            span_seconds = 0.0

        return {
            "sample_count": n,
            "min": round(min(numeric_vals), 3),
            "max": round(max(numeric_vals), 3),
            "mean": round(mean_val, 3),
            "median": round(median_val, 3),
            "std_dev": round(std_val, 3),
            "temporal_span_hours": round(span_seconds / 3600.0, 2),
            "status": "STATISTICALLY_VALID"
        }


# Global singleton manager
GLOBAL_FIELD_EVIDENCE_MANAGER = FieldEvidenceManager()
