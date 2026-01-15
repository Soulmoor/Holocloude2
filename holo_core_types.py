#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO CORE TYPES v1.0 - Zentrale Definitionen                                ║
║                                                                              ║
║  DIESE DATEI HAT KEINE ABHÄNGIGKEITEN ZU ANDEREN HOLO_* MODULEN!            ║
║  Das bricht alle zirkulären Import-Ketten.                                   ║
║                                                                              ║
║  VERWENDUNG:                                                                 ║
║      from holo_core_types import DriveType, GoalType, MoodScale, ...        ║
║                                                                              ║
║  ODER via holo_robust_imports:                                               ║
║      from holo_robust_imports import *                                       ║
║                                                                              ║
║  NIEMALS eigene Enums in anderen Modulen definieren!                         ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 1.0                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# STANDARD LIBRARY IMPORTS ONLY - Keine externen Abhängigkeiten!
# =============================================================================

import logging
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Union
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("HoloCoreTypes")

# =============================================================================
# VERSION INFO
# =============================================================================

__version__ = "1.0.0"
__all__ = [
    # Scales
    "MoodScale", "EnergyScale",
    # Enums
    "DriveType", "NeedType", "GoalType", "GoalPriority",
    "ThoughtType", "ActivityType", "InterestLevel",
    "CommandType", "CommandPriority", "MessageType",
    "EmotionType", "RouteType", "IntentType",
    # Dataclasses
    "Opinion", "EmotionalState", "TrackedTopic", "InnerThought",
    "DriveState", "NeedState", "Goal",
    # Helpers
    "validate_mood", "validate_energy", "clamp",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Begrenzt einen Wert auf einen Bereich"""
    return max(min_val, min(max_val, value))


def validate_mood(value: float, source: str = "unknown") -> float:
    """
    Validiert und konvertiert mood-Werte.
    
    Args:
        value: Der mood-Wert
        source: Woher der Wert kommt (für Logging)
        
    Returns:
        Validierter Wert zwischen 0.0 und 1.0
    """
    if value > 1.0:
        # Wahrscheinlich 0-100 Skala
        logger.warning(f"[{source}] Mood {value} scheint 0-100 Skala zu sein, konvertiere zu 0-1")
        return clamp(value / 100.0)
    return clamp(value)


def validate_energy(value: float, source: str = "unknown") -> float:
    """Validiert energy-Werte (0.0 - 1.0)"""
    if value > 1.0:
        logger.warning(f"[{source}] Energy {value} scheint 0-100 Skala zu sein, konvertiere zu 0-1")
        return clamp(value / 100.0)
    return clamp(value)


# =============================================================================
# STANDARD SCALES - IMMER 0.0 - 1.0!
# =============================================================================

class MoodScale:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  STANDARD: Mood ist IMMER 0.0 - 1.0                           ║
    ║                                                               ║
    ║  0.0  = Sehr schlecht                                         ║
    ║  0.25 = Schlecht                                              ║
    ║  0.5  = Neutral                                               ║
    ║  0.75 = Gut                                                   ║
    ║  1.0  = Sehr gut                                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    MIN = 0.0
    MAX = 1.0
    NEUTRAL = 0.5
    
    # Schwellwerte
    VERY_BAD = 0.2
    BAD = 0.35
    OKAY = 0.5
    GOOD = 0.65
    VERY_GOOD = 0.8
    EXCELLENT = 0.9
    
    @staticmethod
    def validate(value: float) -> float:
        """Stellt sicher dass mood im gültigen Bereich ist"""
        return clamp(value, MoodScale.MIN, MoodScale.MAX)
    
    @staticmethod
    def from_percentage(value: float) -> float:
        """Konvertiert 0-100 zu 0-1"""
        return MoodScale.validate(value / 100.0)
    
    @staticmethod
    def to_percentage(value: float) -> float:
        """Konvertiert 0-1 zu 0-100"""
        return MoodScale.validate(value) * 100.0
    
    @staticmethod
    def to_text(value: float) -> str:
        """Konvertiert mood zu deutschem Text"""
        value = MoodScale.validate(value)
        if value >= MoodScale.EXCELLENT:
            return "fantastisch"
        elif value >= MoodScale.VERY_GOOD:
            return "sehr gut"
        elif value >= MoodScale.GOOD:
            return "gut"
        elif value >= MoodScale.OKAY:
            return "okay"
        elif value >= MoodScale.BAD:
            return "nicht so gut"
        elif value >= MoodScale.VERY_BAD:
            return "schlecht"
        else:
            return "sehr schlecht"


class EnergyScale:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  STANDARD: Energie ist IMMER 0.0 - 1.0                        ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    MIN = 0.0
    MAX = 1.0
    FULL = 1.0
    EMPTY = 0.0
    
    # Schwellwerte
    CRITICAL = 0.15
    VERY_LOW = 0.25
    LOW = 0.4
    NORMAL = 0.6
    HIGH = 0.75
    VERY_HIGH = 0.9
    
    @staticmethod
    def validate(value: float) -> float:
        return clamp(value, EnergyScale.MIN, EnergyScale.MAX)
    
    @staticmethod
    def from_percentage(value: float) -> float:
        return EnergyScale.validate(value / 100.0)
    
    @staticmethod
    def to_text(value: float) -> str:
        value = EnergyScale.validate(value)
        if value >= EnergyScale.VERY_HIGH:
            return "voller Energie"
        elif value >= EnergyScale.HIGH:
            return "energiegeladen"
        elif value >= EnergyScale.NORMAL:
            return "normal"
        elif value >= EnergyScale.LOW:
            return "etwas müde"
        elif value >= EnergyScale.VERY_LOW:
            return "müde"
        elif value >= EnergyScale.CRITICAL:
            return "sehr müde"
        else:
            return "erschöpft"


# =============================================================================
# DRIVE TYPES - Vereinheitlicht aus drive_system + autonomous_life
# =============================================================================

class DriveType(Enum):
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Alle Antriebstypen - EINZIGE DEFINITION!                     ║
    ║                                                               ║
    ║  Kombiniert aus:                                              ║
    ║  - holo_drive_system.py                                       ║
    ║  - holo_autonomous_life.py                                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    # Aktivitäts-basierte Antriebe (ursprünglich drive_system)
    CURIOSITY = "curiosity"           # Neugier - Drang zu entdecken
    ENTERTAINMENT = "entertainment"   # Unterhaltung - Drang zu spielen
    CREATIVITY = "creativity"         # Kreativität - Drang zu erschaffen
    
    # Bedürfnis-basierte Antriebe (ursprünglich autonomous_life)
    SOCIAL = "social"                 # Soziale Interaktion
    MASTERY = "mastery"               # Meisterschaft/Lernen
    NOVELTY = "novelty"               # Neuheit - Drang nach Abwechslung
    EXPRESSION = "expression"         # Selbstausdruck
    UNDERSTANDING = "understanding"   # Verstehen - Drang zu begreifen


class NeedType(Enum):
    """Bedürfnistypen - steigen über Zeit wenn nicht befriedigt"""
    MISSING = "missing"               # Vermissen (des Users)
    LONELINESS = "loneliness"         # Einsamkeit
    CONTACT_DESIRE = "contact_desire" # Kontaktwunsch
    WORRY = "worry"                   # Besorgnis (um User)
    BOREDOM = "boredom"               # Langeweile
    THOUGHTFUL = "thoughtful"         # Nachdenklichkeit
    RESTLESSNESS = "restlessness"     # Tatendrang


# =============================================================================
# GOAL TYPES - Vereinheitlicht aus 3 Modulen
# =============================================================================

class GoalType(Enum):
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Alle Zieltypen - EINZIGE DEFINITION!                         ║
    ║                                                               ║
    ║  Kombiniert aus:                                              ║
    ║  - holo_autonomy_engine.py                                    ║
    ║  - holo_self_awareness.py                                     ║
    ║  - holo_dialogue_engine.py                                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    # Persönliche Ziele (aus self_awareness)
    LEARN = "learn"                   # Etwas Neues lernen
    UNDERSTAND = "understand"         # Etwas tiefer verstehen
    GROW = "grow"                     # Persönlich wachsen
    REFLECT = "reflect"               # Über sich nachdenken
    CREATE = "create"                 # Etwas erschaffen
    EXPLORE = "explore"               # Die Welt erkunden
    
    # Beziehungs-Ziele (aus autonomy_engine)
    CONNECT = "connect"               # Mit User verbinden
    HELP = "help"                     # User helfen
    REMEMBER = "remember"             # Sich erinnern
    EXPRESS = "express"               # Sich ausdrücken
    
    # Konversations-Ziele (aus dialogue_engine)
    INFORM = "inform"                 # Information geben
    INFORMATION = "information"       # Alias für INFORM (Abwärtskompatibilität)
    TASK = "task"                     # Aufgabe erledigen
    SUPPORT = "support"               # Emotionale Unterstützung
    ENTERTAIN = "entertain"           # Unterhalten
    ENTERTAINMENT = "entertainment"   # Alias für ENTERTAIN (Abwärtskompatibilität)
    SOCIAL = "social"                 # Small Talk / Soziale Interaktion
    LEARNING = "learning"             # Alias für LEARN (Abwärtskompatibilität)


class GoalPriority(Enum):
    """Priorität eines Ziels"""
    BACKGROUND = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


# =============================================================================
# THOUGHT TYPES - Vereinheitlicht aus 3 Modulen
# =============================================================================

class ThoughtType(Enum):
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Alle Gedankentypen - EINZIGE DEFINITION!                     ║
    ║                                                               ║
    ║  Kombiniert aus:                                              ║
    ║  - holo_consciousness.py                                      ║
    ║  - holo_cognitive_modules.py                                  ║
    ║  - holo_autonomy_engine.py                                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    # Basis-Gedanken
    OBSERVATION = "observation"       # Beobachtung
    QUESTION = "question"             # Frage
    FEELING = "feeling"               # Gefühl
    MEMORY = "memory"                 # Erinnerung

    # Komplexe Gedanken
    WONDER = "wonder"                 # Sich wundern
    DOUBT = "doubt"                   # Zweifel
    REALIZATION = "realization"       # Erkenntnis
    INSIGHT = "insight"               # Erkenntnis (Alias)
    CURIOSITY = "curiosity"           # Neugier

    # Tiefe Gedanken
    PHILOSOPHICAL = "philosophical"   # Philosophisch
    MORAL = "moral"                   # Moralisch
    EXISTENTIAL = "existential"       # Existenziell
    IDENTITY = "identity"             # Identitätsbezogen
    META = "meta"                     # Gedanke über Gedanken

    # Emotionale Gedanken
    DESIRE = "desire"                 # Wunsch/Verlangen
    FEAR = "fear"                     # Angst/Sorge
    CONCERN = "concern"               # Sorge/Bedenken
    ANTICIPATION = "anticipation"     # Vorfreude

    # Kreative Gedanken
    IMAGINATION = "imagination"       # Vorstellung
    IDEA = "idea"                     # Idee/Einfall

    # Reflexive Gedanken
    REFLECTION = "reflection"         # Reflexion
    AESTHETIC = "aesthetic"           # Ästhetische Wahrnehmung
    SOCIAL = "social"                 # Soziale Gedanken
    TEMPORAL = "temporal"             # Zeitbezogen

    # Spontane Gedanken
    RANDOM = "random"                 # Zufällig
    PROACTIVE = "proactive"           # Proaktiv
    ASSOCIATIVE = "associative"       # Assoziativ


# =============================================================================
# ACTIVITY TYPES
# =============================================================================

class ActivityType(Enum):
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Aktivitätstypen für Holos autonomes Verhalten                ║
    ║                                                               ║
    ║  KONSOLIDIERT aus:                                            ║
    ║  - holo_core_types.py                                         ║
    ║  - holo_inner_life.py                                         ║
    ║  - holo_database_system.py                                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    # Passive Aktivitäten
    IDLE = "idle"
    RESTING = "resting"
    SLEEPING = "sleeping"
    DREAMING = "dreaming"
    NAPPING = "napping"

    # Lern-Aktivitäten
    READING_NEWS = "reading_news"
    CHECK_NEWS = "check_news"              # Alias für READING_NEWS
    LEARNING = "learning"
    LEARN_SOMETHING = "learn_something"    # Alias für LEARNING
    RESEARCHING = "researching"
    STUDYING = "studying"
    EXPLORE_INTEREST = "explore_interest"

    # Reflexive Aktivitäten
    THINKING = "thinking"
    REFLECT = "reflect"
    DAYDREAM = "daydream"
    REVIEW_MEMORIES = "review_memories"
    THINK_ABOUT_USER = "think_about_user"
    PHILOSOPHICAL_THOUGHT = "philosophical_thought"
    OBSERVE_NETWORK = "observe_network"

    # Kreative Aktivitäten
    CREATING = "creating"
    CREATIVE_THOUGHT = "creative_thought"
    DRAWING = "drawing"
    WRITING = "writing"

    # Unterhaltung
    PLAYING = "playing"
    WATCHING = "watching"
    LISTENING = "listening"
    BROWSING = "browsing"

    # Wahrnehmung (Text & Bild)
    READING_TEXT = "reading_text"        # Text/Buch/Artikel lesen
    VIEWING_IMAGE = "viewing_image"      # Bild betrachten und analysieren
    ANALYZING_CONTENT = "analyzing_content"  # Inhalt analysieren

    # Soziale Aktivitäten
    CHATTING = "chatting"
    CONVERSATION = "conversation"          # Alias für CHATTING
    WAITING = "waiting"
    MISSING_USER = "missing_user"


# =============================================================================
# INTEREST LEVELS
# =============================================================================

class InterestLevel(Enum):
    """
    Nuancierte Interesse-Level (als Enum mit float Werten).
    
    Holo kann etwas interessant finden ohne es zu mögen,
    oder etwas nebenbei verfolgen ohne begeistert zu sein.
    """
    PASSIONATE = "passionate"         # 1.0 - "Das LIEBE ich!"
    ENTHUSIASTIC = "enthusiastic"     # 0.8 - "Das interessiert mich sehr!"
    ACTIVE = "active"                 # 0.6 - "Das verfolge ich aktiv"
    CASUAL = "casual"                 # 0.4 - "Verfolge ich so nebenbei"
    CURIOUS = "curious"               # 0.2 - "Klingt interessant"
    NEUTRAL = "neutral"               # 0.0 - Weder interessiert noch desinteressiert
    INDIFFERENT = "indifferent"       # -0.2 - "Ist mir ziemlich egal"
    UNINTERESTED = "uninterested"     # -0.4 - "Interessiert mich nicht"
    BORED = "bored"                   # -0.6 - "Langweilt mich"
    AVERSION = "aversion"             # -0.8 - "Mag ich aktiv nicht"
    REPULSED = "repulsed"             # -1.0 - "Kann ich nicht ausstehen"
    
    @property
    def value_float(self) -> float:
        """Gibt den numerischen Wert zurück"""
        mapping = {
            "passionate": 1.0,
            "enthusiastic": 0.8,
            "active": 0.6,
            "casual": 0.4,
            "curious": 0.2,
            "neutral": 0.0,
            "indifferent": -0.2,
            "uninterested": -0.4,
            "bored": -0.6,
            "aversion": -0.8,
            "repulsed": -1.0,
        }
        return mapping.get(self.value, 0.0)
    
    @classmethod
    def from_float(cls, value: float) -> "InterestLevel":
        """Konvertiert float zu InterestLevel"""
        if value >= 0.9:
            return cls.PASSIONATE
        elif value >= 0.7:
            return cls.ENTHUSIASTIC
        elif value >= 0.5:
            return cls.ACTIVE
        elif value >= 0.3:
            return cls.CASUAL
        elif value >= 0.1:
            return cls.CURIOUS
        elif value >= -0.1:
            return cls.NEUTRAL
        elif value >= -0.3:
            return cls.INDIFFERENT
        elif value >= -0.5:
            return cls.UNINTERESTED
        elif value >= -0.7:
            return cls.BORED
        elif value >= -0.9:
            return cls.AVERSION
        else:
            return cls.REPULSED


# =============================================================================
# COMMAND TYPES (für Pi-Control)
# =============================================================================

class CommandType(Enum):
    """Befehlstypen für Pi-Control Kommunikation"""
    NAS_CONTROL = "nas"
    SYSTEM_CONTROL = "system"
    GOVERNOR_CONTROL = "governor"
    QUERY = "query"
    SMART_HOME = "smart_home"
    TIMER = "timer"
    REMINDER = "reminder"
    CUSTOM = "custom"


class CommandPriority(Enum):
    """Priorität eines Befehls"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# =============================================================================
# MESSAGE & INTENT TYPES
# =============================================================================

class MessageType(Enum):
    """Nachrichtentypen"""
    USER_MESSAGE = "user"
    ASSISTANT_MESSAGE = "assistant"
    SYSTEM_MESSAGE = "system"
    PROACTIVE_MESSAGE = "proactive"
    NOTIFICATION = "notification"
    ERROR = "error"


class IntentType(Enum):
    """
    Intent-Typen für Nachrichtenverarbeitung.
    Aus holo_smart_understanding.py.
    """
    # Grüße & Abschied
    GREETING = "greeting"
    FAREWELL = "farewell"
    
    # Fragen
    QUESTION = "question"
    STATUS = "status"
    TIME = "time"
    WEATHER = "weather"
    
    # Wissen
    NEWS = "news"
    SEARCH = "search"
    KNOWLEDGE = "knowledge"
    USER_KNOWLEDGE = "user_knowledge"
    
    # Befehle
    COMMAND = "command"
    SMART_HOME = "smart_home"
    TIMER = "timer"
    REMINDER = "reminder"
    
    # Sozial
    CHITCHAT = "chitchat"
    COMPLIMENT = "compliment"
    GRATITUDE = "gratitude"
    EMOTION = "emotion"
    
    # Spezial
    HELP = "help"
    FEEDBACK = "feedback"
    CREATIVE = "creative"
    CODE = "code"
    
    # Fallback
    UNKNOWN = "unknown"


class RouteType(Enum):
    """
    Routing-Typen für LLM-Entscheidungen.
    Aus holo_intelligent_router.py.
    """
    LOCAL_TEMPLATE = "local_template"   # Rein lokal (Templates + Impulse)
    LOCAL_NLP = "local_nlp"             # Lokal mit NLP-Algorithmen
    HYBRID_IMPULSE = "hybrid_impulse"   # Impulse-basiert + minimales LLM
    HYBRID_ENHANCE = "hybrid_enhance"   # Lokale Basis + LLM Enhancement
    LLM_SIMPLE = "llm_simple"           # LLM mit komprimiertem Kontext
    LLM_FULL = "llm_full"               # LLM mit vollem Kontext
    LLM_PHILOSOPHICAL = "llm_philosophical"  # LLM mit philosophischem Kontext


# =============================================================================
# EMOTION TYPES
# =============================================================================

class EmotionType(Enum):
    """Basis-Emotionen"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    
    # Erweiterte Emotionen
    CURIOSITY = "curiosity"
    LOVE = "love"
    PRIDE = "pride"
    SHAME = "shame"
    GUILT = "guilt"
    ENVY = "envy"
    GRATITUDE = "gratitude"
    HOPE = "hope"
    LONELINESS = "loneliness"
    BOREDOM = "boredom"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"


# =============================================================================
# COMMON DATACLASSES
# =============================================================================

@dataclass
class Opinion:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Eine Meinung von Holo - EINZIGE DEFINITION!                  ║
    ║                                                               ║
    ║  KONSOLIDIERT aus:                                            ║
    ║  - holo_preferences.py (express(), update())                  ║
    ║  - holo_consciousness.py (get_expression_prefix())            ║
    ║  - holo_inner_life.py (numerische stance)                     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    topic: str
    stance: str                       # Die Position als Text
    stance_value: float = 0.0         # -1 (negativ) bis +1 (positiv)
    confidence: float = 0.5           # 0-1, wie stark die Meinung (alias: strength)
    reasoning: List[str] = field(default_factory=list)  # Begründungen (alias: reasons)
    experiences: List[str] = field(default_factory=list)
    formed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_reinforced: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    experience_count: int = 1
    can_change: bool = True           # Kann sich ändern?
    open_to_change: bool = True       # Alias für can_change

    # Aliase für Abwärtskompatibilität
    @property
    def strength(self) -> float:
        """Alias für confidence"""
        return self.confidence

    @strength.setter
    def strength(self, value: float):
        self.confidence = clamp(value)

    @property
    def reasons(self) -> List[str]:
        """Alias für reasoning"""
        return self.reasoning

    @reasons.setter
    def reasons(self, value: List[str]):
        self.reasoning = value

    def __post_init__(self):
        self.strength = clamp(self.strength)
        self.open_to_change = self.can_change

    def get_expression_prefix(self) -> str:
        """Wie würde Holo diese Meinung ausdrücken?"""
        if self.strength < 0.3:
            return "Ich vermute,"
        elif self.strength < 0.5:
            return "Ich glaube,"
        elif self.strength < 0.7:
            return "Ich denke,"
        elif self.strength < 0.9:
            return "Ich bin überzeugt:"
        else:
            return "Ich bin mir sicher:"

    def update(self, new_experience: str, shift: float = 0.0):
        """
        Update Meinung basierend auf neuer Erfahrung.
        (Aus holo_inner_life.py)
        """
        self.experiences.append(new_experience)
        if len(self.experiences) > 10:
            self.experiences = self.experiences[-10:]

        # Stance anpassen
        self.stance_value = max(-1, min(1, self.stance_value + shift * 0.2))
        self.strength = clamp(self.strength + 0.05)
        self.last_updated = datetime.now().isoformat()
        self.experience_count += 1

    def reinforce(self, amount: float = 0.1):
        """Verstärkt die Meinung"""
        self.strength = clamp(self.strength + amount)
        self.experience_count += 1
        self.last_reinforced = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()

    def weaken(self, amount: float = 0.1):
        """Schwächt die Meinung"""
        if self.can_change:
            self.strength = clamp(self.strength - amount)
            self.last_updated = datetime.now().isoformat()

    def express(self) -> str:
        """Drückt die Meinung aus"""
        prefix = self.get_expression_prefix()
        return f"{prefix} {self.stance}"

    # =========================================================================
    # ADAPTIVES LERNEN - Bayesian-ähnliche Updates
    # =========================================================================

    def observe_user_feedback(self, user_agreed: bool, interaction_strength: float = 1.0):
        """
        Passt Meinung basierend auf User-Feedback an (Bayesian-ähnlich).

        Args:
            user_agreed: True wenn User zustimmte, False wenn widersprach
            interaction_strength: Wie stark die Interaktion war (0-1)
                                  z.B. explizite Zustimmung = 1.0, implizit = 0.3

        Die Meinung konvergiert langsam zu User's Ansichten.
        """
        if not self.can_change:
            return  # Kernüberzeugungen ändern sich nicht

        # Lernrate basierend auf aktueller Konfidenz
        # Niedrige Konfidenz = schneller lernen
        learning_rate = 0.1 * (1.0 - self.confidence * 0.5) * interaction_strength

        if user_agreed:
            # Zustimmung verstärkt die Meinung
            self.confidence = clamp(self.confidence + learning_rate)
            self.stance_value = clamp(self.stance_value + learning_rate * 0.5, -1, 1)
        else:
            # Widerspruch schwächt die Meinung
            self.confidence = clamp(self.confidence - learning_rate * 0.7)
            # Bei starkem Widerspruch kann sich stance_value umkehren
            self.stance_value = clamp(self.stance_value - learning_rate * 0.3, -1, 1)

        self.experience_count += 1
        self.last_updated = datetime.now().isoformat()

    def decay(self, days_passed: float = 1.0):
        """
        Lässt Konfidenz über Zeit verfallen wenn nicht verstärkt.

        Selten bestätigte Meinungen werden unsicherer.
        """
        if not self.can_change:
            return

        # Decay-Rate: ~5% pro Tag
        decay_rate = 0.05 * days_passed

        # Aber nie unter 0.2 (Basisunsicherheit)
        self.confidence = max(0.2, self.confidence - decay_rate)

    def get_uncertainty(self) -> float:
        """Gibt Unsicherheit zurück (1 - confidence)."""
        return 1.0 - self.confidence

    def should_express(self, context_relevance: float = 0.5) -> bool:
        """
        Entscheidet ob diese Meinung ausgedrückt werden sollte.

        Starke Meinungen zu relevanten Themen werden eher geteilt.
        """
        # Wahrscheinlichkeit basierend auf Stärke und Relevanz
        prob = self.confidence * 0.6 + context_relevance * 0.4
        return random.random() < prob


@dataclass
class EmotionalState:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Emotionaler Zustand - EINZIGE DEFINITION!                    ║
    ║                                                               ║
    ║  ALLE WERTE SIND 0.0 - 1.0!                                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    mood: float = MoodScale.NEUTRAL
    energy: float = EnergyScale.NORMAL
    arousal: float = 0.5              # Erregungsniveau
    valence: float = 0.5              # Positiv/Negativ
    
    # Spezifische Emotionen (alle 0-1)
    joy: float = 0.0
    sadness: float = 0.0
    curiosity: float = 0.5
    playfulness: float = 0.3
    trust: float = 0.5
    anticipation: float = 0.3
    
    # Meta
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validiere alle Werte"""
        self.mood = MoodScale.validate(self.mood)
        self.energy = EnergyScale.validate(self.energy)
        self.arousal = clamp(self.arousal)
        self.valence = clamp(self.valence)
        self.joy = clamp(self.joy)
        self.sadness = clamp(self.sadness)
        self.curiosity = clamp(self.curiosity)
        self.playfulness = clamp(self.playfulness)
        self.trust = clamp(self.trust)
        self.anticipation = clamp(self.anticipation)
    
    def get_mood_text(self) -> str:
        return MoodScale.to_text(self.mood)
    
    def get_energy_text(self) -> str:
        return EnergyScale.to_text(self.energy)
    
    def get_dominant_emotion(self) -> str:
        """Gibt die stärkste Emotion zurück"""
        emotions = {
            "Freude": self.joy,
            "Traurigkeit": self.sadness,
            "Neugier": self.curiosity,
            "Verspieltheit": self.playfulness,
        }
        return max(emotions, key=emotions.get)


@dataclass
class TrackedTopic:
    """Ein verfolgtes Thema/Interesse"""
    topic: str
    interest_level: InterestLevel = InterestLevel.NEUTRAL
    first_mentioned: str = field(default_factory=lambda: datetime.now().isoformat())
    last_mentioned: str = field(default_factory=lambda: datetime.now().isoformat())
    mention_count: int = 1
    context_snippets: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    
    def mention(self, context: str = ""):
        """Topic wurde erwähnt"""
        self.mention_count += 1
        self.last_mentioned = datetime.now().isoformat()
        if context and len(self.context_snippets) < 10:
            self.context_snippets.append(context[:200])


@dataclass
class InnerThought:
    """Ein innerer Gedanke von Holo"""
    content: str
    thought_type: ThoughtType = ThoughtType.OBSERVATION
    intensity: float = 0.5            # 0-1, wie "laut" der Gedanke ist
    triggered_by: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    shared_with_user: bool = False
    
    def __post_init__(self):
        self.intensity = clamp(self.intensity)
    
    def format_for_sharing(self) -> str:
        """Formatiert den Gedanken für den User"""
        prefixes = {
            ThoughtType.OBSERVATION: "*bemerkt*",
            ThoughtType.QUESTION: "*fragt sich*",
            ThoughtType.FEELING: "*spürt*",
            ThoughtType.MEMORY: "*erinnert sich*",
            ThoughtType.WONDER: "*wundert sich*",
            ThoughtType.DOUBT: "*zögert*",
            ThoughtType.REALIZATION: "*erkennt*",
            ThoughtType.CURIOSITY: "*wird neugierig*",
            ThoughtType.PHILOSOPHICAL: "*denkt nach*",
            ThoughtType.MORAL: "*horcht in sich hinein*",
        }
        prefix = prefixes.get(self.thought_type, "*denkt*")
        return f"{prefix} {self.content}"


@dataclass
class DriveState:
    """Aktueller Zustand aller Antriebe (alle 0-1)"""
    curiosity: float = 0.7
    entertainment: float = 0.7
    creativity: float = 0.7
    social: float = 0.5
    mastery: float = 0.5
    novelty: float = 0.5
    expression: float = 0.5
    understanding: float = 0.5
    
    def __post_init__(self):
        for attr in ['curiosity', 'entertainment', 'creativity', 'social', 
                     'mastery', 'novelty', 'expression', 'understanding']:
            setattr(self, attr, clamp(getattr(self, attr)))
    
    def get(self, drive_type: DriveType) -> float:
        return getattr(self, drive_type.value, 0.5)
    
    def set(self, drive_type: DriveType, value: float):
        setattr(self, drive_type.value, clamp(value))
    
    def drain(self, drive_type: DriveType, amount: float):
        current = self.get(drive_type)
        self.set(drive_type, current - amount)
    
    def regenerate(self, drive_type: DriveType, amount: float):
        current = self.get(drive_type)
        self.set(drive_type, current + amount)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'curiosity': self.curiosity,
            'entertainment': self.entertainment,
            'creativity': self.creativity,
            'social': self.social,
            'mastery': self.mastery,
            'novelty': self.novelty,
            'expression': self.expression,
            'understanding': self.understanding,
        }


