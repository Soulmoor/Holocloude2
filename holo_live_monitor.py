#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holo Live Monitor v2.0 - Echtzeit-Systemuberwachung fur Holo

Basierend auf holo_tester.py, nutzt den IntelligentAnalyzer direkt.
Holo kann damit live sehen, wenn etwas nicht stimmt und darauf reagieren.

Features:
- Kontinuierliche Hintergrund-Uberwachung
- ALLE Tester-Funktionen verfugbar:
  * Security-Audit (SQL Injection, Secrets, etc.)
  * Code-Komplexitat (McCabe, Wartbarkeits-Index)
  * Code-Qualitat (bare excepts, TODOs, FIXMEs)
  * Config-Validierung
  * Runtime-Tests (Klassen, Funktionen)
  * Integration-Tests (Cross-Module)
  * Unused-Code-Detection
  * Cross-Module Methoden-Check
- Echtzeit-Benachrichtigungen bei Problemen
- Integration mit Control Center
- Proaktive Warnungen an Holo
- Automatische Recovery-Vorschlage

Author: Kira & Claude
Version: 2.0
"""

import ast
import sys
import time
import json
import logging
import threading
import importlib
import importlib.util
import traceback
import py_compile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum


logger = logging.getLogger("HoloLiveMonitor")


# =============================================================================
# ENUMS & KONFIGURATION
# =============================================================================

class IssueSeverity(Enum):
    """Schweregrad eines Problems"""
    CRITICAL = "critical"  # System funktioniert nicht
    ERROR = "error"        # Modul funktioniert nicht
    WARNING = "warning"    # Potentielles Problem
    INFO = "info"          # Hinweis


class IssueCategory(Enum):
    """Kategorie eines Problems"""
    SYNTAX = "syntax"
    IMPORT = "import"
    RUNTIME = "runtime"
    DEPENDENCY = "dependency"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CONFIG = "config"
    MEMORY = "memory"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class MonitorIssue:
    """Ein erkanntes Problem"""
    severity: IssueSeverity
    category: IssueCategory
    module: str
    message: str
    timestamp: float = field(default_factory=time.time)
    details: str = ""
    suggestion: str = ""
    line: int = 0
    auto_fixable: bool = False
    acknowledged: bool = False

    def to_dict(self) -> Dict:
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "module": self.module,
            "message": self.message,
            "timestamp": self.timestamp,
            "details": self.details,
            "suggestion": self.suggestion,
            "line": self.line,
            "auto_fixable": self.auto_fixable,
            "acknowledged": self.acknowledged,
        }

    def to_holo_message(self) -> str:
        """Formatiert das Problem als Nachricht fur Holo"""
        severity_emoji = {
            IssueSeverity.CRITICAL: "!!!",
            IssueSeverity.ERROR: "!!",
            IssueSeverity.WARNING: "!",
            IssueSeverity.INFO: "",
        }
        emoji = severity_emoji.get(self.severity, "")
        return f"{emoji} {self.module}: {self.message}"


@dataclass
class ModuleHealth:
    """Gesundheitszustand eines Moduls"""
    name: str
    path: Path
    is_healthy: bool = True
    last_check: float = 0.0
    syntax_ok: bool = True
    import_ok: bool = True
    import_error: str = ""
    issues: List[MonitorIssue] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    last_modified: float = 0.0
    file_hash: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "is_healthy": self.is_healthy,
            "syntax_ok": self.syntax_ok,
            "import_ok": self.import_ok,
            "import_error": self.import_error,
            "issues_count": len(self.issues),
            "classes": len(self.classes),
            "functions": len(self.functions),
            "dependencies": list(self.dependencies),
        }


@dataclass
class SystemHealth:
    """Gesamtgesundheit des Systems"""
    total_modules: int = 0
    healthy_modules: int = 0
    unhealthy_modules: int = 0
    critical_issues: int = 0
    error_issues: int = 0
    warning_issues: int = 0
    last_full_scan: float = 0.0

    def get_health_percentage(self) -> float:
        if self.total_modules == 0:
            return 100.0
        return (self.healthy_modules / self.total_modules) * 100

    def to_dict(self) -> Dict:
        return {
            "total_modules": self.total_modules,
            "healthy_modules": self.healthy_modules,
            "unhealthy_modules": self.unhealthy_modules,
            "health_percentage": self.get_health_percentage(),
            "critical_issues": self.critical_issues,
            "error_issues": self.error_issues,
            "warning_issues": self.warning_issues,
            "last_full_scan": self.last_full_scan,
        }


# =============================================================================
# HOLO LIVE MONITOR
# =============================================================================

class HoloLiveMonitor:
    """
    Echtzeit-Systemuberwachung fur Holo.

    Lauft im Hintergrund und benachrichtigt Holo bei Problemen.
    """

    def __init__(self,
                 project_dir: Path = None,
                 holo_brain=None,
                 control_center=None,
                 scan_interval: float = 60.0,
                 quick_check_interval: float = 10.0):
        """
        Args:
            project_dir: Projekt-Verzeichnis
            holo_brain: Referenz zu HoloBrain fur Benachrichtigungen
            control_center: Referenz zum Control Center
            scan_interval: Sekunden zwischen vollstandigen Scans
            quick_check_interval: Sekunden zwischen Quick-Checks
        """
        self.project_dir = project_dir or Path(__file__).parent
        self.brain = holo_brain
        self.control_center = control_center

        # Timing
        self.scan_interval = scan_interval
        self.quick_check_interval = quick_check_interval

        # State
        self.modules: Dict[str, ModuleHealth] = {}
        self.system_health = SystemHealth()
        self.issues: deque = deque(maxlen=500)
        self.unacknowledged_issues: List[MonitorIssue] = []

        # File Change Tracking
        self._file_mtimes: Dict[str, float] = {}

        # Threading
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._quick_check_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Callbacks
        self._on_issue_callbacks: List[Callable] = []
        self._on_recovery_callbacks: List[Callable] = []

        # Config
        self._ignore_modules: Set[str] = {"holo_tester", "__pycache__"}

        # Standard-Library Module (werden nicht gepruft)
        self._stdlib_modules = self._get_stdlib_modules()

        logger.info("HoloLiveMonitor initialisiert")

    def _get_stdlib_modules(self) -> Set[str]:
        """Holt alle Standard-Library Module"""
        stdlib = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else set()
        stdlib.update([
            'os', 'sys', 'json', 'time', 'datetime', 'logging', 'threading',
            'asyncio', 'pathlib', 're', 'typing', 'dataclasses', 'enum',
            'collections', 'functools', 'itertools', 'hashlib', 'sqlite3',
            'socket', 'http', 'urllib', 'ssl', 'abc', 'contextlib', 'io',
        ])
        return stdlib

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def start(self):
        """Startet den Monitor"""
        if self._running:
            return

        self._running = True

        # Initial-Scan
        self._full_scan()

        # Monitor-Thread starten
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="HoloLiveMonitor",
            daemon=True
        )
        self._monitor_thread.start()

        # Quick-Check Thread starten
        self._quick_check_thread = threading.Thread(
            target=self._quick_check_loop,
            name="HoloLiveMonitorQuick",
            daemon=True
        )
        self._quick_check_thread.start()

        logger.info("HoloLiveMonitor gestartet")

    def stop(self):
        """Stoppt den Monitor"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        if self._quick_check_thread:
            self._quick_check_thread.join(timeout=5.0)
        logger.info("HoloLiveMonitor gestoppt")

    # =========================================================================
    # MONITORING LOOPS
    # =========================================================================

    def _monitor_loop(self):
        """Hauptschleife fur vollstandige Scans"""
        while self._running:
            try:
                time.sleep(self.scan_interval)
                if self._running:
                    self._full_scan()
            except Exception as e:
                logger.error(f"Monitor-Loop Fehler: {e}")

    def _quick_check_loop(self):
        """Schnelle Checks auf Datei-Anderungen"""
        while self._running:
            try:
                time.sleep(self.quick_check_interval)
                if self._running:
                    self._quick_check()
            except Exception as e:
                logger.error(f"Quick-Check Fehler: {e}")

    # =========================================================================
    # SCANNING
    # =========================================================================

    def _full_scan(self):
        """Fuhrt einen vollstandigen Scan durch"""
        with self._lock:
            self._discover_modules()
            self._check_all_modules()
            self._update_system_health()
            self._check_dependencies()
            self.system_health.last_full_scan = time.time()

        logger.debug(f"Full-Scan abgeschlossen: {self.system_health.healthy_modules}/{self.system_health.total_modules} gesund")

    def _quick_check(self):
        """Schneller Check auf Anderungen"""
        changed_modules = []

        for name, health in self.modules.items():
            try:
                current_mtime = health.path.stat().st_mtime
                if current_mtime != health.last_modified:
                    changed_modules.append(name)
                    health.last_modified = current_mtime
            except Exception:
                pass

        # Nur geanderte Module neu prufen
        for name in changed_modules:
            with self._lock:
                self._check_module(name)

        if changed_modules:
            logger.debug(f"Quick-Check: {len(changed_modules)} Module geandert")
            self._update_system_health()

    def _discover_modules(self):
        """Entdeckt alle Python-Module im Projekt"""
        py_files = list(self.project_dir.glob("holo_*.py"))

        for py_file in py_files:
            name = py_file.stem
            if name in self._ignore_modules:
                continue

            if name not in self.modules:
                self.modules[name] = ModuleHealth(
                    name=name,
                    path=py_file,
                    last_modified=py_file.stat().st_mtime
                )
            else:
                self.modules[name].path = py_file

    def _check_all_modules(self):
        """Pruft alle Module"""
        for name in list(self.modules.keys()):
            self._check_module(name)

    def _check_module(self, name: str):
        """Pruft ein einzelnes Modul"""
        if name not in self.modules:
            return

        health = self.modules[name]
        health.issues.clear()
        health.is_healthy = True

        # 1. Syntax-Check
        if not self._check_syntax(health):
            health.is_healthy = False
            return

        # 2. Import-Check
        if not self._check_import(health):
            health.is_healthy = False

        # 3. AST-Analyse
        self._analyze_ast(health)

        health.last_check = time.time()

    def _check_syntax(self, health: ModuleHealth) -> bool:
        """Pruft die Syntax eines Moduls"""
        try:
            py_compile.compile(str(health.path), doraise=True)
            health.syntax_ok = True
            return True
        except py_compile.PyCompileError as e:
            health.syntax_ok = False
            issue = MonitorIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SYNTAX,
                module=health.name,
                message=f"Syntax-Fehler: {str(e)[:100]}",
                line=getattr(e, 'lineno', 0) or 0,
                suggestion="Prüfe die Syntax in der angegebenen Zeile"
            )
            health.issues.append(issue)
            self._report_issue(issue)
            return False

    def _check_import(self, health: ModuleHealth) -> bool:
        """Pruft ob das Modul importiert werden kann"""
        project_str = str(self.project_dir)
        if project_str not in sys.path:
            sys.path.insert(0, project_str)

        try:
            # Entferne gecachte Version
            if health.name in sys.modules:
                del sys.modules[health.name]

            # Stille Import-Versuche
            from io import StringIO
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = StringIO(), StringIO()

            try:
                spec = importlib.util.spec_from_file_location(health.name, health.path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[health.name] = mod
                    spec.loader.exec_module(mod)
                    health.import_ok = True
                    health.import_error = ""
                    return True
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

        except Exception as e:
            health.import_ok = False
            health.import_error = str(e)[:200]

            issue = MonitorIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.IMPORT,
                module=health.name,
                message=f"Import fehlgeschlagen: {str(e)[:100]}",
                details=traceback.format_exc()[:500],
                suggestion="Prüfe fehlende Abhängigkeiten oder Fehler in importierten Modulen"
            )
            health.issues.append(issue)
            self._report_issue(issue)
            return False

        return False

    def _analyze_ast(self, health: ModuleHealth):
        """Analysiert den AST eines Moduls"""
        try:
            source = health.path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(source)

            health.classes.clear()
            health.functions.clear()
            health.dependencies.clear()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    health.classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') or node.name == '__init__':
                        health.functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        base = alias.name.split('.')[0]
                        health.dependencies.add(base)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        base = node.module.split('.')[0]
                        health.dependencies.add(base)

        except Exception as e:
            logger.debug(f"AST-Analyse Fehler fur {health.name}: {e}")

    def _check_dependencies(self):
        """Pruft Abhangigkeiten zwischen Modulen"""
        project_modules = set(self.modules.keys())

        for name, health in self.modules.items():
            for dep in health.dependencies:
                # Nur Projekt-interne Abhangigkeiten prufen
                if dep in project_modules:
                    dep_health = self.modules.get(dep)
                    if dep_health and not dep_health.is_healthy:
                        issue = MonitorIssue(
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.DEPENDENCY,
                            module=name,
                            message=f"Abhangigkeit '{dep}' ist nicht gesund",
                            suggestion=f"Behebe zuerst die Probleme in {dep}"
                        )
                        health.issues.append(issue)
                        self._report_issue(issue)

    def _update_system_health(self):
        """Aktualisiert die Gesamtgesundheit"""
        healthy = 0
        unhealthy = 0
        critical = 0
        errors = 0
        warnings = 0

        for health in self.modules.values():
            if health.is_healthy:
                healthy += 1
            else:
                unhealthy += 1

            for issue in health.issues:
                if issue.severity == IssueSeverity.CRITICAL:
                    critical += 1
                elif issue.severity == IssueSeverity.ERROR:
                    errors += 1
                elif issue.severity == IssueSeverity.WARNING:
                    warnings += 1

        self.system_health.total_modules = len(self.modules)
        self.system_health.healthy_modules = healthy
        self.system_health.unhealthy_modules = unhealthy
        self.system_health.critical_issues = critical
        self.system_health.error_issues = errors
        self.system_health.warning_issues = warnings

    # =========================================================================
    # ISSUE REPORTING
    # =========================================================================

    def _report_issue(self, issue: MonitorIssue):
        """Meldet ein Problem"""
        self.issues.append(issue)

        # Zu unbestatigten Issues hinzufugen
        if not issue.acknowledged:
            self.unacknowledged_issues.append(issue)

        # Callbacks ausfuhren
        for callback in self._on_issue_callbacks:
            try:
                callback(issue)
            except Exception as e:
                logger.error(f"Issue-Callback Fehler: {e}")

        # Holo benachrichtigen
        self._notify_holo(issue)

        # Control Center informieren
        self._notify_control_center(issue)

    def _notify_holo(self, issue: MonitorIssue):
        """Benachrichtigt Holo uber ein Problem"""
        if not self.brain:
            return

        # Nur bei wichtigen Issues
        if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.ERROR]:
            message = issue.to_holo_message()

            # Versuche proaktive Nachricht zu senden
            if hasattr(self.brain, 'send_proactive_discord'):
                self.brain.send_proactive_discord(
                    f"System-Problem erkannt: {message}",
                    reason="monitor_alert"
                )

    def _notify_control_center(self, issue: MonitorIssue):
        """Informiert das Control Center"""
        if not self.control_center:
            return

        # Modul-Status aktualisieren
        if hasattr(self.control_center, 'update_module_status'):
            from holo_control_center import ModuleStatus
            if issue.severity == IssueSeverity.ERROR:
                self.control_center.update_module_status(issue.module, ModuleStatus.ERROR)

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_issue(self, callback: Callable):
        """Registriert einen Callback fur neue Issues"""
        self._on_issue_callbacks.append(callback)

    def on_recovery(self, callback: Callable):
        """Registriert einen Callback fur Recovery"""
        self._on_recovery_callbacks.append(callback)

    # =========================================================================
    # HOLO INTERFACE - Methoden die Holo direkt aufrufen kann
    # =========================================================================

    def get_status(self) -> Dict:
        """
        Gibt den aktuellen System-Status zuruck.

        Holo kann fragen: "Wie geht es meinen Systemen?"
        """
        return {
            "health": self.system_health.to_dict(),
            "modules": {
                name: health.to_dict()
                for name, health in self.modules.items()
            },
            "recent_issues": [
                issue.to_dict()
                for issue in list(self.issues)[-10:]
            ],
        }

    def get_health_summary(self) -> str:
        """
        Erstellt eine lesbare Zusammenfassung fur Holo.

        Holo kann sagen: "Mir geht es gut, alle 94 Module funktionieren!"
        Oder: "Ich habe 2 Probleme erkannt die behoben werden mussen."
        """
        health = self.system_health
        percentage = health.get_health_percentage()

        if percentage == 100:
            return f"Alle {health.total_modules} Module funktionieren einwandfrei!"
        elif percentage >= 90:
            return (f"{health.healthy_modules}/{health.total_modules} Module gesund "
                   f"({health.error_issues} Fehler, {health.warning_issues} Warnungen)")
        elif percentage >= 70:
            return (f"Einige Probleme: {health.unhealthy_modules} Module haben Fehler. "
                   f"{health.critical_issues} kritisch, {health.error_issues} Fehler.")
        else:
            return (f"Viele Probleme erkannt! Nur {health.healthy_modules}/{health.total_modules} "
                   f"Module funktionieren. Bitte prüfen!")

    def get_problems(self) -> List[str]:
        """
        Gibt alle aktuellen Probleme als Liste zuruck.

        Holo kann sagen: "Ich habe folgende Probleme erkannt: ..."
        """
        problems = []
        for health in self.modules.values():
            for issue in health.issues:
                problems.append(issue.to_holo_message())
        return problems

    def get_unhealthy_modules(self) -> List[str]:
        """
        Gibt Namen aller ungesunden Module zuruck.
        """
        return [
            name for name, health in self.modules.items()
            if not health.is_healthy
        ]

    def get_module_health(self, module_name: str) -> Optional[Dict]:
        """
        Gibt Gesundheit eines spezifischen Moduls zuruck.
        """
        if module_name in self.modules:
            return self.modules[module_name].to_dict()
        return None

    def acknowledge_issue(self, module_name: str = None):
        """
        Bestatigt Issues (Holo hat sie zur Kenntnis genommen).

        Args:
            module_name: Optional - nur Issues dieses Moduls bestatigen
        """
        for issue in self.unacknowledged_issues[:]:
            if module_name is None or issue.module == module_name:
                issue.acknowledged = True
                self.unacknowledged_issues.remove(issue)

    def has_critical_issues(self) -> bool:
        """Pruft ob kritische Issues vorhanden sind"""
        return self.system_health.critical_issues > 0

    def has_unacknowledged_issues(self) -> bool:
        """Pruft ob unbestatigte Issues vorhanden sind"""
        return len(self.unacknowledged_issues) > 0

    def force_check(self, module_name: str = None):
        """
        Erzwingt einen sofortigen Check.

        Args:
            module_name: Optional - nur dieses Modul prufen
        """
        if module_name:
            with self._lock:
                self._check_module(module_name)
                self._update_system_health()
        else:
            self._full_scan()

    def can_i_use(self, module_name: str) -> Tuple[bool, str]:
        """
        Holo fragt: "Kann ich dieses Modul benutzen?"

        Returns:
            (kann_nutzen, grund)
        """
        if module_name not in self.modules:
            return (False, f"Modul {module_name} nicht gefunden")

        health = self.modules[module_name]
        if not health.syntax_ok:
            return (False, f"Syntax-Fehler in {module_name}")
        if not health.import_ok:
            return (False, f"Import-Fehler: {health.import_error[:50]}")
        if not health.is_healthy:
            return (False, f"Modul hat {len(health.issues)} Probleme")

        return (True, "Modul ist gesund und nutzbar")

    def get_suggestions(self) -> List[str]:
        """
        Gibt Vorschlage zur Problembehebung.

        Holo kann sagen: "Ich schlage vor: ..."
        """
        suggestions = []
        for health in self.modules.values():
            for issue in health.issues:
                if issue.suggestion:
                    suggestions.append(f"{issue.module}: {issue.suggestion}")
        return suggestions[:10]  # Max 10 Vorschlage

    # =========================================================================
    # INTEGRATION MIT HOLO_BRAIN
    # =========================================================================

    def integrate_with_brain(self, brain):
        """
        Integriert den Monitor mit HoloBrain.

        Args:
            brain: HoloPersona/HoloBrain Instanz
        """
        self.brain = brain

        # Methoden zu brain hinzufugen falls moglich
        if brain:
            brain.live_monitor = self

            # Callback fur Issues registrieren
            def on_monitor_issue(issue: MonitorIssue):
                if hasattr(brain, 'on_system_issue'):
                    brain.on_system_issue(issue.to_dict())

            self.on_issue(on_monitor_issue)

        logger.info("LiveMonitor mit HoloBrain integriert")

    def integrate_with_control_center(self, control_center):
        """
        Integriert den Monitor mit dem Control Center.

        Args:
            control_center: HoloControlCenter Instanz
        """
        self.control_center = control_center

        # Als Modul registrieren
        if hasattr(control_center, 'register_module'):
            from holo_control_center import ModuleInfo, ModulePriority, ModuleStatus
            info = ModuleInfo(
                name="live_monitor",
                display_name="Live Monitor",
                description="Echtzeit-Systemuberwachung",
                priority=ModulePriority.HIGH,
                status=ModuleStatus.ACTIVE,
                can_pause=True,
                can_disable=False,
                energy_cost=0.05,
            )
            control_center.register_module(info)

        logger.info("LiveMonitor mit Control Center integriert")

    # =========================================================================
    # ERWEITERTE ANALYSE - Nutzt den holo_tester.py Analyzer
    # =========================================================================

    def run_deep_analysis(self, quick_mode: bool = True) -> Dict:
        """
        Fuhrt eine tiefe Analyse mit dem IntelligentAnalyzer durch.

        Nutzt alle Funktionen aus holo_tester.py:
        - Security-Audit
        - Code-Komplexitat
        - Code-Qualitat
        - Config-Validierung
        - Runtime-Tests
        - Integration-Tests
        - Unused-Code-Detection

        Args:
            quick_mode: True fur schnelle Analyse, False fur volle Analyse

        Returns:
            Dict mit Analyse-Ergebnissen
        """
        try:
            from holo_tester import IntelligentAnalyzer
        except ImportError:
            return {"error": "holo_tester nicht verfugbar"}

        analyzer = IntelligentAnalyzer(self.project_dir)
        analysis = analyzer.analyze(quick_mode=quick_mode)

        # Extrahiere wichtige Ergebnisse
        results = {
            "modules": {
                "total": len(analysis.modules),
                "import_ok": len(analysis.import_successes),
                "import_failed": len(analysis.import_failures),
            },
            "security": {
                "issues_count": len(analysis.all_security_issues),
                "issues": [
                    {
                        "severity": i.severity,
                        "module": i.module,
                        "message": i.message,
                        "line": i.line,
                    }
                    for i in analysis.all_security_issues[:10]
                ],
            },
            "quality": {
                "issues_count": len(analysis.all_quality_issues),
                "bare_excepts": analysis.bare_excepts_count,
                "mutable_defaults": analysis.mutable_defaults_count,
                "todos": analysis.todos_count,
                "fixmes": analysis.fixmes_count,
                "long_functions": analysis.long_functions_count,
            },
            "complexity": {
                "total": analysis.total_complexity,
                "average": analysis.avg_complexity,
                "complex_functions": analysis.complex_functions[:5],
            },
            "integration": {
                "passed": analysis.integration_tests_passed,
                "failed": analysis.integration_tests_failed,
            },
            "runtime": {
                "passed": analysis.runtime_tests_passed,
                "failed": analysis.runtime_tests_failed,
            },
            "unused": {
                "imports": len(analysis.unused_imports),
                "functions": len(analysis.unused_functions),
                "classes": len(analysis.unused_classes),
            },
            "config": {
                "issues": analysis.config_issues[:5],
            },
            "database": {
                "tables": len(analysis.db_tables),
                "issues": analysis.db_issues[:5],
            },
        }

        # Erstelle Issues aus den Ergebnissen
        self._create_issues_from_analysis(analysis)

        return results

    def _create_issues_from_analysis(self, analysis):
        """Erstellt MonitorIssues aus der Analyse"""
        # Security Issues
        for si in analysis.all_security_issues:
            if si.severity in ["critical", "high"]:
                issue = MonitorIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.SECURITY,
                    module=si.module,
                    message=f"Sicherheit: {si.message}",
                    line=si.line,
                    suggestion=si.recommendation,
                )
                self._report_issue(issue)

        # Import Failures (als Fehler)
        for mod_name, error in analysis.import_failures:
            if mod_name in self.modules:
                continue  # Bereits erfasst
            issue = MonitorIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.IMPORT,
                module=mod_name,
                message=f"Import: {error[:80]}",
            )
            self._report_issue(issue)

        # Sehr komplexe Funktionen
        for mod_name, func_name, complexity in analysis.complex_functions:
            if complexity > 15:
                issue = MonitorIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.PERFORMANCE,
                    module=mod_name,
                    message=f"Hohe Komplexitat: {func_name} (CC={complexity})",
                    suggestion="Refactoring empfohlen"
                )
                self._report_issue(issue)

    def get_security_issues(self) -> List[Dict]:
        """
        Gibt alle Sicherheitsprobleme zuruck.

        Holo kann sagen: "Ich habe Sicherheitsbedenken bei..."
        """
        try:
            from holo_tester import IntelligentAnalyzer
            analyzer = IntelligentAnalyzer(self.project_dir)
            analysis = analyzer.analyze(quick_mode=True)

            # Nur Security-Audit machen
            analyzer._security_audit()

            return [
                {
                    "severity": i.severity,
                    "module": i.module,
                    "message": i.message,
                    "line": i.line,
                    "code": i.code,
                    "recommendation": i.recommendation,
                }
                for i in analysis.all_security_issues
            ]
        except ImportError:
            return []

    def get_code_quality(self) -> Dict:
        """
        Gibt Code-Qualitatsmetriken zuruck.

        Holo kann sagen: "Meine Code-Qualitat ist bei X%..."
        """
        try:
            from holo_tester import IntelligentAnalyzer
            analyzer = IntelligentAnalyzer(self.project_dir)
            analysis = analyzer.analyze(quick_mode=True)

            return {
                "total_lines": analysis.total_lines,
                "total_functions": analysis.total_functions,
                "total_classes": analysis.total_classes,
                "avg_complexity": analysis.avg_complexity,
                "avg_docstring_coverage": analysis.avg_docstring_coverage,
                "avg_type_coverage": analysis.avg_type_coverage,
                "quality_issues": len(analysis.all_quality_issues),
                "bare_excepts": analysis.bare_excepts_count,
                "todos": analysis.todos_count,
                "fixmes": analysis.fixmes_count,
            }
        except ImportError:
            return {}

    def get_complexity_report(self) -> Dict:
        """
        Gibt Komplexitats-Report zuruck.

        Holo kann sagen: "Diese Funktionen sind sehr komplex..."
        """
        try:
            from holo_tester import IntelligentAnalyzer
            analyzer = IntelligentAnalyzer(self.project_dir)
            analysis = analyzer.analyze(quick_mode=True)

            # Top komplexe Module
            module_complexity = {}
            for mod_name, module in analysis.modules.items():
                if module.complexity_info:
                    module_complexity[mod_name] = {
                        "avg": module.complexity_info.avg_complexity,
                        "max": module.complexity_info.max_complexity,
                        "maintainability": module.complexity_info.maintainability_index,
                        "most_complex": module.complexity_info.max_complex_function,
                    }

            return {
                "total_complexity": analysis.total_complexity,
                "avg_complexity": analysis.avg_complexity,
                "complex_functions": [
                    {"module": m, "function": f, "complexity": c}
                    for m, f, c in analysis.complex_functions[:10]
                ],
                "modules": module_complexity,
            }
        except ImportError:
            return {}

    def get_unused_code(self) -> Dict:
        """
        Gibt unbenutzten Code zuruck.

        Holo kann sagen: "Diese Funktionen werden nicht benutzt..."
        """
        try:
            from holo_tester import IntelligentAnalyzer
            analyzer = IntelligentAnalyzer(self.project_dir)
            analysis = analyzer.analyze(quick_mode=False)  # Volle Analyse nötig

            return {
                "unused_imports": analysis.unused_imports[:20],
                "unused_functions": analysis.unused_functions[:20],
                "unused_classes": analysis.unused_classes[:10],
            }
        except ImportError:
            return {}

    def get_integration_status(self) -> Dict:
        """
        Gibt Integration-Status zuruck.

        Holo kann sagen: "Alle Module kommunizieren korrekt..."
        """
        try:
            from holo_tester import IntelligentAnalyzer
            analyzer = IntelligentAnalyzer(self.project_dir)
            analysis = analyzer.analyze(quick_mode=True)

            failed = [
                {"from": f, "to": t, "error": e}
                for f, t, ok, e in analysis.integration_results
                if not ok
            ]

            return {
                "passed": analysis.integration_tests_passed,
                "failed": analysis.integration_tests_failed,
                "failures": failed[:10],
                "circular_deps": analysis.circular_deps,
            }
        except ImportError:
            return {}

    def get_full_report_for_holo(self) -> str:
        """
        Erstellt einen vollstandigen Report fur Holo.

        Holo kann sagen: "Hier ist mein Systemstatus..."
        """
        lines = ["=== HOLO SYSTEMSTATUS ===", ""]

        # Basis-Gesundheit
        lines.append(f"Gesundheit: {self.get_health_summary()}")
        lines.append("")

        # Erweiterte Analyse
        try:
            results = self.run_deep_analysis(quick_mode=True)

            # Module
            lines.append(f"Module: {results['modules']['import_ok']}/{results['modules']['total']} OK")

            # Sicherheit
            if results['security']['issues_count'] > 0:
                lines.append(f"Sicherheit: {results['security']['issues_count']} Hinweise")

            # Qualitat
            lines.append(f"Qualitat: {results['quality']['bare_excepts']} bare excepts, "
                        f"{results['quality']['todos']} TODOs")

            # Komplexitat
            lines.append(f"Komplexitat: durchschnittlich {results['complexity']['average']:.1f}")

            # Integration
            lines.append(f"Integration: {results['integration']['passed']} OK, "
                        f"{results['integration']['failed']} Fehler")

            # Ungenutzter Code
            lines.append(f"Ungenutzter Code: {results['unused']['functions']} Funktionen, "
                        f"{results['unused']['imports']} Imports")

        except Exception as e:
            lines.append(f"Erweiterte Analyse nicht verfugbar: {e}")

        return "\n".join(lines)


