"""
HOLO BRAIN - ROBUSTE IMPORTS v4.0 (CORE TYPES UPDATE)
======================================================
Importiere das am Anfang von holo_brain.py:
    from holo_robust_imports import *

ÄNDERUNGEN v4.0:
- Importiert aus holo_core_types (bricht zirkuläre Imports!)
- Re-exportiert alle Core Types
- SmartUnderstanding für Intent + Typo-Korrektur
- UnifiedLLM v15 für 3-Tier Routing
- Bessere Fallbacks

Enthält:
- Alle Standard-Imports
- Core Types (DriveType, GoalType, ThoughtType, etc.)
- Robuste Modul-Imports mit Fallbacks
- load_all_modules() Funktion
- SafeModule Wrapper
- safe_call() Funktion
- Alle Fallback-Klassen
"""

# =============================================================================
# CORE TYPES IMPORT - Zuerst! (bricht zirkuläre Imports)
# =============================================================================
try:
    from holo_core_types import (
        # Skalen
        MoodScale, EnergyScale,
        # Enums
        DriveType, NeedType, GoalType, ThoughtType, ActivityType,
        InterestLevel, CommandType, CommandPriority, MessageType,
        IntentType, RouteType, EmotionType, GoalPriority,
        # Dataclasses
        Opinion, EmotionalState, TrackedTopic, InnerThought,
        DriveState, NeedState, Goal,
        # Helpers
        clamp, validate_mood, validate_energy,
    )
    CORE_TYPES_AVAILABLE = True
    logger_init = "✅ holo_core_types geladen"
except ImportError:
    CORE_TYPES_AVAILABLE = False
    logger_init = "⚠️ holo_core_types nicht gefunden - Fallbacks aktiv"

# =============================================================================
# STANDARD IMPORTS
# =============================================================================
import os
import sys
import json
import time
import random
import asyncio
import logging
import threading
import hashlib
import re
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Generator, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import socket
import struct
from difflib import SequenceMatcher
import uuid

# Web/HTTP
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False

# Flask (optional)
try:
    from flask import Flask, request, jsonify, Response, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("HoloBrain")

# Log core types status
logger.info(logger_init)


# =============================================================================
# KERNDATEIEN IMPORTS (Konsolidiert v2.0)
# =============================================================================
# Die 4 Hauptmodule die alle anderen ersetzt haben

# --- CONSCIOUSNESS ---
CONSCIOUSNESS_AVAILABLE = False
OrganicSpontaneousThought = None
SpontaneousThoughtSystem = None
OrganicDream = None
DreamSystem = None
MemoryEmotionSystem = None
OrganicPresenceConfig = None

try:
    from holo_consciousness import (
        HoloConsciousness,
        create_consciousness,
        get_system_prompt_extension,
        SelfReflection,
        InnerMonologue,
        PhilosophicalMind,
        OpinionFormation,
        DaydreamEngine,
        SpontaneousThoughts,
        VirtueEthics,
        Conscience,
        MoralReasoning,
        ConsciousnessConfig,
        ThoughtType,
    )
    CONSCIOUSNESS_AVAILABLE = True
    logger.info("[RobustImports] ✓ holo_consciousness (Basis)")

    # Organic Presence Klassen (optional)
    try:
        from holo_consciousness import (
            OrganicPresenceConfig,
            ConsciousnessEmotionalMemory,  # War: EmotionalMemory
            MemoryEmotionSystem,
            OrganicDream,
            DreamSystem,
            OrganicSpontaneousThought,
            SpontaneousThoughtSystem,
        )
        logger.info("[RobustImports] ✓ holo_consciousness (+ Organic Presence)")
    except ImportError as e:
        logger.warning(f"[RobustImports] Organic Presence Klassen nicht verfügbar: {e}")

except ImportError as e:
    logger.warning(f"[RobustImports] holo_consciousness: {e}")

# --- INNER LIFE ---
INNER_LIFE_AVAILABLE = False
try:
    from holo_inner_life import (
        HoloInnerLife,
        HoloAutonomousLife,
        create_autonomous_life,
        # Triebe & Langeweile
        DriveSystem,
        DriveType as InnerDriveType,
        BoredomSystem,
        MessageQueue,
        AutonomousConfig,
        # Stimmung
        MoodEvolution,
        MoodType,
        # Interessen
        CuriositySystem,
        CuriosityQuest,
        OpinionSystem,
        Opinion as InnerOpinion,
        RelationshipTracker,
        CreativeImpulses,
        CreativeWork,
        # Projekte
        ProjectManager,
        HoloProject,
        SoloActivities,
        InitiativeCoordinator,
        # Autonomie Engine
        AutonomousActivityEngine,
        AutonomousActivityManager,
        # Context
        EmotionalContextTracker,
    )
    INNER_LIFE_AVAILABLE = True
    CURIOSITY_SYSTEM_AVAILABLE = True
    logger.info("[RobustImports] ✓ holo_inner_life (konsolidiert)")
except ImportError as e:
    logger.warning(f"[RobustImports] holo_inner_life: {e}")
    CURIOSITY_SYSTEM_AVAILABLE = False

# --- CONTEXT MIND ---
CONTEXT_MIND_AVAILABLE = False
try:
    from holo_context_mind import (
        HoloContextMind,
        create_context_mind,
        ContextEntry,
        ContextType,
        TopicTracker,
        TrackedTopic as ContextTrackedTopic,
        ConversationContext,
        ChatContextTracker,
        SelfReflectionEngine,
        EnhancedOrganicSystem,
    )
    CONTEXT_MIND_AVAILABLE = True
    logger.info("[RobustImports] ✓ holo_context_mind (konsolidiert)")
