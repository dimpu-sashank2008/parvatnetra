# -*- coding: utf-8 -*-
"""
tests/test_v4_7_field_evidence.py
=================================
Phase V4.7 Test Suite: Field Evidence Packaging, SHA-256 Verification & Event Linkages
"""

import os
import pytest

from services.field_evidence_manager import (
    FieldEvidenceManager,
    EVIDENCE_TYPE_PHOTO,
    EVIDENCE_TYPE_CALIBRATION_CERTIFICATE,
    EVIDENCE_TYPE_INSTALLATION_RECORD,
    LABEL_EVENT,
    LABEL_NON_EVENT,
    LABEL_UNKNOWN
)


@pytest.fixture
def evidence_manager(tmp_path):
    base_dir = str(tmp_path / "evidence")
    mgr = FieldEvidenceManager(base_evidence_dir=base_dir)
    return mgr


class TestFieldEvidenceRegistration:
    """Tests evidence packaging, hash checks, and missingness handling."""

    def test_register_verified_evidence_with_hash(self, evidence_manager, tmp_path):
        sample_file = tmp_path / "cal_cert.pdf"
        sample_file.write_bytes(b"%PDF-1.4 SAMPLE CALIBRATION CERTIFICATE DATA")

        item = evidence_manager.register_evidence(
            sensor_id="PIEZO-NH10-KM48-01",
            evidence_type=EVIDENCE_TYPE_CALIBRATION_CERTIFICATE,
            operator="CalibrationTech",
            description="NABL certified zero offset certificate",
            file_path=str(sample_file),
            is_available=True
        )
        assert item.status == "VERIFIED"
        assert item.file_hash is not None
        assert len(item.file_hash) == 64

    def test_register_missing_evidence_as_not_available(self, evidence_manager):
        item = evidence_manager.register_evidence(
            sensor_id="INCL-NH10-KM48-01",
            evidence_type=EVIDENCE_TYPE_PHOTO,
            operator="FieldInspector",
            description="Borehole casing head photo",
            file_path="/path/does/not/exist.jpg",
            is_available=False
        )
        assert item.status == "NOT_AVAILABLE"
        assert item.file_hash is None


class TestEventLinkageFoundation:
    """Tests temporal event labeling foundation."""

    def test_valid_event_and_control_linkages(self, evidence_manager):
        l1 = evidence_manager.link_event_window(
            event_id="EVT-2023-TEESTA-01",
            sensor_id="PIEZO-NH10-KM48-01",
            corridor_id="CORR-NH10-SIKKIM-KM48",
            event_timestamp_utc="2023-10-04T06:00:00Z",
            window_start_utc="2023-10-01T06:00:00Z",
            window_end_utc="2023-10-04T06:00:00Z",
            label=LABEL_EVENT,
            label_source="GSI_DISASTER_RECORD",
            notes="South Lhonak GLOF Teesta surge"
        )
        assert l1.label == LABEL_EVENT

        l2 = evidence_manager.link_event_window(
            event_id="CTRL-2023-DRY-01",
            sensor_id="PIEZO-NH10-KM48-01",
            corridor_id="CORR-NH10-SIKKIM-KM48",
            event_timestamp_utc="2023-12-15T12:00:00Z",
            window_start_utc="2023-12-12T12:00:00Z",
            window_end_utc="2023-12-15T12:00:00Z",
            label=LABEL_NON_EVENT,
            label_source="IMD_VERIFIED_DRY_WINDOW",
            notes="Verified stable winter period"
        )
        assert l2.label == LABEL_NON_EVENT

        l3 = evidence_manager.link_event_window(
            event_id="UNVERIFIED-WINDOW-01",
            sensor_id="PIEZO-NH10-KM48-01",
            corridor_id="CORR-NH10-SIKKIM-KM48",
            event_timestamp_utc="2024-05-10T00:00:00Z",
            window_start_utc="2024-05-07T00:00:00Z",
            window_end_utc="2024-05-10T00:00:00Z",
            label=LABEL_UNKNOWN,
            label_source="UNMONITORED_SPAN",
            notes="No ground truth report available; non-event cannot be assumed"
        )
        assert l3.label == LABEL_UNKNOWN

    def test_reject_invalid_event_label(self, evidence_manager):
        with pytest.raises(ValueError) as exc:
            evidence_manager.link_event_window(
                event_id="E1",
                sensor_id="S1",
                corridor_id="C1",
                event_timestamp_utc="2024-01-01T00:00:00Z",
                window_start_utc="2024-01-01T00:00:00Z",
                window_end_utc="2024-01-01T00:00:00Z",
                label="MAYBE_LANDSLIDE",  # Invalid
                label_source="TEST"
            )
        assert "Invalid label" in str(exc.value)


class TestBaselineStatistics:
    """Tests descriptive baseline calculations without making failure inferences."""

    def test_descriptive_stats_computation(self, evidence_manager):
        obs = [
            {"value": 10.0, "timestamp_utc": "2026-09-01T10:00:00Z"},
            {"value": 12.0, "timestamp_utc": "2026-09-01T10:05:00Z"},
            {"value": 14.0, "timestamp_utc": "2026-09-01T10:10:00Z"},
            {"value": 16.0, "timestamp_utc": "2026-09-01T10:15:00Z"},
            {"value": 18.0, "timestamp_utc": "2026-09-01T10:20:00Z"}
        ]
        stats = evidence_manager.compute_baseline_statistics(obs)
        assert stats["sample_count"] == 5
        assert stats["min"] == 10.0
        assert stats["max"] == 18.0
        assert stats["mean"] == 14.0
        assert stats["median"] == 14.0
        assert stats["std_dev"] > 0
        assert stats["status"] == "STATISTICALLY_VALID"

    def test_empty_observations_handled_safely(self, evidence_manager):
        stats = evidence_manager.compute_baseline_statistics([])
        assert stats["sample_count"] == 0
        assert stats["missingness_pct"] == 100.0
        assert stats["status"] == "NO_DATA"
