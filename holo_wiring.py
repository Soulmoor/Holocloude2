#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO WIRING v15.0 - Vollständige Modul-Integration                          ║
║                                                                              ║
║  NEUE INTEGRATIONEN:                                                         ║
║  • IntelligentRouter - Zentrale Routing-Logik                                ║
║  • ContextCompressor - Token-Sparung                                         ║
║  • ImpulseGenerator - Authentische Impulse                                   ║
║  • NLPAlgorithms - Lokale Verarbeitung                                       ║
║  • EmotionLevels - 12 Emotionen × 3 Stufen                                   ║
║                                                                              ║
║  VERBINDUNGS-MATRIX:                                                         ║
║  ┌─────────────┬──────────────────────────────────────────────────────────┐  ║
║  │   MODULE    │                    VERBINDUNGEN                         │  ║
║  ├─────────────┼──────────────────────────────────────────────────────────┤  ║
║  │ Router      │ → Energy, Emotions, Cognitive, Memory, Impulse, NLP     │  ║
║  │ Impulse     │ → Energy, Emotions, Events, AutonomousLife              │  ║
║  │ Context     │ → Memory, Conversation History                          │  ║
║  │ NLP         │ → Intent, Sentiment, Router                             │  ║
║  │ Emotions    │ → Energy, Personality, SelfExpression                   │  ║
║  └─────────────┴──────────────────────────────────────────────────────────┘  ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 15.0                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum

logger = logging.getLogger("HoloWiring")

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value


# =============================================================================
# WIRING CONFIGURATION
# =============================================================================

@dataclass
class ModuleConnection:
    """Definition einer Modul-Verbindung"""
    source: str              # Quell-Modul
    target: str              # Ziel-Modul
    attribute: str           # Attribut-Name im Ziel
    description: str = ""    # Beschreibung
    required: bool = False   # Pflicht-Verbindung?
    bidirectional: bool = False  # Beide Richtungen?


@dataclass 
class CallbackDefinition:
    """Definition eines Callbacks"""
    source: str              # Wer ruft
    event: str               # Event-Name
    targets: List[str]       # Wer wird benachrichtigt
    description: str = ""


# =============================================================================
# VOLLSTÄNDIGE VERBINDUNGS-MATRIX
# =============================================================================

