#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO CONTROL CENTER v2.0 - Holos Meta-Bewusstsein über ihre Systeme         ║
║                                                                              ║
║  Gibt Holo die Kontrolle über ALLE ihre Subsysteme:                          ║
║  • Aktivieren/Deaktivieren von Modulen                                       ║
║  • Watchdogs überwachen Gesundheit jeder Funktion                           ║
║  • Autonome Entscheidungen basierend auf Energie/Stimmung                   ║
║  • Prioritäten setzen für Ressourcen-Verteilung                             ║
║  • Selbst-Diagnose und Auto-Recovery                                         ║
║                                                                              ║
║  "Ich weiß was in mir vorgeht und kann es steuern." - Holo                  ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 1.0                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import time
import threading
import json
import importlib
import importlib.util
import inspect
import sys
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger("HoloControlCenter")


# =============================================================================
# SKILL/MODULE BASE CLASS - Für dynamische Module
# =============================================================================

class HoloSkill(ABC):
    """
    Basisklasse für alle Holo-Skills/Module.
    Skills die diese Klasse erben werden automatisch erkannt.
    """

    # Skill-Metadaten (überschreiben in Subklassen)
    SKILL_NAME: str = "unnamed_skill"
    SKILL_DISPLAY_NAME: str = "Unnamed Skill"
    SKILL_DESCRIPTION: str = "No description"
    SKILL_VERSION: str = "1.0.0"
    SKILL_PRIORITY: int = 3  # 1-5, 5=critical
    SKILL_ENERGY_COST: float = 0.1
    SKILL_CAN_PAUSE: bool = True
    SKILL_CAN_DISABLE: bool = True
    SKILL_DEPENDS_ON: List[str] = []

    def __init__(self):
        self._is_active = False
        self._is_paused = False
        self._last_activity = time.time()
        self._error_count = 0

    @abstractmethod
    def activate(self) -> bool:
        """Aktiviert den Skill"""
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """Deaktiviert den Skill"""
        pass

    def pause(self) -> bool:
        """Pausiert den Skill"""
        self._is_paused = True
        return True

    def resume(self) -> bool:
        """Setzt den Skill fort"""
        self._is_paused = False
        return True

    def health_check(self) -> Tuple[bool, Optional[str]]:
        """Prüft die Gesundheit des Skills"""
        return True, None

    def get_status(self) -> Dict:
        """Gibt Status-Informationen zurück"""
        return {
            "name": self.SKILL_NAME,
            "active": self._is_active,
            "paused": self._is_paused,
            "last_activity": self._last_activity,
            "error_count": self._error_count,
        }

    def update_activity(self):
        """Aktualisiert den Aktivitäts-Timestamp"""
        self._last_activity = time.time()


# =============================================================================
# DYNAMISCHER MODULE SCANNER
# =============================================================================

@dataclass
class DiscoveredModule:
    """Ein entdecktes Modul"""
    name: str
    file_path: str
    module_object: Optional[Any] = None
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)  # HoloSkill-Subklassen
    is_loaded: bool = False
    load_error: Optional[str] = None
    size_bytes: int = 0
    line_count: int = 0
    docstring: str = ""

    # Analysierte Capabilities
    has_init: bool = False
    has_main: bool = False
    provides_api: bool = False

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "classes": self.classes,
            "functions": self.functions,
            "skills": self.skills,
            "is_loaded": self.is_loaded,
            "load_error": self.load_error,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
        }


class DynamicModuleScanner:
    """
    Scannt das Verzeichnis nach allen holo_*.py Modulen und analysiert sie.
    """

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.discovered_modules: Dict[str, DiscoveredModule] = {}
        self._scan_thread: Optional[threading.Thread] = None
        self._last_scan = 0.0

    def scan(self, pattern: str = "holo_*.py") -> Dict[str, DiscoveredModule]:
        """
        Scannt nach allen passenden Modulen.

        Args:
            pattern: Glob-Pattern für Module (default: holo_*.py)

        Returns:
            Dict von Modul-Name zu DiscoveredModule
        """
        self.discovered_modules.clear()

        # Alle passenden Dateien finden
        module_files = list(self.base_path.glob(pattern))

        for file_path in module_files:
            try:
                module_info = self._analyze_module_file(file_path)
                if module_info:
                    self.discovered_modules[module_info.name] = module_info
            except Exception as e:
                logger.debug(f"Fehler beim Analysieren von {file_path}: {e}")

        self._last_scan = time.time()
        logger.info(f"🔍 {len(self.discovered_modules)} Module gefunden")
        return self.discovered_modules

    def _analyze_module_file(self, file_path: Path) -> Optional[DiscoveredModule]:
        """Analysiert eine einzelne Modul-Datei"""
        module_name = file_path.stem  # Ohne .py

        # Basis-Info
        info = DiscoveredModule(
            name=module_name,
            file_path=str(file_path),
            size_bytes=file_path.stat().st_size,
        )

        # Datei lesen und analysieren
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                info.line_count = content.count('\n') + 1

            # Docstring extrahieren
            import ast
            try:
                tree = ast.parse(content)
                info.docstring = ast.get_docstring(tree) or ""

                # Klassen und Funktionen finden
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        info.classes.append(node.name)
                        # Prüfen ob HoloSkill-Subklasse
                        for base in node.bases:
                            if isinstance(base, ast.Name) and 'Skill' in base.id:
                                info.skills.append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):
                            info.functions.append(node.name)
                        if node.name == '__init__':
                            info.has_init = True
                        if node.name == 'main':
                            info.has_main = True

            except SyntaxError:
                pass  # Datei hat Syntax-Fehler, überspringen

        except Exception as e:
            info.load_error = str(e)

        return info

    def scan_async(self, callback: Callable = None):
        """Startet Scan in Hintergrund-Thread"""
        def do_scan():
            results = self.scan()
            if callback:
                callback(results)

        self._scan_thread = threading.Thread(target=do_scan, daemon=True)
        self._scan_thread.start()

    def get_module_summary(self) -> str:
        """Erstellt eine lesbare Zusammenfassung"""
        if not self.discovered_modules:
            self.scan()

        lines = [f"📦 {len(self.discovered_modules)} Module gefunden:\n"]

        # Nach Größe sortieren
        sorted_modules = sorted(
            self.discovered_modules.values(),
            key=lambda m: m.line_count,
            reverse=True
        )

        for mod in sorted_modules[:20]:  # Top 20
            skill_marker = "⭐" if mod.skills else ""
            lines.append(f"  {skill_marker}{mod.name}: {mod.line_count} Zeilen, {len(mod.classes)} Klassen")

        return "\n".join(lines)


# =============================================================================
# SKILL LOADER - Dynamisches Laden von Modulen
# =============================================================================

