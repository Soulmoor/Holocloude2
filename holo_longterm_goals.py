"""
holo_longterm_goals.py - Langfristige Zielverfolgung und Planung

Dieses Modul implementiert die Fähigkeit:
- Langfristige Ziele zu setzen und zu verfolgen (Monate/Jahre)
- Meilensteine und Zwischenziele zu definieren
- Fortschritt zu tracken und anzupassen
- Motivation über lange Zeiträume aufrechtzuerhalten
- Zielkonflikte zu erkennen und zu lösen

Autor: Holocloude System
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import json
import math
import random

# ============================================================================
# ENUMS UND TYPEN
# ============================================================================

class GoalTimeframe(Enum):
    """Zeitrahmen für Ziele"""
    IMMEDIATE = "immediate"       # < 1 Tag
    SHORT_TERM = "short_term"     # 1 Tag - 1 Woche
    MEDIUM_TERM = "medium_term"   # 1 Woche - 1 Monat
    LONG_TERM = "long_term"       # 1-6 Monate
    VERY_LONG_TERM = "very_long_term"  # 6-12 Monate
    LIFE_GOAL = "life_goal"       # > 1 Jahr / Lebensziel


class GoalStatus(Enum):
    """Status eines Ziels"""
    DRAFT = "draft"               # Noch nicht aktiv
    ACTIVE = "active"             # Aktiv verfolgt
    ON_HOLD = "on_hold"           # Pausiert
    BLOCKED = "blocked"           # Blockiert
    PROGRESSING = "progressing"   # Macht Fortschritte
    AT_RISK = "at_risk"           # Gefährdet
    COMPLETED = "completed"       # Abgeschlossen
    ABANDONED = "abandoned"       # Aufgegeben
    SUPERSEDED = "superseded"     # Ersetzt durch anderes Ziel


class GoalCategory(Enum):
    """Kategorien von Zielen"""
    PERSONAL_GROWTH = "personal_growth"     # Persönliche Entwicklung
    LEARNING = "learning"                   # Lernen/Wissen
    RELATIONSHIP = "relationship"           # Beziehungen
    HEALTH = "health"                       # Gesundheit
    CAREER = "career"                       # Karriere
    CREATIVE = "creative"                   # Kreativität
    FINANCIAL = "financial"                 # Finanzen
    LIFESTYLE = "lifestyle"                 # Lebensstil
    CONTRIBUTION = "contribution"           # Beitrag/Helfen
    EXPERIENCE = "experience"               # Erfahrungen
    SELF_IMPROVEMENT = "self_improvement"   # Selbstverbesserung


class PriorityLevel(Enum):
    """Prioritätsstufen"""
    CRITICAL = "critical"         # Höchste Priorität
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"         # Nice-to-have


class MilestoneStatus(Enum):
    """Status eines Meilensteins"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    DELAYED = "delayed"


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class Milestone:
    """Ein Meilenstein auf dem Weg zum Ziel"""
    id: str
    title: str
    description: str
    target_date: datetime
    status: MilestoneStatus = MilestoneStatus.PENDING
    completion_date: Optional[datetime] = None
    progress: float = 0.0  # 0.0 - 1.0
    dependencies: List[str] = field(default_factory=list)  # IDs anderer Milestones
    notes: List[str] = field(default_factory=list)

    @property
    def is_overdue(self) -> bool:
        return datetime.now() > self.target_date and self.status != MilestoneStatus.COMPLETED

    @property
    def days_until_due(self) -> int:
        return (self.target_date - datetime.now()).days

    def complete(self):
        """Markiert Meilenstein als abgeschlossen"""
        self.status = MilestoneStatus.COMPLETED
        self.completion_date = datetime.now()
        self.progress = 1.0


