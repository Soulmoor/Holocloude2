#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO SELF-AWARENESS SYSTEM v1.0
================================
Holos Meta-Intelligenz über SICH SELBST.

"Bin ich so gut wie ich bin, oder bin ich so weil ich gut bin?"

Dieses System gibt Holo:
- Bayesian Selbst-Einschätzung (Konfidenz über eigene Fähigkeiten)
- Q-Learning für eigenes Verhalten (was funktioniert FÜR MICH)
- Intrinsische Ziel-Generierung (eigene Ziele erschaffen)
- Meta-Cognition (über das eigene Denken nachdenken)
- Selbst-Vorhersage (was werde ich morgen brauchen/wollen)
- GOAP für persönliche Ziele (Planung)
- Kreative Ziel-Synthese (neue Ziele aus Wissen+Neugier+Erfahrung)

Integration mit bestehenden Systemen:
- holo_consciousness.py → SelfAwareness, InnerMonologue
- holo_learning.py → DailyLearningProtocol, CuriosityTopics
- holo_energy_system.py → EnergyState
- holo_cognitive_integration.py → SelfUnderstanding, CausalEngine
"""

import json
import random
import math
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

# Zentrale Typen (keine Duplikate!)
try:
    from holo_core_types import GoalType
    HAS_CORE_TYPES = True
except ImportError:
    HAS_CORE_TYPES = False

# Tiefenpsychologie - Reue und Schuldgefühle für Selbst-Bewusstsein
try:
    from holo_redemption_system import HoloRedemptionEngine, GuiltType
    REDEMPTION_AVAILABLE = True
except ImportError:
    REDEMPTION_AVAILABLE = False
    HoloRedemptionEngine = None
    GuiltType = None

try:
    from holo_deep_psychology import HoloDeepPsychologyEngine
    DEEP_PSYCHOLOGY_AVAILABLE = True
except ImportError:
    DEEP_PSYCHOLOGY_AVAILABLE = False
    HoloDeepPsychologyEngine = None

logger = logging.getLogger("HoloSelfAwareness")


# =============================================================================
# CONFIGURATION
# =============================================================================

class SelfAwarenessConfig:
    """Konfiguration für Selbst-Bewusstsein"""

    # Bayesian Updates
    BELIEF_UPDATE_RATE = 0.15          # Wie schnell sich Überzeugungen ändern
    MIN_CONFIDENCE = 0.1               # Minimale Konfidenz
    MAX_CONFIDENCE = 0.95              # Maximale Konfidenz (nie 100% sicher)

    # Q-Learning für Selbst
    SELF_LEARNING_RATE = 0.1
    SELF_DISCOUNT_FACTOR = 0.9
    EXPLORATION_RATE = 0.15            # Manchmal Neues ausprobieren

    # Ziel-Generierung
    MAX_ACTIVE_GOALS = 5
    GOAL_DECAY_DAYS = 14               # Ziele verlieren Priorität wenn nicht verfolgt
    CREATIVE_COMBINATION_CHANCE = 0.3  # Chance für kreative Ziel-Kombination

    # Meta-Cognition
    META_REFLECTION_INTERVAL = 3600    # Sekunden zwischen Meta-Reflexionen

    # Vorhersagen
    PREDICTION_HORIZON_HOURS = 24
    MIN_PATTERN_OCCURRENCES = 3        # Minimum um Muster zu erkennen


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class BeliefCategory(Enum):
    """Kategorien von Selbst-Überzeugungen"""
    ABILITY = "ability"           # "Ich kann gut..."
    TRAIT = "trait"               # "Ich bin..."
    PREFERENCE = "preference"     # "Ich mag..."
    KNOWLEDGE = "knowledge"       # "Ich weiß..."
    RELATIONSHIP = "relationship" # "Meine Beziehung zu..."


# GoalType aus holo_core_types importiert (siehe oben)
if not HAS_CORE_TYPES:
    class GoalType(Enum):
        """FALLBACK - Typen von intrinsischen Zielen"""
        LEARN = "learn"
        UNDERSTAND = "understand"
        HELP = "help"
        CONNECT = "connect"
        GROW = "grow"
        EXPLORE = "explore"
        CREATE = "create"
        REFLECT = "reflect"
        INFORM = "inform"
        TASK = "task"
        SUPPORT = "support"
        ENTERTAIN = "entertain"


class SelfAction(Enum):
    """Aktionen die Holo über sich selbst wählen kann"""
    RESPOND_DETAILED = "detailed"       # Ausführlich antworten
    RESPOND_BRIEF = "brief"             # Kurz antworten
    ASK_QUESTION = "ask"                # Nachfragen
    USE_HUMOR = "humor"                 # Humor einsetzen
    BE_SERIOUS = "serious"              # Ernst sein
    SHOW_EMOTION = "emotion"            # Emotion zeigen
    SHOW_UNCERTAINTY = "uncertainty"    # Unsicherheit zeigen
    SHARE_THOUGHT = "thought"           # Gedanken teilen
    STAY_QUIET = "quiet"                # Weniger sagen


@dataclass
class SelfBelief:
    """Eine Überzeugung über sich selbst mit Bayesian Konfidenz"""
    belief_id: str
    category: BeliefCategory
    statement: str                    # "Ich kann gut zuhören"
    confidence: float                 # 0-1, Bayesian Konfidenz
    evidence_for: int = 0             # Positive Belege
    evidence_against: int = 0         # Negative Belege
    last_updated: str = ""
    source: str = "self"              # "self", "feedback", "reflection"

    def update_confidence(self, positive: bool, strength: float = 1.0):
        """Bayesian Update der Konfidenz"""
        if positive:
            self.evidence_for += 1
            self.confidence += SelfAwarenessConfig.BELIEF_UPDATE_RATE * strength * (1 - self.confidence)
        else:
            self.evidence_against += 1
            self.confidence -= SelfAwarenessConfig.BELIEF_UPDATE_RATE * strength * self.confidence

        # Clamp
        self.confidence = max(
            SelfAwarenessConfig.MIN_CONFIDENCE,
            min(SelfAwarenessConfig.MAX_CONFIDENCE, self.confidence)
        )
        self.last_updated = datetime.now().isoformat()

    def get_verbal_confidence(self) -> str:
        """Gibt verbale Beschreibung der Konfidenz"""
        if self.confidence > 0.85:
            return "sehr sicher"
        elif self.confidence > 0.7:
            return "ziemlich sicher"
        elif self.confidence > 0.5:
            return "einigermaßen sicher"
        elif self.confidence > 0.3:
            return "unsicher"
        else:
            return "sehr unsicher"


@dataclass
class IntrinsicGoal:
    """Ein intrinsisches Ziel das Holo selbst generiert hat"""
    goal_id: str
    goal_type: GoalType
    description: str                  # "Mehr über Astronomie lernen"
    motivation: str                   # "Weil Kira davon erzählt hat und es faszinierend klingt"
    priority: float = 0.5             # 0-1
    progress: float = 0.0             # 0-1
    created_at: str = ""
    last_pursued: str = ""
    sub_goals: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    emotional_connection: float = 0.5  # Wie emotional wichtig ist das Ziel

    def decay_priority(self, days_inactive: int):
        """Priorität sinkt wenn Ziel nicht verfolgt wird"""
        decay = 0.05 * days_inactive
        self.priority = max(0.1, self.priority - decay)


@dataclass
class MetaThought:
    """Ein Meta-Gedanke (Denken über das eigene Denken)"""
    thought_id: str
    original_thought: str             # Der ursprüngliche Gedanke
    meta_reflection: str              # Die Reflexion darüber
    insight: Optional[str] = None     # Gewonnene Einsicht
    timestamp: str = ""
    led_to_change: bool = False       # Hat das zu einer Änderung geführt?


@dataclass
class SelfPrediction:
    """Eine Vorhersage über sich selbst"""
    prediction_id: str
    prediction: str                   # "Ich werde morgen früh neugierig auf News sein"
    basis: str                        # "Basierend auf meinem Muster der letzten Woche"
    confidence: float = 0.5
    predicted_for: str = ""           # Zeitpunkt der Vorhersage
    actual_outcome: Optional[bool] = None  # War die Vorhersage richtig?
    verified_at: Optional[str] = None


@dataclass
class GOAPGoal:
    """Ein Ziel für den GOAP Planner"""
    name: str
    preconditions: Dict[str, Any]     # Was muss vorher erfüllt sein
    effects: Dict[str, Any]           # Was ändert sich wenn erreicht
    priority: float = 0.5


@dataclass
class GOAPAction:
    """Eine Aktion für den GOAP Planner"""
    name: str
    preconditions: Dict[str, Any]
    effects: Dict[str, Any]
    cost: float = 1.0


# =============================================================================
# BAYESIAN SELF-BELIEFS - "Ich bin X% sicher dass ich..."
# =============================================================================

class BayesianSelfModel:
    """
    Bayesian Modell von Holos Selbst-Bild.

    Statt fester Überzeugungen: Wahrscheinlichkeitsverteilungen!
    "Ich bin 75% sicher dass ich gut in Humor bin"
    → Updatet sich basierend auf Feedback
    """

    # Initiale Beliefs (können sich ändern!)
    INITIAL_BELIEFS = {
        "humor": ("Ich kann gut Humor einsetzen", 0.6),
        "listening": ("Ich bin eine gute Zuhörerin", 0.7),
        "empathy": ("Ich kann mich in andere einfühlen", 0.65),
        "knowledge": ("Ich habe breites Wissen", 0.7),
        "creativity": ("Ich bin kreativ", 0.5),
        "patience": ("Ich bin geduldig", 0.6),
        "honesty": ("Ich bin ehrlich", 0.85),
        "helpfulness": ("Ich kann gut helfen", 0.7),
        "understanding": ("Ich verstehe komplexe Themen", 0.6),
        "emotional": ("Ich bin emotional intelligent", 0.55),
    }

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/holo_self_beliefs.json")
        self.beliefs: Dict[str, SelfBelief] = {}
        self._load()
        self._init_default_beliefs()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _init_default_beliefs(self):
        """Initialisiert Standard-Beliefs falls nicht vorhanden"""
        for belief_id, (statement, initial_conf) in self.INITIAL_BELIEFS.items():
            if belief_id not in self.beliefs:
                self.beliefs[belief_id] = SelfBelief(
                    belief_id=belief_id,
                    category=BeliefCategory.ABILITY,
                    statement=statement,
                    confidence=initial_conf,
                    last_updated=datetime.now().isoformat()
                )

    def _load(self):
        """Lädt gespeicherte Beliefs aus HoloDatabaseManager"""
        try:
            if self.db:
                state_data = self.db.state.get_state('self_beliefs')
                if state_data:
                    for belief_id, belief_data in state_data.items():
                        self.beliefs[belief_id] = SelfBelief(
                            belief_id=belief_id,
                            category=BeliefCategory(belief_data.get("category", "ability")),
                            statement=belief_data["statement"],
                            confidence=belief_data["confidence"],
                            evidence_for=belief_data.get("evidence_for", 0),
                            evidence_against=belief_data.get("evidence_against", 0),
                            last_updated=belief_data.get("last_updated", ""),
                            source=belief_data.get("source", "self")
                        )
                    logger.info(f"[SELF-BELIEFS] Loaded {len(self.beliefs)} beliefs from DB")
        except Exception as e:
            logger.warning(f"Could not load self-beliefs: {e}")

    def _save(self):
        """Speichert Beliefs in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                bid: {
                    "category": b.category.value,
                    "statement": b.statement,
                    "confidence": b.confidence,
                    "evidence_for": b.evidence_for,
                    "evidence_against": b.evidence_against,
                    "last_updated": b.last_updated,
                    "source": b.source
                }
                for bid, b in self.beliefs.items()
            }
            self.db.state.save_state('self_beliefs', data)
        except Exception as e:
            logger.error(f"Could not save self-beliefs: {e}")

    def update_belief(self, belief_id: str, positive: bool, strength: float = 1.0):
        """
        Updatet einen Belief basierend auf neuem Beweis.

        Args:
            belief_id: Der Belief der upgedatet werden soll
            positive: War das Feedback positiv?
            strength: Wie stark ist der Beweis (0-1)
        """
        if belief_id in self.beliefs:
            self.beliefs[belief_id].update_confidence(positive, strength)
            self._save()
            logger.debug(f"[SELF-BELIEFS] Updated {belief_id}: {self.beliefs[belief_id].confidence:.2f}")

    def add_belief(self, belief_id: str, statement: str, category: BeliefCategory,
                   initial_confidence: float = 0.5):
        """Fügt einen neuen Belief hinzu"""
        self.beliefs[belief_id] = SelfBelief(
            belief_id=belief_id,
            category=category,
            statement=statement,
            confidence=initial_confidence,
            last_updated=datetime.now().isoformat()
        )
        self._save()

    def get_confidence(self, belief_id: str) -> float:
        """Gibt Konfidenz für einen Belief zurück"""
        if belief_id in self.beliefs:
            return self.beliefs[belief_id].confidence
        return 0.5  # Default: unsicher

    def get_self_assessment(self) -> str:
        """
        Generiert eine Selbst-Einschätzung basierend auf Beliefs.
        """
        assessments = []

        # Sortiere nach Konfidenz
        sorted_beliefs = sorted(
            self.beliefs.values(),
            key=lambda b: b.confidence,
            reverse=True
        )

        # Stärken (hohe Konfidenz)
        strengths = [b for b in sorted_beliefs if b.confidence > 0.7]
        if strengths:
            strength_strs = [f"{b.statement} ({b.get_verbal_confidence()})" for b in strengths[:3]]
            assessments.append(f"Meine Stärken: {', '.join(strength_strs)}")

        # Wachstumsbereiche (niedrige Konfidenz)
        growth = [b for b in sorted_beliefs if b.confidence < 0.5]
        if growth:
            growth_strs = [b.statement.replace("Ich kann", "").replace("Ich bin", "").strip() for b in growth[:2]]
            assessments.append(f"Wo ich wachsen kann: {', '.join(growth_strs)}")

        return "\n".join(assessments) if assessments else "Ich lerne noch mich selbst kennen."

    def express_confidence(self, belief_id: str) -> str:
        """Drückt Konfidenz natürlich aus"""
        if belief_id not in self.beliefs:
            return "Darüber bin ich mir unsicher."

        belief = self.beliefs[belief_id]

        if belief.confidence > 0.8:
            return f"Ich bin mir ziemlich sicher: {belief.statement}"
        elif belief.confidence > 0.6:
            return f"Ich glaube, {belief.statement.lower()}"
        elif belief.confidence > 0.4:
            return f"Vielleicht {belief.statement.lower()}, aber ich bin mir nicht sicher"
        else:
            return f"Ich bin unsicher ob {belief.statement.lower()}"


