---
name: backend-fastapi-postgis
description: >-
  Engineering guidelines for developing PARVAT NETRA's FastAPI backend and PostGIS spatial store.
  Use when writing API routes, SQLAlchemy/GeoAlchemy2 models, PostGIS spatial queries,
  ingestion workers, WebSocket/SSE alert dispatchers, or JWT authentication.
---

# PARVAT NETRA — FastAPI & PostGIS Backend Guide

The PARVAT NETRA backend provides high-performance, asynchronous ingestion, spatial querying, and evidence fusion endpoints.

---

## 1. Technology Foundation

- **Framework**: FastAPI (Python 3.11+)
- **ORM / Query Engine**: SQLAlchemy 2.0 (Async) + GeoAlchemy2
- **Database Driver**: `asyncpg`
- **Spatial Extensions**: PostGIS (`GEOMETRY(Point, 4326)`, `GEOMETRY(LineString, 4326)`, `GEOMETRY(Polygon, 4326)`)
- **Validation**: Pydantic v2
- **Real-Time Streaming**: Server-Sent Events (SSE) / WebSockets for live telemetry and emergency broadcasts

---

## 2. Recommended Backend Directory Layout

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # JWT login, registration & RBAC
│   │   │   │   ├── citizen.py       # Citizen localized risk & SOS reports
│   │   │   │   ├── authority.py     # Operations control room & dispatch
│   │   │   │   ├── routes.py        # Safe routes engine (Fastest/Shortest/Safest)
│   │   │   │   ├── telemetry.py     # Sensor & weather observations
│   │   │   │   └── incidents.py     # Incident lifecycle (A-17 scenario)
│   │   │   └── router.py
│   ├── core/
│   │   ├── config.py                # Pydantic Settings from .env
│   │   ├── database.py              # Async engine & session factory
│   │   └── security.py              # Password hashing & JWT verification
│   ├── models/                      # SQLAlchemy Declarative Models
│   │   ├── spatial.py               # Zones, exposure assets, road networks
│   │   ├── telemetry.py             # Sensor stations, readings, rainfall
│   │   └── operations.py            # Incidents, alerts, recovery tasks
│   ├── schemas/                     # Pydantic Request/Response DTOs
│   ├── services/                    # Business Logic & Fusion Engines
│   │   ├── physics_engine.py        # Factor of Safety calculation
│   │   ├── evidence_fusion.py       # Multimodal risk synthesis
│   │   ├── routing_engine.py        # Safe hazard-aware path finding
│   │   └── ingestion_service.py     # External API polling & normalizers
│   └── main.py                      # FastAPI app entry point
├── tests/
└── requirements.txt
```

---

## 3. PostGIS Model Definition Pattern

```python
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base

class SpatialZone(Base):
    __tablename__ = "spatial_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    slope_mean = Column(Float, nullable=False)
    geology_type = Column(String(50), nullable=False)
    # WGS84 Polygon geometry with spatial index
    geom = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
```

---

## 4. Operational Best Practices

1. **Keep Secrets in `.env`**: Never hardcode database connection strings, JWT keys, or API tokens.
2. **Handle Null Geometry**: All spatial endpoints must gracefully handle coordinates outside defined zones.
3. **Always Expose Provenance**: Every response object must include `"data_mode": "LIVE" | "SIMULATED" | "DEMO"`.
