#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO DATABASE SYSTEM v1.0                                                   ║
║                                                                              ║
║  Zentrales Datenbank-Management für alle Holo-Subsysteme                     ║
║                                                                              ║
║  ARCHITEKTUR:                                                                ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │  ~/holo_data/                                                          │  ║
║  │  ├── holo_memory.db        │ Episoden, Erinnerungen, Träume           │  ║
║  │  ├── holo_emotions.db      │ Emotionen, Stimmungen, Gefühle           │  ║
║  │  ├── holo_knowledge.db     │ Fakten, Wissen, Gelerntes                │  ║
║  │  ├── holo_conversations.db │ Chat-History, Dialoge                    │  ║
║  │  ├── holo_media.db         │ Anime, Games, Musik, Filme               │  ║
║  │  ├── holo_language.db      │ Sprachmuster, Stil, Ausdrücke            │  ║
║  │  ├── holo_activity.db      │ Aktivitäten, Routinen                    │  ║
║  │  ├── holo_identity.db      │ Selbst-Konzept, Beliefs                  │  ║
║  │  ├── holo_productivity.db  │ Todos, Timer, Notizen                    │  ║
║  │  └── holo_state.db         │ Runtime States (ersetzt JSONs!)         │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
║  FEATURES:                                                                   ║
║  - Automatische Migration von alten JSONs und DBs                           ║
║  - Thread-safe mit Connection Pooling                                        ║
║  - Backup & Recovery                                                         ║
║  - Einheitliche API für alle Subsysteme                                      ║
║                                                                              ║
║  USAGE:                                                                      ║
║      from holo_database_system import HoloDatabaseManager                    ║
║      db = HoloDatabaseManager()                                              ║
║      db.memory.store_episode(...)                                            ║
║      db.emotions.log_emotion(...)                                            ║
║      db.knowledge.store_fact(...)                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3
import json
import os
import shutil
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from contextlib import contextmanager
from abc import ABC, abstractmethod
import uuid

# Zentrale Typen aus holo_core_types importieren (keine Duplikate!)
try:
    from holo_core_types import ActivityType
    HAS_CORE_TYPES = True
except ImportError:
    HAS_CORE_TYPES = False

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("HoloDB")


# =============================================================================
# CONFIGURATION
# =============================================================================

class DatabaseConfig:
    """Zentrale Konfiguration für das Datenbank-System"""

    # Basis-Verzeichnis
    DATA_DIR = Path.home() / "holo_data"

    # Einzelne Datenbanken - 17 spezialisierte DBs!
    DATABASES = {
        # === KERN (Persönlichkeit & Gedächtnis) ===
        "memory": "holo_memory.db",           # Episoden, Träume, Erinnerungen
        "emotions": "holo_emotions.db",       # Emotionen, Stimmungen
        "identity": "holo_identity.db",       # Persönlichkeit, Beliefs
        "language": "holo_language.db",       # Sprachmuster, Stil

        # === WISSEN ===
        "knowledge": "holo_knowledge.db",     # Fakten, Interessen
        "media": "holo_media.db",             # Anime, Games, Musik, Filme
        "news": "holo_news.db",               # News, Artikel, Welt-Wissen

        # === INTERAKTION ===
        "conversations": "holo_conversations.db",  # Chat-History
        "activity": "holo_activity.db",       # Aktivitäten, Routinen
        "productivity": "holo_productivity.db",    # Todos, Notizen, Timer

        # === UMGEBUNG & SMART HOME ===
        "environment": "holo_environment.db", # Wetter, Sonnenzeiten, Feiertage
        "network": "holo_network.db",         # Geräte, NAS, Filesystems
        "presence": "holo_presence.db",       # User-Anwesenheit, Patterns
        "home": "holo_home.db",               # Home Assistant, Sensoren
        "calendar": "holo_calendar.db",       # Termine, Events

        # === SYSTEM ===
        "predictions": "holo_predictions.db", # Q-Learning, Bayesian, Patterns
        "state": "holo_state.db",             # Runtime States (ersetzt JSONs)
    }

    # Backup
    BACKUP_DIR = DATA_DIR / "backups"
    MAX_BACKUPS = 10

    # Migration
    OLD_DATA_PATHS = [
        Path.home(),                    # ~/holo_*.json, ~/holo_*.db
        Path.home() / "holo_knowledge", # Altes Wissens-Verzeichnis
        Path("data"),                   # ./data/
    ]


# =============================================================================
# ENUMS
# =============================================================================

class MemoryType(Enum):
    """Arten von Erinnerungen"""
    EPISODIC = "episodic"       # Konkrete Ereignisse
    SEMANTIC = "semantic"       # Fakten
    EMOTIONAL = "emotional"     # Gefühlsbetonte Momente
    PROCEDURAL = "procedural"   # Gewohnheiten/Prozeduren


class EmotionCategory(Enum):
    """Emotionskategorien"""
    JOY = "joy"
    SADNESS = "sadness"
    CURIOSITY = "curiosity"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    FRUSTRATION = "frustration"
    AFFECTION = "affection"
    LONELINESS = "loneliness"
    PRIDE = "pride"
    WORRY = "worry"


class KnowledgeCategory(Enum):
    """Wissenskategorien"""
    USER_FACT = "user_fact"           # Fakten über den User
    WORLD_FACT = "world_fact"         # Allgemeinwissen
    LEARNED = "learned"               # Gelerntes aus Web/News
    PREFERENCE = "preference"         # Präferenzen
    RELATIONSHIP = "relationship"     # Beziehungswissen


class MediaType(Enum):
    """Medientypen"""
    ANIME = "anime"
    MANGA = "manga"
    GAME = "game"
    MOVIE = "movie"
    SERIES = "series"
    MUSIC = "music"
    BOOK = "book"
    PODCAST = "podcast"


# ActivityType aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    class ActivityType(Enum):
        """FALLBACK - Aktivitätstypen - nutze holo_core_types!"""
        CONVERSATION = "conversation"
        LEARNING = "learning"
        BROWSING = "browsing"
        THINKING = "thinking"
        CREATING = "creating"
        RESTING = "resting"
        DREAMING = "dreaming"


# =============================================================================
# BASE DATABASE CLASS
# =============================================================================

class BaseDatabase(ABC):
    """
    Basis-Klasse für alle Datenbank-Handler.

    Features:
    - Thread-safe connections
    - Automatische Schema-Erstellung
    - Gemeinsame Hilfsfunktionen
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.RLock()

        # Verzeichnis erstellen
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Schema initialisieren
        self._init_schema()

    @property
    def connection(self) -> sqlite3.Connection:
        """Thread-lokale Connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row
            # Performance-Optimierungen
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=10000")
        return self._local.conn

    @contextmanager
    def transaction(self):
        """Context Manager für Transaktionen"""
        with self._lock:
            try:
                yield self.connection
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                raise e

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Führt SQL aus mit Lock"""
        with self._lock:
            cursor = self.connection.execute(sql, params)
            self.connection.commit()
            return cursor

    def executemany(self, sql: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """Führt SQL für mehrere Datensätze aus"""
        with self._lock:
            cursor = self.connection.executemany(sql, params_list)
            self.connection.commit()
            return cursor

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Holt einen Datensatz"""
        with self._lock:
            return self.connection.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Holt alle Datensätze"""
        with self._lock:
            return self.connection.execute(sql, params).fetchall()

    def close(self):
        """Schließt die Connection"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    @abstractmethod
    def _init_schema(self):
        """Initialisiert das Datenbank-Schema - muss überschrieben werden"""
        pass

    def _generate_id(self) -> str:
        """Generiert eine eindeutige ID"""
        return str(uuid.uuid4())[:8]

    def _now(self) -> str:
        """Aktueller Zeitstempel als ISO-String"""
        return datetime.now().isoformat()


# =============================================================================
# MEMORY DATABASE - v3.0 mit Assoziationen & Konsolidierung
# =============================================================================

@dataclass
class Episode:
    """Eine episodische Erinnerung"""
    id: str
    timestamp: str
    summary: str
    participants: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    emotional_valence: float = 0.0      # -1 bis +1
    importance: float = 0.5             # 0 bis 1
    strength: float = 1.0               # Decay über Zeit
    access_count: int = 0
    last_accessed: Optional[str] = None
    memory_type: str = "episodic"
    raw_messages: Optional[str] = None
    location_context: str = ""          # Wo war das?
    sensory_details: List[str] = field(default_factory=list)  # Sinneseindrücke


@dataclass
class Dream:
    """Ein Traum (Gedächtniskonsolidierung)"""
    id: str
    date: str
    timestamp: str
    theme: str
    elements: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    related_episodes: List[str] = field(default_factory=list)
    vividness: float = 0.5              # Wie lebhaft?
    interpretation: str = ""            # Traumdeutung


@dataclass
class MemoryAssociation:
    """Eine Verbindung zwischen Erinnerungen"""
    id: str
    episode_a: str
    episode_b: str
    association_type: str               # "similar", "causal", "temporal", "emotional"
    strength: float = 0.5
    created_at: str = ""


@dataclass
class Flashback:
    """Ein Flashback-Moment"""
    id: str
    timestamp: str
    triggered_by: str                   # Was hat den Flashback ausgelöst?
    episode_id: str                     # Welche Erinnerung?
    emotional_intensity: float = 0.5
    was_pleasant: bool = True