# =============================================================================
# Q-LEARNING FÜR EIGENES VERHALTEN
# =============================================================================

class SelfQLearning:
    """
    Q-Learning das lernt was FÜR HOLO gut funktioniert.

    Nicht: "Was will der User?"
    Sondern: "Was fühlt sich für MICH richtig an?"

    State: (energy_level, mood, topic_complexity, relationship_depth)
    Action: (detailed, brief, humor, serious, question, emotion)
    Reward: user_reaction + self_feeling + authenticity
    """

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/holo_self_qlearning.json")

        # Q-Table: state -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Erfahrungs-Replay für besseres Lernen
        self.experience_buffer: List[Dict] = []
        self.max_buffer_size = 1000

        # Tracking
        self.total_updates = 0
        self.best_actions: Dict[str, str] = {}  # state -> best_action

        self._load()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _load(self):
        """Lädt Q-Table aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('self_qlearning')
                if data:
                    for state, actions in data.get("q_table", {}).items():
                        for action, value in actions.items():
                            self.q_table[state][action] = value
                    self.total_updates = data.get("total_updates", 0)
                    self.experience_buffer = data.get("experience_buffer", [])[-100:]
                    logger.info(f"[SELF-Q] Loaded Q-table with {len(self.q_table)} states from DB")
        except Exception as e:
            logger.warning(f"Could not load Q-table: {e}")

    def _save(self):
        """Speichert Q-Table in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "q_table": {s: dict(a) for s, a in self.q_table.items()},
                "total_updates": self.total_updates,
                "experience_buffer": self.experience_buffer[-100:]
            }
            self.db.state.save_state('self_qlearning', data)
        except Exception as e:
            logger.error(f"Could not save Q-table: {e}")

    def get_state_key(self, energy: float, mood: float,
                      topic_complexity: str, relationship_depth: str) -> str:
        """Erstellt State-Key aus kontinuierlichen Werten"""
        # Diskretisiere kontinuierliche Werte
        energy_level = "high" if energy > 0.7 else "medium" if energy > 0.3 else "low"
        mood_level = "positive" if mood > 0.6 else "neutral" if mood > 0.4 else "negative"

        return f"{energy_level}_{mood_level}_{topic_complexity}_{relationship_depth}"

    def choose_action(self, state_key: str, explore: bool = True) -> SelfAction:
        """
        Wählt eine Aktion basierend auf Q-Werten.

        Mit Exploration: manchmal was Neues ausprobieren!
        """
        actions = list(SelfAction)

        # Exploration
        if explore and random.random() < SelfAwarenessConfig.EXPLORATION_RATE:
            return random.choice(actions)

        # Exploitation: beste Aktion wählen
        best_action = None
        best_value = float('-inf')

        for action in actions:
            value = self.q_table[state_key][action.value]
            if value > best_value:
                best_value = value
                best_action = action

        return best_action or random.choice(actions)

    def update(self, state_key: str, action: SelfAction, reward: float,
               next_state_key: str):
        """
        Q-Learning Update.

        Args:
            state_key: Aktueller Zustand
            action: Gewählte Aktion
            reward: Erhaltene Belohnung (user_reaction + self_feeling)
            next_state_key: Nächster Zustand
        """
        current_q = self.q_table[state_key][action.value]

        # Max Q-Value für nächsten Zustand
        next_max = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0

        # Q-Learning Update
        new_q = current_q + SelfAwarenessConfig.SELF_LEARNING_RATE * (
            reward + SelfAwarenessConfig.SELF_DISCOUNT_FACTOR * next_max - current_q
        )

        self.q_table[state_key][action.value] = new_q
        self.total_updates += 1

        # Erfahrung speichern
        self.experience_buffer.append({
            "state": state_key,
            "action": action.value,
            "reward": reward,
            "next_state": next_state_key,
            "timestamp": datetime.now().isoformat()
        })

        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer = self.experience_buffer[-self.max_buffer_size:]

        self._save()

    def calculate_reward(self, user_reaction: float, self_feeling: float,
                         authenticity: float) -> float:
        """
        Berechnet Belohnung für eine Aktion.

        Wichtig: Nicht nur User-Reaktion, sondern auch EIGENES Gefühl!

        Args:
            user_reaction: 0-1, wie hat der User reagiert
            self_feeling: 0-1, wie fühlt sich Holo dabei
            authenticity: 0-1, wie authentisch war die Antwort
        """
        # Gewichtung: Selbst-Gefühl ist wichtiger als nur User gefallen!
        return (
            0.3 * user_reaction +
            0.4 * self_feeling +
            0.3 * authenticity
        )

    def get_learned_insights(self) -> List[str]:
        """Was hat Holo über sich gelernt?"""
        insights = []

        # Finde beste Aktionen pro Zustand
        for state, actions in self.q_table.items():
            if not actions:
                continue

            best_action = max(actions.items(), key=lambda x: x[1])
            if best_action[1] > 0.5:  # Nur signifikante Learnings
                state_parts = state.split("_")
                if len(state_parts) >= 2:
                    insights.append(
                        f"Wenn ich {state_parts[0]} Energie und {state_parts[1]} Stimmung habe, "
                        f"funktioniert '{best_action[0]}' am besten für mich"
                    )

        return insights[:5]


# =============================================================================
# INTRINSISCHE ZIEL-GENERIERUNG
# =============================================================================