@dataclass
class LongTermGoal:
    """Ein langfristiges Ziel"""
    id: str
    title: str
    description: str
    category: GoalCategory
    timeframe: GoalTimeframe
    priority: PriorityLevel
    status: GoalStatus = GoalStatus.DRAFT

    # Zeitplanung
    created_date: datetime = field(default_factory=datetime.now)
    target_date: Optional[datetime] = None
    deadline: Optional[datetime] = None  # Harte Deadline falls vorhanden

    # Fortschritt
    progress: float = 0.0  # 0.0 - 1.0
    milestones: List[Milestone] = field(default_factory=list)

    # Motivation
    why: Optional[str] = None  # Warum ist dieses Ziel wichtig?
    vision: Optional[str] = None  # Wie sieht Erfolg aus?
    motivation_score: float = 0.8  # Aktuelle Motivation

    # Reflexion
    last_review: Optional[datetime] = None
    review_notes: List[str] = field(default_factory=list)

    # Hindernisse und Ressourcen
    obstacles: List[str] = field(default_factory=list)
    resources_needed: List[str] = field(default_factory=list)
    resources_available: List[str] = field(default_factory=list)

    # Beziehungen zu anderen Zielen
    parent_goal_id: Optional[str] = None
    sub_goal_ids: List[str] = field(default_factory=list)
    conflicting_goal_ids: List[str] = field(default_factory=list)
    supporting_goal_ids: List[str] = field(default_factory=list)

    # Metriken
    success_metrics: List[str] = field(default_factory=list)
    key_results: Dict[str, float] = field(default_factory=dict)  # OKR-Style

    @property
    def is_active(self) -> bool:
        return self.status in [GoalStatus.ACTIVE, GoalStatus.PROGRESSING]

    @property
    def is_at_risk(self) -> bool:
        if not self.target_date:
            return False
        days_remaining = (self.target_date - datetime.now()).days
        expected_progress = 1 - (days_remaining / max(1, self._total_days()))
        return self.progress < expected_progress * 0.7

    @property
    def completion_rate(self) -> float:
        """Berechnet die Abschlussrate basierend auf Meilensteinen"""
        if not self.milestones:
            return self.progress
        completed = sum(1 for m in self.milestones if m.status == MilestoneStatus.COMPLETED)
        return completed / len(self.milestones)

    def _total_days(self) -> int:
        """Gesamte geplante Dauer in Tagen"""
        if not self.target_date:
            return 365  # Default 1 Jahr
        return max(1, (self.target_date - self.created_date).days)


@dataclass
class GoalReview:
    """Regelmäßige Überprüfung eines Ziels"""
    goal_id: str
    review_date: datetime
    progress_assessment: float
    motivation_level: float
    obstacles_encountered: List[str]
    lessons_learned: List[str]
    adjustments_made: List[str]
    next_actions: List[str]
    overall_sentiment: str  # "positive", "neutral", "negative"


@dataclass
class GoalConflict:
    """Ein Konflikt zwischen Zielen"""
    goal1_id: str
    goal2_id: str
    conflict_type: str  # "resource", "time", "priority", "philosophical"
    severity: float  # 0.0 - 1.0
    description: str
    resolution_options: List[str]


@dataclass
class ProgressEntry:
    """Ein Fortschrittseintrag"""
    goal_id: str
    timestamp: datetime
    progress_delta: float
    milestone_id: Optional[str] = None
    description: Optional[str] = None
    mood: Optional[str] = None


# ============================================================================
# HAUPTKLASSE: LONGTERM GOALS ENGINE
# ============================================================================

