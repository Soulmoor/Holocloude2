#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO ADVANCED REASONING - Erweiterte Reasoning-Modi                         ║
║                                                                              ║
║  Implementiert fortgeschrittene Denkmuster:                                  ║
║                                                                              ║
║  1. BAYESIAN REASONING    → Probabilistisches Denken mit Prior-Updates      ║
║  2. CAUSAL REASONING      → Kausalität verstehen und modellieren            ║
║  3. METACOGNITIVE         → Denken über das eigene Denken                   ║
║  4. DIALECTICAL           → These-Antithese-Synthese Prozesse               ║
║                                                                              ║
║  Diese Modi ermöglichen tieferes, nuancierteres Denken.                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Autor: Holocloude System
Version: 1.0
"""

import math
import random
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from enum import Enum, auto
from datetime import datetime
from collections import defaultdict
from abc import ABC, abstractmethod

logger = logging.getLogger("HoloAdvancedReasoning")


# =============================================================================
# ENUMS
# =============================================================================

class ReasoningMode(Enum):
    """Verfügbare Reasoning-Modi"""
    BAYESIAN = "bayesian"
    CAUSAL = "causal"
    METACOGNITIVE = "metacognitive"
    DIALECTICAL = "dialectical"
    COMBINED = "combined"  # Alle Modi zusammen


class EvidenceType(Enum):
    """Typen von Evidenz"""
    STRONG_SUPPORT = "strong_support"
    WEAK_SUPPORT = "weak_support"
    NEUTRAL = "neutral"
    WEAK_AGAINST = "weak_against"
    STRONG_AGAINST = "strong_against"


class CausalStrength(Enum):
    """Stärke kausaler Beziehungen"""
    DETERMINISTIC = 1.0      # Immer wenn A, dann B
    STRONG = 0.8             # Meist wenn A, dann B
    MODERATE = 0.5           # Manchmal wenn A, dann B
    WEAK = 0.2               # Selten wenn A, dann B
    NEGLIGIBLE = 0.05        # Fast nie Zusammenhang


class MetacognitiveLevel(Enum):
    """Ebenen der Metakognition"""
    MONITORING = "monitoring"      # Beobachten des eigenen Denkens
    EVALUATION = "evaluation"      # Bewerten des Denkprozesses
    REGULATION = "regulation"      # Anpassen der Denkstrategie
    REFLECTION = "reflection"      # Tiefe Reflexion über Erkenntnisse


class DialecticalPhase(Enum):
    """Phasen des dialektischen Prozesses"""
    THESIS = "thesis"
    ANTITHESIS = "antithesis"
    SYNTHESIS = "synthesis"
    META_SYNTHESIS = "meta_synthesis"  # Synthese höherer Ordnung


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class Belief:
    """Eine Überzeugung mit Wahrscheinlichkeit"""
    content: str
    prior_probability: float  # P(H) - Vorherige Wahrscheinlichkeit
    likelihood: float = 0.5   # P(E|H) - Wie wahrscheinlich ist Evidenz gegeben H
    posterior: float = 0.5    # P(H|E) - Aktualisierte Wahrscheinlichkeit
    evidence_history: List[Tuple[str, float]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialisiert Posterior als Prior"""
        if self.posterior == 0.5 and self.prior_probability != 0.5:
            self.posterior = self.prior_probability


@dataclass
class CausalNode:
    """Ein Knoten im kausalen Graphen"""
    name: str
    description: str
    is_observable: bool = True
    state: Optional[Any] = None
    probability: float = 0.5
    interventions: List[str] = field(default_factory=list)


@dataclass
class CausalEdge:
    """Eine Kante im kausalen Graphen"""
    cause: str
    effect: str
    strength: CausalStrength = CausalStrength.MODERATE
    mechanism: str = ""  # Wie genau wirkt die Kausalität?
    confounders: List[str] = field(default_factory=list)
    is_direct: bool = True


@dataclass
class ThinkingTrace:
    """Aufzeichnung eines Denkprozesses für Metakognition"""
    step_id: int
    reasoning_mode: ReasoningMode
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    confidence: float
    duration_ms: float
    notes: List[str] = field(default_factory=list)
    errors_detected: List[str] = field(default_factory=list)


@dataclass
class DialecticalPosition:
    """Eine Position im dialektischen Prozess"""
    phase: DialecticalPhase
    content: str
    arguments: List[str]
    counterarguments: List[str] = field(default_factory=list)
    strength: float = 0.5
    sources: List[str] = field(default_factory=list)


# =============================================================================
# 1. BAYESIAN REASONING - Probabilistisches Denken
# =============================================================================