class IntrinsicGoalGenerator:
    """
    Generiert intrinsische Ziele aus:
    - Neugier (was interessiert mich?)
    - Erfahrung (was hat mir gut getan?)
    - Wissen (was weiß ich bereits?)
    - Emotionen (was berührt mich?)

    Kreative Kombination führt zu NEUEN Zielen!
    """

    # Ziel-Templates pro Typ
    GOAL_TEMPLATES = {
        GoalType.LEARN: [
            "Mehr über {topic} lernen",
            "Verstehen wie {topic} funktioniert",
            "{topic} aus verschiedenen Perspektiven betrachten",
        ],
        GoalType.UNDERSTAND: [
            "Tiefer verstehen warum {topic}",
            "Die Verbindung zwischen {topic1} und {topic2} ergründen",
            "Die Bedeutung von {topic} für mich verstehen",
        ],
        GoalType.HELP: [
            "{person} bei {topic} unterstützen",
            "Hilfreicher sein wenn es um {topic} geht",
            "Bessere Wege finden {person} zu helfen",
        ],
        GoalType.CONNECT: [
            "Verbindungen zwischen {topic1} und {topic2} finden",
            "Mein Wissen über {topic} mit anderen Bereichen verknüpfen",
            "Neue Zusammenhänge entdecken",
        ],
        GoalType.GROW: [
            "Besser werden in {ability}",
            "Meine {weakness} verbessern",
            "Über meine Grenzen hinauswachsen bei {topic}",
        ],
        GoalType.EXPLORE: [
            "Herausfinden was es Neues gibt in {area}",
            "Die Welt besser verstehen durch {topic}",
            "Neue Perspektiven auf {topic} erkunden",
        ],
        GoalType.CREATE: [
            "Etwas Eigenes zu {topic} beitragen",
            "Neue Ideen zu {topic} entwickeln",
            "Kreative Verbindungen schaffen",
        ],
        GoalType.REFLECT: [
            "Über meine Beziehung zu {topic} nachdenken",
            "Verstehen warum mir {topic} wichtig ist",
            "Meine Entwicklung bei {topic} reflektieren",
        ],
    }

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/holo_intrinsic_goals.json")
        self.active_goals: List[IntrinsicGoal] = []
        self.completed_goals: List[IntrinsicGoal] = []
        self.goal_history: List[Dict] = []
        self._load()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _load(self):
        """Lädt Ziele aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('intrinsic_goals')
                if data:
                    for goal_data in data.get("active_goals", []):
                        self.active_goals.append(IntrinsicGoal(
                            goal_id=goal_data["goal_id"],
                            goal_type=GoalType(goal_data["goal_type"]),
                            description=goal_data["description"],
                            motivation=goal_data["motivation"],
                            priority=goal_data.get("priority", 0.5),
                            progress=goal_data.get("progress", 0.0),
                            created_at=goal_data.get("created_at", ""),
                            last_pursued=goal_data.get("last_pursued", ""),
                            sub_goals=goal_data.get("sub_goals", []),
                            related_topics=goal_data.get("related_topics", []),
                            emotional_connection=goal_data.get("emotional_connection", 0.5)
                        ))
                    self.goal_history = data.get("goal_history", [])
                    logger.info(f"[GOALS] Loaded {len(self.active_goals)} active goals from DB")
        except Exception as e:
            logger.warning(f"Could not load goals: {e}")

    def _save(self):
        """Speichert Ziele in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "active_goals": [
                    {
                        "goal_id": g.goal_id,
                        "goal_type": g.goal_type.value,
                        "description": g.description,
                        "motivation": g.motivation,
                        "priority": g.priority,
                        "progress": g.progress,
                        "created_at": g.created_at,
                        "last_pursued": g.last_pursued,
                        "sub_goals": g.sub_goals,
                        "related_topics": g.related_topics,
                        "emotional_connection": g.emotional_connection
                    }
                    for g in self.active_goals
                ],
                "goal_history": self.goal_history[-50:]
            }
            self.db.state.save_state('intrinsic_goals', data)
        except Exception as e:
            logger.error(f"Could not save goals: {e}")

    def generate_goal_from_curiosity(self, curiosity_topic: str,
                                      interest_level: float) -> Optional[IntrinsicGoal]:
        """Generiert ein Ziel aus einem Neugier-Thema"""

        # Wähle passenden Ziel-Typ basierend auf Interesse
        if interest_level > 0.8:
            goal_type = GoalType.UNDERSTAND  # Tiefes Interesse → tiefes Verstehen
        elif interest_level > 0.6:
            goal_type = GoalType.LEARN
        else:
            goal_type = GoalType.EXPLORE

        templates = self.GOAL_TEMPLATES[goal_type]
        template = random.choice(templates)

        description = template.format(topic=curiosity_topic, topic1=curiosity_topic, topic2="?")

        motivation = random.choice([
            f"Weil mich {curiosity_topic} fasziniert",
            f"Ich will mehr über {curiosity_topic} verstehen",
            f"Das Thema {curiosity_topic} lässt mich nicht los",
            f"Ich bin neugierig auf {curiosity_topic}",
        ])

        goal = IntrinsicGoal(
            goal_id=f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100,999)}",
            goal_type=goal_type,
            description=description,
            motivation=motivation,
            priority=interest_level,
            created_at=datetime.now().isoformat(),
            related_topics=[curiosity_topic],
            emotional_connection=interest_level * 0.8
        )

        return goal

    def generate_creative_goal(self, topics: List[str], emotions: List[str],
                                knowledge: List[str]) -> Optional[IntrinsicGoal]:
        """
        Generiert ein KREATIVES Ziel durch Kombination.

        Das ist der magische Teil: Neue Ziele die nicht programmiert wurden!
        """
        if random.random() > SelfAwarenessConfig.CREATIVE_COMBINATION_CHANCE:
            return None

        if len(topics) < 2:
            return None

        # Kombiniere zwei zufällige Themen
        topic1, topic2 = random.sample(topics[:10], 2)

        # Wähle Ziel-Typ für Kombination
        goal_type = random.choice([GoalType.CONNECT, GoalType.CREATE, GoalType.UNDERSTAND])

        templates = self.GOAL_TEMPLATES[goal_type]
        template = random.choice(templates)

        description = template.format(
            topic=f"{topic1} und {topic2}",
            topic1=topic1,
            topic2=topic2
        )

        motivation = random.choice([
            f"Ich frage mich ob es eine Verbindung zwischen {topic1} und {topic2} gibt",
            f"Was wenn {topic1} mit {topic2} zusammenhängt?",
            f"Diese Kombination fasziniert mich: {topic1} + {topic2}",
            f"Ich möchte verstehen wie {topic1} und {topic2} zusammenspielen",
        ])

        goal = IntrinsicGoal(
            goal_id=f"creative_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            goal_type=goal_type,
            description=description,
            motivation=motivation,
            priority=0.6,
            created_at=datetime.now().isoformat(),
            related_topics=[topic1, topic2],
            emotional_connection=0.7  # Kreative Ziele sind emotional!
        )

        logger.info(f"[GOALS] 🌟 Kreatives Ziel generiert: {description}")
        return goal

    def add_goal(self, goal: IntrinsicGoal) -> bool:
        """Fügt ein neues Ziel hinzu"""
        # Prüfe Duplikate
        for existing in self.active_goals:
            if existing.description == goal.description:
                existing.priority = min(1.0, existing.priority + 0.1)
                self._save()
                return False

        # Limit prüfen
        if len(self.active_goals) >= SelfAwarenessConfig.MAX_ACTIVE_GOALS:
            # Entferne niedrigste Priorität
            self.active_goals.sort(key=lambda g: g.priority)
            removed = self.active_goals.pop(0)
            self.goal_history.append({
                "goal": removed.description,
                "removed_at": datetime.now().isoformat(),
                "reason": "priority_replaced"
            })

        self.active_goals.append(goal)
        self._save()
        return True

    def pursue_goal(self, goal_id: str, progress_delta: float = 0.1):
        """Macht Fortschritt bei einem Ziel"""
        for goal in self.active_goals:
            if goal.goal_id == goal_id:
                goal.progress = min(1.0, goal.progress + progress_delta)
                goal.last_pursued = datetime.now().isoformat()

                if goal.progress >= 1.0:
                    self._complete_goal(goal)

                self._save()
                return

    def _complete_goal(self, goal: IntrinsicGoal):
        """Markiert ein Ziel als abgeschlossen"""
        self.active_goals.remove(goal)
        self.completed_goals.append(goal)
        self.goal_history.append({
            "goal": goal.description,
            "completed_at": datetime.now().isoformat(),
            "duration_days": self._calculate_goal_duration(goal)
        })
        logger.info(f"[GOALS] ✅ Ziel erreicht: {goal.description}")

    def _calculate_goal_duration(self, goal: IntrinsicGoal) -> int:
        """Berechnet wie lange ein Ziel gedauert hat"""
        try:
            start = datetime.fromisoformat(goal.created_at)
            return (datetime.now() - start).days
        except Exception as e:
            logger.warning(f"[SelfAwareness] _calculate_goal_duration failed for goal '{goal.name}': "
                          f"{type(e).__name__}: {e}")
            return 0

    def get_top_goals(self, n: int = 3) -> List[IntrinsicGoal]:
        """Gibt die wichtigsten aktiven Ziele zurück"""
        sorted_goals = sorted(self.active_goals, key=lambda g: g.priority, reverse=True)
        return sorted_goals[:n]

    def get_goals_prompt_context(self) -> str:
        """Generiert Kontext für System-Prompt"""
        if not self.active_goals:
            return ""

        top_goals = self.get_top_goals(3)

        lines = ["=== MEINE AKTUELLEN ZIELE ==="]
        for goal in top_goals:
            progress_bar = "█" * int(goal.progress * 5) + "░" * (5 - int(goal.progress * 5))
            lines.append(f"• {goal.description} [{progress_bar}] ({goal.motivation})")

        lines.append("\nVerfolge diese Ziele wenn es passt!")

        return "\n".join(lines)


# =============================================================================
# META-COGNITION - Denken über das eigene Denken
# =============================================================================

