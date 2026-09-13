# -*- coding: utf-8 -*-
"""
engine/observation_store.py
============================
PAHAD AI — Persistent Continuous Observation Store (Phase 5C)
--------------------------------------------------------------
SQLite-backed store for all incoming environmental observations.
Designed to handle millions of rows without loading everything into memory.

Schema per observation:
  id          : auto-increment primary key
  sector_id   : GSI sector identifier
  timestamp   : ISO 8601 observation time
  feature     : feature name (rain_1h, pore_pressure, etc.)
  value       : float or NULL
  unit        : measurement unit string
  source      : data provider name
  quality     : GOOD / DEGRADED / SUSPECT / MISSING
  provenance  : LIVE / CACHED / AUTH_REQUIRED / UNAVAILABLE / MODELLED
  ingested_at : ISO 8601 ingestion time
  extra       : JSON blob for additional metadata

Indices:
  (sector_id, timestamp) — for sector time-series queries
  (feature, timestamp)   — for cross-sector feature queries

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import json
import sqlite3
import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("PAHAD_OBSERVATION_STORE")

OBSERVATION_DB_PATH = os.getenv(
    "OBSERVATION_DB_PATH",
    "data/observations/pahad_observations.db"
)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS observations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_id   TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL,
    feature     TEXT    NOT NULL,
    value       REAL,
    unit        TEXT    DEFAULT '',
    source      TEXT    DEFAULT '',
    quality     TEXT    DEFAULT 'UNKNOWN',
    provenance  TEXT    DEFAULT 'UNKNOWN',
    ingested_at TEXT    NOT NULL,
    extra       TEXT
);
"""

_CREATE_IDX_SECTOR_TS = """
CREATE INDEX IF NOT EXISTS idx_sector_ts
    ON observations(sector_id, timestamp);
"""

_CREATE_IDX_SOURCE_TS = """
CREATE INDEX IF NOT EXISTS idx_source_ts
    ON observations(source, timestamp);
"""

_CREATE_IDX_FEATURE = """
CREATE INDEX IF NOT EXISTS idx_feature
    ON observations(feature, timestamp);
"""

_CREATE_IDX_UNIQUE = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_sector_ts_feature_unique
    ON observations(sector_id, timestamp, feature);
"""

_UPSERT_SQL = """
INSERT INTO observations
    (sector_id, timestamp, feature, value, unit, source, quality, provenance, ingested_at, extra)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT DO NOTHING;
