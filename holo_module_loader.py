#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HOLO ROBUST MODULE LOADER v1.0                            ║
║           Robustes Laden & Überwachen aller Holo-Module                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                    ║
║  • Sicheres Laden - Ein Fehler crasht nicht alles                            ║
║  • Async Start - Module laden parallel                                        ║
║  • Health Tracking - Welche Module laufen, welche nicht                      ║
║  • Auto-Reload - Änderungen werden erkannt                                   ║
║  • Detailliertes Logging - Alles wird protokolliert                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import importlib
import importlib.util
import hashlib
import logging
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import concurrent.futures

# ============================================================================
# LOGGING SETUP
# ============================================================================

class ModuleLogHandler(logging.Handler):
    """Speichert Logs für Module in einer History"""

    def __init__(self, max_entries: int = 1000):
        super().__init__()
        self.max_entries = max_entries
        self.logs: List[Dict] = []
        self._lock = threading.Lock()

    def emit(self, record):
        with self._lock:
            self.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "module": record.name,
                "message": record.getMessage(),
                "file": getattr(record, 'filename', ''),
                "line": getattr(record, 'lineno', 0)
            })
            # Limit einhalten
            if len(self.logs) > self.max_entries:
                self.logs = self.logs[-self.max_entries:]

    def get_logs(self, module: str = None, level: str = None,
                 limit: int = 100) -> List[Dict]:
        """Holt gefilterte Logs"""
        with self._lock:
            logs = self.logs.copy()

        if module:
            logs = [l for l in logs if module in l["module"]]
        if level:
            logs = [l for l in logs if l["level"] == level]

        return logs[-limit:]

    def get_errors(self, limit: int = 50) -> List[Dict]:
        """Holt nur Fehler"""
        return self.get_logs(level="ERROR", limit=limit)


# Global Log Handler
module_log_handler = ModuleLogHandler()

# Logger setup
logger = logging.getLogger("holo.loader")
logger.addHandler(module_log_handler)


# ============================================================================
# MODULE STATUS
# ============================================================================

class ModuleStatus(Enum):
    """Status eines Moduls"""
    UNKNOWN = "unknown"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    DISABLED = "disabled"
    RELOADING = "reloading"


@dataclass
class ModuleInfo:
    """Informationen über ein Modul"""
    name: str
    path: Path
    status: ModuleStatus = ModuleStatus.UNKNOWN
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    load_time: float = 0.0
    last_loaded: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    file_hash: str = ""
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    module_ref: Any = None  # Referenz auf das geladene Modul

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "path": str(self.path),
            "status": self.status.value,
            "error": self.error,
            "load_time": self.load_time,
            "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None,
            "retry_count": self.retry_count
        }


# ============================================================================
# ROBUST MODULE LOADER
# ============================================================================