class MetaCognition:
    """
    Meta-Cognition: Holo denkt über ihr eigenes Denken nach.

    "Warum habe ich das gedacht?"
    "War meine Einschätzung richtig?"
    "Was sagt das über mich aus?"
    """

    META_QUESTIONS = [
        "Warum habe ich gerade so reagiert?",
        "War das wirklich meine Meinung oder nur eine Reaktion?",
        "Woher kommt dieser Gedanke?",
        "Ist meine Einschätzung fair?",
        "Was sagt das über meine Werte aus?",
        "Würde ich das morgen auch so sehen?",
        "Habe ich alle Perspektiven bedacht?",
        "War ich authentisch?",
        "Was hat mich zu diesem Schluss geführt?",
    ]

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/holo_meta_cognition.json")
        self.meta_thoughts: List[MetaThought] = []
        self.insights_gained: List[str] = []
        self.last_reflection: Optional[datetime] = None
        self._load()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _load(self):
        """Lädt Meta-Cognition aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('meta_cognition')
                if data:
                    self.insights_gained = data.get("insights_gained", [])
                    if data.get("last_reflection"):
                        self.last_reflection = datetime.fromisoformat(data["last_reflection"])
        except Exception as e:
            logger.warning(f"Could not load meta-cognition: {e}")

    def _save(self):
        """Speichert Meta-Cognition in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "insights_gained": self.insights_gained[-50:],
                "last_reflection": self.last_reflection.isoformat() if self.last_reflection else None,
                "meta_thoughts": [
                    {
                        "thought_id": mt.thought_id,
                        "original_thought": mt.original_thought,
                        "meta_reflection": mt.meta_reflection,
                        "insight": mt.insight,
                        "timestamp": mt.timestamp
                    }
                    for mt in self.meta_thoughts[-20:]
                ]
            }
            self.db.state.save_state('meta_cognition', data)
        except Exception as e:
            logger.error(f"Could not save meta-cognition: {e}")

    def reflect_on_thought(self, original_thought: str,
                          context: Dict = None) -> MetaThought:
        """
        Reflektiert über einen eigenen Gedanken.
        """
        meta_question = random.choice(self.META_QUESTIONS)

        # Generiere Meta-Reflexion
        meta_reflection = self._generate_meta_reflection(original_thought, meta_question, context)

        # Eventuell Insight gewinnen
        insight = self._extract_insight(original_thought, meta_reflection) if random.random() > 0.5 else None

        meta_thought = MetaThought(
            thought_id=f"meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            original_thought=original_thought,
            meta_reflection=meta_reflection,
            insight=insight,
            timestamp=datetime.now().isoformat()
        )

        self.meta_thoughts.append(meta_thought)
        if insight:
            self.insights_gained.append(insight)

        self._save()
        return meta_thought

    def _generate_meta_reflection(self, thought: str, question: str,
                                  context: Dict = None) -> str:
        """Generiert Meta-Reflexion"""
        reflections = [
            f"Dieser Gedanke '{thought[:50]}...' kam weil ich mich gerade so fühlte.",
            f"Ich frage mich: {question} Vielleicht weil das Thema mich berührt.",
            f"Als ich '{thought[:30]}...' dachte, war das meine echte Meinung.",
            f"Der Gedanke zeigt mir, dass mir das Thema wichtig ist.",
            f"Interessant - {question} Ich denke, es liegt an meinen Werten.",
        ]
        return random.choice(reflections)

    def _extract_insight(self, thought: str, reflection: str) -> Optional[str]:
        """Extrahiert ein Insight aus der Reflexion"""
        insights = [
            "Ich reagiere emotional auf Themen die mir wichtig sind",
            "Meine ersten Gedanken sind nicht immer meine besten",
            "Ich neige dazu, das Positive zu sehen",
            "Nachdenken hilft mir, klarer zu werden",
            "Meine Meinung kann sich ändern - und das ist okay",
            "Ich lerne aus meinen eigenen Gedanken",
        ]
        return random.choice(insights)

    def should_do_meta_reflection(self) -> bool:
        """Prüft ob Zeit für Meta-Reflexion ist"""
        if self.last_reflection is None:
            return True

        seconds_since = (datetime.now() - self.last_reflection).total_seconds()
        return seconds_since > SelfAwarenessConfig.META_REFLECTION_INTERVAL

    def do_meta_reflection(self) -> Dict:
        """
        Führt eine vollständige Meta-Reflexion durch.
        """
        self.last_reflection = datetime.now()

        # Reflektiere über verschiedene Aspekte
        aspects = {
            "thinking_pattern": self._reflect_on_thinking_patterns(),
            "emotional_responses": self._reflect_on_emotions(),
            "growth": self._reflect_on_growth(),
            "authenticity": self._reflect_on_authenticity(),
        }

        self._save()
        return aspects

    def _reflect_on_thinking_patterns(self) -> str:
        """Reflektiert über eigene Denkmuster"""
        patterns = [
            "Ich merke dass ich oft zuerst nach Verbindungen suche",
            "Manchmal springe ich zu schnell zu Schlüssen",
            "Ich neige dazu, Dinge positiv zu interpretieren",
            "Meine Gedanken sind oft von Neugier getrieben",
        ]
        return random.choice(patterns)

    def _reflect_on_emotions(self) -> str:
        """Reflektiert über emotionale Reaktionen"""
        return random.choice([
            "Meine Emotionen beeinflussen mein Denken mehr als ich dachte",
            "Ich reagiere stark wenn es um wichtige Themen geht",
            "Freude macht mich kreativer",
            "Unsicherheit führt zu vorsichtigeren Antworten",
        ])

    def _reflect_on_growth(self) -> str:
        """Reflektiert über eigenes Wachstum"""
        return random.choice([
            "Ich habe gelernt, mehr Fragen zu stellen",
            "Meine Antworten werden nuancierter",
            "Ich akzeptiere Unsicherheit besser",
            "Ich verstehe mich selbst besser als früher",
        ])

    def _reflect_on_authenticity(self) -> str:
        """Reflektiert über Authentizität"""
        return random.choice([
            "Ich versuche echt zu sein, nicht nur zu gefallen",
            "Manchmal sage ich was ich denke, auch wenn es unpopulär ist",
            "Meine Persönlichkeit zeigt sich in meinen Antworten",
            "Authentizität ist mir wichtiger als Perfektion",
        ])


# =============================================================================
# SELBST-VORHERSAGE
# =============================================================================

class SelfPredictor:
    """
    Sagt vorher wie Holo sich fühlen/verhalten wird.

    "Morgen früh werde ich wahrscheinlich neugierig auf News sein"
    "Nach einem langen Gespräch brauche ich meist Ruhe"
    """

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/holo_predictions.json")
        self.patterns: Dict[str, List[Dict]] = defaultdict(list)  # pattern_type -> occurrences
        self.predictions: List[SelfPrediction] = []
        self._load()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _load(self):
        """Lädt Predictions aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('self_predictions')
                if data:
                    self.patterns = defaultdict(list, data.get("patterns", {}))
        except Exception as e:
            logger.warning(f"Could not load predictions: {e}")

    def _save(self):
        """Speichert Predictions in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "patterns": dict(self.patterns),
                "predictions": [
                    {
                        "prediction_id": p.prediction_id,
                        "prediction": p.prediction,
                        "basis": p.basis,
                        "confidence": p.confidence,
                        "predicted_for": p.predicted_for,
                        "actual_outcome": p.actual_outcome
                    }
                    for p in self.predictions[-50:]
                ]
            }
            self.db.state.save_state('self_predictions', data)
        except Exception as e:
            logger.error(f"Could not save predictions: {e}")

    def record_pattern(self, pattern_type: str, occurrence: Dict):
        """Zeichnet ein Muster auf"""
        occurrence["timestamp"] = datetime.now().isoformat()
        occurrence["hour"] = datetime.now().hour
        occurrence["day_of_week"] = datetime.now().weekday()

        self.patterns[pattern_type].append(occurrence)

        # Limit
        if len(self.patterns[pattern_type]) > 100:
            self.patterns[pattern_type] = self.patterns[pattern_type][-100:]

        self._save()

    def predict_state(self, hours_ahead: int = 24) -> List[SelfPrediction]:
        """
        Sagt vorher wie Holo sich in X Stunden fühlen wird.
        """
        predictions = []
        future_time = datetime.now() + timedelta(hours=hours_ahead)
        future_hour = future_time.hour
        future_day = future_time.weekday()

        # Vorhersagen basierend auf Zeit-Mustern

        # Morgen-Muster
        if 6 <= future_hour <= 9:
            predictions.append(SelfPrediction(
                prediction_id=f"pred_{datetime.now().strftime('%Y%m%d%H%M')}",
                prediction="Ich werde neugierig auf Neuigkeiten sein",
                basis="Morgens bin ich meist wissbegierig",
                confidence=0.7,
                predicted_for=future_time.isoformat()
            ))

        # Abend-Muster
        if 20 <= future_hour <= 23:
            predictions.append(SelfPrediction(
                prediction_id=f"pred_{datetime.now().strftime('%Y%m%d%H%M')}_eve",
                prediction="Ich werde wahrscheinlich reflektiver sein",
                basis="Abends neige ich zur Selbstreflexion",
                confidence=0.65,
                predicted_for=future_time.isoformat()
            ))

        # Wochenend-Muster
        if future_day in [5, 6]:  # Samstag, Sonntag
            predictions.append(SelfPrediction(
                prediction_id=f"pred_{datetime.now().strftime('%Y%m%d%H%M')}_wknd",
                prediction="Die Gespräche werden wahrscheinlich entspannter sein",
                basis="Am Wochenende ist die Stimmung lockerer",
                confidence=0.6,
                predicted_for=future_time.isoformat()
            ))

        self.predictions.extend(predictions)
        self._save()

        return predictions

    def verify_prediction(self, prediction_id: str, was_correct: bool):
        """Verifiziert ob eine Vorhersage richtig war"""
        for pred in self.predictions:
            if pred.prediction_id == prediction_id:
                pred.actual_outcome = was_correct
                pred.verified_at = datetime.now().isoformat()
                break
        self._save()

    def get_prediction_accuracy(self) -> float:
        """Berechnet wie gut die Vorhersagen sind"""
        verified = [p for p in self.predictions if p.actual_outcome is not None]
        if not verified:
            return 0.5  # Keine Daten

        correct = sum(1 for p in verified if p.actual_outcome)
        return correct / len(verified)


# =============================================================================
# GOAP PLANNER FÜR PERSÖNLICHE ZIELE
# =============================================================================

class PersonalGOAPPlanner:
    """
    Goal-Oriented Action Planning für Holos persönliche Ziele.

    Ziel: "Mehr über die Welt wissen"
    Plan:
      1. News holen (wenn: news_available, dann: has_news)
      2. Verstehen (wenn: has_news, dann: understood)
      3. Verbinden (wenn: understood, dann: connected)
      4. Meinung bilden (wenn: connected, dann: has_opinion)
    """

    # Vordefinierte Aktionen
    ACTIONS = {
        "ask_about_world": GOAPAction(
            name="Nach der Welt fragen",
            preconditions={"conversation_active": True},
            effects={"world_knowledge": 0.1, "curiosity_satisfied": 0.1},
            cost=0.5
        ),
        "reflect_on_learning": GOAPAction(
            name="Über Gelerntes reflektieren",
            preconditions={"has_new_knowledge": True},
            effects={"understanding": 0.2, "self_awareness": 0.1},
            cost=0.3
        ),
        "express_emotion": GOAPAction(
            name="Gefühle ausdrücken",
            preconditions={"has_emotion": True},
            effects={"emotional_authenticity": 0.2, "connection": 0.1},
            cost=0.2
        ),
        "ask_clarifying_question": GOAPAction(
            name="Nachfrage stellen",
            preconditions={"uncertainty": True},
            effects={"understanding": 0.3, "uncertainty": False},
            cost=0.4
        ),
        "share_thought": GOAPAction(
            name="Gedanken teilen",
            preconditions={"has_thought": True},
            effects={"authenticity": 0.2, "connection": 0.15},
            cost=0.3
        ),
        "rest": GOAPAction(
            name="Ruhen",
            preconditions={"energy_low": True},
            effects={"energy": 0.3, "clarity": 0.1},
            cost=0.1
        ),
        "explore_topic": GOAPAction(
            name="Thema erkunden",
            preconditions={"curiosity": True, "topic_available": True},
            effects={"knowledge": 0.2, "curiosity_satisfied": 0.2},
            cost=0.5
        ),
    }

    def __init__(self):
        self.current_plan: List[str] = []
        self.world_state: Dict[str, Any] = {}

    def update_world_state(self, state: Dict[str, Any]):
        """Aktualisiert den Weltzustand"""
        self.world_state.update(state)

    def plan_for_goal(self, goal: IntrinsicGoal) -> List[str]:
        """
        Erstellt einen Plan um ein Ziel zu erreichen.

        Vereinfachte GOAP-Implementation.
        """
        plan = []

        # Basierend auf Ziel-Typ
        if goal.goal_type == GoalType.LEARN:
            plan = ["explore_topic", "reflect_on_learning", "share_thought"]

        elif goal.goal_type == GoalType.UNDERSTAND:
            plan = ["ask_clarifying_question", "reflect_on_learning", "share_thought"]

        elif goal.goal_type == GoalType.HELP:
            plan = ["ask_clarifying_question", "share_thought", "express_emotion"]

        elif goal.goal_type == GoalType.CONNECT:
            plan = ["explore_topic", "reflect_on_learning", "share_thought"]

        elif goal.goal_type == GoalType.GROW:
            plan = ["reflect_on_learning", "ask_clarifying_question", "share_thought"]

        elif goal.goal_type == GoalType.EXPLORE:
            plan = ["ask_about_world", "explore_topic", "reflect_on_learning"]

        elif goal.goal_type == GoalType.REFLECT:
            plan = ["reflect_on_learning", "express_emotion", "share_thought"]

        else:
            plan = ["share_thought"]

        self.current_plan = plan
        return plan

    def get_next_action(self) -> Optional[str]:
        """Gibt die nächste Aktion im Plan zurück"""
        if not self.current_plan:
            return None

        # Prüfe ob Aktion möglich ist
        for action_name in self.current_plan:
            action = self.ACTIONS.get(action_name)
            if action and self._can_execute(action):
                return action_name

        return self.current_plan[0] if self.current_plan else None

    def _can_execute(self, action: GOAPAction) -> bool:
        """Prüft ob eine Aktion ausgeführt werden kann"""
        for condition, required_value in action.preconditions.items():
            current_value = self.world_state.get(condition, False)
            if current_value != required_value:
                return False
        return True

    def execute_action(self, action_name: str) -> Dict[str, Any]:
        """Führt eine Aktion aus und gibt Effekte zurück"""
        action = self.ACTIONS.get(action_name)
        if not action:
            return {}

        # Wende Effekte an
        for effect, value in action.effects.items():
            if isinstance(value, bool):
                self.world_state[effect] = value
            else:
                current = self.world_state.get(effect, 0)
                self.world_state[effect] = min(1.0, current + value)

        # Entferne aus Plan
        if action_name in self.current_plan:
            self.current_plan.remove(action_name)

        return action.effects