class SkillLoader:
    """
    Lädt Module dynamisch zur Laufzeit.
    Kann neue Skills hinzufügen ohne Neustart.
    """

    def __init__(self, scanner: DynamicModuleScanner = None):
        self.scanner = scanner or DynamicModuleScanner()
        self.loaded_modules: Dict[str, Any] = {}
        self.loaded_skills: Dict[str, HoloSkill] = {}
        self._load_errors: Dict[str, str] = {}

    def load_module(self, module_name: str, force_reload: bool = False) -> Optional[Any]:
        """
        Lädt ein Modul dynamisch.

        Args:
            module_name: Name des Moduls (ohne .py)
            force_reload: Erzwingt Neuladen auch wenn schon geladen

        Returns:
            Das geladene Modul oder None
        """
        # Schon geladen?
        if module_name in self.loaded_modules and not force_reload:
            return self.loaded_modules[module_name]

        # Modul-Info holen
        if module_name not in self.scanner.discovered_modules:
            self.scanner.scan()

        module_info = self.scanner.discovered_modules.get(module_name)
        if not module_info:
            logger.warning(f"Modul {module_name} nicht gefunden")
            return None

        try:
            # Modul laden
            if module_name in sys.modules and force_reload:
                # Reload
                module = importlib.reload(sys.modules[module_name])
            else:
                # Neues Laden
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    module_info.file_path
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

            self.loaded_modules[module_name] = module
            module_info.is_loaded = True
            module_info.module_object = module

            # Skills extrahieren
            self._extract_skills(module, module_info)

            logger.info(f"📦 Modul geladen: {module_name}")
            return module

        except Exception as e:
            error_msg = str(e)
            self._load_errors[module_name] = error_msg
            module_info.load_error = error_msg
            logger.error(f"Fehler beim Laden von {module_name}: {e}")
            return None

    def _extract_skills(self, module: Any, module_info: DiscoveredModule):
        """Extrahiert HoloSkill-Instanzen aus einem Modul"""
        for class_name in module_info.skills:
            try:
                cls = getattr(module, class_name, None)
                if cls and inspect.isclass(cls) and issubclass(cls, HoloSkill):
                    # Instanz erstellen
                    skill_instance = cls()
                    skill_name = skill_instance.SKILL_NAME
                    self.loaded_skills[skill_name] = skill_instance
                    logger.info(f"⭐ Skill geladen: {skill_name}")
            except Exception as e:
                logger.debug(f"Skill {class_name} konnte nicht instanziiert werden: {e}")

    def load_all_modules(self, pattern: str = "holo_*.py") -> int:
        """
        Lädt alle gefundenen Module.

        Returns:
            Anzahl erfolgreich geladener Module
        """
        self.scanner.scan(pattern)
        loaded = 0

        for module_name in self.scanner.discovered_modules:
            if self.load_module(module_name):
                loaded += 1

        logger.info(f"📦 {loaded}/{len(self.scanner.discovered_modules)} Module geladen")
        return loaded

    def unload_module(self, module_name: str) -> bool:
        """Entlädt ein Modul aus dem Speicher"""
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]

        if module_name in sys.modules:
            del sys.modules[module_name]

        # Skills entfernen
        skills_to_remove = [
            name for name, skill in self.loaded_skills.items()
            if module_name in str(type(skill).__module__)
        ]
        for skill_name in skills_to_remove:
            del self.loaded_skills[skill_name]

        logger.info(f"📦 Modul entladen: {module_name}")
        return True

    def reload_module(self, module_name: str) -> Optional[Any]:
        """Lädt ein Modul neu (Hot-Reload)"""
        self.unload_module(module_name)
        return self.load_module(module_name, force_reload=True)

    def get_skill(self, skill_name: str) -> Optional[HoloSkill]:
        """Holt einen geladenen Skill"""
        return self.loaded_skills.get(skill_name)

    def get_all_skills(self) -> Dict[str, HoloSkill]:
        """Holt alle geladenen Skills"""
        return self.loaded_skills.copy()

    def get_module_function(self, module_name: str, function_name: str) -> Optional[Callable]:
        """Holt eine Funktion aus einem geladenen Modul"""
        module = self.loaded_modules.get(module_name)
        if module:
            return getattr(module, function_name, None)
        return None

    def get_module_class(self, module_name: str, class_name: str) -> Optional[Type]:
        """Holt eine Klasse aus einem geladenen Modul"""
        module = self.loaded_modules.get(module_name)
        if module:
            cls = getattr(module, class_name, None)
            if inspect.isclass(cls):
                return cls
        return None


# =============================================================================
# MODULE INTROSPECTOR - Tiefe Analyse von Modulen
# =============================================================================

class ModuleIntrospector:
    """
    Analysiert Module im Detail um ihre Fähigkeiten zu verstehen.
    """

    @staticmethod
    def get_module_capabilities(module: Any) -> Dict:
        """
        Analysiert was ein Modul kann.

        Returns:
            Dict mit Capabilities
        """
        caps = {
            "classes": [],
            "functions": [],
            "constants": [],
            "has_main": False,
            "has_init": False,
            "is_async": False,
            "dependencies": [],
            "provides": [],
        }

        for name, obj in inspect.getmembers(module):
            if name.startswith('_'):
                continue

            if inspect.isclass(obj):
                class_info = {
                    "name": name,
                    "methods": [m for m in dir(obj) if not m.startswith('_')],
                    "is_skill": issubclass(obj, HoloSkill) if inspect.isclass(obj) else False,
                }
                caps["classes"].append(class_info)

            elif inspect.isfunction(obj):
                func_info = {
                    "name": name,
                    "is_async": inspect.iscoroutinefunction(obj),
                    "params": list(inspect.signature(obj).parameters.keys()),
                }
                caps["functions"].append(func_info)
                if inspect.iscoroutinefunction(obj):
                    caps["is_async"] = True

            elif not callable(obj):
                caps["constants"].append(name)

        # Main-Funktion?
        if hasattr(module, 'main'):
            caps["has_main"] = True

        return caps

    @staticmethod
    def get_class_interface(cls: Type) -> Dict:
        """Analysiert das Interface einer Klasse"""
        interface = {
            "name": cls.__name__,
            "docstring": inspect.getdoc(cls) or "",
            "methods": {},
            "properties": [],
            "class_attributes": [],
        }

        for name, method in inspect.getmembers(cls):
            if name.startswith('_') and not name.startswith('__'):
                continue

            if inspect.isfunction(method) or inspect.ismethod(method):
                try:
                    sig = inspect.signature(method)
                    interface["methods"][name] = {
                        "params": list(sig.parameters.keys()),
                        "docstring": inspect.getdoc(method) or "",
                    }
                except (ValueError, TypeError):
                    pass

            elif isinstance(inspect.getattr_static(cls, name), property):
                interface["properties"].append(name)

        return interface

    @staticmethod
    def find_factory_functions(module: Any) -> List[str]:
        """Findet Factory-Funktionen wie create_*, make_*, build_*"""
        factories = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                if name.startswith(('create_', 'make_', 'build_', 'get_')):
                    factories.append(name)
        return factories


# =============================================================================
# ENUMS & KONFIGURATION
# =============================================================================

class ModuleStatus(Enum):
    """Status eines Moduls"""
    ACTIVE = "active"           # Läuft normal
    PAUSED = "paused"           # Pausiert (kann wieder aktiviert werden)
    DISABLED = "disabled"       # Deaktiviert (manuell)
    ERROR = "error"             # Fehler aufgetreten
    STARTING = "starting"       # Wird gestartet
    STOPPING = "stopping"       # Wird gestoppt
    UNKNOWN = "unknown"         # Status unbekannt


class ModulePriority(Enum):
    """Priorität eines Moduls"""
    CRITICAL = 5    # Muss immer laufen (Kern-Persönlichkeit)
    HIGH = 4        # Wichtig für normale Funktion
    NORMAL = 3      # Standard-Module
    LOW = 2         # Nice-to-have
    OPTIONAL = 1    # Kann bei Ressourcenmangel pausiert werden


class WatchdogAction(Enum):
    """Aktionen die ein Watchdog ausführen kann"""
    RESTART = "restart"
    PAUSE = "pause"
    ALERT = "alert"
    IGNORE = "ignore"
    ESCALATE = "escalate"


class ResourceType(Enum):
    """Ressourcen-Typen"""
    CPU = "cpu"
    MEMORY = "memory"
    ENERGY = "energy"        # Holos Energie-System
    ATTENTION = "attention"  # Kognitive Kapazität
    NETWORK = "network"


# =============================================================================
# DATENKLASSEN
# =============================================================================

