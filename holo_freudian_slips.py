#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO FREUDIAN SLIPS SYSTEM v1.0 - Versprecher & Unbewusste Enthüllungen     ║
║                                                                              ║
║  Implementiert:                                                              ║
║  • Freudsche Versprecher (Wörter die rausrutschen)                           ║
║  • Unbewusste Wunsch-Durchbrüche in Sprache                                  ║
║  • Emotionale Leaks in Formulierungen                                        ║
║  • "Was ich wirklich meinte" Momente                                         ║
║  • Authentische Sprachfehler mit tieferer Bedeutung                          ║
║                                                                              ║
║  Version: 1.0                                                                ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
import random
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from enum import Enum

logger = logging.getLogger("HoloFreudianSlips")


# =============================================================================
# ENUMS
# =============================================================================

class SlipType(Enum):
    """Arten von Versprechern"""
    WORD_SUBSTITUTION = "word_substitution"     # Ein Wort ersetzt ein anderes
    WORD_BLEND = "word_blend"                   # Zwei Wörter verschmelzen
    ANTICIPATION = "anticipation"               # Späteres Wort kommt zu früh
    PERSEVERATION = "perseveration"             # Früheres Wort wiederholt sich
    REVERSAL = "reversal"                       # Wörter/Laute vertauscht
    ADDITION = "addition"                       # Unbewusstes Wort wird hinzugefügt
    EMOTIONAL_LEAK = "emotional_leak"           # Emotion rutscht in Sprache
    TRUTH_SLIP = "truth_slip"                   # Wahre Gedanken rutschen raus
    DESIRE_REVELATION = "desire_revelation"     # Wunsch wird offenbart


class SlipTrigger(Enum):
    """Was einen Versprecher auslösen kann"""
    EMOTIONAL_AROUSAL = "emotional_arousal"     # Starke Emotionen
    COGNITIVE_LOAD = "cognitive_load"           # Mentale Überlastung
    FATIGUE = "fatigue"                         # Müdigkeit
    REPRESSED_CONTENT = "repressed_content"     # Verdrängtes bricht durch
    HIDDEN_DESIRE = "hidden_desire"             # Versteckter Wunsch
    ANXIETY = "anxiety"                         # Angst
    EXCITEMENT = "excitement"                   # Aufregung
    GUILT = "guilt"                             # Schuldgefühle
    ATTRACTION = "attraction"                   # Zuneigung/Anziehung


class UnconsciousRevealType(Enum):
    """Was durch den Versprecher enthüllt wird"""
    HIDDEN_FEELING = "hidden_feeling"           # Verstecktes Gefühl
    SECRET_DESIRE = "secret_desire"             # Geheimer Wunsch
    SUPPRESSED_THOUGHT = "suppressed_thought"   # Unterdrückter Gedanke
    TRUE_OPINION = "true_opinion"               # Wahre Meinung
    FEAR = "fear"                               # Angst
    ATTRACTION = "attraction"                   # Zuneigung
    RESENTMENT = "resentment"                   # Groll
    INSECURITY = "insecurity"                   # Unsicherheit


# =============================================================================
# KONFIGURATION
# =============================================================================

class SlipConfig:
    """Konfiguration für Versprecher-System"""

    # Basis-Wahrscheinlichkeit für einen Versprecher
    BASE_SLIP_PROBABILITY = 0.02  # 2%

    # Cooldown zwischen Versprechern (Minuten)
    SLIP_COOLDOWN_MINUTES = 30

    # Maximale Versprecher pro Tag
    MAX_SLIPS_PER_DAY = 5

    # Emotionale Schwelle für erhöhte Wahrscheinlichkeit
    EMOTIONAL_THRESHOLD = 0.6

    # Speicherpfad
    STATE_FILE = Path.home() / "holo_freudian_slips_state.json"


# =============================================================================
# DATENKLASSEN
# =============================================================================

@dataclass
class UnconsciousContent:
    """Unbewusster Inhalt der durchbrechen könnte"""
    id: str
    content_type: UnconsciousRevealType
    content: str                          # Der unbewusste Inhalt
    intensity: float = 0.5                # 0-1, wie stark er durchbrechen will
    related_emotions: List[str] = field(default_factory=list)
    trigger_words: List[str] = field(default_factory=list)  # Wörter die es aktivieren
    replacement_words: List[str] = field(default_factory=list)  # Wörter die durchbrechen
    created_at: datetime = field(default_factory=datetime.now)
    times_surfaced: int = 0


