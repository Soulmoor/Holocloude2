#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║             HOLOCLOUDE INTELLIGENT SYSTEM TESTER v6.0                        ║
║                                                                              ║
║  VOLLSTÄNDIGE PROJEKT-ANALYSE mit 7 neuen Prüfungen:                         ║
║                                                                              ║
║  NEU in v6.0:                                                                ║
║    • FUNKTIONS-TEST    - Prüft ob Funktionen aufrufbar sind                  ║
║    • DOCSTRING-CHECK   - Analysiert Dokumentations-Abdeckung                 ║
║    • TYPE-ANNOTATION   - Prüft Type-Hints in Signaturen                      ║
║    • KOMPLEXITÄT       - McCabe Complexity & Wartbarkeits-Index              ║
║    • SICHERHEIT        - Findet bekannte Sicherheitslücken (OWASP)           ║
║    • CONFIG-CHECK      - Prüft ob alle Config-Keys existieren                ║
║    • DB-SCHEMA         - Verifiziert SQLite-Tabellen und -Struktur           ║
║                                                                              ║
║  Bereits vorhanden (v5.0):                                                   ║
║    • Tiefe Import-Analyse, Import-Ketten, Item-Verfügbarkeit                 ║
║    • Dependency-Graph, Zirkuläre Abhängigkeiten                              ║
║    • Redundanz-Erkennung, Toter Code, Syntax-Prüfung                         ║
║                                                                              ║
║  Verwendung:                                                                 ║
║      python holo_tester.py                     # Vollständige Analyse        ║
║      python holo_tester.py --quick             # Schneller Start-Check       ║
║      python holo_tester.py --functions         # Funktions-Test              ║
║      python holo_tester.py --docstrings        # Docstring-Abdeckung         ║
║      python holo_tester.py --types             # Type-Annotation Check       ║
║      python holo_tester.py --complexity        # Komplexitäts-Analyse        ║
║      python holo_tester.py --security          # Sicherheits-Audit           ║
║      python holo_tester.py --config            # Config-Vollständigkeit      ║
║      python holo_tester.py --db                # Datenbank-Schema Check      ║
║      python holo_tester.py --imports           # Import-Analyse              ║
║      python holo_tester.py --trace MODULE      # Verfolge Modul-Imports      ║
║      python holo_tester.py --all               # Alle erweiterten Prüfungen  ║
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
import subprocess
import traceback
import py_compile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any, NamedTuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum, auto
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

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
class ImportedItem:
    """Ein importiertes Element (Funktion, Klasse, Variable)"""
    name: str
    source_module: str
    import_type: str  # "import", "from_import", "star_import"
    exists: bool = False
    is_callable: bool = False
    actual_type: str = ""  # "function", "class", "module", "variable"


@dataclass
class FunctionInfo:
    """Detaillierte Informationen über eine Funktion"""
    name: str
    lineno: int
    is_async: bool = False
    has_docstring: bool = False
    has_return_type: bool = False
    has_all_param_types: bool = False
    param_count: int = 0
    typed_params: int = 0
    complexity: int = 1  # McCabe Complexity
    lines: int = 0
    is_callable: bool = True
    call_error: str = ""


@dataclass
class SecurityIssue:
    """Sicherheitsproblem"""
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "injection", "crypto", "secrets", etc.
    module: str
    line: int
    code: str
    message: str
    recommendation: str


@dataclass
class ComplexityInfo:
    """Komplexitäts-Metriken für ein Modul"""
    total_complexity: int = 0
    max_complexity: int = 0
    max_complex_function: str = ""
    avg_complexity: float = 0.0
    maintainability_index: float = 100.0
    functions_above_10: int = 0  # Komplexität > 10 = zu komplex
    lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0


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
    compile_ok: bool = True
    import_ok: bool = False
    import_error: str = ""
    issues: List[Issue] = field(default_factory=list)

    # Erwartungen
    expected_items: List[str] = field(default_factory=list)
    missing_items: List[str] = field(default_factory=list)

    # Funktions-Signaturen für Redundanz-Check
    function_signatures: Dict[str, str] = field(default_factory=dict)  # name -> signature hash
    class_methods: Dict[str, List[str]] = field(default_factory=dict)  # class -> [methods]

    # Ungenutzte Funktionen
    internal_calls: Set[str] = field(default_factory=set)  # Funktionen die intern aufgerufen werden
    potentially_unused: List[str] = field(default_factory=list)  # Evtl. ungenutzte Funktionen

    # NEU: Import-Ketten Tracking
    imported_items: List[ImportedItem] = field(default_factory=list)  # Was wird importiert
    import_chain: List[str] = field(default_factory=list)  # Reihenfolge der Imports
    failed_imports: List[Tuple[str, str]] = field(default_factory=list)  # (modul, fehler)
    missing_imported_items: List[str] = field(default_factory=list)  # Items die nicht existieren

    # NEU v6.0: Erweiterte Analyse
    function_details: List[FunctionInfo] = field(default_factory=list)  # Detaillierte Funktions-Infos
    security_issues: List[SecurityIssue] = field(default_factory=list)  # Sicherheitsprobleme
    complexity_info: ComplexityInfo = field(default_factory=ComplexityInfo)  # Komplexitäts-Metriken
    docstring_coverage: float = 0.0  # Prozent mit Docstrings
    type_coverage: float = 0.0  # Prozent mit Type-Hints
    missing_docstrings: List[str] = field(default_factory=list)  # Funktionen ohne Docstring
    missing_types: List[str] = field(default_factory=list)  # Funktionen ohne Type-Hints


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

    # Redundanz-Info
    duplicate_functions: List[Tuple[str, str, str]] = field(default_factory=list)  # (name, modul1, modul2)
    similar_functions: List[Tuple[str, str, str, float]] = field(default_factory=list)  # (name1, name2, modul, similarity)
    global_function_names: Dict[str, List[str]] = field(default_factory=dict)  # func_name -> [modules]

    # Import-Test Ergebnisse
    import_failures: List[Tuple[str, str]] = field(default_factory=list)  # (modul, error)
    import_successes: List[str] = field(default_factory=list)

    # NEU: Import-Ketten Analyse
    import_tree: Dict[str, List[str]] = field(default_factory=dict)  # modul -> [importiert von]
    broken_import_chains: List[Tuple[str, str, str]] = field(default_factory=list)  # (modul, import, fehler)
    missing_items_report: List[Tuple[str, str, str]] = field(default_factory=list)  # (modul, item, source)

    # NEU v6.0: Erweiterte Projekt-Analyse
    all_security_issues: List[SecurityIssue] = field(default_factory=list)
    avg_docstring_coverage: float = 0.0
    avg_type_coverage: float = 0.0
    total_complexity: int = 0
    avg_complexity: float = 0.0
    complex_functions: List[Tuple[str, str, int]] = field(default_factory=list)  # (modul, funktion, complexity)
    config_issues: List[str] = field(default_factory=list)  # Fehlende/ungültige Config-Keys
    db_tables: List[str] = field(default_factory=list)  # Gefundene DB-Tabellen
    db_issues: List[str] = field(default_factory=list)  # DB-Schema Probleme


# =============================================================================
# SICHERHEITS-PATTERNS für Security Audit
# =============================================================================

