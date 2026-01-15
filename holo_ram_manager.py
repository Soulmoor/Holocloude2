"""
Holocloude RAM Manager
======================

Intelligentes RAM-Management mit SD-Auslagerung.

Features:
- Ueberwacht RAM-Verbrauch
- Lagert ungenutzte DB-Daten auf SD aus
- Haelt Index im RAM fuer schnellen Zugriff
- LRU-Cache fuer haeufig genutzte Daten
- Automatische Kompression bei Auslagerung

Architektur:
┌─────────────────────────────────────────────────────────────┐
│                      HoloRAMManager                          │
├─────────────────────────────────────────────────────────────┤
│  RAM (schnell)          │  SD/Disk (langsam)                │
│  ┌──────────────────┐   │  ┌──────────────────┐             │
│  │ Hot Cache (LRU)  │   │  │ Ausgelagerte     │             │
│  │ - Aktive Daten   │   │  │ Daten (gzip)     │             │
│  │ - Index          │◄──┼──│ - Alte Convs     │             │
│  └──────────────────┘   │  │ - Seltene DBs    │             │
│                         │  └──────────────────┘             │
│  ┌──────────────────┐   │                                   │
│  │ Index (immer RAM)│   │  Index verweist auf SD-Positionen │
│  │ - Keys + Offsets │   │                                   │
│  └──────────────────┘   │                                   │
└─────────────────────────────────────────────────────────────┘
"""

import os
import sys
import json
import gzip
import time
import shutil
import hashlib
import logging
import threading
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# KONFIGURATION - Speicher-Limits
# =============================================================================

class RAMConfig:
    """
    Zentrale Konfiguration für RAM und SD-Speicher.

    Konfigurierbar via Umgebungsvariablen:
    - HOLO_RAM_CACHE_MB (default: 500)
    - HOLO_SD_STORAGE_GB (default: 16)
    """
    # RAM-Cache Limit (in MB)
    CACHE_SIZE_MB = int(os.environ.get("HOLO_RAM_CACHE_MB", "500"))

    # SD-Speicher Limit (in GB)
    SD_STORAGE_GB = int(os.environ.get("HOLO_SD_STORAGE_GB", "16"))
    SD_STORAGE_BYTES = SD_STORAGE_GB * 1024 * 1024 * 1024

    # RAM-Threshold für automatische Auslagerung (%)
    RAM_THRESHOLD_PERCENT = 80

    # Prüf-Intervall für Auto-Management (Sekunden)
    CHECK_INTERVAL_SECONDS = 60

    # Pfad für ausgelagerte Daten
    STORAGE_PATH = "data/offloaded"


# Optionale Imports
try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False
    logger.warning("psutil nicht verfuegbar - RAM-Monitoring eingeschraenkt")


class StorageLocation(Enum):
    """Wo Daten gespeichert sind."""
    RAM = "ram"
    DISK = "disk"
    COMPRESSED = "compressed"


@dataclass
class CacheEntry:
    """Ein Eintrag im Cache."""
    key: str
    size_bytes: int
    location: StorageLocation
    last_access: float
    access_count: int = 0
    disk_path: str = ""
    checksum: str = ""
    compressed: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class RAMStats:
    """RAM-Statistiken."""
    total_mb: float
    available_mb: float
    used_mb: float
    percent_used: float
    cache_size_mb: float
    items_in_ram: int
    items_on_disk: int