except ImportError as e:
    logger.warning(f"[RobustImports] holo_context_mind: {e}")

# --- PERSONALITY ---
PERSONALITY_AVAILABLE = False
try:
    from holo_personality import (
        HoloPersonalityEngine,
        HoloPolicies,
        create_personality,
        # Kemonomimi
        KemonomimiBodyLanguage,
        KemonomimiExpression,
        KemonomimiMessageEnhancer,
        EmotionLevels,
        get_kemonomimi_prompt,
        WeatherTranslator,
        AnticipationEngine,
        # Konstanten
        HOLO_KEMONOMIMI_COMPACT,
        HOLO_KEMONOMIMI_DEFINITION,
        HOLO_PERSONALITY,
        # Organic Presence (integriert)
        TypingCharacter,
        TypingSimulator,
        IdleMessage,
        IdlePresenceSystem,
        ResponseModification,
        EnergyResponseModifier,
        OrganicPresenceManager,
    )
    PERSONALITY_AVAILABLE = True
    KEMONOMIMI_AVAILABLE = True
    # Backwards Compatibility
    WolfBodyLanguage = KemonomimiBodyLanguage
    logger.info("[RobustImports] ✓ holo_personality (konsolidiert)")
except ImportError as e:
    logger.warning(f"[RobustImports] holo_personality: {e}")
    KEMONOMIMI_AVAILABLE = False


def get_core_modules_status() -> Dict[str, bool]:
    """Status aller 4 Kerndateien"""
    return {
        "consciousness": CONSCIOUSNESS_AVAILABLE,
        "inner_life": INNER_LIFE_AVAILABLE,
        "context_mind": CONTEXT_MIND_AVAILABLE,
        "personality": PERSONALITY_AVAILABLE,
    }


# =============================================================================
# SAFE IMPORT FUNCTION
# =============================================================================

def safe_import(module_name: str, class_name: str = None, fallback=None):
    """
    Importiert ein Modul/Klasse sicher.
    Bei Fehler wird der Fallback zurückgegeben.
    """
    try:
        module = __import__(module_name)
        if class_name:
            return getattr(module, class_name, fallback)
        return module
    except ImportError as e:
        logger.warning(f"⚠️ Could not import {module_name}: {e}")
        return fallback
    except Exception as e:
        logger.error(f"❌ Error importing {module_name}: {e}")
        return fallback


def safe_call(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Ruft eine Funktion sicher auf.
    Bei Fehler wird default zurückgegeben.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Safe call failed for {getattr(func, '__name__', 'unknown')}: {e}")
        return default


# =============================================================================
# SAFE MODULE WRAPPER
# =============================================================================

class SafeModule:
    """Wrapper der alle Methoden eines Moduls sicher macht."""

    def __init__(self, module: Any, default_return: Any = None):
        self._module = module
        self._default = default_return

    def __getattr__(self, name: str) -> Callable:
        original = getattr(self._module, name, None)

        if original is None:
            return lambda *a, **kw: self._default

        if callable(original):
            def safe_wrapper(*args, **kwargs):
                try:
                    return original(*args, **kwargs)
                except Exception as e:
                    logger.debug(f"SafeModule: {name}() failed: {e}")
                    return self._default
            return safe_wrapper

        return original


# =============================================================================
# FALLBACK KLASSEN
# =============================================================================

class FallbackSmartLLM:
    """Fallback wenn smart_llm_system.py nicht existiert"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackSmartLLM - limited functionality")
        self.model = kwargs.get('model', 'unknown')
        self.ollama_host = kwargs.get('ollama_host', 'http://localhost:11434')

    def query(self, prompt, **kwargs):
        if REQUESTS_AVAILABLE:
            try:
                response = requests.post(
                    f"{self.ollama_host}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt[:500]}],
                        "stream": False
                    },
                    timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "response": data.get("message", {}).get("content", ""),
                        "source": "direct_ollama"
                    }
            except Exception as e:
                logger.debug(f"Direct ollama failed: {e}")

        return {"response": "Ich kann gerade nicht antworten.", "source": "fallback"}

    def query_stream(self, prompt, **kwargs):
        result = self.query(prompt, **kwargs)
        yield result.get("response", "")

    def get_stats(self):
        return {"status": "fallback_mode"}

    def check_connection(self):
        return {"connected": False, "host": self.ollama_host}


class FallbackUnifiedLLM(FallbackSmartLLM):
    """Fallback für UnifiedLLM v15"""
    pass


class FallbackSmartUnderstanding:
    """Fallback wenn holo_smart_understanding.py nicht existiert"""
    def __init__(self):
        logger.warning("⚠️ Using FallbackSmartUnderstanding")

    def understand(self, text: str) -> Dict:
        return {
            "original": text,
            "normalized": text.lower(),
            "keywords": text.lower().split(),
            "intent": None,
            "confidence": 0.0,
            "matches": [],
            "suggested_route": "local"
        }

    def correct_typos(self, text: str) -> Tuple[str, List]:
        return text, []


class FallbackHoloNLP:
    """Fallback wenn holo_nlp_algorithms.py nicht existiert"""
    def __init__(self):
        logger.warning("⚠️ Using FallbackHoloNLP - limited NLP functionality")

    def analyze(self, text: str) -> Dict:
        words = text.lower().split()
        return {
            "text": text,
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "entities": [],
            "intent": None,
            "intent_confidence": 0.0,
            "needs_llm": True,
            "processing_time_ms": 0.0
        }

    def needs_llm(self, text: str) -> Tuple[bool, str, float]:
        """Fallback: Immer LLM nutzen"""
        return True, "unknown", 0.0


class FallbackTextReader:
    """Fallback wenn holo_text_reader.py nicht existiert"""
    def __init__(self, nlp=None, web_curiosity=None):
        logger.warning("⚠️ Using FallbackTextReader - limited text analysis")

    def read(self, text: str, source: str = "", title: str = "") -> Dict:
        sentences = text.split('. ')
        return {
            "source": source,
            "title": title,
            "word_count": len(text.split()),
            "sentence_count": len(sentences),
            "main_topics": [],
            "entities": [],
            "facts": [],
            "keywords": text.lower().split()[:10],
            "summary": text[:200] + "..." if len(text) > 200 else text,
            "key_sentences": sentences[:3],
            "needs_llm_for_deep_analysis": True
        }

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        sentences = text.split('. ')
        return '. '.join(sentences[:max_sentences])

    def extract_keywords(self, text: str, n: int = 10) -> List[str]:
        return text.lower().split()[:n]


class FallbackPiControlBridge:
    """Fallback wenn pi_holo_interface.py nicht existiert"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackPiControlBridge")
        self.connected = False
        self.api_url = kwargs.get('api_url', 'http://localhost:8000')

    def get_status(self):
        return {"_heartbeat_ok": False, "error": "Bridge not available"}

    def execute(self, command):
        return {"success": False, "error": "Bridge not available"}

    @property
    def nas_status(self):
        return {"online": False}

    @property
    def nas_online(self):
        return False

    @property
    def system_metrics(self):
        return {}

    @property
    def weather(self):
        return {}


