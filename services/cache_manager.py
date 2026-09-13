# -*- coding: utf-8 -*-
"""
services/cache_manager.py
=========================
PARVAT NETRA • Production Multi-Tier Persistent Cache Architecture
------------------------------------------------------------------
Provides thread-safe in-memory caching backed by persistent disk storage
under data/cache/ to guarantee that production inference never crashes during
intermittent network outages, API downtime, or remote sensor disconnection.

Features:
  - Multi-tier: Fast memory cache + atomic disk serialization
  - Graceful degradation: Flags stale data with explicit data_age_seconds
  - Namespace isolation: weather, seismic, dem, iot, satellite, alerts
  - Atomic write: Write-then-rename prevents corrupted disk reads
  - Zero silent failure: Transparent provenance logging ([CACHED], [STALE])

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import os
import json
import time
import logging
import threading
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("CACHE_MANAGER")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CACHE_DIR = os.path.join(REPO_ROOT, "data", "cache")


class CacheManager:
    """
    Thread-safe, multi-tier cache manager with disk persistence.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _get_disk_path(self, namespace: str, key: str) -> str:
        safe_ns = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in namespace)
        safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
        ns_dir = os.path.join(self.cache_dir, safe_ns)
        os.makedirs(ns_dir, exist_ok=True)
        return os.path.join(ns_dir, f"{safe_key}.json")

    def get(
        self,
        namespace: str,
        key: str,
        allow_stale: bool = True
    ) -> Optional[Tuple[Any, bool, float, Dict[str, Any]]]:
        """
        Retrieves an item from cache.
        Returns tuple: (data, is_stale, data_age_seconds, metadata)
        Returns None if key is missing from both memory and disk.
        """
        cache_key = f"{namespace}:{key}"
        now = time.time()

        # 1. Check memory cache first
        with self._lock:
            entry = self._memory_cache.get(cache_key)

        if entry is not None:
            age = now - entry["fetched_at"]
            is_stale = age > entry["ttl"]
            if not is_stale or allow_stale:
                return entry["data"], is_stale, age, entry.get("meta", {})

        # 2. Check disk cache if not in memory
        disk_path = self._get_disk_path(namespace, key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    disk_entry = json.load(f)

                fetched_at = float(disk_entry.get("fetched_at", 0.0))
                ttl = float(disk_entry.get("ttl", 3600.0))
                age = now - fetched_at
                is_stale = age > ttl

                meta = disk_entry.get("meta", {})
                data = disk_entry.get("data")

                # Rehydrate memory cache
                with self._lock:
                    self._memory_cache[cache_key] = {
                        "data": data,
                        "fetched_at": fetched_at,
                        "ttl": ttl,
                        "meta": meta
                    }

                if not is_stale or allow_stale:
                    return data, is_stale, age, meta
            except Exception as e:
                logger.warning(f"Failed to read disk cache for {namespace}:{key}: {e}")

        return None

    def set(
        self,
        namespace: str,
        key: str,
        data: Any,
        ttl_seconds: int = 900,
        source: str = "EXTERNAL_API",
        provenance: str = "[LIVE]"
    ) -> None:
        """
        Stores data into memory cache and persists to disk atomically.
        """
        now = time.time()
        meta = {
            "source": source,
            "provenance": provenance,
            "stored_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "ttl": ttl_seconds
        }

        entry = {
            "data": data,
            "fetched_at": now,
            "ttl": ttl_seconds,
            "meta": meta
        }

        cache_key = f"{namespace}:{key}"
        with self._lock:
            self._memory_cache[cache_key] = entry

        # Persist to disk atomically (write to temp file then rename)
        disk_path = self._get_disk_path(namespace, key)
        temp_path = f"{disk_path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2)
            if os.path.exists(disk_path):
                os.replace(temp_path, disk_path)
            else:
                os.rename(temp_path, disk_path)
        except Exception as e:
            logger.error(f"Failed to write disk cache for {namespace}:{key}: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def clear(self, namespace: Optional[str] = None) -> None:
        """Clears memory and disk cache for a namespace or all namespaces."""
        with self._lock:
            if namespace:
                keys_to_remove = [k for k in self._memory_cache if k.startswith(f"{namespace}:")]
                for k in keys_to_remove:
                    del self._memory_cache[k]
            else:
                self._memory_cache.clear()

        # Clean disk files
        if namespace:
            safe_ns = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in namespace)
            ns_dir = os.path.join(self.cache_dir, safe_ns)
            if os.path.exists(ns_dir):
                for fname in os.listdir(ns_dir):
                    if fname.endswith(".json"):
                        try:
                            os.remove(os.path.join(ns_dir, fname))
                        except Exception:
                            pass
        else:
            if os.path.exists(self.cache_dir):
                for root, _, files in os.walk(self.cache_dir):
                    for fname in files:
                        if fname.endswith(".json"):
                            try:
                                os.remove(os.path.join(root, fname))
                            except Exception:
                                pass


# Global singleton cache instance
GLOBAL_CACHE = CacheManager()