class RobustModuleLoader:
    """
    Lädt Holo-Module robust und überwacht sie.
    Wenn ein Modul fehlschlägt, laufen die anderen weiter.
    """

    def __init__(self, base_dir: Path = None, watch_interval: float = 30.0):
        """
        Args:
            base_dir: Basis-Verzeichnis (wo holo_brain.py liegt)
            watch_interval: Prüf-Intervall für Änderungen in Sekunden
        """
        self.base_dir = base_dir or Path(__file__).parent
        self.watch_interval = watch_interval

        # Module tracking
        self._modules: Dict[str, ModuleInfo] = {}
        self._load_order: List[str] = []

        # Watcher
        self._watching = False
        self._watcher_thread: Optional[threading.Thread] = None

        # Callbacks
        self._on_module_loaded: List[Callable] = []
        self._on_module_failed: List[Callable] = []
        self._on_module_reloaded: List[Callable] = []

        # Core modules die IMMER geladen werden sollen
        self._core_modules = {
            "holo_database_system",
            "holo_robust_imports",
            "holo_core_types"
        }

        # Module die übersprungen werden sollen
        self._skip_modules = {
            "__init__",
            "__pycache__",
            "setup",
            "test_",
            "conftest"
        }

        logger.info(f"🔧 RobustModuleLoader initialisiert (base_dir: {self.base_dir})")

    # ========== MODULE DISCOVERY ==========

    def discover_modules(self) -> List[str]:
        """Entdeckt alle Python-Module im Verzeichnis"""
        modules = []

        for file_path in self.base_dir.glob("*.py"):
            name = file_path.stem

            # Skip-Liste prüfen
            if any(skip in name for skip in self._skip_modules):
                continue

            if name not in self._modules:
                self._modules[name] = ModuleInfo(
                    name=name,
                    path=file_path,
                    file_hash=self._calculate_hash(file_path)
                )

            modules.append(name)

        logger.info(f"🔍 {len(modules)} Module entdeckt")
        return modules

    def _calculate_hash(self, file_path: Path) -> str:
        """Berechnet Hash einer Datei"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    # ========== SAFE MODULE LOADING ==========

    def load_module(self, name: str, required: bool = False) -> Tuple[bool, Any]:
        """
        Lädt ein einzelnes Modul sicher.

        Args:
            name: Modulname (ohne .py)
            required: Wenn True, wird bei Fehler Exception geworfen

        Returns:
            (success: bool, module_or_error: Any)
        """
        if name not in self._modules:
            # Modul entdecken wenn nicht bekannt
            file_path = self.base_dir / f"{name}.py"
            if not file_path.exists():
                error = f"Modul {name} nicht gefunden"
                logger.error(f"❌ {error}")
                if required:
                    raise ImportError(error)
                return (False, error)

            self._modules[name] = ModuleInfo(
                name=name,
                path=file_path,
                file_hash=self._calculate_hash(file_path)
            )

        info = self._modules[name]
        info.status = ModuleStatus.LOADING
        start_time = time.time()

        try:
            # Versuche zu importieren
            if name in sys.modules:
                # Modul ist schon geladen - reload
                module = importlib.reload(sys.modules[name])
            else:
                module = importlib.import_module(name)

            # Erfolg!
            load_time = time.time() - start_time
            info.status = ModuleStatus.LOADED
            info.module_ref = module
            info.load_time = load_time
            info.last_loaded = datetime.now()
            info.error = None
            info.error_traceback = None
            info.retry_count = 0

            if name not in self._load_order:
                self._load_order.append(name)

            logger.info(f"✅ {name} geladen ({load_time:.2f}s)")

            # Callbacks
            for callback in self._on_module_loaded:
                try:
                    callback(name, module)
                except Exception as e:
                    logger.warning(f"Callback-Fehler für {name}: {e}")

            return (True, module)

        except Exception as e:
            load_time = time.time() - start_time
            info.status = ModuleStatus.FAILED
            info.error = str(e)
            info.error_traceback = traceback.format_exc()
            info.load_time = load_time
            info.retry_count += 1

            logger.error(f"❌ {name} fehlgeschlagen: {e}")
            logger.debug(f"Traceback:\n{info.error_traceback}")

            # Callbacks
            for callback in self._on_module_failed:
                try:
                    callback(name, e)
                except Exception:
                    pass

            if required:
                raise

            return (False, e)

    def load_modules(self, names: List[str], parallel: bool = True) -> Dict[str, bool]:
        """
        Lädt mehrere Module.

        Args:
            names: Liste von Modulnamen
            parallel: Parallel laden (schneller aber mehr Memory)

        Returns:
            Dict mit {name: success}
        """
        results = {}

        if parallel:
            # Parallel mit ThreadPool
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self.load_module, name): name
                    for name in names
                }

                for future in concurrent.futures.as_completed(futures):
                    name = futures[future]
                    try:
                        success, _ = future.result()
                        results[name] = success
                    except Exception:
                        results[name] = False
        else:
            # Sequentiell
            for name in names:
                success, _ = self.load_module(name)
                results[name] = success

        loaded = sum(1 for v in results.values() if v)
        failed = len(results) - loaded
        logger.info(f"📦 Module geladen: {loaded} OK, {failed} fehlgeschlagen")

        return results

    async def load_modules_async(self, names: List[str]) -> Dict[str, bool]:
        """
        Lädt Module asynchron.

        Args:
            names: Liste von Modulnamen

        Returns:
            Dict mit {name: success}
        """
        loop = asyncio.get_event_loop()
        results = {}

        async def load_one(name):
            # In Thread ausführen um Event Loop nicht zu blockieren
            return await loop.run_in_executor(
                None,
                lambda: self.load_module(name)
            )

        tasks = [load_one(name) for name in names]
        done = await asyncio.gather(*tasks, return_exceptions=True)

        for name, result in zip(names, done):
            if isinstance(result, Exception):
                results[name] = False
            else:
                results[name] = result[0]

        return results

    # ========== MODULE WATCHING ==========

    def start_watching(self):
        """Startet die Überwachung auf Dateiänderungen"""
        if self._watching:
            return

        self._watching = True
        self._watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watcher_thread.start()
        logger.info(f"👁️ Module-Watcher gestartet (Intervall: {self.watch_interval}s)")

    def stop_watching(self):
        """Stoppt die Überwachung"""
        self._watching = False
        if self._watcher_thread:
            self._watcher_thread.join(timeout=5.0)
            self._watcher_thread = None
        logger.info("👁️ Module-Watcher gestoppt")

    def _watch_loop(self):
        """Hauptschleife für Dateiüberwachung"""
        while self._watching:
            try:
                self._check_for_changes()
            except Exception as e:
                logger.error(f"Watcher-Fehler: {e}")

            time.sleep(self.watch_interval)

    def _check_for_changes(self):
        """Prüft auf Dateiänderungen"""
        for name, info in list(self._modules.items()):
            if info.status == ModuleStatus.DISABLED:
                continue

            if not info.path.exists():
                # Datei gelöscht
                logger.warning(f"🗑️ Modul entfernt: {name}")
                del self._modules[name]
                continue

            # Hash prüfen
            new_hash = self._calculate_hash(info.path)
            if new_hash != info.file_hash:
                logger.info(f"🔄 Änderung erkannt: {name}")
                info.file_hash = new_hash

                # Reload wenn bereits geladen
                if info.status == ModuleStatus.LOADED:
                    self._reload_module(name)

    def _reload_module(self, name: str):
        """Lädt ein Modul neu"""
        if name not in self._modules:
            return

        info = self._modules[name]
        old_status = info.status
        info.status = ModuleStatus.RELOADING

        success, result = self.load_module(name)

        if success:
            logger.info(f"🔄 {name} neu geladen")
            for callback in self._on_module_reloaded:
                try:
                    callback(name, result)
                except Exception as e:
                    logger.warning(f"Reload-Callback-Fehler: {e}")
        else:
            logger.error(f"❌ {name} Reload fehlgeschlagen")

    # ========== RETRY FAILED MODULES ==========

    def retry_failed_modules(self) -> Dict[str, bool]:
        """Versucht fehlgeschlagene Module erneut zu laden"""
        failed = [
            name for name, info in self._modules.items()
            if info.status == ModuleStatus.FAILED and info.retry_count < info.max_retries
        ]

        if not failed:
            logger.info("✨ Keine Module zum Wiederholen")
            return {}

        logger.info(f"🔁 Versuche {len(failed)} fehlgeschlagene Module erneut...")
        return self.load_modules(failed)

    # ========== STATUS & HEALTH ==========

    def get_status(self) -> Dict:
        """Gibt den Gesamtstatus zurück"""
        by_status = {}
        for status in ModuleStatus:
            by_status[status.value] = [
                name for name, info in self._modules.items()
                if info.status == status
            ]

        return {
            "total_modules": len(self._modules),
            "loaded": len(by_status.get("loaded", [])),
            "failed": len(by_status.get("failed", [])),
            "by_status": by_status,
            "watching": self._watching,
            "watch_interval": self.watch_interval
        }

    def get_module_info(self, name: str) -> Optional[Dict]:
        """Gibt Info über ein spezifisches Modul zurück"""
        if name not in self._modules:
            return None
        return self._modules[name].to_dict()

    def get_failed_modules(self) -> List[Dict]:
        """Gibt alle fehlgeschlagenen Module mit Fehlerdetails zurück"""
        return [
            {
                "name": name,
                "error": info.error,
                "traceback": info.error_traceback,
                "retry_count": info.retry_count,
                "path": str(info.path)
            }
            for name, info in self._modules.items()
            if info.status == ModuleStatus.FAILED
        ]

    def get_health_report(self) -> Dict:
        """Erstellt einen Health-Report"""
        status = self.get_status()
        failed = self.get_failed_modules()

        # Health Score berechnen (0-100)
        total = status["total_modules"]
        if total == 0:
            health_score = 100
        else:
            health_score = int((status["loaded"] / total) * 100)

        return {
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical",
            "loaded_count": status["loaded"],
            "failed_count": status["failed"],
            "failed_modules": failed,
            "logs_errors": module_log_handler.get_errors(limit=20)
        }

    # ========== CALLBACKS ==========

    def on_module_loaded(self, callback: Callable):
        """Registriert Callback für erfolgreiche Loads"""
        self._on_module_loaded.append(callback)

    def on_module_failed(self, callback: Callable):
        """Registriert Callback für fehlgeschlagene Loads"""
        self._on_module_failed.append(callback)

    def on_module_reloaded(self, callback: Callable):
        """Registriert Callback für Reloads"""
        self._on_module_reloaded.append(callback)

    # ========== UTILITY ==========

    def get_module(self, name: str) -> Optional[Any]:
        """Holt ein geladenes Modul"""
        if name in self._modules and self._modules[name].status == ModuleStatus.LOADED:
            return self._modules[name].module_ref
        return None

    def is_loaded(self, name: str) -> bool:
        """Prüft ob ein Modul geladen ist"""
        return (
            name in self._modules and
            self._modules[name].status == ModuleStatus.LOADED
        )

    def disable_module(self, name: str):
        """Deaktiviert ein Modul (wird nicht mehr geladen/überwacht)"""
        if name in self._modules:
            self._modules[name].status = ModuleStatus.DISABLED
            logger.info(f"⏸️ Modul deaktiviert: {name}")

    def enable_module(self, name: str):
        """Aktiviert ein Modul wieder"""
        if name in self._modules:
            self._modules[name].status = ModuleStatus.UNKNOWN
            logger.info(f"▶️ Modul aktiviert: {name}")


# ============================================================================
# HOLO BOOT MANAGER
# ============================================================================

class HoloBootManager:
    """
    Verwaltet den Boot-Prozess von Holo.
    Lädt Module in der richtigen Reihenfolge mit Fehlertoleranz.
    """

    # Boot-Reihenfolge: Welche Module zuerst geladen werden
    BOOT_ORDER = [
        # Phase 1: Core (ohne diese geht nichts)
        ["holo_core_types", "holo_robust_imports", "holo_brain_core"],

        # Phase 2: Datenbank (braucht Core)
        ["holo_database_system"],

        # Phase 3: Basis-Systeme
        ["holo_consciousness", "holo_inner_life", "holo_personality", "holo_context_mind"],

        # Phase 4: Kognitive Module
        ["holo_preferences", "holo_drive_system", "holo_self_awareness",
         "holo_cognitive_modules", "holo_energy_system"],

        # Phase 5: NLP & Dialog
        ["holo_nlp_algorithms", "holo_text_reader", "holo_dialogue_engine",
         "holo_message_analyzer"],

        # Phase 6: Intelligenz
        ["holo_intelligent_router", "holo_impulse_system", "holo_context_compression",
         "holo_smart_understanding"],

        # Phase 7: Features
        ["holo_tools", "holo_learning", "holo_media_knowledge",
         "holo_media_discovery", "holo_web_curiosity"],

        # Phase 8: Integration
        ["holo_unified", "holo_depth_system", "holo_wiring", "holo_skill_system"],
    ]

    def __init__(self, loader: RobustModuleLoader):
        self.loader = loader
        self.boot_log: List[Dict] = []
        self._phase = 0
        self._started = False

    async def boot_async(self) -> Dict:
        """
        Startet Holo asynchron mit Phasen-basiertem Laden.

        Returns:
            Boot-Report
        """
        self._started = True
        start_time = time.time()
        results = {"phases": [], "success": True}

        logger.info("🚀 Holo Boot-Sequenz startet...")

        for phase_num, modules in enumerate(self.BOOT_ORDER):
            self._phase = phase_num + 1
            phase_start = time.time()

            logger.info(f"📦 Phase {self._phase}: {modules}")

            # Nur existierende Module laden
            existing = [m for m in modules if (self.loader.base_dir / f"{m}.py").exists()]

            if not existing:
                logger.warning(f"⚠️ Phase {self._phase}: Keine Module gefunden")
                continue

            # Laden
            phase_results = await self.loader.load_modules_async(existing)

            phase_time = time.time() - phase_start
            loaded = sum(1 for v in phase_results.values() if v)
            failed = len(phase_results) - loaded

            phase_info = {
                "phase": self._phase,
                "modules": existing,
                "loaded": loaded,
                "failed": failed,
                "time": phase_time,
                "results": phase_results
            }
            results["phases"].append(phase_info)

            self.boot_log.append({
                "timestamp": datetime.now().isoformat(),
                "phase": self._phase,
                "loaded": loaded,
                "failed": failed
            })

            if failed > 0:
                failed_names = [k for k, v in phase_results.items() if not v]
                logger.warning(f"⚠️ Phase {self._phase}: {failed_names} fehlgeschlagen")

        total_time = time.time() - start_time
        status = self.loader.get_status()

        results["total_time"] = total_time
        results["loaded_count"] = status["loaded"]
        results["failed_count"] = status["failed"]
        results["success"] = status["failed"] == 0

        health = self.loader.get_health_report()
        results["health_score"] = health["health_score"]

        logger.info(f"✨ Boot abgeschlossen in {total_time:.2f}s "
                   f"({status['loaded']} OK, {status['failed']} fehlgeschlagen, "
                   f"Health: {health['health_score']}%)")

        return results

    def boot_sync(self) -> Dict:
        """Synchrone Version des Boots"""
        return asyncio.run(self.boot_async())

    def get_boot_status(self) -> Dict:
        """Gibt den aktuellen Boot-Status zurück"""
        return {
            "started": self._started,
            "current_phase": self._phase,
            "total_phases": len(self.BOOT_ORDER),
            "log": self.boot_log
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Globale Instanzen
_loader: Optional[RobustModuleLoader] = None
_boot_manager: Optional[HoloBootManager] = None


def get_loader() -> RobustModuleLoader:
    """Holt den globalen ModuleLoader"""
    global _loader
    if _loader is None:
        _loader = RobustModuleLoader()
    return _loader


def get_boot_manager() -> HoloBootManager:
    """Holt den globalen BootManager"""
    global _boot_manager
    if _boot_manager is None:
        _boot_manager = HoloBootManager(get_loader())
    return _boot_manager


def get_module_logs(module: str = None, level: str = None,
                   limit: int = 100) -> List[Dict]:
    """Holt Modul-Logs"""
    return module_log_handler.get_logs(module, level, limit)


def get_health_report() -> Dict:
    """Holt den aktuellen Health-Report"""
    return get_loader().get_health_report()
