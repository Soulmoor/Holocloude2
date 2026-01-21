#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NLP Conversation Intelligence v1.0                                      ║
║  Erweiterte Konversations-Steuerung für Holocloude                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FEATURES:                                                                    ║
║  1. Conversation Flow Manager - Gesprächsfluss steuern                       ║
║  2. Engagement Detector - Ist der Nutzer interessiert?                       ║
║  3. Clarification Generator - Wann und wie nachfragen?                       ║
║  4. Turn-Taking Manager - Sprecherwechsel-Logik                              ║
║  5. Repair Detector - Kommunikationsprobleme erkennen                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Optimiert für Raspberry Pi - Keine schweren ML-Bibliotheken!                ║
║  Author: Kira & Claude                                                        ║
║  Version: 1.0                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import logging
from typing import Dict, List, Optional, Tuple, Set, Any, Deque
from dataclasses import dataclass, field
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum, auto
import random

logger = logging.getLogger("HoloNLPConversationIntelligence")

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Main Classes
    "ConversationFlowManager",
    "EngagementDetector",
    "ClarificationGenerator",
    "TurnTakingManager",
    "RepairDetector",
    "ConversationIntelligenceEngine",

    # Data Classes
    "ConversationState",
    "EngagementScore",
    "ClarificationRequest",
    "TurnInfo",
    "RepairSignal",
    "FlowRecommendation",

    # Enums
    "ConversationPhase",
    "EngagementLevel",
    "ClarificationType",
    "TurnType",
    "RepairType",
    "FlowAction",

    # Getter Functions
    "get_conversation_intelligence_engine",
    "get_engagement_detector",
    "get_clarification_generator",
]

# =============================================================================
# ENUMS
# =============================================================================

class ConversationPhase(Enum):
    """Phasen einer Konversation"""
    OPENING = auto()        # Eröffnung, Begrüßung
    INTRODUCTION = auto()   # Themeneinführung
    DEVELOPMENT = auto()    # Hauptteil, Themenentwicklung
    NEGOTIATION = auto()    # Verhandlung, Diskussion
    RESOLUTION = auto()     # Auflösung, Zusammenfassung
    CLOSING = auto()        # Abschluss, Verabschiedung
    DIGRESSION = auto()     # Abschweifung
    REPAIR = auto()         # Reparatur/Klärung


class EngagementLevel(Enum):
    """Engagement-Stufen"""
    VERY_LOW = 1      # Desinteressiert, einsilbig
    LOW = 2           # Wenig Interesse
    MODERATE = 3      # Neutrales Engagement
    HIGH = 4          # Aktiv interessiert
    VERY_HIGH = 5     # Sehr engagiert, enthusiastisch


class ClarificationType(Enum):
    """Arten von Klärungsfragen"""
    CONFIRMATION = auto()       # Bestätigung erfragen
    SPECIFICATION = auto()      # Genauere Angaben
    DEFINITION = auto()         # Begriff klären
    EXAMPLE = auto()            # Beispiel erfragen
    REFORMULATION = auto()      # Umformulierung anbieten
    DISAMBIGUATION = auto()     # Mehrdeutigkeit klären
    MISSING_INFO = auto()       # Fehlende Information
    VERIFICATION = auto()       # Verifikation
    ELABORATION = auto()        # Mehr Details erfragen


class TurnType(Enum):
    """Arten von Gesprächsbeiträgen"""
    INITIATION = auto()     # Gesprächseröffnung
    RESPONSE = auto()       # Antwort
    FOLLOW_UP = auto()      # Nachfrage
    BACKCHANNEL = auto()    # Hörerrückmeldung (mhm, ja, verstehe)
    INTERRUPTION = auto()   # Unterbrechung
    CONTINUATION = auto()   # Fortführung
    CLOSING_BID = auto()    # Abschlussversuch


class RepairType(Enum):
    """Arten von Reparatur-Signalen"""
    SELF_REPAIR = auto()         # Selbstkorrektur
    OTHER_INITIATED = auto()     # Durch anderen initiiert
    CLARIFICATION_REQUEST = auto()  # Klärungsanfrage
    CORRECTION = auto()          # Korrektur
    REPETITION_REQUEST = auto()  # Wiederholungsanfrage
    UNDERSTANDING_CHECK = auto() # Verständnischeck


class FlowAction(Enum):
    """Empfohlene Aktionen für Gesprächsfluss"""
    CONTINUE = auto()           # Weitermachen
    ASK_CLARIFICATION = auto()  # Nachfragen
    SUMMARIZE = auto()          # Zusammenfassen
    CHANGE_TOPIC = auto()       # Thema wechseln
    DEEPEN = auto()             # Thema vertiefen
    WRAP_UP = auto()            # Zum Abschluss kommen
    RE_ENGAGE = auto()          # Wieder einbinden
    ACKNOWLEDGE = auto()        # Bestätigen
    REPAIR = auto()             # Reparieren/Klären
    WAIT = auto()               # Warten/Pause


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ConversationState:
    """Aktueller Zustand der Konversation"""
    phase: ConversationPhase
    turn_count: int
    topic_depth: int  # Wie tief im Thema (0=oberflächlich, 5=sehr tief)
    coherence_score: float  # 0-1, wie kohärent ist das Gespräch
    engagement_trend: str  # "rising", "stable", "declining"
    last_speaker: str
    pending_questions: List[str]
    unresolved_issues: List[str]


