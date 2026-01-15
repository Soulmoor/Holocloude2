#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO BRAIN CORE v1.0
====================

Kern-Konfiguration und Basis-Klassen für das Holo Brain System.

Enthält:
- BrainConfig: Zentrale Konfiguration
- Dataclasses für Events, Feedback, etc.
- Memory Store Basis-Implementation
- Emotionale Kern-Klassen

Autor: Holocloude Team
Version: 1.0
"""

import os
import json
import logging
import sqlite3
import threading
import random
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# KONFIGURATION
# =============================================================================

class BrainConfig:
    """Zentrale Konfiguration für Holo Brain"""

    # Server
    HOLO_PORT = 5005
    HOLO_NAME = "Holo"
    HOLO_VERSION = "15"

    # KI Backend
    OLLAMA_HOST = "http://192.168.178.42:11434"  # Remote (Mini-PC)
    LOCAL_HOST = "http://192.168.178.42:11434"   # Local (Pi)

    TEMPERATURE = 0.3
    NUM_CTX = 8192
    TIMEOUT = 120

    # Pfade
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    STATE_DIR = BASE_DIR / "state"
    LOG_DIR = BASE_DIR / "logs"

    # Datenbanken
    DB_FILE = DATA_DIR / "holo_brain_v12.db"
    KNOWLEDGE_DB_FILE = DATA_DIR / "holo_knowledge.db"

    # Cache
    RAM_CACHE_DIR = "/dev/shm/holo_llm_cache"
    PATTERN_STORAGE = DATA_DIR / "llm_patterns.json"

    CACHE_LIMITS = {
        "responses": 250,
        "patterns": 50,
        "context": 50,
        "reasoning": 30,
        "metadata": 20
    }

    KEEP_ALIVE = "30m"
    PATTERN_MIN_CONFIDENCE = 0.75

    @classmethod
    def ensure_directories(cls):
        """Stelle sicher, dass alle nötigen Verzeichnisse existieren."""
        for dir_path in [cls.DATA_DIR, cls.STATE_DIR, cls.LOG_DIR]:
            os.makedirs(dir_path, exist_ok=True)


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class PiFeedback:
    """Feedback vom Pi-System"""
    success: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Optional[Dict] = None


@dataclass
class Reflection:
    """Eine Selbstreflexion"""
    thought: str
    mood: float
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None
    depth: int = 1  # 1=oberflächlich, 5=tiefgründig


@dataclass
class DreamSummary:
    """Zusammenfassung eines Traums"""
    content: str
    themes: List[str]
    emotions: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    interpretation: Optional[str] = None


@dataclass
class WeeklyRecap:
    """Wöchentliche Zusammenfassung"""
    week_number: int
    year: int
    highlights: List[str]
    mood_average: float
    topics_discussed: List[str]
    learned_facts: List[str]
    bond_change: float


@dataclass
class HoloSuggestion:
    """Ein Vorschlag von Holo"""
    text: str
    category: str  # "activity", "topic", "reminder", "question"
    priority: float = 0.5
    expires_at: Optional[datetime] = None


@dataclass
class CalendarEvent:
    """Ein Kalendereintrag"""
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    reminder_minutes: int = 15


@dataclass
class UserActivityPattern:
    """Erkanntes Benutzer-Aktivitätsmuster"""
    pattern_type: str  # "morning_routine", "work_hours", etc.
    typical_times: List[str]
    confidence: float
    last_observed: datetime


@dataclass
class LifeLogEntry:
    """Ein Eintrag im Lebens-Log"""
    timestamp: datetime
    category: str
    content: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class EmotionalMemory:
    """Eine emotionale Erinnerung"""
    event: str
    emotion: str
    intensity: float
    timestamp: datetime
    associated_topics: List[str] = field(default_factory=list)


# =============================================================================
# ENUMS
# =============================================================================

class MoodState(Enum):
    """Stimmungszustände"""
    VERY_SAD = -2
    SAD = -1
    NEUTRAL = 0
    HAPPY = 1
    VERY_HAPPY = 2


class EnergyLevel(Enum):
    """Energie-Level"""
    EXHAUSTED = 0
    TIRED = 1
    NORMAL = 2
    ENERGETIC = 3
    HYPERACTIVE = 4


class InteractionType(Enum):
    """Art der Interaktion"""
    CHAT = "chat"
    COMMAND = "command"
    QUERY = "query"
    EMOTIONAL = "emotional"
    CREATIVE = "creative"


# =============================================================================
# TYPING SIMULATOR - Für realistische Antwort-Verzögerungen
# =============================================================================

class TypingSimulatorBase:
    """Basis-Klasse für Typing-Simulation"""

    def __init__(self, energy_system=None):
        self.energy_system = energy_system
        self.enabled = True
        self.base_speed = 50  # Zeichen pro Sekunde
        self.variance = 0.3   # 30% Varianz

    def calculate_delay(self, text: str) -> float:
        """Berechne realistische Tipp-Verzögerung."""
        if not self.enabled:
            return 0.0

        # Basis-Zeit basierend auf Textlänge
        char_count = len(text)
        base_time = char_count / self.base_speed

        # Energie-Modifikator
        energy_mod = 1.0
        if self.energy_system:
            try:
                energy = self.energy_system.get_total_energy()
                if energy < 0.3:
                    energy_mod = 1.5  # Müde = langsamer
                elif energy > 0.8:
                    energy_mod = 0.7  # Energiegeladen = schneller
            except Exception as e:
                logger.debug(f"[BrainCore] Energy check for typing speed failed: {type(e).__name__}: {e}")

        # Varianz hinzufügen
        variance = random.uniform(1 - self.variance, 1 + self.variance)

        delay = base_time * energy_mod * variance

        # Grenzen
        return max(0.5, min(delay, 10.0))

    def get_chunks(self, text: str, chunk_size: int = 50) -> List[Tuple[str, float]]:
        """Teile Text in Chunks mit Verzögerungen."""
        chunks = []
        words = text.split()
        current_chunk = []
        current_len = 0

        for word in words:
            if current_len + len(word) > chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append((chunk_text, self.calculate_delay(chunk_text) / 3))
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += len(word) + 1

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append((chunk_text, self.calculate_delay(chunk_text) / 3))

        return chunks


# =============================================================================
# SEASONAL EVENTS - Saisonale Events für Holo
# =============================================================================

class SeasonalEventsBase:
    """Basis-Klasse für saisonale Events"""

    GERMAN_HOLIDAYS = {
        (1, 1): ("Neujahr", "Frohes neues Jahr! 🎆"),
        (2, 14): ("Valentinstag", "Alles Liebe zum Valentinstag! 💕"),
        (3, 8): ("Frauentag", "Alles Gute zum Internationalen Frauentag! 🌸"),
        (4, 1): ("April April", "April April! 🃏"),
        (5, 1): ("Tag der Arbeit", "Schönen Tag der Arbeit! ⚒️"),
        (10, 3): ("Tag der Deutschen Einheit", "Schönen Feiertag! 🇩🇪"),
        (10, 31): ("Halloween", "Gruseliger Halloween-Abend! 🎃"),
        (12, 6): ("Nikolaus", "Der Nikolaus war da! 🎅"),
        (12, 24): ("Heiligabend", "Frohe Weihnachten! 🎄"),
        (12, 25): ("1. Weihnachtstag", "Frohe Weihnachten! ⭐"),
        (12, 26): ("2. Weihnachtstag", "Entspannte Weihnachtstage! 🎁"),
        (12, 31): ("Silvester", "Guten Rutsch ins neue Jahr! 🎉"),
    }

    @classmethod
    def get_today_event(cls) -> Optional[Tuple[str, str]]:
        """Gibt das heutige Event zurück (falls vorhanden)."""
        today = datetime.now()
        key = (today.month, today.day)
        return cls.GERMAN_HOLIDAYS.get(key)

    @classmethod
    def get_season(cls) -> str:
        """Aktuelle Jahreszeit."""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "Frühling"
        elif month in [6, 7, 8]:
            return "Sommer"
        elif month in [9, 10, 11]:
            return "Herbst"
        else:
            return "Winter"

    @classmethod
    def get_time_of_day(cls) -> str:
        """Aktuelle Tageszeit."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Morgen"
        elif 12 <= hour < 14:
            return "Mittag"
        elif 14 <= hour < 18:
            return "Nachmittag"
        elif 18 <= hour < 22:
            return "Abend"
        else:
            return "Nacht"