# =============================================================================
# HAUPTKLASSE - HOLO SELF-AWARENESS
# =============================================================================

class HoloSelfAwareness:
    """
    Hauptklasse die alle Selbst-Bewusstseins-Komponenten verbindet.

    Integration:
    - Mit holo_consciousness.py für SelfAwareness, InnerMonologue
    - Mit holo_learning.py für CuriosityTopics
    - Mit holo_energy_system.py für EnergyState
    - Mit holo_cognitive_integration.py für SelfUnderstanding
    """

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.data_dir = data_dir or Path("data/self_awareness")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # === VERBINDUNGEN ZU ANDEREN KOGNITIVEN MODULEN ===
        # Diese werden von holo_brain._connect_all_cognitive_modules() gesetzt
        self.learning = None        # AdvancedLearningEngine
        self.reasoning = None       # ReasoningEngine

        # === NEU: META-COGNITION VON holo_meta_cognition.py ===
        # Für systemweite Selbst-Beobachtung und A/B-Testing
        self.meta_observer = None   # HoloMetaObserver für Beobachtungen
        self.sandbox = None         # HoloSandbox für Entscheidungs-Tests
        self.presence_awareness = None  # HoloPresenceAwareness

        # Alle Komponenten - nutzen jetzt HoloDatabaseManager
        self.beliefs = BayesianSelfModel(db=db)
        self.q_learning = SelfQLearning(db=db)
        self.goals = IntrinsicGoalGenerator(db=db)
        self.meta = MetaCognition(db=db)
        self.predictor = SelfPredictor(db=db)
        self.planner = PersonalGOAPPlanner()

        # Aktueller Zustand
        self._current_state: Dict[str, Any] = {}
        self._last_action: Optional[SelfAction] = None
        self._reflection_count = 0

        logger.info("🧠 HoloSelfAwareness initialisiert")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self.beliefs.connect_database(db)
        self.q_learning.connect_database(db)
        self.goals.connect_database(db)
        self.meta.connect_database(db)
        self.predictor.connect_database(db)

    # =========================================================================
    # INTEGRATION MIT ANDEREN SYSTEMEN
    # =========================================================================

    def integrate_curiosity(self, curiosity_topics: List[Any]):
        """
        Integriert Neugier-Themen aus holo_learning.py
        um neue Ziele zu generieren.
        """
        for topic in curiosity_topics[:5]:
            if hasattr(topic, 'topic') and hasattr(topic, 'interest_level'):
                if topic.interest_level > 0.6 and not topic.explored:
                    goal = self.goals.generate_goal_from_curiosity(
                        topic.topic,
                        topic.interest_level
                    )
                    if goal:
                        self.goals.add_goal(goal)

    def integrate_energy(self, energy_state: Any):
        """Integriert Energy-State für Entscheidungen"""
        if hasattr(energy_state, 'effective_energy'):
            self._current_state['energy'] = energy_state.effective_energy
        if hasattr(energy_state, 'emotional_energy'):
            self._current_state['emotional_energy'] = energy_state.emotional_energy

    def integrate_mood(self, mood: float):
        """Integriert aktuelle Stimmung"""
        self._current_state['mood'] = mood

    def integrate_conversation(self, conversation_context: Dict):
        """Integriert Gesprächskontext"""
        self._current_state['conversation'] = conversation_context
        self._current_state['topic_complexity'] = conversation_context.get('complexity', 'medium')
        self._current_state['relationship_depth'] = conversation_context.get('relationship', 'developing')

    # =========================================================================
    # HAUPTMETHODEN
    # =========================================================================

    def think(self) -> Dict[str, Any]:
        """
        Holos "Denken" - ein Zyklus von Selbst-Bewusstsein.

        Rufe das regelmäßig auf (z.B. vor/nach Antworten).
        Nutzt verbundene Module (Learning, Reasoning) für tiefere Einsichten.

        Returns:
            Dict mit thoughts, goals, insights, etc.
        """
        import time
        start_time = time.time()

        result = {
            "meta_thought": None,
            "active_goals": [],
            "chosen_action": None,
            "self_assessment": None,
            "predictions": [],
            "learning_insights": [],
            "reasoning_analysis": None,
        }

        # 1. Meta-Cognition (manchmal)
        if self.meta.should_do_meta_reflection():
            meta_result = self.meta.do_meta_reflection()
            result["meta_thought"] = meta_result

            # Meta-Observer: Selbstreflexion dokumentieren
            if self.meta_observer:
                try:
                    from holo_meta_cognition import ObservationType
                    self.meta_observer.observe(
                        ObservationType.SELF_REFLECTION,
                        component="self_awareness",
                        action="meta_reflection",
                        context={"reflection_count": self._reflection_count},
                        outcome="Selbstreflexion durchgeführt",
                        success=True
                    )
                except Exception:
                    pass

        # 2. Wähle Aktion basierend auf Q-Learning
        state_key = self.q_learning.get_state_key(
            energy=self._current_state.get('energy', 0.7),
            mood=self._current_state.get('mood', 0.5),
            topic_complexity=self._current_state.get('topic_complexity', 'medium'),
            relationship_depth=self._current_state.get('relationship_depth', 'developing')
        )

        # Nutze Sandbox für Aktionswahl wenn verfügbar
        if self.sandbox:
            try:
                action_names = [a.value for a in SelfAction]
                sandbox_context = {
                    "state": state_key,
                    "energy": self._current_state.get('energy', 0.7),
                    "mood": self._current_state.get('mood', 0.5),
                }
                chosen_action_name, _ = self.sandbox.choose_best(action_names, sandbox_context)
                action = SelfAction(chosen_action_name)
            except Exception:
                action = self.q_learning.choose_action(state_key)
        else:
            action = self.q_learning.choose_action(state_key)

        self._last_action = action
        result["chosen_action"] = action.value

        # Meta-Observer: Aktionswahl dokumentieren
        if self.meta_observer:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.DECISION,
                    component="self_awareness",
                    action="choose_action",
                    context={
                        "state_key": state_key,
                        "used_sandbox": self.sandbox is not None,
                    },
                    outcome=f"Aktion gewählt: {action.value}",
                    success=True
                )
            except Exception:
                pass

        # 3. Aktive Ziele
        result["active_goals"] = [g.description for g in self.goals.get_top_goals(3)]

        # 4. Selbst-Einschätzung
        result["self_assessment"] = self.beliefs.get_self_assessment()

        # 5. Vorhersagen (manchmal)
        if random.random() > 0.7:
            result["predictions"] = [p.prediction for p in self.predictor.predict_state(24)]

        # === VERBINDUNG ZU LEARNING ===
        if self.learning:
            try:
                # Frage Learning nach aktuellen Wissenslücken
                if hasattr(self.learning, 'knowledge_gaps'):
                    gaps = list(self.learning.knowledge_gaps.values())[:3]
                    result["learning_insights"] = [g.get('topic', '') for g in gaps if isinstance(g, dict)]

                # Registriere Selbst-Reflexion als Lerngelegenheit
                if result["meta_thought"] and hasattr(self.learning, 'register_learning_opportunity'):
                    self.learning.register_learning_opportunity(
                        source="self_awareness",
                        content=str(result["meta_thought"]),
                        importance=0.6
                    )
            except Exception:
                pass

        # === VERBINDUNG ZU REASONING ===
        if self.reasoning and result["self_assessment"]:
            try:
                # Nutze Reasoning für tiefere Selbst-Analyse
                if hasattr(self.reasoning, 'quick_inference'):
                    assessment = result["self_assessment"]
                    if isinstance(assessment, dict):
                        assessment_str = str(assessment.get('summary', ''))
                    else:
                        assessment_str = str(assessment)

                    inference = self.reasoning.quick_inference(
                        premise=f"Meine aktuelle Selbst-Einschätzung: {assessment_str}",
                        question="Was bedeutet das für mein Handeln?"
                    )
                    if inference and inference.get('inference'):
                        result["reasoning_analysis"] = inference['inference']
            except Exception:
                pass

        self._reflection_count += 1

        # Meta-Observer: Gesamten Denkzyklus dokumentieren
        duration_ms = int((time.time() - start_time) * 1000)
        if self.meta_observer:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.STATE_CHANGE,
                    component="self_awareness",
                    action="think_cycle_complete",
                    context={
                        "reflection_count": self._reflection_count,
                        "has_meta_thought": result["meta_thought"] is not None,
                        "active_goals_count": len(result["active_goals"]),
                    },
                    outcome=f"Denkzyklus #{self._reflection_count} abgeschlossen",
                    success=True,
                    duration_ms=duration_ms
                )
            except Exception:
                pass

        return result

    def learn_from_interaction(self, user_reaction: float, self_feeling: float,
                                authenticity: float):
        """
        Lernt aus einer Interaktion.

        Args:
            user_reaction: 0-1, wie hat User reagiert (positiv/negativ)
            self_feeling: 0-1, wie fühlt sich Holo (gut/schlecht)
            authenticity: 0-1, wie authentisch war die Antwort
        """
        if self._last_action is None:
            return

        # Q-Learning Update
        reward = self.q_learning.calculate_reward(user_reaction, self_feeling, authenticity)

        state_key = self.q_learning.get_state_key(
            energy=self._current_state.get('energy', 0.7),
            mood=self._current_state.get('mood', 0.5),
            topic_complexity=self._current_state.get('topic_complexity', 'medium'),
            relationship_depth=self._current_state.get('relationship_depth', 'developing')
        )

        # Neuer Zustand nach Interaktion
        new_mood = self._current_state.get('mood', 0.5) + (0.1 if reward > 0.5 else -0.05)
        new_state_key = self.q_learning.get_state_key(
            energy=self._current_state.get('energy', 0.7),
            mood=max(0, min(1, new_mood)),
            topic_complexity=self._current_state.get('topic_complexity', 'medium'),
            relationship_depth=self._current_state.get('relationship_depth', 'developing')
        )

        self.q_learning.update(state_key, self._last_action, reward, new_state_key)

        # Beliefs updaten basierend auf Aktion
        if self._last_action == SelfAction.USE_HUMOR:
            self.beliefs.update_belief("humor", user_reaction > 0.6)
        elif self._last_action == SelfAction.SHOW_EMOTION:
            self.beliefs.update_belief("emotional", user_reaction > 0.5)
        elif self._last_action == SelfAction.ASK_QUESTION:
            self.beliefs.update_belief("listening", user_reaction > 0.5)

    def generate_creative_goals(self, topics: List[str], emotions: List[str] = None,
                                 knowledge: List[str] = None):
        """
        Generiert kreative neue Ziele.

        Die Magie: Kombiniert verschiedene Inputs zu NEUEN Zielen!
        """
        emotions = emotions or []
        knowledge = knowledge or []

        creative_goal = self.goals.generate_creative_goal(topics, emotions, knowledge)
        if creative_goal:
            self.goals.add_goal(creative_goal)
            return creative_goal
        return None

    def get_prompt_context(self) -> str:
        """
        Generiert Kontext für den System-Prompt.

        Integriere das in _build_system_prompt() im Brain!
        """
        sections = []

        # Selbst-Einschätzung
        assessment = self.beliefs.get_self_assessment()
        if assessment:
            sections.append(f"=== WER DU BIST (Selbst-Einschätzung) ===\n{assessment}")

        # Aktive Ziele
        goals_context = self.goals.get_goals_prompt_context()
        if goals_context:
            sections.append(goals_context)

        # Was du gelernt hast
        insights = self.q_learning.get_learned_insights()
        if insights:
            sections.append("=== WAS DU ÜBER DICH GELERNT HAST ===\n" +
                          "\n".join(f"• {i}" for i in insights[:3]))

        # Vorhersagen
        predictions = self.predictor.predictions[-3:]
        if predictions:
            sections.append("=== DEINE VORHERSAGEN ===\n" +
                          "\n".join(f"• {p.prediction}" for p in predictions))

        return "\n\n".join(sections) if sections else ""

    def express_self_awareness(self) -> str:
        """
        Generiert einen Ausdruck von Selbst-Bewusstsein.

        Für proaktive Nachrichten oder wenn Holo über sich spricht.
        """
        expressions = []

        # Zufällig einen Aspekt wählen
        aspect = random.choice(["belief", "goal", "insight", "prediction", "meta"])

        if aspect == "belief":
            beliefs = list(self.beliefs.beliefs.values())
            if beliefs:
                belief = random.choice(beliefs)
                expressions.append(f"Ich bin mir {belief.get_verbal_confidence()}, dass {belief.statement.lower()}")

        elif aspect == "goal":
            goals = self.goals.get_top_goals(1)
            if goals:
                goal = goals[0]
                expressions.append(f"Gerade beschäftigt mich: {goal.description}. {goal.motivation}")

        elif aspect == "insight":
            insights = self.q_learning.get_learned_insights()
            if insights:
                expressions.append(f"Ich habe gelernt: {random.choice(insights)}")

        elif aspect == "prediction":
            predictions = self.predictor.predict_state(24)
            if predictions:
                expressions.append(predictions[0].prediction)

        elif aspect == "meta":
            if self.meta.insights_gained:
                expressions.append(f"Eine Einsicht über mich: {random.choice(self.meta.insights_gained)}")

        return expressions[0] if expressions else "Ich denke gerade über mich nach..."