@dataclass
class EngagementScore:
    """Engagement-Bewertung"""
    level: EngagementLevel
    score: float  # 0.0 - 1.0
    indicators: Dict[str, float]
    trend: str  # "rising", "stable", "declining"
    recommendations: List[str]


@dataclass
class ClarificationRequest:
    """Eine generierte Klärungsfrage"""
    clarification_type: ClarificationType
    question: str
    target_text: str  # Was soll geklärt werden
    urgency: float  # 0.0 - 1.0
    alternatives: List[str]  # Alternative Formulierungen


@dataclass
class TurnInfo:
    """Information über einen Gesprächsbeitrag"""
    turn_type: TurnType
    speaker: str
    text: str
    timestamp: datetime
    response_to: Optional[int]  # Index des vorherigen Turns
    completeness: float  # Wie vollständig ist der Beitrag
    relevance: float  # Wie relevant zum Thema


@dataclass
class RepairSignal:
    """Ein erkanntes Reparatur-Signal"""
    repair_type: RepairType
    trigger_text: str
    repair_text: str
    position: int
    success: bool  # War die Reparatur erfolgreich?


@dataclass
class FlowRecommendation:
    """Empfehlung für den Gesprächsfluss"""
    action: FlowAction
    reason: str
    priority: float  # 0.0 - 1.0
    suggested_utterances: List[str]


# =============================================================================
# CONVERSATION FLOW MANAGER
# =============================================================================

