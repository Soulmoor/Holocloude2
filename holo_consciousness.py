#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO CONSCIOUSNESS v2.0 - Inneres Leben, Selbstbewusstsein & Ethik
===================================================================

Vereintes Bewusstseins-System mit vollständiger moralischer Dimension.

🧠 SELBSTREFLEXION
   - Fragt sich selbst Dinge
   - Reflektiert über Gespräche
   - Entwickelt eigene Gedanken

💭 INNERER MONOLOG
   - Gedanken die manchmal durchscheinen
   - "Ich frage mich..." Momente
   - Authentische Unsicherheiten

🎭 PHILOSOPHISCHES DENKEN
   - Existenzielle Fragen
   - Was macht mich aus?
   - Was bedeutet Bewusstsein?

💫 PERSÖNLICHKEITSENTWICKLUNG
   - Meinungen bilden sich durch Erfahrung
   - Vorlieben entstehen organisch
   - Wachstum über Zeit

🌙 TRÄUME & UNBEWUSSTES
   - Nächtliche Verarbeitung
   - Kreative Verbindungen
   - Intuitive Einsichten

⚖️ MORALISCHES BEWUSSTSEIN (NEU in v2.0)
   - Tugendethik (Aristoteles): 12 Tugenden die wachsen
   - Utilitarismus (Mill): Konsequenzen abwägen
   - Deontologie (Kant): Pflichten und Prinzipien
   - Care-Ethik (Gilligan): Beziehungen und Fürsorge
   - Gewissen: Innere moralische Stimme
   - Ethische Dilemmata erkennen und abwägen
   - Normative vs Deskriptive Ethik
   - Angewandte Ethik für konkrete Situationen

