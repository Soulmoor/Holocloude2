#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║             HOLOCLOUDE INTELLIGENT SYSTEM TESTER v3.0                        ║
║                                                                              ║
║  INTELLIGENT - Versteht das Projekt:                                         ║
║    • Analysiert Modul-Zweck aus Namen und Docstrings                         ║
║    • Erkennt fehlende und ungenutzte Imports                                 ║
║    • Baut Dependency-Graph auf                                               ║
║    • Findet zirkuläre Abhängigkeiten                                         ║
║    • Prüft ob Module zusammenarbeiten                                        ║
║    • Erkennt fehlende Funktionen basierend auf Konventionen                  ║
║    • Validiert Config gegen tatsächliche Nutzung                             ║
║                                                                              ║
║  Verwendung:                                                                 ║
║      python holo_tester.py                 # Intelligente Analyse            ║
║      python holo_tester.py --explain       # Erklärt was jedes Modul tut     ║
║      python holo_tester.py --graph         # Zeigt Dependency-Graph          ║
║      python holo_tester.py --problems      # Nur Probleme anzeigen           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import ast
import json
import time
import socket
import sqlite3
import re
import importlib
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any, NamedTuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum, auto

# =============================================================================
# TERMINAL FARBEN
# =============================================================================

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls):
        for attr in ["GREEN", "RED", "YELLOW", "BLUE", "CYAN", "MAGENTA", "BOLD", "DIM", "RESET"]:
            setattr(cls, attr, "")

if not sys.stdout.isatty():
    Colors.disable()


# =============================================================================
# MODUL-KATEGORIEN & ERWARTUNGEN
# =============================================================================

class ModuleCategory(Enum):
    """Kategorien von Modulen basierend auf Namenskonventionen"""
    CORE = auto()        # Kern-Funktionalität
    DATABASE = auto()    # Datenbank-bezogen
    NLP = auto()         # Natural Language Processing
    AUDIO = auto()       # Audio/Sprache
    VISION = auto()      # Bild/Video
    PERSONALITY = auto() # Persönlichkeit/Emotionen
    INTEGRATION = auto() # Integration/Schnittstellen
    UTILITY = auto()     # Hilfsfunktionen
    CONFIG = auto()      # Konfiguration
    UNKNOWN = auto()     # Unbekannt


# Was erwarten wir von bestimmten Modul-Typen?
MODULE_EXPECTATIONS = {
    # Pattern -> (Kategorie, erwartete Klassen/Funktionen, erwartete Imports)
    r"holo_brain": (ModuleCategory.CORE, ["HoloPersona", "process_message"], ["json", "logging"]),
    r"holo_database|holo_db": (ModuleCategory.DATABASE, ["Database", "connect", "query"], ["sqlite3"]),
    r"holo_nlp|holo_.*understanding|holo_.*language": (ModuleCategory.NLP, ["analyze", "parse", "tokenize"], ["re"]),
    r"holo_audio|holo_voice|holo_speech": (ModuleCategory.AUDIO, ["play", "record", "transcribe"], []),
    r"holo_vision|holo_image|holo_video": (ModuleCategory.VISION, ["capture", "analyze", "detect"], []),
    r"holo_personality|holo_emotion|holo_mood": (ModuleCategory.PERSONALITY, ["Emotion", "get_mood"], []),
    r"holo_.*interface|holo_.*handler|holo_.*receiver": (ModuleCategory.INTEGRATION, ["handle", "receive", "send"], []),
    r"holo_config": (ModuleCategory.CONFIG, ["load_config", "get_config"], ["json", "os"]),
    r"holo_error|holo_log": (ModuleCategory.UTILITY, ["log", "error", "handle"], ["logging"]),
    r"holo_tool|holo_util|holo_helper": (ModuleCategory.UTILITY, [], []),
}


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class Issue:
    """Ein gefundenes Problem"""
    severity: str  # "error", "warning", "info"
    category: str  # "import", "function", "dependency", etc.
    module: str
    message: str
    suggestion: str = ""
    line: int = 0


