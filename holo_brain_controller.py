#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HOLO BRAIN CONTROLLER v1.0                                ║
║            Autonome Steuerung & Selbst-Heilung für Holo                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Eine kleine KI die Holo's Systeme überwacht und steuert:                    ║
║  • Modul-Laden mit Fehlertoleranz                                            ║
║  • Self-Healing bei Problemen                                                ║
║  • Autonome Entscheidungen                                                   ║
║  • Health Monitoring                                                         ║
║  • Graceful Degradation                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import json

from holo_module_loader import (
    RobustModuleLoader,
    HoloBootManager,
    ModuleStatus,
    ModuleInfo,
    get_module_logs
)

# ============================================================================
# LOGGING
# ============================================================================

logger = logging.getLogger("holo.controller")


# ============================================================================
# SYSTEM STATUS
# ============================================================================

class SystemStatus(Enum):
    """Gesamtstatus des Systems"""
    BOOTING = "booting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    HEALING = "healing"
    SHUTDOWN = "shutdown"


class HealingAction(Enum):
    """Mögliche Heilungsaktionen"""
    RETRY_MODULE = "retry_module"
    RELOAD_MODULE = "reload_module"
    DISABLE_MODULE = "disable_module"
    RESTART_SUBSYSTEM = "restart_subsystem"
    FALLBACK_MODE = "fallback_mode"
    ALERT_USER = "alert_user"


@dataclass
class SystemEvent:
    """Ein System-Event für Logging/Tracking"""
    timestamp: datetime
    event_type: str
    module: Optional[str]
    message: str
    severity: str  # info, warning, error, critical
    data: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "type": self.event_type,
            "module": self.module,
            "message": self.message,
            "severity": self.severity,
            "data": self.data
        }


# ============================================================================
# HOLO BRAIN CONTROLLER - Die autonome Steuerung
# ============================================================================