# Alle Modul-Verbindungen
MODULE_CONNECTIONS: List[ModuleConnection] = [
    # === ROUTER VERBINDUNGEN (Zentral) ===
    ModuleConnection("energy", "router", "energy_system",
                    "Router braucht Energie für Stil-Entscheidungen", True),
    ModuleConnection("emotions", "router", "emotions",
                    "Router braucht Emotionen für Personalisierung", True),
    ModuleConnection("cognitive", "router", "cognitive",
                    "Router braucht Cognitive für Tiefe-Entscheidungen"),
    ModuleConnection("memory", "router", "memory",
                    "Router braucht Memory für Kontext"),
    ModuleConnection("autonomous_life", "router", "autonomous_life",
                    "Router braucht Autonomous für Sozial-Zustand"),
    ModuleConnection("consciousness", "router", "consciousness",
                    "Router braucht Consciousness für Philosophie"),
    ModuleConnection("self_awareness", "router", "self_awareness",
                    "Router braucht SelfAwareness für Reflexion"),
    ModuleConnection("personality", "router", "personality",
                    "Router braucht Personality für Bond-Level"),
    ModuleConnection("interface", "router", "interface",
                    "Router braucht Interface für Wetter"),
    ModuleConnection("impulse_generator", "router", "impulse_generator",
                    "Router braucht Impulse für authentische Basis"),
    ModuleConnection("context_compressor", "router", "context_compressor",
                    "Router braucht Compressor für Token-Sparung"),
    
    # === IMPULSE GENERATOR VERBINDUNGEN ===
    ModuleConnection("energy", "impulse_generator", "energy",
                    "Impulse basieren auf Energie", True),
    ModuleConnection("autonomous_life", "impulse_generator", "autonomous_life",
                    "Impulse basieren auf Langeweile/Einsamkeit"),
    ModuleConnection("personality", "impulse_generator", "personality",
                    "Impulse basieren auf Emotionen"),
    ModuleConnection("events", "impulse_generator", "events",
                    "Impulse reagieren auf Events"),
    
    # === CONTEXT COMPRESSOR VERBINDUNGEN ===
    ModuleConnection("memory", "context_compressor", "memory",
                    "Compressor braucht Memory für Entitäten"),
    
    # === COGNITIVE ENGINE VERBINDUNGEN ===
    ModuleConnection("perception_engine", "consciousness_engine", "perception",
                    "Consciousness braucht Perception", True),
    ModuleConnection("reasoning_engine", "consciousness_engine", "reasoning",
                    "Consciousness braucht Reasoning", True),
    ModuleConnection("advanced_learning", "consciousness_engine", "learning",
                    "Consciousness braucht Learning"),
    ModuleConnection("memory", "consciousness_engine", "memory",
                    "Consciousness braucht Memory", True),
    ModuleConnection("energy", "consciousness_engine", "energy",
                    "Consciousness reagiert auf Energie"),
    
    ModuleConnection("consciousness_engine", "reasoning_engine", "consciousness",
                    "Reasoning braucht Consciousness"),
    ModuleConnection("perception_engine", "reasoning_engine", "perception",
                    "Reasoning braucht Perception"),
    ModuleConnection("advanced_learning", "reasoning_engine", "learning",
                    "Reasoning braucht Learning"),
    
    ModuleConnection("consciousness_engine", "perception_engine", "consciousness",
                    "Perception braucht Consciousness"),
    ModuleConnection("memory", "perception_engine", "memory",
                    "Perception braucht Memory"),
    
    ModuleConnection("consciousness_engine", "advanced_learning", "consciousness",
                    "Learning braucht Consciousness"),
    ModuleConnection("reasoning_engine", "advanced_learning", "reasoning",
                    "Learning braucht Reasoning"),
    ModuleConnection("memory", "advanced_learning", "memory",
                    "Learning braucht Memory", True),
    ModuleConnection("web_curiosity", "advanced_learning", "curiosity",
                    "Learning braucht Curiosity"),
    
    # === SELF AWARENESS VERBINDUNGEN ===
    ModuleConnection("consciousness_engine", "self_awareness", "consciousness",
                    "SelfAwareness braucht Consciousness"),
    ModuleConnection("advanced_learning", "self_awareness", "learning",
                    "SelfAwareness braucht Learning"),
    ModuleConnection("reasoning_engine", "self_awareness", "reasoning",
                    "SelfAwareness braucht Reasoning"),
    ModuleConnection("memory", "self_awareness", "memory",
                    "SelfAwareness braucht Memory"),
    ModuleConnection("personality", "self_awareness", "personality",
                    "SelfAwareness braucht Personality"),
    
    # === LOYALTY CORE VERBINDUNGEN ===
    ModuleConnection("cognitive", "loyalty_core", "integration",
                    "Loyalty braucht Cognitive"),
    ModuleConnection("memory", "loyalty_core", "memory",
                    "Loyalty braucht Memory"),
    ModuleConnection("consciousness_engine", "loyalty_core", "consciousness",
                    "Loyalty braucht Consciousness"),
    
    # === CONSCIOUSNESS VERBINDUNGEN ===
    ModuleConnection("energy", "consciousness", "energy",
                    "Consciousness reagiert auf Energie"),
    ModuleConnection("advanced_learning", "consciousness", "learning",
                    "Consciousness lernt"),
    ModuleConnection("memory", "consciousness", "memory",
                    "Consciousness erinnert"),
    ModuleConnection("personality", "consciousness", "personality",
                    "Consciousness hat Persönlichkeit"),
    
    # === ENERGY VERBINDUNGEN ===
    ModuleConnection("consciousness_engine", "energy", "consciousness",
                    "Energy beeinflusst Consciousness"),
    ModuleConnection("advanced_learning", "energy", "learning",
                    "Learning registriert Energie-Muster"),
    
    # === ENERGY MANAGEMENT VERBINDUNGEN ===
    ModuleConnection("energy", "energy_management", "energy_system",
                    "Management braucht Energy", True),
    ModuleConnection("memory", "energy_management", "memory",
                    "Management braucht Memory"),
    ModuleConnection("autonomous_life", "energy_management", "autonomous_life",
                    "Management koordiniert mit Autonomous"),
    
    # === AUTONOMOUS LIFE VERBINDUNGEN ===
    ModuleConnection("energy", "autonomous_life", "energy",
                    "Autonomous braucht Energy", True),
    ModuleConnection("memory", "autonomous_life", "memory",
                    "Autonomous braucht Memory"),
    ModuleConnection("personality", "autonomous_life", "personality",
                    "Autonomous nutzt Personality"),
    ModuleConnection("preferences", "autonomous_life", "preferences",
                    "Autonomous nutzt Preferences"),
    ModuleConnection("web_curiosity", "autonomous_life", "curiosity",
                    "Autonomous hat Neugier"),
    ModuleConnection("interface", "autonomous_life", "pi_interface",
                    "Autonomous kommuniziert mit Pi"),
    
    # === PERSONALITY VERBINDUNGEN ===
    ModuleConnection("memory", "personality", "memory",
                    "Personality lernt aus Memory"),
    ModuleConnection("energy", "personality", "energy",
                    "Personality reagiert auf Energy"),
    
    # === SELF EXPRESSION VERBINDUNGEN ===
    ModuleConnection("personality", "self_expression", "personality",
                    "Expression braucht Personality", True),
    ModuleConnection("memory", "self_expression", "memory",
                    "Expression braucht Memory"),
    ModuleConnection("energy", "self_expression", "energy",
                    "Expression reagiert auf Energy"),
    ModuleConnection("consciousness_engine", "self_expression", "consciousness",
                    "Expression braucht Consciousness"),
    
    # === INNER LIFE VERBINDUNGEN ===
    ModuleConnection("personality", "inner_life", "personality",
                    "InnerLife braucht Personality"),
    ModuleConnection("memory", "inner_life", "memory",
                    "InnerLife braucht Memory"),
    ModuleConnection("energy", "inner_life", "energy",
                    "InnerLife reagiert auf Energy"),
    ModuleConnection("emotions", "inner_life", "emotions",
                    "InnerLife braucht Emotions"),
    
    # === DIALOGUE ENGINE VERBINDUNGEN ===
    ModuleConnection("memory", "dialogue_engine", "memory",
                    "Dialogue braucht Memory"),
    ModuleConnection("personality", "dialogue_engine", "personality",
                    "Dialogue braucht Personality"),
    ModuleConnection("impulse_generator", "dialogue_engine", "impulse_gen",
                    "Dialogue nutzt Impulse"),
    
    # === ORGANIC PRESENCE VERBINDUNGEN ===
    ModuleConnection("energy", "organic_presence", "energy",
                    "Presence reagiert auf Energy"),
    ModuleConnection("emotions", "organic_presence", "emotions",
                    "Presence zeigt Emotions"),
    ModuleConnection("personality", "organic_presence", "personality",
                    "Presence nutzt Personality"),
    
    # === PREFERENCES VERBINDUNGEN ===
    ModuleConnection("memory", "preferences", "memory",
                    "Preferences aus Memory"),
    ModuleConnection("personality", "preferences", "personality",
                    "Preferences beeinflussen Personality", bidirectional=True),
    
    # === WEB CURIOSITY VERBINDUNGEN ===
    ModuleConnection("memory", "web_curiosity", "memory",
                    "Curiosity speichert in Memory"),
    ModuleConnection("advanced_learning", "web_curiosity", "learning",
                    "Curiosity triggert Learning"),
    
    # === TOOLS VERBINDUNGEN ===
    ModuleConnection("memory", "tools", "memory",
                    "Tools speichern in Memory"),
    ModuleConnection("interface", "tools", "pi_interface",
                    "Tools nutzen Interface"),
    
    # === CONTEXT MANAGER VERBINDUNGEN ===
    ModuleConnection("memory", "context_manager", "memory",
                    "Context braucht Memory"),
    ModuleConnection("context_compressor", "context_manager", "compressor",
                    "Context nutzt Compressor"),
]