SECURITY_PATTERNS = {
    # SQL Injection - nur gefährlich wenn User-Input involviert
    ("critical", "injection", r'execute\s*\(\s*["\'].*%s.*["\']',
     "SQL Injection via %s String-Formatierung", "Verwende parameterisierte Queries mit ?"),
    ("critical", "injection", r'execute\s*\(\s*["\'].*\.format\s*\(',
     "SQL Injection via .format()", "Verwende parameterisierte Queries mit ?"),
    ("high", "injection", r'execute\s*\(\s*f["\'].*\{[^}]*input',
     "SQL Injection - f-string mit input", "Verwende ? Platzhalter statt f-strings für User-Input"),
    ("high", "injection", r'execute\s*\(\s*f["\'].*\{[^}]*request',
     "SQL Injection - f-string mit request", "Verwende ? Platzhalter statt f-strings für User-Input"),
    ("high", "injection", r'execute\s*\(\s*f["\'].*\{[^}]*user',
     "SQL Injection - f-string mit user-Daten", "Verwende ? Platzhalter statt f-strings für User-Input"),
    # executescript nur warnen wenn Variable übergeben wird
    ("medium", "injection", r'executescript\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)',
     "executescript mit Variable - prüfe ob vertrauenswürdig", "Stelle sicher dass SQL nicht von externen Quellen kommt"),

    # Command Injection
    ("critical", "injection", r'os\.system\s*\(\s*[^)]*[\+%]',
     "Command Injection Gefahr", "Verwende subprocess mit shell=False"),
    ("critical", "injection", r'subprocess\..*shell\s*=\s*True',
     "Shell Injection möglich", "Setze shell=False und übergebe Args als Liste"),
    ("high", "injection", r'eval\s*\(\s*[^)]*(?:input|request|user)',
     "eval() mit User-Input ist gefährlich", "Verwende ast.literal_eval() oder validiere Input"),
    ("critical", "injection", r'exec\s*\(\s*[^)]*(?:input|request|user)',
     "exec() mit User-Input ist gefährlich", "Vermeide exec() mit externem Input"),

    # Pickle/Deserialization
    ("high", "deserialization", r'pickle\.loads?\s*\(',
     "Pickle ist unsicher für nicht vertrauenswürdige Daten", "Verwende json für externe Daten"),
    ("high", "deserialization", r'yaml\.load\s*\([^)]*\)(?!\s*#\s*safe)',
     "yaml.load ist unsicher", "Verwende yaml.safe_load()"),

    # Hardcoded Secrets - genauer Pattern
    ("high", "secrets", r'(?:password|passwd|api_key|apikey|secret_key)\s*=\s*["\'][A-Za-z0-9+/=]{16,}["\']',
     "Hardcoded Secret/Password gefunden", "Verwende Umgebungsvariablen oder Secrets Manager"),
    ("critical", "secrets", r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----',
     "Private Key im Code", "Speichere Keys extern, nicht im Code"),

    # Crypto Issues - nur für kryptografische Zwecke relevant
    ("low", "crypto", r'hashlib\.md5\s*\(',
     "MD5 - nicht für kryptografische Zwecke nutzen", "Für Hashing/Checksums OK, für Security SHA-256 nutzen"),
    ("low", "crypto", r'hashlib\.sha1\s*\(',
     "SHA1 - veraltet für kryptografische Zwecke", "Für Checksums OK, für Security SHA-256 nutzen"),
    ("high", "crypto", r'random\.\w+\s*\([^)]*(?:password|token|secret|auth)',
     "random für Security-relevante Werte unsicher", "Verwende secrets Modul für Passwörter/Tokens"),

    # Path Traversal
    ("high", "path_traversal", r'open\s*\(\s*[^)]*(?:input|request|user)',
     "Path Traversal möglich", "Validiere Pfade und verwende os.path.realpath()"),

    # SSRF
    ("medium", "ssrf", r'requests\.(?:get|post)\s*\(\s*[^)]*(?:input|request|user)',
     "Potenzielle SSRF", "Validiere URLs gegen Whitelist"),

    # Debug/Logging - präziseres Pattern
    ("low", "debug", r'print\s*\(.*(?:password|secret_key|api_key|auth_token)',
     "Sensitiver Output in print()", "Entferne Debug-Ausgaben mit sensiblen Daten"),
    ("medium", "debug", r'logging\..*\(.*(?:password|secret_key|api_key|auth_token)',
     "Sensitiver Output im Log", "Maskiere sensitive Daten vor dem Logging"),
}


# =============================================================================
# INTELLIGENTER PROJEKT-ANALYZER
# =============================================================================

