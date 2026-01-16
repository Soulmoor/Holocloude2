#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO DIALOGUE ENGINE v2.0 - Dialogue Management & User Modeling             ║
║                                                                              ║
║  REFACTORED: Intent Detection jetzt aus holo_smart_understanding             ║
║                                                                              ║
║  NEUE HAUPTAUFGABE: Dialogführung, User-Profile & Gesprächsplanung           ║
║                                                                              ║
║  FEATURES:                                                                   ║
║  ═══════════════════════════════════════════════════════════════════════════ ║
║  🎭 DIALOGUE STATE MACHINE                                                   ║
║     • Conversation States (GREETING, ACTIVE, ENDING, etc.)                   ║
║     • State Transitions                                                      ║
║     • State-based Response Strategies                                        ║
║                                                                              ║
║  👤 USER MODELING                                                            ║
║     • UserProfile - Präferenzen, Kommunikationsstil, History                 ║
║     • PreferenceTracker - Lernt User-Vorlieben                               ║
║     • ExpertiseLevelEstimator - Schätzt Wissensstand                         ║
║     • CommunicationStyleAnalyzer - Erkennt Kommunikationsstil                ║
║                                                                              ║
║  📋 CONVERSATION PLANNING                                                    ║
║     • ConversationGoals - Was will der User erreichen?                       ║
║     • DialoguePlanner - Plant nächste Schritte                               ║
║     • TaskTracker - Verfolgt laufende Aufgaben                               ║
║                                                                              ║
║  🤝 GROUNDING SYSTEM                                                         ║
║     • MutualUnderstandingChecker - Gegenseitiges Verständnis                 ║
║     • ClarificationGenerator - Rückfragen generieren                         ║
║     • ConfirmationTracker - Bestätigungen tracken                            ║
║                                                                              ║
║  📊 CONVERSATION ANALYTICS                                                   ║
║     • EngagementMetrics - User-Engagement messen                             ║
║     • SatisfactionEstimator - Zufriedenheit schätzen                         ║
║     • ConversationQualityScore - Qualität bewerten                           ║
║                                                                              ║
║  🔄 TURN MANAGEMENT                                                          ║
║     • TurnTakingManager - Wer ist dran?                                      ║
║     • ResponseTimingOptimizer - Optimales Timing                             ║
║     • InterruptionHandler - Unterbrechungen handhaben                        ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 2.0 (Refactored)                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import time
import random
import logging
from collections import deque, defaultdict, Counter
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta

# Zentrale Typen aus holo_core_types importieren (keine Duplikate!)
try:
    from holo_core_types import GoalType
    HAS_CORE_TYPES = True
except ImportError:
    HAS_CORE_TYPES = False

logger = logging.getLogger("HoloDialogueEngine")


# =============================================================================
# CONFIGURATION
# =============================================================================

class DialogueConfig:
    """Konfiguration für Dialogue Engine"""

    # State Machine
    IDLE_TIMEOUT_MINUTES = 30
    GREETING_DURATION_MESSAGES = 3

    # User Modeling
    MIN_MESSAGES_FOR_STYLE_DETECTION = 5
    PREFERENCE_LEARNING_RATE = 0.1

    # Planning
    MAX_ACTIVE_GOALS = 3
    GOAL_TIMEOUT_MINUTES = 60

    # Grounding
    CLARIFICATION_THRESHOLD = 0.4
    CONFIRMATION_INTERVAL = 5

    # Engagement Thresholds
    HIGH_ENGAGEMENT_THRESHOLD = 0.7
    LOW_ENGAGEMENT_THRESHOLD = 0.3


