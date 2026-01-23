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
# IMPORTS VON KONSOLIDIERTEN MODULEN
# =============================================================================

# Kausalitäts-Komponenten aus holo_counterfactual_reasoning (primäres Modul)
try:
    from holo_counterfactual_reasoning import (
        CausalIntegrator,
        InterventionalReasoning,
        CausalDiscovery,
        ConfoundingDetector,
        CausalStrengthEstimator,
        TemporalCausality,
        CausalChainValidator,
        CounterfactualReasoningEngine,
        CausalLink as CounterfactualCausalLink,
        CausalRelationType,
    )
    _HAS_COUNTERFACTUAL = True
    logger.info("[AdvancedReasoning] Nutzt CausalIntegrator aus holo_counterfactual_reasoning")
except ImportError:
    _HAS_COUNTERFACTUAL = False
    CausalIntegrator = None
    logger.warning("[AdvancedReasoning] holo_counterfactual_reasoning nicht verfügbar - nutze lokale Implementierung")

# Meta-Cognition für Integration mit MetacognitiveReasoner
try:
    from holo_meta_cognition import HoloMetaObserver, ObservationType
    _HAS_META_COGNITION = True
    logger.info("[AdvancedReasoning] Nutzt HoloMetaObserver aus holo_meta_cognition")
except ImportError:
    _HAS_META_COGNITION = False
    HoloMetaObserver = None
    ObservationType = None


# =============================================================================
# ENUMS
# =============================================================================