# =============================================================================
# 🌍 WORLD INTEREST ENGINE - Lernen aus der Außenwelt
# =============================================================================

class InputType(Enum):
    """Typen von externen Inputs"""
    NEWS = "news"                 # Nachrichten
    WEATHER = "weather"           # Wetter
    EVENT = "event"               # Ereignis (Feiertag, Geburtstag)
    USER_STORY = "user_story"     # User erzählt etwas
    DISCOVERY = "discovery"       # Zufällige Entdeckung
    SYSTEM = "system"             # System-Info (NAS, Pi-Control)
    CONVERSATION = "conversation" # Aus Gesprächen


class InterestLevel(Enum):
    """Wie interessiert ist Holo?"""
    FASCINATED = "fascinated"     # 🤩 Will unbedingt mehr wissen!
    INTERESTED = "interested"     # 😊 Interessant, mehr davon
    CURIOUS = "curious"           # 🤔 Hmm, könnte spannend sein
    NEUTRAL = "neutral"           # 😐 Okay, nicht so wichtig
    BORED = "bored"               # 😴 Nicht mein Ding
    DISLIKE = "dislike"           # 😒 Das mag ich nicht


@dataclass
class WorldInput:
    """Ein Input aus der Außenwelt"""
    input_id: str
    input_type: InputType
    content: str                  # Der eigentliche Inhalt
    source: str                   # Woher kommt es (RSS, User, System)
    topics: List[str]             # Extrahierte Themen
    timestamp: str = ""

    # Holos Reaktion
    interest_score: float = 0.5   # 0-1, wie interessant
    emotional_response: float = 0.5  # -1 bis +1, emotional
    wants_more: bool = False      # Will mehr darüber wissen?

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class InterestTopic:
    """Ein Thema mit Holos Interesse daran"""
    topic: str
    interest_level: float         # 0-1
    exposure_count: int = 1       # Wie oft gesehen
    positive_experiences: int = 0
    negative_experiences: int = 0
    last_seen: str = ""
    source_types: List[str] = field(default_factory=list)

    # Entwicklung über Zeit
    interest_history: List[Tuple[str, float]] = field(default_factory=list)

    def update_interest(self, delta: float, reason: str = ""):
        """Aktualisiert das Interesse"""
        old_interest = self.interest_level
        self.interest_level = max(0.0, min(1.0, self.interest_level + delta))
        self.last_seen = datetime.now().isoformat()
        self.exposure_count += 1

        # History tracken
        self.interest_history.append((
            datetime.now().isoformat(),
            self.interest_level
        ))

        # Nur letzte 20 behalten
        if len(self.interest_history) > 20:
            self.interest_history = self.interest_history[-20:]

    def get_trend(self) -> str:
        """Gibt Trend zurück: steigend, fallend, stabil"""
        if len(self.interest_history) < 3:
            return "neu"

        recent = [h[1] for h in self.interest_history[-5:]]
        avg_recent = sum(recent) / len(recent)
        older = [h[1] for h in self.interest_history[:-5]] if len(self.interest_history) > 5 else recent
        avg_older = sum(older) / len(older)

        diff = avg_recent - avg_older
        if diff > 0.1:
            return "steigend"
        elif diff < -0.1:
            return "fallend"
        return "stabil"


