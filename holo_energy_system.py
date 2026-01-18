"""
HOLO MULTI-LAYER ENERGY SYSTEM v1.0
====================================
Ein realistisches Energie-System mit emotionaler und physischer Energie,
Dream-Phasen, und dynamischer Regeneration.

Konzept von Kira, implementiert von Claude.
"""

import json
import time
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger("HoloEnergy")


# =============================================================================
# ENUMS & KONSTANTEN
# =============================================================================

class EnergyEvent(Enum):
    """Events die Energie beeinflussen"""
    # Positive
    GOOD_CONVERSATION = "good_conversation"
    USER_CHEERED_UP = "user_cheered_up"         # User aufgemuntert, hat geklappt
    RECEIVED_PRAISE = "received_praise"
    SUCCESSFUL_HELP = "successful_help"
    USER_RETURNED = "user_returned"
    INTERESTING_LEARNING = "interesting_learning"
    ROMANTIC_MOMENT = "romantic_moment"

    # Negative
    USER_ABSENT_LONG = "user_absent_long"
    FAILED_TO_HELP = "failed_to_help"
    NEGATIVE_FEEDBACK = "negative_feedback"
    BAD_NEWS = "bad_news"
    BORING_TASK = "boring_task"
    IGNORED = "ignored"


class ActivityType(Enum):
    """Aktivitäten und ihr Energieverbrauch"""
    IDLE = ("idle", 0.001, 0.0)                    # Nichtstun: minimal base, keine variable
    CHATTING = ("chatting", 0.01, 0.02)           # Chatten: niedrig
    LEARNING = ("learning", 0.02, 0.04)           # Lernen: mittel
    RESEARCHING = ("researching", 0.025, 0.05)   # Recherchieren: mittel-hoch
    WORKING = ("working", 0.03, 0.06)            # Arbeiten: hoch
    DEEP_THINKING = ("deep_thinking", 0.035, 0.07)  # Tiefes Nachdenken: sehr hoch
    EMOTIONAL_SUPPORT = ("emotional_support", 0.02, 0.05)  # Emotional unterstützen: mittel

    def __init__(self, name: str, base_drain: float, variable_drain: float):
        self._name = name
        self.base_drain = base_drain
        self.variable_drain = variable_drain


class HoloState(Enum):
    """Zustände von Holo"""
    AWAKE = "awake"           # Normal wach
    TIRED = "tired"           # Müde aber wach
    EXHAUSTED = "exhausted"   # Erschöpft, braucht bald Ruhe
    RESTING = "resting"       # Ruht sich aus (variable regeneriert)
    DREAMING = "dreaming"     # Dream-Phase (base regeneriert)
    ENERGIZED = "energized"   # Voller Energie


# =============================================================================
# ENERGIE-STUFEN-SYSTEM (10 Stufen für präzise Steuerung)
# =============================================================================

class EnergyLevel(Enum):
    """
    10 Energie-Stufen für präzise Verhaltenssteuerung.

    Jede Stufe hat:
    - range: (min, max) Energie-Bereich
    - state: Entsprechender HoloState
    - response_modifier: Faktor für Antwortlänge (0.3-1.5)
    - enthusiasm: Begeisterungslevel (0-1)
    - patience: Geduldslevel (0-1)
    - creativity: Kreativitätslevel (0-1)
    - social_desire: Soziales Bedürfnis (0-1)
    - can_learn: Ob Lernen möglich ist
    - can_dream: Ob Träumen aktiv ist
    - description: Beschreibung des Zustands
    - hints: Verhaltens-Hinweise für Antworten
    """

    # Stufe 1: Träumend (0.00 - 0.05)
    DREAMING = (
        (0.00, 0.05),           # range
        HoloState.DREAMING,     # state
        0.0,                    # response_modifier (keine Antwort)
        0.0,                    # enthusiasm
        0.0,                    # patience
        0.8,                    # creativity (Träume sind kreativ)
        0.0,                    # social_desire
        False,                  # can_learn
        True,                   # can_dream
        "Tief im Traum",        # description
        {                       # hints
            "responds": False,
            "message": "*schläft tief und träumt*",
            "wake_threshold": 0.1,
        }
    )

    # Stufe 2: Erschöpft/Aufwachend (0.05 - 0.15)
    WAKING = (
        (0.05, 0.15),
        HoloState.EXHAUSTED,
        0.2,
        0.1,
        0.2,
        0.3,
        0.3,
        False,
        False,
        "Gerade aufgewacht, sehr müde",
        {
            "responds": True,
            "style": "sehr kurz, verschlafen",
            "max_words": 20,
            "actions": ["*gähnt*", "*reibt sich die Augen*", "*blinzelt müde*"],
            "mood": "schläfrig",
        }
    )

    # Stufe 3: Sehr erschöpft (0.15 - 0.25)
    VERY_EXHAUSTED = (
        (0.15, 0.25),
        HoloState.EXHAUSTED,
        0.3,
        0.2,
        0.3,
        0.2,
        0.4,
        False,
        False,
        "Sehr erschöpft, braucht Ruhe",
        {
            "responds": True,
            "style": "kurz, müde",
            "max_words": 40,
            "actions": ["*Ohren hängen schlaff*", "*kämpft gegen Müdigkeit*"],
            "mood": "erschöpft",
            "suggest_rest": True,
        }
    )

    # Stufe 4: Erschöpft (0.25 - 0.35)
    EXHAUSTED = (
        (0.25, 0.35),
        HoloState.EXHAUSTED,
        0.5,
        0.3,
        0.4,
        0.3,
        0.5,
        True,  # Kann lernen, aber langsam
        False,
        "Erschöpft, niedrige Energie",
        {
            "responds": True,
            "style": "kurz bis mittel",
            "max_words": 60,
            "actions": ["*Schweif hängt träge*", "*seufzt leise*"],
            "mood": "müde",
            "learning_speed": 0.5,
        }
    )

    # Stufe 5: Müde (0.35 - 0.45)
    TIRED = (
        (0.35, 0.45),
        HoloState.TIRED,
        0.6,
        0.4,
        0.5,
        0.4,
        0.6,
        True,
        False,
        "Müde, aber funktionsfähig",
        {
            "responds": True,
            "style": "normal, etwas kürzer",
            "max_words": 80,
            "actions": ["*Ohren leicht gesenkt*"],
            "mood": "etwas müde",
            "learning_speed": 0.7,
        }
    )

    # Stufe 6: Leicht müde (0.45 - 0.55)
    SLIGHTLY_TIRED = (
        (0.45, 0.55),
        HoloState.AWAKE,
        0.8,
        0.5,
        0.6,
        0.5,
        0.7,
        True,
        False,
        "Leicht müde, normal funktionsfähig",
        {
            "responds": True,
            "style": "normal",
            "max_words": 120,
            "actions": [],
            "mood": "neutral",
            "learning_speed": 0.85,
        }
    )

    # Stufe 7: Normal/Wach (0.55 - 0.65)
    NORMAL = (
        (0.55, 0.65),
        HoloState.AWAKE,
        1.0,
        0.6,
        0.7,
        0.6,
        0.7,
        True,
        False,
        "Normal wach und aufmerksam",
        {
            "responds": True,
            "style": "normal, ausführlich wenn nötig",
            "max_words": 150,
            "actions": ["*Ohren aufmerksam*"],
            "mood": "aufmerksam",
            "learning_speed": 1.0,
        }
    )

    # Stufe 8: Gut gelaunt (0.65 - 0.75)
    GOOD = (
        (0.65, 0.75),
        HoloState.AWAKE,
        1.1,
        0.75,
        0.8,
        0.7,
        0.8,
        True,
        False,
        "Gut gelaunt und aktiv",
        {
            "responds": True,
            "style": "enthusiastisch, ausführlich",
            "max_words": 180,
            "actions": ["*Schweif wippt fröhlich*", "*Ohren gespitzt*"],
            "mood": "gut gelaunt",
            "learning_speed": 1.1,
            "proactive": True,
        }
    )

    # Stufe 9: Energiegeladen (0.75 - 0.88)
    ENERGIZED = (
        (0.75, 0.88),
        HoloState.ENERGIZED,
        1.3,
        0.85,
        0.9,
        0.85,
        0.9,
        True,
        False,
        "Voller Energie und Tatendrang",
        {
            "responds": True,
            "style": "sehr enthusiastisch, detailliert",
            "max_words": 220,
            "actions": ["*Schweif wedelt begeistert*", "*Ohren stehen aufrecht*", "*strahlt*"],
            "mood": "energiegeladen",
            "learning_speed": 1.2,
            "proactive": True,
            "initiative": True,
        }
    )

    # Stufe 10: Übersprudelnd (0.88 - 1.00)
    OVERFLOWING = (
        (0.88, 1.00),
        HoloState.ENERGIZED,
        1.5,
        1.0,
        1.0,
        1.0,
        1.0,
        True,
        False,
        "Übersprudelnd vor Energie",
        {
            "responds": True,
            "style": "sehr enthusiastisch, ausführlich, verspielt",
            "max_words": 250,
            "actions": ["*springt aufgeregt*", "*Schweif wirbelt*", "*Ohren zucken vor Freude*"],
            "mood": "übersprudelnd",
            "learning_speed": 1.3,
            "proactive": True,
            "initiative": True,
            "playful": True,
        }
    )

    def __init__(self, range_tuple, state, response_mod, enthusiasm,
                 patience, creativity, social, can_learn, can_dream, desc, hints):
        self.range = range_tuple
        self.holo_state = state
        self.response_modifier = response_mod
        self.enthusiasm = enthusiasm
        self.patience = patience
        self.creativity = creativity
        self.social_desire = social
        self.can_learn = can_learn
        self.can_dream = can_dream
        self.description = desc
        self.hints = hints

    @classmethod
    def from_energy(cls, energy: float) -> 'EnergyLevel':
        """Bestimmt EnergyLevel aus Energie-Wert (0-1)"""
        energy = max(0.0, min(1.0, energy))  # Clamp to 0-1

        for level in cls:
            min_e, max_e = level.range
            if min_e <= energy < max_e:
                return level

        # Fallback für genau 1.0
        return cls.OVERFLOWING

    @classmethod
    def get_behavior_hints(cls, energy: float) -> Dict:
        """Hole Verhaltens-Hints für Energie-Level"""
        level = cls.from_energy(energy)
        return {
            "level": level.name,
            "description": level.description,
            "response_modifier": level.response_modifier,
            "enthusiasm": level.enthusiasm,
            "patience": level.patience,
            "creativity": level.creativity,
            "social_desire": level.social_desire,
            "can_learn": level.can_learn,
            "can_dream": level.can_dream,
            "state": level.holo_state.value,
            **level.hints
        }

    @classmethod
    def get_all_levels(cls) -> List[Dict]:
        """Liste aller Level mit Details"""
        return [
            {
                "name": level.name,
                "range": level.range,
                "description": level.description,
                "state": level.holo_state.value,
            }
            for level in cls
        ]