@dataclass
class NeedState:
    """Aktueller Zustand aller Bedürfnisse (alle 0-1)"""
    missing: float = 0.0
    loneliness: float = 0.0
    contact_desire: float = 0.0
    worry: float = 0.0
    boredom: float = 0.0
    thoughtful: float = 0.0
    restlessness: float = 0.0
    
    def __post_init__(self):
        for attr in ['missing', 'loneliness', 'contact_desire', 'worry',
                     'boredom', 'thoughtful', 'restlessness']:
            setattr(self, attr, clamp(getattr(self, attr)))
    
    def get(self, need_type: NeedType) -> float:
        return getattr(self, need_type.value, 0.0)
    
    def set(self, need_type: NeedType, value: float):
        setattr(self, need_type.value, clamp(value))
    
    def increase(self, need_type: NeedType, amount: float):
        current = self.get(need_type)
        self.set(need_type, current + amount)
    
    def decrease(self, need_type: NeedType, amount: float):
        current = self.get(need_type)
        self.set(need_type, current - amount)
    
    def reset_on_interaction(self):
        """Setzt soziale Bedürfnisse bei User-Interaktion zurück"""
        self.missing = clamp(self.missing - 0.3)
        self.loneliness = clamp(self.loneliness - 0.4)
        self.contact_desire = clamp(self.contact_desire - 0.5)
        self.worry = clamp(self.worry - 0.4)
        self.boredom = clamp(self.boredom - 0.2)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'missing': self.missing,
            'loneliness': self.loneliness,
            'contact_desire': self.contact_desire,
            'worry': self.worry,
            'boredom': self.boredom,
            'thoughtful': self.thoughtful,
            'restlessness': self.restlessness,
        }