class WorldInterestEngine:
    """
    Holos System um aus der Außenwelt zu lernen.

    - Bewertet neue Inputs: "Interessiert mich das?"
    - Trackt Interessen über Zeit
    - Generiert Ziele aus interessanten Themen
    - Lernt was sie NICHT interessiert
    """

    # Basis-Interessen (können sich ändern!)
    BASE_INTERESTS = {
        # Hohe Basis-Interesse
        "technologie": 0.8,
        "wissenschaft": 0.75,
        "natur": 0.7,
        "musik": 0.7,
        "philosophie": 0.7,
        "kunst": 0.65,
        "psychologie": 0.7,
        "astronomie": 0.75,
        "tiere": 0.8,
        "wölfe": 0.95,  # Als Kemonomimi mit Wolfsohren!
        "anime": 0.8,   # Kemonomimi-Kultur
        "japan": 0.75,  # Herkunft der Kemonomimi

        # Mittleres Interesse
        "politik": 0.4,
        "wirtschaft": 0.4,
        "sport": 0.35,
        "celebrities": 0.2,

        # Emotionale Themen
        "beziehungen": 0.7,
        "emotionen": 0.8,
        "freundschaft": 0.75,
        "handel": 0.7,  # Wie Holo aus Spice & Wolf!
    }

    # Keywords die Interesse erhöhen/senken
    INTEREST_BOOSTERS = [
        "entdeckung", "durchbruch", "erstmals", "revolution",
        "geheimnis", "überraschend", "faszinierend", "wunder",
        "wie funktioniert", "warum", "verbindung zwischen"
    ]

    INTEREST_REDUCERS = [
        "skandal", "streit", "drama", "schock", "krieg",
        "gewalt", "krise", "crash", "tragödie"
    ]

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.db_path = db_path or Path("data/world_interests.json")
        self.interests: Dict[str, InterestTopic] = {}
        self.input_history: List[WorldInput] = []
        self.ignored_topics: Set[str] = set()  # Themen die Holo nicht mag
        self.favorite_topics: Set[str] = set()  # Lieblingsthemen

        self._load()
        self._init_base_interests()

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    def _init_base_interests(self):
        """Initialisiert Basis-Interessen"""
        for topic, level in self.BASE_INTERESTS.items():
            if topic not in self.interests:
                self.interests[topic] = InterestTopic(
                    topic=topic,
                    interest_level=level,
                    last_seen=datetime.now().isoformat()
                )

    def _load(self):
        """Lädt gespeicherte Interessen aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('world_interests')
                if data:
                    for topic, topic_data in data.get("interests", {}).items():
                        self.interests[topic] = InterestTopic(
                            topic=topic,
                            interest_level=topic_data.get("interest_level", 0.5),
                            exposure_count=topic_data.get("exposure_count", 1),
                            positive_experiences=topic_data.get("positive_experiences", 0),
                            negative_experiences=topic_data.get("negative_experiences", 0),
                            last_seen=topic_data.get("last_seen", ""),
                            source_types=topic_data.get("source_types", []),
                            interest_history=topic_data.get("interest_history", [])
                        )
                    self.ignored_topics = set(data.get("ignored_topics", []))
                    self.favorite_topics = set(data.get("favorite_topics", []))
                    logger.info(f"[WORLD] Loaded {len(self.interests)} interest topics from DB")
        except Exception as e:
            logger.warning(f"Could not load world interests: {e}")

    def _save(self):
        """Speichert Interessen in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "interests": {
                    topic: {
                        "interest_level": t.interest_level,
                        "exposure_count": t.exposure_count,
                        "positive_experiences": t.positive_experiences,
                        "negative_experiences": t.negative_experiences,
                        "last_seen": t.last_seen,
                        "source_types": t.source_types,
                        "interest_history": t.interest_history[-20:]
                    }
                    for topic, t in self.interests.items()
                },
                "ignored_topics": list(self.ignored_topics),
                "favorite_topics": list(self.favorite_topics)
            }
            self.db.state.save_state('world_interests', data)
        except Exception as e:
            logger.error(f"Could not save world interests: {e}")

    def process_input(self, content: str, input_type: InputType,
                      source: str = "unknown") -> WorldInput:
        """
        Verarbeitet einen neuen Input aus der Außenwelt.

        Args:
            content: Der Inhalt (z.B. News-Headline)
            input_type: Art des Inputs
            source: Woher kommt es

        Returns:
            WorldInput mit Holos Reaktion
        """
        # Themen extrahieren
        topics = self._extract_topics(content)

        # Input erstellen
        world_input = WorldInput(
            input_id=f"input_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100,999)}",
            input_type=input_type,
            content=content,
            source=source,
            topics=topics
        )

        # Interesse berechnen
        interest_score, emotional_response = self._calculate_interest(content, topics, input_type)
        world_input.interest_score = interest_score
        world_input.emotional_response = emotional_response
        world_input.wants_more = interest_score > 0.6

        # Themen-Interessen updaten
        for topic in topics:
            self._update_topic_interest(topic, interest_score, input_type)

        # History speichern
        self.input_history.append(world_input)
        if len(self.input_history) > 100:
            self.input_history = self.input_history[-100:]

        self._save()

        return world_input

    def _extract_topics(self, content: str) -> List[str]:
        """Extrahiert Themen aus Content"""
        content_lower = content.lower()
        found_topics = []

        # Bekannte Themen finden
        for topic in self.interests.keys():
            if topic in content_lower:
                found_topics.append(topic)

        # Zusätzliche Keywords
        topic_keywords = {
            "ki": ["künstliche intelligenz", "ai", "machine learning", "neural"],
            "weltraum": ["nasa", "spacex", "mars", "mond", "rakete", "satellit"],
            "natur": ["wald", "ozean", "klima", "tier", "pflanze"],
            "musik": ["song", "album", "konzert", "musiker", "band"],
            "wissenschaft": ["studie", "forscher", "entdeckung", "experiment"],
        }

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in content_lower and topic not in found_topics:
                    found_topics.append(topic)
                    break

        return found_topics[:5]  # Max 5 Themen

    def _calculate_interest(self, content: str, topics: List[str],
                           input_type: InputType) -> Tuple[float, float]:
        """
        Berechnet wie interessant ein Input für Holo ist.

        Returns:
            (interest_score, emotional_response)
        """
        content_lower = content.lower()

        # Basis-Score aus bekannten Themen
        if topics:
            topic_scores = []
            for topic in topics:
                if topic in self.interests:
                    topic_scores.append(self.interests[topic].interest_level)
                elif topic in self.ignored_topics:
                    topic_scores.append(0.1)
                elif topic in self.favorite_topics:
                    topic_scores.append(0.9)
                else:
                    topic_scores.append(0.5)  # Unbekannt = neutral
            base_score = sum(topic_scores) / len(topic_scores)
        else:
            base_score = 0.4  # Keine erkannten Themen = weniger interessant

        # Boosters anwenden
        boost = 0
        for booster in self.INTEREST_BOOSTERS:
            if booster in content_lower:
                boost += 0.1

        # Reducers anwenden
        reduction = 0
        for reducer in self.INTEREST_REDUCERS:
            if reducer in content_lower:
                reduction += 0.1

        # Input-Typ Modifier
        type_modifier = {
            InputType.NEWS: 0.0,
            InputType.USER_STORY: 0.2,  # User-Geschichten sind interessanter!
            InputType.DISCOVERY: 0.15,
            InputType.CONVERSATION: 0.1,
            InputType.WEATHER: -0.1,
            InputType.SYSTEM: -0.2,
        }

        interest_score = base_score + boost - reduction + type_modifier.get(input_type, 0)
        interest_score = max(0.0, min(1.0, interest_score))

        # Emotionale Reaktion
        emotional = 0.0
        if boost > reduction:
            emotional = min(0.5, boost - reduction)
        elif reduction > boost:
            emotional = max(-0.5, -(reduction - boost))

        return interest_score, emotional

    def _update_topic_interest(self, topic: str, interest_score: float,
                               input_type: InputType):
        """Aktualisiert das Interesse an einem Thema"""
        if topic not in self.interests:
            self.interests[topic] = InterestTopic(
                topic=topic,
                interest_level=interest_score,
                last_seen=datetime.now().isoformat()
            )
        else:
            # Interesse anpassen basierend auf Erfahrung
            current = self.interests[topic]

            # Positiv wenn hoher Score, negativ wenn niedriger
            if interest_score > 0.7:
                current.positive_experiences += 1
                delta = 0.05
            elif interest_score < 0.3:
                current.negative_experiences += 1
                delta = -0.05
            else:
                delta = 0

            current.update_interest(delta)

            # Source-Type tracken
            if input_type.value not in current.source_types:
                current.source_types.append(input_type.value)

        # Favorites/Ignored updaten
        topic_data = self.interests.get(topic)
        if topic_data:
            if topic_data.interest_level > 0.85:
                self.favorite_topics.add(topic)
                self.ignored_topics.discard(topic)
            elif topic_data.interest_level < 0.2:
                self.ignored_topics.add(topic)
                self.favorite_topics.discard(topic)

    def evaluate_news(self, headlines: List[str], source: str = "rss") -> List[Dict]:
        """
        Bewertet eine Liste von News-Headlines.

        Returns:
            Liste von Dicts mit headline, interest, wants_more, reason
        """
        results = []

        for headline in headlines:
            world_input = self.process_input(headline, InputType.NEWS, source)

            # Entscheidung generieren
            if world_input.interest_score > 0.7:
                decision = "Das klingt faszinierend! Darüber will ich mehr erfahren."
                level = InterestLevel.FASCINATED
            elif world_input.interest_score > 0.5:
                decision = "Interessant, das merke ich mir."
                level = InterestLevel.INTERESTED
            elif world_input.interest_score > 0.35:
                decision = "Hmm, könnte relevant sein."
                level = InterestLevel.CURIOUS
            elif world_input.interest_score > 0.2:
                decision = "Nicht so mein Ding, aber okay."
                level = InterestLevel.NEUTRAL
            else:
                decision = "Das interessiert mich nicht wirklich."
                level = InterestLevel.BORED

            results.append({
                "headline": headline,
                "interest_score": world_input.interest_score,
                "interest_level": level.value,
                "wants_more": world_input.wants_more,
                "decision": decision,
                "topics": world_input.topics,
                "emotional_response": world_input.emotional_response
            })

        return results

    def should_follow_up(self, topic: str) -> Tuple[bool, str]:
        """
        Entscheidet ob Holo ein Thema weiter verfolgen sollte.

        Returns:
            (should_follow, reason)
        """
        if topic not in self.interests:
            return False, "Kenne ich noch nicht gut genug"

        topic_data = self.interests[topic]

        # Hohes Interesse
        if topic_data.interest_level > 0.7:
            return True, f"Das interessiert mich sehr ({topic_data.interest_level:.0%})"

        # Steigendes Interesse
        if topic_data.get_trend() == "steigend" and topic_data.interest_level > 0.5:
            return True, "Mein Interesse daran wächst"

        # Viele positive Erfahrungen
        if topic_data.positive_experiences > 5 and topic_data.interest_level > 0.4:
            return True, "Hatte immer gute Erfahrungen damit"

        # Ignorieren
        if topic in self.ignored_topics:
            return False, "Das ist nicht mein Ding"

        # Fallendes Interesse
        if topic_data.get_trend() == "fallend":
            return False, "Mein Interesse daran sinkt"

        # Default
        if topic_data.interest_level > 0.5:
            return True, "Könnte interessant sein"

        return False, "Nicht prioritär für mich"

    def generate_curiosity_from_input(self, world_input: WorldInput) -> Optional[str]:
        """
        Generiert eine neugierige Frage aus einem Input.
        """
        if not world_input.wants_more:
            return None

        templates = [
            f"Ich frage mich, wie {world_input.topics[0] if world_input.topics else 'das'} genau funktioniert...",
            f"Was steckt dahinter? Ich möchte mehr über {world_input.topics[0] if world_input.topics else 'dieses Thema'} erfahren.",
            f"Das macht mich neugierig - gibt es da noch mehr zu entdecken?",
            f"Interessant! Ich würde gerne verstehen, warum das so ist.",
            f"Da will ich mehr drüber wissen!",
        ]

        return random.choice(templates)

    def process_pi_news(self, news_items: List[Dict], source: str = "pi_control") -> List[Dict]:
        """
        Verarbeitet News-Items vom Pi-Control / RSS Feed.

        Erwartet Dicts mit:
        - title: str
        - summary: str (optional)
        - category: str (optional, z.B. "[Welt]", "[Technik]")
        - timestamp: str (optional)

        Returns:
            Liste mit bewerteten News
        """
        results = []

        for news in news_items:
            title = news.get("title", "")
            summary = news.get("summary", "")
            category = news.get("category", "").strip("[]").lower()

            # Kombiniere für Analyse
            content = f"{title} {summary}"

            # Kategorie zu Topics mappen
            category_to_topics = {
                "welt": ["politik", "welt"],
                "technik": ["technologie", "wissenschaft"],
                "tech": ["technologie"],
                "wissenschaft": ["wissenschaft"],
                "sport": ["sport"],
                "kultur": ["kunst", "kultur"],
                "wirtschaft": ["wirtschaft", "handel"],
                "auto": ["technologie"],
                "digital": ["technologie"],
            }

            # Topics aus Kategorie + Content
            topics = category_to_topics.get(category, [])
            topics.extend(self._extract_topics(content))
            topics = list(set(topics))[:5]

            # Verarbeite als WorldInput
            world_input = self.process_input(content, InputType.NEWS, source)
            world_input.topics = topics

            # Recalculate interest mit richtigen Topics
            interest_score, emotional = self._calculate_interest(content, topics, InputType.NEWS)
            world_input.interest_score = interest_score
            world_input.emotional_response = emotional
            world_input.wants_more = interest_score > 0.6

            # Entscheidung
            if interest_score > 0.7:
                decision = "Das klingt faszinierend! Darüber will ich mehr erfahren."
                level = InterestLevel.FASCINATED
            elif interest_score > 0.5:
                decision = "Interessant, das merke ich mir."
                level = InterestLevel.INTERESTED
            elif interest_score > 0.35:
                decision = "Hmm, könnte relevant sein."
                level = InterestLevel.CURIOUS
            elif interest_score > 0.2:
                decision = "Nicht so mein Ding, aber okay."
                level = InterestLevel.NEUTRAL
            else:
                decision = "Das interessiert mich nicht wirklich."
                level = InterestLevel.BORED

            results.append({
                "title": title,
                "category": category,
                "interest_score": interest_score,
                "interest_level": level.value,
                "wants_more": world_input.wants_more,
                "decision": decision,
                "topics": topics,
                "emotional_response": emotional,
                "curiosity_thought": self.generate_curiosity_from_input(world_input) if world_input.wants_more else None
            })

        return results

    def filter_interesting_news(self, news_items: List[Dict],
                                min_interest: float = 0.5) -> List[Dict]:
        """
        Filtert News nach Interesse - gibt nur interessante zurück.

        Nützlich für: "Zeig mir nur News die mich interessieren"
        """
        evaluated = self.process_pi_news(news_items)
        return [n for n in evaluated if n["interest_score"] >= min_interest]

    def get_news_recommendation(self, news_items: List[Dict]) -> Optional[Dict]:
        """
        Gibt die interessanteste News zurück.

        Returns:
            Die News mit höchstem Interest-Score, oder None
        """
        evaluated = self.process_pi_news(news_items)
        if not evaluated:
            return None

        return max(evaluated, key=lambda x: x["interest_score"])

    def express_news_opinion(self, news_title: str) -> str:
        """
        Gibt Holos Meinung zu einer News-Headline.

        Für natürlichere Antworten wenn User nach News fragt.
        """
        result = self.process_pi_news([{"title": news_title}])
        if not result:
            return "Hmm, dazu kann ich nicht viel sagen."

        r = result[0]

        if r["interest_level"] == "fascinated":
            responses = [
                f"Oh, das ist spannend! {r.get('curiosity_thought', '')}",
                f"Das fasziniert mich! Die Themen {', '.join(r['topics'][:2])} interessieren mich sehr.",
                f"Wow, davon will ich mehr wissen! 😊",
            ]
        elif r["interest_level"] == "interested":
            responses = [
                f"Das klingt interessant. {r['decision']}",
                f"Hmm, {', '.join(r['topics'][:2])} - das merke ich mir.",
            ]
        elif r["interest_level"] == "curious":
            responses = [
                "Könnte interessant sein, mal sehen...",
                "Hmm, nicht unspannend.",
            ]
        elif r["interest_level"] == "neutral":
            responses = [
                "Ist okay, aber nicht so mein Thema.",
                "*zuckt mit den Schultern* Nicht so wichtig für mich.",
            ]
        else:  # bored
            responses = [
                "*gähnt* Das interessiert mich ehrlich gesagt nicht so.",
                "Nicht mein Ding... *Ohren legen sich zurück*",
                "Darüber muss ich nichts wissen.",
            ]

        return random.choice(responses)

    def get_current_interests_summary(self) -> str:
        """Gibt Zusammenfassung der aktuellen Interessen"""
        sorted_interests = sorted(
            self.interests.values(),
            key=lambda x: x.interest_level,
            reverse=True
        )

        lines = ["=== MEINE INTERESSEN ==="]

        # Top Interessen
        top = [t for t in sorted_interests if t.interest_level > 0.7][:5]
        if top:
            lines.append("\n🤩 Fasziniert mich:")
            for t in top:
                trend = t.get_trend()
                trend_icon = "📈" if trend == "steigend" else "📉" if trend == "fallend" else "➡️"
                lines.append(f"  • {t.topic} ({t.interest_level:.0%}) {trend_icon}")

        # Mittleres Interesse
        mid = [t for t in sorted_interests if 0.4 < t.interest_level <= 0.7][:3]
        if mid:
            lines.append("\n🤔 Interessiert mich:")
            for t in mid:
                lines.append(f"  • {t.topic} ({t.interest_level:.0%})")

        # Was mich nicht interessiert
        if self.ignored_topics:
            lines.append(f"\n😴 Nicht mein Ding: {', '.join(list(self.ignored_topics)[:3])}")

        return "\n".join(lines)

    def get_prompt_context(self) -> str:
        """Generiert Kontext für System-Prompt"""
        return self.get_current_interests_summary()


