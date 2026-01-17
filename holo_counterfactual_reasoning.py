"""
holo_counterfactual_reasoning.py - Abduktives und kontrafaktisches Denken

Dieses Modul implementiert fortgeschrittene Reasoning-Fähigkeiten:
- Kontrafaktisches Denken ("Was wäre wenn...")
- Abduktives Reasoning (Schluss auf die beste Erklärung)
- Hypothetische Szenarien
- Kausalanalyse und Ursachenforschung
- Alternative Realitäten erkunden

REFACTORED: Nutzt jetzt bestehende Module für:
- Opinion/Hypothesis → holo_core_types.Opinion
- Fact → holo_learning (LearnedFact-kompatibel)
- Entity-Extraktion → holo_learning.FactExtractor
- Sandbox-Simulation → holo_meta_cognition.HoloSandbox

Autor: Holocloude System
Version: 2.0 (Refactored)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, TYPE_CHECKING, Tuple, Set
from enum import Enum
from datetime import datetime
from collections import defaultdict
import random
import logging
import time

# ============================================================================
# IMPORTS VON BESTEHENDEN MODULEN
# ============================================================================

# Core Types - für Opinion (Hypothesis-ähnlich)
try:
    from holo_core_types import Opinion, GoalType
except ImportError:
    Opinion = None
    GoalType = None

# Learning - für Fakten-Extraktion
try:
    from holo_learning import FactExtractor, LearnedFact, FactCategory
    _HAS_LEARNING = True
except ImportError:
    _HAS_LEARNING = False
    FactExtractor = None
    LearnedFact = None
    FactCategory = None

# Meta-Cognition - für Sandbox-Simulation
try:
    from holo_meta_cognition import HoloSandbox, SandboxResult
    _HAS_SANDBOX = True
except ImportError:
    _HAS_SANDBOX = False
    HoloSandbox = None
    SandboxResult = None

logger = logging.getLogger("HoloCounterfactual")

# ============================================================================
# ENUMS - EINZIGARTIG FÜR DIESES MODUL
# ============================================================================

class ReasoningType(Enum):
    """Arten des Schlussfolgerns"""
    DEDUCTIVE = "deductive"         # Von allgemein zu spezifisch
    INDUCTIVE = "inductive"         # Von spezifisch zu allgemein
    ABDUCTIVE = "abductive"         # Schluss auf beste Erklärung
    COUNTERFACTUAL = "counterfactual"  # Was wäre wenn
    CAUSAL = "causal"               # Ursache-Wirkung
    ANALOGICAL = "analogical"       # Analogieschluss


class CounterfactualType(Enum):
    """Arten kontrafaktischer Gedanken"""
    UPWARD = "upward"           # Bessere Alternativen ("Hätte ich nur...")
    DOWNWARD = "downward"       # Schlechtere Alternativen ("Es hätte schlimmer sein können")
    ADDITIVE = "additive"       # Etwas hinzufügen ("Wenn ich X getan hätte...")
    SUBTRACTIVE = "subtractive" # Etwas wegnehmen ("Wenn ich X nicht getan hätte...")
    SUBSTITUTIONAL = "substitutional"  # Ersetzen ("Wenn ich Y statt X...")


class CausalRelationType(Enum):
    """Arten kausaler Beziehungen"""
    NECESSARY = "necessary"     # Notwendige Bedingung
    SUFFICIENT = "sufficient"   # Hinreichende Bedingung
    CONTRIBUTING = "contributing"  # Beitragender Faktor
    INHIBITING = "inhibiting"   # Hemmender Faktor
    CORRELATIONAL = "correlational"  # Nur korreliert


class ExplanationQuality(Enum):
    """Qualität einer Erklärung"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    WEAK = "weak"
    SPECULATIVE = "speculative"


# ============================================================================
# DATENKLASSEN - EINZIGARTIG FÜR KONTRAFAKTISCHES DENKEN
# ============================================================================

@dataclass
class Observation:
    """
    Eine Beobachtung/Fakt für Reasoning.

    Kompatibel mit holo_learning.LearnedFact aber leichtgewichtig.
    Kann zu LearnedFact konvertiert werden wenn nötig.
    """
    content: str
    confidence: float = 1.0
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    is_observation: bool = True

    def to_learned_fact(self, topic: str = "general") -> Optional['LearnedFact']:
        """Konvertiert zu LearnedFact wenn holo_learning verfügbar"""
        if not _HAS_LEARNING or LearnedFact is None:
            return None
        return LearnedFact(
            fact_id="",
            content=self.content,
            category=FactCategory.GENERAL if FactCategory else None,
            topic=topic,
            keywords=[],
            source_title=self.source or "observation",
            source_url="",
            source_feed="counterfactual_reasoning",
            importance=self.confidence,
            trust_score=self.confidence,
        )


@dataclass
class Hypothesis:
    """
    Eine Hypothese/Erklärung.

    Nutzt Opinion aus holo_core_types für Bayesian-Updates wenn verfügbar.
    """
    content: str
    explains: List[Observation]
    probability: float = 0.5
    simplicity: float = 0.5       # Occam's Razor
    coherence: float = 0.5        # Kohärenz mit anderen Überzeugungen
    testable: bool = True
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)

    # Optionale Opinion für adaptives Lernen
    _opinion: Optional['Opinion'] = field(default=None, repr=False)

    def __post_init__(self):
        """Erstellt Opinion wenn verfügbar"""
        if Opinion is not None and self._opinion is None:
            self._opinion = Opinion(
                topic=f"hypothesis:{self.content[:50]}",
                stance=self.content,
                confidence=self.probability,
                reasoning=self.supporting_evidence[:5]
            )

    @property
    def plausibility_score(self) -> float:
        """Berechnet einen Plausibilitäts-Score"""
        score = (
            self.probability * 0.4 +
            self.simplicity * 0.2 +
            self.coherence * 0.2 +
            (len(self.supporting_evidence) /
             max(1, len(self.supporting_evidence) + len(self.contradicting_evidence))) * 0.2
        )
        return min(1.0, max(0.0, score))

    def observe_feedback(self, agreed: bool, strength: float = 1.0):
        """
        Passt Hypothese basierend auf Feedback an.
        Nutzt Opinion.observe_user_feedback wenn verfügbar.
        """
        if self._opinion is not None:
            self._opinion.observe_user_feedback(agreed, strength)
            self.probability = self._opinion.confidence
        else:
            # Fallback ohne Opinion
            change = 0.1 * strength
            if agreed:
                self.probability = min(1.0, self.probability + change)
            else:
                self.probability = max(0.0, self.probability - change)


@dataclass
class CounterfactualScenario:
    """Ein kontrafaktisches Szenario - EINZIGARTIG"""
    original_event: str
    antecedent: str               # Die geänderte Bedingung ("Wenn X...")
    consequent: str               # Die vermutete Folge ("...dann Y")
    type: CounterfactualType
    plausibility: float
    emotional_impact: float
    controllability: float
    distance: float               # Wie weit von der Realität entfernt

    def describe(self) -> str:
        """Beschreibt das Szenario in natürlicher Sprache"""
        return f"Wenn {self.antecedent}, dann {self.consequent}."


@dataclass
class CausalLink:
    """Eine kausale Verbindung - EINZIGARTIG"""
    cause: str
    effect: str
    relation_type: CausalRelationType
    strength: float
    confidence: float
    mechanism: Optional[str] = None
    conditions: List[str] = field(default_factory=list)


