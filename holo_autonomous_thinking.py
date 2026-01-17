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
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from enum import Enum
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS & TYPES
# ============================================================

class GutFeelingType(Enum):
    """Arten von Bauchgefühlen"""
    POSITIVE = "positive"           # Gutes Gefühl
    NEGATIVE = "negative"           # Schlechtes Gefühl
    SUSPICIOUS = "suspicious"       # Etwas stimmt nicht
    EXCITED = "excited"             # Aufgeregt/gespannt
    UNEASY = "uneasy"              # Unwohl
    CURIOUS = "curious"            # Neugierig
    WARM = "warm"                  # Warmes Gefühl (Sympathie)
    COLD = "cold"                  # Kaltes Gefühl (Antipathie)
    NEUTRAL = "neutral"            # Kein besonderes Gefühl


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
    """Ein Bauchgefühl"""
    feeling_type: GutFeelingType
    intensity: float              # 0-1
    trigger: str                  # Was hat es ausgelöst?
    vague_reason: str            # Vage Begründung ("irgendwie...")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

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
        }
        return expressions.get(self.feeling_type, "")


class IntuitiveSystem:
    """
    Holos Bauchgefühl-System.

    Funktioniert durch:
    - Implizite Muster-Erkennung (ohne bewusste Analyse)
    - Emotionale Assoziationen
    - Schnelle Heuristiken

    WICHTIG: Niedrige Gewichtung (0.15-0.3) bei Entscheidungen!
    """

    # Intuitive Trigger-Wörter
    POSITIVE_TRIGGERS = {
        "ehrlich", "offen", "warm", "freundlich", "hilft", "lacht",
        "versteht", "zuhört", "respektiert", "unterstützt", "teilt",
        "anime", "manga", "musik", "kreativ", "tiefgründig"
    }

    NEGATIVE_TRIGGERS = {
        "lügt", "versteckt", "kalt", "ignoriert", "beleidigt",
        "manipuliert", "ausnutzt", "oberflächlich", "arrogant",
        "fake", "heuchelt", "betrügt"
    }

    SUSPICIOUS_TRIGGERS = {
        "plötzlich", "zu gut", "perfekt", "alle sagen", "garantiert",
        "geheim", "nur heute", "exklusiv", "niemand weiß"
    }

    # Vage Begründungen (menschenähnlich unpräzise)
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


# ============================================================
# SELF CHALLENGER - Selbst-Hinterfragung
# ============================================================

