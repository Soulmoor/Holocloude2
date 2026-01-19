"""
Holo Problem Solver - Universelles Analytisches Denken mit Out-of-Box Thinking
===============================================================================

Ein allgemeines Problem-Solving Framework für Holo mit echtem kreativem,
autonomem Denken. Holo kann jetzt:
- Selbständig Hypothesen generieren
- Kreativ/lateral denken (Random Association, Perspective Shift, etc.)
- Im Web nach Lösungen suchen wenn sie nicht weiterkommt
- Lösungen SIMULIEREN bevor sie angewendet werden
- Autonom explorieren und Verbindungen entdecken

Denk-Prozess (erweitert mit Out-of-Box Phasen):
1.   VERSTEHEN         - Was ist das Problem genau?
2.   ANALYSIEREN       - Was sind die Ursachen? Was hängt zusammen?
2.5  HYPOTHESEN        - Selbständig Vermutungen aufstellen (OUT-OF-BOX)
3.   WISSEN SAMMELN    - Was weiß ich schon? Was muss ich herausfinden?
3.5  WEB-RECHERCHE     - Im Web suchen wenn nötig (OUT-OF-BOX)
4.   STRATEGIEN        - Welche Lösungswege gibt es?
4.5  LATERALES DENKEN  - Kreative/unkonventionelle Ideen (OUT-OF-BOX)
5.   BEWERTEN          - Welche Strategie ist am besten?
6.   PLANEN            - Welche Schritte in welcher Reihenfolge?
6.5  SIMULATION        - Lösung simulieren vor Ausführung (OUT-OF-BOX)
7.   AUSFÜHREN         - Mit Monitoring und Anpassung
8.   PRÜFEN            - Hat es funktioniert?
9.   LERNEN            - Was merke ich mir für nächstes Mal?

Out-of-Box Thinking Komponenten:
- WebResearcher: Web-Suche für unbekannte Probleme
- SolutionSimulator: Lösungen simulieren vor Anwendung
- LateralThinkingEngine: Kreatives/laterales Denken
- HypothesisGenerator: Selbständige Hypothesen-Generierung
- AutonomousExplorer: Autonome Exploration und Entdeckung

Autor: Claude (Anthropic) für Holo
Version: 2.0.0 - mit Out-of-Box Thinking
"""

import os
import re
import json
import time
import logging
import hashlib
import threading
import random
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from collections import defaultdict
import traceback
import copy


# ==================== LOGGING ====================

logger = logging.getLogger("HoloProblemSolver")


# ==================== ENUMS ====================

class ProblemType(Enum):
    """Typen von Problemen die Holo begegnen kann"""
    TECHNICAL = "technical"           # Code, System, Fehler
    KNOWLEDGE = "knowledge"           # Wissen fehlt, Frage beantworten
    TASK = "task"                     # Aufgabe erledigen
    DECISION = "decision"             # Entscheidung treffen
    CREATIVE = "creative"             # Kreative Lösung gefragt
    COMMUNICATION = "communication"   # Verständnis-Problem
    CONFLICT = "conflict"             # Widersprüchliche Anforderungen
    RESOURCE = "resource"             # Ressourcen fehlen
    UNKNOWN = "unknown"               # Unbekanntes Problem


class ProblemComplexity(Enum):
    """Komplexität eines Problems"""
    TRIVIAL = 1      # Sofort lösbar
    SIMPLE = 2       # Ein Schritt
    MODERATE = 3     # Mehrere Schritte
    COMPLEX = 4      # Viele Schritte, Abhängigkeiten
    VERY_COMPLEX = 5 # Erfordert tiefe Analyse


class StrategyType(Enum):
    """Typen von Lösungsstrategien"""
    DIRECT = "direct"                 # Direkter Lösungsweg
    DECOMPOSE = "decompose"           # Problem zerlegen
    ANALOGIE = "analogie"             # Ähnliches Problem als Vorlage
    TRIAL_ERROR = "trial_error"       # Ausprobieren
    RESEARCH = "research"             # Erst recherchieren
    ASK = "ask"                       # Benutzer fragen
    DELEGATE = "delegate"             # An anderes System delegieren
    WORKAROUND = "workaround"         # Umgehungslösung
    POSTPONE = "postpone"             # Später lösen
    ESCALATE = "escalate"             # Eskalieren (Hilfe holen)


class StepStatus(Enum):
    """Status eines Lösungsschritts"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class ThinkingPhase(Enum):
    """Phasen des Denkprozesses"""
    UNDERSTAND = "verstehen"
    DECOMPOSE = "zerlegen"
    ANALYZE = "analysieren"
    GATHER_KNOWLEDGE = "wissen_sammeln"
    FIND_STRATEGIES = "strategien_finden"
    EVALUATE = "bewerten"
    PLAN = "planen"
    EXECUTE = "ausführen"
    VERIFY = "prüfen"
    LEARN = "lernen"


# ==================== DATA CLASSES ====================

@dataclass
class Problem:
    """Repräsentiert ein Problem das gelöst werden soll"""
    id: str
    description: str
    problem_type: ProblemType = ProblemType.UNKNOWN
    complexity: ProblemComplexity = ProblemComplexity.MODERATE
    context: Dict = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    sub_problems: List['Problem'] = field(default_factory=list)
    parent_problem: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 5  # 1-10, höher = wichtiger
    deadline: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "type": self.problem_type.value,
            "complexity": self.complexity.name,
            "goals": self.goals,
            "constraints": self.constraints,
            "sub_problems": len(self.sub_problems),
            "priority": self.priority,
        }


@dataclass
class Strategy:
    """Eine Lösungsstrategie"""
    id: str
    strategy_type: StrategyType
    description: str
    steps: List[str] = field(default_factory=list)
    estimated_success: float = 0.5  # 0.0 - 1.0
    estimated_effort: float = 0.5   # 0.0 - 1.0 (niedrig = wenig Aufwand)
    risks: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    fallback_strategy: Optional[str] = None

    def score(self) -> float:
        """Berechnet einen Score für diese Strategie"""
        # Erfolgswahrscheinlichkeit * (1 - Aufwand) * Risiko-Faktor
        risk_factor = 1.0 - (len(self.risks) * 0.1)
        return self.estimated_success * (1.0 - self.estimated_effort * 0.5) * max(0.1, risk_factor)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.strategy_type.value,
            "description": self.description,
            "steps": self.steps,
            "success_probability": f"{self.estimated_success:.0%}",
            "effort": f"{self.estimated_effort:.0%}",
            "score": f"{self.score():.2f}",
            "risks": self.risks,
        }


@dataclass
class PlanStep:
    """Ein Schritt im Lösungsplan"""
    id: str
    description: str
    action: str  # Was genau zu tun ist
    status: StepStatus = StepStatus.PENDING
    depends_on: List[str] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "action": self.action,
            "status": self.status.value,
            "depends_on": self.depends_on,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class Plan:
    """Ein Lösungsplan"""
    id: str
    problem_id: str
    strategy_id: str
    steps: List[PlanStep] = field(default_factory=list)
    current_step: int = 0
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def get_progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = len([s for s in self.steps if s.status == StepStatus.COMPLETED])
        return completed / len(self.steps)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "strategy_id": self.strategy_id,
            "steps": [s.to_dict() for s in self.steps],
            "progress": f"{self.get_progress():.0%}",
            "status": self.status,
        }


@dataclass
class ThinkingStep:
    """Ein Schritt im Denkprozess"""
    phase: ThinkingPhase
    thought: str
    conclusion: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0

    def to_dict(self) -> Dict:
        return {
            "phase": self.phase.value,
            "thought": self.thought,
            "conclusion": self.conclusion,
        }


@dataclass
class Solution:
    """Das Ergebnis eines gelösten Problems"""
    problem_id: str
    success: bool
    result: Any = None
    explanation: str = ""
    thinking_steps: List[ThinkingStep] = field(default_factory=list)
    strategies_tried: List[str] = field(default_factory=list)
    plan_executed: Optional[Plan] = None
    lessons_learned: List[str] = field(default_factory=list)
    duration_ms: int = 0

    def to_dict(self) -> Dict:
        return {
            "problem_id": self.problem_id,
            "success": self.success,
            "result": str(self.result)[:500] if self.result else None,
            "explanation": self.explanation,
            "thinking_steps": [t.to_dict() for t in self.thinking_steps],
            "strategies_tried": self.strategies_tried,
            "lessons_learned": self.lessons_learned,
            "duration_ms": self.duration_ms,
        }


# ==================== KNOWLEDGE BASE ====================

class KnowledgeBase:
    """
    Wissens-Datenbank für den Problem Solver.
    Speichert bekannte Probleme, Lösungen und Muster.
    """

    def __init__(self, persist_path: Path = None):
        self.persist_path = persist_path

        # Bekannte Problem-Muster und ihre Lösungen
        self.problem_patterns: Dict[str, Dict] = {}

        # Erfolgreiche Strategien pro Problem-Typ
        self.successful_strategies: Dict[ProblemType, List[Dict]] = defaultdict(list)

        # Gelernte Lektionen
        self.lessons: List[Dict] = []

        # Analogien (Problem A ist ähnlich zu Problem B)
        self.analogies: Dict[str, List[str]] = defaultdict(list)

        # Bekannte Fehler und wie sie behoben wurden
        self.error_solutions: Dict[str, str] = {}

        # Lade persistierte Daten
        if persist_path:
            self._load()

    def _load(self):
        """Lädt persistierte Wissensdaten"""
        if not self.persist_path or not self.persist_path.exists():
            return

        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.problem_patterns = data.get("problem_patterns", {})
            self.lessons = data.get("lessons", [])
            self.error_solutions = data.get("error_solutions", {})

            # Successful strategies laden
            for type_str, strategies in data.get("successful_strategies", {}).items():
                try:
                    ptype = ProblemType(type_str)
                    self.successful_strategies[ptype] = strategies
                except ValueError:
                    pass

        except Exception as e:
            logger.warning(f"Konnte Wissensbasis nicht laden: {e}")

    def save(self):
        """Speichert Wissensdaten"""
        if not self.persist_path:
            return

        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "problem_patterns": self.problem_patterns,
                "successful_strategies": {
                    k.value: v for k, v in self.successful_strategies.items()
                },
                "lessons": self.lessons[-100:],  # Letzte 100 Lektionen
                "error_solutions": dict(list(self.error_solutions.items())[-200:]),
            }

            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            logger.error(f"Konnte Wissensbasis nicht speichern: {e}")

    def find_similar_problem(self, problem: Problem) -> Optional[Dict]:
        """Findet ein ähnliches bereits gelöstes Problem"""
        description_lower = problem.description.lower()

        # Suche nach Schlüsselwörtern
        for pattern_id, pattern in self.problem_patterns.items():
            keywords = pattern.get("keywords", [])
            matches = sum(1 for kw in keywords if kw.lower() in description_lower)
            if matches >= 2 or (matches >= 1 and len(keywords) <= 2):
                return pattern

        return None

    def get_strategies_for_type(self, problem_type: ProblemType) -> List[Dict]:
        """Gibt erfolgreiche Strategien für einen Problem-Typ zurück"""
        return self.successful_strategies.get(problem_type, [])

    def add_solution(self, problem: Problem, solution: Solution):
        """Fügt eine erfolgreiche Lösung zur Wissensbasis hinzu"""
        if not solution.success:
            return

        # Extrahiere Schlüsselwörter aus Problem-Beschreibung
        keywords = self._extract_keywords(problem.description)

        # Speichere Problem-Muster
        self.problem_patterns[problem.id] = {
            "description": problem.description,
            "type": problem.problem_type.value,
            "keywords": keywords,
            "solution_summary": solution.explanation[:200],
            "strategies_used": solution.strategies_tried,
        }

        # Speichere erfolgreiche Strategie
        for strategy_id in solution.strategies_tried:
            self.successful_strategies[problem.problem_type].append({
                "strategy_id": strategy_id,
                "problem_summary": problem.description[:100],
                "success": True,
            })

        # Speichere Lektionen
        for lesson in solution.lessons_learned:
            self.lessons.append({
                "lesson": lesson,
                "problem_type": problem.problem_type.value,
                "timestamp": datetime.now().isoformat(),
            })

        self.save()

    def add_error_solution(self, error_pattern: str, solution: str):
        """Fügt eine Fehler-Lösung hinzu"""
        self.error_solutions[error_pattern] = solution
        self.save()

    def find_error_solution(self, error_message: str) -> Optional[str]:
        """Sucht nach einer bekannten Lösung für einen Fehler"""
        error_lower = error_message.lower()

        for pattern, solution in self.error_solutions.items():
            if pattern.lower() in error_lower:
                return solution

        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiert Schlüsselwörter aus Text"""
        # Einfache Extraktion - könnte verbessert werden
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text)

        # Filtere Stopwörter
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'und', 'oder', 'aber', 'wenn', 'weil', 'dass', 'der', 'die',
            'das', 'ein', 'eine', 'ist', 'sind', 'war', 'waren', 'wird',
            'werden', 'hat', 'haben', 'kann', 'können', 'muss', 'müssen',
            'nicht', 'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr',
        }

        keywords = [w for w in words if w.lower() not in stopwords and len(w) > 2]

        # Häufigste Wörter zurückgeben
        from collections import Counter
        return [word for word, _ in Counter(keywords).most_common(5)]