class BayesianReasoner:
    """
    Bayesianisches Reasoning mit Prior-Updates.

    Implementiert:
    - Bayes' Theorem: P(H|E) = P(E|H) * P(H) / P(E)
    - Belief Networks
    - Evidenz-Updates
    - Konfidenz-Kalibrierung
    """

    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
        self.evidence_pool: List[Dict] = []
        self.calibration_history: List[Tuple[float, bool]] = []

    def add_belief(self, name: str, content: str, prior: float = 0.5) -> Belief:
        """Fügt eine neue Überzeugung hinzu"""
        belief = Belief(
            content=content,
            prior_probability=max(0.001, min(0.999, prior)),  # Vermeidet 0 und 1
            posterior=max(0.001, min(0.999, prior))
        )
        self.beliefs[name] = belief
        logger.debug(f"Neue Überzeugung: {name} mit Prior {prior:.3f}")
        return belief

    def update_belief(self, belief_name: str, evidence: str,
                      likelihood_if_true: float, likelihood_if_false: float) -> Optional[Belief]:
        """
        Aktualisiert eine Überzeugung mit neuer Evidenz.

        Bayes' Theorem:
        P(H|E) = P(E|H) * P(H) / [P(E|H) * P(H) + P(E|¬H) * P(¬H)]
        """
        if belief_name not in self.beliefs:
            logger.warning(f"Überzeugung '{belief_name}' nicht gefunden")
            return None

        belief = self.beliefs[belief_name]

        # Bayes Update
        p_h = belief.posterior  # Aktuelle Überzeugung als neuer Prior
        p_not_h = 1 - p_h

        p_e_given_h = max(0.001, min(0.999, likelihood_if_true))
        p_e_given_not_h = max(0.001, min(0.999, likelihood_if_false))

        # P(E) = P(E|H) * P(H) + P(E|¬H) * P(¬H)
        p_e = p_e_given_h * p_h + p_e_given_not_h * p_not_h

        # P(H|E) = P(E|H) * P(H) / P(E)
        posterior = (p_e_given_h * p_h) / p_e if p_e > 0 else p_h

        # Clipping für numerische Stabilität
        belief.posterior = max(0.001, min(0.999, posterior))
        belief.evidence_history.append((evidence, belief.posterior))
        belief.last_updated = datetime.now()

        logger.info(f"Belief Update: {belief_name} {p_h:.3f} → {belief.posterior:.3f}")
        return belief

    def compute_likelihood_ratio(self, belief_name: str,
                                  new_evidence: str,
                                  evidence_type: EvidenceType) -> float:
        """
        Berechnet das Likelihood Ratio für Evidenz.

        LR = P(E|H) / P(E|¬H)
        LR > 1: Evidenz unterstützt Hypothese
        LR < 1: Evidenz spricht gegen Hypothese
        """
        evidence_ratios = {
            EvidenceType.STRONG_SUPPORT: 10.0,
            EvidenceType.WEAK_SUPPORT: 2.0,
            EvidenceType.NEUTRAL: 1.0,
            EvidenceType.WEAK_AGAINST: 0.5,
            EvidenceType.STRONG_AGAINST: 0.1,
        }
        return evidence_ratios.get(evidence_type, 1.0)

    def get_confidence_level(self, belief_name: str) -> str:
        """Interpretiert die Konfidenz in natürlicher Sprache"""
        if belief_name not in self.beliefs:
            return "unbekannt"

        p = self.beliefs[belief_name].posterior

        if p >= 0.95:
            return "praktisch sicher"
        elif p >= 0.85:
            return "sehr wahrscheinlich"
        elif p >= 0.70:
            return "wahrscheinlich"
        elif p >= 0.55:
            return "eher wahrscheinlich"
        elif p >= 0.45:
            return "unsicher"
        elif p >= 0.30:
            return "eher unwahrscheinlich"
        elif p >= 0.15:
            return "unwahrscheinlich"
        elif p >= 0.05:
            return "sehr unwahrscheinlich"
        else:
            return "praktisch ausgeschlossen"

    def compute_joint_probability(self, belief_names: List[str],
                                   assuming_independent: bool = True) -> float:
        """
        Berechnet gemeinsame Wahrscheinlichkeit mehrerer Überzeugungen.
        P(A ∧ B) = P(A) * P(B) wenn unabhängig
        """
        if not belief_names:
            return 0.0

        probabilities = [
            self.beliefs[name].posterior
            for name in belief_names
            if name in self.beliefs
        ]

        if not probabilities:
            return 0.0

        if assuming_independent:
            result = 1.0
            for p in probabilities:
                result *= p
            return result
        else:
            # Für abhängige Ereignisse: Konservative Schätzung
            return min(probabilities)

    def entropy(self, belief_name: str) -> float:
        """
        Berechnet die Entropie (Unsicherheit) einer Überzeugung.
        H = -p*log(p) - (1-p)*log(1-p)
        """
        if belief_name not in self.beliefs:
            return 1.0  # Maximale Unsicherheit

        p = self.beliefs[belief_name].posterior

        if p <= 0.001 or p >= 0.999:
            return 0.0  # Keine Unsicherheit

        return -p * math.log2(p) - (1-p) * math.log2(1-p)

    def most_uncertain_beliefs(self, n: int = 5) -> List[Tuple[str, float]]:
        """Findet die unsichersten Überzeugungen (höchste Entropie)"""
        uncertainties = [
            (name, self.entropy(name))
            for name in self.beliefs
        ]
        return sorted(uncertainties, key=lambda x: x[1], reverse=True)[:n]

    def calibrate(self, predicted_probability: float, actual_outcome: bool):
        """
        Kalibriert den Reasoner basierend auf tatsächlichen Ergebnissen.
        Hilft bei der Über-/Unterkonfidenz-Korrektur.
        """
        self.calibration_history.append((predicted_probability, actual_outcome))

    def get_calibration_score(self) -> float:
        """
        Berechnet den Kalibrierungs-Score (Brier Score).
        0 = perfekt kalibriert, 1 = komplett falsch
        """
        if not self.calibration_history:
            return 0.5

        total = 0.0
        for predicted, actual in self.calibration_history:
            outcome = 1.0 if actual else 0.0
            total += (predicted - outcome) ** 2

        return total / len(self.calibration_history)


# =============================================================================
# 2. CAUSAL REASONING - Kausalität verstehen
# =============================================================================

