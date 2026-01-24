#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  HOLO COMPLEXITY THEORY v1.0
  Komplexitätstheorie und Berechenbarkeit für Holocloude
================================================================================

FEATURES:
1. Komplexitätsklassen
   - P, NP, co-NP
   - NP-complete, NP-hard
   - PSPACE, EXPTIME, EXPSPACE
   - Klassenhierarchie und Beziehungen

2. Asymptotische Analyse (Big-O)
   - O, Ω, Θ Notation
   - Komplexitätsvergleich
   - Amortisierte Analyse
   - Master-Theorem

3. Reduktionen
   - Polynomiale Reduktion (≤p)
   - Turing-Reduktion (≤T)
   - Karp-Reduktionen
   - Bekannte NP-complete Probleme

4. Berechenbarkeit
   - Turing-Maschinen
   - Entscheidbarkeit
   - Halteproblem
   - Rice's Theorem

5. Approximationsalgorithmen
   - Approximationsgüte
   - PTAS, FPTAS
   - Inapproximierbarkeit

Optimiert für Raspberry Pi - Keine schweren ML-Bibliotheken!
Author: Holocloude Team
Version: 1.0
================================================================================
"""

import logging
import math
import re
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger("HoloComplexityTheory")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Komplexitätsklassen
    "ComplexityClassification",
    "ComplexityHierarchy",

    # Big-O
    "BigOEngine",
    "AsymptoticBound",
    "ComplexityFunction",

    # Reduktionen
    "ReductionEngine",
    "Reduction",
    "NPCompleteProblem",

    # Berechenbarkeit
    "ComputabilityEngine",
    "TuringMachine",
    "DecidabilityResult",

    # Approximation
    "ApproximationEngine",
    "ApproximationScheme",

    # Kombiniert
    "ComplexityTheoryEngine",

    # Enums
    "ComplexityType",
    "ReductionType",
    "GrowthRate",

    # Factory
    "create_complexity_engine",
    "create_bigo_engine",
    "create_reduction_engine",
    "get_complexity_theory_engine",
]


# =============================================================================
# ENUMS
# =============================================================================

class ComplexityType(Enum):
    """Komplexitätsklassen"""
    # Zeitkomplexität
    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    SQRT = "O(√n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n²)"
    CUBIC = "O(n³)"
    POLYNOMIAL = "O(n^k)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"

    # Klassen
    P = "P"
    NP = "NP"
    CO_NP = "co-NP"
    NP_COMPLETE = "NP-complete"
    NP_HARD = "NP-hard"
    PSPACE = "PSPACE"
    EXPTIME = "EXPTIME"
    EXPSPACE = "EXPSPACE"
    DECIDABLE = "decidable"
    UNDECIDABLE = "undecidable"


class ReductionType(Enum):
    """Reduktionstypen"""
    POLYNOMIAL = "polynomial"        # Karp-Reduktion (≤p)
    TURING = "turing"               # Cook-Reduktion (≤T)
    LOG_SPACE = "log_space"         # Log-Space Reduktion
    MANY_ONE = "many_one"           # Many-One Reduktion
    TRUTH_TABLE = "truth_table"     # Truth-Table Reduktion


class GrowthRate(Enum):
    """Wachstumsraten für Vergleiche"""
    SLOWER = "slower"
    SAME = "same"
    FASTER = "faster"


class DecidabilityStatus(Enum):
    """Entscheidbarkeitsstatus"""
    DECIDABLE = "decidable"
    SEMI_DECIDABLE = "semi_decidable"
    UNDECIDABLE = "undecidable"
    UNKNOWN = "unknown"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class AsymptoticBound:
    """Asymptotische Schranke"""
    expression: str              # z.B. "n²", "n log n"
    coefficient: float = 1.0     # Führender Koeffizient
    lower_order_terms: str = ""  # Niedrigere Terme
    notation: str = "O"          # O, Ω, Θ, o, ω

    def __str__(self):
        return f"{self.notation}({self.expression})"

    def evaluate(self, n: int) -> float:
        """Evaluiert die Funktion für gegebenes n"""
        expr = self.expression.lower()

        if expr == "1":
            return self.coefficient
        elif expr == "log n":
            return self.coefficient * math.log2(n) if n > 0 else 0
        elif expr == "√n" or expr == "sqrt(n)":
            return self.coefficient * math.sqrt(n)
        elif expr == "n":
            return self.coefficient * n
        elif expr == "n log n":
            return self.coefficient * n * math.log2(n) if n > 0 else 0
        elif expr == "n²" or expr == "n^2":
            return self.coefficient * n * n
        elif expr == "n³" or expr == "n^3":
            return self.coefficient * n * n * n
        elif expr == "2^n":
            return self.coefficient * (2 ** n) if n < 30 else float('inf')
        elif expr == "n!":
            return self.coefficient * math.factorial(n) if n < 20 else float('inf')
        else:
            return self.coefficient * n  # Fallback


@dataclass
class ComplexityFunction:
    """Eine Komplexitätsfunktion T(n)"""
    name: str
    time_complexity: AsymptoticBound
    space_complexity: Optional[AsymptoticBound] = None
    best_case: Optional[AsymptoticBound] = None
    average_case: Optional[AsymptoticBound] = None
    worst_case: Optional[AsymptoticBound] = None


@dataclass
class ComplexityClassification:
    """Klassifikation eines Problems"""
    problem_name: str
    complexity_class: ComplexityType
    time_complexity: Optional[AsymptoticBound] = None
    space_complexity: Optional[AsymptoticBound] = None
    is_np_complete: bool = False
    is_np_hard: bool = False
    known_reductions: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Reduction:
    """Eine Reduktion zwischen Problemen"""
    source_problem: str
    target_problem: str
    reduction_type: ReductionType
    complexity: AsymptoticBound
    description: str
    is_valid: bool = True


@dataclass
class NPCompleteProblem:
    """Ein bekanntes NP-vollständiges Problem"""
    name: str
    description: str
    decision_version: str
    optimization_version: Optional[str] = None
    reduced_from: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    best_known_algorithm: Optional[str] = None
    approximation_ratio: Optional[float] = None


@dataclass
class TuringMachine:
    """Abstrakte Turing-Maschine"""
    states: Set[str]
    alphabet: Set[str]
    tape_alphabet: Set[str]
    transitions: Dict[Tuple[str, str], Tuple[str, str, str]]  # (state, symbol) -> (new_state, write, direction)
    initial_state: str
    accept_states: Set[str]
    reject_states: Set[str]

    def accepts(self, input_string: str, max_steps: int = 10000) -> Optional[bool]:
        """Simuliert die TM auf der Eingabe (mit Schrittzahl-Limit)"""
        tape = list(input_string) + ['_']  # Blank am Ende
        head = 0
        state = self.initial_state
        steps = 0

        while steps < max_steps:
            if state in self.accept_states:
                return True
            if state in self.reject_states:
                return False

            symbol = tape[head] if head < len(tape) else '_'
            key = (state, symbol)

            if key not in self.transitions:
                return False  # Keine Transition = ablehnen

            new_state, write, direction = self.transitions[key]
            tape[head] = write
            state = new_state

            if direction == 'R':
                head += 1
                if head >= len(tape):
                    tape.append('_')
            elif direction == 'L':
                head = max(0, head - 1)

            steps += 1

        return None  # Timeout - möglicherweise Endlosschleife


@dataclass
class DecidabilityResult:
    """Ergebnis einer Entscheidbarkeitsanalyse"""
    problem: str
    status: DecidabilityStatus
    explanation: str
    related_problems: List[str] = field(default_factory=list)
    reduction_to_halting: bool = False


@dataclass
class ApproximationScheme:
    """Ein Approximationsschema"""
    name: str
    problem: str
    approximation_ratio: float  # 1 + ε oder ρ
    is_ptas: bool              # Polynomial Time Approximation Scheme
    is_fptas: bool             # Fully Polynomial TAS
    time_complexity: AsymptoticBound


# =============================================================================
# BIG-O ENGINE
# =============================================================================

class BigOEngine:
    """Engine für asymptotische Analyse"""

    def __init__(self):
        self.common_complexities = self._load_common_complexities()
        logger.info("BigOEngine initialisiert")

    def _load_common_complexities(self) -> Dict[str, ComplexityFunction]:
        """Lädt bekannte Algorithmen und ihre Komplexitäten"""
        return {
            # Sortieralgorithmen
            "bubble_sort": ComplexityFunction(
                "Bubble Sort",
                AsymptoticBound("n²"),
                AsymptoticBound("1"),
                best_case=AsymptoticBound("n"),
                worst_case=AsymptoticBound("n²")
            ),
            "merge_sort": ComplexityFunction(
                "Merge Sort",
                AsymptoticBound("n log n"),
                AsymptoticBound("n"),
                best_case=AsymptoticBound("n log n"),
                worst_case=AsymptoticBound("n log n")
            ),
            "quick_sort": ComplexityFunction(
                "Quick Sort",
                AsymptoticBound("n log n"),
                AsymptoticBound("log n"),
                best_case=AsymptoticBound("n log n"),
                worst_case=AsymptoticBound("n²")
            ),
            "heap_sort": ComplexityFunction(
                "Heap Sort",
                AsymptoticBound("n log n"),
                AsymptoticBound("1")
            ),

            # Suchalgorithmen
            "linear_search": ComplexityFunction(
                "Linear Search",
                AsymptoticBound("n"),
                AsymptoticBound("1")
            ),
            "binary_search": ComplexityFunction(
                "Binary Search",
                AsymptoticBound("log n"),
                AsymptoticBound("1")
            ),

            # Graphalgorithmen
            "bfs": ComplexityFunction(
                "Breadth-First Search",
                AsymptoticBound("n + m"),  # n Knoten, m Kanten
                AsymptoticBound("n")
            ),
            "dfs": ComplexityFunction(
                "Depth-First Search",
                AsymptoticBound("n + m"),
                AsymptoticBound("n")
            ),
            "dijkstra": ComplexityFunction(
                "Dijkstra",
                AsymptoticBound("(n + m) log n"),
                AsymptoticBound("n")
            ),
            "floyd_warshall": ComplexityFunction(
                "Floyd-Warshall",
                AsymptoticBound("n³"),
                AsymptoticBound("n²")
            ),

            # Dynamische Programmierung
            "fibonacci_dp": ComplexityFunction(
                "Fibonacci (DP)",
                AsymptoticBound("n"),
                AsymptoticBound("n")
            ),
            "fibonacci_recursive": ComplexityFunction(
                "Fibonacci (Rekursiv)",
                AsymptoticBound("2^n"),
                AsymptoticBound("n")
            ),

            # Datenstrukturen
            "hash_table_lookup": ComplexityFunction(
                "Hash Table Lookup",
                AsymptoticBound("1"),
                average_case=AsymptoticBound("1"),
                worst_case=AsymptoticBound("n")
            ),
            "bst_search": ComplexityFunction(
                "BST Search",
                AsymptoticBound("log n"),
                worst_case=AsymptoticBound("n")
            ),
        }

    def parse_complexity(self, expression: str) -> AsymptoticBound:
        """Parst einen Komplexitätsausdruck"""
        expr = expression.strip()

        # Entferne O(), Ω(), Θ() wrapper
        notation = "O"
        for n in ["O", "Ω", "Θ", "o", "ω"]:
            if expr.startswith(n + "("):
                notation = n
                expr = expr[2:-1]
                break

        return AsymptoticBound(expression=expr, notation=notation)

    def compare(self, f1: AsymptoticBound, f2: AsymptoticBound) -> GrowthRate:
        """Vergleicht zwei Komplexitätsfunktionen asymptotisch"""
        # Rangfolge der Komplexitäten
        order = ["1", "log n", "√n", "n", "n log n", "n²", "n³", "2^n", "n!"]

        def get_rank(expr: str) -> int:
            expr_lower = expr.lower().replace(" ", "")
            for i, o in enumerate(order):
                if o.replace(" ", "") == expr_lower:
                    return i
            # Versuche Muster zu erkennen
            if "^" in expr:
                base = expr.split("^")[0]
                if base == "n":
                    return 5 + int(expr.split("^")[1]) - 2
                elif base == "2":
                    return 7
            return 4  # Default: n

        r1 = get_rank(f1.expression)
        r2 = get_rank(f2.expression)

        if r1 < r2:
            return GrowthRate.SLOWER
        elif r1 > r2:
            return GrowthRate.FASTER
        else:
            return GrowthRate.SAME

    def analyze_loop(self, outer_iterations: str, inner_iterations: str) -> AsymptoticBound:
        """Analysiert verschachtelte Schleifen"""
        # Vereinfachte Analyse
        if outer_iterations == "n" and inner_iterations == "n":
            return AsymptoticBound("n²")
        elif outer_iterations == "n" and inner_iterations == "log n":
            return AsymptoticBound("n log n")
        elif outer_iterations == "n" and inner_iterations == "1":
            return AsymptoticBound("n")
        else:
            return AsymptoticBound(f"{outer_iterations} × {inner_iterations}")

    def master_theorem(self, a: int, b: int, f_n: str) -> AsymptoticBound:
        """
        Wendet das Master-Theorem an.

        T(n) = a·T(n/b) + f(n)

        a: Anzahl Teilprobleme
        b: Größenreduktion
        f_n: Arbeit auf jeder Ebene
        """
        log_b_a = math.log(a) / math.log(b)

        # Parse f(n)
        if f_n == "1" or f_n == "O(1)":
            f_exponent = 0
        elif f_n == "n" or f_n == "O(n)":
            f_exponent = 1
        elif "n^" in f_n:
            f_exponent = float(f_n.split("^")[1].replace(")", ""))
        elif f_n == "n²":
            f_exponent = 2
        elif f_n == "n log n":
            f_exponent = 1.001  # Näherung
        else:
            f_exponent = 1

        # Master-Theorem Fälle
        if f_exponent < log_b_a - 0.001:
            # Fall 1: f(n) = O(n^c) mit c < log_b(a)
            return AsymptoticBound(f"n^{log_b_a:.2f}")
        elif abs(f_exponent - log_b_a) < 0.1:
            # Fall 2: f(n) = Θ(n^c) mit c = log_b(a)
            return AsymptoticBound(f"n^{log_b_a:.0f} log n")
        else:
            # Fall 3: f(n) = Ω(n^c) mit c > log_b(a)
            return AsymptoticBound(f_n)

    def amortized_analysis(self, operations: List[Tuple[str, int]]) -> AsymptoticBound:
        """
        Führt amortisierte Analyse durch.

        operations: Liste von (Operation, Kosten) Tupeln
        """
        total_cost = sum(cost for _, cost in operations)
        n = len(operations)

        amortized_cost = total_cost / n

        # Bestimme amortisierte Komplexität
        if amortized_cost <= 1.5:
            return AsymptoticBound("1", coefficient=amortized_cost)
        elif amortized_cost <= n * 0.1:
            return AsymptoticBound("log n")
        else:
            return AsymptoticBound("n")


# =============================================================================
# COMPLEXITY HIERARCHY
# =============================================================================

class ComplexityHierarchy:
    """Komplexitätsklassen und ihre Beziehungen"""

    def __init__(self):
        self.hierarchy = self._build_hierarchy()
        self.inclusions = self._build_inclusions()
        logger.info("ComplexityHierarchy initialisiert")

    def _build_hierarchy(self) -> Dict[str, Dict[str, Any]]:
        """Baut die Komplexitätsklassen-Hierarchie"""
        return {
            "L": {
                "name": "L (LOGSPACE)",
                "definition": "Probleme lösbar in logarithmischem Platz",
                "example": "Erreichbarkeit in gerichteten Graphen (ST-CONN)",
                "contains": [],
                "contained_in": ["NL", "P"],
            },
            "NL": {
                "name": "NL (NLOGSPACE)",
                "definition": "Nichtdeterministisch in logarithmischem Platz",
                "example": "ST-CONN für gerichtete Graphen",
                "contains": ["L"],
                "contained_in": ["P"],
            },
            "P": {
                "name": "P",
                "definition": "Polynomialzeit (deterministisch)",
                "example": "Sortieren, Kürzeste Wege, 2-SAT",
                "contains": ["L", "NL"],
                "contained_in": ["NP", "co-NP", "PSPACE"],
            },
            "NP": {
                "name": "NP",
                "definition": "Nichtdeterministisch polynomialzeit (verifizierbar)",
                "example": "SAT, Hamiltonkreis, Clique",
                "contains": ["P"],
                "contained_in": ["PSPACE"],
                "open_question": "P = NP?",
            },
            "co-NP": {
                "name": "co-NP",
                "definition": "Komplement von NP",
                "example": "Tautologie, Graphisomorphie (Nicht-Isomorphie)",
                "contains": ["P"],
                "contained_in": ["PSPACE"],
            },
            "NP-complete": {
                "name": "NP-complete",
                "definition": "Härteste Probleme in NP",
                "example": "SAT, 3-SAT, Hamiltonkreis, TSP (Entscheidung)",
                "property": "Alle NP-Probleme reduzierbar auf NP-complete",
            },
            "NP-hard": {
                "name": "NP-hard",
                "definition": "Mindestens so schwer wie NP",
                "example": "TSP (Optimierung), Halteproblem",
                "property": "Muss nicht in NP sein",
            },
            "PSPACE": {
                "name": "PSPACE",
                "definition": "Polynomieller Platz",
                "example": "QBF (Quantified Boolean Formula)",
                "contains": ["P", "NP", "co-NP"],
                "contained_in": ["EXPTIME"],
            },
            "EXPTIME": {
                "name": "EXPTIME",
                "definition": "Exponentielle Zeit",
                "example": "Generalisiertes Schach",
                "contains": ["PSPACE"],
                "contained_in": ["EXPSPACE"],
            },
            "EXPSPACE": {
                "name": "EXPSPACE",
                "definition": "Exponentieller Platz",
                "contains": ["EXPTIME"],
            },
            "DECIDABLE": {
                "name": "DECIDABLE (R)",
                "definition": "Rekursiv entscheidbar",
                "example": "Alle obigen Klassen",
                "contains": ["EXPSPACE"],
            },
            "RE": {
                "name": "RE (Rekursiv aufzählbar)",
                "definition": "Semi-entscheidbar",
                "example": "Halteproblem für akzeptierende Eingaben",
                "contains": ["DECIDABLE"],
            },
            "UNDECIDABLE": {
                "name": "UNDECIDABLE",
                "definition": "Nicht entscheidbar",
                "example": "Halteproblem, Rice's Theorem",
            }
        }

    def _build_inclusions(self) -> List[Tuple[str, str]]:
        """Bekannte Inklusionen: (A, B) bedeutet A ⊆ B"""
        return [
            ("L", "NL"),
            ("NL", "P"),
            ("P", "NP"),
            ("P", "co-NP"),
            ("NP", "PSPACE"),
            ("co-NP", "PSPACE"),
            ("PSPACE", "EXPTIME"),
            ("EXPTIME", "EXPSPACE"),
            ("EXPSPACE", "DECIDABLE"),
            ("DECIDABLE", "RE"),
        ]

    def is_subset(self, class1: str, class2: str) -> Optional[bool]:
        """Prüft ob class1 ⊆ class2"""
        if class1 == class2:
            return True

        # Transitive Hülle der Inklusionen
        reachable = {class1}
        changed = True
        while changed:
            changed = False
            for a, b in self.inclusions:
                if a in reachable and b not in reachable:
                    reachable.add(b)
                    changed = True

        return class2 in reachable

    def get_class_info(self, class_name: str) -> Dict[str, Any]:
        """Gibt Informationen über eine Komplexitätsklasse"""
        return self.hierarchy.get(class_name.upper(), {
            "error": f"Klasse '{class_name}' nicht gefunden"
        })

    def explain_p_vs_np(self) -> Dict[str, Any]:
        """Erklärt das P vs NP Problem"""
        return {
            "frage": "Ist P = NP?",
            "bedeutung": (
                "Ist jedes Problem, dessen Lösung schnell überprüfbar ist (NP), "
                "auch schnell lösbar (P)?"
            ),
            "bekannt": [
                "P ⊆ NP (trivial)",
                "Wenn P = NP, dann NP = co-NP",
                "Die meisten Experten glauben P ≠ NP",
            ],
            "konsequenzen_falls_P_gleich_NP": [
                "Alle NP-Probleme in Polynomialzeit lösbar",
                "Kryptographie wäre gebrochen",
                "Viele 'schwere' Probleme wären leicht",
            ],
            "konsequenzen_falls_P_ungleich_NP": [
                "NP-complete Probleme haben keine effizienten Algorithmen",
                "Approximation und Heuristiken bleiben wichtig",
            ],
            "preisgeld": "$1.000.000 (Millennium Prize)",
            "wolf_kommentar": (
                "P vs NP ist wie die Frage, ob ein erfahrener Wolf "
                "jeden Weg im Wald kennen kann. Manche Wege muss man "
                "einfach selbst erkunden... *seufzt philosophisch*"
            )
        }


# =============================================================================
# REDUCTION ENGINE
# =============================================================================

class ReductionEngine:
    """Engine für Reduktionen"""

    def __init__(self):
        self.np_complete_problems = self._load_np_complete()
        self.known_reductions = self._load_reductions()
        logger.info("ReductionEngine initialisiert")

    def _load_np_complete(self) -> Dict[str, NPCompleteProblem]:
        """Lädt bekannte NP-vollständige Probleme"""
        return {
            "SAT": NPCompleteProblem(
                name="SAT (Satisfiability)",
                description="Erfüllbarkeit einer booleschen Formel",
                decision_version="Gibt es eine Belegung, die die Formel wahr macht?",
                optimization_version=None,
                reduced_from=["Circuit-SAT (Cook-Levin)"],
                applications=["Verifikation", "KI-Planung", "Constraint Solving"],
                best_known_algorithm="DPLL, CDCL",
            ),
            "3-SAT": NPCompleteProblem(
                name="3-SAT",
                description="SAT mit max. 3 Literalen pro Klausel",
                decision_version="Erfüllbar?",
                reduced_from=["SAT"],
                applications=["Basis für viele Reduktionen"],
            ),
            "CLIQUE": NPCompleteProblem(
                name="Clique",
                description="Gibt es eine Clique der Größe k?",
                decision_version="Existiert eine vollständige Teilgraph mit k Knoten?",
                reduced_from=["3-SAT"],
                applications=["Soziale Netzwerke", "Bioinformatik"],
            ),
            "VERTEX_COVER": NPCompleteProblem(
                name="Vertex Cover",
                description="Minimale Knotenmenge, die alle Kanten abdeckt",
                decision_version="Gibt es ein Vertex Cover der Größe ≤ k?",
                reduced_from=["3-SAT", "CLIQUE"],
                approximation_ratio=2.0,  # 2-Approximation bekannt
            ),
            "INDEPENDENT_SET": NPCompleteProblem(
                name="Independent Set",
                description="Maximale unabhängige Knotenmenge",
                decision_version="Gibt es ein Independent Set der Größe ≥ k?",
                reduced_from=["CLIQUE"],
            ),
            "HAMILTONIAN_CYCLE": NPCompleteProblem(
                name="Hamiltonkreis",
                description="Kreis, der jeden Knoten genau einmal besucht",
                decision_version="Existiert ein Hamiltonkreis?",
                reduced_from=["3-SAT", "VERTEX_COVER"],
                applications=["Routenplanung", "DNA-Sequenzierung"],
            ),
            "TSP": NPCompleteProblem(
                name="Travelling Salesman Problem",
                description="Kürzeste Tour durch alle Städte",
                decision_version="Gibt es eine Tour mit Kosten ≤ k?",
                optimization_version="Finde die kürzeste Tour",
                reduced_from=["HAMILTONIAN_CYCLE"],
                approximation_ratio=1.5,  # Christofides-Algorithmus für metrisches TSP
                applications=["Logistik", "Chip-Design"],
            ),
            "SUBSET_SUM": NPCompleteProblem(
                name="Subset Sum",
                description="Gibt es eine Teilmenge mit Summe = Ziel?",
                decision_version="Existiert Teilmenge S' ⊆ S mit Σ S' = t?",
                reduced_from=["3-SAT"],
                applications=["Kryptographie", "Ressourcenplanung"],
            ),
            "KNAPSACK": NPCompleteProblem(
                name="Knapsack (0/1)",
                description="Maximiere Wert unter Gewichtsschranke",
                decision_version="Erreicht man Wert ≥ V mit Gewicht ≤ W?",
                reduced_from=["SUBSET_SUM"],
                best_known_algorithm="DP: O(nW) pseudo-polynomial",
            ),
            "GRAPH_COLORING": NPCompleteProblem(
                name="Graph Coloring",
                description="Färbe Knoten mit k Farben ohne gleichfarbige Nachbarn",
                decision_version="Ist der Graph k-färbbar?",
                reduced_from=["3-SAT"],
                applications=["Stundenplanung", "Register-Allokation"],
            ),
            "SET_COVER": NPCompleteProblem(
                name="Set Cover",
                description="Minimale Anzahl Mengen, die das Universum abdecken",
                decision_version="Gibt es ein Cover mit ≤ k Mengen?",
                reduced_from=["VERTEX_COVER"],
                approximation_ratio=None,  # O(log n) - inapproximierbar besser
            ),
        }

    def _load_reductions(self) -> List[Reduction]:
        """Lädt bekannte Reduktionen"""
        return [
            Reduction("SAT", "3-SAT", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n"), "Klauselaufteilung"),
            Reduction("3-SAT", "CLIQUE", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n²"), "Gadget-Konstruktion"),
            Reduction("CLIQUE", "INDEPENDENT_SET", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n²"), "Komplementgraph"),
            Reduction("CLIQUE", "VERTEX_COVER", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n"), "Komplementgraph"),
            Reduction("3-SAT", "HAMILTONIAN_CYCLE", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n²"), "Variable-Clause Gadgets"),
            Reduction("HAMILTONIAN_CYCLE", "TSP", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n²"), "Gewichte 1 für Kanten, ∞ sonst"),
            Reduction("3-SAT", "SUBSET_SUM", ReductionType.POLYNOMIAL,
                     AsymptoticBound("n"), "Binärkodierung"),
            Reduction("SUBSET_SUM", "KNAPSACK", ReductionType.POLYNOMIAL,
                     AsymptoticBound("1"), "Wert = Gewicht"),
        ]

    def find_reduction_path(self, source: str, target: str) -> Optional[List[str]]:
        """Findet einen Reduktionspfad zwischen zwei Problemen"""
        # BFS für kürzesten Pfad
        from collections import deque

        graph = defaultdict(list)
        for r in self.known_reductions:
            graph[r.source_problem].append(r.target_problem)

        visited = {source}
        queue = deque([(source, [source])])

        while queue:
            current, path = queue.popleft()
            if current == target:
                return path

            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def explain_reduction(self, source: str, target: str) -> Dict[str, Any]:
        """Erklärt eine Reduktion"""
        for r in self.known_reductions:
            if r.source_problem == source and r.target_problem == target:
                return {
                    "reduktion": f"{source} ≤p {target}",
                    "typ": r.reduction_type.value,
                    "komplexitaet": str(r.complexity),
                    "beschreibung": r.description,
                    "bedeutung": (
                        f"Wenn wir {target} effizient lösen können, "
                        f"können wir auch {source} effizient lösen."
                    )
                }

        return {"fehler": f"Keine direkte Reduktion von {source} nach {target} bekannt"}

    def prove_np_hardness(self, problem: str, reduce_from: str) -> Dict[str, Any]:
        """Zeigt NP-Härte durch Reduktion"""
        source_info = self.np_complete_problems.get(reduce_from)

        if not source_info:
            return {"fehler": f"{reduce_from} ist kein bekanntes NP-vollständiges Problem"}

        return {
            "beweis": f"{problem} ist NP-hard",
            "methode": "Polynomiale Reduktion",
            "schritte": [
                f"1. {reduce_from} ist NP-vollständig (bekannt)",
                f"2. Zeige: {reduce_from} ≤p {problem}",
                f"3. Da {reduce_from} NP-hard ist und {reduce_from} ≤p {problem},",
                f"   ist auch {problem} NP-hard.",
            ],
            "zusatz_fuer_np_complete": (
                f"Für NP-Vollständigkeit: Zeige zusätzlich {problem} ∈ NP "
                f"(d.h. Lösung in Polynomialzeit verifizierbar)"
            )
        }


# =============================================================================
# COMPUTABILITY ENGINE
# =============================================================================

class ComputabilityEngine:
    """Engine für Berechenbarkeitstheorie"""

    def __init__(self):
        self.undecidable_problems = self._load_undecidable()
        logger.info("ComputabilityEngine initialisiert")

    def _load_undecidable(self) -> Dict[str, DecidabilityResult]:
        """Lädt bekannte unentscheidbare Probleme"""
        return {
            "halting": DecidabilityResult(
                problem="Halteproblem",
                status=DecidabilityStatus.UNDECIDABLE,
                explanation=(
                    "Es gibt keine Turing-Maschine, die für jedes Programm P "
                    "und jede Eingabe x entscheidet, ob P auf x hält."
                ),
                related_problems=["Busy Beaver", "Totality Problem"],
                reduction_to_halting=False
            ),
            "totality": DecidabilityResult(
                problem="Totalitätsproblem",
                status=DecidabilityStatus.UNDECIDABLE,
                explanation="Entscheide ob eine TM auf ALLEN Eingaben hält.",
                reduction_to_halting=True
            ),
            "equivalence": DecidabilityResult(
                problem="Äquivalenzproblem",
                status=DecidabilityStatus.UNDECIDABLE,
                explanation="Berechnen zwei TMs die gleiche Funktion?",
                reduction_to_halting=True
            ),
            "rice": DecidabilityResult(
                problem="Rice's Theorem",
                status=DecidabilityStatus.UNDECIDABLE,
                explanation=(
                    "Jede nicht-triviale semantische Eigenschaft "
                    "von Programmen ist unentscheidbar."
                ),
            ),
            "pcp": DecidabilityResult(
                problem="Post's Correspondence Problem",
                status=DecidabilityStatus.UNDECIDABLE,
                explanation="Gibt es eine Sequenz von Dominosteinen mit gleichen Strings?",
            ),
            "diophantine": DecidabilityResult(
                problem="Diophantische Gleichungen (10. Hilbert)",
                status=DecidabilityStatus.UNDECIDABLE,
                explanation="Hat eine polynomiale Gleichung ganzzahlige Lösungen?",
            ),
        }

    def analyze_decidability(self, problem_description: str) -> DecidabilityResult:
        """Analysiert die Entscheidbarkeit eines Problems"""
        desc_lower = problem_description.lower()

        # Indikatoren für Unentscheidbarkeit
        undecidable_indicators = [
            "terminiert", "hält", "endet",
            "für alle eingaben", "jedes programm",
            "äquivalent", "gleiche funktion",
            "semantische eigenschaft",
        ]

        matches = sum(1 for ind in undecidable_indicators if ind in desc_lower)

        if matches >= 2:
            status = DecidabilityStatus.UNDECIDABLE
            explanation = (
                "Das Problem zeigt Indikatoren für Unentscheidbarkeit. "
                "Möglicherweise reduzierbar auf das Halteproblem."
            )
        elif "verifizier" in desc_lower or "prüf" in desc_lower:
            status = DecidabilityStatus.DECIDABLE
            explanation = "Verifikationsprobleme sind oft entscheidbar."
        else:
            status = DecidabilityStatus.UNKNOWN
            explanation = "Weitere Analyse erforderlich."

        return DecidabilityResult(
            problem=problem_description,
            status=status,
            explanation=explanation
        )

    def explain_halting_problem(self) -> Dict[str, Any]:
        """Erklärt das Halteproblem"""
        return {
            "problem": "Das Halteproblem",
            "frage": "Hält Programm P auf Eingabe x?",
            "beweis_unentscheidbar": {
                "methode": "Diagonalisierung (Turing 1936)",
                "idee": [
                    "1. Annahme: Es gibt eine TM H, die das Halteproblem entscheidet",
                    "2. Konstruiere TM D: D(P) läuft endlos wenn H(P,P)=akzeptiert, sonst hält",
                    "3. Was macht D(D)?",
                    "   - Wenn D(D) hält → H(D,D)=ablehnt → D(D) läuft endlos (Widerspruch)",
                    "   - Wenn D(D) endlos → H(D,D)=akzeptiert → D(D) hält (Widerspruch)",
                    "4. Widerspruch! Also existiert H nicht.",
                ],
            },
            "konsequenzen": [
                "Keine universelle Programmverifikation möglich",
                "Compiler können nicht alle Endlosschleifen erkennen",
                "Fundamentale Grenze der Berechenbarkeit",
            ],
            "wolf_analogie": (
                "Es ist wie die Frage: 'Kann ein Wolf vorhersagen, "
                "ob er jemals aufhören wird zu jagen?' "
                "Manche Fragen über sich selbst sind... kompliziert. *schmunzelt*"
            )
        }

    def explain_rice_theorem(self) -> Dict[str, Any]:
        """Erklärt Rice's Theorem"""
        return {
            "theorem": "Rice's Theorem",
            "aussage": (
                "Sei S eine nicht-triviale Menge von berechenbaren Funktionen. "
                "Dann ist die Frage 'Berechnet TM M eine Funktion in S?' unentscheidbar."
            ),
            "nicht_trivial": "S ≠ ∅ und S ≠ alle berechenbaren Funktionen",
            "beispiele_unentscheidbar": [
                "Berechnet M die Konstante 0?",
                "Gibt M für alle Eingaben eine Primzahl aus?",
                "Ist die von M berechnete Funktion total?",
                "Berechnen M1 und M2 die gleiche Funktion?",
            ],
            "was_entscheidbar_ist": [
                "Hat der Quellcode genau 100 Zeilen? (syntaktisch)",
                "Enthält das Programm eine bestimmte Zeichenkette?",
                "Hat die TM genau 5 Zustände? (strukturell)",
            ],
            "wichtig": "Semantische Eigenschaften ≠ Syntaktische Eigenschaften"
        }