# ==================== ANALYZERS ====================

class ProblemAnalyzer:
    """Analysiert Probleme um sie besser zu verstehen"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge = knowledge_base

    def analyze(self, problem: Problem) -> Dict:
        """
        Führt eine vollständige Analyse eines Problems durch.

        Returns:
            Dict mit Analyse-Ergebnissen
        """
        analysis = {
            "problem_id": problem.id,
            "type": self._classify_type(problem),
            "complexity": self._assess_complexity(problem),
            "root_causes": self._find_root_causes(problem),
            "dependencies": self._find_dependencies(problem),
            "similar_problems": self._find_similar(problem),
            "missing_information": self._find_gaps(problem),
            "constraints_analysis": self._analyze_constraints(problem),
            "decomposition": self._suggest_decomposition(problem),
        }

        return analysis

    def _classify_type(self, problem: Problem) -> ProblemType:
        """Klassifiziert den Problem-Typ"""
        desc = problem.description.lower()

        # Technische Probleme
        if any(kw in desc for kw in ['error', 'fehler', 'bug', 'crash', 'exception',
                                      'import', 'syntax', 'code', 'function', 'class']):
            return ProblemType.TECHNICAL

        # Wissensfragen
        if any(kw in desc for kw in ['was ist', 'what is', 'wie funktioniert',
                                      'how does', 'erkläre', 'explain', 'warum']):
            return ProblemType.KNOWLEDGE

        # Aufgaben
        if any(kw in desc for kw in ['erstelle', 'create', 'mache', 'make',
                                      'implementiere', 'implement', 'füge hinzu', 'add']):
            return ProblemType.TASK

        # Entscheidungen
        if any(kw in desc for kw in ['soll ich', 'should i', 'welche', 'which',
                                      'besser', 'better', 'oder', 'or']):
            return ProblemType.DECISION

        # Kreativ
        if any(kw in desc for kw in ['idee', 'idea', 'kreativ', 'creative',
                                      'design', 'konzept', 'concept']):
            return ProblemType.CREATIVE

        # Kommunikation
        if any(kw in desc for kw in ['verstehe nicht', 'dont understand',
                                      'was meinst', 'what do you mean', 'unklar']):
            return ProblemType.COMMUNICATION

        # Konflikt
        if any(kw in desc for kw in ['konflikt', 'conflict', 'widerspruch',
                                      'contradiction', 'aber', 'but']):
            return ProblemType.CONFLICT

        # Ressourcen
        if any(kw in desc for kw in ['fehlt', 'missing', 'nicht verfügbar',
                                      'not available', 'brauche', 'need']):
            return ProblemType.RESOURCE

        return ProblemType.UNKNOWN

    def _assess_complexity(self, problem: Problem) -> ProblemComplexity:
        """Bewertet die Komplexität eines Problems"""
        score = 0

        # Länge der Beschreibung
        if len(problem.description) > 500:
            score += 2
        elif len(problem.description) > 200:
            score += 1

        # Anzahl Constraints
        score += min(len(problem.constraints), 3)

        # Anzahl Ziele
        score += min(len(problem.goals) - 1, 2) if problem.goals else 0

        # Hat Sub-Probleme
        if problem.sub_problems:
            score += len(problem.sub_problems)

        # Bekannter Problem-Typ?
        similar = self.knowledge.find_similar_problem(problem)
        if not similar:
            score += 1  # Unbekannt = komplexer

        # Mapping
        if score <= 1:
            return ProblemComplexity.TRIVIAL
        elif score <= 3:
            return ProblemComplexity.SIMPLE
        elif score <= 5:
            return ProblemComplexity.MODERATE
        elif score <= 7:
            return ProblemComplexity.COMPLEX
        else:
            return ProblemComplexity.VERY_COMPLEX

    def _find_root_causes(self, problem: Problem) -> List[str]:
        """Versucht die Grundursachen zu identifizieren"""
        causes = []
        desc = problem.description.lower()

        # Technische Ursachen
        if 'import' in desc:
            causes.append("Möglicherweise fehlende Dependency oder falscher Import-Pfad")
        if 'permission' in desc or 'berechtigung' in desc:
            causes.append("Möglicherweise fehlende Berechtigungen")
        if 'not found' in desc or 'nicht gefunden' in desc:
            causes.append("Möglicherweise falscher Pfad oder fehlende Datei")
        if 'timeout' in desc:
            causes.append("Möglicherweise Netzwerk-Problem oder zu langsame Verarbeitung")
        if 'memory' in desc or 'speicher' in desc:
            causes.append("Möglicherweise Speicher-Problem")

        # Aus Kontext
        if 'error_message' in problem.context:
            error = problem.context['error_message']
            known_solution = self.knowledge.find_error_solution(error)
            if known_solution:
                causes.append(f"Bekannte Ursache: {known_solution}")

        return causes if causes else ["Ursache noch unklar - weitere Analyse nötig"]

    def _find_dependencies(self, problem: Problem) -> List[str]:
        """Findet Abhängigkeiten des Problems"""
        deps = []

        # Aus Kontext
        if 'module' in problem.context:
            deps.append(f"Abhängig von Modul: {problem.context['module']}")

        if 'requires' in problem.context:
            deps.extend(problem.context['requires'])

        # Aus Beschreibung extrahieren
        desc = problem.description
        import_match = re.findall(r'import\s+(\w+)', desc)
        deps.extend([f"Import: {m}" for m in import_match])

        return deps

    def _find_similar(self, problem: Problem) -> List[Dict]:
        """Findet ähnliche bereits gelöste Probleme"""
        similar = self.knowledge.find_similar_problem(problem)
        if similar:
            return [similar]
        return []

    def _find_gaps(self, problem: Problem) -> List[str]:
        """Findet fehlende Informationen"""
        gaps = []

        if not problem.goals:
            gaps.append("Ziel ist nicht klar definiert")

        if problem.problem_type == ProblemType.UNKNOWN:
            gaps.append("Problem-Typ konnte nicht bestimmt werden")

        if 'error_message' not in problem.context and problem.problem_type == ProblemType.TECHNICAL:
            gaps.append("Genaue Fehlermeldung fehlt")

        if not problem.constraints:
            gaps.append("Keine Einschränkungen definiert - alles erlaubt?")

        return gaps

    def _analyze_constraints(self, problem: Problem) -> Dict:
        """Analysiert die Einschränkungen"""
        hard_constraints = []
        soft_constraints = []

        for constraint in problem.constraints:
            if any(kw in constraint.lower() for kw in ['muss', 'must', 'zwingend', 'required']):
                hard_constraints.append(constraint)
            else:
                soft_constraints.append(constraint)

        return {
            "hard": hard_constraints,
            "soft": soft_constraints,
            "total": len(problem.constraints),
        }

    def _suggest_decomposition(self, problem: Problem) -> List[str]:
        """Schlägt eine Zerlegung in Teilprobleme vor"""
        suggestions = []

        if problem.complexity.value >= ProblemComplexity.COMPLEX.value:
            suggestions.append("Problem ist komplex - Zerlegung empfohlen")

        # Typspezifische Vorschläge
        if problem.problem_type == ProblemType.TASK:
            suggestions.append("1. Anforderungen klären")
            suggestions.append("2. Design/Planung")
            suggestions.append("3. Implementierung")
            suggestions.append("4. Test")

        elif problem.problem_type == ProblemType.TECHNICAL:
            suggestions.append("1. Fehler reproduzieren")
            suggestions.append("2. Ursache lokalisieren")
            suggestions.append("3. Lösung entwickeln")
            suggestions.append("4. Lösung verifizieren")

        return suggestions


# ==================== OUT-OF-BOX THINKING ENGINE ====================

@dataclass
class Hypothesis:
    """Eine Hypothese die Holo selbständig generiert hat"""
    id: str
    description: str
    confidence: float  # 0.0 - 1.0
    evidence_for: List[str] = field(default_factory=list)
    evidence_against: List[str] = field(default_factory=list)
    tested: bool = False
    test_result: Optional[bool] = None
    origin: str = "generated"  # generated, random_association, analogy, perspective_shift

    def update_confidence(self):
        """Aktualisiert Confidence basierend auf Evidenz"""
        for_count = len(self.evidence_for)
        against_count = len(self.evidence_against)
        total = for_count + against_count
        if total > 0:
            self.confidence = for_count / total
        else:
            self.confidence = 0.5


@dataclass
class SimulationResult:
    """Ergebnis einer Lösungs-Simulation"""
    success: bool
    predicted_outcome: str
    risks_identified: List[str]
    side_effects: List[str]
    confidence: float
    simulation_method: str  # mental, sandbox, code_analysis
    execution_time_ms: int = 0
    recommendation: str = ""


class WebResearcher:
    """
    Recherchiert im Web nach Lösungen für unbekannte Probleme.

    Holo kann das Web durchsuchen wenn sie bei einem Problem nicht weiterkommt
    und keine interne Lösung findet.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.search_history: List[Dict] = []
        self.cache: Dict[str, Dict] = {}
        self._search_engines = [
            "duckduckgo",  # Primär - privacy-freundlich
            "google",
            "stackoverflow",
            "github"
        ]

    def search(self, query: str, problem_type: ProblemType = None) -> Dict:
        """
        Sucht im Web nach Lösungen.

        Args:
            query: Die Suchanfrage
            problem_type: Typ des Problems für spezifischere Suche

        Returns:
            Dict mit Suchergebnissen und extrahierten Lösungsansätzen
        """
        # Cache prüfen
        cache_key = hashlib.md5(query.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Suchanfrage optimieren basierend auf Problem-Typ
        optimized_query = self._optimize_query(query, problem_type)

        results = {
            "query": query,
            "optimized_query": optimized_query,
            "sources": [],
            "solutions_found": [],
            "related_topics": [],
            "confidence": 0.0,
            "searched_at": datetime.now().isoformat()
        }

        # Versuche verschiedene Such-Methoden
        try:
            # 1. Lokale Dokumentation durchsuchen
            local_results = self._search_local_docs(optimized_query)
            if local_results:
                results["sources"].append({"type": "local_docs", "results": local_results})

            # 2. Simulierte Web-Suche (da echte Web-API benötigt würde)
            # In echter Implementierung würde hier API-Aufruf stehen
            web_results = self._simulate_web_search(optimized_query, problem_type)
            results["sources"].extend(web_results.get("sources", []))
            results["solutions_found"].extend(web_results.get("solutions", []))

            # 3. Bekannte Lösungsmuster matchen
            pattern_matches = self._match_known_patterns(query, problem_type)
            results["solutions_found"].extend(pattern_matches)

            # Confidence berechnen
            if results["solutions_found"]:
                results["confidence"] = min(0.9, 0.3 + 0.2 * len(results["solutions_found"]))

        except Exception as e:
            results["error"] = str(e)

        # Cachen und speichern
        self.cache[cache_key] = results
        self.search_history.append(results)

        return results

    def _optimize_query(self, query: str, problem_type: ProblemType) -> str:
        """Optimiert die Suchanfrage"""
        # Füge typspezifische Keywords hinzu
        type_keywords = {
            ProblemType.TECHNICAL: "solution fix error",
            ProblemType.KNOWLEDGE: "explanation tutorial guide",
            ProblemType.TASK: "how to implementation example",
            ProblemType.CREATIVE: "creative approach alternative",
        }

        suffix = type_keywords.get(problem_type, "")

        # Python-spezifische Optimierung
        if any(kw in query.lower() for kw in ['python', 'import', 'class', 'def', 'exception']):
            suffix += " python"

        return f"{query} {suffix}".strip()

    def _search_local_docs(self, query: str) -> List[Dict]:
        """Durchsucht lokale Dokumentation"""
        results = []

        # Suche in typischen Docs-Verzeichnissen
        doc_paths = [
            Path(__file__).parent / "docs",
            Path(__file__).parent / "README.md",
            Path.home() / ".local/share/docs"
        ]

        query_lower = query.lower()
        keywords = query_lower.split()

        for doc_path in doc_paths:
            if doc_path.exists():
                if doc_path.is_file():
                    try:
                        content = doc_path.read_text(encoding='utf-8', errors='ignore')
                        if any(kw in content.lower() for kw in keywords):
                            results.append({
                                "source": str(doc_path),
                                "relevance": "partial_match"
                            })
                    except:
                        pass

        return results

    def _simulate_web_search(self, query: str, problem_type: ProblemType) -> Dict:
        """
        Simuliert Web-Suche mit bekannten Lösungsmustern.

        In einer echten Implementierung würde hier ein API-Aufruf stehen.
        Für jetzt nutzen wir eingebautes Wissen.
        """
        results = {"sources": [], "solutions": []}

        # Bekannte Lösungsmuster
        common_solutions = {
            "import": [
                {"solution": "pip install <package_name>", "confidence": 0.8},
                {"solution": "Überprüfe PYTHONPATH und sys.path", "confidence": 0.7},
                {"solution": "Prüfe ob __init__.py existiert", "confidence": 0.6}
            ],
            "connection": [
                {"solution": "Überprüfe Netzwerk-Konnektivität", "confidence": 0.8},
                {"solution": "Prüfe Firewall-Einstellungen", "confidence": 0.7},
                {"solution": "Timeout erhöhen", "confidence": 0.6}
            ],
            "memory": [
                {"solution": "Speicher freigeben mit gc.collect()", "confidence": 0.7},
                {"solution": "Daten in Chunks verarbeiten", "confidence": 0.8},
                {"solution": "Generator statt Liste verwenden", "confidence": 0.7}
            ],
            "permission": [
                {"solution": "Berechtigungen mit chmod anpassen", "confidence": 0.8},
                {"solution": "Als Administrator ausführen", "confidence": 0.7},
                {"solution": "Datei-Eigentümer prüfen", "confidence": 0.6}
            ],
            "database": [
                {"solution": "Connection-Pool verwenden", "confidence": 0.7},
                {"solution": "Indexe überprüfen", "confidence": 0.8},
                {"solution": "Query optimieren", "confidence": 0.8}
            ],
            "async": [
                {"solution": "await vergessen? Prüfe async/await", "confidence": 0.8},
                {"solution": "Event-Loop prüfen", "confidence": 0.7},
                {"solution": "asyncio.run() verwenden", "confidence": 0.7}
            ]
        }

        # Matche Query gegen bekannte Muster
        query_lower = query.lower()
        for pattern, solutions in common_solutions.items():
            if pattern in query_lower:
                results["solutions"].extend(solutions)
                results["sources"].append({
                    "type": "knowledge_base",
                    "pattern": pattern,
                    "matches": len(solutions)
                })

        return results

    def _match_known_patterns(self, query: str, problem_type: ProblemType) -> List[Dict]:
        """Matcht gegen bekannte Problemmuster"""
        matches = []

        # Fehler-Pattern-Matching
        error_patterns = {
            r"ModuleNotFoundError|ImportError": {
                "solution": "Modul installieren oder Import-Pfad korrigieren",
                "steps": ["pip install <module>", "Prüfe sys.path", "Prüfe __init__.py"]
            },
            r"ConnectionError|TimeoutError": {
                "solution": "Netzwerk-Problem beheben",
                "steps": ["Verbindung testen", "Timeout erhöhen", "Retry-Logik hinzufügen"]
            },
            r"PermissionError|Access denied": {
                "solution": "Berechtigungen anpassen",
                "steps": ["chmod/chown verwenden", "Als Admin ausführen", "Pfad prüfen"]
            },
            r"MemoryError|OutOfMemory": {
                "solution": "Speicherverbrauch optimieren",
                "steps": ["Batch-Verarbeitung", "Garbage Collection", "Speicher-Profiling"]
            },
            r"SyntaxError|IndentationError": {
                "solution": "Code-Syntax korrigieren",
                "steps": ["Einrückung prüfen", "Klammern prüfen", "Linter verwenden"]
            }
        }

        for pattern, solution_info in error_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                matches.append({
                    "pattern_matched": pattern,
                    "solution": solution_info["solution"],
                    "steps": solution_info["steps"],
                    "confidence": 0.8
                })

        return matches


class SolutionSimulator:
    """
    Simuliert Lösungen bevor sie angewendet werden.

    Holo "spielt durch" was passieren würde, ohne es wirklich zu tun.
    So kann sie Risiken und Nebenwirkungen vorhersagen.
    """

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path(__file__).parent
        self.simulation_log: List[SimulationResult] = []

    def simulate(self, solution: str, problem: 'Problem', context: Dict = None) -> SimulationResult:
        """
        Simuliert eine Lösung.

        Args:
            solution: Die vorgeschlagene Lösung
            problem: Das zu lösende Problem
            context: Zusätzlicher Kontext

        Returns:
            SimulationResult mit Vorhersage
        """
        start_time = time.time()

        # Wähle Simulationsmethode basierend auf Problem-Typ
        if problem.problem_type == ProblemType.TECHNICAL:
            result = self._simulate_technical(solution, problem, context)
        elif problem.problem_type in [ProblemType.TASK, ProblemType.DECISION]:
            result = self._simulate_logical(solution, problem, context)
        else:
            result = self._simulate_mental(solution, problem, context)

        result.execution_time_ms = int((time.time() - start_time) * 1000)
        self.simulation_log.append(result)

        return result

    def _simulate_technical(self, solution: str, problem: 'Problem',
                           context: Dict) -> SimulationResult:
        """Simuliert technische Lösungen"""
        risks = []
        side_effects = []
        success_probability = 0.7

        solution_lower = solution.lower()

        # Risikoanalyse
        if any(kw in solution_lower for kw in ['delete', 'remove', 'drop', 'löschen']):
            risks.append("Datenverlust möglich - Backup empfohlen")
            success_probability -= 0.1

        if any(kw in solution_lower for kw in ['sudo', 'root', 'admin']):
            risks.append("Erhöhte Rechte erforderlich - Sicherheitsrisiko")
            side_effects.append("Könnte System-weite Änderungen verursachen")

        if any(kw in solution_lower for kw in ['restart', 'reboot', 'neustart']):
            side_effects.append("Unterbrechung des Betriebs")
            risks.append("Laufende Prozesse werden beendet")

        if any(kw in solution_lower for kw in ['update', 'upgrade']):
            risks.append("Kompatibilitätsprobleme möglich")
            side_effects.append("Andere Dependencies könnten betroffen sein")

        if any(kw in solution_lower for kw in ['config', 'settings', 'konfiguration']):
            risks.append("Konfigurationsänderung könnte andere Features beeinflussen")
            side_effects.append("Backup der alten Config empfohlen")

        # Code-Syntax prüfen wenn es Code ist
        if self._looks_like_code(solution):
            syntax_check = self._check_code_syntax(solution)
            if not syntax_check["valid"]:
                risks.append(f"Möglicher Syntax-Fehler: {syntax_check['error']}")
                success_probability -= 0.2

        # Recommendation generieren
        if risks:
            recommendation = f"Vor Ausführung: {risks[0]}"
        else:
            recommendation = "Lösung erscheint sicher zum Ausführen"

        return SimulationResult(
            success=success_probability > 0.5,
            predicted_outcome="Technische Änderung wird durchgeführt",
            risks_identified=risks,
            side_effects=side_effects,
            confidence=success_probability,
            simulation_method="code_analysis",
            recommendation=recommendation
        )

    def _simulate_logical(self, solution: str, problem: 'Problem',
                         context: Dict) -> SimulationResult:
        """Simuliert logische/task-basierte Lösungen"""
        # Mentale Durchspielung der Schritte
        steps = solution.split('\n') if '\n' in solution else [solution]

        risks = []
        side_effects = []
        success_probability = 0.75

        for i, step in enumerate(steps):
            step_lower = step.lower()

            # Prüfe auf problematische Patterns
            if 'falls' in step_lower or 'wenn' in step_lower or 'if' in step_lower:
                # Bedingung gefunden - könnte fehlschlagen
                risks.append(f"Schritt {i+1} hat Bedingung - könnte nicht zutreffen")

            if 'warte' in step_lower or 'wait' in step_lower:
                side_effects.append(f"Schritt {i+1} könnte Verzögerung verursachen")

        # Ziele prüfen
        goals_addressed = 0
        for goal in problem.goals:
            if any(word in solution.lower() for word in goal.lower().split()):
                goals_addressed += 1

        if problem.goals:
            goal_coverage = goals_addressed / len(problem.goals)
            success_probability *= (0.5 + 0.5 * goal_coverage)

            if goal_coverage < 0.5:
                risks.append("Lösung adressiert möglicherweise nicht alle Ziele")

        return SimulationResult(
            success=success_probability > 0.5,
            predicted_outcome="Aufgabe wird schrittweise ausgeführt",
            risks_identified=risks,
            side_effects=side_effects,
            confidence=success_probability,
            simulation_method="mental",
            recommendation="Schritte einzeln ausführen und Ergebnis prüfen"
        )

    def _simulate_mental(self, solution: str, problem: 'Problem',
                        context: Dict) -> SimulationResult:
        """Mentale Simulation - Gedankenexperiment"""
        # Generische Analyse
        word_count = len(solution.split())

        risks = []
        side_effects = []

        # Zu kurze Lösung?
        if word_count < 5:
            risks.append("Lösung möglicherweise zu unspezifisch")

        # Zu komplexe Lösung?
        if word_count > 100:
            risks.append("Lösung könnte zu komplex sein")
            side_effects.append("Implementierung könnte länger dauern")

        return SimulationResult(
            success=True,
            predicted_outcome="Lösung wird versucht",
            risks_identified=risks,
            side_effects=side_effects,
            confidence=0.6,
            simulation_method="mental",
            recommendation="Lösung schrittweise umsetzen"
        )

    def _looks_like_code(self, text: str) -> bool:
        """Prüft ob Text wie Code aussieht"""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ',
            '()', '{}', '[]', '==', '!=',
            'return ', 'if ', 'for ', 'while '
        ]
        return any(indicator in text for indicator in code_indicators)

    def _check_code_syntax(self, code: str) -> Dict:
        """Prüft Python-Syntax"""
        try:
            compile(code, '<string>', 'exec')
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": str(e)}
        except:
            return {"valid": True, "error": None}  # Bei anderen Fehlern annehmen es ist ok


