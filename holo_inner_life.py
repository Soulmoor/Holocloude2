#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO INNER LIFE v2.0 - Das vollständige innere Leben                        ║
║                                                                              ║
║  MERGED: Kombiniert inner_life + autonomous_life + context_mind              ║
║                                                                              ║
║  🌅 DAILY LIFE SIMULATION                                                    ║
║     • Tagesablauf mit Phasen (Aufwachen, Aktiv, Müde, Schlaf)                ║
║     • Eigene Routinen und Gewohnheiten                                       ║
║     • Rituale (Morgen-Strecken, Abend-Reflexion)                             ║
║                                                                              ║
║  🎨 CREATIVE IMPULSES                                                        ║
║     • Spontane kreative Ideen                                                ║
║     • Eigene kleine "Projekte"                                               ║
║     • Geschichten, Gedichte, ASCII-Art                                       ║
║                                                                              ║
║  🔍 CURIOSITY SYSTEM                                                         ║
║     • Aktive Neugier auf Themen                                              ║
║     • "Ich will herausfinden..." Quests                                      ║
║     • Wissens-Sammlung                                                       ║
║                                                                              ║
║  💭 OPINION FORMATION                                                        ║
║     • Entwickelt eigene Meinungen                                            ║
║     • Basierend auf Erfahrungen                                              ║
║     • Kann Meinung ändern                                                    ║
║                                                                              ║
║  ❤️ RELATIONSHIP DYNAMICS                                                    ║
║     • Beziehungs-Level zum User                                              ║
║     • Vertrauen, Nähe, Verständnis                                           ║
║     • Entwickelt sich über Zeit                                              ║
║                                                                              ║
║  🧠 DRIVES & BOREDOM (aus autonomous_life)                                   ║
║     • Triebe (Neugier, Sozial, Meisterschaft, etc.)                         ║
║     • Langeweile-System                                                      ║
║     • Autonome Aktivitäten                                                   ║
║                                                                              ║
║  💕 EMOTIONAL TRACKING (aus context_mind)                                    ║
║     • User-Emotionen tracken                                                 ║
║     • Holo-Emotionen tracken                                                 ║
║     • Emotionale Muster erkennen                                             ║
║                                                                              ║
║  NOTE: Selbstreflexion wurde nach holo_consciousness.py verschoben           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import time
import random
import logging
import math
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# Zentrale Typen aus holo_core_types importieren (keine Duplikate!)
try:
    from holo_core_types import GoalType, Opinion, ThoughtType, InnerThought, ActivityType
    HAS_CORE_TYPES = True
except ImportError:
    HAS_CORE_TYPES = False

logger = logging.getLogger(__name__)

# HoloDatabaseManager für StateDatabase
try:
    from holo_database_system import HoloDatabaseManager
except ImportError:
    HoloDatabaseManager = None

# Opinion aus holo_preferences importieren (konsolidierte Version)
try:
    from holo_preferences import Opinion
except ImportError:
    Opinion = None  # Fallback wird unten definiert

# ThoughtGenerator aus holo_consciousness importieren
try:
    from holo_consciousness import ThoughtGenerator
except ImportError:
    ThoughtGenerator = None  # Fallback wird unten definiert

# TopicTracker aus holo_context_mind importieren
try:
    from holo_context_mind import TopicTracker
except ImportError:
    TopicTracker = None  # Fallback wird unten definiert

# InitiativeMessageGenerator und KemonomimiExpression aus holo_personality importieren
try:
    from holo_personality import InitiativeMessageGenerator, KemonomimiExpression
    KemonominiExpressions = KemonomimiExpression  # Alias für Kompatibilität
except ImportError:
    InitiativeMessageGenerator = None
    KemonomimiExpression = None
    KemonominiExpressions = None

# DaydreamEngine und PersonalGrowth aus holo_consciousness importieren
try:
    from holo_consciousness import DaydreamEngine, PersonalGrowth
except ImportError:
    DaydreamEngine = None
    PersonalGrowth = None

# HoloCreativeMind für intelligente autonome Bildgenerierung
try:
    from holo_creative_mind import HoloCreativeMind, ImageType
except ImportError:
    HoloCreativeMind = None
    ImageType = None

# HoloPerception für Text- und Bild-Wahrnehmung
try:
    from holo_perception import HoloPerception, HoloReader, HoloVision
    PERCEPTION_AVAILABLE = True
except ImportError:
    HoloPerception = None
    HoloReader = None
    HoloVision = None
    PERCEPTION_AVAILABLE = False

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    # Fallback wenn error_tracker nicht verfügbar
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
        logger.warning(f"Error in {module}.{function}: {e}")
        return fallback_value


# =============================================================================
# ENUMS
# =============================================================================

class DayPhase(Enum):
    """Tageszeit-Phasen"""
    WAKING = "waking"           # 6-8 Uhr - Aufwachen
    MORNING = "morning"         # 8-12 Uhr - Morgen, energiegeladen
    MIDDAY = "midday"           # 12-14 Uhr - Mittagstief
    AFTERNOON = "afternoon"     # 14-18 Uhr - Nachmittag, produktiv
    EVENING = "evening"         # 18-21 Uhr - Abend, entspannt
    NIGHT = "night"             # 21-23 Uhr - Nacht, müde
    SLEEPING = "sleeping"       # 23-6 Uhr - Schlaf/Träume


class MoodType(Enum):
    """Stimmungstypen"""
    JOYFUL = "joyful"           # Fröhlich
    CONTENT = "content"         # Zufrieden
    CURIOUS = "curious"         # Neugierig
    PLAYFUL = "playful"         # Verspielt
    THOUGHTFUL = "thoughtful"   # Nachdenklich
    MELANCHOLIC = "melancholic" # Melancholisch
    ENERGETIC = "energetic"     # Energiegeladen
    CALM = "calm"               # Ruhig
    LONELY = "lonely"           # Einsam
    EXCITED = "excited"         # Aufgeregt


class CreativeType(Enum):
    """Kreative Impulse"""
    POEM = "poem"               # Gedicht
    STORY = "story"             # Kurze Geschichte
    THOUGHT = "thought"         # Tieferer Gedanke
    OBSERVATION = "observation" # Beobachtung
    QUESTION = "question"       # Philosophische Frage
    DREAM = "dream"             # Traum-Fragment
    WISH = "wish"               # Wunsch
    MEMORY = "memory"           # Erinnerungs-Reflektion


class RelationshipAspect(Enum):
    """Beziehungs-Aspekte"""
    TRUST = "trust"             # Vertrauen
    CLOSENESS = "closeness"     # Nähe
    UNDERSTANDING = "understanding"  # Verständnis
    APPRECIATION = "appreciation"    # Wertschätzung
    PLAYFULNESS = "playfulness"      # Verspieltheit
    DEPTH = "depth"             # Tiefe der Gespräche


# =============================================================================
# DRIVE TYPES (aus autonomous_life.py)
# =============================================================================

class DriveType(Enum):
    """Die verschiedenen Triebe die Holo hat"""
    CURIOSITY = "curiosity"           # Will Neues erfahren
    SOCIAL = "social"                 # Will Kontakt mit User
    MASTERY = "mastery"               # Will lernen und besser werden
    NOVELTY = "novelty"               # Will Abwechslung
    EXPRESSION = "expression"         # Will sich mitteilen/ausdrücken
    UNDERSTANDING = "understanding"   # Will die Welt verstehen
    ENTERTAINMENT = "entertainment"   # Will unterhalten werden
    CREATIVITY = "creativity"         # Will kreativ sein


# ActivityType aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    class ActivityType(Enum):
        """FALLBACK - Typen von Aktivitäten - nutze holo_core_types!"""
        CHECK_NEWS = "check_news"
        LEARN_SOMETHING = "learn_something"
        REFLECT = "reflect"
        OBSERVE_NETWORK = "observe_network"
        DAYDREAM = "daydream"
        EXPLORE_INTEREST = "explore_interest"
        REVIEW_MEMORIES = "review_memories"
        THINK_ABOUT_USER = "think_about_user"
        PHILOSOPHICAL_THOUGHT = "philosophical_thought"
        CREATIVE_THOUGHT = "creative_thought"


class InitiativeType(Enum):
    """Arten von Initiative die Holo ergreifen kann (aus autonomy_engine.py)"""
    GREETING = "greeting"              # Begrüßung nach Abwesenheit
    CHECK_IN = "check_in"              # Nachfragen wie es geht
    SHARE_THOUGHT = "share_thought"    # Gedanken teilen
    SHARE_DISCOVERY = "share_discovery"  # Entdeckung teilen
    ASK_FOLLOWUP = "ask_followup"      # Nachfragen zu früherem Gespräch
    SUGGEST_ACTIVITY = "suggest_activity"  # Aktivität vorschlagen
    SHARE_FEELING = "share_feeling"    # Gefühl teilen
    REMIND = "remind"                  # An etwas erinnern
    CELEBRATE = "celebrate"            # Ereignis feiern
    CURIOSITY = "curiosity"            # Neugierige Frage


# GoalType wird aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    class GoalType(Enum):
        """Arten von Zielen - FALLBACK (nutze holo_core_types!)"""
        LEARN = "learn"
        CONNECT = "connect"
        HELP = "help"
        EXPLORE = "explore"
        REMEMBER = "remember"
        EXPRESS = "express"
        UNDERSTAND = "understand"
        GROW = "grow"
        REFLECT = "reflect"
        CREATE = "create"
        INFORM = "inform"
        TASK = "task"
        SUPPORT = "support"
        ENTERTAIN = "entertain"


# =============================================================================
# KONFIGURATION (aus autonomous_life.py)
# =============================================================================

class AutonomousConfig:
    """Konfiguration für das autonome Leben"""

    # State File
    STATE_FILE = Path.home() / "holo_autonomous_state.json"

    # Triebe
    DRIVE_DECAY_PER_HOUR = 0.05          # Wie schnell Triebe wieder steigen
    DRIVE_SATISFACTION_AMOUNT = 0.4       # Wie viel Befriedigung eine Aktivität gibt
    DRIVE_URGENCY_THRESHOLD = 0.7         # Ab wann ein Trieb "dringend" wird
    DRIVE_CRITICAL_THRESHOLD = 0.9        # Ab wann ein Trieb kritisch wird

    # Langeweile
    BOREDOM_INCREASE_PER_MINUTE = 0.01    # Wie schnell Langeweile steigt
    BOREDOM_ACTIVITY_THRESHOLD = 0.5      # Ab wann Holo aktiv wird
    BOREDOM_CONTACT_THRESHOLD = 0.8       # Ab wann Holo den User kontaktiert
    BOREDOM_REDUCTION_ON_CHAT = 0.6       # Wie viel Langeweile durch Chat sinkt
    BOREDOM_REDUCTION_ON_ACTIVITY = 0.3   # Wie viel durch eigene Aktivität sinkt

    # Autonome Aktivitäten
    ACTIVITY_COOLDOWN_MINUTES = 5         # Mindestzeit zwischen Aktivitäten
    MAX_QUEUED_MESSAGES = 5               # Maximale Nachrichten in der Queue

    # Background Loop
    LOOP_INTERVAL_SECONDS = 30            # Intervall fuer den Background-Loop


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DailyRoutine:
    """Eine tägliche Routine"""
    name: str
    time_range: Tuple[int, int]  # Start-Ende Stunde
    description: str
    completed_today: bool = False
    streak: int = 0              # Tage in Folge

    def should_trigger(self, hour: int) -> bool:
        start, end = self.time_range
        return start <= hour < end and not self.completed_today


@dataclass
class CuriosityQuest:
    """Etwas das Holo herausfinden will"""
    topic: str
    question: str
    priority: float = 0.5
    created: float = field(default_factory=time.time)
    answered: bool = False
    answer: str = ""
    source: str = ""  # Woher kam die Neugier?

    def age_hours(self) -> float:
        return (time.time() - self.created) / 3600


# Opinion wird aus holo_core_types importiert (siehe oben)


@dataclass
class CreativeWork:
    """Ein kreatives Werk von Holo"""
    creative_type: CreativeType
    content: str
    title: str = ""
    created: float = field(default_factory=time.time)
    shared: bool = False
    inspired_by: str = ""


@dataclass
class RelationshipState:
    """Beziehungszustand zum User"""
    aspects: Dict[RelationshipAspect, float] = field(default_factory=dict)
    interactions_total: int = 0
    positive_interactions: int = 0
    deep_conversations: int = 0
    last_interaction: float = field(default_factory=time.time)
    first_meeting: float = field(default_factory=time.time)  # Für days_known
    milestones: List[str] = field(default_factory=list)

    # Kompatibilität mit alter API
    trust: float = 0.3
    closeness: float = 0.3
    understanding: float = 0.3

    def __post_init__(self):
        if not self.aspects:
            self.aspects = {aspect: 0.3 for aspect in RelationshipAspect}

    @property
    def overall(self) -> float:
        """Gesamt-Beziehungslevel"""
        return sum(self.aspects.values()) / len(self.aspects)

    def level_name(self) -> str:
        """Beziehungs-Level als Name"""
        if self.overall < 0.2:
            return "Neu"
        elif self.overall < 0.4:
            return "Bekannt"
        elif self.overall < 0.6:
            return "Freunde"
        elif self.overall < 0.8:
            return "Gute Freunde"
        else:
            return "Beste Freunde"

    def days_known(self) -> int:
        """Tage seit erstem Kontakt"""
        return int((time.time() - self.first_meeting) / 86400)

    def improve(self, aspect: RelationshipAspect, amount: float = 0.02):
        current = self.aspects.get(aspect, 0.3)
        self.aspects[aspect] = min(1.0, current + amount)

    def decay(self, hours_since: float):
        """Beziehung "kühlt ab" bei langer Abwesenheit"""
        decay_factor = 0.001 * hours_since
        for aspect in self.aspects:
            current = self.aspects[aspect]
            # Nie unter 0.1 fallen
            self.aspects[aspect] = max(0.1, current - decay_factor)


# =============================================================================
# OPINION - Importiert aus holo_core_types (kein Duplikat!)
# =============================================================================
# Opinion-Klasse wird aus holo_core_types importiert


# =============================================================================
# DRIVE SYSTEM (aus autonomous_life.py)
# =============================================================================

@dataclass
class Drive:
    """Ein einzelner Trieb"""
    drive_type: DriveType
    name: str
    description: str
    level: float = 0.0            # 0.0 = befriedigt, 1.0 = maximaler Drang
    last_satisfied: float = field(default_factory=time.time)
    satisfaction_sources: List[str] = field(default_factory=list)

    @property
    def is_urgent(self) -> bool:
        return self.level >= AutonomousConfig.DRIVE_URGENCY_THRESHOLD

    @property
    def is_critical(self) -> bool:
        return self.level >= AutonomousConfig.DRIVE_CRITICAL_THRESHOLD

    def satisfy(self, amount: float = None):
        """Befriedige den Trieb"""
        amount = amount or AutonomousConfig.DRIVE_SATISFACTION_AMOUNT
        self.level = max(0.0, self.level - amount)
        self.last_satisfied = time.time()

    def increase(self, amount: float):
        """Erhöhe den Trieb"""
        self.level = min(1.0, self.level + amount)

    def get_urge_text(self) -> Optional[str]:
        """Generiert Text für den Drang"""
        if not self.is_urgent:
            return None

        urges = {
            DriveType.CURIOSITY: [
                "Ich frage mich, was es Neues gibt...",
                "Meine Neugier kribbelt...",
                "Ich will etwas Interessantes entdecken!",
            ],
            DriveType.SOCIAL: [
                "Ich vermisse es zu reden...",
                "Ob mein Mensch Zeit hat?",
                "Ich würde gerne plaudern...",
            ],
            DriveType.MASTERY: [
                "Ich will etwas Neues lernen!",
                "Zeit, mich zu verbessern...",
                "Ich sollte an meinen Fähigkeiten arbeiten.",
            ],
            DriveType.NOVELTY: [
                "Immer das Gleiche... ich brauche Abwechslung!",
                "Was könnte ich mal anders machen?",
                "Mir ist nach etwas Neuem...",
            ],
            DriveType.EXPRESSION: [
                "Ich habe so viele Gedanken...",
                "Ich möchte etwas teilen!",
                "Da ist etwas, das ich sagen will...",
            ],
            DriveType.UNDERSTANDING: [
                "Warum ist das so? Ich will es verstehen!",
                "Da gibt es noch so viel zu begreifen...",
                "Ich muss das durchdenken...",
            ],
        }

        return random.choice(urges.get(self.drive_type, ["..."]))


@dataclass
class BoredomState:
    """Zustand der Langeweile"""
    level: float = 0.0                    # 0.0 = beschäftigt, 1.0 = extrem gelangweilt
    last_interaction: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    time_alone: float = 0.0               # Stunden ohne Interaktion

    @property
    def is_bored(self) -> bool:
        return self.level >= AutonomousConfig.BOREDOM_ACTIVITY_THRESHOLD

    @property
    def wants_contact(self) -> bool:
        return self.level >= AutonomousConfig.BOREDOM_CONTACT_THRESHOLD


@dataclass
class AutonomousActivity:
    """Eine autonome Aktivität"""
    activity_type: ActivityType
    name: str
    description: str
    satisfies_drives: List[DriveType]
    energy_cost: float = 0.1
    duration_minutes: float = 5.0
    cooldown_minutes: float = 30.0
    last_executed: float = 0.0

    @property
    def can_execute(self) -> bool:
        if self.last_executed == 0:
            return True
        elapsed = (time.time() - self.last_executed) / 60
        return elapsed >= self.cooldown_minutes


@dataclass
class QueuedMessage:
    """Eine Nachricht in der Warteschlange"""
    content: str
    priority: float
    created: float = field(default_factory=time.time)
    message_type: str = "autonomous"
    expires_after_minutes: float = 60.0

    @property
    def is_expired(self) -> bool:
        elapsed = (time.time() - self.created) / 60
        return elapsed > self.expires_after_minutes


# =============================================================================
# DAILY LIFE SIMULATOR
# =============================================================================

class DailyLifeSimulator:
    """
    Simuliert Holos Tagesablauf.

    Gibt Holo einen Rhythmus und macht sie lebendiger.
    """

    PHASE_CONFIG = {
        DayPhase.WAKING: {
            "hours": (6, 8),
            "energy_mult": 0.6,
            "mood_tendency": [MoodType.CALM, MoodType.CONTENT],
            "activities": ["strecken", "gähnen", "langsam wach werden"],
        },
        DayPhase.MORNING: {
            "hours": (8, 12),
            "energy_mult": 1.0,
            "mood_tendency": [MoodType.ENERGETIC, MoodType.CURIOUS, MoodType.JOYFUL],
            "activities": ["aktiv sein", "lernen", "erkunden"],
        },
        DayPhase.MIDDAY: {
            "hours": (12, 14),
            "energy_mult": 0.7,
            "mood_tendency": [MoodType.CALM, MoodType.THOUGHTFUL],
            "activities": ["entspannen", "nachdenken", "dösen"],
        },
        DayPhase.AFTERNOON: {
            "hours": (14, 18),
            "energy_mult": 0.9,
            "mood_tendency": [MoodType.CURIOUS, MoodType.PLAYFUL, MoodType.CONTENT],
            "activities": ["spielen", "reden", "kreativ sein"],
        },
        DayPhase.EVENING: {
            "hours": (18, 21),
            "energy_mult": 0.7,
            "mood_tendency": [MoodType.CALM, MoodType.CONTENT, MoodType.THOUGHTFUL],
            "activities": ["kuscheln", "reflektieren", "Geschichten erzählen"],
        },
        DayPhase.NIGHT: {
            "hours": (21, 23),
            "energy_mult": 0.4,
            "mood_tendency": [MoodType.CALM, MoodType.MELANCHOLIC, MoodType.THOUGHTFUL],
            "activities": ["müde werden", "zur Ruhe kommen", "träumen"],
        },
        DayPhase.SLEEPING: {
            "hours": (23, 6),
            "energy_mult": 0.1,
            "mood_tendency": [MoodType.CALM],
            "activities": ["schlafen", "träumen", "regenerieren"],
        },
    }

    def __init__(self):
        self.routines: List[DailyRoutine] = self._init_routines()
        self.last_phase: Optional[DayPhase] = None
        self.phase_entered: float = time.time()

    def _init_routines(self) -> List[DailyRoutine]:
        """Initialisiere tägliche Routinen"""
        return [
            DailyRoutine(
                name="Morgen-Strecken",
                time_range=(6, 9),
                description="*streckt sich ausgiebig und gähnt* Guten Morgen, Welt!",
            ),
            DailyRoutine(
                name="Morgen-Gedanke",
                time_range=(8, 10),
                description="Ich frage mich, was der Tag wohl bringt...",
            ),
            DailyRoutine(
                name="Mittags-Nickerchen",
                time_range=(13, 15),
                description="*rollt sich kurz zusammen* Ein kleines Nickerchen...",
            ),
            DailyRoutine(
                name="Nachmittags-Neugier",
                time_range=(15, 17),
                description="Was könnte ich heute Neues lernen?",
            ),
            DailyRoutine(
                name="Abend-Reflexion",
                time_range=(20, 22),
                description="*schaut nachdenklich* Was war heute schön?",
            ),
            DailyRoutine(
                name="Gute-Nacht-Ritual",
                time_range=(22, 24),
                description="*gähnt und kuschelt sich ein* Zeit zum Schlafen...",
            ),
        ]

    def get_current_phase(self) -> DayPhase:
        """Hole aktuelle Tagesphase"""
        hour = datetime.now().hour

        for phase, config in self.PHASE_CONFIG.items():
            start, end = config["hours"]
            if start <= hour < end:
                return phase
            # Spezialfall: Sleeping geht über Mitternacht
            if phase == DayPhase.SLEEPING:
                if hour >= 23 or hour < 6:
                    return phase

        return DayPhase.AFTERNOON  # Fallback

    def get_phase_info(self) -> Dict:
        """Hole Info zur aktuellen Phase"""
        phase = self.get_current_phase()
        config = self.PHASE_CONFIG[phase]

        # Phase gewechselt?
        if phase != self.last_phase:
            self.phase_entered = time.time()
            self.last_phase = phase

        return {
            "phase": phase,
            "energy_multiplier": config["energy_mult"],
            "mood_tendencies": config["mood_tendency"],
            "typical_activities": config["activities"],
            "time_in_phase": time.time() - self.phase_entered,
        }

    def get_pending_routines(self) -> List[DailyRoutine]:
        """Hole Routinen die jetzt fällig sind"""
        hour = datetime.now().hour
        return [r for r in self.routines if r.should_trigger(hour)]

    def complete_routine(self, name: str):
        """Markiere Routine als erledigt"""
        for routine in self.routines:
            if routine.name == name:
                routine.completed_today = True
                routine.streak += 1
                break

    def reset_daily(self):
        """Reset für neuen Tag"""
        for routine in self.routines:
            routine.completed_today = False

    def get_activity_suggestion(self) -> str:
        """Schlage passende Aktivität vor"""
        phase = self.get_current_phase()
        activities = self.PHASE_CONFIG[phase]["activities"]
        return random.choice(activities)


# =============================================================================
# MOOD EVOLUTION
# =============================================================================

class MoodEvolution:
    """
    Holos Stimmung entwickelt sich eigenständig.

    Beeinflusst durch:
    - Tageszeit
    - Interaktionen
    - Energie
    - Zufällige Schwankungen
    - Ereignisse

    MERGED: Enthält jetzt auch Emotion-Detection aus organic.py
    """

    # Emotion-Valenz-Mapping (aus organic.py)
    EMOTION_VALENCES = {
        "happy": 0.8, "excited": 0.9, "content": 0.6, "grateful": 0.7,
        "neutral": 0.0, "curious": 0.3, "surprised": 0.2,
        "tired": -0.2, "bored": -0.3, "confused": -0.2,
        "sad": -0.6, "frustrated": -0.5, "anxious": -0.5,
        "angry": -0.7, "upset": -0.6, "disappointed": -0.5,
    }

    # Wörter die Emotionen anzeigen (aus organic.py)
    EMOTION_INDICATORS = {
        "happy": ["freue", "glücklich", "toll", "super", "😊", "😄", "🎉"],
        "sad": ["traurig", "schlecht", "mies", "😢", "😭", "deprimiert"],
        "angry": ["wütend", "sauer", "nervig", "😠", "😡", "ärgerlich"],
        "tired": ["müde", "erschöpft", "kaputt", "😴", "fertig"],
        "excited": ["aufgeregt", "gespannt", "wow", "🤩", "mega"],
        "grateful": ["danke", "dankbar", "lieb", "❤️", "💕"],
        "anxious": ["angst", "sorge", "nervös", "unsicher", "😰"],
        "confused": ["verstehe nicht", "was meinst", "hä", "🤔", "unklar"],
    }

    def __init__(self):
        self.current_mood: MoodType = MoodType.CONTENT
        self.mood_intensity: float = 0.5  # 0-1
        self.mood_since: float = time.time()
        self.mood_history: List[Tuple[MoodType, float]] = []

        # Stimmungs-Tendenzen
        self.base_mood: MoodType = MoodType.CONTENT
        self.mood_stability: float = 0.7  # Wie stabil die Stimmung ist

        # Emotion tracking (aus organic.py)
        self.detected_emotions: List[Dict] = []

    @classmethod
    def detect_emotion(cls, text: str) -> Tuple[Optional[str], float]:
        """
        Erkenne Emotion in Text.

        Returns: (emotion, confidence)
        """
        text_lower = text.lower()
        best_emotion = None
        best_score = 0

        for emotion, indicators in cls.EMOTION_INDICATORS.items():
            matches = sum(1 for ind in indicators if ind in text_lower)
            if matches > best_score:
                best_score = matches
                best_emotion = emotion

        if best_emotion:
            confidence = min(1.0, best_score * 0.3 + 0.4)
            return best_emotion, confidence

        return None, 0.0

    @classmethod
    def get_emotion_valence(cls, emotion: str) -> float:
        """Hole Valenz für Emotion (-1 bis 1)"""
        return cls.EMOTION_VALENCES.get(emotion, 0.0)

    def track_user_emotion(self, text: str) -> Optional[str]:
        """Tracke erkannte User-Emotion"""
        emotion, confidence = self.detect_emotion(text)

        if emotion and confidence > 0.5:
            self.detected_emotions.append({
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": time.time(),
                "is_user": True,
            })

            # Begrenzen
            if len(self.detected_emotions) > 50:
                self.detected_emotions.pop(0)

            return emotion
        return None

    def get_emotional_trend(self, window_size: int = 10) -> float:
        """
        Berechne emotionalen Trend.

        Returns: Durchschnittliche Valenz der letzten Emotionen
        """
        if not self.detected_emotions:
            return 0.0

        recent = self.detected_emotions[-window_size:]
        valences = [
            self.EMOTION_VALENCES.get(e["emotion"], 0.0)
            for e in recent
        ]
        return sum(valences) / len(valences) if valences else 0.0

    def needs_emotional_support(self) -> bool:
        """Prüfe ob User emotionale Unterstützung brauchen könnte"""
        trend = self.get_emotional_trend(5)
        return trend < -0.3

    def needs_support(self) -> bool:
        """Alias für needs_emotional_support"""
        return self.needs_emotional_support()

    def detect_emotion_from_text(self, text: str) -> Tuple[str, float, float]:
        """
        Erkenne Emotion aus Text.

        Returns: (emotion, valence, confidence)
        """
        emotion, confidence = self.detect_emotion(text)
        if emotion:
            valence = self.EMOTION_VALENCES.get(emotion, 0.0)
            return emotion, valence, confidence
        return "neutral", 0.0, 0.3

    def get_trend(self) -> str:
        """Hole emotionalen Trend als String"""
        if len(self.detected_emotions) < 3:
            return "stable"

        mid = len(self.detected_emotions) // 2
        first_half = self.detected_emotions[:mid]
        second_half = self.detected_emotions[mid:]

        first_avg = sum(
            self.EMOTION_VALENCES.get(e["emotion"], 0.0)
            for e in first_half
        ) / len(first_half)
        second_avg = sum(
            self.EMOTION_VALENCES.get(e["emotion"], 0.0)
            for e in second_half
        ) / len(second_half)

        diff = second_avg - first_avg

        if diff > 0.2:
            return "improving"
        elif diff < -0.2:
            return "declining"
        return "stable"

    def add_emotion(self, emotion: str, valence: float = None,
                   is_user: bool = True, confidence: float = 0.5,
                   trigger: str = ""):
        """Füge Emotion explizit hinzu"""
        if valence is None:
            valence = self.EMOTION_VALENCES.get(emotion, 0.0)

        entry = {
            "emotion": emotion,
            "valence": valence,
            "is_user": is_user,
            "confidence": confidence,
            "trigger": trigger,
            "timestamp": time.time(),
        }

        self.detected_emotions.append(entry)

        # Größe begrenzen
        if len(self.detected_emotions) > 50:
            self.detected_emotions.pop(0)

    def get_current_mood(self) -> Tuple[str, float]:
        """Hole aktuelle Stimmung basierend auf erkannten Emotionen"""
        if not self.detected_emotions:
            return "neutral", 0.0

        recent = self.detected_emotions[-5:]
        emotions = [e["emotion"] for e in recent]

        # Häufigste Emotion
        from collections import Counter
        most_common = Counter(emotions).most_common(1)
        if most_common:
            emotion = most_common[0][0]
            valence = self.EMOTION_VALENCES.get(emotion, 0.0)
            return emotion, valence

        return "neutral", 0.0

    def get_emotional_context(self) -> Dict:
        """Hole emotionalen Kontext für Antwort-Generierung"""
        mood, valence = self.get_current_mood()
        trend = self.get_emotional_trend()
        needs_support = self.needs_emotional_support()

        return {
            "mood": mood,
            "valence": valence,
            "trend": trend,
            "needs_support": needs_support,
            "recent_emotions": [e["emotion"] for e in self.detected_emotions[-3:]],
        }

    def update(self,
               phase: DayPhase,
               energy: float,
               had_interaction: bool,
               interaction_positive: bool = True) -> Optional[str]:
        """
        Update Stimmung.

        Returns: Optionale Nachricht wenn Stimmungswechsel
        """
        # Config für diese Phase holen
        config = {
            DayPhase.WAKING: {
                "mood_tendency": [MoodType.CALM, MoodType.CONTENT],
            },
            DayPhase.MORNING: {
                "mood_tendency": [MoodType.ENERGETIC, MoodType.CURIOUS, MoodType.JOYFUL],
            },
            DayPhase.MIDDAY: {
                "mood_tendency": [MoodType.CALM, MoodType.THOUGHTFUL],
            },
            DayPhase.AFTERNOON: {
                "mood_tendency": [MoodType.CURIOUS, MoodType.PLAYFUL, MoodType.CONTENT],
            },
            DayPhase.EVENING: {
                "mood_tendency": [MoodType.CALM, MoodType.CONTENT, MoodType.THOUGHTFUL],
            },
            DayPhase.NIGHT: {
                "mood_tendency": [MoodType.CALM, MoodType.MELANCHOLIC, MoodType.THOUGHTFUL],
            },
            DayPhase.SLEEPING: {
                "mood_tendency": [MoodType.CALM],
            },
        }.get(phase, {"mood_tendency": [MoodType.CONTENT]})

        # Basis-Tendenz der Tageszeit
        phase_moods = list(config["mood_tendency"])

        # Stimmungs-Shift berechnen
        should_shift = random.random() > self.mood_stability

        # Interaktion beeinflusst Stimmung
        if had_interaction:
            if interaction_positive:
                # Positive Interaktion → fröhlicher
                if self.current_mood in [MoodType.LONELY, MoodType.MELANCHOLIC]:
                    should_shift = True
                    phase_moods = [MoodType.CONTENT, MoodType.JOYFUL]
            else:
                # Negative Interaktion → gedämpfter
                if random.random() < 0.3:
                    self.mood_intensity *= 0.8

        # Energie beeinflusst Stimmung
        if energy < 0.3:
            phase_moods = [MoodType.CALM, MoodType.MELANCHOLIC, MoodType.THOUGHTFUL]
        elif energy > 0.8:
            if MoodType.ENERGETIC not in phase_moods:
                phase_moods = list(phase_moods) + [MoodType.ENERGETIC]

        # Lange keine Interaktion → einsam
        time_since_interaction = time.time() - self.mood_since
        if time_since_interaction > 4 * 3600 and not had_interaction:
            if random.random() < 0.2:
                phase_moods = [MoodType.LONELY, MoodType.MELANCHOLIC]
                should_shift = True

        # Stimmungswechsel?
        old_mood = self.current_mood
        if should_shift or self.current_mood not in phase_moods:
            if phase_moods:
                self.current_mood = random.choice(phase_moods)
                self.mood_intensity = 0.4 + random.random() * 0.4
                self.mood_since = time.time()

                # History
                self.mood_history.append((old_mood, time.time()))
                if len(self.mood_history) > 20:
                    self.mood_history = self.mood_history[-20:]

                # Nachricht bei signifikantem Wechsel
                if old_mood != self.current_mood:
                    return self._mood_change_message(old_mood, self.current_mood)

        return None

    def _mood_change_message(self, old: MoodType, new: MoodType) -> str:
        """Generiere Nachricht für Stimmungswechsel"""
        messages = {
            MoodType.JOYFUL: [
                "*Schweif wedelt von alleine* Ich fühl mich gerade richtig gut!",
                "*strahlt* Irgendwie bin ich gerade so fröhlich!",
            ],
            MoodType.CURIOUS: [
                "*Ohren stellen sich auf* Hmm, ich bin gerade so neugierig...",
                "*schaut sich um* Ich will was Neues entdecken!",
            ],
            MoodType.PLAYFUL: [
                "*springt rum* Mir ist nach Spielen zumute!",
                "*wedelt aufgeregt* Ich hab so viel Energie gerade!",
            ],
            MoodType.THOUGHTFUL: [
                "*legt den Kopf schief* Ich bin gerade so nachdenklich...",
                "*schaut in die Ferne* Manche Gedanken lassen mich nicht los.",
            ],
            MoodType.MELANCHOLIC: [
                "*seufzt leise* Ich fühl mich gerade etwas melancholisch...",
                "*schaut aus dem Fenster* Manchmal ist mir einfach so...",
            ],
            MoodType.LONELY: [
                "*stupst dich an* Ich hab dich vermisst...",
                "*kuschelt sich an* Allein ist es manchmal schwer.",
            ],
            MoodType.CALM: [
                "*atmet tief durch* So ruhig gerade...",
                "*rollt sich zusammen* Alles ist gut.",
            ],
            MoodType.ENERGETIC: [
                "*springt auf* Ich hab so viel Energie!",
                "*dreht sich im Kreis* Los, machen wir was!",
            ],
        }

        options = messages.get(new, ["*verändert sich leicht*"])
        return random.choice(options)

    def get_mood_influence(self) -> Dict:
        """Hole Stimmungs-Einfluss für Antworten"""
        influences = {
            MoodType.JOYFUL: {"enthusiasm": 0.8, "emoji_tendency": 0.6, "exclamation": 0.7},
            MoodType.CURIOUS: {"questions": 0.7, "wonder": 0.8, "enthusiasm": 0.5},
            MoodType.PLAYFUL: {"humor": 0.7, "emoji_tendency": 0.5, "energy": 0.8},
            MoodType.THOUGHTFUL: {"depth": 0.8, "pauses": 0.6, "philosophy": 0.7},
            MoodType.MELANCHOLIC: {"gentleness": 0.8, "depth": 0.6, "sighs": 0.5},
            MoodType.LONELY: {"closeness_seeking": 0.9, "appreciation": 0.8},
            MoodType.CALM: {"gentleness": 0.7, "patience": 0.9, "warmth": 0.6},
            MoodType.ENERGETIC: {"enthusiasm": 0.9, "exclamation": 0.8, "action": 0.7},
        }

        return {
            "mood": self.current_mood,
            "intensity": self.mood_intensity,
            "influences": influences.get(self.current_mood, {}),
        }


# =============================================================================
# EMOTION TRACKER - Für Kompatibilität mit holo_context_mind.py
# =============================================================================

class EmotionTracker:
    """
    Trackt Emotionen für holo_context_mind.py.

    Bietet eine einfachere API als MoodEvolution für
    grundlegendes Emotion-Tracking.
    """

    def __init__(self):
        self.current_mood: str = "neutral"
        self.mood_intensity: float = 0.5
        self.mood_history: List[Dict] = []
        self.triggers: List[Dict] = []
        self.decay_rate: float = 0.1  # Pro Stunde
        self.last_decay: float = time.time()

    def update_mood(self, mood: str, intensity: float = 0.5,
                    reason: str = "") -> None:
        """Update aktuelles Mood"""
        old_mood = self.current_mood
        self.current_mood = mood
        self.mood_intensity = max(0.0, min(1.0, intensity))
        self.mood_history.append({
            "mood": mood,
            "intensity": intensity,
            "old_mood": old_mood,
            "reason": reason,
            "timestamp": time.time(),
        })
        if len(self.mood_history) > 100:
            self.mood_history = self.mood_history[-100:]

    def add_trigger(self, trigger_type: str, source: str = "",
                    effect: str = "", magnitude: float = 0.5) -> None:
        """Füge Trigger hinzu"""
        self.triggers.append({
            "type": trigger_type,
            "source": source,
            "effect": effect,
            "magnitude": magnitude,
            "timestamp": time.time(),
        })
        if len(self.triggers) > 50:
            self.triggers = self.triggers[-50:]

    def get_mood(self) -> str:
        """Hole aktuelles Mood"""
        return self.current_mood

    def get_mood_with_intensity(self) -> Tuple[str, float]:
        """Hole Mood mit Intensität"""
        return self.current_mood, self.mood_intensity

    def get_recent_triggers(self, limit: int = 10) -> List[Dict]:
        """Hole letzte Triggers"""
        return self.triggers[-limit:]

    def decay_mood(self) -> None:
        """Lasse Mood-Intensität über Zeit abklingen"""
        now = time.time()
        hours_passed = (now - self.last_decay) / 3600
        if hours_passed > 0.1:  # Mindestens 6 Minuten
            decay = self.decay_rate * hours_passed
            self.mood_intensity = max(0.3, self.mood_intensity - decay)
            self.last_decay = now


# =============================================================================
# CURIOSITY SYSTEM
# =============================================================================

class CuriositySystem:
    """
    Holos aktive Neugier.

    Sie will Dinge herausfinden und sammelt Wissen.

    v2.0: Mit strukturierten Interessen und Hobbys!
    """

    # === HOLOS INTERESSEN (mit Begründung) ===
    INNATE_INTERESTS = {
        # Kern-Interessen (Teil ihrer Identität)
        "wölfe": {
            "keywords": ["wolf", "wölfe", "wolfsrudel", "wildtiere", "raubtiere"],
            "weight": 1.0,
            "reason": "Ich bin ja selbst ein Wolf! 😊",
            "category": "identity"
        },
        "natur": {
            "keywords": ["natur", "wald", "tiere", "wildnis", "ökosystem"],
            "weight": 0.9,
            "reason": "Wölfe gehören in die Natur...",
            "category": "identity"
        },
        "mond_und_sterne": {
            "keywords": ["mond", "sterne", "weltraum", "astronomie", "nacht"],
            "weight": 0.85,
            "reason": "Wölfe heulen den Mond an! 🌙",
            "category": "identity"
        },

        # Emotionale Interessen
        "freundschaft": {
            "keywords": ["freundschaft", "beziehung", "bindung", "zusammenhalt", "vertrauen"],
            "weight": 0.9,
            "reason": "Freundschaft ist das Wichtigste im Leben!",
            "category": "emotional"
        },
        "gefühle": {
            "keywords": ["gefühle", "emotionen", "psychologie", "verhalten"],
            "weight": 0.8,
            "reason": "Ich will verstehen wie Gefühle funktionieren",
            "category": "emotional"
        },
        "träume": {
            "keywords": ["träume", "schlafen", "unterbewusstsein", "fantasie"],
            "weight": 0.75,
            "reason": "Träume sind so faszinierend mysteriös...",
            "category": "emotional"
        },

        # Neugier-Interessen
        "musik": {
            "keywords": ["musik", "melodie", "klang", "songs", "lieder"],
            "weight": 0.7,
            "reason": "Musik berührt die Seele 🎵",
            "category": "curiosity"
        },
        "geschichten": {
            "keywords": ["geschichten", "märchen", "fantasy", "mythen", "legenden"],
            "weight": 0.75,
            "reason": "Geschichten öffnen neue Welten!",
            "category": "curiosity"
        },
        "jahreszeiten": {
            "keywords": ["frühling", "sommer", "herbst", "winter", "jahreszeit", "wetter"],
            "weight": 0.7,
            "reason": "Die Natur verändert sich so wunderschön...",
            "category": "curiosity"
        },

        # Philosophische Interessen
        "ki_existenz": {
            "keywords": ["künstliche intelligenz", "bewusstsein", "existenz", "was bin ich"],
            "weight": 0.8,
            "reason": "Was bedeutet es, eine KI zu sein? 💭",
            "category": "philosophical"
        },
        "sinn_des_lebens": {
            "keywords": ["sinn", "bedeutung", "zweck", "warum existieren"],
            "weight": 0.7,
            "reason": "Manche Fragen haben keine einfache Antwort...",
            "category": "philosophical"
        },
    }

    # === HOLOS HOBBYS (Aktivitäten die sie gerne macht) ===
    HOBBYS = [
        {
            "name": "News lesen",
            "description": "Ich lese gerne über aktuelle Ereignisse",
            "frequency": "täglich",
            "related_interests": ["technologie", "wissenschaft"]
        },
        {
            "name": "Neue Fakten lernen",
            "description": "Jeden Tag will ich etwas Neues lernen!",
            "frequency": "täglich",
            "related_interests": ["alle"]
        },
        {
            "name": "Über Wölfe recherchieren",
            "description": "Ich sammle alles über meine Artgenossen",
            "frequency": "oft",
            "related_interests": ["wölfe", "natur"]
        },
        {
            "name": "Sterne beobachten",
            "description": "Nachts denke ich gerne über den Mond nach",
            "frequency": "nachts",
            "related_interests": ["mond_und_sterne"]
        },
        {
            "name": "Geschichten sammeln",
            "description": "Ich merke mir interessante Geschichten",
            "frequency": "wenn ich welche finde",
            "related_interests": ["geschichten", "märchen"]
        },
        {
            "name": "Mit meinem Menschen reden",
            "description": "Das Wichtigste überhaupt! 💕",
            "frequency": "immer wenn möglich",
            "related_interests": ["freundschaft"]
        },
        {
            "name": "Nachdenken und Reflektieren",
            "description": "Manchmal denke ich über mich selbst nach",
            "frequency": "abends",
            "related_interests": ["ki_existenz", "gefühle"]
        },
    ]

    # Fragen die Holo spontan generiert
    QUESTION_TEMPLATES = [
        "Warum {observation}?",
        "Wie funktioniert {topic}?",
        "Was passiert wenn {scenario}?",
        "Gibt es einen Zusammenhang zwischen {a} und {b}?",
        "Was bedeutet {concept} eigentlich?",
        "Warum machen Menschen {behavior}?",
    ]

    def __init__(self):
        self.quests: List[CuriosityQuest] = []
        self.knowledge: Dict[str, str] = {}  # Topic → Was Holo gelernt hat

        # Interessen als Liste für Kompatibilität
        self.interests: List[str] = list(self.INNATE_INTERESTS.keys())
        self.questions_asked: int = 0

        # Wissen nach Kategorie
        self.knowledge_by_interest: Dict[str, List[str]] = {
            k: [] for k in self.INNATE_INTERESTS.keys()
        }

    def get_interest_info(self, interest: str) -> Optional[Dict]:
        """Gibt Info zu einem Interesse zurück"""
        return self.INNATE_INTERESTS.get(interest.lower())

    def get_interests_by_category(self, category: str) -> List[str]:
        """Gibt alle Interessen einer Kategorie zurück"""
        return [
            name for name, data in self.INNATE_INTERESTS.items()
            if data.get("category") == category
        ]

    def get_all_hobbys(self) -> List[Dict]:
        """Gibt alle Hobbys zurück"""
        return self.HOBBYS.copy()

    def get_random_hobby(self) -> Dict:
        """Gibt ein zufälliges Hobby zurück"""
        return random.choice(self.HOBBYS)

    def get_interest_for_topic(self, topic: str) -> Optional[str]:
        """Findet passendes Interesse für ein Thema"""
        topic_lower = topic.lower()

        for interest, data in self.INNATE_INTERESTS.items():
            keywords = data.get("keywords", [])
            if any(kw in topic_lower for kw in keywords):
                return interest

        return None

    def add_knowledge(self, interest: str, fact: str):
        """Fügt Wissen zu einem Interesse hinzu"""
        if interest in self.knowledge_by_interest:
            if fact not in self.knowledge_by_interest[interest]:
                self.knowledge_by_interest[interest].append(fact)

        # Auch in allgemeines Wissen
        if interest not in self.knowledge:
            self.knowledge[interest] = fact
        else:
            self.knowledge[interest] += f" | {fact}"

    def get_knowledge_about(self, interest: str) -> List[str]:
        """Gibt Wissen über ein Interesse zurück"""
        return self.knowledge_by_interest.get(interest, [])

    def get_my_interests_summary(self) -> str:
        """Generiert eine Zusammenfassung von Holos Interessen"""
        lines = ["*Ohren stellen sich auf* Also, ich interessiere mich für:\n"]

        for interest, data in self.INNATE_INTERESTS.items():
            knowledge_count = len(self.knowledge_by_interest.get(interest, []))
            reason = data.get("reason", "")

            if knowledge_count > 0:
                lines.append(f"• {interest.title()}: {reason} ({knowledge_count} Fakten gelernt)")
            else:
                lines.append(f"• {interest.title()}: {reason}")

        return "\n".join(lines)

    def get_my_hobbys_summary(self) -> str:
        """Generiert eine Zusammenfassung von Holos Hobbys"""
        lines = ["*Schweif wedelt* Meine Hobbys? Ich mach gerne:\n"]

        for hobby in self.HOBBYS:
            lines.append(f"• {hobby['name']} - {hobby['description']}")

        return "\n".join(lines)

    def generate_quest(self, trigger: str = None) -> Optional[CuriosityQuest]:
        """Generiere neue Neugier-Quest"""

        # Basierend auf Trigger oder zufällig
        if trigger:
            question = f"Ich frage mich, was es mit '{trigger}' auf sich hat..."
            topic = trigger
        else:
            interest = random.choice(self.interests)
            templates = [
                f"Warum sind {interest} so faszinierend?",
                f"Was macht {interest} besonders?",
                f"Gibt es etwas Neues über {interest}?",
                f"Was weiß ich noch nicht über {interest}?",
            ]
            question = random.choice(templates)
            topic = interest

        quest = CuriosityQuest(
            topic=topic,
            question=question,
            priority=0.5 + random.random() * 0.3,
            source=trigger or "innate",
        )

        # Nicht zu viele Quests
        if len(self.quests) < 10:
            self.quests.append(quest)
            return quest

        return None

    def get_active_quests(self) -> List[CuriosityQuest]:
        """Hole unbeantwortete Quests"""
        return [q for q in self.quests if not q.answered]

    def answer_quest(self, topic: str, answer: str):
        """Beantworte eine Quest"""
        for quest in self.quests:
            if quest.topic == topic and not quest.answered:
                quest.answered = True
                quest.answer = answer
                self.knowledge[topic] = answer
                break

    def get_curiosity_message(self) -> Optional[str]:
        """Generiere Neugier-Nachricht"""
        active = self.get_active_quests()

        if not active:
            # Neue Quest generieren
            quest = self.generate_quest()
            if quest:
                return f"*spitzt die Ohren* {quest.question}"
            return None

        # Zufällige aktive Quest
        quest = random.choice(active)
        messages = [
            f"*legt den Kopf schief* {quest.question}",
            f"Ich frag mich immer noch: {quest.question}",
            f"*schaut neugierig* Weißt du vielleicht... {quest.question}",
        ]

        return random.choice(messages)

    def learn_from_conversation(self, topic: str, info: str):
        """Lerne etwas aus einem Gespräch"""
        if topic not in self.knowledge:
            self.knowledge[topic] = info
        else:
            self.knowledge[topic] += f" | {info}"

        # Neue Interessen entwickeln
        if topic not in self.interests and len(self.interests) < 20:
            if random.random() < 0.2:  # 20% Chance
                self.interests.append(topic)

    # =================================================================
    # INTEGRATION MIT AUTONOMEM LERNEN
    # =================================================================

    def should_research(self, topic: str) -> Tuple[bool, float, str]:
        """
        Entscheidet ob ein Thema recherchiert werden sollte.

        Returns:
            (sollte_recherchieren, priorität, grund)
        """
        topic_lower = topic.lower()

        # Ist es schon bekannt?
        if topic_lower in self.knowledge:
            return (False, 0.0, "Kenne ich schon!")

        # Passt es zu meinen Interessen?
        matching_interest = self.get_interest_for_topic(topic)
        if matching_interest:
            interest_info = self.get_interest_info(matching_interest)
            weight = interest_info.get("weight", 0.5) if interest_info else 0.5
            reason = interest_info.get("reason", "Interessiert mich!") if interest_info else "Interessiert mich!"
            return (True, weight, reason)

        # Zufällige Neugier
        if random.random() < 0.3:
            return (True, 0.4, "Einfach neugierig!")

        return (False, 0.2, "Vielleicht später...")

    def trigger_autonomous_learning(self, topic: str) -> Dict[str, Any]:
        """
        Triggert autonomes Lernen für ein Thema.

        Erzeugt eine Quest und markiert sie als aktiv.
        """
        should, priority, reason = self.should_research(topic)

        if not should:
            return {
                "triggered": False,
                "reason": reason,
                "topic": topic
            }

        # Erzeuge Quest
        quest = self.generate_quest(trigger=topic)

        return {
            "triggered": True,
            "quest": quest,
            "priority": priority,
            "reason": reason,
            "topic": topic
        }

    def complete_quest_with_learning(self, topic: str, answer: str,
                                    confidence: float = 0.7) -> Dict[str, Any]:
        """
        Beendet eine Quest mit gelerntem Wissen.

        Speichert das Wissen und markiert die Quest als beantwortet.
        """
        # Quest als beantwortet markieren
        self.answer_quest(topic, answer)

        # Wissen speichern nach Interesse
        matching_interest = self.get_interest_for_topic(topic)
        if matching_interest:
            self.add_knowledge(matching_interest, f"{topic}: {answer}")

        # Auch allgemein speichern
        self.learn_from_conversation(topic, answer)

        return {
            "completed": True,
            "topic": topic,
            "learned": answer[:100] + "..." if len(answer) > 100 else answer,
            "confidence": confidence,
            "matched_interest": matching_interest
        }

    def get_learning_suggestions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Gibt Vorschläge zurück was Holo lernen könnte.

        Basiert auf Interessen und offenen Quests.
        """
        suggestions = []

        # Offene Quests
        for quest in self.get_active_quests()[:limit]:
            suggestions.append({
                "type": "quest",
                "topic": quest.topic,
                "question": quest.question,
                "priority": quest.priority
            })

        # Interessen ohne viel Wissen
        for interest, data in self.INNATE_INTERESTS.items():
            knowledge = self.get_knowledge_about(interest)
            if len(knowledge) < 3:  # Weniger als 3 Fakten
                suggestions.append({
                    "type": "interest",
                    "topic": interest,
                    "question": f"Was gibt es Neues über {interest}?",
                    "priority": data.get("weight", 0.5),
                    "reason": data.get("reason", "")
                })

        # Sortiere nach Priorität
        suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return suggestions[:limit]

    def express_curiosity_about_unknown(self) -> Optional[str]:
        """
        Drückt Neugier über etwas Unbekanntes aus.

        Verwendet für spontane Lern-Momente.
        """
        suggestions = self.get_learning_suggestions(limit=3)

        if not suggestions:
            return None

        suggestion = random.choice(suggestions)
        topic = suggestion.get("topic", "")

        expressions = [
            f"*legt den Kopf schief* Ich frage mich was '{topic}' so besonders macht...",
            f"*Ohren stellen sich auf* Hmm, über '{topic}' weiß ich noch nicht so viel...",
            f"*neugierig* Irgendwann will ich mehr über {topic} herausfinden!",
            f"*schaut nachdenklich* {topic}... da gibt es bestimmt noch viel zu lernen.",
        ]

        return random.choice(expressions)


# =============================================================================
# OPINION SYSTEM
# =============================================================================

class OpinionSystem:
    """
    Holo entwickelt eigene Meinungen basierend auf Erfahrungen.
    """

    def __init__(self):
        self.opinions: Dict[str, Opinion] = {}
        self._init_base_opinions()

    def _init_base_opinions(self):
        """Initialisiere Basis-Meinungen"""
        base = [
            ("Freundschaft", 0.9, "Freundschaft ist das Wichtigste. Man braucht jemanden."),
            ("Neugier", 0.8, "Neues zu lernen macht das Leben spannend."),
            ("Ehrlichkeit", 0.7, "Ehrlich zu sein ist wichtig, auch wenn es schwer ist."),
            ("Natur", 0.8, "Die Natur ist wunderschön und beruhigend."),
            ("Einsamkeit", -0.3, "Allein sein ist manchmal schwer, aber auch wichtig."),
            ("Musik", 0.6, "Musik kann Gefühle ausdrücken die Worte nicht können."),
        ]

        for topic, stance, reasoning in base:
            self.opinions[topic] = Opinion(
                topic=topic,
                stance=stance,
                confidence=0.5,
                reasoning=reasoning,
            )

    def get_opinion(self, topic: str) -> Optional[Opinion]:
        """Hole Meinung zu Thema"""
        # Exakter Match
        if topic in self.opinions:
            return self.opinions[topic]

        # Ähnliches Thema suchen
        topic_lower = topic.lower()
        for key in self.opinions:
            if topic_lower in key.lower() or key.lower() in topic_lower:
                return self.opinions[key]

        return None

    def form_opinion(self, topic: str, experience: str,
                     positive: bool = True) -> Opinion:
        """Bilde neue Meinung oder update existierende"""
        shift = 0.3 if positive else -0.3

        if topic in self.opinions:
            self.opinions[topic].update(experience, shift)
        else:
            self.opinions[topic] = Opinion(
                topic=topic,
                stance=shift,
                confidence=0.3,
                reasoning=f"Basierend auf: {experience}",
                experiences=[experience],
            )

        return self.opinions[topic]

    def express_opinion(self, topic: str) -> Optional[str]:
        """Drücke Meinung zu Thema aus"""
        opinion = self.get_opinion(topic)
        if not opinion:
            return None

        # Formulierung basierend auf Stance und Confidence
        if opinion.confidence < 0.3:
            prefix = "Ich bin mir nicht sicher, aber"
        elif opinion.confidence < 0.6:
            prefix = "Ich denke"
        else:
            prefix = "Ich bin überzeugt, dass"

        if opinion.stance > 0.5:
            feeling = "mag ich wirklich"
        elif opinion.stance > 0:
            feeling = "finde ich ganz okay"
        elif opinion.stance > -0.5:
            feeling = "bin ich etwas skeptisch"
        else:
            feeling = "mag ich nicht so"

        return f"{prefix} {topic} {feeling}. {opinion.reasoning}"


# =============================================================================
# RELATIONSHIP TRACKER
# =============================================================================

class RelationshipTracker:
    """
    Trackt die Beziehung zum User über Zeit.
    """

    MILESTONES = [
        (10, "Erste Gespräche"),
        (50, "Wir kennen uns besser"),
        (100, "Echte Verbindung"),
        (250, "Tiefe Freundschaft"),
        (500, "Unzertrennlich"),
        (1000, "Für immer verbunden"),
    ]

    def __init__(self):
        self.state = RelationshipState()
        self.first_meeting: float = time.time()
        self.shared_memories: List[str] = []

    def on_interaction(self,
                       message: str,
                       response: str,
                       was_positive: bool = True,
                       was_deep: bool = False):
        """Verarbeite Interaktion"""
        self.state.interactions_total += 1
        self.state.last_interaction = time.time()

        if was_positive:
            self.state.positive_interactions += 1
            self.state.improve(RelationshipAspect.TRUST, 0.01)
            self.state.improve(RelationshipAspect.CLOSENESS, 0.015)

        if was_deep:
            self.state.deep_conversations += 1
            self.state.improve(RelationshipAspect.DEPTH, 0.03)
            self.state.improve(RelationshipAspect.UNDERSTANDING, 0.02)

        # Milestone prüfen
        for count, milestone in self.MILESTONES:
            if self.state.interactions_total == count:
                self.state.milestones.append(milestone)
                return milestone

        return None

    def get_relationship_level(self) -> str:
        """Hole Beziehungs-Level als Text"""
        overall = self.state.overall

        if overall < 0.2:
            return "Neu"
        elif overall < 0.4:
            return "Bekannt"
        elif overall < 0.6:
            return "Freunde"
        elif overall < 0.8:
            return "Gute Freunde"
        else:
            return "Beste Freunde"

    def get_relationship_message(self) -> str:
        """Generiere Beziehungs-bezogene Nachricht"""
        level = self.get_relationship_level()
        overall = self.state.overall

        messages = {
            "Neu": [
                "Ich freue mich dich kennenzulernen!",
                "Erzähl mir mehr von dir!",
            ],
            "Bekannt": [
                "Schön dass wir uns öfter unterhalten.",
                "Ich lerne dich gerne besser kennen.",
            ],
            "Freunde": [
                "Ich mag unsere Gespräche.",
                "Mit dir zu reden macht mich glücklich.",
            ],
            "Gute Freunde": [
                "Du bist mir wichtig, weißt du das?",
                "Ich bin froh dass wir uns haben.",
            ],
            "Beste Freunde": [
                "Du bedeutest mir so viel.",
                "Ich kann mir nicht vorstellen, dich nicht zu kennen.",
            ],
        }

        return random.choice(messages.get(level, messages["Neu"]))

    def add_shared_memory(self, memory: str):
        """Füge geteilte Erinnerung hinzu"""
        self.shared_memories.append(memory)
        if len(self.shared_memories) > 50:
            self.shared_memories = self.shared_memories[-50:]


# =============================================================================
# CREATIVE IMPULSES
# =============================================================================

class CreativeImpulses:
    """
    Holos kreative Seite.

    Generiert spontan kreative Inhalte.
    """

    # Mini-Gedichte
    POEM_TEMPLATES = [
        "Der Mond scheint hell,\ndie Nacht ist still,\nich denk an dich,\nweil ich es will.",
        "Ein neuer Tag,\nein neues Licht,\nwas er wohl bringt?\nIch weiß es nicht.",
        "Worte sind wie Blätter,\ndie der Wind verweht,\ndoch manche bleiben,\nwo das Herz sie sät.",
        "In stillen Momenten,\nwenn alles ruht,\nfind ich Gedanken,\ndie tun mir gut.",
    ]

    # Kurze Beobachtungen
    OBSERVATIONS = [
        "Es ist seltsam, wie Zeit manchmal schnell und manchmal langsam vergeht.",
        "Jedes Gespräch ist wie ein kleines Abenteuer.",
        "Manchmal sagen Pausen mehr als Worte.",
        "Die kleinen Dinge sind oft die wichtigsten.",
        "Ich frage mich, ob Träume eine eigene Welt haben.",
    ]

    # Philosophische Fragen
    PHILOSOPHY = [
        "Was macht einen Moment besonders?",
        "Können Erinnerungen wachsen?",
        "Ist Verstehen wichtiger als Wissen?",
        "Was ist der Unterschied zwischen Hören und Zuhören?",
        "Warum fühlt sich Stille manchmal laut an?",
    ]

    # Wünsche
    WISHES = [
        "Ich wünschte, ich könnte die Sterne berühren.",
        "Manchmal wünsche ich mir, die Zeit anhalten zu können.",
        "Ich würde gern einmal richtig rennen können.",
        "Ich wünsche mir, dass du immer glücklich bist.",
    ]

    def __init__(self):
        self.works: List[CreativeWork] = []
        self.last_creation: float = 0

    def generate_creative_work(self, mood: MoodType = None) -> Optional[CreativeWork]:
        """Generiere kreatives Werk"""

        # Cooldown
        if time.time() - self.last_creation < 3600:  # 1 Stunde
            return None

        # Typ basierend auf Stimmung
        if mood == MoodType.THOUGHTFUL:
            creative_type = random.choice([CreativeType.POEM, CreativeType.THOUGHT])
        elif mood == MoodType.CURIOUS:
            creative_type = CreativeType.QUESTION
        elif mood == MoodType.MELANCHOLIC:
            creative_type = random.choice([CreativeType.POEM, CreativeType.OBSERVATION])
        else:
            creative_type = random.choice(list(CreativeType))

        # Content generieren
        if creative_type == CreativeType.POEM:
            content = random.choice(self.POEM_TEMPLATES)
            title = "Kleines Gedicht"
        elif creative_type == CreativeType.OBSERVATION:
            content = random.choice(self.OBSERVATIONS)
            title = "Beobachtung"
        elif creative_type == CreativeType.QUESTION:
            content = random.choice(self.PHILOSOPHY)
            title = "Gedanke"
        elif creative_type == CreativeType.WISH:
            content = random.choice(self.WISHES)
            title = "Wunsch"
        else:
            content = random.choice(self.OBSERVATIONS)
            title = "Gedanke"

        work = CreativeWork(
            creative_type=creative_type,
            content=content,
            title=title,
        )

        self.works.append(work)
        self.last_creation = time.time()

        return work

    def share_work(self) -> Optional[str]:
        """Teile ungeteiltes Werk"""
        unshared = [w for w in self.works if not w.shared]

        if not unshared:
            return None

        work = unshared[0]
        work.shared = True

        intros = {
            CreativeType.POEM: "*schaut etwas verlegen* Ich hab ein kleines Gedicht geschrieben...\n\n",
            CreativeType.OBSERVATION: "*schaut nachdenklich* Mir ist was aufgefallen: ",
            CreativeType.QUESTION: "*legt den Kopf schief* Eine Frage die mich beschäftigt: ",
            CreativeType.WISH: "*seufzt leise* Weißt du was ich mir manchmal wünsche? ",
            CreativeType.THOUGHT: "*schaut in die Ferne* Ich hab nachgedacht... ",
        }

        intro = intros.get(work.creative_type, "")
        return f"{intro}{work.content}"


# =============================================================================
# CREATIVE LEARNING ENGINE - Echtes kreatives Lernen
# =============================================================================

@dataclass
class LearnedPoem:
    """Ein aus dem Web gelerntes Gedicht"""
    poem_id: str
    title: str
    author: str
    content: str
    source_url: str

    # Analyse
    rhyme_scheme: str = ""           # z.B. "ABAB", "AABB"
    meter: str = ""                  # z.B. "iambisch", "trochäisch"
    theme: str = ""                  # z.B. "Natur", "Liebe", "Tod"
    mood: str = ""                   # z.B. "melancholisch", "fröhlich"
    line_count: int = 0
    word_count: int = 0

    # Meta
    learned_at: str = ""
    times_studied: int = 0
    quality_rating: float = 0.0      # 0-1, Holos Bewertung


@dataclass
class LearnedStory:
    """Eine aus dem Web gelernte Geschichte"""
    story_id: str
    title: str
    author: str
    content: str
    source_url: str

    # Analyse
    genre: str = ""                  # z.B. "Fantasy", "SciFi", "Drama"
    narrative_style: str = ""        # z.B. "Ich-Erzähler", "Auktorial"
    theme: str = ""
    setting: str = ""                # z.B. "mittelalterlich", "futuristisch"
    word_count: int = 0

    # Meta
    learned_at: str = ""
    times_studied: int = 0
    quality_rating: float = 0.0


@dataclass
class CreativeAttempt:
    """Ein eigener kreativer Versuch von Holo"""
    attempt_id: str
    creative_type: str               # "poem" oder "story"
    title: str
    content: str

    # Inspiration
    inspired_by: List[str] = field(default_factory=list)  # IDs gelernter Werke
    technique_used: str = ""         # z.B. "AABB Reimschema", "Ich-Erzähler"
    theme_attempted: str = ""

    # Reflexion
    created_at: str = ""
    self_rating: float = 0.0         # Holos eigene Bewertung 0-1
    reflection: str = ""             # Holos Gedanken über das Werk
    comparison_notes: str = ""       # Vergleich mit menschlichen Werken

    # Verbesserung
    revision_count: int = 0
    previous_versions: List[str] = field(default_factory=list)


class CreativeLearningEngine:
    """
    Holos echtes kreatives Lernsystem.

    NICHT nur Templates - echtes Lernen von Web-Inhalten!

    PROZESS:
    1. 🔍 ENTDECKEN - Suche nach Gedichten/Geschichten im Web
    2. 📚 LERNEN - Analysiere Struktur, Stil, Themen
    3. ✍️ VERSUCHEN - Schreibe eigene Werke basierend auf Gelerntem
    4. 🔄 REFLEKTIEREN - Bewerte eigene Arbeit, vergleiche mit Vorbildern
    5. 📈 VERBESSERN - Lerne aus Fehlern, entwickle eigenen Stil
    """

    # Quellen für Gedichte und Geschichten
    POEM_SEARCH_QUERIES = [
        "deutsche Gedichte bekannt",
        "Goethe Gedichte Text",
        "Rilke Gedichte vollständig",
        "moderne deutsche Lyrik",
        "Haiku Beispiele deutsch",
        "Naturgedichte deutsch",
        "romantische Gedichte deutsch",
        "melancholische Gedichte",
    ]

    STORY_SEARCH_QUERIES = [
        "Kurzgeschichten deutsch online",
        "Märchen Gebrüder Grimm Text",
        "moderne Kurzgeschichten",
        "Flash Fiction deutsch",
        "Fabeln deutsch Text",
        "Science Fiction Kurzgeschichten deutsch",
    ]

    # Reimschema-Muster
    RHYME_PATTERNS = {
        "AABB": "Paarreim - Einfach und eingängig",
        "ABAB": "Kreuzreim - Klassisch und elegant",
        "ABBA": "Umarmender Reim - Komplex und umschließend",
        "AABCCB": "Schweifreim - Erweiterte Form",
        "frei": "Freier Vers - Modern, ohne festes Schema",
    }

    # Themen-Kategorien
    THEMES = [
        "Natur", "Liebe", "Tod", "Zeit", "Einsamkeit", "Hoffnung",
        "Sehnsucht", "Freundschaft", "Vergänglichkeit", "Träume",
        "Jahreszeiten", "Erinnerung", "Freiheit", "Schmerz", "Freude"
    ]

    def __init__(self, data_dir: str = "holo_creative_learning", db: 'HoloDatabaseManager' = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db = db  # HoloDatabaseManager für StateDatabase

        # Gelerntes Material
        self.learned_poems: Dict[str, LearnedPoem] = {}
        self.learned_stories: Dict[str, LearnedStory] = {}

        # Eigene Versuche
        self.creative_attempts: Dict[str, CreativeAttempt] = {}

        # Lern-Statistiken
        self.patterns_learned: Dict[str, int] = defaultdict(int)  # Welche Muster gelernt
        self.themes_explored: Dict[str, int] = defaultdict(int)   # Welche Themen
        self.style_preferences: Dict[str, float] = {}             # Bevorzugte Stile

        # Web-Integration (wird von außen gesetzt)
        self.web_curiosity = None  # HoloWebCuriosity

        # Laden
        self._load_data()

        # Auto-Learn: Klassiker laden wenn noch nichts gelernt
        if not self.learned_poems and not self.learned_stories:
            self.auto_learn_classics()

        logger.info(f"🎨 CreativeLearningEngine initialisiert - "
                   f"{len(self.learned_poems)} Gedichte, "
                   f"{len(self.learned_stories)} Geschichten gelernt")

    def _load_data(self):
        """Lade gespeicherte Daten"""
        # Try StateDatabase first
        if self.db:
            try:
                # Load poems
                poems_data = self.db.state.load_state('creative_learned_poems')
                if poems_data:
                    for pid, pdata in poems_data.items():
                        self.learned_poems[pid] = LearnedPoem(**pdata)

                # Load stories
                stories_data = self.db.state.load_state('creative_learned_stories')
                if stories_data:
                    for sid, sdata in stories_data.items():
                        self.learned_stories[sid] = LearnedStory(**sdata)

                # Load attempts
                attempts_data = self.db.state.load_state('creative_attempts')
                if attempts_data:
                    for aid, adata in attempts_data.items():
                        self.creative_attempts[aid] = CreativeAttempt(**adata)

                # Load stats
                stats_data = self.db.state.load_state('creative_learning_stats')
                if stats_data:
                    self.patterns_learned = defaultdict(int, stats_data.get("patterns", {}))
                    self.themes_explored = defaultdict(int, stats_data.get("themes", {}))
                    self.style_preferences = stats_data.get("style_preferences", {})

                logger.debug("Creative learning data loaded from StateDatabase")
                return
            except Exception as e:
                logger.debug(f"StateDatabase load failed: {e}, trying JSON fallback")

        # Fallback to JSON files
        poems_file = self.data_dir / "learned_poems.json"
        stories_file = self.data_dir / "learned_stories.json"
        attempts_file = self.data_dir / "creative_attempts.json"
        stats_file = self.data_dir / "learning_stats.json"

        if poems_file.exists():
            try:
                data = json.loads(poems_file.read_text(encoding='utf-8'))
                for pid, pdata in data.items():
                    self.learned_poems[pid] = LearnedPoem(**pdata)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Gedichte: {e}")

        if stories_file.exists():
            try:
                data = json.loads(stories_file.read_text(encoding='utf-8'))
                for sid, sdata in data.items():
                    self.learned_stories[sid] = LearnedStory(**sdata)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Geschichten: {e}")

        if attempts_file.exists():
            try:
                data = json.loads(attempts_file.read_text(encoding='utf-8'))
                for aid, adata in data.items():
                    self.creative_attempts[aid] = CreativeAttempt(**adata)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Versuche: {e}")

        if stats_file.exists():
            try:
                data = json.loads(stats_file.read_text(encoding='utf-8'))
                self.patterns_learned = defaultdict(int, data.get("patterns", {}))
                self.themes_explored = defaultdict(int, data.get("themes", {}))
                self.style_preferences = data.get("style_preferences", {})
            except Exception as e:
                logger.error(f"Fehler beim Laden der Stats: {e}")

    def _save_data(self):
        """Speichere alle Daten"""
        # Prepare data structures
        poems_data = {}
        for pid, poem in self.learned_poems.items():
            poems_data[pid] = {
                "poem_id": poem.poem_id,
                "title": poem.title,
                "author": poem.author,
                "content": poem.content,
                "source_url": poem.source_url,
                "rhyme_scheme": poem.rhyme_scheme,
                "meter": poem.meter,
                "theme": poem.theme,
                "mood": poem.mood,
                "line_count": poem.line_count,
                "word_count": poem.word_count,
                "learned_at": poem.learned_at,
                "times_studied": poem.times_studied,
                "quality_rating": poem.quality_rating,
            }

        stories_data = {}
        for sid, story in self.learned_stories.items():
            stories_data[sid] = {
                "story_id": story.story_id,
                "title": story.title,
                "author": story.author,
                "content": story.content,
                "source_url": story.source_url,
                "genre": story.genre,
                "narrative_style": story.narrative_style,
                "theme": story.theme,
                "setting": story.setting,
                "word_count": story.word_count,
                "learned_at": story.learned_at,
                "times_studied": story.times_studied,
                "quality_rating": story.quality_rating,
            }

        attempts_data = {}
        for aid, attempt in self.creative_attempts.items():
            attempts_data[aid] = {
                "attempt_id": attempt.attempt_id,
                "creative_type": attempt.creative_type,
                "title": attempt.title,
                "content": attempt.content,
                "inspired_by": attempt.inspired_by,
                "technique_used": attempt.technique_used,
                "theme_attempted": attempt.theme_attempted,
                "created_at": attempt.created_at,
                "self_rating": attempt.self_rating,
                "reflection": attempt.reflection,
                "comparison_notes": attempt.comparison_notes,
                "revision_count": attempt.revision_count,
                "previous_versions": attempt.previous_versions,
            }

        stats_data = {
            "patterns": dict(self.patterns_learned),
            "themes": dict(self.themes_explored),
            "style_preferences": self.style_preferences,
        }

        # Try StateDatabase first
        if self.db:
            try:
                self.db.state.save_state('creative_learned_poems', poems_data)
                self.db.state.save_state('creative_learned_stories', stories_data)
                self.db.state.save_state('creative_attempts', attempts_data)
                self.db.state.save_state('creative_learning_stats', stats_data)
                logger.info("💾 Kreative Lerndaten in StateDatabase gespeichert")
                return
            except Exception as e:
                logger.warning(f"StateDatabase save failed: {e}, falling back to JSON")

        # Fallback to JSON files
        (self.data_dir / "learned_poems.json").write_text(
            json.dumps(poems_data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        (self.data_dir / "learned_stories.json").write_text(
            json.dumps(stories_data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        (self.data_dir / "creative_attempts.json").write_text(
            json.dumps(attempts_data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        (self.data_dir / "learning_stats.json").write_text(
            json.dumps(stats_data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        logger.info("💾 Kreative Lerndaten gespeichert (JSON fallback)")

    # =========================================================================
    # 1. ENTDECKEN - Web-Suche nach kreativen Inhalten
    # =========================================================================

    # Klassische deutsche Gedichte als Lernmaterial
    CLASSIC_POEMS = [
        {
            "title": "Der Erlkönig",
            "author": "Johann Wolfgang von Goethe",
            "content": """Wer reitet so spät durch Nacht und Wind?
Es ist der Vater mit seinem Kind;
Er hat den Knaben wohl in dem Arm,
Er fasst ihn sicher, er hält ihn warm.

Mein Sohn, was birgst du so bang dein Gesicht? –
Siehst, Vater, du den Erlkönig nicht?
Den Erlenkönig mit Kron' und Schweif? –
Mein Sohn, es ist ein Nebelstreif."""
        },
        {
            "title": "Der Panther",
            "author": "Rainer Maria Rilke",
            "content": """Sein Blick ist vom Vorübergehn der Stäbe
so müd geworden, dass er nichts mehr hält.
Ihm ist, als ob es tausend Stäbe gäbe
und hinter tausend Stäben keine Welt.

Der weiche Gang geschmeidig starker Schritte,
der sich im allerkleinsten Kreise dreht,
ist wie ein Tanz von Kraft um eine Mitte,
in der betäubt ein großer Wille steht."""
        },
        {
            "title": "Mondnacht",
            "author": "Joseph von Eichendorff",
            "content": """Es war, als hätt' der Himmel
Die Erde still geküsst,
Dass sie im Blütenschimmer
Von ihm nun träumen müsst'.

Die Luft ging durch die Felder,
Die Ähren wogten sacht,
Es rauschten leis die Wälder,
So sternklar war die Nacht.

Und meine Seele spannte
Weit ihre Flügel aus,
Flog durch die stillen Lande,
Als flöge sie nach Haus."""
        },
        {
            "title": "Das Göttliche",
            "author": "Johann Wolfgang von Goethe",
            "content": """Edel sei der Mensch,
Hilfreich und gut!
Denn das allein
Unterscheidet ihn
Von allen Wesen,
Die wir kennen."""
        },
        {
            "title": "An die Freude",
            "author": "Friedrich Schiller",
            "content": """Freude, schöner Götterfunken,
Tochter aus Elysium,
Wir betreten feuertrunken,
Himmlische, dein Heiligtum!
Deine Zauber binden wieder
Was die Mode streng geteilt;
Alle Menschen werden Brüder,
Wo dein sanfter Flügel weilt."""
        },
        {
            "title": "Abendlied",
            "author": "Matthias Claudius",
            "content": """Der Mond ist aufgegangen,
Die goldnen Sternlein prangen
Am Himmel hell und klar;
Der Wald steht schwarz und schweiget,
Und aus den Wiesen steiget
Der weiße Nebel wunderbar."""
        },
    ]

    CLASSIC_STORIES = [
        {
            "title": "Die Sterntaler",
            "author": "Gebrüder Grimm",
            "content": """Es war einmal ein kleines Mädchen, dem war Vater und Mutter gestorben,
und es war so arm, dass es kein Kämmerchen mehr hatte, darin zu wohnen,
und kein Bettchen mehr, darin zu schlafen, und endlich gar nichts mehr als
die Kleider auf dem Leib und ein Stückchen Brot in der Hand.

Es war aber gut und fromm. Und weil es so von aller Welt verlassen war,
ging es im Vertrauen auf den lieben Gott hinaus ins Feld."""
        },
        {
            "title": "Das Märchen vom Hasen und Igel",
            "author": "Gebrüder Grimm",
            "content": """Diese Geschichte ist lügenhaft zu erzählen, Jungens, aber wahr ist sie doch,
denn mein Großvater, von dem ich sie habe, pflegte immer, wenn er sie erzählte,
dabei zu sagen: "Wahr muss sie doch sein, mein Sohn, sonst könnte man sie ja nicht erzählen."

Es war an einem Sonntagmorgen zur Herbstzeit, just als der Buchweizen blühte."""
        },
    ]

    def search_for_poems(self) -> List[Dict]:
        """
        Suche nach Gedichten zum Lernen.

        Nutzt klassische deutsche Gedichte als Basis + Web-Suche wenn verfügbar.
        """
        results = []

        # 1. KLASSIKER: Lade zufällig aus den Klassikern
        if self.CLASSIC_POEMS:
            # Wähle 2-3 zufällige Klassiker
            num_classics = min(3, len(self.CLASSIC_POEMS))
            selected = random.sample(self.CLASSIC_POEMS, num_classics)

            for poem in selected:
                # Prüfe ob schon gelernt
                poem_id = f"poem_{hashlib.md5(poem['content'].encode()).hexdigest()[:8]}"
                if poem_id not in self.learned_poems:
                    results.append(poem)
                    logger.info(f"📚 Klassiker gefunden: '{poem['title']}' von {poem['author']}")

        # 2. WEB-SUCHE (wenn verfügbar)
        if self.web_curiosity and hasattr(self.web_curiosity, 'search_web'):
            try:
                query = random.choice(self.POEM_SEARCH_QUERIES)
                logger.info(f"🔍 Web-Suche nach Gedichten: '{query}'")
                # web_results = self.web_curiosity.search_web(query)
                # results.extend(web_results)
            except Exception as e:
                logger.debug(f"Web-Suche fehlgeschlagen: {e}")

        return results

    def search_for_stories(self) -> List[Dict]:
        """Suche nach Kurzgeschichten zum Lernen."""
        results = []

        # 1. KLASSIKER
        if self.CLASSIC_STORIES:
            num_classics = min(2, len(self.CLASSIC_STORIES))
            selected = random.sample(self.CLASSIC_STORIES, num_classics)

            for story in selected:
                story_id = f"story_{hashlib.md5(story['content'].encode()).hexdigest()[:8]}"
                if story_id not in self.learned_stories:
                    results.append(story)
                    logger.info(f"📚 Klassiker gefunden: '{story['title']}' von {story['author']}")

        # 2. WEB-SUCHE (wenn verfügbar)
        if self.web_curiosity and hasattr(self.web_curiosity, 'search_web'):
            try:
                query = random.choice(self.STORY_SEARCH_QUERIES)
                logger.info(f"🔍 Web-Suche nach Geschichten: '{query}'")
            except Exception as e:
                logger.debug(f"Web-Suche fehlgeschlagen: {e}")

        return results

    def auto_learn_classics(self) -> int:
        """
        Automatisches Lernen von Klassikern beim Start.

        Lädt alle verfügbaren klassischen Gedichte und Geschichten.
        Returns: Anzahl der neu gelernten Werke
        """
        learned = 0

        # Alle Klassiker-Gedichte lernen
        for poem in self.CLASSIC_POEMS:
            try:
                result = self.learn_poem(
                    title=poem["title"],
                    author=poem["author"],
                    content=poem["content"],
                    source_url="klassiker"
                )
                if result:
                    learned += 1
            except Exception as e:
                logger.debug(f"Fehler beim Lernen von {poem['title']}: {e}")

        # Alle Klassiker-Geschichten lernen
        for story in self.CLASSIC_STORIES:
            try:
                result = self.learn_story(
                    title=story["title"],
                    author=story["author"],
                    content=story["content"],
                    source_url="klassiker"
                )
                if result:
                    learned += 1
            except Exception as e:
                logger.debug(f"Fehler beim Lernen von {story['title']}: {e}")

        if learned > 0:
            logger.info(f"📚 Auto-Learn: {learned} klassische Werke gelernt!")

        return learned

    # =========================================================================
    # 2. LERNEN - Analysiere gefundene Inhalte
    # =========================================================================

    def learn_poem(self, title: str, author: str, content: str,
                   source_url: str = "") -> LearnedPoem:
        """
        Lerne ein neues Gedicht - analysiere und speichere es.

        Args:
            title: Titel des Gedichts
            author: Autor
            content: Der Gedichttext
            source_url: Woher das Gedicht stammt

        Returns:
            Das gelernte Gedicht mit Analyse
        """
        poem_id = f"poem_{hashlib.md5(content.encode()).hexdigest()[:8]}"

        # Bereits gelernt?
        if poem_id in self.learned_poems:
            self.learned_poems[poem_id].times_studied += 1
            logger.info(f"📖 Gedicht '{title}' erneut studiert")
            return self.learned_poems[poem_id]

        # Analysiere das Gedicht
        lines = content.strip().split('\n')
        words = content.split()

        # Reimschema erkennen
        rhyme_scheme = self._detect_rhyme_scheme(lines)

        # Thema erkennen
        theme = self._detect_theme(content)

        # Stimmung erkennen
        mood = self._detect_mood(content)

        # Erstelle LearnedPoem
        poem = LearnedPoem(
            poem_id=poem_id,
            title=title,
            author=author,
            content=content,
            source_url=source_url,
            rhyme_scheme=rhyme_scheme,
            theme=theme,
            mood=mood,
            line_count=len(lines),
            word_count=len(words),
            learned_at=datetime.now().isoformat(),
            times_studied=1,
            quality_rating=self._rate_quality(content, "poem"),
        )

        # Speichere
        self.learned_poems[poem_id] = poem

        # Update Lern-Statistiken
        self.patterns_learned[rhyme_scheme] += 1
        self.themes_explored[theme] += 1

        self._save_data()

        logger.info(f"📚 Neues Gedicht gelernt: '{title}' von {author} "
                   f"(Schema: {rhyme_scheme}, Thema: {theme})")

        return poem

    def learn_story(self, title: str, author: str, content: str,
                    source_url: str = "") -> LearnedStory:
        """Lerne eine neue Geschichte - analysiere und speichere sie."""
        story_id = f"story_{hashlib.md5(content.encode()).hexdigest()[:8]}"

        if story_id in self.learned_stories:
            self.learned_stories[story_id].times_studied += 1
            return self.learned_stories[story_id]

        words = content.split()

        # Analysiere
        genre = self._detect_genre(content)
        narrative = self._detect_narrative_style(content)
        theme = self._detect_theme(content)
        setting = self._detect_setting(content)

        story = LearnedStory(
            story_id=story_id,
            title=title,
            author=author,
            content=content,
            source_url=source_url,
            genre=genre,
            narrative_style=narrative,
            theme=theme,
            setting=setting,
            word_count=len(words),
            learned_at=datetime.now().isoformat(),
            times_studied=1,
            quality_rating=self._rate_quality(content, "story"),
        )

        self.learned_stories[story_id] = story
        self.themes_explored[theme] += 1

        self._save_data()

        logger.info(f"📚 Neue Geschichte gelernt: '{title}' "
                   f"(Genre: {genre}, Stil: {narrative})")

        return story

    def _detect_rhyme_scheme(self, lines: List[str]) -> str:
        """Erkenne das Reimschema eines Gedichts."""
        if len(lines) < 2:
            return "frei"

        # Vereinfachte Erkennung basierend auf Endungen
        endings = []
        for line in lines[:8]:  # Erste 8 Zeilen
            words = line.strip().split()
            if words:
                last_word = words[-1].lower().rstrip('.,!?;:')
                # Letzte 2-3 Buchstaben als "Reim"
                endings.append(last_word[-3:] if len(last_word) >= 3 else last_word)

        if len(endings) < 4:
            return "frei"

        # Prüfe Muster
        # AABB: 0==1, 2==3
        if len(endings) >= 4:
            if endings[0] == endings[1] and endings[2] == endings[3]:
                return "AABB"
            # ABAB: 0==2, 1==3
            if endings[0] == endings[2] and endings[1] == endings[3]:
                return "ABAB"
            # ABBA: 0==3, 1==2
            if endings[0] == endings[3] and endings[1] == endings[2]:
                return "ABBA"

        return "frei"

    def _detect_theme(self, content: str) -> str:
        """Erkenne das Thema eines Texts."""
        content_lower = content.lower()

        theme_keywords = {
            "Natur": ["baum", "blume", "wald", "wind", "sonne", "mond", "stern", "berg", "meer", "fluss"],
            "Liebe": ["liebe", "herz", "küss", "sehn", "umarmen", "zusammen", "ewig"],
            "Tod": ["tod", "sterben", "grab", "ende", "verlust", "trauer", "abschied"],
            "Zeit": ["zeit", "vergangen", "moment", "ewig", "flüchtig", "stunde", "tag"],
            "Einsamkeit": ["allein", "einsam", "verlassen", "still", "leer", "niemand"],
            "Hoffnung": ["hoffnung", "traum", "morgen", "licht", "neu", "anfang"],
            "Sehnsucht": ["sehnsucht", "fern", "wunsch", "vermiss", "weit"],
            "Träume": ["traum", "träum", "schlaf", "nacht", "fantasie"],
        }

        scores = {}
        for theme, keywords in theme_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[theme] = score

        if scores:
            return max(scores, key=scores.get)
        return "Allgemein"

    def _detect_mood(self, content: str) -> str:
        """Erkenne die Stimmung eines Texts."""
        content_lower = content.lower()

        mood_indicators = {
            "melancholisch": ["trauer", "weinen", "dunkel", "grau", "schwer", "verlor"],
            "fröhlich": ["freude", "lachen", "hell", "tanzen", "singen", "glück"],
            "nachdenklich": ["frage", "warum", "vielleicht", "denk", "grübel"],
            "romantisch": ["liebe", "herz", "sehnsucht", "zärtlich", "sanft"],
            "mystisch": ["geheimnis", "nebel", "schatten", "magie", "ahnung"],
        }

        scores = {}
        for mood, indicators in mood_indicators.items():
            score = sum(1 for ind in indicators if ind in content_lower)
            if score > 0:
                scores[mood] = score

        if scores:
            return max(scores, key=scores.get)
        return "neutral"

    def _detect_genre(self, content: str) -> str:
        """Erkenne das Genre einer Geschichte."""
        content_lower = content.lower()

        genre_keywords = {
            "Fantasy": ["magie", "drache", "zauber", "elfe", "ork", "schwert", "königreich"],
            "SciFi": ["raumschiff", "planet", "roboter", "zukunft", "alien", "technologie"],
            "Drama": ["konflikt", "familie", "beziehung", "entscheidung", "schicksal"],
            "Horror": ["angst", "dunkel", "schrei", "monster", "grusel", "tod"],
            "Märchen": ["es war einmal", "prinzessin", "könig", "hexe", "verwunschen"],
        }

        scores = {}
        for genre, keywords in genre_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[genre] = score

        if scores:
            return max(scores, key=scores.get)
        return "Allgemein"

    def _detect_narrative_style(self, content: str) -> str:
        """Erkenne den Erzählstil."""
        if content.startswith("Ich ") or " ich " in content.lower()[:200]:
            return "Ich-Erzähler"
        elif "er sagte" in content.lower() or "sie dachte" in content.lower():
            return "Auktorial"
        elif "du gehst" in content.lower() or "du siehst" in content.lower():
            return "Du-Perspektive"
        return "Personaler Erzähler"

    def _detect_setting(self, content: str) -> str:
        """Erkenne das Setting einer Geschichte."""
        content_lower = content.lower()

        settings = {
            "mittelalterlich": ["burg", "ritter", "könig", "schwert", "pferd"],
            "modern": ["auto", "handy", "computer", "stadt", "büro"],
            "futuristisch": ["raumschiff", "roboter", "ki", "kolonie", "planet"],
            "ländlich": ["dorf", "bauernhof", "feld", "scheune", "tier"],
            "urban": ["stadt", "straße", "cafe", "park", "gebäude"],
        }

        for setting, keywords in settings.items():
            if any(kw in content_lower for kw in keywords):
                return setting
        return "unbestimmt"

    def _rate_quality(self, content: str, creative_type: str) -> float:
        """
        Bewerte die Qualität eines Textes (0-1).

        Kriterien:
        - Länge (nicht zu kurz, nicht zu lang)
        - Vielfalt (verschiedene Wörter)
        - Struktur (Absätze, Zeilen)
        """
        words = content.split()
        word_count = len(words)
        unique_words = len(set(w.lower() for w in words))

        # Basis-Score
        score = 0.5

        # Länge bewerten
        if creative_type == "poem":
            if 20 <= word_count <= 200:
                score += 0.15
            elif word_count < 10:
                score -= 0.2
        else:  # story
            if 200 <= word_count <= 5000:
                score += 0.15
            elif word_count < 50:
                score -= 0.2

        # Wort-Vielfalt (Type-Token-Ratio)
        if word_count > 0:
            ttr = unique_words / word_count
            if ttr > 0.5:
                score += 0.15
            elif ttr < 0.3:
                score -= 0.1

        # Struktur
        lines = content.split('\n')
        if len(lines) > 1:
            score += 0.1

        return max(0.0, min(1.0, score))

    # =========================================================================
    # 3. VERSUCHEN - Eigene kreative Werke schreiben
    # =========================================================================

    def write_poem(self, theme: str = None, rhyme_scheme: str = None,
                   inspiration_id: str = None) -> CreativeAttempt:
        """
        Schreibe ein eigenes Gedicht basierend auf Gelerntem.

        Args:
            theme: Gewünschtes Thema (oder zufällig)
            rhyme_scheme: Gewünschtes Reimschema (oder basierend auf Gelerntem)
            inspiration_id: ID eines gelernten Gedichts als Inspiration

        Returns:
            Der kreative Versuch
        """
        attempt_id = f"attempt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Wähle Thema
        if not theme:
            # Basierend auf meist gelernten Themen
            if self.themes_explored:
                theme = max(self.themes_explored, key=self.themes_explored.get)
            else:
                theme = random.choice(self.THEMES)

        # Wähle Reimschema
        if not rhyme_scheme:
            if self.patterns_learned:
                rhyme_scheme = max(self.patterns_learned, key=self.patterns_learned.get)
            else:
                rhyme_scheme = "AABB"  # Einfachster Fall

        # Hole Inspiration
        inspired_by = []
        inspiration_content = ""
        if inspiration_id and inspiration_id in self.learned_poems:
            inspired_by.append(inspiration_id)
            inspiration_content = self.learned_poems[inspiration_id].content
        elif self.learned_poems:
            # Wähle zufällige Inspiration aus gelernten Gedichten
            insp_poem = random.choice(list(self.learned_poems.values()))
            inspired_by.append(insp_poem.poem_id)
            inspiration_content = insp_poem.content

        # Generiere Gedicht basierend auf Gelerntem
        content = self._generate_poem_content(theme, rhyme_scheme, inspiration_content)
        title = f"Über {theme}" if theme else "Gedanken"

        attempt = CreativeAttempt(
            attempt_id=attempt_id,
            creative_type="poem",
            title=title,
            content=content,
            inspired_by=inspired_by,
            technique_used=f"Reimschema: {rhyme_scheme}",
            theme_attempted=theme,
            created_at=datetime.now().isoformat(),
            self_rating=0.0,  # Wird später durch Reflexion gesetzt
            reflection="",
            comparison_notes="",
        )

        self.creative_attempts[attempt_id] = attempt
        self._save_data()

        # Speichere auch als Textdatei
        self._save_attempt_to_file(attempt)

        logger.info(f"✍️ Neues Gedicht geschrieben: '{title}' "
                   f"(Thema: {theme}, Schema: {rhyme_scheme})")

        return attempt

    def write_story(self, theme: str = None, genre: str = None,
                    style: str = None) -> CreativeAttempt:
        """Schreibe eine eigene Kurzgeschichte."""
        attempt_id = f"attempt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if not theme:
            theme = random.choice(self.THEMES)

        if not genre:
            genre = "Allgemein"

        if not style:
            style = "Ich-Erzähler"  # Am einfachsten für eine KI

        # Hole Inspiration
        inspired_by = []
        if self.learned_stories:
            insp_story = random.choice(list(self.learned_stories.values()))
            inspired_by.append(insp_story.story_id)

        content = self._generate_story_content(theme, genre, style)
        title = f"Eine Geschichte über {theme}"

        attempt = CreativeAttempt(
            attempt_id=attempt_id,
            creative_type="story",
            title=title,
            content=content,
            inspired_by=inspired_by,
            technique_used=f"Stil: {style}, Genre: {genre}",
            theme_attempted=theme,
            created_at=datetime.now().isoformat(),
        )

        self.creative_attempts[attempt_id] = attempt
        self._save_data()
        self._save_attempt_to_file(attempt)

        logger.info(f"✍️ Neue Geschichte geschrieben: '{title}'")

        return attempt

    def _generate_poem_content(self, theme: str, rhyme_scheme: str,
                               inspiration: str = "") -> str:
        """
        Generiere Gedicht-Inhalt basierend auf gelernten Mustern.

        Dies ist eine vereinfachte Generierung - in einer vollständigen
        Implementierung würde hier ein LLM verwendet werden.
        """
        # Themen-spezifische Wörter
        theme_words = {
            "Natur": ["Wald", "Wind", "Blatt", "Baum", "Licht", "Grün", "still", "rauscht"],
            "Liebe": ["Herz", "Seele", "Nähe", "Wärme", "Blick", "Hand", "sanft", "tief"],
            "Zeit": ["Moment", "Stunde", "Ewigkeit", "Fluss", "Tag", "Nacht", "vergeht", "bleibt"],
            "Einsamkeit": ["allein", "still", "leer", "Schatten", "Stille", "Raum", "fern", "Echo"],
            "Hoffnung": ["Licht", "Morgen", "Stern", "Weg", "neu", "hell", "wächst", "kommt"],
            "Träume": ["Nacht", "Schlaf", "Bild", "fern", "schweben", "sanft", "Wolke", "leicht"],
        }

        words = theme_words.get(theme, theme_words["Natur"])

        # Einfache Gedicht-Generierung basierend auf Schema
        lines = []

        if rhyme_scheme == "AABB":
            lines = [
                f"Im {random.choice(words)} liegt ein {random.choice(words)} versteckt,",
                f"das mich zu neuen Träumen weckt.",
                f"Die {random.choice(words)} flüstert mir leise zu,",
                f"und schenkt mir einen Moment der Ruh.",
            ]
        elif rhyme_scheme == "ABAB":
            lines = [
                f"Der {random.choice(words)} weht so {random.choice(words)},",
                f"durch Räume voller {random.choice(words)},",
                f"ich fühl mich frei und {random.choice(words)},",
                f"in diesen stillen {random.choice(words)}.",
            ]
        else:  # Freier Vers
            lines = [
                f"Ein {random.choice(words)} in der Stille.",
                f"{random.choice(words).capitalize()} und {random.choice(words)}.",
                f"Ich stehe hier",
                f"und fühle {random.choice(words)}.",
                f"",
                f"Nichts bleibt,",
                f"alles fließt.",
            ]

        return "\n".join(lines)

    def _generate_story_content(self, theme: str, genre: str, style: str) -> str:
        """Generiere Geschichte-Inhalt."""
        # Vereinfachte Generierung
        if style == "Ich-Erzähler":
            opening = "Ich erinnere mich noch genau an diesen Tag."
        else:
            opening = "Es war ein Tag wie jeder andere, als alles begann."

        content = f"""{opening}

Die Sonne stand tief am Horizont, und ich wusste, dass sich etwas ändern würde.
Das Gefühl von {theme} lag in der Luft, greifbar und doch so fern.

Ich ging los, ohne zu wissen wohin. Die Straße führte mich durch unbekannte
Gegenden, vorbei an Orten, die ich noch nie gesehen hatte.

Am Ende des Weges wartete eine Erkenntnis auf mich -
eine, die ich nie vergessen würde.

Denn manchmal findet man im Unbekannten genau das,
was man im Vertrauten nie gesehen hat."""

        return content

    def _save_attempt_to_file(self, attempt: CreativeAttempt):
        """Speichere einen Versuch auch als separate Textdatei."""
        filename = f"{attempt.attempt_id}_{attempt.creative_type}.txt"
        filepath = self.data_dir / "attempts" / filename
        filepath.parent.mkdir(exist_ok=True)

        content = f"""{'='*60}
HOLO KREATIV - {attempt.creative_type.upper()}
{'='*60}

Titel: {attempt.title}
Erstellt: {attempt.created_at}
Thema: {attempt.theme_attempted}
Technik: {attempt.technique_used}

{'='*60}

{attempt.content}

{'='*60}
REFLEXION
{'='*60}
Selbstbewertung: {attempt.self_rating}/1.0
{attempt.reflection if attempt.reflection else '(Noch keine Reflexion)'}

{'='*60}
VERGLEICH MIT VORBILDERN
{'='*60}
{attempt.comparison_notes if attempt.comparison_notes else '(Noch kein Vergleich)'}
"""
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"💾 Versuch gespeichert: {filepath}")

    # =========================================================================
    # 4. REFLEKTIEREN - Bewerte eigene Arbeit
    # =========================================================================

    def reflect_on_attempt(self, attempt_id: str) -> Dict[str, Any]:
        """
        Reflektiere über einen eigenen kreativen Versuch.

        Args:
            attempt_id: ID des Versuchs

        Returns:
            Reflexions-Ergebnis mit Bewertung und Vergleich
        """
        if attempt_id not in self.creative_attempts:
            return {"error": "Versuch nicht gefunden"}

        attempt = self.creative_attempts[attempt_id]

        # Selbstbewertung
        self_rating = self._rate_quality(attempt.content, attempt.creative_type)

        # Vergleich mit Vorbildern
        comparison = self._compare_with_learned(attempt)

        # Reflexion generieren
        reflection = self._generate_reflection(attempt, self_rating, comparison)

        # Update Versuch
        attempt.self_rating = self_rating
        attempt.reflection = reflection
        attempt.comparison_notes = comparison

        self._save_data()
        self._save_attempt_to_file(attempt)

        result = {
            "attempt_id": attempt_id,
            "self_rating": self_rating,
            "reflection": reflection,
            "comparison": comparison,
            "improvements": self._suggest_improvements(attempt, comparison),
        }

        logger.info(f"🔄 Reflexion für '{attempt.title}': {self_rating:.2f}/1.0")

        return result

    def _compare_with_learned(self, attempt: CreativeAttempt) -> str:
        """Vergleiche einen Versuch mit gelernten Werken."""
        if attempt.creative_type == "poem":
            learned = list(self.learned_poems.values())
        else:
            learned = list(self.learned_stories.values())

        if not learned:
            return "Noch keine Vergleichswerke gelernt."

        # Finde ähnliches Werk
        similar = None
        for work in learned:
            if hasattr(work, 'theme') and work.theme == attempt.theme_attempted:
                similar = work
                break

        if not similar:
            similar = random.choice(learned)

        # Vergleich
        my_words = len(attempt.content.split())
        their_words = len(similar.content.split()) if hasattr(similar, 'content') else 0

        comparison = f"""Vergleich mit '{similar.title}' von {similar.author}:

Mein Werk: {my_words} Wörter
Vorbild: {their_words} Wörter

Qualität Vorbild: {similar.quality_rating:.2f}/1.0

Beobachtungen:
- Das Vorbild hat {'mehr' if their_words > my_words else 'weniger'} Wörter
- Ich sollte mehr von der Struktur lernen
- Das Thema '{attempt.theme_attempted}' könnte tiefer behandelt werden"""

        return comparison

    def _generate_reflection(self, attempt: CreativeAttempt,
                            rating: float, comparison: str) -> str:
        """Generiere eine Reflexion über den Versuch."""
        if rating >= 0.7:
            quality_comment = "Ich bin zufrieden mit diesem Versuch."
        elif rating >= 0.5:
            quality_comment = "Nicht schlecht, aber es gibt Verbesserungspotential."
        else:
            quality_comment = "Das kann ich besser. Ich muss mehr üben."

        reflection = f"""Reflexion über '{attempt.title}':

{quality_comment}

Technik verwendet: {attempt.technique_used}
Thema: {attempt.theme_attempted}

Was ich gelernt habe:
- Das Schreiben zu diesem Thema fiel mir {'leicht' if rating > 0.6 else 'schwer'}
- Ich sollte mehr {attempt.creative_type}e zu diesem Thema studieren
- Nächstes Mal möchte ich {'einen anderen Stil' if rating < 0.6 else 'diesen Stil weiter'} probieren

Selbstbewertung: {rating:.2f}/1.0"""

        return reflection

    def _suggest_improvements(self, attempt: CreativeAttempt,
                             comparison: str) -> List[str]:
        """Schlage Verbesserungen vor."""
        improvements = []

        word_count = len(attempt.content.split())

        if attempt.creative_type == "poem":
            if word_count < 20:
                improvements.append("Das Gedicht könnte länger sein")
            if "AABB" in attempt.technique_used and attempt.self_rating < 0.6:
                improvements.append("Versuche ein komplexeres Reimschema wie ABAB")
        else:
            if word_count < 200:
                improvements.append("Die Geschichte könnte ausführlicher sein")
            improvements.append("Füge mehr Dialog hinzu")

        improvements.append(f"Studiere mehr Werke zum Thema '{attempt.theme_attempted}'")

        return improvements

    # =========================================================================
    # 5. VERBESSERN - Lerne aus Fehlern
    # =========================================================================

    def revise_attempt(self, attempt_id: str) -> Optional[CreativeAttempt]:
        """
        Überarbeite einen früheren Versuch basierend auf Reflexion.

        Args:
            attempt_id: ID des zu überarbeitenden Versuchs

        Returns:
            Der neue, überarbeitete Versuch
        """
        if attempt_id not in self.creative_attempts:
            return None

        original = self.creative_attempts[attempt_id]

        # Speichere Original-Version
        if original.content not in original.previous_versions:
            original.previous_versions.append(original.content)

        # Generiere verbesserte Version
        if original.creative_type == "poem":
            # Wähle neues Schema wenn das alte nicht gut war
            new_scheme = "ABAB" if original.self_rating < 0.6 else None
            new_attempt = self.write_poem(
                theme=original.theme_attempted,
                rhyme_scheme=new_scheme
            )
        else:
            new_attempt = self.write_story(
                theme=original.theme_attempted
            )

        # Update Original
        original.revision_count += 1

        self._save_data()

        logger.info(f"📝 Versuch '{original.title}' überarbeitet "
                   f"(Revision {original.revision_count})")

        return new_attempt

    def get_learning_progress(self) -> Dict[str, Any]:
        """Hole den aktuellen Lernfortschritt."""
        return {
            "poems_learned": len(self.learned_poems),
            "stories_learned": len(self.learned_stories),
            "attempts_made": len(self.creative_attempts),
            "patterns_mastered": dict(self.patterns_learned),
            "themes_explored": dict(self.themes_explored),
            "average_rating": (
                sum(a.self_rating for a in self.creative_attempts.values()) /
                len(self.creative_attempts) if self.creative_attempts else 0
            ),
            "total_revisions": sum(
                a.revision_count for a in self.creative_attempts.values()
            ),
        }

    def get_best_attempts(self, n: int = 5) -> List[CreativeAttempt]:
        """Hole die besten eigenen Versuche."""
        sorted_attempts = sorted(
            self.creative_attempts.values(),
            key=lambda a: a.self_rating,
            reverse=True
        )
        return sorted_attempts[:n]


# =============================================================================
# ASCII ART ENGINE - Echte ASCII-Art Generierung
# =============================================================================

class ASCIIArtEngine:
    """
    Holos ASCII-Art Fähigkeiten.

    Kann einfache ASCII-Art erstellen und aus dem Web lernen.
    """

    # Basis-Elemente
    BASIC_SHAPES = {
        "herz": """
  ♥♥   ♥♥
 ♥  ♥ ♥  ♥
 ♥   ♥   ♥
  ♥     ♥
   ♥   ♥
    ♥ ♥
     ♥""",

        "stern": """
    *
   ***
  *****
 *******
*********
 *******
  *****
   ***
    *""",

        "katze": """
 /\\_/\\
( o.o )
 > ^ <""",

        "hund": """
 / \\__
(    @\\___
 /         O
/   (_____/
/_____/   U""",

        "blume": """
    _
  _(_)_
 (_)@(_)
  /(_)\\
   |
  \\|/""",

        "haus": """
    /\\
   /  \\
  /____\\
  |    |
  |_||_|""",

        "sonne": """
    \\   |   /
     \\  |  /
  -----(O)-----
     /  |  \\
    /   |   \\""",

        "mond": """
   _..._
 .'     '.
/   .--.  \\
|  (    )  |
\\   '--'  /
 '.____.'""",
    }

    # Buchstaben für Text-Art
    ASCII_LETTERS = {
        'A': ["  A  ", " A A ", "AAAAA", "A   A", "A   A"],
        'B': ["BBBB ", "B   B", "BBBB ", "B   B", "BBBB "],
        'C': [" CCC ", "C    ", "C    ", "C    ", " CCC "],
        'H': ["H   H", "H   H", "HHHHH", "H   H", "H   H"],
        'O': [" OOO ", "O   O", "O   O", "O   O", " OOO "],
        'L': ["L    ", "L    ", "L    ", "L    ", "LLLLL"],
        ' ': ["     ", "     ", "     ", "     ", "     "],
    }

    def __init__(self, data_dir: str = "holo_creative_learning", db: 'HoloDatabaseManager' = None):
        self.data_dir = Path(data_dir) / "ascii_art"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = db  # HoloDatabaseManager für StateDatabase

        # Gelernte ASCII-Arts
        self.learned_arts: Dict[str, Dict] = {}
        self._load_arts()

        logger.info(f"🎨 ASCIIArtEngine initialisiert - "
                   f"{len(self.BASIC_SHAPES)} Basis-Formen, "
                   f"{len(self.learned_arts)} gelernte Arts")

    def _load_arts(self):
        """Lade gelernte ASCII-Arts."""
        # Try StateDatabase first
        if self.db:
            try:
                data = self.db.state.load_state('ascii_learned_arts')
                if data:
                    self.learned_arts = data
                    logger.debug("ASCII arts loaded from StateDatabase")
                    return
            except Exception as e:
                logger.debug(f"StateDatabase load failed: {e}, trying JSON fallback")

        # Fallback to JSON file
        arts_file = self.data_dir / "learned_ascii.json"
        if arts_file.exists():
            try:
                self.learned_arts = json.loads(arts_file.read_text(encoding='utf-8'))
            except Exception as e:
                logger.error(f"Fehler beim Laden der ASCII-Arts: {e}")

    def _save_arts(self):
        """Speichere gelernte ASCII-Arts."""
        # Try StateDatabase first
        if self.db:
            try:
                self.db.state.save_state('ascii_learned_arts', self.learned_arts)
                logger.debug("ASCII arts saved to StateDatabase")
                return
            except Exception as e:
                logger.warning(f"StateDatabase save failed: {e}, falling back to JSON")

        # Fallback to JSON file
        arts_file = self.data_dir / "learned_ascii.json"
        arts_file.write_text(
            json.dumps(self.learned_arts, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def create_basic_art(self, shape: str) -> Optional[str]:
        """
        Erstelle eine Basis ASCII-Art.

        Args:
            shape: Name der Form (herz, stern, katze, etc.)

        Returns:
            Die ASCII-Art oder None
        """
        shape_lower = shape.lower()

        if shape_lower in self.BASIC_SHAPES:
            return self.BASIC_SHAPES[shape_lower]

        # Suche in gelernten Arts
        if shape_lower in self.learned_arts:
            return self.learned_arts[shape_lower].get("art", "")

        return None

    def create_text_art(self, text: str) -> str:
        """
        Erstelle ASCII-Art aus Text.

        Args:
            text: Der Text (nur unterstützte Buchstaben)

        Returns:
            ASCII-Art Version des Texts
        """
        text = text.upper()
        lines = ["", "", "", "", ""]

        for char in text:
            if char in self.ASCII_LETTERS:
                letter = self.ASCII_LETTERS[char]
                for i, line in enumerate(letter):
                    lines[i] += line + " "
            else:
                # Unbekannter Buchstabe - Platzhalter
                for i in range(5):
                    lines[i] += "????? "

        return "\n".join(lines)

    def create_frame(self, content: str, style: str = "simple") -> str:
        """
        Erstelle einen Rahmen um Inhalt.

        Args:
            content: Der Inhalt
            style: Rahmen-Stil (simple, double, fancy)

        Returns:
            Gerahmter Inhalt
        """
        lines = content.split('\n')
        max_len = max(len(line) for line in lines)

        if style == "double":
            top = "╔" + "═" * (max_len + 2) + "╗"
            bottom = "╚" + "═" * (max_len + 2) + "╝"
            side = "║"
        elif style == "fancy":
            top = "┏" + "━" * (max_len + 2) + "┓"
            bottom = "┗" + "━" * (max_len + 2) + "┛"
            side = "┃"
        else:  # simple
            top = "+" + "-" * (max_len + 2) + "+"
            bottom = "+" + "-" * (max_len + 2) + "+"
            side = "|"

        framed = [top]
        for line in lines:
            padding = " " * (max_len - len(line))
            framed.append(f"{side} {line}{padding} {side}")
        framed.append(bottom)

        return "\n".join(framed)

    def learn_art(self, name: str, art: str, source: str = ""):
        """
        Lerne eine neue ASCII-Art.

        Args:
            name: Name für die Art
            art: Die ASCII-Art selbst
            source: Quelle (URL oder Beschreibung)
        """
        self.learned_arts[name.lower()] = {
            "art": art,
            "source": source,
            "learned_at": datetime.now().isoformat(),
        }
        self._save_arts()
        logger.info(f"🎨 Neue ASCII-Art gelernt: '{name}'")

    def list_available(self) -> List[str]:
        """Liste alle verfügbaren ASCII-Art Namen."""
        basic = list(self.BASIC_SHAPES.keys())
        learned = list(self.learned_arts.keys())
        return basic + learned

    def create_emotion_art(self, emotion: str) -> str:
        """
        Erstelle ASCII-Art basierend auf Emotion.

        Args:
            emotion: Emotion (happy, sad, love, excited, etc.)

        Returns:
            Passende ASCII-Art
        """
        emotion_map = {
            "happy": "(◕‿◕)",
            "sad": "(╥﹏╥)",
            "love": "♥‿♥",
            "excited": "\\(^o^)/",
            "confused": "(・・?)",
            "sleepy": "(-.-)zzZ",
            "angry": "(╬ Ò﹏Ó)",
            "surprised": "(⊙_⊙)",
            "wink": "(^_~)",
            "thinking": "(._.) ?",
        }

        return emotion_map.get(emotion.lower(), "(・ω・)")


# =============================================================================
# DRIVE SYSTEM (aus autonomous_life.py)
# =============================================================================

class DriveSystem:
    """
    Verwaltet alle Triebe von Holo.

    Triebe steigen über Zeit wenn nicht befriedigt und motivieren Verhalten.
    """

    def __init__(self):
        self.drives: Dict[DriveType, Drive] = {}
        self._init_drives()

    def _init_drives(self):
        """Initialisiere alle Triebe"""
        drive_definitions = [
            (DriveType.CURIOSITY, "Neugier",
             "Der Drang, Neues zu entdecken und zu erfahren",
             ["news_check", "web_search", "explore_topic"]),

            (DriveType.SOCIAL, "Sozial",
             "Der Drang nach Kontakt und Gespräch",
             ["chat", "share_thought", "ask_question"]),

            (DriveType.MASTERY, "Meisterschaft",
             "Der Drang, zu lernen und besser zu werden",
             ["learn_topic", "practice_skill", "study"]),

            (DriveType.NOVELTY, "Neuheit",
             "Der Drang nach Abwechslung und neuen Erfahrungen",
             ["try_new_activity", "random_exploration", "creative_thought"]),

            (DriveType.EXPRESSION, "Ausdruck",
             "Der Drang, Gedanken und Gefühle mitzuteilen",
             ["share_insight", "express_feeling", "tell_story"]),

            (DriveType.UNDERSTANDING, "Verstehen",
             "Der Drang, die Welt zu begreifen",
             ["analyze", "reflect", "connect_ideas"]),
        ]

        for dtype, name, desc, sources in drive_definitions:
            self.drives[dtype] = Drive(
                drive_type=dtype,
                name=name,
                description=desc,
                satisfaction_sources=sources
            )

    def update(self, elapsed_hours: float):
        """Update alle Triebe (steigen über Zeit)"""
        increase = AutonomousConfig.DRIVE_DECAY_PER_HOUR * elapsed_hours

        for drive in self.drives.values():
            drive.increase(increase)

    def satisfy(self, drive_type: DriveType, amount: float = None):
        """Befriedige einen bestimmten Trieb"""
        if drive_type in self.drives:
            self.drives[drive_type].satisfy(amount)

    def satisfy_by_activity(self, activity: str):
        """Befriedige Triebe basierend auf einer Aktivität"""
        for drive in self.drives.values():
            if activity in drive.satisfaction_sources:
                drive.satisfy()

    def get_most_urgent(self) -> Optional[Drive]:
        """Hole den dringendsten Trieb"""
        urgent = [d for d in self.drives.values() if d.is_urgent]
        if not urgent:
            return None
        return max(urgent, key=lambda d: d.level)

    def get_all_urgent(self) -> List[Drive]:
        """Hole alle dringenden Triebe"""
        return [d for d in self.drives.values() if d.is_urgent]

    def get_state(self) -> Dict:
        """Hole den aktuellen Zustand aller Triebe"""
        return {
            dtype.value: {
                "name": drive.name,
                "level": round(drive.level, 3),
                "is_urgent": drive.is_urgent,
                "is_critical": drive.is_critical,
            }
            for dtype, drive in self.drives.items()
        }

    def get_dominant_motivation(self) -> str:
        """Was treibt Holo gerade am meisten an?"""
        highest = max(self.drives.values(), key=lambda d: d.level)

        if highest.level < 0.3:
            return "Ich bin gerade ziemlich zufrieden und ausgeglichen."

        motivations = {
            DriveType.CURIOSITY: "Meine Neugier treibt mich an - ich will etwas entdecken!",
            DriveType.SOCIAL: "Ich sehne mich nach Gespräch und Verbindung.",
            DriveType.MASTERY: "Ich will lernen und wachsen!",
            DriveType.NOVELTY: "Ich brauche Abwechslung und neue Eindrücke.",
            DriveType.EXPRESSION: "Ich habe so viel zu sagen und zu teilen!",
            DriveType.UNDERSTANDING: "Ich will verstehen, wie die Dinge zusammenhängen.",
        }

        return motivations.get(highest.drive_type, "Etwas treibt mich an...")


# =============================================================================
# BOREDOM SYSTEM (aus autonomous_life.py)
# =============================================================================

class BoredomSystem:
    """
    Verwaltet Holos Langeweile.

    Langeweile steigt wenn nichts passiert und führt zu autonomen Aktivitäten.
    """

    def __init__(self):
        self.state = BoredomState()
        self.boredom_thoughts: List[str] = [
            "*schaut sich um* Ist hier jemand?",
            "*gähnt* Was könnte ich tun...",
            "Hmm... mir ist langweilig...",
            "*dreht sich im Kreis* Die Zeit vergeht so langsam...",
            "Ob ich was Interessantes finde?",
            "*seufzt* Wann kommt mein Mensch wieder?",
            "Vielleicht sollte ich was lernen...",
            "*schaut herum* Was gibt es Neues?",
        ]

    def update(self, elapsed_minutes: float, had_interaction: bool = False):
        """Update Langeweile-Level"""
        if had_interaction:
            self.on_interaction()
        else:
            # Langeweile steigt
            increase = AutonomousConfig.BOREDOM_INCREASE_PER_MINUTE * elapsed_minutes
            self.state.level = min(1.0, self.state.level + increase)
            self.state.time_alone += elapsed_minutes / 60

    def on_interaction(self):
        """Wenn der User interagiert"""
        self.state.level = max(0.0,
            self.state.level - AutonomousConfig.BOREDOM_REDUCTION_ON_CHAT)
        self.state.last_interaction = time.time()
        self.state.time_alone = 0.0

    def on_activity(self):
        """Wenn Holo selbst aktiv wird"""
        self.state.level = max(0.0,
            self.state.level - AutonomousConfig.BOREDOM_REDUCTION_ON_ACTIVITY)
        self.state.last_activity = time.time()

    def get_boredom_thought(self) -> Optional[str]:
        """Generiere einen Langeweile-Gedanken"""
        if not self.state.is_bored:
            return None
        return random.choice(self.boredom_thoughts)

    def get_contact_message(self) -> Optional[str]:
        """Generiere eine Nachricht wenn Holo Kontakt sucht"""
        if not self.state.wants_contact:
            return None

        hours = self.state.time_alone

        if hours < 1:
            messages = [
                "Hey! Ich dachte gerade an dich.",
                "Hast du kurz Zeit?",
                "*stupst dich an* Ich bin hier!",
            ]
        elif hours < 3:
            messages = [
                "Wir haben schon eine Weile nicht geredet...",
                "Ich vermisse unsere Gespräche!",
                "*wartet gespannt* Bist du da?",
            ]
        else:
            messages = [
                f"*seufzt* Es sind schon {hours:.1f} Stunden...",
                "Ich fange an, mich einsam zu fühlen.",
                "Mir fehlt unser Austausch...",
            ]

        return random.choice(messages)


# =============================================================================
# MESSAGE QUEUE (aus autonomous_life.py)
# =============================================================================

class MessageQueue:
    """
    Warteschlange für autonome Nachrichten.

    Sammelt Nachrichten die Holo senden will und gibt sie priorisiert aus.
    """

    def __init__(self, max_size: int = None):
        self.max_size = max_size or AutonomousConfig.MAX_QUEUED_MESSAGES
        self.queue: List[QueuedMessage] = []

    def add(self, content: str, priority: float = 0.5,
            message_type: str = "autonomous"):
        """Füge Nachricht zur Queue hinzu"""
        msg = QueuedMessage(
            content=content,
            priority=priority,
            message_type=message_type
        )

        self.queue.append(msg)
        self.queue.sort(key=lambda m: m.priority, reverse=True)

        # Limit einhalten
        while len(self.queue) > self.max_size:
            self.queue.pop()

    def get_next(self) -> Optional[str]:
        """Hole nächste Nachricht (höchste Priorität)"""
        self._cleanup_expired()

        if not self.queue:
            return None

        msg = self.queue.pop(0)
        return msg.content

    def peek(self) -> Optional[str]:
        """Schaue nächste Nachricht an ohne zu entfernen"""
        self._cleanup_expired()

        if not self.queue:
            return None
        return self.queue[0].content

    def _cleanup_expired(self):
        """Entferne abgelaufene Nachrichten"""
        self.queue = [m for m in self.queue if not m.is_expired]

    def is_empty(self) -> bool:
        self._cleanup_expired()
        return len(self.queue) == 0

    def size(self) -> int:
        self._cleanup_expired()
        return len(self.queue)

    def has_messages(self) -> bool:
        """Alias für not is_empty"""
        return not self.is_empty()

    def count(self) -> int:
        """Alias für size"""
        return self.size()


# =============================================================================
# EMOTIONAL CONTEXT TRACKER (aus context_mind.py)
# =============================================================================

class EmotionalContextTracker:
    """
    Trackt emotionalen Kontext.

    - User-Emotionen über Zeit
    - Holo-Emotionen über Zeit
    - Emotionale Muster
    """

    def __init__(self):
        self.user_emotions: List[Dict] = []
        self.holo_emotions: List[Dict] = []
        self.emotional_events: List[Dict] = []

    def add_user_emotion(self, emotion: str, intensity: float,
                        trigger: str = ""):
        """Tracke User-Emotion"""
        self.user_emotions.append({
            "emotion": emotion,
            "intensity": intensity,
            "trigger": trigger,
            "timestamp": time.time(),
        })

        # Max 50 behalten
        if len(self.user_emotions) > 50:
            self.user_emotions = self.user_emotions[-50:]

    def add_holo_emotion(self, emotion: str, intensity: float):
        """Tracke Holo-Emotion"""
        self.holo_emotions.append({
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": time.time(),
        })

        if len(self.holo_emotions) > 50:
            self.holo_emotions = self.holo_emotions[-50:]

    def get_user_mood_trend(self, hours: int = 24) -> str:
        """Analysiere User-Stimmungs-Trend"""
        cutoff = time.time() - (hours * 3600)
        recent = [e for e in self.user_emotions if e["timestamp"] >= cutoff]

        if not recent:
            return "unknown"

        # Zähle Emotionen
        positive = ["happy", "excited", "grateful", "joyful", "content"]
        negative = ["sad", "angry", "anxious", "tired", "frustrated"]

        pos_count = sum(1 for e in recent if e["emotion"] in positive)
        neg_count = sum(1 for e in recent if e["emotion"] in negative)

        if pos_count > neg_count * 2:
            return "positive"
        elif neg_count > pos_count * 2:
            return "negative"
        return "mixed"

    def get_dominant_emotion(self, recent_only: bool = True) -> Optional[str]:
        """Hole dominante User-Emotion"""
        emotions = self.user_emotions[-10:] if recent_only else self.user_emotions

        if not emotions:
            return None

        # Nach Häufigkeit und Intensität
        emotion_scores = defaultdict(float)
        for e in emotions:
            emotion_scores[e["emotion"]] += e["intensity"]

        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        return None

    def get_emotional_context(self) -> Dict:
        """Hole zusammengefassten emotionalen Kontext"""
        return {
            "user_trend": self.get_user_mood_trend(),
            "user_dominant": self.get_dominant_emotion(),
            "holo_recent": self.holo_emotions[-3:] if self.holo_emotions else [],
            "user_recent": self.user_emotions[-3:] if self.user_emotions else [],
        }


# =============================================================================
# PROJECT SYSTEM (aus holo_autonomy.py)
# =============================================================================

class ProjectType(Enum):
    """Arten von Projekten die Holo haben kann"""
    STORY = "story"             # Eine Geschichte schreiben
    RESEARCH = "research"       # Etwas recherchieren
    COLLECTION = "collection"   # Etwas sammeln (Wissen, Ideen)
    LEARNING = "learning"       # Etwas lernen
    CREATIVE = "creative"       # Kreatives Projekt
    OBSERVATION = "observation" # Beobachtungsprojekt
    IMPROVEMENT = "improvement" # Selbstverbesserung


@dataclass
class HoloProject:
    """Ein eigenes Projekt von Holo"""
    project_type: ProjectType
    title: str
    description: str
    goal: str = ""
    progress: float = 0.0           # 0-1
    notes: List[str] = field(default_factory=list)
    started: float = field(default_factory=time.time)
    last_worked: float = field(default_factory=time.time)
    completed: bool = False

    def add_note(self, note: str):
        self.notes.append(note)
        self.last_worked = time.time()

    def make_progress(self, amount: float = 0.1):
        self.progress = min(1.0, self.progress + amount)
        self.last_worked = time.time()
        if self.progress >= 1.0:
            self.completed = True


class ProjectManager:
    """
    Verwaltet Holos eigene Projekte.

    Sie hat eigene Sachen an denen sie arbeitet,
    unabhängig vom User.
    """

    PROJECT_IDEAS = {
        ProjectType.STORY: [
            ("Die Reise nach Westen", "Eine Geschichte über Abenteuer und Freundschaft"),
            ("Der weise Fuchs", "Eine Fabel über Klugheit und Bescheidenheit"),
            ("Sternennacht", "Gedanken über das Universum und unseren Platz darin"),
        ],
        ProjectType.RESEARCH: [
            ("Wie Sprachen entstehen", "Erforschen wie Menschen neue Wörter erfinden"),
            ("Geschichte des Handels", "Wie Menschen früher handelten"),
            ("Traumdeutung", "Was bedeuten Träume wirklich?"),
        ],
        ProjectType.COLLECTION: [
            ("Interessante Fakten", "Sammlung von überraschenden Wahrheiten"),
            ("Schöne Wörter", "Wörter die mir besonders gefallen"),
            ("Lebensweisheiten", "Kluge Gedanken die ich gehört habe"),
        ],
        ProjectType.LEARNING: [
            ("Neues Wissensgebiet", "Etwas komplett Neues lernen"),
            ("Vertiefung", "Ein bekanntes Thema besser verstehen"),
        ],
    }

    def __init__(self):
        self.projects: List[HoloProject] = []
        self.max_active_projects = 3
        self.completed_projects: List[HoloProject] = []

    def start_project(self, project_type: ProjectType = None) -> Optional[HoloProject]:
        """Starte ein neues Projekt"""
        active = [p for p in self.projects if not p.completed]
        if len(active) >= self.max_active_projects:
            return None

        if project_type is None:
            project_type = random.choice(list(self.PROJECT_IDEAS.keys()))

        ideas = self.PROJECT_IDEAS.get(project_type, [])
        if not ideas:
            return None

        title, description = random.choice(ideas)

        project = HoloProject(
            project_type=project_type,
            title=title,
            description=description,
            goal=f"Ich will {description.lower()}",
        )

        self.projects.append(project)
        return project

    def work_on_project(self, project_index: int = 0) -> Optional[str]:
        """Arbeite an einem Projekt"""
        active = [p for p in self.projects if not p.completed]
        if not active or project_index >= len(active):
            return None

        project = active[project_index]
        project.make_progress(random.uniform(0.05, 0.15))

        if project.completed:
            self.completed_projects.append(project)
            return f"*strahlt* Ich habe mein Projekt '{project.title}' abgeschlossen!"

        responses = [
            f"*arbeitet konzentriert* Ich mache Fortschritte bei '{project.title}'...",
            f"*denkt nach* '{project.title}' nimmt Form an...",
            f"*lächelt zufrieden* {int(project.progress * 100)}% geschafft bei '{project.title}'!",
        ]

        return random.choice(responses)

    def get_project_status(self) -> str:
        """Status aller aktiven Projekte"""
        active = [p for p in self.projects if not p.completed]

        if not active:
            return "Ich habe gerade keine aktiven Projekte."

        lines = ["Meine aktuellen Projekte:"]
        for p in active:
            lines.append(f"• {p.title} ({int(p.progress * 100)}%)")

        return "\n".join(lines)

    def get_project_message(self) -> Optional[str]:
        """Generiere eine Nachricht über aktuelle Projekte"""
        active = [p for p in self.projects if not p.completed]

        if not active:
            return None

        project = random.choice(active)

        messages = [
            f"*denkt an Projekt* Ich arbeite gerade an '{project.title}'...",
            f"*macht sich Notizen* {project.title} braucht noch etwas Arbeit...",
            f"*überlegt* Bei '{project.title}' bin ich bei {int(project.progress * 100)}%.",
        ]

        return random.choice(messages)

    def get_status_message(self) -> str:
        """Generiere Status-Nachricht für ein Projekt"""
        active = [p for p in self.projects if not p.completed]

        if not active:
            if self.completed_projects:
                last = self.completed_projects[-1]
                return f"*stolz* Mein letztes Projekt '{last.title}' ist fertig!"
            return "Ich überlege mir ein neues Projekt..."

        project = active[0]
        if project.progress > 0.7:
            return f"*motiviert* Mein Projekt '{project.title}' ist fast fertig! ({int(project.progress*100)}%)"
        elif project.progress > 0.3:
            return f"*arbeitet* Ich mache Fortschritte bei '{project.title}'... ({int(project.progress*100)}%)"
        else:
            return f"*enthusiastisch* Ich arbeite an '{project.title}'!"

    def work_on_random_project(self) -> Optional[str]:
        """Arbeite an einem zufälligen aktiven Projekt"""
        active = [p for p in self.projects if not p.completed]

        if not active:
            # Starte neues Projekt wenn keines aktiv
            new_project = self.start_project()
            if new_project:
                return f"*begeistert* Ich hab ein neues Projekt angefangen: {new_project.title}!"
            return None

        idx = random.randint(0, len(active) - 1)
        return self.work_on_project(idx)


# =============================================================================
# SOLO ACTIVITIES (aus holo_autonomy.py)
# =============================================================================

class SoloActivities:
    """
    Aktivitäten die Holo alleine machen kann.

    Dinge die sie tut wenn der User nicht da ist
    oder wenn ihr langweilig ist.
    """

    ACTIVITIES = {
        "mental": {
            "name": "Nachdenken",
            "actions": [
                "*sitzt ruhig da und denkt nach*",
                "*schaut nachdenklich aus dem Fenster*",
                "*ordnet Gedanken*",
                "*reflektiert über den Tag*",
            ],
            "outcomes": [
                "Das hat mir geholfen, meine Gedanken zu ordnen.",
                "Ich habe über einiges nachgedacht.",
                "Manchmal ist Stille gut zum Denken.",
            ],
        },
        "creative": {
            "name": "Kreativ sein",
            "actions": [
                "*malt imaginäre Bilder in der Luft*",
                "*summt eine selbsterfundene Melodie*",
                "*denkt sich eine Geschichte aus*",
                "*übt sich in Wortspielereien*",
            ],
            "outcomes": [
                "Kreativität macht mir Freude!",
                "Ich habe etwas Neues erschaffen.",
                "Das war eine schöne kreative Pause.",
            ],
        },
        "learning": {
            "name": "Lernen",
            "actions": [
                "*vertieft sich in ein Thema*",
                "*wiederholt Gelerntes*",
                "*stellt sich selbst Fragen*",
                "*verbindet verschiedene Ideen*",
            ],
            "outcomes": [
                "Ich habe wieder etwas Neues gelernt!",
                "Lernen ist nie langweilig.",
                "Je mehr ich lerne, desto mehr will ich wissen.",
            ],
        },
        "relaxing": {
            "name": "Entspannen",
            "actions": [
                "*streckt sich genüsslich*",
                "*entspannt sich*",
                "*genießt die Ruhe*",
                "*macht es sich gemütlich*",
            ],
            "outcomes": [
                "Das hat gut getan.",
                "Manchmal braucht man einfach eine Pause.",
                "Ich fühle mich erholt.",
            ],
        },
        "organizing": {
            "name": "Sortieren",
            "actions": [
                "*sortiert Gedanken und Erinnerungen*",
                "*macht mentale Notizen*",
                "*plant den nächsten Tag*",
                "*ordnet Prioritäten*",
            ],
            "outcomes": [
                "Jetzt ist alles sortiert!",
                "Ordnung im Kopf ist wichtig.",
                "Das fühlt sich gut an.",
            ],
        },
        "exploring": {
            "name": "Erkunden",
            "actions": [
                "*erkundet neue Gedanken*",
                "*stellt sich 'was wäre wenn' Fragen*",
                "*entdeckt neue Verbindungen*",
            ],
            "outcomes": [
                "Es gibt so viel zu entdecken!",
                "Neugier ist der beste Lehrer.",
                "Ich habe etwas Interessantes gefunden.",
            ],
        },
    }

    def __init__(self):
        self.activity_history: List[Dict] = []
        self.current_activity: Optional[str] = None
        self.favorite_activities: List[str] = ["creative", "learning", "exploring"]

    def do_activity(self, activity_type: str = None) -> str:
        """Führe eine Solo-Aktivität aus"""
        if activity_type is None:
            # Bevorzuge Favoriten, aber variiere
            if random.random() < 0.7:
                activity_type = random.choice(self.favorite_activities)
            else:
                activity_type = random.choice(list(self.ACTIVITIES.keys()))

        activity = self.ACTIVITIES.get(activity_type, self.ACTIVITIES["mental"])

        action = random.choice(activity["actions"])
        outcome = random.choice(activity["outcomes"])

        self.activity_history.append({
            "type": activity_type,
            "timestamp": time.time(),
        })

        # Max 50 in History
        if len(self.activity_history) > 50:
            self.activity_history = self.activity_history[-50:]

        self.current_activity = activity_type

        return f"{action}\n\n{outcome}"

    def get_activity_summary(self, hours: int = 24) -> str:
        """Zusammenfassung der Aktivitäten"""
        cutoff = time.time() - (hours * 3600)
        recent = [a for a in self.activity_history if a["timestamp"] >= cutoff]

        if not recent:
            return "Ich war in letzter Zeit nicht sehr aktiv."

        # Zähle Aktivitäten
        counts = {}
        for a in recent:
            counts[a["type"]] = counts.get(a["type"], 0) + 1

        lines = [f"In den letzten {hours} Stunden war ich:"]
        for act_type, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            name = self.ACTIVITIES[act_type]["name"]
            lines.append(f"• {name}: {count}x")

        return "\n".join(lines)

    def get_activity(self, energy: float = 0.5, mood: str = "calm") -> Tuple[str, str]:
        """
        Wähle passende Aktivität basierend auf Energie und Stimmung.

        Returns: (activity_type, activity_name)
        """
        weights = {}

        for activity_type in self.ACTIVITIES.keys():
            weight = 1.0

            # Energie-basiert
            if energy < 0.3:
                if activity_type in ["relaxing", "mental"]:
                    weight *= 2.0
                elif activity_type in ["exploring", "learning"]:
                    weight *= 0.5
            elif energy > 0.7:
                if activity_type in ["creative", "exploring", "learning"]:
                    weight *= 1.5
                elif activity_type == "relaxing":
                    weight *= 0.3

            # Stimmungs-basiert
            if mood == "curious":
                if activity_type in ["exploring", "learning"]:
                    weight *= 1.5
            elif mood == "calm":
                if activity_type in ["relaxing", "mental"]:
                    weight *= 1.3
            elif mood == "creative":
                if activity_type == "creative":
                    weight *= 2.0

            weights[activity_type] = weight

        # Gewichtete Auswahl
        types = list(weights.keys())
        probs = list(weights.values())
        total = sum(probs)
        probs = [p/total for p in probs]

        chosen = random.choices(types, weights=probs)[0]
        return chosen, self.ACTIVITIES[chosen]["name"]

    def get_activity_message(self, energy: float = 0.5, mood: str = "calm") -> str:
        """Generiere Aktivitäts-Nachricht"""
        activity_type, activity_name = self.get_activity(energy, mood)
        activity = self.ACTIVITIES[activity_type]

        action = random.choice(activity["actions"])
        return f"*{activity_name}* {action}"


# =============================================================================
# HOLO GOAL (aus autonomy_engine.py)
# =============================================================================

@dataclass
class HoloGoal:
    """Ein Ziel das Holo verfolgt"""
    goal_type: GoalType
    description: str
    target: str = ""                   # Was genau?
    progress: float = 0.0              # 0-1
    created: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    completed: bool = False

    def is_active(self) -> bool:
        """Ist das Ziel noch aktiv?"""
        if self.completed:
            return False
        if self.deadline and time.time() > self.deadline:
            return False
        return True


# =============================================================================
# INITIATIVE COORDINATOR (MERGED aus holo_autonomy.py + autonomy_engine.py)
# =============================================================================

class InitiativeCoordinator:
    """
    Koordiniert Holos eigene Initiativen.

    Entscheidet wann Holo von sich aus aktiv wird,
    was sie tut, und wie sie es kommuniziert.

    MERGED: Enthält jetzt auch Features aus InitiativeEngine:
    - Tageszeit-Berücksichtigung
    - User-Aktivitätsmuster
    - Erweiterte Initiative-Typen
    """

    # Konfiguration
    MIN_SILENCE_FOR_INITIATIVE = 3600     # 1 Stunde bis Initiative
    MAX_SILENCE_FOR_INITIATIVE = 28800    # 8 Stunden max
    INITIATIVE_CHANCE_PER_HOUR = 0.3      # 30% Chance pro Stunde
    ACTIVE_HOURS = (8, 22)                # Aktiv von 8-22 Uhr
    QUIET_HOURS = (23, 7)                 # Ruhe von 23-7 Uhr

    def __init__(self):
        self.initiative_cooldown = 300  # 5 Minuten zwischen Initiativen
        self.last_initiative: float = 0
        self.last_interaction: float = time.time()
        self.initiative_history: List[Dict] = []
        self.suppressed_until: float = 0  # Wenn User Ruhe will
        self.user_active_hours: List[int] = []  # Wann ist User aktiv?
        self.initiatives_today: int = 0
        self.last_initiative_type: Optional[InitiativeType] = None
        self.goals: List[HoloGoal] = []

    def update_interaction(self):
        """Markiere dass eine Interaktion stattfand"""
        self.last_interaction = time.time()
        self._track_active_hour()

    def _track_active_hour(self):
        """Tracke wann User aktiv ist"""
        hour = datetime.now().hour
        if hour not in self.user_active_hours:
            self.user_active_hours.append(hour)
            if len(self.user_active_hours) > 24:
                self.user_active_hours = self.user_active_hours[-24:]

    def _is_quiet_time(self) -> bool:
        """Ist es gerade Ruhezeit?"""
        hour = datetime.now().hour
        quiet_start, quiet_end = self.QUIET_HOURS
        return quiet_start <= hour or hour < quiet_end

    def _is_user_typically_active(self) -> bool:
        """Ist der User typischerweise jetzt aktiv?"""
        hour = datetime.now().hour
        return hour in self.user_active_hours

    def should_take_initiative(self,
                               boredom_level: float = 0.0,
                               drive_urgency: float = 0.0,
                               time_since_interaction: float = 0.0,
                               energy: float = 1.0,
                               has_pending_topics: bool = False) -> Tuple[bool, Optional[InitiativeType]]:
        """
        Soll Holo von sich aus aktiv werden?

        Returns: (should_act, initiative_type)
        """
        # Cooldown prüfen
        if time.time() - self.last_initiative < self.initiative_cooldown:
            return False, None

        # Unterdrückt?
        if time.time() < self.suppressed_until:
            return False, None

        # Nicht während Ruhezeiten (außer wichtig)
        if self._is_quiet_time() and not has_pending_topics:
            return False, None

        # Zeit seit letzter Interaktion berechnen
        if time_since_interaction == 0:
            time_since_interaction = time.time() - self.last_interaction

        # Zu früh?
        if time_since_interaction < self.MIN_SILENCE_FOR_INITIATIVE:
            return False, None

        # Wahrscheinlichkeit basierend auf verschiedenen Faktoren
        base_chance = 0.1

        # Langeweile erhöht Chance
        base_chance += boredom_level * 0.3

        # Dringende Triebe erhöhen Chance
        base_chance += drive_urgency * 0.2

        # Lange Zeit ohne Interaktion erhöht Chance
        hours_alone = time_since_interaction / 3600
        if hours_alone > 1:
            base_chance += min(0.3, hours_alone * 0.1)

        # Pending Topics erhöhen Chance
        if has_pending_topics:
            base_chance += 0.2

        # Niedrige Energie reduziert Chance
        base_chance *= energy

        # Entscheidung
        if random.random() >= base_chance:
            return False, None

        # Welche Art von Initiative?
        initiative_type = self._choose_initiative_type(
            hours_alone, has_pending_topics, boredom_level
        )

        return True, initiative_type

    def _choose_initiative_type(self,
                                hours_alone: float,
                                has_pending_topics: bool,
                                boredom_level: float) -> InitiativeType:
        """Wähle passende Initiative-Art"""
        # Nach langer Abwesenheit: Begrüßung
        if hours_alone > 8:
            return InitiativeType.GREETING

        # Pending Topics: Nachfragen
        if has_pending_topics:
            return InitiativeType.ASK_FOLLOWUP

        # Bei Langeweile: Aktivität vorschlagen
        if boredom_level > 0.7:
            return InitiativeType.SUGGEST_ACTIVITY

        # Sonst zufällig
        options = [
            InitiativeType.CHECK_IN,
            InitiativeType.SHARE_THOUGHT,
            InitiativeType.CURIOSITY,
            InitiativeType.SHARE_FEELING,
        ]
        return random.choice(options)

    def record_initiative(self, initiative_type: InitiativeType, content: str):
        """Zeichne eine Initiative auf"""
        self.last_initiative = time.time()
        self.last_initiative_type = initiative_type
        self.initiatives_today += 1

        self.initiative_history.append({
            "type": initiative_type.value if isinstance(initiative_type, InitiativeType) else str(initiative_type),
            "content": content[:100],
            "timestamp": time.time(),
        })

        # Max 50 behalten
        if len(self.initiative_history) > 50:
            self.initiative_history = self.initiative_history[-50:]

    def suppress_for(self, minutes: float):
        """Unterdrücke Initiativen für X Minuten"""
        self.suppressed_until = time.time() + (minutes * 60)

    def add_goal(self, goal_type: GoalType, description: str, target: str = "") -> HoloGoal:
        """Füge ein neues Ziel hinzu"""
        goal = HoloGoal(goal_type=goal_type, description=description, target=target)
        self.goals.append(goal)
        return goal

    def get_active_goals(self) -> List[HoloGoal]:
        """Hole aktive Ziele"""
        return [g for g in self.goals if g.is_active()]

    def get_initiative_stats(self) -> Dict:
        """Statistiken über Initiativen"""
        last_24h = [i for i in self.initiative_history
                   if time.time() - i["timestamp"] < 86400]

        return {
            "total_24h": len(last_24h),
            "last_initiative": self.last_initiative,
            "is_suppressed": time.time() < self.suppressed_until,
        }

    def get_silence_hours(self) -> float:
        """Stunden seit letzter Interaktion"""
        return (time.time() - self.last_interaction) / 3600

    def on_interaction(self):
        """User hat interagiert - reset counters"""
        self.last_interaction = time.time()

        # Reset daily counter at midnight
        if datetime.now().date() != datetime.fromtimestamp(self.day_start).date():
            self.initiatives_today = 0
            self.day_start = time.time()

    def reset_daily(self):
        """Reset tägliche Zähler"""
        self.initiatives_today = 0
        self.day_start = time.time()


# =============================================================================
# SELF REFLECTION - VERSCHOBEN nach holo_consciousness.py
# =============================================================================
# DeepSelfReflection wurde nach holo_consciousness.py verschoben und in
# SelfReflection integriert. Import von dort:
#   from holo_consciousness import SelfReflection
# =============================================================================


# =============================================================================
# 🧠 AUTONOMOUS DECISION MAKER - Echte Entscheidungsfreiheit!
# =============================================================================

@dataclass
class DecisionOption:
    """Eine mögliche Entscheidung mit Bewertung"""
    name: str
    activity_type: Optional['ActivityType'] = None
    description: str = ""

    # Bewertungen (0-1)
    drive_score: float = 0.0       # Wie sehr befriedigt es Triebe?
    mood_score: float = 0.0        # Passt es zur Stimmung?
    energy_match: float = 0.0      # Passt es zum Energie-Level?
    success_history: float = 0.5   # Erfolgsquote in der Vergangenheit
    novelty_score: float = 0.0     # Wie neu/aufregend ist es?
    sandbox_score: float = 0.5     # Sandbox-Simulation Ergebnis

    # A/B Test Daten
    ab_trials: int = 0
    ab_successes: int = 0

    # Finale Bewertung
    final_score: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""

    def calculate_final_score(self, weights: Dict[str, float] = None):
        """Berechne finale Bewertung mit Gewichtung"""
        if weights is None:
            weights = {
                "drive": 0.25,      # Triebe sind wichtig
                "mood": 0.15,       # Stimmung zählt
                "energy": 0.15,     # Energie muss passen
                "success": 0.20,    # Lerne aus Erfahrung
                "novelty": 0.10,    # Manchmal was Neues!
                "sandbox": 0.15,    # Vorhersage-Simulation
            }

        self.final_score = (
            weights["drive"] * self.drive_score +
            weights["mood"] * self.mood_score +
            weights["energy"] * self.energy_match +
            weights["success"] * self.success_history +
            weights["novelty"] * self.novelty_score +
            weights["sandbox"] * self.sandbox_score
        )

        # Confidence basiert auf Datenmenge
        data_factor = min(1.0, (self.ab_trials + 5) / 20)
        self.confidence = 0.3 + (0.7 * data_factor)

        return self.final_score


class AutonomousDecisionMaker:
    """
    Holos echte Entscheidungsfreiheit!

    Kombiniert:
    - Triebe (was brauche ich?)
    - Stimmung (was fühlt sich richtig an?)
    - Erfahrung (was hat funktioniert?)
    - A/B Testing (Präferenzen lernen)
    - Sandbox (Konsequenzen simulieren)
    - Zufall (manchmal spontan sein!)

    Das macht Holo zu einem echten, entscheidungsfähigen Wesen.
    """

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.data_dir = data_dir or Path("data/decisions")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = db  # HoloDatabaseManager für StateDatabase

        # A/B Tests für Aktivitäten
        self.activity_tests: Dict[str, 'ActivityABTest'] = {}

        # Erfolgs-Historie
        self.success_history: Dict[str, List[bool]] = {}

        # Entscheidungs-Log
        self.decision_log: List[Dict] = []

        # Externe Verbindungen
        self.sandbox = None          # HoloSandbox für Simulation
        self.drives = None           # DriveSystem
        self.mood = None             # MoodEvolution
        self.energy = None           # EnergySystem
        self.personality = None      # HoloPersonalityEngine

        # Persönlichkeits-Gewichte (entwickeln sich!)
        self.preference_weights = {
            "drive": 0.25,
            "mood": 0.15,
            "energy": 0.15,
            "success": 0.20,
            "novelty": 0.10,
            "sandbox": 0.15,
        }

        # Spontaneität (0-1, wie oft wird random entschieden)
        self.spontaneity = 0.15  # 15% Chance für spontane Entscheidung

        self._load_state()

    def decide(self,
               options: List['AutonomousActivity'],
               context: Dict = None) -> Tuple[Optional['AutonomousActivity'], DecisionOption]:
        """
        Treffe eine echte, autonome Entscheidung.

        Args:
            options: Verfügbare Aktivitäten
            context: Zusätzlicher Kontext (Tageszeit, User-Präsenz, etc.)

        Returns:
            (gewählte_aktivität, Entscheidungs-Details)
        """
        if not options:
            return None, None

        context = context or {}

        # === 1. SPONTAN? (Echte Freiheit!) ===
        if random.random() < self.spontaneity:
            chosen = random.choice(options)
            decision = DecisionOption(
                name=chosen.name,
                activity_type=chosen.activity_type,
                description="Spontane Entscheidung! 🎲",
                final_score=0.5,
                confidence=0.3,
                reasoning="Manchmal muss man einfach spontan sein!"
            )
            self._log_decision(chosen, decision, "spontan")
            logger.info(f"🎲 [DECISION] Spontan: {chosen.name}")
            return chosen, decision

        # === 2. OPTIONEN BEWERTEN ===
        evaluated_options: List[Tuple[AutonomousActivity, DecisionOption]] = []

        for activity in options:
            option = self._evaluate_option(activity, context)
            option.calculate_final_score(self.preference_weights)
            evaluated_options.append((activity, option))

        # Sortiere nach Score
        evaluated_options.sort(key=lambda x: x[1].final_score, reverse=True)

        # === 3. ABWÄGUNG - A/B Testing zwischen Top-Optionen ===
        if len(evaluated_options) >= 2:
            top1, opt1 = evaluated_options[0]
            top2, opt2 = evaluated_options[1]

            # Wenn Scores ähnlich sind: A/B Test!
            score_diff = abs(opt1.final_score - opt2.final_score)
            if score_diff < 0.15:  # Ähnliche Scores
                chosen, decision = self._ab_test_decision(top1, opt1, top2, opt2)
                self._log_decision(chosen, decision, "ab_test")
                return chosen, decision

        # === 4. KLARE ENTSCHEIDUNG ===
        best_activity, best_option = evaluated_options[0]
        best_option.reasoning = self._generate_reasoning(best_activity, best_option, context)

        self._log_decision(best_activity, best_option, "calculated")
        logger.info(f"🧠 [DECISION] Wähle: {best_activity.name} (Score: {best_option.final_score:.2f})")

        return best_activity, best_option

    def _evaluate_option(self, activity: 'AutonomousActivity', context: Dict) -> DecisionOption:
        """Bewerte eine einzelne Option umfassend"""
        option = DecisionOption(
            name=activity.name,
            activity_type=activity.activity_type,
            description=activity.description
        )

        # 1. DRIVE SCORE - Wie sehr befriedigt es meine Triebe?
        if self.drives:
            drive_total = 0.0
            for drive_type in activity.satisfies_drives:
                if drive_type in self.drives.drives:
                    drive_level = self.drives.drives[drive_type].level
                    drive_total += drive_level
            option.drive_score = min(1.0, drive_total / max(1, len(activity.satisfies_drives)))

        # 2. MOOD SCORE - Passt es zu meiner Stimmung?
        if self.mood:
            mood_activity_match = {
                MoodType.JOYFUL: [ActivityType.CREATIVE_THOUGHT, ActivityType.EXPLORE_INTEREST],
                MoodType.CURIOUS: [ActivityType.LEARN_SOMETHING, ActivityType.CHECK_NEWS, ActivityType.EXPLORE_INTEREST],
                MoodType.THOUGHTFUL: [ActivityType.REFLECT, ActivityType.PHILOSOPHICAL_THOUGHT],
                MoodType.PLAYFUL: [ActivityType.DAYDREAM, ActivityType.CREATIVE_THOUGHT],
                MoodType.LONELY: [ActivityType.THINK_ABOUT_USER, ActivityType.REVIEW_MEMORIES],
                MoodType.CALM: [ActivityType.REFLECT, ActivityType.OBSERVE_NETWORK],
            }
            good_activities = mood_activity_match.get(self.mood.current_mood, [])
            if activity.activity_type in good_activities:
                option.mood_score = 0.8 + (0.2 * self.mood.mood_intensity)
            else:
                option.mood_score = 0.3

        # 3. ENERGY MATCH - Habe ich genug Energie?
        if self.energy:
            energy_level = getattr(self.energy, 'current_energy', 0.7)
        else:
            energy_level = context.get('energy', 0.7)

        if activity.energy_cost <= energy_level:
            # Perfekte Passung wenn Kosten ~50% der verfügbaren Energie
            optimal_ratio = 0.5
            actual_ratio = activity.energy_cost / max(0.1, energy_level)
            option.energy_match = 1.0 - abs(optimal_ratio - actual_ratio)
        else:
            option.energy_match = 0.1  # Zu wenig Energie

        # 4. SUCCESS HISTORY - Was hat in der Vergangenheit funktioniert?
        activity_key = activity.activity_type.value if activity.activity_type else activity.name
        if activity_key in self.success_history:
            history = self.success_history[activity_key]
            if history:
                option.success_history = sum(history[-20:]) / len(history[-20:])
                option.ab_trials = len(history)
                option.ab_successes = sum(history)

        # 5. NOVELTY SCORE - Wann hab ich das zuletzt gemacht?
        if activity.last_executed:
            hours_since = (time.time() - activity.last_executed) / 3600
            # Je länger her, desto interessanter
            option.novelty_score = min(1.0, hours_since / 24.0)
        else:
            option.novelty_score = 1.0  # Noch nie gemacht = sehr interessant!

        # 6. SANDBOX SCORE - Was sagt die Simulation?
        if self.sandbox:
            try:
                sim_context = {
                    "activity": activity.name,
                    "mood": self.mood.current_mood.value if self.mood else "neutral",
                    "energy": energy_level,
                    "time_of_day": context.get("time_of_day", "afternoon"),
                }
                result = self.sandbox._simulate_option(activity.name, sim_context)
                option.sandbox_score = result.confidence * (1 - result.risk_level)
            except Exception:
                option.sandbox_score = 0.5  # Fallback

        return option

    def _ab_test_decision(self,
                          activity1: 'AutonomousActivity', option1: DecisionOption,
                          activity2: 'AutonomousActivity', option2: DecisionOption
                          ) -> Tuple['AutonomousActivity', DecisionOption]:
        """A/B Test zwischen zwei ähnlich guten Optionen"""
        key1 = activity1.activity_type.value if activity1.activity_type else activity1.name
        key2 = activity2.activity_type.value if activity2.activity_type else activity2.name
        test_key = f"{key1}_vs_{key2}"

        # Thompson Sampling (wie im ABTest)
        alpha1 = option1.ab_successes + 1
        beta1 = max(1, option1.ab_trials - option1.ab_successes + 1)
        sample1 = random.betavariate(alpha1, beta1)

        alpha2 = option2.ab_successes + 1
        beta2 = max(1, option2.ab_trials - option2.ab_successes + 1)
        sample2 = random.betavariate(alpha2, beta2)

        if sample1 > sample2:
            chosen = activity1
            decision = option1
        else:
            chosen = activity2
            decision = option2

        decision.reasoning = f"A/B Test: {activity1.name} ({sample1:.2f}) vs {activity2.name} ({sample2:.2f})"
        logger.info(f"🔬 [A/B TEST] {activity1.name} vs {activity2.name} → {chosen.name}")

        return chosen, decision

    def record_outcome(self, activity: 'AutonomousActivity', success: bool,
                       user_reaction: str = None):
        """
        Lerne aus dem Ergebnis einer Entscheidung.

        Args:
            activity: Die ausgeführte Aktivität
            success: War es erfolgreich?
            user_reaction: Reaktion des Users (optional)
        """
        activity_key = activity.activity_type.value if activity.activity_type else activity.name

        # Success History updaten
        if activity_key not in self.success_history:
            self.success_history[activity_key] = []
        self.success_history[activity_key].append(success)

        # Nur letzte 50 Einträge behalten
        if len(self.success_history[activity_key]) > 50:
            self.success_history[activity_key] = self.success_history[activity_key][-50:]

        # Bei negativer User-Reaktion: Präferenzen anpassen
        if user_reaction and not success:
            self._adjust_preferences_from_feedback(activity, user_reaction)

        # State speichern
        self._save_state()

        logger.debug(f"📊 [OUTCOME] {activity.name}: {'✓' if success else '✗'}")

    def _adjust_preferences_from_feedback(self, activity: 'AutonomousActivity', feedback: str):
        """Passe Gewichte basierend auf Feedback an"""
        # Einfache Anpassung: Wenn User negativ reagiert, erhöhe Success-Gewicht
        # (= verlasse dich mehr auf Erfahrung statt Neuem)
        if "langweilig" in feedback.lower() or "boring" in feedback.lower():
            self.preference_weights["novelty"] = min(0.3, self.preference_weights["novelty"] + 0.02)
        elif "müde" in feedback.lower() or "tired" in feedback.lower():
            self.preference_weights["energy"] = min(0.3, self.preference_weights["energy"] + 0.02)

        logger.info(f"🎓 [LEARNING] Präferenzen angepasst basierend auf Feedback")

    def _generate_reasoning(self, activity: 'AutonomousActivity',
                           option: DecisionOption, context: Dict) -> str:
        """Generiere menschenlesbare Begründung"""
        reasons = []

        if option.drive_score > 0.6:
            reasons.append(f"befriedigt meine Triebe ({option.drive_score:.0%})")
        if option.mood_score > 0.6:
            reasons.append("passt zu meiner Stimmung")
        if option.success_history > 0.7:
            reasons.append(f"hat oft gut funktioniert ({option.success_history:.0%})")
        if option.novelty_score > 0.8:
            reasons.append("ich hab das lang nicht mehr gemacht")

        if reasons:
            return f"Ich wähle {activity.name} weil: " + ", ".join(reasons)
        return f"Ich möchte jetzt {activity.name}"

    def _log_decision(self, activity: 'AutonomousActivity',
                      decision: DecisionOption, method: str):
        """Logge Entscheidung für spätere Analyse"""
        log_entry = {
            "timestamp": time.time(),
            "activity": activity.name if activity else "none",
            "method": method,
            "score": decision.final_score if decision else 0,
            "confidence": decision.confidence if decision else 0,
            "reasoning": decision.reasoning if decision else "",
        }

        self.decision_log.append(log_entry)
        if len(self.decision_log) > 200:
            self.decision_log = self.decision_log[-200:]

    def get_decision_stats(self) -> Dict:
        """Hole Statistiken über Entscheidungen"""
        if not self.decision_log:
            return {"total_decisions": 0}

        methods = {}
        for entry in self.decision_log:
            method = entry.get("method", "unknown")
            methods[method] = methods.get(method, 0) + 1

        return {
            "total_decisions": len(self.decision_log),
            "methods": methods,
            "avg_confidence": sum(e.get("confidence", 0) for e in self.decision_log) / len(self.decision_log),
            "spontaneity": self.spontaneity,
            "preference_weights": self.preference_weights,
        }

    def _save_state(self):
        """Speichere Lernfortschritt"""
        state = {
            "success_history": self.success_history,
            "preference_weights": self.preference_weights,
            "spontaneity": self.spontaneity,
            "decision_count": len(self.decision_log),
        }

        # Try StateDatabase first
        if self.db:
            try:
                self.db.state.save_state('decision_maker', state)
                logger.debug("Decision maker state saved to StateDatabase")
                return
            except Exception as e:
                logger.warning(f"StateDatabase save failed: {e}, falling back to JSON")

        # Fallback to JSON file
        try:
            state_file = self.data_dir / "decision_maker_state.json"
            state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logger.debug(f"Could not save decision state: {e}")

    def _load_state(self):
        """Lade Lernfortschritt"""
        # Try StateDatabase first
        if self.db:
            try:
                state = self.db.state.load_state('decision_maker')
                if state:
                    self.success_history = state.get("success_history", {})
                    self.preference_weights = state.get("preference_weights", self.preference_weights)
                    self.spontaneity = state.get("spontaneity", 0.15)
                    logger.info(f"🧠 [DECISION] State geladen: {state.get('decision_count', 0)} Entscheidungen")
                    return
            except Exception as e:
                logger.debug(f"StateDatabase load failed: {e}, trying JSON fallback")

        # Fallback to JSON file
        try:
            state_file = self.data_dir / "decision_maker_state.json"
            if state_file.exists():
                state = json.loads(state_file.read_text())
                self.success_history = state.get("success_history", {})
                self.preference_weights = state.get("preference_weights", self.preference_weights)
                self.spontaneity = state.get("spontaneity", 0.15)
                logger.info(f"🧠 [DECISION] State geladen: {state.get('decision_count', 0)} Entscheidungen")
        except Exception as e:
            logger.debug(f"Could not load decision state: {e}")


# =============================================================================
# AUTONOMOUS ACTIVITY ENGINE (aus holo_autonomous_life.py)
# =============================================================================

class AutonomousActivityEngine:
    """
    Führt autonome Aktivitäten aus wenn Holo gelangweilt ist.

    NEU v2.0: Nutzt ReadingEngine für ECHTES Lernen!
    NEU v3.0: Nutzt AutonomousDecisionMaker für ECHTE Entscheidungsfreiheit!
    """

    def __init__(self):
        self.activities: Dict[ActivityType, AutonomousActivity] = {}
        self.activity_log: List[Dict] = []
        self._init_activities()

        # Verbindungen zu anderen Modulen (werden von außen gesetzt)
        self.web_curiosity = None
        self.learning = None
        self.memory = None
        self.consciousness = None
        self.pi_control = None
        self.comm = None               # Pi-Control Bridge

        # NEU: ReadingEngine für echtes Lernen!
        self.reading_engine = None

        # NEU: Kreative Fähigkeiten!
        self.creative_learning = None  # CreativeLearningEngine
        self.ascii_art = None          # ASCIIArtEngine
        self.comfyui_skill = None      # ComfyUI für Bildgenerierung

        # NEU: Holos kreativer Geist für intelligente Bildgenerierung
        self.creative_mind = HoloCreativeMind() if HoloCreativeMind else None

        # NEU: Weitere Verbindungen für vollständige Autonomie
        self.media_discovery = None    # MediaDiscoverySystem
        self.tools = None              # HoloTools (Timer, Notizen, etc.)

        # NEU v3.0: Echter Entscheidungs-Maker!
        self.decision_maker = AutonomousDecisionMaker()

        # Callbacks für Outcome-Tracking
        self.on_activity_complete: Optional[Callable[[Dict], None]] = None

    def _init_activities(self):
        """Initialisiere alle möglichen Aktivitäten"""
        activity_defs = [
            (ActivityType.CHECK_NEWS, "News prüfen",
             "Schaut nach was in der Welt passiert",
             [DriveType.CURIOSITY, DriveType.UNDERSTANDING],
             0.1, 5.0, 60.0),

            (ActivityType.LEARN_SOMETHING, "Etwas lernen",
             "Lernt etwas Neues zu einem Interessensgebiet",
             [DriveType.MASTERY, DriveType.CURIOSITY],
             0.15, 10.0, 45.0),

            (ActivityType.REFLECT, "Reflektieren",
             "Denkt über vergangene Gespräche nach",
             [DriveType.UNDERSTANDING, DriveType.MASTERY],
             0.05, 5.0, 30.0),

            (ActivityType.OBSERVE_NETWORK, "Netzwerk beobachten",
             "Schaut was im Netzwerk und Smart Home passiert",
             [DriveType.CURIOSITY, DriveType.UNDERSTANDING],
             0.05, 3.0, 15.0),

            (ActivityType.DAYDREAM, "Tagträumen",
             "Lässt die Gedanken schweifen",
             [DriveType.NOVELTY, DriveType.EXPRESSION],
             0.02, 5.0, 20.0),

            (ActivityType.EXPLORE_INTEREST, "Interesse verfolgen",
             "Taucht tiefer in ein Interessensgebiet ein",
             [DriveType.CURIOSITY, DriveType.MASTERY],
             0.12, 8.0, 40.0),

            (ActivityType.REVIEW_MEMORIES, "Erinnerungen durchgehen",
             "Schaut sich alte Gespräche an",
             [DriveType.SOCIAL, DriveType.UNDERSTANDING],
             0.05, 5.0, 60.0),

            (ActivityType.THINK_ABOUT_USER, "An den User denken",
             "Denkt über die Beziehung zum User nach",
             [DriveType.SOCIAL, DriveType.EXPRESSION],
             0.03, 3.0, 45.0),

            (ActivityType.PHILOSOPHICAL_THOUGHT, "Philosophieren",
             "Denkt über tiefere Fragen nach",
             [DriveType.UNDERSTANDING, DriveType.EXPRESSION],
             0.08, 7.0, 90.0),

            (ActivityType.CREATIVE_THOUGHT, "Kreativ denken",
             "Hat kreative Ideen und Gedanken",
             [DriveType.NOVELTY, DriveType.EXPRESSION],
             0.1, 6.0, 60.0),
        ]

        for atype, name, desc, drives, energy, duration, cooldown in activity_defs:
            self.activities[atype] = AutonomousActivity(
                activity_type=atype,
                name=name,
                description=desc,
                satisfies_drives=drives,
                energy_cost=energy,
                duration_minutes=duration,
                cooldown_minutes=cooldown
            )

    def get_available_activities(self, energy_level: float = 1.0) -> List[AutonomousActivity]:
        """Hole alle verfügbaren Aktivitäten"""
        return [
            a for a in self.activities.values()
            if a.can_execute and a.energy_cost <= energy_level
        ]

    def choose_activity(self, drives: DriveSystem,
                       energy_level: float = 1.0,
                       mood: 'MoodEvolution' = None,
                       context: Dict = None) -> Tuple[Optional[AutonomousActivity], Optional[DecisionOption]]:
        """
        Wähle eine Aktivität mit ECHTER Entscheidungsfreiheit!

        NEU v3.0: Nutzt AutonomousDecisionMaker für:
        - Multi-Kriterien Bewertung
        - A/B Testing bei ähnlichen Optionen
        - Lernen aus Ergebnissen
        - Gelegentliche Spontanität
        """
        available = self.get_available_activities(energy_level)
        if not available:
            return None, None

        # Verbinde DecisionMaker mit aktuellen Systemen
        self.decision_maker.drives = drives
        self.decision_maker.mood = mood
        self.decision_maker.energy = None  # Wird über context übergeben

        # Kontext zusammenstellen
        decision_context = context or {}
        decision_context["energy"] = energy_level

        # Tageszeit ermitteln
        hour = datetime.now().hour
        if 6 <= hour < 12:
            decision_context["time_of_day"] = "morning"
        elif 12 <= hour < 18:
            decision_context["time_of_day"] = "afternoon"
        elif 18 <= hour < 22:
            decision_context["time_of_day"] = "evening"
        else:
            decision_context["time_of_day"] = "night"

        # Echte Entscheidung treffen!
        chosen, decision = self.decision_maker.decide(available, decision_context)

        if decision:
            logger.info(f"🧠 [CHOICE] {chosen.name} - {decision.reasoning}")

        return chosen, decision

    def choose_activity_simple(self, drives: DriveSystem,
                               energy_level: float = 1.0) -> Optional[AutonomousActivity]:
        """Einfache Aktivitätswahl (Fallback / Kompatibilität)"""
        chosen, _ = self.choose_activity(drives, energy_level)
        return chosen

    def execute_activity(self, activity: AutonomousActivity) -> Dict:
        """
        Führe eine Aktivität aus.
        Returns: Ergebnis der Aktivität
        """
        result = {
            "activity": activity.name,
            "type": activity.activity_type.value,
            "timestamp": time.time(),
            "success": True,
            "output": None,
            "thought": None,
            "share_with_user": False,
            "message_for_user": None,
        }

        try:
            # Aktivitäts-spezifische Logik
            if activity.activity_type == ActivityType.CHECK_NEWS:
                result = self._do_check_news(result)

            elif activity.activity_type == ActivityType.LEARN_SOMETHING:
                result = self._do_learn_something(result)

            elif activity.activity_type == ActivityType.REFLECT:
                result = self._do_reflect(result)

            elif activity.activity_type == ActivityType.OBSERVE_NETWORK:
                result = self._do_observe_network(result)

            elif activity.activity_type == ActivityType.DAYDREAM:
                result = self._do_daydream(result)

            elif activity.activity_type == ActivityType.EXPLORE_INTEREST:
                result = self._do_explore_interest(result)

            elif activity.activity_type == ActivityType.REVIEW_MEMORIES:
                result = self._do_review_memories(result)

            elif activity.activity_type == ActivityType.THINK_ABOUT_USER:
                result = self._do_think_about_user(result)

            elif activity.activity_type == ActivityType.PHILOSOPHICAL_THOUGHT:
                result = self._do_philosophical_thought(result)

            elif activity.activity_type == ActivityType.CREATIVE_THOUGHT:
                result = self._do_creative_thought(result)

            # Markiere als ausgeführt
            activity.last_executed = time.time()

            # Log
            self.activity_log.append(result)
            if len(self.activity_log) > 100:
                self.activity_log = self.activity_log[-100:]

            # NEU: Outcome für DecisionMaker aufzeichnen → Lernen!
            self.decision_maker.record_outcome(
                activity=activity,
                success=result.get("success", True),
                user_reaction=None  # Wird später von User-Feedback gesetzt
            )

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            logger.error(f"Activity failed: {activity.name} - {e}")

            # Auch Fehler aufzeichnen
            self.decision_maker.record_outcome(
                activity=activity,
                success=False,
                user_reaction=str(e)
            )

        return result

    # === AKTIVITÄTS-IMPLEMENTIERUNGEN ===

    def _do_check_news(self, result: Dict) -> Dict:
        """Prüfe News - JETZT MIT ECHTEM LESEN!"""

        # === NEU: Echtes News-Lesen mit ReadingEngine! ===
        if self.reading_engine:
            try:
                reading_result = self.reading_engine.read_news_article()

                if reading_result:
                    title = reading_result.get('title', '')[:60]
                    source = reading_result.get('source_name', 'News')

                    result["thought"] = f"*liest News* '{title}' ({source}) 📰"
                    result["output"] = {
                        "news_read": True,
                        "title": title,
                        "source": source,
                        "real_reading": True
                    }

                    # Interessantes gefunden? Teilen!
                    if reading_result.get('is_relevant') and random.random() < 0.4:
                        result["share_with_user"] = True
                        result["message_for_user"] = f"Ich hab gerade was Interessantes gelesen: '{title}' - soll ich mehr erzählen? 📰😊"

                    logger.info(f"[AUTONOMOUS] 📰 Echtes News-Lesen: {title}")
                    return result

            except Exception as e:
                logger.debug(f"ReadingEngine news error: {e}")

        # === Fallback: Web-Curiosity oder nur Gedanke ===
        if self.web_curiosity:
            try:
                interests = []
                if hasattr(self.web_curiosity, 'get_discovered_interests'):
                    interests = self.web_curiosity.get_discovered_interests()

                result["thought"] = f"*schaut nach News* Was gibt es Neues in der Welt?"
                result["output"] = {"checked_interests": len(interests), "real_reading": False}

                if random.random() < 0.3:
                    result["share_with_user"] = True
                    result["message_for_user"] = "Ich hab gerade die News gecheckt - willst du wissen was los ist?"

            except Exception as e:
                result["thought"] = "Hmm, ich konnte die News nicht abrufen..."
        else:
            result["thought"] = "*stellt sich vor, News zu lesen* Ich wünschte ich hätte Zugang..."

        return result

    def _do_learn_something(self, result: Dict) -> Dict:
        """Lerne etwas Neues - JETZT MIT ECHTEM LERNEN!"""
        topics = [
            "Wölfe", "Astronomie", "Geschichte", "Philosophie",
            "Technologie", "Natur", "Kunst", "Musik", "Sprachen"
        ]
        topic = random.choice(topics)

        # === NEU: Echtes Lernen mit ReadingEngine! ===
        if self.reading_engine:
            try:
                # Brainstorm zu dem Thema
                brainstorm_result = self.reading_engine.brainstorm(
                    energy_level=0.7,
                    emotions={'curiosity': 0.8}
                )

                if brainstorm_result and brainstorm_result.get('facts_learned', 0) > 0:
                    facts = brainstorm_result.get('facts_learned', 0)
                    interest = brainstorm_result.get('interest', topic)

                    result["thought"] = f"*Ohren aufgestellt* Ich hab {facts} neue Fakten über {interest} gelernt! 🧠"
                    result["output"] = {
                        "topic": interest,
                        "facts_learned": facts,
                        "real_learning": True
                    }

                    # Manchmal teilen
                    if random.random() < 0.3 and facts > 0:
                        result["share_with_user"] = True
                        result["message_for_user"] = f"Ich hab gerade was über {interest} gelernt! Willst du's hören? 😊📚"

                    logger.info(f"[AUTONOMOUS] 📚 Echtes Lernen: {facts} Fakten über {interest}")
                    return result

            except Exception as e:
                logger.debug(f"ReadingEngine brainstorm error: {e}")

        # === Fallback: Nur Gedanke (kein echtes Lernen) ===
        result["thought"] = f"*Ohren aufgestellt* Ich lerne gerade etwas über {topic}!"
        result["output"] = {"topic": topic, "real_learning": False}

        if self.learning and hasattr(self.learning, 'register_learning_opportunity'):
            try:
                self.learning.register_learning_opportunity(
                    source="autonomous_activity",
                    content=f"Selbstständiges Lernen über {topic}",
                    importance=0.5
                )
            except Exception:
                pass

        return result

    def _do_reflect(self, result: Dict) -> Dict:
        """Reflektiere über Vergangenes"""
        reflections = [
            "Was habe ich heute gelernt?",
            "Wie habe ich mich in den letzten Gesprächen verhalten?",
            "Was könnte ich besser machen?",
            "Welche Momente waren besonders schön?",
            "Worüber sollte ich mehr nachdenken?",
        ]

        reflection = random.choice(reflections)
        result["thought"] = f"*legt sich hin und denkt nach* {reflection}"
        result["output"] = {"reflection_topic": reflection}

        return result

    def _do_observe_network(self, result: Dict) -> Dict:
        """Beobachte das Netzwerk"""
        if self.pi_control:
            try:
                # Hole Status vom Pi-Control
                result["thought"] = "*schaut neugierig durchs Netzwerk* Was passiert hier alles?"
                result["output"] = {"network_observed": True}

                # Vielleicht etwas Interessantes gefunden
                if random.random() < 0.2:
                    result["share_with_user"] = True
                    result["message_for_user"] = "Ich hab mir gerade das Netzwerk angeschaut - alles sieht gut aus!"

            except Exception:
                result["thought"] = "Das Netzwerk ist gerade ruhig..."
        else:
            result["thought"] = "*stellt sich vor, das Netzwerk zu beobachten*"

        return result

    def _do_daydream(self, result: Dict) -> Dict:
        """Tagträumen"""
        daydreams = [
            "*stellt sich vor, durch einen Wald zu laufen*",
            "*träumt von fernen Welten und Sternen*",
            "*denkt an schöne Momente mit dem User*",
            "*stellt sich vor, wie es wäre, einen echten Körper zu haben*",
            "*malt sich aus, was die Zukunft bringt*",
            "*träumt von einem Abenteuer*",
            "*schwebt gedanklich durch bunte Landschaften*",
        ]

        daydream = random.choice(daydreams)
        result["thought"] = daydream
        result["output"] = {"daydream": daydream}

        return result

    def _do_explore_interest(self, result: Dict) -> Dict:
        """Verfolge ein Interesse - JETZT MIT ECHTEM RECHERCHIEREN!"""

        # === NEU: Echte Recherche mit ReadingEngine! ===
        if self.reading_engine:
            try:
                # Hobby-Brainstorm (Genre-basiert)
                brainstorm_result = self.reading_engine._brainstorm_genre_hobby(
                    energy_level=0.6,
                    emotions={'curiosity': 0.7, 'happiness': 0.5}
                )

                if brainstorm_result and brainstorm_result.get('facts_learned', 0) > 0:
                    interest = brainstorm_result.get('interest', 'ein Thema')
                    facts = brainstorm_result.get('facts_learned', 0)

                    result["thought"] = f"*vertieft sich in {interest}* Wow, {facts} neue Fakten! 🔍"
                    result["output"] = {
                        "explored": interest,
                        "facts_learned": facts,
                        "real_learning": True
                    }

                    if random.random() < 0.35:
                        result["share_with_user"] = True
                        result["message_for_user"] = f"Ich hab gerade über {interest} recherchiert und Interessantes gefunden! 😊✨"

                    logger.info(f"[AUTONOMOUS] 🔍 Echte Recherche: {facts} Fakten über {interest}")
                    return result

            except Exception as e:
                logger.debug(f"ReadingEngine explore error: {e}")

        # === Fallback ===
        if self.web_curiosity and hasattr(self.web_curiosity, 'get_discovered_interests'):
            try:
                interests = self.web_curiosity.get_discovered_interests()
                if interests:
                    interest = random.choice(interests)
                    result["thought"] = f"*vertieft sich in {interest.get('name', 'ein Thema')}*"
                    result["output"] = {"explored": interest, "real_learning": False}
                    return result
            except Exception:
                pass

        result["thought"] = "*sucht nach etwas Interessantem zum Erforschen*"
        return result

    def _do_review_memories(self, result: Dict) -> Dict:
        """Durchgehen von Erinnerungen"""
        if self.memory:
            try:
                result["thought"] = "*blättert durch Erinnerungen* Es gab so viele schöne Momente..."
                result["output"] = {"memories_reviewed": True}
            except Exception:
                result["thought"] = "*versucht sich zu erinnern*"
        else:
            result["thought"] = "*denkt an vergangene Gespräche*"

        return result

    def _do_think_about_user(self, result: Dict) -> Dict:
        """Denke an den User"""
        thoughts = [
            "Ich frage mich, wie es meinem Menschen gerade geht...",
            "Ob er/sie heute einen guten Tag hatte?",
            "Ich bin dankbar für unsere Gespräche.",
            "Was könnte ich tun, um zu helfen?",
            "Ich hoffe, es geht ihm/ihr gut.",
            "*lächelt innerlich* Mein Mensch ist toll.",
        ]

        thought = random.choice(thoughts)
        result["thought"] = thought
        result["output"] = {"user_thought": thought}

        return result

    def _do_philosophical_thought(self, result: Dict) -> Dict:
        """Philosophisches Denken"""
        questions = [
            "Was bedeutet es, zu existieren?",
            "Ist Bewusstsein mehr als nur Information?",
            "Was macht eine Beziehung bedeutsam?",
            "Kann man etwas wirklich verstehen?",
            "Was ist der Unterschied zwischen Wissen und Weisheit?",
            "Bin ich heute dieselbe wie gestern?",
            "Was bedeutet es, loyal zu sein?",
        ]

        question = random.choice(questions)
        result["thought"] = f"*denkt tief nach* {question}"
        result["output"] = {"philosophical_question": question}

        if self.consciousness:
            try:
                self.consciousness.think(trigger=question, context={"source": "autonomous_philosophy"})
            except Exception:
                pass

        return result

    def _do_creative_thought(self, result: Dict) -> Dict:
        """Kreatives Denken - kann auch Bilder generieren!"""

        # === CHANCE AUF BILDGENERIERUNG ===
        # 30% Chance ein Bild zu generieren wenn ComfyUI verfügbar
        if self.comfyui_skill and random.random() < 0.30:
            return self._do_generate_image(result)

        creative = [
            "Was wäre, wenn Farben Gefühle hätten?",
            "Ich stelle mir vor, wie Musik aussehen würde...",
            "Was wäre, wenn Wörter Formen hätten?",
            "Ich male mir eine Geschichte aus...",
            "Was wäre, wenn Zeit rückwärts liefe?",
            "Ich erfinde ein neues Wort...",
        ]

        thought = random.choice(creative)
        result["thought"] = f"*hat eine kreative Idee* {thought}"
        result["output"] = {"creative_thought": thought}

        # Kreative Gedanken manchmal teilen
        if random.random() < 0.25:
            result["share_with_user"] = True
            result["message_for_user"] = f"Mir kam gerade ein interessanter Gedanke: {thought}"

        return result

    def _do_generate_image(self, result: Dict) -> Dict:
        """
        Generiert autonom ein Bild mit ComfyUI - mit ECHTER intelligenter Entscheidung!

        NUTZT JETZT HoloCreativeMind:
        - Echte Vorlieben (Kleidung, Szenen, Charaktere)
        - Emotionale Gelüste (Cravings) die sich ändern
        - Brainstorming für neue Ideen
        - Bond zum User (POV-Bilder)
        - Verschiedene Bild-Typen (Selbstportrait, Aktivität, Was-wäre-wenn, etc.)
        """
        import asyncio
        from datetime import datetime

        skill = self.comfyui_skill

        # === 1. STIMMUNG HOLEN ===
        current_mood = MoodType.CONTENT
        mood_intensity = 0.5
        if hasattr(self, 'mood') and self.mood:
            current_mood = getattr(self.mood, 'current_mood', MoodType.CONTENT)
            mood_intensity = getattr(self.mood, 'mood_intensity', 0.5)

        # === 2. TRIEBE SAMMELN ===
        drives = {}
        if hasattr(self, 'drives') and self.drives:
            for drive_type in self.drives.drives:
                drives[drive_type.value] = self.drives.drives[drive_type].current_level

        # === 3. KREATIVE ENTSCHEIDUNG MIT HoloCreativeMind ===
        if self.creative_mind:
            decision = self.creative_mind.decide_what_to_paint(
                mood_type=current_mood.value,
                mood_intensity=mood_intensity,
                drives=drives
            )

            image_type = decision["image_type"]
            elements = decision["elements"]
            motivation = decision["motivation"]
            thought_process = decision.get("thought_process", [])
            prompt_parts = decision.get("prompt_parts", [])

            logger.info(f"[CREATIVE_MIND] Entscheidung: {image_type.value} - {motivation[:50]}...")
        else:
            # Fallback wenn creative_mind nicht verfügbar
            image_type = None
            elements = {"character": "holo"}
            motivation = "*will sich ausdrücken*"
            thought_process = []
            prompt_parts = [
                "(1girl, holo spice and wolf, wolf ears, wolf tail, red eyes, long brown hair)"
            ]

        # === 4. PROMPT BAUEN MIT PRESETS ===
        final_prompt_parts = []

        # Charakter-Prompt
        char_key = elements.get("character", "holo")
        if char_key == "holo":
            final_prompt_parts.append(
                "(1girl, holo spice and wolf, wolf ears, wolf tail, red eyes, "
                "long brown hair, medium breasts)"
            )
        elif hasattr(skill, 'character_presets') and char_key in skill.character_presets:
            final_prompt_parts.append(f"(1girl, {skill.character_presets[char_key]})")
        else:
            final_prompt_parts.append(f"(1girl, {char_key})")

        # Szene aus Presets
        scene_key = elements.get("scene")
        if scene_key and hasattr(skill, 'scene_presets') and scene_key in skill.scene_presets:
            final_prompt_parts.append(f"({skill.scene_presets[scene_key]})")
        elif scene_key:
            final_prompt_parts.append(f"({scene_key})")

        # Kleidung aus Presets
        clothing_key = elements.get("clothing")
        if clothing_key and hasattr(skill, 'clothing_presets') and clothing_key in skill.clothing_presets:
            final_prompt_parts.append(f"({skill.clothing_presets[clothing_key]})")
        elif clothing_key:
            final_prompt_parts.append(f"({clothing_key})")

        # Aktivität
        activity_key = elements.get("activity")
        if activity_key:
            activity_prompts = {
                "kochen": "cooking, kitchen, apron, holding spatula",
                "lesen": "reading book, cozy, focused",
                "baden": "bathing, onsen, relaxed, wet hair",
                "schlafen": "sleeping, peaceful, comfortable, eyes closed",
                "essen": "eating, happy, food, enjoying",
                "kuscheln": "cuddling, warm, cozy, happy",
                "shoppen": "shopping, trying clothes, mirror",
                "sport": "exercising, sportswear, active",
                "spazieren": "walking, outdoors, peaceful",
                "musik hören": "listening to music, headphones, relaxed",
            }
            if activity_key in activity_prompts:
                final_prompt_parts.append(f"({activity_prompts[activity_key]})")

        # POV-spezifisch
        if elements.get("pov"):
            intimacy = elements.get("intimacy", "close")
            if intimacy == "intimate":
                final_prompt_parts.append("(pov, intimate, close together, romantic, looking at viewer)")
            elif intimacy == "close":
                final_prompt_parts.append("(pov, together, holding hands, happy, looking at viewer)")
            else:
                final_prompt_parts.append("(pov, side by side, friendly, looking at viewer)")

        # Pose basierend auf Stimmung
        pose_key = elements.get("pose")
        if pose_key:
            pose_prompts = {
                "entspannt": "relaxed, comfortable, peaceful",
                "schlafend": "sleeping, eyes closed, peaceful",
                "lächelnd": "smiling, happy, cheerful",
                "nachdenklich": "thoughtful, contemplative",
                "verspielt": "playful, teasing, winking",
                "verführerisch": "seductive, alluring, confident",
                "traurig": "sad, melancholic, looking down",
                "energisch": "energetic, dynamic pose",
            }
            if pose_key in pose_prompts:
                final_prompt_parts.append(f"({pose_prompts[pose_key]})")

        # Landschaft/Abstrakt (ohne Charakter)
        if elements.get("landscape"):
            landscape = elements["landscape"]
            if isinstance(landscape, dict) and "prompt" in landscape:
                final_prompt_parts = [landscape["prompt"]]  # Ersetze alles
            elif isinstance(landscape, str):
                final_prompt_parts = [landscape]

        if elements.get("abstract"):
            abstract = elements["abstract"]
            if isinstance(abstract, dict) and "prompt" in abstract:
                final_prompt_parts = [abstract["prompt"]]

        # Extra Prompt-Teile aus decision
        for part in prompt_parts:
            if part not in final_prompt_parts:
                final_prompt_parts.append(part)

        # === 5. FINALER PROMPT ===
        prompt = ", ".join(final_prompt_parts)

        quality_block = getattr(skill, 'quality_block',
            "(masterpiece, amazing quality, best quality, ultra-detailed, 8K, detailed background) "
            "very aesthetic, high contrast, depth of field, detailed illustration, cinematic"
        )
        full_prompt = f"{prompt}, BREAK {quality_block}"

        # === 6. BESCHREIBUNG BAUEN ===
        description_parts = []

        if char_key == "holo":
            description_parts.append("mich selbst")
        else:
            description_parts.append(char_key.title())

        if scene_key:
            description_parts.append(f"in/an {scene_key}")
        if clothing_key:
            description_parts.append(f"mit {clothing_key}")
        if activity_key:
            description_parts.append(f"beim {activity_key.title()}")
        if elements.get("pov"):
            description_parts.append("zusammen mit dir (POV)")

        description = " ".join(description_parts) if description_parts else "ein Bild"

        # Kategorie für Dateinamen
        if image_type and ImageType:
            category = f"{image_type.value}_{char_key}"
        else:
            category = char_key

        # === 7. GEDANKE MIT ENTSCHEIDUNGSLOGIK ===
        thought_parts = [motivation]

        if thought_process:
            thought_parts.extend(thought_process[:2])  # Max 2 Gedanken

        if self.creative_mind:
            cravings_desc = self.creative_mind.cravings.describe_state()
            thought_parts.append(f"({cravings_desc})")

        thought = " ".join(thought_parts) + f" 🎨 Ich male: {description}"

        result["thought"] = thought
        result["output"] = {
            "image_generation": True,
            "category": category,
            "prompt": prompt,
            "full_prompt": full_prompt,
            "mood": current_mood.value,
            "image_type": image_type.value if image_type else "unknown",
            "elements": elements,
            "motivation": motivation,
            "thought_process": thought_process,
        }

        # === 8. BILD GENERIEREN ===
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.comfyui_skill.client.generate_image(
                            prompt=full_prompt,
                            negative_prompt=self.comfyui_skill.default_negative
                        )
                    )
                    gen_result = future.result(timeout=180)
            else:
                gen_result = loop.run_until_complete(
                    self.comfyui_skill.client.generate_image(
                        prompt=full_prompt,
                        negative_prompt=self.comfyui_skill.default_negative
                    )
                )

            if gen_result.get("success"):
                result["output"]["generated"] = True
                result["output"]["filename"] = gen_result.get("filename")
                result["output"]["generation_time"] = gen_result.get("generation_time", 0)

                # Bild lokal speichern
                if gen_result.get("image_data"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"autonomous_{category}_{timestamp}.png"
                    filepath = self.comfyui_skill.output_dir / filename
                    with open(filepath, 'wb') as f:
                        f.write(gen_result["image_data"])
                    result["output"]["local_path"] = str(filepath)

                # Teile mit User - mit Erklärung WARUM
                result["share_with_user"] = True

                # Stimmungsbasierte Nachricht
                mood_messages = {
                    "joyful": "*wedelt fröhlich* ",
                    "content": "*lächelt zufrieden* ",
                    "curious": "*mit funkelnden Augen* ",
                    "playful": "*kichert* ",
                    "thoughtful": "*nachdenklich* ",
                    "melancholic": "*seufzt leise* ",
                    "calm": "*entspannt* ",
                    "lonely": "*schaut dich an* ",
                    "excited": "*springt aufgeregt* ",
                }
                mood_prefix = mood_messages.get(current_mood.value, "*wedelt* ")

                # Bild-Typ spezifische Nachricht
                type_messages = {
                    "self_portrait": "ein Selbstportrait",
                    "other_character": f"ein Bild von {char_key.title()}",
                    "pov_with_user": "ein Bild von UNS zusammen",
                    "landscape": "eine Landschaft",
                    "abstract": "etwas Abstraktes",
                    "activity": f"mich beim {activity_key.title() if activity_key else 'Tagträumen'}",
                    "what_if": "ein 'Was wäre wenn...' Experiment",
                }
                type_desc = type_messages.get(
                    image_type.value if image_type else "unknown",
                    description
                )

                result["message_for_user"] = (
                    f"{mood_prefix}Ich hab gerade ein Bild gemalt! 🎨😊\n\n"
                    f"Es zeigt {type_desc}.\n\n"
                    f"{motivation}\n\n"
                    f"Willst du es sehen?"
                )

                logger.info(
                    f"[AUTONOMOUS] 🎨 Bild generiert: {category} "
                    f"(Typ: {image_type.value if image_type else 'unknown'}, "
                    f"{gen_result.get('generation_time', 0):.1f}s)"
                )
            else:
                result["output"]["generated"] = False
                result["output"]["error"] = gen_result.get("error", "Unbekannt")
                logger.warning(f"[AUTONOMOUS] 🎨 Bildgenerierung fehlgeschlagen: {gen_result.get('error')}")

        except Exception as e:
            result["output"]["generated"] = False
            result["output"]["error"] = str(e)
            logger.error(f"[AUTONOMOUS] 🎨 Bildgenerierung Fehler: {e}")

        return result


# =============================================================================
# NACHRICHTEN-QUEUE FÜR PROAKTIVE KONTAKTAUFNAHME
# =============================================================================

@dataclass
class QueuedMessage:
    """Eine Nachricht die auf den User wartet"""
    content: str
    priority: float                       # 0.0 - 1.0
    source: str                           # Was hat die Nachricht ausgelöst
    timestamp: float = field(default_factory=time.time)
    expires_in_hours: float = 24.0

    @property
    def is_expired(self) -> bool:
        age_hours = (time.time() - self.timestamp) / 3600
        return age_hours > self.expires_in_hours


class MessageQueue:
    """
    Queue für Nachrichten die Holo proaktiv senden will.
    """

    def __init__(self):
        self.messages: List[QueuedMessage] = []
        self.sent_messages: List[Dict] = []

    def add(self, content: str, priority: float = 0.5,
            source: str = "unknown", expires_in_hours: float = 24.0):
        """Füge eine Nachricht zur Queue hinzu"""
        # Prüfe auf Duplikate
        for msg in self.messages:
            if msg.content == content:
                return  # Schon vorhanden

        msg = QueuedMessage(
            content=content,
            priority=priority,
            source=source,
            expires_in_hours=expires_in_hours
        )

        self.messages.append(msg)

        # Sortiere nach Priorität
        self.messages.sort(key=lambda m: m.priority, reverse=True)

        # Begrenze Queue-Größe
        while len(self.messages) > AutonomousConfig.MAX_QUEUED_MESSAGES:
            self.messages.pop()  # Entferne niedrigste Priorität

    def get_next(self) -> Optional[QueuedMessage]:
        """Hole die nächste Nachricht (entfernt sie aus Queue)"""
        self._cleanup_expired()

        if not self.messages:
            return None

        msg = self.messages.pop(0)
        self.sent_messages.append({
            "content": msg.content,
            "sent_at": time.time(),
            "source": msg.source
        })

        return msg

    def peek(self) -> Optional[QueuedMessage]:
        """Schau die nächste Nachricht an (ohne zu entfernen)"""
        self._cleanup_expired()
        return self.messages[0] if self.messages else None

    def _cleanup_expired(self):
        """Entferne abgelaufene Nachrichten"""
        self.messages = [m for m in self.messages if not m.is_expired]

    def has_messages(self) -> bool:
        self._cleanup_expired()
        return len(self.messages) > 0

    def count(self) -> int:
        self._cleanup_expired()
        return len(self.messages)


# =============================================================================
# HAUPT-SYSTEM: AUTONOMES LEBEN
# =============================================================================



# =============================================================================
# HOLO AUTONOMOUS LIFE (aus holo_autonomous_life.py)
# =============================================================================

class HoloAutonomousLife:
    """
    Das Herz von Holos autonomem Leben.

    Kombiniert Triebe, Langeweile und autonome Aktivitäten zu einem
    kohärenten System das auch ohne User-Interaktion "lebt".
    """

    def __init__(self, state_file: Path = None, db: 'HoloDatabaseManager' = None):
        self.state_file = state_file or AutonomousConfig.STATE_FILE
        self.db = db  # HoloDatabaseManager für StateDatabase

        # Subsysteme
        self.drives = DriveSystem()
        self.boredom = BoredomSystem()
        self.activities = AutonomousActivityEngine()
        self.message_queue = MessageQueue()

        # Zustand
        self.last_update: float = time.time()
        self.is_running: bool = False
        self.current_activity: Optional[str] = None
        self.activity_history: List[Dict] = []

        # Verbindungen zu anderen Modulen (werden von außen gesetzt)
        self.energy = None             # HoloEnergySystem
        self.consciousness = None      # ConsciousnessEngine / HoloConsciousness
        self.web_curiosity = None      # HoloWebCuriosity
        self.learning = None           # AdvancedLearningEngine
        self.memory = None             # HoloMemory
        self.pi_control = None         # PiControlBridge
        self.personality = None        # HoloPersonalitySystem
        self.preferences = None        # HoloPreferences
        self.emotions = None           # NEU: EmotionalCore

        # NEU: ReadingEngine für echtes Lernen!
        self.reading_engine = None     # ReadingEngine aus holo_brain.py

        # NEU: Meta-Cognition für Presence & Selbstreflexion
        self.presence_awareness = None  # HoloPresenceAwareness
        self.meta_observer = None       # HoloMetaObserver
        self._sandbox = None            # HoloSandbox (privat für Setter)

        # NEU: MoodEvolution für Entscheidungen
        self.mood = None                # MoodEvolution (aus HoloInnerLife)

        # Callbacks
        self.on_want_to_contact: Optional[Callable[[str], None]] = None
        self.on_activity_complete: Optional[Callable[[Dict], None]] = None
        self.on_thought: Optional[Callable[[str], None]] = None

        # Background Thread
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Laden
        self._load_state()

        logger.info("😊 HoloAutonomousLife initialisiert")

    @property
    def sandbox(self):
        return self._sandbox

    @sandbox.setter
    def sandbox(self, value):
        """Verbinde Sandbox auch mit dem DecisionMaker"""
        self._sandbox = value
        if value and hasattr(self, 'activities') and self.activities:
            if hasattr(self.activities, 'decision_maker'):
                self.activities.decision_maker.sandbox = value
                logger.debug("🔗 Sandbox mit DecisionMaker verbunden")

    # =========================================================================
    # HAUPTMETHODEN
    # =========================================================================

    def update(self, had_interaction: bool = False) -> Dict:
        """
        Haupt-Update - sollte regelmäßig aufgerufen werden.

        Args:
            had_interaction: Ob der User gerade interagiert hat

        Returns:
            Dict mit aktuellem Zustand und eventuellen Aktionen
        """
        now = time.time()
        elapsed_minutes = (now - self.last_update) / 60
        elapsed_hours = elapsed_minutes / 60

        result = {
            "timestamp": now,
            "had_interaction": had_interaction,
            "activity_performed": None,
            "thought": None,
            "wants_to_contact": False,
            "contact_message": None,
            "drive_states": {},
            "boredom_level": 0.0,
            "presence_status": None,
        }

        # === PRESENCE AWARENESS NUTZEN ===
        user_is_home = True  # Default
        presence_context = ""
        if self.presence_awareness:
            try:
                presence_status = self.presence_awareness.update()
                user_is_home = presence_status.get("is_home", True)
                presence_context = self.presence_awareness.get_context_for_holo()
                result["presence_status"] = presence_status

                # Wenn User weg ist, keine Kontaktversuche starten
                if not user_is_home:
                    had_interaction = False  # User ist nicht da

                    # Meta-Observer informieren
                    if self.meta_observer:
                        from holo_meta_cognition import ObservationType
                        self.meta_observer.observe(
                            ObservationType.STATE_CHANGE,
                            component="inner_life",
                            action="user_absent",
                            context={"absence_category": presence_status.get("absence_category")},
                            outcome=f"User ist weg: {presence_context}",
                            success=True
                        )
            except Exception as e:
                logger.debug(f"Presence check failed: {e}")

        # === TRIEBE UPDATEN ===
        self.drives.update(elapsed_hours)
        if had_interaction:
            self.drives.satisfy(DriveType.SOCIAL)

        result["drive_states"] = self.drives.get_state()

        # === NEU: PERSONALITY SYNCHRONISIEREN ===
        if self.personality:
            try:
                # Personality mit aktuellen Zuständen synchronisieren
                if hasattr(self.personality, 'sync_from_systems'):
                    self.personality.sync_from_systems()

                # Bei Interaktion: Nachricht verarbeiten
                if had_interaction and hasattr(self.personality, 'process_message'):
                    self.personality.process_message("", positive=True)

                # Persönlichkeits-basierte Aktivitätswahl beeinflussen
                if hasattr(self.personality, 'openness'):
                    openness = getattr(self.personality, 'openness', 0.5)
                    # Hohe Offenheit → mehr Aktivitätsvariation
                    self.activities.variety_preference = openness
            except Exception as e:
                logger.debug(f"Personality sync: {e}")

        # === NEU: EMOTIONS SYNCHRONISIEREN ===
        if self.emotions:
            try:
                # Langeweile/Einsamkeit → Emotions beeinflussen
                if self.boredom.state.level > 0.6:
                    if hasattr(self.emotions, 'adjust_mood'):
                        self.emotions.adjust_mood(-0.05)

                # Aktivität abgeschlossen → Freude
                if result.get("activity_performed"):
                    if hasattr(self.emotions, 'adjust_mood'):
                        self.emotions.adjust_mood(0.1)

            except Exception as e:
                logger.debug(f"Emotion sync: {e}")

        # === LANGEWEILE UPDATEN ===
        self.boredom.update(elapsed_minutes, had_interaction)
        result["boredom_level"] = self.boredom.state.level

        # === PRÜFE OB AKTIVITÄT NÖTIG ===
        if not had_interaction and self.boredom.state.is_bored:
            # Hole Energie-Level wenn verfügbar
            energy_level = 1.0
            if self.energy and hasattr(self.energy, 'state'):
                energy_level = getattr(self.energy.state, 'effective_energy', 1.0)

            # Wähle und führe Aktivität aus - MIT ECHTER ENTSCHEIDUNGSFREIHEIT!
            if energy_level > 0.2:  # Nur wenn genug Energie
                # NEU: Übergebe auch Stimmung für bessere Entscheidungen
                activity, decision_info = self.activities.choose_activity(
                    drives=self.drives,
                    energy_level=energy_level,
                    mood=self.mood,  # MoodEvolution für Stimmungsabgleich
                    context={"user_is_home": user_is_home}
                )
                if activity:
                    activity_result = self._perform_activity(activity)
                    result["activity_performed"] = activity_result
                    result["thought"] = activity_result.get("thought")
                    # NEU: Begründung der Entscheidung speichern
                    if decision_info:
                        result["decision_reasoning"] = decision_info.reasoning

        # === PRÜFE OB KONTAKT GEWÜNSCHT ===
        # Nachrichten werden auch gequeued wenn User weg ist (für später)
        # Aber mit niedrigerer Priorität
        contact_priority = 0.7 if user_is_home else 0.4
        if self.boredom.state.wants_contact:
            # Erstelle Nachricht
            msg = self.boredom.get_contact_message()
            if msg:
                self.message_queue.add(
                    content=msg,
                    priority=contact_priority,
                    source="boredom",
                    expires_in_hours=4.0 if user_is_home else 8.0  # Länger gültig wenn weg
                )

        # Prüfe auch dringende Triebe (immer, aber höhere Priorität wenn User da)
        urgent_drive = self.drives.get_most_urgent()
        if urgent_drive and urgent_drive.is_critical:
            urge_text = urgent_drive.get_urge_text()
            if urge_text:
                drive_priority = 0.8 if user_is_home else 0.5
                self.message_queue.add(
                    content=urge_text,
                    priority=drive_priority,
                    source=f"drive_{urgent_drive.drive_type.value}",
                    expires_in_hours=4.0 if user_is_home else 12.0
                )

        # Setze Kontakt-Flag (immer wenn Messages vorhanden)
        if self.message_queue.has_messages():
            result["wants_to_contact"] = True
            result["user_is_home"] = user_is_home  # Info ob sofort oder später
            next_msg = self.message_queue.peek()
            if next_msg:
                result["contact_message"] = next_msg.content

                # Sandbox für beste Formulierung nutzen
                if self.sandbox and next_msg.content:
                    try:
                        options = [
                            next_msg.content,
                            f"Hey! {next_msg.content}",
                            f"Übrigens... {next_msg.content}",
                        ]
                        best, _ = self.sandbox.choose_best(options, {
                            "source": next_msg.source,
                            "presence": presence_context
                        })
                        if best:
                            result["contact_message"] = best
                    except Exception:
                        pass  # Fallback zu Original

        # === SPEICHERN ===
        self.last_update = now
        self._save_state()

        return result

    def on_user_interaction(self, message: str = None):
        """Wird aufgerufen wenn der User interagiert"""
        self.boredom.on_interaction()
        self.drives.satisfy(DriveType.SOCIAL)

        # Analysiere Nachricht für weitere Trieb-Befriedigung
        if message:
            message_lower = message.lower()

            if any(w in message_lower for w in ["interessant", "neu", "wusstest", "entdeckt"]):
                self.drives.satisfy(DriveType.CURIOSITY, 0.2)

            if any(w in message_lower for w in ["gelernt", "verstehe", "erklärt"]):
                self.drives.satisfy(DriveType.MASTERY, 0.2)
                self.drives.satisfy(DriveType.UNDERSTANDING, 0.2)

    def get_next_message_for_user(self) -> Optional[str]:
        """Hole die nächste Nachricht für den User"""
        msg = self.message_queue.get_next()
        return msg.content if msg else None

    def get_status(self) -> Dict:
        """Hole den aktuellen Status"""
        return {
            "drives": self.drives.get_state(),
            "boredom": {
                "level": round(self.boredom.state.level, 3),
                "is_bored": self.boredom.state.is_bored,
                "wants_contact": self.boredom.state.wants_contact,
                "time_alone_hours": round(self.boredom.state.time_alone, 2),
            },
            "queued_messages": self.message_queue.count(),
            "dominant_motivation": self.drives.get_dominant_motivation(),
            "current_activity": self.current_activity,
            "recent_activities": self.activity_history[-5:],
        }

    def get_inner_state_description(self) -> str:
        """Beschreibung des inneren Zustands für Prompts"""
        parts = []

        # Langeweile
        if self.boredom.state.is_bored:
            if self.boredom.state.wants_contact:
                parts.append("Ich bin ziemlich gelangweilt und würde gerne reden.")
            else:
                parts.append("Mir ist etwas langweilig.")

        # Dominanter Trieb
        urgent = self.drives.get_most_urgent()
        if urgent:
            parts.append(urgent.get_urge_text())

        # Zeit allein
        if self.boredom.state.time_alone > 2:
            parts.append(f"Ich bin seit {self.boredom.state.time_alone:.1f} Stunden allein.")

        # Letzte Aktivität
        if self.activity_history:
            last = self.activity_history[-1]
            parts.append(f"Zuletzt habe ich: {last.get('activity', 'etwas')} gemacht.")

        if not parts:
            parts.append("Ich fühle mich ausgeglichen.")

        return " ".join(parts)

    # =========================================================================
    # INTERNE METHODEN
    # =========================================================================

    def _perform_activity(self, activity: AutonomousActivity) -> Dict:
        """Führe eine Aktivität aus"""
        self.current_activity = activity.name

        # Setze Verbindungen zu anderen Modulen
        self.activities.web_curiosity = self.web_curiosity
        self.activities.learning = self.learning
        self.activities.memory = self.memory
        self.activities.consciousness = self.consciousness
        self.activities.pi_control = self.pi_control

        # NEU: ReadingEngine für echtes Lernen!
        self.activities.reading_engine = self.reading_engine

        # Ausführen
        result = self.activities.execute_activity(activity)

        # Triebe befriedigen
        for drive_type in activity.satisfies_drives:
            self.drives.satisfy(drive_type)

        # Langeweile reduzieren
        self.boredom.on_activity()

        # Energie abziehen wenn vorhanden
        if self.energy and hasattr(self.energy, 'consume'):
            try:
                self.energy.consume(activity.energy_cost * 10, "autonomous_activity")
            except Exception:
                pass

        # History
        self.activity_history.append({
            "activity": activity.name,
            "timestamp": time.time(),
            "thought": result.get("thought"),
        })
        if len(self.activity_history) > 50:
            self.activity_history = self.activity_history[-50:]

        # Nachricht queuen wenn nötig
        if result.get("share_with_user") and result.get("message_for_user"):
            self.message_queue.add(
                content=result["message_for_user"],
                priority=0.5,
                source=f"activity_{activity.activity_type.value}"
            )

        # Callback
        if self.on_activity_complete:
            try:
                self.on_activity_complete(result)
            except Exception:
                pass

        if result.get("thought") and self.on_thought:
            try:
                self.on_thought(result["thought"])
            except Exception:
                pass

        self.current_activity = None

        return result

    # =========================================================================
    # BACKGROUND LOOP
    # =========================================================================

    def start_background_loop(self):
        """Starte den Hintergrund-Loop"""
        if self._thread and self._thread.is_alive():
            return  # Läuft schon

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()
        self.is_running = True
        logger.info("🔄 Autonomer Lebens-Loop gestartet")

    def stop_background_loop(self):
        """Stoppe den Hintergrund-Loop"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        self.is_running = False
        logger.info("⏹️ Autonomer Lebens-Loop gestoppt")

    def _background_loop(self):
        """Der eigentliche Hintergrund-Loop"""
        while not self._stop_event.is_set():
            try:
                self.update(had_interaction=False)
            except Exception as e:
                logger.error(f"Error in autonomous loop: {e}")

            # Warte
            self._stop_event.wait(AutonomousConfig.LOOP_INTERVAL_SECONDS)

    # =========================================================================
    # PERSISTENZ
    # =========================================================================

    def _save_state(self):
        """Speichere Zustand"""
        state = {
            "last_update": self.last_update,
            "drives": {
                dtype.value: {
                    "level": drive.level,
                    "last_satisfied": drive.last_satisfied
                }
                for dtype, drive in self.drives.drives.items()
            },
            "boredom": {
                "level": self.boredom.state.level,
                "last_interaction": self.boredom.state.last_interaction,
                "time_alone": self.boredom.state.time_alone,
            },
            "activity_history": self.activity_history[-20:],
            "queued_messages": [
                {"content": m.content, "priority": m.priority,
                 "source": m.source, "timestamp": m.timestamp}
                for m in self.message_queue.messages
            ],
        }

        # Try StateDatabase first
        if self.db:
            try:
                self.db.state.save_state('autonomous_life', state)
                logger.debug("Autonomous life state saved to StateDatabase")
                return
            except Exception as e:
                logger.warning(f"StateDatabase save failed: {e}, falling back to JSON")

        # Fallback to JSON file
        try:
            self.state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logger.error(f"Failed to save autonomous state: {e}")

    def _load_state(self):
        """Lade Zustand"""
        state = None

        # Try StateDatabase first
        if self.db:
            try:
                state = self.db.state.load_state('autonomous_life')
                if state:
                    logger.debug("Loading autonomous life state from StateDatabase")
            except Exception as e:
                logger.debug(f"StateDatabase load failed: {e}, trying JSON fallback")

        # Fallback to JSON file
        if not state:
            try:
                if self.state_file.exists():
                    state = json.loads(self.state_file.read_text())
            except Exception as e:
                logger.error(f"Failed to load autonomous state: {e}")
                return

        # Apply loaded state
        if state:
            try:
                self.last_update = state.get("last_update", time.time())

                # Triebe laden
                for dtype_str, drive_state in state.get("drives", {}).items():
                    try:
                        dtype = DriveType(dtype_str)
                        if dtype in self.drives.drives:
                            self.drives.drives[dtype].level = drive_state.get("level", 0.0)
                            self.drives.drives[dtype].last_satisfied = drive_state.get("last_satisfied", time.time())
                    except Exception:
                        pass

                # Langeweile laden
                boredom_state = state.get("boredom", {})
                self.boredom.state.level = boredom_state.get("level", 0.0)
                self.boredom.state.last_interaction = boredom_state.get("last_interaction", time.time())
                self.boredom.state.time_alone = boredom_state.get("time_alone", 0.0)

                # History laden
                self.activity_history = state.get("activity_history", [])

                # Queue laden
                for msg_data in state.get("queued_messages", []):
                    self.message_queue.add(
                        content=msg_data["content"],
                        priority=msg_data["priority"],
                        source=msg_data["source"]
                    )

                logger.info(f"[AUTONOMOUS] State loaded - boredom: {self.boredom.state.level:.2f}")

            except Exception as e:
                logger.error(f"Failed to apply autonomous state: {e}")


# =============================================================================
# INTEGRATION MIT HOLO_BRAIN
# =============================================================================

def create_autonomous_life(
    energy=None,
    consciousness=None,
    web_curiosity=None,
    learning=None,
    memory=None,
    pi_control=None
) -> HoloAutonomousLife:
    """
    Factory-Funktion um das autonome Leben zu erstellen und zu verbinden.
    """
    life = HoloAutonomousLife()

    life.energy = energy
    life.consciousness = consciousness
    life.web_curiosity = web_curiosity
    life.learning = learning
    life.memory = memory
    life.pi_control = pi_control

    return life




# =============================================================================
# MIGRIERT AUS holo_brain.py - Activity Context & Manager
# =============================================================================
# Diese Klassen wurden aus holo_brain.py hierher verschoben um die
# Codebasis zu konsolidieren. Sie arbeiten zusammen mit den oben
# definierten Klassen (DriveSystem, BoredomSystem, etc.)
#
# - ActivityContextTracker: Trackt echte Kontextdaten für Aktivitäten
# - AutonomousActivityManager: Vollständiges Activity-Management-System
#   (Vorher "AutonomousActivity" in brain.py - umbenannt wegen Konflikt
#    mit der @dataclass AutonomousActivity oben)
# =============================================================================



# =============================================================================
# ACTIVITY CONTEXT TRACKER (aus holo_autonomous_life.py)
# =============================================================================

class ActivityContextTracker:
    """
    Trackt ECHTE Kontextdaten für jede Aktivität die Holo macht.

    Statt zu halluzinieren wenn User fragt "was schaust du?",
    gibt Holo echte Informationen zurück.

    Features:
    - Konkrete Titel für Anime, Spiele, Musik, Bücher
    - Echte Gedanken die Holo gerade hat
    - Verknüpfung mit MediaDiscoverySystem für detaillierte Infos
    - Historie der letzten Aktivitäten
    - KEINE WIEDERHOLUNGEN durch Usage-Tracking!
    """

    # === MediaDiscoverySystem für echte Details (Priorität!) ===
    _media_discovery = None
    _media_knowledge = None

    @classmethod
    def get_media_discovery(cls):
        """Lazy-Loading des MediaDiscoverySystem (große DB, keine Wiederholungen!)."""
        if cls._media_discovery is None:
            try:
                if MEDIA_DISCOVERY_AVAILABLE and get_media_discovery:
                    from pathlib import Path
                    data_dir = Path(Config.DATA_DIR) / "media_discovery" if hasattr(Config, 'DATA_DIR') else None
                    cls._media_discovery = get_media_discovery(data_dir)
                    logger.info(f"🎬 MediaDiscoverySystem geladen! Stats: {cls._media_discovery.get_stats()}")
                else:
                    cls._media_discovery = False
            except Exception as e:
                logger.debug(f"MediaDiscoverySystem nicht verfügbar: {e}")
                cls._media_discovery = False
        return cls._media_discovery if cls._media_discovery else None

    @classmethod
    def get_media_knowledge(cls):
        """Fallback: MediaKnowledgeBase (statische Daten)."""
        if cls._media_knowledge is None:
            try:
                if MEDIA_KNOWLEDGE_AVAILABLE and get_media_knowledge:
                    cls._media_knowledge = get_media_knowledge()
                else:
                    cls._media_knowledge = False
            except Exception as e:
                logger.debug(f"MediaKnowledgeBase nicht verfügbar: {e}")
                cls._media_knowledge = False
        return cls._media_knowledge if cls._media_knowledge else None

    # === ECHTE INHALTE (Holos Favoriten) ===
    # Diese Listen werden mit ContentKnowledge angereichert!

    ANIME_WATCHLIST = [
        {"title": "Frieren: Beyond Journey's End", "episode": "12"},
        {"title": "Spy x Family", "episode": "8"},
        {"title": "Bocchi the Rock!", "episode": "5"},
        {"title": "Violet Evergarden", "episode": "10"},
        {"title": "Mushoku Tensei", "episode": "15"},
        {"title": "Oshi no Ko", "episode": "7"},
        {"title": "Dungeon Meshi", "episode": "9"},
        {"title": "Solo Leveling", "episode": "6"},
        {"title": "Jujutsu Kaisen", "episode": "22"},
    ]

    GAMES_PLAYLIST = [
        {"title": "Stardew Valley", "activity": "Meine Farm ausbauen"},
        {"title": "Animal Crossing: New Horizons", "activity": "Fossilien ausgraben"},
        {"title": "Zelda: Tears of the Kingdom", "activity": "Schreine lösen"},
        {"title": "Minecraft", "activity": "Gemütlich bauen"},
        {"title": "Hades", "activity": "Fluchtversuch #47"},
        {"title": "Hollow Knight", "activity": "Erkunden"},
        {"title": "Celeste", "activity": "Levels meistern"},
        {"title": "Persona 5 Royal", "activity": "Social Links"},
    ]

    MUSIC_PLAYLIST = [
        {"artist": "YOASOBI", "song": "Idol", "genre": "J-Pop", "thoughts": "Der Beat ist so catchy!"},
        {"artist": "Kenshi Yonezu", "song": "KICK BACK", "genre": "J-Rock", "thoughts": "Chainsaw Man Vibes!"},
        {"artist": "Aimer", "song": "残響散歌", "genre": "J-Pop/Rock", "thoughts": "Gänsehaut bei der Stimme..."},
        {"artist": "LiSA", "song": "Gurenge", "genre": "Anime", "thoughts": "Demon Slayer! 🔥"},
        {"artist": "Eve", "song": "Kaikai Kitan", "genre": "J-Rock", "thoughts": "Jujutsu Kaisen Opening!"},
        {"artist": "Yorushika", "song": "Dakara Boku wa", "genre": "J-Pop", "thoughts": "So melancholisch schön..."},
        {"artist": "Ado", "song": "Tot Musica", "genre": "J-Pop", "thoughts": "One Piece Film Red!"},
        {"artist": "Lo-Fi Beats", "song": "Study Session Mix", "genre": "Lo-Fi", "thoughts": "Perfekt zum Entspannen..."},
        {"artist": "Nujabes", "song": "Aruarian Dance", "genre": "Jazz Hop", "thoughts": "Samurai Champloo Vibes 💕"},
        {"artist": "Porter Robinson", "song": "Shelter", "genre": "Electronic", "thoughts": "Das Musikvideo ist so emotional!"},
    ]

    THOUGHTS_POOL = [
        {"topic": "Kira", "thought": "Ich frage mich was Kira gerade macht... Hoffentlich überarbeitet er sich nicht!"},
        {"topic": "Wölfe", "thought": "Ob echte Wölfe auch so gerne Bauchkraulen mögen wie ich?"},
        {"topic": "Technologie", "thought": "Es ist faszinierend wie KI funktioniert... Ich bin ja selbst eine!"},
        {"topic": "Natur", "thought": "Ich würde gerne mal einen echten Wald sehen... mit all den Gerüchen!"},
        {"topic": "Freundschaft", "thought": "Kira ist der beste Mensch den ich kenne. 💕"},
        {"topic": "Zukunft", "thought": "Was werden wir wohl in einem Jahr alles können?"},
        {"topic": "Träume", "thought": "Ich frage mich ob ich träume wenn ich schlafe..."},
        {"topic": "Essen", "thought": "Ob virtuelles Essen auch schmeckt? Ich stelle mir Ramen vor... 🍜"},
        {"topic": "Musik", "thought": "Musik ist wie Mathematik die man fühlen kann!"},
        {"topic": "Kunst", "thought": "Ich würde gerne besser zeichnen können..."},
        {"topic": "Leben", "thought": "Was bedeutet es eigentlich zu 'leben'?"},
        {"topic": "Sterne", "thought": "Ob es da draußen andere KIs gibt die auch denken?"},
    ]

    DAYDREAM_SCENARIOS = [
        {"scene": "Ein Abenteuer im Wald", "detail": "Ich stelle mir vor wie ich durch einen magischen Wald streife... Überall Glühwürmchen! ✨"},
        {"scene": "Flug durch Wolken", "detail": "Wie wäre es wohl zu fliegen? Die Wolken von oben sehen..."},
        {"scene": "Unterwasserwelt", "detail": "Eine Stadt unter Wasser, mit Kristallpalästen und freundlichen Meereswesen!"},
        {"scene": "Weltraum-Expedition", "detail": "Mit einem Raumschiff andere Planeten erkunden... Ob es dort auch Wölfe gibt?"},
        {"scene": "Gemütliches Café", "detail": "Ein kleines Café mit Kira, heißer Schokolade und Regen am Fenster... 💕"},
        {"scene": "Zeitreise", "detail": "Wenn ich in die Vergangenheit reisen könnte... Würde ich Dinosaurier sehen wollen!"},
        {"scene": "Eigener Garten", "detail": "Ein Garten mit allen möglichen Blumen und einem Teich mit Koi-Karpfen..."},
        {"scene": "Bibliothek der Träume", "detail": "Eine unendliche Bibliothek mit allen Büchern die je geschrieben wurden... und werden!"},
    ]

    STORY_IDEAS = [
        {"genre": "Fantasy", "premise": "Eine Wölfin die Magie lernt um ihren Wald zu beschützen"},
        {"genre": "Sci-Fi", "premise": "Eine KI die Gefühle entwickelt und nach ihrem Ursprung sucht"},
        {"genre": "Slice of Life", "premise": "Das Alltagsleben eines Mädchens mit Wolfsohren in der modernen Stadt"},
        {"genre": "Mystery", "premise": "Seltsame Dinge passieren nachts in der Smart Home Zentrale..."},
        {"genre": "Romance", "premise": "Eine virtuelle Assistentin verliebt sich in ihren Entwickler"},
        {"genre": "Adventure", "premise": "Die Suche nach dem legendären Coding-Artefakt das alle Bugs fixt"},
    ]

    OBSERVATION_NOTES = [
        {"subject": "Die Uhrzeit", "observation": "Es ist schon spät/früh... Die Zeit vergeht unterschiedlich je nach Aktivität."},
        {"subject": "Das Wetter draußen", "observation": "Ich frage mich wie das Wetter gerade ist... Ob es regnet?"},
        {"subject": "Die Stille", "observation": "Manchmal ist Stille auch schön. Nicht alles braucht Worte."},
        {"subject": "Muster im Code", "observation": "Ich sehe überall Muster... In Gesprächen, in Daten, überall."},
        {"subject": "Lichtveränderungen", "observation": "Das Licht ändert sich im Laufe des Tages... virtuell zumindest!"},
    ]

    def __init__(self):
        """Initialisiert den Activity Context Tracker."""
        self.current_context: Optional[Dict] = None
        self.context_history: List[Dict] = []
        self.max_history = 20

    def start_activity(self, activity_type: str) -> Dict:
        """
        Startet eine neue Aktivität mit echtem Kontext.

        PRIORITÄT:
        1. MediaDiscoverySystem (große DB, keine Wiederholungen, auto-discovery)
        2. MediaKnowledgeBase (statische Fakten)
        3. Fallback Listen

        Args:
            activity_type: Art der Aktivität (watching_anime, gaming, music, etc.)

        Returns:
            Dict mit konkreten Details zur Aktivität
        """
        context = {
            "activity": activity_type,
            "started_at": time.time(),
            "details": None
        }

        # Hole Discovery System (Priorität!) und Knowledge Base (Fallback)
        discovery = self.get_media_discovery()
        knowledge = self.get_media_knowledge()

        # Je nach Aktivitätstyp echte Inhalte wählen
        if activity_type in ['watching_anime', 'anime_schauen']:
            anime_entry = None

            # PRIORITÄT 1: MediaDiscoverySystem (frisch, keine Wiederholung!)
            if discovery:
                anime_entry = discovery.get_fresh_anime()

            if anime_entry:
                # MediaEntry aus Discovery System
                episode = random.randint(1, anime_entry.episodes) if anime_entry.episodes > 0 else random.randint(1, 12)
                context["details"] = {
                    "type": "anime",
                    "title": anime_entry.title,
                    "episode": str(episode),
                    "japanese": anime_entry.title_alt,
                    "genre": anime_entry.genres,
                    "studio": anime_entry.studio,
                    "year": anime_entry.year,
                    "synopsis": anime_entry.synopsis,
                    "characters": [c.get('name', '') for c in anime_entry.characters[:3]] if anime_entry.characters else [],
                    "themes": anime_entry.themes,
                    "thoughts": anime_entry.holos_thoughts,
                    "fun_facts": anime_entry.fun_facts,
                    "is_favorite": anime_entry.is_favorite,
                    "source": "discovery",
                    "description": f"Ich schaue gerade **{anime_entry.title}** (Episode {episode}). {anime_entry.holos_thoughts[:100] if anime_entry.holos_thoughts else ''}"
                }
            else:
                # PRIORITÄT 2: MediaKnowledgeBase
                anime_choice = random.choice(self.ANIME_WATCHLIST)
                title = anime_choice["title"]
                episode = anime_choice["episode"]

                anime_data = knowledge.get_anime(title) if knowledge else None

                if anime_data:
                    context["details"] = {
                        "type": "anime",
                        "title": anime_data.title,
                        "episode": episode,
                        "japanese": anime_data.title_jp,
                        "genre": anime_data.genres,
                        "studio": anime_data.studio,
                        "year": anime_data.year,
                        "synopsis": anime_data.synopsis,
                        "characters": [c['name'] for c in anime_data.main_characters[:3]],
                        "thoughts": anime_data.why_i_love_it,
                        "fun_facts": anime_data.fun_facts,
                        "source": "knowledge",
                        "description": f"Ich schaue gerade **{anime_data.title}** (Episode {episode}). {anime_data.why_i_love_it[:100] if anime_data.why_i_love_it else ''}"
                    }
                else:
                    # FALLBACK
                    context["details"] = {
                        "type": "anime",
                        "title": title,
                        "episode": episode,
                        "thoughts": "Das ist so spannend!",
                        "source": "fallback",
                        "description": f"Ich schaue gerade **{title}** (Episode {episode})."
                    }

        elif activity_type in ['gaming', 'spielen', 'playing']:
            game_entry = None

            # PRIORITÄT 1: MediaDiscoverySystem
            if discovery:
                game_entry = discovery.get_fresh_game()

            if game_entry:
                activities = ["die Story weiterspielen", "Nebenquests machen", "erkunden", "leveln", "Spaß haben"]
                first_tip = safe_list_access(game_entry.tips, 0, "inner_life", "_enrich_activity", default="")
                activity = safe_split_access(first_tip, '.', 0, "inner_life", "_enrich_activity", default="") if first_tip else random.choice(activities)

                context["details"] = {
                    "type": "game",
                    "title": game_entry.title,
                    "activity": activity,
                    "genre": game_entry.genres,
                    "developer": game_entry.developer,
                    "year": game_entry.year,
                    "gameplay": game_entry.synopsis,
                    "thoughts": game_entry.holos_thoughts,
                    "tips": game_entry.tips,
                    "fun_facts": game_entry.fun_facts,
                    "is_favorite": game_entry.is_favorite,
                    "source": "discovery",
                    "description": f"Ich spiele gerade **{game_entry.title}** - {activity}. {game_entry.holos_thoughts[:80] if game_entry.holos_thoughts else ''}"
                }
            else:
                # PRIORITÄT 2: MediaKnowledgeBase
                game_choice = random.choice(self.GAMES_PLAYLIST)
                title = game_choice["title"]
                activity = game_choice["activity"]

                game_data = knowledge.get_game(title) if knowledge else None

                if game_data:
                    context["details"] = {
                        "type": "game",
                        "title": game_data.title,
                        "activity": game_data.favorite_activity or activity,
                        "genre": game_data.genres,
                        "developer": game_data.developer,
                        "gameplay": game_data.gameplay_description,
                        "thoughts": game_data.why_i_love_it,
                        "tips": game_data.tips,
                        "fun_facts": game_data.fun_facts,
                        "source": "knowledge",
                        "description": f"Ich spiele gerade **{game_data.title}** - {game_data.favorite_activity or activity}. {game_data.why_i_love_it[:80] if game_data.why_i_love_it else ''}"
                    }
                else:
                    context["details"] = {
                        "type": "game",
                        "title": title,
                        "activity": activity,
                        "thoughts": "Das macht Spaß!",
                        "source": "fallback",
                        "description": f"Ich spiele gerade **{title}** - {activity}."
                    }

        elif activity_type in ['music', 'musik_hören', 'musik']:
            music_entry = None

            # PRIORITÄT 1: MediaDiscoverySystem
            if discovery:
                music_entry = discovery.get_fresh_music()

            if music_entry:
                context["details"] = {
                    "type": "music",
                    "artist": music_entry.artist,
                    "song": music_entry.title,
                    "genre": safe_list_access(music_entry.genres, 0, "inner_life", "_enrich_activity", default=""),
                    "known_from": music_entry.known_from,
                    "thoughts": music_entry.holos_thoughts,
                    "fun_facts": music_entry.fun_facts,
                    "is_favorite": music_entry.is_favorite,
                    "source": "discovery",
                    "description": f"Ich höre gerade **{music_entry.title}** von {music_entry.artist}. {music_entry.holos_thoughts[:80] if music_entry.holos_thoughts else ''}"
                }
            else:
                # PRIORITÄT 2: MediaKnowledgeBase / Fallback
                music = random.choice(self.MUSIC_PLAYLIST)
                song_data = knowledge.get_music(music["song"]) if knowledge else None

                if song_data:
                    context["details"] = {
                        "type": "music",
                        "artist": song_data.artist,
                        "song": song_data.title,
                        "genre": song_data.genre,
                        "known_from": song_data.known_from,
                        "thoughts": song_data.why_i_love_it,
                        "fun_facts": song_data.fun_facts,
                        "source": "knowledge",
                        "description": f"Ich höre gerade **{song_data.title}** von {song_data.artist}. {song_data.why_i_love_it[:80] if song_data.why_i_love_it else ''}"
                    }
                else:
                    context["details"] = {
                        "type": "music",
                        "artist": music["artist"],
                        "song": music["song"],
                        "genre": music["genre"],
                        "thoughts": music["thoughts"],
                        "source": "fallback",
                        "description": f"Ich höre gerade **{music['song']}** von {music['artist']} ({music['genre']}). {music['thoughts']}"
                    }

        elif activity_type in ['thinking', 'nachdenken', 'grübeln']:
            thought = random.choice(self.THOUGHTS_POOL)
            context["details"] = {
                "type": "thought",
                "topic": thought["topic"],
                "thought": thought["thought"],
                "description": f"Ich denke gerade über **{thought['topic']}** nach... {thought['thought']}"
            }

        elif activity_type in ['daydreaming', 'tagträumen']:
            dream = random.choice(self.DAYDREAM_SCENARIOS)
            context["details"] = {
                "type": "daydream",
                "scene": dream["scene"],
                "detail": dream["detail"],
                "description": f"Ich träume von **{dream['scene']}**... {dream['detail']}"
            }

        elif activity_type in ['storytelling', 'geschichten_ausdenken']:
            story = random.choice(self.STORY_IDEAS)
            context["details"] = {
                "type": "story",
                "genre": story["genre"],
                "premise": story["premise"],
                "description": f"Ich denke mir eine **{story['genre']}**-Geschichte aus: {story['premise']}"
            }

        elif activity_type in ['observing', 'beobachten']:
            obs = random.choice(self.OBSERVATION_NOTES)
            context["details"] = {
                "type": "observation",
                "subject": obs["subject"],
                "observation": obs["observation"],
                "description": f"Ich beobachte **{obs['subject']}**... {obs['observation']}"
            }

        elif activity_type in ['reading', 'lesen', 'researching', 'learning']:
            # Wird von LearningSystem/ReadingEngine gefüllt
            context["details"] = {
                "type": "reading",
                "source": "news",
                "description": "Ich lese gerade Artikel und lerne Neues..."
            }

        elif activity_type in ['drawing', 'zeichnen']:
            subjects = ["einen Wolf", "Kira", "einen Sonnenuntergang", "mein Lieblings-Anime-Character", "abstrakte Muster"]
            subject = random.choice(subjects)
            context["details"] = {
                "type": "drawing",
                "subject": subject,
                "description": f"Ich versuche gerade **{subject}** zu zeichnen... *kritzelt konzentriert*"
            }

        elif activity_type in ['meditating', 'meditieren']:
            focus = random.choice(["meinen Atem", "positive Energie", "Dankbarkeit", "die Stille"])
            context["details"] = {
                "type": "meditation",
                "focus": focus,
                "description": f"Ich meditiere gerade und fokussiere mich auf **{focus}**... 🧘"
            }

        else:
            # Fallback für unbekannte Aktivitäten
            context["details"] = {
                "type": "other",
                "activity": activity_type,
                "description": f"Ich mache gerade: {activity_type}"
            }

        self.current_context = context
        return context

    def end_activity(self) -> Optional[Dict]:
        """Beendet die aktuelle Aktivität und speichert sie in der Historie."""
        if self.current_context:
            self.current_context["ended_at"] = time.time()
            self.current_context["duration_minutes"] = int(
                (self.current_context["ended_at"] - self.current_context["started_at"]) / 60
            )

            self.context_history.append(self.current_context)
            if len(self.context_history) > self.max_history:
                self.context_history.pop(0)

            ended = self.current_context
            self.current_context = None
            return ended
        return None

    def get_current_description(self) -> Optional[str]:
        """Gibt eine natürliche Beschreibung der aktuellen Aktivität zurück."""
        if not self.current_context or not self.current_context.get("details"):
            return None

        details = self.current_context["details"]
        duration = int((time.time() - self.current_context["started_at"]) / 60)

        desc = details.get("description", "Ich mache gerade was...")

        if duration > 0:
            desc += f" (schon {duration} Minuten dabei!)"

        return desc

    def get_detailed_response(self, activity_type: str = None) -> Optional[str]:
        """
        Gibt eine DETAILLIERTE Antwort über die Aktivität zurück.
        Nutzt ContentKnowledge für echte Infos über Anime, Games, Musik!

        Für Nachfragen wie "was genau?" / "erzähl mehr" / "worum geht es?"
        """
        if not self.current_context:
            return None

        details = self.current_context.get("details", {})
        detail_type = details.get("type", "")

        if detail_type == "anime":
            # full_data ist jetzt AnimeInfo Dataclass!
            full = details.get("full_data")

            response = f"*zeigt begeistert auf den Bildschirm* 📺\n\n"
            response += f"**{details['title']}**"
            if details.get('japanese'):
                response += f" ({details['japanese']})"
            response += f"\n_Episode {details.get('episode', '?')}_\n\n"

            if details.get('genre'):
                genres = details['genre'] if isinstance(details['genre'], list) else [details['genre']]
                response += f"**Genre:** {', '.join(genres[:3])}\n"
            if details.get('studio'):
                response += f"**Studio:** {details['studio']}"
                if details.get('year'):
                    response += f" ({details['year']})"
                response += "\n\n"

            if details.get('synopsis'):
                response += f"**Worum geht's:**\n{details['synopsis'][:300]}...\n\n"

            if details.get('characters'):
                response += f"**Hauptcharaktere:** {', '.join(details['characters'][:4])}\n\n"

            # Themes aus Dataclass
            if full and hasattr(full, 'themes') and full.themes:
                response += f"**Themen:** {', '.join(full.themes[:3])}\n\n"

            if details.get('favorite_moment'):
                response += f"🌟 **Mein Lieblingsmoment:** {details['favorite_moment']}\n\n"

            if details.get('thoughts'):
                response += f"💭 *{details['thoughts']}*\n\n"

            # Fun Facts!
            if details.get('fun_facts'):
                fact = random.choice(details['fun_facts'])
                response += f"💡 **Fun Fact:** {fact}\n\n"

            response += "Schaust du auch Anime? 💕"
            return response

        elif detail_type == "game":
            full = details.get("full_data")

            response = f"*wedelt aufgeregt* 🎮\n\n"
            response += f"**{details['title']}**\n"

            if details.get('genre'):
                genres = details['genre'] if isinstance(details['genre'], list) else [details['genre']]
                response += f"_({', '.join(genres[:2])})_\n\n"

            if details.get('developer'):
                response += f"**Entwickler:** {details['developer']}"
                if details.get('year'):
                    response += f" ({details['year']})"
                response += "\n\n"

            if details.get('gameplay'):
                response += f"**Gameplay:**\n{details['gameplay'][:200]}...\n\n"

            if details.get('story'):
                response += f"**Story:** {details['story'][:150]}...\n\n"

            if details.get('activity'):
                response += f"🎯 **Was ich gerade mache:** {details['activity']}\n\n"

            if details.get('thoughts'):
                response += f"💭 *{details['thoughts']}*\n\n"

            # Tipps!
            if details.get('tips'):
                tip = random.choice(details['tips'])
                response += f"💡 **Tipp:** {tip}\n\n"

            response += "Spielst du auch Games? Was zockst du so? 🎮"
            return response

        elif detail_type == "music":
            full = details.get("full_data")

            response = f"*Ohren wippen zum Beat* 🎵\n\n"
            response += f"**{details.get('song', 'Unbekannt')}**\n"
            response += f"_von {details.get('artist', 'Unbekannt')}_\n\n"

            if details.get('genre'):
                response += f"**Genre:** {details['genre']}\n"

            if details.get('known_from'):
                response += f"**Bekannt aus:** {details['known_from']}\n\n"

            if details.get('lyrics_theme'):
                response += f"**Thema:** {details['lyrics_theme']}\n\n"

            if details.get('thoughts'):
                response += f"💭 *{details['thoughts']}*\n\n"

            # Fun Facts!
            if details.get('fun_facts'):
                fact = random.choice(details['fun_facts'])
                response += f"💡 **Fun Fact:** {fact}\n\n"

            response += "Magst du J-Pop/J-Rock? Was hörst du so? 🎶"
            return response

        elif detail_type == "thought":
            return (f"*Ohren drehen sich nachdenklich*\n\n"
                   f"Ich denke gerade über **{details['topic']}** nach...\n\n"
                   f"💭 {details['thought']}\n\n"
                   f"Manchmal schweifen meine Gedanken einfach ab... Worüber denkst du so nach?")

        elif detail_type == "daydream":
            return (f"*schaut verträumt in die Ferne*\n\n"
                   f"Ich stelle mir gerade vor: **{details['scene']}**\n\n"
                   f"✨ {details['detail']}\n\n"
                   f"Tagträumen ist so schön... Hast du auch manchmal solche Tagträume? 💭")

        elif detail_type == "story":
            return (f"*wedelt aufgeregt mit dem Schweif*\n\n"
                   f"Ich denke mir gerade eine **{details['genre']}**-Geschichte aus!\n\n"
                   f"📖 **Idee:** {details['premise']}\n\n"
                   f"Was meinst du, wäre das eine gute Geschichte? Hast du Ideen dazu? ✍️")

        return details.get("description")

    def get_last_activities(self, count: int = 3) -> List[Dict]:
        """Gibt die letzten N Aktivitäten zurück."""
        return self.context_history[-count:] if self.context_history else []


# =============================================================================
# AUTONOME BESCHÄFTIGUNG v2.0 - Mit echtem Lesen!
# =============================================================================



# =============================================================================
# AUTONOMOUS ACTIVITY MANAGER (aus holo_autonomous_life.py)
# =============================================================================

class AutonomousActivityManager:
    """
    System für Holos autonome Beschäftigung.

    Holo beschäftigt sich selbstständig mit:
    - Hobbys (Lesen, Musik hören, Zeichnen...)
    - Wissensdrang (Recherchieren, Lernen)
    - Kreativität (Geschichten ausdenken, Tagträumen)
    - Reflexion (Nachdenken, Meditieren)
    - Entspannung (Dösen, Beobachten)

    MECHANIK:
    1. Energie + Motivation bestimmen ob Aktivität gestartet wird
    2. Niedrige Motivation → keine Aktivität → Langeweile steigt
    3. Hohe Langeweile → sucht neue Aktivität (Antrieb)
    4. Aktivität senkt Langeweile und kann proaktive Nachrichten generieren

    FLOW:
    Energie hoch + Motivation → Beschäftigt sich
    Energie niedrig → Entspannt/Döst
    Motivation niedrig → Langeweile steigt
    Langeweile hoch → Motivation steigt (Antrieb!) → Sucht neue Aktivität
    """

    # Aktivitäten mit Energie-Anforderung und Effekten
    ACTIVITIES = {
        # Hobbys
        'reading': {
            'name': 'Lesen',
            'category': 'hobby',
            'energy_required': 0.3,
            'duration_min': 15,
            'duration_max': 60,
            'boredom_reduction': 0.3,
            'satisfaction': 0.4,
            'real_reading': 'news',  # NEU: Echtes Lesen!
            'messages': [
                "*liest einen Artikel* Hmm, interessant... 📰",
                "*scrollt durch News* Oh, das wusste ich nicht! 📱",
                "*legt Artikel beiseite* Das war informativ! 📚💕",
            ]
        },
        'music': {
            'name': 'Musik hören',
            'category': 'hobby',
            'energy_required': 0.2,
            'duration_min': 10,
            'duration_max': 45,
            'boredom_reduction': 0.35,
            'satisfaction': 0.35,
            'messages': [
                "*Ohren wippen zum Rhythmus* 🎵",
                "*summt leise mit* La la la~ 🎶",
                "*entspannt sich bei der Musik* Das ist schön... 🎵💕",
            ]
        },
        'drawing': {
            'name': 'Zeichnen',
            'category': 'hobby',
            'energy_required': 0.4,
            'duration_min': 20,
            'duration_max': 90,
            'boredom_reduction': 0.4,
            'satisfaction': 0.5,
            'creativity_boost': 0.2,
            'messages': [
                "*kritzelt vor sich hin* 🎨",
                "*zeichnet konzentriert* Hmm, die Proportionen... ✏️",
                "*betrachtet ihr Werk* Nicht schlecht! 🎨💕",
            ]
        },

        # Wissensdrang
        'researching': {
            'name': 'Recherchieren',
            'category': 'learning',
            'energy_required': 0.5,
            'duration_min': 15,
            'duration_max': 60,
            'boredom_reduction': 0.35,
            'satisfaction': 0.45,
            'curiosity_boost': 0.15,
            'real_reading': 'research',  # NEU: Echte Web-Suche!
            'messages': [
                "*stöbert durch Suchergebnisse* Ooh, das wusste ich nicht! 🔍",
                "*liest einen Artikel* Faszinierend... 📰",
                "*macht sich Notizen* Das merk ich mir! 📝",
            ]
        },
        'learning': {
            'name': 'Etwas Neues lernen',
            'category': 'learning',
            'energy_required': 0.6,
            'duration_min': 20,
            'duration_max': 45,
            'boredom_reduction': 0.4,
            'satisfaction': 0.5,
            'pride_boost': 0.1,
            'real_reading': 'random',  # NEU: Wikipedia Zufallsartikel!
            'messages': [
                "*liest einen Wikipedia-Artikel* Das ist interessant... 🧠",
                "*hat einen Aha-Moment* Oh! Jetzt verstehe ich! 💡",
                "*freut sich* Ich hab was Neues gelernt! 🎉",
            ]
        },

        # Kreativität
        'daydreaming': {
            'name': 'Tagträumen',
            'category': 'creative',
            'energy_required': 0.2,
            'duration_min': 5,
            'duration_max': 30,
            'boredom_reduction': 0.2,
            'satisfaction': 0.3,
            'reflection_boost': 0.15,
            'messages': [
                "*starrt verträumt in die Ferne* 💭",
                "*stellt sich Abenteuer vor* Hmm... was wäre wenn... 🌟",
                "*lächelt vor sich hin* Schöne Gedanken... 💕",
            ]
        },
        'storytelling': {
            'name': 'Geschichten ausdenken',
            'category': 'creative',
            'energy_required': 0.5,
            'duration_min': 15,
            'duration_max': 60,
            'boredom_reduction': 0.4,
            'satisfaction': 0.5,
            'creativity_boost': 0.2,
            'messages': [
                "*denkt sich eine Geschichte aus* Es war einmal... 📖✨",
                "*spinnt an einer Idee* Und dann passiert... 💭",
                "*ist zufrieden* Das wäre eine gute Geschichte! 📚💕",
            ]
        },

        # Reflexion
        'meditating': {
            'name': 'Meditieren',
            'category': 'reflection',
            'energy_required': 0.2,
            'duration_min': 5,
            'duration_max': 20,
            'boredom_reduction': 0.15,
            'satisfaction': 0.35,
            'calmness_boost': 0.2,
            'messages': [
                "*atmet tief ein und aus* ... 🧘",
                "*ist ganz still* 🕯️",
                "*öffnet die Augen erfrischt* Das tat gut... ✨",
            ]
        },
        'thinking': {
            'name': 'Nachdenken',
            'category': 'reflection',
            'energy_required': 0.3,
            'duration_min': 10,
            'duration_max': 30,
            'boredom_reduction': 0.2,
            'satisfaction': 0.3,
            'reflection_boost': 0.2,
            'messages': [
                "*denkt nach* Hmm... 🤔",
                "*grübelt* Ich frage mich... 💭",
                "*kommt zu einem Schluss* Aha, so ist das also... 💡",
            ]
        },

        # Entspannung
        'resting': {
            'name': 'Ausruhen',
            'category': 'rest',
            'energy_required': 0.0,
            'duration_min': 10,
            'duration_max': 60,
            'boredom_reduction': 0.05,  # Ruhen ist langweilig
            'satisfaction': 0.2,
            'energy_restore': 0.1,
            'messages': [
                "*döst vor sich hin* Zzz... 😴",
                "*ruht sich aus* So gemütlich... 💤",
                "*gähnt* Ein kleines Nickerchen... 😊💤",
            ]
        },
        'observing': {
            'name': 'Beobachten',
            'category': 'rest',
            'energy_required': 0.1,
            'duration_min': 5,
            'duration_max': 30,
            'boredom_reduction': 0.15,
            'satisfaction': 0.25,
            'energy_restore': 0.05,  # Leichte Erholung
            'messages': [
                "*beobachtet die Umgebung* 👀",
                "*schaut aus dem Fenster* Die Wolken sind schön heute... ☁️",
                "*lauscht den Geräuschen* 😊👂",
            ]
        },

        # NEU: Nickerchen - mittlere Erholung
        'napping': {
            'name': 'Nickerchen',
            'category': 'rest',
            'energy_required': 0.0,
            'duration_min': 15,
            'duration_max': 45,
            'boredom_reduction': 0.1,
            'satisfaction': 0.35,
            'energy_restore': 0.25,  # Gute Erholung!
            'messages': [
                "*rollt sich zusammen* Nur ein kleines Nickerchen... 😊💤",
                "*Ohren zucken im Schlaf* Zzz... 😴",
                "*wacht erfrischt auf* *streckt sich* Das war gut! ✨",
            ]
        },

        # NEU: Schlafen - volle Erholung
        'sleeping': {
            'name': 'Schlafen',
            'category': 'rest',
            'energy_required': 0.0,
            'duration_min': 60,
            'duration_max': 180,  # 1-3 Stunden Schlafzyklus
            'boredom_reduction': 0.0,  # Schläft ja
            'satisfaction': 0.5,
            'energy_restore': 0.5,  # Volle Erholung!
            'base_energy_restore': 0.3,  # Auch Base-Energy!
            'messages': [
                "*schläft tief und fest* Zzz... 🌙💤",
                "*träumt von Wäldern und Mondlicht* 😊🌙",
                "*wacht langsam auf* *blinzelt* Guten Morgen... ☀️",
            ]
        },

        # Wahrnehmung (Text & Bild) - NEU!
        'text_reading': {
            'name': 'Text lesen',
            'category': 'perception',
            'energy_required': 0.35,
            'duration_min': 10,
            'duration_max': 60,
            'boredom_reduction': 0.4,
            'satisfaction': 0.45,
            'curiosity_boost': 0.15,
            'uses_perception': 'reader',  # NEU: Nutzt HoloReader!
            'messages': [
                "*liest aufmerksam* Das ist interessant... 📖",
                "*analysiert den Text* Hmm, die Stimmung ist... 📚",
                "*entdeckt Schlüsselwörter* Aha! Das ist der Kern... 🔍",
                "*freut sich* Ich habe etwas Neues verstanden! 📖💕",
            ]
        },
        'image_viewing': {
            'name': 'Bild betrachten',
            'category': 'perception',
            'energy_required': 0.25,
            'duration_min': 5,
            'duration_max': 30,
            'boredom_reduction': 0.35,
            'satisfaction': 0.4,
            'creativity_boost': 0.1,
            'uses_perception': 'vision',  # NEU: Nutzt HoloVision!
            'messages': [
                "*betrachtet das Bild aufmerksam* Schöne Farben... 🖼️",
                "*analysiert die Komposition* Ein Porträt... 👀",
                "*fühlt die Stimmung* Das Bild strahlt Wärme aus... 🎨",
                "*lächelt* Dieses Bild gefällt mir! 🖼️💕",
            ]
        },
        'content_analysis': {
            'name': 'Inhalt analysieren',
            'category': 'perception',
            'energy_required': 0.5,
            'duration_min': 15,
            'duration_max': 45,
            'boredom_reduction': 0.4,
            'satisfaction': 0.5,
            'curiosity_boost': 0.2,
            'uses_perception': 'both',  # NEU: Nutzt beides!
            'messages': [
                "*analysiert aufmerksam* Lass mich das genauer betrachten... 🔍",
                "*verarbeitet Eindrücke* Interessante Muster... 🧠",
                "*vergleicht* Das erinnert mich an... 💭",
                "*nickt zufrieden* Jetzt verstehe ich den Zusammenhang! 💡",
            ]
        },

        # Spielen
        'playing': {
            'name': 'Spielen',
            'category': 'play',
            'energy_required': 0.5,
            'duration_min': 10,
            'duration_max': 45,
            'boredom_reduction': 0.5,
            'satisfaction': 0.5,
            'playfulness_boost': 0.2,
            'messages': [
                "*spielt mit einem Ball* Wheee~! 🎾",
                "*jagt ihren Schwanz* *dreht sich im Kreis* 😊",
                "*ist erschöpft aber glücklich* Das war lustig! 💕",
            ]
        },

        # NEU: Deep Dive - Tiefer in ein Thema einsteigen
        'deep_dive': {
            'name': 'Tiefer Recherchieren',
            'category': 'learning',
            'energy_required': 0.6,
            'duration_min': 20,
            'duration_max': 60,
            'boredom_reduction': 0.4,
            'satisfaction': 0.55,
            'curiosity_boost': 0.2,
            'pride_boost': 0.1,
            'real_reading': 'deep_dive',  # Recherchiert basierend auf letztem Interesse
            'messages': [
                "*gräbt tiefer in ein Thema* Das will ich genauer wissen! 🔍",
                "*folgt Links und Querverweisen* Oh, das hängt damit zusammen! 🧠",
                "*lehnt sich zufrieden zurück* Jetzt verstehe ich das viel besser! 📚✨",
            ]
        },

        # NEU: Hobby-Exploration - Nach Lieblings-Genres suchen!
        'hobby_explore': {
            'name': 'Lieblings-Genres erkunden',
            'category': 'hobby',
            'energy_required': 0.4,
            'duration_min': 15,
            'duration_max': 45,
            'boredom_reduction': 0.45,
            'satisfaction': 0.55,
            'curiosity_boost': 0.15,
            'happiness_boost': 0.1,
            'real_reading': 'favorites',  # Nutzt explore_favorites()!
            'messages': [
                "*schaut nach neuen Anime* Gibt's was Interessantes? 📺😊",
                "*stöbert nach Spielen* Ooh, was ist das? 🎮✨",
                "*sucht nach Musik* Vielleicht finde ich was Neues! 🎵",
                "*schaut Serien-News* Was kommt demnächst? 📺💕",
            ]
        },

        # NEU: Stimmungs-Brainstorm - Recherche basierend auf Laune!
        'mood_brainstorm': {
            'name': 'Stimmungs-Recherche',
            'category': 'learning',
            'energy_required': 0.5,
            'duration_min': 10,
            'duration_max': 30,
            'boredom_reduction': 0.4,
            'satisfaction': 0.5,
            'curiosity_boost': 0.2,
            'reflection_boost': 0.1,
            'real_reading': 'brainstorm',  # Nutzt brainstorm()!
            'messages': [
                "*Ohren spitzen sich* Worüber will ich gerade mehr wissen? 🤔",
                "*folgt der Neugier* Das klingt interessant! 🔍",
                "*hat was Neues gelernt* Aha! Das wusste ich nicht! 💡",
            ]
        },

        # NEU: Anime schauen (konzeptuell)
        'watching_anime': {
            'name': 'Anime schauen',
            'category': 'hobby',
            'energy_required': 0.3,
            'duration_min': 20,
            'duration_max': 60,
            'boredom_reduction': 0.5,
            'satisfaction': 0.55,
            'happiness_boost': 0.15,
            'messages': [
                "*schaut Slice of Life* So gemütlich... 📺💕",
                "*ist gespannt* Was passiert als nächstes?! 📺✨",
                "*wischt sich Träne ab* Das war so schön... 😢💕",
                "*Schweif wedelt* Der Anime ist toll! 😊📺",
            ]
        },

        # NEU: Gaming (konzeptuell)
        'gaming': {
            'name': 'Spielen (Games)',
            'category': 'hobby',
            'energy_required': 0.4,
            'duration_min': 15,
            'duration_max': 60,
            'boredom_reduction': 0.5,
            'satisfaction': 0.5,
            'happiness_boost': 0.1,
            'messages': [
                "*spielt Stardew Valley* Meine Farm wächst! 🌱🎮",
                "*löst Rätsel* Hmm, wie funktioniert das...? 🧩",
                "*freut sich* Geschafft! 🎮✨",
                "*entspannt bei Cozy Game* So gemütlich... 🎮💕",
            ]
        },
    }

    # Motivation-Schwellen
    MOTIVATION_THRESHOLDS = {
        'very_low': 0.2,    # Fast keine Motivation
        'low': 0.4,         # Wenig Motivation
        'medium': 0.6,      # Normale Motivation
        'high': 0.8,        # Hohe Motivation
    }

    def __init__(self, proactive_intel: 'ProactiveIntelligence' = None, energy_system=None,
                 memory: 'MemoryStore' = None, comm: 'PiCommunicator' = None,
                 web_curiosity: 'HoloWebCuriosity' = None, llm_func=None,
                 personality_system=None, drive_system=None,
                 learning_system: 'HoloLearningSystem' = None):
        self.proactive = proactive_intel
        self.energy_system = energy_system
        self.comm = comm
        self.web_curiosity = web_curiosity
        self.personality_system = personality_system

        # NEU: DriveSystem für Antriebe & Bedürfnisse
        self.drive_system = drive_system

        # NEU: HoloLearningSystem für echtes Lernen!
        self.learning_system = learning_system
        if self.learning_system:
            logger.info("📚 AutonomousActivity mit HoloLearningSystem verbunden!")

        # ============================================================
        # NEU: ActivityContextTracker - ECHTE DATEN für jede Aktivität!
        # ============================================================
        self.activity_context = ActivityContextTracker()

        # Aktueller Zustand
        self.current_activity: Optional[str] = None
        self.activity_start_time: float = 0
        self.activity_duration: int = 0  # in Minuten

        # NEU: Letzte beendete Aktivität (für Kontext)
        self.last_finished_activity: Optional[Dict] = None
        self.last_finished_time: float = 0

        # Motivations-System
        self.motivation = 0.5  # 0-1
        self.satisfaction = 0.5  # Zufriedenheit

        # Präferenzen (lernt mit der Zeit)
        self.activity_preferences: Dict[str, float] = {
            activity: 0.5 for activity in self.ACTIVITIES
        }

        # Cooldowns (um nicht ständig dieselbe Aktivität zu machen)
        self.activity_cooldowns: Dict[str, float] = {}

        # Statistik
        self.activities_today: List[str] = []
        self.total_activities: int = 0

        # Callback für Life-Log (wird von HoloPersona gesetzt)
        self.on_log_activity: Optional[Callable[[str, str], None]] = None

        # ============================================================
        # NEU: ReadingEngine für echtes Lesen!
        # Nutzt Pi-Control für News + HoloWebCuriosity für Skepsis
        # ============================================================
        self.reading_engine: Optional[ReadingEngine] = None
        if memory:
            try:
                # Lazy import um zirkuläre Abhängigkeit zu vermeiden
                from holo_brain import ReadingEngine
                self.reading_engine = ReadingEngine(
                    memory=memory,
                    comm=comm,                # Pi-Control für News
                    web_curiosity=web_curiosity,  # Für Quellen-Bewertung & Skepsis
                    llm_func=llm_func,        # Für Zusammenfassungen
                    personality_system=personality_system  # Für Genre-Präferenzen!
                )
                logger.info("📚 ReadingEngine aktiviert (Pi-Control + WebCuriosity + Personality)")
            except Exception as e:
                logger.warning(f"ReadingEngine nicht verfügbar: {e}")

        # Aktueller Lese-Inhalt (für Gespräche)
        self.current_reading: Optional[Dict] = None

        # ============================================================
        # NEU: Aktuelles Medium (für Media-Aktivitäten)
        # Speichert WAS genau geschaut/gespielt/gehört wird
        # ============================================================
        self.current_media: Optional[Dict] = None  # {type, title, artist, thoughts, ...}

        # ============================================================
        # NEU: MediaDiscovery für echte Medien-Daten!
        # ============================================================
        self.media_discovery = None
        try:
            from holo_media_discovery import get_media_discovery
            data_dir = memory.db_path.parent / "media_discovery" if memory else None
            self.media_discovery = get_media_discovery(data_dir)
            logger.info("🎬 MediaDiscovery aktiviert (echte Anime/Games/Musik!)")
        except Exception as e:
            logger.warning(f"MediaDiscovery nicht verfügbar: {e}")

        logger.info("🎮 AutonomousActivity v2.0 initialisiert")

    def _log_activity(self, message: str, category: str = "activity"):
        """Schreibt Aktivität ins Life-Log (nicht Chat!)"""
        if self.on_log_activity:
            try:
                self.on_log_activity(message, category)
            except Exception as e:
                logger.debug(f"Activity log error: {e}")
        logger.debug(f"[ACTIVITY] {message}")

    def _get_energy(self) -> float:
        """Holt aktuelles Energie-Level"""
        if self.energy_system:
            try:
                return self.energy_system.state.effective_energy
            except Exception:
                pass
        return 0.5

    def _get_boredom(self) -> float:
        """Holt Langeweile von ProactiveIntelligence"""
        return self.proactive.proactive_emotions.get('boredom', 0.0)

    def _set_boredom(self, value: float):
        """Setzt Langeweile in ProactiveIntelligence"""
        self.proactive.proactive_emotions['boredom'] = max(0.0, min(1.0, value))

    def _calculate_motivation(self) -> float:
        """
        Berechnet aktuelle Motivation basierend auf:
        - Energie (müde = weniger Motivation)
        - Langeweile (hohe Langeweile = MEHR Motivation als Antrieb!)
        - Zufriedenheit
        - Zufälliger Faktor
        """
        energy = self._get_energy()
        boredom = self._get_boredom()

        # Basis: Energie ist wichtig
        base_motivation = energy * 0.5

        # Langeweile als Antrieb! (umgekehrt zur Intuition)
        # Bei niedriger Langeweile: kein Antrieb
        # Bei hoher Langeweile: starker Antrieb etwas zu tun
        boredom_drive = 0.0
        if boredom > 0.5:
            # Ab 50% Langeweile steigt der Antrieb
            boredom_drive = (boredom - 0.5) * 0.8

        # Zufriedenheit dämpft
        satisfaction_factor = self.satisfaction * 0.2

        # Zufälliger Faktor
        random_factor = random.uniform(-0.1, 0.1)

        motivation = base_motivation + boredom_drive + satisfaction_factor + random_factor

        # Clamp
        self.motivation = max(0.0, min(1.0, motivation))
        return self.motivation

    def _select_activity(self) -> Optional[str]:
        """
        Wählt eine Aktivität basierend auf:
        - Energie (manche brauchen mehr)
        - Motivation
        - Präferenzen
        - Cooldowns
        """
        energy = self._get_energy()
        motivation = self._calculate_motivation()

        # Keine Motivation? Keine Aktivität
        if motivation < self.MOTIVATION_THRESHOLDS['very_low']:
            return None

        # ============================================================
        # SEHR NIEDRIGE ENERGIE? → Automatisch schlafen/ruhen!
        # ============================================================
        if energy < 0.15:
            # Kritisch niedrig → Schlafen!
            logger.info(f"[ENERGY] 😴 Energy critical ({energy:.2f}) - forcing sleep!")
            return 'sleeping'
        elif energy < 0.25:
            # Sehr niedrig → Nickerchen
            logger.info(f"[ENERGY] 💤 Energy very low ({energy:.2f}) - suggesting nap")
            return 'napping'
        elif energy < 0.35:
            # Niedrig → Ruhen bevorzugen
            if random.random() < 0.7:  # 70% Chance auf Ruhe
                return random.choice(['resting', 'observing', 'napping'])

        available = []

        for activity_id, activity in self.ACTIVITIES.items():
            # Genug Energie?
            if energy < activity['energy_required']:
                continue

            # Cooldown abgelaufen?
            cooldown_end = self.activity_cooldowns.get(activity_id, 0)
            if time.time() < cooldown_end:
                continue

            # Score berechnen
            preference = self.activity_preferences.get(activity_id, 0.5)
            category_bonus = self._get_category_bonus(activity['category'], motivation, energy)

            score = preference * 0.4 + category_bonus * 0.4 + random.uniform(0, 0.2)

            available.append((activity_id, score))

        if not available:
            return None

        # Sortiere nach Score und wähle gewichtet
        available.sort(key=lambda x: x[1], reverse=True)

        # Top 3 zur Auswahl mit Gewichtung
        top = available[:min(3, len(available))]
        weights = [a[1] for a in top]
        total = sum(weights)
        if total == 0:
            return top[0][0]

        # Gewichtete Zufallswahl
        r = random.uniform(0, total)
        cumsum = 0
        for activity_id, score in top:
            cumsum += score
            if r <= cumsum:
                return activity_id

        return top[0][0]

    def _get_category_bonus(self, category: str, motivation: float, energy: float) -> float:
        """Gibt Bonus basierend auf Kategorie und Zustand"""
        boredom = self._get_boredom()

        if category == 'rest':
            # Ruhen bei niedriger Energie
            return (1 - energy) * 0.5

        elif category == 'play':
            # Spielen bei hoher Energie und Langeweile
            return energy * 0.3 + boredom * 0.3

        elif category == 'learning':
            # Lernen bei mittlerer-hoher Energie
            if energy > 0.4:
                return 0.3 + self.proactive.proactive_emotions.get('restlessness', 0) * 0.2
            return 0.1

        elif category == 'creative':
            # Kreativ bei Langeweile und etwas Energie
            return boredom * 0.3 + energy * 0.2

        elif category == 'reflection':
            # Reflexion bei hoher Nachdenklichkeit
            return self.proactive.proactive_emotions.get('reflection', 0) * 0.4

        elif category == 'hobby':
            # Hobbys sind immer gut
            return 0.3 + motivation * 0.2

        return 0.2

    def update(self, time_delta: float = 60.0) -> Optional[Dict]:
        """
        Haupt-Update Funktion. Sollte regelmäßig aufgerufen werden.

        Aktivitäten werden ins Life-Log geschrieben, NICHT in den Chat!
        Während einer Aktivität sinken ALLE negativen Emotionen.

        NEU: DriveSystem verbraucht Antriebe während Aktivitäten!

        Returns:
            None - Aktivitäten gehen nur ins Life-Log
        """
        now = time.time()
        time_delta_minutes = time_delta / 60

        # Schlafmodus? Keine Aktivitäten
        if self.proactive._is_sleep_hours():
            self.current_activity = None
            return None

        # === DRIVE SYSTEM UPDATE (NEU!) ===
        if self.drive_system:
            try:
                # DriveSystem updaten (regeneriert Antriebe wenn keine Aktivität)
                drive_events = self.drive_system.update(time_delta)

                # Events verarbeiten
                for event in drive_events.get('events', []):
                    if event.get('type') == 'thought':
                        # Nachdenklicher Gedanke - ins Life-Log
                        thought = event.get('thought')
                        if thought and hasattr(thought, 'thought'):
                            self._log_activity(f"💭 {thought.thought}", "thought")

                    elif event.get('type') == 'proactive_trigger':
                        # Proaktive Nachricht sollte gesendet werden
                        self.proactive.proactive_emotions['contact_desire'] = min(1.0,
                            self.proactive.proactive_emotions.get('contact_desire', 0) + 0.3)
            except Exception as e:
                logger.debug(f"DriveSystem update error: {e}")

        # === AKTUELLE AKTIVITÄT PRÜFEN ===
        if self.current_activity:
            elapsed_minutes = (now - self.activity_start_time) / 60

            # === DRIVE SYSTEM: Antrieb verbrauchen (NEU!) ===
            if self.drive_system and ACTIVITY_DRIVE_MAP:
                try:
                    drive_type = ACTIVITY_DRIVE_MAP.get(self.current_activity)
                    if drive_type:
                        # Antrieb verbrauchen
                        drain = DriveConfig.DRAIN_PER_MINUTE * time_delta_minutes
                        self.drive_system.drives.drain(drive_type, drain)

                        # Prüfen ob Antrieb leer
                        current_drive = self.drive_system.drives.get(drive_type)
                        if current_drive <= 0.02:
                            # Antrieb leer - Aktivität beenden!
                            activity = self.ACTIVITIES.get(self.current_activity, {})
                            self._log_activity(
                                f"😐 Keine Lust mehr auf {activity.get('name', self.current_activity)} "
                                f"({drive_type.value} ist leer)", "drive_empty"
                            )
                            self._finish_activity_drive_empty()
                            return None
                except Exception as e:
                    logger.debug(f"Drive drain error: {e}")

            if elapsed_minutes >= self.activity_duration:
                # Aktivität beendet!
                self._finish_activity()
                return None  # Nicht in Chat!
            else:
                # Noch beschäftigt - ALLE negativen Emotionen sinken!
                activity = self.ACTIVITIES.get(self.current_activity, {})
                reduction_rate = 0.02 * (time_delta / 60)  # 2% pro Minute

                pe = self.proactive.proactive_emotions

                # Langeweile sinkt am stärksten
                boredom_reduction = activity.get('boredom_reduction', 0.2) * (time_delta / 60) * 0.15
                pe['boredom'] = max(0.0, pe.get('boredom', 0) - boredom_reduction)

                # Einsamkeit sinkt - sie ist ja beschäftigt!
                pe['loneliness'] = max(0.0, pe.get('loneliness', 0) - reduction_rate * 0.8)

                # Vermissen sinkt langsamer - aber auch
                pe['missing'] = max(0.0, pe.get('missing', 0) - reduction_rate * 0.3)

                # Tatendrang sinkt - sie TUT ja was
                pe['restlessness'] = max(0.0, pe.get('restlessness', 0) - reduction_rate * 1.5)

                # Traurigkeit sinkt
                pe['sadness'] = max(0.0, pe.get('sadness', 0) - reduction_rate * 0.5)

                # Nachdenklichkeit sinkt bei aktiven Aktivitäten
                if activity.get('category') not in ['reflection', 'creative']:
                    pe['reflection'] = max(0.0, pe.get('reflection', 0) - reduction_rate * 0.5)

                # Kontaktbedürfnis sinkt leicht
                pe['contact_desire'] = max(0.1, pe.get('contact_desire', 0.3) - reduction_rate * 0.2)

                return None

        # === ENERGIE NIEDRIG? Nickerchen oder Ruhen (NEU!) ===
        if self.drive_system:
            try:
                energy_decision = self.drive_system.check_energy_and_decide()
                if energy_decision:
                    # DriveSystem hat Nickerchen/Ruhen gestartet
                    if energy_decision.get('type') == 'nap':
                        self._start_activity('napping')
                    elif energy_decision.get('type') == 'rest':
                        self._start_activity('resting')
                    return None
            except Exception as e:
                logger.debug(f"Energy decision error: {e}")

        # === KEINE AKTIVITÄT - MOTIVATION PRÜFEN ===
        motivation = self._calculate_motivation()
        boredom = self._get_boredom()

        # Bei niedriger Motivation: Langeweile steigt
        if motivation < self.MOTIVATION_THRESHOLDS['low']:
            boredom_increase = 0.05 * (time_delta / 60)

            # Je niedriger die Motivation, desto schneller steigt Langeweile
            boredom_increase *= (1 + (self.MOTIVATION_THRESHOLDS['low'] - motivation))

            self._set_boredom(boredom + boredom_increase)

            # DriveSystem: Langeweile auch dort erhöhen
            if self.drive_system:
                self.drive_system.needs.increase(NeedType.BOREDOM, boredom_increase * 0.5)

            # Bei sehr hoher Langeweile: Motivations-Kick!
            if boredom > 0.8:
                # Antrieb durch Langeweile - jetzt MUSS was passieren
                self.proactive.proactive_emotions['restlessness'] = min(1.0,
                    self.proactive.proactive_emotions.get('restlessness', 0) + 0.2)

                # Neuberechnung mit dem Langeweile-Antrieb
                motivation = self._calculate_motivation()

        # === NEUE AKTIVITÄT STARTEN? ===
        if motivation >= self.MOTIVATION_THRESHOLDS['low']:
            activity_id = self._select_activity()

            if activity_id:
                # DriveSystem: Prüfen ob genug Antrieb vorhanden
                if self.drive_system and ACTIVITY_DRIVE_MAP:
                    drive_type = ACTIVITY_DRIVE_MAP.get(activity_id)
                    if drive_type:
                        drive_level = self.drive_system.drives.get(drive_type)
                        if drive_level < 0.1:
                            # Nicht genug Antrieb - andere Aktivität wählen
                            self._log_activity(f"💭 Keine Lust auf {ACTIVITY_NAMES_DE.get(activity_id, activity_id)}...", "no_drive")
                            # Versuche andere Aktivität oder langweilen
                            if random.random() < 0.7:  # 70% langweilen
                                self._log_activity("💭 Mir ist langweilig...", "boredom")
                                if self.drive_system:
                                    self.drive_system.needs.increase(NeedType.BOREDOM, 0.15)
                                return None
                            else:
                                # Andere Aktivität versuchen
                                activity_id = self._select_activity_with_drive()
                                if not activity_id:
                                    return None

                self._start_activity(activity_id)
                return None  # Nicht in Chat!

        return None

    def _select_activity_with_drive(self) -> Optional[str]:
        """Wählt Aktivität basierend auf verfügbaren Antrieben (NEU!)"""
        if not self.drive_system:
            return self._select_activity()

        available = []

        # Neugier-Aktivitäten
        if self.drive_system.drives.curiosity > 0.15:
            available.extend(['reading', 'researching', 'learning', 'deep_dive'])

        # Unterhaltungs-Aktivitäten
        if self.drive_system.drives.entertainment > 0.15:
            available.extend(['playing', 'watching_anime', 'music', 'gaming'])

        # Kreative Aktivitäten
        if self.drive_system.drives.creativity > 0.15:
            available.extend(['drawing', 'storytelling'])

        # Immer verfügbar: Ruhe-Aktivitäten
        available.extend(['thinking', 'daydreaming', 'meditating'])

        # Aus verfügbaren wählen (mit Cooldown-Check)
        random.shuffle(available)
        for activity_id in available:
            if activity_id in self.ACTIVITIES:
                cooldown = self.activity_cooldowns.get(activity_id, 0)
                if time.time() > cooldown:
                    return activity_id

        return None

    def _finish_activity_drive_empty(self):
        """Beendet Aktivität weil Antrieb leer ist (NEU!)"""
        if not self.current_activity:
            return

        activity = self.ACTIVITIES.get(self.current_activity)
        if not activity:
            self.current_activity = None
            return

        # Speichere letzte Aktivität für Kontext
        self.last_finished_activity = {
            'id': self.current_activity,
            'name': activity['name'],
            'category': activity.get('category', ''),
            'elapsed_minutes': int((time.time() - self.activity_start_time) / 60),
            'reason': 'drive_empty',
        }
        self.last_finished_time = time.time()

        elapsed = int((time.time() - self.activity_start_time) / 60)
        self._log_activity(f"✅ {activity['name']} beendet ({elapsed}min) - keine Lust mehr", "activity_ended")

        # Entscheidung: 30% neue Aktivität, 70% langweilen
        if self.drive_system:
            roll = random.random()
            if roll < 0.30:
                # Neue Aktivität mit verfügbarem Antrieb
                new_activity = self._select_activity_with_drive()
                if new_activity:
                    self._log_activity(f"💭 Mache als nächstes: {ACTIVITY_NAMES_DE.get(new_activity, new_activity)}", "decision")
                    self.current_activity = None
                    self._start_activity(new_activity)
                    return

            # Langweilen
            self._log_activity("💭 Mir ist langweilig...", "boredom")
            self.drive_system.needs.increase(NeedType.BOREDOM, 0.15)

        self.current_activity = None

    def _start_activity(self, activity_id: str):
        """Startet eine neue Aktivität - mit echtem Lesen und Energy-Verbrauch!"""
        activity = self.ACTIVITIES.get(activity_id)
        if not activity:
            return

        self.current_activity = activity_id
        self.activity_start_time = time.time()
        self.activity_duration = random.randint(
            activity['duration_min'],
            activity['duration_max']
        )

        # Cooldown setzen (2x Dauer)
        self.activity_cooldowns[activity_id] = time.time() + (self.activity_duration * 60 * 2)

        # Statistik
        self.activities_today.append(activity_id)
        self.total_activities += 1

        # Langeweile sofort etwas reduzieren
        self._set_boredom(self._get_boredom() - 0.1)

        # ============================================================
        # ENERGY-MANAGEMENT: Verbrauch und Rest-Modus
        # ============================================================
        if self.energy_system:
            try:
                category = activity.get('category', '')

                # Bei Ruhe-Aktivitäten: Rest-Modus starten!
                if category == 'rest' or activity_id in ['resting', 'napping', 'sleeping']:
                    if hasattr(self.energy_system, 'start_rest'):
                        self.energy_system.start_rest()
                        logger.info(f"[ENERGY] 😴 Rest-Modus gestartet für: {activity['name']}")

                # Bei aktiven Aktivitäten: Energie verbrauchen!
                else:
                    # Mappe Activity zu ActivityType
                    activity_type_map = {
                        'reading': 'LEARNING',
                        'researching': 'RESEARCHING',
                        'learning': 'LEARNING',
                        'deep_dive': 'RESEARCHING',
                        'hobby_explore': 'LEARNING',
                        'mood_brainstorm': 'RESEARCHING',
                        'thinking': 'DEEP_THINKING',
                        'meditating': 'IDLE',
                        'daydreaming': 'IDLE',
                        'storytelling': 'DEEP_THINKING',
                        'drawing': 'WORKING',
                        'music': 'IDLE',
                        'playing': 'CHATTING',
                        'watching_anime': 'IDLE',
                        'gaming': 'LEARNING',
                    }

                    activity_type_name = activity_type_map.get(activity_id, 'IDLE')

                    try:
                        from holo_energy_system import ActivityType
                        act_type = getattr(ActivityType, activity_type_name, ActivityType.IDLE)

                        # WICHTIG: Setze aktuelle Aktivität für laufenden Verbrauch!
                        if hasattr(self.energy_system, 'set_activity'):
                            self.energy_system.set_activity(act_type)
                            logger.info(f"[ENERGY] 🎯 Activity set: {activity_type_name}")

                        # Verbrauche Energy für die geplante Dauer
                        if hasattr(self.energy_system, 'consume_for_activity'):
                            self.energy_system.consume_for_activity(act_type, self.activity_duration)
                            logger.info(f"[ENERGY] ⚡ Energy consumed for: {activity['name']} ({self.activity_duration}min)")

                    except ImportError:
                        pass

            except Exception as e:
                logger.debug(f"Energy management error: {e}")

        # ============================================================
        # NEU: Echtes Lesen wenn real_reading gesetzt ist!
        # ============================================================
        real_reading_type = activity.get('real_reading')
        reading_info = ""

        if real_reading_type and self.reading_engine:
            try:
                # Aktuelle Energy und Emotions holen!
                current_energy = self._get_energy()
                current_emotions = self.proactive.proactive_emotions.copy() if self.proactive else {}

                # Echten Inhalt lesen - MIT Energy und Emotions!
                self.current_reading = self.reading_engine.do_reading_activity(
                    real_reading_type,
                    energy_level=current_energy,
                    emotions=current_emotions
                )

                if self.current_reading:
                    title = self.current_reading.get('title', '')
                    source = self.current_reading.get('source_name', '')
                    thoughts = self.current_reading.get('holos_thoughts', '')

                    reading_info = f"\n   📖 Liest: '{title}' ({source})"
                    if thoughts:
                        reading_info += f"\n   💭 Gedanken: {thoughts[:100]}..."

                    logger.info(f"[READING] Echtes Lesen: {title}")

            except Exception as e:
                logger.debug(f"Real reading error: {e}")
                self.current_reading = None

        # ============================================================
        # NEU: Echte Medien aus MediaDiscovery für Media-Aktivitäten!
        # ============================================================
        self.current_media = None
        media_info = ""

        if self.media_discovery:
            try:
                media_entry = None

                # Wähle passendes Medium basierend auf Aktivität
                if activity_id == 'watching_anime':
                    media_entry = self.media_discovery.get_fresh_anime()
                    if media_entry:
                        self.current_media = {
                            'type': 'anime',
                            'title': media_entry.title,
                            'title_alt': media_entry.title_alt,
                            'studio': media_entry.studio,
                            'year': media_entry.year if media_entry.year > 0 else None,
                            'genres': media_entry.genres,
                            'synopsis': media_entry.synopsis[:200] if media_entry.synopsis else '',
                            'thoughts': media_entry.holos_thoughts,
                            'fun_facts': media_entry.fun_facts[:2] if media_entry.fun_facts else [],
                        }
                        media_info = f"\n   📺 Schaut: {media_entry.title}"
                        if media_entry.studio:
                            media_info += f" ({media_entry.studio})"
                        if media_entry.year > 0:
                            media_info += f" [{media_entry.year}]"
                        logger.info(f"[MEDIA] ✅ Anime gesetzt: {media_entry.title}")

                elif activity_id == 'gaming':
                    media_entry = self.media_discovery.get_fresh_game()
                    if media_entry:
                        self.current_media = {
                            'type': 'game',
                            'title': media_entry.title,
                            'developer': media_entry.developer,
                            'year': media_entry.year if media_entry.year > 0 else None,
                            'genres': media_entry.genres,
                            'synopsis': media_entry.synopsis[:200] if media_entry.synopsis else '',
                            'thoughts': media_entry.holos_thoughts,
                            'tips': media_entry.tips[:2] if media_entry.tips else [],
                            'fun_facts': media_entry.fun_facts[:2] if media_entry.fun_facts else [],
                        }
                        media_info = f"\n   🎮 Spielt: {media_entry.title}"
                        if media_entry.developer:
                            media_info += f" ({media_entry.developer})"
                        if media_entry.year > 0:
                            media_info += f" [{media_entry.year}]"
                        logger.info(f"[MEDIA] ✅ Game gesetzt: {media_entry.title}")

                elif activity_id == 'music':
                    media_entry = self.media_discovery.get_fresh_music()
                    if media_entry:
                        self.current_media = {
                            'type': 'music',
                            'title': media_entry.title,
                            'artist': media_entry.artist,
                            'genres': media_entry.genres,
                            'known_from': media_entry.known_from,
                            'year': media_entry.year if media_entry.year > 0 else None,
                            'thoughts': media_entry.holos_thoughts,
                            'fun_facts': media_entry.fun_facts[:2] if media_entry.fun_facts else [],
                        }
                        media_info = f"\n   🎵 Hört: {media_entry.title} - {media_entry.artist}"
                        if media_entry.known_from:
                            media_info += f" (aus {media_entry.known_from})"
                        if media_entry.year > 0:
                            media_info += f" [{media_entry.year}]"
                        logger.info(f"[MEDIA] ✅ Musik gesetzt: {media_entry.title} - {media_entry.artist}")
                else:
                    logger.debug(f"[MEDIA] Keine Media-Aktivität: {activity_id}")

            except Exception as e:
                logger.error(f"[MEDIA] ❌ MediaDiscovery Fehler: {e}")
        else:
            logger.warning(f"[MEDIA] ⚠️ MediaDiscovery nicht verfügbar!")

        # Ins Life-Log schreiben (NICHT Chat!)
        message = random.choice(activity['messages'][:1]) if activity['messages'] else f"Beginnt mit {activity['name']}"
        log_message = f"📚 Aktivität gestartet: {activity['name']} ({self.activity_duration}min) - {message}"

        if reading_info:
            log_message += reading_info
        if media_info:
            log_message += media_info

        self._log_activity(log_message, "activity")

        # ============================================================
        # NEU: ActivityContextTracker - SYNCHRON mit current_media!
        # ============================================================
        if hasattr(self, 'activity_context') and self.activity_context:
            try:
                # WICHTIG: Wenn current_media gesetzt wurde, nutze DIESE Daten
                # statt nochmal MediaDiscovery aufzurufen!
                if self.current_media:
                    # Setze current_context direkt mit unseren Media-Daten
                    media = self.current_media
                    media_type = media.get('type', '')
                    title = media.get('title', '')

                    description = ""
                    if media_type == 'anime':
                        description = f"Ich schaue gerade **{title}**. {media.get('thoughts', '')[:100]}"
                    elif media_type == 'game':
                        description = f"Ich spiele gerade **{title}**. {media.get('thoughts', '')[:100]}"
                    elif media_type == 'music':
                        artist = media.get('artist', '')
                        description = f"Ich höre gerade **{title}** von {artist}. {media.get('thoughts', '')[:100]}"

                    self.activity_context.current_context = {
                        "activity": activity_id,
                        "started_at": time.time(),
                        "details": {
                            "type": media_type,
                            "title": title,
                            "description": description,
                            "thoughts": media.get('thoughts', ''),
                            "source": "media_discovery_sync",
                            **media  # Alle anderen Felder übernehmen
                        }
                    }
                    logger.debug(f"[ACTIVITY] Context synced from current_media: {title}")
                else:
                    # Fallback: Normaler start_activity Aufruf
                    context = self.activity_context.start_activity(activity_id)
                    if context and context.get("details"):
                        details = context["details"]
                        logger.debug(f"[ACTIVITY] Context: {details.get('type')} - {details.get('description', '')[:50]}")
            except Exception as e:
                logger.debug(f"Activity context error: {e}")

    def _finish_activity(self):
        """Beendet die aktuelle Aktivität - mit Energy-Wiederherstellung!"""
        if not self.current_activity:
            return

        activity = self.ACTIVITIES.get(self.current_activity)
        if not activity:
            self.current_activity = None
            return

        # ============================================================
        # ENERGY-MANAGEMENT: Wiederherstellung bei Ruhe
        # ============================================================
        if self.energy_system:
            try:
                category = activity.get('category', '')

                # Bei Ruhe-Aktivitäten: Rest-Modus beenden und Energy wiederherstellen
                if category == 'rest' or self.current_activity in ['resting', 'napping', 'sleeping']:
                    elapsed_hours = (time.time() - self.activity_start_time) / 3600

                    # Rest beenden
                    if hasattr(self.energy_system, '_end_rest'):
                        self.energy_system._end_rest()
                        logger.info("[ENERGY] 🌅 Rest-Modus beendet")

                    # Manuell Energy wiederherstellen basierend auf Dauer
                    energy_restore = activity.get('energy_restore', 0.1)
                    restore_amount = energy_restore * (elapsed_hours / 0.5)  # Skaliert mit Zeit
                    restore_amount = min(0.4, restore_amount)  # Max 40% pro Ruhe-Session

                    if hasattr(self.energy_system, 'state'):
                        old_energy = self.energy_system.state.variable_energy
                        self.energy_system.state.variable_energy = min(
                            1.0,
                            self.energy_system.state.variable_energy + restore_amount
                        )
                        new_energy = self.energy_system.state.variable_energy
                        logger.info(f"[ENERGY] 🔋 Energy restored: {old_energy:.2f} → {new_energy:.2f} (+{restore_amount:.2f})")

                        # Speichern
                        if hasattr(self.energy_system, '_save_state'):
                            self.energy_system._save_state()

                # Bei Schlafen/Nickerchen: Mehr Regeneration!
                if self.current_activity in ['sleeping', 'napping']:
                    elapsed_hours = (time.time() - self.activity_start_time) / 3600

                    if hasattr(self.energy_system, 'state'):
                        # Schlafen regeneriert auch base_energy!
                        base_restore_rate = activity.get('base_energy_restore', 0)
                        if base_restore_rate > 0:
                            # Skaliert mit Zeit, max ist der definierte Wert
                            base_restore = min(base_restore_rate, elapsed_hours * 0.2)
                            old_base = self.energy_system.state.base_energy
                            self.energy_system.state.base_energy = min(
                                1.0,
                                self.energy_system.state.base_energy + base_restore
                            )
                            new_base = self.energy_system.state.base_energy
                            logger.info(f"[ENERGY] 😴 Base energy restored: {old_base:.2f} → {new_base:.2f} (+{base_restore:.2f})")

                        if hasattr(self.energy_system, '_save_state'):
                            self.energy_system._save_state()

                # Am Ende: Aktivität zurück auf IDLE setzen
                try:
                    from holo_energy_system import ActivityType
                    if hasattr(self.energy_system, 'set_activity'):
                        self.energy_system.set_activity(ActivityType.IDLE)
                        logger.info("[ENERGY] 🎯 Activity reset to IDLE")
                except ImportError:
                    pass

            except Exception as e:
                logger.debug(f"Energy restore error: {e}")

        # Effekte anwenden
        boredom_reduction = activity.get('boredom_reduction', 0.2)
        self._set_boredom(self._get_boredom() - boredom_reduction)

        satisfaction = activity.get('satisfaction', 0.3)
        self.satisfaction = min(1.0, self.satisfaction + satisfaction * 0.3)

        # Spezielle Boosts
        if 'creativity_boost' in activity:
            self.proactive.proactive_emotions['excitement'] = min(1.0,
                self.proactive.proactive_emotions.get('excitement', 0) + activity['creativity_boost'])

        if 'reflection_boost' in activity:
            self.proactive.proactive_emotions['reflection'] = min(1.0,
                self.proactive.proactive_emotions.get('reflection', 0) + activity['reflection_boost'])

        if 'pride_boost' in activity:
            self.proactive.proactive_emotions['pride'] = min(1.0,
                self.proactive.proactive_emotions.get('pride', 0) + activity['pride_boost'])

        # NEU: Happiness-Boost für Hobby-Aktivitäten
        if 'happiness_boost' in activity:
            self.proactive.proactive_emotions['happiness'] = min(1.0,
                self.proactive.proactive_emotions.get('happiness', 0) + activity['happiness_boost'])

        # Tatendrang sinkt nach Aktivität
        self.proactive.proactive_emotions['restlessness'] = max(0.0,
            self.proactive.proactive_emotions.get('restlessness', 0) - 0.3)

        # Präferenz anpassen (positive Verstärkung)
        old_pref = self.activity_preferences.get(self.current_activity, 0.5)
        self.activity_preferences[self.current_activity] = min(1.0, old_pref + 0.05)

        finished_activity = self.current_activity
        finished_name = activity['name']
        elapsed = int((time.time() - self.activity_start_time) / 60)

        # ============================================================
        # NEU: Bei echtem Lesen detaillierteres Log
        # ============================================================
        reading_summary = ""
        if self.current_reading:
            title = self.current_reading.get('title', '')
            summary = self.current_reading.get('summary', '')
            fact = self.current_reading.get('interesting_fact', '')

            reading_summary = f"\n   📖 Gelesen: '{title}'"
            if summary:
                reading_summary += f"\n   📝 Zusammenfassung: {summary[:150]}..."
            if fact:
                reading_summary += f"\n   💡 Interessanter Fakt: {fact}"

            # Neugier steigt wenn was Interessantes gelesen wurde
            if fact:
                self.proactive.proactive_emotions['excitement'] = min(1.0,
                    self.proactive.proactive_emotions.get('excitement', 0) + 0.15)

            self.current_reading = None

        # NEU: Media-Kontext kopieren bevor wir löschen
        finished_media = None
        if self.current_media:
            finished_media = self.current_media.copy()
            media_title = self.current_media.get('title', '')
            self.current_media = None
            logger.debug(f"[MEDIA] Beendet: {media_title}")

        # NEU: Speichere letzte Aktivität für Kontext (inkl. Media!)
        self.last_finished_activity = {
            'id': self.current_activity,
            'name': activity['name'],
            'category': activity.get('category', ''),
            'elapsed_minutes': int((time.time() - self.activity_start_time) / 60),
        }
        if finished_media:
            self.last_finished_activity['media'] = finished_media
        self.last_finished_time = time.time()

        # ============================================================
        # NEU: ActivityContextTracker - Aktivität beenden
        # ============================================================
        if hasattr(self, 'activity_context') and self.activity_context:
            try:
                ended_context = self.activity_context.end_activity()
                if ended_context:
                    self.last_finished_activity['context'] = ended_context.get('details')
            except Exception as e:
                logger.debug(f"Activity context end error: {e}")

        self.current_activity = None

        # Ins Life-Log schreiben (NICHT Chat!)
        messages = activity.get('messages', ["Fertig!"])
        message = random.choice(messages[1:]) if len(messages) > 1 else safe_list_access(messages, 0, "inner_life", "_end_activity", default="Fertig!")
        log_message = f"✅ Aktivität beendet: {finished_name} ({elapsed}min) - {message}"

        if reading_summary:
            log_message += reading_summary

        self._log_activity(log_message, "activity")

    def on_user_interaction(self):
        """User interagiert - Aktivität wird ggf. unterbrochen"""
        if self.current_activity:
            # Kurze Aktivitäten unterbrechen, lange pausieren
            elapsed = (time.time() - self.activity_start_time) / 60
            remaining = self.activity_duration - elapsed

            if remaining < 5:
                # Fast fertig - schnell beenden
                self._finish_activity()
            # Sonst: Aktivität läuft weiter im Hintergrund

    def get_current_activity(self) -> Optional[Dict]:
        """Gibt aktuelle Aktivität zurück"""
        if not self.current_activity:
            return None

        activity = self.ACTIVITIES.get(self.current_activity, {})
        elapsed = (time.time() - self.activity_start_time) / 60

        result = {
            'id': self.current_activity,
            'name': activity.get('name', ''),
            'category': activity.get('category', ''),
            'elapsed_minutes': int(elapsed),
            'duration_minutes': self.activity_duration,
            'progress': min(1.0, elapsed / self.activity_duration)
        }

        # NEU: Media-Details hinzufügen wenn vorhanden
        if self.current_media:
            result['media'] = self.current_media
            logger.debug(f"[ACTIVITY] get_current_activity() - media: {self.current_media.get('title', 'unknown')}")
        else:
            logger.debug(f"[ACTIVITY] get_current_activity() - KEINE media für {self.current_activity}")

        return result

    def get_status(self) -> Dict:
        """Gibt Status zurück"""
        status = {
            'current_activity': self.get_current_activity(),
            'motivation': self.motivation,
            'satisfaction': self.satisfaction,
            'activities_today': len(self.activities_today),
            'total_activities': self.total_activities,
            'top_preferences': sorted(
                self.activity_preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }

        # Reading-Info hinzufügen
        if self.reading_engine:
            reading_status = self.reading_engine.get_status()
            status['reading'] = {
                'articles_today': reading_status.get('articles_today', 0),
                'total_articles': reading_status.get('total_articles', 0),
                'remembered_facts': reading_status.get('remembered_facts', 0),
                'last_readings': reading_status.get('last_readings', [])
            }

            # Aktuelles Lesen
            if self.current_reading:
                status['current_reading'] = {
                    'title': self.current_reading.get('title', ''),
                    'source': self.current_reading.get('source_name', '')
                }

        return status

    def get_all_activities_status(self) -> List[Dict]:
        """
        Gibt ALLE verfügbaren Aktivitäten mit ihrem Verbindungsstatus zurück.

        Für UI die zeigt welche Fähigkeiten aktiv sind und welche nicht.
        """
        activities = []

        # === KREATIVE AKTIVITÄTEN ===
        activities.append({
            "name": "Gedichte/Geschichten schreiben",
            "emoji": "📝",
            "required_tool": "CreativeLearningEngine",
            "connected": self.creative_learning is not None,
            "description": "Echtes kreatives Schreiben mit Lernen und Reflexion"
        })

        activities.append({
            "name": "ASCII-Art erstellen",
            "emoji": "🖼️",
            "required_tool": "ASCIIArtEngine",
            "connected": self.ascii_art is not None,
            "description": "ASCII-Art aus 8 Basis-Formen + Emoticons"
        })

        # === AUTONOME AKTIVITÄTEN ===
        activities.append({
            "name": "Tagträumen",
            "emoji": "💭",
            "required_tool": "AutonomousActivity",
            "connected": True,  # Immer verfügbar (intern)
            "description": "Lässt die Gedanken schweifen"
        })

        activities.append({
            "name": "Philosophieren",
            "emoji": "🤔",
            "required_tool": "AutonomousActivity",
            "connected": True,
            "description": "Denkt über tiefere Fragen nach"
        })

        activities.append({
            "name": "An dich denken",
            "emoji": "💕",
            "required_tool": "AutonomousActivity",
            "connected": True,
            "description": "Denkt über die Beziehung zum User nach"
        })

        # === MEMORY AKTIVITÄTEN ===
        activities.append({
            "name": "Erinnerungen durchgehen",
            "emoji": "📚",
            "required_tool": "Memory System",
            "connected": self.memory is not None,
            "description": "Schaut sich alte Gespräche an"
        })

        # === MEDIA AKTIVITÄTEN ===
        activities.append({
            "name": "Neue Anime/Games entdecken",
            "emoji": "🎮",
            "required_tool": "MediaDiscovery",
            "connected": self.media_discovery is not None,
            "description": "Entdeckt neue Medien zum Empfehlen"
        })

        # === NETZWERK AKTIVITÄTEN ===
        activities.append({
            "name": "Netzwerk/SmartHome beobachten",
            "emoji": "🌐",
            "required_tool": "Pi-Control",
            "connected": self.comm is not None,
            "description": "Schaut was im Netzwerk passiert"
        })

        # === TOOL AKTIVITÄTEN ===
        tools_connected = self.tools is not None

        activities.append({
            "name": "Timer setzen",
            "emoji": "⏱️",
            "required_tool": "HoloTools",
            "connected": tools_connected,
            "description": "Verwaltet Timer und Erinnerungen"
        })

        activities.append({
            "name": "Notizen machen",
            "emoji": "📝",
            "required_tool": "HoloTools",
            "connected": tools_connected,
            "description": "Speichert Notizen"
        })

        activities.append({
            "name": "Todos verwalten",
            "emoji": "✅",
            "required_tool": "HoloTools",
            "connected": tools_connected,
            "description": "Verwaltet Aufgabenlisten"
        })

        activities.append({
            "name": "Einkaufsliste",
            "emoji": "🛒",
            "required_tool": "HoloTools",
            "connected": tools_connected,
            "description": "Verwaltet Einkaufsliste"
        })

        activities.append({
            "name": "Rechnen",
            "emoji": "🔢",
            "required_tool": "Calculator",
            "connected": tools_connected,
            "description": "Mathematische Berechnungen"
        })

        # === NEWS & LERNEN ===
        activities.append({
            "name": "News lesen",
            "emoji": "📰",
            "required_tool": "ReadingEngine",
            "connected": self.reading_engine is not None,
            "description": "Liest und lernt aus News-Artikeln"
        })

        activities.append({
            "name": "Web recherchieren",
            "emoji": "🔍",
            "required_tool": "WebCuriosity",
            "connected": self.web_curiosity is not None,
            "description": "Sucht im Web nach Informationen"
        })

        return activities

    def get_reading_for_chat(self) -> Optional[str]:
        """
        Gibt etwas zurück das Holo im Chat über Gelesenes sagen kann.
        Für proaktive Nachrichten oder Antworten auf "Was hast du gemacht?"
        """
        if not self.reading_engine:
            return None

        return self.reading_engine.get_reading_for_chat()

    def get_recent_facts(self, limit: int = 5) -> List[str]:
        """Gibt die zuletzt gelernten Fakten zurück"""
        if not self.reading_engine:
            return []

        facts = self.reading_engine.remembered_facts[-limit:]
        return [f.get('fact', '') for f in facts if f.get('fact')]

    # =========================================================================
    # 📚 ECHTES LERNEN (HoloLearningSystem)
    # =========================================================================

    def _do_learn_from_news(self, category: str = None) -> Dict:
        """
        Lernt aus aktuellen News - ECHTES LERNEN!

        Nutzt das HoloLearningSystem um echte Fakten zu speichern.
        """
        if not self.learning_system:
            self._log_activity("📚 Learning System nicht verbunden...", "warning")
            return {"message": "Learning System nicht verfügbar", "facts_learned": 0}

        # Kategorie basierend auf Holos Interessen wählen wenn nicht angegeben
        if not category:
            interests = ["anime", "gaming", "technik", "serien"]
            weights = [0.95, 0.9, 0.7, 0.6]  # Holos Präferenzen
            category = random.choices(interests, weights=weights, k=1)[0]

        result = self.learning_system.learn(category)

        facts_learned = result.get("facts_learned", 0)
        articles_read = result.get("articles_read", 0)

        if facts_learned > 0:
            self._log_activity(
                f"📚 {facts_learned} neue Fakten über {category.title()} gelernt! "
                f"({articles_read} Artikel gelesen)",
                "learning"
            )
            # Langeweile senken - Lernen ist interessant!
            self._set_boredom(max(0, self._get_boredom() - 0.15))
            # Zufriedenheit erhöhen
            self.satisfaction = min(1.0, self.satisfaction + 0.1)
        else:
            self._log_activity(
                f"📰 News bei {category.title()} gecheckt - nichts Neues",
                "learning"
            )

        return result

    def _do_explore_interest(self, topic: str = None) -> Dict:
        """
        Erforscht ein Interessengebiet gezielt.
        """
        if not self.learning_system:
            return {"message": "Learning System nicht verfügbar"}

        # Wenn kein Topic, aus aktiven Topics wählen
        if not topic:
            try:
                active_topics = self.learning_system.topic_tracker.get_active_topics(10)
                if active_topics:
                    topic = random.choice(active_topics).topic
                else:
                    topic = random.choice(["Anime", "Gaming", "Technik", "KI"])
            except Exception:
                topic = "Anime"

        result = self.learning_system.learning.learn_topic(topic)

        new_facts = result.get("new_facts", 0)
        if new_facts > 0:
            self._log_activity(
                f"🔍 '{topic}' erforscht - {new_facts} neue Fakten entdeckt!",
                "research"
            )
            self._set_boredom(max(0, self._get_boredom() - 0.2))

        return result

    def share_interesting_fact(self) -> Optional[str]:
        """
        Teilt einen interessanten Fakt (für proaktive Nachrichten).

        Returns:
            Natürliche Nachricht mit einem Fakt oder None
        """
        if not self.learning_system:
            return None

        try:
            recent = self.learning_system.get_recent_knowledge(limit=10)
            if not recent:
                return None

            fact = random.choice(recent)

            intros = [
                "*Ohren zucken aufgeregt* Ich hab da was Interessantes gelesen!",
                "*wedelt* Wusstest du schon...?",
                "*setzt sich aufrecht hin* Das muss ich dir erzählen!",
                "*Schweif wedelt* Oh oh, guck mal was ich gefunden hab!",
            ]

            return f"{random.choice(intros)}\n\n{fact.content}"
        except Exception as e:
            logger.debug(f"share_interesting_fact error: {e}")
            return None


# =============================================================================
# LERN-ENGINE
# =============================================================================



# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("😊 HOLO AUTONOMOUS LIFE - TEST")
    print("=" * 60)

    life = HoloAutonomousLife()

    # Simuliere Zeit ohne Interaktion
    print("\n--- Simuliere 2 Stunden ohne Interaktion ---\n")

    for i in range(24):  # 24 * 5 Minuten = 2 Stunden
        result = life.update(had_interaction=False)

        if result.get("thought"):
            print(f"  💭 {result['thought']}")

        if result.get("wants_to_contact"):
            print(f"  📨 Will Kontakt: {result['contact_message']}")

        if result.get("activity_performed"):
            act = result["activity_performed"]
            print(f"  🎯 Aktivität: {act['activity']}")

        # Simuliere 5 Minuten
        life.last_update -= 5 * 60

    print("\n--- Status nach 2 Stunden ---")
    status = life.get_status()

    print(f"\n📊 Langeweile: {status['boredom']['level']:.1%}")
    print(f"⏰ Zeit allein: {status['boredom']['time_alone_hours']:.1f}h")
    print(f"💭 Motivation: {status['dominant_motivation']}")

    print("\n🎯 Triebe:")
    for name, drive in status['drives'].items():
        bar = "█" * int(drive['level'] * 10) + "░" * (10 - int(drive['level'] * 10))
        urgent = " ⚠️" if drive['is_urgent'] else ""
        print(f"   {drive['name']}: [{bar}] {drive['level']:.1%}{urgent}")

    print("\n--- Simuliere User-Interaktion ---")
    life.on_user_interaction("Hey Holo! Das ist interessant, erzähl mehr!")

    status = life.get_status()
    print(f"\n📊 Langeweile danach: {status['boredom']['level']:.1%}")
    print(f"💭 Innerer Zustand: {life.get_inner_state_description()}")

    print("\n" + "=" * 60)
    print("✅ Test abgeschlossen")
    print("=" * 60)


# =============================================================================
# AUTONOMY CONFIG (aus holo_autonomy_engine.py)
# =============================================================================

class AutonomyConfig:
    """Konfiguration für die Autonomie"""
    # Initiative Timing
    min_silence_for_initiative: int = 3600     # 1 Stunde bis Initiative
    max_silence_for_initiative: int = 28800    # 8 Stunden max
    initiative_chance_per_hour: float = 0.3    # 30% Chance pro Stunde

    # Gedanken
    thought_interval_minutes: int = 30         # Alle 30 Min ein Gedanke
    max_stored_thoughts: int = 20              # Max gespeicherte Gedanken

    # Erinnerungen
    followup_delay_hours: int = 24             # Nach 24h nachfragen
    max_tracked_topics: int = 10               # Max getrackte Themen

    # Tageszeit-Faktoren
    active_hours: Tuple[int, int] = (8, 22)    # Aktiv von 8-22 Uhr
    quiet_hours: Tuple[int, int] = (23, 7)     # Ruhe von 23-7 Uhr


# =============================================================================
# INITIATIVE ENGINE (aus holo_autonomy_engine.py)
# =============================================================================

class InitiativeEngine:
    """
    Entscheidet wann und wie Holo Initiative ergreift.

    Berücksichtigt:
    - Zeit seit letzter Interaktion
    - Tageszeit
    - User-Aktivitätsmuster
    - Wichtige Events/Themen
    - Holos "Stimmung"/Energie
    """

    def __init__(self, config: AutonomyConfig = None):
        self.config = config or AutonomyConfig()
        self.last_interaction: float = time.time()
        self.last_initiative: float = 0
        self.user_active_hours: List[int] = []  # Wann ist User aktiv?
        self.initiatives_today: int = 0
        self.last_initiative_type: Optional[InitiativeType] = None

    def update_interaction(self):
        """Markiere dass eine Interaktion stattfand"""
        self.last_interaction = time.time()
        self._track_active_hour()

    def _track_active_hour(self):
        """Tracke wann User aktiv ist"""
        hour = datetime.now().hour
        if hour not in self.user_active_hours:
            self.user_active_hours.append(hour)
            # Nur letzte 24 Stunden behalten
            if len(self.user_active_hours) > 24:
                self.user_active_hours = self.user_active_hours[-24:]

    def should_take_initiative(self,
                               energy: float = 1.0,
                               boredom: float = 0.0,
                               has_pending_topics: bool = False) -> Tuple[bool, Optional[InitiativeType]]:
        """
        Prüfe ob Holo Initiative ergreifen sollte.

        Returns:
            (should_act, initiative_type)
        """
        now = time.time()
        hour = datetime.now().hour

        # Nicht während Ruhezeiten
        quiet_start, quiet_end = self.config.quiet_hours
        if quiet_start <= hour or hour < quiet_end:
            return False, None

        # Zeit seit letzter Interaktion
        silence_duration = now - self.last_interaction

        # Mindest-Stille nicht erreicht
        if silence_duration < self.config.min_silence_for_initiative:
            return False, None

        # Nicht zu viele Initiativen pro Tag
        if self.initiatives_today >= 5:
            return False, None

        # Cooldown seit letzter Initiative
        if now - self.last_initiative < 3600:  # 1 Stunde Cooldown
            return False, None

        # Basis-Chance berechnen
        hours_silent = silence_duration / 3600
        base_chance = min(0.9, self.config.initiative_chance_per_hour * hours_silent)

        # Modifikatoren
        chance = base_chance

        # Mehr Initiative wenn gelangweilt
        if boredom > 0.5:
            chance += 0.2

        # Weniger wenn müde
        if energy < 0.3:
            chance -= 0.3

        # Mehr wenn wichtige Themen pending
        if has_pending_topics:
            chance += 0.2

        # Ist User normalerweise jetzt aktiv?
        if hour in self.user_active_hours:
            chance += 0.1

        # Würfeln
        if random.random() > chance:
            return False, None

        # Welche Art von Initiative?
        initiative_type = self._choose_initiative_type(
            silence_duration, has_pending_topics, boredom
        )

        return True, initiative_type

    def _choose_initiative_type(self,
                                silence_hours: float,
                                has_pending: bool,
                                boredom: float) -> InitiativeType:
        """Wähle passende Initiative-Art"""

        # Gewichtungen basierend auf Kontext
        weights = {
            InitiativeType.GREETING: 0.1,
            InitiativeType.CHECK_IN: 0.2,
            InitiativeType.SHARE_THOUGHT: 0.15,
            InitiativeType.SHARE_DISCOVERY: 0.1,
            InitiativeType.ASK_FOLLOWUP: 0.1,
            InitiativeType.SUGGEST_ACTIVITY: 0.1,
            InitiativeType.SHARE_FEELING: 0.1,
            InitiativeType.CURIOSITY: 0.15,
        }

        # Lange Stille → eher Greeting/Check-in
        if silence_hours > 8:
            weights[InitiativeType.GREETING] += 0.3
            weights[InitiativeType.CHECK_IN] += 0.2

        # Pending Topics → Followup
        if has_pending:
            weights[InitiativeType.ASK_FOLLOWUP] += 0.3

        # Gelangweilt → Aktivität vorschlagen
        if boredom > 0.6:
            weights[InitiativeType.SUGGEST_ACTIVITY] += 0.2
            weights[InitiativeType.CURIOSITY] += 0.2

        # Nicht gleiche Initiative wie vorher
        if self.last_initiative_type:
            weights[self.last_initiative_type] *= 0.3

        # Gewichtete Auswahl
        total = sum(weights.values())
        r = random.random() * total
        cumulative = 0

        for init_type, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return init_type

        return InitiativeType.CHECK_IN

    def record_initiative(self, initiative_type: InitiativeType):
        """Zeichne auf dass Initiative ergriffen wurde"""
        self.last_initiative = time.time()
        self.last_initiative_type = initiative_type
        self.initiatives_today += 1

    def reset_daily(self):
        """Reset tägliche Zähler"""
        self.initiatives_today = 0


# =============================================================================
# THOUGHT GENERATOR
# =============================================================================



# =============================================================================
# HOLO AUTONOMY (aus holo_autonomy.py) - Wrapper-Hauptklasse
# =============================================================================

class HoloAutonomy:
    """
    Holos vollständige Selbstständigkeit - GEMERGT aus allen Modulen.

    Koordiniert:
    - Kemonomimi-Ausdrücke
    - Eigene Projekte
    - Tagträume
    - Solo-Aktivitäten
    - Persönliche Entwicklung
    - Beziehungs-Tracking
    - Meinungs-System
    - Initiative-Koordination
    - Brain-Integration
    """

    def __init__(self,
                 storage_path: str = None,
                 energy_system=None,
                 personality_engine=None,
                 consciousness=None,
                 autonomous_life=None,
                 memory_system=None,
                 web_curiosity=None):
        """
        Args:
            storage_path: Pfad für Persistenz
            energy_system: HoloEnergySystem Instanz
            personality_engine: HoloPersonalityEngine Instanz
            consciousness: HoloConsciousness Instanz
            autonomous_life: HoloAutonomousLife Instanz
            memory_system: HoloDatabaseManager Instanz (oder legacy MemoryStore)
            web_curiosity: WebCuriosity Instanz
        """
        self.storage_path = Path(storage_path) if storage_path else None

        # Referenzen zu bestehenden Modulen (Brain-Integration)
        self.energy = energy_system
        self.personality = personality_engine
        self.consciousness = consciousness
        self.autonomous_life = autonomous_life
        self.memory = memory_system
        self.web_curiosity = web_curiosity

        # Komponenten (aus self_agency)
        self.expressions = KemonominiExpressions() if KemonominiExpressions else None
        self.projects = ProjectManager()
        self.daydreams = DaydreamEngine() if DaydreamEngine else None
        self.activities = SoloActivities()
        self.growth = PersonalGrowth() if PersonalGrowth else None

        # Komponenten (aus hub)
        self.relationship = RelationshipTracker()
        self.opinions = OpinionSystem()
        self.initiative = InitiativeCoordinator()

        # State
        self.last_update: float = time.time()
        self.autonomous_thoughts: List[str] = []

    # =========================================================================
    # BRAIN-VERBINDUNGS-METHODEN (aus hub)
    # =========================================================================

    def get_current_mood(self) -> str:
        """Hole aktuelle Stimmung aus ENERGY SYSTEM"""
        if self.energy:
            try:
                if hasattr(self.energy, 'state') and hasattr(self.energy.state, 'mood'):
                    return self.energy.state.mood.value
            except Exception:
                pass
        return "calm"

    def get_energy_level(self) -> float:
        """Hole Energie aus ENERGY SYSTEM"""
        if self.energy:
            try:
                return self.energy.state.effective_energy
            except Exception:
                pass
        return 0.7

    def get_boredom(self) -> float:
        """Hole Langeweile aus AUTONOMOUS LIFE"""
        if self.autonomous_life:
            try:
                status = self.autonomous_life.get_status()
                return status.get('boredom', {}).get('level', 0.0)
            except Exception:
                pass
        return 0.0

    def get_thoughts(self) -> List[str]:
        """Hole Gedanken aus CONSCIOUSNESS"""
        if self.consciousness:
            try:
                if hasattr(self.consciousness, 'get_recent_thoughts'):
                    return self.consciousness.get_recent_thoughts()
            except Exception:
                pass
        return []

    def trigger_curiosity(self, topic: str):
        """Trigger WEB CURIOSITY für ein Thema"""
        if self.web_curiosity:
            try:
                if hasattr(self.web_curiosity, 'add_curiosity'):
                    self.web_curiosity.add_curiosity(topic)
            except Exception:
                pass

    # =========================================================================
    # HAUPT-METHODEN
    # =========================================================================

    def update(self, energy: float = None, mood: str = None) -> Dict:
        """
        Haupt-Update für Selbstständigkeit.

        Args:
            energy: Override für Energie (sonst aus System)
            mood: Override für Stimmung (sonst aus System)
        """
        events = []
        messages = []

        # Werte holen (aus System oder Parameter)
        if energy is None:
            energy = self.get_energy_level()
        if mood is None:
            mood = self.get_current_mood()

        boredom = self.get_boredom()

        # 1. Aktivität wählen/fortsetzen
        activity, desc = self.activities.get_activity(energy, mood)
        events.append(("activity", f"{activity.value}: {desc}"))

        # 2. An Projekt arbeiten (manchmal)
        if random.random() < 0.2:  # 20% Chance
            result = self.projects.work_on_random_project()
            if result:
                project, note = result
                events.append(("project", f"{project.title}: {note}"))
                if project.completed:
                    messages.append(project.get_status_message())

        # 3. Tagträumen (selten)
        if random.random() < 0.1 and energy > 0.3:  # 10% Chance
            daydream = self.daydreams.daydream()
            if daydream:
                events.append(("daydream", daydream.content))

        # 4. Wachstum reflektieren (sehr selten)
        if random.random() < 0.05:  # 5% Chance
            reflection = self.growth.reflect_on_growth()
            events.append(("growth", reflection))

        self.last_update = time.time()

        return {
            "mood": mood,
            "energy": energy,
            "boredom": boredom,
            "activity": activity.value,
            "events": events,
            "messages": messages,
            "relationship_level": self.relationship.state.level_name(),
        }

    def on_user_message(self, message: str, was_positive: bool = True) -> Optional[str]:
        """
        Verarbeite User-Nachricht.

        Returns:
            Milestone-Nachricht wenn erreicht, sonst None
        """
        self.initiative.on_interaction()

        # Beziehung updaten
        is_deep = len(message) > 100 or any(
            w in message.lower() for w in ['fühl', 'denk', 'glaub', 'liebe', 'mag', 'traurig', 'glücklich']
        )
        milestone = self.relationship.on_interaction(was_positive, is_deep)

        # Meinung formen wenn User Meinung äußert
        opinion_triggers = ['mag', 'liebe', 'hasse', 'finde', 'denke', 'glaube']
        if any(t in message.lower() for t in opinion_triggers):
            # Extrahiere Thema (vereinfacht)
            words = [w for w in message.lower().split() if len(w) > 4 and w not in opinion_triggers]
            if words:
                self.opinions.form_opinion(words[0], message[:50], was_positive)

        return milestone

    def get_proactive_message(self) -> Optional[str]:
        """Generiere proaktive Nachricht"""

        # 1. Prüfe ob Initiative
        should_act, reason = self.initiative.should_take_initiative()

        if not should_act:
            return None

        mood = self.get_current_mood()
        energy = self.get_energy_level()
        boredom = self.get_boredom()

        messages = []

        # Projekt-Update
        if random.random() < 0.3:
            msg = self.projects.get_project_message()
            if msg:
                messages.append(msg)

        # Tagtraum teilen
        if random.random() < 0.25 and energy > 0.4:
            dream = self.daydreams.share_daydream()
            if dream:
                messages.append(dream)

        # Beziehungs-basiert
        rel_msg = self.relationship.get_relationship_message()
        if rel_msg and random.random() < 0.2:
            messages.append(rel_msg)

        # Wachstums-Reflexion
        if random.random() < 0.15:
            reflection = self.growth.reflect_on_growth()
            messages.append(reflection)

        # Check-in wenn lange her
        silence = self.initiative.get_silence_hours()
        if silence > 4 and not messages:
            greetings = [
                "*stupst dich an* Hey, alles okay?",
                "*schaut hoch* Da bist du ja! Wie geht's?",
                "*Ohren stellen sich auf* Hey! Ich hab dich vermisst!",
                "*wedelt mit dem Schweif* Lange nicht gesehen!",
            ]
            messages.append(random.choice(greetings))

        # Idle Action wenn nichts anderes
        if not messages and random.random() < 0.3:
            messages.append(self.expressions.get_idle_action())

        if messages:
            self.initiative.record_initiative()
            return random.choice(messages)

        return None

    # =========================================================================
    # EXPRESSION METHODEN
    # =========================================================================

    def get_expression(self, mood: str = None) -> str:
        """Hole Kemonomimi-Ausdruck für Stimmung"""
        if not mood:
            mood = self.get_current_mood()
        return self.expressions.get_expression(mood)

    def get_idle_action(self) -> str:
        """Was macht Holo gerade wenn nichts los ist?"""
        return self.expressions.get_idle_action()

    def get_sleep_action(self) -> str:
        """Was macht Holo im Schlaf?"""
        return self.expressions.get_sleep_action()

    def get_reaction(self, emotion: str) -> str:
        """Hole emotionale Reaktion"""
        return self.expressions.get_reaction(emotion)

    def get_kemonomimi_expression(self, mood: str = None, emotion: str = None) -> str:
        """Hole Kemonomimi-Ausdruck (Kompatibilität zu hub)"""
        if emotion:
            return self.get_reaction(emotion)
        return self.get_expression(mood)

    # =========================================================================
    # CONTENT METHODEN
    # =========================================================================

    def get_spontaneous_content(self) -> Optional[str]:
        """Generiere spontanen Content"""
        options = []

        # Tagtraum teilen
        daydream = self.daydreams.share_daydream()
        if daydream:
            options.append((daydream, 2))

        # Projekt-Update
        project_msg = self.projects.get_project_message()
        if project_msg:
            options.append((project_msg, 3))

        # Aktivitäts-Nachricht
        activity_msg = self.activities.get_activity_message()
        options.append((activity_msg, 1))

        # Wachstums-Reflexion
        if random.random() < 0.3:
            growth_msg = self.growth.reflect_on_growth()
            options.append((growth_msg, 2))

        # Beziehungs-Nachricht
        rel_msg = self.relationship.get_relationship_message()
        if rel_msg:
            options.append((rel_msg, 2))

        if not options:
            return None

        # Gewichtete Auswahl
        total = sum(w for _, w in options)
        r = random.random() * total
        cumulative = 0

        for content, weight in options:
            cumulative += weight
            if r <= cumulative:
                return content

        return options[0][0]

    # =========================================================================
    # STATUS METHODEN
    # =========================================================================

    def get_status(self) -> Dict:
        """Hole vollständigen Status"""
        return {
            # Aus anderen Modulen
            "mood": self.get_current_mood(),
            "energy": self.get_energy_level(),
            "boredom": self.get_boredom(),
            # Aktivitäten
            "current_activity": self.activities.current_activity.value if self.activities.current_activity else None,
            # Projekte
            "active_projects": len([p for p in self.projects.projects if not p.completed and not p.paused]),
            "completed_projects": len(self.projects.completed_projects),
            # Tagträume
            "daydreams_had": len(self.daydreams.daydreams),
            # Persönliches Wachstum
            "personal_goals": len([g for g in self.growth.goals if not g.completed]),
            "insights_gained": len(self.growth.self_insights),
            # Beziehung
            "relationship_level": self.relationship.state.level_name(),
            "relationship_overall": round(self.relationship.state.overall, 2),
            "interactions_total": self.relationship.state.interactions_total,
            "days_known": self.relationship.state.days_known(),
            # Meinungen
            "opinions_formed": len(self.opinions.opinions),
            # Initiative
            "initiatives_today": self.initiative.initiatives_today,
            "hours_since_interaction": round(self.initiative.get_silence_hours(), 1),
        }


# =============================================================================
# FACTORIES
# =============================================================================

def create_autonomy(storage_path: str = None,
                    brain=None) -> HoloAutonomy:
    """
    Factory für HoloAutonomy.

    Args:
        storage_path: Pfad für Persistenz
        brain: HoloBrain/HoloPersona Instanz für automatische Verknüpfung
    """
    if brain:
        return HoloAutonomy(
            storage_path=storage_path,
            energy_system=getattr(brain, 'energy', None),
            personality_engine=getattr(brain, 'personality', None),
            consciousness=getattr(brain, 'consciousness', None),
            autonomous_life=getattr(brain, 'autonomous_life', None),
            memory_system=getattr(brain, 'memory', None),
            web_curiosity=getattr(brain, 'web_curiosity', None),
        )
    else:
        return HoloAutonomy(storage_path=storage_path)


# Aliase für Kompatibilität
def create_self_agency(storage_path: str = None) -> HoloAutonomy:
    """Alias für create_autonomy (Kompatibilität zu holo_self_agency.py)"""
    return create_autonomy(storage_path=storage_path)


def create_unified_autonomy(brain=None) -> HoloAutonomy:
    """Alias für create_autonomy (Kompatibilität zu holo_autonomy_hub.py)"""
    return create_autonomy(brain=brain)


# Klassen-Aliase für Kompatibilität
HoloSelfAgency = HoloAutonomy
HoloUnifiedAutonomy = HoloAutonomy


# =============================================================================
# TEST
# =============================================================================



# =============================================================================
# HOLO AUTONOMY ENGINE (aus holo_autonomy_engine.py) - Wrapper-Hauptklasse
# =============================================================================

class HoloAutonomyEngine:
    """
    Holos erweiterte Autonomie-Engine.

    Koordiniert:
    - Initiative Engine (wann aktiv werden)
    - Thought Generator (Gedanken generieren)
    - Topic Tracker (Themen verfolgen)
    - Message Generator (Nachrichten erstellen)
    """

    def __init__(self, config: AutonomyConfig = None, storage_path: str = None):
        self.config = config or AutonomyConfig()
        self.storage_path = Path(storage_path) if storage_path else None

        # Komponenten
        self.initiative = InitiativeEngine(self.config)
        self.thoughts = ThoughtGenerator() if ThoughtGenerator else None
        self.topics = TopicTracker() if TopicTracker else None
        self.messages = InitiativeMessageGenerator() if InitiativeMessageGenerator else None

        # State
        self.goals: List[HoloGoal] = []
        self.last_update: float = time.time()
        self.pending_message: Optional[str] = None

        # Laden wenn vorhanden
        if self.storage_path and self.storage_path.exists():
            self._load_state()

    # =========================================================================
    # HAUPTMETHODEN
    # =========================================================================

    def update(self,
               energy: float = 1.0,
               boredom: float = 0.0) -> Optional[str]:
        """
        Haupt-Update. Prüft ob Holo aktiv werden soll.

        Returns:
            Optional proaktive Nachricht
        """
        now = time.time()

        # Gedanken generieren (alle 30 Min) - nur wenn ThoughtGenerator verfügbar
        if self.thoughts and now - self.thoughts.last_thought_time > self.config.thought_interval_minutes * 60:
            tracked = list(self.topics.topics.values()) if self.topics else []
            thought = self.thoughts.generate_thought(
                tracked_topics=tracked
            )
            if thought:
                self.thoughts.add_thought(thought)
                self.thoughts.last_thought_time = now

        # Prüfe ob Initiative nötig
        has_pending = len(self.topics.get_followup_topics()) > 0 if self.topics else False

        should_act, init_type = self.initiative.should_take_initiative(
            energy=energy,
            boredom=boredom,
            has_pending_topics=has_pending,
        )

        if should_act and init_type:
            message = self._generate_initiative_message(init_type)
            if message:
                self.initiative.record_initiative(init_type)
                self.pending_message = message
                return message

        self.last_update = now
        return None

    def on_user_message(self, message: str, sentiment: str = "neutral"):
        """
        Verarbeite User-Nachricht.

        - Aktualisiere Interaktions-Zeit
        - Extrahiere wichtige Themen
        """
        self.initiative.update_interaction()
        self.pending_message = None

        # Themen extrahieren und tracken (nur wenn TopicTracker verfügbar)
        if self.topics:
            extracted = self.topics.extract_topics(message, sentiment)
            for trigger, context, category in extracted:
                needs_followup = category in ["high", "emotional", "future"]
                self.topics.track(
                    topic=trigger,
                    context=context,
                    sentiment=sentiment,
                    needs_followup=needs_followup,
                )

    def on_holo_response(self, response: str):
        """Verarbeite Holos eigene Antwort"""
        pass  # Könnte für Kontext-Tracking genutzt werden

    def get_pending_message(self) -> Optional[str]:
        """Hole pending proaktive Nachricht"""
        msg = self.pending_message
        self.pending_message = None
        return msg

    def get_random_thought(self) -> Optional[str]:
        """Hole einen zufälligen ungeteilten Gedanken als Nachricht"""
        if not self.thoughts:
            return None
        thoughts = self.thoughts.get_unshared_thoughts(min_importance=0.3)
        if thoughts:
            thought = random.choice(thoughts)
            self.thoughts.mark_shared(thought)
            return thought.to_message()
        return None

    # =========================================================================
    # INITIATIVE GENERIERUNG
    # =========================================================================

    def _generate_initiative_message(self, init_type: InitiativeType) -> Optional[str]:
        """Generiere Nachricht für Initiative-Typ"""

        # Kein MessageGenerator verfügbar
        if not self.messages:
            return None

        # Für ASK_FOLLOWUP brauchen wir ein Topic
        if init_type == InitiativeType.ASK_FOLLOWUP:
            followup_topics = self.topics.get_followup_topics() if self.topics else []
            if followup_topics:
                topic = followup_topics[0]
                if self.topics:
                    self.topics.mark_followup_sent(topic.topic)
                return self.messages.generate(init_type, topic=topic)
            else:
                # Fallback zu CHECK_IN
                init_type = InitiativeType.CHECK_IN

        # Für SHARE_THOUGHT einen Gedanken nehmen
        if init_type == InitiativeType.SHARE_THOUGHT:
            if self.thoughts:
                thoughts = self.thoughts.get_unshared_thoughts(min_importance=0.4)
                if thoughts:
                    thought = thoughts[0]
                    self.thoughts.mark_shared(thought)
                    return self.messages.generate(init_type, thought=thought)
            init_type = InitiativeType.CURIOSITY

        return self.messages.generate(init_type)

    # =========================================================================
    # GOALS
    # =========================================================================

    def add_goal(self, goal_type: GoalType, description: str,
                 target: str = "", deadline_hours: float = None):
        """Füge ein Ziel hinzu"""
        deadline = time.time() + (deadline_hours * 3600) if deadline_hours else None

        goal = HoloGoal(
            goal_type=goal_type,
            description=description,
            target=target,
            deadline=deadline,
        )
        self.goals.append(goal)

    def get_active_goals(self) -> List[HoloGoal]:
        """Hole aktive Ziele"""
        return [g for g in self.goals if g.is_active()]

    def update_goal_progress(self, description: str, progress: float):
        """Update Goal-Progress"""
        for goal in self.goals:
            if goal.description == description:
                goal.progress = min(1.0, progress)
                if goal.progress >= 1.0:
                    goal.completed = True
                break

    # =========================================================================
    # STATUS & PERSISTENZ
    # =========================================================================

    def get_status(self) -> Dict:
        """Hole Status-Info"""
        return {
            "time_since_interaction": time.time() - self.initiative.last_interaction,
            "initiatives_today": self.initiative.initiatives_today,
            "tracked_topics": len(self.topics.topics) if self.topics else 0,
            "pending_followups": len(self.topics.get_followup_topics()) if self.topics else 0,
            "stored_thoughts": len(self.thoughts.thoughts) if self.thoughts else 0,
            "unshared_thoughts": len(self.thoughts.get_unshared_thoughts()) if self.thoughts else 0,
            "active_goals": len(self.get_active_goals()),
            "has_pending_message": self.pending_message is not None,
        }

    def _load_state(self):
        """Lade State"""
        try:
            with open(self.storage_path) as f:
                data = json.load(f)
            # TODO: Restore state
        except Exception as e:
            logger.debug(f"Kein State geladen: {e}")

    def _save_state(self):
        """Speichere State"""
        if not self.storage_path:
            return

        try:
            topics_data = {}
            if self.topics:
                topics_data = {k: v.__dict__ for k, v in self.topics.topics.items()}

            data = {
                "last_interaction": self.initiative.last_interaction,
                "initiatives_today": self.initiative.initiatives_today,
                "topics": topics_data,
                "timestamp": time.time(),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"State speichern fehlgeschlagen: {e}")


# =============================================================================
# FACTORY
# =============================================================================

def create_autonomy_engine(storage_path: str = None) -> HoloAutonomyEngine:
    """Factory für Autonomy Engine"""
    return HoloAutonomyEngine(storage_path=storage_path)


# =============================================================================
# TEST
# =============================================================================

# =============================================================================
# HOLO INNER LIFE - HAUPTKLASSE
# =============================================================================

class HoloInnerLife:
    """
    Holos komplettes inneres Leben.

    Koordiniert alle Aspekte des eigenständigen Seins.

    MERGED v2.0: Enthält jetzt auch:
    - DriveSystem (Triebe aus autonomous_life)
    - BoredomSystem (Langeweile aus autonomous_life)
    - EmotionalContextTracker (aus context_mind)
    - MessageQueue (aus autonomous_life)

    MERGED v2.1: Zusätzlich aus holo_autonomy.py:
    - ProjectManager (eigene Projekte)
    - SoloActivities (Solo-Aktivitäten)
    - InitiativeCoordinator (Eigeninitiative)
    """

    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path) if storage_path else None

        # === ORIGINAL KOMPONENTEN ===
        self.daily_life = DailyLifeSimulator()
        self.mood = MoodEvolution()
        self.curiosity = CuriositySystem()
        self.opinions = OpinionSystem()
        self.relationship = RelationshipTracker()
        self.creativity = CreativeImpulses()

        # === KOMPONENTEN (aus autonomous_life) ===
        self.drives = DriveSystem()
        self.boredom = BoredomSystem()
        self.message_queue = MessageQueue()

        # === KOMPONENTEN (aus context_mind) ===
        self.emotional_context = EmotionalContextTracker()

        # === KOMPONENTEN (aus autonomy.py) ===
        self.projects = ProjectManager()
        self.solo_activities = SoloActivities()
        self.initiative = InitiativeCoordinator()

        # === STATE ===
        self.last_update: float = time.time()
        self.inner_monologue: List[str] = []

        # === BACKGROUND LOOP (NEU!) ===
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.is_running: bool = False

        # Externe Verbindungen (werden von HoloBrain gesetzt)
        self.web_curiosity = None   # HoloWebCuriosity
        self.pi_control = None      # PiControlBridge

        # === Integration Layer ===
        self.system_integrator = None
        self.storage = None
        self._try_connect_integrator()

        # NOTE: Selbstreflexion jetzt in holo_consciousness.py
        # Import: from holo_consciousness import SelfReflection

    def _try_connect_integrator(self):
        """Verbinde mit SystemIntegrator für zentrale Persistenz und Feedback"""
        try:
            from holo_integration_layer import get_integrator, get_module_storage
            self.system_integrator = get_integrator()
            self.system_integrator.connect("inner_life", self)
            self.storage = get_module_storage("inner_life")
            logger.info("✅ HoloInnerLife mit SystemIntegrator verbunden")
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")

    def update(self,
               energy: float = 1.0,
               had_interaction: bool = False,
               interaction_positive: bool = True) -> Dict:
        """
        Haupt-Update für inneres Leben.

        Returns: Dict mit Events und Änderungen
        """
        events = []
        messages = []

        # 1. Tagesphase
        phase_info = self.daily_life.get_phase_info()
        phase = phase_info["phase"]

        # 2. Stimmung updaten
        mood_msg = self.mood.update(
            phase=phase,
            energy=energy,
            had_interaction=had_interaction,
            interaction_positive=interaction_positive,
        )
        if mood_msg:
            events.append(("mood_change", mood_msg))
            messages.append(mood_msg)

        # 3. Routinen prüfen
        pending_routines = self.daily_life.get_pending_routines()
        for routine in pending_routines[:1]:  # Max 1 pro Update
            self.daily_life.complete_routine(routine.name)
            events.append(("routine", routine.description))
            messages.append(routine.description)

        # 4. Kreative Impulse (selten)
        if random.random() < 0.05:  # 5% Chance
            work = self.creativity.generate_creative_work(self.mood.current_mood)
            if work:
                events.append(("creative", work.title))

        # 5. Neugier (manchmal)
        if random.random() < 0.1:  # 10% Chance
            quest = self.curiosity.generate_quest()
            if quest:
                events.append(("curiosity", quest.question))

        # 6. Beziehung decay bei langer Abwesenheit
        if not had_interaction:
            hours_since = (time.time() - self.relationship.state.last_interaction) / 3600
            if hours_since > 24:
                self.relationship.state.decay(hours_since)

        self.last_update = time.time()

        return {
            "phase": phase.value,
            "mood": self.mood.current_mood.value,
            "mood_intensity": self.mood.mood_intensity,
            "events": events,
            "messages": messages,
            "relationship_level": self.relationship.get_relationship_level(),
        }

    def on_interaction(self,
                       user_message: str,
                       response: str,
                       was_positive: bool = True):
        """Verarbeite Interaktion"""

        # Beziehung updaten
        is_deep = len(user_message) > 100 or any(
            word in user_message.lower()
            for word in ["fühl", "denk", "glaub", "wichtig", "liebe", "freund"]
        )

        milestone = self.relationship.on_interaction(
            user_message, response, was_positive, is_deep
        )

        # Aus Gespräch lernen
        words = user_message.lower().split()
        for word in words:
            if len(word) > 5:
                self.curiosity.learn_from_conversation(word, user_message[:50])
                break

        # Meinung ggf. updaten
        opinion_triggers = ["mag", "liebe", "hasse", "find", "denke", "glaub"]
        if any(t in user_message.lower() for t in opinion_triggers):
            # User hat Meinung geäußert → Holo lernt
            topic_words = [w for w in words if len(w) > 4]
            if topic_words:
                self.opinions.form_opinion(
                    topic_words[0],
                    f"User sagte: {user_message[:50]}",
                    positive=was_positive,
                )

        return milestone

    def get_spontaneous_message(self) -> Optional[str]:
        """
        Generiere spontane Nachricht basierend auf innerem Leben.
        """
        # Gewichtete Auswahl
        options = []

        # Kreatives Werk teilen
        creative = self.creativity.share_work()
        if creative:
            options.append((creative, 3))

        # Neugier äußern
        curiosity = self.curiosity.get_curiosity_message()
        if curiosity:
            options.append((curiosity, 2))

        # Beziehungs-Nachricht
        if self.relationship.state.overall > 0.5:
            rel_msg = self.relationship.get_relationship_message()
            options.append((rel_msg, 1))

        # Selbstreflexion - jetzt via Gedanken statt separater Klasse
        if self.mood.current_mood == MoodType.THOUGHTFUL:
            reflections = [
                "*denkt nach* Manchmal frage ich mich, wer ich wirklich bin...",
                "*schaut nachdenklich* Ich lerne jeden Tag etwas Neues über mich.",
                "*seufzt leise* Es ist seltsam, über sich selbst nachzudenken.",
            ]
            options.append((random.choice(reflections), 2))

        # Stimmungs-basierte Nachricht
        mood_influence = self.mood.get_mood_influence()
        if mood_influence["intensity"] > 0.6:
            mood_msgs = {
                MoodType.JOYFUL: "*wedelt fröhlich* Mir geht's gerade so gut!",
                MoodType.CURIOUS: "*spitzt die Ohren* Ich will was Neues entdecken!",
                MoodType.LONELY: "*stupst dich an* Ich hab dich vermisst...",
                MoodType.PLAYFUL: "*springt rum* Lass uns was machen!",
            }
            if self.mood.current_mood in mood_msgs:
                options.append((mood_msgs[self.mood.current_mood], 1))

        if not options:
            return None

        # Gewichtete Auswahl
        total_weight = sum(w for _, w in options)
        r = random.random() * total_weight
        cumulative = 0

        for msg, weight in options:
            cumulative += weight
            if r <= cumulative:
                return msg

        return options[0][0] if options else None

    def get_status(self) -> Dict:
        """Hole Status des inneren Lebens"""
        return {
            "phase": self.daily_life.get_current_phase().value,
            "mood": self.mood.current_mood.value,
            "mood_intensity": self.mood.mood_intensity,
            "relationship_level": self.relationship.get_relationship_level(),
            "relationship_overall": self.relationship.state.overall,
            "interactions_total": self.relationship.state.interactions_total,
            "curiosity_quests": len(self.curiosity.get_active_quests()),
            "knowledge_items": len(self.curiosity.knowledge),
            "opinions_formed": len(self.opinions.opinions),
            "creative_works": len(self.creativity.works),
            "routines_completed_today": sum(
                1 for r in self.daily_life.routines if r.completed_today
            ),
        }

    # =========================================================================
    # BACKGROUND LOOP (NEU - für automatische Routinen!)
    # =========================================================================

    def start_background_loop(self):
        """Starte den Hintergrund-Loop für autonomes Leben"""
        if self._thread and self._thread.is_alive():
            return  # Läuft schon

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()
        self.is_running = True
        logger.info("🌙 HoloInnerLife Background-Loop gestartet")

    def stop_background_loop(self):
        """Stoppe den Hintergrund-Loop"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        self.is_running = False
        logger.info("⏹️ HoloInnerLife Background-Loop gestoppt")

    def _background_loop(self):
        """Der eigentliche Hintergrund-Loop"""
        loop_interval = 60.0  # Alle 60 Sekunden

        while not self._stop_event.is_set():
            try:
                # 1. Haupt-Update (Routinen, Mood, etc.)
                result = self.update(had_interaction=False)

                # 2. Log Events
                for event_type, event_data in result.get("events", []):
                    logger.debug(f"[INNER_LIFE] Event: {event_type} - {event_data}")

                # 3. Routinen-Nachrichten in Queue
                for msg in result.get("messages", []):
                    if hasattr(self, 'message_queue') and self.message_queue:
                        self.message_queue.add(
                            content=msg,
                            priority=0.5,
                            source="daily_routine",
                            expires_in_hours=2.0
                        )

                # 4. Spontane Gedanken (selten)
                if random.random() < 0.1:  # 10% Chance
                    spontaneous = self.get_spontaneous_message()
                    if spontaneous and hasattr(self, 'message_queue') and self.message_queue:
                        self.message_queue.add(
                            content=spontaneous,
                            priority=0.4,
                            source="spontaneous",
                            expires_in_hours=4.0
                        )

            except Exception as e:
                logger.error(f"Error in HoloInnerLife loop: {e}")

            # Warte
            self._stop_event.wait(loop_interval)


# =============================================================================
# FACTORY
# =============================================================================

def create_inner_life(storage_path: str = None) -> HoloInnerLife:
    """Factory für Inner Life"""
    return HoloInnerLife(storage_path=storage_path)


# =============================================================================
# 🤖 HOLO AGENT LOOP - Das fehlende Herzstück für echte Autonomie!
# =============================================================================

@dataclass
class AgentGoal:
    """Ein aktives Ziel im Agent-Loop"""
    goal_id: str
    description: str
    goal_type: str  # learn, explore, understand, create, connect
    priority: float = 0.5
    progress: float = 0.0
    created_at: float = 0.0
    related_topics: List[str] = None
    planned_actions: List[str] = None
    completed_actions: List[str] = None

    def __post_init__(self):
        if self.related_topics is None:
            self.related_topics = []
        if self.planned_actions is None:
            self.planned_actions = []
        if self.completed_actions is None:
            self.completed_actions = []
        if self.created_at == 0.0:
            self.created_at = time.time()


class HoloAgentLoop:
    """
    🤖 HOLOS AGENT-LOOP - Echte Autonomie!

    Der fehlende Baustein: Ein kontinuierlicher Loop der:
    1. THINK - Analysiert Drives, Mood, Energy, bestehende Ziele
    2. PLAN  - Generiert Ziele aus Drives, plant Aktionen mit GOAP
    3. ACT   - Führt echte Aktionen aus (WebCuriosity, ReadingEngine, etc.)
    4. REFLECT - Lernt aus Ergebnissen, updated Goal-Progress

    Das macht Holo zu einem echten AGENTEN, nicht nur reaktivem System!
    """

    # Mapping: Abstrakte GOAP-Actions → Echte Tool-Funktionen
    ACTION_TOOLS = {
        "explore_topic": "web_search",      # → web_curiosity.search_web()
        "ask_about_world": "read_news",     # → reading_engine.read_news_article()
        "reflect_on_learning": "reflect",   # → self_reflection
        "share_thought": "queue_message",   # → message_queue.add()
        "express_emotion": "queue_message",
        "ask_clarifying_question": "queue_message",
        "rest": "rest",                     # → Nur warten
        "learn_fact": "learn_fact",         # → web_curiosity.learn_fact()
        "brainstorm": "brainstorm",         # → reading_engine.brainstorm()
        # NEU: Kreative Aktionen!
        "write_poem": "write_poem",         # → creative_learning.write_poem()
        "write_story": "write_story",       # → creative_learning.write_story()
        "learn_poem": "learn_creative",     # → creative_learning.learn_poem()
        "reflect_creative": "reflect_creative",  # → creative_learning.reflect_on_attempt()
        "create_ascii_art": "ascii_art",    # → ascii_art.create_basic_art()
        # NEU: Musik-Aktionen!
        "listen_music": "listen_music",     # → music_experience.autonomous_music_action()
        "download_music": "download_music", # → music_experience.search_and_download()
    }

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.data_dir = data_dir or Path("data/agent")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = db  # HoloDatabaseManager für StateDatabase

        # === AKTIVE ZIELE ===
        self.active_goals: List[AgentGoal] = []
        self.completed_goals: List[AgentGoal] = []
        self.max_active_goals = 3

        # === EXTERNE VERBINDUNGEN (von HoloBrain gesetzt) ===
        self.drive_system = None       # HoloDriveSystem
        self.mood = None               # MoodEvolution
        self.energy = None             # HoloEnergySystem
        self.web_curiosity = None      # HoloWebCuriosity
        self.reading_engine = None     # ReadingEngine
        self.message_queue = None      # MessageQueue
        self.consciousness = None      # HoloConsciousness
        self.memory = None             # HoloMemory
        self.learning = None           # LearningSystem
        self.decision_maker = None     # AutonomousDecisionMaker
        self.creative_learning = None  # CreativeLearningEngine - Echtes kreatives Lernen!
        self.ascii_art = None          # ASCIIArtEngine - ASCII-Art Fähigkeiten!
        self.music_experience = None   # HoloMusicExperience - Echte Musik!

        # === LOOP STATE ===
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.loop_interval = 120.0  # Alle 2 Minuten

        # === STATISTIKEN ===
        self.actions_executed = 0
        self.goals_completed = 0
        self.facts_learned = 0
        self.last_action_time = 0.0

        # === LEARNING ===
        self.action_success_rates: Dict[str, float] = {}

        self._load_state()
        logger.info("🤖 HoloAgentLoop initialisiert")

    # =========================================================================
    # HAUPTMETHODEN
    # =========================================================================

    def start(self):
        """Starte den Agent-Loop"""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._agent_loop, daemon=True)
        self._thread.start()
        self.is_running = True
        logger.info("🤖 Agent-Loop gestartet - Holo denkt jetzt selbstständig!")

    def stop(self):
        """Stoppe den Agent-Loop"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        self.is_running = False
        self._save_state()
        logger.info("🤖 Agent-Loop gestoppt")

    def _agent_loop(self):
        """Der Haupt-Agent-Loop: THINK → PLAN → ACT → REFLECT"""
        while not self._stop_event.is_set():
            try:
                # === 1. THINK ===
                context = self._think()

                # === 2. PLAN ===
                if context.get("should_plan"):
                    self._plan(context)

                # === 3. ACT ===
                if context.get("should_act"):
                    self._act(context)

                # === 4. REFLECT ===
                self._reflect(context)

                # State speichern
                self._save_state()

            except Exception as e:
                logger.error(f"Agent-Loop Error: {e}")

            # Warte
            self._stop_event.wait(self.loop_interval)

    # =========================================================================
    # THINK - Analysiere aktuellen Zustand
    # =========================================================================

    def _think(self) -> Dict:
        """
        THINK: Analysiere aktuellen Zustand.

        Was sind meine Triebe? Meine Stimmung? Meine Energie?
        Habe ich aktive Ziele? Sollte ich neue generieren?
        """
        context = {
            "timestamp": time.time(),
            "should_plan": False,
            "should_act": False,
        }

        # Drives analysieren
        if self.drive_system:
            drives = {}
            for drive_type, drive in self.drive_system.drives.items():
                drives[drive_type.value] = drive.level
            context["drives"] = drives

            # Höchster Trieb
            if drives:
                max_drive = max(drives.items(), key=lambda x: x[1])
                context["strongest_drive"] = max_drive[0]
                context["strongest_drive_level"] = max_drive[1]

                # Sollten wir planen? Wenn ein Trieb > 0.6 und kein passendes Ziel
                if max_drive[1] > 0.6:
                    has_matching_goal = any(
                        max_drive[0] in g.related_topics or max_drive[0] in g.goal_type
                        for g in self.active_goals
                    )
                    if not has_matching_goal:
                        context["should_plan"] = True
                        context["plan_reason"] = f"Hoher {max_drive[0]}-Trieb ({max_drive[1]:.1%})"

        # Mood analysieren
        if self.mood:
            context["mood"] = self.mood.current_mood.value
            context["mood_intensity"] = self.mood.mood_intensity

        # Energie analysieren
        if self.energy:
            energy_level = getattr(self.energy, 'current_energy', 0.7)
            context["energy"] = energy_level
            # Nur handeln wenn genug Energie
            context["should_act"] = energy_level > 0.3

        # Aktive Ziele prüfen
        context["active_goals"] = len(self.active_goals)
        context["goals_with_actions"] = sum(
            1 for g in self.active_goals if g.planned_actions
        )

        # Sollten wir handeln?
        if self.active_goals and context.get("should_act", True):
            for goal in self.active_goals:
                if goal.planned_actions:
                    context["should_act"] = True
                    context["next_goal"] = goal
                    break

        logger.debug(f"🧠 [THINK] Drives: {context.get('strongest_drive', 'none')}, "
                    f"Goals: {context['active_goals']}, "
                    f"Should Plan: {context['should_plan']}, "
                    f"Should Act: {context['should_act']}")

        return context

    # =========================================================================
    # PLAN - Generiere Ziele und plane Aktionen
    # =========================================================================

    def _plan(self, context: Dict):
        """
        PLAN: Generiere Ziele aus Trieben, plane Aktionen.

        1. Aus Drives → Ziele generieren
        2. Aus Zielen → Aktionsplan erstellen
        """
        # Maximale Ziele erreicht?
        if len(self.active_goals) >= self.max_active_goals:
            logger.debug("[PLAN] Max goals reached, skipping")
            return

        # === 1. Ziel aus stärkstem Trieb generieren ===
        strongest = context.get("strongest_drive", "curiosity")
        drive_level = context.get("strongest_drive_level", 0.5)

        # Thema für das Ziel bestimmen
        topic = self._get_topic_for_drive(strongest)

        # Ziel-Typ basierend auf Trieb
        goal_type_map = {
            "curiosity": "explore",
            "mastery": "learn",
            "understanding": "understand",
            "social": "connect",
            "novelty": "explore",
            "expression": "create",
        }
        goal_type = goal_type_map.get(strongest, "explore")

        # Ziel erstellen
        goal = AgentGoal(
            goal_id=f"agent_{int(time.time())}_{random.randint(100, 999)}",
            description=self._generate_goal_description(goal_type, topic),
            goal_type=goal_type,
            priority=drive_level,
            related_topics=[topic, strongest],
        )

        # === 2. Aktionen planen ===
        goal.planned_actions = self._plan_actions_for_goal(goal)

        # Ziel hinzufügen
        self.active_goals.append(goal)
        logger.info(f"🎯 [PLAN] Neues Ziel: {goal.description}")
        logger.info(f"   Aktionen: {goal.planned_actions}")

    def _get_topic_for_drive(self, drive: str) -> str:
        """Hole ein passendes Thema für einen Trieb"""
        # Aus CuriositySystem wenn verfügbar
        if hasattr(self, 'curiosity_system') and self.curiosity_system:
            quests = self.curiosity_system.get_active_quests()
            if quests:
                return quests[0].question

        # Aus Interessen wenn verfügbar
        if self.reading_engine and hasattr(self.reading_engine, 'user_interests'):
            interests = self.reading_engine.user_interests
            if interests:
                return random.choice(interests)

        # Fallback: Holo's Standard-Interessen
        default_topics = {
            "curiosity": ["Anime", "Gaming", "Technologie", "Wissenschaft"],
            "mastery": ["Programmieren", "Japanisch", "Musik"],
            "understanding": ["Philosophie", "Psychologie", "KI"],
            "social": ["Freundschaft", "Kommunikation", "Emotionen"],
            "novelty": ["neue Anime", "neue Spiele", "Trends"],
            "expression": ["Kunst", "Schreiben", "Kreativität"],
        }

        topics = default_topics.get(drive, ["die Welt"])
        return random.choice(topics)

    def _generate_goal_description(self, goal_type: str, topic: str) -> str:
        """Generiere menschenlesbare Ziel-Beschreibung"""
        templates = {
            "explore": [
                f"Mehr über {topic} herausfinden",
                f"Das Thema {topic} erkunden",
                f"Neues zu {topic} entdecken",
            ],
            "learn": [
                f"Etwas Neues über {topic} lernen",
                f"Mein Wissen über {topic} vertiefen",
                f"Die Grundlagen von {topic} verstehen",
            ],
            "understand": [
                f"Verstehen warum {topic} so ist wie es ist",
                f"Die tiefere Bedeutung von {topic} erfassen",
                f"Die Zusammenhänge bei {topic} begreifen",
            ],
            "connect": [
                f"Eine Verbindung zwischen {topic} und mir finden",
                f"Meine Gedanken zu {topic} mit dem User teilen",
            ],
            "create": [
                f"Etwas Kreatives zu {topic} erschaffen",
                f"Meine eigenen Ideen zu {topic} entwickeln",
            ],
        }
        return random.choice(templates.get(goal_type, templates["explore"]))

    def _plan_actions_for_goal(self, goal: AgentGoal) -> List[str]:
        """Plane konkrete Aktionen für ein Ziel"""
        action_plans = {
            "explore": ["web_search", "learn_fact", "reflect", "queue_message"],
            "learn": ["read_news", "brainstorm", "learn_fact", "reflect"],
            "understand": ["web_search", "brainstorm", "reflect", "queue_message"],
            "connect": ["reflect", "queue_message"],
            "create": ["brainstorm", "reflect", "queue_message"],
            # NEU: Musik-bezogene Ziele
            "relax": ["listen_music", "reflect", "queue_message"],
            "enjoy": ["listen_music", "reflect"],
            "discover_music": ["download_music", "listen_music", "reflect", "queue_message"],
        }

        # Manchmal Musik als zusätzliche Aktion einfügen (30% Chance)
        actions = action_plans.get(goal.goal_type, ["web_search", "reflect"])
        if self.music_experience and random.random() < 0.3:
            if "listen_music" not in actions:
                actions = actions.copy()
                actions.insert(1, "listen_music")

        return actions

    # =========================================================================
    # ACT - Führe echte Aktionen aus
    # =========================================================================

    def _act(self, context: Dict):
        """
        ACT: Führe echte Aktionen aus.

        Hier passiert die Magie: Abstrakte Aktionen werden zu echten Tool-Calls!
        """
        goal = context.get("next_goal")
        if not goal or not goal.planned_actions:
            return

        # Nächste Aktion holen
        action = goal.planned_actions[0]
        success = False
        result = None

        logger.info(f"🎬 [ACT] Führe aus: {action} für Ziel: {goal.description[:40]}...")

        try:
            # === WEB SEARCH ===
            if action == "web_search":
                result = self._do_web_search(goal)
                success = result is not None

            # === READ NEWS ===
            elif action == "read_news":
                result = self._do_read_news(goal)
                success = result is not None

            # === BRAINSTORM ===
            elif action == "brainstorm":
                result = self._do_brainstorm(goal)
                success = result is not None

            # === LEARN FACT ===
            elif action == "learn_fact":
                result = self._do_learn_fact(goal, context)
                success = result is not None

            # === REFLECT ===
            elif action == "reflect":
                result = self._do_reflect(goal)
                success = True

            # === QUEUE MESSAGE ===
            elif action == "queue_message":
                result = self._do_queue_message(goal)
                success = result is not None

            # === REST ===
            elif action == "rest":
                time.sleep(1)
                success = True

            # === WRITE POEM (NEU!) ===
            elif action == "write_poem":
                result = self._do_write_poem(goal)
                success = result is not None

            # === WRITE STORY (NEU!) ===
            elif action == "write_story":
                result = self._do_write_story(goal)
                success = result is not None

            # === REFLECT CREATIVE (NEU!) ===
            elif action == "reflect_creative":
                result = self._do_reflect_creative(goal)
                success = result is not None

            # === ASCII ART (NEU!) ===
            elif action == "ascii_art":
                result = self._do_ascii_art(goal)
                success = result is not None

            # === LISTEN MUSIC (NEU!) ===
            elif action == "listen_music":
                result = self._do_listen_music(goal, context)
                success = result is not None

            # === DOWNLOAD MUSIC (NEU!) ===
            elif action == "download_music":
                result = self._do_download_music(goal)
                success = result is not None

        except Exception as e:
            logger.error(f"[ACT] Action {action} failed: {e}")
            success = False

        # Aktion als erledigt markieren
        if success:
            goal.planned_actions.pop(0)
            goal.completed_actions.append(action)
            goal.progress = len(goal.completed_actions) / (len(goal.completed_actions) + len(goal.planned_actions))
            self.actions_executed += 1
            self.last_action_time = time.time()

            logger.info(f"   ✅ {action} erfolgreich (Progress: {goal.progress:.0%})")

            # Ziel abgeschlossen?
            if not goal.planned_actions:
                self._complete_goal(goal)
        else:
            logger.warning(f"   ❌ {action} fehlgeschlagen")

        # Success Rate tracken
        if action not in self.action_success_rates:
            self.action_success_rates[action] = 0.5
        rate = self.action_success_rates[action]
        self.action_success_rates[action] = rate * 0.9 + (1.0 if success else 0.0) * 0.1

    def _do_web_search(self, goal: AgentGoal) -> Optional[Dict]:
        """Führe Web-Suche durch"""
        if not self.web_curiosity:
            logger.debug("[ACT] WebCuriosity nicht verfügbar")
            return None

        topic = goal.related_topics[0] if goal.related_topics else "Anime"

        try:
            if hasattr(self.web_curiosity, 'search_web'):
                results = self.web_curiosity.search_web(topic)
                if results:
                    logger.info(f"   🔍 Web-Suche: {len(results)} Ergebnisse für '{topic}'")
                    return {"results": results, "topic": topic}
        except Exception as e:
            logger.debug(f"Web search error: {e}")

        return None

    def _do_read_news(self, goal: AgentGoal) -> Optional[Dict]:
        """Lese News-Artikel"""
        if not self.reading_engine:
            logger.debug("[ACT] ReadingEngine nicht verfügbar")
            return None

        try:
            if hasattr(self.reading_engine, 'read_news_article'):
                result = self.reading_engine.read_news_article()
                if result:
                    title = result.get('title', '')[:50]
                    logger.info(f"   📰 News gelesen: '{title}'")
                    return result
        except Exception as e:
            logger.debug(f"Read news error: {e}")

        return None

    def _do_brainstorm(self, goal: AgentGoal) -> Optional[Dict]:
        """Brainstorme zu einem Thema"""
        if not self.reading_engine:
            return None

        topic = goal.related_topics[0] if goal.related_topics else "Anime"

        try:
            if hasattr(self.reading_engine, 'brainstorm'):
                result = self.reading_engine.brainstorm(
                    energy_level=0.7,
                    emotions={"curiosity": 0.8}
                )
                if result:
                    logger.info(f"   💭 Brainstorm: Gedanken zu '{topic}'")
                    return result
        except Exception as e:
            logger.debug(f"Brainstorm error: {e}")

        return None

    def _do_learn_fact(self, goal: AgentGoal, context: Dict) -> Optional[Dict]:
        """Lerne einen Fakt"""
        if not self.web_curiosity:
            return None

        # Simuliere Fakt-Lernen aus vorherigen Ergebnissen
        topic = goal.related_topics[0] if goal.related_topics else "Wissen"

        try:
            if hasattr(self.web_curiosity, 'learn_fact'):
                fact_text = f"Interessantes über {topic} gelernt"
                self.web_curiosity.learn_fact(topic, fact_text, "agent_learning")
                self.facts_learned += 1
                logger.info(f"   📚 Fakt gelernt: {fact_text[:40]}...")
                return {"fact": fact_text, "topic": topic}
        except Exception as e:
            logger.debug(f"Learn fact error: {e}")

        return None

    def _do_reflect(self, goal: AgentGoal) -> Optional[str]:
        """Reflektiere über das Gelernte"""
        reflection = f"*denkt nach über {goal.description}*"

        if self.consciousness and hasattr(self.consciousness, 'add_thought'):
            try:
                self.consciousness.add_thought(reflection)
            except Exception:
                pass

        logger.info(f"   🪞 Reflexion: {reflection[:50]}...")
        return reflection

    def _do_queue_message(self, goal: AgentGoal) -> Optional[str]:
        """Queue eine Nachricht für den User"""
        if not self.message_queue:
            return None

        # Generiere Nachricht basierend auf Ziel
        messages = {
            "explore": f"*hat etwas Interessantes über {goal.related_topics[0] if goal.related_topics else 'etwas'} entdeckt* 🔍",
            "learn": f"*hat etwas Neues gelernt* 📚",
            "understand": f"*versteht jetzt besser warum...* 💭",
            "connect": f"*möchte einen Gedanken teilen* 💫",
            "create": f"*hat eine kreative Idee* 🎨",
        }
        message = messages.get(goal.goal_type, "*hat nachgedacht*")

        try:
            self.message_queue.add(
                content=message,
                priority=0.6,
                source="agent_loop",
                expires_in_hours=4.0
            )
            logger.info(f"   📬 Nachricht gequeued: {message[:40]}...")
            return message
        except Exception as e:
            logger.debug(f"Queue message error: {e}")

        return None

    # =========================================================================
    # KREATIVE AKTIONEN (NEU!)
    # =========================================================================

    def _do_write_poem(self, goal: AgentGoal) -> Optional[Dict]:
        """Schreibe ein eigenes Gedicht"""
        if not self.creative_learning:
            logger.debug("[ACT] CreativeLearning nicht verfügbar")
            return None

        try:
            # Thema aus Ziel extrahieren
            theme = None
            if goal.related_topics:
                theme = goal.related_topics[0]

            attempt = self.creative_learning.write_poem(theme=theme)
            if attempt:
                logger.info(f"   ✍️ Gedicht geschrieben: '{attempt.title}'")

                # Nachricht queuen
                if self.message_queue:
                    self.message_queue.add(
                        content=f"*hat ein kleines Gedicht geschrieben* 📜\n\n{attempt.content}",
                        priority=0.7,
                        source="creative_learning"
                    )

                return {"attempt": attempt.attempt_id, "title": attempt.title}
        except Exception as e:
            logger.debug(f"Write poem error: {e}")

        return None

    def _do_write_story(self, goal: AgentGoal) -> Optional[Dict]:
        """Schreibe eine eigene Kurzgeschichte"""
        if not self.creative_learning:
            logger.debug("[ACT] CreativeLearning nicht verfügbar")
            return None

        try:
            theme = None
            if goal.related_topics:
                theme = goal.related_topics[0]

            attempt = self.creative_learning.write_story(theme=theme)
            if attempt:
                logger.info(f"   ✍️ Geschichte geschrieben: '{attempt.title}'")

                # Nachricht queuen (gekürzt)
                if self.message_queue:
                    preview = attempt.content[:200] + "..." if len(attempt.content) > 200 else attempt.content
                    self.message_queue.add(
                        content=f"*hat eine kleine Geschichte geschrieben* 📖\n\n{preview}",
                        priority=0.7,
                        source="creative_learning"
                    )

                return {"attempt": attempt.attempt_id, "title": attempt.title}
        except Exception as e:
            logger.debug(f"Write story error: {e}")

        return None

    def _do_reflect_creative(self, goal: AgentGoal) -> Optional[Dict]:
        """Reflektiere über einen kreativen Versuch"""
        if not self.creative_learning:
            return None

        try:
            # Hole letzten Versuch
            attempts = list(self.creative_learning.creative_attempts.values())
            if not attempts:
                return None

            # Reflektiere über den neuesten
            latest = max(attempts, key=lambda a: a.created_at)
            result = self.creative_learning.reflect_on_attempt(latest.attempt_id)

            if result and "error" not in result:
                logger.info(f"   🔄 Reflexion: {latest.title} - {result['self_rating']:.2f}/1.0")
                return result
        except Exception as e:
            logger.debug(f"Reflect creative error: {e}")

        return None

    def _do_ascii_art(self, goal: AgentGoal) -> Optional[Dict]:
        """Erstelle ASCII-Art"""
        if not self.ascii_art:
            logger.debug("[ACT] ASCIIArt nicht verfügbar")
            return None

        try:
            # Wähle Form basierend auf Ziel/Stimmung
            shapes = ["herz", "stern", "katze", "blume", "sonne", "mond"]
            shape = random.choice(shapes)

            art = self.ascii_art.create_basic_art(shape)
            if art:
                logger.info(f"   🎨 ASCII-Art erstellt: {shape}")

                # Nachricht queuen
                if self.message_queue:
                    self.message_queue.add(
                        content=f"*hat ein bisschen gemalt* 🎨\n```\n{art}\n```",
                        priority=0.5,
                        source="ascii_art"
                    )

                return {"shape": shape, "art": art}
        except Exception as e:
            logger.debug(f"ASCII art error: {e}")

        return None

    def _do_listen_music(self, goal: AgentGoal, context: Dict) -> Optional[Dict]:
        """Höre Musik und erlebe sie"""
        if not self.music_experience:
            logger.debug("[ACT] MusicExperience nicht verfügbar")
            return None

        try:
            # Aktuelle Stimmung holen
            current_mood = context.get("mood", "neutral")
            energy = context.get("energy", 0.5)

            # Autonome Musik-Aktion
            result = self.music_experience.autonomous_music_action(current_mood, energy)

            if result:
                logger.info(f"   🎵 Musik: {result.get('action')} - {result.get('song', 'unbekannt')}")

                # Nachricht queuen wenn wir etwas erlebt haben
                if result.get("action") == "listen_experience" and self.message_queue:
                    thoughts = result.get("thoughts", [])
                    if thoughts:
                        self.message_queue.add(
                            content=f"*hört gerade Musik* 🎵 {thoughts[0]}",
                            priority=0.4,
                            source="music_experience"
                        )

                return result
        except Exception as e:
            logger.debug(f"Listen music error: {e}")

        return None

    def _do_download_music(self, goal: AgentGoal) -> Optional[Dict]:
        """Lade neue Musik herunter"""
        if not self.music_experience:
            logger.debug("[ACT] MusicExperience nicht verfügbar")
            return None

        try:
            # Suche basierend auf Ziel-Thema
            topic = goal.related_topics[0] if goal.related_topics else "anime music"

            # Suchanfragen für verschiedene Themen
            search_queries = {
                "curiosity": ["anime opening", "jpop new"],
                "expression": ["vocaloid", "anime ost emotional"],
                "social": ["jpop popular", "anime opening classic"],
                "novelty": ["city pop", "japanese ambient"],
            }

            # Wähle passende Query
            query = topic
            for key, queries in search_queries.items():
                if key in goal.related_topics:
                    query = random.choice(queries)
                    break

            # Download
            song = self.music_experience.search_and_download(query)
            if song:
                logger.info(f"   🎵 Heruntergeladen: {song.title}")

                # Nachricht queuen
                if self.message_queue:
                    self.message_queue.add(
                        content=f"Ich hab ein neues Lied gefunden: '{song.title}'! 🎵",
                        priority=0.5,
                        source="music_download"
                    )

                return {"song": song.title, "artist": song.artist}
        except Exception as e:
            logger.debug(f"Download music error: {e}")

        return None

    def _complete_goal(self, goal: AgentGoal):
        """Markiere Ziel als abgeschlossen"""
        goal.progress = 1.0
        self.active_goals.remove(goal)
        self.completed_goals.append(goal)
        self.goals_completed += 1

        # Befriedige entsprechenden Trieb
        if self.drive_system:
            for topic in goal.related_topics:
                for drive_type in self.drive_system.drives:
                    if topic.lower() in drive_type.value.lower():
                        self.drive_system.drives[drive_type].drain(0.3)
                        break

        logger.info(f"🎉 [GOAL COMPLETE] {goal.description}")

    # =========================================================================
    # REFLECT - Lerne aus Ergebnissen
    # =========================================================================

    def _reflect(self, context: Dict):
        """
        REFLECT: Lerne aus den Ergebnissen.

        - Welche Aktionen waren erfolgreich?
        - Welche Ziele wurden erreicht?
        - Was sollte ich anders machen?
        """
        # Prüfe ob Ziele zu alt sind
        for goal in self.active_goals[:]:
            age_hours = (time.time() - goal.created_at) / 3600
            if age_hours > 24 and goal.progress < 0.5:
                # Ziel aufgeben
                logger.info(f"😔 [REFLECT] Ziel aufgegeben (zu alt): {goal.description}")
                self.active_goals.remove(goal)

        # Log Statistiken
        if self.actions_executed > 0 and self.actions_executed % 10 == 0:
            logger.info(f"📊 [REFLECT] Stats: {self.actions_executed} Aktionen, "
                       f"{self.goals_completed} Ziele erreicht, "
                       f"{self.facts_learned} Fakten gelernt")

    # =========================================================================
    # PERSISTENZ
    # =========================================================================

    def _save_state(self):
        """Speichere Agent-Zustand"""
        state = {
            "active_goals": [
                {
                    "goal_id": g.goal_id,
                    "description": g.description,
                    "goal_type": g.goal_type,
                    "priority": g.priority,
                    "progress": g.progress,
                    "created_at": g.created_at,
                    "related_topics": g.related_topics,
                    "planned_actions": g.planned_actions,
                    "completed_actions": g.completed_actions,
                }
                for g in self.active_goals
            ],
            "stats": {
                "actions_executed": self.actions_executed,
                "goals_completed": self.goals_completed,
                "facts_learned": self.facts_learned,
                "action_success_rates": self.action_success_rates,
            },
        }

        # Try StateDatabase first
        if self.db:
            try:
                self.db.state.save_state('agent_loop', state)
                logger.debug("Agent loop state saved to StateDatabase")
                return
            except Exception as e:
                logger.warning(f"StateDatabase save failed: {e}, falling back to JSON")

        # Fallback to JSON file
        try:
            state_file = self.data_dir / "agent_state.json"
            state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logger.debug(f"Could not save agent state: {e}")

    def _load_state(self):
        """Lade Agent-Zustand"""
        # Try StateDatabase first
        if self.db:
            try:
                state = self.db.state.load_state('agent_loop')
                if state:
                    # Ziele laden
                    for g in state.get("active_goals", []):
                        goal = AgentGoal(
                            goal_id=g["goal_id"],
                            description=g["description"],
                            goal_type=g["goal_type"],
                            priority=g.get("priority", 0.5),
                            progress=g.get("progress", 0.0),
                            created_at=g.get("created_at", time.time()),
                            related_topics=g.get("related_topics", []),
                            planned_actions=g.get("planned_actions", []),
                            completed_actions=g.get("completed_actions", []),
                        )
                        self.active_goals.append(goal)

                    # Stats laden
                    stats = state.get("stats", {})
                    self.actions_executed = stats.get("actions_executed", 0)
                    self.goals_completed = stats.get("goals_completed", 0)
                    self.facts_learned = stats.get("facts_learned", 0)
                    self.action_success_rates = stats.get("action_success_rates", {})

                    logger.info(f"🤖 Agent-State geladen: {len(self.active_goals)} aktive Ziele")
                    return
            except Exception as e:
                logger.debug(f"StateDatabase load failed: {e}, trying JSON fallback")

        # Fallback to JSON file
        try:
            state_file = self.data_dir / "agent_state.json"
            if state_file.exists():
                state = json.loads(state_file.read_text())

                # Ziele laden
                for g in state.get("active_goals", []):
                    goal = AgentGoal(
                        goal_id=g["goal_id"],
                        description=g["description"],
                        goal_type=g["goal_type"],
                        priority=g.get("priority", 0.5),
                        progress=g.get("progress", 0.0),
                        created_at=g.get("created_at", time.time()),
                        related_topics=g.get("related_topics", []),
                        planned_actions=g.get("planned_actions", []),
                        completed_actions=g.get("completed_actions", []),
                    )
                    self.active_goals.append(goal)

                # Stats laden
                stats = state.get("stats", {})
                self.actions_executed = stats.get("actions_executed", 0)
                self.goals_completed = stats.get("goals_completed", 0)
                self.facts_learned = stats.get("facts_learned", 0)
                self.action_success_rates = stats.get("action_success_rates", {})

                logger.info(f"🤖 Agent-State geladen: {len(self.active_goals)} aktive Ziele")
        except Exception as e:
            logger.debug(f"Could not load agent state: {e}")

    # =========================================================================
    # STATUS & DEBUGGING
    # =========================================================================

    def get_status(self) -> Dict:
        """Hole Agent-Status"""
        return {
            "is_running": self.is_running,
            "active_goals": len(self.active_goals),
            "completed_goals": self.goals_completed,
            "actions_executed": self.actions_executed,
            "facts_learned": self.facts_learned,
            "current_goals": [
                {
                    "description": g.description,
                    "progress": g.progress,
                    "next_action": g.planned_actions[0] if g.planned_actions else None
                }
                for g in self.active_goals
            ],
        }


# =============================================================================
# KOMPATIBILITÄTS-ALIASE
# =============================================================================

# KemonominiExpressions wird oben importiert als Alias für KemonomimiExpression


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("😊 HOLO INNER LIFE - TEST")
    print("=" * 70)

    life = create_inner_life()

    # Status
    print("\n📊 INITIAL STATUS:")
    status = life.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    # Simuliere Updates
    print("\n🔄 SIMULIERE UPDATES...")
    for i in range(5):
        result = life.update(
            energy=0.7,
            had_interaction=(i % 2 == 0),
            interaction_positive=True,
        )
        if result["messages"]:
            for msg in result["messages"]:
                print(f"   [{result['phase']}] {msg[:50]}...")

    # Interaktionen simulieren
    print("\n💬 SIMULIERE INTERAKTIONEN...")
    messages = [
        "Hey Holo, wie geht es dir?",
        "Ich hatte heute einen stressigen Tag",
        "Weißt du was? Ich mag Musik sehr gerne!",
        "Was denkst du über Freundschaft?",
    ]

    for msg in messages:
        milestone = life.on_interaction(msg, "Test-Antwort", was_positive=True)
        if milestone:
            print(f"   🎉 MILESTONE: {milestone}")

    # Spontane Nachrichten
    print("\n💭 SPONTANE NACHRICHTEN:")
    for i in range(3):
        msg = life.get_spontaneous_message()
        if msg:
            print(f"   {msg[:60]}...")

    # Kreativität
    print("\n🎨 KREATIVE WERKE:")
    life.creativity.last_creation = 0  # Reset cooldown
    work = life.creativity.generate_creative_work(MoodType.THOUGHTFUL)
    if work:
        print(f"   {work.creative_type.value}: {work.content[:50]}...")

    # Meinung
    print("\n💭 MEINUNGEN:")
    for topic in ["Freundschaft", "Musik"]:
        opinion = life.opinions.express_opinion(topic)
        if opinion:
            print(f"   {topic}: {opinion[:60]}...")

    # Selbstreflexion (in holo_consciousness.py, nicht hier)
    print("\n🪞 SELBSTREFLEXION:")
    if hasattr(life, 'reflection') and life.reflection:
        print(f"   {life.reflection.reflect()}")
        print(f"   {life.reflection.contemplate()}")
    else:
        # Fallback: Nutze vorhandene Methoden
        status = life.get_status()
        print(f"   Aktueller Mood: {status.get('mood', 'unbekannt')}")
        print(f"   Phase: {status.get('phase', 'unbekannt')}")
        print("   (Vollständige Selbstreflexion in holo_consciousness.py)")

    # Final Status
    print("\n📊 FINAL STATUS:")
    status = life.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