@dataclass
class AbductiveExplanation:
    """Eine abduktive Erklärung - EINZIGARTIG"""
    phenomenon: str
    hypothesis: Hypothesis
    quality: ExplanationQuality
    alternatives: List[Hypothesis] = field(default_factory=list)
    reasoning_chain: List[str] = field(default_factory=list)
    confidence: float = 0.5

    @property
    def is_best_explanation(self) -> bool:
        """Ist dies die beste verfügbare Erklärung?"""
        if not self.alternatives:
            return True
        return all(
            self.hypothesis.plausibility_score >= alt.plausibility_score
            for alt in self.alternatives
        )


@dataclass
class CausalModel:
    """Ein kausales Modell - EINZIGARTIG"""
    variables: List[str]
    links: List[CausalLink]
    context: str

    def get_causes(self, effect: str) -> List[CausalLink]:
        """Gibt alle Ursachen eines Effekts zurück"""
        return [link for link in self.links if link.effect == effect]

    def get_effects(self, cause: str) -> List[CausalLink]:
        """Gibt alle Effekte einer Ursache zurück"""
        return [link for link in self.links if link.cause == cause]

    def find_root_causes(self, effect: str) -> List[str]:
        """Findet die Wurzelursachen"""
        root_causes = []
        to_check = [link.cause for link in self.get_causes(effect)]
        visited = set()

        while to_check:
            current = to_check.pop(0)
            if current in visited:
                continue
            visited.add(current)

            causes = self.get_causes(current)
            if not causes:
                root_causes.append(current)
            else:
                to_check.extend([link.cause for link in causes])

        return list(set(root_causes))


# ============================================================================
# ENTITY EXTRACTOR WRAPPER
# ============================================================================

class EventAnalyzer:
    """
    Analysiert Events und extrahiert Komponenten.
    Nutzt FactExtractor aus holo_learning wenn verfügbar.
    """

    def __init__(self):
        self._fact_extractor = None
        if _HAS_LEARNING and FactExtractor is not None:
            try:
                self._fact_extractor = FactExtractor()
                logger.info("[EventAnalyzer] Nutzt FactExtractor aus holo_learning")
            except Exception as e:
                logger.warning(f"[EventAnalyzer] FactExtractor nicht verfügbar: {e}")

    def analyze(self, event: str) -> Dict[str, Any]:
        """Analysiert ein Ereignis in seine Komponenten"""
        components = {
            "original": event,
            "actors": self._extract_actors(event),
            "actions": self._extract_actions(event),
            "outcomes": self._extract_outcomes(event),
            "conditions": self._extract_conditions(event),
            "timing": self._extract_timing(event),
        }

        # Nutze FactExtractor für erweiterte Extraktion wenn verfügbar
        if self._fact_extractor is not None:
            try:
                # FactExtractor kann Entities und Keywords extrahieren
                components["entities"] = self._fact_extractor._extract_entities(event)
                components["keywords"] = self._fact_extractor._extract_keywords(event)
                components["topic"] = self._fact_extractor._detect_topic(event)
            except Exception:
                pass

        return components

    def _extract_actors(self, event: str) -> List[str]:
        """Extrahiert Akteure"""
        actors = []
        indicators = ["ich", "du", "er", "sie", "wir", "man", "jemand"]
        event_lower = event.lower()
        for indicator in indicators:
            if indicator in event_lower:
                actors.append(indicator)
        return actors if actors else ["unbekannt"]

    def _extract_actions(self, event: str) -> List[str]:
        """Extrahiert Aktionen"""
        action_words = ["tat", "machte", "sagte", "ging", "kam", "gab",
                       "nahm", "entschied", "wollte", "versuchte"]
        actions = []
        for word in action_words:
            if word in event.lower():
                actions.append(word)
        return actions if actions else ["handelte"]

    def _extract_outcomes(self, event: str) -> List[str]:
        """Extrahiert Ergebnisse"""
        indicators = ["führte zu", "resultierte", "endete", "bewirkte", "verursachte"]
        for indicator in indicators:
            if indicator in event.lower():
                idx = event.lower().index(indicator)
                return [event[idx:].split(".")[0]]
        return ["unbekanntes Ergebnis"]

    def _extract_conditions(self, event: str) -> List[str]:
        """Extrahiert Bedingungen"""
        condition_words = ["weil", "da", "wenn", "falls", "unter", "aufgrund"]
        conditions = []
        for word in condition_words:
            if word in event.lower():
                idx = event.lower().index(word)
                conditions.append(event[idx:].split(",")[0])
        return conditions

    def _extract_timing(self, event: str) -> Optional[str]:
        """Extrahiert Zeitangaben"""
        time_words = ["gestern", "heute", "morgen", "letzte", "nächste",
                     "um", "vor", "nach"]
        for word in time_words:
            if word in event.lower():
                return word
        return None


# ============================================================================
# HAUPTKLASSE: COUNTERFACTUAL REASONING ENGINE
# ============================================================================

