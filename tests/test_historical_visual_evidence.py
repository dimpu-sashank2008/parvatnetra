"""
tests/test_historical_visual_evidence.py
=========================================
Forensic test suite verifying the 5 mandatory visual evidence layer invariants:
1. Events without media remain 100% valid with event_label=1;
2. Media provenance is preserved across ingestion, manifest, and API;
3. Unverified media submissions cannot become verified automatically without statutory authorization;
4. Missing media is explicitly documented and displayed as NOT_AVAILABLE;
5. Synthetic/demo media remains strictly quarantined (DEMO_QUARANTINED).
"""

import json
import os
import unittest
from datetime import datetime

from engine.pahad_events import (
    VALID_EVIDENCE_TYPES,
    VALID_VERIFICATION_STATUSES,
    STATUS_VERIFIED,
    STATUS_NOT_AVAILABLE,
    STATUS_PENDING,
    STATUS_UNVERIFIED,
    STATUS_DEMO_QUARANTINED,
    LandslideEventObservation,
    VisualEvidenceRecord,
)
from engine.pahad_history import (
    HISTORICAL_LANDSLIDES_CATALOG,
    HISTORICAL_RECURRENCE_PREDICTOR,
    HistoricalRecurrencePredictor,
)
from app import app


class TestHistoricalVisualEvidenceLayer(unittest.TestCase):
    """Forensic verification of the provenance-controlled visual evidence layer."""

    def setUp(self):
        self.client = app.test_client()
        self.predictor = HISTORICAL_RECURRENCE_PREDICTOR

    def test_01_events_without_media_remain_valid(self):
        """Invariant 1: Events without media are 100% valid with event_label=1 and not invalidated."""
        # 1. Test LandslideEventObservation dataclass creation with empty visual_evidence
        event_no_media = LandslideEventObservation(
            sector_id="SK-NH10-KM48",
            timestamp="2024-07-15T08:00:00Z",
            event_label=1,
            visual_evidence=[],
        )
        self.assertEqual(event_no_media.event_label, 1)
        self.assertEqual(len(event_no_media.visual_evidence), 0)

        # 2. Test Canonical Inventory Manifest: events without media (e.g. EV-13, EV-15, EV-17)
        manifest_path = os.path.join("data", "manifests", "canonical_event_inventory.json")
        self.assertTrue(os.path.exists(manifest_path), f"Missing manifest: {manifest_path}")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        events = manifest.get("canonical_events", [])
        no_media_events = [
            e for e in events
            if any(ev.get("verification_status") == "NOT_AVAILABLE" for ev in e.get("visual_evidence", []))
            or len(e.get("visual_evidence", [])) == 0
        ]
        self.assertGreaterEqual(len(no_media_events), 3, "Expected at least 3 events with NOT_AVAILABLE media")
        for ev in no_media_events:
            self.assertEqual(ev["event_label"], 1, f"Event {ev['event_id']} label must remain 1")
            self.assertIsNotNone(ev["latitude"])
            self.assertIsNotNone(ev["longitude"])
            self.assertEqual(ev["provenance"], "[HISTORICAL]")

    def test_02_media_provenance_is_preserved(self):
        """Invariant 2: Media provenance tags and cryptographic SHA-256 digests are preserved."""
        # Check disasters catalog
        disaster = HISTORICAL_LANDSLIDES_CATALOG["DIS-2022-NONEY"]
        self.assertIn("visual_evidence", disaster)
        evidence_items = disaster["visual_evidence"]
        self.assertGreaterEqual(len(evidence_items), 2)

        for ev in evidence_items:
            self.assertIn(ev["evidence_type"], VALID_EVIDENCE_TYPES)
            self.assertIn(ev["verification_status"], VALID_VERIFICATION_STATUSES)
            self.assertTrue(
                ev["provenance"].startswith("[") and ev["provenance"].endswith("]"),
                f"Provenance tag '{ev['provenance']}' must follow [TAG] bracket convention"
            )
            self.assertIn("sha256_hash", ev)
            if ev["sha256_hash"]:
                self.assertEqual(len(ev["sha256_hash"]), 64, "SHA-256 hash must be 64 hexadecimal characters")

        # Test through REST API endpoint GET /api/pahad/history/events/<event_id>/evidence
        res = self.client.get("/api/pahad/history/events/DIS-2022-NONEY/evidence")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["event_id"], "DIS-2022-NONEY")
        self.assertGreaterEqual(data["evidence_count"], 2)
        for ev_resp in data["visual_evidence"]:
            self.assertIn("provenance", ev_resp)
            self.assertIn(ev_resp["provenance"], ["[OFFICIAL_GOI]", "[HISTORICAL]", "[NOT_AVAILABLE]"])

    def test_03_unverified_media_cannot_auto_verify(self):
        """Invariant 3: External or user media submissions cannot self-promote to VERIFIED."""
        # Test engine helper: submit_visual_evidence without authority
        pred = HistoricalRecurrencePredictor()
        raw_submission = {
            "evidence_type": "FIELD_PHOTO",
            "source_url": "https://field-reporter.example.org/photo123.jpg",
            "capture_date": "2026-09-10T12:00:00Z",
            "description": "Crack opening at Km 48.2",
            "verification_status": "VERIFIED",  # Maliciously claiming VERIFIED
            "provenance": "[UNAUTHORIZED_SUBMISSION]",
            "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
        
        # Submitting without statutory token
        recorded = pred.submit_visual_evidence("DIS-2024-NH10", raw_submission, authority_token=None)
        self.assertEqual(
            recorded["verification_status"],
            "UNVERIFIED",
            "Unverified submission without token must be demoted to UNVERIFIED"
        )
        self.assertEqual(recorded["provenance"], "[UNVERIFIED_FIELD]")

        # Test REST API POST /api/pahad/history/evidence/submit without token
        api_payload = {
            "event_id": "DIS-2024-NH10",
            "evidence": {
                "evidence_type": "FIELD_PHOTO",
                "source_url": "https://field.example.org/shot.jpg",
                "description": "Eyewitness rockfall",
                "verification_status": "VERIFIED"  # Attempting auto-verification
            }
        }
        api_res = self.client.post(
            "/api/pahad/history/evidence/submit",
            json=api_payload
        )
        self.assertEqual(api_res.status_code, 201)
        res_data = api_res.get_json()
        self.assertEqual(
            res_data["evidence"]["verification_status"],
            "UNVERIFIED",
            "API must enforce UNVERIFIED status for unauthenticated submissions"
        )

        # Submitting with statutory token
        valid_submission = pred.submit_visual_evidence(
            "DIS-2024-NH10",
            {"evidence_type": "GEOTECHNICAL_SKETCH", "description": "GSI Cross-section", "verification_status": "VERIFIED"},
            authority_token="GSI-STATUTORY-AUTH-NER"
        )
        self.assertEqual(valid_submission["verification_status"], "VERIFIED")
        self.assertEqual(valid_submission["provenance"], "[STATUTORY_VERIFIED]")

    def test_04_missing_media_clearly_displayed_as_not_available(self):
        """Invariant 4: Events lacking digital media explicitly display NOT_AVAILABLE."""
        # Query canonical event with NOT_AVAILABLE media (EV-13)
        res = self.client.get("/api/pahad/history/events/EV-13/evidence")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["event_id"], "EV-13")
        self.assertEqual(data["evidence_count"], 1)
        evidence = data["visual_evidence"][0]
        self.assertEqual(evidence["verification_status"], "NOT_AVAILABLE")
        self.assertIn("No digital photographic", evidence["description"])

    def test_05_synthetic_demo_media_quarantined(self):
        """Invariant 5: Synthetic/demo media is tagged DEMO_QUARANTINED and quarantined from operational views."""
        pred = HistoricalRecurrencePredictor()
        
        # Filter evidence with default operational mode (exclude DEMO_QUARANTINED)
        demo_evidence = [
            VisualEvidenceRecord(
                evidence_id="EVID-TEST-01",
                event_id="EV-TEST-01",
                evidence_type="FIELD_PHOTO",
                title="Field Inspection Photograph",
                description="Legitimate GSI field photo",
                source_reference="GSI Technical Bulletin",
                verification_status="VERIFIED",
                provenance="[OFFICIAL_GOI]"
            ).to_dict(),
            VisualEvidenceRecord(
                evidence_id="EVID-TEST-02",
                event_id="EV-TEST-01",
                evidence_type="FIELD_PHOTO",
                title="Synthetic Landslide Simulation",
                description="Synthetic AI generated landslide image for demo",
                source_reference="Synthetic Test Suite",
                verification_status="DEMO_QUARANTINED",
                provenance="[DEMO]"
            ).to_dict()
        ]

        # Operational query (include_quarantined=False)
        operational_view = pred.filter_visual_evidence(demo_evidence, include_quarantined=False)
        self.assertEqual(len(operational_view), 1)
        self.assertEqual(operational_view[0]["verification_status"], "VERIFIED")

        # Demo mode query (include_quarantined=True)
        demo_view = pred.filter_visual_evidence(demo_evidence, include_quarantined=True)
        self.assertEqual(len(demo_view), 2)
        quarantined_items = [ev for ev in demo_view if ev["verification_status"] == "DEMO_QUARANTINED"]
        self.assertEqual(len(quarantined_items), 1)
        self.assertEqual(quarantined_items[0]["provenance"], "[DEMO]")

    def test_06_catalog_api_summary_metrics(self):
        """Verify GET /api/pahad/history/catalog returns visual_evidence_summary."""
        res = self.client.get("/api/pahad/history/catalog")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("visual_evidence_summary", data)
        summary = data["visual_evidence_summary"]
        self.assertIn("total_evidence_items", summary)
        self.assertIn("verified_count", summary)
        self.assertIn("not_available_count", summary)
        self.assertGreaterEqual(summary["verified_count"], 10)


if __name__ == "__main__":
    unittest.main()