class AdaptiveDialogueConfig:
    """
    Adaptive Konfiguration die aus User-Feedback lernt.

    NEU v2.0: Lernt optimale Pacing-Parameter für jeden User.
    """

    def __init__(self):
        # === ADAPTIVES LERNEN v2.0 ===
        # Response-Längen Erfolgsraten: length_category → [erfolge]
        self.length_success: Dict[str, List[float]] = {
            "short": [], "medium": [], "long": []
        }
        # Frage-Frequenz Erfolgsraten: fragen pro N turns → [erfolge]
        self.question_frequency_success: Dict[int, List[float]] = {}
        # Optimale Wartezeit vor Antwort (sekunden → erfolge)
        self.delay_success: Dict[float, List[float]] = {}
        # Wolf-Action Nutzung (verwendet vs nicht → erfolge)
        self.wolf_action_success: Dict[bool, List[float]] = {True: [], False: []}

        # Gelernte Werte
        self.preferred_length: str = "medium"
        self.preferred_question_rate: float = 0.3  # Fragen in 30% der Antworten
        self.preferred_delay: float = 0.5  # Sekunden
        self.preferred_wolf_action: bool = True

        # Tracking
        self.last_length: str = "medium"
        self.last_used_question: bool = False
        self.last_delay: float = 0.5
        self.last_wolf_action: bool = True

    def get_optimal_length(self) -> str:
        """Gibt die optimal gelernte Antwortlänge zurück."""
        best_length = "medium"
        best_score = 0.0

        for length, successes in self.length_success.items():
            if successes:
                # Durchschnitt mit Exploration-Bonus
                avg = sum(successes) / len(successes)
                exploration = 0.1 / (1 + len(successes) * 0.1)
                score = avg + exploration

                if score > best_score:
                    best_score = score
                    best_length = length

        self.preferred_length = best_length
        return best_length

    def should_ask_question(self) -> bool:
        """Entscheidet ob eine Follow-up Frage gestellt werden sollte."""
        # Berechne optimale Rate aus Erfolgen
        if self.question_frequency_success:
            weighted_rate = 0.0
            total_weight = 0.0

            for rate, successes in self.question_frequency_success.items():
                if successes:
                    weight = len(successes)
                    avg_success = sum(successes) / len(successes)
                    weighted_rate += rate * avg_success * weight
                    total_weight += weight

            if total_weight > 0:
                self.preferred_question_rate = weighted_rate / total_weight

        # Random mit gelernter Rate + Exploration
        return random.random() < (self.preferred_question_rate + random.uniform(-0.1, 0.1))

    def get_optimal_delay(self) -> float:
        """Gibt die optimal gelernte Antwort-Verzögerung zurück."""
        if not self.delay_success:
            return self.preferred_delay

        best_delay = self.preferred_delay
        best_score = 0.0

        for delay, successes in self.delay_success.items():
            if successes:
                avg = sum(successes) / len(successes)
                if avg > best_score:
                    best_score = avg
                    best_delay = delay

        self.preferred_delay = best_delay
        return best_delay

    def should_use_wolf_action(self) -> bool:
        """Entscheidet ob Wolf-Aktionen verwendet werden sollen."""
        true_score = 0.5
        false_score = 0.5

        if self.wolf_action_success[True]:
            true_score = sum(self.wolf_action_success[True]) / len(self.wolf_action_success[True])
        if self.wolf_action_success[False]:
            false_score = sum(self.wolf_action_success[False]) / len(self.wolf_action_success[False])

        self.preferred_wolf_action = true_score >= false_score
        return self.preferred_wolf_action

    def record_feedback(self, was_positive: bool,
                        length: str = None,
                        used_question: bool = None,
                        delay: float = None,
                        used_wolf_action: bool = None) -> None:
        """
        Zeichnet Feedback für Dialog-Entscheidungen auf.

        Args:
            was_positive: War die User-Reaktion positiv?
            length: Verwendete Antwortlänge
            used_question: Wurde eine Follow-up Frage gestellt?
            delay: Verwendete Verzögerung
            used_wolf_action: Wurde Wolf-Action verwendet?
        """
        success_value = 0.8 if was_positive else 0.2

        # Length Feedback
        length = length or self.last_length
        if length in self.length_success:
            self.length_success[length].append(success_value)
            if len(self.length_success[length]) > 30:
                self.length_success[length] = self.length_success[length][-30:]

        # Question Feedback
        used_q = used_question if used_question is not None else self.last_used_question
        q_rate = 1 if used_q else 0
        if q_rate not in self.question_frequency_success:
            self.question_frequency_success[q_rate] = []
        self.question_frequency_success[q_rate].append(success_value)
        # Limit to prevent memory leak
        if len(self.question_frequency_success[q_rate]) > 30:
            self.question_frequency_success[q_rate] = self.question_frequency_success[q_rate][-30:]

        # Delay Feedback
        d = delay if delay is not None else self.last_delay
        rounded_delay = round(d, 1)
        if rounded_delay not in self.delay_success:
            self.delay_success[rounded_delay] = []
        self.delay_success[rounded_delay].append(success_value)
        if len(self.delay_success[rounded_delay]) > 20:
            self.delay_success[rounded_delay] = self.delay_success[rounded_delay][-20:]

        # Wolf Action Feedback
        wolf = used_wolf_action if used_wolf_action is not None else self.last_wolf_action
        self.wolf_action_success[wolf].append(success_value)
        if len(self.wolf_action_success[wolf]) > 30:
            self.wolf_action_success[wolf] = self.wolf_action_success[wolf][-30:]

    def record_choice(self, length: str = None, used_question: bool = None,
                      delay: float = None, used_wolf_action: bool = None) -> None:
        """Zeichnet die gemachten Entscheidungen für späteres Feedback auf."""
        if length:
            self.last_length = length
        if used_question is not None:
            self.last_used_question = used_question
        if delay is not None:
            self.last_delay = delay
        if used_wolf_action is not None:
            self.last_wolf_action = used_wolf_action

    def get_learned_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über gelernte Präferenzen zurück."""
        return {
            "preferred_length": self.preferred_length,
            "preferred_question_rate": self.preferred_question_rate,
            "preferred_delay": self.preferred_delay,
            "preferred_wolf_action": self.preferred_wolf_action,
            "length_samples": {k: len(v) for k, v in self.length_success.items()},
            "delay_samples": len(self.delay_success),
        }


# =============================================================================
# DIALOGUE STATES
# =============================================================================

class DialogueState(Enum):
    """Mögliche Zustände des Dialogs"""
    IDLE = auto()           # Keine aktive Konversation
    GREETING = auto()       # Begrüßungsphase
    ACTIVE = auto()         # Aktives Gespräch
    TASK_FOCUSED = auto()   # Fokus auf einer Aufgabe
    CLARIFYING = auto()     # Klärung läuft
    WAITING = auto()        # Wartet auf User-Input
    ENDING = auto()         # Verabschiedungsphase
    SUPPORT = auto()        # Emotionale Unterstützung


class StateTransition:
    """Definiert gültige State-Übergänge"""
    
    VALID_TRANSITIONS = {
        DialogueState.IDLE: [DialogueState.GREETING, DialogueState.ACTIVE],
        DialogueState.GREETING: [DialogueState.ACTIVE, DialogueState.ENDING],
        DialogueState.ACTIVE: [DialogueState.TASK_FOCUSED, DialogueState.CLARIFYING, 
                               DialogueState.SUPPORT, DialogueState.ENDING, DialogueState.WAITING],
        DialogueState.TASK_FOCUSED: [DialogueState.ACTIVE, DialogueState.CLARIFYING, 
                                      DialogueState.ENDING],
        DialogueState.CLARIFYING: [DialogueState.ACTIVE, DialogueState.TASK_FOCUSED],
        DialogueState.WAITING: [DialogueState.ACTIVE, DialogueState.IDLE],
        DialogueState.ENDING: [DialogueState.IDLE],
        DialogueState.SUPPORT: [DialogueState.ACTIVE, DialogueState.ENDING],
    }
    
    @classmethod
    def is_valid(cls, from_state: DialogueState, to_state: DialogueState) -> bool:
        """Prüfe ob Übergang gültig ist"""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])


# =============================================================================
# DIALOGUE STATE MACHINE
# =============================================================================

@dataclass
class StateContext:
    """Kontext für den aktuellen State"""
    entered_at: float = field(default_factory=time.time)
    message_count_in_state: int = 0
    metadata: Dict = field(default_factory=dict)


class DialogueStateMachine:
    """
    State Machine für Dialogführung.
    
    Verwaltet den aktuellen Zustand des Gesprächs
    und bestimmt passende Response-Strategien.
    """
    
    # State-spezifische Response-Strategien
    STATE_STRATEGIES = {
        DialogueState.IDLE: {
            "tone": "neutral",
            "length": "short",
            "should_greet": True,
        },
        DialogueState.GREETING: {
            "tone": "warm",
            "length": "medium",
            "should_ask_howdy": True,
        },
        DialogueState.ACTIVE: {
            "tone": "engaged",
            "length": "adaptive",
            "can_ask_followup": True,
        },
        DialogueState.TASK_FOCUSED: {
            "tone": "helpful",
            "length": "as_needed",
            "stay_on_topic": True,
        },
        DialogueState.CLARIFYING: {
            "tone": "patient",
            "length": "short",
            "ask_questions": True,
        },
        DialogueState.SUPPORT: {
            "tone": "empathetic",
            "length": "medium",
            "be_gentle": True,
        },
        DialogueState.ENDING: {
            "tone": "warm",
            "length": "short",
            "say_goodbye": True,
        },
    }
    
    def __init__(self, initial_state: DialogueState = DialogueState.IDLE):
        self.current_state = initial_state
        self.state_context = StateContext()
        self.state_history: deque = deque(maxlen=20)
        self.transition_callbacks: Dict[Tuple, List[Callable]] = defaultdict(list)
    
    def transition_to(self, new_state: DialogueState, 
                      metadata: Dict = None) -> bool:
        """
        Wechsle zu neuem State.
        
        Args:
            new_state: Ziel-State
            metadata: Zusätzliche Metadaten
            
        Returns:
            True wenn Übergang erfolgreich
        """
        if not StateTransition.is_valid(self.current_state, new_state):
            logger.warning(f"Ungültiger Übergang: {self.current_state} → {new_state}")
            return False
        
        old_state = self.current_state
        
        # State History
        self.state_history.append({
            "from": old_state,
            "to": new_state,
            "timestamp": time.time(),
            "duration_in_old": time.time() - self.state_context.entered_at,
        })
        
        # Neuer State
        self.current_state = new_state
        self.state_context = StateContext(metadata=metadata or {})
        
        # Callbacks ausführen
        for callback in self.transition_callbacks.get((old_state, new_state), []):
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Callback Error: {e}")
        
        logger.debug(f"State: {old_state.name} → {new_state.name}")
        return True
    
    def get_strategy(self) -> Dict:
        """Hole Response-Strategie für aktuellen State"""
        return self.STATE_STRATEGIES.get(self.current_state, {})
    
    def record_message(self) -> None:
        """Zeichne eine Nachricht im aktuellen State auf"""
        self.state_context.message_count_in_state += 1
    
    def should_transition(self, intent: str, user_sentiment: str) -> Optional[DialogueState]:
        """
        Bestimme ob State-Übergang nötig ist.
        
        Args:
            intent: Erkannter Intent
            user_sentiment: User-Sentiment
            
        Returns:
            Neuer State oder None
        """
        current = self.current_state
        
        # IDLE → GREETING/ACTIVE
        if current == DialogueState.IDLE:
            if intent == "greeting":
                return DialogueState.GREETING
            return DialogueState.ACTIVE
        
        # GREETING → ACTIVE (nach ein paar Nachrichten)
        if current == DialogueState.GREETING:
            if self.state_context.message_count_in_state >= DialogueConfig.GREETING_DURATION_MESSAGES:
                return DialogueState.ACTIVE
            if intent == "farewell":
                return DialogueState.ENDING
        
        # ACTIVE → verschiedene States
        if current == DialogueState.ACTIVE:
            if intent == "farewell":
                return DialogueState.ENDING
            if intent in ["command", "task", "help"]:
                return DialogueState.TASK_FOCUSED
            if user_sentiment in ["very_negative", "sad"]:
                return DialogueState.SUPPORT
        
        # TASK_FOCUSED → ACTIVE (wenn Task erledigt)
        if current == DialogueState.TASK_FOCUSED:
            if intent not in ["command", "task", "help", "followup"]:
                return DialogueState.ACTIVE
        
        # SUPPORT → ACTIVE (wenn User sich besser fühlt)
        if current == DialogueState.SUPPORT:
            if user_sentiment in ["positive", "very_positive", "neutral"]:
                return DialogueState.ACTIVE
        
        # ENDING → IDLE (nach Goodbye)
        if current == DialogueState.ENDING:
            return DialogueState.IDLE
        
        return None
    
    def on_transition(self, from_state: DialogueState, to_state: DialogueState,
                      callback: Callable):
        """Registriere Callback für State-Übergang"""
        self.transition_callbacks[(from_state, to_state)].append(callback)
    
    def get_state_duration(self) -> float:
        """Wie lange sind wir im aktuellen State? (Sekunden)"""
        return time.time() - self.state_context.entered_at


# =============================================================================
# USER PROFILE
# =============================================================================

class CommunicationStyle(Enum):
    """Kommunikationsstile"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    BRIEF = "brief"
    DETAILED = "detailed"