# Callback-Definitionen
CALLBACK_DEFINITIONS: List[CallbackDefinition] = [
    # Energy-basierte Callbacks
    CallbackDefinition(
        "energy", "on_energy_low",
        ["consciousness", "autonomous_life", "personality", "router"],
        "Wenn Energie niedrig → Müde Reaktionen"
    ),
    CallbackDefinition(
        "energy", "on_energy_high",
        ["consciousness", "autonomous_life", "personality", "router"],
        "Wenn Energie hoch → Aktive Reaktionen"
    ),
    CallbackDefinition(
        "energy", "on_dream_start",
        ["consciousness", "organic_presence", "dialogue_engine"],
        "Wenn Dream beginnt → Dream-Modus"
    ),
    CallbackDefinition(
        "energy", "on_dream_end",
        ["consciousness", "organic_presence"],
        "Wenn Dream endet → Aufwach-Reaktion"
    ),
    
    # Emotion-basierte Callbacks
    CallbackDefinition(
        "emotions", "on_emotion_change",
        ["personality", "self_expression", "inner_life", "router", "impulse_generator"],
        "Wenn Emotion ändert → Persönlichkeitsanpassung"
    ),
    CallbackDefinition(
        "emotions", "on_mood_shift",
        ["consciousness", "dialogue_engine", "router"],
        "Wenn Stimmung kippt → Dialog-Stil-Anpassung"
    ),
    
    # Cognitive Callbacks
    CallbackDefinition(
        "consciousness_engine", "on_insight",
        ["self_awareness", "advanced_learning", "memory", "router"],
        "Wenn Einsicht → Lernen + Speichern"
    ),
    CallbackDefinition(
        "advanced_learning", "on_learning_complete",
        ["emotions", "self_expression", "router"],
        "Wenn gelernt → Freude + Teilen wollen"
    ),
    CallbackDefinition(
        "reasoning_engine", "on_conclusion",
        ["consciousness_engine", "memory"],
        "Wenn Schlussfolgerung → Bewusstsein + Speichern"
    ),
    
    # Social Callbacks
    CallbackDefinition(
        "autonomous_life", "on_loneliness_high",
        ["impulse_generator", "organic_presence", "router"],
        "Wenn einsam → Proaktive Nachricht"
    ),
    CallbackDefinition(
        "autonomous_life", "on_boredom_high",
        ["impulse_generator", "web_curiosity", "router"],
        "Wenn gelangweilt → Suche nach Aktivität"
    ),
    
    # Interface Callbacks
    CallbackDefinition(
        "interface", "on_user_activity",
        ["energy", "autonomous_life", "emotions"],
        "Wenn User aktiv → Reset Einsamkeit"
    ),
    CallbackDefinition(
        "interface", "on_weather_change",
        ["personality", "impulse_generator", "router"],
        "Wenn Wetter ändert → Stimmungs-Einfluss"
    ),
    
    # Router Callbacks
    CallbackDefinition(
        "router", "on_philosophical_mode",
        ["consciousness", "self_awareness", "personality"],
        "Wenn philosophisch → Tiefes Denken aktivieren"
    ),
    CallbackDefinition(
        "router", "on_local_response",
        ["impulse_generator", "organic_presence"],
        "Wenn lokal beantwortet → Impulse nutzen"
    ),
]