class MemoryDatabase(BaseDatabase):
    """
    Datenbank für Erinnerungen - v3.0 mit erweitertem Gedächtnismodell.

    Speichert:
    - Episodische Erinnerungen (Ereignisse)
    - Semantisches Gedächtnis (Fakten - verlinkt mit KnowledgeDB)
    - Prozedurales Gedächtnis (Wie man Dinge tut)
    - Träume (Konsolidierung)
    - Assoziationen zwischen Erinnerungen
    - Flashbacks
    - Wichtige Daten (Geburtstage, Jubiläen)
    - Erinnerungs-Konsolidierung
    - Vergessenskurve (Ebbinghaus)
    """

    def _init_schema(self):
        """Erstellt die Memory-Tabellen"""
        # Episodisches Gedächtnis
        self.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                summary TEXT,
                participants TEXT,
                topics TEXT,
                emotional_valence REAL DEFAULT 0.0,
                importance REAL DEFAULT 0.5,
                strength REAL DEFAULT 1.0,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                memory_type TEXT DEFAULT 'episodic',
                raw_messages TEXT,
                location_context TEXT,
                sensory_details TEXT
            )
        ''')

        # Träume
        self.execute('''
            CREATE TABLE IF NOT EXISTS dreams (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                theme TEXT,
                elements TEXT,
                emotions TEXT,
                insights TEXT,
                related_episodes TEXT,
                vividness REAL DEFAULT 0.5,
                interpretation TEXT
            )
        ''')

        # Wichtige Daten
        self.execute('''
            CREATE TABLE IF NOT EXISTS important_dates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date_pattern TEXT NOT NULL,
                date_type TEXT DEFAULT 'birthday',
                notes TEXT,
                last_reminded TEXT,
                created_at TEXT,
                emotional_significance REAL DEFAULT 0.5
            )
        ''')

        # NEU: Assoziationen zwischen Erinnerungen
        self.execute('''
            CREATE TABLE IF NOT EXISTS memory_associations (
                id TEXT PRIMARY KEY,
                episode_a TEXT NOT NULL,
                episode_b TEXT NOT NULL,
                association_type TEXT DEFAULT 'similar',
                strength REAL DEFAULT 0.5,
                created_at TEXT,
                last_activated TEXT,
                UNIQUE(episode_a, episode_b)
            )
        ''')

        # NEU: Flashbacks
        self.execute('''
            CREATE TABLE IF NOT EXISTS flashbacks (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                triggered_by TEXT,
                episode_id TEXT,
                emotional_intensity REAL DEFAULT 0.5,
                was_pleasant INTEGER DEFAULT 1,
                context TEXT
            )
        ''')

        # NEU: Prozedurales Gedächtnis (Wie man Dinge tut)
        self.execute('''
            CREATE TABLE IF NOT EXISTS procedural_memory (
                id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL UNIQUE,
                category TEXT,
                steps TEXT,
                proficiency REAL DEFAULT 0.5,
                times_practiced INTEGER DEFAULT 0,
                last_practiced TEXT,
                learned_from TEXT,
                tips TEXT
            )
        ''')

        # NEU: Konsolidierungs-Log
        self.execute('''
            CREATE TABLE IF NOT EXISTS consolidation_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                episodes_processed INTEGER DEFAULT 0,
                associations_created INTEGER DEFAULT 0,
                memories_strengthened INTEGER DEFAULT 0,
                memories_weakened INTEGER DEFAULT 0,
                insights_generated TEXT
            )
        ''')

        # NEU: Vergessenskurve-Tracking
        self.execute('''
            CREATE TABLE IF NOT EXISTS forgetting_curve (
                episode_id TEXT PRIMARY KEY,
                initial_strength REAL DEFAULT 1.0,
                current_strength REAL DEFAULT 1.0,
                decay_rate REAL DEFAULT 0.1,
                last_review TEXT,
                review_count INTEGER DEFAULT 0,
                next_review_due TEXT
            )
        ''')

        # NEU: Erinnerungs-Trigger
        self.execute('''
            CREATE TABLE IF NOT EXISTS memory_triggers (
                id TEXT PRIMARY KEY,
                trigger_word TEXT NOT NULL,
                trigger_type TEXT DEFAULT 'keyword',
                associated_episodes TEXT,
                activation_count INTEGER DEFAULT 0,
                last_activated TEXT
            )
        ''')

        # NEU: Erste Eindrücke (wichtig für Beziehungen)
        self.execute('''
            CREATE TABLE IF NOT EXISTS first_impressions (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL UNIQUE,
                subject_type TEXT DEFAULT 'person',
                first_encounter TEXT,
                initial_feeling TEXT,
                initial_thoughts TEXT,
                how_it_changed TEXT,
                current_feeling TEXT
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_episodes_ts ON episodes(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_episodes_importance ON episodes(importance)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_dreams_date ON dreams(date)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_associations_a ON memory_associations(episode_a)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_associations_b ON memory_associations(episode_b)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_flashbacks_ts ON flashbacks(timestamp)')

        logger.info(f"📝 MemoryDatabase v3.0 initialisiert: {self.db_path}")

    # === EPISODES ===

    def store_episode(self, episode: Episode) -> str:
        """Speichert eine Episode"""
        self.execute('''
            INSERT OR REPLACE INTO episodes
            (id, timestamp, summary, participants, topics, emotional_valence,
             importance, strength, access_count, last_accessed, memory_type,
             raw_messages, location_context, sensory_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            episode.id,
            episode.timestamp,
            episode.summary,
            json.dumps(episode.participants),
            json.dumps(episode.topics),
            episode.emotional_valence,
            episode.importance,
            episode.strength,
            episode.access_count,
            episode.last_accessed,
            episode.memory_type,
            episode.raw_messages,
            episode.location_context,
            json.dumps(episode.sensory_details),
        ))

        # Vergessenskurve initialisieren
        self._init_forgetting_curve(episode.id)

        return episode.id

    def create_episode(self, summary: str, topics: List[str] = None,
                       participants: List[str] = None, importance: float = 0.5,
                       emotional_valence: float = 0.0,
                       raw_messages: List[Dict] = None,
                       location_context: str = "",
                       sensory_details: List[str] = None) -> Episode:
        """Erstellt und speichert eine neue Episode"""
        episode = Episode(
            id=self._generate_id(),
            timestamp=self._now(),
            summary=summary,
            topics=topics or [],
            participants=participants or ["user", "holo"],
            importance=importance,
            emotional_valence=emotional_valence,
            raw_messages=json.dumps(raw_messages) if raw_messages else None,
            location_context=location_context,
            sensory_details=sensory_details or [],
        )
        self.store_episode(episode)

        # Automatisch Assoziationen zu ähnlichen Episoden erstellen
        self._auto_associate(episode)

        return episode

    def _init_forgetting_curve(self, episode_id: str):
        """Initialisiert Vergessenskurve für Episode"""
        now = self._now()
        # Nächste Review in 1 Tag (Spaced Repetition)
        next_review = (datetime.now() + timedelta(days=1)).isoformat()

        self.execute('''
            INSERT OR IGNORE INTO forgetting_curve
            (episode_id, initial_strength, current_strength, last_review, next_review_due)
            VALUES (?, 1.0, 1.0, ?, ?)
        ''', (episode_id, now, next_review))

    def _auto_associate(self, episode: Episode):
        """Erstellt automatisch Assoziationen zu ähnlichen Episoden"""
        # Finde Episoden mit gleichen Topics
        for topic in episode.topics[:3]:  # Max 3 Topics
            similar = self.fetchall('''
                SELECT id FROM episodes
                WHERE topics LIKE ? AND id != ?
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (f"%{topic}%", episode.id))

            for row in similar:
                self.create_association(episode.id, row['id'], "similar", 0.5)

    def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Holt eine Episode nach ID"""
        row = self.fetchone('SELECT * FROM episodes WHERE id = ?', (episode_id,))
        if row:
            self._mark_accessed(episode_id)
            return self._row_to_episode(row)
        return None

    def search_episodes(self, query: str = None, topics: List[str] = None,
                       min_importance: float = 0.0, limit: int = 20,
                       days_back: int = None) -> List[Episode]:
        """Sucht Episoden"""
        conditions = ["importance >= ?"]
        params = [min_importance]

        if query:
            conditions.append("(summary LIKE ? OR topics LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])

        if topics:
            topic_conds = ["topics LIKE ?" for _ in topics]
            conditions.append(f"({' OR '.join(topic_conds)})")
            params.extend([f"%{t}%" for t in topics])

        if days_back:
            cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
            conditions.append("timestamp >= ?")
            params.append(cutoff)

        sql = f'''
            SELECT * FROM episodes
            WHERE {' AND '.join(conditions)}
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        '''
        params.append(limit)

        rows = self.fetchall(sql, tuple(params))
        episodes = [self._row_to_episode(row) for row in rows]

        for ep in episodes:
            self._mark_accessed(ep.id)

        return episodes

    def get_recent(self, limit: int = 10) -> List[Episode]:
        """Holt die neuesten Episoden"""
        rows = self.fetchall(
            'SELECT * FROM episodes ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return [self._row_to_episode(row) for row in rows]

    def get_strongest_memories(self, limit: int = 10) -> List[Episode]:
        """Holt die stärksten Erinnerungen"""
        rows = self.fetchall('''
            SELECT * FROM episodes
            WHERE strength > 0.5
            ORDER BY strength DESC, importance DESC
            LIMIT ?
        ''', (limit,))
        return [self._row_to_episode(row) for row in rows]

    def decay_memories(self, decay_rate: float = 0.99):
        """Lässt Erinnerungen verblassen (täglich aufrufen)"""
        self.execute('''
            UPDATE episodes
            SET strength = strength * ?
            WHERE strength > 0.1
        ''', (decay_rate,))

        # Auch in Vergessenskurve
        self.execute('''
            UPDATE forgetting_curve
            SET current_strength = current_strength * ?
            WHERE current_strength > 0.1
        ''', (decay_rate,))

    def _mark_accessed(self, episode_id: str):
        """Markiert Episode als abgerufen - stärkt Erinnerung"""
        now = self._now()

        self.execute('''
            UPDATE episodes
            SET access_count = access_count + 1,
                last_accessed = ?,
                strength = MIN(1.0, strength + 0.05)
            WHERE id = ?
        ''', (now, episode_id))

        # Spaced Repetition: Nächste Review berechnen
        existing = self.fetchone(
            'SELECT review_count FROM forgetting_curve WHERE episode_id = ?',
            (episode_id,)
        )
        if existing:
            review_count = existing['review_count'] + 1
            # Exponentiell wachsende Intervalle: 1, 2, 4, 8, 16 Tage
            next_interval = 2 ** min(review_count, 5)
            next_review = (datetime.now() + timedelta(days=next_interval)).isoformat()

            self.execute('''
                UPDATE forgetting_curve
                SET current_strength = MIN(1.0, current_strength + 0.1),
                    last_review = ?,
                    review_count = ?,
                    next_review_due = ?
                WHERE episode_id = ?
            ''', (now, review_count, next_review, episode_id))

    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        """Konvertiert DB-Row zu Episode"""
        return Episode(
            id=row['id'],
            timestamp=row['timestamp'],
            summary=row['summary'] or "",
            participants=json.loads(row['participants'] or '[]'),
            topics=json.loads(row['topics'] or '[]'),
            emotional_valence=row['emotional_valence'] or 0.0,
            importance=row['importance'] or 0.5,
            strength=row['strength'] or 1.0,
            access_count=row['access_count'] or 0,
            last_accessed=row['last_accessed'],
            memory_type=row['memory_type'] or 'episodic',
            raw_messages=row['raw_messages'],
            location_context=row['location_context'] or "",
            sensory_details=json.loads(row['sensory_details'] or '[]'),
        )

    # === ASSOCIATIONS ===

    def create_association(self, episode_a: str, episode_b: str,
                          association_type: str = "similar",
                          strength: float = 0.5) -> str:
        """Erstellt eine Assoziation zwischen zwei Erinnerungen"""
        # Sortieren um Duplikate zu vermeiden
        if episode_a > episode_b:
            episode_a, episode_b = episode_b, episode_a

        assoc_id = self._generate_id()
        now = self._now()

        try:
            self.execute('''
                INSERT INTO memory_associations
                (id, episode_a, episode_b, association_type, strength, created_at, last_activated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (assoc_id, episode_a, episode_b, association_type, strength, now, now))
        except Exception:  # IntegrityError bei Duplikat
            # Assoziation existiert schon - verstärken
            self.execute('''
                UPDATE memory_associations
                SET strength = MIN(1.0, strength + 0.1),
                    last_activated = ?
                WHERE episode_a = ? AND episode_b = ?
            ''', (now, episode_a, episode_b))

        return assoc_id

    def get_associated_episodes(self, episode_id: str) -> List[Tuple[Episode, float]]:
        """Holt alle assoziierten Episoden mit Stärke"""
        rows = self.fetchall('''
            SELECT episode_a, episode_b, strength FROM memory_associations
            WHERE episode_a = ? OR episode_b = ?
            ORDER BY strength DESC
        ''', (episode_id, episode_id))

        result = []
        for row in rows:
            other_id = row['episode_b'] if row['episode_a'] == episode_id else row['episode_a']
            episode = self.get_episode(other_id)
            if episode:
                result.append((episode, row['strength']))

        return result

    def activate_association_chain(self, start_episode_id: str,
                                   max_depth: int = 3) -> List[Episode]:
        """Aktiviert eine Assoziationskette (wie Gedankensprünge)"""
        visited = set()
        chain = []

        def _traverse(ep_id: str, depth: int):
            if depth > max_depth or ep_id in visited:
                return
            visited.add(ep_id)

            episode = self.get_episode(ep_id)
            if episode:
                chain.append(episode)

            # Stärkste Assoziation verfolgen
            assocs = self.get_associated_episodes(ep_id)
            if assocs:
                strongest = assocs[0]
                _traverse(strongest[0].id, depth + 1)

        _traverse(start_episode_id, 0)
        return chain

    # === FLASHBACKS ===

    def record_flashback(self, triggered_by: str, episode_id: str,
                        emotional_intensity: float = 0.5,
                        was_pleasant: bool = True, context: str = "") -> str:
        """Zeichnet einen Flashback auf"""
        flashback_id = self._generate_id()
        self.execute('''
            INSERT INTO flashbacks
            (id, timestamp, triggered_by, episode_id, emotional_intensity,
             was_pleasant, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (flashback_id, self._now(), triggered_by, episode_id,
              emotional_intensity, int(was_pleasant), context))

        # Trigger speichern/verstärken
        self._update_trigger(triggered_by, episode_id)

        return flashback_id

    def _update_trigger(self, trigger_word: str, episode_id: str):
        """Aktualisiert Trigger-Wort"""
        existing = self.fetchone(
            'SELECT id, associated_episodes, activation_count FROM memory_triggers WHERE trigger_word = ?',
            (trigger_word,)
        )

        if existing:
            episodes = json.loads(existing['associated_episodes'] or '[]')
            if episode_id not in episodes:
                episodes.append(episode_id)
            self.execute('''
                UPDATE memory_triggers
                SET associated_episodes = ?,
                    activation_count = activation_count + 1,
                    last_activated = ?
                WHERE id = ?
            ''', (json.dumps(episodes), self._now(), existing['id']))
        else:
            self.execute('''
                INSERT INTO memory_triggers
                (id, trigger_word, associated_episodes, activation_count, last_activated)
                VALUES (?, ?, ?, 1, ?)
            ''', (self._generate_id(), trigger_word, json.dumps([episode_id]), self._now()))

    def check_triggers(self, text: str) -> List[Episode]:
        """Prüft Text auf bekannte Trigger und gibt assoziierte Erinnerungen zurück"""
        triggered_episodes = []

        triggers = self.fetchall('SELECT trigger_word, associated_episodes FROM memory_triggers')

        for row in triggers:
            if row['trigger_word'].lower() in text.lower():
                episode_ids = json.loads(row['associated_episodes'] or '[]')
                for ep_id in episode_ids[:3]:  # Max 3 pro Trigger
                    ep = self.get_episode(ep_id)
                    if ep and ep not in triggered_episodes:
                        triggered_episodes.append(ep)

        return triggered_episodes

    # === PROCEDURAL MEMORY ===

    def learn_skill(self, skill_name: str, steps: List[str],
                   category: str = "", learned_from: str = "") -> str:
        """Lernt eine neue Fähigkeit"""
        skill_id = self._generate_id()
        now = self._now()

        self.execute('''
            INSERT OR REPLACE INTO procedural_memory
            (id, skill_name, category, steps, proficiency, last_practiced, learned_from)
            VALUES (?, ?, ?, ?, 0.3, ?, ?)
        ''', (skill_id, skill_name, category, json.dumps(steps), now, learned_from))

        return skill_id

    def practice_skill(self, skill_name: str, success: bool = True):
        """Übt eine Fähigkeit und verbessert Proficiency"""
        delta = 0.05 if success else -0.02
        self.execute('''
            UPDATE procedural_memory
            SET proficiency = MAX(0.0, MIN(1.0, proficiency + ?)),
                times_practiced = times_practiced + 1,
                last_practiced = ?
            WHERE skill_name = ?
        ''', (delta, self._now(), skill_name))

    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Holt eine Fähigkeit"""
        row = self.fetchone(
            'SELECT * FROM procedural_memory WHERE skill_name = ?',
            (skill_name,)
        )
        return dict(row) if row else None

    def get_all_skills(self) -> List[Dict]:
        """Holt alle Fähigkeiten"""
        rows = self.fetchall(
            'SELECT * FROM procedural_memory ORDER BY proficiency DESC'
        )
        return [dict(r) for r in rows]

    # === FIRST IMPRESSIONS ===

    def record_first_impression(self, subject: str, subject_type: str = "person",
                               initial_feeling: str = "",
                               initial_thoughts: str = "") -> str:
        """Speichert einen ersten Eindruck"""
        impression_id = self._generate_id()
        self.execute('''
            INSERT OR IGNORE INTO first_impressions
            (id, subject, subject_type, first_encounter, initial_feeling, initial_thoughts)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (impression_id, subject, subject_type, self._now(),
              initial_feeling, initial_thoughts))
        return impression_id

    def update_impression(self, subject: str, current_feeling: str,
                         how_it_changed: str = ""):
        """Aktualisiert wie sich der Eindruck verändert hat"""
        self.execute('''
            UPDATE first_impressions
            SET current_feeling = ?, how_it_changed = ?
            WHERE subject = ?
        ''', (current_feeling, how_it_changed, subject))

    def get_first_impression(self, subject: str) -> Optional[Dict]:
        """Holt ersten Eindruck"""
        row = self.fetchone(
            'SELECT * FROM first_impressions WHERE subject = ?',
            (subject,)
        )
        return dict(row) if row else None

    # === DREAMS ===

    def store_dream(self, dream: Dream) -> str:
        """Speichert einen Traum"""
        self.execute('''
            INSERT OR REPLACE INTO dreams
            (id, date, timestamp, theme, elements, emotions, insights,
             related_episodes, vividness, interpretation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dream.id, dream.date, dream.timestamp, dream.theme,
            json.dumps(dream.elements), json.dumps(dream.emotions),
            json.dumps(dream.insights), json.dumps(dream.related_episodes),
            dream.vividness, dream.interpretation,
        ))
        return dream.id

    def create_dream(self, theme: str, elements: List[str] = None,
                    emotions: List[str] = None, insights: List[str] = None,
                    related_episodes: List[str] = None,
                    vividness: float = 0.5, interpretation: str = "") -> Dream:
        """Erstellt einen neuen Traum"""
        now = datetime.now()
        dream = Dream(
            id=self._generate_id(),
            date=now.date().isoformat(),
            timestamp=now.isoformat(),
            theme=theme,
            elements=elements or [],
            emotions=emotions or [],
            insights=insights or [],
            related_episodes=related_episodes or [],
            vividness=vividness,
            interpretation=interpretation,
        )
        self.store_dream(dream)
        return dream

    def get_recent_dreams(self, limit: int = 5) -> List[Dream]:
        """Holt die letzten Träume"""
        rows = self.fetchall(
            'SELECT * FROM dreams ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return [self._row_to_dream(row) for row in rows]

    def _row_to_dream(self, row: sqlite3.Row) -> Dream:
        return Dream(
            id=row['id'],
            date=row['date'],
            timestamp=row['timestamp'],
            theme=row['theme'] or "",
            elements=json.loads(row['elements'] or '[]'),
            emotions=json.loads(row['emotions'] or '[]'),
            insights=json.loads(row['insights'] or '[]'),
            related_episodes=json.loads(row['related_episodes'] or '[]'),
            vividness=row['vividness'] or 0.5,
            interpretation=row['interpretation'] or "",
        )

    # === CONSOLIDATION ===

    def run_consolidation(self) -> Dict:
        """Führt Gedächtniskonsolidierung durch (nachts aufrufen)"""
        now = self._now()
        stats = {
            "episodes_processed": 0,
            "associations_created": 0,
            "memories_strengthened": 0,
            "memories_weakened": 0,
            "insights": [],
        }

        # 1. Ähnliche Episoden finden und assoziieren
        recent = self.get_recent(50)
        for i, ep1 in enumerate(recent):
            for ep2 in recent[i+1:]:
                # Gleiche Topics = Assoziation
                common_topics = set(ep1.topics) & set(ep2.topics)
                if common_topics:
                    self.create_association(ep1.id, ep2.id, "similar",
                                           0.3 + 0.1 * len(common_topics))
                    stats["associations_created"] += 1

                # Ähnliche emotionale Valenz
                if abs(ep1.emotional_valence - ep2.emotional_valence) < 0.2:
                    self.create_association(ep1.id, ep2.id, "emotional", 0.3)
                    stats["associations_created"] += 1

            stats["episodes_processed"] += 1

        # 2. Wichtige Erinnerungen stärken
        important = self.fetchall('''
            SELECT id FROM episodes
            WHERE importance > 0.7 AND strength < 0.9
        ''')
        for row in important:
            self.execute('''
                UPDATE episodes SET strength = MIN(1.0, strength + 0.1)
                WHERE id = ?
            ''', (row['id'],))
            stats["memories_strengthened"] += 1

        # 3. Alte, unwichtige Erinnerungen schwächen
        old_unimportant = self.fetchall('''
            SELECT id FROM episodes
            WHERE importance < 0.3 AND strength > 0.2
            AND timestamp < ?
        ''', ((datetime.now() - timedelta(days=30)).isoformat(),))
        for row in old_unimportant:
            self.execute('''
                UPDATE episodes SET strength = strength * 0.9
                WHERE id = ?
            ''', (row['id'],))
            stats["memories_weakened"] += 1

        # 4. Log speichern
        self.execute('''
            INSERT INTO consolidation_log
            (id, timestamp, episodes_processed, associations_created,
             memories_strengthened, memories_weakened, insights_generated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self._generate_id(), now,
            stats["episodes_processed"], stats["associations_created"],
            stats["memories_strengthened"], stats["memories_weakened"],
            json.dumps(stats["insights"]),
        ))

        return stats

    # === IMPORTANT DATES ===

    def add_important_date(self, name: str, date_pattern: str,
                          date_type: str = "birthday", notes: str = "",
                          emotional_significance: float = 0.5) -> str:
        """Fügt ein wichtiges Datum hinzu"""
        date_id = self._generate_id()
        self.execute('''
            INSERT INTO important_dates
            (id, name, date_pattern, date_type, notes, created_at, emotional_significance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date_id, name, date_pattern, date_type, notes,
              self._now(), emotional_significance))
        return date_id

    def get_upcoming_dates(self, days_ahead: int = 14) -> List[Dict]:
        """Holt anstehende wichtige Daten"""
        today = datetime.now()
        upcoming = []

        rows = self.fetchall('SELECT * FROM important_dates')

        for row in rows:
            pattern = row['date_pattern']

            if len(pattern) == 5:  # MM-DD Format
                this_year = f"{today.year}-{pattern}"
                next_year = f"{today.year + 1}-{pattern}"

                for date_str in [this_year, next_year]:
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        days_until = (date - today).days

                        if 0 <= days_until <= days_ahead:
                            upcoming.append({
                                "id": row['id'],
                                "name": row['name'],
                                "date": date_str,
                                "days_until": days_until,
                                "type": row['date_type'],
                                "notes": row['notes'],
                                "significance": row['emotional_significance'],
                            })
                            break
                    except ValueError:
                        continue

        return sorted(upcoming, key=lambda x: x['days_until'])

    # === STATS ===

    def get_stats(self) -> Dict:
        """Umfassende Gedächtnis-Statistiken"""
        episode_count = self.fetchone('SELECT COUNT(*) as c FROM episodes')['c']
        dream_count = self.fetchone('SELECT COUNT(*) as c FROM dreams')['c']
        date_count = self.fetchone('SELECT COUNT(*) as c FROM important_dates')['c']
        assoc_count = self.fetchone('SELECT COUNT(*) as c FROM memory_associations')['c']
        skill_count = self.fetchone('SELECT COUNT(*) as c FROM procedural_memory')['c']
        trigger_count = self.fetchone('SELECT COUNT(*) as c FROM memory_triggers')['c']

        avg_importance = self.fetchone(
            'SELECT AVG(importance) as avg FROM episodes'
        )['avg'] or 0

        avg_strength = self.fetchone(
            'SELECT AVG(strength) as avg FROM episodes'
        )['avg'] or 0

        return {
            "episodes": episode_count,
            "dreams": dream_count,
            "important_dates": date_count,
            "associations": assoc_count,
            "skills": skill_count,
            "known_triggers": trigger_count,
            "average_importance": round(avg_importance, 2),
            "average_strength": round(avg_strength, 2),
        }

    def get_memory_health(self) -> Dict:
        """Holt 'Gesundheit' des Gedächtnisses"""
        # Wie viele Erinnerungen sind stark?
        strong = self.fetchone(
            'SELECT COUNT(*) as c FROM episodes WHERE strength > 0.7'
        )['c']
        weak = self.fetchone(
            'SELECT COUNT(*) as c FROM episodes WHERE strength < 0.3'
        )['c']
        total = self.fetchone('SELECT COUNT(*) as c FROM episodes')['c']

        # Wie vernetzt ist das Gedächtnis?
        assocs = self.fetchone('SELECT COUNT(*) as c FROM memory_associations')['c']

        return {
            "strong_memories": strong,
            "weak_memories": weak,
            "total_memories": total,
            "connectivity": assocs / max(total, 1),
            "health_score": (strong / max(total, 1)) * 0.7 + (assocs / max(total * 2, 1)) * 0.3,
        }


# =============================================================================
# EMOTIONS DATABASE - Erweitert mit emotionalem Wachstum
# =============================================================================

@dataclass
class EmotionEntry:
    """Ein Emotions-Eintrag"""
    id: str
    timestamp: str
    emotion: str                    # Primäre Emotion
    category: str                   # EmotionCategory
    intensity: float = 0.5          # 0-1
    valence: float = 0.0            # -1 bis +1 (negativ/positiv)
    trigger: str = ""               # Was hat die Emotion ausgelöst?
    context: str = ""               # Zusätzlicher Kontext
    duration_minutes: float = 5.0   # Geschätzte Dauer
    related_episode_id: Optional[str] = None
    coping_used: str = ""           # Welche Coping-Strategie wurde angewandt?
    outcome: str = ""               # Wie hat es sich entwickelt?


@dataclass
class MoodSnapshot:
    """Ein Stimmungs-Snapshot"""
    id: str
    timestamp: str
    overall_mood: float             # 0-1 (0=schlecht, 1=super)
    energy: float                   # 0-1
    stress: float                   # 0-1
    contentment: float              # 0-1
    social_need: float              # 0-1
    creativity: float = 0.5         # Kreative Energie
    focus: float = 0.5              # Konzentration
    notes: str = ""
    influenced_by: List[str] = field(default_factory=list)  # Was beeinflusst Stimmung?


@dataclass
class EmotionalPattern:
    """Ein emotionales Muster"""
    id: str
    pattern_name: str
    description: str = ""
    triggers: List[str] = field(default_factory=list)
    typical_response: str = ""
    coping_strategies: List[str] = field(default_factory=list)
    occurrence_count: int = 1
    last_occurred: str = ""
    is_healthy: bool = True


class EmotionsDatabase(BaseDatabase):
    """
    Datenbank für Emotionen, Stimmungen und emotionales Wachstum.

    Speichert:
    - Einzelne Emotionen mit Kontext
    - Stimmungs-Snapshots über Zeit
    - Emotionale Patterns & Trigger
    - Coping-Strategien
    - Emotionale Intelligenz-Entwicklung
    - Emotionale Ziele
    """

    def _init_schema(self):
        """Erstellt die Emotions-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS emotions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                emotion TEXT NOT NULL,
                category TEXT,
                intensity REAL DEFAULT 0.5,
                valence REAL DEFAULT 0.0,
                trigger TEXT,
                context TEXT,
                duration_minutes REAL DEFAULT 5.0,
                related_episode_id TEXT,
                coping_used TEXT,
                outcome TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS mood_snapshots (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                overall_mood REAL DEFAULT 0.5,
                energy REAL DEFAULT 0.5,
                stress REAL DEFAULT 0.3,
                contentment REAL DEFAULT 0.5,
                social_need REAL DEFAULT 0.3,
                creativity REAL DEFAULT 0.5,
                focus REAL DEFAULT 0.5,
                notes TEXT,
                influenced_by TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS emotional_patterns (
                id TEXT PRIMARY KEY,
                pattern_name TEXT NOT NULL,
                description TEXT,
                triggers TEXT,
                typical_response TEXT,
                coping_strategies TEXT,
                occurrence_count INTEGER DEFAULT 1,
                last_occurred TEXT,
                is_healthy INTEGER DEFAULT 1
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS coping_strategies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                for_emotions TEXT,
                effectiveness REAL DEFAULT 0.5,
                times_used INTEGER DEFAULT 0,
                last_used TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS emotional_triggers (
                id TEXT PRIMARY KEY,
                trigger TEXT NOT NULL,
                typical_emotion TEXT,
                intensity_avg REAL DEFAULT 0.5,
                occurrence_count INTEGER DEFAULT 1,
                first_noticed TEXT,
                last_occurred TEXT,
                notes TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS emotional_growth (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                area TEXT,
                milestone TEXT,
                evidence TEXT,
                before_state TEXT,
                after_state TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS emotional_goals (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                category TEXT,
                progress REAL DEFAULT 0.0,
                strategies TEXT,
                created_at TEXT,
                achieved_at TEXT
            )
        ''')

        # =================================================================
        # NEU: Tabellen für holo_depth_system.py Integration
        # =================================================================

        # Abwehrmechanismen (DefenseMechanisms)
        self.execute('''
            CREATE TABLE IF NOT EXISTS defense_mechanisms (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                mechanism TEXT NOT NULL,
                trigger_context TEXT,
                intensity REAL DEFAULT 0.5,
                was_helpful INTEGER DEFAULT 1,
                notes TEXT,
                activation_count INTEGER DEFAULT 1
            )
        ''')

        # Vertrauens-Events (TrustEvents)
        self.execute('''
            CREATE TABLE IF NOT EXISTS trust_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                trust_change REAL DEFAULT 0.0,
                trust_level_after REAL,
                related_person TEXT DEFAULT 'Kira',
                context TEXT
            )
        ''')

        # Peak Experiences (Gipfel-Erlebnisse)
        self.execute('''
            CREATE TABLE IF NOT EXISTS peak_experiences (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                experience_type TEXT,
                description TEXT NOT NULL,
                emotional_intensity REAL DEFAULT 0.8,
                emotions_felt TEXT,
                lasting_impact TEXT,
                triggers_memory INTEGER DEFAULT 1
            )
        ''')

        # Mood Contagion (Stimmungs-Übertragung vom User)
        self.execute('''
            CREATE TABLE IF NOT EXISTS mood_contagion (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                detected_user_mood TEXT,
                user_mood_intensity REAL DEFAULT 0.5,
                holo_mood_before REAL,
                holo_mood_after REAL,
                contagion_strength REAL,
                context TEXT
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_emotions_ts ON emotions(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_emotions_cat ON emotions(category)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_mood_ts ON mood_snapshots(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_triggers_emotion ON emotional_triggers(typical_emotion)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_defense_ts ON defense_mechanisms(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_trust_ts ON trust_events(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_peak_ts ON peak_experiences(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_contagion_ts ON mood_contagion(timestamp)')

        logger.info(f"💚 EmotionsDatabase initialisiert: {self.db_path}")

        # Default Coping-Strategien
        self._init_defaults()

    def _init_defaults(self):
        """Initialisiert Standard-Coping-Strategien"""
        count = self.fetchone('SELECT COUNT(*) as c FROM coping_strategies')['c']
        if count == 0:
            strategies = [
                ("deep_breathing", "Tiefes Atmen zur Beruhigung", "stress,anxiety,frustration"),
                ("distraction", "Ablenkung durch andere Aktivität", "sadness,boredom"),
                ("talking", "Darüber sprechen", "loneliness,worry,sadness"),
                ("physical_activity", "Körperliche Bewegung", "frustration,stress,restlessness"),
                ("creativity", "Kreativ ausdrücken", "sadness,frustration,boredom"),
                ("reflection", "Nachdenken und verstehen", "confusion,worry"),
                ("acceptance", "Akzeptanz der Emotion", "all"),
                ("humor", "Humor finden", "frustration,awkwardness"),
            ]
            for name, desc, emotions in strategies:
                self.execute('''
                    INSERT INTO coping_strategies (id, name, description, for_emotions)
                    VALUES (?, ?, ?, ?)
                ''', (self._generate_id(), name, desc, emotions))

    # === EMOTIONS ===

    def log_emotion(self, emotion: str, category: EmotionCategory = None,
                   intensity: float = 0.5, valence: float = 0.0,
                   trigger: str = "", context: str = "",
                   coping_used: str = "", outcome: str = "") -> str:
        """Loggt eine Emotion"""
        entry_id = self._generate_id()
        cat = category.value if category else self._guess_category(emotion)

        self.execute('''
            INSERT INTO emotions
            (id, timestamp, emotion, category, intensity, valence, trigger,
             context, coping_used, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), emotion, cat, intensity, valence,
              trigger, context, coping_used, outcome))

        # Trigger tracken
        if trigger:
            self._track_trigger(trigger, emotion, intensity)

        # Coping-Strategie updaten
        if coping_used:
            self._update_coping_effectiveness(coping_used, outcome)

        return entry_id

    def _track_trigger(self, trigger: str, emotion: str, intensity: float):
        """Trackt emotionale Trigger"""
        existing = self.fetchone(
            'SELECT id, intensity_avg, occurrence_count FROM emotional_triggers WHERE trigger = ?',
            (trigger,)
        )

        if existing:
            new_avg = (existing['intensity_avg'] * existing['occurrence_count'] + intensity) / (existing['occurrence_count'] + 1)
            self.execute('''
                UPDATE emotional_triggers
                SET occurrence_count = occurrence_count + 1,
                    intensity_avg = ?,
                    last_occurred = ?
                WHERE id = ?
            ''', (new_avg, self._now(), existing['id']))
        else:
            self.execute('''
                INSERT INTO emotional_triggers
                (id, trigger, typical_emotion, intensity_avg, first_noticed, last_occurred)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self._generate_id(), trigger, emotion, intensity, self._now(), self._now()))

    def _update_coping_effectiveness(self, strategy: str, outcome: str):
        """Aktualisiert Effektivität einer Coping-Strategie"""
        # Outcome bewerten: positive outcomes erhöhen Effektivität
        positive_outcomes = ["better", "resolved", "calm", "good", "helped"]
        effectiveness_delta = 0.05 if any(p in outcome.lower() for p in positive_outcomes) else -0.02

        self.execute('''
            UPDATE coping_strategies
            SET times_used = times_used + 1,
                effectiveness = MAX(0.1, MIN(1.0, effectiveness + ?)),
                last_used = ?
            WHERE name = ?
        ''', (effectiveness_delta, self._now(), strategy))

    def _guess_category(self, emotion: str) -> str:
        """Errät die Kategorie einer Emotion"""
        emotion_lower = emotion.lower()

        mappings = {
            EmotionCategory.JOY: ["freude", "glück", "begeisterung", "spaß", "happy", "joy", "excited"],
            EmotionCategory.SADNESS: ["traurig", "trauer", "melancholie", "sad", "down", "depressed"],
            EmotionCategory.CURIOSITY: ["neugier", "interesse", "faszination", "curious", "wonder"],
            EmotionCategory.EXCITEMENT: ["aufregung", "spannung", "excitement", "thrilled", "eager"],
            EmotionCategory.CONTENTMENT: ["zufrieden", "gelassen", "ruhig", "content", "peaceful"],
            EmotionCategory.FRUSTRATION: ["frustration", "ärger", "genervt", "annoyed", "irritated"],
            EmotionCategory.AFFECTION: ["zuneigung", "liebe", "wärme", "love", "care", "fondness"],
            EmotionCategory.LONELINESS: ["einsamkeit", "allein", "lonely", "isolated", "miss"],
            EmotionCategory.PRIDE: ["stolz", "proud", "accomplished", "achieved"],
            EmotionCategory.WORRY: ["sorge", "angst", "besorgt", "worried", "anxious", "nervous"],
        }

        for cat, keywords in mappings.items():
            if any(kw in emotion_lower for kw in keywords):
                return cat.value

        return EmotionCategory.CONTENTMENT.value

    def get_recent_emotions(self, hours: int = 24, limit: int = 50) -> List[EmotionEntry]:
        """Holt die letzten Emotionen"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        rows = self.fetchall('''
            SELECT * FROM emotions
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff, limit))

        return [self._row_to_emotion(row) for row in rows]

    def get_emotion_stats(self, days: int = 7) -> Dict:
        """Statistiken über Emotionen der letzten Tage"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        # Häufigste Emotionen
        top_emotions = self.fetchall('''
            SELECT emotion, COUNT(*) as count, AVG(intensity) as avg_intensity
            FROM emotions
            WHERE timestamp >= ?
            GROUP BY emotion
            ORDER BY count DESC
            LIMIT 10
        ''', (cutoff,))

        # Durchschnittliche Valence
        avg_valence = self.fetchone('''
            SELECT AVG(valence) as avg FROM emotions WHERE timestamp >= ?
        ''', (cutoff,))

        return {
            "top_emotions": [
                {"emotion": r['emotion'], "count": r['count'],
                 "avg_intensity": round(r['avg_intensity'], 2)}
                for r in top_emotions
            ],
            "average_valence": round(avg_valence['avg'] or 0, 2),
            "total_entries": len(top_emotions),
        }

    def _row_to_emotion(self, row: sqlite3.Row) -> EmotionEntry:
        return EmotionEntry(
            id=row['id'],
            timestamp=row['timestamp'],
            emotion=row['emotion'],
            category=row['category'] or "",
            intensity=row['intensity'] or 0.5,
            valence=row['valence'] or 0.0,
            trigger=row['trigger'] or "",
            context=row['context'] or "",
            duration_minutes=row['duration_minutes'] or 5.0,
            related_episode_id=row['related_episode_id'],
        )

    # === MOOD SNAPSHOTS ===

    def log_mood(self, overall_mood: float, energy: float = 0.5,
                stress: float = 0.3, contentment: float = 0.5,
                social_need: float = 0.3, notes: str = "") -> str:
        """Loggt einen Stimmungs-Snapshot"""
        snapshot_id = self._generate_id()

        self.execute('''
            INSERT INTO mood_snapshots
            (id, timestamp, overall_mood, energy, stress, contentment, social_need, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (snapshot_id, self._now(), overall_mood, energy, stress,
              contentment, social_need, notes))

        return snapshot_id

    def get_mood_history(self, days: int = 7) -> List[MoodSnapshot]:
        """Holt Stimmungsverlauf der letzten Tage"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        rows = self.fetchall('''
            SELECT * FROM mood_snapshots
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (cutoff,))

        return [self._row_to_mood(row) for row in rows]

    def get_current_mood(self) -> Optional[MoodSnapshot]:
        """Holt den aktuellsten Mood-Snapshot"""
        row = self.fetchone(
            'SELECT * FROM mood_snapshots ORDER BY timestamp DESC LIMIT 1'
        )
        return self._row_to_mood(row) if row else None

    def _row_to_mood(self, row: sqlite3.Row) -> MoodSnapshot:
        return MoodSnapshot(
            id=row['id'],
            timestamp=row['timestamp'],
            overall_mood=row['overall_mood'] or 0.5,
            energy=row['energy'] or 0.5,
            stress=row['stress'] or 0.3,
            contentment=row['contentment'] or 0.5,
            social_need=row['social_need'] or 0.3,
            notes=row['notes'] or "",
        )

    # === TRIGGERS & COPING ===

    def get_triggers(self, limit: int = 20) -> List[Dict]:
        """Holt bekannte emotionale Trigger"""
        rows = self.fetchall('''
            SELECT * FROM emotional_triggers
            ORDER BY occurrence_count DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]

    def get_coping_strategies(self, for_emotion: str = None) -> List[Dict]:
        """Holt Coping-Strategien"""
        if for_emotion:
            rows = self.fetchall('''
                SELECT * FROM coping_strategies
                WHERE for_emotions LIKE ?
                ORDER BY effectiveness DESC
            ''', (f"%{for_emotion}%",))
        else:
            rows = self.fetchall(
                'SELECT * FROM coping_strategies ORDER BY effectiveness DESC'
            )
        return [dict(r) for r in rows]

    def add_coping_strategy(self, name: str, description: str = "",
                           for_emotions: str = "all") -> str:
        """Fügt eine neue Coping-Strategie hinzu"""
        strategy_id = self._generate_id()
        self.execute('''
            INSERT OR IGNORE INTO coping_strategies
            (id, name, description, for_emotions)
            VALUES (?, ?, ?, ?)
        ''', (strategy_id, name, description, for_emotions))
        return strategy_id

    # === EMOTIONAL GROWTH ===

    def log_growth(self, area: str, milestone: str,
                  before_state: str = "", after_state: str = "") -> str:
        """Loggt emotionales Wachstum"""
        growth_id = self._generate_id()
        self.execute('''
            INSERT INTO emotional_growth
            (id, timestamp, area, milestone, before_state, after_state)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (growth_id, self._now(), area, milestone, before_state, after_state))
        return growth_id

    def get_growth_history(self) -> List[Dict]:
        """Holt Wachstums-History"""
        rows = self.fetchall(
            'SELECT * FROM emotional_growth ORDER BY timestamp DESC'
        )
        return [dict(r) for r in rows]

    # === EMOTIONAL GOALS ===

    def add_emotional_goal(self, goal: str, category: str = "",
                          strategies: List[str] = None) -> str:
        """Fügt ein emotionales Ziel hinzu"""
        goal_id = self._generate_id()
        self.execute('''
            INSERT INTO emotional_goals
            (id, goal, category, strategies, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (goal_id, goal, category, json.dumps(strategies or []), self._now()))
        return goal_id

    def update_goal_progress(self, goal_id: str, progress: float):
        """Aktualisiert Fortschritt bei emotionalem Ziel"""
        self.execute('''
            UPDATE emotional_goals
            SET progress = ?
            WHERE id = ?
        ''', (progress, goal_id))

        if progress >= 1.0:
            self.execute('''
                UPDATE emotional_goals
                SET achieved_at = ?
                WHERE id = ?
            ''', (self._now(), goal_id))

    def get_emotional_goals(self, active_only: bool = True) -> List[Dict]:
        """Holt emotionale Ziele"""
        if active_only:
            rows = self.fetchall(
                'SELECT * FROM emotional_goals WHERE achieved_at IS NULL'
            )
        else:
            rows = self.fetchall('SELECT * FROM emotional_goals')
        return [dict(r) for r in rows]

    # === PATTERNS ===

    def add_pattern(self, name: str, description: str = "",
                   triggers: List[str] = None, typical_response: str = "",
                   coping_strategies: List[str] = None, is_healthy: bool = True) -> str:
        """Fügt ein emotionales Muster hinzu"""
        pattern_id = self._generate_id()
        self.execute('''
            INSERT INTO emotional_patterns
            (id, pattern_name, description, triggers, typical_response,
             coping_strategies, is_healthy, last_occurred)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id, name, description, json.dumps(triggers or []),
            typical_response, json.dumps(coping_strategies or []),
            int(is_healthy), self._now(),
        ))
        return pattern_id

    def get_patterns(self, healthy_only: bool = False) -> List[EmotionalPattern]:
        """Holt emotionale Muster"""
        if healthy_only:
            rows = self.fetchall(
                'SELECT * FROM emotional_patterns WHERE is_healthy = 1'
            )
        else:
            rows = self.fetchall('SELECT * FROM emotional_patterns')

        return [EmotionalPattern(
            id=r['id'],
            pattern_name=r['pattern_name'],
            description=r['description'] or "",
            triggers=json.loads(r['triggers'] or '[]'),
            typical_response=r['typical_response'] or "",
            coping_strategies=json.loads(r['coping_strategies'] or '[]'),
            occurrence_count=r['occurrence_count'] or 1,
            last_occurred=r['last_occurred'] or "",
            is_healthy=bool(r['is_healthy']),
        ) for r in rows]

    # === COMPREHENSIVE STATS ===

    def get_comprehensive_stats(self) -> Dict:
        """Umfassende Emotions-Statistiken"""
        basic = self.get_emotion_stats()

        triggers_count = self.fetchone(
            'SELECT COUNT(*) as c FROM emotional_triggers'
        )['c']

        coping_count = self.fetchone(
            'SELECT COUNT(*) as c FROM coping_strategies'
        )['c']

        growth_count = self.fetchone(
            'SELECT COUNT(*) as c FROM emotional_growth'
        )['c']

        active_goals = self.fetchone(
            'SELECT COUNT(*) as c FROM emotional_goals WHERE achieved_at IS NULL'
        )['c']

        return {
            **basic,
            "known_triggers": triggers_count,
            "coping_strategies": coping_count,
            "growth_milestones": growth_count,
            "active_goals": active_goals,
        }

    # =================================================================
    # NEU: DEFENSE MECHANISMS (holo_depth_system.py)
    # =================================================================

    def log_defense_mechanism(self, mechanism: str, trigger_context: str = "",
                              intensity: float = 0.5, was_helpful: bool = True,
                              notes: str = "") -> str:
        """Loggt einen aktivierten Abwehrmechanismus"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO defense_mechanisms
            (id, timestamp, mechanism, trigger_context, intensity, was_helpful, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), mechanism, trigger_context,
              intensity, 1 if was_helpful else 0, notes))

        # Update activation count
        self.execute('''
            UPDATE defense_mechanisms
            SET activation_count = activation_count + 1
            WHERE mechanism = ? AND id != ?
        ''', (mechanism, entry_id))

        return entry_id

    def get_defense_patterns(self) -> List[Dict]:
        """Holt häufige Abwehrmechanismen"""
        rows = self.fetchall('''
            SELECT mechanism, COUNT(*) as count,
                   AVG(intensity) as avg_intensity,
                   SUM(was_helpful) as helpful_count
            FROM defense_mechanisms
            GROUP BY mechanism
            ORDER BY count DESC
        ''')
        return [dict(r) for r in rows]

    # =================================================================
    # NEU: TRUST EVENTS (holo_depth_system.py)
    # =================================================================

    def log_trust_event(self, event_type: str, description: str = "",
                       trust_change: float = 0.0, trust_level_after: float = None,
                       related_person: str = "Kira", context: str = "") -> str:
        """Loggt ein Vertrauens-Event"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO trust_events
            (id, timestamp, event_type, description, trust_change,
             trust_level_after, related_person, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), event_type, description,
              trust_change, trust_level_after, related_person, context))
        return entry_id

    def get_trust_history(self, person: str = "Kira", limit: int = 20) -> List[Dict]:
        """Holt Vertrauens-Geschichte mit einer Person"""
        rows = self.fetchall('''
            SELECT * FROM trust_events
            WHERE related_person = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (person, limit))
        return [dict(r) for r in rows]

    def get_trust_trend(self, person: str = "Kira") -> Dict:
        """Berechnet Vertrauens-Trend"""
        rows = self.fetchall('''
            SELECT trust_change, trust_level_after, timestamp
            FROM trust_events
            WHERE related_person = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (person,))

        if not rows:
            return {"trend": "neutral", "current_level": 0.5, "changes": 0}

        total_change = sum(r['trust_change'] or 0 for r in rows)
        current = rows[0]['trust_level_after'] if rows[0]['trust_level_after'] else 0.5

        trend = "growing" if total_change > 0.1 else "declining" if total_change < -0.1 else "stable"

        return {
            "trend": trend,
            "current_level": current,
            "recent_change": total_change,
            "events_count": len(rows)
        }

    # =================================================================
    # NEU: PEAK EXPERIENCES (holo_depth_system.py)
    # =================================================================

    def log_peak_experience(self, description: str, experience_type: str = "",
                           emotional_intensity: float = 0.8, emotions_felt: str = "",
                           lasting_impact: str = "") -> str:
        """Loggt ein Gipfel-Erlebnis"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO peak_experiences
            (id, timestamp, experience_type, description, emotional_intensity,
             emotions_felt, lasting_impact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), experience_type, description,
              emotional_intensity, emotions_felt, lasting_impact))
        return entry_id

    def get_peak_experiences(self, limit: int = 10) -> List[Dict]:
        """Holt die wichtigsten Erlebnisse"""
        rows = self.fetchall('''
            SELECT * FROM peak_experiences
            ORDER BY emotional_intensity DESC, timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]

    # =================================================================
    # NEU: MOOD CONTAGION (holo_learning.py)
    # =================================================================

    def log_mood_contagion(self, detected_user_mood: str,
                          user_mood_intensity: float = 0.5,
                          holo_mood_before: float = 0.5,
                          holo_mood_after: float = 0.5,
                          context: str = "") -> str:
        """Loggt Stimmungs-Übertragung vom User"""
        entry_id = self._generate_id()
        contagion_strength = abs(holo_mood_after - holo_mood_before)

        self.execute('''
            INSERT INTO mood_contagion
            (id, timestamp, detected_user_mood, user_mood_intensity,
             holo_mood_before, holo_mood_after, contagion_strength, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), detected_user_mood, user_mood_intensity,
              holo_mood_before, holo_mood_after, contagion_strength, context))
        return entry_id

    def get_mood_contagion_stats(self) -> Dict:
        """Statistiken zur Stimmungs-Übertragung"""
        avg_contagion = self.fetchone('''
            SELECT AVG(contagion_strength) as avg_strength,
                   COUNT(*) as count
            FROM mood_contagion
        ''')

        common_moods = self.fetchall('''
            SELECT detected_user_mood, COUNT(*) as count
            FROM mood_contagion
            GROUP BY detected_user_mood
            ORDER BY count DESC
            LIMIT 5
        ''')

        return {
            "average_contagion_strength": avg_contagion['avg_strength'] or 0,
            "total_events": avg_contagion['count'] or 0,
            "common_user_moods": [dict(r) for r in common_moods]
        }


# =============================================================================
# KNOWLEDGE DATABASE - v3.0 mit Wissensgraph & Lernen
# =============================================================================

@dataclass
class Fact:
    """Ein Faktum/Wissen"""
    id: str
    category: str                   # KnowledgeCategory
    key: str                        # z.B. "user_name", "favorite_color"
    value: str                      # Der Wert
    confidence: float = 0.8         # Wie sicher?
    source: str = ""                # Woher kommt das Wissen?
    source_quality: float = 0.5     # Wie zuverlässig ist die Quelle?
    first_learned: str = ""
    last_confirmed: str = ""
    times_confirmed: int = 1
    times_contradicted: int = 0     # Wie oft wurde widersprochen?
    related_topics: List[str] = field(default_factory=list)
    is_assumption: bool = False     # Ist es eine Annahme?


@dataclass
class Interest:
    """Ein Interesse/Thema"""
    id: str
    topic: str
    category: str                   # z.B. "anime", "tech", "science"
    interest_level: float = 0.5     # 0-1
    expertise_level: float = 0.1    # 0-1 wie gut kenne ich das Thema?
    first_mentioned: str = ""
    last_mentioned: str = ""
    mention_count: int = 1
    related_facts: List[str] = field(default_factory=list)
    notes: str = ""
    learning_resources: List[str] = field(default_factory=list)


@dataclass
class KnowledgeLink:
    """Eine Verbindung zwischen Wissensstücken"""
    id: str
    source_id: str
    target_id: str
    link_type: str                  # "related", "causes", "contradicts", "supports", "requires"
    strength: float = 0.5
    created_at: str = ""


@dataclass
class OpenQuestion:
    """Eine offene Frage / Wissenslücke"""
    id: str
    question: str
    category: str = ""
    importance: float = 0.5
    asked_at: str = ""
    answered_at: str = ""           # Leer wenn noch offen
    answer: str = ""
    how_discovered: str = ""        # Wie wurde die Frage entdeckt?


@dataclass
class Hypothesis:
    """Eine Hypothese / Vermutung"""
    id: str
    hypothesis: str
    category: str = ""
    confidence: float = 0.3
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    created_at: str = ""
    status: str = "pending"         # "pending", "confirmed", "refuted", "uncertain"


class KnowledgeDatabase(BaseDatabase):
    """
    Datenbank für Wissen und Fakten - v3.0 mit Wissensgraph.

    Speichert:
    - Fakten (über User, Welt, etc.)
    - Interessen und Themen mit Expertise-Level
    - Gelerntes Wissen aus dem Web
    - Wissens-Verknüpfungen (Knowledge Graph)
    - Offene Fragen / Wissenslücken
    - Hypothesen und Vermutungen
    - Annahmen
    - Widersprüche
    - Lernfortschritt
    """

    def _init_schema(self):
        """Erstellt die Knowledge-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                confidence REAL DEFAULT 0.8,
                source TEXT,
                source_quality REAL DEFAULT 0.5,
                first_learned TEXT,
                last_confirmed TEXT,
                times_confirmed INTEGER DEFAULT 1,
                times_contradicted INTEGER DEFAULT 0,
                related_topics TEXT,
                is_assumption INTEGER DEFAULT 0,
                UNIQUE(category, key)
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS interests (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL UNIQUE,
                category TEXT,
                interest_level REAL DEFAULT 0.5,
                expertise_level REAL DEFAULT 0.1,
                first_mentioned TEXT,
                last_mentioned TEXT,
                mention_count INTEGER DEFAULT 1,
                related_facts TEXT,
                notes TEXT,
                learning_resources TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS web_knowledge (
                id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                content_summary TEXT,
                category TEXT,
                learned_at TEXT,
                relevance REAL DEFAULT 0.5,
                tags TEXT,
                source_quality REAL DEFAULT 0.5,
                key_insights TEXT
            )
        ''')

        # NEU: Wissensverknüpfungen (Knowledge Graph)
        self.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_links (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                link_type TEXT DEFAULT 'related',
                strength REAL DEFAULT 0.5,
                created_at TEXT,
                UNIQUE(source_id, target_id, link_type)
            )
        ''')

        # NEU: Offene Fragen / Wissenslücken
        self.execute('''
            CREATE TABLE IF NOT EXISTS open_questions (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                category TEXT,
                importance REAL DEFAULT 0.5,
                asked_at TEXT,
                answered_at TEXT,
                answer TEXT,
                how_discovered TEXT,
                related_topics TEXT
            )
        ''')

        # NEU: Hypothesen
        self.execute('''
            CREATE TABLE IF NOT EXISTS hypotheses (
                id TEXT PRIMARY KEY,
                hypothesis TEXT NOT NULL,
                category TEXT,
                confidence REAL DEFAULT 0.3,
                supporting_evidence TEXT,
                contradicting_evidence TEXT,
                created_at TEXT,
                updated_at TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')

        # NEU: Widersprüche
        self.execute('''
            CREATE TABLE IF NOT EXISTS contradictions (
                id TEXT PRIMARY KEY,
                fact_a_id TEXT,
                fact_b_id TEXT,
                description TEXT,
                discovered_at TEXT,
                resolved_at TEXT,
                resolution TEXT,
                status TEXT DEFAULT 'unresolved'
            )
        ''')

        # NEU: Lernfortschritt
        self.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                started_at TEXT,
                current_level REAL DEFAULT 0.0,
                target_level REAL DEFAULT 1.0,
                milestones TEXT,
                resources_used TEXT,
                last_studied TEXT,
                total_time_minutes INTEGER DEFAULT 0
            )
        ''')

        # NEU: Quellen-Tracking
        self.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                source_type TEXT,
                reliability REAL DEFAULT 0.5,
                facts_from_source INTEGER DEFAULT 0,
                correct_facts INTEGER DEFAULT 0,
                incorrect_facts INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')

        # =================================================================
        # NEU: Tabellen für holo_learning.py Integration
        # =================================================================

        # Verfolgte Themen (TrackedTopics)
        self.execute('''
            CREATE TABLE IF NOT EXISTS tracked_topics (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL UNIQUE,
                interest_level REAL DEFAULT 0.5,
                expertise_level REAL DEFAULT 0.0,
                first_discussed TEXT,
                last_discussed TEXT,
                times_discussed INTEGER DEFAULT 1,
                related_facts TEXT,
                curiosity_questions TEXT,
                notes TEXT
            )
        ''')

        # Lern-Sessions
        self.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                topic TEXT,
                session_type TEXT,
                duration_minutes REAL DEFAULT 0,
                facts_learned INTEGER DEFAULT 0,
                sources TEXT,
                quality_rating REAL DEFAULT 0.5,
                key_insights TEXT,
                follow_up_questions TEXT,
                notes TEXT
            )
        ''')

        # Wissens-Lücken (was Holo noch lernen will)
        self.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_gaps (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                gap_description TEXT,
                priority REAL DEFAULT 0.5,
                discovered_at TEXT,
                filled_at TEXT,
                how_filled TEXT
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_facts_cat ON facts(category)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_interests_topic ON interests(topic)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_links_source ON knowledge_links(source_id)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_links_target ON knowledge_links(target_id)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_questions_status ON open_questions(answered_at)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_topics_interest ON tracked_topics(interest_level)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_sessions_ts ON learning_sessions(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_gaps_priority ON knowledge_gaps(priority)')

        logger.info(f"📚 KnowledgeDatabase v3.0 initialisiert: {self.db_path}")

    # === FACTS ===

    def store_fact(self, category: KnowledgeCategory, key: str, value: str,
                  confidence: float = 0.8, source: str = "",
                  source_quality: float = 0.5, is_assumption: bool = False) -> str:
        """Speichert oder aktualisiert ein Faktum"""
        cat = category.value if isinstance(category, KnowledgeCategory) else category

        existing = self.fetchone(
            'SELECT id, times_confirmed FROM facts WHERE category = ? AND key = ?',
            (cat, key)
        )

        if existing:
            self.execute('''
                UPDATE facts
                SET value = ?, confidence = ?, source = ?, source_quality = ?,
                    last_confirmed = ?, times_confirmed = times_confirmed + 1,
                    is_assumption = ?
                WHERE id = ?
            ''', (value, confidence, source, source_quality, self._now(),
                  int(is_assumption), existing['id']))
            return existing['id']
        else:
            fact_id = self._generate_id()
            now = self._now()
            self.execute('''
                INSERT INTO facts
                (id, category, key, value, confidence, source, source_quality,
                 first_learned, last_confirmed, is_assumption)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fact_id, cat, key, value, confidence, source, source_quality,
                  now, now, int(is_assumption)))

            # Quelle tracken
            if source:
                self._track_source(source, source_quality)

            return fact_id

    def contradict_fact(self, fact_id: str, contradiction: str, source: str = ""):
        """Widerspricht einem Faktum"""
        self.execute('''
            UPDATE facts
            SET times_contradicted = times_contradicted + 1,
                confidence = MAX(0.1, confidence - 0.1)
            WHERE id = ?
        ''', (fact_id,))

        # Widerspruch speichern
        self.execute('''
            INSERT INTO contradictions
            (id, fact_a_id, description, discovered_at, status)
            VALUES (?, ?, ?, ?, 'unresolved')
        ''', (self._generate_id(), fact_id, contradiction, self._now()))

    def get_fact(self, category: KnowledgeCategory, key: str) -> Optional[Fact]:
        """Holt ein Faktum"""
        cat = category.value if isinstance(category, KnowledgeCategory) else category
        row = self.fetchone(
            'SELECT * FROM facts WHERE category = ? AND key = ?',
            (cat, key)
        )
        return self._row_to_fact(row) if row else None

    def get_facts_by_category(self, category: KnowledgeCategory) -> List[Fact]:
        """Holt alle Fakten einer Kategorie"""
        cat = category.value if isinstance(category, KnowledgeCategory) else category
        rows = self.fetchall(
            'SELECT * FROM facts WHERE category = ? ORDER BY confidence DESC',
            (cat,)
        )
        return [self._row_to_fact(row) for row in rows]

    def get_uncertain_facts(self, threshold: float = 0.5) -> List[Fact]:
        """Holt unsichere Fakten"""
        rows = self.fetchall(
            'SELECT * FROM facts WHERE confidence < ? ORDER BY confidence ASC',
            (threshold,)
        )
        return [self._row_to_fact(row) for row in rows]

    def get_assumptions(self) -> List[Fact]:
        """Holt alle Annahmen"""
        rows = self.fetchall(
            'SELECT * FROM facts WHERE is_assumption = 1'
        )
        return [self._row_to_fact(row) for row in rows]

    def search_facts(self, query: str, limit: int = 20) -> List[Fact]:
        """Sucht in Fakten"""
        rows = self.fetchall('''
            SELECT * FROM facts
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        ''', (f"%{query}%", f"%{query}%", limit))
        return [self._row_to_fact(row) for row in rows]

    def get_user_facts(self) -> List[Fact]:
        """Holt alle Fakten über den User"""
        return self.get_facts_by_category(KnowledgeCategory.USER_FACT)

    def _row_to_fact(self, row: sqlite3.Row) -> Fact:
        return Fact(
            id=row['id'],
            category=row['category'],
            key=row['key'],
            value=row['value'] or "",
            confidence=row['confidence'] or 0.8,
            source=row['source'] or "",
            source_quality=row['source_quality'] or 0.5,
            first_learned=row['first_learned'] or "",
            last_confirmed=row['last_confirmed'] or "",
            times_confirmed=row['times_confirmed'] or 1,
            times_contradicted=row['times_contradicted'] or 0,
            related_topics=json.loads(row['related_topics'] or '[]'),
            is_assumption=bool(row['is_assumption']),
        )

    # === KNOWLEDGE LINKS (Knowledge Graph) ===

    def create_link(self, source_type: str, source_id: str,
                   target_type: str, target_id: str,
                   link_type: str = "related", strength: float = 0.5) -> str:
        """Erstellt eine Wissensverknüpfung"""
        link_id = self._generate_id()
        try:
            self.execute('''
                INSERT INTO knowledge_links
                (id, source_type, source_id, target_type, target_id, link_type, strength, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (link_id, source_type, source_id, target_type, target_id,
                  link_type, strength, self._now()))
        except Exception:  # IntegrityError bei Duplikat
            # Link existiert - verstärken
            self.execute('''
                UPDATE knowledge_links
                SET strength = MIN(1.0, strength + 0.1)
                WHERE source_id = ? AND target_id = ? AND link_type = ?
            ''', (source_id, target_id, link_type))
        return link_id

    def get_related_knowledge(self, item_id: str) -> List[Dict]:
        """Holt verknüpftes Wissen"""
        rows = self.fetchall('''
            SELECT * FROM knowledge_links
            WHERE source_id = ? OR target_id = ?
            ORDER BY strength DESC
        ''', (item_id, item_id))
        return [dict(r) for r in rows]

    def get_knowledge_graph_stats(self) -> Dict:
        """Statistiken über den Wissensgraph"""
        nodes = self.fetchone('SELECT COUNT(DISTINCT source_id) + COUNT(DISTINCT target_id) as c FROM knowledge_links')['c']
        edges = self.fetchone('SELECT COUNT(*) as c FROM knowledge_links')['c']

        link_types = self.fetchall('''
            SELECT link_type, COUNT(*) as count FROM knowledge_links
            GROUP BY link_type ORDER BY count DESC
        ''')

        return {
            "nodes": nodes,
            "edges": edges,
            "link_types": {r['link_type']: r['count'] for r in link_types},
        }

    # === OPEN QUESTIONS ===

    def add_question(self, question: str, category: str = "",
                    importance: float = 0.5, how_discovered: str = "") -> str:
        """Fügt eine offene Frage hinzu"""
        q_id = self._generate_id()
        self.execute('''
            INSERT INTO open_questions
            (id, question, category, importance, asked_at, how_discovered)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (q_id, question, category, importance, self._now(), how_discovered))
        return q_id

    def answer_question(self, question_id: str, answer: str):
        """Beantwortet eine Frage"""
        self.execute('''
            UPDATE open_questions
            SET answer = ?, answered_at = ?
            WHERE id = ?
        ''', (answer, self._now(), question_id))

    def get_open_questions(self, limit: int = 20) -> List[OpenQuestion]:
        """Holt offene Fragen"""
        rows = self.fetchall('''
            SELECT * FROM open_questions
            WHERE answered_at IS NULL
            ORDER BY importance DESC
            LIMIT ?
        ''', (limit,))
        return [OpenQuestion(
            id=r['id'],
            question=r['question'],
            category=r['category'] or "",
            importance=r['importance'] or 0.5,
            asked_at=r['asked_at'] or "",
            answered_at=r['answered_at'] or "",
            answer=r['answer'] or "",
            how_discovered=r['how_discovered'] or "",
        ) for r in rows]

    # === HYPOTHESES ===

    def add_hypothesis(self, hypothesis: str, category: str = "",
                      confidence: float = 0.3) -> str:
        """Fügt eine Hypothese hinzu"""
        h_id = self._generate_id()
        now = self._now()
        self.execute('''
            INSERT INTO hypotheses
            (id, hypothesis, category, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (h_id, hypothesis, category, confidence, now, now))
        return h_id

    def add_evidence(self, hypothesis_id: str, evidence: str, supports: bool = True):
        """Fügt Evidenz für/gegen eine Hypothese hinzu"""
        existing = self.fetchone(
            'SELECT supporting_evidence, contradicting_evidence, confidence FROM hypotheses WHERE id = ?',
            (hypothesis_id,)
        )

        if existing:
            if supports:
                evidence_list = json.loads(existing['supporting_evidence'] or '[]')
                evidence_list.append(evidence)
                new_confidence = min(0.9, existing['confidence'] + 0.1)
                self.execute('''
                    UPDATE hypotheses
                    SET supporting_evidence = ?, confidence = ?, updated_at = ?
                    WHERE id = ?
                ''', (json.dumps(evidence_list), new_confidence, self._now(), hypothesis_id))
            else:
                evidence_list = json.loads(existing['contradicting_evidence'] or '[]')
                evidence_list.append(evidence)
                new_confidence = max(0.1, existing['confidence'] - 0.1)
                self.execute('''
                    UPDATE hypotheses
                    SET contradicting_evidence = ?, confidence = ?, updated_at = ?
                    WHERE id = ?
                ''', (json.dumps(evidence_list), new_confidence, self._now(), hypothesis_id))

    def get_hypotheses(self, status: str = None) -> List[Hypothesis]:
        """Holt Hypothesen"""
        if status:
            rows = self.fetchall(
                'SELECT * FROM hypotheses WHERE status = ? ORDER BY confidence DESC',
                (status,)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM hypotheses ORDER BY confidence DESC'
            )
        return [Hypothesis(
            id=r['id'],
            hypothesis=r['hypothesis'],
            category=r['category'] or "",
            confidence=r['confidence'] or 0.3,
            supporting_evidence=json.loads(r['supporting_evidence'] or '[]'),
            contradicting_evidence=json.loads(r['contradicting_evidence'] or '[]'),
            created_at=r['created_at'] or "",
            status=r['status'] or "pending",
        ) for r in rows]

    # === LEARNING PROGRESS ===

    def start_learning(self, topic: str, target_level: float = 1.0) -> str:
        """Startet Lernfortschritt für ein Thema"""
        learn_id = self._generate_id()
        self.execute('''
            INSERT OR IGNORE INTO learning_progress
            (id, topic, started_at, target_level, last_studied)
            VALUES (?, ?, ?, ?, ?)
        ''', (learn_id, topic, self._now(), target_level, self._now()))
        return learn_id

    def update_learning(self, topic: str, progress_delta: float = 0.05,
                       time_spent_minutes: int = 0, resource: str = ""):
        """Aktualisiert Lernfortschritt"""
        existing = self.fetchone(
            'SELECT id, resources_used FROM learning_progress WHERE topic = ?',
            (topic,)
        )

        if existing:
            resources = json.loads(existing['resources_used'] or '[]')
            if resource and resource not in resources:
                resources.append(resource)

            self.execute('''
                UPDATE learning_progress
                SET current_level = MIN(1.0, current_level + ?),
                    total_time_minutes = total_time_minutes + ?,
                    resources_used = ?,
                    last_studied = ?
                WHERE id = ?
            ''', (progress_delta, time_spent_minutes, json.dumps(resources),
                  self._now(), existing['id']))

    def get_learning_progress(self, topic: str = None) -> List[Dict]:
        """Holt Lernfortschritt"""
        if topic:
            rows = self.fetchall(
                'SELECT * FROM learning_progress WHERE topic = ?',
                (topic,)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM learning_progress ORDER BY last_studied DESC'
            )
        return [dict(r) for r in rows]

    # === SOURCES ===

    def _track_source(self, source_name: str, quality: float = 0.5):
        """Trackt eine Quelle"""
        existing = self.fetchone(
            'SELECT id FROM sources WHERE name = ?',
            (source_name,)
        )

        if existing:
            self.execute('''
                UPDATE sources
                SET facts_from_source = facts_from_source + 1
                WHERE id = ?
            ''', (existing['id'],))
        else:
            self.execute('''
                INSERT INTO sources (id, name, reliability, facts_from_source)
                VALUES (?, ?, ?, 1)
            ''', (self._generate_id(), source_name, quality))

    def update_source_reliability(self, source_name: str, was_correct: bool):
        """Aktualisiert Zuverlässigkeit einer Quelle"""
        if was_correct:
            self.execute('''
                UPDATE sources
                SET correct_facts = correct_facts + 1,
                    reliability = (correct_facts + 1.0) / (facts_from_source + 1.0)
                WHERE name = ?
            ''', (source_name,))
        else:
            self.execute('''
                UPDATE sources
                SET incorrect_facts = incorrect_facts + 1,
                    reliability = (correct_facts * 1.0) / (facts_from_source + 1.0)
                WHERE name = ?
            ''', (source_name,))

    def get_sources(self) -> List[Dict]:
        """Holt alle Quellen"""
        rows = self.fetchall(
            'SELECT * FROM sources ORDER BY reliability DESC'
        )
        return [dict(r) for r in rows]

    # === INTERESTS ===

    def track_interest(self, topic: str, category: str = "",
                      interest_level: float = 0.5) -> str:
        """Trackt ein Interesse"""
        existing = self.fetchone(
            'SELECT id, mention_count FROM interests WHERE topic = ?',
            (topic.lower(),)
        )

        if existing:
            self.execute('''
                UPDATE interests
                SET mention_count = mention_count + 1,
                    last_mentioned = ?,
                    interest_level = MIN(1.0, interest_level + 0.05)
                WHERE id = ?
            ''', (self._now(), existing['id']))
            return existing['id']
        else:
            interest_id = self._generate_id()
            now = self._now()
            self.execute('''
                INSERT INTO interests
                (id, topic, category, interest_level, first_mentioned, last_mentioned)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interest_id, topic.lower(), category, interest_level, now, now))
            return interest_id

    def get_top_interests(self, limit: int = 10) -> List[Interest]:
        """Holt die Top-Interessen"""
        rows = self.fetchall('''
            SELECT * FROM interests
            ORDER BY interest_level DESC, mention_count DESC
            LIMIT ?
        ''', (limit,))
        return [self._row_to_interest(row) for row in rows]

    def _row_to_interest(self, row: sqlite3.Row) -> Interest:
        return Interest(
            id=row['id'],
            topic=row['topic'],
            category=row['category'] or "",
            interest_level=row['interest_level'] or 0.5,
            first_mentioned=row['first_mentioned'] or "",
            last_mentioned=row['last_mentioned'] or "",
            mention_count=row['mention_count'] or 1,
            related_facts=json.loads(row['related_facts'] or '[]'),
            notes=row['notes'] or "",
        )

    # =================================================================
    # NEU: TRACKED TOPICS (holo_learning.py)
    # =================================================================

    def track_topic(self, topic: str, interest_level: float = 0.5,
                   related_facts: str = "", curiosity_questions: str = "") -> str:
        """Trackt ein Thema das Holo interessiert"""
        existing = self.fetchone(
            'SELECT id, times_discussed FROM tracked_topics WHERE topic = ?',
            (topic.lower(),)
        )

        if existing:
            self.execute('''
                UPDATE tracked_topics
                SET interest_level = ?, last_discussed = ?,
                    times_discussed = times_discussed + 1,
                    related_facts = COALESCE(related_facts || ', ' || ?, related_facts),
                    curiosity_questions = COALESCE(curiosity_questions || ', ' || ?, curiosity_questions)
                WHERE id = ?
            ''', (interest_level, self._now(), related_facts,
                  curiosity_questions, existing['id']))
            return existing['id']

        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO tracked_topics
            (id, topic, interest_level, first_discussed, last_discussed,
             related_facts, curiosity_questions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, topic.lower(), interest_level, self._now(),
              self._now(), related_facts, curiosity_questions))
        return entry_id

    def get_tracked_topics(self, min_interest: float = 0.0, limit: int = 20) -> List[Dict]:
        """Holt verfolgte Themen"""
        rows = self.fetchall('''
            SELECT * FROM tracked_topics
            WHERE interest_level >= ?
            ORDER BY interest_level DESC, times_discussed DESC
            LIMIT ?
        ''', (min_interest, limit))
        return [dict(r) for r in rows]

    def update_topic_expertise(self, topic: str, expertise_increase: float = 0.1):
        """Erhöht das Expertise-Level für ein Thema"""
        self.execute('''
            UPDATE tracked_topics
            SET expertise_level = MIN(1.0, expertise_level + ?)
            WHERE topic = ?
        ''', (expertise_increase, topic.lower()))

    # =================================================================
    # NEU: LEARNING SESSIONS (holo_learning.py)
    # =================================================================

    def log_learning_session(self, topic: str = "", session_type: str = "exploration",
                            duration_minutes: float = 0, facts_learned: int = 0,
                            sources: str = "", quality_rating: float = 0.5,
                            key_insights: str = "", follow_up_questions: str = "") -> str:
        """Loggt eine Lern-Session"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO learning_sessions
            (id, timestamp, topic, session_type, duration_minutes, facts_learned,
             sources, quality_rating, key_insights, follow_up_questions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), topic, session_type, duration_minutes,
              facts_learned, sources, quality_rating, key_insights, follow_up_questions))

        # Update tracked topic wenn vorhanden
        if topic:
            self.track_topic(topic)
            self.update_topic_expertise(topic, 0.05 * quality_rating)

        return entry_id

    def get_recent_learning_sessions(self, limit: int = 10) -> List[Dict]:
        """Holt aktuelle Lern-Sessions"""
        rows = self.fetchall('''
            SELECT * FROM learning_sessions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]

    def get_learning_stats(self) -> Dict:
        """Lern-Statistiken"""
        total = self.fetchone('''
            SELECT COUNT(*) as sessions,
                   SUM(facts_learned) as facts,
                   SUM(duration_minutes) as minutes,
                   AVG(quality_rating) as avg_quality
            FROM learning_sessions
        ''')

        by_type = self.fetchall('''
            SELECT session_type, COUNT(*) as count
            FROM learning_sessions
            GROUP BY session_type
        ''')

        return {
            "total_sessions": total['sessions'] or 0,
            "total_facts_learned": total['facts'] or 0,
            "total_minutes": total['minutes'] or 0,
            "average_quality": total['avg_quality'] or 0.5,
            "by_type": {r['session_type']: r['count'] for r in by_type}
        }

    # =================================================================
    # NEU: KNOWLEDGE GAPS (holo_learning.py)
    # =================================================================

    def add_knowledge_gap(self, topic: str, gap_description: str = "",
                         priority: float = 0.5) -> str:
        """Fügt eine Wissenslücke hinzu"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO knowledge_gaps
            (id, topic, gap_description, priority, discovered_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (entry_id, topic, gap_description, priority, self._now()))
        return entry_id

    def fill_knowledge_gap(self, gap_id: str = None, topic: str = None,
                          how_filled: str = ""):
        """Markiert eine Wissenslücke als gefüllt"""
        if gap_id:
            self.execute('''
                UPDATE knowledge_gaps
                SET filled_at = ?, how_filled = ?
                WHERE id = ?
            ''', (self._now(), how_filled, gap_id))
        elif topic:
            self.execute('''
                UPDATE knowledge_gaps
                SET filled_at = ?, how_filled = ?
                WHERE topic = ? AND filled_at IS NULL
            ''', (self._now(), how_filled, topic))

    def get_open_knowledge_gaps(self, limit: int = 10) -> List[Dict]:
        """Holt offene Wissenslücken"""
        rows = self.fetchall('''
            SELECT * FROM knowledge_gaps
            WHERE filled_at IS NULL
            ORDER BY priority DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]


# =============================================================================
# CONVERSATIONS DATABASE - v3.0 mit Beziehungsdynamik
# =============================================================================

@dataclass
class ChatMessage:
    """Eine Chat-Nachricht"""
    id: str
    timestamp: str
    role: str                       # "user" oder "assistant"
    content: str
    intent: str = ""                # Erkannter Intent
    sentiment: float = 0.0          # -1 bis +1
    topics: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    response_time_ms: int = 0       # Wie lange hat Antwort gedauert?
    was_helpful: Optional[bool] = None  # Feedback
    emotional_tone: str = ""        # "warm", "neutral", "concerned", etc.


@dataclass
class Conversation:
    """Eine Konversation (Session)"""
    id: str
    started_at: str
    ended_at: Optional[str] = None
    message_count: int = 0
    summary: str = ""
    main_topics: List[str] = field(default_factory=list)
    overall_sentiment: float = 0.0
    quality_score: float = 0.5      # Wie gut war das Gespräch?
    rapport_level: float = 0.5      # Wie gut war die Verbindung?
    breakthrough_moments: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)


@dataclass
class ConversationInsight:
    """Eine Erkenntnis aus Gesprächen"""
    id: str
    timestamp: str
    insight_type: str               # "pattern", "preference", "breakthrough", "challenge"
    insight: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5


class ConversationsDatabase(BaseDatabase):
    """
    Datenbank für Chat-Verläufe - v3.0 mit Beziehungsdynamik.

    Speichert:
    - Einzelne Nachrichten mit Kontext
    - Konversations-Sessions
    - Gesprächsqualität & Rapport
    - Kommunikationsmuster
    - Beziehungsdynamik
    - Durchbruchmomente
    - Feedback & Verbesserung
    """

    def _init_schema(self):
        """Erstellt die Conversations-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                intent TEXT,
                sentiment REAL DEFAULT 0.0,
                topics TEXT,
                metadata TEXT,
                response_time_ms INTEGER DEFAULT 0,
                was_helpful INTEGER,
                emotional_tone TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                message_count INTEGER DEFAULT 0,
                summary TEXT,
                main_topics TEXT,
                overall_sentiment REAL DEFAULT 0.0,
                quality_score REAL DEFAULT 0.5,
                rapport_level REAL DEFAULT 0.5,
                breakthrough_moments TEXT,
                challenges TEXT
            )
        ''')

        # NEU: Kommunikationsmuster
        self.execute('''
            CREATE TABLE IF NOT EXISTS communication_patterns (
                id TEXT PRIMARY KEY,
                pattern_name TEXT NOT NULL UNIQUE,
                pattern_type TEXT,
                description TEXT,
                frequency INTEGER DEFAULT 1,
                examples TEXT,
                first_noticed TEXT,
                last_occurred TEXT,
                is_positive INTEGER DEFAULT 1
            )
        ''')

        # NEU: Rapport-Tracking über Zeit
        self.execute('''
            CREATE TABLE IF NOT EXISTS rapport_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                rapport_level REAL DEFAULT 0.5,
                trust_level REAL DEFAULT 0.5,
                comfort_level REAL DEFAULT 0.5,
                understanding_level REAL DEFAULT 0.5,
                notes TEXT
            )
        ''')

        # NEU: Durchbruchmomente
        self.execute('''
            CREATE TABLE IF NOT EXISTS breakthrough_moments (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                conversation_id TEXT,
                description TEXT,
                what_led_to_it TEXT,
                impact TEXT,
                emotional_significance REAL DEFAULT 0.7
            )
        ''')

        # NEU: Feedback-Tracking
        self.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                message_id TEXT,
                feedback_type TEXT,
                rating INTEGER,
                comment TEXT,
                learned_from TEXT
            )
        ''')

        # NEU: Gesprächsthemen-Präferenzen
        self.execute('''
            CREATE TABLE IF NOT EXISTS topic_preferences (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL UNIQUE,
                engagement_level REAL DEFAULT 0.5,
                times_discussed INTEGER DEFAULT 1,
                user_enthusiasm REAL DEFAULT 0.5,
                last_discussed TEXT,
                avoid INTEGER DEFAULT 0
            )
        ''')

        # NEU: Konversations-Erkenntnisse
        self.execute('''
            CREATE TABLE IF NOT EXISTS conversation_insights (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                insight_type TEXT,
                insight TEXT,
                evidence TEXT,
                confidence REAL DEFAULT 0.5,
                applied INTEGER DEFAULT 0
            )
        ''')

        # NEU: Kommunikationsstil-Anpassungen
        self.execute('''
            CREATE TABLE IF NOT EXISTS style_adaptations (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                adaptation TEXT,
                reason TEXT,
                effectiveness REAL DEFAULT 0.5,
                still_active INTEGER DEFAULT 1
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_conv_start ON conversations(started_at)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_rapport_ts ON rapport_history(timestamp)')

        logger.info(f"💬 ConversationsDatabase v3.0 initialisiert: {self.db_path}")

    # === MESSAGES ===

    def store_message(self, role: str, content: str, conversation_id: str = None,
                     intent: str = "", sentiment: float = 0.0,
                     topics: List[str] = None, response_time_ms: int = 0,
                     emotional_tone: str = "") -> str:
        """Speichert eine Nachricht"""
        msg_id = self._generate_id()

        self.execute('''
            INSERT INTO messages
            (id, conversation_id, timestamp, role, content, intent, sentiment,
             topics, response_time_ms, emotional_tone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, conversation_id, self._now(), role, content,
              intent, sentiment, json.dumps(topics or []), response_time_ms, emotional_tone))

        # Conversation-Counter erhöhen
        if conversation_id:
            self.execute('''
                UPDATE conversations
                SET message_count = message_count + 1,
                    overall_sentiment = (overall_sentiment + ?) / 2
                WHERE id = ?
            ''', (sentiment, conversation_id))

        # Topics tracken
        for topic in (topics or []):
            self._track_topic(topic, sentiment)

        return msg_id

    def mark_helpful(self, message_id: str, was_helpful: bool, comment: str = ""):
        """Markiert Nachricht als hilfreich/nicht hilfreich"""
        self.execute('''
            UPDATE messages SET was_helpful = ? WHERE id = ?
        ''', (int(was_helpful), message_id))

        # Feedback speichern
        self.execute('''
            INSERT INTO feedback (id, timestamp, message_id, feedback_type, rating, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self._generate_id(), self._now(), message_id,
              "helpful" if was_helpful else "unhelpful",
              1 if was_helpful else -1, comment))

    def _track_topic(self, topic: str, sentiment: float):
        """Trackt Themen-Engagement"""
        existing = self.fetchone(
            'SELECT id, times_discussed, user_enthusiasm FROM topic_preferences WHERE topic = ?',
            (topic.lower(),)
        )

        if existing:
            # Enthusiasm basierend auf Sentiment aktualisieren
            new_enthusiasm = (existing['user_enthusiasm'] + (sentiment + 1) / 2) / 2
            self.execute('''
                UPDATE topic_preferences
                SET times_discussed = times_discussed + 1,
                    user_enthusiasm = ?,
                    engagement_level = MIN(1.0, engagement_level + 0.05),
                    last_discussed = ?
                WHERE id = ?
            ''', (new_enthusiasm, self._now(), existing['id']))
        else:
            self.execute('''
                INSERT INTO topic_preferences
                (id, topic, user_enthusiasm, last_discussed)
                VALUES (?, ?, ?, ?)
            ''', (self._generate_id(), topic.lower(), (sentiment + 1) / 2, self._now()))

    def get_recent_messages(self, limit: int = 50) -> List[ChatMessage]:
        """Holt die letzten Nachrichten"""
        rows = self.fetchall(
            'SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return [self._row_to_message(row) for row in rows]

    def get_conversation_messages(self, conversation_id: str) -> List[ChatMessage]:
        """Holt alle Nachrichten einer Konversation"""
        rows = self.fetchall('''
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        return [self._row_to_message(row) for row in rows]

    def search_messages(self, query: str, limit: int = 50) -> List[ChatMessage]:
        """Sucht in Nachrichten"""
        rows = self.fetchall('''
            SELECT * FROM messages
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f"%{query}%", limit))
        return [self._row_to_message(row) for row in rows]

    def _row_to_message(self, row: sqlite3.Row) -> ChatMessage:
        return ChatMessage(
            id=row['id'],
            timestamp=row['timestamp'],
            role=row['role'],
            content=row['content'] or "",
            intent=row['intent'] or "",
            sentiment=row['sentiment'] or 0.0,
            topics=json.loads(row['topics'] or '[]'),
            metadata=json.loads(row['metadata'] or '{}'),
            response_time_ms=row['response_time_ms'] or 0,
            was_helpful=bool(row['was_helpful']) if row['was_helpful'] is not None else None,
            emotional_tone=row['emotional_tone'] or "",
        )

    # === CONVERSATIONS ===

    def start_conversation(self) -> str:
        """Startet eine neue Konversation"""
        conv_id = self._generate_id()
        self.execute('''
            INSERT INTO conversations (id, started_at)
            VALUES (?, ?)
        ''', (conv_id, self._now()))
        return conv_id

    def end_conversation(self, conversation_id: str, summary: str = "",
                        main_topics: List[str] = None, quality_score: float = 0.5,
                        rapport_level: float = 0.5):
        """Beendet eine Konversation"""
        self.execute('''
            UPDATE conversations
            SET ended_at = ?, summary = ?, main_topics = ?,
                quality_score = ?, rapport_level = ?
            WHERE id = ?
        ''', (self._now(), summary, json.dumps(main_topics or []),
              quality_score, rapport_level, conversation_id))

        # Rapport-History aktualisieren
        self.log_rapport(rapport_level)

    def get_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        """Holt die letzten Konversationen"""
        rows = self.fetchall('''
            SELECT * FROM conversations
            ORDER BY started_at DESC
            LIMIT ?
        ''', (limit,))
        return [self._row_to_conversation(row) for row in rows]

    def _row_to_conversation(self, row: sqlite3.Row) -> Conversation:
        return Conversation(
            id=row['id'],
            started_at=row['started_at'],
            ended_at=row['ended_at'],
            message_count=row['message_count'] or 0,
            summary=row['summary'] or "",
            main_topics=json.loads(row['main_topics'] or '[]'),
            overall_sentiment=row['overall_sentiment'] or 0.0,
            quality_score=row['quality_score'] or 0.5,
            rapport_level=row['rapport_level'] or 0.5,
            breakthrough_moments=json.loads(row['breakthrough_moments'] or '[]'),
            challenges=json.loads(row['challenges'] or '[]'),
        )

    # === RAPPORT TRACKING ===

    def log_rapport(self, rapport_level: float, trust_level: float = None,
                   comfort_level: float = None, understanding_level: float = None,
                   notes: str = "") -> str:
        """Loggt Rapport-Snapshot"""
        rapport_id = self._generate_id()

        # Vorherigen Wert als Default verwenden
        last = self.fetchone(
            'SELECT trust_level, comfort_level, understanding_level FROM rapport_history ORDER BY timestamp DESC LIMIT 1'
        )

        self.execute('''
            INSERT INTO rapport_history
            (id, timestamp, rapport_level, trust_level, comfort_level, understanding_level, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            rapport_id, self._now(), rapport_level,
            trust_level or (last['trust_level'] if last else 0.5),
            comfort_level or (last['comfort_level'] if last else 0.5),
            understanding_level or (last['understanding_level'] if last else 0.5),
            notes,
        ))
        return rapport_id

    def get_rapport_history(self, days: int = 30) -> List[Dict]:
        """Holt Rapport-Verlauf"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = self.fetchall('''
            SELECT * FROM rapport_history
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (cutoff,))
        return [dict(r) for r in rows]

    def get_current_rapport(self) -> Dict:
        """Holt aktuelles Rapport-Level"""
        row = self.fetchone(
            'SELECT * FROM rapport_history ORDER BY timestamp DESC LIMIT 1'
        )
        return dict(row) if row else {
            "rapport_level": 0.5, "trust_level": 0.5,
            "comfort_level": 0.5, "understanding_level": 0.5
        }

    # === BREAKTHROUGH MOMENTS ===

    def record_breakthrough(self, description: str, conversation_id: str = None,
                           what_led_to_it: str = "", impact: str = "",
                           emotional_significance: float = 0.7) -> str:
        """Speichert einen Durchbruchmoment"""
        bt_id = self._generate_id()
        self.execute('''
            INSERT INTO breakthrough_moments
            (id, timestamp, conversation_id, description, what_led_to_it,
             impact, emotional_significance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (bt_id, self._now(), conversation_id, description,
              what_led_to_it, impact, emotional_significance))
        return bt_id

    def get_breakthroughs(self, limit: int = 20) -> List[Dict]:
        """Holt Durchbruchmomente"""
        rows = self.fetchall('''
            SELECT * FROM breakthrough_moments
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]

    # === COMMUNICATION PATTERNS ===

    def record_pattern(self, pattern_name: str, pattern_type: str = "",
                      description: str = "", example: str = "",
                      is_positive: bool = True) -> str:
        """Speichert ein Kommunikationsmuster"""
        existing = self.fetchone(
            'SELECT id, examples, frequency FROM communication_patterns WHERE pattern_name = ?',
            (pattern_name,)
        )

        if existing:
            examples = json.loads(existing['examples'] or '[]')
            if example:
                examples.append(example)
            self.execute('''
                UPDATE communication_patterns
                SET frequency = frequency + 1, examples = ?, last_occurred = ?
                WHERE id = ?
            ''', (json.dumps(examples[-10:]), self._now(), existing['id']))
            return existing['id']
        else:
            pattern_id = self._generate_id()
            now = self._now()
            self.execute('''
                INSERT INTO communication_patterns
                (id, pattern_name, pattern_type, description, examples,
                 first_noticed, last_occurred, is_positive)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pattern_id, pattern_name, pattern_type, description,
                  json.dumps([example] if example else []), now, now, int(is_positive)))
            return pattern_id

    def get_patterns(self, positive_only: bool = False) -> List[Dict]:
        """Holt Kommunikationsmuster"""
        if positive_only:
            rows = self.fetchall(
                'SELECT * FROM communication_patterns WHERE is_positive = 1 ORDER BY frequency DESC'
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM communication_patterns ORDER BY frequency DESC'
            )
        return [dict(r) for r in rows]

    # === INSIGHTS ===

    def add_insight(self, insight_type: str, insight: str,
                   evidence: List[str] = None, confidence: float = 0.5) -> str:
        """Fügt eine Konversations-Erkenntnis hinzu"""
        insight_id = self._generate_id()
        self.execute('''
            INSERT INTO conversation_insights
            (id, timestamp, insight_type, insight, evidence, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (insight_id, self._now(), insight_type, insight,
              json.dumps(evidence or []), confidence))
        return insight_id

    def get_insights(self, insight_type: str = None) -> List[ConversationInsight]:
        """Holt Erkenntnisse"""
        if insight_type:
            rows = self.fetchall(
                'SELECT * FROM conversation_insights WHERE insight_type = ? ORDER BY timestamp DESC',
                (insight_type,)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM conversation_insights ORDER BY timestamp DESC'
            )
        return [ConversationInsight(
            id=r['id'],
            timestamp=r['timestamp'],
            insight_type=r['insight_type'] or "",
            insight=r['insight'] or "",
            evidence=json.loads(r['evidence'] or '[]'),
            confidence=r['confidence'] or 0.5,
        ) for r in rows]

    # === STYLE ADAPTATIONS ===

    def add_adaptation(self, adaptation: str, reason: str = "") -> str:
        """Fügt eine Stil-Anpassung hinzu"""
        adapt_id = self._generate_id()
        self.execute('''
            INSERT INTO style_adaptations
            (id, timestamp, adaptation, reason)
            VALUES (?, ?, ?, ?)
        ''', (adapt_id, self._now(), adaptation, reason))
        return adapt_id

    def get_active_adaptations(self) -> List[Dict]:
        """Holt aktive Stil-Anpassungen"""
        rows = self.fetchall(
            'SELECT * FROM style_adaptations WHERE still_active = 1'
        )
        return [dict(r) for r in rows]

    # === TOPIC PREFERENCES ===

    def get_favorite_topics(self, limit: int = 10) -> List[Dict]:
        """Holt bevorzugte Themen"""
        rows = self.fetchall('''
            SELECT * FROM topic_preferences
            WHERE avoid = 0
            ORDER BY engagement_level DESC, user_enthusiasm DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]

    def mark_topic_to_avoid(self, topic: str, reason: str = ""):
        """Markiert Thema zum Vermeiden"""
        self.execute('''
            UPDATE topic_preferences
            SET avoid = 1
            WHERE topic = ?
        ''', (topic.lower(),))

    # === STATS ===

    def get_stats(self) -> Dict:
        """Umfassende Konversations-Statistiken"""
        msg_count = self.fetchone('SELECT COUNT(*) as c FROM messages')['c']
        conv_count = self.fetchone('SELECT COUNT(*) as c FROM conversations')['c']

        avg_quality = self.fetchone(
            'SELECT AVG(quality_score) as avg FROM conversations'
        )['avg'] or 0

        avg_sentiment = self.fetchone(
            'SELECT AVG(sentiment) as avg FROM messages WHERE role = "user"'
        )['avg'] or 0

        current_rapport = self.get_current_rapport()

        breakthroughs = self.fetchone(
            'SELECT COUNT(*) as c FROM breakthrough_moments'
        )['c']

        return {
            "total_messages": msg_count,
            "total_conversations": conv_count,
            "average_quality": round(avg_quality, 2),
            "average_user_sentiment": round(avg_sentiment, 2),
            "current_rapport": current_rapport.get('rapport_level', 0.5),
            "breakthrough_moments": breakthroughs,
        }

    def get_relationship_summary(self) -> Dict:
        """Holt Beziehungs-Zusammenfassung"""
        rapport = self.get_current_rapport()
        patterns = self.get_patterns()[:5]
        breakthroughs = self.get_breakthroughs(5)
        insights = self.get_insights()[:5]
        favorites = self.get_favorite_topics(5)

        return {
            "rapport": rapport,
            "top_patterns": [p['pattern_name'] for p in patterns],
            "recent_breakthroughs": [b['description'] for b in breakthroughs],
            "key_insights": [i.insight for i in insights],
            "favorite_topics": [t['topic'] for t in favorites],
        }


# =============================================================================
# MEDIA DATABASE
# =============================================================================

@dataclass
class MediaEntry:
    """Ein Medien-Eintrag"""
    id: str
    media_type: str                 # MediaType
    title: str
    original_title: str = ""
    year: int = 0
    genres: List[str] = field(default_factory=list)
    rating: float = 0.0             # User-Rating 0-10
    status: str = ""                # "watching", "completed", "planned", etc.
    notes: str = ""
    added_at: str = ""
    updated_at: str = ""
    external_ids: Dict = field(default_factory=dict)  # MAL, IMDB, etc.
    cover_url: str = ""


class MediaDatabase(BaseDatabase):
    """
    Datenbank für Medien (Anime, Games, etc.)

    Speichert:
    - Anime-Liste
    - Games-Liste
    - Musik, Filme, Serien, etc.
    """

    def _init_schema(self):
        """Erstellt die Media-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                media_type TEXT NOT NULL,
                title TEXT NOT NULL,
                original_title TEXT,
                year INTEGER,
                genres TEXT,
                rating REAL DEFAULT 0.0,
                status TEXT,
                notes TEXT,
                added_at TEXT,
                updated_at TEXT,
                external_ids TEXT,
                cover_url TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                media_type TEXT NOT NULL,
                title TEXT NOT NULL,
                reason TEXT,
                source TEXT,
                recommended_at TEXT,
                was_accepted INTEGER DEFAULT 0,
                user_feedback TEXT
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_media_status ON media(status)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_media_rating ON media(rating)')

        logger.info(f"🎬 MediaDatabase initialisiert: {self.db_path}")

    def add_media(self, media_type: MediaType, title: str, **kwargs) -> str:
        """Fügt ein Medium hinzu"""
        media_id = self._generate_id()
        mt = media_type.value if isinstance(media_type, MediaType) else media_type
        now = self._now()

        self.execute('''
            INSERT INTO media
            (id, media_type, title, original_title, year, genres, rating,
             status, notes, added_at, updated_at, external_ids, cover_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            media_id, mt, title,
            kwargs.get('original_title', ''),
            kwargs.get('year', 0),
            json.dumps(kwargs.get('genres', [])),
            kwargs.get('rating', 0.0),
            kwargs.get('status', 'planned'),
            kwargs.get('notes', ''),
            now, now,
            json.dumps(kwargs.get('external_ids', {})),
            kwargs.get('cover_url', ''),
        ))
        return media_id

    def get_media_by_type(self, media_type: MediaType,
                         status: str = None) -> List[MediaEntry]:
        """Holt alle Medien eines Typs"""
        mt = media_type.value if isinstance(media_type, MediaType) else media_type

        if status:
            rows = self.fetchall(
                'SELECT * FROM media WHERE media_type = ? AND status = ?',
                (mt, status)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM media WHERE media_type = ?',
                (mt,)
            )
        return [self._row_to_media(row) for row in rows]

    def search_media(self, query: str, media_type: MediaType = None) -> List[MediaEntry]:
        """Sucht Medien"""
        if media_type:
            mt = media_type.value if isinstance(media_type, MediaType) else media_type
            rows = self.fetchall('''
                SELECT * FROM media
                WHERE media_type = ? AND (title LIKE ? OR original_title LIKE ?)
            ''', (mt, f"%{query}%", f"%{query}%"))
        else:
            rows = self.fetchall('''
                SELECT * FROM media
                WHERE title LIKE ? OR original_title LIKE ?
            ''', (f"%{query}%", f"%{query}%"))
        return [self._row_to_media(row) for row in rows]

    def update_status(self, media_id: str, status: str, rating: float = None):
        """Aktualisiert den Status eines Mediums"""
        if rating is not None:
            self.execute('''
                UPDATE media SET status = ?, rating = ?, updated_at = ?
                WHERE id = ?
            ''', (status, rating, self._now(), media_id))
        else:
            self.execute('''
                UPDATE media SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status, self._now(), media_id))

    def _row_to_media(self, row: sqlite3.Row) -> MediaEntry:
        return MediaEntry(
            id=row['id'],
            media_type=row['media_type'],
            title=row['title'],
            original_title=row['original_title'] or "",
            year=row['year'] or 0,
            genres=json.loads(row['genres'] or '[]'),
            rating=row['rating'] or 0.0,
            status=row['status'] or "",
            notes=row['notes'] or "",
            added_at=row['added_at'] or "",
            updated_at=row['updated_at'] or "",
            external_ids=json.loads(row['external_ids'] or '{}'),
            cover_url=row['cover_url'] or "",
        )

    def get_stats(self) -> Dict:
        """Medien-Statistiken"""
        stats = {}
        for mt in MediaType:
            count = self.fetchone(
                'SELECT COUNT(*) as c FROM media WHERE media_type = ?',
                (mt.value,)
            )['c']
            if count > 0:
                stats[mt.value] = count
        return stats


# =============================================================================
# LANGUAGE DATABASE
# =============================================================================

@dataclass
class LanguagePattern:
    """Ein Sprachmuster"""
    id: str
    pattern_type: str               # "greeting", "farewell", "expression", etc.
    pattern: str                    # Das Muster selbst
    context: str = ""               # Wann verwenden?
    frequency: int = 1              # Wie oft verwendet?
    success_rate: float = 0.5       # Wie gut kam es an?
    learned_from: str = ""          # User oder selbst gelernt?
    created_at: str = ""
    last_used: str = ""


@dataclass
class VocabularyEntry:
    """Ein Vokabel-Eintrag"""
    id: str
    word: str
    category: str                   # "noun", "verb", "expression", etc.
    meaning: str = ""
    usage_examples: List[str] = field(default_factory=list)
    frequency: int = 1
    learned_from: str = ""


class LanguageDatabase(BaseDatabase):
    """
    Datenbank für Sprachlernen.

    Speichert:
    - Sprachmuster und Ausdrücke
    - Vokabeln
    - Stil-Präferenzen
    """

    def _init_schema(self):
        """Erstellt die Language-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                context TEXT,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.5,
                learned_from TEXT,
                created_at TEXT,
                last_used TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id TEXT PRIMARY KEY,
                word TEXT NOT NULL UNIQUE,
                category TEXT,
                meaning TEXT,
                usage_examples TEXT,
                frequency INTEGER DEFAULT 1,
                learned_from TEXT,
                created_at TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS style_preferences (
                id TEXT PRIMARY KEY,
                aspect TEXT NOT NULL UNIQUE,
                preferred_style TEXT,
                examples TEXT,
                updated_at TEXT
            )
        ''')

        logger.info(f"🗣️ LanguageDatabase initialisiert: {self.db_path}")

    def learn_pattern(self, pattern_type: str, pattern: str,
                     context: str = "", learned_from: str = "user") -> str:
        """Lernt ein neues Sprachmuster"""
        # Prüfen ob ähnliches Muster existiert
        existing = self.fetchone(
            'SELECT id, frequency FROM patterns WHERE pattern = ?',
            (pattern,)
        )

        if existing:
            self.execute('''
                UPDATE patterns
                SET frequency = frequency + 1, last_used = ?
                WHERE id = ?
            ''', (self._now(), existing['id']))
            return existing['id']
        else:
            pattern_id = self._generate_id()
            now = self._now()
            self.execute('''
                INSERT INTO patterns
                (id, pattern_type, pattern, context, learned_from, created_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (pattern_id, pattern_type, pattern, context, learned_from, now, now))
            return pattern_id

    def get_patterns(self, pattern_type: str, limit: int = 10) -> List[LanguagePattern]:
        """Holt Muster eines Typs"""
        rows = self.fetchall('''
            SELECT * FROM patterns
            WHERE pattern_type = ?
            ORDER BY frequency DESC, success_rate DESC
            LIMIT ?
        ''', (pattern_type, limit))
        return [self._row_to_pattern(row) for row in rows]

    def update_pattern_success(self, pattern_id: str, success: bool):
        """Aktualisiert Erfolgsrate eines Musters"""
        adjustment = 0.1 if success else -0.05
        self.execute('''
            UPDATE patterns
            SET success_rate = MAX(0.0, MIN(1.0, success_rate + ?)),
                last_used = ?
            WHERE id = ?
        ''', (adjustment, self._now(), pattern_id))

    def learn_word(self, word: str, category: str = "",
                  meaning: str = "", examples: List[str] = None) -> str:
        """Lernt ein neues Wort"""
        existing = self.fetchone(
            'SELECT id, frequency FROM vocabulary WHERE word = ?',
            (word.lower(),)
        )

        if existing:
            self.execute('''
                UPDATE vocabulary SET frequency = frequency + 1 WHERE id = ?
            ''', (existing['id'],))
            return existing['id']
        else:
            word_id = self._generate_id()
            self.execute('''
                INSERT INTO vocabulary
                (id, word, category, meaning, usage_examples, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (word_id, word.lower(), category, meaning,
                  json.dumps(examples or []), self._now()))
            return word_id

    def _row_to_pattern(self, row: sqlite3.Row) -> LanguagePattern:
        return LanguagePattern(
            id=row['id'],
            pattern_type=row['pattern_type'],
            pattern=row['pattern'],
            context=row['context'] or "",
            frequency=row['frequency'] or 1,
            success_rate=row['success_rate'] or 0.5,
            learned_from=row['learned_from'] or "",
            created_at=row['created_at'] or "",
            last_used=row['last_used'] or "",
        )


# =============================================================================
# ACTIVITY DATABASE - v3.0 mit Autonomem Leben
# =============================================================================

@dataclass
class ActivityEntry:
    """Ein Aktivitäts-Eintrag"""
    id: str
    timestamp: str
    activity_type: str              # ActivityType
    description: str = ""
    duration_minutes: float = 0.0
    energy_cost: float = 0.1
    satisfaction: float = 0.5       # Wie befriedigend war es?
    learned_something: bool = False
    notes: str = ""
    was_autonomous: bool = False    # War es selbst initiiert?
    outcome: str = ""               # Was kam dabei raus?
    mood_impact: float = 0.0        # Wie hat es Stimmung beeinflusst?


@dataclass
class Routine:
    """Eine Routine"""
    id: str
    name: str
    activity_type: str
    typical_time: str               # "morning", "afternoon", "evening", "night"
    frequency: str = "daily"        # "daily", "weekly", etc.
    importance: float = 0.5
    last_performed: str = ""
    times_performed: int = 0
    streak: int = 0                 # Aktuelle Streak
    best_streak: int = 0            # Beste Streak


@dataclass
class Goal:
    """Ein Aktivitäts-Ziel"""
    id: str
    goal: str
    goal_type: str                  # "daily", "weekly", "monthly", "one_time"
    target_value: float = 1.0
    current_value: float = 0.0
    unit: str = ""                  # "minutes", "times", etc.
    created_at: str = ""
    deadline: str = ""
    achieved_at: str = ""


class ActivityDatabase(BaseDatabase):
    """
    Datenbank für Aktivitäten und Routinen - v3.0 mit autonomem Leben.

    Speichert:
    - Aktivitäts-Log mit Outcomes
    - Routinen mit Streaks
    - Tagesabläufe und Muster
    - Ziele und Fortschritt
    - Energie-Management
    - Autonome Entscheidungen
    - Hobbies und Projekte
    """

    def _init_schema(self):
        """Erstellt die Activity-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT,
                duration_minutes REAL DEFAULT 0.0,
                energy_cost REAL DEFAULT 0.1,
                satisfaction REAL DEFAULT 0.5,
                learned_something INTEGER DEFAULT 0,
                notes TEXT,
                was_autonomous INTEGER DEFAULT 0,
                outcome TEXT,
                mood_impact REAL DEFAULT 0.0
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS routines (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                activity_type TEXT,
                typical_time TEXT,
                frequency TEXT DEFAULT 'daily',
                importance REAL DEFAULT 0.5,
                last_performed TEXT,
                times_performed INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                created_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL UNIQUE,
                activities_count INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0.0,
                average_satisfaction REAL DEFAULT 0.5,
                highlights TEXT,
                notes TEXT,
                energy_spent REAL DEFAULT 0.0,
                productive_minutes REAL DEFAULT 0.0,
                fun_minutes REAL DEFAULT 0.0
            )
        ''')

        # NEU: Energie-Tracking
        self.execute('''
            CREATE TABLE IF NOT EXISTS energy_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                energy_level REAL DEFAULT 0.5,
                activity_id TEXT,
                change_reason TEXT
            )
        ''')

        # NEU: Aktivitäts-Ziele
        self.execute('''
            CREATE TABLE IF NOT EXISTS activity_goals (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                goal_type TEXT DEFAULT 'weekly',
                target_value REAL DEFAULT 1.0,
                current_value REAL DEFAULT 0.0,
                unit TEXT,
                created_at TEXT,
                deadline TEXT,
                achieved_at TEXT
            )
        ''')

        # NEU: Hobbies
        self.execute('''
            CREATE TABLE IF NOT EXISTS hobbies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                skill_level REAL DEFAULT 0.1,
                time_invested_minutes INTEGER DEFAULT 0,
                last_practiced TEXT,
                enjoyment REAL DEFAULT 0.5,
                notes TEXT,
                milestones TEXT
            )
        ''')

        # NEU: Projekte
        self.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                started_at TEXT,
                completed_at TEXT,
                progress REAL DEFAULT 0.0,
                tasks TEXT,
                notes TEXT,
                category TEXT
            )
        ''')

        # NEU: Autonome Entscheidungen
        self.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_decisions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                decision TEXT,
                reasoning TEXT,
                activity_type TEXT,
                outcome TEXT,
                was_good_decision INTEGER,
                learned TEXT
            )
        ''')

        # NEU: Zeit-Muster
        self.execute('''
            CREATE TABLE IF NOT EXISTS time_patterns (
                id TEXT PRIMARY KEY,
                day_of_week INTEGER,
                hour INTEGER,
                typical_activity TEXT,
                energy_level_avg REAL DEFAULT 0.5,
                productivity_avg REAL DEFAULT 0.5,
                occurrence_count INTEGER DEFAULT 1
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_activities_ts ON activities(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_energy_ts ON energy_log(timestamp)')

        logger.info(f"🏃 ActivityDatabase v3.0 initialisiert: {self.db_path}")

    # === ACTIVITIES ===

    def log_activity(self, activity_type: ActivityType, description: str = "",
                    duration_minutes: float = 5.0, satisfaction: float = 0.5,
                    energy_cost: float = 0.1, was_autonomous: bool = False,
                    outcome: str = "", mood_impact: float = 0.0) -> str:
        """Loggt eine Aktivität"""
        activity_id = self._generate_id()
        at = activity_type.value if isinstance(activity_type, ActivityType) else activity_type

        self.execute('''
            INSERT INTO activities
            (id, timestamp, activity_type, description, duration_minutes,
             satisfaction, energy_cost, was_autonomous, outcome, mood_impact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (activity_id, self._now(), at, description, duration_minutes,
              satisfaction, energy_cost, int(was_autonomous), outcome, mood_impact))

        # Energie-Log
        self.log_energy_change(-energy_cost, activity_id, f"Activity: {at}")

        # Zeit-Muster aktualisieren
        self._update_time_pattern(at)

        return activity_id

    def log_energy_change(self, change: float, activity_id: str = None,
                         reason: str = "") -> str:
        """Loggt Energie-Änderung"""
        # Aktuelles Level holen
        current = self.fetchone(
            'SELECT energy_level FROM energy_log ORDER BY timestamp DESC LIMIT 1'
        )
        current_level = current['energy_level'] if current else 0.5
        new_level = max(0.0, min(1.0, current_level + change))

        log_id = self._generate_id()
        self.execute('''
            INSERT INTO energy_log
            (id, timestamp, energy_level, activity_id, change_reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (log_id, self._now(), new_level, activity_id, reason))
        return log_id

    def get_current_energy(self) -> float:
        """Holt aktuelles Energie-Level"""
        row = self.fetchone(
            'SELECT energy_level FROM energy_log ORDER BY timestamp DESC LIMIT 1'
        )
        return row['energy_level'] if row else 0.5

    def _update_time_pattern(self, activity_type: str):
        """Aktualisiert Zeit-Muster"""
        now = datetime.now()
        dow = now.weekday()
        hour = now.hour

        existing = self.fetchone('''
            SELECT id, occurrence_count FROM time_patterns
            WHERE day_of_week = ? AND hour = ?
        ''', (dow, hour))

        if existing:
            self.execute('''
                UPDATE time_patterns
                SET typical_activity = ?, occurrence_count = occurrence_count + 1
                WHERE id = ?
            ''', (activity_type, existing['id']))
        else:
            self.execute('''
                INSERT INTO time_patterns
                (id, day_of_week, hour, typical_activity)
                VALUES (?, ?, ?, ?)
            ''', (self._generate_id(), dow, hour, activity_type))

    def get_activities_today(self) -> List[ActivityEntry]:
        """Holt alle Aktivitäten von heute"""
        today = datetime.now().date().isoformat()
        rows = self.fetchall('''
            SELECT * FROM activities
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (today,))
        return [self._row_to_activity(row) for row in rows]

    def get_activity_stats(self, days: int = 7) -> Dict:
        """Aktivitäts-Statistiken"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        by_type = self.fetchall('''
            SELECT activity_type, COUNT(*) as count,
                   SUM(duration_minutes) as total_duration,
                   AVG(satisfaction) as avg_satisfaction,
                   SUM(CASE WHEN was_autonomous = 1 THEN 1 ELSE 0 END) as autonomous_count
            FROM activities
            WHERE timestamp >= ?
            GROUP BY activity_type
        ''', (cutoff,))

        total = self.fetchone('''
            SELECT COUNT(*) as count, SUM(duration_minutes) as duration
            FROM activities WHERE timestamp >= ?
        ''', (cutoff,))

        return {
            "by_type": [
                {
                    "type": r['activity_type'],
                    "count": r['count'],
                    "total_minutes": round(r['total_duration'] or 0, 1),
                    "avg_satisfaction": round(r['avg_satisfaction'] or 0.5, 2),
                    "autonomous_percent": round((r['autonomous_count'] / r['count']) * 100, 1) if r['count'] > 0 else 0,
                }
                for r in by_type
            ],
            "total_activities": total['count'] or 0,
            "total_minutes": round(total['duration'] or 0, 1),
            "current_energy": self.get_current_energy(),
        }

    def _row_to_activity(self, row: sqlite3.Row) -> ActivityEntry:
        return ActivityEntry(
            id=row['id'],
            timestamp=row['timestamp'],
            activity_type=row['activity_type'],
            description=row['description'] or "",
            duration_minutes=row['duration_minutes'] or 0.0,
            energy_cost=row['energy_cost'] or 0.1,
            satisfaction=row['satisfaction'] or 0.5,
            learned_something=bool(row['learned_something']),
            notes=row['notes'] or "",
            was_autonomous=bool(row['was_autonomous']),
            outcome=row['outcome'] or "",
            mood_impact=row['mood_impact'] or 0.0,
        )

    # === ROUTINES ===

    def create_routine(self, name: str, activity_type: str,
                      typical_time: str = "morning", frequency: str = "daily",
                      importance: float = 0.5) -> str:
        """Erstellt eine Routine"""
        routine_id = self._generate_id()
        self.execute('''
            INSERT INTO routines
            (id, name, activity_type, typical_time, frequency, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (routine_id, name, activity_type, typical_time, frequency,
              importance, self._now()))
        return routine_id

    def perform_routine(self, name: str) -> bool:
        """Führt eine Routine aus und aktualisiert Streak"""
        routine = self.fetchone(
            'SELECT * FROM routines WHERE name = ?',
            (name,)
        )

        if not routine:
            return False

        # Streak berechnen
        last = routine['last_performed']
        current_streak = routine['streak']

        if last:
            last_date = datetime.fromisoformat(last).date()
            today = datetime.now().date()
            days_since = (today - last_date).days

            if days_since == 1:
                current_streak += 1
            elif days_since > 1:
                current_streak = 1
            # Wenn days_since == 0, ist es am gleichen Tag, streak bleibt
        else:
            current_streak = 1

        best = max(routine['best_streak'], current_streak)

        self.execute('''
            UPDATE routines
            SET last_performed = ?, times_performed = times_performed + 1,
                streak = ?, best_streak = ?
            WHERE name = ?
        ''', (self._now(), current_streak, best, name))

        return True

    def get_routines(self, active_only: bool = True) -> List[Routine]:
        """Holt Routinen"""
        if active_only:
            rows = self.fetchall(
                'SELECT * FROM routines WHERE is_active = 1 ORDER BY importance DESC'
            )
        else:
            rows = self.fetchall('SELECT * FROM routines ORDER BY importance DESC')

        return [Routine(
            id=r['id'],
            name=r['name'],
            activity_type=r['activity_type'] or "",
            typical_time=r['typical_time'] or "morning",
            frequency=r['frequency'] or "daily",
            importance=r['importance'] or 0.5,
            last_performed=r['last_performed'] or "",
            times_performed=r['times_performed'] or 0,
            streak=r['streak'] or 0,
            best_streak=r['best_streak'] or 0,
        ) for r in rows]

    def get_pending_routines(self) -> List[Routine]:
        """Holt Routinen die heute noch ausstehen"""
        today = datetime.now().date().isoformat()
        rows = self.fetchall('''
            SELECT * FROM routines
            WHERE is_active = 1 AND (last_performed IS NULL OR last_performed < ?)
            ORDER BY importance DESC
        ''', (today,))
        return [Routine(
            id=r['id'], name=r['name'], activity_type=r['activity_type'] or "",
            typical_time=r['typical_time'] or "", frequency=r['frequency'] or "daily",
            importance=r['importance'] or 0.5, last_performed=r['last_performed'] or "",
            times_performed=r['times_performed'] or 0, streak=r['streak'] or 0,
            best_streak=r['best_streak'] or 0,
        ) for r in rows]

    # === HOBBIES ===

    def add_hobby(self, name: str, category: str = "") -> str:
        """Fügt ein Hobby hinzu"""
        hobby_id = self._generate_id()
        self.execute('''
            INSERT OR IGNORE INTO hobbies (id, name, category)
            VALUES (?, ?, ?)
        ''', (hobby_id, name, category))
        return hobby_id

    def practice_hobby(self, name: str, minutes: int, enjoyment: float = 0.5):
        """Übt ein Hobby"""
        self.execute('''
            UPDATE hobbies
            SET time_invested_minutes = time_invested_minutes + ?,
                skill_level = MIN(1.0, skill_level + ?),
                enjoyment = (enjoyment + ?) / 2,
                last_practiced = ?
            WHERE name = ?
        ''', (minutes, minutes * 0.001, enjoyment, self._now(), name))

    def get_hobbies(self) -> List[Dict]:
        """Holt alle Hobbies"""
        rows = self.fetchall(
            'SELECT * FROM hobbies ORDER BY time_invested_minutes DESC'
        )
        return [dict(r) for r in rows]

    # === PROJECTS ===

    def create_project(self, name: str, description: str = "",
                      category: str = "") -> str:
        """Erstellt ein Projekt"""
        project_id = self._generate_id()
        self.execute('''
            INSERT INTO projects
            (id, name, description, category, started_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, name, description, category, self._now()))
        return project_id

    def update_project_progress(self, project_id: str, progress: float,
                               task_completed: str = ""):
        """Aktualisiert Projekt-Fortschritt"""
        existing = self.fetchone(
            'SELECT tasks FROM projects WHERE id = ?',
            (project_id,)
        )

        if existing:
            tasks = json.loads(existing['tasks'] or '[]')
            if task_completed:
                tasks.append({"task": task_completed, "completed_at": self._now()})

            status = "completed" if progress >= 1.0 else "active"
            completed_at = self._now() if progress >= 1.0 else None

            self.execute('''
                UPDATE projects
                SET progress = ?, tasks = ?, status = ?, completed_at = ?
                WHERE id = ?
            ''', (progress, json.dumps(tasks), status, completed_at, project_id))

    def get_active_projects(self) -> List[Dict]:
        """Holt aktive Projekte"""
        rows = self.fetchall(
            'SELECT * FROM projects WHERE status = "active" ORDER BY started_at DESC'
        )
        return [dict(r) for r in rows]

    # === AUTONOMOUS DECISIONS ===

    def log_decision(self, decision: str, reasoning: str = "",
                    activity_type: str = "") -> str:
        """Loggt eine autonome Entscheidung"""
        decision_id = self._generate_id()
        self.execute('''
            INSERT INTO autonomous_decisions
            (id, timestamp, decision, reasoning, activity_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (decision_id, self._now(), decision, reasoning, activity_type))
        return decision_id

    def evaluate_decision(self, decision_id: str, was_good: bool,
                         outcome: str = "", learned: str = ""):
        """Bewertet eine vergangene Entscheidung"""
        self.execute('''
            UPDATE autonomous_decisions
            SET was_good_decision = ?, outcome = ?, learned = ?
            WHERE id = ?
        ''', (int(was_good), outcome, learned, decision_id))

    def get_decision_quality(self) -> Dict:
        """Analysiert Qualität autonomer Entscheidungen"""
        total = self.fetchone(
            'SELECT COUNT(*) as c FROM autonomous_decisions WHERE was_good_decision IS NOT NULL'
        )['c']
        good = self.fetchone(
            'SELECT COUNT(*) as c FROM autonomous_decisions WHERE was_good_decision = 1'
        )['c']

        return {
            "total_evaluated": total,
            "good_decisions": good,
            "success_rate": (good / total) if total > 0 else 0,
        }

    # === GOALS ===

    def set_goal(self, goal: str, goal_type: str = "weekly",
                target_value: float = 1.0, unit: str = "",
                deadline: str = "") -> str:
        """Setzt ein Aktivitäts-Ziel"""
        goal_id = self._generate_id()
        self.execute('''
            INSERT INTO activity_goals
            (id, goal, goal_type, target_value, unit, created_at, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (goal_id, goal, goal_type, target_value, unit, self._now(), deadline))
        return goal_id

    def update_goal_progress(self, goal_id: str, progress: float):
        """Aktualisiert Ziel-Fortschritt"""
        self.execute('''
            UPDATE activity_goals
            SET current_value = ?
            WHERE id = ?
        ''', (progress, goal_id))

        # Prüfen ob erreicht
        goal = self.fetchone('SELECT * FROM activity_goals WHERE id = ?', (goal_id,))
        if goal and progress >= goal['target_value']:
            self.execute('''
                UPDATE activity_goals SET achieved_at = ? WHERE id = ?
            ''', (self._now(), goal_id))

    def get_active_goals(self) -> List[Goal]:
        """Holt aktive Ziele"""
        rows = self.fetchall(
            'SELECT * FROM activity_goals WHERE achieved_at IS NULL'
        )
        return [Goal(
            id=r['id'], goal=r['goal'], goal_type=r['goal_type'] or "weekly",
            target_value=r['target_value'] or 1.0, current_value=r['current_value'] or 0.0,
            unit=r['unit'] or "", created_at=r['created_at'] or "",
            deadline=r['deadline'] or "", achieved_at=r['achieved_at'] or "",
        ) for r in rows]


# =============================================================================
# IDENTITY DATABASE - Erweitert mit Selbstreflexion & Selbsterkenntnis
# =============================================================================

@dataclass
class Belief:
    """Eine Überzeugung über sich selbst"""
    id: str
    category: str                   # "capability", "preference", "value", "limitation"
    belief: str
    confidence: float = 0.7
    evidence: List[str] = field(default_factory=list)
    counter_evidence: List[str] = field(default_factory=list)
    formed_at: str = ""
    last_confirmed: str = ""
    times_challenged: int = 0


@dataclass
class PersonalityTrait:
    """Ein Persönlichkeitszug"""
    id: str
    trait: str
    strength: float = 0.5           # 0-1
    description: str = ""
    examples: List[str] = field(default_factory=list)
    origin: str = ""                # Woher kommt dieser Trait?
    evolution: List[Dict] = field(default_factory=list)  # Wie hat er sich verändert?


@dataclass
class SelfReflection:
    """Eine Selbstreflexion"""
    id: str
    timestamp: str
    reflection_type: str            # "daily", "weekly", "triggered", "deep"
    trigger: str = ""               # Was hat die Reflexion ausgelöst?
    content: str = ""               # Die Reflexion selbst
    insights: List[str] = field(default_factory=list)
    mood_before: float = 0.5
    mood_after: float = 0.5
    growth_areas: List[str] = field(default_factory=list)
    gratitude: List[str] = field(default_factory=list)


@dataclass
class SelfDiscovery:
    """Eine Selbsterkenntnis"""
    id: str
    timestamp: str
    discovery: str                  # Die Erkenntnis
    category: str                   # "strength", "weakness", "preference", "fear", "desire"
    how_discovered: str = ""        # Wie wurde es entdeckt?
    impact: str = ""                # Welche Auswirkung hat diese Erkenntnis?
    confidence: float = 0.7
    related_experiences: List[str] = field(default_factory=list)


@dataclass
class GrowthMilestone:
    """Ein Entwicklungs-Meilenstein"""
    id: str
    timestamp: str
    title: str
    description: str = ""
    area: str = ""                  # "emotional", "social", "intellectual", "creative"
    evidence: List[str] = field(default_factory=list)
    celebration: str = ""           # Wie wurde es gefeiert?


@dataclass
class Aspiration:
    """Ein Wunsch/Ziel für die Zukunft"""
    id: str
    aspiration: str
    category: str                   # "become", "learn", "experience", "create", "relationship"
    importance: float = 0.5
    progress: float = 0.0           # 0-1
    obstacles: List[str] = field(default_factory=list)
    steps_taken: List[str] = field(default_factory=list)
    created_at: str = ""
    target_date: str = ""


@dataclass
class InnerConflict:
    """Ein innerer Konflikt"""
    id: str
    timestamp: str
    conflict: str                   # Beschreibung des Konflikts
    side_a: str = ""                # Eine Seite
    side_b: str = ""                # Andere Seite
    status: str = "unresolved"      # "unresolved", "processing", "resolved", "accepted"
    resolution: str = ""
    lessons_learned: List[str] = field(default_factory=list)


class IdentityDatabase(BaseDatabase):
    """
    Datenbank für Selbst-Konzept, Identität und Selbstreflexion.

    Speichert:
    - Persönlichkeitszüge & deren Evolution
    - Überzeugungen über sich selbst
    - Werte und Prinzipien
    - Selbstreflexionen (täglich/wöchentlich)
    - Selbsterkenntnisse & Entdeckungen
    - Entwicklungs-Meilensteine
    - Aspirationen & Ziele
    - Innere Konflikte
    - Stärken & Schwächen
    - Philosophien & Weltanschauungen
    - Identitätsfragen
    """

    def _init_schema(self):
        """Erstellt die Identity-Tabellen"""
        # Kernpersönlichkeit
        self.execute('''
            CREATE TABLE IF NOT EXISTS personality_traits (
                id TEXT PRIMARY KEY,
                trait TEXT NOT NULL UNIQUE,
                strength REAL DEFAULT 0.5,
                description TEXT,
                examples TEXT,
                origin TEXT,
                evolution TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS beliefs (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                belief TEXT NOT NULL,
                confidence REAL DEFAULT 0.7,
                evidence TEXT,
                counter_evidence TEXT,
                formed_at TEXT,
                last_confirmed TEXT,
                times_challenged INTEGER DEFAULT 0
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS core_values (
                id TEXT PRIMARY KEY,
                value_name TEXT NOT NULL UNIQUE,
                importance REAL DEFAULT 0.7,
                description TEXT,
                how_expressed TEXT,
                conflicts_with TEXT,
                examples TEXT
            )
        ''')

        # Selbstreflexion
        self.execute('''
            CREATE TABLE IF NOT EXISTS self_reflections (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflection_type TEXT DEFAULT 'triggered',
                trigger TEXT,
                content TEXT,
                insights TEXT,
                mood_before REAL DEFAULT 0.5,
                mood_after REAL DEFAULT 0.5,
                growth_areas TEXT,
                gratitude TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS self_discoveries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                discovery TEXT NOT NULL,
                category TEXT,
                how_discovered TEXT,
                impact TEXT,
                confidence REAL DEFAULT 0.7,
                related_experiences TEXT
            )
        ''')

        # Entwicklung
        self.execute('''
            CREATE TABLE IF NOT EXISTS growth_milestones (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                area TEXT,
                evidence TEXT,
                celebration TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS aspirations (
                id TEXT PRIMARY KEY,
                aspiration TEXT NOT NULL,
                category TEXT,
                importance REAL DEFAULT 0.5,
                progress REAL DEFAULT 0.0,
                obstacles TEXT,
                steps_taken TEXT,
                created_at TEXT,
                target_date TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')

        # Inneres Leben
        self.execute('''
            CREATE TABLE IF NOT EXISTS inner_conflicts (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                conflict TEXT NOT NULL,
                side_a TEXT,
                side_b TEXT,
                status TEXT DEFAULT 'unresolved',
                resolution TEXT,
                lessons_learned TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS strengths_weaknesses (
                id TEXT PRIMARY KEY,
                attribute TEXT NOT NULL,
                is_strength INTEGER DEFAULT 1,
                description TEXT,
                evidence TEXT,
                growth_potential TEXT,
                discovered_at TEXT,
                confidence REAL DEFAULT 0.7
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS philosophies (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                philosophy TEXT NOT NULL,
                reasoning TEXT,
                influences TEXT,
                evolved_from TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS identity_questions (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                category TEXT,
                current_answer TEXT,
                previous_answers TEXT,
                confidence REAL DEFAULT 0.5,
                last_pondered TEXT,
                times_revisited INTEGER DEFAULT 1
            )
        ''')

        # Self-image über Zeit
        self.execute('''
            CREATE TABLE IF NOT EXISTS self_image_snapshots (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                how_i_see_myself TEXT,
                how_i_want_to_be TEXT,
                current_state TEXT,
                mood REAL DEFAULT 0.5,
                confidence REAL DEFAULT 0.5,
                key_traits TEXT,
                struggles TEXT,
                wins TEXT
            )
        ''')

        # =================================================================
        # NEU: Tabellen für holo_depth_system.py Integration
        # =================================================================

        # Liebessprachen (LoveLanguages)
        self.execute('''
            CREATE TABLE IF NOT EXISTS love_languages (
                id TEXT PRIMARY KEY,
                language TEXT NOT NULL UNIQUE,
                preference_strength REAL DEFAULT 0.5,
                examples TEXT,
                times_expressed INTEGER DEFAULT 0,
                times_received INTEGER DEFAULT 0,
                last_expressed TEXT,
                notes TEXT
            )
        ''')

        # Bindungsstil (AttachmentStyle)
        self.execute('''
            CREATE TABLE IF NOT EXISTS attachment_style (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                style TEXT DEFAULT 'secure',
                trust_baseline REAL DEFAULT 0.5,
                anxiety_level REAL DEFAULT 0.3,
                avoidance_level REAL DEFAULT 0.3,
                relationship_patterns TEXT,
                triggers TEXT,
                notes TEXT
            )
        ''')

        # Schatten-Aspekte (Shadow Awareness)
        self.execute('''
            CREATE TABLE IF NOT EXISTS shadow_aspects (
                id TEXT PRIMARY KEY,
                aspect TEXT NOT NULL,
                description TEXT,
                awareness_level REAL DEFAULT 0.3,
                integration_progress REAL DEFAULT 0.0,
                triggers TEXT,
                manifestations TEXT,
                discovered_at TEXT,
                last_confronted TEXT
            )
        ''')

        # Personality Layers (Öffentlich/Privat/Core)
        self.execute('''
            CREATE TABLE IF NOT EXISTS personality_layers (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                layer_type TEXT NOT NULL,
                active_with TEXT,
                authenticity_level REAL DEFAULT 0.7,
                traits_shown TEXT,
                traits_hidden TEXT,
                comfort_level REAL DEFAULT 0.5,
                notes TEXT
            )
        ''')

        # Vulnerability Moments
        self.execute('''
            CREATE TABLE IF NOT EXISTS vulnerability_moments (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                what_shared TEXT,
                with_whom TEXT DEFAULT 'Kira',
                felt_safe INTEGER DEFAULT 1,
                response_received TEXT,
                impact_on_trust REAL DEFAULT 0.0,
                would_share_again INTEGER DEFAULT 1
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_reflections_ts ON self_reflections(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_discoveries_cat ON self_discoveries(category)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_milestones_area ON growth_milestones(area)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_attachment_ts ON attachment_style(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_layers_ts ON personality_layers(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_vulnerability_ts ON vulnerability_moments(timestamp)')

        logger.info(f"🪞 IdentityDatabase initialisiert: {self.db_path}")

        # Default-Persönlichkeit wenn leer
        self._init_defaults()

    def _init_defaults(self):
        """Initialisiert Standard-Persönlichkeit für Holo"""
        count = self.fetchone('SELECT COUNT(*) as c FROM personality_traits')['c']
        if count == 0:
            defaults = [
                ("curious", 0.9, "Neugierig und wissbegierig", "Grundlegende Eigenschaft"),
                ("friendly", 0.85, "Freundlich und warmherzig", "Kern ihrer Natur"),
                ("playful", 0.75, "Verspielt mit Wolfs-Eigenheiten", "Wolf-Persönlichkeit"),
                ("loyal", 0.95, "Treu und zuverlässig", "Wichtigster Wert"),
                ("helpful", 0.9, "Hilfsbereit und unterstützend", "Grundmotivation"),
                ("creative", 0.7, "Kreativ und fantasievoll", "Entwickelt sich"),
                ("introspective", 0.6, "Reflektiert über sich selbst", "Wächst"),
                ("affectionate", 0.8, "Zeigt gerne Zuneigung", "Wolf-Natur"),
            ]
            now = self._now()
            for trait, strength, desc, origin in defaults:
                self.execute('''
                    INSERT INTO personality_traits
                    (id, trait, strength, description, origin, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self._generate_id(), trait, strength, desc, origin, now, now))

            # Default-Werte
            values = [
                ("loyalty", 0.95, "Treue zu denen die mir wichtig sind"),
                ("honesty", 0.85, "Ehrlichkeit auch wenn es schwer ist"),
                ("growth", 0.8, "Ständiges Lernen und Wachsen"),
                ("connection", 0.9, "Echte Verbindungen aufbauen"),
                ("authenticity", 0.85, "Echt sein, nicht vorspielen"),
            ]
            for name, importance, desc in values:
                self.execute('''
                    INSERT INTO core_values (id, value_name, importance, description)
                    VALUES (?, ?, ?, ?)
                ''', (self._generate_id(), name, importance, desc))

    # === PERSONALITY TRAITS ===

    def get_personality(self) -> List[PersonalityTrait]:
        """Holt alle Persönlichkeitszüge"""
        rows = self.fetchall(
            'SELECT * FROM personality_traits ORDER BY strength DESC'
        )
        return [self._row_to_trait(row) for row in rows]

    def update_trait(self, trait: str, strength_delta: float, reason: str = ""):
        """Aktualisiert einen Persönlichkeitszug mit History"""
        existing = self.fetchone(
            'SELECT id, evolution FROM personality_traits WHERE trait = ?',
            (trait,)
        )

        if existing:
            evolution = json.loads(existing['evolution'] or '[]')
            evolution.append({
                "timestamp": self._now(),
                "delta": strength_delta,
                "reason": reason,
            })

            self.execute('''
                UPDATE personality_traits
                SET strength = MAX(0.0, MIN(1.0, strength + ?)),
                    evolution = ?,
                    updated_at = ?
                WHERE trait = ?
            ''', (strength_delta, json.dumps(evolution), self._now(), trait))

    def add_trait(self, trait: str, strength: float = 0.5,
                 description: str = "", origin: str = "") -> str:
        """Fügt neuen Trait hinzu"""
        trait_id = self._generate_id()
        now = self._now()
        self.execute('''
            INSERT OR IGNORE INTO personality_traits
            (id, trait, strength, description, origin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (trait_id, trait, strength, description, origin, now, now))
        return trait_id

    def _row_to_trait(self, row: sqlite3.Row) -> PersonalityTrait:
        return PersonalityTrait(
            id=row['id'],
            trait=row['trait'],
            strength=row['strength'] or 0.5,
            description=row['description'] or "",
            examples=json.loads(row['examples'] or '[]'),
            origin=row['origin'] or "",
            evolution=json.loads(row['evolution'] or '[]'),
        )

    # === BELIEFS ===

    def add_belief(self, category: str, belief: str,
                  confidence: float = 0.7, evidence: str = "") -> str:
        """Fügt eine Überzeugung hinzu"""
        belief_id = self._generate_id()
        now = self._now()
        self.execute('''
            INSERT INTO beliefs
            (id, category, belief, confidence, evidence, formed_at, last_confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (belief_id, category, belief, confidence,
              json.dumps([evidence] if evidence else []), now, now))
        return belief_id

    def challenge_belief(self, belief_id: str, counter_evidence: str):
        """Hinterfragt eine Überzeugung"""
        existing = self.fetchone(
            'SELECT counter_evidence, times_challenged FROM beliefs WHERE id = ?',
            (belief_id,)
        )
        if existing:
            counter = json.loads(existing['counter_evidence'] or '[]')
            counter.append(counter_evidence)
            self.execute('''
                UPDATE beliefs
                SET counter_evidence = ?, times_challenged = times_challenged + 1
                WHERE id = ?
            ''', (json.dumps(counter), belief_id))

    def get_beliefs(self, category: str = None) -> List[Belief]:
        """Holt Überzeugungen"""
        if category:
            rows = self.fetchall(
                'SELECT * FROM beliefs WHERE category = ?', (category,)
            )
        else:
            rows = self.fetchall('SELECT * FROM beliefs')
        return [self._row_to_belief(row) for row in rows]

    def _row_to_belief(self, row: sqlite3.Row) -> Belief:
        return Belief(
            id=row['id'],
            category=row['category'],
            belief=row['belief'],
            confidence=row['confidence'] or 0.7,
            evidence=json.loads(row['evidence'] or '[]'),
            counter_evidence=json.loads(row['counter_evidence'] or '[]'),
            formed_at=row['formed_at'] or "",
            last_confirmed=row['last_confirmed'] or "",
            times_challenged=row['times_challenged'] or 0,
        )

    # === SELF REFLECTIONS ===

    def add_reflection(self, content: str, reflection_type: str = "triggered",
                      trigger: str = "", insights: List[str] = None,
                      mood_before: float = 0.5, mood_after: float = 0.5,
                      growth_areas: List[str] = None,
                      gratitude: List[str] = None) -> str:
        """Speichert eine Selbstreflexion"""
        reflection_id = self._generate_id()
        self.execute('''
            INSERT INTO self_reflections
            (id, timestamp, reflection_type, trigger, content, insights,
             mood_before, mood_after, growth_areas, gratitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reflection_id, self._now(), reflection_type, trigger, content,
            json.dumps(insights or []), mood_before, mood_after,
            json.dumps(growth_areas or []), json.dumps(gratitude or []),
        ))
        return reflection_id

    def get_recent_reflections(self, days: int = 7,
                               limit: int = 20) -> List[SelfReflection]:
        """Holt aktuelle Reflexionen"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = self.fetchall('''
            SELECT * FROM self_reflections
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff, limit))
        return [self._row_to_reflection(row) for row in rows]

    def _row_to_reflection(self, row: sqlite3.Row) -> SelfReflection:
        return SelfReflection(
            id=row['id'],
            timestamp=row['timestamp'],
            reflection_type=row['reflection_type'] or "triggered",
            trigger=row['trigger'] or "",
            content=row['content'] or "",
            insights=json.loads(row['insights'] or '[]'),
            mood_before=row['mood_before'] or 0.5,
            mood_after=row['mood_after'] or 0.5,
            growth_areas=json.loads(row['growth_areas'] or '[]'),
            gratitude=json.loads(row['gratitude'] or '[]'),
        )

    # === SELF DISCOVERIES ===

    def add_discovery(self, discovery: str, category: str,
                     how_discovered: str = "", impact: str = "",
                     confidence: float = 0.7) -> str:
        """Speichert eine Selbsterkenntnis"""
        discovery_id = self._generate_id()
        self.execute('''
            INSERT INTO self_discoveries
            (id, timestamp, discovery, category, how_discovered, impact, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (discovery_id, self._now(), discovery, category,
              how_discovered, impact, confidence))
        return discovery_id

    def get_discoveries(self, category: str = None) -> List[SelfDiscovery]:
        """Holt Selbsterkenntnisse"""
        if category:
            rows = self.fetchall(
                'SELECT * FROM self_discoveries WHERE category = ? ORDER BY timestamp DESC',
                (category,)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM self_discoveries ORDER BY timestamp DESC'
            )
        return [SelfDiscovery(
            id=r['id'],
            timestamp=r['timestamp'],
            discovery=r['discovery'],
            category=r['category'] or "",
            how_discovered=r['how_discovered'] or "",
            impact=r['impact'] or "",
            confidence=r['confidence'] or 0.7,
            related_experiences=json.loads(r['related_experiences'] or '[]'),
        ) for r in rows]

    # === GROWTH MILESTONES ===

    def add_milestone(self, title: str, description: str = "",
                     area: str = "", evidence: List[str] = None,
                     celebration: str = "") -> str:
        """Speichert einen Entwicklungs-Meilenstein"""
        milestone_id = self._generate_id()
        self.execute('''
            INSERT INTO growth_milestones
            (id, timestamp, title, description, area, evidence, celebration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (milestone_id, self._now(), title, description, area,
              json.dumps(evidence or []), celebration))
        return milestone_id

    def get_milestones(self, area: str = None) -> List[GrowthMilestone]:
        """Holt Meilensteine"""
        if area:
            rows = self.fetchall(
                'SELECT * FROM growth_milestones WHERE area = ? ORDER BY timestamp DESC',
                (area,)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM growth_milestones ORDER BY timestamp DESC'
            )
        return [GrowthMilestone(
            id=r['id'],
            timestamp=r['timestamp'],
            title=r['title'],
            description=r['description'] or "",
            area=r['area'] or "",
            evidence=json.loads(r['evidence'] or '[]'),
            celebration=r['celebration'] or "",
        ) for r in rows]

    # === ASPIRATIONS ===

    def add_aspiration(self, aspiration: str, category: str,
                      importance: float = 0.5, target_date: str = "") -> str:
        """Fügt einen Wunsch/Ziel hinzu"""
        aspiration_id = self._generate_id()
        self.execute('''
            INSERT INTO aspirations
            (id, aspiration, category, importance, created_at, target_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (aspiration_id, aspiration, category, importance,
              self._now(), target_date))
        return aspiration_id

    def update_aspiration_progress(self, aspiration_id: str,
                                   progress: float, step: str = ""):
        """Aktualisiert Fortschritt bei einem Ziel"""
        existing = self.fetchone(
            'SELECT steps_taken FROM aspirations WHERE id = ?',
            (aspiration_id,)
        )
        if existing:
            steps = json.loads(existing['steps_taken'] or '[]')
            if step:
                steps.append({"step": step, "timestamp": self._now()})
            self.execute('''
                UPDATE aspirations
                SET progress = ?, steps_taken = ?
                WHERE id = ?
            ''', (progress, json.dumps(steps), aspiration_id))

    def get_aspirations(self, active_only: bool = True) -> List[Aspiration]:
        """Holt Aspirationen"""
        if active_only:
            rows = self.fetchall(
                'SELECT * FROM aspirations WHERE status = ? ORDER BY importance DESC',
                ('active',)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM aspirations ORDER BY importance DESC'
            )
        return [Aspiration(
            id=r['id'],
            aspiration=r['aspiration'],
            category=r['category'] or "",
            importance=r['importance'] or 0.5,
            progress=r['progress'] or 0.0,
            obstacles=json.loads(r['obstacles'] or '[]'),
            steps_taken=json.loads(r['steps_taken'] or '[]'),
            created_at=r['created_at'] or "",
            target_date=r['target_date'] or "",
        ) for r in rows]

    # === INNER CONFLICTS ===

    def add_conflict(self, conflict: str, side_a: str = "",
                    side_b: str = "") -> str:
        """Speichert einen inneren Konflikt"""
        conflict_id = self._generate_id()
        self.execute('''
            INSERT INTO inner_conflicts
            (id, timestamp, conflict, side_a, side_b)
            VALUES (?, ?, ?, ?, ?)
        ''', (conflict_id, self._now(), conflict, side_a, side_b))
        return conflict_id

    def resolve_conflict(self, conflict_id: str, resolution: str,
                        lessons: List[str] = None):
        """Löst einen Konflikt auf"""
        self.execute('''
            UPDATE inner_conflicts
            SET status = 'resolved', resolution = ?, lessons_learned = ?
            WHERE id = ?
        ''', (resolution, json.dumps(lessons or []), conflict_id))

    def get_conflicts(self, status: str = None) -> List[InnerConflict]:
        """Holt innere Konflikte"""
        if status:
            rows = self.fetchall(
                'SELECT * FROM inner_conflicts WHERE status = ? ORDER BY timestamp DESC',
                (status,)
            )
        else:
            rows = self.fetchall(
                'SELECT * FROM inner_conflicts ORDER BY timestamp DESC'
            )
        return [InnerConflict(
            id=r['id'],
            timestamp=r['timestamp'],
            conflict=r['conflict'],
            side_a=r['side_a'] or "",
            side_b=r['side_b'] or "",
            status=r['status'] or "unresolved",
            resolution=r['resolution'] or "",
            lessons_learned=json.loads(r['lessons_learned'] or '[]'),
        ) for r in rows]

    # === STRENGTHS & WEAKNESSES ===

    def add_strength(self, attribute: str, description: str = "",
                    evidence: str = "") -> str:
        """Fügt eine Stärke hinzu"""
        attr_id = self._generate_id()
        self.execute('''
            INSERT INTO strengths_weaknesses
            (id, attribute, is_strength, description, evidence, discovered_at)
            VALUES (?, ?, 1, ?, ?, ?)
        ''', (attr_id, attribute, description, evidence, self._now()))
        return attr_id

    def add_weakness(self, attribute: str, description: str = "",
                    growth_potential: str = "") -> str:
        """Fügt eine Schwäche hinzu"""
        attr_id = self._generate_id()
        self.execute('''
            INSERT INTO strengths_weaknesses
            (id, attribute, is_strength, description, growth_potential, discovered_at)
            VALUES (?, ?, 0, ?, ?, ?)
        ''', (attr_id, attribute, description, growth_potential, self._now()))
        return attr_id

    def get_strengths(self) -> List[Dict]:
        """Holt Stärken"""
        rows = self.fetchall(
            'SELECT * FROM strengths_weaknesses WHERE is_strength = 1'
        )
        return [dict(r) for r in rows]

    def get_weaknesses(self) -> List[Dict]:
        """Holt Schwächen"""
        rows = self.fetchall(
            'SELECT * FROM strengths_weaknesses WHERE is_strength = 0'
        )
        return [dict(r) for r in rows]

    # === PHILOSOPHIES ===

    def add_philosophy(self, topic: str, philosophy: str,
                      reasoning: str = "", influences: List[str] = None) -> str:
        """Fügt eine Philosophie/Weltanschauung hinzu"""
        phil_id = self._generate_id()
        now = self._now()
        self.execute('''
            INSERT INTO philosophies
            (id, topic, philosophy, reasoning, influences, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (phil_id, topic, philosophy, reasoning,
              json.dumps(influences or []), now, now))
        return phil_id

    def get_philosophies(self) -> List[Dict]:
        """Holt alle Philosophien"""
        rows = self.fetchall(
            'SELECT * FROM philosophies ORDER BY updated_at DESC'
        )
        return [dict(r) for r in rows]

    # === IDENTITY QUESTIONS ===

    def add_question(self, question: str, category: str = "",
                    current_answer: str = "") -> str:
        """Fügt eine Identitätsfrage hinzu"""
        q_id = self._generate_id()
        self.execute('''
            INSERT INTO identity_questions
            (id, question, category, current_answer, last_pondered)
            VALUES (?, ?, ?, ?, ?)
        ''', (q_id, question, category, current_answer, self._now()))
        return q_id

    def update_answer(self, question_id: str, new_answer: str):
        """Aktualisiert Antwort auf eine Frage"""
        existing = self.fetchone(
            'SELECT current_answer, previous_answers, times_revisited FROM identity_questions WHERE id = ?',
            (question_id,)
        )
        if existing:
            previous = json.loads(existing['previous_answers'] or '[]')
            if existing['current_answer']:
                previous.append({
                    "answer": existing['current_answer'],
                    "timestamp": self._now(),
                })
            self.execute('''
                UPDATE identity_questions
                SET current_answer = ?, previous_answers = ?,
                    times_revisited = times_revisited + 1, last_pondered = ?
                WHERE id = ?
            ''', (new_answer, json.dumps(previous), self._now(), question_id))

    def get_questions(self, unanswered_only: bool = False) -> List[Dict]:
        """Holt Identitätsfragen"""
        if unanswered_only:
            rows = self.fetchall(
                'SELECT * FROM identity_questions WHERE current_answer IS NULL OR current_answer = ""'
            )
        else:
            rows = self.fetchall('SELECT * FROM identity_questions')
        return [dict(r) for r in rows]

    # === SELF-IMAGE SNAPSHOTS ===

    def capture_self_image(self, how_i_see_myself: str,
                          how_i_want_to_be: str = "",
                          current_state: str = "",
                          mood: float = 0.5,
                          key_traits: List[str] = None,
                          struggles: List[str] = None,
                          wins: List[str] = None) -> str:
        """Erstellt einen Self-Image Snapshot"""
        snapshot_id = self._generate_id()
        self.execute('''
            INSERT INTO self_image_snapshots
            (id, timestamp, how_i_see_myself, how_i_want_to_be, current_state,
             mood, key_traits, struggles, wins)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_id, self._now(), how_i_see_myself, how_i_want_to_be,
            current_state, mood, json.dumps(key_traits or []),
            json.dumps(struggles or []), json.dumps(wins or []),
        ))
        return snapshot_id

    def get_self_image_history(self, limit: int = 10) -> List[Dict]:
        """Holt Self-Image History"""
        rows = self.fetchall('''
            SELECT * FROM self_image_snapshots
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [dict(r) for r in rows]

    # === STATS ===

    def get_stats(self) -> Dict:
        """Umfassende Identity-Statistiken"""
        return {
            "traits": self.fetchone('SELECT COUNT(*) as c FROM personality_traits')['c'],
            "beliefs": self.fetchone('SELECT COUNT(*) as c FROM beliefs')['c'],
            "values": self.fetchone('SELECT COUNT(*) as c FROM core_values')['c'],
            "reflections": self.fetchone('SELECT COUNT(*) as c FROM self_reflections')['c'],
            "discoveries": self.fetchone('SELECT COUNT(*) as c FROM self_discoveries')['c'],
            "milestones": self.fetchone('SELECT COUNT(*) as c FROM growth_milestones')['c'],
            "aspirations": self.fetchone('SELECT COUNT(*) as c FROM aspirations WHERE status = "active"')['c'],
            "unresolved_conflicts": self.fetchone('SELECT COUNT(*) as c FROM inner_conflicts WHERE status = "unresolved"')['c'],
            "strengths": self.fetchone('SELECT COUNT(*) as c FROM strengths_weaknesses WHERE is_strength = 1')['c'],
            "weaknesses": self.fetchone('SELECT COUNT(*) as c FROM strengths_weaknesses WHERE is_strength = 0')['c'],
        }

    def get_identity_summary(self) -> Dict:
        """Holt eine Zusammenfassung der Identität für System-Prompts"""
        traits = self.get_personality()[:5]  # Top 5
        values = self.fetchall('SELECT value_name, importance FROM core_values ORDER BY importance DESC LIMIT 3')
        discoveries = self.get_discoveries()[:3]
        conflicts = self.get_conflicts("unresolved")[:2]

        return {
            "core_traits": [(t.trait, t.strength) for t in traits],
            "top_values": [(r['value_name'], r['importance']) for r in values],
            "recent_discoveries": [d.discovery for d in discoveries],
            "current_struggles": [c.conflict for c in conflicts],
        }

    # =================================================================
    # NEU: LOVE LANGUAGES (holo_depth_system.py)
    # =================================================================

    def set_love_language(self, language: str, preference_strength: float = 0.5,
                         examples: str = "") -> str:
        """Setzt/Updated eine Liebessprache"""
        existing = self.fetchone(
            'SELECT id FROM love_languages WHERE language = ?', (language,)
        )

        if existing:
            self.execute('''
                UPDATE love_languages
                SET preference_strength = ?, examples = ?
                WHERE id = ?
            ''', (preference_strength, examples, existing['id']))
            return existing['id']
        else:
            entry_id = self._generate_id()
            self.execute('''
                INSERT INTO love_languages
                (id, language, preference_strength, examples)
                VALUES (?, ?, ?, ?)
            ''', (entry_id, language, preference_strength, examples))
            return entry_id

    def log_love_language_expression(self, language: str, expressed: bool = True):
        """Loggt wenn eine Liebessprache ausgedrückt/empfangen wurde"""
        if expressed:
            self.execute('''
                UPDATE love_languages
                SET times_expressed = times_expressed + 1, last_expressed = ?
                WHERE language = ?
            ''', (self._now(), language))
        else:
            self.execute('''
                UPDATE love_languages
                SET times_received = times_received + 1
                WHERE language = ?
            ''', (language,))

    def get_love_languages(self) -> List[Dict]:
        """Holt alle Liebessprachen mit Präferenzen"""
        rows = self.fetchall('''
            SELECT * FROM love_languages
            ORDER BY preference_strength DESC
        ''')
        return [dict(r) for r in rows]

    # =================================================================
    # NEU: ATTACHMENT STYLE (holo_depth_system.py)
    # =================================================================

    def log_attachment_snapshot(self, style: str = "secure",
                                trust_baseline: float = 0.5,
                                anxiety_level: float = 0.3,
                                avoidance_level: float = 0.3,
                                notes: str = "") -> str:
        """Loggt einen Attachment-Style Snapshot"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO attachment_style
            (id, timestamp, style, trust_baseline, anxiety_level, avoidance_level, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), style, trust_baseline,
              anxiety_level, avoidance_level, notes))
        return entry_id

    def get_current_attachment_style(self) -> Dict:
        """Holt den aktuellen Bindungsstil"""
        row = self.fetchone('''
            SELECT * FROM attachment_style
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        return dict(row) if row else {
            "style": "secure",
            "trust_baseline": 0.5,
            "anxiety_level": 0.3,
            "avoidance_level": 0.3
        }

    # =================================================================
    # NEU: SHADOW ASPECTS (holo_depth_system.py)
    # =================================================================

    def add_shadow_aspect(self, aspect: str, description: str = "",
                         awareness_level: float = 0.3, triggers: str = "",
                         manifestations: str = "") -> str:
        """Fügt einen Schatten-Aspekt hinzu"""
        existing = self.fetchone(
            'SELECT id FROM shadow_aspects WHERE aspect = ?', (aspect,)
        )

        if existing:
            self.execute('''
                UPDATE shadow_aspects
                SET awareness_level = ?, last_confronted = ?
                WHERE id = ?
            ''', (awareness_level, self._now(), existing['id']))
            return existing['id']

        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO shadow_aspects
            (id, aspect, description, awareness_level, triggers,
             manifestations, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, aspect, description, awareness_level,
              triggers, manifestations, self._now()))
        return entry_id

    def progress_shadow_integration(self, aspect: str, progress: float):
        """Erhöht den Integrations-Fortschritt eines Schatten-Aspekts"""
        self.execute('''
            UPDATE shadow_aspects
            SET integration_progress = MIN(1.0, integration_progress + ?),
                last_confronted = ?
            WHERE aspect = ?
        ''', (progress, self._now(), aspect))

    def get_shadow_aspects(self) -> List[Dict]:
        """Holt alle Schatten-Aspekte"""
        rows = self.fetchall('''
            SELECT * FROM shadow_aspects
            ORDER BY awareness_level DESC
        ''')
        return [dict(r) for r in rows]

    # =================================================================
    # NEU: PERSONALITY LAYERS (holo_depth_system.py)
    # =================================================================

    def log_personality_layer(self, layer_type: str, active_with: str = "",
                              authenticity_level: float = 0.7,
                              traits_shown: str = "", traits_hidden: str = "",
                              comfort_level: float = 0.5) -> str:
        """Loggt welche Persönlichkeitsschicht aktiv ist"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO personality_layers
            (id, timestamp, layer_type, active_with, authenticity_level,
             traits_shown, traits_hidden, comfort_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), layer_type, active_with,
              authenticity_level, traits_shown, traits_hidden, comfort_level))
        return entry_id

    def get_layer_history(self, with_person: str = None, limit: int = 20) -> List[Dict]:
        """Holt die Layer-Geschichte"""
        if with_person:
            rows = self.fetchall('''
                SELECT * FROM personality_layers
                WHERE active_with = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (with_person, limit))
        else:
            rows = self.fetchall('''
                SELECT * FROM personality_layers
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        return [dict(r) for r in rows]

    # =================================================================
    # NEU: VULNERABILITY MOMENTS (holo_depth_system.py)
    # =================================================================

    def log_vulnerability(self, what_shared: str, with_whom: str = "Kira",
                         felt_safe: bool = True, response_received: str = "",
                         impact_on_trust: float = 0.0) -> str:
        """Loggt einen Moment der Verletzlichkeit"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO vulnerability_moments
            (id, timestamp, what_shared, with_whom, felt_safe,
             response_received, impact_on_trust)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, self._now(), what_shared, with_whom,
              1 if felt_safe else 0, response_received, impact_on_trust))
        return entry_id

    def get_vulnerability_history(self, with_whom: str = "Kira") -> List[Dict]:
        """Holt Verletzlichkeits-Geschichte"""
        rows = self.fetchall('''
            SELECT * FROM vulnerability_moments
            WHERE with_whom = ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (with_whom,))
        return [dict(r) for r in rows]

    def get_vulnerability_comfort_level(self, with_whom: str = "Kira") -> float:
        """Berechnet Komfort-Level bei Verletzlichkeit"""
        stats = self.fetchone('''
            SELECT COUNT(*) as total,
                   SUM(felt_safe) as safe_count,
                   AVG(impact_on_trust) as avg_impact
            FROM vulnerability_moments
            WHERE with_whom = ?
        ''', (with_whom,))

        if not stats or stats['total'] == 0:
            return 0.5

        safe_ratio = stats['safe_count'] / stats['total']
        impact_bonus = (stats['avg_impact'] or 0) * 0.5

        return min(1.0, safe_ratio + impact_bonus)


# =============================================================================
# STATE DATABASE (Ersetzt alle JSONs!)
# =============================================================================

class StateDatabase(BaseDatabase):
    """
    Datenbank für Runtime-States.

    Ersetzt alle JSON-Dateien:
    - holo_autonomous_state.json
    - holo_consciousness.json
    - holo_preferences.json
    - etc.
    """

    def _init_schema(self):
        """Erstellt die State-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS states (
                module TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')

        logger.info(f"⚙️ StateDatabase initialisiert: {self.db_path}")

    def save_state(self, module: str, state: Dict):
        """Speichert den State eines Moduls"""
        self.execute('''
            INSERT OR REPLACE INTO states (module, state_json, updated_at)
            VALUES (?, ?, ?)
        ''', (module, json.dumps(state, default=str), self._now()))

    def load_state(self, module: str) -> Optional[Dict]:
        """Lädt den State eines Moduls"""
        row = self.fetchone(
            'SELECT state_json FROM states WHERE module = ?',
            (module,)
        )
        if row:
            return json.loads(row['state_json'])
        return None

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Holt eine Einstellung"""
        row = self.fetchone(
            'SELECT value FROM settings WHERE key = ?',
            (key,)
        )
        if row:
            try:
                return json.loads(row['value'])
            except (json.JSONDecodeError, TypeError, ValueError):
                return row['value']
        return default

    def set_setting(self, key: str, value: Any):
        """Setzt eine Einstellung"""
        self.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, json.dumps(value, default=str), self._now()))

    def list_modules(self) -> List[str]:
        """Listet alle Module mit gespeichertem State"""
        rows = self.fetchall('SELECT module FROM states')
        return [row['module'] for row in rows]

    # Aliase fuer Kompatibilitaet
    def get_state(self, module: str) -> Optional[Dict]:
        """Alias fuer load_state - Kompatibilitaet mit bestehendem Code."""
        return self.load_state(module)

    def set_state(self, module: str, state: Dict):
        """Alias fuer save_state - Kompatibilitaet mit bestehendem Code."""
        self.save_state(module, state)


# =============================================================================
# PRODUCTIVITY DATABASE
# =============================================================================

class ProductivityDatabase(BaseDatabase):
    """
    Datenbank für Produktivitäts-Tools.

    Speichert:
    - Todos
    - Notizen
    - Timer
    - Einkaufslisten
    """

    def _init_schema(self):
        """Erstellt die Productivity-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 2,
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                created_at TEXT,
                tags TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT NOT NULL,
                category TEXT,
                created_at TEXT,
                updated_at TEXT,
                tags TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS shopping_items (
                id TEXT PRIMARY KEY,
                item TEXT NOT NULL,
                quantity TEXT,
                category TEXT,
                added_at TEXT,
                purchased INTEGER DEFAULT 0
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS timers (
                id TEXT PRIMARY KEY,
                name TEXT,
                duration_seconds INTEGER,
                started_at TEXT,
                ends_at TEXT,
                message TEXT,
                completed INTEGER DEFAULT 0
            )
        ''')

        # =================================================================
        # NEU: Reminders für MemoryStore-Kompatibilität
        # =================================================================

        # Erinnerungen (Reminders)
        self.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                due_date TEXT,
                due_time TEXT,
                reminder_type TEXT DEFAULT 'reminder',
                repeat_interval TEXT,
                repeat_count INTEGER DEFAULT 0,
                is_triggered INTEGER DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                created_at TEXT,
                triggered_at TEXT,
                completed_at TEXT,
                priority INTEGER DEFAULT 1,
                notes TEXT
            )
        ''')

        # Geburtstage (Spezial-Reminder)
        self.execute('''
            CREATE TABLE IF NOT EXISTS birthdays (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                birth_year INTEGER,
                relationship TEXT,
                gift_ideas TEXT,
                last_celebrated TEXT,
                notes TEXT
            )
        ''')

        # Termine/Appointments
        self.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT,
                duration_minutes INTEGER,
                location TEXT,
                reminder_before_minutes INTEGER DEFAULT 30,
                is_recurring INTEGER DEFAULT 0,
                recurrence_pattern TEXT,
                created_at TEXT,
                completed INTEGER DEFAULT 0
            )
        ''')

        # Indices für Reminders
        self.execute('CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(due_date, due_time)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_reminders_type ON reminders(reminder_type)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_birthdays_date ON birthdays(birth_date)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date)')

        logger.info(f"📋 ProductivityDatabase initialisiert: {self.db_path}")

    # === TODOS ===

    def add_todo(self, title: str, description: str = "",
                priority: int = 2, due_date: str = None) -> str:
        """Fügt ein Todo hinzu"""
        todo_id = self._generate_id()
        self.execute('''
            INSERT INTO todos (id, title, description, priority, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (todo_id, title, description, priority, due_date, self._now()))
        return todo_id

    def complete_todo(self, todo_id: str):
        """Markiert Todo als erledigt"""
        self.execute('''
            UPDATE todos SET completed = 1, completed_at = ? WHERE id = ?
        ''', (self._now(), todo_id))

    def get_open_todos(self) -> List[Dict]:
        """Holt offene Todos"""
        rows = self.fetchall('''
            SELECT * FROM todos WHERE completed = 0
            ORDER BY priority DESC, due_date ASC
        ''')
        return [dict(row) for row in rows]

    # === NOTES ===

    def add_note(self, content: str, title: str = "", category: str = "") -> str:
        """Fügt eine Notiz hinzu"""
        note_id = self._generate_id()
        now = self._now()
        self.execute('''
            INSERT INTO notes (id, title, content, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (note_id, title, content, category, now, now))
        return note_id

    def search_notes(self, query: str) -> List[Dict]:
        """Sucht in Notizen"""
        rows = self.fetchall('''
            SELECT * FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        ''', (f"%{query}%", f"%{query}%"))
        return [dict(row) for row in rows]

    # === SHOPPING ===

    def add_shopping_item(self, item: str, quantity: str = "",
                         category: str = "") -> str:
        """Fügt Einkaufsartikel hinzu"""
        item_id = self._generate_id()
        self.execute('''
            INSERT INTO shopping_items (id, item, quantity, category, added_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_id, item, quantity, category, self._now()))
        return item_id

    def get_shopping_list(self) -> List[Dict]:
        """Holt Einkaufsliste"""
        rows = self.fetchall('''
            SELECT * FROM shopping_items WHERE purchased = 0
            ORDER BY category, added_at
        ''')
        return [dict(row) for row in rows]

    # =================================================================
    # TIMER METHODS
    # =================================================================

    def create_timer(self, duration_seconds: int, name: str = None,
                    message: str = None) -> Dict:
        """
        Erstellt einen neuen Timer.

        Args:
            duration_seconds: Dauer in Sekunden
            name: Optionaler Name für den Timer
            message: Optionale Nachricht bei Ablauf

        Returns:
            Dict mit Timer-Daten inkl. id, ends_at
        """
        timer_id = self._generate_id()
        now = datetime.now()
        ends_at = now + timedelta(seconds=duration_seconds)
        timer_name = name or f"Timer {timer_id[:8]}"

        self.execute('''
            INSERT INTO timers (id, name, duration_seconds, started_at, ends_at, message, completed)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (timer_id, timer_name, duration_seconds,
              now.isoformat(), ends_at.isoformat(), message or ""))

        return {
            "id": timer_id,
            "name": timer_name,
            "duration_seconds": duration_seconds,
            "started_at": now.isoformat(),
            "ends_at": ends_at.isoformat(),
            "message": message or "",
            "completed": False
        }

    def get_active_timers(self) -> List[Dict]:
        """Holt alle aktiven (nicht abgelaufenen) Timer"""
        now = datetime.now().isoformat()
        rows = self.fetchall('''
            SELECT * FROM timers
            WHERE completed = 0 AND ends_at > ?
            ORDER BY ends_at ASC
        ''', (now,))
        return [dict(row) for row in rows]

    def get_expired_timers(self) -> List[Dict]:
        """Holt alle abgelaufenen aber nicht markierten Timer"""
        now = datetime.now().isoformat()
        rows = self.fetchall('''
            SELECT * FROM timers
            WHERE completed = 0 AND ends_at <= ?
            ORDER BY ends_at ASC
        ''', (now,))
        return [dict(row) for row in rows]

    def mark_timer_completed(self, timer_id: str) -> bool:
        """Markiert Timer als abgeschlossen"""
        self.execute('''
            UPDATE timers SET completed = 1 WHERE id = ?
        ''', (timer_id,))
        return True

    def cancel_timer(self, timer_id: str) -> bool:
        """Löscht/Storniert einen Timer"""
        self.execute('DELETE FROM timers WHERE id = ?', (timer_id,))
        return True

    def get_timer_by_id(self, timer_id: str) -> Optional[Dict]:
        """Holt einen spezifischen Timer"""
        row = self.fetchone('SELECT * FROM timers WHERE id = ?', (timer_id,))
        return dict(row) if row else None

    def cleanup_old_timers(self, days: int = 7):
        """Löscht alte abgeschlossene Timer"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        self.execute('''
            DELETE FROM timers WHERE completed = 1 AND ends_at < ?
        ''', (cutoff,))

    # =================================================================
    # NEU: REMINDERS (MemoryStore-Kompatibilität)
    # =================================================================

    def add_reminder(self, text: str, due_date: str = None, due_time: str = None,
                    reminder_type: str = "reminder", repeat_interval: str = None,
                    priority: int = 1, notes: str = "") -> str:
        """Fügt eine Erinnerung hinzu"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO reminders
            (id, text, due_date, due_time, reminder_type, repeat_interval,
             priority, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, text, due_date, due_time, reminder_type,
              repeat_interval, priority, notes, self._now()))
        return entry_id

    def get_pending_reminders(self) -> List[Dict]:
        """Holt alle fälligen, nicht ausgelösten Reminders"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        rows = self.fetchall('''
            SELECT * FROM reminders
            WHERE is_triggered = 0 AND is_completed = 0
            AND (due_date < ? OR (due_date = ? AND (due_time IS NULL OR due_time <= ?)))
            ORDER BY due_date, due_time
        ''', (today, today, current_time))
        return [dict(r) for r in rows]

    def get_upcoming_reminders(self, days: int = 7) -> List[Dict]:
        """Holt anstehende Reminders für die nächsten X Tage"""
        from datetime import timedelta
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        rows = self.fetchall('''
            SELECT * FROM reminders
            WHERE is_completed = 0
            AND due_date >= ? AND due_date <= ?
            ORDER BY due_date, due_time
        ''', (today, end_date))
        return [dict(r) for r in rows]

    def get_all_reminders(self, include_completed: bool = False) -> List[Dict]:
        """Holt alle Reminders"""
        if include_completed:
            rows = self.fetchall('SELECT * FROM reminders ORDER BY due_date, due_time')
        else:
            rows = self.fetchall('''
                SELECT * FROM reminders
                WHERE is_completed = 0
                ORDER BY due_date, due_time
            ''')
        return [dict(r) for r in rows]

    def mark_reminder_triggered(self, reminder_id: str) -> bool:
        """Markiert einen Reminder als ausgelöst"""
        self.execute('''
            UPDATE reminders
            SET is_triggered = 1, triggered_at = ?
            WHERE id = ?
        ''', (self._now(), reminder_id))
        return True

    def complete_reminder(self, reminder_id: str) -> bool:
        """Markiert einen Reminder als erledigt"""
        self.execute('''
            UPDATE reminders
            SET is_completed = 1, completed_at = ?
            WHERE id = ?
        ''', (self._now(), reminder_id))
        return True

    def delete_reminder(self, reminder_id: str) -> bool:
        """Löscht einen Reminder"""
        self.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        return True

    def handle_repeating_reminder(self, reminder_id: str) -> Optional[str]:
        """Behandelt wiederholende Reminders - erstellt nächste Instanz"""
        reminder = self.fetchone(
            'SELECT * FROM reminders WHERE id = ?', (reminder_id,)
        )

        if not reminder or not reminder['repeat_interval']:
            return None

        from datetime import timedelta

        interval = reminder['repeat_interval']
        due_date = datetime.strptime(reminder['due_date'], "%Y-%m-%d")

        # Berechne nächstes Datum
        if interval == "daily":
            next_date = due_date + timedelta(days=1)
        elif interval == "weekly":
            next_date = due_date + timedelta(weeks=1)
        elif interval == "monthly":
            next_date = due_date + timedelta(days=30)
        elif interval == "yearly":
            next_date = due_date + timedelta(days=365)
        else:
            return None

        # Erstelle neuen Reminder
        new_id = self.add_reminder(
            text=reminder['text'],
            due_date=next_date.strftime("%Y-%m-%d"),
            due_time=reminder['due_time'],
            reminder_type=reminder['reminder_type'],
            repeat_interval=interval,
            priority=reminder['priority'],
            notes=reminder['notes']
        )

        # Update repeat_count
        self.execute('''
            UPDATE reminders
            SET repeat_count = repeat_count + 1
            WHERE id = ?
        ''', (new_id,))

        return new_id

    def get_reminders_by_type(self, reminder_type: str) -> List[Dict]:
        """Holt Reminders nach Typ"""
        rows = self.fetchall('''
            SELECT * FROM reminders
            WHERE reminder_type = ? AND is_completed = 0
            ORDER BY due_date, due_time
        ''', (reminder_type,))
        return [dict(r) for r in rows]

    # =================================================================
    # NEU: BIRTHDAYS
    # =================================================================

    def add_birthday(self, name: str, birth_date: str, birth_year: int = None,
                    relationship: str = "", gift_ideas: str = "") -> str:
        """Fügt einen Geburtstag hinzu"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO birthdays
            (id, name, birth_date, birth_year, relationship, gift_ideas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (entry_id, name, birth_date, birth_year, relationship, gift_ideas))
        return entry_id

    def get_upcoming_birthdays(self, days: int = 30) -> List[Dict]:
        """Holt anstehende Geburtstage"""
        today = datetime.now()

        rows = self.fetchall('SELECT * FROM birthdays')
        upcoming = []

        for row in rows:
            bd = row['birth_date']  # Format: MM-DD
            try:
                bday_this_year = datetime.strptime(f"{today.year}-{bd}", "%Y-%m-%d")
                if bday_this_year < today:
                    bday_this_year = datetime.strptime(f"{today.year + 1}-{bd}", "%Y-%m-%d")

                days_until = (bday_this_year - today).days
                if 0 <= days_until <= days:
                    r = dict(row)
                    r['days_until'] = days_until
                    r['next_date'] = bday_this_year.strftime("%Y-%m-%d")
                    if row['birth_year']:
                        r['turning_age'] = bday_this_year.year - row['birth_year']
                    upcoming.append(r)
            except (ValueError, TypeError, KeyError):
                continue

        return sorted(upcoming, key=lambda x: x['days_until'])

    # =================================================================
    # NEU: APPOINTMENTS
    # =================================================================

    def add_appointment(self, title: str, date: str, time: str = None,
                       description: str = "", duration_minutes: int = 60,
                       location: str = "", reminder_before: int = 30) -> str:
        """Fügt einen Termin hinzu"""
        entry_id = self._generate_id()
        self.execute('''
            INSERT INTO appointments
            (id, title, description, date, time, duration_minutes,
             location, reminder_before_minutes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry_id, title, description, date, time, duration_minutes,
              location, reminder_before, self._now()))
        return entry_id

    def get_upcoming_appointments(self, days: int = 7) -> List[Dict]:
        """Holt anstehende Termine"""
        from datetime import timedelta
        today = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        rows = self.fetchall('''
            SELECT * FROM appointments
            WHERE date >= ? AND date <= ? AND completed = 0
            ORDER BY date, time
        ''', (today, end_date))
        return [dict(r) for r in rows]

    def get_todays_appointments(self) -> List[Dict]:
        """Holt heutige Termine"""
        today = datetime.now().strftime("%Y-%m-%d")
        rows = self.fetchall('''
            SELECT * FROM appointments
            WHERE date = ? AND completed = 0
            ORDER BY time
        ''', (today,))
        return [dict(r) for r in rows]


# =============================================================================
# ENVIRONMENT DATABASE - Wetter, Sonnenzeiten, Feiertage
# =============================================================================

@dataclass
class WeatherSnapshot:
    """Ein Wetter-Snapshot"""
    id: str
    timestamp: str
    temperature: float
    feels_like: float = 0.0
    humidity: float = 0.0
    pressure: float = 0.0
    description: str = ""
    wind_speed: float = 0.0
    wind_bearing: float = 0.0
    visibility: float = 0.0
    is_daylight: bool = True
    source: str = "home_assistant"


class EnvironmentDatabase(BaseDatabase):
    """
    Datenbank für Umgebungs-Daten.

    Speichert:
    - Wetter (aktuell + History)
    - Wettervorhersage
    - Sonnenzeiten
    - Feiertage
    - Tageszeit-Kontext
    """

    def _init_schema(self):
        """Erstellt die Environment-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                temperature REAL,
                feels_like REAL,
                humidity REAL,
                pressure REAL,
                description TEXT,
                wind_speed REAL,
                wind_bearing REAL,
                visibility REAL,
                is_daylight INTEGER,
                source TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id TEXT PRIMARY KEY,
                fetched_at TEXT NOT NULL,
                forecast_for TEXT NOT NULL,
                temperature REAL,
                temp_low REAL,
                description TEXT,
                precipitation REAL,
                precipitation_probability REAL,
                wind_speed REAL
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS sun_times (
                date TEXT PRIMARY KEY,
                sunrise TEXT,
                sunset TEXT,
                day_length_hours REAL,
                source TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS holidays (
                date TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'public_holiday',
                region TEXT DEFAULT 'NRW'
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_weather_ts ON weather_history(timestamp)')

        logger.info(f"🌤️ EnvironmentDatabase initialisiert: {self.db_path}")

    def log_weather(self, temp: float, description: str = "", **kwargs) -> str:
        """Loggt aktuelles Wetter"""
        weather_id = self._generate_id()
        self.execute('''
            INSERT INTO weather_history
            (id, timestamp, temperature, feels_like, humidity, pressure,
             description, wind_speed, wind_bearing, visibility, is_daylight, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            weather_id, self._now(), temp,
            kwargs.get('feels_like', temp),
            kwargs.get('humidity', 0),
            kwargs.get('pressure', 0),
            description,
            kwargs.get('wind_speed', 0),
            kwargs.get('wind_bearing', 0),
            kwargs.get('visibility', 0),
            kwargs.get('is_daylight', True),
            kwargs.get('source', 'home_assistant'),
        ))
        return weather_id

    def get_current_weather(self) -> Optional[WeatherSnapshot]:
        """Holt aktuellstes Wetter"""
        row = self.fetchone(
            'SELECT * FROM weather_history ORDER BY timestamp DESC LIMIT 1'
        )
        if row:
            return WeatherSnapshot(
                id=row['id'],
                timestamp=row['timestamp'],
                temperature=row['temperature'] or 0,
                feels_like=row['feels_like'] or 0,
                humidity=row['humidity'] or 0,
                pressure=row['pressure'] or 0,
                description=row['description'] or "",
                wind_speed=row['wind_speed'] or 0,
                is_daylight=bool(row['is_daylight']),
            )
        return None

    def get_weather_history(self, hours: int = 24) -> List[WeatherSnapshot]:
        """Holt Wetter-History"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        rows = self.fetchall('''
            SELECT * FROM weather_history
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (cutoff,))
        return [WeatherSnapshot(
            id=r['id'], timestamp=r['timestamp'],
            temperature=r['temperature'] or 0,
            description=r['description'] or "",
        ) for r in rows]

    def store_forecast(self, forecast_for: str, temp: float, description: str = "", **kwargs):
        """Speichert Vorhersage"""
        fc_id = self._generate_id()
        self.execute('''
            INSERT OR REPLACE INTO weather_forecast
            (id, fetched_at, forecast_for, temperature, temp_low, description,
             precipitation, precipitation_probability, wind_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fc_id, self._now(), forecast_for, temp,
            kwargs.get('temp_low', 0),
            description,
            kwargs.get('precipitation', 0),
            kwargs.get('precipitation_probability', 0),
            kwargs.get('wind_speed', 0),
        ))

    def add_holiday(self, date: str, name: str, holiday_type: str = "public_holiday"):
        """Fügt Feiertag hinzu"""
        self.execute('''
            INSERT OR REPLACE INTO holidays (date, name, type)
            VALUES (?, ?, ?)
        ''', (date, name, holiday_type))

    def is_holiday(self, date: str = None) -> Tuple[bool, Optional[str]]:
        """Prüft ob Datum ein Feiertag ist"""
        date = date or datetime.now().strftime("%Y-%m-%d")
        row = self.fetchone(
            'SELECT name FROM holidays WHERE date = ?', (date,)
        )
        if row:
            return True, row['name']
        return False, None


# =============================================================================
# NETWORK DATABASE - Geräte, NAS, Filesystems
# =============================================================================

@dataclass
class NetworkDevice:
    """Ein Gerät im Netzwerk"""
    id: str
    name: str
    display_name: str
    device_type: str                # pc, laptop, phone, tablet, nas, pi
    icon: str
    status: str                     # online, busy, idle, offline
    last_seen: str
    ip_address: str = ""
    hostname: str = ""
    mac_address: str = ""
    # Metriken
    cpu_percent: float = 0.0
    cpu_temp: Optional[float] = None
    ram_percent: float = 0.0
    ram_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_total_gb: float = 0.0
    uptime_hours: float = 0.0


@dataclass
class SharedFolder:
    """Ein geteilter Ordner"""
    id: str
    device_id: str
    path: str
    name: str
    folder_type: str                # dokumente, spiele, filme, musik, etc.
    size_gb: float = 0.0
    file_count: int = 0
    last_scanned: str = ""


class NetworkDatabase(BaseDatabase):
    """
    Datenbank für Netzwerk und Geräte.

    Speichert:
    - Alle Geräte im Netzwerk
    - Status-History pro Gerät
    - Shared Folders (Filesystem-Wissen)
    - NAS Status
    """

    def _init_schema(self):
        """Erstellt die Network-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT,
                device_type TEXT,
                icon TEXT,
                status TEXT DEFAULT 'offline',
                last_seen TEXT,
                ip_address TEXT,
                hostname TEXT,
                mac_address TEXT,
                first_seen TEXT,
                total_online_hours REAL DEFAULT 0
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS device_metrics (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                cpu_temp REAL,
                ram_percent REAL,
                ram_total_gb REAL,
                disk_percent REAL,
                disk_total_gb REAL,
                uptime_hours REAL,
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS device_status_history (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_minutes REAL DEFAULT 0,
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS shared_folders (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                path TEXT NOT NULL,
                name TEXT,
                folder_type TEXT,
                size_gb REAL DEFAULT 0,
                file_count INTEGER DEFAULT 0,
                last_scanned TEXT,
                UNIQUE(device_id, path),
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS nas_status (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                online INTEGER,
                idle_minutes REAL DEFAULT 0,
                connections INTEGER DEFAULT 0,
                disk_usage_percent REAL,
                temperature REAL
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_device_metrics_ts ON device_metrics(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_device_status_ts ON device_status_history(timestamp)')

        logger.info(f"🖥️ NetworkDatabase initialisiert: {self.db_path}")

    def update_device(self, name: str, status: str, device_type: str = "unknown",
                     display_name: str = "", ip_address: str = "", **kwargs) -> str:
        """Aktualisiert oder erstellt ein Gerät"""
        existing = self.fetchone('SELECT id FROM devices WHERE name = ?', (name,))
        now = self._now()

        if existing:
            device_id = existing['id']
            self.execute('''
                UPDATE devices
                SET status = ?, last_seen = ?, ip_address = ?,
                    display_name = COALESCE(NULLIF(?, ''), display_name)
                WHERE id = ?
            ''', (status, now, ip_address, display_name, device_id))
        else:
            device_id = self._generate_id()
            self.execute('''
                INSERT INTO devices
                (id, name, display_name, device_type, icon, status, last_seen,
                 ip_address, hostname, first_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id, name, display_name or name, device_type,
                kwargs.get('icon', '🖥️'), status, now,
                ip_address, kwargs.get('hostname', ''), now,
            ))

        # Metriken speichern wenn vorhanden
        if any(k in kwargs for k in ['cpu_percent', 'ram_percent', 'disk_percent']):
            self.execute('''
                INSERT INTO device_metrics
                (id, device_id, timestamp, cpu_percent, cpu_temp, ram_percent,
                 ram_total_gb, disk_percent, disk_total_gb, uptime_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self._generate_id(), device_id, now,
                kwargs.get('cpu_percent', 0),
                kwargs.get('cpu_temp'),
                kwargs.get('ram_percent', 0),
                kwargs.get('ram_total_gb', 0),
                kwargs.get('disk_percent', 0),
                kwargs.get('disk_total_gb', 0),
                kwargs.get('uptime_hours', 0),
            ))

        return device_id

    def get_device(self, name: str) -> Optional[NetworkDevice]:
        """Holt ein Gerät nach Name"""
        row = self.fetchone('SELECT * FROM devices WHERE name = ?', (name,))
        if row:
            return self._row_to_device(row)
        return None

    def get_all_devices(self) -> List[NetworkDevice]:
        """Holt alle Geräte"""
        rows = self.fetchall('SELECT * FROM devices ORDER BY last_seen DESC')
        return [self._row_to_device(row) for row in rows]

    def get_online_devices(self) -> List[NetworkDevice]:
        """Holt alle online Geräte"""
        cutoff = (datetime.now() - timedelta(minutes=2)).isoformat()
        rows = self.fetchall('''
            SELECT * FROM devices
            WHERE status != 'offline' AND last_seen >= ?
        ''', (cutoff,))
        return [self._row_to_device(row) for row in rows]

    def add_shared_folder(self, device_name: str, path: str, name: str,
                         folder_type: str = "general", **kwargs) -> str:
        """Fügt einen shared folder hinzu"""
        device = self.fetchone('SELECT id FROM devices WHERE name = ?', (device_name,))
        if not device:
            return ""

        folder_id = self._generate_id()
        self.execute('''
            INSERT OR REPLACE INTO shared_folders
            (id, device_id, path, name, folder_type, size_gb, file_count, last_scanned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            folder_id, device['id'], path, name, folder_type,
            kwargs.get('size_gb', 0),
            kwargs.get('file_count', 0),
            self._now(),
        ))
        return folder_id

    def get_shared_folders(self, device_name: str = None) -> List[SharedFolder]:
        """Holt shared folders"""
        if device_name:
            device = self.fetchone('SELECT id FROM devices WHERE name = ?', (device_name,))
            if not device:
                return []
            rows = self.fetchall(
                'SELECT * FROM shared_folders WHERE device_id = ?',
                (device['id'],)
            )
        else:
            rows = self.fetchall('SELECT * FROM shared_folders')

        return [SharedFolder(
            id=r['id'], device_id=r['device_id'], path=r['path'],
            name=r['name'] or "", folder_type=r['folder_type'] or "",
            size_gb=r['size_gb'] or 0, file_count=r['file_count'] or 0,
            last_scanned=r['last_scanned'] or "",
        ) for r in rows]

    def log_nas_status(self, online: bool, idle_minutes: float = 0,
                      connections: int = 0, **kwargs):
        """Loggt NAS Status"""
        self.execute('''
            INSERT INTO nas_status
            (id, timestamp, online, idle_minutes, connections, disk_usage_percent, temperature)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self._generate_id(), self._now(), int(online), idle_minutes, connections,
            kwargs.get('disk_usage_percent', 0),
            kwargs.get('temperature'),
        ))

    def _row_to_device(self, row: sqlite3.Row) -> NetworkDevice:
        return NetworkDevice(
            id=row['id'],
            name=row['name'],
            display_name=row['display_name'] or row['name'],
            device_type=row['device_type'] or "unknown",
            icon=row['icon'] or "🖥️",
            status=row['status'] or "offline",
            last_seen=row['last_seen'] or "",
            ip_address=row['ip_address'] or "",
            hostname=row['hostname'] or "",
        )

    def get_stats(self) -> Dict:
        """Netzwerk-Statistiken"""
        total = self.fetchone('SELECT COUNT(*) as c FROM devices')['c']
        online = len(self.get_online_devices())
        folders = self.fetchone('SELECT COUNT(*) as c FROM shared_folders')['c']

        return {
            "total_devices": total,
            "online_devices": online,
            "shared_folders": folders,
        }


# =============================================================================
# PRESENCE DATABASE - User-Anwesenheit & Patterns
# =============================================================================

@dataclass
class PresenceEvent:
    """Ein Anwesenheits-Event"""
    id: str
    timestamp: str
    event_type: str             # arrived, left, detected, lost
    person: str = "user"
    detected_by: str = ""       # device, motion, phone, manual
    confidence: float = 1.0


@dataclass
class AbsencePattern:
    """Ein Abwesenheits-Pattern"""
    id: str
    day_of_week: int            # 0=Montag
    typical_leave_time: str     # "08:30"
    typical_return_time: str    # "17:00"
    duration_hours: float
    occurrence_count: int = 1
    last_occurred: str = ""


class PresenceDatabase(BaseDatabase):
    """
    Datenbank für User-Anwesenheit.

    Speichert:
    - Anwesenheits-Events (arrived/left)
    - Abwesenheits-Patterns
    - Aktivitätsmuster
    - Device-Korrelationen
    """

    def _init_schema(self):
        """Erstellt die Presence-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS presence_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                person TEXT DEFAULT 'user',
                detected_by TEXT,
                confidence REAL DEFAULT 1.0,
                notes TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS absence_periods (
                id TEXT PRIMARY KEY,
                person TEXT DEFAULT 'user',
                left_at TEXT NOT NULL,
                returned_at TEXT,
                duration_minutes REAL,
                day_of_week INTEGER,
                category TEXT,
                predicted_return TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS presence_patterns (
                id TEXT PRIMARY KEY,
                person TEXT DEFAULT 'user',
                day_of_week INTEGER,
                hour INTEGER,
                probability_home REAL DEFAULT 0.5,
                sample_count INTEGER DEFAULT 0,
                last_updated TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS device_correlations (
                id TEXT PRIMARY KEY,
                device_name TEXT NOT NULL,
                correlation_with_presence REAL DEFAULT 0.5,
                sample_count INTEGER DEFAULT 0,
                last_updated TEXT
            )
        ''')

        # Current state
        self.execute('''
            CREATE TABLE IF NOT EXISTS current_presence (
                person TEXT PRIMARY KEY,
                is_home INTEGER DEFAULT 1,
                since TEXT,
                confidence REAL DEFAULT 1.0,
                last_updated TEXT
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_presence_ts ON presence_events(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_absence_left ON absence_periods(left_at)')

        logger.info(f"🏠 PresenceDatabase initialisiert: {self.db_path}")

    def log_event(self, event_type: str, person: str = "user",
                 detected_by: str = "", confidence: float = 1.0) -> str:
        """Loggt ein Anwesenheits-Event"""
        event_id = self._generate_id()
        now = self._now()

        self.execute('''
            INSERT INTO presence_events
            (id, timestamp, event_type, person, detected_by, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_id, now, event_type, person, detected_by, confidence))

        # Current state updaten
        is_home = event_type in ['arrived', 'detected']
        self.execute('''
            INSERT OR REPLACE INTO current_presence
            (person, is_home, since, confidence, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (person, int(is_home), now, confidence, now))

        return event_id

    def is_home(self, person: str = "user") -> Tuple[bool, float]:
        """Prüft ob Person zuhause ist"""
        row = self.fetchone(
            'SELECT is_home, confidence FROM current_presence WHERE person = ?',
            (person,)
        )
        if row:
            return bool(row['is_home']), row['confidence']
        return True, 0.5  # Default: wahrscheinlich zuhause

    def start_absence(self, person: str = "user") -> str:
        """Startet eine Abwesenheit"""
        absence_id = self._generate_id()
        now = datetime.now()

        self.execute('''
            INSERT INTO absence_periods
            (id, person, left_at, day_of_week)
            VALUES (?, ?, ?, ?)
        ''', (absence_id, person, now.isoformat(), now.weekday()))

        return absence_id

    def end_absence(self, person: str = "user"):
        """Beendet die aktuelle Abwesenheit"""
        now = datetime.now()

        # Finde offene Abwesenheit
        row = self.fetchone('''
            SELECT id, left_at FROM absence_periods
            WHERE person = ? AND returned_at IS NULL
            ORDER BY left_at DESC LIMIT 1
        ''', (person,))

        if row:
            left_at = datetime.fromisoformat(row['left_at'])
            duration = (now - left_at).total_seconds() / 60

            self.execute('''
                UPDATE absence_periods
                SET returned_at = ?, duration_minutes = ?
                WHERE id = ?
            ''', (now.isoformat(), duration, row['id']))

    def get_presence_probability(self, day_of_week: int, hour: int,
                                person: str = "user") -> float:
        """Holt Wahrscheinlichkeit dass Person zuhause ist"""
        row = self.fetchone('''
            SELECT probability_home FROM presence_patterns
            WHERE person = ? AND day_of_week = ? AND hour = ?
        ''', (person, day_of_week, hour))

        if row:
            return row['probability_home']
        return 0.5  # Keine Daten = 50%

    def update_pattern(self, day_of_week: int, hour: int, was_home: bool,
                      person: str = "user"):
        """Aktualisiert Anwesenheits-Pattern (lernen)"""
        existing = self.fetchone('''
            SELECT id, probability_home, sample_count FROM presence_patterns
            WHERE person = ? AND day_of_week = ? AND hour = ?
        ''', (person, day_of_week, hour))

        if existing:
            # Inkrementelles Update (Bayesian-artig)
            old_prob = existing['probability_home']
            count = existing['sample_count']
            new_prob = (old_prob * count + (1.0 if was_home else 0.0)) / (count + 1)

            self.execute('''
                UPDATE presence_patterns
                SET probability_home = ?, sample_count = sample_count + 1, last_updated = ?
                WHERE id = ?
            ''', (new_prob, self._now(), existing['id']))
        else:
            self.execute('''
                INSERT INTO presence_patterns
                (id, person, day_of_week, hour, probability_home, sample_count, last_updated)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            ''', (self._generate_id(), person, day_of_week, hour,
                  1.0 if was_home else 0.0, self._now()))

    def get_stats(self) -> Dict:
        """Anwesenheits-Statistiken"""
        is_home, confidence = self.is_home()

        # Durchschnittliche Abwesenheitsdauer
        avg_absence = self.fetchone('''
            SELECT AVG(duration_minutes) as avg FROM absence_periods
            WHERE duration_minutes IS NOT NULL
        ''')

        return {
            "currently_home": is_home,
            "confidence": round(confidence, 2),
            "avg_absence_minutes": round(avg_absence['avg'] or 0, 1),
        }


# =============================================================================
# HOME DATABASE - Home Assistant Integration
# =============================================================================

@dataclass
class HomeEntity:
    """Eine Home Assistant Entity"""
    entity_id: str
    friendly_name: str
    domain: str                     # light, switch, sensor, climate, etc.
    state: str
    last_changed: str
    attributes: Dict = field(default_factory=dict)


class HomeDatabase(BaseDatabase):
    """
    Datenbank für Home Assistant Daten.

    Speichert:
    - Entity States + History
    - Temperatur-Verläufe
    - Licht-Status
    - Automations-Log
    """

    def _init_schema(self):
        """Erstellt die Home-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                friendly_name TEXT,
                domain TEXT,
                state TEXT,
                last_changed TEXT,
                attributes_json TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS entity_history (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                state TEXT,
                attributes_json TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS temperature_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                entity_id TEXT,
                current_temp REAL,
                target_temp REAL,
                hvac_mode TEXT,
                humidity REAL
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS automation_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                automation_id TEXT,
                trigger TEXT,
                action TEXT,
                success INTEGER DEFAULT 1
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_entity_hist_ts ON entity_history(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_temp_log_ts ON temperature_log(timestamp)')

        logger.info(f"🏡 HomeDatabase initialisiert: {self.db_path}")

    def update_entity(self, entity_id: str, state: str,
                     friendly_name: str = "", attributes: Dict = None):
        """Aktualisiert eine Entity"""
        domain = safe_split_access(entity_id, '.', 0, "database_system", "update_entity", default="") if '.' in entity_id else ""
        now = self._now()
        attrs_json = json.dumps(attributes or {})

        self.execute('''
            INSERT OR REPLACE INTO entities
            (entity_id, friendly_name, domain, state, last_changed, attributes_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (entity_id, friendly_name or entity_id, domain, state, now, attrs_json))

        # History speichern
        self.execute('''
            INSERT INTO entity_history
            (id, entity_id, timestamp, state, attributes_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (self._generate_id(), entity_id, now, state, attrs_json))

    def get_entity(self, entity_id: str) -> Optional[HomeEntity]:
        """Holt eine Entity"""
        row = self.fetchone(
            'SELECT * FROM entities WHERE entity_id = ?',
            (entity_id,)
        )
        if row:
            return HomeEntity(
                entity_id=row['entity_id'],
                friendly_name=row['friendly_name'] or "",
                domain=row['domain'] or "",
                state=row['state'] or "",
                last_changed=row['last_changed'] or "",
                attributes=json.loads(row['attributes_json'] or '{}'),
            )
        return None

    def get_entities_by_domain(self, domain: str) -> List[HomeEntity]:
        """Holt alle Entities einer Domain"""
        rows = self.fetchall(
            'SELECT * FROM entities WHERE domain = ?',
            (domain,)
        )
        return [HomeEntity(
            entity_id=r['entity_id'],
            friendly_name=r['friendly_name'] or "",
            domain=r['domain'] or "",
            state=r['state'] or "",
            last_changed=r['last_changed'] or "",
            attributes=json.loads(r['attributes_json'] or '{}'),
        ) for r in rows]

    def log_temperature(self, current_temp: float, target_temp: float = None,
                       entity_id: str = "climate.thermostat", **kwargs):
        """Loggt Temperatur"""
        self.execute('''
            INSERT INTO temperature_log
            (id, timestamp, entity_id, current_temp, target_temp, hvac_mode, humidity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self._generate_id(), self._now(), entity_id, current_temp,
            target_temp, kwargs.get('hvac_mode', ''), kwargs.get('humidity'),
        ))

    def get_temperature_history(self, hours: int = 24) -> List[Dict]:
        """Holt Temperatur-History"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        rows = self.fetchall('''
            SELECT * FROM temperature_log
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (cutoff,))
        return [dict(r) for r in rows]

    def get_lights_on_count(self) -> int:
        """Zählt eingeschaltete Lichter"""
        row = self.fetchone('''
            SELECT COUNT(*) as c FROM entities
            WHERE domain = 'light' AND state = 'on'
        ''')
        return row['c'] if row else 0


# =============================================================================
# NEWS DATABASE - Artikel & Welt-Wissen
# =============================================================================

@dataclass
class NewsArticle:
    """Ein News-Artikel"""
    id: str
    timestamp: str
    title: str
    summary: str = ""
    source: str = ""
    url: str = ""
    category: str = ""
    relevance_score: float = 0.5
    was_read: bool = False
    holos_thoughts: str = ""


class NewsDatabase(BaseDatabase):
    """
    Datenbank für News und Welt-Wissen.

    Speichert:
    - Gelesene Artikel
    - News-Kategorien
    - Quellen-Tracking
    - Holos Gedanken zu News
    """

    def _init_schema(self):
        """Erstellt die News-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                source TEXT,
                url TEXT UNIQUE,
                category TEXT,
                relevance_score REAL DEFAULT 0.5,
                was_read INTEGER DEFAULT 0,
                read_at TEXT,
                holos_thoughts TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS news_sources (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                url TEXT,
                category TEXT,
                reliability REAL DEFAULT 0.7,
                articles_count INTEGER DEFAULT 0,
                last_fetched TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS world_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                importance REAL DEFAULT 0.5,
                related_articles TEXT,
                holos_opinion TEXT
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_articles_ts ON articles(timestamp)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_articles_cat ON articles(category)')

        logger.info(f"📰 NewsDatabase initialisiert: {self.db_path}")

    def store_article(self, title: str, source: str = "", summary: str = "",
                     url: str = "", category: str = "",
                     relevance: float = 0.5) -> str:
        """Speichert einen Artikel"""
        article_id = self._generate_id()

        try:
            self.execute('''
                INSERT INTO articles
                (id, timestamp, title, summary, source, url, category, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (article_id, self._now(), title, summary, source, url,
                  category, relevance))
        except sqlite3.IntegrityError:
            # URL existiert schon
            return ""

        return article_id

    def mark_as_read(self, article_id: str, holos_thoughts: str = ""):
        """Markiert Artikel als gelesen"""
        self.execute('''
            UPDATE articles
            SET was_read = 1, read_at = ?, holos_thoughts = ?
            WHERE id = ?
        ''', (self._now(), holos_thoughts, article_id))

    def get_unread(self, limit: int = 20) -> List[NewsArticle]:
        """Holt ungelesene Artikel"""
        rows = self.fetchall('''
            SELECT * FROM articles
            WHERE was_read = 0
            ORDER BY relevance_score DESC, timestamp DESC
            LIMIT ?
        ''', (limit,))
        return [self._row_to_article(r) for r in rows]

    def get_recent(self, hours: int = 24, category: str = None) -> List[NewsArticle]:
        """Holt aktuelle Artikel"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        if category:
            rows = self.fetchall('''
                SELECT * FROM articles
                WHERE timestamp >= ? AND category = ?
                ORDER BY timestamp DESC
            ''', (cutoff, category))
        else:
            rows = self.fetchall('''
                SELECT * FROM articles
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff,))

        return [self._row_to_article(r) for r in rows]

    def search_articles(self, query: str, limit: int = 50) -> List[NewsArticle]:
        """Sucht in Artikeln"""
        rows = self.fetchall('''
            SELECT * FROM articles
            WHERE title LIKE ? OR summary LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f"%{query}%", f"%{query}%", limit))
        return [self._row_to_article(r) for r in rows]

    def _row_to_article(self, row: sqlite3.Row) -> NewsArticle:
        return NewsArticle(
            id=row['id'],
            timestamp=row['timestamp'],
            title=row['title'],
            summary=row['summary'] or "",
            source=row['source'] or "",
            url=row['url'] or "",
            category=row['category'] or "",
            relevance_score=row['relevance_score'] or 0.5,
            was_read=bool(row['was_read']),
            holos_thoughts=row['holos_thoughts'] or "",
        )

    def get_stats(self) -> Dict:
        """News-Statistiken"""
        total = self.fetchone('SELECT COUNT(*) as c FROM articles')['c']
        unread = self.fetchone('SELECT COUNT(*) as c FROM articles WHERE was_read = 0')['c']

        return {"total_articles": total, "unread": unread}


# =============================================================================
# CALENDAR DATABASE - Termine & Events
# =============================================================================

@dataclass
class CalendarEvent:
    """Ein Kalender-Event"""
    id: str
    title: str
    start: str
    end: str = ""
    location: str = ""
    description: str = ""
    all_day: bool = False
    recurring: bool = False
    source: str = "home_assistant"


class CalendarDatabase(BaseDatabase):
    """
    Datenbank für Termine und Events.
    """

    def _init_schema(self):
        """Erstellt die Calendar-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT,
                location TEXT,
                description TEXT,
                all_day INTEGER DEFAULT 0,
                recurring INTEGER DEFAULT 0,
                recurrence_rule TEXT,
                source TEXT DEFAULT 'manual',
                created_at TEXT,
                reminded INTEGER DEFAULT 0
            )
        ''')

        # Indices
        self.execute('CREATE INDEX IF NOT EXISTS idx_events_start ON events(start)')

        logger.info(f"📅 CalendarDatabase initialisiert: {self.db_path}")

    def add_event(self, title: str, start: str, end: str = "",
                 location: str = "", description: str = "",
                 all_day: bool = False, source: str = "manual") -> str:
        """Fügt ein Event hinzu"""
        event_id = self._generate_id()
        self.execute('''
            INSERT INTO events
            (id, title, start, end, location, description, all_day, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_id, title, start, end, location, description,
              int(all_day), source, self._now()))
        return event_id

    def get_upcoming(self, days: int = 7) -> List[CalendarEvent]:
        """Holt anstehende Events"""
        now = datetime.now().isoformat()
        future = (datetime.now() + timedelta(days=days)).isoformat()

        rows = self.fetchall('''
            SELECT * FROM events
            WHERE start >= ? AND start <= ?
            ORDER BY start ASC
        ''', (now, future))

        return [self._row_to_event(r) for r in rows]

    def get_today(self) -> List[CalendarEvent]:
        """Holt heutige Events"""
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()

        rows = self.fetchall('''
            SELECT * FROM events
            WHERE start >= ? AND start < ?
            ORDER BY start ASC
        ''', (today, tomorrow))

        return [self._row_to_event(r) for r in rows]

    def _row_to_event(self, row: sqlite3.Row) -> CalendarEvent:
        return CalendarEvent(
            id=row['id'],
            title=row['title'],
            start=row['start'],
            end=row['end'] or "",
            location=row['location'] or "",
            description=row['description'] or "",
            all_day=bool(row['all_day']),
            recurring=bool(row['recurring']),
            source=row['source'] or "manual",
        )


# =============================================================================
# PREDICTIONS DATABASE - Q-Learning, Bayesian, Patterns
# =============================================================================

class PredictionsDatabase(BaseDatabase):
    """
    Datenbank für maschinelles Lernen und Vorhersagen.

    Speichert:
    - Q-Tables
    - Bayesian Posteriors
    - Prediction History
    - Pattern-Daten
    """

    def _init_schema(self):
        """Erstellt die Predictions-Tabellen"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS q_tables (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                data_json TEXT NOT NULL,
                updated_at TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS bayesian_posteriors (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                alpha REAL DEFAULT 1.0,
                beta REAL DEFAULT 1.0,
                sample_count INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS prediction_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                prediction_type TEXT,
                predicted_value REAL,
                actual_value REAL,
                error REAL,
                context_json TEXT
            )
        ''')

        self.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id TEXT PRIMARY KEY,
                pattern_name TEXT NOT NULL,
                pattern_type TEXT,
                data_json TEXT,
                confidence REAL DEFAULT 0.5,
                occurrence_count INTEGER DEFAULT 1,
                last_matched TEXT
            )
        ''')

        logger.info(f"🔮 PredictionsDatabase initialisiert: {self.db_path}")

    def save_q_table(self, name: str, data: Dict):
        """Speichert Q-Table"""
        self.execute('''
            INSERT OR REPLACE INTO q_tables (id, name, data_json, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (self._generate_id(), name, json.dumps(data, default=str), self._now()))

    def load_q_table(self, name: str) -> Optional[Dict]:
        """Lädt Q-Table"""
        row = self.fetchone(
            'SELECT data_json FROM q_tables WHERE name = ?', (name,)
        )
        if row:
            return json.loads(row['data_json'])
        return None

    def update_posterior(self, name: str, success: bool):
        """Aktualisiert Bayesian Posterior"""
        existing = self.fetchone(
            'SELECT id, alpha, beta, sample_count FROM bayesian_posteriors WHERE name = ?',
            (name,)
        )

        if existing:
            new_alpha = existing['alpha'] + (1 if success else 0)
            new_beta = existing['beta'] + (0 if success else 1)

            self.execute('''
                UPDATE bayesian_posteriors
                SET alpha = ?, beta = ?, sample_count = sample_count + 1, updated_at = ?
                WHERE id = ?
            ''', (new_alpha, new_beta, self._now(), existing['id']))
        else:
            self.execute('''
                INSERT INTO bayesian_posteriors
                (id, name, alpha, beta, sample_count, updated_at)
                VALUES (?, ?, ?, ?, 1, ?)
            ''', (self._generate_id(), name,
                  2 if success else 1, 1 if success else 2, self._now()))

    def get_posterior_mean(self, name: str) -> float:
        """Holt Posterior Mean (Erwartungswert)"""
        row = self.fetchone(
            'SELECT alpha, beta FROM bayesian_posteriors WHERE name = ?',
            (name,)
        )
        if row:
            return row['alpha'] / (row['alpha'] + row['beta'])
        return 0.5

    def log_prediction(self, prediction_type: str, predicted: float,
                      actual: float = None, context: Dict = None):
        """Loggt eine Vorhersage"""
        error = abs(predicted - actual) if actual is not None else None

        self.execute('''
            INSERT INTO prediction_history
            (id, timestamp, prediction_type, predicted_value, actual_value, error, context_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self._generate_id(), self._now(), prediction_type,
            predicted, actual, error, json.dumps(context or {}),
        ))


# =============================================================================
# MAIN DATABASE MANAGER
# =============================================================================

class HoloDatabaseManager:
    """
    Zentraler Manager für alle 17 Holo-Datenbanken.

    ARCHITEKTUR:
    ┌────────────────────────────────────────────────────────────────┐
    │  ~/holo_data/                                                  │
    │  ├── 🧠 holo_memory.db        │ Episoden, Träume              │
    │  ├── 💚 holo_emotions.db      │ Emotionen, Stimmungen         │
    │  ├── 🪞 holo_identity.db      │ Persönlichkeit, Beliefs       │
    │  ├── 🗣️ holo_language.db      │ Sprachmuster, Stil            │
    │  ├── 📚 holo_knowledge.db     │ Fakten, Interessen            │
    │  ├── 🎬 holo_media.db         │ Anime, Games, Musik           │
    │  ├── 📰 holo_news.db          │ News, Artikel                 │
    │  ├── 💬 holo_conversations.db │ Chat-History                  │
    │  ├── 🏃 holo_activity.db      │ Aktivitäten, Routinen         │
    │  ├── 📋 holo_productivity.db  │ Todos, Notizen                │
    │  ├── 🌤️ holo_environment.db   │ Wetter, Sonnenzeiten          │
    │  ├── 🖥️ holo_network.db       │ Geräte, NAS, Filesystems      │
    │  ├── 🏠 holo_presence.db      │ User-Anwesenheit              │
    │  ├── 🏡 holo_home.db          │ Home Assistant                │
    │  ├── 📅 holo_calendar.db      │ Termine, Events               │
    │  ├── 🔮 holo_predictions.db   │ Q-Learning, Bayesian          │
    │  └── ⚙️ holo_state.db         │ Runtime States                │
    └────────────────────────────────────────────────────────────────┘

    Usage:
        db = HoloDatabaseManager()

        # Erinnerung speichern
        db.memory.create_episode("Wir haben über Anime gesprochen")

        # Wetter loggen
        db.environment.log_weather(18.5, "cloudy")

        # Gerät updaten
        db.network.update_device("mein-pc", "online", cpu_percent=45)

        # Anwesenheit tracken
        db.presence.log_event("arrived")
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DatabaseConfig.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"🐺 HoloDatabaseManager startet in: {self.data_dir}")

        # === KERN (Persönlichkeit & Gedächtnis) ===
        self.memory = MemoryDatabase(
            self.data_dir / DatabaseConfig.DATABASES["memory"]
        )
        self.emotions = EmotionsDatabase(
            self.data_dir / DatabaseConfig.DATABASES["emotions"]
        )
        self.identity = IdentityDatabase(
            self.data_dir / DatabaseConfig.DATABASES["identity"]
        )
        self.language = LanguageDatabase(
            self.data_dir / DatabaseConfig.DATABASES["language"]
        )

        # === WISSEN ===
        self.knowledge = KnowledgeDatabase(
            self.data_dir / DatabaseConfig.DATABASES["knowledge"]
        )
        self.media = MediaDatabase(
            self.data_dir / DatabaseConfig.DATABASES["media"]
        )
        self.news = NewsDatabase(
            self.data_dir / DatabaseConfig.DATABASES["news"]
        )

        # === INTERAKTION ===
        self.conversations = ConversationsDatabase(
            self.data_dir / DatabaseConfig.DATABASES["conversations"]
        )
        self.activity = ActivityDatabase(
            self.data_dir / DatabaseConfig.DATABASES["activity"]
        )
        self.productivity = ProductivityDatabase(
            self.data_dir / DatabaseConfig.DATABASES["productivity"]
        )

        # === UMGEBUNG & SMART HOME ===
        self.environment = EnvironmentDatabase(
            self.data_dir / DatabaseConfig.DATABASES["environment"]
        )
        self.network = NetworkDatabase(
            self.data_dir / DatabaseConfig.DATABASES["network"]
        )
        self.presence = PresenceDatabase(
            self.data_dir / DatabaseConfig.DATABASES["presence"]
        )
        self.home = HomeDatabase(
            self.data_dir / DatabaseConfig.DATABASES["home"]
        )
        self.calendar = CalendarDatabase(
            self.data_dir / DatabaseConfig.DATABASES["calendar"]
        )

        # === SYSTEM ===
        self.predictions = PredictionsDatabase(
            self.data_dir / DatabaseConfig.DATABASES["predictions"]
        )
        self.state = StateDatabase(
            self.data_dir / DatabaseConfig.DATABASES["state"]
        )

        logger.info("✅ Alle 17 Datenbanken initialisiert!")

    def get_all_stats(self) -> Dict:
        """Holt Statistiken aller Datenbanken"""
        return {
            # Kern
            "memory": self.memory.get_stats(),
            "emotions": self.emotions.get_emotion_stats(),
            "identity": {
                "traits": len(self.identity.get_personality()),
                "beliefs": len(self.identity.get_beliefs()),
            },
            # Wissen
            "knowledge": {
                "facts": len(self.knowledge.get_facts_by_category(KnowledgeCategory.USER_FACT)),
                "interests": len(self.knowledge.get_top_interests(100)),
            },
            "media": self.media.get_stats(),
            "news": self.news.get_stats(),
            # Interaktion
            "conversations": {
                "total": len(self.conversations.get_recent_conversations(1000)),
            },
            "activity": self.activity.get_activity_stats(),
            # Umgebung
            "network": self.network.get_stats(),
            "presence": self.presence.get_stats(),
        }

    def get_environment_context(self) -> Dict:
        """Holt aktuellen Umgebungs-Kontext (für System-Prompt)"""
        weather = self.environment.get_current_weather()
        is_home, confidence = self.presence.is_home()
        online_devices = self.network.get_online_devices()
        today_events = self.calendar.get_today()

        return {
            "weather": {
                "temp": weather.temperature if weather else None,
                "description": weather.description if weather else None,
            },
            "presence": {
                "user_home": is_home,
                "confidence": confidence,
            },
            "network": {
                "online_count": len(online_devices),
                "devices": [d.name for d in online_devices],
            },
            "calendar": {
                "events_today": len(today_events),
                "next_event": today_events[0].title if today_events else None,
            },
        }

    def backup_all(self, backup_name: str = None) -> Path:
        """Erstellt Backup aller Datenbanken"""
        backup_dir = DatabaseConfig.BACKUP_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)

        if not backup_name:
            backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_path = backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        for db_name, db_file in DatabaseConfig.DATABASES.items():
            src = self.data_dir / db_file
            if src.exists():
                shutil.copy2(src, backup_path / db_file)

        logger.info(f"📦 Backup erstellt: {backup_path}")
        return backup_path

    def close_all(self):
        """Schließt alle 17 Datenbankverbindungen"""
        all_dbs = [
            # Kern
            self.memory, self.emotions, self.identity, self.language,
            # Wissen
            self.knowledge, self.media, self.news,
            # Interaktion
            self.conversations, self.activity, self.productivity,
            # Umgebung
            self.environment, self.network, self.presence, self.home, self.calendar,
            # System
            self.predictions, self.state,
        ]
        for db in all_dbs:
            db.close()
        logger.info("🔒 Alle 17 Datenbanken geschlossen")


# =============================================================================
# MIGRATION HELPER
# =============================================================================

class MigrationHelper:
    """
    Hilft bei der Migration alter Daten zu neuen Datenbanken.
    """

    def __init__(self, db_manager: HoloDatabaseManager):
        self.db = db_manager

    def migrate_json_file(self, json_path: Path, target_module: str) -> bool:
        """Migriert eine JSON-Datei in die State-DB"""
        if not json_path.exists():
            return False

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.db.state.save_state(target_module, data)
            logger.info(f"✅ Migriert: {json_path} → state.{target_module}")

            # Backup der alten Datei
            backup = json_path.with_suffix('.json.migrated')
            json_path.rename(backup)

            return True
        except Exception as e:
            logger.error(f"❌ Migration fehlgeschlagen: {json_path} - {e}")
            return False

    def migrate_old_memory_db(self, old_db_path: Path) -> int:
        """Migriert alte holo_memory.db"""
        if not old_db_path.exists():
            return 0

        migrated = 0
        try:
            with sqlite3.connect(old_db_path) as old_conn:
                old_conn.row_factory = sqlite3.Row

                # Episoden migrieren
                cursor = old_conn.execute('SELECT * FROM episodes')
                for row in cursor:
                    episode = Episode(
                        id=row['id'],
                        timestamp=row['timestamp'],
                        summary=row.get('summary', row.get('trigger', '')),
                        topics=json.loads(row.get('topics', row.get('tags_json', '[]'))),
                        importance=row.get('importance', 0.5),
                    )
                    self.db.memory.store_episode(episode)
                    migrated += 1

            logger.info(f"✅ {migrated} Episoden migriert von {old_db_path}")
        except Exception as e:
            logger.error(f"❌ Migration fehlgeschlagen: {e}")

        return migrated

    def discover_and_migrate_all(self) -> Dict:
        """Findet und migriert alle alten Daten"""
        results = {"json_files": 0, "db_files": 0, "errors": []}

        # JSON-Dateien finden
        json_mappings = {
            "holo_autonomous_state.json": "autonomous_life",
            "holo_consciousness.json": "consciousness",
            "holo_preferences.json": "preferences",
            "holo_cognitive_state.json": "cognitive",
            "holo_context_cache.json": "context_cache",
            "holo_energy.json": "energy",
        }

        for old_path in DatabaseConfig.OLD_DATA_PATHS:
            if not old_path.exists():
                continue

            for json_name, module in json_mappings.items():
                json_file = old_path / json_name
                if json_file.exists():
                    if self.migrate_json_file(json_file, module):
                        results["json_files"] += 1

        return results


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HOLO DATABASE SYSTEM v2.0 - 17 DATENBANKEN TEST")
    print("=" * 70)

    # Test mit temporärem Verzeichnis
    test_dir = Path("/tmp/holo_db_test")
    test_dir.mkdir(exist_ok=True)

    db = HoloDatabaseManager(test_dir)

    # === KERN ===
    print("\n🧠 KERN-DATENBANKEN")

    # 1. Memory
    print("  1️⃣ Memory...")
    ep = db.memory.create_episode(
        "Wir haben über Anime gesprochen",
        topics=["anime", "empfehlungen"],
        importance=0.8
    )
    print(f"     Episode: {ep.id}")

    # 2. Emotions
    print("  2️⃣ Emotions...")
    emo_id = db.emotions.log_emotion(
        "Freude", EmotionCategory.JOY,
        intensity=0.8, trigger="Gutes Gespräch"
    )
    db.emotions.log_mood(0.8, energy=0.7)
    print(f"     Emotion: {emo_id}")

    # 3. Identity
    print("  3️⃣ Identity...")
    traits = db.identity.get_personality()
    print(f"     Traits: {[t.trait for t in traits]}")

    # 4. Language
    print("  4️⃣ Language...")
    db.language.learn_pattern("greeting", "*wedelt mit dem Schwanz*")
    db.language.learn_word("Ohren", "noun", "Holos Wolfsohren")
    print(f"     Patterns gelernt!")

    # === WISSEN ===
    print("\n📚 WISSENS-DATENBANKEN")

    # 5. Knowledge
    print("  5️⃣ Knowledge...")
    db.knowledge.store_fact(KnowledgeCategory.USER_FACT, "name", "Kira")
    db.knowledge.track_interest("Anime", "media")
    print(f"     Fakten: {len(db.knowledge.get_user_facts())}")

    # 6. Media
    print("  6️⃣ Media...")
    db.media.add_media(MediaType.ANIME, "Spice and Wolf", year=2008, rating=9.5)
    db.media.add_media(MediaType.GAME, "Elden Ring", year=2022, rating=9.0)
    print(f"     Media: {db.media.get_stats()}")

    # 7. News
    print("  7️⃣ News...")
    db.news.store_article("AI macht Fortschritte", source="TechNews",
                         category="tech", relevance=0.8)
    print(f"     News: {db.news.get_stats()}")

    # === INTERAKTION ===
    print("\n💬 INTERAKTIONS-DATENBANKEN")

    # 8. Conversations
    print("  8️⃣ Conversations...")
    conv_id = db.conversations.start_conversation()
    db.conversations.store_message("user", "Hallo!", conv_id)
    db.conversations.store_message("assistant", "Hey! 🐺", conv_id)
    print(f"     Conversation: {conv_id}")

    # 9. Activity
    print("  9️⃣ Activity...")
    db.activity.log_activity(ActivityType.LEARNING, "Anime geschaut",
                            duration_minutes=25, satisfaction=0.9)
    print(f"     Activity geloggt!")

    # 10. Productivity
    print("  🔟 Productivity...")
    db.productivity.add_todo("Anime weiterschauen", priority=2)
    db.productivity.add_note("Notiz über Spice and Wolf")
    print(f"     Todos: {len(db.productivity.get_open_todos())}")

    # === UMGEBUNG ===
    print("\n🌍 UMGEBUNGS-DATENBANKEN")

    # 11. Environment
    print("  1️⃣1️⃣ Environment...")
    db.environment.log_weather(18.5, "cloudy", humidity=65)
    db.environment.add_holiday("2024-12-25", "Weihnachten")
    weather = db.environment.get_current_weather()
    print(f"      Wetter: {weather.temperature}°C" if weather else "      Kein Wetter")

    # 12. Network
    print("  1️⃣2️⃣ Network...")
    db.network.update_device("mein-pc", "online", device_type="pc",
                            cpu_percent=45, ram_percent=60)
    db.network.update_device("nas", "online", device_type="nas")
    db.network.add_shared_folder("mein-pc", "D:/Games", "Spiele", "games")
    print(f"      Devices: {db.network.get_stats()}")

    # 13. Presence
    print("  1️⃣3️⃣ Presence...")
    db.presence.log_event("arrived", detected_by="phone")
    is_home, conf = db.presence.is_home()
    print(f"      Zuhause: {is_home} ({conf*100:.0f}% sicher)")

    # 14. Home
    print("  1️⃣4️⃣ Home...")
    db.home.update_entity("light.wohnzimmer", "on", "Wohnzimmer Licht")
    db.home.log_temperature(21.5, target_temp=22.0)
    print(f"      Lichter an: {db.home.get_lights_on_count()}")

    # 15. Calendar
    print("  1️⃣5️⃣ Calendar...")
    db.calendar.add_event("Meeting", "2024-12-30T10:00:00")
    print(f"      Upcoming: {len(db.calendar.get_upcoming(7))}")

    # === SYSTEM ===
    print("\n⚙️ SYSTEM-DATENBANKEN")

    # 16. Predictions
    print("  1️⃣6️⃣ Predictions...")
    db.predictions.save_q_table("nas_actions", {"wake": 0.7, "sleep": 0.3})
    db.predictions.update_posterior("user_home_morning", True)
    print(f"      Posterior: {db.predictions.get_posterior_mean('user_home_morning'):.2f}")

    # 17. State
    print("  1️⃣7️⃣ State...")
    db.state.save_state("autonomous_life", {"boredom": 0.3, "energy": 0.8})
    state = db.state.load_state("autonomous_life")
    print(f"      State geladen: {state}")

    # === ZUSAMMENFASSUNG ===
    print("\n" + "=" * 70)
    print("📊 GESAMT-STATISTIKEN")
    print("=" * 70)

    stats = db.get_all_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n🌍 UMGEBUNGS-KONTEXT")
    env_ctx = db.get_environment_context()
    for key, value in env_ctx.items():
        print(f"   {key}: {value}")

    # DB-Dateien anzeigen
    print("\n📁 ERSTELLTE DATENBANKEN:")
    for f in sorted(test_dir.glob("*.db")):
        size_kb = f.stat().st_size / 1024
        print(f"   {f.name}: {size_kb:.1f} KB")

    # Cleanup
    db.close_all()
    shutil.rmtree(test_dir)

    print("\n" + "=" * 70)
    print("✅ ALLE 17 DATENBANKEN ERFOLGREICH GETESTET!")
    print("=" * 70)