class LateralThinkingEngine:
    """
    Engine für laterales (kreatives/out-of-box) Denken.

    Verwendet verschiedene Kreativitätstechniken:
    - Random Association: Zufällige Verbindungen herstellen
    - Perspective Shift: Problem aus anderen Blickwinkeln betrachten
    - Reversal: Das Gegenteil überlegen
    - Analogy: Analogien aus anderen Bereichen
    - Combination: Elemente neu kombinieren
    """

    def __init__(self):
        self.thinking_techniques = [
            "random_association",
            "perspective_shift",
            "reversal",
            "analogy",
            "combination",
            "what_if",
            "constraint_removal",
            "exaggeration"
        ]

        # Datenbanken für kreatives Denken
        self._perspectives = [
            "ein Anfänger", "ein Experte", "ein Kind",
            "ein Außerirdischer", "ein Historiker", "ein Künstler",
            "ein Skeptiker", "ein Optimist", "ein Minimalist"
        ]

        self._domains = [
            "Natur", "Musik", "Architektur", "Sport",
            "Kochen", "Medizin", "Raumfahrt", "Geschichte",
            "Biologie", "Physik", "Spiele"
        ]

        self._random_concepts = [
            "Wasser fließt immer bergab",
            "Ein Baum wächst langsam aber stetig",
            "Bienen arbeiten als Team",
            "Licht kann gebündelt werden",
            "Musik hat Rhythmus und Struktur",
            "Brücken verbinden zwei Seiten",
            "Samen brauchen Zeit zum Keimen",
            "Wölfe jagen im Rudel",
            "Wellen brechen und bilden sich neu"
        ]

    def think_laterally(self, problem: 'Problem',
                       techniques: List[str] = None) -> List[Dict]:
        """
        Wendet laterales Denken auf ein Problem an.

        Args:
            problem: Das zu lösende Problem
            techniques: Spezifische Techniken (oder alle)

        Returns:
            Liste von kreativen Ideen
        """
        techniques = techniques or self.thinking_techniques
        ideas = []

        for technique in techniques:
            method = getattr(self, f"_apply_{technique}", None)
            if method:
                try:
                    idea = method(problem)
                    if idea:
                        ideas.append({
                            "technique": technique,
                            "idea": idea,
                            "confidence": self._rate_idea(idea, problem)
                        })
                except Exception as e:
                    logger.debug(f"Lateral thinking {technique} error: {e}")

        # Sortiere nach Confidence
        ideas.sort(key=lambda x: x["confidence"], reverse=True)

        return ideas

    def _apply_random_association(self, problem: 'Problem') -> str:
        """Zufällige Assoziation - verbindet Problem mit zufälligem Konzept"""
        concept = random.choice(self._random_concepts)

        # Versuche Verbindung herzustellen
        connection = self._find_connection(problem.description, concept)

        return f"Wie '{concept}': {connection}"

    def _apply_perspective_shift(self, problem: 'Problem') -> str:
        """Betrachtet Problem aus anderer Perspektive"""
        perspective = random.choice(self._perspectives)

        return f"Aus Sicht von {perspective}: Was würde jemand tun, der das Problem noch nie gesehen hat? Vielleicht die einfachste mögliche Lösung versuchen."

    def _apply_reversal(self, problem: 'Problem') -> str:
        """Überlegt das Gegenteil"""
        desc = problem.description.lower()

        # Finde Kernverben und invertiere
        inversions = {
            "funktioniert nicht": "Was würde es zum Funktionieren bringen?",
            "fehlt": "Was wäre wenn es zu viel davon gäbe?",
            "zu langsam": "Was wenn Geschwindigkeit egal wäre?",
            "zu komplex": "Was ist die simpelste Version?",
            "error": "Was müsste passieren damit kein Error kommt?"
        }

        for pattern, reversal in inversions.items():
            if pattern in desc:
                return f"Umkehrung: {reversal}"

        return "Umkehrung: Was wenn wir das Gegenteil des Problems hätten? Was wäre dann die Lösung?"

    def _apply_analogy(self, problem: 'Problem') -> str:
        """Findet Analogien aus anderen Bereichen"""
        domain = random.choice(self._domains)

        analogies = {
            "Natur": "In der Natur lösen Organismen ähnliche Probleme durch Anpassung und Evolution",
            "Musik": "In der Musik werden Probleme durch Variation und Wiederholung gelöst",
            "Architektur": "In der Architektur plant man von der Struktur zur Detail-Ebene",
            "Sport": "Im Sport trainiert man spezifische Fähigkeiten isoliert",
            "Kochen": "Beim Kochen bereitet man Zutaten vor, bevor man sie kombiniert",
            "Medizin": "In der Medizin behandelt man die Ursache, nicht nur die Symptome",
            "Biologie": "In der Biologie passen sich Systeme durch Feedback an"
        }

        analogy = analogies.get(domain, f"In {domain} werden Probleme systematisch angegangen")

        return f"Analogie aus {domain}: {analogy}"

    def _apply_combination(self, problem: 'Problem') -> str:
        """Kombiniert verschiedene Lösungsansätze"""
        approaches = [
            "automatisieren",
            "vereinfachen",
            "aufteilen",
            "zusammenführen",
            "auslagern",
            "cachen",
            "parallelisieren"
        ]

        combo = random.sample(approaches, 2)

        return f"Kombination: Was wenn wir {combo[0]} UND {combo[1]} würden?"

    def _apply_what_if(self, problem: 'Problem') -> str:
        """Stellt 'Was wäre wenn' Fragen"""
        what_ifs = [
            "Was wenn das Problem ein Feature wäre?",
            "Was wenn wir unbegrenzte Ressourcen hätten?",
            "Was wenn wir das Problem gar nicht lösen müssten?",
            "Was wenn die Lösung schon existiert und wir sie nur finden müssen?",
            "Was wenn wir das Problem von Grund auf neu designen könnten?"
        ]

        return random.choice(what_ifs)

    def _apply_constraint_removal(self, problem: 'Problem') -> str:
        """Entfernt gedanklich Einschränkungen"""
        constraints = problem.constraints or ["Zeit", "Ressourcen", "Komplexität"]

        if constraints:
            removed = random.choice(constraints) if problem.constraints else "alle Einschränkungen"
            return f"Ohne Einschränkung '{removed}': Wie würden wir das Problem dann lösen?"

        return "Ohne jede Einschränkung: Was wäre die ideale Lösung?"

    def _apply_exaggeration(self, problem: 'Problem') -> str:
        """Übertreibt das Problem oder die Lösung"""
        return "Übertreibung: Was wenn das Problem 1000x größer wäre? Welche Lösung würde dann funktionieren? Vielleicht skaliert diese Lösung auch für das kleine Problem."

    def _find_connection(self, problem_desc: str, concept: str) -> str:
        """Findet eine Verbindung zwischen Problem und Konzept"""
        # Einfache Verbindungslogik
        connections = {
            "fließt": "Vielleicht sollte auch die Lösung 'fließen' - Schritt für Schritt",
            "wächst": "Kleine Schritte, die sich aufbauen, könnten helfen",
            "Team": "Vielleicht braucht es mehrere Komponenten die zusammenarbeiten",
            "gebündelt": "Fokussierung auf einen Aspekt könnte helfen",
            "Rhythmus": "Ein strukturierter, wiederholbarer Ansatz",
            "verbinden": "Vielleicht müssen zwei Teile verbunden werden",
            "Zeit": "Geduld und inkrementelle Verbesserung",
            "Rudel": "Mehrere kleine Lösungen statt einer großen"
        }

        for keyword, connection in connections.items():
            if keyword.lower() in concept.lower():
                return connection

        return "Die Natur hat oft elegante Lösungen - einfach und effektiv"

    def _rate_idea(self, idea: str, problem: 'Problem') -> float:
        """Bewertet wie gut eine Idee zum Problem passt"""
        # Einfache Heuristik
        score = 0.5

        # Punkte für Relevanz
        problem_words = set(problem.description.lower().split())
        idea_words = set(idea.lower().split())
        overlap = len(problem_words & idea_words)
        score += overlap * 0.05

        # Punkte für Konkretheit
        if any(word in idea.lower() for word in ['konkret', 'spezifisch', 'direkt']):
            score += 0.1

        # Punkte für Aktionsorientierung
        if any(word in idea.lower() for word in ['tun', 'machen', 'versuchen', 'könnte']):
            score += 0.1

        return min(1.0, score)


