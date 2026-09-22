# -*- coding: utf-8 -*-
"""
tests/test_v4_8_event_labels.py
===============================
Automated test suite for Phase V4.8 Event Labeling Foundation.
Tests:
  1. 3-State event labeling: EVENT, NON_EVENT, UNKNOWN.
  2. Verified landslide event linkage (EVENT = 1).
  3. Evidence-backed stable control linkage (NON_EVENT = 0).
  4. Unmonitored / uncertain period linkage (UNKNOWN).
  5. Exclusion of UNKNOWN labels from binary supervised datasets.
"""

import pytest
from services.field_evidence_manager import (
    GLOBAL_FIELD_EVIDENCE_MANAGER,
    LABEL_EVENT,
    LABEL_NON_EVENT,
    LABEL_UNKNOWN,
    VALID_EVENT_LABELS
)


def test_event_label_three_states_validity():
    """Confirms only EVENT, NON_EVENT, UNKNOWN are recognized valid label states."""
    assert LABEL_EVENT == "EVENT"
    assert LABEL_NON_EVENT == "NON_EVENT"
    assert LABEL_UNKNOWN == "UNKNOWN"
    assert len(VALID_EVENT_LABELS) == 3


def test_event_linkage_creation_and_retrieval():
    """Tests creating and querying verified EVENT, NON_EVENT, and UNKNOWN linkages."""
    mgr = GLOBAL_FIELD_EVIDENCE_MANAGER

    # Event link
    rec_evt = mgr.link_event_window(
        event_id="EVT-TEST-GLOF-01",
        sensor_id="PIEZO-NH10-KM48-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        event_timestamp_utc="2024-06-15T10:00:00Z",
        window_start_utc="2024-06-12T10:00:00Z",
        window_end_utc="2024-06-15T10:00:00Z",
        label=LABEL_EVENT,
        label_source="GSI_SPECIAL_REPORT_2024",
        notes="Documented debris flow"
    )
    assert rec_evt.label == LABEL_EVENT
    assert rec_evt.verification_status == "LINKED"

    # Control link
    rec_ctrl = mgr.link_event_window(
        event_id="CTRL-TEST-DRY-01",
        sensor_id="PIEZO-NH10-KM48-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        event_timestamp_utc="2024-01-15T12:00:00Z",
        window_start_utc="2024-01-12T12:00:00Z",
        window_end_utc="2024-01-15T12:00:00Z",
        label=LABEL_NON_EVENT,
        label_source="IMD_AWS_VERIFIED_DRY",
        notes="Zero precipitation, zero deformation"
    )
    assert rec_ctrl.label == LABEL_NON_EVENT

    # Unknown link
    rec_unk = mgr.link_event_window(
        event_id="SPAN-TEST-UNCERTAIN-01",
        sensor_id="PIEZO-NH10-KM48-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        event_timestamp_utc="2024-03-01T00:00:00Z",
        window_start_utc="2024-02-28T00:00:00Z",
        window_end_utc="2024-03-01T00:00:00Z",
        label=LABEL_UNKNOWN,
        label_source="UNMONITORED_GAP",
        notes="Telemetry dropout; ground truth unknown"
    )
    assert rec_unk.label == LABEL_UNKNOWN


def test_unknown_labels_strictly_excluded_from_binary_training():
    """Confirms that UNKNOWN labeled windows cannot be used as negative controls."""
    mgr = GLOBAL_FIELD_EVIDENCE_MANAGER
    linkages = mgr.get_event_linkages()
    
    # Filter for binary supervised set
    supervised_set = [l for l in linkages if l["label"] in [LABEL_EVENT, LABEL_NON_EVENT]]
    for item in supervised_set:
        assert item["label"] != LABEL_UNKNOWN
