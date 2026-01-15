#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO MEMORY MONITOR v1.0
========================

Überwacht den Speicherverbrauch des Holocloude-Systems und führt
automatische Bereinigung durch wenn nötig.

Features:
- Periodische Memory-Checks
- Auto-Cleanup bei hohem Verbrauch
- Logging von Memory-Spikes
- Holo kann Speicher-Status abfragen
- Intelligente Garbage Collection

Autor: Holocloude Team
Version: 1.0
"""

import os
import gc
import sys
import time
import psutil
import logging
import threading
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)

# =============================================================================
# KONFIGURATION
# =============================================================================

class MemoryThreshold(Enum):
    """Speicher-Schwellenwerte"""
    LOW = 0.50       # 50% - Alles OK
    MEDIUM = 0.70    # 70% - Aufmerksamkeit
    HIGH = 0.85      # 85% - Cleanup starten
    CRITICAL = 0.95  # 95% - Aggressive Cleanup


@dataclass
class MemoryConfig:
    """Konfiguration für Memory Monitor"""
    # Schwellenwerte (Prozent des verfügbaren RAM)
    warning_threshold: float = 0.70   # Ab hier warnen
    cleanup_threshold: float = 0.85   # Ab hier aufräumen
    critical_threshold: float = 0.95  # Ab hier aggressiv aufräumen

    # Monitoring
    check_interval: float = 30.0      # Sekunden zwischen Checks
    spike_detection_window: int = 10  # Anzahl Messungen für Spike-Detection
    spike_threshold_mb: float = 100   # MB Anstieg = Spike

    # Cleanup
    gc_generations: List[int] = field(default_factory=lambda: [0, 1, 2])
    max_cache_age_hours: int = 24
    cleanup_cooldown: float = 60.0    # Sekunden zwischen Cleanups

    # Logging
    log_interval: float = 300.0       # Sekunden zwischen Status-Logs
    keep_history: int = 1000          # Anzahl historischer Messungen


@dataclass
class MemorySnapshot:
    """Ein Speicher-Snapshot"""
    timestamp: datetime
    total_mb: float
    available_mb: float
    used_mb: float
    percent: float
    process_mb: float
    gc_objects: int

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_mb": round(self.total_mb, 2),
            "available_mb": round(self.available_mb, 2),
            "used_mb": round(self.used_mb, 2),
            "percent": round(self.percent, 2),
            "process_mb": round(self.process_mb, 2),
            "gc_objects": self.gc_objects
        }


@dataclass
class MemoryEvent:
    """Ein Memory-Event (Spike, Cleanup, etc.)"""
    timestamp: datetime
    event_type: str  # "spike", "cleanup", "warning", "critical"
    details: str
    memory_before_mb: float
    memory_after_mb: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "details": self.details,
            "memory_before_mb": round(self.memory_before_mb, 2),
            "memory_after_mb": round(self.memory_after_mb, 2) if self.memory_after_mb else None
        }


# =============================================================================
# MEMORY CLEANER - Verschiedene Cleanup-Strategien
# =============================================================================

class MemoryCleaner:
    """Verschiedene Strategien zur Speicherbereinigung"""

    def __init__(self, config: MemoryConfig):
        self.config = config
        self._cleanup_callbacks: List[Callable[[], int]] = []
        self._last_cleanup: datetime = datetime.min

    def register_cleanup_callback(self, callback: Callable[[], int], name: str = ""):
        """
        Registriere eine Cleanup-Funktion.
        Callback sollte die Anzahl bereinigter Objekte zurückgeben.
        """
        self._cleanup_callbacks.append((callback, name))
        logger.debug(f"Cleanup callback registriert: {name}")

    def basic_gc(self) -> Tuple[int, float]:
        """
        Basis Garbage Collection.
        Returns: (collected_objects, freed_mb)
        """
        before = self._get_process_memory()

        # Alle Generationen sammeln
        collected = 0
        for gen in self.config.gc_generations:
            collected += gc.collect(gen)

        after = self._get_process_memory()
        freed = before - after

        logger.debug(f"GC: {collected} Objekte gesammelt, {freed:.2f} MB freigegeben")
        return collected, freed

    def aggressive_gc(self) -> Tuple[int, float]:
        """
        Aggressivere Garbage Collection mit Zyklus-Erkennung.
        """
        before = self._get_process_memory()

        # Cyclic garbage collector Thresholds temporär senken
        old_thresholds = gc.get_threshold()
        gc.set_threshold(100, 5, 5)

        # Mehrfach sammeln
        collected = 0
        for _ in range(3):
            for gen in [2, 1, 0]:
                collected += gc.collect(gen)

        # Thresholds wiederherstellen
        gc.set_threshold(*old_thresholds)

        after = self._get_process_memory()
        freed = before - after

        logger.info(f"Aggressive GC: {collected} Objekte, {freed:.2f} MB freigegeben")
        return collected, freed

    def run_cleanup_callbacks(self) -> Dict[str, int]:
        """Führe alle registrierten Cleanup-Callbacks aus."""
        results = {}
        for callback, name in self._cleanup_callbacks:
            try:
                cleaned = callback()
                results[name or "unnamed"] = cleaned
                logger.debug(f"Cleanup '{name}': {cleaned} items")
            except Exception as e:
                logger.warning(f"Cleanup '{name}' fehlgeschlagen: {e}")
                results[name or "unnamed"] = -1
        return results

    def full_cleanup(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Vollständige Speicherbereinigung.
        """
        # Cooldown prüfen
        now = datetime.now()
        if (now - self._last_cleanup).total_seconds() < self.config.cleanup_cooldown:
            logger.debug("Cleanup-Cooldown aktiv, überspringe")
            return {"skipped": True, "reason": "cooldown"}

        self._last_cleanup = now
        before = self._get_process_memory()

        result = {
            "timestamp": now.isoformat(),
            "memory_before_mb": before,
            "gc_collected": 0,
            "callbacks": {},
            "memory_after_mb": 0,
            "freed_mb": 0
        }

        # 1. Callbacks ausführen
        result["callbacks"] = self.run_cleanup_callbacks()

        # 2. Garbage Collection
        if aggressive:
            collected, _ = self.aggressive_gc()
        else:
            collected, _ = self.basic_gc()
        result["gc_collected"] = collected

        # 3. Ergebnis
        after = self._get_process_memory()
        result["memory_after_mb"] = after
        result["freed_mb"] = before - after

        logger.info(f"Cleanup abgeschlossen: {result['freed_mb']:.2f} MB freigegeben")
        return result

    def _get_process_memory(self) -> float:
        """Aktueller Prozess-Speicherverbrauch in MB."""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except Exception as e:
            logger.warning(f"[MemoryCleaner] _get_process_memory failed: {type(e).__name__}: {e}")
            return 0.0


