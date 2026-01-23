#!/usr/bin/env python3
"""
HOLO LEARNING GOALS SYSTEM v1.0

Lernziel-System fuer strukturiertes, zielgerichtetes Lernen:
- Persoenliche Lernziele setzen und verfolgen
- Meilensteine und Fortschritts-Tracking
- Lern-Pfade fuer verschiedene Themen
- Achievements und Belohnungen
- Woechentliche und monatliche Ziele
- Lern-Statistiken und Analysen

Autor: Claude (Integration)
Datum: 2026-01-23
"""

import logging
import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class GoalType(Enum):
    """Arten von Lernzielen"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TOPIC = "topic"
    SKILL = "skill"
    CHALLENGE = "challenge"


class GoalStatus(Enum):
    """Status eines Ziels"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class AchievementTier(Enum):
    """Rang von Achievements"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class LearningMilestone:
    """Ein Meilenstein auf dem Weg zum Ziel"""
    milestone_id: str
    description: str
    target_value: int
    current_value: int = 0
    completed: bool = False
    completed_at: Optional[datetime] = None

    def get_progress(self) -> float:
        if self.target_value == 0:
            return 1.0
        return min(1.0, self.current_value / self.target_value)

    def update(self, amount: int = 1) -> bool:
        """Aktualisiert den Fortschritt. Gibt True zurueck wenn abgeschlossen."""
        self.current_value = min(self.target_value, self.current_value + amount)
        if self.current_value >= self.target_value and not self.completed:
            self.completed = True
            self.completed_at = datetime.now()
            return True
        return False


@dataclass
class LearningGoal:
    """Ein Lernziel"""
    goal_id: str
    title: str
    description: str
    goal_type: GoalType
    topic: str
    target_value: int
    current_value: int = 0
    milestones: List[LearningMilestone] = field(default_factory=list)
    status: GoalStatus = GoalStatus.NOT_STARTED
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reward_points: int = 100
    tags: List[str] = field(default_factory=list)

    def get_progress(self) -> float:
        if self.target_value == 0:
            return 1.0
        return min(1.0, self.current_value / self.target_value)

    def is_overdue(self) -> bool:
        if self.deadline and self.status != GoalStatus.COMPLETED:
            return datetime.now() > self.deadline
        return False

    def update_progress(self, amount: int = 1) -> Dict:
        """
        Aktualisiert den Fortschritt.

        Returns:
            Dict mit Status-Updates
        """
        result = {
            'previous_value': self.current_value,
            'new_value': 0,
            'completed': False,
            'milestones_completed': [],
        }

        if self.status == GoalStatus.NOT_STARTED:
            self.status = GoalStatus.IN_PROGRESS

        self.current_value = min(self.target_value, self.current_value + amount)
        result['new_value'] = self.current_value

        # Pruefe Meilensteine
        for milestone in self.milestones:
            if not milestone.completed:
                if milestone.update(amount):
                    result['milestones_completed'].append(milestone.description)

        # Pruefe ob Ziel erreicht
        if self.current_value >= self.target_value:
            self.status = GoalStatus.COMPLETED
            self.completed_at = datetime.now()
            result['completed'] = True

        return result

    def to_dict(self) -> Dict:
        return {
            'goal_id': self.goal_id,
            'title': self.title,
            'description': self.description,
            'goal_type': self.goal_type.value,
            'topic': self.topic,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'milestones': [
                {
                    'milestone_id': m.milestone_id,
                    'description': m.description,
                    'target_value': m.target_value,
                    'current_value': m.current_value,
                    'completed': m.completed,
                    'completed_at': m.completed_at.isoformat() if m.completed_at else None,
                } for m in self.milestones
            ],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reward_points': self.reward_points,
            'tags': self.tags,
        }


@dataclass
class Achievement:
    """Ein Achievement/Errungenschaft"""
    achievement_id: str
    title: str
    description: str
    tier: AchievementTier
    requirement: str
    requirement_value: int
    current_value: int = 0
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    reward_points: int = 50
    icon: str = "⭐"

    def check_unlock(self, value: int) -> bool:
        """Prueft ob Achievement freigeschaltet werden soll"""
        self.current_value = value
        if value >= self.requirement_value and not self.unlocked:
            self.unlocked = True
            self.unlocked_at = datetime.now()
            return True
        return False


@dataclass
class LearningPath:
    """Ein strukturierter Lern-Pfad"""
    path_id: str
    title: str
    description: str
    topic: str
    goals: List[str]  # Goal IDs in Reihenfolge
    current_goal_index: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_reward: int = 500

    def is_complete(self) -> bool:
        return self.current_goal_index >= len(self.goals)

    def get_current_goal_id(self) -> Optional[str]:
        if self.is_complete():
            return None
        return self.goals[self.current_goal_index]

    def advance(self) -> bool:
        """Geht zum naechsten Ziel. Gibt True zurueck wenn Pfad abgeschlossen."""
        self.current_goal_index += 1
        if self.is_complete():
            self.completed_at = datetime.now()
            return True
        return False


# =============================================================================
# GOAL TEMPLATES
# =============================================================================

class GoalTemplates:
    """Vordefinierte Lernziel-Vorlagen"""

    DAILY_GOALS = [
        {
            'title': "Taegliches Lern-Minimum",
            'description': "Lerne heute mindestens 3 neue Fakten",
            'target_value': 3,
            'reward_points': 20,
        },
        {
            'title': "Quiz-Meister des Tages",
            'description': "Beantworte 5 Quiz-Fragen richtig",
            'target_value': 5,
            'reward_points': 25,
        },
        {
            'title': "Wissbegieriger Wolf",
            'description': "Erkunde mindestens 2 verschiedene Themen",
            'target_value': 2,
            'reward_points': 15,
        },
    ]

    WEEKLY_GOALS = [
        {
            'title': "Wochen-Lerner",
            'description': "Lerne diese Woche 20 neue Fakten",
            'target_value': 20,
            'reward_points': 100,
            'milestones': [
                {'description': "5 Fakten gelernt", 'target': 5},
                {'description': "10 Fakten gelernt", 'target': 10},
                {'description': "15 Fakten gelernt", 'target': 15},
            ],
        },
        {
            'title': "Quiz-Champion",
            'description': "Erreiche 80% Genauigkeit in 20 Quiz-Fragen",
            'target_value': 16,  # 80% von 20
            'reward_points': 150,
        },
        {
            'title': "Themen-Explorer",
            'description': "Erkunde diese Woche 5 verschiedene Themen",
            'target_value': 5,
            'reward_points': 75,
        },
    ]

    TOPIC_GOALS = {
        'anime': {
            'title': "Anime-Experte",
            'description': "Werde zum Anime-Wissens-Experten",
            'target_value': 30,
            'reward_points': 200,
            'milestones': [
                {'description': "Anime-Neuling: 5 Fakten", 'target': 5},
                {'description': "Anime-Fan: 15 Fakten", 'target': 15},
                {'description': "Anime-Kenner: 25 Fakten", 'target': 25},
            ],
        },
        'gaming': {
            'title': "Gaming-Guru",
            'description': "Meistere das Gaming-Wissen",
            'target_value': 30,
            'reward_points': 200,
        },
        'woelfe': {
            'title': "Wolf-Wissender",
            'description': "Lerne alles ueber Woelfe",
            'target_value': 20,
            'reward_points': 150,
        },
        'japan': {
            'title': "Japan-Kenner",
            'description': "Entdecke die japanische Kultur",
            'target_value': 25,
            'reward_points': 175,
        },
        'technik': {
            'title': "Tech-Spezialist",
            'description': "Verstehe die Welt der Technologie",
            'target_value': 30,
            'reward_points': 200,
        },
    }


# =============================================================================
# ACHIEVEMENTS DATABASE
# =============================================================================

class AchievementsDatabase:
    """Datenbank aller verfuegbaren Achievements"""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self._load_achievements()

    def _load_achievements(self):
        """Laedt alle Achievements"""
        achievements = [
            # Lern-Achievements
            Achievement("learn_first", "Erster Schritt", "Lerne deinen ersten Fakt",
                       AchievementTier.BRONZE, "facts_learned", 1, icon="📚"),
            Achievement("learn_10", "Wissbegierig", "Lerne 10 Fakten",
                       AchievementTier.BRONZE, "facts_learned", 10, reward_points=25, icon="📖"),
            Achievement("learn_50", "Wissens-Sammler", "Lerne 50 Fakten",
                       AchievementTier.SILVER, "facts_learned", 50, reward_points=75, icon="🎓"),
            Achievement("learn_100", "Gelehrte/r", "Lerne 100 Fakten",
                       AchievementTier.GOLD, "facts_learned", 100, reward_points=150, icon="🏆"),
            Achievement("learn_500", "Wissens-Meister/in", "Lerne 500 Fakten",
                       AchievementTier.PLATINUM, "facts_learned", 500, reward_points=500, icon="👑"),

            # Quiz-Achievements
            Achievement("quiz_first", "Quiz-Starter", "Beantworte deine erste Quiz-Frage",
                       AchievementTier.BRONZE, "quiz_answered", 1, icon="❓"),
            Achievement("quiz_perfect", "Perfektionist", "Beantworte 10 Fragen am Stueck richtig",
                       AchievementTier.GOLD, "quiz_streak", 10, reward_points=100, icon="💯"),
            Achievement("quiz_100", "Quiz-Veteran", "Beantworte 100 Quiz-Fragen",
                       AchievementTier.SILVER, "quiz_answered", 100, reward_points=100, icon="🧠"),

            # Streak-Achievements
            Achievement("streak_3", "Auf dem Weg", "Lerne 3 Tage hintereinander",
                       AchievementTier.BRONZE, "daily_streak", 3, icon="🔥"),
            Achievement("streak_7", "Wochen-Krieger", "Lerne 7 Tage hintereinander",
                       AchievementTier.SILVER, "daily_streak", 7, reward_points=100, icon="🔥"),
            Achievement("streak_30", "Monats-Meister", "Lerne 30 Tage hintereinander",
                       AchievementTier.GOLD, "daily_streak", 30, reward_points=300, icon="🌟"),

            # Themen-Achievements
            Achievement("topic_anime", "Anime-Fan", "Lerne 20 Anime-Fakten",
                       AchievementTier.SILVER, "anime_facts", 20, reward_points=75, icon="🎌"),
            Achievement("topic_gaming", "Gamer", "Lerne 20 Gaming-Fakten",
                       AchievementTier.SILVER, "gaming_facts", 20, reward_points=75, icon="🎮"),
            Achievement("topic_wolf", "Wolf-Freund", "Lerne 15 Wolf-Fakten",
                       AchievementTier.SILVER, "wolf_facts", 15, reward_points=75, icon="🐺"),

            # Spezial-Achievements
            Achievement("explorer", "Entdecker/in", "Erkunde 10 verschiedene Themen",
                       AchievementTier.GOLD, "topics_explored", 10, reward_points=150, icon="🧭"),
            Achievement("goal_first", "Zielstrebig", "Schliesse dein erstes Lernziel ab",
                       AchievementTier.BRONZE, "goals_completed", 1, icon="🎯"),
            Achievement("goal_10", "Zielerreicher", "Schliesse 10 Lernziele ab",
                       AchievementTier.GOLD, "goals_completed", 10, reward_points=200, icon="🏅"),
        ]

        for a in achievements:
            self.achievements[a.achievement_id] = a


# =============================================================================
# LEARNING GOALS ENGINE
# =============================================================================

class LearningGoalsEngine:
    """
    Haupt-Engine fuer das Lernziel-System.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/learning_goals")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.goals: Dict[str, LearningGoal] = {}
        self.paths: Dict[str, LearningPath] = {}
        self.achievements_db = AchievementsDatabase()
        self.user_achievements: Dict[str, Achievement] = {}

        # Statistiken
        self.total_points: int = 0
        self.facts_learned: int = 0
        self.quiz_answered: int = 0
        self.quiz_correct: int = 0
        self.daily_streak: int = 0
        self.best_streak: int = 0
        self.last_activity_date: Optional[str] = None
        self.topics_explored: Set[str] = set()
        self.topic_facts: Dict[str, int] = defaultdict(int)
        self.goals_completed: int = 0

        # Holo's Reaktionen
        self.reactions = {
            'goal_created': [
                "*Ohren aufstellen* Ein neues Ziel! Das schaffen wir!",
                "*motiviert* Los geht's! Ich freue mich auf das Lernen!",
                "*Schweif wedelt* Ein Ziel zu haben ist der erste Schritt!",
            ],
            'goal_progress': [
                "*zufrieden* Guter Fortschritt! Weiter so!",
                "*ermunternd* Du machst das toll!",
                "*nickt* Schritt fuer Schritt zum Ziel!",
            ],
            'goal_completed': [
                "*springt vor Freude* GESCHAFFT! Du hast dein Ziel erreicht!",
                "*Schweif wedelt wild* Fantastisch! Ziel abgeschlossen!",
                "*strahlt* Ich wusste, du schaffst das!",
            ],
            'milestone': [
                "*aufgeregt* Ein Meilenstein erreicht!",
                "*klatcht* Zwischenziel geschafft!",
            ],
            'achievement': [
                "*Augen leuchten* WOW! Achievement freigeschaltet: {title}!",
                "*stolz* Du hast '{title}' verdient!",
                "*feiert* {icon} {title} - MEINS!... aehm, DEINS!",
            ],
        }

        self._load_state()

    def create_goal(self, title: str, description: str, goal_type: GoalType,
                    topic: str, target_value: int, deadline: datetime = None,
                    milestones: List[Dict] = None) -> LearningGoal:
        """
        Erstellt ein neues Lernziel.

        Args:
            title: Titel des Ziels
            description: Beschreibung
            goal_type: Art des Ziels
            topic: Thema
            target_value: Zielwert
            deadline: Optionale Deadline
            milestones: Optionale Meilensteine

        Returns:
            Das erstellte LearningGoal
        """
        import hashlib
        goal_id = hashlib.md5(f"goal_{title}_{datetime.now()}".encode()).hexdigest()[:12]

        # Erstelle Meilensteine
        goal_milestones = []
        if milestones:
            for i, m in enumerate(milestones):
                goal_milestones.append(LearningMilestone(
                    milestone_id=f"{goal_id}_m{i}",
                    description=m.get('description', f"Meilenstein {i+1}"),
                    target_value=m.get('target', target_value // (len(milestones) + 1) * (i + 1))
                ))

        # Berechne Belohnung basierend auf Zieltyp
        reward = 100
        if goal_type == GoalType.DAILY:
            reward = 20
        elif goal_type == GoalType.WEEKLY:
            reward = 100
        elif goal_type == GoalType.MONTHLY:
            reward = 300
        elif goal_type == GoalType.TOPIC:
            reward = 150

        goal = LearningGoal(
            goal_id=goal_id,
            title=title,
            description=description,
            goal_type=goal_type,
            topic=topic,
            target_value=target_value,
            milestones=goal_milestones,
            deadline=deadline,
            reward_points=reward,
            tags=[topic, goal_type.value]
        )

        self.goals[goal_id] = goal
        self._save_state()

        logger.info(f"[LearningGoals] Neues Ziel erstellt: {title}")
        return goal

    def create_daily_goal(self) -> LearningGoal:
        """Erstellt ein zufaelliges Tagesziel"""
        template = random.choice(GoalTemplates.DAILY_GOALS)

        tomorrow = datetime.now() + timedelta(days=1)
        deadline = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)

        return self.create_goal(
            title=template['title'],
            description=template['description'],
            goal_type=GoalType.DAILY,
            topic="allgemein",
            target_value=template['target_value'],
            deadline=deadline
        )

    def create_topic_goal(self, topic: str) -> Optional[LearningGoal]:
        """Erstellt ein Themen-spezifisches Ziel"""
        template = GoalTemplates.TOPIC_GOALS.get(topic.lower())
        if not template:
            return None

        milestones = template.get('milestones', [])

        return self.create_goal(
            title=template['title'],
            description=template['description'],
            goal_type=GoalType.TOPIC,
            topic=topic,
            target_value=template['target_value'],
            milestones=milestones
        )

    def record_learning(self, topic: str, facts_count: int = 1) -> Dict:
        """
        Zeichnet Lern-Aktivitaet auf und aktualisiert Ziele.

        Args:
            topic: Das gelernte Thema
            facts_count: Anzahl gelernter Fakten

        Returns:
            Dict mit Updates
        """
        result = {
            'goals_updated': [],
            'goals_completed': [],
            'milestones_completed': [],
            'achievements_unlocked': [],
            'points_earned': 0,
        }

        # Update Statistiken
        self.facts_learned += facts_count
        self.topics_explored.add(topic.lower())
        self.topic_facts[topic.lower()] += facts_count
        self._update_streak()

        # Update relevante Ziele
        for goal in self.goals.values():
            if goal.status in [GoalStatus.NOT_STARTED, GoalStatus.IN_PROGRESS]:
                # Pruefe ob Ziel relevant ist
                should_update = False
                if goal.goal_type == GoalType.DAILY:
                    should_update = True
                elif goal.topic.lower() == topic.lower():
                    should_update = True
                elif goal.topic.lower() == "allgemein":
                    should_update = True

                if should_update:
                    update = goal.update_progress(facts_count)
                    result['goals_updated'].append(goal.goal_id)
                    result['milestones_completed'].extend(update['milestones_completed'])

                    if update['completed']:
                        result['goals_completed'].append(goal.title)
                        result['points_earned'] += goal.reward_points
                        self.total_points += goal.reward_points
                        self.goals_completed += 1

        # Pruefe Achievements
        unlocked = self._check_achievements()
        for achievement in unlocked:
            result['achievements_unlocked'].append({
                'title': achievement.title,
                'icon': achievement.icon,
                'points': achievement.reward_points
            })
            result['points_earned'] += achievement.reward_points
            self.total_points += achievement.reward_points

        self._save_state()
        return result

    def record_quiz_result(self, correct: bool) -> Dict:
        """Zeichnet ein Quiz-Ergebnis auf"""
        self.quiz_answered += 1
        if correct:
            self.quiz_correct += 1

        return self.record_learning("quiz", 0)  # Nutzt das gleiche System

    def _update_streak(self):
        """Aktualisiert den Tages-Streak"""
        today = datetime.now().strftime("%Y-%m-%d")

        if self.last_activity_date:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if self.last_activity_date == yesterday:
                self.daily_streak += 1
            elif self.last_activity_date != today:
                self.daily_streak = 1
        else:
            self.daily_streak = 1

        self.best_streak = max(self.best_streak, self.daily_streak)
        self.last_activity_date = today

    def _check_achievements(self) -> List[Achievement]:
        """Prueft und schaltet Achievements frei"""
        unlocked = []

        # Kopiere Achievement-Zustaende
        for aid, achievement in self.achievements_db.achievements.items():
            if aid in self.user_achievements:
                achievement = self.user_achievements[aid]
            else:
                self.user_achievements[aid] = achievement

        # Pruefe jedes Achievement
        checks = {
            'facts_learned': self.facts_learned,
            'quiz_answered': self.quiz_answered,
            'quiz_streak': self.quiz_correct,  # Vereinfacht
            'daily_streak': self.daily_streak,
            'topics_explored': len(self.topics_explored),
            'goals_completed': self.goals_completed,
            'anime_facts': self.topic_facts.get('anime', 0),
            'gaming_facts': self.topic_facts.get('gaming', 0),
            'wolf_facts': self.topic_facts.get('woelfe', 0),
        }

        for aid, achievement in self.user_achievements.items():
            if not achievement.unlocked:
                check_value = checks.get(achievement.requirement, 0)
                if achievement.check_unlock(check_value):
                    unlocked.append(achievement)
                    logger.info(f"[Achievement] Freigeschaltet: {achievement.title}")

        return unlocked

    def get_active_goals(self) -> List[LearningGoal]:
        """Gibt alle aktiven Ziele zurueck"""
        return [
            g for g in self.goals.values()
            if g.status in [GoalStatus.NOT_STARTED, GoalStatus.IN_PROGRESS]
        ]

    def get_goal_summary(self, goal_id: str) -> Optional[Dict]:
        """Gibt Zusammenfassung eines Ziels"""
        goal = self.goals.get(goal_id)
        if not goal:
            return None

        return {
            'goal_id': goal.goal_id,
            'title': goal.title,
            'description': goal.description,
            'progress': round(goal.get_progress() * 100, 1),
            'current': goal.current_value,
            'target': goal.target_value,
            'status': goal.status.value,
            'is_overdue': goal.is_overdue(),
            'milestones': [
                {
                    'description': m.description,
                    'progress': round(m.get_progress() * 100, 1),
                    'completed': m.completed
                } for m in goal.milestones
            ],
        }

    def get_overall_stats(self) -> Dict:
        """Gibt Gesamtstatistiken zurueck"""
        active_goals = self.get_active_goals()
        completed_goals = [g for g in self.goals.values() if g.status == GoalStatus.COMPLETED]
        unlocked_achievements = [a for a in self.user_achievements.values() if a.unlocked]

        return {
            'total_points': self.total_points,
            'facts_learned': self.facts_learned,
            'quiz_answered': self.quiz_answered,
            'quiz_accuracy': round(self.quiz_correct / self.quiz_answered * 100, 1) if self.quiz_answered > 0 else 0,
            'daily_streak': self.daily_streak,
            'best_streak': self.best_streak,
            'topics_explored': len(self.topics_explored),
            'active_goals': len(active_goals),
            'completed_goals': len(completed_goals),
            'achievements_unlocked': len(unlocked_achievements),
            'total_achievements': len(self.achievements_db.achievements),
        }

    def get_reaction(self, event_type: str, **kwargs) -> str:
        """Generiert eine Reaktion"""
        templates = self.reactions.get(event_type, ["*freut sich*"])
        template = random.choice(templates)
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'goals': {k: v.to_dict() for k, v in self.goals.items()},
                'total_points': self.total_points,
                'facts_learned': self.facts_learned,
                'quiz_answered': self.quiz_answered,
                'quiz_correct': self.quiz_correct,
                'daily_streak': self.daily_streak,
                'best_streak': self.best_streak,
                'last_activity_date': self.last_activity_date,
                'topics_explored': list(self.topics_explored),
                'topic_facts': dict(self.topic_facts),
                'goals_completed': self.goals_completed,
                'achievements': {
                    k: {
                        'current_value': v.current_value,
                        'unlocked': v.unlocked,
                        'unlocked_at': v.unlocked_at.isoformat() if v.unlocked_at else None,
                    } for k, v in self.user_achievements.items()
                },
            }
            with open(self.data_dir / "learning_goals.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte LearningGoals nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "learning_goals.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                self.total_points = state.get('total_points', 0)
                self.facts_learned = state.get('facts_learned', 0)
                self.quiz_answered = state.get('quiz_answered', 0)
                self.quiz_correct = state.get('quiz_correct', 0)
                self.daily_streak = state.get('daily_streak', 0)
                self.best_streak = state.get('best_streak', 0)
                self.last_activity_date = state.get('last_activity_date')
                self.topics_explored = set(state.get('topics_explored', []))
                self.topic_facts = defaultdict(int, state.get('topic_facts', {}))
                self.goals_completed = state.get('goals_completed', 0)

                # Lade Achievement-Zustaende
                for aid, adata in state.get('achievements', {}).items():
                    if aid in self.achievements_db.achievements:
                        self.user_achievements[aid] = self.achievements_db.achievements[aid]
                        self.user_achievements[aid].current_value = adata.get('current_value', 0)
                        self.user_achievements[aid].unlocked = adata.get('unlocked', False)
                        if adata.get('unlocked_at'):
                            self.user_achievements[aid].unlocked_at = datetime.fromisoformat(adata['unlocked_at'])

        except Exception as e:
            logger.debug(f"Konnte LearningGoals nicht laden: {e}")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_learning_goals_engine: Optional[LearningGoalsEngine] = None

def get_learning_goals_engine() -> LearningGoalsEngine:
    """Gibt die globale LearningGoalsEngine-Instanz zurueck"""
    global _learning_goals_engine
    if _learning_goals_engine is None:
        _learning_goals_engine = LearningGoalsEngine()
    return _learning_goals_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO LEARNING GOALS SYSTEM v1.0")
    print("=" * 60)

    engine = LearningGoalsEngine()

    # Erstelle Tagesziel
    print("\n--- TAGESZIEL ERSTELLEN ---")
    daily = engine.create_daily_goal()
    print(f"Ziel: {daily.title}")
    print(f"Beschreibung: {daily.description}")
    print(f"Ziel: {daily.target_value}")

    # Erstelle Themen-Ziel
    print("\n--- THEMEN-ZIEL ERSTELLEN ---")
    topic_goal = engine.create_topic_goal("anime")
    if topic_goal:
        print(f"Ziel: {topic_goal.title}")
        print(f"Meilensteine: {len(topic_goal.milestones)}")

    # Simuliere Lernen
    print("\n--- LERNEN SIMULIEREN ---")
    for i in range(5):
        result = engine.record_learning("anime", 1)
        print(f"Fakt {i+1} gelernt")
        if result['achievements_unlocked']:
            for a in result['achievements_unlocked']:
                print(f"  Achievement: {a['icon']} {a['title']}")
        if result['goals_completed']:
            for g in result['goals_completed']:
                print(f"  Ziel abgeschlossen: {g}")

    # Statistiken
    print("\n--- STATISTIKEN ---")
    stats = engine.get_overall_stats()
    print(f"Gesamtpunkte: {stats['total_points']}")
    print(f"Fakten gelernt: {stats['facts_learned']}")
    print(f"Streak: {stats['daily_streak']} Tage")
    print(f"Achievements: {stats['achievements_unlocked']}/{stats['total_achievements']}")

    # Aktive Ziele
    print("\n--- AKTIVE ZIELE ---")
    for goal in engine.get_active_goals():
        summary = engine.get_goal_summary(goal.goal_id)
        print(f"  {goal.title}: {summary['progress']}%")

    print("\n" + "=" * 60)
    print("Learning Goals System bereit!")
