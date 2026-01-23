#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO EXTENDED COGNITION - Integration erweiterter kognitiver Systeme       ║
║                                                                              ║
║  Zentraler Hub für die neuen Reasoning- und Analyse-Module:                 ║
║                                                                              ║
║  🧠 ADVANCED REASONING                                                       ║
║     • Bayesian Reasoning - Probabilistisches Denken                         ║
║     • Causal Reasoning - Kausalität verstehen                               ║
║     • Metacognitive Reasoning - Denken über Denken                          ║
║     • Dialectical Reasoning - These-Antithese-Synthese                      ║
║                                                                              ║
║  📊 ANALYTICAL STRATEGIES                                                    ║
║     • MECE Analysis - Strukturierte Problemzerlegung                        ║
║     • Root Cause Analysis - Ursachenforschung                               ║
║     • Morphological Analysis - Kombinatorische Lösungsfindung               ║
║                                                                              ║
║  🔬 APPROXIMATION ALGORITHMS                                                 ║
║     • Simulated Annealing - Metallurgische Optimierung                      ║
║     • PSO - Schwarmoptimierung                                              ║
║     • Branch & Bound - Systematische Enumeration                            ║
║                                                                              ║
║  📜 FORMAL AXIOMS                                                            ║
║     • Epistemische Axiome - Wissen & Glauben                                ║
║     • Logik-Axiome - Klassische & Modale Logik                              ║
║     • Ethik-Axiome - Deontische Logik                                       ║
║     • Lern-Axiome - Adaptives Lernen                                        ║
║                                                                              ║
║  Author: Holocloude System                                                   ║
║  Version: 1.0                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger("HoloExtendedCognition")


# =============================================================================
# IMPORTS - Mit Fallbacks für robuste Integration
# =============================================================================

# Advanced Reasoning Module
try:
    from holo_advanced_reasoning import (
        AdvancedReasoningEngine,
        BayesianReasoner,
        CausalReasoner,
        MetacognitiveReasoner,
        DialecticalReasoner,
        ReasoningMode,
        create_advanced_reasoning_engine,
    )
    ADVANCED_REASONING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced Reasoning nicht verfügbar: {e}")
    ADVANCED_REASONING_AVAILABLE = False
    AdvancedReasoningEngine = None
    create_advanced_reasoning_engine = None
    ReasoningMode = None

# Analytical Strategies Module
try:
    from holo_analytical_strategies import (
        AnalyticalStrategyEngine,
        MECEAnalyzer,
        RootCauseAnalyzer,
        MorphologicalAnalyzer,
        AnalysisType,
        create_analytical_engine,
    )
    ANALYTICAL_STRATEGIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analytical Strategies nicht verfügbar: {e}")
    ANALYTICAL_STRATEGIES_AVAILABLE = False
    AnalyticalStrategyEngine = None
    create_analytical_engine = None
    AnalysisType = None

# Approximation Algorithms Module
try:
    from holo_approximation_algorithms import (
        ApproximationEngine,
        SimulatedAnnealing,
        ParticleSwarmOptimization,
        BranchAndBound,
        OptimizationType,
        create_approximation_engine,
        BenchmarkFunctions,
    )
    APPROXIMATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Approximation Algorithms nicht verfügbar: {e}")
    APPROXIMATION_AVAILABLE = False
    ApproximationEngine = None
    create_approximation_engine = None
    OptimizationType = None

# Formal Axioms Module
try:
    from holo_formal_axioms import (
        FormalAxiomSystem,
        EpistemicAxioms,
        LogicAxioms,
        EthicsAxioms,
        LearningAxioms,
        AxiomCategory,
        create_formal_axiom_system,
    )
    FORMAL_AXIOMS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Formal Axioms nicht verfügbar: {e}")
    FORMAL_AXIOMS_AVAILABLE = False
    FormalAxiomSystem = None
    create_formal_axiom_system = None
    AxiomCategory = None


# =============================================================================
# ENUMS
# =============================================================================