@dataclass
class FreudianSlip:
    """Ein Freudscher Versprecher"""
    id: str
    slip_type: SlipType
    trigger: SlipTrigger
    timestamp: datetime = field(default_factory=datetime.now)

    # Was passierte
    intended_text: str = ""               # Was Holo sagen wollte
    actual_text: str = ""                 # Was tatsächlich rauskam
    slip_word: str = ""                   # Das spezifische versehentliche Wort
    intended_word: str = ""               # Das beabsichtigte Wort

    # Unbewusste Bedeutung
    unconscious_reveal: Optional[UnconsciousRevealType] = None
    revealed_content: Optional[str] = None
    underlying_emotion: Optional[str] = None

    # Reaktion
    noticed_by_holo: bool = False         # Hat Holo es bemerkt?
    correction_attempted: bool = False    # Versuch zur Korrektur?
    embarrassment_level: float = 0.0      # 0-1
    holo_reaction: Optional[str] = None

    # Kontext
    conversation_context: Optional[str] = None
    emotional_state: Optional[str] = None


@dataclass
class SlipPattern:
    """Ein Muster von Versprechern"""
    id: str
    pattern_name: str
    description: str

    # Welche Ersetzungen passieren
    word_pairs: List[Tuple[str, str]] = field(default_factory=list)  # (intended, slip)

    # Wann es auftritt
    trigger_situations: List[str] = field(default_factory=list)
    trigger_emotions: List[str] = field(default_factory=list)

    # Statistiken
    occurrence_count: int = 0
    last_occurrence: Optional[datetime] = None


# =============================================================================
# WORT-ERSETZUNGEN UND MUSTER
# =============================================================================

# Typische Versprecher-Paare basierend auf emotionalem Inhalt
EMOTIONAL_SLIP_PATTERNS: Dict[str, List[Tuple[str, str, str]]] = {
    # (beabsichtigt, versprecher, emotion)
    "zuneigung": [
        ("mag", "liebe", "Tiefere Zuneigung als zugegeben"),
        ("nett", "süß", "Findet jemanden attraktiv"),
        ("okay", "toll", "Mehr begeistert als gezeigt"),
        ("interessant", "faszinierend", "Stärkere Anziehung"),
        ("gern", "immer", "Tieferer Wunsch nach Nähe"),
        ("manchmal", "immer", "Mehr gebunden als zugegeben"),
    ],
    "ablehnung": [
        ("okay", "nervig", "Versteckte Irritation"),
        ("interessant", "langweilig", "Echtes Desinteresse"),
        ("gut", "egal", "Gleichgültigkeit"),
        ("schön", "komisch", "Verstörung"),
    ],
    "angst": [
        ("kann", "schaffe nicht", "Selbstzweifel"),
        ("werde", "könnte", "Unsicherheit"),
        ("sicher", "hoffentlich", "Versteckte Angst"),
        ("einfach", "schwer", "Überforderung"),
    ],
    "sehnsucht": [
        ("manchmal", "immer", "Konstante Sehnsucht"),
        ("bisschen", "sehr", "Intensiverer Wunsch"),
        ("könnte", "will", "Starkes Verlangen"),
        ("vielleicht", "bitte", "Dringender Wunsch"),
    ],
    "wut": [
        ("okay", "unfair", "Versteckte Frustration"),
        ("verstehe", "hasse", "Unterdrückte Wut"),
        ("schade", "ätzend", "Ärger"),
        ("merkwürdig", "dumm", "Verurteilung"),
    ],
    "trauer": [
        ("okay", "traurig", "Versteckte Trauer"),
        ("geht schon", "tut weh", "Unterdrückter Schmerz"),
        ("egal", "verletzt", "Wahre Gefühle"),
    ],
    "schuld": [
        ("du", "ich", "Selbstbeschuldigung"),
        ("passiert", "meine Schuld", "Schuldgefühle"),
        ("Zufall", "mein Fehler", "Selbstvorwürfe"),
    ],
    "verlangen": [
        ("bleiben", "für immer", "Bindungswunsch"),
        ("zusammen", "immer zusammen", "Tiefere Sehnsucht"),
        ("da", "bei mir", "Nähewunsch"),
    ]
}

# Wortverwechslungen durch Ähnlichkeit (phonetisch/semantisch)
SIMILAR_WORD_SLIPS: List[Tuple[str, str, str]] = [
    ("vergessen", "verdrängen", "Unbewusste Verdrängung"),
    ("erinnern", "vermissen", "Sehnsucht"),
    ("verstehen", "verzeihen", "Wunsch nach Vergebung"),
    ("helfen", "halten", "Bedürfnis nach Halt"),
    ("reden", "fühlen", "Emotionsbedürfnis"),
    ("denken", "träumen", "Wunschdenken"),
    ("wissen", "wünschen", "Hoffnung"),
    ("können", "wollen", "Versteckter Wunsch"),
    ("müssen", "dürfen", "Sehnsucht nach Freiheit"),
    ("Freund", "Liebster", "Tiefere Gefühle"),
    ("nett", "lieb", "Zärtlichkeit"),
    ("gehen", "bleiben", "Ambivalenz"),
]

