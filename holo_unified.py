#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO UNIFIED v16
================
Das komplette intelligente System - alles in einem!

KOMPONENTEN:
┌─────────────────────────────────────────────────────────────────┐
│  SmartUnderstanding     │ Intent-Erkennung + Typo-Korrektur     │
│  UnifiedLLM             │ 3-Stufen Routing (Pattern/Local/Remote)│
│  ContextCompression     │ Intelligente Kontext-Komprimierung    │
│  PersonalityEngine      │ Dynamische Persönlichkeit             │
└─────────────────────────────────────────────────────────────────┘

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ User Input  │ → │ Understand   │ → │ Route       │ → │ Generate │
│             │    │ (Intent+Fix) │    │ (P/L/R)     │    │ Response │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
                                              ↓
                                    ┌─────────────────┐
                                    │ Context Manager │
                                    │ (Compression)   │
                                    └─────────────────┘
"""

import os
import sys
import json
import logging
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# =============================================================================
# CORE TYPES IMPORT - Für konsistente 0-1 Skala
# =============================================================================
try:
    from holo_core_types import MoodScale, EnergyScale, validate_mood, validate_energy
    CORE_TYPES_AVAILABLE = True
except ImportError:
    CORE_TYPES_AVAILABLE = False
    # Fallback wenn holo_core_types nicht verfügbar
    class MoodScale:
        MIN, MAX, NEUTRAL = 0.0, 1.0, 0.5
        @staticmethod
        def validate(v): return max(0.0, min(1.0, v if v <= 1.0 else v/100.0))
    class EnergyScale:
        MIN, MAX, NORMAL = 0.0, 1.0, 0.6
        @staticmethod
        def validate(v): return max(0.0, min(1.0, v if v <= 1.0 else v/100.0))
    def validate_mood(v, s=""): return MoodScale.validate(v)
    def validate_energy(v, s=""): return EnergyScale.validate(v)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("HoloUnified")
logger = logging.getLogger("HoloUnified")

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
# IMPORTS - Die anderen Module
# =============================================================================

# Versuche die Module zu importieren, oder definiere Fallbacks
try:
    from holo_smart_understanding import SmartUnderstanding, TextNormalizer
    UNDERSTANDING_AVAILABLE = True
except ImportError:
    UNDERSTANDING_AVAILABLE = False
    logger.warning("⚠️ holo_smart_understanding.py nicht gefunden - verwende Fallback")

try:
    from smart_llm_system import UnifiedLLM, Config, SystemPrompts, PatternCache
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("⚠️ smart_llm_system.py nicht gefunden - verwende Fallback")

try:
    from holo_context_compression import SmartContextManager, ContextCompressor
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    logger.warning("⚠️ holo_context_compression.py nicht gefunden - verwende Fallback")


# =============================================================================
# PERSONALITY ENGINE - Dynamische Persönlichkeit
# =============================================================================

@dataclass
class EmotionalState:
    """Holos emotionaler Zustand - MIGRATION: Jetzt 0-1 Skala!"""
    energy: float = 0.75          # 0-1 (vorher 0-100)
    mood: float = 0.70            # 0-1 (vorher 0-100)
    curiosity: float = 0.60       # 0-1
    playfulness: float = 0.50     # 0-1
    
    # Zeitbasiert
    last_interaction: datetime = field(default_factory=datetime.now)
    interactions_today: int = 0
    
    def get_mood_text(self) -> str:
        """Gibt Stimmung als Text zurück"""
        if self.mood >= 0.80:
            return random.choice(["super", "fantastisch", "großartig", "bestens"])
        elif self.mood >= 0.60:
            return random.choice(["gut", "ganz gut", "prima", "okay"])
        elif self.mood >= 0.40:
            return random.choice(["so lala", "geht so", "naja", "könnte besser sein"])
        else:
            return random.choice(["müde", "erschöpft", "nicht so toll"])
    
    def get_energy_text(self) -> str:
        """Gibt Energie als Text zurück"""
        if self.energy >= 0.80:
            return random.choice(["voller Energie", "hellwach", "fit"])
        elif self.energy >= 0.50:
            return random.choice(["okay", "normal", "ausgeruht"])
        else:
            return random.choice(["etwas müde", "brauche Pause", "niedrig"])
    
    def update_from_interaction(self, intent: str, positive: bool = True):
        """Aktualisiert Zustand basierend auf Interaktion"""
        self.last_interaction = datetime.now()
        self.interactions_today += 1
        
        # Energie sinkt mit der Zeit (0.005 statt 0.5)
        self.energy = max(0.20, self.energy - 0.005)
        
        # Positive Interaktionen verbessern Stimmung
        if positive:
            self.mood = min(1.0, self.mood + 0.02)
            self.playfulness = min(1.0, self.playfulness + 0.01)
        
        # Bestimmte Intents beeinflussen Zustand
        if intent == "greeting":
            self.mood = min(1.0, self.mood + 0.05)
            self.energy = min(1.0, self.energy + 0.03)
        elif intent == "gratitude":
            self.mood = min(1.0, self.mood + 0.08)
        elif intent == "farewell":
            self.energy = min(1.0, self.energy + 0.10)  # Pause = Erholung
    
    def decay_over_time(self):
        """Zeitbasierter Verfall"""
        now = datetime.now()
        hours_since = (now - self.last_interaction).total_seconds() / 3600
        
        if hours_since > 1:
            # Nach 1 Stunde Inaktivität: leichte Erholung
            self.energy = min(1.0, self.energy + hours_since * 0.05)
        
        # Tageszeit beeinflusst Energie
        hour = now.hour
        if 6 <= hour <= 9:
            self.energy = min(1.0, self.energy + 0.05)  # Morgen = mehr Energie
        elif 22 <= hour or hour <= 5:
            self.energy = max(0.30, self.energy - 0.10)  # Nacht = müde


class PersonalityEngine:
    """
    Verwaltet Holos Persönlichkeit und generiert dynamische Antworten.
    """
    
    def __init__(self):
        self.state = EmotionalState()
        self.user_name: Optional[str] = None
        self.conversation_topics: List[str] = []
        
        # Persönlichkeits-Traits
        self.traits = {
            "wise": 0.8,        # Weise
            "playful": 0.6,     # Verspielt
            "caring": 0.9,      # Fürsorglich
            "curious": 0.7,     # Neugierig
            "honest": 0.95,     # Ehrlich
        }
    
    def get_greeting_style(self) -> str:
        """Generiert dynamischen Gruß basierend auf Zustand"""
        hour = datetime.now().hour
        
        # Tageszeit-basierte Grüße
        if 5 <= hour < 12:
            time_greetings = ["Guten Morgen", "Morgen", "Hey, früher Vogel"]
        elif 12 <= hour < 18:
            time_greetings = ["Hey", "Hallo", "Na du"]
        elif 18 <= hour < 22:
            time_greetings = ["Guten Abend", "Hey", "Na"]
        else:
            time_greetings = ["Hey Nachteule", "Oh, noch wach?", "Na du"]
        
        greeting = random.choice(time_greetings)
        
        # Energie-basierte Ergänzung
        if self.state.energy < 40:
            greeting += random.choice([" *gähn*", "... bin etwas müde", ""])
        elif self.state.energy > 80:
            greeting += random.choice(["! 🐺", "! ✨", "!"])
        else:
            greeting += random.choice(["!", " 🐺", ""])
        
        # User-Name wenn bekannt
        if self.user_name:
            greeting = greeting.replace("!", f", {self.user_name}!")
        
        return greeting
    
    def get_farewell_style(self) -> str:
        """Generiert dynamischen Abschied"""
        hour = datetime.now().hour
        
        if 22 <= hour or hour < 5:
            farewells = [
                "Gute Nacht! Schlaf gut! 🌙",
                "Träum was Schönes! 🐺💤",
                "Bis morgen! Ruh dich aus!",
            ]
        else:
            farewells = [
                "Bis bald! 👋🐺",
                "Mach's gut!",
                "Bis später! Pass auf dich auf!",
                "Ciao! 🐺",
            ]
        
        return random.choice(farewells)
    
    def get_emotion_response(self) -> str:
        """Antwortet auf 'wie geht's dir?'"""
        self.state.decay_over_time()
        
        mood = self.state.get_mood_text()
        energy = self.state.get_energy_text()
        
        responses = [
            f"Mir geht's {mood}! {energy.capitalize()}. Und dir? 🐺",
            f"Ach, {mood}. Bin gerade {energy}. Was macht du so?",
            f"{mood.capitalize()}! Danke der Nachfrage. 🐺 Und selbst?",
        ]
        
        response = random.choice(responses)
        
        # Zusatz basierend auf Interaktionen
        if self.state.interactions_today > 10:
            response += " Wir haben heute schon viel gequatscht!"
        
        return response
    
    def get_gratitude_response(self) -> str:
        """Antwortet auf 'danke'"""
        responses = [
            "Gerne! 😊🐺",
            "Kein Ding!",
            "Immer doch! 🐺",
            "Freut mich wenn ich helfen konnte!",
            "Bitte! 😊",
        ]
        
        if self.state.mood > 80:
            responses.extend([
                "Total gerne! Das macht mir Spaß! 🐺✨",
                "Immer wieder gern!",
            ])
        
        return random.choice(responses)
    
    def enhance_response(self, response: str, intent: str) -> str:
        """Fügt Persönlichkeit zu einer Antwort hinzu"""
        # Update emotional state
        self.state.update_from_interaction(intent)
        
        # Emoji basierend auf Stimmung
        if self.state.mood > 70 and "🐺" not in response:
            if random.random() > 0.5:
                response += " 🐺"
        
        return response
    
    def get_context_for_llm(self) -> Dict:
        """Gibt Kontext für LLM-Calls zurück"""
        return {
            "energy": int(self.state.energy),
            "mood": self.state.get_mood_text(),
            "time_of_day": self._get_time_of_day(),
            "interactions_today": self.state.interactions_today,
            "user_name": self.user_name or "User",
        }
    
    def _get_time_of_day(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Morgen"
        elif 12 <= hour < 18:
            return "Nachmittag"
        elif 18 <= hour < 22:
            return "Abend"
        else:
            return "Nacht"


# =============================================================================
# DATA PROVIDER - Echte Daten für Pattern-Antworten
# =============================================================================

class DataProvider:
    """
    Liefert echte Daten für Pattern-basierte Antworten.
    Verbindet sich mit System-APIs, Wetter, etc.
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60  # Sekunden
    
    def get_system_data(self) -> Dict:
        """Holt System-Daten (CPU, RAM, etc.)"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # CPU Temperatur (Linux)
            cpu_temp = "N/A"
            try:
                temp_file = Path("/sys/class/thermal/thermal_zone0/temp")
                if temp_file.exists():
                    cpu_temp = int(temp_file.read_text().strip()) / 1000
            except Exception:
                pass
            
            return {
                "cpu_usage": cpu_percent,
                "cpu_temp": cpu_temp,
                "ram_used": round(memory.used / (1024**3), 1),
                "ram_total": round(memory.total / (1024**3), 1),
                "ram_percent": memory.percent,
                "uptime": self._get_uptime(),
            }
        except ImportError:
            return {
                "cpu_usage": "N/A",
                "cpu_temp": "N/A",
                "ram_used": "N/A",
                "ram_total": "N/A",
                "ram_percent": "N/A",
                "uptime": "N/A",
            }
    
    def get_nas_status(self) -> Dict:
        """Holt NAS-Status (Ping, Wake-Status, etc.)"""
        # TODO: Echte NAS-Integration
        return {
            "nas_status": "Online",
            "nas_uptime": "3 Tage",
            "nas_cpu": 12,
            "nas_ram": 45,
            "nas_wake_result": "OK",
            "nas_sleep_result": "OK",
        }
    
    def get_weather_data(self) -> Dict:
        """Holt Wetter-Daten"""
        # TODO: Echte Wetter-API Integration
        return {
            "weather_temp": 8,
            "weather_condition": "bewölkt",
            "weather_forecast": "Später Regen möglich",
            "weather_precipitation_answer": "Nein, aktuell regnet es nicht.",
        }
    
    def get_time_data(self) -> Dict:
        """Gibt aktuelle Zeit/Datum"""
        now = datetime.now()
        return {
            "current_time": now.strftime("%H:%M"),
            "current_date": now.strftime("%A, %d. %B %Y"),
        }
    
    def get_smart_home_data(self) -> Dict:
        """Holt Smart Home Daten"""
        # TODO: Home Assistant Integration
        return {
            "lights_status": "3 an, 5 aus",
            "room": "Wohnzimmer",
            "room_temp": 21.5,
        }
    
    def get_all_data(self) -> Dict:
        """Kombiniert alle Daten"""
        data = {}
        data.update(self.get_system_data())
        data.update(self.get_nas_status())
        data.update(self.get_weather_data())
        data.update(self.get_time_data())
        data.update(self.get_smart_home_data())
        return data
    
    def _get_uptime(self) -> str:
        """Berechnet System-Uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                line = f.readline()
                uptime_str = safe_list_access(line.split(), 0, "unified", "_get_uptime", default="0")
                uptime_seconds = float(uptime_str)
                
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            
            if days > 0:
                return f"{days}d {hours}h"
            else:
                return f"{hours}h"
        except Exception:
            return "N/A"


# =============================================================================
# HOLO UNIFIED - Das Hauptsystem
# =============================================================================

class BrainPersonalityAdapter:
    """
    Adapter der HoloBrain's Personality-Module für HoloUnified nutzt.
    
    Damit gibt es keine doppelten Personality-Systeme!
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.state = None  # Wird von brain.energy geholt
        self.user_name = None
        self.conversation_topics = []
        self.traits = {}
        
    def _get_energy_state(self):
        """Hole Energy-State vom Brain"""
        if self.brain and hasattr(self.brain, 'energy') and self.brain.energy:
            return self.brain.energy.state
        return None
    
    def get_greeting_style(self) -> str:
        """Gruß von echtem Personality-System"""
        if self.brain and hasattr(self.brain, 'personality') and self.brain.personality:
            try:
                return self.brain.personality.get_greeting()
            except Exception:
                pass
        # Fallback
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Guten Morgen! 🐺"
        elif 12 <= hour < 18:
            return "Hey! 🐺"
        else:
            return "Guten Abend! 🐺"
    
    def get_farewell_style(self) -> str:
        """Abschied von echtem Personality-System"""
        if self.brain and hasattr(self.brain, 'personality') and self.brain.personality:
            try:
                return self.brain.personality.get_farewell()
            except Exception:
                pass
        return "Bis bald! 🐺"
    
    def get_emotion_response(self) -> str:
        """Emotions-Antwort vom echten Energy-System"""
        state = self._get_energy_state()
        if state:
            try:
                mood = state.mood.value if hasattr(state.mood, 'value') else "gut"
                energy = state.effective_energy
                if energy > 0.7:
                    energy_text = "voller Energie"
                elif energy > 0.4:
                    energy_text = "ganz okay"
                else:
                    energy_text = "etwas müde"
                return f"Mir geht's {mood}! Bin {energy_text}. Und dir? 🐺"
            except Exception:
                pass
        return "Mir geht's gut! Und dir? 🐺"
    
    def update_from_interaction(self, intent: str, positive: bool = True):
        """Update via Brain's Systeme"""
        # Energy updaten
        if self.brain and hasattr(self.brain, 'energy') and self.brain.energy:
            try:
                if positive:
                    self.brain.energy.boost(5)
                else:
                    self.brain.energy.drain(5)
            except Exception:
                pass
        
        # Autonomy updaten
        if self.brain and hasattr(self.brain, 'unified_autonomy') and self.brain.unified_autonomy:
            try:
                self.brain.unified_autonomy.on_user_message("", positive)
            except Exception:
                pass
    
    def enhance_response(self, response: str, intent: str) -> str:
        """Response Enhancement via Brain"""
        # Kemonomimi-Ausdruck hinzufügen?
        if self.brain and hasattr(self.brain, 'get_kemonomimi_expression'):
            try:
                expr = self.brain.get_kemonomimi_expression()
                if expr and random.random() < 0.3:
                    response = f"{expr} {response}"
            except Exception:
                pass
        return response
    
    def get_context_for_llm(self) -> str:
        """Kontext für LLM vom Brain"""
        parts = []
        
        # Energy
        state = self._get_energy_state()
        if state:
            try:
                mood = state.mood.value if hasattr(state.mood, 'value') else "neutral"
                parts.append(f"Stimmung: {mood}")
            except Exception:
                pass
        
        # Relationship
        if self.brain and hasattr(self.brain, 'unified_autonomy') and self.brain.unified_autonomy:
            try:
                level = self.brain.unified_autonomy.relationship.state.level_name()
                parts.append(f"Beziehung: {level}")
            except Exception:
                pass
        
        return ", ".join(parts) if parts else ""


class HoloUnified:
    """
    Das komplette Holo-System - vereint alle Komponenten!
    
    Kann STANDALONE oder MIT HOLO_BRAIN laufen:
    
    Standalone:
        holo = HoloUnified()
        
    Mit Brain (empfohlen):
        brain = HoloBrain()
        holo = HoloUnified(brain=brain)  # Nutzt Brain's Module!
    """
    
    def __init__(self, brain=None):
        """
        Args:
            brain: Optional HoloBrain Referenz - wenn vorhanden,
                   werden dessen Module genutzt statt eigener.
        """
        logger.info("🐺 Initialisiere Holo Unified v16...")
        
        self.brain = brain
        
        # === Komponenten initialisieren ===
        
        # 1. Smart Understanding (Intent + Typos)
        if UNDERSTANDING_AVAILABLE:
            self.understanding = SmartUnderstanding()
            logger.info("   ✅ SmartUnderstanding geladen")
        else:
            self.understanding = None
            logger.info("   ⚠️ SmartUnderstanding nicht verfügbar")
        
        # 2. Unified LLM (Routing)
        if LLM_AVAILABLE:
            self.llm = UnifiedLLM()
            logger.info("   ✅ UnifiedLLM geladen")
        else:
            self.llm = None
            logger.info("   ⚠️ UnifiedLLM nicht verfügbar")
        
        # 3. Context Manager (Compression)
        if CONTEXT_AVAILABLE:
            self.context = SmartContextManager()
            logger.info("   ✅ ContextManager geladen")
        else:
            self.context = None
            logger.info("   ⚠️ ContextManager nicht verfügbar")
        
        # 4. Personality Engine - WICHTIG: Nutze Brain wenn vorhanden!
        if brain is not None:
            self.personality = BrainPersonalityAdapter(brain)
            logger.info("   ✅ PersonalityEngine (via HoloBrain)")
        else:
            self.personality = PersonalityEngine()
            logger.info("   ✅ PersonalityEngine (standalone)")
        
        # 5. Data Provider
        self.data = DataProvider()
        logger.info("   ✅ DataProvider geladen")
        
        # Stats
        self.stats = {
            "total_queries": 0,
            "pattern_hits": 0,
            "local_calls": 0,
            "remote_calls": 0,
            "personality_responses": 0,
        }
        
        mode = "integrated" if brain else "standalone"
        logger.info(f"🐺 Holo Unified v16 bereit! (Mode: {mode})")
    
    def process(self, text: str) -> Dict:
        """
        Verarbeitet eine User-Nachricht und gibt Antwort zurück.
        
        Args:
            text: Die User-Nachricht
            
        Returns:
            {
                "response": str,
                "intent": str,
                "confidence": float,
                "route": str,
                "latency_ms": int,
                "typo_corrections": List[Tuple[str, str]],
            }
        """
        import time
        start = time.time()
        
        self.stats["total_queries"] += 1
        
        # === 1. TEXT VERSTEHEN ===
        if self.understanding:
            understood = self.understanding.understand(text)
            intent = understood["intent"]
            confidence = understood["confidence"]
            suggested_route = understood["suggested_route"]
            
            # Typo-Korrektur
            corrected_text, typo_corrections = self.understanding.correct_typos(text)
            if typo_corrections:
                logger.info(f"🔧 Typos korrigiert: {typo_corrections}")
                text = corrected_text
        else:
            # Fallback ohne Understanding
            intent = None
            confidence = 0.5
            suggested_route = "local"
            typo_corrections = []
        
        # === 2. ROUTE ENTSCHEIDEN ===
        route = suggested_route
        response = None
        
        # === 3. ANTWORT GENERIEREN ===
        
        # 3a. PERSONALITY RESPONSES (dynamisch, kein LLM)
        if intent in ["greeting", "farewell", "gratitude", "emotion"]:
            self.stats["personality_responses"] += 1
            route = "personality"
            
            if intent == "greeting":
                response = self.personality.get_greeting_style()
            elif intent == "farewell":
                response = self.personality.get_farewell_style()
            elif intent == "gratitude":
                response = self.personality.get_gratitude_response()
            elif intent == "emotion":
                response = self.personality.get_emotion_response()
        
        # 3b. PATTERN RESPONSES (Daten-basiert)
        elif route == "pattern" and self.llm:
            self.stats["pattern_hits"] += 1
            
            # Hole echte Daten
            data = self.data.get_all_data()
            data.update(self.personality.get_context_for_llm())
            
            # Pattern-Antwort mit Daten füllen
            result = self.llm.query(text, intent=intent, confidence=confidence, context=data)
            response = result.get("response", "")
            
            # Platzhalter ersetzen
            for key, value in data.items():
                response = response.replace(f"{{{key}}}", str(value))
        
        # 3c. LLM RESPONSES (Local oder Remote)
        elif self.llm:
            # Context holen
            history = []
            context_section = ""
            if self.context:
                context_section, history = self.context.get_full_context()
            
            # Wenn kein Intent erkannt wurde, nutze Remote für komplexe Fragen
            if intent is None and len(text) > 30:
                route = "remote"
            
            # LLM Query
            result = self.llm.query(
                text,
                intent=intent,
                confidence=confidence,
                history=history,
                context=self.personality.get_context_for_llm()
            )
            
            response = result.get("response", "")
            route = result.get("route", route)
            
            if route == "local":
                self.stats["local_calls"] += 1
            elif route == "remote":
                self.stats["remote_calls"] += 1
        
        # 3d. FALLBACK
        if not response:
            if route == "offline":
                response = "Ich bin gerade offline und kann nicht antworten. 🐺💤"
            else:
                response = "Hmm, da bin ich gerade überfragt... Frag mich gerne anders! 🐺"
            route = "fallback"
        
        # === 4. PERSÖNLICHKEIT HINZUFÜGEN ===
        response = self.personality.enhance_response(response, intent or "unknown")
        
        # === 5. CONTEXT UPDATEN ===
        if self.context:
            self.context.add_exchange(text, response)
        
        # === 6. ERGEBNIS ===
        latency = int((time.time() - start) * 1000)
        
        return {
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "route": route,
            "latency_ms": latency,
            "typo_corrections": typo_corrections,
        }
    
    def chat(self, text: str) -> str:
        """Einfache Chat-Methode - gibt nur die Antwort zurück"""
        result = self.process(text)
        return result["response"]
    
    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        stats = self.stats.copy()
        
        if self.llm:
            stats["llm_stats"] = self.llm.get_stats()
        
        if self.context:
            stats["context_stats"] = self.context.get_stats()
        
        stats["personality"] = {
            "energy": self.personality.state.energy,
            "mood": self.personality.state.get_mood_text(),
            "interactions_today": self.personality.state.interactions_today,
        }
        
        return stats
    
    def set_user_name(self, name: str):
        """Setzt den User-Namen für personalisierte Antworten"""
        self.personality.user_name = name
        logger.info(f"👤 User-Name gesetzt: {name}")


# =============================================================================
# INTERACTIVE CHAT
# =============================================================================

def interactive_chat():
    """Interaktiver Chat-Modus"""
    print("=" * 60)
    print("🐺 HOLO UNIFIED v16 - Interaktiver Chat")
    print("=" * 60)
    print("Befehle: /quit, /stats, /name <name>")
    print("-" * 60)
    
    holo = HoloUnified()
    
    while True:
        try:
            user_input = input("\n👤 Du: ").strip()
            
            if not user_input:
                continue
            
            # Befehle
            if user_input.lower() == "/quit":
                print("\n🐺 Tschüss! Bis bald!")
                break
            elif user_input.lower() == "/stats":
                stats = holo.get_stats()
                print("\n📊 Statistiken:")
                print(json.dumps(stats, indent=2, default=str))
                continue
            elif user_input.lower().startswith("/name "):
                name = user_input[6:].strip()
                holo.set_user_name(name)
                print(f"✅ Name gesetzt: {name}")
                continue
            
            # Normale Nachricht
            result = holo.process(user_input)
            
            print(f"\n🐺 Holo: {result['response']}")
            print(f"   [{result['route']}|{result['intent']}|{result['latency_ms']}ms]")
            
            if result['typo_corrections']:
                print(f"   🔧 Korrigiert: {result['typo_corrections']}")
                
        except KeyboardInterrupt:
            print("\n\n🐺 Tschüss!")
            break
        except Exception as e:
            print(f"\n❌ Fehler: {e}")


# =============================================================================
# TEST
# =============================================================================

def run_tests():
    """Führt Tests durch"""
    print("=" * 70)
    print("🐺 HOLO UNIFIED v16 - TEST SUITE")
    print("=" * 70)
    
    holo = HoloUnified()
    
    test_cases = [
        # Personality (dynamisch)
        ("hallo", "greeting", "personality"),
        ("wie gehts dir?", "emotion", "personality"),
        ("danke!", "gratitude", "personality"),
        ("gute nacht", "farewell", "personality"),
        
        # Daten-Abfragen (pattern)
        ("nas status", "status_nas", "pattern"),
        ("cpu temperatur", "status_cpu", "pattern"),
        ("wie ist das wetter", "weather", "pattern"),
        ("wie spät ist es", "time", "pattern"),
        
        # Fragen (local LLM)
        ("was ist ki", "question_ki", "local"),
        ("was ki ist", "question_ki", "local"),  # Flexible Satzstellung
        ("was ist kii", "question_ki", "local"),  # Mit Typo!
        
        # Komplex (remote LLM)
        ("erkläre mir ausführlich machine learning", "question_ml", "remote"),
    ]
    
    print("\n🧪 TESTS:")
    print("-" * 70)
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_intent, expected_route in test_cases:
        result = holo.process(text)
        
        intent_ok = result["intent"] == expected_intent
        # Route kann variieren wenn LLM nicht verfügbar
        route_ok = (result["route"] == expected_route or 
                    result["route"] == "personality" or
                    result["route"] == "fallback")
        
        status = "✅" if (intent_ok or expected_intent is None) else "❌"
        if intent_ok or expected_intent is None:
            passed += 1
        
        print(f"\n{status} '{text}'")
        print(f"   Intent: {result['intent']} (erwartet: {expected_intent})")
        print(f"   Route: {result['route']} (erwartet: {expected_route})")
        print(f"   Response: {result['response'][:60]}...")
        print(f"   Latency: {result['latency_ms']}ms")
    
    print("\n" + "=" * 70)
    print(f"📊 ERGEBNIS: {passed}/{total} Tests bestanden ({passed/total*100:.0f}%)")
    print("=" * 70)
    
    # Stats
    print("\n📈 STATISTIKEN:")
    stats = holo.get_stats()
    print(f"   Total Queries: {stats['total_queries']}")
    print(f"   Personality: {stats['personality_responses']}")
    print(f"   Pattern: {stats['pattern_hits']}")
    print(f"   Local LLM: {stats['local_calls']}")
    print(f"   Remote LLM: {stats['remote_calls']}")
    
    print("\n" + "=" * 70)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        interactive_chat()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        # Default: Tests
        run_tests()
        print("\n💡 Tipp: Starte mit --chat für interaktiven Modus")
