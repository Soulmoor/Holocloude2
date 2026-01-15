#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pi-Control ULTIMATE v8.0 - Kognitiver Prädiktiver Agent
======================================================

Vollständiges mehrschichtiges System mit:
- Predictive Processing (Surprise-basierte Lernrate)
- Intrinsic Motivation (Curiosity/Information Gain)
- RAM-First State Management (Asynchrone Persistenz)
- Zone-Based Presence & Expertenregeln
- Home Assistant (HA) Integration für Aktoren
- Goal-Oriented Action Planning (GOAP)
- Multi-Criteria Decision Making (MCDM)
- A/B Testing & Sandbox Simulation

ARCHITEKTUR: 7 Schichten + Kognitive Erweiterungen
"""

from __future__ import annotations
import importlib.util
import json
import logging
import os
import shutil
import hashlib
import signal
import socket
import select
import struct
import subprocess
import sys
import threading
import time
import re
import random
import math
import ast
import statistics
import fcntl
import heapq
from collections import deque, defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from logging.handlers import RotatingFileHandler
from pi_holo_interface import HoloInterface

# Optional imports
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False

try:
    import paramiko
    HAVE_PARAMIKO = True
except ImportError:
    HAVE_PARAMIKO = False

try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False

try:
    from dotenv import load_dotenv
    HAVE_DOTENV = True
except ImportError:
    HAVE_DOTENV = False

try:
    import paho.mqtt.client as mqtt
    HAVE_MQTT = True
except ImportError:
    HAVE_MQTT = False

try:
    import icalendar
    HAVE_ICAL = True
except ImportError:
    HAVE_ICAL = False

try:
    from sklearn.neighbors import NearestNeighbors
    HAVE_SKLEARN = True
except ImportError:
    HAVE_SKLEARN = False

# Error-Tracker importieren (für Dashboard-Anzeige)
try:
    from holo_error_tracker import get_error_tracker
    HAVE_ERROR_TRACKER = True
except ImportError:
    get_error_tracker = None
    HAVE_ERROR_TRACKER = False

# RAM-Manager importieren (für Dashboard-Anzeige)
try:
    from holo_ram_manager import get_ram_manager
    HAVE_RAM_MANAGER = True
except ImportError:
    get_ram_manager = None
    HAVE_RAM_MANAGER = False

# Zentrale Konfiguration
try:
    from holo_config import get_config
    HAVE_HOLO_CONFIG = True
except ImportError:
    get_config = lambda path, default=None: default
    HAVE_HOLO_CONFIG = False

# Dashboard-Modul importieren (ausgelagert für bessere Code-Organisation)
try:
    from holo_dashboard import DASHBOARD_HTML, DashboardCache, dashboard_cache
    HAVE_DASHBOARD_MODULE = True
except ImportError:
    HAVE_DASHBOARD_MODULE = False
    DASHBOARD_HTML = "<html><body><h1>Dashboard Module not found</h1></body></html>"
    dashboard_cache = None

try:
    from sentence_transformers import SentenceTransformer
    HAVE_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAVE_SENTENCE_TRANSFORMERS = False


@dataclass
class ExternalStateSnapshot:
    cpu_load: float
    cpu_temp: float
    mem_used: float
    disk_io: float
    net_io: float
    ha_entities: Dict[str, float]
    timestamp: float


# =============================================================================
# LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("pi-control")


# =============================================================================
# UNIVERSAL Q-LEARNING SYSTEM - Für ALLE Aktionen
# =============================================================================

class UniversalAction(Enum):
    """ALLE möglichen Aktionen im System"""
    # NAS Aktionen
    NAS_WAKE = "nas_wake"
    NAS_SLEEP = "nas_sleep"
    NAS_KEEP_ONLINE = "nas_keep_online"
    NAS_KEEP_OFFLINE = "nas_keep_offline"

    # Home Assistant Aktionen
    HA_HEATING_HIGH = "ha_heating_high"        # 21°C
    HA_HEATING_MEDIUM = "ha_heating_medium"    # 19°C
    HA_HEATING_LOW = "ha_heating_low"          # 18°C
    HA_HEATING_OFF = "ha_heating_off"          # Aus
    HA_LIGHT_ON = "ha_light_on"
    HA_LIGHT_OFF = "ha_light_off"
    HA_LIGHT_DIM = "ha_light_dim"              # 50%

    # Governor Aktionen
    GOV_PERFORMANCE = "gov_performance"
    GOV_ONDEMAND = "gov_ondemand"
    GOV_POWERSAVE = "gov_ondemand"
    GOV_CONSERVATIVE = "gov_conservative"

    # MQTT Aktionen (falls aktiviert)
    MQTT_NOTIFY = "mqtt_notify"
    MQTT_LOG = "mqtt_log"

    # Meta-Aktionen
    DO_NOTHING = "do_nothing"
    WAIT_AND_SEE = "wait_and_see"

class AbsenceCategory(Enum):
    """Kategorien für Abwesenheiten"""
    MICRO = "micro"          # < 15min (Müll, Post holen) - wird ignoriert
    SHORT_TRIP = "short"     # 15-90min (Einkaufen, Spaziergang)
    WORK = "work"            # > 90min (Arbeit, längere Termine)
    UNKNOWN = "unknown"


class DayMode(Enum):
    """Erkannter Tages-Modus"""
    UNKNOWN = "unknown"
    WORK_DAY = "work_day"           # Normaler Arbeitstag
    FREE_DAY = "free_day"           # Frei/Urlaub erkannt
    WEEKEND = "weekend"             # Wochenende
    HOME_OFFICE = "home_office"     # Zuhause aber arbeitet (PC an)


@dataclass
class AbsenceEvent:
    """Ein einzelnes Abwesenheitsereignis"""
    departure_time: str  # ISO format
    return_time: Optional[str] = None
    weekday: int = 0
    week_number: int = 0
    year: int = 2024
    duration_minutes: Optional[float] = None
    departure_hour: float = 0.0
    return_hour: Optional[float] = None
    category: str = "unknown"  # micro, short, work
    day_mode: str = "unknown"  # work_day, free_day, weekend

    @classmethod
    def create(cls, departure: datetime, day_mode: str = "unknown") -> 'AbsenceEvent':
        return cls(
            departure_time=departure.isoformat(),
            weekday=departure.weekday(),
            week_number=departure.isocalendar()[1],
            year=departure.year,
            departure_hour=departure.hour + departure.minute / 60,
            day_mode=day_mode
        )

    def finalize(self, return_time: datetime):
        """Abschluss des Events mit Kategorisierung"""
        self.return_time = return_time.isoformat()
        self.return_hour = return_time.hour + return_time.minute / 60
        dep = datetime.fromisoformat(self.departure_time)
        self.duration_minutes = (return_time - dep).total_seconds() / 60

        # Kategorisierung basierend auf Dauer
        if self.duration_minutes < 15:
            self.category = AbsenceCategory.MICRO.value
        elif self.duration_minutes < 90:
            self.category = AbsenceCategory.SHORT_TRIP.value
        else:
            self.category = AbsenceCategory.WORK.value


@dataclass
class DayProfile:
    """Profil für einen Tag - trackt Anwesenheit"""
    date: str  # YYYY-MM-DD
    weekday: int
    first_seen_home: Optional[str] = None  # Erste Aktivität
    total_home_minutes: float = 0.0
    total_away_minutes: float = 0.0
    absence_count: int = 0
    detected_mode: str = "unknown"
    mode_confidence: float = 0.0
    pc_active_minutes: float = 0.0  # Für Home-Office Erkennung

@dataclass
class UniversalState:
    """
    Universeller Zustand für Q-Learning.
    Beschreibt die komplette System-Situation.
    """
    # Zeit
    hour: int
    weekday: int
    is_weekend: bool

    # NAS Status
    nas_online: bool
    nas_idle_minutes: float
    nas_connections: int

    # Devices
    pc_online: bool
    tv_online: bool
    phone_online: bool
    tablet_online: bool

    # Home Assistant
    person_home: bool
    room_temperature: float  # Aktuell
    target_temperature: float  # Gewünscht
    lights_on: int  # Anzahl Lichter an

    # System
    cpu_temp: float
    cpu_usage: float
    governor: str
    cpu_load_duration: int

    # Predictions
    nas_usage_probability: float
    person_home_probability: float

    def to_index(self) -> int:
        """
        Konvertiert zu diskretem State-Index.
        Reduziert Dimensionalität durch Bucketing.
        """
        # 1. Diskretisierung (Werte berechnen)
        hour_bucket = self.hour // 6
        weekday_bucket = 0 if self.is_weekend else 1

        nas_online_bit = 1 if self.nas_online else 0
        nas_idle_bucket = min(4, int(self.nas_idle_minutes / 15))
        nas_conn_bucket = min(3, self.nas_connections)

        devices_online = sum([self.pc_online, self.tv_online, self.phone_online, self.tablet_online])
        device_bucket = min(4, devices_online)

        person_bit = 1 if self.person_home else 0
        temp_diff = self.target_temperature - self.room_temperature
        if temp_diff > 2: temp_bucket = 1
        elif temp_diff < -2: temp_bucket = 2
        else: temp_bucket = 0

        temp_bucket_cpu = min(3, int(self.cpu_temp / 20))
        usage_bucket = min(3, int(self.cpu_usage / 33))

        # NEU: Duration Bucket
        if self.cpu_load_duration < 10: duration_bucket = 0
        elif self.cpu_load_duration < 30: duration_bucket = 1
        else: duration_bucket = 2

        gov_map = {"performance": 0, "ondemand": 1, "powersave": 2, "conservative": 3}
        gov_bucket = gov_map.get(self.governor, 1)

        nas_prob_bucket = int(self.nas_usage_probability * 4)
        home_prob_bucket = int(self.person_home_probability * 4)

        # 2. Index Berechnung (Dynamisch & Fehlerfrei)
        # Liste aller (Wert, Maximale_Anzahl_Zustände)
        # WICHTIG: duration_bucket ist jetzt dabei (mit max 3 Zuständen)
        factors = [
            (hour_bucket, 4),
            (weekday_bucket, 2),
            (nas_online_bit, 2),
            (nas_idle_bucket, 5),
            (nas_conn_bucket, 4),
            (device_bucket, 5),
            (person_bit, 2),
            (temp_bucket, 3),
            (temp_bucket_cpu, 4),
            (usage_bucket, 4),
            (duration_bucket, 3),
            (gov_bucket, 4),
            (nas_prob_bucket, 5),
            (home_prob_bucket, 5)
        ]

        index = 0
        multiplier = 1

        # Rückwärts iterieren und aufsummieren (Stellenwertsystem)
        for val, size in reversed(factors):
            index += val * multiplier
            multiplier *= size

        STATE_SPACE_LIMIT = 1_000_000
        return index % STATE_SPACE_LIMIT

    @staticmethod
    def state_space_size() -> int:
        """Geschätzte State Space Größe"""
        return 1000000  # 1M States (managed durch Modulo)

    def to_features(self) -> Dict[str, float]:
        """Konvertiert zu Feature-Dict für Meta-Learning"""
        return {
            "hour": self.hour,
            "is_weekend": float(self.is_weekend),
            "nas_online": float(self.nas_online),
            "nas_idle": self.nas_idle_minutes,
            "devices_online": sum([self.pc_online, self.tv_online,
                                  self.phone_online, self.tablet_online]),
            "person_home": float(self.person_home),
            "temp_diff": self.target_temperature - self.room_temperature,
            "cpu_temp": self.cpu_temp,
            "cpu_usage": self.cpu_usage,
            "cpu_load_duration": self.cpu_load_duration,
            "nas_prob": self.nas_usage_probability,
            "home_prob": self.person_home_probability,
        }


class UniversalQLearner:
    """
    Universal Q-Learning System für ALLE Aktionen.

    Lernt:
    - Wann welche Aktion optimal ist
    - Welche Aktionen zu guten Outcomes führen
    - Welche Kombinationen funktionieren
    - Langfristige Rewards (nicht nur sofortige)

    Reward-System:
    - Positive Rewards für erfolgreiche Aktionen
    - Negative Rewards für Fehler/Verschwendung
    - Bonus für vorausschauende Aktionen
    - Strafe für reaktive Notfall-Aktionen
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.state_file = data_dir / "universal_qlearning.json"

        # Q-Table: State -> Action -> Q-Value
        self.q_table: Dict[int, Dict[str, float]] = defaultdict(
            lambda: {action.value: 0.5 for action in UniversalAction}
        )

        # Hyperparameter
        self.learning_rate = 0.1
        self.discount_factor = 0.95  # Gamma
        self.epsilon = 0.2  # Exploration Rate
        self.epsilon_decay = 0.9995
        self.epsilon_min = 0.05

        # Experience Replay Buffer
        self.experience_buffer: deque = deque(maxlen=10000)

        # Action Tracking
        self.action_outcomes = defaultdict(lambda: {"success": 0, "failure": 0, "total_reward": 0.0})

        # Context-Specific Learning
        self.context_q = defaultdict(lambda: defaultdict(float))  # context -> action -> q

        # Aktuelle Episode
        self.current_state: Optional[UniversalState] = None
        self.current_action: Optional[UniversalAction] = None
        self.episode_start: float = 0.0

        # Statistiken
        self.total_episodes = 0
        self.total_reward = 0.0
        self.recent_rewards = deque(maxlen=100)

        # Action Success Rates (für Dashboard)
        self.action_success_rates = defaultdict(lambda: {"successes": 0, "attempts": 0})

        self._load()
        self.lock = threading.RLock()
        logger.info("🎮 UniversalQLearner initialized")

    def select_action(self, state: UniversalState,
                     available_actions: List[UniversalAction] = None,
                     explore: bool = True) -> UniversalAction:
        """
        Wählt optimale Aktion mit Epsilon-Greedy Policy.

        Args:
            state: Aktueller Zustand
            available_actions: Welche Aktionen sind erlaubt? (None = alle)
            explore: Exploration erlauben?
        """
        with self.lock:
            state_idx = state.to_index()

            # Welche Aktionen sind verfügbar?
            if available_actions is None:
                available_actions = list(UniversalAction)

            # Exploration
            if explore and random.random() < self.epsilon:
                action = random.choice(available_actions)
                logger.debug(f"🎲 Q-Learning: Exploration → {action.value}")
            else:
                # Exploitation: Beste Aktion wählen
                q_values = self.q_table[state_idx]

                # Nur verfügbare Aktionen berücksichtigen
                available_q = {
                    action.value: q_values[action.value]
                    for action in available_actions
                }

                best_action_str = max(available_q.items(), key=lambda x: x[1])[0]
                action = UniversalAction(best_action_str)

                logger.debug(f"🎯 Q-Learning: Exploitation → {action.value} (Q={q_values[action.value]:.3f})")

            # Speichere für späteren Update
            self.current_state = state
            self.current_action = action
            self.episode_start = time.time()

            self.action_success_rates[action.value]["attempts"] += 1

            return action

    def observe_result(self, new_state: UniversalState,
                      success: bool,
                      reward_details: Dict[str, float] = None):
        """
        Beobachtet Ergebnis und führt Q-Update durch.

        Args:
            new_state: Neuer Zustand nach Aktion
            success: War die Aktion erfolgreich?
            reward_details: Detaillierte Reward-Komponenten
        """
        with self.lock:
            if self.current_state is None or self.current_action is None:
                return

            # Reward berechnen
            reward = self._calculate_reward(
                self.current_state,
                self.current_action,
                new_state,
                success,
                reward_details
            )

            # Experience speichern
            experience = {
                "state": self.current_state.to_index(),
                "action": self.current_action.value,
                "reward": reward,
                "next_state": new_state.to_index(),
                "success": success,
                "timestamp": time.time(),
                "features": self.current_state.to_features(),
            }
            self.experience_buffer.append(experience)

            # Q-Update
            self._q_update(experience)

            # Action Outcome Tracking
            action_key = self.current_action.value
            if success:
                self.action_outcomes[action_key]["success"] += 1
                self.action_success_rates[action_key]["successes"] += 1
            else:
                self.action_outcomes[action_key]["failure"] += 1

            self.action_outcomes[action_key]["total_reward"] += reward

            # Statistiken
            self.total_episodes += 1
            self.total_reward += reward
            self.recent_rewards.append(reward)

            # Epsilon Decay
            self.epsilon = max(self.epsilon_min,
                              self.epsilon * self.epsilon_decay)

            # Periodisch: Experience Replay
            if self.total_episodes % 10 == 0:
                self._experience_replay(batch_size=32)

            # Log signifikante Rewards
            if abs(reward) > 0.5:
                logger.info(f"{'✅' if success else '❌'} Q-Learning: "
                          f"{self.current_action.value} → Reward: {reward:.2f}")

            # Reset
            self.current_state = None
            self.current_action = None

            # Periodisch speichern
            if self.total_episodes % 50 == 0:
                self._save_async()

    def _calculate_reward(self, state: UniversalState,
                         action: UniversalAction,
                         new_state: UniversalState,
                         success: bool,
                         reward_details: Dict[str, float] = None) -> float:
        """
        Berechnet Reward basierend auf Outcome.
        Berücksichtigt ALLE Aspekte: NAS, HA, Energie, Komfort
        """
        reward = 0.0

        # Base Success/Failure
        if success:
            reward += 1.0
        else:
            reward -= 0.5

        # NAS-spezifische Rewards
        if action in [UniversalAction.NAS_WAKE, UniversalAction.NAS_KEEP_ONLINE]:
            if new_state.nas_connections > 0:
                reward += 1.0  # NAS wird genutzt - gut!
            elif new_state.nas_idle_minutes > 5:
                reward -= 3.0  # NAS läuft unnötig - Energieverschwendung
                logger.debug("💀 Penalty: Woke up NAS for nothing (-3.0)")

        elif action in [UniversalAction.NAS_SLEEP, UniversalAction.NAS_KEEP_OFFLINE]:
            if new_state.nas_connections > 0:
                reward -= 2.0  # User will NAS aber es ist aus - schlecht!
            else:
                reward += 0.6  # Energie gespart - gut!

        # Home Assistant Heizungs-Rewards
        if action in [UniversalAction.HA_HEATING_HIGH, UniversalAction.HA_HEATING_MEDIUM]:
            temp_diff = new_state.target_temperature - new_state.room_temperature

            if abs(temp_diff) < 0.5:
                reward += 0.8  # Perfekte Temperatur!
            elif temp_diff > 2:
                reward += 0.3  # Heizt auf, richtig
            elif temp_diff < -2:
                reward -= 0.4  # Zu warm, Energieverschwendung

            # Person nicht zuhause? Strafe!
            if not new_state.person_home:
                reward -= 1.0

        elif action == UniversalAction.HA_HEATING_LOW:
            if not new_state.person_home:
                reward += 0.3  # Spart Energie wenn niemand da
            elif new_state.room_temperature < new_state.target_temperature - 2:
                reward -= 0.2  # Zu kalt für Bewohner

        # Licht-Rewards
        if action == UniversalAction.HA_LIGHT_ON:
            if new_state.person_home and state.hour in range(18, 23):
                reward += 0.3  # Abends Licht an wenn Person da - gut
            elif not new_state.person_home:
                reward -= 0.3  # Licht an ohne Person - Verschwendung

        elif action == UniversalAction.HA_LIGHT_OFF:
            if not new_state.person_home:
                reward += 0.2  # Licht aus wenn niemand da - gut
            elif new_state.person_home and state.hour in range(18, 23):
                reward -= 0.2  # Licht aus obwohl Person da und dunkel

        # Governor Rewards (Optimiert für Spikes & Anti-Flattern)
        if action == UniversalAction.GOV_PERFORMANCE:
            # Fall A: Echte, langanhaltende Last (> 15 Sekunden)
            if new_state.cpu_usage > 70 and new_state.cpu_load_duration > 15:
                reward += 1.0  # Richtig! Power wird benötigt.

            # Fall B: Kurzer Last-Spike (< 15 Sekunden) -> Strafe!
            elif new_state.cpu_usage > 70 and new_state.cpu_load_duration <= 15:
                reward -= 1.5
                logger.debug("📉 Penalty: Premature Performance switch on spike!")

            # Fall C: Temperatur zu hoch -> Strafe!
            elif new_state.cpu_temp > 70: # Pi 4 Limit beachten (60 ist oft normal)
                reward -= 1.0

            # Fall D: Keine Last -> Strafe!
            else:
                reward -= 1.5

        elif action == UniversalAction.GOV_ONDEMAND:
            reward += 0.3 # Basis-Bonus für den "sicheren Hafen"

            # Wenn ein Spike da ist (Hohe Last, aber kurz), ist Ondemand perfekt
            if new_state.cpu_usage > 60 and new_state.cpu_load_duration <= 15:
                reward += 0.8  # Super! Nerven behalten.

            # Im normalen Arbeitsbereich
            if 15 <= new_state.cpu_usage <= 70:
                reward += 0.5

            # Wenn alles kühl ist
            if new_state.cpu_temp < 55:
                reward += 0.4

        elif action == UniversalAction.GOV_POWERSAVE:
            # Nur im echten Leerlauf (<20%)
            if new_state.cpu_usage < 20:
                reward += 0.8
            elif new_state.cpu_temp < 45:
                reward += 0.6  # Bonus fürs Kühlhalten
            else:
                reward -= 1.2  # Performance-Einbuße bei Last bestrafen

        # Proaktive Actions belohnen (WICHTIG!)
        time_taken = time.time() - self.episode_start
        if time_taken < 5 and success:
            reward += 0.2  # Schnelle, proaktive Entscheidung
        elif time_taken > 60:
            reward -= 0.1  # Zu lange gewartet

        # Custom Reward Details (falls vom Caller übergeben)
        if reward_details:
            for key, value in reward_details.items():
                reward += value

        return reward

    def _q_update(self, experience: dict):
        """Q-Learning Update (Temporal Difference)"""
        state = experience["state"]
        action = experience["action"]
        reward = experience["reward"]
        next_state = experience["next_state"]

        # Aktueller Q-Wert
        current_q = self.q_table[state][action]

        # Maximaler Q-Wert im nächsten State
        max_next_q = max(self.q_table[next_state].values())

        # TD Target
        target = reward + self.discount_factor * max_next_q

        # Q-Update
        self.q_table[state][action] = current_q + self.learning_rate * (target - current_q)

    def _experience_replay(self, batch_size: int = 32):
        """Lernt aus vergangenen Erfahrungen"""
        if len(self.experience_buffer) < batch_size:
            return

        batch = random.sample(list(self.experience_buffer), batch_size)
        for exp in batch:
            self._q_update(exp)

    def get_action_rankings(self, state: UniversalState,
                           available_actions: List[UniversalAction] = None) -> List[Tuple[UniversalAction, float]]:
        """
        Gibt Ranking aller Aktionen für einen State.
        Nützlich für Erklärbarkeit und Dashboard.
        """
        with self.lock:
            state_idx = state.to_index()
            q_values = self.q_table[state_idx]

            if available_actions is None:
                available_actions = list(UniversalAction)

            rankings = [
                (action, q_values[action.value])
                for action in available_actions
            ]

            return sorted(rankings, key=lambda x: x[1], reverse=True)

    def get_action_statistics(self) -> Dict[str, Any]:
        """
        Statistiken über Action-Performance.
        Zeigt welche Aktionen gut/schlecht funktionieren.
        """
        with self.lock:
            stats = {}

            for action_str, outcomes in self.action_outcomes.items():
                total = outcomes["success"] + outcomes["failure"]
                if total == 0:
                    continue

                stats[action_str] = {
                    "success_rate": outcomes["success"] / total,
                    "attempts": total,
                    "avg_reward": outcomes["total_reward"] / total,
                    "success": outcomes["success"],
                    "failure": outcomes["failure"],
                }

            # Sortiere nach Success Rate
            sorted_stats = dict(sorted(
                stats.items(),
                key=lambda x: x[1]["success_rate"],
                reverse=True
            ))

            return sorted_stats

    def get_best_actions_for_context(self, context_features: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Findet beste Aktionen für einen bestimmten Kontext.
        Z.B. "Was ist die beste Aktion abends wenn Person zuhause?"
        """
        # Vereinfachter Context-Lookup
        context_key = f"{context_features.get('hour', 0)//6}_{int(context_features.get('person_home', False))}"

        if context_key in self.context_q:
            actions = list(self.context_q[context_key].items())
            return sorted(actions, key=lambda x: x[1], reverse=True)[:5]

        return []

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken für Dashboard"""
        with self.lock:
            action_stats = self.get_action_statistics()

            return {
                "total_episodes": self.total_episodes,
                "total_reward": self.total_reward,
                "avg_recent_reward": statistics.mean(self.recent_rewards) if self.recent_rewards else 0,
                "epsilon": self.epsilon,
                "states_explored": len(self.q_table),
                "experience_buffer_size": len(self.experience_buffer),
                "action_statistics": action_stats,
                "best_actions": list(action_stats.items())[:5] if action_stats else [],
                "worst_actions": list(action_stats.items())[-5:] if action_stats else [],
            }

    def _save_async(self):
        threading.Thread(target=self._save, daemon=True).start()

    def _save(self):
        data = {
            "q_table": {str(k): v for k, v in self.q_table.items()},
            "epsilon": self.epsilon,
            "total_episodes": self.total_episodes,
            "total_reward": self.total_reward,
            "action_outcomes": dict(self.action_outcomes),
            "action_success_rates": dict(self.action_success_rates),
        }
        tmp = str(self.state_file) + ".tmp"
        with open(tmp, 'w') as f:
            json.dump(data, f)
        os.rename(tmp, self.state_file)

    def _load(self):
        if not self.state_file.exists():
            return
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)

            # Q-Table laden
            for k, v in data.get("q_table", {}).items():
                self.q_table[int(k)] = v

            self.epsilon = data.get("epsilon", 0.2)
            self.total_episodes = data.get("total_episodes", 0)
            self.total_reward = data.get("total_reward", 0.0)

            for k, v in data.get("action_outcomes", {}).items():
                self.action_outcomes[k] = v

            for k, v in data.get("action_success_rates", {}).items():
                self.action_success_rates[k] = v

            logger.info(f"📚 Loaded UniversalQLearner: {self.total_episodes} episodes, "
                       f"{len(self.q_table)} states")
        except Exception as e:
            logger.error(f"Failed to load UniversalQLearner: {e}")


class GovernorAI:
    def __init__(self, data_dir: Path):
        self.file_path = data_dir / "governor_ai_qtable.json"
        self.q_table = {} # State -> {Action -> Value}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.2 # 20% Experimentierfreudigkeit (sinkend)
        self._last_load_category = None

        # Mapping für diskrete Zustände
        self.actions = ["powersave", "ondemand", "performance"]
        self._load()

    def get_state_key(self, load, duration_sec):
        """
        State bucketing with hysteresis to prevent flapping at boundaries.
        """
        # Load categories with hysteresis bands
        # Hysteresis: need to cross by 5% to change category
        hysteresis = 5

        if self._last_load_category == "idle":
            if load < 15:  # Stay idle until 15%
                l_cat = "idle"
            elif load < 35:
                l_cat = "light"
            else:
                l_cat = "medium" if load < 75 else ("heavy" if load < 95 else "crit")
        elif self._last_load_category == "light":
            if load < 5:  # Drop to idle only below 5%
                l_cat = "idle"
            elif load < 35:
                l_cat = "light"
            else:
                l_cat = "medium" if load < 75 else ("heavy" if load < 95 else "crit")
        elif self._last_load_category == "medium":
            if load < 25:  # Drop to light only below 25%
                l_cat = "light" if load >= 5 else "idle"
            elif load < 75:
                l_cat = "medium"
            else:
                l_cat = "heavy" if load < 95 else "crit"
        else:
            # Default (first run or unknown)
            if load < 10: l_cat = "idle"
            elif load < 30: l_cat = "light"
            elif load < 70: l_cat = "medium"
            elif load < 90: l_cat = "heavy"
            else: l_cat = "crit"

        self._last_load_category = l_cat

        # Duration categories (no change needed)
        if duration_sec < 5: d_cat = "spike"
        elif duration_sec < 30: d_cat = "short"
        else: d_cat = "long"

        return f"{l_cat}_{d_cat}"

    def choose_action(self, load, duration_sec):
        state = self.get_state_key(load, duration_sec)

        # Init State if unknown
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}

        # Exploration (Zufall) vs Exploitation (Wissen)
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            # Wähle Aktion mit höchstem Q-Wert
            return max(self.q_table[state], key=self.q_table[state].get)

    def learn(self, old_state_key, action, reward, new_load, new_duration):
        """Der Kern des Lernens: Q-Learning Update"""
        new_state = self.get_state_key(new_load, new_duration)

        if new_state not in self.q_table:
            self.q_table[new_state] = {a: 0.0 for a in self.actions}

        # Q-Learning Formel
        old_value = self.q_table[old_state_key][action]
        next_max = max(self.q_table[new_state].values())

        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[old_state_key][action] = new_value

        # Optional: Epsilon decay (KI wird mit der Zeit selbstsicherer)
        if self.epsilon > 0.05:
            self.epsilon *= 0.999

    def calculate_reward(self, action, load, throughput_mb, duration_sec=0):
        """
        Reward function with duration awareness to prevent flapping.
        """
        reward = 0.0

        # 1. FLAPPING PREVENTION (Most Important!)
        # Penalize performance switches on spikes (< 10 sec)
        if action == "performance" and load > 50 and duration_sec < 10:
            reward -= 4.0  # Heavy penalty for spike-switching

        # Reward patience - waiting for sustained load
        if action == "performance" and load > 50 and duration_sec >= 15:
            reward += 2.0  # Good! You waited for sustained load

        # 2. PERFORMANCE PROTECTION
        if load > 50 and action == "powersave":
            reward -= 5.0
        elif load > 80 and action == "ondemand":
            reward -= 2.0

        # 3. ENERGY EFFICIENCY
        if load < 15 and action == "performance":
            reward -= 3.0
        elif load < 15 and action == "ondemand":
            reward -= 0.5

        # 4. IDEAL STATE REWARDS
        if load < 15 and action == "powersave":
            reward += 2.0
        elif load > 80 and duration_sec >= 15 and action == "performance":
            reward += 3.0  # Only reward if sustained!
        elif (15 <= load <= 80) and action == "ondemand":
            reward += 1.5  # Ondemand is the safe choice

        # 5. THROUGHPUT BONUS
        if throughput_mb > 5.0 and action != "performance":
            reward -= 5.0

        return reward

    def save(self):
        try:
            with open(str(self.file_path), 'w') as f:
                json.dump(self.q_table, f)
        except Exception as e:
            logger.warning(f"[LightAI] Failed to save Q-table: {e}")

    def _load(self):
        try:
            with open(str(self.file_path), 'r') as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            pass  # Expected on first run
        except Exception as e:
            logger.warning(f"[LightAI] Failed to load Q-table: {e}")

class NasAI:
    def __init__(self, data_dir: Path):
        self.file_path = data_dir / "nas_ai_qtable.json"
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1

        # Aktionen: Warten oder Schlafen legen
        self.actions = ["wait", "sleep"]
        self._load()

    def get_state_key(self, hour, day_of_week, idle_minutes):
        """
        Der Zustand setzt sich aus Zeit und Inaktivität zusammen.
        """
        # Zeit-Buckets
        if 0 <= hour < 6: t_cat = "night"
        elif 6 <= hour < 17: t_cat = "workday"
        elif 17 <= hour < 23: t_cat = "evening"
        else: t_cat = "late_night"

        # Wochenende?
        is_weekend = "we" if day_of_week >= 5 else "wd"

        # Idle-Buckets (Das ist wichtig!)
        if idle_minutes < 5: i_cat = "active"
        elif idle_minutes < 15: i_cat = "short_idle"
        elif idle_minutes < 45: i_cat = "medium_idle"
        elif idle_minutes < 120: i_cat = "long_idle"
        else: i_cat = "dead"

        return f"{t_cat}_{is_weekend}_{i_cat}"

    def choose_action(self, hour, day_of_week, idle_minutes):
        state = self.get_state_key(hour, day_of_week, idle_minutes)

        if state not in self.q_table:
            # Initialisiere: 'wait' ist am Anfang sicherer (0.0), sleep ist riskant (0.0)
            self.q_table[state] = {"wait": 0.0, "sleep": 0.0}

        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return max(self.q_table[state], key=self.q_table[state].get)

    def learn(self, state, action, reward):
        """Lernen basierend auf dem Ergebnis"""
        if state not in self.q_table:
            self.q_table[state] = {"wait": 0.0, "sleep": 0.0}

        old_value = self.q_table[state][action]
        # Bei NAS Entscheidungen gibt es keinen direkten "Next State" im Sekunden-Takt wie beim Governor.
        # Wir vereinfachen Q-Learning hier zu einfachem Reward-Updating.
        new_value = old_value + self.learning_rate * (reward - old_value)
        self.q_table[state][action] = new_value

        # Epsilon decay
        if self.epsilon > 0.05:
            self.epsilon *= 0.9995

    def save(self):
        try:
            with open(str(self.file_path), 'w') as f:
                json.dump(self.q_table, f)
        except Exception as e:
            logger.warning(f"[NasAI] Failed to save Q-table: {e}")

    def _load(self):
        try:
            with open(str(self.file_path), 'r') as f:
                self.q_table = json.load(f)
        except FileNotFoundError:
            pass  # Expected on first run
        except Exception as e:
            logger.warning(f"[NasAI] Failed to load Q-table: {e}")

# =============================================================================
# BAYESIAN LEARNING ENGINE - Echte Vorhersagen mit Unsicherheit
# =============================================================================

class BayesianDistribution:
    """Beta-Verteilung für Bayesian Updates"""
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        self.alpha = alpha
        self.beta = beta

    def update(self, success: bool, weight: float = 1.0):
        if success:
            self.alpha += weight
        else:
            self.beta += weight

    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def variance(self) -> float:
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))

    def std(self) -> float:
        return math.sqrt(self.variance())

    def confidence_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        mean = self.mean()
        std = self.std()
        z = 1.96 if confidence == 0.95 else 2.576
        return (max(0, mean - z * std), min(1, mean + z * std))

    def sample(self) -> float:
        return random.betavariate(self.alpha, self.beta)

    def to_dict(self) -> dict:
        return {"alpha": self.alpha, "beta": self.beta}

    @classmethod
    def from_dict(cls, d: dict) -> 'BayesianDistribution':
        return cls(d.get("alpha", 1.0), d.get("beta", 1.0))


class GaussianDistribution:
    """Normalverteilung für kontinuierliche Werte"""
    def __init__(self, prior_mean: float = 0.0, prior_var: float = 1.0):
        self.mean = prior_mean
        self.var = prior_var
        self.n = 0
        self._m2 = 0.0

    def update(self, value: float, learning_rate: float = None):
        self.n += 1
        if learning_rate is not None:
            self.mean = (1 - learning_rate) * self.mean + learning_rate * value
            diff = value - self.mean
            self.var = (1 - learning_rate) * self.var + learning_rate * diff * diff
        else:
            delta = value - self.mean
            self.mean += delta / self.n
            delta2 = value - self.mean
            self._m2 += delta * delta2
            self.var = self._m2 / self.n if self.n > 1 else self.var

    def std(self) -> float:
        return math.sqrt(max(0.0001, self.var))

    def to_dict(self) -> dict:
        return {"mean": self.mean, "var": self.var, "n": self.n, "_m2": self._m2}

    @classmethod
    def from_dict(cls, d: dict) -> 'GaussianDistribution':
        g = cls(d.get("mean", 0.0), d.get("var", 1.0))
        g.n = d.get("n", 0)
        g._m2 = d.get("_m2", 0.0)
        return g


@dataclass
class ContextFeatures:
    """Strukturierte Features für Kontext"""
    hour: int
    weekday: int
    is_weekend: bool
    pc_online: bool
    tv_online: bool
    phone_online: bool
    tablet_online: bool
    nas_was_used_recently: bool
    time_since_last_use: float

    def to_key(self) -> str:
        return f"{self.hour}_{self.weekday}_{int(self.pc_online)}_{int(self.tv_online)}_{int(self.phone_online)}"

    def to_vector(self) -> List[float]:
        hour_sin = math.sin(2 * math.pi * self.hour / 24)
        hour_cos = math.cos(2 * math.pi * self.hour / 24)
        day_sin = math.sin(2 * math.pi * self.weekday / 7)
        day_cos = math.cos(2 * math.pi * self.weekday / 7)

        return [
            hour_sin, hour_cos, day_sin, day_cos,
            float(self.is_weekend),
            float(self.pc_online), float(self.tv_online),
            float(self.phone_online), float(self.tablet_online),
            float(self.nas_was_used_recently),
            min(1.0, self.time_since_last_use / 120.0),
        ]


class BayesianLearningEngine:
    """
    ECHTES Bayesian Learning mit:
    - Posterior-Updates
    - Unsicherheitsquantifizierung
    - Thompson Sampling
    - Kontextuelle Bandits
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.state_file = data_dir / "bayesian_learning.json"

        self.global_prior = BayesianDistribution(alpha=2.0, beta=2.0)
        self.context_posteriors: Dict[str, BayesianDistribution] = {}
        self.hourly_usage = [BayesianDistribution(1.0, 1.0) for _ in range(24)]
        self.device_combo_posteriors: Dict[str, BayesianDistribution] = {}
        self.usage_duration = GaussianDistribution(prior_mean=30.0, prior_var=900.0)
        self.idle_before_use = GaussianDistribution(prior_mean=5.0, prior_var=25.0)

        self.recent_observations = deque(maxlen=100)
        self.exploration_bonus = 0.1
        self.prediction_history = deque(maxlen=500)
        self.calibration_buckets = defaultdict(lambda: {"correct": 0, "total": 0})

        self._load()
        self.lock = threading.RLock()
        logger.info("🧠 BayesianLearningEngine initialized")

    def observe(self, context: ContextFeatures, nas_was_used: bool,
                duration_minutes: float = None):
        """Beobachte Ereignis und update Posteriors"""
        with self.lock:
            timestamp = time.time()

            self.global_prior.update(nas_was_used)

            ctx_key = context.to_key()
            if ctx_key not in self.context_posteriors:
                self.context_posteriors[ctx_key] = BayesianDistribution(
                    alpha=self.global_prior.alpha * 0.5,
                    beta=self.global_prior.beta * 0.5
                )
            self.context_posteriors[ctx_key].update(nas_was_used)

            self.hourly_usage[context.hour].update(nas_was_used)

            combo_key = self._device_combo_key(context)
            if combo_key not in self.device_combo_posteriors:
                self.device_combo_posteriors[combo_key] = BayesianDistribution(1.5, 1.5)
            self.device_combo_posteriors[combo_key].update(nas_was_used)

            if nas_was_used and duration_minutes is not None:
                self.usage_duration.update(duration_minutes)

            if nas_was_used and context.time_since_last_use > 0:
                self.idle_before_use.update(context.time_since_last_use)

            self.recent_observations.append({
                "timestamp": timestamp,
                "context": ctx_key,
                "used": nas_was_used,
                "hour": context.hour,
                "devices": combo_key,
            })

            if len(self.recent_observations) % 20 == 0:
                self._save_async()

    def predict(self, context: ContextFeatures,
                use_thompson_sampling: bool = False) -> Dict[str, Any]:
        """Vorhersage mit Unsicherheit"""
        with self.lock:
            ctx_key = context.to_key()
            combo_key = self._device_combo_key(context)

            evidences = []

            if ctx_key in self.context_posteriors:
                ctx_post = self.context_posteriors[ctx_key]
                n_obs = ctx_post.alpha + ctx_post.beta - 2
                weight = min(1.0, n_obs / 20)
                evidences.append(("context", ctx_post, weight * 0.4))

            hour_post = self.hourly_usage[context.hour]
            evidences.append(("hourly", hour_post, 0.2))

            if combo_key in self.device_combo_posteriors:
                combo_post = self.device_combo_posteriors[combo_key]
                evidences.append(("device_combo", combo_post, 0.25))

            evidences.append(("global", self.global_prior, 0.15))

            total_weight = sum(w for _, _, w in evidences)
            probability = sum(post.mean() * w for _, post, w in evidences) / total_weight

            variances = [post.variance() * w for _, post, w in evidences]
            base_uncertainty = math.sqrt(sum(variances) / total_weight)

            means = [post.mean() for _, post, _ in evidences]
            disagreement = statistics.stdev(means) if len(means) > 1 else 0
            total_uncertainty = base_uncertainty + 0.5 * disagreement

            ci_low = max(0.0, probability - 2.0 * total_uncertainty)
            ci_high = min(1.0, probability + 2.0 * total_uncertainty)

            if use_thompson_sampling:
                samples = [post.sample() * w for _, post, w in evidences]
                sample = sum(samples) / total_weight
            else:
                sample = probability

            dominant = max(evidences, key=lambda x: x[2] * x[1].mean())[0]

            return {
                "probability": probability,
                "confidence_low": ci_low,
                "confidence_high": ci_high,
                "uncertainty": total_uncertainty,
                "sample": sample,
                "source": dominant,
                "exploration_value": total_uncertainty * self.exploration_bonus,
            }

    def get_optimal_wake_time(self) -> Dict[str, Any]:
        """Analysiert optimale Wake-Zeiten"""
        with self.lock:
            hourly_probs = [
                (hour, post.mean(), post.std())
                for hour, post in enumerate(self.hourly_usage)
            ]
            sorted_hours = sorted(hourly_probs, key=lambda x: x[1], reverse=True)

            return {
                "peak_hours": [(h, p) for h, p, _ in sorted_hours[:3]],
                "low_hours": [(h, p) for h, p, _ in sorted_hours[-3:]],
                "current_hour_prob": self.hourly_usage[datetime.now().hour].mean(),
            }

    def evaluate_prediction(self, predicted_prob: float, actual_used: bool):
        """Trackt Kalibrierung"""
        with self.lock:
            bucket = int(predicted_prob * 10)
            bucket = min(9, max(0, bucket))

            self.calibration_buckets[bucket]["total"] += 1
            if actual_used:
                self.calibration_buckets[bucket]["correct"] += 1

            self.prediction_history.append({
                "predicted": predicted_prob,
                "actual": actual_used,
                "timestamp": time.time(),
            })

    def get_calibration_report(self) -> Dict[str, Any]:
        """Kalibrierungs-Report"""
        calibration = {}
        for bucket, data in self.calibration_buckets.items():
            if data["total"] > 0:
                expected = (bucket + 0.5) / 10
                actual = data["correct"] / data["total"]
                calibration[f"{bucket*10}-{(bucket+1)*10}%"] = {
                    "expected": expected,
                    "actual": actual,
                    "error": abs(expected - actual),
                    "samples": data["total"],
                }

        total_error = sum(d["error"] * d["samples"] for d in calibration.values())
        total_samples = sum(d["samples"] for d in calibration.values())

        return {
            "buckets": calibration,
            "mean_calibration_error": total_error / total_samples if total_samples > 0 else 0,
            "total_predictions": total_samples,
        }

    def _device_combo_key(self, context: ContextFeatures) -> str:
        devices = []
        if context.pc_online: devices.append("pc")
        if context.tv_online: devices.append("tv")
        if context.phone_online: devices.append("phone")
        if context.tablet_online: devices.append("tablet")
        return "_".join(sorted(devices)) or "none"

    def _save_async(self):
        threading.Thread(target=self._save, daemon=True).start()

    def _save(self):
        data = {
            "global_prior": self.global_prior.to_dict(),
            "context_posteriors": {k: v.to_dict() for k, v in self.context_posteriors.items()},
            "hourly_usage": [p.to_dict() for p in self.hourly_usage],
            "device_combo_posteriors": {k: v.to_dict() for k, v in self.device_combo_posteriors.items()},
            "usage_duration": self.usage_duration.to_dict(),
            "idle_before_use": self.idle_before_use.to_dict(),
            "calibration_buckets": dict(self.calibration_buckets),
        }
        tmp = str(self.state_file) + ".tmp"
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2)
        os.rename(tmp, self.state_file)

    def _load(self):
        if not self.state_file.exists():
            return
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            self.global_prior = BayesianDistribution.from_dict(data.get("global_prior", {}))
            for k, v in data.get("context_posteriors", {}).items():
                self.context_posteriors[k] = BayesianDistribution.from_dict(v)
            for i, p in enumerate(data.get("hourly_usage", [])):
                if i < 24:
                    self.hourly_usage[i] = BayesianDistribution.from_dict(p)
            for k, v in data.get("device_combo_posteriors", {}).items():
                self.device_combo_posteriors[k] = BayesianDistribution.from_dict(v)
            if "usage_duration" in data:
                self.usage_duration = GaussianDistribution.from_dict(data["usage_duration"])
            if "idle_before_use" in data:
                self.idle_before_use = GaussianDistribution.from_dict(data["idle_before_use"])
            self.calibration_buckets = defaultdict(
                lambda: {"correct": 0, "total": 0},
                data.get("calibration_buckets", {})
            )
            logger.info(f"📚 Loaded Bayesian: {len(self.context_posteriors)} contexts")
        except Exception as e:
            logger.error(f"Failed to load Bayesian: {e}")

# =============================================================================
# SEMANTIC MEMORY ENGINE (RAG)
# =============================================================================

class SemanticMemoryEngine:
    """
    Semantisches Gedächtnis mit RAG (Retrieval Augmented Generation).

    Speichert Events mit Kontext und ermöglicht semantische Suche
    nach ähnlichen Situationen für bessere Entscheidungen.

    Features:
    - Event-Speicherung mit reichem Kontext
    - Semantische Ähnlichkeitssuche
    - Automatische Kategorisierung
    - Relevanz-basiertes Retrieval
    - Decay für alte Erinnerungen
    """

    def __init__(self, data_dir: Path, max_memories: int = 5000):
        self.data_dir = data_dir
        self.state_file = data_dir / "semantic_memory.json"
        self.max_memories = max_memories

        # Memory Store
        self.memories: List[Dict] = []

        # Indices für schnelle Suche
        self.category_index: Dict[str, List[int]] = defaultdict(list)
        self.hour_index: Dict[int, List[int]] = defaultdict(list)
        self.weekday_index: Dict[int, List[int]] = defaultdict(list)

        # Embedding Model (falls verfügbar)
        self.embedder = None
        self.embeddings: List[List[float]] = []
        self._init_embedder()

        # Statistics
        self.total_recalls = 0
        self.successful_retrievals = 0

        self._load()
        self.lock = threading.RLock()
        logger.info(f"🧠 SemanticMemoryEngine initialized with {len(self.memories)} memories")

    def _init_embedder(self):
        """Initialisiert Sentence Transformer wenn verfügbar"""
        try:
            if HAVE_SENTENCE_TRANSFORMERS:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("🔤 Semantic embedder loaded (all-MiniLM-L6-v2)")
        except Exception as e:
            logger.warning(f"Could not load sentence embedder: {e}")
            self.embedder = None

    def store_event(self, event_type: str, context: Dict[str, Any],
                    outcome: str, success: bool, metadata: Dict = None):
        """
        Speichert ein Event im semantischen Gedächtnis.

        Args:
            event_type: Art des Events (z.B. "nas_wake", "nas_sleep")
            context: Kontext zum Zeitpunkt des Events
            outcome: Was ist passiert
            success: War es erfolgreich/gewünscht?
            metadata: Zusätzliche Informationen
        """
        with self.lock:
            now = datetime.now()

            memory = {
                "id": len(self.memories),
                "timestamp": now.isoformat(),
                "event_type": event_type,
                "hour": now.hour,
                "weekday": now.weekday(),
                "is_weekend": now.weekday() >= 5,
                "context": context,
                "outcome": outcome,
                "success": success,
                "metadata": metadata or {},
                "recall_count": 0,
                "last_recall": None,
                "importance": 1.0,
            }

            # Text für semantische Suche
            memory["search_text"] = self._generate_search_text(memory)

            # Embedding erstellen
            if self.embedder:
                try:
                    embedding = self.embedder.encode(memory["search_text"]).tolist()
                    self.embeddings.append(embedding)
                except Exception:
                    self.embeddings.append([])

            self.memories.append(memory)

            # Indices aktualisieren
            idx = len(self.memories) - 1
            self.category_index[event_type].append(idx)
            self.hour_index[now.hour].append(idx)
            self.weekday_index[now.weekday()].append(idx)

            # Wichtigkeit für seltene Events
            if len(self.category_index[event_type]) < 10:
                memory["importance"] = 1.5

            # Memory Limit
            if len(self.memories) > self.max_memories:
                self._prune_old_memories()

            if len(self.memories) % 100 == 0:
                self._save_async()

            logger.debug(f"📝 Stored memory: {event_type} - {outcome[:50]}")

    def recall_similar(self, current_context: Dict[str, Any],
                       event_type: str = None, k: int = 5) -> List[Dict]:
        """
        Ruft ähnliche Erinnerungen basierend auf aktuellem Kontext ab.
        """
        with self.lock:
            self.total_recalls += 1

            if not self.memories:
                return []

            now = datetime.now()
            candidates = []

            # Pre-Filter nach Event-Typ
            if event_type and event_type in self.category_index:
                indices = self.category_index[event_type]
            else:
                indices = range(len(self.memories))

            for idx in indices:
                if idx >= len(self.memories):
                    continue
                memory = self.memories[idx]

                similarity = self._calculate_similarity(current_context, memory, now)

                if similarity > 0.1:
                    candidates.append({
                        "memory": memory,
                        "similarity": similarity,
                        "index": idx
                    })

            candidates.sort(key=lambda x: x["similarity"], reverse=True)

            results = []
            for c in candidates[:k]:
                memory = c["memory"]
                memory["recall_count"] += 1
                memory["last_recall"] = now.isoformat()

                results.append({
                    "event_type": memory["event_type"],
                    "context": memory["context"],
                    "outcome": memory["outcome"],
                    "success": memory["success"],
                    "similarity": c["similarity"],
                    "timestamp": memory["timestamp"],
                    "importance": memory["importance"],
                })

            if results:
                self.successful_retrievals += 1

            return results

    def recall_by_semantic_query(self, query: str, k: int = 5) -> List[Dict]:
        """Semantische Suche mit natürlichsprachlicher Query."""
        if not self.embedder or not self.embeddings:
            return []

        with self.lock:
            try:
                query_embedding = self.embedder.encode(query)

                similarities = []
                for i, emb in enumerate(self.embeddings):
                    if emb:
                        sim = self._cosine_similarity(query_embedding, emb)
                        similarities.append((i, sim))

                similarities.sort(key=lambda x: x[1], reverse=True)

                results = []
                for idx, sim in similarities[:k]:
                    memory = self.memories[idx]
                    results.append({
                        "event_type": memory["event_type"],
                        "context": memory["context"],
                        "outcome": memory["outcome"],
                        "success": memory["success"],
                        "similarity": sim,
                        "timestamp": memory["timestamp"],
                    })

                return results
            except Exception as e:
                logger.error(f"Semantic query failed: {e}")
                return []

    def get_pattern_summary(self, event_type: str = None) -> Dict[str, Any]:
        """Gibt Zusammenfassung der gelernten Muster zurück."""
        with self.lock:
            if event_type:
                relevant = [self.memories[i] for i in self.category_index.get(event_type, [])]
            else:
                relevant = self.memories

            if not relevant:
                return {"patterns": [], "total": 0}

            # Stündliche Erfolgsraten
            hourly_success = defaultdict(lambda: {"success": 0, "total": 0})
            for mem in relevant:
                hour = mem["hour"]
                hourly_success[hour]["total"] += 1
                if mem["success"]:
                    hourly_success[hour]["success"] += 1

            hour_rates = [
                (h, d["success"] / d["total"] if d["total"] > 0 else 0)
                for h, d in hourly_success.items()
            ]
            hour_rates.sort(key=lambda x: x[1], reverse=True)

            return {
                "total_memories": len(relevant),
                "success_rate": sum(1 for m in relevant if m["success"]) / len(relevant) if relevant else 0,
                "best_hours": hour_rates[:3],
                "worst_hours": hour_rates[-3:] if len(hour_rates) > 3 else [],
            }

    def _calculate_similarity(self, current: Dict, memory: Dict, now: datetime) -> float:
        """Berechnet Multi-Faktor Ähnlichkeit"""
        score = 0.0

        # 1. Zeitliche Ähnlichkeit (30%)
        hour_diff = abs(now.hour - memory["hour"])
        if hour_diff > 12:
            hour_diff = 24 - hour_diff
        time_sim = 1.0 - (hour_diff / 12.0)
        score += 0.3 * time_sim

        # 2. Wochentag (15%)
        if now.weekday() == memory["weekday"]:
            score += 0.15
        elif (now.weekday() >= 5) == memory["is_weekend"]:
            score += 0.08

        # 3. Kontext-Matching (40%)
        ctx = memory.get("context", {})
        matches = 0
        checks = 0

        for key in ["pc_online", "tv_online", "phone_online", "person_home", "nas_online"]:
            if key in current and key in ctx:
                checks += 1
                if current[key] == ctx[key]:
                    matches += 1

        if checks > 0:
            score += 0.4 * (matches / checks)

        # 4. Recency Bonus (10%)
        try:
            mem_time = datetime.fromisoformat(memory["timestamp"])
            age_days = (now - mem_time).days
            recency = max(0, 1.0 - (age_days / 90))
            score += 0.1 * recency
        except Exception:
            pass

        # 5. Importance & Recall (5%)
        importance = memory.get("importance", 1.0)
        recall_boost = min(0.5, memory.get("recall_count", 0) * 0.05)
        score += 0.05 * (importance + recall_boost)

        return min(1.0, score)

    def _cosine_similarity(self, a, b) -> float:
        """Cosine Similarity zwischen zwei Vektoren"""
        if HAVE_NUMPY:
            a = np.array(a)
            b = np.array(b)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        else:
            dot = sum(x*y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x*x for x in a))
            norm_b = math.sqrt(sum(x*x for x in b))
            return dot / (norm_a * norm_b + 1e-9)

    def _generate_search_text(self, memory: Dict) -> str:
        """Generiert durchsuchbaren Text"""
        parts = [
            f"Event: {memory['event_type']}",
            f"Outcome: {memory['outcome']}",
            f"Hour: {memory['hour']}",
            f"Weekend: {memory['is_weekend']}",
        ]

        ctx = memory.get("context", {})
        for key, value in ctx.items():
            if isinstance(value, bool):
                if value:
                    parts.append(key.replace("_", " "))
            elif isinstance(value, (int, float)):
                parts.append(f"{key}: {value}")

        return " ".join(parts)

    def _prune_old_memories(self):
        """Entfernt alte, unwichtige Erinnerungen"""
        now = datetime.now()
        scored = []

        for i, mem in enumerate(self.memories):
            try:
                mem_time = datetime.fromisoformat(mem["timestamp"])
                age_days = (now - mem_time).days
            except Exception:
                age_days = 365

            score = (
                (1.0 - age_days / 365) * 0.4 +
                mem.get("importance", 1.0) * 0.3 +
                min(1.0, mem.get("recall_count", 0) / 10) * 0.3
            )
            scored.append((i, score))

        scored.sort(key=lambda x: x[1])
        to_remove = int(len(scored) * 0.2)
        remove_indices = set(i for i, _ in scored[:to_remove])

        new_memories = []
        new_embeddings = []

        for i, mem in enumerate(self.memories):
            if i not in remove_indices:
                new_memories.append(mem)
                if i < len(self.embeddings):
                    new_embeddings.append(self.embeddings[i])

        self.memories = new_memories
        self.embeddings = new_embeddings
        self._rebuild_indices()

        logger.info(f"🗑️ Pruned {to_remove} old memories, {len(self.memories)} remaining")

    def _rebuild_indices(self):
        """Baut alle Indices neu auf"""
        self.category_index.clear()
        self.hour_index.clear()
        self.weekday_index.clear()

        for i, mem in enumerate(self.memories):
            mem["id"] = i
            self.category_index[mem["event_type"]].append(i)
            self.hour_index[mem["hour"]].append(i)
            self.weekday_index[mem["weekday"]].append(i)

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken für Dashboard"""
        return {
            "total_memories": len(self.memories),
            "categories": {k: len(v) for k, v in self.category_index.items()},
            "total_recalls": self.total_recalls,
            "successful_retrievals": self.successful_retrievals,
            "retrieval_rate": self.successful_retrievals / max(1, self.total_recalls),
            "has_embeddings": self.embedder is not None,
            "embedding_count": len([e for e in self.embeddings if e]),
        }

    def _save_async(self):
        threading.Thread(target=self._save, daemon=True).start()

    def _save(self):
        data = {
            "version": 1,
            "memories": self.memories,
            "stats": {
                "total_recalls": self.total_recalls,
                "successful_retrievals": self.successful_retrievals,
            }
        }
        try:
            tmp = str(self.state_file) + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(data, f)
            os.rename(tmp, self.state_file)

            if self.embeddings:
                emb_file = self.data_dir / "semantic_embeddings.json"
                with open(str(emb_file) + ".tmp", 'w') as f:
                    json.dump(self.embeddings, f)
                os.rename(str(emb_file) + ".tmp", emb_file)
        except Exception as e:
            logger.error(f"Failed to save semantic memory: {e}")

    def _load(self):
        if not self.state_file.exists():
            return
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)

            self.memories = data.get("memories", [])
            stats = data.get("stats", {})
            self.total_recalls = stats.get("total_recalls", 0)
            self.successful_retrievals = stats.get("successful_retrievals", 0)

            self._rebuild_indices()

            emb_file = self.data_dir / "semantic_embeddings.json"
            if emb_file.exists():
                with open(emb_file, 'r') as f:
                    self.embeddings = json.load(f)

            logger.info(f"📚 Loaded SemanticMemory: {len(self.memories)} memories")
        except Exception as e:
            logger.error(f"Failed to load semantic memory: {e}")



# =============================================================================
# ExternalContextManager
# =============================================================================


# ERSETZE die gesamte ExternalContextManager Klasse (ca. Zeile 1470-1750)

class ExternalContextManager:
    """
    Verwaltet externe Kontextquellen von Home Assistant.

    Quellen:
    - Wetter von HA (weather.forecast_home)
    - Kalender von HA (calendar.kalender)
    - Feiertage (lokal berechnet)
    - Sonnenauf-/untergang (von HA oder berechnet)
    """

    def __init__(self, data_dir: Path, config: Dict = None):
        self.data_dir = data_dir
        self.cache_file = data_dir / "external_context_cache.json"
        self.config = config or {}

        # Home Assistant Konfiguration - aus CONFIG übernehmen
        self.ha_url = CONFIG.get("home_assistant", {}).get("api_url", "").rstrip("/")
        self.ha_token = CONFIG.get("home_assistant", {}).get("api_token", "")

        # Entity IDs
        self.weather_entity = self.config.get("weather_entity", "weather.forecast_home")
        self.calendar_entity = self.config.get("calendar_entity", "calendar.kalender")
        self.sun_entity = "sun.sun"  # Standard HA Entity

        # Location (für Feiertage, Fallback Sonnenzeiten)
        self.location = self.config.get("location", {"lat": 51.4556, "lon": 7.0116})

        # Cache
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = {
            "weather": 600,       # 10 Minuten
            "forecast": 1800,     # 30 Minuten
            "calendar": 300,      # 5 Minuten
            "holidays": 86400,    # 24 Stunden
            "sun_times": 3600,    # 1 Stunde
        }
        self.cache_timestamps: Dict[str, float] = {}

        # Deutsche Feiertage (NRW)
        self.holidays_2024 = self._load_german_holidays(2024)
        self.holidays_2025 = self._load_german_holidays(2025)

        self._load_cache()
        self.lock = threading.RLock()  # ✅ FIX: Lock hinzugefügt
        self._start_background_updates()
        logger.info(f"🌍 ExternalContextManager initialized")

    def _ha_get_state(self, entity_id: str) -> Optional[Dict]:
        """Holt State einer Entity von Home Assistant"""
        if not self.ha_url or not self.ha_token:
            return None

        if not HAVE_REQUESTS:
            return None

        try:
            url = f"{self.ha_url}/states/{entity_id}"
            headers = {
                "Authorization": f"Bearer {self.ha_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.warning(f"HA API error for {entity_id}: {e}")
            return None

    def _ha_get_calendar_events(self, entity_id: str, hours_ahead: int = 24) -> List[Dict]:
        """Holt Kalender-Events von Home Assistant"""
        if not self.ha_url or not self.ha_token:
            return []

        if not HAVE_REQUESTS:
            return []

        try:
            now = datetime.now()
            start = now.isoformat()
            end = (now + timedelta(hours=hours_ahead)).isoformat()

            url = f"{self.ha_url}/calendars/{entity_id}?start={start}&end={end}"
            headers = {
                "Authorization": f"Bearer {self.ha_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.warning(f"HA Calendar API error: {e}")
            return []

    def get_current_context(self) -> Dict[str, Any]:
        """Holt aktuellen Kontext aus allen Quellen"""
        with self.lock:
            now = datetime.now()

            # ✅ FIX: Presence aus globalem state holen
            state_snapshot = state.snapshot()
            ha_presence = state_snapshot.get("ha_presence", {})
            person_home = ha_presence.get("anyone_home", False)

            context = {
                "timestamp": now.isoformat(),
                "weather": self._get_cached_or_fetch("weather", self._fetch_weather_ha),
                "forecast": self._get_cached_or_fetch("forecast", self._fetch_forecast_ha),
                "calendar": self._get_cached_or_fetch("calendar", self._fetch_calendar_ha),
                "holiday": self._get_holiday_info(now),
                "sun_times": self._get_cached_or_fetch("sun_times", self._fetch_sun_times_ha),
                "time_context": self._get_time_context(now),
                "presence": {
                    "anyone_home": person_home,
                    "persons": ha_presence.get("persons", {}),
                },
            }

            context["derived"] = self._derive_insights(context)
            return context

    def get_weather(self) -> Dict[str, Any]:
        """Gibt aktuelle Wetterdaten zurück"""
        return self._get_cached_or_fetch("weather", self._fetch_weather_ha)

    def get_forecast(self, hours: int = 24) -> List[Dict]:
        """Gibt Wettervorhersage zurück"""
        forecast = self._get_cached_or_fetch("forecast", self._fetch_forecast_ha)
        if isinstance(forecast, list):
            return forecast[:hours // 3]
        return []

    def get_calendar_events(self, hours_ahead: int = 24) -> List[Dict]:
        """Gibt kommende Kalender-Events zurück"""
        return self._get_cached_or_fetch("calendar", self._fetch_calendar_ha)

    def is_holiday(self, date: datetime = None) -> Tuple[bool, Optional[str]]:
        """Prüft ob ein Tag ein Feiertag ist"""
        date = date or datetime.now()
        info = self._get_holiday_info(date)
        return info["is_holiday"], info.get("name")

    def is_daylight(self) -> bool:
        """Prüft ob es gerade hell ist"""
        sun = self._get_cached_or_fetch("sun_times", self._fetch_sun_times_ha)
        if not sun or "error" in sun:
            return 6 <= datetime.now().hour < 20

        now = datetime.now().time()
        try:
            sunrise = datetime.strptime(sun["sunrise"], "%H:%M").time()
            sunset = datetime.strptime(sun["sunset"], "%H:%M").time()
            return sunrise <= now <= sunset
        except Exception:
            return 6 <= datetime.now().hour < 20

    def _get_cached_or_fetch(self, key: str, fetch_func: Callable) -> Any:
        """Cache-Logic mit TTL"""
        now = time.time()

        if key in self.cache:
            age = now - self.cache_timestamps.get(key, 0)
            if age < self.cache_ttl.get(key, 3600):
                return self.cache[key]

        try:
            data = fetch_func()
            if data:
                self.cache[key] = data
                self.cache_timestamps[key] = now
                self._save_cache_async()
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch {key}: {e}")
            return self.cache.get(key, {})

    def _fetch_weather_ha(self) -> Dict[str, Any]:
        """Holt Wetterdaten von Home Assistant"""
        ha_state = self._ha_get_state(self.weather_entity)

        if not ha_state:
            return self._get_fallback_weather()

        try:
            attrs = ha_state.get("attributes", {})

            return {
                "temp": attrs.get("temperature"),
                "feels_like": attrs.get("temperature"),
                "humidity": attrs.get("humidity"),
                "pressure": attrs.get("pressure"),
                "description": ha_state.get("state", "unknown"),
                "wind_speed": attrs.get("wind_speed"),
                "wind_bearing": attrs.get("wind_bearing"),
                "visibility": attrs.get("visibility"),
                "source": "home_assistant",
                "entity": self.weather_entity,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error parsing HA weather: {e}")
            return self._get_fallback_weather()

    def _fetch_forecast_ha(self) -> List[Dict]:
        """Holt Wettervorhersage von Home Assistant"""
        ha_state = self._ha_get_state(self.weather_entity)

        if not ha_state:
            return []

        try:
            attrs = ha_state.get("attributes", {})
            forecast_data = attrs.get("forecast", [])

            forecast = []
            for item in forecast_data[:16]:
                forecast.append({
                    "datetime": item.get("datetime"),
                    "temp": item.get("temperature"),
                    "temp_low": item.get("templow"),
                    "description": item.get("condition"),
                    "precipitation": item.get("precipitation"),
                    "precipitation_probability": item.get("precipitation_probability"),
                    "wind_speed": item.get("wind_speed"),
                })

            return forecast
        except Exception as e:
            logger.error(f"Error parsing HA forecast: {e}")
            return []

    def _fetch_calendar_ha(self) -> List[Dict]:
        """Holt Kalender-Events von Home Assistant"""
        events = self._ha_get_calendar_events(self.calendar_entity, hours_ahead=48)

        if not events:
            return []

        try:
            result = []
            for event in events[:20]:
                result.append({
                    "summary": event.get("summary", ""),
                    "start": event.get("start", {}).get("dateTime") or event.get("start", {}).get("date"),
                    "end": event.get("end", {}).get("dateTime") or event.get("end", {}).get("date"),
                    "location": event.get("location", ""),
                    "description": event.get("description", ""),
                    "source": "home_assistant",
                })

            result.sort(key=lambda x: x.get("start", ""))
            return result

        except Exception as e:
            logger.error(f"Error parsing HA calendar: {e}")
            return []

    def _fetch_sun_times_ha(self) -> Dict[str, str]:
        """Holt Sonnenauf-/untergang von Home Assistant"""
        ha_state = self._ha_get_state(self.sun_entity)

        if not ha_state:
            return self._calculate_sun_times()

        try:
            attrs = ha_state.get("attributes", {})

            next_rising = attrs.get("next_rising", "")
            next_setting = attrs.get("next_setting", "")

            sunrise = ""
            sunset = ""

            if next_rising:
                sunrise_dt = datetime.fromisoformat(next_rising.replace("Z", "+00:00"))
                sunrise = sunrise_dt.strftime("%H:%M")

            if next_setting:
                sunset_dt = datetime.fromisoformat(next_setting.replace("Z", "+00:00"))
                sunset = sunset_dt.strftime("%H:%M")

            return {
                "sunrise": sunrise,
                "sunset": sunset,
                "state": ha_state.get("state"),
                "elevation": attrs.get("elevation"),
                "source": "home_assistant",
            }
        except Exception as e:
            logger.warning(f"Error parsing HA sun: {e}, using calculation")
            return self._calculate_sun_times()

    def _get_holiday_info(self, date: datetime) -> Dict[str, Any]:
        """Prüft Feiertage für ein Datum"""
        date_str = date.strftime("%Y-%m-%d")
        year = date.year

        holidays = self.holidays_2024 if year == 2024 else self.holidays_2025

        if date_str in holidays:
            return {
                "is_holiday": True,
                "name": holidays[date_str],
                "type": "public_holiday"
            }

        if date.weekday() >= 5:
            return {
                "is_holiday": False,
                "is_weekend": True,
                "name": "Wochenende"
            }

        return {"is_holiday": False, "is_weekend": False, "name": None}

    def _load_german_holidays(self, year: int = 2024) -> Dict[str, str]:
        """Deutsche Feiertage für NRW"""
        holidays = {
            f"{year}-01-01": "Neujahr",
            f"{year}-05-01": "Tag der Arbeit",
            f"{year}-10-03": "Tag der Deutschen Einheit",
            f"{year}-11-01": "Allerheiligen",
            f"{year}-12-25": "1. Weihnachtsfeiertag",
            f"{year}-12-26": "2. Weihnachtsfeiertag",
        }

        easter = self._calculate_easter(year)

        holidays[self._date_str(easter - timedelta(days=2))] = "Karfreitag"
        holidays[self._date_str(easter)] = "Ostersonntag"
        holidays[self._date_str(easter + timedelta(days=1))] = "Ostermontag"
        holidays[self._date_str(easter + timedelta(days=39))] = "Christi Himmelfahrt"
        holidays[self._date_str(easter + timedelta(days=49))] = "Pfingstsonntag"
        holidays[self._date_str(easter + timedelta(days=50))] = "Pfingstmontag"
        holidays[self._date_str(easter + timedelta(days=60))] = "Fronleichnam"

        return holidays

    def _calculate_easter(self, year: int) -> datetime:
        """Berechnet Ostersonntag (Gauss-Algorithmus)"""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return datetime(year, month, day)

    def _date_str(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    def _calculate_sun_times(self) -> Dict[str, str]:
        """Fallback: Berechnet Sonnenauf- und untergang"""
        now = datetime.now()
        lat = self.location["lat"]
        lon = self.location["lon"]

        day_of_year = now.timetuple().tm_yday
        declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))

        lat_rad = math.radians(lat)
        decl_rad = math.radians(declination)

        cos_hour_angle = -math.tan(lat_rad) * math.tan(decl_rad)
        cos_hour_angle = max(-1, min(1, cos_hour_angle))

        hour_angle = math.degrees(math.acos(cos_hour_angle))

        sunrise_hour = 12 - (hour_angle / 15) - (lon / 15) + 1
        sunset_hour = 12 + (hour_angle / 15) - (lon / 15) + 1

        sunrise = f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}"
        sunset = f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}"

        return {
            "sunrise": sunrise,
            "sunset": sunset,
            "source": "calculated",
        }

    def _get_time_context(self, now: datetime) -> Dict[str, Any]:
        """Zeitbasierter Kontext"""
        hour = now.hour

        if 5 <= hour < 10:
            period = "morning"
        elif 10 <= hour < 14:
            period = "midday"
        elif 14 <= hour < 18:
            period = "afternoon"
        elif 18 <= hour < 22:
            period = "evening"
        else:
            period = "night"

        return {
            "hour": hour,
            "minute": now.minute,
            "weekday": now.weekday(),
            "weekday_name": ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                            "Freitag", "Samstag", "Sonntag"][now.weekday()],
            "is_weekend": now.weekday() >= 5,
            "period": period,
            "week_number": now.isocalendar()[1],
        }

    def _derive_insights(self, context: Dict) -> Dict[str, Any]:
        """Leitet Insights aus dem Kontext ab"""
        insights = {}

        weather = context.get("weather", {})
        if weather and weather.get("temp") is not None:
            temp = weather.get("temp", 20)
            insights["heating_recommendation"] = "high" if temp < 5 else "medium" if temp < 15 else "low"
            insights["outdoor_activity_likely"] = temp >= 10

        calendar = context.get("calendar", [])
        if calendar:
            next_event = calendar[0] if calendar else None
            if next_event and next_event.get("start"):
                try:
                    start_str = next_event["start"]
                    if "T" in start_str:
                        event_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    else:
                        event_time = datetime.strptime(start_str, "%Y-%m-%d")

                    minutes_until = (event_time - datetime.now()).total_seconds() / 60
                    insights["next_event"] = next_event.get("summary", "")
                    insights["next_event_in_minutes"] = int(minutes_until)
                    insights["might_leave_soon"] = 0 < minutes_until < 60
                except Exception as e:
                    logger.debug(f"Could not parse calendar event time: {e}")

        holiday = context.get("holiday", {})
        insights["is_free_day"] = holiday.get("is_holiday", False) or holiday.get("is_weekend", False)

        sun = context.get("sun_times", {})
        if sun.get("state"):
            insights["is_dark_outside"] = sun.get("state") == "below_horizon"
        else:
            insights["is_dark_outside"] = not self.is_daylight()

        return insights

    def _get_fallback_weather(self) -> Dict[str, Any]:
        """Fallback Wetterdaten"""
        now = datetime.now()
        month_temps = {1: 2, 2: 3, 3: 7, 4: 11, 5: 15, 6: 18,
                       7: 20, 8: 20, 9: 16, 10: 11, 11: 6, 12: 3}

        return {
            "temp": month_temps.get(now.month, 15),
            "humidity": 70,
            "description": "keine Daten",
            "is_fallback": True,
            "source": "fallback",
            "timestamp": now.isoformat(),
        }

    def _start_background_updates(self):
        """Background-Thread für Updates"""
        def update_loop():
            while True:
                time.sleep(600)
                try:
                    self._get_cached_or_fetch("weather", self._fetch_weather_ha)
                    self._get_cached_or_fetch("calendar", self._fetch_calendar_ha)
                except Exception as e:
                    logger.warning(f"Background update failed: {e}")

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def _save_cache_async(self):
        threading.Thread(target=self._save_cache, daemon=True).start()

    def _save_cache(self):
        try:
            data = {"cache": self.cache, "timestamps": self.cache_timestamps}
            tmp = str(self.cache_file) + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(data, f, default=str)
            os.rename(tmp, self.cache_file)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _load_cache(self):
        if not self.cache_file.exists():
            return
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            self.cache = data.get("cache", {})
            self.cache_timestamps = data.get("timestamps", {})
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        return {
            "source": "home_assistant",
            "ha_configured": bool(self.ha_url and self.ha_token),
            "weather_entity": self.weather_entity,
            "calendar_entity": self.calendar_entity,
            "cache_entries": len(self.cache),
            "weather_available": "weather" in self.cache,
            "calendar_events": len(self.cache.get("calendar", [])),
        }


# =============================================================================
# TimeSeriesForecaster
# =============================================================================

class TimeSeriesForecaster:
    """
    Vorhersage von zeitbasierten Mustern.

    Features:
    - NAS-Nutzungsvorhersage pro Stunde
    - Anwesenheitsvorhersage
    - Saisonale Muster-Erkennung
    - Trend-Erkennung
    - Confidence Intervals
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.state_file = data_dir / "timeseries_forecaster.json"

        # Historische Daten
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))

        # Stündliche Aggregationen
        self.hourly_stats: Dict[str, Dict[int, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # Wöchentliche Muster (Stunde + Wochentag)
        self.weekly_patterns: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # Trend-Daten
        self.trends: Dict[str, Dict] = {}

        # Smoothing Parameter
        self.alpha = 0.3
        self.beta = 0.1
        self.gamma = 0.2

        self._load()
        self.lock = threading.RLock()
        logger.info("📈 TimeSeriesForecaster initialized")

    def record_observation(self, metric: str, value: float, timestamp: datetime = None):
        """
        Zeichnet eine Beobachtung auf.

        Args:
            metric: Name der Metrik (z.B. "nas_usage", "presence")
            value: Wert (0-1 für Wahrscheinlichkeiten)
            timestamp: Zeitpunkt (default: jetzt)
        """
        with self.lock:
            ts = timestamp or datetime.now()

            # Raw Data speichern
            self.time_series[metric].append({
                "timestamp": ts.isoformat(),
                "value": value,
                "hour": ts.hour,
                "weekday": ts.weekday(),
            })

            # Stündliche Stats
            self.hourly_stats[metric][ts.hour].append(value)
            if len(self.hourly_stats[metric][ts.hour]) > 500:
                self.hourly_stats[metric][ts.hour] = self.hourly_stats[metric][ts.hour][-500:]

            # Wöchentliche Pattern
            pattern_key = f"{ts.weekday()}_{ts.hour}"
            self.weekly_patterns[metric][pattern_key].append(value)
            if len(self.weekly_patterns[metric][pattern_key]) > 100:
                self.weekly_patterns[metric][pattern_key] = \
                    self.weekly_patterns[metric][pattern_key][-100:]

            # Periodisch analysieren
            if len(self.time_series[metric]) % 100 == 0:
                self._update_trends(metric)
                self._save_async()

    def forecast(self, metric: str, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Erstellt Vorhersage für die nächsten Stunden.
        """
        with self.lock:
            if metric not in self.weekly_patterns:
                return self._generate_fallback_forecast(hours_ahead)

            now = datetime.now()
            forecasts = []

            for h in range(hours_ahead):
                target_time = now + timedelta(hours=h)
                pattern_key = f"{target_time.weekday()}_{target_time.hour}"

                # Basis-Vorhersage aus Weekly Pattern
                pattern_data = self.weekly_patterns[metric].get(pattern_key, [])
                hourly_data = self.hourly_stats[metric].get(target_time.hour, [])

                if pattern_data:
                    pattern_mean = statistics.mean(pattern_data)
                    pattern_std = statistics.stdev(pattern_data) if len(pattern_data) > 1 else 0.2

                    hourly_mean = statistics.mean(hourly_data) if hourly_data else pattern_mean

                    # Trend berücksichtigen
                    trend = self.trends.get(metric, {}).get("slope", 0)
                    trend_adjustment = trend * h * 0.1

                    # Kombinierte Vorhersage
                    prediction = (
                        pattern_mean * 0.5 +
                        hourly_mean * 0.3 +
                        (pattern_mean + trend_adjustment) * 0.2
                    )

                    # Konfidenz
                    confidence = min(0.95, 0.3 + len(pattern_data) * 0.02)
                    confidence *= max(0.5, 1 - pattern_std)

                else:
                    if hourly_data:
                        prediction = statistics.mean(hourly_data)
                        confidence = min(0.7, 0.3 + len(hourly_data) * 0.01)
                    else:
                        prediction = 0.5
                        confidence = 0.3

                forecasts.append({
                    "datetime": target_time.isoformat(),
                    "hour": target_time.hour,
                    "weekday": target_time.weekday(),
                    "prediction": round(max(0, min(1, prediction)), 3),
                    "confidence": round(confidence, 2),
                    "confidence_low": round(max(0, prediction - pattern_std), 3) if pattern_data else None,
                    "confidence_high": round(min(1, prediction + pattern_std), 3) if pattern_data else None,
                })

            return forecasts

    def forecast_next_event(self, metric: str, threshold: float = 0.7,
                           max_hours: int = 48) -> Optional[Dict[str, Any]]:
        """
        Vorhersage wann das nächste "Event" eintritt.
        """
        forecasts = self.forecast(metric, max_hours)

        for fc in forecasts:
            if fc["prediction"] >= threshold and fc["confidence"] > 0.4:
                return {
                    "datetime": fc["datetime"],
                    "hours_from_now": (
                        datetime.fromisoformat(fc["datetime"]) - datetime.now()
                    ).total_seconds() / 3600,
                    "probability": fc["prediction"],
                    "confidence": fc["confidence"],
                }

        return None

    def get_peak_hours(self, metric: str, top_n: int = 5) -> List[Tuple[int, float]]:
        """Gibt Stunden mit höchster Aktivität zurück"""
        with self.lock:
            hourly = self.hourly_stats.get(metric, {})
            if not hourly:
                return []

            hour_means = [
                (hour, statistics.mean(values) if values else 0)
                for hour, values in hourly.items()
            ]

            return sorted(hour_means, key=lambda x: x[1], reverse=True)[:top_n]

    def get_low_hours(self, metric: str, top_n: int = 5) -> List[Tuple[int, float]]:
        """Gibt Stunden mit niedrigster Aktivität zurück"""
        with self.lock:
            hourly = self.hourly_stats.get(metric, {})
            if not hourly:
                return []

            hour_means = [
                (hour, statistics.mean(values) if values else 0)
                for hour, values in hourly.items()
            ]

            return sorted(hour_means, key=lambda x: x[1])[:top_n]

    def get_weekly_heatmap(self, metric: str) -> Dict[str, Dict[str, float]]:
        """Erstellt Heatmap der wöchentlichen Aktivität."""
        with self.lock:
            patterns = self.weekly_patterns.get(metric, {})

            heatmap = defaultdict(dict)
            weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

            for weekday in range(7):
                for hour in range(24):
                    key = f"{weekday}_{hour}"
                    values = patterns.get(key, [])
                    avg = statistics.mean(values) if values else 0.5
                    heatmap[weekday_names[weekday]][hour] = round(avg, 2)

            return dict(heatmap)

    def detect_anomaly(self, metric: str, current_value: float) -> Dict[str, Any]:
        """Erkennt Anomalien im aktuellen Wert."""
        with self.lock:
            now = datetime.now()
            pattern_key = f"{now.weekday()}_{now.hour}"

            historical = self.weekly_patterns.get(metric, {}).get(pattern_key, [])

            if len(historical) < 10:
                return {"is_anomaly": False, "reason": "insufficient_data"}

            mean = statistics.mean(historical)
            std = statistics.stdev(historical)

            z_score = (current_value - mean) / (std + 0.001)

            is_anomaly = abs(z_score) > 2.5

            return {
                "is_anomaly": is_anomaly,
                "z_score": round(z_score, 2),
                "expected_value": round(mean, 3),
                "std": round(std, 3),
                "current_value": current_value,
                "severity": "high" if abs(z_score) > 3 else "medium" if abs(z_score) > 2.5 else "low",
            }

    def _update_trends(self, metric: str):
        """Aktualisiert Trend-Informationen"""
        data = list(self.time_series.get(metric, []))

        if len(data) < 100:
            return

        now = datetime.now()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        recent = [d["value"] for d in data
                  if datetime.fromisoformat(d["timestamp"]) > week_ago]
        older = [d["value"] for d in data
                 if two_weeks_ago < datetime.fromisoformat(d["timestamp"]) <= week_ago]

        if recent and older:
            recent_avg = statistics.mean(recent)
            older_avg = statistics.mean(older)

            self.trends[metric] = {
                "slope": recent_avg - older_avg,
                "direction": "up" if recent_avg > older_avg * 1.1 else
                            "down" if recent_avg < older_avg * 0.9 else "stable",
                "recent_avg": round(recent_avg, 3),
                "older_avg": round(older_avg, 3),
                "data_points": len(recent) + len(older),
            }

    def _generate_fallback_forecast(self, hours_ahead: int) -> List[Dict]:
        """Fallback Vorhersage ohne historische Daten"""
        now = datetime.now()
        forecasts = []

        for h in range(hours_ahead):
            target = now + timedelta(hours=h)
            hour = target.hour

            if 8 <= hour <= 22:
                prediction = 0.6 if target.weekday() < 5 else 0.7
            else:
                prediction = 0.2

            forecasts.append({
                "datetime": target.isoformat(),
                "hour": hour,
                "weekday": target.weekday(),
                "prediction": prediction,
                "confidence": 0.3,
                "is_fallback": True,
            })

        return forecasts

    def get_stats(self) -> Dict[str, Any]:
        return {
            "metrics_tracked": list(self.time_series.keys()),
            "data_points": {k: len(v) for k, v in self.time_series.items()},
            "trends": self.trends,
            "has_sufficient_data": {
                k: len(v) >= 100 for k, v in self.time_series.items()
            },
        }

    def _save_async(self):
        threading.Thread(target=self._save, daemon=True).start()

    def _save(self):
        data = {
            "hourly_stats": {k: dict(v) for k, v in self.hourly_stats.items()},
            "weekly_patterns": {k: dict(v) for k, v in self.weekly_patterns.items()},
            "trends": self.trends,
        }
        try:
            tmp = str(self.state_file) + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(data, f)
            os.rename(tmp, self.state_file)
        except Exception as e:
            logger.error(f"Failed to save forecaster: {e}")

    def _load(self):
        if not self.state_file.exists():
            return
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)

            for k, v in data.get("hourly_stats", {}).items():
                self.hourly_stats[k] = defaultdict(list, {int(h): vals for h, vals in v.items()})

            for k, v in data.get("weekly_patterns", {}).items():
                self.weekly_patterns[k] = defaultdict(list, v)

            self.trends = data.get("trends", {})

            logger.info(f"📚 Loaded TimeSeriesForecaster: {len(self.hourly_stats)} metrics")
        except Exception as e:
            logger.error(f"Failed to load forecaster: {e}")



# =============================================================================
# CausalLearningEngine
# =============================================================================

@dataclass
class CausalRelation:
    """Repräsentiert eine kausale Beziehung"""
    strength: float = 0.0
    confidence: float = 0.0
    observations: int = 0
    intervention_count: int = 0
    avg_delay: float = 0.0
    last_observed: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'CausalRelation':
        return cls(**d)


class CausalLearningEngine:
    """
    Lernt echte Ursache-Wirkungs-Beziehungen.

    Unterscheidet zwischen:
    - Korrelation (A und B treten zusammen auf)
    - Kausalität (A verursacht B)
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.state_file = data_dir / "causal_learning.json"

        self.event_log: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        self.causal_relations: Dict[str, Dict[str, CausalRelation]] = defaultdict(dict)
        self.interventions: List[Dict] = []
        self.co_occurrence: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.temporal_precedence: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        self._load()
        self.lock = threading.RLock()
        logger.info("🔬 CausalLearningEngine initialized")

    def observe_event(self, event_type: str, context: Dict[str, Any],
                      triggered_by: str = None):
        """Beobachtet ein Event"""
        with self.lock:
            now = time.time()

            self.event_log[event_type].append({
                "timestamp": now,
                "context": context,
                "triggered_by": triggered_by,
            })

            recent_window = 300

            for other_event, log in self.event_log.items():
                if other_event == event_type:
                    continue

                for entry in reversed(list(log)):
                    time_diff = now - entry["timestamp"]
                    if time_diff > recent_window:
                        break

                    self.co_occurrence[other_event][event_type] += 1
                    self.temporal_precedence[other_event][event_type].append(time_diff)

                    if len(self.temporal_precedence[other_event][event_type]) > 500:
                        self.temporal_precedence[other_event][event_type] = \
                            self.temporal_precedence[other_event][event_type][-500:]

            if triggered_by:
                self._update_causal_relation(triggered_by, event_type, False)

            total_events = sum(len(log) for log in self.event_log.values())
            if total_events % 50 == 0:
                self._analyze_causality()
                self._save_async()

    def record_intervention(self, action: str, expected_effect: str,
                           actual_effect: str, success: bool, context: Dict = None):
        """Zeichnet Intervention auf"""
        with self.lock:
            self.interventions.append({
                "timestamp": time.time(),
                "action": action,
                "expected_effect": expected_effect,
                "actual_effect": actual_effect,
                "success": success,
                "context": context or {},
            })

            if success:
                self._update_causal_relation(action, actual_effect, True)

            logger.info(f"🔬 Intervention: {action} → {actual_effect} (success={success})")

    def get_likely_causes(self, effect: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Findet wahrscheinliche Ursachen"""
        with self.lock:
            causes = []

            for potential_cause in self.temporal_precedence.keys():
                if effect not in self.temporal_precedence[potential_cause]:
                    continue

                time_diffs = self.temporal_precedence[potential_cause][effect]
                if len(time_diffs) < 3:
                    continue

                score = self._calculate_causality_score(potential_cause, effect)

                if score > 0.2:
                    causes.append({
                        "cause": potential_cause,
                        "effect": effect,
                        "score": round(score, 3),
                        "observations": len(time_diffs),
                        "avg_delay_seconds": round(statistics.mean(time_diffs), 1),
                    })

            return sorted(causes, key=lambda x: x["score"], reverse=True)[:top_n]

    def get_likely_effects(self, cause: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Findet wahrscheinliche Effekte"""
        with self.lock:
            effects = []

            if cause not in self.temporal_precedence:
                return []

            for potential_effect, time_diffs in self.temporal_precedence[cause].items():
                if len(time_diffs) < 3:
                    continue

                score = self._calculate_causality_score(cause, potential_effect)

                if score > 0.2:
                    effects.append({
                        "cause": cause,
                        "effect": potential_effect,
                        "score": round(score, 3),
                        "observations": len(time_diffs),
                    })

            return sorted(effects, key=lambda x: x["score"], reverse=True)[:top_n]

    def get_causal_graph(self) -> Dict[str, Any]:
        """Gibt kausalen Graphen zurück"""
        with self.lock:
            nodes = set()
            edges = []

            for cause, effects in self.causal_relations.items():
                nodes.add(cause)
                for effect, relation in effects.items():
                    if relation.strength > 0.3:
                        nodes.add(effect)
                        edges.append({
                            "source": cause,
                            "target": effect,
                            "weight": relation.strength,
                        })

            return {"nodes": list(nodes), "edges": edges}

    def _calculate_causality_score(self, cause: str, effect: str) -> float:
        """Berechnet Kausalitäts-Score"""
        score = 0.0

        time_diffs = self.temporal_precedence.get(cause, {}).get(effect, [])
        if time_diffs:
            mean_delay = statistics.mean(time_diffs)
            consistency = 0.5
            if len(time_diffs) > 1:
                std_delay = statistics.stdev(time_diffs)
                consistency = 1 - min(1, std_delay / max(1, mean_delay))

            delay_score = max(0, 1 - mean_delay / 300)
            score += 0.3 * (consistency * 0.5 + delay_score * 0.5)

        co_count = self.co_occurrence.get(cause, {}).get(effect, 0)
        cause_count = len(self.event_log.get(cause, []))

        if cause_count > 0:
            score += 0.2 * min(1, (co_count / cause_count) * 2)

        intervention_evidence = sum(
            1 for i in self.interventions
            if i["action"] == cause and i["actual_effect"] == effect and i["success"]
        )
        total_interventions = sum(1 for i in self.interventions if i["action"] == cause)

        if total_interventions > 0:
            score += 0.4 * (intervention_evidence / total_interventions)

        effect_count = len(self.event_log.get(effect, []))
        if effect_count > 0 and co_count > 0:
            score += 0.1 * min(1, (co_count / effect_count) * 2)

        return min(1.0, score)

    def _update_causal_relation(self, cause: str, effect: str, is_intervention: bool):
        """Aktualisiert kausale Beziehung"""
        if effect not in self.causal_relations[cause]:
            self.causal_relations[cause][effect] = CausalRelation()

        relation = self.causal_relations[cause][effect]
        relation.observations += 1
        relation.last_observed = time.time()

        if is_intervention:
            relation.intervention_count += 1

        time_diffs = self.temporal_precedence.get(cause, {}).get(effect, [])
        if time_diffs:
            relation.avg_delay = statistics.mean(time_diffs[-50:])

        relation.strength = self._calculate_causality_score(cause, effect)
        relation.confidence = min(0.95, 0.3 + relation.observations * 0.02 +
                                  relation.intervention_count * 0.1)

    def _analyze_causality(self):
        """Periodische Analyse"""
        for cause in list(self.temporal_precedence.keys()):
            for effect in list(self.temporal_precedence[cause].keys()):
                score = self._calculate_causality_score(cause, effect)
                if score > 0.3:
                    if effect not in self.causal_relations[cause]:
                        self.causal_relations[cause][effect] = CausalRelation()
                    self.causal_relations[cause][effect].strength = score

    def get_stats(self) -> Dict[str, Any]:
        return {
            "events_tracked": list(self.event_log.keys()),
            "total_events": sum(len(log) for log in self.event_log.values()),
            "causal_relations": sum(len(e) for e in self.causal_relations.values()),
            "interventions": len(self.interventions),
            "strong_relations": sum(
                1 for effects in self.causal_relations.values()
                for rel in effects.values() if rel.strength > 0.6
            ),
        }

    def _save_async(self):
        threading.Thread(target=self._save, daemon=True).start()

    def _save(self):
        relations_data = {
            cause: {effect: rel.to_dict() for effect, rel in effects.items()}
            for cause, effects in self.causal_relations.items()
        }

        data = {
            "causal_relations": relations_data,
            "interventions": self.interventions[-500:],
            "co_occurrence": {k: dict(v) for k, v in self.co_occurrence.items()},
        }

        try:
            tmp = str(self.state_file) + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(data, f)
            os.rename(tmp, self.state_file)
        except Exception as e:
            logger.error(f"Failed to save causal learning: {e}")

    def _load(self):
        if not self.state_file.exists():
            return
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)

            for cause, effects in data.get("causal_relations", {}).items():
                for effect, rel_data in effects.items():
                    self.causal_relations[cause][effect] = CausalRelation.from_dict(rel_data)

            self.interventions = data.get("interventions", [])

            for k, v in data.get("co_occurrence", {}).items():
                self.co_occurrence[k] = defaultdict(int, v)

            logger.info(f"📚 Loaded CausalLearning: {len(self.causal_relations)} causes")
        except Exception as e:
            logger.error(f"Failed to load causal learning: {e}")


# =============================================================================
# ERWEITERTE AI INTEGRATION
# =============================================================================
class AIUpgradeIntegrationExtended:
    """Erweiterte Integration aller AI Komponenten."""

    def __init__(self, data_dir: Path, config: Dict = None):
        self.data_dir = data_dir
        data_dir.mkdir(parents=True, exist_ok=True)

        # Bestehende Komponenten
        self.bayesian = BayesianLearningEngine(data_dir)
        self.universal_ql = UniversalQLearner(data_dir)

        # NEUE KOMPONENTEN
        self.semantic_memory = SemanticMemoryEngine(data_dir)
        self.external_context = ExternalContextManager(data_dir, config=config)
        self.forecaster = TimeSeriesForecaster(data_dir)
        self.causal_engine = CausalLearningEngine(data_dir)

        self.total_observations = 0
        self.total_predictions = 0

        logger.info("🚀 AI Integration Extended ready!")

    def build_context(self, state_snapshot: dict) -> ContextFeatures:
        """Baut ContextFeatures aus State"""
        device_status = state_snapshot.get("device_status", {})
        now = datetime.now()
        last_activity = state_snapshot.get("last_activity_ts", time.time())
        time_since = (time.time() - last_activity) / 60.0

        return ContextFeatures(
            hour=now.hour,
            weekday=now.weekday(),
            is_weekend=now.weekday() >= 5,
            pc_online=device_status.get("workstation_pc_online", False),
            tv_online=device_status.get("tv_wohnzimmer_online", False),
            phone_online=device_status.get("kira_phone_online", False),
            tablet_online=device_status.get("tablet_kira_online", False),
            nas_was_used_recently=time_since < 30,
            time_since_last_use=time_since,
        )

    # 🆕 NEU HINZUGEFÜGT - Fehlte komplett!
    def build_universal_state(self, state_snapshot: dict, context: ContextFeatures) -> UniversalState:
        """Baut UniversalState für Q-Learning"""
        nas_status = state_snapshot.get("nas_status", {})
        ha_status = state_snapshot.get("ha_status", {})
        ha_presence = state_snapshot.get("ha_presence", {})

        # Person Home aus HA Presence oder HA Status
        person_home = ha_presence.get("anyone_home", False)
        if not person_home and ha_status:
            person_home = ha_status.get("person_kira", {}).get("state") == "home"

        return UniversalState(
            hour=context.hour,
            weekday=context.weekday,
            is_weekend=context.is_weekend,
            nas_online=nas_status.get("online", False),
            nas_idle_minutes=state_snapshot.get("idle_minutes", 0.0),
            nas_connections=nas_status.get("connections", 0),
            pc_online=context.pc_online,
            tv_online=context.tv_online,
            phone_online=context.phone_online,
            tablet_online=context.tablet_online,
            person_home=person_home,
            room_temperature=20.0,
            target_temperature=21.0,
            lights_on=0,
            cpu_temp=state_snapshot.get("system_metrics", {}).get("cpu_temp", 50.0),
            cpu_usage=state_snapshot.get("system_metrics", {}).get("cpu_usage", 25.0),
            governor=state_snapshot.get("current_governor", "ondemand"),
            cpu_load_duration=state_snapshot.get("high_load_duration", 0),  # ✅ FIX!
            nas_usage_probability=0.5,
            person_home_probability=0.5,
        )

    # 🆕 NEU HINZUGEFÜGT - Fehlte komplett!
    def get_recommended_action(self, universal_state: UniversalState,
                               available_actions: List[UniversalAction] = None) -> Tuple[UniversalAction, float]:
        """Empfohlene Aktion vom Q-Learning"""
        action = self.universal_ql.select_action(universal_state, available_actions, explore=False)
        rankings = self.universal_ql.get_action_rankings(universal_state, available_actions)
        confidence = rankings[0][1] if rankings else 0.5
        return action, confidence

    # 🆕 NEU HINZUGEFÜGT - Fehlte komplett!
    def report_action_result(self, universal_state: UniversalState,
                            success: bool, reward_details: Dict = None):
        """Meldet Ergebnis zurück an Q-Learning"""
        self.universal_ql.observe_result(universal_state, success, reward_details)

    def observe(self, context: ContextFeatures, nas_was_used: bool,
                event_type: str = None, outcome: str = None):
        """Beobachtung an alle AI Systeme."""
        self.bayesian.observe(context, nas_was_used)

        if event_type:
            self.semantic_memory.store_event(
                event_type=event_type,
                context={
                    "hour": context.hour, "weekday": context.weekday,
                    "is_weekend": context.is_weekend, "pc_online": context.pc_online,
                    "tv_online": context.tv_online, "phone_online": context.phone_online,
                },
                outcome=outcome or ("nas_used" if nas_was_used else "nas_idle"),
                success=nas_was_used,
            )
            self.causal_engine.observe_event(event_type, {
                "pc_online": context.pc_online, "tv_online": context.tv_online,
            })

        self.forecaster.record_observation("nas_usage", 1.0 if nas_was_used else 0.0)
        self.total_observations += 1

    def predict(self, context: ContextFeatures) -> Dict[str, Any]:
        """Ensemble-Vorhersage."""
        bayesian_result = self.bayesian.predict(context)

        similar = self.semantic_memory.recall_similar({
            "hour": context.hour, "weekday": context.weekday,
            "pc_online": context.pc_online, "tv_online": context.tv_online,
        }, k=5)
        memory_prob = sum(1 for m in similar if m["success"]) / len(similar) if similar else 0.5

        forecast = self.forecaster.forecast("nas_usage", 1)
        forecast_prob = forecast[0]["prediction"] if forecast else 0.5

        ensemble = (bayesian_result["probability"] * 0.4 + memory_prob * 0.25 +
                    forecast_prob * 0.25 + 0.5 * 0.1)

        self.total_predictions += 1

        return {
            "ensemble": ensemble,
            "bayesian": bayesian_result,
            "memory": {"probability": memory_prob, "similar_count": len(similar)},
            "forecast": {"probability": forecast_prob},
            "external": self.external_context.get_weather(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Gesamtstatistiken"""
        return {
            "bayesian": {"contexts": len(self.bayesian.context_posteriors)},
            "universal_ql": self.universal_ql.get_stats(),
            "semantic_memory": self.semantic_memory.get_stats(),
            "external_context": self.external_context.get_stats(),
            "forecaster": self.forecaster.get_stats(),
            "causal_learning": self.causal_engine.get_stats(),
            "total_observations": self.total_observations,
            "total_predictions": self.total_predictions,
        }

# =============================================================================
# PRESENCE PATTERN ENGINE - Lernt Anwesenheitsmuster
# =============================================================================

class PresencePatternEngine:
    """
    Intelligente Anwesenheitserkennung v2.0

    Features:
    - Separate Tracking für kurze vs. lange Abwesenheiten
    - Erkennt "Frei-Tage" wenn User untypisch lange zuhause ist
    - Passt Vorhersagen basierend auf erkanntem Tages-Modus an
    """

    MICRO_THRESHOLD = 15
    SHORT_THRESHOLD = 90
    MIN_DATA_POINTS = 3
    FREE_DAY_DETECTION_DELAY = 90

    def __init__(self, data_file: str = "presence_patterns_v2.json", min_data_points: int = 3):
        self.data_file = Path(data_file)
        self.MIN_DATA_POINTS = min_data_points

        self.work_absences: List[AbsenceEvent] = []
        self.short_trips: List[AbsenceEvent] = []
        self.current_absence: Optional[AbsenceEvent] = None

        self.day_profiles: Dict[str, DayProfile] = {}
        self.current_day_mode: DayMode = DayMode.UNKNOWN
        self.day_mode_detected_at: Optional[datetime] = None

        self.typical_departure_times: Dict[int, List[float]] = defaultdict(list)
        self.typical_return_times: Dict[int, List[float]] = defaultdict(list)

        self._user_is_home: bool = True
        self._load()

    def on_departure(self, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        timestamp = timestamp or datetime.now()
        self._update_day_mode(timestamp)

        self.current_absence = AbsenceEvent.create(
            departure=timestamp,
            day_mode=self.current_day_mode.value
        )
        self._user_is_home = False
        self._save()

        prediction = self.predict_return()
        mode_str = self._get_mode_display_name(self.current_day_mode)

        return {
            "status": "departure_registered",
            "departure_time": timestamp.isoformat(),
            "detected_day_mode": self.current_day_mode.value,
            "mode_display": mode_str,
            "prediction": prediction
        }

    def on_return(self, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        timestamp = timestamp or datetime.now()

        if not self.current_absence:
            self._user_is_home = True
            return {"status": "no_active_absence"}

        self.current_absence.finalize(timestamp)
        event = self.current_absence
        analysis = self._categorize_and_store(event)

        if event.category == AbsenceCategory.WORK.value:
            self._update_typical_times(event)

        self.current_absence = None
        self._user_is_home = True
        self._save()

        return {
            "status": "return_registered",
            "return_time": timestamp.isoformat(),
            "duration_minutes": event.duration_minutes,
            "category": event.category,
            "day_mode": event.day_mode,
            "analysis": analysis
        }

    def predict_return(self) -> Optional[Dict[str, Any]]:
        if not self.current_absence:
            return None

        departure = datetime.fromisoformat(self.current_absence.departure_time)
        now = datetime.now()
        elapsed_minutes = (now - departure).total_seconds() / 60

        # Kontext-basierte Kategorisierung
        if self.current_day_mode in [DayMode.FREE_DAY, DayMode.WEEKEND]:
            likely_category = "short_trip"
            events = self._get_similar_short_trips(self.current_absence)
            if elapsed_minutes > 60:
                likely_category = "possibly_longer"
        elif self.current_day_mode == DayMode.HOME_OFFICE:
            likely_category = "short_trip"
            events = self._get_similar_short_trips(self.current_absence)
        else:
            likely_category = "work"
            events = self._get_similar_work_absences(self.current_absence)

        if len(events) < self.MIN_DATA_POINTS:
            return self._make_fallback_prediction(likely_category, elapsed_minutes)

        return self._calculate_prediction(events, likely_category)

    def tick(self, pc_online: bool = False, timestamp: Optional[datetime] = None):
        """Regelmäßig aufrufen für Frei-Tag-Erkennung"""
        timestamp = timestamp or datetime.now()
        self._update_day_profile(timestamp, pc_online)

        if self._user_is_home:
            self._check_for_free_day(timestamp, pc_online)

    def get_day_mode(self) -> Dict[str, Any]:
        return {
            "mode": self.current_day_mode.value,
            "display_name": self._get_mode_display_name(self.current_day_mode),
            "detected_at": self.day_mode_detected_at.isoformat() if self.day_mode_detected_at else None,
            "reasoning": self._get_mode_reasoning()
        }

    def get_statistics(self) -> Dict[str, Any]:
        work_events = [e for e in self.work_absences if e.duration_minutes]
        short_events = [e for e in self.short_trips if e.duration_minutes]

        stats = {
            "total_events": len(work_events) + len(short_events),
            "total_work_absences": len(work_events),
            "total_short_trips": len(short_events),
            "current_day_mode": self.current_day_mode.value,
            "day_mode_display": self._get_mode_display_name(self.current_day_mode),
            "user_is_home": self._user_is_home,
            "current_absence_active": self.current_absence is not None,
        }

        if work_events:
            durations = [e.duration_minutes for e in work_events]
            stats["work_avg_duration_hours"] = round(statistics.mean(durations) / 60, 1)

        if short_events:
            durations = [e.duration_minutes for e in short_events]
            stats["short_trip_avg_minutes"] = round(statistics.mean(durations), 0)

        return stats

    def is_user_home(self) -> bool:
        return self._user_is_home

    def should_prepare_for_return(self, buffer_minutes: float = 30) -> Tuple[bool, str]:
        if self._user_is_home:
            return False, "User ist zuhause"

        prediction = self.predict_return()
        if not prediction or not prediction.get("expected_return"):
            return False, prediction.get("reasoning", "Keine Vorhersage") if prediction else "Keine Vorhersage"

        minutes_until = prediction.get("minutes_until_return", 999)
        confidence = prediction.get("confidence", 0)

        if minutes_until < 0:
            return True, f"User überfällig seit {abs(minutes_until):.0f}min"
        if minutes_until <= buffer_minutes and confidence >= 0.6:
            return True, f"Rückkehr in ~{minutes_until:.0f}min erwartet ({confidence:.0%})"

        return False, f"Rückkehr erst in ~{minutes_until:.0f}min"

    # === PRIVATE METHODS ===

    def _check_for_free_day(self, timestamp: datetime, pc_online: bool):
        weekday = timestamp.weekday()

        if weekday >= 5:
            if self.current_day_mode != DayMode.WEEKEND:
                self.current_day_mode = DayMode.WEEKEND
                self.day_mode_detected_at = timestamp
                logger.info("📅 Wochenende erkannt")
            return

        if self.current_day_mode in [DayMode.FREE_DAY, DayMode.HOME_OFFICE]:
            if self.day_mode_detected_at and self.day_mode_detected_at.date() == timestamp.date():
                return

        typical_times = self.typical_departure_times.get(weekday, [])
        if not typical_times or len(typical_times) < 3:
            return

        typical_departure = statistics.mean(typical_times)
        current_hour = timestamp.hour + timestamp.minute / 60
        hours_late = current_hour - typical_departure

        if hours_late < (self.FREE_DAY_DETECTION_DELAY / 60):
            return

        if pc_online:
            self.current_day_mode = DayMode.HOME_OFFICE
            self.day_mode_detected_at = timestamp
            logger.info(f"🏠 Home-Office erkannt (PC aktiv, normalerweise um {int(typical_departure)}:{int((typical_departure%1)*60):02d} weg)")
        else:
            self.current_day_mode = DayMode.FREE_DAY
            self.day_mode_detected_at = timestamp
            logger.info(f"🏖️ Freier Tag erkannt (normalerweise um {int(typical_departure)}:{int((typical_departure%1)*60):02d} weg)")

    def _update_day_mode(self, timestamp: datetime):
        if self.day_mode_detected_at:
            if self.day_mode_detected_at.date() != timestamp.date():
                self.current_day_mode = DayMode.UNKNOWN
                self.day_mode_detected_at = None

        if timestamp.weekday() >= 5:
            self.current_day_mode = DayMode.WEEKEND
            self.day_mode_detected_at = timestamp

    def _categorize_and_store(self, event: AbsenceEvent) -> Dict[str, Any]:
        analysis = {"category": event.category, "day_mode": event.day_mode, "comparison": "normal"}

        if event.category == AbsenceCategory.MICRO.value:
            analysis["note"] = "Zu kurz, wird ignoriert"
            return analysis

        elif event.category == AbsenceCategory.SHORT_TRIP.value:
            similar = self._get_similar_short_trips(event)
            self.short_trips.append(event)
            if len(self.short_trips) > 100:
                self.short_trips = self.short_trips[-100:]

            if len(similar) >= 3:
                avg_duration = statistics.mean([e.duration_minutes for e in similar])
                diff = event.duration_minutes - avg_duration
                if abs(diff) < 10:
                    analysis["comparison"] = "normal"
                elif diff > 0:
                    analysis["comparison"] = "longer_than_usual"
                    analysis["diff_minutes"] = round(diff, 1)
                else:
                    analysis["comparison"] = "shorter_than_usual"
                    analysis["diff_minutes"] = round(diff, 1)

        elif event.category == AbsenceCategory.WORK.value:
            similar = self._get_similar_work_absences(event)
            self.work_absences.append(event)
            if len(self.work_absences) > 200:
                self.work_absences = self.work_absences[-200:]

            if len(similar) >= 3 and event.return_hour:
                avg_return = statistics.mean([e.return_hour for e in similar if e.return_hour])
                diff_minutes = (event.return_hour - avg_return) * 60
                if abs(diff_minutes) < 15:
                    analysis["comparison"] = "normal"
                elif diff_minutes > 0:
                    analysis["comparison"] = "later_than_usual"
                    analysis["diff_minutes"] = round(diff_minutes, 1)
                else:
                    analysis["comparison"] = "earlier_than_usual"
                    analysis["diff_minutes"] = round(diff_minutes, 1)

        return analysis

    def _update_typical_times(self, event: AbsenceEvent):
        if event.weekday >= 5:
            return

        self.typical_departure_times[event.weekday].append(event.departure_hour)
        if len(self.typical_departure_times[event.weekday]) > 20:
            self.typical_departure_times[event.weekday] = self.typical_departure_times[event.weekday][-20:]

        if event.return_hour:
            self.typical_return_times[event.weekday].append(event.return_hour)
            if len(self.typical_return_times[event.weekday]) > 20:
                self.typical_return_times[event.weekday] = self.typical_return_times[event.weekday][-20:]

    def _get_similar_short_trips(self, event: AbsenceEvent) -> List[AbsenceEvent]:
        similar = []
        is_weekend = event.weekday >= 5

        for hist in self.short_trips:
            if hist.duration_minutes is None:
                continue
            hist_weekend = hist.weekday >= 5
            if hist_weekend != is_weekend:
                continue
            if abs(hist.departure_hour - event.departure_hour) <= 2:
                similar.append(hist)

        similar.sort(key=lambda e: e.departure_time, reverse=True)
        return similar[:30]

    def _get_similar_work_absences(self, event: AbsenceEvent) -> List[AbsenceEvent]:
        similar = []

        for hist in self.work_absences:
            if hist.duration_minutes is None:
                continue
            day_diff = abs(hist.weekday - event.weekday)
            if day_diff > 1 and day_diff < 6:
                continue
            if abs(hist.departure_hour - event.departure_hour) <= 1:
                similar.append(hist)

        similar.sort(key=lambda e: e.departure_time, reverse=True)
        return similar[:30]

    def _calculate_prediction(self, events: List[AbsenceEvent], category: str) -> Dict[str, Any]:
        if not events:
            return {"error": "no_events"}

        departure = datetime.fromisoformat(self.current_absence.departure_time)

        if category == "short_trip":
            durations = [e.duration_minutes for e in events if e.duration_minutes]
            if not durations:
                return self._make_fallback_prediction(category, 0)

            avg_duration = statistics.mean(durations)
            std_duration = statistics.stdev(durations) if len(durations) > 1 else 15
            expected_return = departure + timedelta(minutes=avg_duration)
        else:
            returns = [e.return_hour for e in events if e.return_hour]
            if not returns:
                return self._make_fallback_prediction(category, 0)

            avg_return = statistics.mean(returns)
            std_hours = statistics.stdev(returns) if len(returns) > 1 else 0.5
            std_duration = std_hours * 60

            expected_return = departure.replace(
                hour=int(avg_return),
                minute=int((avg_return % 1) * 60),
                second=0, microsecond=0
            )
            if expected_return < departure:
                expected_return += timedelta(days=1)

        minutes_until = (expected_return - datetime.now()).total_seconds() / 60
        confidence = self._calculate_confidence(len(events), std_duration)

        return {
            "expected_return": expected_return,
            "expected_return_str": expected_return.strftime("%H:%M"),
            "minutes_until_return": round(minutes_until, 0),
            "confidence": round(confidence, 2),
            "std_minutes": round(std_duration, 1),
            "window_early": (expected_return - timedelta(minutes=std_duration)).strftime("%H:%M"),
            "window_late": (expected_return + timedelta(minutes=std_duration)).strftime("%H:%M"),
            "category": category,
            "sample_size": len(events),
            "reasoning": f"Basierend auf {len(events)} ähnlichen {category} Events"
        }

    def _make_fallback_prediction(self, category: str, elapsed_minutes: float) -> Dict[str, Any]:
        if category == "short_trip":
            expected_duration = 40
            std = 20
            reasoning = "Schätzung für kurzen Trip (keine Daten)"
        else:
            expected_duration = 8 * 60
            std = 60
            reasoning = "Schätzung für Arbeitstag (keine Daten)"

        departure = datetime.fromisoformat(self.current_absence.departure_time)
        expected_return = departure + timedelta(minutes=expected_duration)
        minutes_until = (expected_return - datetime.now()).total_seconds() / 60

        return {
            "expected_return": expected_return,
            "expected_return_str": expected_return.strftime("%H:%M"),
            "minutes_until_return": round(minutes_until, 0),
            "confidence": 0.3,
            "std_minutes": std,
            "category": category,
            "sample_size": 0,
            "reasoning": reasoning,
            "is_fallback": True
        }

    def _calculate_confidence(self, sample_size: int, std_minutes: float) -> float:
        confidence = 0.5
        confidence += min(0.25, sample_size * 0.025)

        if std_minutes < 15:
            confidence += 0.15
        elif std_minutes < 30:
            confidence += 0.05
        elif std_minutes > 60:
            confidence -= 0.10

        if self.current_day_mode in [DayMode.FREE_DAY, DayMode.WEEKEND]:
            confidence += 0.05

        return max(0.1, min(0.95, confidence))

    def _update_day_profile(self, timestamp: datetime, pc_online: bool):
        date_key = timestamp.date().isoformat()

        if date_key not in self.day_profiles:
            self.day_profiles[date_key] = DayProfile(
                date=date_key,
                weekday=timestamp.weekday(),
                first_seen_home=timestamp.isoformat() if self._user_is_home else None
            )

        profile = self.day_profiles[date_key]
        if self._user_is_home:
            profile.total_home_minutes += 1
        else:
            profile.total_away_minutes += 1

        if pc_online and self._user_is_home:
            profile.pc_active_minutes += 1

        profile.detected_mode = self.current_day_mode.value

        cutoff = (datetime.now() - timedelta(days=30)).date().isoformat()
        self.day_profiles = {k: v for k, v in self.day_profiles.items() if k >= cutoff}

    def _get_mode_display_name(self, mode: DayMode) -> str:
        names = {
            DayMode.UNKNOWN: "Unbekannt",
            DayMode.WORK_DAY: "Arbeitstag",
            DayMode.FREE_DAY: "Freier Tag",
            DayMode.WEEKEND: "Wochenende",
            DayMode.HOME_OFFICE: "Home Office"
        }
        return names.get(mode, "Unbekannt")

    def _get_mode_reasoning(self) -> str:
        if self.current_day_mode == DayMode.WEEKEND:
            return "Wochenende (Sa/So)"
        elif self.current_day_mode == DayMode.FREE_DAY:
            return "User ist länger als normal zuhause"
        elif self.current_day_mode == DayMode.HOME_OFFICE:
            return "User zuhause mit aktivem PC"
        else:
            return "Noch nicht erkannt"

    def _save(self):
        data = {
            "version": 2,
            "last_updated": datetime.now().isoformat(),
            "work_absences": [asdict(e) for e in self.work_absences[-200:]],
            "short_trips": [asdict(e) for e in self.short_trips[-100:]],
            "current_absence": asdict(self.current_absence) if self.current_absence else None,
            "typical_departure_times": dict(self.typical_departure_times),
            "typical_return_times": dict(self.typical_return_times),
            "current_day_mode": self.current_day_mode.value,
            "day_mode_detected_at": self.day_mode_detected_at.isoformat() if self.day_mode_detected_at else None,
            "user_is_home": self._user_is_home,
        }
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = str(self.data_file) + ".tmp"
            with open(tmp, 'w') as f:
                json.dump(data, f, indent=2)
            os.rename(tmp, self.data_file)
        except Exception as e:
            logger.error(f"[PresenceEngine] Save error: {e}")

    def _load(self):
        if not self.data_file.exists():
            return
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)

            if data.get("version", 1) < 2:
                self._migrate_v1_data(data)
                return

            self.work_absences = [AbsenceEvent(**e) for e in data.get("work_absences", [])]
            self.short_trips = [AbsenceEvent(**e) for e in data.get("short_trips", [])]

            if data.get("current_absence"):
                self.current_absence = AbsenceEvent(**data["current_absence"])

            for wd, times in data.get("typical_departure_times", {}).items():
                self.typical_departure_times[int(wd)] = times
            for wd, times in data.get("typical_return_times", {}).items():
                self.typical_return_times[int(wd)] = times

            try:
                self.current_day_mode = DayMode(data.get("current_day_mode", "unknown"))
            except Exception:
                self.current_day_mode = DayMode.UNKNOWN

            if data.get("day_mode_detected_at"):
                self.day_mode_detected_at = datetime.fromisoformat(data["day_mode_detected_at"])

            self._user_is_home = data.get("user_is_home", True)

            logger.info(f"[PresenceEngine] Loaded: {len(self.work_absences)} work, {len(self.short_trips)} short")

        except Exception as e:
            logger.error(f"[PresenceEngine] Load error: {e}")

    def _migrate_v1_data(self, old_data: dict):
        """Migriert alte v1 Daten"""
        old_history = old_data.get("history", [])

        for event_data in old_history:
            try:
                event = AbsenceEvent(**event_data)
                if event.duration_minutes:
                    if event.duration_minutes < 15:
                        event.category = AbsenceCategory.MICRO.value
                    elif event.duration_minutes < 90:
                        event.category = AbsenceCategory.SHORT_TRIP.value
                        self.short_trips.append(event)
                    else:
                        event.category = AbsenceCategory.WORK.value
                        self.work_absences.append(event)
                        self._update_typical_times(event)
            except Exception:
                continue

        logger.info(f"[PresenceEngine] Migrated v1 data")
        self._save()





RUNS_AS_ROOT = (os.geteuid() == 0)

BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "state"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
BACKUP_DIR = BASE_DIR / "backups"

for d in [STATE_DIR, DATA_DIR, LOG_DIR, BACKUP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

if HAVE_DOTENV:
    load_dotenv()

CONFIG = {
    "system_name": "Pi-Control Ultimate v8.0",
    "log_level": "INFO",

    "actors": {
        "heating": {
            "wohnzimmer": "climate.sauna", # Beispiel für HA Entitäts-ID
            "schlafzimmer": "climate.schlaflos",
            "küche": "climate.wohnzimmer_thermostat",
        },
        "lights": {
            "küche": "light.küche_licht",
            "wohnzimmer": "light.wohnzimmer_hauptlicht",
        },
    },

    "zone_mapping": {
        "devices_to_scan": get_config("devices.tracked_devices", {
            # Gerätename: IP-Adresse (für Ping/Port-Check) - Fallback wenn keine Config
            "tv_wohnzimmer": "192.168.178.29",
            "workstation_pc": "192.168.178.31",
            "tablet_kira": "192.168.178.35",
            "kira_phone":"192.168.178.34"
        }),
        "mac_addresses": {
            # MAC-Adressen (für WoL und fortgeschrittene Layer 2 Scans)
            "kira_phone": "DE:1C:CA:6C:CB:64",
            "nas": "00:E0:4C:68:04:B0",
        },
        "zones": {
            "wohnzimmer": ["tv_wohnzimmer", "workstation_pc"],
            "küche": ["tablet_kira"],
            "schlafzimmer": [],
        },
        "access_points": {
            "kira_phone": {
                "bssid_wohnzimmer": "wohnzimmer",
            }
        },
    },

    "context_rules": [
        # 1. ACTIVE MODE: Wenn Handy DA ist UND (TV ODER PC an sind) -> NAS WACH HALTEN
        # Regel für TV (Priorität hoch)

        {
            "name": "PC_Active",
            "time_range": [0, 24],
            "conditions": {"workstation_pc_online": True},
            "result_zone": "active_use"
        },

        # 2. TV an = Active (Egal wo das Handy ist)
        {
            "name": "TV_Active",
            "time_range": [0, 24],
            "conditions": {"tv_wohnzimmer_online": True},
            "result_zone": "active_use"
        },



        # 2. PASSIVE/NIGHT MODE: Handy DA, aber TV & PC sind AUS -> NAS SCHLAFEN
        {
            "name": "User_Idle_Home",
            "time_range": [0, 24],
            "conditions": {
                "kira_phone_online": True,
                "tv_wohnzimmer_online": False,
                "workstation_pc_online": False
            },
            "result_zone": "passive_home"
        },

        # 3. AWAY MODE: Handy WEG -> NAS SOFORT AUS (SSH)
        {
            "name": "User_Away",
            "time_range": [0, 24],
            "conditions": {
                "kira_phone_online": False,
                "workstation_pc_online": False, # WICHTIG: PC muss auch aus sein
                "tv_wohnzimmer_online": False   # WICHTIG: TV muss auch aus sein
            },
            "result_zone": "away"
        },

        {"name": "Tablet_In_Kueche", "time_range": [18, 21],
         "conditions": {"tablet_online": True,
        "nas_connected": True}, "result_zone": "küche"},
        {"name": "Night_Mode_Schlafzimmer", "time_range": [22, 7], "conditions": {"tv_wohnzimmer_online": False, "workstation_pc_online": False, "kira_phone_online": True}, "result_zone": "schlafzimmer"},
    ],

    "home_assistant": {
        "enabled": os.getenv("HA_ENABLED", "false").lower() == 'true',
        "api_url": os.getenv("HA_API_URL", get_config("network.home_assistant.api_url", "http://192.168.178.99:8123/api")),
        "api_token": os.getenv("HA_API_TOKEN", get_config("network.home_assistant.token", "")),
    },

    "nas": {
        "ip": os.getenv("NAS_IP", get_config("network.nas.ip", "192.168.178.40")),
        "mac": os.getenv("MAC_ADDRESS", get_config("network.nas.mac", "00:E0:4C:68:04:B0")),
        "ssh_port": int(os.getenv("SSH_PORT", str(get_config("network.nas.ssh_port", 22)))),
        "ssh_user": os.getenv("SSH_USER", get_config("network.nas.ssh_user", "admin")),
        "ssh_key": os.getenv("SSH_KEY_PATH", "/home/zero/.ssh/nas_key"),
        "udp_port": int(os.getenv("NAS_UDP_PORT", "5001")),
    },

    "mqtt": {
        "host": get_config("network.mqtt.broker_ip", "192.168.178.99"),
        "port": get_config("network.mqtt.broker_port", 1883),
        "user": get_config("network.mqtt.username", ""),
        "password": get_config("network.mqtt.password", ""),
    },

    "network": {
        "proxy_listen_ip": "0.0.0.0",
        "proxy_ports": [int(p) for p in os.getenv("PORTS_TO_WATCH", "80,139,445").split(",")],
        "ping_interval": 10,
    },

    "web_ui": {
        "listen_ip": "0.0.0.0",
        "port": int(os.getenv("PREVIEW_HTTP_PORT", "8008")),
    },

    "goals": {
        "energy_saving": {"weight": 0.35, "target_idle_power": 5.0},
        "responsiveness": {"weight": 0.3, "target_latency_ms": 100},
        "stability": {"weight": 0.1, "min_uptime_hours": 24},
        "learning": {"weight": 0.1, "exploration_rate": 0.15},
        "user_comfort": {"weight": 0.10, "target_value": 1.0},
        "curiosity": {"weight": 0.05, "target_information_gain": 1.0},
    },

    "cpu_governors": {
        "available": ["performance", "powersave", "ondemand", "conservative", "schedutil"],
        "properties": {
            "performance": {"speed": 1.0, "energy": 0.2, "stability": 0.9},
            "powersave": {"speed": 0.3, "energy": 1.0, "stability": 0.8},
            "ondemand": {"speed": 0.7, "energy": 0.6, "stability": 0.7},
            "conservative": {"speed": 0.5, "energy": 0.8, "stability": 0.9},
            "schedutil": {"speed": 0.8, "energy": 0.7, "stability": 0.8},
        },
    },

    "learning": {
        "ab_testing_enabled": True,
        "sandbox_depth": 3,
        "min_observations": 20,
        "confidence_threshold": 0.65,
        "base_learning_rate": 0.05,
        "surprise_factor": 2.0,
    },

    "state_file": str(STATE_DIR / "ultimate_state.json"),
}


# =============================================================================
# ⚙️ EXTERNAL CONFIG LOADING (JSON OVERRIDE)
# =============================================================================

def deep_merge_config(base_config: dict, override_config: dict):
    """Verschmilzt externe Config rekursiv."""
    for key, value in override_config.items():
        if isinstance(value, dict) and key in base_config and isinstance(base_config[key], dict):
            deep_merge_config(base_config[key], value)
        else:
            base_config[key] = value

EXTERNAL_CONFIG_FILE = BASE_DIR / "config.json"

if EXTERNAL_CONFIG_FILE.exists():
    try:
        logger.info(f"📂 Lade externe Konfiguration: {EXTERNAL_CONFIG_FILE}")
        with open(EXTERNAL_CONFIG_FILE, 'r', encoding='utf-8') as f:
            external_data = json.load(f)
        deep_merge_config(CONFIG, external_data)
        logger.info("✅ Externe Konfiguration angewendet.")
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON-Fehler in config.json: {e}. Nutze Standards.")
    except Exception as e:
        logger.error(f"❌ FEHLER in config.json: {e}. Nutze Standards.")

else:
    # 🟢 NEU: Automatisch eine Vorlage erstellen, wenn die Datei fehlt!
    logger.info("ℹ️ Keine config.json gefunden. Erstelle eine Standard-Vorlage...")

    default_template = {
        "_comment": "Diese Werte überschreiben die Standards im Skript.",
        "system_name": "Pi-Control Ultimate (Custom)",
        "log_level": "INFO",
        "nas": {
            "ip": CONFIG["nas"]["ip"]  # Übernimmt aktuellen Standard als Beispiel
        },
        "learning": {
            "base_learning_rate": 0.05
        },
        "skills_enabled": ["network_sentinel"] # Beispiel für neue Optionen
    }

    try:
        with open(EXTERNAL_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_template, f, indent=4)
        logger.info(f"✅ Vorlage erstellt: {EXTERNAL_CONFIG_FILE}")
    except PermissionError as e:
        logger.warning(f"⚠️ Keine Schreibrechte für config.json: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Konnte Vorlage nicht erstellen: {e}")


# =============================================================================
# LOGGING SYSTEM (MIT DASHBOARD SUPPORT)
# =============================================================================

# 1. Die Klasse für den Speicher
class MemoryLogHandler(logging.Handler):
    """Speichert die letzten N Logs im RAM für das Dashboard."""
    def __init__(self, capacity=50):
        super().__init__()
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def emit(self, record):
        try:
            msg = self.format(record)
            # Speichere Tuple (Level, Message, Timestamp)
            self.buffer.append({
                "level": record.levelname,
                "message": msg,
                "time": datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
            })
        except Exception:
            self.handleError(record)

    def get_logs(self):
        return list(self.buffer)

# 2. Instanz erstellen
memory_log_handler = MemoryLogHandler(capacity=100)
memory_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

# 3. Logging konfigurieren (File + Console + Memory)
LOG_FILE = LOG_DIR / "ultimate.log"
logging.basicConfig(
    level=getattr(logging, CONFIG["log_level"]),
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler(),
        memory_log_handler
    ]
)

# FIX: Logger must be defined globally BEFORE any class uses it
logger = logging.getLogger("ultimate")


# =============================================================================
# UTILITIES (Asynchronous State Writing)
# =============================================================================

def now_ts() -> float:
    return time.time()

def atomic_write_json(data: dict, filename: str):
    """Schreibt JSON atomar (synchron)"""
    tmp = filename + ".tmp"
    try:
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        with open(tmp, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp, filename)
    except Exception as e:
        logger.error(f"Save failed {filename}: {e}")

def async_atomic_write_json(data: dict, filename: str):
    """Schreibt JSON asynchron, um den Haupt-Thread nicht zu blockieren (RAM-First)."""
    def target():
        atomic_write_json(data, filename)

    threading.Thread(target=target, daemon=True).start()

def load_json_file(filename: str, default: dict) -> dict:
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Load failed {filename}: {e}")
    return default

def send_wol(mac: str) -> bool:
    try:
        mac_bytes = bytes.fromhex(mac.replace(":", ""))
        magic = b'\xff' * 6 + mac_bytes * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic, ("<broadcast>", 9))
        logger.info(f"🌟 WoL sent to {mac}")
        return True
    except Exception as e:
        logger.error(f"WoL failed: {e}")
        return False

def is_port_open(ip: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((ip, port)) == 0
    except Exception:
        return False

def get_cpu_temp() -> float:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return 0.0

def get_cpu_usage() -> float:
    if HAVE_PSUTIL:
        return psutil.cpu_percent(interval=0.1)
    return 0.0

def get_ram_usage() -> float:
    if HAVE_PSUTIL:
        return psutil.virtual_memory().percent
    return 0.0

def send_ssh_command(host: str, user: str, key: str, cmd: str, port: int = 22) -> bool:
    """
    Führt SSH-Befehl sicher aus.

    SECURITY: Lädt bekannte Hosts aus ~/.ssh/known_hosts.
    Bei unbekannten Hosts wird eine Warnung geloggt und der Verbindungsversuch abgebrochen.
    """
    if not HAVE_PARAMIKO:
        return False
    try:
        client = paramiko.SSHClient()
        # SECURITY: Lade bekannte Hosts statt alle zu akzeptieren (verhindert MITM)
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(known_hosts_path):
            client.load_system_host_keys()
            client.load_host_keys(known_hosts_path)
        # Bei unbekanntem Host: Warnung loggen statt blind akzeptieren
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(host, port=port, username=user, key_filename=key, timeout=10)
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        client.close()
        return exit_status == 0
    except paramiko.ssh_exception.SSHException as e:
        logger.error(f"SSH security error for {host}: {e}")
        return False
    except Exception as e:
        logger.error(f"SSH failed: {e}")
        return False

# =============================================================================
# LAYER 0: UDP COMMUNICATION WITH NAS
# =============================================================================

@dataclass
class NASStatus:
    """NAS meldet seinen Status via UDP"""
    state: str
    load: float
    active_connections: int
    cpu_usage: float
    ram_usage: float
    timestamp: float

class UDPNASListener:

    def __init__(self, port: int = 9999):
        self.port = port
        self.running = False
        self.thread = None
        self.socket = None
        self.last_status: Optional[NASStatus] = None
        self.status_lock = threading.Lock()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"📡 UDP NAS Listener started on port {self.port}")

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()

    def _run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(("0.0.0.0", self.port))
            self.socket.settimeout(1.0)
            logger.info(f"✅ UDP listener ready on :{self.port}")

            while self.running:
                try:
                    data, addr = self.socket.recvfrom(4096)
                    self._handle_message(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"UDP receive error: {e}")

        except Exception as e:
            logger.error(f"UDP listener error: {e}")
        finally:
            if self.socket:
                self.socket.close()

    def _handle_message(self, data: bytes, addr: tuple):
        try:
            message = json.loads(data.decode('utf-8'))
            status = NASStatus(
                state=message.get("state", "unknown"),
                load=float(message.get("load", 0.0)),
                active_connections=int(message.get("connections", 0)),
                cpu_usage=float(message.get("cpu", 0.0)),
                ram_usage=float(message.get("ram", 0.0)),
                timestamp=now_ts(),
            )
            with self.status_lock:
                self.last_status = status
            logger.debug(f"📡 NAS status: {status.state} (load: {status.load:.2f}, conn: {status.active_connections})")
        except Exception as e:
            logger.error(f"Failed to parse UDP message: {e}")

    def get_status(self) -> Optional[NASStatus]:
        with self.status_lock:
            if self.last_status and (now_ts() - self.last_status.timestamp) < 60:
                return self.last_status
        return None

class UDPNASClient:

    def __init__(self, nas_ip: str, nas_port: int = 9999):
        self.nas_ip = nas_ip
        self.nas_port = nas_port

    def query_status(self) -> bool:
        try:
            message = json.dumps({"command": "status"})
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(message.encode('utf-8'), (self.nas_ip, self.nas_port))
            logger.debug(f"📤 Status query sent to NAS")
            return True
        except Exception as e:
            logger.error(f"UDP query failed: {e}")
            return False

    def send_command(self, command: str) -> bool:
        try:
            message = json.dumps({"command": command})
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(message.encode('utf-8'), (self.nas_ip, self.nas_port))
            logger.info(f"📤 Command sent to NAS: {command}")
            return True
        except Exception as e:
            logger.error(f"UDP command failed: {e}")
            return False

# =============================================================================
# STATE MANAGER (RAM-First & Asynchrone Persistenz)
# =============================================================================

class StateManager:
    """Erweiterter State Manager mit RAM-First Architektur."""

    def __init__(self):
        self.lock = threading.RLock()

        self.volatile = {
            "system_metrics": {
                "cpu_temp": 0.0,
                "cpu_usage": 0.0,
                "ram_usage": 0.0,
                "high_load_duration": 0,
            },
            "nas_status": {
                "online": False,
                "state": "unknown",
                "load": 0.0,
                "connections": 0,
            },
            "proxy_stats": {
                "active_connections": 0,
                "total_connections": 0,
            },
            "current_governor": "unknown",
            "devices_online": 0,
            "device_status": {},
            "user_location": {"kira": "unknown"},
            "current_zone": "unknown",
            "ha_status": {},
        }

        self.persistent = {
            "last_activity_ts": now_ts(),
            "total_wol": 0,
            "total_shutdowns": 0,
            "governor_performance": {},
            "ab_test_results": {},

            # NEU: Das erlernte "Gedulds-Level" (Startwert: 15 Minuten)
            "learned_idle_threshold": 15.0,
            # NEU: Wann wurde zuletzt geschlafen? (Für Lern-Check)
            "last_sleep_timestamp": 0.0,
        }

        # VOLATILE: NAS Event History (nicht persistent, nur für Dashboard)
        self.nas_events = deque(maxlen=50)  # Letzte 50 Events

        # Manual Override: Wenn User manuell eingreift
        self.manual_override_until = 0.0
        self.manual_override_action = None  # "wake" oder "sleep"

    def add_nas_event(self, event_type: str, source: str, details: str = ""):
        """Fügt ein NAS-Event zur History hinzu (wake/sleep/manual)"""
        event = {
            "time": datetime.now().strftime('%H:%M:%S'),
            "timestamp": now_ts(),
            "type": event_type,  # "wake", "sleep", "manual_suspend", "manual_wake"
            "source": source,   # "ai", "proxy", "user", "away_mode"
            "details": details,
        }
        self.nas_events.append(event)
        logger.info(f"📝 NAS Event: {event_type} by {source} - {details}")

    def get_nas_events(self) -> list:
        """Gibt NAS Event History zurück"""
        return list(self.nas_events)

    def set_manual_override(self, action: str, duration_minutes: int = 10):
        """Setzt Manual Override (User hat manuell eingegriffen)"""
        self.manual_override_until = now_ts() + (duration_minutes * 60)
        self.manual_override_action = action
        logger.warning(f"🛡️ Manual Override SET: {action} for {duration_minutes} minutes")

    def is_manual_override_active(self) -> bool:
        """Prüft ob Manual Override aktiv ist"""
        return now_ts() < self.manual_override_until

    def get_manual_override(self) -> Optional[str]:
        """Gibt aktuelle Override-Aktion zurück oder None"""
        if self.is_manual_override_active():
            return self.manual_override_action
        return None

    def _load(self):
        data = load_json_file(CONFIG["state_file"], {})
        with self.lock:
            for k, v in data.items():
                if k in self.persistent:
                    self.persistent[k] = v

    def save(self):
        """Delegiert die Speicherung an den asynchronen Schreiber."""
        with self.lock:
            data_copy = {k: v for k, v in self.persistent.items()}

        async_atomic_write_json(data_copy, CONFIG["state_file"])

    def update(self, key: str, value: Any, subkey: Optional[str] = None, persistent: bool = False):
        with self.lock:
            target = self.persistent if persistent else self.volatile
            if subkey:
                if key not in target:
                    target[key] = {}
                target[key][subkey] = value
            else:
                target[key] = value

    def set(self, key: str, value: Any, subkey: Optional[str] = None, persistent: bool = False):
        """Alias für update() - Kompatibilität mit externen Skills"""
        self.update(key, value, subkey, persistent)

    def get(self, key: str, subkey: Optional[str] = None, persistent: bool = False, default: Any = None) -> Any:
        with self.lock:
            target = self.persistent if persistent else self.volatile
            if subkey:
                return target.get(key, {}).get(subkey, default)
            return target.get(key, default)

    def snapshot(self) -> dict:
        with self.lock:
            snap = {}
            snap.update(self.volatile)
            snap.update(self.persistent)
            return snap

    def mark_activity(self):
        with self.lock:
            self.persistent["last_activity_ts"] = now_ts()

    def idle_minutes(self) -> float:
        with self.lock:
            return (now_ts() - self.persistent["last_activity_ts"]) / 60.0

state = StateManager()

# =============================================================================
# LAYER 1: SENSORS (Monitor, HA, Device, Proxy)
# =============================================================================

class SystemMonitor:

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("🔍 SystemMonitor started")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                # 1. Werte holen
                metrics = {
                    "cpu_temp": get_cpu_temp(),
                    "cpu_usage": get_cpu_usage(),
                    "ram_usage": get_ram_usage(),
                }

                # 2. LOGIK FÜR LAST-DAUER (Toleranz-Zähler)
                # Wir holen uns den aktuellen Zählerstand aus dem State
                current_duration = state.get("high_load_duration", default=0)

                # KORREKTUR: Wir lesen den Wert aus dem metrics-Dictionary!
                if metrics["cpu_usage"] > 20.0:
                    # Last hält an -> Zähler hochzählen (+3 Sekunden, da wir 3s schlafen)
                    # In SystemMonitor:
                    state.update("system_metrics", current_duration + 3, subkey="high_load_duration")
                else:
                    # Last ist weg -> Reset auf 0
                    state.update("high_load_duration", 0)

                # 3. State updaten
                state.update("system_metrics", metrics)
                time.sleep(3)

            except Exception as e:
                logger.error(f"SystemMonitor error: {e}")
                time.sleep(3)


# =============================================================================
# FIX 1: NasObserver - Entferne _observe(), füge AI am Ende von _run() hinzu
# =============================================================================

class NasObserver:
    def __init__(self, udp_listener: UDPNASListener, udp_client: UDPNASClient):
        self.udp_listener = udp_listener
        self.udp_client = udp_client
        self.running = False
        self.thread = None
        self.logger = logging.getLogger("NasObserver")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info("👁️  NasObserver started")

    def stop(self):
        self.running = False

    # ❌ LÖSCHE DIESE METHODE KOMPLETT:
    # def _observe(self):
    #     ... (Zeilen 1760-1785 löschen!)

    def _run(self):
        while self.running:
            try:
                # 1. UDP Abfrage
                self.udp_client.query_status()
                udp_status = self.udp_listener.get_status()

                # 2. Proxy Aktivität prüfen (Globaler Actor Check)
                proxy_active_count = 0
                if 'actors' in globals() and actors is not None:
                    proxy_active_count = actors.proxy_tracker.get_stats()["active_connections"]

                # --- ENTSCHEIDUNGSLOGIK ---
                if udp_status:
                    # FALL A: NAS meldet sich selbst via UDP (Idealfall)
                    total_connections = udp_status.active_connections + proxy_active_count
                    is_idle = udp_status.active_connections == 0 and udp_status.load < 0.1

                    state.update("nas_idle", is_idle and proxy_active_count == 0)
                    state.update("nas_status", {
                        "online": True,
                        "state": udp_status.state,
                        "load": udp_status.load,
                        "connections": total_connections,
                        "cpu": udp_status.cpu_usage,
                        "ram": udp_status.ram_usage,
                    })

                else:
                    # FALL B: Keine UDP Antwort -> Aktiver Check nötig
                    is_online = is_port_open(CONFIG["nas"]["ip"], 80, timeout=1.0)

                    # 🚀 SMART WAIT LOGIK
                    # Wenn Port zu ist, ABER Proxy Traffic hat (Wake Versuch läuft):
                    if not is_online and proxy_active_count > 0:
                        self.logger.info("⚠️ Traffic detected via Proxy. Polling NAS availability...")

                        # Anstatt 10s stur zu schlafen, prüfen wir 10x jede Sekunde
                        for i in range(10):
                            # Kurzer Check: Ist Port 80 oder 445 (SMB) jetzt offen?
                            if is_port_open(CONFIG["nas"]["ip"], 80, timeout=0.5) or \
                               is_port_open(CONFIG["nas"]["ip"], 445, timeout=0.5):
                                is_online = True
                                self.logger.info(f"✅ NAS came online after {i+1} seconds!")
                                break # Schleife sofort beenden!

                            time.sleep(1) # 1 Sekunde warten, dann nochmal gucken

                        # Wenn nach 10 Sekunden immer noch nichts da ist, versuchen wir den harten Ping
                        if not is_online:
                            try:
                                res = subprocess.call(
                                    ['ping', '-c', '1', '-W', '1', CONFIG["nas"]["ip"]],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL
                                )
                                if res == 0:
                                    is_online = True
                                    self.logger.info("✅ NAS confirmed ONLINE via Ping (Service ports still closed)")
                            except Exception:
                                pass

                        try:
                            # Sende 1 Ping Paket, Warte max 1 Sekunde auf Antwort
                            res = subprocess.call(
                                ['ping', '-c', '1', '-W', '1', CONFIG["nas"]["ip"]],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            if res == 0:
                                is_online = True
                                self.logger.info("✅ NAS confirmed ONLINE via Backup-Ping!")
                        except Exception as e:
                            self.logger.error(f"Backup Ping failed: {e}")

                    # Status Update nach Checks
                    if proxy_active_count > 0:
                        # Wenn Proxy Traffic hat, ist NAS "busy" (auch wenn es noch bootet)
                        state.update("nas_idle", False)
                    else:
                        state.update("nas_idle", not is_online)

                    state.update("nas_status", {
                        "online": is_online,
                        "state": "booting" if (is_online and proxy_active_count > 0) else ("unknown" if is_online else "offline"),
                        "load": 0.0,
                        "connections": proxy_active_count, # Zeige Proxy-Verbindungen an!
                    })

                time.sleep(3) # Zykluszeit

                # 🆕 AI LEARNING: Feed observation (AM ENDE!)
                if 'app' in globals() and app and hasattr(app, 'ai_integration'):
                    try:
                        snapshot = state.snapshot()
                        context = app.ai_integration.build_context(snapshot)

                        # Was the NAS actually used?
                        nas_was_used = (
                            state.get("nas_status", subkey="connections", default=0) > 0 or
                            state.get("nas_status", subkey="load", default=0.0) > 0.1
                        )

                        # Feed observation to Bayesian learner
                        app.ai_integration.observe(context, nas_was_used)

                    except Exception as e:
                        logger.debug(f"AI observation failed: {e}")

            except Exception as e:
                self.logger.error(f"NasObserver error: {e}")
                time.sleep(3)

class DeviceDetector:
    """Detect devices on network with presence pattern tracking"""

    def __init__(self, presence_engine: Optional[PresencePatternEngine] = None):
        self.running = False
        self.thread = None
        self.initial_scan_done = False

        # Presence Pattern Engine Integration
        self.presence_engine = presence_engine
        self._last_phone_status: Optional[bool] = None
        self._phone_device_key = "kira_phone"

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("📡 DeviceDetector started")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                count = self._scan()
                state.update("devices_online", count)

                if not self.initial_scan_done:
                    self.initial_scan_done = True
                    logger.info("✅ DeviceDetector: Initial network scan complete.")

                time.sleep(4)
            except Exception as e:
                logger.error(f"DeviceDetector error: {e}")
                time.sleep(4)

    def _scan(self) -> int:
        """Scannt konfigurierte IP-Geräte und updated den Gerätestatus."""
        online_count = 0
        device_status = {}

        device_list = CONFIG["zone_mapping"]["devices_to_scan"].items()

        for name, address in device_list:
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", address):
                logger.warning(f"Skipping non-IP address in scan: {name}")
                continue

            is_online = is_port_open(address, 80, timeout=0.1)
            if not is_online:
                try:
                    is_online = subprocess.call(['ping', '-c', '1', '-W', '1', address], stdout=subprocess.DEVNULL) == 0
                except Exception:
                    pass

            device_status[name + "_online"] = is_online
            if is_online:
                online_count += 1
                state.mark_activity()

            # Presence Pattern Tracking für Handy
            if name == self._phone_device_key and self.presence_engine:
                self._track_phone_presence(is_online)

        state.update("device_status", device_status)
        return online_count

    def _track_phone_presence(self, phone_online: bool):
        """Trackt Änderungen im Phone-Status für die PresencePatternEngine."""
        # Ersten Scan ignorieren (noch kein Vergleichswert)
        if self._last_phone_status is None:
            self._last_phone_status = phone_online
            return

        # Nur bei Statusänderung reagieren
        if phone_online != self._last_phone_status:
            if phone_online:
                # Handy ist zurück!
                result = self.presence_engine.on_return()
                analysis = result.get("analysis", {})
                comparison = analysis.get("comparison", "unknown")
                diff = abs(analysis.get("diff_minutes", 0))

                if comparison == "late":
                    logger.info(f"📱 User returned ({diff:.0f}min SPÄTER als normal)")
                elif comparison == "early":
                    logger.info(f"📱 User returned ({diff:.0f}min FRÜHER als normal)")
                else:
                    logger.info(f"📱 User returned (normale Zeit)")

                state.update("presence_user_home", True)
                state.update("presence_return_analysis", analysis)

            else:
                # Handy ist weg!
                result = self.presence_engine.on_departure()
                prediction = result.get("initial_prediction")

                if prediction and prediction.get("expected_return"):
                    logger.info(
                        f"📱 User left - Rückkehr erwartet: {prediction['expected_return_str']} "
                        f"(±{prediction['std_minutes']:.0f}min, Konfidenz: {prediction['confidence']:.0%})"
                    )
                    if prediction.get("week_trend") != "normal":
                        logger.info(f"   📊 Wochen-Trend: {prediction['week_trend']} ({prediction['week_adjustment_minutes']:+.0f}min)")
                else:
                    reason = prediction.get("reasoning", "Unbekannt") if prediction else "Keine Daten"
                    logger.info(f"📱 User left - Keine Vorhersage: {reason}")

                state.update("presence_user_home", False)
                state.update("presence_prediction", prediction)

            self._last_phone_status = phone_online


# =============================================================================
# UPGRADE: ProxyConnectionTracker (Thread-Safe + Throughput)
# =============================================================================

class ProxyConnectionTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.connections = {}
        self.connection_counter = 0

    def add_connection(self, client_addr: Tuple[str, int], target_port: int) -> int:
        """Fügt eine neue Verbindung hinzu und gibt die ID zurück."""
        with self.lock:
            self.connection_counter += 1
            conn_id = self.connection_counter

            self.connections[conn_id] = {
                "id": conn_id,
                "client_ip": client_addr[0],
                "client_port": client_addr[1],
                "target_port": target_port,
                "started": now_ts(),
                "bytes_sent": 0,
                "bytes_received": 0,
                "last_activity": now_ts(),
                "status": "active",
            }
            state.mark_activity()
            return conn_id

    def update_connection(self, conn_id: int, bytes_sent: int = 0, bytes_received: int = 0):
        """Aktualisiert Traffic-Daten einer Verbindung."""
        with self.lock:
            if conn_id in self.connections:
                conn = self.connections[conn_id]
                conn["bytes_sent"] += bytes_sent
                conn["bytes_received"] += bytes_received
                conn["last_activity"] = now_ts()
                state.mark_activity()

    def remove_connection(self, conn_id: int):
        """Markiert Verbindung als geschlossen und plant Bereinigung."""
        with self.lock:
            if conn_id in self.connections:
                self.connections[conn_id]["status"] = "closed"
                self.connections[conn_id]["ended"] = now_ts()

                # Asynchrone Bereinigung nach 10s, um History kurz zu halten
                def cleanup():
                    time.sleep(10)
                    with self.lock:
                        if conn_id in self.connections:
                            del self.connections[conn_id]

                threading.Thread(target=cleanup, daemon=True).start()

    def get_active_connections(self) -> List[dict]:
        """Gibt Liste aller aktiven Verbindungen zurück (für Dashboard)."""
        with self.lock:
            return [
                {
                    **conn,
                    "duration": now_ts() - conn["started"],
                    "idle_time": now_ts() - conn["last_activity"],
                }
                for conn in self.connections.values()
                if conn["status"] == "active"
            ]

    def get_stats(self) -> dict:
        """Gibt Statistiken inkl. aktuellem Durchsatz (MB/s) zurück."""
        with self.lock:
            active = [c for c in self.connections.values() if c["status"] == "active"]
            total_bytes = sum(c["bytes_sent"] + c["bytes_received"] for c in active)

            # PI 4 UPGRADE: Durchsatz berechnen (MB/s)
            throughput = 0.0
            now = now_ts()
            for c in active:
                duration = now - c["started"]
                if duration > 1.0: # Vermeide Division durch Null / ungenaue Werte bei Start
                    # Bytes pro Sekunde -> MB pro Sekunde
                    speed = ((c["bytes_sent"] + c["bytes_received"]) / duration) / (1024 * 1024)
                    throughput += speed

            return {
                "active_connections": len(active),
                "total_connections": self.connection_counter,
                "total_data_mb": total_bytes / (1024 * 1024),
                "throughput_mbs": throughput # Wichtig für Governor-Steuerung!
            }


    # =============================================================================
# FINALE VERSION: ProxyServer._handle_connection (mit Warteschleife)
# =============================================================================

class ProxyServer:

    def __init__(self, port: int, target_ip: str, target_port: int, tracker: ProxyConnectionTracker, adaptive_timing: 'AdaptiveProxyTiming' = None):
        self.port = port
        self.target_ip = target_ip
        self.target_port = target_port
        self.tracker = tracker
        self.adaptive_timing = adaptive_timing  # Adaptive Learning
        self.running = False
        self.thread = None
        self.server_socket = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"🔌 Proxy started: {self.port} → {self.target_ip}:{self.target_port}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def _run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((CONFIG["network"]["proxy_listen_ip"], self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            logger.info(f"✅ Proxy listening on :{self.port}")

            while self.running:
                try:
                    client_sock, client_addr = self.server_socket.accept()
                    logger.info(f"🔗 New connection from {client_addr}")

                    handler = threading.Thread(
                        target=self._handle_connection,
                        args=(client_sock, client_addr),
                        daemon=True
                    )
                    handler.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Proxy accept error: {e}")

        except Exception as e:
            logger.error(f"Proxy server error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def _handle_connection(self, client_sock: socket.socket, client_addr: Tuple[str, int]):
        """
        Handle connection mit 'Hold-the-Line' Feature:
        Hält die Verbindung zum Client offen, während das NAS geweckt wird.
        """
        target_sock = None
        conn_id = None

        try:
            # 1. Verbindung registrieren
            conn_id = self.tracker.add_connection(client_addr, self.target_port)

            # Definition der Warte-Parameter
            # ADAPTIVE: Verwende gelernte Timeouts wenn verfügbar
            if self.adaptive_timing:
                nas_is_online = state.get("nas_status", subkey="online", default=False)
                max_retries = self.adaptive_timing.get_optimal_timeout(nas_is_online)
                logger.info(f"🎯 Using adaptive timeout: {max_retries}s (NAS {'online' if nas_is_online else 'offline'})")
            else:
                max_retries = 40  # Fallback
            wol_sent = False

            # 2. Verbindungsschleife (Versuche NAS zu erreichen)
            for i in range(max_retries):
                try:
                    # Immer einen frischen Socket für jeden Versuch erstellen!
                    target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    target_sock.settimeout(2.0) # Kurzer Timeout pro Versuch

                    # Versuch: Verbinde zum NAS
                    target_sock.connect((self.target_ip, self.target_port))

                    # WENN ERFOLGREICH:
                    if i > 0:
                        logger.info(f"🚀 NAS connection established after {i}s wait!")
                    # ADAPTIVE LEARNING: Zeichne Erfolg auf
                    if self.adaptive_timing:
                        # TODO: Implement timing measurement
                        pass
                    break # Raus aus der Schleife, weiter zum Datentransfer

                except OSError as e:
                    # Fehlerbehandlung und Wake-Logik
                    target_sock.close() # Fehlgeschlagenen Socket schließen
                    target_sock = None

                    # Prüfen ob es ein Fehler ist, der auf "NAS aus" hindeutet
                    if e.errno in [113, 10065, 111, 110] or isinstance(e, socket.timeout):

                        # Nur beim ersten Fehlschlag WoL senden
                        if not wol_sent:
                            logger.warning(f"⚠️ Target unreachable. Holding connection & sending WoL...")
                            if 'actors' in globals() and actors is not None:
                                # COGNITIVE: Request wake through controller
                                if 'app' in globals() and app is not None and hasattr(app, 'cognitive_controller'):
                                    result = app.cognitive_controller.request_action(
                                        action="wake_nas",
                                        source="proxy",
                                        reason="client_waiting",
                                        priority=9,
                                        context={"client_addr": str(client_addr), "port": self.target_port}
                                    )
                                    if not result["approved"]:
                                        logger.warning(f"❌ Cognitive Controller rejected wake: {result['reason']}")
                                else:
                                    # Fallback wenn cognitive controller nicht verfügbar
                                    actors.nas.send_wol()
                                # Setze Status auf offline, damit Dashboard Bescheid weiß
                                state.update("nas_status", {"online": False, "state": "waking_up"}, subkey=None)
                            wol_sent = True

                        # Warte 1 Sekunde vor dem nächsten Versuch
                        time.sleep(1.0)
                    else:
                        # Bei anderen Fehlern (z.B. DNS kaputt) sofort abbrechen
                        raise e

            # Wenn nach 40 Versuchen immer noch kein target_sock da ist -> Aufgeben
            if target_sock is None:
                logger.error("❌ NAS did not wake up in time. Dropping connection.")
                return

            # ... (Ab hier: Erfolgreiche Weiterleitung, Code bleibt gleich) ...

            client_sock.setblocking(False)
            target_sock.setblocking(False)

            while self.running:
                readable, _, exceptional = select.select(
                    [client_sock, target_sock],
                    [],
                    [client_sock, target_sock],
                    1.0
                )

                if exceptional: break

                for sock in readable:
                    data = sock.recv(65536)
                    if not data: return

                    if sock is client_sock:
                        target_sock.sendall(data)
                        self.tracker.update_connection(conn_id, bytes_sent=len(data))
                    else:
                        client_sock.sendall(data)
                        self.tracker.update_connection(conn_id, bytes_received=len(data))

        except Exception as e:
            # logger.debug(f"Connection closed/error: {e}")
            pass
        finally:
            if client_sock: client_sock.close()
            if target_sock: target_sock.close()
            if conn_id is not None: self.tracker.remove_connection(conn_id)

# =============================================================================
# LAYER 2: WORLD MODEL (Sequence, PCA, Probabilistic)
# =============================================================================

class SequenceDetector:

    def __init__(self, seq_len: int = 5):
        self.seq_len = seq_len
        self.buffer = deque(maxlen=100)
        self.pattern_outcomes = defaultdict(list)
        self.state_file = str(DATA_DIR / "sequences.json")
        self._load()

    def observe(self, event: str):
        self.buffer.append({"event": event, "ts": now_ts()})
        if len(self.buffer) >= self.seq_len:
            seq = tuple(e["event"] for e in list(self.buffer)[-self.seq_len:])

    def observe_outcome(self, nas_used: bool):
        if len(self.buffer) >= self.seq_len:
            seq = tuple(e["event"] for e in list(self.buffer)[-self.seq_len:])
            self.pattern_outcomes[seq].append(1 if nas_used else 0)
            if len(self.pattern_outcomes[seq]) > 50:
                self.pattern_outcomes[seq] = self.pattern_outcomes[seq][-30:]

    def predict(self) -> Optional[float]:
        if len(self.buffer) < self.seq_len:
            return None
        seq = tuple(e["event"] for e in list(self.buffer)[-self.seq_len:])
        if seq not in self.pattern_outcomes or len(self.pattern_outcomes[seq]) < 3:
            return None
        outcomes = self.pattern_outcomes[seq]
        return sum(outcomes) / len(outcomes)

    def save(self):
        data = {"outcomes": {str(k): v for k, v in self.pattern_outcomes.items()}}
        async_atomic_write_json(data, self.state_file)

    def _load(self):
        data = load_json_file(self.state_file, {})
        if "outcomes" in data:
            for seq_str, outcomes in data["outcomes"].items():
                # SECURITY: Verwende ast.literal_eval statt eval um Code-Injection zu verhindern
                try:
                    seq = ast.literal_eval(seq_str)
                except (ValueError, SyntaxError) as e:
                    logger.warning(f"Konnte Pattern nicht parsen: {seq_str} - {e}")
                    continue
                self.pattern_outcomes[seq] = outcomes


    def set_meta_learner(self, meta_learner):
        """Setzt MetaLearner für Pattern Sharing"""
        self.meta_learner = meta_learner
        logger.info("🔗 SequenceDetector connected to MetaLearner")

class FeatureSelector:

    def __init__(self, n_components: int = 3):
        self.n_components = n_components
        self.use_pca = HAVE_NUMPY
        self.importance = {}

        if self.use_pca:
            self.mean = None
            self.components = None

    def fit(self, features: List[dict], targets: List[int]):
        if not features: return

        if not self.use_pca:
            feature_names = list(features[0].keys())
            for feat in feature_names:
                vals = [f.get(feat, 0) for f in features]
                used = [vals[i] for i in range(len(vals)) if targets[i] == 1]
                not_used = [vals[i] for i in range(len(vals)) if targets[i] == 0]

                if used and not_used:
                    self.importance[feat] = abs(statistics.mean(used) - statistics.mean(not_used))
        else:
            feat_names = sorted(features[0].keys())
            X = np.array([[f.get(n, 0) for n in feat_names] for f in features])

            self.mean = np.mean(X, axis=0)
            X_centered = X - self.mean
            cov = np.cov(X_centered.T)
            eigenvalues, eigenvectors = np.linalg.eig(cov)

            idx = eigenvalues.argsort()[::-1]
            self.components = eigenvectors[:, idx][:, :self.n_components]

    def transform(self, features: dict) -> dict:
        if not self.use_pca:
            if not self.importance: return features
            top = sorted(self.importance.items(), key=lambda x: x[1], reverse=True)[:self.n_components]
            return {name: features.get(name, 0) for name, _ in top}
        else:
            if self.components is None: return features
            feat_names = sorted(features.keys())
            x = np.array([features.get(n, 0) for n in feat_names])
            transformed = self.components.T @ (x - self.mean)
            return {f"PC{i+1}": float(transformed[i]) for i in range(self.n_components)}


# =============================================================================
# UPGRADE v10.0: HYBRID MEMORY (RAM + SD Archiving) - CLEAN VERSION
# =============================================================================

class ProbabilisticEngine:
    """v10.5: Pi 4 Edition - 14 Tage RAM, 24h Disk-Zyklus."""
    def __init__(self):
        # RAM (Short Term) - Jetzt 14 Tage!
        self.stm_nas = deque(); self.stm_no_nas = deque()
        self.retention = 14 * 24 * 3600 # 14 Tage in Sekunden

        # Timer für den SD-Schreib-Zyklus
        self.last_consolidation = time.time()

        # Disk (Long Term)
        self.ltm_file = str(BASE_DIR / "data" / "long_term_memory.json")
        self.ltm_data = {"total_nas": 0, "total_no_nas": 0, "feat_nas": defaultdict(int), "feat_no_nas": defaultdict(int)}
        self._load_ltm()

        self.sequence = SequenceDetector()
        self.learning_rate = CONFIG["learning"]["base_learning_rate"]
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()
        logger.info("🧠 ProbabilisticEngine (14-Day RAM Mode) started")

    def stop(self):
        # Beim Stop ALLES sichern (damit bei Reboot nichts verloren geht)
        self.running = False
        self._consolidate(force=True)
        self.sequence.save()

    def set_learning_rate(self, rate): self.learning_rate = max(0.01, min(1.0, rate))

    def _run(self):
        while self.running:
            try:
                self._learn() # Lernt jede Minute (RAM)

                # PI 4 OPTIMIERUNG: Nur alle 24 Stunden (86400s) auf SD schreiben!
                if time.time() - self.last_consolidation > 86400:
                    logger.info("💾 Daily Job: Consolidating Memory to SD Card...")
                    self._consolidate()
                    self.last_consolidation = time.time()

                time.sleep(3)
            except Exception as e: logger.error(f"Prob Error: {e}"); time.sleep(3)

    def _learn(self):
        ctx = self._build_context()
        conn = state.get("nas_status", subkey="connections")
        has_conn = (conn if conn else 0) > 0

        if state.get("nas_status", subkey="online"):
            ts = time.time()
            if has_conn:
                self.stm_nas.append((ts, ctx))
                self.sequence.observe_outcome(True)
            else:
                self.stm_no_nas.append((ts, ctx))
                self.sequence.observe_outcome(False)

        if has_conn: self.sequence.observe("nas_access")
        if state.get("devices_online") > 0: self.sequence.observe("devices_online")

    def _consolidate(self, force=False):
        # Verschiebt Daten, die älter als 14 Tage sind, ins Archiv
        # Wenn force=True (Shutdown), speichern wir den aktuellen Zustand
        limit = time.time() - self.retention
        save = False

        # Alte Daten aus RAM entfernen und in LTM backen
        while self.stm_nas and self.stm_nas[0][0] < limit:
            _, ctx = self.stm_nas.popleft()
            self._add_ltm(ctx, True); save = True
        while self.stm_no_nas and self.stm_no_nas[0][0] < limit:
            _, ctx = self.stm_no_nas.popleft()
            self._add_ltm(ctx, False); save = True

        if save or force: self._save_ltm()

    def _add_ltm(self, ctx, is_nas):
        if is_nas:
            self.ltm_data["total_nas"] += 1; target = self.ltm_data["feat_nas"]
        else:
            self.ltm_data["total_no_nas"] += 1; target = self.ltm_data["feat_no_nas"]
        for k, v in ctx.items():
            if isinstance(v, float): v = int(v)
            target[f"{k}={v}"] += 1

    def predict(self) -> float:
        ctx = self._build_context()
        c_nas = self.ltm_data["total_nas"] + len(self.stm_nas)
        c_no = self.ltm_data["total_no_nas"] + len(self.stm_no_nas)
        total = c_nas + c_no
        if total < 10: return 0.5

        prior = c_nas / total
        p_nas = 1.0; p_no = 1.0

        # Mehr Features für Pi 4
        keys = ["is_pc_on", "is_tv_on", "is_tablet_on", "is_weekend", "hour"]
        for k in keys:
            v = int(ctx.get(k, 0))
            fk = f"{k}={v}"
            m_nas = self.ltm_data["feat_nas"].get(fk, 0)
            m_no = self.ltm_data["feat_no_nas"].get(fk, 0)
            m_nas += sum(1 for _, c in self.stm_nas if int(c.get(k,0)) == v)
            m_no += sum(1 for _, c in self.stm_no_nas if int(c.get(k,0)) == v)
            p_nas *= (m_nas + 1) / (c_nas + 2)
            p_no *= (m_no + 1) / (c_no + 2)

        num = p_nas * prior
        res = num / (num + (p_no * (1 - prior)))
        seq = self.sequence.predict()
        if seq is not None: return (res * 0.8) + (seq * 0.2)
        return res

    def _build_context(self):
        now = datetime.now()
        dev = state.get("device_status", default={})
        return {
            "hour": now.hour,
            "is_weekend": 1 if now.weekday() >= 5 else 0,
            "is_pc_on": 1 if dev.get("workstation_pc_online") else 0,
            "is_tv_on": 1 if dev.get("tv_wohnzimmer_online") else 0,
            "is_tablet_on": 1 if dev.get("tablet_kira_online") else 0, # Extra Feature
        }

    def _save_ltm(self):
        d = {
            "total_nas": self.ltm_data["total_nas"],
            "total_no_nas": self.ltm_data["total_no_nas"],
            "feat_nas": dict(self.ltm_data["feat_nas"]),
            "feat_no_nas": dict(self.ltm_data["feat_no_nas"])
        }
        async_atomic_write_json(d, self.ltm_file)

    def _load_ltm(self):
        data = load_json_file(self.ltm_file, {})
        if "total_nas" in data:
            self.ltm_data["total_nas"] = data["total_nas"]
            self.ltm_data["total_no_nas"] = data["total_no_nas"]
            for k, v in data.get("feat_nas", {}).items(): self.ltm_data["feat_nas"][k] = v
            for k, v in data.get("feat_no_nas", {}).items(): self.ltm_data["feat_no_nas"][k] = v


class ContextualStateUpdater:
    """Wendet Expertenregeln an (Layer 2)"""

    def __init__(self):
        self.rules = CONFIG["context_rules"]
        self.running = False
        self.thread = None
        self.logger = logging.getLogger("ContextUpdater")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info("🧠 ContextualStateUpdater started.")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                self._update_user_location()
                time.sleep(3)
            except Exception as e:
                self.logger.error(f"Context updater error: {e}")
                time.sleep(3)

    def _update_user_location(self):
        """Überprüft Regeln und leitet die wahrscheinlichste Zone ab."""

        now_hour = datetime.now().hour
        derived_zone = "unknown"

        # 1. Priorität: Home Assistant Location (höchste Genauigkeit)
        now_hour = datetime.now().hour
        derived_zone = "unknown"

        # Hole HA Presence aus State
        snapshot = state.snapshot()
        ha_presence = snapshot.get("ha_presence", {})
        persons = ha_presence.get("persons", {})
        ha_location = state.get("user_location", subkey="kira", default="unknown")

        # Logik korrigiert:
        if ha_location != "unknown":
            derived_zone = ha_location
        elif ha_location == "home":
             derived_zone = "home"

        # 2. Priorität: Expertenregeln
        for rule in self.rules:
            start_h, end_h = rule["time_range"]
            is_time = (start_h <= now_hour < end_h) if start_h < end_h else (now_hour >= start_h or now_hour < end_h)

            if not is_time: continue

            conditions_met = True
            for cond_key, cond_val in rule["conditions"].items():

                if cond_key.endswith("_online"):
                    actual_val = state.get("device_status", subkey=cond_key, default=False)
                    if actual_val != cond_val:
                        conditions_met = False; break

                elif cond_key == "nas_connected":
                    actual_val = state.get("nas_status", subkey="connections", default=0) > 0
                    if actual_val != cond_val:
                        conditions_met = False; break

            if conditions_met:
                derived_zone = rule["result_zone"]
                self.logger.debug(f"Zone '{derived_zone}' abgeleitet durch Regel: {rule['name']}")
                break

        # 3. Update State
        state.update("user_location", derived_zone, subkey="kira")
        state.update("current_zone", derived_zone)

# =============================================================================
# LAYER 3: REASONING & PLANNING (Goals, Sandbox, MCDM, A/B)
# =============================================================================

@dataclass
class Goal:
    """Ein Ziel das das System verfolgt"""
    name: str
    weight: float
    current_value: float
    target_value: float

    def satisfaction(self) -> float:
        if self.target_value == 0:
            return 1.0
        return min(1.0, self.current_value / self.target_value)

    def utility(self) -> float:
        return self.satisfaction() * self.weight


class GoalManager:
    """Verwaltet alle Ziele (inkl. Intrinsic Motivation)"""

    def __init__(self):
        self.goals = {}
        self._init_goals()
        self.goal_history = defaultdict(lambda: deque(maxlen=100))

    def _init_goals(self):
        goal_config = CONFIG["goals"]

        self.goals["energy_saving"] = Goal(name="energy_saving", weight=goal_config["energy_saving"]["weight"], current_value=0.0, target_value=goal_config["energy_saving"]["target_idle_power"])
        self.goals["responsiveness"] = Goal(name="responsiveness", weight=goal_config["responsiveness"]["weight"], current_value=0.0, target_value=goal_config["responsiveness"]["target_latency_ms"])
        self.goals["stability"] = Goal(name="stability", weight=goal_config["stability"]["weight"], current_value=0.0, target_value=goal_config["stability"]["min_uptime_hours"])
        self.goals["learning"] = Goal(name="learning", weight=goal_config["learning"]["weight"], current_value=0.0, target_value=1.0)
        self.goals["user_comfort"] = Goal(name="user_comfort", weight=goal_config["user_comfort"]["weight"], current_value=0.0, target_value=goal_config["user_comfort"]["target_value"])
        self.goals["curiosity"] = Goal(name="curiosity", weight=goal_config["curiosity"]["weight"], current_value=0.0, target_value=goal_config["curiosity"]["target_information_gain"])

    def update_goal(self, goal_name: str, current_value: float):
        if goal_name in self.goals:
            self.goals[goal_name].current_value = current_value
            self.goal_history[goal_name].append({"value": current_value, "satisfaction": self.goals[goal_name].satisfaction(), "timestamp": now_ts()})

    def get_total_utility(self) -> float:
        return sum(goal.utility() for goal in self.goals.values())

    def get_goal_priorities(self) -> List[Tuple[str, float]]:
        """
        Sortierte Liste von Zielen nach Dringlichkeit.
        Unerfüllte Ziele sind dringender.
        """
        priorities = []
        for goal in self.goals.values():
            # Dringlichkeit = Gewicht * (1 - Erfüllung)
            urgency = goal.weight * (1.0 - goal.satisfaction())
            priorities.append((goal.name, urgency))

        priorities.sort(key=lambda x: x[1], reverse=True)
        return priorities

    def calculate_information_gain(self, probabilistic_engine: ProbabilisticEngine) -> float:
        # Prior aus den Daten berechnen
        total_nas = len(probabilistic_engine.stm_nas) + probabilistic_engine.ltm_data["total_nas"]
        total_no = len(probabilistic_engine.stm_no_nas) + probabilistic_engine.ltm_data["total_no_nas"]
        total = total_nas + total_no

        p = total_nas / total if total > 0 else 0.5

        if p == 0 or p == 1:
            gain = 0.0
        else:
            entropy = - (p * math.log2(p) + (1 - p) * math.log2(1 - p))
            gain = entropy  # max entropy = 1.0

        self.goals["curiosity"].current_value = gain
        return gain


# =============================================================================
# LAYER 3: REASONING & PLANNING (World State & Sandbox)
# =============================================================================

class WorldState:
    def __init__(self):
        self.nas_online = False
        self.nas_state = "idle"
        self.cpu_temp = 0.0
        self.cpu_governor = "ondemand"
        self.active_connections = 0
        self.devices_online = 0
        self.idle_minutes = 0.0
        self.power_consumption = 0.0
        self.response_latency = 0.0
        self.uptime_hours = 0.0

    def copy(self) -> 'WorldState':
        new_state = WorldState()
        new_state.__dict__ = self.__dict__.copy()
        return new_state

    @staticmethod
    def from_current() -> 'WorldState':
        ws = WorldState()
        ws.nas_online = state.get("nas_status", subkey="online", default=False)
        ws.nas_state = state.get("nas_status", subkey="state", default="idle")
        ws.cpu_temp = state.get("system_metrics", subkey="cpu_temp", default=0.0)
        ws.cpu_governor = state.get("current_governor", default="ondemand")

        # WICHTIG: Hier holen wir die ECHTE Summe der Verbindungen (NAS + Proxy)
        # Der NasObserver schreibt das bereits korrekt in "nas_status.connections"
        ws.active_connections = state.get("nas_status", subkey="connections", default=0)

        ws.devices_online = state.get("devices_online", default=0)
        ws.idle_minutes = state.idle_minutes()
        ws.power_consumption = ws._estimate_power()
        ws.response_latency = ws._estimate_latency()
        return ws

    def _estimate_power(self) -> float:
        base_power = 2.0
        gov_props = CONFIG["cpu_governors"]["properties"].get(self.cpu_governor, {})
        cpu_power = 3.0 * (1.0 - gov_props.get("energy", 0.5))
        nas_power = 15.0 if self.nas_online else 0.0
        return base_power + cpu_power + nas_power

    def _estimate_latency(self) -> float:
        gov_props = CONFIG["cpu_governors"]["properties"].get(self.cpu_governor, {})
        base_latency = 100.0 * (1.0 - gov_props.get("speed", 0.5))
        if not self.nas_online:
            base_latency += 50.0
        return base_latency

class SandboxSimulator:
    def __init__(self, goal_manager: GoalManager):
        self.goal_manager = goal_manager
        self.simulation_depth = CONFIG["learning"]["sandbox_depth"]

    def plan_best_action(self, available_actions: List[str]) -> Tuple[str, float]:
        current_world = WorldState.from_current()
        best_action = None
        best_utility = -float('inf')

        for action in available_actions:
            predicted_utility = self._simulate_action_chain(current_world, [action], depth=self.simulation_depth)

            if predicted_utility > best_utility:
                best_utility = predicted_utility
                best_action = action

        # logger.debug(f"🤔 Sandbox: Best action '{best_action}' (utility: {best_utility:.3f})")
        return best_action, best_utility

    def _simulate_action_chain(self, world: WorldState, actions: List[str], depth: int) -> float:
        if depth == 0 or not actions:
            return self._evaluate_world_state(world)

        action = actions[0]
        simulated_world = self._apply_action(world.copy(), action)

        remaining_actions = actions[1:]
        return self._simulate_action_chain(simulated_world, remaining_actions, depth - 1)

    def _apply_action(self, world: WorldState, action: str) -> WorldState:
        if action == "nas_wake":
            world.nas_online = True; world.nas_state = "idle"
            world.response_latency = max(50, world.response_latency - 30)
            world.power_consumption += 15.0
        elif action == "nas_sleep":
            world.nas_online = False; world.nas_state = "sleeping"
            world.response_latency += 50.0
            world.power_consumption = max(0, world.power_consumption - 15.0)
        elif action.startswith("set_governor_"):
            governor = action.replace("set_governor_", "")
            world.cpu_governor = governor
            world.power_consumption = world._estimate_power()
            world.response_latency = world._estimate_latency()
        elif action == "wait":
            world.idle_minutes += 5.0
        return world

    def _evaluate_world_state(self, world: WorldState) -> float:
        """
        Bewerte einen World State.
        Hier sitzt die Intelligenz: Abwägung zwischen Sparen und Verbindungsabbruch.
        """
        utility = 0.0

        # 1. Energy Goal
        energy_goal = self.goal_manager.goals["energy_saving"]
        energy_sat = 1.0 - (min(world.power_consumption, 30.0) / 30.0)
        utility += energy_sat * energy_goal.weight

        # 2. Responsiveness Goal
        resp_goal = self.goal_manager.goals["responsiveness"]
        resp_sat = 1.0 - (min(world.response_latency, 200.0) / 200.0)
        utility += resp_sat * resp_goal.weight

        # 3. Stability Goal
        stab_goal = self.goal_manager.goals["stability"]
        stab_sat = 1.0 if world.nas_online and world.nas_state == "idle" else 0.5
        utility += stab_sat * stab_goal.weight

        # 4. User Comfort & Curiosity
        curiosity_goal = self.goal_manager.goals["curiosity"]
        comfort_goal = self.goal_manager.goals["user_comfort"]
        utility += comfort_goal.utility()

        # --- INTELLIGENZ-REGELN (Strafen) ---

        # A: "Connection Drop Penalty" (Das allerwichtigste!)
        # Wenn NAS aus ist, aber Traffic da war -> Katastrophe (-0.8)
        if not world.nas_online and world.active_connections > 0:
            utility -= 0.8

        # B: "Impatience Penalty" (Gedulds-Lernen)
        # Wenn NAS aus ist, aber wir die "gelernte Wartezeit" noch nicht erreicht haben
        learned_threshold = state.get("learned_idle_threshold", persistent=True, default=15.0)
        if not world.nas_online and world.idle_minutes < learned_threshold:
            # Strafe proportional dazu, wie viel zu früh wir sind
            penalty_factor = (learned_threshold - world.idle_minutes) / learned_threshold
            utility -= (penalty_factor * 0.5)

        # Neugierde-Bonus (wenn Utility sonst niedrig ist)
        if utility < 0.5:
             utility += curiosity_goal.weight * 0.5

        return max(0.0, min(1.0, utility))

class MCDMGovernorSelector:

    def __init__(self):
        self.governors = CONFIG["cpu_governors"]["available"]
        self.properties = CONFIG["cpu_governors"]["properties"]
        self.performance_history = defaultdict(lambda: {"avg_temp": [], "avg_load": [], "stability_score": []})
        self.state_file = str(DATA_DIR / "governor_performance.json")
        self._load()

        self.meta_learner = None
    def select_best_governor(self, context: dict) -> str:
        scores = {}
        for governor in self.governors:
            if governor not in self.properties: continue
            props = self.properties[governor]
            load = context.get("load", 0.5)
            temp = context.get("temp", 50.0)
            priority = context.get("priority", "balanced")

            if priority == "energy": weights = {"speed": 0.2, "energy": 0.6, "stability": 0.2}
            elif priority == "performance": weights = {"speed": 0.6, "energy": 0.1, "stability": 0.3}
            else: weights = {"speed": 0.4, "energy": 0.3, "stability": 0.3}

            if load > 0.7: weights["speed"] *= 1.5; weights["energy"] *= 0.7
            if temp > 70.0: weights["energy"] *= 1.5; weights["speed"] *= 0.7

            total_weight = sum(weights.values())
            weights = {k: v / total_weight for k, v in weights.items()}

            score = sum(props.get(criterion, 0.5) * weight for criterion, weight in weights.items())
            history_bonus = self._get_history_bonus(governor)
            score *= (1.0 + history_bonus)
            scores[governor] = score

        best_gov = max(scores.items(), key=lambda x: x[1])
        logger.debug(f"🎯 MCDM Governor scores: {scores}")
        logger.debug(f"🎯 Selected: {best_gov[0]} (score: {best_gov[1]:.3f})")
        return best_gov[0]

    def record_performance(self, governor: str, metrics: dict):
        self.performance_history[governor]["avg_temp"].append(metrics.get("temp", 0))
        self.performance_history[governor]["avg_load"].append(metrics.get("load", 0))
        self.performance_history[governor]["stability_score"].append(metrics.get("stability", 1.0))
        for key in self.performance_history[governor]:
            if len(self.performance_history[governor][key]) > 100:
                self.performance_history[governor][key] = self.performance_history[governor][key][-50:]

    def _get_history_bonus(self, governor: str) -> float:
        if governor not in self.performance_history: return 0.0
        history = self.performance_history[governor]
        temps = history["avg_temp"]
        if temps:
            avg_temp = statistics.mean(temps[-20:])
            temp_bonus = max(0, (70.0 - avg_temp) / 100.0)
        else: temp_bonus = 0.0
        stability = history["stability_score"]
        if stability:
            stab_bonus = statistics.mean(stability[-20:]) * 0.1
        else: stab_bonus = 0.0
        return min(0.2, temp_bonus + stab_bonus)

    def save(self):
        data = {
            gov: {k: list(v) for k, v in metrics.items()}
            for gov, metrics in self.performance_history.items()
        }
        async_atomic_write_json(data, self.state_file)

    def _load(self):
        data = load_json_file(self.state_file, {})
        for gov, metrics in data.items():
            for key, values in metrics.items():
                self.performance_history[gov][key] = values



    def set_meta_learner(self, meta_learner):
        """Setzt MetaLearner für Knowledge Sharing"""
        self.meta_learner = meta_learner
        logger.info("🔗 MCDM connected to MetaLearner")

class ABTest:

    def __init__(self, name: str, variant_a: str, variant_b: str):
        self.name = name
        self.variant_a = variant_a
        self.variant_b = variant_b
        self.a_trials = 0
        self.a_successes = 0
        self.b_trials = 0
        self.b_successes = 0
        self.started = now_ts()
        self.completed = False

    def select_variant(self) -> str:
        alpha_a = self.a_successes + 1
        beta_a = (self.a_trials - self.a_successes) + 1
        sample_a = random.betavariate(alpha_a, beta_a)

        alpha_b = self.b_successes + 1
        beta_b = (self.b_trials - self.b_successes) + 1
        sample_b = random.betavariate(alpha_b, beta_b)

        return self.variant_a if sample_a > sample_b else self.variant_b

    def record_outcome(self, variant: str, success: bool):
        if variant == self.variant_a:
            self.a_trials += 1
            if success: self.a_successes += 1
        else:
            self.b_trials += 1
            if success: self.b_successes += 1

    def get_winner(self, confidence: float = 0.95) -> Optional[str]:
        if self.a_trials < 20 or self.b_trials < 20: return None
        rate_a = self.a_successes / self.a_trials if self.a_trials > 0 else 0
        rate_b = self.b_successes / self.b_trials if self.b_trials > 0 else 0
        if abs(rate_a - rate_b) > 0.1:
            return self.variant_a if rate_a > rate_b else self.variant_b
        return None

    def to_dict(self) -> dict:
        return {"name": self.name, "variant_a": self.variant_a, "variant_b": self.variant_b, "a_trials": self.a_trials, "a_successes": self.a_successes, "b_trials": self.b_trials, "b_successes": self.b_successes, "started": self.started, "completed": self.completed,}

    @staticmethod
    def from_dict(data: dict) -> 'ABTest':
        test = ABTest(data["name"], data["variant_a"], data["variant_b"])
        test.a_trials = data.get("a_trials", 0); test.a_successes = data.get("a_successes", 0)
        test.b_trials = data.get("b_trials", 0); test.b_successes = data.get("b_successes", 0)
        test.started = data.get("started", now_ts()); test.completed = data.get("completed", False)
        return test

class ABTestManager:

    def __init__(self):
        self.active_tests = {}
        self.completed_tests = {}
        self.state_file = str(DATA_DIR / "ab_tests.json")
        self._load()
        if CONFIG["learning"]["ab_testing_enabled"] and not self.active_tests:
            self._create_default_tests()

    def _create_default_tests(self):
        self.create_test("wake_threshold", "threshold_0.60", "threshold_0.70")
        self.create_test("governor_strategy", "always_ondemand", "adaptive_mcdm")

    def create_test(self, name: str, variant_a: str, variant_b: str):
        if name not in self.active_tests:
            self.active_tests[name] = ABTest(name, variant_a, variant_b)
            logger.info(f"🔬 A/B Test created: {name} ({variant_a} vs {variant_b})")

    def get_variant(self, test_name: str) -> Optional[str]:
        if test_name in self.active_tests:
            return self.active_tests[test_name].select_variant()
        return None

    def record_outcome(self, test_name: str, variant: str, success: bool):
        if test_name in self.active_tests:
            self.active_tests[test_name].record_outcome(variant, success)
            winner = self.active_tests[test_name].get_winner()
            if winner:
                logger.info(f"🏆 A/B Test '{test_name}' completed! Winner: {winner}")
                self.active_tests[test_name].completed = True
                self.completed_tests[test_name] = self.active_tests[test_name]
                del self.active_tests[test_name]

    def save(self):
        data = {
            "active": {name: test.to_dict() for name, test in self.active_tests.items()},
            "completed": {name: test.to_dict() for name, test in self.completed_tests.items()},
        }
        async_atomic_write_json(data, self.state_file)

    def _load(self):
        data = load_json_file(self.state_file, {})
        if "active" in data:
            for name, test_data in data["active"].items():
                self.active_tests[name] = ABTest.from_dict(test_data)
        if "completed" in data:
            for name, test_data in data["completed"].items():
                self.completed_tests[name] = ABTest.from_dict(test_data)

# =============================================================================
# LAYER 4: GOAL-ORIENTED ACTION PLANNING (GOAP)
# =============================================================================

@dataclass
class Action:
    """Eine ausführbare Aktion"""
    name: str
    preconditions: Dict[str, Any]
    effects: Dict[str, Any]
    cost: float

    def can_execute(self, world_state: dict) -> bool:
        for key, required_value in self.preconditions.items():
            if world_state.get(key) != required_value:
                return False
        return True

    def apply_effects(self, world_state: dict) -> dict:
        new_state = world_state.copy()
        new_state.update(self.effects)
        return new_state

class GOAPPlanner:
    """Goal-Oriented Action Planning."""

    def __init__(self):
        self.actions = self._define_actions()

    def _define_actions(self) -> List[Action]:
        """Definiere verfügbare Aktionen (inkl. HA-Steuerung)"""
        return [
            # NAS Control
            Action(name="nas_wake", preconditions={"nas_online": False}, effects={"nas_online": True, "power_high": True}, cost=5.0,),
            Action(name="nas_sleep", preconditions={"nas_online": True, "nas_idle": True}, effects={"nas_online": False, "power_low": True}, cost=3.0,),

            # Governor Control
            Action(name="set_governor_performance", preconditions={}, effects={"cpu_fast": True, "power_high": True}, cost=2.0,),
            Action(name="set_governor_powersave", preconditions={}, effects={"cpu_slow": True, "power_low": True}, cost=2.0,),
            Action(name="set_governor_ondemand", preconditions={}, effects={"cpu_adaptive": True, "power_medium": True}, cost=1.0,),

            # Zone Heating/Light Control (HA Actors)
            Action(
                name="set_wohnzimmer_heating_low",
                preconditions={"user_location": "schlafzimmer", "time_is_night": True},
                effects={"thermostat_wohnzimmer_low": True, "energy_low": True},
                cost=3.0,
            ),
            Action(
                name="set_wohnzimmer_heating_high",
                preconditions={"user_location": "wohnzimmer", "wohnzimmer_temp_low": True},
                effects={"thermostat_wohnzimmer_high": True, "energy_medium": True},
                cost=8.0,
            ),
            Action(
                name="light_on_küche",
                preconditions={"user_location": "küche", "is_dark": True, "küche_light_off": True},
                effects={"küche_light_on": True},
                cost=1.0,
            ),

            # Wait (nichts tun)
            Action(name="wait", preconditions={}, effects={"time_passed": True}, cost=0.5,),
        ]

    def plan(self, current_state: dict, goal_state: dict) -> Optional[List[str]]:
        node_id = 0  # ← 8 Leerzeichen Einrückung!
        start_node = (0, node_id, current_state, [])
        frontier = [start_node]
        explored = set()

        max_iterations = 100
        iterations = 0

        while frontier and iterations < max_iterations:
            iterations += 1
            _, _, current, action_seq = heapq.heappop(frontier)  # ← 4 Werte!

            if self._goal_satisfied(current, goal_state):
                logger.debug(f"🎯 GOAP: Plan found with {len(action_seq)} actions")
                return action_seq

            state_hash = self._hash_state(current)
            if state_hash in explored: continue
            explored.add(state_hash)

            for action in self.actions:
                if action.can_execute(current):
                    new_state = action.apply_effects(current)
                    new_actions = action_seq + [action.name]

                    g_cost = sum(a.cost for a in self.actions if a.name in new_actions)
                    h_cost = self._heuristic(new_state, goal_state)
                    f_cost = g_cost + h_cost

                    node_id += 1  # ← 20 Leerzeichen Einrückung!
                    heapq.heappush(frontier, (f_cost, node_id, new_state, new_actions))

        logger.warning("🎯 GOAP: No plan found")
        return None

    def _goal_satisfied(self, state: dict, goal: dict) -> bool:
        for key, required_value in goal.items():
            if state.get(key) != required_value: return False
        return True

    def _hash_state(self, state: dict) -> str:
        return str(sorted(state.items()))

    def _heuristic(self, state: dict, goal: dict) -> float:
        distance = 0
        for key, required_value in goal.items():
            if state.get(key) != required_value:
                distance += 1
        return distance

# =============================================================================
# LAYER 5: META DECISION ENGINE (Predictive Processing & Causal Learning)
# =============================================================================

class MetaDecisionEngine:
    """Orchestriert alle Entscheidungs-Komponenten."""

    def __init__(self, probabilistic_engine, goal_manager, sandbox, mcdm, ab_testing, goap):
        self.prob = probabilistic_engine
        self.goals = goal_manager
        self.sandbox = sandbox
        self.mcdm = mcdm
        self.ab_testing = ab_testing
        self.goap = goap
        self.governor_ai = GovernorAI(DATA_DIR)
        self.nas_ai = NasAI(DATA_DIR)

        self.last_nas_decision_state = None
        self.last_nas_decision_time = 0
        self.last_gov_state = None
        self.last_gov_action = None
        self.running = False
        self.thread = None
        self.last_decision = None
        self.last_decision_time = 0.0
        self.decision_history = deque(maxlen=100)

        self.current_plan = []
        self.plan_index = 0
        self.last_predicted_prob = None

                # 🆕 AI Integration Reference
        self.ai_integration = None  # Will be set by Application

        # Stats & History
        self.decision_history = deque(maxlen=100)

        # NEU: Per-Action Cooldowns (in Sekunden)
        self.action_cooldowns = {
            "nas_wake": 120,      # 2 Minuten zwischen Wakes
            "nas_sleep": 300,     # 5 Minuten zwischen Sleeps
            "governor": 60,       # 1 Minute zwischen Governor-Wechseln
        }
        self.last_action_times = {
            "nas_wake": 0.0,
            "nas_sleep": 0.0,
            "governor": 0.0,
        }

        # NEU: Delayed Evaluation (warte auf NAS Boot)
        self.pending_evaluation = None  # {"action": str, "time": float, "predicted_prob": float}

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("🧠 MetaDecisionEngine started")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                self._think_and_act()
                time.sleep(3)
            except Exception as e:
                logger.error(f"Meta decision error: {e}", exc_info=True)
                time.sleep(3)

    def _learn_from_mistakes(self, action: str):
        """Reinforcement Learning: Bestraft zu frühes Schlafenlegen."""

        # Fall 1: Wir wecken das NAS (manuell oder durch Traffic)
        if action == "nas_wake":
            last_sleep = state.get("last_sleep_timestamp", persistent=True, default=0.0)
            time_since_sleep = (now_ts() - last_sleep) / 60.0 # in Minuten

            # Wenn das NAS vor weniger als 60 Minuten schlafen gelegt wurde, war es wohl zu früh!
            if time_since_sleep < 60.0 and time_since_sleep > 0.5: # >0.5 um "Flackern" zu ignorieren
                logger.warning(f"🎓 LEARNING: NAS was woken up too soon ({time_since_sleep:.1f}m after sleep)!")

                # BESTRAFUNG: Erhöhe den Schwellenwert drastisch (+10 Minuten)
                current_threshold = state.get("learned_idle_threshold", persistent=True, default=15.0)
                new_threshold = min(120.0, current_threshold + 10.0) # Max 2 Stunden

                state.update("learned_idle_threshold", new_threshold, persistent=True)
                logger.info(f"🎓 ADJUSTMENT: I will be more patient. New Idle Threshold: {new_threshold:.1f} min")
                state.save()

        # Fall 2: Wir legen das NAS schlafen
        elif action == "nas_sleep":
            # Speichere den Zeitpunkt des Schlafens für spätere Prüfung
            state.update("last_sleep_timestamp", now_ts(), persistent=True)
            state.save()

        # Fall 3: Belohnung (Langsames Vergessen / Optimierung)
        # Wenn lange nichts passiert ist, können wir den Threshold langsam wieder senken (Energie sparen)
        # Dies passiert einfach periodisch (z.B. bei 'wait')
        elif action == "wait":
            current_threshold = state.get("learned_idle_threshold", persistent=True, default=15.0)
            if current_threshold > 10.0:
                # Ganz langsamer Zerfall: -0.01 Minute pro Tick (ca -1 Min alle 25 Minuten)
                state.update("learned_idle_threshold", current_threshold - 0.01, persistent=True)

    def _evaluate_last_action(self, actual_outcome: bool):
        """
        Predictive Processing: Bewertet die letzte NAS-Aktion, berechnet die Überraschung und passt die Lernrate an.
        """
        if self.last_decision is None or self.last_predicted_prob is None:
            return

        expected_prob = self.last_predicted_prob
        surprise = abs((1 if actual_outcome else 0) - expected_prob)

        # 1. Learning Rate Anpassung (Höhere Surprise = schnelleres Lernen)
        # FIX: Learning Rate CAPPEN auf max 0.5 (war vorher unbegrenzt!)
        raw_rate = CONFIG["learning"]["base_learning_rate"] + (surprise * CONFIG["learning"]["surprise_factor"])
        new_rate = min(0.5, max(0.01, raw_rate))  # Zwischen 0.01 und 0.5
        self.prob.set_learning_rate(new_rate)

        logger.info(f"🧠 PP: Action '{self.last_decision}' | Expected P={expected_prob:.2f} | Actual={actual_outcome} | Surprise={surprise:.2f} | New Rate={new_rate:.2f}")

        # 2. Causal Learning (bei hoher Überraschung)
        if surprise > 0.4:
            logger.warning(f"💥 CAUSAL SURPRISE: Aktion {self.last_decision} hatte unerwarteten Ausgang. System passt das kausale Modell an.")

        self.last_predicted_prob = None

        # Im MetaDecisionEngine oder wo immer Entscheidungen getroffen werden:
    def _make_decision(self) -> Optional[str]:
        """
        Make decision using AI predictions.
        Führt Bayesian + Q-Learning aus und speichert Ergebnisse im State.
        """
        if not self.ai_integration:
            return None

        try:
            # 1. Build context from current state
            snapshot = state.snapshot()
            context = self.ai_integration.build_context(snapshot)
            universal_state = self.ai_integration.build_universal_state(snapshot, context)

            # 2. Get Bayesian prediction for NAS usage
            ai_prediction = self.ai_integration.predict(context)
            bayesian_prob = ai_prediction.get('bayesian', {}).get('probability', 0.5)
            ensemble_prob = ai_prediction.get('ensemble', bayesian_prob)

            # 3. Get Q-Learning action recommendation
            available_actions = [
                UniversalAction.NAS_WAKE,
                UniversalAction.NAS_SLEEP,
                UniversalAction.NAS_KEEP_ONLINE,
                UniversalAction.NAS_KEEP_OFFLINE,
                UniversalAction.DO_NOTHING,
            ]
            recommended_action, confidence = self.ai_integration.get_recommended_action(
                universal_state,
                available_actions
            )

            # 4. Log prediction
            logger.info(f"🤖 AI Prediction: NAS usage prob={bayesian_prob:.2%}, "
                       f"Ensemble={ensemble_prob:.2%}, "
                       f"Recommended={recommended_action.value} (confidence={confidence:.2%})")

            # 5. Store in state for dashboard
            state.update("ai_prediction", {
                "nas_usage_prob": bayesian_prob,
                "ensemble_prob": ensemble_prob,
                "recommended_action": recommended_action.value,
                "confidence": confidence,
                "timestamp": now_ts(),
            })

            # 6. Store for later evaluation
            self.last_predicted_prob = ensemble_prob

            return recommended_action.value

        except Exception as e:
            logger.warning(f"AI prediction failed: {e}")
            return None

    def _manage_skills(self):
        """Ruft periodisch die tick()-Methode aller registrierten Skills auf."""
        skill_manager = app.skill_manager

        for name, skill in skill_manager.skills.items():
            if skill.enabled:
                try:
                    skill.tick()
                except Exception as e:
                    logger.error(f"Skill '{name}' tick failed: {e}")

    def _check_holo_commands(self):
        """Prüft und verarbeitet Holo Brain Befehle"""
        if 'app' not in globals() or app is None:
            return

        if not hasattr(app, 'holo_interface'):
            return

        try:
            # Kontext für Holo zusammenstellen
            snapshot = state.snapshot()
            context = {
                "system_metrics": snapshot.get("system_metrics", {}),
                "nas_status": snapshot.get("nas_status", {}),
                "current_governor": snapshot.get("current_governor", "unknown"),
                "nas_in_use": snapshot.get("nas_status", {}).get("connections", 0) > 0,
                "device_status": snapshot.get("device_status", {}),
                "current_zone": snapshot.get("current_zone", "unknown"),
            }

            # Holo-Befehle prüfen
            results = app.holo_interface.check_and_execute(context)

            # Status an Holo senden
            app.holo_interface.send_status({
                "healthy": True,
                "uptime": time.time(),
                "last_decision": self.last_decision,
                "nas_online": snapshot.get("nas_status", {}).get("online", False),
            })

        except Exception as e:
            logger.debug(f"Holo check failed: {e}")


    def _think_and_act(self):
        """Haupt-Denkschleife"""
        # 🛡️ INTELLIGENTER START-CHECK
        # Wir greifen auf die globale Instanz 'app' zu, um den Sensor zu prüfen.
        # Wenn der DeviceDetector noch nie lief, wissen wir nicht, ob jemand zu Hause ist.
        # Also: Keine Entscheidungen treffen!
        if 'app' in globals() and app is not None:
            if not app.device_detector.initial_scan_done:
                # Optional: Einmalig loggen, damit man weiß, warum nichts passiert
                # logger.debug("⏳ Waiting for initial device scan...")
                return

            # 🏠 PRESENCE ENGINE TICK
            # Prüft ob User ungewöhnlich lange zuhause ist → Frei-Tag/Home-Office Erkennung
            if hasattr(app, 'presence_engine') and app.presence_engine:
                pc_online = state.get("device_status", subkey="workstation_pc_online", default=False)
                app.presence_engine.tick(pc_online=pc_online)

        # 🛡️ MANUAL OVERRIDE CHECK
        # Wenn User manuell eingegriffen hat, respektiere das!
        override = state.get_manual_override()
        if override:
            remaining = int((state.manual_override_until - now_ts()) / 60)
            logger.debug(f"🛡️ Manual Override active: {override} ({remaining}min remaining). Skipping NAS decisions.")
            # Trotzdem Governor und Skills managen
            self._manage_governor()
            self._manage_skills()
            return

        # 0.1 DELAYED EVALUATION (warte 2 Minuten nach Wake, nicht 15s!)
        if self.pending_evaluation:
            elapsed = now_ts() - self.pending_evaluation["time"]
            if elapsed >= 120:  # 2 Minuten warten
                # Jetzt erst evaluieren
                actual_outcome = state.get("nas_status", subkey="connections", default=0) > 0
                # Auch UDP-Status berücksichtigen
                nas_state = state.get("nas_status", subkey="state", default="unknown")
                if nas_state == "busy":
                    actual_outcome = True

                self.last_predicted_prob = self.pending_evaluation["predicted_prob"]
                self.last_decision = self.pending_evaluation["action"]
                self._evaluate_last_action(actual_outcome)
                self.pending_evaluation = None

        # 1. Update Goal Status (inkl. Curiosity/Information Gain)
        self._update_goals()

        # 🆕 2. AI DECISION MAKING (NEU!)
        self._make_decision()

        # 3. Governor Management (MCDM)
        self._manage_governor()

        # 4. Zonen-Aktionen (Heizung, Licht)
        self._manage_zone_comfort()

        # 5. NAS Management (Probabilistic + GOAP)
        self._manage_nas()

        # 6. Skill Management
        self._manage_skills() # Aufruf am Ende der Denkschleife

        # 7. HOLO BRAIN: Befehle prüfen und ausführen
        self._check_holo_commands()

    def _manage_zone_comfort(self):
        """Leitet Aktionen basierend auf der Zone ab (Heuristik/GOAP)."""
        current_zone = state.get("current_zone", default="unknown")

        if current_zone == "schlafzimmer":
            self.goals.update_goal("user_comfort", 0.9)

            # GOAP-Check für Heizung/Licht
            current_state = {"user_location": "schlafzimmer", "time_is_night": True}
            goal_state = {"thermostat_wohnzimmer_low": True}

            plan = self.goap.plan(current_state, goal_state)
            if plan:
                 logger.info(f"🎯 GOAP Plan (Schlafzimmer): {' → '.join(plan)}")
                 self.current_plan = plan
                 self.plan_index = 0

            if state.get("nas_status", subkey="online"):
                self._execute_action("nas_sleep")

        elif current_zone == "wohnzimmer":
            self.goals.update_goal("user_comfort", 0.8)
            pass

            # Beispiel GOAP für Wohnzimmer

        elif current_zone == "küche" and datetime.now().hour in range(18, 20):
            self.goals.update_goal("user_comfort", 0.7)

            current_state = {"user_location": "küche", "is_dark": True, "küche_light_off": True}
            goal_state = {"küche_light_on": True}

            if self.goap.plan(current_state, goal_state):
                 self._execute_action("light_on_küche")


    def _update_goals(self):
        """Update aktuelle Goal-Werte (inkl. Curiosity)"""

        # Energy (Proxy)
        power = state.get("system_metrics", subkey="cpu_temp", default=50) / 10.0
        self.goals.update_goal("energy_saving", power)

        # Responsiveness (basierend auf Governor)
        gov = state.get("current_governor", default="ondemand")
        gov_props = CONFIG["cpu_governors"]["properties"].get(gov, {})
        resp = gov_props.get("speed", 0.5) * 100
        self.goals.update_goal("responsiveness", resp)

        # Stability (Uptime basiert)
        self.goals.update_goal("stability", 12.0)

        # Learning (Anzahl Observations)
        obs_count = (
            len(self.prob.stm_nas) + len(self.prob.stm_no_nas) +
            self.prob.ltm_data["total_nas"] + self.prob.ltm_data["total_no_nas"])
        learning_progress = min(1.0, obs_count / 200.0)
        self.goals.update_goal("learning", learning_progress)

        # User Comfort
        is_responsive = state.get("system_metrics", subkey="cpu_usage", default=100) < 50
        comfort_score = 0.0
        if state.get("current_zone") == "schlafzimmer": comfort_score = 1.0
        elif is_responsive: comfort_score = 0.7
        self.goals.update_goal("user_comfort", comfort_score)

        # Curiosity/Information Gain
        self.goals.calculate_information_gain(self.prob)

    def _manage_governor(self):
        # 1. DATEN SAMMELN
        load = state.get("system_metrics", subkey="cpu_usage", default=0)
        temp = state.get("system_metrics", subkey="cpu_temp", default=50)
        throughput = 0.0
        if 'actors' in globals() and actors:
            throughput = actors.proxy_tracker.get_stats().get("throughput_mbs", 0.0)

        # Last-Dauer Tracker (aus vorherigem Code)
        if load < 20:
            state.update("low_load_duration", state.get("low_load_duration", default=0) + 3)
            state.update("high_load_duration", 0)
        else:
            state.update("low_load_duration", 0)
            state.update("high_load_duration", state.get("high_load_duration", default=0) + 3)

        duration = max(state.get("low_load_duration", 0), state.get("high_load_duration", 0))

        # 2. LERNEN VOM LETZTEN SCHRITT
        # Wir schauen uns an, wie gut die letzte Entscheidung war
        if self.last_gov_state and self.last_gov_action:
            reward = self.governor_ai.calculate_reward(self.last_gov_action, load, throughput, duration)
            self.governor_ai.learn(self.last_gov_state, self.last_gov_action, reward, load, duration)

            # Speichern (asynchron, alle 10 Schritte z.B.)
            if random.random() < 0.1:
                threading.Thread(target=self.governor_ai.save, daemon=True).start()

        # 3. SICHERHEITSNETZ (Hard Constraints überstimmen die KI)
        # Überhitzungsschutz hat immer Vorrang
        current_gov = state.get("current_governor")
        if temp > 75.0:
            if current_gov != "powersave":
                logger.warning(f"🔥 Safety Override: Overheat ({temp}°C) -> Powersave")
                self._execute_action("set_governor_powersave", source="safety")
            return

        # 4. KI ENTSCHEIDUNG
        # Wir fragen die KI: "Bei aktueller Last und Dauer, was soll ich tun?"
        proposed_action = self.governor_ai.choose_action(load, duration)

        # Merken für den nächsten Lern-Schritt
        self.last_gov_state = self.governor_ai.get_state_key(load, duration)
        self.last_gov_action = proposed_action

        # 5. AUSFÜHREN (Wenn Änderung nötig)
        if proposed_action != current_gov:
            # Kleiner Filter gegen Mikro-Flackern (KI ändert Meinung sekündlich)
            if (now_ts() - self.last_action_times.get("governor", 0)) > 30:
                logger.info(f"🤖 AI Governor: Switching to {proposed_action} (Load: {load}%, State: {self.last_gov_state})")
                self._execute_action(f"set_governor_{proposed_action}", source="ai_governor")


    def decide_nas_action(self, context: dict) -> dict:
        """
        GOAP-basierte NAS Entscheidung mit Constraints
        """
        try:
            # 1. Define Goal based on context
            if context["zone"] == "active_use" and not context["nas_online"]:
                # 🟢 FIX: Verwende 'nas_online' statt 'nas_available'
                # 🟢 FIX: Entferne 'power_cost': 'low', da Wecken immer Energie kostet!
                goal_state = {"nas_online": True}

            elif context["nas_online"] and context["idle_minutes"] > 10:
                # Hier wollen wir Strom sparen (NAS aus)
                goal_state = {"nas_online": False} # Action nas_sleep liefert nas_online: False
            else:
                return {"success": True, "action": None, "reason": "no_change_needed"}

            # 2. GOAP Planning
            current_goap_state = {
                "nas_online": context["nas_online"], # 🟢 FIX: Konsistente Benennung
                "user_present": context["zone"] != "away",
                # "predicted_usage": context["predicted_usage"], # Nicht zwingend nötig für den simplen Plan
            }

            plan = self.goap.plan(current_goap_state, goal_state)

            if not plan:
                return {"success": False, "reason": "no_plan_found", "action": None}

            # 3. Evaluate Plan with Goals
            total_utility = self.goals.get_total_utility()
            confidence = min(1.0, max(0.0, total_utility))

            # 4. Extract Action
            action = plan[0] if plan else None

            return {
                "success": True,
                "action": action,
                "confidence": confidence,
                "reason": "goap_planned",
                "plan": plan
            }

        except Exception as e:
            logger.error(f"GOAP planning failed: {e}")
            return {"success": False, "reason": str(e), "action": None}


    def _manage_nas(self):
        """
        AI MANAGED: Entscheidet über NAS Power State.
        Keine künstlichen Cooldowns mehr - vertraut auf NAS 'busy' State.
        """
        # 1. HARD CONSTRAINTS (VETO POWER!)
        nas_online = state.get("nas_status", subkey="online", default=False)
        nas_state = state.get("nas_status", subkey="state", default="unknown")

        throughput = 0.0
        active_conns = 0
        if 'actors' in globals() and actors:
            stats = actors.proxy_tracker.get_stats()
            throughput = stats.get("throughput_mbs", 0.0)
            active_conns = stats.get("active_connections", 0)

        # Busy Check (Das ist jetzt dein "echter" Cooldown!)
        # Solange das NAS "busy" meldet, tun wir NICHTS.
        if nas_state == "busy" or throughput > 0.1 or active_conns > 0:
            if not nas_online and (throughput > 0.1 or active_conns > 0):
                logger.info(f"🚨 HARD CONSTRAINT: Traffic detected. Waking NAS.")
                self._execute_action("nas_wake", source="traffic_veto")
            return

        # Away Mode Check
        current_zone = state.get("current_zone", default="unknown")
        if current_zone == "away":
            if nas_online:
                self._execute_action("nas_sleep", source="away_mode")
            return

        # (Hier war früher der Cooldown-Block - jetzt gelöscht)

        # 2. AI DECISION
        if nas_online:
            idle_minutes = state.idle_minutes()
            now = datetime.now()

            action = self.nas_ai.choose_action(now.hour, now.weekday(), idle_minutes)
            state_key = self.nas_ai.get_state_key(now.hour, now.weekday(), idle_minutes)

            # Status für Dashboard merken
            self.last_nas_decision_state = state_key

            if action == "sleep":
                logger.info(f"🤖 NAS AI: Decided to sleep (Idle: {idle_minutes:.1f}m, State: {state_key})")

                state.update("ai_sleep_decision", {
                    "timestamp": now_ts(),
                    "state_key": state_key,
                    "idle_at_sleep": idle_minutes
                }, persistent=True)

                self._execute_action("nas_sleep", source="nas_ai")

            elif action == "wait":
                # Kleines Feedback für Energieverbrauch beim Warten
                self.nas_ai.learn(state_key, "wait", -0.1)

        else:
            # Proactive Wake Check
            prob = self.prob.predict()
            if prob > 0.85:
                 logger.info(f"🤖 NAS AI: Proactive Wake (Probability {prob:.2%})")
                 self._execute_action("nas_wake", source="ai_prediction")


    def _learn_from_wake_event(self, wake_source):
        """
        Analysiert beim Aufwachen, ob das vorherige Schlafenlegen eine gute Idee war.
        """
        last_decision = state.get("ai_sleep_decision", persistent=True)
        if not last_decision:
            return

        sleep_time = last_decision.get("timestamp", 0)
        state_key = last_decision.get("state_key")

        # Wie lange haben wir geschlafen?
        duration_minutes = (now_ts() - sleep_time) / 60.0

        reward = 0.0

        # BEWERTUNG:
        if duration_minutes < 15:
            # KATASTROPHE: NAS hat geschlafen und wurde < 15 Min später geweckt.
            # User musste warten + Boot-Verschleiß.
            reward = -20.0
            logger.warning(f"🎓 NAS AI Learning: Bad decision! Slept only {duration_minutes:.1f} min. Punishment: -20")

        elif duration_minutes < 60:
            # Naja: War okay, aber Grenzwertig. Kleiner Bonus für Energie.
            reward = 2.0

        else:
            # SUPER: Hat > 1 Stunde geschlafen. Viel Energie gespart.
            # Bonus wächst mit der Dauer (max 10 Punkte)
            reward = min(10.0, 2.0 + (duration_minutes / 60.0))
            logger.info(f"🎓 NAS AI Learning: Good sleep ({duration_minutes:.1f} min). Reward: {reward:.1f}")

        # Lernen!
        self.nas_ai.learn(state_key, "sleep", reward)

        # Daten löschen, damit wir nicht doppelt lernen
        state.update("ai_sleep_decision", None, persistent=True)

        # Speichern
        threading.Thread(target=self.nas_ai.save, daemon=True).start()

    def _execute_action(self, action: str, source: str = "ai"):
        """
        COGNITIVE VERSION: Alle Actions gehen durch CognitiveController
        """
        logger.info(f"⚡ Decision Engine wants to execute: {action} (source: {source})")

        # 1. NAS Actions → Cognitive Controller
        if action == "nas_wake":
            # 🟢 NEU: Lernen, ob das letzte Schlafenlegen schlecht war
            # Wir rufen das VOR dem Wecken auf, um den Schlafzyklus zu bewerten
            self._learn_from_wake_event(source)

            if 'app' in globals() and app is not None and hasattr(app, 'cognitive_controller'):
                result = app.cognitive_controller.request_action(
                    action="wake_nas",
                    source=source,
                    reason="decision_engine_request",
                    priority=7,
                    context={"predicted_prob": self.last_predicted_prob}
                )
                if result["approved"]:
                    self.last_action_times["nas_wake"] = now_ts()
                    # Setup Delayed Evaluation (für MetaLearner)
                    if self.last_predicted_prob is not None:
                        self.pending_evaluation = {
                            "action": action,
                            "time": now_ts(),
                            "predicted_prob": self.last_predicted_prob,
                        }
                else:
                    logger.warning(f"❌ Cognitive Controller rejected: {result['reason']}")
                    return
            else:
                # Fallback: Direct execution (wenn Controller nicht da ist)
                actors.nas.send_wol(source)
                self.last_action_times["nas_wake"] = now_ts()

        elif action == "nas_sleep":
            if 'app' in globals() and app is not None and hasattr(app, 'cognitive_controller'):
                result = app.cognitive_controller.request_action(
                    action="sleep_nas",
                    source=source,
                    reason="decision_engine_request",
                    priority=6,
                    context={}
                )
                if result["approved"]:
                    self.last_action_times["nas_sleep"] = now_ts()
                else:
                    logger.warning(f"❌ Cognitive Controller rejected: {result['reason']}")
                    return
            else:
                # Fallback
                actors.nas.request_shutdown(source)
                self.last_action_times["nas_sleep"] = now_ts()

        elif action.startswith("set_governor_"):
            gov = action.replace("set_governor_", "")
            actors.power.set_governor(gov)
            self.last_action_times["governor"] = now_ts()

        # HA Actor-Delegation
        elif action == "set_wohnzimmer_heating_low":
            actors.ha.set_heating_temp("wohnzimmer", 18.0)
        elif action == "set_wohnzimmer_heating_high":
            actors.ha.set_heating_temp("wohnzimmer", 21.0)
        elif action == "light_on_küche":
            actors.ha.turn_on_light("küche")

        self.last_decision = action
        self.last_decision_time = now_ts()

        # Das hier ist die ALTE Lernmethode für den Threshold (kann bleiben als Backup)
        self._learn_from_mistakes(action)

        self.decision_history.append({"action": action, "timestamp": now_ts(), "goals": self.goals.get_total_utility()})

    def get_status(self) -> dict:
        """Liefert Status-Daten für das Dashboard"""
        return {
            "last_decision": self.last_decision,
            "last_decision_time": self.last_decision_time,
            # GOAP Infos
            "current_plan": self.current_plan,
            "plan_progress": f"{self.plan_index}/{len(self.current_plan)}" if self.current_plan else "0/0",
            # Goal Infos
            "total_utility": self.goals.get_total_utility(),
            "goal_priorities": self.goals.get_goal_priorities(),
            # History
            "decision_history": list(self.decision_history)[-10:],
            # AI Stats (Neu)
            "ai_governor_state": self.last_gov_state,
            "ai_nas_state": getattr(self, 'last_nas_decision_state', 'unknown')
        }
# =============================================================================
# LAYER 6: ACTORS (NAS, Power, HA)
# =============================================================================

class NasActor:
    def __init__(self, udp_client: UDPNASClient):
        self.udp_client = udp_client

    # ✅ Bestehende Methoden bleiben
    def send_wol(self, source: str = "ai") -> bool:
        """Sendet WoL und loggt Event"""
        success = send_wol(CONFIG["zone_mapping"]["mac_addresses"]["nas"])
        if success:
            state.update("total_wol", state.get("total_wol", persistent=True, default=0) + 1, persistent=True)
            state.add_nas_event("wake", source, f"WoL sent to {CONFIG['nas']['ip']}")
            state.save()

            # 🆕 AI REWARD
            self._report_ai_reward("wake_nas", success, source)
        return success

    def request_shutdown(self, source: str = "ai") -> bool:
        """Sendet Shutdown-Request via UDP und loggt Event"""
        success = self.udp_client.send_command("suspend")
        if success:
            state.update("total_shutdowns", state.get("total_shutdowns", persistent=True, default=0) + 1, persistent=True)
            state.add_nas_event("sleep", source, "UDP suspend command sent")
            state.save()

            # 🆕 AI REWARD
            self._report_ai_reward("suspend_nas", success, source)
        return success

    def force_shutdown_ssh(self, source: str = "away_mode") -> bool:
        """Erzwingt Shutdown via SSH und loggt Event"""
        success = send_ssh_command(
            CONFIG["nas"]["ip"],
            CONFIG["nas"]["ssh_user"],
            CONFIG["nas"]["ssh_key"],
            "sudo systemctl suspend"
        )
        if success:
            state.update("total_shutdowns", state.get("total_shutdowns", persistent=True, default=0) + 1, persistent=True)
            state.add_nas_event("force_sleep", source, "SSH force suspend executed")
            state.save()

            # 🆕 AI REWARD
            self._report_ai_reward("force_suspend_nas", success, source)
        return success

    # 🆕 NEUE HELPER-METHODE für AI Rewards
    def _report_ai_reward(self, action: str, success: bool, source: str):
        """Reports action result to AI system"""
        if 'app' in globals() and app and hasattr(app, 'ai_integration'):
            try:
                snapshot = state.snapshot()
                context = app.ai_integration.build_context(snapshot)
                universal_state = app.ai_integration.build_universal_state(snapshot, context)

                app.ai_integration.report_action_result(
                    universal_state,
                    success=success,
                    reward_details={
                        'action': action,
                        'source': source,
                        'reward': 1.0 if success else -0.5
                    }
                )
            except Exception as e:
                logger.debug(f"AI reward feedback failed: {e}")


class PowerActor:
    def __init__(self):
        self.refresh()

    def refresh(self):
        try:
            # Lesen darf jeder
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r") as f:
                gov = f.read().strip()
                state.update("current_governor", gov)
                return gov
        except Exception:
            return "unknown"

    def set_governor(self, governor: str) -> bool:
        # 1. Verfügbare Governors prüfen
        if governor not in self.get_available_governors():
            logger.warning(f"Governor {governor} not supported by CPU.")
            return False

        success = True

        # 2. Alle CPU-Dateien finden
        cpu_files = list(Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_governor"))

        if not cpu_files:
            logger.error("No CPU governor files found!")
            return False

        # 3. DIREKT SCHREIBEN (mit Capabilities statt sudo)
        for gov_file in cpu_files:
            try:
                # Direkt schreiben - funktioniert mit CAP_DAC_OVERRIDE
                with open(str(gov_file), 'w') as f:
                    f.write(governor + '\n')
                    f.flush()
                logger.debug(f"Set governor on {gov_file} to {governor}")

            except PermissionError as e:
                logger.error(f"Permission denied for {gov_file}: {e}")
                logger.error("Make sure CAP_DAC_OVERRIDE is set in systemd service")
                success = False
            except Exception as e:
                logger.error(f"Failed to write to {gov_file}: {e}")
                success = False

        if success:
            logger.info(f"⚡ Governor set to: {governor}")
            self.refresh()
            return True

        return False

    def get_available_governors(self) -> List[str]:
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors", "r") as f:
                return f.read().strip().split()
        except Exception:
            return CONFIG["cpu_governors"]["available"]


class HomeAssistantActor:
    """Steuert Smart Home Entitäten via HA API."""

    def __init__(self):
        self.ha_config = CONFIG["home_assistant"]
        self.actors_config = CONFIG["actors"]
        self.headers = {'Authorization': f'Bearer {self.ha_config["api_token"]}', 'content-type': 'application/json'}
        self.logger = logging.getLogger("HA_Actor")

    def _call_service(self, domain: str, service: str, entity_name: str, data: dict = {}) -> bool:
        """Generische Funktion zum Aufruf eines HA Services."""
        if not HAVE_REQUESTS or not self.ha_config["enabled"]:
            self.logger.warning(f"HA Actor disabled or requests missing.")
            return False

        url = f"{self.ha_config['api_url']}/services/{domain}/{service}"

        entity_id = None
        for category in self.actors_config.values():
            if entity_name in category:
                entity_id = category[entity_name]
                break

        if not entity_id:
            self.logger.error(f"Entity name '{entity_name}' not found in CONFIG['actors'].")
            return False

        payload = {"entity_id": entity_id}
        payload.update(data)

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=5)
            response.raise_for_status()
            self.logger.info(f"✅ HA: Service '{domain}.{service}' called for {entity_id}.")
            return True
        except Exception as e:
            self.logger.error(f"HA Service call failed for {entity_id}: {e}")
            return False

    def set_heating_temp(self, name: str, temp: float) -> bool:
        """Setzt die Zieltemperatur eines Thermostats."""
        return self._call_service(domain="climate", service="set_temperature", entity_name=name, data={"temperature": temp})

    def turn_on_light(self, name: str) -> bool:
        """Schaltet ein Licht ein."""
        return self._call_service(domain="light", service="turn_on", entity_name=name)

    def turn_off_light(self, name: str) -> bool:
        """Schaltet ein Licht aus."""
        return self._call_service(domain="light", service="turn_off", entity_name=name)

    def toggle_light(self, name: str) -> bool:
        """Schaltet ein Licht um."""
        return self._call_service(domain="light", service="toggle", entity_name=name)

    def set_light_brightness(self, name: str, brightness_pct: int) -> bool:
        """Setzt Helligkeit eines Lichts (0-100%)."""
        return self._call_service(
            domain="light", service="turn_on", entity_name=name,
            data={"brightness_pct": max(0, min(100, brightness_pct))}
        )

    def turn_on_switch(self, name: str) -> bool:
        """Schaltet einen Switch/Steckdose ein."""
        return self._call_service(domain="switch", service="turn_on", entity_name=name)

    def turn_off_switch(self, name: str) -> bool:
        """Schaltet einen Switch/Steckdose aus."""
        return self._call_service(domain="switch", service="turn_off", entity_name=name)

    def toggle_switch(self, name: str) -> bool:
        """Schaltet einen Switch um."""
        return self._call_service(domain="switch", service="toggle", entity_name=name)

    def open_cover(self, name: str) -> bool:
        """Öffnet eine Abdeckung (Rollladen, etc.)."""
        return self._call_service(domain="cover", service="open_cover", entity_name=name)

    def close_cover(self, name: str) -> bool:
        """Schließt eine Abdeckung."""
        return self._call_service(domain="cover", service="close_cover", entity_name=name)

    def set_cover_position(self, name: str, position: int) -> bool:
        """Setzt Position einer Abdeckung (0=geschlossen, 100=offen)."""
        return self._call_service(
            domain="cover", service="set_cover_position", entity_name=name,
            data={"position": max(0, min(100, position))}
        )

    def get_entities(self) -> list:
        """Holt alle verfügbaren Entities aus Home Assistant."""
        if not HAVE_REQUESTS or not self.ha_config["enabled"]:
            return []

        url = f"{self.ha_config['api_url']}/states"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"HA get_entities failed: {e}")
            return []

    def get_entity_state(self, entity_id: str) -> dict:
        """Holt Status einer bestimmten Entity."""
        if not HAVE_REQUESTS or not self.ha_config["enabled"]:
            return {}

        url = f"{self.ha_config['api_url']}/states/{entity_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"HA get_entity_state failed: {e}")
            return {}

    def create_calendar_event(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        description: str = "",
        location: str = ""
    ) -> bool:
        """
        Erstellt einen Kalender-Eintrag in Home Assistant.

        Args:
            summary: Titel des Termins
            start_datetime: Start-Zeit im ISO 8601 Format (z.B. "2025-12-23T15:00:00")
            end_datetime: End-Zeit im ISO 8601 Format
            description: Optionale Beschreibung
            location: Optionaler Ort

        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not HAVE_REQUESTS or not self.ha_config["enabled"]:
            self.logger.warning("HA Actor disabled or requests missing.")
            return False

        url = f"{self.ha_config['api_url']}/services/calendar/create_event"

        # Kalender Entity-ID (fest konfiguriert)
        entity_id = "calendar.kalender"

        payload = {
            "entity_id": entity_id,
            "summary": summary,
            "start_date_time": start_datetime,
            "end_date_time": end_datetime
        }

        if description:
            payload["description"] = description
        if location:
            payload["location"] = location

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=5)
            response.raise_for_status()
            self.logger.info(f"✅ HA: Kalender-Event '{summary}' erstellt ({start_datetime})")
            return True
        except Exception as e:
            self.logger.error(f"HA Calendar create failed: {e}")
            return False


class ActorContainer:
    """Container for all actors"""

    def __init__(self, udp_client: UDPNASClient):
        self.nas = NasActor(udp_client)
        self.power = PowerActor()
        self.ha = HomeAssistantActor()

        self.proxy_tracker = ProxyConnectionTracker()
        self.adaptive_timing = AdaptiveProxyTiming()  # Adaptive Learning
        self.proxies = []

        for port in CONFIG["network"]["proxy_ports"]:
            proxy = ProxyServer(
                port,
                CONFIG["nas"]["ip"],
                port,
                self.proxy_tracker,
                self.adaptive_timing  # Adaptive Learning
            )
            self.proxies.append(proxy)

    def start_all(self):
        for proxy in self.proxies:
            proxy.start()
        logger.info("🎬 All actors started")

    def stop_all(self):
        for proxy in self.proxies:
            proxy.stop()

# Global actors instance
actors = None

# =============================================================================
# SKILL SYSTEM
# =============================================================================

class SkillResult:
    """Ergebnis einer Skill-Ausführung für Holo"""
    def __init__(self, success: bool, data: Any = None, message: str = "",
                 error: str = None, metadata: Dict = None):
        self.success = success
        self.data = data  # Ergebnis-Daten (z.B. Bild-URL, Text, etc.)
        self.message = message  # Menschenlesbare Nachricht für Holo
        self.error = error  # Fehlermeldung falls nicht erfolgreich
        self.metadata = metadata or {}  # Zusätzliche Metadaten

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "metadata": self.metadata
        }


class SkillBase:
    """Base class for skills mit HTML-Support und Holo-Integration"""

    # ========== HOLO METADATEN (Optional - für Skill Discovery) ==========
    # Überschreibe diese in deinem Skill für Holo-Integration
    description: str = ""  # Was macht der Skill? (für Holo verständlich)
    keywords: List[str] = []  # Trigger-Wörter ["bild", "male", "zeichne"]
    capabilities: List[str] = []  # Fähigkeiten ["image_generation", "art"]
    examples: List[str] = []  # Beispiel-Anfragen ["Male mir eine Katze"]
    category: str = "general"  # Kategorie: "creative", "info", "control", etc.

    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.logger = logging.getLogger(f"skill.{name}")
        # Holo-spezifisch
        self._execution_count = 0
        self._success_count = 0

    def setup(self, context: dict):
        self.context = context

    def tick(self):
        pass

    def shutdown(self):
        pass

    def get_ui(self) -> dict:
        """
        Standard: Gibt nichts zurück.
        Kann von Skills überschrieben werden.
        Muss zurückgeben: {'tab': 'HTML Button', 'content': 'HTML Div'}
        """
        return None

    # ========== HOLO INTEGRATION (Optional - überschreiben für Holo-Support) ==========

    def can_handle(self, request: str) -> float:
        """
        Prüft ob dieser Skill die Anfrage bearbeiten kann.
        Returns: Confidence 0.0 - 1.0

        Standard-Implementierung prüft keywords.
        Überschreibe für intelligentere Erkennung.
        """
        if not self.keywords:
            return 0.0

        request_lower = request.lower()
        matches = sum(1 for kw in self.keywords if kw.lower() in request_lower)

        if matches == 0:
            return 0.0

        # Mehr Keyword-Matches = höhere Confidence
        confidence = min(0.3 + (matches * 0.2), 0.95)
        return confidence

    async def execute(self, intent: str, params: Dict = None) -> SkillResult:
        """
        Führt den Skill aus - ÜBERSCHREIBE DIESE METHODE!

        Args:
            intent: Was der User will (z.B. "male ein bild von einer katze")
            params: Extrahierte Parameter (z.B. {"subject": "katze", "style": "anime"})

        Returns:
            SkillResult mit Erfolg/Fehler und Daten
        """
        return SkillResult(
            success=False,
            error=f"Skill '{self.name}' hat execute() nicht implementiert"
        )

    def get_holo_info(self) -> Dict:
        """Gibt Skill-Informationen für Holo's Discovery zurück"""
        return {
            "name": self.name,
            "description": self.description or f"Skill: {self.name}",
            "keywords": self.keywords,
            "capabilities": self.capabilities,
            "examples": self.examples,
            "category": self.category,
            "enabled": self.enabled,
            "holo_compatible": bool(self.description and self.keywords),
            "success_rate": (self._success_count / self._execution_count * 100)
                           if self._execution_count > 0 else 0
        }

    def _track_execution(self, success: bool):
        """Trackt Ausführungen für Lernzwecke"""
        self._execution_count += 1
        if success:
            self._success_count += 1

    def load_html_from_file(self, filename: str) -> str:
        """Hilfsfunktion: Lädt HTML aus einer Datei im 'skills' Ordner"""
        try:
            # Pfad: ./skills/deine_datei.html
            path = Path(__file__).parent / "skills" / filename
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                self.logger.error(f"HTML file not found: {path}")
                return f"<div class='card'>Error: {filename} missing</div>"
        except Exception as e:
            self.logger.error(f"Error loading HTML: {e}")
            return ""

class SkillManager:
    """Manages skills with enable/disable and dynamic loading"""

    def __init__(self):
        self.skills = {}
        self.enabled_skills = set()
        self.state_file = str(DATA_DIR / "skills_state.json")
        self._load_state()

    def load_plugins_from_directory(self, directory: Path):
        """Scannt einen Ordner nach .py Dateien und lädt Skill-Klassen"""
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            return

        logger.info(f"🔌 Scanning for skills in {directory}...")

        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("__"): continue # Ignoriere __init__.py

            try:
                # 1. Modul dynamisch laden
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 2. Nach Klassen suchen, die von SkillBase erben
                found = False
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # Prüfen: Ist es eine Klasse? Erbt sie von SkillBase? Ist es NICHT SkillBase selbst?
                    if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:

                        # 3. Instanziieren und Registrieren
                        skill_name = file_path.stem # Dateiname als Skill-ID
                        skill_instance = attr(skill_name)

                        # Wichtig: Setup aufrufen und Kontext übergeben (damit der Skill auf 'state' zugreifen kann)
                        # Wir übergeben hier Zugriff auf das globale 'state' Objekt
                        skill_instance.setup({"state": state})

                        self.register_skill(skill_name, skill_instance)
                        logger.info(f"✨ Loaded external skill: {attr_name} from {file_path.name}")
                        found = True

                if not found:
                    logger.warning(f"⚠️ No Skill class found in {file_path.name}")

            except Exception as e:
                logger.error(f"❌ Failed to load plugin {file_path.name}: {e}")

    def register_skill(self, name: str, skill: SkillBase):
        """Register a skill"""
        self.skills[name] = skill
        # Nur aktivieren, wenn es in der gespeicherten Liste ist ODER neu ist (Standard an)
        if name in self.enabled_skills:
            skill.enabled = True
        elif name not in self.enabled_skills and len(self.enabled_skills) == 0:
             # Beim allerersten Start alles aktivieren
             skill.enabled = True
             self.enabled_skills.add(name)
        else:
            # Wenn wir schon eine Config haben, aber der Skill neu ist -> Standard an
            if name not in self.enabled_skills:
                 self.enabled_skills.add(name)
                 skill.enabled = True

        logger.info(f"🔧 Skill registered: {name} ({'enabled' if skill.enabled else 'disabled'})")

    def enable_skill(self, name: str) -> bool:
        """Enable skill"""
        if name in self.skills:
            self.skills[name].enabled = True
            self.enabled_skills.add(name)
            self._save_state()
            dashboard_cache.invalidate()  # Cache invalidieren
            logger.info(f"✅ Skill enabled: {name}")
            return True
        return False

    def disable_skill(self, name: str) -> bool:
        """Disable skill"""
        if name in self.skills:
            self.skills[name].enabled = False
            self.enabled_skills.discard(name)
            self._save_state()
            logger.info(f"❌ Skill disabled: {name}")
            return True
        return False

    def get_skills_status(self) -> List[dict]:
        """Get status of all skills"""
        return [
            {
                "name": name,
                "enabled": skill.enabled,
            }
            for name, skill in self.skills.items()
        ]

    # ========== HOLO INTEGRATION METHODS ==========

    def get_all_holo_skills(self) -> List[Dict]:
        """
        Gibt alle Skills mit Holo-Metadaten zurück.
        Für Skill Discovery - Holo lernt was sie kann.
        """
        holo_skills = []
        for name, skill in self.skills.items():
            if skill.enabled:
                info = skill.get_holo_info()
                holo_skills.append(info)
        return holo_skills

    def get_holo_compatible_skills(self) -> List[Dict]:
        """Nur Skills die Holo-kompatibel sind (haben description + keywords)"""
        return [
            skill.get_holo_info()
            for skill in self.skills.values()
            if skill.enabled and skill.description and skill.keywords
        ]

    def find_skill_for_request(self, request: str) -> Tuple[Optional[SkillBase], float]:
        """
        Findet den besten Skill für eine Anfrage.

        Args:
            request: Was der User will

        Returns:
            (skill, confidence) oder (None, 0) wenn kein Skill passt
        """
        best_skill = None
        best_confidence = 0.0

        for skill in self.skills.values():
            if not skill.enabled:
                continue

            confidence = skill.can_handle(request)
            if confidence > best_confidence:
                best_confidence = confidence
                best_skill = skill

        return (best_skill, best_confidence)

    def find_all_matching_skills(self, request: str, min_confidence: float = 0.3) -> List[Tuple[SkillBase, float]]:
        """
        Findet alle Skills die eine Anfrage bearbeiten könnten.

        Returns:
            Liste von (skill, confidence) sortiert nach Confidence
        """
        matches = []
        for skill in self.skills.values():
            if not skill.enabled:
                continue

            confidence = skill.can_handle(request)
            if confidence >= min_confidence:
                matches.append((skill, confidence))

        # Sortiere nach Confidence (höchste zuerst)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    async def execute_skill(self, skill_name: str, intent: str, params: Dict = None) -> SkillResult:
        """
        Führt einen Skill aus.

        Args:
            skill_name: Name des Skills
            intent: Was der User will
            params: Extrahierte Parameter

        Returns:
            SkillResult
        """
        if skill_name not in self.skills:
            return SkillResult(
                success=False,
                error=f"Skill '{skill_name}' nicht gefunden"
            )

        skill = self.skills[skill_name]
        if not skill.enabled:
            return SkillResult(
                success=False,
                error=f"Skill '{skill_name}' ist deaktiviert"
            )

        try:
            result = await skill.execute(intent, params or {})
            skill._track_execution(result.success)
            return result
        except Exception as e:
            logger.error(f"Skill execution error: {e}")
            skill._track_execution(False)
            return SkillResult(
                success=False,
                error=str(e)
            )

    async def execute_best_skill(self, request: str, params: Dict = None,
                                  min_confidence: float = 0.4) -> Tuple[Optional[SkillResult], str]:
        """
        Findet und führt den besten Skill aus.

        Returns:
            (SkillResult, skill_name) oder (None, "") wenn kein Skill passt
        """
        skill, confidence = self.find_skill_for_request(request)

        if skill is None or confidence < min_confidence:
            return (None, "")

        result = await self.execute_skill(skill.name, request, params)
        return (result, skill.name)

    def _save_state(self):
        """Save enabled skills"""
        data = {"enabled": list(self.enabled_skills)}
        async_atomic_write_json(data, self.state_file)

    def _load_state(self):
        """Load enabled skills"""
        data = load_json_file(self.state_file, {})
        self.enabled_skills = set(data.get("enabled", []))


# =============================================================================
# NEW SKILL: NETWORK SENTINEL (ARP Watch & Honeypot)
# =============================================================================

class NetworkSentinelSkill(SkillBase):
    """
    Überwacht das Netzwerk auf Anomalien:
    1. ARP Watch: Meldet neue, unbekannte MAC-Adressen.
    2. Honeypot: Lauscht auf 'verbotenen' Ports (z.B. 23).
    """
    def setup(self, context):
        self.known_macs = set()
        self.honeypot_ports = [23, 2323] # Telnet Ports (beliebt bei Botnets)
        self.honeypot_sockets = []

        # Lade bekannte MACs aus der Config (Whitelist)
        # Wir nehmen alle MACs aus der zone_mapping als "bekannt" an
        for mac in CONFIG["zone_mapping"]["mac_addresses"].values():
            self.known_macs.add(mac.upper())

        self._start_honeypots()
        self.logger.info(f"🛡️ Sentinel active. Known Devices: {len(self.known_macs)}")

    def _start_honeypots(self):
        """Startet Fake-Services auf Ports, die niemand nutzen sollte."""
        for port in self.honeypot_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                s.listen(1)
                s.setblocking(False)
                self.honeypot_sockets.append((port, s))
                self.logger.info(f"🪤 Honeypot trap set on port {port}")
            except Exception as e:
                self.logger.warning(f"Could not bind honeypot port {port}: {e}")

    def tick(self):
        if not self.enabled: return

        # 1. HONEYPOT CHECK
        for port, s in self.honeypot_sockets:
            try:
                # Prüfen, ob jemand in die Falle getappt ist
                r, _, _ = select.select([s], [], [], 0)
                if r:
                    conn, addr = s.accept()
                    ip = addr[0]
                    self.logger.warning(f"🚨 SECURITY ALERT: IP {ip} touched Honeypot-Port {port}!")
                    conn.close()

                    # Hier könnte man die IP in eine Blacklist aufnehmen
                    # CONFIG["network"]["blocked_ips"].append(ip)
            except BlockingIOError:
                pass  # Expected for non-blocking sockets
            except Exception as e:
                self.logger.debug(f"Honeypot check error on port {port}: {e}")

        # 2. ARP SCAN (Nur alle 5 Minuten, um Netz nicht zu fluten)
        # Wir nutzen einen einfachen Trick: Wir lesen die lokale ARP-Tabelle des Pi
        # Diese füllt sich automatisch, wenn der DeviceDetector Pings sendet.
        try:
            with open("/proc/net/arp", "r") as f:
                next(f) # Header überspringen
                for line in f:
                    parts = line.split()
                    if len(parts) >= 4:
                        ip = parts[0]
                        mac = parts[3].upper()

                        if mac != "00:00:00:00:00:00" and mac not in self.known_macs:
                            self.logger.warning(f"👾 New Device detected: {ip} ({mac})")
                            self.known_macs.add(mac) # Als gesehen markieren (nur 1x warnen)
        except Exception as e:
            self.logger.error(f"ARP Check failed: {e}")

    def shutdown(self):
        for _, s in self.honeypot_sockets:
            s.close()


# =============================================================================
# META-LEARNING SYSTEM (TEST)
# =============================================================================

class MetaLearner:
    """
    Meta-Learning System das lernt:
    - Welche Features wirklich wichtig sind für gute Entscheidungen
    - Welche Layer-Daten korrelieren mit Erfolg
    - Was gute vs schlechte Entscheidungen unterscheidet
    - Optimiert sich selbst basierend auf Outcomes
    """
    def __init__(self):
        self.state_file = str(DATA_DIR / "meta_learning.json")

        # Feature Importance Tracking
        self.feature_importance = defaultdict(lambda: {"good": 0.0, "bad": 0.0, "neutral": 0.0})
        self.layer_performance = defaultdict(lambda: {"success": 0, "failure": 0})

        # Decision Quality Tracking
        self.decision_history = deque(maxlen=200)  # Letzte 200 Entscheidungen
        self.decision_outcomes = defaultdict(lambda: {"success": 0, "failure": 0})

        # Feature Correlation Matrix (welche Features korrelieren mit Erfolg?)
        self.feature_correlations = {}
        self.feature_usage_count = defaultdict(int)

        # Learned Thresholds (adaptive Schwellwerte)
        self.learned_thresholds = {
            "idle_timeout": {"min": 60, "max": 600, "optimal": 300},
            "presence_confidence": {"min": 0.3, "max": 0.9, "optimal": 0.7},
            "nas_usage_threshold": {"min": 0.1, "max": 0.8, "optimal": 0.3}
        }

        # System Performance Metrics
        self.metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "failed_decisions": 0,
            "optimal_decision_rate": 0.0,
            "feature_reduction": 0.0,  # Wie viele Features können wir ignorieren?
            "confidence_score": 0.5,
        }

        self._load()
        self.lock = threading.Lock()
        logger.info("🧠 MetaLearner initialized")

    def record_decision(self, decision: str, context: dict, features: dict):
        """Zeichnet eine Entscheidung mit ihrem Kontext auf"""
        with self.lock:
            decision_record = {
                "timestamp": time.time(),
                "decision": decision,
                "context": context.copy(),
                "features": features.copy(),
                "outcome": None,  # Wird später evaluiert
                "quality_score": None,
            }
            self.decision_history.append(decision_record)
            self.metrics["total_decisions"] += 1

            # Track Feature Usage
            for feature_name in features.keys():
                self.feature_usage_count[feature_name] += 1

    def evaluate_decision(self, success: bool, reason: str = ""):
        """
        Evaluiert die letzte Entscheidung als Erfolg/Misserfolg
        Lernt daraus welche Features/Context zu gutem Outcome führten
        """
        with self.lock:
            if not self.decision_history:
                return

            # Hole letzte Entscheidung
            last_decision = self.decision_history[-1]
            if last_decision["outcome"] is not None:
                return  # Bereits evaluiert

            # Setze Outcome
            last_decision["outcome"] = success
            last_decision["quality_score"] = 1.0 if success else 0.0
            last_decision["reason"] = reason

            # Update Statistiken
            decision_name = last_decision["decision"]
            if success:
                self.metrics["successful_decisions"] += 1
                self.decision_outcomes[decision_name]["success"] += 1
            else:
                self.metrics["failed_decisions"] += 1
                self.decision_outcomes[decision_name]["failure"] += 1

            # WICHTIG: Lerne Feature Importance
            self._learn_feature_importance(last_decision)

            # Update Layer Performance
            self._update_layer_performance(last_decision)

            # Recalculate Metrics
            self._recalculate_metrics()

            # Auto-Save alle 10 Entscheidungen
            if self.metrics["total_decisions"] % 10 == 0:
                self._save()

            logger.debug(f"📊 Decision evaluated: {decision_name} → {'✅' if success else '❌'} ({reason})")

    def _learn_feature_importance(self, decision_record: dict):
        """
        Lernt welche Features mit erfolgreichen Entscheidungen korrelieren
        """
        features = decision_record["features"]
        success = decision_record["outcome"]

        for feature_name, feature_value in features.items():
            if success:
                self.feature_importance[feature_name]["good"] += 1.0
            else:
                self.feature_importance[feature_name]["bad"] += 1.0

    def _update_layer_performance(self, decision_record: dict):
        """
        Tracked welche Layer (Sensoren) zu guten Entscheidungen beitragen
        """
        context = decision_record["context"]
        success = decision_record["outcome"]

        # Identifiziere welche Layer aktive Daten lieferten
        active_layers = []
        if context.get("nas_status"):
            active_layers.append("nas_observer")
        if context.get("device_status"):
            active_layers.append("device_detector")
        if context.get("system_metrics"):
            active_layers.append("system_monitor")
        if context.get("proxy_active", 0) > 0:
            active_layers.append("proxy_tracker")

        for layer in active_layers:
            if success:
                self.layer_performance[layer]["success"] += 1
            else:
                self.layer_performance[layer]["failure"] += 1

    def _recalculate_metrics(self):
        """Berechnet Meta-Metriken neu"""
        total = self.metrics["total_decisions"]
        if total == 0:
            return

        success = self.metrics["successful_decisions"]
        self.metrics["optimal_decision_rate"] = success / total

        # Confidence Score basierend auf letzten 50 Entscheidungen
        recent = list(self.decision_history)[-50:]
        if recent:
            recent_success = sum(1 for d in recent if d.get("outcome") == True)
            self.metrics["confidence_score"] = recent_success / len(recent)

    def get_feature_ranking(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Gibt die wichtigsten Features zurück (sortiert nach Erfolgskorrelation)
        """
        with self.lock:
            rankings = []
            for feature_name, scores in self.feature_importance.items():
                total = scores["good"] + scores["bad"]
                if total < 5:  # Mindestens 5 Samples
                    continue

                # Success Rate für dieses Feature
                success_rate = scores["good"] / total
                rankings.append((feature_name, success_rate))

            return sorted(rankings, key=lambda x: x[1], reverse=True)[:top_n]

    def get_layer_ranking(self) -> List[Tuple[str, float]]:
        """
        Gibt Layer-Performance zurück (welche Layer sind am nützlichsten?)
        """
        with self.lock:
            rankings = []
            for layer_name, perf in self.layer_performance.items():
                total = perf["success"] + perf["failure"]
                if total < 3:
                    continue

                success_rate = perf["success"] / total
                rankings.append((layer_name, success_rate, total))

            return sorted(rankings, key=lambda x: x[1], reverse=True)

    def should_use_feature(self, feature_name: str) -> bool:
        """
        Entscheidet ob ein Feature wichtig genug ist um genutzt zu werden
        Basis für Feature-Reduktion
        """
        with self.lock:
            if feature_name not in self.feature_importance:
                return True  # Neue Features immer erstmal nutzen

            scores = self.feature_importance[feature_name]
            total = scores["good"] + scores["bad"]

            if total < 10:
                return True  # Zu wenig Daten

            success_rate = scores["good"] / total

            # Feature ist wichtig wenn Success Rate > 60%
            return success_rate > 0.6

    def get_optimal_threshold(self, threshold_name: str) -> float:
        """
        Gibt gelernten optimalen Schwellwert zurück
        """
        with self.lock:
            if threshold_name in self.learned_thresholds:
                return self.learned_thresholds[threshold_name]["optimal"]
            return None

    def adapt_threshold(self, threshold_name: str, observed_value: float, was_good: bool):
        """
        Passt Schwellwerte adaptiv an basierend auf Beobachtungen
        """
        with self.lock:
            if threshold_name not in self.learned_thresholds:
                return

            config = self.learned_thresholds[threshold_name]
            optimal = config["optimal"]

            # Wenn gute Entscheidung: Move optimal closer to observed
            # Wenn schlechte Entscheidung: Move optimal away from observed
            if was_good:
                # Langsam in Richtung observed bewegen (Learning Rate: 0.1)
                new_optimal = optimal * 0.9 + observed_value * 0.1
            else:
                # Weg von observed bewegen
                new_optimal = optimal * 0.95 + observed_value * 0.05

            # Clamping innerhalb Min/Max
            new_optimal = max(config["min"], min(config["max"], new_optimal))
            config["optimal"] = new_optimal

            logger.debug(f"🎯 Adapted threshold '{threshold_name}': {optimal:.2f} → {new_optimal:.2f}")

    def get_decision_quality(self, decision: str) -> float:
        """
        Gibt historische Erfolgsrate einer Entscheidung zurück
        """
        with self.lock:
            if decision not in self.decision_outcomes:
                return 0.5  # Unbekannt = 50%

            perf = self.decision_outcomes[decision]
            total = perf["success"] + perf["failure"]
            if total == 0:
                return 0.5

            return perf["success"] / total

    def get_stats(self) -> dict:
        """Gibt Statistiken für Dashboard zurück"""
        with self.lock:
            feature_rankings = self.get_feature_ranking(5)
            layer_rankings = self.get_layer_ranking()

            return {
                "total_decisions": self.metrics["total_decisions"],
                "success_rate": self.metrics["optimal_decision_rate"],
                "confidence": self.metrics["confidence_score"],
                "top_features": [{"name": name, "score": score} for name, score in feature_rankings],
                "layer_performance": [
                    {"layer": name, "success_rate": rate, "samples": samples}
                    for name, rate, samples in layer_rankings
                ],
                "decision_quality": {
                    name: {
                        "success_rate": perf["success"] / (perf["success"] + perf["failure"]) if (perf["success"] + perf["failure"]) > 0 else 0,
                        "total": perf["success"] + perf["failure"]
                    }
                    for name, perf in self.decision_outcomes.items()
                    if (perf["success"] + perf["failure"]) > 0
                }
            }

    def receive_knowledge(self, source: str, knowledge: dict):
        """
        🔥 KNOWLEDGE-SHARING: Empfängt Wissen von anderen Learning-Komponenten

        Beispiel:
        - AdaptiveProxyTiming teilt: {"avg_boot_time": 18.5, "success_rate": 0.97}
        - MCDM teilt: {"best_governor": "ondemand", "temp_correlation": 0.85}
        - SequenceDetector teilt: {"top_pattern": ["pc_on", "nas_wake"], "confidence": 0.92}
        """
        logger.debug(f"🔗 MetaLearner received knowledge from {source}: {knowledge}")

        # Integriere Wissen in Feature-Importance
        if source == "adaptive_timing":
            # Boot-Zeit-Korrelation ist wichtig
            if knowledge.get("success_rate", 0) > 0.9:
                self.feature_importance["learned_boot_time"]["good"] += 5

        elif source == "mcdm":
            # Governor-Korrelation tracken
            best_gov = knowledge.get("best_governor")
            if best_gov:
                self.feature_importance[f"governor_{best_gov}"]["good"] += 3

        elif source == "sequence_detector":
            # Pattern-Erfolg tracken
            confidence = knowledge.get("confidence", 0)
            if confidence > 0.8:
                self.feature_importance["sequence_patterns"]["good"] += 2

        elif source == "ab_testing":
            # Variant-Performance tracken
            winning_variant = knowledge.get("winning_variant")
            if winning_variant:
                self.feature_importance[f"ab_variant_{winning_variant}"]["good"] += 1

    def _save(self):
        """Speichert gelerntes Wissen"""
        data = {
            "feature_importance": dict(self.feature_importance),
            "layer_performance": dict(self.layer_performance),
            "decision_outcomes": dict(self.decision_outcomes),
            "learned_thresholds": self.learned_thresholds,
            "metrics": self.metrics,
            "feature_usage_count": dict(self.feature_usage_count),
        }
        async_atomic_write_json(data, self.state_file)

    def _load(self):
        """Lädt gespeichertes Wissen"""
        data = load_json_file(self.state_file, {})
        if data:
            self.feature_importance = defaultdict(lambda: {"good": 0.0, "bad": 0.0, "neutral": 0.0}, data.get("feature_importance", {}))
            self.layer_performance = defaultdict(lambda: {"success": 0, "failure": 0}, data.get("layer_performance", {}))
            self.decision_outcomes = defaultdict(lambda: {"success": 0, "failure": 0}, data.get("decision_outcomes", {}))
            self.learned_thresholds = data.get("learned_thresholds", self.learned_thresholds)
            self.metrics = data.get("metrics", self.metrics)
            self.feature_usage_count = defaultdict(int, data.get("feature_usage_count", {}))

            logger.info(f"📚 Loaded meta-learning: {self.metrics['total_decisions']} decisions, {self.metrics['optimal_decision_rate']:.1%} success rate")

    def register_insight(self, source: str, insight_type: str, data: dict):
        """
        🔥 NEUE METHODE: Ermöglicht anderen Learning-Systemen Insights zu teilen

        source: Name des Systems (z.B. "adaptive_timing", "mcdm", "sequence_detector")
        insight_type: Art des Insights (z.B. "boot_time_learned", "governor_optimal", "pattern_found")
        data: Dictionary mit Insight-Daten
        """
        with self.lock:
            # Tracke welche Systeme Insights liefern
            if source not in self.layer_performance:
                self.layer_performance[source] = {"success": 0, "failure": 0}

            # Erfolgreiche Insights zählen als "success" für das System
            self.layer_performance[source]["success"] += 1

            # Log für Transparenz
            logger.debug(f"📨 Insight from {source}: {insight_type} → {data}")

            # Spezifische Insight-Verarbeitung
            if insight_type == "boot_time_learned":
                # AdaptiveProxyTiming hat optimale Zeit gelernt
                if "optimal_timeout" in data:
                    self.learned_thresholds["offline_timeout"] = {
                        "min": 15,
                        "max": 90,
                        "optimal": data["optimal_timeout"]
                    }
                    logger.info(f"🔗 MetaLearner synced: offline_timeout → {data['optimal_timeout']}s")

            elif insight_type == "governor_performance":
                # MCDM hat Governor-Performance gelernt
                if "best_governor" in data and "context" in data:
                    # Markiere Governor als wichtiges Feature
                    gov = data["best_governor"]
                    self.feature_importance[f"governor_{gov}"]["good"] += 1.0

            elif insight_type == "sequence_pattern":
                # SequenceDetector hat Muster gefunden
                if "pattern" in data and "probability" in data:
                    # Patterns mit hoher Probability sind wichtig
                    if data["probability"] > 0.7:
                        for event in data.get("events", []):
                            self.feature_importance[event]["good"] += 0.5

            elif insight_type == "ab_test_result":
                # A/B Testing hat Ergebnis
                if "winner" in data:
                    self.decision_outcomes[data["winner"]]["success"] += 1



# =============================================================================
# ADAPTIVE PROXY TIMING - KI lernt optimale Retry-Zeiten
# =============================================================================

class AdaptiveProxyTiming:
    """
    SAFE VERSION: Lernt Proxy-Retry-Zeiten mit Timeouts und Safe Fallbacks
    """
    def __init__(self, meta_learner=None):
        self.state_file = str(DATA_DIR / "adaptive_proxy_timing.json")
        self.meta_learner = meta_learner

        # Initial Default-Werte
        self.online_retry_seconds = 5
        self.offline_retry_seconds = 40

        # Lern-Daten
        self.boot_times = deque(maxlen=50)
        self.online_connect_times = deque(maxlen=50)

        # Statistiken
        self.successful_boots = 0
        self.failed_boots = 0
        self.quick_connects = 0
        self.slow_connects = 0

        self._load()
        # SAFE: Verwende RLock für re-entrant calls
        self.lock = threading.RLock()
        logger.info("🎯 AdaptiveProxyTiming initialized (SAFE mode)")

    def record_boot_success(self, seconds: float):
        """Zeichnet erfolgreiche Boot-Zeit auf"""
        # SAFE: Timeout beim Lock
        if self.lock.acquire(timeout=2.0):
            try:
                self.boot_times.append(seconds)
                self.successful_boots += 1
                self._update_offline_timing()
                self._save_async()
                logger.info(f"📊 Learned: NAS boot took {seconds:.1f}s")
            finally:
                self.lock.release()
        else:
            logger.warning("⚠️ record_boot_success: Lock timeout!")

    def record_boot_failure(self):
        """Zeichnet fehlgeschlagenen Boot-Versuch auf"""
        if self.lock.acquire(timeout=2.0):
            try:
                self.failed_boots += 1
                if self.failed_boots > 3:
                    self.offline_retry_seconds = min(60, self.offline_retry_seconds + 5)
                self._save_async()
            finally:
                self.lock.release()
        else:
            logger.warning("⚠️ record_boot_failure: Lock timeout!")

    def record_online_connect(self, seconds: float, success: bool):
        """Zeichnet Connect-Zeit bei bereits laufendem NAS auf"""
        if self.lock.acquire(timeout=2.0):
            try:
                if success:
                    self.online_connect_times.append(seconds)
                    self.quick_connects += 1
                    self._update_online_timing()
                else:
                    self.slow_connects += 1
                self._save_async()
            finally:
                self.lock.release()
        else:
            logger.warning("⚠️ record_online_connect: Lock timeout!")

    def _share_knowledge(self):
        """Teilt gelerntes Wissen mit MetaLearner"""
        if 'app' in globals() and app is not None and hasattr(app, 'meta_learner'):
            success_rate = self.successful_boots / (self.successful_boots + self.failed_boots) if (self.successful_boots + self.failed_boots) > 0 else 0

            knowledge = {
                "avg_boot_time": self._avg_boot_time(),
                "avg_online_connect": self._avg_online_time(),
                "success_rate": success_rate,
                "boot_samples": len(self.boot_times),
                "online_timeout": self.online_retry_seconds,
                "offline_timeout": self.offline_retry_seconds,
            }

            app.meta_learner.receive_knowledge("adaptive_timing", knowledge)

    def _avg_boot_time(self) -> float:
        if not self.boot_times:
            return 40.0
        return statistics.mean(self.boot_times)

    def _avg_online_time(self) -> float:
        if not self.online_connect_times:
            return 5.0
        return statistics.mean(self.online_connect_times)

    def _update_offline_timing(self):
        """Passt Offline-Timeout an"""
        if len(self.boot_times) < 5:
            return

        avg = self._avg_boot_time()
        stddev = statistics.stdev(self.boot_times) if len(self.boot_times) > 1 else 5.0
        optimal_timeout = avg + (1.5 * stddev)
        optimal_timeout = max(15, min(90, optimal_timeout))

        if abs(optimal_timeout - self.offline_retry_seconds) > 3:
            old_timeout = self.offline_retry_seconds
            self.offline_retry_seconds = int(optimal_timeout)
            logger.info(f"🎯 Adapted offline timeout: {old_timeout}s → {self.offline_retry_seconds}s (avg: {avg:.1f}s, σ: {stddev:.1f}s)")

            # 🔗 TEILE MIT METALEARNER
            if self.meta_learner:
                self.meta_learner.register_insight(
                    source="adaptive_timing",
                    insight_type="boot_time_learned",
                    data={
                        "optimal_timeout": self.offline_retry_seconds,
                        "avg_boot_time": avg,
                        "stddev": stddev,
                        "samples": len(self.boot_times)
                    }
                )

            # 🔥 KNOWLEDGE-SHARING: Teile Wissen mit MetaLearner
            self._share_knowledge()

    def _update_online_timing(self):
        """Passt Online-Timeout an"""
        if len(self.online_connect_times) < 10:
            return

        avg = self._avg_online_time()
        stddev = statistics.stdev(self.online_connect_times) if len(self.online_connect_times) > 1 else 1.0
        optimal_timeout = avg + (2 * stddev)
        optimal_timeout = max(3, min(15, optimal_timeout))

        if abs(optimal_timeout - self.online_retry_seconds) > 1:
            old_timeout = self.online_retry_seconds
            self.online_retry_seconds = int(optimal_timeout)
            logger.info(f"🎯 Adapted online timeout: {old_timeout}s → {self.online_retry_seconds}s")

    def get_optimal_timeout(self, nas_is_online: bool) -> int:
        """SAFE: Gibt optimalen Timeout zurück"""
        # SAFE: Kein Lock nötig für einfaches Read (atomic int)
        try:
            if nas_is_online:
                return self.online_retry_seconds
            else:
                return self.offline_retry_seconds
        except Exception as e:
            logger.error(f"❌ get_optimal_timeout error: {e}")
            return 40  # Safe Fallback

    def get_stats(self) -> dict:
        """SAFE: Gibt Statistiken für Dashboard zurück"""
        # SAFE: Timeout beim Lock + Fallback
        if self.lock.acquire(timeout=0.5):  # Kurzer Timeout für Dashboard!
            try:
                return {
                    "online_timeout": self.online_retry_seconds,
                    "offline_timeout": self.offline_retry_seconds,
                    "avg_boot_time": self._avg_boot_time() if self.boot_times else None,
                    "avg_online_connect": self._avg_online_time() if self.online_connect_times else None,
                    "successful_boots": self.successful_boots,
                    "failed_boots": self.failed_boots,
                    "boot_samples": len(self.boot_times),
                    "connect_samples": len(self.online_connect_times),
                }
            finally:
                self.lock.release()
        else:
            # SAFE FALLBACK: Lock timeout → return defaults
            logger.warning("⚠️ get_stats: Lock timeout, returning fallback")
            return {
                "online_timeout": 5,
                "offline_timeout": 40,
                "avg_boot_time": None,
                "avg_online_connect": None,
                "successful_boots": 0,
                "failed_boots": 0,
                "boot_samples": 0,
                "connect_samples": 0,
            }

    def _save_async(self):
        """SAFE: Speichert asynchron ohne zu blockieren"""
        try:
            data = {
                "online_retry_seconds": self.online_retry_seconds,
                "offline_retry_seconds": self.offline_retry_seconds,
                "boot_times": list(self.boot_times),
                "online_connect_times": list(self.online_connect_times),
                "successful_boots": self.successful_boots,
                "failed_boots": self.failed_boots,
                "quick_connects": self.quick_connects,
                "slow_connects": self.slow_connects,
            }
            async_atomic_write_json(data, self.state_file)
        except Exception as e:
            logger.error(f"❌ AdaptiveProxyTiming save error: {e}")

    def _load(self):
        """SAFE: Lädt gespeicherte Daten"""
        try:
            data = load_json_file(self.state_file, {})
            if data:
                self.online_retry_seconds = data.get("online_retry_seconds", 5)
                self.offline_retry_seconds = data.get("offline_retry_seconds", 40)
                self.boot_times = deque(data.get("boot_times", []), maxlen=50)
                self.online_connect_times = deque(data.get("online_connect_times", []), maxlen=50)
                self.successful_boots = data.get("successful_boots", 0)
                self.failed_boots = data.get("failed_boots", 0)
                self.quick_connects = data.get("quick_connects", 0)
                self.slow_connects = data.get("slow_connects", 0)
                logger.info(f"📚 Loaded adaptive timing: {self.online_retry_seconds}s (online) / {self.offline_retry_seconds}s (offline)")
        except Exception as e:
            logger.error(f"❌ AdaptiveProxyTiming load error: {e}")



# =============================================================================
# COGNITIVE CONTROL LAYER - Alles geht durch die KI!
# =============================================================================


class CognitiveController:
    """
    Zentrale kognitive Kontrollschicht.
    NICHTS passiert ohne Wissen und Zustimmung der KI!
    """
    def __init__(self, decision_engine, meta_learner, actors):
        self.decision_engine = decision_engine
        self.meta_learner = meta_learner
        self.actors = actors

        # Request Queue
        self.pending_requests = deque(maxlen=100)
        self.request_history = deque(maxlen=200)

        # Approval Tracking
        self.approvals = {
            "auto_approved": 0,
            "rejected": 0,
            "pending": 0,
        }

        self.lock = threading.RLock()
        logger.info("🧠 CognitiveController initialized - All actions now require approval!")

    def request_action(self, action: str, source: str, reason: str, priority: int = 5, context: dict = None) -> dict:
        """
        ZENTRALE METHODE: Alle Actions müssen hier durch!

        Args:
            action: Name der Action ("wake_nas", "sleep_nas", "change_governor")
            source: Wer fordert an? ("proxy", "dashboard", "auto", "scheduler")
            reason: Warum? ("client_waiting", "user_manual", "idle_timeout")
            priority: 1-10 (10=highest)
            context: Zusätzlicher Kontext

        Returns:
            {
                "approved": bool,
                "reason": str,
                "confidence": float,
                "alternatives": list,
            }
        """
        with self.lock:
            # Erstelle Request
            request = {
                "id": f"{action}_{int(time.time()*1000)}",
                "action": action,
                "source": source,
                "reason": reason,
                "priority": priority,
                "context": context or {},
                "timestamp": time.time(),
                "approved": None,
                "executed": False,
            }

            logger.info(f"🧠 COGNITIVE REQUEST: {action} from {source} ({reason})")

            # 1. CRITICAL CHECK: Manual Override?
            if state.is_manual_override_active():
                manual_action = state.get_manual_override()

                # Wenn Override im Widerspruch zur Anfrage (z.B. KI will WAKE, User hat SLEEP gesetzt)
                if (manual_action == "sleep" and action == "wake_nas"):
                    logger.warning(f"⚠️ TEACHING MOMENT: Manual override BLOCKED {action}")

                    # 🔥 NEU: SOFORTIGES NEGATIVES FEEDBACK AN DIE KI
                    if self.meta_learner:
                        # Wir simulieren, dass die Entscheidung getroffen wurde und FALSCH war
                        self.actors.nas._report_ai_reward(
                            action=action,
                            success=False, # War nicht erfolgreich (wurde blockiert)
                            source="manual_override_punishment"
                        )
                        # Wir geben der KI eine extra Strafe (-2.0)
                        # Dazu greifen wir kurz auf den AI Integrator zu (etwas hacky aber effektiv)
                        if self.decision_engine.ai_integration:
                             s_snap = state.snapshot()
                             ctx = self.decision_engine.ai_integration.build_context(s_snap)
                             u_state = self.decision_engine.ai_integration.build_universal_state(s_snap, ctx)
                             self.decision_engine.ai_integration.universal_ql.observe_result(
                                 u_state, False, {"punishment": -5.0} # BÄM! 5 Punkte Abzug
                             )

                    return {
                        "approved": False,
                        "reason": f"Manual override forces SLEEP. AI punished.",
                        "confidence": 0.0,
                        "alternatives": [],
                    }

            # 2. SAFETY CHECK: Action Cooldown
            if not self._check_cooldown(action):
                request["approved"] = False
                request["reason"] = "Action cooldown active"
                self.approvals["rejected"] += 1
                self.request_history.append(request)
                return {
                    "approved": False,
                    "reason": "Action cooldown - too soon!",
                    "confidence": 0.0,
                    "alternatives": ["wait"],
                }

            # 3. COGNITIVE EVALUATION: Frage Decision Engine
            evaluation = self._evaluate_request(request)

            # 4. META-LEARNING: Zeichne auf
            if self.meta_learner:
                self.meta_learner.record_decision(
                    decision=action,
                    context={
                        "source": source,
                        "reason": reason,
                        "priority": priority,
                        **request["context"],
                    },
                    features=self._extract_features(request)
                )

            # 5. APPROVAL DECISION
            request["approved"] = evaluation["approved"]
            request["reason"] = evaluation["reason"]
            request["confidence"] = evaluation["confidence"]

            if evaluation["approved"]:
                self.approvals["auto_approved"] += 1
                logger.info(f"✅ APPROVED: {action} (confidence: {evaluation['confidence']:.2f})")

                # 6. EXECUTE (wenn approved)
                success = self._execute_action(action, source)
                request["executed"] = success

                # 7. OUTCOME TRACKING (für MetaLearner)
                if self.meta_learner:
                    # Später evaluieren (nach z.B. 30s)
                    threading.Timer(
                        30.0,
                        lambda: self._delayed_evaluation(request, success)
                    ).start()
            else:
                self.approvals["rejected"] += 1
                logger.warning(f"❌ REJECTED: {action} - {evaluation['reason']}")

            self.request_history.append(request)
            return evaluation

    def _check_cooldown(self, action: str) -> bool:
        """
        Prüft ob Action Cooldown abgelaufen ist.
        MODIFIZIERT: Deaktiviert für NAS, da NAS seinen Status selbst via 'busy' regelt.
        """
        # Governor schützen wir weiterhin vor Flackern (60s)
        if action == "change_governor":
            last_time = state.get(f"last_{action}_time", default=0.0)
            if (time.time() - last_time) < 60:
                return False

        # Für NAS Actions (wake/sleep) geben wir IMMER True zurück.
        # Wir verlassen uns darauf, dass 'nas_state' == 'busy' die Blockade übernimmt.
        return True

    def _extract_features(self, request: dict) -> dict:
        """Extrahiert Features für MetaLearner"""
        return {
            "action": request["action"],
            "source": request["source"],
            "priority": request["priority"],
            "nas_online": state.get("nas_status", subkey="online", default=False),
            "cpu_temp": state.get("system", subkey="cpu_temp", default=50.0),
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            **request["context"],
        }

    def _evaluate_request(self, request: dict) -> dict:
        """
        Kognitive Evaluation der Anfrage
        Nutzt Decision Engine, GOAP, MCDM, etc.
        """
        action = request["action"]
        source = request["source"]
        reason = request["reason"]

        # 1. HIGH PRIORITY: User Manual Actions (fast immer approved)
        if source in ["user_manual", "dashboard"]:
            return {
                "approved": True,
                "reason": "User manual control",
                "confidence": 1.0,
                "alternatives": [],
            }

        # 2. CONTEXT-BASED EVALUATION
        nas_online = state.get("nas_status", subkey="online", default=False)

        # --- WAKE NAS ---
        if action == "wake_nas":
            if nas_online:
                return {
                    "approved": False,
                    "reason": "NAS already online",
                    "confidence": 0.0,
                    "alternatives": [],
                }

            # HARD CONSTRAINTS (VETO)
            if source == "traffic_veto":
                return {
                    "approved": True,
                    "reason": "Traffic detected (Hard Constraint)",
                    "confidence": 1.0,
                    "alternatives": [],
                }

            # Proxy braucht NAS
            if source == "proxy" and reason == "client_waiting":
                return {
                    "approved": True,
                    "reason": "Client waiting for NAS connection",
                    "confidence": 0.95,
                    "alternatives": [],
                }

            # KI-Entscheidungen (GOAP oder Prediction)
            if source in ["ai_prediction", "ai_goap", "nas_ai"]:
                # Wir vertrauen der KI, dass sie einen Grund hat
                return {
                    "approved": True,
                    "reason": f"AI Request from {source}",
                    "confidence": 0.85,
                    "alternatives": [],
                }

            # Auto-Wake (Legacy Fallback)
            if source == "auto":
                prob = self.decision_engine.prob.predict()
                if prob > 0.8:
                    return {
                        "approved": True,
                        "reason": f"Predicted usage: {prob:.0%}",
                        "confidence": prob,
                        "alternatives": [],
                    }
                else:
                    return {
                        "approved": False,
                        "reason": f"Low usage prediction: {prob:.0%}",
                        "confidence": 1.0 - prob,
                        "alternatives": ["wait"],
                    }

        # --- SLEEP NAS ---
        elif action == "sleep_nas":
            if not nas_online:
                return {
                    "approved": False,
                    "reason": "NAS already offline",
                    "confidence": 0.0,
                    "alternatives": [],
                }

            # Check if NAS is busy
            nas_state = state.get("nas_status", subkey="state", default="unknown")
            if nas_state in ["busy", "waking_up"]:
                return {
                    "approved": False,
                    "reason": f"NAS is {nas_state}",
                    "confidence": 0.0,
                    "alternatives": ["wait"],
                }

            # AWAY MODE (Hard Constraint)
            if source == "away_mode":
                return {
                    "approved": True,
                    "reason": "User Away (Hard Constraint)",
                    "confidence": 1.0,
                    "alternatives": [],
                }

            # NEU: NAS AI (Der neue Q-Learning Agent)
            if source == "nas_ai":
                return {
                    "approved": True,
                    "reason": "NasAI decided to sleep (Q-Learning)",
                    "confidence": 0.9,
                    "alternatives": [],
                }

            # Legacy Auto-Sleep (Falls NasAI mal nicht läuft)
            if source == "auto":
                idle_minutes = state.get("nas_status", subkey="idle_minutes", default=0)
                threshold = state.get("learned_idle_threshold", persistent=True, default=15.0)

                if idle_minutes >= threshold:
                    return {
                        "approved": True,
                        "reason": f"Idle timeout ({idle_minutes:.1f}m >= {threshold:.1f}m)",
                        "confidence": 0.9,
                        "alternatives": [],
                    }
                else:
                    return {
                        "approved": False,
                        "reason": f"Not idle enough",
                        "confidence": 0.8,
                        "alternatives": ["wait"],
                    }

        # --- GOVERNOR ---
        elif action == "change_governor" or action.startswith("set_governor"):
            # Governor-Änderungen sind fast immer okay, da die Logik schon in der Engine sitzt
            return {
                "approved": True,
                "reason": f"Governor optimization by {source}",
                "confidence": 0.8,
                "alternatives": [],
            }

        # Default: Reject unknown actions
        return {
            "approved": False,
            "reason": f"Unknown action: {action} from {source}",
            "confidence": 0.0,
            "alternatives": [],
        }

    def _execute_action(self, action: str, source: str) -> bool:
        """
        Führt approved Action aus
        Ruft die entsprechenden Actors auf
        """
        try:
            # Update last action time
            state.update(f"last_{action}_time", time.time())

            if action == "wake_nas":
                success = self.actors.nas.send_wol(source)
                state.add_nas_event("wake_approved", source, f"Cognitive approval for wake")
                return success

            elif action == "sleep_nas":
                success = self.actors.nas.request_shutdown(source)
                state.add_nas_event("sleep_approved", source, f"Cognitive approval for sleep")
                return success

            elif action == "change_governor":
                governor = state.get("desired_governor", default="ondemand")
                success = self.actors.power.set_governor(governor)
                return success

            else:
                logger.error(f"Unknown action execution: {action}")
                return False

        except Exception as e:
            logger.error(f"Action execution error: {e}", exc_info=True)
            return False

    def _delayed_evaluation(self, request: dict, immediate_success: bool):
        """
        Delayed Evaluation für MetaLearner
        Prüft ob die Action wirklich erfolgreich war
        """
        if not self.meta_learner:
            return

        action = request["action"]

        # Evaluate based on action type
        if action == "wake_nas":
            # Check if NAS is actually online now
            nas_online = state.get("nas_status", subkey="online", default=False)
            success = nas_online and immediate_success
            reason = "NAS is online" if success else "NAS failed to boot"

        elif action == "sleep_nas":
            # Check if NAS is actually offline now
            nas_online = state.get("nas_status", subkey="online", default=False)
            success = not nas_online and immediate_success
            reason = "NAS is offline" if success else "NAS failed to sleep"

        else:
            success = immediate_success
            reason = "Action executed"

        # Inform MetaLearner
        self.meta_learner.evaluate_decision(success, reason)
        logger.info(f"📊 Delayed Evaluation: {action} → {'✅ Success' if success else '❌ Failed'} ({reason})")

    def get_stats(self) -> dict:
        """Stats für Dashboard"""
        with self.lock:
            return {
                "total_requests": len(self.request_history),
                "auto_approved": self.approvals["auto_approved"],
                "rejected": self.approvals["rejected"],
                "approval_rate": self.approvals["auto_approved"] / max(1, len(self.request_history)),
                "recent_requests": [
                    {
                        "action": r["action"],
                        "source": r["source"],
                        "approved": r["approved"],
                        "reason": r["reason"],
                        "timestamp": r["timestamp"],
                    }
                    for r in list(self.request_history)[-10:]
                ],
            }


class Application:
    """Ultimate Pi-Control Application. Orchestriert alle 7 Layer."""

    def __init__(self):
        logger.info("=" * 80)
        logger.info("🚀 Pi-Control ULTIMATE v8.0 - Kognitive Intelligenz")
        logger.info("=" * 80)
        self.holo_interface = HoloInterface()
        logger.info("🔗 HoloInterface initialized")

        # META-LEARNING (TEST): Initialize MetaLearner
        logger.info("🧠 Initializing MetaLearner (TEST MODE)...")
        self.meta_learner = MetaLearner()
        logger.info("✅ MetaLearner initialized")

        # 🆕 AI UPGRADE INTEGRATION
        self.ai_integration = AIUpgradeIntegrationExtended(
            DATA_DIR,
            config={
                "weather_entity": "weather.forecast_home",
                "calendar_entity": "calendar.kalender",
                "location": {"lat": 51.4556, "lon": 7.0116},  # Optional: Dein Standort
            }
        )

        # Skill System
        self.skill_manager = SkillManager()

        # Web UI
        self.web_server = None

        logger.info("✅ AI System initialized - Q-Learning & Bayesian active!")

        # Layer 0: Communication
        self.udp_listener = UDPNASListener(CONFIG["nas"]["udp_port"])
        self.udp_client = UDPNASClient(CONFIG["nas"]["ip"], CONFIG["nas"]["udp_port"])

        # Layer 1: Sensors
        self.system_monitor = SystemMonitor()
        self.nas_observer = NasObserver(self.udp_listener, self.udp_client)
        self.presence_engine = PresencePatternEngine(
            data_file=str(DATA_DIR / "presence_patterns.json"),
            min_data_points=3
        )
        stats = self.presence_engine.get_statistics()
        logger.info(f"📊 PresencePatternEngine: {stats.get('total_events', 0)} historische Events geladen")

        # DeviceDetector mit Presence Engine
        self.device_detector = DeviceDetector(presence_engine=self.presence_engine)

        # Layer 2: World Model
        self.probabilistic_engine = ProbabilisticEngine()
        self.context_updater = ContextualStateUpdater()

        # Layer 3: Reasoning & Planning
        self.goal_manager = GoalManager()
        self.mcdm = MCDMGovernorSelector()
        self.mcdm.set_meta_learner(self.meta_learner)  # Connect MCDM to MetaLearner
        self.probabilistic_engine.sequence.set_meta_learner(self.meta_learner)  # Connect SequenceDetector
        self.ab_testing = ABTestManager()
        self.goap = GOAPPlanner()
        self.sandbox = SandboxSimulator(self.goal_manager)

        # Layer 5: Meta Decision Engine
        self.decision_engine = MetaDecisionEngine(
            self.probabilistic_engine,
            self.goal_manager,
            self.sandbox,
            self.mcdm,
            self.ab_testing,
            self.goap
        )

        # 🆕 Connect AI Integration to Decision Engine
        self.decision_engine.ai_integration = self.ai_integration
        logger.info("🔗 Connected AI Integration to Decision Engine")

        # Layer 6: Actors
        global actors
        actors = ActorContainer(self.udp_client)

        # Connect adaptive_timing to meta_learner
        actors.adaptive_timing.meta_learner = self.meta_learner
        logger.info("🔗 Connected AdaptiveProxyTiming to MetaLearner")

        # COGNITIVE CONTROL: Initialize Controller
        logger.info("🧠 Initializing Cognitive Controller...")
        self.cognitive_controller = CognitiveController(
            decision_engine=self.decision_engine,
            meta_learner=self.meta_learner,
            actors=actors
        )
        logger.info("✅ Cognitive Controller initialized - All actions now require cognitive approval!")

        # Skill System
        self.skill_manager = SkillManager()

        # Web UI
        self.web_server = None
        self.shutdown_event = threading.Event()

    def start(self):
        """Start all systems"""
        logger.info("=" * 80)
        logger.info("🌟 STARTING ALL SYSTEMS")
        logger.info("=" * 80)

        # Layer 0
        logger.info("📡 Layer 0: Communication"); self.udp_listener.start()

        # Layer 1
        logger.info("🔍 Layer 1: Sensors")
        self.system_monitor.start()
        self.nas_observer.start()
        self.device_detector.start()

        # Layer 2
        logger.info("🧠 Layer 2: World Model")
        self.probabilistic_engine.start(); self.context_updater.start()

        # Layer 5
        logger.info("🎯 Layer 5: Meta Decision Engine"); self.decision_engine.start()

        # Layer 6
        logger.info("🎬 Layer 6: Actors"); actors.start_all()

        # Skills (example skills)
        self._register_example_skills()

        # Web UI
        logger.info("🌐 Starting Web Dashboard")
        self.web_server = ThreadingHTTPServer(
            (CONFIG["web_ui"]["listen_ip"], CONFIG["web_ui"]["port"]),
            DashboardHandler
        )
        web_thread = threading.Thread(target=self.web_server.serve_forever, daemon=True)
        web_thread.start()

        logger.info("=" * 80)
        logger.info("✅ ALL SYSTEMS OPERATIONAL")
        logger.info(f"🌐 Dashboard: http://localhost:{CONFIG['web_ui']['port']}")
        logger.info(f"🧠 Goals: {list(self.goal_manager.goals.keys())}")
        logger.info(f"🎯 Governors: {actors.power.get_available_governors()}")
        logger.info(f"🔬 A/B Tests: {list(self.ab_testing.active_tests.keys())}")
        logger.info("=" * 80)

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self._start_periodic_save()

        self.shutdown_event.wait()

    def _register_example_skills(self):
        class EnergyMonitorSkill(SkillBase):
            def tick(self):
                if not self.enabled: return
                power = state.get("system_metrics", subkey="cpu_temp", default=0) / 10.0
                if power > 7.0: self.logger.warning(f"⚡ High power consumption: {power:.1f}W")

        class ConnectionMonitorSkill(SkillBase):
            def tick(self):
                if not self.enabled: return
                conns = actors.proxy_tracker.get_active_connections()
                if len(conns) > 5: self.logger.info(f"🔗 High connection count: {len(conns)}")

        energy_skill = EnergyMonitorSkill("energy_monitor"); energy_skill.setup({})
        self.skill_manager.register_skill("energy_monitor", energy_skill)
        conn_skill = ConnectionMonitorSkill("connection_monitor"); conn_skill.setup({})
        self.skill_manager.register_skill("connection_monitor", conn_skill)
        sentinel = NetworkSentinelSkill("network_sentinel")
        sentinel.setup({})
        self.skill_manager.register_skill("network_sentinel", sentinel)

        # 🟢 2. EXTERNE SKILLS LADEN (Der neue Teil!)
        skills_dir = BASE_DIR / "skills"
        self.skill_manager.load_plugins_from_directory(skills_dir)

    def _start_periodic_save(self):
        """Periodic asynchronous saves (RAM-First)"""
        def save_loop():
            while not self.shutdown_event.is_set():
                time.sleep(300)
                try:
                    state.save()
                    self.probabilistic_engine.sequence.save()
                    self.mcdm.save()
                    self.ab_testing.save()
                    logger.debug("💾 Periodic save delegated asynchronously")
                except Exception as e:
                    logger.error(f"Save delegation error: {e}")

        threading.Thread(target=save_loop, daemon=True).start()

    def shutdown(self):
        logger.info("=" * 80); logger.info("🛑 SHUTTING DOWN"); logger.info("=" * 80)

        self.system_monitor.stop(); self.nas_observer.stop()
        self.device_detector.stop(); self.udp_listener.stop()
        self.probabilistic_engine.stop(); self.decision_engine.stop()
        actors.stop_all()

        if self.web_server: self.web_server.shutdown()

        logger.info("💾 Final save delegation...")
        state.save(); self.probabilistic_engine.sequence.save()
        self.mcdm.save(); self.ab_testing.save()

        logger.info("👋 Shutdown complete")
        self.shutdown_event.set()

    def _signal_handler(self, signum, frame):
        logger.info(f"📢 Signal {signum} received")
        self.shutdown()

# Global app instance
app = None

# =============================================================================
# DASHBOARD - Ausgelagert nach holo_dashboard.py
# =============================================================================
# Das Dashboard-HTML und DashboardCache wurden in holo_dashboard.py verschoben.
# Import erfolgt oben im Datei-Header.
# Falls der Import fehlschlägt, wird ein minimales Fallback-HTML verwendet.
#
# Alte lokale Definition wurde entfernt - siehe holo_dashboard.py für den Code.
# =============================================================================

# Fallback DashboardCache falls Import fehlschlägt
if not HAVE_DASHBOARD_MODULE:
    class DashboardCache:
        """Minimaler Fallback-Cache"""
        def __init__(self):
            self._cached_html = None
        def get_html(self, skill_manager) -> str:
            return DASHBOARD_HTML
        def invalidate(self):
            self._cached_html = None
    dashboard_cache = DashboardCache()

# =============================================================================
# LEGACY CODE REMOVED - War hier: 2000+ Zeilen HTML/CSS/JS
# Siehe: holo_dashboard.py
# =============================================================================

_DASHBOARD_LEGACY_REMOVED = """
<!--
HINWEIS: Der folgende Bereich enthielt das vollstaendige Dashboard HTML.
Dieser Code wurde nach holo_dashboard.py ausgelagert (ca. 2000 Zeilen).
-->
"""

# Das alte Dashboard-HTML (~2000 Zeilen) wurde entfernt.
# Siehe: holo_dashboard.py fuer den vollstaendigen Code.
_LEGACY_HTML_PLACEHOLDER = """
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: var(--text-dim);
            font-size: 1.1em;
        }

        .header-stats {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }

        .header-stat {
            text-align: center;
        }

        .header-stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--accent);
        }

        .header-stat-label {
            font-size: 0.9em;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            border-bottom: 2px solid var(--border);
            flex-wrap: wrap;
        }

        .tab {
            padding: 15px 30px;
            background: transparent;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            font-size: 1.05em;
            font-weight: 500;
        }

        .tab:hover {
            color: var(--text);
            background: rgba(255, 255, 255, 0.05);
        }

        .tab.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Grid System */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .grid-2 {
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        }

        .grid-full {
            grid-template-columns: 1fr;
        }

        /* Cards */
        .card {
            background: var(--card);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid var(--border);
            box-shadow: 0 5px 20px var(--shadow);
            transition: all 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px var(--shadow);
        }

        .card h2 {
            font-size: 1.4em;
            margin-bottom: 20px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border);
        }

        /* NAS Status Display */
        .status-display {
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            font-size: 2.2em;
            font-weight: bold;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 3px;
            position: relative;
            overflow: hidden;
        }

        .status-display::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        .status-online {
            background: linear-gradient(135deg, #00ff88, #00cc66);
            color: #000;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
        }

        .status-offline {
            background: linear-gradient(135deg, #ff4444, #cc0000);
            color: #fff;
            box-shadow: 0 0 30px rgba(255, 68, 68, 0.5);
        }

        .status-busy {
            background: linear-gradient(135deg, #ffaa00, #ff8800);
            color: #000;
            box-shadow: 0 0 30px rgba(255, 170, 0, 0.5);
            animation: busyPulse 1s ease-in-out infinite;
        }

        @keyframes busyPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        .status-idle {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #000;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        }

        /* Log Console */
        .log-console {
            background: #000;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            height: 500px;
            overflow-y: auto;
        }
        .log-entry {
            margin-bottom: 5px;
            border-bottom: 1px solid #111;
            padding-bottom: 2px;
        }
        .log-time { color: #666; margin-right: 10px; }
        .log-INFO { color: #e0e0e0; }
        .log-WARNING { color: var(--warning); }
        .log-ERROR { color: var(--danger); font-weight: bold; }

        /* Stats Grid */
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }

        .stat {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }

        .stat:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: var(--accent);
        }

        .stat-label {
            font-size: 0.85em;
            color: var(--text-dim);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--text);
        }

        .stat-value.good { color: var(--success); }
        .stat-value.warn { color: var(--warning); }
        .stat-value.crit { color: var(--danger); }

        /* Buttons */
        .buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }

        .btn {
            padding: 16px 20px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent), #0099cc);
            color: #000;
        }

        .btn-success {
            background: linear-gradient(135deg, var(--success), #00cc66);
            color: #000;
        }

        .btn-warning {
            background: linear-gradient(135deg, var(--warning), #ff8800);
            color: #000;
        }

        .btn-danger {
            background: linear-gradient(135deg, var(--danger), #cc0000);
            color: #fff;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .badge-success { background: var(--success); color: #000; }
        .badge-warning { background: var(--warning); color: #000; }
        .badge-danger { background: var(--danger); color: #fff; }
        .badge-info { background: var(--accent); color: #000; }

        /* Connection List */
        .connection-list {
            max-height: 400px;
            overflow-y: auto;
            padding-right: 10px;
        }

        .connection-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            transition: all 0.3s;
        }

        .connection-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(5px);
        }

        .connection-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .connection-ip {
            font-family: 'Courier New', monospace;
            color: var(--accent);
            font-weight: bold;
            font-size: 1.1em;
        }

        .connection-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            font-size: 0.9em;
            color: var(--text-dim);
        }

        .connection-detail {
            display: flex;
            flex-direction: column;
        }

        .connection-detail-label {
            font-size: 0.8em;
            color: var(--text-dim);
        }

        .connection-detail-value {
            color: var(--text);
            font-weight: bold;
        }

        /* Skills Management */
        .skill-item {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }

        .skill-item:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: var(--accent);
        }

        .skill-name {
            font-size: 1.1em;
            font-weight: 500;
        }

        .skill-toggle {
            position: relative;
            width: 60px;
            height: 30px;
            cursor: pointer;
        }

        .skill-toggle input {
            display: none;
        }

        .skill-toggle-slider {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #333;
            border-radius: 30px;
            transition: 0.3s;
        }

        .skill-toggle-slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background: white;
            border-radius: 50%;
            transition: 0.3s;
        }

        .skill-toggle input:checked + .skill-toggle-slider {
            background: var(--success);
        }

        .skill-toggle input:checked + .skill-toggle-slider:before {
            transform: translateX(30px);
        }

        /* Progress Bar */
        .progress-bar {
            height: 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--success));
            transition: width 0.5s;
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        /* Gauge */
        .gauge {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 20px auto;
        }

        .gauge-circle {
            transform: rotate(-90deg);
        }

        .gauge-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            font-weight: bold;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 50px;
            color: var(--text-dim);
            font-size: 1.1em;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--accent);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--success);
        }

        /* Toast Notifications */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--card);
            border: 1px solid var(--accent);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 40px var(--shadow);
            z-index: 1000;
            animation: slideIn 0.3s;
        }

        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        /* Presence-specific styles */
        .presence-mode-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            margin: 10px 0;
        }

        .presence-mode-badge.work_day {
            background: linear-gradient(135deg, #4a90d9, #357abd);
            color: #fff;
        }

        .presence-mode-badge.free_day {
            background: linear-gradient(135deg, #ff6b9d, #c44569);
            color: #fff;
        }

        .presence-mode-badge.weekend {
            background: linear-gradient(135deg, #a29bfe, #6c5ce7);
            color: #fff;
        }

        .presence-mode-badge.home_office {
            background: linear-gradient(135deg, #fdcb6e, #f39c12);
            color: #000;
        }

        .presence-mode-badge.unknown {
            background: linear-gradient(135deg, #636e72, #2d3436);
            color: #fff;
        }

        .prediction-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.1));
            border: 1px solid var(--accent);
            border-radius: 15px;
            padding: 20px;
            margin-top: 15px;
        }

        .prediction-time {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--accent);
            text-align: center;
        }

        .prediction-window {
            text-align: center;
            color: var(--text-dim);
            font-size: 0.95em;
            margin-top: 5px;
        }

        .confidence-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 15px;
        }

        .confidence-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s, background 0.5s;
        }

        .confidence-fill.high {
            background: linear-gradient(90deg, var(--success), #00cc66);
        }

        .confidence-fill.medium {
            background: linear-gradient(90deg, var(--warning), #ff8800);
        }

        .confidence-fill.low {
            background: linear-gradient(90deg, var(--danger), #cc0000);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .grid, .grid-2 {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 2em;
            }

            .connection-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Pi-Control Ultimate</h1>
            <div class="subtitle">Goal-Oriented Intelligent Agent • v8.0</div>
            <div class="header-stats">
                <div class="header-stat">
                    <div class="header-stat-value" id="total-utility">0%</div>
                    <div class="header-stat-label">Total Utility</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-value" id="observations-count">0</div>
                    <div class="header-stat-label">Observations</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-value" id="active-tests">0</div>
                    <div class="header-stat-label">A/B Tests</div>
                </div>
            </div>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📊 Übersicht</button>
            <button class="tab" onclick="showTab('nas')">🖥️ NAS Control</button>
            <button class="tab" onclick="showTab('events')">📝 NAS Events</button>
            <button class="tab" onclick="showTab('presence')">🏠 Presence</button>
            <button class="tab" onclick="showTab('connections')">🔌 Verbindungen</button>
            <button class="tab" onclick="showTab('system')">⚙️ System</button>
            <button class="tab" onclick="showTab('ai-learning')">🤖 AI Learning</button>
            <button class="tab" onclick="showTab('goals')">🎯 Goals</button>
            <button class="tab" onclick="showTab('skills')">🔧 Skills</button>
            <button class="tab" onclick="showTab('learning')">🧠 Learning</button>
            <button class="tab" onclick="showTab('logs')">📜 Logs</button>
            <!-- SKILL_TABS_PLACEHOLDER -->
            </div>

        <div id="tab-overview" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h2>🖥️ NAS Status</h2>
                    <div id="nas-status-quick" class="status-display status-offline">OFFLINE</div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">State</div>
                            <div class="stat-value" id="nas-state-quick">Unknown</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Load</div>
                            <div class="stat-value" id="nas-load-quick">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Connections</div>
                            <div class="stat-value good" id="nas-conn-quick">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Idle</div>
                            <div class="stat-value" id="nas-idle-quick">0m</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🔥 System Health</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">CPU Temp</div>
                            <div class="stat-value" id="cpu-temp-quick">--°C</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">CPU Usage</div>
                            <div class="stat-value" id="cpu-usage-quick">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">RAM Usage</div>
                            <div class="stat-value" id="ram-usage-quick">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Governor</div>
                            <div class="stat-value" style="font-size:1em" id="governor-quick">...</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>⚡ Quick Actions</h2>
                    <div class="buttons">
                        <button class="btn btn-success" onclick="sendAction('wake')">
                            🌟 Wake NAS
                        </button>
                        <button class="btn btn-warning" onclick="sendAction('suspend')">
                            💤 Suspend Request
                        </button>
                        <button class="btn btn-danger" onclick="sendAction('force_suspend')">
                            🛑 Force Suspend
                        </button>
                    </div>
                </div>

                <div class="card">
                    <h2>🧠 Decision Engine</h2>
                    <div class="stat">
                        <div class="stat-label">Last Decision</div>
                        <div class="stat-value" style="font-size:1.1em" id="last-decision">--</div>
                    </div>
                    <div class="stat" style="margin-top:15px">
                        <div class="stat-label">Current Plan</div>
                        <div class="stat-value" style="font-size:0.9em" id="current-plan">No active plan</div>
                    </div>
                </div>
            </div>
        </div>


        <div id="tab-ai-learning" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>🤖 AI Learning System</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Bayesian Contexts</div>
                            <div class="stat-value" id="ai-bayesian-contexts">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Q-Learning Updates</div>
                            <div class="stat-value" id="ai-ql-updates">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total AI Observations</div>
                            <div class="stat-value" id="ai-total-obs">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Avg Q-Value</div>
                            <div class="stat-value" id="ai-avg-q">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🎯 AI Prediction</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">NAS Usage Probability</div>
                            <div class="stat-value" id="ai-nas-prob">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Recommended Action</div>
                            <div class="stat-value" id="ai-recommended">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Confidence</div>
                            <div class="stat-value" id="ai-confidence">-</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-nas" class="tab-content">
            <div class="grid grid-2">
                <div class="card">
                    <h2>🖥️ NAS Status & Control</h2>
                    <div id="nas-status-full" class="status-display status-offline">OFFLINE</div>

                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">IP Address</div>
                            <div class="stat-value" style="font-size:1.1em" id="nas-ip">...</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">State</div>
                            <div class="stat-value" id="nas-state">...</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Load</div>
                            <div class="stat-value" id="nas-load">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Active Connections</div>
                            <div class="stat-value good" id="nas-connections">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">CPU Usage</div>
                            <div class="stat-value" id="nas-cpu">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">RAM Usage</div>
                            <div class="stat-value" id="nas-ram">0%</div>
                        </div>
                    </div>

                    <h3 style="margin-top:25px; margin-bottom:15px; color:var(--accent)">Control Actions</h3>
                    <div class="buttons">
                        <button class="btn btn-success" onclick="sendAction('wake')">
                            🌟 Wake on LAN
                        </button>
                        <button class="btn btn-warning" onclick="sendAction('suspend')">
                            💤 Suspend Request (UDP)
                        </button>
                        <button class="btn btn-danger" onclick="sendAction('force_suspend')">
                            🛑 Force Suspend (SSH)
                        </button>
                    </div>
                </div>

                <div class="card">
                    <h2>📊 NAS Statistics</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Total WoL Sent</div>
                            <div class="stat-value" id="total-wol">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Shutdowns</div>
                            <div class="stat-value" id="total-shutdowns">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Idle Time</div>
                            <div class="stat-value" id="idle-time">0m</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Last Activity</div>
                            <div class="stat-value" style="font-size:1em" id="last-activity">--</div>
                        </div>
                    </div>

                    <h3 style="margin-top:25px; margin-bottom:15px; color:var(--accent)">Probability Analysis</h3>
                    <div>
                        <div class="stat-label">NAS Needed Probability</div>
                        <div class="progress-bar">
                            <div id="nas-prob-bar" class="progress-fill" style="width:0%"></div>
                        </div>
                        <div style="text-align:right; color:var(--text-dim); margin-top:5px" id="nas-prob-pct">0%</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-events" class="tab-content">
            <div class="grid grid-2">
                <div class="card">
                    <h2>📝 NAS Event History</h2>
                    <p style="color:var(--text-dim); margin-bottom:15px">Alle Wake/Sleep-Aktionen mit Zeitstempel und Auslöser</p>
                    <div id="nas-events-list" class="log-console" style="height:400px">
                        <div class="empty-state">Keine Events aufgezeichnet</div>
                    </div>
                </div>

                <div class="card">
                    <h2>🛡️ Manual Override Status</h2>
                    <div id="override-status" class="status-display status-offline" style="font-size:1.5em">
                        INAKTIV
                    </div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Override Action</div>
                            <div class="stat-value" id="override-action">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Verbleibend</div>
                            <div class="stat-value" id="override-remaining">-</div>
                        </div>
                    </div>
                    <p style="color:var(--text-dim); margin-top:15px; font-size:0.9em">
                        Manual Override wird aktiv, wenn du Wake/Suspend manuell auslöst.
                        Die KI trifft dann für 10-15 Minuten keine NAS-Entscheidungen.
                    </p>
                    <button class="btn btn-warning" style="margin-top:15px" onclick="sendAction('clear_override')">
                        🔓 Override aufheben
                    </button>
                </div>
            </div>

            <div class="grid grid-full" style="margin-top:20px">
                <div class="card">
                    <h2>📊 Event Statistik</h2>
                    <div class="stats" style="grid-template-columns: repeat(5, 1fr)">
                        <div class="stat">
                            <div class="stat-label">AI Wakes</div>
                            <div class="stat-value good" id="stat-ai-wakes">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Proxy Wakes</div>
                            <div class="stat-value" id="stat-proxy-wakes">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Manual Wakes</div>
                            <div class="stat-value" id="stat-manual-wakes">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Idle Sleeps</div>
                            <div class="stat-value" id="stat-idle-sleeps">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Away Sleeps</div>
                            <div class="stat-value warning" id="stat-away-sleeps">0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ==================== PRESENCE TAB ==================== -->
        <div id="tab-presence" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>🏠 Presence Status</h2>
                    <div id="presence-status" class="status-display status-online">ZUHAUSE</div>

                    <div style="text-align:center; margin: 15px 0;">
                        <div id="presence-mode-badge" class="presence-mode-badge unknown">
                            <span id="presence-mode-icon">❓</span>
                            <span id="presence-mode-text">Unbekannt</span>
                        </div>
                    </div>

                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Tages-Modus</div>
                            <div class="stat-value" style="font-size:1.2em" id="presence-day-mode">Unbekannt</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Erkannt um</div>
                            <div class="stat-value" id="presence-mode-time">--:--</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Grund</div>
                            <div class="stat-value" style="font-size:0.9em" id="presence-mode-reason">--</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">User Status</div>
                            <div class="stat-value" id="presence-user-status">Zuhause</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🔮 Aktuelle Vorhersage</h2>
                    <div id="presence-prediction-container">
                        <div class="prediction-card">
                            <div class="stat-label" style="text-align:center">Erwartete Rückkehr</div>
                            <div class="prediction-time" id="presence-return-time">--:--</div>
                            <div class="prediction-window" id="presence-window">Zeitfenster: -- bis --</div>

                            <div style="margin-top:20px">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px">
                                    <span class="stat-label">Konfidenz</span>
                                    <span id="presence-confidence-pct">--%</span>
                                </div>
                                <div class="confidence-bar">
                                    <div id="presence-confidence-bar" class="confidence-fill medium" style="width:0%"></div>
                                </div>
                            </div>
                        </div>

                        <div class="stats" style="margin-top:15px">
                            <div class="stat">
                                <div class="stat-label">Kategorie</div>
                                <div class="stat-value" style="font-size:1.2em" id="presence-category">--</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Basierend auf</div>
                                <div class="stat-value" style="font-size:1em" id="presence-sample-size">-- Events</div>
                            </div>
                        </div>
                    </div>

                    <div id="presence-no-prediction" style="display:none">
                        <div class="empty-state">
                            <div style="font-size:3em; margin-bottom:15px">🏠</div>
                            <div>User ist zuhause</div>
                            <div style="font-size:0.9em; margin-top:10px; color:var(--text-dim)">
                                Vorhersage wird angezeigt wenn User das Haus verlässt
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>📈 Lern-Statistiken</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">💼 Arbeitstage erfasst</div>
                            <div class="stat-value good" id="presence-work-count">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Ø Arbeitszeit</div>
                            <div class="stat-value" id="presence-work-avg">--h</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">🛒 Short Trips erfasst</div>
                            <div class="stat-value" id="presence-short-count">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Ø Trip-Dauer</div>
                            <div class="stat-value" id="presence-short-avg">--min</div>
                        </div>
                    </div>

                    <div style="margin-top:20px; padding-top:15px; border-top:1px solid var(--border)">
                        <div class="stat-label">Gesamt gelernte Events</div>
                        <div class="progress-bar" style="margin-top:10px">
                            <div id="presence-learning-bar" class="progress-fill" style="width:0%"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:5px; font-size:0.9em; color:var(--text-dim)">
                            <span id="presence-total-events">0 Events</span>
                            <span>Ziel: 50+</span>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>📅 Typische Zeiten</h2>
                    <div id="presence-typical-times">
                        <div class="stat" style="margin-bottom:10px">
                            <div class="stat-label">Mo-Fr Abgang</div>
                            <div class="stat-value" style="font-size:1.3em" id="presence-typical-departure">--:--</div>
                        </div>
                        <div class="stat" style="margin-bottom:10px">
                            <div class="stat-label">Mo-Fr Rückkehr</div>
                            <div class="stat-value" style="font-size:1.3em" id="presence-typical-return">--:--</div>
                        </div>
                    </div>

                    <div style="margin-top:20px; padding-top:15px; border-top:1px solid var(--border)">
                        <div class="stat-label" style="margin-bottom:10px">Kategorien-Verteilung</div>
                        <div style="display:flex; gap:10px; flex-wrap:wrap">
                            <span class="badge badge-info">💼 Work: <span id="presence-cat-work">0</span></span>
                            <span class="badge badge-success">🛒 Short: <span id="presence-cat-short">0</span></span>
                            <span class="badge" style="background:#636e72; color:#fff">🚶 Micro: ignored</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- ==================== END PRESENCE TAB ==================== -->

        <div id="tab-connections" class="tab-content">
            <div class="grid grid-full">
                <div class="card">
                    <h2>🔌 Active Proxy Connections</h2>
                    <div class="stats" style="grid-template-columns: repeat(4, 1fr); margin-bottom:20px">
                        <div class="stat">
                            <div class="stat-label">Active Now</div>
                            <div class="stat-value good" id="conn-active">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Sessions</div>
                            <div class="stat-value" id="conn-total">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Data Transfer</div>
                            <div class="stat-value" id="conn-data">0 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Avg per Session</div>
                            <div class="stat-value" id="conn-avg">0 KB</div>
                        </div>
                    </div>

                    <div id="connection-list" class="connection-list">
                        <div class="empty-state">Keine aktiven Verbindungen</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-system" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>⚙️ CPU Governor</h2>
                    <div class="stat">
                        <div class="stat-label">Current Governor</div>
                        <div class="stat-value" style="font-size:1.3em" id="current-governor">...</div>
                    </div>

                    <h3 style="margin-top:25px; margin-bottom:15px; color:var(--accent)">Available Governors</h3>
                    <div id="governor-buttons" class="buttons">
                        </div>
                </div>

                <div class="card">
                    <h2>📊 System Metrics</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">CPU Temperature</div>
                            <div class="stat-value" id="cpu-temp">--°C</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">CPU Usage</div>
                            <div class="stat-value" id="cpu-usage">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">RAM Usage</div>
                            <div class="stat-value" id="ram-usage">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Devices Online</div>
                            <div class="stat-value" id="devices-online">0</div>
                        </div>
                    </div>
                    <div id="device-list-container" style="margin-top:15px; padding-top:15px; border-top:1px solid #333">
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-goals" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>🎯 Energy Saving</h2>
                    <div class="progress-bar">
                        <div id="goal-energy-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-energy-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Weight</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-energy-weight">40%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Utility</div>
                            <div class="stat-value" id="goal-energy-util">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>⚡ Responsiveness</h2>
                    <div class="progress-bar">
                        <div id="goal-resp-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-resp-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Weight</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-resp-weight">30%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Utility</div>
                            <div class="stat-value" id="goal-resp-util">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🛡️ Stability</h2>
                    <div class="progress-bar">
                        <div id="goal-stab-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-stab-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Weight</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-stab-weight">20%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Utility</div>
                            <div class="stat-value" id="goal-stab-util">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>📚 Learning & Curiosity</h2>
                    <div class="progress-bar">
                        <div id="goal-learn-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-learn-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Curiosity Gain</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-curiosity-gain">0.0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Learning Utility</div>
                            <div class="stat-value" id="goal-learn-util">0.0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-skills" class="tab-content">
            <div class="grid grid-full">
                <div class="card">
                    <h2>🔧 Skills Management</h2>
                    <div id="skills-list">
                        </div>
                </div>
            </div>
        </div>

        <div id="tab-learning" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>🧠 Bayesian Learning</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Total Observations</div>
                            <div class="stat-value" id="bayesian-obs">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Prior Probability</div>
                            <div class="stat-value" id="bayesian-prior">30%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Current Learning Rate</div>
                            <div class="stat-value" style="font-size:1.2em" id="learning-rate">0.05</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Current Zone</div>
                            <div class="stat-value" style="font-size:1.2em" id="current-zone-display">unknown</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🔬 A/B Testing</h2>
                    <div id="ab-tests">
                        </div>
                </div>

                <div class="card">
                    <h2>🎯 GOAP Planner</h2>
                    <div class="stat">
                        <div class="stat-label">Current Plan</div>
                        <div class="stat-value" style="font-size:1em" id="goap-plan">No plan</div>
                    </div>
                    <div class="stat" style="margin-top:15px">
                        <div class="stat-label">Progress</div>
                        <div class="stat-value" id="goap-progress">0/0</div>
                    </div>
                </div>

                <div class="card">
                    <h2>🎲 MCDM Governor</h2>
                    <div id="mcdm-scores">
                        </div>
                </div>
            </div>
        </div>

        <div id="tab-logs" class="tab-content">
            <div class="card">
                <h2>📜 System Live Logs</h2>
                <div id="log-container" class="log-console">
                    </div>
            </div>
        </div>

        <!-- SKILL_CONTENT_PLACEHOLDER -->


    </div>

    <script>
        // Configuration
        const UPDATE_INTERVAL = 2000; // 2 seconds

        let currentTab = 'overview';

        // Show Tab
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

            document.getElementById('tab-' + tabName).classList.add('active');

            // Fix: Find the button that was clicked and activate it
            const buttons = document.getElementsByClassName('tab');
            for(let btn of buttons) {
                if(btn.innerText.includes(tabName.replace('-', ' ').toUpperCase()) ||
                   btn.getAttribute('onclick').includes(tabName)) {
                    btn.classList.add('active');
                }
            }

            currentTab = tabName;
        }

        // Send Action
        function sendAction(action) {
            fetch(`/api/action?action=${action}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`✅ Action: ${action}`, 'success');
                    } else {
                        showToast(`❌ Failed: ${data.message || 'Unknown error'}`, 'error');
                    }
                })
                .catch(e => {
                    console.error('Action error:', e);
                    showToast('❌ Network error', 'error');
                });
        }

        // Toggle Skill
        function toggleSkill(skillName, enabled) {
            const action = enabled ? 'enable' : 'disable';
            fetch(`/api/skill/${action}?name=${skillName}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`Skill ${skillName}: ${action}d`, 'success');
                    }
                })
                .catch(e => console.error('Skill toggle error:', e));
        }

        // Set Governor
        function setGovernor(gov) {
            fetch(`/api/action?action=set_governor_${gov}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`Governor set to: ${gov}`, 'success');
                    }
                })
                .catch(e => console.error('Governor error:', e));
        }

        // Show Toast
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);

            setTimeout(() => toast.remove(), 3000);
        }

        // Format helpers
        function formatTime(timestamp) {
            if (!timestamp) return '--';
            const mins = Math.floor((Date.now()/1000 - timestamp) / 60);
            if (mins < 1) return 'jetzt';
            if (mins < 60) return mins + 'm';
            const hours = Math.floor(mins / 60);
            if (hours < 24) return hours + 'h';
            return Math.floor(hours / 24) + 'd';
        }

        function formatBytes(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB';
            return (bytes/(1024*1024)).toFixed(2) + ' MB';
        }

        function formatDuration(seconds) {
            if (seconds < 60) return seconds.toFixed(0) + 's';
            if (seconds < 3600) return (seconds/60).toFixed(1) + 'm';
            return (seconds/3600).toFixed(1) + 'h';
        }

        // Update UI
        function updateUI() {
            fetch('/api/state')
                .then(r => r.json())
                .then(data => {
                    updateOverview(data);
                    updateNAS(data);
                    updateConnections(data);
                    updateSystem(data);
                    updateGoals(data);
                    updateSkills(data);
                    updateLearning(data);
                    updateAILearning(data);
                    updatePresence(data);
                    updateLogs(data.logs);
                    updateEvents(data);
                })
                .catch(e => console.error('Update error:', e));
        }


        function updateOverview(data) {
            const s = data.state;
            const d = data.decision;

            // Header stats
            document.getElementById('total-utility').textContent =
                (d.total_utility * 100).toFixed(0) + '%';
            document.getElementById('observations-count').textContent =
                data.probabilistic.total_observations;
            document.getElementById('active-tests').textContent =
                Object.keys(data.ab_tests || {}).length;

            // NAS Status Quick
            const nasStatus = s.nas_status.online ?
                (s.nas_status.state === 'busy' ? 'BUSY' :
                 s.nas_status.state === 'idle' ? 'IDLE' : 'ONLINE') :
                'OFFLINE';

            const statusElem = document.getElementById('nas-status-quick');
            statusElem.textContent = nasStatus;
            statusElem.className = 'status-display status-' +
                (nasStatus === 'OFFLINE' ? 'offline' :
                 nasStatus === 'BUSY' ? 'busy' :
                 nasStatus === 'IDLE' ? 'idle' : 'online');

            document.getElementById('nas-state-quick').textContent = s.nas_status.state;
            document.getElementById('nas-load-quick').textContent =
                (s.nas_status.load * 100).toFixed(0) + '%';
            document.getElementById('nas-conn-quick').textContent = s.nas_status.connections;
            document.getElementById('nas-idle-quick').textContent =
                Math.floor((Date.now()/1000 - s.last_activity_ts) / 60) + 'm';

            // System Health Quick
            const temp = s.system_metrics.cpu_temp;
            const tempElem = document.getElementById('cpu-temp-quick');
            tempElem.textContent = temp.toFixed(1) + '°C';
            tempElem.className = 'stat-value';
            if (temp >= 75) tempElem.classList.add('crit');
            else if (temp >= 65) tempElem.classList.add('warn');
            else tempElem.classList.add('good');

            document.getElementById('cpu-usage-quick').textContent =
                s.system_metrics.cpu_usage.toFixed(1) + '%';
            document.getElementById('ram-usage-quick').textContent =
                s.system_metrics.ram_usage.toFixed(1) + '%';
            document.getElementById('governor-quick').textContent = s.current_governor;

            // Decision Status
            document.getElementById('last-decision').textContent =
                d.last_decision || 'None';
            document.getElementById('current-plan').textContent =
                d.current_plan.length > 0 ? d.current_plan.join(' → ') : 'No active plan';
        }

        function updateNAS(data) {
            const s = data.state;
            const p = data.probabilistic;

            // Full Status
            const nasStatus = s.nas_status.online ?
                (s.nas_status.state === 'busy' ? 'BUSY' :
                 s.nas_status.state === 'idle' ? 'IDLE' : 'ONLINE') :
                'OFFLINE';

            const statusElem = document.getElementById('nas-status-full');
            statusElem.textContent = nasStatus;
            statusElem.className = 'status-display status-' +
                (nasStatus === 'OFFLINE' ? 'offline' :
                 nasStatus === 'BUSY' ? 'busy' :
                 nasStatus === 'IDLE' ? 'idle' : 'online');

            document.getElementById('nas-ip').textContent = data.config.nas.ip;
            document.getElementById('nas-state').textContent = s.nas_status.state;
            document.getElementById('nas-load').textContent =
                (s.nas_status.load * 100).toFixed(0) + '%';
            document.getElementById('nas-connections').textContent = s.nas_status.connections;
            document.getElementById('nas-cpu').textContent =
                (s.nas_status.cpu || 0).toFixed(1) + '%';
            document.getElementById('nas-ram').textContent =
                (s.nas_status.ram || 0).toFixed(1) + '%';

            // Statistics
            document.getElementById('total-wol').textContent = s.total_wol || 0;
            document.getElementById('total-shutdowns').textContent = s.total_shutdowns || 0;

            const idleMins = Math.floor((Date.now()/1000 - s.last_activity_ts) / 60);
            document.getElementById('idle-time').textContent = idleMins + 'm';
            document.getElementById('last-activity').textContent = formatTime(s.last_activity_ts);

            // Probability
            const prob = p.probability * 100;
            document.getElementById('nas-prob-bar').style.width = prob + '%';
            document.getElementById('nas-prob-pct').textContent = prob.toFixed(1) + '%';
        }

        function updateConnections(data) {
            const conns = data.connections || [];
            const stats = data.proxy_stats;

            // Stats
            document.getElementById('conn-active').textContent = conns.length;
            document.getElementById('conn-total').textContent = stats.total_connections;
            document.getElementById('conn-data').textContent = stats.total_data_mb.toFixed(2) + ' MB';

            const avgKB = stats.total_connections > 0 ?
                (stats.total_data_mb * 1024) / stats.total_connections : 0;
            document.getElementById('conn-avg').textContent = avgKB.toFixed(1) + ' KB';

            // Connection List
            const container = document.getElementById('connection-list');

            if (conns.length === 0) {
                container.innerHTML = '<div class="empty-state">Keine aktiven Verbindungen</div>';
                return;
            }

            let html = '';
            conns.forEach(conn => {
                const totalBytes = conn.bytes_sent + conn.bytes_received;
                html += `
                    <div class="connection-item">
                        <div class="connection-header">
                            <div class="connection-ip">${conn.client_ip}:${conn.client_port}</div>
                            <span class="badge badge-success">ACTIVE</span>
                        </div>
                        <div class="connection-details">
                            <div class="connection-detail">
                                <span class="connection-detail-label">Target Port</span>
                                <span class="connection-detail-value">${conn.target_port}</span>
                            </div>
                            <div class="connection-detail">
                                <span class="connection-detail-label">Duration</span>
                                <span class="connection-detail-value">${formatDuration(conn.duration)}</span>
                            </div>
                            <div class="connection-detail">
                                <span class="connection-detail-label">Data Transfer</span>
                                <span class="connection-detail-value">${formatBytes(totalBytes)}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function updateSystem(data) {
            const s = data.state;

            // Current Governor
            document.getElementById('current-governor').textContent = s.current_governor;

            // Metrics
            const temp = s.system_metrics.cpu_temp;
            const tempElem = document.getElementById('cpu-temp');
            tempElem.textContent = temp.toFixed(1) + '°C';
            tempElem.className = 'stat-value';
            if (temp >= 75) tempElem.classList.add('crit');
            else if (temp >= 65) tempElem.classList.add('warn');
            else tempElem.classList.add('good');

            document.getElementById('cpu-usage').textContent =
                s.system_metrics.cpu_usage.toFixed(1) + '%';
            document.getElementById('ram-usage').textContent =
                s.system_metrics.ram_usage.toFixed(1) + '%';
            document.getElementById('devices-online').textContent = s.devices_online;

            // NEU: Geräte-Liste anzeigen
            const deviceStatus = s.device_status || {};
            const onlineDevices = Object.keys(deviceStatus)
                .filter(key => deviceStatus[key] === true)
                .map(key => key.replace('_online', '').replace(/_/g, ' ')); // Namen schön machen

            const deviceListContainer = document.getElementById('device-list-container');
            if (onlineDevices.length > 0) {
                deviceListContainer.innerHTML = onlineDevices.map(d =>
                    `<span class="badge badge-success" style="margin-right:5px; margin-bottom:5px; display:inline-block">${d}</span>`
                ).join('');
            } else {
                deviceListContainer.innerHTML = '<span style="color:var(--text-dim)">Keine Geräte online</span>';
            }

            // Governor Buttons (only once)
            if (!window.governorButtonsCreated) {
                const govContainer = document.getElementById('governor-buttons');
                const govs = data.config.cpu_governors.available;

                govContainer.innerHTML = govs.map(gov =>
                    `<button class="btn btn-primary" onclick="setGovernor('${gov}')">${gov}</button>`
                ).join('');

                window.governorButtonsCreated = true;
            }
        }

        function updateGoals(data) {
            const goals = data.goals || {};

            // Energy
            if (goals.energy_saving) {
                const sat = goals.energy_saving.satisfaction * 100;
                document.getElementById('goal-energy-bar').style.width = sat + '%';
                document.getElementById('goal-energy-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-energy-weight').textContent =
                    (goals.energy_saving.weight * 100).toFixed(0) + '%';
                document.getElementById('goal-energy-util').textContent =
                    goals.energy_saving.utility.toFixed(3);
            }

            // Responsiveness
            if (goals.responsiveness) {
                const sat = goals.responsiveness.satisfaction * 100;
                document.getElementById('goal-resp-bar').style.width = sat + '%';
                document.getElementById('goal-resp-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-resp-weight').textContent =
                    (goals.responsiveness.weight * 100).toFixed(0) + '%';
                document.getElementById('goal-resp-util').textContent =
                    goals.responsiveness.utility.toFixed(3);
            }

            // Stability
            if (goals.stability) {
                const sat = goals.stability.satisfaction * 100;
                document.getElementById('goal-stab-bar').style.width = sat + '%';
                document.getElementById('goal-stab-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-stab-weight').textContent =
                    (goals.stability.weight * 100).toFixed(0) + '%';
                document.getElementById('goal-stab-util').textContent =
                    goals.stability.utility.toFixed(3);
            }

            // Learning & Curiosity
            if (goals.learning && goals.curiosity) {
                const sat = goals.learning.satisfaction * 100;
                document.getElementById('goal-learn-bar').style.width = sat + '%';
                document.getElementById('goal-learn-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-curiosity-gain').textContent =
                    goals.curiosity.current.toFixed(3);
                document.getElementById('goal-learn-util').textContent =
                    (goals.learning.utility + goals.curiosity.utility).toFixed(3);
            }
        }

        function updateSkills(data) {
            const skills = data.skills || [];
            const container = document.getElementById('skills-list');

            if (skills.length === 0) {
                container.innerHTML = '<div class="empty-state">No skills available</div>';
                return;
            }

            let html = '';
            skills.forEach(skill => {
                html += `
                    <div class="skill-item">
                        <div class="skill-name">🔧 ${skill.name}</div>
                        <label class="skill-toggle">
                            <input type="checkbox" ${skill.enabled ? 'checked' : ''}
                                   onchange="toggleSkill('${skill.name}', this.checked)">
                            <span class="skill-toggle-slider"></span>
                        </label>
                    </div>
                `;
            });

            // Avoid flickering by only updating if changed (simple check)
            if(container.childElementCount !== skills.length || container.innerHTML.includes('No skills')) {
                 container.innerHTML = html;
            }
        }

        function updateLearning(data) {
            const s = data.state;
            const p = data.probabilistic;
            const ab = data.ab_tests || {};
            const d = data.decision;

            // Bayesian
            document.getElementById('bayesian-obs').textContent = p.total_observations;
            document.getElementById('bayesian-prior').textContent =
                (p.probability * 100).toFixed(0) + '%';
            document.getElementById('learning-rate').textContent =
                p.learning_rate.toFixed(3);
            document.getElementById('current-zone-display').textContent =
                s.current_zone;

            // A/B Tests
            const abContainer = document.getElementById('ab-tests');
            const testNames = Object.keys(ab);

            if (testNames.length === 0) {
                abContainer.innerHTML = '<div class="empty-state">No active tests</div>';
            } else {
                let html = '';
                testNames.forEach(name => {
                    html += `<div class="stat"><div class="stat-label">${name}</div>
                             <div class="stat-value" style="font-size:1em">Active</div></div>`;
                });
                abContainer.innerHTML = html;
            }

            // GOAP
            document.getElementById('goap-plan').textContent =
                d.current_plan.length > 0 ? d.current_plan.join(' → ') : 'No plan';
            document.getElementById('goap-progress').textContent = d.plan_progress;
        }

        function updateAILearning(data) {
            if (!data.ai_upgrade) return;

            const ai = data.ai_upgrade;
            const pred = data.state.ai_prediction || {};

            // Stats
            const bayesianContexts = document.getElementById('ai-bayesian-contexts');
            if (bayesianContexts) {
                bayesianContexts.textContent = ai.bayesian.contexts || 0;
            }

            const qlUpdates = document.getElementById('ai-ql-updates');
            if (qlUpdates) {
                qlUpdates.textContent = ai.universal_ql.total_updates || 0;
            }

            const totalObs = document.getElementById('ai-total-obs');
            if (totalObs) {
                totalObs.textContent = ai.total_observations || 0;
            }

            const avgQ = document.getElementById('ai-avg-q');
            if (avgQ) {
                avgQ.textContent = (ai.universal_ql.avg_q_value || 0).toFixed(3);
            }

            // Current Prediction
            const nasProb = document.getElementById('ai-nas-prob');
            if (nasProb) {
                nasProb.textContent = pred.nas_usage_prob ?
                    (pred.nas_usage_prob * 100).toFixed(1) + '%' : '-';
            }

            const recommended = document.getElementById('ai-recommended');
            if (recommended) {
                recommended.textContent = pred.recommended_action || '-';
            }

            const confidence = document.getElementById('ai-confidence');
            if (confidence) {
                confidence.textContent = pred.confidence ?
                    (pred.confidence * 100).toFixed(1) + '%' : '-';
            }
        }

        // ==================== PRESENCE UPDATE FUNCTION ====================
        function updatePresence(data) {
            const presence = data.presence || {};
            const stats = presence.statistics || {};
            const dayMode = presence.day_mode || {};
            const prediction = data.state.presence_prediction || {};

            // Status Display
            const statusEl = document.getElementById('presence-status');
            const userHome = stats.user_is_home !== false; // default true

            if (userHome) {
                statusEl.textContent = 'ZUHAUSE';
                statusEl.className = 'status-display status-online';
                document.getElementById('presence-user-status').textContent = '🏠 Zuhause';
            } else {
                statusEl.textContent = 'UNTERWEGS';
                statusEl.className = 'status-display status-busy';
                document.getElementById('presence-user-status').textContent = '🚶 Unterwegs';
            }

            // Day Mode Badge
            const mode = stats.current_day_mode || dayMode.mode || 'unknown';
            const modeDisplay = stats.day_mode_display || dayMode.display_name || 'Unbekannt';
            const modeBadge = document.getElementById('presence-mode-badge');
            const modeIcon = document.getElementById('presence-mode-icon');
            const modeText = document.getElementById('presence-mode-text');

            modeBadge.className = 'presence-mode-badge ' + mode;

            const modeIcons = {
                'work_day': '💼',
                'free_day': '🏖️',
                'weekend': '🎉',
                'home_office': '🏠',
                'unknown': '❓'
            };

            modeIcon.textContent = modeIcons[mode] || '❓';
            modeText.textContent = modeDisplay;

            document.getElementById('presence-day-mode').textContent = modeDisplay;
            document.getElementById('presence-mode-reason').textContent =
                dayMode.reasoning || '--';

            // Mode detected time
            if (dayMode.detected_at) {
                const detectedDate = new Date(dayMode.detected_at);
                document.getElementById('presence-mode-time').textContent =
                    detectedDate.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'});
            } else {
                document.getElementById('presence-mode-time').textContent = '--:--';
            }

            // Prediction Section
            const predContainer = document.getElementById('presence-prediction-container');
            const noPrediction = document.getElementById('presence-no-prediction');

            if (!userHome && prediction && prediction.expected_return_str) {
                predContainer.style.display = 'block';
                noPrediction.style.display = 'none';

                document.getElementById('presence-return-time').textContent =
                    prediction.expected_return_str || '--:--';
                document.getElementById('presence-window').textContent =
                    `Zeitfenster: ${prediction.window_early || '--'} bis ${prediction.window_late || '--'}`;

                const confidence = (prediction.confidence || 0) * 100;
                document.getElementById('presence-confidence-pct').textContent =
                    confidence.toFixed(0) + '%';

                const confBar = document.getElementById('presence-confidence-bar');
                confBar.style.width = confidence + '%';
                confBar.className = 'confidence-fill ' +
                    (confidence >= 70 ? 'high' : confidence >= 40 ? 'medium' : 'low');

                const catEmojis = {
                    'short_trip': '🛒 Kurzer Trip',
                    'work': '💼 Arbeit',
                    'possibly_longer': '⏳ Evtl. länger'
                };
                document.getElementById('presence-category').textContent =
                    catEmojis[prediction.category] || prediction.category || '--';

                document.getElementById('presence-sample-size').textContent =
                    (prediction.sample_size || 0) + ' Events';
            } else {
                predContainer.style.display = 'none';
                noPrediction.style.display = 'block';
            }

            // Statistics
            document.getElementById('presence-work-count').textContent =
                stats.total_work_absences || 0;
            document.getElementById('presence-work-avg').textContent =
                (stats.work_avg_duration_hours || '--') + 'h';
            document.getElementById('presence-short-count').textContent =
                stats.total_short_trips || 0;
            document.getElementById('presence-short-avg').textContent =
                (stats.short_trip_avg_minutes || '--') + 'min';

            // Learning Progress Bar
            const totalEvents = (stats.total_work_absences || 0) + (stats.total_short_trips || 0);
            const learningPct = Math.min(100, (totalEvents / 50) * 100);
            document.getElementById('presence-learning-bar').style.width = learningPct + '%';
            document.getElementById('presence-total-events').textContent = totalEvents + ' Events';

            // Category badges
            document.getElementById('presence-cat-work').textContent =
                stats.total_work_absences || 0;
            document.getElementById('presence-cat-short').textContent =
                stats.total_short_trips || 0;

            // Typical times (if available in stats)
            if (stats.typical_return_by_weekday) {
                // Calculate average from weekday data
                const times = Object.values(stats.typical_return_by_weekday);
                if (times.length > 0) {
                    document.getElementById('presence-typical-return').textContent =
                        times[0] || '--:--'; // Just show first for now
                }
            }
        }
        // ==================== END PRESENCE UPDATE ====================


        function updateLogs(logs) {
            const container = document.getElementById('log-container');
            if (!logs) return;

            let html = '';
            logs.forEach(log => {
                // Formatiere die Nachricht etwas (entferne Timestamp doppelt wenn nötig)
                // Wir nehmen an, message enthält schon Zeit durch Formatter,
                // aber wir haben Zeit extra in log.time.
                // Einfachheitshalber nutzen wir log.message direkt wenn Formatter gut ist,
                // oder bauen es selbst:

                html += `
                    <div class="log-entry ${'log-' + log.level}">
                        <span class="log-time">[${log.time}]</span>
                        <span>${log.message.split(' - ').slice(2).join(' - ')}</span>
                    </div>
                `;
                // Hinweis: .split slice join entfernt den doppelten Zeitstempel aus der formatierten Message
            });

            // Nur updaten wenn sich was geändert hat (einfacher Check: Länge)
            if (container.innerHTML.length !== html.length) {
                 container.innerHTML = html;
            }
        }

        function updateEvents(data) {
            const events = data.nas_events || [];
            const override = data.manual_override || {};

            // Event Liste
            const container = document.getElementById('nas-events-list');
            if (events.length === 0) {
                container.innerHTML = '<div class="empty-state">Keine Events aufgezeichnet</div>';
            } else {
                let html = '';
                // Events rückwärts (neueste zuerst)
                [...events].reverse().forEach(event => {
                    let icon = '❓';
                    let colorClass = '';

                    if (event.type.includes('wake')) {
                        icon = '🌟';
                        colorClass = 'log-INFO';
                    } else if (event.type.includes('sleep') || event.type.includes('suspend')) {
                        icon = '💤';
                        colorClass = 'log-WARNING';
                    }

                    if (event.source === 'user' || event.source === 'user_manual') {
                        icon = '👆 ' + icon;
                    }

                    html += `
                        <div class="log-entry ${colorClass}">
                            <span class="log-time">[${event.time}]</span>
                            <span>${icon} <strong>${event.type}</strong> by ${event.source}</span>
                            ${event.details ? `<br><span style="color:#888; margin-left:80px">${event.details}</span>` : ''}
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            // Manual Override Status
            const overrideStatus = document.getElementById('override-status');
            const overrideAction = document.getElementById('override-action');
            const overrideRemaining = document.getElementById('override-remaining');

            if (override.active) {
                overrideStatus.textContent = 'AKTIV';
                overrideStatus.className = 'status-display status-busy';
                overrideAction.textContent = override.action || '-';
                const mins = Math.floor(override.remaining_seconds / 60);
                const secs = override.remaining_seconds % 60;
                overrideRemaining.textContent = `${mins}m ${secs}s`;
            } else {
                overrideStatus.textContent = 'INAKTIV';
                overrideStatus.className = 'status-display status-offline';
                overrideAction.textContent = '-';
                overrideRemaining.textContent = '-';
            }

            // Event Statistiken
            let aiWakes = 0, proxyWakes = 0, manualWakes = 0, idleSleeps = 0, awaySleeps = 0;
            events.forEach(e => {
                if (e.type.includes('wake')) {
                    if (e.source === 'ai_prediction') aiWakes++;
                    else if (e.source === 'proxy') proxyWakes++;
                    else if (e.source.includes('user') || e.source.includes('manual')) manualWakes++;
                } else if (e.type.includes('sleep')) {
                    if (e.source === 'idle_timeout') idleSleeps++;
                    else if (e.source === 'away_mode') awaySleeps++;
                }
            });

            document.getElementById('stat-ai-wakes').textContent = aiWakes;
            document.getElementById('stat-proxy-wakes').textContent = proxyWakes;
            document.getElementById('stat-manual-wakes').textContent = manualWakes;
            document.getElementById('stat-idle-sleeps').textContent = idleSleeps;
            document.getElementById('stat-away-sleeps').textContent = awaySleeps;
        }

        // Start updates
        setInterval(updateUI, UPDATE_INTERVAL);
        updateUI();
    </script>
</body>
</html>
"""

# HINWEIS: DashboardCache und dashboard_cache werden jetzt von holo_dashboard.py importiert
# Die alte lokale Klasse wurde entfernt - siehe holo_dashboard.py

# =============================================================================
# FIX 2: DashboardHandler - Korrekte _serve_state() Implementation
# =============================================================================

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for dashboard"""

    def log_message(self, format, *args):
        pass # Quiet mode

    def do_GET(self):
        if self.path == "/api/state":
            self._serve_state()
        else:
            self._serve_dashboard()

    def do_POST(self):
        try:
            # 1. Bestehende Actions
            if self.path.startswith("/api/action"):
                self._handle_action()

            # 2. Skill Enable/Disable
            elif self.path.startswith("/api/skill/enable"):
                self._handle_skill(True)
            elif self.path.startswith("/api/skill/disable"):
                self._handle_skill(False)

            # 3. Generische Interaktion mit Skills (für Chat etc.)
            elif self.path.startswith("/api/skill/interact"):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                skill_name = data.get("skill")
                payload = data.get("payload")

                if 'app' in globals() and skill_name in app.skill_manager.skills:
                    skill = app.skill_manager.skills[skill_name]
                    if hasattr(skill, 'handle_web_request'):
                        response_data = skill.handle_web_request(payload)
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(response_data).encode())
                        return

                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Skill or method not found"}).encode())

            # 🤖 4. NEU: Holo Brain Command Endpoint
            elif self.path.startswith("/api/command"):
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    command = json.loads(post_data.decode('utf-8'))
                else:
                    command = {}

                action = command.get("action")
                params = command.get("params", command.get("parameters", {}))
                reason = command.get("reason", "Holo Brain Request")

                result = {"success": False, "action": action}

                if action in ["wake_nas", "nas_wake"]:
                    state.set_manual_override("wake", duration_minutes=5)
                    result["success"] = True
                    state.add_nas_event("holo_wake", "holo_brain", reason)

                elif action in ["sleep_nas", "nas_sleep"]:
                    state.set_manual_override("sleep", duration_minutes=5)
                    result["success"] = True
                    state.add_nas_event("holo_sleep", "holo_brain", reason)

                elif action == "set_governor":
                    gov = params.get("governor", "ondemand")
                    result["success"] = actors.power.set_governor(gov)

                elif action == "send_notification":
                    logger.info(f"🔔 Holo: {params.get('message', '')}")
                    result["success"] = True

                elif action == "create_calendar_event":
                    # Kalender-Eintrag erstellen
                    summary = params.get("summary")
                    start_dt = params.get("start_datetime")
                    end_dt = params.get("end_datetime")
                    description = params.get("description", "")
                    location = params.get("location", "")

                    if not summary or not start_dt or not end_dt:
                        result["error"] = "Missing required params: summary, start_datetime, end_datetime"
                    else:
                        success = actors.ha.create_calendar_event(
                            summary=summary,
                            start_datetime=start_dt,
                            end_datetime=end_dt,
                            description=description,
                            location=location
                        )
                        result["success"] = success
                        if success:
                            logger.info(f"📅 Holo created calendar event: {summary} ({start_dt})")
                            result["message"] = f"Kalender-Eintrag '{summary}' erstellt"
                        else:
                            result["error"] = "Home Assistant calendar service failed"

                else:
                    result["error"] = f"Unknown action: {action}"

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return

        except Exception as e:
            logger.error(f"POST error: {e}")
            self.send_error(500)

    def _serve_dashboard(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'private, max-age=60')  # Browser-Cache 60s
        self.end_headers()

            # Gecachtes HTML holen
        html = dashboard_cache.get_html(app.skill_manager)
        self.wfile.write(html.encode())

    def _serve_state(self):
        try:
            # Berechne Total Observations - mit Safety Checks
            total_obs = 0
            try:
                total_obs = (
                    len(app.probabilistic_engine.stm_nas) +
                    len(app.probabilistic_engine.stm_no_nas) +
                    app.probabilistic_engine.ltm_data.get("total_nas", 0) +
                    app.probabilistic_engine.ltm_data.get("total_no_nas", 0)
                )
            except Exception as e:
                logger.warning(f"Failed to calculate total_obs: {e}")
                total_obs = 0

            # Safe probability calculation
            probability = 0.5
            try:
                probability = app.probabilistic_engine.predict()
            except Exception as e:
                logger.warning(f"Failed to predict probability: {e}")

            # Safe decision status
            decision_status = {
                "last_decision": "unknown",
                "last_decision_time": 0,
                "current_plan": [],
                "plan_progress": "0/0",
                "total_utility": 0.0,
                "goal_priorities": [],
                "decision_history": []
            }
            try:
                decision_status = app.decision_engine.get_status()
            except Exception as e:
                logger.warning(f"Failed to get decision status: {e}")

            data = {
                "state": state.snapshot(),
                "config": CONFIG,
                "connections": actors.proxy_tracker.get_active_connections(),
                "proxy_stats": actors.proxy_tracker.get_stats(),
                "decision": decision_status,

                "probabilistic": {
                    "probability": probability,
                    "total_observations": total_obs,
                    "learning_rate": getattr(app.probabilistic_engine, 'learning_rate', 0.05),
                },

                "goals": {
                    name: {
                        "satisfaction": goal.satisfaction(),
                        "weight": goal.weight,
                        "utility": goal.utility(),
                        "current": goal.current_value,
                        "target": goal.target_value,
                    }
                    for name, goal in app.goal_manager.goals.items()
                },

                "skills": app.skill_manager.get_skills_status(),

                "ab_tests": {
                    name: test.to_dict()
                    for name, test in app.ab_testing.active_tests.items()
                },

                "logs": list(reversed(memory_log_handler.get_logs())),
                "nas_events": state.get_nas_events(),

                "manual_override": {
                    "active": state.is_manual_override_active(),
                    "action": state.get_manual_override(),
                    "remaining_seconds": max(0, int(state.manual_override_until - now_ts())) if state.is_manual_override_active() else 0,
                },

                "adaptive_timing": actors.adaptive_timing.get_stats() if actors.adaptive_timing else {
                    "online_timeout": 5,
                    "offline_timeout": 40,
                },

                "cognitive_control": app.cognitive_controller.get_stats() if app and hasattr(app, 'cognitive_controller') else {
                    "total_requests": 0,
                    "auto_approved": 0,
                    "rejected": 0,
                },

                # 🆕 AI UPGRADE STATS
                "ai_upgrade": app.ai_integration.get_stats() if app and hasattr(app, 'ai_integration') else {
                    "bayesian": {
                        "calibration": {"bins": [], "accuracies": []},
                        "optimal_hours": [],
                        "contexts": 0
                    },
                    "universal_ql": {
                        "total_observations": 0,
                        "total_updates": 0,
                        "avg_q_value": 0.0
                    },
                    "total_observations": 0,
                    "total_predictions": 0
                },

                # 🏠 PRESENCE ENGINE
                "presence": {
                    "statistics": app.presence_engine.get_statistics() if app and hasattr(app, 'presence_engine') else {},
                    "day_mode": app.presence_engine.get_day_mode() if app and hasattr(app, 'presence_engine') else {},

                },

                "ai_extended": {
                    "semantic_memory": app.ai_integration.semantic_memory.get_stats()
                        if hasattr(app, 'ai_integration') and hasattr(app.ai_integration, 'semantic_memory') else {},
                    "external_context": app.ai_integration.external_context.get_stats()
                        if hasattr(app, 'ai_integration') and hasattr(app.ai_integration, 'external_context') else {},
                    "forecaster": app.ai_integration.forecaster.get_stats()
                        if hasattr(app, 'ai_integration') and hasattr(app.ai_integration, 'forecaster') else {},
                    "causal_learning": app.ai_integration.causal_engine.get_stats()
                        if hasattr(app, 'ai_integration') and hasattr(app.ai_integration, 'causal_engine') else {},
                    "weather": app.ai_integration.external_context.get_weather()
                        if hasattr(app, 'ai_integration') and hasattr(app.ai_integration, 'external_context') else {},
                    "forecast_24h": app.ai_integration.forecaster.forecast("nas_usage", 24)[:6]
                        if hasattr(app, 'ai_integration') and hasattr(app.ai_integration, 'forecaster') else [],
                },

                # Error-Tracking Daten für Dashboard
                "errors": get_error_tracker().get_dashboard_data()
                    if HAVE_ERROR_TRACKER and get_error_tracker else {
                        "statistics": {"total_errors": 0, "errors_last_hour": 0, "most_common": [], "errors_by_module": {}},
                        "recent_errors": [], "critical_count": 0, "warning_count": 0, "error_count": 0
                    },

                # RAM-Manager Daten für Dashboard
                "ram": get_ram_manager().get_dashboard_data()
                    if HAVE_RAM_MANAGER and get_ram_manager else {
                        "stats": {"total_mb": 0, "available_mb": 0, "used_mb": 0, "percent_used": 0,
                                  "cache_size_mb": 0, "items_in_ram": 0, "items_on_disk": 0},
                        "config": {"cache_size_mb": 500, "sd_storage_gb": 16}
                    },

            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())

        except Exception as e:
            logger.error(f"State serve error: {e}", exc_info=True)
            self.send_error(500)


    def _handle_action(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            action = query.get("action", [None])[0]
            result = {"success": False}

            if action == "wake":
                # COGNITIVE: Request through controller
                state.set_manual_override("wake", duration_minutes=10)
                cognitive_result = app.cognitive_controller.request_action(
                    action="wake_nas",
                    source="user_manual",
                    reason="dashboard_button",
                    priority=10,
                    context={"manual_override": True}
                )
                result["success"] = cognitive_result["approved"]
                result["message"] = f"WoL {'sent' if cognitive_result['approved'] else 'rejected'} (Manual Override: 10min)"
                if cognitive_result["approved"]:
                    state.add_nas_event("manual_wake", "user", "Dashboard button pressed")
            elif action == "suspend":
                # COGNITIVE: Request through controller
                state.set_manual_override("sleep", duration_minutes=10)
                cognitive_result = app.cognitive_controller.request_action(
                    action="sleep_nas",
                    source="user_manual",
                    reason="dashboard_button",
                    priority=10,
                    context={"manual_override": True}
                )
                result["success"] = cognitive_result["approved"]
                result["message"] = f"Suspend {'sent' if cognitive_result['approved'] else 'rejected'} (Manual Override: 10min)"
                if cognitive_result["approved"]:
                    state.add_nas_event("manual_suspend", "user", "Dashboard button pressed")
            elif action == "force_suspend":
                result["success"] = actors.nas.force_shutdown_ssh("user_manual")
                # Manual Override setzen: 15 Minuten keine AI-Entscheidungen
                state.set_manual_override("sleep", duration_minutes=15)
                state.add_nas_event("manual_force_suspend", "user", "Dashboard force button pressed")
                result["message"] = "Force suspend via SSH (Manual Override: 15min)"
            elif action == "clear_override":
                # Neuer Action: Manual Override löschen
                state.manual_override_until = 0
                state.manual_override_action = None
                result["success"] = True
                result["message"] = "Manual Override cleared"
            elif action and action.startswith("set_governor_"):
                gov = action.replace("set_governor_", "")
                result["success"] = actors.power.set_governor(gov)
                result["message"] = f"Governor set to {gov}"
            elif action == "clear_errors":
                # Error-Tracker leeren
                if HAVE_ERROR_TRACKER and get_error_tracker:
                    get_error_tracker().clear_errors()
                    result["success"] = True
                    result["message"] = "Errors cleared"
                else:
                    result["success"] = False
                    result["message"] = "Error tracker not available"
            elif action == "ram_cleanup":
                # RAM-Cache leeren
                if HAVE_RAM_MANAGER and get_ram_manager:
                    get_ram_manager().flush_all()
                    result["success"] = True
                    result["message"] = "RAM cache flushed"
                else:
                    result["success"] = False
                    result["message"] = "RAM manager not available"
            elif action == "disk_cleanup":
                # Disk-Cache leeren
                if HAVE_RAM_MANAGER and get_ram_manager:
                    manager = get_ram_manager()
                    if hasattr(manager, '_cleanup_old_sd_files'):
                        manager._cleanup_old_sd_files(force=True)
                    result["success"] = True
                    result["message"] = "Disk cache cleaned"
                else:
                    result["success"] = False
                    result["message"] = "RAM manager not available"
            else:
                result["error"] = "Unknown action"

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"RAM action failed: {e}")
            self.send_error(500)

    def _handle_skill(self, enable: bool):
        try:
            query = parse_qs(urlparse(self.path).query)
            skill_name = query.get("name", [None])[0]
            if enable: success = app.skill_manager.enable_skill(skill_name)
            else: success = app.skill_manager.disable_skill(skill_name)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}).encode())
        except Exception as e:
            logger.error(f"Skill toggle failed: {e}")
            self.send_error(500)

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    global app

    try:
        app = Application()
        app.start()

    except KeyboardInterrupt:
        logger.info("✋ Interrupted by user")
        if app:
            app.shutdown()
        sys.exit(0)

    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