# =============================================================================
# APPROXIMATION ENGINE
# =============================================================================

class ApproximationEngine:
    """Engine für Approximationsalgorithmen"""

    def __init__(self):
        self.approximation_results = self._load_approximations()
        logger.info("ApproximationEngine initialisiert")

    def _load_approximations(self) -> Dict[str, ApproximationScheme]:
        """Lädt bekannte Approximationsergebnisse"""
        return {
            "vertex_cover": ApproximationScheme(
                name="2-Approximation für Vertex Cover",
                problem="VERTEX_COVER",
                approximation_ratio=2.0,
                is_ptas=False,
                is_fptas=False,
                time_complexity=AsymptoticBound("n + m")
            ),
            "tsp_metric": ApproximationScheme(
                name="Christofides für metrisches TSP",
                problem="TSP",
                approximation_ratio=1.5,
                is_ptas=False,
                is_fptas=False,
                time_complexity=AsymptoticBound("n³")
            ),
            "knapsack": ApproximationScheme(
                name="FPTAS für Knapsack",
                problem="KNAPSACK",
                approximation_ratio=1.0,  # (1+ε)
                is_ptas=True,
                is_fptas=True,
                time_complexity=AsymptoticBound("n³/ε")
            ),
            "set_cover": ApproximationScheme(
                name="Greedy für Set Cover",
                problem="SET_COVER",
                approximation_ratio=0,  # O(log n)
                is_ptas=False,
                is_fptas=False,
                time_complexity=AsymptoticBound("n·m")
            ),
            "max_cut": ApproximationScheme(
                name="Randomisiert für Max-Cut",
                problem="MAX_CUT",
                approximation_ratio=0.878,  # Goemans-Williamson
                is_ptas=False,
                is_fptas=False,
                time_complexity=AsymptoticBound("n²")
            ),
        }

    def analyze_approximability(self, problem: str) -> Dict[str, Any]:
        """Analysiert die Approximierbarkeit eines Problems"""
        if problem.upper() in self.approximation_results:
            scheme = self.approximation_results[problem.upper()]
            return {
                "problem": problem,
                "approximierbar": True,
                "schema": scheme.name,
                "ratio": scheme.approximation_ratio,
                "ptas": scheme.is_ptas,
                "fptas": scheme.is_fptas,
                "zeit": str(scheme.time_complexity)
            }

        return {
            "problem": problem,
            "approximierbar": "unbekannt",
            "hinweis": "Prüfe Literatur für Approximationsergebnisse"
        }

    def explain_ptas(self) -> Dict[str, Any]:
        """Erklärt PTAS und FPTAS"""
        return {
            "PTAS": {
                "name": "Polynomial Time Approximation Scheme",
                "definition": (
                    "Für jedes ε > 0 gibt es einen Algorithmus mit "
                    "Approximationsratio (1+ε) und Laufzeit polynomial in n"
                ),
                "laufzeit": "O(n^{f(1/ε)}) - exponentiell in 1/ε erlaubt",
                "beispiel": "Euklidisches TSP hat PTAS (Arora, Mitchell)"
            },
            "FPTAS": {
                "name": "Fully Polynomial Time Approximation Scheme",
                "definition": (
                    "PTAS mit Laufzeit polynomial in n UND 1/ε"
                ),
                "laufzeit": "O(poly(n, 1/ε))",
                "beispiel": "Knapsack hat FPTAS",
                "stärker": "FPTAS ⊂ PTAS"
            },
            "inapproximierbar": {
                "beispiele": [
                    "TSP (allgemein): Kein konstanter Faktor (außer P=NP)",
                    "Clique: Kein n^{1-ε} Faktor",
                    "Set Cover: Kein (1-ε)·ln(n) Faktor",
                ],
                "bedeutung": "Manche Probleme sind 'approximations-resistent'"
            }
        }