class ReasoningMode(Enum):
    """Verfügbare Reasoning-Modi"""
    BAYESIAN = "bayesian"
    CAUSAL = "causal"
    METACOGNITIVE = "metacognitive"
    DIALECTICAL = "dialectical"
    ABDUCTIVE = "abductive"      # NEU: Schluss auf beste Erklärung
    TEMPORAL = "temporal"        # NEU: Zeitbasiertes Reasoning
    COMBINED = "combined"        # Alle Modi zusammen


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
    Erweitertes Bayesianisches Reasoning mit Prior-Updates.

    Implementiert:
    - Bayes' Theorem: P(H|E) = P(E|H) * P(H) / P(E)
    - Belief Networks mit Abhängigkeiten
    - Evidenz-Updates mit verschiedenen Strategien
    - Konfidenz-Kalibrierung
    - Bedingte Wahrscheinlichkeiten
    - Sensitivitätsanalyse
    - Bayesian Model Averaging
    - Multi-Hypothesen-Vergleich
    - Sequentielles Belief-Update
    - Jeffreys' Prior für uninformative Priors
    - Beta-Binomial Konjugate Priors
    """

    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
        self.evidence_pool: List[Dict] = []
        self.calibration_history: List[Tuple[float, bool]] = []
        # NEU: Erweiterungen
        self.belief_network: Dict[str, List[str]] = {}  # Abhängigkeiten zwischen Beliefs
        self.conditional_probabilities: Dict[str, Dict[str, float]] = {}  # P(A|B) Speicher
        self.hypothesis_models: Dict[str, Dict[str, Any]] = {}  # Mehrere Modelle
        self.prior_strategies: Dict[str, str] = {}  # Prior-Typ pro Belief
        self.sensitivity_cache: Dict[str, Dict[str, float]] = {}  # Sensitivitäts-Ergebnisse
        self.beta_parameters: Dict[str, Tuple[float, float]] = {}  # Alpha, Beta für konjugate Priors
        self.evidence_weights: Dict[str, float] = {}  # Gewichtung verschiedener Evidenzquellen
        self.model_weights: Dict[str, float] = {}  # Für Bayesian Model Averaging

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

    # =========================================================================
    # NEUE ERWEITERUNGEN: Belief Networks
    # =========================================================================

    def add_belief_dependency(self, dependent: str, parent: str,
                               conditional_prob: float = 0.7) -> bool:
        """
        Fügt eine Abhängigkeit zwischen Beliefs hinzu.

        Args:
            dependent: Der abhängige Belief
            parent: Der Eltern-Belief
            conditional_prob: P(dependent|parent)

        Returns:
            True wenn erfolgreich
        """
        if dependent not in self.beliefs or parent not in self.beliefs:
            logger.warning(f"Belief nicht gefunden: {dependent} oder {parent}")
            return False

        if dependent not in self.belief_network:
            self.belief_network[dependent] = []

        if parent not in self.belief_network[dependent]:
            self.belief_network[dependent].append(parent)

        # Speichere bedingte Wahrscheinlichkeit
        key = f"{dependent}|{parent}"
        self.conditional_probabilities[key] = max(0.001, min(0.999, conditional_prob))

        logger.debug(f"Belief-Abhängigkeit: P({dependent}|{parent}) = {conditional_prob:.3f}")
        return True

    def get_conditional_probability(self, belief: str, given: str) -> float:
        """
        Gibt P(belief|given) zurück.
        """
        key = f"{belief}|{given}"
        if key in self.conditional_probabilities:
            return self.conditional_probabilities[key]

        # Fallback: Unabhängigkeitsannahme
        if belief in self.beliefs:
            return self.beliefs[belief].posterior
        return 0.5

    def propagate_belief_network(self, updated_belief: str) -> Dict[str, float]:
        """
        Propagiert Updates durch das Belief-Netzwerk.
        Wenn ein Belief aktualisiert wird, werden abhängige Beliefs angepasst.

        Returns:
            Dict mit allen aktualisierten Beliefs und neuen Wahrscheinlichkeiten
        """
        updates = {}
        if updated_belief not in self.beliefs:
            return updates

        new_value = self.beliefs[updated_belief].posterior
        updates[updated_belief] = new_value

        # Finde alle Beliefs, die von diesem abhängen
        for dependent, parents in self.belief_network.items():
            if updated_belief in parents:
                # Berechne neuen Wert basierend auf bedingter Wahrscheinlichkeit
                cond_key = f"{dependent}|{updated_belief}"
                if cond_key in self.conditional_probabilities:
                    cond_prob = self.conditional_probabilities[cond_key]
                    # P(D) = P(D|U)*P(U) + P(D|¬U)*P(¬U)
                    # Vereinfacht: Gewichtete Anpassung
                    old_posterior = self.beliefs[dependent].posterior
                    adjustment = cond_prob * new_value + (1 - cond_prob) * (1 - new_value)
                    new_posterior = 0.7 * old_posterior + 0.3 * adjustment
                    self.beliefs[dependent].posterior = max(0.001, min(0.999, new_posterior))
                    updates[dependent] = self.beliefs[dependent].posterior

        return updates

    # =========================================================================
    # NEUE ERWEITERUNGEN: Multi-Hypothesen-Vergleich
    # =========================================================================

    def add_hypothesis_model(self, model_name: str, hypotheses: Dict[str, float],
                              prior_weight: float = 1.0) -> None:
        """
        Fügt ein Hypothesen-Modell hinzu für Bayesian Model Averaging.

        Args:
            model_name: Name des Modells
            hypotheses: Dict {hypothesis_name: prior_probability}
            prior_weight: Gewichtung des Modells
        """
        # Normalisiere Wahrscheinlichkeiten
        total = sum(hypotheses.values())
        if total > 0:
            normalized = {h: p/total for h, p in hypotheses.items()}
        else:
            normalized = {h: 1.0/len(hypotheses) for h in hypotheses}

        self.hypothesis_models[model_name] = {
            "hypotheses": normalized,
            "posteriors": normalized.copy(),
            "evidence_history": []
        }
        self.model_weights[model_name] = prior_weight
        logger.debug(f"Neues Hypothesen-Modell: {model_name} mit {len(hypotheses)} Hypothesen")

    def update_hypothesis_model(self, model_name: str, evidence: str,
                                  likelihoods: Dict[str, float]) -> Dict[str, float]:
        """
        Aktualisiert alle Hypothesen in einem Modell mit neuer Evidenz.

        Args:
            model_name: Name des Modells
            evidence: Beschreibung der Evidenz
            likelihoods: P(E|H) für jede Hypothese H

        Returns:
            Aktualisierte Posteriors
        """
        if model_name not in self.hypothesis_models:
            logger.warning(f"Modell '{model_name}' nicht gefunden")
            return {}

        model = self.hypothesis_models[model_name]
        posteriors = model["posteriors"]

        # Berechne P(E) = Σ P(E|H) * P(H)
        p_evidence = sum(
            likelihoods.get(h, 0.5) * posteriors[h]
            for h in posteriors
        )

        if p_evidence < 0.0001:
            p_evidence = 0.0001

        # Update jede Hypothese: P(H|E) = P(E|H) * P(H) / P(E)
        new_posteriors = {}
        for hypothesis, prior in posteriors.items():
            likelihood = likelihoods.get(hypothesis, 0.5)
            posterior = (likelihood * prior) / p_evidence
            new_posteriors[hypothesis] = max(0.0001, min(0.9999, posterior))

        # Normalisieren
        total = sum(new_posteriors.values())
        model["posteriors"] = {h: p/total for h, p in new_posteriors.items()}
        model["evidence_history"].append((evidence, likelihoods))

        return model["posteriors"]

    def get_most_likely_hypothesis(self, model_name: str) -> Tuple[str, float]:
        """
        Gibt die wahrscheinlichste Hypothese eines Modells zurück.
        """
        if model_name not in self.hypothesis_models:
            return ("unknown", 0.0)

        posteriors = self.hypothesis_models[model_name]["posteriors"]
        best = max(posteriors.items(), key=lambda x: x[1])
        return best

    def bayesian_model_average(self, query_hypothesis: str) -> float:
        """
        Bayesian Model Averaging über alle Modelle für eine Hypothese.

        P(H) = Σ P(H|M) * P(M)
        """
        total_weight = sum(self.model_weights.values())
        if total_weight == 0:
            return 0.5

        averaged = 0.0
        for model_name, model in self.hypothesis_models.items():
            if query_hypothesis in model["posteriors"]:
                weight = self.model_weights[model_name] / total_weight
                averaged += model["posteriors"][query_hypothesis] * weight

        return averaged

    # =========================================================================
    # NEUE ERWEITERUNGEN: Sensitivitätsanalyse
    # =========================================================================

    def sensitivity_analysis(self, belief_name: str,
                              prior_range: Tuple[float, float] = (0.1, 0.9),
                              steps: int = 10) -> Dict[str, Any]:
        """
        Führt Sensitivitätsanalyse durch: Wie ändert sich das Posterior
        bei verschiedenen Priors?

        Args:
            belief_name: Name des Beliefs
            prior_range: Min/Max Prior zu testen
            steps: Anzahl der Schritte

        Returns:
            Sensitivitätsergebnisse
        """
        if belief_name not in self.beliefs:
            return {"error": "Belief nicht gefunden"}

        belief = self.beliefs[belief_name]
        results = {
            "belief": belief_name,
            "original_prior": belief.prior_probability,
            "original_posterior": belief.posterior,
            "sensitivity_curve": [],
            "robustness": 0.0
        }

        priors = []
        posteriors = []

        step_size = (prior_range[1] - prior_range[0]) / steps
        for i in range(steps + 1):
            test_prior = prior_range[0] + i * step_size

            # Simuliere Posterior mit diesem Prior
            # Nutze die Evidenz-History
            simulated_posterior = test_prior
            for evidence, _ in belief.evidence_history:
                # Vereinfachte Simulation
                simulated_posterior = simulated_posterior * 1.1 if simulated_posterior < 0.5 else simulated_posterior * 0.9
                simulated_posterior = max(0.001, min(0.999, simulated_posterior))

            priors.append(test_prior)
            posteriors.append(simulated_posterior)
            results["sensitivity_curve"].append({
                "prior": test_prior,
                "posterior": simulated_posterior
            })

        # Berechne Robustheit: Wie stabil ist die Schlussfolgerung?
        if posteriors:
            variance = sum((p - sum(posteriors)/len(posteriors))**2 for p in posteriors) / len(posteriors)
            results["robustness"] = 1.0 - min(variance * 4, 1.0)  # Höhere Varianz = weniger robust

        self.sensitivity_cache[belief_name] = results
        return results

    def information_gain(self, belief_name: str, potential_evidence: str,
                          p_evidence_if_true: float,
                          p_evidence_if_false: float) -> float:
        """
        Berechnet den erwarteten Informationsgewinn durch potenzielle Evidenz.

        KL-Divergenz zwischen Prior und erwartetem Posterior.
        """
        if belief_name not in self.beliefs:
            return 0.0

        prior = self.beliefs[belief_name].posterior

        # Erwartetes Posterior wenn Evidenz positiv
        p_e = p_evidence_if_true * prior + p_evidence_if_false * (1 - prior)
        if p_e < 0.001:
            p_e = 0.001

        posterior_positive = (p_evidence_if_true * prior) / p_e

        # Erwartetes Posterior wenn Evidenz negativ
        p_not_e = (1 - p_evidence_if_true) * prior + (1 - p_evidence_if_false) * (1 - prior)
        if p_not_e < 0.001:
            p_not_e = 0.001
        posterior_negative = ((1 - p_evidence_if_true) * prior) / p_not_e

        # Erwarteter Informationsgewinn
        prior_entropy = self.entropy(belief_name)

        # Entropie nach positiver Evidenz
        post_entropy_pos = 0.0
        if 0.001 < posterior_positive < 0.999:
            post_entropy_pos = -posterior_positive * math.log2(posterior_positive) - \
                              (1-posterior_positive) * math.log2(1-posterior_positive)

        # Entropie nach negativer Evidenz
        post_entropy_neg = 0.0
        if 0.001 < posterior_negative < 0.999:
            post_entropy_neg = -posterior_negative * math.log2(posterior_negative) - \
                              (1-posterior_negative) * math.log2(1-posterior_negative)

        # Gewichteter Erwartungswert
        expected_entropy = p_e * post_entropy_pos + (1 - p_e) * post_entropy_neg

        return max(0, prior_entropy - expected_entropy)

    # =========================================================================
    # NEUE ERWEITERUNGEN: Konjugierte Priors (Beta-Binomial)
    # =========================================================================

    def add_belief_with_beta_prior(self, name: str, content: str,
                                     alpha: float = 1.0, beta: float = 1.0) -> Belief:
        """
        Fügt einen Belief mit Beta-Prior hinzu (konjugiert für Binomial).

        Alpha und Beta repräsentieren "pseudobeobachtungen":
        - Alpha: Anzahl "Erfolge" im Prior
        - Beta: Anzahl "Misserfolge" im Prior
        - Alpha = Beta = 1: Uniformer Prior (keine Vorinformation)
        - Alpha = Beta = 0.5: Jeffreys' uninformativer Prior
        """
        self.beta_parameters[name] = (alpha, beta)
        prior = alpha / (alpha + beta)  # Erwartungswert der Beta-Verteilung

        belief = self.add_belief(name, content, prior)
        self.prior_strategies[name] = "beta_binomial"

        logger.debug(f"Beta-Prior für '{name}': α={alpha}, β={beta}, E[p]={prior:.3f}")
        return belief

    def update_beta_belief(self, belief_name: str, successes: int,
                            failures: int) -> Optional[Belief]:
        """
        Aktualisiert einen Beta-Belief mit Beobachtungen.

        Konjugierte Update-Regel: α' = α + successes, β' = β + failures
        """
        if belief_name not in self.beliefs or belief_name not in self.beta_parameters:
            logger.warning(f"Beta-Belief '{belief_name}' nicht gefunden")
            return None

        alpha, beta = self.beta_parameters[belief_name]
        new_alpha = alpha + successes
        new_beta = beta + failures

        self.beta_parameters[belief_name] = (new_alpha, new_beta)

        # Neuer Erwartungswert
        new_posterior = new_alpha / (new_alpha + new_beta)
        self.beliefs[belief_name].posterior = new_posterior
        self.beliefs[belief_name].evidence_history.append(
            (f"+{successes}/-{failures}", new_posterior)
        )

        logger.info(f"Beta-Update '{belief_name}': α={new_alpha}, β={new_beta}, E[p]={new_posterior:.3f}")
        return self.beliefs[belief_name]

    def get_beta_credible_interval(self, belief_name: str,
                                     credibility: float = 0.95) -> Tuple[float, float]:
        """
        Berechnet das Kredibilitätsintervall für einen Beta-Belief.

        Args:
            belief_name: Name des Beliefs
            credibility: Gewünschte Glaubwürdigkeit (z.B. 0.95 für 95%)

        Returns:
            (lower, upper) Grenzen des Intervalls
        """
        if belief_name not in self.beta_parameters:
            return (0.0, 1.0)

        alpha, beta = self.beta_parameters[belief_name]

        # Approximation des Kredibilitätsintervalls
        # Für große α, β: Beta ≈ Normal mit μ=α/(α+β), σ²=αβ/((α+β)²(α+β+1))
        mean = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))
        std = math.sqrt(variance)

        # Z-Score für Kredibilitätsniveau
        z = 1.96 if credibility >= 0.95 else 1.645 if credibility >= 0.90 else 1.28

        lower = max(0.0, mean - z * std)
        upper = min(1.0, mean + z * std)

        return (lower, upper)

    # =========================================================================
    # NEUE ERWEITERUNGEN: Erweiterte Evidenztypen
    # =========================================================================

    def add_weighted_evidence(self, belief_name: str, evidence: str,
                               evidence_type: EvidenceType,
                               source_reliability: float = 1.0,
                               sample_size: int = 1) -> Optional[Belief]:
        """
        Fügt gewichtete Evidenz hinzu mit Quellen-Zuverlässigkeit.

        Args:
            belief_name: Name des Beliefs
            evidence: Evidenz-Beschreibung
            evidence_type: Art der Evidenz
            source_reliability: Zuverlässigkeit der Quelle (0-1)
            sample_size: Stichprobengröße (mehr = stärker)
        """
        if belief_name not in self.beliefs:
            return None

        # Basis-Likelihood-Ratio aus Evidenztyp
        base_lr = self.compute_likelihood_ratio(belief_name, evidence, evidence_type)

        # Gewichtung durch Quellen-Zuverlässigkeit
        weighted_lr = 1.0 + (base_lr - 1.0) * source_reliability

        # Stichprobengrößen-Anpassung (größere Stichprobe = stärkere Evidenz)
        sample_factor = min(2.0, 1.0 + math.log10(max(1, sample_size)) * 0.3)
        final_lr = 1.0 + (weighted_lr - 1.0) * sample_factor

        # Konvertiere LR zu Likelihoods
        if final_lr > 1:
            likelihood_if_true = min(0.95, 0.5 + 0.45 * (final_lr - 1) / final_lr)
            likelihood_if_false = max(0.05, 0.5 - 0.45 * (final_lr - 1) / final_lr)
        else:
            likelihood_if_true = max(0.05, 0.5 * final_lr)
            likelihood_if_false = min(0.95, 0.5 / final_lr)

        return self.update_belief(belief_name, evidence, likelihood_if_true, likelihood_if_false)

    def sequential_update(self, belief_name: str,
                           evidence_sequence: List[Dict[str, Any]]) -> List[float]:
        """
        Führt sequenzielle Belief-Updates durch und gibt Historie zurück.

        Args:
            belief_name: Name des Beliefs
            evidence_sequence: Liste von {"evidence": str, "type": EvidenceType}

        Returns:
            Liste der Posteriors nach jedem Update
        """
        posteriors = []

        for ev in evidence_sequence:
            evidence = ev.get("evidence", "")
            ev_type = ev.get("type", EvidenceType.NEUTRAL)
            reliability = ev.get("reliability", 1.0)

            result = self.add_weighted_evidence(
                belief_name, evidence, ev_type, reliability
            )

            if result:
                posteriors.append(result.posterior)

        return posteriors

    # =========================================================================
    # NEUE ERWEITERUNGEN: Diagnostische Metriken
    # =========================================================================

    def belief_summary(self, belief_name: str) -> Dict[str, Any]:
        """
        Gibt eine umfassende Zusammenfassung eines Beliefs zurück.
        """
        if belief_name not in self.beliefs:
            return {"error": "Belief nicht gefunden"}

        belief = self.beliefs[belief_name]

        summary = {
            "name": belief_name,
            "content": belief.content,
            "prior": belief.prior_probability,
            "posterior": belief.posterior,
            "confidence_level": self.get_confidence_level(belief_name),
            "entropy": self.entropy(belief_name),
            "evidence_count": len(belief.evidence_history),
            "last_updated": belief.last_updated.isoformat() if belief.last_updated else None,
            "network_parents": self.belief_network.get(belief_name, []),
            "prior_strategy": self.prior_strategies.get(belief_name, "standard"),
        }

        # Beta-Parameter wenn vorhanden
        if belief_name in self.beta_parameters:
            alpha, beta = self.beta_parameters[belief_name]
            summary["beta_alpha"] = alpha
            summary["beta_beta"] = beta
            summary["credible_interval_95"] = self.get_beta_credible_interval(belief_name, 0.95)

        # Sensitivität wenn berechnet
        if belief_name in self.sensitivity_cache:
            summary["robustness"] = self.sensitivity_cache[belief_name].get("robustness", None)

        return summary

    def get_all_beliefs_ranked(self) -> List[Tuple[str, float, str]]:
        """
        Gibt alle Beliefs sortiert nach Posterior zurück.

        Returns:
            Liste von (name, posterior, confidence_level)
        """
        ranked = []
        for name, belief in self.beliefs.items():
            conf = self.get_confidence_level(name)
            ranked.append((name, belief.posterior, conf))

        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def cross_entropy_beliefs(self, belief1: str, belief2: str) -> float:
        """
        Berechnet Cross-Entropy zwischen zwei Beliefs.
        Maß für Übereinstimmung/Konflikt.
        """
        if belief1 not in self.beliefs or belief2 not in self.beliefs:
            return float('inf')

        p = self.beliefs[belief1].posterior
        q = self.beliefs[belief2].posterior

        # H(p,q) = -p*log(q) - (1-p)*log(1-q)
        q = max(0.001, min(0.999, q))

        return -p * math.log2(q) - (1-p) * math.log2(1-q)


# =============================================================================
# 2. CAUSAL REASONING - Kausalität verstehen
# =============================================================================
#
# HINWEIS: Für erweiterte Kausalitäts-Funktionen nutze holo_counterfactual_reasoning.py:
# - CausalIntegrator: Zentraler Hub für alle Kausalitäts-Komponenten
# - InterventionalReasoning: Do-Calculus und Interventionseffekte
# - CausalDiscovery: Kausale Struktur-Entdeckung
# - ConfoundingDetector: Erkennt konfundierende Variablen
# - CausalStrengthEstimator: Quantifiziert kausale Stärke
# - TemporalCausality: Zeitbasierte Kausalitätsanalyse
# - CausalChainValidator: Validiert kausale Ketten
#
# Diese Klasse bietet eine einfache Schnittstelle und delegiert an das
# erweiterte System wenn verfügbar.
# =============================================================================

class CausalDomain(Enum):
    """Domänen für kausale Beziehungen"""
    MEDIZIN = "medizin"
    PSYCHOLOGIE = "psychologie"
    WIRTSCHAFT = "wirtschaft"
    SOZIALES = "soziales"
    PHYSIK = "physik"
    BIOLOGIE = "biologie"
    TECHNOLOGIE = "technologie"
    UMWELT = "umwelt"
    POLITIK = "politik"
    BILDUNG = "bildung"
    ALLGEMEIN = "allgemein"
    # NEU: Erweiterte Domänen
    RECHT = "recht"
    ETHIK = "ethik"
    KUNST = "kunst"
    SPORT = "sport"
    KOMMUNIKATION = "kommunikation"
    NEUROWISSENSCHAFT = "neurowissenschaft"
    PHILOSOPHIE = "philosophie"
    LINGUISTIK = "linguistik"


# =============================================================================
# NEUE ENUMS FÜR ERWEITERTE REASONING-TYPEN
# =============================================================================

class AbductiveHypothesisType(Enum):
    """Typen abduktiver Hypothesen"""
    CAUSAL = "causal"              # Ursache-Erklärung
    FUNCTIONAL = "functional"      # Funktionale Erklärung
    INTENTIONAL = "intentional"    # Absichts-basierte Erklärung
    STRUCTURAL = "structural"      # Struktur-basierte Erklärung
    TELEOLOGICAL = "teleological"  # Zweck-orientierte Erklärung


class TemporalRelation(Enum):
    """Zeitliche Beziehungen zwischen Ereignissen"""
    BEFORE = "before"                 # A vor B
    AFTER = "after"                   # A nach B
    DURING = "during"                 # A während B
    OVERLAPS = "overlaps"             # A überlappt mit B
    MEETS = "meets"                   # A endet wenn B beginnt
    STARTS = "starts"                 # A beginnt mit B
    FINISHES = "finishes"             # A endet mit B
    EQUALS = "equals"                 # A und B sind zeitgleich
    CAUSES_IMMEDIATELY = "causes_immediately"  # A verursacht B sofort
    CAUSES_DELAYED = "causes_delayed"          # A verursacht B verzögert


class TemporalGranularity(Enum):
    """Zeitliche Granularität"""
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    DECADES = "decades"


class MediatorType(Enum):
    """Typen von Mediator-Variablen"""
    FULL_MEDIATION = "full"      # Mediator erklärt gesamten Effekt
    PARTIAL_MEDIATION = "partial"  # Mediator erklärt Teil des Effekts
    INCONSISTENT = "inconsistent"  # Mediator und direkter Effekt haben unterschiedliche Richtungen


class ModeratorEffect(Enum):
    """Arten von Moderations-Effekten"""
    ENHANCING = "enhancing"      # Verstärkt den Effekt
    BUFFERING = "buffering"      # Schwächt den Effekt ab
    ANTAGONISTIC = "antagonistic"  # Kehrt den Effekt um


@dataclass
class CausalChain:
    """Eine kausale Kette von Variablen"""
    chain_id: str
    variables: List[str]
    domain: CausalDomain
    total_strength: float
    mechanisms: List[str]
    time_delays: List[float] = field(default_factory=list)  # In Zeiteinheiten
    is_reversible: bool = False
    confidence: float = 0.5


# =============================================================================
# NEU: DATENSTRUKTUREN FÜR ABDUKTIVES REASONING
# =============================================================================

@dataclass
class Observation:
    """Eine Beobachtung, die erklärt werden soll"""
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    reliability: float = 0.8  # Wie zuverlässig ist die Beobachtung?
    context: Dict[str, Any] = field(default_factory=dict)
    source: str = ""


@dataclass
class AbductiveHypothesis:
    """Eine abduktive Hypothese (mögliche Erklärung)"""
    hypothesis_id: str
    content: str
    hypothesis_type: AbductiveHypothesisType
    explains: List[str]  # Welche Beobachtungen erklärt diese Hypothese?
    plausibility: float  # Wie plausibel ist die Hypothese?
    simplicity: float  # Ockhams Rasiermesser: einfachere Erklärungen bevorzugt
    scope: float  # Wie viele Phänomene erklärt sie?
    coherence: float  # Passt sie zum bestehenden Wissen?
    testability: float  # Kann sie getestet/falsifiziert werden?
    supporting_evidence: List[str] = field(default_factory=list)
    counter_evidence: List[str] = field(default_factory=list)
    prior_probability: float = 0.5

    def overall_score(self) -> float:
        """Berechnet Gesamtbewertung der Hypothese"""
        return (
            self.plausibility * 0.25 +
            self.simplicity * 0.15 +
            self.scope * 0.20 +
            self.coherence * 0.20 +
            self.testability * 0.10 +
            self.prior_probability * 0.10
        )


@dataclass
class InferenceToTheBestExplanation:
    """Ergebnis einer Inference to the Best Explanation (IBE)"""
    observations: List[Observation]
    hypotheses: List[AbductiveHypothesis]
    best_hypothesis: Optional[AbductiveHypothesis]
    ranking: List[Tuple[str, float]]  # (hypothesis_id, score)
    confidence: float
    reasoning_trace: List[str]


# =============================================================================
# NEU: DATENSTRUKTUREN FÜR TEMPORALES REASONING
# =============================================================================

@dataclass
class TemporalEvent:
    """Ein zeitliches Ereignis"""
    event_id: str
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # In Sekunden
    granularity: TemporalGranularity = TemporalGranularity.SECONDS
    is_instantaneous: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalConstraint:
    """Eine zeitliche Einschränkung zwischen Ereignissen"""
    event_a: str
    event_b: str
    relation: TemporalRelation
    min_gap: Optional[float] = None  # Minimaler zeitlicher Abstand
    max_gap: Optional[float] = None  # Maximaler zeitlicher Abstand
    confidence: float = 0.8


@dataclass
class TemporalCausalLink:
    """Eine zeitlich-kausale Verbindung"""
    cause_event: str
    effect_event: str
    delay: float  # Zeitliche Verzögerung
    delay_variance: float = 0.0  # Variabilität der Verzögerung
    strength: float = 0.5
    mechanism: str = ""
    is_deterministic: bool = False


@dataclass
class TemporalPattern:
    """Ein erkanntes zeitliches Muster"""
    pattern_id: str
    description: str
    events_sequence: List[str]  # Reihenfolge der Events
    typical_intervals: List[float]  # Typische Zeitabstände
    frequency: int = 0  # Wie oft wurde das Muster beobachtet?
    confidence: float = 0.5
    is_periodic: bool = False
    period: Optional[float] = None  # Periodendauer wenn periodisch


@dataclass
class Timeline:
    """Eine Zeitleiste mit Ereignissen"""
    timeline_id: str
    events: Dict[str, TemporalEvent] = field(default_factory=dict)
    constraints: List[TemporalConstraint] = field(default_factory=list)
    causal_links: List[TemporalCausalLink] = field(default_factory=list)
    start: Optional[datetime] = None
    end: Optional[datetime] = None


@dataclass
class MediatorRelation:
    """Mediator-Beziehung zwischen Variablen"""
    cause: str
    mediator: str
    effect: str
    mediation_type: MediatorType
    indirect_effect: float  # a*b Pfad
    direct_effect: float    # c' Pfad
    total_effect: float     # c = c' + a*b
    proportion_mediated: float


@dataclass
class ModeratorRelation:
    """Moderator-Beziehung"""
    cause: str
    effect: str
    moderator: str
    moderator_effect: ModeratorEffect
    base_strength: float       # Effektstärke ohne Moderator
    moderated_strength: float  # Effektstärke mit Moderator
    interaction_coefficient: float


class CausalReasoner:
    """
    Erweitertes Kausales Reasoning mit Kausalmodellen.

    KONSOLIDIERT: Delegiert an CausalIntegrator aus holo_counterfactual_reasoning.py
    wenn verfügbar. Bietet Rückwärtskompatibilität für einfache Anwendungsfälle.

    Implementiert:
    - Kausale Graphen (DAGs) mit Domänen
    - Interventionen (do-Operator)
    - Kontrafaktische Fragen
    - Confounder-Erkennung
    - NEU: Mediator-Variablen
    - NEU: Moderator-Variablen
    - NEU: Komplexe kausale Ketten
    - NEU: Domänen-spezifisches Wissen
    - NEU: Zeitliche Kausalität mit Verzögerungen
    - NEU: Feedback-Loops (zyklische Kausalität)
    - NEU: Kausale Stärke-Aggregation

    Für erweiterte Funktionen (ATE, Granger-Kausalität, etc.) nutze direkt:
    - holo_counterfactual_reasoning.CausalIntegrator
    """

    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.edges: List[CausalEdge] = []
        self.observations: List[Dict] = []

        # NEU: Erweiterte Strukturen
        self.causal_chains: Dict[str, CausalChain] = {}
        self.mediators: List[MediatorRelation] = []
        self.moderators: List[ModeratorRelation] = []
        self.domain_knowledge: Dict[CausalDomain, List[Dict]] = defaultdict(list)
        self.feedback_loops: List[List[str]] = []
        self.temporal_delays: Dict[Tuple[str, str], float] = {}  # (cause, effect) -> delay
        self.variable_domains: Dict[str, CausalDomain] = {}

        # Integration mit erweitertem Kausalitäts-System
        self._causal_integrator = None
        self._confounding_detector = None
        if _HAS_COUNTERFACTUAL and CausalIntegrator is not None:
            try:
                self._causal_integrator = CausalIntegrator()
                self._confounding_detector = self._causal_integrator.confounding
                logger.debug("[CausalReasoner] Nutzt CausalIntegrator für erweiterte Analyse")
            except Exception as e:
                logger.warning(f"[CausalReasoner] CausalIntegrator nicht verfügbar: {e}")

        # Initialisiere Domänen-Wissen
        self._initialize_domain_knowledge()

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

        KONSOLIDIERT: Nutzt InterventionalReasoning wenn verfügbar.

        Returns: Erwartete Auswirkungen auf andere Variablen
        """
        if variable not in self.nodes:
            return {}

        effects = {}
        effects[variable] = value

        # Nutze erweiterte Interventionsanalyse wenn verfügbar
        if self._causal_integrator is not None:
            try:
                # Registriere Intervention im erweiterten System
                for node_name in self.nodes:
                    if node_name != variable:
                        result = self._causal_integrator.interventional.estimate_do_effect(
                            variable, node_name
                        )
                        if result.get("causal_effect", 0) > 0.1:
                            effects[node_name] = f"beeinflusst ({result['causal_effect']*100:.0f}%)"
                return effects
            except Exception as e:
                logger.debug(f"[CausalReasoner] Fallback auf lokale Intervention: {e}")

        # Fallback: Lokale Propagation
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

        KONSOLIDIERT: Nutzt ConfoundingDetector wenn verfügbar.
        """
        # Nutze erweiterten Confounder-Detektor wenn verfügbar
        if self._confounding_detector is not None:
            try:
                is_spurious, confounder_list = self._confounding_detector.is_spurious(cause, effect)
                if confounder_list:
                    return confounder_list
            except Exception as e:
                logger.debug(f"[CausalReasoner] Fallback auf lokale Confounder-Suche: {e}")

        # Fallback: Lokale Implementierung
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

        KONSOLIDIERT: Nutzt CounterfactualReasoningEngine für erweiterte Analyse.
        Siehe auch: holo_counterfactual_reasoning.what_would_happen_if()
        """
        # Nutze erweiterte kontrafaktische Engine wenn verfügbar
        if _HAS_COUNTERFACTUAL and CounterfactualReasoningEngine is not None:
            try:
                cf_engine = CounterfactualReasoningEngine()
                # Erstelle Szenario-Beschreibung
                observed_str = ", ".join(f"{k}={v}" for k, v in observed.items())
                intervention_str = ", ".join(f"{k}={v}" for k, v in intervention.items())

                result = cf_engine.what_would_happen_if(
                    f"Beobachtet: {observed_str}",
                    intervention_str
                )
                return f"Kontrafaktisch: Wenn {intervention}, dann wäre {query_variable} = {result.get('predicted_outcome', 'unbestimmt')} (Konfidenz: {result.get('confidence', 0):.0%})"
            except Exception as e:
                logger.debug(f"[CausalReasoner] Fallback auf lokale kontrafaktische Analyse: {e}")

        # Fallback: Lokale Implementierung
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

    # =========================================================================
    # NEUE ERWEITERUNGEN: Domänen-Wissen
    # =========================================================================

    def _initialize_domain_knowledge(self):
        """Initialisiert vordefiniertes Domänen-Wissen für kausale Beziehungen"""

        # MEDIZIN
        self.domain_knowledge[CausalDomain.MEDIZIN] = [
            {"cause": "rauchen", "effect": "lungenkrebs", "strength": 0.85,
             "mechanism": "Karzinogene Substanzen schädigen DNA der Lungenzellen"},
            {"cause": "rauchen", "effect": "herzerkrankung", "strength": 0.70,
             "mechanism": "Gefäßverengung durch Nikotinwirkung"},
            {"cause": "bewegungsmangel", "effect": "adipositas", "strength": 0.65,
             "mechanism": "Unverbrannte Kalorien werden als Fett gespeichert"},
            {"cause": "adipositas", "effect": "diabetes_typ2", "strength": 0.60,
             "mechanism": "Insulinresistenz durch überschüssiges Fettgewebe"},
            {"cause": "stress", "effect": "bluthochdruck", "strength": 0.55,
             "mechanism": "Dauerhafte Aktivierung des sympathischen Nervensystems"},
            {"cause": "schlafmangel", "effect": "immunschwäche", "strength": 0.60,
             "mechanism": "Reduzierte T-Zellen-Produktion bei Schlafentzug"},
            {"cause": "ernährung", "effect": "darmgesundheit", "strength": 0.70,
             "mechanism": "Mikrobiom-Zusammensetzung hängt von Nahrung ab"},
            {"cause": "genetik", "effect": "krankheitsrisiko", "strength": 0.50,
             "mechanism": "Vererbte Genvarianzen beeinflussen Krankheitsanfälligkeit"},
            {"cause": "impfung", "effect": "immunität", "strength": 0.90,
             "mechanism": "Immunsystem lernt Antigen-Erkennung"},
            {"cause": "medikament", "effect": "symptomlinderung", "strength": 0.75,
             "mechanism": "Pharmakologische Wirkung auf Rezeptoren"},
        ]

        # PSYCHOLOGIE
        self.domain_knowledge[CausalDomain.PSYCHOLOGIE] = [
            {"cause": "kindheitstrauma", "effect": "depression", "strength": 0.55,
             "mechanism": "Frühe negative Erfahrungen prägen neuronale Muster"},
            {"cause": "soziale_isolation", "effect": "einsamkeit", "strength": 0.80,
             "mechanism": "Unerfülltes Zugehörigkeitsbedürfnis"},
            {"cause": "schlafmangel", "effect": "kognitive_beeinträchtigung", "strength": 0.70,
             "mechanism": "Gestörte Gedächtniskonsolidierung"},
            {"cause": "achtsamkeit", "effect": "stressreduktion", "strength": 0.60,
             "mechanism": "Aktivierung des parasympathischen Systems"},
            {"cause": "positive_verstärkung", "effect": "verhaltensänderung", "strength": 0.75,
             "mechanism": "Operante Konditionierung durch Belohnung"},
            {"cause": "selbstwirksamkeit", "effect": "leistung", "strength": 0.65,
             "mechanism": "Erhöhte Anstrengung und Persistenz bei Aufgaben"},
            {"cause": "kognitive_verzerrung", "effect": "angst", "strength": 0.60,
             "mechanism": "Überschätzung von Bedrohungen"},
            {"cause": "soziale_unterstützung", "effect": "wohlbefinden", "strength": 0.70,
             "mechanism": "Puffereffekt gegen Stressoren"},
            {"cause": "motivation", "effect": "zielerreichung", "strength": 0.65,
             "mechanism": "Erhöhte Persistenz und Ressourcenallokation"},
            {"cause": "lernen", "effect": "kompetenz", "strength": 0.80,
             "mechanism": "Neuronale Plastizität und Wissensakkumulation"},
        ]

        # WIRTSCHAFT
        self.domain_knowledge[CausalDomain.WIRTSCHAFT] = [
            {"cause": "zinssenkung", "effect": "wirtschaftswachstum", "strength": 0.55,
             "mechanism": "Günstigere Kredite stimulieren Investitionen"},
            {"cause": "geldmenge", "effect": "inflation", "strength": 0.65,
             "mechanism": "Mehr Geld bei gleichem Güterangebot erhöht Preise"},
            {"cause": "arbeitslosigkeit", "effect": "konsum_rückgang", "strength": 0.70,
             "mechanism": "Geringeres Einkommen reduziert Kaufkraft"},
            {"cause": "innovation", "effect": "produktivität", "strength": 0.75,
             "mechanism": "Effizientere Prozesse durch neue Technologien"},
            {"cause": "bildung", "effect": "einkommen", "strength": 0.60,
             "mechanism": "Höhere Qualifikation ermöglicht bessere Jobs"},
            {"cause": "steuersenkung", "effect": "investitionen", "strength": 0.50,
             "mechanism": "Mehr verfügbares Kapital für Unternehmen"},
            {"cause": "nachfrage", "effect": "preis", "strength": 0.80,
             "mechanism": "Angebot-Nachfrage-Gleichgewicht"},
            {"cause": "wettbewerb", "effect": "effizienz", "strength": 0.65,
             "mechanism": "Druck zur Kostenoptimierung"},
            {"cause": "globalisierung", "effect": "arbeitsteilung", "strength": 0.70,
             "mechanism": "Spezialisierung nach komparativen Vorteilen"},
            {"cause": "infrastruktur", "effect": "wirtschaftsentwicklung", "strength": 0.75,
             "mechanism": "Erleichterte Güter- und Informationsflüsse"},
        ]

        # SOZIALES
        self.domain_knowledge[CausalDomain.SOZIALES] = [
            {"cause": "armut", "effect": "kriminalität", "strength": 0.45,
             "mechanism": "Ökonomischer Druck und reduzierte Chancen"},
            {"cause": "bildungsniveau", "effect": "soziale_mobilität", "strength": 0.60,
             "mechanism": "Zugang zu besseren Berufschancen"},
            {"cause": "diskriminierung", "effect": "ungleichheit", "strength": 0.70,
             "mechanism": "Systematische Benachteiligung bestimmter Gruppen"},
            {"cause": "urbanisierung", "effect": "anonymität", "strength": 0.55,
             "mechanism": "Geringere soziale Kontrolle in Großstädten"},
            {"cause": "migration", "effect": "kultureller_wandel", "strength": 0.50,
             "mechanism": "Austausch von Traditionen und Werten"},
            {"cause": "soziale_medien", "effect": "polarisierung", "strength": 0.55,
             "mechanism": "Filterblasen verstärken bestehende Meinungen"},
            {"cause": "vertrauen", "effect": "kooperation", "strength": 0.80,
             "mechanism": "Erwartung von Reziprozität"},
            {"cause": "normen", "effect": "verhalten", "strength": 0.65,
             "mechanism": "Sozialer Druck zur Konformität"},
            {"cause": "gemeinschaft", "effect": "resilienz", "strength": 0.70,
             "mechanism": "Kollektive Ressourcen bei Krisen"},
            {"cause": "ungleichheit", "effect": "soziale_spannungen", "strength": 0.60,
             "mechanism": "Relative Deprivation erzeugt Frustration"},
        ]

        # PHYSIK
        self.domain_knowledge[CausalDomain.PHYSIK] = [
            {"cause": "kraft", "effect": "beschleunigung", "strength": 1.0,
             "mechanism": "F = m * a (Newtons zweites Gesetz)"},
            {"cause": "temperatur", "effect": "volumen_gas", "strength": 0.95,
             "mechanism": "Thermische Expansion (ideales Gasgesetz)"},
            {"cause": "druck", "effect": "siedepunkt", "strength": 0.90,
             "mechanism": "Dampfdruck-Gleichgewicht"},
            {"cause": "gravitation", "effect": "bewegung", "strength": 1.0,
             "mechanism": "Massenanziehung"},
            {"cause": "reibung", "effect": "wärme", "strength": 0.95,
             "mechanism": "Energieumwandlung durch Widerstand"},
            {"cause": "strom", "effect": "magnetfeld", "strength": 1.0,
             "mechanism": "Elektromagnetische Induktion"},
            {"cause": "licht", "effect": "photosynthese", "strength": 0.90,
             "mechanism": "Energieübertragung an Chlorophyll"},
            {"cause": "schall", "effect": "vibration", "strength": 0.95,
             "mechanism": "Mechanische Wellenübertragung"},
        ]

        # BIOLOGIE
        self.domain_knowledge[CausalDomain.BIOLOGIE] = [
            {"cause": "mutation", "effect": "evolution", "strength": 0.80,
             "mechanism": "Genetische Variation ermöglicht Selektion"},
            {"cause": "nahrung", "effect": "energie", "strength": 0.95,
             "mechanism": "Zelluläre Respiration"},
            {"cause": "hormone", "effect": "stoffwechsel", "strength": 0.85,
             "mechanism": "Signalübertragung an Zielzellen"},
            {"cause": "umwelt", "effect": "genexpression", "strength": 0.60,
             "mechanism": "Epigenetische Modifikationen"},
            {"cause": "selektion", "effect": "anpassung", "strength": 0.85,
             "mechanism": "Überleben der am besten Angepassten"},
            {"cause": "symbiose", "effect": "überleben", "strength": 0.70,
             "mechanism": "Gegenseitiger Nutzen"},
            {"cause": "reproduktion", "effect": "population", "strength": 0.90,
             "mechanism": "Nachkommenerzeugung"},
            {"cause": "konkurrenz", "effect": "nischenbildung", "strength": 0.65,
             "mechanism": "Ressourcenteilung zur Koexistenz"},
        ]

        # TECHNOLOGIE
        self.domain_knowledge[CausalDomain.TECHNOLOGIE] = [
            {"cause": "automatisierung", "effect": "effizienz", "strength": 0.80,
             "mechanism": "Reduzierung menschlicher Fehler und Zeit"},
            {"cause": "vernetzung", "effect": "kommunikation", "strength": 0.90,
             "mechanism": "Instantane Informationsübertragung"},
            {"cause": "datenmenge", "effect": "ki_leistung", "strength": 0.75,
             "mechanism": "Mehr Trainingsbeispiele verbessern Modelle"},
            {"cause": "rechenleistung", "effect": "innovation", "strength": 0.70,
             "mechanism": "Komplexere Berechnungen werden möglich"},
            {"cause": "benutzerfreundlichkeit", "effect": "adoption", "strength": 0.80,
             "mechanism": "Geringere Lernkurve erhöht Akzeptanz"},
            {"cause": "sicherheitslücke", "effect": "cyberangriff", "strength": 0.65,
             "mechanism": "Ausnutzung von Schwachstellen"},
            {"cause": "open_source", "effect": "innovation", "strength": 0.60,
             "mechanism": "Kollaborative Entwicklung"},
            {"cause": "regulierung", "effect": "entwicklung", "strength": 0.50,
             "mechanism": "Kann fördern oder hemmen"},
        ]

        # UMWELT
        self.domain_knowledge[CausalDomain.UMWELT] = [
            {"cause": "co2_emissionen", "effect": "klimawandel", "strength": 0.85,
             "mechanism": "Verstärkter Treibhauseffekt"},
            {"cause": "abholzung", "effect": "biodiversitätsverlust", "strength": 0.80,
             "mechanism": "Habitatzerstörung"},
            {"cause": "verschmutzung", "effect": "gesundheitsschäden", "strength": 0.70,
             "mechanism": "Toxische Substanzen im Körper"},
            {"cause": "klimawandel", "effect": "extremwetter", "strength": 0.75,
             "mechanism": "Veränderte atmosphärische Muster"},
            {"cause": "überfischung", "effect": "artensterben", "strength": 0.70,
             "mechanism": "Überschreitung der Reproduktionsrate"},
            {"cause": "erneuerbare_energie", "effect": "emissionsreduktion", "strength": 0.80,
             "mechanism": "Ersatz fossiler Brennstoffe"},
            {"cause": "recycling", "effect": "ressourcenschonung", "strength": 0.65,
             "mechanism": "Kreislaufwirtschaft"},
            {"cause": "landwirtschaft", "effect": "bodendegradation", "strength": 0.55,
             "mechanism": "Nährstofferschöpfung und Erosion"},
        ]

        # POLITIK
        self.domain_knowledge[CausalDomain.POLITIK] = [
            {"cause": "demokratie", "effect": "freiheit", "strength": 0.70,
             "mechanism": "Bürgerrechte und Gewaltenteilung"},
            {"cause": "korruption", "effect": "instabilität", "strength": 0.65,
             "mechanism": "Vertrauensverlust in Institutionen"},
            {"cause": "propaganda", "effect": "meinungsbildung", "strength": 0.60,
             "mechanism": "Selektive Informationsverbreitung"},
            {"cause": "sanktionen", "effect": "wirtschaftsschaden", "strength": 0.70,
             "mechanism": "Handelsbeschränkungen"},
            {"cause": "wahlen", "effect": "regierungswechsel", "strength": 0.80,
             "mechanism": "Demokratische Legitimation"},
            {"cause": "lobbying", "effect": "gesetzgebung", "strength": 0.55,
             "mechanism": "Interessenvertretung bei Entscheidungsträgern"},
            {"cause": "medien", "effect": "öffentliche_meinung", "strength": 0.65,
             "mechanism": "Agenda-Setting und Framing"},
            {"cause": "bildung", "effect": "politische_partizipation", "strength": 0.60,
             "mechanism": "Verständnis politischer Prozesse"},
        ]

        # BILDUNG
        self.domain_knowledge[CausalDomain.BILDUNG] = [
            {"cause": "lehrqualität", "effect": "lernerfolg", "strength": 0.75,
             "mechanism": "Didaktische Kompetenz und Motivation"},
            {"cause": "klassengröße", "effect": "individuelle_förderung", "strength": 0.60,
             "mechanism": "Mehr Zeit pro Schüler"},
            {"cause": "elternengagement", "effect": "schulleistung", "strength": 0.65,
             "mechanism": "Unterstützung und Wertschätzung"},
            {"cause": "frühförderung", "effect": "späterer_erfolg", "strength": 0.70,
             "mechanism": "Entwicklung kognitiver Grundlagen"},
            {"cause": "motivation", "effect": "lernen", "strength": 0.80,
             "mechanism": "Erhöhte Aufmerksamkeit und Anstrengung"},
            {"cause": "feedback", "effect": "verbesserung", "strength": 0.75,
             "mechanism": "Gezielte Fehlerkorrektur"},
            {"cause": "übung", "effect": "kompetenz", "strength": 0.85,
             "mechanism": "Neuronale Verstärkung durch Wiederholung"},
            {"cause": "stress", "effect": "lernbehinderung", "strength": 0.60,
             "mechanism": "Kognitive Ressourcen für Stressbewältigung"},
            # NEU: Erweiterte Bildungs-Kausalitäten
            {"cause": "digitalisierung", "effect": "lernzugang", "strength": 0.75,
             "mechanism": "Ortsunabhängiger Zugang zu Bildungsinhalten"},
            {"cause": "inklusion", "effect": "chancengleichheit", "strength": 0.65,
             "mechanism": "Abbau struktureller Barrieren"},
            {"cause": "sprachförderung", "effect": "lesekompetenz", "strength": 0.80,
             "mechanism": "Frühe sprachliche Grundlagen"},
            {"cause": "peer_learning", "effect": "soziale_kompetenz", "strength": 0.70,
             "mechanism": "Kollaboratives Lernen fördert Sozialkompetenz"},
        ]

        # =================================================================
        # NEU: ERWEITERTE DOMÄNEN
        # =================================================================

        # RECHT
        self.domain_knowledge[CausalDomain.RECHT] = [
            {"cause": "gesetzgebung", "effect": "verhaltenssteuerung", "strength": 0.70,
             "mechanism": "Rechtliche Normen setzen Anreize und Sanktionen"},
            {"cause": "rechtssicherheit", "effect": "investitionsbereitschaft", "strength": 0.75,
             "mechanism": "Vorhersehbare Rechtsfolgen ermöglichen Planung"},
            {"cause": "vertragsbruch", "effect": "schadensersatz", "strength": 0.85,
             "mechanism": "Zivilrechtliche Haftung bei Pflichtverletzung"},
            {"cause": "straftat", "effect": "sanktion", "strength": 0.90,
             "mechanism": "Strafrechtliche Konsequenzen bei Normverstößen"},
            {"cause": "beweislast", "effect": "prozessausgang", "strength": 0.65,
             "mechanism": "Wer nicht beweist, verliert"},
            {"cause": "präzedenzfall", "effect": "rechtsentwicklung", "strength": 0.60,
             "mechanism": "Richterrecht durch Leitentscheidungen"},
            {"cause": "grundrechte", "effect": "freiheitsschutz", "strength": 0.80,
             "mechanism": "Verfassungsrechtliche Abwehrrechte"},
            {"cause": "regulierung", "effect": "marktverhalten", "strength": 0.65,
             "mechanism": "Wirtschaftsrecht steuert Unternehmen"},
            {"cause": "datenschutz", "effect": "privatsphäre", "strength": 0.75,
             "mechanism": "Rechtliche Schranken für Datenverarbeitung"},
            {"cause": "haftung", "effect": "vorsicht", "strength": 0.70,
             "mechanism": "Schadensersatzrisiko fördert Sorgfalt"},
            {"cause": "vertragsfreiheit", "effect": "wirtschaftsverkehr", "strength": 0.80,
             "mechanism": "Autonome Gestaltung von Rechtsbeziehungen"},
            {"cause": "rechtsweg", "effect": "konfliktlösung", "strength": 0.75,
             "mechanism": "Gerichtliche Streitbeilegung"},
        ]

        # ETHIK
        self.domain_knowledge[CausalDomain.ETHIK] = [
            {"cause": "moralische_erziehung", "effect": "charakterbildung", "strength": 0.65,
             "mechanism": "Internalisierung ethischer Werte"},
            {"cause": "empathie", "effect": "prosoziales_verhalten", "strength": 0.75,
             "mechanism": "Einfühlung motiviert Hilfeverhalten"},
            {"cause": "gewissenskonflikt", "effect": "reflexion", "strength": 0.70,
             "mechanism": "Moralisches Dilemma erzwingt Nachdenken"},
            {"cause": "tugend", "effect": "glück", "strength": 0.55,
             "mechanism": "Eudaimonistische Ethik nach Aristoteles"},
            {"cause": "pflichtbewusstsein", "effect": "regelkonformität", "strength": 0.70,
             "mechanism": "Deontologische Motivation"},
            {"cause": "konsequenzbetrachtung", "effect": "entscheidung", "strength": 0.65,
             "mechanism": "Utilitaristische Nutzenabwägung"},
            {"cause": "wertpluralismus", "effect": "toleranz", "strength": 0.60,
             "mechanism": "Anerkennung unterschiedlicher Wertvorstellungen"},
            {"cause": "verantwortung", "effect": "nachhaltigkeit", "strength": 0.70,
             "mechanism": "Generationenübergreifende Ethik"},
            {"cause": "autonomie", "effect": "würde", "strength": 0.80,
             "mechanism": "Selbstbestimmung als Grundwert"},
            {"cause": "gerechtigkeit", "effect": "sozialer_friede", "strength": 0.75,
             "mechanism": "Faire Verteilung reduziert Konflikte"},
            {"cause": "integrität", "effect": "vertrauenswürdigkeit", "strength": 0.85,
             "mechanism": "Konsistenz zwischen Worten und Taten"},
            {"cause": "moralische_vorbilder", "effect": "verhaltensänderung", "strength": 0.60,
             "mechanism": "Modelllernen ethischen Verhaltens"},
        ]

        # KUNST
        self.domain_knowledge[CausalDomain.KUNST] = [
            {"cause": "kreativität", "effect": "innovation", "strength": 0.80,
             "mechanism": "Divergentes Denken erzeugt Neues"},
            {"cause": "übung", "effect": "kunstfertigkeit", "strength": 0.85,
             "mechanism": "Deliberate Practice verbessert Technik"},
            {"cause": "emotion", "effect": "ausdruck", "strength": 0.75,
             "mechanism": "Gefühle finden künstlerische Form"},
            {"cause": "kultureller_kontext", "effect": "stilentwicklung", "strength": 0.65,
             "mechanism": "Zeitgeist prägt künstlerische Strömungen"},
            {"cause": "patronage", "effect": "kunstproduktion", "strength": 0.70,
             "mechanism": "Finanzielle Förderung ermöglicht Schaffen"},
            {"cause": "technologie", "effect": "neue_kunstformen", "strength": 0.75,
             "mechanism": "Neue Medien eröffnen Ausdrucksmöglichkeiten"},
            {"cause": "tradition", "effect": "handwerk", "strength": 0.70,
             "mechanism": "Weitergabe von Techniken und Wissen"},
            {"cause": "provokation", "effect": "aufmerksamkeit", "strength": 0.60,
             "mechanism": "Grenzüberschreitung erzeugt Resonanz"},
            {"cause": "ästhetik", "effect": "wohlbefinden", "strength": 0.65,
             "mechanism": "Schönes wirkt positiv auf Psyche"},
            {"cause": "kunstkritik", "effect": "qualitätsbewusstsein", "strength": 0.55,
             "mechanism": "Diskurs schärft ästhetisches Urteil"},
            {"cause": "inspiration", "effect": "schaffensprozess", "strength": 0.80,
             "mechanism": "Anregung initiiert kreatives Handeln"},
            {"cause": "kunstausbildung", "effect": "professionalisierung", "strength": 0.70,
             "mechanism": "Systematische Vermittlung von Fähigkeiten"},
        ]

        # SPORT
        self.domain_knowledge[CausalDomain.SPORT] = [
            {"cause": "training", "effect": "leistung", "strength": 0.90,
             "mechanism": "Physiologische Anpassung durch Belastung"},
            {"cause": "ernährung", "effect": "regeneration", "strength": 0.75,
             "mechanism": "Nährstoffe für Muskelreparatur"},
            {"cause": "motivation", "effect": "trainingsintensität", "strength": 0.80,
             "mechanism": "Innerer Antrieb steigert Einsatz"},
            {"cause": "verletzung", "effect": "leistungseinbruch", "strength": 0.85,
             "mechanism": "Physische Schäden reduzieren Kapazität"},
            {"cause": "wettkampfdruck", "effect": "nervosität", "strength": 0.65,
             "mechanism": "Hohe Erwartungen erzeugen Stress"},
            {"cause": "teamgeist", "effect": "mannschaftsleistung", "strength": 0.70,
             "mechanism": "Kooperation potenziert Einzelleistungen"},
            {"cause": "taktik", "effect": "spielergebnis", "strength": 0.60,
             "mechanism": "Strategische Planung nutzt Stärken"},
            {"cause": "talent", "effect": "lerngeschwindigkeit", "strength": 0.70,
             "mechanism": "Genetische Prädisposition erleichtert Anpassung"},
            {"cause": "coaching", "effect": "technikverbesserung", "strength": 0.75,
             "mechanism": "Gezielte Anleitung optimiert Bewegungen"},
            {"cause": "doping", "effect": "kurzfristige_leistungssteigerung", "strength": 0.80,
             "mechanism": "Pharmakologische Manipulation der Physiologie"},
            {"cause": "schlaf", "effect": "erholung", "strength": 0.85,
             "mechanism": "Regenerative Prozesse im Schlaf"},
            {"cause": "mentales_training", "effect": "fokus", "strength": 0.65,
             "mechanism": "Visualisierung verbessert Konzentration"},
        ]

        # KOMMUNIKATION
        self.domain_knowledge[CausalDomain.KOMMUNIKATION] = [
            {"cause": "klarheit", "effect": "verständnis", "strength": 0.85,
             "mechanism": "Eindeutige Botschaften reduzieren Missverständnisse"},
            {"cause": "aktives_zuhören", "effect": "beziehungsqualität", "strength": 0.75,
             "mechanism": "Aufmerksamkeit signalisiert Wertschätzung"},
            {"cause": "nonverbale_signale", "effect": "emotionsübertragung", "strength": 0.70,
             "mechanism": "Mimik und Gestik transportieren Gefühle"},
            {"cause": "feedback", "effect": "verhaltensanpassung", "strength": 0.75,
             "mechanism": "Rückmeldung ermöglicht Korrektur"},
            {"cause": "medium", "effect": "botschaftswirkung", "strength": 0.60,
             "mechanism": "Kanal beeinflusst Interpretation (McLuhan)"},
            {"cause": "rauschen", "effect": "informationsverlust", "strength": 0.70,
             "mechanism": "Störungen degradieren Signalqualität"},
            {"cause": "rhetorik", "effect": "überzeugungskraft", "strength": 0.75,
             "mechanism": "Stilmittel verstärken Argumentwirkung"},
            {"cause": "kulturelle_unterschiede", "effect": "missverständnisse", "strength": 0.65,
             "mechanism": "Divergente Interpretationsrahmen"},
            {"cause": "vertrauen", "effect": "offenheit", "strength": 0.80,
             "mechanism": "Sicherheit ermöglicht authentische Kommunikation"},
            {"cause": "konflikt", "effect": "kommunikationsabbruch", "strength": 0.55,
             "mechanism": "Eskalation behindert Dialog"},
            {"cause": "empathische_kommunikation", "effect": "kooperation", "strength": 0.75,
             "mechanism": "Einfühlsame Sprache fördert Zusammenarbeit"},
            {"cause": "transparenz", "effect": "glaubwürdigkeit", "strength": 0.80,
             "mechanism": "Offenlegung stärkt Vertrauen"},
        ]

        # NEUROWISSENSCHAFT
        self.domain_knowledge[CausalDomain.NEUROWISSENSCHAFT] = [
            {"cause": "neurotransmitter", "effect": "stimmung", "strength": 0.80,
             "mechanism": "Chemische Botenstoffe modulieren Emotionen"},
            {"cause": "synaptische_plastizität", "effect": "lernen", "strength": 0.85,
             "mechanism": "Verstärkung neuronaler Verbindungen"},
            {"cause": "stress", "effect": "cortisol", "strength": 0.90,
             "mechanism": "HPA-Achsen-Aktivierung"},
            {"cause": "schlafmangel", "effect": "kognitive_defizite", "strength": 0.80,
             "mechanism": "Gestörte Gedächtniskonsolidierung"},
            {"cause": "neurodegeneration", "effect": "demenz", "strength": 0.85,
             "mechanism": "Verlust von Nervenzellen"},
            {"cause": "dopamin", "effect": "motivation", "strength": 0.75,
             "mechanism": "Belohnungssystem-Aktivierung"},
            {"cause": "serotonin", "effect": "wohlbefinden", "strength": 0.70,
             "mechanism": "Stimmungsregulation"},
            {"cause": "neuroinflammation", "effect": "kognitive_beeinträchtigung", "strength": 0.65,
             "mechanism": "Entzündliche Prozesse im Gehirn"},
            {"cause": "myelinisierung", "effect": "signalgeschwindigkeit", "strength": 0.90,
             "mechanism": "Isolation beschleunigt Nervenleitung"},
            {"cause": "neurogenese", "effect": "gehirnplastizität", "strength": 0.70,
             "mechanism": "Neue Nervenzellen im Hippocampus"},
            {"cause": "meditation", "effect": "gehirnstruktur", "strength": 0.55,
             "mechanism": "Strukturelle Veränderungen durch Training"},
            {"cause": "trauma", "effect": "amygdala_überaktivität", "strength": 0.75,
             "mechanism": "Sensibilisierung des Angstsystems"},
        ]

        # PHILOSOPHIE
        self.domain_knowledge[CausalDomain.PHILOSOPHIE] = [
            {"cause": "skeptizismus", "effect": "erkenntniskritik", "strength": 0.70,
             "mechanism": "Zweifel hinterfragt Gewissheiten"},
            {"cause": "logik", "effect": "argumentationsqualität", "strength": 0.85,
             "mechanism": "Formale Regeln sichern Gültigkeit"},
            {"cause": "dialektik", "effect": "synthese", "strength": 0.70,
             "mechanism": "These-Antithese-Aufhebung"},
            {"cause": "phänomenologie", "effect": "bewusstseinsanalyse", "strength": 0.65,
             "mechanism": "Beschreibung der Erscheinungsweisen"},
            {"cause": "hermeneutik", "effect": "textverständnis", "strength": 0.75,
             "mechanism": "Interpretationslehre erschließt Sinn"},
            {"cause": "existenzialismus", "effect": "authentizität", "strength": 0.60,
             "mechanism": "Selbstentwurf in Freiheit"},
            {"cause": "rationalismus", "effect": "a_priori_erkenntnis", "strength": 0.65,
             "mechanism": "Vernunft als Erkenntnisquelle"},
            {"cause": "empirismus", "effect": "erfahrungsbasiertes_wissen", "strength": 0.70,
             "mechanism": "Sinneserfahrung als Grundlage"},
            {"cause": "konstruktivismus", "effect": "realitätskonstruktion", "strength": 0.60,
             "mechanism": "Wirklichkeit als Konstrukt"},
            {"cause": "pragmatismus", "effect": "handlungsorientierung", "strength": 0.65,
             "mechanism": "Wahrheit durch Praxisrelevanz"},
            {"cause": "analytische_philosophie", "effect": "begriffsklärung", "strength": 0.80,
             "mechanism": "Sprachanalyse löst Probleme"},
            {"cause": "kritische_theorie", "effect": "gesellschaftskritik", "strength": 0.70,
             "mechanism": "Aufklärung über Herrschaftsstrukturen"},
        ]

        # LINGUISTIK
        self.domain_knowledge[CausalDomain.LINGUISTIK] = [
            {"cause": "spracherwerb", "effect": "kommunikationsfähigkeit", "strength": 0.90,
             "mechanism": "Erlernen sprachlicher Regeln"},
            {"cause": "input_frequenz", "effect": "wortschatzerwerb", "strength": 0.75,
             "mechanism": "Häufige Exposition festigt Lexikon"},
            {"cause": "grammatik", "effect": "satzbildung", "strength": 0.85,
             "mechanism": "Syntaktische Regeln strukturieren Sprache"},
            {"cause": "pragmatik", "effect": "kommunikationserfolg", "strength": 0.70,
             "mechanism": "Kontextangemessene Sprachverwendung"},
            {"cause": "sprachkontakt", "effect": "sprachwandel", "strength": 0.65,
             "mechanism": "Entlehnungen und Interferenzen"},
            {"cause": "schriftlichkeit", "effect": "standardisierung", "strength": 0.70,
             "mechanism": "Fixierung stabilisiert Normen"},
            {"cause": "soziolekt", "effect": "gruppenidentität", "strength": 0.60,
             "mechanism": "Sprachliche Marker signalisieren Zugehörigkeit"},
            {"cause": "metapher", "effect": "konzeptbildung", "strength": 0.65,
             "mechanism": "Bildliche Sprache strukturiert Denken"},
            {"cause": "mehrsprachigkeit", "effect": "kognitive_flexibilität", "strength": 0.60,
             "mechanism": "Sprachwechsel trainiert exekutive Funktionen"},
            {"cause": "sprachliche_relativität", "effect": "wahrnehmung", "strength": 0.45,
             "mechanism": "Sprache beeinflusst Weltsicht (Sapir-Whorf)"},
            {"cause": "diskurs", "effect": "wissenskonstruktion", "strength": 0.70,
             "mechanism": "Sprachliche Praktiken formen Wissen"},
            {"cause": "semantik", "effect": "bedeutungsverstehen", "strength": 0.80,
             "mechanism": "Lexikalische und kompositionelle Bedeutung"},
        ]

        # =================================================================
        # ERWEITERTE BEZIEHUNGEN FÜR BESTEHENDE DOMÄNEN
        # =================================================================

        # Erweiterte MEDIZIN-Beziehungen
        self.domain_knowledge[CausalDomain.MEDIZIN].extend([
            {"cause": "mikrobiom", "effect": "immunsystem", "strength": 0.70,
             "mechanism": "Darmbakterien trainieren Immunzellen"},
            {"cause": "entzündung", "effect": "chronische_krankheit", "strength": 0.65,
             "mechanism": "Persistente Inflammation schädigt Gewebe"},
            {"cause": "epigenetik", "effect": "genexpression", "strength": 0.75,
             "mechanism": "Umwelteinflüsse modifizieren Genaktivität"},
            {"cause": "telemedzin", "effect": "versorgungszugang", "strength": 0.65,
             "mechanism": "Fernbehandlung überbrückt Distanzen"},
            {"cause": "personalisierte_medizin", "effect": "therapieerfolg", "strength": 0.70,
             "mechanism": "Individuelle Behandlung nach Genotyp"},
        ])

        # Erweiterte PSYCHOLOGIE-Beziehungen
        self.domain_knowledge[CausalDomain.PSYCHOLOGIE].extend([
            {"cause": "attachment", "effect": "beziehungsfähigkeit", "strength": 0.75,
             "mechanism": "Frühe Bindungserfahrungen prägen Muster"},
            {"cause": "kognitive_umstrukturierung", "effect": "emotionsregulation", "strength": 0.70,
             "mechanism": "Neue Bewertungen ändern Gefühle"},
            {"cause": "flow", "effect": "intrinsische_motivation", "strength": 0.75,
             "mechanism": "Optimale Herausforderung erzeugt Engagement"},
            {"cause": "resilienzfaktoren", "effect": "stressbewältigung", "strength": 0.70,
             "mechanism": "Schutzfaktoren puffern Belastungen"},
            {"cause": "prokrastination", "effect": "leistungsdefizit", "strength": 0.65,
             "mechanism": "Aufschieben verhindert Zielerreichung"},
        ])

        # Erweiterte WIRTSCHAFT-Beziehungen
        self.domain_knowledge[CausalDomain.WIRTSCHAFT].extend([
            {"cause": "netzwerkeffekte", "effect": "monopolbildung", "strength": 0.70,
             "mechanism": "Nutzen steigt mit Nutzerzahl"},
            {"cause": "informationsasymmetrie", "effect": "marktversagen", "strength": 0.65,
             "mechanism": "Ungleiche Information verzerrt Transaktionen"},
            {"cause": "disruption", "effect": "branchenwandel", "strength": 0.75,
             "mechanism": "Radikale Innovation verdrängt Etablierte"},
            {"cause": "schuldenstand", "effect": "fiskalische_flexibilität", "strength": 0.70,
             "mechanism": "Hohe Verschuldung begrenzt Handlungsspielraum"},
            {"cause": "humankapital", "effect": "produktivitätswachstum", "strength": 0.75,
             "mechanism": "Qualifikation steigert Wertschöpfung"},
        ])

        # Erweiterte TECHNOLOGIE-Beziehungen
        self.domain_knowledge[CausalDomain.TECHNOLOGIE].extend([
            {"cause": "künstliche_intelligenz", "effect": "automatisierung", "strength": 0.80,
             "mechanism": "Maschinelles Lernen ersetzt Routineaufgaben"},
            {"cause": "blockchain", "effect": "dezentralisierung", "strength": 0.65,
             "mechanism": "Verteilte Ledger eliminieren Intermediäre"},
            {"cause": "quantencomputing", "effect": "kryptographie_wandel", "strength": 0.60,
             "mechanism": "Neue Rechenkapazitäten brechen Verschlüsselung"},
            {"cause": "iot", "effect": "datenexplosion", "strength": 0.75,
             "mechanism": "Vernetzte Geräte generieren Massendaten"},
            {"cause": "cloud_computing", "effect": "skalierbarkeit", "strength": 0.80,
             "mechanism": "Elastische Ressourcen on demand"},
        ])

        # =================================================================
        # VORDEFINIERTE KAUSALE KETTEN
        # =================================================================
        self._initialize_causal_chains()

    def _initialize_causal_chains(self):
        """Initialisiert vordefinierte komplexe kausale Ketten"""

        # Kette 1: Klimawandel-Kaskade
        self.causal_chains["climate_cascade"] = CausalChain(
            chain_id="climate_cascade",
            variables=["co2_emissionen", "klimawandel", "extremwetter",
                      "landwirtschaftsschäden", "nahrungsmittelknappheit", "migration"],
            domain=CausalDomain.UMWELT,
            total_strength=0.55,
            mechanisms=[
                "Treibhauseffekt verstärkt Erwärmung",
                "Erwärmung destabilisiert Wettersysteme",
                "Extremwetter zerstört Ernten",
                "Ernteausfälle reduzieren Nahrungsversorgung",
                "Mangel treibt Menschen zur Flucht"
            ],
            time_delays=[10.0, 5.0, 0.5, 1.0, 2.0],  # In Jahren
            is_reversible=False,
            confidence=0.75
        )

        # Kette 2: Bildungs-Wohlstands-Kette
        self.causal_chains["education_prosperity"] = CausalChain(
            chain_id="education_prosperity",
            variables=["frühförderung", "schulerfolg", "hochschulabschluss",
                      "qualifizierte_arbeit", "einkommen", "lebensqualität"],
            domain=CausalDomain.BILDUNG,
            total_strength=0.60,
            mechanisms=[
                "Frühe Förderung legt kognitive Grundlagen",
                "Schulische Leistungen ermöglichen höhere Bildung",
                "Akademische Qualifikation öffnet Berufswege",
                "Qualifizierte Arbeit wird besser entlohnt",
                "Höheres Einkommen verbessert Lebensstandard"
            ],
            time_delays=[5.0, 12.0, 5.0, 2.0, 1.0],
            is_reversible=False,
            confidence=0.70
        )

        # Kette 3: Stress-Krankheits-Spirale
        self.causal_chains["stress_disease"] = CausalChain(
            chain_id="stress_disease",
            variables=["chronischer_stress", "cortisol_erhöhung", "immunsuppression",
                      "infektanfälligkeit", "krankheit", "arbeitsausfall"],
            domain=CausalDomain.MEDIZIN,
            total_strength=0.65,
            mechanisms=[
                "Dauerhafte HPA-Achsen-Aktivierung",
                "Cortisol unterdrückt Immunantwort",
                "Geschwächte Abwehr erlaubt Infektionen",
                "Erkrankung beeinträchtigt Arbeitsfähigkeit",
                "Fehltage belasten Wirtschaft"
            ],
            time_delays=[0.5, 0.25, 0.5, 0.25, 0.1],  # In Jahren
            is_reversible=True,
            confidence=0.70
        )

        # Kette 4: Technologie-Disruption
        self.causal_chains["tech_disruption"] = CausalChain(
            chain_id="tech_disruption",
            variables=["innovation", "effizienzsteigerung", "kostensenkung",
                      "marktdurchdringung", "branchenwandel", "arbeitsmarktveränderung"],
            domain=CausalDomain.TECHNOLOGIE,
            total_strength=0.70,
            mechanisms=[
                "Neue Technologie verbessert Prozesse",
                "Effizienz senkt Produktionskosten",
                "Günstigere Preise erhöhen Nachfrage",
                "Massenadoption verändert Branche",
                "Strukturwandel erfordert neue Qualifikationen"
            ],
            time_delays=[2.0, 1.0, 2.0, 5.0, 3.0],
            is_reversible=False,
            confidence=0.75
        )

        # Kette 5: Demokratie-Entwicklung
        self.causal_chains["democracy_development"] = CausalChain(
            chain_id="democracy_development",
            variables=["bildung", "politische_partizipation", "demokratie",
                      "rechtssicherheit", "wirtschaftsentwicklung", "wohlstand"],
            domain=CausalDomain.POLITIK,
            total_strength=0.55,
            mechanisms=[
                "Gebildete Bürger engagieren sich politisch",
                "Partizipation stärkt demokratische Institutionen",
                "Demokratie garantiert Rechtsstaat",
                "Rechtssicherheit fördert Investitionen",
                "Wirtschaftswachstum hebt Lebensstandard"
            ],
            time_delays=[15.0, 10.0, 5.0, 5.0, 5.0],
            is_reversible=True,
            confidence=0.60
        )

        # Kette 6: Sucht-Spirale
        self.causal_chains["addiction_spiral"] = CausalChain(
            chain_id="addiction_spiral",
            variables=["substanzkonsum", "toleranzentwicklung", "dosissteigerung",
                      "abhängigkeit", "entzugssymptome", "rückfall"],
            domain=CausalDomain.PSYCHOLOGIE,
            total_strength=0.75,
            mechanisms=[
                "Regelmäßiger Konsum führt zu Gewöhnung",
                "Toleranz erfordert höhere Dosen",
                "Dauerkonsum verändert Hirnchemie",
                "Neurologische Anpassung erzeugt Entzug",
                "Entzugsleid motiviert erneuten Konsum"
            ],
            time_delays=[0.5, 0.5, 1.0, 0.1, 0.1],
            is_reversible=True,
            confidence=0.80
        )

        # Kette 7: Künstliche Intelligenz Evolution
        self.causal_chains["ai_evolution"] = CausalChain(
            chain_id="ai_evolution",
            variables=["datenmenge", "modelltraining", "leistungssteigerung",
                      "breitere_anwendung", "mehr_daten", "verbesserte_modelle"],
            domain=CausalDomain.TECHNOLOGIE,
            total_strength=0.80,
            mechanisms=[
                "Große Datenmengen ermöglichen Training",
                "Training verbessert Modellgenauigkeit",
                "Bessere Leistung erweitert Einsatzgebiete",
                "Mehr Anwendungen generieren neue Daten",
                "Neue Daten verbessern nächste Generation"
            ],
            time_delays=[0.5, 1.0, 0.5, 1.0, 1.0],
            is_reversible=False,
            confidence=0.85
        )

        # Kette 8: Urbanisierung
        self.causal_chains["urbanization"] = CausalChain(
            chain_id="urbanization",
            variables=["industrialisierung", "arbeitsmigration", "urbanisierung",
                      "infrastrukturausbau", "wirtschaftskonzentration", "landflucht"],
            domain=CausalDomain.SOZIALES,
            total_strength=0.70,
            mechanisms=[
                "Industriejobs ziehen Arbeitskräfte an",
                "Zuwanderung lässt Städte wachsen",
                "Städte bauen Verkehr und Versorgung aus",
                "Wirtschaftskraft konzentriert sich urban",
                "Ländliche Gebiete verlieren Bewohner"
            ],
            time_delays=[20.0, 10.0, 5.0, 10.0, 15.0],
            is_reversible=True,
            confidence=0.75
        )

        # Kette 9: Wissenschaftlicher Fortschritt
        self.causal_chains["scientific_progress"] = CausalChain(
            chain_id="scientific_progress",
            variables=["neugier", "forschung", "entdeckung", "publikation",
                      "replikation", "anwendung", "innovation"],
            domain=CausalDomain.BILDUNG,
            total_strength=0.65,
            mechanisms=[
                "Neugier motiviert systematische Untersuchung",
                "Forschung erzeugt neue Erkenntnisse",
                "Entdeckungen werden veröffentlicht",
                "Andere Forscher prüfen Ergebnisse",
                "Bestätigtes Wissen wird angewendet",
                "Anwendung führt zu praktischen Innovationen"
            ],
            time_delays=[1.0, 3.0, 0.5, 2.0, 3.0, 5.0],
            is_reversible=False,
            confidence=0.70
        )

        # Kette 10: Neurodegenerative Erkrankung
        self.causal_chains["neurodegeneration"] = CausalChain(
            chain_id="neurodegeneration",
            variables=["proteinaggregation", "zellstress", "neuroinflammation",
                      "synapsenverlust", "kognitive_beeinträchtigung", "demenz"],
            domain=CausalDomain.NEUROWISSENSCHAFT,
            total_strength=0.75,
            mechanisms=[
                "Fehlgefaltete Proteine bilden Aggregate",
                "Aggregate stressen Nervenzellen",
                "Stress aktiviert Immunzellen im Gehirn",
                "Entzündung schädigt Synapsen",
                "Synapsenverlust beeinträchtigt Kognition",
                "Fortschreitender Verlust führt zu Demenz"
            ],
            time_delays=[5.0, 3.0, 2.0, 3.0, 5.0, 10.0],
            is_reversible=False,
            confidence=0.70
        )

    def add_variable_with_domain(self, name: str, description: str,
                                   domain: CausalDomain,
                                   is_observable: bool = True) -> CausalNode:
        """Fügt eine Variable mit Domänen-Zuordnung hinzu"""
        node = self.add_variable(name, description, is_observable)
        self.variable_domains[name] = domain
        return node

    def get_domain_causal_knowledge(self, domain: CausalDomain) -> List[Dict]:
        """Gibt vordefiniertes Kausalwissen für eine Domäne zurück"""
        return self.domain_knowledge.get(domain, [])

    def apply_domain_knowledge(self, domain: CausalDomain) -> int:
        """
        Wendet vordefiniertes Domänen-Wissen an und erstellt
        entsprechende Variablen und Kanten.

        Returns:
            Anzahl der hinzugefügten Beziehungen
        """
        knowledge = self.domain_knowledge.get(domain, [])
        added = 0

        for rel in knowledge:
            cause = rel["cause"]
            effect = rel["effect"]
            strength = rel.get("strength", 0.5)
            mechanism = rel.get("mechanism", "")

            # Variablen hinzufügen wenn nicht vorhanden
            if cause not in self.nodes:
                self.add_variable_with_domain(cause, cause.replace("_", " ").title(), domain)
            if effect not in self.nodes:
                self.add_variable_with_domain(effect, effect.replace("_", " ").title(), domain)

            # Kausale Kante hinzufügen
            strength_enum = self._float_to_causal_strength(strength)
            if self.add_causal_link(cause, effect, strength_enum, mechanism):
                added += 1

        logger.info(f"Domänen-Wissen '{domain.value}' angewendet: {added} Beziehungen")
        return added

    def _float_to_causal_strength(self, strength: float) -> CausalStrength:
        """Konvertiert Float zu CausalStrength Enum"""
        if strength >= 0.9:
            return CausalStrength.DETERMINISTIC
        elif strength >= 0.7:
            return CausalStrength.STRONG
        elif strength >= 0.4:
            return CausalStrength.MODERATE
        elif strength >= 0.15:
            return CausalStrength.WEAK
        else:
            return CausalStrength.NEGLIGIBLE

    # =========================================================================
    # NEUE ERWEITERUNGEN: Mediator-Variablen
    # =========================================================================

    def add_mediator(self, cause: str, mediator: str, effect: str,
                      a_path: float = 0.5, b_path: float = 0.5,
                      direct_effect: float = 0.2) -> Optional[MediatorRelation]:
        """
        Fügt eine Mediator-Beziehung hinzu.

        A → M → B (Mediation)
        A ----→ B (direkter Effekt, kann 0 sein bei vollständiger Mediation)

        Args:
            cause: Ursprüngliche Ursache (A)
            mediator: Mediator-Variable (M)
            effect: Endeffekt (B)
            a_path: Stärke A → M
            b_path: Stärke M → B
            direct_effect: Direkter Effekt A → B (c')
        """
        # Sicherstellen, dass alle Variablen existieren
        for var in [cause, mediator, effect]:
            if var not in self.nodes:
                self.add_variable(var, var.replace("_", " ").title())

        # Kausale Links erstellen
        self.add_causal_link(cause, mediator, self._float_to_causal_strength(a_path))
        self.add_causal_link(mediator, effect, self._float_to_causal_strength(b_path))
        if direct_effect > 0.05:
            self.add_causal_link(cause, effect, self._float_to_causal_strength(direct_effect))

        # Berechnungen
        indirect_effect = a_path * b_path
        total_effect = direct_effect + indirect_effect
        proportion_mediated = indirect_effect / total_effect if total_effect > 0 else 0

        # Mediationstyp bestimmen
        if proportion_mediated > 0.9:
            med_type = MediatorType.FULL_MEDIATION
        elif (direct_effect > 0 and indirect_effect > 0 and
              (direct_effect * indirect_effect < 0)):
            med_type = MediatorType.INCONSISTENT
        else:
            med_type = MediatorType.PARTIAL_MEDIATION

        relation = MediatorRelation(
            cause=cause,
            mediator=mediator,
            effect=effect,
            mediation_type=med_type,
            indirect_effect=indirect_effect,
            direct_effect=direct_effect,
            total_effect=total_effect,
            proportion_mediated=proportion_mediated
        )

        self.mediators.append(relation)
        logger.debug(f"Mediator hinzugefügt: {cause} → {mediator} → {effect} "
                    f"(Proportion: {proportion_mediated:.2f})")
        return relation

    def find_mediators_for(self, cause: str, effect: str) -> List[MediatorRelation]:
        """Findet alle Mediatoren zwischen Ursache und Effekt"""
        return [m for m in self.mediators
                if m.cause == cause and m.effect == effect]

    def explain_mediation(self, relation: MediatorRelation) -> str:
        """Erklärt eine Mediations-Beziehung in natürlicher Sprache"""
        explanation = [
            f"Mediation: {relation.cause} → {relation.mediator} → {relation.effect}",
            f"",
            f"  • Indirekter Effekt (über {relation.mediator}): {relation.indirect_effect:.3f}",
            f"  • Direkter Effekt: {relation.direct_effect:.3f}",
            f"  • Gesamteffekt: {relation.total_effect:.3f}",
            f"  • Anteil mediiert: {relation.proportion_mediated:.1%}",
            f"  • Typ: {relation.mediation_type.value}",
        ]

        if relation.mediation_type == MediatorType.FULL_MEDIATION:
            explanation.append(f"  → '{relation.mediator}' erklärt fast den gesamten Effekt!")
        elif relation.mediation_type == MediatorType.INCONSISTENT:
            explanation.append(f"  ⚠ Inkonsistente Mediation: Direkter und indirekter Effekt "
                             f"haben unterschiedliche Richtungen!")

        return "\n".join(explanation)

    # =========================================================================
    # NEUE ERWEITERUNGEN: Moderator-Variablen
    # =========================================================================

    def add_moderator(self, cause: str, effect: str, moderator: str,
                       base_strength: float = 0.5,
                       interaction: float = 0.3) -> Optional[ModeratorRelation]:
        """
        Fügt eine Moderator-Beziehung hinzu.

        Ein Moderator verändert die Stärke der Beziehung zwischen
        Ursache und Effekt, ohne selbst ein Mediator zu sein.

        Args:
            cause: Ursache
            effect: Effekt
            moderator: Moderator-Variable
            base_strength: Basis-Effektstärke ohne Moderator
            interaction: Interaktionskoeffizient (positiv = verstärkt, negativ = puffert)
        """
        # Variablen erstellen
        for var in [cause, effect, moderator]:
            if var not in self.nodes:
                self.add_variable(var, var.replace("_", " ").title())

        # Basis-Link erstellen
        self.add_causal_link(cause, effect, self._float_to_causal_strength(base_strength))

        # Berechne modulierte Stärke (bei Moderator = 1)
        moderated_strength = base_strength + interaction
        moderated_strength = max(0.0, min(1.0, moderated_strength))

        # Moderator-Effekt bestimmen
        if interaction > 0.1:
            mod_effect = ModeratorEffect.ENHANCING
        elif interaction < -0.1:
            mod_effect = ModeratorEffect.BUFFERING
        else:
            mod_effect = ModeratorEffect.ANTAGONISTIC  # Schwacher oder wechselnder Effekt

        relation = ModeratorRelation(
            cause=cause,
            effect=effect,
            moderator=moderator,
            moderator_effect=mod_effect,
            base_strength=base_strength,
            moderated_strength=moderated_strength,
            interaction_coefficient=interaction
        )

        self.moderators.append(relation)
        logger.debug(f"Moderator hinzugefügt: {moderator} moderiert {cause} → {effect}")
        return relation

    def find_moderators_for(self, cause: str, effect: str) -> List[ModeratorRelation]:
        """Findet alle Moderatoren für eine Beziehung"""
        return [m for m in self.moderators
                if m.cause == cause and m.effect == effect]

    def explain_moderation(self, relation: ModeratorRelation) -> str:
        """Erklärt eine Moderations-Beziehung in natürlicher Sprache"""
        explanation = [
            f"Moderation: {relation.moderator} beeinflusst {relation.cause} → {relation.effect}",
            f"",
            f"  • Basis-Effektstärke: {relation.base_strength:.3f}",
            f"  • Modulierte Stärke: {relation.moderated_strength:.3f}",
            f"  • Interaktionskoeffizient: {relation.interaction_coefficient:+.3f}",
            f"  • Moderationsart: {relation.moderator_effect.value}",
        ]

        if relation.moderator_effect == ModeratorEffect.ENHANCING:
            explanation.append(f"  → Wenn '{relation.moderator}' hoch ist, wird der Effekt verstärkt!")
        elif relation.moderator_effect == ModeratorEffect.BUFFERING:
            explanation.append(f"  → Wenn '{relation.moderator}' hoch ist, wird der Effekt abgepuffert!")

        return "\n".join(explanation)

    # =========================================================================
    # NEUE ERWEITERUNGEN: Komplexe Kausale Ketten
    # =========================================================================

    def create_causal_chain(self, chain_id: str, variables: List[str],
                             domain: CausalDomain = CausalDomain.ALLGEMEIN,
                             mechanisms: List[str] = None,
                             time_delays: List[float] = None,
                             strengths: List[float] = None) -> Optional[CausalChain]:
        """
        Erstellt eine vollständige kausale Kette.

        Args:
            chain_id: Eindeutige ID der Kette
            variables: Liste der Variablen in Reihenfolge [A, B, C, ...] → A→B→C→...
            domain: Domäne der Kette
            mechanisms: Mechanismen für jeden Übergang
            time_delays: Zeitverzögerungen zwischen Variablen
            strengths: Stärken der einzelnen Verbindungen
        """
        if len(variables) < 2:
            logger.warning("Kausale Kette benötigt mindestens 2 Variablen")
            return None

        # Defaults
        n_links = len(variables) - 1
        mechanisms = mechanisms or ["" for _ in range(n_links)]
        time_delays = time_delays or [0.0 for _ in range(n_links)]
        strengths = strengths or [0.5 for _ in range(n_links)]

        # Variablen und Links erstellen
        for i, var in enumerate(variables):
            if var not in self.nodes:
                self.add_variable_with_domain(var, var.replace("_", " ").title(), domain)

        for i in range(n_links):
            cause = variables[i]
            effect = variables[i + 1]
            strength = self._float_to_causal_strength(strengths[i])
            mechanism = mechanisms[i] if i < len(mechanisms) else ""

            self.add_causal_link(cause, effect, strength, mechanism)

            # Zeitverzögerung speichern
            if time_delays and i < len(time_delays):
                self.temporal_delays[(cause, effect)] = time_delays[i]

        # Gesamtstärke berechnen (Produkt)
        total_strength = 1.0
        for s in strengths:
            total_strength *= s

        chain = CausalChain(
            chain_id=chain_id,
            variables=variables,
            domain=domain,
            total_strength=total_strength,
            mechanisms=mechanisms,
            time_delays=time_delays,
            is_reversible=False,
            confidence=0.5 + 0.3 * (1 - abs(total_strength - 0.5))
        )

        self.causal_chains[chain_id] = chain
        logger.info(f"Kausale Kette erstellt: {chain_id} mit {len(variables)} Variablen")
        return chain

    def get_chain_strength(self, start: str, end: str) -> float:
        """
        Berechnet die aggregierte kausale Stärke zwischen zwei Variablen.
        Berücksichtigt alle Pfade und deren Stärken.
        """
        paths = self.trace_causal_chain(start, end)
        if not paths:
            return 0.0

        # Für jeden Pfad: Produktregel für Stärken
        path_strengths = []
        for path in paths:
            strength = 1.0
            for i in range(len(path) - 1):
                cause, effect = path[i], path[i + 1]
                # Finde die Kante
                for edge in self.edges:
                    if edge.cause == cause and edge.effect == effect:
                        edge_strength = edge.strength.value if isinstance(edge.strength, CausalStrength) else edge.strength
                        strength *= edge_strength
                        break
            path_strengths.append(strength)

        # Aggregation: Maximale Stärke oder gewichtete Summe
        # Hier: Maximum (stärkster Pfad dominiert)
        return max(path_strengths) if path_strengths else 0.0

    def get_total_time_delay(self, start: str, end: str) -> Optional[float]:
        """
        Berechnet die totale Zeitverzögerung über den kürzesten Pfad.
        """
        paths = self.trace_causal_chain(start, end)
        if not paths:
            return None

        # Kürzeste Verzögerung
        min_delay = float('inf')

        for path in paths:
            delay = 0.0
            for i in range(len(path) - 1):
                key = (path[i], path[i + 1])
                delay += self.temporal_delays.get(key, 0.0)
            min_delay = min(min_delay, delay)

        return min_delay if min_delay != float('inf') else None

    def explain_causal_chain(self, chain: CausalChain) -> str:
        """Erklärt eine kausale Kette in natürlicher Sprache"""
        explanation = [
            f"Kausale Kette: {chain.chain_id}",
            f"Domäne: {chain.domain.value}",
            f"",
            f"Pfad: {' → '.join(chain.variables)}",
            f"",
            f"Mechanismen:",
        ]

        for i, mechanism in enumerate(chain.mechanisms):
            if i < len(chain.variables) - 1:
                explanation.append(f"  {chain.variables[i]} → {chain.variables[i+1]}: {mechanism or '(nicht spezifiziert)'}")

        if chain.time_delays:
            explanation.append(f"")
            explanation.append(f"Zeitverzögerungen:")
            total_delay = 0
            for i, delay in enumerate(chain.time_delays):
                if i < len(chain.variables) - 1:
                    explanation.append(f"  {chain.variables[i]} → {chain.variables[i+1]}: {delay} Einheiten")
                    total_delay += delay
            explanation.append(f"  Gesamt: {total_delay} Einheiten")

        explanation.append(f"")
        explanation.append(f"Gesamtstärke: {chain.total_strength:.3f}")
        explanation.append(f"Konfidenz: {chain.confidence:.1%}")

        return "\n".join(explanation)

    # =========================================================================
    # NEUE ERWEITERUNGEN: Feedback-Loops (Zyklische Kausalität)
    # =========================================================================

    def add_feedback_loop(self, variables: List[str],
                           strengths: List[float] = None,
                           loop_type: str = "positive") -> bool:
        """
        Fügt einen Feedback-Loop hinzu (zyklische Kausalität).

        A → B → C → A (geschlossener Kreis)

        Args:
            variables: Liste der Variablen im Loop (letztes Element führt zum ersten)
            strengths: Stärken der Verbindungen
            loop_type: "positive" (verstärkend) oder "negative" (stabilisierend)
        """
        if len(variables) < 2:
            return False

        # Defaults
        strengths = strengths or [0.5 for _ in variables]

        # Variablen erstellen
        for var in variables:
            if var not in self.nodes:
                self.add_variable(var, var.replace("_", " ").title())

        # Temporär Zyklenprüfung deaktivieren für Feedback-Loops
        # Speichere den Loop und füge Edges manuell hinzu
        loop_edges = []
        for i in range(len(variables)):
            cause = variables[i]
            effect = variables[(i + 1) % len(variables)]  # Zyklisch

            edge = CausalEdge(
                cause=cause,
                effect=effect,
                strength=self._float_to_causal_strength(strengths[i] if i < len(strengths) else 0.5),
                mechanism=f"Feedback-Loop ({loop_type})",
                is_direct=True
            )
            loop_edges.append(edge)

        # Edges zum Graphen hinzufügen
        self.edges.extend(loop_edges)

        # Loop registrieren
        self.feedback_loops.append(variables)

        logger.info(f"Feedback-Loop hinzugefügt: {' → '.join(variables)} → {variables[0]} ({loop_type})")
        return True

    def detect_feedback_loops(self) -> List[List[str]]:
        """
        Erkennt alle Feedback-Loops im kausalen Graphen.

        Returns:
            Liste von Zyklen (jeder Zyklus ist eine Liste von Variablen)
        """
        detected_loops = []
        visited = set()
        rec_stack = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.append(node)

            for edge in self.edges:
                if edge.cause == node:
                    neighbor = edge.effect
                    if neighbor in rec_stack:
                        # Zyklus gefunden
                        cycle_start = rec_stack.index(neighbor)
                        cycle = rec_stack[cycle_start:] + [neighbor]
                        if cycle not in detected_loops:
                            detected_loops.append(cycle)
                    elif neighbor not in visited:
                        dfs(neighbor, path + [neighbor])

            rec_stack.pop()
            return False

        for node in self.nodes:
            if node not in visited:
                dfs(node, [node])

        return detected_loops

    def explain_feedback_loop(self, loop: List[str]) -> str:
        """Erklärt einen Feedback-Loop in natürlicher Sprache"""
        # Bestimme Typ (positiv/negativ)
        total_sign = 1
        explanations = []

        for i in range(len(loop) - 1):
            cause = loop[i]
            effect = loop[i + 1]
            for edge in self.edges:
                if edge.cause == cause and edge.effect == effect:
                    strength = edge.strength.value if isinstance(edge.strength, CausalStrength) else edge.strength
                    explanations.append(f"  {cause} → {effect} (Stärke: {strength:.2f})")
                    break

        # Vollständiger Kreis
        cycle_str = " → ".join(loop)

        loop_type = "positiver (verstärkender)" if total_sign > 0 else "negativer (stabilisierender)"

        return f"""Feedback-Loop ({loop_type} Zyklus):
{cycle_str}

Verbindungen:
{chr(10).join(explanations)}

Bedeutung: Änderungen in '{loop[0]}' wirken über den gesamten Zyklus
auf sich selbst zurück, was zu {"Verstärkung" if total_sign > 0 else "Stabilisierung"} führt."""

    # =========================================================================
    # NEUE ERWEITERUNGEN: Erweiterte Analyse
    # =========================================================================

    def identify_key_nodes(self) -> Dict[str, Dict[str, Any]]:
        """
        Identifiziert Schlüsselknoten im kausalen Graphen.

        Returns:
            Dict mit Knotenname und deren Eigenschaften
        """
        key_nodes = {}

        for node in self.nodes:
            # Zähle ein- und ausgehende Kanten
            incoming = sum(1 for e in self.edges if e.effect == node)
            outgoing = sum(1 for e in self.edges if e.cause == node)

            # Ist Teil eines Feedback-Loops?
            in_loop = any(node in loop for loop in self.feedback_loops)

            # Ist Mediator?
            is_mediator = any(m.mediator == node for m in self.mediators)

            # Ist Moderator?
            is_moderator = any(m.moderator == node for m in self.moderators)

            # Berechne Zentralität (vereinfacht)
            centrality = (incoming + outgoing) / max(1, len(self.edges))

            role = "normal"
            if incoming == 0 and outgoing > 0:
                role = "root_cause"  # Ursprüngliche Ursache
            elif outgoing == 0 and incoming > 0:
                role = "outcome"  # Endpunkt
            elif incoming > 2 and outgoing > 2:
                role = "hub"  # Zentraler Knoten
            elif is_mediator:
                role = "mediator"
            elif is_moderator:
                role = "moderator"
            elif in_loop:
                role = "feedback_participant"

            key_nodes[node] = {
                "incoming_edges": incoming,
                "outgoing_edges": outgoing,
                "centrality": centrality,
                "role": role,
                "in_feedback_loop": in_loop,
                "is_mediator": is_mediator,
                "is_moderator": is_moderator,
                "domain": self.variable_domains.get(node, CausalDomain.ALLGEMEIN).value
            }

        return key_nodes

    def get_causal_summary(self) -> str:
        """Gibt eine umfassende Zusammenfassung des kausalen Modells"""
        summary = [
            "=" * 60,
            "ERWEITERTES KAUSALES MODELL - Zusammenfassung",
            "=" * 60,
            f"",
            f"Variablen: {len(self.nodes)}",
            f"Kausale Beziehungen: {len(self.edges)}",
            f"Kausale Ketten: {len(self.causal_chains)}",
            f"Mediator-Beziehungen: {len(self.mediators)}",
            f"Moderator-Beziehungen: {len(self.moderators)}",
            f"Feedback-Loops: {len(self.feedback_loops)}",
        ]

        # Domänen-Verteilung
        domain_counts = defaultdict(int)
        for domain in self.variable_domains.values():
            domain_counts[domain.value] += 1
        if domain_counts:
            summary.append(f"")
            summary.append(f"Domänen-Verteilung:")
            for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
                summary.append(f"  • {domain}: {count} Variablen")

        # Schlüsselknoten
        key_nodes = self.identify_key_nodes()
        roots = [n for n, info in key_nodes.items() if info["role"] == "root_cause"]
        outcomes = [n for n, info in key_nodes.items() if info["role"] == "outcome"]
        hubs = [n for n, info in key_nodes.items() if info["role"] == "hub"]

        if roots:
            summary.append(f"")
            summary.append(f"Ursprüngliche Ursachen: {', '.join(roots[:5])}")
        if outcomes:
            summary.append(f"Endpunkte: {', '.join(outcomes[:5])}")
        if hubs:
            summary.append(f"Zentrale Hubs: {', '.join(hubs[:5])}")

        # Feedback-Loops
        if self.feedback_loops:
            summary.append(f"")
            summary.append(f"Feedback-Loops:")
            for loop in self.feedback_loops[:3]:
                summary.append(f"  • {' → '.join(loop)} → ...")

        return "\n".join(summary)

    def get_intervention_recommendations(self, target_effect: str) -> List[Dict[str, Any]]:
        """
        Gibt Empfehlungen für Interventionen, um einen Zieleffekt zu erreichen.

        Args:
            target_effect: Die Variable, die beeinflusst werden soll

        Returns:
            Liste von Interventionsempfehlungen mit erwarteter Wirksamkeit
        """
        if target_effect not in self.nodes:
            return []

        recommendations = []

        # Finde alle Ursachen
        all_causes = set()
        ancestors = self._get_ancestors(target_effect)

        for ancestor in ancestors:
            # Berechne Stärke des Einflusses
            strength = self.get_chain_strength(ancestor, target_effect)

            # Prüfe ob direkt beeinflussbar (keine eingehenden Kanten = root cause)
            incoming = sum(1 for e in self.edges if e.effect == ancestor)
            is_root = incoming == 0

            # Prüfe Zeitverzögerung
            delay = self.get_total_time_delay(ancestor, target_effect)

            # Prüfe ob über Mediator
            relevant_mediators = [m for m in self.mediators
                                 if m.cause == ancestor and m.effect == target_effect]

            recommendations.append({
                "intervention_point": ancestor,
                "expected_effect_strength": strength,
                "is_root_cause": is_root,
                "time_delay": delay,
                "has_mediator": len(relevant_mediators) > 0,
                "mediators": [m.mediator for m in relevant_mediators],
                "priority": strength * (1.2 if is_root else 1.0) / (1 + (delay or 0) * 0.1)
            })

        # Nach Priorität sortieren
        recommendations.sort(key=lambda x: x["priority"], reverse=True)

        return recommendations