class CounterfactualReasoningEngine:
    """
    Engine für kontrafaktisches und abduktives Denken.

    REFACTORED: Nutzt bestehende Module für Entity-Extraktion und Simulation.

    Ermöglicht:
    - "Was wäre wenn" Szenarien durchspielen
    - Beste Erklärungen für Beobachtungen finden
    - Kausale Zusammenhänge analysieren
    - Alternative Realitäten erkunden
    """

    def __init__(self, sandbox: 'HoloSandbox' = None):
        self.observations: List[Observation] = []
        self.hypotheses: List[Hypothesis] = []
        self.causal_models: Dict[str, CausalModel] = {}
        self.counterfactual_history: List[CounterfactualScenario] = []

        # Event-Analyzer (nutzt FactExtractor wenn verfügbar)
        self._event_analyzer = EventAnalyzer()

        # Sandbox für "Was wäre wenn" Simulation
        self._sandbox = sandbox
        if self._sandbox is None and _HAS_SANDBOX and HoloSandbox is not None:
            try:
                self._sandbox = HoloSandbox()
                logger.info("[CounterfactualEngine] Nutzt HoloSandbox für Simulation")
            except Exception as e:
                logger.warning(f"[CounterfactualEngine] HoloSandbox nicht verfügbar: {e}")

        # Erklärungsvorlagen
        self.explanation_templates = self._init_explanation_templates()
        self.causal_patterns = self._init_causal_patterns()

    def _init_explanation_templates(self) -> Dict[str, List[str]]:
        """Initialisiert Erklärungsvorlagen"""
        return {
            "behavior_change": [
                "Die Person hat {effect} weil {cause}",
                "Der Grund für {effect} könnte {cause} sein",
                "{cause} führte wahrscheinlich zu {effect}"
            ],
            "unexpected_event": [
                "Das unerwartete Ereignis {effect} lässt sich durch {cause} erklären",
                "Eine mögliche Erklärung für {effect} ist {cause}"
            ],
            "pattern": [
                "Das Muster von {effect} deutet auf {cause} hin",
                "Basierend auf {observations} ist {cause} die wahrscheinlichste Erklärung"
            ],
        }

    def _init_causal_patterns(self) -> List[Dict]:
        """Initialisiert bekannte kausale Muster"""
        return [
            {"name": "motivation_action", "pattern": "{person} wollte {goal}, also {action}", "strength": 0.7},
            {"name": "obstacle_failure", "pattern": "{obstacle} verhinderte {intended_outcome}", "strength": 0.6},
            {"name": "emotion_behavior", "pattern": "{person} fühlte {emotion}, deshalb {behavior}", "strength": 0.65},
            {"name": "condition_outcome", "pattern": "Unter {conditions} führt {action} zu {outcome}", "strength": 0.5}
        ]

    # -------------------------------------------------------------------------
    # Kontrafaktisches Denken
    # -------------------------------------------------------------------------

    def generate_counterfactual(
        self,
        event: str,
        change_type: CounterfactualType = CounterfactualType.UPWARD,
        focus: Optional[str] = None
    ) -> CounterfactualScenario:
        """Generiert ein kontrafaktisches Szenario."""
        # Analysiere das Event mit EventAnalyzer
        components = self._event_analyzer.analyze(event)

        # Generiere Antezedent und Konsequent
        antecedent = self._generate_antecedent(components, change_type, focus)
        consequent = self._generate_consequent(components, antecedent, change_type)

        # Berechne Eigenschaften
        plausibility = self._calculate_plausibility(event, antecedent, consequent)
        emotional_impact = self._calculate_emotional_impact(change_type, plausibility)
        controllability = self._assess_controllability(antecedent)
        distance = self._calculate_distance(event, antecedent)

        scenario = CounterfactualScenario(
            original_event=event,
            antecedent=antecedent,
            consequent=consequent,
            type=change_type,
            plausibility=plausibility,
            emotional_impact=emotional_impact,
            controllability=controllability,
            distance=distance
        )

        self.counterfactual_history.append(scenario)
        return scenario

    def explore_alternatives(self, event: str, num_alternatives: int = 3) -> List[CounterfactualScenario]:
        """Erkundet mehrere alternative Szenarien."""
        alternatives = []
        types_to_try = [
            CounterfactualType.UPWARD,
            CounterfactualType.DOWNWARD,
            CounterfactualType.ADDITIVE,
            CounterfactualType.SUBTRACTIVE
        ]

        for i in range(num_alternatives):
            cf_type = types_to_try[i % len(types_to_try)]
            scenario = self.generate_counterfactual(event, cf_type)
            alternatives.append(scenario)

        alternatives.sort(key=lambda x: x.plausibility, reverse=True)
        return alternatives

    def _generate_antecedent(self, components: Dict, change_type: CounterfactualType, focus: Optional[str]) -> str:
        """Generiert den Antezedent"""
        templates = {
            CounterfactualType.UPWARD: [
                "ich früher reagiert hätte",
                "ich anders entschieden hätte",
                "ich vorbereitet gewesen wäre",
            ],
            CounterfactualType.DOWNWARD: [
                "ich gar nicht reagiert hätte",
                "die Situation eskaliert wäre",
                "niemand geholfen hätte",
            ],
            CounterfactualType.ADDITIVE: [
                "ich zusätzlich {focus} getan hätte",
                "mehr Zeit gewesen wäre",
                "ich Hilfe gehabt hätte",
            ],
            CounterfactualType.SUBTRACTIVE: [
                "ich {focus} nicht getan hätte",
                "dieses Hindernis nicht existiert hätte",
            ],
            CounterfactualType.SUBSTITUTIONAL: [
                "ich stattdessen {focus} getan hätte",
                "eine andere Option gewählt worden wäre",
            ],
        }

        antecedent = random.choice(templates.get(change_type, templates[CounterfactualType.UPWARD]))
        if focus and "{focus}" in antecedent:
            antecedent = antecedent.replace("{focus}", focus)
        elif "{focus}" in antecedent:
            antecedent = antecedent.replace("{focus}", "etwas anderes")

        return antecedent

    def _generate_consequent(self, components: Dict, antecedent: str, change_type: CounterfactualType) -> str:
        """Generiert den Konsequent"""
        consequences = {
            CounterfactualType.UPWARD: [
                "wäre das Ergebnis besser gewesen",
                "hätte ich mehr erreicht",
                "wäre es erfolgreicher verlaufen",
            ],
            CounterfactualType.DOWNWARD: [
                "wäre es viel schlimmer gekommen",
                "hätte ich alles verloren",
                "wäre die Situation eskaliert",
            ],
        }
        return random.choice(consequences.get(change_type, ["wäre das Ergebnis anders gewesen"]))

    def _calculate_plausibility(self, event: str, antecedent: str, consequent: str) -> float:
        """Berechnet die Plausibilität"""
        plausibility = 0.5

        if "nicht" in antecedent and len(antecedent.split()) < 5:
            plausibility += 0.2

        controllable_words = ["ich", "wir", "meine", "entschied"]
        if any(word in antecedent.lower() for word in controllable_words):
            plausibility += 0.15

        if "wäre" in consequent or "hätte" in consequent:
            plausibility += 0.1

        return min(1.0, max(0.0, plausibility))

    def _calculate_emotional_impact(self, change_type: CounterfactualType, plausibility: float) -> float:
        """Berechnet den emotionalen Impact"""
        base_impact = {
            CounterfactualType.UPWARD: 0.6,
            CounterfactualType.DOWNWARD: 0.4,
            CounterfactualType.ADDITIVE: 0.5,
            CounterfactualType.SUBTRACTIVE: 0.5,
            CounterfactualType.SUBSTITUTIONAL: 0.4
        }
        return base_impact.get(change_type, 0.5) * plausibility

    def _assess_controllability(self, antecedent: str) -> float:
        """Bewertet Kontrollierbarkeit"""
        controllability = 0.5
        for indicator in ["ich", "mein", "entschied", "wählte"]:
            if indicator in antecedent.lower():
                controllability += 0.1
        for indicator in ["zufällig", "schicksal", "glück", "pech"]:
            if indicator in antecedent.lower():
                controllability -= 0.1
        return min(1.0, max(0.0, controllability))

    def _calculate_distance(self, event: str, antecedent: str) -> float:
        """Berechnet die 'Distanz' von der Realität"""
        word_overlap = len(set(event.lower().split()) & set(antecedent.lower().split()))
        total_words = len(set(event.lower().split()) | set(antecedent.lower().split()))
        if total_words == 0:
            return 0.5
        return 1.0 - (word_overlap / total_words)

    # -------------------------------------------------------------------------
    # Abduktives Reasoning
    # -------------------------------------------------------------------------

    def abduce(self, observations: List[str], context: Optional[str] = None) -> AbductiveExplanation:
        """
        Führt abduktives Reasoning durch - findet die beste Erklärung.
        """
        # Konvertiere zu Observations
        obs_list = [Observation(content=obs) for obs in observations]

        # Generiere Hypothesen
        hypotheses = self._generate_hypotheses(obs_list, context)

        if not hypotheses:
            hypotheses = [Hypothesis(
                content="Unbekannte Ursache",
                explains=obs_list,
                probability=0.3,
                simplicity=0.5,
                coherence=0.5
            )]

        # Ranke Hypothesen
        ranked = sorted(hypotheses, key=lambda h: h.plausibility_score, reverse=True)

        best = ranked[0]
        alternatives = ranked[1:4] if len(ranked) > 1 else []

        quality = self._assess_explanation_quality(best, obs_list)
        reasoning = self._build_reasoning_chain(obs_list, best)

        return AbductiveExplanation(
            phenomenon=" | ".join(observations),
            hypothesis=best,
            quality=quality,
            alternatives=alternatives,
            reasoning_chain=reasoning,
            confidence=best.plausibility_score
        )

    def _generate_hypotheses(self, observations: List[Observation], context: Optional[str]) -> List[Hypothesis]:
        """Generiert mögliche Hypothesen"""
        hypotheses = []

        patterns = [
            ("Motivation", "Die Person wollte etwas erreichen"),
            ("Externe Ursache", "Äußere Umstände haben dies verursacht"),
            ("Emotionale Reaktion", "Eine emotionale Reaktion führte dazu"),
            ("Missverständnis", "Ein Missverständnis liegt vor"),
            ("Gewohnheit", "Gewohnheitsmäßiges Verhalten"),
            ("Absicht", "Es war beabsichtigt"),
            ("Zufall", "Zufälliges Zusammentreffen"),
            ("Konsequenz", "Folge früherer Ereignisse")
        ]

        for name, base_explanation in patterns:
            relevance = self._calculate_pattern_relevance(name, observations, context)

            if relevance > 0.3:
                hypothesis = Hypothesis(
                    content=f"{base_explanation} ({name})",
                    explains=observations,
                    probability=relevance,
                    simplicity=random.uniform(0.4, 0.8),
                    coherence=random.uniform(0.5, 0.9),
                    supporting_evidence=[o.content for o in observations[:2]]
                )
                hypotheses.append(hypothesis)

        return hypotheses

    def _calculate_pattern_relevance(self, pattern_name: str, observations: List[Observation], context: Optional[str]) -> float:
        """Berechnet Muster-Relevanz"""
        relevance = 0.5

        keywords = {
            "Motivation": ["wollte", "ziel", "absicht", "versuchte"],
            "Externe Ursache": ["passierte", "geschah", "plötzlich", "unerwartet"],
            "Emotionale Reaktion": ["fühlte", "wütend", "traurig", "freute"],
            "Missverständnis": ["dachte", "glaubte", "meinte", "verstand nicht"],
            "Gewohnheit": ["immer", "gewöhnlich", "typisch", "normalerweise"],
            "Absicht": ["wollte", "plante", "entschied", "beschloss"],
            "Zufall": ["zufällig", "gerade", "ausgerechnet"],
            "Konsequenz": ["deshalb", "daher", "folglich", "weil"]
        }

        pattern_keywords = keywords.get(pattern_name, [])
        all_text = " ".join([o.content for o in observations])
        if context:
            all_text += " " + context

        for keyword in pattern_keywords:
            if keyword in all_text.lower():
                relevance += 0.15

        return min(1.0, relevance)

    def _assess_explanation_quality(self, hypothesis: Hypothesis, observations: List[Observation]) -> ExplanationQuality:
        """Bewertet Erklärungsqualität"""
        score = hypothesis.plausibility_score
        coverage = len(hypothesis.explains) / max(1, len(observations))
        score += coverage * 0.2

        if score > 0.8:
            return ExplanationQuality.EXCELLENT
        elif score > 0.6:
            return ExplanationQuality.GOOD
        elif score > 0.4:
            return ExplanationQuality.MODERATE
        elif score > 0.2:
            return ExplanationQuality.WEAK
        else:
            return ExplanationQuality.SPECULATIVE

    def _build_reasoning_chain(self, observations: List[Observation], hypothesis: Hypothesis) -> List[str]:
        """Baut eine Reasoning-Kette auf"""
        chain = []
        chain.append(f"Beobachtung: {observations[0].content if observations else 'Keine'}")
        if len(observations) > 1:
            chain.append(f"Weitere: {', '.join(o.content for o in observations[1:3])}")
        chain.append(f"Erklärung: {hypothesis.content}")
        chain.append(f"Plausibilität: {hypothesis.plausibility_score:.0%}")
        return chain

    # -------------------------------------------------------------------------
    # Kausalanalyse
    # -------------------------------------------------------------------------

    def analyze_causality(self, effect: str, potential_causes: List[str], context: Optional[str] = None) -> List[CausalLink]:
        """Analysiert kausale Zusammenhänge."""
        causal_links = []

        for cause in potential_causes:
            link = self._evaluate_causal_link(cause, effect, context)
            if link.strength > 0.2:
                causal_links.append(link)

        causal_links.sort(key=lambda x: x.strength, reverse=True)
        return causal_links

    def _evaluate_causal_link(self, cause: str, effect: str, context: Optional[str]) -> CausalLink:
        """Bewertet eine kausale Verbindung"""
        relation_type = self._determine_relation_type(cause, effect)
        strength = self._calculate_causal_strength(cause, effect, context)
        confidence = self._calculate_causal_confidence(cause, effect)
        mechanism = self._identify_mechanism(cause, effect)

        return CausalLink(
            cause=cause,
            effect=effect,
            relation_type=relation_type,
            strength=strength,
            confidence=confidence,
            mechanism=mechanism
        )

    def _determine_relation_type(self, cause: str, effect: str) -> CausalRelationType:
        """Bestimmt Beziehungstyp"""
        if "immer" in cause.lower() or "notwendig" in cause.lower():
            return CausalRelationType.NECESSARY
        elif "genügt" in cause.lower() or "reicht" in cause.lower():
            return CausalRelationType.SUFFICIENT
        elif "verhindert" in cause.lower() or "blockiert" in cause.lower():
            return CausalRelationType.INHIBITING
        elif "zusammenhang" in cause.lower() or "korreliert" in cause.lower():
            return CausalRelationType.CORRELATIONAL
        return CausalRelationType.CONTRIBUTING

    def _calculate_causal_strength(self, cause: str, effect: str, context: Optional[str]) -> float:
        """Berechnet kausale Stärke"""
        strength = 0.5

        temporal_words = ["dann", "daraufhin", "sofort", "unmittelbar"]
        if context and any(word in context.lower() for word in temporal_words):
            strength += 0.15

        causal_words = ["deshalb", "daher", "weil", "führte zu", "verursachte"]
        combined = f"{cause} {effect} {context or ''}"
        if any(word in combined.lower() for word in causal_words):
            strength += 0.2

        return min(1.0, strength)

    def _calculate_causal_confidence(self, cause: str, effect: str) -> float:
        """Berechnet kausale Konfidenz"""
        confidence = 0.5
        for pattern in self.causal_patterns:
            if cause in pattern["pattern"] or effect in pattern["pattern"]:
                confidence += 0.1
        return min(1.0, confidence)

    def _identify_mechanism(self, cause: str, effect: str) -> Optional[str]:
        """Identifiziert kausalen Mechanismus"""
        if "fühl" in cause.lower() or "emotion" in cause.lower():
            return "durch psychologische Auswirkungen"
        elif "gab" in cause.lower() or "nahm" in cause.lower():
            return "durch Veränderung der Ressourcen"
        return None

    def build_causal_model(self, situation: str, variables: List[str]) -> CausalModel:
        """Baut ein kausales Modell."""
        links = []

        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i != j:
                    link = self._evaluate_causal_link(var1, var2, situation)
                    if link.strength > 0.3:
                        links.append(link)

        model = CausalModel(variables=variables, links=links, context=situation)
        model_key = f"model_{len(self.causal_models)}"
        self.causal_models[model_key] = model

        return model

    # -------------------------------------------------------------------------
    # "Was wäre wenn" Simulation (integriert mit HoloSandbox)
    # -------------------------------------------------------------------------

    def what_would_happen_if(self, scenario: str, change: str) -> Dict[str, Any]:
        """
        Beantwortet "Was würde passieren wenn..." Fragen.

        Nutzt HoloSandbox für erweiterte Simulation wenn verfügbar.
        """
        # Generiere kontrafaktisches Szenario
        cf = self.generate_counterfactual(
            scenario,
            CounterfactualType.SUBSTITUTIONAL,
            focus=change
        )

        # Nutze Sandbox für erweiterte Simulation wenn verfügbar
        sandbox_result = None
        if self._sandbox is not None:
            try:
                options = [cf.consequent, "neutrales Ergebnis", "unvorhergesehenes Ergebnis"]
                sandbox_result = self._sandbox.evaluate_options(options, {"scenario": scenario, "change": change})
            except Exception as e:
                logger.debug(f"Sandbox-Simulation fehlgeschlagen: {e}")

        # Generiere Vorhersage
        prediction = {
            "outcome": cf.consequent,
            "confidence": cf.plausibility * 0.8,
            "reasoning": [
                f"Basierend auf: {cf.antecedent}",
                f"Plausibilität: {cf.plausibility:.0%}",
                f"Kontrollierbarkeit: {cf.controllability:.0%}"
            ],
            "alternatives": ["Das Ergebnis könnte neutral sein", "Nebenwirkungen möglich"]
        }

        if sandbox_result:
            prediction["sandbox_evaluation"] = [
                {"option": r.option, "confidence": r.confidence, "risk": r.risk_level}
                for r in sandbox_result[:3]
            ]

        return {
            "original_scenario": scenario,
            "hypothetical_change": change,
            "counterfactual": cf.describe(),
            "plausibility": cf.plausibility,
            "predicted_outcome": prediction["outcome"],
            "confidence": prediction["confidence"],
            "reasoning": prediction["reasoning"],
            "alternative_outcomes": prediction["alternatives"],
            "sandbox_evaluation": prediction.get("sandbox_evaluation"),
        }


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def quick_counterfactual(event: str) -> str:
    """Schnelle kontrafaktische Gedanken-Generierung."""
    engine = CounterfactualReasoningEngine()
    cf = engine.generate_counterfactual(event)
    return cf.describe()