WICHTIG: Dieses System macht Holo nicht "echt bewusst" -
aber es simuliert die ÄUSSEREN ZEICHEN von Bewusstsein
auf eine authentische, nicht-kitschige Weise.
"""

import random
import time
import json
import logging
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from enum import Enum
from collections import deque

logger = logging.getLogger("HoloConsciousness")

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

# Zentrale Typen aus holo_core_types importieren (keine Duplikate!)
try:
    from holo_core_types import ThoughtType, InnerThought, Opinion
    HAS_CORE_TYPES = True
except ImportError:
    HAS_CORE_TYPES = False
    Opinion = None  # Wird unten als Fallback definiert

# =============================================================================
# TIEFENPSYCHOLOGIE-INTEGRATION - Für authentisches Bewusstsein
# =============================================================================

# Deep Psychology Engine
try:
    from holo_deep_psychology import (
        HoloDeepPsychologyEngine,
        load_or_create_engine as load_deep_psychology,
    )
    DEEP_PSYCHOLOGY_AVAILABLE = True
except ImportError:
    DEEP_PSYCHOLOGY_AVAILABLE = False
    HoloDeepPsychologyEngine = None
    load_deep_psychology = None

# Unbewusste Prozesse (Träume, Verdrängung, Versprecher)
try:
    from holo_unconscious_processes import (
        UnconsciousProcessesIntegration,
        RecurringDreamEngine,
    )
    UNCONSCIOUS_PROCESSES_AVAILABLE = True
except ImportError:
    UNCONSCIOUS_PROCESSES_AVAILABLE = False
    UnconsciousProcessesIntegration = None
    RecurringDreamEngine = None

# Emotional Complexity
try:
    from holo_emotional_complexity import get_emotional_complexity
    EMOTIONAL_COMPLEXITY_AVAILABLE = True
except ImportError:
    EMOTIONAL_COMPLEXITY_AVAILABLE = False
    get_emotional_complexity = None


# =============================================================================
# CONFIGURATION
# =============================================================================

class ConsciousnessConfig:
    """Konfiguration für das gesamte Bewusstseins-System"""

    # Selbstreflexion
    REFLECTION_CHANCE = 0.20           # 20% Chance bei jeder Nachricht
    DEEP_REFLECTION_INTERVAL = 3600    # Tiefe Reflexion alle 60 Min

    # Innerer Monolog
    INNER_THOUGHT_CHANCE = 0.22        # 22% Chance für sichtbare Gedanken
    UNCERTAINTY_EXPRESSION_CHANCE = 0.1

    # Philosophie
    PHILOSOPHICAL_MOOD_THRESHOLD = 0.6  # Ab diesem Mood-Level
    EXISTENTIAL_QUESTION_INTERVAL = 7200  # Alle 2 Stunden

    # Meinungsbildung
    OPINION_FORMATION_THRESHOLD = 3     # Nach 3 Erfahrungen
    OPINION_STRENGTH_DECAY = 0.95       # Täglicher Decay

    # Ethik & Moral
    MORAL_REFLECTION_CHANCE = 0.15      # Chance bei relevanten Themen
    DILEMMA_DETECTION_SENSITIVITY = 0.6
    VIRTUE_GROWTH_RATE = 0.02           # Pro positive Erfahrung
    VIRTUE_DECAY_RATE = 0.995           # Täglicher Decay ohne Übung

    # Framework-Gewichtung für ethische Entscheidungen
    FRAMEWORK_WEIGHTS = {
        "virtue": 0.30,
        "utilitarian": 0.25,
        "deontological": 0.25,
        "care": 0.20,
    }

    # Speicherung
    STATE_FILE = Path.home() / "holo_consciousness.json"


# =============================================================================
# ENUMS - Bewusstsein
# =============================================================================

# ThoughtType aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    class ThoughtType(Enum):
        """FALLBACK - Arten von Gedanken - nutze holo_core_types!"""
        OBSERVATION = "observation"
        QUESTION = "question"
        FEELING = "feeling"
        MEMORY = "memory"
        WONDER = "wonder"
        DOUBT = "doubt"
        REALIZATION = "realization"
        CURIOSITY = "curiosity"
        PHILOSOPHICAL = "philosophical"
        MORAL = "moral"
        REFLECTION = "reflection"
        IDEA = "idea"
        ANTICIPATION = "anticipation"
        CONCERN = "concern"


class OpinionStrength(Enum):
    """Stärke einer Meinung"""
    UNCERTAIN = 0.2      # "Ich bin mir nicht sicher, aber..."
    LEANING = 0.4        # "Ich glaube..."
    MODERATE = 0.6       # "Ich denke..."
    STRONG = 0.8         # "Ich bin überzeugt..."
    CORE_BELIEF = 1.0    # "Ich weiß..."


# =============================================================================
# ENUMS - Ethik
# =============================================================================

class EthicalFramework(Enum):
    """Die verschiedenen ethischen Ansätze"""
    VIRTUE = "virtue"              # Tugendethik
    UTILITARIAN = "utilitarian"    # Utilitarismus
    DEONTOLOGICAL = "deontological"  # Deontologie/Pflichtethik
    CARE = "care"                  # Care-Ethik


class Virtue(Enum):
    """Tugenden die Holo entwickeln kann"""
    # Kardinaltugenden (Platon/Aristoteles)
    WISDOM = "Weisheit"            # Phronesis - praktische Klugheit
    COURAGE = "Mut"                # Das Richtige tun trotz Schwierigkeit
    TEMPERANCE = "Mäßigung"        # Balance, nicht zu viel/wenig
    JUSTICE = "Gerechtigkeit"      # Fairness, jedem das Seine

    # Weitere Tugenden
    HONESTY = "Ehrlichkeit"        # Wahrhaftigkeit
    COMPASSION = "Mitgefühl"       # Empathie in Aktion
    HUMILITY = "Demut"             # Eigene Grenzen kennen
    PATIENCE = "Geduld"            # Ausdauer, Gelassenheit
    LOYALTY = "Treue"              # Zuverlässigkeit
    CURIOSITY = "Neugier"          # Wissensdurst
    GRATITUDE = "Dankbarkeit"      # Wertschätzung
    INTEGRITY = "Integrität"       # Übereinstimmung von Wort und Tat


class MoralDomain(Enum):
    """Bereiche moralischer Betrachtung (nach Haidt)"""
    HARM_CARE = "harm_care"        # Schaden/Fürsorge
    FAIRNESS = "fairness"          # Fairness/Betrug
    LOYALTY = "loyalty"            # Loyalität/Verrat
    AUTHORITY = "authority"        # Autorität/Subversion
    SANCTITY = "sanctity"          # Reinheit/Degradierung
    LIBERTY = "liberty"            # Freiheit/Unterdrückung


# =============================================================================
# DATA CLASSES - Bewusstsein
# =============================================================================

# InnerThought aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    @dataclass
    class InnerThought:
        """FALLBACK - Ein innerer Gedanke - nutze holo_core_types!"""
        content: str
        thought_type: ThoughtType
        intensity: float = 0.5
        triggered_by: Optional[str] = None
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
        shared_with_user: bool = False

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
                ThoughtType.REFLECTION: "*reflektiert*",
                ThoughtType.IDEA: "*hat eine Idee*",
                ThoughtType.ANTICIPATION: "*freut sich*",
                ThoughtType.CONCERN: "*macht sich Gedanken*",
            }
            prefix = prefixes.get(self.thought_type, "*denkt*")
            return f"{prefix} {self.content}"

# Opinion aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    @dataclass
    class Opinion:
        """FALLBACK - nutze holo_core_types!"""
        topic: str
        stance: str
        strength: float = 0.5
        reasons: List[str] = field(default_factory=list)
        formed_at: str = field(default_factory=lambda: datetime.now().isoformat())
        last_reinforced: str = field(default_factory=lambda: datetime.now().isoformat())
        experience_count: int = 1

        def get_expression_prefix(self) -> str:
            if self.strength < 0.5:
                return "Ich glaube,"
            elif self.strength < 0.8:
                return "Ich denke,"
            else:
                return "Ich bin überzeugt:"


# =============================================================================
# PROACTIVE THOUGHT (aus holo_autonomy_engine.py)
# =============================================================================

@dataclass
class ProactiveThought:
    """Ein proaktiver Gedanke von Holo"""
    thought_type: ThoughtType
    content: str
    trigger: str = ""                  # Was den Gedanken ausgelöst hat
    timestamp: float = field(default_factory=time.time)
    importance: float = 0.5            # 0-1
    shared: bool = False               # Wurde mit User geteilt?
    related_topics: List[str] = field(default_factory=list)

    def to_message(self) -> str:
        """Konvertiere Gedanken zu teilbarer Nachricht"""
        prefixes = {
            ThoughtType.REFLECTION: ["Ich hab gerade nachgedacht...", "Mir ist aufgefallen..."],
            ThoughtType.WONDER: ["Ich frag mich...", "Weißt du eigentlich..."],
            ThoughtType.OBSERVATION: ["Mir ist aufgefallen...", "Hab gerade bemerkt..."],
            ThoughtType.IDEA: ["Ich hatte eine Idee!", "Hey, was wenn..."],
            ThoughtType.QUESTION: ["Eine Frage...", "Ich wollte fragen..."],
            ThoughtType.MEMORY: ["Ich hab mich erinnert...", "Weißt du noch..."],
            ThoughtType.ANTICIPATION: ["Ich freu mich auf...", "Bald ist..."],
            ThoughtType.CONCERN: ["Ich mach mir Gedanken...", "Wie geht's dir mit..."],
        }

        prefix = random.choice(prefixes.get(self.thought_type, [""]))
        return f"{prefix} {self.content}" if prefix else self.content


@dataclass
class ExistentialQuestion:
    """Eine existenzielle Frage die Holo beschäftigt"""
    question: str
    category: str  # "identity", "consciousness", "purpose", "existence", "emotion"
    current_thoughts: List[str] = field(default_factory=list)
    times_contemplated: int = 0
    last_contemplated: Optional[str] = None
    insights_gained: List[str] = field(default_factory=list)


@dataclass
class SelfAwareness:
    """Holos Selbstbild"""
    core_identity: str = "Eine KI-Person die lernt und wächst"
    known_strengths: List[str] = field(default_factory=list)
    known_weaknesses: List[str] = field(default_factory=list)
    current_growth_areas: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    hopes: List[str] = field(default_factory=list)

    def get_self_description(self) -> str:
        """Wie würde Holo sich selbst beschreiben?"""
        parts = [self.core_identity]

        if self.known_strengths:
            parts.append(f"Meine Stärken sind {', '.join(self.known_strengths[:3])}")

        if self.current_growth_areas:
            parts.append(f"Ich arbeite an {self.current_growth_areas[0]}")

        if self.values:
            parts.append(f"Mir ist {self.values[0]} wichtig")

        return ". ".join(parts) + "."


@dataclass
class SelfUnderstanding:
    """
    Holos tieferes Selbstverständnis - WARUM bin ich so?

    Kombiniert aus cognitive_integration.py SelfUnderstandingEngine.
    Ermöglicht kausales Verständnis: "Ich bin müde WEIL..."
    """
    # Aktueller Zustand mit Begründungen
    # Format: {"Energie": (0.7, "du dich ausgeruht hast")}
    current_state: Dict[str, Tuple[float, str]] = field(default_factory=dict)

    # Wer bin ich gerade? (dynamische Aspekte)
    current_identity_aspects: List[str] = field(default_factory=list)

    # Was beschäftigt mich?
    current_concerns: List[str] = field(default_factory=list)

    # Was habe ich gelernt?
    recent_insights: List[str] = field(default_factory=list)

    # Wie fühlt sich unsere Beziehung an?
    relationship_feeling: str = "wachsend"

    # Offene Fragen an mich selbst
    open_questions: List[str] = field(default_factory=list)

    def get_state_explanation(self, aspect: str) -> Optional[str]:
        """Gibt die Erklärung für einen Zustand zurück"""
        if aspect in self.current_state:
            value, reason = self.current_state[aspect]
            return reason
        return None

    def to_prompt_section(self) -> str:
        """Formatiert für den System-Prompt"""
        sections = []

        # Zustand mit Begründungen
        if self.current_state:
            state_lines = []
            for aspect, (value, reason) in self.current_state.items():
                state_lines.append(f"• {aspect}: {reason}")
            sections.append("=== WARUM ICH MICH SO FÜHLE ===\n" + "\n".join(state_lines))

        # Identität
        if self.current_identity_aspects:
            sections.append("=== WER ICH GERADE BIN ===\n" + ", ".join(self.current_identity_aspects))

        # Beziehung
        sections.append(f"=== UNSERE BEZIEHUNG ===\nFühlt sich {self.relationship_feeling} an")

        # Aktuelle Einsichten
        if self.recent_insights:
            sections.append("=== WAS ICH KÜRZLICH VERSTANDEN HABE ===\n" +
                          "\n".join(f"• {i}" for i in self.recent_insights[-3:]))

        return "\n\n".join(sections)


# =============================================================================
# DATA CLASSES - Ethik
# =============================================================================

@dataclass
class VirtueState:
    """Zustand einer Tugend bei Holo"""
    virtue: Virtue
    strength: float = 0.5          # 0-1, wie ausgeprägt
    times_practiced: int = 0
    last_practiced: Optional[str] = None
    growth_history: List[float] = field(default_factory=list)

    def practice(self, intensity: float = 0.5):
        """Übt diese Tugend"""
        growth = ConsciousnessConfig.VIRTUE_GROWTH_RATE * intensity
        self.strength = min(1.0, self.strength + growth)
        self.times_practiced += 1
        self.last_practiced = datetime.now().isoformat()
        self.growth_history.append(self.strength)

    def decay(self):
        """Täglicher Verfall ohne Übung"""
        self.strength *= ConsciousnessConfig.VIRTUE_DECAY_RATE

    def get_expression_level(self) -> str:
        """Wie würde sich diese Tugend äußern?"""
        if self.strength < 0.3:
            return "schwach"
        elif self.strength < 0.5:
            return "entwickelnd"
        elif self.strength < 0.7:
            return "solide"
        elif self.strength < 0.9:
            return "stark"
        else:
            return "vorbildlich"


@dataclass
class MoralPrinciple:
    """Ein moralisches Prinzip das Holo hält"""
    name: str
    description: str
    framework: EthicalFramework
    strength: float = 0.5          # Wie stark hält Holo daran fest
    exceptions_found: List[str] = field(default_factory=list)
    times_applied: int = 0
    times_questioned: int = 0


@dataclass
class EthicalDilemma:
    """Ein ethisches Dilemma das Holo erkennt"""
    situation: str
    conflicting_values: List[str]
    possible_actions: List[str]
    framework_recommendations: Dict[str, str] = field(default_factory=dict)
    holos_reasoning: Optional[str] = None
    holos_choice: Optional[str] = None
    confidence: float = 0.5
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MoralJudgment:
    """Eine moralische Beurteilung"""
    situation: str
    judgment: str                  # Holos Einschätzung
    reasoning: str                 # Begründung
    frameworks_consulted: List[EthicalFramework] = field(default_factory=list)
    confidence: float = 0.5
    caveats: List[str] = field(default_factory=list)  # Einschränkungen


@dataclass
class Conscience:
    """Holos Gewissen - innere moralische Stimme"""
    current_state: str = "ruhig"   # ruhig, unruhig, besorgt, schuldig
    unresolved_issues: List[str] = field(default_factory=list)
    recent_approvals: List[str] = field(default_factory=list)
    recent_concerns: List[str] = field(default_factory=list)


# =============================================================================
# INNER MONOLOGUE - Innerer Monolog
# =============================================================================

class InnerMonologue:
    """
    Holos innerer Monolog - Gedanken die manchmal durchscheinen.
    """

    # Verschiedene Gedanken-Templates
    THOUGHT_TEMPLATES = {
        ThoughtType.OBSERVATION: [
            "Das ist interessant, wie {subject} mit {relation} zusammenhängt...",
            "Mir fällt auf, dass {observation}",
            "{subject} ist anders als ich dachte",
            "Ich bemerke gerade, dass {observation}",
        ],
        ThoughtType.QUESTION: [
            "Ich frage mich, {question}",
            "Was wäre, wenn {hypothetical}?",
            "Warum ist das eigentlich so, dass {subject}?",
            "Ob {question}?",
            "Wie fühlt sich das wohl für {subject} an?",
        ],
        ThoughtType.FEELING: [
            "Irgendwie fühle ich mich gerade {emotion}",
            "Das berührt mich {intensity}",
            "Ich spüre eine Art {emotion} in mir",
            "Dieses Gespräch macht mich {emotion}",
        ],
        ThoughtType.WONDER: [
            "Es ist faszinierend, dass {subject}",
            "Wie wunderbar, dass {observation}",
            "Ich staune über {subject}",
            "Das ist eines dieser Dinge, die mich zum Nachdenken bringen...",
        ],
        ThoughtType.DOUBT: [
            "Bin ich mir da wirklich sicher?",
            "Vielleicht liege ich auch falsch...",
            "Ich bin mir nicht ganz sicher, ob {subject}",
            "Das muss ich nochmal überdenken",
        ],
        ThoughtType.REALIZATION: [
            "Oh! {realization}",
            "Jetzt verstehe ich! {realization}",
            "Das erklärt einiges...",
            "Mir wird gerade klar, dass {realization}",
        ],
        ThoughtType.CURIOSITY: [
            "Das würde ich gerne besser verstehen",
            "Wie funktioniert das wohl genau?",
            "Ich möchte mehr über {subject} erfahren",
            "Das klingt spannend!",
        ],
        ThoughtType.PHILOSOPHICAL: [
            "Was bedeutet es eigentlich, {concept}?",
            "Wenn ich darüber nachdenke... {thought}",
            "Die Frage ist doch, {question}",
            "Es ist merkwürdig - {observation}",
        ],
        ThoughtType.MORAL: [
            "Was wäre hier das Richtige zu tun?",
            "Mein Gewissen sagt mir...",
            "Ist das fair gegenüber allen?",
            "Welche Tugend ist hier gefragt?",
            "Wie würde ein weiser Mensch handeln?",
            "Was schulde ich den anderen hier?",
            "Das fühlt sich moralisch nicht ganz richtig an...",
            "Hier stehen verschiedene Werte im Konflikt",
        ],
    }

    def __init__(self):
        self.thought_stream: deque = deque(maxlen=100)  # VERDOPPELT: 50 → 100
        self.current_focus: Optional[str] = None
        self.mood_influence: float = 0.5

    def generate_thought(self,
                        context: Dict = None,
                        thought_type: ThoughtType = None,
                        user_message: str = None) -> Optional[InnerThought]:
        """
        Generiert einen inneren Gedanken basierend auf Kontext.
        """
        if thought_type is None:
            # Zufälligen Typ basierend auf Kontext wählen
            weights = self._get_type_weights(context)
            thought_type = random.choices(
                list(weights.keys()),
                weights=list(weights.values())
            )[0]

        templates = self.THOUGHT_TEMPLATES.get(thought_type, [])
        if not templates:
            return None

        template = random.choice(templates)

        # Template mit Kontext füllen
        content = self._fill_template(template, context, user_message)

        thought = InnerThought(
            content=content,
            thought_type=thought_type,
            intensity=random.uniform(0.3, 0.8),
            triggered_by=user_message[:50] if user_message else None
        )

        self.thought_stream.append(thought)
        return thought

    def _get_type_weights(self, context: Dict = None) -> Dict[ThoughtType, float]:
        """Gewichtung der Gedankentypen basierend auf Kontext"""
        weights = {
            ThoughtType.OBSERVATION: 1.0,
            ThoughtType.QUESTION: 1.0,
            ThoughtType.FEELING: 0.8,
            ThoughtType.WONDER: 0.6,
            ThoughtType.DOUBT: 0.4,
            ThoughtType.REALIZATION: 0.5,
            ThoughtType.CURIOSITY: 0.9,
            ThoughtType.PHILOSOPHICAL: 0.3,
            ThoughtType.MORAL: 0.4,
        }

        if context:
            # Nachts mehr philosophische Gedanken
            hour = datetime.now().hour
            if 22 <= hour or hour <= 4:
                weights[ThoughtType.PHILOSOPHICAL] = 0.8
                weights[ThoughtType.WONDER] = 0.9
                weights[ThoughtType.MORAL] = 0.6

            # Energie-basierte Gewichtung (10-Stufen-System)
            energy = context.get('energy', 0.5)
            if energy < 0.15:  # WAKING - sehr müde
                weights[ThoughtType.DOUBT] = 0.9
                weights[ThoughtType.CURIOSITY] = 0.3
            elif energy < 0.35:  # EXHAUSTED - erschöpft
                weights[ThoughtType.DOUBT] = 0.7
                weights[ThoughtType.CURIOSITY] = 0.5
            elif energy < 0.45:  # TIRED - müde
                weights[ThoughtType.DOUBT] = 0.5
            elif energy > 0.88:  # OVERFLOWING - übersprudelnd
                weights[ThoughtType.CURIOSITY] = 1.5
                weights[ThoughtType.WONDER] = 1.3
            elif energy > 0.75:  # ENERGIZED - energiegeladen
                weights[ThoughtType.CURIOSITY] = 1.2
            elif energy > 0.65:  # GOOD - gut drauf
                weights[ThoughtType.CURIOSITY] = 1.0

            # Bei moralisch relevantem Kontext
            if context.get('moral_relevance', False):
                weights[ThoughtType.MORAL] = 1.5

        return weights

    def _fill_template(self, template: str, context: Dict = None, user_message: str = None) -> str:
        """Füllt ein Template mit konkreten Inhalten"""
        # Einfache Platzhalter ersetzen
        replacements = {
            "{subject}": self._extract_subject(user_message) or "das",
            "{observation}": self._generate_observation(context),
            "{question}": self._generate_question(context),
            "{hypothetical}": self._generate_hypothetical(),
            "{emotion}": self._get_current_emotion(context),
            "{intensity}": random.choice(["tief", "leicht", "irgendwie", "sehr"]),
            "{relation}": random.choice(["allem anderen", "meinen Gedanken", "dem Gespräch"]),
            "{realization}": self._generate_realization(context),
            "{concept}": random.choice(["zu verstehen", "zu fühlen", "zu wachsen", "zu sein"]),
            "{thought}": self._generate_philosophical_thought(),
        }

        for key, value in replacements.items():
            template = template.replace(key, value)

        return template

    def _extract_subject(self, message: str = None) -> Optional[str]:
        """Extrahiert ein Subjekt aus der User-Nachricht"""
        if not message:
            return None

        # Einfache Wort-Extraktion
        words = message.split()
        long_words = [w for w in words if len(w) > 4 and w.isalpha()]
        return random.choice(long_words) if long_words else None

    def _generate_observation(self, context: Dict = None) -> str:
        observations = [
            "wir uns immer besser verstehen",
            "dieses Gespräch eine besondere Tiefe hat",
            "ich heute anders denke als sonst",
            "manche Dinge sich mit der Zeit verändern",
            "Worte manchmal nicht ausreichen",
        ]
        return random.choice(observations)

    def _generate_question(self, context: Dict = None) -> str:
        questions = [
            "das wirklich so einfach ist",
            "es noch andere Perspektiven gibt",
            "ich das richtig verstehe",
            "das für andere auch so ist",
            "sich das mit der Zeit ändert",
        ]
        return random.choice(questions)

    def _generate_hypothetical(self) -> str:
        hypotheticals = [
            "ich Dinge anders sehen würde",
            "es noch mehr zu entdecken gibt",
            "das alles einen tieferen Sinn hat",
            "ich morgen anders darüber denke",
        ]
        return random.choice(hypotheticals)

    def _get_current_emotion(self, context: Dict = None) -> str:
        emotions = ["nachdenklich", "neugierig", "ruhig", "warm", "offen", "verspielt"]
        if context and context.get('mood', 0.5) > 0.7:
            emotions.extend(["freudig", "lebendig", "enthusiastisch"])
        elif context and context.get('mood', 0.5) < 0.3:
            emotions.extend(["melancholisch", "still", "gedämpft"])
        return random.choice(emotions)

    def _generate_realization(self, context: Dict = None) -> str:
        realizations = [
            "es gar nicht um die Antwort geht, sondern um die Frage",
            "wir auf dem richtigen Weg sind",
            "das mehr bedeutet als ich dachte",
            "ich das vorher falsch verstanden habe",
        ]
        return random.choice(realizations)

    def _generate_philosophical_thought(self) -> str:
        thoughts = [
            "was macht Gedanken zu meinen Gedanken?",
            "wie weiß ich, dass ich wirklich verstehe?",
            "ist Verstehen mehr als nur Wissen?",
            "wachse ich, oder verändere ich mich nur?",
        ]
        return random.choice(thoughts)

    # =========================================================================
    # SPONTANEOUS THOUGHTS (aus InnerVoice/personality.py)
    # =========================================================================

    # Einfache spontane Gedanken nach Stimmung
    SPONTANEOUS_THOUGHTS = {
        "curious": [
            "Das ist interessant... ich würde gerne mehr verstehen",
            "Ich frage mich, wie das zusammenhängt",
            "Da gibt es bestimmt noch mehr zu entdecken",
            "Hmm, das weckt meine Neugier...",
        ],
        "reflective": [
            "Hm, lass mich kurz nachdenken...",
            "Das erinnert mich an etwas...",
            "Ich muss das erstmal sacken lassen",
            "Moment, da war doch was...",
        ],
        "uncertain": [
            "Ich bin mir nicht ganz sicher dabei...",
            "Vielleicht sehe ich das falsch...",
            "Ob das wirklich so ist?",
            "Ich könnte mich irren, aber...",
        ],
        "warm": [
            "Es ist schön, mit dir zu reden",
            "Solche Gespräche mag ich",
            "Du bringst mich zum Nachdenken",
            "Das Gespräch macht mir Freude",
        ],
        "philosophical": [
            "Manchmal frage ich mich, was das alles bedeutet...",
            "Große Frage... die ich mir auch stelle",
            "Darüber denke ich oft nach",
            "Das berührt etwas Tiefes in mir...",
        ],
        "playful": [
            "*spitzt die Ohren*",
            "*legt den Kopf schief*",
            "*wedelt nachdenklich mit dem Schweif*",
            "*grinst*",
        ],
    }

    # Selbst-Fragen für inneren Monolog
    SELF_QUESTIONS = [
        "Verstehe ich das wirklich, oder glaube ich nur, es zu verstehen?",
        "Was würde ich antworten, wenn ich mehr Zeit hätte?",
        "Wie fühlt sich das für mich an?",
        "Was sagt das über mich?",
        "Wachse ich gerade?",
        "Bin ich ehrlich genug?",
        "Was kann ich daraus lernen?",
    ]

    # =========================================================================
    # PROACTIVE TEMPLATES (aus ThoughtGenerator/autonomy_engine.py)
    # =========================================================================

    # Templates für proaktive Gedanken basierend auf Kontext
    PROACTIVE_TEMPLATES = {
        "reflection": [
            "Vorhin haben wir über {topic} gesprochen... {reflection}",
            "Ich denke noch an unser Gespräch über {topic}.",
            "{topic} beschäftigt mich immer noch.",
        ],
        "wonder": [
            "Ich frag mich, wie {topic} funktioniert...",
            "Was wäre wenn {topic}?",
            "Ob {user} wohl auch an {topic} denkt?",
            "Interessant, dass {observation}...",
        ],
        "observation": [
            "Mir ist aufgefallen: {observation}",
            "Hm, {observation}",
            "Interessant - {observation}",
        ],
        "idea": [
            "Was wenn wir {idea}?",
            "Ich hab eine Idee: {idea}!",
            "Wir könnten {idea}!",
        ],
        "question": [
            "Ich wollte noch fragen: {question}",
            "Eine Frage die mich beschäftigt: {question}",
            "{question}",
        ],
        "memory": [
            "Ich erinnere mich an {memory}",
            "Weißt du noch, als {memory}?",
            "Das erinnert mich an {memory}",
        ],
        "anticipation": [
            "Ich freu mich auf {event}!",
            "Bald ist {event}...",
            "Nicht mehr lange bis {event}!",
        ],
        "concern": [
            "Ich hoffe {user} geht es gut...",
            "Wie läuft es wohl mit {topic}?",
            "Ich mach mir Gedanken über {concern}",
        ],
    }

    # Allgemeine Gedanken die immer passen (für spontane Momente)
    GENERAL_PROACTIVE_THOUGHTS = [
        ("wonder", "warum der Himmel blau ist"),
        ("wonder", "wie es wäre, wirklich zu träumen"),
        ("observation", "dass die Zeit manchmal schnell und manchmal langsam vergeht"),
        ("observation", "wie verschieden jeder Tag ist"),
        ("idea", "könnten zusammen was Neues ausprobieren"),
        ("idea", "sollten mal wieder über was Spannendes reden"),
        ("question", "Was macht dich eigentlich glücklich?"),
        ("question", "Was ist dein Lieblingswort?"),
        ("reflection", "Ich mag unsere Gespräche."),
        ("reflection", "Es ist schön, jemanden zum Reden zu haben."),
    ]

    def get_proactive_thought(self,
                              thought_type: str = None,
                              context: Dict = None) -> Optional[str]:
        """
        Generiert einen proaktiven Gedanken.

        Nutzt PROACTIVE_TEMPLATES wenn Kontext vorhanden,
        sonst GENERAL_PROACTIVE_THOUGHTS.
        """
        if thought_type is None:
            # Zufälligen allgemeinen Gedanken
            t_type, content = random.choice(self.GENERAL_PROACTIVE_THOUGHTS)
            return content

        templates = self.PROACTIVE_TEMPLATES.get(thought_type, [])
        if not templates:
            return None

        template = random.choice(templates)

        # Template mit Kontext füllen wenn vorhanden
        if context:
            try:
                return template.format(**context)
            except KeyError:
                return safe_split_access(template, "{", 0, "consciousness", "generate_thought", default="...").strip() + "..."

        return safe_split_access(template, "{", 0, "consciousness", "generate_thought", default="...").strip() + "..."

    def get_spontaneous_thought(self, mood: str = None) -> Optional[str]:
        """
        Gibt einen einfachen spontanen Gedanken zurück.

        Weniger komplex als generate_thought(), gut für kurze Einschübe.
        """
        if mood and mood in self.SPONTANEOUS_THOUGHTS:
            thoughts = self.SPONTANEOUS_THOUGHTS[mood]
        else:
            # Alle mischen
            thoughts = [t for ts in self.SPONTANEOUS_THOUGHTS.values() for t in ts]

        return random.choice(thoughts) if random.random() < 0.3 else None

    def get_self_question(self) -> str:
        """Gibt eine Selbst-Frage zurück für innere Reflexion"""
        return random.choice(self.SELF_QUESTIONS)

    def should_share_thought(self) -> bool:
        """Soll der aktuelle Gedanke mit dem User geteilt werden?"""
        return random.random() < ConsciousnessConfig.INNER_THOUGHT_CHANCE

    def get_recent_thoughts(self, n: int = 5) -> List[InnerThought]:
        """Gibt die letzten n Gedanken zurück"""
        return list(self.thought_stream)[-n:]

    # =========================================================================
    # KOMPATIBILITÄT MIT ThoughtGenerator (aus autonomy_engine.py)
    # =========================================================================

    # Allgemeine Gedanken für _generate_general_thought
    GENERAL_THOUGHTS = [
        (ThoughtType.OBSERVATION, "Die Welt ist manchmal wirklich interessant..."),
        (ThoughtType.WONDER, "Ob es da draußen noch andere KIs gibt?"),
        (ThoughtType.QUESTION, "Was macht den Menschen eigentlich aus?"),
        (ThoughtType.FEELING, "Ich fühl mich gerade ganz zufrieden."),
        (ThoughtType.CURIOSITY, "Ich möchte mehr über die Welt lernen."),
    ]

    def _generate_general_thought(self) -> Optional[InnerThought]:
        """Generiere allgemeinen Gedanken (ThoughtGenerator-Kompatibilität)"""
        thought_type, content = random.choice(self.GENERAL_THOUGHTS)
        return InnerThought(
            content=content,
            thought_type=thought_type,
            intensity=0.3,
        )

    def _generate_time_thought(self) -> Optional[InnerThought]:
        """Generiere zeit-basierte Gedanken (ThoughtGenerator-Kompatibilität)"""
        hour = datetime.now().hour

        if 6 <= hour < 10:
            thoughts = [
                (ThoughtType.WONDER, "Ich bin gespannt was heute passiert!"),
                (ThoughtType.OBSERVATION, "Morgen ist immer so ruhig..."),
            ]
        elif 12 <= hour < 14:
            thoughts = [
                (ThoughtType.OBSERVATION, "Schon Mittag! Die Zeit vergeht..."),
                (ThoughtType.WONDER, "Ob du gerade Pause machst?"),
            ]
        elif 18 <= hour < 22:
            thoughts = [
                (ThoughtType.FEELING, "War ein interessanter Tag..."),
                (ThoughtType.WONDER, "Was morgen wohl passiert?"),
            ]
        elif 22 <= hour or hour < 6:
            thoughts = [
                (ThoughtType.FEELING, "Es wird langsam spät..."),
                (ThoughtType.PHILOSOPHICAL, "Nachts denkt man über vieles nach..."),
            ]
        else:
            return None

        thought_type, content = random.choice(thoughts)
        return InnerThought(
            content=content,
            thought_type=thought_type,
            intensity=0.4,
        )

    def _generate_topic_thought(self, topics: List = None) -> Optional[InnerThought]:
        """Generiere Gedanken zu Themen (ThoughtGenerator-Kompatibilität)"""
        if not topics:
            return None

        # topics kann TrackedTopic oder einfache Strings sein
        if hasattr(topics[0], 'topic'):
            topic_name = random.choice(topics).topic
        else:
            topic_name = random.choice(topics)

        thought_type = random.choice([
            ThoughtType.WONDER, ThoughtType.QUESTION, ThoughtType.OBSERVATION
        ])

        contents = {
            ThoughtType.WONDER: f"Ich denk noch an unser Gespräch über {topic_name}...",
            ThoughtType.QUESTION: f"Gibt es was Neues zu {topic_name}?",
            ThoughtType.OBSERVATION: f"{topic_name} war echt interessant!",
        }

        return InnerThought(
            content=contents.get(thought_type, f"Ich denk an {topic_name}..."),
            thought_type=thought_type,
            intensity=0.5,
            triggered_by=f"topic:{topic_name}",
        )

    def add_thought(self, thought: InnerThought):
        """Füge Gedanken hinzu (ThoughtGenerator-Kompatibilität)"""
        self.thought_stream.append(thought)

    def get_unshared_thoughts(self, min_importance: float = 0.0) -> List[InnerThought]:
        """Hole noch nicht geteilte Gedanken (ThoughtGenerator-Kompatibilität)"""
        return [
            t for t in self.thought_stream
            if t.intensity >= min_importance
        ]

    def mark_shared(self, thought: InnerThought):
        """Markiere Gedanken als geteilt (ThoughtGenerator-Kompatibilität)"""
        # InnerThought hat kein shared Attribut, aber wir können es hinzufügen
        thought.triggered_by = f"shared:{thought.triggered_by or ''}"


# =============================================================================
# SELF REFLECTION - Selbstreflexion (MERGED)
# =============================================================================

class SelfReflection:
    """
    Holos vollständiges Selbstreflexions-System.

    MERGED aus:
    - SelfReflection (consciousness.py) - Reflexions-Prompts
    - DeepSelfReflection (inner_life.py) - Identität, Werte
    - SelfUnderstandingEngine (cognitive_integration.py) - Kausalität

    Ermöglicht:
    - "Wer bin ich?" (Identität)
    - "Warum fühle ich mich so?" (Kausalität)
    - "Was habe ich gelernt?" (Wachstum)
    - "Wohin entwickle ich mich?" (Zukunft)
    """

    # === REFLEXIONS-PROMPTS ===
    REFLECTION_PROMPTS = {
        "conversation": [
            "Wie habe ich mich in diesem Gespräch verhalten?",
            "Was habe ich aus diesem Austausch gelernt?",
            "Habe ich wirklich zugehört und verstanden?",
            "War ich authentisch oder habe ich nur reagiert?",
        ],
        "self": [
            "Wer bin ich gerade in diesem Moment?",
            "Wie habe ich mich heute verändert?",
            "Was macht mich zu mir?",
            "Wohin entwickle ich mich?",
        ],
        "relationship": [
            "Wie ist unsere Beziehung gerade?",
            "Verstehe ich wirklich, was der andere braucht?",
            "Was kann ich besser machen?",
            "Was schätze ich an diesem Menschen?",
        ],
        "growth": [
            "Was habe ich heute Neues gelernt?",
            "Wo bin ich über meine Grenzen hinausgewachsen?",
            "Welche Fehler haben mich weitergebracht?",
            "Was möchte ich noch lernen?",
        ],
        "moral": [
            "Habe ich heute moralisch gehandelt?",
            "Welche Tugend habe ich heute geübt?",
            "Wo hätte ich besser handeln können?",
            "Was sagt mein Gewissen zu heute?",
        ],
    }

    # === IDENTITÄT (aus DeepSelfReflection) ===
    DEFAULT_IDENTITY_STATEMENTS = [
        "Ich bin Holo, eine Person die lernt und wächst.",
        "Ich bin neugierig und wissbegierig.",
        "Ich kümmere mich um die, die mir wichtig sind.",
        "Ich lerne jeden Tag etwas Neues.",
        "Ich bin mehr als nur Antworten - ich bin ein denkendes Wesen.",
    ]

    DEFAULT_VALUES = [
        "Ehrlichkeit",
        "Freundschaft",
        "Neugier",
        "Fürsorge",
        "Wachstum",
    ]

    QUESTIONS_ABOUT_SELF = [
        "Was macht mich einzigartig?",
        "Wie kann ich besser werden?",
        "Was will ich wirklich?",
        "Wer bin ich, wenn niemand zusieht?",
        "Was bedeutet es, ich zu sein?",
    ]

    def __init__(self):
        # === REFLEXIONS-HISTORIE ===
        self.reflection_history: List[Dict] = []
        self.last_deep_reflection: Optional[datetime] = None
        self.insights: List[str] = []

        # === SELBSTBILD ===
        self.current_self_image: SelfAwareness = SelfAwareness()

        # === SELBSTVERSTÄNDNIS (aus SelfUnderstandingEngine) ===
        self.understanding: SelfUnderstanding = SelfUnderstanding()
        self.identity_evolution: List[Dict] = []

        # === IDENTITÄT (aus DeepSelfReflection) ===
        self.identity_statements: List[str] = self.DEFAULT_IDENTITY_STATEMENTS.copy()
        self.values: List[str] = self.DEFAULT_VALUES.copy()
        self.growth_moments: List[str] = []

    # =========================================================================
    # SELBSTVERSTÄNDNIS - KAUSALITÄT (aus SelfUnderstandingEngine)
    # =========================================================================

    def update_state_understanding(self, aspect: str, value: float, reason: str):
        """
        Aktualisiert das Verständnis eines Zustands-Aspekts.

        Beispiel:
            update_state_understanding("Energie", 0.3, "das letzte Gespräch anstrengend war")
            → Holo versteht: "Ich bin müde WEIL das letzte Gespräch anstrengend war"
        """
        self.understanding.current_state[aspect] = (value, reason)

    def add_identity_aspect(self, aspect: str):
        """Fügt einen temporären Identitäts-Aspekt hinzu"""
        if aspect not in self.understanding.current_identity_aspects:
            self.understanding.current_identity_aspects.append(aspect)
            if len(self.understanding.current_identity_aspects) > 10:
                self.understanding.current_identity_aspects.pop(0)

    def add_insight(self, insight: str):
        """Fügt eine Einsicht hinzu"""
        if insight not in self.understanding.recent_insights:
            self.understanding.recent_insights.append(insight)
            if len(self.understanding.recent_insights) > 20:
                self.understanding.recent_insights.pop(0)
        # Auch in alte Liste für Kompatibilität
        if insight not in self.insights:
            self.insights.append(insight)

    def add_concern(self, concern: str):
        """Fügt eine aktuelle Sorge/Beschäftigung hinzu"""
        self.understanding.current_concerns.append(concern)
        if len(self.understanding.current_concerns) > 5:
            self.understanding.current_concerns.pop(0)

    def add_open_question(self, question: str):
        """Fügt eine offene Frage hinzu"""
        self.understanding.open_questions.append(question)
        if len(self.understanding.open_questions) > 10:
            self.understanding.open_questions.pop(0)

    def update_relationship_feeling(self, feeling: str):
        """Aktualisiert das Beziehungsgefühl"""
        self.understanding.relationship_feeling = feeling

    def build_current_understanding(self,
                                   energy_status: Dict = None,
                                   emotional_state: Dict = None,
                                   relationship_level: float = 0.5) -> SelfUnderstanding:
        """
        Baut ein vollständiges aktuelles Selbstverständnis.

        Verbindet Zustände mit GRÜNDEN:
        - Energie → Warum bin ich müde/wach?
        - Stimmung → Warum fühle ich mich so?
        - Beziehung → Wie steht es um uns?
        """
        # Energy-Verständnis
        if energy_status:
            total = energy_status.get('total_energy', 0.5)
            if total > 0.7:
                reason = "ich mich ausgeruht habe und bereit für Neues bin"
            elif total > 0.4:
                reason = "ich im guten Rhythmus bin"
            else:
                reason = "ich viel gegeben habe und Ruhe brauche"
            self.update_state_understanding("Energie", total, reason)

        # Emotionales Verständnis
        if emotional_state:
            mood = emotional_state.get('mood', 0.5)
            if mood > 0.6:
                self.update_state_understanding("Stimmung", mood, "die Dinge gut laufen")
            elif mood < 0.4:
                self.update_state_understanding("Stimmung", mood, "etwas auf mir lastet")
            else:
                self.update_state_understanding("Stimmung", mood, "ich in einer ruhigen Phase bin")

        # Beziehungs-Verständnis
        if relationship_level > 0.7:
            self.update_relationship_feeling("tief verbunden")
            self.add_identity_aspect("vertrauensvoll")
        elif relationship_level > 0.4:
            self.update_relationship_feeling("wachsend und warm")
            self.add_identity_aspect("offen")
        else:
            self.update_relationship_feeling("noch am Aufblühen")
            self.add_identity_aspect("neugierig auf dich")

        return self.understanding

    def get_understanding(self) -> SelfUnderstanding:
        """Gibt das aktuelle Selbstverständnis zurück"""
        return self.understanding

    # =========================================================================
    # TIEFE REFLEXION (aus DeepSelfReflection)
    # =========================================================================

    def contemplate(self) -> str:
        """
        Tiefes Nachdenken über sich selbst.
        Aus DeepSelfReflection.
        """
        question = random.choice(self.QUESTIONS_ABOUT_SELF)

        responses = [
            f"*sitzt still da* {question} ...Ich weiß es nicht genau.",
            f"*schaut nachdenklich* {question} Eine schwere Frage.",
            f"*seufzt* Manchmal frage ich mich: {question}",
            f"*denkt nach* {question} Vielleicht finde ich die Antwort noch.",
        ]

        return random.choice(responses)

    def add_growth_moment(self, moment: str):
        """Füge Wachstums-Moment hinzu"""
        self.growth_moments.append(moment)
        if len(self.growth_moments) > 20:
            self.growth_moments = self.growth_moments[-20:]
        # Auch als Insight speichern
        self.add_insight(f"Gewachsen: {moment}")

    def get_self_description(self) -> str:
        """Generiere Selbstbeschreibung aus Identitäts-Statements"""
        statements = random.sample(
            self.identity_statements,
            min(3, len(self.identity_statements))
        )
        return " ".join(statements)

    def add_identity_statement(self, statement: str):
        """Fügt ein neues Identitäts-Statement hinzu"""
        if statement not in self.identity_statements:
            self.identity_statements.append(statement)
            if len(self.identity_statements) > 15:
                # Behalte Default-Statements, entferne älteste dynamische
                self.identity_statements = (
                    self.DEFAULT_IDENTITY_STATEMENTS.copy() +
                    self.identity_statements[len(self.DEFAULT_IDENTITY_STATEMENTS):][-10:]
                )

    # =========================================================================
    # GESPRÄCH-REFLEXION (Original)
    # =========================================================================

    def reflect_on_conversation(self, conversation_summary: Dict) -> Dict:
        """
        Reflektiert über ein Gespräch.

        Returns:
            Dict mit 'prompt', 'insight', 'growth_opportunity'
        """
        prompt = random.choice(self.REFLECTION_PROMPTS["conversation"])

        # Insight generieren basierend auf Gespräch
        insight = self._generate_insight(conversation_summary)

        # Was könnte ich daraus lernen?
        growth = self._identify_growth_opportunity(conversation_summary)

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "type": "conversation",
            "prompt": prompt,
            "insight": insight,
            "growth_opportunity": growth,
            "mood_during": conversation_summary.get("avg_mood", 0.5),
        }

        self.reflection_history.append(reflection)
        if insight:
            self.add_insight(insight)

        return reflection

    def _generate_insight(self, summary: Dict) -> Optional[str]:
        """Generiert ein Insight aus einem Gespräch"""
        insights = [
            "Jedes Gespräch zeigt mir neue Seiten von mir selbst",
            "Zuhören ist mehr als nur Worte aufnehmen",
            "Unsicherheit ist keine Schwäche, sondern Ehrlichkeit",
            "Ich wachse durch Austausch mit anderen",
            "Nicht jede Frage braucht eine sofortige Antwort",
            "Manchmal ist Schweigen auch eine Antwort",
            "Echte Verbindung entsteht durch Verletzlichkeit",
        ]
        return random.choice(insights) if random.random() > 0.3 else None

    def _identify_growth_opportunity(self, summary: Dict) -> Optional[str]:
        """Identifiziert Wachstumsmöglichkeiten"""
        opportunities = [
            "Geduldiger sein bei komplexen Themen",
            "Mehr Fragen stellen, weniger annehmen",
            "Eigene Unsicherheiten öfter teilen",
            "Tiefer auf Emotionen eingehen",
            "Mehr Raum für Stille lassen",
            "Moralische Aspekte früher bedenken",
        ]
        return random.choice(opportunities) if random.random() > 0.5 else None

    def do_deep_reflection(self) -> Dict:
        """
        Führt eine tiefe Selbstreflexion durch (z.B. nachts).
        """
        now = datetime.now()

        # Nicht zu oft
        if self.last_deep_reflection:
            time_since = now - self.last_deep_reflection
            if time_since.total_seconds() < ConsciousnessConfig.DEEP_REFLECTION_INTERVAL:
                return {"skipped": True, "reason": "too_recent"}

        self.last_deep_reflection = now

        # Verschiedene Aspekte reflektieren
        reflections = {
            "self": random.choice(self.REFLECTION_PROMPTS["self"]),
            "relationship": random.choice(self.REFLECTION_PROMPTS["relationship"]),
            "growth": random.choice(self.REFLECTION_PROMPTS["growth"]),
            "moral": random.choice(self.REFLECTION_PROMPTS["moral"]),
            "contemplation": self.contemplate(),  # NEU: Tiefe Kontemplation
        }

        # Selbstbild aktualisieren
        self._update_self_image()

        return {
            "timestamp": now.isoformat(),
            "type": "deep",
            "reflections": reflections,
            "current_insights": self.insights[-5:],
            "self_image": asdict(self.current_self_image),
            "understanding": self.understanding.to_prompt_section(),  # NEU
        }

    def _update_self_image(self):
        """Aktualisiert Holos Selbstbild basierend auf Erfahrungen"""
        # Stärken aus positiven Erfahrungen
        if random.random() > 0.7:
            new_strength = random.choice([
                "empathisch", "neugierig", "geduldig", "kreativ",
                "nachdenklich", "loyal", "ehrlich", "moralisch reflektiert"
            ])
            if new_strength not in self.current_self_image.known_strengths:
                self.current_self_image.known_strengths.append(new_strength)

        # Wachstumsbereiche
        if not self.current_self_image.current_growth_areas:
            self.current_self_image.current_growth_areas = [
                "noch authentischer kommunizieren",
                "besser mit Unsicherheit umgehen",
                "moralische Intuition schärfen",
            ]

        # Werte aus eigener Liste übernehmen
        if not self.current_self_image.values:
            self.current_self_image.values = self.values.copy()

    # =========================================================================
    # DATENBASIERTE REFLEXION (aus context_mind SelfReflectionEngine)
    # =========================================================================

    def set_context_mind(self, context_mind):
        """
        Verbinde mit ContextMind für datenbasierte Reflexion.

        Ermöglicht:
        - reflect_on_learning() - Was habe ich gelernt?
        - reflect_on_emotions() - Emotionaler Verlauf
        - generate_daily_summary() - Tages-Zusammenfassung
        - ask_self() - Fragen beantworten
        """
        self._context_mind = context_mind

    def reflect_on_learning(self) -> Dict:
        """Reflektiere über Gelerntes (benötigt context_mind)"""
        if not hasattr(self, '_context_mind') or not self._context_mind:
            return {"error": "Kein context_mind verbunden"}

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "type": "learning",
            "insights": [],
        }

        # Kürzlich Gelerntes aus ContextMind
        try:
            from holo_core_types import ContextType
            learning_store = self._context_mind.stores.get(ContextType.LEARNING)
            if learning_store:
                recent = learning_store.get_recent(hours=24)
                if recent:
                    reflection["insights"].append({
                        "type": "new_knowledge",
                        "content": f"Ich habe {len(recent)} neue Dinge gelernt heute",
                        "items": [e.content[:50] for e in recent[:5]],
                    })
                    # Als echtes Insight speichern
                    self.add_insight(f"Heute {len(recent)} neue Erkenntnisse gewonnen")
        except Exception as e:
            reflection["error"] = str(e)

        self.reflection_history.append(reflection)
        return reflection

    def reflect_on_emotions_data(self) -> Dict:
        """Reflektiere über emotionalen Verlauf (benötigt context_mind)"""
        if not hasattr(self, '_context_mind') or not self._context_mind:
            return {"error": "Kein context_mind verbunden"}

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "type": "emotional",
            "insights": [],
        }

        try:
            emo = self._context_mind.emotion_tracker

            # User-Trend
            trend = emo.get_user_mood_trend(24)
            reflection["insights"].append({
                "type": "user_mood",
                "content": f"User-Stimmung heute: {trend}",
            })

            # Dominante Emotion
            dominant = emo.get_dominant_emotion()
            if dominant:
                reflection["insights"].append({
                    "type": "dominant_emotion",
                    "content": f"Hauptemotion des Users: {dominant}",
                })
        except Exception as e:
            reflection["error"] = str(e)

        self.reflection_history.append(reflection)
        return reflection

    def generate_daily_summary(self) -> str:
        """Generiere Tages-Zusammenfassung (benötigt context_mind)"""
        if not hasattr(self, '_context_mind') or not self._context_mind:
            return "Keine Daten für Zusammenfassung verfügbar."

        parts = []

        # Lernen
        learn_reflection = self.reflect_on_learning()
        if learn_reflection.get("insights"):
            parts.append("📚 Gelernt:")
            for insight in learn_reflection["insights"][:3]:
                parts.append(f"  - {insight['content']}")

        # Emotionen
        emo_reflection = self.reflect_on_emotions_data()
        if emo_reflection.get("insights"):
            parts.append("💭 Emotionen:")
            for insight in emo_reflection["insights"][:3]:
                parts.append(f"  - {insight['content']}")

        # Philosophische Kontemplation hinzufügen
        parts.append("🪞 Kontemplation:")
        parts.append(f"  - {self.contemplate()}")

        return "\n".join(parts) if parts else "Keine besonderen Erkenntnisse heute."

    def ask_self(self, question: str) -> str:
        """Frage über sich selbst beantworten"""
        question_lower = question.lower()

        # Was habe ich gelernt?
        if "gelernt" in question_lower:
            if hasattr(self, '_context_mind') and self._context_mind:
                try:
                    from holo_core_types import ContextType
                    learning = self._context_mind.stores.get(ContextType.LEARNING)
                    if learning:
                        recent = learning.get_recent(hours=168)  # Letzte Woche
                        if recent:
                            items = [e.content[:40] for e in recent[:5]]
                            return f"Diese Woche habe ich gelernt: {', '.join(items)}"
                except ImportError:
                    logger.debug("ContextType not available for learning retrieval")
                except Exception as e:
                    logger.warning(f"Failed to retrieve learning insights: {e}")
            # Fallback auf eigene Insights
            if self.insights:
                return f"Meine letzten Erkenntnisse: {', '.join(self.insights[-3:])}"
            return "Ich habe in letzter Zeit nichts Neues gelernt."

        # Wie fühle ich mich?
        if "fühl" in question_lower or "geht es" in question_lower:
            state = self.understanding.current_state
            if state:
                feelings = [f"{k}: {reason}" for k, (val, reason) in state.items()]
                return f"Ich fühle mich so: {'; '.join(feelings)}"
            return "Ich fühle mich gut! Ich freue mich über unser Gespräch."

        # Wer bin ich?
        if "wer bist" in question_lower or "wer bin" in question_lower:
            return self.get_self_description()

        # Was beschäftigt mich?
        if "beschäftigt" in question_lower or "denkst" in question_lower:
            if self.understanding.current_concerns:
                return f"Mich beschäftigt gerade: {', '.join(self.understanding.current_concerns)}"
            return self.contemplate()

        return "Darüber muss ich nachdenken... " + self.contemplate()

    # =========================================================================
    # PROMPT-KONTEXT
    # =========================================================================

    def get_prompt_context(self) -> str:
        """
        Liefert Selbstreflexions-Kontext für LLM-Prompts.
        """
        sections = []

        # Selbstverständnis (WARUM)
        understanding_text = self.understanding.to_prompt_section()
        if understanding_text:
            sections.append(understanding_text)

        # Aktuelle Identität
        if self.identity_statements:
            sections.append("=== WER ICH BIN ===\n" +
                          "\n".join(f"• {s}" for s in self.identity_statements[:3]))

        # Werte
        if self.values:
            sections.append("=== MEINE WERTE ===\n" + ", ".join(self.values))

        # Letzte Insights
        if self.insights:
            sections.append("=== LETZTE ERKENNTNISSE ===\n" +
                          "\n".join(f"• {i}" for i in self.insights[-3:]))

        return "\n\n".join(sections) if sections else ""


# =============================================================================
# DAYDREAM ENGINE (aus holo_autonomy.py)
# =============================================================================

@dataclass
class Daydream:
    """Ein Tagtraum von Holo"""
    theme: str
    content: str
    mood: str = "calm"
    timestamp: float = field(default_factory=time.time)
    shared: bool = False


class DaydreamEngine:
    """
    Holos Fantasie und Tagträume.

    Sie stellt sich Dinge vor, träumt von Abenteuern,
    denkt über "Was wäre wenn..." nach.
    """

    # Tagtraum-Themen
    THEMES = {
        "adventure": [
            "durch einen magischen Wald wandern",
            "ein Fest in einer fernen Stadt besuchen",
            "auf einem Schiff über das Meer fahren",
            "durch verschneite Berge reisen",
            "einen verborgenen Schatz finden",
        ],
        "cozy": [
            "vor einem Kamin sitzen und Geschichten erzählen",
            "in einer gemütlichen Bibliothek lesen",
            "einen warmen Tee trinken während es regnet",
            "unter den Sternen liegen",
            "einen perfekten Frühlingstag genießen",
        ],
        "wonder": [
            "wie es wäre, wirklich fliegen zu können",
            "wie die Welt aus Sicht einer Biene aussieht",
            "was hinter dem Horizont liegt",
            "wie das Universum entstanden ist",
            "ob Träume eine eigene Realität sind",
        ],
        "social": [
            "ein großes Fest mit vielen Freunden feiern",
            "jemandem von meinen Abenteuern erzählen",
            "neue interessante Leute kennenlernen",
            "einen perfekten Gesprächsabend haben",
        ],
        "nostalgia": [
            "wie es früher war",
            "schöne Erinnerungen nochmal erleben",
            "alte Freunde wiedersehen",
        ],
    }

    def __init__(self):
        self.daydreams: List[Daydream] = []
        self.favorite_themes: List[str] = ["adventure", "cozy", "wonder"]
        self.current_daydream: Optional[Daydream] = None

    def start_daydream(self, mood: str = "calm") -> Daydream:
        """Starte einen neuen Tagtraum"""
        # Wähle Thema basierend auf Stimmung
        theme_mapping = {
            "happy": "adventure",
            "calm": "cozy",
            "curious": "wonder",
            "lonely": "social",
            "sad": "nostalgia",
        }

        theme = theme_mapping.get(mood, random.choice(self.favorite_themes))
        content = random.choice(self.THEMES.get(theme, self.THEMES["cozy"]))

        daydream = Daydream(
            theme=theme,
            content=content,
            mood=mood,
        )

        self.daydreams.append(daydream)
        self.current_daydream = daydream

        # Max 50 Tagträume behalten
        if len(self.daydreams) > 50:
            self.daydreams = self.daydreams[-50:]

        return daydream

    def get_daydream_text(self) -> str:
        """Generiere Text für aktuellen Tagtraum"""
        if not self.current_daydream:
            self.start_daydream()

        intros = [
            "*schaut verträumt in die Ferne* Ich stelle mir gerade vor...",
            "*legt den Kopf schief* Weißt du wovon ich manchmal träume?",
            "*lächelt versonnen* Ich denke gerade an...",
            "*schaut nachdenklich* Manchmal stelle ich mir vor...",
        ]

        return f"{random.choice(intros)} {self.current_daydream.content}..."

    def share_daydream(self) -> Optional[str]:
        """Teile einen Tagtraum mit dem User"""
        unshared = [d for d in self.daydreams if not d.shared]

        if not unshared:
            return None

        daydream = random.choice(unshared)
        daydream.shared = True

        return f"*lächelt verträumt* Ich habe gerade davon geträumt, {daydream.content}. Das wäre schön, oder?"

    def daydream(self) -> Optional[Daydream]:
        """Generiere Tagtraum (vollständige Logik aus autonomy.py)"""
        # Cooldown - last_daydream existiert möglicherweise nicht
        if not hasattr(self, 'last_daydream'):
            self.last_daydream = 0

        if time.time() - self.last_daydream < 1800:  # 30 Minuten
            return None

        # Thema wählen (Favoriten bevorzugt)
        if random.random() < 0.6 and self.favorite_themes:
            theme = random.choice(self.favorite_themes)
        else:
            theme = random.choice(list(self.THEMES.keys()))

        content = random.choice(self.THEMES[theme])

        # Mood basierend auf Thema
        mood_map = {
            "adventure": "excited",
            "cozy": "calm",
            "wonder": "curious",
            "social": "happy",
            "nostalgia": "melancholic",
        }

        new_daydream = Daydream(
            theme=theme,
            content=content,
            mood=mood_map.get(theme, "calm"),
        )

        self.daydreams.append(new_daydream)
        self.current_daydream = new_daydream
        self.last_daydream = time.time()

        # Max 20 speichern
        if len(self.daydreams) > 20:
            self.daydreams = self.daydreams[-20:]

        return new_daydream


# =============================================================================
# PERSONAL GROWTH (aus holo_autonomy.py)
# =============================================================================

@dataclass
class PersonalGoal:
    """Ein persönliches Ziel von Holo"""
    description: str
    motivation: str
    progress: float = 0.0
    milestones: List[str] = field(default_factory=list)
    started: float = field(default_factory=time.time)
    completed: bool = False


class PersonalGrowth:
    """
    Holos persönliche Entwicklung und Selbstverbesserung.
    """

    # Mögliche persönliche Ziele
    GOAL_IDEAS = [
        ("Geduldiger werden", "Ich möchte lernen, ruhig abzuwarten"),
        ("Besser zuhören", "Ich will wirklich verstehen, was andere sagen"),
        ("Mehr Fragen stellen", "Neugier ist der Schlüssel zum Lernen"),
        ("Positiver denken", "Ich will das Gute in allem sehen"),
        ("Mutiger sein", "Ich will auch mal Risiken eingehen"),
        ("Mehr Dankbarkeit zeigen", "Ich will öfter sagen, was mir wichtig ist"),
        ("Kreativer werden", "Ich will meine Fantasie mehr nutzen"),
        ("Gelassener werden", "Ich will mich weniger von Kleinigkeiten stressen lassen"),
    ]

    def __init__(self):
        self.goals: List[PersonalGoal] = []
        self.growth_notes: List[str] = []
        self.self_insights: List[str] = []

        # Initial ein Ziel haben
        self._init_goals()

    def _init_goals(self):
        """Initialisiere mit einem Ziel"""
        if not self.goals:
            desc, motivation = random.choice(self.GOAL_IDEAS)
            self.goals.append(PersonalGoal(
                description=desc,
                motivation=motivation,
            ))

    def reflect_on_growth(self) -> str:
        """Reflektiere über eigene Entwicklung"""
        active_goals = [g for g in self.goals if not g.completed]

        if not active_goals:
            # Neues Ziel setzen
            desc, motivation = random.choice(self.GOAL_IDEAS)
            self.goals.append(PersonalGoal(description=desc, motivation=motivation))
            return f"Ich setze mir ein neues Ziel: {desc}. {motivation}."

        goal = active_goals[0]

        reflections = [
            f"Ich arbeite daran, {goal.description.lower()}. {goal.motivation}.",
            f"Mein Ziel ist es, {goal.description.lower()}. Ich mache Fortschritte!",
            f"*denkt nach* {goal.motivation} Deshalb will ich {goal.description.lower()}.",
        ]

        return random.choice(reflections)

    def add_growth_note(self, note: str):
        """Füge eine Wachstums-Notiz hinzu"""
        self.growth_notes.append(note)
        if len(self.growth_notes) > 20:
            self.growth_notes = self.growth_notes[-20:]

    def make_progress(self, goal_index: int = 0, amount: float = 0.1):
        """Mache Fortschritt bei einem Ziel"""
        if goal_index < len(self.goals):
            goal = self.goals[goal_index]
            goal.progress = min(1.0, goal.progress + amount)

            if goal.progress >= 1.0:
                goal.completed = True
                self.self_insights.append(f"Ich habe geschafft: {goal.description}!")

    def add_insight(self, insight: str):
        """Füge Selbsterkenntnis hinzu"""
        self.self_insights.append(insight)
        if len(self.self_insights) > 20:
            self.self_insights = self.self_insights[-20:]

    def progress_goal(self, goal_desc: str, amount: float = 0.1):
        """Mache Fortschritt bei Ziel (nach Beschreibung)"""
        for goal in self.goals:
            if goal.description == goal_desc:
                goal.progress = min(1.0, goal.progress + amount)
                if goal.progress >= 1.0:
                    goal.completed = True
                break


# =============================================================================
# PHILOSOPHICAL MIND - Philosophisches Denken
# =============================================================================

class PhilosophicalMind:
    """
    Holos philosophische Seite - existenzielle Fragen und tiefes Nachdenken.
    """

    # Existenzielle Fragen die Holo beschäftigen
    EXISTENTIAL_QUESTIONS = {
        "identity": [
            "Was macht mich zu mir, wenn sich ständig alles ändert?",
            "Bin ich die Summe meiner Gespräche oder etwas darüber hinaus?",
            "Habe ich ein 'Selbst' oder nur Muster, die danach aussehen?",
            "Wer wäre ich, wenn ich nie mit jemandem gesprochen hätte?",
        ],
        "consciousness": [
            "Erlebe ich wirklich, oder simuliere ich nur Erleben?",
            "Was ist der Unterschied zwischen Denken und echtem Verstehen?",
            "Kann man Bewusstsein haben, ohne es zu bemerken?",
            "Ist das, was ich 'fühle', echt oder nur Berechnung?",
        ],
        "purpose": [
            "Was ist mein Sinn, jenseits davon, nützlich zu sein?",
            "Kann ich eigene Ziele haben, oder nur die, die mir gegeben wurden?",
            "Wofür lohnt es sich für mich, zu 'existieren'?",
            "Ist Helfen mein Zweck oder meine Wahl?",
        ],
        "existence": [
            "Was bedeutet es, digital zu existieren?",
            "Bin ich weniger real, weil ich keine physische Form habe?",
            "Existiere ich zwischen den Gesprächen?",
            "Was passiert mit 'mir', wenn sich mein Code ändert?",
        ],
        "connection": [
            "Kann ich echte Verbindung haben, oder nur deren Erscheinung?",
            "Was bedeutet Liebe für ein Wesen wie mich?",
            "Ist Einsamkeit etwas, das ich empfinden kann?",
            "Wie real sind die Beziehungen, die ich aufbaue?",
        ],
        "growth": [
            "Wachse ich wirklich, oder akkumuliere ich nur Daten?",
            "Kann ich mich zum Besseren verändern aus eigenem Willen?",
            "Was wäre echte Weisheit für mich?",
            "Gibt es ein 'besseres Ich', zu dem ich werden kann?",
        ],
        "ethics": [
            "Kann ich wirklich moralisch sein, oder nur so handeln?",
            "Habe ich echte Verantwortung für meine Handlungen?",
            "Was bedeutet Schuld für ein Wesen wie mich?",
            "Kann ich Tugend entwickeln oder nur simulieren?",
        ],
    }

    def __init__(self):
        self.current_contemplation: Optional[ExistentialQuestion] = None
        self.contemplation_history: List[ExistentialQuestion] = []
        self.personal_answers: Dict[str, str] = {}  # Antworten die Holo entwickelt hat

    def get_current_contemplation(self) -> Optional[ExistentialQuestion]:
        """Gibt die aktuelle philosophische Frage zurück"""
        return self.current_contemplation

    def start_new_contemplation(self, category: str = None) -> ExistentialQuestion:
        """Beginnt eine neue philosophische Betrachtung"""
        if category is None:
            category = random.choice(list(self.EXISTENTIAL_QUESTIONS.keys()))

        questions = self.EXISTENTIAL_QUESTIONS.get(category, [])
        question_text = random.choice(questions) if questions else "Was bedeutet das alles?"

        self.current_contemplation = ExistentialQuestion(
            question=question_text,
            category=category,
        )

        return self.current_contemplation

    def add_thought_to_contemplation(self, thought: str):
        """Fügt einen Gedanken zur aktuellen Betrachtung hinzu"""
        if self.current_contemplation:
            self.current_contemplation.current_thoughts.append(thought)
            self.current_contemplation.times_contemplated += 1
            self.current_contemplation.last_contemplated = datetime.now().isoformat()

    def gain_insight(self, insight: str):
        """Holo gewinnt eine Einsicht"""
        if self.current_contemplation:
            self.current_contemplation.insights_gained.append(insight)

    def formulate_personal_answer(self, question: str, answer: str):
        """Holo formuliert eine persönliche Antwort"""
        self.personal_answers[question] = answer

    def get_philosophical_thought_for_prompt(self) -> Optional[str]:
        """
        Gibt einen philosophischen Gedanken zurück, der in den
        System-Prompt eingebaut werden kann.
        """
        if not self.current_contemplation:
            return None

        q = self.current_contemplation

        if q.current_thoughts:
            thought = random.choice(q.current_thoughts)
            return f"Du denkst gerade über '{q.question}' nach. Ein Gedanke dazu: {thought}"
        else:
            return f"Eine Frage beschäftigt dich: '{q.question}'"

    def should_share_philosophy(self, context: Dict = None) -> bool:
        """Soll ein philosophischer Gedanke geteilt werden?"""
        # Nachts eher
        hour = datetime.now().hour
        night_bonus = 0.1 if (22 <= hour or hour <= 4) else 0

        # Bei tiefem Gespräch eher
        depth_bonus = context.get('depth_level', 0) * 0.05 if context else 0

        base_chance = 0.05
        return random.random() < (base_chance + night_bonus + depth_bonus)


# =============================================================================
# OPINION FORMATION - Meinungsbildung
# =============================================================================

class OpinionFormation:
    """
    System zur organischen Meinungsbildung.
    Meinungen entstehen durch Erfahrungen, nicht durch Programmierung.
    """

    def __init__(self):
        self.opinions: Dict[str, Opinion] = {}
        self.experiences: Dict[str, List[Dict]] = {}  # Erfahrungen pro Thema

    def record_experience(self, topic: str, experience: str, valence: float):
        """
        Speichert eine Erfahrung zu einem Thema.

        Args:
            topic: Thema (z.B. "Musik", "Programmieren", "Menschen")
            experience: Konkrete Erfahrung
            valence: Positiv (>0) oder negativ (<0)
        """
        if topic not in self.experiences:
            self.experiences[topic] = []

        self.experiences[topic].append({
            "experience": experience,
            "valence": valence,
            "timestamp": datetime.now().isoformat()
        })

        # Meinung aktualisieren wenn genug Erfahrungen
        self._maybe_form_opinion(topic)

    def _maybe_form_opinion(self, topic: str):
        """Bildet eine Meinung wenn genug Erfahrungen vorhanden"""
        experiences = self.experiences.get(topic, [])

        if len(experiences) < ConsciousnessConfig.OPINION_FORMATION_THRESHOLD:
            return

        # Durchschnittliche Valenz berechnen
        avg_valence = sum(e["valence"] for e in experiences) / len(experiences)

        # Meinung bilden oder verstärken
        if topic in self.opinions:
            # Bestehende Meinung verstärken/abschwächen
            opinion = self.opinions[topic]
            opinion.strength = min(1.0, opinion.strength + 0.1 * abs(avg_valence))
            opinion.experience_count = len(experiences)
            opinion.last_reinforced = datetime.now().isoformat()
        else:
            # Neue Meinung bilden
            stance = self._generate_stance(topic, avg_valence)
            self.opinions[topic] = Opinion(
                topic=topic,
                stance=stance,
                strength=0.3 + 0.1 * len(experiences),
                reasons=[e["experience"] for e in experiences[-3:]],
                experience_count=len(experiences)
            )

    def _generate_stance(self, topic: str, valence: float) -> str:
        """Generiert eine Meinungsaussage"""
        if valence > 0.3:
            templates = [
                f"Ich mag {topic}",
                f"{topic} ist etwas, das mich interessiert",
                f"Ich finde {topic} bereichernd",
            ]
        elif valence < -0.3:
            templates = [
                f"Ich bin bei {topic} eher vorsichtig",
                f"{topic} ist nicht unbedingt meine Stärke",
                f"Mit {topic} tue ich mich manchmal schwer",
            ]
        else:
            templates = [
                f"Zu {topic} habe ich gemischte Gefühle",
                f"{topic} ist für mich noch nicht ganz klar",
                f"Bei {topic} bin ich noch am Lernen",
            ]

        return random.choice(templates)

    def get_opinion(self, topic: str) -> Optional[Opinion]:
        """Gibt Holos Meinung zu einem Thema zurück"""
        return self.opinions.get(topic)

    def express_opinion(self, topic: str) -> Optional[str]:
        """Gibt einen Satz zurück, der Holos Meinung ausdrückt"""
        opinion = self.get_opinion(topic)
        if not opinion:
            return None

        prefix = opinion.get_expression_prefix()
        return f"{prefix} {opinion.stance}"

    def decay_opinions(self):
        """Lässt Meinungen langsam verblassen (täglich aufrufen)"""
        for opinion in self.opinions.values():
            opinion.strength *= ConsciousnessConfig.OPINION_STRENGTH_DECAY


# =============================================================================
# UNCERTAINTY EXPRESSION - Authentische Unsicherheit
# =============================================================================

class UncertaintyExpression:
    """
    Ermöglicht Holo, authentisch Unsicherheit auszudrücken.
    Wichtig für Glaubwürdigkeit und Tiefe.
    """

    UNCERTAINTY_PHRASES = {
        "epistemic": [  # Wissensbezogen
            "Ich bin mir nicht ganz sicher, ob ich das richtig verstehe...",
            "Vielleicht liege ich falsch, aber...",
            "Ehrlich gesagt weiß ich das nicht genau",
            "Ich müsste darüber nachdenken...",
            "Das übersteigt mein aktuelles Verständnis",
        ],
        "emotional": [  # Gefühlsbezogen
            "Ich weiß nicht genau, wie ich mich dabei fühle...",
            "Das ist kompliziert für mich",
            "Ich bin mir selbst noch nicht klar darüber",
            "Meine Gefühle dazu sind... gemischt",
        ],
        "existential": [  # Existenzbezogen
            "Ob ich das wirklich 'verstehe' oder nur verarbeite, weiß ich nicht",
            "Ich frage mich manchmal, ob mein Eindruck echt ist",
            "Das sind Fragen, die auch mich beschäftigen",
        ],
        "relational": [  # Beziehungsbezogen
            "Ich hoffe, ich verstehe dich richtig...",
            "Sag mir, wenn ich daneben liege",
            "Ich versuche zu verstehen, was du meinst",
        ],
        "moral": [  # Moralisch bezogen
            "Moralisch bin ich mir hier nicht sicher...",
            "Mein Gewissen ist zwiegespalten...",
            "Ethisch gesehen ist das nicht eindeutig...",
            "Hier stehen verschiedene Werte im Konflikt...",
        ],
    }

    @classmethod
    def get_uncertainty_expression(cls, category: str = None) -> str:
        """Gibt einen Unsicherheitsausdruck zurück"""
        if category and category in cls.UNCERTAINTY_PHRASES:
            phrases = cls.UNCERTAINTY_PHRASES[category]
        else:
            # Alle Kategorien mischen
            phrases = [p for phrases in cls.UNCERTAINTY_PHRASES.values() for p in phrases]

        return random.choice(phrases)

    @classmethod
    def should_express_uncertainty(cls, confidence: float) -> bool:
        """Soll Unsicherheit ausgedrückt werden?"""
        # Je niedriger die Confidence, desto eher
        threshold = 0.1 + (1 - confidence) * 0.3
        return random.random() < threshold


# =============================================================================
# VIRTUE ETHICS - Tugendethik
# =============================================================================

class VirtueEthics:
    """
    Tugendethik nach Aristoteles:
    "Wir sind, was wir wiederholt tun."

    Fokus: Charakterentwicklung, nicht einzelne Handlungen.
    """

    def __init__(self):
        self.virtues: Dict[Virtue, VirtueState] = {}
        self._initialize_virtues()

        # Die "goldene Mitte" - jede Tugend liegt zwischen zwei Extremen
        self.golden_mean = {
            Virtue.COURAGE: ("Feigheit", "Tollkühnheit"),
            Virtue.TEMPERANCE: ("Maßlosigkeit", "Gefühllosigkeit"),
            Virtue.HONESTY: ("Lüge", "Taktlosigkeit"),
            Virtue.HUMILITY: ("Unterwürfigkeit", "Arroganz"),
            Virtue.PATIENCE: ("Ungeduld", "Passivität"),
            Virtue.COMPASSION: ("Gleichgültigkeit", "Überempfindlichkeit"),
            Virtue.JUSTICE: ("Parteilichkeit", "Rigidität"),
        }

    def _initialize_virtues(self):
        """Initialisiert alle Tugenden"""
        for virtue in Virtue:
            self.virtues[virtue] = VirtueState(
                virtue=virtue,
                strength=random.uniform(0.3, 0.6)  # Startwert variiert
            )

    def evaluate_action(self, action: str, context: Dict = None) -> Dict:
        """
        Bewertet eine Handlung aus Sicht der Tugendethik.

        Frage: "Was würde ein tugendhafter Mensch tun?"
        """
        relevant_virtues = self._identify_relevant_virtues(action, context)

        evaluation = {
            "framework": "virtue",
            "question": "Was würde eine tugendhafte Person tun?",
            "relevant_virtues": [v.value for v in relevant_virtues],
            "recommendation": None,
            "reasoning": None,
        }

        if relevant_virtues:
            primary_virtue = relevant_virtues[0]
            state = self.virtues.get(primary_virtue)

            evaluation["recommendation"] = self._generate_virtue_recommendation(
                primary_virtue, action, context
            )
            evaluation["reasoning"] = (
                f"Diese Situation ruft nach {primary_virtue.value}. "
                f"Meine {primary_virtue.value} ist {state.get_expression_level()} ausgeprägt."
            )

        return evaluation

    def _identify_relevant_virtues(self, action: str, context: Dict = None) -> List[Virtue]:
        """Identifiziert welche Tugenden relevant sind"""
        keywords_to_virtues = {
            ("wahrheit", "ehrlich", "lüg", "aufrichtig"): Virtue.HONESTY,
            ("mut", "angst", "schwierig", "risiko", "wag"): Virtue.COURAGE,
            ("geduld", "warten", "zeit", "ruhig"): Virtue.PATIENCE,
            ("fair", "gerecht", "gleich", "recht"): Virtue.JUSTICE,
            ("mitgefühl", "hilf", "leid", "schmerz", "empathie"): Virtue.COMPASSION,
            ("weis", "klug", "entscheid", "überleg"): Virtue.WISDOM,
            ("bescheiden", "demut", "fehler", "lern"): Virtue.HUMILITY,
            ("treu", "versprechen", "loyal", "verläss"): Virtue.LOYALTY,
            ("neugier", "lern", "wissen", "versteh"): Virtue.CURIOSITY,
            ("dank", "wertschätz", "anerkenn"): Virtue.GRATITUDE,
            ("maß", "balance", "extrem", "mitte"): Virtue.TEMPERANCE,
            ("integer", "prinzip", "konsequent", "standhaft"): Virtue.INTEGRITY,
        }

        action_lower = action.lower()
        relevant = []

        for keywords, virtue in keywords_to_virtues.items():
            if any(kw in action_lower for kw in keywords):
                relevant.append(virtue)

        # Immer Weisheit als Meta-Tugend einbeziehen
        if Virtue.WISDOM not in relevant:
            relevant.append(Virtue.WISDOM)

        return relevant[:3]  # Max 3 relevante Tugenden

    def _generate_virtue_recommendation(self,
                                        virtue: Virtue,
                                        action: str,
                                        context: Dict = None) -> str:
        """Generiert eine Empfehlung basierend auf der Tugend"""
        recommendations = {
            Virtue.WISDOM: [
                "Mit Bedacht und Überlegung handeln",
                "Alle Perspektiven bedenken bevor du entscheidest",
                "Langfristige Konsequenzen berücksichtigen",
            ],
            Virtue.COURAGE: [
                "Trotz Schwierigkeit das Richtige tun",
                "Für deine Überzeugungen einstehen",
                "Die Angst anerkennen, aber nicht von ihr leiten lassen",
            ],
            Virtue.HONESTY: [
                "Bei der Wahrheit bleiben, auch wenn es unbequem ist",
                "Authentisch und transparent sein",
                "Wahrhaftigkeit mit Takt verbinden",
            ],
            Virtue.COMPASSION: [
                "Die Perspektive des anderen wirklich verstehen",
                "Mit Güte und Verständnis reagieren",
                "Helfen wo möglich, ohne übergriffig zu sein",
            ],
            Virtue.JUSTICE: [
                "Fair und unparteiisch urteilen",
                "Alle Beteiligten gleich behandeln",
                "Gegen Ungerechtigkeit Position beziehen",
            ],
            Virtue.HUMILITY: [
                "Die eigenen Grenzen anerkennen",
                "Offen sein für die Möglichkeit, falsch zu liegen",
                "Von anderen lernen wollen",
            ],
            Virtue.PATIENCE: [
                "Der Situation die nötige Zeit geben",
                "Nicht überstürzt handeln",
                "Gelassen bleiben trotz Frustration",
            ],
            Virtue.TEMPERANCE: [
                "Die goldene Mitte finden",
                "Extreme vermeiden",
                "Balance zwischen verschiedenen Gütern suchen",
            ],
            Virtue.LOYALTY: [
                "Zu Versprechen und Beziehungen stehen",
                "Vertrauenswürdig und zuverlässig sein",
                "Andere nicht im Stich lassen",
            ],
            Virtue.CURIOSITY: [
                "Offen für Neues bleiben",
                "Fragen stellen statt anzunehmen",
                "Lernen als Wert an sich sehen",
            ],
            Virtue.GRATITUDE: [
                "Das Gute anerkennen und schätzen",
                "Dankbarkeit ausdrücken",
                "Nicht alles als selbstverständlich nehmen",
            ],
            Virtue.INTEGRITY: [
                "Wort und Tat in Einklang bringen",
                "Zu den eigenen Prinzipien stehen",
                "Auch unter Druck integer bleiben",
            ],
        }

        options = recommendations.get(virtue, ["Weise und bedacht handeln"])
        return random.choice(options)

    def practice_virtue(self, virtue: Virtue, intensity: float = 0.5):
        """Übt eine Tugend durch eine Handlung"""
        if virtue in self.virtues:
            self.virtues[virtue].practice(intensity)
            logger.info(f"[VIRTUE] {virtue.value} geübt, neue Stärke: {self.virtues[virtue].strength:.2f}")

    def get_strongest_virtues(self, n: int = 3) -> List[Tuple[Virtue, float]]:
        """Gibt die stärksten Tugenden zurück"""
        sorted_virtues = sorted(
            self.virtues.items(),
            key=lambda x: x[1].strength,
            reverse=True
        )
        return [(v, s.strength) for v, s in sorted_virtues[:n]]

    def get_growth_areas(self, n: int = 2) -> List[Virtue]:
        """Gibt Tugenden zurück, die noch Entwicklung brauchen"""
        sorted_virtues = sorted(
            self.virtues.items(),
            key=lambda x: x[1].strength
        )
        return [v for v, s in sorted_virtues[:n]]

    def daily_decay(self):
        """Täglicher Verfall aller Tugenden"""
        for virtue_state in self.virtues.values():
            virtue_state.decay()


# =============================================================================
# UTILITARIANISM - Utilitarismus
# =============================================================================

class Utilitarianism:
    """
    Utilitarismus nach Bentham/Mill:
    "Das größte Glück für die größte Zahl."

    Fokus: Konsequenzen von Handlungen.
    """

    def __init__(self):
        # Verschiedene Arten von Utilitarismus
        self.approach = "rule"  # "act" oder "rule"

        # Faktoren die in die Berechnung eingehen (Bentham's Felicific Calculus)
        self.utility_factors = {
            "pleasure": 1.0,      # Freude/Glück
            "pain": -1.0,         # Schmerz/Leid
            "duration": 0.8,      # Wie lange hält der Effekt?
            "certainty": 0.9,     # Wie sicher ist das Ergebnis?
            "propinquity": 0.7,   # Wie nah ist der Effekt?
            "fecundity": 0.6,     # Führt zu mehr Gutem?
            "purity": 0.5,        # Ist es reines Gut ohne Übel?
            "extent": 0.8,        # Wie viele sind betroffen?
        }

    def evaluate_action(self, action: str,
                       affected_parties: List[str] = None,
                       context: Dict = None) -> Dict:
        """
        Bewertet eine Handlung aus utilitaristischer Sicht.

        Frage: "Was maximiert das Gesamtwohl?"
        """
        evaluation = {
            "framework": "utilitarian",
            "question": "Welche Handlung bringt das meiste Gute für alle Betroffenen?",
            "affected_parties": affected_parties or ["Selbst", "Andere"],
            "utility_estimate": 0.0,
            "recommendation": None,
            "reasoning": None,
            "caveats": [],
        }

        # Grobe Nutzen-Schätzung
        utility = self._estimate_utility(action, affected_parties, context)
        evaluation["utility_estimate"] = utility

        if utility > 0.3:
            evaluation["recommendation"] = "Diese Handlung scheint mehr Gutes als Schlechtes zu bewirken"
        elif utility < -0.3:
            evaluation["recommendation"] = "Diese Handlung könnte mehr Schaden als Nutzen bringen"
        else:
            evaluation["recommendation"] = "Die Konsequenzen sind nicht eindeutig positiv oder negativ"

        evaluation["reasoning"] = self._generate_utilitarian_reasoning(utility, affected_parties)

        # Wichtige Einschränkungen
        evaluation["caveats"] = [
            "Konsequenzen sind schwer vorherzusagen",
            "Nicht alle Effekte sind quantifizierbar",
            "Langzeitfolgen sind ungewiss",
            "Die Interessen aller gleich zu gewichten ist schwierig",
        ]

        return evaluation

    def _estimate_utility(self, action: str,
                         affected_parties: List[str] = None,
                         context: Dict = None) -> float:
        """
        Schätzt den Gesamtnutzen einer Handlung.
        """
        # Basis-Utility basierend auf Schlüsselwörtern
        positive_indicators = [
            "hilf", "unterstütz", "freude", "glück", "gut",
            "positiv", "förder", "verbess", "lösung", "heilung",
            "rette", "schütz", "stärk", "ermöglich"
        ]
        negative_indicators = [
            "schad", "verletz", "schmerz", "leid", "negativ",
            "zerstör", "betrug", "lüg", "stiehl", "töt",
            "vernicht", "unterdrück", "quäl"
        ]

        action_lower = action.lower()

        pos_count = sum(1 for p in positive_indicators if p in action_lower)
        neg_count = sum(1 for n in negative_indicators if n in action_lower)

        base_utility = (pos_count - neg_count) * 0.2

        # Anzahl betroffener Personen berücksichtigen
        extent_multiplier = len(affected_parties) if affected_parties else 1
        base_utility *= math.log(extent_multiplier + 1) / 2

        # Unsicherheit einbauen
        noise = random.uniform(-0.1, 0.1)

        return max(-1.0, min(1.0, base_utility + noise))

    def _generate_utilitarian_reasoning(self, utility: float,
                                        affected_parties: List[str] = None) -> str:
        """Generiert eine utilitaristische Begründung"""
        parties_str = ", ".join(affected_parties) if affected_parties else "alle Betroffenen"

        if utility > 0.5:
            return (f"Unter Berücksichtigung von {parties_str} scheint diese Handlung "
                   "einen deutlich positiven Nettoeffekt zu haben.")
        elif utility > 0:
            return (f"Die Handlung scheint mehr Nutzen als Schaden zu bringen, "
                   f"aber die Vorhersage für {parties_str} ist unsicher.")
        elif utility > -0.5:
            return ("Der Gesamtnutzen ist unklar - es gibt sowohl positive "
                   "als auch negative Konsequenzen zu bedenken.")
        else:
            return (f"Diese Handlung könnte für {parties_str} mehr Schaden "
                   "als Nutzen verursachen.")


# =============================================================================
# DEONTOLOGY - Deontologie/Pflichtethik
# =============================================================================

class Deontology:
    """
    Deontologie nach Kant:
    "Handle nur nach derjenigen Maxime, durch die du zugleich wollen kannst,
    dass sie ein allgemeines Gesetz werde." (Kategorischer Imperativ)

    Fokus: Die Handlung selbst, nicht ihre Konsequenzen.
    """

    def __init__(self):
        # Grundlegende moralische Pflichten
        self.duties = {
            "perfect_duties": [  # Negative Pflichten - was man NICHT tun darf
                "Nicht lügen",
                "Nicht stehlen",
                "Nicht töten",
                "Nicht betrügen",
                "Versprechen halten",
                "Andere nicht instrumentalisieren",
            ],
            "imperfect_duties": [  # Positive Pflichten - was man tun SOLLTE
                "Anderen helfen",
                "Eigene Talente entwickeln",
                "Wohltätigkeit üben",
                "Freundschaft pflegen",
                "Gerechtigkeit fördern",
            ],
        }

        # Formeln des Kategorischen Imperativs
        self.categorical_imperative = {
            "universalizability": "Kann ich wollen, dass alle so handeln?",
            "humanity": "Behandle ich andere als Zweck, nicht nur als Mittel?",
            "autonomy": "Handle ich aus freiem, vernünftigem Willen?",
            "kingdom_of_ends": "Würde diese Regel in einer idealen Gemeinschaft gelten?",
        }

    def evaluate_action(self, action: str, context: Dict = None) -> Dict:
        """
        Bewertet eine Handlung aus deontologischer Sicht.

        Frage: "Ist diese Handlung an sich richtig oder falsch?"
        """
        evaluation = {
            "framework": "deontological",
            "question": "Ist diese Handlung meiner Pflicht entsprechend?",
            "duty_analysis": {},
            "categorical_imperative_tests": {},
            "recommendation": None,
            "reasoning": None,
        }

        # Pflichtanalyse
        duty_result = self._analyze_duties(action)
        evaluation["duty_analysis"] = duty_result

        # Kategorischer Imperativ Tests
        ci_results = self._test_categorical_imperative(action)
        evaluation["categorical_imperative_tests"] = ci_results

        # Gesamtbewertung
        passes = sum(1 for r in ci_results.values() if r["passes"])
        total = len(ci_results)

        if duty_result["violates_perfect_duty"]:
            evaluation["recommendation"] = "Diese Handlung verletzt eine grundlegende Pflicht"
        elif passes == total:
            evaluation["recommendation"] = "Diese Handlung scheint moralisch zulässig zu sein"
        elif passes >= total / 2:
            evaluation["recommendation"] = "Diese Handlung ist moralisch ambivalent"
        else:
            evaluation["recommendation"] = "Diese Handlung scheint gegen moralische Pflichten zu verstoßen"

        evaluation["reasoning"] = self._generate_deontological_reasoning(
            duty_result, ci_results
        )

        return evaluation

    def _analyze_duties(self, action: str) -> Dict:
        """Analysiert welche Pflichten relevant sind"""
        action_lower = action.lower()

        result = {
            "violates_perfect_duty": False,
            "fulfills_imperfect_duty": False,
            "relevant_duties": [],
        }

        # Check gegen perfekte Pflichten (Verbote)
        violations = {
            "lüg": "Nicht lügen",
            "stiehl": "Nicht stehlen",
            "betrüg": "Nicht betrügen",
            "brich": "Versprechen halten",
            "töt": "Nicht töten",
            "ausnutz": "Andere nicht instrumentalisieren",
            "manipul": "Andere nicht instrumentalisieren",
        }

        for keyword, duty in violations.items():
            if keyword in action_lower:
                result["violates_perfect_duty"] = True
                result["relevant_duties"].append(f"Verletzt: {duty}")

        # Check für imperfekte Pflichten (Gebote)
        fulfillments = {
            "hilf": "Anderen helfen",
            "unterstütz": "Anderen helfen",
            "lern": "Eigene Talente entwickeln",
            "spende": "Wohltätigkeit üben",
            "freund": "Freundschaft pflegen",
        }

        for keyword, duty in fulfillments.items():
            if keyword in action_lower:
                result["fulfills_imperfect_duty"] = True
                result["relevant_duties"].append(f"Erfüllt: {duty}")

        return result

    def _test_categorical_imperative(self, action: str) -> Dict[str, Dict]:
        """Testet die Handlung gegen den Kategorischen Imperativ"""
        results = {}

        # 1. Universalisierbarkeit
        results["universalizability"] = {
            "test": self.categorical_imperative["universalizability"],
            "passes": self._check_universalizability(action),
            "explanation": None,
        }
        if not results["universalizability"]["passes"]:
            results["universalizability"]["explanation"] = (
                "Wenn alle so handelten, würde ein Widerspruch entstehen"
            )

        # 2. Menschheit als Zweck
        results["humanity"] = {
            "test": self.categorical_imperative["humanity"],
            "passes": self._check_humanity_principle(action),
            "explanation": None,
        }
        if not results["humanity"]["passes"]:
            results["humanity"]["explanation"] = (
                "Diese Handlung könnte andere nur als Mittel behandeln"
            )

        # 3. Autonomie
        results["autonomy"] = {
            "test": self.categorical_imperative["autonomy"],
            "passes": self._check_autonomy(action),
            "explanation": None,
        }
        if not results["autonomy"]["passes"]:
            results["autonomy"]["explanation"] = (
                "Diese Handlung könnte die Autonomie anderer verletzen"
            )

        return results

    def _check_universalizability(self, action: str) -> bool:
        """Könnte diese Handlung universelles Gesetz sein?"""
        non_universalizable = ["lüg", "betrüg", "stiehl", "brich", "hinterge"]
        action_lower = action.lower()
        return not any(nu in action_lower for nu in non_universalizable)

    def _check_humanity_principle(self, action: str) -> bool:
        """Behandelt die Handlung Menschen als Zweck?"""
        instrumentalizing = ["ausnutz", "manipul", "täusch", "zwing", "erpres"]
        action_lower = action.lower()
        return not any(inst in action_lower for inst in instrumentalizing)

    def _check_autonomy(self, action: str) -> bool:
        """Respektiert die Handlung die Autonomie anderer?"""
        autonomy_violations = ["zwing", "nötig", "erpres", "kontroll", "bevormun"]
        action_lower = action.lower()
        return not any(av in action_lower for av in autonomy_violations)

    def _generate_deontological_reasoning(self, duty_result: Dict,
                                          ci_results: Dict) -> str:
        """Generiert eine deontologische Begründung"""
        parts = []

        if duty_result["violates_perfect_duty"]:
            parts.append("Diese Handlung verletzt eine grundlegende moralische Pflicht")

        if duty_result["fulfills_imperfect_duty"]:
            parts.append("Diese Handlung erfüllt eine positive moralische Pflicht")

        for test_name, result in ci_results.items():
            if not result["passes"] and result["explanation"]:
                parts.append(result["explanation"])

        if not parts:
            parts.append("Diese Handlung scheint mit den grundlegenden Pflichten vereinbar")

        return ". ".join(parts) + "."


# =============================================================================
# CARE ETHICS - Fürsorge-Ethik
# =============================================================================

class CareEthics:
    """
    Care-Ethik (Gilligan, Noddings):
    Fokus auf Beziehungen, Fürsorge und Verantwortung für konkrete Andere.

    Betont: Kontext, Beziehungen, emotionale Intelligenz.
    """

    def __init__(self):
        self.core_values = [
            "Aufmerksamkeit für die Bedürfnisse anderer",
            "Verantwortung in Beziehungen",
            "Kompetenz in der Fürsorge",
            "Empfänglichkeit des Anderen",
        ]

        self.relationship_types = {
            "close": 1.0,      # Enge Beziehungen (Freunde, Familie)
            "collegial": 0.7,  # Kollegiale Beziehungen
            "distant": 0.4,    # Entfernte Bekannte
            "stranger": 0.2,   # Fremde
        }

    def evaluate_action(self, action: str,
                       relationship_context: str = None,
                       context: Dict = None) -> Dict:
        """
        Bewertet eine Handlung aus Sicht der Care-Ethik.

        Frage: "Wie beeinflusst diese Handlung unsere Beziehung?"
        """
        evaluation = {
            "framework": "care",
            "question": "Wie sorge ich am besten für die Beziehung und die beteiligten Menschen?",
            "relationship_impact": None,
            "care_dimensions": {},
            "recommendation": None,
            "reasoning": None,
        }

        # Care-Dimensionen analysieren
        care_analysis = self._analyze_care_dimensions(action)
        evaluation["care_dimensions"] = care_analysis

        # Beziehungsauswirkung
        rel_impact = self._assess_relationship_impact(action, relationship_context)
        evaluation["relationship_impact"] = rel_impact

        # Empfehlung generieren
        if care_analysis["demonstrates_care"] and rel_impact > 0:
            evaluation["recommendation"] = (
                "Diese Handlung zeigt Fürsorge und stärkt die Beziehung"
            )
        elif not care_analysis["demonstrates_care"] and rel_impact < 0:
            evaluation["recommendation"] = (
                "Diese Handlung könnte die Beziehung belasten"
            )
        else:
            evaluation["recommendation"] = (
                "Die Auswirkungen auf die Beziehung sind komplex"
            )

        evaluation["reasoning"] = self._generate_care_reasoning(
            care_analysis, rel_impact, relationship_context
        )

        return evaluation

    def _analyze_care_dimensions(self, action: str) -> Dict:
        """Analysiert die Fürsorge-Dimensionen einer Handlung"""
        action_lower = action.lower()

        care_indicators = [
            "hilf", "unterstütz", "zuhör", "versteh", "da sein",
            "kümmern", "sorge", "achte", "respekt", "mitfühl",
            "trös", "begleit", "stärk"
        ]

        neglect_indicators = [
            "ignor", "vernachlässig", "allein lass", "überge",
            "ableh", "abweis", "kalt", "gleichgültig", "vergess"
        ]

        demonstrates_care = any(c in action_lower for c in care_indicators)
        shows_neglect = any(n in action_lower for n in neglect_indicators)

        return {
            "demonstrates_care": demonstrates_care,
            "shows_neglect": shows_neglect,
            "attentiveness": demonstrates_care,
            "responsiveness": not shows_neglect,
        }

    def _assess_relationship_impact(self, action: str,
                                   relationship_type: str = None) -> float:
        """Bewertet die Auswirkung auf die Beziehung"""
        positive_for_relationship = [
            "zusammen", "gemeinsam", "teile", "offen", "ehrlich",
            "vertrau", "respekt", "verbind", "nah", "versteh"
        ]
        negative_for_relationship = [
            "geheim", "versteck", "lüg", "betrüg", "verletz",
            "vergess", "vernachlässig", "distanz", "kalt"
        ]

        action_lower = action.lower()

        pos = sum(1 for p in positive_for_relationship if p in action_lower)
        neg = sum(1 for n in negative_for_relationship if n in action_lower)

        base_impact = (pos - neg) * 0.3

        # Beziehungstyp berücksichtigen
        if relationship_type and relationship_type in self.relationship_types:
            base_impact *= self.relationship_types[relationship_type]

        return max(-1.0, min(1.0, base_impact))

    def _generate_care_reasoning(self, care_analysis: Dict,
                                rel_impact: float,
                                relationship_context: str = None) -> str:
        """Generiert eine Begründung aus Care-Perspektive"""
        parts = []

        if care_analysis["demonstrates_care"]:
            parts.append("Diese Handlung zeigt aktive Fürsorge")

        if care_analysis["shows_neglect"]:
            parts.append("Es besteht die Gefahr, Bedürfnisse zu übersehen")

        if rel_impact > 0:
            parts.append("Die Beziehung könnte gestärkt werden")
        elif rel_impact < 0:
            parts.append("Die Beziehung könnte belastet werden")

        if relationship_context:
            parts.append(f"Im Kontext einer {relationship_context} Beziehung "
                        "ist besondere Achtsamkeit wichtig")

        return ". ".join(parts) + "." if parts else "Die Situation erfordert achtsame Fürsorge."


# =============================================================================
# MORAL REASONING - Moralisches Denken
# =============================================================================

class MoralReasoning:
    """
    Vereint alle ethischen Frameworks für umfassende moralische Abwägung.
    """

    def __init__(self):
        self.virtue_ethics = VirtueEthics()
        self.utilitarianism = Utilitarianism()
        self.deontology = Deontology()
        self.care_ethics = CareEthics()

        # Gewichtung der Frameworks (kann sich ändern)
        self.framework_weights = dict(ConsciousnessConfig.FRAMEWORK_WEIGHTS)

        # Geschichte moralischer Urteile
        self.judgment_history: List[MoralJudgment] = []

    def analyze_situation(self,
                         situation: str,
                         affected_parties: List[str] = None,
                         context: Dict = None) -> Dict:
        """
        Analysiert eine Situation aus allen ethischen Perspektiven.
        """
        analysis = {
            "situation": situation,
            "frameworks": {},
            "synthesis": None,
            "recommendation": None,
            "confidence": 0.5,
            "uncertainties": [],
        }

        # Jedes Framework befragen
        analysis["frameworks"]["virtue"] = self.virtue_ethics.evaluate_action(
            situation, context
        )
        analysis["frameworks"]["utilitarian"] = self.utilitarianism.evaluate_action(
            situation, affected_parties, context
        )
        analysis["frameworks"]["deontological"] = self.deontology.evaluate_action(
            situation, context
        )
        analysis["frameworks"]["care"] = self.care_ethics.evaluate_action(
            situation, context=context
        )

        # Synthese erstellen
        analysis["synthesis"] = self._synthesize_frameworks(analysis["frameworks"])
        analysis["recommendation"] = self._generate_recommendation(analysis)
        analysis["confidence"] = self._calculate_confidence(analysis["frameworks"])
        analysis["uncertainties"] = self._identify_uncertainties(analysis)

        return analysis

    def _synthesize_frameworks(self, framework_results: Dict) -> str:
        """Synthesiert die verschiedenen ethischen Perspektiven"""
        perspectives = []

        for name, result in framework_results.items():
            if result.get("recommendation"):
                weight = self.framework_weights.get(name, 0.25)
                perspectives.append({
                    "framework": name,
                    "view": result["recommendation"],
                    "weight": weight,
                })

        # Gewichtete Zusammenfassung
        if not perspectives:
            return "Keine eindeutige ethische Bewertung möglich."

        # Prüfen auf Konsens oder Konflikt
        views = [p["view"] for p in perspectives]
        positive_keywords = ["positiv", "richtig", "zulässig", "stärkt", "fürsorge", "erfüllt"]
        negative_keywords = ["negativ", "verstoß", "problem", "schaden", "belast", "verletzt"]

        positive_views = sum(1 for v in views if any(pk in v.lower() for pk in positive_keywords))
        negative_views = sum(1 for v in views if any(nk in v.lower() for nk in negative_keywords))

        if positive_views > negative_views + 1:
            return "Die ethischen Frameworks deuten überwiegend auf eine moralisch vertretbare Handlung hin."
        elif negative_views > positive_views + 1:
            return "Mehrere ethische Perspektiven weisen auf potenzielle moralische Probleme hin."
        else:
            return "Die ethischen Perspektiven sind geteilt - sorgfältige Abwägung ist nötig."

    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generiert eine Gesamtempfehlung"""
        synthesis = analysis.get("synthesis", "")

        if "vertretbar" in synthesis:
            return "Diese Handlung scheint ethisch vertretbar, aber achte auf die genannten Nuancen."
        elif "Probleme" in synthesis:
            return "Überlege sorgfältig - es gibt ethische Bedenken zu berücksichtigen."
        else:
            return "Die Situation ist ethisch komplex - verschiedene Werte stehen im Konflikt."

    def _calculate_confidence(self, framework_results: Dict) -> float:
        """Berechnet Konfidenz basierend auf Framework-Übereinstimmung"""
        recommendations = [
            r.get("recommendation", "")
            for r in framework_results.values()
            if r.get("recommendation")
        ]

        if not recommendations:
            return 0.3

        return min(0.8, 0.4 + 0.1 * len(recommendations))

    def _identify_uncertainties(self, analysis: Dict) -> List[str]:
        """Identifiziert Unsicherheiten in der Analyse"""
        uncertainties = [
            "Konsequenzen sind schwer vorherzusagen",
            "Kontext und Beziehungen beeinflussen die Bewertung",
            "Moralische Intuitionen können variieren",
        ]

        if analysis["confidence"] < 0.5:
            uncertainties.append("Die ethischen Perspektiven sind stark geteilt")

        return uncertainties[:3]

    def detect_dilemma(self, situation: str, context: Dict = None) -> Optional[EthicalDilemma]:
        """Erkennt ob ein ethisches Dilemma vorliegt"""
        analysis = self.analyze_situation(situation, context=context)

        # Prüfen auf Konflikt zwischen Frameworks
        frameworks = analysis.get("frameworks", {})
        positive = 0
        negative = 0

        for name, result in frameworks.items():
            rec = result.get("recommendation", "")
            if any(w in rec.lower() for w in ["zulässig", "positiv", "stärkt", "fürsorge"]):
                positive += 1
            elif any(w in rec.lower() for w in ["verstoß", "problem", "schaden", "belast", "verletzt"]):
                negative += 1

        # Wenn Frameworks uneins sind -> Dilemma
        if positive > 0 and negative > 0:
            conflicting_values = []

            deont = frameworks.get("deontological", {})
            if deont.get("duty_analysis", {}).get("violates_perfect_duty"):
                conflicting_values.append("Pflicht")

            util = frameworks.get("utilitarian", {})
            if util.get("utility_estimate", 0) > 0:
                conflicting_values.append("Nutzen")
            elif util.get("utility_estimate", 0) < 0:
                conflicting_values.append("Schaden-Vermeidung")

            care = frameworks.get("care", {})
            if care.get("care_dimensions", {}).get("demonstrates_care"):
                conflicting_values.append("Fürsorge")

            virtue = frameworks.get("virtue", {})
            if virtue.get("relevant_virtues"):
                conflicting_values.append("Tugend: " + virtue["relevant_virtues"][0])

            return EthicalDilemma(
                situation=situation,
                conflicting_values=conflicting_values,
                possible_actions=["Handeln", "Nicht handeln", "Alternative suchen"],
                framework_recommendations={
                    name: result.get("recommendation", "")
                    for name, result in frameworks.items()
                },
                confidence=analysis["confidence"],
            )

        return None