class IntelligentAnalyzer:
    """Analysiert das Projekt intelligent und versteht Zusammenhänge"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.analysis = ProjectAnalysis()
        self.stdlib_modules = self._get_stdlib_modules()

    def analyze(self, quick_mode: bool = False) -> ProjectAnalysis:
        """Führt komplette intelligente Analyse durch"""
        print(f"\n{Colors.DIM}Analysiere Projekt intelligent...{Colors.RESET}")

        self._load_config()
        self._discover_modules()

        if quick_mode:
            # Schneller Modus: Nur Syntax und Import prüfen
            self._quick_syntax_check()
            self._real_import_test()
            return self.analysis

        self._analyze_all_modules()
        self._build_dependency_graph()
        self._find_circular_dependencies()
        self._find_orphan_modules()
        self._check_module_expectations()
        self._validate_imports()
        self._check_config_usage()
        self._find_redundancy()
        self._find_unused_code()
        self._real_import_test()

        # NEU: Tiefe Import-Analyse nach dem Import-Test
        self._deep_import_analysis()
        self._verify_import_chains()
        self._build_import_order()

        # NEU v6.0: Erweiterte Analysen
        self._analyze_functions_deep()
        self._analyze_docstrings()
        self._analyze_type_annotations()
        self._analyze_complexity()
        self._security_audit()
        self._check_config_completeness()
        self._check_database_schema()

        self._calculate_statistics()

        return self.analysis

    # =========================================================================
    # SCHNELLE SYNTAX-PRÜFUNG
    # =========================================================================

    def _quick_syntax_check(self):
        """Schnelle Syntax-Prüfung aller Module via py_compile"""
        for name, module in self.analysis.modules.items():
            try:
                # Versuche zu kompilieren
                py_compile.compile(str(module.path), doraise=True)
                module.syntax_ok = True
                module.compile_ok = True
            except py_compile.PyCompileError as e:
                module.syntax_ok = False
                module.compile_ok = False
                module.issues.append(Issue(
                    severity="error",
                    category="syntax",
                    module=name,
                    message=f"Kompilierungsfehler: {str(e)[:100]}",
                    line=getattr(e, 'lineno', 0) or 0
                ))

    # =========================================================================
    # ECHTER IMPORT-TEST
    # =========================================================================

    def _real_import_test(self):
        """Testet ob jedes Modul wirklich importiert werden kann"""
        # Projekt-Verzeichnis zu sys.path hinzufügen
        project_str = str(self.project_dir)
        if project_str not in sys.path:
            sys.path.insert(0, project_str)

        for name, module in self.analysis.modules.items():
            if not module.syntax_ok:
                module.import_ok = False
                module.import_error = "Syntax-Fehler"
                self.analysis.import_failures.append((name, "Syntax-Fehler"))
                continue

            try:
                # Stille Import-Versuche
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = StringIO()
                sys.stderr = StringIO()

                try:
                    # Entferne vorher importierte Version
                    if name in sys.modules:
                        del sys.modules[name]

                    # Versuche Import
                    spec = importlib.util.spec_from_file_location(name, module.path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules[name] = mod
                        spec.loader.exec_module(mod)
                        module.import_ok = True
                        self.analysis.import_successes.append(name)
                    else:
                        raise ImportError(f"Konnte {name} nicht laden")

                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            except Exception as e:
                module.import_ok = False
                error_msg = str(e)[:200]
                # Traceback für bessere Fehlerdiagnose
                tb = traceback.format_exc()
                # Finde die relevante Zeile
                for line in tb.split('\n'):
                    if name in line and 'line' in line.lower():
                        error_msg = f"{error_msg} | {line.strip()}"
                        break
                module.import_error = error_msg
                self.analysis.import_failures.append((name, error_msg))
                module.issues.append(Issue(
                    severity="error",
                    category="import",
                    module=name,
                    message=f"Import fehlgeschlagen: {error_msg}",
                    suggestion="Prüfe fehlende Abhängigkeiten oder Syntax-Fehler"
                ))

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
        """Findet zirkuläre Abhängigkeiten - KORRIGIERTE VERSION"""
        found_cycles = set()  # Verhindere Duplikate

        def find_cycle(start: str) -> Optional[List[str]]:
            """Findet einen Zyklus ausgehend von start"""
            visited = set()
            path = []

            def dfs(node: str) -> Optional[List[str]]:
                if node in path:
                    # Zyklus gefunden!
                    cycle_start = path.index(node)
                    return path[cycle_start:] + [node]

                if node in visited:
                    return None

                visited.add(node)
                path.append(node)

                for neighbor in self.analysis.dependency_graph.get(node, set()):
                    result = dfs(neighbor)
                    if result:
                        return result

                path.pop()
                return None

            return dfs(start)

        for module in self.analysis.modules:
            cycle = find_cycle(module)
            if cycle:
                # Normalisiere Zyklus für Duplikat-Check
                cycle_key = tuple(sorted(cycle[:-1]))  # Ohne das doppelte Ende-Element
                if cycle_key not in found_cycles:
                    found_cycles.add(cycle_key)
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
    # REDUNDANZ-ERKENNUNG
    # =========================================================================

    def _find_redundancy(self):
        """Findet redundante/doppelte Funktionen und Klassen"""
        # Sammle alle Funktionsnamen mit ihren Modulen
        func_to_modules: Dict[str, List[str]] = defaultdict(list)
        class_to_modules: Dict[str, List[str]] = defaultdict(list)

        for name, module in self.analysis.modules.items():
            for func in module.functions:
                # Ignoriere private Funktionen und common patterns
                if not func.startswith('_') and func not in {'main', 'setup', 'run', 'start', 'stop', 'init'}:
                    func_to_modules[func].append(name)

            for cls in module.classes:
                if not cls.startswith('_'):
                    class_to_modules[cls].append(name)

        # Finde doppelte Funktionsnamen
        for func, modules in func_to_modules.items():
            if len(modules) > 1:
                self.analysis.global_function_names[func] = modules
                # Nur warnen wenn es wirklich identisch aussieht
                if len(modules) <= 3:
                    self.analysis.duplicate_functions.append((func, modules[0], modules[1]))
                    self.analysis.all_issues.append(Issue(
                        severity="info",
                        category="redundancy",
                        module=modules[0],
                        message=f"Funktion '{func}' existiert auch in: {', '.join(modules[1:])}",
                        suggestion="Prüfe ob Konsolidierung sinnvoll ist"
                    ))

        # Finde doppelte Klassennamen
        for cls, modules in class_to_modules.items():
            if len(modules) > 1 and cls not in {'Config', 'Logger', 'Handler', 'Error', 'Exception'}:
                self.analysis.all_issues.append(Issue(
                    severity="info",
                    category="redundancy",
                    module=modules[0],
                    message=f"Klasse '{cls}' existiert auch in: {', '.join(modules[1:])}",
                    suggestion="Prüfe ob gemeinsame Basisklasse sinnvoll ist"
                ))

    def _find_unused_code(self):
        """Findet potenziell ungenutzten Code"""
        # Sammle alle Funktions-Aufrufe im Projekt
        all_calls: Set[str] = set()

        for name, module in self.analysis.modules.items():
            try:
                source = module.path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    # Finde Funktionsaufrufe
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            all_calls.add(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            all_calls.add(node.func.attr)

                    # Finde Attribut-Zugriffe (für Methoden)
                    if isinstance(node, ast.Attribute):
                        all_calls.add(node.attr)

                module.internal_calls = all_calls.copy()

            except Exception:
                pass

        # Prüfe welche Funktionen nie aufgerufen werden
        for name, module in self.analysis.modules.items():
            for func in module.functions:
                # Ignoriere typische Entry-Points und Magic Methods
                if func in {'main', '__init__', '__call__', '__enter__', '__exit__',
                           'setup', 'run', 'start', 'stop', 'handle', 'process'}:
                    continue
                if func.startswith('_'):
                    continue

                # Prüfe ob diese Funktion irgendwo aufgerufen wird
                if func not in all_calls:
                    # Zusätzlicher Check: Wird sie als Callback referenziert?
                    found_as_ref = False
                    for other_module in self.analysis.modules.values():
                        try:
                            source = other_module.path.read_text(encoding="utf-8", errors="ignore")
                            # Suche nach Referenzen wie "callback=func" oder "handler=func"
                            if re.search(rf'\b{func}\b', source):
                                found_as_ref = True
                                break
                        except:
                            pass

                    if not found_as_ref:
                        module.potentially_unused.append(func)

            # Nur warnen wenn mehrere ungenutzte Funktionen
            if len(module.potentially_unused) >= 3:
                self.analysis.all_issues.append(Issue(
                    severity="info",
                    category="unused",
                    module=name,
                    message=f"{len(module.potentially_unused)} potenziell ungenutzte Funktionen: {', '.join(module.potentially_unused[:5])}",
                    suggestion="Prüfe ob diese Funktionen noch benötigt werden"
                ))

    # =========================================================================
    # TIEFE IMPORT-ANALYSE
    # =========================================================================

    def _deep_import_analysis(self):
        """Führt tiefe Import-Analyse durch: Verfolgt Ketten, prüft Verfügbarkeit"""
        project_modules = set(self.analysis.modules.keys())
        project_str = str(self.project_dir)

        if project_str not in sys.path:
            sys.path.insert(0, project_str)

        for name, module in self.analysis.modules.items():
            if not module.syntax_ok:
                continue

            self._analyze_module_imports(name, module, project_modules)

    def _analyze_module_imports(self, name: str, module: ModuleAnalysis, project_modules: Set[str]):
        """Analysiert alle Imports eines Moduls im Detail"""
        try:
            source = module.path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except Exception:
            return

        # Analysiere jeden Import-Statement
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_import(name, module, alias.name, None, "import")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        import_name = alias.name
                        if import_name == "*":
                            self._check_star_import(name, module, node.module)
                        else:
                            self._check_import(name, module, node.module, import_name, "from_import")

    def _check_import(self, module_name: str, module: ModuleAnalysis,
                      source_module: str, item_name: Optional[str], import_type: str):
        """Prüft einen einzelnen Import auf Verfügbarkeit"""
        project_modules = set(self.analysis.modules.keys())
        base_module = source_module.split(".")[0]

        # Erstelle ImportedItem
        imported_item = ImportedItem(
            name=item_name or source_module,
            source_module=source_module,
            import_type=import_type
        )

        # Versuche zu importieren und zu prüfen
        try:
            # Stille Imports
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = StringIO(), StringIO()

            try:
                if base_module in project_modules:
                    # Projekt-internes Modul
                    project_module = self.analysis.modules.get(base_module)
                    if project_module and project_module.import_ok:
                        imported_item.exists = True

                        # Prüfe ob spezifisches Item existiert
                        if item_name:
                            loaded_mod = sys.modules.get(base_module)
                            if loaded_mod and hasattr(loaded_mod, item_name):
                                imported_item.exists = True
                                attr = getattr(loaded_mod, item_name)
                                imported_item.is_callable = callable(attr)
                                if isinstance(attr, type):
                                    imported_item.actual_type = "class"
                                elif callable(attr):
                                    imported_item.actual_type = "function"
                                else:
                                    imported_item.actual_type = "variable"
                            else:
                                imported_item.exists = False
                                module.missing_imported_items.append(f"{source_module}.{item_name}")
                                self.analysis.missing_items_report.append(
                                    (module_name, item_name, source_module)
                                )
                    else:
                        # Source-Modul lädt nicht
                        module.failed_imports.append((source_module, "Modul lädt nicht"))
                        self.analysis.broken_import_chains.append(
                            (module_name, source_module, "Basis-Modul fehlerhaft")
                        )
                else:
                    # Externes Modul
                    try:
                        ext_mod = importlib.import_module(source_module)
                        imported_item.exists = True

                        if item_name:
                            if hasattr(ext_mod, item_name):
                                imported_item.exists = True
                                attr = getattr(ext_mod, item_name)
                                imported_item.is_callable = callable(attr)
                            else:
                                imported_item.exists = False
                                module.missing_imported_items.append(f"{source_module}.{item_name}")

                    except ImportError as e:
                        imported_item.exists = False
                        # Nur warnen bei Nicht-Standard-Modulen
                        if base_module not in self.stdlib_modules:
                            module.failed_imports.append((source_module, str(e)[:50]))

            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

        except Exception as e:
            imported_item.exists = False

        module.imported_items.append(imported_item)

        # Baue Import-Baum
        if source_module not in self.analysis.import_tree:
            self.analysis.import_tree[source_module] = []
        if module_name not in self.analysis.import_tree[source_module]:
            self.analysis.import_tree[source_module].append(module_name)

    def _check_star_import(self, module_name: str, module: ModuleAnalysis, source_module: str):
        """Prüft einen Star-Import (from X import *)"""
        imported_item = ImportedItem(
            name="*",
            source_module=source_module,
            import_type="star_import"
        )

        project_modules = set(self.analysis.modules.keys())
        base_module = source_module.split(".")[0]

        if base_module in project_modules:
            project_module = self.analysis.modules.get(base_module)
            if project_module:
                imported_item.exists = project_module.import_ok
                if not project_module.import_ok:
                    module.failed_imports.append((f"{source_module}.*", "Basis-Modul fehlerhaft"))
        else:
            try:
                importlib.import_module(source_module)
                imported_item.exists = True
            except ImportError:
                imported_item.exists = False

        module.imported_items.append(imported_item)

    def _verify_import_chains(self):
        """Verifiziert dass Import-Ketten vollständig funktionieren"""
        project_modules = set(self.analysis.modules.keys())

        for name, module in self.analysis.modules.items():
            if not module.import_ok:
                continue

            # Prüfe alle Projekt-internen Imports
            for imp_module in module.uses_modules:
                if imp_module in project_modules:
                    dep_module = self.analysis.modules.get(imp_module)
                    if dep_module and not dep_module.import_ok:
                        # Abhängigkeit ist kaputt
                        self.analysis.broken_import_chains.append(
                            (name, imp_module, dep_module.import_error or "Import fehlerhaft")
                        )
                        module.issues.append(Issue(
                            severity="warning",
                            category="import_chain",
                            module=name,
                            message=f"Import-Kette unterbrochen: {name} -> {imp_module}",
                            suggestion=f"Prüfe {imp_module}: {dep_module.import_error[:50] if dep_module.import_error else 'unbekannter Fehler'}"
                        ))

    def _build_import_order(self):
        """Bestimmt die korrekte Import-Reihenfolge (topologische Sortierung)"""
        # Kahn's Algorithmus für topologische Sortierung
        in_degree = {name: 0 for name in self.analysis.modules}
        project_modules = set(self.analysis.modules.keys())

        for name, module in self.analysis.modules.items():
            for dep in module.uses_modules:
                if dep in project_modules:
                    in_degree[name] += 1

        # Starte mit Modulen ohne Abhängigkeiten
        queue = [name for name, degree in in_degree.items() if degree == 0]
        order = []

        while queue:
            current = queue.pop(0)
            order.append(current)

            # Reduziere in_degree für abhängige Module
            for name, module in self.analysis.modules.items():
                if current in module.uses_modules and current in project_modules:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)

        # Speichere Import-Reihenfolge
        for i, name in enumerate(order):
            if name in self.analysis.modules:
                self.analysis.modules[name].import_chain = order[:i]

    # =========================================================================
    # NEU v6.0: FUNKTIONS-TEST
    # =========================================================================

    def _analyze_functions_deep(self):
        """Analysiert alle Funktionen im Detail (Signaturen, Aufrufbarkeit)"""
        for name, module in self.analysis.modules.items():
            if not module.syntax_ok:
                continue

            try:
                source = module.path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)
                lines = source.splitlines()

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_info = self._analyze_single_function(node, lines)
                        module.function_details.append(func_info)

                        # Prüfe Komplexität
                        if func_info.complexity > 10:
                            self.analysis.complex_functions.append(
                                (name, func_info.name, func_info.complexity)
                            )

            except Exception:
                pass

        # Prüfe ob Funktionen aufrufbar sind (für erfolgreich importierte Module)
        self._test_function_callability()

    def _analyze_single_function(self, node: ast.FunctionDef, lines: List[str]) -> FunctionInfo:
        """Analysiert eine einzelne Funktion"""
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Docstring
        has_docstring = ast.get_docstring(node) is not None

        # Return Type
        has_return_type = node.returns is not None

        # Parameter Types
        params = node.args.args + node.args.posonlyargs + node.args.kwonlyargs
        param_count = len(params)
        typed_params = sum(1 for p in params if p.annotation is not None)
        has_all_param_types = param_count == typed_params if param_count > 0 else True

        # Zeilen zählen
        if hasattr(node, 'end_lineno'):
            func_lines = node.end_lineno - node.lineno + 1
        else:
            func_lines = 1

        # McCabe Complexity berechnen
        complexity = self._calculate_mccabe_complexity(node)

        return FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            is_async=is_async,
            has_docstring=has_docstring,
            has_return_type=has_return_type,
            has_all_param_types=has_all_param_types,
            param_count=param_count,
            typed_params=typed_params,
            complexity=complexity,
            lines=func_lines
        )

    def _calculate_mccabe_complexity(self, node: ast.AST) -> int:
        """Berechnet McCabe Cyclomatic Complexity"""
        complexity = 1  # Basis

        for child in ast.walk(node):
            # Verzweigungen erhöhen Komplexität
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
            # Boolesche Operatoren
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Ternärer Operator
            elif isinstance(child, ast.IfExp):
                complexity += 1

        return complexity

    def _test_function_callability(self):
        """Testet ob Funktionen wirklich aufrufbar sind"""
        project_str = str(self.project_dir)
        if project_str not in sys.path:
            sys.path.insert(0, project_str)

        for name, module in self.analysis.modules.items():
            if not module.import_ok:
                continue

            loaded_mod = sys.modules.get(name)
            if not loaded_mod:
                continue

            for func_info in module.function_details:
                try:
                    func = getattr(loaded_mod, func_info.name, None)
                    if func is None:
                        # Vielleicht eine Methode in einer Klasse
                        func_info.is_callable = True  # Kann nicht direkt getestet werden
                    elif callable(func):
                        func_info.is_callable = True
                    else:
                        func_info.is_callable = False
                        func_info.call_error = "Nicht aufrufbar"
                except Exception as e:
                    func_info.is_callable = False
                    func_info.call_error = str(e)[:50]

    # =========================================================================
    # NEU v6.0: DOCSTRING-CHECK
    # =========================================================================

    def _analyze_docstrings(self):
        """Analysiert Docstring-Abdeckung"""
        for name, module in self.analysis.modules.items():
            if not module.function_details:
                continue

            with_docstring = sum(1 for f in module.function_details if f.has_docstring)
            total = len(module.function_details)

            if total > 0:
                module.docstring_coverage = (with_docstring / total) * 100

            # Sammle fehlende Docstrings (nur für public Funktionen)
            for func in module.function_details:
                if not func.has_docstring and not func.name.startswith('_'):
                    module.missing_docstrings.append(func.name)

        # Projekt-Durchschnitt
        coverages = [m.docstring_coverage for m in self.analysis.modules.values()
                     if m.function_details]
        if coverages:
            self.analysis.avg_docstring_coverage = sum(coverages) / len(coverages)

    # =========================================================================
    # NEU v6.0: TYPE-ANNOTATION CHECK
    # =========================================================================

    def _analyze_type_annotations(self):
        """Analysiert Type-Hint-Abdeckung"""
        for name, module in self.analysis.modules.items():
            if not module.function_details:
                continue

            fully_typed = sum(1 for f in module.function_details
                              if f.has_return_type and f.has_all_param_types)
            total = len(module.function_details)

            if total > 0:
                module.type_coverage = (fully_typed / total) * 100

            # Sammle fehlende Types (nur für public Funktionen)
            for func in module.function_details:
                if not func.name.startswith('_'):
                    if not func.has_return_type or not func.has_all_param_types:
                        module.missing_types.append(func.name)

        # Projekt-Durchschnitt
        coverages = [m.type_coverage for m in self.analysis.modules.values()
                     if m.function_details]
        if coverages:
            self.analysis.avg_type_coverage = sum(coverages) / len(coverages)

    # =========================================================================
    # NEU v6.0: KOMPLEXITÄTS-ANALYSE
    # =========================================================================

    def _analyze_complexity(self):
        """Berechnet Komplexitäts-Metriken für alle Module"""
        for name, module in self.analysis.modules.items():
            if not module.syntax_ok:
                continue

            try:
                source = module.path.read_text(encoding="utf-8", errors="ignore")
                lines = source.splitlines()

                # Zähle Zeilen
                code_lines = 0
                comment_lines = 0
                blank_lines = 0

                in_multiline_string = False
                for line in lines:
                    stripped = line.strip()

                    if not stripped:
                        blank_lines += 1
                    elif stripped.startswith('#'):
                        comment_lines += 1
                    elif stripped.startswith('"""') or stripped.startswith("'''"):
                        if in_multiline_string:
                            in_multiline_string = False
                        else:
                            in_multiline_string = True
                        comment_lines += 1
                    elif in_multiline_string:
                        comment_lines += 1
                    else:
                        code_lines += 1

                # Komplexität berechnen
                complexities = [f.complexity for f in module.function_details]
                total_complexity = sum(complexities) if complexities else 0
                max_complexity = max(complexities) if complexities else 0
                avg_complexity = total_complexity / len(complexities) if complexities else 0

                max_func = ""
                for f in module.function_details:
                    if f.complexity == max_complexity:
                        max_func = f.name
                        break

                # Wartbarkeits-Index (Microsoft-Formel, vereinfacht)
                # MI = 171 - 5.2*ln(HV) - 0.23*CC - 16.2*ln(LOC)
                # Vereinfacht: MI = 100 - (avg_complexity * 3) - (code_lines * 0.01)
                mi = 100 - (avg_complexity * 3) - (code_lines * 0.01)
                mi = max(0, min(100, mi))  # Clamp 0-100

                module.complexity_info = ComplexityInfo(
                    total_complexity=total_complexity,
                    max_complexity=max_complexity,
                    max_complex_function=max_func,
                    avg_complexity=avg_complexity,
                    maintainability_index=mi,
                    functions_above_10=sum(1 for c in complexities if c > 10),
                    lines_of_code=code_lines,
                    comment_lines=comment_lines,
                    blank_lines=blank_lines
                )

                self.analysis.total_complexity += total_complexity

            except Exception:
                pass

        # Projekt-Durchschnitt
        all_complexities = [m.complexity_info.avg_complexity
                           for m in self.analysis.modules.values()
                           if m.function_details]
        if all_complexities:
            self.analysis.avg_complexity = sum(all_complexities) / len(all_complexities)

    # =========================================================================
    # NEU v6.0: SICHERHEITS-AUDIT
    # =========================================================================

    def _security_audit(self):
        """Führt Sicherheits-Audit durch"""
        for name, module in self.analysis.modules.items():
            if not module.syntax_ok:
                continue

            try:
                source = module.path.read_text(encoding="utf-8", errors="ignore")
                lines = source.splitlines()

                for severity, category, pattern, message, recommendation in SECURITY_PATTERNS:
                    try:
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                issue = SecurityIssue(
                                    severity=severity,
                                    category=category,
                                    module=name,
                                    line=i,
                                    code=line.strip()[:60],
                                    message=message,
                                    recommendation=recommendation
                                )
                                module.security_issues.append(issue)
                                self.analysis.all_security_issues.append(issue)
                    except re.error:
                        pass  # Ungültiges Pattern

            except Exception:
                pass

    # =========================================================================
    # NEU v6.0: CONFIG-VOLLSTÄNDIGKEIT
    # =========================================================================

    def _check_config_completeness(self):
        """Prüft ob alle verwendeten Config-Keys existieren"""
        if not self.analysis.config:
            return

        # Sammle alle verfügbaren Keys (flach)
        def flatten_keys(d: dict, prefix: str = "") -> Set[str]:
            keys = set()
            for k, v in d.items():
                full_key = f"{prefix}.{k}" if prefix else k
                keys.add(full_key)
                keys.add(k)  # Auch ohne Prefix
                if isinstance(v, dict):
                    keys.update(flatten_keys(v, full_key))
            return keys

        available_keys = flatten_keys(self.analysis.config)

        # Sammle alle verwendeten Keys aus allen Modulen
        all_used_keys = set()
        for module in self.analysis.modules.values():
            all_used_keys.update(module.config_keys_used)

        # Prüfe auf fehlende Keys
        for key in all_used_keys:
            # Suche nach Key (exakt oder als Teil)
            found = False
            for available in available_keys:
                if key == available or key in available or available.endswith(f".{key}"):
                    found = True
                    break

            if not found and not key.startswith("HOLO_"):
                self.analysis.config_issues.append(f"Config-Key '{key}' nicht gefunden")

        # Prüfe auch auf ungenutzte Config-Keys (optional)
        for available in available_keys:
            if "." in available:  # Nur top-level
                continue
            used = any(available in k or k == available for k in all_used_keys)
            # Nicht warnen für ungenutzte Keys - ist normal

    # =========================================================================
    # NEU v6.0: DATENBANK-SCHEMA CHECK
    # =========================================================================

    def _check_database_schema(self):
        """Prüft SQLite-Datenbank-Schema"""
        # Suche nach DB-Dateien
        db_files = list(self.project_dir.glob("**/*.db"))
        db_files.extend(self.project_dir.glob("**/*.sqlite"))
        db_files.extend(self.project_dir.glob("**/*.sqlite3"))

        # Filtere __pycache__
        db_files = [f for f in db_files if "__pycache__" not in str(f)]

        if not db_files:
            return

        # Sammle erwartete Tabellen aus Code
        expected_tables = self._find_expected_tables()

        for db_file in db_files:
            try:
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()

                # Hole alle Tabellen
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                self.analysis.db_tables.extend(tables)

                # Prüfe ob erwartete Tabellen existieren
                for expected in expected_tables:
                    if expected not in tables:
                        self.analysis.db_issues.append(
                            f"Tabelle '{expected}' fehlt in {db_file.name}"
                        )

                # Prüfe Schema-Integrität
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                if result[0] != "ok":
                    self.analysis.db_issues.append(
                        f"{db_file.name}: Integritätsprüfung fehlgeschlagen"
                    )

                conn.close()

            except sqlite3.Error as e:
                self.analysis.db_issues.append(f"{db_file.name}: {str(e)[:50]}")

    def _find_expected_tables(self) -> Set[str]:
        """Findet erwartete Tabellen aus CREATE TABLE Statements im Code"""
        tables = set()

        for module in self.analysis.modules.values():
            try:
                source = module.path.read_text(encoding="utf-8", errors="ignore")

                # Suche nach CREATE TABLE
                patterns = [
                    r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["\']?(\w+)["\']?',
                    r'\.execute\([^)]*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["\']?(\w+)',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, source, re.IGNORECASE)
                    tables.update(matches)

            except Exception:
                pass

        return tables

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
        description="Holocloude Intelligent System Tester v6.0 - Vollständige Code-Qualitäts-Analyse"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Mehr Details")
    parser.add_argument("--no-color", action="store_true", help="Keine Farben")
    parser.add_argument("--quick", "-q", action="store_true", help="Schneller Start-Check (nur Syntax + Import)")
    parser.add_argument("--explain", action="store_true", help="Erklärt was jedes Modul tut")
    parser.add_argument("--problems", action="store_true", help="Nur Probleme anzeigen")
    parser.add_argument("--graph", action="store_true", help="Zeigt Dependency-Graph")
    parser.add_argument("--redundancy", action="store_true", help="Zeigt Redundanzen und doppelten Code")
    parser.add_argument("--imports", action="store_true", help="Zeigt Import-Ketten und -Abhängigkeiten")
    parser.add_argument("--trace", type=str, metavar="MODULE", help="Verfolgt alle Imports eines bestimmten Moduls")

    # NEU v6.0: Erweiterte Prüfungen
    parser.add_argument("--functions", action="store_true", help="Funktions-Test: Prüft Aufrufbarkeit aller Funktionen")
    parser.add_argument("--docstrings", action="store_true", help="Docstring-Check: Analysiert Dokumentations-Abdeckung")
    parser.add_argument("--types", action="store_true", help="Type-Annotation Check: Prüft Type-Hints")
    parser.add_argument("--complexity", action="store_true", help="Komplexitäts-Analyse: McCabe + Wartbarkeits-Index")
    parser.add_argument("--security", action="store_true", help="Sicherheits-Audit: Findet bekannte Schwachstellen")
    parser.add_argument("--config", action="store_true", help="Config-Check: Prüft Config-Vollständigkeit")
    parser.add_argument("--db", action="store_true", help="Datenbank-Schema Check: Verifiziert SQLite-Tabellen")
    parser.add_argument("--all", action="store_true", help="Alle erweiterten Prüfungen ausführen")

    args = parser.parse_args()

    if args.no_color:
        Colors.disable()

    print()
    print(f"{Colors.BOLD}{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║      HOLOCLOUDE INTELLIGENT SYSTEM TESTER v6.0               ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║      {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^50} ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")

    # Analyse
    analyzer = IntelligentAnalyzer()
    analysis = analyzer.analyze(quick_mode=args.quick)

    if not args.quick:
        print(f"{Colors.DIM}  Gefunden: {len(analysis.modules)} Module, "
              f"{analysis.total_classes} Klassen, "
              f"{analysis.total_functions} Funktionen{Colors.RESET}")
    else:
        print(f"{Colors.DIM}  Gefunden: {len(analysis.modules)} Module{Colors.RESET}")

    # Quick-Modus: Nur Import-Test Ergebnisse
    if args.quick:
        print()
        print(f"{Colors.BOLD}SCHNELLER START-CHECK:{Colors.RESET}")

        success_count = len(analysis.import_successes)
        fail_count = len(analysis.import_failures)
        total = success_count + fail_count

        print(f"\n{Colors.BOLD}Import-Test Ergebnisse:{Colors.RESET}")
        print(f"  {Colors.GREEN}✓ {success_count}/{total} Module erfolgreich importiert{Colors.RESET}")

        if analysis.import_failures:
            print(f"  {Colors.RED}✗ {fail_count} Module fehlgeschlagen:{Colors.RESET}")
            for module, error in analysis.import_failures[:15]:
                short_error = error[:80] + "..." if len(error) > 80 else error
                print(f"      {Colors.RED}• {module}: {short_error}{Colors.RESET}")

            if len(analysis.import_failures) > 15:
                print(f"      {Colors.DIM}... und {len(analysis.import_failures) - 15} weitere{Colors.RESET}")

        print()
        if fail_count == 0:
            print(f"  {Colors.GREEN}{Colors.BOLD}✓ ALLE MODULE STARTEN OHNE FEHLER{Colors.RESET}")
        else:
            print(f"  {Colors.RED}{Colors.BOLD}✗ {fail_count} MODULE HABEN PROBLEME{Colors.RESET}")

        sys.exit(1 if fail_count > 0 else 0)

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

    # Redundancy-Modus
    if args.redundancy:
        print()
        print(f"{Colors.BOLD}REDUNDANZ-ANALYSE:{Colors.RESET}")

        if analysis.duplicate_functions:
            print(f"\n{Colors.YELLOW}Doppelte Funktionsnamen ({len(analysis.duplicate_functions)}):{Colors.RESET}")
            for func, mod1, mod2 in analysis.duplicate_functions[:20]:
                print(f"  • {func}: {mod1}, {mod2}")

        # Zeige alle Funktionen die in mehreren Modulen vorkommen
        multi_funcs = {k: v for k, v in analysis.global_function_names.items() if len(v) > 2}
        if multi_funcs:
            print(f"\n{Colors.YELLOW}Funktionen in 3+ Modulen:{Colors.RESET}")
            for func, modules in sorted(multi_funcs.items(), key=lambda x: -len(x[1]))[:10]:
                print(f"  • {func} ({len(modules)}x): {', '.join(modules[:5])}")

        # Zeige potenziell ungenutzten Code
        unused_total = sum(len(m.potentially_unused) for m in analysis.modules.values())
        if unused_total > 0:
            print(f"\n{Colors.YELLOW}Potenziell ungenutzter Code ({unused_total} Funktionen):{Colors.RESET}")
            for name, module in analysis.modules.items():
                if module.potentially_unused:
                    print(f"  {name}: {', '.join(module.potentially_unused[:5])}")
                    if len(module.potentially_unused) > 5:
                        print(f"          ... und {len(module.potentially_unused) - 5} weitere")

        if not analysis.duplicate_functions and not multi_funcs and unused_total == 0:
            print(f"\n{Colors.GREEN}Keine signifikanten Redundanzen gefunden!{Colors.RESET}")

        sys.exit(0)

    # Imports-Modus: Zeigt Import-Ketten
    if args.imports:
        print()
        print(f"{Colors.BOLD}IMPORT-ANALYSE:{Colors.RESET}")

        # Zeige kaputte Import-Ketten
        if analysis.broken_import_chains:
            print(f"\n{Colors.RED}Unterbrochene Import-Ketten ({len(analysis.broken_import_chains)}):{Colors.RESET}")
            for module, dep, error in analysis.broken_import_chains[:15]:
                print(f"  {Colors.RED}✗ {module} → {dep}: {error[:50]}{Colors.RESET}")

        # Zeige fehlende importierte Items
        if analysis.missing_items_report:
            print(f"\n{Colors.YELLOW}Fehlende importierte Items ({len(analysis.missing_items_report)}):{Colors.RESET}")
            for module, item, source in analysis.missing_items_report[:15]:
                print(f"  {Colors.YELLOW}⚠ {module}: '{item}' nicht in {source}{Colors.RESET}")

        # Zeige meistgenutzte Module (Import-Baum)
        if analysis.import_tree:
            print(f"\n{Colors.CYAN}Meistgenutzte Module (wer importiert was):{Colors.RESET}")
            sorted_imports = sorted(analysis.import_tree.items(), key=lambda x: len(x[1]), reverse=True)
            for source, importers in sorted_imports[:15]:
                if source.startswith("holo_"):
                    print(f"  {Colors.CYAN}{source}{Colors.RESET} wird importiert von {len(importers)} Modulen")
                    if len(importers) <= 5:
                        print(f"      → {', '.join(importers)}")

        # Statistik
        total_imports = sum(len(m.imported_items) for m in analysis.modules.values())
        failed_imports = sum(len(m.failed_imports) for m in analysis.modules.values())
        missing_items = sum(len(m.missing_imported_items) for m in analysis.modules.values())

        print(f"\n{Colors.BOLD}Statistik:{Colors.RESET}")
        print(f"  Gesamt Imports: {total_imports}")
        print(f"  Fehlgeschlagen: {failed_imports}")
        print(f"  Fehlende Items: {missing_items}")

        if failed_imports == 0 and missing_items == 0:
            print(f"\n  {Colors.GREEN}✓ ALLE IMPORT-KETTEN INTAKT{Colors.RESET}")
        else:
            print(f"\n  {Colors.YELLOW}⚠ {failed_imports + missing_items} PROBLEME GEFUNDEN{Colors.RESET}")

        sys.exit(0)

    # Trace-Modus: Verfolgt Imports eines bestimmten Moduls
    if args.trace:
        module_name = args.trace
        print()
        print(f"{Colors.BOLD}IMPORT-TRACE für '{module_name}':{Colors.RESET}")

        if module_name not in analysis.modules:
            print(f"{Colors.RED}Modul '{module_name}' nicht gefunden!{Colors.RESET}")
            print(f"Verfügbare Module: {', '.join(sorted(analysis.modules.keys())[:10])}...")
            sys.exit(1)

        module = analysis.modules[module_name]

        # Zeige was dieses Modul importiert
        print(f"\n{Colors.CYAN}Was '{module_name}' importiert:{Colors.RESET}")
        if module.imported_items:
            for item in module.imported_items:
                status = f"{Colors.GREEN}✓{Colors.RESET}" if item.exists else f"{Colors.RED}✗{Colors.RESET}"
                type_info = f" [{item.actual_type}]" if item.actual_type else ""
                print(f"  {status} from {item.source_module} import {item.name}{type_info}")
        else:
            print(f"  {Colors.DIM}(keine Projekt-internen Imports gefunden){Colors.RESET}")

        # Zeige wer dieses Modul importiert
        print(f"\n{Colors.CYAN}Wer '{module_name}' importiert:{Colors.RESET}")
        if module.used_by_modules:
            for user in sorted(module.used_by_modules):
                print(f"  ← {user}")
        else:
            print(f"  {Colors.DIM}(wird von keinem Modul importiert){Colors.RESET}")

        # Zeige fehlgeschlagene Imports
        if module.failed_imports:
            print(f"\n{Colors.RED}Fehlgeschlagene Imports:{Colors.RESET}")
            for imp, error in module.failed_imports:
                print(f"  {Colors.RED}✗ {imp}: {error}{Colors.RESET}")

        # Zeige fehlende Items
        if module.missing_imported_items:
            print(f"\n{Colors.YELLOW}Fehlende importierte Items:{Colors.RESET}")
            for item in module.missing_imported_items:
                print(f"  {Colors.YELLOW}⚠ {item}{Colors.RESET}")

        # Zeige Import-Kette (Reihenfolge)
        if module.import_chain:
            print(f"\n{Colors.DIM}Import-Reihenfolge (muss vor {module_name} geladen sein):{Colors.RESET}")
            print(f"  {' → '.join(module.import_chain[-5:])}{' → ...' if len(module.import_chain) > 5 else ''}")

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

    # ==========================================================================
    # NEU v6.0: Erweiterte Prüfungen
    # ==========================================================================

    # Funktions-Test
    if args.functions or args.all:
        print()
        print(f"{Colors.BOLD}FUNKTIONS-ANALYSE:{Colors.RESET}")

        total_funcs = sum(len(m.function_details) for m in analysis.modules.values())
        callable_funcs = sum(
            sum(1 for f in m.function_details if f.is_callable)
            for m in analysis.modules.values()
        )

        print(f"\n  {Colors.GREEN}✓ {callable_funcs}/{total_funcs} Funktionen aufrufbar{Colors.RESET}")

        # Zeige nicht-aufrufbare
        not_callable = []
        for name, module in analysis.modules.items():
            for func in module.function_details:
                if not func.is_callable:
                    not_callable.append((name, func.name, func.call_error))

        if not_callable:
            print(f"\n  {Colors.RED}Nicht aufrufbar ({len(not_callable)}):{Colors.RESET}")
            for mod, func, error in not_callable[:10]:
                print(f"    • {mod}.{func}: {error}")

        # Zeige komplexe Funktionen
        if analysis.complex_functions:
            print(f"\n  {Colors.YELLOW}Komplexe Funktionen (Complexity > 10):{Colors.RESET}")
            for mod, func, comp in sorted(analysis.complex_functions, key=lambda x: -x[2])[:10]:
                color = Colors.RED if comp > 20 else Colors.YELLOW
                print(f"    {color}• {mod}.{func}: {comp}{Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # Docstring-Check
    if args.docstrings or args.all:
        print()
        print(f"{Colors.BOLD}DOCSTRING-ABDECKUNG:{Colors.RESET}")

        print(f"\n  Projekt-Durchschnitt: {Colors.CYAN}{analysis.avg_docstring_coverage:.1f}%{Colors.RESET}")

        # Zeige Module mit niedriger Abdeckung
        low_coverage = [(n, m.docstring_coverage) for n, m in analysis.modules.items()
                        if m.function_details and m.docstring_coverage < 50]
        low_coverage.sort(key=lambda x: x[1])

        if low_coverage:
            print(f"\n  {Colors.YELLOW}Module mit < 50% Docstrings:{Colors.RESET}")
            for name, coverage in low_coverage[:10]:
                print(f"    • {name}: {coverage:.1f}%")

        # Zeige Module ohne Docstrings
        no_docs = [(n, m.missing_docstrings) for n, m in analysis.modules.items()
                   if len(m.missing_docstrings) > 3]
        if no_docs:
            print(f"\n  {Colors.YELLOW}Module mit vielen fehlenden Docstrings:{Colors.RESET}")
            for name, missing in sorted(no_docs, key=lambda x: -len(x[1]))[:5]:
                print(f"    • {name}: {len(missing)} Funktionen ohne Docstring")

        if analysis.avg_docstring_coverage >= 80:
            print(f"\n  {Colors.GREEN}✓ Gute Dokumentation!{Colors.RESET}")
        elif analysis.avg_docstring_coverage >= 50:
            print(f"\n  {Colors.YELLOW}⚠ Dokumentation könnte verbessert werden{Colors.RESET}")
        else:
            print(f"\n  {Colors.RED}✗ Dokumentation ist unzureichend{Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # Type-Annotation Check
    if args.types or args.all:
        print()
        print(f"{Colors.BOLD}TYPE-ANNOTATION ABDECKUNG:{Colors.RESET}")

        print(f"\n  Projekt-Durchschnitt: {Colors.CYAN}{analysis.avg_type_coverage:.1f}%{Colors.RESET}")

        # Zeige Module mit niedriger Abdeckung
        low_type = [(n, m.type_coverage) for n, m in analysis.modules.items()
                    if m.function_details and m.type_coverage < 30]
        low_type.sort(key=lambda x: x[1])

        if low_type:
            print(f"\n  {Colors.YELLOW}Module mit < 30% Type-Hints:{Colors.RESET}")
            for name, coverage in low_type[:10]:
                print(f"    • {name}: {coverage:.1f}%")

        if analysis.avg_type_coverage >= 70:
            print(f"\n  {Colors.GREEN}✓ Gute Type-Annotation!{Colors.RESET}")
        elif analysis.avg_type_coverage >= 30:
            print(f"\n  {Colors.YELLOW}⚠ Type-Hints könnten verbessert werden{Colors.RESET}")
        else:
            print(f"\n  {Colors.DIM}Type-Hints sind optional, aber empfohlen{Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # Komplexitäts-Analyse
    if args.complexity or args.all:
        print()
        print(f"{Colors.BOLD}KOMPLEXITÄTS-ANALYSE:{Colors.RESET}")

        print(f"\n  Gesamt-Komplexität: {analysis.total_complexity}")
        print(f"  Durchschnitt: {analysis.avg_complexity:.1f}")

        # Zeige komplexeste Module
        complex_modules = [(n, m.complexity_info) for n, m in analysis.modules.items()
                          if m.complexity_info.max_complexity > 0]
        complex_modules.sort(key=lambda x: -x[1].max_complexity)

        if complex_modules:
            print(f"\n  {Colors.CYAN}Komplexeste Module:{Colors.RESET}")
            for name, ci in complex_modules[:10]:
                mi_color = Colors.GREEN if ci.maintainability_index >= 70 else (
                    Colors.YELLOW if ci.maintainability_index >= 40 else Colors.RED)
                print(f"    • {name}: max={ci.max_complexity} ({ci.max_complex_function}), "
                      f"MI={mi_color}{ci.maintainability_index:.0f}{Colors.RESET}")

        # Wartbarkeits-Index Zusammenfassung
        mis = [m.complexity_info.maintainability_index for m in analysis.modules.values()
               if m.function_details]
        if mis:
            avg_mi = sum(mis) / len(mis)
            print(f"\n  Durchschnittlicher Wartbarkeits-Index: ", end="")
            if avg_mi >= 70:
                print(f"{Colors.GREEN}{avg_mi:.0f} (Gut){Colors.RESET}")
            elif avg_mi >= 40:
                print(f"{Colors.YELLOW}{avg_mi:.0f} (Akzeptabel){Colors.RESET}")
            else:
                print(f"{Colors.RED}{avg_mi:.0f} (Refactoring nötig){Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # Sicherheits-Audit
    if args.security or args.all:
        print()
        print(f"{Colors.BOLD}SICHERHEITS-AUDIT:{Colors.RESET}")

        if not analysis.all_security_issues:
            print(f"\n  {Colors.GREEN}✓ Keine offensichtlichen Sicherheitsprobleme gefunden!{Colors.RESET}")
        else:
            # Gruppiere nach Severity
            by_severity = defaultdict(list)
            for issue in analysis.all_security_issues:
                by_severity[issue.severity].append(issue)

            for severity in ["critical", "high", "medium", "low"]:
                issues = by_severity.get(severity, [])
                if not issues:
                    continue

                color = {
                    "critical": Colors.RED + Colors.BOLD,
                    "high": Colors.RED,
                    "medium": Colors.YELLOW,
                    "low": Colors.DIM
                }.get(severity, "")

                print(f"\n  {color}{severity.upper()} ({len(issues)}):{Colors.RESET}")
                for issue in issues[:5]:
                    print(f"    • [{issue.module}:{issue.line}] {issue.message}")
                    print(f"      {Colors.DIM}Code: {issue.code[:50]}{Colors.RESET}")
                    print(f"      {Colors.CYAN}→ {issue.recommendation}{Colors.RESET}")

                if len(issues) > 5:
                    print(f"    {Colors.DIM}... und {len(issues) - 5} weitere{Colors.RESET}")

            # Zusammenfassung
            critical = len(by_severity.get("critical", []))
            high = len(by_severity.get("high", []))

            if critical > 0:
                print(f"\n  {Colors.RED}{Colors.BOLD}⚠ KRITISCHE SICHERHEITSLÜCKEN GEFUNDEN!{Colors.RESET}")
            elif high > 0:
                print(f"\n  {Colors.YELLOW}⚠ Sicherheitsprobleme sollten behoben werden{Colors.RESET}")
            else:
                print(f"\n  {Colors.GREEN}✓ Keine kritischen Sicherheitsprobleme{Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # Config-Check
    if args.config or args.all:
        print()
        print(f"{Colors.BOLD}CONFIG-VOLLSTÄNDIGKEIT:{Colors.RESET}")

        if not analysis.config:
            print(f"\n  {Colors.YELLOW}⚠ Keine config.json gefunden{Colors.RESET}")
        else:
            config_keys = len(analysis.config)
            print(f"\n  Config geladen: {config_keys} Top-Level Keys")

            if analysis.config_issues:
                print(f"\n  {Colors.YELLOW}Fehlende Config-Keys ({len(analysis.config_issues)}):{Colors.RESET}")
                for issue in analysis.config_issues[:10]:
                    print(f"    • {issue}")
            else:
                print(f"\n  {Colors.GREEN}✓ Alle verwendeten Config-Keys sind vorhanden{Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # Datenbank-Check
    if args.db or args.all:
        print()
        print(f"{Colors.BOLD}DATENBANK-SCHEMA CHECK:{Colors.RESET}")

        if not analysis.db_tables:
            print(f"\n  {Colors.DIM}Keine SQLite-Datenbanken gefunden{Colors.RESET}")
        else:
            # Unique tables
            unique_tables = list(set(analysis.db_tables))
            print(f"\n  Gefundene Tabellen: {len(unique_tables)}")
            if unique_tables:
                print(f"    {', '.join(sorted(unique_tables)[:15])}")
                if len(unique_tables) > 15:
                    print(f"    ... und {len(unique_tables) - 15} weitere")

            if analysis.db_issues:
                print(f"\n  {Colors.YELLOW}DB-Probleme ({len(analysis.db_issues)}):{Colors.RESET}")
                for issue in analysis.db_issues[:10]:
                    print(f"    • {issue}")
            else:
                print(f"\n  {Colors.GREEN}✓ Datenbank-Schema OK{Colors.RESET}")

        if not args.all:
            sys.exit(0)

    # --all Modus: Zusammenfassung
    if args.all:
        print()
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  ZUSAMMENFASSUNG ALLER PRÜFUNGEN{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")

        # Berechne Funktions-Aufrufbarkeit
        total_funcs = sum(len(m.function_details) for m in analysis.modules.values())
        callable_funcs = sum(sum(1 for f in m.function_details if f.is_callable)
                             for m in analysis.modules.values())
        func_ratio = callable_funcs / max(1, total_funcs)

        checks = [
            ("Funktionen aufrufbar (>= 99%)", func_ratio >= 0.99),
            ("Docstring-Abdeckung >= 50%", analysis.avg_docstring_coverage >= 50),
            ("Type-Hints >= 30%", analysis.avg_type_coverage >= 30),
            ("Keine kritischen Security-Issues", not any(i.severity == "critical" for i in analysis.all_security_issues)),
            ("Config vollständig", len(analysis.config_issues) == 0),
            ("DB-Schema OK", len(analysis.db_issues) == 0),
        ]

        passed = sum(1 for _, ok in checks if ok)
        print()
        for name, ok in checks:
            icon = f"{Colors.GREEN}✓{Colors.RESET}" if ok else f"{Colors.RED}✗{Colors.RESET}"
            print(f"  {icon} {name}")

        print()
        print(f"  {passed}/{len(checks)} Prüfungen bestanden")

        sys.exit(0)

    # Standard: Alle Tests
    tester = IntelligentTester(analysis, verbose=args.verbose)
    tester.run_all_tests()

    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == "__main__":
    main()