@dataclass
class ModuleAnalysis:
    """Tiefe Analyse eines Moduls"""
    name: str
    path: Path
    size_bytes: int
    lines: int = 0

    # Aus AST
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: Dict[str, List[str]] = field(default_factory=dict)  # modul -> [namen]
    from_imports: Dict[str, List[str]] = field(default_factory=dict)  # modul -> [namen]

    # Aus Docstring
    docstring: str = ""
    purpose: str = ""  # Erkannter Zweck

    # Kategorisierung
    category: ModuleCategory = ModuleCategory.UNKNOWN

    # Verwendung
    uses_modules: Set[str] = field(default_factory=set)  # Module die dieses Modul verwendet
    used_by_modules: Set[str] = field(default_factory=set)  # Module die dieses Modul verwenden

    # Umgebungsvariablen
    env_vars_used: List[str] = field(default_factory=list)
    config_keys_used: List[str] = field(default_factory=list)

    # Status
    syntax_ok: bool = True
    import_ok: bool = False
    issues: List[Issue] = field(default_factory=list)

    # Erwartungen
    expected_items: List[str] = field(default_factory=list)
    missing_items: List[str] = field(default_factory=list)


@dataclass
class ProjectAnalysis:
    """Gesamtanalyse des Projekts"""
    modules: Dict[str, ModuleAnalysis] = field(default_factory=dict)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    reverse_deps: Dict[str, Set[str]] = field(default_factory=dict)
    circular_deps: List[List[str]] = field(default_factory=list)
    orphan_modules: List[str] = field(default_factory=list)
    all_issues: List[Issue] = field(default_factory=list)
    config: Dict = field(default_factory=dict)

    # Statistiken
    total_lines: int = 0
    total_classes: int = 0
    total_functions: int = 0


# =============================================================================
# INTELLIGENTER PROJEKT-ANALYZER
# =============================================================================