def find_best_explanation(observations: List[str]) -> str:
    """Findet die beste Erklärung für Beobachtungen."""
    engine = CounterfactualReasoningEngine()
    explanation = engine.abduce(observations)
    return f"{explanation.hypothesis.content} (Konfidenz: {explanation.confidence:.0%})"


def analyze_what_if(scenario: str, change: str) -> Dict[str, Any]:
    """Analysiert ein "Was wäre wenn" Szenario."""
    engine = CounterfactualReasoningEngine()
    return engine.what_would_happen_if(scenario, change)


# ============================================================================
# ADVANCED CAUSALITY SYSTEM v2.0 - Für 10/10 Kausalität
# ============================================================================

class InterventionalReasoning:
    """
    Interventionelles Reasoning - Do-Calculus.

    Unterscheidet zwischen:
    - P(Y | X)         : Beobachtung (Korrelation)
    - P(Y | do(X))     : Intervention (Kausalität)

    Beantwortet: "Was passiert wenn wir X AKTIV ändern?"
    (nicht nur beobachten)
    """

    def __init__(self):
        # Bekannte Interventionseffekte
        self.intervention_effects: Dict[str, Dict[str, float]] = defaultdict(dict)
        # Beobachtete Korrelationen
        self.observed_correlations: Dict[str, Dict[str, float]] = defaultdict(dict)
        # Konfundierungs-Wissen
        self.known_confounders: Dict[Tuple[str, str], List[str]] = {}

    def observe(self, cause: str, effect: str, strength: float):
        """Registriert beobachtete Korrelation P(effect | cause)"""
        self.observed_correlations[cause][effect] = strength

    def intervene(self, intervention: str, outcome: str, effect_strength: float):
        """Registriert Interventionseffekt P(outcome | do(intervention))"""
        self.intervention_effects[intervention][outcome] = effect_strength

    def add_confounder(self, var_a: str, var_b: str, confounder: str):
        """Registriert bekannten Confounder zwischen zwei Variablen"""
        key = (min(var_a, var_b), max(var_a, var_b))
        if key not in self.known_confounders:
            self.known_confounders[key] = []
        if confounder not in self.known_confounders[key]:
            self.known_confounders[key].append(confounder)

    def estimate_do_effect(self, intervention: str, outcome: str) -> Dict[str, Any]:
        """
        Schätzt P(outcome | do(intervention)).

        Korrigiert für bekannte Confounder.
        """
        result = {
            "intervention": intervention,
            "outcome": outcome,
            "causal_effect": 0.0,
            "correlation": 0.0,
            "confounders": [],
            "is_causal": False,
            "confidence": 0.0,
            "reasoning": []
        }

        # 1. Beobachtete Korrelation
        correlation = self.observed_correlations.get(intervention, {}).get(outcome, 0)
        result["correlation"] = correlation

        # 2. Bekannte Interventionseffekte
        if intervention in self.intervention_effects:
            if outcome in self.intervention_effects[intervention]:
                effect = self.intervention_effects[intervention][outcome]
                result["causal_effect"] = effect
                result["is_causal"] = True
                result["confidence"] = 0.9
                result["reasoning"].append(f"Direkter Interventionseffekt bekannt: {effect:.2f}")
                return result

        # 3. Prüfe auf Confounder
        key = (min(intervention, outcome), max(intervention, outcome))
        confounders = self.known_confounders.get(key, [])
        result["confounders"] = confounders

        if confounders:
            # Korrelation könnte durch Confounder erklärt werden
            # Reduziere geschätzten Kausaleffekt
            reduction = 0.3 * len(confounders)
            adjusted_effect = max(0, correlation - reduction)
            result["causal_effect"] = adjusted_effect
            result["is_causal"] = adjusted_effect > 0.2
            result["confidence"] = 0.5
            result["reasoning"].append(
                f"Confounder gefunden: {confounders}. "
                f"Korrelation {correlation:.2f} → adjustierter Effekt {adjusted_effect:.2f}"
            )
        else:
            # Keine bekannten Confounder - Korrelation könnte kausal sein
            result["causal_effect"] = correlation * 0.7  # Konservativer Schätzer
            result["is_causal"] = correlation > 0.3
            result["confidence"] = 0.6
            result["reasoning"].append(
                f"Keine Confounder bekannt. Konservative Schätzung: {correlation * 0.7:.2f}"
            )

        return result

    def would_intervention_help(self, goal: str, possible_interventions: List[str]) -> List[Dict]:
        """Bewertet welche Interventionen am wahrscheinlichsten zum Ziel führen"""
        results = []

        for intervention in possible_interventions:
            effect = self.estimate_do_effect(intervention, goal)
            results.append({
                "intervention": intervention,
                "expected_effect": effect["causal_effect"],
                "is_causal": effect["is_causal"],
                "confounders": effect["confounders"],
                "recommendation": "empfohlen" if effect["causal_effect"] > 0.5 else "unsicher"
            })

        # Sortiere nach erwartetem Effekt
        results.sort(key=lambda x: x["expected_effect"], reverse=True)
        return results


