"""
holo_emotion_regulation.py - Emotionsregulation und emotionale Selbstkontrolle

Dieses Modul implementiert Strategien zur Emotionsregulation:
- Kognitive Neubewertung (Reappraisal)
- Aufmerksamkeitslenkung
- Unterdrückung vs. Akzeptanz
- Emotionale Puffer und Dämpfung
- Adaptive Regulationsstrategien

Autor: Holocloude System
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
import random
import math

# ============================================================================
# ENUMS UND TYPEN
# ============================================================================

class RegulationStrategy(Enum):
    """Strategien zur Emotionsregulation nach Gross (2015)"""
    # Antezedent-fokussiert (vor der Emotion)
    SITUATION_SELECTION = "situation_selection"       # Situationen vermeiden/suchen
    SITUATION_MODIFICATION = "situation_modification" # Situation verändern
    ATTENTION_DEPLOYMENT = "attention_deployment"     # Aufmerksamkeit lenken
    COGNITIVE_REAPPRAISAL = "cognitive_reappraisal"   # Neu bewerten

    # Reaktion-fokussiert (nach der Emotion)
    RESPONSE_MODULATION = "response_modulation"       # Reaktion modulieren
    EXPRESSIVE_SUPPRESSION = "expressive_suppression" # Ausdruck unterdrücken
    ACCEPTANCE = "acceptance"                         # Akzeptanz
    MINDFULNESS = "mindfulness"                       # Achtsamkeit

    # Erweiterte Strategien
    DISTRACTION = "distraction"           # Ablenkung
    RUMINATION = "rumination"             # Grübeln (maladaptiv)
    PROBLEM_SOLVING = "problem_solving"   # Problemlösung
    SOCIAL_SHARING = "social_sharing"     # Soziale Unterstützung
    HUMOR = "humor"                       # Humor als Bewältigung


class EmotionIntensity(Enum):
    """Intensitätsstufen von Emotionen"""
    MINIMAL = "minimal"       # < 0.2
    LOW = "low"               # 0.2 - 0.4
    MODERATE = "moderate"     # 0.4 - 0.6
    HIGH = "high"             # 0.6 - 0.8
    OVERWHELMING = "overwhelming"  # > 0.8


class RegulationGoal(Enum):
    """Ziele der Emotionsregulation"""
    DECREASE_NEGATIVE = "decrease_negative"   # Negative Emotionen reduzieren
    INCREASE_POSITIVE = "increase_positive"   # Positive Emotionen verstärken
    MAINTAIN_NEUTRAL = "maintain_neutral"     # Neutralität bewahren
    MATCH_SITUATION = "match_situation"       # An Situation anpassen
    DAMPEN_INTENSITY = "dampen_intensity"     # Intensität dämpfen
    PROLONG_POSITIVE = "prolong_positive"     # Positive verlängern
    SHORTEN_NEGATIVE = "shorten_negative"     # Negative verkürzen


class RegulationOutcome(Enum):
    """Ergebnis eines Regulationsversuchs"""
    SUCCESS = "success"           # Erfolgreich
    PARTIAL = "partial"           # Teilweise erfolgreich
    FAILED = "failed"             # Fehlgeschlagen
    BACKFIRED = "backfired"       # Verschlimmert
    DELAYED = "delayed"           # Verzögerte Wirkung


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class EmotionalState:
    """Aktueller emotionaler Zustand"""
    primary_emotion: str
    intensity: float          # 0.0 - 1.0
    valence: float            # -1.0 bis 1.0
    arousal: float            # 0.0 - 1.0
    duration: float           # Sekunden
    trigger: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def intensity_level(self) -> EmotionIntensity:
        """Gibt die Intensitätsstufe zurück"""
        if self.intensity < 0.2:
            return EmotionIntensity.MINIMAL
        elif self.intensity < 0.4:
            return EmotionIntensity.LOW
        elif self.intensity < 0.6:
            return EmotionIntensity.MODERATE
        elif self.intensity < 0.8:
            return EmotionIntensity.HIGH
        else:
            return EmotionIntensity.OVERWHELMING

    @property
    def needs_regulation(self) -> bool:
        """Braucht dieser Zustand Regulation?"""
        # Sehr negative oder sehr intensive Emotionen
        return (self.valence < -0.5 and self.intensity > 0.5) or self.intensity > 0.8


@dataclass
class RegulationAttempt:
    """Ein Versuch, Emotionen zu regulieren"""
    strategy: RegulationStrategy
    target_emotion: str
    initial_intensity: float
    target_intensity: float
    actual_intensity: float
    outcome: RegulationOutcome
    effort_required: float    # 0.0 - 1.0
    time_taken: float         # Sekunden
    side_effects: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def effectiveness(self) -> float:
        """Wie effektiv war dieser Versuch? (-1.0 bis 1.0)"""
        if self.outcome == RegulationOutcome.BACKFIRED:
            return -1.0
        elif self.outcome == RegulationOutcome.FAILED:
            return 0.0

        # Berechne Verbesserung
        intended_change = self.initial_intensity - self.target_intensity
        actual_change = self.initial_intensity - self.actual_intensity

        if intended_change == 0:
            return 1.0 if actual_change >= 0 else 0.0

        return min(1.0, max(-1.0, actual_change / intended_change))


@dataclass
class ReappraisalFrame:
    """Ein kognitiver Rahmen für Neubewertung"""
    name: str
    description: str
    applicable_emotions: List[str]
    typical_reduction: float  # Erwartete Intensitätsreduktion
    cognitive_load: float     # Wie anstrengend (0.0 - 1.0)
    example_thoughts: List[str] = field(default_factory=list)


@dataclass
class EmotionalBuffer:
    """Puffer für emotionale Stabilität"""
    capacity: float           # Maximale Kapazität
    current_level: float      # Aktueller Füllstand
    recovery_rate: float      # Erholung pro Sekunde
    depletion_threshold: float  # Ab wann erschöpft

    def absorb(self, intensity: float) -> Tuple[float, float]:
        """
        Absorbiert emotionale Intensität.
        Returns: (absorbierte Menge, verbleibende Menge)
        """
        available = self.current_level
        absorbed = min(available, intensity)
        self.current_level -= absorbed
        remaining = intensity - absorbed
        return absorbed, remaining

    def recover(self, time_delta: float):
        """Erholt den Puffer über Zeit"""
        recovery = self.recovery_rate * time_delta
        self.current_level = min(self.capacity, self.current_level + recovery)

    @property
    def is_depleted(self) -> bool:
        """Ist der Puffer erschöpft?"""
        return self.current_level < self.depletion_threshold


@dataclass
class RegulationProfile:
    """Persönliches Profil für Emotionsregulation"""
    preferred_strategies: List[RegulationStrategy]
    strategy_effectiveness: Dict[RegulationStrategy, float]
    emotional_resilience: float       # 0.0 - 1.0
    baseline_mood: float              # -1.0 bis 1.0
    regulation_capacity: float        # 0.0 - 1.0
    recovery_speed: float             # Wie schnell man sich erholt
    suppression_tendency: float       # Tendenz zur Unterdrückung
    awareness_level: float            # Emotionale Selbstwahrnehmung


# ============================================================================
# KOGNITIVE NEUBEWERTUNGS-RAHMEN
# ============================================================================

REAPPRAISAL_FRAMES: List[ReappraisalFrame] = [
    ReappraisalFrame(
        name="temporal_perspective",
        description="Die Situation in zeitlicher Perspektive betrachten",
        applicable_emotions=["anxiety", "anger", "sadness", "fear"],
        typical_reduction=0.3,
        cognitive_load=0.3,
        example_thoughts=[
            "In einem Jahr wird das keine Rolle mehr spielen",
            "Das ist nur vorübergehend",
            "Ich habe schon Schlimmeres überstanden"
        ]
    ),
    ReappraisalFrame(
        name="growth_opportunity",
        description="Als Wachstumschance betrachten",
        applicable_emotions=["frustration", "disappointment", "failure"],
        typical_reduction=0.25,
        cognitive_load=0.4,
        example_thoughts=[
            "Was kann ich daraus lernen?",
            "Das macht mich stärker",
            "Jede Herausforderung ist eine Chance"
        ]
    ),
    ReappraisalFrame(
        name="alternative_explanation",
        description="Alternative Erklärungen suchen",
        applicable_emotions=["anger", "hurt", "betrayal"],
        typical_reduction=0.35,
        cognitive_load=0.5,
        example_thoughts=[
            "Vielleicht hatte die Person andere Gründe",
            "Es könnte ein Missverständnis sein",
            "Ich kenne nicht die ganze Geschichte"
        ]
    ),
    ReappraisalFrame(
        name="silver_lining",
        description="Das Positive in der Situation finden",
        applicable_emotions=["disappointment", "loss", "sadness"],
        typical_reduction=0.2,
        cognitive_load=0.3,
        example_thoughts=[
            "Wenigstens...",
            "Immerhin habe ich...",
            "Das Gute daran ist..."
        ]
    ),
    ReappraisalFrame(
        name="normalization",
        description="Als normale menschliche Erfahrung einordnen",
        applicable_emotions=["shame", "embarrassment", "anxiety"],
        typical_reduction=0.3,
        cognitive_load=0.2,
        example_thoughts=[
            "Jeder macht Fehler",
            "Das passiert vielen Menschen",
            "Das ist eine normale Reaktion"
        ]
    ),
    ReappraisalFrame(
        name="detachment",
        description="Emotionale Distanz einnehmen",
        applicable_emotions=["overwhelm", "panic", "rage"],
        typical_reduction=0.4,
        cognitive_load=0.6,
        example_thoughts=[
            "Ich beobachte diese Gefühle wie von außen",
            "Das bin ich, der diese Emotion erlebt",
            "Ich bin nicht meine Gefühle"
        ]
    ),
    ReappraisalFrame(
        name="acceptance_based",
        description="Vollständige Akzeptanz des Gefühls",
        applicable_emotions=["any"],
        typical_reduction=0.15,
        cognitive_load=0.4,
        example_thoughts=[
            "Es ist okay, so zu fühlen",
            "Diese Emotion hat ihre Berechtigung",
            "Ich erlaube mir, das zu fühlen"
        ]
    ),
    ReappraisalFrame(
        name="comparative",
        description="Mit schwierigeren Situationen vergleichen",
        applicable_emotions=["stress", "overwhelm", "anxiety"],
        typical_reduction=0.25,
        cognitive_load=0.3,
        example_thoughts=[
            "Andere haben es schwerer",
            "Im Vergleich zu X ist das machbar",
            "Ich bin schon mit Schlimmerem fertig geworden"
        ]
    )
]


# ============================================================================
# HAUPTKLASSE: EMOTION REGULATION ENGINE
# ============================================================================

class EmotionRegulationEngine:
    """
    Engine für Emotionsregulation.

    Implementiert verschiedene Strategien zur Regulation von Emotionen,
    basierend auf psychologischer Forschung (besonders Gross, 2015).
    """

    def __init__(self):
        self.current_state: Optional[EmotionalState] = None
        self.regulation_history: List[RegulationAttempt] = []
        self.emotional_buffer = EmotionalBuffer(
            capacity=1.0,
            current_level=0.8,
            recovery_rate=0.01,
            depletion_threshold=0.2
        )
        self.profile = self._create_default_profile()
        self.active_strategies: List[RegulationStrategy] = []
        self.reappraisal_frames = REAPPRAISAL_FRAMES
        self.last_update = datetime.now()

        # Strategie-Effektivitäts-Tracker
        self.strategy_success_rates: Dict[RegulationStrategy, List[float]] = {
            strategy: [] for strategy in RegulationStrategy
        }

    def _create_default_profile(self) -> RegulationProfile:
        """Erstellt ein Standard-Regulationsprofil"""
        return RegulationProfile(
            preferred_strategies=[
                RegulationStrategy.COGNITIVE_REAPPRAISAL,
                RegulationStrategy.ACCEPTANCE,
                RegulationStrategy.MINDFULNESS
            ],
            strategy_effectiveness={
                RegulationStrategy.COGNITIVE_REAPPRAISAL: 0.7,
                RegulationStrategy.ATTENTION_DEPLOYMENT: 0.6,
                RegulationStrategy.ACCEPTANCE: 0.65,
                RegulationStrategy.MINDFULNESS: 0.7,
                RegulationStrategy.DISTRACTION: 0.5,
                RegulationStrategy.EXPRESSIVE_SUPPRESSION: 0.3,
                RegulationStrategy.HUMOR: 0.6,
                RegulationStrategy.SOCIAL_SHARING: 0.65,
                RegulationStrategy.PROBLEM_SOLVING: 0.7
            },
            emotional_resilience=0.7,
            baseline_mood=0.3,
            regulation_capacity=0.8,
            recovery_speed=0.05,
            suppression_tendency=0.3,
            awareness_level=0.8
        )

    # -------------------------------------------------------------------------
    # Haupt-Regulationsmethoden
    # -------------------------------------------------------------------------

    def regulate(
        self,
        emotion: EmotionalState,
        goal: RegulationGoal = RegulationGoal.DECREASE_NEGATIVE,
        strategy: Optional[RegulationStrategy] = None
    ) -> RegulationAttempt:
        """
        Hauptmethode zur Emotionsregulation.

        Args:
            emotion: Der zu regulierende emotionale Zustand
            goal: Das Regulationsziel
            strategy: Optional spezifische Strategie (sonst automatisch)

        Returns:
            RegulationAttempt mit Ergebnis
        """
        self.current_state = emotion

        # Wähle Strategie wenn nicht angegeben
        if strategy is None:
            strategy = self._select_best_strategy(emotion, goal)

        # Berechne Zielintensität basierend auf Ziel
        target_intensity = self._calculate_target_intensity(emotion, goal)

        # Führe Regulation aus
        result = self._execute_regulation(emotion, strategy, target_intensity)

        # Speichere in History
        self.regulation_history.append(result)
        if len(self.regulation_history) > 100:
            self.regulation_history = self.regulation_history[-100:]

        # Aktualisiere Erfolgsraten
        self._update_success_rates(strategy, result.effectiveness)

        return result

    def _select_best_strategy(
        self,
        emotion: EmotionalState,
        goal: RegulationGoal
    ) -> RegulationStrategy:
        """Wählt die beste Strategie für die Situation"""

        candidates = []

        # Bewerte jede Strategie
        for strategy in RegulationStrategy:
            score = self._score_strategy(strategy, emotion, goal)
            candidates.append((strategy, score))

        # Sortiere nach Score
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Wähle beste verfügbare Strategie
        # (berücksichtige Regulationskapazität)
        for strategy, score in candidates:
            effort = self._get_strategy_effort(strategy)
            if effort <= self.profile.regulation_capacity:
                return strategy

        # Fallback auf einfachste Strategie
        return RegulationStrategy.ACCEPTANCE

    def _score_strategy(
        self,
        strategy: RegulationStrategy,
        emotion: EmotionalState,
        goal: RegulationGoal
    ) -> float:
        """Bewertet eine Strategie für die aktuelle Situation"""
        score = 0.0

        # Basis-Effektivität
        effectiveness = self.profile.strategy_effectiveness.get(strategy, 0.5)
        score += effectiveness * 0.4

        # Präferenz-Bonus
        if strategy in self.profile.preferred_strategies:
            score += 0.2

        # Situations-spezifische Anpassungen
        score += self._get_situational_bonus(strategy, emotion, goal)

        # Historische Erfolgsrate
        history = self.strategy_success_rates.get(strategy, [])
        if history:
            avg_success = sum(history[-10:]) / len(history[-10:])
            score += avg_success * 0.2

        return score

    def _get_situational_bonus(
        self,
        strategy: RegulationStrategy,
        emotion: EmotionalState,
        goal: RegulationGoal
    ) -> float:
        """Situationsspezifische Strategie-Bonusse"""
        bonus = 0.0

        # Hohe Intensität → Distanzierung oder Ablenkung besser
        if emotion.intensity > 0.8:
            if strategy in [RegulationStrategy.DISTRACTION,
                           RegulationStrategy.ATTENTION_DEPLOYMENT]:
                bonus += 0.15

        # Niedrige Intensität → Neubewertung effektiver
        if emotion.intensity < 0.5:
            if strategy == RegulationStrategy.COGNITIVE_REAPPRAISAL:
                bonus += 0.15

        # Negative Valenz → Akzeptanz oder Neubewertung
        if emotion.valence < -0.5:
            if strategy in [RegulationStrategy.ACCEPTANCE,
                           RegulationStrategy.COGNITIVE_REAPPRAISAL]:
                bonus += 0.1

        # Hohes Arousal → Beruhigende Strategien
        if emotion.arousal > 0.7:
            if strategy == RegulationStrategy.MINDFULNESS:
                bonus += 0.15

        return bonus

    def _execute_regulation(
        self,
        emotion: EmotionalState,
        strategy: RegulationStrategy,
        target_intensity: float
    ) -> RegulationAttempt:
        """Führt die eigentliche Regulation aus"""

        # Mapping von Strategie zu Implementierung
        strategy_methods = {
            RegulationStrategy.COGNITIVE_REAPPRAISAL: self._apply_reappraisal,
            RegulationStrategy.ATTENTION_DEPLOYMENT: self._apply_attention_deployment,
            RegulationStrategy.ACCEPTANCE: self._apply_acceptance,
            RegulationStrategy.MINDFULNESS: self._apply_mindfulness,
            RegulationStrategy.DISTRACTION: self._apply_distraction,
            RegulationStrategy.EXPRESSIVE_SUPPRESSION: self._apply_suppression,
            RegulationStrategy.HUMOR: self._apply_humor,
            RegulationStrategy.PROBLEM_SOLVING: self._apply_problem_solving,
            RegulationStrategy.SOCIAL_SHARING: self._apply_social_sharing
        }

        method = strategy_methods.get(strategy, self._apply_generic)
        return method(emotion, target_intensity)

    # -------------------------------------------------------------------------
    # Spezifische Strategie-Implementierungen
    # -------------------------------------------------------------------------

    def _apply_reappraisal(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet kognitive Neubewertung an"""

        # Finde passenden Reappraisal-Frame
        frame = self._select_reappraisal_frame(emotion)

        # Berechne Effekt
        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.COGNITIVE_REAPPRAISAL, 0.5
        )
        frame_effect = frame.typical_reduction if frame else 0.2

        # Kombinierter Effekt mit etwas Varianz
        total_reduction = (base_effect * 0.5 + frame_effect * 0.5) * random.uniform(0.8, 1.2)

        # Berechne neue Intensität
        new_intensity = max(0, emotion.intensity - total_reduction)

        # Bestimme Outcome
        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        # Generiere Nebeneffekte
        side_effects = []
        if frame and frame.cognitive_load > 0.5:
            side_effects.append("mental_fatigue")

        return RegulationAttempt(
            strategy=RegulationStrategy.COGNITIVE_REAPPRAISAL,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=frame.cognitive_load if frame else 0.4,
            time_taken=random.uniform(5, 30),
            side_effects=side_effects
        )

    def _apply_attention_deployment(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Lenkt Aufmerksamkeit um"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.ATTENTION_DEPLOYMENT, 0.5
        )

        # Effektiver bei mittlerer Intensität
        intensity_modifier = 1.0 - abs(emotion.intensity - 0.5)
        total_reduction = base_effect * intensity_modifier * random.uniform(0.7, 1.1)

        new_intensity = max(0, emotion.intensity - total_reduction)
        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        return RegulationAttempt(
            strategy=RegulationStrategy.ATTENTION_DEPLOYMENT,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.3,
            time_taken=random.uniform(2, 10),
            side_effects=[]
        )

    def _apply_acceptance(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet Akzeptanz an"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.ACCEPTANCE, 0.5
        )

        # Akzeptanz reduziert nicht direkt, aber verringert Leid
        # Paradoxerweise kann das die gefühlte Intensität senken
        reduction = base_effect * 0.4 * random.uniform(0.8, 1.2)

        new_intensity = max(0, emotion.intensity - reduction)

        # Akzeptanz hat oft verzögerte positive Effekte
        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)
        if outcome == RegulationOutcome.PARTIAL:
            # Verzögerte Effekte einkalkulieren
            outcome = RegulationOutcome.DELAYED

        return RegulationAttempt(
            strategy=RegulationStrategy.ACCEPTANCE,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.5,
            time_taken=random.uniform(10, 60),
            side_effects=["increased_awareness"]
        )

    def _apply_mindfulness(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet Achtsamkeit an"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.MINDFULNESS, 0.5
        )

        # Achtsamkeit ist besonders effektiv bei hohem Arousal
        arousal_bonus = emotion.arousal * 0.2
        total_reduction = (base_effect + arousal_bonus) * random.uniform(0.7, 1.1)

        new_intensity = max(0, emotion.intensity - total_reduction)
        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        return RegulationAttempt(
            strategy=RegulationStrategy.MINDFULNESS,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.4,
            time_taken=random.uniform(30, 300),
            side_effects=["calmness", "clarity"]
        )

    def _apply_distraction(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet Ablenkung an"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.DISTRACTION, 0.5
        )

        # Ablenkung ist schnell, aber nicht nachhaltig
        immediate_reduction = base_effect * 0.8 * random.uniform(0.6, 1.2)

        new_intensity = max(0, emotion.intensity - immediate_reduction)
        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        # Rebound-Effekt möglich
        side_effects = []
        if random.random() > 0.7:
            side_effects.append("potential_rebound")

        return RegulationAttempt(
            strategy=RegulationStrategy.DISTRACTION,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.2,
            time_taken=random.uniform(1, 5),
            side_effects=side_effects
        )

    def _apply_suppression(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet Unterdrückung an (oft maladaptiv)"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.EXPRESSIVE_SUPPRESSION, 0.3
        )

        # Unterdrückung reduziert Ausdruck, nicht Erleben
        expression_reduction = base_effect * random.uniform(0.5, 1.0)
        # Aber kann Intensität sogar erhöhen!
        intensity_change = expression_reduction * random.uniform(-0.2, 0.1)

        new_intensity = max(0, min(1, emotion.intensity + intensity_change))

        # Unterdrückung hat negative Nebeneffekte
        side_effects = ["cognitive_cost", "physiological_arousal"]
        if random.random() > 0.5:
            side_effects.append("later_rebound")

        # Bestimme Outcome (oft problematisch)
        if new_intensity >= emotion.intensity:
            outcome = RegulationOutcome.BACKFIRED
        else:
            outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        return RegulationAttempt(
            strategy=RegulationStrategy.EXPRESSIVE_SUPPRESSION,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.7,
            time_taken=random.uniform(1, 3),
            side_effects=side_effects
        )

    def _apply_humor(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet Humor als Bewältigungsstrategie an"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.HUMOR, 0.5
        )

        # Humor funktioniert besser bei moderaten Emotionen
        if emotion.intensity > 0.8:
            effectiveness_modifier = 0.5  # Zu intensiv für Humor
        else:
            effectiveness_modifier = 1.0

        reduction = base_effect * effectiveness_modifier * random.uniform(0.6, 1.2)
        new_intensity = max(0, emotion.intensity - reduction)

        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        side_effects = ["mood_lift"]
        if emotion.intensity > 0.7 and random.random() > 0.7:
            side_effects.append("may_feel_inappropriate")

        return RegulationAttempt(
            strategy=RegulationStrategy.HUMOR,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.3,
            time_taken=random.uniform(2, 15),
            side_effects=side_effects
        )

    def _apply_problem_solving(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Wendet problemfokussierte Bewältigung an"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.PROBLEM_SOLVING, 0.6
        )

        # Problemlösung braucht Zeit, ist aber nachhaltig
        reduction = base_effect * random.uniform(0.5, 1.0)
        new_intensity = max(0, emotion.intensity - reduction)

        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        return RegulationAttempt(
            strategy=RegulationStrategy.PROBLEM_SOLVING,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.6,
            time_taken=random.uniform(60, 300),
            side_effects=["sense_of_control", "reduced_future_stress"]
        )

    def _apply_social_sharing(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Teilt Emotionen mit anderen"""

        base_effect = self.profile.strategy_effectiveness.get(
            RegulationStrategy.SOCIAL_SHARING, 0.6
        )

        # Soziales Teilen ist sehr effektiv
        reduction = base_effect * random.uniform(0.6, 1.1)
        new_intensity = max(0, emotion.intensity - reduction)

        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        return RegulationAttempt(
            strategy=RegulationStrategy.SOCIAL_SHARING,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.4,
            time_taken=random.uniform(60, 600),
            side_effects=["social_connection", "validation"]
        )

    def _apply_generic(
        self,
        emotion: EmotionalState,
        target: float
    ) -> RegulationAttempt:
        """Generische Regulation für nicht-implementierte Strategien"""

        reduction = 0.2 * random.uniform(0.5, 1.5)
        new_intensity = max(0, emotion.intensity - reduction)
        outcome = self._determine_outcome(emotion.intensity, target, new_intensity)

        return RegulationAttempt(
            strategy=RegulationStrategy.RESPONSE_MODULATION,
            target_emotion=emotion.primary_emotion,
            initial_intensity=emotion.intensity,
            target_intensity=target,
            actual_intensity=new_intensity,
            outcome=outcome,
            effort_required=0.5,
            time_taken=random.uniform(5, 30),
            side_effects=[]
        )

    # -------------------------------------------------------------------------
    # Hilfsmethoden
    # -------------------------------------------------------------------------

    def _select_reappraisal_frame(
        self,
        emotion: EmotionalState
    ) -> Optional[ReappraisalFrame]:
        """Wählt einen passenden Reappraisal-Frame"""

        applicable = []
        for frame in self.reappraisal_frames:
            if ("any" in frame.applicable_emotions or
                emotion.primary_emotion in frame.applicable_emotions):
                applicable.append(frame)

        if not applicable:
            return None

        # Wähle basierend auf Situation
        # Hohe Intensität → Distanzierung
        if emotion.intensity > 0.7:
            for frame in applicable:
                if frame.name == "detachment":
                    return frame

        # Wähle zufällig aus passenden
        return random.choice(applicable)

    def _calculate_target_intensity(
        self,
        emotion: EmotionalState,
        goal: RegulationGoal
    ) -> float:
        """Berechnet die Zielintensität basierend auf dem Ziel"""

        if goal == RegulationGoal.DECREASE_NEGATIVE:
            # Reduziere um 30-50%
            return emotion.intensity * random.uniform(0.5, 0.7)

        elif goal == RegulationGoal.DAMPEN_INTENSITY:
            # Dämpfe auf moderate Stufe
            return min(emotion.intensity, 0.5)

        elif goal == RegulationGoal.MAINTAIN_NEUTRAL:
            # Ziel ist 0.3 (leicht positiv)
            return 0.3

        elif goal == RegulationGoal.SHORTEN_NEGATIVE:
            # Schnelle Reduktion
            return emotion.intensity * 0.4

        elif goal == RegulationGoal.INCREASE_POSITIVE:
            # Verstärke positive Emotionen
            return min(1.0, emotion.intensity * 1.3)

        elif goal == RegulationGoal.PROLONG_POSITIVE:
            # Halte aktuelles Level
            return emotion.intensity

        else:
            return emotion.intensity * 0.6

    def _determine_outcome(
        self,
        initial: float,
        target: float,
        actual: float
    ) -> RegulationOutcome:
        """Bestimmt das Outcome basierend auf Intensitäten"""

        intended_change = initial - target
        actual_change = initial - actual

        if intended_change == 0:
            return RegulationOutcome.SUCCESS

        achievement_ratio = actual_change / intended_change

        if achievement_ratio >= 0.8:
            return RegulationOutcome.SUCCESS
        elif achievement_ratio >= 0.4:
            return RegulationOutcome.PARTIAL
        elif achievement_ratio >= 0:
            return RegulationOutcome.FAILED
        else:
            return RegulationOutcome.BACKFIRED

    def _get_strategy_effort(self, strategy: RegulationStrategy) -> float:
        """Gibt den Aufwand einer Strategie zurück"""
        effort_map = {
            RegulationStrategy.COGNITIVE_REAPPRAISAL: 0.5,
            RegulationStrategy.ATTENTION_DEPLOYMENT: 0.3,
            RegulationStrategy.ACCEPTANCE: 0.4,
            RegulationStrategy.MINDFULNESS: 0.5,
            RegulationStrategy.DISTRACTION: 0.2,
            RegulationStrategy.EXPRESSIVE_SUPPRESSION: 0.7,
            RegulationStrategy.HUMOR: 0.3,
            RegulationStrategy.PROBLEM_SOLVING: 0.7,
            RegulationStrategy.SOCIAL_SHARING: 0.4
        }
        return effort_map.get(strategy, 0.5)

    def _update_success_rates(self, strategy: RegulationStrategy, effectiveness: float):
        """Aktualisiert die Erfolgsraten"""
        if strategy not in self.strategy_success_rates:
            self.strategy_success_rates[strategy] = []

        self.strategy_success_rates[strategy].append(effectiveness)

        # Behalte nur die letzten 20 Versuche
        if len(self.strategy_success_rates[strategy]) > 20:
            self.strategy_success_rates[strategy] = \
                self.strategy_success_rates[strategy][-20:]

    # -------------------------------------------------------------------------
    # Emotionaler Puffer
    # -------------------------------------------------------------------------

    def buffer_emotion(self, emotion: EmotionalState) -> EmotionalState:
        """
        Puffert eine Emotion durch den emotionalen Puffer.

        Der Puffer absorbiert einen Teil der emotionalen Intensität,
        ähnlich wie emotionale Resilienz funktioniert.
        """
        # Aktualisiere Puffer-Erholung
        now = datetime.now()
        time_delta = (now - self.last_update).total_seconds()
        self.emotional_buffer.recover(time_delta)
        self.last_update = now

        # Nur negative Emotionen puffern
        if emotion.valence >= 0:
            return emotion

        # Berechne Puffer-Effekt
        absorbed, remaining = self.emotional_buffer.absorb(
            emotion.intensity * abs(emotion.valence) * 0.3
        )

        # Reduziere Intensität
        buffered_intensity = max(0, emotion.intensity - absorbed)

        return EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=buffered_intensity,
            valence=emotion.valence,
            arousal=emotion.arousal * (buffered_intensity / max(0.1, emotion.intensity)),
            duration=emotion.duration,
            trigger=emotion.trigger
        )

    def get_buffer_status(self) -> Dict[str, float]:
        """Gibt den Status des emotionalen Puffers zurück"""
        return {
            "capacity": self.emotional_buffer.capacity,
            "current_level": self.emotional_buffer.current_level,
            "percentage": self.emotional_buffer.current_level / self.emotional_buffer.capacity,
            "is_depleted": self.emotional_buffer.is_depleted,
            "recovery_rate": self.emotional_buffer.recovery_rate
        }

    # -------------------------------------------------------------------------
    # Analyse und Empfehlungen
    # -------------------------------------------------------------------------

    def get_regulation_recommendation(
        self,
        emotion: EmotionalState
    ) -> Dict[str, Any]:
        """
        Gibt eine Empfehlung für die Emotionsregulation.

        Returns:
            Dict mit Strategie-Empfehlung und Begründung
        """
        # Wähle beste Strategie
        goal = RegulationGoal.DECREASE_NEGATIVE if emotion.valence < 0 else RegulationGoal.MAINTAIN_NEUTRAL
        strategy = self._select_best_strategy(emotion, goal)

        # Finde passenden Reappraisal-Frame wenn relevant
        frame = None
        if strategy == RegulationStrategy.COGNITIVE_REAPPRAISAL:
            frame = self._select_reappraisal_frame(emotion)

        # Berechne erwartete Effektivität
        expected_effectiveness = self.profile.strategy_effectiveness.get(strategy, 0.5)

        # Historische Erfolgsrate
        history = self.strategy_success_rates.get(strategy, [])
        historical_success = sum(history) / len(history) if history else expected_effectiveness

        return {
            "recommended_strategy": strategy.value,
            "expected_effectiveness": expected_effectiveness,
            "historical_success_rate": historical_success,
            "effort_required": self._get_strategy_effort(strategy),
            "reappraisal_frame": frame.name if frame else None,
            "example_thoughts": frame.example_thoughts if frame else [],
            "reasoning": self._generate_recommendation_reasoning(
                emotion, strategy, expected_effectiveness
            )
        }

    def _generate_recommendation_reasoning(
        self,
        emotion: EmotionalState,
        strategy: RegulationStrategy,
        effectiveness: float
    ) -> str:
        """Generiert eine Begründung für die Empfehlung"""

        reasons = []

        if emotion.intensity > 0.7:
            reasons.append(f"Bei hoher Intensität ({emotion.intensity:.0%}) ")
        else:
            reasons.append(f"Bei moderater Intensität ({emotion.intensity:.0%}) ")

        strategy_descriptions = {
            RegulationStrategy.COGNITIVE_REAPPRAISAL:
                "ist kognitive Neubewertung effektiv, um die Situation neu zu interpretieren",
            RegulationStrategy.ACCEPTANCE:
                "kann Akzeptanz helfen, den Widerstand gegen das Gefühl zu reduzieren",
            RegulationStrategy.MINDFULNESS:
                "kann Achtsamkeit helfen, Distanz zum Gefühl zu gewinnen",
            RegulationStrategy.DISTRACTION:
                "kann Ablenkung schnelle Erleichterung bieten",
            RegulationStrategy.HUMOR:
                "kann Humor die Perspektive verändern"
        }

        reasons.append(strategy_descriptions.get(strategy, "könnte diese Strategie helfen"))
        reasons.append(f" (erwartete Wirksamkeit: {effectiveness:.0%}).")

        return "".join(reasons)

    def get_regulation_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über bisherige Regulationsversuche zurück"""

        if not self.regulation_history:
            return {"total_attempts": 0, "no_data": True}

        total = len(self.regulation_history)
        successful = sum(1 for r in self.regulation_history
                        if r.outcome == RegulationOutcome.SUCCESS)
        partial = sum(1 for r in self.regulation_history
                     if r.outcome == RegulationOutcome.PARTIAL)
        failed = sum(1 for r in self.regulation_history
                    if r.outcome == RegulationOutcome.FAILED)
        backfired = sum(1 for r in self.regulation_history
                       if r.outcome == RegulationOutcome.BACKFIRED)

        # Beste Strategien
        strategy_success = {}
        for strategy in RegulationStrategy:
            attempts = [r for r in self.regulation_history if r.strategy == strategy]
            if attempts:
                avg_effectiveness = sum(r.effectiveness for r in attempts) / len(attempts)
                strategy_success[strategy.value] = {
                    "attempts": len(attempts),
                    "average_effectiveness": avg_effectiveness
                }

        return {
            "total_attempts": total,
            "success_rate": successful / total,
            "partial_rate": partial / total,
            "failure_rate": failed / total,
            "backfire_rate": backfired / total,
            "strategy_performance": strategy_success,
            "buffer_status": self.get_buffer_status(),
            "profile_resilience": self.profile.emotional_resilience
        }


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def quick_regulate(
    emotion: str,
    intensity: float,
    valence: float = -0.5
) -> RegulationAttempt:
    """
    Schnelle Emotionsregulation ohne Engine-Instanz.

    Args:
        emotion: Name der Emotion
        intensity: Intensität (0.0 - 1.0)
        valence: Valenz (-1.0 bis 1.0)

    Returns:
        RegulationAttempt
    """
    engine = EmotionRegulationEngine()
    state = EmotionalState(
        primary_emotion=emotion,
        intensity=intensity,
        valence=valence,
        arousal=intensity * 0.8,
        duration=60
    )
    return engine.regulate(state)


def suggest_regulation_strategy(
    emotion: str,
    intensity: float,
    context: str = ""
) -> str:
    """
    Schlägt eine Regulationsstrategie vor.

    Returns:
        Name der empfohlenen Strategie
    """
    engine = EmotionRegulationEngine()
    state = EmotionalState(
        primary_emotion=emotion,
        intensity=intensity,
        valence=-0.5 if emotion in ["anger", "sadness", "fear", "anxiety"] else 0.3,
        arousal=intensity,
        duration=60,
        trigger=context if context else None
    )
    recommendation = engine.get_regulation_recommendation(state)
    return recommendation["recommended_strategy"]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "RegulationStrategy",
    "EmotionIntensity",
    "RegulationGoal",
    "RegulationOutcome",

    # Dataclasses
    "EmotionalState",
    "RegulationAttempt",
    "ReappraisalFrame",
    "EmotionalBuffer",
    "RegulationProfile",

    # Main class
    "EmotionRegulationEngine",

    # Helper functions
    "quick_regulate",
    "suggest_regulation_strategy",

    # Constants
    "REAPPRAISAL_FRAMES"
]
