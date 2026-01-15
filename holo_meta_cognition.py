#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO META-COGNITION SYSTEM v1.0
================================
Echte Selbstreflexion und System-Beobachtung.

Komponenten:
- HoloPresenceAwareness: Versteht User-Anwesenheit/Abwesenheit
- HoloSandbox: Simuliert Aktionen vor Ausführung (A/B Testing)
- HoloMetaObserver: Beobachtet das gesamte System und lernt

Diese Meta-Schicht analysiert:
- Warum Entscheidungen getroffen wurden
- Was funktioniert und was nicht
- Wie Komponenten zusammenarbeiten
- Muster im eigenen Verhalten

Version: 1.0
"""

import logging
import json
import statistics
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
import hashlib
import random

logger = logging.getLogger("HoloMetaCognition")


# =============================================================================
# KONFIGURATION
# =============================================================================

class MetaConfig:
    """Konfiguration für Meta-Cognition"""

    # Observation
    MAX_OBSERVATIONS = 1000
    OBSERVATION_WINDOW_HOURS = 24

    # Learning
    MIN_SAMPLES_FOR_PATTERN = 5
    CONFIDENCE_THRESHOLD = 0.7

    # Sandbox
    MAX_SIMULATIONS = 10
    SIMULATION_DEPTH = 3

    # Presence
    PRESENCE_CHECK_INTERVAL = 60  # Sekunden
    ABSENCE_CATEGORIES = {
        "micro": (0, 15),      # 0-15 min
        "short": (15, 90),     # 15-90 min
        "work": (90, 600),     # 90min - 10h
        "extended": (600, None) # > 10h
    }


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

class ObservationType(Enum):
    """Typen von Beobachtungen"""
    DECISION = "decision"           # Eine Entscheidung wurde getroffen
    RESPONSE = "response"           # Eine Antwort wurde generiert
    EMOTION_CHANGE = "emotion"      # Emotionszustand änderte sich
    LEARNING = "learning"           # Etwas wurde gelernt
    ERROR = "error"                 # Ein Fehler trat auf
    USER_FEEDBACK = "feedback"      # User reagierte
    COMPONENT_CALL = "component"    # Komponente wurde aufgerufen
    STATE_CHANGE = "state"          # Systemzustand änderte sich


class PresenceState(Enum):
    """User-Anwesenheitszustand"""
    HOME = "home"
    AWAY_MICRO = "away_micro"       # Kurz weg (< 15 min)
    AWAY_SHORT = "away_short"       # Einkaufen etc (15-90 min)
    AWAY_WORK = "away_work"         # Arbeit (> 90 min)
    AWAY_EXTENDED = "away_extended" # Lange weg (> 10h)
    UNKNOWN = "unknown"


@dataclass
class SystemObservation:
    """Eine Beobachtung des Systems"""
    id: str
    timestamp: str
    observation_type: ObservationType
    component: str                  # Welche Komponente war beteiligt
    action: str                     # Was wurde getan
    context: Dict                   # Kontext der Beobachtung
    outcome: Optional[str] = None   # Was war das Ergebnis
    success: Optional[bool] = None  # War es erfolgreich?
    duration_ms: Optional[float] = None
    related_observations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "type": self.observation_type.value,
            "component": self.component,
            "action": self.action,
            "context": self.context,
            "outcome": self.outcome,
            "success": self.success,
            "duration_ms": self.duration_ms,
        }


@dataclass
class LearnedPattern:
    """Ein gelerntes Muster im Systemverhalten"""
    id: str
    pattern_type: str               # z.B. "decision_chain", "error_cause"
    description: str
    conditions: Dict                # Unter welchen Bedingungen
    typical_outcome: str            # Was passiert typischerweise
    confidence: float               # Wie sicher (0-1)
    sample_count: int               # Wie oft beobachtet
    first_seen: str
    last_seen: str
    success_rate: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.pattern_type,
            "description": self.description,
            "conditions": self.conditions,
            "outcome": self.typical_outcome,
            "confidence": self.confidence,
            "samples": self.sample_count,
            "success_rate": self.success_rate,
        }


@dataclass
class ComponentInsight:
    """Erkenntnisse über eine Komponente"""
    component_name: str
    purpose: str                    # Wofür ist sie da
    typical_usage: List[str]        # Wann wird sie genutzt
    dependencies: List[str]         # Was braucht sie
    dependents: List[str]           # Wer braucht sie
    avg_response_time_ms: float
    success_rate: float
    common_errors: List[str]
    last_analyzed: str


@dataclass
class SandboxResult:
    """Ergebnis einer Sandbox-Simulation"""
    option: str
    predicted_outcome: str
    confidence: float
    predicted_user_reaction: str
    risk_level: float               # 0-1
    benefits: List[str]
    drawbacks: List[str]
    recommendation: str


# =============================================================================
# PRESENCE AWARENESS
# =============================================================================

class HoloPresenceAwareness:
    """
    Versteht User-Anwesenheit basierend auf pi_control Daten.

    Nutzt:
    - presence_statistics von pi_control
    - Historische Muster
    - Tageszeit-Korrelationen
    """

    def __init__(self, pi_interface=None, db: 'HoloDatabaseManager' = None, data_dir: Path = None):
        self.pi_interface = pi_interface
        self.db = db
        self.data_dir = data_dir or Path.home() / "holo_data" / "meta_cognition"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self.data_dir / "presence_history.db"

        # Aktueller Zustand
        self._current_state = PresenceState.UNKNOWN
        self._absence_start: Optional[datetime] = None
        self._last_check = datetime.now()

        # Muster-Lernen
        self._absence_history: List[Dict] = []
        self._daily_patterns: Dict[int, Dict] = {}  # weekday -> pattern

        # Vorhersagen
        self._predicted_return: Optional[datetime] = None
        self._prediction_confidence: float = 0.0

        # DB initialisieren und History laden
        self._init_db()
        self._load_history()

        logger.info("[PresenceAwareness] Initialisiert mit DB-Persistenz")

    def _init_db(self):
        """Erstellt die Presence-Datenbank-Tabellen"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS absence_history (
                    id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_minutes REAL,
                    category TEXT,
                    weekday INTEGER,
                    hour_start INTEGER,
                    hour_end INTEGER,
                    predicted_return TEXT,
                    actual_return TEXT,
                    prediction_accuracy REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS daily_patterns (
                    id TEXT PRIMARY KEY,
                    weekday INTEGER NOT NULL UNIQUE,
                    avg_absence_minutes REAL,
                    typical_leave_hour REAL,
                    typical_return_hour REAL,
                    absence_count INTEGER,
                    last_updated TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS state_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    state TEXT NOT NULL,
                    is_home INTEGER,
                    duration_since_last REAL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_absence_start ON absence_history(start_time)')
            conn.commit()

    def _load_history(self):
        """Lädt historische Presence-Daten aus der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Lade Absence History (letzte 90 Tage)
                cursor = conn.execute('''
                    SELECT * FROM absence_history
                    WHERE start_time > datetime('now', '-90 days')
                    ORDER BY start_time DESC
                    LIMIT 500
                ''')
                self._absence_history = [{
                    'start': row['start_time'],
                    'end': row['end_time'],
                    'duration_min': row['duration_minutes'],
                    'category': row['category'],
                    'weekday': row['weekday'],
                } for row in cursor]

                # Lade Daily Patterns
                cursor = conn.execute('SELECT * FROM daily_patterns')
                for row in cursor:
                    self._daily_patterns[row['weekday']] = {
                        'avg_absence_min': row['avg_absence_minutes'],
                        'typical_leave': row['typical_leave_hour'],
                        'typical_return': row['typical_return_hour'],
                        'count': row['absence_count'],
                    }

                logger.info(f"[Presence] {len(self._absence_history)} Abwesenheiten, "
                           f"{len(self._daily_patterns)} Tagesmuster geladen")

        except Exception as e:
            logger.warning(f"[Presence] Konnte History nicht laden: {e}")

    def _save_absence(self, absence_data: Dict):
        """Speichert eine Abwesenheit in der DB"""
        try:
            absence_id = hashlib.md5(
                f"{absence_data.get('start', '')}".encode()
            ).hexdigest()[:16]

            start_dt = datetime.fromisoformat(absence_data.get('start', ''))

            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO absence_history
                    (id, start_time, end_time, duration_minutes, category,
                     weekday, hour_start, hour_end, predicted_return, actual_return, prediction_accuracy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    absence_id,
                    absence_data.get('start'),
                    absence_data.get('end'),
                    absence_data.get('duration_min'),
                    absence_data.get('category'),
                    start_dt.weekday(),
                    start_dt.hour,
                    datetime.fromisoformat(absence_data['end']).hour if absence_data.get('end') else None,
                    absence_data.get('predicted_return'),
                    absence_data.get('end'),
                    absence_data.get('prediction_accuracy'),
                ))
                conn.commit()
        except Exception as e:
            logger.debug(f"[Presence] Konnte Abwesenheit nicht speichern: {e}")

    def _save_daily_pattern(self, weekday: int, pattern: Dict):
        """Speichert ein Tagesmuster in der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO daily_patterns
                    (id, weekday, avg_absence_minutes, typical_leave_hour,
                     typical_return_hour, absence_count, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"pattern_{weekday}",
                    weekday,
                    pattern.get('avg_absence_min'),
                    pattern.get('typical_leave'),
                    pattern.get('typical_return'),
                    pattern.get('count'),
                    datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.debug(f"[Presence] Konnte Pattern nicht speichern: {e}")

    def _log_state_change(self, new_state: PresenceState, is_home: bool):
        """Loggt State-Änderungen in die DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                duration_since = (datetime.now() - self._last_check).total_seconds() / 60
                conn.execute('''
                    INSERT INTO state_log (timestamp, state, is_home, duration_since_last)
                    VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    new_state.value,
                    1 if is_home else 0,
                    duration_since
                ))
                conn.commit()
        except Exception as e:
            logger.debug(f"[Presence] Konnte State nicht loggen: {e}")

    def get_absence_statistics(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über Abwesenheiten zurück für Nachvollziehbarkeit.
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Gesamt-Statistiken
                cursor = conn.execute('''
                    SELECT
                        COUNT(*) as total_absences,
                        AVG(duration_minutes) as avg_duration,
                        MAX(duration_minutes) as max_duration,
                        AVG(prediction_accuracy) as avg_prediction_accuracy
                    FROM absence_history
                    WHERE start_time > datetime('now', '-30 days')
                ''')
                row = cursor.fetchone()

                # Nach Kategorie
                cursor = conn.execute('''
                    SELECT category, COUNT(*) as count, AVG(duration_minutes) as avg_duration
                    FROM absence_history
                    WHERE start_time > datetime('now', '-30 days')
                    GROUP BY category
                ''')
                by_category = {r['category']: {'count': r['count'], 'avg_min': r['avg_duration']} for r in cursor}

                return {
                    'total_absences_30d': row['total_absences'],
                    'avg_duration_min': row['avg_duration'],
                    'max_duration_min': row['max_duration'],
                    'prediction_accuracy': row['avg_prediction_accuracy'],
                    'by_category': by_category,
                    'daily_patterns': dict(self._daily_patterns),
                }
        except Exception as e:
            logger.warning(f"[Presence] Konnte Statistiken nicht laden: {e}")
            return {}

    def connect_pi_interface(self, pi_interface):
        """Verbindet mit pi_control Interface"""
        self.pi_interface = pi_interface
        logger.info("[PresenceAwareness] Mit pi_control verbunden")

    def update(self) -> Dict[str, Any]:
        """
        Aktualisiert Presence-Status von pi_control.

        Returns:
            Dict mit aktuellem Status
        """
        if not self.pi_interface:
            return {"state": "unknown", "error": "no_interface"}

        try:
            # Hole Presence-Daten von pi_control
            stats = self.pi_interface.bridge.presence_statistics
            is_home = stats.get("user_is_home", True)
            absence_active = stats.get("current_absence_active", False)
            day_mode = stats.get("current_day_mode", "unknown")

            old_state = self._current_state

            if is_home:
                self._current_state = PresenceState.HOME
                if self._absence_start:
                    # Abwesenheit beendet - lerne daraus
                    self._record_absence_end()
            else:
                # User ist weg - kategorisiere
                if absence_active and self._absence_start is None:
                    self._absence_start = datetime.now()

                duration = self._get_absence_duration()
                self._current_state = self._categorize_absence(duration)

                # Aktualisiere Vorhersage
                self._update_return_prediction(duration, day_mode)

            # State-Change loggen
            if old_state != self._current_state:
                logger.info(f"[Presence] State: {old_state.value} → {self._current_state.value}")
                self._log_state_change(self._current_state, is_home)
                self._last_check = datetime.now()

            return self.get_status()

        except Exception as e:
            logger.warning(f"[Presence] Update-Fehler: {e}")
            return {"state": "error", "error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Gibt aktuellen Presence-Status zurück"""
        return {
            "state": self._current_state.value,
            "is_home": self._current_state == PresenceState.HOME,
            "absence_duration_min": self._get_absence_duration(),
            "predicted_return": self._predicted_return.isoformat() if self._predicted_return else None,
            "prediction_confidence": self._prediction_confidence,
            "absence_category": self._get_absence_category_name(),
        }

    def get_context_for_holo(self) -> str:
        """Gibt Kontext-String für Holo zurück"""
        status = self.get_status()

        if status["is_home"]:
            return ""

        duration = status["absence_duration_min"]
        category = status["absence_category"]

        if category == "micro":
            return "[User ist kurz weg]"
        elif category == "short":
            return f"[User ist seit {duration:.0f} min weg - vermutlich Einkaufen/Spaziergang]"
        elif category == "work":
            if self._predicted_return:
                return_time = self._predicted_return.strftime("%H:%M")
                return f"[User ist bei der Arbeit - erwartet zurück ~{return_time}]"
            return f"[User ist bei der Arbeit (seit {duration:.0f} min)]"
        else:
            return f"[User ist länger weg (seit {duration/60:.1f}h)]"

    def predict_return(self) -> Optional[Dict]:
        """Sagt vorher wann User zurückkommt"""
        if self._current_state == PresenceState.HOME:
            return None

        if self._predicted_return:
            return {
                "expected_time": self._predicted_return.isoformat(),
                "confidence": self._prediction_confidence,
                "based_on": "historical_patterns"
            }
        return None

    def _get_absence_duration(self) -> float:
        """Gibt Abwesenheitsdauer in Minuten zurück"""
        if not self._absence_start:
            return 0
        return (datetime.now() - self._absence_start).total_seconds() / 60

    def _categorize_absence(self, duration_min: float) -> PresenceState:
        """Kategorisiert Abwesenheit nach Dauer"""
        for category, (min_dur, max_dur) in MetaConfig.ABSENCE_CATEGORIES.items():
            if max_dur is None:
                if duration_min >= min_dur:
                    return PresenceState(f"away_{category}")
            elif min_dur <= duration_min < max_dur:
                return PresenceState(f"away_{category}")
        return PresenceState.AWAY_MICRO

    def _get_absence_category_name(self) -> str:
        """Gibt Kategorie-Namen zurück"""
        state = self._current_state.value
        if state.startswith("away_"):
            return state[5:]
        return "none"

    def _update_return_prediction(self, current_duration: float, day_mode: str):
        """Aktualisiert Rückkehr-Vorhersage"""
        weekday = datetime.now().weekday()
        hour = datetime.now().hour

        # Hole historische Daten für diesen Wochentag
        if weekday in self._daily_patterns:
            pattern = self._daily_patterns[weekday]
            avg_duration = pattern.get("avg_work_duration", 480)  # Default 8h

            if day_mode in ["work", "arbeit"]:
                # Bei Arbeit: basierend auf typischer Arbeitsdauer
                remaining = max(0, avg_duration - current_duration)
                self._predicted_return = datetime.now() + timedelta(minutes=remaining)
                self._prediction_confidence = min(0.8, pattern.get("confidence", 0.5))
        else:
            # Keine historischen Daten - schätze
            if current_duration > 90:  # Wahrscheinlich Arbeit
                # Schätze 8h Arbeitstag
                remaining = max(0, 480 - current_duration)
                self._predicted_return = datetime.now() + timedelta(minutes=remaining)
                self._prediction_confidence = 0.3

    def _record_absence_end(self):
        """Speichert beendete Abwesenheit für Lernen"""
        if not self._absence_start:
            return

        duration = (datetime.now() - self._absence_start).total_seconds() / 60
        weekday = self._absence_start.weekday()
        hour = self._absence_start.hour

        # Berechne Vorhersage-Genauigkeit
        prediction_accuracy = None
        if self._predicted_return:
            actual_return = datetime.now()
            predicted_error_min = abs((actual_return - self._predicted_return).total_seconds() / 60)
            # Accuracy: 1.0 wenn exakt, 0.0 wenn > 60 min daneben
            prediction_accuracy = max(0.0, 1.0 - (predicted_error_min / 60))

        record = {
            "start": self._absence_start.isoformat(),
            "end": datetime.now().isoformat(),
            "duration_min": duration,
            "weekday": weekday,
            "start_hour": hour,
            "category": self._get_absence_category_name(),
            "predicted_return": self._predicted_return.isoformat() if self._predicted_return else None,
            "prediction_accuracy": prediction_accuracy,
        }

        self._absence_history.append(record)
        if len(self._absence_history) > 100:
            self._absence_history = self._absence_history[-100:]

        # In DB speichern
        self._save_absence(record)

        # Update daily patterns
        self._update_daily_pattern(record)

        # Reset
        self._absence_start = None
        self._predicted_return = None

        logger.info(f"[Presence] Abwesenheit beendet: {duration:.0f} min ({record['category']})")

    def _update_daily_pattern(self, record: Dict):
        """Aktualisiert Tagesmuster"""
        weekday = record["weekday"]

        if weekday not in self._daily_patterns:
            self._daily_patterns[weekday] = {
                "durations": [],
                "start_hours": [],
            }

        pattern = self._daily_patterns[weekday]
        pattern["durations"].append(record["duration_min"])
        pattern["start_hours"].append(record["start_hour"])

        # Berechne Statistiken
        if len(pattern["durations"]) >= 3:
            pattern["avg_absence_min"] = statistics.mean(pattern["durations"])
            pattern["typical_leave"] = statistics.mean(pattern["start_hours"])
            pattern["count"] = len(pattern["durations"])
            pattern["confidence"] = min(0.9, len(pattern["durations"]) / 20)

            # Berechne typische Rückkehrzeit (leave + avg_duration)
            avg_dur_hours = pattern["avg_absence_min"] / 60
            pattern["typical_return"] = pattern["typical_leave"] + avg_dur_hours

            # In DB speichern
            self._save_daily_pattern(weekday, pattern)


# =============================================================================
# SANDBOX SIMULATOR
# =============================================================================

class HoloSandbox:
    """
    Simuliert Aktionen vor Ausführung (A/B Testing).

    Ermöglicht:
    - Vergleich verschiedener Antwort-Optionen
    - Risiko-Bewertung
    - Vorhersage von User-Reaktionen
    """

    def __init__(self, db: 'HoloDatabaseManager' = None, data_dir: Path = None):
        self.db = db
        self.data_dir = data_dir or Path.home() / "holo_data" / "meta_cognition"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self.data_dir / "sandbox_decisions.db"

        # Historische Ergebnisse für Lernen
        self._outcome_history: Dict[str, List[Dict]] = defaultdict(list)
        self._action_success_rates: Dict[str, float] = {}

        # User-Reaktions-Modell
        self._user_preferences: Dict[str, float] = {}
        self._negative_patterns: List[str] = []

        # DB initialisieren und Historie laden
        self._init_db()
        self._load_history()

        logger.info("[Sandbox] Initialisiert mit DB-Persistenz")

    def _init_db(self):
        """Erstellt die Sandbox-Datenbank-Tabellen"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sandbox_decisions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    chosen_option TEXT NOT NULL,
                    confidence REAL,
                    risk_level REAL,
                    all_results_json TEXT,
                    reasoning TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sandbox_outcomes (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT,
                    action_hash TEXT,
                    context_hash TEXT,
                    success INTEGER,
                    user_reaction TEXT,
                    feedback_score REAL,
                    FOREIGN KEY (decision_id) REFERENCES sandbox_decisions(id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sandbox_patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_text TEXT NOT NULL,
                    success_rate REAL,
                    sample_count INTEGER,
                    last_seen TEXT,
                    is_negative INTEGER DEFAULT 0
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_decisions_ts ON sandbox_decisions(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_outcomes_ts ON sandbox_outcomes(timestamp)')
            conn.commit()

    def _load_history(self):
        """Lädt historische Daten aus der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Lade Outcomes für Success-Rates
                cursor = conn.execute('''
                    SELECT action_type, success FROM sandbox_outcomes
                    WHERE timestamp > datetime('now', '-30 days')
                    ORDER BY timestamp DESC
                ''')
                outcomes_by_type = defaultdict(list)
                for row in cursor:
                    outcomes_by_type[row['action_type']].append({
                        'success': bool(row['success'])
                    })

                # Berechne Success-Rates
                for action_type, outcomes in outcomes_by_type.items():
                    self._outcome_history[action_type] = outcomes
                    if len(outcomes) >= 5:
                        successes = sum(1 for o in outcomes[:20] if o['success'])
                        self._action_success_rates[action_type] = successes / min(20, len(outcomes))

                # Lade negative Patterns
                cursor = conn.execute('''
                    SELECT pattern_text FROM sandbox_patterns
                    WHERE is_negative = 1 AND sample_count >= 3
                ''')
                self._negative_patterns = [row['pattern_text'] for row in cursor]

                logger.info(f"[Sandbox] {len(self._action_success_rates)} Action-Types, "
                           f"{len(self._negative_patterns)} negative Patterns geladen")

        except Exception as e:
            logger.warning(f"[Sandbox] Konnte History nicht laden: {e}")

    def _save_decision(self, options: List[str], context: Dict,
                       chosen: str, result: 'SandboxResult', all_results: List['SandboxResult']):
        """Speichert eine Entscheidung in der DB"""
        try:
            decision_id = hashlib.md5(
                f"{datetime.now().isoformat()}{chosen}".encode()
            ).hexdigest()[:16]

            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT INTO sandbox_decisions
                    (id, timestamp, options_json, context_json, chosen_option,
                     confidence, risk_level, all_results_json, reasoning)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision_id,
                    datetime.now().isoformat(),
                    json.dumps(options, ensure_ascii=False),
                    json.dumps(context, ensure_ascii=False),
                    chosen,
                    result.confidence if result else 0.5,
                    result.risk_level if result else 0.2,
                    json.dumps([{
                        'option': r.option[:200],
                        'confidence': r.confidence,
                        'risk': r.risk_level,
                        'predicted_outcome': r.predicted_outcome
                    } for r in all_results], ensure_ascii=False),
                    result.predicted_outcome if result else None
                ))
                conn.commit()

            return decision_id
        except Exception as e:
            logger.warning(f"[Sandbox] Konnte Entscheidung nicht speichern: {e}")
            return None

    def evaluate_options(self, options: List[str], context: Dict) -> List[SandboxResult]:
        """
        Bewertet mehrere Optionen und gibt Ranking zurück.

        Args:
            options: Liste von möglichen Aktionen/Antworten
            context: Aktueller Kontext (Stimmung, Thema, etc.)

        Returns:
            Sortierte Liste von SandboxResults (beste zuerst)
        """
        results = []

        for option in options:
            result = self._simulate_option(option, context)
            results.append(result)

        # Sortiere nach Confidence * (1 - Risk)
        results.sort(key=lambda r: r.confidence * (1 - r.risk_level), reverse=True)

        return results

    def choose_best(self, options: List[str], context: Dict) -> Tuple[str, SandboxResult]:
        """
        Wählt die beste Option aus.

        Returns:
            (gewählte_option, SandboxResult)
        """
        if not options:
            return None, None

        results = self.evaluate_options(options, context)
        best = results[0]

        # Speichere Entscheidung in DB für spätere Nachvollziehbarkeit
        self._save_decision(options, context, best.option, best, results)

        logger.debug(f"[Sandbox] Beste Option: {best.option[:50]}... (conf={best.confidence:.2f})")

        return best.option, best

    def record_outcome(self, action: str, context: Dict,
                       success: bool, user_reaction: str = None,
                       decision_id: str = None):
        """
        Speichert das tatsächliche Ergebnis einer Aktion.

        Wird aufgerufen nachdem eine Aktion ausgeführt wurde.
        Speichert sowohl im RAM als auch in der DB.
        """
        action_type = self._categorize_action(action)

        outcome = {
            "timestamp": datetime.now().isoformat(),
            "action_hash": self._hash_action(action),
            "context_hash": self._hash_context(context),
            "success": success,
            "user_reaction": user_reaction,
        }

        # Im RAM speichern
        self._outcome_history[action_type].append(outcome)

        # Update success rate
        history = self._outcome_history[action_type]
        if len(history) >= 5:
            successes = sum(1 for o in history[-20:] if o["success"])
            self._action_success_rates[action_type] = successes / min(20, len(history))

        # In DB speichern
        self._save_outcome(action, action_type, context, success, user_reaction, decision_id)

        # Lerne von negativen Reaktionen
        if not success and user_reaction:
            self._learn_negative_pattern(action, user_reaction)

    def _save_outcome(self, action: str, action_type: str, context: Dict,
                      success: bool, user_reaction: str, decision_id: str = None):
        """Speichert Outcome in der DB"""
        try:
            outcome_id = hashlib.md5(
                f"{datetime.now().isoformat()}{action[:50]}".encode()
            ).hexdigest()[:16]

            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT INTO sandbox_outcomes
                    (id, decision_id, timestamp, action_type, action_hash,
                     context_hash, success, user_reaction, feedback_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    outcome_id,
                    decision_id,
                    datetime.now().isoformat(),
                    action_type,
                    self._hash_action(action),
                    self._hash_context(context),
                    1 if success else 0,
                    user_reaction,
                    1.0 if success else 0.0
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"[Sandbox] Konnte Outcome nicht speichern: {e}")

    def get_decision_history(self, limit: int = 50) -> List[Dict]:
        """
        Gibt die letzten Entscheidungen zurück für Nachvollziehbarkeit.

        Returns:
            Liste von Entscheidungen mit allen Details
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT d.*,
                           o.success as outcome_success,
                           o.user_reaction as outcome_reaction
                    FROM sandbox_decisions d
                    LEFT JOIN sandbox_outcomes o ON o.decision_id = d.id
                    ORDER BY d.timestamp DESC
                    LIMIT ?
                ''', (limit,))

                decisions = []
                for row in cursor:
                    decisions.append({
                        'id': row['id'],
                        'timestamp': row['timestamp'],
                        'options': json.loads(row['options_json']),
                        'context': json.loads(row['context_json']),
                        'chosen': row['chosen_option'],
                        'confidence': row['confidence'],
                        'risk': row['risk_level'],
                        'reasoning': row['reasoning'],
                        'outcome_success': row['outcome_success'],
                        'outcome_reaction': row['outcome_reaction'],
                    })
                return decisions
        except Exception as e:
            logger.warning(f"[Sandbox] Konnte History nicht laden: {e}")
            return []

    def explain_decision(self, decision_id: str) -> str:
        """
        Erklärt warum eine bestimmte Entscheidung getroffen wurde.

        Args:
            decision_id: ID der Entscheidung

        Returns:
            Erklärungstext
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM sandbox_decisions WHERE id = ?
                ''', (decision_id,))
                row = cursor.fetchone()

                if not row:
                    return f"Entscheidung {decision_id} nicht gefunden."

                options = json.loads(row['options_json'])
                all_results = json.loads(row['all_results_json'])
                context = json.loads(row['context_json'])

                lines = [
                    f"=== Entscheidung {decision_id} ===",
                    f"Zeitpunkt: {row['timestamp']}",
                    f"",
                    f"Kontext: {json.dumps(context, ensure_ascii=False, indent=2)}",
                    f"",
                    f"Optionen ({len(options)}):",
                ]

                for i, result in enumerate(all_results):
                    marker = "→" if result['option'][:50] == row['chosen_option'][:50] else " "
                    lines.append(
                        f"  {marker} [{i+1}] \"{result['option'][:60]}...\" "
                        f"(conf={result['confidence']:.2f}, risk={result['risk']:.2f})"
                    )

                lines.extend([
                    f"",
                    f"Gewählt: \"{row['chosen_option'][:80]}...\"",
                    f"Begründung: {row['reasoning']}",
                    f"Confidence: {row['confidence']:.2f}",
                    f"Risiko: {row['risk_level']:.2f}",
                ])

                # Check outcome
                cursor = conn.execute('''
                    SELECT * FROM sandbox_outcomes WHERE decision_id = ?
                ''', (decision_id,))
                outcome = cursor.fetchone()
                if outcome:
                    lines.extend([
                        f"",
                        f"=== Ergebnis ===",
                        f"Erfolgreich: {'Ja' if outcome['success'] else 'Nein'}",
                        f"User-Reaktion: {outcome['user_reaction'] or 'Keine'}",
                    ])

                return "\n".join(lines)
        except Exception as e:
            return f"Fehler beim Laden der Erklärung: {e}"

    def _simulate_option(self, option: str, context: Dict) -> SandboxResult:
        """Simuliert eine einzelne Option"""
        action_type = self._categorize_action(option)

        # Basis-Confidence aus historischen Daten
        base_confidence = self._action_success_rates.get(action_type, 0.5)

        # Kontext-Anpassungen
        confidence = base_confidence
        risk = 0.2  # Basis-Risiko

        # Prüfe auf negative Muster
        for pattern in self._negative_patterns:
            if pattern.lower() in option.lower():
                confidence *= 0.7
                risk += 0.2

        # Kontext-basierte Anpassungen
        mood = context.get("user_mood", "neutral")
        if mood == "negative" and self._is_risky_action(option):
            risk += 0.3
            confidence *= 0.8

        # Längen-basierte Risiko-Bewertung
        if len(option) > 500:
            risk += 0.1  # Lange Antworten sind riskanter

        # Generiere Vorhersagen
        predicted_outcome = self._predict_outcome(option, context)
        predicted_reaction = self._predict_user_reaction(option, context)
        benefits = self._identify_benefits(option, context)
        drawbacks = self._identify_drawbacks(option, context)

        return SandboxResult(
            option=option,
            predicted_outcome=predicted_outcome,
            confidence=min(0.95, max(0.1, confidence)),
            predicted_user_reaction=predicted_reaction,
            risk_level=min(1.0, max(0.0, risk)),
            benefits=benefits,
            drawbacks=drawbacks,
            recommendation=self._generate_recommendation(confidence, risk)
        )

    def _categorize_action(self, action: str) -> str:
        """Kategorisiert eine Aktion"""
        action_lower = action.lower()

        if "?" in action:
            return "question"
        elif any(w in action_lower for w in ["sorry", "entschuldigung", "tut mir leid"]):
            return "apology"
        elif any(w in action_lower for w in ["danke", "freut mich", "gerne"]):
            return "positive"
        elif any(w in action_lower for w in ["erkläre", "hier ist", "also"]):
            return "explanation"
        elif any(w in action_lower for w in ["weiß nicht", "unsicher", "vielleicht"]):
            return "uncertain"
        else:
            return "statement"

    def _hash_action(self, action: str) -> str:
        """Erstellt Hash einer Aktion"""
        return hashlib.md5(action.encode()).hexdigest()[:8]

    def _hash_context(self, context: Dict) -> str:
        """Erstellt Hash eines Kontexts"""
        key_parts = [
            context.get("topic", ""),
            context.get("mood", ""),
            str(context.get("turn_count", 0) // 5),  # Gruppiert in 5er-Schritten
        ]
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()[:8]

    def _is_risky_action(self, action: str) -> bool:
        """Prüft ob Aktion riskant ist"""
        risky_patterns = [
            "solltest", "musst", "falsch", "nein", "aber",
            "eigentlich", "tatsächlich", "korrektur"
        ]
        return any(p in action.lower() for p in risky_patterns)

    def _predict_outcome(self, option: str, context: Dict) -> str:
        """Sagt Outcome vorher"""
        action_type = self._categorize_action(option)
        success_rate = self._action_success_rates.get(action_type, 0.5)

        if success_rate > 0.7:
            return "Wahrscheinlich positive Reaktion"
        elif success_rate > 0.4:
            return "Neutrale Reaktion erwartet"
        else:
            return "Risiko negativer Reaktion"

    def _predict_user_reaction(self, option: str, context: Dict) -> str:
        """Sagt User-Reaktion vorher"""
        if "?" in option:
            return "User wird antworten"
        elif len(option) > 300:
            return "User liest aufmerksam oder überspringt"
        else:
            return "User nimmt Information auf"

    def _identify_benefits(self, option: str, context: Dict) -> List[str]:
        """Identifiziert Vorteile der Option"""
        benefits = []

        if "?" in option:
            benefits.append("Fördert Dialog")
        if any(w in option.lower() for w in ["interessant", "spannend", "cool"]):
            benefits.append("Zeigt Interesse")
        if len(option) < 100:
            benefits.append("Kurz und prägnant")

        return benefits or ["Standard-Antwort"]

    def _identify_drawbacks(self, option: str, context: Dict) -> List[str]:
        """Identifiziert Nachteile der Option"""
        drawbacks = []

        if len(option) > 500:
            drawbacks.append("Möglicherweise zu lang")
        if self._is_risky_action(option):
            drawbacks.append("Könnte als kritisch wahrgenommen werden")

        return drawbacks

    def _generate_recommendation(self, confidence: float, risk: float) -> str:
        """Generiert Empfehlung"""
        score = confidence * (1 - risk)

        if score > 0.7:
            return "Empfohlen"
        elif score > 0.4:
            return "Akzeptabel"
        else:
            return "Mit Vorsicht"

    def _learn_negative_pattern(self, action: str, reaction: str):
        """Lernt aus negativen Reaktionen"""
        # Extrahiere Schlüsselwörter aus der Aktion
        words = action.lower().split()
        # Füge auffällige Wörter zu negativen Mustern hinzu
        for word in words:
            if len(word) > 4 and word not in self._negative_patterns:
                # Vereinfachte Heuristik - in Produktion würde man ML nutzen
                if reaction and any(neg in reaction.lower() for neg in ["nicht", "nein", "falsch"]):
                    self._negative_patterns.append(word)
                    if len(self._negative_patterns) > 50:
                        self._negative_patterns = self._negative_patterns[-50:]


# =============================================================================
# META OBSERVER - Die Kern-Komponente
# =============================================================================

class HoloMetaObserver:
    """
    Beobachtet das gesamte Holo-System und lernt daraus.

    Diese Meta-Schicht:
    - Beobachtet alle Komponenten-Aufrufe
    - Analysiert Entscheidungsmuster
    - Versteht Ursache-Wirkung zwischen Komponenten
    - Lernt was funktioniert und was nicht
    - Generiert Einsichten über das eigene Verhalten
    """

    def __init__(self, db: 'HoloDatabaseManager' = None, data_dir: Path = None):
        self.db = db
        self.data_dir = data_dir or Path.home() / "holo_data" / "meta_cognition"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self.data_dir / "meta_observations.db"

        # Beobachtungen
        self._observations: deque = deque(maxlen=MetaConfig.MAX_OBSERVATIONS)
        self._component_calls: Dict[str, List[Dict]] = defaultdict(list)

        # Gelernte Muster
        self._patterns: Dict[str, LearnedPattern] = {}
        self._component_insights: Dict[str, ComponentInsight] = {}

        # Kausale Beziehungen zwischen Komponenten
        self._component_chains: Dict[str, List[str]] = defaultdict(list)
        self._cause_effect: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Aktuelle Session-Metriken
        self._session_start = datetime.now()
        self._session_stats = {
            "total_observations": 0,
            "decisions_made": 0,
            "errors_caught": 0,
            "patterns_learned": 0,
        }

        # Pending Observation für Chain-Tracking
        self._pending_chain: List[str] = []

        # DB initialisieren und gelernte Patterns laden
        self._init_db()
        self._load_learned_patterns()

        logger.info("[MetaObserver] Initialisiert mit DB-Persistenz")

    def _init_db(self):
        """Erstellt die Beobachtungs-Datenbank-Tabellen"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS observations (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    observation_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    action TEXT NOT NULL,
                    context_json TEXT,
                    outcome TEXT,
                    success INTEGER,
                    duration_ms REAL,
                    related_json TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_key TEXT NOT NULL UNIQUE,
                    success_rate REAL,
                    avg_duration_ms REAL,
                    sample_count INTEGER,
                    confidence REAL,
                    last_updated TEXT,
                    context_json TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cause_effect (
                    id TEXT PRIMARY KEY,
                    cause_component TEXT NOT NULL,
                    effect_component TEXT NOT NULL,
                    strength REAL,
                    occurrences INTEGER,
                    last_seen TEXT,
                    UNIQUE(cause_component, effect_component)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS component_insights (
                    id TEXT PRIMARY KEY,
                    component TEXT NOT NULL UNIQUE,
                    purpose TEXT,
                    common_actions_json TEXT,
                    success_rate REAL,
                    avg_duration_ms REAL,
                    call_count INTEGER,
                    last_updated TEXT
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_obs_ts ON observations(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_obs_comp ON observations(component)')
            conn.commit()

    def _load_learned_patterns(self):
        """Lädt gelernte Patterns aus der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Lade Patterns
                cursor = conn.execute('SELECT * FROM learned_patterns')
                for row in cursor:
                    self._patterns[row['pattern_key']] = LearnedPattern(
                        pattern_type=row['pattern_type'],
                        key=row['pattern_key'],
                        success_rate=row['success_rate'],
                        avg_duration_ms=row['avg_duration_ms'],
                        sample_count=row['sample_count'],
                        confidence=row['confidence'],
                        context=json.loads(row['context_json']) if row['context_json'] else {}
                    )

                # Lade Cause-Effect
                cursor = conn.execute('SELECT * FROM cause_effect')
                for row in cursor:
                    self._cause_effect[row['cause_component']][row['effect_component']] = row['strength']

                # Lade Component Insights
                cursor = conn.execute('SELECT * FROM component_insights')
                for row in cursor:
                    self._component_insights[row['component']] = ComponentInsight(
                        component=row['component'],
                        purpose=row['purpose'],
                        common_actions=json.loads(row['common_actions_json']) if row['common_actions_json'] else [],
                        success_rate=row['success_rate'],
                        avg_duration_ms=row['avg_duration_ms'],
                        call_count=row['call_count'],
                    )

                logger.info(f"[MetaObserver] {len(self._patterns)} Patterns, "
                           f"{sum(len(v) for v in self._cause_effect.values())} Cause-Effects, "
                           f"{len(self._component_insights)} Insights geladen")

        except Exception as e:
            logger.warning(f"[MetaObserver] Konnte Patterns nicht laden: {e}")

    def _save_observation(self, obs: 'SystemObservation'):
        """Speichert eine Beobachtung in der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO observations
                    (id, timestamp, observation_type, component, action,
                     context_json, outcome, success, duration_ms, related_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    obs.id,
                    obs.timestamp,
                    obs.observation_type.value if isinstance(obs.observation_type, Enum) else obs.observation_type,
                    obs.component,
                    obs.action,
                    json.dumps(obs.context, ensure_ascii=False),
                    obs.outcome,
                    1 if obs.success else 0 if obs.success is not None else None,
                    obs.duration_ms,
                    json.dumps(obs.related_observations, ensure_ascii=False)
                ))
                conn.commit()
        except Exception as e:
            logger.debug(f"[MetaObserver] Konnte Observation nicht speichern: {e}")

    def _save_pattern(self, pattern: 'LearnedPattern'):
        """Speichert ein Pattern in der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO learned_patterns
                    (id, pattern_type, pattern_key, success_rate, avg_duration_ms,
                     sample_count, confidence, last_updated, context_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    hashlib.md5(pattern.key.encode()).hexdigest()[:16],
                    pattern.pattern_type,
                    pattern.key,
                    pattern.success_rate,
                    pattern.avg_duration_ms,
                    pattern.sample_count,
                    pattern.confidence,
                    datetime.now().isoformat(),
                    json.dumps(pattern.context, ensure_ascii=False)
                ))
                conn.commit()
        except Exception as e:
            logger.debug(f"[MetaObserver] Konnte Pattern nicht speichern: {e}")

    def _save_cause_effect(self, cause: str, effect: str, strength: float, occurrences: int):
        """Speichert Cause-Effect Beziehung in der DB"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cause_effect
                    (id, cause_component, effect_component, strength, occurrences, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    hashlib.md5(f"{cause}->{effect}".encode()).hexdigest()[:16],
                    cause,
                    effect,
                    strength,
                    occurrences,
                    datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.debug(f"[MetaObserver] Konnte Cause-Effect nicht speichern: {e}")

    def get_observation_history(self, component: str = None, limit: int = 100) -> List[Dict]:
        """
        Gibt Beobachtungshistorie für Nachvollziehbarkeit zurück.

        Args:
            component: Optionaler Filter für bestimmte Komponente
            limit: Maximale Anzahl

        Returns:
            Liste von Beobachtungen
        """
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                if component:
                    cursor = conn.execute('''
                        SELECT * FROM observations
                        WHERE component = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (component, limit))
                else:
                    cursor = conn.execute('''
                        SELECT * FROM observations
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (limit,))

                return [{
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'type': row['observation_type'],
                    'component': row['component'],
                    'action': row['action'],
                    'outcome': row['outcome'],
                    'success': bool(row['success']) if row['success'] is not None else None,
                    'duration_ms': row['duration_ms'],
                } for row in cursor]
        except Exception as e:
            logger.warning(f"[MetaObserver] Konnte History nicht laden: {e}")
            return []

    # =========================================================================
    # BEOBACHTUNG
    # =========================================================================

    def observe(self, observation_type: ObservationType, component: str,
                action: str, context: Dict = None, outcome: str = None,
                success: bool = None, duration_ms: float = None):
        """
        Zeichnet eine Beobachtung auf.

        Wird von anderen Komponenten aufgerufen um Meta-Lernen zu ermöglichen.
        """
        obs = SystemObservation(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            observation_type=observation_type,
            component=component,
            action=action,
            context=context or {},
            outcome=outcome,
            success=success,
            duration_ms=duration_ms,
            related_observations=list(self._pending_chain[-3:]),
        )

        self._observations.append(obs)
        self._session_stats["total_observations"] += 1

        # In DB speichern
        self._save_observation(obs)

        # Track component call
        self._component_calls[component].append({
            "time": obs.timestamp,
            "action": action,
            "success": success,
            "duration_ms": duration_ms,
        })

        # Update chain
        self._pending_chain.append(obs.id)
        if len(self._pending_chain) > 10:
            self._pending_chain = self._pending_chain[-10:]

        # Track cause-effect
        if len(self._pending_chain) >= 2:
            prev_id = self._pending_chain[-2]
            prev_obs = self._find_observation(prev_id)
            if prev_obs:
                self._track_cause_effect(prev_obs.component, component)

        # Typ-spezifische Stats
        if observation_type == ObservationType.DECISION:
            self._session_stats["decisions_made"] += 1
        elif observation_type == ObservationType.ERROR:
            self._session_stats["errors_caught"] += 1

        # Periodische Muster-Analyse
        if self._session_stats["total_observations"] % 50 == 0:
            self._analyze_patterns()

    def observe_decision(self, component: str, options: List[str],
                        chosen: str, reason: str, context: Dict = None):
        """Spezialisierte Beobachtung für Entscheidungen"""
        self.observe(
            ObservationType.DECISION,
            component=component,
            action=f"chose: {chosen[:50]}...",
            context={
                **(context or {}),
                "options_count": len(options),
                "reason": reason,
            }
        )

    def observe_error(self, component: str, error: str,
                     context: Dict = None, recovered: bool = False):
        """Spezialisierte Beobachtung für Fehler"""
        self.observe(
            ObservationType.ERROR,
            component=component,
            action=f"error: {error[:100]}",
            context={
                **(context or {}),
                "recovered": recovered,
            },
            success=recovered,
        )

    def observe_component_call(self, component: str, method: str,
                               duration_ms: float = None, success: bool = True):
        """Spezialisierte Beobachtung für Komponenten-Aufrufe"""
        self.observe(
            ObservationType.COMPONENT_CALL,
            component=component,
            action=method,
            duration_ms=duration_ms,
            success=success,
        )

    # =========================================================================
    # ANALYSE & LERNEN
    # =========================================================================

    def _analyze_patterns(self):
        """Analysiert gesammelte Beobachtungen auf Muster"""
        # Analysiere Komponenten-Ketten
        self._analyze_component_chains()

        # Analysiere Erfolgsraten
        self._analyze_success_patterns()

        # Analysiere Zeitliche Muster
        self._analyze_temporal_patterns()

        self._session_stats["patterns_learned"] = len(self._patterns)

        # Speichere alle Patterns in DB
        for pattern in self._patterns.values():
            self._save_pattern(pattern)

        # Speichere Cause-Effect Beziehungen
        for cause, effects in self._cause_effect.items():
            for effect, strength in effects.items():
                self._save_cause_effect(cause, effect, strength, 1)

    def _analyze_component_chains(self):
        """Findet häufige Komponenten-Aufruf-Ketten"""
        # Baue Sequenzen aus Beobachtungen
        recent = list(self._observations)[-200:]

        for i in range(len(recent) - 2):
            chain = [
                recent[i].component,
                recent[i+1].component,
                recent[i+2].component,
            ]
            chain_key = " → ".join(chain)

            if chain_key not in self._component_chains:
                self._component_chains[chain_key] = []
            self._component_chains[chain_key].append({
                "time": recent[i].timestamp,
                "success": all(o.success for o in [recent[i], recent[i+1], recent[i+2]] if o.success is not None)
            })

        # Erstelle Patterns aus häufigen Ketten
        for chain_key, occurrences in self._component_chains.items():
            if len(occurrences) >= MetaConfig.MIN_SAMPLES_FOR_PATTERN:
                success_rate = sum(1 for o in occurrences if o.get("success", True)) / len(occurrences)

                pattern_id = f"chain_{hashlib.md5(chain_key.encode()).hexdigest()[:8]}"
                self._patterns[pattern_id] = LearnedPattern(
                    id=pattern_id,
                    pattern_type="component_chain",
                    description=f"Häufige Aufruf-Kette: {chain_key}",
                    conditions={"chain": chain_key},
                    typical_outcome="normal_flow" if success_rate > 0.8 else "sometimes_fails",
                    confidence=min(0.9, len(occurrences) / 50),
                    sample_count=len(occurrences),
                    first_seen=occurrences[0]["time"],
                    last_seen=occurrences[-1]["time"],
                    success_rate=success_rate,
                )

    def _analyze_success_patterns(self):
        """Analysiert was zu Erfolg/Misserfolg führt"""
        for component, calls in self._component_calls.items():
            if len(calls) < 10:
                continue

            recent = calls[-50:]
            successes = [c for c in recent if c.get("success", True)]
            failures = [c for c in recent if c.get("success") == False]

            if failures:
                # Analysiere was bei Fehlern anders war
                fail_actions = [f["action"] for f in failures]

                pattern_id = f"fail_{component}"
                self._patterns[pattern_id] = LearnedPattern(
                    id=pattern_id,
                    pattern_type="failure_pattern",
                    description=f"{component} versagt bei bestimmten Aktionen",
                    conditions={"component": component, "problematic_actions": fail_actions[:5]},
                    typical_outcome="failure",
                    confidence=len(failures) / len(recent),
                    sample_count=len(failures),
                    first_seen=failures[0]["time"],
                    last_seen=failures[-1]["time"],
                    success_rate=len(successes) / len(recent),
                )

    def _analyze_temporal_patterns(self):
        """Analysiert zeitliche Muster"""
        recent = list(self._observations)[-100:]

        # Gruppiere nach Stunde
        hourly = defaultdict(list)
        for obs in recent:
            try:
                hour = datetime.fromisoformat(obs.timestamp).hour
                hourly[hour].append(obs)
            except Exception:
                pass  # Invalid timestamp format, skip this observation

        # Finde auffällige Stunden
        for hour, obs_list in hourly.items():
            if len(obs_list) >= 5:
                error_count = sum(1 for o in obs_list if o.observation_type == ObservationType.ERROR)
                if error_count > len(obs_list) * 0.3:
                    pattern_id = f"temporal_error_{hour}"
                    self._patterns[pattern_id] = LearnedPattern(
                        id=pattern_id,
                        pattern_type="temporal_pattern",
                        description=f"Erhöhte Fehlerrate um {hour}:00 Uhr",
                        conditions={"hour": hour, "error_rate": error_count / len(obs_list)},
                        typical_outcome="more_errors",
                        confidence=0.6,
                        sample_count=len(obs_list),
                        first_seen=obs_list[0].timestamp,
                        last_seen=obs_list[-1].timestamp,
                    )

    def _track_cause_effect(self, cause_component: str, effect_component: str):
        """Trackt Ursache-Wirkung zwischen Komponenten"""
        if cause_component not in self._cause_effect:
            self._cause_effect[cause_component] = {}

        if effect_component not in self._cause_effect[cause_component]:
            self._cause_effect[cause_component][effect_component] = 0

        self._cause_effect[cause_component][effect_component] += 1

    # =========================================================================
    # KOMPONENTEN-INSIGHTS
    # =========================================================================

    def analyze_component(self, component_name: str) -> ComponentInsight:
        """
        Analysiert eine einzelne Komponente.

        Returns:
            Detaillierte Insights über die Komponente
        """
        calls = self._component_calls.get(component_name, [])

        if not calls:
            return ComponentInsight(
                component_name=component_name,
                purpose="Unbekannt (keine Beobachtungen)",
                typical_usage=[],
                dependencies=[],
                dependents=[],
                avg_response_time_ms=0,
                success_rate=0,
                common_errors=[],
                last_analyzed=datetime.now().isoformat(),
            )

        # Berechne Metriken
        durations = [c["duration_ms"] for c in calls if c.get("duration_ms")]
        successes = sum(1 for c in calls if c.get("success", True))

        # Finde Dependencies aus cause_effect
        dependencies = []
        for cause, effects in self._cause_effect.items():
            if component_name in effects and effects[component_name] > 3:
                dependencies.append(cause)

        # Finde Dependents
        dependents = list(self._cause_effect.get(component_name, {}).keys())

        # Finde häufige Aktionen
        action_counts = defaultdict(int)
        for c in calls:
            action_counts[c["action"]] += 1
        typical_usage = sorted(action_counts.keys(), key=lambda a: action_counts[a], reverse=True)[:5]

        # Finde Fehler
        errors = [c["action"] for c in calls if not c.get("success", True)]

        insight = ComponentInsight(
            component_name=component_name,
            purpose=self._infer_purpose(component_name, typical_usage),
            typical_usage=typical_usage,
            dependencies=dependencies[:5],
            dependents=dependents[:5],
            avg_response_time_ms=statistics.mean(durations) if durations else 0,
            success_rate=successes / len(calls) if calls else 0,
            common_errors=list(set(errors))[:5],
            last_analyzed=datetime.now().isoformat(),
        )

        self._component_insights[component_name] = insight
        return insight

    def _infer_purpose(self, component_name: str, typical_actions: List[str]) -> str:
        """Leitet Zweck einer Komponente ab"""
        name_lower = component_name.lower()

        purpose_hints = {
            "learning": "Lernen und Wissensaufbau",
            "emotion": "Emotionsverarbeitung",
            "memory": "Gedächtnisspeicherung",
            "reasoning": "Logisches Denken",
            "personality": "Persönlichkeitsausdruck",
            "consciousness": "Bewusstseinsmodellierung",
            "dialogue": "Dialogführung",
            "nlp": "Sprachverarbeitung",
            "context": "Kontextverwaltung",
            "energy": "Energiemanagement",
            "self": "Selbstreflexion",
            "skill": "Fähigkeitsverwaltung",
            "database": "Datenpersistenz",
        }

        for hint, purpose in purpose_hints.items():
            if hint in name_lower:
                return purpose

        return f"Verarbeitung von: {', '.join(typical_actions[:3])}"

    # =========================================================================
    # SELBSTREFLEXION
    # =========================================================================

    def get_self_reflection(self) -> Dict[str, Any]:
        """
        Generiert eine Selbstreflexion über das System.

        Returns:
            Dict mit Erkenntnissen über das eigene Verhalten
        """
        # Analysiere zuerst
        self._analyze_patterns()

        # Sammle Insights
        active_components = list(self._component_calls.keys())

        # Top Patterns
        top_patterns = sorted(
            self._patterns.values(),
            key=lambda p: p.sample_count,
            reverse=True
        )[:5]

        # Problematische Bereiche
        problems = [p for p in self._patterns.values() if p.success_rate < 0.7]

        # Stärken
        strengths = [p for p in self._patterns.values() if p.success_rate > 0.9]

        # Generiere Reflexions-Text
        reflection_text = self._generate_reflection_text(
            active_components, top_patterns, problems, strengths
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "session_duration_min": (datetime.now() - self._session_start).seconds / 60,
            "session_stats": self._session_stats,
            "active_components": active_components,
            "patterns_found": len(self._patterns),
            "top_patterns": [p.to_dict() for p in top_patterns],
            "problems": [p.to_dict() for p in problems[:3]],
            "strengths": [p.to_dict() for p in strengths[:3]],
            "component_relationships": dict(self._cause_effect),
            "reflection": reflection_text,
        }

    def _generate_reflection_text(self, components: List[str],
                                   patterns: List[LearnedPattern],
                                   problems: List[LearnedPattern],
                                   strengths: List[LearnedPattern]) -> str:
        """Generiert lesbaren Reflexions-Text"""
        lines = [
            "=== SELBSTREFLEXION ===",
            "",
            f"Ich habe {len(components)} aktive Komponenten beobachtet.",
            f"Dabei wurden {len(patterns)} Verhaltensmuster identifiziert.",
            "",
        ]

        if strengths:
            lines.append("STÄRKEN:")
            for s in strengths[:3]:
                lines.append(f"  • {s.description} (Erfolgsrate: {s.success_rate:.0%})")
            lines.append("")

        if problems:
            lines.append("VERBESSERUNGSBEREICHE:")
            for p in problems[:3]:
                lines.append(f"  • {p.description} (Erfolgsrate: {p.success_rate:.0%})")
            lines.append("")

        # Wichtigste Erkenntnisse
        if patterns:
            lines.append("WICHTIGSTE ERKENNTNISSE:")
            for p in patterns[:3]:
                lines.append(f"  • {p.description}")

        return "\n".join(lines)

    def explain_component(self, component_name: str) -> str:
        """
        Erklärt was eine Komponente tut basierend auf Beobachtungen.
        """
        insight = self.analyze_component(component_name)

        lines = [
            f"=== {component_name} ===",
            f"Zweck: {insight.purpose}",
            f"Erfolgsrate: {insight.success_rate:.0%}",
            f"Durchschnittliche Antwortzeit: {insight.avg_response_time_ms:.1f}ms",
            "",
        ]

        if insight.typical_usage:
            lines.append("Typische Verwendung:")
            for use in insight.typical_usage:
                lines.append(f"  • {use}")

        if insight.dependencies:
            lines.append(f"\nBraucht: {', '.join(insight.dependencies)}")

        if insight.dependents:
            lines.append(f"Wird gebraucht von: {', '.join(insight.dependents)}")

        if insight.common_errors:
            lines.append("\nHäufige Probleme:")
            for err in insight.common_errors:
                lines.append(f"  • {err}")

        return "\n".join(lines)

    def why_did_i(self, action_description: str) -> str:
        """
        Erklärt warum eine bestimmte Aktion durchgeführt wurde.

        Sucht in RAM UND DB nach passenden Entscheidungen und Beobachtungen.
        """
        explanation_parts = []

        # 1. Suche in RAM-Beobachtungen
        relevant_ram = []
        for obs in self._observations:
            if action_description.lower() in obs.action.lower():
                relevant_ram.append(obs)

        # 2. Suche in DB-Beobachtungen (für ältere Daten)
        relevant_db = []
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM observations
                    WHERE action LIKE ? OR outcome LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT 20
                ''', (f'%{action_description}%', f'%{action_description}%'))
                relevant_db = list(cursor)
        except Exception as e:
            logger.debug(f"DB-Suche fehlgeschlagen: {e}")

        if not relevant_ram and not relevant_db:
            return f"Keine Aufzeichnungen zu '{action_description}' gefunden."

        explanation_parts.append(f"=== Warum '{action_description}'? ===\n")

        # Analysiere RAM-Beobachtungen
        if relevant_ram:
            obs = relevant_ram[-1]  # Neueste
            explanation_parts.append(f"📍 Letzte Beobachtung (Session):")
            explanation_parts.append(f"   Zeitpunkt: {obs.timestamp}")
            explanation_parts.append(f"   Komponente: {obs.component}")
            explanation_parts.append(f"   Aktion: {obs.action}")
            if obs.context:
                explanation_parts.append(f"   Kontext: {json.dumps(obs.context, ensure_ascii=False)}")
            if obs.outcome:
                explanation_parts.append(f"   Ergebnis: {obs.outcome}")
            if obs.success is not None:
                explanation_parts.append(f"   Erfolgreich: {'Ja' if obs.success else 'Nein'}")

            # Finde vorherige Beobachtungen in der Kette
            chain = []
            for related_id in obs.related_observations:
                related = self._find_observation(related_id)
                if related:
                    chain.append(f"{related.component}: {related.action}")
            if chain:
                explanation_parts.append("\n   Auslöser-Kette:")
                for step in chain:
                    explanation_parts.append(f"      → {step}")

        # Analysiere DB-Beobachtungen (Historie)
        if relevant_db:
            explanation_parts.append(f"\n📚 Historische Daten ({len(relevant_db)} Einträge):")
            for i, row in enumerate(relevant_db[:5]):
                explanation_parts.append(
                    f"   [{i+1}] {row['timestamp'][:16]} - {row['component']}.{row['action']}"
                    f" ({'✓' if row['success'] else '✗'})"
                )

            # Berechne Erfolgsrate für diese Aktion
            successes = sum(1 for r in relevant_db if r['success'])
            success_rate = successes / len(relevant_db) if relevant_db else 0
            explanation_parts.append(f"\n   Erfolgsrate für diese Aktion: {success_rate:.0%}")

        # Suche nach passenden Patterns
        matching_patterns = []
        for pattern in self._patterns.values():
            if action_description.lower() in pattern.key.lower():
                matching_patterns.append(pattern)

        if matching_patterns:
            explanation_parts.append("\n🧠 Gelernte Muster:")
            for p in matching_patterns[:3]:
                explanation_parts.append(
                    f"   • {p.key}: Erfolgsrate {p.success_rate:.0%} "
                    f"(basierend auf {p.sample_count} Beobachtungen)"
                )

        # Suche nach Ursache-Wirkung
        for cause, effects in self._cause_effect.items():
            if action_description.lower() in cause.lower():
                explanation_parts.append(f"\n🔗 Führt typischerweise zu:")
                for effect, strength in effects.items():
                    explanation_parts.append(f"   → {effect} (Stärke: {strength:.1f})")

        return "\n".join(explanation_parts)

    def get_full_self_reflection(self, include_sandbox: bool = True) -> str:
        """
        Generiert eine vollständige Selbstreflexion mit DB-Daten.

        Kombiniert:
        - Aktuelle Session-Statistiken
        - Historische Patterns aus DB
        - Sandbox-Entscheidungen
        - Gelernte Erkenntnisse

        Returns:
            Ausführlicher Reflexions-Text
        """
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║              HOLO SELBSTREFLEXION                            ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
        ]

        # 1. Session-Statistiken
        lines.append("📊 AKTUELLE SESSION:")
        lines.append(f"   Laufzeit: {(datetime.now() - self._session_start).seconds // 60} Minuten")
        lines.append(f"   Beobachtungen: {self._session_stats['total_observations']}")
        lines.append(f"   Entscheidungen: {self._session_stats['decisions_made']}")
        lines.append(f"   Fehler abgefangen: {self._session_stats['errors_caught']}")
        lines.append(f"   Patterns gelernt: {len(self._patterns)}")
        lines.append("")

        # 2. Top aktive Komponenten
        if self._component_calls:
            lines.append("🔧 AKTIVE KOMPONENTEN (Top 5):")
            sorted_components = sorted(
                self._component_calls.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:5]
            for comp, calls in sorted_components:
                success_rate = sum(1 for c in calls if c.get('success', True)) / len(calls) if calls else 0
                lines.append(f"   • {comp}: {len(calls)} Aufrufe ({success_rate:.0%} Erfolg)")
            lines.append("")

        # 3. Gelernte Patterns aus DB
        if self._patterns:
            lines.append("🧠 WAS ICH GELERNT HABE:")

            # Stärken (hohe Erfolgsrate)
            strengths = [p for p in self._patterns.values() if p.success_rate > 0.85]
            if strengths:
                lines.append("   ✓ Stärken:")
                for p in sorted(strengths, key=lambda x: x.success_rate, reverse=True)[:3]:
                    lines.append(f"      • {p.key}: {p.success_rate:.0%} Erfolg")

            # Schwächen (niedrige Erfolgsrate)
            weaknesses = [p for p in self._patterns.values() if p.success_rate < 0.6]
            if weaknesses:
                lines.append("   ✗ Verbesserungsbedarf:")
                for p in sorted(weaknesses, key=lambda x: x.success_rate)[:3]:
                    lines.append(f"      • {p.key}: nur {p.success_rate:.0%} Erfolg")
            lines.append("")

        # 4. Cause-Effect Verständnis
        if self._cause_effect:
            lines.append("🔗 URSACHE-WIRKUNG VERSTÄNDNIS:")
            for cause, effects in list(self._cause_effect.items())[:5]:
                effect_str = ", ".join(f"{e}" for e, s in list(effects.items())[:3])
                lines.append(f"   {cause} → {effect_str}")
            lines.append("")

        # 5. Historische DB-Daten
        try:
            with sqlite3.connect(self._db_path) as conn:
                # Gesamt-Statistiken
                cursor = conn.execute('''
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
                    FROM observations
                    WHERE timestamp > datetime('now', '-7 days')
                ''')
                row = cursor.fetchone()
                if row and row[0] > 0:
                    lines.append("📈 LETZTE 7 TAGE (aus DB):")
                    lines.append(f"   Gesamt-Beobachtungen: {row[0]}")
                    lines.append(f"   Erfolgsrate: {row[1]/row[0]:.0%}" if row[0] > 0 else "")

                # Top Komponenten historisch
                cursor = conn.execute('''
                    SELECT component, COUNT(*) as cnt,
                           AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
                    FROM observations
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY component
                    ORDER BY cnt DESC
                    LIMIT 5
                ''')
                lines.append("   Top Komponenten:")
                for row in cursor:
                    lines.append(f"      • {row[0]}: {row[1]} Aufrufe ({row[2]:.0%} Erfolg)")
                lines.append("")

        except Exception as e:
            logger.debug(f"DB-Statistiken nicht verfügbar: {e}")

        # 6. Was ich daraus lerne
        lines.append("💡 ERKENNTNISSE:")
        if self._patterns:
            # Beste Patterns
            best = max(self._patterns.values(), key=lambda p: p.success_rate * p.sample_count, default=None)
            if best:
                lines.append(f"   • Mein bestes Verhaltensmuster: {best.key}")
                lines.append(f"     (Erfolgsrate {best.success_rate:.0%}, {best.sample_count} Beobachtungen)")

            # Häufigste Fehler
            worst = min(self._patterns.values(), key=lambda p: p.success_rate if p.sample_count > 3 else 1, default=None)
            if worst and worst.success_rate < 0.7:
                lines.append(f"   • Hier sollte ich mich verbessern: {worst.key}")
                lines.append(f"     (Nur {worst.success_rate:.0%} Erfolg)")
        else:
            lines.append("   • Noch nicht genug Daten für Erkenntnisse gesammelt")

        lines.append("")
        lines.append("═" * 66)

        return "\n".join(lines)

    # =========================================================================
    # HILFSMETHODEN
    # =========================================================================

    def _generate_id(self) -> str:
        """Generiert eindeutige ID"""
        return f"obs_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

    def _find_observation(self, obs_id: str) -> Optional[SystemObservation]:
        """Findet Beobachtung nach ID"""
        for obs in self._observations:
            if obs.id == obs_id:
                return obs
        return None

    def get_stats(self) -> Dict:
        """Gibt aktuelle Statistiken zurück"""
        return {
            "session_duration_min": (datetime.now() - self._session_start).seconds / 60,
            "total_observations": len(self._observations),
            "patterns_found": len(self._patterns),
            "components_tracked": len(self._component_calls),
            "session_stats": self._session_stats,
        }


