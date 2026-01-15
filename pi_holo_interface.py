#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PI-CONTROL HOLO INTERFACE v12.0
================================
Vollständige Schnittstelle zwischen Holo Brain und Pi-Control.

NEU IN v12: Komplette Datenbrücke für Holos Persönlichkeit!
- Zugriff auf ALLE Pi-Control Daten
- Kontext-Extraktion für System-Prompt
- Proaktive Nachrichten
- Kalender, Geburtstage, Feiertage
- Wetter mit Interpretation
- AI Learning Insights

ENTHÄLT ALLE KLASSEN die holo_brain.py benötigt:
- PiControlBridge: API-Kommunikation mit Pi-Control
- HoloContextProvider: NEU! Kompletter Kontext für Holo
- NaturalLanguageHelper: Intent-Erkennung aus natürlicher Sprache
- DecisionEngine: Entscheidungslogik für Aktionen
- HoloInterface: High-Level Interface (kombiniert alles)
- HoloCommand, ExecutionResult: Datenklassen

Version: 12.0
"""

import json
import time
import re
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum

logger = logging.getLogger("PiHoloInterface")


# =============================================================================
# KONFIGURATION
# =============================================================================

class InterfaceConfig:
    """Konfiguration für die Pi-Control Schnittstelle"""

    # Pi-Control API
    PI_CONTROL_URL = "http://localhost:8008"

    # Timeouts
    API_TIMEOUT = 10
    HEALTH_CHECK_TIMEOUT = 3

    # State-Verzeichnis
    STATE_DIR = Path("/home/zero/pi/state")

    # Sicherheits-Einstellungen
    REQUIRE_CONFIRMATION_FOR = ["nas_sleep", "system_reboot", "governor_performance"]
    COOLDOWN_SECONDS = 5

    # Context Cache
    CONTEXT_CACHE_TTL = 30  # 30 Sekunden

    DEBUG_MODE = False


# =============================================================================
# ENUMS & DATENKLASSEN
# =============================================================================

class CommandPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class CommandType(Enum):
    NAS_CONTROL = "nas"
    SYSTEM_CONTROL = "system"
    GOVERNOR_CONTROL = "governor"
    QUERY = "query"
    CUSTOM = "custom"


@dataclass
class HoloCommand:
    """Ein Befehl von Holo an Pi-Control"""
    id: str
    command_type: CommandType
    action: str
    params: Dict = field(default_factory=dict)
    priority: CommandPriority = CommandPriority.NORMAL
    requires_confirmation: bool = False
    timestamp: float = field(default_factory=time.time)
    source: str = "holo"

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.command_type.value,
            "action": self.action,
            "params": self.params,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "source": self.source
        }


@dataclass
class ExecutionResult:
    """Ergebnis einer Befehlsausführung"""
    command_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    executed: bool = True
    execution_time_ms: float = 0
    reason: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "command_id": self.command_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "executed": self.executed,
            "execution_time_ms": self.execution_time_ms,
            "reason": self.reason
        }


# =============================================================================
# PI CONTROL BRIDGE - API Kommunikation
# =============================================================================

class PiControlBridge:
    """
    Bridge für Holo Brain zur Kommunikation mit Pi-Control.
    Ermöglicht direkten API-Zugriff auf Pi-Control Funktionen.
    """

    def __init__(self, api_url: str = None, state_dir: Path = None):
        self.api_url = (api_url or InterfaceConfig.PI_CONTROL_URL).rstrip('/')
        self.state_dir = state_dir or InterfaceConfig.STATE_DIR

        self._cached_state: Dict = {}
        self._cache_time: float = 0
        self._cache_ttl: float = 2.0
        self._connected: bool = False

        logger.info(f"[BRIDGE] Initialized: {self.api_url}")

    # === INTERNAL HELPERS ===

    def _get_state(self) -> Dict:
        """Holt aktuellen Status mit Cache"""
        now = time.time()
        if self._cached_state and (now - self._cache_time) < self._cache_ttl:
            return self._cached_state

        try:
            resp = requests.get(
                f"{self.api_url}/api/state",
                timeout=InterfaceConfig.API_TIMEOUT
            )
            if resp.status_code == 200:
                self._cached_state = resp.json()
                self._cache_time = now
                self._connected = True
                return self._cached_state
        except Exception as e:
            logger.debug(f"State fetch error: {e}")
            self._connected = False

        return self._cached_state or {}

    def _api_call(self, method: str, endpoint: str,
                  data: dict = None, timeout: int = None) -> Dict:
        """Generischer API-Aufruf"""
        url = f"{self.api_url}{endpoint}"
        timeout = timeout or InterfaceConfig.API_TIMEOUT

        try:
            if method.upper() == "GET":
                resp = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                resp = requests.post(url, json=data or {}, timeout=timeout)
            else:
                return {"success": False, "error": f"Unknown method: {method}"}

            self._connected = True

            if resp.status_code == 200:
                return resp.json() if resp.text else {"success": True}
            return {"success": False, "error": f"HTTP {resp.status_code}"}

        except requests.exceptions.Timeout:
            self._connected = False
            return {"success": False, "error": "Timeout"}
        except requests.exceptions.ConnectionError:
            self._connected = False
            return {"success": False, "error": "Connection refused"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === BASIC PROPERTIES ===

    @property
    def connected(self) -> bool:
        """Prüft ob Pi-Control erreichbar ist"""
        if time.time() - self._cache_time > 10:
            self._get_state()
        return self._connected

    @property
    def full_state(self) -> Dict:
        """Gibt den kompletten State zurück"""
        return self._get_state()

    @property
    def state_block(self) -> Dict:
        """Gibt den state Block zurück"""
        return self._get_state().get("state", {})

    @property
    def ai_extended(self) -> Dict:
        """Gibt ai_extended Block zurück"""
        return self._get_state().get("ai_extended", {})

    @property
    def presence(self) -> Dict:
        """Gibt presence Block zurück"""
        return self._get_state().get("presence", {})

    # === NAS ===

    @property
    def nas_status(self) -> Dict:
        """Gibt NAS-Status zurück"""
        return self.state_block.get("nas_status", {})

    @property
    def nas_online(self) -> bool:
        """Prüft ob NAS online ist"""
        return self.nas_status.get("online", False)

    @property
    def nas_connections(self) -> int:
        """Aktive NAS-Verbindungen"""
        return self.nas_status.get("connections", 0)

    # === SYSTEM ===

    @property
    def system_metrics(self) -> Dict:
        """Gibt System-Metriken zurück"""
        return self.state_block.get("system_metrics", {})

    @property
    def cpu_temp(self) -> float:
        """CPU Temperatur in °C"""
        return self.system_metrics.get("cpu_temp", 0)

    @property
    def cpu_usage(self) -> float:
        """CPU Auslastung in %"""
        return self.system_metrics.get("cpu_usage", 0)

    @property
    def current_governor(self) -> str:
        """Aktueller CPU Governor"""
        return self.state_block.get("cpu_governor", "unknown")

    # === WETTER ===

    @property
    def weather(self) -> Dict:
        """Wetter-Daten"""
        return self.ai_extended.get("weather", {})

    @property
    def forecast(self) -> List[Dict]:
        """Wettervorhersage"""
        return self.ai_extended.get("forecast_24h", [])

    # === KALENDER & EVENTS ===

    @property
    def calendar_events(self) -> List[Dict]:
        """Kalender-Events"""
        ext_ctx = self.ai_extended.get("external_context", {})
        return ext_ctx.get("calendar", [])

    @property
    def holidays(self) -> Dict:
        """Feiertags-Info"""
        ext_ctx = self.ai_extended.get("external_context", {})
        return ext_ctx.get("holiday", {})

    # === PRESENCE ===

    @property
    def day_mode(self) -> Dict:
        """Aktueller Tages-Modus"""
        return self.presence.get("day_mode", {})

    @property
    def presence_statistics(self) -> Dict:
        """Presence-Statistiken"""
        return self.presence.get("statistics", {})

    @property
    def user_is_home(self) -> bool:
        """Ist User zuhause?"""
        return self.presence_statistics.get("currently_home", True)

    @property
    def device_status(self) -> Dict:
        """Geräte-Status"""
        return self.state_block.get("device_status", {})

    # === AI LEARNING ===

    @property
    def ai_upgrade(self) -> Dict:
        """AI Upgrade Stats"""
        return self._get_state().get("ai_upgrade", {})

    @property
    def probabilistic(self) -> Dict:
        """Probabilistic Engine Stats"""
        return self._get_state().get("probabilistic", {})

    @property
    def nas_probability(self) -> float:
        """NAS-Nutzungswahrscheinlichkeit"""
        return self.probabilistic.get("probability", 0.5)

    @property
    def optimal_hours(self) -> List[int]:
        """Optimale Stunden für NAS"""
        bayesian = self.ai_upgrade.get("bayesian", {})
        return bayesian.get("optimal_hours", [])

    # === GOALS & DECISIONS ===

    @property
    def goals(self) -> Dict:
        """Aktuelle Goals"""
        return self._get_state().get("goals", {})

    @property
    def decision(self) -> Dict:
        """Aktuelle Decision/Plan"""
        return self._get_state().get("decision", {})

    # === EVENTS ===

    @property
    def nas_events(self) -> List[Dict]:
        """NAS Event History"""
        return self._get_state().get("nas_events", [])

    @property
    def logs(self) -> List[Dict]:
        """System Logs"""
        return self._get_state().get("logs", [])

    # === AKTIONEN ===

    def wake_nas(self) -> Dict:
        """Weckt das NAS per Wake-on-LAN"""
        logger.info("[BRIDGE] Waking NAS...")
        return self._api_call("POST", "/api/action?action=wake")

    def sleep_nas(self, force: bool = False) -> Dict:
        """Legt das NAS schlafen"""
        logger.info(f"[BRIDGE] Sleeping NAS (force={force})...")
        action = "force_suspend" if force else "suspend"
        return self._api_call("POST", f"/api/action?action={action}")

    def set_governor(self, governor: str) -> Dict:
        """Setzt den CPU Governor"""
        logger.info(f"[BRIDGE] Setting governor: {governor}")
        return self._api_call("POST", f"/api/action?action=set_governor_{governor}")

    def set_performance_mode(self) -> Dict:
        return self.set_governor("performance")

    def set_powersave_mode(self) -> Dict:
        return self.set_governor("powersave")

    def create_calendar_event(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        description: str = "",
        location: str = ""
    ) -> Dict:
        """Erstellt einen Kalender-Eintrag in Home Assistant"""
        logger.info(f"[BRIDGE] Creating calendar event: {summary}")
        return self._api_call("POST", "/api/command", data={
            "action": "create_calendar_event",
            "params": {
                "summary": summary,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "description": description,
                "location": location
            }
        })

    def get_full_state(self) -> Dict:
        """Gibt den vollständigen System-Status zurück (Force Refresh)"""
        self._cache_time = 0
        return self._get_state()

    def get_status_summary(self) -> str:
        """Gibt eine lesbare Status-Zusammenfassung"""
        state = self._get_state()

        if not state:
            return "Pi-Control nicht erreichbar"

        nas = "Online" if self.nas_online else "Offline"
        cpu = f"{self.cpu_usage:.0f}%, {self.cpu_temp:.1f}°C"
        gov = self.current_governor

        weather = self.weather
        weather_str = ""
        if weather.get("temp") is not None:
            weather_str = f", Wetter: {weather['temp']}°C"

        return f"NAS: {nas} | CPU: {cpu} | Governor: {gov}{weather_str}"


# =============================================================================
# HOLO CONTEXT PROVIDER - NEU IN v12!
# =============================================================================

class HoloContextProvider:
    """
    Stellt den kompletten Kontext für Holos Persönlichkeit bereit.

    Nutzt alle Pi-Control Daten um:
    - System-Prompt Kontext zu generieren
    - Proaktive Nachrichten zu erstellen
    - Wetter, Kalender, Events zu interpretieren

    NEU IN v12!
    """

    # Deutsche Wochentage
    WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                   "Freitag", "Samstag", "Sonntag"]

    # Bekannte deutsche Feiertage (Fallback)
    KNOWN_HOLIDAYS = [
        ("01-01", "Neujahr"),
        ("12-24", "Heiligabend"),
        ("12-25", "1. Weihnachtstag"),
        ("12-26", "2. Weihnachtstag"),
        ("12-31", "Silvester"),
    ]

    def __init__(self, bridge: PiControlBridge):
        self.bridge = bridge
        self._reminded_today: set = set()
        self._last_proactive_check = 0

    # =========================================================================
    # KOMPLETTER KONTEXT
    # =========================================================================

    def get_complete_context(self) -> Dict[str, Any]:
        """
        Holt den kompletten Kontext für Holo.

        Returns:
            Dict mit allen interpretierten Daten
        """
        return {
            "environment": self._get_environment(),
            "calendar": self._get_calendar_context(),
            "user": self._get_user_context(),
            "system": self._get_system_context(),
            "ai_insights": self._get_ai_insights(),
            "proactive": self._get_proactive_context(),
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "connected": self.bridge.connected,
            }
        }

    # =========================================================================
    # UMWELT / WETTER
    # =========================================================================

    def _get_environment(self) -> Dict:
        """Umwelt-Kontext (Wetter, Zeit, etc.)"""
        weather = self.bridge.weather

        return {
            "weather": self._interpret_weather(weather),
            "forecast": self.bridge.forecast[:4],
            "time": self._get_time_context(),
        }

    def _interpret_weather(self, weather: Dict) -> Dict:
        """Interpretiert Wetter persönlich für Holo"""
        temp = weather.get("temp")
        condition = (weather.get("condition") or "").lower()

        if temp is None:
            return {"available": False}

        # Temperatur-Gefühl
        if temp < -5:
            feeling, icon, suggestion = "eiskalt", "🥶", "BRRR! Bleib drinnen!"
        elif temp < 5:
            feeling, icon, suggestion = "kalt", "❄️", "Zieh dich warm an!"
        elif temp < 15:
            feeling, icon, suggestion = "kühl", "🌤️", "Jacke nicht vergessen!"
        elif temp < 25:
            feeling, icon, suggestion = "angenehm", "☀️", "Perfektes Wetter!"
        elif temp < 30:
            feeling, icon, suggestion = "warm", "🌡️", "Schön warm heute!"
        else:
            feeling, icon, suggestion = "heiß", "🔥", "Trink genug Wasser!"

        # Wetter-Bedingungen überschreiben
        if "rain" in condition or "regen" in condition:
            suggestion = "Regenschirm nicht vergessen! ☔"
            icon = "🌧️"
        elif "snow" in condition or "schnee" in condition:
            suggestion = "Es schneit! ❄️"
            icon = "🌨️"
        elif "storm" in condition or "gewitter" in condition:
            suggestion = "Gewitter! Bleib drinnen!"
            icon = "⛈️"

        return {
            "available": True,
            "temp": temp,
            "condition": weather.get("condition", ""),
            "humidity": weather.get("humidity"),
            "feeling": feeling,
            "icon": icon,
            "suggestion": suggestion,
        }

    def _get_time_context(self) -> Dict:
        """Zeit-Kontext"""
        now = datetime.now()
        hour = now.hour

        periods = [
            (5, 10, "morgen", "Guten Morgen", "🌅"),
            (10, 12, "vormittag", "Schönen Vormittag", "☀️"),
            (12, 14, "mittag", "Mahlzeit", "🍽️"),
            (14, 18, "nachmittag", "Schönen Nachmittag", "🌤️"),
            (18, 22, "abend", "Guten Abend", "🌆"),
            (22, 24, "nacht", "Gute Nacht", "🌙"),
            (0, 5, "nacht", "Noch wach?", "🌙"),
        ]

        period, greeting, emoji = "tag", "Hallo", "👋"
        for start, end, p, g, e in periods:
            if start <= hour < end:
                period, greeting, emoji = p, g, e
                break

        return {
            "period": period,
            "greeting": greeting,
            "emoji": emoji,
            "hour": hour,
            "weekday": self.WEEKDAYS_DE[now.weekday()],
            "is_weekend": now.weekday() >= 5,
            "date": now.strftime("%d.%m.%Y"),
        }

    # =========================================================================
    # KALENDER
    # =========================================================================

    def _get_calendar_context(self) -> Dict:
        """Kalender-Kontext mit Events, Geburtstagen, Feiertagen"""
        events = self.bridge.calendar_events
        today = datetime.now().date()

        today_events = []
        upcoming = []
        birthdays = []

        for event in events[:20]:
            try:
                start_str = event.get("start", "")
                if "T" in start_str:
                    event_date = datetime.fromisoformat(
                        start_str.replace("Z", "+00:00")
                    ).date()
                else:
                    event_date = datetime.strptime(start_str[:10], "%Y-%m-%d").date()

                days_until = (event_date - today).days

                formatted = {
                    "title": event.get("summary", event.get("title", "?")),
                    "start": start_str,
                    "days_until": days_until,
                }

                # Geburtstag?
                title_lower = formatted["title"].lower()
                is_birthday = any(x in title_lower for x in
                                  ["geburtstag", "birthday", "geb."])

                if is_birthday:
                    birthdays.append(formatted)
                elif days_until == 0:
                    today_events.append(formatted)
                elif 0 < days_until <= 7:
                    upcoming.append(formatted)

            except Exception as e:
                logger.debug(f"Event parse error: {e}")
                continue

        # Feiertage
        holidays = self._get_holidays()

        return {
            "today": today_events,
            "upcoming": sorted(upcoming, key=lambda x: x["days_until"])[:5],
            "birthdays": sorted(birthdays, key=lambda x: x["days_until"])[:5],
            "holidays": holidays,
            "has_events_today": len(today_events) > 0,
            "next_birthday": birthdays[0] if birthdays else None,
            "next_holiday": holidays[0] if holidays else None,
        }

    def _get_holidays(self) -> List[Dict]:
        """Holt Feiertage (von HA oder Fallback)"""
        # Versuche von Pi-Control
        holiday_info = self.bridge.holidays
        if holiday_info.get("is_holiday"):
            return [{"name": holiday_info.get("name"), "days_until": 0}]

        # Fallback: Bekannte Feiertage
        today = datetime.now()
        year = today.year

        holidays = []
        for month_day, name in self.KNOWN_HOLIDAYS:
            for y in [year, year + 1]:
                try:
                    date = datetime.strptime(f"{y}-{month_day}", "%Y-%m-%d").date()
                    days_until = (date - today.date()).days
                    if 0 <= days_until <= 14:
                        holidays.append({"name": name, "days_until": days_until})
                except Exception as e:
                    logger.debug(f"[PiHoloInterface] Holiday date parse failed for {name}: {e}")
                    continue

        return sorted(holidays, key=lambda x: x["days_until"])[:5]

    # =========================================================================
    # USER / PRESENCE
    # =========================================================================

    def _get_user_context(self) -> Dict:
        """User/Presence Kontext"""
        day_mode = self.bridge.day_mode
        device_status = self.bridge.device_status

        devices_online = [
            k.replace("_online", "")
            for k, v in device_status.items() if v
        ]

        return {
            "is_home": self.bridge.user_is_home,
            "day_mode": {
                "mode": day_mode.get("mode", "unknown"),
                "display": day_mode.get("display_name", day_mode.get("mode", "?")),
                "is_weekend": day_mode.get("mode") in ["weekend", "Wochenende"],
            },
            "devices_online": devices_online,
            "pc_active": device_status.get("workstation_pc_online", False),
        }

    # =========================================================================
    # SYSTEM
    # =========================================================================

    def _get_system_context(self) -> Dict:
        """System-Kontext"""
        return {
            "nas": {
                "online": self.bridge.nas_online,
                "connections": self.bridge.nas_connections,
            },
            "pi": {
                "cpu_temp": self.bridge.cpu_temp,
                "cpu_usage": self.bridge.cpu_usage,
                "governor": self.bridge.current_governor,
            },
        }

    # =========================================================================
    # AI INSIGHTS
    # =========================================================================

    def _get_ai_insights(self) -> Dict:
        """AI Learning Insights"""
        return {
            "nas_probability": self.bridge.nas_probability,
            "nas_likely": self.bridge.nas_probability > 0.6,
            "optimal_hours": self.bridge.optimal_hours[:3],
            "total_observations": self.bridge.probabilistic.get("total_observations", 0),
        }

    # =========================================================================
    # PROAKTIVE NACHRICHTEN
    # =========================================================================

    def _get_proactive_context(self) -> Dict:
        """Proaktive Nachrichten und Hinweise"""
        messages = []
        hints = []
        today_key = datetime.now().strftime("%Y-%m-%d")

        # Kalender holen
        cal = self._get_calendar_context()

        # Geburtstage
        for bday in cal.get("birthdays", [])[:2]:
            days = bday["days_until"]
            title = bday["title"]
            key = f"bday_{title}_{today_key}"

            if key not in self._reminded_today:
                if days == 0:
                    messages.append(f"🎂 Hey! Heute ist {title}! Nicht vergessen zu gratulieren!")
                    self._reminded_today.add(key)
                elif days == 1:
                    messages.append(f"📅 Morgen ist {title}!")
                    self._reminded_today.add(key)
                elif days <= 3:
                    hints.append(f"In {days} Tagen: {title}")

        # Feiertage
        for holiday in cal.get("holidays", [])[:1]:
            days = holiday["days_until"]
            name = holiday["name"]
            key = f"holiday_{name}_{today_key}"

            if key not in self._reminded_today:
                if days == 0:
                    messages.append(f"🎉 Heute ist {name}!")
                    self._reminded_today.add(key)
                elif days == 1:
                    messages.append(f"🎄 Morgen ist {name}!")
                    self._reminded_today.add(key)
                elif days <= 3:
                    hints.append(f"Nur noch {days} Tage bis {name}!")

        # Wetter-Hinweise
        weather = self._interpret_weather(self.bridge.weather)
        if weather.get("available") and weather.get("suggestion"):
            if "!" in weather["suggestion"]:  # Wichtige Hinweise
                hints.append(weather["suggestion"])

        return {
            "messages": messages,
            "hints": hints,
            "has_proactive": len(messages) > 0,
        }

    def get_proactive_messages(self) -> List[str]:
        """
        Gibt aktuelle proaktive Nachrichten zurück.

        Für direkten Zugriff ohne kompletten Kontext.
        """
        ctx = self._get_proactive_context()
        return ctx.get("messages", []) + ctx.get("hints", [])

    # =========================================================================
    # SYSTEM PROMPT BUILDER
    # =========================================================================

    def build_prompt_context(self) -> str:
        """
        Baut den kompletten Kontext für Holos System-Prompt.

        Returns:
            Formatierter String zum Einfügen in den System-Prompt
        """
        ctx = self.get_complete_context()
        parts = []

        # === HEADER ===
        parts.append("=" * 50)
        parts.append("UNTERBEWUSSTSEIN (Pi-Control)")
        parts.append("=" * 50)

        # === ZEIT & DATUM ===
        time_ctx = ctx["environment"]["time"]
        parts.append(f"\n📅 {time_ctx['weekday']}, {time_ctx['date']}")
        parts.append(f"⏰ {time_ctx['period'].capitalize()} {time_ctx['emoji']}")

        # === WETTER ===
        weather = ctx["environment"]["weather"]
        if weather.get("available"):
            parts.append(f"\n🌡️ Wetter: {weather['temp']}°C, {weather['condition']}")
            parts.append(f"   → {weather['feeling']} {weather['icon']}")
            if weather.get("suggestion"):
                parts.append(f"   💡 {weather['suggestion']}")

        # === FEIERTAGE ===
        cal = ctx["calendar"]
        if cal.get("holidays"):
            h = cal["holidays"][0]
            if h["days_until"] == 0:
                parts.append(f"\n🎉 HEUTE IST {h['name'].upper()}!")
            elif h["days_until"] == 1:
                parts.append(f"\n🎄 MORGEN ist {h['name']}!")
            elif h["days_until"] <= 7:
                parts.append(f"\n✨ In {h['days_until']} Tagen: {h['name']}")

        # === GEBURTSTAGE ===
        if cal.get("birthdays"):
            parts.append("\n🎂 GEBURTSTAGE:")
            for bday in cal["birthdays"][:3]:
                if bday["days_until"] == 0:
                    parts.append(f"   🎉 HEUTE: {bday['title']}!")
                elif bday["days_until"] == 1:
                    parts.append(f"   📅 Morgen: {bday['title']}")
                else:
                    parts.append(f"   📅 In {bday['days_until']} Tagen: {bday['title']}")

        # === TERMINE HEUTE ===
        if cal.get("today"):
            parts.append("\n📋 TERMINE HEUTE:")
            for event in cal["today"][:3]:
                parts.append(f"   • {event['title']}")

        # === USER STATUS ===
        user = ctx["user"]
        parts.append(f"\n👤 USER: {'Zuhause' if user['is_home'] else 'Unterwegs'}")
        parts.append(f"   Modus: {user['day_mode']['display']}")

        # === SYSTEM ===
        sys = ctx["system"]
        parts.append(f"\n💻 NAS: {'🟢 Online' if sys['nas']['online'] else '🔴 Offline'}")
        if sys['nas']['connections'] > 0:
            parts.append(f"   Verbindungen: {sys['nas']['connections']}")

        # === AI INSIGHTS ===
        ai = ctx["ai_insights"]
        if ai["nas_probability"] > 0.3:
            parts.append(f"\n🧠 NAS-Nutzung: {ai['nas_probability']*100:.0f}% wahrscheinlich")

        # === PROAKTIVE HINWEISE ===
        proactive = ctx["proactive"]
        if proactive.get("hints"):
            parts.append("\n💡 PROAKTIV:")
            for hint in proactive["hints"][:3]:
                parts.append(f"   → {hint}")

        parts.append("\n" + "=" * 50)

        return "\n".join(parts)


# =============================================================================
# SMART HOME CONTROLLER - NEU IN v12!
# =============================================================================

class SmartHomeNLP:
    """Erkennt Smart Home Befehle aus natürlicher Sprache"""

    ROOM_ALIASES = {
        "wohnzimmer": ["wohnzimmer", "wozi", "living"],
        "schlafzimmer": ["schlafzimmer", "bedroom", "schlazi"],
        "küche": ["küche", "kitchen", "kueche"],
        "bad": ["bad", "badezimmer", "bathroom"],
        "flur": ["flur", "gang", "corridor"],
        "büro": ["büro", "arbeitszimmer", "office"],
    }

    DEVICE_ALIASES = {
        "licht": ["licht", "lampe", "beleuchtung", "light"],
        "heizung": ["heizung", "thermostat", "temperatur", "heating", "wärme"],
        "tv": ["tv", "fernseher", "television"],
    }

    ACTION_PATTERNS = {
        "turn_on": [r"(?:mach|schalte?).*(?:an|ein)", r"aktiviere?", r"starte?"],
        "turn_off": [r"(?:mach|schalte?).*(?:aus)", r"deaktiviere?"],
        "increase": [r"(?:wärmer|heller|höher|mehr)", r"(?:erhöhe?|rauf)"],
        "decrease": [r"(?:kälter|dunkler|niedriger|weniger)", r"(?:reduziere?|runter)"],
        "set_value": [r"(?:auf|zu)\s*(\d+)", r"(\d+)\s*(?:grad|prozent)"],
    }

    def __init__(self):
        self._compiled = {
            action: [re.compile(p, re.IGNORECASE) for p in patterns]
            for action, patterns in self.ACTION_PATTERNS.items()
        }

    def parse(self, text: str) -> Dict[str, Any]:
        """Analysiert Smart Home Befehl"""
        text_lower = text.lower().strip()

        result = {
            "recognized": False,
            "action": None,
            "domain": None,
            "room": None,
            "device": None,
            "value": None,
        }

        # Aktion erkennen
        for action, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    result["action"] = action
                    break
            if result["action"]:
                break

        if not result["action"]:
            return result

        # Raum erkennen
        for room, aliases in self.ROOM_ALIASES.items():
            if any(a in text_lower for a in aliases):
                result["room"] = room
                break

        # Gerät erkennen
        device_to_domain = {"licht": "light", "heizung": "climate", "tv": "media_player"}
        for device, aliases in self.DEVICE_ALIASES.items():
            if any(a in text_lower for a in aliases):
                result["device"] = device
                result["domain"] = device_to_domain.get(device)
                break

        # Wert erkennen
        match = re.search(r'(\d+)', text_lower)
        if match:
            result["value"] = int(match.group(1))

        # Erkannt wenn Aktion + (Raum oder Gerät)
        if result["action"] and (result["room"] or result["device"]):
            result["recognized"] = True

        return result


class SmartHomeController:
    """
    Controller für Smart Home Befehle über Pi-Control.

    Ermöglicht Holo:
    - Lichter an/aus/dimmen
    - Heizung wärmer/kälter/Temperatur setzen
    - Status abfragen
    """

    TEMP_STEP = 1.0
    BRIGHTNESS_STEP = 25

    def __init__(self, bridge):
        self.bridge = bridge
        self.nlp = SmartHomeNLP()

    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Verarbeitet natürlichsprachlichen Smart Home Befehl.

        Args:
            text: "Mach das Licht in der Küche an"

        Returns:
            {"success": bool, "message": str, ...}
        """
        parsed = self.nlp.parse(text)

        if not parsed["recognized"]:
            return {
                "success": False,
                "message": "Ich hab nicht verstanden was du steuern möchtest.",
            }

        # Entity finden
        entity_id = self._find_entity(
            room=parsed["room"],
            device=parsed["device"],
            domain=parsed["domain"]
        )

        if not entity_id:
            room_str = f"im {parsed['room']}" if parsed["room"] else ""
            device_str = parsed["device"] or "Gerät"
            return {
                "success": False,
                "message": f"Ich finde kein {device_str} {room_str}.",
            }

        # Aktion ausführen
        result = self._execute_action(
            action=parsed["action"],
            entity_id=entity_id,
            domain=parsed["domain"],
            value=parsed["value"]
        )

        return {
            "success": result.get("success", False),
            "message": result.get("message", ""),
            "entity_id": entity_id,
            "action": parsed["action"],
        }

    def _find_entity(self, room: str = None, device: str = None,
                     domain: str = None) -> Optional[str]:
        """Findet passende Entity-ID aus CONFIG"""
        config = self.bridge.full_state.get("config", {})
        actors = config.get("actors", {})

        domain_to_key = {"light": "lights", "climate": "heating", "switch": "switches"}
        actor_key = domain_to_key.get(domain, "lights")
        entities = actors.get(actor_key, {})

        # Suche nach Raum
        if room:
            for name, eid in entities.items():
                if room in name.lower():
                    return eid

        # Fallback
        if entities:
            return list(entities.values())[0]

        return None

    def _execute_action(self, action: str, entity_id: str,
                        domain: str, value: int = None) -> Dict:
        """Führt Aktion aus"""

        if action == "turn_on":
            return self._call_service(domain, "turn_on", entity_id)

        elif action == "turn_off":
            return self._call_service(domain, "turn_off", entity_id)

        elif action == "increase":
            if domain == "climate":
                # Temperatur erhöhen
                return self._call_service(
                    "climate", "set_temperature", entity_id,
                    {"temperature": 21}  # TODO: Aktuelle Temp + STEP
                )
            elif domain == "light":
                return self._call_service(
                    "light", "turn_on", entity_id,
                    {"brightness_pct": 75}
                )

        elif action == "decrease":
            if domain == "climate":
                return self._call_service(
                    "climate", "set_temperature", entity_id,
                    {"temperature": 19}
                )
            elif domain == "light":
                return self._call_service(
                    "light", "turn_on", entity_id,
                    {"brightness_pct": 25}
                )

        elif action == "set_value" and value is not None:
            if domain == "climate":
                temp = max(16, min(28, value))
                return self._call_service(
                    "climate", "set_temperature", entity_id,
                    {"temperature": temp}
                )
            elif domain == "light":
                brightness = max(0, min(100, value))
                return self._call_service(
                    "light", "turn_on", entity_id,
                    {"brightness_pct": brightness}
                )

        return {"success": False, "message": "Unbekannte Aktion"}

    def _call_service(self, domain: str, service: str,
                      entity_id: str, data: Dict = None) -> Dict:
        """Ruft HA Service über Pi-Control auf"""
        result = self.bridge._api_call(
            "POST",
            "/api/ha/service",
            {
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "data": data or {}
            }
        )

        if result.get("success"):
            # Benutzerfreundliche Nachricht
            friendly_name = entity_id.split(".")[-1].replace("_", " ").title()

            if service == "turn_on":
                msg = f"✅ {friendly_name} ist jetzt an"
            elif service == "turn_off":
                msg = f"✅ {friendly_name} ist jetzt aus"
            elif service == "set_temperature":
                temp = data.get("temperature", "?")
                msg = f"✅ {friendly_name} auf {temp}°C gestellt"
            else:
                msg = f"✅ {friendly_name}: {service}"

            return {"success": True, "message": msg}
        else:
            return {
                "success": False,
                "message": f"❌ Fehler: {result.get('error', 'Pi-Control nicht erreichbar')}"
            }

    def get_available_entities(self) -> Dict[str, List[str]]:
        """Gibt verfügbare Entitäten zurück"""
        config = self.bridge.full_state.get("config", {})
        actors = config.get("actors", {})

        return {
            "lights": list(actors.get("lights", {}).keys()),
            "heating": list(actors.get("heating", {}).keys()),
            "switches": list(actors.get("switches", {}).keys()),
        }


