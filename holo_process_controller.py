#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO PROCESS CONTROLLER v1.0
============================

Ermöglicht Holo die Kontrolle über Hintergrundprozesse:
- Prozesse registrieren, pausieren, fortsetzen
- Prioritäten anpassen
- Ressourcen-basierte Entscheidungen
- Automatische Lastverteilung
- Monitoring aller Prozesse

Features:
- Holo kann entscheiden welche Prozesse laufen
- Automatisches Pausieren bei hoher Last
- Prioritäts-basierte Scheduling
- Vollständiges Monitoring

Autor: Holocloude Team
Version: 1.0
"""

import time
import logging
import threading
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import psutil

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS & DATACLASSES
# =============================================================================

class ProcessState(Enum):
    """Status eines Prozesses"""
    STOPPED = "stopped"       # Nicht gestartet
    RUNNING = "running"       # Läuft aktiv
    PAUSED = "paused"         # Pausiert (kann fortgesetzt werden)
    SLEEPING = "sleeping"     # Schläft (wartet auf Trigger)
    ERROR = "error"           # Fehler aufgetreten
    COOLDOWN = "cooldown"     # In Abkühlphase


class ProcessPriority(Enum):
    """Priorität eines Prozesses"""
    CRITICAL = 100    # Muss immer laufen (z.B. Memory Monitor)
    HIGH = 75         # Wichtig (z.B. Message Handler)
    NORMAL = 50       # Standard
    LOW = 25          # Kann warten (z.B. Analytics)
    BACKGROUND = 10   # Nur wenn Ressourcen frei


class ProcessCategory(Enum):
    """Kategorie eines Prozesses"""
    CORE = "core"               # Kern-Funktionalität
    COMMUNICATION = "comm"      # Kommunikation
    MONITORING = "monitoring"   # Überwachung
    LEARNING = "learning"       # Lernen & Analyse
    CREATIVE = "creative"       # Kreative Funktionen
    MAINTENANCE = "maintenance" # Wartung & Cleanup
    OPTIONAL = "optional"       # Optionale Features


@dataclass
class ProcessInfo:
    """Informationen über einen registrierten Prozess"""
    name: str
    description: str
    category: ProcessCategory
    priority: ProcessPriority = ProcessPriority.NORMAL

    # Callbacks
    start_callback: Optional[Callable[[], bool]] = None
    stop_callback: Optional[Callable[[], bool]] = None
    pause_callback: Optional[Callable[[], bool]] = None
    resume_callback: Optional[Callable[[], bool]] = None
    update_callback: Optional[Callable[[float], None]] = None  # update(time_delta)
    status_callback: Optional[Callable[[], Dict]] = None

    # State
    state: ProcessState = ProcessState.STOPPED
    last_run: datetime = field(default_factory=lambda: datetime.min)
    last_error: Optional[str] = None
    error_count: int = 0
    run_count: int = 0

    # Timing
    min_interval: float = 1.0  # Mindestabstand zwischen Updates (Sekunden)
    last_update: datetime = field(default_factory=lambda: datetime.min)

    # Ressourcen
    estimated_cpu_percent: float = 5.0
    estimated_memory_mb: float = 10.0

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.name,
            "state": self.state.value,
            "last_run": self.last_run.isoformat() if self.last_run != datetime.min else None,
            "last_error": self.last_error,
            "error_count": self.error_count,
            "run_count": self.run_count,
            "min_interval": self.min_interval,
            "estimated_cpu": self.estimated_cpu_percent,
            "estimated_memory_mb": self.estimated_memory_mb
        }


@dataclass
class ProcessEvent:
    """Ein Prozess-Event"""
    timestamp: datetime
    process_name: str
    event_type: str  # "start", "stop", "pause", "resume", "error"
    details: str
    old_state: Optional[ProcessState] = None
    new_state: Optional[ProcessState] = None

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "process": self.process_name,
            "event": self.event_type,
            "details": self.details,
            "old_state": self.old_state.value if self.old_state else None,
            "new_state": self.new_state.value if self.new_state else None
        }


@dataclass
class ResourceLimits:
    """Ressourcen-Limits für automatische Steuerung"""
    max_cpu_percent: float = 80.0      # Bei mehr CPU pausieren
    max_memory_percent: float = 85.0   # Bei mehr Memory pausieren
    min_processes: int = 2             # Mindestens X Prozesse aktiv
    max_processes: int = 20            # Maximal X Prozesse gleichzeitig


# =============================================================================
# HOLO PROCESS CONTROLLER
# =============================================================================

class HoloProcessController:
    """
    Zentraler Controller für alle Hintergrundprozesse.

    Holo kann:
    - Prozesse registrieren und verwalten
    - Prozesse pausieren/fortsetzen
    - Prioritäten ändern
    - Status abfragen
    - Automatische Ressourcen-Verwaltung aktivieren
    """

    def __init__(self, resource_limits: Optional[ResourceLimits] = None):
        self.limits = resource_limits or ResourceLimits()

        # Prozess-Registry
        self._processes: Dict[str, ProcessInfo] = {}
        self._lock = threading.RLock()

        # Events
        self._events: deque = deque(maxlen=500)

        # Scheduler
        self._scheduler_running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._scheduler_interval = 1.0  # Sekunden

        # Auto-Management
        self._auto_manage = False
        self._paused_by_system: Set[str] = set()

        # Holo Decision Callbacks
        self._on_decision_needed: Optional[Callable[[str, str], str]] = None

        logger.info("HoloProcessController initialisiert")

    # =========================================================================
    # PROZESS REGISTRIERUNG
    # =========================================================================

    def register_process(
        self,
        name: str,
        description: str,
        category: ProcessCategory = ProcessCategory.OPTIONAL,
        priority: ProcessPriority = ProcessPriority.NORMAL,
        start_callback: Optional[Callable] = None,
        stop_callback: Optional[Callable] = None,
        pause_callback: Optional[Callable] = None,
        resume_callback: Optional[Callable] = None,
        update_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
        min_interval: float = 1.0,
        estimated_cpu: float = 5.0,
        estimated_memory: float = 10.0
    ) -> bool:
        """
        Registriere einen neuen Prozess.

        Args:
            name: Eindeutiger Name
            description: Beschreibung für Holo
            category: Kategorie des Prozesses
            priority: Priorität
            start_callback: Funktion zum Starten
            stop_callback: Funktion zum Stoppen
            pause_callback: Funktion zum Pausieren
            resume_callback: Funktion zum Fortsetzen
            update_callback: Funktion für periodische Updates
            status_callback: Funktion für Status-Abfrage
            min_interval: Mindestzeit zwischen Updates
            estimated_cpu: Geschätzte CPU-Nutzung in %
            estimated_memory: Geschätzter Speicherverbrauch in MB
        """
        with self._lock:
            if name in self._processes:
                logger.warning(f"Prozess '{name}' bereits registriert")
                return False

            info = ProcessInfo(
                name=name,
                description=description,
                category=category,
                priority=priority,
                start_callback=start_callback,
                stop_callback=stop_callback,
                pause_callback=pause_callback,
                resume_callback=resume_callback,
                update_callback=update_callback,
                status_callback=status_callback,
                min_interval=min_interval,
                estimated_cpu_percent=estimated_cpu,
                estimated_memory_mb=estimated_memory
            )

            self._processes[name] = info
            self._log_event(name, "registered", f"Prozess registriert: {description}")

            logger.info(f"Prozess registriert: {name} ({category.value}, {priority.name})")
            return True

    def unregister_process(self, name: str) -> bool:
        """Entferne einen Prozess."""
        with self._lock:
            if name not in self._processes:
                return False

            # Erst stoppen
            self.stop_process(name)

            del self._processes[name]
            self._log_event(name, "unregistered", "Prozess entfernt")
            return True

    # =========================================================================
    # PROZESS STEUERUNG - HOLO API
    # =========================================================================

    def start_process(self, name: str) -> bool:
        """
        Starte einen Prozess.

        Returns:
            True wenn erfolgreich gestartet
        """
        with self._lock:
            if name not in self._processes:
                logger.warning(f"Prozess '{name}' nicht gefunden")
                return False

            info = self._processes[name]

            if info.state == ProcessState.RUNNING:
                logger.debug(f"Prozess '{name}' läuft bereits")
                return True

            old_state = info.state

            # Start-Callback aufrufen
            if info.start_callback:
                try:
                    result = info.start_callback()
                    if not result:
                        logger.warning(f"Start von '{name}' fehlgeschlagen")
                        return False
                except Exception as e:
                    info.last_error = str(e)
                    info.error_count += 1
                    info.state = ProcessState.ERROR
                    self._log_event(name, "error", f"Start-Fehler: {e}", old_state, info.state)
                    return False

            info.state = ProcessState.RUNNING
            info.last_run = datetime.now()
            info.run_count += 1

            self._log_event(name, "start", "Prozess gestartet", old_state, info.state)
            logger.info(f"Prozess gestartet: {name}")
            return True

    def stop_process(self, name: str) -> bool:
        """Stoppe einen Prozess."""
        with self._lock:
            if name not in self._processes:
                return False

            info = self._processes[name]
            old_state = info.state

            if info.state == ProcessState.STOPPED:
                return True

            # Stop-Callback aufrufen
            if info.stop_callback:
                try:
                    info.stop_callback()
                except Exception as e:
                    logger.warning(f"Stop-Fehler bei '{name}': {e}")

            info.state = ProcessState.STOPPED
            self._log_event(name, "stop", "Prozess gestoppt", old_state, info.state)
            return True

    def pause_process(self, name: str, reason: str = "Manuell pausiert") -> bool:
        """
        Pausiere einen Prozess (kann später fortgesetzt werden).
        """
        with self._lock:
            if name not in self._processes:
                return False

            info = self._processes[name]

            if info.state != ProcessState.RUNNING:
                return False

            old_state = info.state

            # Pause-Callback aufrufen
            if info.pause_callback:
                try:
                    result = info.pause_callback()
                    if not result:
                        return False
                except Exception as e:
                    logger.warning(f"Pause-Fehler bei '{name}': {e}")
                    return False

            info.state = ProcessState.PAUSED
            self._log_event(name, "pause", reason, old_state, info.state)
            logger.info(f"Prozess pausiert: {name} ({reason})")
            return True

    def resume_process(self, name: str) -> bool:
        """Setze einen pausierten Prozess fort."""
        with self._lock:
            if name not in self._processes:
                return False

            info = self._processes[name]

            if info.state != ProcessState.PAUSED:
                return False

            old_state = info.state

            # Resume-Callback aufrufen
            if info.resume_callback:
                try:
                    result = info.resume_callback()
                    if not result:
                        return False
                except Exception as e:
                    info.last_error = str(e)
                    return False

            info.state = ProcessState.RUNNING
            info.last_run = datetime.now()

            # Aus System-Pausiert entfernen
            self._paused_by_system.discard(name)

            self._log_event(name, "resume", "Prozess fortgesetzt", old_state, info.state)
            logger.info(f"Prozess fortgesetzt: {name}")
            return True

    def set_priority(self, name: str, priority: ProcessPriority) -> bool:
        """Ändere die Priorität eines Prozesses."""
        with self._lock:
            if name not in self._processes:
                return False

            old_priority = self._processes[name].priority
            self._processes[name].priority = priority

            self._log_event(
                name, "priority_change",
                f"Priorität: {old_priority.name} → {priority.name}"
            )
            return True

    def sleep_process(self, name: str, duration_seconds: float = 0) -> bool:
        """
        Lege einen Prozess schlafen.
        Unterschied zu Pause: Schlafen ist geplant, Pause ist unterbrechend.
        """
        with self._lock:
            if name not in self._processes:
                return False

            info = self._processes[name]
            old_state = info.state

            info.state = ProcessState.SLEEPING
            self._log_event(
                name, "sleep",
                f"Prozess schläft{f' für {duration_seconds}s' if duration_seconds else ''}",
                old_state, info.state
            )
            return True

    # =========================================================================
    # STATUS & MONITORING - HOLO API
    # =========================================================================

    def get_process_status(self, name: str) -> Optional[Dict]:
        """Status eines einzelnen Prozesses."""
        with self._lock:
            if name not in self._processes:
                return None

            info = self._processes[name]
            result = info.to_dict()

            # Status-Callback für Live-Daten
            if info.status_callback:
                try:
                    live_status = info.status_callback()
                    result["live_status"] = live_status
                except Exception as e:
                    logger.debug(f"Status callback failed: {e}")

            return result

    def get_all_status(self) -> Dict[str, Any]:
        """Status aller Prozesse."""
        with self._lock:
            processes = {}
            counts = {state.value: 0 for state in ProcessState}

            for name, info in self._processes.items():
                processes[name] = info.to_dict()
                counts[info.state.value] += 1

            return {
                "processes": processes,
                "counts": counts,
                "total": len(self._processes),
                "auto_manage": self._auto_manage,
                "scheduler_running": self._scheduler_running,
                "system_paused": list(self._paused_by_system)
            }

    def get_running_processes(self) -> List[str]:
        """Liste aller laufenden Prozesse."""
        with self._lock:
            return [
                name for name, info in self._processes.items()
                if info.state == ProcessState.RUNNING
            ]

    def get_paused_processes(self) -> List[str]:
        """Liste aller pausierten Prozesse."""
        with self._lock:
            return [
                name for name, info in self._processes.items()
                if info.state == ProcessState.PAUSED
            ]

    def get_processes_by_category(self, category: ProcessCategory) -> List[str]:
        """Prozesse einer bestimmten Kategorie."""
        with self._lock:
            return [
                name for name, info in self._processes.items()
                if info.category == category
            ]

    def get_processes_by_priority(self, min_priority: ProcessPriority) -> List[str]:
        """Prozesse mit mindestens gegebener Priorität."""
        with self._lock:
            return [
                name for name, info in self._processes.items()
                if info.priority.value >= min_priority.value
            ]

    def get_status_summary(self) -> str:
        """Kurze Status-Zusammenfassung für Holo."""
        status = self.get_all_status()
        counts = status["counts"]

        running = counts.get("running", 0)
        paused = counts.get("paused", 0)
        errors = counts.get("error", 0)
        total = status["total"]

        if errors > 0:
            return f"⚠️ {running}/{total} Prozesse aktiv, {errors} mit Fehler!"
        elif paused > 0:
            return f"⏸️ {running}/{total} Prozesse aktiv, {paused} pausiert"
        else:
            return f"✅ {running}/{total} Prozesse aktiv"

    def get_events(self, count: int = 50) -> List[Dict]:
        """Letzte Events."""
        with self._lock:
            return [e.to_dict() for e in list(self._events)[-count:]]

    # =========================================================================
    # HOLO ENTSCHEIDUNGEN
    # =========================================================================

    def get_decision_options(self) -> Dict[str, Any]:
        """
        Optionen für Holo zur Entscheidung.
        Zeigt was pausiert/fortgesetzt werden kann.
        """
        with self._lock:
            can_pause = []
            can_resume = []
            can_start = []
            recommendations = []

            for name, info in self._processes.items():
                if info.state == ProcessState.RUNNING:
                    if info.priority != ProcessPriority.CRITICAL:
                        can_pause.append({
                            "name": name,
                            "priority": info.priority.name,
                            "description": info.description
                        })

                elif info.state == ProcessState.PAUSED:
                    can_resume.append({
                        "name": name,
                        "paused_by_system": name in self._paused_by_system,
                        "description": info.description
                    })

                elif info.state == ProcessState.STOPPED:
                    can_start.append({
                        "name": name,
                        "description": info.description
                    })

                # Empfehlungen generieren
                if info.error_count > 3:
                    recommendations.append(
                        f"'{name}' hat {info.error_count} Fehler - prüfen?"
                    )

            # Ressourcen-Check
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent

            if cpu > self.limits.max_cpu_percent:
                recommendations.append(
                    f"CPU bei {cpu:.0f}% - niedrig-priorisierte Prozesse pausieren?"
                )

            if mem > self.limits.max_memory_percent:
                recommendations.append(
                    f"Speicher bei {mem:.0f}% - Cleanup oder Prozesse pausieren?"
                )

            return {
                "can_pause": can_pause,
                "can_resume": can_resume,
                "can_start": can_start,
                "recommendations": recommendations,
                "resources": {"cpu_percent": cpu, "memory_percent": mem}
            }

    def ask_holo_decision(self, situation: str, options: List[str]) -> Optional[str]:
        """
        Frage Holo nach einer Entscheidung.

        Wird verwendet wenn Auto-Management unsicher ist.
        """
        if self._on_decision_needed:
            try:
                return self._on_decision_needed(situation, ", ".join(options))
            except Exception as e:
                logger.warning(f"Decision callback failed: {e}")
        return None

    def set_decision_callback(self, callback: Callable[[str, str], str]):
        """Setze den Callback für Holo-Entscheidungen."""
        self._on_decision_needed = callback

    # =========================================================================
    # AUTO-MANAGEMENT
    # =========================================================================

    def enable_auto_management(self, enable: bool = True):
        """
        Aktiviere/Deaktiviere automatisches Ressourcen-Management.

        Bei aktiviert: Prozesse werden automatisch pausiert/fortgesetzt
        basierend auf Ressourcen-Nutzung.
        """
        self._auto_manage = enable
        logger.info(f"Auto-Management: {'aktiviert' if enable else 'deaktiviert'}")

    def _auto_manage_resources(self):
        """Automatische Ressourcen-Verwaltung."""
        if not self._auto_manage:
            return

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        with self._lock:
            # Hohe Last - niedrig-priorisierte Prozesse pausieren
            if cpu > self.limits.max_cpu_percent or mem > self.limits.max_memory_percent:
                self._reduce_load()

            # Normale Last - pausierte Prozesse fortsetzen
            elif cpu < self.limits.max_cpu_percent * 0.7 and mem < self.limits.max_memory_percent * 0.7:
                self._restore_load()

    def _reduce_load(self):
        """Reduziere Last durch Pausieren von Prozessen."""
        # Sortiere nach Priorität (niedrigste zuerst)
        sorted_processes = sorted(
            self._processes.items(),
            key=lambda x: x[1].priority.value
        )

        for name, info in sorted_processes:
            if info.state == ProcessState.RUNNING:
                if info.priority.value < ProcessPriority.HIGH.value:
                    if self.pause_process(name, "Automatisch pausiert (hohe Last)"):
                        self._paused_by_system.add(name)
                        logger.info(f"Auto-Pause: {name}")
                        return  # Nur einen auf einmal

    def _restore_load(self):
        """Stelle pausierte Prozesse wieder her."""
        # Sortiere nach Priorität (höchste zuerst)
        sorted_paused = sorted(
            [name for name in self._paused_by_system if name in self._processes],
            key=lambda x: self._processes[x].priority.value,
            reverse=True
        )

        for name in sorted_paused:
            if self.resume_process(name):
                logger.info(f"Auto-Resume: {name}")
                return  # Nur einen auf einmal

    # =========================================================================
    # SCHEDULER
    # =========================================================================

    def start_scheduler(self, interval: float = 1.0):
        """Starte den Process-Scheduler."""
        if self._scheduler_running:
            return

        self._scheduler_interval = interval
        self._scheduler_running = True
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="HoloProcessScheduler",
            daemon=True
        )
        self._scheduler_thread.start()
        logger.info("Process Scheduler gestartet")

    def stop_scheduler(self):
        """Stoppe den Scheduler."""
        self._scheduler_running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
        logger.info("Process Scheduler gestoppt")

    def _scheduler_loop(self):
        """Scheduler-Hauptschleife."""
        while self._scheduler_running:
            try:
                self._scheduler_tick()
                time.sleep(self._scheduler_interval)
            except Exception as e:
                logger.error(f"Scheduler-Fehler: {e}")
                time.sleep(1.0)

    def _scheduler_tick(self):
        """Ein Scheduler-Tick - Update alle laufenden Prozesse."""
        now = datetime.now()

        with self._lock:
            for name, info in self._processes.items():
                if info.state != ProcessState.RUNNING:
                    continue

                # Prüfe ob Update fällig
                if info.update_callback:
                    elapsed = (now - info.last_update).total_seconds()

                    if elapsed >= info.min_interval:
                        try:
                            info.update_callback(elapsed)
                            info.last_update = now
                        except Exception as e:
                            info.last_error = str(e)
                            info.error_count += 1
                            logger.warning(f"Update-Fehler bei '{name}': {e}")

        # Auto-Management
        self._auto_manage_resources()

    # =========================================================================
    # BATCH OPERATIONS - HOLO API
    # =========================================================================

    def pause_all(self, except_critical: bool = True) -> int:
        """
        Pausiere alle Prozesse.

        Args:
            except_critical: Wenn True, kritische Prozesse nicht pausieren

        Returns:
            Anzahl pausierter Prozesse
        """
        count = 0
        with self._lock:
            for name, info in self._processes.items():
                if info.state == ProcessState.RUNNING:
                    if except_critical and info.priority == ProcessPriority.CRITICAL:
                        continue
                    if self.pause_process(name, "Batch-Pause"):
                        count += 1

        logger.info(f"Batch-Pause: {count} Prozesse pausiert")
        return count

    def resume_all(self) -> int:
        """Setze alle pausierten Prozesse fort."""
        count = 0
        with self._lock:
            for name, info in self._processes.items():
                if info.state == ProcessState.PAUSED:
                    if self.resume_process(name):
                        count += 1

        logger.info(f"Batch-Resume: {count} Prozesse fortgesetzt")
        return count

    def start_category(self, category: ProcessCategory) -> int:
        """Starte alle Prozesse einer Kategorie."""
        count = 0
        for name in self.get_processes_by_category(category):
            if self.start_process(name):
                count += 1
        return count

    def stop_category(self, category: ProcessCategory) -> int:
        """Stoppe alle Prozesse einer Kategorie."""
        count = 0
        for name in self.get_processes_by_category(category):
            if self.stop_process(name):
                count += 1
        return count

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _log_event(
        self,
        process_name: str,
        event_type: str,
        details: str,
        old_state: Optional[ProcessState] = None,
        new_state: Optional[ProcessState] = None
    ):
        """Logge ein Prozess-Event."""
        event = ProcessEvent(
            timestamp=datetime.now(),
            process_name=process_name,
            event_type=event_type,
            details=details,
            old_state=old_state,
            new_state=new_state
        )
        self._events.append(event)


# =============================================================================
# FACTORY & SINGLETON
# =============================================================================

_controller_instance: Optional[HoloProcessController] = None

def get_process_controller() -> HoloProcessController:
    """Singleton-Accessor für den Process Controller."""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = HoloProcessController()
    return _controller_instance

def create_process_controller(
    max_cpu_percent: float = 80.0,
    max_memory_percent: float = 85.0,
    auto_manage: bool = False,
    start_scheduler: bool = True,
    scheduler_interval: float = 1.0
) -> HoloProcessController:
    """Erstelle einen neuen Process Controller."""
    limits = ResourceLimits(
        max_cpu_percent=max_cpu_percent,
        max_memory_percent=max_memory_percent
    )

    controller = HoloProcessController(limits)

    if auto_manage:
        controller.enable_auto_management(True)

    if start_scheduler:
        controller.start_scheduler(scheduler_interval)

    return controller


# =============================================================================
# CONVENIENCE DECORATORS
# =============================================================================

def background_process(
    name: str,
    description: str = "",
    category: ProcessCategory = ProcessCategory.OPTIONAL,
    priority: ProcessPriority = ProcessPriority.NORMAL,
    min_interval: float = 1.0
):
    """
    Decorator um eine Funktion als Hintergrundprozess zu registrieren.

    Usage:
        @background_process("my_process", "Mein Prozess", ProcessCategory.LEARNING)
        def my_update_function(time_delta: float):
            # wird periodisch aufgerufen
            pass
    """
    def decorator(func):
        controller = get_process_controller()
        controller.register_process(
            name=name,
            description=description or func.__doc__ or name,
            category=category,
            priority=priority,
            update_callback=func,
            min_interval=min_interval
        )
        return func
    return decorator


# =============================================================================
# TEST / DEMO
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=== Holo Process Controller Test ===\n")

    # Controller erstellen
    controller = create_process_controller(
        auto_manage=True,
        start_scheduler=True,
        scheduler_interval=2.0
    )

    # Test-Prozesse registrieren
    def test_update(delta):
        print(f"  Test Update (delta={delta:.1f}s)")

    def test_status():
        return {"test": "running", "count": 42}

    controller.register_process(
        name="test_process",
        description="Ein Test-Prozess",
        category=ProcessCategory.OPTIONAL,
        priority=ProcessPriority.NORMAL,
        update_callback=test_update,
        status_callback=test_status,
        min_interval=3.0
    )

    controller.register_process(
        name="critical_process",
        description="Ein kritischer Prozess",
        category=ProcessCategory.CORE,
        priority=ProcessPriority.CRITICAL,
        update_callback=lambda d: print(f"  Critical Update"),
        min_interval=5.0
    )

    # Starten
    print("Prozesse starten...")
    controller.start_process("test_process")
    controller.start_process("critical_process")

    # Status
    print("\nStatus:")
    print(controller.get_status_summary())

    # Optionen
    print("\nEntscheidungs-Optionen:")
    options = controller.get_decision_options()
    print(f"  Kann pausieren: {[p['name'] for p in options['can_pause']]}")
    print(f"  Ressourcen: CPU={options['resources']['cpu_percent']:.0f}%, "
          f"MEM={options['resources']['memory_percent']:.0f}%")

    # Laufen lassen
    print("\nScheduler läuft für 15 Sekunden...")
    time.sleep(15)

    # Pausieren
    print("\nPausiere test_process:")
    controller.pause_process("test_process", "Test-Pause")

    time.sleep(5)

    # Resume
    print("\nResume test_process:")
    controller.resume_process("test_process")

    time.sleep(5)

    # Events
    print("\nLetzte Events:")
    for event in controller.get_events(10):
        print(f"  {event['timestamp']}: {event['process']} - {event['event']}")

    # Cleanup
    controller.stop_scheduler()
    print("\nTest abgeschlossen!")