class ExpertiseLevel(Enum):
    """Wissensstand-Level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class UserProfile:
    """
    Profil eines Users.
    
    Speichert Präferenzen, Kommunikationsstil und History.
    """
    # Identifikation
    user_id: str = "default"
    name: Optional[str] = None
    
    # Kommunikation
    preferred_style: CommunicationStyle = CommunicationStyle.FRIENDLY
    preferred_length: str = "medium"  # short, medium, long
    uses_emojis: bool = False
    formal_language: bool = False
    
    # Expertise
    expertise_levels: Dict[str, ExpertiseLevel] = field(default_factory=dict)
    
    # Präferenzen
    interests: Set[str] = field(default_factory=set)
    dislikes: Set[str] = field(default_factory=set)
    preferred_topics: List[str] = field(default_factory=list)
    
    # Stats
    total_messages: int = 0
    avg_message_length: float = 0.0
    avg_response_time: float = 0.0  # Sekunden
    
    # Timestamps
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    
    # Custom
    metadata: Dict = field(default_factory=dict)


class UserProfileManager:
    """
    Verwaltet und aktualisiert User-Profile.
    
    Features:
    - Automatisches Lernen von Präferenzen
    - Stil-Erkennung
    - Expertise-Schätzung
    """
    
    # Style Indicators
    STYLE_INDICATORS = {
        CommunicationStyle.FORMAL: ["Sie", "Ihnen", "bitte", "freundlich", "gestatten"],
        CommunicationStyle.CASUAL: ["hey", "hi", "cool", "krass", "nice", "lol"],
        CommunicationStyle.TECHNICAL: ["api", "code", "server", "debug", "deploy", "git"],
        CommunicationStyle.BRIEF: [],  # Basiert auf Nachrichtenlänge
        CommunicationStyle.DETAILED: [],  # Basiert auf Nachrichtenlänge
    }
    
    # Expertise Indicators by Topic
    EXPERTISE_INDICATORS = {
        "ki": {
            ExpertiseLevel.BEGINNER: ["was ist ki", "erkläre mir", "verstehe nicht"],
            ExpertiseLevel.INTERMEDIATE: ["neural network", "training", "model"],
            ExpertiseLevel.ADVANCED: ["transformer", "attention", "gradient", "backprop"],
            ExpertiseLevel.EXPERT: ["rlhf", "constitutional ai", "emergent", "scaling laws"],
        },
        "programmieren": {
            ExpertiseLevel.BEGINNER: ["was ist eine variable", "wie programmiert man"],
            ExpertiseLevel.INTERMEDIATE: ["funktion", "klasse", "loop", "if else"],
            ExpertiseLevel.ADVANCED: ["async", "decorator", "metaclass", "generator"],
            ExpertiseLevel.EXPERT: ["compiler", "runtime", "memory management", "gc"],
        },
    }
    
    def __init__(self):
        self.profiles: Dict[str, UserProfile] = {}
        self.current_profile: Optional[UserProfile] = None
        self.message_buffer: deque = deque(maxlen=50)
    
    def get_or_create_profile(self, user_id: str = "default") -> UserProfile:
        """Hole oder erstelle User-Profil"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id=user_id)
        
        self.current_profile = self.profiles[user_id]
        return self.current_profile
    
    def update_from_message(self, message: str, profile: UserProfile = None) -> None:
        """
        Aktualisiere Profil basierend auf Nachricht.

        Lernt:
        - Kommunikationsstil
        - Expertise-Level
        - Präferenzen
        """
        profile = profile or self.current_profile
        if not profile:
            return
        
        message_lower = message.lower()
        self.message_buffer.append(message)
        
        # Stats updaten
        profile.total_messages += 1
        profile.last_seen = time.time()
        
        # Durchschnittliche Nachrichtenlänge
        old_avg = profile.avg_message_length
        profile.avg_message_length = (
            (old_avg * (profile.total_messages - 1) + len(message)) / 
            profile.total_messages
        )
        
        # Emoji-Nutzung
        if any(c in message for c in "😀🙂🐺❤️👍🎉"):
            profile.uses_emojis = True
        
        # Kommunikationsstil erkennen
        if profile.total_messages >= DialogueConfig.MIN_MESSAGES_FOR_STYLE_DETECTION:
            self._detect_communication_style(profile)
        
        # Expertise erkennen
        self._detect_expertise(message_lower, profile)
        
        # Interessen erkennen
        self._detect_interests(message_lower, profile)
    
    def _detect_communication_style(self, profile: UserProfile):
        """Erkenne Kommunikationsstil aus Message Buffer"""
        style_scores = Counter()
        
        all_text = ' '.join(self.message_buffer).lower()
        
        for style, indicators in self.STYLE_INDICATORS.items():
            for indicator in indicators:
                if indicator in all_text:
                    style_scores[style] += 1
        
        # Längen-basierte Styles
        if profile.avg_message_length < 30:
            style_scores[CommunicationStyle.BRIEF] += 2
        elif profile.avg_message_length > 100:
            style_scores[CommunicationStyle.DETAILED] += 2
        
        # Dominanten Style wählen
        if style_scores:
            profile.preferred_style = style_scores.most_common(1)[0][0]
        
        # Preferred Length
        if profile.avg_message_length < 30:
            profile.preferred_length = "short"
        elif profile.avg_message_length > 100:
            profile.preferred_length = "long"
        else:
            profile.preferred_length = "medium"
    
    def _detect_expertise(self, message_lower: str, profile: UserProfile):
        """Erkenne Expertise-Level für Topics"""
        for topic, level_indicators in self.EXPERTISE_INDICATORS.items():
            for level, indicators in level_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        # Expertise nur erhöhen, nicht senken
                        current_level = profile.expertise_levels.get(topic, ExpertiseLevel.BEGINNER)
                        if level.value > current_level.value:
                            profile.expertise_levels[topic] = level
                        break
    
    def _detect_interests(self, message_lower: str, profile: UserProfile):
        """Erkenne Interessen"""
        interest_keywords = {
            "technik": ["computer", "software", "hardware", "tech"],
            "ki": ["ki", "ai", "machine learning", "neural"],
            "musik": ["musik", "song", "band", "album"],
            "gaming": ["game", "spiel", "zocken", "spielen"],
            "natur": ["natur", "tier", "pflanze", "wald"],
        }
        
        for interest, keywords in interest_keywords.items():
            if any(kw in message_lower for kw in keywords):
                profile.interests.add(interest)
    
    def get_response_guidelines(self, profile: UserProfile = None) -> Dict:
        """
        Generiere Response-Richtlinien basierend auf Profil.
        
        Returns:
            {
                'length': str,
                'use_emojis': bool,
                'formality': str,
                'technical_level': str,
                'adapt_to_expertise': Dict,
            }
        """
        profile = profile or self.current_profile
        if not profile:
            return {}
        
        guidelines = {
            'length': profile.preferred_length,
            'use_emojis': profile.uses_emojis,
            'formality': 'formal' if profile.formal_language else 'casual',
            'style': profile.preferred_style.value,
            'adapt_to_expertise': {},
        }
        
        # Expertise-Anpassungen
        for topic, level in profile.expertise_levels.items():
            if level == ExpertiseLevel.BEGINNER:
                guidelines['adapt_to_expertise'][topic] = "explain_simply"
            elif level == ExpertiseLevel.EXPERT:
                guidelines['adapt_to_expertise'][topic] = "use_technical_terms"
        
        return guidelines


# =============================================================================
# CONVERSATION GOALS & PLANNING
# =============================================================================

# GoalType aus holo_core_types importiert (siehe oben)
# Fallback nur wenn Import fehlschlägt:
if not HAS_CORE_TYPES:
    class GoalType(Enum):
        """FALLBACK - Typen von Konversations-Zielen - nutze holo_core_types!"""
        INFORMATION = "information"
        TASK = "task"
        SOCIAL = "social"
        SUPPORT = "support"
        LEARNING = "learning"
        ENTERTAINMENT = "entertainment"


@dataclass
class ConversationGoal:
    """Ein Konversations-Ziel"""
    goal_type: GoalType
    description: str
    priority: int = 1
    progress: float = 0.0  # 0.0 - 1.0
    created_at: float = field(default_factory=time.time)
    completed: bool = False
    sub_goals: List['ConversationGoal'] = field(default_factory=list)


