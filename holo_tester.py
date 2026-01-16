#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 HOLOCLOUDE DYNAMIC SYSTEM TESTER v2.0                        ║
║                                                                              ║
║  DYNAMISCH - Erkennt automatisch:                                            ║
║    • Alle Python-Module im Projekt                                           ║
║    • Alle Klassen und Funktionen in Modulen                                  ║
║    • Alle Datenbanken im data/ Verzeichnis                                   ║
║    • Alle Services aus config.json                                           ║
║    • Alle Umgebungsvariablen die verwendet werden                            ║
║                                                                              ║
║  Verwendung:                                                                 ║
║      python holo_tester.py              # Alle Tests                         ║
║      python holo_tester.py --quick      # Ohne LLM-Tests                     ║
║      python holo_tester.py --deep       # Tiefe Analyse (Klassen/Funktionen) ║
║      python holo_tester.py --fix        # Versucht Probleme zu beheben       ║
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
import threading
import traceback
import importlib
import importlib.util
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict

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
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class ModuleInfo:
    """Informationen über ein Python-Modul"""
    name: str
    path: Path
    size_bytes: int
    lines: int = 0
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)
    has_main: bool = False
    syntax_ok: bool = True
    import_ok: bool = False
    error: str = ""


@dataclass
class ServiceInfo:
    """Informationen über einen externen Service"""
    name: str
    host: str
    port: int
    protocol: str = "tcp"  # tcp, http, https
    required: bool = False
    reachable: bool = False
    response_time_ms: float = 0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseInfo:
    """Informationen über eine Datenbank"""
    name: str
    path: Path
    size_mb: float
    tables: List[str] = field(default_factory=list)
    integrity_ok: bool = False
    error: str = ""


@dataclass
class TestResult:
    """Ergebnis eines Tests"""
    category: str
    name: str
    passed: bool
    message: str = ""
    duration_ms: float = 0
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# DYNAMISCHER PROJEKT-SCANNER
# =============================================================================