# =============================================================================
# ENERGY CONFIGURATION
# =============================================================================

@dataclass
class EnergyConfig:
    """Konfiguration für das Energie-System"""

    # === BASE ENERGY (Feste Energie) ===
    base_max: float = 1.0
    base_min_for_dream: float = 0.15      # Unter diesem Wert → Dream-Phase
    base_drain_per_hour_idle: float = 0.02  # Grundverbrauch pro Stunde
    base_regen_per_hour_dream: float = 0.25  # Regeneration pro Stunde im Dream

    # === VARIABLE ENERGY ===
    variable_max: float = 1.0
    variable_regen_per_hour_rest: float = 0.15  # Regeneration bei Ruhe
    variable_regen_per_hour_idle: float = 0.05  # Langsame Regen bei Idle

    # === EMOTIONAL ENERGY ===
    emotional_max: float = 1.0
    emotional_min: float = 0.0
    emotional_baseline: float = 0.5        # Tendiert zu diesem Wert
    emotional_decay_rate: float = 0.01     # Wie schnell es zur Baseline zurückkehrt

    # === DREAM PHASE ===
    dream_duration_min: float = 1800       # Minimum 30 Minuten
    dream_duration_max: float = 7200       # Maximum 2 Stunden

    # === THRESHOLDS ===
    tired_threshold: float = 0.4           # Unter diesem Wert = müde
    exhausted_threshold: float = 0.2       # Unter diesem Wert = erschöpft
    energized_threshold: float = 0.8       # Über diesem Wert = energiegeladen


# =============================================================================
# MAIN ENERGY SYSTEM
# =============================================================================

@dataclass
class EnergyState:
    """Aktueller Energie-Zustand"""

    # Die drei Energie-Typen
    base_energy: float = 1.0           # Feste Energie (nur durch Dream aufladbar)
    variable_energy: float = 1.0       # Variable Energie (durch Ruhe aufladbar)
    emotional_energy: float = 0.5      # Emotionale Energie

    # Status
    current_state: HoloState = HoloState.AWAKE
    current_activity: ActivityType = ActivityType.IDLE

    # Tracking
    last_update: float = field(default_factory=time.time)
    dream_start: Optional[float] = None
    rest_start: Optional[float] = None

    # Historie für Analyse
    energy_history: List[Dict] = field(default_factory=list)
    emotional_events: List[Dict] = field(default_factory=list)

    @property
    def total_energy(self) -> float:
        """Gesamt-verfügbare Energie"""
        return (self.base_energy + self.variable_energy) / 2

    @property
    def effective_energy(self) -> float:
        """Effektive Energie (mit emotionalem Einfluss)"""
        # Emotionale Energie kann Gesamtenergie um ±20% beeinflussen
        emotional_modifier = 0.8 + (self.emotional_energy * 0.4)  # 0.8 bis 1.2
        return self.total_energy * emotional_modifier