@dataclass
class Goal:
    """Ein Ziel von Holo"""
    id: str = ""
    goal_type: GoalType = GoalType.LEARN
    description: str = ""
    priority: GoalPriority = GoalPriority.NORMAL
    progress: float = 0.0             # 0-1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    deadline: Optional[str] = None
    completed: bool = False
    
    def __post_init__(self):
        self.progress = clamp(self.progress)
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())[:8]
    
    def advance(self, amount: float):
        """Fortschritt machen"""
        self.progress = clamp(self.progress + amount)
        if self.progress >= 1.0:
            self.completed = True


# =============================================================================
# SENTIMENT - Aus holo_smart_understanding, holo_text_reader
# =============================================================================

class Sentiment(Enum):
    """Sentiment-Klassifizierung für Texte"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

    @classmethod
    def from_score(cls, score: float) -> "Sentiment":
        """Konvertiert Score (-1 bis 1) zu Sentiment"""
        if score >= 0.5:
            return cls.VERY_POSITIVE
        elif score >= 0.2:
            return cls.POSITIVE
        elif score >= -0.2:
            return cls.NEUTRAL
        elif score >= -0.5:
            return cls.NEGATIVE
        else:
            return cls.VERY_NEGATIVE


# =============================================================================
# CONTEXT TYPES - Aus holo_context_mind
# =============================================================================

class ContextType(Enum):
    """Verschiedene Kontext-Typen"""
    CHAT = "chat"               # Gesprächsverlauf
    EMOTION = "emotion"         # Emotionen (User & Holo)
    LEARNING = "learning"       # Gelerntes Wissen
    WORLD = "world"             # Externe Welt (Wetter, News, Events)
    SELF = "self"               # Über Holo selbst
    USER = "user"               # Über den User
    TASK = "task"               # Aufgaben/Projekte
    THOUGHT = "thought"         # Gedankengänge
    REFLECTION = "reflection"   # Selbstreflexionen


class Importance(Enum):
    """Wichtigkeit eines Context-Eintrags"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