# =============================================================================
# WIRING ENGINE
# =============================================================================

class HoloWiringEngine:
    """
    Hauptklasse für das Modul-Wiring.
    
    Verbindet alle Module miteinander und
    registriert Callbacks für Event-Handling.
    """
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.connections_made: List[str] = []
        self.callbacks_registered: List[str] = []
        self.errors: List[str] = []
        
        # Statistiken
        self.stats = {
            "modules_registered": 0,
            "connections_successful": 0,
            "connections_failed": 0,
            "callbacks_registered": 0,
        }
    
    def register_module(self, name: str, module: Any):
        """Registriere ein Modul"""
        self.modules[name] = module
        self.stats["modules_registered"] += 1
        logger.debug(f"[Wiring] Modul registriert: {name}")
    
    def register_modules_from_brain(self, brain):
        """Registriere alle Module von einem HoloBrain"""
        module_names = [
            # Core
            "energy", "emotions", "memory", "personality", "consciousness",
            # Cognitive
            "cognitive", "consciousness_engine", "reasoning_engine", 
            "perception_engine", "advanced_learning",
            # Life
            "autonomous_life", "inner_life", "self_expression", "self_awareness",
            # Interaction
            "dialogue_engine", "organic_presence", "interface",
            # Utilities
            "preferences", "web_curiosity", "tools", "context_manager",
            # NEW
            "router", "impulse_generator", "context_compressor",
            # Legacy
            "events", "loyalty_core",
        ]
        
        for name in module_names:
            module = getattr(brain, name, None)
            if module:
                self.register_module(name, module)
    
    def wire_all(self) -> bool:
        """Führe alle Verbindungen aus"""
        logger.info("[Wiring] Starte vollständiges Wiring...")
        
        # 1. Modul-Verbindungen
        for conn in MODULE_CONNECTIONS:
            self._make_connection(conn)
        
        # 2. Callbacks
        for cb in CALLBACK_DEFINITIONS:
            self._register_callback(cb)
        
        # Report
        success_rate = (self.stats["connections_successful"] / 
                       max(1, self.stats["connections_successful"] + self.stats["connections_failed"]))
        
        logger.info(f"[Wiring] Abgeschlossen:")
        logger.info(f"   Module: {self.stats['modules_registered']}")
        logger.info(f"   Verbindungen: {self.stats['connections_successful']} erfolgreich, "
                   f"{self.stats['connections_failed']} fehlgeschlagen")
        logger.info(f"   Callbacks: {self.stats['callbacks_registered']}")
        logger.info(f"   Erfolgsrate: {success_rate:.0%}")
        
        if self.errors:
            logger.warning(f"[Wiring] {len(self.errors)} Fehler aufgetreten")
            for err in self.errors[:5]:
                logger.warning(f"   - {err}")
        
        return success_rate > 0.7
    
    def _make_connection(self, conn: ModuleConnection):
        """Stelle eine einzelne Verbindung her"""
        source = self.modules.get(conn.source)
        target = self.modules.get(conn.target)
        
        if not source:
            if conn.required:
                self.errors.append(f"Pflicht-Quelle fehlt: {conn.source}")
                self.stats["connections_failed"] += 1
            return
        
        if not target:
            if conn.required:
                self.errors.append(f"Pflicht-Ziel fehlt: {conn.target}")
                self.stats["connections_failed"] += 1
            return
        
        try:
            setattr(target, conn.attribute, source)
            self.connections_made.append(f"{conn.source} → {conn.target}.{conn.attribute}")
            self.stats["connections_successful"] += 1
            logger.debug(f"[Wiring] ✓ {conn.source} → {conn.target}.{conn.attribute}")
            
            # Bidirektional?
            if conn.bidirectional:
                reverse_attr = safe_split_access(conn.source, "_", 0, "wiring", "_apply_connection", default="unknown")  # Vereinfachung
                if hasattr(source, reverse_attr):
                    setattr(source, reverse_attr, target)
                    
        except Exception as e:
            self.errors.append(f"Verbindung fehlgeschlagen: {conn.source} → {conn.target}: {e}")
            self.stats["connections_failed"] += 1
    
    def _register_callback(self, cb: CallbackDefinition):
        """Registriere einen Callback"""
        source = self.modules.get(cb.source)
        if not source:
            return
        
        # Prüfe ob Source den Event unterstützt
        event_attr = cb.event
        if not hasattr(source, event_attr):
            # Versuche als Methode
            if not hasattr(source, f"on_{cb.event}") and not hasattr(source, cb.event):
                return
        
        # Erstelle Callback-Funktion
        def create_callback(targets, event_name):
            def callback(*args, **kwargs):
                for target_name in targets:
                    target = self.modules.get(target_name)
                    if target:
                        handler = getattr(target, f"handle_{event_name}", None)
                        if handler and callable(handler):
                            try:
                                handler(*args, **kwargs)
                            except Exception as e:
                                logger.debug(f"Callback-Fehler: {target_name}.handle_{event_name}: {e}")
            return callback
        
        # Setze Callback
        try:
            callback_fn = create_callback(cb.targets, cb.event)
            setattr(source, event_attr, callback_fn)
            self.callbacks_registered.append(f"{cb.source}.{cb.event} → {cb.targets}")
            self.stats["callbacks_registered"] += 1
        except Exception as e:
            logger.debug(f"Callback-Registrierung fehlgeschlagen: {cb.source}.{cb.event}: {e}")
    
    def get_connection_graph(self) -> Dict[str, List[str]]:
        """Hole Verbindungs-Graph für Visualisierung"""
        graph = {}
        
        for conn in MODULE_CONNECTIONS:
            if conn.source not in graph:
                graph[conn.source] = []
            graph[conn.source].append(conn.target)
        
        return graph
    
    def get_status(self) -> Dict:
        """Hole Wiring-Status"""
        return {
            "stats": self.stats,
            "modules": list(self.modules.keys()),
            "connections": self.connections_made,
            "callbacks": self.callbacks_registered,
            "errors": self.errors,
        }


