# -*- coding: utf-8 -*-
"""
engine/geospatial_registry.py
=============================
PARVAT NETRA • Geospatial Data Asset Registry & Catalog
-------------------------------------------------------
Authoritative catalog tracking all terrain, satellite, vegetation,
and hazard layers influencing hillslope stability across the Northeast Region.

Tracks:
  - dataset_id, source, dataset_name, coverage, resolution
  - acquired_at, updated_at, status, provenance, local_path, checksum
  - explicit provenance states: [LIVE], [CACHED], [HISTORICAL], [SIMULATED], [DEMO], [DEGRADED]

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class GeospatialDatasetRecord:
    dataset_id: str
    source: str
    dataset_name: str
    category: str  # 'dem', 'vegetation', 'satellite', 'landslides', 'roads', 'anthropogenic', 'offline_package'
    coverage: str
    resolution: str
    acquired_at: str
    updated_at: str
    status: str  # 'AVAILABLE', 'CACHED', 'UPDATING', 'DEGRADED', 'UNAVAILABLE'
    provenance: str  # '[LIVE]', '[CACHED]', '[HISTORICAL]', '[SIMULATED]', '[DEMO]', '[DEGRADED]'
    local_path: Optional[str] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    name: Optional[str] = None
    version: str = "1.0.0"
    size: int = 45000
    created_at: Optional[str] = None
    download_available: bool = True
    installed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["name"] = self.name or self.dataset_name
        d["created_at"] = self.created_at or self.acquired_at
        d["version"] = self.version
        d["size"] = self.size
        d["download_available"] = self.download_available
        d["installed"] = self.installed
        if self.provenance:
            d["provenance"] = self.provenance
        return d


class GeospatialRegistry:
    """Central registry tracking geospatial intelligence datasets."""

    def __init__(self, data_root: Optional[str] = None) -> None:
        self.data_root = data_root or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "geospatial"
        )
        self._catalog: Dict[str, GeospatialDatasetRecord] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        """Initializes canonical authoritative datasets for the North-Eastern Region."""
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Digital Elevation Model (DEM)
        self.register(GeospatialDatasetRecord(
            dataset_id="DEM_COPERNICUS_30M",
            source="Copernicus GLO-30 / ISRO CartoDEM",
            dataset_name="Copernicus 30m Digital Elevation Model (Himalayan Arc)",
            category="dem",
            coverage="NER (20.0-30.0N, 87.0-98.0E)",
            resolution="30m (1.0 arc-sec)",
            acquired_at="2024-01-15T00:00:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[HISTORICAL]",
            local_path=os.path.join(self.data_root, "dem", "ner_elevation_30m.tif"),
            metadata={
                "crs": "EPSG:4326",
                "vertical_datum": "EGM2008",
                "accuracy_le90_m": 4.0,
                "provider": "European Space Agency / ISRO Bhuvan"
            }
        ))

        # 2. Sentinel-2 Optical & Vegetation (NDVI)
        self.register(GeospatialDatasetRecord(
            dataset_id="SENTINEL2_MSI_NDVI",
            source="Copernicus Sentinel-2 / ESA",
            dataset_name="Sentinel-2 MSI Level-2A BOA Surface Reflectance & NDVI",
            category="vegetation",
            coverage="Teesta Basin & NH-10 Corridor",
            resolution="10m",
            acquired_at="2026-08-28T04:45:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[CACHED]",
            local_path=os.path.join(self.data_root, "vegetation", "sikkim_ndvi_10m.tif"),
            metadata={
                "red_band": "B04 (665nm)",
                "nir_band": "B08 (842nm)",
                "cloud_coverage_pct": 12.4,
                "revisit_days": 5
            }
        ))

        # 3. Sentinel-1 SAR & InSAR Ground Deformation
        self.register(GeospatialDatasetRecord(
            dataset_id="SENTINEL1_SAR_LOS",
            source="Copernicus Sentinel-1 / ISRO NISAR",
            dataset_name="Sentinel-1 C-Band Interferometric SAR (IW) Ground Deformation",
            category="satellite",
            coverage="Sikkim Highway Lifelines & North Bengal Faults",
            resolution="20m x 5m",
            acquired_at="2026-08-25T11:20:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[SIMULATED]",
            local_path=os.path.join(self.data_root, "imagery", "sikkim_sar_deformation.json"),
            metadata={
                "polarization": "VV+VH",
                "look_angle_deg": 38.5,
                "orbit": "Descending (Track 121)",
                "wavelength_cm": 5.6
            }
        ))

        # 4. GSI National Landslide Inventory
        self.register(GeospatialDatasetRecord(
            dataset_id="GSI_LANDSLIDE_INVENTORY",
            source="Geological Survey of India (GSI) / NRSC",
            dataset_name="GSI National Landslide Susceptibility Mapping (NLSM) Records",
            category="landslides",
            coverage="North-East India & Himalayan Mountain Corridors",
            resolution="Field GPS Ground Truth / Point Geometry",
            acquired_at="2024-12-01T00:00:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[HISTORICAL]",
            local_path=os.path.join(self.data_root, "landslides", "gsi_historical_events.geojson"),
            metadata={
                "agency": "Geological Survey of India",
                "total_cataloged": 1420,
                "primary_geology": "Daling Group quartz-chlorite phyllites"
            }
        ))

        # 5. BRO & PWD Arterial Mountain Highway Corridors
        self.register(GeospatialDatasetRecord(
            dataset_id="BRO_PWD_MOUNTAIN_ROADS",
            source="Border Roads Organisation (BRO) Project Swastik & State PWD",
            dataset_name="NER Strategic Arterial Highway Network & Bridges",
            category="roads",
            coverage="NH-10, NH-717A, NH-310, NH-29, NH-6",
            resolution="Sub-meter Vector Network",
            acquired_at="2025-06-10T00:00:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[HISTORICAL]",
            local_path=os.path.join(self.data_root, "roads", "ner_mountain_highways.geojson"),
            metadata={
                "classification": "National Highway / Strategic Defense Line",
                "critical_bridges": 14,
                "culverts": 118
            }
        ))

        # 6. Anthropogenic Disturbance & Road-cut Excavations
        self.register(GeospatialDatasetRecord(
            dataset_id="ANTHROPOGENIC_DISTURBANCE_CATALOG",
            source="NHIDCL / BRO / GSI Field Mapping",
            dataset_name="Toe-Slope Excavation & Hill-Cut Vulnerability Catalog",
            category="anthropogenic",
            coverage="Teesta Corridor Valley Slopes",
            resolution="Sector Corridor Points",
            acquired_at="2025-09-01T00:00:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[HISTORICAL]",
            local_path=os.path.join(self.data_root, "terrain_products", "anthropogenic_cuts.json"),
            metadata={
                "risk_factor": "Toe-slope destabilization from 4-lane widening"
            }
        ))

        # 7. Administrative Boundaries (8 NER States)
        self.register(GeospatialDatasetRecord(
            dataset_id="NER_ADMIN_BOUNDARIES",
            source="Survey of India / Census of India",
            dataset_name="North Eastern Region 8 States Administrative Boundaries",
            category="boundaries",
            coverage="Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura",
            resolution="State & District Polyline/Polygon",
            acquired_at="2025-01-01T00:00:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[HISTORICAL]",
            local_path=os.path.join(self.data_root, "boundaries", "ner_admin_boundaries.geojson"),
            metadata={
                "states_count": 8,
                "districts_covered": 128,
                "crs": "EPSG:4326"
            }
        ))

        # 8. Emergency Shelters & Relief Staging Hubs
        self.register(GeospatialDatasetRecord(
            dataset_id="NER_EMERGENCY_SHELTERS",
            source="NDMA / State Disaster Management Authorities (SDMA)",
            dataset_name="Designated Emergency Evacuation Shelters & Relief Staging Nodes",
            category="shelters",
            coverage="NER Mountain Highway Corridors & District Hubs",
            resolution="Point Facilities with Capacity & Medical Facility Metas",
            acquired_at="2025-10-15T00:00:00Z",
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[HISTORICAL]",
            local_path=os.path.join(self.data_root, "shelters", "ner_shelters.geojson"),
            metadata={
                "total_shelters_cataloged": 64,
                "primary_corridors": ["NH-10", "NH-717A", "NH-29", "NH-6"]
            }
        ))

        # 9. Critical Sector Risk Snapshots (Offline Cache)
        self.register(GeospatialDatasetRecord(
            dataset_id="CRITICAL_SECTOR_RISK_SNAPSHOTS",
            source="PAHAD AI Multimodal Risk Engine",
            dataset_name="Pre-calculated Sector Risk & Stability Vector Snapshots (Offline Bundle)",
            category="risk_snapshots",
            coverage="18 Mountain Lifeline Corridors (NER)",
            resolution="Sector Corridor GeoJSON with CRI, FoS, Event Prob",
            acquired_at=now_iso,
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[CACHED]",
            local_path=os.path.join(self.data_root, "snapshots", "critical_sectors_offline.json"),
            metadata={
                "sectors_count": 18,
                "horizons": ["6h", "12h", "24h", "48h"],
                "engine_version": "PAHAD_AI_PHASE_3"
            }
        ))

        # 10. Pre-bundled NER Operational Base Map Package
        self.register(GeospatialDatasetRecord(
            dataset_id="ner-core-v1",
            source="PARVAT NETRA Core GIS Intelligence",
            dataset_name="NER Operational Base Map",
            name="NER Operational Base Map",
            version="1.0",
            size=52142,
            category="offline_package",
            coverage="North-Eastern Region (8 States)",
            resolution="Vector GeoJSON (Admin, Roads, Hydrology, Sectors, Shelters)",
            acquired_at=now_iso,
            created_at=now_iso,
            updated_at=now_iso,
            status="AVAILABLE",
            provenance="[CACHED]",
            download_available=True,
            installed=True,
            local_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "data", "offline_core_package.json"),
            checksum="75f4f3dcebc407d8672ab857af817bc45a0882610c35e49fda4dc727bc127350",
            metadata={
                "features_count": 66,
                "offline_compatible": True
            }
        ))

    def register(self, record: GeospatialDatasetRecord) -> None:
        """Registers or updates a dataset record in the catalog."""
        self._catalog[record.dataset_id] = record

    def get_dataset(self, dataset_id: str) -> Optional[GeospatialDatasetRecord]:
        """Retrieves a dataset record by ID."""
        return self._catalog.get(dataset_id)

    def list_datasets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists registered datasets, optionally filtered by category."""
        records = self._catalog.values()
        if category:
            records = [r for r in records if r.category.lower() == category.lower()]
        return [r.to_dict() for r in records]

    def export_manifest(self) -> Dict[str, Any]:
        """Exports an offline preparation manifest with timestamps and statuses."""
        datasets = [r.to_dict() for r in self._catalog.values()]
        now_iso = datetime.now(timezone.utc).isoformat()

        # Compute bundle checksum across dataset records
        hasher = hashlib.sha256()
        for d in sorted(datasets, key=lambda x: x.get("dataset_id", "")):
            hasher.update(str(d.get("dataset_id", "")).encode())
            hasher.update(str(d.get("version", "")).encode())
            hasher.update(str(d.get("checksum", "")).encode())
        bundle_checksum = hasher.hexdigest()

        return {
            "status": "OPERATIONAL",
            "bundle_version": "5.4.0-phase5d",
            "manifest_version": "3.0.0",
            "created_at": now_iso,
            "manifest_generated_at": now_iso,
            "region": "North-Eastern Region (NER)",
            "coverage": "North-Eastern Region (8 States: SK, AS, ML, AR, NL, MN, MZ, TR)",
            "model_version": "v5.2.0-phase5b",
            "checksum": bundle_checksum,
            "source_versions": {
                "dem": "GLO-30-v1",
                "boundaries": "Census-2021",
                "roads": "BRO-NHIDCL-2026",
                "sectors": "GSI-NLFC-2026"
            },
            "dataset_versions": {d["dataset_id"]: d.get("version", "1.0.0") for d in datasets},
            "total_datasets": len(self._catalog),
            "offline_capabilities": {
                "vector_tiles_cached": True,
                "raster_dem_available": True,
                "offline_sync_supported": True,
                "storage_type": "SQLite / GeoPackage / IndexedDB",
                "sync_endpoint": "/api/geospatial/offline-manifest"
            },
            "datasets": datasets,
            "available_layers": datasets
        }


# Singleton Instance
GEOSPATIAL_REGISTRY = GeospatialRegistry()
