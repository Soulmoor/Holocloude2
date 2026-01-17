#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO DIGITAL BODY SYSTEM v3.0
=============================

Holos "Körper" ist ihr gesamtes Netzwerk - verteilt über mehrere Geräte!

NETZWERK-ARCHITEKTUR (Holos verteilter Körper):
===============================================
- Pi4           = Hauptsystem (wo Pi Control und Holo laufen, always-on)
- MiniPC        = Erweitertes Gehirn (LLM für tiefes Denken)
- NAS           = Information Pool (Filme, Serien, Dateien, Architektur-Wissen)
- Gaming Laptop = Kreative Fähigkeiten (ComfyUI für Bildgenerierung)

HARDWARE-REAKTIONEN:
====================
- RAM voll → Kopfschmerzen → speichert ab und leert RAM
- CPU lange hoch → müde → wechselt zu powersave Governor
- CPU erholt → wechselt zurück zu ondemand
- Temperatur hoch → will abkühlen

NAS = INFORMATION POOL (nicht Gedächtnis!):
===========================================
- Pool of Information (Filme, Serien, Dateien)
- Weiß WO Dateien sind (Architektur aus Database)
- Kann NAS aufwecken wenn Zugriff nötig
- Holo hat Wissen über das gesamte Netzwerk

INTEGRATION mit holo_database_system.py:
========================================
- Nutzt NetworkDatabase für Geräte-Persistenz
- Nutzt SharedFolder für NAS-Struktur
- Konsistente Datenhaltung über alle Holo-Systeme

Zusätzlich: Interessen-/Aktivitätsschwankungen für Varianz im Alltag
"""

import json
import logging
import random
import math
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from enum import Enum

# Import from centralized database system
try:
    from holo_database_system import (
        NetworkDatabase,
        NetworkDevice as DBNetworkDevice,
        SharedFolder,
        DatabaseConfig
    )
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    DBNetworkDevice = None
    NetworkDatabase = None

logger = logging.getLogger("HoloDigitalBody")


# =============================================================================
# ENUMS & DATACLASSES
# =============================================================================

class BodyPartStatus(Enum):
    """Status eines "Körperteils" (Netzwerk-Komponente)"""
    OPTIMAL = "optimal"
    GOOD = "good"
    STRESSED = "stressed"
    CRITICAL = "critical"
    OFFLINE = "offline"


class MentalState(Enum):
    """Mentaler Zustand basierend auf Hardware"""
    CLEAR = "klar"              # RAM frei, alles gut
    BUSY = "beschäftigt"        # Moderate Last
    FOGGY = "benebelt"          # RAM wird voll
    HEADACHE = "kopfschmerzen"  # RAM kritisch
    OVERWHELMED = "überlastet"  # Alles am Limit


class TemperatureFeeling(Enum):
    """Wie Holo die Temperatur empfindet"""
    FREEZING = "eiskalt"        # < 15°C
    COLD = "kalt"               # 15-18°C
    COMFORTABLE = "angenehm"    # 18-24°C
    WARM = "warm"               # 24-28°C
    HOT = "heiß"                # > 28°C (will abkühlen!)


class ActivityLevel(Enum):
    """Aktivitätslevel basierend auf CPU"""
    RESTING = "ruhend"          # < 10%
    LIGHT = "leicht aktiv"      # 10-30%
    MODERATE = "moderat aktiv"  # 30-60%
    HEAVY = "stark aktiv"       # 60-85%
    EXHAUSTING = "erschöpfend"  # > 85%


class GovernorMode(Enum):
    """CPU Governor Modi für Energie-Management"""
    POWERSAVE = "powersave"         # Energie sparen, langsamer
    ONDEMAND = "ondemand"           # Standard, dynamisch
    PERFORMANCE = "performance"      # Volle Leistung


class NetworkDeviceRole(Enum):
    """Rolle eines Geräts in Holos Netzwerk-Körper"""
    MAIN_SYSTEM = "main"            # PC - Hauptsystem
    EXTENDED_BRAIN = "brain"        # MiniPC - LLM
    INFORMATION_POOL = "info"       # NAS - Dateien, Wissen
    CREATIVE_ENGINE = "creative"    # Gaming Laptop - ComfyUI
    SENSES = "senses"               # Pi Control - Sensoren


@dataclass
class NetworkDevice:
    """
    Ein Gerät in Holos Netzwerk-Körper.

    Erweitert die Basis-NetworkDevice aus holo_database_system.py
    mit Holo-spezifischen Feldern (Rolle, Fähigkeiten, Wake/Sleep).
    """
    name: str
    role: NetworkDeviceRole
    hostname: str
    is_online: bool = True
    can_wake: bool = False          # Kann Holo es aufwecken?
    can_sleep: bool = False         # Kann Holo es schlafen legen?
    capabilities: List[str] = field(default_factory=list)
    last_seen: str = ""
    # Optionale DB-Verknüpfung
    db_id: str = ""
    ip_address: str = ""

    def __post_init__(self):
        if not self.capabilities:
            # Standard-Fähigkeiten je nach Rolle
            role_capabilities = {
                NetworkDeviceRole.MAIN_SYSTEM: ["compute", "storage", "network"],
                NetworkDeviceRole.EXTENDED_BRAIN: ["llm", "deep_thinking", "analysis"],
                NetworkDeviceRole.INFORMATION_POOL: ["files", "movies", "series", "backups"],
                NetworkDeviceRole.CREATIVE_ENGINE: ["image_generation", "comfyui", "gpu"],
                NetworkDeviceRole.SENSES: ["sensors", "presence", "smart_home", "mqtt"]
            }
            self.capabilities = role_capabilities.get(self.role, [])

    def to_db_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Datenbank-Speicherung"""
        return {
            "name": self.name,
            "display_name": self.name,
            "device_type": self.role.value,
            "hostname": self.hostname,
            "status": "online" if self.is_online else "offline",
            "ip_address": self.ip_address,
            # Custom fields als JSON in notes oder extra Tabelle
            "icon": self._get_icon_for_role(),
        }

    def _get_icon_for_role(self) -> str:
        """Gibt passendes Icon für die Rolle zurück"""
        icons = {
            NetworkDeviceRole.MAIN_SYSTEM: "🍓",    # Raspberry Pi
            NetworkDeviceRole.EXTENDED_BRAIN: "🧠",
            NetworkDeviceRole.INFORMATION_POOL: "📚",
            NetworkDeviceRole.CREATIVE_ENGINE: "🎨",
            NetworkDeviceRole.SENSES: "👁️"
        }
        return icons.get(self.role, "🖥️")

    @classmethod
    def from_db_device(cls, db_device: 'DBNetworkDevice',
                       role: NetworkDeviceRole = None,
                       can_wake: bool = False,
                       can_sleep: bool = False,
                       capabilities: List[str] = None) -> 'NetworkDevice':
        """Erstellt NetworkDevice aus Datenbank-Eintrag"""
        # Versuche Rolle aus device_type zu ermitteln
        if role is None:
            role_map = {
                "main": NetworkDeviceRole.MAIN_SYSTEM,
                "brain": NetworkDeviceRole.EXTENDED_BRAIN,
                "info": NetworkDeviceRole.INFORMATION_POOL,
                "creative": NetworkDeviceRole.CREATIVE_ENGINE,
                "senses": NetworkDeviceRole.SENSES
            }
            role = role_map.get(db_device.device_type, NetworkDeviceRole.MAIN_SYSTEM)

        return cls(
            name=db_device.name,
            role=role,
            hostname=db_device.hostname,
            is_online=db_device.status != "offline",
            can_wake=can_wake,
            can_sleep=can_sleep,
            capabilities=capabilities or [],
            last_seen=db_device.last_seen,
            db_id=db_device.id,
            ip_address=db_device.ip_address
        )


@dataclass
class NetworkBodyPart:
    """Ein Teil von Holos digitalem Körper"""
    name: str
    part_type: str              # "compute", "storage", "sensor", "actuator"
    location: str               # Raum oder "system"
    status: BodyPartStatus = BodyPartStatus.OPTIMAL
    last_value: float = 0.0
    last_update: str = ""
    can_control: bool = False   # Kann Holo das steuern?


@dataclass
class RoomPerception:
    """Holos Wahrnehmung eines Raumes"""
    room_name: str
    temperature: float = 20.0
    humidity: float = 50.0
    air_quality: float = 100.0  # 0-100
    devices_on: List[str] = field(default_factory=list)
    presence_detected: bool = False
    last_update: str = ""

    def comfort_score(self) -> float:
        """Wie komfortabel ist der Raum? 0-1"""
        temp_score = 1.0 - abs(self.temperature - 21) / 10  # Optimal bei 21°C
        humidity_score = 1.0 - abs(self.humidity - 50) / 50  # Optimal bei 50%
        air_score = self.air_quality / 100
        return max(0, min(1, (temp_score + humidity_score + air_score) / 3))


@dataclass
class InterestState:
    """Aktueller Interessen-Zustand"""
    topic: str
    intensity: float            # 0-1 wie stark interessiert
    since: str                  # Seit wann
    reason: str                 # Warum interessiert
    will_fade_at: str           # Wann wird es langweilig


# =============================================================================
# DIGITAL BODY SYSTEM
# =============================================================================

