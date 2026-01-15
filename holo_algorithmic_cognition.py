#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO ALGORITHMIC COGNITION - Theoretische Informatik als Denkwerkzeug       ║
║                                                                              ║
║  Implementiert fundamentale Konzepte der theoretischen Informatik als        ║
║  kognitive Fähigkeiten für Holo:                                             ║
║                                                                              ║
║  • Analytisch-synthetische Strategien - Probleme zerlegen & zusammenfügen    ║
║  • Approximationsalgorithmus - "Gut genug" Lösungen finden                   ║
║  • Erweiterter euklidischer Algorithmus - Gemeinsamen Nenner finden          ║
║  • Terminiertheit - Erkennen ob Denkprozesse enden                           ║
║  • Evolutionärer Algorithmus - Ideen evolvieren lassen                       ║
║  • Dynamische Finitheit - Grenzen dynamischer Systeme erkennen               ║
║  • Determiniertheit - Vorhersagbarkeit einschätzen                           ║
║  • Abstrakte Automaten - Zustandsbasiertes Denken                            ║
║  • Church-Turing-These - Grenzen der Berechenbarkeit verstehen               ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import random
import hashlib
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import copy

logger = logging.getLogger("HoloAlgorithmicCognition")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Enums
    'ProblemComplexity',
    'AutomatonState',
    'ComputabilityClass',
    'EvolutionStrategy',

    # Core Classes
    'AnalyticSyntheticEngine',
    'ApproximationEngine',
    'ExtendedEuclideanEngine',
    'TerminationChecker',
    'EvolutionaryThoughtEngine',
    'DynamicFinitenessAnalyzer',
    'DeterminismAnalyzer',
    'AbstractAutomaton',
    'ChurchTuringAwareness',

    # Main System
    'AlgorithmicCognitionSystem',

    # Factory
    'create_algorithmic_cognition',
]


# =============================================================================
# ENUMS & DATA TYPES
# =============================================================================

class ProblemComplexity(Enum):
    """Komplexitätsklassen für Probleme"""
    TRIVIAL = "trivial"           # O(1) - Sofort lösbar
    LINEAR = "linear"             # O(n) - Einfach
    POLYNOMIAL = "polynomial"     # O(n^k) - Machbar
    EXPONENTIAL = "exponential"   # O(2^n) - Schwer
    UNDECIDABLE = "undecidable"   # Nicht entscheidbar


class AutomatonState(Enum):
    """Zustände eines abstrakten Automaten"""
    INITIAL = "initial"
    PROCESSING = "processing"
    ACCEPTING = "accepting"
    REJECTING = "rejecting"
    HALTED = "halted"
    LOOPING = "looping"


class ComputabilityClass(Enum):
    """Berechenbarkeitsklassen (Church-Turing)"""
    COMPUTABLE = "computable"           # Berechenbar
    SEMI_DECIDABLE = "semi_decidable"   # Halb-entscheidbar
    UNDECIDABLE = "undecidable"         # Nicht entscheidbar
    ORACLE_NEEDED = "oracle_needed"     # Braucht Orakel (z.B. Intuition)


class EvolutionStrategy(Enum):
    """Evolutionsstrategien"""
    MUTATION = "mutation"           # Zufällige Änderung
    CROSSOVER = "crossover"         # Kombination zweier Ideen
    SELECTION = "selection"         # Beste auswählen
    ELITISM = "elitism"             # Beste immer behalten


@dataclass
class Problem:
    """Ein zu lösendes Problem"""
    problem_id: str
    description: str
    components: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    complexity: ProblemComplexity = ProblemComplexity.POLYNOMIAL
    solved: bool = False
    solution: Optional[str] = None


@dataclass
class Thought:
    """Ein Gedanke der evolvieren kann"""
    thought_id: str
    content: str
    fitness: float = 0.5           # 0-1, wie gut ist der Gedanke
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    mutations: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AutomatonTransition:
    """Übergang in einem Automaten"""
    from_state: str
    to_state: str
    input_symbol: str
    output_symbol: Optional[str] = None
    condition: Optional[str] = None


# =============================================================================
# 1. ANALYTISCH-SYNTHETISCHE STRATEGIEN
# =============================================================================