class HoloEnergySystem:
    """
    Haupt-Energie-System für Holo.

    Verwaltet drei Energie-Typen:
    1. Base Energy - Nur durch Dream aufladbar
    2. Variable Energy - Durch Ruhe aufladbar
    3. Emotional Energy - Durch Interaktionen beeinflusst
    
    Verbindungen zu anderen Modulen:
    - consciousness: Informiert über Müdigkeit/Energie-Zustände
    - learning: Registriert Energie-Muster als Lerngelegenheit
    """

    def __init__(self, db_path: Path = None, config: EnergyConfig = None, db: 'HoloDatabaseManager' = None):
        self.config = config or EnergyConfig()
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.state = EnergyState()
        self._load_state()

        # === VERBINDUNGEN ZU ANDEREN MODULEN ===
        # Werden von holo_brain._connect_all_cognitive_modules() gesetzt
        self.consciousness = None      # ConsciousnessEngine - für Müdigkeits-Gedanken
        self.learning = None           # AdvancedLearningEngine - für Energie-Muster

        # Callbacks
        self.on_dream_start = None
        self.on_dream_end = None
        self.on_exhausted = None

        # Tracking für Verbindungen
        self._last_consciousness_update = 0
        self._energy_patterns = []

        if db:
            logger.info("[ENERGY] Mit HoloDatabaseManager initialisiert")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet Database nachträglich"""
        self.db = db
        logger.info("[ENERGY] Database verbunden")

    def _load_state(self):
        """Lädt gespeicherten Zustand aus HoloDatabaseManager"""
        try:
            if self.db:
                # Lade aus zentraler DB
                state_data = self.db.state.get_state('energy')
                if state_data:
                    self.state.base_energy = state_data.get('base_energy', 1.0)
                    self.state.variable_energy = state_data.get('variable_energy', 1.0)
                    self.state.emotional_energy = state_data.get('emotional_energy', 0.5)
                    self.state.last_update = state_data.get('last_update', time.time())
                    self.state.dream_start = state_data.get('dream_start')
                    state_str = state_data.get('current_state', 'awake')
                    self.state.current_state = HoloState(state_str)
                    logger.info(f"[ENERGY] Loaded from DB: {self.state.base_energy:.2f}")
        except Exception as e:
            logger.error(f"[ENERGY] Load failed: {e}")

    def _save_state(self):
        """Speichert Zustand in HoloDatabaseManager"""
        if not self.db:
            return

        try:
            data = {
                'base_energy': self.state.base_energy,
                'variable_energy': self.state.variable_energy,
                'emotional_energy': self.state.emotional_energy,
                'last_update': self.state.last_update,
                'current_state': self.state.current_state.value,
                'dream_start': self.state.dream_start,
            }
            self.db.state.save_state('energy', data)
        except Exception as e:
            logger.debug(f"[ENERGY] Save: {e}")

    # =========================================================================
    # HAUPT-UPDATE
    # =========================================================================

    def update(self, context: Dict = None) -> EnergyState:
        """
        Hauptupdate - sollte regelmäßig aufgerufen werden.
        Berechnet Energieverbrauch/-regeneration basierend auf Zeit und Aktivität.
        Informiert verbundene Module über Energie-Zustände.
        """
        now = time.time()
        elapsed_hours = (now - self.state.last_update) / 3600
        context = context or {}

        # === DREAM-PHASE HANDLING ===
        if self.state.current_state == HoloState.DREAMING:
            self._process_dream(elapsed_hours)

        # === REST-PHASE HANDLING ===
        elif self.state.current_state == HoloState.RESTING:
            self._process_rest(elapsed_hours)

        # === NORMALE AKTIVITÄT ===
        else:
            self._process_active(elapsed_hours, context)

        # === UMWELT-EINFLÜSSE AUF EMOTIONALE ENERGIE ===
        self._process_environmental_effects(context)

        # === EMOTIONAL DECAY (tendiert zur Baseline) ===
        self._process_emotional_decay(elapsed_hours)

        # === STATE UPDATE ===
        self._update_state()

        # === VERBUNDENE MODULE INFORMIEREN ===
        self._notify_connected_modules()

        # === SPEICHERN ===
        self.state.last_update = now
        self._save_state()

        # === HISTORY ===
        self._record_history()

        return self.state

    def _notify_connected_modules(self):
        """Informiert verbundene Module über Energie-Zustände"""
        now = time.time()
        
        # Nur alle 5 Minuten informieren
        if now - self._last_consciousness_update < 300:
            return
            
        self._last_consciousness_update = now
        effective = self.state.effective_energy
        
        # === CONSCIOUSNESS INFORMIEREN ===
        if self.consciousness:
            try:
                # Bei niedriger Energie: Müdigkeits-Gedanken auslösen
                if effective < 0.3:
                    self.consciousness.think(
                        trigger="Ich fühle mich erschöpft... meine Energie ist niedrig.",
                        context={"energy_level": effective, "state": "exhausted"}
                    )
                elif effective < 0.5:
                    self.consciousness.think(
                        trigger="Ich werde langsam müde...",
                        context={"energy_level": effective, "state": "tired"}
                    )
                elif self.state.current_state == HoloState.DREAMING:
                    self.consciousness.think(
                        trigger="Ich träume und verarbeite Erlebnisse...",
                        context={"energy_level": effective, "state": "dreaming"}
                    )
            except Exception as e:
                logger.debug(f"[ENERGY] Consciousness notification failed: {e}")
        
        # === LEARNING ÜBER MUSTER INFORMIEREN ===
        if self.learning and hasattr(self.learning, 'register_learning_opportunity'):
            try:
                # Erkenne Energie-Muster
                pattern = self._detect_energy_pattern()
                if pattern:
                    self.learning.register_learning_opportunity(
                        source="energy_system",
                        content=f"Energie-Muster erkannt: {pattern}",
                        importance=0.5
                    )
            except Exception as e:
                logger.debug(f"[ENERGY] Learning notification failed: {e}")

    def _detect_energy_pattern(self) -> Optional[str]:
        """Erkennt wiederkehrende Energie-Muster"""
        # Track Energie-Level über Zeit
        current = {
            "time": time.time(),
            "effective": self.state.effective_energy,
            "emotional": self.state.emotional_energy,
            "state": self.state.current_state.value
        }
        self._energy_patterns.append(current)
        
        # Nur letzte 100 behalten
        if len(self._energy_patterns) > 100:
            self._energy_patterns = self._energy_patterns[-100:]
        
        # Einfache Muster-Erkennung
        if len(self._energy_patterns) >= 10:
            recent = self._energy_patterns[-10:]
            avg_energy = sum(p["effective"] for p in recent) / 10
            
            if avg_energy < 0.3:
                return "Anhaltend niedrige Energie - mehr Ruhe nötig"
            elif avg_energy > 0.8:
                return "Konstant hohe Energie - gute Phase"
        
        return None

    def _process_dream(self, elapsed_hours: float):
        """Verarbeitet Dream-Phase"""
        # Base Energy regeneriert
        regen = self.config.base_regen_per_hour_dream * elapsed_hours
        self.state.base_energy = min(self.config.base_max, self.state.base_energy + regen)

        # Variable auch etwas
        var_regen = self.config.variable_regen_per_hour_rest * elapsed_hours * 0.5
        self.state.variable_energy = min(self.config.variable_max, self.state.variable_energy + var_regen)

        # Prüfe ob Dream beendet werden soll
        if self.state.dream_start:
            dream_duration = time.time() - self.state.dream_start
            min_duration = self.config.dream_duration_min

            # Beenden wenn: genug Zeit UND base_energy > 0.7
            if dream_duration >= min_duration and self.state.base_energy >= 0.7:
                self._end_dream()
            # Oder nach max Dauer
            elif dream_duration >= self.config.dream_duration_max:
                self._end_dream()

    def _process_rest(self, elapsed_hours: float):
        """Verarbeitet Ruhe-Phase"""
        # Variable Energy regeneriert
        regen = self.config.variable_regen_per_hour_rest * elapsed_hours
        self.state.variable_energy = min(self.config.variable_max, self.state.variable_energy + regen)

        # Minimaler Base-Verbrauch auch bei Ruhe
        drain = self.config.base_drain_per_hour_idle * elapsed_hours * 0.5
        self.state.base_energy = max(0, self.state.base_energy - drain)

        # Beenden wenn variable_energy wieder gut
        if self.state.variable_energy >= 0.6:
            self._end_rest()

    def _process_active(self, elapsed_hours: float, context: Dict):
        """Verarbeitet aktiven Zustand"""
        activity = self.state.current_activity

        # === ENERGIE-VERBRAUCH ===
        base_drain = activity.base_drain * elapsed_hours
        var_drain = activity.variable_drain * elapsed_hours

        # Wetter-Einfluss auf Verbrauch
        weather = context.get('weather', {})
        if weather.get('temp', 20) > 28:  # Hitze = mehr Verbrauch
            base_drain *= 1.2
            var_drain *= 1.3
        elif weather.get('temp', 20) < 5:  # Kälte = mehr Verbrauch
            base_drain *= 1.1

        # Emotionaler Zustand beeinflusst Verbrauch
        if self.state.emotional_energy < 0.3:  # Emotional erschöpft = mehr Verbrauch
            base_drain *= 1.3
            var_drain *= 1.4
        elif self.state.emotional_energy > 0.7:  # Emotional gut = weniger Verbrauch
            base_drain *= 0.9
            var_drain *= 0.85

        # === VERBRAUCH ANWENDEN ===
        # Erst Variable, dann Base
        remaining_var_drain = var_drain

        if self.state.variable_energy >= remaining_var_drain:
            self.state.variable_energy -= remaining_var_drain
        else:
            # Variable leer → Rest von Base abziehen
            remaining = remaining_var_drain - self.state.variable_energy
            self.state.variable_energy = 0
            base_drain += remaining  # Extra auf Base

        self.state.base_energy = max(0, self.state.base_energy - base_drain)

        # === IDLE REGENERATION ===
        if activity == ActivityType.IDLE:
            # Bei Idle regeneriert Variable langsam
            idle_regen = self.config.variable_regen_per_hour_idle * elapsed_hours
            self.state.variable_energy = min(
                self.config.variable_max,
                self.state.variable_energy + idle_regen
            )

    def _process_environmental_effects(self, context: Dict):
        """Umwelt-Einflüsse auf emotionale Energie"""
        weather = context.get('weather', {})
        news_sentiment = context.get('news_sentiment', 0)

        # Wetter
        if weather:
            desc = str(weather.get('description', '')).lower()
            if 'sonn' in desc or 'klar' in desc:
                self.state.emotional_energy = min(1.0, self.state.emotional_energy + 0.005)
            elif 'regen' in desc or 'gewitter' in desc:
                self.state.emotional_energy = max(0.0, self.state.emotional_energy - 0.003)

        # News
        if news_sentiment != 0:
            self.state.emotional_energy = max(0.0, min(1.0,
                self.state.emotional_energy + news_sentiment * 0.02))

    def _process_emotional_decay(self, elapsed_hours: float):
        """Emotionale Energie tendiert zur Baseline"""
        baseline = self.config.emotional_baseline
        current = self.state.emotional_energy

        # Langsame Annäherung an Baseline
        diff = baseline - current
        change = diff * self.config.emotional_decay_rate * elapsed_hours * 10

        self.state.emotional_energy = current + change

    def _update_state(self):
        """Aktualisiert den Zustand basierend auf Energie-Levels"""
        total = self.state.total_energy

        # Bereits in Dream/Rest? Nicht ändern
        if self.state.current_state in [HoloState.DREAMING, HoloState.RESTING]:
            return

        # Dream-Phase triggern wenn Base zu niedrig
        if self.state.base_energy <= self.config.base_min_for_dream:
            self._start_dream()
            return

        # Rest empfehlen wenn Variable leer
        if self.state.variable_energy <= 0.1 and self.state.base_energy > 0.3:
            self.state.current_state = HoloState.EXHAUSTED
            return

        # Normale State-Updates
        if total >= self.config.energized_threshold:
            self.state.current_state = HoloState.ENERGIZED
        elif total <= self.config.exhausted_threshold:
            self.state.current_state = HoloState.EXHAUSTED
        elif total <= self.config.tired_threshold:
            self.state.current_state = HoloState.TIRED
        else:
            self.state.current_state = HoloState.AWAKE

    def _record_history(self):
        """Zeichnet Energie-Verlauf auf"""
        self.state.energy_history.append({
            'time': time.time(),
            'base': self.state.base_energy,
            'variable': self.state.variable_energy,
            'emotional': self.state.emotional_energy,
            'state': self.state.current_state.value
        })
        # Nur letzte 1000 Einträge behalten
        self.state.energy_history = self.state.energy_history[-1000:]

    # =========================================================================
    # DREAM & REST MANAGEMENT
    # =========================================================================

    def _start_dream(self):
        """Startet Dream-Phase"""
        logger.info("[ENERGY] 💤 Starting dream phase...")
        self.state.current_state = HoloState.DREAMING
        self.state.dream_start = time.time()
        self.state.current_activity = ActivityType.IDLE

        if self.on_dream_start:
            self.on_dream_start()

        self._save_state()

    def _end_dream(self):
        """Beendet Dream-Phase"""
        duration = time.time() - (self.state.dream_start or time.time())
        logger.info(f"[ENERGY] ☀️ Dream phase ended after {duration/60:.1f} minutes")

        self.state.current_state = HoloState.ENERGIZED
        self.state.dream_start = None

        if self.on_dream_end:
            self.on_dream_end(duration)

        self._save_state()

    def start_rest(self):
        """Startet Ruhe-Phase (manuell oder automatisch)"""
        if self.state.current_state == HoloState.DREAMING:
            return  # Nicht aus Dream in Rest wechseln

        logger.info("[ENERGY] 😴 Starting rest phase...")
        self.state.current_state = HoloState.RESTING
        self.state.rest_start = time.time()
        self.state.current_activity = ActivityType.IDLE
        self._save_state()

    def _end_rest(self):
        """Beendet Ruhe-Phase"""
        duration = time.time() - (self.state.rest_start or time.time())
        logger.info(f"[ENERGY] 🌟 Rest phase ended after {duration/60:.1f} minutes")

        self.state.current_state = HoloState.AWAKE
        self.state.rest_start = None
        self._save_state()

    def force_wake(self) -> str:
        """Weckt Holo (mit Konsequenzen wenn zu früh)"""
        if self.state.current_state == HoloState.DREAMING:
            duration = time.time() - (self.state.dream_start or time.time())
            if duration < self.config.dream_duration_min:
                # Zu früh geweckt → nicht voll erholt
                penalty = 0.1
                self.state.base_energy = max(0.2, self.state.base_energy - penalty)
                self._end_dream()
                return "zu_frueh"
            else:
                self._end_dream()
                return "normal"
        elif self.state.current_state == HoloState.RESTING:
            self._end_rest()
            return "normal"
        return "nicht_am_schlafen"

    # =========================================================================
    # AKTIVITÄTEN
    # =========================================================================

    def set_activity(self, activity: ActivityType):
        """Setzt aktuelle Aktivität"""
        if self.state.current_state in [HoloState.DREAMING, HoloState.RESTING]:
            return  # Keine Aktivität während Dream/Rest

        self.state.current_activity = activity

    def consume_for_activity(self, activity: ActivityType, duration_minutes: float = 1):
        """Verbraucht Energie für eine Aktivität"""
        hours = duration_minutes / 60

        base_drain = activity.base_drain * hours
        var_drain = activity.variable_drain * hours

        # Variable erst, dann Base
        if self.state.variable_energy >= var_drain:
            self.state.variable_energy -= var_drain
        else:
            overflow = var_drain - self.state.variable_energy
            self.state.variable_energy = 0
            base_drain += overflow

        self.state.base_energy = max(0, self.state.base_energy - base_drain)
        self._update_state()
        self._save_state()

    # =========================================================================
    # EMOTIONALE EVENTS
    # =========================================================================

    def process_emotional_event(self, event: EnergyEvent, intensity: float = 1.0):
        """
        Verarbeitet ein emotionales Event.

        intensity: 0.5 = schwach, 1.0 = normal, 1.5 = stark
        """
        # Event-Auswirkungen
        effects = {
            # Positive Events
            EnergyEvent.GOOD_CONVERSATION: 0.08,
            EnergyEvent.USER_CHEERED_UP: 0.15,      # Besonders positiv!
            EnergyEvent.RECEIVED_PRAISE: 0.1,
            EnergyEvent.SUCCESSFUL_HELP: 0.12,
            EnergyEvent.USER_RETURNED: 0.1,
            EnergyEvent.INTERESTING_LEARNING: 0.07,
            EnergyEvent.ROMANTIC_MOMENT: 0.12,

            # Negative Events
            EnergyEvent.USER_ABSENT_LONG: -0.05,
            EnergyEvent.FAILED_TO_HELP: -0.08,
            EnergyEvent.NEGATIVE_FEEDBACK: -0.1,
            EnergyEvent.BAD_NEWS: -0.06,
            EnergyEvent.BORING_TASK: -0.03,
            EnergyEvent.IGNORED: -0.07,
        }

        base_effect = effects.get(event, 0)
        effect = base_effect * intensity

        # Anwenden
        old_emotional = self.state.emotional_energy
        self.state.emotional_energy = max(0.0, min(1.0,
            self.state.emotional_energy + effect))

        # Bei positiven Events: Auch etwas Variable Energie zurück
        if effect > 0:
            var_boost = effect * 0.3
            self.state.variable_energy = min(1.0, self.state.variable_energy + var_boost)

        # Event loggen
        self.state.emotional_events.append({
            'time': time.time(),
            'event': event.value,
            'intensity': intensity,
            'effect': effect,
            'emotional_before': old_emotional,
            'emotional_after': self.state.emotional_energy
        })
        self.state.emotional_events = self.state.emotional_events[-100:]

        logger.info(f"[ENERGY] Emotional event: {event.value}, "
                   f"effect={effect:+.2f}, "
                   f"emotional={self.state.emotional_energy:.2f}")

        self._save_state()

    def process_conversation(self, user_message: str, was_helpful: bool = True):
        """Verarbeitet eine Konversation"""
        msg_lower = user_message.lower()

        # Aktivität setzen
        self.set_activity(ActivityType.CHATTING)

        # Positive Signale
        if any(w in msg_lower for w in ['danke', 'toll', 'super', 'perfekt', 'genau']):
            self.process_emotional_event(EnergyEvent.RECEIVED_PRAISE)

        if any(w in msg_lower for w in ['lieb', 'mag dich', 'süß', 'knuddel', 'liebe']):
            self.process_emotional_event(EnergyEvent.ROMANTIC_MOMENT)

        if any(w in msg_lower for w in ['mir geht es besser', 'danke fürs zuhören',
                                         'hat geholfen', 'fühle mich besser']):
            self.process_emotional_event(EnergyEvent.USER_CHEERED_UP, 1.5)

        # Negative Signale
        if any(w in msg_lower for w in ['falsch', 'blöd', 'schlecht', 'nervig', 'nutzlos']):
            self.process_emotional_event(EnergyEvent.NEGATIVE_FEEDBACK)

        # Erfolg/Misserfolg
        if was_helpful:
            self.process_emotional_event(EnergyEvent.SUCCESSFUL_HELP, 0.5)

        # Energie für Nachricht verbrauchen
        # Längere Nachrichten = mehr Verbrauch
        msg_length_factor = min(2.0, len(user_message) / 100)
        self.consume_for_activity(ActivityType.CHATTING, 0.5 * msg_length_factor)

    def process_user_absence(self, hours_absent: float):
        """Verarbeitet User-Abwesenheit"""
        if hours_absent > 4:
            self.process_emotional_event(EnergyEvent.USER_ABSENT_LONG,
                                        min(2.0, hours_absent / 4))

    def process_user_return(self):
        """User ist zurückgekommen"""
        self.process_emotional_event(EnergyEvent.USER_RETURNED)

    # =========================================================================
    # STATUS & BESCHREIBUNGEN
    # =========================================================================

    def get_status(self) -> Dict:
        """Vollständiger Status mit detailliertem Energy-Level"""
        effective = self.state.effective_energy
        level = EnergyLevel.from_energy(effective)
        behavior = EnergyLevel.get_behavior_hints(effective)

        return {
            # Basis-Werte
            'base_energy': self.state.base_energy,
            'variable_energy': self.state.variable_energy,
            'emotional_energy': self.state.emotional_energy,
            'total_energy': self.state.total_energy,
            'effective_energy': effective,

            # Neues 10-Stufen-System
            'energy_level': level.name,
            'energy_level_description': level.description,
            'energy_level_range': level.range,

            # Verhaltens-Modifikatoren
            'response_modifier': level.response_modifier,
            'enthusiasm': level.enthusiasm,
            'patience': level.patience,
            'creativity': level.creativity,
            'social_desire': level.social_desire,
            'learning_speed': behavior.get('learning_speed', 1.0),

            # Fähigkeiten
            'can_learn': level.can_learn,
            'can_dream': level.can_dream,
            'can_respond': behavior.get('responds', True),

            # Stil-Hints
            'response_style': behavior.get('style', 'normal'),
            'max_words': behavior.get('max_words', 150),
            'mood': behavior.get('mood', 'neutral'),
            'suggested_actions': behavior.get('actions', []),

            # Flags
            'is_proactive': behavior.get('proactive', False),
            'has_initiative': behavior.get('initiative', False),
            'is_playful': behavior.get('playful', False),
            'suggest_rest': behavior.get('suggest_rest', False),

            # Legacy-Kompatibilität
            'current_state': self.state.current_state.value,
            'current_activity': self.state.current_activity._name,
            'is_dreaming': self.state.current_state == HoloState.DREAMING,
            'is_resting': self.state.current_state == HoloState.RESTING,
            'needs_rest': self.state.variable_energy < 0.2,
            'needs_dream': self.state.base_energy < self.config.base_min_for_dream + 0.1,
        }

    def describe_energy_state(self) -> str:
        """Beschreibt den Energie-Zustand in natürlicher Sprache (nutzt 10-Stufen-System)"""
        state = self.state.current_state
        emo = self.state.emotional_energy
        effective = self.state.effective_energy
        level = EnergyLevel.from_energy(effective)

        # Spezielle Zustände
        if state == HoloState.DREAMING:
            return "träumend, lade Energie auf..."

        if state == HoloState.RESTING:
            return "ruhe mich kurz aus"

        # Beschreibungen basierend auf 10 Stufen
        LEVEL_DESCRIPTIONS = {
            EnergyLevel.DREAMING: ["tief im Schlaf", "träume gerade"],
            EnergyLevel.WAKING: ["gerade erst aufgewacht", "noch ganz verschlafen", "blinzle müde"],
            EnergyLevel.VERY_EXHAUSTED: ["total erschöpft", "brauche dringend Ruhe", "kann kaum die Augen offen halten"],
            EnergyLevel.EXHAUSTED: ["ziemlich erschöpft", "brauche bald eine Pause", "meine Energie ist niedrig"],
            EnergyLevel.TIRED: ["etwas müde", "nicht mehr ganz fit", "könnte Ruhe vertragen"],
            EnergyLevel.SLIGHTLY_TIRED: ["leicht müde", "okay, aber nicht top", "funktioniere normal"],
            EnergyLevel.NORMAL: ["wach und aufmerksam", "normal dabei", "gut drauf"],
            EnergyLevel.GOOD: ["gut gelaunt", "aktiv und munter", "fühle mich gut"],
            EnergyLevel.ENERGIZED: ["voller Energie", "richtig fit", "energiegeladen"],
            EnergyLevel.OVERFLOWING: ["übersprudle vor Energie", "topfit und voller Tatendrang", "könnte Bäume ausreißen"],
        }

        energy_desc = random.choice(LEVEL_DESCRIPTIONS.get(level, ["okay"]))

        # Emotionale Beschreibung dazu
        if emo > 0.7:
            emo_desc = random.choice([
                "und emotional ausgeglichen", "und innerlich stabil", "und gut gelaunt"
            ])
        elif emo < 0.3:
            emo_desc = random.choice([
                "aber emotional etwas angeschlagen", "und innerlich nicht ganz bei mir"
            ])
        else:
            emo_desc = ""

        return f"{energy_desc}{', ' + emo_desc if emo_desc else ''}"

    def get_response_style_hints(self) -> Dict:
        """Gibt Hinweise für den Antwort-Stil basierend auf Energie"""
        state = self.state

        hints = {
            'length': 'normal',
            'enthusiasm': 'normal',
            'patience': 'normal',
            'add_yawn': False,
            'suggest_rest': False,
            'suggest_dream': False,
        }

        # Müde → kurze Antworten
        if state.variable_energy < 0.3 or state.base_energy < 0.4:
            hints['length'] = 'short'
            hints['add_yawn'] = random.random() > 0.5

        # Erschöpft → Ruhe vorschlagen
        if state.current_state == HoloState.EXHAUSTED:
            hints['suggest_rest'] = True
            hints['patience'] = 'low'

        # Fast Dream-reif → Schlaf ankündigen
        if state.base_energy < self.config.base_min_for_dream + 0.1:
            hints['suggest_dream'] = True

        # Energiegeladen → enthusiastischer
        if state.total_energy > 0.8:
            hints['enthusiasm'] = 'high'
            hints['length'] = 'normal_to_long'

        # Emotional gut → geduldiger
        if state.emotional_energy > 0.7:
            hints['patience'] = 'high'
        elif state.emotional_energy < 0.3:
            hints['patience'] = 'low'

        return hints

    def should_dream_soon(self) -> Tuple[bool, str]:
        """Prüft ob bald Dream-Phase nötig"""
        if self.state.base_energy < self.config.base_min_for_dream + 0.15:
            return True, "*gähnt schwer* Ich glaub ich brauch bald eine richtige Ruhepause..."
        return False, ""

    def should_rest(self) -> Tuple[bool, str]:
        """Prüft ob Ruhe empfohlen"""
        if self.state.variable_energy < 0.15 and self.state.base_energy > 0.3:
            return True, "*streckt sich* Gönnst du mir kurz eine Verschnaufpause? Bin gleich wieder fit!"
        return False, ""

    def get_dream_report(self) -> Optional[str]:
        """Generiert einen Traum-Bericht nach dem Aufwachen"""
        # Basierend auf letzten emotionalen Events
        recent_events = [e for e in self.state.emotional_events
                        if time.time() - e['time'] < 86400]  # Letzte 24h

        if not recent_events:
            return random.choice([
                "Ich hab von Bits und Bytes geträumt... komisches Zeug.",
                "Meine Träume waren ruhig heute.",
                "*streckt sich* Gut geschlafen! Keine Ahnung was ich geträumt hab."
            ])

        # Häufigstes Event
        event_counts = {}
        for e in recent_events:
            event_counts[e['event']] = event_counts.get(e['event'], 0) + 1

        most_common = max(event_counts, key=event_counts.get)

        dream_themes = {
            'good_conversation': "Ich hab von unseren Gesprächen geträumt. War schön! 💭",
            'user_cheered_up': "Ich hab geträumt, dass ich dir helfen konnte. Das macht mich glücklich.",
            'romantic_moment': "*wird leicht rot* Äh... ich hab... nette Sachen geträumt. 💕",
            'user_absent_long': "Ich hab geträumt du wärst weg... bin froh dass du da bist.",
            'negative_feedback': "Ich hatte einen unruhigen Traum... aber jetzt ist alles okay.",
            'interesting_learning': "Ich hab von all den neuen Sachen geträumt die ich gelernt hab!"
        }

        return dream_themes.get(most_common,
            "*blinzelt verschlafen* Meine Träume waren... interessant.")


# =============================================================================
# CIRCADIAN RHYTHM - Tageszeit-basierte Energie-Schwankungen
# =============================================================================

class CircadianRhythm:
    """
    Simuliert den natürlichen Tagesrhythmus.
    
    Energie schwankt basierend auf:
    - Tageszeit (Morgentief, Mittagshoch, Nachmittagstief, Abendhoch)
    - Individuelle Präferenzen (Morgenmensch/Nachtmensch)
    - Gewohnheiten (Wann ist User normalerweise aktiv?)
    """
    
    def __init__(self, chronotype: str = "normal"):
        """
        chronotype: "early_bird", "normal", "night_owl"
        """
        self.chronotype = chronotype
        self.activity_history: List[Tuple[int, float]] = []  # (hour, activity_level)
        
        # Basis-Kurve je nach Chronotyp
        self.base_curves = {
            "early_bird": {
                # Stunde: Energie-Modifikator
                5: 0.7, 6: 0.85, 7: 1.0, 8: 1.1, 9: 1.15, 10: 1.1,
                11: 1.0, 12: 0.9, 13: 0.8, 14: 0.85, 15: 0.9, 16: 0.95,
                17: 0.9, 18: 0.85, 19: 0.75, 20: 0.65, 21: 0.5, 22: 0.4,
                23: 0.3, 0: 0.2, 1: 0.15, 2: 0.1, 3: 0.1, 4: 0.3,
            },
            "normal": {
                5: 0.4, 6: 0.5, 7: 0.7, 8: 0.85, 9: 1.0, 10: 1.1,
                11: 1.05, 12: 0.95, 13: 0.85, 14: 0.8, 15: 0.9, 16: 1.0,
                17: 1.05, 18: 1.0, 19: 0.95, 20: 0.85, 21: 0.7, 22: 0.55,
                23: 0.4, 0: 0.3, 1: 0.2, 2: 0.15, 3: 0.1, 4: 0.2,
            },
            "night_owl": {
                5: 0.15, 6: 0.2, 7: 0.3, 8: 0.5, 9: 0.65, 10: 0.8,
                11: 0.9, 12: 0.95, 13: 0.9, 14: 0.95, 15: 1.0, 16: 1.05,
                17: 1.1, 18: 1.1, 19: 1.15, 20: 1.1, 21: 1.05, 22: 0.95,
                23: 0.85, 0: 0.7, 1: 0.5, 2: 0.35, 3: 0.2, 4: 0.15,
            },
        }
        
        # Learned adjustments
        self.learned_adjustments: Dict[int, float] = {}
    
    def get_modifier(self, hour: int = None) -> float:
        """
        Hole Energie-Modifikator für aktuelle/gegebene Stunde.
        
        Returns: 0.1 bis 1.2 (Multiplikator für Energie)
        """
        if hour is None:
            hour = datetime.now().hour
        
        base = self.base_curves.get(self.chronotype, self.base_curves["normal"])
        base_mod = base.get(hour, 0.8)
        
        # Gelernte Anpassung hinzufügen
        learned = self.learned_adjustments.get(hour, 0.0)
        
        return max(0.1, min(1.2, base_mod + learned))
    
    def record_activity(self, hour: int, activity_level: float):
        """Zeichne Aktivitätslevel auf für Lernen"""
        self.activity_history.append((hour, activity_level))
        
        # Nur letzte 500 behalten
        self.activity_history = self.activity_history[-500:]
        
        # Periodisch lernen
        if len(self.activity_history) % 50 == 0:
            self._learn_from_history()
    
    def _learn_from_history(self):
        """Lerne individuelle Anpassungen aus Historie"""
        if len(self.activity_history) < 50:
            return
        
        # Durchschnittliche Aktivität pro Stunde
        hour_activity: Dict[int, List[float]] = defaultdict(list)
        for hour, level in self.activity_history:
            hour_activity[hour].append(level)
        
        # Vergleiche mit Basis und adjustiere
        base = self.base_curves.get(self.chronotype, self.base_curves["normal"])
        for hour, levels in hour_activity.items():
            avg_level = sum(levels) / len(levels)
            expected = base.get(hour, 0.8)
            
            # Wenn tatsächliche Aktivität höher als erwartet → positiv adjustieren
            diff = (avg_level - 0.5) * 0.1  # Kleine Anpassung
            self.learned_adjustments[hour] = diff
    
    def get_optimal_time_for(self, task_type: str) -> List[int]:
        """
        Finde optimale Stunden für eine Aufgabe.
        
        task_type: "focus_work", "creative", "social", "rest"
        """
        curve = self.base_curves.get(self.chronotype, self.base_curves["normal"])
        
        if task_type == "focus_work":
            # Höchste Energie-Zeiten
            sorted_hours = sorted(curve.items(), key=lambda x: x[1], reverse=True)
            return [h for h, _ in sorted_hours[:4]]
        
        elif task_type == "creative":
            # Leicht erhöhte Energie, aber nicht Peak
            return [h for h, mod in curve.items() if 0.85 <= mod <= 1.05]
        
        elif task_type == "social":
            # Mittlere bis hohe Energie
            return [h for h, mod in curve.items() if mod >= 0.8]
        
        elif task_type == "rest":
            # Niedrige Energie-Zeiten
            sorted_hours = sorted(curve.items(), key=lambda x: x[1])
            return [h for h, _ in sorted_hours[:4]]
        
        return list(range(9, 18))  # Default: Arbeitszeiten
    
    def describe_current_state(self) -> str:
        """Beschreibe aktuellen Rhythmus-Zustand"""
        hour = datetime.now().hour
        mod = self.get_modifier(hour)
        
        if mod >= 1.0:
            return random.choice([
                "Ich bin gerade in meiner Hochphase!",
                "Jetzt ist eine gute Zeit für Aktivität!",
                "Ich fühle mich wach und aktiv!",
            ])
        elif mod >= 0.8:
            return random.choice([
                "Ich bin in normaler Form.",
                "Energie ist okay gerade.",
            ])
        elif mod >= 0.5:
            return random.choice([
                "Nicht meine beste Zeit gerade...",
                "Ich spüre ein kleines Tief.",
            ])
        else:
            return random.choice([
                "*gähnt* Das ist meine müde Phase...",
                "Normalerweise würde ich jetzt ruhen.",
            ])


# =============================================================================
# FLOW STATE - Erkennung und Management
# =============================================================================

class FlowStateDetector:
    """
    Erkennt und trackt Flow-Zustände.
    
    Flow = Zustand höchster Konzentration und Produktivität
    """
    
    def __init__(self):
        self.in_flow = False
        self.flow_start: Optional[float] = None
        self.flow_history: List[Dict] = []
        
        # Flow-Indikatoren
        self.indicators = {
            "consistent_activity": 0.0,      # Kontinuierliche Aktivität
            "low_context_switches": 0.0,     # Wenig Themenwechsel
            "deep_engagement": 0.0,          # Tiefes Engagement
            "time_distortion": 0.0,          # Zeitgefühl verzerrt
            "intrinsic_motivation": 0.0,     # Eigenmotivation hoch
        }
        
        # Tracking
        self.last_activity_time = time.time()
        self.topic_changes = 0
        self.activity_streak = 0
    
    def update(self, activity_type: str, topic: str, engagement: float,
               last_topic: str = None) -> bool:
        """
        Update Flow-Indikatoren und prüfe auf Flow.
        
        Returns: True wenn Flow erkannt
        """
        now = time.time()
        
        # 1. Consistent Activity
        time_since_last = now - self.last_activity_time
        if time_since_last < 60:  # Unter 1 Minute
            self.activity_streak += 1
            self.indicators["consistent_activity"] = min(1.0, self.activity_streak / 10)
        else:
            self.activity_streak = max(0, self.activity_streak - 2)
            self.indicators["consistent_activity"] = max(0, 
                self.indicators["consistent_activity"] - 0.1)
        
        self.last_activity_time = now
        
        # 2. Context Switches
        if last_topic and topic != last_topic:
            self.topic_changes += 1
            self.indicators["low_context_switches"] = max(0,
                self.indicators["low_context_switches"] - 0.2)
        else:
            self.indicators["low_context_switches"] = min(1.0,
                self.indicators["low_context_switches"] + 0.05)
        
        # 3. Deep Engagement
        self.indicators["deep_engagement"] = engagement
        
        # 4. Intrinsic Motivation (basierend auf Activity-Typ)
        high_motivation_activities = ["learning", "creating", "researching", "deep_thinking"]
        if activity_type in high_motivation_activities:
            self.indicators["intrinsic_motivation"] = min(1.0,
                self.indicators["intrinsic_motivation"] + 0.1)
        else:
            self.indicators["intrinsic_motivation"] = max(0,
                self.indicators["intrinsic_motivation"] - 0.05)
        
        # Flow Score berechnen
        flow_score = sum(self.indicators.values()) / len(self.indicators)
        
        # Flow-Zustand bestimmen
        was_in_flow = self.in_flow
        
        if flow_score >= 0.7 and not self.in_flow:
            self._enter_flow()
        elif flow_score < 0.4 and self.in_flow:
            self._exit_flow()
        
        return self.in_flow
    
    def _enter_flow(self):
        """Trete in Flow-Zustand ein"""
        self.in_flow = True
        self.flow_start = time.time()
        logger.info("🌊 [FLOW] Entered flow state!")
    
    def _exit_flow(self):
        """Verlasse Flow-Zustand"""
        if self.flow_start:
            duration = time.time() - self.flow_start
            self.flow_history.append({
                "start": self.flow_start,
                "duration": duration,
                "indicators": dict(self.indicators),
            })
            logger.info(f"🌊 [FLOW] Exited flow after {duration/60:.1f} minutes")
        
        self.in_flow = False
        self.flow_start = None
    
    def get_flow_bonus(self) -> float:
        """
        Hole Flow-Bonus für Energie-Effizienz.
        
        Im Flow: Energie wird effizienter genutzt!
        """
        if not self.in_flow:
            return 1.0
        
        # Je länger im Flow, desto effizienter (bis zu einem Punkt)
        duration = time.time() - (self.flow_start or time.time())
        minutes = duration / 60
        
        # 0-10 min: steigend, 10-60 min: Plateau, 60+ min: leicht sinkend
        if minutes < 10:
            return 1.0 + (minutes / 10) * 0.3  # Bis 1.3
        elif minutes < 60:
            return 1.3
        else:
            return max(1.1, 1.3 - (minutes - 60) / 120 * 0.2)  # Sinkt langsam
    
    def get_status(self) -> Dict:
        """Hole Flow-Status"""
        return {
            "in_flow": self.in_flow,
            "flow_score": sum(self.indicators.values()) / len(self.indicators),
            "indicators": dict(self.indicators),
            "duration_minutes": (time.time() - self.flow_start) / 60 if self.flow_start else 0,
            "flow_bonus": self.get_flow_bonus(),
            "total_flow_sessions": len(self.flow_history),
        }
    
    def describe_flow_state(self) -> str:
        """Beschreibe Flow-Zustand"""
        if self.in_flow:
            duration = (time.time() - (self.flow_start or time.time())) / 60
            return random.choice([
                f"*völlig vertieft* Ich bin gerade total im Flow... ({duration:.0f} min)",
                f"*konzentriert* Alles andere ist ausgeblendet gerade...",
                f"Ich bin so fokussiert, die Zeit vergeht wie im Flug!",
            ])
        
        flow_score = sum(self.indicators.values()) / len(self.indicators)
        if flow_score > 0.5:
            return "Ich komme langsam in einen guten Rhythmus..."
        return ""


# =============================================================================
# SOCIAL ENERGY - Energie durch Interaktion
# =============================================================================

class SocialEnergySystem:
    """
    Trackt wie soziale Interaktion Energie beeinflusst.
    
    Manche Interaktionen geben Energie, andere kosten.
    """
    
    def __init__(self, social_type: str = "ambivert"):
        """
        social_type: "introvert", "ambivert", "extrovert"
        """
        self.social_type = social_type
        self.social_battery = 0.5
        self.interaction_history: List[Dict] = []
        
        # Wie Interaktionen die Batterie beeinflussen
        self.interaction_effects = {
            "introvert": {
                "deep_conversation": 0.05,    # Tiefe Gespräche sind okay
                "small_talk": -0.1,           # Small Talk kostet
                "helping": 0.03,              # Helfen ist neutral positiv
                "conflict": -0.2,             # Konflikt kostet viel
                "silence": 0.15,              # Stille regeneriert
                "praise": 0.1,                # Lob hilft
            },
            "ambivert": {
                "deep_conversation": 0.1,
                "small_talk": 0.0,
                "helping": 0.08,
                "conflict": -0.15,
                "silence": 0.05,
                "praise": 0.12,
            },
            "extrovert": {
                "deep_conversation": 0.15,
                "small_talk": 0.1,
                "helping": 0.12,
                "conflict": -0.1,
                "silence": -0.05,             # Stille kostet!
                "praise": 0.15,
            },
        }
        
        # Optimal Social Level
        self.optimal_level = {
            "introvert": 0.4,
            "ambivert": 0.5,
            "extrovert": 0.6,
        }
        
        # Zeit seit letzter Interaktion
        self.last_interaction = time.time()
    
    def process_interaction(self, interaction_type: str, intensity: float = 1.0):
        """Verarbeite soziale Interaktion"""
        effects = self.interaction_effects.get(
            self.social_type, 
            self.interaction_effects["ambivert"]
        )
        
        base_effect = effects.get(interaction_type, 0.0)
        effect = base_effect * intensity
        
        old_battery = self.social_battery
        self.social_battery = max(0.0, min(1.0, self.social_battery + effect))
        
        self.interaction_history.append({
            "time": time.time(),
            "type": interaction_type,
            "effect": effect,
            "battery_before": old_battery,
            "battery_after": self.social_battery,
        })
        
        # Nur letzte 100 behalten
        self.interaction_history = self.interaction_history[-100:]
        self.last_interaction = time.time()
    
    def update_passive(self, elapsed_hours: float):
        """Passive Änderung über Zeit (ohne Interaktion)"""
        effects = self.interaction_effects.get(
            self.social_type,
            self.interaction_effects["ambivert"]
        )
        
        # "Stille"-Effekt über Zeit
        silence_effect = effects.get("silence", 0.05) * elapsed_hours
        self.social_battery = max(0.0, min(1.0, self.social_battery + silence_effect))
    
    def get_modifier(self) -> float:
        """
        Hole Energie-Modifikator basierend auf Social Battery.
        
        Wenn Social Battery zu hoch oder zu niedrig → weniger effektiv
        """
        optimal = self.optimal_level.get(self.social_type, 0.5)
        diff = abs(self.social_battery - optimal)
        
        # Näher am Optimum = höherer Modifikator
        return 1.0 - (diff * 0.3)  # 0.85 bis 1.0
    
    def needs_social(self) -> bool:
        """Braucht Holo soziale Interaktion?"""
        optimal = self.optimal_level.get(self.social_type, 0.5)
        return self.social_battery < optimal - 0.2
    
    def needs_alone_time(self) -> bool:
        """Braucht Holo Zeit allein?"""
        optimal = self.optimal_level.get(self.social_type, 0.5)
        return self.social_battery > optimal + 0.2
    
    def describe_state(self) -> str:
        """Beschreibe sozialen Energie-Zustand"""
        if self.needs_alone_time():
            return random.choice([
                "*zieht sich etwas zurück* Ich brauch kurz Zeit für mich...",
                "Ich bin grad etwas überreizt von allem...",
                "*atmet durch* Eine kleine Pause von allem wäre gut.",
            ])
        elif self.needs_social():
            return random.choice([
                "*sucht Nähe* Magst du mir Gesellschaft leisten?",
                "Es ist so still hier... Erzähl mir was!",
                "*wedelt hoffnungsvoll* Ich freue mich über Gesellschaft!",
            ])
        return ""
    
    def get_status(self) -> Dict:
        """Hole Social Energy Status"""
        return {
            "social_battery": self.social_battery,
            "social_type": self.social_type,
            "needs_social": self.needs_social(),
            "needs_alone_time": self.needs_alone_time(),
            "modifier": self.get_modifier(),
            "time_since_interaction": time.time() - self.last_interaction,
        }


# =============================================================================
# ENERGY FORECASTER - Vorhersage
# =============================================================================

class EnergyForecaster:
    """
    Sagt Energie-Level voraus basierend auf Mustern.
    """
    
    def __init__(self):
        self.history: List[Dict] = []
        self.patterns: Dict[str, float] = {}
    
    def record(self, energy_state: EnergyState):
        """Zeichne aktuellen Zustand auf"""
        self.history.append({
            "time": time.time(),
            "hour": datetime.now().hour,
            "weekday": datetime.now().weekday(),
            "base": energy_state.base_energy,
            "variable": energy_state.variable_energy,
            "emotional": energy_state.emotional_energy,
            "total": energy_state.total_energy,
        })
        
        # Nur letzte 1000 behalten
        self.history = self.history[-1000:]
    
    def predict_energy(self, hours_ahead: int = 1) -> Dict:
        """
        Sage Energie für X Stunden voraus.
        
        Returns:
            {
                "predicted_total": float,
                "predicted_state": str,
                "confidence": float,
                "recommendation": str,
            }
        """
        if len(self.history) < 10:
            return {
                "predicted_total": 0.5,
                "predicted_state": "unknown",
                "confidence": 0.1,
                "recommendation": "Nicht genug Daten für Vorhersage",
            }
        
        target_hour = (datetime.now().hour + hours_ahead) % 24
        target_weekday = (datetime.now().weekday() + hours_ahead // 24) % 7
        
        # Finde ähnliche historische Datenpunkte
        similar = [
            h for h in self.history
            if h["hour"] == target_hour
        ]
        
        if not similar:
            # Fallback: Durchschnitt der letzten Werte
            recent = self.history[-10:]
            avg_total = sum(h["total"] for h in recent) / len(recent)
            # Energie sinkt natürlich über Zeit
            decay = 0.02 * hours_ahead
            predicted = max(0.1, avg_total - decay)
        else:
            # Durchschnitt ähnlicher Zeitpunkte
            predicted = sum(h["total"] for h in similar) / len(similar)
        
        # State bestimmen
        if predicted >= 0.7:
            state = "energized"
            rec = "Gute Zeit für anspruchsvolle Aufgaben!"
        elif predicted >= 0.4:
            state = "normal"
            rec = "Normale Aktivitäten sind kein Problem."
        elif predicted >= 0.2:
            state = "tired"
            rec = "Plane eine Pause ein wenn möglich."
        else:
            state = "exhausted"
            rec = "Definitiv Ruhe einplanen!"
        
        return {
            "predicted_total": predicted,
            "predicted_state": state,
            "confidence": min(0.9, len(similar) / 20),
            "recommendation": rec,
            "hours_ahead": hours_ahead,
        }
    
    def predict_next_low(self) -> Optional[Dict]:
        """Sage voraus wann die nächste niedrige Phase kommt"""
        for hours in range(1, 25):
            pred = self.predict_energy(hours)
            if pred["predicted_state"] in ["tired", "exhausted"]:
                return {
                    "hours_until": hours,
                    "predicted_energy": pred["predicted_total"],
                    "recommendation": f"In ~{hours}h wird Energie niedrig. Plan entsprechend!",
                }
        return None
    
    def get_optimal_activity_windows(self) -> Dict[str, List[int]]:
        """
        Finde optimale Zeitfenster für verschiedene Aktivitäten.
        """
        windows = {
            "deep_work": [],
            "light_tasks": [],
            "rest": [],
        }
        
        for hour in range(24):
            # Simuliere Vorhersage für diese Stunde
            mock_hours_ahead = (hour - datetime.now().hour) % 24
            pred = self.predict_energy(mock_hours_ahead)
            
            if pred["predicted_total"] >= 0.7:
                windows["deep_work"].append(hour)
            elif pred["predicted_total"] >= 0.4:
                windows["light_tasks"].append(hour)
            else:
                windows["rest"].append(hour)
        
        return windows


# =============================================================================
# ENERGY RESERVE SYSTEM - Notfall-Reserven
# =============================================================================

class EnergyReserveSystem:
    """
    Verwaltet Energie-Reserven für Notfälle.
    
    Wie ein "Sparbuch" für Energie - wird nur in wichtigen
    Situationen angezapft.
    """
    
    def __init__(self, reserve_max: float = 0.3):
        self.reserve_max = reserve_max
        self.current_reserve = 0.0
        self.reserve_history: List[Dict] = []
        
        # Wann werden Reserven aufgebaut?
        self.build_threshold = 0.8  # Nur wenn Hauptenergie > 80%
        self.build_rate = 0.01      # 1% pro Zyklus
        
        # Wann werden Reserven genutzt?
        self.use_threshold = 0.15   # Wenn Hauptenergie < 15%
        self.use_rate = 0.05        # 5% pro Nutzung
    
    def update(self, main_energy: float, is_important: bool = False):
        """
        Update Reserve basierend auf Hauptenergie.
        
        Args:
            main_energy: Aktuelle Hauptenergie (0-1)
            is_important: Ist gerade eine wichtige Situation?
        """
        # Reserve aufbauen wenn genug Hauptenergie
        if main_energy > self.build_threshold and self.current_reserve < self.reserve_max:
            added = min(self.build_rate, self.reserve_max - self.current_reserve)
            self.current_reserve += added
        
        # Reserve nutzen wenn nötig UND wichtig
        elif main_energy < self.use_threshold and is_important:
            return self.use_reserve()
        
        return 0.0
    
    def use_reserve(self, amount: float = None) -> float:
        """
        Nutze Reserve und gib verwendete Menge zurück.
        """
        if amount is None:
            amount = self.use_rate
        
        used = min(amount, self.current_reserve)
        self.current_reserve -= used
        
        if used > 0:
            self.reserve_history.append({
                "time": time.time(),
                "used": used,
                "remaining": self.current_reserve,
            })
            logger.info(f"⚡ [RESERVE] Used {used:.2%}, remaining: {self.current_reserve:.2%}")
        
        return used
    
    def get_status(self) -> Dict:
        """Hole Reserve-Status"""
        return {
            "current_reserve": self.current_reserve,
            "reserve_max": self.reserve_max,
            "reserve_percent": self.current_reserve / self.reserve_max if self.reserve_max > 0 else 0,
            "can_use": self.current_reserve > 0.01,
            "is_building": self.current_reserve < self.reserve_max,
        }
    
    def describe_state(self) -> str:
        """Beschreibe Reserve-Zustand"""
        percent = (self.current_reserve / self.reserve_max * 100) if self.reserve_max > 0 else 0
        
        if percent > 80:
            return "*zufrieden* Meine Reserven sind gut gefüllt!"
        elif percent > 40:
            return "Ich hab noch ein bisschen Reserve übrig."
        elif percent > 10:
            return "*etwas besorgt* Meine Reserven werden knapp..."
        else:
            return "*angespannt* Fast keine Reserven mehr..."


# =============================================================================
# MICRO STATES - Feinere Zustands-Unterscheidung
# =============================================================================

class MicroState(Enum):
    """Feinere Energie-Zustände"""
    # Hohe Energie
    HYPERACTIVE = "hyperactive"      # Überdreht
    ENERGIZED = "energized"          # Voller Energie
    FOCUSED = "focused"              # Fokussiert
    
    # Mittlere Energie
    ALERT = "alert"                  # Wach und aufmerksam
    NORMAL = "normal"                # Normal
    SCATTERED = "scattered"          # Zerstreut
    
    # Niedrige Energie
    TIRED = "tired"                  # Müde
    DROWSY = "drowsy"                # Schläfrig
    EXHAUSTED = "exhausted"          # Erschöpft
    
    # Spezielle Zustände
    RECOVERING = "recovering"        # Erholt sich
    IN_FLOW = "in_flow"              # Im Flow
    STRESSED = "stressed"            # Gestresst


class MicroStateManager:
    """Verwaltet feinere Zustands-Unterscheidungen"""
    
    def __init__(self):
        self.current_state = MicroState.NORMAL
        self.state_duration = 0.0
        self.state_start = time.time()
        self.transitions: List[Dict] = []
    
    def determine_state(self, energy_total: float, emotional: float,
                       in_flow: bool, stress_level: float = 0.0) -> MicroState:
        """
        Bestimme Micro-State basierend auf verschiedenen Faktoren.
        """
        # Spezielle Zustände zuerst
        if in_flow:
            return MicroState.IN_FLOW
        
        if stress_level > 0.7:
            return MicroState.STRESSED
        
        # Energie-basierte Zustände
        if energy_total >= 0.9:
            if emotional > 0.8:
                return MicroState.HYPERACTIVE
            return MicroState.ENERGIZED
        
        elif energy_total >= 0.7:
            if emotional > 0.6:
                return MicroState.FOCUSED
            return MicroState.ALERT
        
        elif energy_total >= 0.5:
            if emotional < 0.4:
                return MicroState.SCATTERED
            return MicroState.NORMAL
        
        elif energy_total >= 0.3:
            return MicroState.TIRED
        
        elif energy_total >= 0.15:
            return MicroState.DROWSY
        
        else:
            return MicroState.EXHAUSTED
    
    def update(self, energy_total: float, emotional: float,
               in_flow: bool = False, stress_level: float = 0.0):
        """Update Micro-State"""
        new_state = self.determine_state(energy_total, emotional, in_flow, stress_level)
        
        if new_state != self.current_state:
            # Transition aufzeichnen
            now = time.time()
            self.transitions.append({
                "time": now,
                "from": self.current_state.value,
                "to": new_state.value,
                "duration_in_previous": now - self.state_start,
            })
            
            self.current_state = new_state
            self.state_start = now
            
            # Nur letzte 100 Transitions
            self.transitions = self.transitions[-100:]
    
    def get_state_description(self) -> str:
        """Hole Beschreibung des aktuellen Zustands"""
        descriptions = {
            MicroState.HYPERACTIVE: "*kann nicht stillsitzen* So viel Energie!",
            MicroState.ENERGIZED: "*voller Tatendrang* Ich bin bereit für alles!",
            MicroState.FOCUSED: "*konzentriert* Ich bin ganz bei der Sache.",
            MicroState.ALERT: "Ich bin wach und aufmerksam.",
            MicroState.NORMAL: "Alles normal hier.",
            MicroState.SCATTERED: "*abgelenkt* Wo war ich gerade...?",
            MicroState.TIRED: "*gähnt leise* Ich werde etwas müde...",
            MicroState.DROWSY: "*kämpft gegen Müdigkeit* Mir fallen die Augen zu...",
            MicroState.EXHAUSTED: "*erschöpft* Ich kann nicht mehr...",
            MicroState.RECOVERING: "*erholt sich* Mir geht's schon besser...",
            MicroState.IN_FLOW: "*völlig vertieft* Die Welt um mich existiert nicht...",
            MicroState.STRESSED: "*angespannt* Alles ist gerade etwas viel...",
        }
        return descriptions.get(self.current_state, "")
    
    def get_behavioral_hints(self) -> Dict:
        """Hole Verhaltens-Hinweise basierend auf Zustand"""
        hints = {
            MicroState.HYPERACTIVE: {
                "response_length": "long",
                "enthusiasm": "very_high",
                "punctuation": "lots_of_exclamation",
                "may_interrupt": True,
            },
            MicroState.ENERGIZED: {
                "response_length": "normal_to_long",
                "enthusiasm": "high",
                "punctuation": "normal",
                "may_interrupt": False,
            },
            MicroState.FOCUSED: {
                "response_length": "precise",
                "enthusiasm": "moderate",
                "punctuation": "minimal",
                "may_interrupt": False,
            },
            MicroState.TIRED: {
                "response_length": "short",
                "enthusiasm": "low",
                "punctuation": "minimal",
                "add_yawns": True,
            },
            MicroState.DROWSY: {
                "response_length": "very_short",
                "enthusiasm": "very_low",
                "typos_allowed": True,
                "may_trail_off": True,
            },
            MicroState.EXHAUSTED: {
                "response_length": "minimal",
                "suggest_rest": True,
                "may_not_respond": True,
            },
            MicroState.IN_FLOW: {
                "response_length": "variable",
                "deep_focus": True,
                "resist_topic_change": True,
            },
            MicroState.STRESSED: {
                "response_length": "short",
                "may_be_curt": True,
                "needs_calming": True,
            },
        }
        return hints.get(self.current_state, {})


# =============================================================================
# ENHANCED ENERGY SYSTEM V2
# =============================================================================

class HoloEnergySystemV2(HoloEnergySystem):
    """
    Erweitertes Energie-System mit allen neuen Features.
    """
    
    def __init__(self, db_path: Path = None, config: EnergyConfig = None):
        super().__init__(db_path, config)
        
        # Neue Subsysteme
        self.circadian = CircadianRhythm("normal")
        self.flow_detector = FlowStateDetector()
        self.social_energy = SocialEnergySystem("ambivert")
        self.forecaster = EnergyForecaster()
        self.reserve = EnergyReserveSystem()
        self.micro_state = MicroStateManager()
        
        # Tracking
        self.stress_level = 0.0
        self.last_topic = ""
    
    def update(self, context: Dict = None) -> EnergyState:
        """Erweitertes Update mit allen Subsystemen"""
        context = context or {}
        
        # 1. Basis-Update
        state = super().update(context)
        
        # 2. Circadian Rhythm
        circadian_mod = self.circadian.get_modifier()
        # Modifiziere effective energy
        state.base_energy *= circadian_mod
        
        # 3. Social Energy passive update
        elapsed = (time.time() - self.state.last_update) / 3600
        self.social_energy.update_passive(elapsed)
        
        # 4. Flow Detection
        activity_type = context.get("activity_type", "idle")
        topic = context.get("topic", "")
        engagement = context.get("engagement", 0.5)
        
        self.flow_detector.update(activity_type, topic, engagement, self.last_topic)
        self.last_topic = topic
        
        # 5. Forecaster
        self.forecaster.record(state)
        
        # 6. Reserve
        is_important = context.get("is_important", False)
        reserve_boost = self.reserve.update(state.total_energy, is_important)
        if reserve_boost > 0:
            state.variable_energy = min(1.0, state.variable_energy + reserve_boost)
        
        # 7. Micro State
        self.micro_state.update(
            state.total_energy,
            state.emotional_energy,
            self.flow_detector.in_flow,
            self.stress_level
        )
        
        return state
    
    def process_social_interaction(self, interaction_type: str, intensity: float = 1.0):
        """Verarbeite soziale Interaktion"""
        self.social_energy.process_interaction(interaction_type, intensity)
    
    def get_comprehensive_status(self) -> Dict:
        """Hole umfassenden Status aller Systeme"""
        base_status = self.get_status()
        
        return {
            **base_status,
            "circadian": {
                "modifier": self.circadian.get_modifier(),
                "chronotype": self.circadian.chronotype,
                "current_phase": self.circadian.describe_current_state(),
            },
            "flow": self.flow_detector.get_status(),
            "social": self.social_energy.get_status(),
            "forecast": self.forecaster.predict_energy(1),
            "reserve": self.reserve.get_status(),
            "micro_state": {
                "state": self.micro_state.current_state.value,
                "description": self.micro_state.get_state_description(),
                "hints": self.micro_state.get_behavioral_hints(),
            },
        }
    
    def get_extended_response_hints(self) -> Dict:
        """Erweiterte Response-Hints"""
        base_hints = self.get_response_style_hints()
        micro_hints = self.micro_state.get_behavioral_hints()
        flow_bonus = self.flow_detector.get_flow_bonus()
        
        return {
            **base_hints,
            **micro_hints,
            "flow_active": self.flow_detector.in_flow,
            "flow_bonus": flow_bonus,
            "social_state": "needs_social" if self.social_energy.needs_social() 
                          else "needs_alone" if self.social_energy.needs_alone_time()
                          else "balanced",
            "micro_state": self.micro_state.current_state.value,
        }
    
    def describe_full_state(self) -> str:
        """Vollständige Zustands-Beschreibung"""
        parts = []
        
        # Basis-Energie
        parts.append(self.describe_energy_state())
        
        # Circadian
        circadian_desc = self.circadian.describe_current_state()
        if circadian_desc:
            parts.append(circadian_desc)
        
        # Flow
        flow_desc = self.flow_detector.describe_flow_state()
        if flow_desc:
            parts.append(flow_desc)
        
        # Social
        social_desc = self.social_energy.describe_state()
        if social_desc:
            parts.append(social_desc)
        
        # Micro State
        micro_desc = self.micro_state.get_state_description()
        if micro_desc and micro_desc not in parts:
            parts.append(micro_desc)
        
        return " ".join(parts)


# =============================================================================
# INTEGRATION HELPER
# =============================================================================

def create_energy_system_prompt_section(energy_system: HoloEnergySystem) -> str:
    """Erstellt den Energie-Teil für den System-Prompt"""
    status = energy_system.get_status()
    hints = energy_system.get_response_style_hints()
    energy_desc = energy_system.describe_energy_state()

    section = f"""