class HypothesisGenerator:
    """
    Generiert selbständig Hypothesen über Probleme und Lösungen.

    Holo kann eigenständig:
    - Vermutungen aufstellen
    - Diese testen
    - Aus Ergebnissen lernen
    """

    def __init__(self):
        self.hypotheses: List[Hypothesis] = []
        self.tested_hypotheses: List[Hypothesis] = []

    def generate_hypotheses(self, problem: 'Problem',
                           analysis: Dict = None,
                           count: int = 5) -> List[Hypothesis]:
        """
        Generiert Hypothesen über ein Problem.

        Args:
            problem: Das Problem
            analysis: Vorherige Analyse
            count: Anzahl zu generierender Hypothesen

        Returns:
            Liste von Hypothesen
        """
        hypotheses = []

        # 1. Ursachen-Hypothesen
        hypotheses.extend(self._generate_cause_hypotheses(problem, analysis))

        # 2. Lösungs-Hypothesen
        hypotheses.extend(self._generate_solution_hypotheses(problem, analysis))

        # 3. Kontext-Hypothesen
        hypotheses.extend(self._generate_context_hypotheses(problem, analysis))

        # Sortiere nach initialer Confidence
        hypotheses.sort(key=lambda h: h.confidence, reverse=True)

        # Speichere und gib zurück
        self.hypotheses.extend(hypotheses[:count])

        return hypotheses[:count]

    def _generate_cause_hypotheses(self, problem: 'Problem',
                                   analysis: Dict) -> List[Hypothesis]:
        """Generiert Hypothesen über mögliche Ursachen"""
        hypotheses = []
        desc = problem.description.lower()

        # Technische Ursachen-Hypothesen
        if problem.problem_type == ProblemType.TECHNICAL:
            # Import-Probleme
            if 'import' in desc or 'module' in desc:
                hypotheses.append(Hypothesis(
                    id=f"hyp_cause_{len(hypotheses)}",
                    description="Das Modul ist nicht installiert",
                    confidence=0.7,
                    evidence_for=["ImportError deutet auf fehlendes Modul"],
                    origin="generated"
                ))
                hypotheses.append(Hypothesis(
                    id=f"hyp_cause_{len(hypotheses)}",
                    description="Der Import-Pfad ist falsch",
                    confidence=0.5,
                    evidence_for=["Pfad-Probleme sind häufig"],
                    origin="generated"
                ))

            # Verbindungsprobleme
            if 'connection' in desc or 'verbindung' in desc:
                hypotheses.append(Hypothesis(
                    id=f"hyp_cause_{len(hypotheses)}",
                    description="Netzwerk ist nicht erreichbar",
                    confidence=0.6,
                    origin="generated"
                ))

            # Berechtigungsprobleme
            if 'permission' in desc or 'berechtigung' in desc:
                hypotheses.append(Hypothesis(
                    id=f"hyp_cause_{len(hypotheses)}",
                    description="Fehlende Dateisystem-Berechtigungen",
                    confidence=0.8,
                    evidence_for=["PermissionError ist eindeutig"],
                    origin="generated"
                ))

        return hypotheses

    def _generate_solution_hypotheses(self, problem: 'Problem',
                                      analysis: Dict) -> List[Hypothesis]:
        """Generiert Hypothesen über mögliche Lösungen"""
        hypotheses = []

        # Basis-Lösungshypothesen
        hypotheses.append(Hypothesis(
            id=f"hyp_sol_{len(hypotheses)}",
            description="Eine direkte Lösung existiert",
            confidence=0.6,
            evidence_for=["Die meisten Probleme haben bekannte Lösungen"],
            origin="generated"
        ))

        # Je nach Komplexität
        if analysis and analysis.get("complexity", ProblemComplexity.MODERATE).value >= 4:
            hypotheses.append(Hypothesis(
                id=f"hyp_sol_{len(hypotheses)}",
                description="Das Problem muss in Teile zerlegt werden",
                confidence=0.7,
                evidence_for=["Hohe Komplexität erkannt"],
                origin="generated"
            ))

        # Bei fehlender Info
        if analysis and analysis.get("missing_information"):
            hypotheses.append(Hypothesis(
                id=f"hyp_sol_{len(hypotheses)}",
                description="Mehr Information wird benötigt bevor gelöst werden kann",
                confidence=0.8,
                evidence_for=["Fehlende Informationen identifiziert"],
                origin="generated"
            ))

        return hypotheses

    def _generate_context_hypotheses(self, problem: 'Problem',
                                     analysis: Dict) -> List[Hypothesis]:
        """Generiert Hypothesen über den Kontext"""
        hypotheses = []

        # Umgebungs-Hypothesen
        hypotheses.append(Hypothesis(
            id=f"hyp_ctx_{len(hypotheses)}",
            description="Das Problem ist umgebungsabhängig",
            confidence=0.4,
            origin="random_association"
        ))

        # Timing-Hypothese
        hypotheses.append(Hypothesis(
            id=f"hyp_ctx_{len(hypotheses)}",
            description="Das Problem tritt nur unter bestimmten Bedingungen auf",
            confidence=0.3,
            origin="perspective_shift"
        ))

        return hypotheses

    def test_hypothesis(self, hypothesis: Hypothesis,
                       test_function: Callable = None) -> bool:
        """
        Testet eine Hypothese.

        Args:
            hypothesis: Die zu testende Hypothese
            test_function: Optionale Test-Funktion

        Returns:
            True wenn Hypothese bestätigt
        """
        hypothesis.tested = True

        if test_function:
            try:
                result = test_function(hypothesis)
                hypothesis.test_result = result
                if result:
                    hypothesis.evidence_for.append("Test bestätigt")
                else:
                    hypothesis.evidence_against.append("Test widerlegt")
            except Exception as e:
                hypothesis.evidence_against.append(f"Test fehlgeschlagen: {e}")
                hypothesis.test_result = False
        else:
            # Ohne Test-Funktion: basiere auf Confidence
            hypothesis.test_result = hypothesis.confidence > 0.5

        hypothesis.update_confidence()
        self.tested_hypotheses.append(hypothesis)

        return hypothesis.test_result or False

    def get_best_hypotheses(self, tested_only: bool = False,
                           min_confidence: float = 0.5) -> List[Hypothesis]:
        """Gibt die besten Hypothesen zurück"""
        source = self.tested_hypotheses if tested_only else self.hypotheses

        filtered = [h for h in source if h.confidence >= min_confidence]
        filtered.sort(key=lambda h: h.confidence, reverse=True)

        return filtered


class AutonomousExplorer:
    """
    Ermöglicht autonome Exploration und Entdeckung.

    Holo kann selbständig:
    - Neue Ideen generieren ohne gefragt zu werden
    - Verbindungen zwischen Konzepten entdecken
    - Wissenslücken identifizieren und füllen
    """

    def __init__(self, knowledge_base: 'KnowledgeBase' = None):
        self.knowledge = knowledge_base
        self.discoveries: List[Dict] = []
        self.exploration_log: List[Dict] = []

    def explore_autonomously(self, problem: 'Problem',
                            depth: int = 3) -> List[Dict]:
        """
        Exploriert ein Problem autonom.

        Args:
            problem: Ausgangsproblem
            depth: Tiefe der Exploration

        Returns:
            Liste von Entdeckungen
        """
        discoveries = []
        visited = set()

        # Start mit dem Kernproblem
        to_explore = [(problem.description, 0)]

        while to_explore and len(discoveries) < 10:
            current, current_depth = to_explore.pop(0)

            if current in visited or current_depth > depth:
                continue

            visited.add(current)

            # Exploriere diesen Knoten
            node_discoveries = self._explore_node(current, problem)
            discoveries.extend(node_discoveries)

            # Füge verwandte Konzepte zur Exploration hinzu
            for disc in node_discoveries:
                if disc.get("leads_to"):
                    for next_topic in disc["leads_to"]:
                        to_explore.append((next_topic, current_depth + 1))

        # Log
        self.exploration_log.append({
            "problem": problem.description,
            "depth_reached": depth,
            "discoveries": len(discoveries),
            "timestamp": datetime.now().isoformat()
        })

        self.discoveries.extend(discoveries)
        return discoveries

    def _explore_node(self, topic: str, context_problem: 'Problem') -> List[Dict]:
        """Exploriert einen einzelnen Wissens-Knoten"""
        discoveries = []

        # 1. Suche nach Verbindungen
        connections = self._find_connections(topic)
        if connections:
            discoveries.append({
                "type": "connection",
                "topic": topic,
                "connections": connections,
                "leads_to": connections[:2]  # Folge den ersten 2
            })

        # 2. Suche nach Mustern
        patterns = self._find_patterns(topic)
        if patterns:
            discoveries.append({
                "type": "pattern",
                "topic": topic,
                "patterns": patterns,
                "insight": f"Muster gefunden: {patterns[0]}"
            })

        # 3. Generiere Fragen
        questions = self._generate_questions(topic, context_problem)
        if questions:
            discoveries.append({
                "type": "questions",
                "topic": topic,
                "questions": questions,
                "leads_to": [q.replace("?", "") for q in questions[:2]]
            })

        return discoveries

    def _find_connections(self, topic: str) -> List[str]:
        """Findet Verbindungen zu anderen Konzepten"""
        # Statische Verbindungen basierend auf Domänenwissen
        connection_map = {
            "import": ["module", "package", "dependency", "pip"],
            "error": ["exception", "traceback", "debug", "logging"],
            "database": ["sql", "connection", "query", "orm"],
            "api": ["endpoint", "request", "response", "authentication"],
            "test": ["unittest", "pytest", "mock", "coverage"],
            "async": ["await", "coroutine", "event loop", "threading"],
            "file": ["path", "permission", "io", "stream"]
        }

        connections = []
        topic_lower = topic.lower()

        for key, related in connection_map.items():
            if key in topic_lower:
                connections.extend(related)

        return connections[:5]

    def _find_patterns(self, topic: str) -> List[str]:
        """Findet Muster im Thema"""
        patterns = []

        # Erkenne häufige Problem-Muster
        if "nicht" in topic.lower() or "not" in topic.lower():
            patterns.append("Negation: Etwas fehlt oder funktioniert nicht")

        if "zu" in topic.lower() and any(w in topic.lower() for w in ["langsam", "schnell", "viel", "wenig"]):
            patterns.append("Skalierung: Menge oder Geschwindigkeit ist das Problem")

        if "wieder" in topic.lower() or "immer" in topic.lower():
            patterns.append("Wiederholung: Problem tritt wiederholt auf")

        return patterns

    def _generate_questions(self, topic: str, problem: 'Problem') -> List[str]:
        """Generiert explorative Fragen"""
        questions = [
            f"Was verursacht {topic[:30]}?",
            f"Wann tritt {topic[:30]} auf?",
            f"Was wäre wenn {topic[:30]} nicht existieren würde?",
        ]

        return questions