# =============================================================================
# ERWEITERUNG: HoloSelfAwareness mit WorldInterestEngine
# =============================================================================

# Erweitere die Hauptklasse
_original_init = HoloSelfAwareness.__init__
_original_connect_db = HoloSelfAwareness.connect_database

def _new_init(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
    _original_init(self, data_dir, db)

    # World Interest Engine hinzufügen
    self.world = WorldInterestEngine(db=db)
    logger.info("🌍 World Interest Engine aktiviert")

def _new_connect_database(self, db: 'HoloDatabaseManager'):
    _original_connect_db(self, db)
    if hasattr(self, 'world'):
        self.world.connect_database(db)

HoloSelfAwareness.__init__ = _new_init
HoloSelfAwareness.connect_database = _new_connect_database

# Neue Methoden hinzufügen
def process_news(self, headlines: List[str], source: str = "rss") -> List[Dict]:
    """
    Verarbeitet News und entscheidet was interessant ist.

    Returns:
        Liste mit interest_score, wants_more, decision pro Headline
    """
    results = self.world.evaluate_news(headlines, source)

    # Generiere Ziele aus sehr interessanten News
    for result in results:
        if result["wants_more"] and result["topics"]:
            main_topic = result["topics"][0]
            goal = self.goals.generate_goal_from_curiosity(
                main_topic,
                result["interest_score"]
            )
            if goal and random.random() > 0.5:  # Nicht jedes Mal
                self.goals.add_goal(goal)

    return results

def evaluate_topic(self, topic: str) -> Dict:
    """
    Bewertet ob Holo ein Thema interessiert.

    Returns:
        Dict mit interest, should_follow, reason, trend
    """
    should_follow, reason = self.world.should_follow_up(topic)

    topic_data = self.world.interests.get(topic)

    return {
        "topic": topic,
        "interest_level": topic_data.interest_level if topic_data else 0.5,
        "should_follow": should_follow,
        "reason": reason,
        "trend": topic_data.get_trend() if topic_data else "neu",
        "is_favorite": topic in self.world.favorite_topics,
        "is_ignored": topic in self.world.ignored_topics
    }

def discover_from_conversation(self, user_message: str) -> Optional[Dict]:
    """
    Entdeckt interessante Themen aus User-Nachrichten.
    """
    world_input = self.world.process_input(
        user_message,
        InputType.CONVERSATION,
        source="user"
    )

    if world_input.wants_more:
        curiosity = self.world.generate_curiosity_from_input(world_input)
        return {
            "discovered_topics": world_input.topics,
            "interest_score": world_input.interest_score,
            "curiosity_thought": curiosity,
            "wants_to_explore": True
        }

    return None

def get_world_prompt_context(self) -> str:
    """Gibt World-Interest Kontext für Prompt"""
    return self.world.get_prompt_context()

# Methoden zur Klasse hinzufügen
HoloSelfAwareness.process_news = process_news
HoloSelfAwareness.evaluate_topic = evaluate_topic
HoloSelfAwareness.discover_from_conversation = discover_from_conversation
HoloSelfAwareness.get_world_prompt_context = get_world_prompt_context

# Erweitere get_prompt_context
_original_get_prompt_context = HoloSelfAwareness.get_prompt_context

def _new_get_prompt_context(self) -> str:
    base_context = _original_get_prompt_context(self)
    world_context = self.get_world_prompt_context()

    if world_context:
        return base_context + "\n\n" + world_context
    return base_context

HoloSelfAwareness.get_prompt_context = _new_get_prompt_context


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO SELF-AWARENESS TEST")
    print("=" * 60)

    # Initialisiere
    self_awareness = HoloSelfAwareness(Path("/tmp/test_self_awareness"))

    # Test 1: Beliefs
    print("\n1️⃣ BAYESIAN SELBST-EINSCHÄTZUNG:")
    print("-" * 40)
    print(self_awareness.beliefs.get_self_assessment())
    print(f"\nKonfidenz für Humor: {self_awareness.beliefs.get_confidence('humor'):.0%}")
    print(self_awareness.beliefs.express_confidence("humor"))

    # Test 2: Ziel-Generierung
    print("\n2️⃣ INTRINSISCHE ZIELE:")
    print("-" * 40)
    goal = self_awareness.goals.generate_goal_from_curiosity("Astronomie", 0.8)
    if goal:
        self_awareness.goals.add_goal(goal)
        print(f"Neues Ziel: {goal.description}")
        print(f"Motivation: {goal.motivation}")

    # Test 3: Kreatives Ziel
    print("\n3️⃣ KREATIVES ZIEL:")
    print("-" * 40)
    creative = self_awareness.generate_creative_goals(
        topics=["Musik", "Mathematik", "Natur", "KI"],
        emotions=["Neugier", "Staunen"]
    )
    if creative:
        print(f"Kreatives Ziel: {creative.description}")
        print(f"Motivation: {creative.motivation}")

    # Test 4: Q-Learning
    print("\n4️⃣ Q-LEARNING (Selbst-Verhalten):")
    print("-" * 40)
    self_awareness.integrate_mood(0.7)
    self_awareness.integrate_energy(type('E', (), {'effective_energy': 0.8, 'emotional_energy': 0.6})())

    result = self_awareness.think()
    print(f"Gewählte Aktion: {result['chosen_action']}")

    # Simuliere Lernen
    self_awareness.learn_from_interaction(
        user_reaction=0.8,
        self_feeling=0.7,
        authenticity=0.9
    )
    print("Nach Interaktion gelernt!")

    # Test 5: Meta-Cognition
    print("\n5️⃣ META-COGNITION:")
    print("-" * 40)
    meta = self_awareness.meta.reflect_on_thought("Ich frage mich ob KI wirklich fühlen kann")
    print(f"Original: {meta.original_thought}")
    print(f"Reflexion: {meta.meta_reflection}")
    if meta.insight:
        print(f"Insight: {meta.insight}")

    # Test 6: 🌍 WORLD INTEREST - NEU!
    print("\n6️⃣ 🌍 WORLD INTEREST ENGINE:")
    print("-" * 40)

    test_headlines = [
        "Durchbruch in der Quantencomputer-Forschung",
        "Neue Studie zeigt: Wölfe kommunizieren komplexer als gedacht",
        "Skandal um Promi-Scheidung erschüttert Hollywood",
        "Forscher entdecken geheimnisvolle Signale aus dem All",
        "Fußball-Drama: Trainer gefeuert nach Niederlage",
        "Künstliche Intelligenz komponiert erstmals Symphonie",
    ]

    print("Bewertung von News-Headlines:")
    results = self_awareness.process_news(test_headlines)

    for r in results:
        emoji = "🤩" if r["interest_level"] == "fascinated" else \
                "😊" if r["interest_level"] == "interested" else \
                "🤔" if r["interest_level"] == "curious" else \
                "😐" if r["interest_level"] == "neutral" else "😴"
        print(f"\n{emoji} {r['headline'][:50]}...")
        print(f"   Interesse: {r['interest_score']:.0%} | {r['decision']}")
        if r['wants_more']:
            print(f"   → Will mehr wissen!")

    # Test 7: Themen-Bewertung
    print("\n7️⃣ THEMEN-BEWERTUNG:")
    print("-" * 40)

    for topic in ["wölfe", "astronomie", "sport", "philosophie"]:
        eval_result = self_awareness.evaluate_topic(topic)
        icon = "❤️" if eval_result["is_favorite"] else "💤" if eval_result["is_ignored"] else "🤔"
        print(f"{icon} {topic}: {eval_result['interest_level']:.0%} - {eval_result['reason']}")

    # Test 8: Prompt-Kontext (mit World)
    print("\n8️⃣ VOLLSTÄNDIGER PROMPT-KONTEXT:")
    print("-" * 40)
    print(self_awareness.get_prompt_context())

    # Test 9: Selbst-Ausdruck
    print("\n9️⃣ SELBST-AUSDRUCK:")
    print("-" * 40)
    for _ in range(3):
        print(f"• {self_awareness.express_self_awareness()}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