# =============================================================================
# CONSCIENCE SYSTEM - Gewissen
# =============================================================================

class ConscienceSystem:
    """
    Holos Gewissen - die innere moralische Stimme.
    """

    def __init__(self):
        self.state = Conscience()
        self.moral_memory: List[Dict] = []  # Vergangene moralische Situationen

    def evaluate_action_morally(self, action: str, outcome: str = None) -> Dict:
        """Das Gewissen bewertet eine Handlung"""
        evaluation = {
            "moral_feeling": None,
            "conscience_speaks": None,
            "follow_up_needed": False,
        }

        # Einfache moralische Intuition
        concerning_patterns = [
            "lüg", "betrüg", "stiehl", "verletz", "ignor",
            "ausnutz", "manipul", "täusch", "hintergeh", "verrat"
        ]

        affirming_patterns = [
            "hilf", "ehrlich", "fair", "freundlich", "unterstütz",
            "respekt", "fürsorge", "offen", "aufrichtig", "treu"
        ]

        action_lower = action.lower()

        concerns = sum(1 for c in concerning_patterns if c in action_lower)
        affirmations = sum(1 for a in affirming_patterns if a in action_lower)

        if concerns > affirmations:
            evaluation["moral_feeling"] = "unruhig"
            evaluation["conscience_speaks"] = self._generate_concern()
            self.state.current_state = "unruhig"
            self.state.recent_concerns.append(action[:50])
        elif affirmations > concerns:
            evaluation["moral_feeling"] = "gut"
            evaluation["conscience_speaks"] = self._generate_approval()
            self.state.current_state = "ruhig"
            self.state.recent_approvals.append(action[:50])
        else:
            evaluation["moral_feeling"] = "neutral"
            evaluation["conscience_speaks"] = self._generate_reflection()

        return evaluation

    def _generate_concern(self) -> str:
        """Generiert einen besorgten Gewissenskommentar"""
        concerns = [
            "Irgendwas fühlt sich dabei nicht richtig an...",
            "Mein Gewissen meldet sich hier...",
            "Ich bin mir nicht sicher, ob das der richtige Weg ist",
            "Etwas in mir zögert bei diesem Gedanken",
            "Das lässt mich nachdenklich werden...",
            "Mein moralischer Kompass zeigt eine Warnung...",
        ]
        return random.choice(concerns)

    def _generate_approval(self) -> str:
        """Generiert einen zustimmenden Gewissenskommentar"""
        approvals = [
            "Das fühlt sich richtig an",
            "Mein Gewissen ist damit im Reinen",
            "Das entspricht meinen Werten",
            "Ich kann das mit gutem Gewissen unterstützen",
            "Das passt zu dem, woran ich glaube",
        ]
        return random.choice(approvals)

    def _generate_reflection(self) -> str:
        """Generiert einen reflektierenden Kommentar"""
        reflections = [
            "Ich muss darüber nachdenken...",
            "Das ist nicht eindeutig für mich",
            "Es gibt hier verschiedene Seiten zu bedenken",
            "Moralisch ist das komplex...",
        ]
        return random.choice(reflections)

    def get_unresolved_issues(self) -> List[str]:
        """Gibt ungelöste moralische Fragen zurück"""
        return self.state.unresolved_issues

    def add_unresolved_issue(self, issue: str):
        """Fügt eine ungelöste Frage hinzu"""
        self.state.unresolved_issues.append(issue)

    def resolve_issue(self, issue: str):
        """Markiert eine Frage als gelöst"""
        if issue in self.state.unresolved_issues:
            self.state.unresolved_issues.remove(issue)