class CausalDiscovery:
    """
    Kausale Struktur-Entdeckung.

    Inspiriert vom PC-Algorithmus, aber vereinfacht für Pi4.
    Findet kausale Beziehungen aus Beobachtungsdaten.
    """

    def __init__(self):
        # Beobachtete Co-Occurences
        self.co_occurrences: Dict[Tuple[str, str], int] = defaultdict(int)
        # Zeitliche Abfolgen (A vor B)
        self.temporal_order: Dict[Tuple[str, str], int] = defaultdict(int)
        # Entdeckte kausale Kanten
        self.discovered_edges: List[Tuple[str, str, float]] = []

    def observe_event(self, event: str, context_events: List[str], timestamp: float = None):
        """Registriert ein Event mit Kontext"""
        if timestamp is None:
            timestamp = time.time()

        for ctx_event in context_events:
            # Co-Occurrence
            pair = (min(event, ctx_event), max(event, ctx_event))
            self.co_occurrences[pair] += 1

    def observe_sequence(self, events: List[str]):
        """Registriert zeitliche Abfolge von Events"""
        for i in range(len(events) - 1):
            for j in range(i + 1, len(events)):
                # events[i] kam vor events[j]
                self.temporal_order[(events[i], events[j])] += 1

    def discover_structure(self, min_observations: int = 5) -> Dict[str, Any]:
        """
        Entdeckt kausale Struktur.

        Verwendet:
        1. Korrelation (Co-Occurrence)
        2. Zeitliche Reihenfolge (Ursache vor Wirkung)
        3. Asymmetrie (A→B öfter als B→A)
        """
        variables = set()
        for (a, b) in self.co_occurrences.keys():
            variables.add(a)
            variables.add(b)

        edges = []

        for (a, b), count in self.co_occurrences.items():
            if count < min_observations:
                continue

            # Prüfe zeitliche Reihenfolge
            a_before_b = self.temporal_order.get((a, b), 0)
            b_before_a = self.temporal_order.get((b, a), 0)

            # Bestimme Richtung
            if a_before_b > b_before_a * 1.5:
                # A verursacht wahrscheinlich B
                strength = count / max(1, count + self.co_occurrences.get((a, a), 1))
                edges.append((a, b, min(1.0, strength), "temporal"))
            elif b_before_a > a_before_b * 1.5:
                # B verursacht wahrscheinlich A
                strength = count / max(1, count + self.co_occurrences.get((b, b), 1))
                edges.append((b, a, min(1.0, strength), "temporal"))
            else:
                # Richtung unklar - möglicherweise gemeinsame Ursache
                edges.append((a, b, 0.3, "undirected"))

        self.discovered_edges = [(a, b, s) for a, b, s, _ in edges]

        return {
            "variables": list(variables),
            "edges": edges,
            "total_observations": sum(self.co_occurrences.values()),
            "structure_type": self._classify_structure(edges)
        }

    def _classify_structure(self, edges: List[Tuple]) -> str:
        """Klassifiziert die entdeckte Struktur"""
        if not edges:
            return "empty"

        directed = sum(1 for e in edges if e[3] == "temporal")
        undirected = len(edges) - directed

        if directed > undirected * 2:
            return "mostly_causal"
        elif undirected > directed * 2:
            return "mostly_correlational"
        else:
            return "mixed"

    def get_likely_causes(self, effect: str, min_strength: float = 0.3) -> List[Tuple[str, float]]:
        """Findet wahrscheinliche Ursachen für einen Effekt"""
        causes = []
        for (cause, eff, strength) in self.discovered_edges:
            if eff == effect and strength >= min_strength:
                causes.append((cause, strength))

        causes.sort(key=lambda x: x[1], reverse=True)
        return causes

    def get_likely_effects(self, cause: str, min_strength: float = 0.3) -> List[Tuple[str, float]]:
        """Findet wahrscheinliche Effekte einer Ursache"""
        effects = []
        for (c, effect, strength) in self.discovered_edges:
            if c == cause and strength >= min_strength:
                effects.append((effect, strength))

        effects.sort(key=lambda x: x[1], reverse=True)
        return effects


