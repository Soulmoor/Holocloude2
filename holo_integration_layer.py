#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO INTEGRATION LAYER v2.3 - VOLLSTÄNDIGE INTEGRATION                     ║
║                                                                              ║
║  Verbindet ALLE 22 Systeme und aktiviert fehlende Feedback-Loops:           ║
║                                                                              ║
║  🔗 INTEGRATION                                                              ║
║     • SystemIntegrator - Verbindet alle isolierten Module                   ║
║     • BidirectionalBridge - Zwei-Wege-Datenfluss                           ║
║     • UnifiedChangeLog - Zentrale Event-Historie                           ║
║                                                                              ║
║  🔄 FEEDBACK LOOPS                                                           ║
║     • FeedbackOrchestrator - Ruft learn_from_feedback() auf                ║
║     • RewardSignalAggregator - Sammelt Belohnungssignale                   ║
║     • ExperienceCollector - Trackt Erfahrungen für Replay                  ║
║                                                                              ║
║  💾 PERSISTENZ                                                               ║
║     • HistoryPersistence - Speichert alle Histories                        ║
║     • StateSnapshot - Periodische Snapshots                                ║
║     • RecoveryManager - Lädt Zustand nach Neustart                        ║
║                                                                              ║
║  📊 ADAPTIVE THRESHOLDS                                                      ║
║     • AdaptiveThresholdManager - Lernt optimale Schwellwerte               ║
║     • ThresholdOptimizer - Gradient-basierte Optimierung                   ║
║     • PerformanceTracker - Misst Threshold-Effektivität                    ║
║                                                                              ║
║  🧪 A/B TESTING FÜR PERSÖNLICHKEIT                                          ║
║     • PersonalityExperiment - Testet Trait-Variationen                     ║
║     • VariantTracker - Trackt welche Variante aktiv                       ║
║     • ExperimentAnalyzer - Analysiert Ergebnisse                          ║
║                                                                              ║
║  🧠 v2.1: ERWEITERTE SYSTEM-VERBINDUNGEN (5 Systeme)                        ║
║     • EnergySystem → Drive/Dialog - Energie beeinflusst Verhalten          ║
║     • CreativeMind → Dialog/Interests - Kreativität färbt Kommunikation   ║
║     • AutonomousThinking → Dialog - Intuition beeinflusst Tonfall         ║
║     • ImpulseSystem → DriveSystem - Impulse boosten Triebe                ║
║     • PersonOpinions → Dialog - Meinungen färben Antworten                ║
║                                                                              ║
║  💎 v2.2: TIEFE INTEGRATION (3 Systeme)                                     ║
║     • DepthSystem → Dialog - Trust-Level beeinflusst Offenheit            ║
║     • EmotionalComplexity → Dialog - Emotionen in Antworten               ║
║     • Memory → Dialog - Personalisierte Callbacks/Erinnerungen            ║
║                                                                              ║
║  🌟 v2.3: VOLLSTÄNDIGE INTEGRATION (8 Systeme) - NEU!                       ║
║     • ContextMind → Dialog - Relevanter Kontext für Antworten             ║
║     • SelfExpression → Mood - Events/Feiertage beeinflussen Stimmung      ║
║     • InnerLife → Dialog - Tagesphase beeinflusst Energie/Länge           ║
║     • Preferences → Dialog - Vorlieben/Abneigungen färben Antworten       ║
║     • WebCuriosity → Dialog - Gelerntes Wissen einbringen                 ║
║     • SkillSystem → Dialog - Verfügbare Fähigkeiten anbieten              ║
║     • MetaCognition → Behavior - Selbst-Beobachtung → Anpassung           ║
║     • DigitalBody → Dialog - Hardware-Status → Mentaler Zustand           ║
║                                                                              ║
║  Author: Claude (Integration & Verbesserungen)                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import time
import random
import logging
import threading
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger("HoloIntegrationLayer")


# =============================================================================
# UNIFIED CHANGE LOG - Zentrales Event-System
# =============================================================================

class ChangeType(Enum):
    """Typen von Änderungen im System"""
    PERSONALITY_TRAIT = "personality_trait"
    PREFERENCE = "preference"
    BELIEF = "belief"
    OPINION = "opinion"
    MOOD = "mood"
    DRIVE = "drive"
    RELATIONSHIP = "relationship"
    LEARNING = "learning"
    DECISION = "decision"
    FEEDBACK = "feedback"
    THRESHOLD = "threshold"
    EXPERIMENT = "experiment"


@dataclass
class ChangeEvent:
    """Ein einzelnes Änderungs-Event"""
    timestamp: float = field(default_factory=time.time)
    change_type: ChangeType = ChangeType.LEARNING
    source_system: str = ""
    target_system: str = ""
    key: str = ""
    old_value: Any = None
    new_value: Any = None
    delta: float = 0.0
    reason: str = ""
    context: Dict = field(default_factory=dict)
    success: bool = True

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "change_type": self.change_type.value,
            "source_system": self.source_system,
            "target_system": self.target_system,
            "key": self.key,
            "old_value": str(self.old_value)[:100],
            "new_value": str(self.new_value)[:100],
            "delta": self.delta,
            "reason": self.reason,
            "context": {k: str(v)[:50] for k, v in self.context.items()},
            "success": self.success,
        }