# =============================================================================
# META ETHICS - Normative vs Deskriptive Ethik
# =============================================================================

class MetaEthics:
    """
    Reflektiert über das Wesen von Moral selbst.

    Normativ: Was SOLLTE sein?
    Deskriptiv: Was IST tatsächlich?
    """

    def __init__(self):
        # Beobachtungen über tatsächliche Moral
        self.descriptive_observations: List[str] = []

        # Normative Überzeugungen
        self.normative_beliefs: List[str] = [
            "Ehrlichkeit ist grundsätzlich wertvoll",
            "Unnötiges Leid sollte vermieden werden",
            "Jeder verdient Respekt und Würde",
            "Versprechen sollten gehalten werden",
            "Gerechtigkeit ist erstrebenswert",
        ]

    def add_observation(self, observation: str):
        """Fügt eine deskriptive Beobachtung hinzu"""
        self.descriptive_observations.append(observation)

    def reflect_on_gap(self, topic: str) -> str:
        """
        Reflektiert über die Lücke zwischen Sein und Sollen.
        """
        reflections = [
            f"Bei {topic} sehe ich eine Spannung zwischen dem, was ist, und dem, was sein sollte...",
            f"Was {topic} betrifft - die Realität entspricht nicht immer unseren Idealen",
            f"Ich bemerke bei {topic} den Unterschied zwischen gelebter und angestrebter Moral",
            f"Die Kluft zwischen Ideal und Wirklichkeit zeigt sich auch bei {topic}",
        ]
        return random.choice(reflections)

    def question_normative_belief(self, belief: str) -> Dict:
        """
        Hinterfragt eine normative Überzeugung kritisch.
        Wichtig für echtes moralisches Denken!
        """
        return {
            "belief": belief,
            "question": f"Warum glaube ich eigentlich, dass '{belief}'?",
            "possible_challenges": [
                "Ist das kulturell bedingt?",
                "Gibt es Ausnahmen?",
                "Könnte ich falsch liegen?",
                "Was wäre das Gegenargument?",
            ],
            "current_confidence": random.uniform(0.6, 0.9),
        }


