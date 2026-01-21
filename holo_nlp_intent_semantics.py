#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NLP Intent & Semantics v1.0                                             ║
║  Erweiterte Intent-Erkennung und Semantische Analyse für Holocloude           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FEATURES:                                                                    ║
║  1. Intent Classifier - Was will der Nutzer wirklich?                        ║
║  2. Semantic Role Labeling - Wer tut was mit wem?                            ║
║  3. Implied Meaning Detector - Unausgesprochenes erkennen                    ║
║  4. Speech Act Classifier - Illokutive Akte erkennen                         ║
║  5. Presupposition Analyzer - Implizite Annahmen aufdecken                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Optimiert für Raspberry Pi - Keine schweren ML-Bibliotheken!                ║
║  Author: Kira & Claude                                                        ║
║  Version: 1.0                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import logging
from typing import Dict, List, Optional, Tuple, Set, Any, NamedTuple
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum, auto

logger = logging.getLogger("HoloNLPIntentSemantics")

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Main Classes
    "AdvancedIntentClassifier",
    "SemanticRoleLabeler",
    "ImpliedMeaningDetector",
    "SpeechActClassifier",
    "PresuppositionAnalyzer",
    "IntentSemanticsEngine",

    # Data Classes
    "Intent",
    "SemanticFrame",
    "SemanticRole",
    "ImpliedMeaning",
    "SpeechAct",
    "Presupposition",

    # Enums
    "IntentType",
    "IntentCategory",
    "RoleType",
    "SpeechActType",
    "ImplicationType",

    # Getter Functions
    "get_intent_semantics_engine",
    "get_intent_classifier",
    "get_semantic_role_labeler",
]

# =============================================================================
# ENUMS
# =============================================================================

class IntentType(Enum):
    """Spezifische Intent-Typen"""
    # Informations-Intents
    QUESTION_FACTUAL = auto()      # Faktenfrage
    QUESTION_OPINION = auto()      # Meinungsfrage
    QUESTION_PROCEDURAL = auto()   # Wie-macht-man-Frage
    QUESTION_CLARIFICATION = auto() # Klärungsfrage
    QUESTION_RHETORICAL = auto()   # Rhetorische Frage

    # Aktions-Intents
    REQUEST_ACTION = auto()        # Bitte um Handlung
    REQUEST_INFO = auto()          # Bitte um Information
    COMMAND = auto()               # Direkter Befehl
    SUGGESTION = auto()            # Vorschlag

    # Emotions-Intents
    COMPLAINT = auto()             # Beschwerde
    PRAISE = auto()                # Lob
    FRUSTRATION = auto()           # Frustration ausdrücken
    GRATITUDE = auto()             # Dankbarkeit

    # Soziale Intents
    GREETING = auto()              # Begrüßung
    FAREWELL = auto()              # Verabschiedung
    SMALL_TALK = auto()            # Smalltalk
    APOLOGY = auto()               # Entschuldigung

    # Statement-Intents
    STATEMENT_FACT = auto()        # Faktische Aussage
    STATEMENT_OPINION = auto()     # Meinung
    STATEMENT_EXPERIENCE = auto()  # Erfahrungsbericht
    EXPLANATION = auto()           # Erklärung

    # Meta-Intents
    CORRECTION = auto()            # Korrektur
    CONFIRMATION = auto()          # Bestätigung
    DENIAL = auto()                # Verneinung/Ablehnung
    CLARIFICATION = auto()         # Klarstellung

    UNKNOWN = auto()


class IntentCategory(Enum):
    """Grobe Intent-Kategorien"""
    QUESTION = auto()
    REQUEST = auto()
    STATEMENT = auto()
    SOCIAL = auto()
    EMOTIONAL = auto()
    META = auto()
    UNKNOWN = auto()


class RoleType(Enum):
    """Semantische Rollen nach VerbNet/FrameNet-Stil"""
    AGENT = auto()           # Wer handelt
    PATIENT = auto()         # Wer/was ist betroffen
    THEME = auto()           # Was wird bewegt/verändert
    EXPERIENCER = auto()     # Wer erlebt/fühlt
    BENEFICIARY = auto()     # Wer profitiert
    INSTRUMENT = auto()      # Womit
    LOCATION = auto()        # Wo
    SOURCE = auto()          # Woher
    GOAL = auto()            # Wohin
    TIME = auto()            # Wann
    MANNER = auto()          # Wie
    CAUSE = auto()           # Warum
    PURPOSE = auto()         # Wozu
    RECIPIENT = auto()       # Empfänger
    STIMULUS = auto()        # Auslöser (bei psychologischen Verben)
    ATTRIBUTE = auto()       # Eigenschaft
    RESULT = auto()          # Ergebnis


class SpeechActType(Enum):
    """Sprechakt-Typen nach Searle"""
    ASSERTIVE = auto()       # Behaupten, Berichten
    DIRECTIVE = auto()       # Befehlen, Bitten
    COMMISSIVE = auto()      # Versprechen, Ankündigen
    EXPRESSIVE = auto()      # Danken, Entschuldigen
    DECLARATIVE = auto()     # Erklären, Definieren


class ImplicationType(Enum):
    """Arten von Implikationen"""
    CONVERSATIONAL = auto()  # Konversationelle Implikatur
    CONVENTIONAL = auto()    # Konventionelle Implikatur
    PRESUPPOSITION = auto()  # Präsupposition
    ENTAILMENT = auto()      # Logische Folgerung
    INFERENCE = auto()       # Schlussfolgerung


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Intent:
    """Ein erkannter Intent"""
    intent_type: IntentType
    category: IntentCategory
    confidence: float
    keywords: List[str]
    modifiers: Dict[str, Any]  # Urgency, Politeness, etc.
    original_text: str
    slots: Dict[str, str] = field(default_factory=dict)  # Extrahierte Entities


@dataclass
class SemanticRole:
    """Eine semantische Rolle im Satz"""
    role_type: RoleType
    text: str
    head_word: str
    start_pos: int
    end_pos: int
    confidence: float


@dataclass
class SemanticFrame:
    """Ein semantischer Frame (Verb + Rollen)"""
    predicate: str
    frame_name: str  # z.B. "Giving", "Motion", "Communication"
    roles: List[SemanticRole]
    sentence: str
    confidence: float


@dataclass
class ImpliedMeaning:
    """Eine implizierte/unausgesprochene Bedeutung"""
    implication_type: ImplicationType
    explicit_text: str
    implied_meaning: str
    confidence: float
    reasoning: str  # Warum diese Implikation


@dataclass
class SpeechAct:
    """Ein Sprechakt"""
    act_type: SpeechActType
    illocutionary_force: str  # Detaillierte Funktion
    propositional_content: str
    felicity_conditions: List[str]  # Gelingensbedingungen
    confidence: float