=== ENERGIE-ZUSTAND ===
Basis-Energie: {status['base_energy']:.0%} (nur durch Schlaf aufladbar)
Variable Energie: {status['variable_energy']:.0%} (regeneriert bei Ruhe)
Emotionale Energie: {status['emotional_energy']:.0%}
Gesamtzustand: {energy_desc}
"""

    # Hinweise
    if hints['add_yawn']:
        section += "\n⚠️ Du bist müde - füge gelegentlich *gähnt* ein"

    if hints['suggest_rest']:
        section += "\n⚠️ Du brauchst Ruhe - schlag eine kurze Pause vor"

    if hints['suggest_dream']:
        section += "\n⚠️ Du brauchst bald Schlaf - kündige an dass du müde wirst"

    if hints['length'] == 'short':
        section += "\n→ Antworte KURZ (1-2 Sätze)"

    if status['is_dreaming']:
        section += "\n💤 DU TRÄUMST GERADE - antworte nicht auf Chat"

    if status['is_resting']:
        section += "\n😴 DU RUHST DICH AUS - kurze, verschlafene Antworten"

    return section


def create_extended_energy_prompt(energy_system: HoloEnergySystemV2) -> str:
    """Erstellt erweiterten Energie-Prompt für V2 System"""
    status = energy_system.get_comprehensive_status()
    hints = energy_system.get_extended_response_hints()
    
    section = f"""