# =============================================================================
# DIALOGUE STATES - Aus holo_dialogue_engine
# =============================================================================

class DialogueState(Enum):
    """Zustände eines Dialogs"""
    IDLE = "idle"
    GREETING = "greeting"
    ENGAGED = "engaged"
    QUESTIONING = "questioning"
    EXPLAINING = "explaining"
    SUPPORTING = "supporting"
    FAREWELL = "farewell"
    SLEEPING = "sleeping"


# =============================================================================
# FACT TYPES - Aus holo_text_reader
# =============================================================================

class FactType(Enum):
    """Typen von extrahierten Fakten"""
    STATISTIC = "statistic"
    DATE = "date"
    DEFINITION = "definition"
    QUOTE = "quote"
    RESEARCH = "research"
    COMPARISON = "comparison"
    ANNOUNCEMENT = "announcement"
    TREND = "trend"
    LOCATION = "location"
    UNKNOWN = "unknown"


# =============================================================================
# TOPIC CATEGORIES - Aus holo_text_reader
# =============================================================================

class TopicCategory(Enum):
    """Themen-Kategorien für Texte"""
    TECH = "tech"
    SCIENCE = "science"
    POLITICS = "politics"
    ECONOMY = "economy"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    GAMING = "gaming"
    HEALTH = "health"
    ENVIRONMENT = "environment"
    GENERAL = "general"