class ConversationPlanner:
    """
    Plant und verfolgt Konversations-Ziele.
    
    Features:
    - Ziel-Erkennung aus User-Input
    - Fortschritts-Tracking
    - Nächste Schritte vorschlagen
    """
    
    # Goal Detection Patterns
    GOAL_PATTERNS = {
        GoalType.INFORMATION: [
            r"was ist", r"wer ist", r"wie funktioniert", r"erkläre",
            r"erzähl mir", r"weißt du", r"kennst du",
        ],
        GoalType.TASK: [
            r"mach", r"schalte", r"starte", r"stoppe", r"erstelle",
            r"hilf mir", r"kannst du", r"könntest du",
        ],
        GoalType.SOCIAL: [
            r"wie geht", r"was machst du", r"hast du", r"magst du",
        ],
        GoalType.SUPPORT: [
            r"ich bin traurig", r"ich brauche hilfe", r"mir geht es nicht",
            r"ich habe angst", r"ich mache mir sorgen",
        ],
        GoalType.LEARNING: [
            r"ich möchte lernen", r"bring mir bei", r"tutorial",
            r"wie kann ich", r"wo fange ich an",
        ],
    }
    
    def __init__(self):
        self.active_goals: List[ConversationGoal] = []
        self.completed_goals: deque = deque(maxlen=20)
    
    def detect_goal(self, message: str) -> Optional[ConversationGoal]:
        """
        Erkenne Ziel aus Nachricht.
        
        Returns:
            Erkanntes Goal oder None
        """
        message_lower = message.lower()
        
        for goal_type, patterns in self.GOAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return ConversationGoal(
                        goal_type=goal_type,
                        description=message[:100]
                    )
        
        return None
    
    def add_goal(self, goal: ConversationGoal) -> None:
        """Füge neues Ziel hinzu"""
        # Limit aktive Goals
        if len(self.active_goals) >= DialogueConfig.MAX_ACTIVE_GOALS:
            # Ältestes Goal entfernen
            oldest = min(self.active_goals, key=lambda g: g.created_at)
            self.active_goals.remove(oldest)
        
        self.active_goals.append(goal)
    
    def update_progress(self, goal: ConversationGoal, progress_delta: float):
        """Aktualisiere Fortschritt"""
        goal.progress = min(1.0, goal.progress + progress_delta)
        
        if goal.progress >= 1.0:
            self.complete_goal(goal)
    
    def complete_goal(self, goal: ConversationGoal):
        """Markiere Ziel als erledigt"""
        goal.completed = True
        if goal in self.active_goals:
            self.active_goals.remove(goal)
        self.completed_goals.append(goal)
    
    def get_current_goal(self) -> Optional[ConversationGoal]:
        """Hole aktuelles Haupt-Ziel"""
        if not self.active_goals:
            return None
        
        # Nach Priorität und Recency
        return max(self.active_goals, 
                   key=lambda g: (g.priority, -g.created_at))
    
    def suggest_next_step(self, goal: ConversationGoal = None) -> Optional[str]:
        """Schlage nächsten Schritt vor"""
        goal = goal or self.get_current_goal()
        if not goal:
            return None
        
        if goal.goal_type == GoalType.INFORMATION:
            if goal.progress < 0.3:
                return "provide_overview"
            elif goal.progress < 0.7:
                return "give_details"
            else:
                return "ask_if_clear"
        
        elif goal.goal_type == GoalType.TASK:
            if goal.progress < 0.5:
                return "clarify_task"
            else:
                return "execute_task"
        
        elif goal.goal_type == GoalType.SUPPORT:
            return "show_empathy"
        
        return None


# =============================================================================
# GROUNDING SYSTEM
# =============================================================================

@dataclass
class UnderstandingState:
    """Status des gegenseitigen Verständnisses"""
    topic: str
    holo_understands: float = 0.5  # 0-1
    user_understands: float = 0.5  # 0-1
    last_confirmation: float = field(default_factory=time.time)
    needs_clarification: bool = False
    clarification_count: int = 0


class GroundingSystem:
    """
    Stellt gegenseitiges Verständnis sicher.
    
    Features:
    - Erkennt Missverständnisse
    - Generiert Rückfragen
    - Trackt Bestätigungen
    """
    
    CONFUSION_INDICATORS = [
        "verstehe nicht", "was meinst du", "wie bitte", "hä",
        "???", "das ergibt keinen sinn", "ich bin verwirrt",
    ]
    
    CONFIRMATION_INDICATORS = [
        "ja", "genau", "richtig", "stimmt", "okay", "verstanden",
        "alles klar", "ah ok", "ach so", "jetzt verstehe ich",
    ]
    
    CLARIFICATION_TEMPLATES = [
        "Meinst du damit {topic}?",
        "Verstehe ich richtig, dass {topic}?",
        "Kannst du mir mehr zu {topic} sagen?",
        "*legt Kopf schief* Was genau meinst du mit {topic}?",
    ]
    
    def __init__(self):
        self.understanding_states: Dict[str, UnderstandingState] = {}
        self.confirmation_count = 0
        self.clarification_count = 0
    
    def check_understanding(self, message: str, topic: str = "general") -> UnderstandingState:
        """
        Prüfe Verständnis-Status nach einer Nachricht.
        
        Returns:
            UnderstandingState für das Thema
        """
        message_lower = message.lower()
        
        # State holen oder erstellen
        if topic not in self.understanding_states:
            self.understanding_states[topic] = UnderstandingState(topic=topic)
        
        state = self.understanding_states[topic]
        
        # Confusion Check
        if any(ind in message_lower for ind in self.CONFUSION_INDICATORS):
            state.user_understands *= 0.5
            state.needs_clarification = True
        
        # Confirmation Check
        if any(ind in message_lower for ind in self.CONFIRMATION_INDICATORS):
            state.user_understands = min(1.0, state.user_understands + 0.3)
            state.last_confirmation = time.time()
            state.needs_clarification = False
            self.confirmation_count += 1
        
        return state
    
    def needs_clarification(self, topic: str = "general") -> bool:
        """Prüfe ob Klärung nötig ist"""
        state = self.understanding_states.get(topic)
        if not state:
            return False
        
        return (state.needs_clarification or 
                state.user_understands < DialogueConfig.CLARIFICATION_THRESHOLD)
    
    def generate_clarification(self, topic: str) -> str:
        """Generiere Klärungs-Frage"""
        self.clarification_count += 1
        
        template = random.choice(self.CLARIFICATION_TEMPLATES)
        return template.format(topic=topic)
    
    def record_confirmation(self, topic: str = "general"):
        """Zeichne Bestätigung auf"""
        if topic in self.understanding_states:
            state = self.understanding_states[topic]
            state.user_understands = min(1.0, state.user_understands + 0.2)
            state.last_confirmation = time.time()
    
    def should_confirm(self) -> bool:
        """
        Sollten wir Verständnis bestätigen?
        
        Basierend auf Nachrichten seit letzter Bestätigung.
        """
        return self.confirmation_count % DialogueConfig.CONFIRMATION_INTERVAL == 0


# =============================================================================
# TURN TAKING MANAGER
# =============================================================================

class TurnState(Enum):
    """Wer ist am Zug?"""
    USER_TURN = auto()
    HOLO_TURN = auto()
    OVERLAP = auto()
    PAUSE = auto()


class TurnTakingManager:
    """
    Managed Turn-Taking im Dialog.
    
    Features:
    - Wer ist dran?
    - Unterbrechungen erkennen
    - Optimales Timing
    """
    
    def __init__(self):
        self.current_turn = TurnState.USER_TURN
        self.turn_history: deque = deque(maxlen=50)
        self.last_turn_time = time.time()
        self.interruption_count = 0
    
    def user_message(self):
        """User hat Nachricht gesendet"""
        previous_turn = self.current_turn
        
        # Unterbrechung?
        if previous_turn == TurnState.HOLO_TURN:
            self.interruption_count += 1
        
        self.current_turn = TurnState.USER_TURN
        self._record_turn("user")
    
    def holo_response(self):
        """Holo antwortet"""
        self.current_turn = TurnState.HOLO_TURN
        self._record_turn("holo")
    
    def _record_turn(self, speaker: str):
        """Zeichne Turn auf"""
        now = time.time()
        self.turn_history.append({
            "speaker": speaker,
            "timestamp": now,
            "gap": now - self.last_turn_time,
        })
        self.last_turn_time = now
    
    def get_response_timing(self) -> Dict[str, float]:
        """
        Berechne optimales Response-Timing.
        
        Returns:
            {
                'suggested_delay': float,  # Sekunden
                'user_avg_response_time': float,
            }
        """
        user_turns = [t for t in self.turn_history if t["speaker"] == "user"]
        
        if len(user_turns) < 2:
            return {'suggested_delay': 0.5, 'user_avg_response_time': 0}
        
        # Durchschnittliche User-Response-Zeit
        user_gaps = [t["gap"] for t in user_turns[1:]]
        avg_user_time = sum(user_gaps) / len(user_gaps)
        
        # Holo sollte etwas schneller sein, aber nicht zu schnell
        suggested_delay = min(1.0, avg_user_time * 0.3)
        
        return {
            'suggested_delay': suggested_delay,
            'user_avg_response_time': avg_user_time,
        }
    
    def should_wait_for_more(self) -> bool:
        """
        Sollten wir auf mehr Input warten?
        
        z.B. wenn User mehrere kurze Nachrichten schnell hintereinander schickt.
        """
        recent = list(self.turn_history)[-3:]
        user_recent = [t for t in recent if t["speaker"] == "user"]
        
        if len(user_recent) >= 2:
            # Zwei User-Nachrichten in < 2 Sekunden
            if user_recent[-1]["gap"] < 2.0:
                return True
        
        return False


# =============================================================================
# ENGAGEMENT METRICS
# =============================================================================

@dataclass
class EngagementMetrics:
    """Metriken für User-Engagement"""
    overall_score: float = 0.5
    response_rate: float = 1.0  # Anteil beantworteter Fragen
    avg_message_length: float = 0.0
    topic_depth: float = 0.0
    session_duration: float = 0.0
    messages_per_minute: float = 0.0