class CognitionMode(Enum):
    """Kognitionsmodus für verschiedene Aufgaben"""
    INTUITIVE = "intuitive"          # Schnell, heuristisch
    ANALYTICAL = "analytical"        # Systematisch, strukturiert
    CREATIVE = "creative"            # Explorativ, kombinatorisch
    CRITICAL = "critical"            # Skeptisch, prüfend
    REFLECTIVE = "reflective"        # Metakognitiv, selbst-analysierend


class TaskComplexity(Enum):
    """Komplexität einer Aufgabe"""
    SIMPLE = "simple"               # Einfache Antwort
    MODERATE = "moderate"           # Etwas Überlegung nötig
    COMPLEX = "complex"             # Tiefes Nachdenken
    EXPERT = "expert"               # Expertenanalyse


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class CognitiveTask:
    """Eine kognitive Aufgabe"""
    description: str
    complexity: TaskComplexity = TaskComplexity.MODERATE
    requires_reasoning: bool = True
    requires_analysis: bool = False
    requires_optimization: bool = False
    requires_ethics: bool = False
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveResult:
    """Ergebnis einer kognitiven Verarbeitung"""
    task: CognitiveTask
    conclusion: str
    reasoning_trace: List[str] = field(default_factory=list)
    confidence: float = 0.5
    modules_used: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# EXTENDED COGNITION ENGINE
# =============================================================================