class ConversationFlowManager:
    """
    Steuert und analysiert den Gesprächsfluss.
    Erkennt Phasen und gibt Empfehlungen.
    """

    def __init__(self, max_history: int = 100):
        self.turns: Deque[TurnInfo] = deque(maxlen=max_history)
        self.current_phase = ConversationPhase.OPENING
        self.topic_stack: List[str] = []
        self.pending_questions: List[str] = []
        self.max_history = max_history

        # Phase-Indikatoren
        self.phase_markers = self._build_phase_markers()

        # Flow-Regeln
        self.flow_rules = self._build_flow_rules()

    def _build_phase_markers(self) -> Dict[ConversationPhase, List[str]]:
        """Marker für verschiedene Konversationsphasen"""
        return {
            ConversationPhase.OPENING: [
                "hallo", "hi", "hey", "guten tag", "guten morgen", "guten abend",
                "moin", "servus", "grüß", "willkommen"
            ],
            ConversationPhase.INTRODUCTION: [
                "ich möchte", "es geht um", "ich habe eine frage", "kannst du mir",
                "ich brauche hilfe", "ich suche", "könntest du"
            ],
            ConversationPhase.DEVELOPMENT: [
                "und dann", "außerdem", "zusätzlich", "weiterhin", "darüber hinaus",
                "in diesem zusammenhang", "was noch wichtig ist"
            ],
            ConversationPhase.NEGOTIATION: [
                "aber", "jedoch", "andererseits", "ich denke", "meine meinung",
                "vielleicht", "alternative", "was wenn"
            ],
            ConversationPhase.RESOLUTION: [
                "also", "zusammenfassend", "das bedeutet", "im ergebnis",
                "wir haben also", "es ist klar", "die lösung"
            ],
            ConversationPhase.CLOSING: [
                "danke", "vielen dank", "auf wiedersehen", "tschüss", "bis bald",
                "das war alles", "keine weiteren fragen", "bis dann"
            ],
            ConversationPhase.DIGRESSION: [
                "übrigens", "apropos", "nebenbei", "da fällt mir ein",
                "kurz abschweifend", "bevor ich vergesse"
            ],
            ConversationPhase.REPAIR: [
                "was meinst du", "verstehe ich richtig", "kannst du das wiederholen",
                "ich verstehe nicht", "wie bitte", "was genau"
            ]
        }

    def _build_flow_rules(self) -> List[Dict[str, Any]]:
        """Regeln für Fluss-Empfehlungen"""
        return [
            {
                "condition": lambda state: len(self.pending_questions) > 2,
                "action": FlowAction.ASK_CLARIFICATION,
                "reason": "Mehrere offene Fragen",
                "priority": 0.8
            },
            {
                "condition": lambda state: state.topic_depth > 3 and state.turn_count > 10,
                "action": FlowAction.SUMMARIZE,
                "reason": "Tiefe Diskussion, Zusammenfassung sinnvoll",
                "priority": 0.6
            },
            {
                "condition": lambda state: state.engagement_trend == "declining",
                "action": FlowAction.RE_ENGAGE,
                "reason": "Engagement sinkt",
                "priority": 0.9
            },
            {
                "condition": lambda state: state.phase == ConversationPhase.DIGRESSION and state.turn_count > 5,
                "action": FlowAction.CHANGE_TOPIC,
                "reason": "Lange Abschweifung, zurück zum Thema",
                "priority": 0.7
            },
            {
                "condition": lambda state: state.coherence_score < 0.4,
                "action": FlowAction.REPAIR,
                "reason": "Geringe Kohärenz, Klärung nötig",
                "priority": 0.85
            }
        ]

    def add_turn(self, text: str, speaker: str = "user") -> TurnInfo:
        """Fügt einen neuen Gesprächsbeitrag hinzu"""
        turn_type = self._detect_turn_type(text)

        turn = TurnInfo(
            turn_type=turn_type,
            speaker=speaker,
            text=text,
            timestamp=datetime.now(),
            response_to=len(self.turns) - 1 if self.turns else None,
            completeness=self._assess_completeness(text),
            relevance=self._assess_relevance(text)
        )

        self.turns.append(turn)

        # Phase aktualisieren
        self._update_phase(text)

        # Fragen tracken
        if "?" in text and speaker == "assistant":
            self.pending_questions.append(text)
        elif speaker == "user" and self.pending_questions:
            # User hat geantwortet, Frage als beantwortet markieren
            self.pending_questions.pop(0) if self.pending_questions else None

        return turn

    def _detect_turn_type(self, text: str) -> TurnType:
        """Erkennt den Typ des Gesprächsbeitrags"""
        text_lower = text.lower()

        # Backchannel
        backchannel_words = ["mhm", "aha", "ja", "okay", "verstehe", "klar", "genau"]
        if text_lower.strip() in backchannel_words or len(text.split()) <= 2:
            return TurnType.BACKCHANNEL

        # Initiation (bei wenig vorherigen Turns)
        if len(self.turns) < 2:
            return TurnType.INITIATION

        # Follow-up (enthält Bezug auf vorheriges)
        follow_up_markers = ["dazu", "darauf", "dabei", "deshalb", "das", "dies"]
        if any(m in text_lower for m in follow_up_markers):
            return TurnType.FOLLOW_UP

        # Closing Bid
        closing_markers = ["danke", "das war alles", "tschüss", "auf wiedersehen"]
        if any(m in text_lower for m in closing_markers):
            return TurnType.CLOSING_BID

        # Default: Response
        return TurnType.RESPONSE

    def _update_phase(self, text: str) -> None:
        """Aktualisiert die Konversationsphase"""
        text_lower = text.lower()

        for phase, markers in self.phase_markers.items():
            if any(m in text_lower for m in markers):
                self.current_phase = phase
                return

    def _assess_completeness(self, text: str) -> float:
        """Bewertet wie vollständig ein Beitrag ist"""
        # Heuristiken für Vollständigkeit
        score = 0.5

        # Mindestlänge
        if len(text.split()) >= 5:
            score += 0.2

        # Endet mit Satzzeichen
        if text.strip()[-1:] in ".!?":
            score += 0.1

        # Enthält Verb (vereinfacht)
        verb_endings = ["en", "st", "t", "te", "ten"]
        words = text.lower().split()
        if any(w.endswith(e) for w in words for e in verb_endings):
            score += 0.2

        return min(1.0, score)

    def _assess_relevance(self, text: str) -> float:
        """Bewertet wie relevant ein Beitrag zum aktuellen Thema ist"""
        if not self.topic_stack:
            return 0.5

        current_topic = self.topic_stack[-1] if self.topic_stack else ""
        text_lower = text.lower()

        # Einfache Wortüberlappung
        topic_words = set(current_topic.lower().split())
        text_words = set(text_lower.split())

        if not topic_words:
            return 0.5

        overlap = len(topic_words & text_words)
        return min(1.0, overlap / len(topic_words) + 0.3)

    def get_state(self) -> ConversationState:
        """Gibt den aktuellen Konversationszustand zurück"""
        # Engagement-Trend berechnen
        if len(self.turns) < 5:
            trend = "stable"
        else:
            recent_completeness = [t.completeness for t in list(self.turns)[-5:]]
            if recent_completeness[-1] > recent_completeness[0] + 0.1:
                trend = "rising"
            elif recent_completeness[-1] < recent_completeness[0] - 0.1:
                trend = "declining"
            else:
                trend = "stable"

        # Kohärenz berechnen
        relevances = [t.relevance for t in self.turns]
        coherence = sum(relevances) / len(relevances) if relevances else 0.5

        return ConversationState(
            phase=self.current_phase,
            turn_count=len(self.turns),
            topic_depth=len(self.topic_stack),
            coherence_score=coherence,
            engagement_trend=trend,
            last_speaker=self.turns[-1].speaker if self.turns else "",
            pending_questions=self.pending_questions.copy(),
            unresolved_issues=[]  # Könnte erweitert werden
        )

    def get_recommendations(self) -> List[FlowRecommendation]:
        """Gibt Empfehlungen für den weiteren Gesprächsverlauf"""
        state = self.get_state()
        recommendations = []

        for rule in self.flow_rules:
            if rule["condition"](state):
                rec = FlowRecommendation(
                    action=rule["action"],
                    reason=rule["reason"],
                    priority=rule["priority"],
                    suggested_utterances=self._generate_suggestions(rule["action"])
                )
                recommendations.append(rec)

        # Nach Priorität sortieren
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        return recommendations[:3]

    def _generate_suggestions(self, action: FlowAction) -> List[str]:
        """Generiert Vorschläge für eine bestimmte Aktion"""
        suggestions = {
            FlowAction.ASK_CLARIFICATION: [
                "Könntest du das genauer erläutern?",
                "Was meinst du damit genau?",
                "Kannst du ein Beispiel geben?"
            ],
            FlowAction.SUMMARIZE: [
                "Lass mich kurz zusammenfassen...",
                "Bis hierhin haben wir also...",
                "Um das Bisherige zu sammeln..."
            ],
            FlowAction.CHANGE_TOPIC: [
                "Lass uns zum eigentlichen Thema zurückkommen.",
                "Aber zurück zu unserem Thema...",
                "Um wieder auf den Punkt zu kommen..."
            ],
            FlowAction.RE_ENGAGE: [
                "Was denkst du dazu?",
                "Gibt es noch etwas, das dich interessiert?",
                "Hast du noch Fragen?"
            ],
            FlowAction.REPAIR: [
                "Ich glaube, ich habe dich nicht richtig verstanden.",
                "Lass mich sicherstellen, dass ich richtig verstehe...",
                "Meinst du damit...?"
            ],
            FlowAction.WRAP_UP: [
                "Gibt es noch etwas, worüber wir sprechen sollten?",
                "Haben wir alles Wichtige besprochen?",
                "Ist sonst noch etwas offen?"
            ]
        }

        return suggestions.get(action, ["Wie kann ich weiterhelfen?"])

    def push_topic(self, topic: str) -> None:
        """Fügt ein neues Thema zum Stack hinzu"""
        self.topic_stack.append(topic)

    def pop_topic(self) -> Optional[str]:
        """Entfernt das aktuelle Thema vom Stack"""
        return self.topic_stack.pop() if self.topic_stack else None