class EngagementTracker:
    """
    Trackt und analysiert User-Engagement.
    
    Features:
    - Engagement-Score berechnen
    - Trends erkennen
    - Empfehlungen geben
    """
    
    def __init__(self):
        self.session_start = time.time()
        self.message_count = 0
        self.message_lengths: List[int] = []
        self.questions_asked = 0
        self.questions_answered = 0
        self.topic_switches = 0
        self.deep_dive_count = 0
    
    def record_message(self, message: str, is_question: bool = False) -> None:
        """Zeichne Nachricht auf"""
        self.message_count += 1
        self.message_lengths.append(len(message))
        
        if is_question:
            self.questions_asked += 1
    
    def record_answer(self):
        """Zeichne Antwort auf Frage auf"""
        self.questions_answered += 1
    
    def record_topic_switch(self):
        """Zeichne Themenwechsel auf"""
        self.topic_switches += 1
    
    def record_deep_dive(self):
        """Zeichne tiefgehende Diskussion auf"""
        self.deep_dive_count += 1
    
    def calculate_metrics(self) -> EngagementMetrics:
        """Berechne Engagement-Metriken"""
        now = time.time()
        duration = now - self.session_start
        duration_minutes = duration / 60
        
        # Response Rate
        response_rate = (self.questions_answered / self.questions_asked 
                        if self.questions_asked > 0 else 1.0)
        
        # Avg Message Length
        avg_length = (sum(self.message_lengths) / len(self.message_lengths)
                     if self.message_lengths else 0)
        
        # Messages per Minute
        mpm = self.message_count / duration_minutes if duration_minutes > 0 else 0
        
        # Topic Depth (weniger Wechsel = tiefer)
        if self.message_count > 5:
            topic_depth = 1.0 - (self.topic_switches / self.message_count)
        else:
            topic_depth = 0.5
        
        # Overall Score
        # Gewichtet: Response Rate, Message Length, Topic Depth
        overall = (
            response_rate * 0.3 +
            min(1.0, avg_length / 100) * 0.3 +
            topic_depth * 0.2 +
            min(1.0, mpm / 5) * 0.2
        )
        
        return EngagementMetrics(
            overall_score=overall,
            response_rate=response_rate,
            avg_message_length=avg_length,
            topic_depth=topic_depth,
            session_duration=duration,
            messages_per_minute=mpm,
        )
    
    def get_engagement_level(self) -> str:
        """Hole Engagement-Level als String"""
        metrics = self.calculate_metrics()
        
        if metrics.overall_score >= DialogueConfig.HIGH_ENGAGEMENT_THRESHOLD:
            return "high"
        elif metrics.overall_score <= DialogueConfig.LOW_ENGAGEMENT_THRESHOLD:
            return "low"
        return "medium"


# =============================================================================
# RESPONSE GENERATOR
# =============================================================================

class ResponseGenerator:
    """
    Generiert Response-Rahmen basierend auf Dialog-Kontext.

    HINWEIS: Es gibt eine ANDERE ResponseGenerator-Klasse in holo_brain.py!
    Diese hier: Generiert Response-Framework (Ton, Stil, Länge) für LLM
    Die andere:  Generiert fertige Antwort-Texte basierend auf Intent + Emotion

    Bestimmt:
    - Ton und Stil
    - Länge
    - Struktur
    - Zusätzliche Elemente (Fragen, Emojis, etc.)

    NEU v2.0: Nutzt AdaptiveDialogueConfig für gelernte Präferenzen.
    """

    def __init__(self, state_machine: DialogueStateMachine,
                 user_profile: UserProfile = None,
                 adaptive_config: 'AdaptiveDialogueConfig' = None):
        self.state_machine = state_machine
        self.user_profile = user_profile
        self.adaptive_config = adaptive_config

    def generate_framework(self,
                          intent: str,
                          context: Dict = None) -> Dict[str, Any]:
        """
        Generiere Response-Framework.

        NEU: Nutzt gelernte Präferenzen aus AdaptiveDialogueConfig.

        Returns:
            {
                'tone': str,
                'length': str,
                'structure': List[str],
                'include_question': bool,
                'include_emoji': bool,
                'wolf_action': bool,
                'grounding_element': Optional[str],
            }
        """
        context = context or {}

        # State-basierte Strategie
        strategy = self.state_machine.get_strategy()

        # === ADAPTIVES LERNEN v2.0 ===
        # Hole gelernte Präferenzen wenn verfügbar
        if self.adaptive_config:
            optimal_length = self.adaptive_config.get_optimal_length()
            should_question = self.adaptive_config.should_ask_question()
            use_wolf = self.adaptive_config.should_use_wolf_action()
        else:
            optimal_length = strategy.get('length', 'medium')
            should_question = False
            use_wolf = True

        # Basis-Framework mit gelernten Werten
        framework = {
            'tone': strategy.get('tone', 'neutral'),
            'length': optimal_length,
            'structure': ['main_content'],
            'include_question': should_question,
            'include_emoji': False,
            'wolf_action': use_wolf,
            'grounding_element': None,
        }

        # User-Profil Anpassungen (kann adaptive Werte überschreiben)
        if self.user_profile:
            if self.user_profile.uses_emojis:
                framework['include_emoji'] = True
            # Nur wenn kein adaptives Lernen oder nicht genug Daten
            if not self.adaptive_config or not any(self.adaptive_config.length_success.values()):
                framework['length'] = self.user_profile.preferred_length

        # Intent-basierte Anpassungen
        if intent == "greeting":
            framework['structure'] = ['wolf_action', 'greeting', 'optional_question']
            # Nutze gelernte Frage-Rate statt 50%
            framework['include_question'] = should_question if self.adaptive_config else random.random() < 0.5

        elif intent == "farewell":
            framework['structure'] = ['wolf_action', 'farewell', 'optional_wish']

        elif intent in ["question", "topic_explain", "news"]:
            framework['structure'] = ['wolf_action', 'main_content', 'optional_followup']
            # Nutze gelernte Rate + State-Strategie
            if self.adaptive_config:
                framework['include_question'] = should_question and strategy.get('can_ask_followup', True)
            else:
                framework['include_question'] = strategy.get('can_ask_followup', False)

        elif intent in ["command", "task"]:
            framework['structure'] = ['confirmation', 'action_result']
            framework['wolf_action'] = False  # Fokus auf Ergebnis

        elif intent == "support":
            framework['structure'] = ['empathy_action', 'supportive_message', 'offer_help']
            framework['tone'] = 'empathetic'

        # Grounding wenn nötig
        if context.get('needs_clarification'):
            framework['grounding_element'] = 'clarification_question'
            framework['structure'].append('grounding')

        # === Entscheidungen aufzeichnen für späteres Feedback ===
        if self.adaptive_config:
            self.adaptive_config.record_choice(
                length=framework['length'],
                used_question=framework['include_question'],
                used_wolf_action=framework['wolf_action']
            )

        return framework
    
    def suggest_opening(self, intent: str, emotion: str = "neutral") -> str:
        """Schlage Response-Eröffnung vor"""
        openings = {
            ("greeting", "happy"): "*wedelt freudig*",
            ("greeting", "neutral"): "*hebt den Kopf*",
            ("question", "curious"): "*spitzt die Ohren*",
            ("question", "thinking"): "*überlegt*",
            ("support", "empathetic"): "*stupst sanft an*",
            ("news", "excited"): "*Ohren zucken*",
            ("default", "default"): "*schaut dich an*",
        }
        
        key = (intent, emotion)
        if key in openings:
            return openings[key]
        
        # Fallback
        return openings.get(("default", "default"), "")


# =============================================================================
# HOLO DIALOGUE ENGINE - HAUPTKLASSE
# =============================================================================