class FallbackEnergySystem:
    """Fallback wenn holo_energy_system.py nicht existiert"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackEnergySystem")
        self._energy = 0.75

    def get_status(self):
        return {
            "total_energy": self._energy,
            "current_state": "normal",
            "components": {}
        }

    def update(self, context=None):
        pass

    def consume(self, activity_type, amount=0.01):
        self._energy = max(0, self._energy - amount)

    def regenerate(self, amount=0.02):
        self._energy = min(1, self._energy + amount)

    def get_energy_modifier(self):
        return {"energy_level": self._energy, "modifiers": []}


class FallbackPersonalityEngine:
    """Fallback wenn holo_personality.py nicht existiert"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackPersonalityEngine")

    def get_personality_context(self):
        return "Du bist Holo, eine freundliche und weise Wölfin."

    def get_current_quirks(self):
        return []

    def get_greeting(self):
        return "Hallo! 🐺"

    def get_farewell(self):
        return "Bis bald! 👋🐺"

    def update(self, context=None):
        pass


class FallbackLearningProtocol:
    """Fallback wenn HoloLearningSystem nicht verfügbar"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackLearningProtocol")

    def should_learn(self):
        return False

    def learn(self):
        return None

    def get_learning_summary(self):
        return "Lernsystem nicht verfügbar."


class FallbackCognitiveCore:
    """Fallback für CognitiveIntegrationCore"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackCognitiveCore")
        self.safety = FallbackSafetyCore()

    def process_and_integrate(self, message):
        return FallbackIntegratedContext()

    def connect_systems(self, **kwargs):
        pass


class FallbackIntegratedContext:
    """Fallback für IntegratedContext"""
    def to_full_prompt(self):
        return ""


class FallbackSafetyCore:
    """Fallback für LoyaltySafetyCore"""
    def __init__(self):
        pass

    def receive_master_command(self, message):
        return {"compliant": True}

    def filter_response(self, response):
        return response


class FallbackConsciousness:
    """Fallback für HoloConsciousness"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackConsciousness")

    def get_inner_state(self):
        return {"awareness": 0.5, "thoughts": []}

    def reflect(self, topic):
        return f"Ich denke über {topic} nach..."

    def get_prompt_section(self):
        return ""

    def process_interaction(self, user_message, context=None):
        return {}

    def get_prompt_additions(self, context=None):
        return ""

    def evaluate_ethically(self, situation, **kwargs):
        return {"recommendation": "neutral"}

    def generate_inner_thought(self):
        return None


class FallbackInnerLife:
    """Fallback für HoloInnerLife"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackInnerLife")

    def update(self, **kwargs):
        return {}

    def get_status(self):
        return {"mood": "neutral", "phase": "unknown"}

    def simulate_time(self, minutes):
        pass


class FallbackAutonomousLife:
    """Fallback für HoloAutonomousLife"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackAutonomousLife")

    def update(self, **kwargs):
        return {}

    def get_motivation(self):
        return "Ich bin hier."

    def check_for_proactive_message(self):
        return None

    def simulate_time_alone(self, minutes):
        pass


class FallbackContextMind:
    """Fallback für HoloContextMind"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackContextMind")
        self.entries = []

    def add_message(self, role, content, **kwargs):
        self.entries.append({"role": role, "content": content})

    def get_context_for_response(self, query=None):
        return {}

    def get_summary(self):
        return ""


class FallbackInnerVoice:
    """Fallback für InnerVoice"""
    def generate_thought(self):
        return None


class FallbackAuthenticityEngine:
    """Fallback für AuthenticityEngine"""
    def check_authenticity(self, response):
        return {"authentic": True, "score": 1.0}