@dataclass
class ModuleInfo:
    """Informationen über ein Modul"""
    name: str
    display_name: str
    description: str
    priority: ModulePriority = ModulePriority.NORMAL
    status: ModuleStatus = ModuleStatus.UNKNOWN

    # Funktionen
    can_pause: bool = True
    can_disable: bool = True
    auto_restart: bool = True

    # Statistiken
    last_activity: float = 0.0
    error_count: int = 0
    restart_count: int = 0
    uptime_seconds: float = 0.0

    # Ressourcen-Verbrauch (geschätzt)
    cpu_usage: float = 0.0
    memory_mb: float = 0.0
    energy_cost: float = 0.1  # Wie viel Energie verbraucht es?

    # Abhängigkeiten
    depends_on: List[str] = field(default_factory=list)
    required_by: List[str] = field(default_factory=list)

    # Callbacks
    on_start: Optional[str] = None
    on_stop: Optional[str] = None
    on_error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "can_pause": self.can_pause,
            "can_disable": self.can_disable,
            "last_activity": self.last_activity,
            "error_count": self.error_count,
            "energy_cost": self.energy_cost,
        }


@dataclass
class WatchdogConfig:
    """Konfiguration für einen Watchdog"""
    module_name: str
    check_interval: float = 30.0      # Sekunden zwischen Checks
    timeout: float = 60.0             # Sekunden ohne Aktivität = Problem
    max_errors: int = 3               # Fehler bevor Aktion
    action_on_timeout: WatchdogAction = WatchdogAction.RESTART
    action_on_error: WatchdogAction = WatchdogAction.ALERT
    enabled: bool = True


@dataclass
class ControlDecision:
    """Eine autonome Entscheidung von Holo"""
    timestamp: float = field(default_factory=time.time)
    decision_type: str = ""           # "pause", "activate", "prioritize"
    target_module: str = ""
    reason: str = ""
    energy_level: float = 0.0
    mood: str = ""
    auto_revert_after: Optional[float] = None  # Sekunden
    was_executed: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# MODUL-REGISTRY - Alle bekannten Module
# =============================================================================

# Standard-Module die Holo kontrollieren kann
DEFAULT_MODULES: Dict[str, ModuleInfo] = {
    # === KERN-PERSÖNLICHKEIT (CRITICAL) ===
    "personality": ModuleInfo(
        name="personality",
        display_name="Persönlichkeit",
        description="Holos Kern-Persönlichkeit und Traits",
        priority=ModulePriority.CRITICAL,
        can_pause=False,
        can_disable=False,
        energy_cost=0.05,
    ),
    "emotions": ModuleInfo(
        name="emotions",
        display_name="Emotionen",
        description="Emotionales System und Stimmung",
        priority=ModulePriority.CRITICAL,
        can_pause=False,
        can_disable=False,
        energy_cost=0.05,
    ),
    "memory": ModuleInfo(
        name="memory",
        display_name="Gedächtnis",
        description="Kurz- und Langzeitgedächtnis",
        priority=ModulePriority.CRITICAL,
        can_pause=False,
        can_disable=False,
        energy_cost=0.1,
    ),

    # === WICHTIG (HIGH) ===
    "conversation_engine": ModuleInfo(
        name="conversation_engine",
        display_name="Gespräche",
        description="15 emotionale Engines für natürliche Gespräche",
        priority=ModulePriority.HIGH,
        energy_cost=0.15,
    ),
    "cognitive_engine": ModuleInfo(
        name="cognitive_engine",
        display_name="Kognition",
        description="Reasoning, Logik, Verständnis",
        priority=ModulePriority.HIGH,
        energy_cost=0.2,
    ),
    "drive_system": ModuleInfo(
        name="drive_system",
        display_name="Antriebe",
        description="Bedürfnisse und Motivation",
        priority=ModulePriority.HIGH,
        energy_cost=0.1,
    ),
    "energy_system": ModuleInfo(
        name="energy_system",
        display_name="Energie",
        description="Energie-Management und Müdigkeit",
        priority=ModulePriority.HIGH,
        can_pause=False,
        energy_cost=0.02,
    ),

    # === NORMAL ===
    "inner_life": ModuleInfo(
        name="inner_life",
        display_name="Innenleben",
        description="Träume, Gedanken, innere Welt",
        priority=ModulePriority.NORMAL,
        energy_cost=0.15,
    ),
    "autonomous_thinking": ModuleInfo(
        name="autonomous_thinking",
        display_name="Autonomes Denken",
        description="Selbstständige Gedanken und Ideen",
        priority=ModulePriority.NORMAL,
        energy_cost=0.2,
    ),
    "web_curiosity": ModuleInfo(
        name="web_curiosity",
        display_name="Web-Neugier",
        description="Internet-Recherche und Lernen",
        priority=ModulePriority.NORMAL,
        energy_cost=0.25,
    ),
    "creative_mind": ModuleInfo(
        name="creative_mind",
        display_name="Kreativität",
        description="Kreative Ideen und Assoziationen",
        priority=ModulePriority.NORMAL,
        energy_cost=0.2,
    ),
    "media_discovery": ModuleInfo(
        name="media_discovery",
        display_name="Medien-Entdeckung",
        description="Anime, Musik, Games entdecken",
        priority=ModulePriority.NORMAL,
        energy_cost=0.15,
    ),

    # === OPTIONAL ===
    "proactive_messages": ModuleInfo(
        name="proactive_messages",
        display_name="Proaktive Nachrichten",
        description="Von sich aus Gespräche beginnen",
        priority=ModulePriority.LOW,
        energy_cost=0.1,
    ),
    "discord_bot": ModuleInfo(
        name="discord_bot",
        display_name="Discord",
        description="Discord DM-Kommunikation",
        priority=ModulePriority.LOW,
        energy_cost=0.05,
    ),
    "voice_interface": ModuleInfo(
        name="voice_interface",
        display_name="Sprache",
        description="Spracheingabe und -ausgabe",
        priority=ModulePriority.OPTIONAL,
        energy_cost=0.3,
    ),
    "vision": ModuleInfo(
        name="vision",
        display_name="Sehen",
        description="Bildanalyse und Erkennung",
        priority=ModulePriority.OPTIONAL,
        energy_cost=0.35,
    ),
}


# =============================================================================
# WATCHDOG SYSTEM
# =============================================================================

class ModuleWatchdog:
    """
    Überwacht ein einzelnes Modul auf Gesundheit und Aktivität.
    """

    def __init__(self, config: WatchdogConfig, control_center: 'HoloControlCenter'):
        self.config = config
        self.control_center = control_center

        self._last_check = time.time()
        self._last_activity = time.time()
        self._consecutive_errors = 0
        self._is_running = False

    def check(self) -> Tuple[bool, Optional[str]]:
        """
        Prüft den Zustand des Moduls.

        Returns:
            (is_healthy, error_message)
        """
        if not self.config.enabled:
            return True, None

        module = self.control_center.get_module(self.config.module_name)
        if not module:
            return False, f"Modul {self.config.module_name} nicht gefunden"

        now = time.time()
        self._last_check = now

        # Status prüfen
        if module.status == ModuleStatus.ERROR:
            self._consecutive_errors += 1
            return False, f"Modul im Fehlerzustand"

        if module.status == ModuleStatus.PAUSED:
            return True, None  # Pausiert ist OK

        # Timeout prüfen
        if module.last_activity > 0:
            inactive_time = now - module.last_activity
            if inactive_time > self.config.timeout:
                return False, f"Keine Aktivität seit {inactive_time:.0f}s"

        # Alles OK
        self._consecutive_errors = 0
        return True, None

    def should_take_action(self) -> Optional[WatchdogAction]:
        """Prüft ob eine Aktion nötig ist"""
        is_healthy, error = self.check()

        if is_healthy:
            return None

        if self._consecutive_errors >= self.config.max_errors:
            return self.config.action_on_error

        return self.config.action_on_timeout