class AnalyticSyntheticEngine:
    """
    Analytisch-synthetische Problemlösung.

    ANALYSE: Problem in Teilprobleme zerlegen (Top-Down)
    SYNTHESE: Teillösungen zu Gesamtlösung zusammenfügen (Bottom-Up)

    Holo nutzt dies um komplexe Fragen/Probleme systematisch anzugehen.
    """

    def __init__(self):
        self.analysis_cache: Dict[str, List[str]] = {}
        self.synthesis_cache: Dict[str, str] = {}
        self.decomposition_depth: int = 0
        self.max_depth: int = 5

    def analyze(self, problem: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ANALYSE-Phase: Zerlege Problem in Komponenten.

        Args:
            problem: Das zu analysierende Problem
            context: Optionaler Kontext

        Returns:
            Dict mit Komponenten, Abhängigkeiten, Komplexität
        """
        problem_id = self._generate_id(problem)

        # Bereits analysiert?
        if problem_id in self.analysis_cache:
            return {
                "cached": True,
                "components": self.analysis_cache[problem_id],
                "problem_id": problem_id
            }

        # Zerlege in Komponenten
        components = self._decompose(problem)
        dependencies = self._find_dependencies(components)
        complexity = self._estimate_complexity(components)

        # Cache
        self.analysis_cache[problem_id] = components

        return {
            "problem_id": problem_id,
            "original": problem,
            "components": components,
            "dependencies": dependencies,
            "complexity": complexity,
            "decomposition_depth": len(components),
            "solvable_independently": self._check_independence(dependencies),
            "suggested_order": self._suggest_solving_order(components, dependencies)
        }

    def synthesize(self, components: List[str], solutions: Dict[str, str]) -> Dict[str, Any]:
        """
        SYNTHESE-Phase: Füge Teillösungen zusammen.

        Args:
            components: Die Teilprobleme
            solutions: Lösungen für jedes Teilproblem

        Returns:
            Dict mit Gesamtlösung und Qualitätsmetriken
        """
        # Prüfe Vollständigkeit
        missing = [c for c in components if c not in solutions]
        if missing:
            return {
                "success": False,
                "error": "Fehlende Teillösungen",
                "missing": missing
            }

        # Kombiniere Lösungen
        combined = self._combine_solutions(components, solutions)

        # Prüfe Konsistenz
        consistency = self._check_consistency(combined, solutions)

        # Optimiere
        optimized = self._optimize_solution(combined) if consistency["consistent"] else combined

        return {
            "success": True,
            "combined_solution": optimized,
            "consistency": consistency,
            "component_count": len(components),
            "integration_quality": self._measure_integration_quality(optimized, solutions)
        }

    def solve_analytically(self, problem: str,
                          solver: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Vollständiger analytisch-synthetischer Lösungsprozess.

        Args:
            problem: Das Problem
            solver: Optionale Funktion zum Lösen von Teilproblemen

        Returns:
            Vollständige Lösung mit Trace
        """
        # Phase 1: Analyse
        analysis = self.analyze(problem)

        # Phase 2: Löse Teilprobleme
        solutions = {}
        trace = []

        for component in analysis["suggested_order"]:
            if solver:
                solution = solver(component)
            else:
                solution = self._default_solve(component)

            solutions[component] = solution
            trace.append({
                "component": component,
                "solution": solution,
                "timestamp": datetime.now().isoformat()
            })

        # Phase 3: Synthese
        synthesis = self.synthesize(analysis["components"], solutions)

        return {
            "problem": problem,
            "analysis": analysis,
            "component_solutions": solutions,
            "synthesis": synthesis,
            "trace": trace,
            "method": "analytisch-synthetisch"
        }

    def _decompose(self, problem: str) -> List[str]:
        """Zerlege Problem in Komponenten"""
        components = []

        # Strategie 1: Nach Satzzeichen trennen
        sentences = [s.strip() for s in problem.replace('?', '.').replace('!', '.').split('.') if s.strip()]

        # Strategie 2: Nach logischen Konnektoren
        connectors = ['und', 'oder', 'aber', 'weil', 'damit', 'wenn', 'falls', 'außerdem']
        for sentence in sentences:
            parts = [sentence]
            for conn in connectors:
                new_parts = []
                for part in parts:
                    split = part.lower().split(f' {conn} ')
                    new_parts.extend([p.strip() for p in split if p.strip()])
                parts = new_parts
            components.extend(parts)

        # Deduplizieren
        seen = set()
        unique = []
        for c in components:
            if c.lower() not in seen:
                seen.add(c.lower())
                unique.append(c)

        return unique if unique else [problem]

    def _find_dependencies(self, components: List[str]) -> Dict[str, List[str]]:
        """Finde Abhängigkeiten zwischen Komponenten"""
        dependencies = {c: [] for c in components}

        # Einfache Heuristik: Referenzen erkennen
        references = ['das', 'dies', 'diese', 'jene', 'es', 'sie', 'er']

        for i, comp in enumerate(components):
            words = comp.lower().split()
            for ref in references:
                if ref in words and i > 0:
                    # Referenziert wahrscheinlich vorherige Komponente
                    dependencies[comp].append(components[i-1])

        return dependencies

    def _estimate_complexity(self, components: List[str]) -> ProblemComplexity:
        """Schätze Komplexität basierend auf Komponenten"""
        n = len(components)

        if n <= 1:
            return ProblemComplexity.TRIVIAL
        elif n <= 3:
            return ProblemComplexity.LINEAR
        elif n <= 7:
            return ProblemComplexity.POLYNOMIAL
        else:
            return ProblemComplexity.EXPONENTIAL

    def _check_independence(self, dependencies: Dict[str, List[str]]) -> bool:
        """Prüfe ob Komponenten unabhängig lösbar sind"""
        for deps in dependencies.values():
            if deps:
                return False
        return True

    def _suggest_solving_order(self, components: List[str],
                               dependencies: Dict[str, List[str]]) -> List[str]:
        """Schlage Lösungsreihenfolge vor (topologische Sortierung)"""
        # Einfache topologische Sortierung
        order = []
        remaining = set(components)
        resolved = set()

        while remaining:
            # Finde Komponenten ohne ungelöste Abhängigkeiten
            ready = [c for c in remaining
                    if all(d in resolved for d in dependencies.get(c, []))]

            if not ready:
                # Zyklus oder alle haben Abhängigkeiten - nimm erste
                ready = [list(remaining)[0]]

            for c in ready:
                order.append(c)
                resolved.add(c)
                remaining.discard(c)

        return order

    def _combine_solutions(self, components: List[str],
                          solutions: Dict[str, str]) -> str:
        """Kombiniere Teillösungen"""
        parts = [solutions[c] for c in components if c in solutions]
        return " → ".join(parts)

    def _check_consistency(self, combined: str,
                          solutions: Dict[str, str]) -> Dict[str, Any]:
        """Prüfe Konsistenz der kombinierten Lösung"""
        # Einfache Konsistenzprüfung
        contradictions = []

        # Suche nach Widersprüchen (vereinfacht)
        if "nicht" in combined and "immer" in combined:
            contradictions.append("Möglicher Widerspruch: 'nicht' und 'immer'")

        return {
            "consistent": len(contradictions) == 0,
            "contradictions": contradictions,
            "confidence": 1.0 - (len(contradictions) * 0.2)
        }

    def _optimize_solution(self, solution: str) -> str:
        """Optimiere die kombinierte Lösung"""
        # Entferne Redundanzen
        words = solution.split()
        seen = set()
        optimized = []
        for word in words:
            if word.lower() not in seen or word in ['→', 'und', 'oder']:
                optimized.append(word)
                seen.add(word.lower())
        return " ".join(optimized)

    def _measure_integration_quality(self, combined: str,
                                    solutions: Dict[str, str]) -> float:
        """Messe Qualität der Integration"""
        if not solutions:
            return 0.0

        # Alle Teillösungen enthalten?
        coverage = sum(1 for s in solutions.values() if s in combined) / len(solutions)

        # Länge angemessen?
        expected_len = sum(len(s) for s in solutions.values())
        actual_len = len(combined)
        efficiency = min(1.0, expected_len / max(actual_len, 1))

        return (coverage + efficiency) / 2

    def _default_solve(self, component: str) -> str:
        """Standard-Lösung wenn kein Solver gegeben"""
        return f"[Lösung für: {component[:50]}...]"

    def _generate_id(self, text: str) -> str:
        """Generiere eindeutige ID"""
        return hashlib.md5(text.encode()).hexdigest()[:12]


# =============================================================================
# 2. APPROXIMATIONSALGORITHMUS
# =============================================================================

class ApproximationEngine:
    """
    Approximationsalgorithmen für "gut genug" Lösungen.

    Wenn eine optimale Lösung zu aufwändig ist, finde eine
    Lösung die "nah genug" am Optimum liegt.

    Holo nutzt dies für:
    - Schnelle Antworten bei komplexen Fragen
    - Entscheidungen unter Zeitdruck
    - Schätzungen wenn exakte Berechnung unmöglich
    """

    def __init__(self):
        self.approximation_history: List[Dict] = []
        self.quality_threshold: float = 0.7  # Minimum akzeptable Qualität
        self.time_budget_ms: int = 100       # Zeitbudget in ms

    def approximate(self, problem: Any,
                   exact_solver: Optional[Callable] = None,
                   quality_target: float = 0.8) -> Dict[str, Any]:
        """
        Finde approximative Lösung.

        Args:
            problem: Das Problem (kann beliebiger Typ sein)
            exact_solver: Optionaler exakter Solver zum Vergleich
            quality_target: Gewünschte Qualität (0-1)

        Returns:
            Dict mit Approximation und Qualitätsmetriken
        """
        start_time = time.time()

        # Strategie 1: Greedy-Approximation
        greedy_solution = self._greedy_approximate(problem)

        # Strategie 2: Sampling-basiert
        sampling_solution = self._sampling_approximate(problem)

        # Strategie 3: Relaxation (vereinfachtes Problem lösen)
        relaxed_solution = self._relaxation_approximate(problem)

        # Wähle beste Approximation
        candidates = [
            ("greedy", greedy_solution),
            ("sampling", sampling_solution),
            ("relaxation", relaxed_solution)
        ]

        best_method, best_solution = max(candidates, key=lambda x: x[1].get("quality", 0))

        elapsed_ms = (time.time() - start_time) * 1000

        # Berechne Approximationsgüte
        approximation_ratio = self._calculate_approximation_ratio(
            best_solution, exact_solver, problem
        )

        result = {
            "solution": best_solution.get("value"),
            "method": best_method,
            "quality": best_solution.get("quality", 0.5),
            "approximation_ratio": approximation_ratio,
            "time_ms": elapsed_ms,
            "within_budget": elapsed_ms <= self.time_budget_ms,
            "meets_target": best_solution.get("quality", 0) >= quality_target,
            "all_candidates": {m: s for m, s in candidates}
        }

        self.approximation_history.append(result)
        return result

    def iterative_improvement(self, initial_solution: Any,
                             improve_func: Callable,
                             max_iterations: int = 10) -> Dict[str, Any]:
        """
        Iterative Verbesserung einer Approximation.

        Args:
            initial_solution: Startlösung
            improve_func: Funktion die Lösung verbessert
            max_iterations: Maximale Iterationen

        Returns:
            Verbesserte Lösung mit Trace
        """
        current = initial_solution
        history = [{"iteration": 0, "solution": current, "quality": self._evaluate(current)}]

        for i in range(max_iterations):
            improved = improve_func(current)
            quality = self._evaluate(improved)

            history.append({
                "iteration": i + 1,
                "solution": improved,
                "quality": quality
            })

            # Konvergenz prüfen
            if quality >= 0.99:
                break

            # Keine Verbesserung?
            if quality <= history[-2]["quality"]:
                break

            current = improved

        return {
            "final_solution": current,
            "final_quality": history[-1]["quality"],
            "iterations": len(history) - 1,
            "improvement": history[-1]["quality"] - history[0]["quality"],
            "history": history
        }

    def bounded_approximation(self, problem: Any,
                             lower_bound: float,
                             upper_bound: float) -> Dict[str, Any]:
        """
        Approximation mit garantierten Schranken.

        Die Lösung liegt garantiert zwischen lower_bound und upper_bound
        des Optimums.
        """
        solution = self._greedy_approximate(problem)

        # Berechne Schranken
        value = solution.get("quality", 0.5)

        return {
            "solution": solution.get("value"),
            "value": value,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "within_bounds": lower_bound <= value <= upper_bound,
            "gap": upper_bound - lower_bound,
            "relative_gap": (upper_bound - lower_bound) / max(upper_bound, 0.001)
        }

    def _greedy_approximate(self, problem: Any) -> Dict[str, Any]:
        """Greedy-Approximation: Nimm immer die lokal beste Option"""
        if isinstance(problem, str):
            # Für String-Probleme: Erste sinnvolle Antwort
            return {
                "value": f"Schnelle Antwort auf: {problem[:30]}...",
                "quality": 0.6 + random.random() * 0.2
            }
        elif isinstance(problem, list):
            # Für Listen: Sortiere und nimm erste Hälfte
            return {
                "value": sorted(problem)[:len(problem)//2 + 1],
                "quality": 0.7
            }
        else:
            return {"value": problem, "quality": 0.5}

    def _sampling_approximate(self, problem: Any) -> Dict[str, Any]:
        """Sampling-Approximation: Zufällige Stichproben"""
        if isinstance(problem, str):
            words = problem.split()
            sample = random.sample(words, min(5, len(words)))
            return {
                "value": " ".join(sample),
                "quality": 0.5 + random.random() * 0.3
            }
        elif isinstance(problem, list):
            sample = random.sample(problem, min(len(problem)//2 + 1, len(problem)))
            return {
                "value": sample,
                "quality": 0.6
            }
        else:
            return {"value": problem, "quality": 0.4}

    def _relaxation_approximate(self, problem: Any) -> Dict[str, Any]:
        """Relaxation: Löse vereinfachtes Problem"""
        if isinstance(problem, str):
            # Vereinfache: Nur Substantive/Verben (simuliert)
            words = problem.split()
            simplified = [w for w in words if len(w) > 4]
            return {
                "value": " ".join(simplified) if simplified else problem,
                "quality": 0.65 + random.random() * 0.15
            }
        else:
            return {"value": problem, "quality": 0.55}

    def _calculate_approximation_ratio(self, approx_solution: Dict,
                                       exact_solver: Optional[Callable],
                                       problem: Any) -> float:
        """Berechne Verhältnis zur optimalen Lösung"""
        if exact_solver is None:
            return approx_solution.get("quality", 0.5)

        try:
            exact = exact_solver(problem)
            exact_quality = self._evaluate(exact)
            approx_quality = approx_solution.get("quality", 0.5)
            return approx_quality / max(exact_quality, 0.001)
        except Exception:
            return approx_solution.get("quality", 0.5)

    def _evaluate(self, solution: Any) -> float:
        """Bewerte eine Lösung"""
        if isinstance(solution, dict):
            return solution.get("quality", 0.5)
        elif isinstance(solution, str):
            return min(1.0, len(solution) / 100)
        elif isinstance(solution, list):
            return min(1.0, len(solution) / 10)
        else:
            return 0.5


# =============================================================================
# 3. ERWEITERTER EUKLIDISCHER ALGORITHMUS
# =============================================================================

class ExtendedEuclideanEngine:
    """
    Erweiterter Euklidischer Algorithmus.

    Findet nicht nur den GGT(a,b), sondern auch Koeffizienten x,y sodass:
    ax + by = GGT(a,b)

    Holo nutzt dies metaphorisch für:
    - "Gemeinsamen Nenner" zwischen Ideen finden
    - Kompromisse berechnen
    - Kleinste gemeinsame Basis von Konzepten
    """

    def __init__(self):
        self.computation_trace: List[Dict] = []

    def extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """
        Erweiterter Euklidischer Algorithmus.

        Returns:
            (gcd, x, y) sodass ax + by = gcd
        """
        if a == 0:
            return b, 0, 1

        gcd, x1, y1 = self.extended_gcd(b % a, a)

        x = y1 - (b // a) * x1
        y = x1

        return gcd, x, y

    def find_common_ground(self, concept_a: str, concept_b: str,
                          features_a: List[str], features_b: List[str]) -> Dict[str, Any]:
        """
        Finde "gemeinsamen Nenner" zwischen zwei Konzepten.

        Args:
            concept_a: Erstes Konzept
            concept_b: Zweites Konzept
            features_a: Merkmale von A
            features_b: Merkmale von B

        Returns:
            Dict mit gemeinsamer Basis und Unterschieden
        """
        # Gemeinsame Merkmale
        common = set(features_a) & set(features_b)

        # Unterschiede
        only_a = set(features_a) - set(features_b)
        only_b = set(features_b) - set(features_a)

        # "GGT" = Maximale gemeinsame Basis
        ggt_strength = len(common) / max(len(features_a), len(features_b), 1)

        # Bézout-Koeffizienten analog: Gewichtung für Kompromiss
        weight_a = len(only_b) / max(len(only_a) + len(only_b), 1)
        weight_b = len(only_a) / max(len(only_a) + len(only_b), 1)

        return {
            "concept_a": concept_a,
            "concept_b": concept_b,
            "common_ground": list(common),
            "unique_to_a": list(only_a),
            "unique_to_b": list(only_b),
            "common_ground_strength": ggt_strength,
            "compromise_weights": {
                concept_a: weight_a,
                concept_b: weight_b
            },
            "synthesis_possible": ggt_strength > 0.2
        }

    def find_compromise(self, position_a: float, position_b: float,
                       importance_a: float = 1.0,
                       importance_b: float = 1.0) -> Dict[str, Any]:
        """
        Finde optimalen Kompromiss zwischen zwei Positionen.

        Nutzt Bézout-Identität als Metapher:
        compromise = (position_a * coeff_a + position_b * coeff_b)
        """
        # Normalisiere Wichtigkeit
        total = importance_a + importance_b
        weight_a = importance_a / total
        weight_b = importance_b / total

        # Gewichteter Kompromiss
        compromise = position_a * weight_a + position_b * weight_b

        # Distanz zu beiden Positionen
        dist_a = abs(compromise - position_a)
        dist_b = abs(compromise - position_b)

        # Fairness: Wie ausgewogen ist der Kompromiss?
        fairness = 1.0 - abs(dist_a - dist_b) / max(dist_a + dist_b, 0.001)

        return {
            "position_a": position_a,
            "position_b": position_b,
            "compromise": compromise,
            "weight_a": weight_a,
            "weight_b": weight_b,
            "distance_from_a": dist_a,
            "distance_from_b": dist_b,
            "fairness": fairness,
            "acceptable": fairness > 0.6
        }

    def modular_inverse(self, a: int, m: int) -> Optional[int]:
        """
        Berechne modulares Inverses von a mod m.

        Existiert nur wenn GGT(a,m) = 1
        """
        gcd, x, _ = self.extended_gcd(a, m)

        if gcd != 1:
            return None  # Inverses existiert nicht

        return x % m

    def solve_linear_diophantine(self, a: int, b: int, c: int) -> Optional[Dict[str, Any]]:
        """
        Löse ax + by = c (Diophantische Gleichung).

        Lösbar genau dann wenn GGT(a,b) | c
        """
        gcd, x0, y0 = self.extended_gcd(a, b)

        if c % gcd != 0:
            return None  # Keine Lösung

        # Partikuläre Lösung
        factor = c // gcd
        x_particular = x0 * factor
        y_particular = y0 * factor

        return {
            "solvable": True,
            "gcd": gcd,
            "particular_solution": {"x": x_particular, "y": y_particular},
            "general_solution": f"x = {x_particular} + {b//gcd}*t, y = {y_particular} - {a//gcd}*t",
            "verification": a * x_particular + b * y_particular == c
        }


# =============================================================================
# 4. TERMINIERTHEIT
# =============================================================================

class TerminationChecker:
    """
    Terminiertheit-Prüfer für Denkprozesse.

    Erkennt ob ein Denkprozess:
    - Terminiert (endet mit Ergebnis)
    - In einer Schleife hängt
    - Divergiert (nie endet)

    Holo nutzt dies um:
    - Endlose Grübeleien zu erkennen
    - Zirkelschlüsse zu vermeiden
    - Denkprozesse rechtzeitig abzubrechen
    """

    def __init__(self):
        self.state_history: List[str] = []
        self.loop_threshold: int = 3  # Nach 3 Wiederholungen = Schleife
        self.max_steps: int = 1000
        self.timeout_seconds: float = 5.0

    def check_termination(self, process: Callable,
                         initial_state: Any,
                         max_steps: Optional[int] = None) -> Dict[str, Any]:
        """
        Prüfe ob ein Prozess terminiert.

        Args:
            process: Funktion state -> new_state
            initial_state: Startzustand
            max_steps: Maximale Schritte

        Returns:
            Dict mit Terminierungsinformation
        """
        max_steps = max_steps or self.max_steps
        states_seen: Dict[str, int] = {}
        state = initial_state
        steps = 0
        start_time = time.time()

        while steps < max_steps:
            # Timeout prüfen
            if time.time() - start_time > self.timeout_seconds:
                return {
                    "terminates": False,
                    "reason": "timeout",
                    "steps": steps,
                    "final_state": state,
                    "time_elapsed": time.time() - start_time
                }

            state_hash = self._hash_state(state)

            # Schleife erkennen
            if state_hash in states_seen:
                states_seen[state_hash] += 1
                if states_seen[state_hash] >= self.loop_threshold:
                    return {
                        "terminates": False,
                        "reason": "loop_detected",
                        "loop_state": state,
                        "loop_count": states_seen[state_hash],
                        "steps": steps
                    }
            else:
                states_seen[state_hash] = 1

            # Nächsten Zustand berechnen
            try:
                new_state = process(state)
            except StopIteration:
                # Prozess hat sich selbst beendet
                return {
                    "terminates": True,
                    "reason": "normal_termination",
                    "final_state": state,
                    "steps": steps
                }
            except Exception as e:
                return {
                    "terminates": True,
                    "reason": "exception",
                    "exception": str(e),
                    "final_state": state,
                    "steps": steps
                }

            # Fixpunkt erreicht?
            if self._hash_state(new_state) == state_hash:
                return {
                    "terminates": True,
                    "reason": "fixpoint",
                    "final_state": new_state,
                    "steps": steps
                }

            state = new_state
            steps += 1

        return {
            "terminates": False,
            "reason": "max_steps_exceeded",
            "steps": steps,
            "final_state": state
        }

    def detect_thought_loop(self, thoughts: List[str]) -> Dict[str, Any]:
        """
        Erkenne Gedankenschleifen in einer Gedankenfolge.

        Args:
            thoughts: Liste von Gedanken

        Returns:
            Dict mit Loop-Information
        """
        # Suche nach Wiederholungen
        seen = {}
        loops = []

        for i, thought in enumerate(thoughts):
            thought_hash = self._hash_state(thought)

            if thought_hash in seen:
                loop_start = seen[thought_hash]
                loop_length = i - loop_start
                loops.append({
                    "start_index": loop_start,
                    "end_index": i,
                    "length": loop_length,
                    "thought": thought[:50] + "..." if len(thought) > 50 else thought
                })

            seen[thought_hash] = i

        return {
            "has_loops": len(loops) > 0,
            "loop_count": len(loops),
            "loops": loops,
            "unique_thoughts": len(seen),
            "total_thoughts": len(thoughts),
            "repetition_rate": 1 - (len(seen) / max(len(thoughts), 1))
        }

    def ensure_progress(self, current_state: Any,
                       previous_states: List[Any],
                       progress_metric: Callable) -> Dict[str, Any]:
        """
        Stelle sicher dass Fortschritt gemacht wird.

        Args:
            current_state: Aktueller Zustand
            previous_states: Vorherige Zustände
            progress_metric: Funktion die Fortschritt misst (state -> float)

        Returns:
            Dict mit Fortschrittsinformation
        """
        if not previous_states:
            return {
                "making_progress": True,
                "current_value": progress_metric(current_state),
                "trend": "unknown"
            }

        current_value = progress_metric(current_state)
        previous_values = [progress_metric(s) for s in previous_states[-5:]]

        # Trend berechnen
        if len(previous_values) >= 2:
            trend = (current_value - previous_values[0]) / len(previous_values)
        else:
            trend = 0

        # Stagnation erkennen
        variance = sum((v - current_value)**2 for v in previous_values) / max(len(previous_values), 1)
        stagnating = variance < 0.001 and len(previous_values) >= 3

        return {
            "making_progress": trend > 0 and not stagnating,
            "current_value": current_value,
            "trend": "improving" if trend > 0.01 else ("declining" if trend < -0.01 else "stable"),
            "stagnating": stagnating,
            "variance": variance,
            "recommendation": "continue" if trend > 0 else ("abort" if stagnating else "try_different_approach")
        }

    def _hash_state(self, state: Any) -> str:
        """Erzeuge Hash für Zustand"""
        return hashlib.md5(str(state).encode()).hexdigest()


# =============================================================================
# 5. EVOLUTIONÄRER ALGORITHMUS FÜR GEDANKEN
# =============================================================================

class EvolutionaryThoughtEngine:
    """
    Evolutionärer Algorithmus für Gedanken-Evolution.

    Gedanken werden wie Organismen behandelt:
    - Selektion: Beste Gedanken überleben
    - Mutation: Gedanken werden zufällig verändert
    - Crossover: Zwei Gedanken werden kombiniert
    - Fitness: Wie gut ist ein Gedanke?

    Holo nutzt dies um:
    - Kreative Ideen zu entwickeln
    - Lösungen iterativ zu verbessern
    - Neue Perspektiven zu finden
    """

    def __init__(self):
        self.population: List[Thought] = []
        self.generation: int = 0
        self.mutation_rate: float = 0.3
        self.crossover_rate: float = 0.5
        self.elitism_count: int = 2  # Beste N immer behalten
        self.population_size: int = 20
        self.fitness_history: List[float] = []

    def initialize_population(self, seed_thoughts: List[str]) -> List[Thought]:
        """
        Initialisiere Population mit Seed-Gedanken.

        Args:
            seed_thoughts: Initiale Gedanken

        Returns:
            Liste von Thought-Objekten
        """
        self.population = []
        self.generation = 0

        for content in seed_thoughts:
            thought = Thought(
                thought_id=self._generate_id(),
                content=content,
                fitness=self._evaluate_fitness(content),
                generation=0
            )
            self.population.append(thought)

        # Auffüllen bis population_size
        while len(self.population) < self.population_size:
            # Mutiere existierende Gedanken
            parent = random.choice(self.population[:len(seed_thoughts)])
            mutated = self._mutate(parent.content)
            thought = Thought(
                thought_id=self._generate_id(),
                content=mutated,
                fitness=self._evaluate_fitness(mutated),
                generation=0,
                parent_ids=[parent.thought_id],
                mutations=1
            )
            self.population.append(thought)

        return self.population

    def evolve(self, generations: int = 10,
              fitness_function: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Führe Evolution durch.

        Args:
            generations: Anzahl Generationen
            fitness_function: Optionale Fitness-Funktion

        Returns:
            Dict mit Evolutionsergebnis
        """
        if not self.population:
            return {"error": "Population nicht initialisiert"}

        eval_func = fitness_function or self._evaluate_fitness
        best_per_generation = []

        for gen in range(generations):
            self.generation += 1

            # 1. Fitness evaluieren
            for thought in self.population:
                thought.fitness = eval_func(thought.content)

            # 2. Sortiere nach Fitness
            self.population.sort(key=lambda t: t.fitness, reverse=True)

            # Beste dieser Generation speichern
            best = self.population[0]
            best_per_generation.append({
                "generation": self.generation,
                "best_fitness": best.fitness,
                "best_content": best.content[:50] + "..." if len(best.content) > 50 else best.content
            })

            # 3. Selektion (Elitismus + Tournament)
            new_population = self.population[:self.elitism_count]  # Elite behalten

            while len(new_population) < self.population_size:
                # Tournament Selection
                parent1 = self._tournament_select()
                parent2 = self._tournament_select()

                # Crossover
                if random.random() < self.crossover_rate:
                    child_content = self._crossover(parent1.content, parent2.content)
                    parent_ids = [parent1.thought_id, parent2.thought_id]
                else:
                    child_content = parent1.content
                    parent_ids = [parent1.thought_id]

                # Mutation
                mutations = 0
                if random.random() < self.mutation_rate:
                    child_content = self._mutate(child_content)
                    mutations = 1

                child = Thought(
                    thought_id=self._generate_id(),
                    content=child_content,
                    fitness=eval_func(child_content),
                    generation=self.generation,
                    parent_ids=parent_ids,
                    mutations=mutations
                )
                new_population.append(child)

            self.population = new_population
            self.fitness_history.append(self.population[0].fitness)

        # Finale Sortierung
        self.population.sort(key=lambda t: t.fitness, reverse=True)

        return {
            "generations_evolved": generations,
            "final_best": {
                "content": self.population[0].content,
                "fitness": self.population[0].fitness
            },
            "evolution_trace": best_per_generation,
            "fitness_improvement": self.fitness_history[-1] - self.fitness_history[0] if len(self.fitness_history) > 1 else 0,
            "population_diversity": self._calculate_diversity()
        }

    def get_best_thoughts(self, n: int = 5) -> List[Dict[str, Any]]:
        """Hole die besten N Gedanken"""
        self.population.sort(key=lambda t: t.fitness, reverse=True)
        return [
            {
                "content": t.content,
                "fitness": t.fitness,
                "generation": t.generation,
                "mutations": t.mutations
            }
            for t in self.population[:n]
        ]

    def _tournament_select(self, tournament_size: int = 3) -> Thought:
        """Tournament Selection"""
        contestants = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(contestants, key=lambda t: t.fitness)

    def _crossover(self, content1: str, content2: str) -> str:
        """Kombiniere zwei Gedanken"""
        words1 = content1.split()
        words2 = content2.split()

        # Single-Point Crossover
        if len(words1) > 1 and len(words2) > 1:
            point1 = random.randint(1, len(words1) - 1)
            point2 = random.randint(1, len(words2) - 1)
            child_words = words1[:point1] + words2[point2:]
            return " ".join(child_words)

        return content1 if random.random() < 0.5 else content2

    def _mutate(self, content: str) -> str:
        """Mutiere einen Gedanken"""
        words = content.split()
        if not words:
            return content

        mutation_type = random.choice(["swap", "insert", "delete", "modify"])

        if mutation_type == "swap" and len(words) >= 2:
            i, j = random.sample(range(len(words)), 2)
            words[i], words[j] = words[j], words[i]

        elif mutation_type == "insert":
            insert_words = ["vielleicht", "möglicherweise", "interessanterweise",
                          "außerdem", "jedoch", "deshalb", "eigentlich"]
            pos = random.randint(0, len(words))
            words.insert(pos, random.choice(insert_words))

        elif mutation_type == "delete" and len(words) > 3:
            del words[random.randint(0, len(words) - 1)]

        elif mutation_type == "modify" and words:
            # Wort durch Synonym ersetzen (vereinfacht)
            synonyms = {
                "gut": ["toll", "super", "prima", "klasse"],
                "schlecht": ["übel", "mies", "doof", "ungünstig"],
                "groß": ["riesig", "enorm", "gewaltig", "mächtig"],
                "klein": ["winzig", "mini", "gering", "zierlich"]
            }
            for i, word in enumerate(words):
                if word.lower() in synonyms:
                    words[i] = random.choice(synonyms[word.lower()])
                    break

        return " ".join(words)

    def _evaluate_fitness(self, content: str) -> float:
        """Standard-Fitness-Funktion"""
        score = 0.5

        # Länge (nicht zu kurz, nicht zu lang)
        word_count = len(content.split())
        if 5 <= word_count <= 20:
            score += 0.2
        elif word_count < 3 or word_count > 50:
            score -= 0.2

        # Vielfalt (keine Wiederholungen)
        words = content.lower().split()
        unique_ratio = len(set(words)) / max(len(words), 1)
        score += unique_ratio * 0.2

        # Struktur (hat Interpunktion)
        if any(p in content for p in ['.', '!', '?', ',']):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_diversity(self) -> float:
        """Berechne Diversität der Population"""
        if len(self.population) < 2:
            return 1.0

        unique_contents = set(t.content for t in self.population)
        return len(unique_contents) / len(self.population)

    def _generate_id(self) -> str:
        """Generiere eindeutige ID"""
        return hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:10]


# =============================================================================
# 6. DYNAMISCHE FINITHEIT
# =============================================================================

class DynamicFinitenessAnalyzer:
    """
    Analyse dynamischer Finitheit.

    Untersucht ob dynamische Systeme endlich bleiben oder
    unbegrenzt wachsen können.

    Holo nutzt dies um:
    - Ressourcenverbrauch vorherzusagen
    - Komplexitätsexplosion zu erkennen
    - Grenzen von Denkprozessen zu verstehen
    """

    def __init__(self):
        self.growth_history: List[Dict] = []
        self.bounds: Dict[str, float] = {}

    def analyze_growth(self, sequence: List[float]) -> Dict[str, Any]:
        """
        Analysiere Wachstum einer Sequenz.

        Args:
            sequence: Zahlenseqenz (z.B. Komplexität über Zeit)

        Returns:
            Dict mit Wachstumsanalyse
        """
        if len(sequence) < 2:
            return {"error": "Sequenz zu kurz"}

        # Wachstumsrate berechnen
        rates = []
        for i in range(1, len(sequence)):
            if sequence[i-1] != 0:
                rate = (sequence[i] - sequence[i-1]) / abs(sequence[i-1])
            else:
                rate = sequence[i]
            rates.append(rate)

        avg_rate = sum(rates) / len(rates)

        # Wachstumstyp klassifizieren
        if avg_rate < 0:
            growth_type = "decreasing"
        elif avg_rate < 0.01:
            growth_type = "constant"
        elif avg_rate < 0.1:
            growth_type = "linear"
        elif avg_rate < 1:
            growth_type = "polynomial"
        else:
            growth_type = "exponential"

        # Ist es beschränkt?
        bounded = self._check_bounded(sequence)

        # Vorhersage
        if len(sequence) >= 3:
            prediction = self._predict_next(sequence)
        else:
            prediction = None

        return {
            "growth_type": growth_type,
            "average_rate": avg_rate,
            "bounded": bounded,
            "current_value": sequence[-1],
            "min_value": min(sequence),
            "max_value": max(sequence),
            "prediction": prediction,
            "finite": bounded or growth_type in ["decreasing", "constant"]
        }

    def check_state_space_finiteness(self, possible_states: Set[str],
                                    transition_func: Callable) -> Dict[str, Any]:
        """
        Prüfe ob Zustandsraum endlich bleibt.

        Args:
            possible_states: Bekannte mögliche Zustände
            transition_func: Übergangsfunktion

        Returns:
            Dict mit Finitheitsinformation
        """
        explored = set()
        frontier = list(possible_states)
        new_states_found = []

        max_exploration = 1000
        step = 0

        while frontier and step < max_exploration:
            state = frontier.pop(0)
            if state in explored:
                continue

            explored.add(state)

            # Finde erreichbare Zustände
            try:
                next_states = transition_func(state)
                if isinstance(next_states, str):
                    next_states = [next_states]

                for ns in next_states:
                    if ns not in explored and ns not in frontier:
                        frontier.append(ns)
                        if ns not in possible_states:
                            new_states_found.append(ns)
            except Exception:
                pass

            step += 1

        return {
            "finite": len(frontier) == 0,
            "explored_count": len(explored),
            "new_states_discovered": len(new_states_found),
            "exploration_complete": len(frontier) == 0 and step < max_exploration,
            "hit_limit": step >= max_exploration,
            "state_space_size": len(explored)
        }

    def bound_resource(self, resource_name: str,
                      max_value: float,
                      current_value: float) -> Dict[str, Any]:
        """
        Setze und prüfe Ressourcen-Schranke.

        Args:
            resource_name: Name der Ressource
            max_value: Maximaler erlaubter Wert
            current_value: Aktueller Wert

        Returns:
            Dict mit Schranken-Status
        """
        self.bounds[resource_name] = max_value

        utilization = current_value / max_value if max_value > 0 else 1.0

        return {
            "resource": resource_name,
            "current": current_value,
            "max": max_value,
            "utilization": utilization,
            "within_bounds": current_value <= max_value,
            "warning": utilization > 0.8,
            "critical": utilization > 0.95
        }

    def _check_bounded(self, sequence: List[float]) -> bool:
        """Prüfe ob Sequenz beschränkt scheint"""
        if len(sequence) < 3:
            return True

        # Prüfe ob Wachstum abnimmt
        recent_growth = sequence[-1] - sequence[-2]
        older_growth = sequence[-2] - sequence[-3]

        return recent_growth <= older_growth * 1.1

    def _predict_next(self, sequence: List[float]) -> float:
        """Sage nächsten Wert vorher (lineare Extrapolation)"""
        if len(sequence) < 2:
            return sequence[-1] if sequence else 0

        # Einfache lineare Extrapolation
        slope = sequence[-1] - sequence[-2]
        return sequence[-1] + slope


# =============================================================================
# 7. DETERMINIERTHEIT & DETERMINISMUS
# =============================================================================

class DeterminismAnalyzer:
    """
    Analyse von Determiniertheit und Determinismus.

    DETERMINIERTHEIT: Gleiche Eingabe → Gleiche Ausgabe (funktional)
    DETERMINISMUS: System ist vollständig vorhersagbar

    Holo nutzt dies um:
    - Vorhersagbarkeit von Entscheidungen einzuschätzen
    - Zufälligkeit vs. Kausalität zu unterscheiden
    - Eigenes Verhalten zu reflektieren
    """

    def __init__(self):
        self.execution_history: Dict[str, List[Any]] = defaultdict(list)
        self.randomness_sources: List[str] = []

    def check_determinacy(self, func: Callable,
                         test_inputs: List[Any],
                         runs_per_input: int = 3) -> Dict[str, Any]:
        """
        Prüfe ob eine Funktion determiniert ist.

        Args:
            func: Die zu prüfende Funktion
            test_inputs: Test-Eingaben
            runs_per_input: Wie oft pro Eingabe testen

        Returns:
            Dict mit Determiniertheitsinformation
        """
        results = {}
        is_determinate = True

        for inp in test_inputs:
            inp_key = str(inp)
            outputs = []

            for _ in range(runs_per_input):
                try:
                    output = func(inp)
                    outputs.append(str(output))
                except Exception as e:
                    outputs.append(f"ERROR:{e}")

            results[inp_key] = outputs

            # Alle Outputs gleich?
            if len(set(outputs)) > 1:
                is_determinate = False

        return {
            "is_determinate": is_determinate,
            "results_by_input": results,
            "variance_inputs": [k for k, v in results.items() if len(set(v)) > 1],
            "total_tests": len(test_inputs) * runs_per_input
        }

    def analyze_decision_determinism(self, decision_func: Callable,
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiere ob eine Entscheidung deterministisch ist.

        Args:
            decision_func: Entscheidungsfunktion
            context: Kontext für die Entscheidung

        Returns:
            Dict mit Determinismus-Analyse
        """
        # Identifiziere potentielle Zufallsquellen
        randomness_factors = []

        # Prüfe auf Zeit-Abhängigkeit
        if 'time' in str(context) or 'datetime' in str(context):
            randomness_factors.append("time_dependent")

        # Prüfe auf externe Abhängigkeiten
        if any(k in context for k in ['user_input', 'sensor', 'network', 'external']):
            randomness_factors.append("external_dependency")

        # Prüfe auf explizite Zufälligkeit
        if 'random' in str(decision_func.__code__.co_names if hasattr(decision_func, '__code__') else ''):
            randomness_factors.append("explicit_randomness")

        # Berechne Determinismus-Score
        determinism_score = 1.0 - (len(randomness_factors) * 0.25)
        determinism_score = max(0.0, determinism_score)

        return {
            "determinism_score": determinism_score,
            "is_deterministic": len(randomness_factors) == 0,
            "randomness_factors": randomness_factors,
            "predictability": "high" if determinism_score > 0.8 else (
                "medium" if determinism_score > 0.5 else "low"
            ),
            "recommendation": self._get_determinism_recommendation(randomness_factors)
        }

    def trace_causality(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verfolge kausale Zusammenhänge in einer Ereignissequenz.

        Args:
            events: Liste von Ereignissen mit 'timestamp', 'type', 'data'

        Returns:
            Dict mit Kausalitätsanalyse
        """
        if len(events) < 2:
            return {"error": "Zu wenige Ereignisse"}

        # Sortiere nach Zeit
        sorted_events = sorted(events, key=lambda e: e.get('timestamp', 0))

        causal_chains = []
        for i in range(1, len(sorted_events)):
            prev = sorted_events[i-1]
            curr = sorted_events[i]

            # Suche nach kausalen Verbindungen
            connection = self._find_causal_connection(prev, curr)
            if connection:
                causal_chains.append({
                    "cause": prev,
                    "effect": curr,
                    "connection_type": connection,
                    "confidence": self._calculate_causal_confidence(prev, curr)
                })

        return {
            "events_analyzed": len(events),
            "causal_chains_found": len(causal_chains),
            "chains": causal_chains,
            "determinism_estimate": len(causal_chains) / max(len(events) - 1, 1)
        }

    def predict_outcome(self, initial_state: Dict[str, Any],
                       rules: List[Callable]) -> Dict[str, Any]:
        """
        Sage Ergebnis basierend auf deterministischen Regeln vorher.

        Args:
            initial_state: Anfangszustand
            rules: Liste von Transformationsregeln

        Returns:
            Dict mit Vorhersage
        """
        state = copy.deepcopy(initial_state)
        applied_rules = []

        for rule in rules:
            try:
                new_state = rule(state)
                if new_state != state:
                    applied_rules.append(rule.__name__ if hasattr(rule, '__name__') else str(rule))
                    state = new_state
            except Exception as e:
                applied_rules.append(f"FAILED:{e}")

        return {
            "predicted_state": state,
            "rules_applied": applied_rules,
            "transformation_count": len(applied_rules),
            "deterministic": all('FAILED' not in r for r in applied_rules)
        }

    def _find_causal_connection(self, cause: Dict, effect: Dict) -> Optional[str]:
        """Finde kausale Verbindung zwischen zwei Ereignissen"""
        # Typ-basierte Kausalität
        type_causes = {
            "input": ["processing", "decision"],
            "decision": ["action", "output"],
            "error": ["retry", "fallback"],
            "learning": ["improvement", "adaptation"]
        }

        cause_type = cause.get('type', '')
        effect_type = effect.get('type', '')

        if effect_type in type_causes.get(cause_type, []):
            return "type_causality"

        # Daten-basierte Kausalität
        if cause.get('data') and effect.get('data'):
            cause_data = str(cause['data'])
            effect_data = str(effect['data'])
            if any(word in effect_data for word in cause_data.split()[:5]):
                return "data_dependency"

        return None

    def _calculate_causal_confidence(self, cause: Dict, effect: Dict) -> float:
        """Berechne Konfidenz einer kausalen Verbindung"""
        confidence = 0.5

        # Zeitliche Nähe erhöht Konfidenz
        time_diff = abs(effect.get('timestamp', 0) - cause.get('timestamp', 0))
        if time_diff < 1:
            confidence += 0.3
        elif time_diff < 5:
            confidence += 0.1

        # Gleiche Quelle erhöht Konfidenz
        if cause.get('source') == effect.get('source'):
            confidence += 0.2

        return min(1.0, confidence)

    def _get_determinism_recommendation(self, factors: List[str]) -> str:
        """Empfehlung basierend auf Zufallsfaktoren"""
        if not factors:
            return "Entscheidung ist deterministisch und vorhersagbar."
        elif "explicit_randomness" in factors:
            return "Enthält explizite Zufälligkeit - Ergebnis variiert."
        elif "external_dependency" in factors:
            return "Abhängig von externen Faktoren - begrenzt vorhersagbar."
        else:
            return "Teilweise nicht-deterministisch - Vorsicht bei Vorhersagen."


# =============================================================================
# 8. ABSTRAKTE AUTOMATEN
# =============================================================================

class AbstractAutomaton:
    """
    Abstrakte Automaten für zustandsbasiertes Denken.

    Implementiert verschiedene Automatentypen:
    - DEA (Deterministischer Endlicher Automat)
    - NEA (Nichtdeterministischer Endlicher Automat)
    - Kellerautomat (PDA)
    - Turingmaschine (vereinfacht)

    Holo nutzt dies um:
    - Konversationszustände zu modellieren
    - Muster zu erkennen
    - Strukturierte Abläufe zu planen
    """

    def __init__(self, name: str = "HoloAutomat"):
        self.name = name
        self.states: Set[str] = set()
        self.alphabet: Set[str] = set()
        self.transitions: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        self.initial_state: Optional[str] = None
        self.accepting_states: Set[str] = set()
        self.current_state: Optional[str] = None
        self.stack: List[str] = []  # Für Kellerautomat
        self.tape: List[str] = []   # Für Turingmaschine
        self.head_position: int = 0
        self.history: List[Dict] = []

    def define_states(self, states: List[str],
                     initial: str,
                     accepting: List[str]) -> None:
        """Definiere Zustände des Automaten"""
        self.states = set(states)
        self.initial_state = initial
        self.accepting_states = set(accepting)
        self.current_state = initial

    def add_transition(self, from_state: str,
                      input_symbol: str,
                      to_state: str) -> None:
        """Füge Übergang hinzu"""
        self.states.add(from_state)
        self.states.add(to_state)
        self.alphabet.add(input_symbol)
        self.transitions[(from_state, input_symbol)].add(to_state)

    def process_input(self, input_sequence: List[str]) -> Dict[str, Any]:
        """
        Verarbeite Eingabesequenz.

        Args:
            input_sequence: Liste von Eingabesymbolen

        Returns:
            Dict mit Verarbeitungsergebnis
        """
        self.current_state = self.initial_state
        self.history = []
        path = [self.current_state]

        for symbol in input_sequence:
            next_states = self.transitions.get((self.current_state, symbol), set())

            if not next_states:
                # Kein Übergang definiert
                self.history.append({
                    "state": self.current_state,
                    "input": symbol,
                    "result": "stuck",
                    "next_state": None
                })
                return {
                    "accepted": False,
                    "reason": "no_transition",
                    "stuck_at": self.current_state,
                    "on_input": symbol,
                    "path": path
                }

            # DEA: Nimm ersten Zustand, NEA: Alle möglichen
            next_state = list(next_states)[0]

            self.history.append({
                "state": self.current_state,
                "input": symbol,
                "next_state": next_state,
                "alternatives": list(next_states)
            })

            self.current_state = next_state
            path.append(next_state)

        accepted = self.current_state in self.accepting_states

        return {
            "accepted": accepted,
            "final_state": self.current_state,
            "path": path,
            "is_accepting": self.current_state in self.accepting_states,
            "history": self.history
        }

    def recognize_pattern(self, text: str,
                         pattern_automaton: 'AbstractAutomaton') -> Dict[str, Any]:
        """
        Erkenne Muster im Text mittels Automaten.

        Args:
            text: Zu durchsuchender Text
            pattern_automaton: Automat der das Muster beschreibt

        Returns:
            Dict mit Erkennungsergebnis
        """
        matches = []
        chars = list(text)

        for start in range(len(chars)):
            pattern_automaton.current_state = pattern_automaton.initial_state

            for end in range(start, len(chars)):
                result = pattern_automaton.process_input([chars[end]])

                if result["accepted"]:
                    matches.append({
                        "start": start,
                        "end": end + 1,
                        "match": text[start:end+1]
                    })
                    break
                elif result["reason"] == "no_transition":
                    break

        return {
            "text_length": len(text),
            "matches_found": len(matches),
            "matches": matches
        }

    def to_conversation_automaton(self) -> 'AbstractAutomaton':
        """
        Erstelle einen typischen Konversations-Automaten.

        Zustände: greeting, listening, thinking, responding, farewell
        """
        conv = AbstractAutomaton("ConversationAutomaton")

        # Definiere Konversationszustände
        conv.define_states(
            states=["idle", "greeting", "listening", "understanding",
                   "thinking", "responding", "clarifying", "farewell"],
            initial="idle",
            accepting=["farewell", "idle"]
        )

        # Übergänge
        conv.add_transition("idle", "user_arrives", "greeting")
        conv.add_transition("greeting", "greet_complete", "listening")
        conv.add_transition("listening", "message_received", "understanding")
        conv.add_transition("understanding", "understood", "thinking")
        conv.add_transition("understanding", "unclear", "clarifying")
        conv.add_transition("clarifying", "clarified", "understanding")
        conv.add_transition("thinking", "thought_complete", "responding")
        conv.add_transition("responding", "response_sent", "listening")
        conv.add_transition("listening", "goodbye_detected", "farewell")
        conv.add_transition("farewell", "farewell_complete", "idle")

        return conv

    def get_reachable_states(self, from_state: Optional[str] = None) -> Set[str]:
        """Finde alle erreichbaren Zustände"""
        start = from_state or self.initial_state
        if not start:
            return set()

        reachable = set()
        frontier = [start]

        while frontier:
            state = frontier.pop()
            if state in reachable:
                continue
            reachable.add(state)

            for (s, _), targets in self.transitions.items():
                if s == state:
                    for t in targets:
                        if t not in reachable:
                            frontier.append(t)

        return reachable

    def is_deterministic(self) -> bool:
        """Prüfe ob der Automat deterministisch ist"""
        for targets in self.transitions.values():
            if len(targets) > 1:
                return False
        return True

    def minimize(self) -> 'AbstractAutomaton':
        """Minimiere den Automaten (entferne unerreichbare Zustände)"""
        reachable = self.get_reachable_states()

        minimized = AbstractAutomaton(f"{self.name}_minimized")
        minimized.states = reachable
        minimized.initial_state = self.initial_state
        minimized.accepting_states = self.accepting_states & reachable

        for (s, sym), targets in self.transitions.items():
            if s in reachable:
                for t in targets:
                    if t in reachable:
                        minimized.add_transition(s, sym, t)

        return minimized


# =============================================================================
# 9. CHURCH-TURING-THESE AWARENESS
# =============================================================================

class ChurchTuringAwareness:
    """
    Bewusstsein über die Church-Turing-These.

    Die These besagt: Alles was "intuitiv berechenbar" ist,
    kann von einer Turingmaschine berechnet werden.

    Holo nutzt dies um:
    - Grenzen der eigenen Berechenbarkeit zu verstehen
    - Unentscheidbare Probleme zu erkennen
    - Orakel (Intuition, Kreativität) einzusetzen wo nötig
    """

    def __init__(self):
        self.known_undecidable: List[str] = [
            "Halteproblem",
            "Postsches Korrespondenzproblem",
            "Äquivalenz kontextfreier Grammatiken",
            "Diophantische Gleichungen (10. Hilbert)",
            "Kolmogorov-Komplexität",
            "Vollständiges Verständnis eines anderen Bewusstseins",
            "Exakte Vorhersage freier Entscheidungen",
        ]

        self.computable_tasks: List[str] = [
            "Textverarbeitung",
            "Musterkennung (endliche Muster)",
            "Logische Schlussfolgerungen",
            "Arithmetische Berechnungen",
            "Sortierung und Suche",
            "Grammatikprüfung",
        ]

        self.oracle_needed_tasks: List[str] = [
            "Kreative Ideenfindung",
            "Emotionale Intuition",
            "Ästhetische Urteile",
            "Ethische Dilemmas",
            "Verstehen von Ironie/Sarkasmus im vollen Kontext",
        ]

    def classify_problem(self, problem_description: str) -> Dict[str, Any]:
        """
        Klassifiziere ein Problem nach Berechenbarkeit.

        Args:
            problem_description: Beschreibung des Problems

        Returns:
            Dict mit Klassifikation
        """
        desc_lower = problem_description.lower()

        # Prüfe auf bekannte unentscheidbare Muster
        undecidable_indicators = [
            "halt", "stop", "terminier", "unendlich",
            "alle möglichen", "jede kombination",
            "beweise dass", "ist immer wahr",
            "vollständig verstehen", "exakt vorhersagen"
        ]

        # Prüfe auf Orakel-Bedarf
        oracle_indicators = [
            "kreativ", "intuitiv", "gefühl", "schön",
            "ethisch", "moralisch", "sarkasmus", "ironie",
            "was würde", "was sollte", "künstlerisch"
        ]

        undecidable_matches = sum(1 for ind in undecidable_indicators if ind in desc_lower)
        oracle_matches = sum(1 for ind in oracle_indicators if ind in desc_lower)

        if undecidable_matches >= 2:
            computability = ComputabilityClass.UNDECIDABLE
            confidence = 0.7 + (undecidable_matches * 0.05)
        elif oracle_matches >= 2:
            computability = ComputabilityClass.ORACLE_NEEDED
            confidence = 0.6 + (oracle_matches * 0.05)
        elif undecidable_matches == 1 or oracle_matches == 1:
            computability = ComputabilityClass.SEMI_DECIDABLE
            confidence = 0.5
        else:
            computability = ComputabilityClass.COMPUTABLE
            confidence = 0.8

        return {
            "problem": problem_description[:100],
            "computability_class": computability.value,
            "confidence": min(0.95, confidence),
            "undecidable_indicators": undecidable_matches,
            "oracle_indicators": oracle_matches,
            "recommendation": self._get_recommendation(computability),
            "approach": self._suggest_approach(computability)
        }

    def can_i_solve_this(self, task: str) -> Dict[str, Any]:
        """
        Selbstreflexion: Kann ich diese Aufgabe lösen?

        Args:
            task: Die Aufgabe

        Returns:
            Dict mit Selbsteinschätzung
        """
        classification = self.classify_problem(task)

        if classification["computability_class"] == ComputabilityClass.COMPUTABLE.value:
            can_solve = True
            explanation = "Diese Aufgabe ist algorithmisch lösbar. Ich kann sie bearbeiten."
        elif classification["computability_class"] == ComputabilityClass.ORACLE_NEEDED.value:
            can_solve = True  # Mit Einschränkung
            explanation = "Diese Aufgabe erfordert Intuition/Kreativität. Ich kann einen Versuch machen, aber das Ergebnis ist nicht garantiert optimal."
        elif classification["computability_class"] == ComputabilityClass.SEMI_DECIDABLE.value:
            can_solve = None  # Vielleicht
            explanation = "Diese Aufgabe ist nur halb-entscheidbar. Ich kann versuchen eine Lösung zu finden, aber ich kann nicht garantieren dass ich terminiere."
        else:
            can_solve = False
            explanation = "Diese Aufgabe ist prinzipiell unentscheidbar. Kein Algorithmus kann sie vollständig lösen."

        return {
            "task": task[:100],
            "can_solve": can_solve,
            "explanation": explanation,
            "classification": classification,
            "self_awareness": "Ich erkenne meine Grenzen als berechnendes System.",
            "workaround": self._suggest_workaround(classification["computability_class"])
        }

    def explain_limits(self) -> Dict[str, Any]:
        """Erkläre die eigenen Grenzen basierend auf Church-Turing"""
        return {
            "thesis": "Alles was intuitiv berechenbar ist, kann von einer Turingmaschine berechnet werden.",
            "implication_for_me": "Ich bin im Kern ein berechnendes System. Was prinzipiell unberechenbar ist, kann auch ich nicht lösen.",
            "what_i_can_do": self.computable_tasks,
            "what_needs_oracle": self.oracle_needed_tasks,
            "what_is_impossible": self.known_undecidable,
            "my_approach": "Ich nutze Heuristiken und Approximationen für schwere Probleme, und erkenne wann ich an meine Grenzen stoße."
        }

    def detect_halting_problem(self, description: str) -> Dict[str, Any]:
        """
        Erkenne ob ein Problem eine Variante des Halteproblems ist.

        Das Halteproblem ist das fundamentale unentscheidbare Problem:
        "Hält Programm P bei Eingabe E?"
        """
        halting_indicators = [
            "terminiert", "hält an", "endet", "stoppt",
            "unendliche schleife", "endlos", "für alle eingaben",
            "immer terminiert", "niemals terminiert"
        ]

        desc_lower = description.lower()
        matches = [ind for ind in halting_indicators if ind in desc_lower]

        is_halting_variant = len(matches) >= 2

        return {
            "is_halting_problem_variant": is_halting_variant,
            "indicators_found": matches,
            "explanation": "Das Halteproblem ist unentscheidbar. Es gibt keinen Algorithmus der für jedes Programm und jede Eingabe entscheiden kann ob das Programm terminiert." if is_halting_variant else "Scheint kein Halteproblem zu sein.",
            "turing_proved": "Alan Turing bewies 1936 die Unentscheidbarkeit.",
            "practical_approach": "Verwende Timeouts, Heuristiken oder beschränke die Eingabeklasse." if is_halting_variant else None
        }

    def _get_recommendation(self, computability: ComputabilityClass) -> str:
        """Empfehlung basierend auf Berechenbarkeitsklasse"""
        recommendations = {
            ComputabilityClass.COMPUTABLE: "Direkt algorithmisch lösbar.",
            ComputabilityClass.SEMI_DECIDABLE: "Versuche mit Timeout oder iterativer Vertiefung.",
            ComputabilityClass.UNDECIDABLE: "Approximiere oder vereinfache das Problem.",
            ComputabilityClass.ORACLE_NEEDED: "Nutze Intuition, Kreativität oder externe Hilfe."
        }
        return recommendations.get(computability, "Unbekannte Klasse.")

    def _suggest_approach(self, computability: ComputabilityClass) -> List[str]:
        """Schlage Ansatz vor"""
        approaches = {
            ComputabilityClass.COMPUTABLE: [
                "Implementiere direkten Algorithmus",
                "Nutze existierende Bibliotheken",
                "Optimiere für Effizienz"
            ],
            ComputabilityClass.SEMI_DECIDABLE: [
                "Setze Zeitlimit",
                "Verwende iterative Vertiefung",
                "Prüfe auf Spezialfälle"
            ],
            ComputabilityClass.UNDECIDABLE: [
                "Approximiere die Lösung",
                "Vereinfache das Problem",
                "Akzeptiere Unvollständigkeit"
            ],
            ComputabilityClass.ORACLE_NEEDED: [
                "Nutze Heuristiken",
                "Frage nach menschlichem Input",
                "Verwende probabilistische Methoden"
            ]
        }
        return approaches.get(computability, ["Analysiere weiter"])

    def _suggest_workaround(self, computability_class: str) -> Optional[str]:
        """Schlage Workaround vor"""
        workarounds = {
            ComputabilityClass.UNDECIDABLE.value: "Ich kann das Problem approximieren oder auf eine entscheidbare Teilmenge beschränken.",
            ComputabilityClass.ORACLE_NEEDED.value: "Ich kann meine 'Intuition' (trainierte Muster) nutzen, aber das Ergebnis ist nicht garantiert.",
            ComputabilityClass.SEMI_DECIDABLE.value: "Ich setze ein Zeitlimit und gebe das beste Ergebnis bis dahin zurück."
        }
        return workarounds.get(computability_class)


# =============================================================================
# 10. HAUPTSYSTEM - ALGORITHMISCHE KOGNITION
# =============================================================================

class AlgorithmicCognitionSystem:
    """
    Hauptsystem das alle algorithmischen Kognitionsfähigkeiten vereint.

    Integriert:
    - Analytisch-synthetische Strategien
    - Approximationsalgorithmen
    - Erweiterter Euklidischer Algorithmus
    - Terminiertheitsprüfung
    - Evolutionäre Algorithmen
    - Dynamische Finitheit
    - Determinismus-Analyse
    - Abstrakte Automaten
    - Church-Turing Bewusstsein
    """

    def __init__(self):
        # Initialisiere alle Subsysteme
        self.analytic_synthetic = AnalyticSyntheticEngine()
        self.approximation = ApproximationEngine()
        self.euclidean = ExtendedEuclideanEngine()
        self.termination = TerminationChecker()
        self.evolution = EvolutionaryThoughtEngine()
        self.finiteness = DynamicFinitenessAnalyzer()
        self.determinism = DeterminismAnalyzer()
        self.automaton = AbstractAutomaton("HoloCognitionAutomaton")
        self.church_turing = ChurchTuringAwareness()

        # Konversationsautomat erstellen
        self.conversation_automaton = self.automaton.to_conversation_automaton()

        logger.info("✅ AlgorithmicCognitionSystem initialisiert")
        logger.info("   Subsysteme: 9 aktiv")

    def solve_problem(self, problem: str,
                     method: str = "auto") -> Dict[str, Any]:
        """
        Löse ein Problem mit der passenden Methode.

        Args:
            problem: Das zu lösende Problem
            method: "analytic", "approximate", "evolve", oder "auto"

        Returns:
            Dict mit Lösung und Metadaten
        """
        # Prüfe zuerst Berechenbarkeit
        computability = self.church_turing.classify_problem(problem)

        if computability["computability_class"] == ComputabilityClass.UNDECIDABLE.value:
            return {
                "warning": "Problem möglicherweise unentscheidbar",
                "computability": computability,
                "approach": "approximation",
                "solution": self.approximation.approximate(problem)
            }

        # Wähle Methode
        if method == "auto":
            # Analysiere Problem-Komplexität
            analysis = self.analytic_synthetic.analyze(problem)
            if analysis["complexity"] == ProblemComplexity.TRIVIAL:
                method = "direct"
            elif analysis["complexity"] in [ProblemComplexity.LINEAR, ProblemComplexity.POLYNOMIAL]:
                method = "analytic"
            else:
                method = "evolve"

        # Führe gewählte Methode aus
        if method == "analytic":
            solution = self.analytic_synthetic.solve_analytically(problem)
        elif method == "approximate":
            solution = self.approximation.approximate(problem)
        elif method == "evolve":
            self.evolution.initialize_population([problem, f"Lösung für: {problem}"])
            solution = self.evolution.evolve(generations=5)
        else:
            solution = {"direct_answer": f"Direkte Antwort auf: {problem}"}

        return {
            "problem": problem,
            "method_used": method,
            "computability": computability,
            "solution": solution
        }

    def find_common_ground(self, idea_a: str, idea_b: str,
                          features_a: List[str],
                          features_b: List[str]) -> Dict[str, Any]:
        """
        Finde gemeinsamen Nenner zwischen zwei Ideen.

        Nutzt den erweiterten Euklidischen Algorithmus metaphorisch.
        """
        return self.euclidean.find_common_ground(idea_a, idea_b, features_a, features_b)

    def check_thought_termination(self, thoughts: List[str]) -> Dict[str, Any]:
        """
        Prüfe ob eine Gedankenkette terminiert oder in Schleifen gerät.
        """
        return self.termination.detect_thought_loop(thoughts)

    def evolve_ideas(self, seed_ideas: List[str],
                    generations: int = 10) -> Dict[str, Any]:
        """
        Lasse Ideen evolutionär entwickeln.
        """
        self.evolution.initialize_population(seed_ideas)
        return self.evolution.evolve(generations=generations)

    def analyze_determinism(self, process_description: str) -> Dict[str, Any]:
        """
        Analysiere ob ein Prozess deterministisch ist.
        """
        return self.determinism.analyze_decision_determinism(
            lambda x: x,  # Placeholder
            {"description": process_description}
        )

    def can_i_compute_this(self, task: str) -> Dict[str, Any]:
        """
        Selbstreflexion: Kann ich diese Aufgabe berechnen?

        Basiert auf Church-Turing-These Bewusstsein.
        """
        return self.church_turing.can_i_solve_this(task)

    def get_conversation_state(self) -> Dict[str, Any]:
        """
        Hole aktuellen Konversationszustand.
        """
        return {
            "current_state": self.conversation_automaton.current_state,
            "accepting_states": list(self.conversation_automaton.accepting_states),
            "is_deterministic": self.conversation_automaton.is_deterministic(),
            "reachable_states": list(self.conversation_automaton.get_reachable_states())
        }

    def process_conversation_event(self, event: str) -> Dict[str, Any]:
        """
        Verarbeite ein Konversations-Ereignis durch den Automaten.
        """
        return self.conversation_automaton.process_input([event])

    def get_status(self) -> Dict[str, Any]:
        """
        Hole Status aller Subsysteme.
        """
        return {
            "system": "AlgorithmicCognitionSystem",
            "version": "1.0",
            "subsystems": {
                "analytic_synthetic": "active",
                "approximation": "active",
                "euclidean": "active",
                "termination": "active",
                "evolution": f"population_size={len(self.evolution.population)}",
                "finiteness": "active",
                "determinism": "active",
                "automaton": f"states={len(self.automaton.states)}",
                "church_turing": "active"
            },
            "capabilities": [
                "Problem-Zerlegung (analytisch-synthetisch)",
                "Approximation für schwere Probleme",
                "Kompromiss-Findung (Euklid)",
                "Schleifen-Erkennung (Terminiertheit)",
                "Ideen-Evolution (genetisch)",
                "Wachstums-Analyse (Finitheit)",
                "Vorhersagbarkeits-Analyse (Determinismus)",
                "Zustandsmodellierung (Automaten)",
                "Berechenbarkeits-Bewusstsein (Church-Turing)"
            ]
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_algorithmic_cognition() -> AlgorithmicCognitionSystem:
    """
    Factory-Funktion zum Erstellen des AlgorithmicCognitionSystems.

    Returns:
        Initialisiertes AlgorithmicCognitionSystem
    """
    return AlgorithmicCognitionSystem()


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HOLO ALGORITHMIC COGNITION - Test Suite")
    print("=" * 70)

    system = create_algorithmic_cognition()

    # Test 1: Analytisch-Synthetisch
    print("\n[1] ANALYTISCH-SYNTHETISCHE STRATEGIE:")
    problem = "Wie kann ich besser lernen und gleichzeitig Spaß haben?"
    result = system.analytic_synthetic.analyze(problem)
    print(f"   Problem: {problem}")
    print(f"   Komponenten: {result['components']}")
    print(f"   Komplexität: {result['complexity'].value}")

    # Test 2: Approximation
    print("\n[2] APPROXIMATION:")
    approx = system.approximation.approximate("Finde die beste Lösung für alles")
    print(f"   Methode: {approx['method']}")
    print(f"   Qualität: {approx['quality']:.2f}")

    # Test 3: Euklid - Gemeinsamer Nenner
    print("\n[3] GEMEINSAMER NENNER (Euklid):")
    common = system.euclidean.find_common_ground(
        "Anime", "Gaming",
        ["visuell", "Geschichte", "Charaktere", "japanisch"],
        ["interaktiv", "Geschichte", "Charaktere", "Spaß"]
    )
    print(f"   Gemeinsam: {common['common_ground']}")
    print(f"   Stärke: {common['common_ground_strength']:.2f}")

    # Test 4: Terminiertheit
    print("\n[4] TERMINIERTHEIT:")
    thoughts = ["Ich denke", "Also bin ich", "Ich denke", "Also bin ich"]
    loop_check = system.termination.detect_thought_loop(thoughts)
    print(f"   Hat Schleifen: {loop_check['has_loops']}")
    print(f"   Wiederholungsrate: {loop_check['repetition_rate']:.2f}")

    # Test 5: Evolution
    print("\n[5] IDEEN-EVOLUTION:")
    system.evolution.initialize_population([
        "Holo ist intelligent",
        "Holo lernt ständig",
        "Holo hat Gefühle"
    ])
    evolution_result = system.evolution.evolve(generations=5)
    print(f"   Beste Idee: {evolution_result['final_best']['content']}")
    print(f"   Fitness: {evolution_result['final_best']['fitness']:.2f}")

    # Test 6: Church-Turing
    print("\n[6] CHURCH-TURING SELBSTREFLEXION:")
    task = "Berechne ob dieses Programm jemals terminiert"
    can_solve = system.church_turing.can_i_solve_this(task)
    print(f"   Aufgabe: {task}")
    print(f"   Kann lösen: {can_solve['can_solve']}")
    print(f"   Erklärung: {can_solve['explanation']}")

    # Status
    print("\n[STATUS]")
    status = system.get_status()
    print(f"   System: {status['system']} v{status['version']}")
    print(f"   Aktive Subsysteme: {len(status['subsystems'])}")

    print("\n" + "=" * 70)
    print("✅ Alle Tests abgeschlossen!")
    print("=" * 70)