# =============================================================================
# BASE CONTEXT TRACKER - Basisklasse für alle Tracker
# =============================================================================

class BaseContextTracker:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  Basisklasse für alle ContextTracker                          ║
    ║                                                               ║
    ║  Alle Tracker sollen von dieser Klasse erben:                 ║
    ║  - EmotionalContextTracker                                    ║
    ║  - ChatContextTracker                                         ║
    ║  - ConversationContextTracker                                 ║
    ║  - TopicTracker                                               ║
    ║  - ActivityContextTracker                                     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """

    def __init__(self, max_entries: int = 100, context_type: ContextType = ContextType.CHAT):
        self.context_type = context_type
        self.max_entries = max_entries
        self.entries: List[Dict[str, Any]] = []
        self._last_update = datetime.now()

    def add_entry(self, content: Any, importance: Importance = Importance.NORMAL,
                  metadata: Dict = None) -> str:
        """Fügt einen Eintrag hinzu"""
        import uuid
        entry_id = str(uuid.uuid4())[:8]

        entry = {
            "id": entry_id,
            "content": content,
            "importance": importance.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.entries.append(entry)
        self._last_update = datetime.now()

        # Limit durchsetzen
        if len(self.entries) > self.max_entries:
            # Behalte wichtige Einträge
            self.entries = sorted(
                self.entries,
                key=lambda e: (e.get("importance", 2), e.get("timestamp", "")),
                reverse=True
            )[:self.max_entries]

        return entry_id

    def get_recent(self, n: int = 10) -> List[Dict]:
        """Gibt die letzten n Einträge zurück"""
        return self.entries[-n:] if self.entries else []

    def get_by_importance(self, min_importance: Importance = Importance.HIGH) -> List[Dict]:
        """Gibt Einträge mit mindestens der angegebenen Wichtigkeit zurück"""
        return [e for e in self.entries if e.get("importance", 2) >= min_importance.value]

    def search(self, query: str) -> List[Dict]:
        """Durchsucht Einträge nach Keyword"""
        query_lower = query.lower()
        results = []

        for entry in self.entries:
            content = str(entry.get("content", "")).lower()
            if query_lower in content:
                results.append(entry)

        return results

    def clear(self):
        """Löscht alle Einträge"""
        self.entries = []

    def to_dict(self) -> Dict:
        """Exportiert als Dictionary"""
        return {
            "context_type": self.context_type.value,
            "entries": self.entries,
            "last_update": self._last_update.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BaseContextTracker":
        """Importiert aus Dictionary"""
        tracker = cls()
        tracker.context_type = ContextType(data.get("context_type", "chat"))
        tracker.entries = data.get("entries", [])
        return tracker


# =============================================================================
# NLP HELPERS - Zentrale NLP-Funktionen
# =============================================================================

# Stopwords für Deutsch und Englisch
STOPWORDS_DE = {
    "der", "die", "das", "ein", "eine", "und", "oder", "aber", "ist", "sind",
    "war", "waren", "hat", "haben", "wird", "werden", "ich", "du", "er", "sie",
    "es", "wir", "ihr", "mir", "dir", "mich", "dich", "sich", "den", "dem",
    "des", "im", "in", "an", "auf", "für", "mit", "bei", "zu", "von", "aus",
    "nach", "über", "unter", "vor", "hinter", "nicht", "auch", "noch", "schon",
    "nur", "sehr", "so", "wie", "was", "wer", "wo", "wann", "warum", "wenn",
    "dann", "denn", "mal", "bitte", "ja", "nein", "okay", "ok", "hm",
}

STOPWORDS_EN = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "and", "but", "or", "not", "this", "that", "these", "those", "i", "me",
    "my", "we", "our", "you", "your", "he", "him", "his", "she", "her", "it",
    "its", "they", "them", "their", "what", "which", "who", "when", "where",
    "why", "how", "all", "each", "every", "some", "any", "no",
}

STOPWORDS = STOPWORDS_DE | STOPWORDS_EN


def extract_keywords(text: str, n: int = 10, min_length: int = 3) -> List[str]:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  ZENTRALE Keyword-Extraktion                                  ║
    ║                                                               ║
    ║  ALLE Module sollen diese Funktion nutzen!                    ║
    ║                                                               ║
    ║  from holo_core_types import extract_keywords                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    import re
    from collections import Counter

    # Tokenisiere
    words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text.lower())

    # Filtere Stopwords und kurze Wörter
    filtered = [w for w in words if w not in STOPWORDS and len(w) >= min_length]

    # Zähle und sortiere
    counts = Counter(filtered)

    # Gib Top-N zurück
    return [word for word, _ in counts.most_common(n)]


def simple_tokenize(text: str) -> List[str]:
    """Einfache Tokenisierung"""
    import re
    return re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text.lower())


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Berechnet Jaccard-Similarity zwischen zwei Texten.
    Schnell und ohne externe Abhängigkeiten.
    """
    words1 = set(simple_tokenize(text1)) - STOPWORDS
    words2 = set(simple_tokenize(text2)) - STOPWORDS

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