class HoloDialogueEngine:
    """
    Hauptklasse für Dialogführung.
    
    Kombiniert alle Komponenten zu einem
    kohärenten Dialogmanagement-System.
    
    Usage:
        engine = HoloDialogueEngine()
        
        # Nachricht verarbeiten
        context = engine.process("Hallo Holo!", intent="greeting")
        
        # Response-Framework holen
        framework = engine.get_response_framework(context)
    """
    
    def __init__(self, user_id: str = "default"):
        # Core Components
        self.state_machine = DialogueStateMachine()
        self.profile_manager = UserProfileManager()
        self.user_profile = self.profile_manager.get_or_create_profile(user_id)

        # === ADAPTIVES LERNEN v2.0 ===
        self.adaptive_config = AdaptiveDialogueConfig()

        # Planning & Goals
        self.planner = ConversationPlanner()

        # Grounding
        self.grounding = GroundingSystem()

        # Turn Taking
        self.turn_manager = TurnTakingManager()

        # Engagement
        self.engagement = EngagementTracker()

        # Response Generation (mit adaptive config)
        self.response_generator = ResponseGenerator(
            self.state_machine,
            self.user_profile,
            self.adaptive_config
        )

        # Stats
        self.conversation_start = time.time()
        self.total_turns = 0

        logger.info(f"[DialogueEngine] Initialisiert für User: {user_id}")
    
    def process(self, message: str, 
                intent: str = "general",
                sentiment: str = "neutral",
                entities: List = None) -> Dict[str, Any]:
        """
        Verarbeite eine User-Nachricht.
        
        Args:
            message: Die Nachricht
            intent: Erkannter Intent
            sentiment: Erkanntes Sentiment
            entities: Extrahierte Entities
            
        Returns:
            Kontext-Dict für Response-Generierung
        """
        self.total_turns += 1
        entities = entities or []
        
        # Turn Management
        self.turn_manager.user_message()
        
        # State Machine Update
        self.state_machine.record_message()
        new_state = self.state_machine.should_transition(intent, sentiment)
        if new_state:
            self.state_machine.transition_to(new_state)
        
        # User Profile Update
        self.profile_manager.update_from_message(message, self.user_profile)
        
        # Goal Detection
        detected_goal = self.planner.detect_goal(message)
        if detected_goal:
            self.planner.add_goal(detected_goal)
        
        # Grounding Check
        topic = entities[0]["value"] if entities else "general"
        understanding = self.grounding.check_understanding(message, topic)
        
        # Engagement
        is_question = "?" in message
        self.engagement.record_message(message, is_question)
        
        # Kontext erstellen
        context = {
            # State
            'dialogue_state': self.state_machine.current_state.name,
            'state_strategy': self.state_machine.get_strategy(),
            'state_duration': self.state_machine.get_state_duration(),
            
            # User
            'user_profile': self.user_profile,
            'user_guidelines': self.profile_manager.get_response_guidelines(),
            
            # Goals
            'current_goal': self.planner.get_current_goal(),
            'next_step': self.planner.suggest_next_step(),
            
            # Grounding
            'understanding': understanding,
            'needs_clarification': self.grounding.needs_clarification(topic),
            
            # Turn
            'timing': self.turn_manager.get_response_timing(),
            'should_wait': self.turn_manager.should_wait_for_more(),
            
            # Engagement
            'engagement_level': self.engagement.get_engagement_level(),
            'engagement_metrics': self.engagement.calculate_metrics(),
            
            # Meta
            'total_turns': self.total_turns,
            'conversation_duration': time.time() - self.conversation_start,
            'intent': intent,
            'sentiment': sentiment,
        }
        
        return context
    
    def get_response_framework(self, context: Dict) -> Dict[str, Any]:
        """
        Hole Response-Framework basierend auf Kontext.
        
        Returns:
            Framework-Dict für Response-Generierung
        """
        intent = context.get('intent', 'general')
        
        # Emotion aus State ableiten
        state = context.get('dialogue_state', 'ACTIVE')
        if state == 'SUPPORT':
            emotion = 'empathetic'
        elif state == 'GREETING':
            emotion = 'happy'
        else:
            emotion = 'neutral'
        
        framework = self.response_generator.generate_framework(
            intent=intent,
            context=context
        )
        
        # Opening hinzufügen
        framework['suggested_opening'] = self.response_generator.suggest_opening(
            intent, emotion
        )
        
        return framework
    
    def record_response(self):
        """Zeichne Holo-Response auf"""
        self.turn_manager.holo_response()
    
    def complete_goal(self, goal: ConversationGoal = None):
        """Markiere aktuelles Goal als erledigt"""
        goal = goal or self.planner.get_current_goal()
        if goal:
            self.planner.complete_goal(goal)
    
    def get_summary(self) -> Dict[str, Any]:
        """Hole Zusammenfassung der Konversation"""
        return {
            'duration_minutes': (time.time() - self.conversation_start) / 60,
            'total_turns': self.total_turns,
            'current_state': self.state_machine.current_state.name,
            'engagement': self.engagement.calculate_metrics(),
            'active_goals': len(self.planner.active_goals),
            'completed_goals': len(self.planner.completed_goals),
            'clarifications_needed': self.grounding.clarification_count,
        }

    # === ADAPTIVES LERNEN v2.0 ===

    def record_response_feedback(self, was_positive: bool) -> None:
        """
        Zeichnet Feedback für die letzte Response auf.

        Args:
            was_positive: War die User-Reaktion positiv?
        """
        if self.adaptive_config:
            self.adaptive_config.record_feedback(was_positive)

    def get_learned_preferences(self) -> Dict[str, Any]:
        """Gibt gelernte Dialog-Präferenzen zurück."""
        if self.adaptive_config:
            return self.adaptive_config.get_learned_stats()
        return {}

    def auto_detect_feedback(self, user_message: str, sentiment: str) -> None:
        """
        Erkennt automatisch Feedback aus User-Nachricht.

        Positive Signale: Bestätigung, Dank, Lob, positive Sentiment
        Negative Signale: Verwirrung, Kritik, negative Sentiment
        """
        if not self.adaptive_config:
            return

        message_lower = user_message.lower()

        # Positive Indikatoren
        positive_indicators = [
            "danke", "super", "toll", "perfekt", "genau", "richtig",
            "verstanden", "cool", "nice", "gut", "hilfreich", "👍"
        ]

        # Negative Indikatoren
        negative_indicators = [
            "verstehe nicht", "was meinst du", "hä", "???",
            "zu lang", "zu kurz", "nervig", "unnötig", "falsch"
        ]

        is_positive = False
        is_negative = False

        if any(ind in message_lower for ind in positive_indicators):
            is_positive = True
        if sentiment in ["positive", "very_positive"]:
            is_positive = True

        if any(ind in message_lower for ind in negative_indicators):
            is_negative = True
        if sentiment in ["negative", "very_negative", "confused"]:
            is_negative = True

        # Nur bei eindeutigem Signal Feedback aufzeichnen
        if is_positive and not is_negative:
            self.adaptive_config.record_feedback(was_positive=True)
        elif is_negative and not is_positive:
            self.adaptive_config.record_feedback(was_positive=False)


# =============================================================================
# FACTORY & HELPERS
# =============================================================================

def create_engine(user_id: str = "default") -> HoloDialogueEngine:
    """Factory für Dialogue Engine"""
    return HoloDialogueEngine(user_id)


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# UserModel ist jetzt UserProfile
UserModel = UserProfile


@dataclass
class DialogueContext:
    """
    LEGACY CLASS - Für Abwärtskompatibilität mit holo_brain.py.
    
    Neue Code sollte HoloDialogueEngine.process() verwenden!
    """
    state: DialogueState = DialogueState.IDLE
    user_profile: UserProfile = None
    current_goal: ConversationGoal = None
    engagement_level: str = "medium"
    needs_clarification: bool = False
    suggested_response_type: str = "normal"
    
    def __post_init__(self):
        if self.user_profile is None:
            self.user_profile = UserProfile()
    
    @classmethod
    def from_engine(cls, engine: HoloDialogueEngine) -> 'DialogueContext':
        """Erstelle DialogueContext aus Engine"""
        return cls(
            state=engine.state_machine.current_state,
            user_profile=engine.user_profile,
            current_goal=engine.planner.get_current_goal(),
            engagement_level=engine.engagement.get_engagement_level(),
            needs_clarification=False,
            suggested_response_type="normal",
        )


class ResponseQualityChecker:
    """
    LEGACY CLASS - Response Quality Checker.
    
    Prüft ob eine Antwort gut ist.
    """
    
    def __init__(self):
        self.min_length = 10
        self.max_length = 500
    
    def check(self, response: str, context: Dict = None) -> Dict:
        """Prüfe Response-Qualität"""
        issues = []
        score = 1.0
        
        # Längencheck
        if len(response) < self.min_length:
            issues.append("too_short")
            score -= 0.3
        elif len(response) > self.max_length:
            issues.append("too_long")
            score -= 0.1
        
        # Leer-Check
        if not response.strip():
            issues.append("empty")
            score = 0.0
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "is_good": score >= 0.7,
        }


# =============================================================================
# ADVANCED DIALOGUE: Topic Tracker
# =============================================================================