class CausalReasoner:
    """
    Kausales Reasoning mit Kausalmodellen.

    Implementiert:
    - Kausale Graphen (DAGs)
    - Interventionen (do-Operator)
    - Kontrafaktische Fragen
    - Confounder-Erkennung
    """

    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.edges: List[CausalEdge] = []
        self.observations: List[Dict] = []

    def add_variable(self, name: str, description: str,
                      is_observable: bool = True) -> CausalNode:
        """Fügt eine Variable zum kausalen Modell hinzu"""
        node = CausalNode(
            name=name,
            description=description,
            is_observable=is_observable
        )
        self.nodes[name] = node
        return node

    def add_causal_link(self, cause: str, effect: str,
                         strength: CausalStrength = CausalStrength.MODERATE,
                         mechanism: str = "") -> Optional[CausalEdge]:
        """Fügt eine kausale Beziehung hinzu"""
        if cause not in self.nodes or effect not in self.nodes:
            logger.warning(f"Knoten nicht gefunden: {cause} oder {effect}")
            return None

        # Prüfe auf Zyklen (einfache Version)
        if self._would_create_cycle(cause, effect):
            logger.warning(f"Kausale Beziehung würde Zyklus erzeugen: {cause} → {effect}")
            return None

        edge = CausalEdge(
            cause=cause,
            effect=effect,
            strength=strength,
            mechanism=mechanism
        )
        self.edges.append(edge)
        return edge

    def _would_create_cycle(self, new_cause: str, new_effect: str) -> bool:
        """Prüft ob eine neue Kante einen Zyklus erzeugen würde"""
        visited = set()

        def dfs(node: str) -> bool:
            if node == new_cause:
                return True
            if node in visited:
                return False
            visited.add(node)

            for edge in self.edges:
                if edge.cause == node:
                    if dfs(edge.effect):
                        return True
            return False

        return dfs(new_effect)

    def get_causes(self, effect: str) -> List[Tuple[str, CausalStrength]]:
        """Findet alle direkten Ursachen eines Effekts"""
        causes = []
        for edge in self.edges:
            if edge.effect == effect:
                causes.append((edge.cause, edge.strength))
        return causes

    def get_effects(self, cause: str) -> List[Tuple[str, CausalStrength]]:
        """Findet alle direkten Effekte einer Ursache"""
        effects = []
        for edge in self.edges:
            if edge.cause == cause:
                effects.append((edge.effect, edge.strength))
        return effects

    def trace_causal_chain(self, start: str, end: str,
                            max_depth: int = 10) -> List[List[str]]:
        """
        Findet alle kausalen Pfade zwischen zwei Variablen.
        """
        all_paths = []

        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            if current == target:
                all_paths.append(path[:])
                return

            for edge in self.edges:
                if edge.cause == current and edge.effect not in path:
                    path.append(edge.effect)
                    dfs(edge.effect, target, path, depth + 1)
                    path.pop()

        dfs(start, end, [start], 0)
        return all_paths

    def intervene(self, variable: str, value: Any) -> Dict[str, Any]:
        """
        Simuliert eine Intervention (do-Operator).
        do(X=x): Setzt X auf x und entfernt alle eingehenden Kanten.

        Returns: Erwartete Auswirkungen auf andere Variablen
        """
        if variable not in self.nodes:
            return {}

        effects = {}
        effects[variable] = value

        # Propagiere Effekte durch den Graph
        visited = {variable}
        queue = [variable]

        while queue:
            current = queue.pop(0)
            current_value = effects.get(current, self.nodes[current].state)

            for edge in self.edges:
                if edge.cause == current and edge.effect not in visited:
                    # Berechne erwarteten Effekt basierend auf Stärke
                    effect_strength = edge.strength.value if isinstance(edge.strength, CausalStrength) else edge.strength

                    if current_value is not None:
                        # Vereinfachte Propagation
                        effects[edge.effect] = f"beeinflusst ({effect_strength*100:.0f}%)"

                    visited.add(edge.effect)
                    queue.append(edge.effect)

        return effects

    def find_confounders(self, cause: str, effect: str) -> List[str]:
        """
        Findet gemeinsame Ursachen (Confounder) zwischen zwei Variablen.
        Confounder: Variable die sowohl Ursache als auch Effekt beeinflusst.
        """
        cause_ancestors = self._get_ancestors(cause)
        effect_ancestors = self._get_ancestors(effect)

        # Gemeinsame Vorfahren sind potentielle Confounder
        confounders = cause_ancestors.intersection(effect_ancestors)

        # Filtere: Nur echte Confounder (haben Pfade zu beiden)
        true_confounders = []
        for conf in confounders:
            has_path_to_cause = len(self.trace_causal_chain(conf, cause)) > 0
            has_path_to_effect = len(self.trace_causal_chain(conf, effect)) > 0
            if has_path_to_cause and has_path_to_effect:
                true_confounders.append(conf)

        return true_confounders

    def _get_ancestors(self, node: str) -> Set[str]:
        """Findet alle Vorfahren (indirekte Ursachen) eines Knotens"""
        ancestors = set()

        def dfs(current: str):
            for edge in self.edges:
                if edge.effect == current and edge.cause not in ancestors:
                    ancestors.add(edge.cause)
                    dfs(edge.cause)

        dfs(node)
        return ancestors

    def counterfactual_query(self, observed: Dict[str, Any],
                              intervention: Dict[str, Any],
                              query_variable: str) -> str:
        """
        Beantwortet kontrafaktische Fragen.
        "Gegeben X=x wurde beobachtet, was wäre Y gewesen, wenn wir do(Z=z) gemacht hätten?"
        """
        # Schritt 1: Abduktion - Finde konsistente Hintergrundvariablen
        background = self._abduce_background(observed)

        # Schritt 2: Intervention - Setze Variable
        modified_state = {**background, **intervention}

        # Schritt 3: Prediction - Propagiere durch Graph
        prediction = self.intervene(list(intervention.keys())[0],
                                     list(intervention.values())[0])

        result = prediction.get(query_variable, "unbestimmt")

        return f"Kontrafaktisch: Wenn {intervention}, dann wäre {query_variable} = {result}"

    def _abduce_background(self, observed: Dict[str, Any]) -> Dict[str, Any]:
        """Inferiert Hintergrundvariablen aus Beobachtungen"""
        background = {}

        for var, value in observed.items():
            background[var] = value
            # Inferiere Ursachen
            causes = self.get_causes(var)
            for cause, strength in causes:
                if cause not in observed:
                    # Wahrscheinlichste Ursache gegeben Effekt
                    background[cause] = f"inferiert (basierend auf {var})"

        return background

    def explain_causal_relationship(self, cause: str, effect: str) -> str:
        """Erklärt die kausale Beziehung in natürlicher Sprache"""
        paths = self.trace_causal_chain(cause, effect)

        if not paths:
            confounders = self.find_confounders(cause, effect)
            if confounders:
                return (f"Es gibt keine direkte Kausalität zwischen '{cause}' und '{effect}'. "
                       f"Aber sie teilen gemeinsame Ursachen: {', '.join(confounders)}. "
                       f"Das könnte eine Scheinkorrelation sein!")
            return f"Keine kausale Verbindung zwischen '{cause}' und '{effect}' gefunden."

        explanations = []
        for path in paths:
            chain = " → ".join(path)
            explanations.append(f"  • {chain}")

        return f"Kausale Pfade von '{cause}' zu '{effect}':\n" + "\n".join(explanations)