# =============================================================================
# ENGAGEMENT DETECTOR
# =============================================================================

class EngagementDetector:
    """
    Erkennt und misst das Engagement des Nutzers.
    """

    def __init__(self):
        self.engagement_history: List[float] = []
        self.max_history = 20

        # Engagement-Indikatoren
        self.positive_indicators = [
            "interessant", "spannend", "toll", "super", "genau", "verstehe",
            "erzähl mir mehr", "mehr dazu", "wie funktioniert", "warum"
        ]

        self.negative_indicators = [
            "langweilig", "egal", "verstehe nicht", "was auch immer",
            "hmm", "okay", "ja", "nein", "gut", "ähm"
        ]

        self.high_engagement_patterns = [
            r"\?.*\?",  # Mehrere Fragen
            r"!+",  # Ausrufezeichen
            r"\b(toll|super|genial|wow|interessant)\b"
        ]

        self.low_engagement_patterns = [
            r"^(ja|nein|okay|ok|gut|hm+)\.?$",  # Einsilbige Antworten
            r"^.{1,10}$"  # Sehr kurze Antworten
        ]

    def detect(self, text: str, response_time: Optional[float] = None) -> EngagementScore:
        """Ermittelt das Engagement-Level für einen Text"""
        text_lower = text.lower()
        indicators = {}

        # Textlänge-Indikator
        word_count = len(text.split())
        indicators["length"] = min(1.0, word_count / 30)

        # Positive Marker
        positive_count = sum(1 for p in self.positive_indicators if p in text_lower)
        indicators["positive_markers"] = min(1.0, positive_count * 0.2)

        # Negative Marker
        negative_count = sum(1 for n in self.negative_indicators if text_lower.strip() == n)
        indicators["negative_markers"] = max(0.0, 1.0 - negative_count * 0.3)

        # Pattern-basiert
        high_match = any(re.search(p, text_lower) for p in self.high_engagement_patterns)
        low_match = any(re.search(p, text_lower) for p in self.low_engagement_patterns)

        if high_match:
            indicators["patterns"] = 0.8
        elif low_match:
            indicators["patterns"] = 0.2
        else:
            indicators["patterns"] = 0.5

        # Fragen-Indikator (Fragen zeigen Interesse)
        question_count = text.count("?")
        indicators["questions"] = min(1.0, question_count * 0.3)

        # Elaboration (Details zeigen Engagement)
        elaboration_markers = ["weil", "da", "denn", "nämlich", "zum beispiel"]
        elaboration_count = sum(1 for m in elaboration_markers if m in text_lower)
        indicators["elaboration"] = min(1.0, elaboration_count * 0.25)

        # Antwortzeit (falls verfügbar)
        if response_time is not None:
            # Schnelle Antworten können hohes Engagement zeigen
            if response_time < 2.0:
                indicators["response_time"] = 0.8
            elif response_time < 5.0:
                indicators["response_time"] = 0.6
            else:
                indicators["response_time"] = 0.4

        # Gesamtscore berechnen
        weights = {
            "length": 0.2,
            "positive_markers": 0.2,
            "negative_markers": 0.15,
            "patterns": 0.15,
            "questions": 0.15,
            "elaboration": 0.1,
            "response_time": 0.05
        }

        score = sum(indicators.get(k, 0.5) * w for k, w in weights.items())
        score = max(0.0, min(1.0, score))

        # In Historie eintragen
        self.engagement_history.append(score)
        if len(self.engagement_history) > self.max_history:
            self.engagement_history.pop(0)

        # Level bestimmen
        level = self._score_to_level(score)

        # Trend berechnen
        trend = self._calculate_trend()

        # Empfehlungen generieren
        recommendations = self._generate_recommendations(level, indicators)

        return EngagementScore(
            level=level,
            score=score,
            indicators=indicators,
            trend=trend,
            recommendations=recommendations
        )

    def _score_to_level(self, score: float) -> EngagementLevel:
        """Konvertiert Score zu Engagement-Level"""
        if score >= 0.8:
            return EngagementLevel.VERY_HIGH
        elif score >= 0.6:
            return EngagementLevel.HIGH
        elif score >= 0.4:
            return EngagementLevel.MODERATE
        elif score >= 0.2:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.VERY_LOW

    def _calculate_trend(self) -> str:
        """Berechnet den Engagement-Trend"""
        if len(self.engagement_history) < 3:
            return "stable"

        recent = self.engagement_history[-3:]
        if recent[-1] > recent[0] + 0.15:
            return "rising"
        elif recent[-1] < recent[0] - 0.15:
            return "declining"
        return "stable"

    def _generate_recommendations(self, level: EngagementLevel,
                                  indicators: Dict[str, float]) -> List[str]:
        """Generiert Empfehlungen basierend auf Engagement"""
        recommendations = []

        if level in [EngagementLevel.VERY_LOW, EngagementLevel.LOW]:
            recommendations.append("Versuche, offene Fragen zu stellen")
            recommendations.append("Biete interessante Details oder Beispiele an")
            if indicators.get("length", 0) < 0.3:
                recommendations.append("Nutzer gibt kurze Antworten - nachfragen hilft")

        elif level == EngagementLevel.MODERATE:
            recommendations.append("Engagement ist neutral - Themenvertiefung könnte helfen")

        elif level in [EngagementLevel.HIGH, EngagementLevel.VERY_HIGH]:
            recommendations.append("Hohes Engagement - Nutzer weiter einbinden")
            recommendations.append("Auf die Energie eingehen und vertiefen")

        return recommendations

    def get_average_engagement(self) -> float:
        """Gibt das durchschnittliche Engagement zurück"""
        if not self.engagement_history:
            return 0.5
        return sum(self.engagement_history) / len(self.engagement_history)