class TopicTracker:
    """
    Trackt Topic-Progression durch die Konversation.

    Ermöglicht:
    - Erkennen von Topic-Shifts
    - Kohärenz-Prüfung
    - Topic-Bridges vorschlagen
    """

    def __init__(self):
        # Topic-Historie
        self.topic_history: List[Dict] = []

        # Aktives Topic
        self.current_topic: Optional[str] = None
        self.topic_depth: int = 0

        # Topic-Beziehungen (gelernt)
        self.topic_relations: Dict[str, List[str]] = {}

        # Shift-Detection
        self.shift_threshold: float = 0.5

        logger.info("📌 TopicTracker initialisiert")

    def detect_topic(self, message: str, context: Dict = None) -> Dict:
        """Erkennt das Topic einer Nachricht"""
        message_lower = message.lower()

        # Topic-Keywords
        topic_keywords = {
            "anime": ["anime", "manga", "staffel", "episode", "studio", "japanisch"],
            "gaming": ["spiel", "game", "zocken", "gameplay", "steam", "playstation", "xbox"],
            "tech": ["computer", "software", "code", "programmieren", "app", "website"],
            "personal": ["ich", "mein", "mir", "fühle", "denke", "glaube"],
            "question": ["was", "wie", "warum", "wann", "wo", "wer", "kannst du"],
            "smalltalk": ["hey", "hallo", "wie geht", "was machst", "schönes wetter"],
        }

        # Topic-Scores berechnen
        scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[topic] = score

        # Bestes Topic wählen
        if scores:
            best_topic = max(scores.items(), key=lambda x: x[1])
            detected = best_topic[0]
            confidence = min(1.0, best_topic[1] / 3)
        else:
            detected = "general"
            confidence = 0.3

        return {
            "topic": detected,
            "confidence": confidence,
            "all_scores": scores,
        }

    def update(self, message: str, context: Dict = None) -> Dict:
        """Aktualisiert Topic-Tracking"""
        detection = self.detect_topic(message, context)
        new_topic = detection["topic"]

        # Topic-Shift erkennen
        is_shift = False
        if self.current_topic and new_topic != self.current_topic:
            is_shift = True
            self.topic_depth = 0
        else:
            self.topic_depth += 1

        # Historie aktualisieren
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": new_topic,
            "confidence": detection["confidence"],
            "is_shift": is_shift,
            "previous_topic": self.current_topic,
            "depth": self.topic_depth,
        }
        self.topic_history.append(entry)

        # Topic-Relation lernen
        if is_shift and self.current_topic:
            if self.current_topic not in self.topic_relations:
                self.topic_relations[self.current_topic] = []
            if new_topic not in self.topic_relations[self.current_topic]:
                self.topic_relations[self.current_topic].append(new_topic)

        self.current_topic = new_topic

        # Nur letzte 100
        if len(self.topic_history) > 100:
            self.topic_history = self.topic_history[-100:]

        return entry

    def get_topic_sequence(self) -> List[str]:
        """Gibt Topic-Sequenz zurück"""
        return [h["topic"] for h in self.topic_history]

    def is_coherent(self, new_topic: str = None) -> bool:
        """Prüft ob Topic-Übergang kohärent ist"""
        if not self.current_topic:
            return True

        if new_topic == self.current_topic:
            return True

        # Prüfen ob bekannte Relation
        related = self.topic_relations.get(self.current_topic, [])
        return new_topic in related

    def suggest_bridge(self, from_topic: str, to_topic: str) -> Optional[str]:
        """Schlägt eine Topic-Bridge vor"""
        bridges = {
            ("anime", "gaming"): "Apropos, hast du auch Anime-Spiele gespielt?",
            ("gaming", "anime"): "Das erinnert mich an einen Anime...",
            ("personal", "anime"): "Was schaust du denn so in deiner Freizeit?",
            ("smalltalk", "anime"): "Übrigens, läuft gerade eine interessante Anime-Season!",
            ("tech", "gaming"): "Hast du auch Game-Development Erfahrung?",
        }

        return bridges.get((from_topic, to_topic)) or \
               f"Wollen wir über {to_topic} sprechen?"

    def get_stats(self) -> Dict:
        return {
            "current_topic": self.current_topic,
            "topic_depth": self.topic_depth,
            "total_shifts": sum(1 for h in self.topic_history if h.get("is_shift")),
            "learned_relations": len(self.topic_relations),
        }


# =============================================================================
# ADVANCED DIALOGUE: Conversation Memory
# =============================================================================

class ConversationMemory:
    """
    Multi-Turn Memory für Konversationen.

    Ermöglicht:
    - Kontext-Fenster über mehrere Turns
    - Vermeidung von Wiederholungen
    - Callback auf frühere Punkte
    """

    def __init__(self, max_size: int = 50):
        self.max_size = max_size

        # Exchange-History: (user_msg, holo_response, context)
        self.exchanges: List[Dict] = []

        # Mention-Tracking: Was wurde schon erwähnt
        self.mentioned_topics: Dict[str, int] = {}  # topic -> count
        self.mentioned_entities: Dict[str, int] = {}

        # Repetition-Tracking
        self.recent_responses: List[str] = []

        logger.info("🧠 ConversationMemory initialisiert")

    def add_exchange(self, user_message: str, holo_response: str,
                     context: Dict = None):
        """Fügt einen Exchange hinzu"""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "holo": holo_response,
            "context": context or {},
        }
        self.exchanges.append(exchange)

        # Entities/Topics tracken
        self._track_mentions(user_message)
        self._track_mentions(holo_response)

        # Response-Tracking
        self.recent_responses.append(holo_response[:100])
        if len(self.recent_responses) > 20:
            self.recent_responses = self.recent_responses[-20:]

        # Memory begrenzen
        if len(self.exchanges) > self.max_size:
            self.exchanges = self.exchanges[-self.max_size:]

    def _track_mentions(self, text: str):
        """Trackt erwähnte Topics/Entities"""
        text_lower = text.lower()

        # Einfaches Keyword-Tracking
        keywords = ["anime", "manga", "game", "spiel", "arbeit", "schule", "musik", "film"]
        for kw in keywords:
            if kw in text_lower:
                self.mentioned_topics[kw] = self.mentioned_topics.get(kw, 0) + 1

    def get_context_window(self, depth: int = 5) -> List[Dict]:
        """Gibt die letzten N Exchanges zurück"""
        return self.exchanges[-depth:]

    def detect_repetition(self, response: str, threshold: float = 0.7) -> bool:
        """Prüft ob eine Response zu ähnlich zu kürzlichen ist"""
        response_lower = response.lower()[:100]

        for recent in self.recent_responses[-5:]:
            recent_lower = recent.lower()

            # Einfache Ähnlichkeit (Wort-Overlap)
            response_words = set(response_lower.split())
            recent_words = set(recent_lower.split())

            if not response_words or not recent_words:
                continue

            overlap = len(response_words & recent_words)
            similarity = overlap / max(len(response_words), len(recent_words))

            if similarity >= threshold:
                return True

        return False

    def recall_related(self, query: str, limit: int = 3) -> List[Dict]:
        """Findet verwandte frühere Exchanges"""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored = []
        for exchange in self.exchanges:
            # Relevanz berechnen
            exchange_text = (exchange["user"] + " " + exchange["holo"]).lower()
            exchange_words = set(exchange_text.split())

            overlap = len(query_words & exchange_words)
            if overlap > 0:
                scored.append((exchange, overlap))

        # Nach Relevanz sortieren
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:limit]]

    def get_callback_opportunity(self) -> Optional[Dict]:
        """Findet Gelegenheit auf früheren Punkt zurückzukommen"""
        if len(self.exchanges) < 5:
            return None

        # Suche nach unbeantworteten Fragen
        for exchange in self.exchanges[-10:-3]:
            user_msg = exchange["user"]
            if "?" in user_msg and len(exchange["holo"]) < 50:
                return {
                    "type": "unanswered_question",
                    "original": user_msg,
                    "suggestion": f"Übrigens, du hattest gefragt: '{user_msg[:50]}...'",
                }

        return None

    def get_summary(self) -> Dict:
        """Gibt Zusammenfassung der Konversation"""
        return {
            "total_exchanges": len(self.exchanges),
            "mentioned_topics": dict(self.mentioned_topics),
            "duration_turns": len(self.exchanges),
        }

    def get_stats(self) -> Dict:
        return {
            "exchanges": len(self.exchanges),
            "topics_mentioned": len(self.mentioned_topics),
            "entities_mentioned": len(self.mentioned_entities),
        }


# =============================================================================
# ADVANCED DIALOGUE: Turn Predictor
# =============================================================================