# =============================================================================
# FACTORY FUNKTION
# =============================================================================

def create_live_monitor(project_dir: Path = None,
                       holo_brain=None,
                       control_center=None,
                       auto_start: bool = True) -> HoloLiveMonitor:
    """
    Erstellt einen HoloLiveMonitor.

    Args:
        project_dir: Projekt-Verzeichnis
        holo_brain: HoloPersona Instanz
        control_center: HoloControlCenter Instanz
        auto_start: Automatisch starten

    Returns:
        HoloLiveMonitor Instanz
    """
    monitor = HoloLiveMonitor(
        project_dir=project_dir,
        holo_brain=holo_brain,
        control_center=control_center
    )

    if holo_brain:
        monitor.integrate_with_brain(holo_brain)

    if control_center:
        monitor.integrate_with_control_center(control_center)

    if auto_start:
        monitor.start()

    return monitor


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("HOLO LIVE MONITOR TEST")
    print("=" * 60)

    # Monitor erstellen
    monitor = create_live_monitor(auto_start=False)

    # Einmal scannen
    monitor._full_scan()

    # Status ausgeben
    print(f"\n{monitor.get_health_summary()}")

    print(f"\nModule-Status:")
    for name, health in sorted(monitor.modules.items()):
        status = "OK" if health.is_healthy else "!!FEHLER"
        print(f"  {status} {name}: {len(health.classes)} Klassen, {len(health.functions)} Funktionen")

    # Probleme ausgeben
    problems = monitor.get_problems()
    if problems:
        print(f"\n{len(problems)} Probleme gefunden:")
        for p in problems[:10]:
            print(f"  - {p}")
    else:
        print("\nKeine Probleme gefunden!")

    # Vorschlage
    suggestions = monitor.get_suggestions()
    if suggestions:
        print(f"\nVorschlage:")
        for s in suggestions[:5]:
            print(f"  - {s}")

    print("\nTest abgeschlossen!")