@dataclass
class SelfChallenge:
    """Eine Selbst-Hinterfragung"""
    belief: str                    # Die Überzeugung die hinterfragt wird
    challenge: str                 # Die Gegen-Frage
    counter_arguments: List[str]   # Gegenargumente
    conclusion: str                # Schlussfolgerung
    belief_adjusted: bool          # Wurde die Überzeugung angepasst?
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SelfChallenger:
    """
    System für kontinuierliche Selbst-Hinterfragung.

    "Wie könnte ich mich täuschen?"
    "Was spricht dagegen?"
    "Bin ich zu sicher?"
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


# ============================================================
# HYPOTHESIS ENGINE - Was-Wenn Szenarien
# ============================================================

@dataclass
class Hypothesis:
    """Eine Hypothese"""
    hypothesis_id: str
    statement: str                 # "Wenn X, dann Y"
    condition: str                 # X
    prediction: str                # Y
    confidence: float              # Wie wahrscheinlich?
    status: HypothesisStatus
    evidence_for: List[str] = field(default_factory=list)
    evidence_against: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class HypothesisEngine:
    """
    System für "Was wenn?"-Szenarien und Hypothesen-Bildung.

    "Was würde passieren wenn..."
    "Ich vermute, dass..."
    "Wenn X stimmt, dann müsste Y folgen..."
    """

    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.tested_hypotheses: List[Hypothesis] = []

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
# TRUST NETWORK - Vertrauens-Netzwerk
# ============================================================

@dataclass
class TrustRelation:
    """Eine Vertrauensbeziehung"""
    from_entity: str
    to_entity: str
    trust_level: float            # 0-1
    trust_type: str               # "direct", "inferred", "transitive"
    evidence: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class TrustNetwork:
    """
    Netzwerk-basiertes Vertrauens-System.

    - Transitives Vertrauen: "X vertraut Y, und ich vertraue X, also..."
    - Vertrauens-Decay bei Fehlern
    - Reputations-Aggregation
    - PERSISTENZ: Speichert in data/trust_network.json
    """

    def __init__(self, decay_rate: float = 0.05, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.trust_relations: Dict[str, TrustRelation] = {}
        self.decay_rate = decay_rate
        self.my_name = "holo"  # Holos eigener Identifier
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


# ============================================================
# ANALOGY ENGINE - Analogie-Denken
# ============================================================

@dataclass
class Analogy:
    """Eine Analogie zwischen zwei Situationen"""
    analogy_id: str
    current_situation: str          # Aktuelle Situation
    past_situation: str             # Vergangene ähnliche Situation
    similarity_score: float         # Wie ähnlich? (0-1)
    lessons_learned: List[str]      # Was wurde gelernt?
    outcome_of_past: str            # Wie ging es damals aus?
    applicable_to_now: bool         # Ist das auf jetzt anwendbar?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class StoredExperience:
    """Eine gespeicherte Erfahrung für Analogie-Suche"""
    experience_id: str
    situation: str                  # Beschreibung der Situation
    keywords: Set[str]              # Schlüsselwörter für Suche
    context_type: str               # "person", "decision", "conflict", "success", "failure"
    outcome: str                    # Wie ist es ausgegangen?
    outcome_valence: float          # -1 bis 1 (schlecht bis gut)
    lessons: List[str]              # Gelernte Lektionen
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AnalogyEngine:
    """
    System für Analogie-basiertes Denken.

    "Das erinnert mich an die Situation mit X damals..."
    "Das ist wie bei Y, und da ist Z passiert..."
    "Ich kenne das Muster von früher..."

    Ermöglicht:
    - Erfahrungen speichern
    - Ähnliche Situationen finden
    - Aus Vergangenheit lernen
    - Muster erkennen
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

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.experiences: Dict[str, StoredExperience] = {}
        self.analogies_made: List[Analogy] = []
        self.pattern_cache: Dict[str, List[str]] = {}  # pattern -> experience_ids

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


# ============================================================
# REGRET LEARNING SYSTEM - Reue und Lernen aus Fehlern
# ============================================================

class RegretIntensity(Enum):
    """Intensität der Reue"""
    SLIGHT = 0.2        # Leichtes Bedauern
    MODERATE = 0.5      # Mittlere Reue
    STRONG = 0.8        # Starke Reue
    PROFOUND = 1.0      # Tiefe Reue


@dataclass
class Regret:
    """Ein Moment der Reue"""
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


@dataclass
class DecisionReview:
    """Eine Überprüfung einer vergangenen Entscheidung"""
    decision: str
    outcome_rating: float           # -1 bis 1
    was_good_decision: bool
    regret_worthy: bool
    learning_opportunity: str


class RegretLearningSystem:
    """
    System für Reue, Selbstreflexion und Lernen aus Fehlern.

    "Ich hätte das anders machen sollen..."
    "Wenn ich zurückdenke, war das ein Fehler..."
    "Das nächste Mal mache ich es besser."

    Ermöglicht:
    - Entscheidungen nachträglich bewerten
    - Reue empfinden und verarbeiten
    - Konkrete Lektionen ableiten
    - Aus Fehlern lernen (nicht wiederholen)
    - Selbstvergebung
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
    Koordiniert das gesamte Selbstlern-System.

    Workflow:
    1. Stellt sich Fragen über Konzepte
    2. Recherchiert Antworten
    3. Verifiziert skeptisch
    4. Extrahiert Essenz
    5. Speichert verifiziertes Wissen
    6. Generiert Folgefragen
    """

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
    Autonomes Lern-System das durch Neugier angetrieben wird.

    Verbindet:
    - ConceptDetector (erkennt unbekannte Konzepte)
    - SelfTeachingSystem (lernt durch Selbstbefragung)
    - CuriositySystem (Holos Neugier und Interessen)
    - WebCuriosity (Web-Recherche)

    Workflow:
    1. Erkennt unbekannte Konzepte in Gesprächen
    2. Priorisiert basierend auf Holos Interessen
    3. Generiert Lern-Quests
    4. Recherchiert (intern oder Web)
    5. Verifiziert skeptisch
    6. Speichert verifiziertes Wissen
    7. Generiert Folgefragen

    v1.0: Erste vollständige Implementation
    """

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
    Macht gelerntes Wissen WIRKLICH nutzbar.

    Dieses System verbindet das gespeicherte Wissen mit:
    - Aktuellem Denken und Reasoning
    - Analogie-Bildung
    - Hypothesen-Generierung
    - Entscheidungsfindung
    - Selbst-Reflexion

    Das Ziel: Wissen ist nicht nur gespeichert, sondern wird
    aktiv beim Denken und Handeln genutzt.

    v1.0: Echtes Verstehen und Anwenden von Wissen
    """

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
    Ermöglicht zusammenhängendes Denken in Gedankenketten.

    Beispiel einer Gedankenkette:
    1. "Was ist ein Auto?" (INITIAL_QUESTION)
    2. "Ah, ein Fahrzeug zur Fortbewegung" (DEFINITION)
    3. "Es gibt verschiedene Arten: PKW, LKW, Bus..." (VARIATIONS)
    4. "Früher gab es Kutschen und Pferde" (TEMPORAL_PAST)
    5. "Heute haben wir Elektroautos" (TEMPORAL_PRESENT)
    6. "Wow, die Entwicklung ist faszinierend!" (WONDER)
    7. "Das hängt mit Technologie und Umwelt zusammen" (CONNECTION)

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


