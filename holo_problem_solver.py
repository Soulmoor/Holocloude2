"""
Holo Problem Solver - Universelles Analytisches Denken
======================================================

Ein allgemeines Problem-Solving Framework für Holo.
Wird aktiviert wenn Holo bei IRGENDEINEM Problem nicht weiterkommt.

Denk-Prozess:
1. VERSTEHEN   - Was ist das Problem genau?
2. ZERLEGEN    - Kann ich es in Teilprobleme aufteilen?
3. ANALYSIEREN - Was sind die Ursachen? Was hängt zusammen?
4. WISSEN      - Was weiß ich schon? Was muss ich herausfinden?
5. STRATEGIEN  - Welche Lösungswege gibt es?
6. BEWERTEN    - Welche Strategie ist am besten?
7. PLANEN      - Welche Schritte in welcher Reihenfolge?
8. AUSFÜHREN   - Mit Monitoring und Anpassung
9. PRÜFEN      - Hat es funktioniert?
10. LERNEN     - Was merke ich mir für nächstes Mal?

Autor: Claude (Anthropic) für Holo
Version: 1.0.0
"""

import os
import re
import json
import time
import logging
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from collections import defaultdict
import traceback


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

        # State
        self.current_problem: Optional[Problem] = None
        self.thinking_log: List[ThinkingStep] = []
        self._problem_counter = 0

        # Statistiken
        self.stats = {
            "problems_solved": 0,
            "problems_failed": 0,
            "total_thinking_time_ms": 0,
        }

        logger.info("HoloProblemSolver initialisiert")

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

        # ============================================
        # PHASE 1: VERSTEHEN
        # ============================================
        self._think(ThinkingPhase.UNDERSTAND,
                   f"Was ist das Problem? '{problem_description[:100]}...'")

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
        # PHASE 3: WISSEN SAMMELN
        # ============================================
        if analysis["missing_information"]:
            self._think(ThinkingPhase.GATHER_KNOWLEDGE,
                       f"Fehlende Infos: {analysis['missing_information']}",
                       "Muss eventuell nachfragen oder recherchieren")

        # ============================================
        # PHASE 4: STRATEGIEN FINDEN
        # ============================================
        self._think(ThinkingPhase.FIND_STRATEGIES,
                   "Suche nach möglichen Lösungsstrategien...")

        strategies = self.strategy_finder.find_strategies(problem, analysis)

        self._think(ThinkingPhase.FIND_STRATEGIES,
                   f"Gefundene Strategien: {[s.strategy_type.value for s in strategies]}",
                   f"{len(strategies)} Strategien zur Auswahl")

        # ============================================
        # PHASE 5: BEWERTEN
        # ============================================
        self._think(ThinkingPhase.EVALUATE,
                   "Bewerte Strategien nach Erfolgswahrscheinlichkeit und Aufwand...")

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
        # PHASE 7: AUSFÜHREN
        # ============================================
        self._think(ThinkingPhase.EXECUTE,
                   "Führe Plan aus...")

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
        }


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