class IntelligentAnalyzer:
    """Analysiert das Projekt intelligent und versteht Zusammenhänge"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.analysis = ProjectAnalysis()
        self.stdlib_modules = self._get_stdlib_modules()

    def analyze(self) -> ProjectAnalysis:
        """Führt komplette intelligente Analyse durch"""
        print(f"\n{Colors.DIM}Analysiere Projekt intelligent...{Colors.RESET}")

        self._load_config()
        self._discover_modules()
        self._analyze_all_modules()
        self._build_dependency_graph()
        self._find_circular_dependencies()
        self._find_orphan_modules()
        self._check_module_expectations()
        self._validate_imports()
        self._check_config_usage()
        self._calculate_statistics()

        return self.analysis

    # =========================================================================
    # CONFIG
    # =========================================================================

    def _load_config(self):
        """Lädt config.json"""
        config_path = self.project_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    self.analysis.config = json.load(f)
            except Exception as e:
                self.analysis.all_issues.append(Issue(
                    severity="error",
                    category="config",
                    module="config.json",
                    message=f"Config nicht lesbar: {e}"
                ))

    # =========================================================================
    # MODUL-DISCOVERY
    # =========================================================================

    def _discover_modules(self):
        """Findet alle Python-Module"""
        py_files = list(self.project_dir.glob("*.py"))
        py_files.extend(self.project_dir.glob("**/*.py"))

        for py_file in sorted(set(py_files)):
            if "__pycache__" in str(py_file):
                continue
            if py_file.name == "holo_tester.py":
                continue

            name = py_file.stem
            self.analysis.modules[name] = ModuleAnalysis(
                name=name,
                path=py_file,
                size_bytes=py_file.stat().st_size
            )

    # =========================================================================
    # TIEFE MODUL-ANALYSE
    # =========================================================================

    def _analyze_all_modules(self):
        """Analysiert alle Module im Detail"""
        for name, module in self.analysis.modules.items():
            self._analyze_module(module)

    def _analyze_module(self, module: ModuleAnalysis):
        """Analysiert ein einzelnes Modul tiefgehend"""
        try:
            source = module.path.read_text(encoding="utf-8", errors="ignore")
            module.lines = len(source.splitlines())

            # AST Parsing
            tree = ast.parse(source)
            module.syntax_ok = True

            # Docstring extrahieren
            module.docstring = ast.get_docstring(tree) or ""
            module.purpose = self._extract_purpose(module.docstring, module.name)

            # Kategorie bestimmen
            module.category = self._categorize_module(module.name, module.docstring)

            for node in ast.walk(tree):
                self._analyze_node(node, module, source)

            # Env-Vars und Config-Keys finden
            module.env_vars_used = self._find_env_vars(source)
            module.config_keys_used = self._find_config_keys(source)

        except SyntaxError as e:
            module.syntax_ok = False
            module.issues.append(Issue(
                severity="error",
                category="syntax",
                module=module.name,
                message=f"Syntax-Fehler in Zeile {e.lineno}: {e.msg}",
                line=e.lineno or 0
            ))
        except Exception as e:
            module.issues.append(Issue(
                severity="error",
                category="parse",
                module=module.name,
                message=f"Parse-Fehler: {str(e)}"
            ))

    def _analyze_node(self, node: ast.AST, module: ModuleAnalysis, source: str):
        """Analysiert einen AST-Knoten"""

        # Klassen
        if isinstance(node, ast.ClassDef):
            module.classes.append(node.name)

        # Funktionen (nur top-level)
        elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
            if not node.name.startswith("_") or node.name in ["__init__", "__call__"]:
                module.functions.append(node.name)

        # import X
        elif isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split(".")[0]
                if base_module not in module.imports:
                    module.imports[base_module] = []
                module.imports[base_module].append(alias.name)
                module.uses_modules.add(base_module)

        # from X import Y
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split(".")[0]
                if base_module not in module.from_imports:
                    module.from_imports[base_module] = []
                for alias in node.names:
                    module.from_imports[base_module].append(alias.name)
                module.uses_modules.add(base_module)

    def _extract_purpose(self, docstring: str, name: str) -> str:
        """Extrahiert den Zweck eines Moduls aus Docstring oder Namen"""
        if docstring:
            # Erste Zeile oder bis zum ersten Absatz
            first_line = docstring.split("\n")[0].strip()
            if first_line:
                return first_line[:100]

        # Aus Namen ableiten
        parts = name.replace("holo_", "").replace("_", " ").title()
        return f"Holocloude {parts} Modul"

    def _categorize_module(self, name: str, docstring: str) -> ModuleCategory:
        """Kategorisiert ein Modul basierend auf Namen und Inhalt"""
        name_lower = name.lower()
        doc_lower = (docstring or "").lower()

        for pattern, (category, _, _) in MODULE_EXPECTATIONS.items():
            if re.search(pattern, name_lower):
                return category

        # Aus Docstring
        if "database" in doc_lower or "sqlite" in doc_lower:
            return ModuleCategory.DATABASE
        if "nlp" in doc_lower or "language" in doc_lower or "understanding" in doc_lower:
            return ModuleCategory.NLP
        if "audio" in doc_lower or "voice" in doc_lower or "speech" in doc_lower:
            return ModuleCategory.AUDIO
        if "vision" in doc_lower or "image" in doc_lower or "camera" in doc_lower:
            return ModuleCategory.VISION
        if "emotion" in doc_lower or "personality" in doc_lower or "mood" in doc_lower:
            return ModuleCategory.PERSONALITY

        return ModuleCategory.UNKNOWN

    def _find_env_vars(self, source: str) -> List[str]:
        """Findet alle verwendeten Umgebungsvariablen"""
        pattern = r'os\.(?:getenv|environ\.get|environ\[)["\']([A-Z_][A-Z0-9_]*)["\']'
        return list(set(re.findall(pattern, source)))

    def _find_config_keys(self, source: str) -> List[str]:
        """Findet alle verwendeten Config-Keys"""
        patterns = [
            r'get_config\(["\']([^"\']+)["\']',
            r'config\.get\(["\']([^"\']+)["\']',
            r'config\[["\']([^"\']+)["\']\]',
            r'self\.config\[["\']([^"\']+)["\']\]',
        ]
        keys = []
        for pattern in patterns:
            keys.extend(re.findall(pattern, source))
        return list(set(keys))

    # =========================================================================
    # DEPENDENCY GRAPH
    # =========================================================================

    def _build_dependency_graph(self):
        """Baut den Abhängigkeitsgraphen auf"""
        project_modules = set(self.analysis.modules.keys())

        for name, module in self.analysis.modules.items():
            # Nur Projekt-interne Abhängigkeiten
            deps = module.uses_modules & project_modules
            self.analysis.dependency_graph[name] = deps

            # Reverse Dependencies
            for dep in deps:
                if dep not in self.analysis.reverse_deps:
                    self.analysis.reverse_deps[dep] = set()
                self.analysis.reverse_deps[dep].add(name)

                # Setze used_by im Modul
                if dep in self.analysis.modules:
                    self.analysis.modules[dep].used_by_modules.add(name)

    def _find_circular_dependencies(self):
        """Findet zirkuläre Abhängigkeiten"""
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.analysis.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    cycle = dfs(neighbor, path)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Zyklus gefunden
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        for module in self.analysis.modules:
            if module not in visited:
                cycle = dfs(module, [])
                if cycle:
                    self.analysis.circular_deps.append(cycle)
                    self.analysis.all_issues.append(Issue(
                        severity="warning",
                        category="dependency",
                        module=cycle[0],
                        message=f"Zirkuläre Abhängigkeit: {' -> '.join(cycle)}",
                        suggestion="Refactoring nötig um Zyklus aufzubrechen"
                    ))

    def _find_orphan_modules(self):
        """Findet Module die von keinem anderen Modul verwendet werden"""
        entry_points = {"holo_brain", "holo_tester", "__main__"}

        for name, module in self.analysis.modules.items():
            if name in entry_points:
                continue
            if not module.used_by_modules:
                self.analysis.orphan_modules.append(name)
                # Kein Issue - kann gewollt sein (CLI tools, etc.)

    # =========================================================================
    # ERWARTUNGS-PRÜFUNG
    # =========================================================================

    def _check_module_expectations(self):
        """Prüft ob Module erwartete Elemente enthalten"""
        for name, module in self.analysis.modules.items():
            for pattern, (category, expected_items, expected_imports) in MODULE_EXPECTATIONS.items():
                if re.search(pattern, name.lower()):
                    module.expected_items = expected_items.copy()

                    # Prüfe erwartete Klassen/Funktionen
                    for item in expected_items:
                        item_lower = item.lower()
                        found = False

                        # Suche in Klassen und Funktionen (case-insensitive partial match)
                        for cls in module.classes:
                            if item_lower in cls.lower():
                                found = True
                                break
                        if not found:
                            for func in module.functions:
                                if item_lower in func.lower():
                                    found = True
                                    break

                        if not found:
                            module.missing_items.append(item)

                    # Prüfe erwartete Imports
                    all_imports = set(module.imports.keys()) | set(module.from_imports.keys())
                    for exp_import in expected_imports:
                        if exp_import not in all_imports:
                            module.issues.append(Issue(
                                severity="info",
                                category="import",
                                module=name,
                                message=f"Erwarteter Import '{exp_import}' fehlt",
                                suggestion=f"Füge 'import {exp_import}' hinzu falls benötigt"
                            ))

                    break

    # =========================================================================
    # IMPORT-VALIDIERUNG
    # =========================================================================

    def _validate_imports(self):
        """Validiert alle Imports"""
        project_modules = set(self.analysis.modules.keys())

        for name, module in self.analysis.modules.items():
            all_imports = set(module.imports.keys()) | set(module.from_imports.keys())

            for imp in all_imports:
                # Ist es ein Projekt-Modul?
                if imp in project_modules:
                    continue

                # Ist es stdlib?
                if imp in self.stdlib_modules:
                    continue

                # Versuche zu importieren
                try:
                    importlib.import_module(imp)
                except ImportError:
                    module.issues.append(Issue(
                        severity="error",
                        category="import",
                        module=name,
                        message=f"Import '{imp}' nicht gefunden",
                        suggestion=f"Installiere mit: pip install {imp}"
                    ))
                except Exception:
                    pass  # Andere Fehler ignorieren

            # Prüfe auf ungenutzte Imports (vereinfacht)
            # TODO: Vollständige Nutzungsanalyse

    # =========================================================================
    # CONFIG VALIDIERUNG
    # =========================================================================

    def _check_config_usage(self):
        """Prüft ob Config-Keys tatsächlich existieren"""
        if not self.analysis.config:
            return

        def get_all_keys(d: dict, prefix: str = "") -> Set[str]:
            keys = set()
            for k, v in d.items():
                full_key = f"{prefix}.{k}" if prefix else k
                keys.add(full_key)
                if isinstance(v, dict):
                    keys.update(get_all_keys(v, full_key))
            return keys

        available_keys = get_all_keys(self.analysis.config)

        for name, module in self.analysis.modules.items():
            for used_key in module.config_keys_used:
                # Prüfe ob Key existiert (auch partielle Matches)
                found = any(used_key in key or key.endswith(used_key) for key in available_keys)
                if not found and not used_key.startswith("HOLO_"):
                    module.issues.append(Issue(
                        severity="warning",
                        category="config",
                        module=name,
                        message=f"Config-Key '{used_key}' nicht in config.json gefunden",
                        suggestion="Prüfe ob der Key korrekt ist oder füge ihn zur Config hinzu"
                    ))

    # =========================================================================
    # STATISTIKEN
    # =========================================================================

    def _calculate_statistics(self):
        """Berechnet Projekt-Statistiken"""
        for module in self.analysis.modules.values():
            self.analysis.total_lines += module.lines
            self.analysis.total_classes += len(module.classes)
            self.analysis.total_functions += len(module.functions)

            # Sammle alle Issues
            self.analysis.all_issues.extend(module.issues)

    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================

    def _get_stdlib_modules(self) -> Set[str]:
        """Gibt Standard-Library-Module zurück"""
        return {
            "os", "sys", "json", "time", "datetime", "pathlib", "typing",
            "collections", "itertools", "functools", "re", "logging",
            "threading", "multiprocessing", "subprocess", "socket",
            "sqlite3", "hashlib", "base64", "urllib", "http", "email",
            "html", "xml", "csv", "io", "tempfile", "shutil", "glob",
            "random", "math", "statistics", "decimal", "fractions",
            "copy", "pickle", "shelve", "dbm", "gzip", "zipfile",
            "tarfile", "configparser", "argparse", "getopt", "warnings",
            "traceback", "inspect", "abc", "contextlib", "dataclasses",
            "enum", "ast", "dis", "gc", "weakref", "array", "struct",
            "codecs", "locale", "gettext", "unicodedata", "string",
            "textwrap", "difflib", "calendar", "heapq", "bisect",
            "queue", "sched", "select", "selectors", "signal", "mmap",
            "ctypes", "uuid", "secrets", "hmac", "ssl", "asyncio",
            "concurrent", "contextvars", "importlib", "pkgutil",
            "unittest", "doctest", "pdb", "profile", "timeit",
            "platform", "errno", "stat", "fileinput", "fnmatch",
            "operator", "keyword", "token", "tokenize", "pprint",
            "builtins", "types", "numbers", "cmath", "atexit",
        }


# =============================================================================
# INTELLIGENTER TESTER
# =============================================================================

class IntelligentTester:
    """Testet das Projekt basierend auf intelligenter Analyse"""

    def __init__(self, analysis: ProjectAnalysis, verbose: bool = False):
        self.analysis = analysis
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_all_tests(self):
        """Führt alle Tests durch"""
        self._test_module_health()
        self._test_imports()
        self._test_dependencies()
        self._test_config()
        self._test_services()
        self._show_issues()
        self._print_report()

    def _print_header(self, title: str):
        """Druckt einen Header"""
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")

    def _print_result(self, name: str, passed: bool, message: str = "", warn: bool = False):
        """Druckt ein Testergebnis"""
        if passed and not warn:
            icon = f"{Colors.GREEN}✓{Colors.RESET}"
            self.passed += 1
        elif warn:
            icon = f"{Colors.YELLOW}⚠{Colors.RESET}"
            self.warnings += 1
        else:
            icon = f"{Colors.RED}✗{Colors.RESET}"
            self.failed += 1

        print(f"  {icon} {name}")
        if message and (not passed or self.verbose):
            color = Colors.RED if not passed else Colors.YELLOW if warn else Colors.DIM
            print(f"      {color}→ {message}{Colors.RESET}")

    # =========================================================================
    # MODUL-GESUNDHEIT
    # =========================================================================

    def _test_module_health(self):
        """Testet die Gesundheit aller Module"""
        self._print_header(f"MODUL-ANALYSE ({len(self.analysis.modules)} Module)")

        # Gruppiere nach Kategorie
        by_category = defaultdict(list)
        for name, module in self.analysis.modules.items():
            by_category[module.category].append((name, module))

        for category in ModuleCategory:
            modules = by_category.get(category, [])
            if not modules:
                continue

            print(f"\n{Colors.BOLD}{category.name} ({len(modules)}):{Colors.RESET}")

            for name, module in sorted(modules, key=lambda x: x[1].size_bytes, reverse=True):
                # Bestimme Status
                if not module.syntax_ok:
                    self._print_result(name, False, "Syntax-Fehler")
                    continue

                # Versuche Import
                try:
                    if str(self.analysis.modules[name].path.parent) not in sys.path:
                        sys.path.insert(0, str(self.analysis.modules[name].path.parent))
                    importlib.import_module(name)
                    module.import_ok = True
                except Exception as e:
                    module.import_ok = False
                    self._print_result(name, False, f"Import-Fehler: {str(e)[:60]}")
                    continue

                # Erfolg mit Details
                details = []
                if module.classes:
                    details.append(f"{len(module.classes)} Klassen")
                if module.functions:
                    details.append(f"{len(module.functions)} Funktionen")
                details.append(f"{module.lines} Zeilen")

                has_warnings = len(module.missing_items) > 0 or len(module.issues) > 0

                if module.missing_items:
                    self._print_result(
                        name, True,
                        f"{', '.join(details)} - Fehlt: {', '.join(module.missing_items)}",
                        warn=True
                    )
                else:
                    self._print_result(name, True, ', '.join(details))

    # =========================================================================
    # IMPORT-TESTS
    # =========================================================================

    def _test_imports(self):
        """Testet alle externen Imports"""
        self._print_header("ABHÄNGIGKEITEN")

        # Sammle alle externen Imports
        external = set()
        for module in self.analysis.modules.values():
            for imp in module.imports.keys():
                if imp not in self.analysis.modules and imp not in IntelligentAnalyzer(self.analysis.modules[list(self.analysis.modules.keys())[0]].path.parent)._get_stdlib_modules():
                    external.add(imp)
            for imp in module.from_imports.keys():
                if imp not in self.analysis.modules and imp not in IntelligentAnalyzer(self.analysis.modules[list(self.analysis.modules.keys())[0]].path.parent)._get_stdlib_modules():
                    external.add(imp)

        if not external:
            print(f"{Colors.DIM}  Keine externen Abhängigkeiten{Colors.RESET}")
            return

        for imp in sorted(external):
            try:
                importlib.import_module(imp)
                self._print_result(imp, True, "Installiert")
            except ImportError:
                self._print_result(imp, False, f"Nicht installiert → pip install {imp}")

    # =========================================================================
    # DEPENDENCY TESTS
    # =========================================================================

    def _test_dependencies(self):
        """Testet Modul-Abhängigkeiten"""
        self._print_header("MODUL-ABHÄNGIGKEITEN")

        # Zirkuläre Abhängigkeiten
        if self.analysis.circular_deps:
            for cycle in self.analysis.circular_deps:
                self._print_result(
                    "Zirkuläre Abhängigkeit",
                    False,
                    " → ".join(cycle)
                )
        else:
            self._print_result("Keine zirkulären Abhängigkeiten", True)

        # Verwaiste Module
        if self.analysis.orphan_modules:
            orphans = self.analysis.orphan_modules[:5]
            more = len(self.analysis.orphan_modules) - 5
            msg = ", ".join(orphans)
            if more > 0:
                msg += f" (+{more} weitere)"
            self._print_result(
                f"{len(self.analysis.orphan_modules)} ungenutzte Module",
                True,
                msg,
                warn=True
            )
        else:
            self._print_result("Alle Module werden verwendet", True)

        # Abhängigkeits-Statistik
        avg_deps = sum(len(deps) for deps in self.analysis.dependency_graph.values()) / max(1, len(self.analysis.dependency_graph))
        max_deps = max((len(deps) for deps in self.analysis.dependency_graph.values()), default=0)
        max_dep_module = next((name for name, deps in self.analysis.dependency_graph.items() if len(deps) == max_deps), "?")

        print(f"\n{Colors.DIM}  Durchschnittliche Abhängigkeiten: {avg_deps:.1f}")
        print(f"  Maximale Abhängigkeiten: {max_deps} ({max_dep_module}){Colors.RESET}")

    # =========================================================================
    # CONFIG TESTS
    # =========================================================================

    def _test_config(self):
        """Testet Konfiguration"""
        self._print_header("KONFIGURATION")

        # Config-Datei
        config_exists = bool(self.analysis.config)
        self._print_result("config.json", config_exists,
                          "Geladen" if config_exists else "Nicht gefunden")

        # Verzeichnisse
        project_dir = Path.cwd()
        for dirname in ["data", "logs", "state"]:
            path = project_dir / dirname
            exists = path.exists() and path.is_dir()
            self._print_result(f"{dirname}/", exists,
                              "Existiert" if exists else "Fehlt - erstelle mit: mkdir " + dirname)

        # Umgebungsvariablen
        all_env_vars = set()
        for module in self.analysis.modules.values():
            all_env_vars.update(module.env_vars_used)

        if all_env_vars:
            set_vars = [v for v in all_env_vars if os.getenv(v)]
            unset = [v for v in all_env_vars if not os.getenv(v)]

            if unset and len(unset) <= 5:
                self._print_result(
                    f"Umgebungsvariablen ({len(set_vars)}/{len(all_env_vars)} gesetzt)",
                    True,
                    f"Nicht gesetzt: {', '.join(unset[:5])}",
                    warn=True
                )
            else:
                self._print_result(
                    f"Umgebungsvariablen ({len(set_vars)}/{len(all_env_vars)} gesetzt)",
                    True
                )

    # =========================================================================
    # SERVICE TESTS
    # =========================================================================

    def _test_services(self):
        """Testet externe Services aus Config"""
        if not self.analysis.config.get("network"):
            return

        self._print_header("SERVICES")

        network = self.analysis.config["network"]

        # Ollama
        if "ollama" in network:
            host = network["ollama"].get("host", "localhost")
            port = network["ollama"].get("port", 11434)
            reachable, info = self._test_service(host, port, "http")
            self._print_result(f"Ollama ({host}:{port})", reachable, info)

        # MQTT
        if "mqtt" in network:
            host = network["mqtt"].get("broker_ip", "localhost")
            port = network["mqtt"].get("port", 1883)
            reachable, info = self._test_service(host, port, "tcp")
            self._print_result(f"MQTT ({host}:{port})", reachable, info)

        # Home Assistant
        if "home_assistant" in network:
            url = network["home_assistant"].get("api_url", "")
            if url:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                host = parsed.hostname or "localhost"
                port = parsed.port or 8123
                reachable, info = self._test_service(host, port, "http")
                self._print_result(f"Home Assistant ({host}:{port})", reachable, info)

        # NAS
        if "nas" in network and network["nas"].get("ip"):
            host = network["nas"]["ip"]
            reachable, info = self._test_service(host, 22, "tcp")
            self._print_result(f"NAS SSH ({host}:22)", reachable, info)

    def _test_service(self, host: str, port: int, protocol: str) -> Tuple[bool, str]:
        """Testet einen Service"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                if protocol == "http" and port == 11434:
                    # Ollama spezifisch
                    try:
                        import urllib.request
                        url = f"http://{host}:{port}/api/tags"
                        with urllib.request.urlopen(url, timeout=3) as resp:
                            data = json.loads(resp.read())
                            models = [m.get("name") for m in data.get("models", [])]
                            return True, f"{len(models)} Modelle verfügbar"
                    except:
                        return True, "Erreichbar"
                return True, "Erreichbar"
            return False, "Nicht erreichbar"
        except socket.timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)[:30]

    # =========================================================================
    # ISSUES
    # =========================================================================

    def _show_issues(self):
        """Zeigt alle gefundenen Probleme"""
        errors = [i for i in self.analysis.all_issues if i.severity == "error"]
        warnings = [i for i in self.analysis.all_issues if i.severity == "warning"]

        if not errors and not warnings:
            return

        self._print_header("GEFUNDENE PROBLEME")

        if errors:
            print(f"\n{Colors.RED}{Colors.BOLD}Fehler ({len(errors)}):{Colors.RESET}")
            for issue in errors[:10]:
                print(f"  {Colors.RED}✗ [{issue.module}] {issue.message}{Colors.RESET}")
                if issue.suggestion:
                    print(f"      {Colors.DIM}→ {issue.suggestion}{Colors.RESET}")

        if warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnungen ({len(warnings)}):{Colors.RESET}")
            for issue in warnings[:10]:
                print(f"  {Colors.YELLOW}⚠ [{issue.module}] {issue.message}{Colors.RESET}")
                if issue.suggestion:
                    print(f"      {Colors.DIM}→ {issue.suggestion}{Colors.RESET}")

    # =========================================================================
    # REPORT
    # =========================================================================

    def _print_report(self):
        """Druckt den finalen Report"""
        print()
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  ZUSAMMENFASSUNG{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")

        total = self.passed + self.failed + self.warnings

        print()
        if self.failed == 0:
            print(f"  {Colors.GREEN}{Colors.BOLD}✓ ALLE TESTS BESTANDEN{Colors.RESET}")
        elif self.failed < self.passed:
            print(f"  {Colors.YELLOW}{Colors.BOLD}⚠ EINIGE PROBLEME GEFUNDEN{Colors.RESET}")
        else:
            print(f"  {Colors.RED}{Colors.BOLD}✗ KRITISCHE PROBLEME{Colors.RESET}")

        print()
        print(f"  {Colors.GREEN}✓ {self.passed} bestanden{Colors.RESET}")
        print(f"  {Colors.YELLOW}⚠ {self.warnings} Warnungen{Colors.RESET}")
        print(f"  {Colors.RED}✗ {self.failed} fehlgeschlagen{Colors.RESET}")

        print()
        print(f"{Colors.BOLD}Projekt-Statistik:{Colors.RESET}")
        print(f"  Module:         {len(self.analysis.modules)}")
        print(f"  Code-Zeilen:    {self.analysis.total_lines:,}")
        print(f"  Klassen:        {self.analysis.total_classes}")
        print(f"  Funktionen:     {self.analysis.total_functions}")
        print(f"  Abhängigkeiten: {sum(len(d) for d in self.analysis.dependency_graph.values())}")
        print()


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Holocloude Intelligent System Tester - Versteht und testet das Projekt"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Mehr Details")
    parser.add_argument("--no-color", action="store_true", help="Keine Farben")
    parser.add_argument("--explain", action="store_true", help="Erklärt was jedes Modul tut")
    parser.add_argument("--problems", action="store_true", help="Nur Probleme anzeigen")
    parser.add_argument("--graph", action="store_true", help="Zeigt Dependency-Graph")

    args = parser.parse_args()

    if args.no_color:
        Colors.disable()

    print()
    print(f"{Colors.BOLD}{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║      HOLOCLOUDE INTELLIGENT SYSTEM TESTER v3.0               ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║      {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^50} ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")

    # Analyse
    analyzer = IntelligentAnalyzer()
    analysis = analyzer.analyze()

    print(f"{Colors.DIM}  Gefunden: {len(analysis.modules)} Module, "
          f"{analysis.total_classes} Klassen, "
          f"{analysis.total_functions} Funktionen{Colors.RESET}")

    # Explain-Modus
    if args.explain:
        print()
        print(f"{Colors.BOLD}MODUL-ERKLÄRUNGEN:{Colors.RESET}")
        for name, module in sorted(analysis.modules.items()):
            cat_name = module.category.name
            print(f"\n  {Colors.CYAN}{name}{Colors.RESET} [{cat_name}]")
            print(f"      {module.purpose}")
            if module.classes:
                print(f"      Klassen: {', '.join(module.classes[:5])}")
        sys.exit(0)

    # Graph-Modus
    if args.graph:
        print()
        print(f"{Colors.BOLD}DEPENDENCY GRAPH:{Colors.RESET}")
        for name, deps in sorted(analysis.dependency_graph.items()):
            if deps:
                print(f"  {name} → {', '.join(sorted(deps))}")
        sys.exit(0)

    # Problems-Modus
    if args.problems:
        errors = [i for i in analysis.all_issues if i.severity == "error"]
        warnings = [i for i in analysis.all_issues if i.severity == "warning"]

        if errors:
            print(f"\n{Colors.RED}FEHLER ({len(errors)}):{Colors.RESET}")
            for i in errors:
                print(f"  [{i.module}] {i.message}")

        if warnings:
            print(f"\n{Colors.YELLOW}WARNUNGEN ({len(warnings)}):{Colors.RESET}")
            for i in warnings:
                print(f"  [{i.module}] {i.message}")

        if not errors and not warnings:
            print(f"\n{Colors.GREEN}Keine Probleme gefunden!{Colors.RESET}")

        sys.exit(1 if errors else 0)

    # Standard: Alle Tests
    tester = IntelligentTester(analysis, verbose=args.verbose)
    tester.run_all_tests()

    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == "__main__":
    main()