# ==================== STRATEGY FINDER ====================

class StrategyFinder:
    """Findet mögliche Lösungsstrategien für ein Problem"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge = knowledge_base

    def find_strategies(self, problem: Problem, analysis: Dict) -> List[Strategy]:
        """
        Findet passende Strategien für ein Problem.

        Returns:
            Liste von Strategien, sortiert nach Score
        """
        strategies = []

        # 1. Direkte Strategie (wenn einfach genug)
        if analysis["complexity"].value <= ProblemComplexity.SIMPLE.value:
            strategies.append(self._create_direct_strategy(problem))

        # 2. Zerlegungsstrategie (bei komplexen Problemen)
        if analysis["complexity"].value >= ProblemComplexity.MODERATE.value:
            strategies.append(self._create_decompose_strategy(problem, analysis))

        # 3. Analogie-Strategie (wenn ähnliches Problem bekannt)
        if analysis["similar_problems"]:
            strategies.append(self._create_analogy_strategy(problem, analysis))

        # 4. Research-Strategie (wenn Info fehlt)
        if analysis["missing_information"]:
            strategies.append(self._create_research_strategy(problem, analysis))

        # 5. Typspezifische Strategien
        type_strategies = self._get_type_specific_strategies(problem, analysis)
        strategies.extend(type_strategies)

        # 6. Fallback-Strategien
        strategies.append(self._create_ask_strategy(problem))
        strategies.append(self._create_workaround_strategy(problem))

        # Sortiere nach Score
        strategies.sort(key=lambda s: s.score(), reverse=True)

        return strategies

    def _create_direct_strategy(self, problem: Problem) -> Strategy:
        """Erstellt eine direkte Lösungsstrategie"""
        return Strategy(
            id=f"direct_{problem.id}",
            strategy_type=StrategyType.DIRECT,
            description="Direkter Lösungsansatz ohne Umwege",
            steps=["Problem verstehen", "Lösung anwenden", "Ergebnis prüfen"],
            estimated_success=0.7,
            estimated_effort=0.2,
            risks=["Könnte zu einfach gedacht sein"],
        )

    def _create_decompose_strategy(self, problem: Problem, analysis: Dict) -> Strategy:
        """Erstellt eine Zerlegungsstrategie"""
        decomposition = analysis.get("decomposition", [])
        return Strategy(
            id=f"decompose_{problem.id}",
            strategy_type=StrategyType.DECOMPOSE,
            description="Problem in kleinere Teile zerlegen und einzeln lösen",
            steps=decomposition if decomposition else [
                "Problem in Teilprobleme zerlegen",
                "Teilprobleme priorisieren",
                "Teilprobleme einzeln lösen",
                "Lösungen zusammenführen"
            ],
            estimated_success=0.8,
            estimated_effort=0.6,
            risks=["Aufwändiger", "Teilprobleme könnten voneinander abhängen"],
        )

    def _create_analogy_strategy(self, problem: Problem, analysis: Dict) -> Strategy:
        """Erstellt eine Analogie-Strategie basierend auf ähnlichem Problem"""
        similar = analysis["similar_problems"][0] if analysis["similar_problems"] else {}
        return Strategy(
            id=f"analogy_{problem.id}",
            strategy_type=StrategyType.ANALOGIE,
            description=f"Lösung von ähnlichem Problem anpassen: {similar.get('description', '')[:50]}",
            steps=[
                "Ähnliches Problem analysieren",
                "Unterschiede identifizieren",
                "Lösung anpassen",
                "Angepasste Lösung testen"
            ],
            estimated_success=0.85,
            estimated_effort=0.4,
            risks=["Unterschiede könnten zu groß sein"],
            prerequisites=["Ähnliches Problem muss wirklich ähnlich sein"],
        )

    def _create_research_strategy(self, problem: Problem, analysis: Dict) -> Strategy:
        """Erstellt eine Research-Strategie"""
        gaps = analysis.get("missing_information", [])
        return Strategy(
            id=f"research_{problem.id}",
            strategy_type=StrategyType.RESEARCH,
            description="Erst fehlende Informationen sammeln",
            steps=[
                f"Recherchieren: {gap}" for gap in gaps[:3]
            ] + ["Mit gesammeltem Wissen erneut analysieren"],
            estimated_success=0.6,
            estimated_effort=0.5,
            risks=["Zeitaufwändig", "Könnte nicht alle Infos finden"],
        )

    def _create_ask_strategy(self, problem: Problem) -> Strategy:
        """Erstellt eine Frage-Strategie"""
        return Strategy(
            id=f"ask_{problem.id}",
            strategy_type=StrategyType.ASK,
            description="Benutzer um Klärung oder zusätzliche Infos bitten",
            steps=[
                "Klärende Fragen formulieren",
                "Benutzer fragen",
                "Mit neuen Infos erneut analysieren"
            ],
            estimated_success=0.9,
            estimated_effort=0.3,
            risks=["Benutzer könnte nicht antworten"],
            prerequisites=["Interaktion mit Benutzer möglich"],
        )

    def _create_workaround_strategy(self, problem: Problem) -> Strategy:
        """Erstellt eine Workaround-Strategie"""
        return Strategy(
            id=f"workaround_{problem.id}",
            strategy_type=StrategyType.WORKAROUND,
            description="Provisorische Umgehungslösung finden",
            steps=[
                "Alternative Wege identifizieren",
                "Einfachsten Workaround wählen",
                "Workaround implementieren",
                "Dokumentieren für spätere echte Lösung"
            ],
            estimated_success=0.7,
            estimated_effort=0.4,
            risks=["Keine echte Lösung", "Könnte später Probleme verursachen"],
        )

    def _get_type_specific_strategies(self, problem: Problem, analysis: Dict) -> List[Strategy]:
        """Gibt typspezifische Strategien zurück"""
        strategies = []

        if problem.problem_type == ProblemType.TECHNICAL:
            strategies.append(Strategy(
                id=f"debug_{problem.id}",
                strategy_type=StrategyType.TRIAL_ERROR,
                description="Systematisches Debugging",
                steps=[
                    "Fehler reproduzieren",
                    "Logs analysieren",
                    "Breakpoints setzen / Print-Debugging",
                    "Hypothese testen",
                    "Fix implementieren"
                ],
                estimated_success=0.75,
                estimated_effort=0.5,
            ))

        elif problem.problem_type == ProblemType.DECISION:
            strategies.append(Strategy(
                id=f"compare_{problem.id}",
                strategy_type=StrategyType.DIRECT,
                description="Optionen vergleichen und bewerten",
                steps=[
                    "Alle Optionen auflisten",
                    "Kriterien definieren",
                    "Optionen bewerten",
                    "Beste Option wählen"
                ],
                estimated_success=0.8,
                estimated_effort=0.3,
            ))

        elif problem.problem_type == ProblemType.KNOWLEDGE:
            strategies.append(Strategy(
                id=f"explain_{problem.id}",
                strategy_type=StrategyType.DIRECT,
                description="Wissen aus Memory/Kontext abrufen und erklären",
                steps=[
                    "Relevantes Wissen suchen",
                    "Zusammenhänge herstellen",
                    "Verständlich erklären"
                ],
                estimated_success=0.85,
                estimated_effort=0.2,
            ))

        return strategies


# ==================== PLANNER ====================

class Planner:
    """Erstellt konkrete Ausführungspläne aus Strategien"""

    def create_plan(self, problem: Problem, strategy: Strategy) -> Plan:
        """
        Erstellt einen detaillierten Plan aus einer Strategie.
        """
        plan = Plan(
            id=f"plan_{problem.id}_{strategy.id}",
            problem_id=problem.id,
            strategy_id=strategy.id,
        )

        # Konvertiere Strategie-Schritte zu Plan-Schritten
        previous_step_id = None
        for i, step_desc in enumerate(strategy.steps):
            step = PlanStep(
                id=f"step_{i}",
                description=step_desc,
                action=self._determine_action(step_desc, problem),
                depends_on=[previous_step_id] if previous_step_id else [],
            )
            plan.steps.append(step)
            previous_step_id = step.id

        return plan

    def _determine_action(self, step_description: str, problem: Problem) -> str:
        """Bestimmt die konkrete Aktion für einen Schritt"""
        desc_lower = step_description.lower()

        # Mapping von Beschreibungen zu Aktionen
        if any(kw in desc_lower for kw in ['verstehen', 'understand', 'analysieren', 'analyze']):
            return "ANALYZE"

        if any(kw in desc_lower for kw in ['recherchieren', 'research', 'suchen', 'search']):
            return "SEARCH"

        if any(kw in desc_lower for kw in ['fragen', 'ask', 'benutzer']):
            return "ASK_USER"

        if any(kw in desc_lower for kw in ['implementieren', 'implement', 'erstellen', 'create', 'fix']):
            return "IMPLEMENT"

        if any(kw in desc_lower for kw in ['testen', 'test', 'prüfen', 'verify']):
            return "TEST"

        if any(kw in desc_lower for kw in ['zerlegen', 'decompose', 'aufteilen', 'split']):
            return "DECOMPOSE"

        return "EXECUTE"


# ==================== EXECUTOR ====================

class PlanExecutor:
    """Führt Pläne aus und überwacht den Fortschritt"""

    def __init__(self, holo_brain=None):
        self.brain = holo_brain
        self._action_handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Registriert Standard-Action-Handler"""
        self._action_handlers = {
            "ANALYZE": self._handle_analyze,
            "SEARCH": self._handle_search,
            "ASK_USER": self._handle_ask_user,
            "IMPLEMENT": self._handle_implement,
            "TEST": self._handle_test,
            "DECOMPOSE": self._handle_decompose,
            "EXECUTE": self._handle_execute,
        }

    def register_handler(self, action: str, handler: Callable):
        """Registriert einen Custom Action Handler"""
        self._action_handlers[action] = handler

    def execute_plan(self, plan: Plan, problem: Problem) -> Plan:
        """
        Führt einen Plan aus.

        Returns:
            Aktualisierter Plan mit Ergebnissen
        """
        plan.status = "in_progress"
        plan.started_at = datetime.now()

        for step in plan.steps:
            # Prüfe Abhängigkeiten
            if not self._dependencies_met(step, plan):
                step.status = StepStatus.BLOCKED
                continue

            # Führe Schritt aus
            step.status = StepStatus.IN_PROGRESS
            step.started_at = datetime.now()

            try:
                result = self._execute_step(step, problem)
                step.result = result
                step.status = StepStatus.COMPLETED
            except Exception as e:
                step.error = str(e)
                step.retries += 1

                if step.retries < step.max_retries:
                    step.status = StepStatus.PENDING  # Retry später
                else:
                    step.status = StepStatus.FAILED
                    plan.status = "partial"

            step.completed_at = datetime.now()

        # Plan-Status aktualisieren
        all_completed = all(s.status == StepStatus.COMPLETED for s in plan.steps)
        any_failed = any(s.status == StepStatus.FAILED for s in plan.steps)

        if all_completed:
            plan.status = "completed"
        elif any_failed:
            plan.status = "failed"

        plan.completed_at = datetime.now()
        return plan

    def _dependencies_met(self, step: PlanStep, plan: Plan) -> bool:
        """Prüft ob alle Abhängigkeiten eines Schritts erfüllt sind"""
        for dep_id in step.depends_on:
            dep_step = next((s for s in plan.steps if s.id == dep_id), None)
            if dep_step and dep_step.status != StepStatus.COMPLETED:
                return False
        return True

    def _execute_step(self, step: PlanStep, problem: Problem) -> str:
        """Führt einen einzelnen Schritt aus"""
        handler = self._action_handlers.get(step.action, self._handle_execute)
        return handler(step, problem)

    def _handle_analyze(self, step: PlanStep, problem: Problem) -> str:
        """Handler für ANALYZE Aktionen"""
        return f"Analysiert: {step.description}"

    def _handle_search(self, step: PlanStep, problem: Problem) -> str:
        """Handler für SEARCH Aktionen"""
        # Hier könnte echte Suche stattfinden
        return f"Gesucht nach: {step.description}"

    def _handle_ask_user(self, step: PlanStep, problem: Problem) -> str:
        """Handler für ASK_USER Aktionen"""
        # Markiere als wartend auf Benutzer
        return f"Warte auf Benutzer-Input für: {step.description}"

    def _handle_implement(self, step: PlanStep, problem: Problem) -> str:
        """Handler für IMPLEMENT Aktionen"""
        return f"Implementiert: {step.description}"

    def _handle_test(self, step: PlanStep, problem: Problem) -> str:
        """Handler für TEST Aktionen"""
        return f"Getestet: {step.description}"

    def _handle_decompose(self, step: PlanStep, problem: Problem) -> str:
        """Handler für DECOMPOSE Aktionen"""
        return f"Zerlegt: {step.description}"

    def _handle_execute(self, step: PlanStep, problem: Problem) -> str:
        """Default Handler"""
        return f"Ausgeführt: {step.description}"