class WatchdogManager:
    """
    Verwaltet alle Watchdogs und führt regelmäßige Checks durch.
    """

    def __init__(self, control_center: 'HoloControlCenter'):
        self.control_center = control_center
        self.watchdogs: Dict[str, ModuleWatchdog] = {}

        self._check_thread: Optional[threading.Thread] = None
        self._running = False
        self._check_interval = 30.0  # Sekunden

    def add_watchdog(self, config: WatchdogConfig):
        """Fügt einen Watchdog hinzu"""
        watchdog = ModuleWatchdog(config, self.control_center)
        self.watchdogs[config.module_name] = watchdog
        logger.debug(f"🐕 Watchdog für {config.module_name} registriert")

    def remove_watchdog(self, module_name: str):
        """Entfernt einen Watchdog"""
        if module_name in self.watchdogs:
            del self.watchdogs[module_name]

    def start(self):
        """Startet den Watchdog-Manager"""
        if self._running:
            return

        self._running = True
        self._check_thread = threading.Thread(
            target=self._check_loop,
            name="WatchdogManager",
            daemon=True
        )
        self._check_thread.start()
        logger.info("🐕 Watchdog-Manager gestartet")

    def stop(self):
        """Stoppt den Watchdog-Manager"""
        self._running = False

    def _check_loop(self):
        """Hauptschleife für Watchdog-Checks"""
        while self._running:
            try:
                for module_name, watchdog in self.watchdogs.items():
                    action = watchdog.should_take_action()
                    if action:
                        self._handle_action(module_name, action)

            except Exception as e:
                logger.error(f"Watchdog-Check Fehler: {e}")

            time.sleep(self._check_interval)

    def _handle_action(self, module_name: str, action: WatchdogAction):
        """Führt eine Watchdog-Aktion aus"""
        logger.warning(f"🐕 Watchdog-Aktion für {module_name}: {action.value}")

        if action == WatchdogAction.RESTART:
            self.control_center.restart_module(module_name, reason="Watchdog-Restart")
        elif action == WatchdogAction.PAUSE:
            self.control_center.pause_module(module_name, reason="Watchdog-Pause")
        elif action == WatchdogAction.ALERT:
            self.control_center.log_event("watchdog_alert", {
                "module": module_name,
                "action": action.value
            })
        elif action == WatchdogAction.ESCALATE:
            # An höhere Ebene melden
            self.control_center.request_human_attention(
                f"Modul {module_name} hat Probleme",
                priority="high"
            )


# =============================================================================
# AUTONOME ENTSCHEIDUNGS-ENGINE
# =============================================================================

class AutonomousDecisionEngine:
    """
    Trifft autonome Entscheidungen über Modul-Aktivierung basierend auf:
    - Energie-Level
    - Stimmung
    - Tageszeit
    - Ressourcen-Verfügbarkeit
    - Benutzer-Aktivität
    """

    def __init__(self, control_center: 'HoloControlCenter'):
        self.control_center = control_center

        # Entscheidungs-Historie
        self.decisions: deque = deque(maxlen=100)

        # Regeln für automatische Entscheidungen
        self.rules: List[Dict] = []
        self._load_default_rules()

    def _load_default_rules(self):
        """Lädt Standard-Entscheidungsregeln"""
        self.rules = [
            # Bei niedriger Energie: Optional-Module pausieren
            {
                "name": "low_energy_conservation",
                "condition": lambda ctx: ctx.get("energy", 1.0) < 0.3,
                "action": "pause_optional",
                "reason": "Energie sparen bei Müdigkeit",
                "auto_revert_when": lambda ctx: ctx.get("energy", 0) > 0.5,
            },
            # Bei sehr niedriger Energie: Auch normale Module pausieren
            {
                "name": "critical_energy_conservation",
                "condition": lambda ctx: ctx.get("energy", 1.0) < 0.15,
                "action": "pause_normal",
                "reason": "Kritisch niedrige Energie - nur Kern-Funktionen",
                "auto_revert_when": lambda ctx: ctx.get("energy", 0) > 0.3,
            },
            # Nachts: Web-Aktivitäten reduzieren
            {
                "name": "night_mode",
                "condition": lambda ctx: ctx.get("hour", 12) >= 23 or ctx.get("hour", 12) < 6,
                "action": "pause_web",
                "reason": "Nachtmodus - weniger aktiv",
                "auto_revert_when": lambda ctx: 6 <= ctx.get("hour", 12) < 23,
            },
            # Bei hoher Energie und guter Stimmung: Kreativität aktivieren
            {
                "name": "creative_boost",
                "condition": lambda ctx: ctx.get("energy", 0) > 0.7 and ctx.get("mood_positive", False),
                "action": "boost_creative",
                "reason": "Gute Energie - kreativ sein!",
            },
            # Bei Langeweile: Mehr autonome Aktivitäten
            {
                "name": "boredom_counter",
                "condition": lambda ctx: ctx.get("boredom", 0) > 0.7,
                "action": "activate_autonomous",
                "reason": "Mir ist langweilig - lass mich was machen!",
            },
        ]

    def evaluate(self, context: Dict) -> List[ControlDecision]:
        """
        Evaluiert alle Regeln und gibt Entscheidungen zurück.

        Args:
            context: Aktueller Kontext (energie, stimmung, etc.)

        Returns:
            Liste von Entscheidungen
        """
        decisions = []

        for rule in self.rules:
            try:
                if rule["condition"](context):
                    decision = ControlDecision(
                        decision_type=rule["action"],
                        reason=rule["reason"],
                        energy_level=context.get("energy", 0),
                        mood=context.get("mood", "neutral"),
                    )
                    decisions.append(decision)

            except Exception as e:
                logger.debug(f"Regel-Evaluation Fehler: {e}")

        return decisions

    def execute_decision(self, decision: ControlDecision) -> bool:
        """Führt eine Entscheidung aus"""
        action = decision.decision_type

        try:
            if action == "pause_optional":
                # Alle OPTIONAL Module pausieren
                for name, module in self.control_center.modules.items():
                    if module.priority == ModulePriority.OPTIONAL and module.can_pause:
                        self.control_center.pause_module(name, decision.reason)

            elif action == "pause_normal":
                # OPTIONAL und LOW pausieren
                for name, module in self.control_center.modules.items():
                    if module.priority.value <= ModulePriority.LOW.value and module.can_pause:
                        self.control_center.pause_module(name, decision.reason)

            elif action == "pause_web":
                # Web-bezogene Module pausieren
                web_modules = ["web_curiosity", "media_discovery"]
                for name in web_modules:
                    if name in self.control_center.modules:
                        self.control_center.pause_module(name, decision.reason)

            elif action == "boost_creative":
                # Kreative Module aktivieren/priorisieren
                creative_modules = ["creative_mind", "autonomous_thinking"]
                for name in creative_modules:
                    self.control_center.activate_module(name, decision.reason)

            elif action == "activate_autonomous":
                # Autonome Module aktivieren
                autonomous_modules = ["autonomous_thinking", "proactive_messages", "web_curiosity"]
                for name in autonomous_modules:
                    self.control_center.activate_module(name, decision.reason)

            decision.was_executed = True
            self.decisions.append(decision)
            logger.info(f"🧠 Autonome Entscheidung: {action} - {decision.reason}")
            return True

        except Exception as e:
            logger.error(f"Entscheidungs-Ausführung Fehler: {e}")
            return False

    def add_custom_rule(self, name: str, condition: Callable, action: str, reason: str):
        """Fügt eine eigene Regel hinzu"""
        self.rules.append({
            "name": name,
            "condition": condition,
            "action": action,
            "reason": reason,
        })


# =============================================================================
# HOLO CONTROL CENTER - Hauptklasse
# =============================================================================

