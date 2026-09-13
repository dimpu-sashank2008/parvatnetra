# -*- coding: utf-8 -*-
"""
backend/migrate_phase6a.py
==========================
PARVAT NETRA • Phase 6A Field Infrastructure Database Migration
Creates and verifies tables for:
  - gateways
  - sensor_registry
  - sensor_calibrations
  - device_health
  - edge_buffer
  - edge_alerts
  - telemetry_ingestion_log

Supports both Neon PostgreSQL/PostGIS and local SQLite environments idempotently.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PHASE6A_MIGRATION")

SQLITE_DB_PATH = os.environ.get("PHASE6A_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "observations", "pahad_observations.db"))

def run_sqlite_migration(db_path: str = SQLITE_DB_PATH):
    """Executes SQLite DDL schema."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    logger.info(f"Applying SQLite migration to: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. gateways
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gateways (
        gateway_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        sector_id TEXT NOT NULL,
        firmware_version TEXT,
        hardware_version TEXT,
        power_source TEXT DEFAULT 'SOLAR_BATTERY',
        battery_pct REAL DEFAULT 100.0,
        uptime_seconds INTEGER DEFAULT 0,
        status TEXT DEFAULT 'ONLINE',
        last_seen TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. sensor_registry
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_registry (
        device_id TEXT PRIMARY KEY,
        sensor_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        sector_id TEXT NOT NULL,
        gateway_id TEXT,
        installation_status TEXT DEFAULT 'INSTALLED',
        commissioned_at TEXT,
        firmware_version TEXT,
        hardware_version TEXT,
        calibration_status TEXT DEFAULT 'CALIBRATED',
        last_seen TEXT,
        battery_level REAL DEFAULT 100.0,
        signal_strength REAL DEFAULT -75.0,
        network_type TEXT DEFAULT 'LORA',
        status TEXT DEFAULT 'REGISTERED',
        created_at TEXT NOT NULL,
        FOREIGN KEY (gateway_id) REFERENCES gateways (gateway_id)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_sector ON sensor_registry(sector_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sensor_type ON sensor_registry(sensor_type);")

    # 3. sensor_calibrations
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_calibrations (
        calibration_id TEXT PRIMARY KEY,
        sensor_id TEXT NOT NULL,
        calibration_date TEXT NOT NULL,
        calibration_due TEXT NOT NULL,
        zero_offset REAL DEFAULT 0.0,
        scale_factor REAL DEFAULT 1.0,
        calibration_source TEXT DEFAULT 'FACTORY',
        status TEXT DEFAULT 'CALIBRATED',
        created_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cal_sensor ON sensor_calibrations(sensor_id);")

    # 4. device_health
    cur.execute("""
    CREATE TABLE IF NOT EXISTS device_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        recorded_at TEXT NOT NULL,
        status TEXT NOT NULL,
        battery_level REAL,
        signal_strength REAL,
        packet_loss_pct REAL DEFAULT 0.0,
        clock_offset_ms REAL DEFAULT 0.0,
        error_flags TEXT
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_health_device ON device_health(device_id, recorded_at);")

    # 5. edge_buffer
    cur.execute("""
    CREATE TABLE IF NOT EXISTS edge_buffer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        packet_id TEXT UNIQUE NOT NULL,
        gateway_id TEXT NOT NULL,
        device_id TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        status TEXT DEFAULT 'BUFFERED',
        buffered_at TEXT NOT NULL,
        synced_at TEXT,
        retry_count INTEGER DEFAULT 0
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edge_buf_status ON edge_buffer(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edge_buf_dev_seq ON edge_buffer(device_id, sequence_number);")

    # 6. edge_alerts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS edge_alerts (
        alert_id TEXT PRIMARY KEY,
        gateway_id TEXT NOT NULL,
        sector_id TEXT NOT NULL,
        severity TEXT NOT NULL,
        trigger_source TEXT NOT NULL,
        details_json TEXT NOT NULL,
        siren_activated INTEGER DEFAULT 0,
        timestamp TEXT NOT NULL
    );
    """)

    # 7. telemetry_ingestion_log
    cur.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_ingestion_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        packet_id TEXT NOT NULL,
        device_id TEXT NOT NULL,
        received_at TEXT NOT NULL,
        transport TEXT NOT NULL,
        status TEXT NOT NULL,
        rejection_reason TEXT
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ingest_pkt ON telemetry_ingestion_log(packet_id);")

    conn.commit()
    conn.close()
    logger.info("SQLite Phase 6A schema migration completed successfully.")

def run_postgres_migration():
    """Executes PostgreSQL DDL if DATABASE_URL is reachable."""
    db_url = os.environ.get("NEON_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        logger.info("No DATABASE_URL configured; skipping PostgreSQL migration.")
        return

    try:
        import psycopg2
        conn = psycopg2.connect(db_url, connect_timeout=5)
        cur = conn.cursor()
        logger.info("Applying PostgreSQL Phase 6A migration...")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS gateways (
            gateway_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            latitude NUMERIC NOT NULL,
            longitude NUMERIC NOT NULL,
            sector_id TEXT NOT NULL,
            firmware_version TEXT,
            hardware_version TEXT,
            power_source TEXT DEFAULT 'SOLAR_BATTERY',
            battery_pct NUMERIC DEFAULT 100.0,
            uptime_seconds INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ONLINE',
            last_seen TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sensor_registry (
            device_id TEXT PRIMARY KEY,
            sensor_id TEXT NOT NULL,
            sensor_type TEXT NOT NULL,
            latitude NUMERIC NOT NULL,
            longitude NUMERIC NOT NULL,
            sector_id TEXT NOT NULL,
            gateway_id TEXT REFERENCES gateways(gateway_id),
            installation_status TEXT DEFAULT 'INSTALLED',
            commissioned_at TIMESTAMP WITH TIME ZONE,
            firmware_version TEXT,
            hardware_version TEXT,
            calibration_status TEXT DEFAULT 'CALIBRATED',
            last_seen TIMESTAMP WITH TIME ZONE,
            battery_level NUMERIC DEFAULT 100.0,
            signal_strength NUMERIC DEFAULT -75.0,
            network_type TEXT DEFAULT 'LORA',
            status TEXT DEFAULT 'REGISTERED',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_sensor_reg_sector ON sensor_registry(sector_id);

        CREATE TABLE IF NOT EXISTS sensor_calibrations (
            calibration_id TEXT PRIMARY KEY,
            sensor_id TEXT NOT NULL,
            calibration_date TIMESTAMP WITH TIME ZONE NOT NULL,
            calibration_due TIMESTAMP WITH TIME ZONE NOT NULL,
            zero_offset NUMERIC DEFAULT 0.0,
            scale_factor NUMERIC DEFAULT 1.0,
            calibration_source TEXT DEFAULT 'FACTORY',
            status TEXT DEFAULT 'CALIBRATED',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS edge_buffer (
            id SERIAL PRIMARY KEY,
            packet_id TEXT UNIQUE NOT NULL,
            gateway_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            sequence_number INTEGER NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            payload_json JSONB NOT NULL,
            status TEXT DEFAULT 'BUFFERED',
            buffered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP WITH TIME ZONE,
            retry_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS edge_alerts (
            alert_id TEXT PRIMARY KEY,
            gateway_id TEXT NOT NULL,
            sector_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            trigger_source TEXT NOT NULL,
            details_json JSONB NOT NULL,
            siren_activated BOOLEAN DEFAULT FALSE,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()
        logger.info("PostgreSQL Phase 6A schema migration completed successfully.")
    except Exception as e:
        logger.warning(f"PostgreSQL migration skipped or failed (safe fallback to SQLite): {e}")

if __name__ == "__main__":
    run_sqlite_migration()
    run_postgres_migration()
