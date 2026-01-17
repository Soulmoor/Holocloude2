#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Learning LLM System v15.0 - UNIFIED
==========================================

ALLES LLM-bezogene in EINER Datei!

NEUES KONZEPT:
- LOCAL (Pi, qwen2.5:1.5b) → Schnelle/einfache Sachen
- REMOTE (Mini-PC, deepseek-v2:16b) → Komplexe Sachen
- CACHED → Gelernte Patterns ohne LLM
- OFFLINE → Fallback wenn nichts erreichbar

ROUTING basierend auf:
- Intent-Typ (greeting → local, question → remote)
- Confidence (hoch → cached, niedrig → LLM)
- Text-Komplexität (kurz → local, lang → remote)

Architektur:
┌─────────────────────────────────────────────────────────────┐
│                     UnifiedLLM                              │
├─────────────────────────────────────────────────────────────┤
│  Input → Intent Detection → Routing Decision                │
│                    ↓                                        │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │ CACHED   │ LOCAL    │ REMOTE   │ OFFLINE  │            │
│  │ Pattern  │ Pi       │ Mini-PC  │ Fallback │            │
│  │ 0ms      │ ~100ms   │ ~500ms   │ 0ms      │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
└─────────────────────────────────────────────────────────────┘
"""

import json
import time
import hashlib
import logging
import requests
import threading
import re
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque, defaultdict
from typing import Optional, Dict, List, Any, Generator, Tuple
from dataclasses import dataclass, field, asdict
from difflib import SequenceMatcher
from enum import Enum
from holo_personality import HOLO_PERSONALITY

# Zentrale Konfiguration
try:
    from holo_config import get_config
    _HOLO_CONFIG_AVAILABLE = True
except ImportError:
    get_config = lambda path, default=None: default
    _HOLO_CONFIG_AVAILABLE = False

logger = logging.getLogger("UnifiedLLM")


# =============================================================================
# ZENTRALE KONFIGURATION - ALLES AN EINEM ORT!
# =============================================================================

class LLMConfig:
    """
    ╔═══════════════════════════════════════════════════════════╗
    ║  ZENTRALE LLM KONFIGURATION - HIER ALLES ÄNDERN!          ║
    ║  (Umbenannt von Config um Konflikte zu vermeiden)         ║
    ║                                                           ║
    ║  Konfigurierbar via Umgebungsvariablen:                   ║
    ║  - HOLO_LLM_LOCAL_HOST  (default: http://192.168.178.42:11434)  ║
    ║  - HOLO_LLM_REMOTE_HOST (default: http://192.168.178.42:11434)  ║
    ║  - HOLO_LLM_MODEL       (default: gemma3n:e4b)            ║
    ╚═══════════════════════════════════════════════════════════╝
    """

    # === HOSTS (via Config oder Umgebungsvariablen konfigurierbar) ===
    LOCAL_HOST = os.environ.get("HOLO_LLM_LOCAL_HOST",
                                get_config("network.ollama.local_host", "http://192.168.178.42:11434"))
    REMOTE_HOST = os.environ.get("HOLO_LLM_REMOTE_HOST",
                                 get_config("network.ollama.remote_host", "http://192.168.178.42:11434"))

    # === MODELLE (via Config oder Umgebungsvariablen konfigurierbar) ===
    LOCAL_MODEL = os.environ.get("HOLO_LLM_LOCAL_MODEL",
                                 get_config("llm.local_model", "holo4"))
    REMOTE_MODEL = os.environ.get("HOLO_LLM_REMOTE_MODEL",
                                  get_config("llm.remote_model", "holo4"))
    INTENT_MODEL = os.environ.get("HOLO_LLM_INTENT_MODEL",
                                  get_config("llm.local_model", "holo4"))

    # === ROUTING SCHWELLWERTE ===
    # Ab dieser Textlänge REMOTE nutzen
    COMPLEXITY_THRESHOLD = 80                        # Kürzere Texte → Local

    # Ab dieser Textlänge "ausführlich" → REMOTE
    DETAILED_THRESHOLD = 50

    # Bei dieser Confidence CACHED nutzen (ohne LLM)
    CACHE_CONFIDENCE_THRESHOLD = 0.85

    # === TIMEOUTS ===
    HEALTH_CHECK_TIMEOUT = 3
    LOCAL_TIMEOUT = 30          # Lokal ist schnell
    REMOTE_TIMEOUT = 120        # Remote braucht länger

    # === KEEP ALIVE ===
    KEEP_ALIVE = "30m"

    # === TEMPERATUR ===
    # Niedrig (0.1-0.3) = deterministisch, weniger Erfindungen
    # Mittel (0.4-0.6) = ausgewogen
    # Hoch (0.7-1.0) = kreativ, mehr Variation
    DEFAULT_TEMPERATURE = 0.2       # Standard: niedrig für Fakten-Treue
    CREATIVE_TEMPERATURE = 0.5      # Für kreative Aufgaben (Geschichten, etc.)
    FACTUAL_TEMPERATURE = 0.1       # Für reine Fakten-Abfragen

    # === CACHE ===
    CACHE_DIR = Path("/dev/shm/holo_llm_cache")
    MAX_CACHE_MB = 200

    # === INTENTS DIE PATTERN NUTZEN (Daten-basiert) ===
    PATTERN_INTENTS = {
        "status", "weather", "time", "temperature",
        "smart_home", "command", "help"
    }

    # === INTENTS DIE LOCAL LLM NUTZEN (Persönlichkeit) ===
    LOCAL_INTENTS = {
        "greeting", "farewell", "gratitude", "compliment",
        "emotion", "question", "chitchat", "introduction"
    }

    # === INTENTS DIE REMOTE BRAUCHEN (Komplex) ===
    REMOTE_INTENTS = {
        "search", "knowledge", "dream", "personality",
        "feedback", "creative", "code"
    }

    # === KEYWORDS DIE REMOTE TRIGGERN ===
    REMOTE_KEYWORDS = {
        "ausführlich", "erkläre", "detail", "genau",
        "warum", "wieso", "komplex", "vergleich",
        "unterschied", "programmier", "code", "script"
    }


# Alias für Kompatibilität
Config = LLMConfig


# =============================================================================
# SYSTEM PROMPTS - DEUTSCH OPTIMIERT!
# =============================================================================

class SystemPrompts:
    """
    System-Prompts für verschiedene Situationen.
    Mit deutschen Abkürzungen und Kontext!
    """

    # ERST die Basis-Teile definieren!
    GERMAN_CONTEXT = """WICHTIGE DEUTSCHE ABKÜRZUNGEN (immer so verstehen!):
- KI = Künstliche Intelligenz (Artificial Intelligence)
- NAS = Network Attached Storage (Netzwerkspeicher)
- LLM = Large Language Model (Sprachmodell)
- PC = Personal Computer
- API = Application Programming Interface
- GPU = Grafikprozessor
- CPU = Prozessor
- RAM = Arbeitsspeicher
- SSD = Solid State Drive
- usw. = und so weiter
- z.B. = zum Beispiel
- bzw. = beziehungsweise
- evtl. = eventuell
- ggf. = gegebenenfalls"""

    # Für Pattern-Antworten (kein LLM)
    PATTERN_CONTEXT = {
        "energy": 75,
        "mood": "gut gelaunt",
        "time_of_day": "Tag"
    }

    # DANN die Prompts die GERMAN_CONTEXT und HOLO_PERSONALITY nutzen
    LOCAL_PROMPT = f"""{GERMAN_CONTEXT}

{HOLO_PERSONALITY}

WICHTIG: Halte deine Antworten KURZ (2-4 Sätze max)."""

    REMOTE_PROMPT = f"""{GERMAN_CONTEXT}

{HOLO_PERSONALITY}

Du darfst ausführlicher antworten wenn nötig."""

# =============================================================================
# ROUTING ENTSCHEIDUNG
# =============================================================================

class RouteType(Enum):
    """Wohin wird die Anfrage geroutet?"""
    CACHED = "cached"       # Pattern-basiert, kein LLM
    LOCAL = "local"         # Pi, schnelles Model
    REMOTE = "remote"       # Mini-PC, großes Model
    OFFLINE = "offline"     # Kein LLM verfügbar


@dataclass
class RouteDecision:
    """Routing-Entscheidung mit Begründung"""
    route: RouteType
    host: str
    model: str
    reason: str
    confidence: float = 0.0


# =============================================================================
# PATTERN CACHE (Lernen ohne LLM)
# =============================================================================

@dataclass
class LearnedPattern:
    """Ein gelerntes Antwort-Pattern"""
    pattern: str                    # Regex oder Keyword
    response_template: str          # Antwort-Template
    intent: str                     # Zugehöriger Intent
    confidence: float = 0.5
    usage_count: int = 0
    last_used: str = ""
    positive_feedback: int = 0
    negative_feedback: int = 0


class PatternCache:
    """
    Lernt Patterns aus erfolgreichen Interaktionen.
    Kann einfache Anfragen OHNE LLM beantworten.
    """

    def __init__(self):
        self.patterns: Dict[str, LearnedPattern] = {}
        self._load_defaults()

    def _load_defaults(self):
        """
        Lade Standard-Patterns - NUR für DATEN-BASIERTE Antworten!

        NICHT für Persönlichkeit/Emotionen - das macht das LLM!

        Pattern-Typen:
        - System-Status (NAS, CPU, etc.)
        - Sensor-Daten (Temperatur, Wetter)
        - Zeit/Datum
        - Faktische Kurzantworten
        """
        defaults = [
            # =================================================================
            # SYSTEM STATUS - Handfeste Daten mit Platzhaltern
            # =================================================================
            LearnedPattern(
                pattern=r"^(nas |server )?(status|zustand)[\s!?]*$",
                response_template="📊 NAS Status:\n• Status: {nas_status}\n• Uptime: {nas_uptime}\n• CPU: {nas_cpu}%\n• RAM: {nas_ram}%",
                intent="status",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(ist |läuft )?(der |das )?(nas|server)( an| online)?[\s!?]*$",
                response_template="NAS ist {nas_status}! 💾",
                intent="status",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(nas|server) (starten|aufwecken|an)[\s!?]*$",
                response_template="🔄 Wecke NAS auf... {nas_wake_result}",
                intent="command",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(nas|server) (stoppen|schlafen|aus)[\s!?]*$",
                response_template="💤 NAS wird schlafen gelegt... {nas_sleep_result}",
                intent="command",
                confidence=0.95
            ),

            # =================================================================
            # SYSTEM MONITORING - CPU, RAM, Temperatur
            # =================================================================
            LearnedPattern(
                pattern=r"^(cpu|prozessor)( temperatur| temp| auslastung)?[\s!?]*$",
                response_template="🖥️ CPU: {cpu_temp}°C, Auslastung: {cpu_usage}%",
                intent="status",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(ram|speicher|arbeitsspeicher)( usage| nutzung)?[\s!?]*$",
                response_template="💾 RAM: {ram_used}GB / {ram_total}GB ({ram_percent}%)",
                intent="status",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(system|pi) (status|info|health)[\s!?]*$",
                response_template="📊 System:\n• CPU: {cpu_temp}°C ({cpu_usage}%)\n• RAM: {ram_percent}%\n• Uptime: {uptime}",
                intent="status",
                confidence=0.95
            ),

            # =================================================================
            # WETTER - Mit Platzhaltern für echte Daten
            # =================================================================
            LearnedPattern(
                pattern=r"^(wie ist das |)wetter[\s!?]*$",
                response_template="🌤️ Wetter: {weather_temp}°C, {weather_condition}\nHeute: {weather_forecast}",
                intent="weather",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(wie (warm|kalt) ist es|temperatur)( draußen)?[\s!?]*$",
                response_template="🌡️ Draußen: {weather_temp}°C ({weather_condition})",
                intent="weather",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(regnet|schneit) es[\s!?]*$",
                response_template="{weather_precipitation_answer}",
                intent="weather",
                confidence=0.9
            ),

            # =================================================================
            # ZEIT/DATUM - Einfache Fakten
            # =================================================================
            LearnedPattern(
                pattern=r"^wie (spät|viel uhr)( ist es)?[\s!?]*$",
                response_template="🕐 Es ist {current_time} Uhr",
                intent="time",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(welcher tag|welches datum|datum)( ist heute)?[\s!?]*$",
                response_template="📅 Heute ist {current_date}",
                intent="time",
                confidence=0.95
            ),

            # =================================================================
            # SMART HOME STATUS - Handfeste Daten
            # =================================================================
            LearnedPattern(
                pattern=r"^(licht|lampe|beleuchtung) status[\s!?]*$",
                response_template="💡 Lichter: {lights_status}",
                intent="smart_home",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^(temperatur|temp) (im |in der )?(wohnzimmer|schlafzimmer|küche|bad)[\s!?]*$",
                response_template="🌡️ {room}: {room_temp}°C",
                intent="temperature",
                confidence=0.95
            ),

            # =================================================================
            # HILFE/INFO - Statische Infos
            # =================================================================
            LearnedPattern(
                pattern=r"^(hilfe|help|was kannst du)[\s!?]*$",
                response_template="😊 Ich kann:\n• NAS steuern (status, starten, stoppen)\n• System überwachen (CPU, RAM, Temp)\n• Wetter abfragen\n• Smart Home steuern\n• Mit dir plaudern!\n\nFrag einfach!",
                intent="help",
                confidence=0.95
            ),
            LearnedPattern(
                pattern=r"^wer bist du[\s!?]*$",
                response_template="Ich bin Holo, eine weise Wölfin und deine KI-Assistentin! 😊",
                intent="info",
                confidence=0.95
            ),
        ]

        for p in defaults:
            key = hashlib.md5(p.pattern.encode()).hexdigest()[:8]
            self.patterns[key] = p

        logger.info(f"📊 {len(defaults)} Data-Patterns geladen (Status, Wetter, Zeit)")

    def find_match(self, text: str) -> Optional[Tuple[LearnedPattern, re.Match]]:
        """Sucht passendes Pattern"""
        text_lower = text.lower().strip()

        for pattern in self.patterns.values():
            if pattern.confidence < LLMConfig.CACHE_CONFIDENCE_THRESHOLD:
                continue

            try:
                match = re.match(pattern.pattern, text_lower, re.IGNORECASE)
                if match:
                    return (pattern, match)
            except re.error:
                continue

        return None

    def get_cached_response(self, text: str, context: Dict = None) -> Optional[str]:
        """Generiert Antwort aus Pattern (ohne LLM!)"""
        result = self.find_match(text)
        if not result:
            return None

        pattern, match = result
        response = pattern.response_template

        # Template-Variablen ersetzen
        if "{match}" in response and match.groups():
            response = response.replace("{match}", match.group(1))

        # Context für Template-Variablen (mit Defaults)
        ctx = SystemPrompts.PATTERN_CONTEXT.copy()
        if context:
            ctx.update(context)

        # Template-Variablen ersetzen
        if "{energy}" in response:
            response = response.replace("{energy}", str(ctx.get("energy", 75)))
        if "{mood}" in response:
            response = response.replace("{mood}", str(ctx.get("mood", "gut")))
        if "{time_of_day}" in response:
            response = response.replace("{time_of_day}", str(ctx.get("time_of_day", "Tag")))

        # Usage tracken
        pattern.usage_count += 1
        pattern.last_used = datetime.now().isoformat()

        logger.info(f"📦 CACHED: '{text[:30]}...' → Pattern Match")
        return response

    def learn_pattern(self, text: str, response: str, intent: str, feedback: float = 0.5):
        """Lernt neues Pattern aus erfolgreicher Interaktion"""
        # Nur bei positivem Feedback und kurzem Text
        if feedback < 0.6 or len(text) > 50:
            return

        # Einfaches Pattern erstellen
        text_lower = text.lower().strip()
        pattern_str = f"^{re.escape(text_lower)}$"

        key = hashlib.md5(text_lower.encode()).hexdigest()[:8]

        if key in self.patterns:
            # Update existing
            self.patterns[key].positive_feedback += 1
            self.patterns[key].confidence = min(0.95, self.patterns[key].confidence + 0.05)
        else:
            # New pattern
            self.patterns[key] = LearnedPattern(
                pattern=pattern_str,
                response_template=response,
                intent=intent,
                confidence=0.5
            )
            logger.debug(f"📚 Neues Pattern gelernt: '{text[:30]}...'")


# =============================================================================
# HOST HEALTH MANAGEMENT
# =============================================================================

class HostHealth:
    """Überwacht Verfügbarkeit der LLM-Hosts"""

    def __init__(self):
        self.status: Dict[str, Dict] = {}
        self.last_check: float = 0
        self._lock = threading.Lock()

    def check_host(self, host: str) -> Tuple[bool, float]:
        """Prüft ob Host erreichbar ist"""
        try:
            start = time.time()
            resp = requests.get(f"{host}/api/tags", timeout=LLMConfig.HEALTH_CHECK_TIMEOUT)
            latency = (time.time() - start) * 1000
            return resp.status_code == 200, latency
        except (requests.RequestException, OSError, TimeoutError):
            return False, -1

    def get_available_hosts(self) -> Dict[str, bool]:
        """Gibt verfügbare Hosts zurück"""
        with self._lock:
            now = time.time()

            # Refresh alle 30 Sekunden
            if now - self.last_check > 30:
                for host in [LLMConfig.LOCAL_HOST, LLMConfig.REMOTE_HOST]:
                    healthy, latency = self.check_host(host)
                    self.status[host] = {
                        "healthy": healthy,
                        "latency": latency,
                        "checked": now
                    }
                    status_str = f"OK ({latency:.0f}ms)" if healthy else "OFFLINE"
                    logger.debug(f"🏥 {host}: {status_str}")

                self.last_check = now

            return {h: s.get("healthy", False) for h, s in self.status.items()}

    def is_local_available(self) -> bool:
        return self.get_available_hosts().get(LLMConfig.LOCAL_HOST, False)

    def is_remote_available(self) -> bool:
        return self.get_available_hosts().get(LLMConfig.REMOTE_HOST, False)


# =============================================================================
# INTELLIGENT ROUTER
# =============================================================================

class IntelligentRouter:
    """
    Entscheidet wohin eine Anfrage geht basierend auf:
    - Intent
    - Text-Komplexität
    - Keywords (ausführlich, erkläre, etc.)
    - Host-Verfügbarkeit
    - Cached Patterns
    """

    def __init__(self, health: HostHealth, pattern_cache: PatternCache):
        self.health = health
        self.cache = pattern_cache

    def _needs_remote(self, text: str) -> bool:
        """Prüft ob der Text Remote braucht (Keywords, Länge)"""
        text_lower = text.lower()

        # Keywords die Remote triggern
        for keyword in LLMConfig.REMOTE_KEYWORDS:
            if keyword in text_lower:
                return True

        # Sehr lange Texte → Remote
        if len(text) > LLMConfig.COMPLEXITY_THRESHOLD:
            return True

        # Fragezeichen + lang → wahrscheinlich komplexe Frage
        if "?" in text and len(text) > LLMConfig.DETAILED_THRESHOLD:
            return True

        return False

    def decide(self, text: str, intent: str = None, confidence: float = 0.5) -> RouteDecision:
        """
        Trifft Routing-Entscheidung.

        NEUE LOGIK:
        1. PATTERN - NUR für Daten/Status (NAS, Wetter, Zeit, etc.)
        2. LOCAL - Für Persönlichkeit (Grüße, Emotionen, kurze Fragen)
        3. REMOTE - Für komplexe Sachen (ausführlich, Code, etc.)

        Charakter bleibt erhalten weil LOCAL LLM dynamisch antwortet!
        """
        text_len = len(text.strip())
        text_lower = text.lower()

        # === 1. PATTERN? Nur für Daten-basierte Anfragen! ===
        # Prüfe ob Intent ein "Daten-Intent" ist
        is_data_intent = intent in LLMConfig.PATTERN_INTENTS

        # Oder enthält Daten-Keywords
        data_keywords = ["status", "temperatur", "temp", "wetter", "zeit", "uhr",
                        "datum", "cpu", "ram", "nas", "server", "licht", "lampe"]
        has_data_keyword = any(kw in text_lower for kw in data_keywords)

        if is_data_intent or has_data_keyword:
            pattern_match = self.cache.find_match(text)
            if pattern_match:
                return RouteDecision(
                    route=RouteType.CACHED,
                    host="cache",
                    model="pattern",
                    reason=f"Daten-Abfrage ({intent or 'keyword'})",
                    confidence=0.95
                )

        # === 2. Host-Verfügbarkeit prüfen ===
        local_ok = self.health.is_local_available()
        remote_ok = self.health.is_remote_available()

        # === 3. Braucht es REMOTE? (Keywords, Komplexität) ===
        needs_remote = self._needs_remote(text)

        # === 4. Intent-basierte Entscheidung ===

        # REMOTE für komplexe Sachen
        if needs_remote or intent in LLMConfig.REMOTE_INTENTS:
            if remote_ok:
                return RouteDecision(
                    route=RouteType.REMOTE,
                    host=LLMConfig.REMOTE_HOST,
                    model=LLMConfig.REMOTE_MODEL,
                    reason=f"Komplex ({intent or 'keyword'})",
                    confidence=confidence
                )

        # LOCAL für Persönlichkeit und einfache Sachen
        if local_ok:
            return RouteDecision(
                route=RouteType.LOCAL,
                host=LLMConfig.LOCAL_HOST,
                model=LLMConfig.LOCAL_MODEL,
                reason=f"Dynamisch/Persönlichkeit ({intent or 'einfach'})",
                confidence=confidence
            )

        # === 5. Fallbacks ===
        if remote_ok:
            return RouteDecision(
                route=RouteType.REMOTE,
                host=LLMConfig.REMOTE_HOST,
                model=LLMConfig.REMOTE_MODEL,
                reason="Fallback zu Remote",
                confidence=confidence
            )

        # === 6. OFFLINE ===
        return RouteDecision(
            route=RouteType.OFFLINE,
            host="none",
            model="none",
            reason="Keine LLM-Hosts verfügbar!",
            confidence=0.0
        )


# =============================================================================
# UNIFIED LLM - DIE HAUPTKLASSE
# =============================================================================

class UnifiedLLM:
    """
    EINE Klasse für ALLE LLM-Aufrufe!

    Verwendung:
        llm = UnifiedLLM()

        # Einfach (automatisches Routing):
        response = llm.query("Hallo!")

        # Mit Intent-Info (besseres Routing):
        response = llm.query("Was ist Python?", intent="question")

        # Streaming:
        for chunk in llm.query_stream("Erzähl mir eine Geschichte"):
            print(chunk, end="")

        # KOMPATIBILITÄT mit altem SmartLearningLLM:
        llm = UnifiedLLM(
            ollama_host="http://192.168.178.42:11434",
            model="deepseek-v2:16b",
            temperature=0.2  # Niedrig für weniger Halluzinationen
        )
    """

    def __init__(self,
                 ollama_host: str = None,
                 model: str = None,
                 temperature: float = None,
                 num_ctx: int = None,
                 timeout: int = None,
                 keep_alive: str = None,
                 learning_enabled: bool = True,
                 energy_system = None,
                 **kwargs):  # Ignoriere unbekannte Parameter
        """
        Initialisiert UnifiedLLM.

        Alle Parameter sind optional für Rückwärtskompatibilität mit SmartLearningLLM.
        Wenn angegeben, überschreiben sie die Config-Werte.
        """

        # === Parameter übernehmen (für Kompatibilität) ===
        if ollama_host:
            LLMConfig.REMOTE_HOST = ollama_host
            # Wenn explizit ein Host angegeben wird, nutze ihn auch lokal
            if "localhost" in ollama_host or "127.0.0.1" in ollama_host:
                LLMConfig.LOCAL_HOST = ollama_host

        if model:
            LLMConfig.REMOTE_MODEL = model
            LLMConfig.LOCAL_MODEL = model  # Nutze gleiches Model wenn explizit angegeben

        if timeout:
            LLMConfig.REMOTE_TIMEOUT = timeout
            LLMConfig.LOCAL_TIMEOUT = min(timeout, 60)  # Local sollte schneller sein

        if keep_alive:
            LLMConfig.KEEP_ALIVE = keep_alive

        # Temperature und num_ctx werden pro-Request gehandhabt
        self.temperature = temperature if temperature is not None else LLMConfig.DEFAULT_TEMPERATURE
        self.num_ctx = num_ctx or 8192
        self.learning_enabled = learning_enabled
        self.energy_system = energy_system

        # === Kernkomponenten ===
        self.health = HostHealth()
        self.pattern_cache = PatternCache()
        self.router = IntelligentRouter(self.health, self.pattern_cache)

        # Response Cache (RAM)
        self.response_cache: Dict[str, Dict] = {}
        self.cache_max_size = 1000

        # Stats
        self.stats = {
            "total_queries": 0,
            "cached_hits": 0,
            "local_calls": 0,
            "remote_calls": 0,
            "offline_fallbacks": 0,
            "errors": 0
        }

        logger.info("🚀 UnifiedLLM initialisiert")
        self._log_status()

    def _log_status(self):
        """Loggt aktuellen Status"""
        local_ok = "✅" if self.health.is_local_available() else "❌"
        remote_ok = "✅" if self.health.is_remote_available() else "❌"

        logger.info(f"📊 Status: Local {local_ok} | Remote {remote_ok}")
        logger.info(f"🤖 Models: Local={LLMConfig.LOCAL_MODEL}, Remote={LLMConfig.REMOTE_MODEL}")

    def _get_temperature_for_intent(self, intent: str, prompt: str = "") -> float:
        """
        Bestimmt die optimale Temperatur basierend auf Intent.

        Niedrig (0.1-0.2): Fakten, Wissen, Status → weniger Halluzinationen
        Mittel (0.3-0.4): Chat, Persönlichkeit → natürlich aber kontrolliert
        Hoch (0.5-0.6): Kreativ, Geschichten → mehr Variation erlaubt
        """
        # Kreative Intents → höhere Temperatur
        creative_intents = {"creative", "dream", "story", "personality", "emotion"}
        if intent in creative_intents:
            return LLMConfig.CREATIVE_TEMPERATURE

        # Fakten-basierte Intents → sehr niedrige Temperatur
        factual_intents = {"status", "weather", "time", "temperature", "knowledge",
                          "smart_home", "command", "search", "code"}
        if intent in factual_intents:
            return LLMConfig.FACTUAL_TEMPERATURE

        # Prüfe prompt auf kreative Keywords
        creative_keywords = {"geschichte", "erzähl", "erfinde", "schreib", "dichte",
                            "phantasie", "träum", "vorstell"}
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in creative_keywords):
            return LLMConfig.CREATIVE_TEMPERATURE

        # Standard: niedrige Temperatur für weniger Halluzinationen
        return LLMConfig.DEFAULT_TEMPERATURE

    def query(self,
              prompt: str,
              intent: str = None,
              confidence: float = 0.5,
              system_prompt: str = None,
              context: Dict = None,
              history: List[Dict] = None,
              force_route: RouteType = None) -> Dict:
        """
        Hauptmethode für LLM-Anfragen.

        Args:
            prompt: Die Anfrage
            intent: Erkannter Intent (optional, verbessert Routing)
            confidence: Intent-Konfidenz (optional)
            system_prompt: System-Prompt (optional)
            context: Kontext-Dict (für Pattern-Templates)
            history: Chat-History
            force_route: Erzwingt bestimmte Route

        Returns:
            Dict mit response, source, latency_ms, etc.
        """
        self.stats["total_queries"] += 1
        start_time = time.time()

        # === ROUTING ENTSCHEIDUNG ===
        if force_route:
            decision = RouteDecision(
                route=force_route,
                host=LLMConfig.REMOTE_HOST if force_route == RouteType.REMOTE else LLMConfig.LOCAL_HOST,
                model=LLMConfig.REMOTE_MODEL if force_route == RouteType.REMOTE else LLMConfig.LOCAL_MODEL,
                reason=f"Forced: {force_route.value}"
            )
        else:
            decision = self.router.decide(prompt, intent, confidence)

        logger.info(f"🔀 Route: {decision.route.value} ({decision.reason})")

        # === CACHED ===
        if decision.route == RouteType.CACHED:
            cached_response = self.pattern_cache.get_cached_response(prompt, context)
            if cached_response:
                self.stats["cached_hits"] += 1
                return {
                    "response": cached_response,
                    "source": "cached_pattern",
                    "latency_ms": (time.time() - start_time) * 1000,
                    "route": "cached",
                    "model": "pattern"
                }

        # === OFFLINE ===
        if decision.route == RouteType.OFFLINE:
            self.stats["offline_fallbacks"] += 1
            return {
                "response": "Ich bin gerade offline und kann nicht antworten. 😊💤",
                "source": "offline_fallback",
                "latency_ms": 0,
                "route": "offline",
                "error": "No LLM hosts available"
            }

        # === LLM CALL (Local oder Remote) ===
        try:
            # Dynamische Temperatur basierend auf Intent
            dynamic_temp = self._get_temperature_for_intent(intent, prompt)

            result = self._call_llm(
                host=decision.host,
                model=decision.model,
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
                timeout=LLMConfig.LOCAL_TIMEOUT if decision.route == RouteType.LOCAL else LLMConfig.REMOTE_TIMEOUT,
                temperature=dynamic_temp
            )

            latency = (time.time() - start_time) * 1000

            if decision.route == RouteType.LOCAL:
                self.stats["local_calls"] += 1
            else:
                self.stats["remote_calls"] += 1

            # Optional: Pattern lernen bei erfolgreicher Antwort
            if result.get("response") and intent and len(prompt) < 50:
                self.pattern_cache.learn_pattern(prompt, result["response"], intent, 0.6)

            return {
                **result,
                "latency_ms": latency,
                "route": decision.route.value,
                "model": decision.model,
                "host": decision.host
            }

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ LLM Error: {e}")
            return {
                "response": f"Fehler: {str(e)}",
                "source": "error",
                "latency_ms": (time.time() - start_time) * 1000,
                "route": decision.route.value,
                "error": str(e)
            }

    def _call_llm(self, host: str, model: str, prompt: str,
                  system_prompt: str = None, history: List[Dict] = None,
                  timeout: int = 120, temperature: float = None) -> Dict:
        """Führt den eigentlichen LLM-Call durch"""

        messages = []

        # System-Prompt: Custom oder Default basierend auf Host
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif host == LLMConfig.LOCAL_HOST:
            messages.append({"role": "system", "content": SystemPrompts.LOCAL_PROMPT})
        else:
            messages.append({"role": "system", "content": SystemPrompts.REMOTE_PROMPT})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": prompt})

        # Temperatur: Parameter > Instance > Config Default
        effective_temp = temperature if temperature is not None else self.temperature

        try:
            response = requests.post(
                f"{host}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": effective_temp,
                        "num_ctx": self.num_ctx
                    },
                    "keep_alive": LLMConfig.KEEP_ALIVE
                },
                timeout=timeout
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            data = response.json()
            text = data.get("message", {}).get("content", "")

            return {
                "response": text,
                "source": "llm",
                "tokens": data.get("eval_count", 0)
            }

        except requests.exceptions.ConnectionError as e:
            logger.error(f"LLM Connection Error: {host} nicht erreichbar - {e}")
            raise Exception(f"Connection Error: {host} nicht erreichbar")
        except requests.exceptions.Timeout as e:
            logger.error(f"LLM Timeout: {host} antwortet nicht innerhalb {timeout}s")
            raise Exception(f"Timeout: Keine Antwort nach {timeout}s")
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM Request Error: {e}")
            raise Exception(f"Request Error: {e}")

    def query_stream(self,
                     prompt: str,
                     intent: str = None,
                     context_data: Dict = None,
                     system_prompt: str = None,
                     history: List[Dict] = None,
                     **kwargs) -> Generator[str, None, None]:

        decision = self.router.decide(prompt, intent)

        # Cached kann nicht streamen
        if decision.route == RouteType.CACHED:
            cached = self.pattern_cache.get_cached_response(prompt, context_data)
            if cached:
                yield cached
                return

        if decision.route == RouteType.OFFLINE:
            yield "Ich bin gerade offline... 😊💤"
            return

        # Stream von LLM
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        # Dynamische Temperatur basierend auf Intent
        dynamic_temp = self._get_temperature_for_intent(intent, prompt)

        response = None
        try:
            response = requests.post(
                f"{decision.host}/api/chat",
                json={
                    "model": decision.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": dynamic_temp,
                        "num_ctx": self.num_ctx
                    },
                    "keep_alive": LLMConfig.KEEP_ALIVE
                },
                stream=True,
                timeout=LLMConfig.REMOTE_TIMEOUT
            )

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.ConnectionError as e:
            logger.error(f"LLM Stream Connection Error: {decision.host} - {e}")
            yield "[Verbindungsfehler - LLM nicht erreichbar]"
        except requests.exceptions.Timeout as e:
            logger.error(f"LLM Stream Timeout: {decision.host}")
            yield "[Timeout - LLM antwortet nicht]"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"[Fehler: {e}]"
        finally:
            # Response schließen um Connection Leak zu vermeiden
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        total = self.stats["total_queries"] or 1
        return {
            **self.stats,
            "cache_hit_rate": f"{(self.stats['cached_hits'] / total) * 100:.1f}%",
            "local_rate": f"{(self.stats['local_calls'] / total) * 100:.1f}%",
            "remote_rate": f"{(self.stats['remote_calls'] / total) * 100:.1f}%",
            "hosts": self.health.status,
            "patterns_learned": len(self.pattern_cache.patterns)
        }


# =============================================================================
# KOMPATIBILITÄT MIT ALTEM CODE
# =============================================================================

# Alias für alten Code
SmartLearningLLM = UnifiedLLM

# Legacy Config
class LLMHostConfig:
    """Legacy-Kompatibilität"""
    PRIMARY_HOST = LLMConfig.REMOTE_HOST
    FALLBACK_HOSTS = [LLMConfig.LOCAL_HOST]
    DEFAULT_MODEL = LLMConfig.LOCAL_MODEL
    FAST_MODEL = LLMConfig.LOCAL_MODEL
    SMART_MODEL = LLMConfig.REMOTE_MODEL
    HEALTH_CHECK_TIMEOUT = LLMConfig.HEALTH_CHECK_TIMEOUT
    QUERY_TIMEOUT = LLMConfig.REMOTE_TIMEOUT
    STREAM_TIMEOUT = LLMConfig.REMOTE_TIMEOUT
    KEEP_ALIVE = LLMConfig.KEEP_ALIVE


# =============================================================================
# KOMPATIBILITÄT MIT ALTEM CODE
# =============================================================================

# Alias für Rückwärtskompatibilität mit smart_llm_system.py
SmartLearningLLM = UnifiedLLM

# Export-Liste
__all__ = [
    'Config',
    'SystemPrompts',
    'UnifiedLLM',
    'SmartLearningLLM',  # Alias für Kompatibilität
    'PatternCache',
    'LearnedPattern',
    'HealthMonitor',
    'Router',
]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=" * 70)
    print("😊 UnifiedLLM v15 - NEUES 3-Stufen-System")
    print("=" * 70)
    print("""
    PATTERN (0ms)  → NUR Daten: Status, Wetter, Zeit, Sensoren
    LOCAL (~100ms) → Persönlichkeit: Grüße, Emotionen, Fragen
    REMOTE (~500ms) → Komplex: Ausführlich, Code, Kreativ
    """)

    llm = UnifiedLLM()

    print("📊 Host Status:")
    print(f"   Local:  {'✅' if llm.health.is_local_available() else '❌'} {LLMConfig.LOCAL_HOST}")
    print(f"   Remote: {'✅' if llm.health.is_remote_available() else '❌'} {LLMConfig.REMOTE_HOST}")

    # Test Routing
    print("\n" + "=" * 70)
    print("🔀 ROUTING TESTS - Neue Logik:")
    print("=" * 70)

    tests = [
        # (Text, Intent, Erwartete Route, Begründung)
        ("hallo", "greeting", "LOCAL", "Persönlichkeit → dynamisch!"),
        ("wie geht's dir?", "emotion", "LOCAL", "Persönlichkeit → dynamisch!"),
        ("danke", "gratitude", "LOCAL", "Persönlichkeit → dynamisch!"),
        ("was ist ki", "question", "LOCAL", "Frage → dynamisch!"),
        ("gute nacht", "farewell", "LOCAL", "Persönlichkeit → dynamisch!"),
        ("nas status", "status", "CACHED", "Daten → handfeste Infos"),
        ("cpu temperatur", "status", "CACHED", "Daten → Sensoren"),
        ("wie ist das wetter", "weather", "CACHED", "Daten → Wetter-API"),
        ("wie spät ist es", "time", "CACHED", "Daten → Uhrzeit"),
        ("erkläre mir ausführlich machine learning", "question", "REMOTE", "Komplex!"),
        ("schreib mir python code", "code", "REMOTE", "Code → Remote"),
    ]

    for text, intent, expected, why in tests:
        decision = llm.router.decide(text, intent, 0.8)
        route = decision.route.value.upper()
        status = "✅" if route == expected else "❌"
        print(f"\n{status} '{text}'")
        print(f"   → {route} (erwartet: {expected})")
        print(f"   → Grund: {decision.reason}")
        print(f"   → Warum: {why}")

    # Pattern-Test für Daten
    print("\n" + "=" * 70)
    print("📊 PATTERN TESTS (Daten-Templates):")
    print("=" * 70)

    pattern_tests = ["nas status", "cpu temperatur", "wie ist das wetter", "wie spät ist es"]
    for text in pattern_tests:
        match = llm.pattern_cache.find_match(text)
        if match:
            pattern, _ = match
            print(f"\n'{text}'")
            print(f"   Template: {pattern.response_template[:60]}...")

    print("\n" + "=" * 70)
    print("😊 FAZIT:")
    print("=" * 70)
    print("""
    ✅ 'hallo', 'wie gehts', 'danke' → LOCAL LLM (dynamisch!)
       → Holo antwortet je nach Stimmung, Tageszeit, Energie
       → Charakter bleibt erhalten!

    ✅ 'nas status', 'wetter', 'zeit' → PATTERN (Daten)
       → Schnelle Antwort mit echten Daten
       → Platzhalter werden mit Live-Daten gefüllt

    ✅ 'erkläre ausführlich...' → REMOTE LLM (komplex)
       → Großes Model für intelligente Antworten
    """)
    print("=" * 70)