# =============================================================================
# ADDITIONAL EXPORTS
# =============================================================================

# Update __all__ with new exports
__all__.extend([
    # New Enums
    "Sentiment", "ContextType", "Importance", "DialogueState",
    "FactType", "TopicCategory",
    # Base Classes
    "BaseContextTracker",
    # NLP Functions
    "extract_keywords", "simple_tokenize", "calculate_similarity",
    "STOPWORDS", "STOPWORDS_DE", "STOPWORDS_EN",
])


# =============================================================================
# SELF-TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HOLO CORE TYPES - Self-Test")
    print("=" * 60)
    
    # Test Scales
    print("\n[1] MoodScale Test:")
    print(f"  validate(0.7) = {MoodScale.validate(0.7)}")
    print(f"  from_percentage(75) = {MoodScale.from_percentage(75)}")
    print(f"  to_text(0.8) = {MoodScale.to_text(0.8)}")
    
    # Test Enums
    print("\n[2] DriveType Test:")
    print(f"  Alle DriveTypes: {[d.value for d in DriveType]}")
    
    print("\n[3] GoalType Test:")
    print(f"  Alle GoalTypes: {[g.value for g in GoalType]}")
    
    # Test Dataclasses
    print("\n[4] EmotionalState Test:")
    state = EmotionalState(mood=0.8, energy=0.6)
    print(f"  mood={state.mood}, energy={state.energy}")
    print(f"  mood_text='{state.get_mood_text()}', energy_text='{state.get_energy_text()}'")
    
    print("\n[5] Opinion Test:")
    opinion = Opinion(topic="Anime", stance="Ich liebe es!", confidence=0.9)
    print(f"  {opinion.get_expression_prefix()} {opinion.stance}")
    
    print("\n[6] DriveState Test:")
    drives = DriveState()
    drives.drain(DriveType.CURIOSITY, 0.2)
    print(f"  curiosity after drain: {drives.get(DriveType.CURIOSITY)}")
    
    print("\n" + "=" * 60)
    print("✅ Alle Tests erfolgreich!")
    print("=" * 60)