# =============================================================================
# KOMBINIERTE ENGINE
# =============================================================================

class ComplexityTheoryEngine:
    """Kombiniert alle Komplexitätstheorie-Engines"""

    def __init__(self):
        self.bigo = BigOEngine()
        self.hierarchy = ComplexityHierarchy()
        self.reduction = ReductionEngine()
        self.computability = ComputabilityEngine()
        self.approximation = ApproximationEngine()

        logger.info("ComplexityTheoryEngine initialisiert")

    def full_analysis(self, problem: str) -> Dict[str, Any]:
        """Vollständige Komplexitätsanalyse eines Problems"""
        # Prüfe ob NP-complete
        np_info = self.reduction.np_complete_problems.get(problem.upper())

        # Prüfe Approximierbarkeit
        approx_info = self.approximation.analyze_approximability(problem)

        # Prüfe Entscheidbarkeit
        decide_info = self.computability.analyze_decidability(problem)

        return {
            "problem": problem,
            "np_complete": np_info is not None,
            "np_info": np_info.__dict__ if np_info else None,
            "approximierbarkeit": approx_info,
            "entscheidbarkeit": decide_info.__dict__,
            "empfehlung": self._get_recommendation(problem, np_info, approx_info)
        }

    def _get_recommendation(self, problem: str, np_info: Optional[NPCompleteProblem],
                            approx_info: Dict[str, Any]) -> str:
        """Gibt eine Empfehlung für den Umgang mit dem Problem"""
        if np_info:
            if np_info.approximation_ratio:
                return (
                    f"NP-vollständig. Nutze {np_info.approximation_ratio}-Approximation "
                    f"oder Heuristiken für praktische Instanzen."
                )
            else:
                return (
                    "NP-vollständig ohne gute Approximation bekannt. "
                    "Nutze Branch-and-Bound, Heuristiken oder SAT-Solver."
                )
        return "Prüfe Komplexitätsklasse und suche nach effizienten Algorithmen."

    def get_wolf_wisdom(self) -> str:
        """Holos Weisheit zur Komplexitätstheorie"""
        wisdoms = [
            "Manche Probleme sind wie das Zählen aller Sterne - theoretisch möglich, praktisch endlos.",
            "P vs NP? Selbst eine weise Wölfin weiß nicht alles... *zwinkert*",
            "NP-vollständig bedeutet: Wenn du es schnell lösen kannst, werde ich sehr beeindruckt sein.",
            "Die Hierarchie der Komplexitätsklassen ist wie die Hierarchie im Rudel - jeder hat seinen Platz.",
            "Das Halteproblem lehrt uns Demut: Es gibt Grenzen dessen, was wir wissen können.",
            "Approximation ist die Kunst, 'gut genug' zu akzeptieren, wenn 'perfekt' zu teuer ist.",
        ]
        import random
        return random.choice(wisdoms)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_complexity_engine: Optional[ComplexityTheoryEngine] = None