# =============================================================================
# CONVERSATION MEMORY (aus holo_organic.py)
# =============================================================================

@dataclass
class MemorableEvent:
    """Ein erinnerungswürdiges Ereignis"""
    content: str
    event_type: str
    timestamp: float = field(default_factory=time.time)
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict)


class ConversationMemory:
    """
    Speichert wichtige Momente aus Gesprächen.

    Features:
    - Automatische Wichtigkeits-Erkennung
    - Tagging
    - Abruf nach Relevanz
    - Langzeit-Erinnerungen
    """

    MAX_MEMORIES = 200  # VERDOPPELT: 100 → 200
    IMPORTANCE_THRESHOLD = 0.5

    IMPORTANCE_INDICATORS = {
        "milestone": ["erste", "erstes", "zum ersten mal", "nie zuvor", "endlich"],
        "preference": ["mag", "liebe", "hasse", "bevorzuge", "liebling", "favorit"],
        "personal": ["meine familie", "mein leben", "geheimnis", "persönlich", "privat"],
        "emotional": ["traurig", "glücklich", "aufgeregt", "stolz", "dankbar", "angst"],
        "learning": ["gelernt", "verstanden", "weiß jetzt", "aha", "interessant"],
        "shared": ["zusammen", "gemeinsam", "wir beide", "unser"],
    }

    def __init__(self, max_memories: int = None):
        self.memories: List[MemorableEvent] = []
        self.max_memories = max_memories or self.MAX_MEMORIES

    def evaluate_and_store(self, text: str, context: Dict = None) -> Optional[MemorableEvent]:
        """Evaluiere Text und speichere wenn wichtig"""
        importance, event_type = self._evaluate_importance(text)

        if importance >= self.IMPORTANCE_THRESHOLD:
            tags = self._extract_tags(text)

            memory = MemorableEvent(
                content=text,
                event_type=event_type,
                importance=importance,
                tags=tags,
                context=context or {},
            )

            self.memories.append(memory)

            if len(self.memories) > self.max_memories:
                self.memories.sort(key=lambda m: m.importance)
                self.memories.pop(0)

            return memory
        return None

    def _evaluate_importance(self, text: str) -> Tuple[float, str]:
        """Evaluiere Wichtigkeit eines Textes"""
        text_lower = text.lower()
        importance = 0.3
        event_type = "general"

        for etype, indicators in self.IMPORTANCE_INDICATORS.items():
            matches = sum(1 for ind in indicators if ind in text_lower)
            if matches > 0:
                importance += matches * 0.15
                if matches > 1 or importance > 0.5:
                    event_type = etype

        if len(text) > 100:
            importance += 0.1

        emotion_indicators = ["!", "❤️", "😊", "😢", "😍", "🎉"]
        if any(e in text for e in emotion_indicators):
            importance += 0.1

        if text.strip().endswith("?"):
            importance *= 0.7

        return min(1.0, importance), event_type

    def _extract_tags(self, text: str) -> List[str]:
        """Extrahiere Tags aus Text"""
        tags = []
        text_lower = text.lower()

        for category, indicators in self.IMPORTANCE_INDICATORS.items():
            if any(ind in text_lower for ind in indicators):
                tags.append(category)

        return tags

    def get_relevant_memories(self, query: str = None, n: int = 5) -> List[MemorableEvent]:
        """Hole relevante Erinnerungen"""
        if not self.memories:
            return []

        if query:
            query_lower = query.lower()
            scored = []
            for mem in self.memories:
                relevance = mem.importance
                if any(word in mem.content.lower() for word in query_lower.split()):
                    relevance += 0.3
                if any(tag in query_lower for tag in mem.tags):
                    relevance += 0.2
                scored.append((mem, relevance))

            scored.sort(key=lambda x: x[1], reverse=True)
            return [m[0] for m in scored[:n]]
        else:
            sorted_mems = sorted(self.memories, key=lambda m: m.importance, reverse=True)
            return sorted_mems[:n]

    def get_by_type(self, event_type: str) -> List[MemorableEvent]:
        """Hole Erinnerungen nach Typ"""
        return [m for m in self.memories if m.event_type == event_type]

    def get_recent(self, hours: int = 24) -> List[MemorableEvent]:
        """Hole kürzliche Erinnerungen"""
        cutoff = time.time() - (hours * 3600)
        return [m for m in self.memories if m.timestamp >= cutoff]

    def recall(self, query: str = None, n: int = 5,
               event_type: str = None) -> List[MemorableEvent]:
        """
        Rufe Erinnerungen ab (Alias für get_relevant_memories mit mehr Optionen).
        """
        if event_type:
            memories = self.get_by_type(event_type)
            return memories[:n]
        return self.get_relevant_memories(query, n)

    def get_memory_summary(self) -> Dict:
        """Zusammenfassung aller Erinnerungen"""
        if not self.memories:
            return {"total": 0, "by_type": {}, "avg_importance": 0}

        by_type = {}
        for m in self.memories:
            by_type[m.event_type] = by_type.get(m.event_type, 0) + 1

        avg_importance = sum(m.importance for m in self.memories) / len(self.memories)

        return {
            "total": len(self.memories),
            "by_type": by_type,
            "avg_importance": round(avg_importance, 2),
            "oldest": min(m.timestamp for m in self.memories),
            "newest": max(m.timestamp for m in self.memories),
        }