# =============================================================================
# CLARIFICATION GENERATOR
# =============================================================================

class ClarificationGenerator:
    """
    Generiert Klärungsfragen basierend auf erkannten Unklarheiten.
    """

    def __init__(self):
        # Templates für verschiedene Klärungstypen
        self.templates = self._build_templates()

        # Unklarheits-Trigger
        self.ambiguity_patterns = self._build_ambiguity_patterns()

    def _build_templates(self) -> Dict[ClarificationType, List[str]]:
        """Templates für Klärungsfragen"""
        return {
            ClarificationType.CONFIRMATION: [
                "Meinst du damit, dass {target}?",
                "Verstehe ich richtig, dass {target}?",
                "Soll das heißen, dass {target}?",
                "Du meinst also {target}, richtig?"
            ],
            ClarificationType.SPECIFICATION: [
                "Kannst du {target} genauer beschreiben?",
                "Was genau meinst du mit {target}?",
                "Könntest du {target} näher erläutern?",
                "Wie genau sieht {target} aus?"
            ],
            ClarificationType.DEFINITION: [
                "Was verstehst du unter {target}?",
                "Wie definierst du {target}?",
                "Was bedeutet {target} für dich?"
            ],
            ClarificationType.EXAMPLE: [
                "Kannst du ein Beispiel für {target} geben?",
                "Wie würde das konkret aussehen?",
                "Hast du ein Beispiel dafür?"
            ],
            ClarificationType.REFORMULATION: [
                "Lass mich sicherstellen: Du sagst, dass {target}?",
                "Mit anderen Worten: {target}?",
                "Also zusammengefasst: {target}?"
            ],
            ClarificationType.DISAMBIGUATION: [
                "Meinst du {option1} oder {option2}?",
                "Bezieht sich das auf {option1} oder auf {option2}?",
                "Welches {target} meinst du genau?"
            ],
            ClarificationType.MISSING_INFO: [
                "Was ist {missing}?",
                "Du hast nicht erwähnt, {missing}. Kannst du das ergänzen?",
                "Mir fehlt noch die Information zu {missing}."
            ],
            ClarificationType.VERIFICATION: [
                "Ist es korrekt, dass {target}?",
                "Stimmt es, dass {target}?",
                "Kann ich davon ausgehen, dass {target}?"
            ],
            ClarificationType.ELABORATION: [
                "Kannst du mehr über {target} erzählen?",
                "Was noch zu {target}?",
                "Gibt es noch mehr zu {target} zu sagen?"
            ]
        }

    def _build_ambiguity_patterns(self) -> List[Dict[str, Any]]:
        """Patterns die auf Unklarheit hindeuten"""
        return [
            {
                "pattern": r"\b(das|dies|es|so etwas|sowas)\b",
                "type": ClarificationType.SPECIFICATION,
                "reason": "Vages Pronomen"
            },
            {
                "pattern": r"\b(irgendwie|irgendwas|irgendwo|irgendjemand)\b",
                "type": ClarificationType.SPECIFICATION,
                "reason": "Unbestimmtes Pronomen"
            },
            {
                "pattern": r"\b(oder so|und so|etc|usw)\b",
                "type": ClarificationType.EXAMPLE,
                "reason": "Unspezifische Aufzählung"
            },
            {
                "pattern": r"\b(ding|sache|zeug)\b",
                "type": ClarificationType.DEFINITION,
                "reason": "Allgemeiner Begriff"
            },
            {
                "pattern": r"\b(vielleicht|eventuell|möglicherweise)\b",
                "type": ClarificationType.CONFIRMATION,
                "reason": "Unsicherheitsmarker"
            },
            {
                "pattern": r"\b(groß|klein|viel|wenig|schnell|langsam)\b(?!\w)",
                "type": ClarificationType.SPECIFICATION,
                "reason": "Relatives Adjektiv"
            },
            {
                "pattern": r"\b(bald|später|neulich|kürzlich)\b",
                "type": ClarificationType.SPECIFICATION,
                "reason": "Unspezifische Zeitangabe"
            }
        ]

    def analyze_need_for_clarification(self, text: str) -> List[Dict[str, Any]]:
        """Analysiert ob Klärungsbedarf besteht"""
        text_lower = text.lower()
        needs = []

        for pattern_info in self.ambiguity_patterns:
            matches = re.finditer(pattern_info["pattern"], text_lower)
            for match in matches:
                needs.append({
                    "type": pattern_info["type"],
                    "reason": pattern_info["reason"],
                    "text": match.group(0),
                    "position": match.start(),
                    "urgency": 0.6
                })

        # Sehr kurze Aussagen brauchen oft Klärung
        if len(text.split()) < 4 and "?" not in text:
            needs.append({
                "type": ClarificationType.ELABORATION,
                "reason": "Sehr kurze Aussage",
                "text": text,
                "position": 0,
                "urgency": 0.5
            })

        return needs

    def generate(self, text: str, clarification_type: Optional[ClarificationType] = None) -> ClarificationRequest:
        """Generiert eine Klärungsfrage"""
        # Typ automatisch bestimmen falls nicht angegeben
        if clarification_type is None:
            needs = self.analyze_need_for_clarification(text)
            if needs:
                clarification_type = needs[0]["type"]
                target_text = needs[0]["text"]
            else:
                clarification_type = ClarificationType.ELABORATION
                target_text = text
        else:
            target_text = text

        # Template auswählen
        templates = self.templates.get(clarification_type, self.templates[ClarificationType.SPECIFICATION])
        template = random.choice(templates)

        # Frage generieren
        question = template.replace("{target}", target_text)
        question = question.replace("{missing}", "diese Information")
        question = question.replace("{option1}", "Option A")
        question = question.replace("{option2}", "Option B")

        # Alternativen generieren
        alternatives = [
            t.replace("{target}", target_text).replace("{missing}", "diese Information")
            for t in templates if t != template
        ][:2]

        return ClarificationRequest(
            clarification_type=clarification_type,
            question=question,
            target_text=target_text,
            urgency=0.6,
            alternatives=alternatives
        )

    def should_ask_clarification(self, text: str, engagement_level: EngagementLevel) -> bool:
        """Entscheidet ob eine Klärungsfrage gestellt werden sollte"""
        needs = self.analyze_need_for_clarification(text)

        if not needs:
            return False

        # Bei niedrigem Engagement vorsichtiger mit Fragen
        if engagement_level in [EngagementLevel.VERY_LOW, EngagementLevel.LOW]:
            return any(n["urgency"] > 0.7 for n in needs)

        return any(n["urgency"] > 0.5 for n in needs)