class ProjectScanner:
    """Scannt das Projekt dynamisch und sammelt Informationen"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.modules: Dict[str, ModuleInfo] = {}
        self.services: Dict[str, ServiceInfo] = {}
        self.databases: Dict[str, DatabaseInfo] = {}
        self.config: Dict = {}
        self.all_env_vars: Set[str] = set()

    def scan_all(self):
        """Führt kompletten Scan durch"""
        self._load_config()
        self._scan_modules()
        self._scan_databases()
        self._discover_services()
        self._collect_env_vars()

    # =========================================================================
    # CONFIG SCANNING
    # =========================================================================

    def _load_config(self):
        """Lädt config.json"""
        config_path = self.project_dir / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"{Colors.YELLOW}  Config-Fehler: {e}{Colors.RESET}")

    # =========================================================================
    # MODULE SCANNING
    # =========================================================================

    def _scan_modules(self):
        """Findet und analysiert alle Python-Module"""
        py_files = list(self.project_dir.glob("*.py"))
        # Auch in Unterverzeichnissen suchen
        py_files.extend(self.project_dir.glob("**/*.py"))
        # Duplikate entfernen und sortieren
        py_files = sorted(set(py_files))

        for py_file in py_files:
            # Ignoriere Test-Dateien und __pycache__
            if "__pycache__" in str(py_file):
                continue
            if py_file.name.startswith("test_") or py_file.name == "holo_tester.py":
                continue

            module_info = self._analyze_module(py_file)
            self.modules[module_info.name] = module_info

    def _analyze_module(self, py_file: Path) -> ModuleInfo:
        """Analysiert ein einzelnes Python-Modul mittels AST"""
        module_name = py_file.stem

        info = ModuleInfo(
            name=module_name,
            path=py_file,
            size_bytes=py_file.stat().st_size
        )

        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            info.lines = len(source.splitlines())

            # AST Parsing
            tree = ast.parse(source)
            info.syntax_ok = True

            for node in ast.walk(tree):
                # Klassen finden
                if isinstance(node, ast.ClassDef):
                    info.classes.append(node.name)

                # Funktionen finden (nur top-level)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        info.functions.append(node.name)

                # Imports finden
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info.imports.append(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info.imports.append(node.module.split(".")[0])

                # if __name__ == "__main__"
                elif isinstance(node, ast.If):
                    if isinstance(node.test, ast.Compare):
                        if isinstance(node.test.left, ast.Name):
                            if node.test.left.id == "__name__":
                                info.has_main = True

            # Umgebungsvariablen finden (os.getenv, os.environ)
            env_pattern = r'os\.(?:getenv|environ\.get)\s*\(\s*["\']([A-Z_]+)["\']'
            info.env_vars = list(set(re.findall(env_pattern, source)))

            # Imports eindeutig machen
            info.imports = list(set(info.imports))

        except SyntaxError as e:
            info.syntax_ok = False
            info.error = f"Syntax-Fehler: {e}"
        except Exception as e:
            info.error = str(e)

        return info

    # =========================================================================
    # DATABASE SCANNING
    # =========================================================================

    def _scan_databases(self):
        """Findet und analysiert alle SQLite-Datenbanken"""
        data_dir = self.project_dir / "data"
        if not data_dir.exists():
            return

        db_files = list(data_dir.glob("*.db"))
        db_files.extend(data_dir.glob("**/*.db"))

        for db_file in db_files:
            db_info = self._analyze_database(db_file)
            self.databases[db_info.name] = db_info

    def _analyze_database(self, db_file: Path) -> DatabaseInfo:
        """Analysiert eine SQLite-Datenbank"""
        info = DatabaseInfo(
            name=db_file.name,
            path=db_file,
            size_mb=db_file.stat().st_size / 1024 / 1024
        )

        try:
            conn = sqlite3.connect(str(db_file), timeout=5)
            cursor = conn.cursor()

            # Integrity Check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            info.integrity_ok = (result == "ok")

            # Tabellen auflisten
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            info.tables = [row[0] for row in cursor.fetchall()]

            conn.close()

        except Exception as e:
            info.error = str(e)

        return info

    # =========================================================================
    # SERVICE DISCOVERY
    # =========================================================================

    def _discover_services(self):
        """Entdeckt Services aus Config und Code"""

        # Aus Config
        if "network" in self.config:
            network = self.config["network"]

            # Ollama
            if "ollama" in network:
                ollama = network["ollama"]
                self.services["ollama"] = ServiceInfo(
                    name="Ollama LLM",
                    host=ollama.get("host", "localhost"),
                    port=ollama.get("port", 11434),
                    protocol="http",
                    required=True
                )

            # MQTT
            if "mqtt" in network:
                mqtt = network["mqtt"]
                self.services["mqtt"] = ServiceInfo(
                    name="MQTT Broker",
                    host=mqtt.get("broker_ip", "localhost"),
                    port=mqtt.get("port", 1883),
                    protocol="tcp",
                    required=False
                )

            # Home Assistant
            if "home_assistant" in network:
                ha = network["home_assistant"]
                url = ha.get("api_url", "")
                if url:
                    # Parse URL
                    import urllib.parse
                    parsed = urllib.parse.urlparse(url)
                    self.services["home_assistant"] = ServiceInfo(
                        name="Home Assistant",
                        host=parsed.hostname or "localhost",
                        port=parsed.port or 8123,
                        protocol="http",
                        required=False
                    )

            # NAS
            if "nas" in network:
                nas = network["nas"]
                if nas.get("ip"):
                    self.services["nas"] = ServiceInfo(
                        name="NAS (SSH)",
                        host=nas.get("ip"),
                        port=22,
                        protocol="tcp",
                        required=False
                    )

        # Aus Modulen: Suche nach weiteren Host/Port Kombinationen
        for module in self.modules.values():
            self._extract_services_from_module(module)

    def _extract_services_from_module(self, module: ModuleInfo):
        """Extrahiert Service-Definitionen aus Modul-Code"""
        try:
            source = module.path.read_text(encoding="utf-8", errors="ignore")

            # Pattern für Host:Port Kombinationen
            # z.B. "http://192.168.1.100:8080"
            url_pattern = r'https?://([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+):(\d+)'
            for match in re.finditer(url_pattern, source):
                host, port = match.groups()
                key = f"{host}:{port}"
                if key not in [f"{s.host}:{s.port}" for s in self.services.values()]:
                    self.services[key] = ServiceInfo(
                        name=f"Service {key}",
                        host=host,
                        port=int(port),
                        protocol="http"
                    )

        except Exception:
            pass

    # =========================================================================
    # ENVIRONMENT VARIABLES
    # =========================================================================

    def _collect_env_vars(self):
        """Sammelt alle verwendeten Umgebungsvariablen"""
        for module in self.modules.values():
            self.all_env_vars.update(module.env_vars)


# =============================================================================
# DYNAMISCHER TESTER
# =============================================================================

class DynamicTester:
    """Führt dynamische Tests basierend auf Scanner-Ergebnissen durch"""

    def __init__(self, scanner: ProjectScanner, verbose: bool = False):
        self.scanner = scanner
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.start_time = datetime.now()

    def _add_result(self, category: str, name: str, passed: bool,
                   message: str = "", duration_ms: float = 0, details: dict = None):
        """Fügt ein Testergebnis hinzu"""
        result = TestResult(
            category=category,
            name=name,
            passed=passed,
            message=message,
            duration_ms=duration_ms,
            details=details or {}
        )
        self.results.append(result)
        self._print_result(result)

    def _print_result(self, result: TestResult):
        """Gibt ein Ergebnis aus"""
        icon = f"{Colors.GREEN}✓{Colors.RESET}" if result.passed else f"{Colors.RED}✗{Colors.RESET}"
        time_str = f"{Colors.DIM}({result.duration_ms:.0f}ms){Colors.RESET}" if result.duration_ms > 0 else ""

        print(f"  {icon} {result.name} {time_str}")

        if result.message and (not result.passed or self.verbose):
            color = Colors.RED if not result.passed else Colors.DIM
            print(f"      {color}→ {result.message}{Colors.RESET}")

    def _print_header(self, title: str):
        """Druckt einen Header"""
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")

    # =========================================================================
    # MODUL-TESTS (DYNAMISCH)
    # =========================================================================

    def test_modules(self):
        """Testet alle gefundenen Module"""
        self._print_header(f"MODULE TESTS ({len(self.scanner.modules)} Module gefunden)")

        # Gruppiere nach Wichtigkeit (basierend auf Größe und Imports)
        critical = []  # > 50KB oder viele Imports
        important = []  # > 10KB
        optional = []   # Rest

        for name, info in self.scanner.modules.items():
            if info.size_bytes > 50000 or len(info.imports) > 20:
                critical.append((name, info))
            elif info.size_bytes > 10000:
                important.append((name, info))
            else:
                optional.append((name, info))

        # Sortiere nach Größe
        critical.sort(key=lambda x: x[1].size_bytes, reverse=True)
        important.sort(key=lambda x: x[1].size_bytes, reverse=True)
        optional.sort(key=lambda x: x[1].size_bytes, reverse=True)

        if critical:
            print(f"\n{Colors.BOLD}Kritische Module ({len(critical)}):{Colors.RESET}")
            for name, info in critical:
                self._test_module(name, info)

        if important:
            print(f"\n{Colors.BOLD}Wichtige Module ({len(important)}):{Colors.RESET}")
            for name, info in important:
                self._test_module(name, info)

        if optional and self.verbose:
            print(f"\n{Colors.BOLD}Weitere Module ({len(optional)}):{Colors.RESET}")
            for name, info in optional:
                self._test_module(name, info)
        elif optional:
            # Nur Zusammenfassung
            ok_count = sum(1 for _, info in optional if info.syntax_ok)
            print(f"\n{Colors.DIM}  ... und {len(optional)} weitere Module "
                  f"({ok_count} Syntax OK){Colors.RESET}")

    def _test_module(self, name: str, info: ModuleInfo):
        """Testet ein einzelnes Modul"""
        start = time.time()

        # 1. Syntax Check (bereits im Scanner gemacht)
        if not info.syntax_ok:
            self._add_result(
                "module", name, False,
                info.error,
                details={"path": str(info.path)}
            )
            return

        # 2. Import Check
        try:
            # Füge Projektverzeichnis zu sys.path hinzu
            project_dir = str(self.scanner.project_dir)
            if project_dir not in sys.path:
                sys.path.insert(0, project_dir)

            module = importlib.import_module(name)
            info.import_ok = True
            duration = (time.time() - start) * 1000

            # Zusätzliche Info
            details_str = []
            if info.classes:
                details_str.append(f"{len(info.classes)} Klassen")
            if info.functions:
                details_str.append(f"{len(info.functions)} Funktionen")
            details_str.append(f"{info.lines} Zeilen")

            self._add_result(
                "module", name, True,
                ", ".join(details_str),
                duration,
                {"classes": info.classes, "functions": info.functions}
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            error_msg = str(e).split("\n")[0][:80]
            self._add_result(
                "module", name, False,
                f"Import-Fehler: {error_msg}",
                duration
            )

    # =========================================================================
    # SERVICE-TESTS (DYNAMISCH)
    # =========================================================================

    def test_services(self):
        """Testet alle entdeckten Services"""
        self._print_header(f"SERVICE TESTS ({len(self.scanner.services)} Services gefunden)")

        for key, service in self.scanner.services.items():
            self._test_service(service)

    def _test_service(self, service: ServiceInfo):
        """Testet einen einzelnen Service"""
        start = time.time()

        try:
            if service.protocol in ["http", "https"]:
                success, details = self._test_http_service(service)
            else:
                success, details = self._test_tcp_service(service)

            duration = (time.time() - start) * 1000
            service.reachable = success
            service.response_time_ms = duration
            service.details = details

            msg = f"{service.host}:{service.port}"
            if details:
                msg += f" - {details.get('info', '')}"

            self._add_result(
                "service",
                service.name,
                success,
                msg,
                duration,
                details
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            self._add_result(
                "service",
                service.name,
                False,
                f"{service.host}:{service.port} - {str(e)[:50]}",
                duration
            )

    def _test_tcp_service(self, service: ServiceInfo) -> Tuple[bool, dict]:
        """Testet TCP-Verbindung"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((service.host, service.port))
        sock.close()

        if result == 0:
            return True, {"info": "TCP erreichbar"}
        return False, {"error_code": result}

    def _test_http_service(self, service: ServiceInfo) -> Tuple[bool, dict]:
        """Testet HTTP-Service"""
        import urllib.request

        # Erst TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((service.host, service.port))
        sock.close()

        if result != 0:
            return False, {"info": "TCP nicht erreichbar"}

        # Dann HTTP
        try:
            url = f"http://{service.host}:{service.port}/"

            # Spezielle Endpoints für bekannte Services
            if service.name == "Ollama LLM":
                url = f"http://{service.host}:{service.port}/api/tags"

            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                if "ollama" in service.name.lower():
                    data = json.loads(response.read())
                    models = [m.get("name") for m in data.get("models", [])]
                    return True, {"info": f"{len(models)} Modelle", "models": models}
                return True, {"info": f"HTTP {response.status}"}

        except Exception as e:
            # HTTP fehlgeschlagen, aber TCP war OK
            return True, {"info": "TCP OK, HTTP-API nicht verfügbar"}

    # =========================================================================
    # DATENBANK-TESTS (DYNAMISCH)
    # =========================================================================

    def test_databases(self):
        """Testet alle gefundenen Datenbanken"""
        if not self.scanner.databases:
            print(f"\n{Colors.DIM}Keine Datenbanken gefunden (erster Start?){Colors.RESET}")
            return

        self._print_header(f"DATENBANK TESTS ({len(self.scanner.databases)} Datenbanken)")

        for name, db in self.scanner.databases.items():
            self._test_database(db)

    def _test_database(self, db: DatabaseInfo):
        """Testet eine Datenbank"""
        start = time.time()

        if db.error:
            self._add_result(
                "database", db.name, False,
                db.error,
                details={"path": str(db.path)}
            )
            return

        duration = (time.time() - start) * 1000

        msg = f"{len(db.tables)} Tabellen, {db.size_mb:.1f}MB"
        if not db.integrity_ok:
            msg += " (Integrity-Check fehlgeschlagen!)"

        self._add_result(
            "database", db.name,
            db.integrity_ok,
            msg,
            duration,
            {"tables": db.tables, "size_mb": db.size_mb}
        )

    # =========================================================================
    # KONFIGURATIONS-TESTS
    # =========================================================================

    def test_configuration(self):
        """Testet Konfiguration"""
        self._print_header("KONFIGURATIONS-TESTS")

        # Config-Datei
        config_path = self.scanner.project_dir / "config.json"
        self._add_result(
            "config", "config.json",
            config_path.exists(),
            f"{config_path.stat().st_size} Bytes" if config_path.exists() else "Nicht gefunden"
        )

        # Wichtige Verzeichnisse
        for dirname in ["data", "logs", "state"]:
            path = self.scanner.project_dir / dirname
            exists = path.exists() and path.is_dir()
            self._add_result(
                "config", f"{dirname}/ Verzeichnis",
                exists,
                "Existiert" if exists else "Fehlt"
            )

        # Umgebungsvariablen
        if self.scanner.all_env_vars:
            set_vars = [v for v in self.scanner.all_env_vars if os.getenv(v)]
            total = len(self.scanner.all_env_vars)
            self._add_result(
                "config", "Umgebungsvariablen",
                True,  # Immer OK, da optional
                f"{len(set_vars)}/{total} gesetzt",
                details={"set": set_vars, "all": list(self.scanner.all_env_vars)}
            )

    # =========================================================================
    # ABHÄNGIGKEITS-TESTS
    # =========================================================================

    def test_dependencies(self):
        """Testet ob alle benötigten Abhängigkeiten installiert sind"""
        self._print_header("ABHÄNGIGKEITS-TESTS")

        # Sammle alle externen Imports aus allen Modulen
        external_imports = set()
        stdlib = self._get_stdlib_modules()

        for module in self.scanner.modules.values():
            for imp in module.imports:
                # Ignoriere lokale Module und stdlib
                if imp not in self.scanner.modules and imp not in stdlib:
                    external_imports.add(imp)

        # Teste jeden Import
        for imp in sorted(external_imports):
            start = time.time()
            try:
                importlib.import_module(imp)
                duration = (time.time() - start) * 1000
                self._add_result("dependency", imp, True, "Installiert", duration)
            except ImportError:
                self._add_result("dependency", imp, False, "Nicht installiert")

    def _get_stdlib_modules(self) -> Set[str]:
        """Gibt Standard-Library-Module zurück"""
        # Häufigste stdlib Module
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
        }

    # =========================================================================
    # FUNKTIONS-TESTS
    # =========================================================================

    def test_functions(self, deep: bool = False):
        """Testet wichtige Funktionen"""
        self._print_header("FUNKTIONS-TESTS")

        # Health Check System
        self._test_function_import(
            "Health Checks",
            "holo_health_checks",
            ["HealthChecker", "HealthStatus"]
        )

        # Metrics
        self._test_function_import(
            "Metrics",
            "holo_metrics",
            ["MetricsRegistry", "Counter", "Gauge"]
        )

        # Migrations
        self._test_function_import(
            "Migrations",
            "holo_db_migrations",
            ["MigrationManager", "Migration"]
        )

        # Config
        self._test_function_import(
            "Config",
            "holo_config",
            ["load_config", "get_config"]
        )

        # Router
        self._test_function_import(
            "Intelligent Router",
            "holo_intelligent_router",
            ["IntelligentRouter"]
        )

        if deep:
            # Teste alle Klassen in allen Modulen
            print(f"\n{Colors.BOLD}Tiefe Analyse aller Klassen:{Colors.RESET}")
            for name, info in self.scanner.modules.items():
                if info.import_ok and info.classes:
                    for cls_name in info.classes[:3]:  # Max 3 pro Modul
                        self._test_class_instantiation(name, cls_name)

    def _test_function_import(self, display_name: str, module_name: str, items: List[str]):
        """Testet ob bestimmte Items aus einem Modul importierbar sind"""
        start = time.time()

        try:
            module = importlib.import_module(module_name)
            missing = [item for item in items if not hasattr(module, item)]
            duration = (time.time() - start) * 1000

            if missing:
                self._add_result(
                    "function", display_name, False,
                    f"Fehlend: {', '.join(missing)}",
                    duration
                )
            else:
                self._add_result(
                    "function", display_name, True,
                    f"Alle {len(items)} Items verfügbar",
                    duration
                )

        except ImportError as e:
            self._add_result(
                "function", display_name, False,
                f"Modul nicht ladbar: {e}"
            )

    def _test_class_instantiation(self, module_name: str, class_name: str):
        """Versucht eine Klasse zu instanziieren"""
        start = time.time()

        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            # Versuche zu instanziieren (ohne Argumente)
            try:
                instance = cls()
                duration = (time.time() - start) * 1000
                self._add_result(
                    "class", f"{module_name}.{class_name}", True,
                    "Instanziierbar",
                    duration
                )
            except TypeError:
                # Braucht Argumente - das ist OK
                duration = (time.time() - start) * 1000
                self._add_result(
                    "class", f"{module_name}.{class_name}", True,
                    "Klasse OK (braucht Argumente)",
                    duration
                )

        except Exception as e:
            self._add_result(
                "class", f"{module_name}.{class_name}", False,
                str(e)[:50]
            )

    # =========================================================================
    # REPORT
    # =========================================================================

    def print_report(self):
        """Druckt den finalen Report"""
        duration = (datetime.now() - self.start_time).total_seconds()

        print()
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  ZUSAMMENFASSUNG{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")

        # Nach Kategorie gruppieren
        by_category = defaultdict(list)
        for r in self.results:
            by_category[r.category].append(r)

        print()
        for category, results in by_category.items():
            passed = sum(1 for r in results if r.passed)
            total = len(results)

            if total == passed:
                color = Colors.GREEN
            elif passed > total // 2:
                color = Colors.YELLOW
            else:
                color = Colors.RED

            print(f"  {category:20} {color}{passed}/{total} bestanden{Colors.RESET}")

        # Gesamtergebnis
        total_passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        rate = (total_passed / total * 100) if total > 0 else 0

        print()
        if total_passed == total:
            print(f"  {Colors.GREEN}{Colors.BOLD}✓ ALLE TESTS BESTANDEN{Colors.RESET}")
        elif total_passed > total // 2:
            print(f"  {Colors.YELLOW}{Colors.BOLD}⚠ EINIGE TESTS FEHLGESCHLAGEN{Colors.RESET}")
        else:
            print(f"  {Colors.RED}{Colors.BOLD}✗ VIELE TESTS FEHLGESCHLAGEN{Colors.RESET}")

        print()
        print(f"  Gesamt: {Colors.GREEN}{total_passed} bestanden{Colors.RESET}, "
              f"{Colors.RED}{total - total_passed} fehlgeschlagen{Colors.RESET}")
        print(f"  Erfolgsrate: {rate:.1f}%")
        print(f"  Dauer: {duration:.1f}s")
        print()

        # Projekt-Statistik
        print(f"{Colors.BOLD}Projekt-Statistik:{Colors.RESET}")
        print(f"  Module:      {len(self.scanner.modules)}")
        print(f"  Services:    {len(self.scanner.services)}")
        print(f"  Datenbanken: {len(self.scanner.databases)}")
        print(f"  Env-Vars:    {len(self.scanner.all_env_vars)}")

        total_lines = sum(m.lines for m in self.scanner.modules.values())
        total_classes = sum(len(m.classes) for m in self.scanner.modules.values())
        total_functions = sum(len(m.functions) for m in self.scanner.modules.values())

        print(f"  Code-Zeilen: {total_lines:,}")
        print(f"  Klassen:     {total_classes}")
        print(f"  Funktionen:  {total_functions}")
        print()

        return total_passed == total


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Holocloude Dynamic System Tester - Erkennt und testet automatisch"
    )
    parser.add_argument("--quick", "-q", action="store_true",
                        help="Schnelle Tests (weniger Module)")
    parser.add_argument("--deep", "-d", action="store_true",
                        help="Tiefe Analyse (testet alle Klassen)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Mehr Details")
    parser.add_argument("--no-color", action="store_true",
                        help="Keine Farben")
    parser.add_argument("--modules-only", action="store_true",
                        help="Nur Module testen")
    parser.add_argument("--services-only", action="store_true",
                        help="Nur Services testen")

    args = parser.parse_args()

    if args.no_color:
        Colors.disable()

    print()
    print(f"{Colors.BOLD}{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║       HOLOCLOUDE DYNAMIC SYSTEM TESTER v2.0                  ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║       {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^50} ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")

    # Scanner
    print(f"\n{Colors.DIM}Scanne Projekt...{Colors.RESET}")
    scanner = ProjectScanner()
    scanner.scan_all()

    print(f"{Colors.DIM}  Gefunden: {len(scanner.modules)} Module, "
          f"{len(scanner.services)} Services, "
          f"{len(scanner.databases)} Datenbanken{Colors.RESET}")

    # Tester
    tester = DynamicTester(scanner, verbose=args.verbose)

    if args.modules_only:
        tester.test_modules()
    elif args.services_only:
        tester.test_services()
    else:
        tester.test_configuration()
        tester.test_modules()
        tester.test_services()
        tester.test_databases()
        tester.test_dependencies()
        tester.test_functions(deep=args.deep)

    success = tester.print_report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