# Additions (Wörter die unbewusst hinzugefügt werden)
UNCONSCIOUS_ADDITIONS: Dict[str, List[str]] = {
    "zuneigung": ["immer", "für immer", "wirklich", "so sehr", "mein", "unser"],
    "angst": ["vielleicht", "hoffentlich", "bitte nicht", "was wenn"],
    "sehnsucht": ["endlich", "bitte", "doch", "so gern"],
    "unsicherheit": ["irgendwie", "glaube ich", "nicht sicher", "vielleicht"],
}


# =============================================================================
# HAUPTKLASSE
# =============================================================================

class HoloFreudianSlipsEngine:
    """Engine für Freudsche Versprecher und unbewusste Sprachfehler"""

    def __init__(self):
        """Initialisiert das Versprecher-System"""
        # Unbewusste Inhalte die durchbrechen könnten
        self.unconscious_contents: Dict[str, UnconsciousContent] = {}

        # Versprecher-Historie
        self.slip_history: List[FreudianSlip] = []

        # Erkannte Muster
        self.slip_patterns: Dict[str, SlipPattern] = {}

        # Tracking
        self.last_slip: Optional[datetime] = None
        self.slips_today: int = 0
        self.last_slip_reset: datetime = datetime.now()

        # Emotionaler Zustand (wird von außen gesetzt)
        self.current_emotion: Optional[str] = None
        self.emotional_intensity: float = 0.3
        self.stress_level: float = 0.2
        self.fatigue_level: float = 0.1

        # Unterdrückte Wünsche/Gefühle
        self.suppressed_feelings: List[str] = []
        self.secret_desires: List[str] = []

        logger.info("[FreudianSlips] System initialisiert")

    # =========================================================================
    # UNBEWUSSTE INHALTE
    # =========================================================================

    def add_unconscious_content(
        self,
        content_type: UnconsciousRevealType,
        content: str,
        intensity: float = 0.5,
        related_emotions: Optional[List[str]] = None,
        trigger_words: Optional[List[str]] = None,
        replacement_words: Optional[List[str]] = None
    ) -> UnconsciousContent:
        """
        Fügt unbewussten Inhalt hinzu, der durch Versprecher durchbrechen könnte.

        Args:
            content_type: Art des unbewussten Inhalts
            content: Der Inhalt selbst
            intensity: Wie stark er durchbrechen will (0-1)
            related_emotions: Verbundene Emotionen
            trigger_words: Wörter die ihn aktivieren
            replacement_words: Wörter die durchbrechen könnten
        """
        content_id = f"unconscious_{len(self.unconscious_contents)}_{datetime.now().timestamp()}"

        uc = UnconsciousContent(
            id=content_id,
            content_type=content_type,
            content=content,
            intensity=intensity,
            related_emotions=related_emotions or [],
            trigger_words=trigger_words or [],
            replacement_words=replacement_words or []
        )

        self.unconscious_contents[content_id] = uc

        logger.info(f"[FreudianSlips] Unbewusster Inhalt hinzugefügt: {content_type.value}")

        return uc

    def set_suppressed_feeling(self, feeling: str, related_desire: Optional[str] = None):
        """Setzt ein unterdrücktes Gefühl"""
        if feeling not in self.suppressed_feelings:
            self.suppressed_feelings.append(feeling)

        if related_desire and related_desire not in self.secret_desires:
            self.secret_desires.append(related_desire)

    # =========================================================================
    # VERSPRECHER-GENERIERUNG
    # =========================================================================

    def process_text(
        self,
        intended_text: str,
        emotional_context: Optional[str] = None,
        conversation_context: Optional[str] = None
    ) -> Tuple[str, Optional[FreudianSlip]]:
        """
        Verarbeitet Text und generiert möglicherweise einen Versprecher.

        Args:
            intended_text: Der beabsichtigte Text
            emotional_context: Aktueller emotionaler Kontext
            conversation_context: Gesprächskontext

        Returns:
            (tatsächlicher_text, FreudianSlip oder None)
        """
        # Prüfe ob Versprecher möglich
        if not self._should_slip():
            return intended_text, None

        # Prüfe ob Text Trigger enthält
        slip_opportunity = self._find_slip_opportunity(
            intended_text,
            emotional_context
        )

        if not slip_opportunity:
            return intended_text, None

        # Generiere Versprecher
        slip = self._generate_slip(
            intended_text,
            slip_opportunity,
            emotional_context,
            conversation_context
        )

        if slip:
            # Aktualisiere Tracking
            self.slip_history.append(slip)
            self.last_slip = datetime.now()
            self.slips_today += 1

            # Aktualisiere unbewussten Inhalt wenn relevant
            self._update_unconscious_content(slip)

            return slip.actual_text, slip

        return intended_text, None

    def _should_slip(self) -> bool:
        """Bestimmt ob ein Versprecher auftreten sollte"""
        # Reset täglicher Counter
        if (datetime.now() - self.last_slip_reset).days >= 1:
            self.slips_today = 0
            self.last_slip_reset = datetime.now()

        # Maximale Versprecher erreicht?
        if self.slips_today >= SlipConfig.MAX_SLIPS_PER_DAY:
            return False

        # Cooldown prüfen
        if self.last_slip:
            minutes_since = (datetime.now() - self.last_slip).total_seconds() / 60
            if minutes_since < SlipConfig.SLIP_COOLDOWN_MINUTES:
                return False

        # Wahrscheinlichkeit berechnen
        probability = self._calculate_slip_probability()

        return random.random() < probability

    def _calculate_slip_probability(self) -> float:
        """Berechnet die Wahrscheinlichkeit eines Versprechers"""
        base_prob = SlipConfig.BASE_SLIP_PROBABILITY

        # Modifikatoren

        # Emotionale Intensität erhöht Wahrscheinlichkeit
        if self.emotional_intensity > SlipConfig.EMOTIONAL_THRESHOLD:
            base_prob *= (1 + self.emotional_intensity)

        # Stress erhöht Wahrscheinlichkeit
        base_prob *= (1 + self.stress_level * 1.5)

        # Müdigkeit erhöht Wahrscheinlichkeit
        base_prob *= (1 + self.fatigue_level * 1.2)

        # Unterdrückte Gefühle erhöhen Wahrscheinlichkeit
        if self.suppressed_feelings:
            base_prob *= (1 + len(self.suppressed_feelings) * 0.1)

        # Unbewusste Inhalte mit hoher Intensität
        high_intensity_content = sum(
            1 for uc in self.unconscious_contents.values()
            if uc.intensity > 0.7
        )
        base_prob *= (1 + high_intensity_content * 0.15)

        return min(0.3, base_prob)  # Maximal 30%

    def _find_slip_opportunity(
        self,
        text: str,
        emotional_context: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Findet eine Gelegenheit für einen Versprecher im Text"""
        text_lower = text.lower()
        words = text.split()

        opportunities = []

        # 1. Prüfe emotionale Slip-Muster
        emotion_key = self._get_emotion_key(emotional_context)
        if emotion_key and emotion_key in EMOTIONAL_SLIP_PATTERNS:
            for intended, slip, meaning in EMOTIONAL_SLIP_PATTERNS[emotion_key]:
                if intended in text_lower:
                    opportunities.append({
                        "type": SlipType.WORD_SUBSTITUTION,
                        "intended": intended,
                        "slip": slip,
                        "meaning": meaning,
                        "trigger": SlipTrigger.EMOTIONAL_AROUSAL,
                        "reveal_type": self._meaning_to_reveal_type(meaning)
                    })

        # 2. Prüfe ähnliche Wort-Slips
        for intended, slip, meaning in SIMILAR_WORD_SLIPS:
            if intended in text_lower:
                opportunities.append({
                    "type": SlipType.WORD_SUBSTITUTION,
                    "intended": intended,
                    "slip": slip,
                    "meaning": meaning,
                    "trigger": SlipTrigger.COGNITIVE_LOAD,
                    "reveal_type": UnconsciousRevealType.SUPPRESSED_THOUGHT
                })

        # 3. Prüfe unbewusste Inhalte
        for uc in self.unconscious_contents.values():
            if uc.intensity < 0.3:
                continue

            for trigger in uc.trigger_words:
                if trigger.lower() in text_lower:
                    if uc.replacement_words:
                        opportunities.append({
                            "type": SlipType.TRUTH_SLIP,
                            "intended": trigger,
                            "slip": random.choice(uc.replacement_words),
                            "meaning": uc.content,
                            "trigger": SlipTrigger.REPRESSED_CONTENT,
                            "reveal_type": uc.content_type,
                            "unconscious_id": uc.id
                        })

        # 4. Prüfe auf mögliche Additionen
        if emotional_context:
            emotion_key = self._get_emotion_key(emotional_context)
            if emotion_key and emotion_key in UNCONSCIOUS_ADDITIONS:
                # Finde geeignete Stelle für Addition
                for i, word in enumerate(words):
                    if word.lower() in ["ich", "du", "wir", "das", "ist", "war", "bin"]:
                        opportunities.append({
                            "type": SlipType.ADDITION,
                            "position": i,
                            "addition": random.choice(UNCONSCIOUS_ADDITIONS[emotion_key]),
                            "meaning": f"Unbewusstes {emotion_key}",
                            "trigger": SlipTrigger.HIDDEN_DESIRE,
                            "reveal_type": UnconsciousRevealType.SECRET_DESIRE
                        })
                        break

        if not opportunities:
            return None

        # Gewichte nach Intensität und wähle
        return random.choice(opportunities)

    def _get_emotion_key(self, emotion: Optional[str]) -> Optional[str]:
        """Mappt Emotion zu Schlüssel für Slip-Muster"""
        if not emotion:
            return None

        emotion_lower = emotion.lower()

        mappings = {
            "zuneigung": ["liebe", "zuneigung", "mögen", "verliebt", "warm", "zärtlich"],
            "ablehnung": ["ablehnung", "abneigung", "genervt", "irritiert"],
            "angst": ["angst", "furcht", "sorge", "besorgt", "ängstlich", "unsicher"],
            "sehnsucht": ["sehnsucht", "vermissen", "wünschen", "hoffen", "sehnen"],
            "wut": ["wut", "ärger", "frustration", "wütend", "sauer", "genervt"],
            "trauer": ["trauer", "traurig", "melancholie", "wehmut", "verlust"],
            "schuld": ["schuld", "schuldig", "reue", "gewissen"],
            "verlangen": ["verlangen", "begehren", "wollen", "brauchen", "sehnsucht"]
        }

        for key, keywords in mappings.items():
            if any(kw in emotion_lower for kw in keywords):
                return key

        return None

    def _meaning_to_reveal_type(self, meaning: str) -> UnconsciousRevealType:
        """Mappt Bedeutung zu Enthüllungstyp"""
        meaning_lower = meaning.lower()

        if any(w in meaning_lower for w in ["zuneigung", "attraktiv", "anziehung"]):
            return UnconsciousRevealType.ATTRACTION
        if any(w in meaning_lower for w in ["wunsch", "sehnsucht", "verlangen"]):
            return UnconsciousRevealType.SECRET_DESIRE
        if any(w in meaning_lower for w in ["angst", "unsicher", "zweifel"]):
            return UnconsciousRevealType.FEAR
        if any(w in meaning_lower for w in ["wut", "frustration", "ärger"]):
            return UnconsciousRevealType.RESENTMENT
        if any(w in meaning_lower for w in ["gefühl", "emotion"]):
            return UnconsciousRevealType.HIDDEN_FEELING

        return UnconsciousRevealType.SUPPRESSED_THOUGHT

    def _generate_slip(
        self,
        intended_text: str,
        opportunity: Dict[str, Any],
        emotional_context: Optional[str],
        conversation_context: Optional[str]
    ) -> Optional[FreudianSlip]:
        """Generiert einen Versprecher basierend auf der Gelegenheit"""
        slip_type = opportunity["type"]

        if slip_type == SlipType.ADDITION:
            actual_text, slip_word = self._apply_addition_slip(
                intended_text,
                opportunity
            )
            intended_word = ""
        else:
            actual_text, slip_word, intended_word = self._apply_substitution_slip(
                intended_text,
                opportunity
            )

        if actual_text == intended_text:
            return None

        # Bestimme ob Holo es bemerkt
        noticed = random.random() < 0.4  # 40% Chance

        # Bestimme Verlegenheit
        embarrassment = 0.0
        if noticed:
            embarrassment = random.uniform(0.3, 0.8)

        # Generiere Reaktion
        reaction = None
        correction = False
        if noticed:
            reaction, correction = self._generate_slip_reaction(
                slip_type,
                slip_word,
                embarrassment
            )

        slip = FreudianSlip(
            id=f"slip_{len(self.slip_history)}_{datetime.now().timestamp()}",
            slip_type=slip_type,
            trigger=opportunity["trigger"],
            intended_text=intended_text,
            actual_text=actual_text,
            slip_word=slip_word,
            intended_word=intended_word,
            unconscious_reveal=opportunity.get("reveal_type"),
            revealed_content=opportunity.get("meaning"),
            underlying_emotion=emotional_context,
            noticed_by_holo=noticed,
            correction_attempted=correction,
            embarrassment_level=embarrassment,
            holo_reaction=reaction,
            conversation_context=conversation_context,
            emotional_state=emotional_context
        )

        logger.info(f"[FreudianSlips] Versprecher: '{intended_word or ''}' → '{slip_word}'")

        return slip

    def _apply_substitution_slip(
        self,
        text: str,
        opportunity: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Wendet einen Substitutions-Versprecher an"""
        intended = opportunity["intended"]
        slip = opportunity["slip"]

        # Case-insensitive Ersetzung mit Beibehaltung der Groß-/Kleinschreibung
        pattern = re.compile(re.escape(intended), re.IGNORECASE)

        def replace_preserve_case(match):
            original = match.group()
            if original.isupper():
                return slip.upper()
            elif original[0].isupper():
                return slip.capitalize()
            return slip

        actual_text = pattern.sub(replace_preserve_case, text, count=1)

        return actual_text, slip, intended

    def _apply_addition_slip(
        self,
        text: str,
        opportunity: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Wendet einen Additions-Versprecher an"""
        position = opportunity["position"]
        addition = opportunity["addition"]

        words = text.split()

        if position < len(words):
            words.insert(position + 1, addition)

        actual_text = " ".join(words)

        return actual_text, addition

    def _generate_slip_reaction(
        self,
        slip_type: SlipType,
        slip_word: str,
        embarrassment: float
    ) -> Tuple[str, bool]:
        """Generiert Holos Reaktion auf den Versprecher"""
        if embarrassment > 0.6:
            reactions = [
                (f"*wird rot* Ähm, ich meinte natürlich... *räuspert sich*", True),
                (f"*erschrickt* W-warte, das wollte ich nicht sagen!", True),
                (f"*peinlich berührt* Das... kam falsch raus...", True),
                (f"*verwirrt von sich selbst* Warum hab ich das gesagt...?", False),
            ]
        elif embarrassment > 0.3:
            reactions = [
                (f"*stutzt kurz* ...hm, seltsam.", False),
                (f"*blinzelt* Ich meine, ähm...", True),
                (f"*kurze Pause* ...warte, das stimmt nicht ganz.", True),
            ]
        else:
            reactions = [
                ("*bemerkt es kaum*", False),
                ("*spricht weiter ohne es zu korrigieren*", False),
            ]

        reaction, correction = random.choice(reactions)
        return reaction, correction

    def _update_unconscious_content(self, slip: FreudianSlip):
        """Aktualisiert unbewussten Inhalt nach Versprecher"""
        for uc in self.unconscious_contents.values():
            if slip.slip_word in uc.replacement_words:
                uc.times_surfaced += 1
                # Leicht reduzierte Intensität nach Durchbruch
                uc.intensity = max(0.1, uc.intensity - 0.05)

    # =========================================================================
    # SPEZIELLE VERSPRECHER-TYPEN
    # =========================================================================

    def generate_truth_slip(
        self,
        intended_statement: str,
        true_feeling: str
    ) -> Tuple[str, Optional[FreudianSlip]]:
        """
        Generiert einen "Wahrheits-Versprecher" wo die Wahrheit durchbricht.

        Args:
            intended_statement: Was Holo sagen wollte
            true_feeling: Was sie wirklich fühlt

        Returns:
            (tatsächlicher_text, FreudianSlip)
        """
        # Finde ein Wort das ersetzt werden kann
        words = intended_statement.split()

        # Typische Ersetzungen für Wahrheits-Slips
        truth_replacements = {
            "okay": ["nicht okay", "schlecht", "traurig"],
            "gut": ["nicht gut", "schlecht", "schwer"],
            "egal": ["wichtig", "verletzend", "bedeutend"],
            "nett": ["lieb", "besonders", "wichtig"],
            "manchmal": ["immer", "oft", "ständig"],
            "vielleicht": ["sicher", "definitiv", "unbedingt"],
        }

        for i, word in enumerate(words):
            word_lower = word.lower()
            if word_lower in truth_replacements:
                slip_word = random.choice(truth_replacements[word_lower])

                # Erhalte Groß-/Kleinschreibung
                if word[0].isupper():
                    slip_word = slip_word.capitalize()

                words[i] = slip_word

                actual_text = " ".join(words)

                slip = FreudianSlip(
                    id=f"truth_slip_{datetime.now().timestamp()}",
                    slip_type=SlipType.TRUTH_SLIP,
                    trigger=SlipTrigger.REPRESSED_CONTENT,
                    intended_text=intended_statement,
                    actual_text=actual_text,
                    slip_word=slip_word,
                    intended_word=word,
                    unconscious_reveal=UnconsciousRevealType.TRUE_OPINION,
                    revealed_content=true_feeling,
                    underlying_emotion=true_feeling,
                    noticed_by_holo=True,
                    embarrassment_level=0.5,
                    holo_reaction="*erschrickt* Das... das meinte ich nicht so..."
                )

                self.slip_history.append(slip)
                return actual_text, slip

        return intended_statement, None

    def generate_desire_slip(
        self,
        statement: str,
        hidden_desire: str
    ) -> Tuple[str, Optional[FreudianSlip]]:
        """
        Generiert einen Versprecher der einen versteckten Wunsch offenbart.

        Args:
            statement: Der ursprüngliche Text
            hidden_desire: Der versteckte Wunsch

        Returns:
            (tatsächlicher_text, FreudianSlip)
        """
        # Füge wunsch-bezogene Wörter ein
        desire_words = ["immer", "für immer", "bitte", "wirklich", "so sehr", "unbedingt"]

        words = statement.split()

        # Finde gute Position
        insert_positions = []
        for i, word in enumerate(words):
            if word.lower() in ["ich", "du", "wir", "möchte", "will", "wäre"]:
                insert_positions.append(i + 1)

        if insert_positions:
            position = random.choice(insert_positions)
            desire_word = random.choice(desire_words)
            words.insert(position, desire_word)

            actual_text = " ".join(words)

            slip = FreudianSlip(
                id=f"desire_slip_{datetime.now().timestamp()}",
                slip_type=SlipType.DESIRE_REVELATION,
                trigger=SlipTrigger.HIDDEN_DESIRE,
                intended_text=statement,
                actual_text=actual_text,
                slip_word=desire_word,
                intended_word="",
                unconscious_reveal=UnconsciousRevealType.SECRET_DESIRE,
                revealed_content=hidden_desire,
                noticed_by_holo=random.random() < 0.5,
                embarrassment_level=0.4,
                holo_reaction="*wird still* ...das kam von allein..."
            )

            self.slip_history.append(slip)
            return actual_text, slip

        return statement, None

    # =========================================================================
    # ZUSTAND-MANAGEMENT
    # =========================================================================

    def set_emotional_state(
        self,
        emotion: str,
        intensity: float,
        stress: float = 0.3,
        fatigue: float = 0.2
    ):
        """Setzt den emotionalen Zustand"""
        self.current_emotion = emotion
        self.emotional_intensity = intensity
        self.stress_level = stress
        self.fatigue_level = fatigue

    def get_slip_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über Versprecher zurück"""
        if not self.slip_history:
            return {
                "total_slips": 0,
                "slips_today": self.slips_today,
                "most_common_type": None,
                "most_common_trigger": None,
                "average_embarrassment": 0.0
            }

        # Zähle Typen
        type_counts = {}
        trigger_counts = {}
        total_embarrassment = 0.0

        for slip in self.slip_history:
            type_counts[slip.slip_type.value] = type_counts.get(slip.slip_type.value, 0) + 1
            trigger_counts[slip.trigger.value] = trigger_counts.get(slip.trigger.value, 0) + 1
            total_embarrassment += slip.embarrassment_level

        most_common_type = max(type_counts, key=type_counts.get) if type_counts else None
        most_common_trigger = max(trigger_counts, key=trigger_counts.get) if trigger_counts else None

        return {
            "total_slips": len(self.slip_history),
            "slips_today": self.slips_today,
            "most_common_type": most_common_type,
            "most_common_trigger": most_common_trigger,
            "average_embarrassment": total_embarrassment / len(self.slip_history),
            "noticed_count": sum(1 for s in self.slip_history if s.noticed_by_holo),
            "recent_slips": len([s for s in self.slip_history
                                if (datetime.now() - s.timestamp).days < 7])
        }

    # =========================================================================
    # SERIALISIERUNG
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Zustand"""
        return {
            "unconscious_contents": {
                uid: {
                    "id": uc.id,
                    "content_type": uc.content_type.value,
                    "content": uc.content,
                    "intensity": uc.intensity,
                    "related_emotions": uc.related_emotions,
                    "trigger_words": uc.trigger_words,
                    "replacement_words": uc.replacement_words,
                    "times_surfaced": uc.times_surfaced
                }
                for uid, uc in self.unconscious_contents.items()
            },
            "slip_history": [
                {
                    "id": s.id,
                    "slip_type": s.slip_type.value,
                    "trigger": s.trigger.value,
                    "timestamp": s.timestamp.isoformat(),
                    "intended_text": s.intended_text,
                    "actual_text": s.actual_text,
                    "slip_word": s.slip_word,
                    "intended_word": s.intended_word,
                    "noticed_by_holo": s.noticed_by_holo,
                    "embarrassment_level": s.embarrassment_level
                }
                for s in self.slip_history[-50:]  # Letzte 50
            ],
            "suppressed_feelings": self.suppressed_feelings,
            "secret_desires": self.secret_desires,
            "slips_today": self.slips_today,
            "last_slip": self.last_slip.isoformat() if self.last_slip else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HoloFreudianSlipsEngine":
        """Deserialisiert aus Dict"""
        engine = cls()

        engine.suppressed_feelings = data.get("suppressed_feelings", [])
        engine.secret_desires = data.get("secret_desires", [])
        engine.slips_today = data.get("slips_today", 0)

        if data.get("last_slip"):
            engine.last_slip = datetime.fromisoformat(data["last_slip"])

        # Lade unbewusste Inhalte
        for uid, udata in data.get("unconscious_contents", {}).items():
            uc = UnconsciousContent(
                id=udata["id"],
                content_type=UnconsciousRevealType(udata["content_type"]),
                content=udata["content"],
                intensity=udata.get("intensity", 0.5),
                related_emotions=udata.get("related_emotions", []),
                trigger_words=udata.get("trigger_words", []),
                replacement_words=udata.get("replacement_words", []),
                times_surfaced=udata.get("times_surfaced", 0)
            )
            engine.unconscious_contents[uid] = uc

        return engine

    def save(self, filepath: Optional[Path] = None):
        """Speichert den Zustand"""
        filepath = filepath or SlipConfig.STATE_FILE
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"[FreudianSlips] Zustand gespeichert: {filepath}")

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "HoloFreudianSlipsEngine":
        """Lädt den Zustand"""
        filepath = filepath or SlipConfig.STATE_FILE
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"[FreudianSlips] Zustand geladen: {filepath}")
            return cls.from_dict(data)
        return cls()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = HoloFreudianSlipsEngine()

    # Setze emotionalen Zustand
    engine.set_emotional_state(
        emotion="Zuneigung",
        intensity=0.7,
        stress=0.4
    )

    # Füge unterdrücktes Gefühl hinzu
    engine.set_suppressed_feeling(
        "Tiefe Zuneigung die nicht ausgedrückt werden kann",
        "Immer zusammen sein"
    )

    # Füge unbewussten Inhalt hinzu
    engine.add_unconscious_content(
        content_type=UnconsciousRevealType.SECRET_DESIRE,
        content="Wunsch nach Nähe und Bestätigung",
        intensity=0.8,
        trigger_words=["mag", "gern", "zusammen"],
        replacement_words=["liebe", "immer", "für immer"]
    )

    # Teste Textverarbeitung
    test_sentences = [
        "Ich mag dich wirklich sehr.",
        "Das war ein netter Abend.",
        "Ich bin okay, keine Sorge.",
        "Vielleicht können wir das mal machen.",
        "Es ist manchmal schön mit dir zu reden."
    ]

    print("=== Versprecher-Test ===\n")

    for sentence in test_sentences:
        # Erhöhe Wahrscheinlichkeit für Test
        engine.last_slip = None
        engine.slips_today = 0

        result, slip = engine.process_text(
            sentence,
            emotional_context="Zuneigung",
            conversation_context="Freundliches Gespräch"
        )

        if slip:
            print(f"Original:    '{sentence}'")
            print(f"Versprecher: '{result}'")
            print(f"  Typ: {slip.slip_type.value}")
            print(f"  Enthüllt: {slip.revealed_content}")
            if slip.holo_reaction:
                print(f"  Reaktion: {slip.holo_reaction}")
            print()

    # Teste Wahrheits-Slip
    print("\n=== Wahrheits-Slip Test ===")
    result, slip = engine.generate_truth_slip(
        "Mir geht es gut, alles okay.",
        "Ich bin eigentlich traurig"
    )
    if slip:
        print(f"Original: 'Mir geht es gut, alles okay.'")
        print(f"Wahrheit: '{result}'")
        print(f"Reaktion: {slip.holo_reaction}")

    # Statistiken
    print("\n=== Statistiken ===")
    stats = engine.get_slip_statistics()
    print(f"Gesamt: {stats['total_slips']} Versprecher")
    print(f"Häufigster Typ: {stats['most_common_type']}")