# =============================================================================
# 3. METACOGNITIVE REASONING - Denken über Denken
# =============================================================================

class MetacognitiveReasoner:
    """
    Metakognition - Denken über das eigene Denken.

    Implementiert:
    - Monitoring: Beobachten des eigenen Denkprozesses
    - Evaluation: Bewerten der Denkqualität
    - Regulation: Anpassen der Denkstrategie
    - Reflection: Tiefe Selbstreflexion
    """

    def __init__(self):
        self.thinking_traces: List[ThinkingTrace] = []
        self.current_confidence: float = 0.5
        self.known_biases: List[str] = []
        self.strategy_performance: Dict[str, List[float]] = defaultdict(list)
        self.reflection_journal: List[Dict] = []

    def start_monitoring(self, reasoning_mode: ReasoningMode,
                          input_state: Dict[str, Any]) -> int:
        """Beginnt die Überwachung eines Denkprozesses"""
        step_id = len(self.thinking_traces)
        trace = ThinkingTrace(
            step_id=step_id,
            reasoning_mode=reasoning_mode,
            input_state=input_state.copy(),
            output_state={},
            confidence=self.current_confidence,
            duration_ms=0.0
        )
        self.thinking_traces.append(trace)
        return step_id

    def end_monitoring(self, step_id: int, output_state: Dict[str, Any],
                        confidence: float, duration_ms: float,
                        notes: List[str] = None):
        """Beendet die Überwachung und speichert Ergebnisse"""
        if step_id < len(self.thinking_traces):
            trace = self.thinking_traces[step_id]
            trace.output_state = output_state.copy()
            trace.confidence = confidence
            trace.duration_ms = duration_ms
            trace.notes = notes or []
            self.current_confidence = confidence

    def detect_cognitive_biases(self, thinking_trace: ThinkingTrace) -> List[str]:
        """
        Erkennt kognitive Verzerrungen im Denkprozess.
        """
        biases_detected = []

        input_data = thinking_trace.input_state
        output_data = thinking_trace.output_state

        # Confirmation Bias: Nur bestätigende Evidenz beachtet?
        if "evidence_considered" in input_data:
            supporting = sum(1 for e in input_data["evidence_considered"]
                           if e.get("supports", False))
            total = len(input_data["evidence_considered"])
            if total > 0 and supporting / total > 0.9:
                biases_detected.append("Bestätigungsfehler (Confirmation Bias): "
                                      "Fast nur unterstützende Evidenz betrachtet")

        # Overconfidence: Zu hohe Sicherheit bei wenig Daten?
        if thinking_trace.confidence > 0.9:
            data_points = len(input_data.get("data", []))
            if data_points < 5:
                biases_detected.append("Überkonfidenz: Hohe Sicherheit trotz weniger Datenpunkte")

        # Anchoring: Erste Information dominiert?
        if "initial_estimate" in input_data and "final_estimate" in output_data:
            initial = input_data["initial_estimate"]
            final = output_data["final_estimate"]
            # Wenn das Ergebnis zu nah am Anfangswert liegt
            if isinstance(initial, (int, float)) and isinstance(final, (int, float)):
                if abs(final - initial) / max(abs(initial), 1) < 0.1:
                    biases_detected.append("Ankereffekt: Ergebnis sehr nah an initialem Schätzwert")

        # Availability Heuristic: Aktuelle Ereignisse übergewichtet?
        if "recent_events" in input_data and "historical_data" in input_data:
            recent_weight = input_data.get("recent_weight", 0)
            if recent_weight > 0.7:
                biases_detected.append("Verfügbarkeitsheuristik: "
                                      "Aktuelle Ereignisse möglicherweise übergewichtet")

        self.known_biases.extend(biases_detected)
        return biases_detected

    def evaluate_reasoning_quality(self) -> Dict[str, Any]:
        """
        Bewertet die Qualität des bisherigen Denkens.
        """
        if not self.thinking_traces:
            return {"quality": "unknown", "score": 0.0}

        total_confidence = sum(t.confidence for t in self.thinking_traces)
        avg_confidence = total_confidence / len(self.thinking_traces)

        total_duration = sum(t.duration_ms for t in self.thinking_traces)
        avg_duration = total_duration / len(self.thinking_traces)

        # Konsistenz prüfen
        confidences = [t.confidence for t in self.thinking_traces]
        confidence_variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)

        # Anzahl erkannter Biases
        bias_count = len(self.known_biases)

        # Gesamtscore
        score = (
            avg_confidence * 0.3 +
            (1 - min(confidence_variance, 1)) * 0.2 +  # Konsistenz
            (1 / (1 + bias_count * 0.1)) * 0.3 +       # Weniger Biases = besser
            min(avg_duration / 1000, 1) * 0.2          # Angemessene Zeit zum Nachdenken
        )

        quality = "excellent" if score > 0.8 else "good" if score > 0.6 else "moderate" if score > 0.4 else "poor"

        return {
            "quality": quality,
            "score": score,
            "avg_confidence": avg_confidence,
            "confidence_variance": confidence_variance,
            "biases_detected": bias_count,
            "total_thinking_steps": len(self.thinking_traces),
            "avg_duration_ms": avg_duration
        }

    def suggest_strategy_change(self) -> Optional[str]:
        """
        Schlägt Änderungen der Denkstrategie vor basierend auf Metakognition.
        """
        evaluation = self.evaluate_reasoning_quality()
        suggestions = []

        if evaluation["score"] < 0.4:
            suggestions.append("Grundlegende Neuausrichtung empfohlen: "
                             "Sammle mehr Informationen bevor du schlussfolgere")

        if evaluation["avg_confidence"] > 0.9:
            suggestions.append("Überprüfe deine Annahmen kritischer - "
                             "sehr hohe Konfidenz kann auf blinde Flecken hindeuten")

        if evaluation["avg_confidence"] < 0.3:
            suggestions.append("Du scheinst sehr unsicher zu sein - "
                             "fokussiere dich auf die stärksten Argumente")

        if evaluation["biases_detected"] > 2:
            suggestions.append(f"Es wurden {evaluation['biases_detected']} kognitive Verzerrungen erkannt. "
                             "Versuche bewusst Gegenargumente zu finden.")

        if evaluation["confidence_variance"] > 0.2:
            suggestions.append("Deine Konfidenz schwankt stark - "
                             "versuche konsistentere Kriterien anzuwenden")

        return " | ".join(suggestions) if suggestions else None

    def deep_reflection(self, topic: str) -> Dict[str, Any]:
        """
        Führt eine tiefe Selbstreflexion über einen Denkprozess durch.
        """
        reflection = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "what_i_know": [],
            "what_i_dont_know": [],
            "assumptions": [],
            "potential_errors": [],
            "confidence_assessment": "",
            "lessons_learned": []
        }

        # Analysiere relevante Traces
        relevant_traces = [t for t in self.thinking_traces
                         if topic.lower() in str(t.input_state).lower()
                         or topic.lower() in str(t.output_state).lower()]

        if relevant_traces:
            # Was weiß ich?
            for trace in relevant_traces:
                if trace.confidence > 0.7:
                    reflection["what_i_know"].append(
                        f"Hohe Konfidenz ({trace.confidence:.2f}) bei {trace.reasoning_mode.value}"
                    )
                elif trace.confidence < 0.4:
                    reflection["what_i_dont_know"].append(
                        f"Niedrige Konfidenz ({trace.confidence:.2f}) bei {trace.reasoning_mode.value}"
                    )

        # Annahmen identifizieren
        reflection["assumptions"] = [
            "Implizite Annahme: Die verfügbaren Daten sind repräsentativ",
            "Implizite Annahme: Meine Kategorisierungen sind angemessen",
            "Implizite Annahme: Der Kontext wurde richtig verstanden"
        ]

        # Potentielle Fehler
        if self.known_biases:
            reflection["potential_errors"] = [
                f"Möglicher Fehler durch {bias}" for bias in self.known_biases[:3]
            ]

        # Konfidenz-Assessment
        eval_result = self.evaluate_reasoning_quality()
        reflection["confidence_assessment"] = (
            f"Gesamtqualität: {eval_result['quality']} "
            f"(Score: {eval_result['score']:.2f})"
        )

        self.reflection_journal.append(reflection)
        return reflection

    def get_thinking_summary(self) -> str:
        """Gibt eine lesbare Zusammenfassung des Denkprozesses"""
        if not self.thinking_traces:
            return "Noch keine Denkprozesse aufgezeichnet."

        summary = ["=== Metakognitive Zusammenfassung ===\n"]

        # Statistiken
        eval_result = self.evaluate_reasoning_quality()
        summary.append(f"Qualität: {eval_result['quality']} ({eval_result['score']:.2f})")
        summary.append(f"Denkschritte: {eval_result['total_thinking_steps']}")
        summary.append(f"Durchschnittliche Konfidenz: {eval_result['avg_confidence']:.2f}")

        # Verwendete Modi
        modes = [t.reasoning_mode.value for t in self.thinking_traces]
        mode_counts = {}
        for m in modes:
            mode_counts[m] = mode_counts.get(m, 0) + 1
        summary.append(f"\nVerwendete Reasoning-Modi: {mode_counts}")

        # Erkannte Biases
        if self.known_biases:
            summary.append(f"\nErkannte kognitive Verzerrungen:")
            for bias in set(self.known_biases):
                summary.append(f"  • {bias}")

        # Strategieempfehlung
        suggestion = self.suggest_strategy_change()
        if suggestion:
            summary.append(f"\nEmpfehlung: {suggestion}")

        return "\n".join(summary)