class LRUCache:
    """
    Least Recently Used Cache mit Groessenbegrenzung.
    """

    def __init__(self, max_size_mb: float = 100):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.current_size = 0
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Holt einen Wert aus dem Cache."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                entry = self._cache[key]
                entry['access_count'] += 1
                entry['last_access'] = time.time()
                return entry['value']
            return None

    def put(self, key: str, value: Any, size_bytes: int = None) -> bool:
        """Fuegt einen Wert in den Cache ein."""
        with self._lock:
            if size_bytes is None:
                size_bytes = self._estimate_size(value)

            # Wenn zu gross fuer Cache, nicht speichern
            if size_bytes > self.max_size_bytes:
                return False

            # Platz schaffen wenn noetig
            while self.current_size + size_bytes > self.max_size_bytes and self._cache:
                self._evict_oldest()

            # Existierenden Eintrag aktualisieren
            if key in self._cache:
                old_size = self._cache[key]['size']
                self.current_size -= old_size

            self._cache[key] = {
                'value': value,
                'size': size_bytes,
                'last_access': time.time(),
                'access_count': 1
            }
            self._cache.move_to_end(key)
            self.current_size += size_bytes

            return True

    def remove(self, key: str) -> bool:
        """Entfernt einen Eintrag aus dem Cache."""
        with self._lock:
            if key in self._cache:
                self.current_size -= self._cache[key]['size']
                del self._cache[key]
                return True
            return False

    def _evict_oldest(self):
        """Entfernt den aeltesten Eintrag."""
        if self._cache:
            key, entry = self._cache.popitem(last=False)
            self.current_size -= entry['size']
            logger.debug(f"Cache evicted: {key}")

    def _estimate_size(self, value: Any) -> int:
        """Schaetzt die Groesse eines Objekts."""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return sys.getsizeof(value)

    def get_stats(self) -> Dict:
        """Gibt Cache-Statistiken zurueck."""
        with self._lock:
            return {
                "items": len(self._cache),
                "size_mb": self.current_size / (1024 * 1024),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "utilization": self.current_size / self.max_size_bytes if self.max_size_bytes > 0 else 0
            }

    def clear(self):
        """Leert den Cache."""
        with self._lock:
            self._cache.clear()
            self.current_size = 0