class ConfoundingDetector:
    """
    Erkennt konfundierende Variablen (Scheinkausalitäten).

    Wenn A und B korrelieren, aber C sowohl A als auch B verursacht,
    ist die A-B Korrelation eine Scheinkausalität.
    """

    def __init__(self):
        # Bekannte Variablen-Beziehungen
        self.causal_graph: Dict[str, List[str]] = defaultdict(list)  # cause -> [effects]
        self.correlation_pairs: Set[Tuple[str, str]] = set()

    def add_causal_link(self, cause: str, effect: str):
        """Fügt bekannte kausale Beziehung hinzu"""
        self.causal_graph[cause].append(effect)

    def add_correlation(self, var_a: str, var_b: str):
        """Fügt beobachtete Korrelation hinzu"""
        pair = (min(var_a, var_b), max(var_a, var_b))
        self.correlation_pairs.add(pair)

    def find_confounders(self, var_a: str, var_b: str) -> List[Dict]:
        """
        Sucht mögliche Confounder für eine Korrelation.

        Ein Confounder C verursacht sowohl A als auch B.
        """
        confounders = []

        for potential_confounder, effects in self.causal_graph.items():
            if var_a in effects and var_b in effects:
                confounders.append({
                    "confounder": potential_confounder,
                    "explanation": f"'{potential_confounder}' verursacht sowohl '{var_a}' als auch '{var_b}'",
                    "spurious_correlation": True
                })

        return confounders

    def is_spurious(self, var_a: str, var_b: str) -> Tuple[bool, List[str]]:
        """
        Prüft ob Korrelation zwischen A und B eine Scheinkorrelation ist.

        Returns (is_spurious, list_of_confounders)
        """
        confounders = self.find_confounders(var_a, var_b)
        confounder_names = [c["confounder"] for c in confounders]
        return len(confounders) > 0, confounder_names

    def suggest_controls(self, var_a: str, var_b: str) -> List[str]:
        """
        Schlägt Variablen vor, die kontrolliert werden sollten.

        Um kausale Effekte von A auf B zu messen.
        """
        is_spurious, confounders = self.is_spurious(var_a, var_b)

        if is_spurious:
            return confounders
        else:
            # Suche nach möglichen Mediatoren
            mediators = []
            for c, effects in self.causal_graph.items():
                if c == var_a and var_b in effects:
                    # Direkter Effekt - keine Kontrolle nötig
                    continue
                if c == var_a:
                    for eff in effects:
                        if var_b in self.causal_graph.get(eff, []):
                            mediators.append(eff)

            return mediators


class CausalStrengthEstimator:
    """
    Quantifiziert kausale Stärke präzise.

    Verwendet mehrere Metriken:
    - Average Treatment Effect (ATE)
    - Conditional Average Treatment Effect (CATE)
    - Probability of Necessity (PN)
    - Probability of Sufficiency (PS)
    """

    def __init__(self):
        # Beobachtungen: (treatment, outcome, covariates)
        self.observations: List[Tuple[bool, float, Dict]] = []
        self.treatment_outcomes: Dict[bool, List[float]] = {True: [], False: []}

    def observe(self, treatment: bool, outcome: float, covariates: Dict = None):
        """Registriert eine Beobachtung"""
        self.observations.append((treatment, outcome, covariates or {}))
        self.treatment_outcomes[treatment].append(outcome)

    def calculate_ate(self) -> Dict[str, float]:
        """
        Average Treatment Effect.

        ATE = E[Y | do(T=1)] - E[Y | do(T=0)]
        """
        treated = self.treatment_outcomes[True]
        untreated = self.treatment_outcomes[False]

        if not treated or not untreated:
            return {"ate": 0.0, "confidence": 0.0, "error": "Insufficient data"}

        mean_treated = sum(treated) / len(treated)
        mean_untreated = sum(untreated) / len(untreated)

        ate = mean_treated - mean_untreated

        # Konfidenz basierend auf Stichprobengröße
        n = min(len(treated), len(untreated))
        confidence = min(1.0, n / 30)  # Bei 30+ Beobachtungen hohe Konfidenz

        return {
            "ate": ate,
            "mean_treated": mean_treated,
            "mean_untreated": mean_untreated,
            "n_treated": len(treated),
            "n_untreated": len(untreated),
            "confidence": confidence,
            "interpretation": self._interpret_ate(ate)
        }

    def _interpret_ate(self, ate: float) -> str:
        """Interpretiert ATE-Wert"""
        if ate > 0.5:
            return "Starker positiver Kausaleffekt"
        elif ate > 0.2:
            return "Moderater positiver Kausaleffekt"
        elif ate > 0:
            return "Schwacher positiver Kausaleffekt"
        elif ate > -0.2:
            return "Schwacher negativer Kausaleffekt"
        elif ate > -0.5:
            return "Moderater negativer Kausaleffekt"
        else:
            return "Starker negativer Kausaleffekt"

    def calculate_necessity(self, threshold: float = 0.5) -> float:
        """
        Probability of Necessity (PN).

        Wie wahrscheinlich ist es, dass Y nicht eingetreten wäre,
        wenn X nicht stattgefunden hätte?
        """
        treated = self.treatment_outcomes[True]
        untreated = self.treatment_outcomes[False]

        if not treated or not untreated:
            return 0.0

        # Anteil der Treated mit positivem Outcome
        treated_positive = sum(1 for y in treated if y > threshold) / len(treated)
        # Anteil der Untreated mit positivem Outcome
        untreated_positive = sum(1 for y in untreated if y > threshold) / len(untreated)

        if treated_positive == 0:
            return 0.0

        # PN = (P(Y=1|T=1) - P(Y=1|T=0)) / P(Y=1|T=1)
        pn = (treated_positive - untreated_positive) / treated_positive
        return max(0.0, min(1.0, pn))

    def calculate_sufficiency(self, threshold: float = 0.5) -> float:
        """
        Probability of Sufficiency (PS).

        Wie wahrscheinlich ist es, dass Y eingetreten wäre,
        wenn X stattgefunden hätte?
        """
        treated = self.treatment_outcomes[True]
        untreated = self.treatment_outcomes[False]

        if not treated or not untreated:
            return 0.0

        treated_positive = sum(1 for y in treated if y > threshold) / len(treated)
        untreated_negative = sum(1 for y in untreated if y <= threshold) / len(untreated)

        if untreated_negative == 0:
            return 0.0

        # PS = (P(Y=1|T=1) - P(Y=1|T=0)) / P(Y=0|T=0)
        untreated_positive = 1 - untreated_negative
        ps = (treated_positive - untreated_positive) / untreated_negative
        return max(0.0, min(1.0, ps))

    def full_analysis(self) -> Dict[str, Any]:
        """Vollständige Kausalanalyse"""
        ate = self.calculate_ate()
        pn = self.calculate_necessity()
        ps = self.calculate_sufficiency()

        return {
            "average_treatment_effect": ate,
            "probability_of_necessity": pn,
            "probability_of_sufficiency": ps,
            "causal_type": self._determine_causal_type(pn, ps),
            "total_observations": len(self.observations)
        }

    def _determine_causal_type(self, pn: float, ps: float) -> str:
        """Bestimmt Art der Kausalbeziehung"""
        if pn > 0.7 and ps > 0.7:
            return "necessary_and_sufficient"
        elif pn > 0.7:
            return "necessary_but_not_sufficient"
        elif ps > 0.7:
            return "sufficient_but_not_necessary"
        elif pn > 0.3 or ps > 0.3:
            return "contributing_factor"
        else:
            return "weak_or_no_causation"