class FallbackContextManager:
    """Fallback für SmartContextManager"""
    def __init__(self):
        self.messages = []

    def add_exchange(self, user_msg, assistant_msg):
        self.messages.append({"role": "user", "content": user_msg})
        self.messages.append({"role": "assistant", "content": assistant_msg})

    def get_context_for_llm(self):
        return "", self.messages[-10:]  # Letzte 10

    def get_full_context(self):
        return self.get_context_for_llm()

    def get_stats(self):
        return {"messages": len(self.messages)}


class FallbackPreferences:
    """Fallback für HoloPreferences/HoloPersonalitySystem"""
    def __init__(self, *args, **kwargs):
        logger.warning("⚠️ Using FallbackPreferences")

    def get_personality_for_prompt(self):
        return ""

    def check_for_quirk(self, message):
        return None

    def update_from_interaction(self, message, response):
        pass


class FallbackIntentDetector:
    """Fallback für IntentDetector - nutzt SmartUnderstanding wenn verfügbar"""
    def __init__(self):
        try:
            from holo_smart_understanding import SmartUnderstanding
            self._understanding = SmartUnderstanding()
            self._use_new = True
            logger.info("✅ IntentDetector using SmartUnderstanding")
        except ImportError:
            self._use_new = False
            logger.warning("⚠️ Using basic FallbackIntentDetector")

    def detect_intent(self, text: str) -> Dict:
        if self._use_new:
            result = self._understanding.understand(text)
            return {
                "intent": result.get("intent") or "unknown",
                "confidence": result.get("confidence", 0.5),
                "requires_llm": result.get("suggested_route") not in ["personality", "pattern"],
                "route": result.get("suggested_route", "local"),
                "typo_corrections": result.get("typo_corrections", [])
            }
        else:
            # Einfache Fallback-Logik
            text_lower = text.lower().strip()

            if any(g in text_lower for g in ["hallo", "hi", "hey", "moin", "guten"]):
                return {"intent": "greeting", "confidence": 0.9, "requires_llm": False}
            elif any(g in text_lower for g in ["tschüss", "bye", "ciao", "nacht"]):
                return {"intent": "farewell", "confidence": 0.9, "requires_llm": False}
            elif any(g in text_lower for g in ["danke", "thanks", "thx"]):
                return {"intent": "gratitude", "confidence": 0.9, "requires_llm": False}
            elif "wie geht" in text_lower or "gehts" in text_lower:
                return {"intent": "emotion", "confidence": 0.9, "requires_llm": False}

            return {"intent": "unknown", "confidence": 0.5, "requires_llm": True}

    def detect_user_mood(self, text: str) -> Dict:
        text_lower = text.lower()
        valence = 0.5

        positive = ["gut", "super", "toll", "freue", "glücklich", "schön", "liebe", "danke"]
        negative = ["schlecht", "müde", "traurig", "stress", "problem", "mist", "scheiße"]

        for word in positive:
            if word in text_lower:
                valence += 0.1
        for word in negative:
            if word in text_lower:
                valence -= 0.1

        return {"valence": max(0, min(1, valence)), "arousal": 0.5}