"""


@dataclass
class ObservationRecord:
    """A single structured sensor/model observation."""
    sector_id: str
    timestamp: str           # ISO 8601 observation time
    feature: str             # e.g. 'rain_1h', 'pore_pressure', 'fos'
    value: Optional[float]
    unit: str = ""
    source: str = ""
    quality: str = "UNKNOWN"
    provenance: str = "UNKNOWN"
    ingested_at: str = ""
    extra: Optional[Dict[str, Any]] = None
    id: Optional[int] = None  # set after insert

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sector_id": self.sector_id,
            "timestamp": self.timestamp,
            "feature": self.feature,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "quality": self.quality,
            "provenance": self.provenance,
            "ingested_at": self.ingested_at,
            "extra": self.extra,
        }


class ObservationStore:
    """
    Thread-safe persistent SQLite store for environmental observations.

    Operations:
      insert()                  — insert a single observation (idempotent)
      insert_many()             — batch insert
      get_latest()              — most recent N records for sector+feature
      get_history()             — time-range query
      get_latest_by_sector()    — latest observation per feature for a sector
      count()                   — total records, optionally filtered

    All operations acquire a threading.Lock before any SQLite access.
    """

    def __init__(self, db_path: str = OBSERVATION_DB_PATH) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        # Create parent directory eagerly
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Initialize schema on first construction
        conn = self._connect()
        conn.execute(_CREATE_TABLE_SQL)
        conn.execute(_CREATE_IDX_SECTOR_TS)
        conn.execute(_CREATE_IDX_SOURCE_TS)
        conn.execute(_CREATE_IDX_FEATURE)
        try:
            conn.execute(_CREATE_IDX_UNIQUE)
        except sqlite3.IntegrityError:
            conn.execute("""
                DELETE FROM observations
                WHERE id NOT IN (
                    SELECT MIN(id) FROM observations GROUP BY sector_id, timestamp, feature
                )
            """)
            conn.execute(_CREATE_IDX_UNIQUE)
        conn.commit()
        logger.info(f"[OBS-STORE] Initialized at {db_path}")

    def _connect(self) -> sqlite3.Connection:
        """Return persistent connection (lazy init). Thread-safe via lock."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0
            )
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _row_to_record(self, row: sqlite3.Row) -> ObservationRecord:
        extra_str = row["extra"]
        extra = json.loads(extra_str) if extra_str else None
        return ObservationRecord(
            id=row["id"],
            sector_id=row["sector_id"],
            timestamp=row["timestamp"],
            feature=row["feature"],
            value=row["value"],
            unit=row["unit"] or "",
            source=row["source"] or "",
            quality=row["quality"] or "UNKNOWN",
            provenance=row["provenance"] or "UNKNOWN",
            ingested_at=row["ingested_at"],
            extra=extra
        )

    def insert(self, record: ObservationRecord) -> int:
        """
        Insert a single observation.  Idempotent: same sector+timestamp+feature
        is silently ignored (ON CONFLICT DO NOTHING).
        Returns the new row id or 0 if duplicate.
        """
        ingested_at = record.ingested_at or datetime.now(timezone.utc).isoformat()
        extra_str = json.dumps(record.extra) if record.extra else None

        with self._lock:
            conn = self._connect()
            cur = conn.execute(_UPSERT_SQL, (
                record.sector_id,
                record.timestamp,
                record.feature,
                record.value,
                record.unit,
                record.source,
                record.quality,
                record.provenance,
                ingested_at,
                extra_str
            ))
            conn.commit()
            rowid = cur.lastrowid or 0
        return rowid

    def insert_many(self, records: List[ObservationRecord]) -> int:
        """Batch insert. Returns count of rows inserted."""
        if not records:
            return 0
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        for r in records:
            rows.append((
                r.sector_id,
                r.timestamp,
                r.feature,
                r.value,
                r.unit,
                r.source,
                r.quality,
                r.provenance,
                r.ingested_at or now,
                json.dumps(r.extra) if r.extra else None
            ))
        with self._lock:
            conn = self._connect()
            conn.executemany(_UPSERT_SQL, rows)
            conn.commit()
        return len(rows)

    def get_latest(
        self,
        sector_id: str,
        feature: str,
        limit: int = 1
    ) -> List[ObservationRecord]:
        """Return the most recent observations for a sector+feature pair."""
        sql = """
            SELECT * FROM observations
            WHERE sector_id = ? AND feature = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        with self._lock:
            conn = self._connect()
            rows = conn.execute(sql, (sector_id, feature, limit)).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_history(
        self,
        sector_id: str,
        feature: str,
        since_iso: str,
        limit: int = 100
    ) -> List[ObservationRecord]:
        """Return observations for sector+feature after since_iso, newest first."""
        sql = """
            SELECT * FROM observations
            WHERE sector_id = ? AND feature = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        with self._lock:
            conn = self._connect()
            rows = conn.execute(sql, (sector_id, feature, since_iso, limit)).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_latest_by_sector(
        self,
        sector_id: str,
        max_age_seconds: float = 3600.0
    ) -> Dict[str, ObservationRecord]:
        """
        Return the latest observation per feature for a given sector.
        Only includes observations within max_age_seconds of now.

        Returns: dict mapping feature_name -> ObservationRecord
        """
        from datetime import timedelta
        cutoff = (
            datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        ).isoformat()

        sql = """
            SELECT * FROM observations
            WHERE sector_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        """
        with self._lock:
            conn = self._connect()
            rows = conn.execute(sql, (sector_id, cutoff)).fetchall()

        # Build dict keeping only the latest per feature
        result: Dict[str, ObservationRecord] = {}
        for row in rows:
            rec = self._row_to_record(row)
            if rec.feature not in result:
                result[rec.feature] = rec
        return result

    def count(self, sector_id: Optional[str] = None) -> int:
        """Return total observation count, optionally filtered by sector."""
        with self._lock:
            conn = self._connect()
            if sector_id:
                row = conn.execute(
                    "SELECT COUNT(*) FROM observations WHERE sector_id = ?",
                    (sector_id,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) FROM observations").fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
        logger.info("[OBS-STORE] Connection closed.")


# Global singleton — uses the configured path
GLOBAL_OBSERVATION_STORE = ObservationStore()