# =============================================================================
# FACTORY FUNKTION
# =============================================================================

def create_meta_cognition_system(pi_interface=None, db=None, data_dir: Path = None) -> Dict[str, Any]:
    """
    Erstellt das komplette Meta-Cognition System.

    Args:
        pi_interface: Pi-Interface für Hardware-Zugriff
        db: HoloDatabaseManager für Persistenz
        data_dir: Datenverzeichnis für JSON-Fallback

    Returns:
        Dict mit allen Komponenten
    """
    presence = HoloPresenceAwareness(pi_interface=pi_interface, db=db, data_dir=data_dir)
    sandbox = HoloSandbox(db=db, data_dir=data_dir)
    observer = HoloMetaObserver(db=db, data_dir=data_dir)

    logger.info("[MetaCognition] System erstellt mit Presence, Sandbox, Observer")

    return {
        "presence": presence,
        "sandbox": sandbox,
        "observer": observer,
    }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO META-COGNITION TEST")
    print("=" * 70)

    # Erstelle System
    system = create_meta_cognition_system()

    observer = system["observer"]
    sandbox = system["sandbox"]

    # Simuliere einige Beobachtungen
    print("\n📊 Simuliere Beobachtungen...")

    components = ["learning_system", "reasoning_engine", "personality", "dialogue"]
    actions = ["process", "analyze", "generate", "evaluate"]

    for i in range(30):
        comp = random.choice(components)
        action = random.choice(actions)
        success = random.random() > 0.2

        observer.observe(
            ObservationType.COMPONENT_CALL,
            component=comp,
            action=action,
            success=success,
            duration_ms=random.uniform(10, 500)
        )

    # Test Sandbox
    print("\n🧪 Teste Sandbox...")
    options = [
        "Das ist eine gute Frage!",
        "Ich bin mir nicht sicher, aber vielleicht...",
        "Lass mich das ausführlich erklären...",
    ]

    results = sandbox.evaluate_options(options, {"mood": "positive"})
    print("\nSandbox Ergebnisse:")
    for r in results:
        print(f"  [{r.recommendation}] {r.option[:40]}... (conf={r.confidence:.2f}, risk={r.risk_level:.2f})")

    # Test Selbstreflexion
    print("\n🔍 Generiere Selbstreflexion...")
    reflection = observer.get_self_reflection()
    print(reflection["reflection"])

    # Test Komponenten-Erklärung
    print("\n📖 Erkläre Komponente...")
    print(observer.explain_component("learning_system"))

    print("\n" + "=" * 70)
    print("✅ TEST ERFOLGREICH")
    print("=" * 70)