# =============================================================================
# 4. DIALECTICAL REASONING - These-Antithese-Synthese
# =============================================================================

class DialecticalReasoner:
    """
    Dialektisches Reasoning nach Hegel.

    Prozess:
    1. These: Eine Position aufstellen
    2. Antithese: Die Gegenposition formulieren
    3. Synthese: Wahrheiten aus beiden vereinen
    4. (Optional) Meta-Synthese: Wiederholung auf höherer Ebene
    """

    def __init__(self):
        self.positions: List[DialecticalPosition] = []
        self.synthesis_history: List[Dict] = []
        self.current_phase: DialecticalPhase = DialecticalPhase.THESIS

    def propose_thesis(self, content: str, arguments: List[str],
                        sources: List[str] = None) -> DialecticalPosition:
        """Stellt eine These auf"""
        thesis = DialecticalPosition(
            phase=DialecticalPhase.THESIS,
            content=content,
            arguments=arguments,
            sources=sources or [],
            strength=self._calculate_strength(arguments)
        )
        self.positions.append(thesis)
        self.current_phase = DialecticalPhase.ANTITHESIS
        return thesis

    def propose_antithesis(self, thesis: DialecticalPosition,
                           counter_content: str,
                           counter_arguments: List[str]) -> DialecticalPosition:
        """Formuliert die Antithese zur gegebenen These"""
        antithesis = DialecticalPosition(
            phase=DialecticalPhase.ANTITHESIS,
            content=counter_content,
            arguments=counter_arguments,
            counterarguments=thesis.arguments,  # These-Argumente sind jetzt Gegenargumente
            strength=self._calculate_strength(counter_arguments),
            sources=[]
        )

        # Verlinke These und Antithese
        thesis.counterarguments = counter_arguments

        self.positions.append(antithesis)
        self.current_phase = DialecticalPhase.SYNTHESIS
        return antithesis

    def generate_antithesis_suggestions(self, thesis: DialecticalPosition) -> List[str]:
        """
        Generiert Vorschläge für mögliche Antithesen.
        """
        suggestions = []

        # Negation der Hauptaussage
        suggestions.append(f"Das Gegenteil von '{thesis.content}' könnte wahr sein")

        # Kontext-Abhängigkeit hinterfragen
        suggestions.append(f"'{thesis.content}' gilt nur unter bestimmten Bedingungen")

        # Alternative Perspektiven
        suggestions.append(f"Aus anderer Perspektive betrachtet ist '{thesis.content}' problematisch")

        # Unbeabsichtigte Konsequenzen
        suggestions.append(f"'{thesis.content}' führt zu unerwünschten Nebeneffekten")

        # Für jedes Argument eine Gegenposition
        for arg in thesis.arguments[:3]:
            suggestions.append(f"Gegenargument zu '{arg}': [hier Gegenposition entwickeln]")

        return suggestions

    def synthesize(self, thesis: DialecticalPosition,
                    antithesis: DialecticalPosition) -> DialecticalPosition:
        """
        Erstellt eine Synthese aus These und Antithese.

        Die Synthese behält die Stärken beider Positionen und
        überwindet ihre Schwächen.
        """
        # Identifiziere gemeinsame Elemente
        common_ground = self._find_common_ground(thesis, antithesis)

        # Identifiziere überwindbare Widersprüche
        resolvable = self._find_resolvable_contradictions(thesis, antithesis)

        # Identifiziere bleibende Spannungen
        tensions = self._find_remaining_tensions(thesis, antithesis)

        # Erstelle Synthese-Argumente
        synthesis_arguments = []

        # Gemeinsamer Boden als Fundament
        for common in common_ground:
            synthesis_arguments.append(f"Beide Seiten stimmen überein: {common}")

        # Aufgelöste Widersprüche
        for resolution in resolvable:
            synthesis_arguments.append(f"Auflösung: {resolution}")

        # Anerkannte Spannungen
        for tension in tensions:
            synthesis_arguments.append(f"Produktive Spannung: {tension}")

        # Synthese-Inhalt generieren
        synthesis_content = self._generate_synthesis_content(
            thesis.content,
            antithesis.content,
            common_ground,
            resolvable
        )

        synthesis = DialecticalPosition(
            phase=DialecticalPhase.SYNTHESIS,
            content=synthesis_content,
            arguments=synthesis_arguments,
            strength=(thesis.strength + antithesis.strength) / 2 + 0.1  # Bonus für Synthese
        )

        self.positions.append(synthesis)
        self.synthesis_history.append({
            "thesis": thesis.content,
            "antithesis": antithesis.content,
            "synthesis": synthesis_content,
            "timestamp": datetime.now().isoformat()
        })

        self.current_phase = DialecticalPhase.META_SYNTHESIS
        return synthesis

    def _calculate_strength(self, arguments: List[str]) -> float:
        """Berechnet die Stärke einer Position basierend auf Argumenten"""
        if not arguments:
            return 0.1

        # Mehr Argumente = stärker (mit abnehmenden Erträgen)
        count_score = min(1.0, len(arguments) / 5)

        # Längere, elaborierte Argumente = stärker
        avg_length = sum(len(arg) for arg in arguments) / len(arguments)
        length_score = min(1.0, avg_length / 100)

        return count_score * 0.6 + length_score * 0.4

    def _find_common_ground(self, thesis: DialecticalPosition,
                             antithesis: DialecticalPosition) -> List[str]:
        """Findet Gemeinsamkeiten zwischen These und Antithese"""
        common = []

        # Einfache Wortüberlappung als Heuristik
        thesis_words = set(thesis.content.lower().split())
        antithesis_words = set(antithesis.content.lower().split())

        overlap = thesis_words.intersection(antithesis_words)
        significant_overlap = [w for w in overlap if len(w) > 4]

        if significant_overlap:
            common.append(f"Gemeinsame Konzepte: {', '.join(list(significant_overlap)[:5])}")

        # Implizite Gemeinsamkeiten
        common.append("Beide Positionen anerkennen die Relevanz des Themas")

        return common

    def _find_resolvable_contradictions(self, thesis: DialecticalPosition,
                                         antithesis: DialecticalPosition) -> List[str]:
        """Findet auflösbare Widersprüche"""
        resolutions = []

        # Kontext-basierte Auflösung
        resolutions.append(
            f"These gilt in Kontext A, Antithese in Kontext B"
        )

        # Zeitliche Auflösung
        resolutions.append(
            "Kurzfristig vs. langfristig können unterschiedliche Perspektiven richtig sein"
        )

        # Ebenen-Auflösung
        resolutions.append(
            "Auf individueller Ebene gilt X, auf systemischer Ebene Y"
        )

        return resolutions

    def _find_remaining_tensions(self, thesis: DialecticalPosition,
                                  antithesis: DialecticalPosition) -> List[str]:
        """Findet bleibende, produktive Spannungen"""
        tensions = []

        tensions.append(
            f"Die Spannung zwischen '{thesis.content[:30]}...' und "
            f"'{antithesis.content[:30]}...' bleibt fruchtbar"
        )

        return tensions

    def _generate_synthesis_content(self, thesis_content: str,
                                     antithesis_content: str,
                                     common_ground: List[str],
                                     resolutions: List[str]) -> str:
        """Generiert den Inhalt der Synthese"""
        # Vereinfachte Synthese-Generierung
        synthesis = (
            f"Eine höhere Perspektive, die sowohl '{thesis_content[:50]}...' "
            f"als auch '{antithesis_content[:50]}...' integriert, "
            f"erkennt an, dass beide Wahrheitskerne enthalten. "
        )

        if common_ground:
            synthesis += f"Aufbauend auf {common_ground[0].lower()}, "

        if resolutions:
            synthesis += f"lässt sich der Widerspruch auflösen durch: {resolutions[0]}."

        return synthesis

    def meta_synthesize(self, previous_synthesis: DialecticalPosition,
                         new_challenge: str) -> DialecticalPosition:
        """
        Führt eine Meta-Synthese durch - wendet den dialektischen Prozess
        auf eine bestehende Synthese an.
        """
        # Die vorherige Synthese wird zur neuen These
        meta_thesis = DialecticalPosition(
            phase=DialecticalPhase.THESIS,
            content=previous_synthesis.content,
            arguments=previous_synthesis.arguments,
            strength=previous_synthesis.strength
        )

        # Die neue Herausforderung wird zur Antithese
        meta_antithesis = DialecticalPosition(
            phase=DialecticalPhase.ANTITHESIS,
            content=new_challenge,
            arguments=[f"Herausforderung an die Synthese: {new_challenge}"],
            strength=0.5
        )

        # Neue Synthese auf höherer Ebene
        meta_synthesis = self.synthesize(meta_thesis, meta_antithesis)
        meta_synthesis.phase = DialecticalPhase.META_SYNTHESIS

        return meta_synthesis

    def get_dialectical_summary(self) -> str:
        """Gibt eine Zusammenfassung des dialektischen Prozesses"""
        summary = ["=== Dialektischer Prozess ===\n"]

        for i, pos in enumerate(self.positions):
            summary.append(f"{i+1}. [{pos.phase.value.upper()}]")
            summary.append(f"   {pos.content[:100]}...")
            summary.append(f"   Stärke: {pos.strength:.2f}")
            summary.append(f"   Argumente: {len(pos.arguments)}")
            summary.append("")

        if self.synthesis_history:
            summary.append(f"\nDurchgeführte Synthesen: {len(self.synthesis_history)}")

        return "\n".join(summary)