class FallbackResponseGenerator:
    """Fallback für ResponseGenerator"""
    def __init__(self, emotions=None):
        self.emotions = emotions

    def generate_greeting_response(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return random.choice(["Guten Morgen! 🌅", "Morgen! ☀️", "Hey, früher Vogel! 🐺"])
        elif 12 <= hour < 18:
            return random.choice(["Hey! 👋", "Hallo! 🐺", "Na du! 😊"])
        elif 18 <= hour < 22:
            return random.choice(["Guten Abend! 🌙", "Hey! 🐺", "Nabend! ✨"])
        else:
            return random.choice(["Hey Nachteule! 🦉", "Oh, noch wach? 🌙", "Na du! 🐺"])

    def generate_farewell_response(self):
        hour = datetime.now().hour
        if 22 <= hour or hour < 5:
            return random.choice(["Gute Nacht! Schlaf gut! 🌙", "Träum was Schönes! 💤🐺"])
        else:
            return random.choice(["Bis bald! 👋🐺", "Mach's gut! 😊", "Ciao! 🐺"])

    def generate_gratitude_response(self):
        return random.choice([
            "Gerne! 😊🐺",
            "Kein Ding!",
            "Immer doch! 🐺",
            "Freut mich wenn ich helfen konnte!"
        ])

    def generate_feelings_response(self):
        moods = ["gut", "ganz okay", "super", "ein bisschen müde aber okay"]
        return random.choice([
            f"Mir geht's {random.choice(moods)}! Und dir? 🐺",
            f"Ach, {random.choice(moods)}. Was macht du so?",
            "Prima soweit! Danke der Nachfrage! 😊🐺"
        ])


class FallbackMoodContagion:
    """Fallback für MoodContagion"""
    def __init__(self):
        pass

    def apply(self, user_mood, target_emotions):
        pass


class FallbackNaturalLanguageHelper:
    """Fallback für NaturalLanguageHelper"""
    def parse_command(self, text):
        return {"command": None, "confidence": 0}


# =============================================================================
# MODUL-IMPORTS MIT FALLBACKS
# =============================================================================

# ============================================================================
# SMART UNDERSTANDING (NEU v3.0!)
# ============================================================================
SmartUnderstanding = safe_import('holo_smart_understanding', 'SmartUnderstanding', FallbackSmartUnderstanding)
TextNormalizer = safe_import('holo_smart_understanding', 'TextNormalizer', None)
FuzzyMatcher = safe_import('holo_smart_understanding', 'FuzzyMatcher', None)
KeywordDetector = safe_import('holo_smart_understanding', 'KeywordDetector', None)

# ============================================================================
# UNIFIED LLM v15 (NEU v3.0!)
# ============================================================================
# Versuche erst v15, dann Fallback auf altes System
UnifiedLLM = safe_import('smart_llm_system', 'UnifiedLLM', None)
PatternCache = safe_import('smart_llm_system', 'PatternCache', None)

if UnifiedLLM is None:
    # Fallback auf altes System
    SmartLearningLLM = safe_import('smart_llm_system', 'SmartLearningLLM', FallbackSmartLLM)
else:
    # Nutze UnifiedLLM, aber behalte Alias für Kompatibilität
    SmartLearningLLM = UnifiedLLM
    logger.info("✅ UnifiedLLM v15 geladen")

# ============================================================================
# PI CONTROL BRIDGE
# ============================================================================
PiControlBridge = safe_import('pi_holo_interface', 'PiControlBridge', FallbackPiControlBridge)
NaturalLanguageHelper = safe_import('pi_holo_interface', 'NaturalLanguageHelper', FallbackNaturalLanguageHelper)
HoloInterface = safe_import('pi_holo_interface', 'HoloInterface', None)
DecisionEngine = safe_import('pi_holo_interface', 'DecisionEngine', None)

# ============================================================================
# ENERGY SYSTEM
# ============================================================================
HoloEnergySystem = safe_import('holo_energy_system', 'HoloEnergySystem', FallbackEnergySystem)
EnergyEvent = safe_import('holo_energy_system', 'EnergyEvent', None)
ActivityType = safe_import('holo_energy_system', 'ActivityType', None)

# ============================================================================
# PERSONALITY ENGINE
# ============================================================================
HoloPersonalityEngine = safe_import('holo_personality', 'HoloPersonalityEngine', FallbackPersonalityEngine)
InnerVoice = safe_import('holo_personality', 'InnerVoice', FallbackInnerVoice)
AuthenticityEngine = safe_import('holo_personality', 'AuthenticityEngine', FallbackAuthenticityEngine)

# ============================================================================
# LEARNING
# ============================================================================
HoloLearningSystem = safe_import('holo_learning', 'HoloLearningSystem', FallbackLearningProtocol)
MoodContagion = safe_import('holo_learning', 'MoodContagion', FallbackMoodContagion)
EmotionalMemoryStore = safe_import('holo_learning', 'EmotionalMemoryStore', None)
LearningSession = safe_import('holo_learning', 'LearningSession', None)
EmotionalMemory = None  # holo_memory_system existiert nicht mehr
CuriosityTopic = safe_import('holo_learning', 'CuriosityTopic', None)

# ============================================================================
# COGNITIVE INTEGRATION
# ============================================================================
CognitiveIntegrationCore = safe_import('holo_cognitive_integration', 'CognitiveIntegrationCore', FallbackCognitiveCore)
CausalEngine = safe_import('holo_cognitive_integration', 'CausalEngine', None)
SelfUnderstandingEngine = safe_import('holo_cognitive_integration', 'SelfUnderstandingEngine', None)
IntegratedContext = safe_import('holo_cognitive_integration', 'IntegratedContext', FallbackIntegratedContext)

# Alte Referenz für Kompatibilität
CognitiveIntegration = CognitiveIntegrationCore

# ============================================================================
# COGNITIVE MODULES
# ============================================================================
LoyaltySafetyCore = safe_import('holo_cognitive_modules', 'LoyaltySafetyCore', FallbackSafetyCore)
ConsciousnessEngine = safe_import('holo_cognitive_modules', 'ConsciousnessEngine', None)
ReasoningEngine = safe_import('holo_cognitive_modules', 'ReasoningEngine', None)
PerceptionEngine = safe_import('holo_cognitive_modules', 'PerceptionEngine', None)
AdvancedLearningEngine = safe_import('holo_cognitive_modules', 'AdvancedLearningEngine', None)
PerceptionLayer = safe_import('holo_cognitive_modules', 'PerceptionLayer', None)

# ============================================================================
# ORGANIC (KONSOLIDIERT - Intent Detection in holo_context_mind.py)
# ============================================================================
# IntentDetector jetzt aus context_mind
if CONTEXT_MIND_AVAILABLE:
    IntentDetector = safe_import('holo_context_mind', 'IntentDetector', FallbackIntentDetector)
    ResponseGenerator = FallbackResponseGenerator  # Nicht mehr in organic
else:
    IntentDetector = FallbackIntentDetector
    ResponseGenerator = FallbackResponseGenerator
ResponseHints = None
# ConversationContext bereits oben aus context_mind importiert
CallbackSystem = safe_import('holo_context_mind', 'CallbackSystem', None) if CONTEXT_MIND_AVAILABLE else None

# ============================================================================
# CONSCIOUSNESS SYSTEM (KONSOLIDIERT in holo_consciousness.py)
# ============================================================================
# Bereits oben importiert via KERNDATEIEN IMPORTS
# Definiere Fallbacks für alle Fälle
UncertaintyExpression = None  # Nicht mehr in consciousness enthalten

if not CONSCIOUSNESS_AVAILABLE:
    HoloConsciousness = FallbackConsciousness
    InnerMonologue = None
    SelfReflection = None
    PhilosophicalMind = None
    OpinionFormation = None

# ============================================================================
# CONTEXT COMPRESSION
# ============================================================================
ContextCompressor = safe_import('holo_context_compression', 'ContextCompressor', None)
SmartContextManager = safe_import('holo_context_compression', 'SmartContextManager', FallbackContextManager)
EntityExtractor = safe_import('holo_context_compression', 'EntityExtractor', None)

# ============================================================================
# MEMORY SYSTEM (holo_memory_system existiert nicht mehr - nutze holo_database_system)
# ============================================================================
HoloMemory = None
ShortTermMemory = None
LongTermMemory = None
MemoryRetriever = None
Episode = None

# ============================================================================
# PREFERENCES
# ============================================================================
HoloPreferences = safe_import('holo_preferences', 'HoloPersonalitySystem', FallbackPreferences)
PreferenceManager = safe_import('holo_preferences', 'PreferenceManager', None)
PersonalityExpression = safe_import('holo_preferences', 'PersonalityExpression', None)
CorePreferences = safe_import('holo_preferences', 'CorePreferences', None)

# ============================================================================
# HOLO TOOLS (Timer, Notizen, Einkaufen, Todos)
# ============================================================================
HoloTools = safe_import('holo_tools', 'HoloTools', None)
WeatherTranslator = safe_import('holo_tools', 'WeatherTranslator', None)
TimerManager = safe_import('holo_tools', 'TimerManager', None)
NotesManager = safe_import('holo_tools', 'NotesManager', None)
ShoppingList = safe_import('holo_tools', 'ShoppingList', None)
TodoManager = safe_import('holo_tools', 'TodoManager', None)
Calculator = safe_import('holo_tools', 'Calculator', None)

# ============================================================================
# AUTONOMES LEBEN (KONSOLIDIERT in holo_inner_life.py)
# ============================================================================
# Bereits oben importiert via KERNDATEIEN IMPORTS
if not INNER_LIFE_AVAILABLE:
    HoloAutonomousLife = FallbackAutonomousLife
    HoloInnerLife = FallbackInnerLife
    DriveSystem = None
    BoredomSystem = None
    DriveType = None
    ActivityType = None
    CuriositySystem = None

# ============================================================================
# WIRING (Zentrale Modul-Verdrahtung)
# ============================================================================
HoloWiringEngine = safe_import('holo_wiring', 'HoloWiringEngine', None)
wire_holo_brain = safe_import('holo_wiring', 'wire_holo_brain', None)
check_connections = safe_import('holo_wiring', 'check_connections', None)
get_wiring_diagram = safe_import('holo_wiring', 'get_wiring_diagram', None)

# ============================================================================
# SELF EXPRESSION (Events, persönliche Antworten, Smart Context)
# ============================================================================
HoloSelfExpression = safe_import('holo_self_expression', 'HoloSelfExpression', None)
HoloEventAwareness = safe_import('holo_self_expression', 'HoloEventAwareness', None)
HoloSelfReport = safe_import('holo_self_expression', 'HoloSelfReport', None)
IntelligentContextManager = safe_import('holo_self_expression', 'IntelligentContextManager', None)
SelfDirectedPrompting = safe_import('holo_self_expression', 'SelfDirectedPrompting', None)

# ============================================================================
# SELF EXPRESSION (Events, persönliche Antworten, Smart Context)
# ============================================================================
HoloSelfExpressionEngine = safe_import('holo_self_expression', 'HoloSelfExpressionEngine', None)
HoloEventStyle = safe_import('holo_self_expression', 'HoloEventStyle', None)
SmartContextSelector = safe_import('holo_self_expression', 'SmartContextSelector', None)
HoloMetaPrompting = safe_import('holo_self_expression', 'HoloMetaPrompting', None)

# ============================================================================
# NLP SYSTEM (NEU v5.1 - Pi-optimiert)
# ============================================================================
HoloNLP = safe_import('holo_nlp_algorithms', 'HoloNLP', None)
LightweightVectorEngine = safe_import('holo_nlp_algorithms', 'LightweightVectorEngine', None)
IntentDatabase = safe_import('holo_nlp_algorithms', 'IntentDatabase', None)
NLPEntityExtractor = safe_import('holo_nlp_algorithms', 'EntityExtractor', None)
GermanSentenceParser = safe_import('holo_nlp_algorithms', 'GermanSentenceParser', None)
AdvancedFuzzyMatcher = safe_import('holo_nlp_algorithms', 'AdvancedFuzzyMatcher', None)
AdvancedSentimentAnalyzer = safe_import('holo_nlp_algorithms', 'AdvancedSentimentAnalyzer', None)

# ============================================================================
# ENTITY DATABASE (NEU - 2000+ Namen, 700+ Entities)
# ============================================================================
get_all_names_with_gender = safe_import('holo_entity_database', 'get_all_names_with_gender', None)
get_all_known_entities = safe_import('holo_entity_database', 'get_all_known_entities', None)
GAMING_CHARACTERS = safe_import('holo_entity_database', 'GAMING_CHARACTERS', {})
ANIME_CHARACTERS = safe_import('holo_entity_database', 'ANIME_CHARACTERS', {})

# ============================================================================
# TEXT READER (NEU - Liest und analysiert Text ohne LLM)
# ============================================================================
HoloTextReader = safe_import('holo_text_reader', 'HoloTextReader', None)
KeywordExtractor = safe_import('holo_text_reader', 'KeywordExtractor', None)
SentenceRanker = safe_import('holo_text_reader', 'SentenceRanker', None)
FactExtractor = safe_import('holo_text_reader', 'FactExtractor', None)
TopicDetector = safe_import('holo_text_reader', 'TopicDetector', None)

# ============================================================================
# WEB CURIOSITY (Kritisches Denken, Fakten-Verifizierung)
# ============================================================================
HoloWebCuriosity = safe_import('holo_web_curiosity', 'HoloWebCuriosity', None)
TrustedSourcesDB = safe_import('holo_web_curiosity', 'TrustedSourcesDB', None)
FactVerificationEngine = safe_import('holo_web_curiosity', 'FactVerificationEngine', None)
WebFactsDB = safe_import('holo_web_curiosity', 'WebFactsDB', None)


# =============================================================================
# LOAD ALL MODULES FUNCTION
# =============================================================================

def load_all_modules() -> Dict[str, Any]:
    """
    Lädt alle Holo-Module robust.

    Returns:
        Dict mit allen geladenen Modulen/Klassen oder Fallbacks
    """
    status_lines = ["=== MODULE STATUS v5.0 ==="]

    # Module-Status sammeln
    modules_check = [
        # Kern-Systeme
        ("SmartUnderstanding", SmartUnderstanding, FallbackSmartUnderstanding),
        ("UnifiedLLM", UnifiedLLM, None),
        ("SmartLearningLLM", SmartLearningLLM, FallbackSmartLLM),

        # NEU: NLP System (Pi-optimiert)
        ("HoloNLP", HoloNLP, FallbackHoloNLP),
        ("HoloTextReader", HoloTextReader, FallbackTextReader),
        ("HoloWebCuriosity", HoloWebCuriosity, None),

        # Kognitive Module
        ("CognitiveIntegrationCore", CognitiveIntegrationCore, FallbackCognitiveCore),
        ("HoloConsciousness", HoloConsciousness, FallbackConsciousness),
        ("IntentDetector", IntentDetector, FallbackIntentDetector),

        # Persönlichkeit & Emotion
        ("HoloPersonalityEngine", HoloPersonalityEngine, FallbackPersonalityEngine),
        ("HoloPreferences", HoloPreferences, FallbackPreferences),

        # Gedächtnis & Lernen
        ("SmartContextManager", SmartContextManager, FallbackContextManager),
        ("HoloLearningSystem", HoloLearningSystem, FallbackLearningProtocol),

        # Energie & Rhythmus
        ("HoloEnergySystem", HoloEnergySystem, FallbackEnergySystem),
        ("HoloAutonomousLife", HoloAutonomousLife, None),

        # Safety
        ("LoyaltySafetyCore", LoyaltySafetyCore, FallbackSafetyCore),

        # Hardware
        ("PiControlBridge", PiControlBridge, FallbackPiControlBridge),

        # Wiring
        ("HoloWiringEngine", HoloWiringEngine, None),
    ]

    for name, actual, fallback in modules_check:
        if actual is None:
            status_lines.append(f"❌ {name}: NOT AVAILABLE")
        elif fallback and (actual == fallback or fallback.__name__ in str(type(actual))):
            status_lines.append(f"🔄 {name}: FALLBACK")
        else:
            status_lines.append(f"✅ {name}: OK")

    status = "\n".join(status_lines)

    return {
        # NEU: Smart Understanding
        'smart_understanding': SmartUnderstanding,
        'text_normalizer': TextNormalizer,
        'fuzzy_matcher': FuzzyMatcher,

        # NEU: Unified LLM
        'unified_llm': UnifiedLLM,
        'pattern_cache': PatternCache,

        # Klassen (nicht Instanzen!)
        'energy_system': HoloEnergySystem,
        'personality_engine': HoloPersonalityEngine,
        'cognitive_core': CognitiveIntegrationCore,
        'smart_llm': SmartLearningLLM,
        'pi_bridge': PiControlBridge,
        'learning': HoloLearningSystem,
        'intent_detector': IntentDetector,
        'response_generator': ResponseGenerator,

        # Consciousness
        'consciousness': HoloConsciousness,

        # Context Compression
        'context_manager': SmartContextManager,

        # Memory System
        'memory': HoloMemory,

        # Cognitive Integration
        'cognitive_integration': CognitiveIntegrationCore,

        # Cognitive Engines
        'loyalty_core': LoyaltySafetyCore,
        'consciousness_engine': ConsciousnessEngine,
        'reasoning_engine': ReasoningEngine,
        'perception_engine': PerceptionEngine,

        # Preferences
        'preferences': HoloPreferences,

        # Autonomes Leben (NEU!)
        'autonomous_life': HoloAutonomousLife,
        'drive_system': DriveSystem,
        'boredom_system': BoredomSystem,

        # Wiring (NEU!)
        'wiring_engine': HoloWiringEngine,
        'wire_brain': wire_holo_brain,
        'check_connections': check_connections,

        # NLP System (NEU v5.1 - Pi-optimiert!)
        'nlp': HoloNLP,
        'vector_engine': LightweightVectorEngine,
        'intent_database': IntentDatabase,
        'entity_extractor': NLPEntityExtractor,
        'sentence_parser': GermanSentenceParser,

        # Text Reader (NEU!)
        'text_reader': HoloTextReader,
        'keyword_extractor': KeywordExtractor,
        'fact_extractor': FactExtractor,
        'topic_detector': TopicDetector,

        # Web Curiosity (NEU!)
        'web_curiosity': HoloWebCuriosity,
        'trusted_sources': TrustedSourcesDB,
        'fact_verification': FactVerificationEngine,
        'web_facts_db': WebFactsDB,

        # Status
        'status': status
    }


# =============================================================================
# PRINT STATUS ON IMPORT
# =============================================================================

def print_module_status():
    """Zeigt welche Module geladen wurden"""
    modules = load_all_modules()
    print(modules['status'])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Standard
    'os', 'sys', 'json', 'time', 'random', 'asyncio', 'logging',
    'threading', 'hashlib', 're', 'sqlite3', 'socket', 'struct',
    'datetime', 'timedelta', 'Path',
    'Dict', 'List', 'Optional', 'Any', 'Tuple', 'Generator', 'Callable',
    'dataclass', 'field', 'asdict',
    'defaultdict', 'deque', 'Enum', 'ABC', 'abstractmethod',
    'SequenceMatcher',
    'logger',

    # KERNDATEIEN FLAGS (NEU!)
    'CONSCIOUSNESS_AVAILABLE',
    'INNER_LIFE_AVAILABLE',
    'CONTEXT_MIND_AVAILABLE',
    'PERSONALITY_AVAILABLE',
    'CURIOSITY_SYSTEM_AVAILABLE',
    'KEMONOMIMI_AVAILABLE',
    'get_core_modules_status',

    # Kerndateien Klassen
    'HoloConsciousness', 'HoloInnerLife', 'HoloAutonomousLife',
    'HoloContextMind', 'HoloPersonalityEngine',
    'FallbackConsciousness', 'FallbackInnerLife', 'FallbackAutonomousLife',
    'FallbackContextMind',

    # HTTP Server
    'BaseHTTPRequestHandler', 'HTTPServer', 'ThreadingHTTPServer',
    'urlparse', 'parse_qs',
    'requests', 'REQUESTS_AVAILABLE',

    # Functions
    'safe_import', 'safe_call', 'load_all_modules', 'print_module_status',

    # Classes
    'SafeModule',

    # NEU: Smart Understanding
    'SmartUnderstanding', 'TextNormalizer', 'FuzzyMatcher', 'KeywordDetector',
    'FallbackSmartUnderstanding',

    # NEU: Unified LLM
    'UnifiedLLM', 'PatternCache', 'FallbackUnifiedLLM',

    # Module Classes (real or fallback)
    'SmartLearningLLM',
    'PiControlBridge', 'NaturalLanguageHelper', 'HoloInterface', 'DecisionEngine',
    'HoloEnergySystem', 'EnergyEvent', 'ActivityType',
    'HoloPersonalityEngine', 'InnerVoice', 'AuthenticityEngine',
    'HoloLearningSystem', 'MoodContagion', 'EmotionalMemoryStore',
    'LearningSession', 'EmotionalMemory', 'CuriosityTopic',

    # Cognitive Integration
    'CognitiveIntegrationCore', 'CognitiveIntegration',
    'CausalEngine', 'SelfUnderstandingEngine', 'IntegratedContext',

    # Cognitive Engines
    'LoyaltySafetyCore', 'ConsciousnessEngine', 'ReasoningEngine',
    'PerceptionEngine', 'AdvancedLearningEngine', 'PerceptionLayer',

    # Organic
    'IntentDetector', 'ResponseGenerator', 'ResponseHints',
    'ConversationContext', 'CallbackSystem',

    # Consciousness System
    'HoloConsciousness', 'InnerMonologue', 'SelfReflection',
    'PhilosophicalMind', 'OpinionFormation', 'UncertaintyExpression',

    # Context Compression
    'ContextCompressor', 'SmartContextManager', 'EntityExtractor',

    # Memory System
    'HoloMemory', 'ShortTermMemory', 'LongTermMemory', 'MemoryRetriever', 'Episode',

    # Preferences
    'HoloPreferences', 'PreferenceManager', 'PersonalityExpression', 'CorePreferences',

    # Holo Tools
    'HoloTools', 'WeatherTranslator', 'TimerManager', 'NotesManager',
    'ShoppingList', 'TodoManager', 'Calculator',

    # Fallbacks
    'FallbackSmartLLM', 'FallbackPiControlBridge', 'FallbackEnergySystem',
    'FallbackPersonalityEngine', 'FallbackLearningProtocol', 'FallbackCognitiveCore',
    'FallbackConsciousness', 'FallbackInnerVoice', 'FallbackAuthenticityEngine',
    'FallbackContextManager', 'FallbackPreferences', 'FallbackSafetyCore',
    'FallbackIntentDetector', 'FallbackResponseGenerator', 'FallbackMoodContagion',
    'FallbackNaturalLanguageHelper', 'FallbackIntegratedContext',
    'FallbackHoloNLP', 'FallbackTextReader',

    # NEU: NLP System (Pi-optimiert)
    'HoloNLP', 'LightweightVectorEngine', 'IntentDatabase',
    'NLPEntityExtractor', 'GermanSentenceParser',
    'AdvancedFuzzyMatcher', 'AdvancedSentimentAnalyzer',

    # NEU: Entity Database
    'get_all_names_with_gender', 'get_all_known_entities',
    'GAMING_CHARACTERS', 'ANIME_CHARACTERS',

    # NEU: Text Reader
    'HoloTextReader', 'KeywordExtractor', 'SentenceRanker',
    'FactExtractor', 'TopicDetector',

    # NEU: Web Curiosity
    'HoloWebCuriosity', 'TrustedSourcesDB',
    'FactVerificationEngine', 'WebFactsDB',
]