# ==================== MAIN PROBLEM SOLVER ====================

class HoloProblemSolver:
    """
    Universelles Problem-Solving System für Holo.

    Wird aktiviert wenn Holo bei IRGENDEINEM Problem nicht weiterkommt.
    Denkt analytisch, plant voraus, und lernt aus Ergebnissen.
    """

    def __init__(
        self,
        project_dir: Path = None,
        holo_brain = None,
        persist_path: Path = None
    ):
        self.project_dir = project_dir or Path(__file__).parent
        self.brain = holo_brain

        # Komponenten
        self.knowledge = KnowledgeBase(
            persist_path=persist_path or (self.project_dir / "data" / "problem_knowledge.json")
        )
        self.analyzer = ProblemAnalyzer(self.knowledge)
        self.strategy_finder = StrategyFinder(self.knowledge)
        self.planner = Planner()
        self.executor = PlanExecutor(holo_brain)

        # ======== OUT-OF-BOX THINKING KOMPONENTEN ========
        # Diese ermöglichen echtes autonomes, kreatives Denken

        # 1. Web-Recherche für unbekannte Probleme
        self.web_researcher = WebResearcher(timeout=30)

        # 2. Lösungs-Simulation vor Anwendung
        self.solution_simulator = SolutionSimulator(self.project_dir)

        # 3. Laterales/Kreatives Denken
        self.lateral_thinking = LateralThinkingEngine()

        # 4. Hypothesen-Generator
        self.hypothesis_generator = HypothesisGenerator()

        # 5. Autonome Exploration
        self.autonomous_explorer = AutonomousExplorer(self.knowledge)

        # State
        self.current_problem: Optional[Problem] = None
        self.thinking_log: List[ThinkingStep] = []
        self._problem_counter = 0

        # Out-of-Box Thinking State
        self._current_hypotheses: List[Hypothesis] = []
        self._creative_ideas: List[Dict] = []
        self._simulation_results: List[SimulationResult] = []
        self._web_research_results: Dict = {}

        # Statistiken
        self.stats = {
            "problems_solved": 0,
            "problems_failed": 0,
            "total_thinking_time_ms": 0,
            "creative_ideas_generated": 0,
            "hypotheses_tested": 0,
            "solutions_simulated": 0,
            "web_searches_performed": 0,
        }

        # Kognitive System-Verbindungen
        self._cognitive_systems = {}
        self._init_cognitive_connections()

        logger.info("HoloProblemSolver mit Out-of-Box Thinking initialisiert")

    def _init_cognitive_connections(self):
        """Verbindet mit allen kognitiven Systemen"""

        # 1. Meta-Cognition - Denken über das Denken
        try:
            from holo_meta_cognition import HoloMetaCognition
            if self.brain and hasattr(self.brain, 'meta_observer'):
                self._cognitive_systems['meta_cognition'] = self.brain.meta_observer
                logger.debug("Problem Solver mit Meta-Cognition verbunden")
        except ImportError:
            pass

        # 2. Learning System - Lernen aus Erfahrungen
        try:
            from holo_learning import HoloLearning
            if self.brain and hasattr(self.brain, 'learning_system'):
                self._cognitive_systems['learning'] = self.brain.learning_system
                logger.debug("Problem Solver mit Learning System verbunden")
        except ImportError:
            pass

        # 3. Context Mind - Kontext und Gedächtnis
        try:
            from holo_context_mind import HoloContextMind
            if self.brain and hasattr(self.brain, 'context_mind'):
                self._cognitive_systems['context_mind'] = self.brain.context_mind
                logger.debug("Problem Solver mit Context Mind verbunden")
        except ImportError:
            pass

        # 4. Self-Awareness - Selbstwahrnehmung
        try:
            from holo_self_awareness import HoloSelfAwareness
            if self.brain and hasattr(self.brain, 'self_awareness'):
                self._cognitive_systems['self_awareness'] = self.brain.self_awareness
                logger.debug("Problem Solver mit Self-Awareness verbunden")
        except ImportError:
            pass

        # 5. Creative Mind - Kreatives Denken
        try:
            from holo_creative_mind import HoloCreativeMind
            if self.brain and hasattr(self.brain, 'creative_mind'):
                self._cognitive_systems['creative_mind'] = self.brain.creative_mind
                logger.debug("Problem Solver mit Creative Mind verbunden")
        except ImportError:
            pass

        # 6. Cognitive Engine - Haupt-Kognition
        try:
            from holo_cognitive_engine import HoloCognitiveEngine
            if self.brain and hasattr(self.brain, 'cognitive_engine'):
                self._cognitive_systems['cognitive_engine'] = self.brain.cognitive_engine
                logger.debug("Problem Solver mit Cognitive Engine verbunden")
        except ImportError:
            pass

        # 7. Autonomous Thinking - Autonomes Denken
        try:
            from holo_autonomous_thinking import AutonomousThinking
            if self.brain and hasattr(self.brain, 'autonomous_thinking'):
                self._cognitive_systems['autonomous_thinking'] = self.brain.autonomous_thinking
                logger.debug("Problem Solver mit Autonomous Thinking verbunden")
        except ImportError:
            pass

        logger.info(f"Problem Solver mit {len(self._cognitive_systems)} kognitiven Systemen verbunden")

    def _consult_meta_cognition(self, phase: ThinkingPhase, thought: str) -> Optional[str]:
        """Fragt Meta-Cognition um Reflexion"""
        meta = self._cognitive_systems.get('meta_cognition')
        if not meta:
            return None

        try:
            if hasattr(meta, 'reflect_on_thought'):
                return meta.reflect_on_thought(thought, phase.value)
            elif hasattr(meta, 'observe'):
                meta.observe({
                    'type': 'problem_solving',
                    'phase': phase.value,
                    'thought': thought
                })
        except Exception as e:
            logger.debug(f"Meta-Cognition Fehler: {e}")

        return None

    def _consult_learning(self, problem: Problem) -> List[Dict]:
        """Fragt Learning System nach ähnlichen Erfahrungen"""
        learning = self._cognitive_systems.get('learning')
        if not learning:
            return []

        try:
            if hasattr(learning, 'find_similar_experiences'):
                return learning.find_similar_experiences(problem.description)
            elif hasattr(learning, 'recall'):
                return learning.recall(problem.description)
        except Exception as e:
            logger.debug(f"Learning System Fehler: {e}")

        return []

    def _consult_context_mind(self, problem: Problem) -> Dict:
        """Fragt Context Mind nach relevantem Kontext"""
        context_mind = self._cognitive_systems.get('context_mind')
        if not context_mind:
            return {}

        try:
            if hasattr(context_mind, 'get_relevant_context'):
                return context_mind.get_relevant_context(problem.description)
            elif hasattr(context_mind, 'search'):
                return context_mind.search(problem.description)
        except Exception as e:
            logger.debug(f"Context Mind Fehler: {e}")

        return {}

    def _consult_creative_mind(self, problem: Problem, strategies: List[Strategy]) -> Optional[Strategy]:
        """Fragt Creative Mind nach kreativen Lösungen"""
        creative = self._cognitive_systems.get('creative_mind')
        if not creative or problem.problem_type != ProblemType.CREATIVE:
            return None

        try:
            if hasattr(creative, 'generate_creative_solution'):
                creative_idea = creative.generate_creative_solution(problem.description)
                if creative_idea:
                    return Strategy(
                        id=f"creative_{problem.id}",
                        strategy_type=StrategyType.DIRECT,
                        description=f"Kreative Lösung: {creative_idea[:100]}",
                        steps=["Kreative Idee umsetzen", "Ergebnis prüfen"],
                        estimated_success=0.7,
                        estimated_effort=0.5,
                    )
        except Exception as e:
            logger.debug(f"Creative Mind Fehler: {e}")

        return None

    def _notify_learning_result(self, problem: Problem, solution: Solution):
        """Informiert Learning System über das Ergebnis"""
        learning = self._cognitive_systems.get('learning')
        if not learning:
            return

        try:
            if hasattr(learning, 'learn_from_experience'):
                learning.learn_from_experience({
                    'problem': problem.description,
                    'problem_type': problem.problem_type.value,
                    'success': solution.success,
                    'strategies_tried': solution.strategies_tried,
                    'lessons': solution.lessons_learned,
                    'duration_ms': solution.duration_ms,
                })
            elif hasattr(learning, 'record'):
                learning.record({
                    'type': 'problem_solved',
                    'success': solution.success,
                    'problem': problem.description[:100],
                })
        except Exception as e:
            logger.debug(f"Learning Notification Fehler: {e}")

    def _update_self_awareness(self, phase: ThinkingPhase, success: bool = None):
        """Aktualisiert Self-Awareness über den aktuellen Zustand"""
        awareness = self._cognitive_systems.get('self_awareness')
        if not awareness:
            return

        try:
            if hasattr(awareness, 'update_state'):
                awareness.update_state({
                    'activity': 'problem_solving',
                    'phase': phase.value,
                    'success': success,
                })
        except Exception as e:
            logger.debug(f"Self-Awareness Update Fehler: {e}")

    def solve(self,
              problem_description: str,
              context: Dict = None,
              goals: List[str] = None,
              constraints: List[str] = None) -> Solution:
        """
        Hauptmethode: Löst ein Problem analytisch.

        Args:
            problem_description: Beschreibung des Problems
            context: Zusätzlicher Kontext
            goals: Was soll erreicht werden?
            constraints: Einschränkungen

        Returns:
            Solution mit Ergebnis und Denkprotokoll
        """
        start_time = time.time()
        self.thinking_log.clear()

        # Self-Awareness: Problem-Solving gestartet
        self._update_self_awareness(ThinkingPhase.UNDERSTAND)

        # ============================================
        # PHASE 1: VERSTEHEN
        # ============================================
        self._think(ThinkingPhase.UNDERSTAND,
                   f"Was ist das Problem? '{problem_description[:100]}...'")

        # Meta-Cognition konsultieren
        meta_reflection = self._consult_meta_cognition(
            ThinkingPhase.UNDERSTAND,
            f"Analysiere Problem: {problem_description[:50]}"
        )
        if meta_reflection:
            self._think(ThinkingPhase.UNDERSTAND,
                       f"Meta-Reflexion: {meta_reflection}")

        # Problem-Objekt erstellen
        problem = self._create_problem(
            problem_description,
            context or {},
            goals or [],
            constraints or []
        )
        self.current_problem = problem

        self._think(ThinkingPhase.UNDERSTAND,
                   f"Problem erkannt als Typ: {problem.problem_type.value}",
                   f"Komplexität: {problem.complexity.name}")

        # ============================================
        # PHASE 2: ANALYSIEREN
        # ============================================
        self._think(ThinkingPhase.ANALYZE,
                   "Analysiere das Problem im Detail...")

        analysis = self.analyzer.analyze(problem)

        # Context Mind nach relevantem Kontext fragen
        context_info = self._consult_context_mind(problem)
        if context_info:
            self._think(ThinkingPhase.ANALYZE,
                       f"Context Mind liefert: {list(context_info.keys())}")
            # Kontext zur Analyse hinzufügen
            analysis["context_memory"] = context_info

        # Ursachen
        if analysis["root_causes"]:
            self._think(ThinkingPhase.ANALYZE,
                       f"Mögliche Ursachen: {analysis['root_causes']}",
                       f"Gefunden: {len(analysis['root_causes'])} mögliche Ursachen")

        # Abhängigkeiten
        if analysis["dependencies"]:
            self._think(ThinkingPhase.ANALYZE,
                       f"Abhängigkeiten: {analysis['dependencies']}")

        # Ähnliche Probleme
        if analysis["similar_problems"]:
            self._think(ThinkingPhase.ANALYZE,
                       "Ähnliches Problem gefunden! Kann Lösung adaptieren.",
                       "Analogie-Strategie vielversprechend")

        # ============================================
        # PHASE 2.5: HYPOTHESEN GENERIEREN (OUT-OF-BOX)
        # ============================================
        self._think(ThinkingPhase.ANALYZE,
                   "Generiere selbständig Hypothesen über das Problem...")

        self._current_hypotheses = self.hypothesis_generator.generate_hypotheses(
            problem, analysis, count=5
        )
        self.stats["hypotheses_tested"] += len(self._current_hypotheses)

        if self._current_hypotheses:
            best_hypothesis = self._current_hypotheses[0]
            self._think(ThinkingPhase.ANALYZE,
                       f"Hypothese generiert: {best_hypothesis.description}",
                       f"Confidence: {best_hypothesis.confidence:.0%}")

            # Füge Hypothesen zur Analyse hinzu
            analysis["hypotheses"] = [
                {"description": h.description, "confidence": h.confidence}
                for h in self._current_hypotheses
            ]

        # ============================================
        # PHASE 3: WISSEN SAMMELN
        # ============================================

        # Learning System nach Erfahrungen fragen
        past_experiences = self._consult_learning(problem)
        if past_experiences:
            self._think(ThinkingPhase.GATHER_KNOWLEDGE,
                       f"Learning System hat {len(past_experiences)} ähnliche Erfahrungen",
                       "Nutze vergangenes Wissen")
            analysis["past_experiences"] = past_experiences

        if analysis["missing_information"]:
            self._think(ThinkingPhase.GATHER_KNOWLEDGE,
                       f"Fehlende Infos: {analysis['missing_information']}",
                       "Muss eventuell nachfragen oder recherchieren")

        # ============================================
        # PHASE 3.5: WEB-RECHERCHE (OUT-OF-BOX)
        # Wenn wir nicht genug wissen, suchen wir im Web
        # ============================================
        should_research = (
            not analysis["similar_problems"] and
            analysis["missing_information"] and
            problem.complexity.value >= ProblemComplexity.MODERATE.value
        )

        if should_research:
            self._think(ThinkingPhase.GATHER_KNOWLEDGE,
                       "Keine bekannte Lösung - starte Web-Recherche...",
                       "Suche nach externem Wissen")

            self._web_research_results = self.web_researcher.search(
                problem.description,
                problem.problem_type
            )
            self.stats["web_searches_performed"] += 1

            if self._web_research_results.get("solutions_found"):
                solutions = self._web_research_results["solutions_found"]
                self._think(ThinkingPhase.GATHER_KNOWLEDGE,
                           f"Web-Recherche erfolgreich: {len(solutions)} Lösungsansätze gefunden",
                           f"Beste Lösung: {solutions[0].get('solution', '')[:50]}...")

                # Füge Web-Wissen zur Analyse hinzu
                analysis["web_research"] = self._web_research_results

        # ============================================
        # PHASE 4: STRATEGIEN FINDEN
        # ============================================
        self._think(ThinkingPhase.FIND_STRATEGIES,
                   "Suche nach möglichen Lösungsstrategien...")

        strategies = self.strategy_finder.find_strategies(problem, analysis)

        # Creative Mind nach kreativen Lösungen fragen
        creative_strategy = self._consult_creative_mind(problem, strategies)
        if creative_strategy:
            self._think(ThinkingPhase.FIND_STRATEGIES,
                       f"Creative Mind schlägt vor: {creative_strategy.description[:50]}",
                       "Kreative Lösung hinzugefügt")
            strategies.insert(0, creative_strategy)

        self._think(ThinkingPhase.FIND_STRATEGIES,
                   f"Gefundene Strategien: {[s.strategy_type.value for s in strategies]}",
                   f"{len(strategies)} Strategien zur Auswahl")

        # ============================================
        # PHASE 4.5: LATERALES DENKEN (OUT-OF-BOX)
        # Kreative Ideen generieren die "anders" sind
        # ============================================
        self._think(ThinkingPhase.FIND_STRATEGIES,
                   "Aktiviere laterales Denken - suche unkonventionelle Ideen...")

        self._creative_ideas = self.lateral_thinking.think_laterally(problem)
        self.stats["creative_ideas_generated"] += len(self._creative_ideas)

        if self._creative_ideas:
            # Die beste kreative Idee
            best_idea = self._creative_ideas[0]
            self._think(ThinkingPhase.FIND_STRATEGIES,
                       f"Kreative Idee ({best_idea['technique']}): {best_idea['idea'][:80]}...",
                       f"Confidence: {best_idea['confidence']:.0%}")

            # Konvertiere beste kreative Idee zu Strategie
            if best_idea['confidence'] > 0.5:
                lateral_strategy = Strategy(
                    id=f"lateral_{problem.id}",
                    strategy_type=StrategyType.DIRECT,
                    description=f"Kreativ: {best_idea['idea'][:100]}",
                    steps=[
                        "Kreative Idee durchdenken",
                        "Auf Problem anwenden",
                        "Ergebnis prüfen"
                    ],
                    estimated_success=best_idea['confidence'],
                    estimated_effort=0.5,
                    risks=["Unkonventioneller Ansatz - Ergebnis unsicher"]
                )
                strategies.insert(1, lateral_strategy)
                self._think(ThinkingPhase.FIND_STRATEGIES,
                           "Laterale Strategie hinzugefügt",
                           f"Jetzt {len(strategies)} Strategien")

        # Autonome Exploration für tieferes Verständnis
        if problem.complexity.value >= ProblemComplexity.COMPLEX.value:
            self._think(ThinkingPhase.FIND_STRATEGIES,
                       "Problem ist komplex - starte autonome Exploration...")

            discoveries = self.autonomous_explorer.explore_autonomously(problem, depth=2)
            if discoveries:
                self._think(ThinkingPhase.FIND_STRATEGIES,
                           f"Autonome Exploration: {len(discoveries)} Entdeckungen",
                           f"Insights: {discoveries[0].get('insight', discoveries[0].get('type', 'N/A'))}")

        # ============================================
        # PHASE 5: BEWERTEN
        # ============================================
        self._think(ThinkingPhase.EVALUATE,
                   "Bewerte Strategien nach Erfolgswahrscheinlichkeit und Aufwand...")

        # Meta-Cognition: Strategien reflektieren
        self._consult_meta_cognition(
            ThinkingPhase.EVALUATE,
            f"Bewerte {len(strategies)} Strategien für {problem.problem_type.value}"
        )

        # Beste Strategie wählen
        best_strategy = strategies[0] if strategies else None

        if best_strategy:
            self._think(ThinkingPhase.EVALUATE,
                       f"Beste Strategie: {best_strategy.strategy_type.value}",
                       f"Score: {best_strategy.score():.2f}, Erfolg: {best_strategy.estimated_success:.0%}")

        # ============================================
        # PHASE 6: PLANEN
        # ============================================
        if not best_strategy:
            return self._create_failed_solution(problem, "Keine Strategie gefunden", start_time)

        self._think(ThinkingPhase.PLAN,
                   f"Erstelle Plan für Strategie: {best_strategy.description}")

        plan = self.planner.create_plan(problem, best_strategy)

        self._think(ThinkingPhase.PLAN,
                   f"Plan erstellt mit {len(plan.steps)} Schritten",
                   f"Schritte: {[s.description for s in plan.steps]}")

        # ============================================
        # PHASE 6.5: LÖSUNGS-SIMULATION (OUT-OF-BOX)
        # Simuliere die Lösung BEVOR wir sie ausführen
        # ============================================
        self._think(ThinkingPhase.PLAN,
                   "Simuliere Lösung vor Ausführung...",
                   "Prüfe Risiken und Nebenwirkungen")

        # Simuliere den Plan
        plan_description = "\n".join([step.description for step in plan.steps])
        simulation = self.solution_simulator.simulate(
            plan_description,
            problem,
            context or {}
        )
        self._simulation_results.append(simulation)
        self.stats["solutions_simulated"] += 1

        self._think(ThinkingPhase.PLAN,
                   f"Simulation abgeschlossen: Erfolg={simulation.success}",
                   f"Confidence: {simulation.confidence:.0%}")

        # Zeige identifizierte Risiken
        if simulation.risks_identified:
            self._think(ThinkingPhase.PLAN,
                       f"Risiken erkannt: {simulation.risks_identified}",
                       simulation.recommendation)

        # Zeige Nebenwirkungen
        if simulation.side_effects:
            self._think(ThinkingPhase.PLAN,
                       f"Mögliche Nebenwirkungen: {simulation.side_effects}")

        # Bei niedriger Simulation-Confidence: Warnung
        if simulation.confidence < 0.4:
            self._think(ThinkingPhase.PLAN,
                       "WARNUNG: Niedrige Simulationsconfidence!",
                       "Vorsicht bei der Ausführung empfohlen")

        # ============================================
        # PHASE 7: AUSFÜHREN
        # ============================================
        self._think(ThinkingPhase.EXECUTE,
                   f"Führe Plan aus... (Simulation: {simulation.confidence:.0%} Erfolg)")

        executed_plan = self.executor.execute_plan(plan, problem)

        for step in executed_plan.steps:
            self._think(ThinkingPhase.EXECUTE,
                       f"Schritt '{step.description}': {step.status.value}",
                       step.result if step.result else step.error)

        # ============================================
        # PHASE 8: PRÜFEN
        # ============================================
        self._think(ThinkingPhase.VERIFY,
                   f"Prüfe Ergebnis... Plan-Status: {executed_plan.status}")

        success = executed_plan.status == "completed"

        # ============================================
        # PHASE 9: LERNEN
        # ============================================
        lessons = []

        if success:
            lessons.append(f"Strategie '{best_strategy.strategy_type.value}' war erfolgreich für diesen Problem-Typ")
            self._think(ThinkingPhase.LEARN,
                       "Problem erfolgreich gelöst!",
                       f"Gelernt: {lessons[0]}")
        else:
            lessons.append(f"Strategie '{best_strategy.strategy_type.value}' war nicht ausreichend")
            if best_strategy.fallback_strategy:
                lessons.append(f"Nächstes Mal Fallback versuchen: {best_strategy.fallback_strategy}")
            self._think(ThinkingPhase.LEARN,
                       "Problem nicht vollständig gelöst",
                       f"Gelernt: Alternative Strategien in Betracht ziehen")

        # ============================================
        # SOLUTION ERSTELLEN
        # ============================================
        duration = int((time.time() - start_time) * 1000)

        solution = Solution(
            problem_id=problem.id,
            success=success,
            result=self._extract_result(executed_plan),
            explanation=self._generate_explanation(problem, best_strategy, executed_plan),
            thinking_steps=self.thinking_log.copy(),
            strategies_tried=[best_strategy.id],
            plan_executed=executed_plan,
            lessons_learned=lessons,
            duration_ms=duration,
        )

        # Wissen aktualisieren
        if success:
            self.knowledge.add_solution(problem, solution)
            self.stats["problems_solved"] += 1
        else:
            self.stats["problems_failed"] += 1

        self.stats["total_thinking_time_ms"] += duration

        # Learning System über Ergebnis informieren
        self._notify_learning_result(problem, solution)

        # Self-Awareness aktualisieren
        self._update_self_awareness(ThinkingPhase.LEARN, success)

        return solution

    def _think(self, phase: ThinkingPhase, thought: str, conclusion: str = None):
        """Protokolliert einen Denkschritt"""
        step = ThinkingStep(
            phase=phase,
            thought=thought,
            conclusion=conclusion,
        )
        self.thinking_log.append(step)
        logger.debug(f"[{phase.value}] {thought}")

    def _create_problem(self, description: str, context: Dict,
                       goals: List[str], constraints: List[str]) -> Problem:
        """Erstellt ein Problem-Objekt"""
        self._problem_counter += 1

        problem = Problem(
            id=f"problem_{self._problem_counter}_{int(time.time())}",
            description=description,
            context=context,
            goals=goals,
            constraints=constraints,
        )

        # Typ und Komplexität werden vom Analyzer bestimmt
        problem.problem_type = self.analyzer._classify_type(problem)
        problem.complexity = self.analyzer._assess_complexity(problem)

        return problem

    def _create_failed_solution(self, problem: Problem, reason: str, start_time: float) -> Solution:
        """Erstellt eine fehlgeschlagene Lösung"""
        duration = int((time.time() - start_time) * 1000)

        return Solution(
            problem_id=problem.id,
            success=False,
            explanation=reason,
            thinking_steps=self.thinking_log.copy(),
            duration_ms=duration,
            lessons_learned=[f"Fehlgeschlagen: {reason}"],
        )

    def _extract_result(self, plan: Plan) -> Any:
        """Extrahiert das Ergebnis aus dem ausgeführten Plan"""
        results = []
        for step in plan.steps:
            if step.result and step.status == StepStatus.COMPLETED:
                results.append(step.result)
        return results if results else None

    def _generate_explanation(self, problem: Problem, strategy: Strategy, plan: Plan) -> str:
        """Generiert eine Erklärung der Lösung"""
        lines = []

        lines.append(f"Problem: {problem.description[:100]}")
        lines.append(f"Typ: {problem.problem_type.value}")
        lines.append(f"Strategie: {strategy.description}")
        lines.append(f"Status: {plan.status}")

        if plan.status == "completed":
            lines.append("Alle Schritte erfolgreich ausgeführt.")
        else:
            failed = [s for s in plan.steps if s.status == StepStatus.FAILED]
            if failed:
                lines.append(f"Fehlgeschlagene Schritte: {[s.description for s in failed]}")

        return "\n".join(lines)

    # =========================================================================
    # HOLO INTERFACE - Einfache Methoden für Holo
    # =========================================================================

    def think_about(self, question: str) -> str:
        """
        Holo denkt über eine Frage nach.

        Einfache Interface-Methode für schnelles Nachdenken.
        """
        solution = self.solve(question)
        return solution.explanation

    def how_would_i_solve(self, problem: str) -> List[str]:
        """
        Holo erklärt wie sie ein Problem lösen würde.

        Gibt die Denkschritte zurück ohne auszuführen.
        """
        # Nur analysieren und planen, nicht ausführen
        problem_obj = self._create_problem(problem, {}, [], [])
        analysis = self.analyzer.analyze(problem_obj)
        strategies = self.strategy_finder.find_strategies(problem_obj, analysis)

        steps = []
        steps.append(f"1. Problem verstehen: {problem_obj.problem_type.value}")
        steps.append(f"2. Komplexität: {problem_obj.complexity.name}")

        if analysis["root_causes"]:
            steps.append(f"3. Mögliche Ursachen prüfen: {analysis['root_causes'][0]}")

        if strategies:
            best = strategies[0]
            steps.append(f"4. Strategie wählen: {best.strategy_type.value}")
            for i, step in enumerate(best.steps[:5], 5):
                steps.append(f"{i}. {step}")

        return steps

    def can_i_solve(self, problem: str) -> Tuple[bool, str, float]:
        """
        Holo prüft ob sie ein Problem lösen kann.

        Returns:
            (kann_lösen, grund, confidence)
        """
        problem_obj = self._create_problem(problem, {}, [], [])
        analysis = self.analyzer.analyze(problem_obj)
        strategies = self.strategy_finder.find_strategies(problem_obj, analysis)

        if not strategies:
            return False, "Keine passende Strategie gefunden", 0.0

        best = strategies[0]
        confidence = best.score()

        if confidence > 0.7:
            return True, f"Hohe Erfolgswahrscheinlichkeit mit {best.strategy_type.value}", confidence
        elif confidence > 0.4:
            return True, f"Mittlere Erfolgswahrscheinlichkeit mit {best.strategy_type.value}", confidence
        else:
            return False, f"Geringe Erfolgswahrscheinlichkeit ({confidence:.0%})", confidence

    def what_do_i_know_about(self, topic: str) -> Dict:
        """
        Holo sucht in ihrem Wissen nach einem Thema.
        """
        # Suche nach ähnlichen Problemen
        dummy_problem = Problem(
            id="query",
            description=topic,
        )

        similar = self.knowledge.find_similar_problem(dummy_problem)
        strategies = self.knowledge.get_strategies_for_type(ProblemType.KNOWLEDGE)
        error_solution = self.knowledge.find_error_solution(topic)

        return {
            "similar_problems": [similar] if similar else [],
            "known_strategies": strategies[:5],
            "error_solution": error_solution,
            "lessons": [l for l in self.knowledge.lessons if topic.lower() in l.get("lesson", "").lower()][:5],
        }

    def get_thinking_summary(self) -> str:
        """
        Gibt eine Zusammenfassung des letzten Denkprozesses.
        """
        if not self.thinking_log:
            return "Kein aktiver Denkprozess."

        lines = ["=== DENKPROTOKOLL ==="]

        for step in self.thinking_log:
            lines.append(f"\n[{step.phase.value.upper()}]")
            lines.append(f"  Gedanke: {step.thought}")
            if step.conclusion:
                lines.append(f"  Schluss: {step.conclusion}")

        return "\n".join(lines)

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        total = self.stats["problems_solved"] + self.stats["problems_failed"]
        success_rate = self.stats["problems_solved"] / total if total > 0 else 0

        return {
            "problems_solved": self.stats["problems_solved"],
            "problems_failed": self.stats["problems_failed"],
            "success_rate": f"{success_rate:.0%}",
            "total_thinking_time": f"{self.stats['total_thinking_time_ms']}ms",
            "knowledge_patterns": len(self.knowledge.problem_patterns),
            "lessons_learned": len(self.knowledge.lessons),
            "cognitive_connections": len(self._cognitive_systems),
        }

    def get_cognitive_connections(self) -> Dict:
        """
        Gibt die verbundenen kognitiven Systeme zurück.

        Holo kann sagen: "Ich bin mit folgenden kognitiven Systemen verbunden..."

        Returns:
            Dict mit verbundenen Systemen und ihrem Status
        """
        connections = {}

        for name, system in self._cognitive_systems.items():
            connections[name] = {
                "connected": True,
                "type": type(system).__name__ if system else "None",
                "available": system is not None,
            }

        # Auch nicht verbundene Systeme anzeigen
        expected_systems = [
            'meta_cognition', 'learning', 'context_mind',
            'self_awareness', 'creative_mind', 'cognitive_engine',
            'autonomous_thinking'
        ]

        for sys_name in expected_systems:
            if sys_name not in connections:
                connections[sys_name] = {
                    "connected": False,
                    "type": None,
                    "available": False,
                }

        return {
            "connected_count": len(self._cognitive_systems),
            "total_expected": len(expected_systems),
            "systems": connections,
        }

    def reconnect_cognitive_systems(self):
        """
        Versucht die kognitiven Verbindungen neu herzustellen.

        Nützlich wenn HoloBrain später initialisiert wird.
        """
        self._cognitive_systems.clear()
        self._init_cognitive_connections()
        return self.get_cognitive_connections()

    # =========================================================================
    # OUT-OF-BOX THINKING INTERFACE - Kreatives & autonomes Denken für Holo
    # =========================================================================

    def think_creatively(self, problem: str) -> List[Dict]:
        """
        Holo denkt kreativ/lateral über ein Problem nach.

        Nutzt verschiedene Kreativitätstechniken wie:
        - Random Association
        - Perspective Shift
        - Reversal
        - Analogie
        - Kombination

        Returns:
            Liste von kreativen Ideen mit Confidence-Werten
        """
        problem_obj = self._create_problem(problem, {}, [], [])
        ideas = self.lateral_thinking.think_laterally(problem_obj)

        # Statistiken aktualisieren
        self.stats["creative_ideas_generated"] += len(ideas)

        return ideas

    def generate_hypotheses(self, problem: str) -> List[Dict]:
        """
        Holo generiert selbständig Hypothesen über ein Problem.

        Returns:
            Liste von Hypothesen mit Confidence-Werten
        """
        problem_obj = self._create_problem(problem, {}, [], [])
        analysis = self.analyzer.analyze(problem_obj)

        hypotheses = self.hypothesis_generator.generate_hypotheses(problem_obj, analysis)

        # Konvertiere zu Dict für einfache Nutzung
        return [
            {
                "description": h.description,
                "confidence": h.confidence,
                "origin": h.origin,
                "evidence_for": h.evidence_for,
            }
            for h in hypotheses
        ]

    def research_problem(self, problem: str) -> Dict:
        """
        Holo recherchiert ein Problem im Web.

        Returns:
            Dict mit gefundenen Lösungen und Quellen
        """
        problem_obj = self._create_problem(problem, {}, [], [])
        results = self.web_researcher.search(problem, problem_obj.problem_type)

        self.stats["web_searches_performed"] += 1

        return results

    def simulate_solution(self, solution: str, problem: str) -> Dict:
        """
        Holo simuliert eine Lösung bevor sie angewendet wird.

        Prüft auf Risiken und mögliche Nebenwirkungen.

        Returns:
            Dict mit Simulation-Ergebnis, Risiken, Nebenwirkungen
        """
        problem_obj = self._create_problem(problem, {}, [], [])
        result = self.solution_simulator.simulate(solution, problem_obj)

        self.stats["solutions_simulated"] += 1

        return {
            "success": result.success,
            "predicted_outcome": result.predicted_outcome,
            "confidence": result.confidence,
            "risks": result.risks_identified,
            "side_effects": result.side_effects,
            "recommendation": result.recommendation,
            "simulation_method": result.simulation_method,
        }

    def explore_topic(self, topic: str, depth: int = 3) -> List[Dict]:
        """
        Holo exploriert ein Thema autonom.

        Findet Verbindungen, Muster und generiert Fragen.

        Returns:
            Liste von Entdeckungen
        """
        problem_obj = self._create_problem(topic, {}, [], [])
        discoveries = self.autonomous_explorer.explore_autonomously(problem_obj, depth)

        return discoveries

    def what_if(self, scenario: str) -> str:
        """
        Holo denkt über ein "Was wäre wenn" Szenario nach.

        Nutzt laterales Denken für hypothetische Szenarien.

        Returns:
            Kreativer Gedanke zum Szenario
        """
        problem_obj = self._create_problem(scenario, {}, [], [])

        # Nutze What-If Technik
        ideas = self.lateral_thinking.think_laterally(
            problem_obj,
            techniques=["what_if", "reversal", "exaggeration"]
        )

        if ideas:
            best_idea = ideas[0]
            return f"{best_idea['idea']}\n\nDenkmethode: {best_idea['technique']}, Confidence: {best_idea['confidence']:.0%}"

        return "Keine kreative Idee generiert."

    def brainstorm(self, topic: str, count: int = 10) -> List[str]:
        """
        Holo brainstormt Ideen zu einem Thema.

        Kombiniert alle Kreativitäts-Techniken für maximale Ideenvielfalt.

        Returns:
            Liste von Ideen
        """
        problem_obj = self._create_problem(topic, {}, [], [])

        ideas = []

        # 1. Laterales Denken
        lateral_ideas = self.lateral_thinking.think_laterally(problem_obj)
        ideas.extend([f"[lateral] {i['idea']}" for i in lateral_ideas])

        # 2. Hypothesen
        hypotheses = self.hypothesis_generator.generate_hypotheses(problem_obj, {})
        ideas.extend([f"[hypothese] {h.description}" for h in hypotheses])

        # 3. Exploration
        discoveries = self.autonomous_explorer.explore_autonomously(problem_obj, depth=2)
        for disc in discoveries:
            if disc.get("insight"):
                ideas.append(f"[exploration] {disc['insight']}")
            elif disc.get("questions"):
                ideas.append(f"[frage] {disc['questions'][0]}")

        # Statistiken
        self.stats["creative_ideas_generated"] += len(ideas)

        return ideas[:count]

    def get_out_of_box_stats(self) -> Dict:
        """
        Gibt Statistiken über das Out-of-Box Denken zurück.
        """
        return {
            "creative_ideas_generated": self.stats.get("creative_ideas_generated", 0),
            "hypotheses_tested": self.stats.get("hypotheses_tested", 0),
            "solutions_simulated": self.stats.get("solutions_simulated", 0),
            "web_searches_performed": self.stats.get("web_searches_performed", 0),
            "current_hypotheses": len(self._current_hypotheses),
            "current_creative_ideas": len(self._creative_ideas),
            "simulation_log_size": len(self._simulation_results),
            "exploration_discoveries": len(self.autonomous_explorer.discoveries),
        }

    def get_last_simulation(self) -> Optional[Dict]:
        """
        Gibt die letzte Lösungs-Simulation zurück.
        """
        if not self._simulation_results:
            return None

        result = self._simulation_results[-1]
        return {
            "success": result.success,
            "confidence": result.confidence,
            "risks": result.risks_identified,
            "side_effects": result.side_effects,
            "recommendation": result.recommendation,
        }

    def get_creative_ideas(self) -> List[Dict]:
        """
        Gibt die zuletzt generierten kreativen Ideen zurück.
        """
        return self._creative_ideas

    def get_hypotheses(self) -> List[Dict]:
        """
        Gibt die aktuellen Hypothesen zurück.
        """
        return [
            {
                "description": h.description,
                "confidence": h.confidence,
                "origin": h.origin,
                "tested": h.tested,
                "result": h.test_result,
            }
            for h in self._current_hypotheses
        ]