class HoloBrainController:
    """
    Autonome Steuerung für Holo's Gehirn.

    Überwacht alle Module, trifft Entscheidungen bei Problemen,
    und heilt das System wenn möglich selbst.
    """

    # Kritische Module ohne die nichts geht
    CRITICAL_MODULES = {
        "holo_core_types",
        "holo_database_system"
    }

    # Wichtige Module (System degradiert ohne sie)
    IMPORTANT_MODULES = {
        "holo_consciousness",
        "holo_personality",
        "holo_inner_life",
        "holo_intelligent_router"
    }

    # Optional (System läuft auch ohne)
    OPTIONAL_MODULES = {
        "holo_media_discovery",
        "holo_web_curiosity",
        "holo_voice_interface",
        "holo_media_knowledge"
    }

    def __init__(self, base_dir: Path = None):
        """
        Args:
            base_dir: Basis-Verzeichnis (wo holo_brain.py liegt)
        """
        self.base_dir = base_dir or Path(__file__).parent

        # Module Loader
        self.loader = RobustModuleLoader(
            base_dir=self.base_dir,
            watch_interval=30.0
        )

        # Boot Manager
        self.boot_manager = HoloBootManager(self.loader)

        # Status
        self._status = SystemStatus.BOOTING
        self._health_score = 0
        self._last_health_check = None

        # Event History
        self._events: List[SystemEvent] = []
        self._max_events = 500

        # Healing
        self._healing_in_progress = False
        self._healing_attempts: Dict[str, int] = {}
        self._max_healing_attempts = 3

        # Autonome Überwachung
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_interval = 60.0  # Sekunden

        # Callbacks für externe Systeme
        self._on_status_change: List[Callable] = []
        self._on_healing_action: List[Callable] = []
        self._on_critical_error: List[Callable] = []

        # Geladene Module-Referenzen (für schnellen Zugriff)
        self._modules: Dict[str, Any] = {}

        # Registriere Callbacks beim Loader
        self.loader.on_module_loaded(self._on_module_loaded)
        self.loader.on_module_failed(self._on_module_failed)
        self.loader.on_module_reloaded(self._on_module_reloaded)

        self._log_event("controller_init", None, "HoloBrainController initialisiert", "info")
        logger.info("🧠 HoloBrainController initialisiert")

    # ========== BOOT SEQUENCE ==========

    async def boot(self) -> Dict:
        """
        Startet Holo mit intelligenter Boot-Sequenz.

        Returns:
            Boot-Report mit Status und Details
        """
        self._status = SystemStatus.BOOTING
        self._log_event("boot_start", None, "Boot-Sequenz startet", "info")

        start_time = time.time()

        try:
            # 1. Module entdecken
            modules = self.loader.discover_modules()
            self._log_event("modules_discovered", None,
                           f"{len(modules)} Module entdeckt", "info")

            # 2. Phasen-basierter Boot
            boot_result = await self.boot_manager.boot_async()

            # 3. Module-Referenzen sammeln
            self._collect_module_refs()

            # 4. Health Check
            health = self._calculate_health()
            self._health_score = health["score"]

            # 5. Status bestimmen
            if health["score"] >= 80:
                self._status = SystemStatus.HEALTHY
            elif health["score"] >= 50:
                self._status = SystemStatus.DEGRADED
            else:
                self._status = SystemStatus.CRITICAL

            # 6. Bei Problemen: Healing versuchen
            if self._status != SystemStatus.HEALTHY:
                await self._attempt_healing()

            # 7. Monitoring starten
            self.start_monitoring()

            boot_time = time.time() - start_time

            result = {
                "success": self._status != SystemStatus.CRITICAL,
                "status": self._status.value,
                "health_score": self._health_score,
                "boot_time": boot_time,
                "loaded_modules": boot_result.get("loaded_count", 0),
                "failed_modules": boot_result.get("failed_count", 0),
                "phases": boot_result.get("phases", [])
            }

            self._log_event("boot_complete", None,
                           f"Boot abgeschlossen: {self._status.value} ({self._health_score}%)",
                           "info" if result["success"] else "warning",
                           result)

            logger.info(f"✨ Boot abgeschlossen: {self._status.value} "
                       f"(Health: {self._health_score}%, Zeit: {boot_time:.2f}s)")

            return result

        except Exception as e:
            self._status = SystemStatus.CRITICAL
            self._log_event("boot_failed", None, f"Boot fehlgeschlagen: {e}", "critical")
            logger.error(f"❌ Boot fehlgeschlagen: {e}")
            raise

    def boot_sync(self) -> Dict:
        """Synchrone Version des Boots"""
        return asyncio.run(self.boot())

    def _collect_module_refs(self):
        """Sammelt Referenzen auf geladene Module"""
        self._modules = {}
        for name in self.loader._modules:
            module = self.loader.get_module(name)
            if module:
                self._modules[name] = module

    # ========== HEALTH MONITORING ==========

    def _calculate_health(self) -> Dict:
        """Berechnet den Gesundheitszustand des Systems"""
        status = self.loader.get_status()

        total = status["total_modules"]
        loaded = status["loaded"]
        failed = status["failed"]

        if total == 0:
            return {"score": 100, "status": "unknown", "issues": [],
                    "loaded": 0, "failed": 0, "total": 0}

        # Basis-Score
        base_score = (loaded / total) * 100

        # Abzüge für kritische/wichtige Module
        issues = []
        penalty = 0

        failed_modules = self.loader.get_failed_modules()
        for fm in failed_modules:
            name = fm["name"]
            if name in self.CRITICAL_MODULES:
                penalty += 30
                issues.append(f"KRITISCH: {name} fehlt")
            elif name in self.IMPORTANT_MODULES:
                penalty += 15
                issues.append(f"WICHTIG: {name} fehlt")
            elif name not in self.OPTIONAL_MODULES:
                penalty += 5
                issues.append(f"Fehlt: {name}")

        score = max(0, min(100, base_score - penalty))

        return {
            "score": int(score),
            "status": "healthy" if score >= 80 else "degraded" if score >= 50 else "critical",
            "loaded": loaded,
            "failed": failed,
            "total": total,
            "issues": issues
        }

    def start_monitoring(self):
        """Startet die autonome Überwachung"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        # Auch den File-Watcher starten
        self.loader.start_watching()

        logger.info("👁️ Autonome Überwachung gestartet")

    def stop_monitoring(self):
        """Stoppt die Überwachung"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        self.loader.stop_watching()
        logger.info("👁️ Überwachung gestoppt")

    def _monitor_loop(self):
        """Hauptschleife der autonomen Überwachung"""
        while self._monitoring:
            try:
                self._perform_health_check()
            except Exception as e:
                logger.error(f"Monitor-Fehler: {e}")

            time.sleep(self._monitor_interval)

    def _perform_health_check(self):
        """Führt einen Health-Check durch und reagiert"""
        health = self._calculate_health()
        old_status = self._status
        old_score = self._health_score

        self._health_score = health["score"]
        self._last_health_check = datetime.now()

        # Status aktualisieren
        if health["score"] >= 80:
            new_status = SystemStatus.HEALTHY
        elif health["score"] >= 50:
            new_status = SystemStatus.DEGRADED
        else:
            new_status = SystemStatus.CRITICAL

        # Hat sich was geändert?
        if new_status != old_status or abs(health["score"] - old_score) >= 10:
            self._status = new_status
            self._log_event("health_change", None,
                           f"Health: {old_score}% → {health['score']}%, "
                           f"Status: {old_status.value} → {new_status.value}",
                           "warning" if new_status.value in ["degraded", "critical"] else "info")

            # Callbacks
            for callback in self._on_status_change:
                try:
                    callback(old_status, new_status, health)
                except Exception as e:
                    logger.warning(f"Status-Change Callback Fehler: {e}")

        # Bei Problemen: Healing versuchen
        if new_status in [SystemStatus.DEGRADED, SystemStatus.CRITICAL]:
            if not self._healing_in_progress:
                asyncio.run(self._attempt_healing())

    # ========== SELF-HEALING ==========

    async def _attempt_healing(self):
        """Versucht das System zu heilen"""
        if self._healing_in_progress:
            return

        self._healing_in_progress = True
        old_status = self._status
        self._status = SystemStatus.HEALING

        self._log_event("healing_start", None, "Self-Healing gestartet", "info")
        logger.info("🏥 Self-Healing gestartet...")

        healed = []
        failed = []

        try:
            # 1. Fehlgeschlagene Module identifizieren
            failed_modules = self.loader.get_failed_modules()

            for fm in failed_modules:
                name = fm["name"]

                # Zu viele Versuche?
                attempts = self._healing_attempts.get(name, 0)
                if attempts >= self._max_healing_attempts:
                    logger.warning(f"⏭️ {name}: Max Versuche erreicht, überspringe")
                    continue

                # Healing-Aktion bestimmen
                action = self._decide_healing_action(name, fm)

                self._log_event("healing_action", name,
                               f"Aktion: {action.value}", "info")

                # Aktion ausführen
                success = await self._execute_healing_action(action, name)

                if success:
                    healed.append(name)
                    self._healing_attempts[name] = 0
                    logger.info(f"✅ {name} geheilt")
                else:
                    failed.append(name)
                    self._healing_attempts[name] = attempts + 1
                    logger.warning(f"❌ {name} Heilung fehlgeschlagen")

            # Neuen Status berechnen
            health = self._calculate_health()
            self._health_score = health["score"]

            if health["score"] >= 80:
                self._status = SystemStatus.HEALTHY
            elif health["score"] >= 50:
                self._status = SystemStatus.DEGRADED
            else:
                self._status = SystemStatus.CRITICAL

            self._log_event("healing_complete", None,
                           f"Healing abgeschlossen: {len(healed)} geheilt, "
                           f"{len(failed)} fehlgeschlagen, Status: {self._status.value}",
                           "info" if not failed else "warning")

        except Exception as e:
            logger.error(f"Healing-Fehler: {e}")
            self._status = old_status
            self._log_event("healing_error", None, str(e), "error")

        finally:
            self._healing_in_progress = False

    def _decide_healing_action(self, module_name: str, module_info: Dict) -> HealingAction:
        """Entscheidet welche Healing-Aktion ausgeführt werden soll"""
        attempts = self._healing_attempts.get(module_name, 0)
        error = module_info.get("error", "")

        # Bei Import-Fehlern: Retry
        if "ImportError" in error or "ModuleNotFoundError" in error:
            if attempts < 2:
                return HealingAction.RETRY_MODULE
            else:
                return HealingAction.DISABLE_MODULE

        # Bei Syntax-Fehlern: Kann man nicht fixen
        if "SyntaxError" in error:
            return HealingAction.DISABLE_MODULE

        # Bei anderen Fehlern: Erst Retry, dann Reload
        if attempts == 0:
            return HealingAction.RETRY_MODULE
        elif attempts == 1:
            return HealingAction.RELOAD_MODULE
        else:
            # Kritische Module: Weiter versuchen
            if module_name in self.CRITICAL_MODULES:
                return HealingAction.RETRY_MODULE
            else:
                return HealingAction.DISABLE_MODULE

    async def _execute_healing_action(self, action: HealingAction,
                                       module_name: str) -> bool:
        """Führt eine Healing-Aktion aus"""
        try:
            if action == HealingAction.RETRY_MODULE:
                success, _ = self.loader.load_module(module_name)
                return success

            elif action == HealingAction.RELOAD_MODULE:
                # Modul aus sys.modules entfernen und neu laden
                import sys
                if module_name in sys.modules:
                    del sys.modules[module_name]
                success, _ = self.loader.load_module(module_name)
                return success

            elif action == HealingAction.DISABLE_MODULE:
                self.loader.disable_module(module_name)
                return True  # "Erfolgreich" deaktiviert

            elif action == HealingAction.ALERT_USER:
                # TODO: Nachricht an User senden
                for callback in self._on_critical_error:
                    callback(module_name, "Modul konnte nicht geladen werden")
                return False

            return False

        except Exception as e:
            logger.error(f"Healing-Aktion fehlgeschlagen: {e}")
            return False

    # ========== MODULE ACCESS ==========

    def get(self, module_name: str, default: Any = None) -> Any:
        """
        Holt ein Modul sicher.

        Args:
            module_name: Name des Moduls
            default: Fallback-Wert wenn nicht verfügbar

        Returns:
            Das Modul oder default
        """
        if module_name in self._modules:
            return self._modules[module_name]

        # Versuche nachzuladen
        module = self.loader.get_module(module_name)
        if module:
            self._modules[module_name] = module
            return module

        return default

    def get_class(self, module_name: str, class_name: str, default: Any = None) -> Any:
        """
        Holt eine Klasse aus einem Modul sicher.

        Args:
            module_name: Name des Moduls
            class_name: Name der Klasse
            default: Fallback-Wert

        Returns:
            Die Klasse oder default
        """
        module = self.get(module_name)
        if module is None:
            return default

        return getattr(module, class_name, default)

    def is_available(self, module_name: str) -> bool:
        """Prüft ob ein Modul verfügbar ist"""
        return self.loader.is_loaded(module_name)

    def require(self, module_name: str) -> Any:
        """
        Fordert ein Modul an - wirft Exception wenn nicht verfügbar.

        Args:
            module_name: Name des Moduls

        Returns:
            Das Modul

        Raises:
            RuntimeError wenn Modul nicht verfügbar
        """
        module = self.get(module_name)
        if module is None:
            raise RuntimeError(f"Required module not available: {module_name}")
        return module

    # ========== STATUS & REPORTING ==========

    def get_status(self) -> Dict:
        """Gibt den aktuellen System-Status zurück"""
        health = self._calculate_health()

        return {
            "status": self._status.value,
            "health_score": health["score"],
            "health_status": health["status"],
            "issues": health["issues"],
            "loaded_modules": health["loaded"],
            "failed_modules": health["failed"],
            "total_modules": health["total"],
            "monitoring": self._monitoring,
            "last_health_check": self._last_health_check.isoformat() if self._last_health_check else None,
            "healing_in_progress": self._healing_in_progress
        }

    def get_health_report(self) -> Dict:
        """Erstellt einen detaillierten Health-Report"""
        health = self._calculate_health()
        failed = self.loader.get_failed_modules()

        return {
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "status": self._status.value,
                "score": health["score"],
                "loaded": health["loaded"],
                "failed": health["failed"]
            },
            "critical_modules": {
                name: self.is_available(name)
                for name in self.CRITICAL_MODULES
            },
            "important_modules": {
                name: self.is_available(name)
                for name in self.IMPORTANT_MODULES
            },
            "failed_details": failed,
            "recent_events": [e.to_dict() for e in self._events[-20:]],
            "healing_attempts": self._healing_attempts.copy()
        }

    def get_health(self) -> Dict:
        """Kurzform für Health-Status (Alias für _calculate_health)"""
        return self._calculate_health()

    def get_recent_events(self, limit: int = 50,
                          severity: str = None) -> List[Dict]:
        """Holt die letzten Events"""
        events = self._events
        if severity:
            events = [e for e in events if e.severity == severity]
        return [e.to_dict() for e in events[-limit:]]

    # ========== EVENT LOGGING ==========

    def _log_event(self, event_type: str, module: Optional[str],
                   message: str, severity: str, data: Dict = None):
        """Loggt ein System-Event"""
        event = SystemEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            module=module,
            message=message,
            severity=severity,
            data=data or {}
        )

        self._events.append(event)

        # Limit einhalten
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]

        # Auch normales Logging
        log_func = {
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
            "critical": logger.critical
        }.get(severity, logger.info)

        log_func(f"[{event_type}] {module or 'system'}: {message}")

    # ========== CALLBACKS ==========

    def on_status_change(self, callback: Callable):
        """Registriert Callback für Status-Änderungen"""
        self._on_status_change.append(callback)

    def on_healing_action(self, callback: Callable):
        """Registriert Callback für Healing-Aktionen"""
        self._on_healing_action.append(callback)

    def on_critical_error(self, callback: Callable):
        """Registriert Callback für kritische Fehler"""
        self._on_critical_error.append(callback)

    # ========== MODULE CALLBACKS ==========

    def _on_module_loaded(self, name: str, module: Any):
        """Callback wenn ein Modul geladen wurde"""
        self._modules[name] = module
        self._log_event("module_loaded", name, "Modul geladen", "info")

    def _on_module_failed(self, name: str, error: Exception):
        """Callback wenn ein Modul fehlschlägt"""
        severity = "critical" if name in self.CRITICAL_MODULES else "warning"
        self._log_event("module_failed", name, str(error), severity)

        # Bei kritischen Modulen: Sofort Healing versuchen
        if name in self.CRITICAL_MODULES and not self._healing_in_progress:
            logger.warning(f"⚠️ Kritisches Modul {name} fehlgeschlagen - starte Healing")
            asyncio.run(self._attempt_healing())

    def _on_module_reloaded(self, name: str, module: Any):
        """Callback wenn ein Modul neu geladen wurde"""
        self._modules[name] = module
        self._log_event("module_reloaded", name, "Modul neu geladen", "info")

    # ========== SHUTDOWN ==========

    def shutdown(self):
        """Fährt den Controller herunter"""
        self._status = SystemStatus.SHUTDOWN
        self.stop_monitoring()
        self._log_event("shutdown", None, "Controller heruntergefahren", "info")
        logger.info("🔌 HoloBrainController heruntergefahren")

    def is_busy(self) -> bool:
        """Prüft ob der Controller gerade beschäftigt ist"""
        return self._healing_in_progress or self._status == SystemStatus.BOOTING

    def stop(self):
        """Stoppt den Controller (Alias für shutdown)"""
        self.shutdown()


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_controller: Optional[HoloBrainController] = None


def get_controller() -> HoloBrainController:
    """Holt den globalen Controller"""
    global _controller
    if _controller is None:
        _controller = HoloBrainController()
    return _controller


async def boot_holo() -> Dict:
    """Startet Holo mit dem Controller"""
    controller = get_controller()
    return await controller.boot()


def boot_holo_sync() -> Dict:
    """Synchrone Version"""
    return asyncio.run(boot_holo())
