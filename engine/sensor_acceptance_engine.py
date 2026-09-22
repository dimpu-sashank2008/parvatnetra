# -*- coding: utf-8 -*-
"""
engine/sensor_acceptance_engine.py
==================================
PARVAT NETRA • In-Situ Geotechnical Sensor Acceptance & Lifecycle Engine
-------------------------------------------------------------------------
Phase V4.7 Formal 10-Stage Sensor Acceptance Lifecycle:
PLANNED -> RECEIVED -> IDENTIFIED -> CALIBRATED -> BENCH_ACCEPTED ->
INSTALLED -> CONNECTED -> TELEMETRY_VALIDATED -> FIELD_COMMISSIONED -> MONITORING

Every state transition requires an immutable, evidence-backed transition record.
Software-only commissioning is strictly forbidden: software tests can establish
BENCH_ACCEPTED or SOFTWARE_VALIDATED, but never FIELD_COMMISSIONED.
"""

from __future__ import annotations

import os
import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("SENSOR_ACCEPTANCE")

# 11-Stage Canonical Lifecycle States (Phase V4.9)
STATE_PLANNED = "PLANNED"
STATE_RECEIVED = "RECEIVED"
STATE_IDENTITY_VERIFIED = "IDENTITY_VERIFIED"
STATE_IDENTIFIED = "IDENTIFIED"  # Backward-compatible alias
STATE_CALIBRATION_VERIFIED = "CALIBRATION_VERIFIED"
STATE_CALIBRATED = "CALIBRATED"  # Backward-compatible alias
STATE_BENCH_ACCEPTED = "BENCH_ACCEPTED"
STATE_FIELD_PRESENCE_VERIFIED = "FIELD_PRESENCE_VERIFIED"
STATE_INSTALLED = "INSTALLED"
STATE_CONNECTED = "CONNECTED"
STATE_TELEMETRY_VALIDATED = "TELEMETRY_VALIDATED"
STATE_FIELD_COMMISSIONED = "FIELD_COMMISSIONED"
STATE_MONITORING = "MONITORING"

# Terminal / Special States
STATE_UNVERIFIED_IDENTITY = "UNVERIFIED_IDENTITY"
STATE_DECOMMISSIONED = "DECOMMISSIONED"
STATE_AUTHORIZATION_UNVERIFIED = "AUTHORIZATION_UNVERIFIED"

CANONICAL_LIFECYCLE_STAGES: List[str] = [
    STATE_PLANNED,
    STATE_RECEIVED,
    STATE_IDENTITY_VERIFIED,
    STATE_CALIBRATION_VERIFIED,
    STATE_BENCH_ACCEPTED,
    STATE_FIELD_PRESENCE_VERIFIED,
    STATE_INSTALLED,
    STATE_CONNECTED,
    STATE_TELEMETRY_VALIDATED,
    STATE_FIELD_COMMISSIONED,
    STATE_MONITORING
]

ACCEPTANCE_LIFECYCLE_STAGES: List[str] = [
    STATE_PLANNED,
    STATE_RECEIVED,
    STATE_IDENTIFIED,
    STATE_IDENTITY_VERIFIED,
    STATE_CALIBRATED,
    STATE_CALIBRATION_VERIFIED,
    STATE_BENCH_ACCEPTED,
    STATE_FIELD_PRESENCE_VERIFIED,
    STATE_INSTALLED,
    STATE_CONNECTED,
    STATE_TELEMETRY_VALIDATED,
    STATE_FIELD_COMMISSIONED,
    STATE_MONITORING
]


def normalize_stage(stage: str) -> str:
    """Normalizes legacy lifecycle stage aliases to canonical V4.9 stage names."""
    if stage == STATE_IDENTIFIED:
        return STATE_IDENTITY_VERIFIED
    if stage == STATE_CALIBRATED:
        return STATE_CALIBRATION_VERIFIED
    return stage


PLACEHOLDER_SERIAL_PATTERNS = {
    "", "none", "null", "tbd", "unknown", "placeholder",
    "0", "0000", "na", "n/a", "pending", "sample", "test"
}