class LongTermGoalsEngine:
    """
    Engine für die Verwaltung langfristiger Ziele.

    Features:
    - Ziele über Monate/Jahre verfolgen
    - Meilensteine und Zwischenziele
    - Fortschrittstracking
    - Motivation aufrechterhalten
    - Zielkonflikte lösen
    """

    def __init__(self):
        self.goals: Dict[str, LongTermGoal] = {}
        self.reviews: List[GoalReview] = []
        self.progress_history: List[ProgressEntry] = []
        self.conflicts: List[GoalConflict] = []
        self._id_counter = 0

    # -------------------------------------------------------------------------
    # Ziel-Erstellung und -Verwaltung
    # -------------------------------------------------------------------------

    def create_goal(
        self,
        title: str,
        description: str,
        category: GoalCategory,
        timeframe: GoalTimeframe,
        target_date: Optional[datetime] = None,
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        why: Optional[str] = None,
        vision: Optional[str] = None
    ) -> LongTermGoal:
        """
        Erstellt ein neues langfristiges Ziel.

        Args:
            title: Titel des Ziels
            description: Ausführliche Beschreibung
            category: Kategorie des Ziels
            timeframe: Zeitrahmen
            target_date: Zieldatum (optional)
            priority: Priorität
            why: Warum ist das Ziel wichtig?
            vision: Wie sieht Erfolg aus?

        Returns:
            Das erstellte Ziel
        """
        self._id_counter += 1
        goal_id = f"goal_{self._id_counter:04d}"

        # Berechne Standardzieldatum basierend auf Timeframe
        if not target_date:
            target_date = self._calculate_default_target(timeframe)

        goal = LongTermGoal(
            id=goal_id,
            title=title,
            description=description,
            category=category,
            timeframe=timeframe,
            priority=priority,
            target_date=target_date,
            why=why,
            vision=vision,
            status=GoalStatus.DRAFT
        )

        self.goals[goal_id] = goal
        return goal

    def activate_goal(self, goal_id: str) -> bool:
        """Aktiviert ein Ziel zur Verfolgung"""
        if goal_id not in self.goals:
            return False

        goal = self.goals[goal_id]
        goal.status = GoalStatus.ACTIVE
        return True

    def add_milestone(
        self,
        goal_id: str,
        title: str,
        description: str,
        target_date: datetime,
        dependencies: Optional[List[str]] = None
    ) -> Optional[Milestone]:
        """
        Fügt einen Meilenstein zu einem Ziel hinzu.

        Args:
            goal_id: ID des Ziels
            title: Titel des Meilensteins
            description: Beschreibung
            target_date: Zieldatum
            dependencies: Abhängige Meilenstein-IDs

        Returns:
            Der erstellte Meilenstein
        """
        if goal_id not in self.goals:
            return None

        goal = self.goals[goal_id]
        milestone_id = f"{goal_id}_ms_{len(goal.milestones) + 1:02d}"

        milestone = Milestone(
            id=milestone_id,
            title=title,
            description=description,
            target_date=target_date,
            dependencies=dependencies or []
        )

        goal.milestones.append(milestone)
        return milestone

    def complete_milestone(
        self,
        goal_id: str,
        milestone_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Markiert einen Meilenstein als abgeschlossen"""
        if goal_id not in self.goals:
            return False

        goal = self.goals[goal_id]
        for milestone in goal.milestones:
            if milestone.id == milestone_id:
                milestone.complete()
                if notes:
                    milestone.notes.append(notes)

                # Aktualisiere Zielfortschritt
                self._update_goal_progress(goal)
                return True

        return False

    def update_progress(
        self,
        goal_id: str,
        progress_delta: float,
        description: Optional[str] = None,
        milestone_id: Optional[str] = None
    ) -> bool:
        """
        Aktualisiert den Fortschritt eines Ziels.

        Args:
            goal_id: ID des Ziels
            progress_delta: Fortschrittsänderung (-1.0 bis 1.0)
            description: Beschreibung der Änderung
            milestone_id: Optional - zugehöriger Meilenstein

        Returns:
            True wenn erfolgreich
        """
        if goal_id not in self.goals:
            return False

        goal = self.goals[goal_id]
        goal.progress = max(0.0, min(1.0, goal.progress + progress_delta))

        # Logging
        entry = ProgressEntry(
            goal_id=goal_id,
            timestamp=datetime.now(),
            progress_delta=progress_delta,
            milestone_id=milestone_id,
            description=description
        )
        self.progress_history.append(entry)

        # Status aktualisieren
        self._update_goal_status(goal)

        return True

    # -------------------------------------------------------------------------
    # Ziel-Hierarchie
    # -------------------------------------------------------------------------

    def create_sub_goal(
        self,
        parent_goal_id: str,
        title: str,
        description: str,
        timeframe: GoalTimeframe = GoalTimeframe.MEDIUM_TERM
    ) -> Optional[LongTermGoal]:
        """
        Erstellt ein Unterziel für ein bestehendes Ziel.

        Args:
            parent_goal_id: ID des übergeordneten Ziels
            title: Titel des Unterziels
            description: Beschreibung

        Returns:
            Das erstellte Unterziel
        """
        if parent_goal_id not in self.goals:
            return None

        parent = self.goals[parent_goal_id]

        sub_goal = self.create_goal(
            title=title,
            description=description,
            category=parent.category,
            timeframe=timeframe,
            priority=PriorityLevel.MEDIUM
        )

        sub_goal.parent_goal_id = parent_goal_id
        parent.sub_goal_ids.append(sub_goal.id)

        return sub_goal

    def get_goal_hierarchy(self, goal_id: str) -> Dict[str, Any]:
        """
        Gibt die Hierarchie eines Ziels zurück.

        Returns:
            Dict mit Eltern- und Unterzielen
        """
        if goal_id not in self.goals:
            return {}

        goal = self.goals[goal_id]

        hierarchy = {
            "goal": self._goal_summary(goal),
            "parent": None,
            "sub_goals": []
        }

        if goal.parent_goal_id and goal.parent_goal_id in self.goals:
            hierarchy["parent"] = self._goal_summary(self.goals[goal.parent_goal_id])

        for sub_id in goal.sub_goal_ids:
            if sub_id in self.goals:
                hierarchy["sub_goals"].append(self._goal_summary(self.goals[sub_id]))

        return hierarchy

    # -------------------------------------------------------------------------
    # Review und Reflexion
    # -------------------------------------------------------------------------

    def conduct_review(
        self,
        goal_id: str,
        motivation_level: float,
        obstacles: List[str],
        lessons: List[str],
        adjustments: List[str],
        next_actions: List[str]
    ) -> GoalReview:
        """
        Führt eine Überprüfung eines Ziels durch.

        Args:
            goal_id: ID des Ziels
            motivation_level: Aktuelle Motivation (0.0 - 1.0)
            obstacles: Aufgetretene Hindernisse
            lessons: Gelernte Lektionen
            adjustments: Vorgenommene Anpassungen
            next_actions: Nächste Schritte

        Returns:
            GoalReview-Objekt
        """
        if goal_id not in self.goals:
            raise ValueError(f"Goal {goal_id} not found")

        goal = self.goals[goal_id]

        # Bestimme Sentiment
        if goal.progress >= 0.8 and motivation_level >= 0.7:
            sentiment = "positive"
        elif goal.is_at_risk or motivation_level < 0.4:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        review = GoalReview(
            goal_id=goal_id,
            review_date=datetime.now(),
            progress_assessment=goal.progress,
            motivation_level=motivation_level,
            obstacles_encountered=obstacles,
            lessons_learned=lessons,
            adjustments_made=adjustments,
            next_actions=next_actions,
            overall_sentiment=sentiment
        )

        # Update goal
        goal.last_review = datetime.now()
        goal.motivation_score = motivation_level
        goal.obstacles.extend(obstacles)
        goal.review_notes.append(f"Review {review.review_date.date()}: {sentiment}")

        self.reviews.append(review)
        return review

    def get_review_schedule(self) -> Dict[str, datetime]:
        """
        Gibt den empfohlenen Review-Zeitplan zurück.

        Returns:
            Dict mit goal_id -> nächstes Review-Datum
        """
        schedule = {}

        for goal_id, goal in self.goals.items():
            if not goal.is_active:
                continue

            # Review-Intervall basierend auf Timeframe
            interval_days = {
                GoalTimeframe.IMMEDIATE: 1,
                GoalTimeframe.SHORT_TERM: 3,
                GoalTimeframe.MEDIUM_TERM: 7,
                GoalTimeframe.LONG_TERM: 14,
                GoalTimeframe.VERY_LONG_TERM: 30,
                GoalTimeframe.LIFE_GOAL: 30
            }.get(goal.timeframe, 14)

            last = goal.last_review or goal.created_date
            next_review = last + timedelta(days=interval_days)

            schedule[goal_id] = next_review

        return schedule

    def generate_reflection_prompts(self, goal_id: str) -> List[str]:
        """
        Generiert Reflexionsfragen für ein Ziel.

        Returns:
            Liste von Reflexionsfragen
        """
        if goal_id not in self.goals:
            return []

        goal = self.goals[goal_id]
        prompts = [
            f"Warum ist '{goal.title}' immer noch wichtig für mich?",
            f"Was habe ich in der letzten Zeit für dieses Ziel getan?",
            f"Welche Hindernisse stehen mir im Weg?",
            f"Was ist der nächste kleine Schritt, den ich machen kann?",
            f"Wie werde ich mich fühlen, wenn ich dieses Ziel erreiche?"
        ]

        # Anpassung basierend auf Status
        if goal.is_at_risk:
            prompts.append("Was muss sich ändern, damit ich dieses Ziel erreiche?")
            prompts.append("Ist dieses Ziel noch realistisch?")

        if goal.motivation_score < 0.5:
            prompts.append("Was hat mich ursprünglich zu diesem Ziel motiviert?")
            prompts.append("Gibt es einen anderen Weg, das gleiche Bedürfnis zu erfüllen?")

        return prompts

    # -------------------------------------------------------------------------
    # Konflikt-Erkennung und -Lösung
    # -------------------------------------------------------------------------

    def detect_conflicts(self) -> List[GoalConflict]:
        """
        Erkennt Konflikte zwischen aktiven Zielen.

        Returns:
            Liste von GoalConflict-Objekten
        """
        conflicts = []
        active_goals = [g for g in self.goals.values() if g.is_active]

        for i, goal1 in enumerate(active_goals):
            for goal2 in active_goals[i+1:]:
                conflict = self._check_conflict(goal1, goal2)
                if conflict:
                    conflicts.append(conflict)

        self.conflicts = conflicts
        return conflicts

    def _check_conflict(
        self,
        goal1: LongTermGoal,
        goal2: LongTermGoal
    ) -> Optional[GoalConflict]:
        """Prüft ob zwei Ziele in Konflikt stehen"""

        # Zeitkonflikt: Beide haben enge Deadlines
        time_conflict = False
        if goal1.target_date and goal2.target_date:
            days1 = (goal1.target_date - datetime.now()).days
            days2 = (goal2.target_date - datetime.now()).days
            if days1 < 30 and days2 < 30 and goal1.priority == goal2.priority:
                time_conflict = True

        # Ressourcenkonflikt: Ähnliche Ressourcen benötigt
        resource_conflict = False
        shared_resources = set(goal1.resources_needed) & set(goal2.resources_needed)
        if len(shared_resources) >= 2:
            resource_conflict = True

        # Kategoriekonflikt: Work-Life-Balance
        category_conflict = False
        work_categories = {GoalCategory.CAREER, GoalCategory.FINANCIAL}
        life_categories = {GoalCategory.HEALTH, GoalCategory.RELATIONSHIP, GoalCategory.LIFESTYLE}
        if goal1.category in work_categories and goal2.category in life_categories:
            if goal1.priority == PriorityLevel.HIGH and goal2.priority == PriorityLevel.HIGH:
                category_conflict = True

        if time_conflict or resource_conflict or category_conflict:
            conflict_type = "time" if time_conflict else "resource" if resource_conflict else "priority"
            severity = 0.7 if time_conflict else 0.5 if resource_conflict else 0.4

            return GoalConflict(
                goal1_id=goal1.id,
                goal2_id=goal2.id,
                conflict_type=conflict_type,
                severity=severity,
                description=f"Konflikt zwischen '{goal1.title}' und '{goal2.title}'",
                resolution_options=self._generate_resolution_options(conflict_type)
            )

        return None

    def _generate_resolution_options(self, conflict_type: str) -> List[str]:
        """Generiert Lösungsoptionen für einen Konflikt"""
        options = {
            "time": [
                "Prioritäten neu bewerten",
                "Ein Ziel verschieben",
                "Beide Ziele in kleinere Schritte aufteilen",
                "Mehr Zeit für beide einplanen"
            ],
            "resource": [
                "Ressourcen aufteilen",
                "Zusätzliche Ressourcen beschaffen",
                "Ein Ziel pausieren",
                "Synergien finden"
            ],
            "priority": [
                "Work-Life-Balance überdenken",
                "Grenzen setzen",
                "Zeitfenster für jedes Ziel definieren",
                "Unterstützung suchen"
            ]
        }
        return options.get(conflict_type, ["Situation analysieren", "Prioritäten klären"])

    # -------------------------------------------------------------------------
    # Motivation und Fortschritts-Tracking
    # -------------------------------------------------------------------------

    def get_motivation_boosters(self, goal_id: str) -> List[str]:
        """
        Generiert motivierende Nachrichten für ein Ziel.

        Returns:
            Liste von Motivations-Boostern
        """
        if goal_id not in self.goals:
            return []

        goal = self.goals[goal_id]
        boosters = []

        # Fortschritts-basiert
        if goal.progress > 0:
            percent = int(goal.progress * 100)
            boosters.append(f"Du hast bereits {percent}% geschafft!")

        # Meilenstein-basiert
        completed_ms = sum(1 for m in goal.milestones if m.status == MilestoneStatus.COMPLETED)
        if completed_ms > 0:
            boosters.append(f"Du hast schon {completed_ms} Meilenstein(e) erreicht!")

        # Vision-basiert
        if goal.vision:
            boosters.append(f"Stell dir vor: {goal.vision}")

        # Why-basiert
        if goal.why:
            boosters.append(f"Denk daran, warum: {goal.why}")

        # Allgemeine Motivation
        boosters.extend([
            "Jeder kleine Schritt zählt",
            "Du bist auf dem richtigen Weg",
            "Konsistenz schlägt Perfektion"
        ])

        return boosters

    def calculate_momentum(self, goal_id: str) -> Dict[str, Any]:
        """
        Berechnet das Momentum (Schwung) für ein Ziel.

        Returns:
            Dict mit Momentum-Metriken
        """
        if goal_id not in self.goals:
            return {}

        goal = self.goals[goal_id]

        # Sammle Fortschritts-Historie
        history = [e for e in self.progress_history if e.goal_id == goal_id]

        if len(history) < 2:
            return {
                "momentum": 0.5,
                "trend": "neutral",
                "consistency": 0.5,
                "recent_activity": False
            }

        # Berechne Trend (letzte 7 Tage vs. davor)
        week_ago = datetime.now() - timedelta(days=7)
        recent = [e.progress_delta for e in history if e.timestamp > week_ago]
        older = [e.progress_delta for e in history if e.timestamp <= week_ago]

        recent_avg = sum(recent) / len(recent) if recent else 0
        older_avg = sum(older) / len(older) if older else 0

        if recent_avg > older_avg * 1.2:
            trend = "accelerating"
            momentum = 0.8
        elif recent_avg < older_avg * 0.8:
            trend = "slowing"
            momentum = 0.3
        else:
            trend = "steady"
            momentum = 0.5

        # Konsistenz: Wie regelmäßig wird gearbeitet?
        if len(history) >= 5:
            days_between = []
            for i in range(1, len(history)):
                delta = (history[i].timestamp - history[i-1].timestamp).days
                days_between.append(delta)
            avg_gap = sum(days_between) / len(days_between) if days_between else 30
            consistency = max(0, 1 - (avg_gap / 14))  # 14 Tage als Maximum
        else:
            consistency = 0.5

        # Aktuelle Aktivität
        recent_activity = len(recent) > 0

        return {
            "momentum": momentum,
            "trend": trend,
            "consistency": consistency,
            "recent_activity": recent_activity,
            "recent_progress_count": len(recent),
            "total_progress_entries": len(history)
        }

    def suggest_next_actions(self, goal_id: str) -> List[str]:
        """
        Schlägt nächste Aktionen für ein Ziel vor.

        Returns:
            Liste von vorgeschlagenen Aktionen
        """
        if goal_id not in self.goals:
            return []

        goal = self.goals[goal_id]
        actions = []

        # Basierend auf Meilensteinen
        pending_ms = [m for m in goal.milestones
                     if m.status == MilestoneStatus.PENDING]
        if pending_ms:
            next_ms = min(pending_ms, key=lambda m: m.target_date)
            actions.append(f"Nächster Meilenstein: {next_ms.title}")

            # Abhängigkeiten prüfen
            for dep_id in next_ms.dependencies:
                for m in goal.milestones:
                    if m.id == dep_id and m.status != MilestoneStatus.COMPLETED:
                        actions.insert(0, f"Zuerst: {m.title} abschließen")

        # Basierend auf Status
        if goal.status == GoalStatus.BLOCKED:
            actions.append("Blockade analysieren und lösen")
        elif goal.is_at_risk:
            actions.append("Review durchführen und Plan anpassen")
        elif goal.motivation_score < 0.5:
            actions.append("Motivation auffrischen - Why erinnern")

        # Basierend auf Momentum
        momentum = self.calculate_momentum(goal_id)
        if momentum.get("trend") == "slowing":
            actions.append("Kleine, schnelle Erfolge einplanen")
        elif not momentum.get("recent_activity"):
            actions.append("Heute einen kleinen Schritt machen")

        # Ressourcen
        missing = set(goal.resources_needed) - set(goal.resources_available)
        if missing:
            actions.append(f"Fehlende Ressourcen: {', '.join(list(missing)[:2])}")

        return actions[:5]  # Max 5 Aktionen

    # -------------------------------------------------------------------------
    # Statistiken und Übersicht
    # -------------------------------------------------------------------------

    def get_goals_overview(self) -> Dict[str, Any]:
        """
        Gibt eine Übersicht aller Ziele zurück.

        Returns:
            Dict mit Statistiken
        """
        total = len(self.goals)
        active = sum(1 for g in self.goals.values() if g.is_active)
        completed = sum(1 for g in self.goals.values()
                       if g.status == GoalStatus.COMPLETED)
        at_risk = sum(1 for g in self.goals.values() if g.is_at_risk)

        # Nach Kategorie
        by_category = defaultdict(int)
        for goal in self.goals.values():
            by_category[goal.category.value] += 1

        # Nach Timeframe
        by_timeframe = defaultdict(int)
        for goal in self.goals.values():
            by_timeframe[goal.timeframe.value] += 1

        # Durchschnittlicher Fortschritt
        active_goals = [g for g in self.goals.values() if g.is_active]
        avg_progress = sum(g.progress for g in active_goals) / len(active_goals) if active_goals else 0

        return {
            "total_goals": total,
            "active_goals": active,
            "completed_goals": completed,
            "at_risk_goals": at_risk,
            "average_progress": avg_progress,
            "by_category": dict(by_category),
            "by_timeframe": dict(by_timeframe),
            "conflicts_detected": len(self.conflicts)
        }

    def get_timeline_view(self) -> List[Dict[str, Any]]:
        """
        Gibt eine Timeline-Ansicht aller Ziele und Meilensteine zurück.

        Returns:
            Liste von Events sortiert nach Datum
        """
        events = []

        for goal in self.goals.values():
            # Ziel-Deadline
            if goal.target_date:
                events.append({
                    "type": "goal_target",
                    "date": goal.target_date,
                    "title": goal.title,
                    "goal_id": goal.id,
                    "progress": goal.progress
                })

            # Meilensteine
            for ms in goal.milestones:
                events.append({
                    "type": "milestone",
                    "date": ms.target_date,
                    "title": ms.title,
                    "goal_id": goal.id,
                    "milestone_id": ms.id,
                    "status": ms.status.value
                })

        # Sortiere nach Datum
        events.sort(key=lambda e: e["date"])
        return events

    # -------------------------------------------------------------------------
    # Hilfsmethoden
    # -------------------------------------------------------------------------

    def _calculate_default_target(self, timeframe: GoalTimeframe) -> datetime:
        """Berechnet ein Standard-Zieldatum basierend auf Timeframe"""
        days = {
            GoalTimeframe.IMMEDIATE: 1,
            GoalTimeframe.SHORT_TERM: 7,
            GoalTimeframe.MEDIUM_TERM: 30,
            GoalTimeframe.LONG_TERM: 90,
            GoalTimeframe.VERY_LONG_TERM: 180,
            GoalTimeframe.LIFE_GOAL: 365
        }
        return datetime.now() + timedelta(days=days.get(timeframe, 90))

    def _update_goal_progress(self, goal: LongTermGoal):
        """Aktualisiert den Fortschritt basierend auf Meilensteinen"""
        if not goal.milestones:
            return

        completed = sum(1 for m in goal.milestones
                       if m.status == MilestoneStatus.COMPLETED)
        goal.progress = completed / len(goal.milestones)

    def _update_goal_status(self, goal: LongTermGoal):
        """Aktualisiert den Status basierend auf Fortschritt"""
        if goal.progress >= 1.0:
            goal.status = GoalStatus.COMPLETED
        elif goal.progress > 0 and goal.status == GoalStatus.ACTIVE:
            goal.status = GoalStatus.PROGRESSING
        elif goal.is_at_risk and goal.status != GoalStatus.AT_RISK:
            goal.status = GoalStatus.AT_RISK

    def _goal_summary(self, goal: LongTermGoal) -> Dict[str, Any]:
        """Erstellt eine Zusammenfassung eines Ziels"""
        return {
            "id": goal.id,
            "title": goal.title,
            "status": goal.status.value,
            "progress": goal.progress,
            "target_date": goal.target_date.isoformat() if goal.target_date else None
        }

    # -------------------------------------------------------------------------
    # Persistenz
    # -------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert die Engine zu einem Dictionary"""
        return {
            "goals": {
                gid: {
                    "id": g.id,
                    "title": g.title,
                    "description": g.description,
                    "category": g.category.value,
                    "timeframe": g.timeframe.value,
                    "priority": g.priority.value,
                    "status": g.status.value,
                    "progress": g.progress,
                    "target_date": g.target_date.isoformat() if g.target_date else None,
                    "why": g.why,
                    "vision": g.vision,
                    "motivation_score": g.motivation_score,
                    "milestones": [
                        {
                            "id": m.id,
                            "title": m.title,
                            "description": m.description,
                            "target_date": m.target_date.isoformat(),
                            "status": m.status.value,
                            "progress": m.progress
                        }
                        for m in g.milestones
                    ]
                }
                for gid, g in self.goals.items()
            },
            "id_counter": self._id_counter
        }

    def save(self, filepath: str):
        """Speichert die Engine in eine Datei"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def create_smart_goal(
    title: str,
    category: str = "personal_growth",
    months: int = 3
) -> LongTermGoal:
    """
    Schnelle Erstellung eines SMART-Ziels.

    Args:
        title: Titel des Ziels
        category: Kategorie (als String)
        months: Zeitrahmen in Monaten

    Returns:
        Erstelltes Ziel
    """
    engine = LongTermGoalsEngine()

    cat = GoalCategory[category.upper()] if category.upper() in GoalCategory.__members__ else GoalCategory.PERSONAL_GROWTH

    timeframe = GoalTimeframe.MEDIUM_TERM if months <= 1 else \
                GoalTimeframe.LONG_TERM if months <= 6 else \
                GoalTimeframe.VERY_LONG_TERM

    return engine.create_goal(
        title=title,
        description=f"Ziel: {title} in {months} Monaten erreichen",
        category=cat,
        timeframe=timeframe,
        target_date=datetime.now() + timedelta(days=months * 30)
    )


def quick_goal_check(goal_title: str, current_progress: float) -> str:
    """
    Schnelle Statusprüfung für ein Ziel.

    Returns:
        Status-Nachricht
    """
    if current_progress >= 1.0:
        return f"'{goal_title}' ist abgeschlossen!"
    elif current_progress >= 0.75:
        return f"'{goal_title}': Fast geschafft! ({current_progress:.0%})"
    elif current_progress >= 0.5:
        return f"'{goal_title}': Auf halbem Weg ({current_progress:.0%})"
    elif current_progress >= 0.25:
        return f"'{goal_title}': Guter Anfang ({current_progress:.0%})"
    else:
        return f"'{goal_title}': Noch am Anfang ({current_progress:.0%})"


# ============================================================================
# ALIASE FÜR RÜCKWÄRTSKOMPATIBILITÄT
# ============================================================================

# holo_brain.py erwartet diesen Namen
LongtermGoalManager = LongTermGoalsEngine


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "GoalTimeframe",
    "GoalStatus",
    "GoalCategory",
    "PriorityLevel",
    "MilestoneStatus",

    # Dataclasses
    "Milestone",
    "LongTermGoal",
    "GoalReview",
    "GoalConflict",
    "ProgressEntry",

    # Main class
    "LongTermGoalsEngine",
    "LongtermGoalManager",  # Alias

    # Helper functions
    "create_smart_goal",
    "quick_goal_check"
]