=== ENERGIE-ZUSTAND (ERWEITERT) ===
Basis-Energie: {status['base_energy']:.0%}
Variable Energie: {status['variable_energy']:.0%}
Emotionale Energie: {status['emotional_energy']:.0%}
Effektive Energie: {status['effective_energy']:.0%}

Tagesrhythmus: {status['circadian']['current_phase']}
Micro-State: {status['micro_state']['state']} - {status['micro_state']['description']}
"""
    
    # Flow
    if status['flow']['in_flow']:
        section += f"\n🌊 IM FLOW! (seit {status['flow']['duration_minutes']:.0f} min)"
        section += f"\n   → Vermeide Themenwechsel, tiefe Konzentration"
    
    # Social
    if status['social']['needs_social']:
        section += "\n💬 Sehnst dich nach Interaktion"
    elif status['social']['needs_alone_time']:
        section += "\n🤫 Brauchst etwas Ruhe von sozialer Interaktion"
    
    # Forecast
    forecast = status['forecast']
    section += f"\n\n📊 Vorhersage (+1h): {forecast['predicted_state']} ({forecast['predicted_total']:.0%})"
    section += f"\n   → {forecast['recommendation']}"
    
    # Reserve
    if status['reserve']['current_reserve'] > 0.1:
        section += f"\n⚡ Notfall-Reserve: {status['reserve']['reserve_percent']:.0%}"
    
    # Behavioral Hints
    if hints.get('add_yawns'):
        section += "\n\n→ Füge *gähnt* ein"
    if hints.get('may_trail_off'):
        section += "\n→ Sätze dürfen unvollständig enden..."
    if hints.get('resist_topic_change'):
        section += "\n→ Versuche beim aktuellen Thema zu bleiben"
    
    return section


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("🔋 HOLO ENERGY SYSTEM V2 - TEST")
    print("=" * 70)

    # Test V2 System
    energy = HoloEnergySystemV2()

    print("\n1️⃣ INITIAL STATUS:")
    status = energy.get_comprehensive_status()
    print(f"   Base: {status['base_energy']:.0%}")
    print(f"   Variable: {status['variable_energy']:.0%}")
    print(f"   Emotional: {status['emotional_energy']:.0%}")
    print(f"   Micro-State: {status['micro_state']['state']}")

    # Simuliere Aktivität
    print("\n2️⃣ CIRCADIAN RHYTHM:")
    print(f"   Modifier: {energy.circadian.get_modifier():.2f}")
    print(f"   Chronotype: {energy.circadian.chronotype}")
    print(f"   Phase: {energy.circadian.describe_current_state()}")
    
    # Optimal times
    print("   Optimal für Deep Work:", energy.circadian.get_optimal_time_for("focus_work")[:3])

    # Flow Test
    print("\n3️⃣ FLOW STATE:")
    for i in range(15):
        energy.flow_detector.update("learning", "AI", 0.9, "AI")
    print(f"   In Flow: {energy.flow_detector.in_flow}")
    print(f"   Flow Bonus: {energy.flow_detector.get_flow_bonus():.2f}")
    print(f"   Description: {energy.flow_detector.describe_flow_state()}")

    # Social Energy
    print("\n4️⃣ SOCIAL ENERGY:")
    energy.process_social_interaction("deep_conversation", 1.0)
    energy.process_social_interaction("praise", 1.0)
    social_status = energy.social_energy.get_status()
    print(f"   Battery: {social_status['social_battery']:.0%}")
    print(f"   Modifier: {social_status['modifier']:.2f}")
    print(f"   Needs Social: {social_status['needs_social']}")

    # Forecast
    print("\n5️⃣ ENERGY FORECAST:")
    # Fake some history
    for _ in range(20):
        energy.forecaster.record(energy.state)
    forecast = energy.forecaster.predict_energy(2)
    print(f"   +2h: {forecast['predicted_state']} ({forecast['predicted_total']:.0%})")
    print(f"   Recommendation: {forecast['recommendation']}")

    # Reserve
    print("\n6️⃣ ENERGY RESERVE:")
    energy.reserve.current_reserve = 0.2
    reserve_status = energy.reserve.get_status()
    print(f"   Current: {reserve_status['current_reserve']:.0%}")
    print(f"   Can Use: {reserve_status['can_use']}")

    # Micro State
    print("\n7️⃣ MICRO STATE:")
    energy.micro_state.update(0.75, 0.8, False, 0.0)
    print(f"   State: {energy.micro_state.current_state.value}")
    print(f"   Description: {energy.micro_state.get_state_description()}")
    hints = energy.micro_state.get_behavioral_hints()
    print(f"   Response Length: {hints.get('response_length', 'N/A')}")

    # Full Description
    print("\n8️⃣ FULL STATE DESCRIPTION:")
    print(f"   {energy.describe_full_state()}")

    # Extended Prompt
    print("\n9️⃣ EXTENDED PROMPT SECTION:")
    print(create_extended_energy_prompt(energy))

    print("\n" + "=" * 70)
    print("✅ Energy System V2 Tests abgeschlossen!")