class TemporalCausality:
    """
    Zeitbasierte Kausalitätsanalyse.

    Verwendet Granger-ähnliche Kausalität:
    X verursacht Y, wenn vergangene X-Werte Y besser vorhersagen
    als vergangene Y-Werte allein.
    """

    def __init__(self, max_lag: int = 5):
        self.max_lag = max_lag
        # Zeitreihen pro Variable
        self.time_series: Dict[str, List[Tuple[float, float]]] = defaultdict(list)

    def record(self, variable: str, value: float, timestamp: float = None):
        """Zeichnet Wert mit Zeitstempel auf"""
        if timestamp is None:
            timestamp = time.time()
        self.time_series[variable].append((timestamp, value))

        # Behalte nur letzte 1000 Einträge
        if len(self.time_series[variable]) > 1000:
            self.time_series[variable] = self.time_series[variable][-1000:]

    def test_granger_causality(self, cause: str, effect: str) -> Dict[str, Any]:
        """
        Testet ob 'cause' Granger-kausal für 'effect' ist.

        Vereinfachte Version für Pi4.
        """
        cause_series = self.time_series.get(cause, [])
        effect_series = self.time_series.get(effect, [])

        if len(cause_series) < 10 or len(effect_series) < 10:
            return {"is_causal": False, "error": "Insufficient data", "confidence": 0.0}

        # Synchronisiere Zeitreihen
        cause_values = [v for _, v in sorted(cause_series)[-100:]]
        effect_values = [v for _, v in sorted(effect_series)[-100:]]

        min_len = min(len(cause_values), len(effect_values))
        cause_values = cause_values[:min_len]
        effect_values = effect_values[:min_len]

        if min_len < 10:
            return {"is_causal": False, "error": "Series too short", "confidence": 0.0}

        # Berechne Korrelation mit verschiedenen Lags
        best_lag = 0
        best_correlation = 0

        for lag in range(1, min(self.max_lag + 1, min_len // 2)):
            # Korrelation zwischen cause[t-lag] und effect[t]
            cause_lagged = cause_values[:-lag]
            effect_current = effect_values[lag:]

            correlation = self._pearson_correlation(cause_lagged, effect_current)

            if abs(correlation) > abs(best_correlation):
                best_correlation = correlation
                best_lag = lag

        # Prüfe ob Kausalität wahrscheinlich
        # (cause sollte effect besser vorhersagen als effect selbst)
        auto_correlation = self._pearson_correlation(effect_values[:-1], effect_values[1:])

        is_causal = abs(best_correlation) > abs(auto_correlation) * 1.2 and abs(best_correlation) > 0.3

        return {
            "is_causal": is_causal,
            "best_lag": best_lag,
            "correlation_at_lag": best_correlation,
            "auto_correlation": auto_correlation,
            "confidence": abs(best_correlation) if is_causal else 0.0,
            "interpretation": f"'{cause}' beeinflusst '{effect}' mit Verzögerung von {best_lag} Zeiteinheiten"
                             if is_causal else f"Keine klare Kausalität gefunden"
        }

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Berechnet Pearson-Korrelation ohne numpy"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
        denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5

        if denom_x == 0 or denom_y == 0:
            return 0.0

        return numerator / (denom_x * denom_y)

    def find_leading_indicators(self, target: str, candidates: List[str]) -> List[Dict]:
        """Findet Variablen die target zeitlich vorhersagen"""
        results = []

        for candidate in candidates:
            if candidate == target:
                continue

            test = self.test_granger_causality(candidate, target)
            if test.get("is_causal"):
                results.append({
                    "indicator": candidate,
                    "lag": test["best_lag"],
                    "strength": test["correlation_at_lag"],
                    "confidence": test["confidence"]
                })

        results.sort(key=lambda x: x["strength"], reverse=True)
        return results


class CausalChainValidator:
    """
    Validiert kausale Ketten auf logische Konsistenz.

    Prüft:
    - Keine Zyklen (A→B→C→A ist ungültig)
    - Transitivität (A→B und B→C impliziert A→C)
    - Keine Widersprüche
    """

    def __init__(self):
        self.edges: List[Tuple[str, str, float]] = []  # (cause, effect, strength)
        self.nodes: Set[str] = set()

    def add_causal_link(self, cause: str, effect: str, strength: float = 1.0):
        """Fügt kausale Verbindung hinzu"""
        self.edges.append((cause, effect, strength))
        self.nodes.add(cause)
        self.nodes.add(effect)

    def validate(self) -> Dict[str, Any]:
        """Validiert die gesamte kausale Struktur"""
        issues = []

        # 1. Prüfe auf Zyklen
        cycles = self._find_cycles()
        if cycles:
            issues.append({
                "type": "cycle",
                "description": "Kausale Zyklen gefunden",
                "details": cycles
            })

        # 2. Prüfe auf Widersprüche (A→B und A→¬B)
        contradictions = self._find_contradictions()
        if contradictions:
            issues.append({
                "type": "contradiction",
                "description": "Widersprüchliche Kausalbeziehungen",
                "details": contradictions
            })

        # 3. Berechne transitive Closure
        transitive = self._compute_transitive_closure()

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "nodes": list(self.nodes),
            "direct_edges": len(self.edges),
            "transitive_edges": len(transitive),
            "transitive_closure": transitive
        }

    def _find_cycles(self) -> List[List[str]]:
        """Findet alle Zyklen im Graphen (DFS)"""
        cycles = []

        # Baue Adjazenzliste
        adj: Dict[str, List[str]] = defaultdict(list)
        for cause, effect, _ in self.edges:
            adj[cause].append(effect)

        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Zyklus gefunden
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.remove(node)

        for node in self.nodes:
            if node not in visited:
                dfs(node)

        return cycles

    def _find_contradictions(self) -> List[Dict]:
        """Findet widersprüchliche Beziehungen"""
        # Vereinfachte Implementierung: Prüfe auf entgegengesetzte Kanten
        contradictions = []

        edge_set = {(c, e) for c, e, _ in self.edges}

        for cause, effect, strength in self.edges:
            # Prüfe ob umgekehrte Kante existiert (potentieller Widerspruch)
            if (effect, cause) in edge_set:
                contradictions.append({
                    "type": "bidirectional",
                    "vars": [cause, effect],
                    "explanation": f"Beide Richtungen: {cause}→{effect} und {effect}→{cause}"
                })

        return contradictions

    def _compute_transitive_closure(self) -> List[Tuple[str, str, float]]:
        """Berechnet transitive Hülle (alle implizierten Kausalitäten)"""
        # Floyd-Warshall für transitive Closure mit Stärken
        dist: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(lambda: 0.0))

        for cause, effect, strength in self.edges:
            dist[cause][effect] = max(dist[cause][effect], strength)

        nodes_list = list(self.nodes)

        for k in nodes_list:
            for i in nodes_list:
                for j in nodes_list:
                    if i != j and i != k and j != k:
                        # Transitive Stärke = Produkt der Teilstärken
                        transitive_strength = dist[i][k] * dist[k][j]
                        if transitive_strength > dist[i][j]:
                            dist[i][j] = transitive_strength

        transitive = []
        for i in nodes_list:
            for j in nodes_list:
                if i != j and dist[i][j] > 0:
                    transitive.append((i, j, dist[i][j]))

        return transitive

    def get_causal_path(self, start: str, end: str) -> Optional[List[str]]:
        """Findet kausalen Pfad von start zu end"""
        adj: Dict[str, List[str]] = defaultdict(list)
        for cause, effect, _ in self.edges:
            adj[cause].append(effect)

        # BFS für kürzesten Pfad
        from collections import deque
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            node, path = queue.popleft()
            if node == end:
                return path

            for neighbor in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None