# =============================================================================
# 3. METACOGNITIVE REASONING - Denken über Denken
# =============================================================================
#
# HINWEIS: Für System-weite Meta-Beobachtung nutze holo_meta_cognition.HoloMetaObserver.
# Diese Klasse fokussiert auf die Metakognition des Reasoning-Prozesses selbst.
#
# Integration:
# - MetacognitiveReasoner: Überwacht Denkprozesse (Biases, Konfidenz, Strategien)
# - HoloMetaObserver: Überwacht System-Komponenten (Aufrufe, Muster, Kausalität)
#
# Beide können zusammenarbeiten für vollständige Meta-Kognition.
# =============================================================================

class MetacognitiveReasoner:
    """
    Metakognition - Denken über das eigene Denken.

    KONSOLIDIERT: Integriert mit HoloMetaObserver aus holo_meta_cognition.py
    für System-weite Meta-Beobachtung.

    Implementiert:
    - Monitoring: Beobachten des eigenen Denkprozesses
    - Evaluation: Bewerten der Denkqualität
    - Regulation: Anpassen der Denkstrategie
    - Reflection: Tiefe Selbstreflexion

    Für System-weite Beobachtung siehe:
    - holo_meta_cognition.HoloMetaObserver
    """

    def __init__(self, meta_observer: 'HoloMetaObserver' = None):
        self.thinking_traces: List[ThinkingTrace] = []
        self.current_confidence: float = 0.5
        self.known_biases: List[str] = []
        self.strategy_performance: Dict[str, List[float]] = defaultdict(list)
        self.reflection_journal: List[Dict] = []

        # Integration mit HoloMetaObserver
        self._meta_observer = meta_observer
        if self._meta_observer is None and _HAS_META_COGNITION and HoloMetaObserver is not None:
            try:
                self._meta_observer = HoloMetaObserver()
                logger.info("[MetacognitiveReasoner] Nutzt HoloMetaObserver für System-Beobachtung")
            except Exception as e:
                logger.debug(f"[MetacognitiveReasoner] HoloMetaObserver nicht verfügbar: {e}")

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

        # Beobachte auch im HoloMetaObserver wenn verfügbar
        if self._meta_observer is not None and ObservationType is not None:
            try:
                self._meta_observer.observe(
                    observation_type=ObservationType.DECISION,
                    component="MetacognitiveReasoner",
                    action=f"start_monitoring:{reasoning_mode.value}",
                    context={"step_id": step_id, "input_keys": list(input_state.keys())},
                )
            except Exception:
                pass

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

            # Beobachte auch im HoloMetaObserver wenn verfügbar
            if self._meta_observer is not None and ObservationType is not None:
                try:
                    self._meta_observer.observe(
                        observation_type=ObservationType.DECISION,
                        component="MetacognitiveReasoner",
                        action=f"end_monitoring:{trace.reasoning_mode.value}",
                        context={"step_id": step_id, "output_keys": list(output_state.keys())},
                        outcome=f"confidence={confidence:.2f}",
                        success=confidence > 0.5,
                        duration_ms=duration_ms,
                    )
                except Exception:
                    pass

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

    def get_system_observation_history(self, limit: int = 50) -> List[Dict]:
        """
        Gibt System-weite Beobachtungen aus HoloMetaObserver zurück.

        KONSOLIDIERT: Nutzt HoloMetaObserver für System-weite Beobachtungen.

        Args:
            limit: Maximale Anzahl zurückgegebener Beobachtungen

        Returns:
            Liste von Beobachtungen aus dem Meta-System
        """
        if self._meta_observer is not None:
            try:
                return self._meta_observer.get_observation_history(
                    component="MetacognitiveReasoner",
                    limit=limit
                )
            except Exception as e:
                logger.debug(f"[MetacognitiveReasoner] Konnte History nicht laden: {e}")
        return []

    def get_combined_insight(self) -> Dict[str, Any]:
        """
        Kombiniert lokale Metakognition mit System-weiter Beobachtung.

        KONSOLIDIERT: Vereint MetacognitiveReasoner und HoloMetaObserver Einsichten.
        """
        result = {
            "reasoning_quality": self.evaluate_reasoning_quality(),
            "biases_detected": list(set(self.known_biases)),
            "thinking_steps": len(self.thinking_traces),
            "strategy_suggestion": self.suggest_strategy_change(),
        }

        # Füge System-Beobachtungen hinzu wenn verfügbar
        if self._meta_observer is not None:
            try:
                history = self._meta_observer.get_observation_history(limit=10)
                result["system_observations"] = len(history)
                result["meta_observer_active"] = True
            except Exception:
                result["meta_observer_active"] = False
        else:
            result["meta_observer_active"] = False

        return result


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
# 5. ABDUCTIVE REASONING - Schluss auf die beste Erklärung
# =============================================================================