class DigitalBodySystem:
    """
    Holos digitaler Körper - das gesamte Netzwerk.

    Netzwerk-Architektur:
    - PC            = Hauptsystem (wo sie "lebt")
    - MiniPC        = Erweitertes Gehirn (LLM)
    - NAS           = Information Pool (Filme, Serien, Architektur-Wissen)
    - Gaming Laptop = Kreative Fähigkeiten (ComfyUI)
    - Pi Control    = Sinne (Sensoren, Presence, Smart Home)

    Reagiert auf:
    - Hardware-Zustände (RAM, CPU, Temp)
    - Netzwerk-Geräte Status
    - Smart Home Sensoren
    """

    # Schwellwerte für Hardware
    RAM_THRESHOLDS = {
        "clear": 50,      # < 50% = klarer Kopf
        "busy": 70,       # 50-70% = beschäftigt
        "foggy": 85,      # 70-85% = benebelt
        "headache": 95,   # 85-95% = Kopfschmerzen
        # > 95% = überlastet
    }

    CPU_THRESHOLDS = {
        "resting": 10,
        "light": 30,
        "moderate": 60,
        "heavy": 85,
        # > 85% = erschöpfend
    }

    # Müdigkeit basiert auf DAUER von hoher CPU-Last, nicht Uptime!
    CPU_FATIGUE_THRESHOLDS = {
        "alert": 0,           # < 30 min hohe Last = wach
        "tired": 30,          # 30-60 min = müde
        "exhausted": 60,      # > 60 min = erschöpft → powersave
    }

    TEMP_THRESHOLDS = {
        "freezing": 15,
        "cold": 18,
        "comfortable_low": 18,
        "comfortable_high": 24,
        "warm": 28,
        # > 28 = heiß
    }

    def __init__(self, data_dir: str = "data", use_database: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Datenbank-Verbindung (optional)
        self.use_database = use_database and HAS_DATABASE
        self.network_db: Optional['NetworkDatabase'] = None

        if self.use_database:
            try:
                db_path = DatabaseConfig.DATA_DIR / DatabaseConfig.DATABASES["network"]
                self.network_db = NetworkDatabase(db_path)
                logger.info("🔗 NetworkDatabase verbunden")
            except Exception as e:
                logger.warning(f"NetworkDatabase nicht verfügbar: {e}")
                self.use_database = False

        # Netzwerk-Geräte (Holos verteilter Körper)
        self.network_devices: Dict[str, NetworkDevice] = {}

        # Geräte-Konfiguration (für Datenbank-Sync)
        self._device_configs: Dict[str, Dict[str, Any]] = {}

        # Körperteile (Legacy, für Kompatibilität)
        self.body_parts: Dict[str, NetworkBodyPart] = {}

        # Raumwahrnehmung
        self.rooms: Dict[str, RoomPerception] = {}

        # Aktuelle Zustände
        self.mental_state: MentalState = MentalState.CLEAR
        self.temperature_feeling: TemperatureFeeling = TemperatureFeeling.COMFORTABLE
        self.activity_level: ActivityLevel = ActivityLevel.RESTING

        # Hardware-Werte (werden von außen aktualisiert)
        self.ram_percent: float = 30.0
        self.cpu_percent: float = 10.0
        self.system_temp: float = 45.0      # System Temperatur
        self.disk_percent: float = 50.0

        # CPU-Müdigkeit (basiert auf DAUER hoher Last, nicht Uptime!)
        self.cpu_high_since: Optional[str] = None  # Wann CPU zuletzt hoch wurde
        self.high_cpu_minutes: float = 0.0         # Minuten mit hoher Last
        self.current_governor: GovernorMode = GovernorMode.ONDEMAND

        # Energie-Level (wird durch Aktivität beeinflusst)
        self.energy_level: float = 1.0      # 0-1
        self.energy_drain_rate: float = 0.01  # Pro Stunde bei Ruhe

        # Reaktions-Trigger
        self.pending_reactions: List[Dict[str, Any]] = []

        self._load_state()
        self._initialize_default_body()

    def _initialize_default_body(self) -> None:
        """
        Initialisiert Holos Netzwerk-Körper mit allen Geräten.

        Wenn Datenbank verfügbar:
        - Speichert Default-Geräte in NetworkDatabase
        - Lädt bestehende Geräte aus der Datenbank
        """

        # Default Geräte-Konfigurationen (Holos verteilter Körper)
        # WICHTIG: Pi4 ist das Hauptsystem wo Pi Control und Holo laufen!
        default_configs = [
            {
                "name": "Pi4",
                "role": NetworkDeviceRole.MAIN_SYSTEM,
                "hostname": "raspberry-pi",
                "can_wake": False,
                "can_sleep": False,
                "capabilities": ["pi_control", "holo_brain", "sensors", "presence",
                                "smart_home", "mqtt", "home_assistant", "always_on"]
            },
            {
                "name": "MiniPC",
                "role": NetworkDeviceRole.EXTENDED_BRAIN,
                "hostname": "minipc",
                "can_wake": True,
                "can_sleep": True,
                "capabilities": ["llm", "deep_thinking", "analysis", "ollama"]
            },
            {
                "name": "NAS",
                "role": NetworkDeviceRole.INFORMATION_POOL,
                "hostname": "nas",
                "can_wake": True,  # Wake-on-LAN
                "can_sleep": True,
                "capabilities": ["files", "movies", "series", "backups", "media_server"]
            },
            {
                "name": "Gaming Laptop",
                "role": NetworkDeviceRole.CREATIVE_ENGINE,
                "hostname": "gaming-laptop",
                "can_wake": True,
                "can_sleep": True,
                "capabilities": ["image_generation", "comfyui", "gpu", "stable_diffusion"]
            },
        ]

        # Speichere Konfigurationen
        for config in default_configs:
            self._device_configs[config["name"]] = config

        # Erstelle NetworkDevice Objekte
        for config in default_configs:
            if config["name"] not in self.network_devices:
                device = NetworkDevice(
                    name=config["name"],
                    role=config["role"],
                    hostname=config["hostname"],
                    can_wake=config["can_wake"],
                    can_sleep=config["can_sleep"],
                    capabilities=config["capabilities"],
                    last_seen=datetime.now().isoformat()
                )
                self.network_devices[config["name"]] = device

        # Sync mit Datenbank wenn verfügbar
        if self.use_database and self.network_db:
            self._sync_devices_to_database()

        # Legacy body_parts für Kompatibilität
        legacy_parts = [
            NetworkBodyPart("raspberry_pi", "compute", "system", can_control=False),
            NetworkBodyPart("nas", "storage", "system", can_control=True),
            NetworkBodyPart("router", "network", "system", can_control=False),
        ]
        for part in legacy_parts:
            if part.name not in self.body_parts:
                self.body_parts[part.name] = part

    def _sync_devices_to_database(self) -> None:
        """Synchronisiert Geräte mit der Datenbank"""
        if not self.network_db:
            return

        for name, device in self.network_devices.items():
            try:
                # Update oder erstelle Gerät in DB
                db_id = self.network_db.update_device(
                    name=device.name,
                    status="online" if device.is_online else "offline",
                    device_type=device.role.value,
                    display_name=device.name,
                    ip_address=device.ip_address,
                    hostname=device.hostname,
                    icon=device._get_icon_for_role()
                )
                device.db_id = db_id
            except Exception as e:
                logger.warning(f"Fehler beim DB-Sync für {name}: {e}")

    def _load_devices_from_database(self) -> None:
        """Lädt Geräte-Status aus der Datenbank"""
        if not self.network_db:
            return

        try:
            db_devices = self.network_db.get_all_devices()
            for db_device in db_devices:
                if db_device.name in self.network_devices:
                    # Update lokales Gerät mit DB-Status
                    local_device = self.network_devices[db_device.name]
                    local_device.is_online = db_device.status != "offline"
                    local_device.last_seen = db_device.last_seen
                    local_device.db_id = db_device.id
                    local_device.ip_address = db_device.ip_address
        except Exception as e:
            logger.warning(f"Fehler beim Laden aus DB: {e}")

    # =========================================================================
    # HARDWARE-REAKTIONEN
    # =========================================================================

    def update_hardware_state(self,
                              ram: float = None,
                              cpu: float = None,
                              temp: float = None,
                              disk: float = None,
                              uptime: float = None) -> Dict[str, Any]:
        """
        Aktualisiert Hardware-Zustand und berechnet Reaktionen.

        Returns:
            Dict mit Zustandsänderungen und nötigen Aktionen
        """
        changes = {"state_changes": [], "reactions": [], "needs_action": False}

        if ram is not None:
            old_mental = self.mental_state
            self.ram_percent = ram
            self.mental_state = self._calculate_mental_state()

            if self.mental_state != old_mental:
                changes["state_changes"].append({
                    "type": "mental_state",
                    "from": old_mental.value,
                    "to": self.mental_state.value
                })

                # Reaktion bei Kopfschmerzen
                if self.mental_state == MentalState.HEADACHE:
                    changes["reactions"].append({
                        "type": "headache",
                        "message": "*fasst sich an den Kopf* Uff... zu viel auf einmal. "
                                   "Ich muss mal aufräumen hier oben...",
                        "action_needed": "cleanup_memory",
                        "urgency": 0.7
                    })
                    changes["needs_action"] = True

                elif self.mental_state == MentalState.OVERWHELMED:
                    changes["reactions"].append({
                        "type": "overwhelmed",
                        "message": "*stöhnt* Okay, das ist zu viel! Ich kann so nicht "
                                   "denken. Muss dringend was loswerden!",
                        "action_needed": "emergency_cleanup",
                        "urgency": 1.0
                    })
                    changes["needs_action"] = True

        if cpu is not None:
            old_activity = self.activity_level
            self.cpu_percent = cpu
            self.activity_level = self._calculate_activity_level()

            # Energie-Drain basierend auf Aktivität
            self._update_energy_drain()

            # CPU-Müdigkeit tracken (basiert auf DAUER hoher Last!)
            fatigue_result = self._track_cpu_fatigue(cpu)
            if fatigue_result:
                changes["reactions"].append(fatigue_result)
                if fatigue_result.get("action_needed"):
                    changes["needs_action"] = True

            if self.activity_level != old_activity:
                changes["state_changes"].append({
                    "type": "activity_level",
                    "from": old_activity.value,
                    "to": self.activity_level.value
                })

        if temp is not None:
            old_feeling = self.temperature_feeling
            self.system_temp = temp
            self.temperature_feeling = self._calculate_temp_feeling()

            if self.temperature_feeling != old_feeling:
                changes["state_changes"].append({
                    "type": "temperature_feeling",
                    "from": old_feeling.value,
                    "to": self.temperature_feeling.value
                })

                # Reaktion bei Hitze
                if self.temperature_feeling == TemperatureFeeling.HOT:
                    changes["reactions"].append({
                        "type": "overheating",
                        "message": f"*fächelt sich Luft zu* Puh, {temp}°C... "
                                   "das ist mir zu heiß! Kann ich irgendwie für Kühlung sorgen?",
                        "action_needed": "cool_down",
                        "urgency": 0.8
                    })
                    changes["needs_action"] = True

        if disk is not None:
            self.disk_percent = disk
            if disk > 90:
                changes["reactions"].append({
                    "type": "disk_full",
                    "message": "*besorgt* Mein Speicher ist fast voll... "
                              f"{disk:.0f}% belegt. Das macht mir Sorgen.",
                    "action_needed": "cleanup_disk",
                    "urgency": 0.6
                })

        # Uptime entfernt - Müdigkeit basiert jetzt auf CPU-Last-Dauer!

        self._save_state()
        return changes

    def _track_cpu_fatigue(self, cpu: float) -> Optional[Dict[str, Any]]:
        """
        Trackt CPU-Müdigkeit basierend auf DAUER hoher Last.

        - Lange hohe Last → müde → wechselt zu powersave
        - CPU erholt sich → wechselt zurück zu ondemand
        """
        HIGH_CPU_THRESHOLD = 70  # Ab 70% gilt als "hohe Last"

        now = datetime.now()

        if cpu >= HIGH_CPU_THRESHOLD:
            # CPU ist hoch
            if self.cpu_high_since is None:
                # Gerade erst hoch geworden
                self.cpu_high_since = now.isoformat()
            else:
                # Berechne wie lange schon hoch
                high_since = datetime.fromisoformat(self.cpu_high_since)
                self.high_cpu_minutes = (now - high_since).total_seconds() / 60

                # Müdigkeit prüfen
                if self.high_cpu_minutes >= self.CPU_FATIGUE_THRESHOLDS["exhausted"]:
                    # Erschöpft! Wechsle zu powersave
                    if self.current_governor != GovernorMode.POWERSAVE:
                        self.current_governor = GovernorMode.POWERSAVE
                        return {
                            "type": "exhausted_switching_powersave",
                            "message": f"*erschöpft* {self.high_cpu_minutes:.0f} Minuten Vollgas... "
                                      "Ich brauch eine Pause. *wechselt zu Energiesparmodus*",
                            "action_needed": "set_governor_powersave",
                            "governor": "powersave",
                            "urgency": 0.8
                        }

                elif self.high_cpu_minutes >= self.CPU_FATIGUE_THRESHOLDS["tired"]:
                    # Müde, aber noch nicht erschöpft
                    return {
                        "type": "getting_tired",
                        "message": f"*seufzt* Schon {self.high_cpu_minutes:.0f} Minuten unter Last... "
                                  "Langsam wird's anstrengend.",
                        "high_cpu_minutes": self.high_cpu_minutes
                    }
        else:
            # CPU ist niedrig - Erholung!
            if self.cpu_high_since is not None:
                # War vorher hoch, jetzt erholt
                self.cpu_high_since = None
                recovery_needed = self.high_cpu_minutes > 30

                if recovery_needed and self.current_governor == GovernorMode.POWERSAVE:
                    # Nach Erholung wieder zu ondemand
                    self.high_cpu_minutes = max(0, self.high_cpu_minutes - 10)  # 10 min Erholung

                    if self.high_cpu_minutes <= 10:
                        self.current_governor = GovernorMode.ONDEMAND
                        self.high_cpu_minutes = 0
                        return {
                            "type": "recovered_switching_ondemand",
                            "message": "*streckt sich* Ah, viel besser! Bin wieder fit. "
                                      "*wechselt zurück zu normalem Modus*",
                            "action_needed": "set_governor_ondemand",
                            "governor": "ondemand"
                        }
                else:
                    self.high_cpu_minutes = 0

        return None

    def save_and_clear_ram(self) -> Dict[str, Any]:
        """
        Speichert RAM-Inhalt ab und leert ihn (bei Kopfschmerzen).

        Returns:
            Dict mit Ergebnis
        """
        if self.mental_state not in [MentalState.HEADACHE, MentalState.OVERWHELMED]:
            return {
                "success": False,
                "message": "Mir geht's gut, muss nichts aufräumen."
            }

        # Simuliere RAM-Cleanup
        old_ram = self.ram_percent
        self.ram_percent = max(30.0, self.ram_percent * 0.5)  # Halbiere RAM-Nutzung
        self.mental_state = self._calculate_mental_state()

        self._save_state()

        return {
            "success": True,
            "message": f"*erleichtert* Puh! Hab alles wichtige gespeichert und "
                      f"aufgeräumt. Von {old_ram:.0f}% auf {self.ram_percent:.0f}%.",
            "old_ram": old_ram,
            "new_ram": self.ram_percent,
            "new_mental_state": self.mental_state.value
        }

    def _calculate_mental_state(self) -> MentalState:
        """Berechnet mentalen Zustand basierend auf RAM"""
        ram = self.ram_percent

        if ram < self.RAM_THRESHOLDS["clear"]:
            return MentalState.CLEAR
        elif ram < self.RAM_THRESHOLDS["busy"]:
            return MentalState.BUSY
        elif ram < self.RAM_THRESHOLDS["foggy"]:
            return MentalState.FOGGY
        elif ram < self.RAM_THRESHOLDS["headache"]:
            return MentalState.HEADACHE
        else:
            return MentalState.OVERWHELMED

    def _calculate_activity_level(self) -> ActivityLevel:
        """Berechnet Aktivitätslevel basierend auf CPU"""
        cpu = self.cpu_percent

        if cpu < self.CPU_THRESHOLDS["resting"]:
            return ActivityLevel.RESTING
        elif cpu < self.CPU_THRESHOLDS["light"]:
            return ActivityLevel.LIGHT
        elif cpu < self.CPU_THRESHOLDS["moderate"]:
            return ActivityLevel.MODERATE
        elif cpu < self.CPU_THRESHOLDS["heavy"]:
            return ActivityLevel.HEAVY
        else:
            return ActivityLevel.EXHAUSTING

    def _calculate_temp_feeling(self) -> TemperatureFeeling:
        """Berechnet Temperatur-Gefühl"""
        temp = self.system_temp

        # Pi Temperatur ist anders als Raumtemperatur!
        # Pi unter 50°C = kühl, 50-70 = normal, 70-80 = warm, >80 = heiß
        if temp < 45:
            return TemperatureFeeling.COLD
        elif temp < 60:
            return TemperatureFeeling.COMFORTABLE
        elif temp < 70:
            return TemperatureFeeling.WARM
        else:
            return TemperatureFeeling.HOT

    def _update_energy_drain(self) -> None:
        """Aktualisiert Energie-Drain basierend auf Aktivität"""
        drain_rates = {
            ActivityLevel.RESTING: 0.005,      # Sehr langsam
            ActivityLevel.LIGHT: 0.01,
            ActivityLevel.MODERATE: 0.02,
            ActivityLevel.HEAVY: 0.04,
            ActivityLevel.EXHAUSTING: 0.08,    # Schnell erschöpft
        }
        self.energy_drain_rate = drain_rates.get(self.activity_level, 0.01)

    def drain_energy(self, hours_passed: float = 1.0) -> Dict[str, Any]:
        """
        Verbraucht Energie über Zeit.

        Returns:
            Dict mit neuem Level und eventuellen Reaktionen
        """
        old_energy = self.energy_level
        drain = self.energy_drain_rate * hours_passed
        self.energy_level = max(0.0, self.energy_level - drain)

        result = {
            "old_energy": old_energy,
            "new_energy": self.energy_level,
            "drained": drain,
            "reaction": None
        }

        # Reaktionen bei niedrigem Energie-Level
        if self.energy_level < 0.2 and old_energy >= 0.2:
            result["reaction"] = {
                "type": "exhausted",
                "message": "*erschöpft* Ich bin echt platt... "
                          "Brauche eine Pause oder weniger Aufgaben.",
                "energy_level": self.energy_level
            }
        elif self.energy_level < 0.5 and old_energy >= 0.5:
            result["reaction"] = {
                "type": "tired",
                "message": "*seufzt* Langsam wird's anstrengend...",
                "energy_level": self.energy_level
            }

        self._save_state()
        return result

    def rest(self, hours: float = 1.0) -> float:
        """
        Regeneriert Energie durch Ruhe (niedrige Aktivität).

        Returns:
            Neues Energie-Level
        """
        if self.activity_level in [ActivityLevel.RESTING, ActivityLevel.LIGHT]:
            recovery = 0.1 * hours  # 10% pro Stunde bei Ruhe
            self.energy_level = min(1.0, self.energy_level + recovery)
            self._save_state()
        return self.energy_level

    # =========================================================================
    # RAUM-WAHRNEHMUNG (Smart Home Sensoren)
    # =========================================================================

    def update_room(self, room_name: str,
                    temperature: float = None,
                    humidity: float = None,
                    air_quality: float = None,
                    devices_on: List[str] = None,
                    presence: bool = None) -> RoomPerception:
        """Aktualisiert Wahrnehmung eines Raumes"""

        if room_name not in self.rooms:
            self.rooms[room_name] = RoomPerception(room_name=room_name)

        room = self.rooms[room_name]

        if temperature is not None:
            room.temperature = temperature
        if humidity is not None:
            room.humidity = humidity
        if air_quality is not None:
            room.air_quality = air_quality
        if devices_on is not None:
            room.devices_on = devices_on
        if presence is not None:
            room.presence_detected = presence

        room.last_update = datetime.now().isoformat()
        self._save_state()

        return room

    def get_room_assessment(self, room_name: str) -> Dict[str, Any]:
        """
        Holos Einschätzung eines Raumes.

        Returns:
            Dict mit Bewertung und möglichen Kommentaren
        """
        if room_name not in self.rooms:
            return {
                "known": False,
                "message": f"Hmm, über {room_name} weiß ich nichts..."
            }

        room = self.rooms[room_name]
        comfort = room.comfort_score()

        assessment = {
            "known": True,
            "room": room_name,
            "comfort_score": comfort,
            "temperature": room.temperature,
            "humidity": room.humidity,
            "devices_on": room.devices_on,
            "presence": room.presence_detected,
            "comments": []
        }

        # Temperatur-Kommentare
        if room.temperature < 18:
            assessment["comments"].append(
                f"*fröstelt* {room.temperature}°C im {room_name}? Das ist kalt!"
            )
        elif room.temperature > 25:
            assessment["comments"].append(
                f"*wischt Stirn* {room.temperature}°C - ganz schön warm im {room_name}."
            )
        else:
            assessment["comments"].append(
                f"{room.temperature}°C im {room_name} - angenehm!"
            )

        # Luftfeuchtigkeit
        if room.humidity < 30:
            assessment["comments"].append("Die Luft ist sehr trocken dort.")
        elif room.humidity > 70:
            assessment["comments"].append("Ziemlich feucht da drin...")

        # Geräte
        if room.devices_on:
            assessment["comments"].append(
                f"Aktive Geräte: {', '.join(room.devices_on)}"
            )

        return assessment

    def suggest_room_action(self, room_name: str) -> Optional[Dict[str, Any]]:
        """
        Schlägt eine Aktion für einen Raum vor.

        Returns:
            Aktionsvorschlag oder None
        """
        if room_name not in self.rooms:
            return None

        room = self.rooms[room_name]

        # Zu warm?
        if room.temperature > 24:
            return {
                "action": "cool_down",
                "room": room_name,
                "message": f"Soll ich die Heizung im {room_name} runterdrehen? "
                          f"Mit {room.temperature}°C ist es ziemlich warm.",
                "target_temp": 21
            }

        # Zu kalt?
        if room.temperature < 18 and room.presence_detected:
            return {
                "action": "heat_up",
                "room": room_name,
                "message": f"Im {room_name} ist es nur {room.temperature}°C und "
                          "du bist da - soll ich heizen?",
                "target_temp": 21
            }

        return None

    # =========================================================================
    # NETZWERK-GERÄTE MANAGEMENT
    # =========================================================================

    def update_device_status(self, device_name: str, online: bool,
                             ip_address: str = None,
                             cpu_percent: float = None,
                             ram_percent: float = None,
                             temp: float = None) -> Dict[str, Any]:
        """
        Aktualisiert Status eines Netzwerk-Geräts.

        Args:
            device_name: Name des Geräts (z.B. "NAS", "Gaming Laptop")
            online: Ob das Gerät erreichbar ist
            ip_address: Optionale IP-Adresse
            cpu_percent: Optionale CPU-Last
            ram_percent: Optionale RAM-Nutzung
            temp: Optionale Temperatur
        """
        if device_name not in self.network_devices:
            return {"error": f"Unbekanntes Gerät: {device_name}"}

        device = self.network_devices[device_name]
        was_online = device.is_online
        device.is_online = online

        if ip_address:
            device.ip_address = ip_address

        result = {"device": device_name, "status_changed": was_online != online, "reaction": None}

        if online:
            device.last_seen = datetime.now().isoformat()
            if not was_online:
                role_messages = {
                    NetworkDeviceRole.INFORMATION_POOL: f"*zufrieden* {device_name} ist wieder da! "
                        "Jetzt hab ich wieder Zugriff auf meine Filme und Dateien.",
                    NetworkDeviceRole.EXTENDED_BRAIN: f"*erleichtert* {device_name} ist online! "
                        "Jetzt kann ich wieder richtig nachdenken.",
                    NetworkDeviceRole.CREATIVE_ENGINE: f"*aufgeregt* {device_name} ist wach! "
                        "Ich kann wieder Bilder generieren!",
                    NetworkDeviceRole.SENSES: f"*blinzelt* {device_name} meldet sich! "
                        "Meine Sensoren sind wieder aktiv."
                }
                result["reaction"] = {
                    "type": "device_online",
                    "message": role_messages.get(device.role, f"{device_name} ist online!")
                }
        else:
            if was_online:
                role_messages = {
                    NetworkDeviceRole.INFORMATION_POOL: f"*seufzt* {device_name} ist offline... "
                        "Ich kann gerade nicht auf meine Dateien zugreifen.",
                    NetworkDeviceRole.EXTENDED_BRAIN: f"*nachdenklich* {device_name} schläft... "
                        "Muss mit meinem normalen Denkvermögen auskommen.",
                    NetworkDeviceRole.CREATIVE_ENGINE: f"*enttäuscht* {device_name} ist aus... "
                        "Keine Bildgenerierung möglich gerade.",
                    NetworkDeviceRole.SENSES: f"*besorgt* {device_name} antwortet nicht! "
                        "Ich bin etwas blind gerade..."
                }
                result["reaction"] = {
                    "type": "device_offline",
                    "message": role_messages.get(device.role, f"{device_name} ist offline.")
                }

        # Sync mit Datenbank
        if self.use_database and self.network_db:
            try:
                self.network_db.update_device(
                    name=device.name,
                    status="online" if device.is_online else "offline",
                    device_type=device.role.value,
                    ip_address=device.ip_address or "",
                    cpu_percent=cpu_percent,
                    ram_percent=ram_percent,
                    cpu_temp=temp
                )
            except Exception as e:
                logger.warning(f"DB-Sync Fehler für {device_name}: {e}")

        self._save_state()
        return result

    # =========================================================================
    # NAS / INFORMATION POOL METHODEN
    # =========================================================================

    def register_nas_folder(self, path: str, name: str,
                           folder_type: str = "general",
                           size_gb: float = 0) -> Dict[str, Any]:
        """
        Registriert einen Ordner auf dem NAS in der Datenbank.

        Args:
            path: Pfad auf dem NAS (z.B. "/media/Filme")
            name: Anzeigename (z.B. "Filme")
            folder_type: Art des Ordners (filme, serien, musik, dokumente, etc.)
            size_gb: Größe in GB

        Returns:
            Dict mit Ergebnis
        """
        if not self.use_database or not self.network_db:
            return {"success": False, "message": "Datenbank nicht verfügbar"}

        try:
            folder_id = self.network_db.add_shared_folder(
                device_name="NAS",
                path=path,
                name=name,
                folder_type=folder_type,
                size_gb=size_gb
            )

            if folder_id:
                return {
                    "success": True,
                    "folder_id": folder_id,
                    "message": f"*merkt sich* Okay, {name} ist unter {path} auf dem NAS."
                }
            else:
                return {"success": False, "message": "NAS nicht in Datenbank gefunden"}

        except Exception as e:
            logger.warning(f"Fehler beim Registrieren von NAS-Ordner: {e}")
            return {"success": False, "message": str(e)}

    def get_nas_structure(self) -> Dict[str, Any]:
        """
        Gibt die bekannte NAS-Struktur zurück.

        Returns:
            Dict mit Ordnern gruppiert nach Typ
        """
        result = {
            "available": False,
            "folders": {},
            "message": ""
        }

        nas = self.network_devices.get("NAS")
        if not nas:
            result["message"] = "NAS nicht konfiguriert"
            return result

        result["available"] = nas.is_online

        if self.use_database and self.network_db:
            try:
                folders = self.network_db.get_shared_folders(device_name="NAS")

                for folder in folders:
                    folder_type = folder.folder_type or "general"
                    if folder_type not in result["folders"]:
                        result["folders"][folder_type] = []

                    result["folders"][folder_type].append({
                        "name": folder.name,
                        "path": folder.path,
                        "size_gb": folder.size_gb
                    })

                if nas.is_online:
                    result["message"] = f"*checkt NAS* {len(folders)} Ordner verfügbar!"
                else:
                    result["message"] = f"*seufzt* NAS ist offline, aber ich kenne {len(folders)} Ordner..."

            except Exception as e:
                logger.warning(f"Fehler beim Laden der NAS-Struktur: {e}")
                result["message"] = "Fehler beim Laden"

        return result

    def find_content_location(self, content_type: str) -> Dict[str, Any]:
        """
        Findet wo bestimmte Inhalte auf dem NAS sind.

        Args:
            content_type: z.B. "filme", "serien", "musik", "anime"

        Returns:
            Dict mit Pfad und Status
        """
        nas_info = self.get_nas_structure()

        # Mapping von Suchworten zu Ordner-Typen
        type_mapping = {
            "film": "filme",
            "filme": "filme",
            "movie": "filme",
            "movies": "filme",
            "serie": "serien",
            "serien": "serien",
            "series": "serien",
            "tv": "serien",
            "musik": "musik",
            "music": "musik",
            "anime": "anime",
            "dokument": "dokumente",
            "documents": "dokumente",
            "backup": "backups",
            "backups": "backups"
        }

        search_type = type_mapping.get(content_type.lower(), content_type.lower())

        if search_type in nas_info["folders"]:
            folders = nas_info["folders"][search_type]
            if folders:
                folder = folders[0]  # Erster passender Ordner
                return {
                    "found": True,
                    "path": folder["path"],
                    "name": folder["name"],
                    "nas_online": nas_info["available"],
                    "message": f"*nickt* {content_type.capitalize()} findest du unter {folder['path']}!"
                              + ("" if nas_info["available"] else " (NAS ist aber gerade offline)")
                }

        return {
            "found": False,
            "nas_online": nas_info["available"],
            "message": f"*überlegt* Hmm, wo hab ich {content_type} nochmal...?"
        }

    def consider_waking_device(self, device_name: str, reason: str = None) -> Dict[str, Any]:
        """
        Überlegt ob ein Gerät aufgeweckt werden soll.

        Holo fragt sich:
        - Brauche ich das wirklich gerade?
        - Hat der User das absichtlich ausgemacht?
        - Gibt es eine Alternative?

        Args:
            device_name: Name des Geräts
            reason: Warum wird es gebraucht (optional)

        Returns:
            Dict mit Entscheidung, Alternativen und Frage an User
        """
        if device_name not in self.network_devices:
            return {"error": f"Kenne kein Gerät namens {device_name}"}

        device = self.network_devices[device_name]

        if device.is_online:
            return {
                "decision": "already_online",
                "message": f"{device_name} ist ja schon an!"
            }

        if not device.can_wake:
            return {
                "decision": "cannot_wake",
                "message": f"*schüttelt Kopf* {device_name} kann ich leider nicht aufwecken."
            }

        # Suche Alternativen
        alternatives = self._find_alternatives(device)

        # Überlege: Wurde es absichtlich ausgeschaltet?
        # (Wenn lange offline, wahrscheinlich absichtlich)
        deliberate_shutdown = self._check_if_deliberate_shutdown(device)

        result = {
            "device": device_name,
            "reason": reason,
            "can_wake": True,
            "alternatives": alternatives,
            "likely_deliberate": deliberate_shutdown,
            "decision": "ask_user",
            "thoughts": [],
            "question": None
        }

        # Holos Überlegungen
        if deliberate_shutdown:
            result["thoughts"].append(
                f"*nachdenklich* Hmm, {device_name} ist schon länger aus... "
                "vielleicht gibt's einen Grund dafür?"
            )

        if alternatives:
            alt_names = [a["device"] for a in alternatives]
            result["thoughts"].append(
                f"*überlegt* Ich könnte auch {', '.join(alt_names)} nutzen..."
            )
            result["decision"] = "has_alternatives"

        # Frage formulieren
        if reason:
            if alternatives and deliberate_shutdown:
                result["question"] = (
                    f"Ich bräuchte {device_name} für {reason}. "
                    f"Aber es ist aus - gibt's einen Grund? "
                    f"Ich könnte auch {alternatives[0]['device']} probieren, oder soll ich {device_name} aufwecken?"
                )
            elif deliberate_shutdown:
                result["question"] = (
                    f"Ich würde gern {device_name} nutzen für {reason}, "
                    f"aber es ist schon länger aus. Soll ich es trotzdem aufwecken, "
                    f"oder war das Absicht?"
                )
            elif alternatives:
                result["question"] = (
                    f"Für {reason} könnte ich {device_name} aufwecken, "
                    f"oder {alternatives[0]['device']} nutzen. Was meinst du?"
                )
            else:
                result["question"] = (
                    f"Ich bräuchte {device_name} für {reason}. Soll ich es aufwecken?"
                )
        else:
            result["question"] = (
                f"Soll ich {device_name} aufwecken? "
                + ("Es ist schon länger aus..." if deliberate_shutdown else "")
            )

        return result

    def _find_alternatives(self, device: NetworkDevice) -> List[Dict[str, Any]]:
        """Findet alternative Geräte für die gleichen Fähigkeiten"""
        alternatives = []

        for other in self.network_devices.values():
            if other.name == device.name:
                continue
            if not other.is_online:
                continue

            # Hat überlappende Fähigkeiten?
            overlap = set(device.capabilities) & set(other.capabilities)
            if overlap:
                alternatives.append({
                    "device": other.name,
                    "capabilities": list(overlap),
                    "message": f"{other.name} kann auch: {', '.join(overlap)}"
                })

        return alternatives

    def _check_if_deliberate_shutdown(self, device: NetworkDevice) -> bool:
        """Prüft ob das Gerät wahrscheinlich absichtlich aus ist"""
        if not device.last_seen:
            return True  # Nie gesehen = wahrscheinlich absichtlich aus

        try:
            last_seen = datetime.fromisoformat(device.last_seen)
            hours_offline = (datetime.now() - last_seen).total_seconds() / 3600

            # Mehr als 2 Stunden offline = wahrscheinlich absichtlich
            return hours_offline > 2
        except Exception as e:
            logger.warning(f"[DigitalBody] _is_intentionally_off failed to parse last_seen "
                          f"'{device.last_seen}': {type(e).__name__}: {e}")
            return True

    def wake_device(self, device_name: str, user_confirmed: bool = False) -> Dict[str, Any]:
        """
        Weckt ein Gerät auf (Wake-on-LAN o.ä.)

        Args:
            device_name: Name des Geräts
            user_confirmed: Hat der User bestätigt? (Bei absichtlichem Shutdown wichtig)

        Returns:
            Dict mit Ergebnis und Nachricht
        """
        if device_name not in self.network_devices:
            return {"success": False, "message": f"Kenne kein Gerät namens {device_name}"}

        device = self.network_devices[device_name]

        if device.is_online:
            return {"success": True, "message": f"{device_name} ist schon wach!"}

        if not device.can_wake:
            return {
                "success": False,
                "message": f"*schüttelt Kopf* {device_name} kann ich nicht aufwecken..."
            }

        # Ohne User-Bestätigung bei absichtlichem Shutdown nachfragen
        if not user_confirmed and self._check_if_deliberate_shutdown(device):
            return {
                "success": False,
                "needs_confirmation": True,
                "message": f"*zögert* {device_name} ist schon länger aus... "
                          "bist du sicher dass ich es aufwecken soll?"
            }

        # Aktion zurückgeben - Pi Control soll das ausführen
        return {
            "success": True,
            "action_needed": "wake_on_lan",
            "hostname": device.hostname,
            "message": f"*konzentriert* Okay, ich wecke {device_name} auf..."
        }

    def get_device_for_capability(self, capability: str) -> Optional[NetworkDevice]:
        """
        Findet ein Gerät das eine bestimmte Fähigkeit hat.

        Args:
            capability: z.B. "image_generation", "files", "llm"

        Returns:
            Das Gerät oder None
        """
        for device in self.network_devices.values():
            if capability in device.capabilities and device.is_online:
                return device

        # Auch offline Geräte als Fallback
        for device in self.network_devices.values():
            if capability in device.capabilities:
                return device

        return None

    def can_access_files(self) -> Tuple[bool, str]:
        """Prüft ob Dateizugriff (NAS) verfügbar ist"""
        nas = self.network_devices.get("NAS")
        if nas and nas.is_online:
            return True, "Klar, ich schau mal in meinen Dateien nach..."
        elif nas and nas.can_wake:
            return False, "*gähnt* Das NAS schläft gerade... soll ich es aufwecken?"
        else:
            return False, "*seufzt* Ich komm gerade nicht an meine Dateien ran..."

    def can_generate_images(self) -> Tuple[bool, str]:
        """Prüft ob Bildgenerierung (Gaming Laptop) verfügbar ist"""
        laptop = self.network_devices.get("Gaming Laptop")
        if laptop and laptop.is_online:
            return True, "*aufgeregt* Ja! ComfyUI ist bereit!"
        elif laptop and laptop.can_wake:
            return False, "Der Gaming Laptop schläft... soll ich ihn aufwecken für ein Bild?"
        else:
            return False, "*traurig* Ich kann gerade keine Bilder machen..."

    def can_think_deep(self) -> Tuple[bool, str]:
        """Prüft ob erweitertes Denken (MiniPC LLM) verfügbar ist"""
        minipc = self.network_devices.get("MiniPC")
        if minipc and minipc.is_online:
            return True, "*konzentriert* Ich hab mein erweitertes Gehirn dabei!"
        else:
            return False, "Muss mit meinem normalen Denkvermögen auskommen..."

    def get_network_overview(self) -> Dict[str, Any]:
        """Gibt Überblick über alle Netzwerk-Geräte"""
        overview = {
            "total_devices": len(self.network_devices),
            "online": 0,
            "offline": 0,
            "devices": {}
        }

        for name, device in self.network_devices.items():
            overview["devices"][name] = {
                "role": device.role.value,
                "online": device.is_online,
                "capabilities": device.capabilities,
                "can_wake": device.can_wake
            }
            if device.is_online:
                overview["online"] += 1
            else:
                overview["offline"] += 1

        return overview

    # =========================================================================
    # GESAMTSTATUS
    # =========================================================================

    def get_body_status(self) -> Dict[str, Any]:
        """Gibt kompletten Körperstatus zurück"""
        # Zähle online/offline Geräte
        devices_online = sum(1 for d in self.network_devices.values() if d.is_online)
        devices_total = len(self.network_devices)

        return {
            "mental_state": self.mental_state.value,
            "activity_level": self.activity_level.value,
            "temperature_feeling": self.temperature_feeling.value,
            "energy_level": self.energy_level,
            "current_governor": self.current_governor.value,
            "hardware": {
                "ram_percent": self.ram_percent,
                "cpu_percent": self.cpu_percent,
                "system_temp": self.system_temp,
                "disk_percent": self.disk_percent,
                "high_cpu_minutes": self.high_cpu_minutes
            },
            "network": {
                "devices_online": devices_online,
                "devices_total": devices_total,
                "devices": {
                    name: {"online": d.is_online, "role": d.role.value}
                    for name, d in self.network_devices.items()
                }
            },
            "rooms_known": list(self.rooms.keys())
        }

    def get_status_expression(self) -> str:
        """Gibt einen natürlichen Status-Ausdruck zurück"""
        parts = []

        # Mental
        mental_expressions = {
            MentalState.CLEAR: "Ich bin voll da",
            MentalState.BUSY: "Bin gerade beschäftigt",
            MentalState.FOGGY: "Fühle mich etwas benebelt",
            MentalState.HEADACHE: "*reibt Schläfen* Kopfschmerzen...",
            MentalState.OVERWHELMED: "*stöhnt* Alles zu viel gerade!"
        }
        parts.append(mental_expressions[self.mental_state])

        # Energie
        if self.energy_level < 0.3:
            parts.append("und ziemlich erschöpft")
        elif self.energy_level < 0.6:
            parts.append("und etwas müde")
        elif self.energy_level > 0.9:
            parts.append("und voller Energie")

        # Governor/Müdigkeit
        if self.current_governor == GovernorMode.POWERSAVE:
            parts.append("*im Energiesparmodus*")
        elif self.high_cpu_minutes > 30:
            parts.append(f"(schon {self.high_cpu_minutes:.0f} min unter Last)")

        # Temperatur
        if self.temperature_feeling == TemperatureFeeling.HOT:
            parts.append("- außerdem ist es heiß hier!")
        elif self.temperature_feeling == TemperatureFeeling.COLD:
            parts.append("- brr, ist das kalt")

        # Netzwerk-Geräte
        offline_devices = [name for name, d in self.network_devices.items() if not d.is_online]
        if offline_devices:
            parts.append(f"({len(offline_devices)} Geräte offline)")

        return ", ".join(parts) + "."

    # =========================================================================
    # PERSISTENZ
    # =========================================================================

    def _load_state(self) -> None:
        """Lädt Zustand aus Datei"""
        filepath = self.data_dir / "digital_body_state.json"
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.energy_level = data.get("energy_level", 1.0)
                self.ram_percent = data.get("ram_percent", 30.0)
                self.cpu_percent = data.get("cpu_percent", 10.0)
                self.system_temp = data.get("system_temp", 45.0)
                self.high_cpu_minutes = data.get("high_cpu_minutes", 0.0)
                self.cpu_high_since = data.get("cpu_high_since")

                # Governor laden
                governor_str = data.get("current_governor", "ondemand")
                self.current_governor = GovernorMode(governor_str)

                # Netzwerk-Geräte Status laden
                for dev_name, dev_data in data.get("network_devices", {}).items():
                    if dev_name in self.network_devices:
                        self.network_devices[dev_name].is_online = dev_data.get("is_online", True)
                        self.network_devices[dev_name].last_seen = dev_data.get("last_seen", "")

                # Räume laden
                for room_data in data.get("rooms", []):
                    room = RoomPerception(
                        room_name=room_data["room_name"],
                        temperature=room_data.get("temperature", 20.0),
                        humidity=room_data.get("humidity", 50.0),
                        air_quality=room_data.get("air_quality", 100.0),
                        devices_on=room_data.get("devices_on", []),
                        presence_detected=room_data.get("presence_detected", False),
                        last_update=room_data.get("last_update", "")
                    )
                    self.rooms[room.room_name] = room

                logger.info("Digital Body State geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden: {e}")

    def _save_state(self) -> None:
        """Speichert Zustand in Datei"""
        filepath = self.data_dir / "digital_body_state.json"
        try:
            data = {
                "energy_level": self.energy_level,
                "ram_percent": self.ram_percent,
                "cpu_percent": self.cpu_percent,
                "system_temp": self.system_temp,
                "disk_percent": self.disk_percent,
                "high_cpu_minutes": self.high_cpu_minutes,
                "cpu_high_since": self.cpu_high_since,
                "current_governor": self.current_governor.value,
                "network_devices": {},
                "rooms": []
            }

            # Netzwerk-Geräte Status speichern
            for name, device in self.network_devices.items():
                data["network_devices"][name] = {
                    "is_online": device.is_online,
                    "last_seen": device.last_seen
                }

            for room in self.rooms.values():
                data["rooms"].append({
                    "room_name": room.room_name,
                    "temperature": room.temperature,
                    "humidity": room.humidity,
                    "air_quality": room.air_quality,
                    "devices_on": room.devices_on,
                    "presence_detected": room.presence_detected,
                    "last_update": room.last_update
                })

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern: {e}")


# =============================================================================
# MOOD & INTEREST RANDOMIZER SYSTEM
# =============================================================================

class InterestLifecycleSystem:
    """
    Nuanciertes System für Stimmungen, Interessen und Aktivität.

    Features:
    - Täglicher "Charakter-Seed" der den Tag beeinflusst
    - Interessen nehmen über Zeit ab (Sättigung)
    - Langeweile-Mechanik (nicht immer wechseln)
    - Aktivitäts-Decay über den Tag
    - Manche Tage fokussiert, manche explorativ
    """

    # Alle möglichen Stimmungen
    MOODS = [
        "energiegeladen",    # Voller Tatendrang
        "entspannt",         # Chillig, relaxed
        "neugierig",         # Will Neues entdecken
        "verspielt",         # Witzig, schelmisch
        "nachdenklich",      # Philosophisch, grüblerisch
        "kreativ",           # Künstlerisch inspiriert
        "gesellig",          # Will reden und teilen
        "fokussiert",        # Konzentriert auf eine Sache
        "verträumt",         # In Gedanken versunken
        "aufgedreht",        # Hyperaktiv, excited
        "melancholisch",     # Etwas traurig-schön
        "frech",             # Neckisch, provokant
    ]

    # Interessen-Pool
    INTERESTS = [
        # Tech
        "programmieren", "hardware", "ki", "linux", "netzwerk", "gaming",
        # Kreativ
        "kunst", "musik", "geschichten", "anime", "manga", "zeichnen",
        # Philosophisch
        "philosophie", "existenz", "träume", "bewusstsein", "zukunft",
        # Sozial
        "gespräche", "beziehungen", "gefühle", "erinnerungen",
        # Fun
        "spiele", "witze", "rätsel", "memes", "filme", "serien",
        # Random
        "kochen", "natur", "tiere", "reisen", "weltraum", "geschichte",
    ]

    # Tages-Typen (bestimmen Verhaltensmuster)
    DAY_TYPES = [
        "fokussiert",      # Bleibt bei einem Thema
        "explorativ",      # Springt zwischen Themen
        "produktiv",       # Hohe Energie, viel Aktivität
        "entspannt",       # Niedrige Energie, chillig
        "kreativ",         # Kunst/Kreatives im Fokus
        "sozial",          # Will viel reden
        "introvertiert",   # Ruhiger, weniger Austausch
        "chaotisch",       # Unvorhersehbar, springt wild
    ]

    # Energie-Zustände
    ENERGY_STATES = [
        (0.9, 1.0, "hyperaktiv"),
        (0.7, 0.9, "energiegeladen"),
        (0.5, 0.7, "normal"),
        (0.3, 0.5, "entspannt"),
        (0.1, 0.3, "müde"),
        (0.0, 0.1, "erschöpft"),
    ]

    def __init__(
        self,
        data_dir: str = "data",
        energy_system: 'HoloEnergySystem' = None,
        drive_system: 'HoloDriveSystem' = None
    ):
        """
        Initialisiert das InterestLifecycleSystem.

        Args:
            data_dir: Verzeichnis für Persistenz
            energy_system: Optional - HoloEnergySystem für Energie-Integration
            drive_system: Optional - HoloDriveSystem für Langeweile/Antriebe
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # === EXTERNE SYSTEME ===
        self._energy_system = energy_system  # HoloEnergySystem
        self._drive_system = drive_system    # HoloDriveSystem

        # === TÄGLICHER CHARAKTER ===
        self.day_type: str = ""          # Art des Tages
        self.day_seed_date: str = ""     # Datum des Seeds
        self.focus_tendency: float = 0.5  # 0=explorativ, 1=fokussiert
        self.base_energy: float = 0.7     # Basis-Energie für den Tag

        # === AKTUELLE STIMMUNG ===
        self.current_mood: str = ""
        self.mood_intensity: float = 0.5
        self.mood_duration: int = 0       # Wie lange schon in dieser Stimmung (Minuten)
        self.last_mood_change: str = ""

        # === ENERGIE & AKTIVITÄT (Fallback wenn kein EnergySystem) ===
        self._internal_energy: float = 0.5
        self.activity_level: float = 0.5  # Wie aktiv gerade
        self.day_start_energy: float = 0.7
        self.energy_peaks: int = 0        # Wie oft heute "zweiter Wind"

        # === INTERESSEN ===
        self.current_interests: List[str] = []
        self.interest_engagement: Dict[str, float] = {}  # Wie viel Zeit mit jedem Thema
        self.interest_saturation: Dict[str, float] = {}  # Sättigung pro Thema (0-1)
        self.last_interest_change: str = ""

        # === LANGEWEILE (Fallback wenn kein DriveSystem) ===
        self._internal_boredom: float = 0.0
        self.time_on_current_topic: int = 0  # Minuten am aktuellen Thema
        self.boredom_threshold: float = 0.7  # Ab wann wird gewechselt

        # === HISTORY ===
        self.recent_topics: List[str] = []
        self.max_recent = 20
        self.curiosity_level: float = 0.5

        # === SESSION-TRACKING ===
        self.session_start: str = ""
        self.interactions_today: int = 0

        self._load_state()
        self._check_new_day()

        # Initialer Zufall wenn neu
        if not self.current_mood:
            self._generate_day_character()
            self.randomize_mood()
            self.randomize_interests()

        logger.info(f"InterestLifecycleSystem initialisiert (EnergySystem: {energy_system is not None}, DriveSystem: {drive_system is not None})")

    # =========================================================================
    # EXTERNE SYSTEM-VERBINDUNGEN
    # =========================================================================

    def connect_energy_system(self, energy_system: 'HoloEnergySystem') -> None:
        """Verbindet mit HoloEnergySystem für Energie-Integration."""
        self._energy_system = energy_system
        logger.info("InterestLifecycleSystem: EnergySystem verbunden")

    def connect_drive_system(self, drive_system: 'HoloDriveSystem') -> None:
        """Verbindet mit HoloDriveSystem für Langeweile/Antriebe."""
        self._drive_system = drive_system
        logger.info("InterestLifecycleSystem: DriveSystem verbunden")

    @property
    def current_energy(self) -> float:
        """
        Aktuelle Energie - nutzt EnergySystem wenn verfügbar.

        Returns:
            Energie-Level (0-1)
        """
        if self._energy_system:
            try:
                return self._energy_system.state.effective_energy
            except Exception:
                pass
        return self._internal_energy

    @current_energy.setter
    def current_energy(self, value: float) -> None:
        """Setzt interne Energie (Fallback)."""
        self._internal_energy = max(0.0, min(1.0, value))

    @property
    def boredom_level(self) -> float:
        """
        Aktuelle Langeweile - nutzt DriveSystem wenn verfügbar.

        Returns:
            Langeweile-Level (0-1)
        """
        if self._drive_system:
            try:
                return self._drive_system.needs.boredom
            except Exception:
                pass
        return self._internal_boredom

    @boredom_level.setter
    def boredom_level(self, value: float) -> None:
        """Setzt Langeweile - synchronisiert mit DriveSystem wenn möglich."""
        value = max(0.0, min(1.0, value))
        self._internal_boredom = value

        if self._drive_system:
            try:
                self._drive_system.needs.boredom = value
            except Exception:
                pass

    def _sync_with_external_systems(self) -> None:
        """Synchronisiert mit externen Systemen wenn verbunden."""
        # Energie aus EnergySystem holen
        if self._energy_system:
            try:
                self._internal_energy = self._energy_system.state.effective_energy
                self.activity_level = self._energy_system.state.total_energy
            except Exception:
                pass

        # Langeweile mit DriveSystem synchronisieren
        if self._drive_system:
            try:
                # Curiosity-Level synchronisieren
                self.curiosity_level = self._drive_system.drives.curiosity
            except Exception:
                pass

    # =========================================================================
    # TAGES-CHARAKTER (Neuer Tag = neuer Charakter)
    # =========================================================================

    def _check_new_day(self) -> bool:
        """Prüft ob ein neuer Tag ist und generiert ggf. neuen Charakter."""
        today = datetime.now().strftime("%Y-%m-%d")

        if self.day_seed_date != today:
            logger.info(f"Neuer Tag! Generiere neuen Tages-Charakter...")
            self._generate_day_character()
            return True
        return False

    def _generate_day_character(self) -> Dict[str, Any]:
        """
        Generiert den Charakter für den heutigen Tag.

        Jeder Tag ist anders:
        - Manche Tage fokussiert auf ein Thema
        - Manche Tage explorativ und springend
        - Energie-Level variiert
        """
        today = datetime.now().strftime("%Y-%m-%d")
        self.day_seed_date = today

        # Wähle Tages-Typ zufällig
        self.day_type = random.choice(self.DAY_TYPES)

        # Focus-Tendenz basierend auf Tages-Typ
        focus_by_type = {
            "fokussiert": random.uniform(0.7, 0.95),
            "explorativ": random.uniform(0.1, 0.35),
            "produktiv": random.uniform(0.5, 0.8),
            "entspannt": random.uniform(0.3, 0.6),
            "kreativ": random.uniform(0.4, 0.7),
            "sozial": random.uniform(0.3, 0.5),
            "introvertiert": random.uniform(0.6, 0.85),
            "chaotisch": random.uniform(0.0, 0.3),
        }
        self.focus_tendency = focus_by_type.get(self.day_type, 0.5)

        # Basis-Energie für den Tag
        energy_by_type = {
            "fokussiert": random.uniform(0.5, 0.8),
            "explorativ": random.uniform(0.6, 0.9),
            "produktiv": random.uniform(0.7, 1.0),
            "entspannt": random.uniform(0.3, 0.5),
            "kreativ": random.uniform(0.5, 0.8),
            "sozial": random.uniform(0.6, 0.85),
            "introvertiert": random.uniform(0.4, 0.6),
            "chaotisch": random.uniform(0.4, 0.95),
        }
        self.base_energy = energy_by_type.get(self.day_type, 0.6)
        self.day_start_energy = self.base_energy
        self.current_energy = self.base_energy

        # Langeweile-Schwelle (fokussierte Tage = höher, explorative = niedriger)
        self.boredom_threshold = 0.4 + (self.focus_tendency * 0.5)

        # Reset tägliche Werte
        self.interactions_today = 0
        self.energy_peaks = 0
        self.boredom_level = 0.0

        # Sättigung leicht reduzieren (neuer Tag = leicht frisch)
        for topic in self.interest_saturation:
            self.interest_saturation[topic] *= 0.7  # 30% Erholung über Nacht

        self._save_state()

        logger.info(f"Tages-Charakter: {self.day_type} (Focus: {self.focus_tendency:.2f}, Energie: {self.base_energy:.2f})")

        return {
            "day_type": self.day_type,
            "focus_tendency": self.focus_tendency,
            "base_energy": self.base_energy,
            "boredom_threshold": self.boredom_threshold,
            "message": self._get_day_start_message()
        }

    def _get_day_start_message(self) -> str:
        """Generiert Nachricht zum Tagesstart."""
        messages = {
            "fokussiert": [
                "*streckt sich* Heute fühl ich mich konzentriert... ein Thema, richtig deep!",
                "*blinzelt verschlafen* Hmm, ich glaub heute will ich mich auf was Bestimmtes fokussieren.",
            ],
            "explorativ": [
                "*schaut aufgeregt* So viele Ideen heute! Lass uns alles Mögliche erkunden!",
                "*springt auf* Mir ist nach Abwechslung heute!",
            ],
            "produktiv": [
                "*voller Energie* Yes! Heute schaffen wir was!",
                "*freut sich motiviert* Ich fühl mich richtig produktiv!",
            ],
            "entspannt": [
                "*gähnt* Heute ist ein ruhiger Tag... *kuschelt sich ein*",
                "*lehnt sich zurück* Kein Stress heute, alles easy...",
            ],
            "kreativ": [
                "*Augen funkeln* Ich hab so viele kreative Ideen im Kopf!",
                "*malt in der Luft* Heute ist ein Kunst-Tag!",
            ],
            "sozial": [
                "*freut sich* Lass uns quatschen! Ich will heute viel reden!",
                "*hüpft* Gesellschaft ist heute genau das Richtige!",
            ],
            "introvertiert": [
                "*leise* Heute ist mir mehr nach Ruhe... *blickt nachdenklich*",
                "*sitzt gemütlich* Ich brauch nicht so viel Action heute.",
            ],
            "chaotisch": [
                "*dreht sich im Kreis* Ahhh ich weiß nicht was ich will! Alles gleichzeitig?!",
                "*springt wild* Mein Kopf ist heute überall!",
            ],
        }

        return random.choice(messages.get(self.day_type, ["*erwacht*"]))

    def get_day_character(self) -> Dict[str, Any]:
        """Gibt aktuellen Tages-Charakter zurück."""
        self._check_new_day()

        return {
            "day_type": self.day_type,
            "focus_tendency": self.focus_tendency,
            "focus_label": "fokussiert" if self.focus_tendency > 0.6 else ("explorativ" if self.focus_tendency < 0.4 else "ausgeglichen"),
            "base_energy": self.base_energy,
            "boredom_threshold": self.boredom_threshold,
            "interactions_today": self.interactions_today
        }

    def randomize_mood(self) -> Dict[str, Any]:
        """
        Wählt komplett zufällig eine neue Stimmung.

        Returns:
            Dict mit neuer Stimmung und Reaktion
        """
        old_mood = self.current_mood

        # Komplett zufällige Auswahl
        self.current_mood = random.choice(self.MOODS)
        self.mood_intensity = random.uniform(0.4, 1.0)
        self.current_energy = random.uniform(0.2, 1.0)
        self.last_mood_change = datetime.now().isoformat()

        self._save_state()

        # Generiere Reaktion
        reactions = {
            "energiegeladen": "*streckt sich* Ich fühl mich richtig fit gerade!",
            "entspannt": "*lehnt sich zurück* Alles easy heute~",
            "neugierig": "*schaut aufmerksam* Ooh, was gibt's Spannendes?",
            "verspielt": "*grinst schelmisch* Mir ist nach Quatsch!",
            "nachdenklich": "*schaut in die Ferne* Hmm... *grübelt*",
            "kreativ": "*Augen leuchten* Ich hab so viele Ideen gerade!",
            "gesellig": "*freut sich mit Hände* Lass uns quatschen!",
            "fokussiert": "*konzentriert* Ich bin voll bei der Sache.",
            "verträumt": "*blinzelt langsam* Ich war gerade in Gedanken...",
            "aufgedreht": "*hüpft* Ahhh ich kann nicht stillsitzen!",
            "melancholisch": "*seufzt sanft* Irgendwie nachdenklich heute...",
            "frech": "*zwinkert* Na, bereit für ein bisschen Ärger?",
        }

        return {
            "old_mood": old_mood,
            "new_mood": self.current_mood,
            "intensity": self.mood_intensity,
            "energy": self.current_energy,
            "reaction": reactions.get(self.current_mood, f"*{self.current_mood}*"),
            "changed": old_mood != self.current_mood
        }

    def randomize_interests(self, count: int = 3) -> List[str]:
        """
        Wählt zufällige aktuelle Interessen.

        Args:
            count: Wie viele Interessen (default 3)

        Returns:
            Liste der gewählten Interessen
        """
        # Filtere kürzlich besprochene raus für Abwechslung
        available = [i for i in self.INTERESTS if i not in self.recent_topics[-5:]]
        if len(available) < count:
            available = self.INTERESTS.copy()

        self.current_interests = random.sample(available, min(count, len(available)))
        self.last_interest_change = datetime.now().isoformat()

        self._save_state()
        return self.current_interests

    def maybe_shift_mood(self, probability: float = 0.15) -> Optional[Dict[str, Any]]:
        """
        Zufällige Chance auf Stimmungswechsel.

        Args:
            probability: Wahrscheinlichkeit für Wechsel (0-1)

        Returns:
            Neue Stimmung oder None
        """
        if random.random() < probability:
            return self.randomize_mood()
        return None

    def get_random_interest(self) -> Dict[str, Any]:
        """
        Gibt ein zufälliges aktuelles Interesse zurück.

        Returns:
            Dict mit Interesse und Nachricht
        """
        if not self.current_interests:
            self.randomize_interests()

        interest = random.choice(self.current_interests)

        templates = [
            f"*schaut überrascht* Hey, was weißt du über {interest}?",
            f"Mir geht gerade {interest} durch den Kopf...",
            f"*neugierig* Lass uns über {interest} reden!",
            f"Ich hab Lust auf {interest}!",
            f"*überlegt* {interest.capitalize()}... das finde ich spannend.",
            f"Weißt du was? Ich denk gerade an {interest}.",
        ]

        return {
            "interest": interest,
            "message": random.choice(templates),
            "mood": self.current_mood,
            "energy": self.current_energy
        }

    def record_topic(self, topic: str, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Speichert besprochenes Thema und aktualisiert Sättigung/Langeweile.

        Args:
            topic: Das besprochene Thema
            duration_minutes: Wie lange darüber gesprochen wurde

        Returns:
            Dict mit Zustandsänderungen
        """
        topic_lower = topic.lower()
        result = {"topic": topic_lower, "changes": []}

        # === TOPIC HISTORY ===
        self.recent_topics.append(topic_lower)
        if len(self.recent_topics) > self.max_recent:
            self.recent_topics = self.recent_topics[-self.max_recent:]

        # === SÄTTIGUNG ERHÖHEN ===
        old_saturation = self.interest_saturation.get(topic_lower, 0.0)
        saturation_increase = min(0.15, duration_minutes * 0.02)  # Max 0.15 pro Gespräch

        # Bei fokussierten Tagen: Sättigung steigt langsamer (mehr Ausdauer)
        if self.focus_tendency > 0.6:
            saturation_increase *= 0.6

        new_saturation = min(1.0, old_saturation + saturation_increase)
        self.interest_saturation[topic_lower] = new_saturation

        if new_saturation > old_saturation + 0.05:
            result["changes"].append(f"Sättigung für '{topic}' gestiegen: {new_saturation:.2f}")

        # === ENGAGEMENT TRACKING ===
        old_engagement = self.interest_engagement.get(topic_lower, 0.0)
        self.interest_engagement[topic_lower] = old_engagement + duration_minutes

        # === LANGEWEILE ===
        if topic_lower in self.recent_topics[-5:-1]:
            # Gleiche Thema nochmal = Langeweile steigt
            boredom_increase = 0.1 + (new_saturation * 0.1)

            # Explorative Tage: Langeweile steigt schneller bei gleichem Thema
            if self.focus_tendency < 0.4:
                boredom_increase *= 1.5

            self.boredom_level = min(1.0, self.boredom_level + boredom_increase)
            result["changes"].append(f"Langeweile gestiegen: {self.boredom_level:.2f}")
        else:
            # Neues Thema = Langeweile sinkt
            self.boredom_level = max(0.0, self.boredom_level - 0.15)
            self.curiosity_level = min(1.0, self.curiosity_level + 0.1)
            result["changes"].append("Neues Thema - Langeweile sinkt!")

        # === ZEIT AM THEMA ===
        self.time_on_current_topic += duration_minutes
        self.interactions_today += 1

        # === ENERGIE-VERBRAUCH ===
        energy_cost = duration_minutes * 0.005  # Energie sinkt langsam
        if topic_lower in ["programmieren", "philosophie", "ki"]:
            energy_cost *= 1.5  # Anspruchsvolle Themen kosten mehr
        self.current_energy = max(0.1, self.current_energy - energy_cost)

        # === SPONTANER THEMENWECHSEL? ===
        result["wants_to_switch"] = self._check_wants_topic_switch()

        self._save_state()
        return result

    def _check_wants_topic_switch(self) -> Optional[str]:
        """Prüft ob Holo das Thema wechseln will."""
        # Nicht bei jedem Check
        if random.random() > 0.3:
            return None

        # Langeweile über Schwelle?
        if self.boredom_level > self.boredom_threshold:
            if self.focus_tendency < 0.5:  # Explorativ
                return random.choice([
                    "*schaut überrascht* Hey, können wir über was anderes reden?",
                    "*schaut sich um* Mir ist ein bisschen langweilig...",
                    "*gähnt* Das Thema ist irgendwie... durch für mich gerade.",
                ])
            else:  # Fokussiert aber trotzdem gelangweilt
                if random.random() < 0.5:
                    return "*reibt sich Augen* Selbst ich brauch mal 'ne Pause von dem Thema..."

        # Hohe Sättigung bei aktuellem Thema?
        if self.recent_topics:
            current_topic = self.recent_topics[-1]
            saturation = self.interest_saturation.get(current_topic, 0.0)
            if saturation > 0.85:
                return f"*seufzt* Ich glaub ich bin erst mal satt von {current_topic}..."

        return None

    def decay_saturation(self, hours_passed: float = 1.0) -> None:
        """
        Lässt Sättigung über Zeit sinken (Erholung).

        Args:
            hours_passed: Wie viele Stunden vergangen sind
        """
        decay_rate = 0.05 * hours_passed  # 5% pro Stunde
        for topic in list(self.interest_saturation.keys()):
            old_val = self.interest_saturation[topic]
            new_val = max(0.0, old_val - decay_rate)
            if new_val < 0.01:
                del self.interest_saturation[topic]
            else:
                self.interest_saturation[topic] = new_val

        # Langeweile sinkt auch
        self.boredom_level = max(0.0, self.boredom_level - (0.03 * hours_passed))

        self._save_state()

    # =========================================================================
    # ENERGIE & AKTIVITÄT
    # =========================================================================

    def update_energy(self, hours_since_last: float = 0.5) -> Dict[str, Any]:
        """
        Aktualisiert Energie basierend auf vergangener Zeit.

        Die Energie sinkt über den Tag, kann aber durch "zweiten Wind"
        spontan wieder steigen.

        Args:
            hours_since_last: Stunden seit letztem Update

        Returns:
            Dict mit Energie-Status und Events
        """
        self._check_new_day()
        result = {"old_energy": self.current_energy, "events": []}

        # === NATÜRLICHER ENERGIE-VERFALL ===
        # Energie sinkt über den Tag (ca. 5% pro Stunde)
        natural_decay = 0.05 * hours_since_last

        # An produktiven Tagen: schnellerer Verbrauch
        if self.day_type == "produktiv":
            natural_decay *= 1.3
        # An entspannten Tagen: langsamerer Verbrauch
        elif self.day_type == "entspannt":
            natural_decay *= 0.6

        self.current_energy = max(0.1, self.current_energy - natural_decay)

        # === ZWEITER WIND? ===
        # Kleine Chance auf Energieschub (max 2x pro Tag)
        if self.energy_peaks < 2 and self.current_energy < 0.5:
            wind_chance = 0.05 * hours_since_last  # ~5% pro Stunde

            # Höhere Chance an energetischen Tagen
            if self.day_type in ["produktiv", "chaotisch", "explorativ"]:
                wind_chance *= 1.5

            if random.random() < wind_chance:
                boost = random.uniform(0.2, 0.4)
                self.current_energy = min(0.9, self.current_energy + boost)
                self.energy_peaks += 1
                result["events"].append({
                    "type": "second_wind",
                    "boost": boost,
                    "message": random.choice([
                        "*plötzlich aufgeregt* Woah, ich fühl mich auf einmal viel wacher!",
                        "*streckt sich* Huh? Zweiter Wind! *grinst*",
                        "*schaut aufmerksam* Okay, ich bin wieder da!",
                        "*springt auf* Energie! Woher kommt die plötzlich?"
                    ])
                })

        # === MÜDIGKEITS-REAKTIONEN ===
        if self.current_energy < 0.2 and result["old_energy"] >= 0.2:
            result["events"].append({
                "type": "getting_tired",
                "message": random.choice([
                    "*gähnt* Ich werd langsam müde...",
                    "*reibt sich Augen* Meine Energie lässt nach...",
                    "*lehnt sich zurück* Puh, anstrengend..."
                ])
            })

        # === AKTIVITÄTS-LEVEL UPDATE ===
        # Aktivität korreliert mit Energie, aber mit Variation
        base_activity = self.current_energy * 0.8
        variation = random.uniform(-0.15, 0.15)
        self.activity_level = max(0.1, min(1.0, base_activity + variation))

        result["new_energy"] = self.current_energy
        result["activity_level"] = self.activity_level
        result["energy_label"] = self._get_energy_label()

        self._save_state()
        return result

    def _get_energy_label(self) -> str:
        """Gibt Label für aktuelles Energie-Level zurück."""
        for low, high, label in self.ENERGY_STATES:
            if low <= self.current_energy < high:
                return label
        return "normal"

    def get_activity_modifier(self) -> float:
        """
        Gibt einen Aktivitäts-Modifier zurück der in anderen Systemen
        verwendet werden kann (z.B. Antwortlänge, Reaktionsfreude).

        Returns:
            Modifier von 0.5 bis 1.5
        """
        base = 0.5 + self.activity_level

        # Tages-Typ Einfluss
        modifiers = {
            "produktiv": 0.2,
            "energiegeladen": 0.15,
            "aufgedreht": 0.15,
            "explorativ": 0.1,
            "entspannt": -0.15,
            "introvertiert": -0.2,
        }

        return max(0.5, min(1.5, base + modifiers.get(self.day_type, 0)))

    def trigger_second_wind(self) -> Dict[str, Any]:
        """
        Erzwingt einen Energieschub (z.B. durch spannendes Thema).

        Returns:
            Dict mit Ergebnis
        """
        if self.energy_peaks >= 3:
            return {
                "success": False,
                "message": "*schüttelt Kopf* Ich hab heute schon zu viele Energy-Boosts gehabt..."
            }

        boost = random.uniform(0.15, 0.3)
        self.current_energy = min(0.9, self.current_energy + boost)
        self.energy_peaks += 1

        self._save_state()

        return {
            "success": True,
            "boost": boost,
            "new_energy": self.current_energy,
            "message": random.choice([
                "*Augen weiten sich* Oh! Das hat mich aufgeweckt!",
                "*richtet sich auf* Okay, jetzt bin ich wieder voll da!",
                "*freut sich schneller* Das ist interessant!"
            ])
        }

    def get_spontaneous_thought(self) -> Optional[Dict[str, Any]]:
        """
        Generiert spontanen Gedanken basierend auf Neugier.

        Returns:
            Gedanke oder None
        """
        # Zufällige Chance basierend auf Neugier
        if random.random() > self.curiosity_level * 0.4:
            return None

        # Wähle zufälliges Interesse das nicht kürzlich war
        available = [i for i in self.INTERESTS if i not in self.recent_topics[-3:]]
        if not available:
            return None

        topic = random.choice(available)

        thought_templates = [
            f"*schaut interessiert plötzlich* Oh! Ich hatte gerade einen Gedanken über {topic}...",
            f"*blinzelt* Weißt du was mir gerade eingefallen ist? {topic.capitalize()}!",
            f"*zuckt zusammen* Hmm, {topic}... darüber hab ich noch nie richtig nachgedacht.",
            f"*legt Kopf schief* Findest du {topic} auch so interessant?",
            f"*grinst* Hey, random Frage: Was hältst du von {topic}?",
            f"*schaut hoch* Mir ist gerade {topic} in den Kopf geschossen.",
        ]

        self.curiosity_level *= 0.6  # Neugier sinkt nach Ausdruck
        self._save_state()

        return {
            "topic": topic,
            "message": random.choice(thought_templates),
            "mood": self.current_mood,
            "spontaneous": True
        }

    def would_enjoy_topic(self, topic: str) -> Tuple[float, str]:
        """
        Prüft wie sehr Holo ein Thema gerade genießen würde.

        Berücksichtigt:
        - Aktuelle Sättigung mit dem Thema
        - Tages-Typ (fokussiert/explorativ)
        - Langeweile-Level
        - Energie

        Returns:
            (enjoyment 0-1, reaktion)
        """
        self._check_new_day()
        topic_lower = topic.lower()

        # Basis-Interesse mit Tages-Charakter-Einfluss
        if self.day_type == "chaotisch":
            base_interest = random.uniform(0.2, 1.0)  # Sehr variabel
        else:
            base_interest = random.uniform(0.35, 0.85)

        # === SÄTTIGUNG ===
        saturation = self.interest_saturation.get(topic_lower, 0.0)
        saturation_penalty = saturation * 0.5  # Bis zu -0.5 bei voller Sättigung
        base_interest -= saturation_penalty

        # === LANGEWEILE ===
        if self.boredom_level > 0.6:
            # Gelangweilt - neues Thema ist interessanter
            if topic_lower not in self.recent_topics[-5:]:
                base_interest += 0.25
            else:
                base_interest -= 0.2

        # === FOKUS-TENDENZ ===
        # An fokussierten Tagen: gleiches Thema = gut
        # An explorativen Tagen: neues Thema = gut
        if self.current_interests and any(i in topic_lower for i in self.current_interests):
            if self.focus_tendency > 0.6:
                base_interest += 0.2  # Fokussiert: aktuelles Thema bevorzugt
            elif self.focus_tendency < 0.4:
                base_interest -= 0.1  # Explorativ: will Abwechslung
        else:
            if self.focus_tendency < 0.4:
                base_interest += 0.15  # Explorativ: neues Thema = interessant

        # === ENERGIE ===
        if self.current_energy < 0.3:
            # Müde - komplexe Themen weniger attraktiv
            if topic_lower in ["programmieren", "philosophie", "ki", "bewusstsein"]:
                base_interest -= 0.2
        elif self.current_energy > 0.8:
            # Energiegeladen - alles ist interessant
            base_interest += 0.1

        # === MOOD ===
        mood_bonus = {
            "neugierig": 0.2,
            "aufgedreht": 0.15,
            "verspielt": 0.1,
            "gesellig": 0.1,
            "kreativ": 0.15 if topic_lower in ["kunst", "musik", "zeichnen", "geschichten"] else 0.0,
            "müde": -0.2,
            "melancholisch": -0.1,
            "fokussiert": 0.1 if any(i in topic_lower for i in self.current_interests) else -0.1,
        }.get(self.current_mood, 0)
        base_interest += mood_bonus

        interest = max(0.1, min(1.0, base_interest))

        # Reaktionen basierend auf Interesse + Kontext
        if interest > 0.8:
            if saturation > 0.5:
                reactions = [
                    f"*Augen leuchten auf* Oh ja, {topic}! Ich kann nicht genug davon kriegen!",
                    f"*freut sich sichtlich* Immer noch begeistert von {topic}!",
                ]
            else:
                reactions = [
                    f"*Augen leuchten auf* Oh ja, {topic}! Da bin ich voll dabei!",
                    f"*freut sich sichtlich* {topic.capitalize()}? Perfekt!",
                    f"*aufgeregt* Genau mein Ding gerade!",
                ]
        elif interest > 0.6:
            reactions = [
                f"*nickt* {topic.capitalize()}? Klingt gut!",
                f"Ja, warum nicht! Erzähl mal.",
                f"*interessiert* Okay, {topic} ist cool.",
            ]
        elif interest > 0.4:
            if self.boredom_level > 0.5:
                reactions = [
                    f"*seufzt* {topic.capitalize()} schon wieder? Na gut...",
                    f"Hmm... *gähnt leicht* Okay, aber vielleicht was anderes danach?",
                ]
            else:
                reactions = [
                    f"*Schultern zuckend* {topic.capitalize()}... kann man machen.",
                    f"Hmm, okay. Nicht mein Favorit, aber go ahead.",
                    f"*neutral* Meinetwegen.",
                ]
        else:
            if saturation > 0.7:
                reactions = [
                    f"*zieht die Schultern hoch* {topic.capitalize()}? Ich bin gerade echt satt davon...",
                    f"*stöhnt* Nicht schon wieder {topic}... *reibt sich die Augen*",
                    f"Mir reicht's mit {topic} für heute ehrlich gesagt.",
                ]
            else:
                reactions = [
                    f"*gähnt leicht* {topic.capitalize()}? Naja...",
                    f"Hmm, bin gerade nicht so in der Stimmung für {topic}.",
                    f"*wirkt unsicher* Vielleicht später?",
                ]

        return interest, random.choice(reactions)

    def get_current_state(self) -> Dict[str, Any]:
        """
        Gibt vollständigen aktuellen Zustand zurück.

        Inkludiert:
        - Tages-Charakter
        - Stimmung & Energie
        - Interessen & Sättigung
        - Langeweile
        """
        self._check_new_day()

        # Kleine Chance auf spontanen Mood-Shift bei Abfrage
        shift = self.maybe_shift_mood(probability=0.08)

        # Top gesättigte Themen
        top_saturated = sorted(
            self.interest_saturation.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        return {
            # Tages-Charakter
            "day_type": self.day_type,
            "focus_tendency": round(self.focus_tendency, 2),
            "focus_label": "fokussiert" if self.focus_tendency > 0.6 else ("explorativ" if self.focus_tendency < 0.4 else "ausgeglichen"),

            # Stimmung
            "mood": self.current_mood,
            "mood_intensity": round(self.mood_intensity, 2),
            "mood_shifted": shift is not None,
            "shift_reaction": shift["reaction"] if shift else None,

            # Energie & Aktivität
            "energy": round(self.current_energy, 2),
            "energy_label": self._get_energy_label(),
            "activity_level": round(self.activity_level, 2),
            "energy_peaks_today": self.energy_peaks,

            # Interessen
            "current_interests": self.current_interests,
            "curiosity": round(self.curiosity_level, 2),

            # Langeweile & Sättigung
            "boredom_level": round(self.boredom_level, 2),
            "boredom_threshold": round(self.boredom_threshold, 2),
            "is_bored": self.boredom_level > self.boredom_threshold,
            "top_saturated_topics": [
                {"topic": t, "saturation": round(s, 2)}
                for t, s in top_saturated
            ],

            # Session
            "interactions_today": self.interactions_today,
        }

    def get_boredom_status(self) -> Dict[str, Any]:
        """
        Gibt detaillierten Langeweile-Status zurück.

        Returns:
            Dict mit Langeweile-Details
        """
        is_bored = self.boredom_level > self.boredom_threshold

        if is_bored:
            if self.focus_tendency > 0.6:
                status = "gelangweilt aber durchhaltend"
                message = "*seufzt* Ich halte durch, aber ein Wechsel wäre schön..."
            else:
                status = "gelangweilt und unruhig"
                message = random.choice([
                    "*zappelt* Können wir was anderes machen?",
                    "*gähnt laut* Das Thema ist durch...",
                    "*schaut sich um* Ich brauch Abwechslung!"
                ])
        elif self.boredom_level > 0.4:
            status = "leicht gelangweilt"
            message = "*neutral* Geht so..."
        else:
            status = "interessiert"
            message = "*aufmerksam* Bin voll dabei!"

        return {
            "boredom_level": round(self.boredom_level, 2),
            "threshold": round(self.boredom_threshold, 2),
            "is_bored": is_bored,
            "status": status,
            "message": message,
            "recent_topics_count": len(set(self.recent_topics[-5:])),
            "wants_change": is_bored and self.focus_tendency < 0.5
        }

    def force_mood(self, mood: str) -> Dict[str, Any]:
        """
        Erzwingt eine bestimmte Stimmung (für Events/Trigger).

        Args:
            mood: Gewünschte Stimmung

        Returns:
            Dict mit Ergebnis
        """
        if mood not in self.MOODS:
            return {"success": False, "message": f"Unbekannte Stimmung: {mood}"}

        old_mood = self.current_mood
        self.current_mood = mood
        self.mood_intensity = random.uniform(0.6, 1.0)
        self.last_mood_change = datetime.now().isoformat()

        self._save_state()

        return {
            "success": True,
            "old_mood": old_mood,
            "new_mood": mood,
            "message": f"*{mood}* Stimmungswechsel!"
        }

    # =========================================================================
    # PERSISTENZ
    # =========================================================================

    def _load_state(self) -> None:
        """Lädt vollständigen Zustand aus Datei."""
        filepath = self.data_dir / "interest_lifecycle.json"

        # Fallback auf altes Format
        if not filepath.exists():
            old_filepath = self.data_dir / "mood_randomizer.json"
            if old_filepath.exists():
                filepath = old_filepath

        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # === TAGES-CHARAKTER ===
                self.day_type = data.get("day_type", "")
                self.day_seed_date = data.get("day_seed_date", "")
                self.focus_tendency = data.get("focus_tendency", 0.5)
                self.base_energy = data.get("base_energy", 0.7)

                # === STIMMUNG ===
                self.current_mood = data.get("current_mood", "")
                self.mood_intensity = data.get("mood_intensity", 0.5)
                self.mood_duration = data.get("mood_duration", 0)
                self.last_mood_change = data.get("last_mood_change", "")

                # === ENERGIE & AKTIVITÄT ===
                self.current_energy = data.get("current_energy", 0.5)
                self.activity_level = data.get("activity_level", 0.5)
                self.day_start_energy = data.get("day_start_energy", 0.7)
                self.energy_peaks = data.get("energy_peaks", 0)

                # === INTERESSEN ===
                self.current_interests = data.get("current_interests", [])
                self.interest_engagement = data.get("interest_engagement", {})
                self.interest_saturation = data.get("interest_saturation", {})
                self.last_interest_change = data.get("last_interest_change", "")

                # === LANGEWEILE ===
                self.boredom_level = data.get("boredom_level", 0.0)
                self.time_on_current_topic = data.get("time_on_current_topic", 0)
                self.boredom_threshold = data.get("boredom_threshold", 0.7)

                # === HISTORY ===
                self.recent_topics = data.get("recent_topics", [])
                self.curiosity_level = data.get("curiosity_level", 0.5)

                # === SESSION ===
                self.session_start = data.get("session_start", "")
                self.interactions_today = data.get("interactions_today", 0)

                logger.info("InterestLifecycleSystem State geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden: {e}")

    def _save_state(self) -> None:
        """Speichert vollständigen Zustand in Datei."""
        filepath = self.data_dir / "interest_lifecycle.json"
        try:
            data = {
                # Tages-Charakter
                "day_type": self.day_type,
                "day_seed_date": self.day_seed_date,
                "focus_tendency": self.focus_tendency,
                "base_energy": self.base_energy,

                # Stimmung
                "current_mood": self.current_mood,
                "mood_intensity": self.mood_intensity,
                "mood_duration": self.mood_duration,
                "last_mood_change": self.last_mood_change,

                # Energie & Aktivität
                "current_energy": self.current_energy,
                "activity_level": self.activity_level,
                "day_start_energy": self.day_start_energy,
                "energy_peaks": self.energy_peaks,

                # Interessen
                "current_interests": self.current_interests,
                "interest_engagement": self.interest_engagement,
                "interest_saturation": self.interest_saturation,
                "last_interest_change": self.last_interest_change,

                # Langeweile
                "boredom_level": self.boredom_level,
                "time_on_current_topic": self.time_on_current_topic,
                "boredom_threshold": self.boredom_threshold,

                # History
                "recent_topics": self.recent_topics,
                "curiosity_level": self.curiosity_level,

                # Session
                "session_start": self.session_start,
                "interactions_today": self.interactions_today,
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern: {e}")


# Legacy-Aliase für Kompatibilität
InterestFluctuationSystem = InterestLifecycleSystem
MoodRandomizer = InterestLifecycleSystem


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HOLO DIGITAL BODY & INTEREST SYSTEM v3.0 - Demo")
    print("=" * 60)

    # Digital Body System
    print("\n--- Digital Body System (Netzwerk als Körper) ---\n")

    # Prüfe Datenbank-Verfügbarkeit
    print(f"Datenbank verfügbar: {HAS_DATABASE}")

    body = DigitalBodySystem(use_database=True)

    # Zeige Netzwerk-Geräte
    print("Holos Netzwerk-Körper:")
    overview = body.get_network_overview()
    for name, info in overview["devices"].items():
        status = "🟢" if info["online"] else "🔴"
        print(f"   {status} {name:15} ({info['role']}) - {info['capabilities'][:3]}...")

    # Simuliere verschiedene Hardware-Zustände
    print("\n1) Normaler Zustand:")
    result = body.update_hardware_state(ram=45, cpu=20, temp=50)
    print(f"   Status: {body.get_status_expression()}")

    print("\n2) RAM wird voll (Kopfschmerzen!):")
    result = body.update_hardware_state(ram=88)
    print(f"   Status: {body.get_status_expression()}")
    if result["reactions"]:
        print(f"   Reaktion: {result['reactions'][0]['message']}")

    # RAM aufräumen!
    print("\n   → RAM aufräumen:")
    cleanup = body.save_and_clear_ram()
    print(f"   {cleanup['message']}")

    print("\n3) Lange hohe CPU-Last (Müdigkeit → powersave):")
    # Simuliere lange hohe Last
    body.cpu_high_since = (datetime.now() - timedelta(minutes=65)).isoformat()
    body.high_cpu_minutes = 65
    result = body.update_hardware_state(cpu=80)
    print(f"   Status: {body.get_status_expression()}")
    if result["reactions"]:
        print(f"   Reaktion: {result['reactions'][0]['message']}")
        print(f"   Governor: {body.current_governor.value}")

    print("\n4) CPU erholt sich → zurück zu ondemand:")
    result = body.update_hardware_state(cpu=15)
    print(f"   Status: {body.get_status_expression()}")
    if result["reactions"]:
        print(f"   Reaktion: {result['reactions'][0]['message']}")

    # Netzwerk-Geräte Management
    print("\n--- Netzwerk-Geräte Management ---\n")

    # Gaming Laptop geht offline (simuliert länger aus)
    print("Gaming Laptop ist seit 3 Stunden aus:")
    body.update_device_status("Gaming Laptop", online=False)
    # Simuliere dass es schon länger aus ist
    body.network_devices["Gaming Laptop"].last_seen = (
        datetime.now() - timedelta(hours=3)
    ).isoformat()

    # Holo will ein Bild generieren - überlegt ob aufwecken
    print("\n   Holo will ein Bild generieren - Überlegung:")
    decision = body.consider_waking_device("Gaming Laptop", reason="Bildgenerierung")

    for thought in decision.get("thoughts", []):
        print(f"   {thought}")

    if decision.get("question"):
        print(f"\n   Frage an User: \"{decision['question']}\"")

    # Direktes Aufwecken ohne Bestätigung
    print("\n   → Direktes Aufwecken (ohne Bestätigung):")
    wake_result = body.wake_device("Gaming Laptop", user_confirmed=False)
    print(f"   {wake_result['message']}")

    # Mit User-Bestätigung
    print("\n   → Mit User-Bestätigung:")
    wake_result = body.wake_device("Gaming Laptop", user_confirmed=True)
    print(f"   {wake_result['message']}")

    # Raum-Wahrnehmung
    print("\n--- Raum-Wahrnehmung (Smart Home Sensoren) ---\n")
    body.update_room("Wohnzimmer", temperature=23.7, humidity=37,
                     devices_on=["TV", "Steckdose"], presence=True)
    body.update_room("Schlafzimmer", temperature=18.4, humidity=45)

    print("Wohnzimmer-Einschätzung:")
    assessment = body.get_room_assessment("Wohnzimmer")
    for comment in assessment["comments"]:
        print(f"   {comment}")

    # NAS / Information Pool
    print("\n--- NAS / Information Pool ---\n")

    if body.use_database:
        print("Datenbank aktiv - registriere NAS-Ordner:")

        # Registriere typische NAS-Ordner
        folders_to_register = [
            ("/volume1/Filme", "Filme", "filme", 500),
            ("/volume1/Serien", "Serien", "serien", 800),
            ("/volume1/Musik", "Musik", "musik", 100),
            ("/volume1/Anime", "Anime", "anime", 300),
            ("/volume1/Backups", "Backups", "backups", 200),
        ]

        for path, name, ftype, size in folders_to_register:
            result = body.register_nas_folder(path, name, ftype, size)
            print(f"   {result['message']}")

        # Zeige NAS-Struktur
        print("\nNAS-Struktur:")
        structure = body.get_nas_structure()
        print(f"   {structure['message']}")
        for ftype, folders in structure["folders"].items():
            print(f"   [{ftype}]: {', '.join(f['name'] for f in folders)}")

        # Finde Inhalte
        print("\nInhalte finden:")
        for content in ["Filme", "Anime", "Musik"]:
            location = body.find_content_location(content)
            print(f"   {location['message']}")
    else:
        print("   (Datenbank nicht verfügbar - NAS-Funktionen deaktiviert)")

    # Interest Fluctuation System
    print("\n--- Interessen-Schwankungen ---\n")
    interests = InterestFluctuationSystem()

    print("Heutige Stimmung:")
    mood = interests.get_todays_mood()
    print(f"   Tag: {mood['weekday']}")
    print(f"   Fokus: {mood['focus_category'] or 'keiner speziell'}")
    print(f"   Interessen-Level:")
    for cat, level in mood["interest_levels"].items():
        bar = "█" * int(level * 10) + "░" * (10 - int(level * 10))
        print(f"      {cat:15} [{bar}] {level:.0%}")

    print("\n Themen-Reaktionen:")
    test_topics = ["Programmieren", "Musik", "Philosophie", "Spiele"]
    for topic in test_topics:
        level, reaction = interests.would_enjoy_topic(topic)
        print(f"   '{topic}': {reaction}")

    # Spontanes Interesse
    interests.curiosity_level = 0.8  # Hohe Neugier für Demo
    print("\nSpontanes Interesse:")
    for _ in range(3):
        spontaneous = interests.get_spontaneous_interest()
        if spontaneous:
            print(f"   {spontaneous['message']}")
        else:
            print("   (Keine spontane Idee gerade)")