# =============================================================================
# NATURAL LANGUAGE HELPER
# =============================================================================

class NaturalLanguageHelper:
    """
    Erkennt Absichten aus natürlicher Sprache.
    """

    PATTERNS = {
        "nas_wake": [
            r"nas.*(?:aufwecken|wecken|starten|an(?:machen)?|einschalten|wake)",
            r"(?:weck|start|mach).*nas.*(?:auf|an)",
            r"nas.*hochfahren",
            r"ich.*(?:brauche?|will|möchte).*nas",
        ],
        "nas_sleep": [
            r"nas.*(?:schlafen|ausschalten|runterfahren|aus(?:machen)?)",
            r"(?:leg|fahr).*nas.*(?:schlafen|runter|aus)",
        ],
        "nas_status": [
            r"(?:ist|wie).*nas.*(?:status|online|an|erreichbar)",
            r"nas.*(?:erreichbar|verfügbar|online)\??",
        ],
        "governor_performance": [
            r"(?:performance|leistung|schnell).*(?:modus|mode)",
            r"cpu.*(?:schneller|volle.*leistung|performance)",
        ],
        "governor_powersave": [
            r"(?:energiespar|powersave|stromspar).*(?:modus|mode)",
            r"cpu.*(?:sparen|langsamer|energiespar)",
        ],
        "system_status": [
            r"(?:wie|was).*(?:status|system|cpu|temperatur)",
            r"(?:zeig|gib).*(?:status|system.*info)",
        ],
        "weather": [
            r"(?:wie|was).*wetter",
            r"(?:temperatur|temp).*(?:draußen|außen)",
        ],
        # Smart Home Patterns
        "light_on": [
            r"(?:mach|schalte?).*licht.*(?:an|ein)",
            r"licht.*(?:an|ein)(?:schalten)?",
            r"(?:lampe|beleuchtung).*(?:an|ein)",
        ],
        "light_off": [
            r"(?:mach|schalte?).*licht.*aus",
            r"licht.*aus(?:schalten)?",
            r"(?:lampe|beleuchtung).*aus",
        ],
        "heating_up": [
            r"(?:mach|stell).*(?:heizung|temperatur).*(?:wärmer|höher)",
            r"(?:heizung|thermostat).*(?:wärmer|höher|rauf)",
            r"(?:wärmer).*(?:machen|stellen)?",
        ],
        "heating_down": [
            r"(?:mach|stell).*(?:heizung|temperatur).*(?:kälter|niedriger)",
            r"(?:heizung|thermostat).*(?:kälter|runter)",
        ],
        "set_temperature": [
            r"(?:heizung|temperatur).*(\d+)\s*(?:grad)?",
            r"(\d+)\s*grad",
        ],
    }

    def __init__(self):
        self._compiled = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in self.PATTERNS.items()
        }

    def parse(self, text: str) -> Dict:
        """Analysiert Text und erkennt Intent"""
        text_lower = text.lower().strip()

        best_intent = None
        best_confidence = 0

        for intent, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    confidence = 0.7 + (0.1 * len(pattern.findall(text_lower)))
                    if confidence > best_confidence:
                        best_confidence = min(1.0, confidence)
                        best_intent = intent

        return {
            "intent": best_intent,
            "confidence": best_confidence,
            "entities": self._extract_entities(text_lower),
            "original_text": text,
            "recognized": best_intent is not None
        }

    def _extract_entities(self, text: str) -> Dict:
        """Extrahiert Entitäten"""
        entities = {}

        # Governor
        if "performance" in text or "schnell" in text:
            entities["governor"] = "performance"
        elif "powersave" in text or "spar" in text:
            entities["governor"] = "powersave"

        # Force Flag
        if "sofort" in text or "force" in text or "trotzdem" in text:
            entities["force"] = True

        # Räume (für Smart Home)
        rooms = {
            "wohnzimmer": ["wohnzimmer", "wozi"],
            "schlafzimmer": ["schlafzimmer", "schlazi"],
            "küche": ["küche", "kueche", "kitchen"],
            "bad": ["bad", "badezimmer"],
            "flur": ["flur", "gang"],
            "büro": ["büro", "office", "arbeitszimmer"],
        }
        for room, aliases in rooms.items():
            if any(a in text for a in aliases):
                entities["room"] = room
                break

        # Temperatur
        import re
        temp_match = re.search(r'(\d+)\s*(?:grad)?', text)
        if temp_match:
            entities["temperature"] = int(temp_match.group(1))

        return entities

    def get_supported_intents(self) -> List[str]:
        return list(self.PATTERNS.keys())