# =============================================================================
# MEMORY MONITOR - Hauptklasse
# =============================================================================

class HoloMemoryMonitor:
    """
    Zentrales Memory Monitoring für Holocloude.

    Kann von Holo abgefragt werden um den Speicher-Status zu erfahren
    und entscheidet automatisch über Cleanup-Aktionen.
    """

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.cleaner = MemoryCleaner(self.config)

        # History
        self._history: deque = deque(maxlen=self.config.keep_history)
        self._events: deque = deque(maxlen=100)
        self._spike_window: deque = deque(maxlen=self.config.spike_detection_window)

        # Monitoring Thread
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Status
        self._last_status_log = datetime.min
        self._current_threshold = MemoryThreshold.LOW

        # Holo Callbacks
        self._on_warning: Optional[Callable[[str], None]] = None
        self._on_critical: Optional[Callable[[str], None]] = None
        self._on_spike: Optional[Callable[[str], None]] = None

        logger.info("HoloMemoryMonitor initialisiert")

    # =========================================================================
    # PUBLIC API - Von Holo nutzbar
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Aktueller Memory-Status für Holo.

        Returns:
            Dict mit allen relevanten Speicher-Informationen
        """
        snapshot = self._take_snapshot()

        return {
            "current": snapshot.to_dict(),
            "threshold": self._current_threshold.name,
            "is_healthy": snapshot.percent < self.config.warning_threshold * 100,
            "needs_cleanup": snapshot.percent >= self.config.cleanup_threshold * 100,
            "is_critical": snapshot.percent >= self.config.critical_threshold * 100,
            "recommendation": self._get_recommendation(snapshot),
            "recent_events": [e.to_dict() for e in list(self._events)[-5:]],
            "trend": self._calculate_trend()
        }

    def get_status_text(self) -> str:
        """
        Lesbarer Status-Text für Holo.
        """
        status = self.get_status()
        current = status["current"]

        if status["is_critical"]:
            return (f"Speicher kritisch! {current['percent']:.0f}% belegt "
                   f"({current['used_mb']:.0f} MB). Sofortige Bereinigung empfohlen!")
        elif status["needs_cleanup"]:
            return (f"Speicher hoch: {current['percent']:.0f}% belegt. "
                   f"Aufräumen würde helfen.")
        elif not status["is_healthy"]:
            return (f"Speicher erhöht: {current['percent']:.0f}% belegt. "
                   f"Beobachte weiter.")
        else:
            return (f"Speicher OK: {current['percent']:.0f}% belegt "
                   f"({current['available_mb']:.0f} MB frei).")

    def get_recommendation(self) -> str:
        """Empfehlung für Holo was zu tun ist."""
        snapshot = self._take_snapshot()
        return self._get_recommendation(snapshot)

    def request_cleanup(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Holo kann explizit Cleanup anfordern.

        Args:
            aggressive: Wenn True, aggressivere Cleanup-Strategien

        Returns:
            Cleanup-Ergebnis
        """
        logger.info(f"Cleanup von Holo angefordert (aggressive={aggressive})")
        return self.cleaner.full_cleanup(aggressive=aggressive)

    def get_history(self, minutes: int = 60) -> List[Dict]:
        """
        Speicher-Historie der letzten X Minuten.
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        with self._lock:
            return [
                s.to_dict() for s in self._history
                if s.timestamp >= cutoff
            ]

    def get_events(self, count: int = 20) -> List[Dict]:
        """Letzte Memory-Events."""
        with self._lock:
            return [e.to_dict() for e in list(self._events)[-count:]]

    def get_detailed_analysis(self) -> Dict[str, Any]:
        """
        Detaillierte Speicher-Analyse für Debugging/Monitoring.
        """
        snapshot = self._take_snapshot()

        # Top memory consumers im Python-Prozess
        gc_stats = gc.get_stats()

        return {
            "current_snapshot": snapshot.to_dict(),
            "gc_stats": gc_stats,
            "gc_thresholds": gc.get_threshold(),
            "gc_counts": gc.get_count(),
            "config": {
                "warning_threshold": self.config.warning_threshold,
                "cleanup_threshold": self.config.cleanup_threshold,
                "critical_threshold": self.config.critical_threshold,
                "check_interval": self.config.check_interval
            },
            "monitoring": {
                "is_running": self._running,
                "history_size": len(self._history),
                "events_count": len(self._events),
                "current_threshold_level": self._current_threshold.name
            },
            "trend": self._calculate_trend()
        }

    # =========================================================================
    # CALLBACKS - Holo benachrichtigen
    # =========================================================================

    def set_warning_callback(self, callback: Callable[[str], None]):
        """Callback wenn Speicher über Warning-Threshold."""
        self._on_warning = callback

    def set_critical_callback(self, callback: Callable[[str], None]):
        """Callback wenn Speicher kritisch."""
        self._on_critical = callback

    def set_spike_callback(self, callback: Callable[[str], None]):
        """Callback bei Speicher-Spike."""
        self._on_spike = callback

    def register_cleanup_callback(self, callback: Callable[[], int], name: str = ""):
        """Registriere Cleanup-Funktion (wird bei Cleanup aufgerufen)."""
        self.cleaner.register_cleanup_callback(callback, name)

    # =========================================================================
    # MONITORING THREAD
    # =========================================================================

    def start_monitoring(self):
        """Starte den Monitoring-Thread."""
        if self._running:
            logger.warning("Memory Monitor läuft bereits")
            return

        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="HoloMemoryMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("Memory Monitoring gestartet")

    def stop_monitoring(self):
        """Stoppe den Monitoring-Thread."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info("Memory Monitoring gestoppt")

    def _monitor_loop(self):
        """Haupt-Monitoring-Loop."""
        while self._running:
            try:
                self._check_memory()
                time.sleep(self.config.check_interval)
            except Exception as e:
                logger.error(f"Memory Monitor Fehler: {e}")
                time.sleep(5.0)

    def _check_memory(self):
        """Führe einen Memory-Check durch."""
        snapshot = self._take_snapshot()

        with self._lock:
            self._history.append(snapshot)
            self._spike_window.append(snapshot)

        # Threshold-Level aktualisieren
        old_threshold = self._current_threshold
        self._current_threshold = self._get_threshold_level(snapshot.percent / 100)

        # Events behandeln
        self._check_for_spike()
        self._handle_threshold_change(old_threshold, snapshot)

        # Periodisches Status-Log
        now = datetime.now()
        if (now - self._last_status_log).total_seconds() >= self.config.log_interval:
            self._log_status(snapshot)
            self._last_status_log = now

    def _take_snapshot(self) -> MemorySnapshot:
        """Erstelle einen Memory-Snapshot."""
        mem = psutil.virtual_memory()

        try:
            process = psutil.Process(os.getpid())
            process_mb = process.memory_info().rss / (1024 * 1024)
        except Exception as e:
            logger.warning(f"[MemoryMonitor] Process memory read failed: {type(e).__name__}: {e}")
            process_mb = 0.0

        return MemorySnapshot(
            timestamp=datetime.now(),
            total_mb=mem.total / (1024 * 1024),
            available_mb=mem.available / (1024 * 1024),
            used_mb=mem.used / (1024 * 1024),
            percent=mem.percent,
            process_mb=process_mb,
            gc_objects=len(gc.get_objects())
        )

    def _get_threshold_level(self, percent: float) -> MemoryThreshold:
        """Bestimme das Threshold-Level."""
        if percent >= self.config.critical_threshold:
            return MemoryThreshold.CRITICAL
        elif percent >= self.config.cleanup_threshold:
            return MemoryThreshold.HIGH
        elif percent >= self.config.warning_threshold:
            return MemoryThreshold.MEDIUM
        else:
            return MemoryThreshold.LOW

    def _check_for_spike(self):
        """Prüfe auf Speicher-Spikes."""
        if len(self._spike_window) < 3:
            return

        snapshots = list(self._spike_window)
        recent = snapshots[-1]
        oldest = snapshots[0]

        increase_mb = recent.process_mb - oldest.process_mb

        if increase_mb >= self.config.spike_threshold_mb:
            event = MemoryEvent(
                timestamp=datetime.now(),
                event_type="spike",
                details=f"Speicher-Spike: +{increase_mb:.1f} MB in {len(snapshots)} Messungen",
                memory_before_mb=oldest.process_mb,
                memory_after_mb=recent.process_mb
            )

            with self._lock:
                self._events.append(event)

            logger.warning(event.details)

            if self._on_spike:
                try:
                    self._on_spike(event.details)
                except Exception as e:
                    logger.error(f"Spike callback Fehler: {e}")

    def _handle_threshold_change(self, old: MemoryThreshold, snapshot: MemorySnapshot):
        """Behandle Änderungen im Threshold-Level."""
        new = self._current_threshold

        if new == old:
            return

        # Event erstellen
        event = MemoryEvent(
            timestamp=datetime.now(),
            event_type=new.name.lower(),
            details=f"Speicher-Level: {old.name} → {new.name} ({snapshot.percent:.1f}%)",
            memory_before_mb=snapshot.process_mb
        )

        with self._lock:
            self._events.append(event)

        # Callbacks & Aktionen
        if new == MemoryThreshold.CRITICAL:
            logger.critical(f"KRITISCHER SPEICHER: {snapshot.percent:.1f}%!")

            if self._on_critical:
                try:
                    self._on_critical(event.details)
                except Exception as e:
                    logger.error(f"Critical callback failed: {e}")

            # Automatischer aggressiver Cleanup
            result = self.cleaner.full_cleanup(aggressive=True)
            event.memory_after_mb = result.get("memory_after_mb")

        elif new == MemoryThreshold.HIGH:
            logger.warning(f"Hoher Speicherverbrauch: {snapshot.percent:.1f}%")

            # Automatischer Cleanup
            result = self.cleaner.full_cleanup(aggressive=False)
            event.memory_after_mb = result.get("memory_after_mb")

        elif new == MemoryThreshold.MEDIUM:
            logger.info(f"Speicher erhöht: {snapshot.percent:.1f}%")

            if self._on_warning:
                try:
                    self._on_warning(event.details)
                except Exception as e:
                    logger.warning(f"Warning callback failed: {e}")

    def _calculate_trend(self) -> Dict[str, Any]:
        """Berechne Speicher-Trend."""
        if len(self._history) < 5:
            return {"direction": "unknown", "change_mb_per_minute": 0}

        snapshots = list(self._history)[-30:]  # Letzte 30 Messungen

        if len(snapshots) < 2:
            return {"direction": "stable", "change_mb_per_minute": 0}

        first = snapshots[0]
        last = snapshots[-1]

        time_diff = (last.timestamp - first.timestamp).total_seconds() / 60
        if time_diff <= 0:
            return {"direction": "stable", "change_mb_per_minute": 0}

        mem_diff = last.process_mb - first.process_mb
        rate = mem_diff / time_diff

        if rate > 5:
            direction = "increasing_fast"
        elif rate > 1:
            direction = "increasing"
        elif rate < -5:
            direction = "decreasing_fast"
        elif rate < -1:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "change_mb_per_minute": round(rate, 2),
            "measurements_used": len(snapshots),
            "time_span_minutes": round(time_diff, 1)
        }

    def _get_recommendation(self, snapshot: MemorySnapshot) -> str:
        """Generiere Empfehlung basierend auf aktuellem Zustand."""
        percent = snapshot.percent / 100

        if percent >= self.config.critical_threshold:
            return "SOFORT aufräumen! Aggressive Cleanup empfohlen."
        elif percent >= self.config.cleanup_threshold:
            return "Cleanup empfohlen. Nicht-essentielle Prozesse pausieren."
        elif percent >= self.config.warning_threshold:
            return "Speicher beobachten. Bei weiterem Anstieg eingreifen."
        else:
            return "Alles OK. Kein Eingreifen nötig."

    def _log_status(self, snapshot: MemorySnapshot):
        """Logge aktuellen Status."""
        trend = self._calculate_trend()
        logger.info(
            f"Memory Status: {snapshot.percent:.1f}% "
            f"(Prozess: {snapshot.process_mb:.1f} MB, "
            f"Verfügbar: {snapshot.available_mb:.0f} MB, "
            f"Trend: {trend['direction']}, "
            f"GC-Objekte: {snapshot.gc_objects})"
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_monitor_instance: Optional[HoloMemoryMonitor] = None

def get_memory_monitor(config: Optional[MemoryConfig] = None) -> HoloMemoryMonitor:
    """
    Singleton-Accessor für den Memory Monitor.
    """
    global _monitor_instance

    if _monitor_instance is None:
        _monitor_instance = HoloMemoryMonitor(config)

    return _monitor_instance

def create_memory_monitor(
    warning_threshold: float = 0.70,
    cleanup_threshold: float = 0.85,
    critical_threshold: float = 0.95,
    check_interval: float = 30.0,
    auto_start: bool = True
) -> HoloMemoryMonitor:
    """
    Erstelle einen neuen Memory Monitor mit angepasster Konfiguration.
    """
    config = MemoryConfig(
        warning_threshold=warning_threshold,
        cleanup_threshold=cleanup_threshold,
        critical_threshold=critical_threshold,
        check_interval=check_interval
    )

    monitor = HoloMemoryMonitor(config)

    if auto_start:
        monitor.start_monitoring()

    return monitor


# =============================================================================
# TEST / DEMO
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=== Holo Memory Monitor Test ===\n")

    # Monitor erstellen
    monitor = create_memory_monitor(
        check_interval=5.0,  # Schneller für Test
        auto_start=True
    )

    # Status anzeigen
    print("Aktueller Status:")
    print(monitor.get_status_text())
    print()

    # Detaillierte Analyse
    print("Detaillierte Analyse:")
    analysis = monitor.get_detailed_analysis()
    for key, value in analysis["current_snapshot"].items():
        print(f"  {key}: {value}")
    print()

    # Trend
    print(f"Trend: {analysis['trend']}")
    print()

    # Cleanup Test
    print("Manueller Cleanup:")
    result = monitor.request_cleanup()
    print(f"  Freigegeben: {result.get('freed_mb', 0):.2f} MB")
    print(f"  GC collected: {result.get('gc_collected', 0)}")

    # Kurz laufen lassen
    print("\nMonitoring für 30 Sekunden...")
    time.sleep(30)

    # Historie
    print("\nHistorie der letzten 5 Minuten:")
    history = monitor.get_history(minutes=5)
    for h in history[-5:]:
        print(f"  {h['timestamp']}: {h['percent']:.1f}%")

    # Stoppen
    monitor.stop_monitoring()
    print("\nTest abgeschlossen!")