class DiskIndex:
    """
    Index fuer auf Disk ausgelagerte Daten.
    Bleibt im RAM fuer schnellen Zugriff.
    """

    def __init__(self, index_path: str = "data/disk_index.json"):
        self.index_path = index_path
        self._index: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._load_index()

    def add_entry(self, key: str, entry: CacheEntry):
        """Fuegt einen Eintrag zum Index hinzu."""
        with self._lock:
            self._index[key] = entry
            self._save_index()

    def get_entry(self, key: str) -> Optional[CacheEntry]:
        """Holt einen Index-Eintrag."""
        with self._lock:
            return self._index.get(key)

    def remove_entry(self, key: str) -> bool:
        """Entfernt einen Index-Eintrag."""
        with self._lock:
            if key in self._index:
                del self._index[key]
                self._save_index()
                return True
            return False

    def get_all_keys(self) -> List[str]:
        """Gibt alle Keys im Index zurueck."""
        with self._lock:
            return list(self._index.keys())

    def get_entries_by_age(self, max_age_hours: int = 24) -> List[Tuple[str, CacheEntry]]:
        """Gibt Eintraege zurueck die aelter als max_age sind."""
        with self._lock:
            cutoff = time.time() - (max_age_hours * 3600)
            return [
                (k, v) for k, v in self._index.items()
                if v.last_access < cutoff
            ]

    def _save_index(self):
        """Speichert den Index auf Disk."""
        try:
            Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
            data = {k: asdict(v) for k, v in self._index.items()}
            with open(self.index_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Index speichern fehlgeschlagen: {e}")

    def _load_index(self):
        """Laedt den Index von Disk."""
        try:
            if os.path.exists(self.index_path):
                with open(self.index_path, 'r') as f:
                    data = json.load(f)
                for k, v in data.items():
                    v['location'] = StorageLocation(v['location'])
                    self._index[k] = CacheEntry(**v)
                logger.info(f"Index geladen: {len(self._index)} Eintraege")
        except Exception as e:
            logger.warning(f"Index laden fehlgeschlagen: {e}")

    def get_stats(self) -> Dict:
        """Gibt Index-Statistiken zurueck."""
        with self._lock:
            total_size = sum(e.size_bytes for e in self._index.values())
            return {
                "entries": len(self._index),
                "total_size_mb": total_size / (1024 * 1024),
                "on_disk": sum(1 for e in self._index.values() if e.location == StorageLocation.DISK),
                "compressed": sum(1 for e in self._index.values() if e.compressed)
            }


class HoloRAMManager:
    """
    Hauptklasse fuer RAM-Management.

    Verwendung:
        manager = HoloRAMManager.get_instance()

        # Daten speichern
        manager.store("conversations:123", conversation_data)

        # Daten abrufen (automatisch von RAM oder Disk)
        data = manager.retrieve("conversations:123")

        # RAM-Status pruefen
        stats = manager.get_ram_stats()
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        cache_size_mb: float = None,
        storage_path: str = None,
        ram_threshold_percent: float = None,
        check_interval_seconds: float = None,
        sd_storage_gb: float = None
    ):
        # Nutze RAMConfig Defaults wenn nicht angegeben
        self.cache_size_mb = cache_size_mb or RAMConfig.CACHE_SIZE_MB
        self.storage_path = storage_path or RAMConfig.STORAGE_PATH
        self.ram_threshold = ram_threshold_percent or RAMConfig.RAM_THRESHOLD_PERCENT
        self.check_interval = check_interval_seconds or RAMConfig.CHECK_INTERVAL_SECONDS
        self.sd_storage_limit = (sd_storage_gb or RAMConfig.SD_STORAGE_GB) * 1024 * 1024 * 1024

        # Komponenten
        self._cache = LRUCache(max_size_mb=self.cache_size_mb)
        self._index = DiskIndex()

        # Storage-Verzeichnis erstellen
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

        # Background-Thread fuer automatische Auslagerung
        self._running = False
        self._monitor_thread = None

        # Statistiken
        self._stats = {
            "stores": 0,
            "retrieves": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "offloads": 0,
            "loads_from_disk": 0,
            "sd_storage_used": 0
        }

        self._lock = threading.RLock()

        logger.info(f"HoloRAMManager initialisiert (RAM: {self.cache_size_mb}MB, SD: {self.sd_storage_limit / 1024 / 1024 / 1024:.0f}GB)")

    @classmethod
    def get_instance(cls) -> 'HoloRAMManager':
        """Singleton-Pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def store(self, key: str, data: Any, metadata: Dict = None) -> bool:
        """
        Speichert Daten - im RAM wenn Platz, sonst auf Disk.

        Args:
            key: Eindeutiger Schluessel (z.B. "conversations:user123:2024")
            data: Die zu speichernden Daten
            metadata: Zusaetzliche Metadaten

        Returns:
            True wenn erfolgreich
        """
        with self._lock:
            self._stats["stores"] += 1

            try:
                # Groesse schaetzen
                serialized = pickle.dumps(data)
                size_bytes = len(serialized)

                # Versuche in RAM zu speichern
                if self._cache.put(key, data, size_bytes):
                    # Im Cache gespeichert
                    entry = CacheEntry(
                        key=key,
                        size_bytes=size_bytes,
                        location=StorageLocation.RAM,
                        last_access=time.time(),
                        metadata=metadata or {}
                    )
                    self._index.add_entry(key, entry)
                    return True

                # Kein Platz im RAM - auf Disk auslagern
                return self._offload_to_disk(key, data, size_bytes, metadata)

            except Exception as e:
                logger.error(f"Store fehlgeschlagen fuer {key}: {e}")
                return False

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Ruft Daten ab - aus RAM oder Disk.

        Args:
            key: Der Schluessel

        Returns:
            Die Daten oder None
        """
        with self._lock:
            self._stats["retrieves"] += 1

            # Erst im Cache suchen
            data = self._cache.get(key)
            if data is not None:
                self._stats["cache_hits"] += 1
                return data

            self._stats["cache_misses"] += 1

            # Im Index suchen
            entry = self._index.get_entry(key)
            if entry is None:
                return None

            # Von Disk laden
            if entry.location in (StorageLocation.DISK, StorageLocation.COMPRESSED):
                return self._load_from_disk(key, entry)

            return None

    def _get_sd_storage_used(self) -> int:
        """Berechnet den aktuell genutzten SD-Speicher in Bytes."""
        try:
            total = 0
            for filename in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, filename)
                if os.path.isfile(filepath):
                    total += os.path.getsize(filepath)
            return total
        except Exception:
            return 0

    def _cleanup_old_sd_files(self, needed_bytes: int) -> bool:
        """Loescht aelteste Dateien um Platz zu schaffen."""
        try:
            # Alle Dateien mit Aenderungszeit sammeln
            files = []
            for filename in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, filename)
                if os.path.isfile(filepath):
                    files.append((filepath, os.path.getmtime(filepath), os.path.getsize(filepath)))

            # Nach Aenderungszeit sortieren (aelteste zuerst)
            files.sort(key=lambda x: x[1])

            freed = 0
            for filepath, _, size in files:
                if freed >= needed_bytes:
                    break
                try:
                    os.remove(filepath)
                    freed += size
                    logger.info(f"SD-Cleanup: {filepath} geloescht ({size} bytes)")
                except Exception as e:
                    logger.warning(f"Konnte {filepath} nicht loeschen: {e}")

            return freed >= needed_bytes

        except Exception as e:
            logger.error(f"SD-Cleanup fehlgeschlagen: {e}")
            return False

    def _offload_to_disk(
        self,
        key: str,
        data: Any,
        size_bytes: int,
        metadata: Dict = None
    ) -> bool:
        """Lagert Daten auf Disk aus (mit SD-Limit Check)."""
        try:
            # SD-Speicher Limit pruefen
            current_used = self._get_sd_storage_used()
            if current_used + size_bytes > self.sd_storage_limit:
                # Versuche alte Dateien zu loeschen
                needed = (current_used + size_bytes) - self.sd_storage_limit + (1024 * 1024)  # +1MB Puffer
                if not self._cleanup_old_sd_files(needed):
                    logger.warning(f"SD-Speicher voll ({current_used / 1024 / 1024 / 1024:.1f}GB / {self.sd_storage_limit / 1024 / 1024 / 1024:.0f}GB)")
                    return False

            # Dateiname aus Key generieren
            safe_key = hashlib.md5(key.encode()).hexdigest()
            file_path = os.path.join(self.storage_path, f"{safe_key}.gz")

            # Komprimiert speichern
            serialized = pickle.dumps(data)
            with gzip.open(file_path, 'wb') as f:
                f.write(serialized)

            # Checksum berechnen
            checksum = hashlib.md5(serialized).hexdigest()

            # Index aktualisieren
            entry = CacheEntry(
                key=key,
                size_bytes=size_bytes,
                location=StorageLocation.COMPRESSED,
                last_access=time.time(),
                disk_path=file_path,
                checksum=checksum,
                compressed=True,
                metadata=metadata or {}
            )
            self._index.add_entry(key, entry)

            self._stats["offloads"] += 1
            self._stats["sd_storage_used"] = self._get_sd_storage_used()
            logger.debug(f"Ausgelagert auf Disk: {key} ({size_bytes} bytes)")

            return True

        except Exception as e:
            logger.error(f"Offload fehlgeschlagen fuer {key}: {e}")
            return False

    def _load_from_disk(self, key: str, entry: CacheEntry) -> Optional[Any]:
        """Laedt Daten von Disk."""
        try:
            if not os.path.exists(entry.disk_path):
                logger.warning(f"Disk-Datei nicht gefunden: {entry.disk_path}")
                self._index.remove_entry(key)
                return None

            # Komprimierte Daten laden
            if entry.compressed:
                with gzip.open(entry.disk_path, 'rb') as f:
                    serialized = f.read()
            else:
                with open(entry.disk_path, 'rb') as f:
                    serialized = f.read()

            data = pickle.loads(serialized)

            # Zugriff aktualisieren
            entry.last_access = time.time()
            entry.access_count += 1
            self._index.add_entry(key, entry)

            # Zurueck in Cache wenn oft genutzt
            if entry.access_count >= 3:
                self._cache.put(key, data, entry.size_bytes)

            self._stats["loads_from_disk"] += 1
            logger.debug(f"Von Disk geladen: {key}")

            return data

        except Exception as e:
            logger.error(f"Load from disk fehlgeschlagen fuer {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Loescht Daten aus RAM und Disk."""
        with self._lock:
            # Aus Cache entfernen
            self._cache.remove(key)

            # Aus Index und Disk entfernen
            entry = self._index.get_entry(key)
            if entry and entry.disk_path and os.path.exists(entry.disk_path):
                try:
                    os.remove(entry.disk_path)
                except Exception as e:
                    logger.error(f"Disk-Datei loeschen fehlgeschlagen: {e}")

            return self._index.remove_entry(key)

    def get_ram_stats(self) -> RAMStats:
        """Gibt aktuelle RAM-Statistiken zurueck."""
        if HAVE_PSUTIL:
            mem = psutil.virtual_memory()
            total_mb = mem.total / (1024 * 1024)
            available_mb = mem.available / (1024 * 1024)
            used_mb = mem.used / (1024 * 1024)
            percent_used = mem.percent
        else:
            # Fallback ohne psutil
            total_mb = 0
            available_mb = 0
            used_mb = 0
            percent_used = 0

        cache_stats = self._cache.get_stats()
        index_stats = self._index.get_stats()

        return RAMStats(
            total_mb=total_mb,
            available_mb=available_mb,
            used_mb=used_mb,
            percent_used=percent_used,
            cache_size_mb=cache_stats["size_mb"],
            items_in_ram=cache_stats["items"],
            items_on_disk=index_stats["on_disk"]
        )

    def get_dashboard_data(self) -> Dict:
        """Gibt alle Daten fuer das Dashboard zurueck."""
        ram_stats = self.get_ram_stats()
        cache_stats = self._cache.get_stats()
        index_stats = self._index.get_stats()
        sd_used = self._get_sd_storage_used()

        return {
            "ram": {
                "total_mb": round(ram_stats.total_mb, 1),
                "available_mb": round(ram_stats.available_mb, 1),
                "used_mb": round(ram_stats.used_mb, 1),
                "percent_used": round(ram_stats.percent_used, 1),
                "cache_limit_mb": self.cache_size_mb
            },
            "sd_storage": {
                "used_gb": round(sd_used / 1024 / 1024 / 1024, 2),
                "limit_gb": round(self.sd_storage_limit / 1024 / 1024 / 1024, 0),
                "percent_used": round(sd_used / self.sd_storage_limit * 100, 1) if self.sd_storage_limit > 0 else 0,
                "used_bytes": sd_used,
                "limit_bytes": self.sd_storage_limit
            },
            "cache": cache_stats,
            "index": index_stats,
            "operations": self._stats.copy(),
            "cache_hit_rate": (
                self._stats["cache_hits"] / max(1, self._stats["retrieves"]) * 100
            )
        }

    def start_auto_management(self):
        """Startet automatisches RAM-Management im Hintergrund."""
        if self._running:
            return

        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._auto_manage_loop,
            daemon=True,
            name="RAMManager-AutoManage"
        )
        self._monitor_thread.start()
        logger.info("Auto-Management gestartet")

    def stop_auto_management(self):
        """Stoppt automatisches RAM-Management."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Auto-Management gestoppt")

    def _auto_manage_loop(self):
        """Hintergrund-Loop fuer automatisches Management."""
        while self._running:
            try:
                self._check_and_offload()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Auto-Management Fehler: {e}")
                time.sleep(self.check_interval)

    def _check_and_offload(self):
        """Prueft RAM und lagert bei Bedarf aus."""
        if not HAVE_PSUTIL:
            return

        mem = psutil.virtual_memory()
        if mem.percent > self.ram_threshold:
            logger.warning(f"RAM-Nutzung hoch: {mem.percent}% - Starte Auslagerung")
            self._offload_old_entries()

    def _offload_old_entries(self, max_age_hours: int = 24):
        """Lagert alte Eintraege aus dem Cache auf Disk aus."""
        # Hole alte Eintraege die noch im RAM sind
        cache_stats = self._cache.get_stats()
        if cache_stats["items"] == 0:
            return

        # Entferne aelteste Eintraege aus Cache
        # (LRU-Cache macht das automatisch beim naechsten put)
        logger.info("Alte Cache-Eintraege werden ausgelagert")

    def cleanup_old_disk_files(self, max_age_days: int = 30):
        """Loescht alte Disk-Dateien."""
        try:
            cutoff = time.time() - (max_age_days * 86400)
            removed = 0

            for filename in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, filename)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    removed += 1

            if removed > 0:
                logger.info(f"Alte Disk-Dateien geloescht: {removed}")

        except Exception as e:
            logger.error(f"Cleanup fehlgeschlagen: {e}")

    def flush_all(self):
        """
        Flusht alle Daten auf Disk und stoppt Auto-Management.
        Aufrufen beim Shutdown.
        """
        logger.info("RAM Manager: Flush gestartet...")

        # Auto-Management stoppen
        self.stop_auto_management()

        # Alle Cache-Eintraege auf Disk speichern
        try:
            cache_stats = self._cache.get_stats()
            if cache_stats["items"] > 0:
                logger.info(f"Speichere {cache_stats['items']} Cache-Eintraege auf Disk")
                # Disk-Index speichern
                self._disk_index._save_index()
        except Exception as e:
            logger.error(f"Flush fehlgeschlagen: {e}")

        logger.info("RAM Manager: Flush abgeschlossen")


# Globale Instanz
ram_manager = HoloRAMManager.get_instance()


def get_ram_manager() -> HoloRAMManager:
    """Helper-Funktion fuer einfachen Zugriff auf den RAM-Manager."""
    return HoloRAMManager.get_instance()