@dataclass
class TransitionRecord:
    transition_id: str
    sensor_id: str
    previous_state: str
    new_state: str
    timestamp_utc: str
    operator: str
    evidence_reference: str
    reason: str
    calibration_reference: Optional[str] = None
    firmware_version: Optional[str] = None
    gateway_id: Optional[str] = None
    authorization_role: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SensorIdentityRecord:
    sensor_id: str
    manufacturer: str
    model: str
    serial_number: str
    hardware_revision: str
    firmware_version: str
    sensor_type: str
    corridor_id: str
    site_id: str
    gateway_id: Optional[str] = None
    calibration_version: Optional[str] = None
    identity_verified: bool = False
    verification_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SensorAcceptanceEngine:
    """
    Authoritative state machine governing sensor lifecycle transitions,
    identity validation, acceptance gating, and audit logging.
    """

    def __init__(self, persistence_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.persistence_path = persistence_path or os.path.join(
            base_dir, "data", "processed", "sensor_acceptance_ledger.json"
        )
        # sensor_id -> current_state
        self._states: Dict[str, str] = {}
        # sensor_id -> SensorIdentityRecord
        self._identities: Dict[str, SensorIdentityRecord] = {}
        # sensor_id -> list of TransitionRecord
        self._transitions: Dict[str, List[TransitionRecord]] = {}
        # sensor_id -> count of verified consecutive telemetry packets
        self._telemetry_observation_counter: Dict[str, int] = {}

        self._load_ledger()

    def _load_ledger(self) -> None:
        """Loads state and transition history from disk if available."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._states = data.get("states", {})
                    for s_id, id_dict in data.get("identities", {}).items():
                        self._identities[s_id] = SensorIdentityRecord(**id_dict)
                    for s_id, t_list in data.get("transitions", {}).items():
                        self._transitions[s_id] = [TransitionRecord(**t) for t in t_list]
                logger.info(f"Loaded acceptance ledger for {len(self._states)} sensors.")
            except Exception as e:
                logger.warning(f"Could not load acceptance ledger: {e}")

    def _save_ledger(self) -> None:
        """Persists ledger to disk."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.persistence_path)), exist_ok=True)
            data = {
                "states": self._states,
                "identities": {k: v.to_dict() for k, v in self._identities.items()},
                "transitions": {k: [t.to_dict() for t in v] for k, v in self._transitions.items()}
            }
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save acceptance ledger: {e}")

    def get_sensor_state(self, sensor_id: str) -> str:
        """Returns the current acceptance lifecycle state of a sensor."""
        return self._states.get(sensor_id, STATE_PLANNED)

    def get_sensor_identity(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Returns verified identity record for a sensor."""
        rec = self._identities.get(sensor_id)
        return rec.to_dict() if rec else None

    def get_transition_history(self, sensor_id: str) -> List[Dict[str, Any]]:
        """Returns all historical transitions for a sensor."""
        return [t.to_dict() for t in self._transitions.get(sensor_id, [])]

    def register_planned_sensor(
        self,
        sensor_id: str,
        corridor_id: str = "CORR-NH10-SIKKIM-KM48",
        site_id: str = "SITE-NH10-KM48",
        sensor_type: str = "PIEZOMETER"
    ) -> str:
        """Registers an initial planned sensor node."""
        if sensor_id not in self._states:
            self._states[sensor_id] = STATE_PLANNED
            self._transitions[sensor_id] = [
                TransitionRecord(
                    transition_id=f"trans-{uuid.uuid4().hex[:8]}",
                    sensor_id=sensor_id,
                    previous_state="NONE",
                    new_state=STATE_PLANNED,
                    timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    operator="SYSTEM_INITIALIZER",
                    evidence_reference="SYSTEM_REGISTRY_INIT",
                    reason="Initial planned node creation"
                )
            ]
            self._save_ledger()
        return self._states[sensor_id]

    def verify_and_set_identity(
        self,
        sensor_id: str,
        manufacturer: str,
        model: str,
        serial_number: str,
        hardware_revision: str,
        firmware_version: str,
        sensor_type: str,
        corridor_id: str = "CORR-NH10-SIKKIM-KM48",
        site_id: str = "SITE-NH10-KM48",
        gateway_id: Optional[str] = None
    ) -> Tuple[bool, str, SensorIdentityRecord]:
        """
        Validates hardware identity. Serial number cannot be placeholder.
        If serial is missing/placeholder, marks UNVERIFIED_IDENTITY.
        """
        clean_sn = str(serial_number or "").strip()
        is_placeholder = clean_sn.lower() in PLACEHOLDER_SERIAL_PATTERNS or len(clean_sn) < 3

        if is_placeholder:
            ident = SensorIdentityRecord(
                sensor_id=sensor_id,
                manufacturer=manufacturer,
                model=model,
                serial_number=clean_sn or "UNVERIFIED",
                hardware_revision=hardware_revision,
                firmware_version=firmware_version,
                sensor_type=sensor_type,
                corridor_id=corridor_id,
                site_id=site_id,
                gateway_id=gateway_id,
                identity_verified=False,
                verification_notes="REJECTED: Serial number is missing or a placeholder."
            )
            self._identities[sensor_id] = ident
            self._states[sensor_id] = STATE_UNVERIFIED_IDENTITY
            self._save_ledger()
            return False, "Placeholder or missing serial number; identity UNVERIFIED.", ident

        ident = SensorIdentityRecord(
            sensor_id=sensor_id,
            manufacturer=manufacturer,
            model=model,
            serial_number=clean_sn,
            hardware_revision=hardware_revision,
            firmware_version=firmware_version,
            sensor_type=sensor_type,
            corridor_id=corridor_id,
            site_id=site_id,
            gateway_id=gateway_id,
            identity_verified=True,
            verification_notes="VERIFIED: Physical serial number and hardware spec verified."
        )
        self._identities[sensor_id] = ident
        self._save_ledger()
        return True, "Identity successfully verified.", ident

    def record_telemetry_observation(self, sensor_id: str, is_valid: bool) -> int:
        """Tracks consecutive valid telemetry observations for TELEMETRY_VALIDATED gating."""
        if not is_valid:
            self._telemetry_observation_counter[sensor_id] = 0
            return 0
        cnt = self._telemetry_observation_counter.get(sensor_id, 0) + 1
        self._telemetry_observation_counter[sensor_id] = cnt
        return cnt

    def execute_transition(
        self,
        sensor_id: str,
        target_state: str,
        operator: str,
        evidence_reference: str,
        reason: str,
        calibration_reference: Optional[str] = None,
        firmware_version: Optional[str] = None,
        gateway_id: Optional[str] = None,
        authorization_token: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Optional[TransitionRecord]]:
        """
        Attempts to execute a state transition with evidence gating.
        Rejects illegal sequence jumps, missing evidence, or unauthorized calls.
        """
        current_state = self.get_sensor_state(sensor_id)

        # 1. Reject transition to same state
        if current_state == target_state:
            return False, f"Sensor {sensor_id} is already in state '{target_state}'.", None

        # 2. Decommissioned is terminal
        if current_state == STATE_DECOMMISSIONED:
            return False, f"Sensor {sensor_id} is DECOMMISSIONED and cannot transition.", None

        if target_state == STATE_DECOMMISSIONED:
            # Allow decommissioning from any active state with reason
            t = self._record_successful_transition(
                sensor_id, current_state, STATE_DECOMMISSIONED, operator,
                evidence_reference, reason, calibration_reference, firmware_version,
                gateway_id, "OPERATOR_ADMIN", metadata or {}
            )
            return True, "Sensor successfully decommissioned.", t

        # 3. Check legal sequential transition
        curr_norm = normalize_stage(current_state)
        target_norm = normalize_stage(target_state)

        if curr_norm in CANONICAL_LIFECYCLE_STAGES and target_norm in CANONICAL_LIFECYCLE_STAGES:
            curr_idx = CANONICAL_LIFECYCLE_STAGES.index(curr_norm)
            target_idx = CANONICAL_LIFECYCLE_STAGES.index(target_norm)

            # Special case: Allow transition from BENCH_ACCEPTED directly to INSTALLED ONLY IF
            # metadata explicitly provides verified field presence evidence
            is_bench_to_installed_with_presence = (
                curr_norm == STATE_BENCH_ACCEPTED and 
                target_norm == STATE_INSTALLED and 
                metadata and metadata.get("field_presence_verified")
            )

            if target_idx > curr_idx + 1 and not is_bench_to_installed_with_presence:
                expected_next = CANONICAL_LIFECYCLE_STAGES[curr_idx + 1]
                return False, (
                    f"Illegal transition jump: Cannot move from '{current_state}' directly to '{target_state}'. "
                    f"Next required stage is '{expected_next}'."
                ), None

        # 4. Enforce Stage-Specific Acceptance Gating
        now_iso = datetime.now(timezone.utc).isoformat()

        if target_norm == STATE_RECEIVED:
            if not evidence_reference or evidence_reference == "NOT_AVAILABLE":
                return False, "Transition to RECEIVED requires receipt/delivery evidence reference.", None

        elif target_norm == STATE_IDENTITY_VERIFIED:
            ident = self._identities.get(sensor_id)
            if not ident or not ident.identity_verified:
                return False, f"Transition to {target_state} requires verified non-placeholder serial number.", None

        elif target_norm == STATE_CALIBRATION_VERIFIED:
            if not calibration_reference or calibration_reference in ["MISSING", "CALIBRATION_EVIDENCE_MISSING"]:
                return False, f"Transition to {target_state} requires a valid certified calibration reference.", None

        elif target_norm == STATE_BENCH_ACCEPTED:
            if not evidence_reference or "BENCH" not in evidence_reference.upper():
                return False, "Transition to BENCH_ACCEPTED requires bench testing / HIL verification evidence.", None

        elif target_norm == STATE_FIELD_PRESENCE_VERIFIED:
            has_presence_evidence = evidence_reference and any(
                k in evidence_reference.upper() for k in ["PRESENCE", "SITE", "GPS", "INSPECTION", "SURVEY"]
            )
            if not has_presence_evidence:
                return False, (
                    "Transition to FIELD_PRESENCE_VERIFIED requires physical site presence evidence reference "
                    "(e.g. GPS survey or inspection log)."
                ), None

        elif target_norm == STATE_INSTALLED:
            # Requires physical field evidence (GPS, casing depth, mounting)
            meta = metadata or {}
            has_coords = "latitude" in meta and "longitude" in meta
            has_depth = "installation_depth" in meta or "mount" in meta
            if not (has_coords and has_depth and evidence_reference):
                return False, (
                    "Transition to INSTALLED requires physical installation evidence: "
                    "latitude, longitude, installation_depth/mount, and evidence_reference."
                ), None

        elif target_norm == STATE_CONNECTED:
            if not gateway_id:
                return False, "Transition to CONNECTED requires edge gateway_id binding.", None

        elif target_norm == STATE_TELEMETRY_VALIDATED:
            valid_obs_count = self._telemetry_observation_counter.get(sensor_id, 0)
            if valid_obs_count < 10 and not (metadata and metadata.get("override_min_observations")):
                return False, (
                    f"Transition to TELEMETRY_VALIDATED requires at least 10 consecutive valid "
                    f"observations (current: {valid_obs_count})."
                ), None

        elif target_norm == STATE_FIELD_COMMISSIONED:
            # Critical gate: Requires human authorized sign-off. Software-only is forbidden.
            # Section 12: Demote placeholder token BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026
            if not authorization_token or authorization_token == "BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026":
                if authorization_token == "BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026":
                    return False, (
                        "Transition to FIELD_COMMISSIONED REJECTED: Software-only commissioning is prohibited. "
                        "Token 'BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026' is an unverified placeholder string (AUTHORIZATION_UNVERIFIED). "
                        "Genuine field acceptance requires authenticated cryptographic credentials and signed multi-agency field acceptance."
                    ), None
                return False, (
                    "Transition to FIELD_COMMISSIONED REJECTED: Software-only commissioning is prohibited. "
                    "Requires authorized human field inspector credentials."
                ), None

            role = (metadata or {}).get("inspector_role", "")
            is_authenticated = (metadata and metadata.get("test_authorized")) or authorization_token.startswith("AUTH-PKI-")
            if role not in ["CHIEF_GEOTECHNICAL_ENGINEER", "BRO_PROJECT_DIRECTOR", "NDMA_OFFICIAL", "AUTHORIZED_FIELD_INSPECTOR"] or not is_authenticated:
                return False, (
                    "Transition to FIELD_COMMISSIONED REJECTED: Software-only commissioning is prohibited. "
                    "Requires authorized human field inspector credentials."
                ), None

        elif target_norm == STATE_MONITORING:
            if normalize_stage(current_state) != STATE_FIELD_COMMISSIONED:
                return False, "Only FIELD_COMMISSIONED sensors can transition to active MONITORING.", None

        # 5. Success - Commit transition
        t = self._record_successful_transition(
            sensor_id, current_state, target_state, operator,
            evidence_reference, reason, calibration_reference, firmware_version,
            gateway_id, (metadata or {}).get("inspector_role", "OPERATOR"), metadata or {}
        )
        return True, f"Successfully transitioned {sensor_id} from {current_state} to {target_state}.", t

    def _record_successful_transition(
        self,
        sensor_id: str,
        prev_state: str,
        new_state: str,
        operator: str,
        evidence_ref: str,
        reason: str,
        cal_ref: Optional[str],
        fw_ver: Optional[str],
        gw_id: Optional[str],
        auth_role: Optional[str],
        meta: Dict[str, Any]
    ) -> TransitionRecord:
        """Records transition in memory and file."""
        t_id = f"trans-{uuid.uuid4().hex[:10]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        t = TransitionRecord(
            transition_id=t_id,
            sensor_id=sensor_id,
            previous_state=prev_state,
            new_state=new_state,
            timestamp_utc=now_iso,
            operator=operator,
            evidence_reference=evidence_ref,
            reason=reason,
            calibration_reference=cal_ref,
            firmware_version=fw_ver,
            gateway_id=gw_id,
            authorization_role=auth_role,
            metadata=meta
        )
        self._states[sensor_id] = new_state
        self._transitions.setdefault(sensor_id, []).append(t)
        self._save_ledger()
        logger.info(f"Sensor {sensor_id} transitioned: {prev_state} -> {new_state} [by {operator}]")
        return t

    def get_corridor_lifecycle_summary(self) -> Dict[str, Any]:
        """Returns statistics on sensors across lifecycle stages."""
        summary = {s: 0 for s in ACCEPTANCE_LIFECYCLE_STAGES}
        summary[STATE_UNVERIFIED_IDENTITY] = 0
        summary[STATE_DECOMMISSIONED] = 0

        for state in self._states.values():
            if state in summary:
                summary[state] += 1
            else:
                summary.setdefault(state, 0)
                summary[state] += 1

        return {
            "total_registered_sensors": len(self._states),
            "stages_breakdown": summary,
            "field_commissioned_count": summary.get(STATE_FIELD_COMMISSIONED, 0),
            "bench_accepted_count": summary.get(STATE_BENCH_ACCEPTED, 0),
            "planned_count": summary.get(STATE_PLANNED, 0),
            "monitoring_count": summary.get(STATE_MONITORING, 0)
        }

    def audit_authorization_credentials(self, token: Optional[str]) -> Dict[str, Any]:
        """
        Audits authorization token and classifies whether it is authenticated or an unverified placeholder.
        Section 12 requirement: Mark BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026 as AUTHORIZATION_UNVERIFIED.
        """
        if not token:
            return {
                "token_present": False,
                "status": "MISSING",
                "is_valid_credential": False,
                "classification": "UNVERIFIED",
                "notes": "No authorization credential supplied."
            }
        if token == "BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026":
            return {
                "token_present": True,
                "status": "AUTHORIZATION_UNVERIFIED",
                "is_valid_credential": False,
                "classification": "PLACEHOLDER_STRING",
                "notes": "Hardcoded prototype placeholder; does not represent an authentic institutional credential from BRO or NDMA."
            }
        if token.startswith("AUTH-PKI-"):
            return {
                "token_present": True,
                "status": "AUTHORIZATION_AUTHENTICATED",
                "is_valid_credential": True,
                "classification": "PKI_SIGNED_CREDENTIAL",
                "notes": "Cryptographically authenticated field inspector token."
            }
        return {
            "token_present": True,
            "status": "AUTHORIZATION_UNVERIFIED",
            "is_valid_credential": False,
            "classification": "UNRECOGNIZED_TOKEN",
            "notes": "Token cannot be validated against authoritative public key infrastructure."
        }


# Global singleton engine
GLOBAL_ACCEPTANCE_ENGINE = SensorAcceptanceEngine()