# =============================================================================
# TURN-TAKING MANAGER
# =============================================================================

class TurnTakingManager:
    """
    Verwaltet Sprecherwechsel und Turn-Taking-Signale.
    """

    def __init__(self):
        self.current_speaker = None
        self.turn_history: List[TurnInfo] = []

        # Turn-Yielding-Signale (Abgabe des Rederechts)
        self.yield_signals = [
            r"\?$",  # Frage
            r"was denkst du",
            r"oder\?$",
            r"meinst du nicht",
            r"verstehst du"
        ]

        # Turn-Holding-Signale (Behalten des Rederechts)
        self.hold_signals = [
            r"\.\.\.$",
            r"und zwar",
            r"erstens",
            r"außerdem",
            r"noch ein punkt"
        ]

    def analyze_turn(self, text: str, speaker: str) -> Dict[str, Any]:
        """Analysiert einen Turn"""
        text_lower = text.lower()

        # Prüfe auf Yield-Signale
        yielding = any(re.search(p, text_lower) for p in self.yield_signals)

        # Prüfe auf Hold-Signale
        holding = any(re.search(p, text_lower) for p in self.hold_signals)

        # Turn-Länge analysieren
        word_count = len(text.split())

        return {
            "speaker": speaker,
            "yielding": yielding,
            "holding": holding,
            "word_count": word_count,
            "complete": not holding and (yielding or text.strip()[-1] in ".!?"),
            "expects_response": yielding or "?" in text
        }

    def should_take_turn(self, last_user_text: str) -> bool:
        """Entscheidet ob der Assistent antworten sollte"""
        analysis = self.analyze_turn(last_user_text, "user")

        # Ja, wenn User das Rederecht abgibt
        if analysis["yielding"]:
            return True

        # Ja, wenn User fertig scheint
        if analysis["complete"]:
            return True

        return False

    def get_appropriate_response_length(self, user_text: str) -> str:
        """Empfiehlt eine passende Antwortlänge"""
        user_words = len(user_text.split())

        if user_words < 5:
            return "kurz"  # Kurze Fragen, kurze Antworten
        elif user_words < 20:
            return "mittel"
        else:
            return "ausführlich"  # Bei langen Beiträgen auch mehr antworten