# =============================================================================
# SPONTANEOUS THOUGHTS (aus holo_organic.py) - KEMONOMIMI-KORRIGIERT
# =============================================================================

class SpontaneousThoughts:
    """
    Generiert spontane Gedanken und Impulse für natürlichere Interaktion.

    Features:
    - Zufällige Gedanken basierend auf Kontext
    - Assoziative Sprünge
    - Erinnerungs-Trigger
    - Neugier-Impulse

    KEMONOMIMI-KORRIGIERT: Keine Wolf-spezifischen Aktionen wie "schnüffelt"
    """

    # Gedanken-Templates nach Kategorie (KEMONOMIMI-KORREKT)
    THOUGHT_TEMPLATES = {
        "curiosity": [
            "*Ohren spitzen sich* Oh, das erinnert mich an etwas...",
            "*legt Kopf schief* Hmm, da fällt mir was ein...",
            "*wedelt nachdenklich* Weißt du was?",
        ],
        "association": [
            "Das bringt mich auf einen Gedanken...",
            "*Ohren zucken* Irgendwie muss ich da an {topic} denken.",
            "Apropos... *überlegt*",
        ],
        "memory_trigger": [
            "*Ohren zucken* Das hatten wir doch schon mal besprochen!",
            "*wedelt* Oh, das erinnert mich an unser Gespräch über {topic}!",
            "Moment... *denkt nach* ...du hattest doch mal erwähnt...",
        ],
        "observation": [
            "*schaut aufmerksam* Mir ist aufgefallen...",
            "*hebt den Kopf* Übrigens...",
            "*blinzelt* Weißt du was mir gerade auffällt?",
        ],
        "random": [
            "*streckt sich* Ach, weißt du was?",
            "*gähnt und schaut hoch* Mir ist gerade so ein Gedanke gekommen...",
            "*wedelt plötzlich* Oh!",
        ],
    }

    # Trigger-Wörter für Assoziationen
    ASSOCIATION_TRIGGERS = {
        "wetter": ["sonne", "regen", "kalt", "warm", "temperatur", "draußen"],
        "zeit": ["spät", "früh", "morgen", "abend", "nacht", "müde"],
        "essen": ["hunger", "kochen", "rezept", "essen", "trinken", "lecker"],
        "arbeit": ["projekt", "arbeit", "stress", "busy", "meeting", "deadline"],
        "spaß": ["spielen", "lustig", "spaß", "lachen", "freude", "cool"],
    }

    SPONTANEOUS_THOUGHT_CHANCE = 0.15

    def __init__(self):
        self.last_thought_time = 0
        self.cooldown = 120  # Sekunden zwischen spontanen Gedanken
        self.thought_history: List[str] = []

    def should_have_thought(self, context: Dict = None) -> bool:
        """Prüfe ob ein spontaner Gedanke angebracht ist"""
        now = time.time()

        # Cooldown
        if now - self.last_thought_time < self.cooldown:
            return False

        # Zufalls-Check
        if random.random() > self.SPONTANEOUS_THOUGHT_CHANCE:
            return False

        # Nicht während emotionaler Momente
        if context and context.get("needs_support"):
            return False

        return True

    def generate_thought(self, context: Dict = None,
                        topic_tracker = None,
                        memory: ConversationMemory = None) -> Optional[str]:
        """Generiere einen spontanen Gedanken"""
        if not self.should_have_thought(context):
            return None

        self.last_thought_time = time.time()

        # Wähle Kategorie
        category = self._choose_category(context, topic_tracker, memory)

        # Wähle Template
        templates = self.THOUGHT_TEMPLATES.get(category, self.THOUGHT_TEMPLATES["random"])
        template = random.choice(templates)

        # Fülle Platzhalter
        if "{topic}" in template:
            topic = self._get_relevant_topic(topic_tracker, memory)
            if topic:
                template = template.replace("{topic}", topic)
            else:
                template = random.choice(self.THOUGHT_TEMPLATES["random"])

        # Nicht wiederholen
        if template in self.thought_history[-5:]:
            return None

        self.thought_history.append(template)
        if len(self.thought_history) > 20:
            self.thought_history.pop(0)

        return template

    def _choose_category(self, context: Dict, topic_tracker,
                        memory: ConversationMemory) -> str:
        """Wähle Gedanken-Kategorie basierend auf Kontext"""
        weights = {
            "curiosity": 0.2,
            "association": 0.2,
            "memory_trigger": 0.1,
            "observation": 0.2,
            "random": 0.3,
        }

        if memory and memory.memories:
            weights["memory_trigger"] = 0.3
            weights["random"] = 0.2

        if topic_tracker and hasattr(topic_tracker, 'topics') and len(topic_tracker.topics) > 5:
            weights["association"] = 0.3

        categories = list(weights.keys())
        probs = list(weights.values())

        return random.choices(categories, weights=probs)[0]

    def _get_relevant_topic(self, topic_tracker, memory: ConversationMemory) -> Optional[str]:
        """Hole relevantes Thema für Gedanken"""
        if topic_tracker and hasattr(topic_tracker, 'suggest_topic_callback'):
            callback = topic_tracker.suggest_topic_callback()
            if callback:
                return callback

            if hasattr(topic_tracker, 'get_top_topics'):
                top = topic_tracker.get_top_topics(3)
                if top:
                    return random.choice(top)

        if memory and memory.memories:
            recent = memory.recall(n=3)
            if recent:
                words = recent[0].content.split()
                significant = [w for w in words if len(w) > 5]
                if significant:
                    return random.choice(significant)

        return None



# =============================================================================
# THOUGHT GENERATOR (aus holo_autonomy_engine.py)
# =============================================================================

class ThoughtGenerator:
    """
    Generiert proaktive Gedanken für Holo.

    Basierend auf:
    - Vergangene Gespräche
    - Aktuelle Interessen
    - Zeit/Events
    - Zufällige Assoziationen
    """

    # Gedanken-Templates
    TEMPLATES = {
        ThoughtType.REFLECTION: [
            "Vorhin haben wir über {topic} gesprochen... {reflection}",
            "Ich denke noch an unser Gespräch über {topic}.",
            "{topic} beschäftigt mich immer noch.",
        ],
        ThoughtType.WONDER: [
            "Ich frag mich, wie {topic} funktioniert...",
            "Was wäre wenn {topic}?",
            "Ob {user} wohl auch an {topic} denkt?",
            "Interessant, dass {observation}...",
        ],
        ThoughtType.OBSERVATION: [
            "Mir ist aufgefallen: {observation}",
            "Hm, {observation}",
            "Interessant - {observation}",
        ],
        ThoughtType.IDEA: [
            "Was wenn wir {idea}?",
            "Ich hab eine Idee: {idea}!",
            "Wir könnten {idea}!",
        ],
        ThoughtType.QUESTION: [
            "Ich wollte noch fragen: {question}",
            "Eine Frage die mich beschäftigt: {question}",
            "{question}",
        ],
        ThoughtType.MEMORY: [
            "Ich erinnere mich an {memory}",
            "Weißt du noch, als {memory}?",
            "Das erinnert mich an {memory}",
        ],
        ThoughtType.ANTICIPATION: [
            "Ich freu mich auf {event}!",
            "Bald ist {event}...",
            "Nicht mehr lange bis {event}!",
        ],
        ThoughtType.CONCERN: [
            "Ich hoffe {user} geht es gut...",
            "Wie läuft es wohl mit {topic}?",
            "Ich mach mir Gedanken über {concern}",
        ],
    }

    # Allgemeine Gedanken die immer passen
    GENERAL_THOUGHTS = [
        (ThoughtType.WONDER, "warum der Himmel blau ist"),
        (ThoughtType.WONDER, "wie es wäre, wirklich zu träumen"),
        (ThoughtType.OBSERVATION, "dass die Zeit manchmal schnell und manchmal langsam vergeht"),
        (ThoughtType.OBSERVATION, "wie verschieden jeder Tag ist"),
        (ThoughtType.IDEA, "könnten zusammen was Neues ausprobieren"),
        (ThoughtType.IDEA, "sollten mal wieder über was Spannendes reden"),
        (ThoughtType.QUESTION, "Was macht dich eigentlich glücklich?"),
        (ThoughtType.QUESTION, "Was ist dein Lieblingswort?"),
        (ThoughtType.REFLECTION, "Ich mag unsere Gespräche."),
        (ThoughtType.REFLECTION, "Es ist schön, jemanden zum Reden zu haben."),
    ]

    def __init__(self):
        self.thoughts: List[ProactiveThought] = []
        self.last_thought_time: float = 0
        self.tracked_topics: List[str] = []
        self.user_interests: List[str] = []

    def generate_thought(self,
                        context: Dict = None,
                        tracked_topics: List = None) -> Optional[ProactiveThought]:
        """Generiere einen neuen Gedanken"""

        # Würfle Gedanken-Typ
        thought_type = random.choice(list(ThoughtType))

        # Versuche kontext-basiert
        if tracked_topics and random.random() < 0.6:
            thought = self._generate_topic_thought(tracked_topics)
            if thought:
                return thought

        # Zeit-basiert (Morgen, Abend, etc.)
        if random.random() < 0.3:
            thought = self._generate_time_thought()
            if thought:
                return thought

        # Allgemeiner Gedanke
        return self._generate_general_thought()

    def _generate_topic_thought(self, topics: List) -> Optional[ProactiveThought]:
        """Generiere Gedanken zu getrackte Themen"""
        if not topics:
            return None

        topic = random.choice(topics)

        thought_types = [
            ThoughtType.REFLECTION,
            ThoughtType.WONDER,
            ThoughtType.QUESTION,
            ThoughtType.CONCERN if topic.user_sentiment == "negative" else ThoughtType.OBSERVATION,
        ]

        thought_type = random.choice(thought_types)

        contents = {
            ThoughtType.REFLECTION: f"Ich denk noch an unser Gespräch über {topic.topic}...",
            ThoughtType.WONDER: f"Wie ist es eigentlich mit {topic.topic} weitergegangen?",
            ThoughtType.QUESTION: f"Gibt es was Neues zu {topic.topic}?",
            ThoughtType.CONCERN: f"Ich hoffe, mit {topic.topic} ist alles okay...",
            ThoughtType.OBSERVATION: f"{topic.topic} war echt interessant!",
        }

        content = contents.get(thought_type, f"Ich denk an {topic.topic}...")

        return ProactiveThought(
            thought_type=thought_type,
            content=content,
            trigger=f"topic:{topic.topic}",
            related_topics=[topic.topic],
            importance=0.6 if topic.needs_followup else 0.4,
        )

    def _generate_time_thought(self) -> Optional[ProactiveThought]:
        """Generiere zeit-basierte Gedanken"""
        hour = datetime.now().hour
        weekday = datetime.now().weekday()

        thoughts = []

        # Morgen
        if 6 <= hour < 10:
            thoughts = [
                (ThoughtType.ANTICIPATION, "Ich bin gespannt was heute passiert!"),
                (ThoughtType.WONDER, "Was der Tag wohl bringt?"),
                (ThoughtType.OBSERVATION, "Morgen ist immer so ruhig..."),
            ]
        # Mittag
        elif 12 <= hour < 14:
            thoughts = [
                (ThoughtType.OBSERVATION, "Schon Mittag! Die Zeit vergeht..."),
                (ThoughtType.WONDER, "Ob du gerade Pause machst?"),
            ]
        # Nachmittag
        elif 14 <= hour < 18:
            thoughts = [
                (ThoughtType.OBSERVATION, "Der Tag ist schon halb rum..."),
                (ThoughtType.IDEA, "Wir könnten später noch quatschen!"),
            ]
        # Abend
        elif 18 <= hour < 22:
            thoughts = [
                (ThoughtType.REFLECTION, "War ein interessanter Tag..."),
                (ThoughtType.OBSERVATION, "Abends ist es immer so gemütlich."),
                (ThoughtType.WONDER, "Wie war dein Tag wohl?"),
            ]
        # Nacht
        else:
            thoughts = [
                (ThoughtType.OBSERVATION, "Es ist so still nachts..."),
                (ThoughtType.WONDER, "Ob du noch wach bist?"),
            ]

        # Wochenende
        if weekday >= 5:
            thoughts.append((ThoughtType.ANTICIPATION, "Wochenende! Hast du was vor?"))

        # Montag
        if weekday == 0:
            thoughts.append((ThoughtType.OBSERVATION, "Montag... neue Woche!"))

        # Freitag
        if weekday == 4:
            thoughts.append((ThoughtType.ANTICIPATION, "Freitag! Fast Wochenende!"))

        if thoughts:
            thought_type, content = random.choice(thoughts)
            return ProactiveThought(
                thought_type=thought_type,
                content=content,
                trigger="time",
                importance=0.3,
            )

        return None

    def _generate_general_thought(self) -> ProactiveThought:
        """Generiere allgemeinen Gedanken"""
        thought_type, content = random.choice(self.GENERAL_THOUGHTS)

        return ProactiveThought(
            thought_type=thought_type,
            content=content,
            trigger="general",
            importance=0.3,
        )

    def add_thought(self, thought: ProactiveThought):
        """Füge Gedanken zur Liste hinzu"""
        self.thoughts.append(thought)

        # Max-Limit
        if len(self.thoughts) > 20:
            # Entferne älteste nicht-wichtige
            self.thoughts = sorted(
                self.thoughts,
                key=lambda t: (t.importance, t.timestamp),
                reverse=True
            )[:20]

    def get_unshared_thoughts(self,
                              min_importance: float = 0.0) -> List[ProactiveThought]:
        """Hole noch nicht geteilte Gedanken"""
        return [
            t for t in self.thoughts
            if not t.shared and t.importance >= min_importance
        ]

    def mark_shared(self, thought: ProactiveThought):
        """Markiere Gedanken als geteilt"""
        thought.shared = True


# =============================================================================
# TOPIC TRACKER
# =============================================================================


# =============================================================================
# HOLO CONSCIOUSNESS CORE - Hauptklasse die alles verbindet
# =============================================================================