class ExtendedCognitionEngine:
    """
    Zentraler Hub für erweiterte kognitive Fähigkeiten.

    Integriert:
    - Advanced Reasoning (Bayesian, Causal, Metacognitive, Dialectical)
    - Analytical Strategies (MECE, Root Cause, Morphological)
    - Approximation Algorithms (SA, PSO, B&B)
    - Formal Axioms (Epistemic, Logic, Ethics, Learning)
    """

    def __init__(self):
        # Initialisiere Module
        self.reasoning: Optional[AdvancedReasoningEngine] = None
        self.analytics: Optional[AnalyticalStrategyEngine] = None
        self.approximation: Optional[ApproximationEngine] = None
        self.axioms: Optional[FormalAxiomSystem] = None

        # Status
        self.modules_available = {
            "advanced_reasoning": ADVANCED_REASONING_AVAILABLE,
            "analytical_strategies": ANALYTICAL_STRATEGIES_AVAILABLE,
            "approximation": APPROXIMATION_AVAILABLE,
            "formal_axioms": FORMAL_AXIOMS_AVAILABLE,
        }

        # Initialisiere verfügbare Module
        self._initialize_modules()

        # Tracking
        self.processing_history: List[CognitiveResult] = []
        self.current_mode: CognitionMode = CognitionMode.ANALYTICAL

        logger.info(f"ExtendedCognitionEngine initialisiert. Verfügbare Module: {self.modules_available}")

    def _initialize_modules(self):
        """Initialisiert alle verfügbaren Module"""
        if ADVANCED_REASONING_AVAILABLE:
            self.reasoning = create_advanced_reasoning_engine()
            # Aktiviere alle Modi
            for mode in ReasoningMode:
                self.reasoning.activate_mode(mode)

        if ANALYTICAL_STRATEGIES_AVAILABLE:
            self.analytics = create_analytical_engine()

        if APPROXIMATION_AVAILABLE:
            self.approximation = create_approximation_engine()

        if FORMAL_AXIOMS_AVAILABLE:
            self.axioms = create_formal_axiom_system()
            # Erstelle Default-Agent
            if self.axioms:
                self.axioms.epistemic.create_agent("Holo")

    # -------------------------------------------------------------------------
    # REASONING METHODS
    # -------------------------------------------------------------------------

    def bayesian_update(self, belief: str, prior: float,
                         evidence: str, likelihood_true: float,
                         likelihood_false: float) -> Dict[str, Any]:
        """
        Führt ein Bayesianisches Belief-Update durch.

        Args:
            belief: Die Überzeugung
            prior: Vorherige Wahrscheinlichkeit
            evidence: Neue Evidenz
            likelihood_true: P(E|H)
            likelihood_false: P(E|¬H)

        Returns:
            Update-Ergebnis mit Posterior
        """
        if not ADVANCED_REASONING_AVAILABLE or not self.reasoning:
            return {"error": "Advanced Reasoning nicht verfügbar"}

        belief_name = f"belief_{len(self.reasoning.bayesian.beliefs)}"
        self.reasoning.bayesian.add_belief(belief_name, belief, prior)
        self.reasoning.bayesian.update_belief(
            belief_name, evidence, likelihood_true, likelihood_false
        )

        return {
            "belief": belief,
            "prior": prior,
            "evidence": evidence,
            "posterior": self.reasoning.bayesian.beliefs[belief_name].posterior,
            "confidence_level": self.reasoning.bayesian.get_confidence_level(belief_name),
            "entropy": self.reasoning.bayesian.entropy(belief_name)
        }

    def causal_analysis(self, cause: str, effect: str,
                         variables: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Analysiert kausale Beziehungen.

        Args:
            cause: Potentielle Ursache
            effect: Beobachteter Effekt
            variables: Zusätzliche Variablen

        Returns:
            Kausale Analyse
        """
        if not ADVANCED_REASONING_AVAILABLE or not self.reasoning:
            return {"error": "Advanced Reasoning nicht verfügbar"}

        # Füge Variablen hinzu
        self.reasoning.causal.add_variable(cause, f"Ursache: {cause}")
        self.reasoning.causal.add_variable(effect, f"Effekt: {effect}")

        if variables:
            for var in variables:
                self.reasoning.causal.add_variable(
                    var.get("name", "unknown"),
                    var.get("description", "")
                )

        # Füge kausale Verbindung hinzu
        self.reasoning.causal.add_causal_link(cause, effect)

        return {
            "cause": cause,
            "effect": effect,
            "explanation": self.reasoning.causal.explain_causal_relationship(cause, effect),
            "confounders": self.reasoning.causal.find_confounders(cause, effect),
            "causal_chains": self.reasoning.causal.trace_causal_chain(cause, effect)
        }

    def dialectical_reasoning(self, thesis: str, thesis_args: List[str],
                                antithesis_args: List[str] = None) -> Dict[str, Any]:
        """
        Führt dialektisches Reasoning durch.

        Args:
            thesis: Die Ausgangsthese
            thesis_args: Argumente für die These
            antithesis_args: Optionale Gegenargumente

        Returns:
            Dialektische Analyse mit Synthese
        """
        if not ADVANCED_REASONING_AVAILABLE or not self.reasoning:
            return {"error": "Advanced Reasoning nicht verfügbar"}

        # Erstelle These
        thesis_pos = self.reasoning.dialectical.propose_thesis(thesis, thesis_args)

        # Generiere Antithese-Vorschläge wenn keine gegeben
        if not antithesis_args:
            antithesis_args = self.reasoning.dialectical.generate_antithesis_suggestions(thesis_pos)[:2]

        # Erstelle Antithese
        antithesis_content = f"Gegenposition zu: {thesis}"
        antithesis_pos = self.reasoning.dialectical.propose_antithesis(
            thesis_pos, antithesis_content, antithesis_args
        )

        # Synthese
        synthesis = self.reasoning.dialectical.synthesize(thesis_pos, antithesis_pos)

        return {
            "thesis": thesis,
            "thesis_strength": thesis_pos.strength,
            "antithesis": antithesis_content,
            "antithesis_strength": antithesis_pos.strength,
            "synthesis": synthesis.content,
            "synthesis_strength": synthesis.strength,
            "synthesis_arguments": synthesis.arguments
        }

    # -------------------------------------------------------------------------
    # ANALYTICAL METHODS
    # -------------------------------------------------------------------------

    def mece_breakdown(self, problem: str,
                        categories: List[str] = None) -> Dict[str, Any]:
        """
        Erstellt eine MECE-Zerlegung eines Problems.

        Args:
            problem: Das zu analysierende Problem
            categories: Optionale vordefinierte Kategorien

        Returns:
            MECE-Analyse
        """
        if not ANALYTICAL_STRATEGIES_AVAILABLE or not self.analytics:
            return {"error": "Analytical Strategies nicht verfügbar"}

        # Hole Framework-Vorschlag wenn keine Kategorien gegeben
        if not categories:
            framework_name, categories = self.analytics.mece.suggest_framework(problem)
        else:
            framework_name = "custom"

        result = self.analytics.mece.create_mece_breakdown(problem, categories)

        return {
            "problem": problem,
            "framework": framework_name,
            "categories": [c.name for c in result.categories],
            "status": result.status.value,
            "coverage": result.total_coverage,
            "overlaps": result.overlaps,
            "gaps": result.gaps,
            "summary": self.analytics.mece.get_mece_summary(result)
        }

    def root_cause_analysis(self, problem: str,
                             known_causes: List[str] = None) -> Dict[str, Any]:
        """
        Führt eine Root Cause Analysis durch.

        Args:
            problem: Das Problem
            known_causes: Bekannte Ursachen

        Returns:
            RCA-Ergebnis
        """
        if not ANALYTICAL_STRATEGIES_AVAILABLE or not self.analytics:
            return {"error": "Analytical Strategies nicht verfügbar"}

        result = self.analytics.rca.full_root_cause_analysis(
            problem, known_causes or []
        )

        return {
            "problem": problem,
            "root_causes": result.root_causes,
            "identified_causes": result.identified_causes,
            "recommendations": result.recommended_actions,
            "confidence": result.confidence,
            "summary": self.analytics.rca.get_rca_summary(result)
        }

    def morphological_exploration(self, problem: str,
                                    parameters: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Führt eine morphologische Analyse durch.

        Args:
            problem: Das Problem
            parameters: Parameter mit Optionen

        Returns:
            Morphologische Lösungen
        """
        if not ANALYTICAL_STRATEGIES_AVAILABLE or not self.analytics:
            return {"error": "Analytical Strategies nicht verfügbar"}

        from holo_analytical_strategies import MorphologicalParameter, MorphologicalDimension

        # Konvertiere Parameter
        morph_params = []
        if parameters:
            for p in parameters:
                morph_params.append(MorphologicalParameter(
                    name=p.get("name", "Parameter"),
                    dimension=MorphologicalDimension.FUNCTION,
                    options=p.get("options", ["Option A", "Option B"])
                ))
        else:
            # Default-Parameter
            morph_params = [
                MorphologicalParameter("Ansatz", MorphologicalDimension.FUNCTION,
                                       ["Präventiv", "Reaktiv", "Adaptiv"]),
                MorphologicalParameter("Umfang", MorphologicalDimension.RESOURCE,
                                       ["Minimal", "Moderat", "Umfassend"]),
                MorphologicalParameter("Zeitrahmen", MorphologicalDimension.CONSTRAINT,
                                       ["Sofort", "Kurzfristig", "Langfristig"])
            ]

        box = self.analytics.morphological.create_morphological_box(problem, morph_params)
        solutions = self.analytics.morphological.generate_targeted_solutions(problem, n_solutions=5)

        return {
            "problem": problem,
            "parameters": len(morph_params),
            "total_combinations": box["total_combinations"],
            "top_solutions": [
                {
                    "configuration": sol.parameters,
                    "feasibility": sol.feasibility_score,
                    "novelty": sol.novelty_score
                }
                for sol in solutions[:5]
            ],
            "summary": self.analytics.morphological.get_morphological_summary(problem)
        }

    # -------------------------------------------------------------------------
    # OPTIMIZATION METHODS
    # -------------------------------------------------------------------------

    def optimize_function(self, objective_name: str,
                           dimensions: int = 5,
                           bounds: List[Tuple[float, float]] = None,
                           method: str = "pso") -> Dict[str, Any]:
        """
        Optimiert eine Benchmark-Funktion.

        Args:
            objective_name: "sphere", "rastrigin", "rosenbrock", "ackley"
            dimensions: Anzahl Dimensionen
            bounds: Suchraum-Grenzen
            method: "pso" oder "sa"

        Returns:
            Optimierungsergebnis
        """
        if not APPROXIMATION_AVAILABLE or not self.approximation:
            return {"error": "Approximation nicht verfügbar"}

        # Wähle Zielfunktion
        objectives = {
            "sphere": BenchmarkFunctions.sphere,
            "rastrigin": BenchmarkFunctions.rastrigin,
            "rosenbrock": BenchmarkFunctions.rosenbrock,
            "ackley": BenchmarkFunctions.ackley,
        }

        objective = objectives.get(objective_name.lower(), BenchmarkFunctions.sphere)
        bounds = bounds or [(-5, 5)] * dimensions

        result = self.approximation.solve_continuous_optimization(
            objective, dimensions, bounds, method=method
        )

        return {
            "objective": objective_name,
            "method": method,
            "dimensions": dimensions,
            "best_value": result.best_solution.value,
            "best_position": result.best_solution.state[:5] if result.best_solution.state else [],
            "iterations": result.iterations,
            "status": result.status.value,
            "time_ms": result.elapsed_time_ms
        }

    # -------------------------------------------------------------------------
    # AXIOMATIC METHODS
    # -------------------------------------------------------------------------

    def learn_knowledge(self, proposition: str, certainty: float = 0.8,
                         agent: str = "Holo") -> Dict[str, Any]:
        """
        Fügt Wissen zum epistemischen System hinzu.

        Args:
            proposition: Die zu lernende Aussage
            certainty: Gewissheitsgrad (0-1)
            agent: Der lernende Agent

        Returns:
            Lernbestätigung
        """
        if not FORMAL_AXIOMS_AVAILABLE or not self.axioms:
            return {"error": "Formal Axioms nicht verfügbar"}

        self.axioms.epistemic.learn(agent, proposition, certainty)

        knows = self.axioms.epistemic.knows(agent, proposition)
        believes = self.axioms.epistemic.believes(agent, proposition)

        return {
            "proposition": proposition,
            "certainty": certainty,
            "agent": agent,
            "is_knowledge": knows,
            "is_belief": believes,
            "status": "Wissen" if knows else "Glaube" if believes else "Unsicher"
        }

    def evaluate_ethics(self, action: str,
                         context: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Bewertet eine Handlung ethisch.

        Args:
            action: Die zu bewertende Handlung
            context: Kontextbedingungen

        Returns:
            Ethische Bewertung
        """
        if not FORMAL_AXIOMS_AVAILABLE or not self.axioms:
            return {"error": "Formal Axioms nicht verfügbar"}

        result = self.axioms.ethics.evaluate_action(action, context)

        return {
            "action": action,
            "verdict": result["status"],
            "reasoning": result["reasoning"],
            "confidence": result["confidence"],
            "conflicts": len(result.get("conflicts", [])),
            "applicable_axioms": [
                a.name for a in self.axioms.list_axioms_by_category(AxiomCategory.ETHICS)[:3]
            ]
        }

    def logical_inference(self, premises: List[str],
                           rule: str = "modus_ponens") -> Dict[str, Any]:
        """
        Führt logische Schlussfolgerung durch.

        Args:
            premises: Die Prämissen
            rule: Schlussregel

        Returns:
            Inferenz-Ergebnis
        """
        if not FORMAL_AXIOMS_AVAILABLE or not self.axioms:
            return {"error": "Formal Axioms nicht verfügbar"}

        from holo_formal_axioms import InferenceRule

        rule_map = {
            "modus_ponens": InferenceRule.MODUS_PONENS,
            "modus_tollens": InferenceRule.MODUS_TOLLENS,
            "conjunction": InferenceRule.CONJUNCTION,
            "simplification": InferenceRule.SIMPLIFICATION,
        }

        inference_rule = rule_map.get(rule.lower(), InferenceRule.MODUS_PONENS)
        result = self.axioms.logic.apply_inference(inference_rule, premises)

        if result:
            return {
                "premises": premises,
                "rule": rule,
                "conclusion": result.conclusion,
                "valid": result.is_valid,
                "explanation": result.explanation
            }
        else:
            return {
                "premises": premises,
                "rule": rule,
                "conclusion": None,
                "valid": False,
                "explanation": "Schlussregel konnte nicht angewendet werden"
            }

    # -------------------------------------------------------------------------
    # INTEGRATED COGNITIVE PROCESSING
    # -------------------------------------------------------------------------

    def process(self, task: CognitiveTask) -> CognitiveResult:
        """
        Verarbeitet eine kognitive Aufgabe mit den passenden Modulen.

        Args:
            task: Die zu verarbeitende Aufgabe

        Returns:
            Kognitives Ergebnis
        """
        start_time = datetime.now()
        reasoning_trace = []
        modules_used = []
        conclusion_parts = []

        # 1. Reasoning (wenn nötig)
        if task.requires_reasoning and ADVANCED_REASONING_AVAILABLE and self.reasoning:
            reasoning_result = self.reasoning.reason(
                task.description,
                task.context
            )
            reasoning_trace.append(f"Reasoning: {reasoning_result.get('modes_used', [])}")
            modules_used.append("advanced_reasoning")

            if "bayesian" in reasoning_result.get("results", {}):
                conclusion_parts.append(
                    f"Bayesian: {reasoning_result['results']['bayesian'].get('confidence_level', 'unbekannt')}"
                )

        # 2. Analyse (wenn nötig)
        if task.requires_analysis and ANALYTICAL_STRATEGIES_AVAILABLE and self.analytics:
            analysis_result = self.analytics.analyze_problem(
                task.description,
                AnalysisType.COMBINED
            )
            reasoning_trace.append(f"Analyse: {list(analysis_result.get('analyses', {}).keys())}")
            modules_used.append("analytical_strategies")

            if "mece" in analysis_result.get("analyses", {}):
                conclusion_parts.append(
                    f"MECE: {analysis_result['analyses']['mece'].get('status', 'unbekannt')}"
                )

        # 3. Ethik (wenn nötig)
        if task.requires_ethics and FORMAL_AXIOMS_AVAILABLE and self.axioms:
            ethics_result = self.axioms.ethics.evaluate_action(
                task.description,
                task.context
            )
            reasoning_trace.append(f"Ethik: {ethics_result.get('status', 'unbekannt')}")
            modules_used.append("formal_axioms")
            conclusion_parts.append(f"Ethisch: {ethics_result.get('status', 'erlaubt')}")

        # Ergebnis zusammenstellen
        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        conclusion = " | ".join(conclusion_parts) if conclusion_parts else "Verarbeitung abgeschlossen"

        result = CognitiveResult(
            task=task,
            conclusion=conclusion,
            reasoning_trace=reasoning_trace,
            confidence=0.7,
            modules_used=modules_used,
            processing_time_ms=elapsed
        )

        self.processing_history.append(result)
        return result

    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------

    def get_capabilities(self) -> Dict[str, Any]:
        """Gibt verfügbare Fähigkeiten zurück"""
        capabilities = {
            "reasoning": {
                "available": ADVANCED_REASONING_AVAILABLE,
                "modes": ["bayesian", "causal", "metacognitive", "dialectical"]
                         if ADVANCED_REASONING_AVAILABLE else []
            },
            "analytics": {
                "available": ANALYTICAL_STRATEGIES_AVAILABLE,
                "strategies": ["mece", "root_cause", "morphological"]
                              if ANALYTICAL_STRATEGIES_AVAILABLE else []
            },
            "optimization": {
                "available": APPROXIMATION_AVAILABLE,
                "algorithms": ["simulated_annealing", "pso", "branch_and_bound"]
                              if APPROXIMATION_AVAILABLE else []
            },
            "axioms": {
                "available": FORMAL_AXIOMS_AVAILABLE,
                "categories": ["epistemic", "logic", "ethics", "learning"]
                              if FORMAL_AXIOMS_AVAILABLE else []
            }
        }
        return capabilities

    def get_summary(self) -> str:
        """Gibt eine Zusammenfassung des Systems"""
        summary = ["=" * 60]
        summary.append("EXTENDED COGNITION ENGINE - Status")
        summary.append("=" * 60)

        capabilities = self.get_capabilities()

        for module, info in capabilities.items():
            status = "✓" if info["available"] else "✗"
            summary.append(f"\n{status} {module.upper()}")
            if info["available"]:
                items = info.get("modes") or info.get("strategies") or info.get("algorithms") or info.get("categories", [])
                for item in items:
                    summary.append(f"    • {item}")

        summary.append(f"\nVerarbeitete Aufgaben: {len(self.processing_history)}")
        summary.append(f"Aktueller Modus: {self.current_mode.value}")

        return "\n".join(summary)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_engine_instance: Optional[ExtendedCognitionEngine] = None


def get_extended_cognition_engine() -> ExtendedCognitionEngine:
    """
    Gibt die Singleton-Instanz der Extended Cognition Engine zurück.
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ExtendedCognitionEngine()
    return _engine_instance


def create_extended_cognition_engine() -> ExtendedCognitionEngine:
    """
    Erstellt eine neue Extended Cognition Engine.
    """
    return ExtendedCognitionEngine()


# =============================================================================
# BEISPIEL / TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🧠 Extended Cognition Engine - Demo\n")

    engine = get_extended_cognition_engine()

    # Zeige Fähigkeiten
    print("Verfügbare Fähigkeiten:")
    print("-" * 40)
    for module, info in engine.get_capabilities().items():
        status = "✓" if info["available"] else "✗"
        print(f"  {status} {module}")

    # Test Bayesian Update
    print("\n--- Bayesian Update ---")
    result = engine.bayesian_update(
        belief="Es wird morgen regnen",
        prior=0.3,
        evidence="Dunkle Wolken am Himmel",
        likelihood_true=0.8,
        likelihood_false=0.2
    )
    print(f"Prior: {result.get('prior', 'N/A')} → Posterior: {result.get('posterior', 'N/A'):.3f}")
    print(f"Konfidenz: {result.get('confidence_level', 'N/A')}")

    # Test Dialektisches Reasoning
    print("\n--- Dialektisches Reasoning ---")
    result = engine.dialectical_reasoning(
        thesis="KI sollte streng reguliert werden",
        thesis_args=["Sicherheit", "Kontrolle", "Verantwortung"]
    )
    print(f"These: {result.get('thesis', 'N/A')[:50]}...")
    print(f"Synthese-Stärke: {result.get('synthesis_strength', 'N/A'):.2f}")

    # Test MECE
    print("\n--- MECE Breakdown ---")
    result = engine.mece_breakdown("Wie steigern wir den Umsatz?")
    print(f"Framework: {result.get('framework', 'N/A')}")
    print(f"Kategorien: {result.get('categories', [])}")

    # Test Root Cause Analysis
    print("\n--- Root Cause Analysis ---")
    result = engine.root_cause_analysis(
        "Kundenbeschwerden nehmen zu",
        ["Lange Wartezeiten", "Produktqualität"]
    )
    print(f"Root Causes: {result.get('root_causes', [])}")

    # Test Ethik
    print("\n--- Ethische Bewertung ---")
    result = engine.evaluate_ethics("anderen helfen")
    print(f"Handlung: {result.get('action', 'N/A')}")
    print(f"Bewertung: {result.get('verdict', 'N/A')}")

    # Test Logische Inferenz
    print("\n--- Logische Inferenz ---")
    result = engine.logical_inference(
        premises=["Es regnet", "Es regnet → Die Straße ist nass"],
        rule="modus_ponens"
    )
    print(f"Prämissen: {result.get('premises', [])}")
    print(f"Konklusion: {result.get('conclusion', 'N/A')}")

    # Zusammenfassung
    print("\n" + engine.get_summary())