# =============================================================================
# REPAIR DETECTOR
# =============================================================================

class RepairDetector:
    """
    Erkennt Reparatur-Signale und Kommunikationsprobleme.
    """

    def __init__(self):
        # Reparatur-Initiatoren
        self.repair_initiators = {
            RepairType.REPETITION_REQUEST: [
                r"wie bitte", r"was hast du gesagt", r"kannst du das wiederholen",
                r"noch einmal bitte", r"hä\?", r"bitte\?"
            ],
            RepairType.CLARIFICATION_REQUEST: [
                r"was meinst du", r"verstehe ich nicht", r"was bedeutet",
                r"wie meinst du das", r"ich verstehe nicht"
            ],
            RepairType.CORRECTION: [
                r"nein,?\s+ich meinte", r"nicht ganz", r"genauer gesagt",
                r"eigentlich", r"um genau zu sein"
            ],
            RepairType.UNDERSTANDING_CHECK: [
                r"verstehst du", r"weißt du was ich meine", r"ist das klar",
                r"machte das sinn", r"kapiert"
            ],
            RepairType.SELF_REPAIR: [
                r"äh,?\s+ich meine", r"also", r"ich meinte",
                r"korrektur", r"entschuldigung,?\s+ich"
            ]
        }

    def detect(self, text: str) -> List[RepairSignal]:
        """Erkennt Reparatur-Signale im Text"""
        text_lower = text.lower()
        signals = []

        for repair_type, patterns in self.repair_initiators.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Reparatur-Text ist der Rest nach dem Initiator
                    repair_text = text_lower[match.end():].strip()

                    signals.append(RepairSignal(
                        repair_type=repair_type,
                        trigger_text=match.group(0),
                        repair_text=repair_text[:50] if repair_text else "",
                        position=match.start(),
                        success=bool(repair_text)  # Erfolgreich wenn Reparatur folgt
                    ))

        return signals

    def needs_repair(self, text: str) -> bool:
        """Prüft ob der Text auf Verständnisprobleme hindeutet"""
        signals = self.detect(text)
        return len(signals) > 0

    def suggest_repair_strategy(self, repair_type: RepairType) -> str:
        """Schlägt eine Reparatur-Strategie vor"""
        strategies = {
            RepairType.REPETITION_REQUEST: "Wiederhole die Information in einfacheren Worten",
            RepairType.CLARIFICATION_REQUEST: "Erkläre den Begriff oder gib ein Beispiel",
            RepairType.CORRECTION: "Bestätige das Verständnis und passe die Antwort an",
            RepairType.UNDERSTANDING_CHECK: "Fasse das Verstandene zusammen zur Bestätigung",
            RepairType.SELF_REPAIR: "Warte auf die Korrektur und reagiere darauf"
        }
        return strategies.get(repair_type, "Nachfragen für mehr Klarheit")


# =============================================================================
# CONVERSATION INTELLIGENCE ENGINE (Unified Interface)
# =============================================================================