class AbductiveReasoner:
    """
    Abduktives Reasoning - Inference to the Best Explanation (IBE).

    Prozess:
    1. Beobachtung eines Phänomens
    2. Generierung möglicher Erklärungen (Hypothesen)
    3. Bewertung der Hypothesen nach Kriterien
    4. Auswahl der besten Erklärung

    Bewertungskriterien:
    - Plausibilität: Passt die Erklärung zum bekannten Wissen?
    - Einfachheit: Ockhams Rasiermesser
    - Erklärungsweite: Wie viele Phänomene erklärt die Hypothese?
    - Kohärenz: Konsistenz mit anderen Überzeugungen
    - Testbarkeit: Kann die Hypothese falsifiziert werden?
    """

    def __init__(self):
        self.observations: List[Observation] = []
        self.hypotheses: Dict[str, AbductiveHypothesis] = {}
        self.inference_history: List[InferenceToTheBestExplanation] = []
        self.domain_priors: Dict[str, float] = {}  # Domänenspezifische Prior-Wahrscheinlichkeiten
        self._hypothesis_counter = 0

    def add_observation(self, description: str, reliability: float = 0.8,
                        context: Dict[str, Any] = None, source: str = "") -> Observation:
        """
        Fügt eine zu erklärende Beobachtung hinzu.

        Args:
            description: Beschreibung des beobachteten Phänomens
            reliability: Zuverlässigkeit der Beobachtung (0-1)
            context: Zusätzlicher Kontext
            source: Quelle der Beobachtung
        """
        obs = Observation(
            description=description,
            reliability=min(1.0, max(0.0, reliability)),
            context=context or {},
            source=source
        )
        self.observations.append(obs)
        logger.debug(f"[AbductiveReasoner] Neue Beobachtung: {description[:50]}...")
        return obs

    def generate_hypothesis(self, content: str,
                            hypothesis_type: AbductiveHypothesisType = AbductiveHypothesisType.CAUSAL,
                            explains: List[str] = None,
                            plausibility: float = 0.5,
                            simplicity: float = 0.5,
                            prior: float = 0.5) -> AbductiveHypothesis:
        """
        Generiert eine abduktive Hypothese.

        Args:
            content: Inhalt der Hypothese
            hypothesis_type: Art der Erklärung
            explains: Liste von Beobachtungs-Beschreibungen, die erklärt werden
            plausibility: A-priori Plausibilität
            simplicity: Einfachheit der Erklärung
            prior: Prior-Wahrscheinlichkeit
        """
        self._hypothesis_counter += 1
        h_id = f"H{self._hypothesis_counter}"

        # Berechne Scope basierend auf erklärten Beobachtungen
        explains = explains or []
        scope = len(explains) / max(len(self.observations), 1) if self.observations else 0.5

        hypothesis = AbductiveHypothesis(
            hypothesis_id=h_id,
            content=content,
            hypothesis_type=hypothesis_type,
            explains=explains,
            plausibility=plausibility,
            simplicity=simplicity,
            scope=scope,
            coherence=0.5,  # Wird später berechnet
            testability=0.5,  # Wird später berechnet
            prior_probability=prior
        )

        self.hypotheses[h_id] = hypothesis
        logger.debug(f"[AbductiveReasoner] Neue Hypothese {h_id}: {content[:50]}...")
        return hypothesis

    def add_supporting_evidence(self, hypothesis_id: str, evidence: str):
        """Fügt unterstützende Evidenz für eine Hypothese hinzu"""
        if hypothesis_id in self.hypotheses:
            self.hypotheses[hypothesis_id].supporting_evidence.append(evidence)
            # Erhöhe Plausibilität leicht
            h = self.hypotheses[hypothesis_id]
            h.plausibility = min(1.0, h.plausibility + 0.05)

    def add_counter_evidence(self, hypothesis_id: str, evidence: str):
        """Fügt Gegenbeweise für eine Hypothese hinzu"""
        if hypothesis_id in self.hypotheses:
            self.hypotheses[hypothesis_id].counter_evidence.append(evidence)
            # Senke Plausibilität
            h = self.hypotheses[hypothesis_id]
            h.plausibility = max(0.0, h.plausibility - 0.10)

    def evaluate_coherence(self, hypothesis: AbductiveHypothesis,
                            background_beliefs: List[str] = None) -> float:
        """
        Bewertet die Kohärenz einer Hypothese mit Hintergrundwissen.

        Args:
            hypothesis: Die zu bewertende Hypothese
            background_beliefs: Liste von Hintergrund-Überzeugungen
        """
        if not background_beliefs:
            return 0.5  # Neutral wenn kein Hintergrundwissen

        # Einfache Wortüberlappung als Proxy für Kohärenz
        h_words = set(hypothesis.content.lower().split())
        coherence_scores = []

        for belief in background_beliefs:
            belief_words = set(belief.lower().split())
            overlap = len(h_words.intersection(belief_words))
            total = len(h_words.union(belief_words))
            if total > 0:
                coherence_scores.append(overlap / total)

        if coherence_scores:
            hypothesis.coherence = sum(coherence_scores) / len(coherence_scores)
        else:
            hypothesis.coherence = 0.5

        return hypothesis.coherence

    def evaluate_testability(self, hypothesis: AbductiveHypothesis) -> float:
        """
        Bewertet die Testbarkeit/Falsifizierbarkeit einer Hypothese.

        Heuristiken:
        - Spezifische Vorhersagen erhöhen Testbarkeit
        - Vage Aussagen senken Testbarkeit
        """
        content = hypothesis.content.lower()

        # Indikatoren für hohe Testbarkeit
        testable_indicators = [
            "wenn", "dann", "führt zu", "verursacht", "resultiert in",
            "messbar", "beobachtbar", "vorhersagt", "spezifisch"
        ]

        # Indikatoren für niedrige Testbarkeit
        vague_indicators = [
            "vielleicht", "möglicherweise", "irgendwie", "könnte sein",
            "unbekannt", "mysteriös", "immer", "niemals", "alle"
        ]

        testable_count = sum(1 for ind in testable_indicators if ind in content)
        vague_count = sum(1 for ind in vague_indicators if ind in content)

        # Basis-Testbarkeit
        testability = 0.5

        # Anpassungen
        testability += testable_count * 0.1
        testability -= vague_count * 0.1

        # Kausale und strukturelle Hypothesen sind oft besser testbar
        if hypothesis.hypothesis_type in [AbductiveHypothesisType.CAUSAL,
                                          AbductiveHypothesisType.STRUCTURAL]:
            testability += 0.1

        hypothesis.testability = min(1.0, max(0.0, testability))
        return hypothesis.testability

    def infer_best_explanation(self, observations: List[Observation] = None,
                                top_n: int = 3) -> InferenceToTheBestExplanation:
        """
        Führt Inference to the Best Explanation durch.

        Args:
            observations: Zu erklärende Beobachtungen (oder alle gespeicherten)
            top_n: Anzahl der besten Hypothesen im Ranking

        Returns:
            IBE-Ergebnis mit Ranking der Hypothesen
        """
        observations = observations or self.observations

        if not observations:
            logger.warning("[AbductiveReasoner] Keine Beobachtungen für IBE")
            return InferenceToTheBestExplanation(
                observations=[],
                hypotheses=[],
                best_hypothesis=None,
                ranking=[],
                confidence=0.0,
                reasoning_trace=["Keine Beobachtungen vorhanden"]
            )

        if not self.hypotheses:
            logger.warning("[AbductiveReasoner] Keine Hypothesen für IBE")
            return InferenceToTheBestExplanation(
                observations=observations,
                hypotheses=[],
                best_hypothesis=None,
                ranking=[],
                confidence=0.0,
                reasoning_trace=["Keine Hypothesen generiert"]
            )

        reasoning_trace = []
        reasoning_trace.append(f"Starte IBE mit {len(observations)} Beobachtungen und "
                              f"{len(self.hypotheses)} Hypothesen")

        # Berechne Scores für alle Hypothesen
        scores: List[Tuple[str, float]] = []

        for h_id, hypothesis in self.hypotheses.items():
            # Evaluiere Kohärenz und Testbarkeit
            self.evaluate_testability(hypothesis)

            # Berechne Gesamtscore
            score = hypothesis.overall_score()

            # Bonus für Hypothesen, die mehr Beobachtungen erklären
            obs_explained = 0
            for obs in observations:
                if obs.description in hypothesis.explains or \
                   any(e.lower() in obs.description.lower() for e in hypothesis.explains):
                    obs_explained += 1

            explanation_bonus = (obs_explained / len(observations)) * 0.2
            final_score = score + explanation_bonus

            # Malus für Gegenbeweise
            if hypothesis.counter_evidence:
                final_score -= len(hypothesis.counter_evidence) * 0.05

            # Bonus für unterstützende Evidenz
            if hypothesis.supporting_evidence:
                final_score += len(hypothesis.supporting_evidence) * 0.03

            scores.append((h_id, min(1.0, max(0.0, final_score))))
            reasoning_trace.append(
                f"Hypothese {h_id}: Score={final_score:.3f} "
                f"(Plausibilität={hypothesis.plausibility:.2f}, "
                f"Einfachheit={hypothesis.simplicity:.2f}, "
                f"Scope={hypothesis.scope:.2f})"
            )

        # Sortiere nach Score
        scores.sort(key=lambda x: x[1], reverse=True)
        ranking = scores[:top_n]

        # Beste Hypothese
        best_h_id = scores[0][0] if scores else None
        best_hypothesis = self.hypotheses.get(best_h_id)

        # Berechne Konfidenz basierend auf Abstand zwischen Top-Hypothesen
        if len(scores) >= 2:
            confidence = (scores[0][1] - scores[1][1]) + scores[0][1] * 0.5
            confidence = min(1.0, max(0.0, confidence))
        else:
            confidence = scores[0][1] if scores else 0.0

        reasoning_trace.append(f"Beste Erklärung: {best_h_id} mit Score {scores[0][1]:.3f}")
        reasoning_trace.append(f"IBE-Konfidenz: {confidence:.2f}")

        result = InferenceToTheBestExplanation(
            observations=observations,
            hypotheses=list(self.hypotheses.values()),
            best_hypothesis=best_hypothesis,
            ranking=ranking,
            confidence=confidence,
            reasoning_trace=reasoning_trace
        )

        self.inference_history.append(result)
        return result

    def generate_alternative_hypotheses(self, observation: Observation,
                                          num_alternatives: int = 3) -> List[AbductiveHypothesis]:
        """
        Generiert automatisch alternative Hypothesen für eine Beobachtung.

        Dies ist eine heuristische Methode, die verschiedene Erklärungstypen erzeugt.
        """
        alternatives = []
        obs_desc = observation.description

        # Kausale Hypothese
        causal_h = self.generate_hypothesis(
            content=f"Eine unbekannte Ursache führt zu: {obs_desc}",
            hypothesis_type=AbductiveHypothesisType.CAUSAL,
            explains=[obs_desc],
            plausibility=0.4,
            simplicity=0.6
        )
        alternatives.append(causal_h)

        # Funktionale Hypothese
        functional_h = self.generate_hypothesis(
            content=f"Das Phänomen dient einem bestimmten Zweck: {obs_desc}",
            hypothesis_type=AbductiveHypothesisType.FUNCTIONAL,
            explains=[obs_desc],
            plausibility=0.3,
            simplicity=0.5
        )
        alternatives.append(functional_h)

        # Strukturelle Hypothese
        structural_h = self.generate_hypothesis(
            content=f"Eine zugrundeliegende Struktur erklärt: {obs_desc}",
            hypothesis_type=AbductiveHypothesisType.STRUCTURAL,
            explains=[obs_desc],
            plausibility=0.4,
            simplicity=0.4
        )
        alternatives.append(structural_h)

        return alternatives[:num_alternatives]

    def likelyhood_weighting(self, hypothesis: AbductiveHypothesis,
                              evidence_strength: float = 0.5) -> float:
        """
        Berechnet gewichtete Wahrscheinlichkeit basierend auf Evidenzstärke.

        Verwendet Bayes'sche Intuition ohne vollständiges Update.
        """
        prior = hypothesis.prior_probability
        likelihood = evidence_strength * hypothesis.plausibility

        # Vereinfachtes Bayes-Update
        posterior = (likelihood * prior) / ((likelihood * prior) + ((1 - likelihood) * (1 - prior)))

        return posterior

    def explain_inference(self, ibe_result: InferenceToTheBestExplanation) -> str:
        """Gibt eine lesbare Erklärung des IBE-Prozesses"""
        lines = [
            "=" * 60,
            "ABDUKTIVE INFERENZ - Schluss auf die beste Erklärung",
            "=" * 60,
            "",
            f"Beobachtungen ({len(ibe_result.observations)}):"
        ]

        for i, obs in enumerate(ibe_result.observations[:5]):
            lines.append(f"  {i+1}. {obs.description[:70]}...")

        lines.append("")
        lines.append(f"Hypothesen-Ranking ({len(ibe_result.ranking)}):")

        for rank, (h_id, score) in enumerate(ibe_result.ranking, 1):
            h = self.hypotheses.get(h_id)
            if h:
                lines.append(f"  {rank}. [{h_id}] Score: {score:.3f}")
                lines.append(f"      {h.content[:60]}...")
                lines.append(f"      Typ: {h.hypothesis_type.value}, "
                           f"Plausibilität: {h.plausibility:.2f}")

        lines.append("")
        if ibe_result.best_hypothesis:
            lines.append(f"BESTE ERKLÄRUNG: {ibe_result.best_hypothesis.content}")
        lines.append(f"Konfidenz: {ibe_result.confidence:.2f}")

        return "\n".join(lines)

    def get_summary(self) -> str:
        """Gibt eine Zusammenfassung des abduktiven Reasoners"""
        return (
            f"=== Abduktiver Reasoner ===\n"
            f"Beobachtungen: {len(self.observations)}\n"
            f"Hypothesen: {len(self.hypotheses)}\n"
            f"Durchgeführte IBE: {len(self.inference_history)}"
        )


