# PAHAD AI — MCP Integration Status

**Document**: `MCP_INTEGRATION_STATUS.md`
**Phase**: Phase 5C — Real Data Connectors & Continuous Live Operations
**Date**: 2026-09-10
**Classification**: Infrastructure & DevOps

---

## Overview

This document catalogues the Model Context Protocol (MCP) servers available in the PARVAT NETRA development environment and their relevance to PAHAD AI live operations.

> [!IMPORTANT]
> MCP servers are **development infrastructure tools**. They do NOT provide live environmental sensor data (seismic, rainfall, landslide telemetry). All real-world observation data must originate from IMD, NCS, USGS, Open-Meteo, or deployed field hardware.

---

## MCP Server Inventory

| MCP | PURPOSE | CONNECTED | USED FOR | LIMITATIONS |
|-----|---------|-----------|----------|-------------|
| `neon-mcp-server` | Neon PostgreSQL DB management | YES (`DATABASE_URL` configured) | Schema inspection, query validation, PostGIS audit | Development & DB inspection only; not for live IoT sensor feeds |
| `firebase-mcp-server` | Firebase project, auth, Firestore | YES (dev environment) | Auth rule validation, SDK configuration | Development tool; does not provide real-time landslide telemetry |
| `chrome-devtools-mcp` | Browser automation and inspection | YES (local Chrome target) | Frontend E2E testing, accessibility auditing | Dev/test only; does not provide environmental sensor data |
| `github-mcp-server` | GitHub repository operations | YES (repo workspace) | Issue tracking, PR reviews, release management | Codebase & repository operations only |
| `sequential-thinking` | Structured multi-step reasoning | YES (in-agent tool) | System design planning and safety invariant auditing | Reasoning tool only; has no external network access |
| `gemini-api-docs` | Google Gemini API documentation | YES (eager documentation server) | SDK reference and API schema lookup | Documentation search only; does not perform telemetry ingestion |

---

## Live Data Sources (NOT MCP)

The following external APIs provide actual environmental observations for PAHAD AI. These are called directly via HTTP, **not through MCP**:

| SOURCE | TYPE | AUTH | ENDPOINT |
|--------|------|------|----------|
| Open-Meteo | Weather/precipitation | None (public) | `https://api.open-meteo.com/v1/forecast` |
| USGS FDSNws | Seismic events | None (public) | `https://earthquake.usgs.gov/fdsnws/event/1/query` |
| IMD Nowcast | Official weather | `AUTH_REQUIRED` | Set `IMD_API_BASE_URL` in .env |
| NCS Seismology | Official seismic | `AUTH_REQUIRED` | Set `NCS_API_BASE_URL` in .env |
| Copernicus CDSE | SAR/Optical catalogue | Partial (search free) | `https://catalogue.dataspace.copernicus.eu` |
| NRSC Bhoonidhi | CartoDEM / NDVI | `AUTH_REQUIRED` (MOU) | Set `BHOONIDHI_API_URL` in .env |

---

## Neon MCP Usage for PAHAD

The `neon-mcp-server` is the one MCP server with direct operational relevance:

- **DATABASE_URL**: Set in `.env` (Neon PostgreSQL on AWS)
- **Use cases**:
  - Inspect observation schema during development
  - Run migration queries for `observations` table if using Neon instead of local SQLite
  - Audit sector risk history stored in PostGIS

> [!NOTE]
> The `ObservationStore` (Phase 5C) defaults to local SQLite (`data/observations/pahad_observations.db`). To use Neon PostgreSQL instead, set `OBSERVATION_DB_PATH` and update the store to use `psycopg2` — this is a future migration task.

---

## Conclusion

```
MCP INTEGRATION VERDICT
═══════════════════════
Role in PAHAD AI: DEVELOPMENT INFRASTRUCTURE ONLY
Live sensor data: ❌ None provided by MCP
Database access : ✅ neon-mcp-server (Neon PostgreSQL)
Frontend testing: ✅ chrome-devtools-mcp
Repo management : ✅ github-mcp-server

The live data pipeline is entirely HTTP-based:
  Open-Meteo + USGS → operational today
  IMD + NCS → AUTH_REQUIRED (apply separately)
  IoT → hardware deployment needed
```