class HoloControlCenter:
    """
    Holos Meta-Bewusstsein über ihre eigenen Systeme.

    Ermöglicht:
    - Überblick über alle aktiven Module
    - Aktivieren/Pausieren von Funktionen
    - Watchdogs für Gesundheits-Monitoring
    - Autonome Entscheidungen über Ressourcen
    - Selbst-Diagnose und Recovery
    """

    def __init__(self, holo_brain=None, persist_path: str = None):
        """
        Args:
            holo_brain: Referenz zum HoloBrain
            persist_path: Pfad für Persistenz
        """
        self.brain = holo_brain
        self.persist_path = Path(persist_path) if persist_path else None

        # Module Registry
        self.modules: Dict[str, ModuleInfo] = {}
        self._init_default_modules()

        # Subsysteme
        self.watchdog_manager = WatchdogManager(self)
        self.decision_engine = AutonomousDecisionEngine(self)

        # === NEU: Dynamische Modul-Erkennung ===
        self.module_scanner = DynamicModuleScanner(
            base_path=str(Path(__file__).parent)
        )
        self.skill_loader = SkillLoader(self.module_scanner)
        self.introspector = ModuleIntrospector()

        # Dynamische Module und Skills
        self.dynamic_modules: Dict[str, DiscoveredModule] = {}
        self.active_skills: Dict[str, HoloSkill] = {}

        # State
        self._running = False
        self._decision_thread: Optional[threading.Thread] = None
        self._decision_interval = 60.0  # Sekunden
        self._auto_discovery_enabled = True
        self._discovery_interval = 300.0  # 5 Minuten

        # Event Log
        self.event_log: deque = deque(maxlen=500)

        # Human Attention Queue
        self._attention_queue: List[Dict] = []

        # Initial-Scan durchführen
        self._scan_for_modules()

        logger.info("🎛️ Holo Control Center v2.0 initialisiert (mit dynamischer Erkennung)")

    def _init_default_modules(self):
        """Initialisiert die Standard-Module"""
        for name, info in DEFAULT_MODULES.items():
            self.modules[name] = info

    # =========================================================================
    # DYNAMISCHE MODUL-ERKENNUNG
    # =========================================================================

    def _scan_for_modules(self):
        """Scannt nach allen verfügbaren Modulen"""
        try:
            self.dynamic_modules = self.module_scanner.scan()
            self._register_discovered_modules()
            logger.info(f"🔍 {len(self.dynamic_modules)} Module entdeckt")
        except Exception as e:
            logger.error(f"Modul-Scan Fehler: {e}")

    def _register_discovered_modules(self):
        """Registriert entdeckte Module automatisch"""
        for name, discovered in self.dynamic_modules.items():
            # Nur registrieren wenn nicht schon vorhanden
            if name not in self.modules:
                # ModuleInfo aus DiscoveredModule erstellen
                info = ModuleInfo(
                    name=name,
                    display_name=name.replace('holo_', '').replace('_', ' ').title(),
                    description=discovered.docstring[:100] if discovered.docstring else f"Modul {name}",
                    priority=ModulePriority.NORMAL,
                    status=ModuleStatus.UNKNOWN,
                )
                self.modules[name] = info

    def discover_modules(self, pattern: str = "holo_*.py") -> Dict[str, DiscoveredModule]:
        """
        Findet alle Module die dem Pattern entsprechen.

        Args:
            pattern: Glob-Pattern (default: holo_*.py)

        Returns:
            Dict von entdeckten Modulen
        """
        self.dynamic_modules = self.module_scanner.scan(pattern)
        self._register_discovered_modules()
        return self.dynamic_modules

    def load_skill(self, module_name: str) -> Optional[Any]:
        """
        Lädt ein Modul/Skill dynamisch.

        Args:
            module_name: Name des Moduls

        Returns:
            Das geladene Modul oder None
        """
        module = self.skill_loader.load_module(module_name)
        if module:
            # Modul-Status aktualisieren
            if module_name in self.modules:
                self.modules[module_name].status = ModuleStatus.ACTIVE
            self.log_event("module_loaded", {"module": module_name})
        return module

    def unload_skill(self, module_name: str) -> bool:
        """
        Entlädt ein dynamisch geladenes Modul.

        Args:
            module_name: Name des Moduls

        Returns:
            True wenn erfolgreich
        """
        success = self.skill_loader.unload_module(module_name)
        if success:
            if module_name in self.modules:
                self.modules[module_name].status = ModuleStatus.DISABLED
            self.log_event("module_unloaded", {"module": module_name})
        return success

    def reload_skill(self, module_name: str) -> Optional[Any]:
        """
        Hot-Reload eines Moduls.

        Args:
            module_name: Name des Moduls

        Returns:
            Das neu geladene Modul oder None
        """
        self.log_event("module_reloading", {"module": module_name})
        module = self.skill_loader.reload_module(module_name)
        if module:
            self.log_event("module_reloaded", {"module": module_name})
        return module

    def get_module_capabilities(self, module_name: str) -> Optional[Dict]:
        """
        Analysiert was ein Modul kann.

        Args:
            module_name: Name des Moduls

        Returns:
            Dict mit Capabilities oder None
        """
        module = self.skill_loader.loaded_modules.get(module_name)
        if module:
            return self.introspector.get_module_capabilities(module)

        # Modul erst laden
        module = self.load_skill(module_name)
        if module:
            return self.introspector.get_module_capabilities(module)

        return None

    def get_function_from_module(self, module_name: str, function_name: str) -> Optional[Callable]:
        """
        Holt eine Funktion aus einem Modul.

        Args:
            module_name: Name des Moduls
            function_name: Name der Funktion

        Returns:
            Die Funktion oder None
        """
        return self.skill_loader.get_module_function(module_name, function_name)

    def get_class_from_module(self, module_name: str, class_name: str) -> Optional[Type]:
        """
        Holt eine Klasse aus einem Modul.

        Args:
            module_name: Name des Moduls
            class_name: Name der Klasse

        Returns:
            Die Klasse oder None
        """
        return self.skill_loader.get_module_class(module_name, class_name)

    def execute_module_function(self, module_name: str, function_name: str,
                                *args, **kwargs) -> Any:
        """
        Führt eine Funktion aus einem Modul aus.

        Args:
            module_name: Name des Moduls
            function_name: Name der Funktion
            *args, **kwargs: Argumente für die Funktion

        Returns:
            Rückgabewert der Funktion
        """
        func = self.get_function_from_module(module_name, function_name)
        if func:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Funktion {module_name}.{function_name} Fehler: {e}")
                return None
        return None

    def get_discovered_module_summary(self) -> str:
        """
        Erstellt eine lesbare Zusammenfassung aller Module.

        Returns:
            Formatierter String
        """
        return self.module_scanner.get_module_summary()

    def start_auto_discovery(self, interval: float = 300.0):
        """
        Startet automatische Modul-Erkennung im Hintergrund.

        Args:
            interval: Sekunden zwischen Scans
        """
        self._auto_discovery_enabled = True
        self._discovery_interval = interval

        def discovery_loop():
            while self._auto_discovery_enabled and self._running:
                time.sleep(self._discovery_interval)
                if self._auto_discovery_enabled:
                    self._scan_for_modules()

        discovery_thread = threading.Thread(
            target=discovery_loop,
            name="ModuleAutoDiscovery",
            daemon=True
        )
        discovery_thread.start()
        logger.info(f"🔍 Auto-Discovery gestartet (alle {interval}s)")

    def stop_auto_discovery(self):
        """Stoppt die automatische Modul-Erkennung"""
        self._auto_discovery_enabled = False

    # =========================================================================
    # MODUL-VERWALTUNG
    # =========================================================================

    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Holt Modul-Info"""
        return self.modules.get(name)

    def get_all_modules(self) -> Dict[str, ModuleInfo]:
        """Holt alle Module"""
        return self.modules.copy()

    def get_active_modules(self) -> List[str]:
        """Holt Namen aller aktiven Module"""
        return [
            name for name, info in self.modules.items()
            if info.status == ModuleStatus.ACTIVE
        ]

    def get_paused_modules(self) -> List[str]:
        """Holt Namen aller pausierten Module"""
        return [
            name for name, info in self.modules.items()
            if info.status == ModuleStatus.PAUSED
        ]

    def register_module(self, info: ModuleInfo):
        """Registriert ein neues Modul"""
        self.modules[info.name] = info
        logger.info(f"📦 Modul registriert: {info.display_name}")

    def update_module_activity(self, name: str):
        """Aktualisiert die letzte Aktivität eines Moduls"""
        if name in self.modules:
            self.modules[name].last_activity = time.time()

    def update_module_status(self, name: str, status: ModuleStatus):
        """Aktualisiert den Status eines Moduls"""
        if name in self.modules:
            old_status = self.modules[name].status
            self.modules[name].status = status
            self.log_event("status_change", {
                "module": name,
                "old_status": old_status.value,
                "new_status": status.value,
            })

    # =========================================================================
    # KONTROLLE
    # =========================================================================

    def pause_module(self, name: str, reason: str = "") -> bool:
        """
        Pausiert ein Modul.

        Args:
            name: Modul-Name
            reason: Grund für die Pause

        Returns:
            True wenn erfolgreich
        """
        module = self.modules.get(name)
        if not module:
            logger.warning(f"Modul {name} nicht gefunden")
            return False

        if not module.can_pause:
            logger.warning(f"Modul {name} kann nicht pausiert werden")
            return False

        if module.status == ModuleStatus.PAUSED:
            return True  # Bereits pausiert

        # Status ändern
        module.status = ModuleStatus.PAUSED

        # Callback ausführen wenn vorhanden
        if module.on_stop and self.brain:
            self._execute_callback(module.on_stop)

        # Tatsächliches Pausieren im Brain
        if self.brain:
            self._pause_brain_module(name)

        self.log_event("module_paused", {
            "module": name,
            "reason": reason,
        })

        logger.info(f"⏸️ Modul pausiert: {module.display_name} ({reason})")
        return True

    def activate_module(self, name: str, reason: str = "") -> bool:
        """
        Aktiviert ein Modul.

        Args:
            name: Modul-Name
            reason: Grund für die Aktivierung

        Returns:
            True wenn erfolgreich
        """
        module = self.modules.get(name)
        if not module:
            logger.warning(f"Modul {name} nicht gefunden")
            return False

        if module.status == ModuleStatus.ACTIVE:
            return True  # Bereits aktiv

        # Abhängigkeiten prüfen
        for dep in module.depends_on:
            dep_module = self.modules.get(dep)
            if dep_module and dep_module.status != ModuleStatus.ACTIVE:
                logger.warning(f"Abhängigkeit {dep} nicht aktiv")
                # Abhängigkeit auch aktivieren
                self.activate_module(dep, f"Abhängigkeit von {name}")

        # Status ändern
        module.status = ModuleStatus.ACTIVE
        module.last_activity = time.time()

        # Callback ausführen
        if module.on_start and self.brain:
            self._execute_callback(module.on_start)

        # Tatsächliches Aktivieren im Brain
        if self.brain:
            self._activate_brain_module(name)

        self.log_event("module_activated", {
            "module": name,
            "reason": reason,
        })

        logger.info(f"▶️ Modul aktiviert: {module.display_name} ({reason})")
        return True

    def restart_module(self, name: str, reason: str = "") -> bool:
        """Startet ein Modul neu"""
        module = self.modules.get(name)
        if not module:
            return False

        if not module.auto_restart:
            logger.warning(f"Modul {name} kann nicht neu gestartet werden")
            return False

        # Pausieren
        self.pause_module(name, f"Restart: {reason}")
        time.sleep(0.5)

        # Aktivieren
        self.activate_module(name, f"Restart: {reason}")

        module.restart_count += 1
        return True

    def disable_module(self, name: str, reason: str = "") -> bool:
        """Deaktiviert ein Modul komplett"""
        module = self.modules.get(name)
        if not module:
            return False

        if not module.can_disable:
            logger.warning(f"Modul {name} kann nicht deaktiviert werden")
            return False

        module.status = ModuleStatus.DISABLED

        if self.brain:
            self._disable_brain_module(name)

        self.log_event("module_disabled", {
            "module": name,
            "reason": reason,
        })

        logger.info(f"⏹️ Modul deaktiviert: {module.display_name}")
        return True

    # =========================================================================
    # BRAIN-INTEGRATION
    # =========================================================================

    def _pause_brain_module(self, name: str):
        """Pausiert ein Modul im Brain"""
        if not self.brain:
            return

        # Mapping von Control-Center Namen zu Brain-Attributen
        attr_map = {
            "conversation_engine": "conversation_engine",
            "cognitive_engine": "cognitive_engine",
            "inner_life": "inner_life",
            "autonomous_thinking": "autonomous_thinking",
            "web_curiosity": "web_curiosity",
            "creative_mind": "creative_mind",
            "media_discovery": "media_discovery",
            "proactive_messages": "proactive_intel",
            "discord_bot": "discord_bot",
            "voice_interface": "voice_interface",
        }

        attr = attr_map.get(name)
        if attr and hasattr(self.brain, attr):
            obj = getattr(self.brain, attr)
            if obj and hasattr(obj, 'pause'):
                obj.pause()
            elif obj and hasattr(obj, 'stop'):
                obj.stop()

    def _activate_brain_module(self, name: str):
        """Aktiviert ein Modul im Brain"""
        if not self.brain:
            return

        attr_map = {
            "conversation_engine": "conversation_engine",
            "cognitive_engine": "cognitive_engine",
            "inner_life": "inner_life",
            "autonomous_thinking": "autonomous_thinking",
            "web_curiosity": "web_curiosity",
            "creative_mind": "creative_mind",
            "media_discovery": "media_discovery",
            "proactive_messages": "proactive_intel",
            "discord_bot": "discord_bot",
            "voice_interface": "voice_interface",
        }

        attr = attr_map.get(name)
        if attr and hasattr(self.brain, attr):
            obj = getattr(self.brain, attr)
            if obj and hasattr(obj, 'resume'):
                obj.resume()
            elif obj and hasattr(obj, 'start'):
                obj.start()

    def _disable_brain_module(self, name: str):
        """Deaktiviert ein Modul im Brain komplett"""
        if not self.brain:
            return

        attr_map = {
            "discord_bot": "discord_bot",
            "voice_interface": "voice_interface",
        }

        attr = attr_map.get(name)
        if attr and hasattr(self.brain, attr):
            obj = getattr(self.brain, attr)
            if obj and hasattr(obj, 'close'):
                obj.close()
            setattr(self.brain, attr, None)

    def _execute_callback(self, callback_name: str):
        """Führt einen Callback aus"""
        if self.brain and hasattr(self.brain, callback_name):
            try:
                getattr(self.brain, callback_name)()
            except Exception as e:
                logger.error(f"Callback {callback_name} Fehler: {e}")

    # =========================================================================
    # AUTONOME ENTSCHEIDUNGEN
    # =========================================================================

    def start_autonomous_control(self):
        """Startet die autonome Kontrolle"""
        if self._running:
            return

        self._running = True

        # Watchdogs starten
        self._init_watchdogs()
        self.watchdog_manager.start()

        # Entscheidungs-Loop starten
        self._decision_thread = threading.Thread(
            target=self._decision_loop,
            name="ControlCenterDecisions",
            daemon=True
        )
        self._decision_thread.start()

        logger.info("🎛️ Autonome Kontrolle gestartet")

    def stop_autonomous_control(self):
        """Stoppt die autonome Kontrolle"""
        self._running = False
        self.watchdog_manager.stop()
        logger.info("🎛️ Autonome Kontrolle gestoppt")

    def _init_watchdogs(self):
        """Initialisiert Watchdogs für alle Module"""
        for name, module in self.modules.items():
            if module.priority.value >= ModulePriority.HIGH.value:
                config = WatchdogConfig(
                    module_name=name,
                    check_interval=30.0,
                    timeout=120.0,
                    max_errors=3,
                )
                self.watchdog_manager.add_watchdog(config)

    def _decision_loop(self):
        """Hauptschleife für autonome Entscheidungen"""
        while self._running:
            try:
                # Kontext sammeln
                context = self._gather_context()

                # Entscheidungen evaluieren
                decisions = self.decision_engine.evaluate(context)

                # Entscheidungen ausführen
                for decision in decisions:
                    self.decision_engine.execute_decision(decision)

            except Exception as e:
                logger.error(f"Entscheidungs-Loop Fehler: {e}")

            time.sleep(self._decision_interval)

    def _gather_context(self) -> Dict:
        """Sammelt aktuellen Kontext für Entscheidungen"""
        context = {
            "hour": datetime.now().hour,
            "energy": 0.5,
            "mood": "neutral",
            "mood_positive": False,
            "boredom": 0.0,
            "user_active": False,
        }

        if self.brain:
            # Energie
            if hasattr(self.brain, 'get_energy_level'):
                context["energy"] = self.brain.get_energy_level()

            # Stimmung
            if hasattr(self.brain, 'get_current_mood'):
                mood = self.brain.get_current_mood()
                context["mood"] = mood
                context["mood_positive"] = mood in ["happy", "excited", "content", "curious"]

            # Langeweile
            if hasattr(self.brain, 'autonomous_life') and self.brain.autonomous_life:
                if hasattr(self.brain.autonomous_life, 'boredom'):
                    context["boredom"] = self.brain.autonomous_life.boredom

        return context

    # =========================================================================
    # HILFSMETHODEN
    # =========================================================================

    def log_event(self, event_type: str, data: Dict = None):
        """Loggt ein Event"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "data": data or {},
        }
        self.event_log.append(event)

    def request_human_attention(self, message: str, priority: str = "normal"):
        """Fordert menschliche Aufmerksamkeit an"""
        self._attention_queue.append({
            "timestamp": time.time(),
            "message": message,
            "priority": priority,
        })

        # Auch über Discord senden wenn verfügbar
        if self.brain and hasattr(self.brain, 'send_proactive_discord'):
            self.brain.send_proactive_discord(
                f"⚠️ {message}",
                reason="attention_request"
            )

    def get_status_summary(self) -> Dict:
        """Erstellt eine Status-Zusammenfassung"""
        active = sum(1 for m in self.modules.values() if m.status == ModuleStatus.ACTIVE)
        paused = sum(1 for m in self.modules.values() if m.status == ModuleStatus.PAUSED)
        errors = sum(1 for m in self.modules.values() if m.status == ModuleStatus.ERROR)

        total_energy_cost = sum(
            m.energy_cost for m in self.modules.values()
            if m.status == ModuleStatus.ACTIVE
        )

        return {
            "total_modules": len(self.modules),
            "active": active,
            "paused": paused,
            "errors": errors,
            "total_energy_cost": total_energy_cost,
            "watchdogs_active": len(self.watchdog_manager.watchdogs),
            "recent_decisions": len(self.decision_engine.decisions),
            "attention_requests": len(self._attention_queue),
        }

    def get_module_list_for_holo(self) -> str:
        """
        Erstellt eine lesbare Liste aller Module für Holo.
        Kann in Prompts verwendet werden.
        """
        lines = ["Meine aktiven Systeme:\n"]

        # Nach Priorität sortieren
        sorted_modules = sorted(
            self.modules.items(),
            key=lambda x: x[1].priority.value,
            reverse=True
        )

        status_emoji = {
            ModuleStatus.ACTIVE: "✅",
            ModuleStatus.PAUSED: "⏸️",
            ModuleStatus.DISABLED: "⏹️",
            ModuleStatus.ERROR: "❌",
            ModuleStatus.UNKNOWN: "❓",
        }

        for name, module in sorted_modules:
            emoji = status_emoji.get(module.status, "❓")
            lines.append(f"{emoji} {module.display_name}: {module.description}")

        return "\n".join(lines)

    def can_i_do(self, action: str) -> Tuple[bool, str]:
        """
        Prüft ob Holo eine Aktion ausführen kann.

        Args:
            action: Gewünschte Aktion

        Returns:
            (kann_ausführen, grund)
        """
        # Mapping von Aktionen zu benötigten Modulen
        action_modules = {
            "recherchieren": ["web_curiosity"],
            "kreativ sein": ["creative_mind"],
            "träumen": ["inner_life"],
            "nachdenken": ["autonomous_thinking"],
            "musik entdecken": ["media_discovery"],
            "discord schreiben": ["discord_bot"],
            "sprechen": ["voice_interface"],
            "sehen": ["vision"],
        }

        required = action_modules.get(action.lower(), [])

        for module_name in required:
            module = self.modules.get(module_name)
            if not module:
                return False, f"Modul {module_name} nicht vorhanden"
            if module.status != ModuleStatus.ACTIVE:
                return False, f"{module.display_name} ist gerade pausiert"

        return True, "Kann ausgeführt werden"