# =============================================================================
# DECISION ENGINE
# =============================================================================

class DecisionEngine:
    """Entscheidet ob Befehle ausgeführt werden"""

    def __init__(self, bridge: PiControlBridge = None):
        self.bridge = bridge
        self._cooldowns: Dict[str, float] = {}
        self._pending_confirmations: Dict[str, HoloCommand] = {}

    def should_execute(self, command: HoloCommand, context: Dict = None) -> Tuple[bool, str]:
        """Entscheidet ob ein Befehl ausgeführt werden soll"""
        context = context or {}

        # Cooldown prüfen
        last_exec = self._cooldowns.get(command.action, 0)
        if time.time() - last_exec < InterfaceConfig.COOLDOWN_SECONDS:
            remaining = InterfaceConfig.COOLDOWN_SECONDS - (time.time() - last_exec)
            return False, f"Cooldown aktiv ({remaining:.0f}s)"

        # Bestätigung erforderlich?
        if command.action in InterfaceConfig.REQUIRE_CONFIRMATION_FOR:
            if command.id not in self._pending_confirmations:
                self._pending_confirmations[command.id] = command
                return False, "Bestätigung erforderlich"

        # Kontext-basierte Entscheidungen
        if command.action == "nas_sleep":
            if context.get("nas_in_use") and not command.params.get("force"):
                return False, "NAS wird gerade benutzt"

        if command.action == "governor_performance":
            cpu_temp = context.get("cpu_temp", 0)
            if cpu_temp > 75:
                return False, f"CPU zu heiß ({cpu_temp}°C)"

        return True, "OK"

    def confirm_command(self, command_id: str) -> bool:
        if command_id in self._pending_confirmations:
            del self._pending_confirmations[command_id]
            return True
        return False

    def record_execution(self, action: str):
        self._cooldowns[action] = time.time()

    def get_pending_confirmations(self) -> List[HoloCommand]:
        return list(self._pending_confirmations.values())