# =============================================================================
# KOMBINIERTER REASONING-ENGINE
# =============================================================================

class AdvancedReasoningEngine:
    """
    Kombiniert alle vier Reasoning-Modi zu einem integrierten System.
    """

    def __init__(self):
        self.bayesian = BayesianReasoner()
        self.causal = CausalReasoner()
        self.metacognitive = MetacognitiveReasoner()
        self.dialectical = DialecticalReasoner()

        self.active_modes: Set[ReasoningMode] = set()
        self.reasoning_log: List[Dict] = []

    def activate_mode(self, mode: ReasoningMode):
        """Aktiviert einen Reasoning-Modus"""
        self.active_modes.add(mode)
        logger.info(f"Reasoning-Modus aktiviert: {mode.value}")

    def deactivate_mode(self, mode: ReasoningMode):
        """Deaktiviert einen Reasoning-Modus"""
        self.active_modes.discard(mode)
        logger.info(f"Reasoning-Modus deaktiviert: {mode.value}")

    def reason(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Führt Multi-Modal Reasoning durch.

        Args:
            question: Die zu beantwortende Frage
            context: Zusätzlicher Kontext

        Returns:
            Reasoning-Ergebnisse aus allen aktiven Modi
        """
        context = context or {}
        results = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "modes_used": [m.value for m in self.active_modes],
            "results": {}
        }

        start_time = datetime.now()

        # Metakognition: Monitoring starten
        if ReasoningMode.METACOGNITIVE in self.active_modes:
            step_id = self.metacognitive.start_monitoring(
                ReasoningMode.COMBINED,
                {"question": question, "context": context}
            )

        # Bayesianisches Reasoning
        if ReasoningMode.BAYESIAN in self.active_modes:
            results["results"]["bayesian"] = self._apply_bayesian(question, context)

        # Kausales Reasoning
        if ReasoningMode.CAUSAL in self.active_modes:
            results["results"]["causal"] = self._apply_causal(question, context)

        # Dialektisches Reasoning
        if ReasoningMode.DIALECTICAL in self.active_modes:
            results["results"]["dialectical"] = self._apply_dialectical(question, context)

        # Metakognition: Evaluation
        if ReasoningMode.METACOGNITIVE in self.active_modes:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.metacognitive.end_monitoring(
                step_id,
                results,
                confidence=self._calculate_overall_confidence(results),
                duration_ms=duration
            )
            results["results"]["metacognitive"] = self.metacognitive.evaluate_reasoning_quality()

        self.reasoning_log.append(results)
        return results

    def _apply_bayesian(self, question: str, context: Dict) -> Dict:
        """Wendet bayesianisches Reasoning an"""
        # Erstelle Belief aus Frage
        belief_name = f"belief_{len(self.bayesian.beliefs)}"
        self.bayesian.add_belief(
            belief_name,
            question,
            prior=context.get("prior_probability", 0.5)
        )

        # Falls Evidenz im Kontext
        if "evidence" in context:
            for ev in context["evidence"]:
                self.bayesian.update_belief(
                    belief_name,
                    ev.get("description", ""),
                    ev.get("likelihood_if_true", 0.7),
                    ev.get("likelihood_if_false", 0.3)
                )

        return {
            "belief": belief_name,
            "posterior": self.bayesian.beliefs[belief_name].posterior,
            "confidence_level": self.bayesian.get_confidence_level(belief_name),
            "entropy": self.bayesian.entropy(belief_name)
        }

    def _apply_causal(self, question: str, context: Dict) -> Dict:
        """Wendet kausales Reasoning an"""
        results = {
            "causal_analysis": "Kausale Analyse durchgeführt",
            "identified_causes": [],
            "identified_effects": []
        }

        # Falls kausale Variablen im Kontext
        if "causal_variables" in context:
            for var in context["causal_variables"]:
                self.causal.add_variable(
                    var["name"],
                    var.get("description", "")
                )

        if "causal_links" in context:
            for link in context["causal_links"]:
                self.causal.add_causal_link(
                    link["cause"],
                    link["effect"],
                    CausalStrength.MODERATE
                )

        # Analysiere kausale Struktur
        if self.causal.nodes:
            for node in self.causal.nodes:
                causes = self.causal.get_causes(node)
                effects = self.causal.get_effects(node)
                if causes:
                    results["identified_causes"].append({
                        "variable": node,
                        "causes": [(c, s.value) for c, s in causes]
                    })
                if effects:
                    results["identified_effects"].append({
                        "variable": node,
                        "effects": [(e, s.value) for e, s in effects]
                    })

        return results

    def _apply_dialectical(self, question: str, context: Dict) -> Dict:
        """Wendet dialektisches Reasoning an"""
        # Generiere These aus Frage
        thesis = self.dialectical.propose_thesis(
            content=f"Ja, {question}" if "?" in question else question,
            arguments=context.get("thesis_arguments", ["Grundannahme"])
        )

        # Generiere Antithese
        antithesis_suggestions = self.dialectical.generate_antithesis_suggestions(thesis)
        antithesis = self.dialectical.propose_antithesis(
            thesis,
            counter_content=f"Nein, nicht {question}" if "?" in question else f"Gegenteil: {question}",
            counter_arguments=context.get("antithesis_arguments", antithesis_suggestions[:2])
        )

        # Synthese
        synthesis = self.dialectical.synthesize(thesis, antithesis)

        return {
            "thesis": thesis.content,
            "antithesis": antithesis.content,
            "synthesis": synthesis.content,
            "synthesis_strength": synthesis.strength
        }

    def _calculate_overall_confidence(self, results: Dict) -> float:
        """Berechnet Gesamtkonfidenz aus allen Ergebnissen"""
        confidences = []

        if "bayesian" in results.get("results", {}):
            confidences.append(results["results"]["bayesian"].get("posterior", 0.5))

        if "dialectical" in results.get("results", {}):
            confidences.append(results["results"]["dialectical"].get("synthesis_strength", 0.5))

        return sum(confidences) / len(confidences) if confidences else 0.5

    def get_reasoning_summary(self) -> str:
        """Gibt eine Zusammenfassung aller Reasoning-Aktivitäten"""
        summary = ["=" * 60]
        summary.append("ADVANCED REASONING ENGINE - Zusammenfassung")
        summary.append("=" * 60)

        summary.append(f"\nAktive Modi: {[m.value for m in self.active_modes]}")
        summary.append(f"Durchgeführte Reasoning-Schritte: {len(self.reasoning_log)}")

        # Bayesian Summary
        summary.append(f"\n--- Bayesian Reasoner ---")
        summary.append(f"Überzeugungen: {len(self.bayesian.beliefs)}")
        uncertain = self.bayesian.most_uncertain_beliefs(3)
        if uncertain:
            summary.append(f"Unsicherste Beliefs: {uncertain}")

        # Causal Summary
        summary.append(f"\n--- Causal Reasoner ---")
        summary.append(f"Variablen: {len(self.causal.nodes)}")
        summary.append(f"Kausale Links: {len(self.causal.edges)}")

        # Metacognitive Summary
        summary.append(f"\n--- Metacognitive Reasoner ---")
        eval_result = self.metacognitive.evaluate_reasoning_quality()
        summary.append(f"Denkqualität: {eval_result['quality']} ({eval_result['score']:.2f})")

        # Dialectical Summary
        summary.append(f"\n--- Dialectical Reasoner ---")
        summary.append(f"Positionen: {len(self.dialectical.positions)}")
        summary.append(f"Synthesen: {len(self.dialectical.synthesis_history)}")

        return "\n".join(summary)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_advanced_reasoning_engine(modes: List[ReasoningMode] = None) -> AdvancedReasoningEngine:
    """
    Erstellt eine Advanced Reasoning Engine mit den gewünschten Modi.

    Args:
        modes: Liste der zu aktivierenden Modi. Default: alle

    Returns:
        Konfigurierte AdvancedReasoningEngine
    """
    engine = AdvancedReasoningEngine()

    if modes is None:
        modes = [ReasoningMode.BAYESIAN, ReasoningMode.CAUSAL,
                 ReasoningMode.METACOGNITIVE, ReasoningMode.DIALECTICAL]

    for mode in modes:
        engine.activate_mode(mode)

    return engine


# =============================================================================
# BEISPIEL / TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🧠 Advanced Reasoning Engine - Demo\n")

    # Erstelle Engine mit allen Modi
    engine = create_advanced_reasoning_engine()

    # Teste Bayesian Reasoning
    print("--- Bayesian Reasoning ---")
    engine.bayesian.add_belief("regen_morgen", "Es wird morgen regnen", prior=0.3)
    engine.bayesian.update_belief("regen_morgen", "Dunkle Wolken am Himmel", 0.8, 0.2)
    print(f"P(Regen|Wolken): {engine.bayesian.beliefs['regen_morgen'].posterior:.3f}")
    print(f"Konfidenz: {engine.bayesian.get_confidence_level('regen_morgen')}")

    # Teste Causal Reasoning
    print("\n--- Causal Reasoning ---")
    engine.causal.add_variable("rauchen", "Rauchen")
    engine.causal.add_variable("lungenkrebs", "Lungenkrebs")
    engine.causal.add_variable("gene", "Genetische Prädisposition")
    engine.causal.add_causal_link("rauchen", "lungenkrebs", CausalStrength.STRONG)
    engine.causal.add_causal_link("gene", "lungenkrebs", CausalStrength.MODERATE)
    print(engine.causal.explain_causal_relationship("rauchen", "lungenkrebs"))

    # Teste Dialectical Reasoning
    print("\n--- Dialectical Reasoning ---")
    thesis = engine.dialectical.propose_thesis(
        "KI wird die Menschheit voranbringen",
        ["Effizienzsteigerung", "Medizinische Durchbrüche", "Wissenschaftliche Entdeckungen"]
    )
    antithesis = engine.dialectical.propose_antithesis(
        thesis,
        "KI birgt existenzielle Risiken",
        ["Arbeitsplatzverlust", "Kontrollverlust", "Missbrauchspotential"]
    )
    synthesis = engine.dialectical.synthesize(thesis, antithesis)
    print(f"Synthese: {synthesis.content[:200]}...")

    # Teste kombiniertes Reasoning
    print("\n--- Kombiniertes Reasoning ---")
    result = engine.reason(
        "Sollten wir KI-Entwicklung regulieren?",
        context={
            "prior_probability": 0.6,
            "evidence": [
                {"description": "KI-Unfälle nehmen zu", "likelihood_if_true": 0.8, "likelihood_if_false": 0.3}
            ],
            "thesis_arguments": ["Sicherheit geht vor", "Verantwortungsvolle Innovation"],
            "antithesis_arguments": ["Innovation wird gebremst", "Internationale Konkurrenz"]
        }
    )
    print(f"Ergebnis: {result['results'].keys()}")

    # Gesamtzusammenfassung
    print("\n" + engine.get_reasoning_summary())