# =============================================================================
# 6. TEMPORAL REASONING - Zeitbasiertes Schlussfolgern
# =============================================================================

class TemporalReasoner:
    """
    Temporales Reasoning - Zeitbasiertes Schlussfolgern.

    Implementiert:
    - Allen's Interval Algebra (Zeitintervall-Beziehungen)
    - Temporale Kausalität mit Verzögerungen
    - Mustererkennung in Zeitreihen
    - Vorhersage zukünftiger Ereignisse
    - Zeitliche Konsistenzprüfung

    Anwendungsfälle:
    - Sequenzielle Ereignisanalyse
    - Kausale Zeitreihenanalyse
    - Planung und Scheduling
    - Historische Analyse
    """

    def __init__(self):
        self.timelines: Dict[str, Timeline] = {}
        self.events: Dict[str, TemporalEvent] = {}
        self.constraints: List[TemporalConstraint] = []
        self.causal_links: List[TemporalCausalLink] = []
        self.patterns: Dict[str, TemporalPattern] = {}
        self._default_timeline = Timeline(timeline_id="default")
        self.timelines["default"] = self._default_timeline

    def add_event(self, event_id: str, description: str,
                  start_time: datetime = None, end_time: datetime = None,
                  duration: float = None,
                  granularity: TemporalGranularity = TemporalGranularity.SECONDS,
                  is_instantaneous: bool = False,
                  timeline_id: str = "default") -> TemporalEvent:
        """
        Fügt ein zeitliches Ereignis hinzu.

        Args:
            event_id: Eindeutige ID des Events
            description: Beschreibung
            start_time: Startzeit (optional)
            end_time: Endzeit (optional)
            duration: Dauer in Sekunden (optional)
            granularity: Zeitliche Auflösung
            is_instantaneous: Punktuelles Ereignis?
            timeline_id: Zugehörige Timeline
        """
        event = TemporalEvent(
            event_id=event_id,
            description=description,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            granularity=granularity,
            is_instantaneous=is_instantaneous
        )

        self.events[event_id] = event

        # Zu Timeline hinzufügen
        if timeline_id in self.timelines:
            self.timelines[timeline_id].events[event_id] = event

        logger.debug(f"[TemporalReasoner] Event hinzugefügt: {event_id}")
        return event

    def add_constraint(self, event_a: str, event_b: str,
                       relation: TemporalRelation,
                       min_gap: float = None, max_gap: float = None,
                       confidence: float = 0.8) -> TemporalConstraint:
        """
        Fügt eine zeitliche Einschränkung zwischen Events hinzu.

        Args:
            event_a: Erstes Event
            event_b: Zweites Event
            relation: Zeitliche Beziehung (Allen's Interval Algebra)
            min_gap: Minimaler zeitlicher Abstand (Sekunden)
            max_gap: Maximaler zeitlicher Abstand (Sekunden)
            confidence: Konfidenz der Einschränkung
        """
        constraint = TemporalConstraint(
            event_a=event_a,
            event_b=event_b,
            relation=relation,
            min_gap=min_gap,
            max_gap=max_gap,
            confidence=confidence
        )

        self.constraints.append(constraint)
        self._default_timeline.constraints.append(constraint)

        logger.debug(f"[TemporalReasoner] Constraint: {event_a} {relation.value} {event_b}")
        return constraint

    def add_temporal_causal_link(self, cause_event: str, effect_event: str,
                                   delay: float, strength: float = 0.5,
                                   delay_variance: float = 0.0,
                                   mechanism: str = "",
                                   is_deterministic: bool = False) -> TemporalCausalLink:
        """
        Fügt eine zeitlich-kausale Verbindung hinzu.

        Args:
            cause_event: Ursache-Event
            effect_event: Effekt-Event
            delay: Zeitliche Verzögerung (Sekunden)
            strength: Kausale Stärke
            delay_variance: Variabilität der Verzögerung
            mechanism: Beschreibung des Mechanismus
            is_deterministic: Ist die Kausalität deterministisch?
        """
        link = TemporalCausalLink(
            cause_event=cause_event,
            effect_event=effect_event,
            delay=delay,
            delay_variance=delay_variance,
            strength=strength,
            mechanism=mechanism,
            is_deterministic=is_deterministic
        )

        self.causal_links.append(link)
        self._default_timeline.causal_links.append(link)

        # Implizite Constraint hinzufügen
        self.add_constraint(
            cause_event, effect_event,
            TemporalRelation.CAUSES_DELAYED if delay > 0 else TemporalRelation.CAUSES_IMMEDIATELY,
            min_gap=delay - delay_variance,
            max_gap=delay + delay_variance,
            confidence=strength
        )

        return link

    def infer_relation(self, event_a: str, event_b: str) -> Optional[TemporalRelation]:
        """
        Inferiert die zeitliche Beziehung zwischen zwei Events.

        Basiert auf Allen's Interval Algebra.
        """
        if event_a not in self.events or event_b not in self.events:
            return None

        ea = self.events[event_a]
        eb = self.events[event_b]

        # Wenn beide Zeitstempel haben
        if ea.start_time and eb.start_time:
            if ea.end_time and eb.end_time:
                # Volle Intervall-Analyse
                return self._infer_interval_relation(
                    ea.start_time, ea.end_time,
                    eb.start_time, eb.end_time
                )
            elif ea.is_instantaneous and eb.is_instantaneous:
                # Punktuelle Events
                if ea.start_time < eb.start_time:
                    return TemporalRelation.BEFORE
                elif ea.start_time > eb.start_time:
                    return TemporalRelation.AFTER
                else:
                    return TemporalRelation.EQUALS

        # Versuche aus Constraints abzuleiten
        for c in self.constraints:
            if c.event_a == event_a and c.event_b == event_b:
                return c.relation
            elif c.event_a == event_b and c.event_b == event_a:
                return self._inverse_relation(c.relation)

        return None

    def _infer_interval_relation(self, a_start: datetime, a_end: datetime,
                                   b_start: datetime, b_end: datetime) -> TemporalRelation:
        """Inferiert Beziehung basierend auf Intervallen (Allen's Algebra)"""

        # A ends before B starts
        if a_end < b_start:
            return TemporalRelation.BEFORE

        # A starts after B ends
        if a_start > b_end:
            return TemporalRelation.AFTER

        # A ends exactly when B starts
        if a_end == b_start:
            return TemporalRelation.MEETS

        # A and B are identical
        if a_start == b_start and a_end == b_end:
            return TemporalRelation.EQUALS

        # A starts with B but ends earlier
        if a_start == b_start and a_end < b_end:
            return TemporalRelation.STARTS

        # A ends with B but starts later
        if a_end == b_end and a_start > b_start:
            return TemporalRelation.FINISHES

        # A completely during B
        if a_start > b_start and a_end < b_end:
            return TemporalRelation.DURING

        # Overlap
        return TemporalRelation.OVERLAPS

    def _inverse_relation(self, relation: TemporalRelation) -> TemporalRelation:
        """Gibt die inverse Beziehung zurück"""
        inverses = {
            TemporalRelation.BEFORE: TemporalRelation.AFTER,
            TemporalRelation.AFTER: TemporalRelation.BEFORE,
            TemporalRelation.MEETS: TemporalRelation.MEETS,
            TemporalRelation.OVERLAPS: TemporalRelation.OVERLAPS,
            TemporalRelation.STARTS: TemporalRelation.STARTS,
            TemporalRelation.FINISHES: TemporalRelation.FINISHES,
            TemporalRelation.DURING: TemporalRelation.DURING,
            TemporalRelation.EQUALS: TemporalRelation.EQUALS,
            TemporalRelation.CAUSES_IMMEDIATELY: TemporalRelation.CAUSES_IMMEDIATELY,
            TemporalRelation.CAUSES_DELAYED: TemporalRelation.CAUSES_DELAYED,
        }
        return inverses.get(relation, relation)

    def check_consistency(self) -> Tuple[bool, List[str]]:
        """
        Prüft die temporale Konsistenz aller Constraints.

        Returns:
            (is_consistent, list_of_violations)
        """
        violations = []

        # Prüfe direkte Widersprüche
        for i, c1 in enumerate(self.constraints):
            for c2 in self.constraints[i+1:]:
                if c1.event_a == c2.event_a and c1.event_b == c2.event_b:
                    if c1.relation != c2.relation:
                        if not self._relations_compatible(c1.relation, c2.relation):
                            violations.append(
                                f"Widerspruch: {c1.event_a} ist sowohl {c1.relation.value} "
                                f"als auch {c2.relation.value} zu {c1.event_b}"
                            )

        # Prüfe Transitivität
        transitivity_violations = self._check_transitivity()
        violations.extend(transitivity_violations)

        # Prüfe zeitliche Konsistenz mit Timestamps
        for event_id, event in self.events.items():
            if event.start_time and event.end_time:
                if event.start_time > event.end_time:
                    violations.append(
                        f"Event {event_id}: Startzeit nach Endzeit"
                    )

        return len(violations) == 0, violations

    def _relations_compatible(self, r1: TemporalRelation, r2: TemporalRelation) -> bool:
        """Prüft ob zwei Relationen kompatibel sind"""
        incompatible = {
            (TemporalRelation.BEFORE, TemporalRelation.AFTER),
            (TemporalRelation.AFTER, TemporalRelation.BEFORE),
            (TemporalRelation.BEFORE, TemporalRelation.EQUALS),
            (TemporalRelation.AFTER, TemporalRelation.EQUALS),
        }
        return (r1, r2) not in incompatible and (r2, r1) not in incompatible

    def _check_transitivity(self) -> List[str]:
        """Prüft transitive Konsistenz"""
        violations = []

        # Aufbau eines Graphen
        edges = {}
        for c in self.constraints:
            key = (c.event_a, c.event_b)
            edges[key] = c.relation

        # Prüfe Transitivität für BEFORE
        for c1 in self.constraints:
            if c1.relation == TemporalRelation.BEFORE:
                for c2 in self.constraints:
                    if c2.relation == TemporalRelation.BEFORE and c2.event_a == c1.event_b:
                        # A < B und B < C => A < C
                        expected = (c1.event_a, c2.event_b)
                        if expected in edges and edges[expected] == TemporalRelation.AFTER:
                            violations.append(
                                f"Transitivitätsverletzung: {c1.event_a} < {c1.event_b} < {c2.event_b}, "
                                f"aber {c1.event_a} > {c2.event_b}"
                            )

        return violations

    def detect_pattern(self, event_sequence: List[str],
                        pattern_id: str = None) -> Optional[TemporalPattern]:
        """
        Erkennt ein temporales Muster in einer Event-Sequenz.

        Args:
            event_sequence: Liste von Event-IDs in Reihenfolge
            pattern_id: Optionale ID für das Muster
        """
        if len(event_sequence) < 2:
            return None

        # Berechne typische Intervalle
        intervals = []
        for i in range(len(event_sequence) - 1):
            e1 = self.events.get(event_sequence[i])
            e2 = self.events.get(event_sequence[i + 1])

            if e1 and e2 and e1.start_time and e2.start_time:
                delta = (e2.start_time - e1.start_time).total_seconds()
                intervals.append(delta)

        # Prüfe auf Periodizität
        is_periodic = False
        period = None

        if len(intervals) >= 2:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)

            # Niedrige Varianz deutet auf Periodizität hin
            if variance < (avg_interval * 0.1) ** 2:  # 10% Toleranz
                is_periodic = True
                period = avg_interval

        pattern = TemporalPattern(
            pattern_id=pattern_id or f"pattern_{len(self.patterns)}",
            description=f"Muster: {' -> '.join(event_sequence)}",
            events_sequence=event_sequence,
            typical_intervals=intervals,
            frequency=1,
            confidence=0.5 + len(event_sequence) * 0.05,
            is_periodic=is_periodic,
            period=period
        )

        self.patterns[pattern.pattern_id] = pattern
        return pattern

    def predict_next_event(self, current_event: str,
                            lookahead: float = None) -> List[Tuple[str, float, float]]:
        """
        Sagt das nächste wahrscheinliche Event vorher.

        Args:
            current_event: Aktuelles Event
            lookahead: Zeitfenster für Vorhersage (Sekunden)

        Returns:
            Liste von (event_id, probability, expected_delay)
        """
        predictions = []

        # Basierend auf kausalen Links
        for link in self.causal_links:
            if link.cause_event == current_event:
                if lookahead is None or link.delay <= lookahead:
                    predictions.append((
                        link.effect_event,
                        link.strength,
                        link.delay
                    ))

        # Basierend auf Patterns
        for pattern in self.patterns.values():
            if current_event in pattern.events_sequence:
                idx = pattern.events_sequence.index(current_event)
                if idx < len(pattern.events_sequence) - 1:
                    next_event = pattern.events_sequence[idx + 1]
                    delay = pattern.typical_intervals[idx] if idx < len(pattern.typical_intervals) else 0
                    if lookahead is None or delay <= lookahead:
                        predictions.append((
                            next_event,
                            pattern.confidence * 0.8,
                            delay
                        ))

        # Sortiere nach Wahrscheinlichkeit
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions

    def construct_timeline_from_events(self, event_ids: List[str],
                                         timeline_id: str = None) -> Timeline:
        """
        Konstruiert eine Timeline aus einer Liste von Events.
        """
        tl_id = timeline_id or f"timeline_{len(self.timelines)}"

        # Sortiere Events nach Zeit wenn möglich
        sorted_events = []
        unsorted = []

        for eid in event_ids:
            if eid in self.events:
                event = self.events[eid]
                if event.start_time:
                    sorted_events.append((event.start_time, event))
                else:
                    unsorted.append(event)

        sorted_events.sort(key=lambda x: x[0])

        timeline = Timeline(
            timeline_id=tl_id,
            events={e.event_id: e for _, e in sorted_events},
            start=sorted_events[0][0] if sorted_events else None,
            end=sorted_events[-1][0] if sorted_events else None
        )

        # Füge unsortierte Events hinzu
        for event in unsorted:
            timeline.events[event.event_id] = event

        # Relevante Constraints hinzufügen
        for c in self.constraints:
            if c.event_a in event_ids and c.event_b in event_ids:
                timeline.constraints.append(c)

        # Relevante kausale Links
        for link in self.causal_links:
            if link.cause_event in event_ids and link.effect_event in event_ids:
                timeline.causal_links.append(link)

        self.timelines[tl_id] = timeline
        return timeline

    def reason_about_sequence(self, event_sequence: List[str]) -> Dict[str, Any]:
        """
        Analysiert eine Event-Sequenz und zieht Schlussfolgerungen.

        Returns:
            Analyseergebnis mit Relationen, Mustern und Vorhersagen
        """
        analysis = {
            "sequence": event_sequence,
            "relations": [],
            "causal_chains": [],
            "patterns_found": [],
            "predictions": [],
            "consistency": True,
            "violations": []
        }

        # Inferiere Relationen zwischen aufeinanderfolgenden Events
        for i in range(len(event_sequence) - 1):
            relation = self.infer_relation(event_sequence[i], event_sequence[i + 1])
            if relation:
                analysis["relations"].append({
                    "from": event_sequence[i],
                    "to": event_sequence[i + 1],
                    "relation": relation.value
                })

        # Finde kausale Ketten
        current_chain = [event_sequence[0]] if event_sequence else []
        for i in range(len(event_sequence) - 1):
            is_causal = False
            for link in self.causal_links:
                if link.cause_event == event_sequence[i] and \
                   link.effect_event == event_sequence[i + 1]:
                    current_chain.append(event_sequence[i + 1])
                    is_causal = True
                    break

            if not is_causal and len(current_chain) > 1:
                analysis["causal_chains"].append(current_chain)
                current_chain = [event_sequence[i + 1]]

        if len(current_chain) > 1:
            analysis["causal_chains"].append(current_chain)

        # Mustererkennung
        pattern = self.detect_pattern(event_sequence)
        if pattern:
            analysis["patterns_found"].append({
                "pattern_id": pattern.pattern_id,
                "is_periodic": pattern.is_periodic,
                "period": pattern.period
            })

        # Vorhersage
        if event_sequence:
            predictions = self.predict_next_event(event_sequence[-1])
            analysis["predictions"] = [
                {"event": p[0], "probability": p[1], "delay": p[2]}
                for p in predictions[:3]
            ]

        # Konsistenzprüfung
        is_consistent, violations = self.check_consistency()
        analysis["consistency"] = is_consistent
        analysis["violations"] = violations

        return analysis

    def get_summary(self) -> str:
        """Gibt eine Zusammenfassung des temporalen Reasoners"""
        lines = [
            "=== Temporaler Reasoner ===",
            f"Events: {len(self.events)}",
            f"Constraints: {len(self.constraints)}",
            f"Kausale Links: {len(self.causal_links)}",
            f"Patterns: {len(self.patterns)}",
            f"Timelines: {len(self.timelines)}",
        ]

        is_consistent, violations = self.check_consistency()
        lines.append(f"Konsistent: {'Ja' if is_consistent else 'Nein (' + str(len(violations)) + ' Verletzungen)'}")

        return "\n".join(lines)

    def visualize_timeline(self, timeline_id: str = "default") -> str:
        """Erzeugt eine textuelle Visualisierung einer Timeline"""
        if timeline_id not in self.timelines:
            return f"Timeline '{timeline_id}' nicht gefunden"

        tl = self.timelines[timeline_id]
        lines = [
            f"Timeline: {timeline_id}",
            "=" * 50
        ]

        # Sortiere Events nach Zeit
        sorted_events = sorted(
            [(e.start_time or datetime.min, e) for e in tl.events.values()],
            key=lambda x: x[0]
        )

        for i, (time, event) in enumerate(sorted_events):
            time_str = time.strftime("%Y-%m-%d %H:%M:%S") if time != datetime.min else "???"
            lines.append(f"[{time_str}] {event.event_id}: {event.description[:40]}...")

            # Zeige kausale Links
            for link in tl.causal_links:
                if link.cause_event == event.event_id:
                    lines.append(f"    --> verursacht: {link.effect_event} (Delay: {link.delay}s)")

        return "\n".join(lines)