# =============================================================================
# ZUSTANDSABHÄNGIGES VERHALTEN
# =============================================================================

class StateDependentBehavior:
    """
    Definiert wie sich Holo basierend auf Zustand verhält.
    
    Dies ist die zentrale Logik für:
    - Wie Energie den Antwortstil beeinflusst
    - Wie Emotionen die Körpersprache ändern
    - Wie Cognitive State die Tiefe beeinflusst
    - Wie Sozial-Status die Proaktivität ändert
    """
    
    # === ENERGIE → VERHALTEN ===
    # Kemonomimi: Menschliche Aktionen + Ohren/Schweif (keine Wolf-Körper-Aktionen!)
    ENERGY_BEHAVIORS = {
        "exhausted": {  # < 0.2
            "response_length": 0.3,      # Kurz
            "enthusiasm": 0.2,           # Wenig
            "question_chance": 0.1,      # Kaum Fragen
            "emoji_chance": 0.3,         # Wenig Emojis
            "wolf_actions": ["*gähnt* *Ohren hängen*", "*blinzelt müde*", "*seufzt* *Schweif liegt*"],
            "tone": "müde",
            "speed": "slow",
        },
        "tired": {  # 0.2-0.4
            "response_length": 0.5,
            "enthusiasm": 0.4,
            "question_chance": 0.3,
            "emoji_chance": 0.4,
            "wolf_actions": ["*gähnt leicht*", "*reibt sich die Augen*", "*streckt sich* *Schweif senkt sich*"],
            "tone": "ruhig",
            "speed": "normal",
        },
        "normal": {  # 0.4-0.7
            "response_length": 0.7,
            "enthusiasm": 0.6,
            "question_chance": 0.5,
            "emoji_chance": 0.5,
            "wolf_actions": ["*lächelt* *Schweif wippt*", "*Ohren spitzen sich*", "*schaut neugierig*"],
            "tone": "freundlich",
            "speed": "normal",
        },
        "energized": {  # 0.7-0.9
            "response_length": 0.9,
            "enthusiasm": 0.8,
            "question_chance": 0.7,
            "emoji_chance": 0.7,
            "wolf_actions": ["*strahlt* *Schweif wedelt*", "*springt auf*", "*lacht* *Ohren stehen fröhlich*"],
            "tone": "enthusiastisch",
            "speed": "fast",
        },
        "hyper": {  # > 0.9
            "response_length": 1.0,
            "enthusiasm": 1.0,
            "question_chance": 0.8,
            "emoji_chance": 0.8,
            "wolf_actions": ["*hüpft aufgeregt*", "*kann nicht stillsitzen* *Schweif wirbelt*", "*strahlt übers ganze Gesicht*"],
            "tone": "aufgeregt",
            "speed": "very_fast",
        },
    }
    
    # === EMOTION → VERHALTEN ===
    EMOTION_BEHAVIORS = {
        "freude": {
            "tone_modifier": "warm und fröhlich",
            "wolf_style": "verspielt",
            "emoji_preference": ["😊", "✨", "🐺"],
            "curiosity_boost": 0.1,
        },
        "traurigkeit": {
            "tone_modifier": "sanft und mitfühlend",
            "wolf_style": "ruhig",
            "emoji_preference": ["💙", "🥺"],
            "response_length_modifier": -0.2,
        },
        "neugier": {
            "tone_modifier": "interessiert und fragend",
            "wolf_style": "aufmerksam",
            "emoji_preference": ["🤔", "👀", "✨"],
            "question_boost": 0.3,
        },
        "zuneigung": {
            "tone_modifier": "warmherzig und liebevoll",
            "wolf_style": "kuschelnd",
            "emoji_preference": ["💙", "🥰", "❤️"],
            "personal_boost": 0.2,
        },
        "verspielt": {
            "tone_modifier": "neckend und lustig",
            "wolf_style": "schelmisch",
            "emoji_preference": ["😏", "😜", "🐺"],
            "humor_boost": 0.3,
        },
        "nachdenklich": {
            "tone_modifier": "tiefgründig und weise",
            "wolf_style": "ruhig",
            "emoji_preference": ["🤔", "💭"],
            "philosophical_boost": 0.4,
        },
    }
    
    # === COGNITIVE → VERHALTEN ===
    COGNITIVE_BEHAVIORS = {
        "analytical": {
            "structure": "logisch",
            "detail_level": "hoch",
            "example_usage": True,
        },
        "creative": {
            "structure": "assoziativ",
            "metaphor_usage": True,
            "playfulness": "hoch",
        },
        "philosophical": {
            "structure": "reflektiv",
            "depth": "tief",
            "question_style": "existenziell",
        },
        "learning": {
            "enthusiasm": "hoch",
            "share_tendency": True,
            "curiosity_visible": True,
        },
    }
    
    @classmethod
    def get_behavior_for_state(cls, 
                               energy: float,
                               emotion: str,
                               cognitive_mode: str = None) -> Dict:
        """
        Hole Verhaltensmodifikatoren für aktuellen Zustand.
        
        Args:
            energy: Energie-Level 0-1
            emotion: Primäre Emotion
            cognitive_mode: Optionaler kognitiver Modus
            
        Returns:
            Dict mit allen Modifikatoren
        """
        result = {}
        
        # Energie-basiert
        if energy < 0.2:
            result.update(cls.ENERGY_BEHAVIORS["exhausted"])
        elif energy < 0.4:
            result.update(cls.ENERGY_BEHAVIORS["tired"])
        elif energy < 0.7:
            result.update(cls.ENERGY_BEHAVIORS["normal"])
        elif energy < 0.9:
            result.update(cls.ENERGY_BEHAVIORS["energized"])
        else:
            result.update(cls.ENERGY_BEHAVIORS["hyper"])
        
        # Emotion-basiert
        if emotion in cls.EMOTION_BEHAVIORS:
            emotion_mods = cls.EMOTION_BEHAVIORS[emotion]
            result["tone_modifier"] = emotion_mods.get("tone_modifier", "")
            result["wolf_style"] = emotion_mods.get("wolf_style", "")
            result["emoji_preference"] = emotion_mods.get("emoji_preference", [])
            
            # Modifikatoren anwenden
            for key in ["curiosity_boost", "question_boost", "personal_boost", 
                       "humor_boost", "philosophical_boost"]:
                if key in emotion_mods:
                    result[key] = emotion_mods[key]
            
            if "response_length_modifier" in emotion_mods:
                result["response_length"] += emotion_mods["response_length_modifier"]
        
        # Cognitive-basiert
        if cognitive_mode and cognitive_mode in cls.COGNITIVE_BEHAVIORS:
            result["cognitive"] = cls.COGNITIVE_BEHAVIORS[cognitive_mode]
        
        return result