@dataclass
class Presupposition:
    """Eine Präsupposition"""
    trigger: str
    trigger_type: str  # factive, aspectual, existential, etc.
    presupposed_content: str
    sentence: str
    confidence: float


# =============================================================================
# ADVANCED INTENT CLASSIFIER
# =============================================================================

class AdvancedIntentClassifier:
    """
    Erweiterter Intent-Classifier mit feingranularer Erkennung.
    Erkennt nicht nur WAS, sondern auch WIE (Höflichkeit, Dringlichkeit).
    """

    def __init__(self):
        # Intent-Pattern-Mappings
        self.intent_patterns = self._build_intent_patterns()
        self.politeness_markers = self._build_politeness_markers()
        self.urgency_markers = self._build_urgency_markers()

    def _build_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Baut Intent-Pattern-Wörterbuch auf"""
        return {
            # Fragen
            IntentType.QUESTION_FACTUAL: [
                r"^(?:was|wer|wo|wann|welche?r?s?|wie ?viele?)\b",
                r"^(?:ist|sind|war|waren|hat|haben|wird|werden)\s+\w+\s*\?",
                r"weißt du", r"kannst du mir sagen", r"kennst du"
            ],
            IntentType.QUESTION_OPINION: [
                r"was (?:denkst|meinst|glaubst|hältst) du",
                r"wie findest du", r"was ist deine meinung",
                r"was würdest du", r"wie siehst du das"
            ],
            IntentType.QUESTION_PROCEDURAL: [
                r"wie (?:kann|könnte|soll|mache?) (?:ich|man)",
                r"was muss ich tun", r"wie geht das",
                r"kannst du mir (?:zeigen|erklären)"
            ],
            IntentType.QUESTION_CLARIFICATION: [
                r"was meinst du (?:damit|genau)", r"wie meinst du das",
                r"kannst du das (?:erklären|präzisieren)",
                r"verstehe ich (?:richtig|das richtig)"
            ],
            IntentType.QUESTION_RHETORICAL: [
                r"ist das nicht", r"wer hätte das gedacht",
                r"was soll das", r"wie kann das sein"
            ],

            # Aufforderungen
            IntentType.REQUEST_ACTION: [
                r"(?:kannst|könntest|würdest) du (?:bitte\s+)?(?!mir sagen)",
                r"bitte (?:\w+\s+)?(?:mach|tu|hilf|gib|zeig)",
                r"wärst du so (?:nett|freundlich|lieb)"
            ],
            IntentType.REQUEST_INFO: [
                r"(?:kannst|könntest) du mir sagen",
                r"(?:sag|erzähl|erkläre?) mir", r"ich (?:möchte|würde) gerne wissen"
            ],
            IntentType.COMMAND: [
                r"^(?:mach|tu|gib|zeig|hilf|sag|erkläre?|öffne|schließ|stopp)",
                r"^(?:nicht|hör auf)", r"^(?:lass|halt)"
            ],
            IntentType.SUGGESTION: [
                r"(?:wir könnten|man könnte|vielleicht\s+(?:sollten|könnten))",
                r"wie wäre es", r"was hältst du von",
                r"(?:ich schlage vor|mein vorschlag)"
            ],

            # Emotionen
            IntentType.COMPLAINT: [
                r"(?:das nervt|das stört|das ärgert)",
                r"(?:ich bin (?:genervt|frustriert|verärgert))",
                r"(?:schon wieder|immer noch|noch immer)",
                r"(?:warum funktioniert|warum geht.*nicht)"
            ],
            IntentType.PRAISE: [
                r"(?:das ist (?:super|toll|genial|fantastisch|wunderbar|klasse))",
                r"(?:gut gemacht|sehr gut|prima|bravo)",
                r"(?:du bist (?:der|die) beste)"
            ],
            IntentType.FRUSTRATION: [
                r"(?:argh|ugh|verdammt|mist|scheiße)",
                r"(?:ich verstehe nicht|das macht keinen sinn)",
                r"(?:nichts funktioniert|alles kaputt)"
            ],
            IntentType.GRATITUDE: [
                r"(?:danke|vielen dank|herzlichen dank)",
                r"(?:ich danke dir|das ist sehr nett)",
                r"(?:super|toll|prima)[,!]?\s*(?:danke)?"
            ],

            # Sozial
            IntentType.GREETING: [
                r"^(?:hallo|hi|hey|guten (?:tag|morgen|abend)|moin|servus|grüß)",
                r"(?:was geht|wie geht's|wie läuft's)"
            ],
            IntentType.FAREWELL: [
                r"(?:tschüss|tschau|auf wiedersehen|bye|ciao)",
                r"(?:bis (?:bald|später|morgen|dann))",
                r"(?:gute nacht|schönen (?:tag|abend))"
            ],
            IntentType.SMALL_TALK: [
                r"(?:wie war dein (?:tag|wochenende))",
                r"(?:schönes wetter|das wetter)",
                r"(?:hast du (?:gehört|gesehen))"
            ],
            IntentType.APOLOGY: [
                r"(?:entschuldigung|entschuldige|tut mir leid|sorry)",
                r"(?:verzeih mir|ich bitte um verzeihung)"
            ],

            # Statements
            IntentType.STATEMENT_FACT: [
                r"(?:es ist|es gibt|tatsächlich|in wirklichkeit)",
                r"(?:laut|gemäß|entsprechend|basierend auf)"
            ],
            IntentType.STATEMENT_OPINION: [
                r"(?:ich denke|ich glaube|ich meine|meiner meinung nach)",
                r"(?:für mich|aus meiner sicht|ich finde)"
            ],
            IntentType.STATEMENT_EXPERIENCE: [
                r"(?:ich habe (?:mal|einmal)|mir ist.*passiert)",
                r"(?:als ich|damals|früher)"
            ],
            IntentType.EXPLANATION: [
                r"(?:weil|denn|da|deshalb|daher|der grund ist)",
                r"(?:das bedeutet|das heißt|sprich)"
            ],

            # Meta
            IntentType.CORRECTION: [
                r"(?:nein,?\s+(?:ich meinte|das stimmt nicht))",
                r"(?:eigentlich|genau genommen|korrektur)",
                r"(?:das ist falsch|nicht ganz)"
            ],
            IntentType.CONFIRMATION: [
                r"^(?:ja|jawohl|richtig|genau|stimmt|korrekt|exakt)",
                r"(?:das ist richtig|so ist es)"
            ],
            IntentType.DENIAL: [
                r"^(?:nein|nö|ne|nicht|keineswegs|auf keinen fall)",
                r"(?:das stimmt nicht|falsch)"
            ],
            IntentType.CLARIFICATION: [
                r"(?:also|um (?:klar|deutlich) zu sein)",
                r"(?:ich meine damit|was ich sagen will)",
                r"(?:um es anders zu sagen|mit anderen worten)"
            ],
        }

    def _build_politeness_markers(self) -> Dict[str, float]:
        """Höflichkeitsmarker mit Scores"""
        return {
            "bitte": 0.3,
            "könntest": 0.2,
            "könnten": 0.2,
            "würdest": 0.2,
            "würden": 0.2,
            "wärst so nett": 0.4,
            "wäre es möglich": 0.4,
            "dürfte ich": 0.3,
            "wenn es nicht zu viel mühe macht": 0.5,
            "entschuldigung": 0.2,
            "vielen dank": 0.3,
            "ich wäre dankbar": 0.4,
        }

    def _build_urgency_markers(self) -> Dict[str, float]:
        """Dringlichkeitsmarker mit Scores"""
        return {
            "sofort": 0.9,
            "schnell": 0.7,
            "dringend": 0.9,
            "eilig": 0.8,
            "jetzt": 0.6,
            "gleich": 0.5,
            "wichtig": 0.6,
            "asap": 0.9,
            "notfall": 1.0,
            "unmittelbar": 0.8,
            "so bald wie möglich": 0.7,
        }

    def classify(self, text: str) -> Intent:
        """Klassifiziert den Intent eines Textes"""
        text_lower = text.lower().strip()

        # Intent-Typ bestimmen
        intent_type, keywords, confidence = self._detect_intent_type(text_lower)

        # Kategorie ableiten
        category = self._get_category(intent_type)

        # Modifikatoren extrahieren
        modifiers = self._extract_modifiers(text_lower)

        # Slots extrahieren
        slots = self._extract_slots(text, intent_type)

        return Intent(
            intent_type=intent_type,
            category=category,
            confidence=confidence,
            keywords=keywords,
            modifiers=modifiers,
            original_text=text,
            slots=slots
        )

    def _detect_intent_type(self, text: str) -> Tuple[IntentType, List[str], float]:
        """Erkennt den spezifischen Intent-Typ"""
        best_type = IntentType.UNKNOWN
        best_keywords = []
        best_confidence = 0.0

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Confidence basierend auf Pattern-Spezifität
                    pattern_length = len(pattern)
                    confidence = min(0.95, 0.5 + pattern_length * 0.01)

                    if confidence > best_confidence:
                        best_type = intent_type
                        best_keywords = [match.group(0)]
                        best_confidence = confidence

        # Fallback: Einfache Heuristiken
        if best_type == IntentType.UNKNOWN:
            if "?" in text:
                best_type = IntentType.QUESTION_FACTUAL
                best_confidence = 0.5
            elif text.endswith("!"):
                best_type = IntentType.COMMAND
                best_confidence = 0.4
            else:
                best_type = IntentType.STATEMENT_FACT
                best_confidence = 0.3

        return best_type, best_keywords, best_confidence

    def _get_category(self, intent_type: IntentType) -> IntentCategory:
        """Ordnet Intent-Typ einer Kategorie zu"""
        category_mapping = {
            IntentType.QUESTION_FACTUAL: IntentCategory.QUESTION,
            IntentType.QUESTION_OPINION: IntentCategory.QUESTION,
            IntentType.QUESTION_PROCEDURAL: IntentCategory.QUESTION,
            IntentType.QUESTION_CLARIFICATION: IntentCategory.QUESTION,
            IntentType.QUESTION_RHETORICAL: IntentCategory.QUESTION,

            IntentType.REQUEST_ACTION: IntentCategory.REQUEST,
            IntentType.REQUEST_INFO: IntentCategory.REQUEST,
            IntentType.COMMAND: IntentCategory.REQUEST,
            IntentType.SUGGESTION: IntentCategory.REQUEST,

            IntentType.COMPLAINT: IntentCategory.EMOTIONAL,
            IntentType.PRAISE: IntentCategory.EMOTIONAL,
            IntentType.FRUSTRATION: IntentCategory.EMOTIONAL,
            IntentType.GRATITUDE: IntentCategory.EMOTIONAL,

            IntentType.GREETING: IntentCategory.SOCIAL,
            IntentType.FAREWELL: IntentCategory.SOCIAL,
            IntentType.SMALL_TALK: IntentCategory.SOCIAL,
            IntentType.APOLOGY: IntentCategory.SOCIAL,

            IntentType.STATEMENT_FACT: IntentCategory.STATEMENT,
            IntentType.STATEMENT_OPINION: IntentCategory.STATEMENT,
            IntentType.STATEMENT_EXPERIENCE: IntentCategory.STATEMENT,
            IntentType.EXPLANATION: IntentCategory.STATEMENT,

            IntentType.CORRECTION: IntentCategory.META,
            IntentType.CONFIRMATION: IntentCategory.META,
            IntentType.DENIAL: IntentCategory.META,
            IntentType.CLARIFICATION: IntentCategory.META,
        }

        return category_mapping.get(intent_type, IntentCategory.UNKNOWN)

    def _extract_modifiers(self, text: str) -> Dict[str, Any]:
        """Extrahiert Modifikatoren wie Höflichkeit und Dringlichkeit"""
        modifiers = {
            "politeness": 0.5,  # Baseline
            "urgency": 0.0,
            "certainty": 0.5,
            "formality": 0.5,
        }

        # Höflichkeit
        for marker, score in self.politeness_markers.items():
            if marker in text:
                modifiers["politeness"] = min(1.0, modifiers["politeness"] + score)

        # Dringlichkeit
        for marker, score in self.urgency_markers.items():
            if marker in text:
                modifiers["urgency"] = max(modifiers["urgency"], score)

        # Gewissheit
        certainty_markers = {
            "definitiv": 0.9, "sicher": 0.8, "bestimmt": 0.8,
            "vielleicht": 0.3, "möglicherweise": 0.3, "eventuell": 0.3,
            "wahrscheinlich": 0.6, "vermutlich": 0.5
        }
        for marker, score in certainty_markers.items():
            if marker in text:
                modifiers["certainty"] = score
                break

        # Formalität
        if any(w in text for w in ["sie", "ihnen", "würden sie", "könnten sie"]):
            modifiers["formality"] = 0.8
        if any(w in text for w in ["du", "dich", "dir", "hey", "hi"]):
            modifiers["formality"] = 0.3

        return modifiers

    def _extract_slots(self, text: str, intent_type: IntentType) -> Dict[str, str]:
        """Extrahiert Intent-spezifische Slots"""
        slots = {}

        # Zeit-Slots
        time_patterns = [
            (r'\b(heute|morgen|gestern|übermorgen)\b', "time_relative"),
            (r'\b(\d{1,2}:\d{2})\b', "time_specific"),
            (r'\b(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)\b', "weekday"),
        ]

        for pattern, slot_name in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                slots[slot_name] = match.group(1)

        # Objekt-Slots (nach "das", "die", "den")
        obj_match = re.search(r'\b(?:das|die|den|einen?)\s+(\w+)\b', text.lower())
        if obj_match:
            slots["object"] = obj_match.group(1)

        # Person-Slots
        person_match = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]+)\b', text)
        if person_match:
            slots["person"] = person_match.group(1)

        return slots


# =============================================================================
# SEMANTIC ROLE LABELER
# =============================================================================

class SemanticRoleLabeler:
    """
    Weist semantische Rollen zu: Wer tut was mit wem wo wann wie warum.
    Basiert auf Frame-Semantik.
    """

    def __init__(self):
        # Verb-Frame-Mappings
        self.verb_frames = self._build_verb_frames()

        # Rolle-Marker (Präpositionen etc.)
        self.role_markers = self._build_role_markers()

    def _build_verb_frames(self) -> Dict[str, Dict[str, List[RoleType]]]:
        """Definiert Verb-Frames mit erwarteten Rollen"""
        return {
            # Bewegungsverben
            "gehen": {"name": "Motion", "roles": [RoleType.AGENT, RoleType.GOAL, RoleType.SOURCE]},
            "kommen": {"name": "Motion", "roles": [RoleType.AGENT, RoleType.GOAL, RoleType.SOURCE]},
            "fahren": {"name": "Motion", "roles": [RoleType.AGENT, RoleType.GOAL, RoleType.INSTRUMENT]},
            "laufen": {"name": "Motion", "roles": [RoleType.AGENT, RoleType.GOAL, RoleType.MANNER]},
            "fliegen": {"name": "Motion", "roles": [RoleType.AGENT, RoleType.GOAL, RoleType.SOURCE]},

            # Transferverben
            "geben": {"name": "Giving", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT]},
            "schicken": {"name": "Sending", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT, RoleType.GOAL]},
            "bringen": {"name": "Bringing", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.GOAL]},
            "nehmen": {"name": "Taking", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.SOURCE]},
            "bekommen": {"name": "Receiving", "roles": [RoleType.RECIPIENT, RoleType.THEME, RoleType.SOURCE]},

            # Kommunikationsverben
            "sagen": {"name": "Communication", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT]},
            "erzählen": {"name": "Telling", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT]},
            "fragen": {"name": "Questioning", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT]},
            "antworten": {"name": "Responding", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.STIMULUS]},
            "sprechen": {"name": "Speaking", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT]},

            # Kognitive Verben
            "denken": {"name": "Cognition", "roles": [RoleType.EXPERIENCER, RoleType.THEME]},
            "wissen": {"name": "Knowing", "roles": [RoleType.EXPERIENCER, RoleType.THEME]},
            "glauben": {"name": "Believing", "roles": [RoleType.EXPERIENCER, RoleType.THEME]},
            "verstehen": {"name": "Understanding", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS]},
            "lernen": {"name": "Learning", "roles": [RoleType.EXPERIENCER, RoleType.THEME, RoleType.SOURCE]},

            # Emotionale Verben
            "lieben": {"name": "Emotion", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS]},
            "hassen": {"name": "Emotion", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS]},
            "fürchten": {"name": "Emotion", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS]},
            "freuen": {"name": "Emotion", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS]},

            # Handlungsverben
            "machen": {"name": "Creating", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.INSTRUMENT]},
            "bauen": {"name": "Building", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.INSTRUMENT, RoleType.LOCATION]},
            "kaufen": {"name": "Commerce", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.SOURCE]},
            "verkaufen": {"name": "Commerce", "roles": [RoleType.AGENT, RoleType.THEME, RoleType.RECIPIENT]},
            "arbeiten": {"name": "Working", "roles": [RoleType.AGENT, RoleType.LOCATION, RoleType.PURPOSE]},

            # Zustandsverben
            "sein": {"name": "State", "roles": [RoleType.THEME, RoleType.ATTRIBUTE]},
            "haben": {"name": "Possession", "roles": [RoleType.AGENT, RoleType.THEME]},
            "bleiben": {"name": "State", "roles": [RoleType.THEME, RoleType.LOCATION]},
            "werden": {"name": "Change", "roles": [RoleType.THEME, RoleType.RESULT]},

            # Wahrnehmungsverben
            "sehen": {"name": "Perception", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS, RoleType.LOCATION]},
            "hören": {"name": "Perception", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS, RoleType.SOURCE]},
            "fühlen": {"name": "Perception", "roles": [RoleType.EXPERIENCER, RoleType.STIMULUS]},
        }

    def _build_role_markers(self) -> Dict[str, RoleType]:
        """Präpositionen und andere Marker für Rollen"""
        return {
            # Ziel/Richtung
            "nach": RoleType.GOAL,
            "zu": RoleType.GOAL,
            "in": RoleType.GOAL,  # auch LOCATION
            "an": RoleType.GOAL,

            # Quelle
            "von": RoleType.SOURCE,
            "aus": RoleType.SOURCE,

            # Empfänger
            "für": RoleType.BENEFICIARY,
            "an": RoleType.RECIPIENT,

            # Instrument
            "mit": RoleType.INSTRUMENT,
            "durch": RoleType.INSTRUMENT,
            "mittels": RoleType.INSTRUMENT,
            "per": RoleType.INSTRUMENT,

            # Ort
            "bei": RoleType.LOCATION,
            "auf": RoleType.LOCATION,
            "unter": RoleType.LOCATION,
            "neben": RoleType.LOCATION,
            "zwischen": RoleType.LOCATION,

            # Zeit
            "um": RoleType.TIME,
            "am": RoleType.TIME,
            "seit": RoleType.TIME,
            "bis": RoleType.TIME,

            # Art und Weise
            "wie": RoleType.MANNER,

            # Grund
            "wegen": RoleType.CAUSE,
            "aufgrund": RoleType.CAUSE,
            "weil": RoleType.CAUSE,

            # Zweck
            "um zu": RoleType.PURPOSE,
            "damit": RoleType.PURPOSE,
        }

    def label(self, sentence: str) -> SemanticFrame:
        """Labelt die semantischen Rollen in einem Satz"""
        words = sentence.split()
        sentence_lower = sentence.lower()

        # Verb finden
        predicate, frame_info = self._find_predicate(sentence_lower)

        if not predicate:
            return SemanticFrame(
                predicate="",
                frame_name="Unknown",
                roles=[],
                sentence=sentence,
                confidence=0.0
            )

        # Rollen extrahieren
        roles = self._extract_roles(sentence, sentence_lower, predicate, frame_info)

        return SemanticFrame(
            predicate=predicate,
            frame_name=frame_info.get("name", "Unknown"),
            roles=roles,
            sentence=sentence,
            confidence=0.7 if roles else 0.3
        )

    def _find_predicate(self, sentence: str) -> Tuple[Optional[str], Dict]:
        """Findet das Hauptverb/Prädikat"""
        words = sentence.split()

        for word in words:
            # Basisform des Verbs suchen
            for verb, frame in self.verb_frames.items():
                if word.startswith(verb) or verb in word:
                    return verb, frame

        return None, {}

    def _extract_roles(self, sentence: str, sentence_lower: str,
                      predicate: str, frame_info: Dict) -> List[SemanticRole]:
        """Extrahiert semantische Rollen basierend auf Position und Markern"""
        roles = []
        words = sentence.split()
        words_lower = sentence_lower.split()

        # Subjekt als Agent/Experiencer (vor dem Verb in deutschen Hauptsätzen)
        predicate_idx = self._find_word_index(words_lower, predicate)

        if predicate_idx > 0:
            # Alles vor dem Verb könnte Subjekt sein
            subject_words = words[:predicate_idx]
            subject_text = " ".join(subject_words)

            # Artikel entfernen für Head-Word
            head_word = subject_words[-1] if subject_words else ""
            if head_word.lower() in ["der", "die", "das", "ein", "eine"]:
                head_word = subject_words[-2] if len(subject_words) > 1 else ""

            expected_roles = frame_info.get("roles", [])
            role_type = RoleType.AGENT
            if RoleType.EXPERIENCER in expected_roles:
                role_type = RoleType.EXPERIENCER

            if subject_text.strip():
                roles.append(SemanticRole(
                    role_type=role_type,
                    text=subject_text,
                    head_word=head_word,
                    start_pos=0,
                    end_pos=len(subject_text),
                    confidence=0.7
                ))

        # Präpositional-Phrasen für andere Rollen
        for prep, role_type in self.role_markers.items():
            pattern = rf'\b{prep}\s+(\w+(?:\s+\w+)?)'
            match = re.search(pattern, sentence_lower)
            if match:
                pp_text = f"{prep} {match.group(1)}"
                roles.append(SemanticRole(
                    role_type=role_type,
                    text=pp_text,
                    head_word=match.group(1).split()[-1],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.6
                ))

        # Direktes Objekt (Akkusativ) nach dem Verb
        if predicate_idx >= 0 and predicate_idx < len(words) - 1:
            obj_words = []
            for w in words[predicate_idx + 1:]:
                if w.lower() in self.role_markers:
                    break
                obj_words.append(w)

            if obj_words:
                obj_text = " ".join(obj_words)
                # Bestimme ob Theme oder Patient
                role_type = RoleType.THEME
                if frame_info.get("name") in ["Perception", "Cognition"]:
                    role_type = RoleType.STIMULUS

                roles.append(SemanticRole(
                    role_type=role_type,
                    text=obj_text,
                    head_word=obj_words[-1],
                    start_pos=sentence.find(obj_text),
                    end_pos=sentence.find(obj_text) + len(obj_text),
                    confidence=0.5
                ))

        return roles

    def _find_word_index(self, words: List[str], target: str) -> int:
        """Findet den Index eines Wortes (oder Worts das damit beginnt)"""
        for i, word in enumerate(words):
            if word.startswith(target) or target in word:
                return i
        return -1


# =============================================================================
# IMPLIED MEANING DETECTOR
# =============================================================================

class ImpliedMeaningDetector:
    """
    Erkennt unausgesprochene, implizierte Bedeutungen.
    Analysiert Implikaturen und Inferenzen.
    """

    def __init__(self):
        # Implikatur-Trigger
        self.implicature_triggers = self._build_implicature_triggers()

        # Indirekte Sprechakte
        self.indirect_patterns = self._build_indirect_patterns()

    def _build_implicature_triggers(self) -> List[Dict[str, Any]]:
        """Trigger für konversationelle Implikaturen"""
        return [
            # Mengenbezogene Implikaturen (Maxime der Quantität)
            {
                "pattern": r"einige\s+(\w+)",
                "implication": "nicht alle {0}",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "Quantitäts-Implikatur: 'einige' impliziert 'nicht alle'"
            },
            {
                "pattern": r"manchmal\b",
                "implication": "nicht immer",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "Quantitäts-Implikatur: 'manchmal' impliziert 'nicht immer'"
            },
            {
                "pattern": r"versuchen\s+zu\s+(\w+)",
                "implication": "möglicherweise ohne Erfolg",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "'versuchen' impliziert unsicheren Erfolg"
            },

            # Hedge-Wörter
            {
                "pattern": r"(?:irgendwie|sozusagen|quasi|gewissermaßen)\s+(\w+)",
                "implication": "nicht genau {0}",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "Abschwächung durch Hedge-Wort"
            },

            # Ironische Strukturen
            {
                "pattern": r"(?:das ist ja|na toll|wie schön),?\s+(.+)",
                "implication": "möglicherweise ironisch gemeint: nicht {0}",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "Potenzielle Ironie-Marker erkannt"
            },

            # Aber-Struktur
            {
                "pattern": r"(\w+.*),?\s+aber\s+(.+)",
                "implication": "Einschränkung oder Widerspruch: {0} gilt nur bedingt",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "'aber' impliziert Einschränkung der ersten Aussage"
            },

            # Eigentlich
            {
                "pattern": r"eigentlich\s+(.+)",
                "implication": "im Grunde {0}, aber möglicherweise nicht ganz",
                "type": ImplicationType.CONVERSATIONAL,
                "reasoning": "'eigentlich' impliziert Abweichung von Erwartung"
            },

            # Noch-Struktur
            {
                "pattern": r"noch\s+nicht\s+(.+)",
                "implication": "wird in Zukunft {0}",
                "type": ImplicationType.INFERENCE,
                "reasoning": "'noch nicht' impliziert zukünftige Änderung"
            },

            # Schon-Struktur
            {
                "pattern": r"schon\s+(\w+)",
                "implication": "früher als erwartet",
                "type": ImplicationType.CONVENTIONAL,
                "reasoning": "'schon' impliziert Überraschung über Zeitpunkt"
            },
        ]

    def _build_indirect_patterns(self) -> List[Dict[str, Any]]:
        """Patterns für indirekte Sprechakte"""
        return [
            # Indirekte Bitten
            {
                "pattern": r"(?:kannst|könntest) du\s+(?:mir\s+)?(.+)\?",
                "explicit": "Frage nach Fähigkeit",
                "implied": "Bitte: {0}",
                "type": ImplicationType.CONVERSATIONAL,
            },
            {
                "pattern": r"(?:wärst|würdest) du so (?:nett|freundlich)\s+(.+)\?",
                "explicit": "Frage nach Freundlichkeit",
                "implied": "Höfliche Bitte: {0}",
                "type": ImplicationType.CONVERSATIONAL,
            },
            {
                "pattern": r"(?:hast|hättest) du\s+(?:vielleicht\s+)?(.+)\?",
                "explicit": "Frage nach Besitz",
                "implied": "Bitte um: {0}",
                "type": ImplicationType.CONVERSATIONAL,
            },

            # Indirekte Kritik
            {
                "pattern": r"das ist (?:interessant|spannend|schön)\b",
                "explicit": "Positive Bewertung",
                "implied": "möglicherweise diplomatische Kritik oder Skepsis",
                "type": ImplicationType.CONVERSATIONAL,
            },

            # Indirekte Ablehnung
            {
                "pattern": r"ich muss (?:erst\s+)?(?:mal\s+)?(?:darüber\s+)?nachdenken",
                "explicit": "Ankündigung von Nachdenken",
                "implied": "wahrscheinlich Ablehnung oder Zögern",
                "type": ImplicationType.CONVERSATIONAL,
            },
            {
                "pattern": r"wir werden sehen",
                "explicit": "Aussage über Zukunft",
                "implied": "wahrscheinlich nein oder Unsicherheit",
                "type": ImplicationType.CONVERSATIONAL,
            },

            # Höfliche Umschreibungen
            {
                "pattern": r"nicht unbedingt\s+(\w+)",
                "explicit": "Verneinung mit Abschwächung",
                "implied": "eher das Gegenteil von {0}",
                "type": ImplicationType.CONVERSATIONAL,
            },
        ]

    def detect(self, text: str) -> List[ImpliedMeaning]:
        """Erkennt implizierte Bedeutungen im Text"""
        results = []
        text_lower = text.lower()

        # Implikatur-Trigger prüfen
        for trigger in self.implicature_triggers:
            match = re.search(trigger["pattern"], text_lower)
            if match:
                # Platzhalter in Implikation ersetzen
                implication = trigger["implication"]
                for i, group in enumerate(match.groups()):
                    implication = implication.replace(f"{{{i}}}", group if group else "")

                results.append(ImpliedMeaning(
                    implication_type=trigger["type"],
                    explicit_text=match.group(0),
                    implied_meaning=implication,
                    confidence=0.7,
                    reasoning=trigger["reasoning"]
                ))

        # Indirekte Sprechakte prüfen
        for pattern in self.indirect_patterns:
            match = re.search(pattern["pattern"], text_lower)
            if match:
                implied = pattern["implied"]
                for i, group in enumerate(match.groups()):
                    implied = implied.replace(f"{{{i}}}", group if group else "")

                results.append(ImpliedMeaning(
                    implication_type=pattern["type"],
                    explicit_text=pattern["explicit"],
                    implied_meaning=implied,
                    confidence=0.65,
                    reasoning="Indirekter Sprechakt erkannt"
                ))

        return results


# =============================================================================
# SPEECH ACT CLASSIFIER
# =============================================================================

class SpeechActClassifier:
    """
    Klassifiziert Sprechakte nach Searle.
    Unterscheidet Assertive, Direktive, Kommissive, Expressive, Deklarative.
    """

    def __init__(self):
        self.act_patterns = self._build_act_patterns()

    def _build_act_patterns(self) -> Dict[SpeechActType, List[Dict[str, Any]]]:
        """Patterns für verschiedene Sprechakt-Typen"""
        return {
            SpeechActType.ASSERTIVE: [
                {"pattern": r"(?:ich denke|ich glaube|ich meine)\b", "force": "opinion"},
                {"pattern": r"(?:es ist|es gibt|tatsächlich)\b", "force": "assertion"},
                {"pattern": r"(?:man kann sagen|es lässt sich sagen)\b", "force": "claim"},
                {"pattern": r"(?:ich behaupte|ich stelle fest)\b", "force": "strong_assertion"},
                {"pattern": r"(?:vermutlich|wahrscheinlich)\b", "force": "speculation"},
            ],
            SpeechActType.DIRECTIVE: [
                {"pattern": r"^(?:mach|tu|gib|zeig|hilf)\b", "force": "command"},
                {"pattern": r"(?:bitte|könntest du)\b", "force": "request"},
                {"pattern": r"(?:du musst|du solltest)\b", "force": "obligation"},
                {"pattern": r"(?:lass uns|wollen wir)\b", "force": "suggestion"},
                {"pattern": r"\?$", "force": "question"},
            ],
            SpeechActType.COMMISSIVE: [
                {"pattern": r"(?:ich verspreche|ich schwöre)\b", "force": "promise"},
                {"pattern": r"(?:ich werde|ich will)\b", "force": "intention"},
                {"pattern": r"(?:ich garantiere|ich sichere zu)\b", "force": "guarantee"},
                {"pattern": r"(?:wir werden|wir wollen)\b", "force": "commitment"},
            ],
            SpeechActType.EXPRESSIVE: [
                {"pattern": r"(?:danke|vielen dank)\b", "force": "thanking"},
                {"pattern": r"(?:entschuldigung|tut mir leid|sorry)\b", "force": "apologizing"},
                {"pattern": r"(?:gratuliere|herzlichen glückwunsch)\b", "force": "congratulating"},
                {"pattern": r"(?:willkommen|herzlich willkommen)\b", "force": "welcoming"},
                {"pattern": r"(?:ich freue mich|das freut mich)\b", "force": "expressing_joy"},
                {"pattern": r"(?:schade|leider)\b", "force": "expressing_regret"},
            ],
            SpeechActType.DECLARATIVE: [
                {"pattern": r"(?:hiermit erkläre ich|ich erkläre)\b", "force": "declaring"},
                {"pattern": r"(?:ich benenne|ich taufe)\b", "force": "naming"},
                {"pattern": r"(?:das meeting ist|die sitzung ist)\s+(?:eröffnet|beendet)", "force": "institutional"},
            ],
        }

    def classify(self, text: str) -> SpeechAct:
        """Klassifiziert den Sprechakt eines Textes"""
        text_lower = text.lower().strip()

        best_act = None
        best_force = ""
        best_confidence = 0.0

        for act_type, patterns in self.act_patterns.items():
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], text_lower):
                    # Confidence basierend auf Pattern-Spezifität
                    pattern_len = len(pattern_info["pattern"])
                    confidence = min(0.9, 0.5 + pattern_len * 0.01)

                    if confidence > best_confidence:
                        best_act = act_type
                        best_force = pattern_info["force"]
                        best_confidence = confidence

        if not best_act:
            # Default: Assertive für Aussagen, Directive für Fragen
            if "?" in text:
                best_act = SpeechActType.DIRECTIVE
                best_force = "question"
            else:
                best_act = SpeechActType.ASSERTIVE
                best_force = "statement"
            best_confidence = 0.4

        # Propositional Content extrahieren
        prop_content = self._extract_propositional_content(text, best_act)

        # Felicity Conditions
        felicity = self._get_felicity_conditions(best_act, best_force)

        return SpeechAct(
            act_type=best_act,
            illocutionary_force=best_force,
            propositional_content=prop_content,
            felicity_conditions=felicity,
            confidence=best_confidence
        )

    def _extract_propositional_content(self, text: str, act_type: SpeechActType) -> str:
        """Extrahiert den propositionalen Gehalt"""
        # Performative Verben entfernen
        performatives = [
            r"ich denke,?\s*", r"ich glaube,?\s*", r"ich meine,?\s*",
            r"ich verspreche,?\s*", r"ich bitte dich,?\s*",
            r"bitte\s*", r"könntest du\s*"
        ]

        result = text
        for perf in performatives:
            result = re.sub(perf, "", result, flags=re.IGNORECASE)

        return result.strip()

    def _get_felicity_conditions(self, act_type: SpeechActType, force: str) -> List[str]:
        """Gibt die Gelingensbedingungen für einen Sprechakt zurück"""
        conditions = {
            SpeechActType.ASSERTIVE: [
                "Sprecher glaubt an Wahrheit der Aussage",
                "Hörer weiß nicht bereits, was gesagt wird"
            ],
            SpeechActType.DIRECTIVE: [
                "Hörer ist in der Lage, Handlung auszuführen",
                "Sprecher will, dass Hörer die Handlung ausführt"
            ],
            SpeechActType.COMMISSIVE: [
                "Sprecher ist in der Lage, Versprechen zu halten",
                "Hörer will, dass Sprecher die Handlung ausführt"
            ],
            SpeechActType.EXPRESSIVE: [
                "Sprecher hat entsprechende Gefühle/Einstellungen",
                "Anlass für Expression ist vorhanden"
            ],
            SpeechActType.DECLARATIVE: [
                "Sprecher hat institutionelle Autorität",
                "Kontext ermöglicht Deklaration"
            ],
        }

        return conditions.get(act_type, ["Keine spezifischen Bedingungen"])


# =============================================================================
# PRESUPPOSITION ANALYZER
# =============================================================================

class PresuppositionAnalyzer:
    """
    Analysiert Präsuppositionen - was als selbstverständlich vorausgesetzt wird.
    """

    def __init__(self):
        self.triggers = self._build_presupposition_triggers()

    def _build_presupposition_triggers(self) -> List[Dict[str, Any]]:
        """Präsuppositions-Trigger"""
        return [
            # Faktive Verben
            {
                "pattern": r"(?:weiß|wusste|wissen),?\s+dass\s+(.+)",
                "trigger_type": "factive",
                "presupposition": "{0} ist wahr",
            },
            {
                "pattern": r"(?:bereut|bereute),?\s+dass\s+(.+)",
                "trigger_type": "factive",
                "presupposition": "{0} ist wahr",
            },
            {
                "pattern": r"(?:es ist (?:klar|offensichtlich)),?\s+dass\s+(.+)",
                "trigger_type": "factive",
                "presupposition": "{0} ist wahr",
            },

            # Aspektuelle Verben
            {
                "pattern": r"(?:aufhören|hör(?:te|en)? auf),?\s+(?:zu\s+)?(.+)",
                "trigger_type": "aspectual",
                "presupposition": "hat vorher {0}",
            },
            {
                "pattern": r"(?:anfangen|fing an|beginnen|begann),?\s+(?:zu\s+)?(.+)",
                "trigger_type": "aspectual",
                "presupposition": "hat vorher nicht {0}",
            },
            {
                "pattern": r"(?:weiterhin|immer noch)\s+(.+)",
                "trigger_type": "aspectual",
                "presupposition": "hat vorher bereits {0}",
            },

            # Iterative Ausdrücke
            {
                "pattern": r"(?:wieder|erneut|nochmal)\s+(.+)",
                "trigger_type": "iterative",
                "presupposition": "hat vorher bereits einmal {0}",
            },
            {
                "pattern": r"(?:zurück|retour)\w*\s+(.+)",
                "trigger_type": "iterative",
                "presupposition": "war vorher an diesem Ort/Zustand",
            },

            # Definite Beschreibungen
            {
                "pattern": r"(?:der|die|das)\s+(\w+(?:\s+\w+)?)\s+(?:von|des|der)\s+(\w+)",
                "trigger_type": "definite",
                "presupposition": "{1} hat ein(e) {0}",
            },
            {
                "pattern": r"(?:sein|ihr|dessen|deren)\s+(\w+)",
                "trigger_type": "possessive",
                "presupposition": "hat ein(e) {0}",
            },

            # Temporale Nebensätze
            {
                "pattern": r"(?:nachdem|bevor|als|während)\s+(.+?),",
                "trigger_type": "temporal",
                "presupposition": "{0} ist/war der Fall",
            },

            # Cleft-Sätze
            {
                "pattern": r"es war\s+(\w+),?\s+(?:der|die|das)\s+(.+)",
                "trigger_type": "cleft",
                "presupposition": "jemand {1}",
            },

            # Komparative
            {
                "pattern": r"(\w+)\s+ist\s+(\w+)er\s+als\s+(\w+)",
                "trigger_type": "comparative",
                "presupposition": "{2} ist auch {1}",
            },

            # Additive Partikeln
            {
                "pattern": r"(?:auch|sogar|selbst)\s+(\w+)",
                "trigger_type": "additive",
                "presupposition": "andere Entitäten haben die gleiche Eigenschaft",
            },

            # Einschränkende Partikeln
            {
                "pattern": r"(?:nur|lediglich|bloß)\s+(.+)",
                "trigger_type": "restrictive",
                "presupposition": "es gibt andere Alternativen",
            },

            # Kontrafaktische Konditionalen
            {
                "pattern": r"(?:wenn|hätte)\s+(.+?),?\s+(?:wäre|hätte)\s+(.+)",
                "trigger_type": "counterfactual",
                "presupposition": "{0} ist nicht der Fall",
            },
        ]

    def analyze(self, text: str) -> List[Presupposition]:
        """Analysiert Präsuppositionen im Text"""
        results = []
        text_lower = text.lower()

        for trigger in self.triggers:
            match = re.search(trigger["pattern"], text_lower)
            if match:
                # Präsupposition formulieren
                presup = trigger["presupposition"]
                for i, group in enumerate(match.groups()):
                    presup = presup.replace(f"{{{i}}}", group if group else "")

                results.append(Presupposition(
                    trigger=match.group(0),
                    trigger_type=trigger["trigger_type"],
                    presupposed_content=presup,
                    sentence=text,
                    confidence=0.75
                ))

        return results


# =============================================================================
# INTENT SEMANTICS ENGINE (Unified Interface)
# =============================================================================

class IntentSemanticsEngine:
    """
    Vereinte Engine für Intent-Erkennung und Semantische Analyse.
    Kombiniert alle Komponenten.
    """

    def __init__(self):
        self.intent_classifier = AdvancedIntentClassifier()
        self.role_labeler = SemanticRoleLabeler()
        self.implied_detector = ImpliedMeaningDetector()
        self.speech_act_classifier = SpeechActClassifier()
        self.presup_analyzer = PresuppositionAnalyzer()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Vollständige Analyse eines Textes"""
        # Intent klassifizieren
        intent = self.intent_classifier.classify(text)

        # Semantische Rollen
        semantic_frame = self.role_labeler.label(text)

        # Implizierte Bedeutungen
        implied_meanings = self.implied_detector.detect(text)

        # Sprechakt
        speech_act = self.speech_act_classifier.classify(text)

        # Präsuppositionen
        presuppositions = self.presup_analyzer.analyze(text)

        return {
            "intent": {
                "type": intent.intent_type.name,
                "category": intent.category.name,
                "confidence": intent.confidence,
                "keywords": intent.keywords,
                "modifiers": intent.modifiers,
                "slots": intent.slots
            },
            "semantic_frame": {
                "predicate": semantic_frame.predicate,
                "frame_name": semantic_frame.frame_name,
                "roles": [
                    {
                        "type": r.role_type.name,
                        "text": r.text,
                        "head": r.head_word
                    }
                    for r in semantic_frame.roles
                ],
                "confidence": semantic_frame.confidence
            },
            "implied_meanings": [
                {
                    "type": im.implication_type.name,
                    "explicit": im.explicit_text,
                    "implied": im.implied_meaning,
                    "reasoning": im.reasoning
                }
                for im in implied_meanings
            ],
            "speech_act": {
                "type": speech_act.act_type.name,
                "force": speech_act.illocutionary_force,
                "proposition": speech_act.propositional_content,
                "confidence": speech_act.confidence
            },
            "presuppositions": [
                {
                    "trigger": p.trigger,
                    "type": p.trigger_type,
                    "content": p.presupposed_content
                }
                for p in presuppositions
            ],
            "original_text": text
        }

    def get_quick_intent(self, text: str) -> Tuple[str, str, float]:
        """Schnelle Intent-Erkennung: (type, category, confidence)"""
        intent = self.intent_classifier.classify(text)
        return (intent.intent_type.name, intent.category.name, intent.confidence)

    def get_semantic_roles(self, text: str) -> List[Tuple[str, str]]:
        """Gibt Rollen als Liste von (role, text) zurück"""
        frame = self.role_labeler.label(text)
        return [(r.role_type.name, r.text) for r in frame.roles]


