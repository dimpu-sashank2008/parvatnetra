"""
engine/pahad_cap.py
===================
PAHAD Phase 3 — OASIS / ITU-T CAP v1.2 Engine for NDMA SACHET
--------------------------------------------------------------
Generates compliant OASIS Common Alerting Protocol (CAP) v1.2
XML payloads for NDMA SACHET disaster warning gateway ingestion.

Standards Compliance:
- OASIS CAP v1.2 (urn:oasis:names:tc:emergency:cap:1.2)
- ITU-T Recommendation X.1303
- NDMA All-India Disaster Alerting Protocol (SACHET)

Author : PARVAT NETRA / PAHAD Engineering Team
Data   : [SIMULATED] OASIS CAP v1.2 NDMA SACHET feed
"""

from __future__ import annotations

import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

CAP_NAMESPACE = "urn:oasis:names:tc:emergency:cap:1.2"
DEFAULT_SENDER = "pahad-ews@ner.gov.in"


class CAPAlertGenerator:
    """
    OASIS Common Alerting Protocol (CAP) v1.2 XML generator.
    Produces compliant payloads ready for NDMA SACHET ingestion.
    """

    def __init__(self, sender: str = DEFAULT_SENDER) -> None:
        self.sender = sender

    @staticmethod
    def map_cri_to_severity(band: str = "", cri_score: Optional[float] = None) -> str:
        """Map PAHAD CRI score / risk band to CAP severity (Extreme|Severe|Moderate)."""
        b = (band or "").upper()
        if b in ("EXTREME", "CRITICAL") or (cri_score is not None and cri_score >= 80.0):
            return "Extreme"
        if b in ("VERY_HIGH", "HIGH", "SEVERE") or (cri_score is not None and cri_score >= 50.0):
            return "Severe"
        return "Moderate"

    @staticmethod
    def map_severity_to_urgency(severity: str) -> str:
        """Map CAP severity to urgency (Immediate|Expected|Future)."""
        s = severity.capitalize()
        if s == "Extreme":
            return "Immediate"
        if s == "Severe":
            return "Expected"
        return "Future"

    @staticmethod
    def map_severity_to_certainty(severity: str) -> str:
        """Map CAP severity to certainty (Observed|Likely|Possible)."""
        s = severity.capitalize()
        if s == "Extreme":
            return "Observed"
        if s == "Severe":
            return "Likely"
        return "Possible"

    def format_polygon_coords(self, coords: Any) -> str:
        """
        Format list of [lat, lon] points into CAP 1.2 space-delimited string:
        'lat,lon lat,lon lat,lon ... lat,lon' ensuring closed polygon.
        """
        if isinstance(coords, str) and coords.strip():
            return coords.strip()

        if isinstance(coords, (list, tuple)) and len(coords) >= 3:
            pts = []
            for p in coords:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    pts.append(f"{float(p[0]):.5f},{float(p[1]):.5f}")
            if pts:
                # Ensure closed polygon (first point == last point)
                if pts[0] != pts[-1]:
                    pts.append(pts[0])
                return " ".join(pts)

        # Default fallback polygon around NH-10 Km 48 (Sikkim corridor)
        return (
            "27.33000,88.61000 27.33500,88.61000 27.33500,88.61500 "
            "27.33000,88.61500 27.33000,88.61000"
        )

    def build_cap_xml(self, alert_data: Dict[str, Any]) -> str:
        """
        Build and validate OASIS CAP v1.2 XML string from input alert dictionary.

        Required elements enforced:
        - identifier, sender, sent, status, msgType, scope
        - info: category, event, urgency, severity, certainty, area (areaDesc, polygon)
        """
        # Register namespace without prefix so root becomes <alert xmlns="...">
        ET.register_namespace("", CAP_NAMESPACE)

        # 1. Identifier
        raw_id = alert_data.get("identifier")
        if not raw_id:
            sec = alert_data.get("sector_id", "NER")
            clean_sec = str(sec).replace(" ", "-").replace("/", "-")
            short_uuid = uuid.uuid4().hex[:8].upper()
            identifier = f"PAHAD-{clean_sec}-2026-{short_uuid}"
        else:
            identifier = str(raw_id)

        # 2. Administrative envelopes
        sender = str(alert_data.get("sender", self.sender))
        sent = str(alert_data.get("sent") or datetime.now(timezone.utc).isoformat())
        status = str(alert_data.get("status", "Actual"))
        msg_type = str(alert_data.get("msgType", "Alert"))
        scope = str(alert_data.get("scope", "Public"))

        # 3. Info metadata
        category = str(alert_data.get("category", "Geo"))
        event = str(alert_data.get("event", "Landslide Risk Warning"))

        # Severity resolution
        severity = alert_data.get("severity")
        if not severity:
            severity = self.map_cri_to_severity(
                band=alert_data.get("band", ""),
                cri_score=alert_data.get("cri_score")
            )
        severity = str(severity).capitalize()
        if severity not in ("Extreme", "Severe", "Moderate", "Minor", "Unknown"):
            severity = "Severe"

        urgency = str(alert_data.get("urgency") or self.map_severity_to_urgency(severity)).capitalize()
        certainty = str(alert_data.get("certainty") or self.map_severity_to_certainty(severity)).capitalize()

        # Textual annotations
        sector_name = alert_data.get("sector_name", alert_data.get("sector_id", "NH-10 Himalayan Corridor"))
        headline = alert_data.get("headline", f"PAHAD Landslide Warning for {sector_name}")
        description = alert_data.get(
            "description",
            f"Multi-hazard geotechnical instability detected in {sector_name}. "
            f"Rainfall and pore pressure exceed threshold levels."
        )
        instruction = alert_data.get(
            "instruction",
            "Evacuate vulnerable slope corridors immediately. Follow SDRF/BRO detour advisories."
        )

        # 4. Area descriptor & polygon
        area_desc = str(alert_data.get("areaDesc") or sector_name)
        polygon_str = self.format_polygon_coords(
            alert_data.get("coordinates_polygon") or alert_data.get("polygon")
        )

        # 5. Assemble XML DOM tree
        ns_prefix = f"{{{CAP_NAMESPACE}}}"
        root = ET.Element(f"{ns_prefix}alert")

        # Top-level alert elements
        ET.SubElement(root, f"{ns_prefix}identifier").text = identifier
        ET.SubElement(root, f"{ns_prefix}sender").text = sender
        ET.SubElement(root, f"{ns_prefix}sent").text = sent
        ET.SubElement(root, f"{ns_prefix}status").text = status
        ET.SubElement(root, f"{ns_prefix}msgType").text = msg_type
        ET.SubElement(root, f"{ns_prefix}scope").text = scope

        # <info> element
        info_elem = ET.SubElement(root, f"{ns_prefix}info")
        ET.SubElement(info_elem, f"{ns_prefix}category").text = category
        ET.SubElement(info_elem, f"{ns_prefix}event").text = event
        ET.SubElement(info_elem, f"{ns_prefix}urgency").text = urgency
        ET.SubElement(info_elem, f"{ns_prefix}severity").text = severity
        ET.SubElement(info_elem, f"{ns_prefix}certainty").text = certainty

        # Event code for SAME / CAP indexing
        event_code = ET.SubElement(info_elem, f"{ns_prefix}eventCode")
        ET.SubElement(event_code, f"{ns_prefix}valueName").text = "SAME"
        ET.SubElement(event_code, f"{ns_prefix}value").text = "LSW"

        # Effective and expiry times
        effective_time = str(alert_data.get("effective") or sent)
        expires_time = str(alert_data.get("expires") or alert_data.get("expiry") or "")
        ET.SubElement(info_elem, f"{ns_prefix}effective").text = effective_time
        if expires_time:
            ET.SubElement(info_elem, f"{ns_prefix}expires").text = expires_time

        # Language
        language = str(alert_data.get("language", "en-IN"))
        ET.SubElement(info_elem, f"{ns_prefix}language").text = language

        ET.SubElement(info_elem, f"{ns_prefix}headline").text = headline
        ET.SubElement(info_elem, f"{ns_prefix}description").text = description
        ET.SubElement(info_elem, f"{ns_prefix}instruction").text = instruction

        # Authorization Reference Parameter
        auth_ref = alert_data.get("authorization_reference") or alert_data.get("authorization_token") or alert_data.get("auth_ref")
        if auth_ref:
            param_elem = ET.SubElement(info_elem, f"{ns_prefix}parameter")
            ET.SubElement(param_elem, f"{ns_prefix}valueName").text = "authorizationReference"
            ET.SubElement(param_elem, f"{ns_prefix}value").text = str(auth_ref)

        # <area> element
        area_elem = ET.SubElement(info_elem, f"{ns_prefix}area")
        ET.SubElement(area_elem, f"{ns_prefix}areaDesc").text = area_desc
        ET.SubElement(area_elem, f"{ns_prefix}polygon").text = polygon_str

        # Format with indentation for readability
        ET.indent(root, space="  ")

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        xml_str = xml_bytes.decode("utf-8")

        # Validate well-formedness
        ET.fromstring(xml_str.encode("utf-8"))

        return xml_str

    def build_cap_dict(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns structured dictionary conforming to OASIS CAP v1.2 specification."""
        sec = alert_data.get("sector_id", "NER")
        clean_sec = str(sec).replace(" ", "-").replace("/", "-")
        identifier = str(alert_data.get("identifier") or f"PAHAD-{clean_sec}-2026-{uuid.uuid4().hex[:8].upper()}")
        now_iso = datetime.now(timezone.utc).isoformat()
        severity = str(alert_data.get("severity") or "Severe").capitalize()
        auth_ref = str(alert_data.get("authorization_reference") or alert_data.get("authorization_token") or "UNSPECIFIED")

        return {
            "identifier": identifier,
            "sender": str(alert_data.get("sender", self.sender)),
            "sent": str(alert_data.get("sent", now_iso)),
            "status": str(alert_data.get("status", "Actual")),
            "msgType": str(alert_data.get("msgType", "Alert")),
            "scope": str(alert_data.get("scope", "Public")),
            "info": {
                "category": str(alert_data.get("category", "Geo")),
                "event": str(alert_data.get("event", "Landslide Hazard Warning")),
                "urgency": str(alert_data.get("urgency") or self.map_severity_to_urgency(severity)),
                "severity": severity,
                "certainty": str(alert_data.get("certainty") or self.map_severity_to_certainty(severity)),
                "effective": str(alert_data.get("effective", now_iso)),
                "expires": str(alert_data.get("expires", "")),
                "headline": str(alert_data.get("headline", f"PAHAD Warning: {sec}")),
                "description": str(alert_data.get("description", "Hillslope instability hazard detected.")),
                "instruction": str(alert_data.get("instruction", "Follow evacuation routes.")),
                "language": str(alert_data.get("language", "en-IN")),
                "authorization_reference": auth_ref,
                "area": {
                    "areaDesc": str(alert_data.get("areaDesc", sec)),
                    "polygon": self.format_polygon_coords(alert_data.get("coordinates_polygon") or alert_data.get("polygon"))
                }
            }
        }