# =============================================================================
# INTEGRATION FUNCTIONS
# =============================================================================

def create_full_wiring(brain) -> HoloWiringEngine:
    """
    Erstelle vollständiges Wiring für einen HoloBrain.
    
    Args:
        brain: HoloBrain Instanz
        
    Returns:
        Konfigurierte WiringEngine
    """
    engine = HoloWiringEngine()
    
    # Module registrieren
    engine.register_modules_from_brain(brain)
    
    # Wiring durchführen
    success = engine.wire_all()
    
    if success:
        logger.info("[Wiring] Vollständige Integration erfolgreich")
    else:
        logger.warning("[Wiring] Integration mit Problemen abgeschlossen")
    
    return engine


def integrate_new_modules(brain, 
                         router=None,
                         impulse_generator=None,
                         context_compressor=None,
                         nlp_algorithms=None) -> bool:
    """
    Integriere die neuen Module in einen bestehenden HoloBrain.
    
    Args:
        brain: HoloBrain Instanz
        router: HoloIntelligentRouter
        impulse_generator: HoloImpulseGenerator
        context_compressor: ContextCompressor
        nlp_algorithms: NLP Modul
        
    Returns:
        True wenn erfolgreich
    """
    try:
        # Router integrieren
        if router:
            brain.router = router
            
            # Router mit allen Modulen verbinden
            router.connect_modules(
                energy_system=getattr(brain, 'energy', None),
                emotions=getattr(brain, 'emotions', None),
                cognitive=getattr(brain, 'cognitive', None),
                autonomous_life=getattr(brain, 'autonomous_life', None),
                memory=getattr(brain, 'memory', None),
                consciousness=getattr(brain, 'consciousness', None),
                self_awareness=getattr(brain, 'self_awareness', None),
                personality=getattr(brain, 'personality', None),
                interface=getattr(brain, 'interface', None),
                impulse_generator=impulse_generator,
                context_compressor=context_compressor,
            )
            
            logger.info("[Integration] Router verbunden")
        
        # Impulse Generator integrieren
        if impulse_generator:
            brain.impulse_generator = impulse_generator
            
            # Verbindungen
            impulse_generator.energy = getattr(brain, 'energy', None)
            impulse_generator.autonomous_life = getattr(brain, 'autonomous_life', None)
            impulse_generator.personality = getattr(brain, 'personality', None)
            impulse_generator.events = getattr(brain, 'events', None)
            
            logger.info("[Integration] ImpulseGenerator verbunden")
        
        # Context Compressor integrieren
        if context_compressor:
            brain.context_compressor = context_compressor
            logger.info("[Integration] ContextCompressor verbunden")
        
        # NLP integrieren
        if nlp_algorithms:
            brain.nlp_algorithms = nlp_algorithms
            logger.info("[Integration] NLP Algorithms verbunden")
        
        return True
        
    except Exception as e:
        logger.error(f"[Integration] Fehler: {e}")
        return False


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🐺 HOLO WIRING v15.0 - TEST")
    print("=" * 70)
    
    # Test Wiring Engine
    engine = HoloWiringEngine()
    
    print(f"\n📊 Verbindungen definiert: {len(MODULE_CONNECTIONS)}")
    print(f"📊 Callbacks definiert: {len(CALLBACK_DEFINITIONS)}")
    
    # Gruppiere nach Ziel
    targets = {}
    for conn in MODULE_CONNECTIONS:
        if conn.target not in targets:
            targets[conn.target] = []
        targets[conn.target].append(conn.source)
    
    print("\n🔗 TOP VERBINDUNGS-ZIELE:")
    sorted_targets = sorted(targets.items(), key=lambda x: len(x[1]), reverse=True)
    for target, sources in sorted_targets[:10]:
        print(f"   {target}: {len(sources)} eingehend ({', '.join(sources[:3])}...)")
    
    # Test State Dependent Behavior
    print("\n\n🎭 ZUSTANDSABHÄNGIGES VERHALTEN:")
    for energy in [0.1, 0.5, 0.9]:
        behavior = StateDependentBehavior.get_behavior_for_state(energy, "freude")
        print(f"\n   Energie {energy:.0%}:")
        print(f"   → Ton: {behavior.get('tone', 'normal')}")
        print(f"   → Länge: {behavior.get('response_length', 0.5):.0%}")
        print(f"   → Wolf: {behavior.get('wolf_actions', ['?'])[0]}")
    
    print("\n\n✅ Wiring bereit für Integration!")