# =============================================================================
# INTEGRATION MIT BESTEHENDEM SKILL-SYSTEM
# =============================================================================

class SkillSystemIntegration:
    """
    Integration des bestehenden holo_skill_system.py in das Control Center.

    Verbindet:
    - HoloSkillBridge (Skill-Ausführung)
    - SkillWatcher (Ordner-Überwachung)
    - HoloSkillSelector (Intent-Erkennung)
    - SkillComposer (Skill-Ketten)

    Mit dem Control Center für einheitliche Kontrolle.
    """

    def __init__(self, control_center: 'HoloControlCenter'):
        self.control_center = control_center
        self.skill_bridge = None
        self.skill_selector = None
        self.skill_composer = None
        self._initialized = False

    def initialize(self, skill_manager=None, database_manager=None):
        """
        Initialisiert das Skill-System.

        Args:
            skill_manager: Optional - pi_control SkillManager
            database_manager: Optional - HoloDatabaseManager
        """
        try:
            from holo_skill_system import (
                HoloSkillBridge,
                HoloSkillSelector,
                SkillComposer,
                create_holo_skill_system
            )

            # Skill-System erstellen
            self.skill_bridge, self.skill_selector, self.skill_composer = \
                create_holo_skill_system(
                    skill_manager=skill_manager,
                    database_manager=database_manager,
                    auto_watch=True,
                    watch_interval=30.0
                )

            self._initialized = True
            logger.info("🔧 Skill-System Integration initialisiert")

            # Skills als Module im Control Center registrieren
            self._register_skills_as_modules()

            return True

        except ImportError as e:
            logger.warning(f"Skill-System nicht verfügbar: {e}")
            return False
        except Exception as e:
            logger.error(f"Skill-System Initialisierung Fehler: {e}")
            return False

    def _register_skills_as_modules(self):
        """Registriert gefundene Skills als Module im Control Center"""
        if not self.skill_bridge:
            return

        # Entdecke Skills
        skills = self.skill_bridge.discover_skills()

        for skill in skills:
            if skill.name not in self.control_center.modules:
                # Skill als Modul registrieren
                info = ModuleInfo(
                    name=f"skill_{skill.name}",
                    display_name=f"Skill: {skill.name}",
                    description=skill.description[:100] if skill.description else f"Skill {skill.name}",
                    priority=ModulePriority.NORMAL,
                    status=ModuleStatus.ACTIVE if skill.enabled else ModuleStatus.DISABLED,
                    can_pause=True,
                    can_disable=True,
                    energy_cost=0.1,
                )
                self.control_center.modules[info.name] = info

        logger.info(f"📦 {len(skills)} Skills als Module registriert")

    async def execute_skill(self, skill_name: str, intent: str,
                           params: Dict = None) -> Optional[Dict]:
        """
        Führt einen Skill aus (über das bestehende System).

        Args:
            skill_name: Name des Skills
            intent: User-Intent
            params: Parameter

        Returns:
            Skill-Ergebnis oder None
        """
        if not self._initialized or not self.skill_bridge:
            return None

        # Prüfe ob Skill im Control Center aktiv ist
        module_name = f"skill_{skill_name}"
        if module_name in self.control_center.modules:
            module = self.control_center.modules[module_name]
            if module.status != ModuleStatus.ACTIVE:
                logger.warning(f"Skill {skill_name} ist pausiert")
                return {"success": False, "error": "Skill ist pausiert"}

        try:
            result = await self.skill_bridge.execute_skill(skill_name, intent, params)

            # Update Aktivität
            self.control_center.update_module_activity(module_name)

            return result.to_dict() if result else None

        except Exception as e:
            logger.error(f"Skill-Ausführung Fehler: {e}")
            return {"success": False, "error": str(e)}

    async def find_and_execute(self, request: str,
                               params: Dict = None) -> Optional[Dict]:
        """
        Findet den besten Skill für eine Anfrage und führt ihn aus.

        Args:
            request: User-Anfrage
            params: Optionale Parameter

        Returns:
            Ergebnis oder None
        """
        if not self._initialized or not self.skill_selector:
            return None

        try:
            result = await self.skill_selector.select_and_execute(request)
            return result.to_dict() if result else None
        except Exception as e:
            logger.error(f"Skill-Suche Fehler: {e}")
            return None

    def can_do(self, request: str) -> Tuple[bool, str, float]:
        """
        Prüft ob Holo eine Anfrage mit einem Skill erfüllen kann.

        Returns:
            (kann_ich, skill_name, confidence)
        """
        if not self._initialized or not self.skill_bridge:
            return (False, "", 0.0)

        return self.skill_bridge.can_i_do(request)

    def get_skill_summary(self) -> str:
        """Gibt eine Zusammenfassung aller Skills für Holo"""
        if not self._initialized or not self.skill_bridge:
            return "Skill-System nicht initialisiert."

        return self.skill_bridge.get_skill_summary_for_holo()

    def pause_skill(self, skill_name: str, reason: str = "") -> bool:
        """Pausiert einen Skill über das Control Center"""
        module_name = f"skill_{skill_name}"
        if module_name in self.control_center.modules:
            return self.control_center.pause_module(module_name, reason)
        return False

    def activate_skill(self, skill_name: str, reason: str = "") -> bool:
        """Aktiviert einen Skill über das Control Center"""
        module_name = f"skill_{skill_name}"
        if module_name in self.control_center.modules:
            return self.control_center.activate_module(module_name, reason)
        return False

    def get_skills_status(self) -> Dict[str, Dict]:
        """Gibt Status aller Skills zurück"""
        status = {}
        for name, module in self.control_center.modules.items():
            if name.startswith("skill_"):
                skill_name = name.replace("skill_", "")
                status[skill_name] = {
                    "active": module.status == ModuleStatus.ACTIVE,
                    "paused": module.status == ModuleStatus.PAUSED,
                    "energy_cost": module.energy_cost,
                    "last_activity": module.last_activity,
                }
        return status

    def learn_pattern(self, skill_name: str, pattern: str):
        """Fügt ein neues Pattern für einen Skill hinzu"""
        if self.skill_bridge:
            self.skill_bridge.learn_pattern(skill_name, pattern)

    def compose_skill_chain(self, request: str, max_skills: int = 3) -> List[str]:
        """Erstellt eine optimale Skill-Kette"""
        if self.skill_composer:
            return self.skill_composer.compose_chain(request, max_skills)
        return []