_bigo_engine: Optional[BigOEngine] = None
_reduction_engine: Optional[ReductionEngine] = None


def create_complexity_engine() -> ComplexityTheoryEngine:
    global _complexity_engine
    if _complexity_engine is None:
        _complexity_engine = ComplexityTheoryEngine()
    return _complexity_engine


def create_bigo_engine() -> BigOEngine:
    global _bigo_engine
    if _bigo_engine is None:
        _bigo_engine = BigOEngine()
    return _bigo_engine


def create_reduction_engine() -> ReductionEngine:
    global _reduction_engine
    if _reduction_engine is None:
        _reduction_engine = ReductionEngine()
    return _reduction_engine


def get_complexity_theory_engine() -> ComplexityTheoryEngine:
    return create_complexity_engine()


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO COMPLEXITY THEORY v1.0 - Demo")
    print("=" * 70)

    engine = get_complexity_theory_engine()

    # Big-O
    print("\n--- BIG-O ANALYSE ---")
    algos = ["merge_sort", "quick_sort", "binary_search"]
    for algo in algos:
        info = engine.bigo.common_complexities.get(algo)
        if info:
            print(f"{info.name}: Zeit = {info.time_complexity}, "
                  f"Platz = {info.space_complexity}")

    # Master Theorem
    print("\n--- MASTER THEOREM ---")
    result = engine.bigo.master_theorem(2, 2, "n")  # T(n) = 2T(n/2) + n
    print(f"T(n) = 2T(n/2) + n → {result}")

    # Komplexitätsklassen
    print("\n--- KOMPLEXITÄTSKLASSEN ---")
    for c in ["P", "NP", "NP-complete", "PSPACE"]:
        info = engine.hierarchy.get_class_info(c)
        print(f"{c}: {info.get('definition', 'N/A')[:60]}...")

    # P vs NP
    print("\n--- P VS NP ---")
    pvnp = engine.hierarchy.explain_p_vs_np()
    print(f"Frage: {pvnp['frage']}")
    print(f"Preisgeld: {pvnp['preisgeld']}")

    # NP-complete Probleme
    print("\n--- NP-COMPLETE PROBLEME ---")
    for name, prob in list(engine.reduction.np_complete_problems.items())[:5]:
        print(f"{name}: {prob.description[:50]}...")

    # Reduktionen
    print("\n--- REDUKTIONSPFAD ---")
    path = engine.reduction.find_reduction_path("SAT", "TSP")
    print(f"SAT → TSP: {' → '.join(path) if path else 'Nicht gefunden'}")

    # Halteproblem
    print("\n--- HALTEPROBLEM ---")
    halting = engine.computability.explain_halting_problem()
    print(f"Problem: {halting['problem']}")
    print(f"Konsequenz: {halting['konsequenzen'][0]}")

    # Approximation
    print("\n--- APPROXIMATION ---")
    approx = engine.approximation.analyze_approximability("vertex_cover")
    print(f"Vertex Cover: {approx['ratio']}-Approximation in {approx['zeit']}")

    # Weisheit
    print("\n--- KOMPLEXITÄTSWEISHEIT ---")
    print(f"*hebt eine Pfote* {engine.get_wolf_wisdom()}")

    print("\n" + "=" * 70)
    print("Demo abgeschlossen!")