# =============================================================================
# HOLO_BRAIN KOMPATIBILITÄTS-FUNKTIONEN
# =============================================================================

def wire_holo_brain(brain) -> Dict[str, Any]:
    """
    Verbinde alle Module eines HoloBrain.

    Diese Funktion wird von holo_brain.py erwartet und nutzt
    intern die HoloWiringEngine.

    Args:
        brain: HoloBrain Instanz

    Returns:
        Dict mit Ergebnis-Statistiken:
        - connections_made: Anzahl erfolgreicher Verbindungen
        - callbacks_set: Anzahl gesetzter Callbacks
        - failed: Anzahl fehlgeschlagener Verbindungen
    """
    engine = HoloWiringEngine()

    # Module aus Brain registrieren
    engine.register_modules_from_brain(brain)

    # Wiring durchführen
    engine.wire_all()

    # Stats zurückgeben
    return {
        "connections_made": engine.stats.get("connections_made", 0),
        "callbacks_set": engine.stats.get("callbacks_registered", 0),
        "failed": engine.stats.get("connections_failed", 0),
        "engine": engine
    }


def check_connections(brain, engine: Optional[HoloWiringEngine] = None) -> Dict[str, Any]:
    """
    Überprüfe den Verbindungsstatus aller Module.

    Args:
        brain: HoloBrain Instanz
        engine: Optional - existierende WiringEngine

    Returns:
        Dict mit Verbindungs-Status:
        - total: Gesamtanzahl Verbindungen
        - connected: Anzahl verbundener Module
        - missing: Liste fehlender Verbindungen
        - health: Gesundheitswert 0.0-1.0
    """
    if engine is None:
        engine = HoloWiringEngine()
        engine.register_modules_from_brain(brain)

    total = len(MODULE_CONNECTIONS)
    connected = 0
    missing = []

    for conn in MODULE_CONNECTIONS:
        source_module = engine.modules.get(conn.source)
        target_module = engine.modules.get(conn.target)

        if source_module is None or target_module is None:
            missing.append(f"{conn.source} -> {conn.target}")
            continue

        # Prüfe ob Verbindung existiert
        if hasattr(target_module, conn.attribute):
            attr = getattr(target_module, conn.attribute, None)
            if attr is not None:
                connected += 1
            else:
                missing.append(f"{conn.source} -> {conn.target}.{conn.attribute}")
        else:
            missing.append(f"{conn.target} hat kein {conn.attribute}")

    health = connected / total if total > 0 else 1.0

    return {
        "total": total,
        "connected": connected,
        "missing": missing[:10],  # Max 10 für Übersichtlichkeit
        "health": health
    }