# =============================================================================
# KOMBINIERTER REASONING-ENGINE
# =============================================================================

class AdvancedReasoningEngine:
    """
    Kombiniert alle sechs Reasoning-Modi zu einem integrierten System.

    Modi:
    1. BAYESIAN - Probabilistisches Reasoning mit Prior-Updates
    2. CAUSAL - Kausalitätsanalyse und Interventionen
    3. METACOGNITIVE - Denken über das eigene Denken
    4. DIALECTICAL - These-Antithese-Synthese Prozesse
    5. ABDUCTIVE - Schluss auf die beste Erklärung (NEU)
    6. TEMPORAL - Zeitbasiertes Schlussfolgern (NEU)
    """

    def __init__(self):
        self.bayesian = BayesianReasoner()
        self.causal = CausalReasoner()
        self.metacognitive = MetacognitiveReasoner()
        self.dialectical = DialecticalReasoner()
        # NEU: Erweiterte Reasoner
        self.abductive = AbductiveReasoner()
        self.temporal = TemporalReasoner()

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

        # NEU: Abduktives Reasoning
        if ReasoningMode.ABDUCTIVE in self.active_modes:
            results["results"]["abductive"] = self._apply_abductive(question, context)

        # NEU: Temporales Reasoning
        if ReasoningMode.TEMPORAL in self.active_modes:
            results["results"]["temporal"] = self._apply_temporal(question, context)

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

    def _apply_abductive(self, question: str, context: Dict) -> Dict:
        """Wendet abduktives Reasoning an (Inference to the Best Explanation)"""
        # Beobachtung aus Frage erstellen
        obs = self.abductive.add_observation(
            description=question,
            reliability=context.get("observation_reliability", 0.8),
            source=context.get("source", "user_query")
        )

        # Hypothesen aus Kontext oder automatisch generieren
        if "hypotheses" in context:
            for h in context["hypotheses"]:
                self.abductive.generate_hypothesis(
                    content=h.get("content", ""),
                    hypothesis_type=AbductiveHypothesisType.CAUSAL,
                    explains=[question],
                    plausibility=h.get("plausibility", 0.5),
                    simplicity=h.get("simplicity", 0.5),
                    prior=h.get("prior", 0.5)
                )
        else:
            # Automatisch alternative Hypothesen generieren
            self.abductive.generate_alternative_hypotheses(obs, num_alternatives=3)

        # Inferenz durchführen
        ibe_result = self.abductive.infer_best_explanation()

        return {
            "observations": len(ibe_result.observations),
            "hypotheses_evaluated": len(ibe_result.hypotheses),
            "best_explanation": ibe_result.best_hypothesis.content if ibe_result.best_hypothesis else None,
            "best_score": ibe_result.ranking[0][1] if ibe_result.ranking else 0,
            "confidence": ibe_result.confidence,
            "ranking": [(h_id, score) for h_id, score in ibe_result.ranking[:3]]
        }

    def _apply_temporal(self, question: str, context: Dict) -> Dict:
        """Wendet temporales Reasoning an"""
        results = {
            "events_analyzed": 0,
            "constraints_found": 0,
            "patterns_detected": 0,
            "predictions": [],
            "consistency": True
        }

        # Events aus Kontext hinzufügen
        if "events" in context:
            for event in context["events"]:
                self.temporal.add_event(
                    event_id=event.get("id", f"event_{len(self.temporal.events)}"),
                    description=event.get("description", ""),
                    start_time=event.get("start_time"),
                    end_time=event.get("end_time"),
                    is_instantaneous=event.get("instantaneous", True)
                )
            results["events_analyzed"] = len(context["events"])

        # Constraints aus Kontext hinzufügen
        if "temporal_constraints" in context:
            for tc in context["temporal_constraints"]:
                self.temporal.add_constraint(
                    event_a=tc.get("event_a"),
                    event_b=tc.get("event_b"),
                    relation=TemporalRelation(tc.get("relation", "before")),
                    min_gap=tc.get("min_gap"),
                    max_gap=tc.get("max_gap")
                )
            results["constraints_found"] = len(context["temporal_constraints"])

        # Kausale Links aus Kontext
        if "causal_links" in context:
            for link in context["causal_links"]:
                self.temporal.add_temporal_causal_link(
                    cause_event=link.get("cause"),
                    effect_event=link.get("effect"),
                    delay=link.get("delay", 0),
                    strength=link.get("strength", 0.5),
                    mechanism=link.get("mechanism", "")
                )

        # Sequenz analysieren wenn vorhanden
        if "sequence" in context:
            sequence_analysis = self.temporal.reason_about_sequence(context["sequence"])
            results["patterns_detected"] = len(sequence_analysis.get("patterns_found", []))
            results["predictions"] = sequence_analysis.get("predictions", [])

        # Konsistenz prüfen
        is_consistent, violations = self.temporal.check_consistency()
        results["consistency"] = is_consistent
        if not is_consistent:
            results["violations"] = violations

        return results

    def _calculate_overall_confidence(self, results: Dict) -> float:
        """Berechnet Gesamtkonfidenz aus allen Ergebnissen"""
        confidences = []

        if "bayesian" in results.get("results", {}):
            confidences.append(results["results"]["bayesian"].get("posterior", 0.5))

        if "dialectical" in results.get("results", {}):
            confidences.append(results["results"]["dialectical"].get("synthesis_strength", 0.5))

        # NEU: Abduktive Konfidenz
        if "abductive" in results.get("results", {}):
            confidences.append(results["results"]["abductive"].get("confidence", 0.5))

        # NEU: Temporale Konsistenz als Konfidenzindikator
        if "temporal" in results.get("results", {}):
            if results["results"]["temporal"].get("consistency", True):
                confidences.append(0.7)  # Konsistent = höhere Konfidenz
            else:
                confidences.append(0.3)  # Inkonsistent = niedrigere Konfidenz

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
        summary.append(f"Kausale Ketten: {len(self.causal.causal_chains)}")
        summary.append(f"Domänen-Wissen: {sum(len(v) for v in self.causal.domain_knowledge.values())} Beziehungen")

        # Metacognitive Summary
        summary.append(f"\n--- Metacognitive Reasoner ---")
        eval_result = self.metacognitive.evaluate_reasoning_quality()
        summary.append(f"Denkqualität: {eval_result['quality']} ({eval_result['score']:.2f})")

        # Dialectical Summary
        summary.append(f"\n--- Dialectical Reasoner ---")
        summary.append(f"Positionen: {len(self.dialectical.positions)}")
        summary.append(f"Synthesen: {len(self.dialectical.synthesis_history)}")

        # NEU: Abductive Summary
        summary.append(f"\n--- Abductive Reasoner ---")
        summary.append(f"Beobachtungen: {len(self.abductive.observations)}")
        summary.append(f"Hypothesen: {len(self.abductive.hypotheses)}")
        summary.append(f"Durchgeführte IBE: {len(self.abductive.inference_history)}")

        # NEU: Temporal Summary
        summary.append(f"\n--- Temporal Reasoner ---")
        summary.append(f"Events: {len(self.temporal.events)}")
        summary.append(f"Constraints: {len(self.temporal.constraints)}")
        summary.append(f"Kausale Links: {len(self.temporal.causal_links)}")
        summary.append(f"Patterns: {len(self.temporal.patterns)}")

        return "\n".join(summary)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_advanced_reasoning_engine(modes: List[ReasoningMode] = None,
                                      include_all: bool = False) -> AdvancedReasoningEngine:
    """
    Erstellt eine Advanced Reasoning Engine mit den gewünschten Modi.

    Args:
        modes: Liste der zu aktivierenden Modi. Default: Basis-Modi
        include_all: Wenn True, werden alle 6 Modi aktiviert

    Returns:
        Konfigurierte AdvancedReasoningEngine

    Beispiel:
        # Basis-Engine (4 Modi)
        engine = create_advanced_reasoning_engine()

        # Alle 6 Modi aktivieren
        engine = create_advanced_reasoning_engine(include_all=True)

        # Spezifische Modi
        engine = create_advanced_reasoning_engine(modes=[
            ReasoningMode.CAUSAL,
            ReasoningMode.ABDUCTIVE,
            ReasoningMode.TEMPORAL
        ])
    """
    engine = AdvancedReasoningEngine()

    if include_all:
        modes = [
            ReasoningMode.BAYESIAN,
            ReasoningMode.CAUSAL,
            ReasoningMode.METACOGNITIVE,
            ReasoningMode.DIALECTICAL,
            ReasoningMode.ABDUCTIVE,
            ReasoningMode.TEMPORAL
        ]
    elif modes is None:
        # Default: Basis-Modi für Rückwärtskompatibilität
        modes = [ReasoningMode.BAYESIAN, ReasoningMode.CAUSAL,
                 ReasoningMode.METACOGNITIVE, ReasoningMode.DIALECTICAL]

    for mode in modes:
        engine.activate_mode(mode)

    return engine