# =============================================================================
# ERWEITERTE CONTROL CENTER METHODEN
# =============================================================================

# Patch HoloControlCenter um Skill-Integration hinzuzufügen
_original_init = HoloControlCenter.__init__

def _patched_init(self, holo_brain=None, persist_path: str = None):
    """Erweiterte __init__ mit Skill-Integration"""
    _original_init(self, holo_brain, persist_path)

    # Skill-System Integration hinzufügen
    self.skill_system = SkillSystemIntegration(self)

    # Automatisch initialisieren wenn brain verfügbar
    if holo_brain:
        db = getattr(holo_brain, 'db', None)
        skill_manager = getattr(holo_brain, 'skill_manager', None)
        self.skill_system.initialize(
            skill_manager=skill_manager,
            database_manager=db
        )

HoloControlCenter.__init__ = _patched_init


# Neue Methoden für HoloControlCenter
def execute_skill(self, skill_name: str, intent: str, params: Dict = None):
    """Führt einen Skill aus"""
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.ensure_future(
            self.skill_system.execute_skill(skill_name, intent, params)
        )
        return future
    else:
        return asyncio.run(
            self.skill_system.execute_skill(skill_name, intent, params)
        )

def can_do_skill(self, request: str) -> Tuple[bool, str, float]:
    """Prüft ob ein Skill für die Anfrage existiert"""
    return self.skill_system.can_do(request)

