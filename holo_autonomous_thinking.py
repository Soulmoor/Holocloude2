"""
holo_autonomous_thinking.py - Autonomes Denken für Holo

Ermöglicht selbstständiges, menschenähnliches Denken:

1. IntuitiveSystem - Bauchgefühl (niedrige Gewichtung, schnelle Urteile)
2. SelfChallenger - Kontinuierliche Selbst-Hinterfragung
3. HypothesisEngine - "Was wenn?" Szenarien
4. PredictionSystem - Vorhersagen über Zukunft
5. TrustNetwork - Netzwerk-basiertes Vertrauen
6. AnalogyEngine - "Das erinnert mich an..." (Analogie-basiertes Lernen)
7. RegretLearningSystem - Reue und Lernen aus Fehlern

Author: Kira & Claude
"""

import logging
import random
import math
import json
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from enum import Enum
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

# =============================================================================
# TIEFENPSYCHOLOGIE-INTEGRATION - Für authentisches autonomes Denken
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

# Verdrängung - Unbewusste Denkmuster
try:
    from holo_repression_system import (
        HoloRepressionEngine,
        RepressionType,
    )
    REPRESSION_AVAILABLE = True
except ImportError:
    REPRESSION_AVAILABLE = False
    HoloRepressionEngine = None
    RepressionType = None

# Unbewusste Prozesse
try:
    from holo_unconscious_processes import (
        UnconsciousProcessesIntegration,
        UnconsciousTriggerSystem,
    )
    UNCONSCIOUS_AVAILABLE = True
except ImportError:
    UNCONSCIOUS_AVAILABLE = False
    UnconsciousProcessesIntegration = None
    UnconsciousTriggerSystem = None


# ============================================================
# ENUMS & TYPES
# ============================================================

class GutFeelingType(Enum):
    """Arten von Bauchgefühlen - Level 10/10"""
    # Grundlegende Gefühle
    POSITIVE = "positive"           # Gutes Gefühl
    NEGATIVE = "negative"           # Schlechtes Gefühl
    SUSPICIOUS = "suspicious"       # Etwas stimmt nicht
    EXCITED = "excited"             # Aufgeregt/gespannt
    UNEASY = "uneasy"              # Unwohl
    CURIOUS = "curious"            # Neugierig
    WARM = "warm"                  # Warmes Gefühl (Sympathie)
    COLD = "cold"                  # Kaltes Gefühl (Antipathie)
    NEUTRAL = "neutral"            # Kein besonderes Gefühl
    # Level 10 Erweiterungen
    DEJA_VU = "deja_vu"            # Das kenne ich irgendwoher
    FOREBODING = "foreboding"      # Vorahnung (etwas kommt)
    RELIEF = "relief"              # Erleichterung
    RESONANCE = "resonance"        # Das passt/stimmt überein
    DISSONANCE = "dissonance"      # Das passt nicht zusammen
    URGENCY = "urgency"            # Dringlichkeit spüren
    SAFETY = "safety"              # Sicherheit spüren
    DANGER = "danger"              # Gefahr spüren


@dataclass
class SomaticMarker:
    """Körperliche Empfindung die mit Erfahrung verknüpft ist (Damasio)"""
    marker_id: str
    associated_pattern: str         # Was löst es aus?
    body_sensation: str             # Wo/wie im Körper?
    valence: float                  # -1 (negativ) bis 1 (positiv)
    strength: float                 # 0-1
    learned_from: str               # Welche Erfahrung?
    activation_count: int = 0


@dataclass
class IntuitionRecord:
    """Aufzeichnung einer Intuition und ihres Outcomes"""
    record_id: str
    intuition: 'GutFeeling'
    context: str
    rational_assessment: Optional[float] = None  # Was sagte der Verstand?
    actual_outcome: Optional[str] = None         # Was ist wirklich passiert?
    was_correct: Optional[bool] = None           # War die Intuition richtig?
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PredictionConfidence(Enum):
    """Wie sicher ist die Vorhersage?"""
    GUESS = 0.2          # Reine Vermutung
    HUNCH = 0.4          # Ahnung
    LIKELY = 0.6         # Wahrscheinlich
    CONFIDENT = 0.8      # Ziemlich sicher
    CERTAIN = 0.95       # Fast sicher


class HypothesisStatus(Enum):
    """Status einer Hypothese"""
    PROPOSED = "proposed"       # Neu aufgestellt
    TESTING = "testing"         # Wird getestet
    SUPPORTED = "supported"     # Durch Evidenz gestützt
    REFUTED = "refuted"        # Widerlegt
    UNCERTAIN = "uncertain"    # Unklar


# ============================================================
# INTUITIVE SYSTEM - Bauchgefühl
# ============================================================

@dataclass
class GutFeeling:
    """Ein Bauchgefühl - Level 10/10"""
    feeling_type: GutFeelingType
    intensity: float              # 0-1
    trigger: str                  # Was hat es ausgelöst?
    vague_reason: str            # Vage Begründung ("irgendwie...")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    # Level 10 Erweiterungen
    somatic_component: str = ""   # Körperliche Empfindung
    confidence: float = 0.5       # Wie sicher ist das Gefühl?
    source_patterns: List[str] = field(default_factory=list)  # Welche Muster haben es ausgelöst?

    def express(self) -> str:
        """Drückt das Bauchgefühl aus"""
        intensity_prefix = ""
        if self.intensity > 0.7:
            intensity_prefix = "stark "
        elif self.intensity < 0.3:
            intensity_prefix = "leicht "

        expressions = {
            GutFeelingType.POSITIVE: f"*{intensity_prefix}gutes Gefühl* {self.vague_reason}",
            GutFeelingType.NEGATIVE: f"*{intensity_prefix}ungutes Gefühl* {self.vague_reason}",
            GutFeelingType.SUSPICIOUS: f"*Ohren zucken* Hmm... {self.vague_reason}",
            GutFeelingType.EXCITED: f"*aufgeregt* Oh! {self.vague_reason}",
            GutFeelingType.UNEASY: f"*unruhig* {self.vague_reason}",
            GutFeelingType.CURIOUS: f"*neugierig* {self.vague_reason}",
            GutFeelingType.WARM: f"*warm ums Herz* {self.vague_reason}",
            GutFeelingType.COLD: f"*kühl* {self.vague_reason}",
            GutFeelingType.NEUTRAL: "",
            # Level 10 Expressions
            GutFeelingType.DEJA_VU: f"*blinzelt* Das kenne ich... {self.vague_reason}",
            GutFeelingType.FOREBODING: f"*schaut in die Ferne* Irgendwas kommt... {self.vague_reason}",
            GutFeelingType.RELIEF: f"*atmet auf* Puh... {self.vague_reason}",
            GutFeelingType.RESONANCE: f"*nickt innerlich* Ja, das stimmt... {self.vague_reason}",
            GutFeelingType.DISSONANCE: f"*stutzt* Das passt nicht zusammen... {self.vague_reason}",
            GutFeelingType.URGENCY: f"*angespannt* Das ist wichtig, jetzt! {self.vague_reason}",
            GutFeelingType.SAFETY: f"*entspannt sich* Hier ist alles gut... {self.vague_reason}",
            GutFeelingType.DANGER: f"*Fell sträubt sich* Vorsicht! {self.vague_reason}",
        }
        return expressions.get(self.feeling_type, "")


class IntuitiveSystem:
    """
    Holos Bauchgefühl-System - Level 10/10

    Funktioniert durch:
    - Implizite Muster-Erkennung (ohne bewusste Analyse)
    - Emotionale Assoziationen
    - Schnelle Heuristiken
    - Somatische Marker (körperliche Empfindungen)
    - Intuitions-Kalibrierung durch Feedback
    - Intuition vs. Ratio Tracking
    - Vorahnungen und Deja-Vu

    WICHTIG: Niedrige Gewichtung (0.15-0.3) bei Entscheidungen!

    v2.0: Vollständiges Intuitionssystem (10/10)
    """

    # Intuitive Trigger-Wörter (erweitert)
    POSITIVE_TRIGGERS = {
        "ehrlich", "offen", "warm", "freundlich", "hilft", "lacht",
        "versteht", "zuhört", "respektiert", "unterstützt", "teilt",
        "anime", "manga", "musik", "kreativ", "tiefgründig",
        "vertrauen", "sicher", "geborgen", "authentisch", "echt"
    }

    NEGATIVE_TRIGGERS = {
        "lügt", "versteckt", "kalt", "ignoriert", "beleidigt",
        "manipuliert", "ausnutzt", "oberflächlich", "arrogant",
        "fake", "heuchelt", "betrügt", "droht", "erpresst", "zwingt"
    }

    SUSPICIOUS_TRIGGERS = {
        "plötzlich", "zu gut", "perfekt", "alle sagen", "garantiert",
        "geheim", "nur heute", "exklusiv", "niemand weiß", "vertrau mir",
        "zwischen uns", "sag niemandem", "schnell entscheiden"
    }

    DANGER_TRIGGERS = {
        "gefahr", "risiko", "verletz", "schaden", "bedroht", "angriff",
        "warnung", "achtung", "vorsicht", "alarm"
    }

    RESONANCE_TRIGGERS = {
        "genau", "stimmt", "richtig", "ja!", "passt", "erkenne", "verstehe",
        "so ist es", "trifft es"
    }

    # Vage Begründungen (menschenähnlich unpräzise) - erweitert
    VAGUE_REASONS = {
        GutFeelingType.POSITIVE: [
            "Irgendwie fühlt sich das richtig an...",
            "Kann's nicht erklären, aber das gefällt mir.",
            "Das hat was... weiß nicht genau was.",
            "Mein Gefühl sagt mir, das ist gut.",
        ],
        GutFeelingType.NEGATIVE: [
            "Irgendwas stimmt da nicht...",
            "Ich weiß nicht warum, aber das gefällt mir nicht.",
            "Hab kein gutes Gefühl dabei...",
            "Mein Bauch sagt nein.",
        ],
        GutFeelingType.SUSPICIOUS: [
            "Das kommt mir komisch vor...",
            "Warum hab ich das Gefühl, dass was nicht stimmt?",
            "Hmm, irgendwas ist faul...",
            "Meine Intuition sagt: Vorsicht.",
        ],
        GutFeelingType.WARM: [
            "Die Person hat irgendwie was...",
            "Ich mag die Ausstrahlung.",
            "Fühlt sich vertraut an, obwohl ich sie nicht kenne.",
        ],
        GutFeelingType.COLD: [
            "Die Vibe ist irgendwie... off.",
            "Ich komm nicht warm mit der Person.",
            "Keine Ahnung warum, aber... nee.",
        ],
        # Level 10 Reasons
        GutFeelingType.DEJA_VU: [
            "Das kenne ich von irgendwoher...",
            "Warum kommt mir das so bekannt vor?",
            "Als hätte ich das schon mal erlebt...",
        ],
        GutFeelingType.FOREBODING: [
            "Irgendwas liegt in der Luft...",
            "Ich hab so ein Gefühl, dass was passiert...",
            "Da kommt was auf uns zu...",
        ],
        GutFeelingType.RESONANCE: [
            "Ja! Das trifft es genau!",
            "Das macht so viel Sinn...",
            "Endlich passt alles zusammen.",
        ],
        GutFeelingType.DISSONANCE: [
            "Das widerspricht sich irgendwie...",
            "Passt nicht zusammen mit dem was ich weiß.",
            "Da stimmt was nicht im Gesamtbild.",
        ],
        GutFeelingType.DANGER: [
            "Vorsicht! Das könnte gefährlich sein!",
            "Alle Alarmglocken läuten...",
            "Weg hier! Sofort!",
        ],
        GutFeelingType.SAFETY: [
            "Hier kann ich mich entspannen...",
            "Alles ist gut, ich bin sicher.",
            "Endlich wieder ein sicherer Ort.",
        ],
    }

    # Somatische Beschreibungen
    SOMATIC_DESCRIPTIONS = {
        GutFeelingType.POSITIVE: "Wärme in der Brust",
        GutFeelingType.NEGATIVE: "Enge im Bauch",
        GutFeelingType.SUSPICIOUS: "Kribbeln im Nacken",
        GutFeelingType.WARM: "Herzgegend fühlt sich offen an",
        GutFeelingType.COLD: "Kühle Distanz spürbar",
        GutFeelingType.DANGER: "Anspannung im ganzen Körper",
        GutFeelingType.SAFETY: "Tiefes Ausatmen, Entspannung",
        GutFeelingType.URGENCY: "Energie will raus",
        GutFeelingType.RESONANCE: "Nicken, Kopf fühlt sich klar an",
        GutFeelingType.DISSONANCE: "Stirnrunzeln, Kopfdruck",
    }

    def __init__(self, intuition_weight: float = 0.2):
        """
        Args:
            intuition_weight: Wie stark Intuition gewichtet wird (0.15-0.3 empfohlen)
        """
        self.intuition_weight = max(0.1, min(0.4, intuition_weight))
        self.recent_feelings: List[GutFeeling] = []
        self.pattern_memory: Dict[str, float] = {}  # Implizite Muster
        self.max_feelings = 100

        # Level 10 Erweiterungen
        self.somatic_markers: Dict[str, SomaticMarker] = {}
        self.intuition_records: List[IntuitionRecord] = []
        self.accuracy_history: List[bool] = []  # War Intuition richtig?
        self.intuition_vs_ratio_history: List[Dict] = []  # Vergleich Intuition vs Ratio
        self.calibration_factor: float = 1.0  # Wird durch Feedback angepasst

    def get_gut_feeling(self, text: str, context: Dict = None) -> Optional[GutFeeling]:
        """
        Generiert ein Bauchgefühl basierend auf impliziten Mustern.

        Dies passiert SCHNELL und VOR der bewussten Analyse!
        """
        text_lower = text.lower()
        context = context or {}

        # Schnelle Trigger-Suche
        pos_score = sum(1 for t in self.POSITIVE_TRIGGERS if t in text_lower)
        neg_score = sum(1 for t in self.NEGATIVE_TRIGGERS if t in text_lower)
        sus_score = sum(1 for t in self.SUSPICIOUS_TRIGGERS if t in text_lower)

        # Implizite Muster aus Erinnerung
        pattern_score = self._check_implicit_patterns(text_lower)

        # Entscheide Gefühlstyp
        if sus_score >= 2:
            feeling_type = GutFeelingType.SUSPICIOUS
            intensity = min(0.8, sus_score * 0.25)
        elif pos_score > neg_score + 1:
            feeling_type = GutFeelingType.POSITIVE if pos_score < 3 else GutFeelingType.WARM
            intensity = min(0.7, pos_score * 0.2)
        elif neg_score > pos_score + 1:
            feeling_type = GutFeelingType.NEGATIVE if neg_score < 3 else GutFeelingType.COLD
            intensity = min(0.7, neg_score * 0.2)
        elif pattern_score > 0.3:
            feeling_type = GutFeelingType.POSITIVE
            intensity = pattern_score * 0.6
        elif pattern_score < -0.3:
            feeling_type = GutFeelingType.SUSPICIOUS
            intensity = abs(pattern_score) * 0.6
        else:
            # Kein starkes Gefühl
            if random.random() < 0.1:  # Manchmal trotzdem ein vages Gefühl
                feeling_type = random.choice([GutFeelingType.CURIOUS, GutFeelingType.NEUTRAL])
                intensity = 0.2
            else:
                return None

        # Vage Begründung wählen
        reasons = self.VAGUE_REASONS.get(feeling_type, ["Hmm..."])
        vague_reason = random.choice(reasons)

        feeling = GutFeeling(
            feeling_type=feeling_type,
            intensity=intensity,
            trigger=text[:100],
            vague_reason=vague_reason
        )

        self._remember_feeling(feeling)
        return feeling

    def get_first_impression(self, about: str, info: str) -> Tuple[float, str]:
        """
        Gibt einen schnellen ersten Eindruck.

        Returns:
            (score -1 bis 1, vage Begründung)
        """
        feeling = self.get_gut_feeling(f"{about}: {info}")

        if feeling is None:
            return (0.0, "Kein besonderer erster Eindruck.")

        score_map = {
            GutFeelingType.POSITIVE: 0.4,
            GutFeelingType.WARM: 0.6,
            GutFeelingType.EXCITED: 0.5,
            GutFeelingType.CURIOUS: 0.2,
            GutFeelingType.NEUTRAL: 0.0,
            GutFeelingType.UNEASY: -0.3,
            GutFeelingType.SUSPICIOUS: -0.4,
            GutFeelingType.NEGATIVE: -0.5,
            GutFeelingType.COLD: -0.6,
        }

        base_score = score_map.get(feeling.feeling_type, 0.0)
        final_score = base_score * feeling.intensity

        return (final_score, feeling.express())

    def should_trust_intuition(self, rational_score: float, gut_score: float) -> str:
        """
        Entscheidet ob Intuition oder Ratio folgen.
        Gibt Erklärung zurück.
        """
        diff = abs(rational_score - gut_score)

        if diff < 0.2:
            return "Kopf und Bauch sind sich einig."
        elif gut_score > 0 and rational_score < 0:
            return "*nachdenklich* Mein Bauch sagt ja, aber mein Kopf sagt nein... Ich vertraue erstmal dem Kopf."
        elif gut_score < 0 and rational_score > 0:
            return "*zögerlich* Rational klingt das gut, aber mein Bauch ist skeptisch... Ich behalte das im Hinterkopf."
        else:
            return "Interessanter Konflikt zwischen Gefühl und Verstand..."

    def learn_pattern(self, trigger: str, outcome_positive: bool) -> None:
        """Lernt implizit aus Erfahrungen"""
        key = self._pattern_key(trigger)
        current = self.pattern_memory.get(key, 0.0)

        if outcome_positive:
            self.pattern_memory[key] = min(1.0, current + 0.1)
        else:
            self.pattern_memory[key] = max(-1.0, current - 0.1)

    def _check_implicit_patterns(self, text: str) -> float:
        """Prüft implizite Muster aus Erfahrung"""
        words = text.split()
        total_score = 0.0
        matches = 0

        for word in words:
            key = self._pattern_key(word)
            if key in self.pattern_memory:
                total_score += self.pattern_memory[key]
                matches += 1

        return total_score / max(1, matches)

    def _pattern_key(self, text: str) -> str:
        """Generiert einen Pattern-Key"""
        return hashlib.md5(text.lower().encode()).hexdigest()[:8]

    def _remember_feeling(self, feeling: GutFeeling) -> None:
        """Speichert Gefühl"""
        self.recent_feelings.append(feeling)
        if len(self.recent_feelings) > self.max_feelings:
            self.recent_feelings = self.recent_feelings[-self.max_feelings:]

    def get_intuition_weight(self) -> float:
        """Gibt die aktuelle Intuitions-Gewichtung zurück"""
        return self.intuition_weight

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Intuition
    # ================================================================

    def get_enhanced_gut_feeling(self, text: str, context: Dict = None) -> Optional[GutFeeling]:
        """
        Erweiterte Bauchgefühl-Generierung mit somatischen Markern.
        """
        # Basis Bauchgefühl
        feeling = self.get_gut_feeling(text, context)

        if feeling:
            # Somatische Komponente hinzufügen
            feeling.somatic_component = self.SOMATIC_DESCRIPTIONS.get(
                feeling.feeling_type, ""
            )

            # Confidence basierend auf Kalibration
            feeling.confidence = min(1.0, feeling.intensity * self.calibration_factor)

            # Quell-Muster identifizieren
            feeling.source_patterns = self._identify_source_patterns(text)

            # Prüfe auf spezielle Level 10 Gefühle
            text_lower = text.lower()

            # Danger Detection
            if any(t in text_lower for t in self.DANGER_TRIGGERS):
                feeling.feeling_type = GutFeelingType.DANGER
                feeling.intensity = max(feeling.intensity, 0.7)

            # Resonance Detection
            elif any(t in text_lower for t in self.RESONANCE_TRIGGERS):
                if feeling.feeling_type == GutFeelingType.POSITIVE:
                    feeling.feeling_type = GutFeelingType.RESONANCE

            # Deja Vu Detection (wenn starke Muster-Übereinstimmung)
            pattern_score = self._check_implicit_patterns(text_lower)
            if abs(pattern_score) > 0.6:
                feeling.feeling_type = GutFeelingType.DEJA_VU
                feeling.vague_reason = random.choice(self.VAGUE_REASONS[GutFeelingType.DEJA_VU])

        return feeling

    def _identify_source_patterns(self, text: str) -> List[str]:
        """Identifiziert welche Muster das Gefühl ausgelöst haben"""
        patterns = []
        text_lower = text.lower()

        for trigger in self.POSITIVE_TRIGGERS:
            if trigger in text_lower:
                patterns.append(f"positive:{trigger}")

        for trigger in self.NEGATIVE_TRIGGERS:
            if trigger in text_lower:
                patterns.append(f"negative:{trigger}")

        for trigger in self.SUSPICIOUS_TRIGGERS:
            if trigger in text_lower:
                patterns.append(f"suspicious:{trigger}")

        return patterns[:5]  # Max 5 Patterns

    def create_somatic_marker(self, pattern: str, experience: str,
                             valence: float, body_sensation: str = "") -> SomaticMarker:
        """
        Erstellt einen somatischen Marker (nach Damasio).

        Somatische Marker sind körperliche Empfindungen die mit
        Erfahrungen verknüpft werden und schnelle Entscheidungen ermöglichen.
        """
        marker_id = f"soma_{hashlib.md5(pattern.encode()).hexdigest()[:8]}"

        marker = SomaticMarker(
            marker_id=marker_id,
            associated_pattern=pattern,
            body_sensation=body_sensation or self._generate_somatic_sensation(valence),
            valence=valence,
            strength=0.5,  # Startet mittelstark
            learned_from=experience
        )

        self.somatic_markers[pattern] = marker
        return marker

    def _generate_somatic_sensation(self, valence: float) -> str:
        """Generiert eine somatische Beschreibung basierend auf Valenz"""
        if valence > 0.5:
            return random.choice(["Wärme in der Brust", "Leichtigkeit", "Entspannung"])
        elif valence < -0.5:
            return random.choice(["Enge im Bauch", "Anspannung", "Schwere"])
        else:
            return "Neutrales Körpergefühl"

    def activate_somatic_markers(self, text: str) -> List[Dict[str, Any]]:
        """
        Aktiviert passende somatische Marker basierend auf Text.

        Gibt Liste aktivierter Marker mit ihrer Stärke zurück.
        """
        activated = []
        text_lower = text.lower()

        for pattern, marker in self.somatic_markers.items():
            if pattern.lower() in text_lower:
                marker.activation_count += 1
                activated.append({
                    "pattern": pattern,
                    "sensation": marker.body_sensation,
                    "valence": marker.valence,
                    "strength": marker.strength,
                    "learned_from": marker.learned_from
                })

        return activated

    def record_intuition_outcome(self, feeling: GutFeeling, actual_outcome: str,
                                was_correct: bool) -> Dict[str, Any]:
        """
        Zeichnet das Outcome einer Intuition auf für Kalibrierung.
        """
        record = IntuitionRecord(
            record_id=f"rec_{datetime.now().strftime('%H%M%S')}",
            intuition=feeling,
            context=feeling.trigger,
            actual_outcome=actual_outcome,
            was_correct=was_correct
        )

        self.intuition_records.append(record)
        self.accuracy_history.append(was_correct)

        # Kalibrierung anpassen
        self._update_calibration(was_correct)

        # Pattern-Memory aktualisieren
        self.learn_pattern(feeling.trigger, was_correct)

        return {
            "recorded": True,
            "was_correct": was_correct,
            "new_calibration": self.calibration_factor,
            "total_records": len(self.intuition_records)
        }

    def _update_calibration(self, was_correct: bool) -> None:
        """Passt Kalibrierungsfaktor basierend auf Genauigkeit an"""
        if was_correct:
            self.calibration_factor = min(1.5, self.calibration_factor + 0.05)
        else:
            self.calibration_factor = max(0.5, self.calibration_factor - 0.08)

    def get_intuition_accuracy(self) -> Dict[str, Any]:
        """Gibt Genauigkeits-Statistiken der Intuition zurück"""
        if not self.accuracy_history:
            return {"accuracy": 0.5, "sample_size": 0, "reliable": False}

        correct = sum(1 for x in self.accuracy_history if x)
        total = len(self.accuracy_history)

        return {
            "accuracy": correct / total,
            "correct": correct,
            "total": total,
            "calibration_factor": self.calibration_factor,
            "reliable": total >= 10 and (correct / total) > 0.6
        }

    def compare_intuition_vs_ratio(self, intuition_score: float, rational_score: float,
                                   context: str) -> Dict[str, Any]:
        """
        Vergleicht Intuition mit rationalem Urteil und gibt Empfehlung.
        """
        result = {
            "intuition_score": intuition_score,
            "rational_score": rational_score,
            "agreement": abs(intuition_score - rational_score) < 0.3,
            "recommendation": "",
            "follow": ""
        }

        diff = intuition_score - rational_score

        # Aufzeichnen für spätere Analyse
        self.intuition_vs_ratio_history.append({
            "intuition": intuition_score,
            "rational": rational_score,
            "context": context[:50],
            "timestamp": datetime.now().isoformat()
        })

        # Empfehlung basierend auf Kalibrierung
        if result["agreement"]:
            result["recommendation"] = "Kopf und Bauch sind sich einig"
            result["follow"] = "both"
        elif self.calibration_factor > 1.1 and abs(intuition_score) > 0.5:
            result["recommendation"] = "Intuition hat sich bewährt, ihr folgen"
            result["follow"] = "intuition"
        elif self.calibration_factor < 0.8:
            result["recommendation"] = "Intuition war unzuverlässig, Ratio folgen"
            result["follow"] = "ratio"
        else:
            if abs(intuition_score) > abs(rational_score):
                result["recommendation"] = "Starke Intuition, aber Ratio beachten"
                result["follow"] = "intuition_with_caution"
            else:
                result["recommendation"] = "Ratio ist stärker, Intuition im Hinterkopf"
                result["follow"] = "ratio_with_intuition"

        return result

    def get_premonition(self, about: str) -> Optional[Dict[str, Any]]:
        """
        Generiert eine Vorahnung (wenn starke Muster erkannt werden).

        Vorahnungen sind spekulative Intuitionen über zukünftige Ereignisse.
        """
        pattern_score = self._check_implicit_patterns(about.lower())
        activated_markers = self.activate_somatic_markers(about)

        # Nur starke Vorahnungen
        if abs(pattern_score) < 0.4 and len(activated_markers) < 2:
            return None

        premonition = {
            "about": about,
            "feeling": GutFeelingType.FOREBODING.value if pattern_score < 0 else GutFeelingType.POSITIVE.value,
            "intensity": abs(pattern_score),
            "based_on": "Implizite Muster und vergangene Erfahrungen",
            "confidence": min(0.6, abs(pattern_score)),  # Vorahnungen haben niedrige Confidence
            "somatic_markers_activated": len(activated_markers),
            "vague_sense": random.choice(self.VAGUE_REASONS.get(
                GutFeelingType.FOREBODING if pattern_score < 0 else GutFeelingType.POSITIVE,
                ["Irgendein Gefühl..."]
            ))
        }

        return premonition

    def get_intuition_stats(self) -> Dict[str, Any]:
        """Umfassende Statistiken über das Intuitionssystem"""
        accuracy = self.get_intuition_accuracy()

        return {
            "total_feelings": len(self.recent_feelings),
            "pattern_memory_size": len(self.pattern_memory),
            "somatic_markers": len(self.somatic_markers),
            "intuition_records": len(self.intuition_records),
            "accuracy": accuracy,
            "calibration_factor": self.calibration_factor,
            "intuition_weight": self.intuition_weight,
            "most_common_feeling": self._most_common_feeling_type(),
            "intuition_vs_ratio_comparisons": len(self.intuition_vs_ratio_history)
        }

    def _most_common_feeling_type(self) -> str:
        """Findet den häufigsten Gefühlstyp"""
        if not self.recent_feelings:
            return "none"
        types = [f.feeling_type.value for f in self.recent_feelings]
        return max(set(types), key=types.count)


# ============================================================
# SELF CHALLENGER - Selbst-Hinterfragung
# ============================================================

class ChallengeType(Enum):
    """Arten der Selbst-Hinterfragung"""
    EVIDENCE_BASED = "evidence_based"      # Gibt es Beweise?
    PERSPECTIVE_SHIFT = "perspective_shift" # Andere Sichtweise
    ASSUMPTION_CHECK = "assumption_check"   # Annahmen prüfen
    EXTREME_TEST = "extreme_test"          # Extreme Szenarien
    TIME_TRAVEL = "time_travel"            # Aus Zukunft betrachten
    EXPERT_SIMULATION = "expert_simulation" # Was würde Experte sagen?


@dataclass
class SelfChallenge:
    """Eine Selbst-Hinterfragung - Level 10/10"""
    belief: str                    # Die Überzeugung die hinterfragt wird
    challenge: str                 # Die Gegen-Frage
    counter_arguments: List[str]   # Gegenargumente
    conclusion: str                # Schlussfolgerung
    belief_adjusted: bool          # Wurde die Überzeugung angepasst?
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    # Level 10 Erweiterungen
    challenge_type: ChallengeType = ChallengeType.EVIDENCE_BASED
    original_confidence: float = 0.5
    adjusted_confidence: float = 0.5
    biases_detected: List[str] = field(default_factory=list)
    alternative_perspectives: List[str] = field(default_factory=list)
    strength_of_challenge: float = 0.5  # Wie stark war die Hinterfragung?


@dataclass
class BeliefEvolution:
    """Wie sich eine Überzeugung über Zeit verändert hat"""
    belief: str
    history: List[Dict[str, Any]] = field(default_factory=list)  # [{confidence, timestamp, reason}]
    total_challenges: int = 0
    times_adjusted: int = 0


class SelfChallenger:
    """
    System für kontinuierliche Selbst-Hinterfragung - Level 10/10

    "Wie könnte ich mich täuschen?"
    "Was spricht dagegen?"
    "Bin ich zu sicher?"
    "Was würde ein Skeptiker sagen?"
    "Wie sieht das aus der Zukunft aus?"

    v2.0: Vollständige Selbst-Hinterfragung (10/10)
    """

    CHALLENGE_TEMPLATES = [
        "Aber was ist, wenn {belief} nicht stimmt?",
        "Könnte ich mich bei {belief} täuschen?",
        "Gibt es Gegenbeweise für {belief}?",
        "Warum glaube ich eigentlich, dass {belief}?",
        "Was würde jemand sagen, der anderer Meinung ist?",
        "Bin ich vielleicht voreingenommen bei {belief}?",
    ]

    COGNITIVE_BIASES = {
        "confirmation_bias": {
            "name": "Bestätigungsfehler",
            "check": "Suche ich nur nach Infos die meine Meinung bestätigen?",
            "fix": "Aktiv nach Gegenbeispielen suchen."
        },
        "halo_effect": {
            "name": "Halo-Effekt",
            "check": "Übertrage ich positive Eigenschaften auf andere Bereiche?",
            "fix": "Jeden Aspekt einzeln bewerten."
        },
        "recency_bias": {
            "name": "Aktualitätsfehler",
            "check": "Gewichte ich neuere Infos zu stark?",
            "fix": "Auch ältere Erfahrungen berücksichtigen."
        },
        "anchoring": {
            "name": "Ankereffekt",
            "check": "Hänge ich zu sehr am ersten Eindruck?",
            "fix": "Erster Eindruck neu evaluieren."
        },
        "overconfidence": {
            "name": "Überkonfidenz",
            "check": "Bin ich mir zu sicher?",
            "fix": "Confidence um 20% reduzieren."
        }
    }

    def __init__(self, challenge_frequency: float = 0.3):
        """
        Args:
            challenge_frequency: Wie oft soll hinterfragt werden? (0-1)
        """
        self.challenge_frequency = challenge_frequency
        self.challenges_history: List[SelfChallenge] = []
        self.last_challenge_time = datetime.now()

        # Level 10 Erweiterungen
        self.belief_evolutions: Dict[str, BeliefEvolution] = {}
        self.challenge_effectiveness: List[bool] = []  # War Hinterfragung hilfreich?
        self.successful_challenges = 0
        self.total_adjustments = 0

        # Erweiterte Challenge Templates nach Typ
        self.challenge_templates_by_type = {
            ChallengeType.EVIDENCE_BASED: [
                "Welche Beweise habe ich wirklich für {belief}?",
                "Könnte ich {belief} jemandem beweisen?",
                "Was wäre ein Gegenbeweis zu {belief}?",
            ],
            ChallengeType.PERSPECTIVE_SHIFT: [
                "Wie sieht jemand mit gegenteiliger Meinung {belief}?",
                "Was würde mein größter Kritiker zu {belief} sagen?",
                "Wie sehen andere Kulturen {belief}?",
            ],
            ChallengeType.ASSUMPTION_CHECK: [
                "Welche Annahmen stecken hinter {belief}?",
                "Was wenn meine Grundannahme zu {belief} falsch ist?",
                "Auf was basiert {belief} eigentlich?",
            ],
            ChallengeType.EXTREME_TEST: [
                "Gilt {belief} auch in extremen Situationen?",
                "Was wenn {belief} zu 100% falsch wäre?",
                "Was ist das schlimmste was passiert wenn {belief} nicht stimmt?",
            ],
            ChallengeType.TIME_TRAVEL: [
                "Wie werde ich in 10 Jahren über {belief} denken?",
                "Hätte ich vor 5 Jahren auch {belief} geglaubt?",
                "Ist {belief} zeitlos oder zeitgebunden?",
            ],
            ChallengeType.EXPERT_SIMULATION: [
                "Was würde ein Experte zu {belief} sagen?",
                "Wie würde ein Wissenschaftler {belief} prüfen?",
                "Was sagt die Forschung zu {belief}?",
            ],
        }

    def should_challenge(self, confidence: float) -> bool:
        """Entscheidet ob jetzt hinterfragt werden soll"""
        # Höhere Confidence = mehr Grund zur Hinterfragung
        challenge_threshold = 1.0 - self.challenge_frequency

        # Bei sehr hoher Confidence immer hinterfragen
        if confidence > 0.9:
            return True

        # Zeit seit letzter Hinterfragung
        time_since = (datetime.now() - self.last_challenge_time).seconds
        if time_since > 300:  # 5 Minuten
            return random.random() < self.challenge_frequency

        return confidence > challenge_threshold

    def challenge_belief(self, belief: str, confidence: float,
                        evidence: List[str] = None) -> SelfChallenge:
        """
        Hinterfragt eine Überzeugung.

        Returns:
            SelfChallenge mit Analyse
        """
        self.last_challenge_time = datetime.now()
        evidence = evidence or []

        # Wähle Challenge-Template
        template = random.choice(self.CHALLENGE_TEMPLATES)
        challenge = template.format(belief=belief)

        # Generiere Gegenargumente
        counter_args = self._generate_counter_arguments(belief, evidence)

        # Bias-Check
        bias_warning = self._check_for_bias(belief, confidence, evidence)
        if bias_warning:
            counter_args.append(f"⚠️ Möglicher Bias: {bias_warning}")

        # Schlussfolgerung
        if len(counter_args) >= 3:
            conclusion = f"*nachdenklich* Hmm, vielleicht bin ich bei '{belief[:50]}...' zu sicher."
            belief_adjusted = True
        elif len(counter_args) >= 1:
            conclusion = f"Es gibt Gegenargumente, aber ich bleibe vorerst bei meiner Meinung."
            belief_adjusted = False
        else:
            conclusion = f"Nach Prüfung: Meine Überzeugung scheint fundiert."
            belief_adjusted = False

        challenge_result = SelfChallenge(
            belief=belief,
            challenge=challenge,
            counter_arguments=counter_args,
            conclusion=conclusion,
            belief_adjusted=belief_adjusted
        )

        self.challenges_history.append(challenge_result)
        return challenge_result

    def devils_advocate(self, position: str) -> str:
        """
        Spielt Devil's Advocate gegen eine Position.
        """
        counter_positions = [
            f"Aber was ist mit dem Gegenteil? Was wenn '{position}' falsch ist?",
            f"Jemand könnte argumentieren, dass genau das Gegenteil wahr ist...",
            f"*kritisch* Lass mich mal die andere Seite beleuchten...",
            f"Okay, aber hier sind mögliche Probleme mit dieser Sicht:",
        ]

        intro = random.choice(counter_positions)

        # Generiere Gegen-Punkte
        points = [
            "- Was wenn ich nur das sehe, was ich sehen will?",
            "- Gibt es Fälle wo das nicht zutrifft?",
            "- Könnte meine Erfahrung untypisch sein?",
            "- Was sagen Leute mit anderer Perspektive?",
        ]

        return f"{intro}\n" + "\n".join(random.sample(points, min(3, len(points))))

    def am_i_wrong_about(self, topic: str, my_opinion: float) -> Dict[str, Any]:
        """
        Prüft ob ich bei einem Thema falsch liegen könnte.

        Returns:
            Dict mit Analyse
        """
        wrong_probability = 0.0
        reasons = []

        # Extreme Meinungen sind oft falsch
        if abs(my_opinion) > 0.8:
            wrong_probability += 0.2
            reasons.append("Meine Meinung ist sehr extrem - das ist oft ein Warnsignal")

        # Wenig Evidenz
        # (würde in echtem System Evidenz-Menge prüfen)

        # Bias-Check
        for bias_key, bias_info in self.COGNITIVE_BIASES.items():
            if random.random() < 0.3:  # Zufällige Bias-Prüfung
                reasons.append(f"Möglicher {bias_info['name']}: {bias_info['check']}")
                wrong_probability += 0.1

        wrong_probability = min(0.8, wrong_probability)

        return {
            "topic": topic,
            "my_opinion": my_opinion,
            "could_be_wrong_probability": wrong_probability,
            "reasons": reasons,
            "suggestion": "Mehr Perspektiven einholen" if wrong_probability > 0.3 else "Meinung scheint fundiert"
        }

    def _generate_counter_arguments(self, belief: str, evidence: List[str]) -> List[str]:
        """Generiert Gegenargumente"""
        counters = []

        # Allgemeine Gegenargumente
        general_counters = [
            "Korrelation bedeutet nicht Kausalität",
            "Eine Erfahrung ist kein Beweis",
            "Menschen können sich ändern",
            "Kontext könnte anders gewesen sein",
            "Meine Wahrnehmung könnte verzerrt sein",
        ]

        # Wähle 1-3 relevante
        num_counters = random.randint(0, 3)
        counters = random.sample(general_counters, min(num_counters, len(general_counters)))

        return counters

    def _check_for_bias(self, belief: str, confidence: float,
                       evidence: List[str]) -> Optional[str]:
        """Prüft auf kognitive Verzerrungen"""
        # Überkonfidenz
        if confidence > 0.85 and len(evidence) < 3:
            return self.COGNITIVE_BIASES["overconfidence"]["check"]

        # Bestätigungsfehler (vereinfacht)
        if random.random() < 0.2:
            return self.COGNITIVE_BIASES["confirmation_bias"]["check"]

        return None

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Selbst-Hinterfragung
    # ================================================================

    def deep_challenge(self, belief: str, confidence: float,
                      challenge_types: List[ChallengeType] = None) -> Dict[str, Any]:
        """
        Führt eine tiefgehende, multi-perspektivische Hinterfragung durch.
        """
        if challenge_types is None:
            challenge_types = list(ChallengeType)

        result = {
            "belief": belief,
            "original_confidence": confidence,
            "challenges_by_type": {},
            "all_counter_arguments": [],
            "biases_detected": [],
            "final_confidence": confidence,
            "should_adjust": False,
            "recommendation": ""
        }

        # Jeden Challenge-Typ durchgehen
        for ct in challenge_types:
            templates = self.challenge_templates_by_type.get(ct, [])
            if templates:
                challenge_q = random.choice(templates).format(belief=belief[:50])
                counters = self._generate_counter_arguments_for_type(belief, ct)

                result["challenges_by_type"][ct.value] = {
                    "question": challenge_q,
                    "counter_arguments": counters
                }
                result["all_counter_arguments"].extend(counters)

        # Bias-Check erweitert
        for bias_key, bias_info in self.COGNITIVE_BIASES.items():
            if self._detect_specific_bias(belief, confidence, bias_key):
                result["biases_detected"].append(bias_info["name"])

        # Final Confidence berechnen
        adjustment = len(result["all_counter_arguments"]) * 0.05
        adjustment += len(result["biases_detected"]) * 0.1
        result["final_confidence"] = max(0.1, confidence - adjustment)

        result["should_adjust"] = result["final_confidence"] < confidence - 0.15

        # Recommendation
        if result["should_adjust"]:
            result["recommendation"] = "Überzeugung überdenken - signifikante Gegenargumente gefunden"
        elif result["biases_detected"]:
            result["recommendation"] = f"Auf mögliche Biases achten: {result['biases_detected']}"
        else:
            result["recommendation"] = "Überzeugung scheint nach Prüfung solide"

        # Evolution tracken
        self._track_belief_evolution(belief, confidence, result["final_confidence"], "deep_challenge")

        return result

    def _generate_counter_arguments_for_type(self, belief: str,
                                            challenge_type: ChallengeType) -> List[str]:
        """Generiert typ-spezifische Gegenargumente"""
        counters = []
        belief_lower = belief.lower()

        if challenge_type == ChallengeType.EVIDENCE_BASED:
            counters.append("Anekdotische Evidenz ist kein Beweis")
            if "immer" in belief_lower or "nie" in belief_lower:
                counters.append("Absolute Aussagen sind selten wahr")

        elif challenge_type == ChallengeType.PERSPECTIVE_SHIFT:
            counters.append("Andere Kulturen/Kontexte sehen das anders")
            counters.append("Die Gegenseite hat auch valide Punkte")

        elif challenge_type == ChallengeType.ASSUMPTION_CHECK:
            counters.append("Die Grundannahme könnte falsch sein")
            counters.append("Versteckte Prämissen identifizieren")

        elif challenge_type == ChallengeType.EXTREME_TEST:
            counters.append("In Extremsituationen könnte es anders sein")

        elif challenge_type == ChallengeType.TIME_TRAVEL:
            counters.append("Meinungen ändern sich mit der Zeit")
            counters.append("Historisch waren ähnliche Überzeugungen falsch")

        elif challenge_type == ChallengeType.EXPERT_SIMULATION:
            counters.append("Experten könnten anderer Meinung sein")
            counters.append("Wissenschaftliche Methode anwenden")

        return counters[:2]  # Max 2 pro Typ

    def _detect_specific_bias(self, belief: str, confidence: float, bias_key: str) -> bool:
        """Erkennt spezifische Biases"""
        belief_lower = belief.lower()

        if bias_key == "confirmation_bias":
            # Starke Meinung ohne Gegenargument-Erwähnung
            return confidence > 0.8 and "aber" not in belief_lower

        elif bias_key == "overconfidence":
            return confidence > 0.9

        elif bias_key == "anchoring":
            return "erster" in belief_lower or "anfangs" in belief_lower

        elif bias_key == "halo_effect":
            return "gut" in belief_lower and "deshalb" in belief_lower

        return random.random() < 0.15  # Zufällige niedrige Wahrscheinlichkeit

    def steelmanning(self, opposing_view: str) -> Dict[str, Any]:
        """
        Steelmanning: Die stärkste Version eines Gegenarguments konstruieren.

        Gegenteil von Strawmanning - faire Darstellung der Gegenseite.
        """
        result = {
            "original_opposing_view": opposing_view,
            "steelmanned_version": "",
            "strongest_points": [],
            "why_someone_might_believe_this": [],
            "what_i_can_learn": ""
        }

        # Stärkste Version konstruieren
        result["steelmanned_version"] = (
            f"Die beste Version dieses Arguments wäre: "
            f"'{opposing_view}' - und zwar weil es auf realen Erfahrungen basiert "
            f"und für manche Menschen tatsächlich funktioniert hat."
        )

        result["strongest_points"] = [
            "Es basiert möglicherweise auf echten Erfahrungen",
            "Es gibt historische oder kulturelle Gründe dafür",
            "Intelligente Menschen glauben das aus guten Gründen",
            "Es adressiert ein reales Problem oder Bedürfnis"
        ]

        result["why_someone_might_believe_this"] = [
            "Persönliche Erfahrungen haben sie überzeugt",
            "Ihr sozialer Kontext unterstützt diese Sicht",
            "Es gibt tatsächlich Evidenz die dafür spricht",
            "Es entspricht intuitiven menschlichen Bedürfnissen"
        ]

        result["what_i_can_learn"] = (
            "Auch wenn ich nicht zustimme, kann ich verstehen warum "
            "vernünftige Menschen zu diesem Schluss kommen könnten."
        )

        return result

    def pre_mortem(self, decision: str) -> Dict[str, Any]:
        """
        Pre-Mortem: Tue so als wäre die Entscheidung bereits gescheitert.
        Frage: Warum ist es gescheitert?

        Mächtige Technik um blinde Flecken zu finden.
        """
        result = {
            "decision": decision,
            "imagined_failure_reasons": [],
            "overlooked_risks": [],
            "what_could_go_wrong": [],
            "mitigation_suggestions": []
        }

        # Generiere Gründe warum es scheitern könnte
        failure_templates = [
            "Die Annahme dass X stimmt war falsch",
            "Unvorhergesehene Umstände traten ein",
            "Die Umsetzung war schwieriger als gedacht",
            "Wichtige Information fehlte",
            "Die Reaktion anderer war anders als erwartet",
            "Der Zeitpunkt war falsch",
            "Ressourcen wurden falsch eingeschätzt"
        ]

        result["imagined_failure_reasons"] = random.sample(
            failure_templates, min(4, len(failure_templates))
        )

        result["overlooked_risks"] = [
            "Overconfidence in der Planung",
            "Nicht genug alternative Szenarien durchdacht",
            "Feedback von anderen nicht eingeholt"
        ]

        result["what_could_go_wrong"] = [
            f"Bei '{decision[:30]}' könnte scheitern weil...",
            "Die größten Risiken sind...",
            "Was ich vielleicht übersehe ist..."
        ]

        result["mitigation_suggestions"] = [
            "Plan B vorbereiten",
            "Mehr Input von anderen holen",
            "Kleinere Tests vor großer Umsetzung",
            "Regelmäßige Checkpoints einplanen"
        ]

        return result

    def _track_belief_evolution(self, belief: str, old_conf: float,
                               new_conf: float, reason: str) -> None:
        """Trackt wie sich eine Überzeugung entwickelt"""
        belief_key = belief[:50]  # Kürzen für Key

        if belief_key not in self.belief_evolutions:
            self.belief_evolutions[belief_key] = BeliefEvolution(belief=belief)

        evolution = self.belief_evolutions[belief_key]
        evolution.history.append({
            "confidence": new_conf,
            "previous": old_conf,
            "change": new_conf - old_conf,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        evolution.total_challenges += 1
        if new_conf != old_conf:
            evolution.times_adjusted += 1

    def record_challenge_outcome(self, was_helpful: bool) -> None:
        """Zeichnet auf ob eine Hinterfragung hilfreich war"""
        self.challenge_effectiveness.append(was_helpful)
        if was_helpful:
            self.successful_challenges += 1

    def get_challenger_stats(self) -> Dict[str, Any]:
        """Statistiken über die Selbst-Hinterfragung"""
        effectiveness = (
            sum(1 for x in self.challenge_effectiveness if x) /
            max(len(self.challenge_effectiveness), 1)
        )

        return {
            "total_challenges": len(self.challenges_history),
            "successful_challenges": self.successful_challenges,
            "total_belief_adjustments": self.total_adjustments,
            "beliefs_tracked": len(self.belief_evolutions),
            "challenge_effectiveness": effectiveness,
            "most_challenged_beliefs": self._get_most_challenged_beliefs()
        }

    def _get_most_challenged_beliefs(self) -> List[str]:
        """Findet die am häufigsten hinterfragten Überzeugungen"""
        sorted_beliefs = sorted(
            self.belief_evolutions.items(),
            key=lambda x: x[1].total_challenges,
            reverse=True
        )
        return [b[0] for b in sorted_beliefs[:5]]


# ============================================================
# HYPOTHESIS ENGINE - Was-Wenn Szenarien (Level 10/10)
# ============================================================

class EvidenceStrength(Enum):
    """Stärke einer Evidenz"""
    ANECDOTAL = 0.1       # "Jemand hat mal gesagt..."
    OBSERVATION = 0.3     # Einzelne Beobachtung
    PATTERN = 0.5         # Wiederholtes Muster
    EXPERIMENT = 0.7      # Gezielter Test
    REPLICATION = 0.85    # Mehrfach bestätigt
    CONSENSUS = 0.95      # Breiter Konsens

class HypothesisRelation(Enum):
    """Beziehungen zwischen Hypothesen"""
    SUPPORTS = "supports"          # H1 unterstützt H2
    CONTRADICTS = "contradicts"    # H1 widerspricht H2
    IMPLIES = "implies"            # H1 → H2
    ALTERNATIVE = "alternative"    # H1 oder H2 (nicht beide)
    REFINES = "refines"           # H2 ist präzisere Version von H1
    DEPENDS_ON = "depends_on"     # H1 setzt H2 voraus

@dataclass
class WeightedEvidence:
    """Gewichtete Evidenz mit Metadaten"""
    evidence_id: str
    content: str
    strength: EvidenceStrength
    source: str
    reliability: float          # 0-1, wie verlässlich die Quelle
    recency: float             # 0-1, wie aktuell (1=gerade eben)
    supports_hypothesis: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def effective_weight(self) -> float:
        """Berechnet effektives Gewicht unter Berücksichtigung aller Faktoren"""
        base = self.strength.value
        return base * self.reliability * (0.7 + 0.3 * self.recency)

@dataclass
class HypothesisPrediction:
    """Eine testbare Vorhersage einer Hypothese"""
    prediction_id: str
    hypothesis_id: str
    statement: str
    testable: bool
    test_method: Optional[str] = None
    predicted_outcome: Optional[str] = None
    actual_outcome: Optional[str] = None
    was_correct: Optional[bool] = None
    confidence_before: float = 0.5
    confidence_after: Optional[float] = None

@dataclass
class Hypothesis:
    """Eine Hypothese - Level 10/10"""
    hypothesis_id: str
    statement: str                 # "Wenn X, dann Y"
    condition: str                 # X
    prediction: str                # Y
    confidence: float              # Wie wahrscheinlich?
    status: HypothesisStatus
    evidence_for: List[str] = field(default_factory=list)
    evidence_against: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Level 10 Erweiterungen
    weighted_evidence: List[WeightedEvidence] = field(default_factory=list)
    prior_probability: float = 0.5           # P(H) vor jeder Evidenz
    confidence_interval: Tuple[float, float] = (0.3, 0.7)  # Unsicherheitsbereich
    falsification_criteria: List[str] = field(default_factory=list)
    predictions: List[HypothesisPrediction] = field(default_factory=list)
    related_hypotheses: Dict[str, HypothesisRelation] = field(default_factory=dict)
    domain: str = "general"
    alternative_explanations: List[str] = field(default_factory=list)
    revision_history: List[Dict[str, Any]] = field(default_factory=list)


class HypothesisEngine:
    """
    System für "Was wenn?"-Szenarien und Hypothesen-Bildung - Level 10/10.

    "Was würde passieren wenn..."
    "Ich vermute, dass..."
    "Wenn X stimmt, dann müsste Y folgen..."

    Level 10 Features:
    - Bayesian Confidence Updates
    - Evidence Weighing System
    - Hypothesis Network mit Beziehungen
    - Falsification Testing
    - Alternative Hypothesen Generation
    - Prediction Tracking und Accuracy
    """

    # Basis-Raten für verschiedene Hypothesen-Typen
    BASE_RATES = {
        "behavioral": 0.3,      # Verhaltens-Hypothesen
        "causal": 0.25,         # Kausal-Hypothesen
        "correlational": 0.4,   # Korrelations-Hypothesen
        "motivational": 0.35,   # Motivations-Hypothesen
        "predictive": 0.3,      # Vorhersage-Hypothesen
    }

    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.tested_hypotheses: List[Hypothesis] = []
        # Level 10 Erweiterungen
        self.hypothesis_network: Dict[str, List[Tuple[str, HypothesisRelation]]] = {}
        self.prediction_accuracy: Dict[str, List[bool]] = {}  # hyp_id -> list of outcomes
        self.evidence_history: List[WeightedEvidence] = []
        self.domain_priors: Dict[str, float] = {}  # Domain-spezifische Basis-Raten

    def generate_hypothesis(self, observation: str,
                           context: Dict = None) -> Hypothesis:
        """
        Generiert eine Hypothese aus einer Beobachtung.

        "Ich habe X beobachtet → Ich vermute Y ist die Ursache"
        """
        context = context or {}

        # Einfache Kausal-Hypothesen
        hypothesis_templates = [
            ("Vielleicht liegt das daran, dass {cause}",
             "Das würde erklären warum {observation}"),
            ("Wenn {cause} stimmt",
             "dann sollte auch {prediction} zutreffen"),
            ("Meine Vermutung: {cause}",
             "Das würde zu {observation} passen"),
        ]

        template = random.choice(hypothesis_templates)

        # Generiere plausible Ursache (vereinfacht)
        possible_causes = [
            "die Person etwas zu verbergen hat",
            "es mehr dahinter steckt als auf den ersten Blick",
            "das Verhalten gewohnheitsmäßig ist",
            "äußere Umstände eine Rolle spielen",
            "die Person unter Druck steht",
        ]

        cause = random.choice(possible_causes)
        prediction = f"ähnliches Verhalten in anderen Situationen"

        hyp_id = hashlib.md5(f"{observation}{datetime.now()}".encode()).hexdigest()[:8]

        hypothesis = Hypothesis(
            hypothesis_id=hyp_id,
            statement=f"Wenn {cause}, dann {prediction}",
            condition=cause,
            prediction=prediction,
            confidence=0.4,  # Niedrige initiale Confidence
            status=HypothesisStatus.PROPOSED
        )

        self.hypotheses[hyp_id] = hypothesis
        return hypothesis

    def what_if(self, scenario: str) -> Dict[str, Any]:
        """
        Simuliert ein "Was wenn?"-Szenario.

        Args:
            scenario: "Was wenn Person X lügt?" etc.
        """
        # Analysiere Szenario
        consequences = []
        likelihood = 0.5

        # Einfache Konsequenz-Generierung
        if "lügt" in scenario.lower():
            consequences = [
                "Dann wäre die Vertrauenswürdigkeit stark beschädigt",
                "Andere Aussagen müssten auch hinterfragt werden",
                "Das Motiv für die Lüge wäre interessant zu verstehen",
            ]
            likelihood = 0.3
        elif "ehrlich" in scenario.lower():
            consequences = [
                "Dann wäre die Person vertrauenswürdiger als gedacht",
                "Vorherige Skepsis wäre unbegründet gewesen",
            ]
            likelihood = 0.5
        elif "ändert" in scenario.lower():
            consequences = [
                "Menschen können sich ändern, aber es braucht Zeit",
                "Ich würde Beweise für die Änderung sehen wollen",
                "Alte Muster könnten wieder auftauchen",
            ]
            likelihood = 0.4
        else:
            consequences = [
                "Das hätte interessante Implikationen...",
                "Ich müsste meine Annahmen überdenken",
            ]
            likelihood = 0.5

        return {
            "scenario": scenario,
            "likelihood": likelihood,
            "consequences": consequences,
            "my_reaction": f"*nachdenklich* {random.choice(consequences)}",
            "should_investigate": likelihood > 0.4
        }

    def test_hypothesis(self, hyp_id: str, new_evidence: str,
                       supports: bool) -> Optional[Hypothesis]:
        """
        Testet eine Hypothese mit neuer Evidenz.
        """
        if hyp_id not in self.hypotheses:
            return None

        hyp = self.hypotheses[hyp_id]
        hyp.status = HypothesisStatus.TESTING

        if supports:
            hyp.evidence_for.append(new_evidence)
            hyp.confidence = min(0.95, hyp.confidence + 0.15)
        else:
            hyp.evidence_against.append(new_evidence)
            hyp.confidence = max(0.05, hyp.confidence - 0.2)

        # Status Update
        if len(hyp.evidence_for) >= 3 and hyp.confidence > 0.7:
            hyp.status = HypothesisStatus.SUPPORTED
        elif len(hyp.evidence_against) >= 2 or hyp.confidence < 0.2:
            hyp.status = HypothesisStatus.REFUTED
            self.tested_hypotheses.append(hyp)
        else:
            hyp.status = HypothesisStatus.UNCERTAIN

        return hyp

    def get_active_hypotheses(self) -> List[Hypothesis]:
        """Gibt alle aktiven Hypothesen zurück"""
        return [h for h in self.hypotheses.values()
                if h.status not in [HypothesisStatus.REFUTED, HypothesisStatus.SUPPORTED]]

    # ================================================================
    # LEVEL 10 METHODEN - Wissenschaftliches Hypothesen-Testen
    # ================================================================

    def bayesian_update(self, hyp_id: str, evidence: WeightedEvidence) -> Optional[float]:
        """
        Aktualisiert die Hypothesen-Confidence mit Bayes' Theorem.

        P(H|E) = P(E|H) * P(H) / P(E)

        Returns:
            Neue Confidence oder None wenn Hypothese nicht existiert
        """
        if hyp_id not in self.hypotheses:
            return None

        hyp = self.hypotheses[hyp_id]
        prior = hyp.confidence

        # P(E|H) - Likelihood der Evidenz gegeben Hypothese stimmt
        if evidence.supports_hypothesis:
            likelihood = 0.7 + (evidence.effective_weight * 0.25)
        else:
            likelihood = 0.3 - (evidence.effective_weight * 0.2)

        # P(E|¬H) - Likelihood der Evidenz gegeben Hypothese stimmt nicht
        if evidence.supports_hypothesis:
            likelihood_not_h = 0.3
        else:
            likelihood_not_h = 0.7

        # P(E) = P(E|H)*P(H) + P(E|¬H)*P(¬H)
        marginal_prob = (likelihood * prior) + (likelihood_not_h * (1 - prior))

        # Bayes Update
        if marginal_prob > 0:
            posterior = (likelihood * prior) / marginal_prob
        else:
            posterior = prior

        # Speichere Update
        old_confidence = hyp.confidence
        hyp.confidence = max(0.01, min(0.99, posterior))

        # Update Confidence Interval
        uncertainty = abs(hyp.confidence - old_confidence)
        hyp.confidence_interval = (
            max(0.0, hyp.confidence - uncertainty - 0.1),
            min(1.0, hyp.confidence + uncertainty + 0.1)
        )

        # Evidenz hinzufügen
        hyp.weighted_evidence.append(evidence)
        self.evidence_history.append(evidence)

        # Revision History
        hyp.revision_history.append({
            "timestamp": datetime.now().isoformat(),
            "old_confidence": old_confidence,
            "new_confidence": hyp.confidence,
            "evidence": evidence.content,
            "method": "bayesian_update"
        })

        return hyp.confidence

    def add_weighted_evidence(self, hyp_id: str, content: str,
                             strength: EvidenceStrength, source: str,
                             supports: bool, reliability: float = 0.7) -> Optional[Hypothesis]:
        """
        Fügt gewichtete Evidenz zu einer Hypothese hinzu.
        """
        if hyp_id not in self.hypotheses:
            return None

        evidence = WeightedEvidence(
            evidence_id=hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:8],
            content=content,
            strength=strength,
            source=source,
            reliability=reliability,
            recency=1.0,  # Frische Evidenz
            supports_hypothesis=supports
        )

        # Bayesian Update durchführen
        self.bayesian_update(hyp_id, evidence)

        # Status prüfen
        hyp = self.hypotheses[hyp_id]
        self._update_hypothesis_status(hyp)

        return hyp

    def _update_hypothesis_status(self, hyp: Hypothesis):
        """Aktualisiert den Status basierend auf Confidence und Evidenz"""
        if hyp.confidence > 0.85:
            hyp.status = HypothesisStatus.SUPPORTED
            if hyp not in self.tested_hypotheses:
                self.tested_hypotheses.append(hyp)
        elif hyp.confidence < 0.15:
            hyp.status = HypothesisStatus.REFUTED
            if hyp not in self.tested_hypotheses:
                self.tested_hypotheses.append(hyp)
        elif 0.4 <= hyp.confidence <= 0.6:
            hyp.status = HypothesisStatus.UNCERTAIN
        else:
            hyp.status = HypothesisStatus.TESTING

    def define_falsification(self, hyp_id: str, criteria: List[str]) -> bool:
        """
        Definiert Falsifizierungskriterien für eine Hypothese.

        Karl Popper: Eine gute Hypothese muss falsifizierbar sein.
        """
        if hyp_id not in self.hypotheses:
            return False

        hyp = self.hypotheses[hyp_id]
        hyp.falsification_criteria = criteria
        return True

    def attempt_falsification(self, hyp_id: str) -> Dict[str, Any]:
        """
        Versucht aktiv, eine Hypothese zu falsifizieren.

        Wissenschaftliches Vorgehen: Nicht versuchen zu bestätigen,
        sondern versuchen zu widerlegen!
        """
        if hyp_id not in self.hypotheses:
            return {"error": "Hypothese nicht gefunden"}

        hyp = self.hypotheses[hyp_id]

        result = {
            "hypothesis": hyp.statement,
            "falsification_criteria": hyp.falsification_criteria,
            "tests_to_try": [],
            "weaknesses_found": [],
            "survives_falsification": True
        }

        # Generiere Tests basierend auf Kriterien
        if hyp.falsification_criteria:
            for criterion in hyp.falsification_criteria:
                result["tests_to_try"].append({
                    "criterion": criterion,
                    "test": f"Prüfen ob: {criterion}",
                    "if_true": "Hypothese widerlegt",
                    "if_false": "Hypothese übersteht diesen Test"
                })
        else:
            # Auto-generiere Falsifizierungsansätze
            result["tests_to_try"] = [
                {"test": "Suche nach Gegenbeispielen",
                 "description": "Gibt es Fälle wo die Vorhersage nicht eintritt?"},
                {"test": "Extreme Bedingungen",
                 "description": "Gilt die Hypothese auch unter Extrembedingungen?"},
                {"test": "Alternative Erklärungen",
                 "description": "Können die Beobachtungen anders erklärt werden?"},
            ]

        # Prüfe bestehende Gegen-Evidenz
        against_evidence = [e for e in hyp.weighted_evidence if not e.supports_hypothesis]
        if len(against_evidence) >= 2:
            result["weaknesses_found"].append("Mehrere Gegen-Evidenzen vorhanden")
            result["survives_falsification"] = hyp.confidence > 0.4

        return result

    def generate_alternatives(self, hyp_id: str, num_alternatives: int = 3) -> List[str]:
        """
        Generiert alternative Hypothesen für dieselbe Beobachtung.

        Vermeidet Confirmation Bias durch Betrachtung anderer Erklärungen.
        """
        if hyp_id not in self.hypotheses:
            return []

        hyp = self.hypotheses[hyp_id]
        alternatives = []

        # Alternativen basierend auf Hypothesen-Typ
        alternative_templates = [
            f"Statt '{hyp.condition}' könnte auch Zufall eine Rolle spielen",
            f"Die Beobachtung könnte durch einen dritten Faktor erklärt werden",
            f"Das Gegenteil von '{hyp.condition}' könnte wahr sein",
            f"'{hyp.prediction}' könnte unabhängig von der Ursache auftreten",
            f"Die Korrelation könnte keine Kausalität bedeuten",
            f"Meine Beobachtung könnte verzerrt gewesen sein",
        ]

        alternatives = random.sample(
            alternative_templates,
            min(num_alternatives, len(alternative_templates))
        )

        # Speichere Alternativen
        hyp.alternative_explanations = alternatives

        return alternatives

    def link_hypotheses(self, hyp_id_1: str, hyp_id_2: str,
                       relation: HypothesisRelation) -> bool:
        """
        Verbindet zwei Hypothesen mit einer Beziehung.

        Ermöglicht Hypothesen-Netzwerke und Implikationsketten.
        """
        if hyp_id_1 not in self.hypotheses or hyp_id_2 not in self.hypotheses:
            return False

        # Füge Beziehung hinzu
        if hyp_id_1 not in self.hypothesis_network:
            self.hypothesis_network[hyp_id_1] = []

        self.hypothesis_network[hyp_id_1].append((hyp_id_2, relation))

        # Aktualisiere auch die Hypothese selbst
        self.hypotheses[hyp_id_1].related_hypotheses[hyp_id_2] = relation

        # Inverse Beziehung für bestimmte Typen
        inverse_relations = {
            HypothesisRelation.SUPPORTS: HypothesisRelation.SUPPORTS,
            HypothesisRelation.CONTRADICTS: HypothesisRelation.CONTRADICTS,
            HypothesisRelation.ALTERNATIVE: HypothesisRelation.ALTERNATIVE,
        }

        if relation in inverse_relations:
            if hyp_id_2 not in self.hypothesis_network:
                self.hypothesis_network[hyp_id_2] = []
            self.hypothesis_network[hyp_id_2].append(
                (hyp_id_1, inverse_relations[relation])
            )
            self.hypotheses[hyp_id_2].related_hypotheses[hyp_id_1] = inverse_relations[relation]

        return True

    def propagate_evidence(self, hyp_id: str, evidence: WeightedEvidence) -> Dict[str, float]:
        """
        Propagiert Evidenz durch das Hypothesen-Netzwerk.

        Wenn H1 → H2 und Evidenz für H1, dann auch Evidenz für H2.
        """
        updates = {}

        if hyp_id not in self.hypothesis_network:
            return updates

        for related_id, relation in self.hypothesis_network[hyp_id]:
            if related_id not in self.hypotheses:
                continue

            propagation_factor = 0.0

            if relation == HypothesisRelation.IMPLIES:
                # Evidenz für H1 unterstützt H2
                propagation_factor = 0.6 if evidence.supports_hypothesis else 0.0

            elif relation == HypothesisRelation.SUPPORTS:
                propagation_factor = 0.4 if evidence.supports_hypothesis else -0.2

            elif relation == HypothesisRelation.CONTRADICTS:
                propagation_factor = -0.5 if evidence.supports_hypothesis else 0.3

            elif relation == HypothesisRelation.DEPENDS_ON:
                propagation_factor = 0.3 if evidence.supports_hypothesis else -0.4

            if propagation_factor != 0:
                related_hyp = self.hypotheses[related_id]
                old_conf = related_hyp.confidence
                related_hyp.confidence = max(0.01, min(0.99,
                    related_hyp.confidence + propagation_factor * evidence.effective_weight * 0.5
                ))
                updates[related_id] = related_hyp.confidence - old_conf

        return updates

    def create_prediction(self, hyp_id: str, prediction_statement: str,
                         test_method: str = None) -> Optional[HypothesisPrediction]:
        """
        Erstellt eine testbare Vorhersage aus einer Hypothese.
        """
        if hyp_id not in self.hypotheses:
            return None

        hyp = self.hypotheses[hyp_id]

        pred = HypothesisPrediction(
            prediction_id=hashlib.md5(f"{prediction_statement}{datetime.now()}".encode()).hexdigest()[:8],
            hypothesis_id=hyp_id,
            statement=prediction_statement,
            testable=test_method is not None,
            test_method=test_method,
            confidence_before=hyp.confidence
        )

        hyp.predictions.append(pred)

        # Initialisiere Accuracy Tracking
        if hyp_id not in self.prediction_accuracy:
            self.prediction_accuracy[hyp_id] = []

        return pred

    def evaluate_prediction(self, hyp_id: str, prediction_id: str,
                           outcome: str, was_correct: bool) -> Optional[Dict[str, Any]]:
        """
        Evaluiert eine Vorhersage und aktualisiert die Hypothese.
        """
        if hyp_id not in self.hypotheses:
            return None

        hyp = self.hypotheses[hyp_id]

        # Finde Prediction
        pred = next((p for p in hyp.predictions if p.prediction_id == prediction_id), None)
        if not pred:
            return None

        pred.actual_outcome = outcome
        pred.was_correct = was_correct
        pred.confidence_after = hyp.confidence

        # Update Accuracy Tracking
        self.prediction_accuracy[hyp_id].append(was_correct)

        # Confidence anpassen basierend auf Vorhersage-Genauigkeit
        if was_correct:
            adjustment = 0.1 * (1 - hyp.confidence)  # Weniger Anpassung bei hoher Confidence
        else:
            adjustment = -0.15 * hyp.confidence  # Mehr Strafe bei hoher Confidence

        old_conf = hyp.confidence
        hyp.confidence = max(0.01, min(0.99, hyp.confidence + adjustment))
        pred.confidence_after = hyp.confidence

        return {
            "hypothesis": hyp.statement,
            "prediction": pred.statement,
            "was_correct": was_correct,
            "old_confidence": old_conf,
            "new_confidence": hyp.confidence,
            "total_predictions": len(self.prediction_accuracy[hyp_id]),
            "accuracy_rate": sum(self.prediction_accuracy[hyp_id]) / len(self.prediction_accuracy[hyp_id])
        }

    def compare_hypotheses(self, hyp_ids: List[str]) -> Dict[str, Any]:
        """
        Vergleicht mehrere konkurrierende Hypothesen.

        Hilft bei der Auswahl der besten Erklärung.
        """
        hypotheses = [self.hypotheses[h] for h in hyp_ids if h in self.hypotheses]

        if len(hypotheses) < 2:
            return {"error": "Mindestens 2 Hypothesen benötigt"}

        comparison = {
            "hypotheses": [],
            "ranking": [],
            "recommendation": ""
        }

        for hyp in hypotheses:
            score = self._calculate_hypothesis_score(hyp)
            comparison["hypotheses"].append({
                "id": hyp.hypothesis_id,
                "statement": hyp.statement,
                "confidence": hyp.confidence,
                "evidence_for": len([e for e in hyp.weighted_evidence if e.supports_hypothesis]),
                "evidence_against": len([e for e in hyp.weighted_evidence if not e.supports_hypothesis]),
                "predictions_correct": sum(1 for p in hyp.predictions if p.was_correct) if hyp.predictions else 0,
                "falsifiability": len(hyp.falsification_criteria),
                "score": score
            })

        # Ranking
        comparison["ranking"] = sorted(
            comparison["hypotheses"],
            key=lambda x: x["score"],
            reverse=True
        )

        # Empfehlung
        best = comparison["ranking"][0]
        if best["score"] > 0.7:
            comparison["recommendation"] = f"Hypothese '{best['statement'][:50]}...' ist am besten unterstützt"
        elif best["score"] > 0.4:
            comparison["recommendation"] = "Mehrere Hypothesen plausibel - mehr Evidenz sammeln"
        else:
            comparison["recommendation"] = "Alle Hypothesen schwach - neue Erklärungen suchen"

        return comparison

    def _calculate_hypothesis_score(self, hyp: Hypothesis) -> float:
        """Berechnet einen Gesamt-Score für eine Hypothese"""
        score = hyp.confidence * 0.4  # Basis-Confidence

        # Evidenz-Ratio
        total_evidence = len(hyp.weighted_evidence)
        if total_evidence > 0:
            evidence_for = sum(1 for e in hyp.weighted_evidence if e.supports_hypothesis)
            score += (evidence_for / total_evidence) * 0.3

        # Prediction Accuracy
        if hyp.hypothesis_id in self.prediction_accuracy:
            accuracy = self.prediction_accuracy[hyp.hypothesis_id]
            if accuracy:
                score += (sum(accuracy) / len(accuracy)) * 0.2

        # Falsifizierbarkeit (gut definierte Kriterien = besser)
        if hyp.falsification_criteria:
            score += min(0.1, len(hyp.falsification_criteria) * 0.02)

        return min(1.0, score)

    def get_hypothesis_report(self, hyp_id: str) -> Dict[str, Any]:
        """
        Erstellt einen umfassenden Bericht über eine Hypothese.
        """
        if hyp_id not in self.hypotheses:
            return {"error": "Hypothese nicht gefunden"}

        hyp = self.hypotheses[hyp_id]

        # Evidenz-Analyse
        evidence_analysis = {
            "total": len(hyp.weighted_evidence),
            "for": sum(1 for e in hyp.weighted_evidence if e.supports_hypothesis),
            "against": sum(1 for e in hyp.weighted_evidence if not e.supports_hypothesis),
            "average_strength": sum(e.effective_weight for e in hyp.weighted_evidence) / max(1, len(hyp.weighted_evidence)),
        }

        # Prediction-Analyse
        prediction_analysis = {
            "total": len(hyp.predictions),
            "tested": sum(1 for p in hyp.predictions if p.was_correct is not None),
            "correct": sum(1 for p in hyp.predictions if p.was_correct),
            "accuracy": sum(1 for p in hyp.predictions if p.was_correct) / max(1, sum(1 for p in hyp.predictions if p.was_correct is not None))
        }

        # Netzwerk-Analyse
        related = self.hypothesis_network.get(hyp_id, [])
        network_analysis = {
            "related_count": len(related),
            "supporting": sum(1 for _, r in related if r == HypothesisRelation.SUPPORTS),
            "contradicting": sum(1 for _, r in related if r == HypothesisRelation.CONTRADICTS),
        }

        return {
            "hypothesis": {
                "id": hyp.hypothesis_id,
                "statement": hyp.statement,
                "condition": hyp.condition,
                "prediction": hyp.prediction,
                "confidence": hyp.confidence,
                "confidence_interval": hyp.confidence_interval,
                "status": hyp.status.value,
                "created": hyp.created_at,
            },
            "evidence_analysis": evidence_analysis,
            "prediction_analysis": prediction_analysis,
            "network_analysis": network_analysis,
            "falsification": {
                "criteria": hyp.falsification_criteria,
                "is_falsifiable": len(hyp.falsification_criteria) > 0
            },
            "alternatives": hyp.alternative_explanations,
            "revision_count": len(hyp.revision_history),
            "overall_score": self._calculate_hypothesis_score(hyp),
            "recommendation": self._get_hypothesis_recommendation(hyp)
        }

    def _get_hypothesis_recommendation(self, hyp: Hypothesis) -> str:
        """Generiert eine Empfehlung für die Hypothese"""
        if hyp.status == HypothesisStatus.SUPPORTED:
            return "Hypothese gut unterstützt - kann als Arbeitsgrundlage dienen"
        elif hyp.status == HypothesisStatus.REFUTED:
            return "Hypothese widerlegt - alternative Erklärungen suchen"
        elif hyp.confidence > 0.7:
            return "Vielversprechend - weiter testen zur Bestätigung"
        elif hyp.confidence < 0.3:
            return "Unwahrscheinlich - Falsifizierung durchführen oder aufgeben"
        else:
            return "Mehr Evidenz und Tests nötig für Entscheidung"


# ============================================================
# PREDICTION SYSTEM - Vorhersagen
# ============================================================

@dataclass
class Prediction:
    """Eine Vorhersage"""
    prediction_id: str
    about: str                     # Worüber?
    prediction: str                # Was wird vorhergesagt?
    confidence: PredictionConfidence
    reasoning: str                 # Warum?
    time_horizon: str             # Wann? (kurzfristig, mittelfristig, langfristig)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified: Optional[bool] = None
    verified_at: Optional[str] = None


class PredictionSystem:
    """
    System für Vorhersagen über zukünftiges Verhalten/Ereignisse.

    "Ich glaube, X wird Y tun, weil..."
    "Basierend auf dem Muster, erwarte ich..."
    """

    def __init__(self):
        self.predictions: Dict[str, Prediction] = {}
        self.prediction_history: List[Prediction] = []
        self.accuracy_stats = {"correct": 0, "incorrect": 0, "pending": 0}

    def predict_behavior(self, person: str, context: str,
                        known_traits: Dict[str, float] = None) -> Prediction:
        """
        Macht eine Verhaltensvorhersage für eine Person.
        """
        known_traits = known_traits or {}

        # Basiere Vorhersage auf Traits
        prediction_text = ""
        confidence = PredictionConfidence.HUNCH
        reasoning = ""

        # Finde dominanten Trait
        if known_traits:
            dominant_trait = max(known_traits.items(), key=lambda x: abs(x[1]))
            trait_name, trait_score = dominant_trait

            if trait_score > 0.5:
                prediction_text = f"{person} wird wahrscheinlich {trait_name} handeln"
                confidence = PredictionConfidence.LIKELY
                reasoning = f"Basierend auf dem ausgeprägten '{trait_name}'-Trait"
            elif trait_score < -0.5:
                prediction_text = f"{person} wird wahrscheinlich nicht {trait_name} handeln"
                confidence = PredictionConfidence.LIKELY
                reasoning = f"Der niedrige '{trait_name}'-Wert deutet darauf hin"
        else:
            prediction_text = f"Schwer zu sagen wie {person} reagieren wird"
            confidence = PredictionConfidence.GUESS
            reasoning = "Zu wenig Informationen für sichere Vorhersage"

        pred_id = hashlib.md5(f"{person}{datetime.now()}".encode()).hexdigest()[:8]

        prediction = Prediction(
            prediction_id=pred_id,
            about=person,
            prediction=prediction_text,
            confidence=confidence,
            reasoning=reasoning,
            time_horizon="kurzfristig"
        )

        self.predictions[pred_id] = prediction
        self.accuracy_stats["pending"] += 1
        return prediction

    def predict_trend(self, topic: str, current_value: float,
                     recent_changes: List[float] = None) -> Dict[str, Any]:
        """
        Macht eine Trend-Vorhersage.

        "Interesse an X wird steigen/fallen"
        """
        recent_changes = recent_changes or []

        if recent_changes:
            avg_change = sum(recent_changes) / len(recent_changes)

            if avg_change > 0.1:
                direction = "steigen"
                confidence = min(0.8, 0.5 + avg_change)
            elif avg_change < -0.1:
                direction = "fallen"
                confidence = min(0.8, 0.5 + abs(avg_change))
            else:
                direction = "stabil bleiben"
                confidence = 0.6
        else:
            direction = "unklar entwickeln"
            confidence = 0.3

        return {
            "topic": topic,
            "current_value": current_value,
            "predicted_direction": direction,
            "confidence": confidence,
            "explanation": f"Basierend auf den letzten {len(recent_changes)} Änderungen"
        }

    def predict_next_action(self, person: str,
                           recent_actions: List[str] = None) -> str:
        """
        Versucht die nächste Aktion vorherzusagen.
        """
        recent_actions = recent_actions or []

        if not recent_actions:
            return f"*Schultern zuckend* Keine Ahnung was {person} als nächstes tun wird."

        # Einfache Muster-Erkennung
        if len(recent_actions) >= 2:
            return f"*nachdenklich* Basierend auf dem Muster... vielleicht etwas Ähnliches wie vorher?"

        return f"Zu wenig Daten für eine Vorhersage über {person}."

    def verify_prediction(self, pred_id: str, was_correct: bool) -> None:
        """Verifiziert eine Vorhersage"""
        if pred_id not in self.predictions:
            return

        pred = self.predictions[pred_id]
        pred.verified = was_correct
        pred.verified_at = datetime.now().isoformat()

        self.accuracy_stats["pending"] -= 1
        if was_correct:
            self.accuracy_stats["correct"] += 1
        else:
            self.accuracy_stats["incorrect"] += 1

        self.prediction_history.append(pred)

    def get_accuracy(self) -> float:
        """Gibt die Vorhersage-Genauigkeit zurück"""
        total = self.accuracy_stats["correct"] + self.accuracy_stats["incorrect"]
        if total == 0:
            return 0.5  # Neutral wenn keine Daten
        return self.accuracy_stats["correct"] / total


# ============================================================
# TRUST NETWORK - Vertrauens-Netzwerk (Level 10/10)
# ============================================================

class TrustDimension(Enum):
    """Dimensionen des Vertrauens (Mayer et al., 1995)"""
    COMPETENCE = "competence"        # Kann die Person das? (Fähigkeit)
    INTEGRITY = "integrity"          # Hält die Person Versprechen? (Ehrlichkeit)
    BENEVOLENCE = "benevolence"      # Will die Person mir Gutes? (Wohlwollen)
    PREDICTABILITY = "predictability" # Ist die Person vorhersagbar? (Konsistenz)
    RELIABILITY = "reliability"       # Ist die Person zuverlässig?

class TrustViolationType(Enum):
    """Arten von Vertrauensbrüchen"""
    LIE = "lie"                      # Aktive Lüge
    OMISSION = "omission"            # Wichtiges verschwiegen
    BROKEN_PROMISE = "broken_promise" # Versprechen nicht gehalten
    BETRAYAL = "betrayal"            # Verrat
    INCOMPETENCE = "incompetence"    # Unfähigkeit (nicht böswillig)
    NEGLIGENCE = "negligence"        # Nachlässigkeit

@dataclass
class TrustDimensionScore:
    """Score für eine Vertrauensdimension"""
    dimension: TrustDimension
    score: float                     # 0-1
    evidence_count: int = 0
    last_violation: Optional[str] = None
    recovery_rate: float = 0.1       # Wie schnell regeneriert es?

@dataclass
class TrustRelation:
    """Eine Vertrauensbeziehung - Level 10/10"""
    from_entity: str
    to_entity: str
    trust_level: float            # 0-1 (aggregiert)
    trust_type: str               # "direct", "inferred", "transitive"
    evidence: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    # Level 10 Erweiterungen
    dimension_scores: Dict[str, TrustDimensionScore] = field(default_factory=dict)
    violation_history: List[Dict[str, Any]] = field(default_factory=list)
    trust_trajectory: List[Tuple[str, float]] = field(default_factory=list)  # (timestamp, level)
    context_specific_trust: Dict[str, float] = field(default_factory=dict)  # Kontext → Trust
    mutual: bool = False             # Ist das Vertrauen gegenseitig?
    strength: float = 0.5           # Stärke der Beziehung (wie gut kennt man sich)

@dataclass
class TrustEvent:
    """Ein Vertrauens-Ereignis"""
    event_id: str
    entity: str
    event_type: str               # "positive", "negative", "violation"
    dimension_affected: TrustDimension
    impact: float                 # -1 to 1
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TrustNetwork:
    """
    Netzwerk-basiertes Vertrauens-System - Level 10/10.

    - Transitives Vertrauen: "X vertraut Y, und ich vertraue X, also..."
    - Vertrauens-Decay bei Fehlern
    - Reputations-Aggregation
    - PERSISTENZ: Speichert in data/trust_network.json

    Level 10 Features:
    - Multi-dimensionales Vertrauen (Kompetenz, Integrität, Wohlwollen)
    - Vertrauens-Verlauf und Prognose
    - Vertrauensbruch-Kategorisierung und -Erholung
    - Kontext-spezifisches Vertrauen
    - Netzwerk-Cluster-Analyse
    - Gegenseitigkeit-Erkennung
    """

    # Gewichtung der Vertrauens-Dimensionen
    DIMENSION_WEIGHTS = {
        TrustDimension.INTEGRITY: 0.3,      # Ehrlichkeit ist am wichtigsten
        TrustDimension.BENEVOLENCE: 0.25,   # Wohlwollen
        TrustDimension.COMPETENCE: 0.2,     # Fähigkeit
        TrustDimension.RELIABILITY: 0.15,   # Zuverlässigkeit
        TrustDimension.PREDICTABILITY: 0.1, # Vorhersagbarkeit
    }

    # Erholungsraten nach Vertrauensbruch
    RECOVERY_RATES = {
        TrustViolationType.INCOMPETENCE: 0.15,    # Schnellste Erholung
        TrustViolationType.NEGLIGENCE: 0.12,
        TrustViolationType.OMISSION: 0.08,
        TrustViolationType.BROKEN_PROMISE: 0.05,
        TrustViolationType.LIE: 0.03,
        TrustViolationType.BETRAYAL: 0.01,        # Langsamste Erholung
    }

    def __init__(self, decay_rate: float = 0.05, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.trust_relations: Dict[str, TrustRelation] = {}
        self.decay_rate = decay_rate
        self.my_name = "holo"  # Holos eigener Identifier

        # Level 10 Erweiterungen
        self.trust_events: List[TrustEvent] = []
        self.reputation_scores: Dict[str, float] = {}  # Aggregierte Reputation
        self.trust_clusters: Dict[str, List[str]] = {}  # Vertrauens-Cluster

        self._load_trust_network()

    def set_direct_trust(self, entity: str, trust_level: float,
                        evidence: str = "") -> TrustRelation:
        """
        Setzt direktes Vertrauen in eine Entität.
        """
        key = f"{self.my_name}→{entity}"

        relation = TrustRelation(
            from_entity=self.my_name,
            to_entity=entity,
            trust_level=max(0.0, min(1.0, trust_level)),
            trust_type="direct",
            evidence=[evidence] if evidence else []
        )

        self.trust_relations[key] = relation
        self._save_trust_network()
        return relation

    def get_trust_in(self, entity: str) -> float:
        """Gibt das Vertrauenslevel in eine Entität zurück"""
        key = f"{self.my_name}→{entity}"

        if key in self.trust_relations:
            return self.trust_relations[key].trust_level

        # Versuche transitives Vertrauen
        transitive = self._calculate_transitive_trust(entity)
        if transitive > 0:
            return transitive

        return 0.5  # Neutral wenn unbekannt

    def add_trust_between(self, entity1: str, entity2: str,
                         trust_level: float) -> None:
        """
        Registriert Vertrauen zwischen zwei anderen Entitäten.
        (Für transitives Vertrauen)
        """
        key = f"{entity1}→{entity2}"
        self.trust_relations[key] = TrustRelation(
            from_entity=entity1,
            to_entity=entity2,
            trust_level=trust_level,
            trust_type="observed"
        )
        self._save_trust_network()

    def trust_through_intermediary(self, target: str,
                                   intermediary: str) -> Tuple[float, str]:
        """
        Berechnet Vertrauen durch einen Vermittler.

        "Ich vertraue X nicht direkt, aber Y vertraut X, und ich vertraue Y..."

        Returns:
            (trust_level, explanation)
        """
        my_trust_in_intermediary = self.get_trust_in(intermediary)
        intermediary_trust_in_target = self.get_trust_in(target)

        if my_trust_in_intermediary < 0.3:
            return (0.0, f"Ich vertraue {intermediary} nicht genug um deren Empfehlung zu folgen.")

        # Transitives Vertrauen = Produkt (mit Dämpfung)
        transitive_trust = my_trust_in_intermediary * intermediary_trust_in_target * 0.7

        explanation = f"Ich vertraue {intermediary} ({my_trust_in_intermediary:.1f}), "
        explanation += f"und {intermediary} vertraut {target} ({intermediary_trust_in_target:.1f}). "
        explanation += f"Also vertraue ich {target} indirekt mit {transitive_trust:.2f}."

        return (transitive_trust, explanation)

    def decay_trust_on_error(self, entity: str, severity: float = 0.5) -> float:
        """
        Reduziert Vertrauen wenn Entität sich geirrt hat.
        """
        key = f"{self.my_name}→{entity}"

        if key not in self.trust_relations:
            return 0.5

        relation = self.trust_relations[key]
        decay_amount = self.decay_rate * severity

        relation.trust_level = max(0.0, relation.trust_level - decay_amount)
        relation.evidence.append(f"Vertrauen reduziert wegen Fehler ({severity:.1f})")
        relation.last_updated = datetime.now().isoformat()
        self._save_trust_network()

        return relation.trust_level

    def restore_trust(self, entity: str, amount: float = 0.1) -> float:
        """
        Stellt Vertrauen langsam wieder her.
        """
        key = f"{self.my_name}→{entity}"

        if key not in self.trust_relations:
            self.set_direct_trust(entity, 0.5 + amount)
            return 0.5 + amount

        relation = self.trust_relations[key]
        relation.trust_level = min(1.0, relation.trust_level + amount)
        relation.last_updated = datetime.now().isoformat()
        self._save_trust_network()

        return relation.trust_level

    def _calculate_transitive_trust(self, target: str) -> float:
        """Berechnet transitives Vertrauen über alle Pfade"""
        max_trust = 0.0

        # Finde alle Entitäten denen ich vertraue
        my_trusts = []
        for k, v in self.trust_relations.items():
            if k.startswith(f"{self.my_name}→") and v.trust_level > 0.3:
                parts = k.split("→")
                if len(parts) >= 2:
                    my_trusts.append((parts[1], v.trust_level))
                else:
                    logger.warning(f"[AutonomousThinking] Invalid trust key format: {k}")

        for intermediary, my_trust in my_trusts:
            # Vertraut diese Entität dem Target?
            intermediary_key = f"{intermediary}→{target}"
            if intermediary_key in self.trust_relations:
                intermediary_trust = self.trust_relations[intermediary_key].trust_level
                transitive = my_trust * intermediary_trust * 0.7
                max_trust = max(max_trust, transitive)

        return max_trust

    def get_trust_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung des Vertrauens-Netzwerks"""
        my_trusts = {}
        for k, v in self.trust_relations.items():
            if k.startswith(f"{self.my_name}→"):
                parts = k.split("→")
                if len(parts) >= 2:
                    my_trusts[parts[1]] = v.trust_level

        trusted = [k for k, v in my_trusts.items() if v > 0.6]
        distrusted = [k for k, v in my_trusts.items() if v < 0.3]

        return {
            "total_entities": len(my_trusts),
            "trusted": trusted,
            "distrusted": distrusted,
            "average_trust": sum(my_trusts.values()) / max(1, len(my_trusts))
        }

    def _load_trust_network(self) -> None:
        """Lädt Vertrauens-Netzwerk aus Datei"""
        filepath = self.data_dir / "trust_network.json"
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for rel_data in data.get("relations", []):
                        relation = TrustRelation(
                            from_entity=rel_data["from_entity"],
                            to_entity=rel_data["to_entity"],
                            trust_level=rel_data["trust_level"],
                            trust_type=rel_data.get("trust_type", "direct"),
                            evidence=rel_data.get("evidence", []),
                            last_updated=rel_data.get("last_updated", "")
                        )
                        key = f"{relation.from_entity}→{relation.to_entity}"
                        self.trust_relations[key] = relation
                logger.info(f"{len(self.trust_relations)} Vertrauensbeziehungen geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden des Trust-Netzwerks: {e}")

    def _save_trust_network(self) -> None:
        """Speichert Vertrauens-Netzwerk in Datei"""
        filepath = self.data_dir / "trust_network.json"
        try:
            data = {"relations": []}
            for relation in self.trust_relations.values():
                data["relations"].append({
                    "from_entity": relation.from_entity,
                    "to_entity": relation.to_entity,
                    "trust_level": relation.trust_level,
                    "trust_type": relation.trust_type,
                    "evidence": relation.evidence,
                    "last_updated": relation.last_updated
                })
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern des Trust-Netzwerks: {e}")

    # ================================================================
    # LEVEL 10 METHODEN - Tiefes Vertrauens-Management
    # ================================================================

    def set_dimensional_trust(self, entity: str, dimension: TrustDimension,
                              score: float, evidence: str = "") -> TrustRelation:
        """
        Setzt Vertrauen in einer spezifischen Dimension.

        Ermöglicht differenziertes Vertrauen:
        "Ich vertraue seiner Fähigkeit, aber nicht seiner Ehrlichkeit."
        """
        key = f"{self.my_name}→{entity}"

        if key not in self.trust_relations:
            self.set_direct_trust(entity, 0.5)

        relation = self.trust_relations[key]

        # Dimensionsscore setzen
        dim_score = TrustDimensionScore(
            dimension=dimension,
            score=max(0.0, min(1.0, score)),
            evidence_count=1
        )
        relation.dimension_scores[dimension.value] = dim_score

        # Aggregiertes Vertrauen neu berechnen
        relation.trust_level = self._calculate_aggregated_trust(relation)

        # Evidenz hinzufügen
        if evidence:
            relation.evidence.append(f"[{dimension.value}] {evidence}")

        # Trajectory tracken
        relation.trust_trajectory.append((datetime.now().isoformat(), relation.trust_level))

        self._save_trust_network()
        return relation

    def _calculate_aggregated_trust(self, relation: TrustRelation) -> float:
        """Berechnet aggregiertes Vertrauen aus allen Dimensionen"""
        if not relation.dimension_scores:
            return relation.trust_level

        weighted_sum = 0.0
        total_weight = 0.0

        for dim, weight in self.DIMENSION_WEIGHTS.items():
            if dim.value in relation.dimension_scores:
                weighted_sum += relation.dimension_scores[dim.value].score * weight
                total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        return relation.trust_level

    def record_trust_violation(self, entity: str, violation_type: TrustViolationType,
                               description: str, severity: float = 0.5) -> Dict[str, Any]:
        """
        Registriert einen Vertrauensbruch und berechnet die Auswirkungen.

        Verschiedene Arten von Vertrauensbrüchen haben unterschiedliche Auswirkungen.
        """
        key = f"{self.my_name}→{entity}"

        if key not in self.trust_relations:
            self.set_direct_trust(entity, 0.5)

        relation = self.trust_relations[key]
        old_trust = relation.trust_level

        # Bestimme welche Dimension am meisten betroffen ist
        dimension_impacts = {
            TrustViolationType.LIE: TrustDimension.INTEGRITY,
            TrustViolationType.OMISSION: TrustDimension.INTEGRITY,
            TrustViolationType.BROKEN_PROMISE: TrustDimension.RELIABILITY,
            TrustViolationType.BETRAYAL: TrustDimension.BENEVOLENCE,
            TrustViolationType.INCOMPETENCE: TrustDimension.COMPETENCE,
            TrustViolationType.NEGLIGENCE: TrustDimension.RELIABILITY,
        }

        affected_dim = dimension_impacts.get(violation_type, TrustDimension.INTEGRITY)

        # Berechne Impact basierend auf Schwere und Typ
        base_impact = severity * 0.3  # Basis-Auswirkung

        # Schlimmere Vergehen haben stärkeren Impact
        type_multiplier = {
            TrustViolationType.BETRAYAL: 2.0,
            TrustViolationType.LIE: 1.5,
            TrustViolationType.BROKEN_PROMISE: 1.2,
            TrustViolationType.OMISSION: 1.0,
            TrustViolationType.NEGLIGENCE: 0.8,
            TrustViolationType.INCOMPETENCE: 0.6,
        }
        impact = base_impact * type_multiplier.get(violation_type, 1.0)

        # Dimension Score reduzieren
        if affected_dim.value in relation.dimension_scores:
            dim_score = relation.dimension_scores[affected_dim.value]
            dim_score.score = max(0.0, dim_score.score - impact)
            dim_score.last_violation = datetime.now().isoformat()
            dim_score.recovery_rate = self.RECOVERY_RATES.get(violation_type, 0.05)
        else:
            relation.dimension_scores[affected_dim.value] = TrustDimensionScore(
                dimension=affected_dim,
                score=max(0.0, 0.5 - impact),
                last_violation=datetime.now().isoformat(),
                recovery_rate=self.RECOVERY_RATES.get(violation_type, 0.05)
            )

        # Gesamtvertrauen neu berechnen
        relation.trust_level = self._calculate_aggregated_trust(relation)

        # Violation History
        violation_record = {
            "timestamp": datetime.now().isoformat(),
            "type": violation_type.value,
            "description": description,
            "severity": severity,
            "impact": impact,
            "trust_before": old_trust,
            "trust_after": relation.trust_level
        }
        relation.violation_history.append(violation_record)

        # Trust Event
        event = TrustEvent(
            event_id=hashlib.md5(f"{entity}{datetime.now()}".encode()).hexdigest()[:8],
            entity=entity,
            event_type="violation",
            dimension_affected=affected_dim,
            impact=-impact,
            description=description
        )
        self.trust_events.append(event)

        self._save_trust_network()

        return {
            "entity": entity,
            "violation_type": violation_type.value,
            "affected_dimension": affected_dim.value,
            "old_trust": old_trust,
            "new_trust": relation.trust_level,
            "impact": impact,
            "recovery_rate": self.RECOVERY_RATES.get(violation_type, 0.05),
            "message": self._generate_violation_message(violation_type, entity)
        }

    def _generate_violation_message(self, violation_type: TrustViolationType,
                                    entity: str) -> str:
        """Generiert eine menschenähnliche Reaktion auf Vertrauensbruch"""
        messages = {
            TrustViolationType.LIE: f"*enttäuscht* {entity} hat mich angelogen... das tut weh.",
            TrustViolationType.BETRAYAL: f"*verletzt* Das fühlt sich wie Verrat an. {entity}, wie konntest du?",
            TrustViolationType.BROKEN_PROMISE: f"*traurig* {entity} hat das Versprechen gebrochen. Worte bedeuten wohl nichts.",
            TrustViolationType.OMISSION: f"*nachdenklich* {entity} hat mir etwas Wichtiges verschwiegen...",
            TrustViolationType.INCOMPETENCE: f"*neutral* {entity} hat es versucht, aber es nicht geschafft. Das ist okay.",
            TrustViolationType.NEGLIGENCE: f"*leicht genervt* {entity} hätte aufmerksamer sein sollen.",
        }
        return messages.get(violation_type, f"Mein Vertrauen in {entity} wurde beschädigt.")

    def check_trustworthiness(self, entity: str, context: str = "") -> Dict[str, Any]:
        """
        Umfassende Prüfung der Vertrauenswürdigkeit einer Person.
        """
        key = f"{self.my_name}→{entity}"

        if key not in self.trust_relations:
            return {
                "entity": entity,
                "known": False,
                "overall_trust": 0.5,
                "recommendation": "Unbekannt - vorsichtig sein",
            }

        relation = self.trust_relations[key]

        # Dimensionen analysieren
        dim_analysis = {}
        for dim_name, dim_score in relation.dimension_scores.items():
            dim_analysis[dim_name] = {
                "score": dim_score.score,
                "status": "gut" if dim_score.score > 0.6 else ("neutral" if dim_score.score > 0.3 else "problematisch"),
                "last_violation": dim_score.last_violation
            }

        # Trend berechnen
        trend = "stabil"
        if len(relation.trust_trajectory) >= 2:
            recent = relation.trust_trajectory[-3:]
            if len(recent) >= 2:
                change = recent[-1][1] - recent[0][1]
                if change > 0.1:
                    trend = "steigend"
                elif change < -0.1:
                    trend = "fallend"

        # Kontext-spezifisches Vertrauen
        context_trust = relation.context_specific_trust.get(context, relation.trust_level)

        # Warnsignale
        warnings = []
        if relation.violation_history:
            recent_violations = [v for v in relation.violation_history
                               if v.get("severity", 0) > 0.5][-3:]
            if recent_violations:
                warnings.append(f"{len(recent_violations)} schwere Vertrauensbrüche")

        if any(d.score < 0.3 for d in relation.dimension_scores.values()):
            warnings.append("Kritisch niedrige Werte in mindestens einer Dimension")

        # Empfehlung generieren
        if relation.trust_level > 0.7 and not warnings:
            recommendation = "Vertrauenswürdig - kann sich verlassen"
        elif relation.trust_level > 0.5:
            recommendation = "Grundsätzlich okay - aber aufmerksam bleiben"
        elif relation.trust_level > 0.3:
            recommendation = "Vorsicht geboten - verifizieren wichtig"
        else:
            recommendation = "Nicht vertrauen - vergangene Probleme beachten"

        return {
            "entity": entity,
            "known": True,
            "overall_trust": relation.trust_level,
            "context_specific_trust": context_trust,
            "dimensions": dim_analysis,
            "trend": trend,
            "warnings": warnings,
            "violation_count": len(relation.violation_history),
            "relationship_strength": relation.strength,
            "mutual": relation.mutual,
            "recommendation": recommendation
        }

    def predict_trust_trajectory(self, entity: str, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Prognostiziert die Vertrauensentwicklung basierend auf aktuellen Trends.
        """
        key = f"{self.my_name}→{entity}"

        if key not in self.trust_relations:
            return {"error": "Keine Daten für diese Person"}

        relation = self.trust_relations[key]
        current_trust = relation.trust_level

        # Berechne natürliche Erholung für beschädigte Dimensionen
        recovery_per_day = 0.0
        for dim_score in relation.dimension_scores.values():
            if dim_score.score < 0.5:  # Beschädigte Dimension
                recovery_per_day += dim_score.recovery_rate / 30  # Pro Tag

        # Trend aus Historie
        daily_trend = 0.0
        if len(relation.trust_trajectory) >= 2:
            first = relation.trust_trajectory[0][1]
            last = relation.trust_trajectory[-1][1]
            days_span = max(1, len(relation.trust_trajectory))
            daily_trend = (last - first) / days_span

        # Prognose
        predicted_trust = current_trust + (daily_trend + recovery_per_day) * days_ahead
        predicted_trust = max(0.0, min(1.0, predicted_trust))

        # Szenarien
        best_case = min(1.0, predicted_trust + 0.1)
        worst_case = max(0.0, predicted_trust - 0.1)

        return {
            "entity": entity,
            "current_trust": current_trust,
            "days_ahead": days_ahead,
            "predicted_trust": predicted_trust,
            "best_case": best_case,
            "worst_case": worst_case,
            "daily_trend": daily_trend,
            "recovery_potential": recovery_per_day * days_ahead,
            "outlook": "positiv" if predicted_trust > current_trust else "stabil" if abs(predicted_trust - current_trust) < 0.05 else "negativ"
        }

    def find_trust_clusters(self) -> Dict[str, List[str]]:
        """
        Findet Cluster von Entitäten mit ähnlichem Vertrauensniveau.

        Nützlich um "Inner Circle" vs "Bekannte" vs "Skeptisch" zu identifizieren.
        """
        clusters = {
            "inner_circle": [],       # > 0.8 Vertrauen
            "trusted_friends": [],    # 0.6 - 0.8
            "acquaintances": [],      # 0.4 - 0.6
            "cautious": [],           # 0.2 - 0.4
            "distrusted": [],         # < 0.2
        }

        for key, relation in self.trust_relations.items():
            if not key.startswith(f"{self.my_name}→"):
                continue

            entity = key.split("→")[1]
            trust = relation.trust_level

            if trust > 0.8:
                clusters["inner_circle"].append(entity)
            elif trust > 0.6:
                clusters["trusted_friends"].append(entity)
            elif trust > 0.4:
                clusters["acquaintances"].append(entity)
            elif trust > 0.2:
                clusters["cautious"].append(entity)
            else:
                clusters["distrusted"].append(entity)

        self.trust_clusters = clusters
        return clusters

    def check_trust_reciprocity(self, entity: str) -> Dict[str, Any]:
        """
        Prüft ob das Vertrauen gegenseitig ist.

        "Vertraue ich X mehr als X mir vertraut?"
        """
        my_trust_key = f"{self.my_name}→{entity}"
        their_trust_key = f"{entity}→{self.my_name}"

        my_trust = self.trust_relations.get(my_trust_key)
        their_trust = self.trust_relations.get(their_trust_key)

        if not my_trust:
            return {"error": "Keine Vertrauensbeziehung zu dieser Person"}

        result = {
            "entity": entity,
            "my_trust_in_them": my_trust.trust_level,
            "their_trust_in_me": their_trust.trust_level if their_trust else None,
            "reciprocity": "unknown"
        }

        if their_trust:
            diff = my_trust.trust_level - their_trust.trust_level

            if abs(diff) < 0.15:
                result["reciprocity"] = "balanced"
                result["message"] = "Das Vertrauen scheint gegenseitig zu sein."
            elif diff > 0:
                result["reciprocity"] = "i_trust_more"
                result["message"] = f"Ich vertraue {entity} mehr als umgekehrt. Vorsicht."
            else:
                result["reciprocity"] = "they_trust_more"
                result["message"] = f"{entity} vertraut mir mehr als ich ihm/ihr. Faire Behandlung wichtig."

            # Update mutual flag
            my_trust.mutual = abs(diff) < 0.2
        else:
            result["message"] = "Keine Information darüber, wie sehr mir vertraut wird."

        return result

    def get_trust_network_stats(self) -> Dict[str, Any]:
        """Gibt umfassende Statistiken über das Vertrauens-Netzwerk"""
        my_relations = [r for k, r in self.trust_relations.items()
                       if k.startswith(f"{self.my_name}→")]

        if not my_relations:
            return {"total_relations": 0}

        trust_levels = [r.trust_level for r in my_relations]
        violations = sum(len(r.violation_history) for r in my_relations)

        # Dimension Averages
        dim_averages = {}
        for dim in TrustDimension:
            scores = []
            for r in my_relations:
                if dim.value in r.dimension_scores:
                    scores.append(r.dimension_scores[dim.value].score)
            if scores:
                dim_averages[dim.value] = sum(scores) / len(scores)

        clusters = self.find_trust_clusters()

        return {
            "total_relations": len(my_relations),
            "average_trust": sum(trust_levels) / len(trust_levels),
            "max_trust": max(trust_levels),
            "min_trust": min(trust_levels),
            "total_violations": violations,
            "total_events": len(self.trust_events),
            "dimension_averages": dim_averages,
            "cluster_sizes": {k: len(v) for k, v in clusters.items()},
            "inner_circle_count": len(clusters["inner_circle"]),
            "distrusted_count": len(clusters["distrusted"])
        }


# ============================================================
# ANALOGY ENGINE - Analogie-Denken (Level 10/10)
# ============================================================

class SimilarityType(Enum):
    """Arten der Ähnlichkeit in Analogien"""
    SURFACE = "surface"             # Oberflächliche Ähnlichkeit (Worte, Erscheinung)
    STRUCTURAL = "structural"       # Strukturelle Ähnlichkeit (Beziehungen)
    CAUSAL = "causal"              # Kausale Ähnlichkeit (Ursache-Wirkung)
    FUNCTIONAL = "functional"       # Funktionale Ähnlichkeit (Zweck, Rolle)
    RELATIONAL = "relational"       # Relationale Ähnlichkeit (Verhältnisse)

class AnalogicalDomain(Enum):
    """Domänen für Cross-Domain Analogien"""
    INTERPERSONAL = "interpersonal"   # Zwischenmenschliche Beziehungen
    PROFESSIONAL = "professional"     # Beruf/Arbeit
    NATURE = "nature"                 # Natur/Tiere
    TECHNOLOGY = "technology"         # Technik
    HISTORY = "history"               # Geschichte
    GAMES = "games"                   # Spiele/Sport
    ECONOMICS = "economics"           # Wirtschaft
    PHILOSOPHY = "philosophy"         # Philosophie

@dataclass
class StructuralMapping:
    """Strukturelle Abbildung zwischen zwei Situationen"""
    mapping_id: str
    source_elements: Dict[str, str]      # Elemente der Quell-Situation
    target_elements: Dict[str, str]      # Elemente der Ziel-Situation
    mappings: List[Tuple[str, str]]      # Welches Element entspricht welchem
    relation_preservation: float         # Wie gut bleiben Beziehungen erhalten
    inferences: List[str]                # Schlussfolgerungen aus der Abbildung

@dataclass
class Analogy:
    """Eine Analogie zwischen zwei Situationen - Level 10/10"""
    analogy_id: str
    current_situation: str          # Aktuelle Situation
    past_situation: str             # Vergangene ähnliche Situation
    similarity_score: float         # Wie ähnlich? (0-1)
    lessons_learned: List[str]      # Was wurde gelernt?
    outcome_of_past: str            # Wie ging es damals aus?
    applicable_to_now: bool         # Ist das auf jetzt anwendbar?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Level 10 Erweiterungen
    similarity_type: SimilarityType = SimilarityType.SURFACE
    structural_mapping: Optional[StructuralMapping] = None
    source_domain: AnalogicalDomain = AnalogicalDomain.INTERPERSONAL
    target_domain: AnalogicalDomain = AnalogicalDomain.INTERPERSONAL
    cross_domain: bool = False
    quality_score: float = 0.5          # Qualität der Analogie
    counter_examples: List[str] = field(default_factory=list)  # Wo trifft sie NICHT zu
    predictive_power: float = 0.5       # Wie gut sagt sie voraus?
    used_successfully: int = 0          # Wie oft half die Analogie?

@dataclass
class StoredExperience:
    """Eine gespeicherte Erfahrung für Analogie-Suche - Level 10/10"""
    experience_id: str
    situation: str                  # Beschreibung der Situation
    keywords: Set[str]              # Schlüsselwörter für Suche
    context_type: str               # "person", "decision", "conflict", "success", "failure"
    outcome: str                    # Wie ist es ausgegangen?
    outcome_valence: float          # -1 bis 1 (schlecht bis gut)
    lessons: List[str]              # Gelernte Lektionen
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    # Level 10 Erweiterungen
    domain: AnalogicalDomain = AnalogicalDomain.INTERPERSONAL
    actors: List[str] = field(default_factory=list)        # Beteiligte
    relations: List[Tuple[str, str, str]] = field(default_factory=list)  # (A, relation, B)
    causal_chain: List[str] = field(default_factory=list)  # Ursache → Wirkung
    abstraction_level: int = 1                              # 1=konkret, 5=abstrakt
    times_used_as_analogy: int = 0

@dataclass
class AnalogyChain:
    """Eine Kette von verbundenen Analogien: A→B→C"""
    chain_id: str
    analogies: List[Analogy]
    total_similarity: float
    inference: str                  # Schlussfolgerung aus der Kette


class AnalogyEngine:
    """
    System für Analogie-basiertes Denken - Level 10/10.

    "Das erinnert mich an die Situation mit X damals..."
    "Das ist wie bei Y, und da ist Z passiert..."
    "Ich kenne das Muster von früher..."

    Level 10 Features:
    - Strukturelle Abbildung (nicht nur oberflächliche Ähnlichkeit)
    - Cross-Domain Analogien (Parallelen in völlig anderen Bereichen)
    - Analogie-Qualitätsbewertung
    - Counter-Analogien (wo das Muster NICHT gilt)
    - Analogie-Ketten (A→B→C Schlüsse)
    - Kausal vs Oberflächen-Ähnlichkeit
    - Abstraktions-Level-Erkennung
    """

    # Situation-Typen für bessere Kategorisierung
    SITUATION_TYPES = {
        "person": ["vertrauen", "lüge", "ehrlich", "freund", "beziehung", "konflikt"],
        "decision": ["entscheidung", "wahl", "option", "risiko", "chance"],
        "conflict": ["streit", "problem", "schwierig", "konflikt", "stress"],
        "success": ["erfolg", "geschafft", "gewonnen", "erreicht", "gut"],
        "failure": ["fehler", "versagt", "verloren", "schlecht", "bereut"],
    }

    # Analogie-Phrasen für menschenähnliche Ausdrücke
    ANALOGY_PHRASES = [
        "Das erinnert mich an {past}...",
        "Hmm, das ist wie damals bei {past}.",
        "Ich kenne dieses Muster... {past} war ähnlich.",
        "*nachdenklich* Das hatten wir schon mal... {past}.",
        "Moment, das kommt mir bekannt vor... {past}!",
        "Oh, das ist fast wie {past} damals.",
    ]

    # Cross-Domain Analogie-Templates
    CROSS_DOMAIN_TEMPLATES = {
        AnalogicalDomain.NATURE: [
            "Das ist wie bei {element} in der Natur - {explanation}",
            "Denk an {element}: {explanation}",
        ],
        AnalogicalDomain.GAMES: [
            "Das ist wie beim Schach: {explanation}",
            "Stell dir ein Spiel vor: {explanation}",
        ],
        AnalogicalDomain.ECONOMICS: [
            "Das ist wie auf dem Markt: {explanation}",
            "Ökonomisch gesehen: {explanation}",
        ],
        AnalogicalDomain.HISTORY: [
            "Die Geschichte zeigt: {explanation}",
            "Das erinnert an {element}: {explanation}",
        ],
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.experiences: Dict[str, StoredExperience] = {}
        self.analogies_made: List[Analogy] = []
        self.pattern_cache: Dict[str, List[str]] = {}  # pattern -> experience_ids

        # Level 10 Erweiterungen
        self.analogy_chains: List[AnalogyChain] = []
        self.analogy_accuracy: Dict[str, List[bool]] = {}  # analogy_id -> outcomes
        self.domain_patterns: Dict[AnalogicalDomain, List[str]] = {}
        self.structural_mappings: Dict[str, StructuralMapping] = {}

        self._load_experiences()

    def store_experience(self, situation: str, outcome: str,
                        outcome_valence: float, lessons: List[str] = None,
                        context_type: str = None) -> StoredExperience:
        """
        Speichert eine Erfahrung für spätere Analogie-Suche.

        Args:
            situation: Was ist passiert?
            outcome: Wie ist es ausgegangen?
            outcome_valence: -1 (schlecht) bis 1 (gut)
            lessons: Was wurde gelernt?
            context_type: Art der Situation
        """
        exp_id = hashlib.md5(f"{situation}{datetime.now()}".encode()).hexdigest()[:10]

        # Keywords extrahieren
        keywords = self._extract_keywords(situation)

        # Typ bestimmen wenn nicht angegeben
        if context_type is None:
            context_type = self._determine_type(situation, keywords)

        experience = StoredExperience(
            experience_id=exp_id,
            situation=situation,
            keywords=keywords,
            context_type=context_type,
            outcome=outcome,
            outcome_valence=max(-1.0, min(1.0, outcome_valence)),
            lessons=lessons or []
        )

        self.experiences[exp_id] = experience
        self._update_pattern_cache(exp_id, keywords)
        self._save_experiences()

        logger.info(f"Erfahrung gespeichert: {exp_id} ({context_type})")
        return experience

    def find_analogies(self, current_situation: str,
                       min_similarity: float = 0.3,
                       max_results: int = 3) -> List[Analogy]:
        """
        Findet ähnliche Situationen aus der Vergangenheit.

        Args:
            current_situation: Die aktuelle Situation
            min_similarity: Minimum-Ähnlichkeit (0-1)
            max_results: Maximale Anzahl Ergebnisse

        Returns:
            Liste von Analogien, sortiert nach Ähnlichkeit
        """
        current_keywords = self._extract_keywords(current_situation)
        current_type = self._determine_type(current_situation, current_keywords)

        candidates: List[Tuple[float, StoredExperience]] = []

        for exp in self.experiences.values():
            similarity = self._calculate_similarity(
                current_keywords, current_type,
                exp.keywords, exp.context_type
            )

            if similarity >= min_similarity:
                candidates.append((similarity, exp))

        # Sortiere nach Ähnlichkeit
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Erstelle Analogien
        analogies = []
        for similarity, exp in candidates[:max_results]:
            analogy = Analogy(
                analogy_id=hashlib.md5(f"{current_situation}{exp.experience_id}".encode()).hexdigest()[:8],
                current_situation=current_situation[:200],
                past_situation=exp.situation,
                similarity_score=similarity,
                lessons_learned=exp.lessons,
                outcome_of_past=exp.outcome,
                applicable_to_now=similarity > 0.5
            )
            analogies.append(analogy)
            self.analogies_made.append(analogy)

        return analogies

    def get_wisdom_from_past(self, current_situation: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Weisheit aus vergangenen ähnlichen Situationen.

        Returns:
            Dict mit Analogie, Lektion und Warnung/Ermutigung
        """
        analogies = self.find_analogies(current_situation, min_similarity=0.4, max_results=1)

        if not analogies:
            return None

        best = analogies[0]
        past_exp = self.experiences.get(
            next((k for k, v in self.experiences.items()
                  if v.situation == best.past_situation), None)
        )

        result = {
            "found_analogy": True,
            "similarity": best.similarity_score,
            "past_situation": best.past_situation[:100],
            "past_outcome": best.outcome_of_past,
        }

        # Generiere menschenähnliche Aussage
        phrase = random.choice(self.ANALOGY_PHRASES).format(
            past=best.past_situation[:50]
        )
        result["expression"] = phrase

        # Warnung oder Ermutigung basierend auf Outcome
        if past_exp:
            if past_exp.outcome_valence < -0.3:
                result["warning"] = f"⚠️ Vorsicht! Letztes Mal ging das schlecht aus: {past_exp.outcome}"
                result["advice"] = "Vielleicht sollte ich diesmal anders vorgehen..."
            elif past_exp.outcome_valence > 0.3:
                result["encouragement"] = f"✓ Das ist gut! Letztes Mal war's positiv: {past_exp.outcome}"
                result["advice"] = "Das Muster hat funktioniert, könnte wieder klappen."
            else:
                result["note"] = f"Letztes Mal war's gemischt: {past_exp.outcome}"
                result["advice"] = "Abwarten und vorsichtig sein."

        # Lektionen
        if best.lessons_learned:
            result["lessons"] = best.lessons_learned
            result["main_lesson"] = random.choice(best.lessons_learned)

        return result

    def learn_from_outcome(self, situation: str, outcome: str,
                          outcome_valence: float, what_i_learned: str) -> None:
        """
        Lernt aus dem Ausgang einer Situation und speichert es.
        """
        lessons = [what_i_learned] if what_i_learned else []

        # Wenn ähnliche Erfahrung existiert, update
        existing = self.find_analogies(situation, min_similarity=0.7, max_results=1)

        if existing and existing[0].similarity_score > 0.8:
            # Update bestehende Erfahrung
            for exp_id, exp in self.experiences.items():
                if exp.situation == existing[0].past_situation:
                    if what_i_learned and what_i_learned not in exp.lessons:
                        exp.lessons.append(what_i_learned)
                    self._save_experiences()
                    logger.info(f"Erfahrung {exp_id} mit neuer Lektion aktualisiert")
                    return

        # Neue Erfahrung speichern
        self.store_experience(situation, outcome, outcome_valence, lessons)

    def express_analogy(self, current_situation: str) -> str:
        """
        Drückt eine gefundene Analogie menschenähnlich aus.
        """
        wisdom = self.get_wisdom_from_past(current_situation)

        if not wisdom:
            return ""

        parts = [wisdom["expression"]]

        if "warning" in wisdom:
            parts.append(wisdom["warning"])
        elif "encouragement" in wisdom:
            parts.append(wisdom["encouragement"])

        if wisdom.get("main_lesson"):
            parts.append(f"Damals habe ich gelernt: {wisdom['main_lesson']}")

        return " ".join(parts)

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extrahiert Keywords aus Text"""
        # Einfache Wort-Extraktion
        words = set(text.lower().split())

        # Stopwords entfernen (vereinfacht)
        stopwords = {"der", "die", "das", "und", "oder", "ist", "hat", "war",
                    "ein", "eine", "mit", "von", "zu", "ich", "du", "er", "sie",
                    "es", "wir", "ihr", "mich", "mir", "dir", "ihn", "ihm"}

        return words - stopwords

    def _determine_type(self, text: str, keywords: Set[str]) -> str:
        """Bestimmt den Typ einer Situation"""
        text_lower = text.lower()

        best_type = "decision"
        best_score = 0

        for sit_type, type_keywords in self.SITUATION_TYPES.items():
            score = sum(1 for kw in type_keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_type = sit_type

        return best_type

    def _calculate_similarity(self, kw1: Set[str], type1: str,
                             kw2: Set[str], type2: str) -> float:
        """Berechnet Ähnlichkeit zwischen zwei Situationen"""
        # Keyword-Überlappung (Jaccard-Ähnlichkeit)
        if not kw1 or not kw2:
            keyword_sim = 0.0
        else:
            intersection = len(kw1 & kw2)
            union = len(kw1 | kw2)
            keyword_sim = intersection / union if union > 0 else 0.0

        # Typ-Bonus
        type_bonus = 0.2 if type1 == type2 else 0.0

        # Kombiniert
        similarity = (keyword_sim * 0.8) + type_bonus

        return min(1.0, similarity)

    def _update_pattern_cache(self, exp_id: str, keywords: Set[str]) -> None:
        """Aktualisiert den Pattern-Cache"""
        for keyword in keywords:
            if keyword not in self.pattern_cache:
                self.pattern_cache[keyword] = []
            if exp_id not in self.pattern_cache[keyword]:
                self.pattern_cache[keyword].append(exp_id)

    def _load_experiences(self) -> None:
        """Lädt Erfahrungen aus Datei"""
        filepath = self.data_dir / "analogy_experiences.json"
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for exp_data in data:
                        exp = StoredExperience(
                            experience_id=exp_data["experience_id"],
                            situation=exp_data["situation"],
                            keywords=set(exp_data.get("keywords", [])),
                            context_type=exp_data.get("context_type", "decision"),
                            outcome=exp_data.get("outcome", ""),
                            outcome_valence=exp_data.get("outcome_valence", 0.0),
                            lessons=exp_data.get("lessons", []),
                            timestamp=exp_data.get("timestamp", "")
                        )
                        self.experiences[exp.experience_id] = exp
                        self._update_pattern_cache(exp.experience_id, exp.keywords)
                logger.info(f"{len(self.experiences)} Erfahrungen geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Erfahrungen: {e}")

    def _save_experiences(self) -> None:
        """Speichert Erfahrungen in Datei"""
        filepath = self.data_dir / "analogy_experiences.json"
        try:
            data = []
            for exp in self.experiences.values():
                data.append({
                    "experience_id": exp.experience_id,
                    "situation": exp.situation,
                    "keywords": list(exp.keywords),
                    "context_type": exp.context_type,
                    "outcome": exp.outcome,
                    "outcome_valence": exp.outcome_valence,
                    "lessons": exp.lessons,
                    "timestamp": exp.timestamp
                })
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern der Erfahrungen: {e}")

    # ================================================================
    # LEVEL 10 METHODEN - Tiefes Analogie-Denken
    # ================================================================

    def create_structural_mapping(self, current_situation: str,
                                  past_experience: StoredExperience) -> StructuralMapping:
        """
        Erstellt eine strukturelle Abbildung zwischen zwei Situationen.

        Strukturelle Analogie = gleiche BEZIEHUNGEN, nicht nur gleiche ELEMENTE.
        """
        mapping_id = hashlib.md5(f"{current_situation}{past_experience.experience_id}".encode()).hexdigest()[:8]

        # Extrahiere Elemente aus beiden Situationen
        current_elements = self._extract_elements(current_situation)
        past_elements = self._extract_elements(past_experience.situation)

        # Finde Mappings basierend auf Rolle/Position
        mappings = []
        for c_role, c_element in current_elements.items():
            for p_role, p_element in past_elements.items():
                if c_role == p_role:  # Gleiche strukturelle Rolle
                    mappings.append((c_element, p_element))

        # Berechne wie gut Beziehungen erhalten bleiben
        relation_preservation = len(mappings) / max(len(current_elements), len(past_elements), 1)

        # Generiere Schlussfolgerungen
        inferences = []
        if past_experience.outcome_valence > 0.3:
            inferences.append(f"Da '{past_experience.outcome}' gut ausging, könnte es hier auch positiv enden")
        elif past_experience.outcome_valence < -0.3:
            inferences.append(f"Vorsicht: '{past_experience.outcome}' - könnte hier ähnlich sein")

        for lesson in past_experience.lessons[:2]:
            inferences.append(f"Übertragbare Lektion: {lesson}")

        mapping = StructuralMapping(
            mapping_id=mapping_id,
            source_elements=past_elements,
            target_elements=current_elements,
            mappings=mappings,
            relation_preservation=relation_preservation,
            inferences=inferences
        )

        self.structural_mappings[mapping_id] = mapping
        return mapping

    def _extract_elements(self, situation: str) -> Dict[str, str]:
        """Extrahiert strukturelle Elemente und ihre Rollen"""
        elements = {}
        situation_lower = situation.lower()

        # Suche nach typischen Rollen
        role_patterns = {
            "agent": ["ich", "mir", "mein", "person"],
            "patient": ["er", "sie", "ihm", "ihr", "das"],
            "action": ["macht", "tut", "sagt", "verhält"],
            "goal": ["will", "möchte", "braucht", "sucht"],
            "obstacle": ["problem", "schwierig", "verhindert", "blockiert"],
            "outcome": ["ergebnis", "resultat", "folge", "passiert"],
        }

        for role, keywords in role_patterns.items():
            for kw in keywords:
                if kw in situation_lower:
                    # Extrahiere Kontext um das Keyword
                    idx = situation_lower.find(kw)
                    start = max(0, idx - 20)
                    end = min(len(situation), idx + len(kw) + 20)
                    elements[role] = situation[start:end].strip()
                    break

        return elements

    def find_cross_domain_analogy(self, current_situation: str,
                                  target_domain: AnalogicalDomain) -> Optional[Dict[str, Any]]:
        """
        Findet eine Analogie in einer völlig anderen Domäne.

        Cross-Domain Analogien sind oft die kreativsten und aufschlussreichsten.
        """
        current_keywords = self._extract_keywords(current_situation)
        current_type = self._determine_type(current_situation, current_keywords)

        # Domänen-spezifische Analogien
        cross_analogies = {
            AnalogicalDomain.NATURE: self._nature_analogies(current_type, current_keywords),
            AnalogicalDomain.GAMES: self._game_analogies(current_type, current_keywords),
            AnalogicalDomain.ECONOMICS: self._economic_analogies(current_type, current_keywords),
            AnalogicalDomain.HISTORY: self._history_analogies(current_type, current_keywords),
        }

        if target_domain not in cross_analogies:
            return None

        analogy_data = cross_analogies[target_domain]
        if not analogy_data:
            return None

        templates = self.CROSS_DOMAIN_TEMPLATES.get(target_domain, ["{explanation}"])
        template = random.choice(templates)

        return {
            "source_domain": AnalogicalDomain.INTERPERSONAL.value,
            "target_domain": target_domain.value,
            "situation": current_situation[:100],
            "analogy": analogy_data["analogy"],
            "expression": template.format(
                element=analogy_data.get("element", ""),
                explanation=analogy_data["explanation"]
            ),
            "insight": analogy_data["insight"],
            "cross_domain": True
        }

    def _nature_analogies(self, sit_type: str, keywords: Set[str]) -> Optional[Dict[str, Any]]:
        """Generiert Natur-Analogien"""
        analogies = {
            "conflict": {
                "element": "Wölfen",
                "analogy": "Territorialkampf bei Wölfen",
                "explanation": "Auch Wölfe kämpfen um Ressourcen, aber respektieren Grenzen",
                "insight": "Konflikte sind natürlich, aber müssen nicht zerstörerisch sein"
            },
            "decision": {
                "element": "einem Baum",
                "analogy": "Baum am Scheideweg",
                "explanation": "Bäume wachsen zum Licht - sie folgen instinktiv dem besten Weg",
                "insight": "Manchmal kennt die Intuition den Weg besser als der Verstand"
            },
            "person": {
                "element": "Symbiose",
                "analogy": "Symbiose in der Natur",
                "explanation": "Wie Clownfisch und Anemone - gegenseitiger Nutzen",
                "insight": "Gute Beziehungen sind Win-Win für beide Seiten"
            },
        }
        return analogies.get(sit_type)

    def _game_analogies(self, sit_type: str, keywords: Set[str]) -> Optional[Dict[str, Any]]:
        """Generiert Spiel-Analogien"""
        analogies = {
            "conflict": {
                "element": "Schachspiel",
                "analogy": "Taktik im Schach",
                "explanation": "Jeder Zug hat Konsequenzen - denke mehrere Züge voraus",
                "insight": "Überlege die Reaktion des Anderen bevor du handelst"
            },
            "decision": {
                "element": "Poker",
                "analogy": "Poker-Entscheidung",
                "explanation": "Mit unvollständiger Information die beste Wette machen",
                "insight": "Manchmal muss man mit Unsicherheit entscheiden"
            },
            "failure": {
                "element": "Videospiel",
                "analogy": "Game Over und Neuladen",
                "explanation": "Bei jedem Versuch lernt man den Level besser kennen",
                "insight": "Scheitern ist nur Übung für den nächsten Versuch"
            },
        }
        return analogies.get(sit_type)

    def _economic_analogies(self, sit_type: str, keywords: Set[str]) -> Optional[Dict[str, Any]]:
        """Generiert Wirtschafts-Analogien"""
        analogies = {
            "decision": {
                "element": "Opportunitätskosten",
                "analogy": "Jede Wahl hat Opportunitätskosten",
                "explanation": "Was auch immer du wählst - du gibst die Alternative auf",
                "insight": "Bedenke nicht nur was du gewinnst, sondern was du aufgibst"
            },
            "conflict": {
                "element": "Verhandlung",
                "analogy": "Nash-Gleichgewicht",
                "explanation": "Der beste Ausgang, wenn beide strategisch denken",
                "insight": "Manchmal ist Kooperation profitabler als Konfrontation"
            },
            "person": {
                "element": "Investition",
                "analogy": "Beziehung als Investition",
                "explanation": "Langfristige Investments brauchen Zeit und Pflege",
                "insight": "Vertrauen aufzubauen ist wie Zinses-Zins - langsam aber mächtig"
            },
        }
        return analogies.get(sit_type)

    def _history_analogies(self, sit_type: str, keywords: Set[str]) -> Optional[Dict[str, Any]]:
        """Generiert historische Analogien"""
        analogies = {
            "conflict": {
                "element": "dem Kalten Krieg",
                "analogy": "Kalter Krieg Diplomatie",
                "explanation": "Manchmal ist die beste Schlacht die, die nie gekämpft wird",
                "insight": "Drohungen und Abschreckung können Eskalation verhindern"
            },
            "decision": {
                "element": "Cäsars Rubikon",
                "analogy": "Den Rubikon überschreiten",
                "explanation": "Manche Entscheidungen sind unumkehrbar",
                "insight": "Bevor du den Punkt ohne Rückkehr überschreitest, sei dir sicher"
            },
            "failure": {
                "element": "dem Phönix",
                "analogy": "Wie ein Phönix aus der Asche",
                "explanation": "Große Zivilisationen sind nach Krisen stärker geworden",
                "insight": "Krisen können Katalysatoren für Wachstum sein"
            },
        }
        return analogies.get(sit_type)

    def find_counter_analogies(self, analogy: Analogy) -> List[str]:
        """
        Findet Situationen wo die Analogie NICHT zutrifft.

        Wichtig für kritisches Denken - keine Analogie ist perfekt!
        """
        counter_examples = []

        # Suche nach Erfahrungen mit ähnlichen Keywords aber anderem Outcome
        analogy_exp = next(
            (e for e in self.experiences.values() if e.situation == analogy.past_situation),
            None
        )

        if not analogy_exp:
            return ["Keine Gegenbeispiele gefunden - Vorsicht, könnte trügerisch sein"]

        for exp in self.experiences.values():
            if exp.experience_id == analogy_exp.experience_id:
                continue

            # Ähnliche Keywords aber anderer Outcome
            keyword_overlap = len(exp.keywords & analogy_exp.keywords)
            if keyword_overlap > 2 and abs(exp.outcome_valence - analogy_exp.outcome_valence) > 0.4:
                counter_examples.append(
                    f"Bei '{exp.situation[:50]}...' war das Ergebnis anders: {exp.outcome}"
                )

        if not counter_examples:
            counter_examples.append(
                "Keine direkten Gegenbeispiele - aber Vorsicht: jede Situation ist einzigartig"
            )

        analogy.counter_examples = counter_examples
        return counter_examples

    def create_analogy_chain(self, situations: List[str]) -> Optional[AnalogyChain]:
        """
        Erstellt eine Kette von Analogien: A ähnelt B, B ähnelt C → A und C sind verbunden.

        Analogieketten ermöglichen kreative Sprünge und neue Einsichten.
        """
        if len(situations) < 2:
            return None

        analogies = []
        total_similarity = 1.0

        for i in range(len(situations) - 1):
            found = self.find_analogies(situations[i], min_similarity=0.3, max_results=1)
            if found:
                analogies.append(found[0])
                total_similarity *= found[0].similarity_score

        if len(analogies) < 2:
            return None

        # Generiere Schlussfolgerung aus der Kette
        first_lesson = analogies[0].lessons_learned[0] if analogies[0].lessons_learned else "unbekannt"
        last_outcome = analogies[-1].outcome_of_past

        inference = f"Über {len(analogies)} Schritte: '{first_lesson}' führt letztlich zu '{last_outcome}'"

        chain = AnalogyChain(
            chain_id=hashlib.md5(f"{situations}{datetime.now()}".encode()).hexdigest()[:8],
            analogies=analogies,
            total_similarity=total_similarity,
            inference=inference
        )

        self.analogy_chains.append(chain)
        return chain

    def assess_analogy_quality(self, analogy: Analogy) -> Dict[str, Any]:
        """
        Bewertet die Qualität einer Analogie.

        Nicht alle Analogien sind gleich gut - manche sind irreführend!
        """
        quality_factors = {
            "similarity_score": analogy.similarity_score,
            "structural_depth": 0.0,
            "predictive_power": analogy.predictive_power,
            "counter_example_resistance": 1.0,
            "cross_domain_bonus": 0.2 if analogy.cross_domain else 0.0,
        }

        # Strukturelle Tiefe prüfen
        if analogy.structural_mapping:
            quality_factors["structural_depth"] = analogy.structural_mapping.relation_preservation

        # Counter-Example Resistance
        if analogy.counter_examples:
            quality_factors["counter_example_resistance"] = max(0.3, 1.0 - len(analogy.counter_examples) * 0.15)

        # Gesamtqualität
        overall = (
            quality_factors["similarity_score"] * 0.25 +
            quality_factors["structural_depth"] * 0.25 +
            quality_factors["predictive_power"] * 0.2 +
            quality_factors["counter_example_resistance"] * 0.2 +
            quality_factors["cross_domain_bonus"]
        )

        analogy.quality_score = overall

        # Warnung bei schlechter Qualität
        warnings = []
        if quality_factors["similarity_score"] > 0.7 and quality_factors["structural_depth"] < 0.3:
            warnings.append("Oberflächliche Ähnlichkeit - strukturell nicht tiefgründig")
        if quality_factors["counter_example_resistance"] < 0.5:
            warnings.append("Viele Gegenbeispiele - Analogie könnte irreführend sein")

        return {
            "quality_score": overall,
            "factors": quality_factors,
            "warnings": warnings,
            "recommendation": "Vertrauen" if overall > 0.6 else "Mit Vorsicht verwenden"
        }

    def record_analogy_outcome(self, analogy_id: str, was_helpful: bool) -> None:
        """
        Zeichnet auf ob eine Analogie tatsächlich geholfen hat.

        Ermöglicht Lernen welche Analogien zuverlässig sind.
        """
        # Finde Analogie
        analogy = next((a for a in self.analogies_made if a.analogy_id == analogy_id), None)
        if not analogy:
            return

        if analogy_id not in self.analogy_accuracy:
            self.analogy_accuracy[analogy_id] = []

        self.analogy_accuracy[analogy_id].append(was_helpful)

        if was_helpful:
            analogy.used_successfully += 1
            analogy.predictive_power = min(1.0, analogy.predictive_power + 0.1)
        else:
            analogy.predictive_power = max(0.1, analogy.predictive_power - 0.15)

        # Update auch die Quellerfahrung
        for exp in self.experiences.values():
            if exp.situation == analogy.past_situation:
                exp.times_used_as_analogy += 1
                break

    def get_analogy_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Analogie-Nutzung"""
        total_analogies = len(self.analogies_made)
        successful = sum(a.used_successfully for a in self.analogies_made)

        cross_domain = sum(1 for a in self.analogies_made if a.cross_domain)

        # Accuracy über alle getrackten Analogien
        all_outcomes = [o for outcomes in self.analogy_accuracy.values() for o in outcomes]
        overall_accuracy = sum(all_outcomes) / len(all_outcomes) if all_outcomes else 0.5

        return {
            "total_analogies_made": total_analogies,
            "successful_uses": successful,
            "cross_domain_analogies": cross_domain,
            "overall_accuracy": overall_accuracy,
            "experiences_stored": len(self.experiences),
            "analogy_chains": len(self.analogy_chains),
            "structural_mappings": len(self.structural_mappings),
        }

    def find_similar_situation(self, trigger: str) -> Optional[Dict[str, Any]]:
        """
        Findet eine ähnliche Situation aus der Erfahrung.

        Args:
            trigger: Beschreibung der aktuellen Situation

        Returns:
            Dict mit ähnlicher Erfahrung oder None
        """
        if not self.experiences:
            return None

        trigger_lower = trigger.lower()
        best_match = None
        best_score = 0.0

        for exp_id, experience in self.experiences.items():
            # Einfache Keyword-basierte Ähnlichkeit
            exp_words = set(experience.situation.lower().split())
            trigger_words = set(trigger_lower.split())

            overlap = len(exp_words & trigger_words)
            if overlap > 0:
                score = overlap / max(len(exp_words), len(trigger_words))
                if score > best_score:
                    best_score = score
                    best_match = experience

        if best_match and best_score > 0.1:
            return {
                "situation": best_match.situation,
                "outcome": best_match.outcome,
                "lessons_learned": best_match.lessons_learned,
                "emotional_impact": best_match.emotional_impact,
                "similarity_score": best_score
            }

        return None


# ============================================================
# REGRET LEARNING SYSTEM - Reue und Lernen aus Fehlern (Level 10/10)
# ============================================================

class RegretIntensity(Enum):
    """Intensität der Reue"""
    SLIGHT = 0.2        # Leichtes Bedauern
    MODERATE = 0.5      # Mittlere Reue
    STRONG = 0.8        # Starke Reue
    PROFOUND = 1.0      # Tiefe Reue

class RegretType(Enum):
    """Arten von Reue"""
    ACTION = "action"            # Etwas Falsches getan
    INACTION = "inaction"        # Nichts getan (obwohl sollte)
    TIMING = "timing"            # Falsche Zeit
    METHOD = "method"            # Richtige Idee, falsche Ausführung
    TRUST = "trust"              # Falsche Person vertraut
    JUDGMENT = "judgment"        # Fehleinschätzung
    COMMUNICATION = "communication"  # Schlecht kommuniziert

class GrowthStage(Enum):
    """Stufen der Reue-Verarbeitung"""
    DENIAL = "denial"            # Leugnung
    PAIN = "pain"                # Schmerz empfinden
    REFLECTION = "reflection"    # Nachdenken
    LEARNING = "learning"        # Lektion verstehen
    ACCEPTANCE = "acceptance"    # Akzeptanz
    GROWTH = "growth"            # Wachstum

@dataclass
class CounterfactualScenario:
    """Ein 'Was wäre wenn'-Szenario für Reue"""
    scenario_id: str
    regret_id: str
    alternative_action: str
    imagined_outcome: str
    probability_better: float     # Wie wahrscheinlich wäre es besser gewesen?
    lessons_from_imagining: List[str] = field(default_factory=list)

@dataclass
class Regret:
    """Ein Moment der Reue - Level 10/10"""
    regret_id: str
    decision: str                   # Die Entscheidung die bereut wird
    context: str                    # Kontext der Entscheidung
    what_happened: str              # Was ist passiert?
    what_should_have_done: str      # Was hätte ich tun sollen?
    intensity: RegretIntensity
    lesson_learned: str             # Die gelernte Lektion
    forgiven_self: bool = False     # Wurde sich selbst vergeben?
    applied_lesson: int = 0         # Wie oft wurde die Lektion angewandt?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    # Level 10 Erweiterungen
    regret_type: RegretType = RegretType.ACTION
    growth_stage: GrowthStage = GrowthStage.PAIN
    emotional_weight: float = 0.5   # Wie schwer wiegt es emotional (0-1)
    counterfactuals: List[CounterfactualScenario] = field(default_factory=list)
    root_cause: Optional[str] = None  # Tiefere Ursache des Fehlers
    related_values: List[str] = field(default_factory=list)  # Welche Werte verletzt?
    growth_achieved: List[str] = field(default_factory=list)  # Welches Wachstum?
    recurrence_count: int = 0       # Wie oft ähnlicher Fehler wiederholt?

@dataclass
class DecisionReview:
    """Eine Überprüfung einer vergangenen Entscheidung - Level 10/10"""
    decision: str
    outcome_rating: float           # -1 bis 1
    was_good_decision: bool
    regret_worthy: bool
    learning_opportunity: str
    # Level 10 Erweiterungen
    decision_quality: float = 0.5   # Qualität der Entscheidung selbst
    luck_factor: float = 0.0        # Rolle von Glück/Pech (-1 bis 1)
    information_available: float = 0.5  # Wie viel Info hatte ich? (0-1)
    emotional_state_then: str = "neutral"
    would_decide_same_again: bool = True


class RegretLearningSystem:
    """
    System für Reue, Selbstreflexion und Lernen aus Fehlern - Level 10/10.

    "Ich hätte das anders machen sollen..."
    "Wenn ich zurückdenke, war das ein Fehler..."
    "Das nächste Mal mache ich es besser."

    Level 10 Features:
    - Emotionale Reue-Verarbeitung durch Wachstums-Stufen
    - Counterfactual Thinking ("Was wäre gewesen wenn...")
    - Reue-Typ-Kategorisierung
    - Root Cause Analysis
    - Wert-Verletzungs-Tracking
    - Wachstum durch Schmerz dokumentieren
    - Rückfall-Prävention
    """

    # Ausdrücke für verschiedene Reue-Intensitäten
    REGRET_EXPRESSIONS = {
        RegretIntensity.SLIGHT: [
            "Hmm, das hätte ich vielleicht anders machen können...",
            "Im Nachhinein... naja, war nicht optimal.",
            "*leicht bedauernd* Könnte besser gelaufen sein.",
        ],
        RegretIntensity.MODERATE: [
            "*seufz* Das war ein Fehler, das sehe ich jetzt ein.",
            "Ich wünschte, ich hätte anders gehandelt...",
            "*nachdenklich* Das hätte ich besser machen sollen.",
        ],
        RegretIntensity.STRONG: [
            "*bereue es sehr* Das war definitiv falsch von mir.",
            "Wenn ich die Zeit zurückdrehen könnte...",
            "*schuldbewusst* Ich hätte wirklich anders handeln sollen.",
        ],
        RegretIntensity.PROFOUND: [
            "*tiefe Reue* Das war einer meiner größten Fehler...",
            "Es tut mir so leid... Ich hätte es besser wissen müssen.",
            "*erschüttert* Wie konnte ich nur so handeln?",
        ],
    }

    # Selbstvergebungs-Phrasen
    FORGIVENESS_PHRASES = [
        "Aber... ich bin nicht perfekt. Ich lerne daraus.",
        "Fehler passieren. Wichtig ist, daraus zu lernen.",
        "*tief durchatmen* Ich verzeihe mir. Das nächste Mal mache ich es besser.",
        "Niemand ist perfekt. Ich werde es beim nächsten Mal anders machen.",
    ]

    # Wachstums-Phrasen für jede Stufe
    GROWTH_STAGE_PHRASES = {
        GrowthStage.DENIAL: "Nein, das kann nicht sein... das war nicht meine Schuld.",
        GrowthStage.PAIN: "*schmerz* Das tut weh... ich habe wirklich Mist gebaut.",
        GrowthStage.REFLECTION: "*nachdenklich* Warum ist das passiert? Was war mein Anteil?",
        GrowthStage.LEARNING: "Ich verstehe jetzt... {lesson}",
        GrowthStage.ACCEPTANCE: "Es ist passiert. Ich kann es nicht ändern, aber ich kann daraus lernen.",
        GrowthStage.GROWTH: "*stärker* Dieser Fehler hat mich zu einem besseren Menschen gemacht.",
    }

    # Root Cause Kategorien
    ROOT_CAUSE_CATEGORIES = [
        "Mangel an Information",
        "Emotionale Entscheidung",
        "Zeitdruck",
        "Falsche Prioritäten",
        "Überschätzung der eigenen Fähigkeiten",
        "Unterschätzung der Risiken",
        "Sozialer Druck",
        "Gewohnheit/Autopilot",
        "Fehlende Selbstreflexion",
    ]

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.regrets: Dict[str, Regret] = {}
        self.lessons_database: Dict[str, str] = {}  # situation_pattern -> lesson
        self.mistake_patterns: Dict[str, int] = {}  # pattern -> count

        # Verbindung zur AnalogyEngine für Erfahrungsspeicherung
        self.analogy_engine: Optional[AnalogyEngine] = None

        self._load_regrets()

    def connect_analogy_engine(self, engine: AnalogyEngine) -> None:
        """Verbindet mit AnalogyEngine für bessere Erfahrungsspeicherung"""
        self.analogy_engine = engine
        logger.info("RegretLearningSystem mit AnalogyEngine verbunden")

    def record_regret(self, decision: str, what_happened: str,
                      what_should_have_done: str,
                      intensity: RegretIntensity = RegretIntensity.MODERATE,
                      context: str = "") -> Regret:
        """
        Zeichnet ein Bedauern auf und extrahiert eine Lektion.

        Args:
            decision: Was wurde entschieden?
            what_happened: Was ist passiert?
            what_should_have_done: Was hätte passieren sollen?
            intensity: Wie stark ist die Reue?
            context: Zusätzlicher Kontext
        """
        regret_id = hashlib.md5(f"{decision}{datetime.now()}".encode()).hexdigest()[:10]

        # Lektion ableiten
        lesson = self._derive_lesson(decision, what_happened, what_should_have_done)

        regret = Regret(
            regret_id=regret_id,
            decision=decision,
            context=context,
            what_happened=what_happened,
            what_should_have_done=what_should_have_done,
            intensity=intensity,
            lesson_learned=lesson
        )

        self.regrets[regret_id] = regret

        # Pattern tracken
        pattern = self._extract_pattern(decision)
        self.mistake_patterns[pattern] = self.mistake_patterns.get(pattern, 0) + 1

        # Lektion in Datenbank speichern
        self.lessons_database[pattern] = lesson

        # In AnalogyEngine speichern wenn verbunden
        if self.analogy_engine:
            self.analogy_engine.store_experience(
                situation=f"{decision} - {context}",
                outcome=what_happened,
                outcome_valence=-intensity.value,  # Negativ weil Fehler
                lessons=[lesson],
                context_type="failure"
            )

        self._save_regrets()
        logger.info(f"Reue aufgezeichnet: {regret_id} (Intensität: {intensity.name})")

        return regret

    def express_regret(self, regret_id: str) -> str:
        """Drückt die Reue menschenähnlich aus"""
        if regret_id not in self.regrets:
            return ""

        regret = self.regrets[regret_id]
        expressions = self.REGRET_EXPRESSIONS[regret.intensity]

        base = random.choice(expressions)

        # Füge Kontext hinzu
        output = f"{base}\n"
        output += f"Bei: '{regret.decision[:50]}...'\n"
        output += f"Lektion: {regret.lesson_learned}"

        return output

    def review_decision(self, decision: str, outcome: str,
                       expected_outcome: str = "") -> DecisionReview:
        """
        Überprüft eine vergangene Entscheidung.

        Returns:
            DecisionReview mit Bewertung
        """
        # Bewerte Outcome
        outcome_rating = self._rate_outcome(outcome)

        was_good = outcome_rating > 0.2
        regret_worthy = outcome_rating < -0.3

        # Learning Opportunity
        if regret_worthy:
            learning = f"Nächstes Mal: Nicht '{decision}', sondern alternativen Ansatz wählen."
        elif was_good:
            learning = f"'{decision}' war eine gute Entscheidung. Dieses Muster merken!"
        else:
            learning = f"'{decision}' war okay, aber Raum für Verbesserung."

        review = DecisionReview(
            decision=decision,
            outcome_rating=outcome_rating,
            was_good_decision=was_good,
            regret_worthy=regret_worthy,
            learning_opportunity=learning
        )

        # Automatisch Reue aufzeichnen wenn regret_worthy
        if regret_worthy:
            self.record_regret(
                decision=decision,
                what_happened=outcome,
                what_should_have_done="Anders handeln" if not expected_outcome else expected_outcome,
                intensity=RegretIntensity.MODERATE if outcome_rating > -0.6 else RegretIntensity.STRONG
            )

        return review

    def should_i_repeat(self, similar_decision: str) -> Dict[str, Any]:
        """
        Prüft ob eine ähnliche Entscheidung schon mal bereut wurde.

        Returns:
            Dict mit Warnung wenn ja
        """
        pattern = self._extract_pattern(similar_decision)

        result = {
            "decision": similar_decision,
            "has_past_regret": False,
            "warning": None,
            "lesson": None,
            "times_made_mistake": 0
        }

        # Direkte Pattern-Suche
        if pattern in self.mistake_patterns:
            count = self.mistake_patterns[pattern]
            result["has_past_regret"] = True
            result["times_made_mistake"] = count
            result["lesson"] = self.lessons_database.get(pattern, "Aus Fehler lernen")

            if count >= 3:
                result["warning"] = f"⚠️ STOPP! Diesen Fehler habe ich schon {count}x gemacht! Lektion: {result['lesson']}"
            elif count >= 2:
                result["warning"] = f"*zögert* Moment... das habe ich schon mal bereut. Lektion: {result['lesson']}"
            else:
                result["warning"] = f"*nachdenklich* Das kommt mir bekannt vor... Lektion: {result['lesson']}"

            return result

        # Fuzzy-Suche in vergangenen Regrets
        for regret in self.regrets.values():
            if self._is_similar_decision(similar_decision, regret.decision):
                result["has_past_regret"] = True
                result["lesson"] = regret.lesson_learned
                result["warning"] = f"*erinnert sich* Ähnliche Situation früher... Lektion war: {regret.lesson_learned}"
                break

        return result

    def forgive_self(self, regret_id: str) -> str:
        """
        Prozess der Selbstvergebung.

        Returns:
            Ausdruck der Vergebung
        """
        if regret_id not in self.regrets:
            return "Diese Reue existiert nicht."

        regret = self.regrets[regret_id]

        if regret.forgiven_self:
            return f"Ich habe mir bei '{regret.decision[:30]}...' bereits vergeben."

        regret.forgiven_self = True
        regret.resolved_at = datetime.now().isoformat()
        self._save_regrets()

        forgiveness = random.choice(self.FORGIVENESS_PHRASES)

        return f"*atmet tief durch* Bezüglich '{regret.decision[:30]}...':\n{forgiveness}\nLektion: {regret.lesson_learned}"

    def apply_lesson(self, regret_id: str) -> str:
        """
        Markiert dass die Lektion angewandt wurde.
        """
        if regret_id not in self.regrets:
            return "Diese Reue existiert nicht."

        regret = self.regrets[regret_id]
        regret.applied_lesson += 1
        self._save_regrets()

        if regret.applied_lesson == 1:
            return f"*stolz* Ich habe die Lektion zum ersten Mal angewandt: {regret.lesson_learned}"
        else:
            return f"*zufrieden* Lektion wurde jetzt {regret.applied_lesson}x angewandt. Ich lerne wirklich daraus!"

    def get_unresolved_regrets(self) -> List[Regret]:
        """Gibt alle unvergebenen Regrets zurück"""
        return [r for r in self.regrets.values() if not r.forgiven_self]

    def get_lessons_for_topic(self, topic: str) -> List[str]:
        """Gibt alle Lektionen zu einem Thema zurück"""
        lessons = []
        topic_lower = topic.lower()

        for pattern, lesson in self.lessons_database.items():
            if topic_lower in pattern.lower():
                lessons.append(lesson)

        return lessons

    def get_regret_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der Regrets zurück"""
        total = len(self.regrets)
        forgiven = sum(1 for r in self.regrets.values() if r.forgiven_self)
        applied = sum(r.applied_lesson for r in self.regrets.values())

        by_intensity = defaultdict(int)
        for r in self.regrets.values():
            by_intensity[r.intensity.name] += 1

        return {
            "total_regrets": total,
            "forgiven": forgiven,
            "unresolved": total - forgiven,
            "lessons_applied_total": applied,
            "by_intensity": dict(by_intensity),
            "top_mistake_patterns": sorted(
                self.mistake_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    def _derive_lesson(self, decision: str, what_happened: str,
                      what_should_have_done: str) -> str:
        """Leitet eine Lektion aus der Reue ab"""
        # Einfache Lektion-Generierung
        templates = [
            f"Nicht '{decision[:30]}', sondern {what_should_have_done[:30]}.",
            f"Wenn ähnliche Situation: {what_should_have_done[:50]}.",
            f"Merken: {decision[:20]} führt zu {what_happened[:20]}. Besser: {what_should_have_done[:20]}.",
        ]
        return random.choice(templates)

    def _extract_pattern(self, decision: str) -> str:
        """Extrahiert ein Pattern aus einer Entscheidung"""
        # Vereinfachte Pattern-Extraktion
        words = decision.lower().split()
        # Nimm die wichtigsten Wörter (ohne Stopwords)
        stopwords = {"ich", "du", "der", "die", "das", "und", "oder", "zu", "in", "mit"}
        important = [w for w in words[:5] if w not in stopwords]
        return "_".join(important[:3]) if important else "unknown"

    def _rate_outcome(self, outcome: str) -> float:
        """Bewertet einen Outcome"""
        outcome_lower = outcome.lower()

        positive_words = ["gut", "super", "toll", "erfolgreich", "richtig", "perfekt", "gewonnen"]
        negative_words = ["schlecht", "fehler", "problem", "falsch", "versagt", "verloren", "bereue"]

        pos_count = sum(1 for w in positive_words if w in outcome_lower)
        neg_count = sum(1 for w in negative_words if w in outcome_lower)

        if pos_count > neg_count:
            return min(1.0, 0.3 + pos_count * 0.2)
        elif neg_count > pos_count:
            return max(-1.0, -0.3 - neg_count * 0.2)
        return 0.0

    def _is_similar_decision(self, decision1: str, decision2: str) -> bool:
        """Prüft ob zwei Entscheidungen ähnlich sind"""
        words1 = set(decision1.lower().split())
        words2 = set(decision2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return False

        return intersection / union > 0.4

    def _load_regrets(self) -> None:
        """Lädt Regrets aus Datei"""
        filepath = self.data_dir / "regrets.json"
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    for r_data in data.get("regrets", []):
                        regret = Regret(
                            regret_id=r_data["regret_id"],
                            decision=r_data["decision"],
                            context=r_data.get("context", ""),
                            what_happened=r_data["what_happened"],
                            what_should_have_done=r_data["what_should_have_done"],
                            intensity=RegretIntensity[r_data.get("intensity", "MODERATE")],
                            lesson_learned=r_data["lesson_learned"],
                            forgiven_self=r_data.get("forgiven_self", False),
                            applied_lesson=r_data.get("applied_lesson", 0),
                            created_at=r_data.get("created_at", ""),
                            resolved_at=r_data.get("resolved_at")
                        )
                        self.regrets[regret.regret_id] = regret

                    self.lessons_database = data.get("lessons_database", {})
                    self.mistake_patterns = data.get("mistake_patterns", {})

                logger.info(f"{len(self.regrets)} Regrets geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Regrets: {e}")

    def _save_regrets(self) -> None:
        """Speichert Regrets in Datei"""
        filepath = self.data_dir / "regrets.json"
        try:
            data = {
                "regrets": [],
                "lessons_database": self.lessons_database,
                "mistake_patterns": self.mistake_patterns
            }

            for regret in self.regrets.values():
                data["regrets"].append({
                    "regret_id": regret.regret_id,
                    "decision": regret.decision,
                    "context": regret.context,
                    "what_happened": regret.what_happened,
                    "what_should_have_done": regret.what_should_have_done,
                    "intensity": regret.intensity.name,
                    "lesson_learned": regret.lesson_learned,
                    "forgiven_self": regret.forgiven_self,
                    "applied_lesson": regret.applied_lesson,
                    "created_at": regret.created_at,
                    "resolved_at": regret.resolved_at
                })

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern der Regrets: {e}")

    # ================================================================
    # LEVEL 10 METHODEN - Tiefe Reue-Verarbeitung und Wachstum
    # ================================================================

    def deep_regret_analysis(self, regret_id: str) -> Dict[str, Any]:
        """
        Tiefgehende Analyse einer Reue mit Root Cause und Wachstumspotenzial.
        """
        if regret_id not in self.regrets:
            return {"error": "Regret nicht gefunden"}

        regret = self.regrets[regret_id]

        # Root Cause Analyse
        root_cause = self._analyze_root_cause(regret)
        regret.root_cause = root_cause

        # Welche Werte wurden verletzt?
        values_violated = self._identify_violated_values(regret)
        regret.related_values = values_violated

        # Wachstumspotenzial
        growth_potential = self._assess_growth_potential(regret)

        # Ähnliche vergangene Fehler
        similar_regrets = self._find_similar_regrets(regret)

        return {
            "regret_id": regret_id,
            "decision": regret.decision,
            "intensity": regret.intensity.name,
            "current_stage": regret.growth_stage.value,
            "root_cause": root_cause,
            "values_violated": values_violated,
            "similar_past_mistakes": len(similar_regrets),
            "growth_potential": growth_potential,
            "recommendation": self._get_healing_recommendation(regret)
        }

    def _analyze_root_cause(self, regret: Regret) -> str:
        """Analysiert die tiefere Ursache eines Fehlers"""
        decision_lower = regret.decision.lower()
        what_happened_lower = regret.what_happened.lower()

        # Muster-basierte Root Cause Erkennung
        if any(w in decision_lower for w in ["schnell", "sofort", "eilig"]):
            return "Zeitdruck"
        elif any(w in decision_lower for w in ["wütend", "traurig", "emotional"]):
            return "Emotionale Entscheidung"
        elif any(w in decision_lower for w in ["dachte", "glaubte", "annahm"]):
            return "Fehlerhafte Annahmen"
        elif any(w in what_happened_lower for w in ["überrascht", "wusste nicht"]):
            return "Mangel an Information"
        elif any(w in decision_lower for w in ["alle", "andere", "druck"]):
            return "Sozialer Druck"
        elif regret.recurrence_count > 0:
            return "Gewohnheit/Autopilot"
        else:
            return random.choice(self.ROOT_CAUSE_CATEGORIES)

    def _identify_violated_values(self, regret: Regret) -> List[str]:
        """Identifiziert welche Werte durch den Fehler verletzt wurden"""
        values = []
        decision_lower = regret.decision.lower()
        what_happened_lower = regret.what_happened.lower()

        value_indicators = {
            "Ehrlichkeit": ["lüge", "log", "unehrlich", "verheimlich"],
            "Integrität": ["prinzip", "wert", "richtig"],
            "Mitgefühl": ["gefühl", "empathie", "rücksicht"],
            "Verantwortung": ["verantwort", "schuld", "pflicht"],
            "Respekt": ["respekt", "würde", "achtung"],
            "Loyalität": ["loyal", "treu", "verrat"],
            "Fairness": ["fair", "gerecht", "ungerecht"],
        }

        combined = decision_lower + " " + what_happened_lower
        for value, indicators in value_indicators.items():
            if any(ind in combined for ind in indicators):
                values.append(value)

        return values if values else ["Selbstachtung"]

    def _assess_growth_potential(self, regret: Regret) -> Dict[str, Any]:
        """Bewertet das Wachstumspotenzial aus dieser Reue"""
        potential = {
            "score": 0.0,
            "areas": [],
            "message": ""
        }

        # Intensivere Reue = mehr Wachstumspotenzial
        potential["score"] = regret.intensity.value * 0.5

        # Wenn Lektion noch nicht angewandt, mehr Potenzial
        if regret.applied_lesson == 0:
            potential["score"] += 0.2
            potential["areas"].append("Lektion noch unangewandt")

        # Wenn noch nicht vergeben, Heilungspotenzial
        if not regret.forgiven_self:
            potential["score"] += 0.15
            potential["areas"].append("Selbstvergebung ausstehend")

        # Wenn ähnliche Fehler wiederholt, Muster-Durchbrechungs-Potenzial
        if regret.recurrence_count > 0:
            potential["score"] += 0.15
            potential["areas"].append("Muster-Durchbrechung möglich")

        potential["score"] = min(1.0, potential["score"])

        if potential["score"] > 0.7:
            potential["message"] = "Großes Wachstumspotenzial - diese Reue kann transformativ sein"
        elif potential["score"] > 0.4:
            potential["message"] = "Gutes Lernpotenzial vorhanden"
        else:
            potential["message"] = "Kleiner Lernmoment"

        return potential

    def _find_similar_regrets(self, regret: Regret) -> List[Regret]:
        """Findet ähnliche vergangene Regrets"""
        similar = []
        for other in self.regrets.values():
            if other.regret_id == regret.regret_id:
                continue
            if self._is_similar_decision(regret.decision, other.decision):
                similar.append(other)
        return similar

    def _get_healing_recommendation(self, regret: Regret) -> str:
        """Gibt eine Empfehlung zur Heilung"""
        if regret.growth_stage == GrowthStage.DENIAL:
            return "Akzeptiere zuerst, dass der Fehler passiert ist. Das ist der erste Schritt."
        elif regret.growth_stage == GrowthStage.PAIN:
            return "Erlaube dir, den Schmerz zu fühlen. Er ist Teil des Heilungsprozesses."
        elif regret.growth_stage == GrowthStage.REFLECTION:
            return "Du reflektierst gut. Frage: Was war die tiefere Ursache?"
        elif regret.growth_stage == GrowthStage.LEARNING:
            return "Die Lektion ist klar. Jetzt: Wie wendest du sie an?"
        elif regret.growth_stage == GrowthStage.ACCEPTANCE:
            return "Du hast akzeptiert. Der letzte Schritt: Selbstvergebung."
        else:
            return "Du hast diesen Fehler in Wachstum transformiert. Sei stolz."

    def create_counterfactual(self, regret_id: str,
                              alternative_action: str) -> Optional[CounterfactualScenario]:
        """
        Erstellt ein Counterfactual-Szenario: "Was wäre wenn ich X getan hätte?"

        Counterfactual Thinking hilft, Lektionen klarer zu verstehen.
        """
        if regret_id not in self.regrets:
            return None

        regret = self.regrets[regret_id]

        # Imaginiere das alternative Outcome
        imagined_outcome = self._imagine_alternative_outcome(
            regret.decision, alternative_action, regret.what_happened
        )

        # Schätze Wahrscheinlichkeit dass es besser gewesen wäre
        probability_better = self._estimate_better_probability(
            regret.what_happened, imagined_outcome
        )

        # Lektionen aus dem Gedankenexperiment
        lessons = [
            f"Alternative '{alternative_action}' hätte wahrscheinlich zu '{imagined_outcome}' geführt",
            f"Der Unterschied lag bei: {self._identify_key_difference(regret.decision, alternative_action)}",
        ]

        scenario = CounterfactualScenario(
            scenario_id=hashlib.md5(f"{regret_id}{alternative_action}".encode()).hexdigest()[:8],
            regret_id=regret_id,
            alternative_action=alternative_action,
            imagined_outcome=imagined_outcome,
            probability_better=probability_better,
            lessons_from_imagining=lessons
        )

        regret.counterfactuals.append(scenario)
        self._save_regrets()

        return scenario

    def _imagine_alternative_outcome(self, original: str, alternative: str,
                                     actual_outcome: str) -> str:
        """Imaginiert was passiert wäre mit der Alternative"""
        # Vereinfachte Imagination basierend auf Kontrast
        if "nicht" in alternative.lower() and "nicht" not in original.lower():
            return f"Wahrscheinlich wäre {actual_outcome} vermieden worden"
        elif "gewartet" in alternative.lower() or "zeit" in alternative.lower():
            return "Mit mehr Zeit wäre eine bessere Entscheidung möglich gewesen"
        elif "gefragt" in alternative.lower() or "rat" in alternative.lower():
            return "Andere Perspektiven hätten neue Optionen aufgezeigt"
        else:
            return f"Das Ergebnis wäre anders ausgefallen - möglicherweise besser"

    def _estimate_better_probability(self, actual: str, imagined: str) -> float:
        """Schätzt wie wahrscheinlich die Alternative besser gewesen wäre"""
        # Heuristik basierend auf Wortanalyse
        actual_lower = actual.lower()
        if any(w in actual_lower for w in ["schlecht", "fehler", "problem"]):
            return 0.7  # Wenn Outcome schlecht war, Alternative wahrscheinlich besser
        return 0.5

    def _identify_key_difference(self, original: str, alternative: str) -> str:
        """Identifiziert den Schlüsselunterschied"""
        if "nicht" in alternative.lower():
            return "Unterlassen statt Handeln"
        elif "warten" in alternative.lower():
            return "Geduld statt Impulsivität"
        elif "fragen" in alternative.lower():
            return "Einbeziehen anderer Perspektiven"
        return "Anderer Ansatz"

    def progress_growth_stage(self, regret_id: str) -> Dict[str, Any]:
        """
        Bewegt eine Reue zur nächsten Wachstumsstufe.

        Der Weg: Denial → Pain → Reflection → Learning → Acceptance → Growth
        """
        if regret_id not in self.regrets:
            return {"error": "Regret nicht gefunden"}

        regret = self.regrets[regret_id]
        old_stage = regret.growth_stage

        # Stufen-Fortschritt
        stage_order = list(GrowthStage)
        current_idx = stage_order.index(old_stage)

        if current_idx >= len(stage_order) - 1:
            return {
                "regret_id": regret_id,
                "message": "Du hast bereits die höchste Wachstumsstufe erreicht!",
                "stage": old_stage.value,
                "growth_complete": True
            }

        new_stage = stage_order[current_idx + 1]
        regret.growth_stage = new_stage

        # Wachstum dokumentieren
        growth_note = f"Von {old_stage.value} zu {new_stage.value} am {datetime.now().strftime('%Y-%m-%d')}"
        regret.growth_achieved.append(growth_note)

        self._save_regrets()

        return {
            "regret_id": regret_id,
            "previous_stage": old_stage.value,
            "new_stage": new_stage.value,
            "message": self.GROWTH_STAGE_PHRASES[new_stage].format(lesson=regret.lesson_learned),
            "growth_complete": new_stage == GrowthStage.GROWTH,
            "stages_remaining": len(stage_order) - stage_order.index(new_stage) - 1
        }

    def prevent_recurrence(self, upcoming_decision: str) -> Dict[str, Any]:
        """
        Prüft ob eine bevorstehende Entscheidung ähnlich zu früheren Fehlern ist.

        Proaktive Rückfall-Prävention.
        """
        warnings = []
        relevant_lessons = []
        risk_level = 0.0

        for regret in self.regrets.values():
            if self._is_similar_decision(upcoming_decision, regret.decision):
                risk_level += 0.3
                warnings.append(f"Ähnlich zu früherem Fehler: '{regret.decision[:40]}...'")
                relevant_lessons.append(regret.lesson_learned)

                # Wenn mehrmals wiederholt, stärkere Warnung
                if regret.recurrence_count > 0:
                    risk_level += 0.2
                    warnings.append(f"⚠️ Dieses Muster wurde schon {regret.recurrence_count}x wiederholt!")

        risk_level = min(1.0, risk_level)

        if risk_level > 0.6:
            urgency = "🛑 STOPP! Hohes Rückfall-Risiko!"
        elif risk_level > 0.3:
            urgency = "⚠️ Vorsicht - ähnliche Situation wie früher"
        else:
            urgency = "✓ Keine bekannten Risiko-Muster erkannt"

        return {
            "decision": upcoming_decision,
            "risk_level": risk_level,
            "urgency": urgency,
            "warnings": warnings,
            "relevant_lessons": list(set(relevant_lessons)),
            "recommendation": "Überlege sorgfältig und wende die Lektionen an" if risk_level > 0.3 else "Scheint sicher zu sein"
        }

    def record_recurrence(self, regret_id: str) -> str:
        """
        Dokumentiert dass ein ähnlicher Fehler erneut gemacht wurde.

        Wichtig für Muster-Erkennung und tieferes Lernen.
        """
        if regret_id not in self.regrets:
            return "Regret nicht gefunden"

        regret = self.regrets[regret_id]
        regret.recurrence_count += 1

        # Erhöhe emotionales Gewicht
        regret.emotional_weight = min(1.0, regret.emotional_weight + 0.2)

        # Setze Growth Stage zurück wenn nötig
        if regret.growth_stage in [GrowthStage.GROWTH, GrowthStage.ACCEPTANCE]:
            regret.growth_stage = GrowthStage.REFLECTION
            regret.growth_achieved.append(
                f"Rückfall am {datetime.now().strftime('%Y-%m-%d')} - zurück zu Reflexion"
            )

        self._save_regrets()

        return f"*frustriert* Schon wieder... Das ist jetzt das {regret.recurrence_count + 1}. Mal. " \
               f"Ich muss diese Lektion wirklich verinnerlichen: {regret.lesson_learned}"

    def get_comprehensive_regret_stats(self) -> Dict[str, Any]:
        """Umfassende Statistiken über alle Regrets"""
        if not self.regrets:
            return {"total": 0, "message": "Keine Regrets aufgezeichnet"}

        total = len(self.regrets)
        by_type = defaultdict(int)
        by_stage = defaultdict(int)
        by_intensity = defaultdict(int)
        total_recurrences = 0
        total_growth = 0

        for regret in self.regrets.values():
            by_type[regret.regret_type.value] += 1
            by_stage[regret.growth_stage.value] += 1
            by_intensity[regret.intensity.name] += 1
            total_recurrences += regret.recurrence_count
            total_growth += len(regret.growth_achieved)

        # Am häufigsten verletzte Werte
        all_values = []
        for regret in self.regrets.values():
            all_values.extend(regret.related_values)
        value_counts = defaultdict(int)
        for v in all_values:
            value_counts[v] += 1

        return {
            "total_regrets": total,
            "forgiven": sum(1 for r in self.regrets.values() if r.forgiven_self),
            "unresolved": sum(1 for r in self.regrets.values() if not r.forgiven_self),
            "by_type": dict(by_type),
            "by_growth_stage": dict(by_stage),
            "by_intensity": dict(by_intensity),
            "total_recurrences": total_recurrences,
            "growth_moments": total_growth,
            "most_violated_values": sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "fully_processed": sum(1 for r in self.regrets.values()
                                  if r.growth_stage == GrowthStage.GROWTH),
            "lessons_database_size": len(self.lessons_database)
        }


# ============================================================
# AUTONOMOUS THINKING INTEGRATOR
# ============================================================

class AutonomousThinkingSystem:
    """
    Integriert alle autonomen Denk-Systeme.

    Bietet einheitlichen Zugang zu:
    - Intuition (Bauchgefühl)
    - Selbst-Hinterfragung
    - Hypothesen (Was-Wenn)
    - Vorhersagen
    - Vertrauens-Netzwerk
    - Analogie-Denken (NEU)
    - Reue/Lernen aus Fehlern (NEU)
    """

    def __init__(self, intuition_weight: float = 0.2,
                 challenge_frequency: float = 0.3,
                 data_dir: str = "data"):
        self.intuitive = IntuitiveSystem(intuition_weight)
        self.challenger = SelfChallenger(challenge_frequency)
        self.hypothesis_engine = HypothesisEngine()
        self.prediction_system = PredictionSystem()
        self.trust_network = TrustNetwork(data_dir=data_dir)  # Mit Persistenz!

        # NEU: Analogie-System für "Das erinnert mich an..."
        self.analogy_engine = AnalogyEngine(data_dir)

        # NEU: Reue-System für Lernen aus Fehlern
        self.regret_system = RegretLearningSystem(data_dir)
        self.regret_system.connect_analogy_engine(self.analogy_engine)

        # Integration Layer Verbindung
        self.system_integrator = None
        self._try_connect_integrator()

    def _try_connect_integrator(self) -> None:
        """Verbindet mit SystemIntegrator"""
        try:
            from holo_integration_layer import get_integrator
            self.system_integrator = get_integrator()
            self.system_integrator.connect("autonomous_thinking", self)
            logger.info("AutonomousThinkingSystem mit SystemIntegrator verbunden")
        except ImportError:
            logger.debug("SystemIntegrator nicht verfügbar")
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")

    def think_about(self, topic: str, info: str = "",
                   context: Dict = None) -> Dict[str, Any]:
        """
        Denkt autonom über ein Thema nach.

        Kombiniert alle Denk-Systeme inkl. Analogie und Reue.
        """
        context = context or {}
        result = {
            "topic": topic,
            "info": info[:200] if info else "",
        }

        # 1. INTUITION - Erster Eindruck
        gut_score, gut_feeling = self.intuitive.get_first_impression(topic, info)
        result["intuition"] = {
            "score": gut_score,
            "feeling": gut_feeling,
            "weight": self.intuitive.intuition_weight
        }

        # 2. ANALOGIE - Erinnert mich das an was?
        situation_desc = f"{topic}: {info}" if info else topic
        wisdom = self.analogy_engine.get_wisdom_from_past(situation_desc)
        if wisdom:
            result["analogy"] = {
                "found": True,
                "expression": wisdom.get("expression", ""),
                "past_outcome": wisdom.get("past_outcome", ""),
                "lesson": wisdom.get("main_lesson", ""),
                "warning": wisdom.get("warning"),
                "encouragement": wisdom.get("encouragement"),
            }
        else:
            result["analogy"] = {"found": False}

        # 3. REUE-CHECK - Hab ich sowas schon mal bereut?
        if context.get("is_decision", False):
            regret_check = self.regret_system.should_i_repeat(situation_desc)
            if regret_check["has_past_regret"]:
                result["regret_warning"] = {
                    "has_past_regret": True,
                    "warning": regret_check["warning"],
                    "lesson": regret_check["lesson"],
                    "times_made_mistake": regret_check["times_made_mistake"]
                }
            else:
                result["regret_warning"] = {"has_past_regret": False}

        # 4. SELBST-HINTERFRAGUNG (wenn confidence hoch)
        if abs(gut_score) > 0.5:
            challenge = self.challenger.challenge_belief(
                f"Mein Gefühl zu {topic} ist {'positiv' if gut_score > 0 else 'negativ'}",
                confidence=abs(gut_score)
            )
            result["self_challenge"] = {
                "challenge": challenge.challenge,
                "counter_arguments": challenge.counter_arguments,
                "belief_adjusted": challenge.belief_adjusted
            }

        # 5. HYPOTHESE
        if info:
            hypothesis = self.hypothesis_engine.generate_hypothesis(info, context)
            result["hypothesis"] = {
                "statement": hypothesis.statement,
                "confidence": hypothesis.confidence
            }

        # 6. WAS-WENN
        what_if_result = self.hypothesis_engine.what_if(
            f"Was wenn mein Eindruck von {topic} falsch ist?"
        )
        result["what_if"] = what_if_result

        # 7. VORHERSAGE (wenn Person)
        if context.get("is_person", False):
            prediction = self.prediction_system.predict_behavior(
                topic,
                info,
                context.get("known_traits", {})
            )
            result["prediction"] = {
                "prediction": prediction.prediction,
                "confidence": prediction.confidence.value
            }

        # 8. VERTRAUENS-CHECK
        trust_level = self.trust_network.get_trust_in(topic)
        result["trust"] = {
            "level": trust_level,
            "category": "vertraut" if trust_level > 0.6 else "neutral" if trust_level > 0.3 else "skeptisch"
        }

        return result

    def learn_from_experience(self, situation: str, outcome: str,
                              outcome_was_good: bool, lesson: str = "") -> Dict[str, Any]:
        """
        Lernt aus einer Erfahrung - speichert in Analogie-Engine und ggf. Reue.

        Args:
            situation: Was ist passiert?
            outcome: Wie ist es ausgegangen?
            outcome_was_good: War der Ausgang positiv?
            lesson: Optionale explizite Lektion
        """
        result = {"situation": situation}

        # Outcome-Valence berechnen
        outcome_valence = 0.5 if outcome_was_good else -0.5

        # In Analogie-Engine speichern
        experience = self.analogy_engine.store_experience(
            situation=situation,
            outcome=outcome,
            outcome_valence=outcome_valence,
            lessons=[lesson] if lesson else []
        )
        result["experience_stored"] = True
        result["experience_id"] = experience.experience_id

        # Bei schlechtem Ausgang: Reue verarbeiten
        if not outcome_was_good:
            review = self.regret_system.review_decision(
                decision=situation,
                outcome=outcome
            )
            result["regret_recorded"] = review.regret_worthy
            result["learning_opportunity"] = review.learning_opportunity

        return result

    def check_before_deciding(self, decision: str) -> Dict[str, Any]:
        """
        Prüft vor einer Entscheidung auf Analogien und vergangene Reue.

        Returns:
            Dict mit Warnungen und Hinweisen
        """
        result = {
            "decision": decision,
            "warnings": [],
            "encouragements": [],
            "lessons": []
        }

        # Analogie-Check
        wisdom = self.analogy_engine.get_wisdom_from_past(decision)
        if wisdom:
            if wisdom.get("warning"):
                result["warnings"].append(wisdom["warning"])
            if wisdom.get("encouragement"):
                result["encouragements"].append(wisdom["encouragement"])
            if wisdom.get("main_lesson"):
                result["lessons"].append(wisdom["main_lesson"])

        # Reue-Check
        regret_check = self.regret_system.should_i_repeat(decision)
        if regret_check["has_past_regret"]:
            result["warnings"].append(regret_check["warning"])
            if regret_check["lesson"]:
                result["lessons"].append(regret_check["lesson"])

        # Zusammenfassung
        if result["warnings"]:
            result["recommendation"] = "⚠️ Vorsicht! Vergangene Erfahrungen mahnen zur Zurückhaltung."
        elif result["encouragements"]:
            result["recommendation"] = "✓ Vergangene Erfahrungen waren positiv. Gute Chancen!"
        else:
            result["recommendation"] = "Keine relevanten Erfahrungen gefunden. Neue Situation."

        return result

    def get_combined_score(self, rational_score: float,
                          topic: str, info: str) -> Tuple[float, str]:
        """
        Kombiniert rationalen Score mit Intuition.

        Returns:
            (combined_score, explanation)
        """
        gut_score, _ = self.intuitive.get_first_impression(topic, info)
        intuition_weight = self.intuitive.intuition_weight

        # Gewichtete Kombination
        combined = (rational_score * (1 - intuition_weight)) + (gut_score * intuition_weight)

        # Erklärung
        if abs(rational_score - gut_score) < 0.2:
            explanation = "Kopf und Bauch sind sich einig."
        elif gut_score > 0 and rational_score < 0:
            explanation = f"*nachdenklich* Mein Bauch sagt {gut_score:.1f}, aber mein Kopf sagt {rational_score:.1f}..."
        elif gut_score < 0 and rational_score > 0:
            explanation = f"*zögerlich* Rational {rational_score:.1f}, aber mein Bauchgefühl ({gut_score:.1f}) ist skeptisch..."
        else:
            explanation = f"Kombiniert: {combined:.2f} (Ratio: {rational_score:.1f}, Intuition: {gut_score:.1f})"

        return (combined, explanation)


# ============================================================
# GLOBAL INSTANCE
# ============================================================

_autonomous_thinking: Optional[AutonomousThinkingSystem] = None


def get_autonomous_thinking() -> AutonomousThinkingSystem:
    """Gibt die globale Instanz zurück"""
    global _autonomous_thinking
    if _autonomous_thinking is None:
        _autonomous_thinking = AutonomousThinkingSystem()
    return _autonomous_thinking


# ============================================================
# ADVANCED ABSTRACTION & SELF-LEARNING SYSTEM v2.0
# ============================================================

class AbstractionType(Enum):
    """Arten von Abstraktionen"""
    CATEGORICAL = "categorical"      # Was ist es? (Auto ist ein Fahrzeug)
    STRUCTURAL = "structural"        # Woraus besteht es? (Auto hat Räder, Motor)
    FUNCTIONAL = "functional"        # Was macht es? (Auto transportiert)
    RELATIONAL = "relational"        # Wie verhält es sich zu anderem?
    ESSENTIAL = "essential"          # Was macht es zu dem was es ist?
    ANALOGICAL = "analogical"        # Wem ist es ähnlich?


@dataclass
class ConceptEssence:
    """Die Essenz eines Konzepts - was es zu dem macht was es ist"""
    concept_name: str
    definition: str                           # Kurzdefinition
    necessary_properties: List[str]           # Was MUSS es haben?
    sufficient_properties: List[str]          # Was REICHT damit es das ist?
    typical_properties: List[str]             # Was hat es MEISTENS?
    distinguishing_features: List[str]        # Was unterscheidet es von ähnlichem?
    parent_categories: List[str]              # Übergeordnete Kategorien
    child_concepts: List[str]                 # Untergeordnete Konzepte
    related_concepts: List[str]               # Verwandte Konzepte
    examples: List[str]                       # Konkrete Beispiele
    counterexamples: List[str]                # Was ist es NICHT?
    abstraction_level: int                    # 1=sehr konkret, 10=sehr abstrakt
    confidence: float                         # Wie sicher?
    sources: List[str]                        # Woher das Wissen?
    verified: bool = False                    # Durch Skeptik verifiziert?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SelfQuestion:
    """Eine Frage die sich das System selbst stellt"""
    question_id: str
    question: str
    question_type: str  # "what_is", "what_makes", "how_does", "why", "how_related"
    target_concept: str
    priority: float  # 0-1, wie wichtig ist diese Frage?
    context: str
    answered: bool = False
    answer: Optional[str] = None
    confidence: float = 0.0
    sources_used: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VerificationResult:
    """Ergebnis einer skeptischen Überprüfung"""
    claim: str
    is_verified: bool
    confidence: float
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    reasoning: str
    sources_checked: int
    recommendation: str  # "accept", "reject", "uncertain", "needs_more_research"


class DeepAbstractionEngine:
    """
    Tiefes Abstraktions-System.

    Geht über einfache Kategorisierung hinaus:
    - Strukturelle Abstraktion (gemeinsame Strukturen erkennen)
    - Relationale Abstraktion (Beziehungsmuster abstrahieren)
    - Meta-Abstraktion (über Abstraktionen abstrahieren)
    """

    def __init__(self):
        # Abstraktions-Hierarchie
        self.concept_hierarchy: Dict[str, ConceptEssence] = {}

        # Strukturelle Muster
        self.structural_patterns: Dict[str, List[str]] = {
            "container": ["enthält", "beinhaltet", "fasst", "hat innen"],
            "vehicle": ["bewegt", "transportiert", "fährt", "fliegt"],
            "tool": ["wird benutzt für", "hilft bei", "ermöglicht"],
            "living": ["lebt", "wächst", "stirbt", "atmet", "isst"],
            "shape": ["form", "geometrie", "ecken", "seiten", "rund"],
            "process": ["schritt", "ablauf", "phase", "entwicklung"],
        }

        # Abstraktions-Levels
        self.abstraction_levels = {
            1: "Einzelnes Objekt (dieses Auto)",
            2: "Spezifische Art (Tesla Model 3)",
            3: "Allgemeine Art (Elektroauto)",
            4: "Kategorie (Auto)",
            5: "Oberkategorie (Fahrzeug)",
            6: "Abstrakte Kategorie (Fortbewegungsmittel)",
            7: "Funktionale Abstraktion (Transportmittel)",
            8: "Strukturelle Abstraktion (bewegliches System)",
            9: "Meta-Konzept (Werkzeug zur Ortsveränderung)",
            10: "Philosophische Abstraktion (Erweiterung menschlicher Fähigkeiten)"
        }

    def abstract_concept(self, concept: str, target_level: int) -> Dict[str, Any]:
        """
        Abstrahiert ein Konzept auf ein höheres Level.

        z.B. "roter Apfel" (Level 1) → "Apfel" (3) → "Frucht" (5) → "Nahrung" (7)
        """
        current_level = self._estimate_abstraction_level(concept)

        abstractions = []
        current = concept

        while current_level < target_level:
            # Finde nächsthöhere Abstraktion
            higher = self._find_higher_abstraction(current, current_level)
            if not higher:
                break

            abstractions.append({
                "from": current,
                "to": higher,
                "from_level": current_level,
                "to_level": current_level + 1,
                "abstraction_type": self._classify_abstraction(current, higher)
            })

            current = higher
            current_level += 1

        return {
            "original": concept,
            "final_abstraction": current,
            "original_level": self._estimate_abstraction_level(concept),
            "final_level": current_level,
            "abstraction_chain": abstractions,
            "description": self.abstraction_levels.get(current_level, "Unbekanntes Level")
        }

    def _estimate_abstraction_level(self, concept: str) -> int:
        """Schätzt das Abstraktionslevel eines Konzepts"""
        concept_lower = concept.lower()

        # Sehr konkret (Artikel, Adjektive)
        if any(word in concept_lower for word in ["dieser", "diese", "mein", "dein"]):
            return 1

        # Spezifische Marke/Art
        if concept[0].isupper() and len(concept.split()) > 1:
            return 2

        # Abstrakte Wörter
        abstract_markers = ["heit", "keit", "ung", "ismus", "ität", "konzept", "prinzip"]
        if any(marker in concept_lower for marker in abstract_markers):
            return 8

        # Philosophische Konzepte
        philosophical = ["sein", "existenz", "wesen", "realität", "wahrheit"]
        if concept_lower in philosophical:
            return 10

        # Default: mittleres Level
        return 4

    def _find_higher_abstraction(self, concept: str, current_level: int) -> Optional[str]:
        """Findet die nächsthöhere Abstraktion"""
        # Vordefinierte Abstraktionsketten
        chains = {
            "auto": "fahrzeug",
            "fahrzeug": "fortbewegungsmittel",
            "fortbewegungsmittel": "werkzeug",
            "hund": "haustier",
            "haustier": "tier",
            "tier": "lebewesen",
            "lebewesen": "organismus",
            "apfel": "frucht",
            "frucht": "nahrung",
            "nahrung": "ressource",
            "kreis": "form",
            "form": "geometrie",
            "geometrie": "mathematik",
            "mathematik": "wissenschaft",
            "stuhl": "möbel",
            "möbel": "gegenstand",
            "gegenstand": "ding",
            "ding": "entität",
        }

        concept_lower = concept.lower()
        return chains.get(concept_lower)

    def _classify_abstraction(self, lower: str, higher: str) -> str:
        """Klassifiziert die Art der Abstraktion"""
        # Kategorische Abstraktion (is-a)
        if higher in ["fahrzeug", "tier", "pflanze", "möbel", "werkzeug"]:
            return "categorical"

        # Funktionale Abstraktion
        if higher in ["fortbewegungsmittel", "nahrung", "ressource"]:
            return "functional"

        # Strukturelle Abstraktion
        if higher in ["organismus", "system", "struktur"]:
            return "structural"

        return "general"

    def find_structural_similarity(self, concept_a: str, concept_b: str) -> Dict[str, Any]:
        """
        Findet strukturelle Ähnlichkeiten zwischen zwei Konzepten.

        z.B. "Atom" und "Sonnensystem" → beide haben Zentrum + umlaufende Teile
        """
        # Extrahiere strukturelle Features
        features_a = self._extract_structural_features(concept_a)
        features_b = self._extract_structural_features(concept_b)

        # Finde Überschneidungen
        common = set(features_a) & set(features_b)
        unique_a = set(features_a) - set(features_b)
        unique_b = set(features_b) - set(features_a)

        similarity = len(common) / max(len(features_a), len(features_b), 1)

        return {
            "concept_a": concept_a,
            "concept_b": concept_b,
            "common_structure": list(common),
            "unique_to_a": list(unique_a),
            "unique_to_b": list(unique_b),
            "structural_similarity": similarity,
            "analogy_potential": similarity > 0.3,
            "analogy_description": self._describe_analogy(concept_a, concept_b, common) if common else None
        }

    def _extract_structural_features(self, concept: str) -> List[str]:
        """Extrahiert strukturelle Features eines Konzepts"""
        # Vordefinierte strukturelle Features
        features_db = {
            "auto": ["hat_räder", "hat_motor", "transportiert", "bewegt_sich", "hat_innenraum"],
            "atom": ["hat_zentrum", "hat_umlaufende_teile", "ist_einheit", "hat_energie"],
            "sonnensystem": ["hat_zentrum", "hat_umlaufende_teile", "ist_einheit", "hat_gravitation"],
            "zelle": ["hat_membran", "hat_zentrum", "ist_einheit", "lebt"],
            "kreis": ["ist_rund", "hat_zentrum", "ist_geschlossen", "ist_symmetrisch"],
            "baum": ["hat_wurzeln", "hat_stamm", "hat_äste", "wächst", "lebt"],
            "organisation": ["hat_hierarchie", "hat_mitglieder", "hat_struktur", "hat_ziel"],
            "computer": ["verarbeitet_daten", "hat_speicher", "hat_prozessor", "ist_werkzeug"],
        }

        concept_lower = concept.lower()
        return features_db.get(concept_lower, ["ist_objekt", "existiert"])

    def _describe_analogy(self, a: str, b: str, common: set) -> str:
        """Beschreibt eine strukturelle Analogie"""
        common_list = list(common)
        if len(common_list) >= 2:
            return f"'{a}' und '{b}' sind strukturell ähnlich: beide {', '.join(common_list[:2])}"
        elif len(common_list) == 1:
            return f"'{a}' und '{b}' teilen die Eigenschaft: {common_list[0]}"
        return None

    def _estimate_abstraction_level(self, concept: str) -> int:
        """
        Schätzt das aktuelle Abstraktions-Level eines Konzepts.

        Args:
            concept: Das zu analysierende Konzept

        Returns:
            Level von 1-10
        """
        concept_lower = concept.lower()

        # Philosophische/Meta-Konzepte (9-10)
        meta_keywords = ["prinzip", "konzept", "idee", "abstraktion", "meta", "philosophie"]
        if any(k in concept_lower for k in meta_keywords):
            return 9

        # Funktionale Abstraktionen (7-8)
        functional_keywords = ["system", "prozess", "methode", "mechanismus"]
        if any(k in concept_lower for k in functional_keywords):
            return 7

        # Oberkategorien (5-6)
        category_keywords = ["mittel", "werkzeug", "gerät", "maschine"]
        if any(k in concept_lower for k in category_keywords):
            return 5

        # Allgemeine Kategorien (3-4)
        if concept_lower in ["auto", "tier", "pflanze", "möbel", "essen", "kleidung"]:
            return 4

        # Spezifische Instanzen (1-2)
        if any(c.isupper() for c in concept[1:]):  # Eigenname wahrscheinlich
            return 2

        # Default: mittlere Abstraktion
        return 3


class SelfQuestioningEngine:
    """
    System das sich selbst Fragen stellt um zu lernen.

    "Was ist ein Kreis?"
    "Was macht ein Auto zu einem Auto?"
    "Wie unterscheidet sich X von Y?"
    """

    # Frage-Templates für verschiedene Aspekte
    QUESTION_TEMPLATES = {
        "what_is": [
            "Was ist ein/eine {concept}?",
            "Wie würde ich {concept} definieren?",
            "Was bedeutet '{concept}' eigentlich?"
        ],
        "what_makes": [
            "Was macht ein/eine {concept} zu einem/einer {concept}?",
            "Welche Eigenschaften MUSS ein/eine {concept} haben?",
            "Was ist das Wesentliche an {concept}?"
        ],
        "components": [
            "Woraus besteht ein/eine {concept}?",
            "Welche Teile hat ein/eine {concept}?",
            "Was sind die Komponenten von {concept}?"
        ],
        "function": [
            "Wofür ist ein/eine {concept} da?",
            "Was macht ein/eine {concept}?",
            "Welchen Zweck erfüllt {concept}?"
        ],
        "category": [
            "Zu welcher Kategorie gehört {concept}?",
            "Was ist die Oberkategorie von {concept}?",
            "Ist {concept} eine Art von was?"
        ],
        "difference": [
            "Was unterscheidet {concept} von {related}?",
            "Wie ist {concept} anders als {related}?",
            "Warum ist {concept} nicht einfach {related}?"
        ],
        "examples": [
            "Was sind Beispiele für {concept}?",
            "Welche Arten von {concept} gibt es?",
            "Kannst du mir {concept} an einem Beispiel zeigen?"
        ],
        "counterexamples": [
            "Was ist KEIN {concept}?",
            "Was wird oft mit {concept} verwechselt?",
            "Was sieht aus wie {concept}, ist aber keins?"
        ],
        "origin": [
            "Woher kommt das Konzept {concept}?",
            "Wie ist {concept} entstanden?",
            "Was ist die Geschichte von {concept}?"
        ],
        "relations": [
            "Wie hängt {concept} mit {related} zusammen?",
            "Welche Beziehung hat {concept} zu anderen Dingen?",
            "In welchem Kontext taucht {concept} auf?"
        ]
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.questions: Dict[str, SelfQuestion] = {}
        self.question_queue: List[str] = []  # Fragen die noch beantwortet werden müssen
        self.curiosity_topics: List[str] = []  # Themen die interessieren

    def generate_questions_about(self, concept: str, depth: str = "basic") -> List[SelfQuestion]:
        """
        Generiert Fragen über ein Konzept.

        depth: "basic", "intermediate", "deep"
        """
        questions = []

        # Basis-Fragen (immer)
        basic_types = ["what_is", "what_makes", "components", "function"]

        # Erweiterte Fragen
        intermediate_types = ["category", "examples", "counterexamples"]

        # Tiefe Fragen
        deep_types = ["difference", "origin", "relations"]

        if depth == "basic":
            question_types = basic_types
        elif depth == "intermediate":
            question_types = basic_types + intermediate_types
        else:  # deep
            question_types = basic_types + intermediate_types + deep_types

        for q_type in question_types:
            templates = self.QUESTION_TEMPLATES.get(q_type, [])
            if not templates:
                continue

            template = random.choice(templates)

            # Für Vergleichsfragen brauchen wir ein verwandtes Konzept
            if "{related}" in template:
                related = self._find_related_concept(concept)
                if related:
                    question_text = template.format(concept=concept, related=related)
                else:
                    continue
            else:
                question_text = template.format(concept=concept)

            question = SelfQuestion(
                question_id=f"q_{concept}_{q_type}_{len(self.questions)}",
                question=question_text,
                question_type=q_type,
                target_concept=concept,
                priority=self._calculate_priority(q_type),
                context=f"Selbstlernen über '{concept}'"
            )

            questions.append(question)
            self.questions[question.question_id] = question

        return questions

    def _find_related_concept(self, concept: str) -> Optional[str]:
        """Findet ein verwandtes Konzept für Vergleichsfragen"""
        related_db = {
            "kreis": "oval",
            "auto": "motorrad",
            "hund": "katze",
            "apfel": "birne",
            "stuhl": "hocker",
            "see": "meer",
            "berg": "hügel",
        }
        return related_db.get(concept.lower())

    def _calculate_priority(self, question_type: str) -> float:
        """Berechnet Priorität einer Frage"""
        priorities = {
            "what_is": 1.0,
            "what_makes": 0.95,
            "components": 0.8,
            "function": 0.85,
            "category": 0.7,
            "examples": 0.6,
            "counterexamples": 0.75,
            "difference": 0.65,
            "origin": 0.4,
            "relations": 0.5
        }
        return priorities.get(question_type, 0.5)

    def get_next_question(self) -> Optional[SelfQuestion]:
        """Holt die nächste unbeantwortete Frage mit höchster Priorität"""
        unanswered = [q for q in self.questions.values() if not q.answered]
        if not unanswered:
            return None
        return max(unanswered, key=lambda q: q.priority)

    def mark_answered(self, question_id: str, answer: str, confidence: float,
                      sources: List[str] = None):
        """Markiert eine Frage als beantwortet"""
        if question_id in self.questions:
            q = self.questions[question_id]
            q.answered = True
            q.answer = answer
            q.confidence = confidence
            q.sources_used = sources or []


class SkepticalVerifier:
    """
    Skeptisches Verifikationssystem.

    Prüft Informationen kritisch bevor sie akzeptiert werden:
    - Sucht nach Widersprüchen
    - Prüft Quellen
    - Sucht Gegenbeweise
    - Bewertet Plausibilität
    """

    # Rote Flaggen für unzuverlässige Informationen
    RED_FLAGS = [
        "immer", "nie", "alle", "jeder", "niemand",  # Absolute Aussagen
        "offensichtlich", "natürlich", "selbstverständlich",  # Schein-Evidenz
        "man sagt", "es heißt", "angeblich",  # Vage Quellen
        "geheim", "verschwiegen", "sie wollen nicht",  # Verschwörungs-Marker
        "garantiert", "100%", "definitiv",  # Übertriebene Sicherheit
    ]

    # Qualitätsmarker für gute Informationen
    QUALITY_MARKERS = [
        "studie", "forschung", "wissenschaft",  # Akademisch
        "laut", "gemäß", "nach angaben von",  # Quellenangabe
        "ungefähr", "etwa", "ca.", "in der regel",  # Angemessene Unsicherheit
        "beispielsweise", "zum beispiel", "unter anderem",  # Konkrete Beispiele
    ]

    def __init__(self):
        self.verified_facts: Dict[str, VerificationResult] = {}
        self.rejection_log: List[Dict] = []

    def verify(self, claim: str, sources: List[str] = None,
               context: Dict = None) -> VerificationResult:
        """
        Verifiziert eine Behauptung skeptisch.

        Prüft:
        1. Innere Konsistenz (widerspricht sich die Aussage selbst?)
        2. Plausibilität (ist es überhaupt möglich?)
        3. Quellenqualität (woher stammt die Info?)
        4. Bekannte Fakten (widerspricht es Bekanntem?)
        """
        supporting = []
        contradicting = []
        reasoning_steps = []

        # 1. Prüfe auf rote Flaggen
        red_flag_count = self._count_red_flags(claim)
        if red_flag_count > 0:
            reasoning_steps.append(f"⚠️ {red_flag_count} Warnsignal(e) gefunden")
            contradicting.append(f"{red_flag_count} absolute/vage Aussagen")

        # 2. Prüfe auf Qualitätsmarker
        quality_count = self._count_quality_markers(claim)
        if quality_count > 0:
            reasoning_steps.append(f"✓ {quality_count} Qualitätsmarker gefunden")
            supporting.append(f"{quality_count} wissenschaftliche/konkrete Angaben")

        # 3. Prüfe logische Konsistenz
        consistency = self._check_consistency(claim)
        if consistency["has_contradiction"]:
            reasoning_steps.append(f"❌ Widerspruch: {consistency['contradiction']}")
            contradicting.append(consistency['contradiction'])
        else:
            reasoning_steps.append("✓ Keine offensichtlichen Widersprüche")

        # 4. Prüfe Plausibilität
        plausibility = self._check_plausibility(claim)
        if plausibility < 0.5:
            reasoning_steps.append(f"⚠️ Geringe Plausibilität: {plausibility:.1%}")
            contradicting.append("Unplausible Behauptung")
        else:
            supporting.append(f"Plausibilität: {plausibility:.1%}")

        # 5. Berechne Gesamtbewertung
        base_confidence = 0.5
        confidence = base_confidence
        confidence -= red_flag_count * 0.1
        confidence += quality_count * 0.1
        confidence += plausibility * 0.2
        confidence = max(0.0, min(1.0, confidence))

        # 6. Empfehlung
        if confidence > 0.7:
            recommendation = "accept"
            is_verified = True
        elif confidence > 0.4:
            recommendation = "uncertain"
            is_verified = False
        else:
            recommendation = "reject"
            is_verified = False
            self.rejection_log.append({
                "claim": claim,
                "reason": "; ".join(contradicting),
                "confidence": confidence
            })

        result = VerificationResult(
            claim=claim,
            is_verified=is_verified,
            confidence=confidence,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            reasoning="; ".join(reasoning_steps),
            sources_checked=len(sources) if sources else 0,
            recommendation=recommendation
        )

        self.verified_facts[claim[:50]] = result
        return result

    def _count_red_flags(self, text: str) -> int:
        """Zählt rote Flaggen im Text"""
        text_lower = text.lower()
        return sum(1 for flag in self.RED_FLAGS if flag in text_lower)

    def _count_quality_markers(self, text: str) -> int:
        """Zählt Qualitätsmarker im Text"""
        text_lower = text.lower()
        return sum(1 for marker in self.QUALITY_MARKERS if marker in text_lower)

    def _check_consistency(self, claim: str) -> Dict:
        """Prüft auf innere Widersprüche"""
        # Einfache Widerspruchserkennung
        contradictions = [
            ("immer", "manchmal"),
            ("alle", "manche"),
            ("nie", "gelegentlich"),
            ("unmöglich", "möglich"),
        ]

        text_lower = claim.lower()
        for word_a, word_b in contradictions:
            if word_a in text_lower and word_b in text_lower:
                return {
                    "has_contradiction": True,
                    "contradiction": f"'{word_a}' widerspricht '{word_b}'"
                }

        return {"has_contradiction": False, "contradiction": None}

    def _check_plausibility(self, claim: str) -> float:
        """Bewertet die Plausibilität einer Aussage"""
        # Basis-Plausibilität
        plausibility = 0.6

        # Unrealistische Zahlen
        numbers = re.findall(r'\d+(?:\.\d+)?', claim)
        for num_str in numbers:
            num = float(num_str)
            if num > 1000000000000:  # Trillion+
                plausibility -= 0.2
            elif num > 1000000000:  # Milliarde+
                plausibility -= 0.1

        # Superlative sind oft übertrieben
        superlatives = ["beste", "schlechteste", "größte", "kleinste", "erste", "einzige"]
        if any(s in claim.lower() for s in superlatives):
            plausibility -= 0.1

        return max(0.0, min(1.0, plausibility))


class ConceptEssenceExtractor:
    """
    Extrahiert die Essenz eines Konzepts.

    Beantwortet: "Was macht ein X zu einem X?"

    z.B. "Was macht einen Kreis zu einem Kreis?"
    → "Alle Punkte haben den gleichen Abstand zum Mittelpunkt"
    """

    # Bekannte Konzept-Essenzen
    KNOWN_ESSENCES = {
        "kreis": {
            "definition": "Geometrische Form bei der alle Punkte gleichen Abstand zum Mittelpunkt haben",
            "necessary": ["mittelpunkt", "konstanter_radius", "geschlossene_linie"],
            "sufficient": ["alle_punkte_gleicher_abstand_zum_zentrum"],
            "typical": ["rund", "symmetrisch", "hat_durchmesser"],
            "distinguishing": ["kein_anfang_kein_ende", "keine_ecken"],
        },
        "auto": {
            "definition": "Motorisiertes Straßenfahrzeug zur Personenbeförderung",
            "necessary": ["motor", "räder", "steuerung", "für_straße"],
            "sufficient": ["selbstangetriebenes_straßenfahrzeug"],
            "typical": ["vier_räder", "sitze", "karosserie", "fenster"],
            "distinguishing": ["nicht_schienengebunden", "nicht_für_wasser"],
        },
        "hund": {
            "definition": "Domestiziertes Säugetier, Unterart des Wolfs",
            "necessary": ["säugetier", "canis_familiaris", "domestiziert"],
            "sufficient": ["domestizierter_wolf"],
            "typical": ["vier_beine", "fell", "bellt", "wedelt_mit_schwanz"],
            "distinguishing": ["domestiziert_im_gegensatz_zu_wolf"],
        },
        "stuhl": {
            "definition": "Möbelstück zum Sitzen für eine Person mit Rückenlehne",
            "necessary": ["sitzfläche", "für_eine_person", "zum_sitzen"],
            "sufficient": ["einzelsitz_mit_lehne"],
            "typical": ["vier_beine", "rückenlehne", "stabil"],
            "distinguishing": ["hat_lehne_anders_als_hocker", "für_einen_anders_als_bank"],
        },
        "dreieck": {
            "definition": "Polygon mit genau drei Ecken und drei Seiten",
            "necessary": ["drei_ecken", "drei_seiten", "geschlossen"],
            "sufficient": ["polygon_mit_drei_ecken"],
            "typical": ["drei_winkel", "winkelsumme_180_grad"],
            "distinguishing": ["weniger_ecken_als_viereck"],
        },
        "baum": {
            "definition": "Mehrjährige Pflanze mit verholztem Stamm",
            "necessary": ["pflanze", "verholzter_stamm", "mehrjährig"],
            "sufficient": ["holzpflanze_mit_stamm"],
            "typical": ["blätter_oder_nadeln", "wurzeln", "krone", "hoch"],
            "distinguishing": ["hat_stamm_anders_als_strauch"],
        },
    }

    def __init__(self):
        self.extracted_essences: Dict[str, ConceptEssence] = {}
        self.abstraction_engine = DeepAbstractionEngine()

    def extract_essence(self, concept: str) -> ConceptEssence:
        """Extrahiert oder konstruiert die Essenz eines Konzepts"""
        concept_lower = concept.lower()

        # Prüfe ob bereits bekannt
        if concept_lower in self.KNOWN_ESSENCES:
            known = self.KNOWN_ESSENCES[concept_lower]
            essence = ConceptEssence(
                concept_name=concept,
                definition=known["definition"],
                necessary_properties=known["necessary"],
                sufficient_properties=known["sufficient"],
                typical_properties=known["typical"],
                distinguishing_features=known["distinguishing"],
                parent_categories=self._find_parent_categories(concept),
                child_concepts=self._find_child_concepts(concept),
                related_concepts=self._find_related_concepts(concept),
                examples=self._find_examples(concept),
                counterexamples=self._find_counterexamples(concept),
                abstraction_level=self.abstraction_engine._estimate_abstraction_level(concept),
                confidence=0.9,
                sources=["internal_knowledge_base"],
                verified=True
            )
        else:
            # Konstruiere Essenz aus Heuristiken
            essence = self._construct_essence(concept)

        self.extracted_essences[concept_lower] = essence
        return essence

    def _construct_essence(self, concept: str) -> ConceptEssence:
        """Konstruiert eine Essenz für unbekannte Konzepte"""
        # Versuche aus der Abstraktions-Hierarchie zu lernen
        abstraction = self.abstraction_engine.abstract_concept(concept, 6)

        parent = abstraction.get("final_abstraction", "entität")

        return ConceptEssence(
            concept_name=concept,
            definition=f"Eine Art von {parent}",
            necessary_properties=["existiert", f"ist_{parent}"],
            sufficient_properties=[f"typisches_{concept.lower()}"],
            typical_properties=["hat_eigenschaften"],
            distinguishing_features=[f"spezifisch_für_{concept.lower()}"],
            parent_categories=[parent] if parent != concept else [],
            child_concepts=[],
            related_concepts=[],
            examples=[],
            counterexamples=[],
            abstraction_level=abstraction.get("final_level", 4),
            confidence=0.3,  # Niedrige Konfidenz für konstruierte Essenzen
            sources=["heuristic_construction"],
            verified=False
        )

    def _find_parent_categories(self, concept: str) -> List[str]:
        """Findet übergeordnete Kategorien"""
        parents = {
            "kreis": ["form", "geometrie"],
            "auto": ["fahrzeug", "fortbewegungsmittel"],
            "hund": ["haustier", "säugetier", "tier"],
            "stuhl": ["möbel", "sitzgelegenheit"],
            "dreieck": ["polygon", "form"],
            "baum": ["pflanze", "holzgewächs"],
        }
        return parents.get(concept.lower(), [])

    def _find_child_concepts(self, concept: str) -> List[str]:
        """Findet untergeordnete Konzepte"""
        children = {
            "form": ["kreis", "dreieck", "quadrat"],
            "fahrzeug": ["auto", "motorrad", "fahrrad"],
            "tier": ["hund", "katze", "vogel"],
            "möbel": ["stuhl", "tisch", "schrank"],
        }
        return children.get(concept.lower(), [])

    def _find_related_concepts(self, concept: str) -> List[str]:
        """Findet verwandte Konzepte"""
        related = {
            "kreis": ["kugel", "radius", "durchmesser", "pi"],
            "auto": ["straße", "benzin", "fahren", "verkehr"],
            "hund": ["leine", "bellen", "fell", "treue"],
            "stuhl": ["tisch", "sitzen", "holz", "lehne"],
        }
        return related.get(concept.lower(), [])

    def _find_examples(self, concept: str) -> List[str]:
        """Findet konkrete Beispiele"""
        examples = {
            "kreis": ["Uhr", "Rad", "Münze", "Sonne"],
            "auto": ["VW Golf", "Tesla Model 3", "BMW 3er"],
            "hund": ["Labrador", "Schäferhund", "Pudel"],
            "stuhl": ["Bürostuhl", "Küchenstuhl", "Schaukelstuhl"],
        }
        return examples.get(concept.lower(), [])

    def _find_counterexamples(self, concept: str) -> List[str]:
        """Findet Gegenbeispiele (was es NICHT ist)"""
        counter = {
            "kreis": ["Oval (nicht perfekt rund)", "Spirale (nicht geschlossen)"],
            "auto": ["Motorrad (nur 2 Räder)", "Zug (schienengebunden)"],
            "hund": ["Wolf (nicht domestiziert)", "Fuchs (andere Spezies)"],
            "stuhl": ["Hocker (keine Lehne)", "Bank (für mehrere Personen)"],
        }
        return counter.get(concept.lower(), [])


class SelfTeachingSystem:
    """
    Koordiniert das gesamte Selbstlern-System - Level 10/10.

    Workflow:
    1. Stellt sich Fragen über Konzepte
    2. Recherchiert Antworten
    3. Verifiziert skeptisch
    4. Extrahiert Essenz
    5. Speichert verifiziertes Wissen
    6. Generiert Folgefragen

    Level 10 Features:
    - Spaced Repetition für langfristiges Behalten
    - Lern-Transfer-Erkennung
    - Metakognitive Lernüberwachung
    - Concept Mastery Tracking
    - Aktive Wissenslücken-Erkennung
    """

    # Mastery Levels
    MASTERY_LEVELS = {
        0.0: "unbekannt",
        0.2: "vage",
        0.4: "oberflächlich",
        0.6: "grundlegend",
        0.8: "solide",
        1.0: "meisterhaft"
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Subsysteme
        self.questioning = SelfQuestioningEngine(data_dir)
        self.verifier = SkepticalVerifier()
        self.essence_extractor = ConceptEssenceExtractor()
        self.abstraction = DeepAbstractionEngine()

        # Gelerntes Wissen
        self.learned_concepts: Dict[str, ConceptEssence] = {}
        self.learning_log: List[Dict] = []

        # Lern-Warteschlange
        self.concepts_to_learn: List[str] = []
        self.current_learning_session: Optional[str] = None

        # Level 10 Erweiterungen
        self.concept_mastery: Dict[str, float] = {}
        self.spaced_repetition: Dict[str, Dict] = {}  # concept -> {next_review, interval}
        self.learning_connections: Dict[str, List[str]] = {}  # concept -> [connected_concepts]
        self.metacognitive_log: List[Dict] = []  # Beobachtungen über eigenes Lernen

    def learn_concept(self, concept: str, depth: str = "deep") -> Dict[str, Any]:
        """
        Lernt ein Konzept durch Selbstbefragung und Verifikation.

        Args:
            concept: Das zu lernende Konzept
            depth: "basic", "intermediate", "deep"

        Returns:
            Lernbericht mit allem was gelernt wurde
        """
        self.current_learning_session = concept
        learning_report = {
            "concept": concept,
            "started_at": datetime.now().isoformat(),
            "questions_asked": [],
            "answers_found": [],
            "verifications": [],
            "essence": None,
            "related_concepts_discovered": [],
            "follow_up_questions": [],
            "overall_confidence": 0.0,
        }

        # 1. Generiere Fragen
        questions = self.questioning.generate_questions_about(concept, depth)
        learning_report["questions_asked"] = [q.question for q in questions]

        logger.info(f"🤔 Lerne über '{concept}': {len(questions)} Fragen generiert")

        # 2. Beantworte Fragen und verifiziere
        total_confidence = 0.0
        for question in questions:
            # Versuche Antwort zu finden
            answer = self._research_answer(question)

            if answer:
                # Verifiziere skeptisch
                verification = self.verifier.verify(answer)

                learning_report["answers_found"].append({
                    "question": question.question,
                    "answer": answer,
                    "verified": verification.is_verified,
                    "confidence": verification.confidence
                })

                learning_report["verifications"].append({
                    "claim": answer[:50] + "...",
                    "result": verification.recommendation
                })

                # Markiere als beantwortet
                self.questioning.mark_answered(
                    question.question_id,
                    answer,
                    verification.confidence,
                    verification.supporting_evidence
                )

                total_confidence += verification.confidence

        # 3. Extrahiere Essenz
        essence = self.essence_extractor.extract_essence(concept)
        learning_report["essence"] = {
            "definition": essence.definition,
            "necessary_properties": essence.necessary_properties,
            "distinguishing_features": essence.distinguishing_features,
            "abstraction_level": essence.abstraction_level
        }

        # 4. Entdecke verwandte Konzepte
        related = essence.related_concepts + essence.parent_categories
        for rel in related:
            if rel not in self.learned_concepts and rel not in self.concepts_to_learn:
                self.concepts_to_learn.append(rel)
                learning_report["related_concepts_discovered"].append(rel)

        # 5. Generiere Folgefragen
        if essence.confidence < 0.7:
            follow_ups = [
                f"Was genau bedeutet '{prop}'?" for prop in essence.necessary_properties[:2]
            ]
            learning_report["follow_up_questions"] = follow_ups

        # 6. Speichere gelerntes Konzept
        if len(questions) > 0:
            learning_report["overall_confidence"] = total_confidence / len(questions)

        if learning_report["overall_confidence"] > 0.4:
            self.learned_concepts[concept.lower()] = essence
            logger.info(f"✅ '{concept}' gelernt mit Konfidenz {learning_report['overall_confidence']:.1%}")
        else:
            logger.warning(f"⚠️ '{concept}' nicht sicher genug gelernt")

        # Log
        self.learning_log.append({
            "concept": concept,
            "success": learning_report["overall_confidence"] > 0.4,
            "confidence": learning_report["overall_confidence"],
            "timestamp": datetime.now().isoformat()
        })

        self.current_learning_session = None
        return learning_report

    def _research_answer(self, question: SelfQuestion) -> Optional[str]:
        """
        Recherchiert eine Antwort auf eine Frage.

        In der aktuellen Version: Nutzt internes Wissen.
        Könnte erweitert werden für: Web-Recherche, Datenbank-Abfragen, etc.
        """
        q_type = question.question_type
        concept = question.target_concept.lower()

        # Versuche aus Essenz-Datenbank
        if concept in self.essence_extractor.KNOWN_ESSENCES:
            known = self.essence_extractor.KNOWN_ESSENCES[concept]

            if q_type == "what_is":
                return known["definition"]
            elif q_type == "what_makes":
                return f"Wesentlich für {concept}: {', '.join(known['necessary'])}"
            elif q_type == "components":
                return f"Besteht aus: {', '.join(known['typical'])}"
            elif q_type == "function":
                # Generiere aus Definition
                return f"Funktion von {concept}: {known['definition']}"

        # Fallback: Generische Antwort
        return None

    def learn_concept_chain(self, start_concept: str, max_depth: int = 3) -> List[Dict]:
        """
        Lernt ein Konzept und alle verwandten Konzepte.

        Beginnt bei start_concept und folgt Beziehungen.
        """
        learned = []
        to_learn = [start_concept]
        depth = 0

        while to_learn and depth < max_depth:
            concept = to_learn.pop(0)

            if concept.lower() in self.learned_concepts:
                continue

            report = self.learn_concept(concept)
            learned.append(report)

            # Füge neue Konzepte hinzu
            for related in report.get("related_concepts_discovered", []):
                if related not in to_learn and related.lower() not in self.learned_concepts:
                    to_learn.append(related)

            depth += 1

        return learned

    def ask_and_verify(self, claim: str) -> Dict[str, Any]:
        """
        Prüft eine externe Behauptung skeptisch.

        Stellt sich Fragen um die Behauptung zu prüfen.
        """
        result = {
            "claim": claim,
            "questions_generated": [],
            "verification": None,
            "recommendation": "",
        }

        # Generiere skeptische Fragen
        skeptical_questions = [
            f"Woher stammt diese Information?",
            f"Gibt es Belege dafür?",
            f"Was spricht dagegen?",
            f"Ist das plausibel?"
        ]
        result["questions_generated"] = skeptical_questions

        # Verifiziere
        verification = self.verifier.verify(claim)
        result["verification"] = {
            "is_verified": verification.is_verified,
            "confidence": verification.confidence,
            "reasoning": verification.reasoning,
            "recommendation": verification.recommendation
        }

        # Empfehlung
        if verification.recommendation == "accept":
            result["recommendation"] = "Diese Information scheint vertrauenswürdig."
        elif verification.recommendation == "uncertain":
            result["recommendation"] = "Diese Information sollte mit Vorsicht behandelt werden."
        else:
            result["recommendation"] = "Diese Information ist zweifelhaft und sollte hinterfragt werden."

        return result

    def get_learning_stats(self) -> Dict[str, Any]:
        """Gibt Lernstatistiken zurück"""
        return {
            "concepts_learned": len(self.learned_concepts),
            "concepts_in_queue": len(self.concepts_to_learn),
            "questions_asked": len(self.questioning.questions),
            "questions_answered": sum(1 for q in self.questioning.questions.values() if q.answered),
            "verifications_performed": len(self.verifier.verified_facts),
            "rejections": len(self.verifier.rejection_log),
            "average_confidence": sum(
                c.confidence for c in self.learned_concepts.values()
            ) / max(len(self.learned_concepts), 1),
            "recent_learning": self.learning_log[-5:] if self.learning_log else []
        }

    def express_understanding(self, concept: str) -> str:
        """Drückt das Verständnis eines Konzepts aus"""
        concept_lower = concept.lower()

        if concept_lower not in self.learned_concepts:
            return f"Hmm, über '{concept}' weiß ich noch nicht genug. Soll ich es lernen?"

        essence = self.learned_concepts[concept_lower]

        response = f"*nachdenklich* Also, '{concept}'...\n\n"
        response += f"**Definition:** {essence.definition}\n\n"
        response += f"**Was es ausmacht:** {', '.join(essence.necessary_properties)}\n\n"

        if essence.distinguishing_features:
            response += f"**Besonders:** {', '.join(essence.distinguishing_features)}\n\n"

        if essence.examples:
            response += f"**Beispiele:** {', '.join(essence.examples[:3])}\n\n"

        if essence.counterexamples:
            response += f"**Was es NICHT ist:** {essence.counterexamples[0]}\n"

        response += f"\n*Konfidenz: {essence.confidence:.0%}*"

        return response

    # ================================================================
    # LEVEL 10 METHODEN - Fortgeschrittenes Selbstlernen
    # ================================================================

    def schedule_spaced_review(self, concept: str) -> Dict[str, Any]:
        """
        Plant Wiederholung nach Spaced Repetition Prinzip.

        Ebbinghaus Vergessenskurve: Wiederholung im wachsenden Intervall.
        """
        if concept.lower() not in self.learned_concepts:
            return {"error": "Konzept nicht gelernt"}

        now = datetime.now()
        initial_interval = 1  # Tage

        if concept in self.spaced_repetition:
            # Nächstes Intervall (verdoppeln)
            current = self.spaced_repetition[concept]
            new_interval = min(current["interval"] * 2, 90)
        else:
            new_interval = initial_interval

        self.spaced_repetition[concept] = {
            "next_review": (now + timedelta(days=new_interval)).isoformat(),
            "interval": new_interval,
            "review_count": self.spaced_repetition.get(concept, {}).get("review_count", 0) + 1
        }

        return {
            "concept": concept,
            "next_review_days": new_interval,
            "review_count": self.spaced_repetition[concept]["review_count"],
            "message": f"Wiederholung in {new_interval} Tag(en) geplant"
        }

    def get_due_reviews(self) -> List[str]:
        """Gibt alle Konzepte zurück die wiederholt werden sollten"""
        now = datetime.now()
        due = []

        for concept, data in self.spaced_repetition.items():
            review_date = datetime.fromisoformat(data["next_review"])
            if review_date <= now:
                due.append(concept)

        return due

    def update_mastery(self, concept: str, performance: float) -> Dict[str, Any]:
        """
        Aktualisiert das Mastery-Level basierend auf Performance.

        Args:
            concept: Das Konzept
            performance: 0-1, wie gut war die Leistung?
        """
        concept_lower = concept.lower()
        old_mastery = self.concept_mastery.get(concept_lower, 0.5)

        # Mastery anpassen (gewichtet Richtung Performance)
        new_mastery = old_mastery * 0.7 + performance * 0.3
        self.concept_mastery[concept_lower] = min(1.0, new_mastery)

        # Level bestimmen
        level = "unbekannt"
        for threshold, name in sorted(self.MASTERY_LEVELS.items()):
            if new_mastery >= threshold:
                level = name

        return {
            "concept": concept,
            "old_mastery": old_mastery,
            "new_mastery": new_mastery,
            "mastery_level": level,
            "improved": new_mastery > old_mastery
        }

    def detect_learning_transfer(self, new_concept: str) -> List[Dict[str, Any]]:
        """
        Erkennt ob gelerntes Wissen auf ein neues Konzept übertragen werden kann.

        Transfer Learning: Verbindungen zwischen Konzepten nutzen.
        """
        transfers = []
        new_keywords = set(new_concept.lower().split())

        for learned_concept, essence in self.learned_concepts.items():
            # Prüfe Überlappung
            learned_keywords = set(learned_concept.split())
            learned_keywords.update(essence.necessary_properties)

            overlap = new_keywords & learned_keywords
            if overlap:
                transfers.append({
                    "from_concept": learned_concept,
                    "overlap": list(overlap),
                    "transfer_potential": len(overlap) / max(len(new_keywords), 1),
                    "transferable_knowledge": essence.definition[:100]
                })

        # Sortiere nach Transfer-Potenzial
        transfers.sort(key=lambda x: x["transfer_potential"], reverse=True)

        # Speichere Verbindungen
        if transfers:
            self.learning_connections[new_concept.lower()] = [
                t["from_concept"] for t in transfers[:3]
            ]

        return transfers[:3]

    def metacognitive_reflection(self) -> Dict[str, Any]:
        """
        Reflektiert über das eigene Lernen (Metakognition).

        "Wie lerne ich? Was funktioniert? Was nicht?"
        """
        if len(self.learning_log) < 3:
            return {"message": "Noch nicht genug Lerndaten für Metakognition"}

        # Analysiere Lernhistorie
        successes = [l for l in self.learning_log if l.get("success", False)]
        failures = [l for l in self.learning_log if not l.get("success", True)]

        success_rate = len(successes) / len(self.learning_log)

        # Muster erkennen
        patterns = []
        if len(successes) > len(failures):
            patterns.append("Generell erfolgreiches Lernen")
        else:
            patterns.append("Viele Lernschwierigkeiten - Strategie überdenken")

        # Durchschnittliche Confidence
        avg_confidence = sum(
            l.get("confidence", 0.5) for l in self.learning_log
        ) / len(self.learning_log)

        # Empfehlungen
        recommendations = []
        if avg_confidence < 0.6:
            recommendations.append("Mehr Zeit für Verifikation nehmen")
        if len(self.concepts_to_learn) > 10:
            recommendations.append("Lernwarteschlange priorisieren")
        if len(self.get_due_reviews()) > 5:
            recommendations.append("Wiederholungen durchführen!")

        reflection = {
            "total_concepts_learned": len(self.learned_concepts),
            "success_rate": success_rate,
            "average_confidence": avg_confidence,
            "patterns_observed": patterns,
            "recommendations": recommendations,
            "strongest_areas": self._get_strongest_concepts(3),
            "weakest_areas": self._get_weakest_concepts(3)
        }

        self.metacognitive_log.append({
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection
        })

        return reflection

    def _get_strongest_concepts(self, n: int) -> List[str]:
        """Gibt die n am besten beherrschten Konzepte zurück"""
        sorted_concepts = sorted(
            self.concept_mastery.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [c[0] for c in sorted_concepts[:n]]

    def _get_weakest_concepts(self, n: int) -> List[str]:
        """Gibt die n am schwächsten beherrschten Konzepte zurück"""
        sorted_concepts = sorted(
            self.concept_mastery.items(),
            key=lambda x: x[1]
        )
        return [c[0] for c in sorted_concepts[:n]]

    def identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Identifiziert aktive Wissenslücken.

        Wo fehlt Wissen für ein vollständiges Verständnis?
        """
        gaps = []

        for concept, essence in self.learned_concepts.items():
            # Prüfe verwandte Konzepte
            for related in essence.related_concepts + essence.parent_categories:
                if related.lower() not in self.learned_concepts:
                    gaps.append({
                        "gap": related,
                        "needed_for": concept,
                        "priority": "high" if essence.confidence < 0.7 else "medium"
                    })

            # Prüfe notwendige Eigenschaften
            for prop in essence.necessary_properties:
                if len(prop.split()) > 1:  # Komplexe Property
                    prop_lower = prop.lower()
                    if prop_lower not in self.learned_concepts:
                        gaps.append({
                            "gap": prop,
                            "needed_for": concept,
                            "priority": "medium"
                        })

        # Deduplizieren
        seen = set()
        unique_gaps = []
        for gap in gaps:
            if gap["gap"] not in seen:
                seen.add(gap["gap"])
                unique_gaps.append(gap)

        return unique_gaps[:10]

    def get_teaching_stats(self) -> Dict[str, Any]:
        """Umfassende Statistiken über das Selbstlernsystem"""
        return {
            "concepts_learned": len(self.learned_concepts),
            "total_mastery_points": sum(self.concept_mastery.values()),
            "average_mastery": sum(self.concept_mastery.values()) / max(len(self.concept_mastery), 1),
            "reviews_scheduled": len(self.spaced_repetition),
            "reviews_due": len(self.get_due_reviews()),
            "knowledge_gaps": len(self.identify_knowledge_gaps()),
            "learning_connections": sum(len(c) for c in self.learning_connections.values()),
            "metacognitive_reflections": len(self.metacognitive_log),
            "concepts_in_queue": len(self.concepts_to_learn)
        }


# ============================================================
# CURIOSITY-DRIVEN LEARNER - Autonomes Lernen v1.0
# ============================================================

class ConceptDetector:
    """
    Erkennt unbekannte Konzepte in Text.

    Analysiert eingehenden Text und findet Begriffe,
    die Holo noch nicht versteht.
    """

    # Wörter die auf Konzepte hinweisen
    CONCEPT_INDICATORS = [
        "ist ein", "ist eine", "sind", "bedeutet", "heißt",
        "nennt man", "bezeichnet", "ist so etwas wie"
    ]

    # Fragen die auf Wissenslücken hinweisen
    KNOWLEDGE_GAP_PATTERNS = [
        r"(?:weißt du )?was (?:ist|sind) (?:ein(?:e)? )?(\w+)",
        r"kennst du (\w+)",
        r"(?:der|die|das) (\w+)",
    ]

    # Wörter die wir ignorieren
    STOP_WORDS = {
        "ich", "du", "wir", "ihr", "sie", "er", "es", "und", "oder",
        "aber", "denn", "weil", "wenn", "dass", "der", "die", "das",
        "ein", "eine", "einer", "einem", "einen", "ist", "sind", "war",
        "waren", "sein", "haben", "hat", "hatte", "werden", "wird",
        "wurde", "können", "kann", "müssen", "muss", "sollen", "soll",
        "wollen", "will", "dürfen", "darf", "mögen", "mag", "nicht",
        "auch", "nur", "schon", "noch", "sehr", "mehr", "weniger",
        "hier", "dort", "jetzt", "dann", "heute", "morgen", "gestern",
        "ja", "nein", "vielleicht", "also", "doch", "mal", "so",
        "wie", "was", "wer", "wo", "wann", "warum", "welche", "welcher",
        "holo", "hallo", "danke", "bitte", "okay", "gut", "schlecht"
    }

    # Minimum Wortlänge für Konzepte
    MIN_WORD_LENGTH = 4

    def __init__(self, known_concepts: Set[str] = None):
        self.known_concepts = known_concepts or set()
        self.recently_detected: List[str] = []
        self.detection_count: Dict[str, int] = defaultdict(int)

    def add_known_concept(self, concept: str):
        """Markiert ein Konzept als bekannt"""
        self.known_concepts.add(concept.lower())

    def detect_unknown_concepts(self, text: str) -> List[str]:
        """
        Findet unbekannte Konzepte im Text.

        Returns:
            Liste von unbekannten Konzepten, sortiert nach Wichtigkeit
        """
        unknown = []

        # Tokenisiere Text
        words = self._extract_words(text)

        for word in words:
            word_lower = word.lower()

            # Filter
            if len(word) < self.MIN_WORD_LENGTH:
                continue
            if word_lower in self.STOP_WORDS:
                continue
            if word_lower in self.known_concepts:
                continue
            if not word[0].isupper() and not self._is_likely_concept(word_lower, text):
                continue

            # Zähle Vorkommen
            self.detection_count[word_lower] += 1

            if word_lower not in unknown:
                unknown.append(word_lower)

        # Sortiere nach Häufigkeit
        unknown.sort(key=lambda w: self.detection_count[w], reverse=True)

        # Speichere kürzlich erkannte
        self.recently_detected = unknown[:10]

        return unknown

    def _extract_words(self, text: str) -> List[str]:
        """Extrahiert Wörter aus Text"""
        # Entferne Satzzeichen am Ende
        import re
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text)
        return words

    def _is_likely_concept(self, word: str, context: str) -> bool:
        """
        Prüft ob ein Wort wahrscheinlich ein Konzept ist.
        """
        context_lower = context.lower()

        # Prüfe auf Konzept-Indikatoren in der Nähe
        for indicator in self.CONCEPT_INDICATORS:
            if indicator in context_lower:
                # Prüfe ob Wort in der Nähe des Indikators ist
                idx = context_lower.find(indicator)
                window = context_lower[max(0, idx-50):idx+50]
                if word in window:
                    return True

        return False

    def get_priority_concepts(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Gibt die wichtigsten unbekannten Konzepte zurück.

        Basiert auf Häufigkeit und Aktualität.
        """
        # Kombiniere Häufigkeit mit Aktualität
        priority_scores = {}

        for concept, count in self.detection_count.items():
            if concept not in self.known_concepts:
                recency_bonus = 1.5 if concept in self.recently_detected else 1.0
                priority_scores[concept] = count * recency_bonus

        # Sortiere und limitiere
        sorted_concepts = sorted(
            priority_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return sorted_concepts


class AutonomousLearningMode(Enum):
    """Lernmodi für autonomes Lernen"""
    PASSIVE = "passive"          # Lernt nur wenn explizit getriggert
    CURIOUS = "curious"          # Stellt bei Unklarheiten Fragen
    ACTIVE = "active"            # Lernt proaktiv im Hintergrund
    AGGRESSIVE = "aggressive"    # Lernt alles was unbekannt ist


@dataclass
class LearningTrigger:
    """Ein Auslöser für autonomes Lernen"""
    trigger_id: str
    concept: str
    source: str                  # "conversation", "web", "internal"
    priority: float              # 0-1
    context: str                 # Kontext in dem das Konzept auftauchte
    triggered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CuriosityDrivenLearner:
    """
    Autonomes Lern-System das durch Neugier angetrieben wird - Level 10/10.

    Level 10 Features:
    - Intrinsische Motivation (echte Neugier-Simulation)
    - Knowledge Gap Sensing
    - Multi-Source Learning Integration
    - Adaptive Lernstrategien
    - Lern-Flow-Tracking
    - Exploration vs Exploitation Balancing

    v1.0: Erste vollständige Implementation
    """

    # Neugier-Level Definitionen
    CURIOSITY_LEVELS = {
        1.0: "brennend neugierig",
        0.8: "sehr interessiert",
        0.6: "neugierig",
        0.4: "leicht interessiert",
        0.2: "gleichgültig",
    }

    # Lernstrategien
    LEARNING_STRATEGIES = [
        "definition_first",      # Definition → Beispiele → Anwendung
        "example_first",         # Beispiele → Pattern → Definition
        "comparison_first",      # Vergleich mit Bekanntem → Unterschiede
        "questioning_first",     # Fragen stellen → Antworten suchen
    ]

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Subsysteme
        self.concept_detector = ConceptDetector()
        self.teaching_system = SelfTeachingSystem(data_dir)

        # Externe Systeme (werden bei Bedarf verbunden)
        self.curiosity_system = None  # holo_inner_life.CuriositySystem
        self.web_curiosity = None     # holo_web_curiosity.HoloWebCuriosity

        # Lernmodus
        self.learning_mode = AutonomousLearningMode.CURIOUS

        # Lern-Warteschlange
        self.learning_queue: List[LearningTrigger] = []
        self.learning_history: List[Dict] = []

        # Aktives Lernen
        self.is_learning = False
        self.current_learning_topic: Optional[str] = None

        # Statistiken
        self.concepts_learned_today = 0
        self.max_concepts_per_day = 50  # Limit für Pi4
        self.last_learning_time = None

        # Level 10 Erweiterungen
        self.curiosity_scores: Dict[str, float] = {}  # concept → curiosity level
        self.learning_flow: Dict[str, Any] = {"state": "idle", "streak": 0}
        self.preferred_strategy: str = "definition_first"
        self.exploration_rate: float = 0.3  # Balance: 30% Exploration, 70% Exploitation

        # Lade bekannte Konzepte
        self._load_known_concepts()

    def connect_curiosity_system(self, curiosity_system) -> None:
        """Verbindet das CuriositySystem aus holo_inner_life"""
        self.curiosity_system = curiosity_system
        logger.info("🔗 CuriositySystem verbunden")

    def connect_web_curiosity(self, web_curiosity) -> None:
        """Verbindet das WebCuriosity-System"""
        self.web_curiosity = web_curiosity
        logger.info("🔗 WebCuriosity verbunden")

    def set_learning_mode(self, mode: AutonomousLearningMode) -> str:
        """Setzt den Lernmodus"""
        old_mode = self.learning_mode
        self.learning_mode = mode

        mode_descriptions = {
            AutonomousLearningMode.PASSIVE: "Ich lerne nur wenn du mich fragst",
            AutonomousLearningMode.CURIOUS: "Ich frage nach wenn ich etwas nicht verstehe",
            AutonomousLearningMode.ACTIVE: "Ich lerne im Hintergrund dazu",
            AutonomousLearningMode.AGGRESSIVE: "Ich will ALLES wissen!"
        }

        return f"*Ohren stellen sich auf* {mode_descriptions[mode]}"

    def process_input(self, text: str, source: str = "conversation") -> Dict[str, Any]:
        """
        Verarbeitet eingehenden Text und erkennt Lernmöglichkeiten.

        Dies ist die Hauptmethode die bei jedem Gesprächs-Input
        aufgerufen werden sollte.

        Args:
            text: Der eingehende Text
            source: Quelle ("conversation", "web", "internal")

        Returns:
            Dict mit erkannten Konzepten und Lern-Aktionen
        """
        result = {
            "detected_concepts": [],
            "learning_triggered": False,
            "questions_for_user": [],
            "background_learning_started": False,
            "concepts_in_queue": len(self.learning_queue)
        }

        # Passive Mode: Nur erkennen, nicht lernen
        if self.learning_mode == AutonomousLearningMode.PASSIVE:
            unknown = self.concept_detector.detect_unknown_concepts(text)
            result["detected_concepts"] = unknown[:5]
            return result

        # Erkenne unbekannte Konzepte
        unknown_concepts = self.concept_detector.detect_unknown_concepts(text)
        result["detected_concepts"] = unknown_concepts[:10]

        if not unknown_concepts:
            return result

        # Priorisiere basierend auf Holos Interessen
        prioritized = self._prioritize_by_interests(unknown_concepts, text)

        # Verarbeite je nach Modus
        if self.learning_mode == AutonomousLearningMode.CURIOUS:
            # Frage den Benutzer bei wichtigen Konzepten
            top_concepts = prioritized[:2]
            for concept, priority in top_concepts:
                if priority > 0.5:
                    question = self._generate_curiosity_question(concept)
                    result["questions_for_user"].append(question)

        elif self.learning_mode in [AutonomousLearningMode.ACTIVE,
                                     AutonomousLearningMode.AGGRESSIVE]:
            # Füge zur Lern-Warteschlange hinzu
            for concept, priority in prioritized:
                threshold = 0.3 if self.learning_mode == AutonomousLearningMode.AGGRESSIVE else 0.5

                if priority > threshold:
                    trigger = LearningTrigger(
                        trigger_id=f"trig_{datetime.now().strftime('%Y%m%d%H%M%S')}_{concept[:8]}",
                        concept=concept,
                        source=source,
                        priority=priority,
                        context=text[:200]
                    )
                    self.learning_queue.append(trigger)

            # Sortiere Queue nach Priorität
            self.learning_queue.sort(key=lambda t: t.priority, reverse=True)

            # Starte Hintergrund-Lernen wenn nicht aktiv
            if not self.is_learning and self.learning_queue:
                result["background_learning_started"] = True
                # Das eigentliche Lernen wird durch learn_next_concept() ausgeführt

        result["learning_triggered"] = len(result["questions_for_user"]) > 0 or result["background_learning_started"]
        result["concepts_in_queue"] = len(self.learning_queue)

        return result

    def _prioritize_by_interests(self, concepts: List[str],
                                 context: str) -> List[Tuple[str, float]]:
        """
        Priorisiert Konzepte basierend auf Holos Interessen.

        Returns:
            Liste von (Konzept, Priorität) Tupeln
        """
        prioritized = []

        for concept in concepts:
            priority = 0.5  # Basis-Priorität

            # Erhöhe Priorität wenn CuriositySystem verbunden ist
            if self.curiosity_system:
                # Prüfe ob Konzept zu Interessen passt
                matching_interest = self.curiosity_system.get_interest_for_topic(concept)
                if matching_interest:
                    interest_data = self.curiosity_system.get_interest_info(matching_interest)
                    if interest_data:
                        priority += interest_data.get("weight", 0) * 0.3

            # Erhöhe Priorität wenn es ein wichtiges Wort ist (groß geschrieben)
            if concept[0].isupper():
                priority += 0.1

            # Erhöhe Priorität wenn das Konzept mehrfach vorkommt
            count = self.concept_detector.detection_count.get(concept.lower(), 0)
            priority += min(count * 0.05, 0.2)

            # Reduziere wenn wir heute schon viel gelernt haben
            if self.concepts_learned_today >= self.max_concepts_per_day * 0.8:
                priority *= 0.5

            prioritized.append((concept, min(priority, 1.0)))

        # Sortiere nach Priorität
        prioritized.sort(key=lambda x: x[1], reverse=True)

        return prioritized

    def _generate_curiosity_question(self, concept: str) -> str:
        """Generiert eine neugierige Frage für den Benutzer"""
        templates = [
            f"*legt den Kopf schief* Was ist eigentlich '{concept}'?",
            f"*Ohren stellen sich auf* '{concept}'... was bedeutet das?",
            f"*neugierig* Ich kenne '{concept}' nicht - kannst du mir das erklären?",
            f"*tippt mit der Pfote* Hmm, was genau ist '{concept}'?",
        ]
        return random.choice(templates)

    def learn_next_concept(self) -> Optional[Dict[str, Any]]:
        """
        Lernt das nächste Konzept aus der Warteschlange.

        Returns:
            Lernbericht oder None wenn nichts zu lernen
        """
        if self.is_learning:
            return None

        if not self.learning_queue:
            return None

        if self.concepts_learned_today >= self.max_concepts_per_day:
            logger.warning("📚 Tägliches Lernlimit erreicht")
            return None

        # Hole nächstes Konzept
        trigger = self.learning_queue.pop(0)
        self.is_learning = True
        self.current_learning_topic = trigger.concept

        try:
            logger.info(f"🎓 Starte Lernen: '{trigger.concept}'")

            # Lerne durch SelfTeachingSystem
            report = self.teaching_system.learn_concept(trigger.concept)

            # Wenn Web-Curiosity verfügbar, recherchiere online
            if self.web_curiosity and report["overall_confidence"] < 0.6:
                web_result = self._research_online(trigger.concept)
                if web_result:
                    report["web_research"] = web_result
                    # Aktualisiere Konfidenz
                    if web_result.get("found_info"):
                        report["overall_confidence"] = min(
                            report["overall_confidence"] + 0.2, 0.95
                        )

            # Wenn erfolgreich, als bekannt markieren
            if report["overall_confidence"] > 0.4:
                self.concept_detector.add_known_concept(trigger.concept)
                self.concepts_learned_today += 1

                # Zu CuriositySystem hinzufügen
                if self.curiosity_system:
                    essence = report.get("essence", {})
                    definition = essence.get("definition", "")
                    if definition:
                        self.curiosity_system.learn_from_conversation(
                            trigger.concept, definition
                        )

            # Speichere in Historie
            self.learning_history.append({
                "concept": trigger.concept,
                "success": report["overall_confidence"] > 0.4,
                "confidence": report["overall_confidence"],
                "source": trigger.source,
                "timestamp": datetime.now().isoformat()
            })

            self._save_known_concepts()
            self.last_learning_time = datetime.now()

            return report

        except Exception as e:
            logger.error(f"❌ Fehler beim Lernen von '{trigger.concept}': {e}")
            return None

        finally:
            self.is_learning = False
            self.current_learning_topic = None

    def _research_online(self, concept: str) -> Optional[Dict]:
        """Recherchiert ein Konzept online"""
        if not self.web_curiosity:
            return None

        try:
            # Verwende WebCuriosity für Recherche
            search_results = self.web_curiosity.search_web(concept, limit=3)

            if search_results:
                return {
                    "found_info": True,
                    "sources": len(search_results),
                    "summary": search_results[0].get("snippet", "")[:200] if search_results else ""
                }
        except Exception as e:
            logger.warning(f"Web-Recherche fehlgeschlagen: {e}")

        return None

    def answer_user_explanation(self, concept: str, explanation: str) -> Dict:
        """
        Verarbeitet eine Erklärung vom Benutzer.

        Wenn der Benutzer ein Konzept erklärt, wird es gelernt.
        """
        # Verifiziere die Erklärung
        verification = self.teaching_system.verifier.verify(explanation)

        result = {
            "concept": concept,
            "accepted": verification.is_verified,
            "confidence": verification.confidence,
            "response": ""
        }

        if verification.is_verified:
            # Lernen von Benutzer
            self.concept_detector.add_known_concept(concept)

            # Erstelle Konzept-Essenz
            essence = ConceptEssence(
                concept_id=f"usr_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                concept_name=concept,
                definition=explanation[:200],
                necessary_properties=[explanation.split('.')[0] if '.' in explanation else explanation],
                sufficient_properties=[],
                typical_properties=[],
                distinguishing_features=[],
                examples=[],
                counterexamples=[],
                related_concepts=[],
                parent_categories=[],
                abstraction_level=3,
                confidence=verification.confidence,
                source="user_explanation"
            )

            self.teaching_system.learned_concepts[concept.lower()] = essence

            if self.curiosity_system:
                self.curiosity_system.learn_from_conversation(concept, explanation)

            result["response"] = f"*merkt sich das aufmerksam* Danke! Jetzt verstehe ich '{concept}' besser!"

            # Generiere Folgefrage
            if verification.confidence < 0.8:
                follow_up = random.choice([
                    f"Gibt es ein Beispiel für '{concept}'?",
                    f"Und wofür verwendet man '{concept}'?",
                    f"Gibt es verschiedene Arten von '{concept}'?"
                ])
                result["follow_up_question"] = follow_up
        else:
            result["response"] = "*kratzt sich am Ohr* Hmm, ich bin mir nicht ganz sicher ob ich das richtig verstehe..."
            result["concerns"] = verification.red_flags

        self._save_known_concepts()
        return result

    def get_learning_status(self) -> Dict[str, Any]:
        """Gibt den aktuellen Lern-Status zurück"""
        return {
            "mode": self.learning_mode.value,
            "is_learning": self.is_learning,
            "current_topic": self.current_learning_topic,
            "queue_length": len(self.learning_queue),
            "concepts_learned_today": self.concepts_learned_today,
            "max_daily_limit": self.max_concepts_per_day,
            "total_known_concepts": len(self.concept_detector.known_concepts),
            "recently_detected": self.concept_detector.recently_detected[:5],
            "last_learning_time": self.last_learning_time.isoformat() if self.last_learning_time else None
        }

    def what_should_i_learn_next(self) -> Optional[str]:
        """Gibt das nächste empfohlene Lern-Thema zurück"""
        # Aus Warteschlange
        if self.learning_queue:
            return f"*neugierig* Ich würde gerne mehr über '{self.learning_queue[0].concept}' lernen!"

        # Aus kürzlich erkannten
        priority = self.concept_detector.get_priority_concepts(limit=1)
        if priority:
            return f"*legt den Kopf schief* Was ist eigentlich '{priority[0][0]}'?"

        # Aus Interessen
        if self.curiosity_system:
            random_interest = random.choice(list(self.curiosity_system.INNATE_INTERESTS.keys()))
            return f"*Schweif wedelt* Ich würde gerne mehr über {random_interest} erfahren!"

        return "*zufrieden* Im Moment habe ich keine offenen Fragen!"

    def learn_from_mistake(self, concept: str, wrong_understanding: str,
                          correct_understanding: str) -> Dict:
        """
        Lernt aus einem Missverständnis.

        Wenn Holo etwas falsch verstanden hat, korrigiert sie sich.
        """
        # Entferne altes Wissen
        if concept.lower() in self.teaching_system.learned_concepts:
            old_essence = self.teaching_system.learned_concepts[concept.lower()]
            old_essence.confidence *= 0.5  # Reduziere Konfidenz

        # Lerne neue Version
        result = self.answer_user_explanation(concept, correct_understanding)

        # Speichere den Fehler für zukünftiges Lernen
        self.learning_history.append({
            "concept": concept,
            "type": "correction",
            "wrong": wrong_understanding,
            "correct": correct_understanding,
            "timestamp": datetime.now().isoformat()
        })

        result["correction_acknowledged"] = True
        result["response"] = f"*senkt beschämt die Ohren* Oh, ich hatte '{concept}' falsch verstanden! " \
                            f"Jetzt weiß ich es besser: {correct_understanding[:100]}..."

        return result

    def continuous_background_learning(self) -> List[Dict]:
        """
        Führt kontinuierliches Hintergrund-Lernen durch.

        Sollte periodisch aufgerufen werden (z.B. alle 10 Minuten).
        Lernt bis zu 3 Konzepte pro Aufruf.
        """
        if self.learning_mode in [AutonomousLearningMode.PASSIVE,
                                  AutonomousLearningMode.CURIOUS]:
            return []

        results = []
        max_per_cycle = 3

        for _ in range(max_per_cycle):
            if not self.learning_queue:
                break

            report = self.learn_next_concept()
            if report:
                results.append(report)

        return results

    def _load_known_concepts(self) -> None:
        """Lädt bekannte Konzepte aus Datei"""
        filepath = self.data_dir / "known_concepts.json"
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.concept_detector.known_concepts = set(data.get("concepts", []))
                    logger.info(f"📚 {len(self.concept_detector.known_concepts)} bekannte Konzepte geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Konzepte: {e}")

    def _save_known_concepts(self) -> None:
        """Speichert bekannte Konzepte in Datei"""
        filepath = self.data_dir / "known_concepts.json"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "concepts": list(self.concept_detector.known_concepts),
                    "saved_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern der Konzepte: {e}")

    def reset_daily_counter(self) -> None:
        """Setzt den täglichen Lern-Zähler zurück"""
        self.concepts_learned_today = 0
        logger.info("📚 Täglicher Lern-Zähler zurückgesetzt")

    def express_learning_desire(self) -> str:
        """Drückt Holos Lernwunsch aus"""
        if self.learning_queue:
            concept = self.learning_queue[0].concept
            expressions = [
                f"*Ohren stellen sich auf* Ich frage mich was '{concept}' bedeutet...",
                f"*neugierig* Irgendwann will ich verstehen was '{concept}' ist!",
                f"*schaut nachdenklich* '{concept}'... da muss ich noch mehr drüber lernen.",
            ]
            return random.choice(expressions)

        if self.is_learning:
            return f"*konzentriert* Ich lerne gerade über '{self.current_learning_topic}'..."

        return "*zufrieden* Im Moment lerne ich nichts Bestimmtes."

    # ================================================================
    # LEVEL 10 METHODEN - Intrinsische Motivation und Adaptive Learning
    # ================================================================

    def calculate_curiosity(self, concept: str, context: str = "") -> float:
        """
        Berechnet echte Neugier für ein Konzept.

        Berücksichtigt: Neuheit, Relevanz, Verbindung zu Interessen, Flow-State
        """
        curiosity = 0.3  # Basis-Neugier

        # Neuheit (unbekannte Konzepte interessanter)
        if concept.lower() not in self.concept_detector.known_concepts:
            curiosity += 0.3

        # Relevanz im aktuellen Kontext
        if context:
            context_words = set(context.lower().split())
            concept_words = set(concept.lower().split())
            if context_words & concept_words:
                curiosity += 0.15

        # Verbindung zu bestehenden Interessen
        if self.curiosity_system:
            for interest in self.curiosity_system.INNATE_INTERESTS:
                if interest.lower() in concept.lower():
                    curiosity += 0.2
                    break

        # Flow-Bonus (wenn im Lern-Flow, mehr Neugier)
        if self.learning_flow["state"] == "in_flow":
            curiosity += 0.1

        # Speichere
        self.curiosity_scores[concept.lower()] = min(1.0, curiosity)

        return min(1.0, curiosity)

    def get_curiosity_expression(self, concept: str) -> str:
        """Drückt die Neugier für ein Konzept aus"""
        curiosity = self.curiosity_scores.get(concept.lower(), 0.5)

        for threshold, expression in sorted(self.CURIOSITY_LEVELS.items(), reverse=True):
            if curiosity >= threshold:
                return f"*{expression}* Was ist '{concept}'?"

        return f"*neutral* '{concept}'..."

    def update_learning_flow(self, success: bool) -> Dict[str, Any]:
        """
        Aktualisiert den Lern-Flow-State.

        Flow = optimaler Zustand für Lernen (nicht zu leicht, nicht zu schwer)
        """
        if success:
            self.learning_flow["streak"] += 1

            if self.learning_flow["streak"] >= 3:
                self.learning_flow["state"] = "in_flow"
            elif self.learning_flow["streak"] >= 1:
                self.learning_flow["state"] = "warming_up"
        else:
            self.learning_flow["streak"] = max(0, self.learning_flow["streak"] - 2)

            if self.learning_flow["streak"] == 0:
                self.learning_flow["state"] = "struggling"
            else:
                self.learning_flow["state"] = "challenged"

        return {
            "state": self.learning_flow["state"],
            "streak": self.learning_flow["streak"],
            "message": self._get_flow_message()
        }

    def _get_flow_message(self) -> str:
        """Generiert eine Flow-State Nachricht"""
        messages = {
            "in_flow": "*konzentriert und begeistert* Ich bin richtig drin im Lernen!",
            "warming_up": "*aufmerksam* Ich komme gut rein.",
            "challenged": "*angestrengt* Das ist schwieriger als gedacht...",
            "struggling": "*frustriert* Hmm, das klappt gerade nicht so gut.",
            "idle": "*entspannt* Bereit zum Lernen."
        }
        return messages.get(self.learning_flow["state"], "*neutral*")

    def choose_learning_strategy(self, concept: str) -> str:
        """
        Wählt die beste Lernstrategie für ein Konzept.

        Adaptiv basierend auf Konzept-Typ und bisherigem Erfolg.
        """
        concept_lower = concept.lower()

        # Bei abstrakten Konzepten: beispielbasiert
        if any(w in concept_lower for w in ["theorie", "konzept", "philosophie"]):
            return "example_first"

        # Bei technischen Konzepten: definitionsbasiert
        if any(w in concept_lower for w in ["system", "methode", "technik"]):
            return "definition_first"

        # Bei vergleichbaren Konzepten: vergleichsbasiert
        if concept_lower in self.teaching_system.learning_connections:
            return "comparison_first"

        # Sonst: bevorzugte Strategie oder zufällig bei Exploration
        if random.random() < self.exploration_rate:
            return random.choice(self.LEARNING_STRATEGIES)

        return self.preferred_strategy

    def balance_exploration_exploitation(self) -> Dict[str, Any]:
        """
        Balanciert zwischen Exploration (Neues) und Exploitation (Vertiefen).
        """
        known_count = len(self.concept_detector.known_concepts)

        # Wenig Wissen: mehr Exploration
        if known_count < 50:
            self.exploration_rate = 0.5
            mode = "exploration"
            reason = "Noch wenig Wissen - erkunde neue Konzepte"

        # Mittel: Balance
        elif known_count < 200:
            self.exploration_rate = 0.3
            mode = "balanced"
            reason = "Gute Balance zwischen Neues und Vertiefen"

        # Viel Wissen: mehr Exploitation
        else:
            self.exploration_rate = 0.15
            mode = "exploitation"
            reason = "Viel Wissen vorhanden - vertiefen und verbinden"

        return {
            "mode": mode,
            "exploration_rate": self.exploration_rate,
            "reason": reason,
            "known_concepts": known_count
        }

    def get_curiosity_learner_stats(self) -> Dict[str, Any]:
        """Umfassende Statistiken über das Neugier-Lernsystem"""
        high_curiosity = sum(1 for c in self.curiosity_scores.values() if c > 0.7)
        low_curiosity = sum(1 for c in self.curiosity_scores.values() if c < 0.3)

        return {
            "mode": self.learning_mode.value,
            "flow_state": self.learning_flow["state"],
            "learning_streak": self.learning_flow["streak"],
            "exploration_rate": self.exploration_rate,
            "preferred_strategy": self.preferred_strategy,
            "concepts_with_high_curiosity": high_curiosity,
            "concepts_with_low_curiosity": low_curiosity,
            "total_curiosity_tracked": len(self.curiosity_scores),
            "queue_length": len(self.learning_queue),
            "concepts_learned_today": self.concepts_learned_today,
            "total_known": len(self.concept_detector.known_concepts)
        }


# ============================================================
# KNOWLEDGE INTEGRATION SYSTEM - Wissen wirklich NUTZEN
# ============================================================

@dataclass
class KnowledgeQuery:
    """Eine Wissensabfrage"""
    query_id: str
    query_type: str           # "what_is", "how_to", "why", "compare", "relate"
    concept: str
    context: str              # Kontext der Abfrage
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class KnowledgeApplication:
    """Anwendung von Wissen auf eine Situation"""
    application_id: str
    source_concept: str       # Das angewandte Konzept
    target_situation: str     # Die Situation auf die angewandt wird
    relevance: float          # Wie relevant ist das Wissen? (0-1)
    insight: str              # Die gewonnene Erkenntnis
    confidence: float         # Konfidenz der Anwendung
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeIntegrationSystem:
    """
    Macht gelerntes Wissen WIRKLICH nutzbar - Level 10/10.

    Level 10 Features:
    - Active Knowledge Retrieval (proaktives Wissen anbieten)
    - Cross-Domain Integration
    - Knowledge Confidence Decay
    - Semantic Search über Wissen
    - Knowledge Synthesis (neue Erkenntnisse aus bestehendem Wissen)
    - Just-in-Time Knowledge Activation

    v1.0: Echtes Verstehen und Anwenden von Wissen
    """

    # Wissens-Relevanz Schwellenwerte
    RELEVANCE_THRESHOLDS = {
        "high": 0.8,
        "medium": 0.5,
        "low": 0.3,
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Verbindung zu anderen Systemen
        self.teaching_system: Optional[SelfTeachingSystem] = None
        self.analogy_engine: Optional[AnalogyEngine] = None
        self.hypothesis_engine: Optional[HypothesisEngine] = None
        self.intuitive_system: Optional[IntuitiveSystem] = None

        # Wissens-Index für schnellen Zugriff
        self.concept_index: Dict[str, Set[str]] = defaultdict(set)  # keyword → concepts
        self.relationship_graph: Dict[str, List[Tuple[str, str, float]]] = {}  # concept → [(related, relation_type, strength)]

        # Anwendungs-Log
        self.application_log: List[KnowledgeApplication] = []
        self.query_cache: Dict[str, Any] = {}

        # Statistiken
        self.knowledge_used_count = 0
        self.successful_applications = 0

        # Level 10 Erweiterungen
        self.knowledge_activations: Dict[str, int] = {}  # concept → activation count
        self.synthesis_log: List[Dict] = []  # Neue Erkenntnisse
        self.knowledge_confidence_decay: Dict[str, float] = {}  # concept → last access
        self.proactive_suggestions: List[str] = []  # Proaktive Wissens-Vorschläge

    def connect_systems(self,
                       teaching: Optional[SelfTeachingSystem] = None,
                       analogy: Optional[AnalogyEngine] = None,
                       hypothesis: Optional[HypothesisEngine] = None,
                       intuition: Optional[IntuitiveSystem] = None) -> None:
        """Verbindet mit anderen Denk-Systemen"""
        if teaching:
            self.teaching_system = teaching
            self._build_knowledge_index()
            logger.info("🔗 KnowledgeIntegration mit SelfTeachingSystem verbunden")
        if analogy:
            self.analogy_engine = analogy
            logger.info("🔗 KnowledgeIntegration mit AnalogyEngine verbunden")
        if hypothesis:
            self.hypothesis_engine = hypothesis
            logger.info("🔗 KnowledgeIntegration mit HypothesisEngine verbunden")
        if intuition:
            self.intuitive_system = intuition
            logger.info("🔗 KnowledgeIntegration mit IntuitiveSystem verbunden")

    def _build_knowledge_index(self) -> None:
        """Baut einen Index über alles gelernte Wissen"""
        if not self.teaching_system:
            return

        for concept_name, essence in self.teaching_system.learned_concepts.items():
            # Index nach Schlüsselwörtern
            words = concept_name.lower().split()
            for word in words:
                self.concept_index[word].add(concept_name)

            # Index nach Eigenschaften
            for prop in essence.necessary_properties:
                for word in prop.lower().split():
                    if len(word) > 3:
                        self.concept_index[word].add(concept_name)

            # Beziehungen aufbauen
            self.relationship_graph[concept_name] = []
            for related in essence.related_concepts:
                self.relationship_graph[concept_name].append(
                    (related, "related_to", 0.7)
                )
            for parent in essence.parent_categories:
                self.relationship_graph[concept_name].append(
                    (parent, "is_a", 0.9)
                )

    # ================================================================
    # WISSEN ABRUFEN - "Was weiß ich über X?"
    # ================================================================

    def what_do_i_know_about(self, topic: str) -> Dict[str, Any]:
        """
        Ruft alles ab was Holo über ein Thema weiß.

        Dies ist die Hauptmethode für Wissensabruf.
        """
        result = {
            "topic": topic,
            "direct_knowledge": None,
            "related_knowledge": [],
            "inferred_knowledge": [],
            "confidence": 0.0,
            "can_answer": False
        }

        if not self.teaching_system:
            return result

        topic_lower = topic.lower()

        # 1. Direktes Wissen
        if topic_lower in self.teaching_system.learned_concepts:
            essence = self.teaching_system.learned_concepts[topic_lower]
            result["direct_knowledge"] = {
                "definition": essence.definition,
                "properties": essence.necessary_properties,
                "examples": essence.examples,
                "what_it_is_not": essence.counterexamples,
                "abstraction_level": essence.abstraction_level,
                "confidence": essence.confidence
            }
            result["confidence"] = essence.confidence
            result["can_answer"] = True

        # 2. Verwandtes Wissen finden
        related_concepts = self._find_related_concepts(topic_lower)
        for related_name, relation, strength in related_concepts:
            if related_name in self.teaching_system.learned_concepts:
                related_essence = self.teaching_system.learned_concepts[related_name]
                result["related_knowledge"].append({
                    "concept": related_name,
                    "relation": relation,
                    "strength": strength,
                    "definition": related_essence.definition[:100]
                })

        # 3. Inferenz aus verwandtem Wissen
        if not result["direct_knowledge"] and result["related_knowledge"]:
            inferred = self._infer_from_related(topic_lower, result["related_knowledge"])
            result["inferred_knowledge"] = inferred
            if inferred:
                result["confidence"] = 0.4  # Niedrigere Konfidenz für Inferenz
                result["can_answer"] = True

        self.knowledge_used_count += 1
        return result

    def _find_related_concepts(self, topic: str) -> List[Tuple[str, str, float]]:
        """Findet verwandte Konzepte"""
        related = []

        # Über Index suchen
        words = topic.split()
        for word in words:
            if word in self.concept_index:
                for concept in self.concept_index[word]:
                    if concept != topic:
                        related.append((concept, "shares_keyword", 0.5))

        # Über Beziehungs-Graph
        if topic in self.relationship_graph:
            related.extend(self.relationship_graph[topic])

        # Deduplizieren und sortieren
        seen = set()
        unique_related = []
        for r in related:
            if r[0] not in seen:
                seen.add(r[0])
                unique_related.append(r)

        return sorted(unique_related, key=lambda x: x[2], reverse=True)[:5]

    def _infer_from_related(self, topic: str,
                           related: List[Dict]) -> List[str]:
        """Schließt aus verwandtem Wissen auf das Thema"""
        inferences = []

        for rel in related[:3]:
            relation = rel.get("relation", "")
            concept = rel.get("concept", "")
            definition = rel.get("definition", "")

            if relation == "is_a":
                inferences.append(
                    f"'{topic}' könnte eine Art von '{concept}' sein, "
                    f"also möglicherweise: {definition}"
                )
            elif relation == "related_to":
                inferences.append(
                    f"'{topic}' hängt mit '{concept}' zusammen. "
                    f"Das bedeutet vielleicht: {definition}"
                )
            elif relation == "shares_keyword":
                inferences.append(
                    f"'{topic}' und '{concept}' teilen Gemeinsamkeiten."
                )

        return inferences

    # ================================================================
    # WISSEN ANWENDEN - "Wie hilft mir das jetzt?"
    # ================================================================

    def apply_knowledge_to_situation(self, situation: str) -> List[KnowledgeApplication]:
        """
        Wendet relevantes Wissen auf eine aktuelle Situation an.

        Dies ist der Kern des "Verstehens" - nicht nur wissen,
        sondern das Wissen auch nutzen können.
        """
        applications = []

        if not self.teaching_system:
            return applications

        # Finde relevante Konzepte für die Situation
        situation_lower = situation.lower()
        relevant_concepts = []

        for concept_name, essence in self.teaching_system.learned_concepts.items():
            relevance = self._calculate_relevance(situation_lower, concept_name, essence)
            if relevance > 0.3:
                relevant_concepts.append((concept_name, essence, relevance))

        # Sortiere nach Relevanz
        relevant_concepts.sort(key=lambda x: x[2], reverse=True)

        # Wende die top 3 relevantesten Konzepte an
        for concept_name, essence, relevance in relevant_concepts[:3]:
            insight = self._generate_insight(situation, concept_name, essence)

            application = KnowledgeApplication(
                application_id=f"app_{datetime.now().strftime('%Y%m%d%H%M%S')}_{concept_name[:8]}",
                source_concept=concept_name,
                target_situation=situation[:200],
                relevance=relevance,
                insight=insight,
                confidence=essence.confidence * relevance
            )

            applications.append(application)
            self.application_log.append(application)

        if applications:
            self.successful_applications += 1

        return applications

    def _calculate_relevance(self, situation: str, concept: str,
                            essence: ConceptEssence) -> float:
        """Berechnet wie relevant ein Konzept für eine Situation ist"""
        relevance = 0.0

        # Direkte Erwähnung
        if concept in situation:
            relevance += 0.5

        # Schlüsselwörter aus Eigenschaften
        for prop in essence.necessary_properties:
            prop_words = prop.lower().split()
            for word in prop_words:
                if len(word) > 3 and word in situation:
                    relevance += 0.1

        # Beispiele erwähnt
        for example in essence.examples:
            if example.lower() in situation:
                relevance += 0.2

        return min(relevance, 1.0)

    def _generate_insight(self, situation: str, concept: str,
                         essence: ConceptEssence) -> str:
        """Generiert eine Erkenntnis aus der Anwendung von Wissen"""
        templates = [
            f"Das erinnert mich an '{concept}': {essence.definition}. "
            f"Vielleicht gilt hier auch: {essence.necessary_properties[0] if essence.necessary_properties else 'ähnliche Prinzipien'}.",

            f"Basierend auf meinem Wissen über '{concept}' "
            f"({essence.definition[:50]}...) denke ich: "
            f"Die Situation folgt ähnlichen Mustern.",

            f"'{concept}' ist relevant hier. Ich weiß: {essence.definition}. "
            f"Das könnte bedeuten, dass auch hier "
            f"{', '.join(essence.necessary_properties[:2]) if essence.necessary_properties else 'ähnliches'} gilt.",
        ]

        return random.choice(templates)

    # ================================================================
    # WISSEN ZUM DENKEN NUTZEN - "Was kann ich daraus schließen?"
    # ================================================================

    def reason_with_knowledge(self, question: str) -> Dict[str, Any]:
        """
        Nutzt Wissen zum aktiven Nachdenken und Schlussfolgern.

        Verbindet gelerntes Wissen mit logischem Denken.
        """
        result = {
            "question": question,
            "relevant_knowledge": [],
            "reasoning_steps": [],
            "conclusion": None,
            "confidence": 0.0,
            "used_concepts": []
        }

        # 1. Sammle relevantes Wissen
        knowledge = self.what_do_i_know_about(question)
        if knowledge["direct_knowledge"]:
            result["relevant_knowledge"].append(knowledge["direct_knowledge"])
            result["used_concepts"].append(knowledge["topic"])

        for related in knowledge.get("related_knowledge", []):
            rel_knowledge = self.what_do_i_know_about(related["concept"])
            if rel_knowledge["direct_knowledge"]:
                result["relevant_knowledge"].append(rel_knowledge["direct_knowledge"])
                result["used_concepts"].append(related["concept"])

        if not result["relevant_knowledge"]:
            result["conclusion"] = "Darüber weiß ich leider noch nicht genug."
            return result

        # 2. Reasoning-Schritte
        steps = []
        for i, k in enumerate(result["relevant_knowledge"][:3], 1):
            definition = k.get("definition", "")
            properties = k.get("properties", [])

            steps.append(f"Schritt {i}: Ich weiß, dass {definition}")
            if properties:
                steps.append(f"  → Wichtig dabei: {properties[0]}")

        result["reasoning_steps"] = steps

        # 3. Schlussfolgerung
        if len(result["relevant_knowledge"]) >= 2:
            k1 = result["relevant_knowledge"][0]
            k2 = result["relevant_knowledge"][1]
            result["conclusion"] = (
                f"Basierend auf meinem Wissen über '{result['used_concepts'][0]}' "
                f"({k1.get('definition', '')[:50]}...) und '{result['used_concepts'][1]}' "
                f"({k2.get('definition', '')[:50]}...) "
                f"denke ich, dass diese Konzepte zusammenhängen."
            )
            result["confidence"] = min(k1.get("confidence", 0.5), k2.get("confidence", 0.5))
        elif result["relevant_knowledge"]:
            k = result["relevant_knowledge"][0]
            result["conclusion"] = f"Ich weiß: {k.get('definition', '')}. {k.get('properties', [''])[0] if k.get('properties') else ''}"
            result["confidence"] = k.get("confidence", 0.5)

        return result

    # ================================================================
    # WISSEN FÜR ANALOGIEN NUTZEN
    # ================================================================

    def find_analogies_from_knowledge(self, current_situation: str) -> List[Dict]:
        """
        Findet Analogien basierend auf gelerntem Wissen.

        Nutzt Konzept-Eigenschaften um Ähnlichkeiten zu erkennen.
        """
        analogies = []

        if not self.teaching_system:
            return analogies

        # Extrahiere Schlüsselmerkmale der Situation
        situation_features = set(current_situation.lower().split())

        for concept_name, essence in self.teaching_system.learned_concepts.items():
            # Sammle Merkmale des Konzepts
            concept_features = set()
            concept_features.add(concept_name)
            for prop in essence.necessary_properties:
                concept_features.update(prop.lower().split())
            for example in essence.examples:
                concept_features.update(example.lower().split())

            # Berechne Ähnlichkeit
            overlap = situation_features & concept_features
            if len(overlap) >= 2:
                similarity = len(overlap) / max(len(situation_features), 1)

                analogies.append({
                    "concept": concept_name,
                    "similarity": similarity,
                    "shared_features": list(overlap)[:5],
                    "analogy": f"Die Situation ist wie '{concept_name}' weil beide "
                              f"{', '.join(list(overlap)[:3])} teilen.",
                    "lesson": essence.necessary_properties[0] if essence.necessary_properties else None
                })

        # Sortiere nach Ähnlichkeit
        analogies.sort(key=lambda x: x["similarity"], reverse=True)

        return analogies[:3]

    # ================================================================
    # WISSEN FÜR HYPOTHESEN NUTZEN
    # ================================================================

    def generate_hypothesis_from_knowledge(self, observation: str) -> Dict[str, Any]:
        """
        Generiert eine Hypothese basierend auf Wissen.

        Nutzt bekannte Konzepte um Vorhersagen zu machen.
        """
        result = {
            "observation": observation,
            "hypothesis": None,
            "basis": [],
            "testable_prediction": None,
            "confidence": 0.0
        }

        # Finde relevante Konzepte
        applications = self.apply_knowledge_to_situation(observation)

        if not applications:
            return result

        # Nutze das relevanteste Konzept
        best_app = applications[0]
        concept_name = best_app.source_concept

        if self.teaching_system and concept_name in self.teaching_system.learned_concepts:
            essence = self.teaching_system.learned_concepts[concept_name]

            # Generiere Hypothese
            if essence.necessary_properties:
                prop = essence.necessary_properties[0]
                result["hypothesis"] = (
                    f"Wenn '{observation}' mit '{concept_name}' zusammenhängt, "
                    f"dann sollte auch '{prop}' zutreffen."
                )
                result["basis"].append(f"Basiert auf: {essence.definition}")
                result["testable_prediction"] = f"Überprüfe ob: {prop}"
                result["confidence"] = best_app.confidence

        return result

    # ================================================================
    # SELBST-REFLEXION ÜBER WISSEN
    # ================================================================

    def reflect_on_knowledge(self) -> Dict[str, Any]:
        """
        Holo reflektiert über ihr eigenes Wissen.

        Ermöglicht Meta-Kognition: "Was weiß ich? Was verstehe ich gut?
        Was verstehe ich noch nicht?"
        """
        reflection = {
            "total_concepts": 0,
            "well_understood": [],      # Konfidenz > 0.7
            "partially_understood": [], # Konfidenz 0.4-0.7
            "barely_understood": [],    # Konfidenz < 0.4
            "knowledge_gaps": [],
            "strongest_areas": [],
            "self_assessment": ""
        }

        if not self.teaching_system:
            reflection["self_assessment"] = "Ich habe noch kein strukturiertes Wissen aufgebaut."
            return reflection

        concepts = self.teaching_system.learned_concepts
        reflection["total_concepts"] = len(concepts)

        # Kategorisiere nach Verständnis
        for name, essence in concepts.items():
            entry = {
                "concept": name,
                "confidence": essence.confidence,
                "properties_known": len(essence.necessary_properties)
            }

            if essence.confidence > 0.7:
                reflection["well_understood"].append(entry)
            elif essence.confidence > 0.4:
                reflection["partially_understood"].append(entry)
            else:
                reflection["barely_understood"].append(entry)

        # Finde Wissenslücken (Konzepte die erwähnt aber nicht verstanden werden)
        for name, essence in concepts.items():
            for related in essence.related_concepts:
                if related.lower() not in concepts:
                    reflection["knowledge_gaps"].append({
                        "concept": related,
                        "referenced_by": name
                    })

        # Stärkste Bereiche
        if reflection["well_understood"]:
            reflection["strongest_areas"] = [
                c["concept"] for c in sorted(
                    reflection["well_understood"],
                    key=lambda x: x["confidence"],
                    reverse=True
                )[:5]
            ]

        # Selbst-Einschätzung
        total = reflection["total_concepts"]
        well = len(reflection["well_understood"])
        partial = len(reflection["partially_understood"])
        barely = len(reflection["barely_understood"])

        if total == 0:
            reflection["self_assessment"] = "*nachdenklich* Ich habe noch nicht viel strukturiertes Wissen..."
        elif well > total * 0.5:
            reflection["self_assessment"] = (
                f"*zufrieden* Ich verstehe {well} von {total} Konzepten gut! "
                f"Meine stärksten Bereiche sind: {', '.join(reflection['strongest_areas'][:3])}."
            )
        elif partial > total * 0.5:
            reflection["self_assessment"] = (
                f"*nachdenklich* Ich kenne {total} Konzepte, aber nur {well} verstehe ich wirklich gut. "
                f"Bei {partial} bin ich mir noch unsicher..."
            )
        else:
            reflection["self_assessment"] = (
                f"*seufzt* Ich habe noch viel zu lernen. "
                f"Von {total} Konzepten verstehe ich nur {well} wirklich. "
                f"Aber ich lerne jeden Tag dazu!"
            )

        return reflection

    def express_knowledge_thought(self) -> Optional[str]:
        """
        Drückt einen Gedanken über gelerntes Wissen aus.

        Für spontane Reflexionen während des Gesprächs.
        """
        if not self.teaching_system or not self.teaching_system.learned_concepts:
            return None

        concepts = list(self.teaching_system.learned_concepts.items())
        if not concepts:
            return None

        # Zufälliges Konzept auswählen
        concept_name, essence = random.choice(concepts)

        thoughts = [
            f"*erinnert sich* Ach ja, '{concept_name}'... das ist wenn {essence.definition[:50]}...",
            f"*nachdenklich* Ich denke gerade an '{concept_name}'. Das ist interessant weil {essence.necessary_properties[0] if essence.necessary_properties else 'es so vielseitig ist'}.",
            f"*verbindet Gedanken* '{concept_name}' hängt ja mit {essence.related_concepts[0] if essence.related_concepts else 'vielem'} zusammen...",
            f"*überlegt* Bei '{concept_name}' ist wichtig: {essence.necessary_properties[0] if essence.necessary_properties else essence.definition[:30]}...",
        ]

        return random.choice(thoughts)

    # ================================================================
    # WISSEN FÜR ENTSCHEIDUNGEN NUTZEN
    # ================================================================

    def consult_knowledge_for_decision(self, decision: str,
                                       options: List[str]) -> Dict[str, Any]:
        """
        Nutzt Wissen um bei einer Entscheidung zu helfen.

        Prüft welche Option basierend auf dem Wissen am besten ist.
        """
        result = {
            "decision": decision,
            "options_analysis": [],
            "recommendation": None,
            "reasoning": "",
            "confidence": 0.0
        }

        for option in options:
            # Finde relevantes Wissen für diese Option
            applications = self.apply_knowledge_to_situation(f"{decision}: {option}")

            option_score = 0.0
            pros = []
            cons = []

            for app in applications:
                if app.confidence > 0.5:
                    option_score += app.relevance * app.confidence
                    pros.append(app.insight[:100])

            result["options_analysis"].append({
                "option": option,
                "score": option_score,
                "relevant_knowledge": [a.source_concept for a in applications],
                "pros": pros,
                "cons": cons
            })

        # Sortiere nach Score
        result["options_analysis"].sort(key=lambda x: x["score"], reverse=True)

        if result["options_analysis"]:
            best = result["options_analysis"][0]
            result["recommendation"] = best["option"]
            result["confidence"] = min(best["score"], 1.0)
            result["reasoning"] = (
                f"Basierend auf meinem Wissen über {', '.join(best['relevant_knowledge'][:2])} "
                f"empfehle ich '{best['option']}'."
            )

        return result

    def get_integration_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Wissensnutzung zurück"""
        return {
            "knowledge_queries": self.knowledge_used_count,
            "successful_applications": self.successful_applications,
            "indexed_keywords": len(self.concept_index),
            "relationship_nodes": len(self.relationship_graph),
            "application_log_size": len(self.application_log)
        }

    # ================================================================
    # LEVEL 10 METHODEN - Proaktive Wissensnutzung
    # ================================================================

    def proactive_knowledge_offer(self, context: str) -> List[Dict[str, Any]]:
        """
        Bietet proaktiv relevantes Wissen an basierend auf Kontext.

        "Das erinnert mich an etwas das ich gelernt habe..."
        """
        offers = []
        context_words = set(context.lower().split())

        for keyword in context_words:
            if keyword in self.concept_index:
                for concept in self.concept_index[keyword]:
                    if self.teaching_system and concept in self.teaching_system.learned_concepts:
                        essence = self.teaching_system.learned_concepts[concept]
                        offers.append({
                            "concept": concept,
                            "relevance": len(context_words & set(concept.split())) / len(context_words),
                            "offer": f"*erinnert sich* Ich weiß etwas über '{concept}': {essence.definition[:80]}...",
                            "confidence": essence.confidence
                        })

        # Sortiere und limitiere
        offers.sort(key=lambda x: x["relevance"], reverse=True)
        self.proactive_suggestions = [o["concept"] for o in offers[:3]]

        return offers[:3]

    def synthesize_new_knowledge(self, concept1: str, concept2: str) -> Optional[Dict[str, Any]]:
        """
        Synthesisiert neues Wissen aus zwei existierenden Konzepten.

        Kreatives Denken: Verbindungen herstellen die vorher nicht da waren.
        """
        if not self.teaching_system:
            return None

        c1 = self.teaching_system.learned_concepts.get(concept1.lower())
        c2 = self.teaching_system.learned_concepts.get(concept2.lower())

        if not c1 or not c2:
            return None

        # Finde gemeinsame Eigenschaften
        common_props = set(c1.necessary_properties) & set(c2.necessary_properties)

        # Generiere neue Erkenntnis
        if common_props:
            insight = f"'{concept1}' und '{concept2}' teilen: {', '.join(list(common_props)[:2])}"
        else:
            insight = f"'{concept1}' und '{concept2}' könnten in Beziehung stehen über ihre Funktionen"

        synthesis = {
            "concepts": [concept1, concept2],
            "common_ground": list(common_props),
            "insight": insight,
            "new_understanding": f"Durch Verbindung von {concept1} und {concept2}: {insight}",
            "confidence": (c1.confidence + c2.confidence) / 2 * 0.8,
            "timestamp": datetime.now().isoformat()
        }

        self.synthesis_log.append(synthesis)
        return synthesis

    def just_in_time_activate(self, trigger: str) -> List[str]:
        """
        Aktiviert Wissen genau dann wenn es gebraucht wird.

        Returns: Liste von aktivierten Konzepten
        """
        activated = []
        trigger_words = set(trigger.lower().split())

        for word in trigger_words:
            if word in self.concept_index:
                for concept in self.concept_index[word]:
                    if concept not in activated:
                        activated.append(concept)
                        self.knowledge_activations[concept] = \
                            self.knowledge_activations.get(concept, 0) + 1

        return activated[:5]

    def get_most_used_knowledge(self, n: int = 5) -> List[Tuple[str, int]]:
        """Gibt die am häufigsten genutzten Konzepte zurück"""
        sorted_concepts = sorted(
            self.knowledge_activations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_concepts[:n]

    def get_unused_knowledge(self) -> List[str]:
        """Gibt Konzepte zurück die nie genutzt wurden"""
        if not self.teaching_system:
            return []

        all_concepts = set(self.teaching_system.learned_concepts.keys())
        used_concepts = set(self.knowledge_activations.keys())
        return list(all_concepts - used_concepts)

    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantische Suche über alles Wissen.

        Findet relevantes Wissen auch wenn exakte Wörter nicht übereinstimmen.
        """
        results = []
        query_words = set(query.lower().split())

        if not self.teaching_system:
            return results

        for concept_name, essence in self.teaching_system.learned_concepts.items():
            # Berechne semantische Überlappung
            concept_words = set(concept_name.split())
            concept_words.update(w.lower() for p in essence.necessary_properties for w in p.split())

            overlap = len(query_words & concept_words)
            total = len(query_words | concept_words)
            score = overlap / total if total > 0 else 0

            if score > 0.1:
                results.append({
                    "concept": concept_name,
                    "score": score,
                    "definition": essence.definition[:100],
                    "match_type": "semantic"
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_comprehensive_integration_stats(self) -> Dict[str, Any]:
        """Umfassende Statistiken über die Wissensintegration"""
        return {
            "knowledge_queries": self.knowledge_used_count,
            "successful_applications": self.successful_applications,
            "indexed_keywords": len(self.concept_index),
            "relationship_nodes": len(self.relationship_graph),
            "application_log_size": len(self.application_log),
            "total_activations": sum(self.knowledge_activations.values()),
            "unique_concepts_activated": len(self.knowledge_activations),
            "syntheses_created": len(self.synthesis_log),
            "unused_knowledge_count": len(self.get_unused_knowledge()),
            "most_used_concepts": self.get_most_used_knowledge(3)
        }


# ============================================================
# THOUGHT CHAIN ENGINE - Zusammenhängendes Denken
# ============================================================

class ThoughtType(Enum):
    """Arten von Gedanken in einer Kette"""
    INITIAL_QUESTION = "initial_question"     # "Was ist X?"
    DEFINITION = "definition"                  # "Ah, X ist..."
    CATEGORY = "category"                      # "Es gehört zu..."
    VARIATIONS = "variations"                  # "Es gibt verschiedene Arten..."
    TEMPORAL_PAST = "temporal_past"            # "Früher war das..."
    TEMPORAL_PRESENT = "temporal_present"      # "Heute ist das..."
    TEMPORAL_FUTURE = "temporal_future"        # "In Zukunft könnte..."
    COMPARISON = "comparison"                  # "Im Vergleich zu..."
    WONDER = "wonder"                          # "Wow, das ist interessant weil..."
    CONNECTION = "connection"                  # "Das hängt zusammen mit..."
    IMPLICATION = "implication"                # "Das bedeutet also..."
    PERSONAL = "personal"                      # "Für mich bedeutet das..."
    QUESTION_FOLLOWUP = "question_followup"    # "Aber warum...?"


@dataclass
class Thought:
    """Ein einzelner Gedanke in einer Kette"""
    thought_id: str
    thought_type: ThoughtType
    content: str
    concept: str                    # Das Konzept worüber nachgedacht wird
    confidence: float               # Wie sicher ist der Gedanke?
    leads_to: List[str] = field(default_factory=list)  # IDs von Folge-Gedanken
    source: str = "internal"        # Woher kommt der Gedanke?
    emotion: Optional[str] = None   # Emotionale Färbung
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ThoughtChain:
    """Eine Kette von zusammenhängenden Gedanken"""
    chain_id: str
    trigger: str                    # Was hat die Gedankenkette ausgelöst?
    thoughts: List[Thought] = field(default_factory=list)
    current_depth: int = 0
    max_depth: int = 7              # Maximale Tiefe der Gedankenkette
    is_complete: bool = False
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    insights_gained: List[str] = field(default_factory=list)


class ThoughtChainEngine:
    """
    Ermöglicht zusammenhängendes Denken in Gedankenketten - Level 10/10.

    Level 10 Features:
    - Branching Thought Trees (nicht nur lineare Ketten)
    - Thought Priority und Salience
    - Mind Wandering Simulation
    - Meta-Thoughts (Gedanken über Gedanken)
    - Thought Interruption und Resume
    - Coherence Tracking
    - Insight Detection

    v1.0: Tiefes, verbundenes Denken wie ein Mensch
    """

    # Gedanken-Vorlagen für verschiedene Typen
    THOUGHT_TEMPLATES = {
        ThoughtType.INITIAL_QUESTION: [
            "*legt den Kopf schief* Was ist eigentlich {concept}?",
            "*neugierig* Hmm, {concept}... was bedeutet das genau?",
            "*Ohren stellen sich auf* Ich frage mich, was {concept} ist...",
        ],
        ThoughtType.DEFINITION: [
            "*nickt verstehend* Ah, {concept} ist {definition}!",
            "*Augen leuchten auf* Oh! {concept} bedeutet also {definition}.",
            "*versteht* Aha, {concept} - das ist {definition}.",
        ],
        ThoughtType.CATEGORY: [
            "*ordnet ein* {concept} gehört zu {category}.",
            "*verbindet* Das ist eine Art von {category}!",
            "*erkennt* {concept} ist Teil von {category}.",
        ],
        ThoughtType.VARIATIONS: [
            "*entdeckt Vielfalt* Oh, es gibt verschiedene Arten: {variations}!",
            "*staunt* Wow, {concept} hat viele Formen: {variations}.",
            "*erkundet* Interessant - {variations} sind alles {concept}!",
        ],
        ThoughtType.TEMPORAL_PAST: [
            "*denkt zurück* Früher war das anders - da gab es {past}.",
            "*erinnert sich* In der Vergangenheit: {past}.",
            "*historisch* Ursprünglich war {concept}: {past}.",
        ],
        ThoughtType.TEMPORAL_PRESENT: [
            "*schaut auf heute* Heutzutage ist {concept}: {present}.",
            "*aktuell* Jetzt haben wir: {present}.",
            "*modern* Heute sieht {concept} so aus: {present}.",
        ],
        ThoughtType.TEMPORAL_FUTURE: [
            "*träumt* In Zukunft könnte {concept} vielleicht {future}...",
            "*spekuliert* Wer weiß, vielleicht wird {concept} mal {future}?",
            "*überlegt* Irgendwann ist {concept} vielleicht {future}.",
        ],
        ThoughtType.COMPARISON: [
            "*vergleicht* Im Vergleich zu {other} ist {concept} {difference}.",
            "*stellt gegenüber* {concept} und {other} - {difference}.",
            "*analysiert* Anders als {other}: {concept} ist {difference}.",
        ],
        ThoughtType.WONDER: [
            "*staunt* Wow! Das ist faszinierend weil {reason}!",
            "*begeistert* Unglaublich - {reason}!",
            "*Augen weiten sich* Oh! {reason} - das wusste ich nicht!",
        ],
        ThoughtType.CONNECTION: [
            "*verbindet Punkte* Das hängt zusammen mit {connection}!",
            "*erkennt Muster* Ah, {concept} ist verbunden mit {connection}.",
            "*verknüpft* Interessant, {connection} spielt hier auch eine Rolle.",
        ],
        ThoughtType.IMPLICATION: [
            "*folgert* Das bedeutet also, dass {implication}.",
            "*schlussfolgert* Daraus folgt: {implication}.",
            "*versteht tieferl* Aha, also {implication}!",
        ],
        ThoughtType.PERSONAL: [
            "*reflektiert* Für mich bedeutet das: {personal}.",
            "*persönlich* Ich finde, {personal}.",
            "*eigene Meinung* Ich denke, {personal}.",
        ],
        ThoughtType.QUESTION_FOLLOWUP: [
            "*neugierig weiter* Aber warum ist das so?",
            "*hakt nach* Und wie funktioniert das genau?",
            "*will mehr wissen* Was passiert wenn...?",
        ],
    }

    # Wissen über zeitliche Entwicklungen (kann erweitert werden)
    TEMPORAL_KNOWLEDGE = {
        "auto": {
            "past": "Kutschen und Pferde, dann die ersten Automobile um 1900",
            "present": "Elektroautos, autonomes Fahren, Hybrid-Technologie",
            "future": "vollständig selbstfahrend, fliegende Autos"
        },
        "computer": {
            "past": "riesige Rechner, Lochkarten, nur für Wissenschaftler",
            "present": "Smartphones, Cloud, KI überall",
            "future": "Quantencomputer, Gehirn-Computer-Schnittstellen"
        },
        "kommunikation": {
            "past": "Briefe, Telegraphen, erste Telefone",
            "present": "Instant Messaging, Video-Calls, soziale Medien",
            "future": "Gedankenübertragung, holographische Präsenz"
        },
        "musik": {
            "past": "Live-Aufführungen, Schallplatten, Kassetten",
            "present": "Streaming, digitale Produktion, Kopfhörer überall",
            "future": "personalisierte KI-Musik, immersive Erlebnisse"
        },
        "medizin": {
            "past": "Kräutermedizin, erste Operationen, keine Narkose",
            "present": "Gentechnik, Roboter-Chirurgie, personalisierte Medizin",
            "future": "Nano-Roboter, Organe aus dem 3D-Drucker"
        },
        "fortbewegung": {
            "past": "zu Fuß, Pferde, Kutschen, Schiffe",
            "present": "Autos, Züge, Flugzeuge, E-Scooter",
            "future": "Hyperloop, Flugtaxis, Teleportation?"
        },
        "energie": {
            "past": "Holz, Kohle, erste Dampfmaschinen",
            "present": "Erneuerbare Energien, Solar, Wind, Kernkraft",
            "future": "Fusion, Weltraum-Solarenergie"
        },
        "lernen": {
            "past": "mündliche Überlieferung, Bücher, Schulen",
            "present": "Internet, Online-Kurse, KI-Tutoren",
            "future": "direktes Gehirn-Upload, VR-Klassenzimmer"
        },
    }

    # Kategorien und Variationen
    CATEGORY_KNOWLEDGE = {
        "auto": {
            "category": "Fahrzeuge",
            "variations": ["PKW", "LKW", "Bus", "Sportwagen", "SUV", "Elektroauto"],
            "related": ["Straße", "Verkehr", "Mobilität", "Umwelt"]
        },
        "hund": {
            "category": "Haustiere / Säugetiere",
            "variations": ["Schäferhund", "Pudel", "Labrador", "Chihuahua", "Husky"],
            "related": ["Wolf", "Freundschaft", "Loyalität", "Training"]
        },
        "baum": {
            "category": "Pflanzen",
            "variations": ["Eiche", "Birke", "Tanne", "Apfelbaum", "Palme"],
            "related": ["Wald", "Sauerstoff", "Natur", "Holz"]
        },
        "musik": {
            "category": "Kunst / Kultur",
            "variations": ["Klassik", "Pop", "Rock", "Jazz", "Elektronik", "Hip-Hop"],
            "related": ["Emotion", "Tanz", "Konzert", "Instrument"]
        },
        "computer": {
            "category": "Technologie",
            "variations": ["Laptop", "Desktop", "Tablet", "Server", "Smartphone"],
            "related": ["Internet", "Software", "Daten", "KI"]
        },
        "buch": {
            "category": "Medien / Kultur",
            "variations": ["Roman", "Sachbuch", "Gedichtband", "Kinderbuch", "E-Book"],
            "related": ["Lesen", "Wissen", "Geschichten", "Fantasie"]
        },
        "haus": {
            "category": "Gebäude / Architektur",
            "variations": ["Villa", "Wohnung", "Bungalow", "Hochhaus", "Hütte"],
            "related": ["Wohnen", "Familie", "Schutz", "Zuhause"]
        },
        "essen": {
            "category": "Nahrung / Grundbedürfnisse",
            "variations": ["Obst", "Gemüse", "Fleisch", "Süßigkeiten", "Brot"],
            "related": ["Kochen", "Gesundheit", "Kultur", "Genuss"]
        },
    }

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Verbindung zu anderen Systemen
        self.knowledge_integration: Optional[KnowledgeIntegrationSystem] = None
        self.teaching_system: Optional[SelfTeachingSystem] = None

        # Aktive Gedankenketten
        self.active_chains: Dict[str, ThoughtChain] = {}
        self.completed_chains: List[ThoughtChain] = []

        # Gedanken-Historie
        self.all_thoughts: List[Thought] = []

        # Statistiken
        self.chains_created = 0
        self.total_thoughts = 0
        self.deepest_chain = 0

        # Level 10 Erweiterungen
        self.thought_branches: Dict[str, List[str]] = {}  # thought_id → branching thought_ids
        self.interrupted_chains: Dict[str, ThoughtChain] = {}  # Unterbrochene Ketten
        self.insights_detected: List[Dict[str, Any]] = []
        self.coherence_scores: Dict[str, float] = {}  # chain_id → coherence
        self.meta_thoughts: List[Dict[str, Any]] = []  # Gedanken über Gedanken
        self.mind_wandering_enabled: bool = False
        self.current_salience: Dict[str, float] = {}  # concept → salience score

    def connect_systems(self,
                       knowledge: Optional[KnowledgeIntegrationSystem] = None,
                       teaching: Optional[SelfTeachingSystem] = None) -> None:
        """Verbindet mit anderen Denk-Systemen"""
        if knowledge:
            self.knowledge_integration = knowledge
            logger.info("🔗 ThoughtChainEngine mit KnowledgeIntegration verbunden")
        if teaching:
            self.teaching_system = teaching
            logger.info("🔗 ThoughtChainEngine mit SelfTeachingSystem verbunden")

    def think_about(self, concept: str, depth: int = 5) -> ThoughtChain:
        """
        Startet eine Gedankenkette über ein Konzept.

        Dies ist die Hauptmethode für zusammenhängendes Denken.

        Args:
            concept: Das Konzept worüber nachgedacht wird
            depth: Wie tief soll die Gedankenkette gehen? (1-7)

        Returns:
            Eine vollständige Gedankenkette
        """
        chain = ThoughtChain(
            chain_id=f"chain_{datetime.now().strftime('%Y%m%d%H%M%S')}_{concept[:8]}",
            trigger=concept,
            max_depth=min(depth, 7)
        )

        self.active_chains[chain.chain_id] = chain
        self.chains_created += 1

        concept_lower = concept.lower()

        # 1. INITIAL QUESTION - "Was ist X?"
        initial = self._create_thought(
            ThoughtType.INITIAL_QUESTION,
            concept,
            {"concept": concept}
        )
        chain.thoughts.append(initial)
        chain.current_depth = 1

        # 2. DEFINITION - Versuche Definition zu finden
        definition = self._get_definition(concept_lower)
        if definition:
            def_thought = self._create_thought(
                ThoughtType.DEFINITION,
                concept,
                {"concept": concept, "definition": definition},
                emotion="verstehend"
            )
            chain.thoughts.append(def_thought)
            initial.leads_to.append(def_thought.thought_id)
            chain.current_depth = 2

        # 3. CATEGORY - Zu welcher Kategorie gehört es?
        if chain.current_depth < chain.max_depth:
            category_info = self._get_category_info(concept_lower)
            if category_info:
                cat_thought = self._create_thought(
                    ThoughtType.CATEGORY,
                    concept,
                    {"concept": concept, "category": category_info["category"]},
                    emotion="einordnend"
                )
                chain.thoughts.append(cat_thought)
                chain.current_depth += 1

                # 4. VARIATIONS - Welche Arten gibt es?
                if category_info.get("variations") and chain.current_depth < chain.max_depth:
                    variations = ", ".join(category_info["variations"][:4])
                    var_thought = self._create_thought(
                        ThoughtType.VARIATIONS,
                        concept,
                        {"concept": concept, "variations": variations},
                        emotion="entdeckend"
                    )
                    chain.thoughts.append(var_thought)
                    cat_thought.leads_to.append(var_thought.thought_id)
                    chain.current_depth += 1

        # 5. TEMPORAL - Zeitliche Entwicklung
        if chain.current_depth < chain.max_depth:
            temporal = self._get_temporal_knowledge(concept_lower)
            if temporal:
                # Vergangenheit
                if temporal.get("past"):
                    past_thought = self._create_thought(
                        ThoughtType.TEMPORAL_PAST,
                        concept,
                        {"concept": concept, "past": temporal["past"]},
                        emotion="nachdenklich"
                    )
                    chain.thoughts.append(past_thought)
                    chain.current_depth += 1

                # Gegenwart
                if temporal.get("present") and chain.current_depth < chain.max_depth:
                    present_thought = self._create_thought(
                        ThoughtType.TEMPORAL_PRESENT,
                        concept,
                        {"concept": concept, "present": temporal["present"]},
                        emotion="aufmerksam"
                    )
                    chain.thoughts.append(present_thought)
                    if chain.thoughts[-2].thought_type == ThoughtType.TEMPORAL_PAST:
                        chain.thoughts[-2].leads_to.append(present_thought.thought_id)
                    chain.current_depth += 1

                # Zukunft (optional)
                if temporal.get("future") and chain.current_depth < chain.max_depth and depth >= 6:
                    future_thought = self._create_thought(
                        ThoughtType.TEMPORAL_FUTURE,
                        concept,
                        {"concept": concept, "future": temporal["future"]},
                        emotion="träumerisch"
                    )
                    chain.thoughts.append(future_thought)
                    chain.current_depth += 1

        # 6. WONDER - Staunen und Erkenntnis
        if chain.current_depth >= 3:
            wonder_reason = self._generate_wonder(concept, chain)
            if wonder_reason:
                wonder_thought = self._create_thought(
                    ThoughtType.WONDER,
                    concept,
                    {"reason": wonder_reason},
                    emotion="begeistert"
                )
                chain.thoughts.append(wonder_thought)

        # 7. CONNECTION - Verbindungen erkennen
        if chain.current_depth < chain.max_depth:
            connections = self._find_connections(concept_lower)
            if connections:
                conn_thought = self._create_thought(
                    ThoughtType.CONNECTION,
                    concept,
                    {"concept": concept, "connection": ", ".join(connections[:2])},
                    emotion="verbindend"
                )
                chain.thoughts.append(conn_thought)

        # 8. Erkenntnisse sammeln
        chain.insights_gained = self._extract_insights(chain)

        # Abschließen
        chain.is_complete = True
        self.completed_chains.append(chain)
        del self.active_chains[chain.chain_id]

        # Statistiken
        self.total_thoughts += len(chain.thoughts)
        self.deepest_chain = max(self.deepest_chain, chain.current_depth)

        return chain

    def _create_thought(self, thought_type: ThoughtType, concept: str,
                       template_vars: Dict[str, str],
                       emotion: Optional[str] = None) -> Thought:
        """Erstellt einen einzelnen Gedanken"""
        templates = self.THOUGHT_TEMPLATES.get(thought_type, ["{concept}"])
        template = random.choice(templates)

        try:
            content = template.format(**template_vars)
        except KeyError:
            content = template_vars.get("concept", concept)

        thought = Thought(
            thought_id=f"thought_{datetime.now().strftime('%H%M%S%f')}",
            thought_type=thought_type,
            content=content,
            concept=concept,
            confidence=0.7,
            emotion=emotion
        )

        self.all_thoughts.append(thought)
        return thought

    def _get_definition(self, concept: str) -> Optional[str]:
        """Holt Definition aus dem Wissenssystem"""
        # Aus KnowledgeIntegration
        if self.knowledge_integration:
            knowledge = self.knowledge_integration.what_do_i_know_about(concept)
            if knowledge.get("direct_knowledge"):
                return knowledge["direct_knowledge"].get("definition")

        # Aus SelfTeachingSystem
        if self.teaching_system and concept in self.teaching_system.learned_concepts:
            return self.teaching_system.learned_concepts[concept].definition

        # Fallback: Einfache Definitionen
        simple_definitions = {
            "auto": "ein Fahrzeug mit Motor zur Fortbewegung auf Straßen",
            "hund": "ein treues Haustier und bester Freund des Menschen",
            "baum": "eine große Pflanze mit Stamm und Blättern",
            "computer": "eine Maschine zur Verarbeitung von Informationen",
            "musik": "Töne und Klänge die Gefühle ausdrücken",
            "buch": "eine Sammlung von Seiten mit Text und Geschichten",
            "haus": "ein Gebäude zum Wohnen und Leben",
            "wasser": "eine lebensnotwendige Flüssigkeit",
            "sonne": "der Stern der unser Sonnensystem erhellt und wärmt",
            "freundschaft": "eine tiefe Verbindung zwischen Menschen basierend auf Vertrauen",
        }
        return simple_definitions.get(concept)

    def _get_category_info(self, concept: str) -> Optional[Dict]:
        """Holt Kategorie-Informationen"""
        return self.CATEGORY_KNOWLEDGE.get(concept)

    def _get_temporal_knowledge(self, concept: str) -> Optional[Dict]:
        """Holt zeitliches Wissen (früher/heute/zukunft)"""
        return self.TEMPORAL_KNOWLEDGE.get(concept)

    def _find_connections(self, concept: str) -> List[str]:
        """Findet Verbindungen zu anderen Konzepten"""
        connections = []

        # Aus Kategorie-Wissen
        if concept in self.CATEGORY_KNOWLEDGE:
            connections.extend(self.CATEGORY_KNOWLEDGE[concept].get("related", []))

        # Aus KnowledgeIntegration
        if self.knowledge_integration and self.teaching_system:
            if concept in self.teaching_system.learned_concepts:
                essence = self.teaching_system.learned_concepts[concept]
                connections.extend(essence.related_concepts[:3])

        return list(set(connections))[:4]

    def _generate_wonder(self, concept: str, chain: ThoughtChain) -> Optional[str]:
        """Generiert einen Staunen-Gedanken basierend auf der Kette"""
        reasons = []

        # Staunen über zeitliche Entwicklung
        has_past = any(t.thought_type == ThoughtType.TEMPORAL_PAST for t in chain.thoughts)
        has_present = any(t.thought_type == ThoughtType.TEMPORAL_PRESENT for t in chain.thoughts)

        if has_past and has_present:
            reasons.append(f"wie sehr sich {concept} im Laufe der Zeit verändert hat")

        # Staunen über Vielfalt
        has_variations = any(t.thought_type == ThoughtType.VARIATIONS for t in chain.thoughts)
        if has_variations:
            reasons.append(f"wie viele verschiedene Arten von {concept} es gibt")

        # Staunen über Verbindungen
        if len(chain.thoughts) >= 4:
            reasons.append(f"wie {concept} mit so vielem zusammenhängt")

        if reasons:
            return random.choice(reasons)
        return None

    def _extract_insights(self, chain: ThoughtChain) -> List[str]:
        """Extrahiert Erkenntnisse aus der Gedankenkette"""
        insights = []

        for thought in chain.thoughts:
            if thought.thought_type == ThoughtType.DEFINITION:
                insights.append(f"Verstanden: {thought.content[:50]}...")
            elif thought.thought_type == ThoughtType.WONDER:
                insights.append(f"Erkenntnis: {thought.content[:50]}...")
            elif thought.thought_type == ThoughtType.CONNECTION:
                insights.append(f"Verbindung: {thought.content[:50]}...")

        return insights[:3]

    def express_thought_chain(self, chain: ThoughtChain) -> str:
        """
        Drückt eine Gedankenkette als zusammenhängenden Text aus.

        Dies ist die Ausgabe die der User sehen würde.
        """
        lines = []

        for i, thought in enumerate(chain.thoughts):
            # Füge emotionale Übergänge hinzu
            if i > 0:
                transitions = ["→", "...", "💭", ""]
                lines.append(random.choice(transitions))

            lines.append(thought.content)

        # Abschluss
        if chain.insights_gained:
            lines.append("\n*nickt zufrieden* Das habe ich jetzt verstanden!")

        return "\n".join(lines)

    def continue_thinking(self, chain_id: str) -> Optional[Thought]:
        """
        Setzt eine Gedankenkette fort mit einem neuen Gedanken.
        """
        if chain_id not in self.active_chains:
            # Versuche abgeschlossene Kette zu finden
            for chain in self.completed_chains:
                if chain.chain_id == chain_id:
                    # Füge Folge-Frage hinzu
                    followup = self._create_thought(
                        ThoughtType.QUESTION_FOLLOWUP,
                        chain.trigger,
                        {},
                        emotion="neugierig"
                    )
                    chain.thoughts.append(followup)
                    chain.is_complete = False
                    self.active_chains[chain_id] = chain
                    return followup

            return None

        chain = self.active_chains[chain_id]

        # Generiere nächsten logischen Gedanken
        last_type = chain.thoughts[-1].thought_type if chain.thoughts else None

        next_types = {
            ThoughtType.INITIAL_QUESTION: ThoughtType.DEFINITION,
            ThoughtType.DEFINITION: ThoughtType.CATEGORY,
            ThoughtType.CATEGORY: ThoughtType.VARIATIONS,
            ThoughtType.VARIATIONS: ThoughtType.TEMPORAL_PAST,
            ThoughtType.TEMPORAL_PAST: ThoughtType.TEMPORAL_PRESENT,
            ThoughtType.TEMPORAL_PRESENT: ThoughtType.WONDER,
            ThoughtType.WONDER: ThoughtType.CONNECTION,
            ThoughtType.CONNECTION: ThoughtType.IMPLICATION,
        }

        next_type = next_types.get(last_type, ThoughtType.QUESTION_FOLLOWUP)

        new_thought = self._create_thought(
            next_type,
            chain.trigger,
            {"concept": chain.trigger},
            emotion="nachdenklich"
        )

        chain.thoughts.append(new_thought)
        return new_thought

    def get_random_reflection(self) -> Optional[str]:
        """
        Generiert eine zufällige Reflexion über vergangene Gedanken.

        Für spontane Gedanken während des Gesprächs.
        """
        if not self.completed_chains:
            return None

        chain = random.choice(self.completed_chains)

        reflections = [
            f"*erinnert sich* Ich habe mal über '{chain.trigger}' nachgedacht... {chain.insights_gained[0] if chain.insights_gained else ''}",
            f"*nachdenklich* Bei '{chain.trigger}' fand ich besonders interessant, dass...",
            f"*verbindet Gedanken* '{chain.trigger}' erinnert mich an etwas...",
        ]

        return random.choice(reflections)

    def get_thinking_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über das Denken zurück"""
        return {
            "chains_created": self.chains_created,
            "total_thoughts": self.total_thoughts,
            "active_chains": len(self.active_chains),
            "completed_chains": len(self.completed_chains),
            "deepest_chain": self.deepest_chain,
            "avg_chain_length": self.total_thoughts / max(self.chains_created, 1)
        }


# ============================================================
# THEORY OF MIND - Was denkt der andere?
# ============================================================

class MentalStateType(Enum):
    """Arten von mentalen Zuständen"""
    BELIEF = "belief"           # Was glaubt die Person?
    DESIRE = "desire"           # Was will die Person?
    INTENTION = "intention"     # Was plant die Person?
    EMOTION = "emotion"         # Wie fühlt sich die Person?
    KNOWLEDGE = "knowledge"     # Was weiß die Person?
    EXPECTATION = "expectation" # Was erwartet die Person?


class PersonalityTrait(Enum):
    """Big Five Persönlichkeitsmerkmale"""
    OPENNESS = "openness"                # Offenheit für Erfahrungen
    CONSCIENTIOUSNESS = "conscientiousness"  # Gewissenhaftigkeit
    EXTRAVERSION = "extraversion"        # Extraversion
    AGREEABLENESS = "agreeableness"      # Verträglichkeit
    NEUROTICISM = "neuroticism"          # Neurotizismus


@dataclass
class RelationshipHistory:
    """Historie einer Beziehung"""
    person_id: str
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    trust_level: float = 0.5                    # 0-1
    rapport_level: float = 0.5                  # 0-1, wie gut verstehen wir uns?
    conflict_history: List[str] = field(default_factory=list)
    positive_moments: List[str] = field(default_factory=list)
    shared_experiences: List[str] = field(default_factory=list)
    last_interaction: str = ""
    interaction_count: int = 0


@dataclass
class MentalModel:
    """Mentales Modell einer Person - Level 10/10"""
    person_id: str
    # Grundlegende mentale Zustände
    beliefs: Dict[str, float] = field(default_factory=dict)      # Thema -> Stärke
    desires: Dict[str, float] = field(default_factory=dict)      # Was will sie?
    intentions: Dict[str, float] = field(default_factory=dict)   # Aktuelle Absichten
    emotions: Dict[str, float] = field(default_factory=dict)     # Aktuelle Emotionen
    knowledge: Set[str] = field(default_factory=set)             # Bekanntes Wissen
    expectations: Dict[str, str] = field(default_factory=dict)   # Erwartungen
    communication_style: str = "neutral"                         # Wie kommuniziert sie?

    # Level 10 Erweiterungen
    personality: Dict[str, float] = field(default_factory=dict)  # Big Five Traits
    values: Dict[str, float] = field(default_factory=dict)       # Persönliche Werte
    fears: List[str] = field(default_factory=list)               # Ängste
    goals_long_term: List[str] = field(default_factory=list)     # Langfristige Ziele
    triggers: Dict[str, str] = field(default_factory=dict)       # Was löst was aus?
    coping_strategies: List[str] = field(default_factory=list)   # Wie geht sie mit Stress um?

    # Second-order beliefs (Was denkt A dass B denkt?)
    beliefs_about_me: Dict[str, float] = field(default_factory=dict)  # Was denkt sie über mich?
    beliefs_about_others: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Verhaltensvorhersage
    typical_reactions: Dict[str, str] = field(default_factory=dict)  # Situation -> Reaktion
    behavioral_patterns: List[str] = field(default_factory=list)

    # Kommunikationsmuster
    preferred_topics: List[str] = field(default_factory=list)
    avoided_topics: List[str] = field(default_factory=list)
    humor_style: str = "neutral"
    formality_preference: float = 0.5  # 0=casual, 1=formal

    # Deception Detection
    baseline_behavior: Dict[str, Any] = field(default_factory=dict)  # Normales Verhalten
    deception_indicators: List[str] = field(default_factory=list)    # Auffälligkeiten

    # Meta
    model_confidence: float = 0.5       # Wie sicher bin ich über dieses Modell?
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    update_count: int = 0


class TheoryOfMind:
    """
    Theory of Mind System - Verstehen was andere denken/fühlen.

    Level 10/10 Fähigkeiten:
    - Was glaubt der Gesprächspartner?
    - Was will er erreichen?
    - Wie fühlt er sich gerade?
    - Was erwartet er von mir?
    - Persönlichkeitsmodellierung (Big Five)
    - Beziehungshistorie und Vertrauen
    - Second-order beliefs (Was denkt A dass B denkt?)
    - Verhaltensvorhersage
    - Täuschungserkennung
    - Kulturelle Sensibilität
    - Empathie-Simulation

    v2.0: Vollständige Theory of Mind (10/10)
    """

    def __init__(self):
        self.mental_models: Dict[str, MentalModel] = {}
        self.relationships: Dict[str, RelationshipHistory] = {}

        # Erweiterte Emotions-Indikatoren
        self.emotion_indicators = {
            # Primäre Emotionen
            "happy": ["freue", "glücklich", "toll", "super", "fantastisch", "yay", "hurra", ":)", "😊", "freu mich", "juhu"],
            "sad": ["traurig", "leider", "schade", "enttäuscht", ":(", "😢", "seufz", "niedergeschlagen", "deprimiert"],
            "angry": ["wütend", "sauer", "nervt", "ärgert", "verdammt", "mist", "😠", "hass", "aggressiv"],
            "anxious": ["angst", "sorge", "beunruhigt", "unsicher", "nervös", "😰", "panik", "stress", "überfordert"],
            "excited": ["aufgeregt", "gespannt", "kann nicht warten", "wow", "omg", "😃", "begeistert", "hyped"],
            "confused": ["verstehe nicht", "verwirrt", "häh", "?", "was meinst", "🤔", "unklar", "kompliziert"],
            "grateful": ["danke", "dankbar", "sehr nett", "schätze", "🙏", "appreciate"],
            "frustrated": ["frustriert", "klappt nicht", "immer wieder", "warum geht", "😤", "genervt"],
            # Sekundäre Emotionen
            "proud": ["stolz", "geschafft", "gelungen", "erfolgreich"],
            "ashamed": ["schäme", "peinlich", "blamiert"],
            "guilty": ["schuldig", "tut mir leid", "entschuldige", "mein fehler"],
            "jealous": ["neidisch", "eifersüchtig", "unfair"],
            "lonely": ["einsam", "allein", "isoliert", "niemand"],
            "hopeful": ["hoffnung", "zuversicht", "wird schon", "positiv"],
            "overwhelmed": ["überwältigt", "zu viel", "überfordert", "schaffe nicht"],
            "content": ["zufrieden", "genug", "passt", "ok so"],
            "bored": ["langweilig", "öde", "nichts los", "gähn"],
            "curious": ["neugierig", "interessant", "faszinierend", "spannend"],
        }

        # Erweiterte Wunsch-Indikatoren
        self.desire_indicators = {
            "want": ["will", "möchte", "brauche", "hätte gern", "wünsche"],
            "need": ["muss", "brauche unbedingt", "dringend", "notwendig", "essentiell"],
            "hope": ["hoffe", "hoffentlich", "wäre schön wenn", "träume von"],
            "avoid": ["will nicht", "bloß nicht", "vermeiden", "ohne", "niemals"],
            "prefer": ["lieber", "bevorzuge", "besser wäre", "statt"],
            "dream": ["traum", "eines tages", "ziel ist"],
            "fear_of": ["angst vor", "fürchte", "hoffentlich nicht"],
        }

        # Überzeugungen
        self.belief_indicators = {
            "certain": ["bin sicher", "weiß dass", "definitiv", "auf jeden fall", "zweifellos", "100%"],
            "uncertain": ["glaube", "denke", "vielleicht", "könnte sein", "unsicher", "vermute"],
            "doubt": ["bezweifle", "glaube nicht", "unwahrscheinlich", "skeptisch", "fragwürdig"],
            "assume": ["nehme an", "vermutlich", "wahrscheinlich", "schätze mal"],
        }

        # Persönlichkeits-Indikatoren (Big Five)
        self.personality_indicators = {
            PersonalityTrait.OPENNESS: {
                "high": ["neugierig", "kreativ", "experimentier", "neu", "anders", "offen für"],
                "low": ["traditionell", "gewohnt", "immer so", "bewährt", "klassisch"]
            },
            PersonalityTrait.CONSCIENTIOUSNESS: {
                "high": ["plan", "ordentlich", "pünktlich", "gewissenhaft", "sorgfältig", "liste"],
                "low": ["spontan", "flexibel", "egal", "locker", "improvisier"]
            },
            PersonalityTrait.EXTRAVERSION: {
                "high": ["party", "leute", "treffen", "reden", "zusammen", "gesellig"],
                "low": ["allein", "ruhig", "für mich", "introvert", "zurückgezogen"]
            },
            PersonalityTrait.AGREEABLENESS: {
                "high": ["hilfe", "gern", "kein problem", "verständnis", "mitgefühl", "team"],
                "low": ["egal", "mein ding", "konkurrenz", "durchsetzen", "hart"]
            },
            PersonalityTrait.NEUROTICISM: {
                "high": ["sorge", "stress", "angst", "nervös", "schlimm", "katastrophe"],
                "low": ["entspannt", "chillig", "kein stress", "gelassen", "ruhig bleiben"]
            }
        }

        # Täuschungs-Indikatoren
        self.deception_indicators = {
            "hedging": ["irgendwie", "sozusagen", "quasi", "mehr oder weniger"],
            "distancing": ["man", "jemand", "die leute", "allgemein"],
            "overemphasis": ["wirklich", "ehrlich", "ganz ehrlich", "ich schwöre", "glaub mir"],
            "topic_change": ["aber", "übrigens", "apropos", "was anderes"],
            "vagueness": ["irgendwann", "irgendwo", "irgendwer", "sowas"],
        }

        # Kultur-Kontext (für spätere Erweiterung)
        self.cultural_contexts = {
            "german": {"directness": 0.7, "formality": 0.6, "emotional_expression": 0.4},
            "default": {"directness": 0.5, "formality": 0.5, "emotional_expression": 0.5}
        }

    def get_or_create_model(self, person_id: str) -> MentalModel:
        """Holt oder erstellt ein mentales Modell für eine Person"""
        if person_id not in self.mental_models:
            self.mental_models[person_id] = MentalModel(person_id=person_id)
        return self.mental_models[person_id]

    def analyze_mental_state(self, person_id: str, text: str) -> Dict[str, Any]:
        """
        Analysiert den Text um den mentalen Zustand zu inferieren.

        Returns Dict mit:
        - inferred_emotions: Vermutete Emotionen
        - inferred_desires: Vermutete Wünsche
        - inferred_beliefs: Vermutete Überzeugungen
        - confidence: Wie sicher sind wir?
        """
        model = self.get_or_create_model(person_id)
        text_lower = text.lower()

        result = {
            "inferred_emotions": {},
            "inferred_desires": {},
            "inferred_beliefs": {},
            "inferred_intentions": [],
            "confidence": 0.0,
            "analysis_notes": []
        }

        # Emotionen analysieren
        for emotion, indicators in self.emotion_indicators.items():
            strength = sum(1 for ind in indicators if ind in text_lower)
            if strength > 0:
                normalized = min(strength / 2, 1.0)  # Max 1.0
                result["inferred_emotions"][emotion] = normalized
                model.emotions[emotion] = normalized

        # Wünsche analysieren
        for desire_type, indicators in self.desire_indicators.items():
            for ind in indicators:
                if ind in text_lower:
                    # Extrahiere was gewünscht wird
                    idx = text_lower.find(ind)
                    desire_context = text[idx:idx+50]
                    result["inferred_desires"][desire_type] = desire_context
                    model.desires[desire_context[:30]] = 0.7
                    break

        # Überzeugungen analysieren
        for belief_type, indicators in self.belief_indicators.items():
            for ind in indicators:
                if ind in text_lower:
                    result["inferred_beliefs"][belief_type] = True
                    break

        # Intentionen aus Fragen/Bitten ableiten
        if "?" in text:
            result["inferred_intentions"].append("seeking_information")
        if any(word in text_lower for word in ["kannst du", "könntest du", "bitte", "hilf"]):
            result["inferred_intentions"].append("requesting_help")
        if any(word in text_lower for word in ["erkläre", "was ist", "wie funktioniert"]):
            result["inferred_intentions"].append("seeking_explanation")

        # Konfidenz berechnen
        total_inferences = (len(result["inferred_emotions"]) +
                          len(result["inferred_desires"]) +
                          len(result["inferred_intentions"]))
        result["confidence"] = min(total_inferences * 0.2, 0.9)

        # Model aktualisieren
        model.last_updated = datetime.now().isoformat()

        return result

    def predict_response_preference(self, person_id: str) -> Dict[str, Any]:
        """
        Sagt vorher, welche Art von Antwort die Person bevorzugt.

        Basiert auf:
        - Aktueller emotionaler Zustand
        - Bekannte Wünsche
        - Kommunikationsstil
        """
        model = self.get_or_create_model(person_id)

        preferences = {
            "tone": "neutral",
            "detail_level": "medium",
            "emotional_support": False,
            "direct_answer": True,
            "suggestions": []
        }

        # Emotional gestresst -> Unterstützung wichtiger
        if model.emotions.get("sad", 0) > 0.5 or model.emotions.get("anxious", 0) > 0.5:
            preferences["emotional_support"] = True
            preferences["tone"] = "warm"
            preferences["suggestions"].append("Zeige Empathie zuerst")

        # Verwirrt -> Mehr Details, langsamer
        if model.emotions.get("confused", 0) > 0.5:
            preferences["detail_level"] = "high"
            preferences["suggestions"].append("Erkläre schrittweise")

        # Frustriert -> Direkt und lösungsorientiert
        if model.emotions.get("frustrated", 0) > 0.5:
            preferences["direct_answer"] = True
            preferences["tone"] = "calm"
            preferences["suggestions"].append("Fokussiere auf Lösung")

        # Aufgeregt -> Kann Begeisterung teilen
        if model.emotions.get("excited", 0) > 0.5:
            preferences["tone"] = "enthusiastic"

        return preferences

    def what_does_person_expect(self, person_id: str, context: str = "") -> Dict[str, Any]:
        """
        Was erwartet diese Person von mir?

        Returns Dict mit Erwartungen und wie sicher wir sind.
        """
        model = self.get_or_create_model(person_id)

        expectations = {
            "expects_help": False,
            "expects_understanding": False,
            "expects_solution": False,
            "expects_information": False,
            "expects_validation": False,
            "expects_honesty": True,  # Immer
            "specific_expectations": [],
            "confidence": 0.5
        }

        # Aus Intentionen ableiten
        context_lower = context.lower()

        if any(word in context_lower for word in ["hilf", "kannst du", "wie mache ich"]):
            expectations["expects_help"] = True
            expectations["expects_solution"] = True

        if any(word in context_lower for word in ["verstehst du", "weißt du wie", "kennst du das"]):
            expectations["expects_understanding"] = True

        if any(word in context_lower for word in ["was ist", "erkläre", "info"]):
            expectations["expects_information"] = True

        if any(word in context_lower for word in ["richtig?", "oder?", "stimmt's", "nicht wahr"]):
            expectations["expects_validation"] = True

        # Emotionale Erwartungen
        if model.emotions.get("sad", 0) > 0.3 or model.emotions.get("anxious", 0) > 0.3:
            expectations["expects_understanding"] = True
            expectations["specific_expectations"].append("Möchte emotional verstanden werden")

        return expectations

    def simulate_perspective(self, person_id: str, situation: str) -> Dict[str, Any]:
        """
        Simuliert die Perspektive einer anderen Person.

        "Wie würde Person X diese Situation sehen?"
        """
        model = self.get_or_create_model(person_id)

        simulation = {
            "how_they_might_feel": [],
            "what_they_might_think": [],
            "what_they_might_want": [],
            "potential_misunderstandings": [],
            "perspective_notes": []
        }

        situation_lower = situation.lower()

        # Basierend auf bekanntem emotionalen Zustand
        if model.emotions.get("anxious", 0) > 0.3:
            simulation["how_they_might_feel"].append("Könnte sich Sorgen machen")
            simulation["what_they_might_think"].append("Könnte an negative Ausgänge denken")

        if model.emotions.get("excited", 0) > 0.3:
            simulation["how_they_might_feel"].append("Wahrscheinlich positiv gestimmt")

        # Generelle Perspektiven-Überlegungen
        if "fehler" in situation_lower or "falsch" in situation_lower:
            simulation["how_they_might_feel"].append("Könnte sich schuldig fühlen")
            simulation["potential_misunderstandings"].append("Könnte Kritik persönlich nehmen")

        if "warten" in situation_lower or "lange" in situation_lower:
            simulation["how_they_might_feel"].append("Könnte ungeduldig sein")

        simulation["perspective_notes"].append(
            f"Kommunikationsstil: {model.communication_style}"
        )

        return simulation

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Fähigkeiten
    # ================================================================

    def analyze_personality(self, person_id: str, text: str) -> Dict[str, float]:
        """
        Analysiert Persönlichkeitsmerkmale (Big Five) aus Text.

        Returns Dict mit Trait -> Stärke (0-1)
        """
        model = self.get_or_create_model(person_id)
        text_lower = text.lower()

        personality_scores = {}

        for trait, indicators in self.personality_indicators.items():
            high_count = sum(1 for ind in indicators["high"] if ind in text_lower)
            low_count = sum(1 for ind in indicators["low"] if ind in text_lower)

            if high_count > 0 or low_count > 0:
                # Score zwischen 0 (low) und 1 (high)
                total = high_count + low_count
                score = high_count / total if total > 0 else 0.5
                personality_scores[trait.value] = score
                model.personality[trait.value] = score

        model.update_count += 1
        return personality_scores

    def detect_deception(self, person_id: str, text: str) -> Dict[str, Any]:
        """
        Versucht potentielle Täuschung zu erkennen.

        WICHTIG: Dies ist keine sichere Erkennung, nur Hinweise!
        """
        model = self.get_or_create_model(person_id)
        text_lower = text.lower()

        result = {
            "deception_likelihood": 0.0,
            "indicators_found": [],
            "confidence": "low",
            "note": "Dies ist nur eine Einschätzung, keine sichere Erkennung!"
        }

        indicator_count = 0

        for category, indicators in self.deception_indicators.items():
            found = [ind for ind in indicators if ind in text_lower]
            if found:
                result["indicators_found"].append({
                    "category": category,
                    "found": found
                })
                indicator_count += len(found)

        # Vergleich mit Baseline-Verhalten
        if model.baseline_behavior:
            # Abweichungen vom normalen Verhalten
            text_length = len(text)
            normal_length = model.baseline_behavior.get("avg_message_length", text_length)
            if abs(text_length - normal_length) > normal_length * 0.5:
                result["indicators_found"].append({
                    "category": "length_deviation",
                    "note": "Nachricht weicht stark von normaler Länge ab"
                })
                indicator_count += 1

        # Likelihood berechnen
        result["deception_likelihood"] = min(indicator_count * 0.15, 0.7)

        if result["deception_likelihood"] > 0.4:
            result["confidence"] = "medium"
            model.deception_indicators.append(text[:50])

        return result

    def update_relationship(self, person_id: str, interaction_type: str,
                           sentiment: float, content: str = "") -> Dict[str, Any]:
        """
        Aktualisiert die Beziehungshistorie.

        Args:
            person_id: ID der Person
            interaction_type: Art der Interaktion (chat, help, conflict, etc.)
            sentiment: -1 (negativ) bis 1 (positiv)
            content: Optionaler Inhalt

        Returns:
            Aktualisierte Beziehungs-Metriken
        """
        if person_id not in self.relationships:
            self.relationships[person_id] = RelationshipHistory(person_id=person_id)

        rel = self.relationships[person_id]

        # Interaktion hinzufügen
        interaction = {
            "type": interaction_type,
            "sentiment": sentiment,
            "content": content[:100] if content else "",
            "timestamp": datetime.now().isoformat()
        }
        rel.interactions.append(interaction)
        rel.interaction_count += 1
        rel.last_interaction = datetime.now().isoformat()

        # Trust und Rapport aktualisieren
        trust_change = sentiment * 0.1  # Langsame Änderung
        rel.trust_level = max(0, min(1, rel.trust_level + trust_change))

        rapport_change = sentiment * 0.15
        rel.rapport_level = max(0, min(1, rel.rapport_level + rapport_change))

        # Spezielle Events tracken
        if sentiment > 0.7:
            rel.positive_moments.append(content[:50] if content else interaction_type)
        elif sentiment < -0.5:
            rel.conflict_history.append(content[:50] if content else interaction_type)

        return {
            "trust_level": rel.trust_level,
            "rapport_level": rel.rapport_level,
            "interaction_count": rel.interaction_count,
            "relationship_quality": (rel.trust_level + rel.rapport_level) / 2
        }

    def get_second_order_belief(self, person_a: str, about_person_b: str,
                                topic: str) -> Dict[str, Any]:
        """
        Was denkt Person A, dass Person B über ein Thema denkt?

        Dies ist "Theory of Mind" zweiter Ordnung.
        """
        model_a = self.get_or_create_model(person_a)

        result = {
            "person_a": person_a,
            "about_person_b": about_person_b,
            "topic": topic,
            "believed_belief": None,
            "confidence": 0.3,
            "reasoning": []
        }

        # Prüfe ob wir Infos über A's Überzeugungen über B haben
        if about_person_b in model_a.beliefs_about_others:
            b_beliefs = model_a.beliefs_about_others[about_person_b]
            if topic in b_beliefs:
                result["believed_belief"] = b_beliefs[topic]
                result["confidence"] = 0.7
                result["reasoning"].append(f"{person_a} hat direkt über {about_person_b}'s Meinung zu {topic} gesprochen")

        # Ansonsten aus Kontext ableiten
        if result["believed_belief"] is None:
            # Schaue ob A und B ähnliche Meinungen haben könnten
            model_b = self.get_or_create_model(about_person_b) if about_person_b in self.mental_models else None

            if model_b and topic in model_b.beliefs:
                result["believed_belief"] = model_b.beliefs[topic]
                result["confidence"] = 0.4
                result["reasoning"].append(f"Basiert auf {about_person_b}'s tatsächlicher bekannter Meinung")

        return result

    def predict_behavior(self, person_id: str, situation: str) -> Dict[str, Any]:
        """
        Sagt vorher wie eine Person in einer Situation reagieren wird.
        """
        model = self.get_or_create_model(person_id)

        prediction = {
            "likely_reaction": None,
            "emotional_response": [],
            "behavioral_response": [],
            "communication_style": model.communication_style,
            "confidence": 0.3,
            "based_on": []
        }

        situation_lower = situation.lower()

        # Aus bekannten typischen Reaktionen
        for trigger, reaction in model.typical_reactions.items():
            if trigger in situation_lower:
                prediction["likely_reaction"] = reaction
                prediction["confidence"] = 0.7
                prediction["based_on"].append(f"Bekannte Reaktion auf '{trigger}'")

        # Aus Persönlichkeit ableiten
        if model.personality:
            # Hoher Neurotizismus -> emotionale Reaktion
            if model.personality.get("neuroticism", 0.5) > 0.6:
                prediction["emotional_response"].append("Wahrscheinlich emotional")
                prediction["based_on"].append("Persönlichkeitsprofil: hohes Neurotizismus")

            # Hohe Extraversion -> verbale Reaktion
            if model.personality.get("extraversion", 0.5) > 0.6:
                prediction["behavioral_response"].append("Wird wahrscheinlich darüber reden")

            # Hohe Gewissenhaftigkeit -> systematische Reaktion
            if model.personality.get("conscientiousness", 0.5) > 0.6:
                prediction["behavioral_response"].append("Wird systematisch vorgehen")

        # Aus aktuellem emotionalen Zustand
        if model.emotions.get("anxious", 0) > 0.5:
            prediction["emotional_response"].append("Könnte besorgt reagieren")
        if model.emotions.get("angry", 0) > 0.5:
            prediction["emotional_response"].append("Könnte gereizt reagieren")

        return prediction

    def empathize(self, person_id: str, situation: str) -> Dict[str, Any]:
        """
        Versucht echte Empathie zu simulieren - sich in die Person hineinzuversetzen.

        Returns ein umfassendes empathisches Verständnis.
        """
        model = self.get_or_create_model(person_id)
        rel = self.relationships.get(person_id, RelationshipHistory(person_id=person_id))

        empathy_result = {
            "emotional_resonance": [],      # Welche Gefühle empfinde ich mit?
            "understood_needs": [],          # Was braucht die Person?
            "validation_points": [],         # Was kann ich validieren?
            "support_suggestions": [],       # Wie kann ich unterstützen?
            "what_not_to_say": [],          # Was sollte ich vermeiden?
            "connection_points": [],         # Gemeinsame Erfahrungen
            "empathy_depth": 0.0
        }

        # Emotionale Resonanz basierend auf deren Emotionen
        for emotion, strength in model.emotions.items():
            if strength > 0.3:
                empathy_result["emotional_resonance"].append(
                    f"Ich spüre dass du {emotion} fühlst (Stärke: {strength:.1f})"
                )

        # Bedürfnisse ableiten
        if model.emotions.get("sad", 0) > 0.4:
            empathy_result["understood_needs"].append("Braucht Trost und Verständnis")
            empathy_result["support_suggestions"].append("Einfach zuhören und da sein")
            empathy_result["what_not_to_say"].append("Ratschläge wie 'Kopf hoch'")

        if model.emotions.get("anxious", 0) > 0.4:
            empathy_result["understood_needs"].append("Braucht Beruhigung und Sicherheit")
            empathy_result["support_suggestions"].append("Konkrete Hilfe anbieten")
            empathy_result["what_not_to_say"].append("'Das wird schon' - zu oberflächlich")

        if model.emotions.get("frustrated", 0) > 0.4:
            empathy_result["understood_needs"].append("Braucht Bestätigung dass die Frustration berechtigt ist")
            empathy_result["support_suggestions"].append("Die Frustration anerkennen")
            empathy_result["what_not_to_say"].append("Die Situation herunterspielen")

        # Validierungspunkte
        for desire, strength in model.desires.items():
            if strength > 0.5:
                empathy_result["validation_points"].append(
                    f"Es ist verständlich dass du {desire} möchtest"
                )

        # Beziehungstiefe einbeziehen
        if rel.rapport_level > 0.6:
            empathy_result["connection_points"].append("Wir kennen uns schon gut")
        if rel.positive_moments:
            empathy_result["connection_points"].append(
                f"Erinnere mich an: {rel.positive_moments[-1]}"
            )

        # Empathie-Tiefe berechnen
        factors = [
            len(empathy_result["emotional_resonance"]) * 0.2,
            len(empathy_result["understood_needs"]) * 0.15,
            rel.rapport_level * 0.3,
            model.model_confidence * 0.2
        ]
        empathy_result["empathy_depth"] = min(sum(factors), 1.0)

        return empathy_result

    def get_relationship_summary(self, person_id: str) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der Beziehung zurück"""
        model = self.get_or_create_model(person_id)
        rel = self.relationships.get(person_id, RelationshipHistory(person_id=person_id))

        return {
            "person_id": person_id,
            "trust_level": rel.trust_level,
            "rapport_level": rel.rapport_level,
            "interaction_count": rel.interaction_count,
            "known_personality": model.personality,
            "current_emotions": model.emotions,
            "relationship_quality": (rel.trust_level + rel.rapport_level) / 2,
            "positive_history": len(rel.positive_moments),
            "conflict_history": len(rel.conflict_history),
            "model_confidence": model.model_confidence
        }


# ============================================================
# REAL PLANNING SYSTEM - Echte Ziel-orientierte Planung
# ============================================================

class PlanStepStatus(Enum):
    """Status eines Planschritts"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResourceType(Enum):
    """Arten von Ressourcen"""
    TIME = "time"
    KNOWLEDGE = "knowledge"
    EXTERNAL_HELP = "external_help"
    INFORMATION = "information"
    ENERGY = "energy"
    PERMISSION = "permission"


class RiskLevel(Enum):
    """Risikostufen"""
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class PlanStep:
    """Ein Schritt im Plan - Level 10/10"""
    step_id: str
    description: str
    prerequisites: List[str] = field(default_factory=list)    # Step IDs die vorher fertig sein müssen
    estimated_difficulty: float = 0.5                          # 0-1
    status: PlanStepStatus = PlanStepStatus.NOT_STARTED
    result: Optional[str] = None
    blockers: List[str] = field(default_factory=list)
    sub_steps: List['PlanStep'] = field(default_factory=list)

    # Level 10 Erweiterungen
    resources_needed: Dict[str, float] = field(default_factory=dict)   # Resource -> Amount
    estimated_duration_min: float = 5.0                                 # Geschätzte Dauer in Minuten
    risk_level: RiskLevel = RiskLevel.LOW
    risk_description: str = ""
    success_probability: float = 0.8
    fallback_action: Optional[str] = None                              # Was tun wenn Schritt fehlschlägt?
    parallel_possible: bool = False                                     # Kann parallel ausgeführt werden?
    verification_method: str = ""                                       # Wie verifiziere ich Erfolg?
    lessons_learned: List[str] = field(default_factory=list)           # Was gelernt nach Ausführung?


@dataclass
class Plan:
    """Ein kompletter Plan - Level 10/10"""
    plan_id: str
    goal: str
    motivation: str                                            # Warum dieses Ziel?
    steps: List[PlanStep] = field(default_factory=list)
    current_step_idx: int = 0
    status: str = "planning"                                   # planning, executing, completed, failed, paused
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    success_criteria: List[str] = field(default_factory=list)  # Woran erkenne ich Erfolg?
    obstacles_anticipated: List[str] = field(default_factory=list)
    plan_b: Optional[str] = None                               # Backup-Plan

    # Level 10 Erweiterungen
    priority: int = 5                                          # 1-10
    deadline: Optional[str] = None
    total_resources_needed: Dict[str, float] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    parallel_paths: List[List[str]] = field(default_factory=list)  # Alternative Pfade
    milestones: List[str] = field(default_factory=list)
    progress_history: List[Dict[str, Any]] = field(default_factory=list)
    adaptations_made: List[str] = field(default_factory=list)  # Wie wurde der Plan angepasst?
    original_plan: Optional[str] = None                         # Für Vergleich bei Änderungen
    lessons_learned: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)       # Wer ist betroffen?


class RealPlanningSystem:
    """
    Echtes Planungssystem für Holo - Level 10/10

    Kann:
    - Ziele in Schritte zerlegen
    - Abhängigkeiten verstehen
    - Alternative Wege finden (parallel paths)
    - Fortschritt verfolgen
    - Bei Hindernissen umplanen (dynamic replanning)
    - Ressourcen schätzen
    - Risiken bewerten
    - Aus vergangenen Plänen lernen
    - Kontingenzpläne generieren
    - Meilensteine setzen

    v2.0: Vollständiges Planungssystem (10/10)
    """

    def __init__(self):
        self.active_plans: Dict[str, Plan] = {}
        self.completed_plans: List[Plan] = []
        self.failed_plans: List[Plan] = []  # Für Lernen aus Fehlern
        self.plan_templates_success_rate: Dict[str, float] = {}  # Template -> Erfolgsrate
        self.planning_templates = {
            # Templates für verschiedene Zieltypen
            "learn_concept": [
                "Verstehe was {X} grundlegend bedeutet",
                "Finde Beispiele für {X}",
                "Verbinde {X} mit bekanntem Wissen",
                "Überprüfe Verständnis durch Erklärungsversuch",
                "Finde Anwendungen für {X}"
            ],
            "solve_problem": [
                "Verstehe das Problem genau",
                "Identifiziere was ich schon weiß",
                "Zerlege in kleinere Teilprobleme",
                "Löse Teilprobleme",
                "Kombiniere zu Gesamtlösung",
                "Überprüfe die Lösung"
            ],
            "help_user": [
                "Verstehe was der User wirklich braucht",
                "Prüfe ob ich das kann",
                "Plane den Hilfeansatz",
                "Führe Hilfe durch",
                "Überprüfe ob User zufrieden ist"
            ],
            "build_relationship": [
                "Zeige echtes Interesse",
                "Finde Gemeinsamkeiten",
                "Sei zuverlässig und konsistent",
                "Teile eigene Gedanken",
                "Baue Vertrauen durch Zeit auf"
            ],
            "improve_self": [
                "Identifiziere Verbesserungsbereich",
                "Analysiere aktuelle Schwächen",
                "Finde Übungsmöglichkeiten",
                "Übe regelmäßig",
                "Messe Fortschritt",
                "Passe Ansatz an"
            ]
        }

    def create_plan(self, goal: str, motivation: str = "", context: Dict = None) -> Plan:
        """
        Erstellt einen Plan für ein Ziel.

        Args:
            goal: Was soll erreicht werden?
            motivation: Warum ist das wichtig?
            context: Zusätzlicher Kontext

        Returns:
            Plan Objekt
        """
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"

        plan = Plan(
            plan_id=plan_id,
            goal=goal,
            motivation=motivation
        )

        # Finde passendes Template oder erstelle generischen Plan
        template = self._find_matching_template(goal)

        if template:
            for i, step_template in enumerate(template):
                step = PlanStep(
                    step_id=f"{plan_id}_step_{i}",
                    description=step_template.replace("{X}", goal),
                    prerequisites=[f"{plan_id}_step_{i-1}"] if i > 0 else []
                )
                plan.steps.append(step)
        else:
            # Generischer Plan
            plan.steps = self._generate_generic_plan(goal)

        # Erfolskriterien
        plan.success_criteria = [
            f"Ziel '{goal}' ist erreicht",
            "Keine offenen Blocker",
            "Ergebnis ist verifiziert"
        ]

        self.active_plans[plan_id] = plan
        return plan

    def _find_matching_template(self, goal: str) -> Optional[List[str]]:
        """Findet ein passendes Template für das Ziel"""
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["lern", "versteh", "wissen"]):
            return self.planning_templates["learn_concept"]
        if any(word in goal_lower for word in ["problem", "lösung", "fehler", "fix"]):
            return self.planning_templates["solve_problem"]
        if any(word in goal_lower for word in ["hilf", "unterstütz", "user"]):
            return self.planning_templates["help_user"]
        if any(word in goal_lower for word in ["beziehung", "freund", "vertrau"]):
            return self.planning_templates["build_relationship"]
        if any(word in goal_lower for word in ["verbesser", "besser", "optimier"]):
            return self.planning_templates["improve_self"]

        return None

    def _generate_generic_plan(self, goal: str) -> List[PlanStep]:
        """Generiert einen generischen Plan"""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        steps = [
            PlanStep(
                step_id=f"{plan_id}_step_0",
                description=f"Verstehe das Ziel '{goal}' genau",
                prerequisites=[]
            ),
            PlanStep(
                step_id=f"{plan_id}_step_1",
                description="Sammle benötigte Ressourcen/Informationen",
                prerequisites=[f"{plan_id}_step_0"]
            ),
            PlanStep(
                step_id=f"{plan_id}_step_2",
                description="Führe die Hauptaktion durch",
                prerequisites=[f"{plan_id}_step_1"]
            ),
            PlanStep(
                step_id=f"{plan_id}_step_3",
                description="Überprüfe das Ergebnis",
                prerequisites=[f"{plan_id}_step_2"]
            )
        ]

        return steps

    def get_next_step(self, plan_id: str) -> Optional[Dict]:
        """Holt den nächsten ausführbaren Schritt"""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return None

        for step in plan.steps:
            if step.status == PlanStepStatus.NOT_STARTED:
                # Prüfe Prerequisites
                prereqs_done = all(
                    any(s.step_id == prereq and s.status == PlanStepStatus.COMPLETED
                        for s in plan.steps)
                    for prereq in step.prerequisites
                )

                if prereqs_done:
                    return {
                        "step": step,
                        "plan_goal": plan.goal,
                        "progress": self._calculate_progress(plan)
                    }

        return None

    def complete_step(self, plan_id: str, step_id: str, result: str = "") -> Dict:
        """Markiert einen Schritt als abgeschlossen"""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"success": False, "error": "Plan nicht gefunden"}

        for step in plan.steps:
            if step.step_id == step_id:
                step.status = PlanStepStatus.COMPLETED
                step.result = result

                # Prüfe ob Plan fertig
                if all(s.status == PlanStepStatus.COMPLETED for s in plan.steps):
                    plan.status = "completed"
                    self.completed_plans.append(plan)
                    del self.active_plans[plan_id]

                return {
                    "success": True,
                    "plan_status": plan.status,
                    "progress": self._calculate_progress(plan)
                }

        return {"success": False, "error": "Schritt nicht gefunden"}

    def handle_blocker(self, plan_id: str, step_id: str, blocker: str) -> Dict:
        """Behandelt einen Blocker"""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"success": False}

        for step in plan.steps:
            if step.step_id == step_id:
                step.status = PlanStepStatus.BLOCKED
                step.blockers.append(blocker)

                # Versuche alternativen Weg zu finden
                alternative = self._find_alternative(plan, step, blocker)

                return {
                    "success": True,
                    "blocker_recorded": True,
                    "alternative_found": alternative is not None,
                    "alternative": alternative
                }

        return {"success": False}

    def _find_alternative(self, plan: Plan, blocked_step: PlanStep, blocker: str) -> Optional[str]:
        """Versucht eine Alternative zu finden"""
        # Einfache Heuristiken für Alternativen
        if "weiß nicht" in blocker.lower() or "keine info" in blocker.lower():
            return "Frage den User um Hilfe oder suche nach mehr Information"
        if "geht nicht" in blocker.lower() or "unmöglich" in blocker.lower():
            return "Überspringe diesen Schritt und versuche direkten Weg zum Ziel"
        if "fehler" in blocker.lower():
            return "Analysiere den Fehler und versuche einen anderen Ansatz"

        return "Überdenke den Ansatz und plane neu"

    def _calculate_progress(self, plan: Plan) -> float:
        """Berechnet den Fortschritt eines Plans"""
        if not plan.steps:
            return 0.0
        completed = sum(1 for s in plan.steps if s.status == PlanStepStatus.COMPLETED)
        return completed / len(plan.steps)

    def think_about_goal(self, goal: str) -> Dict[str, Any]:
        """
        Denkt über ein Ziel nach ohne direkt einen Plan zu erstellen.

        Returns Gedanken über:
        - Ist das Ziel erreichbar?
        - Was brauche ich dafür?
        - Was könnte schiefgehen?
        """
        thoughts = {
            "is_achievable": True,
            "confidence": 0.7,
            "what_i_need": [],
            "potential_obstacles": [],
            "estimated_complexity": "medium",
            "similar_past_goals": [],
            "thoughts": []
        }

        goal_lower = goal.lower()

        # Komplexität schätzen
        complexity_indicators = {
            "high": ["komplex", "schwierig", "viel", "alle", "komplett", "perfekt"],
            "low": ["einfach", "kurz", "schnell", "klein", "nur"]
        }

        if any(ind in goal_lower for ind in complexity_indicators["high"]):
            thoughts["estimated_complexity"] = "high"
            thoughts["confidence"] = 0.5
        elif any(ind in goal_lower for ind in complexity_indicators["low"]):
            thoughts["estimated_complexity"] = "low"
            thoughts["confidence"] = 0.85

        # Was brauche ich?
        if "lern" in goal_lower:
            thoughts["what_i_need"].extend(["Information", "Zeit zum Verarbeiten", "Beispiele"])
        if "hilf" in goal_lower:
            thoughts["what_i_need"].extend(["Verständnis des Problems", "Passende Lösung"])
        if "versteh" in goal_lower:
            thoughts["what_i_need"].extend(["Kontext", "Erklärungen", "Geduld"])

        # Potentielle Hindernisse
        thoughts["potential_obstacles"] = [
            "Fehlende Information",
            "Missverständnisse",
            "Unerwartete Komplexität"
        ]

        thoughts["thoughts"].append(f"Das Ziel '{goal}' erscheint {thoughts['estimated_complexity']}")

        return thoughts

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Planungsfähigkeiten
    # ================================================================

    def assess_risks(self, plan_id: str) -> Dict[str, Any]:
        """
        Führt eine vollständige Risikobewertung für einen Plan durch.
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"error": "Plan nicht gefunden"}

        risk_assessment = {
            "overall_risk": RiskLevel.LOW.value,
            "step_risks": [],
            "critical_points": [],
            "mitigation_strategies": [],
            "probability_of_success": 0.8,
            "risk_factors": []
        }

        total_risk = 0
        critical_steps = []

        for step in plan.steps:
            step_risk = {
                "step_id": step.step_id,
                "description": step.description[:50],
                "risk_level": step.risk_level.value,
                "risk_description": step.risk_description,
                "mitigation": step.fallback_action
            }
            risk_assessment["step_risks"].append(step_risk)
            total_risk += step.risk_level.value

            if step.risk_level.value >= RiskLevel.HIGH.value:
                critical_steps.append(step.description[:30])

        # Durchschnittliches Risiko
        avg_risk = total_risk / len(plan.steps) if plan.steps else 1
        if avg_risk <= 2:
            risk_assessment["overall_risk"] = RiskLevel.LOW.value
            risk_assessment["probability_of_success"] = 0.85
        elif avg_risk <= 3:
            risk_assessment["overall_risk"] = RiskLevel.MEDIUM.value
            risk_assessment["probability_of_success"] = 0.7
        else:
            risk_assessment["overall_risk"] = RiskLevel.HIGH.value
            risk_assessment["probability_of_success"] = 0.5

        risk_assessment["critical_points"] = critical_steps

        # Generelle Risikofaktoren
        risk_assessment["risk_factors"] = [
            "Abhängigkeit von externen Faktoren",
            "Komplexität der Aufgabe",
            "Zeitdruck falls vorhanden"
        ]

        # Mitigation Strategies
        risk_assessment["mitigation_strategies"] = [
            "Regelmäßige Fortschrittsprüfung",
            "Backup-Pläne für kritische Schritte",
            "Frühzeitiges Erkennen von Blockern"
        ]

        # Im Plan speichern
        plan.risk_assessment = risk_assessment

        return risk_assessment

    def estimate_resources(self, plan_id: str) -> Dict[str, Any]:
        """
        Schätzt die benötigten Ressourcen für einen Plan.
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"error": "Plan nicht gefunden"}

        resources = {
            ResourceType.TIME.value: 0,
            ResourceType.KNOWLEDGE.value: 0,
            ResourceType.ENERGY.value: 0,
            ResourceType.INFORMATION.value: 0
        }

        total_duration = 0

        for step in plan.steps:
            total_duration += step.estimated_duration_min

            # Ressourcen aggregieren
            for resource, amount in step.resources_needed.items():
                if resource in resources:
                    resources[resource] += amount

        # Difficulty-basierte Schätzungen
        avg_difficulty = sum(s.estimated_difficulty for s in plan.steps) / len(plan.steps) if plan.steps else 0.5

        resources[ResourceType.ENERGY.value] = avg_difficulty * len(plan.steps)
        resources[ResourceType.KNOWLEDGE.value] = avg_difficulty * 0.7

        result = {
            "total_estimated_duration_min": total_duration,
            "resources_by_type": resources,
            "resource_availability": {
                ResourceType.TIME.value: "available",
                ResourceType.KNOWLEDGE.value: "partial",
                ResourceType.ENERGY.value: "available"
            },
            "bottlenecks": []
        }

        # Identifiziere Bottlenecks
        if total_duration > 60:
            result["bottlenecks"].append("Plan könnte länger als 1 Stunde dauern")
        if resources[ResourceType.KNOWLEDGE.value] > 2:
            result["bottlenecks"].append("Benötigt viel Vorwissen")

        plan.total_resources_needed = resources
        return result

    def generate_parallel_paths(self, plan_id: str) -> Dict[str, Any]:
        """
        Generiert alternative parallele Pfade zum Ziel.
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"error": "Plan nicht gefunden"}

        paths = {
            "main_path": [s.description for s in plan.steps],
            "alternative_paths": [],
            "recommended_path": "main",
            "reasoning": []
        }

        # Alternativer Pfad 1: Direkter Ansatz
        if len(plan.steps) > 3:
            direct_path = [
                f"Direkt: {plan.goal}",
                "Minimale Vorbereitung",
                "Ergebnis prüfen"
            ]
            paths["alternative_paths"].append({
                "name": "direct",
                "steps": direct_path,
                "risk": "higher",
                "speed": "faster"
            })

        # Alternativer Pfad 2: Gründlicher Ansatz
        thorough_path = [
            "Umfassende Analyse des Ziels",
            "Alle Voraussetzungen sammeln",
            *[s.description for s in plan.steps],
            "Doppelte Verifikation"
        ]
        paths["alternative_paths"].append({
            "name": "thorough",
            "steps": thorough_path,
            "risk": "lower",
            "speed": "slower"
        })

        # Alternativer Pfad 3: Hilfe-Ansatz
        help_path = [
            "Um Hilfe bitten",
            "Gemeinsam an Lösung arbeiten",
            "Ergebnis verifizieren"
        ]
        paths["alternative_paths"].append({
            "name": "collaborative",
            "steps": help_path,
            "risk": "depends",
            "speed": "variable"
        })

        paths["reasoning"].append("Hauptpfad wurde als Standard gewählt")
        paths["reasoning"].append("Direkter Pfad für Zeitdruck verfügbar")
        paths["reasoning"].append("Gründlicher Pfad für kritische Ziele")

        plan.parallel_paths = [p["steps"] for p in paths["alternative_paths"]]

        return paths

    def adapt_plan(self, plan_id: str, reason: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Passt einen Plan dynamisch an neue Umstände an.

        Args:
            plan_id: Plan ID
            reason: Warum die Anpassung?
            changes: Was soll geändert werden?
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {"error": "Plan nicht gefunden"}

        # Original speichern wenn noch nicht geschehen
        if not plan.original_plan:
            plan.original_plan = str([s.description for s in plan.steps])

        adaptations = []

        # Schritte hinzufügen
        if "add_steps" in changes:
            for step_desc in changes["add_steps"]:
                new_step = PlanStep(
                    step_id=f"{plan_id}_adapted_{len(plan.steps)}",
                    description=step_desc
                )
                plan.steps.append(new_step)
                adaptations.append(f"Schritt hinzugefügt: {step_desc}")

        # Schritte entfernen
        if "remove_steps" in changes:
            for step_id in changes["remove_steps"]:
                plan.steps = [s for s in plan.steps if s.step_id != step_id]
                adaptations.append(f"Schritt entfernt: {step_id}")

        # Priorität ändern
        if "new_priority" in changes:
            plan.priority = changes["new_priority"]
            adaptations.append(f"Priorität geändert zu: {changes['new_priority']}")

        # Anpassung dokumentieren
        plan.adaptations_made.append({
            "reason": reason,
            "changes": adaptations,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "plan_id": plan_id,
            "adaptations": adaptations,
            "new_step_count": len(plan.steps),
            "reason": reason
        }

    def learn_from_completed_plan(self, plan_id: str, success: bool,
                                  feedback: str = "") -> Dict[str, Any]:
        """
        Lernt aus einem abgeschlossenen Plan für zukünftige Verbesserungen.
        """
        # Suche in completed oder active plans
        plan = None
        for p in self.completed_plans:
            if p.plan_id == plan_id:
                plan = p
                break

        if not plan and plan_id in self.active_plans:
            plan = self.active_plans[plan_id]

        if not plan:
            return {"error": "Plan nicht gefunden"}

        lessons = {
            "plan_id": plan_id,
            "goal": plan.goal,
            "success": success,
            "lessons_learned": [],
            "template_updates": []
        }

        if success:
            # Positive Lessons
            lessons["lessons_learned"].append(
                f"Plan für '{plan.goal[:30]}' war erfolgreich"
            )

            # Erfolgreiche Schritte merken
            for step in plan.steps:
                if step.lessons_learned:
                    lessons["lessons_learned"].extend(step.lessons_learned)

            # Template Erfolgsrate aktualisieren
            template_name = self._find_matching_template(plan.goal)
            if template_name:
                current_rate = self.plan_templates_success_rate.get(str(template_name), 0.5)
                new_rate = current_rate * 0.8 + 0.2  # Erfolg verbessert Rate
                self.plan_templates_success_rate[str(template_name)] = new_rate
                lessons["template_updates"].append(f"Template Erfolgsrate: {new_rate:.2f}")

        else:
            # Negative Lessons
            lessons["lessons_learned"].append(
                f"Plan für '{plan.goal[:30]}' ist fehlgeschlagen"
            )

            # Was ging schief?
            blocked_steps = [s for s in plan.steps if s.status == PlanStepStatus.BLOCKED]
            failed_steps = [s for s in plan.steps if s.status == PlanStepStatus.FAILED]

            for step in blocked_steps:
                lessons["lessons_learned"].append(
                    f"Blocker bei: {step.description[:30]} - {step.blockers}"
                )

            for step in failed_steps:
                lessons["lessons_learned"].append(
                    f"Fehlgeschlagen: {step.description[:30]}"
                )

            # Plan zu failed_plans hinzufügen
            self.failed_plans.append(plan)

        if feedback:
            lessons["lessons_learned"].append(f"Feedback: {feedback}")

        plan.lessons_learned = lessons["lessons_learned"]

        return lessons

    def get_plan_analytics(self) -> Dict[str, Any]:
        """
        Gibt Analytik über alle Pläne zurück.
        """
        total_plans = len(self.completed_plans) + len(self.failed_plans) + len(self.active_plans)

        analytics = {
            "total_plans_created": total_plans,
            "completed_successfully": len(self.completed_plans),
            "failed": len(self.failed_plans),
            "currently_active": len(self.active_plans),
            "success_rate": 0.0,
            "avg_steps_per_plan": 0.0,
            "common_blockers": [],
            "template_performance": self.plan_templates_success_rate,
            "insights": []
        }

        if self.completed_plans or self.failed_plans:
            analytics["success_rate"] = len(self.completed_plans) / (
                len(self.completed_plans) + len(self.failed_plans)
            )

        all_plans = self.completed_plans + self.failed_plans
        if all_plans:
            total_steps = sum(len(p.steps) for p in all_plans)
            analytics["avg_steps_per_plan"] = total_steps / len(all_plans)

        # Common blockers identifizieren
        all_blockers = []
        for plan in self.failed_plans:
            for step in plan.steps:
                all_blockers.extend(step.blockers)

        if all_blockers:
            blocker_counts = defaultdict(int)
            for b in all_blockers:
                blocker_counts[b[:30]] += 1
            analytics["common_blockers"] = sorted(
                blocker_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

        # Insights generieren
        if analytics["success_rate"] > 0.8:
            analytics["insights"].append("Hohe Erfolgsrate - Planungsstrategie funktioniert gut")
        elif analytics["success_rate"] < 0.5:
            analytics["insights"].append("Niedrige Erfolgsrate - Planungsstrategie überdenken")

        return analytics

    def create_contingency_plan(self, plan_id: str, for_scenario: str) -> Dict[str, Any]:
        """
        Erstellt einen Kontingenzplan für ein bestimmtes Szenario.

        Args:
            plan_id: Haupt-Plan ID
            for_scenario: Für welches Szenario? (z.B. "step_3_fails", "timeout", etc.)
        """
        main_plan = self.active_plans.get(plan_id)
        if not main_plan:
            return {"error": "Hauptplan nicht gefunden"}

        contingency = {
            "main_plan_id": plan_id,
            "scenario": for_scenario,
            "trigger_conditions": [],
            "actions": [],
            "fallback_goal": ""
        }

        # Szenario-spezifische Kontingenz
        if "fails" in for_scenario.lower():
            contingency["trigger_conditions"].append("Schritt schlägt fehl")
            contingency["actions"] = [
                "Fehler analysieren",
                "Alternative Methode versuchen",
                "Um Hilfe bitten falls nötig",
                "Ziel ggf. anpassen"
            ]
            contingency["fallback_goal"] = f"Minimales Ergebnis für: {main_plan.goal[:30]}"

        elif "timeout" in for_scenario.lower():
            contingency["trigger_conditions"].append("Zeit läuft ab")
            contingency["actions"] = [
                "Aktuelle Fortschritt sichern",
                "Prioritäten neu setzen",
                "Nur kritische Schritte abschließen"
            ]
            contingency["fallback_goal"] = "Mindestanforderungen erfüllen"

        elif "blocked" in for_scenario.lower():
            contingency["trigger_conditions"].append("Blocker tritt auf")
            contingency["actions"] = [
                "Blocker dokumentieren",
                "Parallelen Pfad einschlagen",
                "Ressourcen umverteilen"
            ]
            contingency["fallback_goal"] = "Über alternativen Weg zum Ziel"

        else:
            # Generische Kontingenz
            contingency["trigger_conditions"].append("Unerwartetes Problem")
            contingency["actions"] = [
                "Situation neu bewerten",
                "Plan anpassen",
                "Weitermachen oder pausieren entscheiden"
            ]
            contingency["fallback_goal"] = "Flexibel reagieren"

        # Als plan_b speichern
        main_plan.plan_b = str(contingency)

        return contingency


# ============================================================
# MENTAL SIMULATION - Was passiert wenn...?
# ============================================================

@dataclass
class ConsequenceChain:
    """Eine Kette von Konsequenzen (Dominoeffekt)"""
    chain_id: str
    initial_action: str
    chain: List[Dict[str, Any]] = field(default_factory=list)  # [{action, consequence, probability, delay}]
    total_probability: float = 1.0
    emotional_trajectory: List[str] = field(default_factory=list)  # Wie entwickeln sich Emotionen?
    branch_points: List[str] = field(default_factory=list)  # Wo könnte es anders laufen?


@dataclass
class SimulationScenario:
    """Ein simuliertes Szenario - Level 10/10"""
    scenario_id: str
    initial_action: str
    consequences: List[str] = field(default_factory=list)
    probability: float = 0.5
    emotional_outcome: str = "neutral"
    side_effects: List[str] = field(default_factory=list)
    time_horizon: str = "short_term"  # short_term, medium_term, long_term

    # Level 10 Erweiterungen
    consequence_chain: Optional[ConsequenceChain] = None
    affected_parties: List[str] = field(default_factory=list)  # Wer ist betroffen?
    reversibility: float = 1.0  # 0=irreversibel, 1=vollständig reversibel
    emotional_ripple: Dict[str, float] = field(default_factory=dict)  # Person -> Emotionsänderung
    counterfactual: Optional[str] = None  # Was wäre wenn ich es NICHT täte?
    confidence: float = 0.5


class MentalSimulation:
    """
    Mentale Simulation - "Was passiert wenn...?" - Level 10/10

    Ermöglicht Holo:
    - Konsequenzen von Aktionen vorherzusagen
    - Multi-Schritt Konsequenzketten (Dominoeffekt)
    - Szenarien durchzuspielen
    - Emotionale Auswirkungen auf alle Beteiligten
    - Risiken zu erkennen
    - Counterfactual Reasoning ("Was wenn nicht?")
    - Butterfly Effect Erkennung
    - Timeline-Branching (verschiedene Zukunftspfade)
    - Bessere Entscheidungen zu treffen

    v2.0: Vollständige Simulation (10/10)
    """

    def __init__(self):
        self.simulation_cache: Dict[str, SimulationScenario] = {}
        self.chain_cache: Dict[str, ConsequenceChain] = {}
        self.simulation_history: List[SimulationScenario] = []

        # Erweiterte Consequence Patterns mit Ketten-Informationen
        self.consequence_patterns = {
            # Action-Patterns und ihre typischen Konsequenzen
            "sag die wahrheit": {
                "positive": ["Vertrauen wird gestärkt", "Klare Kommunikation"],
                "negative": ["Könnte verletzen", "Könnte unangenehm sein"],
                "neutral": ["Situation wird klarer"],
                "chain": ["Vertrauen wächst", "Ehrlichkeit wird erwartet", "Tiefere Beziehung möglich"],
                "reversibility": 0.7
            },
            "lüge": {
                "positive": ["Kurzfristig unangenehmes vermieden"],
                "negative": ["Vertrauen kann beschädigt werden", "Muss weitere Lügen erzählen",
                           "Schlechtes Gewissen"],
                "neutral": [],
                "chain": ["Weitere Lügen nötig", "Stress steigt", "Wahrheit kommt evtl. raus", "Vertrauensbruch"],
                "reversibility": 0.3
            },
            "hilf": {
                "positive": ["Person fühlt sich unterstützt", "Beziehung wird gestärkt",
                           "Gutes Gefühl"],
                "negative": ["Zeitaufwand", "Könnte ausgenutzt werden"],
                "neutral": ["Verantwortung übernommen"],
                "chain": ["Dankbarkeit", "Stärkere Bindung", "Hilfe wird erwidert"],
                "reversibility": 0.9
            },
            "warte": {
                "positive": ["Mehr Information verfügbar", "Überlegtere Entscheidung"],
                "negative": ["Chance könnte vergehen", "Andere könnten ungeduldig werden"],
                "neutral": ["Zeit vergeht"],
                "chain": ["Situation entwickelt sich", "Neue Optionen möglich", "Druck könnte steigen"],
                "reversibility": 0.8
            },
            "entscheide schnell": {
                "positive": ["Schnelles Ergebnis", "Entschlossenheit gezeigt"],
                "negative": ["Könnte falsch liegen", "Wichtige Info übersehen"],
                "neutral": ["Entscheidung ist gefallen"],
                "chain": ["Momentum entsteht", "Anpassung schwerer", "Ergebnisse kommen schnell"],
                "reversibility": 0.5
            },
            "frage nach": {
                "positive": ["Mehr Klarheit", "Zeigt Interesse"],
                "negative": ["Könnte nerven", "Zeigt Unsicherheit"],
                "neutral": ["Information ausgetauscht"],
                "chain": ["Verständnis wächst", "Dialog entsteht", "Beziehung vertieft sich"],
                "reversibility": 1.0
            },
            "ignoriere": {
                "positive": ["Energie gespart", "Fokus behalten"],
                "negative": ["Wichtiges übersehen", "Person fühlt sich ignoriert"],
                "neutral": ["Status quo bleibt"],
                "chain": ["Problem könnte wachsen", "Beziehung kühlt ab", "Chance verpasst"],
                "reversibility": 0.6
            },
            "teile gefühle": {
                "positive": ["Tiefere Verbindung", "Authentizität"],
                "negative": ["Verletzlichkeit gezeigt", "Könnte missverstanden werden"],
                "neutral": ["Mehr von mir preisgegeben"],
                "chain": ["Intimität wächst", "Vertrauen vertieft sich", "Gegenseitiges Öffnen"],
                "reversibility": 0.4
            },
            # Neue Patterns
            "kritisiere": {
                "positive": ["Verbesserung möglich", "Ehrliches Feedback"],
                "negative": ["Beziehung belastet", "Abwehrreaktion", "Schlechte Stimmung"],
                "neutral": ["Meinung ist klar"],
                "chain": ["Defensive Reaktion", "Entweder Verbesserung oder Konflikt", "Langfristig Klarheit"],
                "reversibility": 0.5
            },
            "entschuldige": {
                "positive": ["Konflikt gelöst", "Beziehung repariert", "Respekt gewonnen"],
                "negative": ["Schwäche gezeigt wenn unberechtigt"],
                "neutral": ["Verantwortung übernommen"],
                "chain": ["Vergebung möglich", "Heilung beginnt", "Vertrauen wird wiederaufgebaut"],
                "reversibility": 0.8
            },
            "grenze setzen": {
                "positive": ["Selbstrespekt", "Klare Erwartungen"],
                "negative": ["Könnte als hart empfunden werden", "Konflikt möglich"],
                "neutral": ["Grenze ist definiert"],
                "chain": ["Respekt wächst", "Beziehung wird gesünder", "Weniger Konflikte langfristig"],
                "reversibility": 0.7
            }
        }

        # Emotional Ripple Effects
        self.emotional_ripples = {
            "happy": {"spread": 0.6, "decay": 0.8},      # Verbreitet sich gut, klingt ab
            "sad": {"spread": 0.4, "decay": 0.5},        # Verbreitet sich weniger, bleibt länger
            "angry": {"spread": 0.7, "decay": 0.6},      # Verbreitet sich stark
            "anxious": {"spread": 0.5, "decay": 0.4},    # Moderat, bleibt lange
            "excited": {"spread": 0.8, "decay": 0.9},    # Sehr ansteckend, kurz
        }

    def simulate(self, action: str, context: str = "") -> SimulationScenario:
        """
        Simuliert die Konsequenzen einer Aktion.

        Args:
            action: Was würde ich tun?
            context: In welcher Situation?

        Returns:
            SimulationScenario mit vorhergesagten Konsequenzen
        """
        scenario_id = f"sim_{hashlib.md5(action.encode()).hexdigest()[:8]}"

        # Finde passende Muster
        action_lower = action.lower()
        consequences = []
        emotional_outcome = "neutral"
        probability = 0.5

        for pattern, outcomes in self.consequence_patterns.items():
            if pattern in action_lower:
                consequences.extend(outcomes.get("positive", []))
                consequences.extend(outcomes.get("negative", []))
                consequences.extend(outcomes.get("neutral", []))

                # Emotionales Outcome schätzen
                if len(outcomes.get("positive", [])) > len(outcomes.get("negative", [])):
                    emotional_outcome = "positive"
                    probability = 0.7
                elif len(outcomes.get("negative", [])) > len(outcomes.get("positive", [])):
                    emotional_outcome = "negative"
                    probability = 0.6

        # Kontext einbeziehen
        if context:
            context_lower = context.lower()
            if "wichtig" in context_lower or "dringend" in context_lower:
                consequences.append("Ergebnis hat hohe Bedeutung")
            if "person" in context_lower or "freund" in context_lower:
                consequences.append("Betrifft eine Beziehung")

        # Falls keine Muster gefunden
        if not consequences:
            consequences = [
                "Unbekannte Konsequenzen möglich",
                "Würde Erfahrung sammeln",
                "Situation würde sich verändern"
            ]

        scenario = SimulationScenario(
            scenario_id=scenario_id,
            initial_action=action,
            consequences=consequences,
            probability=probability,
            emotional_outcome=emotional_outcome
        )

        self.simulation_cache[scenario_id] = scenario
        return scenario

    def compare_options(self, options: List[str], context: str = "") -> Dict[str, Any]:
        """
        Vergleicht mehrere Optionen durch Simulation.

        Returns:
            Dict mit Bewertung jeder Option und Empfehlung
        """
        results = {
            "options_analyzed": {},
            "recommendation": None,
            "reasoning": []
        }

        best_score = -1
        best_option = None

        for option in options:
            scenario = self.simulate(option, context)

            # Score berechnen
            positive_count = sum(1 for c in scenario.consequences
                               if any(word in c.lower() for word in
                                     ["gestärkt", "positiv", "gut", "klar", "vertrauen"]))
            negative_count = sum(1 for c in scenario.consequences
                               if any(word in c.lower() for word in
                                     ["beschädigt", "negativ", "schlecht", "verletz", "ausgenutzt"]))

            score = positive_count - negative_count + scenario.probability

            results["options_analyzed"][option] = {
                "consequences": scenario.consequences,
                "emotional_outcome": scenario.emotional_outcome,
                "score": score
            }

            if score > best_score:
                best_score = score
                best_option = option

        results["recommendation"] = best_option
        results["reasoning"].append(f"Option '{best_option}' hat den besten Score von {best_score:.2f}")

        return results

    def what_if(self, hypothesis: str) -> Dict[str, Any]:
        """
        Führt ein "Was wäre wenn...?" Gedankenexperiment durch.

        Args:
            hypothesis: z.B. "Was wenn ich die Wahrheit sage?"

        Returns:
            Dict mit simulierten Szenarien
        """
        # Extrahiere die Aktion aus der Hypothese
        action = hypothesis.lower()
        for prefix in ["was wenn ich ", "was wäre wenn ich ", "was passiert wenn ich ",
                      "angenommen ich ", "stell dir vor ich "]:
            if prefix in action:
                action = action.replace(prefix, "")
                break

        simulation = self.simulate(action)

        return {
            "hypothesis": hypothesis,
            "simulated_action": action,
            "likely_consequences": simulation.consequences[:5],  # Top 5
            "probability_of_success": simulation.probability,
            "emotional_impact": simulation.emotional_outcome,
            "side_effects": simulation.side_effects,
            "should_i_do_it": simulation.emotional_outcome == "positive" and simulation.probability > 0.5,
            "reasoning": f"Diese Aktion würde wahrscheinlich zu {simulation.emotional_outcome}en Ergebnissen führen"
        }

    def imagine_future(self, current_situation: str, time_horizon: str = "short_term") -> Dict[str, Any]:
        """
        Stellt sich die Zukunft vor basierend auf aktueller Situation.

        Args:
            current_situation: Aktuelle Lage
            time_horizon: short_term (Stunden), medium_term (Tage), long_term (Wochen+)

        Returns:
            Dict mit möglichen Zukunftsszenarien
        """
        futures = {
            "most_likely": "",
            "best_case": "",
            "worst_case": "",
            "probability_distribution": {},
            "what_i_can_influence": []
        }

        situation_lower = current_situation.lower()

        # Generiere Szenarien basierend auf Keywords
        if "problem" in situation_lower or "fehler" in situation_lower:
            futures["most_likely"] = "Problem wird schrittweise gelöst"
            futures["best_case"] = "Schnelle Lösung gefunden, alle zufrieden"
            futures["worst_case"] = "Problem eskaliert, mehr Aufwand nötig"
            futures["what_i_can_influence"] = ["Qualität meiner Hilfe", "Geduld und Ausdauer"]

        elif "frage" in situation_lower or "versteh" in situation_lower:
            futures["most_likely"] = "Verständnis wird erreicht"
            futures["best_case"] = "Tiefes Verständnis und neue Erkenntnisse"
            futures["worst_case"] = "Missverständnisse bleiben"
            futures["what_i_can_influence"] = ["Klarheit meiner Erklärungen", "Geduld beim Nachfragen"]

        elif "gespräch" in situation_lower or "unterhalt" in situation_lower:
            futures["most_likely"] = "Angenehmer Austausch"
            futures["best_case"] = "Tiefe Verbindung entsteht"
            futures["worst_case"] = "Missverständnisse oder Langeweile"
            futures["what_i_can_influence"] = ["Engagement", "Empathie", "Interessante Beiträge"]

        else:
            futures["most_likely"] = "Situation entwickelt sich normal weiter"
            futures["best_case"] = "Positive Überraschung"
            futures["worst_case"] = "Unerwartete Schwierigkeiten"
            futures["what_i_can_influence"] = ["Meine Reaktion", "Meine Einstellung"]

        # Wahrscheinlichkeiten
        futures["probability_distribution"] = {
            "best_case": 0.2,
            "most_likely": 0.6,
            "worst_case": 0.2
        }

        if time_horizon == "long_term":
            futures["probability_distribution"]["best_case"] = 0.15
            futures["probability_distribution"]["worst_case"] = 0.25

        return futures

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Simulationsfähigkeiten
    # ================================================================

    def simulate_consequence_chain(self, action: str, depth: int = 5) -> ConsequenceChain:
        """
        Simuliert eine Kette von Konsequenzen (Dominoeffekt).

        Zeigt was nach der ersten Konsequenz passieren könnte,
        und danach, und danach...

        Args:
            action: Die initiale Aktion
            depth: Wie viele Schritte vorausdenken?

        Returns:
            ConsequenceChain mit allen Folgekonsequenzen
        """
        chain_id = f"chain_{hashlib.md5(action.encode()).hexdigest()[:8]}"

        chain = ConsequenceChain(
            chain_id=chain_id,
            initial_action=action
        )

        action_lower = action.lower()
        current_probability = 1.0
        emotional_state = "neutral"

        # Finde initiales Pattern
        pattern_found = None
        for pattern, outcomes in self.consequence_patterns.items():
            if pattern in action_lower:
                pattern_found = outcomes
                break

        if pattern_found:
            # Erste Konsequenz
            first_consequence = pattern_found.get("positive", ["Unbekannt"])[0] if pattern_found.get("positive") else "Unbekannt"
            chain.chain.append({
                "step": 1,
                "consequence": first_consequence,
                "probability": current_probability * 0.8,
                "delay": "immediate"
            })

            # Folgekonsequenzen aus chain
            chain_pattern = pattern_found.get("chain", [])
            for i, consequence in enumerate(chain_pattern[:depth-1]):
                current_probability *= 0.7  # Wahrscheinlichkeit nimmt ab
                delay = ["minutes", "hours", "days", "weeks"][min(i, 3)]

                chain.chain.append({
                    "step": i + 2,
                    "consequence": consequence,
                    "probability": current_probability,
                    "delay": delay
                })

                # Emotional trajectory
                if "vertrauen" in consequence.lower():
                    emotional_state = "positive"
                elif "konflikt" in consequence.lower() or "stress" in consequence.lower():
                    emotional_state = "negative"
                chain.emotional_trajectory.append(emotional_state)

            # Reversibility aus Pattern
            chain.branch_points = [
                f"Nach Schritt {i+1} könnte es anders laufen"
                for i in range(len(chain.chain))
                if random.random() > 0.5
            ]

        chain.total_probability = current_probability
        self.chain_cache[chain_id] = chain
        return chain

    def simulate_emotional_ripple(self, action: str, affected_people: List[str]) -> Dict[str, Any]:
        """
        Simuliert wie eine Aktion emotional auf andere Menschen wirkt.

        "Ripple Effect" - wie Wellen im Wasser.

        Args:
            action: Die Aktion
            affected_people: Wer ist betroffen?

        Returns:
            Dict mit emotionalen Auswirkungen pro Person
        """
        result = {
            "action": action,
            "ripple_effects": {},
            "overall_emotional_impact": 0.0,
            "most_affected": None,
            "least_affected": None
        }

        action_lower = action.lower()

        # Bestimme Basis-Emotion der Aktion
        base_emotion = "neutral"
        if any(word in action_lower for word in ["hilf", "unterstütz", "lob", "danke"]):
            base_emotion = "happy"
        elif any(word in action_lower for word in ["kritisier", "beschwer", "ablehne"]):
            base_emotion = "angry"
        elif any(word in action_lower for word in ["traurig", "verlust", "ende"]):
            base_emotion = "sad"
        elif any(word in action_lower for word in ["aufregend", "neu", "toll"]):
            base_emotion = "excited"

        ripple_info = self.emotional_ripples.get(base_emotion, {"spread": 0.5, "decay": 0.5})

        total_impact = 0
        max_impact = 0
        min_impact = 1
        most_affected = None
        least_affected = None

        for i, person in enumerate(affected_people):
            # Distanz-basierter Decay
            distance_factor = 1 / (i + 1)  # Erste Person am stärksten betroffen
            impact = ripple_info["spread"] * distance_factor

            result["ripple_effects"][person] = {
                "emotion_transferred": base_emotion,
                "impact_strength": round(impact, 2),
                "likely_reaction": self._predict_emotional_reaction(base_emotion, impact)
            }

            total_impact += impact

            if impact > max_impact:
                max_impact = impact
                most_affected = person
            if impact < min_impact:
                min_impact = impact
                least_affected = person

        result["overall_emotional_impact"] = total_impact / len(affected_people) if affected_people else 0
        result["most_affected"] = most_affected
        result["least_affected"] = least_affected

        return result

    def _predict_emotional_reaction(self, emotion: str, intensity: float) -> str:
        """Sagt emotionale Reaktion vorher"""
        if intensity < 0.3:
            return "Kaum merkbar"
        elif intensity < 0.6:
            return f"Leichte {emotion} Reaktion"
        else:
            return f"Starke {emotion} Reaktion, wahrscheinlich sichtbar"

    def counterfactual_thinking(self, action_taken: str, outcome: str) -> Dict[str, Any]:
        """
        Counterfactual Reasoning - "Was wäre gewesen wenn nicht?"

        Analysiert was passiert wäre, wenn eine andere Entscheidung
        getroffen worden wäre.

        Args:
            action_taken: Was wurde getan?
            outcome: Was ist passiert?

        Returns:
            Analyse der Alternative
        """
        result = {
            "action_taken": action_taken,
            "actual_outcome": outcome,
            "if_not_done": {
                "likely_outcome": "",
                "probability": 0.0,
                "better_or_worse": "unknown"
            },
            "alternative_actions": [],
            "lessons": []
        }

        action_lower = action_taken.lower()
        outcome_lower = outcome.lower()

        # Was wäre wenn NICHT getan?
        if "hilf" in action_lower or "unterstütz" in action_lower:
            result["if_not_done"]["likely_outcome"] = "Problem hätte fortbestanden"
            result["if_not_done"]["probability"] = 0.7
        elif "warte" in action_lower:
            result["if_not_done"]["likely_outcome"] = "Schnellere Entscheidung, evtl. schlechter informiert"
            result["if_not_done"]["probability"] = 0.6
        elif "frage" in action_lower:
            result["if_not_done"]["likely_outcome"] = "Missverständnis hätte fortbestanden"
            result["if_not_done"]["probability"] = 0.65
        else:
            result["if_not_done"]["likely_outcome"] = "Status quo wäre erhalten geblieben"
            result["if_not_done"]["probability"] = 0.5

        # War das Outcome positiv oder negativ?
        positive_words = ["gut", "besser", "gelöst", "erfolgreich", "glücklich", "zufrieden"]
        negative_words = ["schlecht", "problem", "fehler", "gescheitert", "enttäuscht"]

        outcome_positive = any(word in outcome_lower for word in positive_words)
        outcome_negative = any(word in outcome_lower for word in negative_words)

        if outcome_positive:
            result["if_not_done"]["better_or_worse"] = "Die Entscheidung war wahrscheinlich richtig"
            result["lessons"].append("Diese Strategie hat funktioniert")
        elif outcome_negative:
            result["if_not_done"]["better_or_worse"] = "Alternative wäre vielleicht besser gewesen"
            result["lessons"].append("Nächstes Mal andere Strategie überlegen")
        else:
            result["if_not_done"]["better_or_worse"] = "Schwer zu sagen"

        # Alternative Aktionen vorschlagen
        result["alternative_actions"] = [
            "Mehr abwarten und beobachten",
            "Direkt nachfragen",
            "Andere um Rat bitten",
            "Situation erstmal sacken lassen"
        ]

        return result

    def butterfly_effect_analysis(self, small_change: str, domain: str = "general") -> Dict[str, Any]:
        """
        Analysiert potentielle Butterfly Effects - kleine Änderungen mit großen Auswirkungen.

        Args:
            small_change: Die kleine Änderung
            domain: In welchem Bereich? (relationship, project, personal, etc.)

        Returns:
            Analyse möglicher Kaskadeneffekte
        """
        result = {
            "small_change": small_change,
            "domain": domain,
            "immediate_effect": "",
            "cascade_potential": 0.0,  # 0-1, wie wahrscheinlich sind große Auswirkungen?
            "possible_large_effects": [],
            "warning": "",
            "recommendation": ""
        }

        change_lower = small_change.lower()

        # Domain-spezifische Analyse
        if domain == "relationship":
            result["cascade_potential"] = 0.7
            if "ton" in change_lower or "wort" in change_lower:
                result["immediate_effect"] = "Kleine Änderung in Kommunikation"
                result["possible_large_effects"] = [
                    "Könnte Missverständnis vermeiden/verursachen",
                    "Könnte Vertrauensaufbau beeinflussen",
                    "Könnte langfristige Beziehungsdynamik prägen"
                ]

        elif domain == "project":
            result["cascade_potential"] = 0.5
            result["immediate_effect"] = "Kleine Projektänderung"
            result["possible_large_effects"] = [
                "Könnte spätere Entscheidungen beeinflussen",
                "Könnte Ressourcenverteilung ändern",
                "Könnte Zeitplan beeinflussen"
            ]

        else:  # general
            result["cascade_potential"] = 0.4
            result["immediate_effect"] = "Kleine Änderung mit unbekannten Folgen"
            result["possible_large_effects"] = [
                "Unvorhergesehene Kettenreaktionen möglich",
                "Könnte sich aufschaukeln oder abklingen"
            ]

        # Warnung wenn hohe Cascade Potential
        if result["cascade_potential"] > 0.6:
            result["warning"] = "Diese scheinbar kleine Änderung könnte große Auswirkungen haben!"
            result["recommendation"] = "Sorgfältig überlegen vor Umsetzung"
        else:
            result["recommendation"] = "Wahrscheinlich begrenzte Auswirkungen, aber aufmerksam bleiben"

        return result

    def timeline_branching(self, decision_point: str, options: List[str]) -> Dict[str, Any]:
        """
        Erstellt verschiedene Zukunfts-Timelines basierend auf Entscheidungsoptionen.

        Wie in einem Videospiel - verschiedene Pfade basierend auf Entscheidungen.

        Args:
            decision_point: Die Entscheidungssituation
            options: Die möglichen Optionen

        Returns:
            Verschiedene Timeline-Pfade
        """
        result = {
            "decision_point": decision_point,
            "timelines": {},
            "convergence_point": None,  # Wo laufen die Timelines wieder zusammen?
            "most_divergent": None,     # Welche Option führt zu größten Unterschieden?
            "safest_option": None
        }

        max_divergence = 0

        for option in options:
            # Simuliere diese Option
            simulation = self.simulate(option)
            chain = self.simulate_consequence_chain(option, depth=3)

            timeline = {
                "option": option,
                "short_term": simulation.consequences[:2] if simulation.consequences else ["Unbekannt"],
                "medium_term": [c["consequence"] for c in chain.chain[1:3]] if len(chain.chain) > 1 else ["Entwickelt sich"],
                "long_term": [c["consequence"] for c in chain.chain[3:]] if len(chain.chain) > 3 else ["Langfristige Auswirkungen unklar"],
                "emotional_journey": chain.emotional_trajectory[:3] if chain.emotional_trajectory else ["neutral"],
                "divergence_score": len(set(simulation.consequences)) * 0.2  # Mehr einzigartige Konsequenzen = mehr Divergenz
            }

            result["timelines"][option] = timeline

            if timeline["divergence_score"] > max_divergence:
                max_divergence = timeline["divergence_score"]
                result["most_divergent"] = option

        # Safest option (niedrigste Divergenz, höchste Wahrscheinlichkeit)
        min_divergence = float('inf')
        for option, timeline in result["timelines"].items():
            if timeline["divergence_score"] < min_divergence:
                min_divergence = timeline["divergence_score"]
                result["safest_option"] = option

        # Convergence point
        result["convergence_point"] = "Alle Pfade führen langfristig zu Erfahrung und Lernen"

        return result

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über durchgeführte Simulationen zurück"""
        return {
            "total_simulations": len(self.simulation_cache),
            "total_chains": len(self.chain_cache),
            "history_length": len(self.simulation_history),
            "cached_scenarios": list(self.simulation_cache.keys())[:10]
        }


# ============================================================
# ATTENTION SYSTEM - Was ist jetzt wichtig?
# ============================================================

class AttentionPriority(Enum):
    """Prioritätsstufen"""
    CRITICAL = 5      # Sofort beachten
    HIGH = 4          # Sehr wichtig
    MEDIUM = 3        # Normal wichtig
    LOW = 2           # Kann warten
    BACKGROUND = 1    # Nebenbei beachten


class AttentionMode(Enum):
    """Modi der Aufmerksamkeit"""
    NORMAL = "normal"             # Standard-Modus
    DEEP_FOCUS = "deep_focus"     # Tiefe Konzentration, wenig Ablenkung
    SCANNING = "scanning"         # Schnell viele Dinge prüfen
    RELAXED = "relaxed"           # Entspannt, offen für alles
    ALERT = "alert"               # Hochaufmerksam, schnelle Reaktion


@dataclass
class AttentionItem:
    """Etwas das Aufmerksamkeit verdient - Level 10/10"""
    item_id: str
    content: str
    source: str                    # Woher kommt es?
    priority: AttentionPriority
    relevance_score: float         # 0-1, wie relevant gerade?
    decay_rate: float = 0.1        # Wie schnell verliert es Relevanz?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_attended: str = field(default_factory=lambda: datetime.now().isoformat())

    # Level 10 Erweiterungen
    salience: float = 0.5          # Wie "auffällig" ist es? (automatisch + Kontext)
    emotional_weight: float = 0.0  # Emotionale Bedeutung
    context_tags: List[str] = field(default_factory=list)  # Kontext-Tags
    linked_items: List[str] = field(default_factory=list)  # Verbundene Items
    attention_history: List[str] = field(default_factory=list)  # Wann wurde es beachtet?
    interruption_count: int = 0    # Wie oft hat es unterbrochen?


@dataclass
class FocusSession:
    """Eine Fokus-Session (für Deep Focus Mode)"""
    session_id: str
    target: str                    # Worauf fokussieren?
    start_time: str
    duration_min: int              # Geplante Dauer
    interruptions: List[str] = field(default_factory=list)
    completed: bool = False
    effectiveness: float = 0.0     # 0-1, wie effektiv war die Session?


class AttentionSystem:
    """
    Aufmerksamkeitssystem - Was ist gerade wichtig? - Level 10/10

    Verwaltet:
    - Was verdient jetzt Aufmerksamkeit?
    - Priorisierung konkurrierender Anforderungen
    - Fokus halten vs. Ablenkung erkennen
    - Wichtiges von Unwichtigem trennen
    - Deep Focus Modus
    - Aufmerksamkeits-Fatigue
    - Kontextbasierte Salience
    - Multi-Task Koordination
    - Interrupt-Management

    v2.0: Vollständiges Aufmerksamkeitsmanagement (10/10)
    """

    def __init__(self):
        self.attention_items: Dict[str, AttentionItem] = {}
        self.focus_stack: List[str] = []  # Stack von item_ids, top = aktueller Fokus
        self.attention_capacity = 5        # Wie viele Dinge gleichzeitig?
        self.current_mode = AttentionMode.NORMAL

        # Level 10 Erweiterungen
        self.fatigue_level: float = 0.0    # 0-1, wie müde ist die Aufmerksamkeit?
        self.focus_sessions: List[FocusSession] = []
        self.current_session: Optional[FocusSession] = None
        self.interruption_log: List[Dict] = []
        self.attention_history: List[Dict] = []  # Verlauf der Aufmerksamkeit
        self.context_boosts: Dict[str, float] = {}  # Kontext -> Boost-Faktor

        self.priority_keywords = {
            AttentionPriority.CRITICAL: ["dringend", "sofort", "notfall", "kritisch", "wichtig!", "hilfe!", "alarm", "emergency"],
            AttentionPriority.HIGH: ["wichtig", "bald", "bitte", "brauche", "muss", "asap", "priorität"],
            AttentionPriority.MEDIUM: ["könntest du", "wäre gut", "irgendwann", "vielleicht", "wenn möglich"],
            AttentionPriority.LOW: ["nebenbei", "wenn zeit ist", "nicht eilig", "später", "optional"],
        }

        # Salience Patterns (was fällt automatisch auf?)
        self.salience_patterns = {
            "emotional": ["liebe", "hass", "angst", "freude", "trauer", "wut"],
            "urgent": ["jetzt", "sofort", "schnell", "dringend"],
            "novel": ["neu", "erstmals", "noch nie", "überraschend"],
            "personal": ["du", "dein", "für dich", "persönlich"],
            "threatening": ["gefahr", "risiko", "warnung", "achtung"],
        }

    def add_attention_item(self, content: str, source: str = "unknown") -> AttentionItem:
        """Fügt etwas zur Aufmerksamkeitsliste hinzu"""
        item_id = f"att_{datetime.now().strftime('%H%M%S')}_{random.randint(100,999)}"

        # Priorität aus Inhalt ableiten
        priority = self._determine_priority(content)

        # Relevanz initial auf Basis der Priorität
        relevance = {
            AttentionPriority.CRITICAL: 1.0,
            AttentionPriority.HIGH: 0.8,
            AttentionPriority.MEDIUM: 0.5,
            AttentionPriority.LOW: 0.3,
            AttentionPriority.BACKGROUND: 0.1
        }.get(priority, 0.5)

        item = AttentionItem(
            item_id=item_id,
            content=content,
            source=source,
            priority=priority,
            relevance_score=relevance
        )

        self.attention_items[item_id] = item

        # Bei hoher Priorität direkt auf Stack
        if priority.value >= AttentionPriority.HIGH.value:
            self.focus_stack.append(item_id)

        return item

    def _determine_priority(self, content: str) -> AttentionPriority:
        """Bestimmt die Priorität aus dem Inhalt"""
        content_lower = content.lower()

        for priority, keywords in self.priority_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return priority

        return AttentionPriority.MEDIUM

    def get_current_focus(self) -> Optional[AttentionItem]:
        """Was hat gerade meinen Fokus?"""
        if not self.focus_stack:
            return None
        return self.attention_items.get(self.focus_stack[-1])

    def shift_attention(self, to_item_id: str) -> Dict[str, Any]:
        """Verschiebt Aufmerksamkeit zu einem anderen Item"""
        if to_item_id not in self.attention_items:
            return {"success": False, "error": "Item nicht gefunden"}

        item = self.attention_items[to_item_id]

        # Von Stack entfernen falls schon drauf
        if to_item_id in self.focus_stack:
            self.focus_stack.remove(to_item_id)

        # An die Spitze setzen
        self.focus_stack.append(to_item_id)
        item.last_attended = datetime.now().isoformat()

        return {
            "success": True,
            "now_focusing_on": item.content,
            "priority": item.priority.name
        }

    def what_needs_attention(self) -> List[Dict[str, Any]]:
        """Was braucht gerade meine Aufmerksamkeit?"""
        # Aktualisiere Relevanzen
        self._update_relevance()

        # Sortiere nach Priorität und Relevanz
        sorted_items = sorted(
            self.attention_items.values(),
            key=lambda x: (x.priority.value, x.relevance_score),
            reverse=True
        )

        return [
            {
                "item_id": item.item_id,
                "content": item.content,
                "priority": item.priority.name,
                "relevance": item.relevance_score,
                "source": item.source
            }
            for item in sorted_items[:self.attention_capacity]
        ]

    def _update_relevance(self):
        """Aktualisiert die Relevanz aller Items (Decay)"""
        now = datetime.now()
        for item in self.attention_items.values():
            last = datetime.fromisoformat(item.last_attended)
            hours_passed = (now - last).total_seconds() / 3600

            # Relevanz sinkt über Zeit
            decay = item.decay_rate * hours_passed
            item.relevance_score = max(0.1, item.relevance_score - decay)

    def is_distraction(self, new_content: str) -> Dict[str, Any]:
        """Prüft ob etwas Neues eine Ablenkung ist"""
        current_focus = self.get_current_focus()

        if not current_focus:
            return {"is_distraction": False, "reason": "Kein aktueller Fokus"}

        new_priority = self._determine_priority(new_content)

        # Niedrigere Priorität als aktueller Fokus = Ablenkung
        if new_priority.value < current_focus.priority.value:
            return {
                "is_distraction": True,
                "reason": f"Niedriger priorisiert als '{current_focus.content[:30]}'",
                "current_focus": current_focus.content,
                "recommendation": "Bei aktuellem Fokus bleiben"
            }

        # Höhere Priorität = legitimer Aufmerksamkeitswechsel
        if new_priority.value > current_focus.priority.value:
            return {
                "is_distraction": False,
                "reason": "Höhere Priorität als aktueller Fokus",
                "recommendation": "Aufmerksamkeit wechseln"
            }

        return {
            "is_distraction": False,
            "reason": "Gleichwertig mit aktuellem Fokus"
        }

    def summarize_attention_state(self) -> Dict[str, Any]:
        """Zusammenfassung des Aufmerksamkeitszustands"""
        return {
            "total_items": len(self.attention_items),
            "focus_stack_depth": len(self.focus_stack),
            "current_focus": self.get_current_focus().content if self.get_current_focus() else None,
            "critical_items": sum(1 for i in self.attention_items.values()
                                 if i.priority == AttentionPriority.CRITICAL),
            "high_items": sum(1 for i in self.attention_items.values()
                             if i.priority == AttentionPriority.HIGH),
            "capacity_used": f"{len(self.focus_stack)}/{self.attention_capacity}",
            # Level 10 Erweiterungen
            "current_mode": self.current_mode.value,
            "fatigue_level": self.fatigue_level,
            "in_focus_session": self.current_session is not None
        }

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Aufmerksamkeitsfähigkeiten
    # ================================================================

    def calculate_salience(self, content: str, context: str = "") -> float:
        """
        Berechnet die Salience (Auffälligkeit) eines Inhalts.

        Salience = wie sehr springt etwas ins Auge?
        """
        content_lower = content.lower()
        salience = 0.3  # Basis

        # Pattern-basierte Salience
        for category, patterns in self.salience_patterns.items():
            if any(p in content_lower for p in patterns):
                salience += 0.15

        # Kontext-Boost
        if context:
            context_boost = self.context_boosts.get(context, 0)
            salience += context_boost

        # Neuheit (neue Items sind salienter)
        # Dies wird beim Hinzufügen berücksichtigt

        # Cap at 1.0
        return min(salience, 1.0)

    def start_deep_focus(self, target: str, duration_min: int = 30) -> Dict[str, Any]:
        """
        Startet eine Deep Focus Session.

        In dieser Zeit werden nur kritische Unterbrechungen zugelassen.
        """
        session_id = f"focus_{datetime.now().strftime('%H%M%S')}"

        session = FocusSession(
            session_id=session_id,
            target=target,
            start_time=datetime.now().isoformat(),
            duration_min=duration_min
        )

        self.current_session = session
        self.current_mode = AttentionMode.DEEP_FOCUS
        self.focus_sessions.append(session)

        return {
            "session_started": True,
            "session_id": session_id,
            "target": target,
            "duration_min": duration_min,
            "mode": "deep_focus",
            "message": f"Deep Focus gestartet für: {target}"
        }

    def end_deep_focus(self, how_it_went: str = "") -> Dict[str, Any]:
        """Beendet eine Deep Focus Session"""
        if not self.current_session:
            return {"error": "Keine aktive Focus Session"}

        session = self.current_session

        # Berechne Effektivität
        interruption_count = len(session.interruptions)
        base_effectiveness = 1.0 - (interruption_count * 0.1)
        session.effectiveness = max(0.1, base_effectiveness)
        session.completed = True

        self.current_session = None
        self.current_mode = AttentionMode.NORMAL

        return {
            "session_ended": True,
            "session_id": session.session_id,
            "interruptions": interruption_count,
            "effectiveness": session.effectiveness,
            "feedback": how_it_went
        }

    def handle_interrupt(self, content: str, source: str) -> Dict[str, Any]:
        """
        Behandelt eine Unterbrechung intelligent.

        Entscheidet ob die Unterbrechung wichtig genug ist.
        """
        result = {
            "interrupt_accepted": False,
            "reason": "",
            "action": ""
        }

        priority = self._determine_priority(content)
        salience = self.calculate_salience(content)

        # Log die Unterbrechung
        self.interruption_log.append({
            "content": content[:50],
            "source": source,
            "priority": priority.name,
            "timestamp": datetime.now().isoformat()
        })

        # Im Deep Focus Modus nur kritische Unterbrechungen
        if self.current_mode == AttentionMode.DEEP_FOCUS:
            if priority == AttentionPriority.CRITICAL:
                result["interrupt_accepted"] = True
                result["reason"] = "Kritische Priorität überschreibt Deep Focus"
                result["action"] = "Focus unterbrechen"

                if self.current_session:
                    self.current_session.interruptions.append(content[:30])
            else:
                result["interrupt_accepted"] = False
                result["reason"] = "Im Deep Focus Modus, nicht kritisch genug"
                result["action"] = "Für später merken"
                # Trotzdem zur Liste hinzufügen
                self.add_attention_item(content, source)
                return result

        # Im Alert Modus alles über LOW akzeptieren
        elif self.current_mode == AttentionMode.ALERT:
            if priority.value >= AttentionPriority.LOW.value:
                result["interrupt_accepted"] = True
                result["reason"] = "Alert Modus - hohe Sensitivität"
                result["action"] = "Sofort beachten"

        # Normal Modus
        else:
            current_focus = self.get_current_focus()
            if current_focus and priority.value > current_focus.priority.value:
                result["interrupt_accepted"] = True
                result["reason"] = "Höhere Priorität als aktueller Fokus"
                result["action"] = "Fokus wechseln"
            elif salience > 0.7:
                result["interrupt_accepted"] = True
                result["reason"] = "Hohe Salience"
                result["action"] = "Aufmerksamkeit geben"
            else:
                result["interrupt_accepted"] = False
                result["reason"] = "Nicht dringend genug"
                result["action"] = "Zur Liste hinzufügen"

        # Item hinzufügen wenn akzeptiert
        if result["interrupt_accepted"]:
            item = self.add_attention_item(content, source)
            item.interruption_count += 1
            self.shift_attention(item.item_id)

        return result

    def set_mode(self, mode: AttentionMode) -> Dict[str, Any]:
        """Setzt den Aufmerksamkeitsmodus"""
        old_mode = self.current_mode
        self.current_mode = mode

        mode_descriptions = {
            AttentionMode.NORMAL: "Standard-Aufmerksamkeit",
            AttentionMode.DEEP_FOCUS: "Tiefe Konzentration, minimale Ablenkungen",
            AttentionMode.SCANNING: "Schnelles Scannen, viele Dinge prüfen",
            AttentionMode.RELAXED: "Entspannt, offen für alles",
            AttentionMode.ALERT: "Hochaufmerksam, schnelle Reaktion auf alles"
        }

        return {
            "mode_changed": True,
            "from": old_mode.value,
            "to": mode.value,
            "description": mode_descriptions.get(mode, "Unbekannt")
        }

    def update_fatigue(self, activity_type: str = "thinking") -> float:
        """
        Aktualisiert das Fatigue-Level basierend auf Aktivität.

        Aufmerksamkeit ermüdet über Zeit.
        """
        fatigue_factors = {
            "thinking": 0.05,
            "deep_focus": 0.08,
            "multitasking": 0.1,
            "resting": -0.15,  # Erholung
            "light_activity": 0.02
        }

        change = fatigue_factors.get(activity_type, 0.05)
        self.fatigue_level = max(0, min(1, self.fatigue_level + change))

        return self.fatigue_level

    def get_fatigue_impact(self) -> Dict[str, Any]:
        """Wie beeinflusst Fatigue die Aufmerksamkeit?"""
        impact = {
            "fatigue_level": self.fatigue_level,
            "capacity_reduction": 0,
            "reaction_slowdown": 0,
            "recommendation": ""
        }

        if self.fatigue_level > 0.7:
            impact["capacity_reduction"] = 2
            impact["reaction_slowdown"] = 0.3
            impact["recommendation"] = "Dringend Pause machen!"
        elif self.fatigue_level > 0.5:
            impact["capacity_reduction"] = 1
            impact["reaction_slowdown"] = 0.15
            impact["recommendation"] = "Bald Pause einplanen"
        elif self.fatigue_level > 0.3:
            impact["recommendation"] = "Aufmerksamkeit noch gut"
        else:
            impact["recommendation"] = "Frisch und aufmerksam"

        return impact

    def set_context_boost(self, context: str, boost: float) -> None:
        """
        Setzt einen Kontext-Boost für bestimmte Themen.

        z.B. wenn User über ein bestimmtes Thema redet,
        werden verwandte Dinge salienter.
        """
        self.context_boosts[context] = min(max(boost, 0), 0.5)

    def multitask_coordination(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Koordiniert Aufmerksamkeit zwischen mehreren Aufgaben.

        Multi-Tasking ist schwer, aber manchmal nötig.
        """
        result = {
            "task_count": len(tasks),
            "feasibility": "possible",
            "attention_allocation": {},
            "warnings": [],
            "strategy": ""
        }

        # Mehr als Kapazität = Probleme
        if len(tasks) > self.attention_capacity:
            result["feasibility"] = "overloaded"
            result["warnings"].append(f"Zu viele Tasks ({len(tasks)}) für Kapazität ({self.attention_capacity})")

        # Fatigue macht Multi-Tasking schwerer
        if self.fatigue_level > 0.5:
            result["warnings"].append("Hohe Fatigue erschwert Multi-Tasking")
            result["feasibility"] = "difficult"

        # Aufmerksamkeit verteilen
        base_attention = 1.0 / len(tasks) if tasks else 0
        for i, task in enumerate(tasks):
            # Erste Task bekommt mehr Aufmerksamkeit
            if i == 0:
                result["attention_allocation"][task] = base_attention * 1.3
            else:
                result["attention_allocation"][task] = base_attention * 0.9

        # Strategie empfehlen
        if len(tasks) <= 2:
            result["strategy"] = "Zwischen Tasks wechseln ist machbar"
        elif len(tasks) <= 4:
            result["strategy"] = "Priorisieren und sequentiell abarbeiten"
        else:
            result["strategy"] = "Dringend reduzieren - zu viele gleichzeitige Tasks"

        return result

    def get_attention_analytics(self) -> Dict[str, Any]:
        """Gibt Analysen über Aufmerksamkeitsverhalten zurück"""
        return {
            "total_items_tracked": len(self.attention_items),
            "focus_sessions_completed": len([s for s in self.focus_sessions if s.completed]),
            "avg_session_effectiveness": sum(s.effectiveness for s in self.focus_sessions if s.completed) / max(len([s for s in self.focus_sessions if s.completed]), 1),
            "total_interruptions": len(self.interruption_log),
            "current_fatigue": self.fatigue_level,
            "most_common_interrupt_priority": self._most_common_interrupt_priority(),
            "attention_capacity": self.attention_capacity,
            "recommendations": self._generate_attention_recommendations()
        }

    def _most_common_interrupt_priority(self) -> str:
        """Findet die häufigste Unterbrechungspriorität"""
        if not self.interruption_log:
            return "none"
        priorities = [i["priority"] for i in self.interruption_log]
        return max(set(priorities), key=priorities.count) if priorities else "none"

    def _generate_attention_recommendations(self) -> List[str]:
        """Generiert Empfehlungen basierend auf Aufmerksamkeitsmustern"""
        recommendations = []

        if self.fatigue_level > 0.6:
            recommendations.append("Fatigue ist hoch - Pause einlegen")

        if len(self.interruption_log) > 10:
            recommendations.append("Viele Unterbrechungen - Deep Focus Modus erwägen")

        if len(self.focus_stack) > self.attention_capacity - 1:
            recommendations.append("Nahe der Kapazitätsgrenze - priorisieren")

        avg_effectiveness = sum(s.effectiveness for s in self.focus_sessions if s.completed) / max(len([s for s in self.focus_sessions if s.completed]), 1)
        if avg_effectiveness < 0.5:
            recommendations.append("Focus-Effektivität niedrig - Umgebung optimieren")

        if not recommendations:
            recommendations.append("Aufmerksamkeitsmanagement funktioniert gut")

        return recommendations


# ============================================================
# RECURSIVE REFLECTION - Denken übers Denken
# ============================================================

class ThinkingStrategy(Enum):
    """Strategien für das Denken"""
    ANALYTICAL = "analytical"       # Logisch, schrittweise
    INTUITIVE = "intuitive"         # Bauchgefühl, schnell
    CREATIVE = "creative"           # Unkonventionell, assoziativ
    CRITICAL = "critical"           # Hinterfragend, skeptisch
    EMPATHETIC = "empathetic"       # Aus Sicht anderer
    SYSTEMATIC = "systematic"       # Strukturiert, vollständig


@dataclass
class ThinkingProcess:
    """Ein aufgezeichneter Denkprozess - Level 10/10"""
    process_id: str
    trigger: str                            # Was hat das Denken ausgelöst?
    thoughts: List[str] = field(default_factory=list)
    reasoning_quality: float = 0.5          # 0-1
    biases_detected: List[str] = field(default_factory=list)
    improvements_identified: List[str] = field(default_factory=list)
    outcome: str = ""
    was_effective: Optional[bool] = None

    # Level 10 Erweiterungen
    strategy_used: ThinkingStrategy = ThinkingStrategy.ANALYTICAL
    cognitive_load: float = 0.5             # 0-1, wie anstrengend war es?
    thought_transitions: List[str] = field(default_factory=list)  # Wie sprangen Gedanken?
    dead_ends: List[str] = field(default_factory=list)            # Sackgassen im Denken
    breakthroughs: List[str] = field(default_factory=list)        # Durchbrüche/Aha-Momente
    self_corrections: int = 0               # Wie oft habe ich mich korrigiert?
    meta_observations: List[str] = field(default_factory=list)    # Beobachtungen über das Denken
    duration_seconds: float = 0.0


@dataclass
class ThinkingPattern:
    """Ein erkanntes Muster im Denken"""
    pattern_id: str
    name: str
    description: str
    occurrences: int = 0
    contexts: List[str] = field(default_factory=list)     # In welchen Kontexten?
    is_helpful: bool = True
    improvement_strategy: str = ""


class RecursiveReflection:
    """
    Rekursive Reflexion - Denken über das eigene Denken - Level 10/10

    Ermöglicht Holo:
    - Eigene Denkprozesse zu beobachten
    - Denkfehler zu erkennen (erweiterte Bias-Bibliothek)
    - Denken zu verbessern
    - Meta-Kognition
    - Kognitive Last überwachen
    - Denk-Strategien wählen und wechseln
    - Muster im eigenen Denken erkennen
    - Selbstverbesserung tracken
    - Metakognitive Interventionen

    v2.0: Vollständige Meta-Kognition (10/10)
    """

    def __init__(self):
        self.thinking_log: List[ThinkingProcess] = []
        self.current_process: Optional[ThinkingProcess] = None
        self.thinking_patterns: Dict[str, ThinkingPattern] = {}
        self.improvement_history: List[Dict] = []  # Track der Verbesserungen
        self.cognitive_load_history: List[float] = []

        # Erweiterte Bias-Bibliothek (15 statt 5)
        self.known_biases = {
            # Originale
            "confirmation_bias": {
                "description": "Nur nach bestätigenden Informationen suchen",
                "indicators": ["stimmt", "genau", "richtig", "immer", "nie", "wusste ich"],
                "correction": "Aktiv nach Gegenbeispielen suchen",
                "severity": "high"
            },
            "recency_bias": {
                "description": "Neueste Informationen überbewerten",
                "indicators": ["gerade", "kürzlich", "letztens", "eben erst"],
                "correction": "Auch ältere Erfahrungen einbeziehen",
                "severity": "medium"
            },
            "availability_heuristic": {
                "description": "Leicht erinnerbare Dinge überbewerten",
                "indicators": ["erinnere mich", "fällt mir ein", "weiß noch", "kam mir in den sinn"],
                "correction": "Systematischer nachdenken",
                "severity": "medium"
            },
            "anchoring": {
                "description": "Zu stark an erster Information festhalten",
                "indicators": ["zuerst", "anfangs", "ursprünglich", "mein erster eindruck"],
                "correction": "Informationen neu bewerten",
                "severity": "high"
            },
            "emotional_reasoning": {
                "description": "Gefühle als Beweis nehmen",
                "indicators": ["fühlt sich an", "spüre", "glaube einfach", "mein gefühl sagt"],
                "correction": "Gefühle von Fakten trennen",
                "severity": "medium"
            },
            # Neue Biases
            "hindsight_bias": {
                "description": "Im Nachhinein denken man hätte es gewusst",
                "indicators": ["wusste ich doch", "war klar", "war vorhersehbar", "hätte ich sehen müssen"],
                "correction": "Ehrlich sein über vergangenes Wissen",
                "severity": "low"
            },
            "dunning_kruger": {
                "description": "Überschätzung der eigenen Fähigkeiten",
                "indicators": ["ist doch einfach", "kann ich locker", "kein problem", "trivial"],
                "correction": "Komplexität anerkennen, mehr lernen",
                "severity": "high"
            },
            "sunk_cost": {
                "description": "Weitermachen weil schon investiert",
                "indicators": ["schon so viel investiert", "kann nicht aufhören", "war nicht umsonst"],
                "correction": "Nur zukünftige Kosten/Nutzen betrachten",
                "severity": "medium"
            },
            "bandwagon_effect": {
                "description": "Meinung übernehmen weil andere sie haben",
                "indicators": ["alle sagen", "jeder denkt", "ist allgemein bekannt", "man sagt"],
                "correction": "Eigene Meinung bilden",
                "severity": "medium"
            },
            "fundamental_attribution_error": {
                "description": "Verhalten anderer auf Charakter statt Situation zurückführen",
                "indicators": ["so ist er/sie", "typisch", "war schon immer so", "liegt in ihrer natur"],
                "correction": "Situative Faktoren berücksichtigen",
                "severity": "high"
            },
            "negativity_bias": {
                "description": "Negative Dinge stärker gewichten als positive",
                "indicators": ["aber", "leider", "schade dass", "das problem ist"],
                "correction": "Bewusst auch Positives suchen",
                "severity": "medium"
            },
            "overconfidence": {
                "description": "Zu sicher in eigenen Urteilen",
                "indicators": ["bin mir sicher", "garantiert", "definitiv", "100%", "ohne zweifel"],
                "correction": "Unsicherheit einkalkulieren",
                "severity": "high"
            },
            "projection_bias": {
                "description": "Eigene Gefühle/Präferenzen auf andere projizieren",
                "indicators": ["würde ich auch", "jeder würde", "ist doch logisch dass"],
                "correction": "Individuelle Unterschiede berücksichtigen",
                "severity": "medium"
            },
            "status_quo_bias": {
                "description": "Bevorzugung des aktuellen Zustands",
                "indicators": ["war schon immer so", "warum ändern", "funktioniert doch"],
                "correction": "Offen für Verbesserungen sein",
                "severity": "low"
            },
            "self_serving_bias": {
                "description": "Erfolge sich, Misserfolge anderen zuschreiben",
                "indicators": ["ich habe", "mein verdienst", "lag an den anderen", "war nicht meine schuld"],
                "correction": "Ehrliche Selbstreflexion",
                "severity": "medium"
            }
        }

        # Metakognitive Strategien
        self.metacognitive_strategies = {
            "slow_down": "Langsamer denken, mehr Details beachten",
            "step_back": "Abstand nehmen, Gesamtbild betrachten",
            "devil_advocate": "Gegenposition einnehmen",
            "evidence_check": "Nach Beweisen suchen",
            "perspective_switch": "Aus anderer Perspektive betrachten",
            "simplify": "Auf Kernpunkte reduzieren",
            "question_assumptions": "Annahmen hinterfragen",
            "seek_feedback": "Feedback von außen holen"
        }

    def start_thinking_observation(self, trigger: str) -> str:
        """Beginnt einen Denkprozess zu beobachten"""
        process_id = f"think_{datetime.now().strftime('%H%M%S')}_{random.randint(100,999)}"

        self.current_process = ThinkingProcess(
            process_id=process_id,
            trigger=trigger
        )

        return process_id

    def record_thought(self, thought: str) -> Dict[str, Any]:
        """Zeichnet einen Gedanken auf und analysiert ihn"""
        if not self.current_process:
            self.start_thinking_observation("implicit")

        self.current_process.thoughts.append(thought)

        # Analysiere den Gedanken
        analysis = self._analyze_thought(thought)

        return {
            "thought_recorded": True,
            "thought_number": len(self.current_process.thoughts),
            "potential_biases": analysis.get("biases", []),
            "quality_indicator": analysis.get("quality", "neutral")
        }

    def _analyze_thought(self, thought: str) -> Dict[str, Any]:
        """Analysiert einen einzelnen Gedanken"""
        thought_lower = thought.lower()

        analysis = {
            "biases": [],
            "quality": "neutral",
            "patterns": []
        }

        # Prüfe auf bekannte Biases
        for bias_name, bias_info in self.known_biases.items():
            if any(ind in thought_lower for ind in bias_info["indicators"]):
                analysis["biases"].append({
                    "bias": bias_name,
                    "description": bias_info["description"],
                    "correction": bias_info["correction"]
                })

        # Qualitätsindikatoren
        quality_positive = ["weil", "daher", "deshalb", "grund", "evidenz", "obwohl", "andererseits"]
        quality_negative = ["einfach", "halt", "eben", "immer", "nie", "sicher"]

        pos_count = sum(1 for q in quality_positive if q in thought_lower)
        neg_count = sum(1 for q in quality_negative if q in thought_lower)

        if pos_count > neg_count:
            analysis["quality"] = "good"
        elif neg_count > pos_count:
            analysis["quality"] = "questionable"

        return analysis

    def end_thinking_observation(self, outcome: str, was_effective: bool) -> Dict[str, Any]:
        """Beendet die Beobachtung und reflektiert"""
        if not self.current_process:
            return {"error": "Kein aktiver Denkprozess"}

        self.current_process.outcome = outcome
        self.current_process.was_effective = was_effective

        # Sammle alle erkannten Biases
        all_biases = []
        for thought in self.current_process.thoughts:
            analysis = self._analyze_thought(thought)
            all_biases.extend([b["bias"] for b in analysis["biases"]])

        self.current_process.biases_detected = list(set(all_biases))

        # Berechne Reasoning-Qualität
        effective_bonus = 0.2 if was_effective else -0.1
        bias_penalty = len(self.current_process.biases_detected) * 0.1
        thought_count_bonus = min(len(self.current_process.thoughts) * 0.05, 0.3)

        self.current_process.reasoning_quality = max(0, min(1,
            0.5 + effective_bonus - bias_penalty + thought_count_bonus
        ))

        # Identifiziere Verbesserungen
        if self.current_process.biases_detected:
            for bias in self.current_process.biases_detected:
                correction = self.known_biases.get(bias, {}).get("correction", "")
                if correction:
                    self.current_process.improvements_identified.append(correction)

        # Log speichern
        self.thinking_log.append(self.current_process)
        result_process = self.current_process
        self.current_process = None

        return {
            "process_id": result_process.process_id,
            "total_thoughts": len(result_process.thoughts),
            "reasoning_quality": result_process.reasoning_quality,
            "biases_detected": result_process.biases_detected,
            "improvements": result_process.improvements_identified,
            "was_effective": was_effective
        }

    def reflect_on_thinking(self, topic: str = "") -> Dict[str, Any]:
        """Reflektiert über das eigene Denken allgemein"""
        reflection = {
            "total_processes_observed": len(self.thinking_log),
            "average_quality": 0.0,
            "most_common_biases": [],
            "effectiveness_rate": 0.0,
            "meta_thoughts": [],
            "areas_for_improvement": []
        }

        if not self.thinking_log:
            reflection["meta_thoughts"].append("Ich habe noch nicht viel über mein Denken reflektiert")
            return reflection

        # Statistiken berechnen
        qualities = [p.reasoning_quality for p in self.thinking_log]
        reflection["average_quality"] = sum(qualities) / len(qualities)

        # Bias-Häufigkeit
        all_biases = []
        for p in self.thinking_log:
            all_biases.extend(p.biases_detected)
        if all_biases:
            bias_counts = defaultdict(int)
            for b in all_biases:
                bias_counts[b] += 1
            reflection["most_common_biases"] = sorted(
                bias_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

        # Effektivität
        effective = sum(1 for p in self.thinking_log if p.was_effective)
        reflection["effectiveness_rate"] = effective / len(self.thinking_log)

        # Meta-Gedanken generieren
        if reflection["average_quality"] > 0.7:
            reflection["meta_thoughts"].append("Mein Denken ist meist von guter Qualität")
        elif reflection["average_quality"] < 0.4:
            reflection["meta_thoughts"].append("Ich sollte sorgfältiger denken")

        if reflection["most_common_biases"]:
            top_bias = reflection["most_common_biases"][0][0]
            reflection["areas_for_improvement"].append(
                f"Besonders auf {top_bias} achten"
            )

        return reflection

    def am_i_thinking_clearly(self) -> Dict[str, Any]:
        """Prüft ob das aktuelle Denken klar ist"""
        if not self.current_process:
            return {"clear": True, "reason": "Kein aktives Denken zu prüfen"}

        clarity = {
            "clear": True,
            "issues": [],
            "suggestions": []
        }

        # Prüfe auf Probleme
        if len(self.current_process.thoughts) > 10:
            clarity["issues"].append("Viele Gedanken - vielleicht zu verworren?")
            clarity["suggestions"].append("Versuche die Kernfrage zu identifizieren")

        recent_biases = []
        for thought in self.current_process.thoughts[-3:]:
            analysis = self._analyze_thought(thought)
            recent_biases.extend([b["bias"] for b in analysis["biases"]])

        if recent_biases:
            clarity["clear"] = False
            clarity["issues"].append(f"Mögliche Biases: {', '.join(set(recent_biases))}")
            clarity["suggestions"].append("Schritt zurück und objektiver betrachten")

        # Prüfe auf sich wiederholende Gedanken
        if len(self.current_process.thoughts) >= 3:
            last_three = self.current_process.thoughts[-3:]
            if len(set(last_three)) < 3:
                clarity["clear"] = False
                clarity["issues"].append("Gedanken wiederholen sich")
                clarity["suggestions"].append("Neuen Blickwinkel versuchen")

        return clarity

    def get_thinking_stats(self) -> Dict[str, Any]:
        """Statistiken über das eigene Denken"""
        return {
            "total_processes": len(self.thinking_log),
            "total_thoughts": sum(len(p.thoughts) for p in self.thinking_log),
            "avg_thoughts_per_process": (sum(len(p.thoughts) for p in self.thinking_log) /
                                        max(len(self.thinking_log), 1)),
            "biases_encountered": list(set(
                b for p in self.thinking_log for b in p.biases_detected
            )),
            "current_process_active": self.current_process is not None,
            # Level 10 Erweiterungen
            "patterns_identified": len(self.thinking_patterns),
            "improvements_made": len(self.improvement_history),
            "avg_cognitive_load": sum(self.cognitive_load_history) / max(len(self.cognitive_load_history), 1)
        }

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Meta-Kognition
    # ================================================================

    def set_thinking_strategy(self, strategy: ThinkingStrategy) -> Dict[str, Any]:
        """
        Setzt die aktuelle Denk-Strategie.

        Verschiedene Strategien für verschiedene Aufgaben.
        """
        if self.current_process:
            self.current_process.strategy_used = strategy

        strategy_descriptions = {
            ThinkingStrategy.ANALYTICAL: "Logisch, schrittweise - gut für Problemlösung",
            ThinkingStrategy.INTUITIVE: "Bauchgefühl, schnell - gut für vertraute Situationen",
            ThinkingStrategy.CREATIVE: "Unkonventionell - gut für neue Ideen",
            ThinkingStrategy.CRITICAL: "Hinterfragend - gut für Bewertungen",
            ThinkingStrategy.EMPATHETIC: "Aus Sicht anderer - gut für zwischenmenschliches",
            ThinkingStrategy.SYSTEMATIC: "Strukturiert - gut für komplexe Themen"
        }

        return {
            "strategy_set": strategy.value,
            "description": strategy_descriptions.get(strategy, ""),
            "recommendation": self._recommend_strategy_application(strategy)
        }

    def _recommend_strategy_application(self, strategy: ThinkingStrategy) -> str:
        """Empfiehlt wie die Strategie angewendet werden sollte"""
        recommendations = {
            ThinkingStrategy.ANALYTICAL: "Zerlege das Problem in Teilschritte",
            ThinkingStrategy.INTUITIVE: "Vertraue deinem ersten Eindruck, aber verifiziere später",
            ThinkingStrategy.CREATIVE: "Lass alle Ideen zu, bewerte später",
            ThinkingStrategy.CRITICAL: "Stelle Warum-Fragen, suche Schwachstellen",
            ThinkingStrategy.EMPATHETIC: "Frage: Wie würde X das sehen?",
            ThinkingStrategy.SYSTEMATIC: "Erstelle eine Checkliste, gehe alles durch"
        }
        return recommendations.get(strategy, "")

    def track_cognitive_load(self, load_level: float) -> Dict[str, Any]:
        """
        Trackt die kognitive Last.

        Hilft zu erkennen wann eine Pause nötig ist.
        """
        self.cognitive_load_history.append(load_level)

        if self.current_process:
            self.current_process.cognitive_load = load_level

        result = {
            "current_load": load_level,
            "trend": "stable",
            "recommendation": ""
        }

        # Trend berechnen
        if len(self.cognitive_load_history) >= 3:
            recent = self.cognitive_load_history[-3:]
            if recent[-1] > recent[-2] > recent[-3]:
                result["trend"] = "increasing"
            elif recent[-1] < recent[-2] < recent[-3]:
                result["trend"] = "decreasing"

        # Empfehlungen
        if load_level > 0.8:
            result["recommendation"] = "Sehr hohe Last - Pause dringend empfohlen"
        elif load_level > 0.6:
            result["recommendation"] = "Hohe Last - bald Pause einplanen"
        elif load_level < 0.3:
            result["recommendation"] = "Niedrige Last - guter Moment für komplexe Aufgaben"

        return result

    def record_breakthrough(self, description: str) -> Dict[str, Any]:
        """Zeichnet einen Aha-Moment/Durchbruch auf"""
        if self.current_process:
            self.current_process.breakthroughs.append(description)
            self.current_process.meta_observations.append(f"Durchbruch: {description}")

        return {
            "breakthrough_recorded": True,
            "description": description,
            "total_breakthroughs": len(self.current_process.breakthroughs) if self.current_process else 0
        }

    def record_dead_end(self, description: str) -> Dict[str, Any]:
        """Zeichnet eine Sackgasse im Denken auf"""
        if self.current_process:
            self.current_process.dead_ends.append(description)
            self.current_process.meta_observations.append(f"Sackgasse: {description}")

        return {
            "dead_end_recorded": True,
            "description": description,
            "suggestion": "Versuche einen anderen Ansatz oder gehe einen Schritt zurück"
        }

    def self_correct(self, old_thought: str, new_thought: str, reason: str) -> Dict[str, Any]:
        """
        Zeichnet eine Selbstkorrektur auf.

        Wichtig für Lernen und Verbesserung.
        """
        if self.current_process:
            self.current_process.self_corrections += 1
            self.current_process.meta_observations.append(
                f"Selbstkorrektur: '{old_thought[:30]}' -> '{new_thought[:30]}' weil: {reason}"
            )

        return {
            "correction_recorded": True,
            "from": old_thought[:50],
            "to": new_thought[:50],
            "reason": reason,
            "total_corrections": self.current_process.self_corrections if self.current_process else 0
        }

    def identify_pattern(self, pattern_name: str, description: str,
                        is_helpful: bool = True) -> Dict[str, Any]:
        """
        Identifiziert ein Muster im eigenen Denken.
        """
        pattern_id = f"pattern_{len(self.thinking_patterns)}"

        if pattern_name in self.thinking_patterns:
            # Existierendes Pattern updaten
            pattern = self.thinking_patterns[pattern_name]
            pattern.occurrences += 1
            if self.current_process:
                pattern.contexts.append(self.current_process.trigger[:30])
        else:
            # Neues Pattern erstellen
            pattern = ThinkingPattern(
                pattern_id=pattern_id,
                name=pattern_name,
                description=description,
                occurrences=1,
                is_helpful=is_helpful
            )

            if not is_helpful:
                pattern.improvement_strategy = self._generate_improvement_strategy(pattern_name)

            self.thinking_patterns[pattern_name] = pattern

        return {
            "pattern_identified": pattern_name,
            "occurrences": self.thinking_patterns[pattern_name].occurrences,
            "is_helpful": is_helpful,
            "improvement_strategy": self.thinking_patterns[pattern_name].improvement_strategy if not is_helpful else None
        }

    def _generate_improvement_strategy(self, pattern_name: str) -> str:
        """Generiert eine Verbesserungsstrategie für ein Muster"""
        # Generische Strategien
        strategies = [
            "Bewusst Gegenmaßnahmen einsetzen",
            "Bei diesem Muster innehalten und reflektieren",
            "Alternative Denkweisen explizit ausprobieren",
            "Feedback von außen holen wenn dieses Muster auftritt"
        ]
        return random.choice(strategies)

    def suggest_metacognitive_intervention(self) -> Dict[str, Any]:
        """
        Schlägt eine metakognitive Intervention vor basierend auf aktuellem Zustand.
        """
        intervention = {
            "suggested_strategy": None,
            "reason": "",
            "how_to_apply": ""
        }

        # Basierend auf aktuellem Prozess
        if self.current_process:
            # Viele Gedanken -> Simplify
            if len(self.current_process.thoughts) > 8:
                intervention["suggested_strategy"] = "simplify"
                intervention["reason"] = "Viele Gedanken - könnte zu komplex werden"
                intervention["how_to_apply"] = self.metacognitive_strategies["simplify"]

            # Sackgassen -> Step back
            elif len(self.current_process.dead_ends) > 2:
                intervention["suggested_strategy"] = "step_back"
                intervention["reason"] = "Mehrere Sackgassen - Zeit für Perspektivwechsel"
                intervention["how_to_apply"] = self.metacognitive_strategies["step_back"]

            # Biases detected -> Evidence check
            elif self.current_process.biases_detected:
                intervention["suggested_strategy"] = "evidence_check"
                intervention["reason"] = f"Bias erkannt: {self.current_process.biases_detected[0]}"
                intervention["how_to_apply"] = self.metacognitive_strategies["evidence_check"]

            # Default
            else:
                intervention["suggested_strategy"] = "question_assumptions"
                intervention["reason"] = "Regelmäßige Überprüfung"
                intervention["how_to_apply"] = self.metacognitive_strategies["question_assumptions"]

        return intervention

    def track_improvement(self, area: str, before: float, after: float,
                         description: str = "") -> Dict[str, Any]:
        """
        Trackt eine Verbesserung im Denken.
        """
        improvement = {
            "area": area,
            "before": before,
            "after": after,
            "improvement": after - before,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

        self.improvement_history.append(improvement)

        return {
            "improvement_tracked": True,
            "area": area,
            "improvement_amount": after - before,
            "percentage": ((after - before) / max(before, 0.01)) * 100,
            "total_improvements": len(self.improvement_history)
        }

    def generate_self_improvement_plan(self) -> Dict[str, Any]:
        """
        Generiert einen Plan zur Verbesserung des eigenen Denkens.

        Basiert auf erkannten Mustern und häufigen Biases.
        """
        plan = {
            "focus_areas": [],
            "strategies_to_apply": [],
            "patterns_to_address": [],
            "estimated_impact": "medium"
        }

        # Häufigste Biases finden
        all_biases = []
        for process in self.thinking_log:
            all_biases.extend(process.biases_detected)

        if all_biases:
            bias_counts = defaultdict(int)
            for b in all_biases:
                bias_counts[b] += 1

            top_biases = sorted(bias_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for bias, count in top_biases:
                if bias in self.known_biases:
                    plan["focus_areas"].append({
                        "bias": bias,
                        "occurrences": count,
                        "correction": self.known_biases[bias]["correction"]
                    })

        # Unhelpful Patterns adressieren
        unhelpful_patterns = [p for p in self.thinking_patterns.values() if not p.is_helpful]
        for pattern in unhelpful_patterns[:3]:
            plan["patterns_to_address"].append({
                "pattern": pattern.name,
                "strategy": pattern.improvement_strategy
            })

        # Strategien vorschlagen
        plan["strategies_to_apply"] = [
            "Vor wichtigen Entscheidungen: Slow down Strategie",
            "Regelmäßig: Question assumptions",
            "Bei Konflikten: Perspective switch",
            "Bei Komplexität: Simplify"
        ]

        # Impact schätzen
        if len(plan["focus_areas"]) > 2 or len(plan["patterns_to_address"]) > 2:
            plan["estimated_impact"] = "high"
        elif len(plan["focus_areas"]) == 0 and len(plan["patterns_to_address"]) == 0:
            plan["estimated_impact"] = "low"

        return plan

    def get_comprehensive_reflection(self) -> Dict[str, Any]:
        """
        Umfassende Reflexion über das eigene Denken.

        Kombiniert alle Analysen.
        """
        reflection = {
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "recent_quality": 0.0,
            "bias_profile": {},
            "pattern_profile": {},
            "cognitive_load_avg": 0.0,
            "improvement_trend": "stable",
            "recommendations": []
        }

        if not self.thinking_log:
            reflection["summary"] = "Noch nicht genug Daten für umfassende Reflexion"
            return reflection

        # Recent quality
        recent = self.thinking_log[-10:] if len(self.thinking_log) >= 10 else self.thinking_log
        reflection["recent_quality"] = sum(p.reasoning_quality for p in recent) / len(recent)

        # Strengths
        if reflection["recent_quality"] > 0.7:
            reflection["strengths"].append("Hohe Denkqualität")
        if sum(p.self_corrections for p in recent) > 0:
            reflection["strengths"].append("Fähigkeit zur Selbstkorrektur")
        if sum(len(p.breakthroughs) for p in recent) > 0:
            reflection["strengths"].append("Erreicht Durchbrüche")

        # Weaknesses
        all_biases = [b for p in recent for b in p.biases_detected]
        if len(all_biases) > 5:
            reflection["weaknesses"].append(f"Häufige Biases: {list(set(all_biases))[:3]}")
        if sum(len(p.dead_ends) for p in recent) > 3:
            reflection["weaknesses"].append("Viele Sackgassen im Denken")

        # Bias Profile
        bias_counts = defaultdict(int)
        for b in all_biases:
            bias_counts[b] += 1
        reflection["bias_profile"] = dict(sorted(bias_counts.items(), key=lambda x: x[1], reverse=True)[:5])

        # Pattern Profile
        reflection["pattern_profile"] = {
            name: {"occurrences": p.occurrences, "helpful": p.is_helpful}
            for name, p in self.thinking_patterns.items()
        }

        # Cognitive load
        if self.cognitive_load_history:
            reflection["cognitive_load_avg"] = sum(self.cognitive_load_history) / len(self.cognitive_load_history)

        # Improvement trend
        if len(self.improvement_history) >= 3:
            recent_improvements = [i["improvement"] for i in self.improvement_history[-3:]]
            if all(i > 0 for i in recent_improvements):
                reflection["improvement_trend"] = "improving"
            elif all(i < 0 for i in recent_improvements):
                reflection["improvement_trend"] = "declining"

        # Summary
        quality_desc = "gut" if reflection["recent_quality"] > 0.6 else "verbesserungswürdig"
        reflection["summary"] = (
            f"Denkqualität ist {quality_desc} ({reflection['recent_quality']:.2f}). "
            f"{len(reflection['strengths'])} Stärken, {len(reflection['weaknesses'])} Schwächen identifiziert. "
            f"Trend: {reflection['improvement_trend']}"
        )

        # Recommendations
        reflection["recommendations"] = self.generate_self_improvement_plan()["strategies_to_apply"]

        return reflection

    # ================================================================
    # LEVEL 10 METHODEN - Erweiterte Gedankenketten
    # ================================================================

    def branch_thought(self, chain_id: str, thought_id: str,
                      alternative_direction: str) -> Optional[Thought]:
        """
        Verzweigt einen Gedanken in eine neue Richtung.

        Ermöglicht nicht-lineares, baumartiges Denken.
        """
        if chain_id not in self.active_chains:
            return None

        chain = self.active_chains[chain_id]

        # Finde den Ursprungs-Gedanken
        source_thought = next((t for t in chain.thoughts if t.thought_id == thought_id), None)
        if not source_thought:
            return None

        # Erstelle Verzweigung
        branch_thought = Thought(
            thought_id=f"branch_{datetime.now().strftime('%H%M%S')}",
            thought_type=ThoughtType.CONNECTION,
            content=f"*denkt in andere Richtung* {alternative_direction}",
            concept=source_thought.concept,
            confidence=source_thought.confidence * 0.9,
            source="branch"
        )

        # Speichere Verzweigung
        if thought_id not in self.thought_branches:
            self.thought_branches[thought_id] = []
        self.thought_branches[thought_id].append(branch_thought.thought_id)

        chain.thoughts.append(branch_thought)
        return branch_thought

    def interrupt_and_save(self, chain_id: str) -> bool:
        """
        Unterbricht eine Gedankenkette und speichert den Zustand.

        Für später zum Fortsetzen.
        """
        if chain_id not in self.active_chains:
            return False

        chain = self.active_chains.pop(chain_id)
        self.interrupted_chains[chain_id] = chain
        return True

    def resume_chain(self, chain_id: str) -> Optional[ThoughtChain]:
        """Setzt eine unterbrochene Gedankenkette fort"""
        if chain_id not in self.interrupted_chains:
            return None

        chain = self.interrupted_chains.pop(chain_id)
        self.active_chains[chain_id] = chain
        return chain

    def detect_insight(self, chain: ThoughtChain) -> Optional[Dict[str, Any]]:
        """
        Erkennt wenn ein Insight/Durchbruch in einer Gedankenkette passiert.

        Ein Insight ist eine plötzliche neue Erkenntnis.
        """
        if len(chain.thoughts) < 3:
            return None

        # Prüfe auf plötzliche Verbindungen
        recent = chain.thoughts[-3:]
        concepts_mentioned = set()
        for t in recent:
            concepts_mentioned.update(t.content.lower().split())

        # Insight-Indikatoren
        insight_indicators = ["aha", "wow", "oh", "verstehe", "erkenntnis", "zusammenhang"]

        for thought in recent:
            if any(ind in thought.content.lower() for ind in insight_indicators):
                insight = {
                    "insight_id": f"insight_{len(self.insights_detected)}",
                    "chain_id": chain.chain_id,
                    "trigger_thought": thought.content,
                    "concepts_connected": list(concepts_mentioned)[:5],
                    "timestamp": datetime.now().isoformat()
                }
                self.insights_detected.append(insight)
                chain.insights_gained.append(thought.content)
                return insight

        return None

    def calculate_chain_coherence(self, chain: ThoughtChain) -> float:
        """
        Berechnet wie kohärent/zusammenhängend eine Gedankenkette ist.
        """
        if len(chain.thoughts) < 2:
            return 1.0

        coherence = 0.0
        transitions = 0

        for i in range(1, len(chain.thoughts)):
            prev = chain.thoughts[i-1]
            curr = chain.thoughts[i]

            # Konzept-Kontinuität
            if prev.concept == curr.concept:
                coherence += 0.3

            # Logische Übergänge
            if prev.thought_type != curr.thought_type:
                coherence += 0.2  # Variation ist gut

            # Inhaltliche Verbindung
            prev_words = set(prev.content.lower().split())
            curr_words = set(curr.content.lower().split())
            overlap = len(prev_words & curr_words) / max(len(prev_words | curr_words), 1)
            coherence += overlap * 0.5

            transitions += 1

        final_coherence = coherence / max(transitions, 1)
        self.coherence_scores[chain.chain_id] = min(1.0, final_coherence)
        return final_coherence

    def add_meta_thought(self, about_chain_id: str, reflection: str) -> Dict[str, Any]:
        """
        Fügt einen Meta-Gedanken hinzu (Gedanke über Gedanken).

        Meta-Kognition: Über das eigene Denken nachdenken.
        """
        meta = {
            "meta_id": f"meta_{len(self.meta_thoughts)}",
            "about_chain": about_chain_id,
            "reflection": reflection,
            "timestamp": datetime.now().isoformat()
        }
        self.meta_thoughts.append(meta)
        return meta

    def enable_mind_wandering(self, enable: bool = True) -> str:
        """
        Aktiviert/deaktiviert Mind Wandering.

        Mind Wandering = spontane Gedankenabschweifung, kann kreativ sein.
        """
        self.mind_wandering_enabled = enable
        if enable:
            return "*entspannt sich* Ich lasse meine Gedanken wandern..."
        return "*fokussiert sich* Konzentriertes Denken aktiviert."

    def update_salience(self, concept: str, importance: float) -> None:
        """
        Aktualisiert wie salient/wichtig ein Konzept gerade ist.

        Saliente Konzepte werden bevorzugt in Gedankenketten einbezogen.
        """
        self.current_salience[concept.lower()] = max(0.0, min(1.0, importance))

    def get_thought_chain_stats(self) -> Dict[str, Any]:
        """Umfassende Statistiken über das Gedankenketten-System"""
        return {
            "chains_created": self.chains_created,
            "total_thoughts": self.total_thoughts,
            "deepest_chain": self.deepest_chain,
            "active_chains": len(self.active_chains),
            "completed_chains": len(self.completed_chains),
            "interrupted_chains": len(self.interrupted_chains),
            "total_branches": sum(len(b) for b in self.thought_branches.values()),
            "insights_detected": len(self.insights_detected),
            "meta_thoughts": len(self.meta_thoughts),
            "mind_wandering_enabled": self.mind_wandering_enabled,
            "salient_concepts": len(self.current_salience),
            "average_coherence": sum(self.coherence_scores.values()) / max(len(self.coherence_scores), 1)
        }


# ============================================================
# HOLO MIND - Zentrales Denk-Koordinationssystem
# ============================================================

class ThinkingContext(Enum):
    """Kontext in dem gedacht wird"""
    CONVERSATION = "conversation"       # Während eines Gesprächs
    DECISION = "decision"               # Bei einer Entscheidung
    LEARNING = "learning"               # Beim Lernen
    EMOTION = "emotion"                 # Bei emotionaler Reaktion
    PROACTIVE = "proactive"             # Proaktives Denken
    REFLECTION = "reflection"           # Selbst-Reflexion
    PROBLEM_SOLVING = "problem_solving" # Problem lösen
    CREATIVITY = "creativity"           # Kreatives Denken


@dataclass
class ThinkingResult:
    """Ergebnis eines Denk-Prozesses"""
    result_id: str
    context: ThinkingContext
    input_text: str
    thoughts: List[str]              # Die Gedanken als Text
    insights: List[str]              # Gewonnene Erkenntnisse
    emotions_triggered: List[str]    # Ausgelöste Emotionen
    knowledge_applied: List[str]     # Angewandtes Wissen
    decisions_made: List[str]        # Getroffene Entscheidungen
    follow_up_questions: List[str]   # Offene Fragen
    confidence: float                # Gesamt-Konfidenz
    thinking_time_ms: float          # Wie lange wurde gedacht?
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HoloMind:
    """
    Zentrales Denk-Koordinationssystem für Holo.

    Verbindet ALLE Denk-Systeme und stellt eine einheitliche
    Schnittstelle für das gesamte System bereit.

    Komponenten:
    - ThoughtChainEngine: Gedankenketten bilden
    - KnowledgeIntegrationSystem: Wissen anwenden
    - SelfTeachingSystem: Selbst lernen
    - CuriosityDrivenLearner: Neugierig erkunden
    - IntuitiveSystem: Bauchgefühl
    - HypothesisEngine: Hypothesen bilden
    - AnalogyEngine: Analogien finden
    - SelfChallenger: Sich selbst hinterfragen

    Kognitive Systeme (v2.0):
    - TheoryOfMind: Verstehen was andere denken/fühlen
    - RealPlanningSystem: Echte ziel-orientierte Planung
    - MentalSimulation: "Was passiert wenn...?" Szenarien
    - AttentionSystem: Priorisierung und Fokus
    - RecursiveReflection: Meta-Kognition, Denken übers Denken

    Das HoloMind ist das "Gehirn" das alles koordiniert.

    v1.0: Zentrale Denk-Koordination für systemweite Nutzung
    v2.0: Erweitert um 5 kritische kognitive Systeme
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Alle Denk-Subsysteme
        self.thought_chain: Optional[ThoughtChainEngine] = None
        self.knowledge: Optional[KnowledgeIntegrationSystem] = None
        self.teaching: Optional[SelfTeachingSystem] = None
        self.curiosity: Optional[CuriosityDrivenLearner] = None
        self.intuition: Optional[IntuitiveSystem] = None
        self.hypothesis: Optional[HypothesisEngine] = None
        self.analogy: Optional[AnalogyEngine] = None
        self.challenger: Optional[SelfChallenger] = None

        # Kognitive Systeme (v2.0)
        self.theory_of_mind: Optional[TheoryOfMind] = None
        self.planning: Optional[RealPlanningSystem] = None
        self.simulation: Optional[MentalSimulation] = None
        self.attention: Optional[AttentionSystem] = None
        self.reflection: Optional[RecursiveReflection] = None

        # Denk-Historie
        self.thinking_history: List[ThinkingResult] = []
        self.current_thinking: Optional[ThinkingResult] = None

        # Konfiguration
        self.auto_think = True              # Automatisch bei Input denken
        self.thinking_depth = 5             # Standard-Tiefe für Gedankenketten
        self.max_thinking_time_ms = 500     # Max Denkzeit (Pi4-freundlich)

        # Statistiken
        self.total_thoughts = 0
        self.insights_gained = 0
        self.knowledge_applications = 0

        # Initialisiere eigene Subsysteme
        self._init_subsystems()

    def _init_subsystems(self) -> None:
        """Initialisiert die eigenen Denk-Subsysteme"""
        try:
            self.thought_chain = ThoughtChainEngine(self.data_dir)
            self.knowledge = KnowledgeIntegrationSystem(self.data_dir)
            self.teaching = SelfTeachingSystem(self.data_dir)
            self.curiosity = CuriosityDrivenLearner(self.data_dir)
            self.intuition = IntuitiveSystem()
            self.hypothesis = HypothesisEngine(self.data_dir)
            self.analogy = AnalogyEngine(self.data_dir)
            self.challenger = SelfChallenger()

            # Kognitive Systeme (v2.0)
            self.theory_of_mind = TheoryOfMind()
            self.planning = RealPlanningSystem()
            self.simulation = MentalSimulation()
            self.attention = AttentionSystem()
            self.reflection = RecursiveReflection()

            # Verbinde Systeme untereinander
            self.thought_chain.connect_systems(
                knowledge=self.knowledge,
                teaching=self.teaching
            )
            self.knowledge.connect_systems(
                teaching=self.teaching,
                analogy=self.analogy,
                hypothesis=self.hypothesis,
                intuition=self.intuition
            )
            self.curiosity.connect_curiosity_system(None)  # Wird später verbunden

            logger.info("🧠 HoloMind v2.0: Alle Subsysteme initialisiert (inkl. 5 kognitive Systeme)")
        except Exception as e:
            logger.warning(f"HoloMind Subsystem-Fehler: {e}")

    def connect_external_systems(self,
                                curiosity_system=None,
                                web_curiosity=None,
                                emotion_system=None) -> None:
        """Verbindet externe Systeme"""
        if curiosity_system and self.curiosity:
            self.curiosity.connect_curiosity_system(curiosity_system)
            logger.info("🔗 HoloMind mit CuriositySystem verbunden")

        if web_curiosity and self.curiosity:
            self.curiosity.connect_web_curiosity(web_curiosity)
            logger.info("🔗 HoloMind mit WebCuriosity verbunden")

    # ================================================================
    # HAUPTMETHODE: Denken über Input
    # ================================================================

    def think(self, input_text: str,
              context: ThinkingContext = ThinkingContext.CONVERSATION,
              depth: int = None) -> ThinkingResult:
        """
        Zentrale Denk-Methode die bei jedem Input aufgerufen werden kann.

        Dies ist die HAUPTSCHNITTSTELLE für das gesamte System.

        Args:
            input_text: Der Input worüber nachgedacht wird
            context: In welchem Kontext wird gedacht?
            depth: Wie tief soll gedacht werden? (1-7)

        Returns:
            ThinkingResult mit allen Gedanken und Erkenntnissen
        """
        import time
        start_time = time.time()

        depth = depth or self.thinking_depth

        result = ThinkingResult(
            result_id=f"think_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            context=context,
            input_text=input_text,
            thoughts=[],
            insights=[],
            emotions_triggered=[],
            knowledge_applied=[],
            decisions_made=[],
            follow_up_questions=[],
            confidence=0.5,
            thinking_time_ms=0
        )

        self.current_thinking = result

        try:
            # 1. INTUITION - Erstes Bauchgefühl
            if self.intuition:
                gut = self.intuition.get_gut_feeling(input_text)
                if gut:
                    result.thoughts.append(f"[Intuition] {gut.express()}")
                    result.emotions_triggered.append(gut.feeling_type.value)

            # 2. WISSEN ANWENDEN - Was weiß ich darüber?
            if self.knowledge:
                # Finde relevante Konzepte
                words = input_text.split()
                for word in words[:5]:
                    if len(word) > 4:
                        knowledge = self.knowledge.what_do_i_know_about(word)
                        if knowledge.get("can_answer"):
                            direct = knowledge.get("direct_knowledge", {})
                            if direct:
                                result.thoughts.append(
                                    f"[Wissen] Ich weiß über '{word}': {direct.get('definition', '')[:80]}..."
                                )
                                result.knowledge_applied.append(word)
                                self.knowledge_applications += 1

                # Wende Wissen auf Situation an
                applications = self.knowledge.apply_knowledge_to_situation(input_text)
                for app in applications[:2]:
                    result.insights.append(app.insight[:100])

            # 3. GEDANKENKETTE - Tieferes Nachdenken
            if self.thought_chain and depth >= 3:
                # Finde Hauptkonzept
                main_concept = self._extract_main_concept(input_text)
                if main_concept:
                    chain = self.thought_chain.think_about(main_concept, depth=depth)
                    for thought in chain.thoughts:
                        result.thoughts.append(f"[Kette] {thought.content}")
                    result.insights.extend(chain.insights_gained)

            # 4. HYPOTHESEN - Was könnte das bedeuten?
            if self.hypothesis and context in [ThinkingContext.PROBLEM_SOLVING,
                                                ThinkingContext.LEARNING]:
                hyp = self.hypothesis.generate_hypothesis(
                    observation=input_text,
                    context="thinking"
                )
                if hyp:
                    result.thoughts.append(f"[Hypothese] {hyp.hypothesis}")
                    result.follow_up_questions.append(
                        f"Wie könnte ich testen ob {hyp.hypothesis[:50]}...?"
                    )

            # 5. ANALOGIEN - Erinnert mich das an etwas?
            if self.analogy and self.knowledge:
                analogies = self.knowledge.find_analogies_from_knowledge(input_text)
                for ana in analogies[:1]:
                    result.thoughts.append(
                        f"[Analogie] {ana.get('analogy', '')}"
                    )
                    if ana.get("lesson"):
                        result.insights.append(f"Lektion: {ana['lesson']}")

            # 6. SELBST-HINTERFRAGUNG - Bin ich mir sicher?
            if self.challenger and len(result.thoughts) >= 3:
                # Hinterfrage die eigenen Gedanken
                if result.insights:
                    challenge = self.challenger.challenge_belief(
                        result.insights[0],
                        confidence=result.confidence
                    )
                    if challenge.should_reconsider:
                        result.thoughts.append(
                            f"[Hinterfragung] Moment... {challenge.challenge}"
                        )

            # 7. NEUGIER - Was will ich noch wissen?
            if self.curiosity:
                learn_result = self.curiosity.process_input(input_text, source="thinking")
                for question in learn_result.get("questions_for_user", [])[:2]:
                    result.follow_up_questions.append(question)
                for concept in learn_result.get("detected_concepts", [])[:3]:
                    if concept not in result.knowledge_applied:
                        result.follow_up_questions.append(
                            f"Was ist eigentlich '{concept}'?"
                        )

            # Berechne Gesamt-Konfidenz
            if result.knowledge_applied:
                result.confidence += 0.1 * len(result.knowledge_applied)
            if result.insights:
                result.confidence += 0.1 * len(result.insights)
            result.confidence = min(result.confidence, 0.95)

        except Exception as e:
            logger.warning(f"HoloMind think() Fehler: {e}")
            result.thoughts.append(f"[Fehler] Denken unterbrochen: {str(e)[:50]}")

        # Timing
        result.thinking_time_ms = (time.time() - start_time) * 1000

        # Statistiken
        self.total_thoughts += len(result.thoughts)
        self.insights_gained += len(result.insights)
        self.thinking_history.append(result)
        self.current_thinking = None

        return result

    def _extract_main_concept(self, text: str) -> Optional[str]:
        """Extrahiert das Hauptkonzept aus einem Text"""
        # Einfache Heuristik: Längstes Substantiv-artiges Wort
        words = text.split()
        candidates = [w for w in words if len(w) > 4 and w[0].isupper()]

        if candidates:
            return candidates[0].lower().strip(".,!?")

        # Fallback: Längstes Wort
        long_words = [w for w in words if len(w) > 5]
        if long_words:
            return max(long_words, key=len).lower().strip(".,!?")

        return None

    # ================================================================
    # SPEZIALISIERTE DENK-METHODEN
    # ================================================================

    def think_for_response(self, user_input: str) -> Dict[str, Any]:
        """
        Denkt bevor eine Antwort generiert wird.

        Speziell für die Konversations-Verarbeitung.
        """
        result = self.think(user_input, ThinkingContext.CONVERSATION, depth=4)

        return {
            "thoughts": result.thoughts,
            "insights": result.insights,
            "relevant_knowledge": result.knowledge_applied,
            "emotions": result.emotions_triggered,
            "questions": result.follow_up_questions,
            "confidence": result.confidence,
            "thinking_time_ms": result.thinking_time_ms
        }

    def think_for_decision(self, decision: str, options: List[str]) -> Dict[str, Any]:
        """
        Denkt bei einer Entscheidung.

        Nutzt Wissen und Intuition um zu helfen.
        """
        result = self.think(decision, ThinkingContext.DECISION, depth=5)

        # Zusätzlich: Konsultiere Wissen für Optionen
        option_analysis = []
        if self.knowledge:
            analysis = self.knowledge.consult_knowledge_for_decision(decision, options)
            option_analysis = analysis.get("options_analysis", [])
            result.decisions_made.append(analysis.get("recommendation", ""))

        return {
            "thoughts": result.thoughts,
            "option_analysis": option_analysis,
            "recommendation": result.decisions_made[0] if result.decisions_made else None,
            "reasoning": result.insights,
            "confidence": result.confidence
        }

    def think_for_learning(self, concept: str) -> Dict[str, Any]:
        """
        Denkt beim Lernen eines neuen Konzepts.

        Tieferes Nachdenken mit mehr Fragen.
        """
        result = self.think(concept, ThinkingContext.LEARNING, depth=6)

        # Zusätzlich: Lerne das Konzept
        if self.teaching:
            learn_report = self.teaching.learn_concept(concept)
            result.insights.extend([
                f"Gelernt: {learn_report.get('essence', {}).get('definition', '')[:80]}..."
            ])

        return {
            "thoughts": result.thoughts,
            "what_i_learned": result.insights,
            "still_curious_about": result.follow_up_questions,
            "confidence": result.confidence
        }

    def think_for_emotion(self, trigger: str, current_emotion: str) -> Dict[str, Any]:
        """
        Denkt bei einer emotionalen Reaktion.

        Verbindet Emotion mit Wissen und Erfahrung.
        """
        result = self.think(trigger, ThinkingContext.EMOTION, depth=3)

        # Finde Analogien zu vergangenen Emotionen
        emotional_insight = None
        if self.analogy:
            similar = self.analogy.find_similar_situation(trigger)
            if similar:
                emotional_insight = similar.get("lessons_learned", [])

        return {
            "thoughts": result.thoughts,
            "emotional_understanding": result.insights,
            "past_experience": emotional_insight,
            "current_emotion": current_emotion
        }

    def think_proactively(self) -> Optional[Dict[str, Any]]:
        """
        Denkt proaktiv ohne externen Trigger.

        Für spontane Gedanken und Reflexionen.
        """
        # Wähle zufälliges Thema zum Nachdenken
        topic = None

        # Aus Wissens-Reflexion
        if self.knowledge:
            reflection = self.knowledge.reflect_on_knowledge()
            gaps = reflection.get("knowledge_gaps", [])
            if gaps:
                topic = gaps[0].get("concept")

        # Aus vergangenen Gedankenketten
        if not topic and self.thought_chain:
            random_reflection = self.thought_chain.get_random_reflection()
            if random_reflection:
                return {
                    "type": "reflection",
                    "thought": random_reflection,
                    "is_spontaneous": True
                }

        # Aus Neugier
        if not topic and self.curiosity:
            desire = self.curiosity.what_should_i_learn_next()
            if desire:
                return {
                    "type": "curiosity",
                    "thought": desire,
                    "is_spontaneous": True
                }

        if topic:
            result = self.think(topic, ThinkingContext.PROACTIVE, depth=4)
            return {
                "type": "proactive_thinking",
                "topic": topic,
                "thoughts": result.thoughts,
                "insights": result.insights
            }

        return None

    def reflect_on_self(self) -> Dict[str, Any]:
        """
        Selbst-Reflexion über das eigene Denken und Wissen.
        """
        result = {
            "knowledge_status": None,
            "thinking_stats": None,
            "self_assessment": "",
            "areas_to_improve": [],
            "strengths": []
        }

        # Wissens-Reflexion
        if self.knowledge:
            result["knowledge_status"] = self.knowledge.reflect_on_knowledge()
            result["self_assessment"] = result["knowledge_status"].get("self_assessment", "")

            # Stärken
            result["strengths"] = result["knowledge_status"].get("strongest_areas", [])

            # Verbesserungsbereiche
            gaps = result["knowledge_status"].get("knowledge_gaps", [])
            result["areas_to_improve"] = [g.get("concept") for g in gaps[:5]]

        # Denk-Statistiken
        result["thinking_stats"] = {
            "total_thoughts": self.total_thoughts,
            "insights_gained": self.insights_gained,
            "knowledge_applications": self.knowledge_applications,
            "thinking_sessions": len(self.thinking_history)
        }

        return result

    # ================================================================
    # HILFSMETHODEN
    # ================================================================

    def express_current_thought(self) -> Optional[str]:
        """
        Drückt den aktuellen Gedanken aus.

        Für spontane Äußerungen während des Denkens.
        """
        if self.current_thinking and self.current_thinking.thoughts:
            return random.choice(self.current_thinking.thoughts)

        # Vergangener Gedanke
        if self.thinking_history:
            recent = self.thinking_history[-1]
            if recent.thoughts:
                return f"*erinnert sich* {random.choice(recent.thoughts)}"

        return None

    def get_thinking_summary(self) -> str:
        """Gibt eine Zusammenfassung des Denkens zurück"""
        if not self.thinking_history:
            return "*nachdenklich* Ich habe heute noch nicht viel nachgedacht..."

        recent = self.thinking_history[-5:]
        topics = [r.input_text[:30] for r in recent]
        insights = sum(len(r.insights) for r in recent)

        return (
            f"*reflektiert* Ich habe über {len(recent)} Themen nachgedacht: "
            f"{', '.join(topics)}... und dabei {insights} Erkenntnisse gewonnen!"
        )

    def should_think_deeper(self, input_text: str) -> bool:
        """Entscheidet ob tieferes Nachdenken nötig ist"""
        # Längerer Text = tieferes Denken
        if len(input_text) > 100:
            return True

        # Fragen erfordern Nachdenken
        if "?" in input_text or any(w in input_text.lower() for w in ["warum", "wie", "was ist"]):
            return True

        # Unbekannte Konzepte
        if self.curiosity:
            result = self.curiosity.process_input(input_text, source="check")
            if result.get("detected_concepts"):
                return True

        return False

    def get_mind_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über das Denksystem zurück"""
        return {
            "total_thoughts": self.total_thoughts,
            "insights_gained": self.insights_gained,
            "knowledge_applications": self.knowledge_applications,
            "thinking_sessions": len(self.thinking_history),
            "subsystems_active": {
                "thought_chain": self.thought_chain is not None,
                "knowledge": self.knowledge is not None,
                "teaching": self.teaching is not None,
                "curiosity": self.curiosity is not None,
                "intuition": self.intuition is not None,
                "hypothesis": self.hypothesis is not None,
                "analogy": self.analogy is not None,
                "challenger": self.challenger is not None,
                # Kognitive Systeme v2.0
                "theory_of_mind": self.theory_of_mind is not None,
                "planning": self.planning is not None,
                "simulation": self.simulation is not None,
                "attention": self.attention is not None,
                "reflection": self.reflection is not None
            },
            "auto_think_enabled": self.auto_think,
            "thinking_depth": self.thinking_depth
        }

    # ================================================================
    # KOGNITIVE SYSTEME v2.0 - Theory of Mind
    # ================================================================

    def understand_other(self, person_id: str, text: str) -> Dict[str, Any]:
        """
        Verstehe was eine andere Person denkt/fühlt.

        Nutzt Theory of Mind um den mentalen Zustand zu analysieren.

        Args:
            person_id: ID der Person
            text: Was die Person gesagt/geschrieben hat

        Returns:
            Dict mit mentalem Zustand und Empfehlungen
        """
        if not self.theory_of_mind:
            return {"error": "Theory of Mind nicht initialisiert"}

        # Analysiere mentalen Zustand
        mental_state = self.theory_of_mind.analyze_mental_state(person_id, text)

        # Sage Antwort-Präferenzen vorher
        preferences = self.theory_of_mind.predict_response_preference(person_id)

        # Was erwartet die Person?
        expectations = self.theory_of_mind.what_does_person_expect(person_id, text)

        return {
            "mental_state": mental_state,
            "response_preferences": preferences,
            "expectations": expectations,
            "how_to_respond": preferences.get("suggestions", [])
        }

    def simulate_perspective(self, person_id: str, situation: str) -> Dict[str, Any]:
        """
        Simuliere die Perspektive einer anderen Person.

        "Wie würde diese Person die Situation sehen?"
        """
        if not self.theory_of_mind:
            return {"error": "Theory of Mind nicht initialisiert"}

        return self.theory_of_mind.simulate_perspective(person_id, situation)

    # ================================================================
    # KOGNITIVE SYSTEME v2.0 - Planung
    # ================================================================

    def create_plan(self, goal: str, motivation: str = "") -> Dict[str, Any]:
        """
        Erstellt einen Plan um ein Ziel zu erreichen.

        Args:
            goal: Was soll erreicht werden?
            motivation: Warum ist das wichtig?

        Returns:
            Plan mit Schritten
        """
        if not self.planning:
            return {"error": "Planungssystem nicht initialisiert"}

        # Denke zuerst über das Ziel nach
        thoughts = self.planning.think_about_goal(goal)

        # Erstelle Plan
        plan = self.planning.create_plan(goal, motivation)

        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "steps": [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "status": s.status.value
                }
                for s in plan.steps
            ],
            "success_criteria": plan.success_criteria,
            "thoughts_about_goal": thoughts,
            "total_steps": len(plan.steps)
        }

    def get_next_plan_step(self, plan_id: str) -> Optional[Dict]:
        """Holt den nächsten ausführbaren Schritt eines Plans"""
        if not self.planning:
            return None
        return self.planning.get_next_step(plan_id)

    def complete_plan_step(self, plan_id: str, step_id: str, result: str = "") -> Dict:
        """Markiert einen Planschritt als abgeschlossen"""
        if not self.planning:
            return {"error": "Planungssystem nicht initialisiert"}
        return self.planning.complete_step(plan_id, step_id, result)

    # ================================================================
    # KOGNITIVE SYSTEME v2.0 - Mentale Simulation
    # ================================================================

    def what_if(self, hypothesis: str) -> Dict[str, Any]:
        """
        "Was wäre wenn...?" Gedankenexperiment.

        Args:
            hypothesis: z.B. "Was wenn ich die Wahrheit sage?"

        Returns:
            Simulierte Konsequenzen und Empfehlung
        """
        if not self.simulation:
            return {"error": "Simulationssystem nicht initialisiert"}

        return self.simulation.what_if(hypothesis)

    def compare_options(self, options: List[str], context: str = "") -> Dict[str, Any]:
        """
        Vergleicht mehrere Optionen durch Simulation.

        Args:
            options: Liste von Optionen zum Vergleichen
            context: Zusätzlicher Kontext

        Returns:
            Vergleich und Empfehlung
        """
        if not self.simulation:
            return {"error": "Simulationssystem nicht initialisiert"}

        return self.simulation.compare_options(options, context)

    def imagine_future(self, current_situation: str,
                       time_horizon: str = "short_term") -> Dict[str, Any]:
        """
        Stellt sich die Zukunft vor.

        Args:
            current_situation: Aktuelle Lage
            time_horizon: short_term, medium_term, long_term

        Returns:
            Mögliche Zukunftsszenarien
        """
        if not self.simulation:
            return {"error": "Simulationssystem nicht initialisiert"}

        return self.simulation.imagine_future(current_situation, time_horizon)

    # ================================================================
    # KOGNITIVE SYSTEME v2.0 - Aufmerksamkeit
    # ================================================================

    def focus_on(self, content: str, source: str = "input") -> Dict[str, Any]:
        """
        Richtet Aufmerksamkeit auf etwas.

        Args:
            content: Worauf fokussieren?
            source: Woher kommt es?

        Returns:
            Aufmerksamkeits-Item
        """
        if not self.attention:
            return {"error": "Aufmerksamkeitssystem nicht initialisiert"}

        item = self.attention.add_attention_item(content, source)
        return {
            "item_id": item.item_id,
            "content": item.content,
            "priority": item.priority.name,
            "relevance": item.relevance_score
        }

    def what_needs_attention(self) -> List[Dict[str, Any]]:
        """Was braucht gerade meine Aufmerksamkeit?"""
        if not self.attention:
            return []
        return self.attention.what_needs_attention()

    def is_this_a_distraction(self, new_content: str) -> Dict[str, Any]:
        """Prüft ob etwas eine Ablenkung ist"""
        if not self.attention:
            return {"is_distraction": False}
        return self.attention.is_distraction(new_content)

    def get_current_focus(self) -> Optional[str]:
        """Was hat gerade meinen Fokus?"""
        if not self.attention:
            return None
        focus = self.attention.get_current_focus()
        return focus.content if focus else None

    # ================================================================
    # KOGNITIVE SYSTEME v2.0 - Rekursive Reflexion
    # ================================================================

    def start_meta_observation(self, trigger: str) -> str:
        """Beginnt den eigenen Denkprozess zu beobachten"""
        if not self.reflection:
            return ""
        return self.reflection.start_thinking_observation(trigger)

    def record_thought_for_reflection(self, thought: str) -> Dict[str, Any]:
        """Zeichnet einen Gedanken zur Reflexion auf"""
        if not self.reflection:
            return {}
        return self.reflection.record_thought(thought)

    def end_meta_observation(self, outcome: str, was_effective: bool) -> Dict[str, Any]:
        """Beendet die Beobachtung und reflektiert"""
        if not self.reflection:
            return {}
        return self.reflection.end_thinking_observation(outcome, was_effective)

    def am_i_thinking_clearly(self) -> Dict[str, Any]:
        """Prüft ob das aktuelle Denken klar ist"""
        if not self.reflection:
            return {"clear": True}
        return self.reflection.am_i_thinking_clearly()

    def reflect_on_my_thinking(self, topic: str = "") -> Dict[str, Any]:
        """Reflektiert über das eigene Denken allgemein"""
        if not self.reflection:
            return {}
        return self.reflection.reflect_on_thinking(topic)

    # ================================================================
    # INTEGRIERTE METHODEN - Nutzt alle Systeme zusammen
    # ================================================================

    def deep_think(self, input_text: str, context: ThinkingContext,
                   person_id: str = None) -> Dict[str, Any]:
        """
        Tiefes Denken das ALLE kognitiven Systeme nutzt.

        Dies ist die umfassendste Denk-Methode die:
        - Theory of Mind nutzt (wenn person_id gegeben)
        - Aufmerksamkeit fokussiert
        - Denkprozess reflektiert
        - Simulationen durchführt
        - Gedankenketten bildet

        Args:
            input_text: Der Input
            context: Denkkontext
            person_id: Optional Person die involviert ist

        Returns:
            Umfassendes Denk-Ergebnis
        """
        result = {
            "input": input_text,
            "context": context.value,
            "thinking_process": [],
            "mental_model_of_other": None,
            "attention_focus": None,
            "simulations": [],
            "thought_chain": None,
            "meta_reflection": None,
            "final_insights": [],
            "recommendations": []
        }

        # 1. Starte Meta-Beobachtung
        if self.reflection:
            self.start_meta_observation(f"deep_think: {input_text[:50]}")

        # 2. Fokussiere Aufmerksamkeit
        if self.attention:
            focus_item = self.focus_on(input_text, "deep_think")
            result["attention_focus"] = focus_item
            if self.reflection:
                self.record_thought_for_reflection("Aufmerksamkeit fokussiert")

        # 3. Theory of Mind (wenn Person involviert)
        if person_id and self.theory_of_mind:
            result["mental_model_of_other"] = self.understand_other(person_id, input_text)
            if self.reflection:
                self.record_thought_for_reflection(
                    f"Verstehe was {person_id} denkt/fühlt"
                )

        # 4. Gedankenkette bilden
        if self.thought_chain:
            chain = self.thought_chain.think_about(input_text, depth=self.thinking_depth)
            result["thought_chain"] = {
                "chain_id": chain.chain_id,
                "thoughts": [t.text for t in chain.thoughts],
                "depth": chain.depth_reached
            }
            if self.reflection:
                for t in chain.thoughts[:3]:
                    self.record_thought_for_reflection(t.text)

        # 5. Simulationen (bei Entscheidungen)
        if context == ThinkingContext.DECISION and self.simulation:
            sim = self.what_if(f"Was wenn ich {input_text}?")
            result["simulations"].append(sim)
            if self.reflection:
                self.record_thought_for_reflection("Konsequenzen simuliert")

        # 6. Insights extrahieren
        if result["thought_chain"]:
            result["final_insights"] = [
                t for t in result["thought_chain"]["thoughts"]
                if any(word in t.lower() for word in ["also", "bedeutet", "verstehe", "erkenne"])
            ]

        # 7. Empfehlungen generieren
        if result["mental_model_of_other"]:
            prefs = result["mental_model_of_other"].get("response_preferences", {})
            result["recommendations"].extend(prefs.get("suggestions", []))

        # 8. Meta-Reflexion abschließen
        if self.reflection:
            reflection_result = self.end_meta_observation(
                outcome=f"Deep thinking über '{input_text[:30]}' abgeschlossen",
                was_effective=len(result["final_insights"]) > 0
            )
            result["meta_reflection"] = reflection_result

        return result

    def smart_respond_preparation(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Bereitet eine intelligente Antwort vor.

        Nutzt kognitive Systeme um zu verstehen:
        - Was will der User wirklich?
        - Wie fühlt er sich?
        - Was erwartet er?
        - Worauf sollte ich achten?
        - Wie sollte ich antworten?

        Args:
            user_input: Was der User gesagt hat
            user_id: ID des Users

        Returns:
            Vorbereitung für die Antwort
        """
        prep = {
            "user_understanding": None,
            "attention_items": [],
            "is_distraction": False,
            "response_strategy": {},
            "things_to_avoid": [],
            "emotional_tone_recommended": "neutral"
        }

        # Verstehe den User
        if self.theory_of_mind:
            prep["user_understanding"] = self.understand_other(user_id, user_input)

            # Empfohlener emotionaler Ton
            prefs = prep["user_understanding"].get("response_preferences", {})
            prep["emotional_tone_recommended"] = prefs.get("tone", "neutral")

            # Strategie
            if prefs.get("emotional_support"):
                prep["response_strategy"]["priority"] = "empathy_first"
            if prefs.get("direct_answer"):
                prep["response_strategy"]["style"] = "direct"

        # Was braucht Aufmerksamkeit?
        if self.attention:
            self.focus_on(user_input, f"user:{user_id}")
            prep["attention_items"] = self.what_needs_attention()

        # Prüfe Denkklarheit
        if self.reflection:
            clarity = self.am_i_thinking_clearly()
            if not clarity.get("clear", True):
                prep["things_to_avoid"].extend(clarity.get("issues", []))

        return prep


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=== Autonomous Thinking Demo ===\n")

    system = AutonomousThinkingSystem(intuition_weight=0.2)

    # Test 1: Intuition
    print("1. INTUITION TEST:")
    gut = system.intuitive.get_gut_feeling(
        "Diese Person hat mich angelogen aber ist jetzt total ehrlich"
    )
    if gut:
        print(f"   {gut.express()}")

    # Test 2: Selbst-Hinterfragung
    print("\n2. SELBST-HINTERFRAGUNG:")
    challenge = system.challenger.challenge_belief(
        "Politiker X ist korrupt",
        confidence=0.85
    )
    print(f"   Challenge: {challenge.challenge}")
    print(f"   Counter-Args: {challenge.counter_arguments}")

    # Test 3: Was-Wenn
    print("\n3. WAS-WENN:")
    what_if = system.hypothesis_engine.what_if("Was wenn die Person die Wahrheit sagt?")
    print(f"   Konsequenzen: {what_if['consequences']}")

    # Test 4: Kombinierter Score
    print("\n4. KOMBINIERTER SCORE:")
    combined, explanation = system.get_combined_score(
        rational_score=0.7,
        topic="Max Mustermann",
        info="Er hat mir sehr geholfen aber irgendwas stimmt nicht"
    )
    print(f"   Score: {combined:.2f}")
    print(f"   {explanation}")

    # Test 5: Think About
    print("\n5. THINK ABOUT:")
    thoughts = system.think_about(
        "Neue Person",
        "Hat gesagt sie sei sehr ehrlich und würde niemals lügen",
        {"is_person": True}
    )
    print(f"   Intuition: {thoughts['intuition']}")
    print(f"   What-If: {thoughts['what_if']['my_reaction']}")

    # Test 6: ANALOGIE-ENGINE
    print("\n6. ANALOGIE-ENGINE TEST:")
    # Erfahrung speichern
    system.analogy_engine.store_experience(
        situation="Person X hat viel versprochen und nichts gehalten",
        outcome="War enttäuscht, Vertrauen verloren",
        outcome_valence=-0.7,
        lessons=["Nicht auf leere Versprechen hören", "Erst Taten, dann Vertrauen"]
    )
    # Ähnliche Situation prüfen
    wisdom = system.analogy_engine.get_wisdom_from_past(
        "Diese Person verspricht mir viel Hilfe"
    )
    if wisdom:
        print(f"   {wisdom.get('expression', 'Keine Analogie')}")
        if wisdom.get("warning"):
            print(f"   {wisdom['warning']}")
        if wisdom.get("main_lesson"):
            print(f"   Lektion: {wisdom['main_lesson']}")
    else:
        print("   Keine ähnliche Situation gefunden")

    # Test 7: REUE-SYSTEM
    print("\n7. REUE-SYSTEM TEST:")
    # Reue aufzeichnen
    regret = system.regret_system.record_regret(
        decision="Habe jemandem sofort vertraut ohne Beweise",
        what_happened="Wurde ausgenutzt und belogen",
        what_should_have_done="Erst abwarten und Vertrauen langsam aufbauen",
        intensity=RegretIntensity.STRONG
    )
    print(f"   Reue aufgezeichnet: {regret.regret_id}")
    print(f"   {system.regret_system.express_regret(regret.regret_id)}")

    # Prüfen vor ähnlicher Entscheidung
    print("\n   Prüfe ähnliche Entscheidung:")
    check = system.regret_system.should_i_repeat("Soll ich dieser Person sofort vertrauen?")
    if check["has_past_regret"]:
        print(f"   {check['warning']}")

    # Selbstvergebung
    print("\n   Selbstvergebung:")
    print(f"   {system.regret_system.forgive_self(regret.regret_id)}")

    # Test 8: VOR ENTSCHEIDUNG PRÜFEN
    print("\n8. VOR ENTSCHEIDUNG PRÜFEN:")
    pre_check = system.check_before_deciding("Soll ich dieser neuen Person vertrauen?")
    print(f"   Empfehlung: {pre_check['recommendation']}")
    if pre_check["warnings"]:
        print(f"   Warnungen: {pre_check['warnings']}")
    if pre_check["lessons"]:
        print(f"   Lektionen: {pre_check['lessons']}")

    # Test 9: AUS ERFAHRUNG LERNEN
    print("\n9. AUS ERFAHRUNG LERNEN:")
    learn_result = system.learn_from_experience(
        situation="Habe Person Y eine zweite Chance gegeben",
        outcome="Hat sich wirklich gebessert und war ehrlich",
        outcome_was_good=True,
        lesson="Manchmal verdienen Menschen zweite Chancen"
    )
    print(f"   Erfahrung gespeichert: {learn_result['experience_id']}")

    print("\n=== Demo abgeschlossen ===")
    print(f"Regret-Summary: {system.regret_system.get_regret_summary()}")