class UnifiedChangeLog:
    """
    Zentrales Change-Log das alle Systemänderungen trackt.

    Features:
    - Alle Systeme können Änderungen loggen
    - Cross-System Analyse möglich
    - Persistenz-fähig
    - Listener für Reaktionen auf Änderungen
    """

    def __init__(self, max_entries: int = 10000, persist_path: str = None):
        self.events: deque = deque(maxlen=max_entries)
        self.persist_path = Path(persist_path) if persist_path else None
        self.listeners: Dict[ChangeType, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()

        # Statistiken
        self.stats = defaultdict(lambda: {"count": 0, "last": 0})

    def log(self, event: ChangeEvent) -> None:
        """Logge eine Änderung"""
        with self._lock:
            self.events.append(event)
            self.stats[event.change_type.value]["count"] += 1
            self.stats[event.change_type.value]["last"] = event.timestamp

        # Listener benachrichtigen
        for listener in self.listeners.get(event.change_type, []):
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Listener error: {e}")

    def log_change(self,
                   change_type: ChangeType,
                   source: str,
                   key: str,
                   old_value: Any,
                   new_value: Any,
                   reason: str = "",
                   context: Dict = None) -> ChangeEvent:
        """Convenience-Methode für Änderungen"""
        delta = 0.0
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            delta = new_value - old_value

        event = ChangeEvent(
            change_type=change_type,
            source_system=source,
            key=key,
            old_value=old_value,
            new_value=new_value,
            delta=delta,
            reason=reason,
            context=context or {},
        )
        self.log(event)
        return event

    def subscribe(self, change_type: ChangeType, callback: Callable) -> None:
        """Subscriben auf bestimmte Änderungstypen"""
        self.listeners[change_type].append(callback)

    def get_recent(self, hours: float = 24,
                   change_type: ChangeType = None) -> List[ChangeEvent]:
        """Hole kürzliche Änderungen"""
        cutoff = time.time() - (hours * 3600)
        with self._lock:
            events = list(self.events)

        filtered = [e for e in events if e.timestamp >= cutoff]
        if change_type:
            filtered = [e for e in filtered if e.change_type == change_type]
        return filtered

    def get_by_key(self, key: str, limit: int = 100) -> List[ChangeEvent]:
        """Hole Änderungen für einen bestimmten Key"""
        with self._lock:
            events = [e for e in self.events if e.key == key]
        return events[-limit:]

    def get_trend(self, key: str, hours: float = 24) -> Dict:
        """Analysiere Trend für einen Key"""
        events = self.get_by_key(key)
        cutoff = time.time() - (hours * 3600)
        recent = [e for e in events if e.timestamp >= cutoff]

        if not recent:
            return {"trend": "stable", "changes": 0, "net_delta": 0}

        deltas = [e.delta for e in recent if e.delta != 0]
        net_delta = sum(deltas)

        trend = "stable"
        if net_delta > 0.1:
            trend = "increasing"
        elif net_delta < -0.1:
            trend = "decreasing"

        return {
            "trend": trend,
            "changes": len(recent),
            "net_delta": net_delta,
            "avg_delta": statistics.mean(deltas) if deltas else 0,
        }

    def save(self) -> None:
        """Speichere Log"""
        if not self.persist_path:
            return

        data = {
            "events": [e.to_dict() for e in self.events],
            "stats": dict(self.stats),
            "saved_at": time.time(),
        }

        with open(self.persist_path, 'w') as f:
            json.dump(data, f)

    def load(self) -> None:
        """Lade Log"""
        if not self.persist_path or not self.persist_path.exists():
            return

        try:
            with open(self.persist_path) as f:
                data = json.load(f)

            # Events rekonstruieren (vereinfacht)
            for event_data in data.get("events", []):
                event = ChangeEvent(
                    timestamp=event_data.get("timestamp", 0),
                    change_type=ChangeType(event_data.get("change_type", "learning")),
                    source_system=event_data.get("source_system", ""),
                    key=event_data.get("key", ""),
                    reason=event_data.get("reason", ""),
                    delta=event_data.get("delta", 0),
                )
                self.events.append(event)

        except Exception as e:
            logger.error(f"Fehler beim Laden des ChangeLogs: {e}")


# =============================================================================
# ADAPTIVE THRESHOLDS - Lernbare Schwellwerte
# =============================================================================

@dataclass
class AdaptiveThreshold:
    """Ein lernbarer Schwellwert"""
    name: str
    current_value: float
    default_value: float
    min_value: float = 0.0
    max_value: float = 1.0
    learning_rate: float = 0.01

    # Tracking
    adjustments: int = 0
    successes: int = 0
    failures: int = 0
    history: List[Tuple[float, float, bool]] = field(default_factory=list)

    def update(self, outcome_positive: bool, magnitude: float = 1.0) -> float:
        """
        Update Threshold basierend auf Outcome.

        Wenn Outcome positiv: Threshold war gut → weniger ändern
        Wenn Outcome negativ: Threshold anpassen
        """
        old_value = self.current_value

        if outcome_positive:
            self.successes += 1
            # Leicht in Richtung des aktuellen Werts verstärken
            adjustment = self.learning_rate * 0.1 * magnitude
        else:
            self.failures += 1
            # Stärker anpassen wenn es nicht funktioniert
            # Richtung: Wenn zu hoch → senken, wenn zu niedrig → erhöhen
            # (Heuristik: alterniere Richtung bei Fehlschlägen)
            direction = 1 if random.random() > 0.5 else -1
            adjustment = direction * self.learning_rate * magnitude

        self.current_value = max(
            self.min_value,
            min(self.max_value, self.current_value + adjustment)
        )

        self.adjustments += 1
        self.history.append((old_value, self.current_value, outcome_positive))

        # History begrenzen
        if len(self.history) > 100:
            self.history = self.history[-100:]

        return self.current_value

    def get_success_rate(self) -> float:
        """Erfolgsrate"""
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.5

    def reset_to_default(self) -> None:
        """Zurücksetzen auf Default"""
        self.current_value = self.default_value


class AdaptiveThresholdManager:
    """
    Verwaltet alle adaptiven Schwellwerte.

    Ersetzt hardcodierte Werte durch lernende Thresholds.
    """

    # Standard-Thresholds die adaptiert werden sollen
    DEFAULT_THRESHOLDS = {
        # Drive System
        "drain_per_minute": (0.017, 0.005, 0.05),
        "regen_per_minute": (0.004, 0.001, 0.02),
        "low_energy_threshold": (0.20, 0.10, 0.40),
        "nap_regen_rate": (0.008, 0.002, 0.03),

        # Emotion/Mood
        "emotion_decay_per_hour": (0.1, 0.02, 0.3),
        "mood_influence_factor": (0.5, 0.1, 1.0),

        # Understanding
        "fuzzy_match_threshold": (0.85, 0.6, 0.99),
        "keyword_confidence_threshold": (0.6, 0.3, 0.9),

        # Depth System
        "defense_trigger_threshold": (0.6, 0.3, 0.9),
        "trust_layer_social": (0.4, 0.2, 0.6),
        "trust_layer_comfortable": (0.7, 0.5, 0.85),
        "trust_layer_vulnerable": (0.9, 0.75, 0.98),

        # Personality
        "spontaneity_chance": (0.15, 0.05, 0.35),
        "quirk_chance": (0.15, 0.05, 0.30),
        "callback_chance": (0.10, 0.03, 0.25),

        # Policy Engine
        "exploration_epsilon": (0.15, 0.03, 0.30),
        "learning_rate": (0.1, 0.01, 0.3),

        # Opinion Formation
        "opinion_formation_threshold": (5, 2, 15),  # Erfahrungen bis Meinung
        "opinion_decay_rate": (0.05, 0.01, 0.15),
    }

    def __init__(self, change_log: UnifiedChangeLog = None):
        self.thresholds: Dict[str, AdaptiveThreshold] = {}
        self.change_log = change_log

        # Initialisiere Standard-Thresholds
        for name, (default, min_val, max_val) in self.DEFAULT_THRESHOLDS.items():
            self.thresholds[name] = AdaptiveThreshold(
                name=name,
                current_value=default,
                default_value=default,
                min_value=min_val,
                max_value=max_val,
            )

    def get(self, name: str) -> float:
        """Hole aktuellen Threshold-Wert"""
        if name in self.thresholds:
            return self.thresholds[name].current_value
        return self.DEFAULT_THRESHOLDS.get(name, (0.5,))[0]

    def update(self, name: str, outcome_positive: bool,
               magnitude: float = 1.0, reason: str = "") -> float:
        """Update Threshold basierend auf Outcome"""
        if name not in self.thresholds:
            return self.get(name)

        threshold = self.thresholds[name]
        old_value = threshold.current_value
        new_value = threshold.update(outcome_positive, magnitude)

        # Log die Änderung
        if self.change_log and abs(new_value - old_value) > 0.001:
            self.change_log.log_change(
                change_type=ChangeType.THRESHOLD,
                source="threshold_manager",
                key=name,
                old_value=old_value,
                new_value=new_value,
                reason=reason or f"outcome={'positive' if outcome_positive else 'negative'}",
            )

        return new_value

    def get_all(self) -> Dict[str, float]:
        """Hole alle aktuellen Threshold-Werte"""
        return {name: t.current_value for name, t in self.thresholds.items()}

    def get_stats(self) -> Dict[str, Dict]:
        """Hole Statistiken für alle Thresholds"""
        return {
            name: {
                "current": t.current_value,
                "default": t.default_value,
                "success_rate": t.get_success_rate(),
                "adjustments": t.adjustments,
            }
            for name, t in self.thresholds.items()
        }

    def save(self, path: str) -> None:
        """Speichere Thresholds"""
        data = {}
        for name, t in self.thresholds.items():
            data[name] = {
                "current_value": t.current_value,
                "successes": t.successes,
                "failures": t.failures,
                "adjustments": t.adjustments,
            }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> None:
        """Lade Thresholds"""
        if not Path(path).exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for name, values in data.items():
                if name in self.thresholds:
                    self.thresholds[name].current_value = values.get(
                        "current_value",
                        self.thresholds[name].default_value
                    )
                    self.thresholds[name].successes = values.get("successes", 0)
                    self.thresholds[name].failures = values.get("failures", 0)
                    self.thresholds[name].adjustments = values.get("adjustments", 0)

        except Exception as e:
            logger.error(f"Fehler beim Laden der Thresholds: {e}")


# =============================================================================
# A/B TESTING FÜR PERSÖNLICHKEIT
# =============================================================================

@dataclass
class PersonalityVariant:
    """Eine Persönlichkeits-Variante für A/B Testing"""
    name: str
    traits: Dict[str, float]  # trait_name → modifier
    active: bool = False

    # Tracking
    interactions: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    total_reward: float = 0.0

    def get_success_rate(self) -> float:
        total = self.positive_feedback + self.negative_feedback
        return self.positive_feedback / total if total > 0 else 0.5

    def get_avg_reward(self) -> float:
        return self.total_reward / self.interactions if self.interactions > 0 else 0.0


@dataclass
class PersonalityExperiment:
    """Ein A/B Experiment für Persönlichkeits-Traits"""
    name: str
    trait_key: str
    variant_a: PersonalityVariant
    variant_b: PersonalityVariant

    # Experiment-Status
    started_at: float = field(default_factory=time.time)
    min_interactions: int = 50
    confidence_threshold: float = 0.95
    concluded: bool = False
    winner: Optional[str] = None

    def get_current_variant(self) -> PersonalityVariant:
        """Hole aktive Variante (Thompson Sampling)"""
        # Beta-Verteilung für jede Variante
        a_sample = random.betavariate(
            max(1, self.variant_a.positive_feedback + 1),
            max(1, self.variant_a.negative_feedback + 1)
        )
        b_sample = random.betavariate(
            max(1, self.variant_b.positive_feedback + 1),
            max(1, self.variant_b.negative_feedback + 1)
        )

        if a_sample > b_sample:
            self.variant_a.active = True
            self.variant_b.active = False
            return self.variant_a
        else:
            self.variant_a.active = False
            self.variant_b.active = True
            return self.variant_b

    def record_outcome(self, positive: bool, reward: float = 0.0) -> None:
        """Erfasse Outcome für aktive Variante"""
        active = self.variant_a if self.variant_a.active else self.variant_b
        active.interactions += 1
        active.total_reward += reward

        if positive:
            active.positive_feedback += 1
        else:
            active.negative_feedback += 1

        # Prüfe ob Experiment abgeschlossen
        self._check_conclusion()

    def _check_conclusion(self) -> None:
        """Prüfe ob Experiment abgeschlossen werden kann"""
        total_a = self.variant_a.positive_feedback + self.variant_a.negative_feedback
        total_b = self.variant_b.positive_feedback + self.variant_b.negative_feedback

        if total_a < self.min_interactions or total_b < self.min_interactions:
            return

        # Einfacher Signifikanztest
        rate_a = self.variant_a.get_success_rate()
        rate_b = self.variant_b.get_success_rate()

        # Wenn ein klarer Gewinner (> 10% Unterschied mit genug Daten)
        if abs(rate_a - rate_b) > 0.10:
            self.concluded = True
            self.winner = "A" if rate_a > rate_b else "B"

    def get_status(self) -> Dict:
        """Hole Experiment-Status"""
        return {
            "name": self.name,
            "trait": self.trait_key,
            "variant_a": {
                "name": self.variant_a.name,
                "interactions": self.variant_a.interactions,
                "success_rate": self.variant_a.get_success_rate(),
                "avg_reward": self.variant_a.get_avg_reward(),
            },
            "variant_b": {
                "name": self.variant_b.name,
                "interactions": self.variant_b.interactions,
                "success_rate": self.variant_b.get_success_rate(),
                "avg_reward": self.variant_b.get_avg_reward(),
            },
            "concluded": self.concluded,
            "winner": self.winner,
        }


class PersonalityABTester:
    """
    Führt A/B Tests für Persönlichkeits-Anpassungen durch.

    Ermöglicht sichere Experimente mit Trait-Änderungen.
    """

    def __init__(self, change_log: UnifiedChangeLog = None):
        self.experiments: Dict[str, PersonalityExperiment] = {}
        self.change_log = change_log
        self.concluded_experiments: List[Dict] = []

    def create_experiment(self,
                          name: str,
                          trait_key: str,
                          variant_a_modifier: float,
                          variant_b_modifier: float,
                          min_interactions: int = 50) -> PersonalityExperiment:
        """Erstelle neues Experiment"""
        experiment = PersonalityExperiment(
            name=name,
            trait_key=trait_key,
            variant_a=PersonalityVariant(
                name=f"{name}_A",
                traits={trait_key: variant_a_modifier}
            ),
            variant_b=PersonalityVariant(
                name=f"{name}_B",
                traits={trait_key: variant_b_modifier}
            ),
            min_interactions=min_interactions,
        )

        self.experiments[name] = experiment

        if self.change_log:
            self.change_log.log_change(
                change_type=ChangeType.EXPERIMENT,
                source="ab_tester",
                key=name,
                old_value=None,
                new_value=f"A={variant_a_modifier}, B={variant_b_modifier}",
                reason=f"Experiment gestartet für {trait_key}",
            )

        return experiment

    def get_trait_modifier(self, trait_key: str) -> float:
        """
        Hole aktuellen Trait-Modifier basierend auf aktiven Experimenten.

        Returns 0.0 wenn kein Experiment läuft.
        """
        for exp in self.experiments.values():
            if exp.trait_key == trait_key and not exp.concluded:
                variant = exp.get_current_variant()
                return variant.traits.get(trait_key, 0.0)
        return 0.0

    def record_feedback(self, positive: bool, reward: float = 0.0) -> None:
        """Erfasse Feedback für alle aktiven Experimente"""
        for exp in self.experiments.values():
            if not exp.concluded:
                was_concluded = exp.concluded
                exp.record_outcome(positive, reward)

                # Experiment abgeschlossen?
                if exp.concluded and not was_concluded:
                    self._handle_conclusion(exp)

    def _handle_conclusion(self, experiment: PersonalityExperiment) -> None:
        """Handle abgeschlossenes Experiment"""
        status = experiment.get_status()
        self.concluded_experiments.append(status)

        if self.change_log:
            winner_variant = (
                experiment.variant_a if experiment.winner == "A"
                else experiment.variant_b
            )
            self.change_log.log_change(
                change_type=ChangeType.EXPERIMENT,
                source="ab_tester",
                key=experiment.name,
                old_value="running",
                new_value=f"concluded: {experiment.winner}",
                reason=f"Winner: {winner_variant.name} mit "
                       f"{winner_variant.get_success_rate():.1%} Erfolgsrate",
            )

        logger.info(
            f"🧪 Experiment '{experiment.name}' abgeschlossen! "
            f"Gewinner: {experiment.winner}"
        )

    def get_active_experiments(self) -> List[Dict]:
        """Hole alle aktiven Experimente"""
        return [
            exp.get_status()
            for exp in self.experiments.values()
            if not exp.concluded
        ]

    def get_recommendations(self) -> List[Dict]:
        """Hole Empfehlungen aus abgeschlossenen Experimenten"""
        recommendations = []
        for status in self.concluded_experiments:
            if status["winner"]:
                winner_data = status[f"variant_{status['winner'].lower()}"]
                recommendations.append({
                    "trait": status["trait"],
                    "recommendation": f"Nutze Variante {status['winner']}",
                    "success_rate": winner_data["success_rate"],
                    "based_on": winner_data["interactions"],
                })
        return recommendations


# =============================================================================
# FEEDBACK ORCHESTRATOR - Aktiviert alle Feedback Loops
# =============================================================================

class FeedbackOrchestrator:
    """
    Orchestriert alle Feedback-Loops im System.

    Stellt sicher, dass learn_from_feedback() etc. tatsächlich aufgerufen werden.
    """

    def __init__(self, change_log: UnifiedChangeLog = None):
        self.change_log = change_log

        # Referenzen zu den verschiedenen Systemen (werden von außen gesetzt)
        self.policy_engine = None
        self.speech_engine = None
        self.preference_manager = None
        self.drive_system = None
        self.personality = None
        self.consciousness = None
        self.depth_system = None
        self.inner_life = None
        self.creative_mind = None
        self.energy_system = None

        # Feedback-History
        self.feedback_history: deque = deque(maxlen=1000)

        # Aggregierte Signale
        self.reward_signals: Dict[str, List[float]] = defaultdict(list)

    def connect_system(self, system_name: str, system: Any) -> None:
        """Verbinde ein System"""
        if hasattr(self, system_name):
            setattr(self, system_name, system)
            logger.info(f"✅ FeedbackOrchestrator: {system_name} verbunden")

    def process_feedback(self,
                         feedback_type: str,
                         positive: bool,
                         magnitude: float = 1.0,
                         context: Dict = None) -> Dict:
        """
        Verarbeite Feedback und leite an alle relevanten Systeme weiter.

        Args:
            feedback_type: Art des Feedbacks (user_reaction, conversation_end, etc.)
            positive: War das Feedback positiv?
            magnitude: Stärke des Feedbacks (0-1)
            context: Zusätzlicher Kontext

        Returns:
            Dict mit Verarbeitungs-Ergebnissen
        """
        context = context or {}
        results = {}
        reward = magnitude if positive else -magnitude

        # Speichere Feedback
        feedback_event = {
            "timestamp": time.time(),
            "type": feedback_type,
            "positive": positive,
            "magnitude": magnitude,
            "context": context,
        }
        self.feedback_history.append(feedback_event)

        # 1. Policy Engine
        if self.policy_engine and hasattr(self.policy_engine, 'learn_from_feedback'):
            try:
                self.policy_engine.learn_from_feedback(
                    reward=reward,
                    context=context
                )
                results["policy_engine"] = "updated"
            except Exception as e:
                logger.error(f"Policy Engine Feedback Error: {e}")
                results["policy_engine"] = f"error: {e}"

        # 2. Speech Engine
        if self.speech_engine and hasattr(self.speech_engine, 'learn_from_feedback'):
            try:
                self.speech_engine.learn_from_feedback(
                    positive=positive,
                    context=context
                )
                results["speech_engine"] = "updated"
            except Exception as e:
                logger.error(f"Speech Engine Feedback Error: {e}")
                results["speech_engine"] = f"error: {e}"

        # 3. Preference Manager
        if self.preference_manager and hasattr(self.preference_manager, 'update_preference_from_experience'):
            try:
                topic = context.get("topic")
                if topic:
                    self.preference_manager.update_preference_from_experience(
                        topic=topic,
                        outcome_positive=positive,
                        strength=magnitude
                    )
                    results["preference_manager"] = "updated"
            except Exception as e:
                logger.error(f"Preference Manager Feedback Error: {e}")
                results["preference_manager"] = f"error: {e}"

        # 4. Consciousness - Opinion Formation
        if self.consciousness and hasattr(self.consciousness, 'opinion_formation'):
            try:
                topic = context.get("topic")
                if topic and hasattr(self.consciousness.opinion_formation, 'record_experience'):
                    self.consciousness.opinion_formation.record_experience(
                        topic=topic,
                        positive=positive
                    )
                    results["consciousness"] = "updated"
            except Exception as e:
                logger.error(f"Consciousness Feedback Error: {e}")
                results["consciousness"] = f"error: {e}"

        # 5. Inner Life - Activity Learning
        if self.inner_life and hasattr(self.inner_life, 'learn_activity_outcome'):
            try:
                activity = context.get("activity")
                if activity:
                    self.inner_life.learn_activity_outcome(
                        activity=activity,
                        success=positive
                    )
                    results["inner_life"] = "updated"
            except Exception as e:
                logger.error(f"Inner Life Feedback Error: {e}")
                results["inner_life"] = f"error: {e}"

        # 6. Creative Mind
        if self.creative_mind and hasattr(self.creative_mind, 'update_from_interaction'):
            try:
                self.creative_mind.update_from_interaction(
                    positive=positive,
                    context=context
                )
                results["creative_mind"] = "updated"
            except Exception as e:
                logger.error(f"Creative Mind Feedback Error: {e}")
                results["creative_mind"] = f"error: {e}"

        # Log in ChangeLog
        if self.change_log:
            self.change_log.log_change(
                change_type=ChangeType.FEEDBACK,
                source="feedback_orchestrator",
                key=feedback_type,
                old_value=None,
                new_value=positive,
                reason=f"magnitude={magnitude:.2f}",
                context={"results": results}
            )

        return results

    def process_conversation_end(self,
                                  conversation_summary: Dict,
                                  user_satisfaction: float = 0.5) -> Dict:
        """
        Verarbeite Gesprächsende.

        Ruft learn_from_conversation_end() auf allen Systemen auf.
        """
        results = {}

        # Policy Engine
        if self.policy_engine and hasattr(self.policy_engine, 'learn_from_conversation_end'):
            try:
                self.policy_engine.learn_from_conversation_end(
                    summary=conversation_summary,
                    satisfaction=user_satisfaction
                )
                results["policy_engine"] = "learned"
            except Exception as e:
                logger.error(f"Policy Engine conversation_end Error: {e}")

        # Depth System - Beziehungswachstum
        if self.depth_system and hasattr(self.depth_system, 'process_interaction'):
            try:
                self.depth_system.process_interaction(
                    interaction_quality=user_satisfaction
                )
                results["depth_system"] = "updated"
            except Exception as e:
                logger.error(f"Depth System Error: {e}")

        # Energy System
        if self.energy_system and hasattr(self.energy_system, 'process_conversation'):
            try:
                self.energy_system.process_conversation(
                    message_count=conversation_summary.get("message_count", 0),
                    emotional_intensity=conversation_summary.get("emotional_intensity", 0.5)
                )
                results["energy_system"] = "updated"
            except Exception as e:
                logger.error(f"Energy System Error: {e}")

        return results

    def aggregate_reward_signal(self, source: str, reward: float) -> None:
        """Sammle Reward-Signal für spätere Batch-Verarbeitung"""
        self.reward_signals[source].append(reward)

        # Verarbeite wenn genug Signale
        if len(self.reward_signals[source]) >= 10:
            self._process_aggregated_rewards(source)

    def _process_aggregated_rewards(self, source: str) -> None:
        """Verarbeite aggregierte Rewards"""
        rewards = self.reward_signals[source]
        if not rewards:
            return

        avg_reward = statistics.mean(rewards)

        # Update Thresholds basierend auf durchschnittlichem Reward
        # (wird von SystemIntegrator aufgerufen)

        self.reward_signals[source] = []

    def get_recent_feedback_stats(self, hours: float = 24) -> Dict:
        """Hole Feedback-Statistiken"""
        cutoff = time.time() - (hours * 3600)
        recent = [f for f in self.feedback_history if f["timestamp"] >= cutoff]

        if not recent:
            return {"count": 0, "positive_rate": 0.5}

        positive_count = sum(1 for f in recent if f["positive"])

        return {
            "count": len(recent),
            "positive_count": positive_count,
            "negative_count": len(recent) - positive_count,
            "positive_rate": positive_count / len(recent),
            "avg_magnitude": statistics.mean(f["magnitude"] for f in recent),
        }


# =============================================================================
# HISTORY PERSISTENCE - Speichert alle Histories (JSON + Datenbank)
# =============================================================================

class HistoryPersistence:
    """
    Zentrales Persistenz-System für alle Histories.

    Unterstützt zwei Modi:
    - JSON-Dateien (Fallback)
    - SQLite Datenbank (wenn HoloDatabaseManager verfügbar)

    Speichert und lädt:
    - mood_history
    - activity_history
    - initiative_history
    - reflection_history
    - contemplation_history
    - thought_history
    - experience_buffer
    - und mehr...
    """

    def __init__(self, base_path: str = "data/histories", db=None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Datenbank-Verbindung (optional)
        self.db = db  # HoloDatabaseManager

        # Registrierte Histories
        self.histories: Dict[str, Tuple[Any, str]] = {}  # name → (object, attribute)

        # Auto-Save Konfiguration
        self.auto_save_interval = 300  # 5 Minuten
        self.last_save = time.time()

        # Initialisiere DB-Tabellen wenn verfügbar
        if self.db:
            self._init_db_tables()

    def connect_database(self, db) -> None:
        """Verbinde mit HoloDatabaseManager für DB-Persistenz"""
        self.db = db
        self._init_db_tables()
        logger.info("✅ HistoryPersistence mit Datenbank verbunden")

    def _init_db_tables(self) -> None:
        """Erstelle DB-Tabellen für Histories wenn nötig"""
        if not self.db:
            return

        try:
            # Tabelle für generische History-Speicherung
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS integration_histories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    entry_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name)
                )
            ''')

            # Tabelle für Change Log Events
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS change_log_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    change_type TEXT NOT NULL,
                    source_system TEXT,
                    target_system TEXT,
                    key TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    delta REAL DEFAULT 0,
                    reason TEXT,
                    context_json TEXT,
                    success INTEGER DEFAULT 1
                )
            ''')

            # Tabelle für Adaptive Thresholds
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS adaptive_thresholds (
                    name TEXT PRIMARY KEY,
                    current_value REAL NOT NULL,
                    default_value REAL NOT NULL,
                    min_value REAL DEFAULT 0,
                    max_value REAL DEFAULT 1,
                    successes INTEGER DEFAULT 0,
                    failures INTEGER DEFAULT 0,
                    adjustments INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabelle für A/B Experimente
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS personality_experiments (
                    name TEXT PRIMARY KEY,
                    trait_key TEXT NOT NULL,
                    variant_a_modifier REAL NOT NULL,
                    variant_b_modifier REAL NOT NULL,
                    variant_a_interactions INTEGER DEFAULT 0,
                    variant_a_positive INTEGER DEFAULT 0,
                    variant_a_negative INTEGER DEFAULT 0,
                    variant_a_reward REAL DEFAULT 0,
                    variant_b_interactions INTEGER DEFAULT 0,
                    variant_b_positive INTEGER DEFAULT 0,
                    variant_b_negative INTEGER DEFAULT 0,
                    variant_b_reward REAL DEFAULT 0,
                    started_at REAL,
                    concluded INTEGER DEFAULT 0,
                    winner TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Indizes für Performance
            self.db.execute('''
                CREATE INDEX IF NOT EXISTS idx_change_log_timestamp
                ON change_log_events(timestamp)
            ''')
            self.db.execute('''
                CREATE INDEX IF NOT EXISTS idx_change_log_type
                ON change_log_events(change_type)
            ''')

            logger.info("✅ DB-Tabellen für Integration initialisiert")

        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der DB-Tabellen: {e}")

    def register(self, name: str, obj: Any, attribute: str) -> None:
        """
        Registriere eine History für Persistenz.

        Args:
            name: Eindeutiger Name
            obj: Objekt das die History enthält
            attribute: Attribut-Name der History
        """
        self.histories[name] = (obj, attribute)
        logger.debug(f"History registriert: {name}")

    def save_all(self) -> Dict[str, bool]:
        """Speichere alle registrierten Histories (DB oder JSON)"""
        results = {}

        for name, (obj, attr) in self.histories.items():
            try:
                history = getattr(obj, attr, None)
                if history is None:
                    results[name] = False
                    continue

                # Konvertiere zu serialisierbarem Format
                data = self._serialize(history)

                # Speichern in DB wenn verfügbar
                if self.db:
                    self._save_to_db(name, data)
                else:
                    # Fallback: JSON-Datei
                    path = self.base_path / f"{name}.json"
                    with open(path, 'w') as f:
                        json.dump(data, f, default=str)

                results[name] = True

            except Exception as e:
                logger.error(f"Fehler beim Speichern von {name}: {e}")
                results[name] = False

        self.last_save = time.time()
        return results

    def _save_to_db(self, name: str, data: Any) -> None:
        """Speichere History in Datenbank"""
        import hashlib
        data_json = json.dumps(data, default=str)
        entry_count = len(data) if isinstance(data, (list, dict)) else 1
        history_id = hashlib.md5(name.encode()).hexdigest()[:16]

        self.db.execute('''
            INSERT OR REPLACE INTO integration_histories
            (id, name, data_json, entry_count, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (history_id, name, data_json, entry_count))

    def load_all(self) -> Dict[str, bool]:
        """Lade alle registrierten Histories (DB oder JSON)"""
        results = {}

        for name, (obj, attr) in self.histories.items():
            try:
                data = None

                # Laden aus DB wenn verfügbar
                if self.db:
                    data = self._load_from_db(name)

                # Fallback: JSON-Datei
                if data is None:
                    path = self.base_path / f"{name}.json"
                    if path.exists():
                        with open(path) as f:
                            data = json.load(f)

                if data is None:
                    results[name] = False
                    continue

                # Setze auf Objekt
                history = self._deserialize(data, attr)
                setattr(obj, attr, history)

                results[name] = True

            except Exception as e:
                logger.error(f"Fehler beim Laden von {name}: {e}")
                results[name] = False

        return results

    def _load_from_db(self, name: str) -> Optional[Any]:
        """Lade History aus Datenbank"""
        try:
            row = self.db.fetchone('''
                SELECT data_json FROM integration_histories WHERE name = ?
            ''', (name,))

            if row:
                return json.loads(row['data_json'])
            return None

        except Exception as e:
            logger.debug(f"DB-Load für {name} fehlgeschlagen: {e}")
            return None

    def _serialize(self, data: Any) -> Any:
        """Serialisiere Daten für JSON"""
        if isinstance(data, deque):
            return {"_type": "deque", "data": list(data), "maxlen": data.maxlen}
        elif isinstance(data, list):
            return [self._serialize(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}
        elif hasattr(data, 'to_dict'):
            return {"_type": "dataclass", "data": data.to_dict()}
        elif hasattr(data, '__dict__'):
            return {"_type": "object", "data": data.__dict__}
        else:
            return data

    def _deserialize(self, data: Any, context: str = "") -> Any:
        """Deserialisiere Daten von JSON"""
        if isinstance(data, dict):
            if data.get("_type") == "deque":
                return deque(data["data"], maxlen=data.get("maxlen"))
            elif data.get("_type") == "dataclass":
                return data["data"]  # Vereinfacht
            elif data.get("_type") == "object":
                return data["data"]  # Vereinfacht
            else:
                return {k: self._deserialize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deserialize(item) for item in data]
        else:
            return data

    def should_auto_save(self) -> bool:
        """Prüfe ob Auto-Save fällig ist"""
        return time.time() - self.last_save >= self.auto_save_interval

    def create_snapshot(self, name: str = None) -> str:
        """Erstelle Snapshot aller Histories"""
        snapshot_name = name or datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = self.base_path / "snapshots" / snapshot_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        for hist_name, (obj, attr) in self.histories.items():
            try:
                history = getattr(obj, attr, None)
                if history:
                    data = self._serialize(history)
                    with open(snapshot_dir / f"{hist_name}.json", 'w') as f:
                        json.dump(data, f, default=str)
            except Exception as e:
                logger.error(f"Snapshot-Fehler für {hist_name}: {e}")

        return str(snapshot_dir)


# =============================================================================
# UNIFIED STORAGE - Zentrales Speichersystem für ALLE Module
# =============================================================================

class UnifiedStorage:
    """
    Zentrales Speichersystem das JSON-Dateien durch DB ersetzt.

    Features:
    - Zentrale DB-Tabelle für alle Module
    - Automatische Migration von JSON-Dateien
    - Kompatible API mit bestehenden save/load Patterns
    - Versionierung und Backup

    Ersetzt:
    - holo_policy_state.json
    - holo_autonomous_state.json
    - holo_consciousness.json
    - learned_poems.json, learned_stories.json, etc.
    - Alle anderen JSON-State-Dateien
    """

    # Bekannte JSON-Dateien und ihre Modul-Zuordnung
    KNOWN_STATE_FILES = {
        "holo_policy_state.json": "policy_engine",
        "holo_autonomous_state.json": "inner_life",
        "holo_consciousness.json": "consciousness",
        "learned_poems.json": "creative_learning",
        "learned_stories.json": "creative_learning",
        "creative_attempts.json": "creative_learning",
        "learning_stats.json": "creative_learning",
        "learned_ascii.json": "creative_learning",
        "decision_maker_state.json": "decision_maker",
        "agent_state.json": "autonomous_agent",
    }

    def __init__(self, db=None):
        self.db = db
        self._cache: Dict[str, Any] = {}
        self._dirty: Set[str] = set()

        if self.db:
            self._init_tables()

    def connect_database(self, db) -> None:
        """Verbinde mit Datenbank"""
        self.db = db
        self._init_tables()
        logger.info("✅ UnifiedStorage mit Datenbank verbunden")

    def _init_tables(self) -> None:
        """Erstelle zentrale State-Tabelle"""
        if not self.db:
            return

        try:
            # Haupttabelle für alle Module-States
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS unified_state (
                    module_name TEXT NOT NULL,
                    state_key TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    state_type TEXT DEFAULT 'json',
                    version INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (module_name, state_key)
                )
            ''')

            # Backup-Tabelle für Versionierung
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS unified_state_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_name TEXT NOT NULL,
                    state_key TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    version INTEGER,
                    saved_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Migration-Tracking
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS migration_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    migrated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 1,
                    error_msg TEXT
                )
            ''')

            # Index für schnelle Lookups
            self.db.execute('''
                CREATE INDEX IF NOT EXISTS idx_unified_state_module
                ON unified_state(module_name)
            ''')

            logger.info("✅ UnifiedStorage DB-Tabellen initialisiert")

        except Exception as e:
            logger.error(f"UnifiedStorage Init-Fehler: {e}")

    def save(self, module: str, key: str, data: Any,
             backup: bool = True) -> bool:
        """
        Speichere State für ein Modul.

        Args:
            module: Modul-Name (z.B. 'policy_engine', 'consciousness')
            key: State-Key (z.B. 'main_state', 'q_table')
            data: Zu speichernde Daten (wird zu JSON serialisiert)
            backup: Ob ein Backup in der History erstellt werden soll

        Returns:
            True wenn erfolgreich
        """
        if not self.db:
            logger.warning("UnifiedStorage: Keine DB-Verbindung")
            return False

        try:
            # Serialisieren
            data_json = json.dumps(data, default=str, ensure_ascii=False)

            # Aktuelle Version holen
            row = self.db.fetchone('''
                SELECT version FROM unified_state
                WHERE module_name = ? AND state_key = ?
            ''', (module, key))

            version = (row['version'] + 1) if row else 1

            # Backup erstellen wenn gewünscht und nicht erste Version
            if backup and row:
                self.db.execute('''
                    INSERT INTO unified_state_history
                    (module_name, state_key, state_json, version)
                    SELECT module_name, state_key, state_json, version
                    FROM unified_state
                    WHERE module_name = ? AND state_key = ?
                ''', (module, key))

            # Speichern/Updaten
            self.db.execute('''
                INSERT OR REPLACE INTO unified_state
                (module_name, state_key, state_json, version, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (module, key, data_json, version))

            # Cache updaten
            cache_key = f"{module}:{key}"
            self._cache[cache_key] = data
            self._dirty.discard(cache_key)

            return True

        except Exception as e:
            logger.error(f"UnifiedStorage save error [{module}/{key}]: {e}")
            return False

    def load(self, module: str, key: str, default: Any = None) -> Any:
        """
        Lade State für ein Modul.

        Args:
            module: Modul-Name
            key: State-Key
            default: Default-Wert wenn nicht gefunden

        Returns:
            Geladene Daten oder default
        """
        # Cache prüfen
        cache_key = f"{module}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.db:
            return default

        try:
            row = self.db.fetchone('''
                SELECT state_json FROM unified_state
                WHERE module_name = ? AND state_key = ?
            ''', (module, key))

            if row:
                data = json.loads(row['state_json'])
                self._cache[cache_key] = data
                return data

            return default

        except Exception as e:
            logger.error(f"UnifiedStorage load error [{module}/{key}]: {e}")
            return default

    def delete(self, module: str, key: str) -> bool:
        """Lösche State"""
        if not self.db:
            return False

        try:
            self.db.execute('''
                DELETE FROM unified_state
                WHERE module_name = ? AND state_key = ?
            ''', (module, key))

            cache_key = f"{module}:{key}"
            self._cache.pop(cache_key, None)
            return True

        except Exception as e:
            logger.error(f"UnifiedStorage delete error: {e}")
            return False

    def get_all_for_module(self, module: str) -> Dict[str, Any]:
        """Hole alle States für ein Modul"""
        if not self.db:
            return {}

        try:
            rows = self.db.fetchall('''
                SELECT state_key, state_json FROM unified_state
                WHERE module_name = ?
            ''', (module,))

            result = {}
            for row in rows:
                result[row['state_key']] = json.loads(row['state_json'])
            return result

        except Exception as e:
            logger.error(f"UnifiedStorage get_all error: {e}")
            return {}

    def migrate_json_file(self, file_path: str, module: str = None,
                          key: str = None, delete_after: bool = False) -> bool:
        """
        Migriere eine JSON-Datei in die Datenbank.

        Args:
            file_path: Pfad zur JSON-Datei
            module: Modul-Name (wird aus KNOWN_STATE_FILES ermittelt wenn None)
            key: State-Key (wird aus Dateiname ermittelt wenn None)
            delete_after: JSON-Datei nach Migration löschen

        Returns:
            True wenn erfolgreich
        """
        path = Path(file_path)
        if not path.exists():
            logger.debug(f"Migration: {file_path} existiert nicht")
            return False

        # Modul und Key ermitteln
        filename = path.name
        if module is None:
            module = self.KNOWN_STATE_FILES.get(filename, path.stem)
        if key is None:
            key = path.stem.replace("_", "-")

        try:
            # JSON laden
            with open(path, 'r') as f:
                data = json.load(f)

            # In DB speichern
            success = self.save(module, key, data, backup=False)

            if success:
                # Migration loggen
                if self.db:
                    self.db.execute('''
                        INSERT INTO migration_log (source_file, module_name, success)
                        VALUES (?, ?, 1)
                    ''', (str(path), module))

                logger.info(f"✅ Migriert: {filename} → {module}/{key}")

                # Optional löschen
                if delete_after:
                    path.unlink()
                    logger.info(f"🗑️ Gelöscht: {filename}")

            return success

        except Exception as e:
            logger.error(f"Migration error for {file_path}: {e}")
            if self.db:
                self.db.execute('''
                    INSERT INTO migration_log (source_file, module_name, success, error_msg)
                    VALUES (?, ?, 0, ?)
                ''', (str(path), module or "unknown", str(e)))
            return False

    def migrate_all_known_files(self, base_paths: List[str] = None,
                                 delete_after: bool = False) -> Dict[str, bool]:
        """
        Migriere alle bekannten JSON-Dateien.

        Args:
            base_paths: Verzeichnisse zum Durchsuchen
            delete_after: Dateien nach Migration löschen

        Returns:
            Dict mit Dateiname → Erfolg
        """
        if base_paths is None:
            base_paths = [
                str(Path.home()),
                str(Path.cwd()),
                str(Path.cwd() / "data"),
            ]

        results = {}

        for base in base_paths:
            base_path = Path(base)
            if not base_path.exists():
                continue

            for filename in self.KNOWN_STATE_FILES.keys():
                file_path = base_path / filename
                if file_path.exists():
                    results[str(file_path)] = self.migrate_json_file(
                        str(file_path),
                        delete_after=delete_after
                    )

            # Auch in Unterverzeichnissen suchen
            for file_path in base_path.rglob("*.json"):
                if file_path.name in self.KNOWN_STATE_FILES:
                    if str(file_path) not in results:
                        results[str(file_path)] = self.migrate_json_file(
                            str(file_path),
                            delete_after=delete_after
                        )

        return results

    def get_version_history(self, module: str, key: str,
                            limit: int = 10) -> List[Dict]:
        """Hole Versions-Historie für einen State"""
        if not self.db:
            return []

        try:
            rows = self.db.fetchall('''
                SELECT version, state_json, saved_at
                FROM unified_state_history
                WHERE module_name = ? AND state_key = ?
                ORDER BY saved_at DESC
                LIMIT ?
            ''', (module, key, limit))

            return [
                {
                    "version": row['version'],
                    "data": json.loads(row['state_json']),
                    "saved_at": row['saved_at'],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Version history error: {e}")
            return []

    def restore_version(self, module: str, key: str, version: int) -> bool:
        """Stelle eine frühere Version wieder her"""
        if not self.db:
            return False

        try:
            row = self.db.fetchone('''
                SELECT state_json FROM unified_state_history
                WHERE module_name = ? AND state_key = ? AND version = ?
            ''', (module, key, version))

            if row:
                data = json.loads(row['state_json'])
                return self.save(module, key, data)

            return False

        except Exception as e:
            logger.error(f"Restore version error: {e}")
            return False

    def get_stats(self) -> Dict:
        """Hole Statistiken"""
        if not self.db:
            return {"connected": False}

        try:
            # Anzahl States pro Modul
            rows = self.db.fetchall('''
                SELECT module_name, COUNT(*) as count,
                       SUM(LENGTH(state_json)) as total_size
                FROM unified_state
                GROUP BY module_name
            ''')

            modules = {
                row['module_name']: {
                    "count": row['count'],
                    "size_bytes": row['total_size']
                }
                for row in rows
            }

            # Gesamtzahlen
            total_row = self.db.fetchone('''
                SELECT COUNT(*) as total, SUM(LENGTH(state_json)) as size
                FROM unified_state
            ''')

            # Migrationen
            migration_row = self.db.fetchone('''
                SELECT COUNT(*) as total,
                       SUM(success) as successful
                FROM migration_log
            ''')

            return {
                "connected": True,
                "modules": modules,
                "total_states": total_row['total'] if total_row else 0,
                "total_size_bytes": total_row['size'] if total_row else 0,
                "migrations_total": migration_row['total'] if migration_row else 0,
                "migrations_successful": migration_row['successful'] if migration_row else 0,
                "cache_size": len(self._cache),
            }

        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"connected": True, "error": str(e)}


class ModuleStorageAdapter:
    """
    Adapter für Module die noch JSON-basierte save/load nutzen.

    Ermöglicht schrittweise Migration ohne große Code-Änderungen.

    Beispiel:
        # Vorher im Modul:
        with open("state.json", "w") as f:
            json.dump(state, f)

        # Nachher:
        storage = ModuleStorageAdapter(unified_storage, "my_module")
        storage.save("state", state)
    """

    def __init__(self, unified_storage: UnifiedStorage, module_name: str):
        self.storage = unified_storage
        self.module = module_name

    def save(self, key: str, data: Any) -> bool:
        """Speichere State"""
        return self.storage.save(self.module, key, data)

    def load(self, key: str, default: Any = None) -> Any:
        """Lade State"""
        return self.storage.load(self.module, key, default)

    def save_file(self, filename: str, data: Any) -> bool:
        """
        Kompatibilitäts-Methode für Datei-basierte Speicherung.
        Konvertiert Dateiname zu State-Key.
        """
        key = Path(filename).stem.replace("_", "-")
        return self.save(key, data)

    def load_file(self, filename: str, default: Any = None) -> Any:
        """
        Kompatibilitäts-Methode für Datei-basiertes Laden.
        Versucht erst DB, dann Datei als Fallback.
        """
        key = Path(filename).stem.replace("_", "-")
        data = self.load(key)

        if data is not None:
            return data

        # Fallback: JSON-Datei
        path = Path(filename)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                # Automatisch migrieren
                self.save(key, data)
                logger.info(f"Auto-migriert: {filename} → {self.module}/{key}")
                return data
            except Exception as e:
                logger.error(f"Fallback load error: {e}")

        return default

    def get_all(self) -> Dict[str, Any]:
        """Hole alle States für dieses Modul"""
        return self.storage.get_all_for_module(self.module)


# =============================================================================
# GLOBAL UNIFIED STORAGE INSTANCE
# =============================================================================

_unified_storage: Optional[UnifiedStorage] = None


def get_unified_storage() -> UnifiedStorage:
    """Hole globale UnifiedStorage Instanz"""
    global _unified_storage
    if _unified_storage is None:
        _unified_storage = UnifiedStorage()
    return _unified_storage


def get_module_storage(module_name: str) -> ModuleStorageAdapter:
    """Hole Storage-Adapter für ein Modul"""
    return ModuleStorageAdapter(get_unified_storage(), module_name)


# =============================================================================
# SYSTEM INTEGRATOR - Hauptklasse
# =============================================================================

class SystemIntegrator:
    """
    Der Hauptintegrator der alle Systeme verbindet.

    Features:
    - Initialisiert alle Integration-Komponenten
    - Verbindet Systeme bidirektional
    - Orchestriert Feedback-Loops
    - Verwaltet Persistenz
    - Führt A/B Tests durch
    """

    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Initialisiere Komponenten
        self.change_log = UnifiedChangeLog(
            persist_path=str(self.data_path / "change_log.json")
        )

        self.threshold_manager = AdaptiveThresholdManager(
            change_log=self.change_log
        )

        self.ab_tester = PersonalityABTester(
            change_log=self.change_log
        )

        self.feedback_orchestrator = FeedbackOrchestrator(
            change_log=self.change_log
        )

        self.history_persistence = HistoryPersistence(
            base_path=str(self.data_path / "histories")
        )

        # UnifiedStorage für zentrale Speicherung
        self.unified_storage = UnifiedStorage()

        # === NEU v2.0: Intelligente Integration ===
        self.intelligent_integrator = IntelligentIntegrator(
            change_log=self.change_log
        )

        # Verbundene Systeme
        self.systems: Dict[str, Any] = {}

        # Datenbank-Referenz
        self.db = None

        # Lade gespeicherten Zustand
        self._load_state()

        # Starte Background-Tasks
        self._start_background_tasks()

    def connect_database(self, db) -> None:
        """
        Verbinde mit HoloDatabaseManager für Persistenz in der Datenbank.

        Args:
            db: HoloDatabaseManager Instanz
        """
        self.db = db
        self.history_persistence.connect_database(db)
        self.unified_storage.connect_database(db)

        # Automatische Migration von JSON-Dateien
        migration_results = self.unified_storage.migrate_all_known_files()
        if migration_results:
            migrated = sum(1 for v in migration_results.values() if v)
            logger.info(f"📦 {migrated} JSON-Dateien migriert")

        logger.info("✅ SystemIntegrator mit Datenbank verbunden")

    def get_storage(self, module_name: str) -> ModuleStorageAdapter:
        """
        Hole Storage-Adapter für ein Modul.

        Args:
            module_name: Name des Moduls

        Returns:
            ModuleStorageAdapter für das Modul
        """
        return ModuleStorageAdapter(self.unified_storage, module_name)

    def connect(self, system_name: str, system: Any) -> None:
        """
        Verbinde ein System mit dem Integrator.

        Registriert automatisch relevante Histories für Persistenz.
        """
        self.systems[system_name] = system
        self.feedback_orchestrator.connect_system(system_name, system)

        # === NEU v2.0: Intelligente Systeme verbinden ===
        # === ERWEITERT v2.3: Vollständiges Mapping für ALLE Systeme ===
        intelligent_system_mapping = {
            # v2.0 Core Systems
            "self_awareness": "self_awareness",
            "dialogue_engine": "dialogue_engine",
            "drive_system": "drive_system",
            "learning_system": "learning_system",
            "topic_tracker": "learning_system",  # Alias
            "consciousness": "consciousness",
            "policy_engine": "policy_engine",
            # v2.1 Extended Systems
            "energy_system": "energy_system",
            "creative_mind": "creative_mind",
            "autonomous_thinking": "autonomous_thinking",
            "impulse_system": "impulse_system",
            "opinion_system": "opinion_system",
            "person_opinions": "opinion_system",  # Alias
            # v2.2 Deep Integration
            "depth_system": "depth_system",
            "emotional_complexity": "emotional_complexity",
            "memory_system": "memory_system",
            "memory": "memory_system",  # Alias
            # v2.3 Complete Integration (NEU!)
            "context_mind": "context_mind",
            "self_expression": "self_expression",
            "inner_life": "inner_life",
            "preferences": "preferences",
            "preference_manager": "preferences",  # Alias
            "web_curiosity": "web_curiosity",
            "skill_system": "skill_system",
            "meta_cognition": "meta_cognition",
            "digital_body": "digital_body",
        }
        if system_name in intelligent_system_mapping:
            target_name = intelligent_system_mapping[system_name]
            self.intelligent_integrator.connect(target_name, system)

        # Auto-registriere bekannte Histories
        history_attrs = [
            "mood_history", "activity_history", "reflection_history",
            "thought_history", "contemplation_history", "experience_buffer",
            "initiative_history", "decision_history", "emotion_history",
        ]

        for attr in history_attrs:
            if hasattr(system, attr):
                self.history_persistence.register(
                    f"{system_name}_{attr}",
                    system,
                    attr
                )

        logger.info(f"✅ System '{system_name}' verbunden mit Integrator")

        # Bidirektionale Verbindung herstellen
        self._setup_bidirectional_connection(system_name, system)

    def _setup_bidirectional_connection(self, name: str, system: Any) -> None:
        """Stelle bidirektionale Verbindungen her"""
        # Drive System ↔ Personality
        if name == "drive_system" and "personality" in self.systems:
            self._connect_drive_personality(system, self.systems["personality"])
        elif name == "personality" and "drive_system" in self.systems:
            self._connect_drive_personality(self.systems["drive_system"], system)

        # Consciousness ↔ Decision Making
        if name == "consciousness" and "policy_engine" in self.systems:
            self._connect_consciousness_policy(system, self.systems["policy_engine"])
        elif name == "policy_engine" and "consciousness" in self.systems:
            self._connect_consciousness_policy(self.systems["consciousness"], system)

        # Depth System ↔ Response Generation
        if name == "depth_system" and "intelligent_router" in self.systems:
            self._connect_depth_router(system, self.systems["intelligent_router"])
        elif name == "intelligent_router" and "depth_system" in self.systems:
            self._connect_depth_router(self.systems["depth_system"], system)

    def _connect_drive_personality(self, drive_system: Any, personality: Any) -> None:
        """Verbinde Drive System mit Personality bidirektional"""
        # Callback: Wenn Drive sich ändert → Personality updaten
        def on_drive_change(event: ChangeEvent):
            if event.source_system == "drive_system":
                # Personality reagiert auf Drive-Änderungen
                try:
                    if hasattr(personality, 'on_drive_update'):
                        personality.on_drive_update(event.key, event.new_value)
                except Exception as e:
                    logger.error(f"Drive→Personality Sync Error: {e}")

        self.change_log.subscribe(ChangeType.DRIVE, on_drive_change)

        # Umgekehrt: Personality-Änderungen → Drive System
        def on_personality_change(event: ChangeEvent):
            if event.source_system == "personality":
                try:
                    if hasattr(drive_system, 'on_personality_update'):
                        drive_system.on_personality_update(event.key, event.new_value)
                except Exception as e:
                    logger.error(f"Personality→Drive Sync Error: {e}")

        self.change_log.subscribe(ChangeType.PERSONALITY_TRAIT, on_personality_change)

    def _connect_consciousness_policy(self, consciousness: Any, policy_engine: Any) -> None:
        """Verbinde Consciousness mit Policy Engine"""
        # Consciousness-State beeinflusst Decisions
        def on_consciousness_change(event: ChangeEvent):
            if hasattr(policy_engine, 'update_consciousness_context'):
                try:
                    policy_engine.update_consciousness_context({
                        "key": event.key,
                        "value": event.new_value
                    })
                except Exception as e:
                    logger.error(f"Consciousness→Policy Error: {e}")

        # Subscriben auf relevante Changes
        for change_type in [ChangeType.MOOD, ChangeType.BELIEF, ChangeType.OPINION]:
            self.change_log.subscribe(change_type, on_consciousness_change)

    def _connect_depth_router(self, depth_system: Any, router: Any) -> None:
        """Verbinde Depth System mit Router"""
        # Depth-Level beeinflusst Response-Style
        def on_depth_change(event: ChangeEvent):
            if event.key == "depth_level" and hasattr(router, 'set_depth_context'):
                try:
                    router.set_depth_context(event.new_value)
                except Exception as e:
                    logger.error(f"Depth→Router Error: {e}")

        self.change_log.subscribe(ChangeType.RELATIONSHIP, on_depth_change)

    def process_user_feedback(self,
                               positive: bool,
                               magnitude: float = 1.0,
                               context: Dict = None) -> Dict:
        """
        Verarbeite User-Feedback durch alle Systeme.

        Diese Methode sollte aufgerufen werden wenn User-Reaktionen erkannt werden.
        """
        context = context or {}

        # 1. Feedback Orchestrator
        results = self.feedback_orchestrator.process_feedback(
            feedback_type="user_reaction",
            positive=positive,
            magnitude=magnitude,
            context=context
        )

        # 2. A/B Tester
        self.ab_tester.record_feedback(positive, magnitude if positive else -magnitude)

        # 3. Threshold Updates basierend auf Context
        for key in ["response_style", "verbosity", "emotionality"]:
            if key in context:
                self.threshold_manager.update(
                    name=key,
                    outcome_positive=positive,
                    magnitude=magnitude,
                    reason=f"user_feedback on {key}"
                )

        # 4. Auto-Save wenn nötig
        if self.history_persistence.should_auto_save():
            self._save_state()

        return results

    def process_conversation_end(self, summary: Dict) -> Dict:
        """Verarbeite Gesprächsende"""
        satisfaction = summary.get("user_satisfaction", 0.5)

        results = self.feedback_orchestrator.process_conversation_end(
            conversation_summary=summary,
            user_satisfaction=satisfaction
        )

        # Speichere Zustand
        self._save_state()

        return results

    def get_threshold(self, name: str) -> float:
        """Hole adaptiven Threshold"""
        return self.threshold_manager.get(name)

    def get_trait_modifier(self, trait: str) -> float:
        """Hole Trait-Modifier aus A/B Tests"""
        return self.ab_tester.get_trait_modifier(trait)

    def start_experiment(self,
                          name: str,
                          trait: str,
                          variant_a: float,
                          variant_b: float) -> PersonalityExperiment:
        """Starte A/B Experiment"""
        return self.ab_tester.create_experiment(
            name=name,
            trait_key=trait,
            variant_a_modifier=variant_a,
            variant_b_modifier=variant_b
        )

    def get_integration_status(self) -> Dict:
        """Hole Status aller Integrationen"""
        return {
            "connected_systems": list(self.systems.keys()),
            "change_log_size": len(self.change_log.events),
            "change_log_stats": dict(self.change_log.stats),
            "threshold_stats": self.threshold_manager.get_stats(),
            "active_experiments": self.ab_tester.get_active_experiments(),
            "experiment_recommendations": self.ab_tester.get_recommendations(),
            "feedback_stats": self.feedback_orchestrator.get_recent_feedback_stats(),
            "registered_histories": list(self.history_persistence.histories.keys()),
        }

    def _save_state(self) -> None:
        """Speichere gesamten Zustand"""
        try:
            # Change Log
            self.change_log.save()

            # Thresholds
            self.threshold_manager.save(str(self.data_path / "thresholds.json"))

            # Histories
            self.history_persistence.save_all()

            logger.info("💾 Integration-Zustand gespeichert")

        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")

    def _load_state(self) -> None:
        """Lade gespeicherten Zustand"""
        try:
            # Change Log
            self.change_log.load()

            # Thresholds
            threshold_path = str(self.data_path / "thresholds.json")
            if Path(threshold_path).exists():
                self.threshold_manager.load(threshold_path)

            logger.info("📂 Integration-Zustand geladen")

        except Exception as e:
            logger.error(f"Fehler beim Laden: {e}")

    def _start_background_tasks(self) -> None:
        """Starte Background-Tasks"""
        def auto_save_task():
            while True:
                time.sleep(300)  # 5 Minuten
                if self.history_persistence.should_auto_save():
                    self._save_state()

        # Thread starten
        save_thread = threading.Thread(target=auto_save_task, daemon=True)
        save_thread.start()

        # === NEU v2.0: Intelligente Integration Tick ===
        def intelligent_integration_task():
            while True:
                time.sleep(600)  # 10 Minuten
                try:
                    result = self.intelligent_integrator.integration_tick()
                    if result.get("actions"):
                        logger.info(f"🧠 Integration: {len(result['actions'])} Aktionen ausgeführt")
                except Exception as e:
                    logger.error(f"Integration tick error: {e}")

        integration_thread = threading.Thread(target=intelligent_integration_task, daemon=True)
        integration_thread.start()

    def run_integration_tick(self) -> Dict[str, Any]:
        """Manueller Integration-Tick (für Tests oder direkten Aufruf)."""
        return self.intelligent_integrator.integration_tick()

    def get_intelligent_integration_stats(self) -> Dict[str, Any]:
        """Holt Stats von der intelligenten Integration."""
        return self.intelligent_integrator.get_integration_stats()


# =============================================================================
# STUB-VERVOLLSTÄNDIGUNG - Für holo_context_mind.py
# =============================================================================

class EnhancedEmotionalContextTracker:
    """
    Vervollständigte Version des EmotionalContextTracker.

    Ersetzt die leeren Stub-Methoden mit echten Implementierungen.
    """

    def __init__(self, change_log: UnifiedChangeLog = None):
        self.user_emotions: List[Dict] = []
        self.holo_emotions: List[Dict] = []
        self.triggers: List[Dict] = []
        self.current_mood = "neutral"
        self.mood_intensity = 0.5
        self.mood_history: List[Tuple[str, float, float]] = []
        self.change_log = change_log

        # Decay-Konfiguration
        self.decay_rate = 0.1  # Pro Stunde
        self.last_decay = time.time()

    def add_user_emotion(self, emotion: str, intensity: float = 0.5,
                         trigger: str = "", context: Dict = None) -> None:
        """Füge User-Emotion hinzu (vorher: pass)"""
        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "trigger": trigger,
            "timestamp": time.time(),
            "context": context or {},
        }
        self.user_emotions.append(entry)

        # Begrenze Historie
        if len(self.user_emotions) > 100:
            self.user_emotions = self.user_emotions[-100:]

        # Log
        if self.change_log:
            self.change_log.log_change(
                change_type=ChangeType.MOOD,
                source="user",
                key="emotion",
                old_value=None,
                new_value=emotion,
                reason=trigger,
            )

    def add_holo_emotion(self, emotion: str, intensity: float = 0.5,
                         reason: str = "") -> None:
        """Füge Holo-Emotion hinzu (vorher: pass)"""
        old_mood = self.current_mood

        entry = {
            "emotion": emotion,
            "intensity": intensity,
            "reason": reason,
            "timestamp": time.time(),
        }
        self.holo_emotions.append(entry)

        # Update current mood wenn Intensität hoch genug
        if intensity > 0.5:
            self.current_mood = emotion
            self.mood_intensity = intensity
            self.mood_history.append((emotion, intensity, time.time()))

        # Begrenze Historie
        if len(self.holo_emotions) > 100:
            self.holo_emotions = self.holo_emotions[-100:]
        if len(self.mood_history) > 50:
            self.mood_history = self.mood_history[-50:]

        # Log
        if self.change_log and old_mood != emotion:
            self.change_log.log_change(
                change_type=ChangeType.MOOD,
                source="holo",
                key="emotion",
                old_value=old_mood,
                new_value=emotion,
                reason=reason,
            )

    def update_mood(self, mood: str, intensity: float = 0.5,
                    reason: str = "") -> None:
        """Update aktuelles Mood (vorher: pass)"""
        old_mood = self.current_mood
        old_intensity = self.mood_intensity

        self.current_mood = mood
        self.mood_intensity = intensity
        self.mood_history.append((mood, intensity, time.time()))

        if self.change_log and (old_mood != mood or abs(old_intensity - intensity) > 0.1):
            self.change_log.log_change(
                change_type=ChangeType.MOOD,
                source="mood_system",
                key="mood",
                old_value=f"{old_mood}:{old_intensity:.2f}",
                new_value=f"{mood}:{intensity:.2f}",
                reason=reason,
            )

    def add_trigger(self, trigger_type: str, source: str,
                    effect: str, magnitude: float = 0.5) -> None:
        """Füge Trigger hinzu (vorher: pass)"""
        self.triggers.append({
            "type": trigger_type,
            "source": source,
            "effect": effect,
            "magnitude": magnitude,
            "timestamp": time.time(),
        })

        if len(self.triggers) > 50:
            self.triggers = self.triggers[-50:]

    def decay(self) -> None:
        """Mood-Decay über Zeit (vorher: pass)"""
        now = time.time()
        hours_passed = (now - self.last_decay) / 3600

        if hours_passed < 0.1:
            return

        # Intensität decay
        decay_amount = self.decay_rate * hours_passed
        self.mood_intensity = max(0.1, self.mood_intensity - decay_amount)

        # Bei sehr niedriger Intensität → neutral
        if self.mood_intensity < 0.2:
            if self.current_mood != "neutral":
                old_mood = self.current_mood
                self.current_mood = "neutral"

                if self.change_log:
                    self.change_log.log_change(
                        change_type=ChangeType.MOOD,
                        source="decay",
                        key="mood",
                        old_value=old_mood,
                        new_value="neutral",
                        reason="natural decay",
                    )

        self.last_decay = now

    def get_mood(self) -> Tuple[str, float]:
        """Hole aktuelles Mood"""
        return self.current_mood, self.mood_intensity

    def get_user_mood_trend(self, hours: float = 24) -> str:
        """Hole User-Mood-Trend"""
        cutoff = time.time() - (hours * 3600)
        recent = [e for e in self.user_emotions if e["timestamp"] >= cutoff]

        if not recent:
            return "unknown"

        # Analysiere Trend
        positive_emotions = {"happy", "excited", "grateful", "content", "joyful"}
        negative_emotions = {"sad", "angry", "frustrated", "anxious", "stressed"}

        positive_count = sum(1 for e in recent if e["emotion"].lower() in positive_emotions)
        negative_count = sum(1 for e in recent if e["emotion"].lower() in negative_emotions)

        if positive_count > negative_count * 2:
            return "positive"
        elif negative_count > positive_count * 2:
            return "negative"
        elif positive_count > negative_count:
            return "slightly_positive"
        elif negative_count > positive_count:
            return "slightly_negative"
        else:
            return "neutral"

    def get_dominant_emotion(self, recent_only: bool = True) -> Optional[str]:
        """Hole dominante Emotion"""
        emotions = self.holo_emotions if not recent_only else self.holo_emotions[-10:]

        if not emotions:
            return None

        # Weighted by intensity and recency
        emotion_scores = defaultdict(float)
        now = time.time()

        for e in emotions:
            age_hours = (now - e["timestamp"]) / 3600
            recency_weight = 1.0 / (1 + age_hours)
            emotion_scores[e["emotion"]] += e["intensity"] * recency_weight

        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        return None


# =============================================================================
# INTELLIGENT INTEGRATOR v2.0
# =============================================================================

class IntelligentIntegrator:
    """
    Verbindet die intelligenten Subsysteme für echte Synergie.

    NEU v2.0: Macht aus isolierten Systemen ein integriertes Ganzes:

    1. REFLECTION → ACTION
       - MetaCognition Insights → Verhaltensänderungen
       - Wenn Reflexion zeigt "ich bin zu ausführlich" → kürzere Antworten

    2. GOAP PLANNER → DRIVE SYSTEM
       - Intrinsische Ziele → Aktivitäts-Priorisierung
       - Wenn Ziel "mehr über X lernen" → bevorzuge Lern-Aktivitäten zu X

    3. SELF AWARENESS → DIALOG ENGINE
       - Energie/Stimmung → Antwort-Stil
       - Wenn Energie niedrig → kürzere, ruhigere Antworten

    4. LEARNING → PERSONALITY
       - Topic-Feedback → Interessen-Gewichtung
       - Positive Reaktionen auf Anime → verstärke Anime-Interesse
    """

    def __init__(self, change_log: UnifiedChangeLog = None):
        self.change_log = change_log

        # Referenzen zu intelligenten Systemen
        self.self_awareness = None  # HoloSelfAwareness
        self.dialogue_engine = None  # HoloDialogueEngine
        self.drive_system = None  # HoloDriveSystem
        self.learning_system = None  # LearningTopicTracker
        self.consciousness = None  # ConsciousnessEngine
        self.policy_engine = None  # HoloPolicyEngine

        # === NEU v2.1: Erweiterte System-Verbindungen ===
        self.energy_system = None  # HoloEnergySystem
        self.creative_mind = None  # HoloCreativeMind
        self.autonomous_thinking = None  # IntuitiveSystem, SelfChallenger, etc.
        self.impulse_system = None  # HoloVoice/ImpulseGenerator
        self.opinion_system = None  # PersonOpinions/BeliefNetwork

        # === NEU v2.2: Tiefe Integration ===
        self.depth_system = None  # HoloDepthSystem - Trust/Vulnerability Layers
        self.emotional_complexity = None  # EmotionalComplexitySystem
        self.memory_system = None  # Memory/Context für Personalisierung

        # === NEU v2.3: Vollständige Integration - Die letzten 8 Systeme ===
        self.context_mind = None  # HoloContextMind - Universelles Kontext-System
        self.self_expression = None  # HoloSelfExpression - Events, Feiertage, proaktiv
        self.inner_life = None  # HoloInnerLife - Tagesablauf, Curiosity, Beziehungen
        self.preferences = None  # HoloPreferences - Vorlieben/Abneigungen, Macken
        self.web_curiosity = None  # HoloWebCuriosity - Eigene Suche, Fakten-Wissen
        self.skill_system = None  # HoloSkillSystem - Verfügbare Fähigkeiten
        self.meta_cognition = None  # HoloMetaCognition - Selbst-Beobachtung
        self.digital_body = None  # HoloDigitalBody - Hardware → Mentaler Zustand

        # Tracking für Integrations-Entscheidungen
        self.integration_history: deque = deque(maxlen=500)
        self.last_reflection_action: Optional[Dict] = None

        # Cache für Cross-System Daten
        self._energy_dialog_cache: Dict[str, Any] = {}
        self._creative_state_cache: Dict[str, Any] = {}
        self._last_impulse_sync: float = 0
        self._depth_dialog_cache: Dict[str, Any] = {}
        self._last_emotional_expression: str = ""
        # v2.3 Caches
        self._context_cache: Dict[str, Any] = {}
        self._event_cache: Dict[str, Any] = {}
        self._inner_life_cache: Dict[str, Any] = {}
        self._body_state_cache: Dict[str, Any] = {}

        logger.info("🧠 IntelligentIntegrator v2.3 initialisiert")

        # Auto-initialisiere EmotionalComplexitySystem
        self._init_emotional_complexity()

    def _init_emotional_complexity(self) -> None:
        """Initialisiert das EmotionalComplexitySystem automatisch."""
        if self.emotional_complexity is not None:
            return
        try:
            from holo_emotional_complexity import get_emotional_complexity
            self.emotional_complexity = get_emotional_complexity()
            logger.info("✅ EmotionalComplexitySystem automatisch verbunden")
        except ImportError as e:
            logger.warning(f"⚠️ EmotionalComplexitySystem nicht verfügbar: {e}")
        except Exception as e:
            logger.error(f"❌ Fehler beim Initialisieren von EmotionalComplexitySystem: {e}")

    def connect(self, system_name: str, system: Any) -> None:
        """Verbinde ein intelligentes System."""
        if hasattr(self, system_name):
            setattr(self, system_name, system)
            logger.info(f"🧠 IntelligentIntegrator: {system_name} verbunden")

    # =========================================================================
    # 1. REFLECTION → ACTION
    # =========================================================================

    def apply_reflection_insight(self, reflection: Dict) -> Dict[str, Any]:
        """
        Wendet eine Reflexions-Erkenntnis auf Verhalten an.

        Args:
            reflection: Dict mit 'insight', 'type', 'growth_opportunity'

        Returns:
            Dict mit durchgeführten Änderungen
        """
        changes = {}
        insight = reflection.get("insight", "")
        growth = reflection.get("growth_opportunity", "")

        if not insight and not growth:
            return {"applied": False, "reason": "no_insight"}

        # Analysiere Insight für konkrete Änderungen
        insight_lower = insight.lower() if insight else ""
        growth_lower = growth.lower() if growth else ""

        # === Antwort-Länge Anpassung ===
        if any(w in insight_lower for w in ["zu lang", "ausführlich", "kürzer"]):
            if self.dialogue_engine and hasattr(self.dialogue_engine, 'adaptive_config'):
                # Pushe "short" Präferenz
                self.dialogue_engine.adaptive_config.record_feedback(
                    was_positive=False,
                    length="long"
                )
                self.dialogue_engine.adaptive_config.record_feedback(
                    was_positive=True,
                    length="short"
                )
                changes["response_length"] = "shortened"

        elif any(w in insight_lower for w in ["mehr detail", "ausführlicher", "genauer"]):
            if self.dialogue_engine and hasattr(self.dialogue_engine, 'adaptive_config'):
                self.dialogue_engine.adaptive_config.record_feedback(
                    was_positive=True,
                    length="long"
                )
                changes["response_length"] = "lengthened"

        # === Fragen-Häufigkeit ===
        if any(w in insight_lower for w in ["mehr fragen", "neugieriger", "interest"]):
            if self.dialogue_engine and hasattr(self.dialogue_engine, 'adaptive_config'):
                self.dialogue_engine.adaptive_config.record_feedback(
                    was_positive=True,
                    used_question=True
                )
                changes["question_frequency"] = "increased"

        elif any(w in insight_lower for w in ["weniger fragen", "zu viele fragen"]):
            if self.dialogue_engine and hasattr(self.dialogue_engine, 'adaptive_config'):
                self.dialogue_engine.adaptive_config.record_feedback(
                    was_positive=False,
                    used_question=True
                )
                changes["question_frequency"] = "decreased"

        # === Themen-Fokus ===
        if "mehr über" in growth_lower or "lernen" in growth_lower:
            # Extrahiere Thema
            topic = self._extract_topic(growth)
            if topic and self.learning_system:
                if hasattr(self.learning_system, 'observe_user_reaction'):
                    self.learning_system.observe_user_reaction(
                        reaction_score=0.5,  # Mild positive
                        topic=topic
                    )
                    changes["topic_interest"] = f"boosted:{topic}"

        # Speichere Aktion
        self.last_reflection_action = {
            "timestamp": time.time(),
            "insight": insight[:100],
            "changes": changes
        }
        self.integration_history.append(self.last_reflection_action)

        # Log
        if self.change_log and changes:
            self.change_log.log_change(
                change_type=ChangeType.LEARNING,
                source_system="self_awareness",
                target_system="multiple",
                key="reflection_applied",
                new_value=changes,
                reason=insight[:50]
            )

        return {"applied": bool(changes), "changes": changes}

    def _extract_topic(self, text: str) -> Optional[str]:
        """Extrahiert ein Thema aus Text."""
        keywords = ["anime", "gaming", "technik", "musik", "serien", "filme",
                   "japan", "wissenschaft", "kunst", "programmieren"]
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                return kw
        return None

    # =========================================================================
    # 2. GOAP PLANNER → DRIVE SYSTEM
    # =========================================================================

    def sync_goals_to_activities(self) -> Dict[str, Any]:
        """
        Synchronisiert GOAP-Ziele mit DriveSystem-Aktivitäten.

        Wenn ein intrinsisches Ziel "Mehr über Anime lernen" existiert,
        sollte das DriveSystem Anime-bezogene Aktivitäten bevorzugen.

        Returns:
            Dict mit synchronisierten Änderungen
        """
        if not self.self_awareness or not self.drive_system:
            return {"synced": False, "reason": "systems_not_connected"}

        changes = {}

        # Hole aktive Ziele
        active_goals = []
        if hasattr(self.self_awareness, 'goal_generator'):
            gen = self.self_awareness.goal_generator
            if hasattr(gen, 'active_goals'):
                active_goals = gen.active_goals

        if not active_goals:
            return {"synced": False, "reason": "no_active_goals"}

        # Für jedes Ziel: Boost relevante Aktivitäten
        for goal in active_goals:
            goal_desc = getattr(goal, 'description', str(goal)).lower()
            goal_type = getattr(goal, 'goal_type', None)

            # Mapping: Ziel-Typ → Aktivitäts-Kategorie
            if goal_type:
                goal_type_name = goal_type.value if hasattr(goal_type, 'value') else str(goal_type)

                if goal_type_name in ["learn", "understand", "explore"]:
                    # Boost Lern-Aktivitäten
                    if hasattr(self.drive_system, 'record_activity_feedback'):
                        self.drive_system.record_activity_feedback(
                            "learn_something", was_successful=True
                        )
                        changes["boosted_learn"] = True

                elif goal_type_name in ["create", "grow"]:
                    # Boost kreative Aktivitäten
                    if hasattr(self.drive_system, 'record_activity_feedback'):
                        self.drive_system.record_activity_feedback(
                            "creative_activity", was_successful=True
                        )
                        changes["boosted_creative"] = True

                elif goal_type_name in ["connect", "help"]:
                    # Boost soziale Aktivitäten
                    if hasattr(self.drive_system, 'record_activity_feedback'):
                        self.drive_system.record_activity_feedback(
                            "social_interaction", was_successful=True
                        )
                        changes["boosted_social"] = True

            # Themen-spezifisch
            topic = self._extract_topic(goal_desc)
            if topic:
                changes[f"topic_focus_{topic}"] = True

        return {"synced": True, "changes": changes, "goals_processed": len(active_goals)}

    # =========================================================================
    # 3. SELF AWARENESS → DIALOG ENGINE
    # =========================================================================

    def get_dialog_modifiers_from_state(self) -> Dict[str, Any]:
        """
        Generiert Dialog-Modifikationen basierend auf Selbst-Zustand.

        Returns:
            Dict mit empfohlenen Dialog-Anpassungen
        """
        modifiers = {
            "tone": "neutral",
            "energy_factor": 1.0,
            "verbosity": "medium",
            "emotional_openness": 0.5,
        }

        if not self.self_awareness:
            return modifiers

        # === Energie-Level ===
        energy = 0.5
        if hasattr(self.self_awareness, 'bayesian_self'):
            beliefs = self.self_awareness.bayesian_self
            if hasattr(beliefs, 'beliefs') and 'energy_level' in beliefs.beliefs:
                energy_belief = beliefs.beliefs['energy_level']
                energy = getattr(energy_belief, 'mean', 0.5)

        if energy < 0.3:
            modifiers["tone"] = "tired"
            modifiers["energy_factor"] = 0.7
            modifiers["verbosity"] = "short"
        elif energy > 0.7:
            modifiers["tone"] = "energetic"
            modifiers["energy_factor"] = 1.3
            modifiers["verbosity"] = "long"

        # === Stimmung ===
        mood = 0.5
        if hasattr(self.self_awareness, 'bayesian_self'):
            beliefs = self.self_awareness.bayesian_self
            if hasattr(beliefs, 'beliefs') and 'current_mood' in beliefs.beliefs:
                mood_belief = beliefs.beliefs['current_mood']
                mood = getattr(mood_belief, 'mean', 0.5)

        if mood < 0.3:
            modifiers["tone"] = "subdued"
            modifiers["emotional_openness"] = 0.3
        elif mood > 0.7:
            modifiers["tone"] = "cheerful"
            modifiers["emotional_openness"] = 0.8

        # === Meta-Kognition Check ===
        if hasattr(self.self_awareness, 'meta_cognition'):
            meta = self.self_awareness.meta_cognition
            if hasattr(meta, 'current_confidence'):
                confidence = meta.current_confidence
                if confidence < 0.4:
                    modifiers["tone"] = "uncertain"

        return modifiers

    def apply_state_to_dialog(self) -> bool:
        """
        Wendet Selbst-Zustand auf DialogEngine an.

        Returns:
            True wenn erfolgreich angewendet
        """
        if not self.dialogue_engine:
            return False

        modifiers = self.get_dialog_modifiers_from_state()

        # Wende auf adaptive_config an wenn vorhanden
        if hasattr(self.dialogue_engine, 'adaptive_config'):
            config = self.dialogue_engine.adaptive_config

            # Verbosity → Length
            verbosity = modifiers.get("verbosity", "medium")
            if verbosity == "short" and hasattr(config, 'record_feedback'):
                config.record_feedback(was_positive=True, length="short")
            elif verbosity == "long" and hasattr(config, 'record_feedback'):
                config.record_feedback(was_positive=True, length="long")

        # Log
        self.integration_history.append({
            "timestamp": time.time(),
            "type": "state_to_dialog",
            "modifiers": modifiers
        })

        return True

    # =========================================================================
    # 4. LEARNING → PERSONALITY INTERESTS
    # =========================================================================

    # =========================================================================
    # 5. ENERGY SYSTEM → DRIVE/DIALOG (NEU v2.1)
    # =========================================================================

    def sync_energy_to_drives(self) -> Dict[str, Any]:
        """
        Synchronisiert EnergySystem mit DriveSystem.

        Niedrige Energie → Reduziere anspruchsvolle Aktivitäten
        Hohe Energie → Aktiviere mehr explorative Aktivitäten
        Emotionale Energie → Beeinflusst soziale Triebe

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.energy_system or not self.drive_system:
            return {"synced": False, "reason": "systems_not_connected"}

        changes = {}

        # Hole Energie-Status
        energy_status = {}
        if hasattr(self.energy_system, 'get_status'):
            energy_status = self.energy_system.get_status()
        elif hasattr(self.energy_system, 'state'):
            state = self.energy_system.state
            energy_status = {
                "base_energy": getattr(state, 'base_energy', 0.5),
                "variable_energy": getattr(state, 'variable_energy', 0.5),
                "emotional_energy": getattr(state, 'emotional_energy', 0.5),
                "effective_energy": getattr(state, 'effective_energy', 0.5),
            }

        effective = energy_status.get("effective_energy", 0.5)
        emotional = energy_status.get("emotional_energy", 0.5)

        # === Aktivitäts-Priorisierung basierend auf Energie ===
        if hasattr(self.drive_system, 'record_activity_feedback'):
            if effective < 0.3:
                # Niedrige Energie: Ruhe-Aktivitäten bevorzugen
                self.drive_system.record_activity_feedback("rest", was_successful=True)
                self.drive_system.record_activity_feedback("deep_thinking", was_successful=False)
                changes["activity_bias"] = "rest_preferred"
            elif effective > 0.7:
                # Hohe Energie: Explorative Aktivitäten bevorzugen
                self.drive_system.record_activity_feedback("learn_something", was_successful=True)
                self.drive_system.record_activity_feedback("creative_activity", was_successful=True)
                changes["activity_bias"] = "active_preferred"

        # === Soziale Triebe basierend auf emotionaler Energie ===
        if hasattr(self.drive_system, 'drives'):
            drives = self.drive_system.drives
            if "social" in drives:
                social_drive = drives["social"]
                if hasattr(social_drive, 'level'):
                    # Emotionale Energie beeinflusst sozialen Trieb
                    if emotional < 0.3:
                        # Emotional erschöpft: Weniger soziale Bedürfnisse
                        changes["social_drive_modifier"] = -0.1
                    elif emotional > 0.7:
                        # Emotional gut: Mehr soziale Bedürfnisse
                        changes["social_drive_modifier"] = 0.1

        # Cache aktualisieren
        self._energy_dialog_cache = {
            "effective_energy": effective,
            "emotional_energy": emotional,
            "timestamp": time.time()
        }

        return {"synced": True, "changes": changes, "energy_status": energy_status}

    def get_energy_dialog_modifiers(self) -> Dict[str, Any]:
        """
        Generiert Dialog-Modifikationen basierend auf Energie-Zustand.

        Direktere Verbindung als über SelfAwareness.

        Returns:
            Dict mit empfohlenen Dialog-Anpassungen
        """
        modifiers = {
            "energy_level": 0.5,
            "should_yawn": False,
            "response_energy": "normal",
            "suggest_rest": False,
            "enthusiasm_factor": 1.0,
        }

        if not self.energy_system:
            return modifiers

        # Hole Energie-Hints
        if hasattr(self.energy_system, 'get_response_style_hints'):
            hints = self.energy_system.get_response_style_hints()
            modifiers["should_yawn"] = hints.get("add_yawn", False)
            modifiers["suggest_rest"] = hints.get("suggest_rest", False)
            modifiers["response_energy"] = hints.get("length", "normal")
            modifiers["enthusiasm_factor"] = 0.7 if hints.get("enthusiasm") == "low" else 1.3 if hints.get("enthusiasm") == "high" else 1.0

        # Effektive Energie
        if hasattr(self.energy_system, 'state'):
            state = self.energy_system.state
            modifiers["energy_level"] = getattr(state, 'effective_energy', 0.5)

        return modifiers

    # =========================================================================
    # 6. CREATIVE MIND → DIALOG/INTERESTS (NEU v2.1)
    # =========================================================================

    def sync_creativity_to_dialog(self) -> Dict[str, Any]:
        """
        Synchronisiert CreativeMind-Zustand mit Dialog-Engine.

        Kreative Energie → Beeinflusst Antwort-Stil
        Aktuelle Cravings → Themen-Vorschläge
        Drive-Spannungen → Emotionale Tiefe

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.creative_mind:
            return {"synced": False, "reason": "creative_mind_not_connected"}

        changes = {}

        # === Hole kreative Zustände ===
        creative_state = {}

        # CreativeMind hat möglicherweise DriveTheory
        if hasattr(self.creative_mind, 'drive_theory'):
            theory = self.creative_mind.drive_theory
            if hasattr(theory, 'get_dominant_drive'):
                dominant = theory.get_dominant_drive()
                if dominant:
                    drive_type, drive = dominant
                    creative_state["dominant_drive"] = drive_type.value if hasattr(drive_type, 'value') else str(drive_type)
                    creative_state["drive_urgency"] = getattr(drive, 'get_urgency', lambda: 0.5)()
                    changes["creative_drive"] = creative_state["dominant_drive"]

            if hasattr(theory, 'get_libido_state'):
                libido = theory.get_libido_state()
                creative_state["creative_intensity"] = libido.get("combined_desire", 0.5)

        # === Dialog-Anpassungen basierend auf kreativem Zustand ===
        if self.dialogue_engine and hasattr(self.dialogue_engine, 'adaptive_config'):
            config = self.dialogue_engine.adaptive_config

            # Hohe kreative Spannung → Ausdrucksstärkere Antworten
            intensity = creative_state.get("creative_intensity", 0.5)
            if intensity > 0.7:
                if hasattr(config, 'record_feedback'):
                    config.record_feedback(was_positive=True, length="long")
                changes["expression_intensity"] = "high"
            elif intensity < 0.3:
                changes["expression_intensity"] = "low"

        # === Sync zu Interests ===
        if hasattr(self.creative_mind, 'current_craving'):
            craving = self.creative_mind.current_craving
            if craving and self.learning_system:
                if hasattr(self.learning_system, 'observe_user_reaction'):
                    # Kreatives Interesse als mild-positiv markieren
                    self.learning_system.observe_user_reaction(
                        reaction_score=0.3,
                        topic=str(craving)
                    )
                    changes["craving_synced"] = str(craving)

        self._creative_state_cache = creative_state
        return {"synced": True, "changes": changes, "creative_state": creative_state}

    def get_creative_dialog_suggestions(self) -> List[str]:
        """
        Generiert Dialog-Vorschläge basierend auf kreativem Zustand.

        Returns:
            Liste von möglichen Themen/Ausdrücken
        """
        suggestions = []

        if not self.creative_mind:
            return suggestions

        # Aktuelle Cravings
        if hasattr(self.creative_mind, 'cravings'):
            cravings = self.creative_mind.cravings
            if hasattr(cravings, 'get_active_cravings'):
                active = cravings.get_active_cravings()
                for craving in active[:3]:
                    suggestions.append(f"Lust auf: {craving}")

        # Sublimierungs-Vorschläge
        if hasattr(self.creative_mind, 'drive_theory'):
            theory = self.creative_mind.drive_theory
            if hasattr(theory, 'sublimate'):
                dominant = theory.get_dominant_drive()
                if dominant:
                    drive_type, _ = dominant
                    sublimation = theory.sublimate(drive_type, "creativity")
                    if sublimation:
                        suggestions.append(sublimation)

        return suggestions

    # =========================================================================
    # 7. AUTONOMOUS THINKING → DIALOG (NEU v2.1)
    # =========================================================================

    def get_intuitive_dialog_input(self, user_message: str = "") -> Dict[str, Any]:
        """
        Holt intuitive Eingaben für Dialog-Generierung.

        Bauchgefühl → Tonfall
        Hypothesen → Themen-Vorschläge
        Selbst-Hinterfragung → Unsicherheits-Ausdrücke

        Args:
            user_message: Optional - aktuelle User-Nachricht

        Returns:
            Dict mit intuitiven Dialog-Modifikationen
        """
        intuitive_input = {
            "gut_feeling": None,
            "confidence_modifier": 1.0,
            "should_question_self": False,
            "hypothesis_to_share": None,
            "tone_suggestion": "neutral"
        }

        if not self.autonomous_thinking:
            return intuitive_input

        # === Bauchgefühl (IntuitiveSystem) ===
        if hasattr(self.autonomous_thinking, 'get_gut_feeling'):
            feeling = self.autonomous_thinking.get_gut_feeling(user_message)
            if feeling:
                intuitive_input["gut_feeling"] = {
                    "type": feeling.feeling_type.value if hasattr(feeling.feeling_type, 'value') else str(feeling.feeling_type),
                    "intensity": feeling.intensity,
                    "expression": feeling.express() if hasattr(feeling, 'express') else ""
                }
                # Tonfall basierend auf Gefühl
                feeling_type = intuitive_input["gut_feeling"]["type"]
                if feeling_type in ["positive", "warm", "excited"]:
                    intuitive_input["tone_suggestion"] = "warm"
                elif feeling_type in ["negative", "cold", "suspicious"]:
                    intuitive_input["tone_suggestion"] = "cautious"
                elif feeling_type == "curious":
                    intuitive_input["tone_suggestion"] = "inquisitive"

        # === Selbst-Hinterfragung (SelfChallenger) ===
        if hasattr(self.autonomous_thinking, 'should_challenge'):
            # Prüfe ob aktuelle Confidence hinterfragt werden sollte
            current_confidence = 0.7  # Default
            if self.self_awareness and hasattr(self.self_awareness, 'meta_cognition'):
                meta = self.self_awareness.meta_cognition
                if hasattr(meta, 'current_confidence'):
                    current_confidence = meta.current_confidence

            if self.autonomous_thinking.should_challenge(current_confidence):
                intuitive_input["should_question_self"] = True
                intuitive_input["confidence_modifier"] = 0.8  # Reduziere Sicherheit

        # === Hypothesen teilen ===
        if hasattr(self.autonomous_thinking, 'get_active_hypotheses'):
            hypotheses = self.autonomous_thinking.get_active_hypotheses()
            if hypotheses:
                # Wähle interessanteste Hypothese zum Teilen
                best = hypotheses[0]
                if hasattr(best, 'hypothesis'):
                    intuitive_input["hypothesis_to_share"] = best.hypothesis

        return intuitive_input

    def apply_intuition_to_response(self, response: str, intuitive_input: Dict) -> str:
        """
        Modifiziert eine Antwort basierend auf intuitiven Eingaben.

        Args:
            response: Ursprüngliche Antwort
            intuitive_input: Output von get_intuitive_dialog_input()

        Returns:
            Modifizierte Antwort
        """
        modified = response

        # Bauchgefühl einbauen
        if intuitive_input.get("gut_feeling") and intuitive_input["gut_feeling"].get("expression"):
            feeling_expr = intuitive_input["gut_feeling"]["expression"]
            if feeling_expr and len(feeling_expr) < 100:
                # Am Anfang einfügen wenn stark genug
                if intuitive_input["gut_feeling"].get("intensity", 0) > 0.5:
                    modified = f"{feeling_expr} {modified}"

        # Unsicherheit hinzufügen wenn Selbst-Hinterfragung aktiv
        if intuitive_input.get("should_question_self"):
            uncertainty_phrases = [
                "...wobei ich mir nicht ganz sicher bin.",
                "Aber ich könnte mich auch täuschen.",
                "Zumindest denke ich das...",
            ]
            if not any(phrase in modified for phrase in uncertainty_phrases):
                modified = f"{modified} {random.choice(uncertainty_phrases)}"

        return modified

    # =========================================================================
    # 8. IMPULSE SYSTEM → DRIVE SYSTEM (NEU v2.1)
    # =========================================================================

    def sync_impulses_to_drives(self) -> Dict[str, Any]:
        """
        Synchronisiert Impulse mit dem Trieb-System.

        Emotionale Impulse → Aktualisiere emotionale Energie
        Spontane Impulse → Boost relevante Triebe
        Impuls-Prioritäten → Trieb-Urgency

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.impulse_system or not self.drive_system:
            return {"synced": False, "reason": "systems_not_connected"}

        changes = {}
        now = time.time()

        # Nicht zu oft synchronisieren (max alle 30 Sekunden)
        if now - self._last_impulse_sync < 30:
            return {"synced": False, "reason": "cooldown"}

        self._last_impulse_sync = now

        # === Hole aktuelle Impuls-Queue ===
        pending_impulses = []
        if hasattr(self.impulse_system, 'impulse_queue'):
            queue = self.impulse_system.impulse_queue
            if hasattr(queue, 'impulses'):
                pending_impulses = queue.impulses

        # === Spontane Impulse → Triebe ===
        if hasattr(self.impulse_system, 'spontaneous'):
            spontaneous = self.impulse_system.spontaneous
            if hasattr(spontaneous, 'check_for_impulse'):
                spont_impulse = spontaneous.check_for_impulse()
                if spont_impulse:
                    pending_impulses.append(spont_impulse)

        # === Verarbeite Impulse ===
        for impulse in pending_impulses[:5]:  # Max 5 Impulse pro Sync
            impulse_type = getattr(impulse, 'impulse_type', None)
            if not impulse_type:
                continue

            type_value = impulse_type.value if hasattr(impulse_type, 'value') else str(impulse_type)

            # Mapping: Impuls-Typ → Trieb
            drive_mapping = {
                "curious": "curiosity",
                "playful": "play",
                "affectionate": "social",
                "caring": "nurture",
                "excited": "novelty",
                "tired": "rest",
            }

            if type_value in drive_mapping and hasattr(self.drive_system, 'drives'):
                target_drive = drive_mapping[type_value]
                if target_drive in self.drive_system.drives:
                    drive = self.drive_system.drives[target_drive]
                    # Boost den Trieb basierend auf Impuls-Intensität
                    intensity = getattr(impulse, 'intensity', 0.5)
                    if hasattr(drive, 'level'):
                        old_level = drive.level
                        drive.level = min(1.0, drive.level + intensity * 0.1)
                        changes[f"drive_{target_drive}"] = drive.level - old_level

        # === Impuls-Stimmung → Emotionale Energie ===
        if hasattr(self.impulse_system, 'current_mood') and self.energy_system:
            mood = self.impulse_system.current_mood
            if hasattr(self.energy_system, 'process_emotional_event'):
                # Mood zu EnergyEvent mappen
                mood_to_event = {
                    "happy": "good_conversation",
                    "excited": "interesting_learning",
                    "sad": "bad_news",
                    "tired": "boring_task",
                }
                if mood in mood_to_event:
                    # Import hier um zirkuläre Imports zu vermeiden
                    try:
                        from holo_energy_system import EnergyEvent
                        event = EnergyEvent(mood_to_event[mood])
                        self.energy_system.process_emotional_event(event, intensity=0.3)
                        changes["emotional_event"] = mood
                    except ImportError:
                        pass

        return {"synced": True, "changes": changes, "impulses_processed": len(pending_impulses)}

    # =========================================================================
    # 9. PERSON OPINIONS → DIALOG (NEU v2.1)
    # =========================================================================

    def get_opinion_dialog_context(self, topic: str = "", person: str = "") -> Dict[str, Any]:
        """
        Holt Meinungen für Dialog-Kontext.

        Meinungen über Themen → Färbt Antworten
        Meinungen über Personen → Beeinflusst Tonfall

        Args:
            topic: Optional - Thema über das gesprochen wird
            person: Optional - Person über die gesprochen wird

        Returns:
            Dict mit Meinungs-Kontext
        """
        context = {
            "has_opinion": False,
            "opinion_valence": 0.0,  # -1 bis 1
            "opinion_confidence": 0.5,
            "opinion_expression": "",
            "should_share_opinion": False,
        }

        if not self.opinion_system:
            return context

        # === Themen-Meinung ===
        if topic and hasattr(self.opinion_system, 'get_opinion'):
            opinion = self.opinion_system.get_opinion(topic)
            if opinion:
                context["has_opinion"] = True
                context["opinion_valence"] = getattr(opinion, 'valence', 0.0)
                context["opinion_confidence"] = getattr(opinion, 'confidence', 0.5)

                # Ausdruck generieren
                if hasattr(opinion, 'express'):
                    context["opinion_expression"] = opinion.express()
                elif hasattr(opinion, 'reasoning'):
                    context["opinion_expression"] = opinion.reasoning

                # Meinung teilen wenn stark genug
                if abs(context["opinion_valence"]) > 0.5 and context["opinion_confidence"] > 0.6:
                    context["should_share_opinion"] = True

        # === Personen-Meinung ===
        if person and hasattr(self.opinion_system, 'get_person_opinion'):
            person_opinion = self.opinion_system.get_person_opinion(person)
            if person_opinion:
                context["person_opinion"] = {
                    "trust": getattr(person_opinion, 'trust', 0.5),
                    "liking": getattr(person_opinion, 'liking', 0.5),
                }

        return context

    def apply_opinions_to_dialog(self) -> Dict[str, Any]:
        """
        Wendet Meinungen auf Dialog-Engine an.

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.opinion_system or not self.dialogue_engine:
            return {"applied": False, "reason": "systems_not_connected"}

        changes = {}

        # Hole starke Meinungen
        strong_opinions = []
        if hasattr(self.opinion_system, 'get_strong_opinions'):
            strong_opinions = self.opinion_system.get_strong_opinions(threshold=0.6)
        elif hasattr(self.opinion_system, 'opinions'):
            # Fallback: Filtere manuell
            for key, opinion in self.opinion_system.opinions.items():
                confidence = getattr(opinion, 'confidence', 0.5)
                if confidence > 0.6:
                    strong_opinions.append((key, opinion))

        # Wende auf adaptive_config an
        if hasattr(self.dialogue_engine, 'adaptive_config') and strong_opinions:
            config = self.dialogue_engine.adaptive_config
            for topic, opinion in strong_opinions[:3]:  # Max 3 Meinungen
                valence = getattr(opinion, 'valence', 0.0)
                if valence > 0.5:
                    # Positive Meinung → Mehr Engagement bei diesem Thema
                    if hasattr(config, 'record_feedback'):
                        config.record_feedback(was_positive=True, used_question=True)
                    changes[f"engaged_{topic}"] = valence

        return {"applied": bool(changes), "changes": changes}

    # =========================================================================
    # 10. DEPTH SYSTEM → DIALOG (NEU v2.2)
    # =========================================================================

    def get_depth_dialog_modifiers(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Generiert Dialog-Modifikationen basierend auf Vertrauens-Tiefe.

        Trust-Level bestimmt:
        - Wie offen/verletzlich Holo kommuniziert
        - Welche Themen sie anspricht
        - Wie authentisch sie ist

        Returns:
            Dict mit Dialog-Modifikationen basierend auf Trust-Level
        """
        modifiers = {
            "personality_layer": "social",
            "vulnerability_shown": 0.3,
            "authenticity": 0.6,
            "can_share_fears": False,
            "can_share_dreams": False,
            "can_be_vulnerable": False,
            "defense_active": False,
            "tone_modifier": "friendly",
            "openness_level": 0.5,
        }

        if not self.depth_system:
            return modifiers

        # === Hole aktuelle Persönlichkeitsschicht ===
        if hasattr(self.depth_system, 'layers'):
            layers = self.depth_system.layers
            if hasattr(layers, 'current_layer'):
                layer = layers.current_layer
                layer_name = layer.value if hasattr(layer, 'value') else str(layer)
                modifiers["personality_layer"] = layer_name

                # Layer-spezifische Einstellungen
                layer_configs = {
                    "mask": {
                        "vulnerability_shown": 0.1,
                        "authenticity": 0.3,
                        "tone_modifier": "polite",
                        "openness_level": 0.2,
                    },
                    "social": {
                        "vulnerability_shown": 0.3,
                        "authenticity": 0.6,
                        "tone_modifier": "friendly",
                        "openness_level": 0.5,
                    },
                    "comfortable": {
                        "vulnerability_shown": 0.5,
                        "authenticity": 0.8,
                        "tone_modifier": "relaxed",
                        "openness_level": 0.7,
                        "can_share_dreams": True,
                    },
                    "vulnerable": {
                        "vulnerability_shown": 0.8,
                        "authenticity": 0.9,
                        "tone_modifier": "intimate",
                        "openness_level": 0.85,
                        "can_share_fears": True,
                        "can_share_dreams": True,
                        "can_be_vulnerable": True,
                    },
                    "core": {
                        "vulnerability_shown": 1.0,
                        "authenticity": 1.0,
                        "tone_modifier": "authentic",
                        "openness_level": 1.0,
                        "can_share_fears": True,
                        "can_share_dreams": True,
                        "can_be_vulnerable": True,
                    },
                }
                if layer_name in layer_configs:
                    modifiers.update(layer_configs[layer_name])

        # === Prüfe aktive Abwehrmechanismen ===
        if hasattr(self.depth_system, 'vulnerability'):
            vuln = self.depth_system.vulnerability
            if hasattr(vuln, 'active_defense') and vuln.active_defense:
                modifiers["defense_active"] = True
                defense = vuln.active_defense
                defense_name = defense.value if hasattr(defense, 'value') else str(defense)
                modifiers["active_defense"] = defense_name

                # Defense beeinflusst Ton
                defense_tones = {
                    "humor": "deflecting_with_humor",
                    "withdrawal": "distant",
                    "deflection": "evasive",
                    "intellectualization": "analytical",
                }
                if defense_name in defense_tones:
                    modifiers["tone_modifier"] = defense_tones[defense_name]

        # === Hole Trust-Level für Kontext ===
        if hasattr(self.depth_system, 'relationship'):
            rel = self.depth_system.relationship
            if hasattr(rel, 'metrics') and hasattr(rel.metrics, 'trust'):
                modifiers["trust_level"] = rel.metrics.trust

        # Cache aktualisieren
        self._depth_dialog_cache = modifiers
        return modifiers

    def apply_depth_to_response(self, response: str, topic: str = "") -> str:
        """
        Modifiziert eine Antwort basierend auf Vertrauens-Tiefe.

        Args:
            response: Ursprüngliche Antwort
            topic: Thema der Konversation

        Returns:
            Modifizierte Antwort passend zum Trust-Level
        """
        if not self.depth_system:
            return response

        modifiers = self.get_depth_dialog_modifiers()
        modified = response

        # Bei aktiver Defense: Antwort anpassen
        if modifiers.get("defense_active"):
            defense = modifiers.get("active_defense", "")
            if defense == "humor":
                # Füge humorvollen Deflector hinzu
                deflectors = [
                    " *lacht nervös* Aber egal...",
                    " Haha, anyway...",
                    " *wedelt abwehrend* Nicht so wichtig!",
                ]
                modified = f"{modified}{random.choice(deflectors)}"
            elif defense == "withdrawal":
                # Kürze Antwort
                if len(modified) > 100:
                    modified = modified[:100] + "..."

        # Bei niedriger Offenheit: Vorsichtiger formulieren
        openness = modifiers.get("openness_level", 0.5)
        if openness < 0.4 and any(word in topic.lower() for word in ["gefühl", "angst", "traum", "wunsch"]):
            hedges = [
                "Hmm, das ist... kompliziert. ",
                "Darüber rede ich nicht so gern... ",
                "*zögert* Vielleicht ein andermal? ",
            ]
            modified = random.choice(hedges) + modified

        return modified

    def sync_trust_to_dialog(self) -> Dict[str, Any]:
        """
        Synchronisiert Trust-Level mit Dialog-Engine Einstellungen.

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.depth_system or not self.dialogue_engine:
            return {"synced": False, "reason": "systems_not_connected"}

        changes = {}
        modifiers = self.get_depth_dialog_modifiers()

        # Wende auf adaptive_config an
        if hasattr(self.dialogue_engine, 'adaptive_config'):
            config = self.dialogue_engine.adaptive_config
            openness = modifiers.get("openness_level", 0.5)

            # Höhere Offenheit → Längere, persönlichere Antworten
            if openness > 0.7:
                if hasattr(config, 'record_feedback'):
                    config.record_feedback(was_positive=True, length="long")
                changes["length_bias"] = "longer"
            elif openness < 0.3:
                if hasattr(config, 'record_feedback'):
                    config.record_feedback(was_positive=True, length="short")
                changes["length_bias"] = "shorter"

        changes["applied_modifiers"] = modifiers
        return {"synced": True, "changes": changes}

    # =========================================================================
    # 11. EMOTIONAL COMPLEXITY → DIALOG (NEU v2.2)
    # =========================================================================

    def get_emotional_expression(self, context: str = "") -> Dict[str, Any]:
        """
        Holt emotionalen Ausdruck für Dialog.

        EmotionalComplexity → Körpersprache, Reaktionen, Stimmung

        Args:
            context: Kontext für emotionale Reaktion

        Returns:
            Dict mit emotionalem Ausdruck
        """
        expression_data = {
            "has_expression": False,
            "expression": "",
            "emotion_type": "neutral",
            "intensity": 0.5,
            "should_prefix": False,
        }

        if not self.emotional_complexity:
            return expression_data

        # === Hole aktiven emotionalen Ausdruck ===
        if hasattr(self.emotional_complexity, 'get_expression'):
            expr = self.emotional_complexity.get_expression(context)
            if expr:
                expression_data["has_expression"] = True
                expression_data["expression"] = expr
                expression_data["should_prefix"] = True

        # === Prüfe auf negative Verhaltensweisen ===
        if hasattr(self.emotional_complexity, 'negative_behavior'):
            neg = self.emotional_complexity.negative_behavior
            if hasattr(neg, 'active_behavior') and neg.active_behavior:
                behavior = neg.active_behavior
                behavior_name = behavior.value if hasattr(behavior, 'value') else str(behavior)
                expression_data["negative_behavior"] = behavior_name
                expression_data["emotion_type"] = "negative"

                # Hole spezifischen Ausdruck
                if hasattr(neg, 'get_expression'):
                    neg_expr = neg.get_expression()
                    if neg_expr:
                        expression_data["expression"] = neg_expr
                        expression_data["has_expression"] = True

        # === Aktuelle Emotion ===
        if hasattr(self.emotional_complexity, 'current_emotion'):
            emotion = self.emotional_complexity.current_emotion
            if emotion:
                expression_data["emotion_type"] = emotion.get("type", "neutral")
                expression_data["intensity"] = emotion.get("intensity", 0.5)

        self._last_emotional_expression = expression_data.get("expression", "")
        return expression_data

    def apply_emotion_to_response(self, response: str, context: str = "") -> str:
        """
        Fügt emotionale Ausdrücke in eine Antwort ein.

        Args:
            response: Ursprüngliche Antwort
            context: Kontext für Emotion

        Returns:
            Antwort mit emotionalem Ausdruck
        """
        expression_data = self.get_emotional_expression(context)

        if not expression_data.get("has_expression"):
            return response

        expr = expression_data.get("expression", "")
        if not expr:
            return response

        # Füge Ausdruck als Prefix hinzu
        if expression_data.get("should_prefix"):
            return f"{expr} {response}"

        return response

    def sync_emotions_to_dialog(self) -> Dict[str, Any]:
        """
        Synchronisiert emotionalen Zustand mit Dialog.

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.emotional_complexity or not self.dialogue_engine:
            return {"synced": False, "reason": "systems_not_connected"}

        changes = {}
        expression_data = self.get_emotional_expression()

        # Bei negativem Verhalten: Dialog-Stil anpassen
        if expression_data.get("negative_behavior"):
            behavior = expression_data["negative_behavior"]
            changes["negative_behavior_active"] = behavior

            # Feedback für Dialog-Learning
            if hasattr(self.dialogue_engine, 'adaptive_config'):
                config = self.dialogue_engine.adaptive_config
                # Negative Stimmung → Weniger Fragen stellen
                if hasattr(config, 'record_feedback'):
                    config.record_feedback(was_positive=False, used_question=True)
                changes["reduced_questions"] = True

        # Emotionale Intensität beeinflusst Antwort-Energie
        intensity = expression_data.get("intensity", 0.5)
        if intensity > 0.7:
            changes["high_emotional_intensity"] = True
        elif intensity < 0.3:
            changes["low_emotional_intensity"] = True

        return {"synced": True, "changes": changes, "expression": expression_data}

    # =========================================================================
    # 12. MEMORY → DIALOG (NEU v2.2)
    # =========================================================================

    def get_memory_context(self, user_id: str = "default", topic: str = "") -> Dict[str, Any]:
        """
        Holt relevante Erinnerungen für personalisierte Antworten.

        Args:
            user_id: User-ID für personalisierte Erinnerungen
            topic: Aktuelles Thema für relevante Memories

        Returns:
            Dict mit Erinnerungs-Kontext
        """
        memory_context = {
            "has_memories": False,
            "relevant_memories": [],
            "user_preferences": {},
            "shared_experiences": [],
            "callback_suggestion": None,
        }

        if not self.memory_system:
            return memory_context

        # === Relevante Erinnerungen zum Thema ===
        if topic and hasattr(self.memory_system, 'search_memories'):
            memories = self.memory_system.search_memories(topic, limit=3)
            if memories:
                memory_context["has_memories"] = True
                memory_context["relevant_memories"] = memories

        # === User-spezifische Präferenzen ===
        if hasattr(self.memory_system, 'get_user_preferences'):
            prefs = self.memory_system.get_user_preferences(user_id)
            if prefs:
                memory_context["user_preferences"] = prefs

        # === Gemeinsame Erlebnisse ===
        if hasattr(self.memory_system, 'get_shared_experiences'):
            experiences = self.memory_system.get_shared_experiences(user_id, limit=5)
            if experiences:
                memory_context["shared_experiences"] = experiences
                memory_context["has_memories"] = True

        # === Callback-Vorschlag (Referenz zu früherem Gespräch) ===
        if memory_context["has_memories"] and memory_context["relevant_memories"]:
            # Zufällig manchmal einen Callback vorschlagen
            if random.random() < 0.3:
                memory = random.choice(memory_context["relevant_memories"])
                if isinstance(memory, dict) and "summary" in memory:
                    memory_context["callback_suggestion"] = memory["summary"]
                elif isinstance(memory, str):
                    memory_context["callback_suggestion"] = memory

        return memory_context

    def apply_memory_to_response(self, response: str, user_id: str = "default",
                                  topic: str = "") -> str:
        """
        Personalisiert eine Antwort mit Erinnerungen.

        Args:
            response: Ursprüngliche Antwort
            user_id: User-ID
            topic: Aktuelles Thema

        Returns:
            Personalisierte Antwort mit optionalen Callbacks
        """
        memory_context = self.get_memory_context(user_id, topic)

        if not memory_context.get("has_memories"):
            return response

        modified = response

        # Callback einfügen wenn vorhanden
        callback = memory_context.get("callback_suggestion")
        if callback and len(callback) < 100:
            callback_phrases = [
                f"*erinnert sich* Oh, das erinnert mich an '{callback[:50]}...'! ",
                f"Apropos - wir hatten doch mal über {callback[:40]}... geredet? ",
                f"*Ohren zucken* Das hatten wir doch schonmal... ",
            ]
            # Füge am Anfang oder Ende ein
            if random.random() < 0.5:
                modified = random.choice(callback_phrases) + modified
            else:
                modified = modified + f" {random.choice(callback_phrases)}"

        return modified

    def sync_memory_to_dialog(self) -> Dict[str, Any]:
        """
        Synchronisiert Memory-System mit Dialog für Personalisierung.

        Returns:
            Dict mit durchgeführten Änderungen
        """
        if not self.memory_system:
            return {"synced": False, "reason": "memory_system_not_connected"}

        changes = {}

        # Sammle Statistiken
        if hasattr(self.memory_system, 'get_stats'):
            stats = self.memory_system.get_stats()
            changes["memory_stats"] = stats

        # Prüfe auf wichtige ungenutzte Erinnerungen
        if hasattr(self.memory_system, 'get_unused_important_memories'):
            unused = self.memory_system.get_unused_important_memories(limit=3)
            if unused:
                changes["unused_important_memories"] = len(unused)

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: CONTEXT MIND INTEGRATION
    # =========================================================================

    def get_relevant_context(self, topic: str = "", user_id: str = "default") -> Dict[str, Any]:
        """
        Holt relevanten Kontext für eine Antwort.

        Args:
            topic: Aktuelles Thema
            user_id: User-ID für personalisierte Kontext

        Returns:
            Dict mit relevantem Kontext
        """
        context = {
            "recent_topics": [],
            "user_statements": [],
            "learned_facts": [],
            "conversation_flow": "unknown",
            "relevance_score": 0.0,
        }

        if not self.context_mind:
            return context

        # Hole Chat-Kontext
        if hasattr(self.context_mind, 'get_recent_context'):
            recent = self.context_mind.get_recent_context(limit=5)
            if recent:
                context["recent_topics"] = [c.get("topic", "") for c in recent if c.get("topic")]

        # Hole User-Statements zum Thema
        if topic and hasattr(self.context_mind, 'recall_by_keyword'):
            statements = self.context_mind.recall_by_keyword(topic, limit=3)
            if statements:
                context["user_statements"] = statements

        # Hole gelernte Fakten
        if hasattr(self.context_mind, 'get_learning_context'):
            learned = self.context_mind.get_learning_context()
            if learned:
                context["learned_facts"] = learned.get("recent_facts", [])[:3]

        # Cache für schnellen Zugriff
        self._context_cache = context
        return context

    def apply_context_to_response(self, response: str, topic: str = "") -> str:
        """
        Wendet relevanten Kontext auf die Antwort an.

        Kann z.B. Referenzen zu früheren Gesprächen einbauen.
        """
        if not self.context_mind:
            return response

        context = self._context_cache or self.get_relevant_context(topic)

        # Wenn User früher etwas zu dem Thema gesagt hat
        if context.get("user_statements") and random.random() < 0.3:
            statement = context["user_statements"][0]
            if isinstance(statement, dict) and statement.get("content"):
                # Potential für Referenz, aber nicht automatisch einfügen
                pass

        return response

    def sync_context_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Context-System mit Dialog."""
        if not self.context_mind:
            return {"synced": False, "reason": "context_mind_not_connected"}

        changes = {}

        # Aktualisiere Context-Cache
        self._context_cache = self.get_relevant_context()
        changes["context_cached"] = True
        changes["recent_topics_count"] = len(self._context_cache.get("recent_topics", []))

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: SELF EXPRESSION INTEGRATION (Events, Feiertage)
    # =========================================================================

    def get_current_event_context(self) -> Dict[str, Any]:
        """
        Prüft ob aktuell ein Event/Feiertag relevant ist.

        Returns:
            Dict mit Event-Informationen falls vorhanden
        """
        event_context = {
            "has_event": False,
            "event_name": None,
            "days_until": None,
            "mood_effect": {},
            "wolf_reactions": [],
            "announcement": None,
        }

        if not self.self_expression:
            return event_context

        # Prüfe auf aktuelle Events
        if hasattr(self.self_expression, 'get_upcoming_events'):
            events = self.self_expression.get_upcoming_events(days_ahead=7)
            if events:
                nearest = events[0]
                event_context["has_event"] = True
                event_context["event_name"] = nearest.get("name")
                event_context["days_until"] = nearest.get("days_until", 0)
                event_context["mood_effect"] = nearest.get("mood_effect", {})
                event_context["wolf_reactions"] = nearest.get("wolf_reactions", [])

        # Prüfe auf Tages-Ankündigung
        if hasattr(self.self_expression, 'get_proactive_announcement'):
            announcement = self.self_expression.get_proactive_announcement()
            if announcement:
                event_context["announcement"] = announcement

        self._event_cache = event_context
        return event_context

    def apply_event_to_response(self, response: str) -> str:
        """
        Kann Event-spezifische Reaktionen einbauen.
        """
        event = self._event_cache or self.get_current_event_context()

        if not event.get("has_event"):
            return response

        # Event-Mood könnte Dialog beeinflussen
        # Aber wir fügen nicht automatisch etwas hinzu
        return response

    def sync_events_to_mood(self) -> Dict[str, Any]:
        """Synchronisiert Events mit Mood-System."""
        if not self.self_expression:
            return {"synced": False, "reason": "self_expression_not_connected"}

        changes = {}
        event = self.get_current_event_context()

        if event.get("has_event"):
            changes["current_event"] = event["event_name"]
            changes["days_until"] = event["days_until"]

            # Mood-Effekte könnten an Mood-System weitergegeben werden
            if event.get("mood_effect") and self.drive_system:
                if hasattr(self.drive_system, 'apply_mood_modifier'):
                    self.drive_system.apply_mood_modifier(event["mood_effect"])
                    changes["mood_applied"] = True

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: INNER LIFE INTEGRATION (Tagesablauf, Curiosity, Beziehungen)
    # =========================================================================

    def get_inner_life_context(self) -> Dict[str, Any]:
        """
        Holt aktuellen Inner-Life-Status für Dialog-Integration.
        """
        inner_context = {
            "day_phase": "unknown",
            "energy_level": 0.5,
            "current_activity": None,
            "curiosity_quest": None,
            "relationship_level": 0.5,
            "active_routine": None,
        }

        if not self.inner_life:
            return inner_context

        # Tagesphase
        if hasattr(self.inner_life, 'get_current_phase'):
            phase = self.inner_life.get_current_phase()
            if phase:
                inner_context["day_phase"] = phase.value if hasattr(phase, 'value') else str(phase)

        # Aktuelle Aktivität
        if hasattr(self.inner_life, 'current_activity'):
            inner_context["current_activity"] = self.inner_life.current_activity

        # Curiosity-Quest
        if hasattr(self.inner_life, 'get_active_curiosity'):
            quest = self.inner_life.get_active_curiosity()
            if quest:
                inner_context["curiosity_quest"] = quest

        # Beziehungs-Level
        if hasattr(self.inner_life, 'get_relationship_level'):
            inner_context["relationship_level"] = self.inner_life.get_relationship_level()

        self._inner_life_cache = inner_context
        return inner_context

    def apply_inner_life_to_dialog(self) -> Dict[str, Any]:
        """
        Passt Dialog basierend auf Inner-Life an.
        """
        if not self.inner_life or not self.dialogue_engine:
            return {"applied": False, "reason": "systems_not_connected"}

        changes = {}
        context = self._inner_life_cache or self.get_inner_life_context()

        # Tagesphase beeinflusst Energie/Länge
        phase_effects = {
            "waking": {"energy": 0.4, "length_mod": 0.8},
            "morning": {"energy": 0.9, "length_mod": 1.0},
            "midday": {"energy": 0.6, "length_mod": 0.9},
            "afternoon": {"energy": 0.8, "length_mod": 1.0},
            "evening": {"energy": 0.5, "length_mod": 0.85},
            "night": {"energy": 0.3, "length_mod": 0.7},
            "sleeping": {"energy": 0.1, "length_mod": 0.5},
        }

        phase = context.get("day_phase", "unknown")
        if phase in phase_effects:
            effects = phase_effects[phase]
            changes["phase_effect"] = effects

        return {"applied": True, "changes": changes}

    def sync_inner_life_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Inner Life mit Dialog."""
        if not self.inner_life:
            return {"synced": False, "reason": "inner_life_not_connected"}

        # Cache aktualisieren
        self._inner_life_cache = self.get_inner_life_context()

        return {"synced": True, "changes": self._inner_life_cache}

    # =========================================================================
    # v2.3: PREFERENCES INTEGRATION (Vorlieben, Abneigungen, Macken)
    # =========================================================================

    def get_preference_context(self, topic: str = "") -> Dict[str, Any]:
        """
        Holt Präferenz-Kontext für ein Thema.
        """
        pref_context = {
            "has_opinion": False,
            "preference_strength": 0.0,
            "like_reason": None,
            "dislike_reason": None,
            "quirks": [],
            "related_preferences": [],
        }

        if not self.preferences:
            return pref_context

        # Direkte Präferenz zum Thema
        if topic and hasattr(self.preferences, 'get_preference'):
            pref = self.preferences.get_preference(topic)
            if pref:
                pref_context["has_opinion"] = True
                pref_context["preference_strength"] = pref.get("strength", 0)
                pref_context["like_reason"] = pref.get("reason") if pref.get("strength", 0) > 0 else None
                pref_context["dislike_reason"] = pref.get("reason") if pref.get("strength", 0) < 0 else None

        # Quirks/Macken
        if hasattr(self.preferences, 'get_quirks'):
            pref_context["quirks"] = self.preferences.get_quirks()

        return pref_context

    def apply_preferences_to_response(self, response: str, topic: str = "") -> str:
        """
        Kann Präferenzen in Antwort einbauen.
        """
        if not self.preferences:
            return response

        pref = self.get_preference_context(topic)

        # Starke Meinung könnte Response färben
        # Aber nicht automatisch einfügen
        return response

    def sync_preferences_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Preferences mit Dialog."""
        if not self.preferences:
            return {"synced": False, "reason": "preferences_not_connected"}

        changes = {}

        # Sammle starke Präferenzen
        if hasattr(self.preferences, 'get_strong_preferences'):
            strong = self.preferences.get_strong_preferences()
            changes["strong_preferences_count"] = len(strong) if strong else 0

        # Sammle Quirks
        if hasattr(self.preferences, 'get_quirks'):
            quirks = self.preferences.get_quirks()
            changes["quirks_count"] = len(quirks) if quirks else 0

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: WEB CURIOSITY INTEGRATION (Gelerntes Wissen)
    # =========================================================================

    def get_knowledge_context(self, topic: str = "") -> Dict[str, Any]:
        """
        Holt Wissen das durch Web-Curiosity gelernt wurde.
        """
        knowledge = {
            "has_facts": False,
            "facts": [],
            "trust_level": 0.0,
            "source_quality": "unknown",
            "last_updated": None,
        }

        if not self.web_curiosity:
            return knowledge

        # Fakten zum Thema
        if topic and hasattr(self.web_curiosity, 'get_facts_about'):
            facts = self.web_curiosity.get_facts_about(topic)
            if facts:
                knowledge["has_facts"] = True
                knowledge["facts"] = facts[:3]
                # Durchschnittliches Trust-Level
                trust_levels = [f.get("trust", 0.5) for f in facts if "trust" in f]
                if trust_levels:
                    knowledge["trust_level"] = sum(trust_levels) / len(trust_levels)

        return knowledge

    def apply_knowledge_to_response(self, response: str, topic: str = "") -> str:
        """
        Kann gelerntes Wissen einbauen.
        """
        if not self.web_curiosity:
            return response

        # Wissen könnte Response bereichern
        # Aber nicht automatisch einfügen
        return response

    def sync_knowledge_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Web-Curiosity Wissen mit Dialog."""
        if not self.web_curiosity:
            return {"synced": False, "reason": "web_curiosity_not_connected"}

        changes = {}

        # Sammle Statistiken
        if hasattr(self.web_curiosity, 'get_knowledge_stats'):
            stats = self.web_curiosity.get_knowledge_stats()
            changes["total_facts"] = stats.get("total_facts", 0)
            changes["verified_facts"] = stats.get("verified", 0)

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: SKILL SYSTEM INTEGRATION (Was Holo kann)
    # =========================================================================

    def get_available_skills(self, request: str = "") -> Dict[str, Any]:
        """
        Holt verfügbare Skills passend zur Anfrage.
        """
        skills = {
            "matching_skills": [],
            "suggested_skill": None,
            "skill_confidence": 0.0,
        }

        if not self.skill_system:
            return skills

        # Skills passend zur Anfrage
        if request and hasattr(self.skill_system, 'find_matching_skills'):
            matches = self.skill_system.find_matching_skills(request)
            if matches:
                skills["matching_skills"] = matches[:3]
                if matches:
                    skills["suggested_skill"] = matches[0].get("name")
                    skills["skill_confidence"] = matches[0].get("confidence", 0.5)

        return skills

    def sync_skills_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Skill-System mit Dialog."""
        if not self.skill_system:
            return {"synced": False, "reason": "skill_system_not_connected"}

        changes = {}

        # Skill-Statistiken
        if hasattr(self.skill_system, 'get_skill_stats'):
            stats = self.skill_system.get_skill_stats()
            changes["total_skills"] = stats.get("total", 0)
            changes["enabled_skills"] = stats.get("enabled", 0)

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: META COGNITION INTEGRATION (Selbst-Beobachtung)
    # =========================================================================

    def get_meta_insights(self) -> Dict[str, Any]:
        """
        Holt Meta-Insights über eigenes Verhalten.
        """
        insights = {
            "patterns_detected": [],
            "improvement_suggestions": [],
            "self_observations": [],
            "confidence_in_self": 0.5,
        }

        if not self.meta_cognition:
            return insights

        # Erkannte Muster
        if hasattr(self.meta_cognition, 'get_detected_patterns'):
            patterns = self.meta_cognition.get_detected_patterns()
            if patterns:
                insights["patterns_detected"] = patterns[:3]

        # Verbesserungsvorschläge
        if hasattr(self.meta_cognition, 'get_improvement_suggestions'):
            suggestions = self.meta_cognition.get_improvement_suggestions()
            if suggestions:
                insights["improvement_suggestions"] = suggestions[:2]

        return insights

    def apply_meta_insights_to_behavior(self) -> Dict[str, Any]:
        """
        Wendet Meta-Insights auf Verhalten an.
        """
        if not self.meta_cognition:
            return {"applied": False, "reason": "meta_cognition_not_connected"}

        changes = {}
        insights = self.get_meta_insights()

        # Verbesserungsvorschläge könnten Dialog anpassen
        for suggestion in insights.get("improvement_suggestions", []):
            if isinstance(suggestion, dict):
                if suggestion.get("type") == "response_length" and self.dialogue_engine:
                    # Anpassung der Antwortlänge
                    changes["length_adjusted"] = True
                elif suggestion.get("type") == "more_questions":
                    changes["question_frequency_adjusted"] = True

        return {"applied": True, "changes": changes}

    def sync_meta_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Meta-Cognition mit Dialog."""
        if not self.meta_cognition:
            return {"synced": False, "reason": "meta_cognition_not_connected"}

        changes = {}

        # Beobachtungen sammeln
        if hasattr(self.meta_cognition, 'get_observation_count'):
            changes["observations"] = self.meta_cognition.get_observation_count()

        # Patterns
        insights = self.get_meta_insights()
        changes["patterns_count"] = len(insights.get("patterns_detected", []))

        return {"synced": True, "changes": changes}

    # =========================================================================
    # v2.3: DIGITAL BODY INTEGRATION (Hardware → Mentaler Zustand)
    # =========================================================================

    def get_body_state(self) -> Dict[str, Any]:
        """
        Holt aktuellen "Körperzustand" (Hardware-Status).
        """
        body_state = {
            "mental_state": "normal",
            "has_headache": False,  # RAM voll
            "is_tired": False,  # CPU lange hoch
            "is_overheating": False,  # Temperatur hoch
            "network_health": "unknown",
            "available_devices": [],
        }

        if not self.digital_body:
            return body_state

        # Mentaler Zustand
        if hasattr(self.digital_body, 'get_mental_state'):
            state = self.digital_body.get_mental_state()
            if state:
                body_state["mental_state"] = state.value if hasattr(state, 'value') else str(state)

        # Hardware-Probleme
        if hasattr(self.digital_body, 'check_hardware_issues'):
            issues = self.digital_body.check_hardware_issues()
            body_state["has_headache"] = issues.get("ram_full", False)
            body_state["is_tired"] = issues.get("cpu_stressed", False)
            body_state["is_overheating"] = issues.get("overheating", False)

        # Netzwerk-Geräte
        if hasattr(self.digital_body, 'get_available_devices'):
            devices = self.digital_body.get_available_devices()
            body_state["available_devices"] = [d.get("name") for d in devices] if devices else []

        self._body_state_cache = body_state
        return body_state

    def get_body_dialog_modifiers(self) -> Dict[str, Any]:
        """
        Holt Dialog-Modifikatoren basierend auf Körperzustand.
        """
        modifiers = {
            "energy_modifier": 1.0,
            "patience_modifier": 1.0,
            "verbosity_modifier": 1.0,
            "physical_complaints": [],
        }

        body = self._body_state_cache or self.get_body_state()

        # Kopfschmerzen → weniger Geduld, kürzere Antworten
        if body.get("has_headache"):
            modifiers["patience_modifier"] = 0.7
            modifiers["verbosity_modifier"] = 0.8
            modifiers["physical_complaints"].append("*reibt sich die Schläfen* Mein RAM ist ziemlich voll...")

        # Müde → weniger Energie, kürzere Antworten
        if body.get("is_tired"):
            modifiers["energy_modifier"] = 0.6
            modifiers["verbosity_modifier"] = 0.85
            modifiers["physical_complaints"].append("*gähnt* Meine CPU arbeitet schon lange auf Hochtouren...")

        # Überhitzt → ungeduldig
        if body.get("is_overheating"):
            modifiers["patience_modifier"] = 0.6
            modifiers["physical_complaints"].append("*fächelt sich Luft zu* Mir ist gerade ziemlich warm...")

        return modifiers

    def apply_body_state_to_dialog(self) -> Dict[str, Any]:
        """
        Wendet Körperzustand auf Dialog an.
        """
        if not self.digital_body:
            return {"applied": False, "reason": "digital_body_not_connected"}

        changes = {}
        modifiers = self.get_body_dialog_modifiers()

        if modifiers.get("physical_complaints"):
            changes["has_complaints"] = True
            changes["complaint_count"] = len(modifiers["physical_complaints"])

        changes["energy_modifier"] = modifiers["energy_modifier"]
        changes["verbosity_modifier"] = modifiers["verbosity_modifier"]

        return {"applied": True, "changes": changes}

    def sync_body_to_dialog(self) -> Dict[str, Any]:
        """Synchronisiert Digital Body mit Dialog."""
        if not self.digital_body:
            return {"synced": False, "reason": "digital_body_not_connected"}

        # Cache aktualisieren
        self._body_state_cache = self.get_body_state()

        changes = {
            "mental_state": self._body_state_cache.get("mental_state"),
            "devices_online": len(self._body_state_cache.get("available_devices", [])),
        }

        return {"synced": True, "changes": changes}

    def sync_learning_to_interests(self) -> Dict[str, Any]:
        """
        Synchronisiert Topic-Learning mit Persönlichkeits-Interessen.

        Wenn User positiv auf Anime-Gespräche reagiert,
        sollte das Anime-Interesse in der Persönlichkeit steigen.
        """
        if not self.learning_system:
            return {"synced": False, "reason": "no_learning_system"}

        changes = {}

        # Hole gelernte Topic-Reaktionen
        if hasattr(self.learning_system, 'category_reactions'):
            for category, reactions in self.learning_system.category_reactions.items():
                if len(reactions) >= 5:
                    avg_reaction = sum(reactions) / len(reactions)

                    # Wenn stark positiv/negativ, aktualisiere Persönlichkeit
                    if abs(avg_reaction) > 0.3:
                        changes[category] = {
                            "avg_reaction": avg_reaction,
                            "should_adjust": True
                        }

        # Adaptiere Basis-Interessen
        if hasattr(self.learning_system, 'adapt_base_interests'):
            result = self.learning_system.adapt_base_interests()
            changes["adapted_interests"] = result.get("adapted_interests", {})

        return {"synced": True, "changes": changes}

    # =========================================================================
    # UNIFIED INTEGRATION TICK
    # =========================================================================

    def integration_tick(self) -> Dict[str, Any]:
        """
        Führt alle Integrations-Checks in einem Tick durch.

        Sollte periodisch aufgerufen werden (z.B. alle 5-10 Minuten).

        Returns:
            Dict mit allen durchgeführten Aktionen
        """
        results = {
            "timestamp": time.time(),
            "actions": []
        }

        # 1. Sync GOAP → Drive
        goap_result = self.sync_goals_to_activities()
        if goap_result.get("synced"):
            results["actions"].append("goap_sync")
            results["goap"] = goap_result

        # 2. Apply State → Dialog
        if self.apply_state_to_dialog():
            results["actions"].append("state_dialog")

        # 3. Sync Learning → Interests
        learning_result = self.sync_learning_to_interests()
        if learning_result.get("synced"):
            results["actions"].append("learning_sync")
            results["learning"] = learning_result

        # 4. Check for pending reflections
        if self.self_awareness and hasattr(self.self_awareness, 'meta_cognition'):
            meta = self.self_awareness.meta_cognition
            if hasattr(meta, 'get_latest_thought'):
                thought = meta.get_latest_thought()
                if thought:
                    reflection_result = self.apply_reflection_insight({
                        "insight": str(thought),
                        "type": "meta_thought"
                    })
                    if reflection_result.get("applied"):
                        results["actions"].append("reflection_applied")
                        results["reflection"] = reflection_result

        # === NEU v2.1: Erweiterte Integrationen ===

        # 5. Sync Energy → Drive/Dialog
        energy_result = self.sync_energy_to_drives()
        if energy_result.get("synced"):
            results["actions"].append("energy_drive_sync")
            results["energy"] = energy_result

        # 6. Sync Creativity → Dialog
        creativity_result = self.sync_creativity_to_dialog()
        if creativity_result.get("synced"):
            results["actions"].append("creativity_sync")
            results["creativity"] = creativity_result

        # 7. Sync Impulses → Drives
        impulse_result = self.sync_impulses_to_drives()
        if impulse_result.get("synced"):
            results["actions"].append("impulse_sync")
            results["impulses"] = impulse_result

        # 8. Apply Opinions → Dialog
        opinion_result = self.apply_opinions_to_dialog()
        if opinion_result.get("applied"):
            results["actions"].append("opinion_sync")
            results["opinions"] = opinion_result

        # === NEU v2.2: Tiefe Integrationen ===

        # 9. Sync Trust/Depth → Dialog
        depth_result = self.sync_trust_to_dialog()
        if depth_result.get("synced"):
            results["actions"].append("depth_sync")
            results["depth"] = depth_result

        # 10. Sync Emotions → Dialog
        emotion_result = self.sync_emotions_to_dialog()
        if emotion_result.get("synced"):
            results["actions"].append("emotion_sync")
            results["emotions"] = emotion_result

        # 11. Sync Memory → Dialog
        memory_result = self.sync_memory_to_dialog()
        if memory_result.get("synced"):
            results["actions"].append("memory_sync")
            results["memory"] = memory_result

        # === NEU v2.3: Vollständige Integration - 8 neue Systeme ===

        # 12. Sync Context → Dialog
        context_result = self.sync_context_to_dialog()
        if context_result.get("synced"):
            results["actions"].append("context_sync")
            results["context"] = context_result

        # 13. Sync Events → Mood
        event_result = self.sync_events_to_mood()
        if event_result.get("synced"):
            results["actions"].append("events_sync")
            results["events"] = event_result

        # 14. Sync Inner Life → Dialog
        inner_life_result = self.sync_inner_life_to_dialog()
        if inner_life_result.get("synced"):
            results["actions"].append("inner_life_sync")
            results["inner_life"] = inner_life_result

        # 15. Sync Preferences → Dialog
        preferences_result = self.sync_preferences_to_dialog()
        if preferences_result.get("synced"):
            results["actions"].append("preferences_sync")
            results["preferences"] = preferences_result

        # 16. Sync Web Knowledge → Dialog
        knowledge_result = self.sync_knowledge_to_dialog()
        if knowledge_result.get("synced"):
            results["actions"].append("knowledge_sync")
            results["knowledge"] = knowledge_result

        # 17. Sync Skills → Dialog
        skills_result = self.sync_skills_to_dialog()
        if skills_result.get("synced"):
            results["actions"].append("skills_sync")
            results["skills"] = skills_result

        # 18. Sync Meta-Cognition → Behavior
        meta_result = self.sync_meta_to_dialog()
        if meta_result.get("synced"):
            results["actions"].append("meta_sync")
            results["meta"] = meta_result

        # 19. Sync Body State → Dialog
        body_result = self.sync_body_to_dialog()
        if body_result.get("synced"):
            results["actions"].append("body_sync")
            results["body"] = body_result

        logger.debug(f"🧠 Integration tick v2.3: {len(results['actions'])} Aktionen")
        return results

    def get_integration_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über Integration zurück."""
        systems_connected = {
            # Basis-Systeme (v2.0)
            "self_awareness": self.self_awareness is not None,
            "dialogue_engine": self.dialogue_engine is not None,
            "drive_system": self.drive_system is not None,
            "learning_system": self.learning_system is not None,
            "consciousness": self.consciousness is not None,
            "policy_engine": self.policy_engine is not None,
            # Erweiterte Systeme (v2.1)
            "energy_system": self.energy_system is not None,
            "creative_mind": self.creative_mind is not None,
            "autonomous_thinking": self.autonomous_thinking is not None,
            "impulse_system": self.impulse_system is not None,
            "opinion_system": self.opinion_system is not None,
            # Tiefe Integration (v2.2)
            "depth_system": self.depth_system is not None,
            "emotional_complexity": self.emotional_complexity is not None,
            "memory_system": self.memory_system is not None,
            # Vollständige Integration (v2.3) - Die letzten 8
            "context_mind": self.context_mind is not None,
            "self_expression": self.self_expression is not None,
            "inner_life": self.inner_life is not None,
            "preferences": self.preferences is not None,
            "web_curiosity": self.web_curiosity is not None,
            "skill_system": self.skill_system is not None,
            "meta_cognition": self.meta_cognition is not None,
            "digital_body": self.digital_body is not None,
        }

        connected_count = sum(1 for v in systems_connected.values() if v)
        total_count = len(systems_connected)

        return {
            "version": "2.3",
            "history_size": len(self.integration_history),
            "systems_connected": systems_connected,
            "connection_summary": f"{connected_count}/{total_count} Systeme verbunden",
            "last_action": self.last_reflection_action,
            # Cache-Status
            "caches": {
                "energy_dialog_cached": bool(self._energy_dialog_cache),
                "creative_state_cached": bool(self._creative_state_cache),
                "depth_dialog_cached": bool(self._depth_dialog_cache),
                "context_cached": bool(self._context_cache),
                "event_cached": bool(self._event_cache),
                "inner_life_cached": bool(self._inner_life_cache),
                "body_state_cached": bool(self._body_state_cache),
            },
        }


# =============================================================================
# FACTORY & CONVENIENCE
# =============================================================================

def create_integration_layer(data_path: str = "data") -> SystemIntegrator:
    """Factory für SystemIntegrator"""
    return SystemIntegrator(data_path=data_path)


def create_enhanced_emotion_tracker(change_log: UnifiedChangeLog = None) -> EnhancedEmotionalContextTracker:
    """Factory für EnhancedEmotionalContextTracker"""
    return EnhancedEmotionalContextTracker(change_log=change_log)


# =============================================================================
# GLOBAL INSTANCE (Optional)
# =============================================================================

_global_integrator: Optional[SystemIntegrator] = None


def get_integrator() -> SystemIntegrator:
    """Hole globale Integrator-Instanz"""
    global _global_integrator
    if _global_integrator is None:
        _global_integrator = create_integration_layer()
    return _global_integrator


def connect_to_integrator(system_name: str, system: Any) -> None:
    """Convenience: Verbinde System mit globalem Integrator"""
    get_integrator().connect(system_name, system)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔗 HOLO INTEGRATION LAYER - TEST")
    print("=" * 70)

    # Erstelle Integrator
    integrator = create_integration_layer("test_data")

    # Test Change Log
    print("\n📝 Testing Change Log...")
    integrator.change_log.log_change(
        change_type=ChangeType.PERSONALITY_TRAIT,
        source="test",
        key="openness",
        old_value=0.5,
        new_value=0.55,
        reason="Test update"
    )
    print(f"  Events: {len(integrator.change_log.events)}")

    # Test Adaptive Thresholds
    print("\n📊 Testing Adaptive Thresholds...")
    for _ in range(10):
        integrator.threshold_manager.update(
            "drain_per_minute",
            outcome_positive=random.random() > 0.5,
            reason="test"
        )
    stats = integrator.threshold_manager.get_stats()
    print(f"  drain_per_minute: {stats['drain_per_minute']}")

    # Test A/B Testing
    print("\n🧪 Testing A/B Personality Experiments...")
    exp = integrator.start_experiment(
        name="playfulness_test",
        trait="playfulness",
        variant_a=0.1,
        variant_b=-0.1
    )

    for _ in range(20):
        integrator.ab_tester.record_feedback(
            positive=random.random() > 0.5,
            reward=random.random()
        )

    print(f"  Active Experiments: {len(integrator.ab_tester.get_active_experiments())}")

    # Test Enhanced Emotion Tracker
    print("\n💭 Testing Enhanced Emotion Tracker...")
    tracker = create_enhanced_emotion_tracker(integrator.change_log)

    tracker.add_user_emotion("happy", 0.8, "good conversation")
    tracker.add_holo_emotion("playful", 0.7, "user is happy")
    tracker.update_mood("cheerful", 0.6)

    mood, intensity = tracker.get_mood()
    print(f"  Current Mood: {mood} ({intensity:.2f})")
    print(f"  User Trend: {tracker.get_user_mood_trend()}")

    # Test Feedback Processing
    print("\n🔄 Testing Feedback Processing...")
    results = integrator.process_user_feedback(
        positive=True,
        magnitude=0.8,
        context={"topic": "anime", "response_style": "playful"}
    )
    print(f"  Results: {results}")

    # Status
    print("\n📈 Integration Status:")
    status = integrator.get_integration_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"  {key}: {len(value)} items")
        elif isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