# =============================================================================
# LIFE LOG - Lebens-Protokoll
# =============================================================================

class LifeLog:
    """Protokolliert Holos "Leben" für spätere Reflexion"""

    def __init__(self, max_entries: int = 10000):
        self._entries: deque = deque(maxlen=max_entries)
        self._lock = threading.Lock()

    def log(self, category: str, content: str, metadata: Dict = None):
        """Füge einen Eintrag hinzu."""
        entry = LifeLogEntry(
            timestamp=datetime.now(),
            category=category,
            content=content,
            metadata=metadata or {}
        )
        with self._lock:
            self._entries.append(entry)

    def get_entries(
        self,
        hours: int = None,
        days: int = None,
        category: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Hole Einträge mit Filtern."""
        with self._lock:
            entries = list(self._entries)

        # Zeit-Filter
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            entries = [e for e in entries if e.timestamp >= cutoff]
        elif days:
            cutoff = datetime.now() - timedelta(days=days)
            entries = [e for e in entries if e.timestamp >= cutoff]

        # Kategorie-Filter
        if category:
            entries = [e for e in entries if e.category == category]

        # Limit und Reverse (neueste zuerst)
        entries = entries[-limit:]
        entries.reverse()

        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "category": e.category,
                "content": e.content,
                "metadata": e.metadata
            }
            for e in entries
        ]

    def get_summary(self, days: int = 7) -> Dict:
        """Erstelle eine Zusammenfassung."""
        entries = self.get_entries(days=days, limit=1000)

        categories = {}
        for e in entries:
            cat = e["category"]
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "period_days": days,
            "total_entries": len(entries),
            "categories": categories,
            "first_entry": entries[-1]["timestamp"] if entries else None,
            "last_entry": entries[0]["timestamp"] if entries else None
        }


# =============================================================================
# MEMORY STORE BASE
# =============================================================================

class MemoryStoreBase:
    """
    Basis-Implementation für den Memory Store.
    Wird von MemoryStore und MemoryStoreWrapper erweitert.
    """

    def __init__(self):
        self._conversation_history: deque = deque(maxlen=1000)
        self._reflections: deque = deque(maxlen=500)
        self._emotional_memories: deque = deque(maxlen=1000)
        self._life_log = LifeLog()
        self._lock = threading.Lock()

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Füge eine Nachricht zur Historie hinzu."""
        with self._lock:
            self._conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })

    def get_recent_messages(self, count: int = 10) -> List[Dict]:
        """Hole die letzten N Nachrichten."""
        with self._lock:
            return list(self._conversation_history)[-count:]

    def add_reflection(self, reflection: Reflection):
        """Füge eine Reflexion hinzu."""
        with self._lock:
            self._reflections.append(reflection)

    def get_reflections(self, count: int = 10) -> List[Reflection]:
        """Hole die letzten Reflexionen."""
        with self._lock:
            return list(self._reflections)[-count:]

    def log_life_event(self, category: str, content: str, metadata: Dict = None):
        """Logge ein Lebens-Event."""
        self._life_log.log(category, content, metadata)

    def get_life_log(self, **kwargs) -> List[Dict]:
        """Hole Life-Log Einträge."""
        return self._life_log.get_entries(**kwargs)

    def get_chat_stats(self) -> Dict:
        """Statistiken über Chats."""
        with self._lock:
            total = len(self._conversation_history)
            user_msgs = sum(1 for m in self._conversation_history if m.get("role") == "user")
            holo_msgs = total - user_msgs

            return {
                "total_messages": total,
                "user_messages": user_msgs,
                "holo_messages": holo_msgs,
                "reflections": len(self._reflections)
            }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Config
    "BrainConfig",

    # Dataclasses
    "PiFeedback",
    "Reflection",
    "DreamSummary",
    "WeeklyRecap",
    "HoloSuggestion",
    "CalendarEvent",
    "UserActivityPattern",
    "LifeLogEntry",
    "EmotionalMemory",

    # Enums
    "MoodState",
    "EnergyLevel",
    "InteractionType",

    # Classes
    "TypingSimulatorBase",
    "SeasonalEventsBase",
    "LifeLog",
    "MemoryStoreBase",
]