def get_skill_summary(self) -> str:
    """Gibt Skill-Zusammenfassung zurück"""
    return self.skill_system.get_skill_summary()

def pause_skill(self, skill_name: str, reason: str = "") -> bool:
    """Pausiert einen Skill"""
    return self.skill_system.pause_skill(skill_name, reason)

def activate_skill(self, skill_name: str, reason: str = "") -> bool:
    """Aktiviert einen Skill"""
    return self.skill_system.activate_skill(skill_name, reason)

# Methoden zu HoloControlCenter hinzufügen
HoloControlCenter.execute_skill = execute_skill
HoloControlCenter.can_do_skill = can_do_skill
HoloControlCenter.get_skill_summary = get_skill_summary
HoloControlCenter.pause_skill = pause_skill
HoloControlCenter.activate_skill = activate_skill


# =============================================================================
# FACTORY & HILFSFUNKTIONEN
# =============================================================================

def create_control_center(holo_brain=None, persist_path: str = None) -> HoloControlCenter:
    """
    Factory-Funktion zum Erstellen des Control Centers.

    Args:
        holo_brain: HoloPersona Instanz
        persist_path: Optionaler Pfad für Persistenz

    Returns:
        HoloControlCenter Instanz
    """
    return HoloControlCenter(holo_brain=holo_brain, persist_path=persist_path)


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("🎛️ HOLO CONTROL CENTER TEST")
    print("=" * 60)

    # Control Center erstellen
    cc = create_control_center()

    # Status anzeigen
    print("\n📊 Status-Übersicht:")
    status = cc.get_status_summary()
    for key, value in status.items():
        print(f"  {key}: {value}")

    # Module anzeigen
    print("\n📦 Module:")
    print(cc.get_module_list_for_holo())

    # Test: Modul pausieren
    print("\n⏸️ Test: web_curiosity pausieren...")
    cc.pause_module("web_curiosity", "Test")

    # Test: Modul aktivieren
    print("▶️ Test: web_curiosity aktivieren...")
    cc.activate_module("web_curiosity", "Test")

    # Test: Entscheidung
    print("\n🧠 Test: Autonome Entscheidung (niedrige Energie)...")
    context = {"energy": 0.2, "hour": 14, "mood": "tired"}
    decisions = cc.decision_engine.evaluate(context)
    for d in decisions:
        print(f"  → {d.decision_type}: {d.reason}")

    print("\n✅ Control Center Test abgeschlossen!")