# =============================================================================
# HOLO INTERFACE - High-Level
# =============================================================================

class HoloInterface:
    """
    High-Level Interface das alles kombiniert.

    NEU IN v12:
    - HoloContextProvider: Kompletter Kontext für Persönlichkeit
    - SmartHomeController: Smart Home Steuerung!
    """

    def __init__(self, api_url: str = None, state_dir: str = None):
        self.bridge = PiControlBridge(
            api_url=api_url,
            state_dir=Path(state_dir) if state_dir else None
        )
        self.nlp = NaturalLanguageHelper()
        self.decision = DecisionEngine(self.bridge)

        # NEU: Context Provider
        self.context = HoloContextProvider(self.bridge)

        # NEU: Smart Home Controller
        self.smart_home = SmartHomeController(self.bridge)

        self._handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

        logger.info("[INTERFACE] HoloInterface v12 initialized (with Smart Home!)")

    def _register_default_handlers(self):
        """Registriert Standard-Handler"""

        @self.register_handler("nas_wake")
        def handle_nas_wake(params, context):
            result = self.bridge.wake_nas()
            return result.get("success", False), "NAS wake gesendet"

        @self.register_handler("nas_sleep")
        def handle_nas_sleep(params, context):
            force = params.get("force", False)
            result = self.bridge.sleep_nas(force=force)
            return result.get("success", False), "NAS sleep gesendet"

        @self.register_handler("nas_status")
        def handle_nas_status(params, context):
            online = self.bridge.nas_online
            conns = self.bridge.nas_connections
            return True, f"NAS ist {'online' if online else 'offline'}" + \
                         (f" ({conns} Verbindungen)" if conns else "")

        @self.register_handler("governor_performance")
        def handle_gov_perf(params, context):
            result = self.bridge.set_performance_mode()
            return result.get("success", False), "Governor: performance"

        @self.register_handler("governor_powersave")
        def handle_gov_save(params, context):
            result = self.bridge.set_powersave_mode()
            return result.get("success", False), "Governor: powersave"

        @self.register_handler("system_status")
        def handle_sys_status(params, context):
            return True, self.bridge.get_status_summary()

        @self.register_handler("weather")
        def handle_weather(params, context):
            w = self.context._interpret_weather(self.bridge.weather)
            if w.get("available"):
                return True, f"{w['temp']}°C, {w['condition']} {w['icon']}"
            return False, "Wetter nicht verfügbar"

        # NEU: Smart Home Handlers
        @self.register_handler("light_on")
        def handle_light_on(params, context):
            room = params.get("room", "")
            result = self.smart_home.process_command(f"Licht an {room}")
            return result["success"], result["message"]

        @self.register_handler("light_off")
        def handle_light_off(params, context):
            room = params.get("room", "")
            result = self.smart_home.process_command(f"Licht aus {room}")
            return result["success"], result["message"]

        @self.register_handler("heating_up")
        def handle_heating_up(params, context):
            room = params.get("room", "")
            result = self.smart_home.process_command(f"Heizung wärmer {room}")
            return result["success"], result["message"]

        @self.register_handler("heating_down")
        def handle_heating_down(params, context):
            room = params.get("room", "")
            result = self.smart_home.process_command(f"Heizung kälter {room}")
            return result["success"], result["message"]

        @self.register_handler("set_temperature")
        def handle_set_temp(params, context):
            room = params.get("room", "")
            temp = params.get("temperature", 20)
            result = self.smart_home.process_command(f"Heizung {room} auf {temp} Grad")
            return result["success"], result["message"]

        @self.register_handler("smart_home")
        def handle_smart_home(params, context):
            text = params.get("text", params.get("command", ""))
            result = self.smart_home.process_command(text)
            return result["success"], result["message"]

    def register_handler(self, action: str):
        """Decorator zum Registrieren eines Handlers"""
        def decorator(func):
            self._handlers[action] = func
            return func
        return decorator

    def process_text(self, text: str, context: Dict = None) -> ExecutionResult:
        """Verarbeitet natürlichsprachlichen Text"""
        parsed = self.nlp.parse(text)

        if not parsed["recognized"]:
            return ExecutionResult(
                command_id="none",
                success=False,
                executed=False,
                reason="Intent nicht erkannt"
            )

        command = HoloCommand(
            id=f"cmd_{int(time.time()*1000)}",
            command_type=CommandType.CUSTOM,
            action=parsed["intent"],
            params=parsed["entities"]
        )

        return self.execute(command, context)

    def execute(self, command: HoloCommand, context: Dict = None) -> ExecutionResult:
        """Führt einen Befehl aus"""
        context = context or {}
        start_time = time.time()

        should_exec, reason = self.decision.should_execute(command, context)

        if not should_exec:
            return ExecutionResult(
                command_id=command.id,
                success=False,
                executed=False,
                reason=reason
            )

        handler = self._handlers.get(command.action)

        if not handler:
            return ExecutionResult(
                command_id=command.id,
                success=False,
                executed=False,
                reason=f"Kein Handler für: {command.action}"
            )

        try:
            success, result = handler(command.params, context)
            self.decision.record_execution(command.action)

            return ExecutionResult(
                command_id=command.id,
                success=success,
                result=result,
                executed=True,
                execution_time_ms=(time.time() - start_time) * 1000
            )

        except Exception as e:
            logger.error(f"Handler error for {command.action}: {e}")
            return ExecutionResult(
                command_id=command.id,
                success=False,
                error=str(e),
                executed=True,
                execution_time_ms=(time.time() - start_time) * 1000
            )

    # === NEU: Context Methods ===

    def get_holo_context(self) -> Dict:
        """
        Gibt den kompletten Kontext für Holo zurück.

        NEU IN v12!
        """
        return self.context.get_complete_context()

    def get_prompt_context(self) -> str:
        """
        Gibt formatierten Kontext für System-Prompt zurück.

        NEU IN v12!
        """
        return self.context.build_prompt_context()

    def get_proactive_messages(self) -> List[str]:
        """
        Gibt proaktive Nachrichten zurück.

        NEU IN v12!
        """
        return self.context.get_proactive_messages()

    def get_status(self) -> Dict:
        """Gibt Interface-Status zurück"""
        return {
            "connected": self.bridge.connected,
            "api_url": self.bridge.api_url,
            "pending_confirmations": len(self.decision.get_pending_confirmations()),
            "registered_handlers": list(self._handlers.keys()),
            "version": "12.0"
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_interface(api_url: str = None) -> HoloInterface:
    """Erstellt ein HoloInterface"""
    return HoloInterface(api_url=api_url)


def create_bridge(api_url: str = None) -> PiControlBridge:
    """Erstellt eine PiControlBridge"""
    return PiControlBridge(api_url=api_url)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PI-CONTROL HOLO INTERFACE v12.0")
    print("=" * 60)

    print("""
NEU IN v12:
  - HoloContextProvider: Kompletter Kontext für Holo
  - SmartHomeController: Smart Home Steuerung!
  - Wetter-Interpretation mit Gefühlen
  - Kalender, Geburtstage, Feiertage
  - Proaktive Nachrichten
  - NLP für Smart Home Befehle

Klassen:
  - PiControlBridge: API-Kommunikation (erweitert!)
  - HoloContextProvider: Kontext für Persönlichkeit
  - SmartHomeController: NEU! Smart Home Steuerung
  - NaturalLanguageHelper: Intent-Erkennung (+ Smart Home)
  - HoloInterface: High-Level Interface

Beispiel:
  interface = HoloInterface()

  # Kompletter Kontext für System-Prompt
  prompt_ctx = interface.get_prompt_context()

  # Smart Home steuern
  result = interface.smart_home.process_command("Licht an in der Küche")

  # Oder über process_text (mit NLP)
  result = interface.process_text("Mach die Heizung wärmer")
""")

    # Smart Home NLP Test
    print("\n" + "-" * 40)
    print("🏠 Smart Home NLP Test:")
    print("-" * 40)

    nlp = NaturalLanguageHelper()

    test_phrases = [
        "Mach das Licht in der Küche an",
        "Heizung im Wohnzimmer wärmer",
        "Stell das Schlafzimmer auf 22 Grad",
        "Licht aus im Bad",
        "Mach die Lampe an",
        "Weck das NAS auf",
        "Wie ist das Wetter?",
    ]

    for phrase in test_phrases:
        result = nlp.parse(phrase)
        status = "✅" if result["recognized"] else "❌"
        intent = result["intent"] or "?"
        entities = result.get("entities", {})
        room = entities.get("room", "-")
        temp = entities.get("temperature", "-")
        print(f"  {status} '{phrase}'")
        print(f"     → Intent: {intent}, Room: {room}, Temp: {temp}")

    # Zeit Demo
    print("\n" + "-" * 40)
    print("⏰ Zeit-Kontext Demo:")
    print("-" * 40)

    now = datetime.now()
    hour = now.hour

    periods = [
        (5, 10, "morgen", "Guten Morgen", "🌅"),
        (10, 12, "vormittag", "Schönen Vormittag", "☀️"),
        (12, 14, "mittag", "Mahlzeit", "🍽️"),
        (14, 18, "nachmittag", "Schönen Nachmittag", "🌤️"),
        (18, 22, "abend", "Guten Abend", "🌆"),
        (22, 24, "nacht", "Gute Nacht", "🌙"),
        (0, 5, "nacht", "Noch wach?", "🌙"),
    ]

    for start, end, period, greeting, emoji in periods:
        if start <= hour < end:
            print(f"  Zeit: {period} → {greeting} {emoji}")
            break

    print(f"  Wochentag: {['Mo','Di','Mi','Do','Fr','Sa','So'][now.weekday()]}")

    # Feiertags-Check
    month_day = now.strftime("%m-%d")
    holidays = {
        "12-24": "Heiligabend",
        "12-25": "1. Weihnachtstag",
        "12-26": "2. Weihnachtstag",
        "12-31": "Silvester",
        "01-01": "Neujahr",
    }

    if month_day in holidays:
        print(f"  🎉 HEUTE: {holidays[month_day]}!")
    else:
        for md, name in holidays.items():
            try:
                h_date = datetime.strptime(f"{now.year}-{md}", "%Y-%m-%d")
                if h_date < now:
                    h_date = datetime.strptime(f"{now.year+1}-{md}", "%Y-%m-%d")
                days = (h_date.date() - now.date()).days
                if 0 < days <= 7:
                    print(f"  ✨ In {days} Tagen: {name}")
                    break
            except (ValueError, TypeError):
                pass  # Invalid date format

    # Pi-Control Patch Info
    print("\n" + "=" * 60)
    print("📋 BENÖTIGTER PI-CONTROL PATCH:")
    print("=" * 60)
    print("""
Füge in pi_control_v8_AI-extendet.py folgende API-Endpoints hinzu:

1. In DashboardHandler.do_POST(), nach anderen /api/ handlers:

    elif self.path.startswith("/api/ha/service"):
        # Smart Home Service aufrufen
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))

        domain = post_data.get("domain")
        service = post_data.get("service")
        entity_id = post_data.get("entity_id")
        data = post_data.get("data", {})

        # Extrahiere Name aus entity_id für actors.ha Aufruf
        name = entity_id.split(".")[-1]

        if domain == "light":
            if service == "turn_on":
                success = actors.ha.turn_on_light(name)
            elif service == "turn_off":
                success = actors.ha.turn_off_light(name)
        elif domain == "climate":
            temp = data.get("temperature", 20)
            success = actors.ha.set_heating_temp(name, temp)
        else:
            success = False

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": success}).encode())

2. Erweitere HomeAssistantActor um turn_off_light():

    def turn_off_light(self, name: str) -> bool:
        return self._call_service(domain="light", service="turn_off",
                                  entity_name=name)

3. Erweitere CONFIG["actors"] mit deinen Entitäten:

    "actors": {
        "heating": {
            "wohnzimmer": "climate.wohnzimmer_thermostat",
            "schlafzimmer": "climate.schlafzimmer_thermostat",
        },
        "lights": {
            "küche": "light.kuche_decke",
            "wohnzimmer": "light.wohnzimmer_main",
            "schlafzimmer": "light.schlafzimmer",
            "bad": "light.bad_decke",
        },
    }
""")
