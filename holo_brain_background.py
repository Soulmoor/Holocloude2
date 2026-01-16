#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO BRAIN BACKGROUND v1.0
==========================

Hintergrundprozesse für das Holo Brain System.
Integriert mit dem Process Controller für Holo-gesteuerte Verwaltung.

Prozesse:
- DreamProcessor: Nächtliche Traum-Verarbeitung
- SmartObserverProcess: Pattern-Erkennung
- ProactiveEngine: Proaktives Verhalten
- ActivityTracker: Aktivitäts-Tracking
- LearningProcessor: Hintergrund-Lernen
- MaintenanceWorker: Wartung & Cleanup

Features:
- Holo kann Prozesse pausieren/fortsetzen
- Automatische Ressourcen-Verwaltung
- Prioritäts-basiertes Scheduling
- Vollständiges Monitoring

Autor: Holocloude Team
Version: 1.0
"""

import time
import logging
import threading
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)

# Import Process Controller
try:
    from holo_process_controller import (
        HoloProcessController,
        ProcessState,
        ProcessPriority,
        ProcessCategory,
        get_process_controller
    )
    PROCESS_CONTROLLER_AVAILABLE = True
except ImportError:
    PROCESS_CONTROLLER_AVAILABLE = False
    logger.warning("Process Controller nicht verfügbar")
    # Fallback Enums wenn Process Controller nicht verfügbar
    from enum import Enum, auto
    class ProcessCategory(Enum):
        CORE = auto()
        COMMUNICATION = auto()
        LEARNING = auto()
        CREATIVE = auto()
        MAINTENANCE = auto()
        OPTIONAL = auto()
    class ProcessPriority(Enum):
        CRITICAL = auto()
        HIGH = auto()
        NORMAL = auto()
        LOW = auto()
        BACKGROUND = auto()
    class ProcessState(Enum):
        STOPPED = auto()
        RUNNING = auto()
        PAUSED = auto()
    def get_process_controller():
        return None

# Import Memory Monitor
try:
    from holo_memory_monitor import get_memory_monitor, HoloMemoryMonitor
    MEMORY_MONITOR_AVAILABLE = True
except ImportError:
    MEMORY_MONITOR_AVAILABLE = False
    logger.warning("Memory Monitor nicht verfügbar")


# =============================================================================
# BACKGROUND PROCESS BASE CLASS
# =============================================================================

class BackgroundProcessBase:
    """
    Basis-Klasse für alle Hintergrundprozesse.
    Integriert automatisch mit dem Process Controller.
    """

    def __init__(
        self,
        name: str,
        description: str,
        category: ProcessCategory = ProcessCategory.OPTIONAL,
        priority: ProcessPriority = ProcessPriority.NORMAL,
        min_interval: float = 5.0,
        auto_register: bool = True
    ):
        self.name = name
        self.description = description
        self.category = category
        self.priority = priority
        self.min_interval = min_interval

        self._is_running = False
        self._is_paused = False
        self._last_run = datetime.min
        self._run_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None

        # Stats
        self._stats: Dict[str, Any] = {}
        self._lock = threading.Lock()

        # Mit Controller registrieren
        if auto_register and PROCESS_CONTROLLER_AVAILABLE:
            self._register_with_controller()

    def _register_with_controller(self):
        """Registriere diesen Prozess beim Controller."""
        try:
            controller = get_process_controller()
            controller.register_process(
                name=self.name,
                description=self.description,
                category=self.category,
                priority=self.priority,
                start_callback=self.start,
                stop_callback=self.stop,
                pause_callback=self.pause,
                resume_callback=self.resume,
                update_callback=self.update,
                status_callback=self.get_status,
                min_interval=self.min_interval
            )
            logger.debug(f"Prozess '{self.name}' beim Controller registriert")
        except Exception as e:
            logger.warning(f"Konnte '{self.name}' nicht registrieren: {e}")

    def start(self) -> bool:
        """Starte den Prozess."""
        with self._lock:
            if self._is_running:
                return True
            self._is_running = True
            self._is_paused = False
        logger.info(f"Prozess gestartet: {self.name}")
        return True

    def stop(self) -> bool:
        """Stoppe den Prozess."""
        with self._lock:
            self._is_running = False
            self._is_paused = False
        logger.info(f"Prozess gestoppt: {self.name}")
        return True

    def pause(self) -> bool:
        """Pausiere den Prozess."""
        with self._lock:
            if not self._is_running:
                return False
            self._is_paused = True
        logger.info(f"Prozess pausiert: {self.name}")
        return True

    def resume(self) -> bool:
        """Setze den Prozess fort."""
        with self._lock:
            if not self._is_running:
                return False
            self._is_paused = False
        logger.info(f"Prozess fortgesetzt: {self.name}")
        return True

    def update(self, time_delta: float):
        """
        Periodisches Update - wird vom Scheduler aufgerufen.
        Überschreibe diese Methode in Unterklassen.
        """
        with self._lock:
            if not self._is_running or self._is_paused:
                return

        try:
            self._do_work(time_delta)
            self._last_run = datetime.now()
            self._run_count += 1
        except Exception as e:
            self._last_error = str(e)
            self._error_count += 1
            logger.error(f"Fehler in {self.name}: {e}")

    def _do_work(self, time_delta: float):
        """
        Eigentliche Arbeit - überschreibe in Unterklassen.
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Status des Prozesses."""
        with self._lock:
            return {
                "name": self.name,
                "is_running": self._is_running,
                "is_paused": self._is_paused,
                "last_run": self._last_run.isoformat() if self._last_run != datetime.min else None,
                "run_count": self._run_count,
                "error_count": self._error_count,
                "last_error": self._last_error,
                "stats": self._stats.copy()
            }

    @property
    def is_active(self) -> bool:
        """Ist der Prozess aktiv (läuft und nicht pausiert)?"""
        with self._lock:
            return self._is_running and not self._is_paused


# =============================================================================
# DREAM PROCESSOR - Nächtliche Verarbeitung
# =============================================================================

class DreamProcessor(BackgroundProcessBase):
    """
    Verarbeitet "Träume" - nächtliche Gedanken-Konsolidierung.
    Läuft nur nachts oder wenn explizit aktiviert.
    """

    def __init__(self, memory_store=None, emotions=None):
        super().__init__(
            name="dream_processor",
            description="Nächtliche Traum-Verarbeitung & Gedanken-Konsolidierung",
            category=ProcessCategory.CREATIVE,
            priority=ProcessPriority.LOW,
            min_interval=60.0  # Einmal pro Minute prüfen
        )

        self.memory_store = memory_store
        self.emotions = emotions
        self._dreams: deque = deque(maxlen=100)
        self._is_dream_time = False

    def _do_work(self, time_delta: float):
        """Prüfe ob Traum-Zeit und verarbeite."""
        hour = datetime.now().hour

        # Traum-Zeit: 23:00 - 06:00
        self._is_dream_time = hour >= 23 or hour < 6

        if not self._is_dream_time:
            return

        # Träume verarbeiten
        self._process_dreams()

    def _process_dreams(self):
        """Erstelle und verarbeite Träume."""
        if not self.memory_store:
            return

        try:
            # Hole aktuelle Emotionen
            mood = 0.5
            if self.emotions:
                try:
                    mood = self.emotions.get_dominant_mood()
                except Exception as e:
                    logger.warning(f"[BackgroundProcessor] Dream: get_dominant_mood failed: {type(e).__name__}: {e}")

            # Erstelle Traum basierend auf Erinnerungen
            recent = self.memory_store.get_recent_messages(20)

            if not recent:
                return

            # Extrahiere Themen
            topics = self._extract_topics(recent)

            dream = {
                "timestamp": datetime.now().isoformat(),
                "mood": mood,
                "topics": topics,
                "intensity": random.uniform(0.3, 0.9),
                "type": random.choice(["verarbeitung", "kreativ", "emotional"])
            }

            self._dreams.append(dream)
            self._stats["total_dreams"] = len(self._dreams)
            self._stats["last_dream"] = dream

            logger.debug(f"Traum verarbeitet: {dream['type']} mit {len(topics)} Themen")

        except Exception as e:
            logger.warning(f"Traum-Verarbeitung fehlgeschlagen: {e}")

    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """Extrahiere Themen aus Nachrichten."""
        topics = set()

        # Einfache Keyword-Extraktion
        keywords = [
            "arbeit", "projekt", "lernen", "musik", "anime", "spiel",
            "freude", "trauer", "frage", "idee", "plan", "ziel"
        ]

        for msg in messages:
            content = msg.get("content", "").lower()
            for kw in keywords:
                if kw in content:
                    topics.add(kw)

        return list(topics)[:5]

    def get_recent_dreams(self, count: int = 10) -> List[Dict]:
        """Hole aktuelle Träume."""
        return list(self._dreams)[-count:]


# =============================================================================
# SMART OBSERVER - Pattern-Erkennung
# =============================================================================

class SmartObserverProcess(BackgroundProcessBase):
    """
    Beobachtet Muster in Gesprächen und Verhalten.
    """

    def __init__(self, memory_store=None):
        super().__init__(
            name="smart_observer",
            description="Erkennt Muster in Gesprächen und Verhalten",
            category=ProcessCategory.LEARNING,
            priority=ProcessPriority.NORMAL,
            min_interval=30.0
        )

        self.memory_store = memory_store
        self._patterns: Dict[str, Any] = {}
        self._observations: deque = deque(maxlen=500)

    def _do_work(self, time_delta: float):
        """Analysiere aktuelle Daten."""
        if not self.memory_store:
            return

        try:
            recent = self.memory_store.get_recent_messages(50)
            self._analyze_patterns(recent)
        except Exception as e:
            logger.warning(f"Observer-Analyse fehlgeschlagen: {e}")

    def _analyze_patterns(self, messages: List[Dict]):
        """Analysiere Muster in Nachrichten."""
        if not messages:
            return

        # Zeit-Muster
        hours = [
            datetime.fromisoformat(m["timestamp"]).hour
            for m in messages if "timestamp" in m
        ]

        if hours:
            avg_hour = sum(hours) / len(hours)
            self._patterns["average_activity_hour"] = round(avg_hour, 1)

        # Nachrichtenlänge
        lengths = [len(m.get("content", "")) for m in messages]
        if lengths:
            self._patterns["average_message_length"] = round(sum(lengths) / len(lengths))

        # User vs Holo Ratio
        user_msgs = sum(1 for m in messages if m.get("role") == "user")
        self._patterns["user_message_ratio"] = round(user_msgs / len(messages), 2)

        self._stats.update(self._patterns)

    def get_patterns(self) -> Dict[str, Any]:
        """Hole erkannte Muster."""
        return self._patterns.copy()


# =============================================================================
# PROACTIVE ENGINE - Proaktives Verhalten
# =============================================================================

class ProactiveEngine(BackgroundProcessBase):
    """
    Generiert proaktive Nachrichten und Vorschläge.
    """

    def __init__(self, memory_store=None, emotions=None):
        super().__init__(
            name="proactive_engine",
            description="Generiert proaktive Nachrichten und Vorschläge",
            category=ProcessCategory.COMMUNICATION,
            priority=ProcessPriority.HIGH,
            min_interval=10.0
        )

        self.memory_store = memory_store
        self.emotions = emotions
        self._pending_messages: deque = deque(maxlen=50)
        self._last_proactive = datetime.min

    def _do_work(self, time_delta: float):
        """Prüfe ob proaktive Nachricht generiert werden soll."""
        now = datetime.now()

        # Mindestens 5 Minuten zwischen proaktiven Nachrichten
        if (now - self._last_proactive).total_seconds() < 300:
            return

        # Prüfe Trigger
        should_message = self._check_triggers()

        if should_message:
            message = self._generate_proactive_message()
            if message:
                self._pending_messages.append({
                    "message": message,
                    "timestamp": now.isoformat(),
                    "type": "proactive"
                })
                self._last_proactive = now
                self._stats["messages_generated"] = self._stats.get("messages_generated", 0) + 1

    def _check_triggers(self) -> bool:
        """Prüfe ob proaktive Nachricht sinnvoll ist."""
        hour = datetime.now().hour

        # Morgen-Begrüßung
        if 6 <= hour < 9:
            return random.random() < 0.3

        # Abend-Check
        if 20 <= hour < 23:
            return random.random() < 0.2

        # Zufällig tagsüber
        if 9 <= hour < 20:
            return random.random() < 0.05

        return False

    def _generate_proactive_message(self) -> Optional[str]:
        """Generiere eine proaktive Nachricht."""
        hour = datetime.now().hour
        messages = []

        if 6 <= hour < 9:
            messages = [
                "Guten Morgen! Wie hast du geschlafen? 🌅",
                "Moin! Bereit für einen neuen Tag?",
                "Hey, schon wach? Ich hoffe du hattest schöne Träume!",
            ]
        elif 12 <= hour < 14:
            messages = [
                "Zeit für eine Mittagspause? 🍜",
                "Schon Mittag! Wie läuft dein Tag bisher?",
            ]
        elif 20 <= hour < 23:
            messages = [
                "Wie war dein Tag? 🌙",
                "Feierabend! Zeit zum Entspannen?",
                "Der Abend naht... Hast du was Schönes vor?",
            ]
        else:
            messages = [
                "Hey! Alles klar bei dir?",
                "Ich hab gerade an dich gedacht! 💭",
            ]

        return random.choice(messages) if messages else None

    def get_pending_messages(self) -> List[Dict]:
        """Hole ausstehende proaktive Nachrichten."""
        messages = list(self._pending_messages)
        self._pending_messages.clear()
        return messages

    def get_pending_count(self) -> int:
        """Anzahl ausstehender Nachrichten."""
        return len(self._pending_messages)


# =============================================================================
# ACTIVITY TRACKER - Aktivitäts-Tracking
# =============================================================================

class ActivityTracker(BackgroundProcessBase):
    """
    Trackt Benutzer-Aktivitäten und lernt Muster.
    """

    def __init__(self, memory_store=None):
        super().__init__(
            name="activity_tracker",
            description="Trackt Aktivitäten und lernt Muster",
            category=ProcessCategory.MONITORING,
            priority=ProcessPriority.NORMAL,
            min_interval=60.0
        )

        self.memory_store = memory_store
        self._activity_log: deque = deque(maxlen=1000)
        self._last_activity: Optional[datetime] = None
        self._activity_patterns: Dict[str, Any] = {}

    def _do_work(self, time_delta: float):
        """Update Activity Tracking."""
        now = datetime.now()

        # Inaktivität prüfen
        if self._last_activity:
            inactive_minutes = (now - self._last_activity).total_seconds() / 60
            self._stats["inactive_minutes"] = round(inactive_minutes, 1)

        # Pattern-Update
        self._update_patterns()

    def log_activity(self, activity_type: str, details: str = ""):
        """Logge eine Aktivität."""
        now = datetime.now()

        self._activity_log.append({
            "timestamp": now.isoformat(),
            "type": activity_type,
            "details": details,
            "hour": now.hour,
            "weekday": now.weekday()
        })

        self._last_activity = now

    def _update_patterns(self):
        """Aktualisiere Aktivitäts-Muster."""
        if len(self._activity_log) < 10:
            return

        activities = list(self._activity_log)[-100:]

        # Aktivste Stunden
        hour_counts = {}
        for a in activities:
            h = a.get("hour", 0)
            hour_counts[h] = hour_counts.get(h, 0) + 1

        if hour_counts:
            most_active_hour = max(hour_counts, key=hour_counts.get)
            self._activity_patterns["most_active_hour"] = most_active_hour

        # Aktivste Tage
        day_counts = {}
        for a in activities:
            d = a.get("weekday", 0)
            day_counts[d] = day_counts.get(d, 0) + 1

        if day_counts:
            most_active_day = max(day_counts, key=day_counts.get)
            days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
            self._activity_patterns["most_active_day"] = days[most_active_day]

        self._stats["patterns"] = self._activity_patterns

    def get_activity_summary(self) -> Dict[str, Any]:
        """Aktivitäts-Zusammenfassung."""
        return {
            "total_activities": len(self._activity_log),
            "patterns": self._activity_patterns,
            "last_activity": self._last_activity.isoformat() if self._last_activity else None
        }


# =============================================================================
# LEARNING PROCESSOR - Hintergrund-Lernen
# =============================================================================

class LearningProcessor(BackgroundProcessBase):
    """
    Verarbeitet Lern-Daten im Hintergrund.
    """

    def __init__(self, learning_system=None):
        super().__init__(
            name="learning_processor",
            description="Verarbeitet Lern-Daten im Hintergrund",
            category=ProcessCategory.LEARNING,
            priority=ProcessPriority.NORMAL,
            min_interval=120.0  # Alle 2 Minuten
        )

        self.learning_system = learning_system
        self._pending_facts: deque = deque(maxlen=100)
        self._processed_count = 0

    def queue_fact(self, fact: str, category: str = "general"):
        """Füge einen Fakt zur Verarbeitung hinzu."""
        self._pending_facts.append({
            "fact": fact,
            "category": category,
            "queued_at": datetime.now().isoformat()
        })

    def _do_work(self, time_delta: float):
        """Verarbeite ausstehende Fakten."""
        if not self._pending_facts:
            return

        # Verarbeite bis zu 5 Fakten pro Durchlauf
        processed = 0
        while self._pending_facts and processed < 5:
            fact_data = self._pending_facts.popleft()

            if self.learning_system:
                try:
                    self.learning_system.learn_fact(
                        fact_data["fact"],
                        fact_data["category"]
                    )
                    processed += 1
                except Exception as e:
                    logger.warning(f"Fakt-Verarbeitung fehlgeschlagen: {e}")

        self._processed_count += processed
        self._stats["processed_facts"] = self._processed_count
        self._stats["pending_facts"] = len(self._pending_facts)


# =============================================================================
# MAINTENANCE WORKER - Wartung & Cleanup
# =============================================================================

class MaintenanceWorker(BackgroundProcessBase):
    """
    Führt Wartungsarbeiten durch: Cleanup, Optimierung, etc.
    """

    def __init__(self):
        super().__init__(
            name="maintenance_worker",
            description="Wartung, Cleanup & Optimierung",
            category=ProcessCategory.MAINTENANCE,
            priority=ProcessPriority.LOW,
            min_interval=300.0  # Alle 5 Minuten
        )

        self._last_cleanup = datetime.min
        self._cleanup_count = 0

    def _do_work(self, time_delta: float):
        """Führe Wartungsarbeiten durch."""
        now = datetime.now()

        # Cleanup alle 30 Minuten
        if (now - self._last_cleanup).total_seconds() >= 1800:
            self._perform_cleanup()
            self._last_cleanup = now

    def _perform_cleanup(self):
        """Führe Cleanup durch."""
        import gc

        # Garbage Collection
        collected = gc.collect()
        self._cleanup_count += 1

        self._stats["last_cleanup"] = datetime.now().isoformat()
        self._stats["gc_collected"] = collected
        self._stats["cleanup_count"] = self._cleanup_count

        logger.debug(f"Maintenance: GC collected {collected} objects")

        # Memory Monitor Cleanup wenn verfügbar
        if MEMORY_MONITOR_AVAILABLE:
            try:
                monitor = get_memory_monitor()
                status = monitor.get_status()
                if status.get("needs_cleanup"):
                    monitor.request_cleanup()
            except Exception as e:
                logger.debug(f"Memory monitor cleanup check failed: {e}")


# =============================================================================
# BACKGROUND PROCESS MANAGER
# =============================================================================

class BackgroundProcessManager:
    """
    Manager für alle Hintergrundprozesse.
    Bietet eine vereinfachte API für Holo.
    """

    def __init__(self, memory_store=None, emotions=None, learning_system=None):
        self.memory_store = memory_store
        self.emotions = emotions
        self.learning_system = learning_system

        # Prozesse erstellen
        self.processes: Dict[str, BackgroundProcessBase] = {}
        self._initialize_processes()

        # Controller-Referenz
        self._controller: Optional[HoloProcessController] = None
        if PROCESS_CONTROLLER_AVAILABLE:
            self._controller = get_process_controller()

    def _initialize_processes(self):
        """Initialisiere alle Hintergrundprozesse."""
        self.processes["dream_processor"] = DreamProcessor(
            self.memory_store, self.emotions
        )
        self.processes["smart_observer"] = SmartObserverProcess(
            self.memory_store
        )
        self.processes["proactive_engine"] = ProactiveEngine(
            self.memory_store, self.emotions
        )
        self.processes["activity_tracker"] = ActivityTracker(
            self.memory_store
        )
        self.processes["learning_processor"] = LearningProcessor(
            self.learning_system
        )
        self.processes["maintenance_worker"] = MaintenanceWorker()

        logger.info(f"{len(self.processes)} Hintergrundprozesse initialisiert")

    def start_all(self):
        """Starte alle Prozesse."""
        for name, process in self.processes.items():
            process.start()
        logger.info("Alle Hintergrundprozesse gestartet")

    def stop_all(self):
        """Stoppe alle Prozesse."""
        for name, process in self.processes.items():
            process.stop()
        logger.info("Alle Hintergrundprozesse gestoppt")

    def get_status(self) -> Dict[str, Any]:
        """Status aller Prozesse."""
        return {
            name: process.get_status()
            for name, process in self.processes.items()
        }

    def get_status_text(self) -> str:
        """Lesbarer Status für Holo."""
        status = self.get_status()
        running = sum(1 for s in status.values() if s["is_running"])
        paused = sum(1 for s in status.values() if s["is_paused"])

        return f"Hintergrundprozesse: {running}/{len(status)} aktiv, {paused} pausiert"

    # Direkter Zugriff auf spezifische Prozesse
    @property
    def dream_processor(self) -> DreamProcessor:
        return self.processes["dream_processor"]

    @property
    def smart_observer(self) -> SmartObserverProcess:
        return self.processes["smart_observer"]

    @property
    def proactive_engine(self) -> ProactiveEngine:
        return self.processes["proactive_engine"]

    @property
    def activity_tracker(self) -> ActivityTracker:
        return self.processes["activity_tracker"]

    @property
    def learning_processor(self) -> LearningProcessor:
        return self.processes["learning_processor"]


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_background_manager(
    memory_store=None,
    emotions=None,
    learning_system=None,
    auto_start: bool = True
) -> BackgroundProcessManager:
    """
    Erstelle einen Background Process Manager.
    """
    manager = BackgroundProcessManager(
        memory_store=memory_store,
        emotions=emotions,
        learning_system=learning_system
    )

    if auto_start:
        manager.start_all()

    return manager


# =============================================================================
# TEST / DEMO
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=== Holo Background Processes Test ===\n")

    # Manager erstellen
    manager = create_background_manager(auto_start=True)

    # Status anzeigen
    print("Status:")
    print(manager.get_status_text())
    print()

    # Einzelne Prozesse testen
    print("Prozess-Details:")
    for name, status in manager.get_status().items():
        print(f"  {name}: {'aktiv' if status['is_running'] else 'inaktiv'}")

    # Process Controller starten wenn verfügbar
    if PROCESS_CONTROLLER_AVAILABLE:
        print("\nProcess Controller verfügbar!")
        controller = get_process_controller()
        controller.start_scheduler()

        # 30 Sekunden laufen lassen
        print("Laufe für 30 Sekunden...")
        time.sleep(30)

        # Events anzeigen
        print("\nLetzte Events:")
        for event in controller.get_events(10):
            print(f"  {event['timestamp']}: {event['process']} - {event['event']}")

        controller.stop_scheduler()

    manager.stop_all()
    print("\nTest abgeschlossen!")