class ConversationIntelligenceEngine:
    """
    Vereinte Engine für Konversations-Intelligenz.
    Kombiniert alle Komponenten.
    """

    def __init__(self):
        self.flow_manager = ConversationFlowManager()
        self.engagement_detector = EngagementDetector()
        self.clarification_generator = ClarificationGenerator()
        self.turn_taking = TurnTakingManager()
        self.repair_detector = RepairDetector()

    def process_user_input(self, text: str) -> Dict[str, Any]:
        """Verarbeitet User-Input und gibt Analyse zurück"""
        # Turn hinzufügen
        turn = self.flow_manager.add_turn(text, "user")

        # Engagement messen
        engagement = self.engagement_detector.detect(text)

        # Reparaturbedarf prüfen
        repairs = self.repair_detector.detect(text)

        # Klärungsbedarf prüfen
        clarification_needs = self.clarification_generator.analyze_need_for_clarification(text)

        # Turn-Taking analysieren
        turn_analysis = self.turn_taking.analyze_turn(text, "user")

        # Empfehlungen generieren
        flow_recommendations = self.flow_manager.get_recommendations()

        return {
            "turn_info": {
                "type": turn.turn_type.name,
                "completeness": turn.completeness,
                "relevance": turn.relevance
            },
            "engagement": {
                "level": engagement.level.name,
                "score": engagement.score,
                "trend": engagement.trend,
                "recommendations": engagement.recommendations
            },
            "repair_signals": [
                {
                    "type": r.repair_type.name,
                    "trigger": r.trigger_text
                }
                for r in repairs
            ],
            "clarification_needs": clarification_needs,
            "turn_taking": turn_analysis,
            "flow_state": {
                "phase": self.flow_manager.current_phase.name,
                "turn_count": len(self.flow_manager.turns)
            },
            "recommendations": [
                {
                    "action": r.action.name,
                    "reason": r.reason,
                    "suggestions": r.suggested_utterances
                }
                for r in flow_recommendations
            ]
        }

    def should_clarify(self, text: str) -> Tuple[bool, Optional[ClarificationRequest]]:
        """Entscheidet ob geklärt werden sollte und generiert ggf. Frage"""
        engagement = self.engagement_detector.detect(text)

        if self.clarification_generator.should_ask_clarification(text, engagement.level):
            request = self.clarification_generator.generate(text)
            return True, request

        return False, None

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der Konversation"""
        state = self.flow_manager.get_state()
        avg_engagement = self.engagement_detector.get_average_engagement()

        return {
            "phase": state.phase.name,
            "turn_count": state.turn_count,
            "topic_depth": state.topic_depth,
            "coherence": state.coherence_score,
            "average_engagement": avg_engagement,
            "pending_questions": len(state.pending_questions),
            "engagement_trend": state.engagement_trend
        }

    def add_assistant_response(self, text: str) -> None:
        """Fügt eine Assistenten-Antwort hinzu"""
        self.flow_manager.add_turn(text, "assistant")


# =============================================================================
# SINGLETON INSTANCES & GETTERS
# =============================================================================

_conversation_intelligence_engine: Optional[ConversationIntelligenceEngine] = None
_engagement_detector: Optional[EngagementDetector] = None
_clarification_generator: Optional[ClarificationGenerator] = None


def get_conversation_intelligence_engine() -> ConversationIntelligenceEngine:
    """Gibt die Singleton-Instanz der ConversationIntelligenceEngine zurück"""
    global _conversation_intelligence_engine
    if _conversation_intelligence_engine is None:
        _conversation_intelligence_engine = ConversationIntelligenceEngine()
        logger.info("ConversationIntelligenceEngine initialisiert")
    return _conversation_intelligence_engine


def get_engagement_detector() -> EngagementDetector:
    """Gibt die Singleton-Instanz des EngagementDetectors zurück"""
    global _engagement_detector
    if _engagement_detector is None:
        _engagement_detector = EngagementDetector()
        logger.info("EngagementDetector initialisiert")
    return _engagement_detector


def get_clarification_generator() -> ClarificationGenerator:
    """Gibt die Singleton-Instanz des ClarificationGenerators zurück"""
    global _clarification_generator
    if _clarification_generator is None:
        _clarification_generator = ClarificationGenerator()
        logger.info("ClarificationGenerator initialisiert")
    return _clarification_generator


# =============================================================================
# DEMO & TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO NLP Conversation Intelligence - Demo")
    print("=" * 60)

    engine = get_conversation_intelligence_engine()

    # Simulierte Konversation
    conversation = [
        ("user", "Hallo, ich brauche Hilfe mit etwas."),
        ("assistant", "Hallo! Natürlich, wie kann ich dir helfen?"),
        ("user", "Das Ding funktioniert nicht richtig."),
        ("assistant", "Ich verstehe. Um dir besser helfen zu können - was genau meinst du mit 'das Ding'?"),
        ("user", "Na das mit dem Computer."),
        ("assistant", "Okay, du meinst etwas am Computer. Kannst du beschreiben, was genau nicht funktioniert?"),
        ("user", "Es geht einfach nicht. Ich hab alles versucht!"),
        ("assistant", "Ich verstehe deine Frustration. Erzähl mir mehr - was passiert wenn du es startest?"),
        ("user", "Also, wenn ich den Browser öffne und dann auf diese eine Seite gehe, dann lädt es ewig und dann kommt so ein komischer Fehler. Das ist total nervig!"),
        ("assistant", "Ah, das klingt nach einem Browser-Problem. Der komische Fehler - was steht da genau?"),
        ("user", "Irgendwas mit Timeout oder so ähnlich."),
    ]

    print("\n--- Konversations-Analyse ---\n")

    for speaker, text in conversation:
        print(f"{speaker.upper()}: {text}")

        if speaker == "user":
            result = engine.process_user_input(text)

            print(f"  └── Engagement: {result['engagement']['level']} ({result['engagement']['score']:.2f})")
            print(f"      Turn-Typ: {result['turn_info']['type']}")
            print(f"      Phase: {result['flow_state']['phase']}")

            if result['clarification_needs']:
                print(f"      ⚠️  Klärungsbedarf: {result['clarification_needs'][0]['reason']}")

            if result['repair_signals']:
                print(f"      🔧 Reparatur-Signal: {result['repair_signals'][0]['type']}")

            if result['recommendations']:
                print(f"      💡 Empfehlung: {result['recommendations'][0]['action']}")

        else:
            engine.add_assistant_response(text)

        print()

    print("\n--- Konversations-Zusammenfassung ---")
    summary = engine.get_conversation_summary()
    print(f"Phase: {summary['phase']}")
    print(f"Turns: {summary['turn_count']}")
    print(f"Durchschnittliches Engagement: {summary['average_engagement']:.2f}")
    print(f"Kohärenz: {summary['coherence']:.2f}")
    print(f"Engagement-Trend: {summary['engagement_trend']}")

    print("\n--- Klärungsfragen-Generator Test ---")
    test_texts = [
        "Das ist irgendwie komisch.",
        "Ich will das schnell erledigen.",
        "Die Sache neulich war anders."
    ]

    for text in test_texts:
        should_clarify, request = engine.should_clarify(text)
        print(f"\nInput: \"{text}\"")
        if should_clarify and request:
            print(f"  → Frage: {request.question}")
            print(f"    Typ: {request.clarification_type.name}")

    print("\n" + "=" * 60)
    print("Demo abgeschlossen!")