# =============================================================================
# HILFS-FUNKTIONEN FÜR REASONING-INTEGRATION
# =============================================================================

def create_causal_reasoner_with_domain(domain: CausalDomain) -> CausalReasoner:
    """
    Erstellt einen CausalReasoner mit vorgeladenem Domänenwissen.

    Args:
        domain: Die Domäne, deren Wissen geladen werden soll

    Returns:
        CausalReasoner mit aktiviertem Domänenwissen
    """
    reasoner = CausalReasoner()
    reasoner.apply_domain_knowledge(domain)
    return reasoner


def create_full_reasoning_system() -> Dict[str, Any]:
    """
    Erstellt ein vollständiges Reasoning-System mit allen Komponenten.

    Returns:
        Dictionary mit allen Reasoning-Komponenten
    """
    return {
        "engine": create_advanced_reasoning_engine(include_all=True),
        "bayesian": BayesianReasoner(),
        "causal": CausalReasoner(),
        "metacognitive": MetacognitiveReasoner(),
        "dialectical": DialecticalReasoner(),
        "abductive": AbductiveReasoner(),
        "temporal": TemporalReasoner(),
    }


# =============================================================================
# BEISPIEL / TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("  HOLO ADVANCED REASONING ENGINE - Erweiterte Demo")
    print("  6 Reasoning-Modi: Bayesian, Causal, Metacognitive,")
    print("                    Dialectical, Abductive, Temporal")
    print("=" * 70)

    # Erstelle Engine mit ALLEN Modi (NEU)
    engine = create_advanced_reasoning_engine(include_all=True)

    # Teste Bayesian Reasoning
    print("\n--- 1. Bayesian Reasoning ---")
    engine.bayesian.add_belief("regen_morgen", "Es wird morgen regnen", prior=0.3)
    engine.bayesian.update_belief("regen_morgen", "Dunkle Wolken am Himmel", 0.8, 0.2)
    print(f"P(Regen|Wolken): {engine.bayesian.beliefs['regen_morgen'].posterior:.3f}")
    print(f"Konfidenz: {engine.bayesian.get_confidence_level('regen_morgen')}")

    # Teste Causal Reasoning mit erweitertem Domänenwissen
    print("\n--- 2. Causal Reasoning (mit erweiterten Domänen) ---")
    engine.causal.apply_domain_knowledge(CausalDomain.MEDIZIN)
    engine.causal.apply_domain_knowledge(CausalDomain.NEUROWISSENSCHAFT)  # NEU
    print(f"Geladene Variablen: {len(engine.causal.nodes)}")
    print(f"Kausale Beziehungen: {len(engine.causal.edges)}")
    print(f"Vordefinierte Ketten: {len(engine.causal.causal_chains)}")

    # Zeige eine kausale Kette
    if "stress_disease" in engine.causal.causal_chains:
        chain = engine.causal.causal_chains["stress_disease"]
        print(f"\nBeispiel Kausalkette '{chain.chain_id}':")
        print(f"  {' -> '.join(chain.variables)}")
        print(f"  Gesamtstärke: {chain.total_strength:.2f}")

    # Teste Dialectical Reasoning
    print("\n--- 3. Dialectical Reasoning ---")
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
    print(f"Synthese: {synthesis.content[:150]}...")

    # NEU: Teste Abductive Reasoning
    print("\n--- 4. Abductive Reasoning (NEU) ---")
    # Beobachtung hinzufügen
    obs = engine.abductive.add_observation(
        "Der Patient zeigt Müdigkeit, Konzentrationsschwäche und Gewichtszunahme",
        reliability=0.9,
        source="Arztbericht"
    )

    # Hypothesen generieren
    h1 = engine.abductive.generate_hypothesis(
        content="Schilddrüsenunterfunktion (Hypothyreose) verursacht die Symptome",
        hypothesis_type=AbductiveHypothesisType.CAUSAL,
        explains=[obs.description],
        plausibility=0.7,
        simplicity=0.8,
        prior=0.3
    )

    h2 = engine.abductive.generate_hypothesis(
        content="Depression ist die Ursache der Symptome",
        hypothesis_type=AbductiveHypothesisType.CAUSAL,
        explains=[obs.description],
        plausibility=0.6,
        simplicity=0.7,
        prior=0.4
    )

    h3 = engine.abductive.generate_hypothesis(
        content="Schlafapnoe verursacht die Beschwerden",
        hypothesis_type=AbductiveHypothesisType.CAUSAL,
        explains=[obs.description],
        plausibility=0.5,
        simplicity=0.6,
        prior=0.2
    )

    # Evidenz hinzufügen
    engine.abductive.add_supporting_evidence(h1.hypothesis_id, "TSH-Wert erhöht")
    engine.abductive.add_counter_evidence(h2.hypothesis_id, "Patient zeigt keine Traurigkeit")

    # Inference to the Best Explanation durchführen
    ibe_result = engine.abductive.infer_best_explanation()
    print(f"Beste Erklärung: {ibe_result.best_hypothesis.content if ibe_result.best_hypothesis else 'N/A'}")
    print(f"Konfidenz: {ibe_result.confidence:.2f}")
    print(f"Ranking: {[(h_id, f'{score:.3f}') for h_id, score in ibe_result.ranking]}")

    # NEU: Teste Temporal Reasoning
    print("\n--- 5. Temporal Reasoning (NEU) ---")
    # Events hinzufügen
    engine.temporal.add_event("infektion", "Virus-Infektion beginnt", is_instantaneous=True)
    engine.temporal.add_event("inkubation", "Inkubationszeit", is_instantaneous=False)
    engine.temporal.add_event("symptome", "Erste Symptome erscheinen", is_instantaneous=True)
    engine.temporal.add_event("höhepunkt", "Krankheitshöhepunkt", is_instantaneous=True)
    engine.temporal.add_event("genesung", "Genesung", is_instantaneous=False)

    # Temporale Constraints
    engine.temporal.add_constraint("infektion", "symptome", TemporalRelation.BEFORE, min_gap=86400, max_gap=432000)
    engine.temporal.add_constraint("symptome", "höhepunkt", TemporalRelation.BEFORE)
    engine.temporal.add_constraint("höhepunkt", "genesung", TemporalRelation.BEFORE)

    # Kausale Links mit Zeitverzögerung
    engine.temporal.add_temporal_causal_link(
        "infektion", "symptome",
        delay=259200,  # 3 Tage
        strength=0.9,
        mechanism="Virusvermehrung erreicht symptomatisches Niveau"
    )

    # Konsistenz prüfen
    is_consistent, violations = engine.temporal.check_consistency()
    print(f"Temporale Konsistenz: {'Ja' if is_consistent else 'Nein'}")

    # Vorhersage
    predictions = engine.temporal.predict_next_event("symptome")
    if predictions:
        print(f"Nächstes erwartetes Event nach 'symptome': {predictions[0][0]} (P={predictions[0][1]:.2f})")

    # Sequenz-Analyse
    sequence = ["infektion", "inkubation", "symptome", "höhepunkt", "genesung"]
    analysis = engine.temporal.reason_about_sequence(sequence)
    print(f"Analysierte Sequenz: {' -> '.join(sequence)}")
    print(f"Kausale Ketten gefunden: {len(analysis['causal_chains'])}")

    # Teste kombiniertes Reasoning mit ALLEN Modi
    print("\n--- 6. Kombiniertes Multi-Modal Reasoning ---")
    result = engine.reason(
        "Warum steigt die Zahl der Burnout-Fälle?",
        context={
            "prior_probability": 0.7,
            "evidence": [
                {"description": "Arbeitsdichte nimmt zu", "likelihood_if_true": 0.85, "likelihood_if_false": 0.2},
                {"description": "Digitalisierung führt zu Always-On-Mentalität", "likelihood_if_true": 0.75, "likelihood_if_false": 0.3}
            ],
            "thesis_arguments": ["Arbeitsbelastung", "Gesellschaftlicher Druck", "Mangelnde Work-Life-Balance"],
            "antithesis_arguments": ["Bessere Diagnosekriterien", "Erhöhte Sensibilisierung", "Mehr Offenheit"],
            "hypotheses": [
                {"content": "Strukturelle Arbeitsmarktveränderungen", "plausibility": 0.7},
                {"content": "Individuelle Stressresistenz sinkt", "plausibility": 0.4}
            ]
        }
    )
    print(f"Verwendete Modi: {result['modes_used']}")
    print(f"Ergebnis-Kategorien: {list(result['results'].keys())}")

    # Gesamtzusammenfassung
    print("\n" + engine.get_reasoning_summary())

    # Zeige Domänen-Statistik
    print("\n--- Verfügbare Domänen mit Kausalwissen ---")
    for domain in CausalDomain:
        knowledge_count = len(engine.causal.domain_knowledge.get(domain, []))
        if knowledge_count > 0:
            print(f"  {domain.value}: {knowledge_count} Beziehungen")

    print("\n" + "=" * 70)
    print("  Demo abgeschlossen!")
    print("=" * 70)