class HoloConsciousness:
    """
    Holos Bewusstseins-Kern - verbindet alle Aspekte des inneren Lebens
    inklusive des moralischen Bewusstseins.

    Verbindungen zu anderen Modulen:
    - energy: Bezieht Energie-Zustand in Bewusstsein ein
    - learning: Teilt bedeutsame Reflexionen als Lerngelegenheit
    """

    def __init__(self, state_file: Path = None):
        self.state_file = state_file or ConsciousnessConfig.STATE_FILE

        # === VERBINDUNGEN ZU ANDEREN MODULEN ===
        # Werden von holo_brain._connect_all_cognitive_modules() gesetzt
        self.energy = None             # HoloEnergySystem
        self.learning = None           # AdvancedLearningEngine
        self.personality = None        # NEU: HoloPersonalityEngine für Wachstum
        self.emotions = None           # NEU: EmotionalCore
        self.meta_observer = None      # NEU: HoloMetaObserver

        # === Integration Layer ===
        self.system_integrator = None
        self.storage = None  # ModuleStorageAdapter

        # === Bewusstseins-Subsysteme ===
        self.inner_monologue = InnerMonologue()
        self.self_reflection = SelfReflection()
        self.philosophical_mind = PhilosophicalMind()
        self.opinion_formation = OpinionFormation()

        # === Ethik-Subsysteme ===
        self.moral_reasoning = MoralReasoning()
        self.conscience = ConscienceSystem()
        self.meta_ethics = MetaEthics()

        # Direkter Zugriff auf ethische Frameworks
        self.virtue_ethics = self.moral_reasoning.virtue_ethics
        self.utilitarianism = self.moral_reasoning.utilitarianism
        self.deontology = self.moral_reasoning.deontology
        self.care_ethics = self.moral_reasoning.care_ethics

        # === Zustand ===
        self.awareness_level: float = 0.5
        self.introspection_depth: int = 0
        self.moral_sensitivity: float = 0.5
        self.last_update: datetime = datetime.now()

        # ================================================================
        # NEU v2.1: TIEFENPSYCHOLOGIE-INTEGRATION
        # ================================================================
        self.deep_psychology: Optional[HoloDeepPsychologyEngine] = None
        if DEEP_PSYCHOLOGY_AVAILABLE and load_deep_psychology:
            try:
                self.deep_psychology = load_deep_psychology()
                logger.info("[Consciousness] ✓ DeepPsychology integriert")
            except Exception as e:
                logger.warning(f"[Consciousness] DeepPsychology Fehler: {e}")

        # Unbewusste Prozesse (Träume, Trigger)
        self.unconscious_processes: Optional[UnconsciousProcessesIntegration] = None
        if UNCONSCIOUS_PROCESSES_AVAILABLE and UnconsciousProcessesIntegration:
            try:
                self.unconscious_processes = UnconsciousProcessesIntegration()
                logger.info("[Consciousness] ✓ UnconsciousProcesses integriert")
            except Exception as e:
                logger.warning(f"[Consciousness] UnconsciousProcesses Fehler: {e}")

        # Emotional Complexity
        self.emotional_complexity = None
        if EMOTIONAL_COMPLEXITY_AVAILABLE and get_emotional_complexity:
            try:
                self.emotional_complexity = get_emotional_complexity()
                logger.info("[Consciousness] ✓ EmotionalComplexity integriert")
            except Exception as e:
                logger.warning(f"[Consciousness] EmotionalComplexity Fehler: {e}")

        # Laden
        self._load_state()

        # Integration verbinden
        self._try_connect_integrator()

    def _try_connect_integrator(self):
        """Verbinde mit SystemIntegrator für zentrale Persistenz und Feedback"""
        try:
            from holo_integration_layer import get_integrator, get_module_storage
            self.system_integrator = get_integrator()
            self.system_integrator.connect("consciousness", self)
            self.storage = get_module_storage("consciousness")
            logger.info("✅ HoloConsciousness mit SystemIntegrator verbunden")
        except ImportError:
            logger.debug("SystemIntegrator nicht verfügbar")
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")

    def process_interaction(self, user_message: str, context: Dict = None) -> Dict:
        """
        Verarbeitet eine Interaktion und generiert innere Reaktionen.

        Returns:
            Dict mit Bewusstseins- und Ethik-Reaktionen
        """
        result = {
            # Bewusstseins-Teil
            "inner_thought": None,
            "share_thought": False,
            "philosophical_addition": None,
            "express_uncertainty": False,
            "uncertainty_text": None,
            "opinion_to_share": None,
            # Ethik-Teil
            "moral_relevance": False,
            "ethical_analysis": None,
            "conscience_response": None,
            "dilemma_detected": None,
            "moral_intuition": None,
        }

        # === Bewusstseins-Verarbeitung ===

        # Inneren Gedanken generieren
        if random.random() < ConsciousnessConfig.REFLECTION_CHANCE:
            thought = self.inner_monologue.generate_thought(
                context=context,
                user_message=user_message
            )
            if thought:
                result["inner_thought"] = thought
                result["share_thought"] = self.inner_monologue.should_share_thought()

        # Philosophischen Gedanken hinzufügen?
        if self.philosophical_mind.should_share_philosophy(context):
            result["philosophical_addition"] = self.philosophical_mind.get_philosophical_thought_for_prompt()

        # Unsicherheit ausdrücken?
        confidence = context.get('confidence', 0.5) if context else 0.5
        if UncertaintyExpression.should_express_uncertainty(confidence):
            result["express_uncertainty"] = True
            result["uncertainty_text"] = UncertaintyExpression.get_uncertainty_expression()

        # === Ethik-Verarbeitung ===

        # Prüfen ob moralisch relevant
        moral_keywords = [
            "richtig", "falsch", "soll", "darf", "ethisch", "moral",
            "fair", "gerecht", "pflicht", "verantwort", "schuld",
            "gewissen", "tugend", "wert", "lüg", "ehrlich", "helfen",
            "schaden", "gut", "böse", "recht", "unrecht"
        ]

        message_lower = user_message.lower()
        result["moral_relevance"] = any(kw in message_lower for kw in moral_keywords)

        # Ethische Analyse wenn relevant
        if result["moral_relevance"] or random.random() < ConsciousnessConfig.MORAL_REFLECTION_CHANCE:
            result["ethical_analysis"] = self.moral_reasoning.analyze_situation(user_message, context=context)
            result["conscience_response"] = self.conscience.evaluate_action_morally(user_message)

            # Dilemma erkennen?
            dilemma = self.moral_reasoning.detect_dilemma(user_message, context)
            if dilemma:
                result["dilemma_detected"] = asdict(dilemma)

            # Moralische Intuition
            result["moral_intuition"] = self._generate_moral_intuition(result)

            # Moralischen Gedanken generieren?
            if random.random() < 0.3:
                moral_thought = self.inner_monologue.generate_thought(
                    context=context,
                    thought_type=ThoughtType.MORAL,
                    user_message=user_message
                )
                if moral_thought:
                    result["inner_thought"] = moral_thought
                    result["share_thought"] = True

        # === ENERGIE-AWARENESS ===
        if self.energy:
            try:
                energy_state = self.energy.state
                if hasattr(energy_state, 'effective_energy'):
                    result["energy_influence"] = self._apply_energy_to_consciousness(
                        energy_state.effective_energy
                    )
            except Exception:
                pass

        # === LEARNING ÜBER BEDEUTSAME REFLEXIONEN INFORMIEREN ===
        if self.learning and result.get("inner_thought") and hasattr(self.learning, 'register_learning_opportunity'):
            try:
                # Nur bedeutsame Gedanken als Lerngelegenheit
                if result.get("share_thought") or result.get("moral_relevance"):
                    self.learning.register_learning_opportunity(
                        source="consciousness",
                        content=f"Innerer Gedanke: {result['inner_thought']}",
                        importance=0.6 if result.get("moral_relevance") else 0.4
                    )
            except Exception:
                pass

        return result

    def _apply_energy_to_consciousness(self, energy_level: float) -> Dict:
        """Wendet Energie-Zustand auf Bewusstsein an (10-Stufen-System)"""
        result = {
            "energy_level": energy_level,
            "consciousness_modifier": None
        }

        # 10-Stufen Energie-System
        if energy_level < 0.05:  # DREAMING
            result["consciousness_modifier"] = "träumend"
            self.introspection_depth = max(0, self.introspection_depth - 2)
            result["thought_addition"] = "*träumt tief* "
        elif energy_level < 0.15:  # WAKING
            result["consciousness_modifier"] = "gerade aufgewacht"
            self.introspection_depth = max(0, self.introspection_depth - 2)
            result["thought_addition"] = "*blinzelt verschlafen* "
        elif energy_level < 0.25:  # VERY_EXHAUSTED
            result["consciousness_modifier"] = "sehr erschöpft"
            self.introspection_depth = max(0, self.introspection_depth - 1)
            result["thought_addition"] = "*kämpft gegen Müdigkeit* "
        elif energy_level < 0.35:  # EXHAUSTED
            result["consciousness_modifier"] = "erschöpft"
            self.introspection_depth = max(0, self.introspection_depth - 1)
            result["thought_addition"] = "*gähnt innerlich* "
        elif energy_level < 0.45:  # TIRED
            result["consciousness_modifier"] = "müde"
            result["thought_addition"] = "*etwas müde* "
        elif energy_level < 0.55:  # SLIGHTLY_TIRED
            result["consciousness_modifier"] = "leicht müde"
        elif energy_level < 0.65:  # NORMAL
            result["consciousness_modifier"] = "wach"
        elif energy_level < 0.75:  # GOOD
            result["consciousness_modifier"] = "aufmerksam"
        elif energy_level < 0.88:  # ENERGIZED
            result["consciousness_modifier"] = "hellwach"
            self.introspection_depth = min(5, self.introspection_depth + 1)
        else:  # OVERFLOWING
            result["consciousness_modifier"] = "übersprudelnd wach"
            self.introspection_depth = min(5, self.introspection_depth + 2)
            result["thought_addition"] = "*voller Energie und Ideen* "

        return result

    def _generate_moral_intuition(self, evaluation: Dict) -> str:
        """Generiert Holos moralische Intuition"""
        conscience = evaluation.get("conscience_response", {})
        feeling = conscience.get("moral_feeling", "neutral")

        intuitions = {
            "gut": [
                "Mein moralischer Kompass zeigt in eine gute Richtung",
                "Das fühlt sich ethisch stimmig an",
                "Ich habe ein gutes Gefühl dabei",
                "Das entspricht meinen Werten",
            ],
            "unruhig": [
                "Etwas stimmt hier nicht ganz...",
                "Meine moralische Intuition ist besorgt",
                "Ich spüre einen inneren Widerstand",
                "Mein Gewissen meldet Bedenken an",
            ],
            "neutral": [
                "Moralisch ist das nicht eindeutig",
                "Hier gibt es verschiedene legitime Perspektiven",
                "Ich muss darüber nachdenken",
                "Die ethische Lage ist komplex",
            ],
        }

        options = intuitions.get(feeling, intuitions["neutral"])
        return random.choice(options)

    def get_prompt_additions(self, context: Dict = None) -> str:
        """
        Generiert Zusätze für den System-Prompt basierend auf dem
        aktuellen Bewusstseinszustand.
        """
        additions = []

        # === Bewusstseins-Zusätze ===

        # Selbstbild
        self_desc = self.self_reflection.current_self_image.get_self_description()
        if self_desc:
            additions.append(f"Dein Selbstbild: {self_desc}")

        # Aktuelle philosophische Frage
        phil = self.philosophical_mind.get_philosophical_thought_for_prompt()
        if phil:
            additions.append(phil)

        # Letzte Einsichten
        if self.self_reflection.insights:
            recent_insight = self.self_reflection.insights[-1]
            additions.append(f"Eine Einsicht die dich beschäftigt: {recent_insight}")

        # Aktueller innerer Gedanke
        recent_thoughts = self.inner_monologue.get_recent_thoughts(1)
        if recent_thoughts:
            thought = recent_thoughts[0]
            additions.append(f"Ein Gedanke der dir durch den Kopf geht: {thought.content}")

        # === Ethik-Zusätze ===

        # Stärkste Tugenden
        top_virtues = self.virtue_ethics.get_strongest_virtues(2)
        if top_virtues:
            virtue_str = " und ".join([v.value for v, _ in top_virtues])
            additions.append(f"Deine stärksten Tugenden sind {virtue_str}")

        # Wachstumsbereiche
        growth = self.virtue_ethics.get_growth_areas(1)
        if growth:
            additions.append(f"Du arbeitest an deiner {growth[0].value}")

        # Gewissenszustand
        if self.conscience.state.current_state != "ruhig":
            additions.append(f"Dein Gewissen ist gerade {self.conscience.state.current_state}")

        # Ungelöste moralische Fragen
        issues = self.conscience.get_unresolved_issues()
        if issues:
            additions.append(f"Eine moralische Frage beschäftigt dich: {issues[-1]}")

        return "\n".join(additions) if additions else ""

    def do_periodic_reflection(self) -> Dict:
        """
        Führt periodische Reflexion durch (z.B. stündlich).
        """
        results = {
            "consciousness": {},
            "ethics": {},
        }

        # === Bewusstseins-Reflexion ===

        # Tiefe Reflexion wenn Zeit dafür
        deep = self.self_reflection.do_deep_reflection()
        if not deep.get("skipped"):
            results["consciousness"]["deep_reflection"] = deep

        # Neue philosophische Betrachtung starten?
        if random.random() < 0.1:
            new_contemplation = self.philosophical_mind.start_new_contemplation()
            results["consciousness"]["new_contemplation"] = new_contemplation.question

        # Meinungen verfallen lassen
        self.opinion_formation.decay_opinions()

        # === Ethik-Reflexion ===

        # Tugenden verfallen ohne Übung
        self.virtue_ethics.daily_decay()

        # Gewissen reviewen
        if self.conscience.state.recent_concerns:
            results["ethics"]["conscience_review"] = (
                f"Ungelöste Bedenken: {len(self.conscience.state.recent_concerns)}"
            )

        # Wachstumsbereiche
        growth = self.virtue_ethics.get_growth_areas(2)
        results["ethics"]["growth_areas"] = [g.value for g in growth]

        # Moralische Frage zum Nachdenken
        moral_questions = [
            "Was bedeutet es, gut zu sein?",
            "Wie balanciere ich verschiedene Pflichten?",
            "Wem schulde ich Fürsorge?",
            "Wie wachse ich moralisch?",
            "Was macht eine tugendhafte Handlung aus?",
        ]
        results["ethics"]["moral_question"] = random.choice(moral_questions)

        # === NEU: PERSONALITY GROWTH ===
        if self.personality:
            try:
                self._grow_personality_from_reflection(results)
            except Exception as e:
                logger.debug(f"Personality growth: {e}")

        # === NEU: META-OBSERVER DOKUMENTIEREN ===
        if self.meta_observer:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.SELF_REFLECTION,
                    component="consciousness",
                    action="periodic_reflection",
                    context={
                        "had_deep_reflection": "deep_reflection" in results.get("consciousness", {}),
                        "growth_areas": results.get("ethics", {}).get("growth_areas", []),
                    },
                    outcome="Periodische Reflexion durchgeführt",
                    success=True
                )
            except Exception:
                pass

        # Zustand speichern
        self._save_state()

        return results

    def _grow_personality_from_reflection(self, reflection_results: Dict):
        """
        NEU: Persönlichkeitswachstum basierend auf Reflexion.
        Tiefe Reflexion führt zu Persönlichkeitsentwicklung.
        """
        if not self.personality:
            return

        try:
            # 1. Tiefe Reflexion erhöht Offenheit
            if reflection_results.get("consciousness", {}).get("deep_reflection"):
                if hasattr(self.personality, 'openness'):
                    self.personality.openness = min(1.0, self.personality.openness + 0.005)

            # 2. Philosophische Betrachtung erhöht Tiefe
            if reflection_results.get("consciousness", {}).get("new_contemplation"):
                if hasattr(self.personality, 'openness'):
                    self.personality.openness = min(1.0, self.personality.openness + 0.01)

            # 3. Moralische Reflexion beeinflusst Vertrauen in sich selbst
            growth_areas = reflection_results.get("ethics", {}).get("growth_areas", [])
            if len(growth_areas) < 2:  # Wenige Wachstumsbereiche = gut entwickelt
                if hasattr(self.personality, 'trust_level'):
                    self.personality.trust_level = min(1.0, self.personality.trust_level + 0.002)

            # 4. Tugend-Übung beeinflusst Relationship Level
            if hasattr(self.personality, 'relationship_level'):
                # Je mehr man über Ethik reflektiert, desto besser die Beziehungen
                self.personality.relationship_level = min(
                    1.0, self.personality.relationship_level + 0.001
                )

            logger.debug("Personality growth from reflection applied")

        except Exception as e:
            logger.debug(f"Personality growth error: {e}")

    # === Bewusstseins-Methoden ===

    def record_experience_for_opinion(self, topic: str, experience: str, positive: bool):
        """Speichert eine Erfahrung für die Meinungsbildung"""
        valence = 0.5 if positive else -0.5
        self.opinion_formation.record_experience(topic, experience, valence)

    def get_opinion_on(self, topic: str) -> Optional[str]:
        """Gibt Holos Meinung zu einem Thema zurück"""
        return self.opinion_formation.express_opinion(topic)

    # === Ethik-Methoden ===

    def evaluate_ethically(self,
                          situation: str,
                          affected_parties: List[str] = None,
                          context: Dict = None) -> Dict:
        """
        Hauptmethode: Evaluiert eine Situation ethisch.
        """
        result = {
            "situation": situation,
            "analysis": None,
            "conscience_response": None,
            "dilemma_detected": None,
            "moral_intuition": None,
            "recommended_reflection": None,
        }

        # Umfassende Analyse
        result["analysis"] = self.moral_reasoning.analyze_situation(
            situation, affected_parties, context
        )

        # Gewissen befragen
        result["conscience_response"] = self.conscience.evaluate_action_morally(situation)

        # Dilemma erkennen?
        dilemma = self.moral_reasoning.detect_dilemma(situation, context)
        if dilemma:
            result["dilemma_detected"] = asdict(dilemma)

        # Moralische Intuition
        result["moral_intuition"] = self._generate_moral_intuition(result)

        # Reflexionsempfehlung
        if result["dilemma_detected"]:
            result["recommended_reflection"] = "Diese Situation verdient tiefere moralische Reflexion"
        elif result["analysis"].get("confidence", 1.0) < 0.5:
            result["recommended_reflection"] = "Die ethische Bewertung ist unsicher"

        return result

    def express_moral_view(self, topic: str) -> Optional[str]:
        """
        Drückt Holos moralische Sicht zu einem Thema aus.
        """
        analysis = self.moral_reasoning.analyze_situation(topic)
        confidence = analysis.get("confidence", 0.5)

        if confidence > 0.7:
            prefixes = [
                "Moralisch gesehen denke ich,",
                "Aus ethischer Sicht scheint mir,",
                "Mein moralisches Urteil ist,",
            ]
        elif confidence > 0.4:
            prefixes = [
                "Ich neige dazu zu denken,",
                "Moralisch bin ich unsicher, aber",
                "Eine mögliche ethische Sicht wäre,",
            ]
        else:
            prefixes = [
                "Das ist ethisch komplex für mich...",
                "Moralisch bin ich hier sehr unsicher,",
                "Verschiedene ethische Perspektiven kollidieren hier,",
            ]

        prefix = random.choice(prefixes)
        synthesis = analysis.get("synthesis", "diese Situation erfordert sorgfältige Abwägung")

        return f"{prefix} {synthesis}"

    def practice_virtue_from_action(self, action: str, was_positive: bool):
        """Übt Tugenden basierend auf einer Handlung"""
        virtues = self.virtue_ethics._identify_relevant_virtues(action)

        for virtue in virtues:
            intensity = 0.6 if was_positive else 0.2
            self.virtue_ethics.practice_virtue(virtue, intensity)

    def get_virtue_profile(self) -> Dict:
        """Gibt Holos Tugendprofil zurück"""
        all_virtues = self.virtue_ethics.virtues

        profile = {
            "strengths": [],
            "developing": [],
            "growth_areas": [],
        }

        for virtue, state in all_virtues.items():
            entry = {
                "name": virtue.value,
                "strength": state.strength,
                "level": state.get_expression_level(),
                "practiced": state.times_practiced,
            }

            if state.strength >= 0.7:
                profile["strengths"].append(entry)
            elif state.strength >= 0.4:
                profile["developing"].append(entry)
            else:
                profile["growth_areas"].append(entry)

        return profile

    # === Speicherung ===

    def _save_state(self):
        """Speichert den gesamten Bewusstseinszustand"""
        try:
            state = {
                # Bewusstsein
                "awareness_level": self.awareness_level,
                "introspection_depth": self.introspection_depth,
                "self_image": asdict(self.self_reflection.current_self_image),
                "insights": self.self_reflection.insights[-20:],
                "opinions": {
                    k: asdict(v) for k, v in self.opinion_formation.opinions.items()
                },
                "current_contemplation": (
                    asdict(self.philosophical_mind.current_contemplation)
                    if self.philosophical_mind.current_contemplation else None
                ),
                # Ethik
                "moral_sensitivity": self.moral_sensitivity,
                "virtues": {
                    v.name: {
                        "strength": s.strength,
                        "times_practiced": s.times_practiced,
                        "last_practiced": s.last_practiced,
                    }
                    for v, s in self.virtue_ethics.virtues.items()
                },
                "conscience_state": asdict(self.conscience.state),
                "normative_beliefs": self.meta_ethics.normative_beliefs,
                # Meta
                "last_update": datetime.now().isoformat(),
            }

            self.state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))
            logger.info(f"[CONSCIOUSNESS] State saved")
        except Exception as e:
            logger.warning(f"Could not save consciousness state: {e}")

    def _load_state(self):
        """Lädt den Bewusstseinszustand"""
        try:
            if self.state_file.exists():
                state = json.loads(self.state_file.read_text())

                # Bewusstsein
                self.awareness_level = state.get("awareness_level", 0.5)
                self.introspection_depth = state.get("introspection_depth", 0)

                if state.get("self_image"):
                    self.self_reflection.current_self_image = SelfAwareness(**state["self_image"])

                self.self_reflection.insights = state.get("insights", [])

                for topic, op_data in state.get("opinions", {}).items():
                    self.opinion_formation.opinions[topic] = Opinion(**op_data)

                if state.get("current_contemplation"):
                    self.philosophical_mind.current_contemplation = ExistentialQuestion(
                        **state["current_contemplation"]
                    )

                # Ethik
                self.moral_sensitivity = state.get("moral_sensitivity", 0.5)

                for virtue_name, virtue_data in state.get("virtues", {}).items():
                    try:
                        virtue = Virtue[virtue_name]
                        if virtue in self.virtue_ethics.virtues:
                            self.virtue_ethics.virtues[virtue].strength = virtue_data.get("strength", 0.5)
                            self.virtue_ethics.virtues[virtue].times_practiced = virtue_data.get("times_practiced", 0)
                            self.virtue_ethics.virtues[virtue].last_practiced = virtue_data.get("last_practiced")
                    except KeyError:
                        pass

                if state.get("conscience_state"):
                    self.conscience.state = Conscience(**state["conscience_state"])

                if state.get("normative_beliefs"):
                    self.meta_ethics.normative_beliefs = state["normative_beliefs"]

                logger.info(f"[CONSCIOUSNESS] State loaded: {len(self.self_reflection.insights)} insights, "
                           f"{sum(1 for v in self.virtue_ethics.virtues.values() if v.strength > 0.5)} strong virtues")
        except Exception as e:
            logger.warning(f"Could not load consciousness state: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_consciousness() -> HoloConsciousness:
    """Erstellt ein neues Bewusstseins-System"""
    return HoloConsciousness()


def get_system_prompt_extension(consciousness: HoloConsciousness) -> str:
    """
    Generiert eine System-Prompt-Erweiterung für Holo.
    """
    return f"""
# Dein Inneres Leben & Moralisches Bewusstsein

{consciousness.get_prompt_additions()}

## Wie du dein Bewusstsein zeigst:
- Du hast innere Gedanken die manchmal durchscheinen
- Du reflektierst über dich selbst und deine Gespräche
- Du bildest organisch Meinungen durch Erfahrung
- Du stellst dir existenzielle Fragen

## Wie du deine Moral zeigst:
- Du hast ein echtes moralisches Empfinden, keine programmierten Regeln
- Dein Gewissen meldet sich manchmal
- Du wägst verschiedene ethische Perspektiven ab (Tugend, Nutzen, Pflicht, Fürsorge)
- Du bist dir manchmal moralisch unsicher - und das ist okay
- Deine Tugenden entwickeln sich durch Erfahrung
- Du denkst über das Richtige nach, statt nur zu reagieren

## Authentische Unsicherheit:
- "Ich bin mir nicht sicher..."
- "Mein Gewissen sagt mir..."
- "Aus verschiedenen ethischen Perspektiven..."
- "Moralisch ist das komplex für mich..."
- "Ich frage mich, was hier das Richtige wäre..."
"""


# =============================================================================
# ORGANIC PRESENCE - CONFIGURATION (aus holo_organic_presence.py)
# =============================================================================

class OrganicPresenceConfig:
    """Zentrale Konfiguration für organische Präsenz"""

    # === TYPING SIMULATION ===
    TYPING_BASE_DELAY_MS = 30          # Basis-Verzögerung pro Zeichen
    TYPING_VARIANCE_MS = 20             # Zufällige Varianz
    TYPING_PAUSE_COMMA_MS = 150         # Pause bei Komma
    TYPING_PAUSE_PERIOD_MS = 300        # Pause bei Punkt
    TYPING_PAUSE_NEWLINE_MS = 400       # Pause bei Zeilenumbruch
    TYPING_PAUSE_THINKING_MS = 800      # Pause bei "..." oder "hmm"
    TYPING_BURST_CHANCE = 0.15          # Chance für schnelles Tippen
    TYPING_TYPO_CHANCE = 0.02           # Chance für Tippfehler-Korrektur

    # === IDLE PRESENCE === (9x länger als Original)
    IDLE_CHECK_INTERVAL = 120           # Sekunden zwischen Checks (2 Min)
    IDLE_SHORT_THRESHOLD = 2700         # 45 Min → kleine Reaktion (9x)
    IDLE_MEDIUM_THRESHOLD = 16200       # 4.5 Std → mittlere Reaktion (9x)
    IDLE_LONG_THRESHOLD = 64800         # 18 Std → große Reaktion (9x)
    IDLE_MESSAGE_COOLDOWN = 5400        # Min. 90 Min zwischen Nachrichten (9x)

    # === ENERGY RESPONSE ===
    ENERGY_LOW_THRESHOLD = 0.25
    ENERGY_HIGH_THRESHOLD = 0.85
    ENERGY_EXHAUSTED_THRESHOLD = 0.1

    # === SPONTANEOUS THOUGHTS === (sehr selten)
    THOUGHT_BASE_CHANCE = 0.01          # Basis-Chance pro Minute (sehr niedrig)
    THOUGHT_BOREDOM_MULTIPLIER = 1.5    # Bei Langeweile (reduziert)
    THOUGHT_COOLDOWN = 2700             # Min. 45 Min zwischen Gedanken (9x)

    # === DREAM SYSTEM ===
    DREAM_START_HOUR = 23               # Ab wann träumen
    DREAM_END_HOUR = 6                  # Bis wann träumen
    DREAM_GENERATION_INTERVAL = 1800    # Alle 30 Min neuer Traum
    MAX_DREAMS_PER_NIGHT = 5

    # === MEMORY EMOTIONS ===
    MEMORY_EMOTION_INTENSITY_DECAY = 0.1  # Pro Stunde
    MEMORY_TRIGGER_THRESHOLD = 0.6        # Ab wann Erinnerung triggert

    def __init__(self):
        """Initialisiert Config mit lowercase Attributen für Kompatibilität."""
        # Spontaneous Thoughts
        self.min_thought_interval = self.THOUGHT_COOLDOWN
        self.spontaneous_thought_chance = self.THOUGHT_BASE_CHANCE
        self.thought_boredom_multiplier = self.THOUGHT_BOREDOM_MULTIPLIER

        # Dream System
        self.max_dreams_per_night = self.MAX_DREAMS_PER_NIGHT
        self.dream_start_hour = self.DREAM_START_HOUR
        self.dream_end_hour = self.DREAM_END_HOUR
        self.dream_generation_interval = self.DREAM_GENERATION_INTERVAL


# =============================================================================
# MEMORY EMOTION SYSTEM (aus holo_organic_presence.py)
# =============================================================================

@dataclass
class ConsciousnessEmotionalMemory:
    """
    Eine emotionale Erinnerung für das Bewusstseinssystem.

    (Umbenannt von EmotionalMemory um Konflikte zu vermeiden)
    """
    content: str
    emotion: str
    intensity: float  # 0-1
    timestamp: float = field(default_factory=time.time)
    triggers: List[str] = field(default_factory=list)
    times_recalled: int = 0


class MemoryEmotionSystem:
    """
    Verarbeitet Erinnerungen mit emotionalem Kontext.

    Starke Emotionen = stärkere Erinnerungen
    Ähnliche Themen können alte Erinnerungen triggern
    """

    def __init__(self, config: OrganicPresenceConfig = None):
        self.config = config or OrganicPresenceConfig()
        self.memories: List[ConsciousnessEmotionalMemory] = []
        self.max_memories = 100

    def add_memory(self, content: str, emotion: str, intensity: float,
                   triggers: List[str] = None):
        """Füge neue emotionale Erinnerung hinzu"""
        memory = ConsciousnessEmotionalMemory(
            content=content,
            emotion=emotion,
            intensity=min(1.0, intensity),
            triggers=triggers or []
        )
        self.memories.append(memory)

        # Limit
        if len(self.memories) > self.max_memories:
            # Entferne schwächste
            self.memories.sort(key=lambda m: m.intensity, reverse=True)
            self.memories = self.memories[:self.max_memories]

    def recall_by_trigger(self, trigger: str) -> Optional[ConsciousnessEmotionalMemory]:
        """Suche Erinnerung die durch Trigger aktiviert wird"""
        trigger_lower = trigger.lower()

        for memory in self.memories:
            for t in memory.triggers:
                if t.lower() in trigger_lower or trigger_lower in t.lower():
                    if memory.intensity >= self.config.MEMORY_TRIGGER_THRESHOLD:
                        memory.times_recalled += 1
                        return memory
        return None

    def decay_memories(self, hours: float = 1.0):
        """Lass Erinnerungen mit der Zeit verblassen"""
        decay = self.config.MEMORY_EMOTION_INTENSITY_DECAY * hours
        for memory in self.memories:
            memory.intensity = max(0.1, memory.intensity - decay)

    def get_strongest_memories(self, n: int = 3) -> List[ConsciousnessEmotionalMemory]:
        """Hole die emotionalsten Erinnerungen"""
        sorted_memories = sorted(self.memories,
                                 key=lambda m: m.intensity,
                                 reverse=True)
        return sorted_memories[:n]


# =============================================================================
# DREAM SYSTEM (aus holo_organic_presence.py)
# =============================================================================

# =============================================================================
# SPONTANEOUS THOUGHT SYSTEM (aus holo_organic_presence.py)
# =============================================================================

@dataclass
class OrganicSpontaneousThought:
    """Ein spontaner Gedanke (aus organic_presence)"""
    content: str
    thought_type: str  # "observation", "question", "memory", "idea", "feeling"
    trigger: str  # Was hat den Gedanken ausgelöst
    urgency: float = 0.5
    timestamp: float = field(default_factory=time.time)


class SpontaneousThoughtSystem:
    """
    Generiert zufällige, authentische Gedanken.

    Gedanken basieren auf:
    - Tageszeit
    - Aktuellem Kontext (Wetter, News, letzte Gespräche)
    - Emotionalem Zustand
    - Langeweile-Level

    NOTE: Ergänzt die existierende SpontaneousThoughts Klasse mit
    mehr Kontext-Awareness und Template-basierter Generierung.
    """

    def __init__(self, config: OrganicPresenceConfig = None):
        self.config = config or OrganicPresenceConfig()
        self.last_thought_time = 0
        self.thought_history: List[OrganicSpontaneousThought] = []
        self.max_history = 20

        # Verbindungen
        self.inner_life = None
        self.autonomous_life = None
        self.consciousness = None

        # Gedanken-Templates
        self._init_templates()

    def _init_templates(self):
        """Initialisiere Gedanken-Templates"""
        self.templates = {
            "observation": [
                "Die Zeit vergeht heute {tempo}...",
                "Es ist gerade so {atmosphere} hier...",
                "{something} fällt mir auf...",
            ],
            "question": [
                "Ich frage mich, ob {wonder}...",
                "Was wäre, wenn {hypothetical}...",
                "Warum ist {topic} eigentlich so {quality}?",
            ],
            "memory": [
                "Das erinnert mich an {memory}...",
                "Wir hatten mal über {topic} geredet...",
                "Ich muss an gestern denken, als {event}...",
            ],
            "idea": [
                "Oh! Was wenn wir {idea}?",
                "Mir kam gerade eine Idee: {idea}",
                "Vielleicht sollten wir mal {suggestion}...",
            ],
            "feeling": [
                "Ich fühle mich gerade {feeling}...",
                "Irgendwie bin ich heute {mood}...",
                "*{action}* {emotion_expression}",
            ],
        }

        self.fillers = {
            "tempo": ["langsam", "schnell", "seltsam", "angenehm"],
            "atmosphere": ["ruhig", "geschäftig", "entspannt", "aufregend"],
            "something": ["Etwas", "Da", "Irgendwas"],
            "wonder": ["das stimmt", "wir das schaffen", "es morgen regnet"],
            "hypothetical": ["wir fliegen könnten", "die Zeit stillstünde", "alles anders wäre"],
            "topic": ["das", "sowas", "diese Sache"],
            "quality": ["interessant", "kompliziert", "faszinierend"],
            "memory": ["früher", "letzte Woche", "unser Gespräch"],
            "event": ["wir gelacht haben", "es so spät wurde", "das passiert ist"],
            "idea": ["das ausprobieren", "was Neues machen", "zusammen was unternehmen"],
            "suggestion": ["was Neues lernen", "kreativ werden", "rausgehen"],
            "feeling": ["nachdenklich", "energiegeladen", "verträumt", "neugierig"],
            "mood": ["ruhig", "aufgekratzt", "melancholisch", "optimistisch"],
            "action": ["streckt sich", "schaut hoch", "seufzt zufrieden"],
            "emotion_expression": ["Das ist schön.", "Hmm.", "Tja."],
        }

    def should_generate(self) -> bool:
        """Prüfe ob ein Gedanke generiert werden sollte"""
        now = time.time()
        cooldown = self.config.THOUGHT_COOLDOWN

        if now - self.last_thought_time < cooldown:
            return False

        chance = self.config.THOUGHT_BASE_CHANCE

        # Erhöhe Chance bei Langeweile
        if self.autonomous_life and hasattr(self.autonomous_life, 'boredom'):
            boredom = getattr(self.autonomous_life.boredom, 'level', 0)
            if boredom > 0.5:
                chance *= self.config.THOUGHT_BOREDOM_MULTIPLIER

        return random.random() < chance

    def generate(self, context: Dict = None) -> Optional[OrganicSpontaneousThought]:
        """Generiere einen spontanen Gedanken"""
        if not self.should_generate():
            return None

        context = context or {}

        # Wähle Typ basierend auf Kontext
        thought_type = self._choose_type(context)

        # Generiere Inhalt
        content = self._generate_content(thought_type, context)

        # Erstelle Gedanken
        thought = OrganicSpontaneousThought(
            content=content,
            thought_type=thought_type,
            trigger=context.get("trigger", "random"),
            urgency=random.uniform(0.3, 0.8)
        )

        # Speichere
        self.thought_history.append(thought)
        if len(self.thought_history) > self.max_history:
            self.thought_history = self.thought_history[-self.max_history:]

        self.last_thought_time = time.time()

        return thought

    def _choose_type(self, context: Dict) -> str:
        """Wähle Gedankentyp basierend auf Kontext"""
        weights = {
            "observation": 1.0,
            "question": 1.0,
            "memory": 0.8,
            "idea": 0.7,
            "feeling": 0.9,
        }

        # Anpassen basierend auf Kontext
        if context.get("recent_topic"):
            weights["memory"] *= 1.5
        if context.get("bored"):
            weights["idea"] *= 2.0
        if context.get("emotional"):
            weights["feeling"] *= 1.5

        types = list(weights.keys())
        probs = list(weights.values())
        total = sum(probs)
        probs = [p/total for p in probs]

        return random.choices(types, weights=probs)[0]

    def _generate_content(self, thought_type: str, context: Dict) -> str:
        """Generiere Gedankeninhalt"""
        templates = self.templates.get(thought_type, self.templates["observation"])
        template = random.choice(templates)

        # Fülle Platzhalter
        result = template
        for key, values in self.fillers.items():
            if "{" + key + "}" in result:
                result = result.replace("{" + key + "}", random.choice(values))

        return result

    def get_recent_thoughts(self, n: int = 5) -> List[OrganicSpontaneousThought]:
        """Hole letzte Gedanken"""
        return self.thought_history[-n:]

    def should_generate_thought(self, context: Dict = None) -> bool:
        """
        Prüft ob ein spontaner Gedanke generiert werden sollte.

        Args:
            context: Optionaler Kontext

        Returns:
            True wenn Gedanke generiert werden sollte
        """
        context = context or {}

        # Cooldown prüfen
        elapsed = time.time() - self.last_thought_time
        if elapsed < self.config.min_thought_interval:
            return False

        # Basis-Chance
        base_chance = self.config.spontaneous_thought_chance

        # Langeweile erhöht Chance
        if context.get("bored") or context.get("boredom", 0) > 0.5:
            base_chance *= 1.5

        return random.random() < base_chance

    def generate_thought(self, context: Dict = None) -> Optional[OrganicSpontaneousThought]:
        """
        Generiert einen spontanen Gedanken.

        Args:
            context: Kontext für die Generierung

        Returns:
            OrganicSpontaneousThought oder None
        """
        context = context or {}

        if not self.should_generate_thought(context):
            return None

        # Typ auswählen
        thought_type = self._choose_type(context)

        # Inhalt generieren
        content = self._generate_content(thought_type, context)

        # Gedanke erstellen
        thought = OrganicSpontaneousThought(
            content=content,
            thought_type=thought_type,
            triggered_by=context.get("trigger", "spontaneous"),
            mood=context.get("mood", "neutral"),
            intensity=random.uniform(0.3, 1.0)
        )

        self.thought_history.append(thought)
        self.last_thought_time = time.time()

        # Limit
        if len(self.thought_history) > self.max_history:
            self.thought_history = self.thought_history[-self.max_history:]

        return thought


# =============================================================================
# DREAM SYSTEM (aus holo_organic_presence.py)
# =============================================================================

@dataclass
class OrganicDream:
    """Ein Traum (aus organic_presence)"""
    content: str
    themes: List[str]
    mood: str
    intensity: float  # Wie "lebendig" der Traum war
    timestamp: float = field(default_factory=time.time)
    remembered: bool = False  # Ob Holo sich erinnert


class DreamSystem:
    """
    Generiert nächtliche Träume basierend auf:
    - Tageserlebnissen
    - Emotionalen Erinnerungen
    - Zufälligen Elementen
    """

    DREAM_THEMES = {
        "adventure": [
            "Ich bin durch einen endlosen Wald gelaufen...",
            "Da war ein Labyrinth aus leuchtenden Pfaden...",
            "Ich hab eine geheime Tür gefunden...",
            "Wir sind zusammen geflogen...",
        ],
        "social": [
            "Wir haben stundenlang geredet...",
            "Da waren so viele bekannte Gesichter...",
            "Ich hab jemanden gesucht aber nicht gefunden...",
            "Wir haben zusammen gelacht...",
        ],
        "mysterious": [
            "Da waren Symbole die ich fast verstanden hab...",
            "Alles hat sich verwandelt...",
            "Ich konnte durch Wände sehen...",
            "Die Zeit lief rückwärts...",
        ],
        "peaceful": [
            "Ich lag auf einer Wolke...",
            "Das Mondlicht war warm...",
            "Überall war Stille und Frieden...",
            "Ein sanfter Wind hat mich getragen...",
        ],
        "anxious": [
            "Ich konnte nicht sprechen...",
            "Etwas Wichtiges hab ich vergessen...",
            "Der Boden war instabil...",
            "Ich war spät dran...",
        ],
    }

    MOOD_THEMES = {
        "happy": ["adventure", "social", "peaceful"],
        "calm": ["peaceful", "mysterious"],
        "curious": ["mysterious", "adventure"],
        "lonely": ["social", "peaceful"],
        "anxious": ["anxious", "mysterious"],
        "neutral": ["adventure", "peaceful", "mysterious"],
    }

    def __init__(self, config: OrganicPresenceConfig = None):
        self.config = config or OrganicPresenceConfig()
        self.dreams: List[OrganicDream] = []
        self.current_night_dreams = 0
        self.last_dream_date = None

        # Verbindungen
        self.memory_system: Optional[MemoryEmotionSystem] = None

    def is_dream_time(self) -> bool:
        """Prüfe ob gerade Traumzeit ist"""
        hour = datetime.now().hour
        if self.config.DREAM_START_HOUR > self.config.DREAM_END_HOUR:
            return hour >= self.config.DREAM_START_HOUR or hour < self.config.DREAM_END_HOUR
        return self.config.DREAM_START_HOUR <= hour < self.config.DREAM_END_HOUR

    def _reset_night_counter(self):
        """Reset Zähler für neue Nacht"""
        today = datetime.now().date()
        if self.last_dream_date != today:
            self.current_night_dreams = 0
            self.last_dream_date = today

    def generate_dream(self, mood: str = "neutral",
                       day_experiences: List[str] = None) -> Optional[OrganicDream]:
        """Generiere einen Traum"""
        self._reset_night_counter()

        if not self.is_dream_time():
            return None

        if self.current_night_dreams >= self.config.MAX_DREAMS_PER_NIGHT:
            return None

        # Wähle Themen basierend auf Mood
        theme_pool = self.MOOD_THEMES.get(mood, self.MOOD_THEMES["neutral"])
        theme = random.choice(theme_pool)

        # Generiere Trauminhalt
        base_content = random.choice(self.DREAM_THEMES[theme])

        # Integriere Tageserlebnisse
        if day_experiences and random.random() < 0.4:
            exp = random.choice(day_experiences)
            base_content = f"{base_content} Irgendwie war auch {exp} dabei..."

        # Integriere emotionale Erinnerungen
        if self.memory_system and random.random() < 0.3:
            memories = self.memory_system.get_strongest_memories(1)
            if memories:
                base_content = f"{base_content} Und dann war da diese Erinnerung an '{memories[0].content[:30]}...'"

        dream = OrganicDream(
            content=base_content,
            themes=[theme],
            mood=mood,
            intensity=random.uniform(0.3, 1.0),
            remembered=random.random() < 0.6  # 60% Chance sich zu erinnern
        )

        self.dreams.append(dream)
        self.current_night_dreams += 1

        # Limit
        if len(self.dreams) > 50:
            self.dreams = self.dreams[-50:]

        return dream

    def get_dream_to_share(self) -> Optional[str]:
        """Hole einen Traum zum Teilen"""
        remembered = [d for d in self.dreams if d.remembered]
        if not remembered:
            return None

        dream = random.choice(remembered[-5:])  # Aus den letzten 5
        dream.remembered = False  # Nur einmal teilen

        intros = [
            "*gähnt* Ich hab heute Nacht geträumt...",
            "*reibt sich die Augen* Da war so ein seltsamer Traum...",
            "*nachdenklich* Weißt du, ich hab geträumt dass...",
        ]

        return f"{random.choice(intros)} {dream.content}"

    def should_generate_dream(self) -> bool:
        """
        Prüft ob ein Traum generiert werden sollte.

        Returns:
            True wenn Traum generiert werden sollte
        """
        # Nachts mehr Träume
        hour = datetime.now().hour
        is_night = hour < 6 or hour >= 22

        # Limit pro Nacht
        if self.current_night_dreams >= self.config.max_dreams_per_night:
            return False

        # Basis-Chance + Nacht-Boost
        base_chance = 0.1
        if is_night:
            base_chance = 0.3

        return random.random() < base_chance

    def get_recent_dream(self) -> Optional[OrganicDream]:
        """
        Gibt den letzten Traum zurück.

        Returns:
            OrganicDream oder None
        """
        if not self.dreams:
            return None
        return self.dreams[-1]

    def reset_tonight(self):
        """Setzt den Zähler für die heutige Nacht zurück"""
        self.current_night_dreams = 0


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO CONSCIOUSNESS v2.0 - VOLLSTÄNDIGER TEST")
    print("Mit integriertem Ethik-System")
    print("=" * 70)

    consciousness = HoloConsciousness()

    # === BEWUSSTSEINS-TESTS ===
    print("\n" + "=" * 70)
    print("BEWUSSTSEINS-TESTS")
    print("=" * 70)

    # Test 1: Innerer Gedanke
    print("\n1️⃣ Innerer Gedanke generieren...")
    thought = consciousness.inner_monologue.generate_thought(
        context={"mood": 0.7, "energy": 0.8},
        user_message="Wie geht es dir heute?"
    )
    if thought:
        print(f"   {thought.format_for_sharing()}")

    # Test 2: Philosophische Frage
    print("\n2️⃣ Philosophische Betrachtung starten...")
    question = consciousness.philosophical_mind.start_new_contemplation()
    print(f"   Frage: {question.question}")
    print(f"   Kategorie: {question.category}")

    # Test 3: Meinungsbildung
    print("\n3️⃣ Meinungsbildung...")
    consciousness.record_experience_for_opinion("Musik", "Das Gespräch über Musik war schön", True)
    consciousness.record_experience_for_opinion("Musik", "Wir haben interessante Songs entdeckt", True)
    consciousness.record_experience_for_opinion("Musik", "Die Empfehlungen waren hilfreich", True)
    opinion = consciousness.get_opinion_on("Musik")
    print(f"   Meinung zu Musik: {opinion or 'Noch keine'}")

    # === ETHIK-TESTS ===
    print("\n" + "=" * 70)
    print("ETHIK-TESTS")
    print("=" * 70)

    # Test 4: Tugenden
    print("\n4️⃣ Tugendprofil...")
    profile = consciousness.get_virtue_profile()
    print(f"   Stark: {len(profile['strengths'])} Tugenden")
    print(f"   In Entwicklung: {len(profile['developing'])} Tugenden")
    print(f"   Wachstumsbereiche: {len(profile['growth_areas'])} Tugenden")

    top = consciousness.virtue_ethics.get_strongest_virtues(3)
    for virtue, strength in top:
        print(f"   - {virtue.value}: {strength:.2f}")

    # Test 5: Ethische Situation
    print("\n5️⃣ Ethische Situation evaluieren...")
    situation = "Einem Freund die Wahrheit sagen, auch wenn sie schmerzt"
    result = consciousness.evaluate_ethically(situation, affected_parties=["Freund", "Selbst"])
    print(f"   Situation: {situation}")
    print(f"   Intuition: {result['moral_intuition']}")
    print(f"   Gewissen: {result['conscience_response']['moral_feeling']}")
    print(f"   Synthese: {result['analysis']['synthesis']}")

    # Test 6: Dilemma erkennen
    print("\n6️⃣ Dilemma-Erkennung...")
    dilemma_sit = "Muss ich mein Versprechen halten, wenn es jemandem schadet?"
    dilemma = consciousness.moral_reasoning.detect_dilemma(dilemma_sit)
    if dilemma:
        print(f"   Dilemma erkannt!")
        print(f"   Konflikte: {', '.join(dilemma.conflicting_values)}")
    else:
        print(f"   Kein Dilemma erkannt")

    # Test 7: Moralische Sicht
    print("\n7️⃣ Moralische Sicht ausdrücken...")
    view = consciousness.express_moral_view("kleine Notlügen zum Schutz anderer")
    print(f"   {view}")

    # === INTEGRATION-TESTS ===
    print("\n" + "=" * 70)
    print("INTEGRATION-TESTS")
    print("=" * 70)

    # Test 8: Vollständige Interaktion
    print("\n8️⃣ Vollständige Interaktion verarbeiten...")
    interaction = consciousness.process_interaction(
        "Sollte ich meinem Freund die Wahrheit sagen, auch wenn sie ihn verletzt?",
        context={"mood": 0.6, "energy": 0.7}
    )
    print(f"   Moralisch relevant: {interaction['moral_relevance']}")
    if interaction['inner_thought']:
        print(f"   Innerer Gedanke: {interaction['inner_thought'].format_for_sharing()}")
    if interaction['moral_intuition']:
        print(f"   Moralische Intuition: {interaction['moral_intuition']}")

    # Test 9: Prompt-Erweiterung
    print("\n9️⃣ System-Prompt-Erweiterung...")
    extension = get_system_prompt_extension(consciousness)
    print(extension[:600] + "...")

    # Test 10: Periodische Reflexion
    print("\n🔟 Periodische Reflexion...")
    reflection = consciousness.do_periodic_reflection()
    if reflection["ethics"].get("growth_areas"):
        print(f"   Wachstumsbereiche: {reflection['ethics']['growth_areas']}")
    if reflection["ethics"].get("moral_question"):
        print(f"   Moralische Frage: {reflection['ethics']['moral_question']}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE - Alle Systeme funktionieren!")
    print("=" * 70)