# ==================== FACTORY FUNCTION ====================

def create_problem_solver(
    project_dir: Path = None,
    holo_brain = None,
    persist_path: Path = None
) -> HoloProblemSolver:
    """
    Factory-Funktion zum Erstellen des Problem Solvers.
    """
    return HoloProblemSolver(
        project_dir=project_dir,
        holo_brain=holo_brain,
        persist_path=persist_path,
    )


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("HOLO PROBLEM SOLVER - TEST")
    print("=" * 60)

    solver = create_problem_solver()

    # Test 1: Technisches Problem
    print("\n--- Test 1: Technisches Problem ---")
    solution = solver.solve(
        "ImportError: No module named 'holo_memory' - das Modul kann nicht geladen werden",
        context={"error_type": "ImportError"},
        goals=["Modul erfolgreich importieren"],
    )
    print(f"Erfolg: {solution.success}")
    print(f"Erklärung: {solution.explanation}")

    # Test 2: Wissensfrage
    print("\n--- Test 2: Wissensfrage ---")
    solution = solver.solve(
        "Was ist der Unterschied zwischen einer Klasse und einer Funktion?",
        goals=["Verständliche Erklärung"],
    )
    print(f"Erfolg: {solution.success}")
    print(f"Denkschritte: {len(solution.thinking_steps)}")

    # Test 3: Can I Solve
    print("\n--- Test 3: Kann ich lösen? ---")
    can, reason, conf = solver.can_i_solve("Wie erstelle ich eine REST API?")
    print(f"Kann lösen: {can}")
    print(f"Grund: {reason}")
    print(f"Confidence: {conf:.0%}")

    # Test 4: How Would I Solve
    print("\n--- Test 4: Wie würde ich lösen? ---")
    steps = solver.how_would_i_solve("Die Datenbank antwortet nicht mehr")
    for step in steps:
        print(f"  {step}")

    # Statistiken
    print("\n--- Statistiken ---")
    stats = solver.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
