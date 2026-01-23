#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO ANALYTICAL STRATEGIES - Analytisch-Synthetische Strategien            ║
║                                                                              ║
║  Implementiert systematische Problemlösungs-Frameworks:                      ║
║                                                                              ║
║  1. MECE ANALYSIS         → Mutually Exclusive, Collectively Exhaustive     ║
║  2. ROOT CAUSE ANALYSIS   → 5-Why, Ishikawa, Fault Tree                     ║
║  3. MORPHOLOGICAL         → Zwicky Box, Kombinatorische Analyse             ║
║                                                                              ║
║  Diese Strategien strukturieren komplexe Probleme systematisch.             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Autor: Holocloude System
Version: 1.0
"""

import logging
import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from enum import Enum, auto
from datetime import datetime
from collections import defaultdict
import random

logger = logging.getLogger("HoloAnalyticalStrategies")


# =============================================================================
# ENUMS
# =============================================================================

class AnalysisType(Enum):
    """Verfügbare Analyse-Strategien"""
    MECE = "mece"
    ROOT_CAUSE = "root_cause"
    MORPHOLOGICAL = "morphological"
    COMBINED = "combined"


class MECEStatus(Enum):
    """Status einer MECE-Zerlegung"""
    VALID = "valid"                # Perfekt MECE
    OVERLAPPING = "overlapping"    # Kategorien überlappen
    INCOMPLETE = "incomplete"      # Nicht alle Fälle abgedeckt
    BOTH_ISSUES = "both_issues"    # Sowohl Überlappung als auch unvollständig


class RootCauseMethod(Enum):
    """Root Cause Analysis Methoden"""
    FIVE_WHY = "five_why"
    ISHIKAWA = "ishikawa"          # Fishbone Diagram
    FAULT_TREE = "fault_tree"
    PARETO = "pareto"
    COMBINED = "combined"


class IshikawaCategory(Enum):
    """Standard Ishikawa (6M) Kategorien"""
    MENSCH = "mensch"              # People / Man
    MASCHINE = "maschine"          # Machine / Equipment
    MATERIAL = "material"          # Materials
    METHODE = "methode"            # Methods / Process
    MESSUNG = "messung"            # Measurement
    MILIEU = "milieu"              # Environment / Mother Nature


class MorphologicalDimension(Enum):
    """Dimensionen für morphologische Analyse"""
    FUNCTION = "function"          # Was soll es tun?
    STRUCTURE = "structure"        # Wie ist es aufgebaut?
    PROCESS = "process"            # Wie funktioniert es?
    INTERFACE = "interface"        # Wie interagiert es?
    RESOURCE = "resource"          # Was wird benötigt?
    CONSTRAINT = "constraint"      # Was sind die Grenzen?


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class MECECategory:
    """Eine Kategorie in einer MECE-Zerlegung"""
    name: str
    description: str
    elements: List[str] = field(default_factory=list)
    subcategories: List['MECECategory'] = field(default_factory=list)
    coverage_percentage: float = 0.0
    parent: Optional[str] = None


@dataclass
class MECEAnalysis:
    """Ergebnis einer MECE-Analyse"""
    problem: str
    categories: List[MECECategory]
    status: MECEStatus
    overlaps: List[Tuple[str, str]]  # Paare überlappender Kategorien
    gaps: List[str]                   # Nicht abgedeckte Bereiche
    total_coverage: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WhyNode:
    """Ein Knoten in der 5-Why-Analyse"""
    question: str
    answer: str
    level: int  # 1-5
    is_root_cause: bool = False
    evidence: List[str] = field(default_factory=list)
    children: List['WhyNode'] = field(default_factory=list)


@dataclass
class IshikawaCause:
    """Eine Ursache im Ishikawa-Diagramm"""
    category: IshikawaCategory
    cause: str
    sub_causes: List[str] = field(default_factory=list)
    probability: float = 0.5
    controllable: bool = True


@dataclass
class FaultTreeNode:
    """Ein Knoten im Fehlerbaum"""
    event: str
    is_basic_event: bool = False
    gate_type: str = "OR"  # "AND" oder "OR"
    children: List['FaultTreeNode'] = field(default_factory=list)
    probability: float = 0.0


@dataclass
class RootCauseResult:
    """Ergebnis einer Root Cause Analysis"""
    problem: str
    method: RootCauseMethod
    identified_causes: List[str]
    root_causes: List[str]
    evidence: Dict[str, List[str]]
    recommended_actions: List[str]
    confidence: float


@dataclass
class MorphologicalParameter:
    """Ein Parameter in der morphologischen Box"""
    name: str
    dimension: MorphologicalDimension
    options: List[str]
    description: str = ""


@dataclass
class MorphologicalSolution:
    """Eine Lösung aus der morphologischen Analyse"""
    parameters: Dict[str, str]  # Parameter -> gewählte Option
    feasibility_score: float
    novelty_score: float
    description: str = ""


# =============================================================================
# 1. MECE ANALYSIS - Mutually Exclusive, Collectively Exhaustive
# =============================================================================

class MECEAnalyzer:
    """
    MECE-Analyse Framework (McKinsey-Methode).

    MECE = Mutually Exclusive, Collectively Exhaustive
    - Kategorien überlappen nicht (ME)
    - Alle Möglichkeiten sind abgedeckt (CE)
    """

    def __init__(self):
        self.analyses: List[MECEAnalysis] = []
        self.common_frameworks: Dict[str, List[str]] = self._load_frameworks()

    def _load_frameworks(self) -> Dict[str, List[str]]:
        """Lädt vordefinierte MECE-Frameworks"""
        return {
            "markt_segmentierung": [
                "Geografisch",
                "Demografisch",
                "Psychografisch",
                "Verhaltensbasiert"
            ],
            "wertschöpfungskette": [
                "Eingangslogistik",
                "Produktion",
                "Ausgangslogistik",
                "Marketing & Vertrieb",
                "Service"
            ],
            "profitabilität": [
                "Umsatz",
                "Kosten"
            ],
            "umsatz": [
                "Preis",
                "Menge"
            ],
            "kosten": [
                "Fixkosten",
                "Variable Kosten"
            ],
            "zeitlich": [
                "Vergangenheit",
                "Gegenwart",
                "Zukunft"
            ],
            "stakeholder": [
                "Intern",
                "Extern"
            ],
            "swot": [
                "Stärken",
                "Schwächen",
                "Chancen",
                "Risiken"
            ],
            "3c": [
                "Company (Unternehmen)",
                "Customers (Kunden)",
                "Competitors (Wettbewerber)"
            ],
            "4p_marketing": [
                "Product (Produkt)",
                "Price (Preis)",
                "Place (Vertrieb)",
                "Promotion (Kommunikation)"
            ],
            "entscheidung": [
                "Ja",
                "Nein"
            ],
            "risiko": [
                "Hohe Wahrscheinlichkeit / Hoher Impact",
                "Hohe Wahrscheinlichkeit / Niedriger Impact",
                "Niedrige Wahrscheinlichkeit / Hoher Impact",
                "Niedrige Wahrscheinlichkeit / Niedriger Impact"
            ],
            "prozess": [
                "Input",
                "Verarbeitung",
                "Output"
            ],
            "kommunikation": [
                "Was (Inhalt)",
                "Wer (Zielgruppe)",
                "Wie (Kanal)",
                "Wann (Timing)"
            ]
        }

    def create_mece_breakdown(self, problem: str,
                               categories: List[str],
                               elements_per_category: Dict[str, List[str]] = None) -> MECEAnalysis:
        """
        Erstellt eine MECE-Zerlegung eines Problems.

        Args:
            problem: Das zu analysierende Problem
            categories: Die MECE-Kategorien
            elements_per_category: Optionale Elemente pro Kategorie

        Returns:
            MECEAnalysis mit Status und Validierung
        """
        elements_per_category = elements_per_category or {}

        mece_categories = []
        for cat_name in categories:
            category = MECECategory(
                name=cat_name,
                description=f"Kategorie: {cat_name}",
                elements=elements_per_category.get(cat_name, [])
            )
            mece_categories.append(category)

        # Validiere MECE-Eigenschaften
        overlaps = self._find_overlaps(mece_categories)
        gaps = self._find_gaps(problem, mece_categories)

        if overlaps and gaps:
            status = MECEStatus.BOTH_ISSUES
        elif overlaps:
            status = MECEStatus.OVERLAPPING
        elif gaps:
            status = MECEStatus.INCOMPLETE
        else:
            status = MECEStatus.VALID

        # Berechne Coverage
        total_elements = sum(len(cat.elements) for cat in mece_categories)
        coverage = min(1.0, total_elements / max(1, len(categories) * 3))

        analysis = MECEAnalysis(
            problem=problem,
            categories=mece_categories,
            status=status,
            overlaps=overlaps,
            gaps=gaps,
            total_coverage=coverage
        )

        self.analyses.append(analysis)
        return analysis

    def suggest_framework(self, problem: str) -> Tuple[str, List[str]]:
        """
        Schlägt ein passendes MECE-Framework für ein Problem vor.
        """
        problem_lower = problem.lower()

        # Keyword-basierte Vorschläge
        if any(kw in problem_lower for kw in ["markt", "kunde", "segment"]):
            return "markt_segmentierung", self.common_frameworks["markt_segmentierung"]

        if any(kw in problem_lower for kw in ["umsatz", "einnahmen", "revenue"]):
            return "umsatz", self.common_frameworks["umsatz"]

        if any(kw in problem_lower for kw in ["kosten", "ausgaben", "expense"]):
            return "kosten", self.common_frameworks["kosten"]

        if any(kw in problem_lower for kw in ["profit", "gewinn", "rentabilität"]):
            return "profitabilität", self.common_frameworks["profitabilität"]

        if any(kw in problem_lower for kw in ["wettbewerb", "konkurrenz", "strategie"]):
            return "3c", self.common_frameworks["3c"]

        if any(kw in problem_lower for kw in ["marketing", "werbung", "vertrieb"]):
            return "4p_marketing", self.common_frameworks["4p_marketing"]

        if any(kw in problem_lower for kw in ["risiko", "gefahr", "bedrohung"]):
            return "risiko", self.common_frameworks["risiko"]

        if any(kw in problem_lower for kw in ["stärke", "schwäche", "chance"]):
            return "swot", self.common_frameworks["swot"]

        if any(kw in problem_lower for kw in ["prozess", "ablauf", "workflow"]):
            return "prozess", self.common_frameworks["prozess"]

        # Default: Zeitlich
        return "zeitlich", self.common_frameworks["zeitlich"]

    def _find_overlaps(self, categories: List[MECECategory]) -> List[Tuple[str, str]]:
        """Findet überlappende Kategorien"""
        overlaps = []

        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                # Prüfe Element-Überlappung
                shared = set(cat1.elements).intersection(set(cat2.elements))
                if shared:
                    overlaps.append((cat1.name, cat2.name))

                # Prüfe semantische Ähnlichkeit (vereinfacht)
                cat1_words = set(cat1.name.lower().split())
                cat2_words = set(cat2.name.lower().split())
                if cat1_words.intersection(cat2_words):
                    # Könnte überlappen
                    pass

        return overlaps

    def _find_gaps(self, problem: str, categories: List[MECECategory]) -> List[str]:
        """Findet potentielle Lücken in der Abdeckung"""
        gaps = []

        # Heuristische Gap-Erkennung
        problem_words = set(problem.lower().split())
        covered_words = set()

        for cat in categories:
            covered_words.update(cat.name.lower().split())
            for elem in cat.elements:
                covered_words.update(elem.lower().split())

        # Wichtige Wörter die nicht abgedeckt sind
        important_uncovered = problem_words - covered_words - {
            "wie", "was", "warum", "wer", "wann", "wo", "der", "die", "das",
            "ein", "eine", "ist", "sind", "wird", "werden", "hat", "haben"
        }

        if important_uncovered:
            gaps.append(f"Möglicherweise nicht abgedeckt: {', '.join(list(important_uncovered)[:5])}")

        return gaps

    def refine_categories(self, analysis: MECEAnalysis,
                          category_name: str,
                          subcategories: List[str]) -> MECEAnalysis:
        """
        Verfeinert eine Kategorie durch Unterkategorien (auch MECE).
        """
        for cat in analysis.categories:
            if cat.name == category_name:
                for subcat_name in subcategories:
                    subcat = MECECategory(
                        name=subcat_name,
                        description=f"Unterkategorie von {category_name}",
                        parent=category_name
                    )
                    cat.subcategories.append(subcat)
                break

        return analysis

    def validate_mece(self, categories: List[str]) -> Dict[str, Any]:
        """
        Validiert ob gegebene Kategorien MECE-konform sind.
        """
        result = {
            "is_mece": True,
            "mutually_exclusive": True,
            "collectively_exhaustive": True,
            "issues": []
        }

        # Prüfe auf offensichtliche Überlappungen
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                cat1_lower = cat1.lower()
                cat2_lower = cat2.lower()

                # Substring-Check
                if cat1_lower in cat2_lower or cat2_lower in cat1_lower:
                    result["mutually_exclusive"] = False
                    result["issues"].append(f"'{cat1}' und '{cat2}' könnten überlappen")

        # Prüfe auf offensichtliche Lücken (heuristisch)
        if len(categories) < 2:
            result["collectively_exhaustive"] = False
            result["issues"].append("Zu wenige Kategorien für vollständige Abdeckung")

        result["is_mece"] = result["mutually_exclusive"] and result["collectively_exhaustive"]
        return result

    def get_mece_summary(self, analysis: MECEAnalysis) -> str:
        """Generiert eine Zusammenfassung der MECE-Analyse"""
        summary = [f"=== MECE-Analyse: {analysis.problem} ===\n"]

        summary.append(f"Status: {analysis.status.value}")
        summary.append(f"Coverage: {analysis.total_coverage*100:.1f}%\n")

        summary.append("Kategorien:")
        for cat in analysis.categories:
            summary.append(f"  📁 {cat.name}")
            if cat.elements:
                for elem in cat.elements[:3]:
                    summary.append(f"      • {elem}")
                if len(cat.elements) > 3:
                    summary.append(f"      ... und {len(cat.elements)-3} weitere")
            if cat.subcategories:
                for subcat in cat.subcategories:
                    summary.append(f"      └─ {subcat.name}")

        if analysis.overlaps:
            summary.append(f"\n⚠️ Überlappungen: {analysis.overlaps}")

        if analysis.gaps:
            summary.append(f"\n⚠️ Lücken: {analysis.gaps}")

        return "\n".join(summary)


# =============================================================================
# 2. ROOT CAUSE ANALYSIS - Ursachenforschung
# =============================================================================

class RootCauseAnalyzer:
    """
    Root Cause Analysis Framework.

    Methoden:
    - 5-Why: Iteratives "Warum?" fragen
    - Ishikawa: Fishbone/Fischgräten-Diagramm
    - Fault Tree: Fehlerbaum-Analyse
    - Pareto: 80/20-Analyse
    """

    def __init__(self):
        self.analyses: List[RootCauseResult] = []
        self.cause_database: Dict[str, List[str]] = defaultdict(list)

    # -------------------------------------------------------------------------
    # 5-WHY ANALYSIS
    # -------------------------------------------------------------------------

    def five_why_analysis(self, problem: str,
                          answers: List[str] = None,
                          max_depth: int = 5) -> WhyNode:
        """
        Führt eine 5-Why-Analyse durch.

        Args:
            problem: Das Ausgangsproblem
            answers: Optionale vorgegebene Antworten
            max_depth: Maximale Tiefe der Analyse

        Returns:
            Wurzelknoten des Why-Baums
        """
        answers = answers or []

        root = WhyNode(
            question=f"Warum tritt '{problem}' auf?",
            answer=answers[0] if answers else "Ursache unbekannt",
            level=1
        )

        current_node = root
        for i in range(1, max_depth):
            if i < len(answers):
                answer = answers[i]
            else:
                # Generiere Folgefrage basierend auf vorheriger Antwort
                answer = f"Tiefere Ursache für '{current_node.answer}' noch zu ermitteln"

            child = WhyNode(
                question=f"Warum {current_node.answer.lower()}?",
                answer=answer,
                level=i + 1,
                is_root_cause=(i == max_depth - 1)
            )
            current_node.children.append(child)
            current_node = child

        return root

    def get_five_why_path(self, root: WhyNode) -> List[Tuple[str, str]]:
        """Extrahiert den Pfad der 5-Why-Analyse"""
        path = []
        current = root

        while current:
            path.append((current.question, current.answer))
            if current.children:
                current = current.children[0]
            else:
                current = None

        return path

    # -------------------------------------------------------------------------
    # ISHIKAWA ANALYSIS (Fishbone Diagram)
    # -------------------------------------------------------------------------

    def ishikawa_analysis(self, problem: str,
                          causes_by_category: Dict[IshikawaCategory, List[str]] = None) -> Dict[str, Any]:
        """
        Erstellt eine Ishikawa (Fishbone) Analyse.

        Die 6M-Kategorien:
        - Mensch: Menschliche Faktoren
        - Maschine: Technische Faktoren
        - Material: Materialfaktoren
        - Methode: Prozessfaktoren
        - Messung: Messfaktoren
        - Milieu: Umweltfaktoren
        """
        causes_by_category = causes_by_category or {}

        # Initialisiere alle Kategorien
        fishbone = {
            "problem": problem,
            "categories": {}
        }

        for category in IshikawaCategory:
            causes = causes_by_category.get(category, [])
            fishbone["categories"][category.value] = {
                "name": category.value.capitalize(),
                "causes": [
                    IshikawaCause(
                        category=category,
                        cause=cause,
                        probability=0.5
                    ) for cause in causes
                ]
            }

        # Generiere Standardvorschläge wenn leer
        if not causes_by_category:
            fishbone["categories"][IshikawaCategory.MENSCH.value]["causes"] = [
                IshikawaCause(IshikawaCategory.MENSCH, "Mangelnde Schulung"),
                IshikawaCause(IshikawaCategory.MENSCH, "Kommunikationsprobleme"),
                IshikawaCause(IshikawaCategory.MENSCH, "Überlastung")
            ]
            fishbone["categories"][IshikawaCategory.MASCHINE.value]["causes"] = [
                IshikawaCause(IshikawaCategory.MASCHINE, "Veraltete Ausrüstung"),
                IshikawaCause(IshikawaCategory.MASCHINE, "Fehlende Wartung"),
                IshikawaCause(IshikawaCategory.MASCHINE, "Software-Bugs")
            ]
            fishbone["categories"][IshikawaCategory.METHODE.value]["causes"] = [
                IshikawaCause(IshikawaCategory.METHODE, "Unklare Prozesse"),
                IshikawaCause(IshikawaCategory.METHODE, "Fehlende Standards"),
                IshikawaCause(IshikawaCategory.METHODE, "Ineffiziente Abläufe")
            ]

        return fishbone

    def rate_ishikawa_causes(self, fishbone: Dict,
                              ratings: Dict[str, float]) -> Dict[str, Any]:
        """
        Bewertet Ishikawa-Ursachen nach Wahrscheinlichkeit.
        """
        for cat_name, cat_data in fishbone["categories"].items():
            for cause in cat_data["causes"]:
                if cause.cause in ratings:
                    cause.probability = ratings[cause.cause]

        # Sortiere nach Wahrscheinlichkeit
        for cat_name, cat_data in fishbone["categories"].items():
            cat_data["causes"].sort(key=lambda c: c.probability, reverse=True)

        return fishbone

    def get_top_causes(self, fishbone: Dict, n: int = 5) -> List[IshikawaCause]:
        """Gibt die n wahrscheinlichsten Ursachen zurück"""
        all_causes = []
        for cat_data in fishbone["categories"].values():
            all_causes.extend(cat_data["causes"])

        return sorted(all_causes, key=lambda c: c.probability, reverse=True)[:n]

    # -------------------------------------------------------------------------
    # FAULT TREE ANALYSIS
    # -------------------------------------------------------------------------

    def create_fault_tree(self, top_event: str,
                          structure: Dict[str, Any] = None) -> FaultTreeNode:
        """
        Erstellt einen Fehlerbaum.

        Struktur-Format:
        {
            "event": "Top Event",
            "gate": "OR",
            "children": [
                {"event": "Sub-Event 1", "basic": True, "probability": 0.1},
                {"event": "Sub-Event 2", "gate": "AND", "children": [...]}
            ]
        }
        """
        if structure is None:
            # Default: Einfacher OR-Baum
            return FaultTreeNode(
                event=top_event,
                gate_type="OR",
                children=[
                    FaultTreeNode(event="Ursache A", is_basic_event=True, probability=0.1),
                    FaultTreeNode(event="Ursache B", is_basic_event=True, probability=0.1),
                    FaultTreeNode(event="Ursache C", is_basic_event=True, probability=0.1)
                ]
            )

        return self._build_fault_tree(structure)

    def _build_fault_tree(self, structure: Dict) -> FaultTreeNode:
        """Rekursiver Aufbau des Fehlerbaums"""
        node = FaultTreeNode(
            event=structure.get("event", "Unknown"),
            is_basic_event=structure.get("basic", False),
            gate_type=structure.get("gate", "OR"),
            probability=structure.get("probability", 0.0)
        )

        if "children" in structure:
            for child_struct in structure["children"]:
                child_node = self._build_fault_tree(child_struct)
                node.children.append(child_node)

        return node

    def calculate_fault_tree_probability(self, root: FaultTreeNode) -> float:
        """
        Berechnet die Wahrscheinlichkeit des Top-Events.

        OR-Gate: P = 1 - ∏(1 - P_i)
        AND-Gate: P = ∏P_i
        """
        if root.is_basic_event:
            return root.probability

        child_probs = [
            self.calculate_fault_tree_probability(child)
            for child in root.children
        ]

        if not child_probs:
            return 0.0

        if root.gate_type == "AND":
            # AND: Alle müssen eintreten
            result = 1.0
            for p in child_probs:
                result *= p
            return result
        else:
            # OR: Mindestens eines muss eintreten
            result = 1.0
            for p in child_probs:
                result *= (1 - p)
            return 1 - result

    def find_minimal_cut_sets(self, root: FaultTreeNode) -> List[Set[str]]:
        """
        Findet minimale Schnittmengen (Minimal Cut Sets).
        Das sind die kleinsten Kombinationen von Basisereignissen,
        die zum Top-Event führen.
        """
        if root.is_basic_event:
            return [{root.event}]

        child_cut_sets = [
            self.find_minimal_cut_sets(child)
            for child in root.children
        ]

        if root.gate_type == "AND":
            # AND: Kombiniere alle Cut Sets
            if not child_cut_sets:
                return []
            result = child_cut_sets[0]
            for other_sets in child_cut_sets[1:]:
                new_result = []
                for set1 in result:
                    for set2 in other_sets:
                        new_result.append(set1.union(set2))
                result = new_result
            return result
        else:
            # OR: Vereinige alle Cut Sets
            result = []
            for cut_sets in child_cut_sets:
                result.extend(cut_sets)
            return result

    # -------------------------------------------------------------------------
    # PARETO ANALYSIS
    # -------------------------------------------------------------------------

    def pareto_analysis(self, causes: Dict[str, float]) -> Dict[str, Any]:
        """
        Führt eine Pareto-Analyse (80/20) durch.

        Args:
            causes: Dict von Ursache -> Häufigkeit/Impact

        Returns:
            Pareto-Analyse mit vital few und trivial many
        """
        total = sum(causes.values())
        sorted_causes = sorted(causes.items(), key=lambda x: x[1], reverse=True)

        cumulative = 0
        vital_few = []
        trivial_many = []
        threshold = 0.8 * total

        for cause, value in sorted_causes:
            cumulative += value
            percentage = value / total if total > 0 else 0
            cumulative_pct = cumulative / total if total > 0 else 0

            entry = {
                "cause": cause,
                "value": value,
                "percentage": percentage,
                "cumulative_percentage": cumulative_pct
            }

            if cumulative <= threshold or not vital_few:
                vital_few.append(entry)
            else:
                trivial_many.append(entry)

        return {
            "total": total,
            "vital_few": vital_few,
            "trivial_many": trivial_many,
            "vital_few_count": len(vital_few),
            "vital_few_percentage": len(vital_few) / len(causes) if causes else 0,
            "recommendation": f"Fokussiere auf die Top {len(vital_few)} Ursachen "
                            f"({len(vital_few)/len(causes)*100:.0f}% der Ursachen, "
                            f"~80% des Impacts)"
        }

    # -------------------------------------------------------------------------
    # COMBINED ANALYSIS
    # -------------------------------------------------------------------------

    def full_root_cause_analysis(self, problem: str,
                                   known_causes: List[str] = None,
                                   cause_frequencies: Dict[str, float] = None) -> RootCauseResult:
        """
        Führt eine vollständige Root Cause Analysis mit allen Methoden durch.
        """
        known_causes = known_causes or []
        cause_frequencies = cause_frequencies or {}

        # 5-Why
        five_why = self.five_why_analysis(problem, known_causes[:5])
        why_path = self.get_five_why_path(five_why)

        # Ishikawa
        ishikawa = self.ishikawa_analysis(problem)
        top_ishikawa = self.get_top_causes(ishikawa, 3)

        # Pareto (wenn Frequenzen vorhanden)
        pareto_result = None
        if cause_frequencies:
            pareto_result = self.pareto_analysis(cause_frequencies)

        # Identifiziere Root Causes
        root_causes = []
        if why_path:
            root_causes.append(why_path[-1][1])  # Letzte Antwort der 5-Why

        if top_ishikawa:
            root_causes.extend([c.cause for c in top_ishikawa[:2]])

        # Empfehlungen
        recommendations = [
            f"Adressiere primär: {root_causes[0]}" if root_causes else "Weitere Analyse nötig",
            "Implementiere Präventivmaßnahmen",
            "Etabliere Monitoring für Frühwarnung"
        ]

        result = RootCauseResult(
            problem=problem,
            method=RootCauseMethod.COMBINED,
            identified_causes=known_causes + [c.cause for c in top_ishikawa],
            root_causes=list(set(root_causes)),
            evidence={"5_why_path": [f"{q}: {a}" for q, a in why_path]},
            recommended_actions=recommendations,
            confidence=0.7 if root_causes else 0.3
        )

        self.analyses.append(result)
        return result

    def get_rca_summary(self, result: RootCauseResult) -> str:
        """Generiert eine Zusammenfassung der Root Cause Analysis"""
        summary = [f"=== Root Cause Analysis: {result.problem} ===\n"]

        summary.append(f"Methode: {result.method.value}")
        summary.append(f"Konfidenz: {result.confidence*100:.0f}%\n")

        summary.append("Identifizierte Ursachen:")
        for cause in result.identified_causes[:5]:
            summary.append(f"  • {cause}")

        summary.append("\n🎯 Root Causes:")
        for rc in result.root_causes:
            summary.append(f"  ★ {rc}")

        summary.append("\n📋 Empfohlene Maßnahmen:")
        for action in result.recommended_actions:
            summary.append(f"  → {action}")

        return "\n".join(summary)


# =============================================================================
# 3. MORPHOLOGICAL ANALYSIS - Kombinatorische Lösungsfindung
# =============================================================================

class MorphologicalAnalyzer:
    """
    Morphologische Analyse (Zwicky Box).

    Systematische Methode zur Lösungsfindung durch:
    1. Identifikation der relevanten Dimensionen/Parameter
    2. Auflistung aller möglichen Ausprägungen je Parameter
    3. Systematische Kombination zu Lösungsalternativen
    """

    def __init__(self):
        self.analyses: Dict[str, List[MorphologicalParameter]] = {}
        self.generated_solutions: List[MorphologicalSolution] = []

    def create_morphological_box(self, problem: str,
                                   parameters: List[MorphologicalParameter]) -> Dict[str, Any]:
        """
        Erstellt eine morphologische Box für ein Problem.
        """
        self.analyses[problem] = parameters

        # Berechne Lösungsraum
        total_combinations = 1
        for param in parameters:
            total_combinations *= len(param.options)

        return {
            "problem": problem,
            "parameters": parameters,
            "parameter_count": len(parameters),
            "total_combinations": total_combinations,
            "matrix": self._create_matrix(parameters)
        }

    def _create_matrix(self, parameters: List[MorphologicalParameter]) -> Dict[str, List[str]]:
        """Erstellt die Morphologie-Matrix"""
        return {param.name: param.options for param in parameters}

    def generate_all_solutions(self, problem: str,
                                 max_solutions: int = 100) -> List[MorphologicalSolution]:
        """
        Generiert alle möglichen Lösungen aus der morphologischen Box.
        """
        if problem not in self.analyses:
            return []

        parameters = self.analyses[problem]

        # Generiere alle Kombinationen
        param_names = [p.name for p in parameters]
        param_options = [p.options for p in parameters]

        all_combinations = list(itertools.product(*param_options))

        # Limitiere auf max_solutions
        if len(all_combinations) > max_solutions:
            all_combinations = random.sample(all_combinations, max_solutions)

        solutions = []
        for combo in all_combinations:
            param_dict = dict(zip(param_names, combo))
            solution = MorphologicalSolution(
                parameters=param_dict,
                feasibility_score=self._estimate_feasibility(param_dict),
                novelty_score=self._estimate_novelty(param_dict, solutions),
                description=self._generate_solution_description(param_dict)
            )
            solutions.append(solution)

        self.generated_solutions.extend(solutions)
        return solutions

    def generate_targeted_solutions(self, problem: str,
                                      constraints: Dict[str, List[str]] = None,
                                      n_solutions: int = 10) -> List[MorphologicalSolution]:
        """
        Generiert Lösungen unter Berücksichtigung von Constraints.

        Args:
            problem: Das Problem
            constraints: Dict von Parameter -> erlaubte Werte
            n_solutions: Anzahl gewünschter Lösungen
        """
        if problem not in self.analyses:
            return []

        constraints = constraints or {}
        parameters = self.analyses[problem]

        # Filtere Parameter-Optionen basierend auf Constraints
        filtered_options = []
        param_names = []

        for param in parameters:
            param_names.append(param.name)
            if param.name in constraints:
                # Nur erlaubte Optionen
                allowed = [opt for opt in param.options if opt in constraints[param.name]]
                filtered_options.append(allowed if allowed else param.options)
            else:
                filtered_options.append(param.options)

        # Generiere Kombinationen
        all_combinations = list(itertools.product(*filtered_options))

        # Wähle beste Lösungen
        solutions = []
        for combo in all_combinations[:n_solutions * 2]:
            param_dict = dict(zip(param_names, combo))
            feasibility = self._estimate_feasibility(param_dict)

            if feasibility > 0.3:  # Mindest-Feasibility
                solution = MorphologicalSolution(
                    parameters=param_dict,
                    feasibility_score=feasibility,
                    novelty_score=self._estimate_novelty(param_dict, solutions),
                    description=self._generate_solution_description(param_dict)
                )
                solutions.append(solution)

            if len(solutions) >= n_solutions:
                break

        return sorted(solutions, key=lambda s: s.feasibility_score, reverse=True)

    def _estimate_feasibility(self, params: Dict[str, str]) -> float:
        """
        Schätzt die Machbarkeit einer Lösung.
        Basiert auf heuristischen Regeln.
        """
        score = 0.5  # Basis-Score

        # Heuristische Anpassungen
        param_values = list(params.values())

        # Längere/komplexere Optionen = niedrigere Feasibility
        avg_length = sum(len(v) for v in param_values) / len(param_values)
        if avg_length > 30:
            score -= 0.1

        # Mehr einzigartige Wörter = höhere Komplexität
        all_words = " ".join(param_values).lower().split()
        unique_ratio = len(set(all_words)) / len(all_words) if all_words else 0
        score += unique_ratio * 0.2

        return max(0.1, min(1.0, score))

    def _estimate_novelty(self, params: Dict[str, str],
                          existing_solutions: List[MorphologicalSolution]) -> float:
        """Schätzt die Neuartigkeit einer Lösung"""
        if not existing_solutions:
            return 0.8  # Erste Lösung ist relativ neu

        # Vergleiche mit existierenden Lösungen
        param_set = set(params.values())
        max_overlap = 0

        for sol in existing_solutions:
            existing_set = set(sol.parameters.values())
            overlap = len(param_set.intersection(existing_set)) / len(param_set)
            max_overlap = max(max_overlap, overlap)

        return 1.0 - max_overlap

    def _generate_solution_description(self, params: Dict[str, str]) -> str:
        """Generiert eine Beschreibung für eine Lösung"""
        parts = [f"{k}: {v}" for k, v in params.items()]
        return " | ".join(parts)

    def rank_solutions(self, solutions: List[MorphologicalSolution],
                        weights: Dict[str, float] = None) -> List[MorphologicalSolution]:
        """
        Rankt Lösungen nach gewichteten Kriterien.

        weights: {"feasibility": 0.6, "novelty": 0.4}
        """
        weights = weights or {"feasibility": 0.6, "novelty": 0.4}

        for solution in solutions:
            score = (
                solution.feasibility_score * weights.get("feasibility", 0.5) +
                solution.novelty_score * weights.get("novelty", 0.5)
            )
            solution.feasibility_score = score  # Überschreibe mit Gesamtscore

        return sorted(solutions, key=lambda s: s.feasibility_score, reverse=True)

    def cross_consistency_analysis(self, problem: str,
                                     incompatibilities: List[Tuple[Tuple[str, str], Tuple[str, str]]]) -> Dict[str, Any]:
        """
        Führt eine Cross-Consistency-Analyse durch.

        Identifiziert inkonsistente Parameterkombinationen.

        Args:
            incompatibilities: Liste von inkompatiblen Paaren
                [((param1, value1), (param2, value2)), ...]
        """
        if problem not in self.analyses:
            return {"error": "Problem nicht gefunden"}

        parameters = self.analyses[problem]
        total_pairs = 0
        incompatible_pairs = len(incompatibilities)

        # Zähle alle möglichen Paare
        for i, p1 in enumerate(parameters):
            for p2 in parameters[i+1:]:
                total_pairs += len(p1.options) * len(p2.options)

        consistency_ratio = 1 - (incompatible_pairs / max(1, total_pairs))

        return {
            "problem": problem,
            "total_parameter_pairs": total_pairs,
            "incompatible_pairs": incompatible_pairs,
            "consistency_ratio": consistency_ratio,
            "incompatibilities": incompatibilities,
            "recommendation": (
                "Hohe Konsistenz - viele Lösungen möglich"
                if consistency_ratio > 0.8
                else "Mittlere Konsistenz - einige Einschränkungen"
                if consistency_ratio > 0.5
                else "Niedrige Konsistenz - starke Einschränkungen beachten"
            )
        }

    def get_morphological_summary(self, problem: str) -> str:
        """Generiert eine Zusammenfassung der morphologischen Analyse"""
        if problem not in self.analyses:
            return f"Keine Analyse für '{problem}' gefunden."

        parameters = self.analyses[problem]
        summary = [f"=== Morphologische Analyse: {problem} ===\n"]

        total_combinations = 1
        for param in parameters:
            total_combinations *= len(param.options)
            summary.append(f"📊 {param.name} ({param.dimension.value}):")
            for opt in param.options:
                summary.append(f"    • {opt}")

        summary.append(f"\n🔢 Gesamter Lösungsraum: {total_combinations:,} Kombinationen")

        # Generierte Lösungen
        relevant_solutions = [
            s for s in self.generated_solutions
            if any(k in problem.lower() for k in s.parameters.keys())
        ]

        if relevant_solutions:
            summary.append(f"\n✨ Top Lösungen ({len(relevant_solutions)} generiert):")
            for sol in sorted(relevant_solutions,
                            key=lambda x: x.feasibility_score,
                            reverse=True)[:3]:
                summary.append(f"    [{sol.feasibility_score:.2f}] {sol.description[:80]}...")

        return "\n".join(summary)


# =============================================================================
# KOMBINIERTER ANALYTICAL STRATEGY ENGINE
# =============================================================================

class AnalyticalStrategyEngine:
    """
    Kombiniert alle analytischen Strategien zu einem integrierten System.
    """

    def __init__(self):
        self.mece = MECEAnalyzer()
        self.rca = RootCauseAnalyzer()
        self.morphological = MorphologicalAnalyzer()
        self.analysis_log: List[Dict] = []

    def analyze_problem(self, problem: str,
                         strategy: AnalysisType = AnalysisType.COMBINED) -> Dict[str, Any]:
        """
        Analysiert ein Problem mit der gewählten Strategie.
        """
        results = {
            "problem": problem,
            "strategy": strategy.value,
            "timestamp": datetime.now().isoformat(),
            "analyses": {}
        }

        if strategy in [AnalysisType.MECE, AnalysisType.COMBINED]:
            # MECE-Analyse
            framework_name, categories = self.mece.suggest_framework(problem)
            mece_result = self.mece.create_mece_breakdown(problem, categories)
            results["analyses"]["mece"] = {
                "framework": framework_name,
                "status": mece_result.status.value,
                "categories": [c.name for c in mece_result.categories],
                "coverage": mece_result.total_coverage
            }

        if strategy in [AnalysisType.ROOT_CAUSE, AnalysisType.COMBINED]:
            # Root Cause Analysis
            rca_result = self.rca.full_root_cause_analysis(problem)
            results["analyses"]["root_cause"] = {
                "method": rca_result.method.value,
                "root_causes": rca_result.root_causes,
                "recommendations": rca_result.recommended_actions,
                "confidence": rca_result.confidence
            }

        if strategy in [AnalysisType.MORPHOLOGICAL, AnalysisType.COMBINED]:
            # Morphologische Analyse (mit Standardparametern)
            default_params = [
                MorphologicalParameter(
                    name="Ansatz",
                    dimension=MorphologicalDimension.FUNCTION,
                    options=["Präventiv", "Reaktiv", "Adaptiv"]
                ),
                MorphologicalParameter(
                    name="Ressourcen",
                    dimension=MorphologicalDimension.RESOURCE,
                    options=["Minimal", "Moderat", "Umfangreich"]
                ),
                MorphologicalParameter(
                    name="Zeitrahmen",
                    dimension=MorphologicalDimension.CONSTRAINT,
                    options=["Kurzfristig", "Mittelfristig", "Langfristig"]
                )
            ]
            morph_box = self.morphological.create_morphological_box(problem, default_params)
            solutions = self.morphological.generate_targeted_solutions(problem, n_solutions=5)

            results["analyses"]["morphological"] = {
                "parameters": len(morph_box["parameters"]),
                "total_combinations": morph_box["total_combinations"],
                "top_solutions": [
                    {"params": s.parameters, "score": s.feasibility_score}
                    for s in solutions[:3]
                ]
            }

        self.analysis_log.append(results)
        return results

    def get_strategy_summary(self) -> str:
        """Gibt eine Zusammenfassung aller Analysen"""
        summary = ["=" * 60]
        summary.append("ANALYTICAL STRATEGY ENGINE - Zusammenfassung")
        summary.append("=" * 60)

        summary.append(f"\nDurchgeführte Analysen: {len(self.analysis_log)}")

        # MECE Stats
        mece_analyses = len(self.mece.analyses)
        summary.append(f"\n--- MECE Analyzer ---")
        summary.append(f"Analysen: {mece_analyses}")

        # RCA Stats
        rca_analyses = len(self.rca.analyses)
        summary.append(f"\n--- Root Cause Analyzer ---")
        summary.append(f"Analysen: {rca_analyses}")

        # Morphological Stats
        morph_problems = len(self.morphological.analyses)
        morph_solutions = len(self.morphological.generated_solutions)
        summary.append(f"\n--- Morphological Analyzer ---")
        summary.append(f"Probleme analysiert: {morph_problems}")
        summary.append(f"Lösungen generiert: {morph_solutions}")

        return "\n".join(summary)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_analytical_engine() -> AnalyticalStrategyEngine:
    """Erstellt eine Analytical Strategy Engine"""
    return AnalyticalStrategyEngine()


# =============================================================================
# BEISPIEL / TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("📊 Analytical Strategies Engine - Demo\n")

    engine = create_analytical_engine()

    # Test MECE
    print("--- MECE Analyse ---")
    mece_result = engine.mece.create_mece_breakdown(
        "Wie können wir den Umsatz steigern?",
        ["Preis erhöhen", "Menge erhöhen"],
        {
            "Preis erhöhen": ["Premium-Positionierung", "Weniger Rabatte"],
            "Menge erhöhen": ["Neue Kunden", "Mehr pro Kunde", "Neue Märkte"]
        }
    )
    print(engine.mece.get_mece_summary(mece_result))

    # Test Root Cause Analysis
    print("\n--- Root Cause Analysis ---")
    rca_result = engine.rca.full_root_cause_analysis(
        "Kundenbeschwerden haben zugenommen",
        ["Lange Wartezeiten", "Qualitätsmängel", "Kommunikationsprobleme"]
    )
    print(engine.rca.get_rca_summary(rca_result))

    # Test Morphological Analysis
    print("\n--- Morphologische Analyse ---")
    params = [
        MorphologicalParameter("Zielgruppe", MorphologicalDimension.INTERFACE,
                              ["B2B", "B2C", "B2B2C"]),
        MorphologicalParameter("Preismodell", MorphologicalDimension.FUNCTION,
                              ["Einmalkauf", "Abo", "Freemium", "Pay-per-Use"]),
        MorphologicalParameter("Vertriebskanal", MorphologicalDimension.PROCESS,
                              ["Online", "Einzelhandel", "Direktvertrieb"])
    ]
    engine.morphological.create_morphological_box("Neues Produkt launchen", params)
    solutions = engine.morphological.generate_targeted_solutions(
        "Neues Produkt launchen",
        constraints={"Zielgruppe": ["B2C", "B2B2C"]},
        n_solutions=5
    )
    print(f"\nTop Lösungen für Produkt-Launch:")
    for sol in solutions[:3]:
        print(f"  [{sol.feasibility_score:.2f}] {sol.description}")

    # Kombinierte Analyse
    print("\n--- Kombinierte Analyse ---")
    combined = engine.analyze_problem("Mitarbeiterfluktuation reduzieren")
    print(f"Ergebnis-Keys: {combined['analyses'].keys()}")

    # Zusammenfassung
    print("\n" + engine.get_strategy_summary())
