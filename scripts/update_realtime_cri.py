#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/update_realtime_cri.py
==============================
PARVAT NETRA • Real-Time CRI Dataset Harvester & File Generator
---------------------------------------------------------------
Ingests real-time environmental data (weather, seismic, geotech, hydrology),
computes the Composite Risk Index (CRI) for all critical mountain sectors,
and files the unified dataset into CSV and JSON on disk.

Usage:
  python scripts/update_realtime_cri.py
  python scripts/update_realtime_cri.py --output-dir data/realtime
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timezone

# Ensure project root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from services.realtime_cri_service import REALTIME_CRI_SERVICE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("UPDATE_REALTIME_CRI")


def main():
    parser = argparse.ArgumentParser(description="PARVAT NETRA Real-Time CRI Data Collector & Filer")
    parser.add_argument("--output-dir", default=None, help="Custom output directory for filed datasets")
    args = parser.parse_args()

    if args.output_dir:
        REALTIME_CRI_SERVICE.data_dir = os.path.abspath(args.output_dir)
        REALTIME_CRI_SERVICE.csv_path = os.path.join(REALTIME_CRI_SERVICE.data_dir, "realtime_cri_dataset.csv")
        REALTIME_CRI_SERVICE.json_path = os.path.join(REALTIME_CRI_SERVICE.data_dir, "realtime_cri_dataset.json")

    logger.info("Starting real-time multi-modal dataset harvesting and CRI calculation...")
    start_t = datetime.now(timezone.utc)

    result = REALTIME_CRI_SERVICE.refresh_and_file_dataset()

    elapsed = (datetime.now(timezone.utc) - start_t).total_seconds()
    if result.get("status") == "SUCCESS":
        logger.info(f"Successfully processed and filed {result['record_count']} sector datasets in {elapsed:.2f}s.")
        logger.info(f"CSV Filed  : {result['csv_path']}")
        logger.info(f"JSON Filed : {result['json_path']}")
        logger.info(f"SHA-256    : {result['dataset_hash_sha256']}")
        logger.info(f"Risk Bands : {result.get('band_summary')}")
        print("\n=======================================================================================")
        print("PARVAT NETRA • REAL-TIME CRI DATASET GENERATION SUMMARY")
        print("=======================================================================================")
        print(f"Total Sectors Evaluated : {result['record_count']}")
        print(f"Generation Timestamp    : {result['generated_at']}")
        print(f"CSV File Path           : {result['csv_path']}")
        print(f"JSON File Path          : {result['json_path']}")
        print(f"SHA-256 Dataset Hash    : {result['dataset_hash_sha256']}")
        print(f"Risk Band Distribution  : {result.get('band_summary')}")
        print("=======================================================================================\n")
    else:
        logger.error("Failed to generate real-time CRI dataset.")
        sys.exit(1)


if __name__ == "__main__":
    main()