# =============================================================================
# SINGLETON INSTANCES & GETTERS
# =============================================================================

_intent_semantics_engine: Optional[IntentSemanticsEngine] = None
_intent_classifier: Optional[AdvancedIntentClassifier] = None
_semantic_role_labeler: Optional[SemanticRoleLabeler] = None


def get_intent_semantics_engine() -> IntentSemanticsEngine:
    """Gibt die Singleton-Instanz der IntentSemanticsEngine zurück"""
    global _intent_semantics_engine
    if _intent_semantics_engine is None:
        _intent_semantics_engine = IntentSemanticsEngine()
        logger.info("IntentSemanticsEngine initialisiert")
    return _intent_semantics_engine


def get_intent_classifier() -> AdvancedIntentClassifier:
    """Gibt die Singleton-Instanz des IntentClassifiers zurück"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = AdvancedIntentClassifier()
        logger.info("AdvancedIntentClassifier initialisiert")
    return _intent_classifier


def get_semantic_role_labeler() -> SemanticRoleLabeler:
    """Gibt die Singleton-Instanz des SemanticRoleLabelers zurück"""
    global _semantic_role_labeler
    if _semantic_role_labeler is None:
        _semantic_role_labeler = SemanticRoleLabeler()
        logger.info("SemanticRoleLabeler initialisiert")
    return _semantic_role_labeler


# =============================================================================
# DEMO & TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO NLP Intent & Semantics - Demo")
    print("=" * 60)

    engine = get_intent_semantics_engine()

    test_sentences = [
        "Könntest du mir bitte das Buch geben?",
        "Maria hat aufgehört zu rauchen.",
        "Ich denke, dass wir schnell handeln müssen.",
        "Das ist ja toll, wieder ein Fehler!",
        "Nachdem er ankam, begann das Meeting.",
        "Einige Studenten haben die Prüfung bestanden.",
        "Wärst du so nett, mir zu helfen?",
        "Peter gibt seiner Schwester das Geschenk.",
        "Ich verspreche, morgen pünktlich zu sein.",
        "Entschuldigung, ich habe mich verspätet.",
    ]

    for sentence in test_sentences:
        print(f"\n{'─' * 50}")
        print(f"INPUT: {sentence}")
        print(f"{'─' * 50}")

        result = engine.analyze(sentence)

        print(f"\nINTENT: {result['intent']['type']} ({result['intent']['category']})")
        print(f"  Confidence: {result['intent']['confidence']:.2f}")
        print(f"  Modifiers: Politeness={result['intent']['modifiers']['politeness']:.1f}, "
              f"Urgency={result['intent']['modifiers']['urgency']:.1f}")

        print(f"\nSEMANTIC FRAME: {result['semantic_frame']['frame_name']}")
        print(f"  Predicate: {result['semantic_frame']['predicate']}")
        for role in result['semantic_frame']['roles']:
            print(f"  - {role['type']}: {role['text']}")

        print(f"\nSPEECH ACT: {result['speech_act']['type']} ({result['speech_act']['force']})")

        if result['implied_meanings']:
            print("\nIMPLIED MEANINGS:")
            for im in result['implied_meanings']:
                print(f"  - {im['implied']} ({im['type']})")

        if result['presuppositions']:
            print("\nPRESUPPOSITIONS:")
            for p in result['presuppositions']:
                print(f"  - {p['content']} (trigger: {p['type']})")

    print("\n" + "=" * 60)
    print("Demo abgeschlossen!")