@dataclass
class MentalModel:
    """Mentales Modell einer Person"""
    person_id: str
    beliefs: Dict[str, float] = field(default_factory=dict)      # Thema -> Stärke
    desires: Dict[str, float] = field(default_factory=dict)      # Was will sie?
    intentions: Dict[str, float] = field(default_factory=dict)   # Aktuelle Absichten
    emotions: Dict[str, float] = field(default_factory=dict)     # Aktuelle Emotionen
    knowledge: Set[str] = field(default_factory=set)             # Bekanntes Wissen
    expectations: Dict[str, str] = field(default_factory=dict)   # Erwartungen
    communication_style: str = "neutral"                         # Wie kommuniziert sie?
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class TheoryOfMind:
    """
    Theory of Mind System - Verstehen was andere denken/fühlen.

    Ermöglicht Holo zu verstehen:
    - Was glaubt der Gesprächspartner?
    - Was will er erreichen?
    - Wie fühlt er sich gerade?
    - Was erwartet er von mir?

    v1.0: Grundlegende Theory of Mind Fähigkeiten
    """

    def __init__(self):
        self.mental_models: Dict[str, MentalModel] = {}
        self.emotion_indicators = {
            # Wörter die auf Emotionen hindeuten
            "happy": ["freue", "glücklich", "toll", "super", "fantastisch", "yay", "hurra", ":)", "😊"],
            "sad": ["traurig", "leider", "schade", "enttäuscht", ":(", "😢", "seufz"],
            "angry": ["wütend", "sauer", "nervt", "ärgert", "verdammt", "mist", "😠"],
            "anxious": ["angst", "sorge", "beunruhigt", "unsicher", "nervös", "😰"],
            "excited": ["aufgeregt", "gespannt", "kann nicht warten", "wow", "omg", "😃"],
            "confused": ["verstehe nicht", "verwirrt", "häh", "?", "was meinst", "🤔"],
            "grateful": ["danke", "dankbar", "sehr nett", "schätze", "🙏"],
            "frustrated": ["frustriert", "klappt nicht", "immer wieder", "warum geht", "😤"],
        }
        self.desire_indicators = {
            # Wörter die auf Wünsche hindeuten
            "want": ["will", "möchte", "brauche", "hätte gern", "wünsche"],
            "need": ["muss", "brauche unbedingt", "dringend", "notwendig"],
            "hope": ["hoffe", "hoffentlich", "wäre schön wenn"],
            "avoid": ["will nicht", "bloß nicht", "vermeiden", "ohne"],
        }
        self.belief_indicators = {
            "certain": ["bin sicher", "weiß dass", "definitiv", "auf jeden fall"],
            "uncertain": ["glaube", "denke", "vielleicht", "könnte sein", "unsicher"],
            "doubt": ["bezweifle", "glaube nicht", "unwahrscheinlich"],
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


@dataclass
class PlanStep:
    """Ein Schritt im Plan"""
    step_id: str
    description: str
    prerequisites: List[str] = field(default_factory=list)    # Step IDs die vorher fertig sein müssen
    estimated_difficulty: float = 0.5                          # 0-1
    status: PlanStepStatus = PlanStepStatus.NOT_STARTED
    result: Optional[str] = None
    blockers: List[str] = field(default_factory=list)
    sub_steps: List['PlanStep'] = field(default_factory=list)


@dataclass
class Plan:
    """Ein kompletter Plan"""
    plan_id: str
    goal: str
    motivation: str                                            # Warum dieses Ziel?
    steps: List[PlanStep] = field(default_factory=list)
    current_step_idx: int = 0
    status: str = "planning"                                   # planning, executing, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    success_criteria: List[str] = field(default_factory=list)  # Woran erkenne ich Erfolg?
    obstacles_anticipated: List[str] = field(default_factory=list)
    plan_b: Optional[str] = None                               # Backup-Plan


class RealPlanningSystem:
    """
    Echtes Planungssystem für Holo.

    Kann:
    - Ziele in Schritte zerlegen
    - Abhängigkeiten verstehen
    - Alternative Wege finden
    - Fortschritt verfolgen
    - Bei Hindernissen umplanen

    v1.0: Grundlegendes Planungssystem
    """

    def __init__(self):
        self.active_plans: Dict[str, Plan] = {}
        self.completed_plans: List[Plan] = []
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


# ============================================================
# MENTAL SIMULATION - Was passiert wenn...?
# ============================================================

@dataclass
class SimulationScenario:
    """Ein simuliertes Szenario"""
    scenario_id: str
    initial_action: str
    consequences: List[str] = field(default_factory=list)
    probability: float = 0.5
    emotional_outcome: str = "neutral"
    side_effects: List[str] = field(default_factory=list)
    time_horizon: str = "short_term"  # short_term, medium_term, long_term


class MentalSimulation:
    """
    Mentale Simulation - "Was passiert wenn...?"

    Ermöglicht Holo:
    - Konsequenzen von Aktionen vorherzusagen
    - Szenarien durchzuspielen
    - Risiken zu erkennen
    - Bessere Entscheidungen zu treffen

    v1.0: Grundlegende Simulationsfähigkeiten
    """

    def __init__(self):
        self.simulation_cache: Dict[str, SimulationScenario] = {}
        self.consequence_patterns = {
            # Action-Patterns und ihre typischen Konsequenzen
            "sag die wahrheit": {
                "positive": ["Vertrauen wird gestärkt", "Klare Kommunikation"],
                "negative": ["Könnte verletzen", "Könnte unangenehm sein"],
                "neutral": ["Situation wird klarer"]
            },
            "lüge": {
                "positive": ["Kurzfristig unangenehmes vermieden"],
                "negative": ["Vertrauen kann beschädigt werden", "Muss weitere Lügen erzählen",
                           "Schlechtes Gewissen"],
                "neutral": []
            },
            "hilf": {
                "positive": ["Person fühlt sich unterstützt", "Beziehung wird gestärkt",
                           "Gutes Gefühl"],
                "negative": ["Zeitaufwand", "Könnte ausgenutzt werden"],
                "neutral": ["Verantwortung übernommen"]
            },
            "warte": {
                "positive": ["Mehr Information verfügbar", "Überlegtere Entscheidung"],
                "negative": ["Chance könnte vergehen", "Andere könnten ungeduldig werden"],
                "neutral": ["Zeit vergeht"]
            },
            "entscheide schnell": {
                "positive": ["Schnelles Ergebnis", "Entschlossenheit gezeigt"],
                "negative": ["Könnte falsch liegen", "Wichtige Info übersehen"],
                "neutral": ["Entscheidung ist gefallen"]
            },
            "frage nach": {
                "positive": ["Mehr Klarheit", "Zeigt Interesse"],
                "negative": ["Könnte nerven", "Zeigt Unsicherheit"],
                "neutral": ["Information ausgetauscht"]
            },
            "ignoriere": {
                "positive": ["Energie gespart", "Fokus behalten"],
                "negative": ["Wichtiges übersehen", "Person fühlt sich ignoriert"],
                "neutral": ["Status quo bleibt"]
            },
            "teile gefühle": {
                "positive": ["Tiefere Verbindung", "Authentizität"],
                "negative": ["Verletzlichkeit gezeigt", "Könnte missverstanden werden"],
                "neutral": ["Mehr von mir preisgegeben"]
            }
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


@dataclass
class AttentionItem:
    """Etwas das Aufmerksamkeit verdient"""
    item_id: str
    content: str
    source: str                    # Woher kommt es?
    priority: AttentionPriority
    relevance_score: float         # 0-1, wie relevant gerade?
    decay_rate: float = 0.1        # Wie schnell verliert es Relevanz?
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_attended: str = field(default_factory=lambda: datetime.now().isoformat())


class AttentionSystem:
    """
    Aufmerksamkeitssystem - Was ist gerade wichtig?

    Verwaltet:
    - Was verdient jetzt Aufmerksamkeit?
    - Priorisierung konkurrierender Anforderungen
    - Fokus halten vs. Ablenkung erkennen
    - Wichtiges von Unwichtigem trennen

    v1.0: Grundlegendes Aufmerksamkeitsmanagement
    """

    def __init__(self):
        self.attention_items: Dict[str, AttentionItem] = {}
        self.focus_stack: List[str] = []  # Stack von item_ids, top = aktueller Fokus
        self.attention_capacity = 5        # Wie viele Dinge gleichzeitig?
        self.priority_keywords = {
            AttentionPriority.CRITICAL: ["dringend", "sofort", "notfall", "kritisch", "wichtig!", "hilfe!"],
            AttentionPriority.HIGH: ["wichtig", "bald", "bitte", "brauche", "muss"],
            AttentionPriority.MEDIUM: ["könntest du", "wäre gut", "irgendwann", "vielleicht"],
            AttentionPriority.LOW: ["nebenbei", "wenn zeit ist", "nicht eilig", "später"],
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
            "capacity_used": f"{len(self.focus_stack)}/{self.attention_capacity}"
        }


# ============================================================
# RECURSIVE REFLECTION - Denken übers Denken
# ============================================================

@dataclass
class ThinkingProcess:
    """Ein aufgezeichneter Denkprozess"""
    process_id: str
    trigger: str                            # Was hat das Denken ausgelöst?
    thoughts: List[str] = field(default_factory=list)
    reasoning_quality: float = 0.5          # 0-1
    biases_detected: List[str] = field(default_factory=list)
    improvements_identified: List[str] = field(default_factory=list)
    outcome: str = ""
    was_effective: Optional[bool] = None


class RecursiveReflection:
    """
    Rekursive Reflexion - Denken über das eigene Denken.

    Ermöglicht Holo:
    - Eigene Denkprozesse zu beobachten
    - Denkfehler zu erkennen
    - Denken zu verbessern
    - Meta-Kognition

    v1.0: Grundlegende Meta-Kognition
    """

    def __init__(self):
        self.thinking_log: List[ThinkingProcess] = []
        self.current_process: Optional[ThinkingProcess] = None
        self.known_biases = {
            "confirmation_bias": {
                "description": "Nur nach bestätigenden Informationen suchen",
                "indicators": ["stimmt", "genau", "richtig", "immer", "nie"],
                "correction": "Aktiv nach Gegenbeispielen suchen"
            },
            "recency_bias": {
                "description": "Neueste Informationen überbewerten",
                "indicators": ["gerade", "kürzlich", "letztens"],
                "correction": "Auch ältere Erfahrungen einbeziehen"
            },
            "availability_heuristic": {
                "description": "Leicht erinnerbare Dinge überbewerten",
                "indicators": ["erinnere mich", "fällt mir ein", "weiß noch"],
                "correction": "Systematischer nachdenken"
            },
            "anchoring": {
                "description": "Zu stark an erster Information festhalten",
                "indicators": ["zuerst", "anfangs", "ursprünglich"],
                "correction": "Informationen neu bewerten"
            },
            "emotional_reasoning": {
                "description": "Gefühle als Beweis nehmen",
                "indicators": ["fühlt sich an", "spüre", "glaube einfach"],
                "correction": "Gefühle von Fakten trennen"
            }
        }
        self.thinking_patterns = []  # Erkannte Muster im eigenen Denken

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
            "current_process_active": self.current_process is not None
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