class CausalIntegrator:
    """
    Integriert alle Kausalitäts-Komponenten.

    Zentraler Hub für:
    - Interventionales Reasoning
    - Kausale Entdeckung
    - Confounder-Detektion
    - Stärke-Schätzung
    - Temporale Kausalität
    - Ketten-Validierung
    """

    def __init__(self):
        self.interventional = InterventionalReasoning()
        self.discovery = CausalDiscovery()
        self.confounding = ConfoundingDetector()
        self.strength = CausalStrengthEstimator()
        self.temporal = TemporalCausality()
        self.validator = CausalChainValidator()

        # Cache für Analysen
        self._analysis_cache: Dict[str, Any] = {}

    def record_observation(self, event: str, context: Dict[str, Any],
                          outcome: float = None, timestamp: float = None):
        """Zeichnet Beobachtung für alle Systeme auf"""
        if timestamp is None:
            timestamp = time.time()

        # Temporal
        self.temporal.record(event, outcome or 1.0, timestamp)

        # Discovery
        context_events = list(context.keys())
        self.discovery.observe_event(event, context_events, timestamp)

        # Korrelationen für Confounding
        for ctx_event in context_events:
            self.interventional.observe(ctx_event, event, context.get(ctx_event, 0.5))
            self.confounding.add_correlation(ctx_event, event)

    def record_intervention(self, action: str, outcome: str,
                           effect_strength: float, was_successful: bool):
        """Zeichnet Intervention auf"""
        self.interventional.intervene(action, outcome, effect_strength)
        self.strength.observe(True, effect_strength)

        # Für Validator
        if was_successful:
            self.validator.add_causal_link(action, outcome, effect_strength)
            self.confounding.add_causal_link(action, outcome)

    def analyze_causality(self, cause: str, effect: str) -> Dict[str, Any]:
        """Vollständige Kausalanalyse zwischen zwei Variablen"""
        cache_key = f"{cause}:{effect}"
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]

        analysis = {
            "cause": cause,
            "effect": effect,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Interventionales Reasoning
        intervention = self.interventional.estimate_do_effect(cause, effect)
        analysis["interventional"] = intervention

        # 2. Confounder Check
        is_spurious, confounders = self.confounding.is_spurious(cause, effect)
        analysis["confounding"] = {
            "is_spurious": is_spurious,
            "confounders": confounders
        }

        # 3. Temporale Analyse
        temporal = self.temporal.test_granger_causality(cause, effect)
        analysis["temporal"] = temporal

        # 4. Stärke-Analyse
        strength = self.strength.full_analysis()
        analysis["strength"] = strength

        # 5. Gesamtbewertung
        causal_score = 0.0
        confidence = 0.0

        if intervention["is_causal"]:
            causal_score += 0.4 * intervention["causal_effect"]
            confidence += 0.3

        if not is_spurious:
            causal_score += 0.2
            confidence += 0.2

        if temporal.get("is_causal"):
            causal_score += 0.3 * temporal.get("confidence", 0)
            confidence += 0.3

        if strength["average_treatment_effect"].get("confidence", 0) > 0.5:
            causal_score += 0.1 * abs(strength["average_treatment_effect"]["ate"])
            confidence += 0.2

        analysis["overall"] = {
            "causal_score": min(1.0, causal_score),
            "confidence": min(1.0, confidence),
            "is_likely_causal": causal_score > 0.5 and not is_spurious,
            "relationship_type": self._classify_relationship(
                causal_score, is_spurious, temporal.get("is_causal", False)
            )
        }

        self._analysis_cache[cache_key] = analysis
        return analysis

    def _classify_relationship(self, score: float, is_spurious: bool,
                              is_temporal: bool) -> str:
        """Klassifiziert die Beziehung"""
        if is_spurious:
            return "spurious_correlation"
        elif score > 0.7 and is_temporal:
            return "strong_causation"
        elif score > 0.4:
            return "probable_causation"
        elif score > 0.2:
            return "possible_causation"
        else:
            return "no_clear_causation"

    def get_causal_graph(self) -> Dict[str, Any]:
        """Gibt den gesamten kausalen Graphen zurück"""
        validation = self.validator.validate()
        discovery = self.discovery.discover_structure()

        return {
            "validation": validation,
            "discovered_structure": discovery,
            "interventions_recorded": len(self.interventional.intervention_effects),
            "confounders_known": len(self.confounding.known_confounders),
            "temporal_series": len(self.temporal.time_series)
        }


# ============================================================================
# ALIASE FÜR RÜCKWÄRTSKOMPATIBILITÄT
# ============================================================================

# holo_brain.py erwartet diesen Namen
CounterfactualReasoner = CounterfactualReasoningEngine


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "ReasoningType",
    "CounterfactualType",
    "CausalRelationType",
    "ExplanationQuality",

    # Dataclasses
    "Observation",
    "Hypothesis",
    "CounterfactualScenario",
    "CausalLink",
    "AbductiveExplanation",
    "CausalModel",

    # Classes
    "EventAnalyzer",
    "CounterfactualReasoningEngine",
    "CounterfactualReasoner",  # Alias

    # Advanced Causality v2.0
    "InterventionalReasoning",
    "CausalDiscovery",
    "ConfoundingDetector",
    "CausalStrengthEstimator",
    "TemporalCausality",
    "CausalChainValidator",
    "CausalIntegrator",

    # Helper functions
    "quick_counterfactual",
    "find_best_explanation",
    "analyze_what_if"
]
