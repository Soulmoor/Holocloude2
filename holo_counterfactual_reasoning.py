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
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from enum import Enum
from datetime import datetime
import random
import logging

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

    # Helper functions
    "quick_counterfactual",
    "find_best_explanation",
    "analyze_what_if"
]