class TurnPredictor:
    """
    Sagt vorher was der User als nächstes tun wird.

    Ermöglicht proaktive Response-Vorbereitung.
    """

    def __init__(self):
        # Intent-Transition-Matrix
        self.transition_counts: Dict[str, Dict[str, int]] = {}

        # Pattern-History
        self.pattern_history: List[Dict] = []

        # Prediction-Tracking
        self.predictions: List[Dict] = []
        self.correct_predictions: int = 0
        self.total_predictions: int = 0

        logger.info("🔮 TurnPredictor initialisiert")

    def record_transition(self, from_intent: str, to_intent: str):
        """Zeichnet Intent-Übergang auf"""
        if from_intent not in self.transition_counts:
            self.transition_counts[from_intent] = {}

        self.transition_counts[from_intent][to_intent] = \
            self.transition_counts[from_intent].get(to_intent, 0) + 1

    def predict_next_intent(self, current_intent: str,
                            context: Dict = None) -> Tuple[str, float]:
        """Sagt nächsten Intent vorher"""
        # Basierend auf Übergängen
        transitions = self.transition_counts.get(current_intent, {})

        if not transitions:
            # Default-Vorhersagen
            defaults = {
                "greeting": ("question", 0.6),
                "question": ("followup", 0.5),
                "statement": ("question", 0.4),
                "gratitude": ("farewell", 0.7),
            }
            return defaults.get(current_intent, ("statement", 0.3))

        # Wahrscheinlichsten Übergang finden
        total = sum(transitions.values())
        best_intent = max(transitions.items(), key=lambda x: x[1])

        confidence = best_intent[1] / total

        # Prediction speichern
        self.predictions.append({
            "timestamp": datetime.now().isoformat(),
            "current_intent": current_intent,
            "predicted_intent": best_intent[0],
            "confidence": confidence,
        })
        self.total_predictions += 1

        return best_intent[0], confidence

    def predict_emotional_trajectory(self, recent_sentiments: List[float]) -> str:
        """Sagt emotionalen Trend vorher"""
        if len(recent_sentiments) < 2:
            return "stable"

        # Trend berechnen
        recent = recent_sentiments[-5:]
        if len(recent) < 2:
            return "stable"

        trend = recent[-1] - recent[0]

        if trend > 0.2:
            return "improving"
        elif trend < -0.2:
            return "declining"
        else:
            return "stable"

    def suggest_proactive_response(self, prediction: str,
                                    confidence: float) -> Optional[str]:
        """Schlägt proaktive Response vor"""
        if confidence < 0.5:
            return None

        suggestions = {
            "question": "Bereite eine informative Antwort vor",
            "followup": "Sei bereit für Vertiefung des Themas",
            "farewell": "Bereite einen herzlichen Abschied vor",
            "gratitude": "Bereite eine bescheidene Antwort vor",
            "complaint": "Bereite empathische Reaktion vor",
        }

        return suggestions.get(prediction)

    def verify_prediction(self, predicted: str, actual: str):
        """Verifiziert eine Vorhersage"""
        if predicted == actual:
            self.correct_predictions += 1

    def get_accuracy(self) -> float:
        """Gibt Vorhersage-Genauigkeit zurück"""
        if self.total_predictions == 0:
            return 0.0
        return self.correct_predictions / self.total_predictions

    def get_stats(self) -> Dict:
        return {
            "total_predictions": self.total_predictions,
            "accuracy": self.get_accuracy(),
            "transitions_learned": len(self.transition_counts),
        }


# =============================================================================
# ADVANCED DIALOGUE: Coherence Validator
# =============================================================================

class CoherenceValidator:
    """
    Validiert Kohärenz über mehrere Turns hinweg.

    Erkennt:
    - Widersprüche
    - Themen-Sprünge
    - Logische Inkonsistenzen
    """

    def __init__(self):
        # Statement-Tracking
        self.statements: List[Dict] = []

        # Coherence-History
        self.coherence_scores: List[float] = []

        logger.info("✅ CoherenceValidator initialisiert")

    def add_statement(self, statement: str, speaker: str, topic: str = None):
        """Fügt ein Statement hinzu"""
        self.statements.append({
            "timestamp": datetime.now().isoformat(),
            "statement": statement,
            "speaker": speaker,
            "topic": topic,
        })

        # Nur letzte 50 behalten
        if len(self.statements) > 50:
            self.statements = self.statements[-50:]

    def check_coherence(self, new_statement: str, context: Dict = None) -> Dict:
        """Prüft Kohärenz eines neuen Statements"""
        result = {
            "is_coherent": True,
            "score": 1.0,
            "issues": [],
            "suggestions": [],
        }

        if len(self.statements) < 2:
            return result

        # Topic-Kohärenz prüfen
        recent_topics = [s.get("topic") for s in self.statements[-5:] if s.get("topic")]
        if recent_topics and context:
            current_topic = context.get("topic")
            if current_topic and current_topic not in recent_topics:
                result["issues"].append("topic_shift")
                result["score"] -= 0.2
                result["suggestions"].append("Consider adding a transition")

        # Längen-Kohärenz (plötzlich viel länger/kürzer)
        recent_lengths = [len(s["statement"]) for s in self.statements[-5:]]
        avg_length = sum(recent_lengths) / len(recent_lengths)
        new_length = len(new_statement)

        if new_length > avg_length * 3 or new_length < avg_length * 0.2:
            result["issues"].append("length_inconsistency")
            result["score"] -= 0.1

        # Final score
        result["is_coherent"] = result["score"] >= 0.7
        self.coherence_scores.append(result["score"])

        return result

    def get_conversation_coherence(self) -> float:
        """Gibt durchschnittliche Kohärenz der Konversation"""
        if not self.coherence_scores:
            return 1.0
        return sum(self.coherence_scores) / len(self.coherence_scores)

    def detect_contradiction(self, statement_a: str, statement_b: str) -> bool:
        """Erkennt Widersprüche zwischen zwei Statements (vereinfacht)"""
        # Einfache Negations-Erkennung
        negations = ["nicht", "kein", "nie", "niemals", "nein"]

        a_lower = statement_a.lower()
        b_lower = statement_b.lower()

        # Wenn eines negiert und ähnliche Wörter
        a_has_neg = any(neg in a_lower for neg in negations)
        b_has_neg = any(neg in b_lower for neg in negations)

        if a_has_neg != b_has_neg:
            # Prüfe Wort-Overlap
            a_words = set(a_lower.split()) - set(negations)
            b_words = set(b_lower.split()) - set(negations)

            overlap = len(a_words & b_words)
            if overlap > 3:  # Signifikanter Overlap mit unterschiedlicher Negation
                return True

        return False

    def get_stats(self) -> Dict:
        return {
            "statements_tracked": len(self.statements),
            "avg_coherence": self.get_conversation_coherence(),
            "checks_performed": len(self.coherence_scores),
        }


# Exports
__all__ = [
    'HoloDialogueEngine',
    'DialogueStateMachine',
    'DialogueState',
    'DialogueContext',
    'DialogueConfig',
    'AdaptiveDialogueConfig',  # NEU v2.0
    'UserProfile',
    'UserModel',
    'UserProfileManager',
    'ConversationPlanner',
    'ConversationGoal',
    'GoalType',
    'GroundingSystem',
    'TurnTakingManager',
    'EngagementTracker',
    'ResponseGenerator',
    'ResponseQualityChecker',
    # NEU v3.0: Advanced Dialogue
    'TopicTracker',
    'ConversationMemory',
    'TurnPredictor',
    'CoherenceValidator',
]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import re
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    print("=" * 70)
    print("🎭 HOLO DIALOGUE ENGINE v2.0 - TEST")
    print("    Dialogue Management & User Modeling")
    print("=" * 70)
    
    engine = HoloDialogueEngine(user_id="kira")
    
    # Simuliere Konversation
    conversation = [
        {"msg": "Hey Holo!", "intent": "greeting", "sentiment": "positive"},
        {"msg": "Ich möchte etwas über Machine Learning lernen.", "intent": "learning", "sentiment": "neutral"},
        {"msg": "Was ist ein Neural Network?", "intent": "question", "sentiment": "curious"},
        {"msg": "Verstehe ich nicht ganz...", "intent": "clarification", "sentiment": "confused"},
        {"msg": "Ah ok, jetzt verstehe ich!", "intent": "confirmation", "sentiment": "positive"},
        {"msg": "Danke, das war sehr hilfreich!", "intent": "gratitude", "sentiment": "positive"},
        {"msg": "Tschüss!", "intent": "farewell", "sentiment": "positive"},
    ]
    
    print("\n📝 DIALOG-SIMULATION:")
    print("-" * 70)
    
    for turn in conversation:
        msg = turn["msg"]
        print(f"\n👤 User: {msg}")
        
        context = engine.process(
            message=msg,
            intent=turn["intent"],
            sentiment=turn["sentiment"]
        )
        
        framework = engine.get_response_framework(context)
        engine.record_response()
        
        print(f"\n   📊 State: {context['dialogue_state']}")
        print(f"   🎯 Goal: {context['current_goal'].goal_type.value if context['current_goal'] else 'None'}")
        print(f"   💭 Next Step: {context['next_step']}")
        print(f"   📈 Engagement: {context['engagement_level']}")
        print(f"   🎭 Framework: tone={framework['tone']}, length={framework['length']}")
        print(f"   🐺 Opening: {framework['suggested_opening']}")
    
    # Summary
    print("\n\n📊 KONVERSATIONS-ZUSAMMENFASSUNG:")
    print("-" * 70)
    
    summary = engine.get_summary()
    print(f"   Dauer: {summary['duration_minutes']:.1f} Minuten")
    print(f"   Turns: {summary['total_turns']}")
    print(f"   End-State: {summary['current_state']}")
    print(f"   Engagement Score: {summary['engagement'].overall_score:.2f}")
    
    # User Profile Test
    print("\n\n👤 USER PROFILE:")
    print("-" * 70)
    
    profile = engine.user_profile
    print(f"   Style: {profile.preferred_style.value}")
    print(f"   Preferred Length: {profile.preferred_length}")
    print(f"   Total Messages: {profile.total_messages}")
    print(f"   Avg Message Length: {profile.avg_message_length:.0f}")
    print(f"   Interests: {profile.interests}")
    
    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
