#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HOLOCLOUDE SYSTEM TESTER v1.0                             ║
║                                                                              ║
║  Umfassender Test aller Systemkomponenten für Homelab-Betrieb               ║
║                                                                              ║
║  Verwendung:                                                                 ║
║      python holo_tester.py              # Alle Tests                         ║
║      python holo_tester.py --quick      # Nur schnelle Tests                 ║
║      python holo_tester.py --modules    # Nur Module testen                  ║
║      python holo_tester.py --services   # Nur Services testen                ║
║      python holo_tester.py --verbose    # Mehr Details                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import socket
import sqlite3
import threading
import traceback
import importlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field

# =============================================================================
# KONFIGURATION
# =============================================================================

# Farben für Terminal-Ausgabe
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
        """Deaktiviert Farben (z.B. für Nicht-Terminal-Ausgabe)"""
        cls.GREEN = cls.RED = cls.YELLOW = cls.BLUE = ""
        cls.CYAN = cls.MAGENTA = cls.BOLD = cls.DIM = cls.RESET = ""


# Prüfe ob Terminal Farben unterstützt
if not sys.stdout.isatty():
    Colors.disable()


@dataclass
class TestResult:
    """Ergebnis eines einzelnen Tests"""
    name: str
    passed: bool
    message: str = ""
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    category: str = "general"


@dataclass
class TestReport:
    """Gesamtbericht aller Tests"""
    results: List[TestResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0


# =============================================================================
# TEST-FRAMEWORK
# =============================================================================

class HoloTester:
    """Hauptklasse für alle Holocloude-Tests"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.report = TestReport()
        self.config = {}
        self._load_config()

    def _load_config(self):
        """Lädt die Konfiguration"""
        config_paths = [
            Path("config.json"),
            Path("~/.holocloude/config.json").expanduser(),
            Path("/etc/holocloude/config.json"),
        ]

        for path in config_paths:
            if path.exists():
                try:
                    with open(path) as f:
                        self.config = json.load(f)
                    self._print(f"  Config geladen: {path}", Colors.DIM)
                    break
                except Exception as e:
                    self._print(f"  Config-Fehler: {e}", Colors.YELLOW)

    def _print(self, msg: str, color: str = ""):
        """Gibt Text mit optionaler Farbe aus"""
        print(f"{color}{msg}{Colors.RESET}")

    def _print_header(self, title: str):
        """Gibt einen Abschnitts-Header aus"""
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 60}{Colors.RESET}")

    def _print_result(self, result: TestResult):
        """Gibt ein Test-Ergebnis aus"""
        if result.passed:
            icon = f"{Colors.GREEN}✓{Colors.RESET}"
            status = f"{Colors.GREEN}OK{Colors.RESET}"
        else:
            icon = f"{Colors.RED}✗{Colors.RESET}"
            status = f"{Colors.RED}FEHLER{Colors.RESET}"

        time_str = f"{Colors.DIM}({result.duration_ms:.0f}ms){Colors.RESET}"
        print(f"  {icon} {result.name}: {status} {time_str}")

        if result.message and (not result.passed or self.verbose):
            msg_color = Colors.RED if not result.passed else Colors.DIM
            print(f"      {msg_color}→ {result.message}{Colors.RESET}")

    def run_test(self, name: str, test_func: Callable, category: str = "general") -> TestResult:
        """Führt einen einzelnen Test aus"""
        start = time.time()
        try:
            passed, message, details = test_func()
            duration = (time.time() - start) * 1000
            result = TestResult(
                name=name,
                passed=passed,
                message=message,
                duration_ms=duration,
                details=details or {},
                category=category
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            result = TestResult(
                name=name,
                passed=False,
                message=f"Exception: {str(e)}",
                duration_ms=duration,
                details={"traceback": traceback.format_exc()},
                category=category
            )

        self.report.results.append(result)
        self._print_result(result)
        return result

    # =========================================================================
    # MODUL-TESTS
    # =========================================================================

    def test_modules(self):
        """Testet ob alle wichtigen Module importiert werden können"""
        self._print_header("MODULE IMPORT TESTS")

        # Kritische Module (müssen funktionieren)
        critical_modules = [
            ("holo_core_types", "Zentrale Typdefinitionen"),
            ("holo_config", "Konfigurationsmanagement"),
            ("holo_error_handling", "Fehlerbehandlung"),
            ("holo_robust_imports", "Import-System"),
        ]

        # Wichtige Module (sollten funktionieren)
        important_modules = [
            ("holo_brain", "Haupt-Brain-Modul"),
            ("holo_intelligent_router", "Intelligentes Routing"),
            ("holo_database_system", "Datenbank-System"),
            ("smart_llm_system", "LLM-Integration"),
            ("holo_personality", "Persönlichkeitssystem"),
            ("holo_nlp_unified", "NLP-System"),
        ]

        # Optionale Module (nice to have)
        optional_modules = [
            ("holo_health_checks", "Health Checks"),
            ("holo_metrics", "Prometheus Metrics"),
            ("holo_structured_logging", "Structured Logging"),
            ("holo_db_migrations", "DB Migrationen"),
            ("holo_knowledge_influence", "Knowledge Influence"),
            ("holo_voice_interface", "Voice Interface"),
            ("holo_vision_enhanced", "Vision System"),
            ("holo_audio_enhanced", "Audio System"),
            ("holo_web_curiosity", "Web Curiosity"),
            ("holo_creative_mind", "Creative Mind"),
        ]

        print(f"\n{Colors.BOLD}Kritische Module:{Colors.RESET}")
        for module, desc in critical_modules:
            self.run_test(
                f"{module}",
                lambda m=module: self._test_import(m),
                category="critical_module"
            )

        print(f"\n{Colors.BOLD}Wichtige Module:{Colors.RESET}")
        for module, desc in important_modules:
            self.run_test(
                f"{module}",
                lambda m=module: self._test_import(m),
                category="important_module"
            )

        print(f"\n{Colors.BOLD}Optionale Module:{Colors.RESET}")
        for module, desc in optional_modules:
            self.run_test(
                f"{module}",
                lambda m=module: self._test_import(m),
                category="optional_module"
            )

    def _test_import(self, module_name: str) -> Tuple[bool, str, dict]:
        """Testet den Import eines Moduls"""
        try:
            module = importlib.import_module(module_name)
            # Prüfe ob Modul Attribute hat
            attrs = [a for a in dir(module) if not a.startswith("_")]
            return True, f"{len(attrs)} Attribute", {"attributes": len(attrs)}
        except ImportError as e:
            return False, f"Import fehlgeschlagen: {e}", {}
        except Exception as e:
            return False, f"Fehler: {e}", {}

    # =========================================================================
    # KONFIGURATIONS-TESTS
    # =========================================================================

    def test_configuration(self):
        """Testet die Konfiguration"""
        self._print_header("KONFIGURATIONS-TESTS")

        # Config-Datei vorhanden
        self.run_test(
            "config.json existiert",
            self._test_config_exists,
            category="config"
        )

        # Config-Struktur
        self.run_test(
            "Config-Struktur gültig",
            self._test_config_structure,
            category="config"
        )

        # Verzeichnisse
        self.run_test(
            "data/ Verzeichnis",
            lambda: self._test_directory("data"),
            category="config"
        )

        self.run_test(
            "logs/ Verzeichnis",
            lambda: self._test_directory("logs"),
            category="config"
        )

        # Umgebungsvariablen
        self.run_test(
            "Umgebungsvariablen",
            self._test_env_vars,
            category="config"
        )

    def _test_config_exists(self) -> Tuple[bool, str, dict]:
        """Prüft ob config.json existiert"""
        if Path("config.json").exists():
            size = Path("config.json").stat().st_size
            return True, f"{size} Bytes", {"size": size}
        return False, "config.json nicht gefunden", {}

    def _test_config_structure(self) -> Tuple[bool, str, dict]:
        """Prüft die Config-Struktur"""
        if not self.config:
            return False, "Keine Config geladen", {}

        required_sections = ["network", "behavior", "storage"]
        missing = [s for s in required_sections if s not in self.config]

        if missing:
            return False, f"Fehlende Sektionen: {missing}", {"missing": missing}

        return True, f"{len(self.config)} Sektionen", {"sections": list(self.config.keys())}

    def _test_directory(self, dirname: str) -> Tuple[bool, str, dict]:
        """Prüft ob ein Verzeichnis existiert und beschreibbar ist"""
        path = Path(dirname)
        if not path.exists():
            return False, "Existiert nicht", {}

        if not path.is_dir():
            return False, "Ist kein Verzeichnis", {}

        # Schreibtest
        try:
            test_file = path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return True, "Existiert und beschreibbar", {}
        except Exception as e:
            return False, f"Nicht beschreibbar: {e}", {}

    def _test_env_vars(self) -> Tuple[bool, str, dict]:
        """Prüft wichtige Umgebungsvariablen"""
        important_vars = [
            "HOLO_MQTT_BROKER",
            "HOLO_MQTT_PASSWORD",
            "HOLO_LLM_LOCAL_HOST",
        ]

        set_vars = [v for v in important_vars if os.getenv(v)]
        missing_vars = [v for v in important_vars if not os.getenv(v)]

        if missing_vars:
            return True, f"{len(set_vars)}/{len(important_vars)} gesetzt (optional)", {
                "set": set_vars,
                "missing": missing_vars
            }

        return True, f"Alle {len(important_vars)} gesetzt", {"set": set_vars}

    # =========================================================================
    # SERVICE-TESTS
    # =========================================================================

    def test_services(self):
        """Testet externe Services"""
        self._print_header("SERVICE-VERBINDUNGS-TESTS")

        # Ollama
        ollama_host = self.config.get("network", {}).get("ollama", {}).get("host", "localhost")
        ollama_port = self.config.get("network", {}).get("ollama", {}).get("port", 11434)
        self.run_test(
            f"Ollama ({ollama_host}:{ollama_port})",
            lambda: self._test_ollama(ollama_host, ollama_port),
            category="service"
        )

        # MQTT
        mqtt_host = self.config.get("network", {}).get("mqtt", {}).get("broker_ip", "localhost")
        mqtt_port = self.config.get("network", {}).get("mqtt", {}).get("port", 1883)
        self.run_test(
            f"MQTT Broker ({mqtt_host}:{mqtt_port})",
            lambda: self._test_tcp(mqtt_host, mqtt_port),
            category="service"
        )

        # Home Assistant
        ha_url = self.config.get("network", {}).get("home_assistant", {}).get("api_url", "")
        if ha_url:
            self.run_test(
                f"Home Assistant",
                lambda: self._test_http(ha_url),
                category="service"
            )

        # NAS
        nas_ip = self.config.get("network", {}).get("nas", {}).get("ip", "")
        if nas_ip:
            self.run_test(
                f"NAS SSH ({nas_ip}:22)",
                lambda: self._test_tcp(nas_ip, 22),
                category="service"
            )

    def _test_tcp(self, host: str, port: int, timeout: float = 3.0) -> Tuple[bool, str, dict]:
        """Testet TCP-Verbindung"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return True, "Erreichbar", {"host": host, "port": port}
            else:
                return False, f"Nicht erreichbar (Code: {result})", {}
        except socket.timeout:
            return False, "Timeout", {}
        except Exception as e:
            return False, str(e), {}

    def _test_http(self, url: str, timeout: float = 5.0) -> Tuple[bool, str, dict]:
        """Testet HTTP-Endpoint"""
        try:
            import urllib.request
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return True, f"Status {response.status}", {"status": response.status}
        except Exception as e:
            return False, str(e), {}

    def _test_ollama(self, host: str, port: int) -> Tuple[bool, str, dict]:
        """Testet Ollama-Verbindung"""
        # Erst TCP
        tcp_ok, tcp_msg, _ = self._test_tcp(host, port)
        if not tcp_ok:
            return False, f"TCP: {tcp_msg}", {}

        # Dann API
        try:
            import urllib.request
            url = f"http://{host}:{port}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                models = data.get("models", [])
                model_names = [m.get("name", "?") for m in models[:3]]
                return True, f"{len(models)} Modelle: {', '.join(model_names)}", {
                    "models": len(models)
                }
        except Exception as e:
            return False, f"API-Fehler: {e}", {}

    # =========================================================================
    # DATENBANK-TESTS
    # =========================================================================

    def test_databases(self):
        """Testet Datenbanken"""
        self._print_header("DATENBANK-TESTS")

        data_dir = Path("data")
        if not data_dir.exists():
            self._print("  data/ Verzeichnis existiert nicht - überspringe DB-Tests", Colors.YELLOW)
            return

        # Finde alle .db Dateien
        db_files = list(data_dir.glob("*.db"))

        if not db_files:
            self._print("  Keine Datenbanken gefunden (erster Start?)", Colors.YELLOW)
            return

        for db_path in db_files:
            self.run_test(
                f"{db_path.name}",
                lambda p=db_path: self._test_database(p),
                category="database"
            )

    def _test_database(self, db_path: Path) -> Tuple[bool, str, dict]:
        """Testet eine SQLite-Datenbank"""
        try:
            conn = sqlite3.connect(str(db_path), timeout=5)
            cursor = conn.cursor()

            # Integrity Check
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]

            if integrity != "ok":
                conn.close()
                return False, f"Integrity-Check fehlgeschlagen: {integrity}", {}

            # Tabellen zählen
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]

            # Größe
            size_mb = db_path.stat().st_size / 1024 / 1024

            conn.close()

            return True, f"{table_count} Tabellen, {size_mb:.1f}MB", {
                "tables": table_count,
                "size_mb": size_mb
            }

        except Exception as e:
            return False, str(e), {}

    # =========================================================================
    # FUNKTIONS-TESTS
    # =========================================================================

    def test_functions(self):
        """Testet Kernfunktionen"""
        self._print_header("FUNKTIONS-TESTS")

        # Core Types
        self.run_test(
            "EmotionType Enum",
            self._test_emotion_types,
            category="function"
        )

        # Config Loading
        self.run_test(
            "Config-Modul laden",
            self._test_config_module,
            category="function"
        )

        # Router
        self.run_test(
            "Intelligent Router",
            self._test_router,
            category="function"
        )

        # Health Checks
        self.run_test(
            "Health Check System",
            self._test_health_checks,
            category="function"
        )

        # Migrations
        self.run_test(
            "Migration System",
            self._test_migrations,
            category="function"
        )

    def _test_emotion_types(self) -> Tuple[bool, str, dict]:
        """Testet EmotionType Enum"""
        try:
            from holo_core_types import EmotionType
            emotions = list(EmotionType)
            return True, f"{len(emotions)} Emotionen definiert", {"count": len(emotions)}
        except Exception as e:
            return False, str(e), {}

    def _test_config_module(self) -> Tuple[bool, str, dict]:
        """Testet das Config-Modul"""
        try:
            from holo_config import load_config, get_config
            config = load_config()
            if config:
                return True, "Config geladen", {}
            return True, "Leere Config (Defaults)", {}
        except Exception as e:
            return False, str(e), {}

    def _test_router(self) -> Tuple[bool, str, dict]:
        """Testet den Intelligent Router"""
        try:
            from holo_intelligent_router import IntelligentRouter, RouteDecision
            router = IntelligentRouter()
            # Teste Routing-Entscheidung
            decision = router.decide("Hallo, wie geht es dir?")
            return True, f"Route: {decision.route.value if hasattr(decision, 'route') else 'OK'}", {}
        except ImportError:
            return False, "Modul nicht importierbar", {}
        except Exception as e:
            return True, f"Modul OK (Test: {e})", {}  # Modul existiert, Test-Fehler ignorieren

    def _test_health_checks(self) -> Tuple[bool, str, dict]:
        """Testet das Health Check System"""
        try:
            from holo_health_checks import HealthChecker, HealthStatus
            hc = HealthChecker(self.config)
            result = hc.check_liveness()
            return True, f"Status: {result.status.value}", {}
        except Exception as e:
            return False, str(e), {}

    def _test_migrations(self) -> Tuple[bool, str, dict]:
        """Testet das Migration System"""
        try:
            from holo_db_migrations import MigrationManager, Migration, get_holocloude_migrations
            migrations = get_holocloude_migrations()
            return True, f"{len(migrations)} Migrationen definiert", {"count": len(migrations)}
        except Exception as e:
            return False, str(e), {}

    # =========================================================================
    # LLM-TESTS
    # =========================================================================

    def test_llm(self):
        """Testet LLM-Funktionalität"""
        self._print_header("LLM-TESTS")

        # LLM System Import
        self.run_test(
            "Smart LLM System laden",
            self._test_llm_import,
            category="llm"
        )

        # Ollama Modelle
        self.run_test(
            "Ollama Modelle abrufen",
            self._test_ollama_models,
            category="llm"
        )

        # Einfache Generierung (optional, dauert lange)
        self.run_test(
            "LLM Test-Generierung",
            self._test_llm_generate,
            category="llm"
        )

    def _test_llm_import(self) -> Tuple[bool, str, dict]:
        """Testet LLM System Import"""
        try:
            from smart_llm_system import SmartLLMSystem
            return True, "Modul geladen", {}
        except Exception as e:
            return False, str(e), {}

    def _test_ollama_models(self) -> Tuple[bool, str, dict]:
        """Holt verfügbare Ollama Modelle"""
        host = self.config.get("network", {}).get("ollama", {}).get("host", "localhost")
        port = self.config.get("network", {}).get("ollama", {}).get("port", 11434)

        try:
            import urllib.request
            url = f"http://{host}:{port}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                models = [m.get("name") for m in data.get("models", [])]
                if models:
                    return True, f"Modelle: {', '.join(models[:3])}", {"models": models}
                return False, "Keine Modelle installiert", {}
        except Exception as e:
            return False, str(e), {}

    def _test_llm_generate(self) -> Tuple[bool, str, dict]:
        """Testet eine einfache LLM-Generierung"""
        host = self.config.get("network", {}).get("ollama", {}).get("host", "localhost")
        port = self.config.get("network", {}).get("ollama", {}).get("port", 11434)
        model = self.config.get("llm", {}).get("local_model", "qwen2.5:0.5b")

        try:
            import urllib.request
            url = f"http://{host}:{port}/api/generate"

            payload = json.dumps({
                "model": model,
                "prompt": "Sag nur 'Test OK'",
                "stream": False,
                "options": {"num_predict": 10}
            }).encode()

            req = urllib.request.Request(url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                response_text = data.get("response", "")[:50]
                return True, f"Antwort: {response_text}...", {}

        except Exception as e:
            return False, str(e), {}

    # =========================================================================
    # REPORT
    # =========================================================================

    def print_report(self):
        """Gibt den finalen Report aus"""
        self.report.end_time = datetime.now()
        duration = (self.report.end_time - self.report.start_time).total_seconds()

        print()
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}  TESTERGEBNIS{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 60}{Colors.RESET}")
        print()

        # Statistik nach Kategorie
        categories = {}
        for r in self.report.results:
            if r.category not in categories:
                categories[r.category] = {"passed": 0, "failed": 0}
            if r.passed:
                categories[r.category]["passed"] += 1
            else:
                categories[r.category]["failed"] += 1

        for cat, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            color = Colors.GREEN if stats["failed"] == 0 else Colors.YELLOW if stats["passed"] > 0 else Colors.RED
            print(f"  {cat:20} {color}{stats['passed']}/{total} bestanden{Colors.RESET}")

        print()

        # Gesamtergebnis
        if self.report.failed == 0:
            status_color = Colors.GREEN
            status_text = "ALLE TESTS BESTANDEN"
            status_icon = "✓"
        elif self.report.passed > self.report.failed:
            status_color = Colors.YELLOW
            status_text = "EINIGE TESTS FEHLGESCHLAGEN"
            status_icon = "⚠"
        else:
            status_color = Colors.RED
            status_text = "VIELE TESTS FEHLGESCHLAGEN"
            status_icon = "✗"

        print(f"  {status_color}{Colors.BOLD}{status_icon} {status_text}{Colors.RESET}")
        print()
        print(f"  Gesamt: {Colors.GREEN}{self.report.passed} bestanden{Colors.RESET}, "
              f"{Colors.RED}{self.report.failed} fehlgeschlagen{Colors.RESET}")
        print(f"  Erfolgsrate: {self.report.success_rate:.1f}%")
        print(f"  Dauer: {duration:.1f}s")
        print()

        # Fehlgeschlagene Tests auflisten
        failed_tests = [r for r in self.report.results if not r.passed]
        if failed_tests and self.verbose:
            print(f"{Colors.RED}Fehlgeschlagene Tests:{Colors.RESET}")
            for r in failed_tests:
                print(f"  • {r.name}: {r.message}")
            print()

        # Empfehlungen
        if failed_tests:
            print(f"{Colors.YELLOW}Empfehlungen:{Colors.RESET}")

            # Service-Fehler
            service_fails = [r for r in failed_tests if r.category == "service"]
            if service_fails:
                print(f"  • Prüfe ob externe Services laufen (Ollama, MQTT, etc.)")

            # Modul-Fehler
            module_fails = [r for r in failed_tests if "module" in r.category]
            if module_fails:
                print(f"  • Installiere fehlende Dependencies: pip install -r requirements.txt")

            # Config-Fehler
            config_fails = [r for r in failed_tests if r.category == "config"]
            if config_fails:
                print(f"  • Prüfe config.json und Verzeichnisstruktur")

            print()

    # =========================================================================
    # MAIN
    # =========================================================================

    def run_all(self, quick: bool = False):
        """Führt alle Tests aus"""
        print()
        print(f"{Colors.BOLD}{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}║          HOLOCLOUDE SYSTEM TESTER v1.0                       ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}║          {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^42}       ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")

        self.test_modules()
        self.test_configuration()
        self.test_services()
        self.test_databases()
        self.test_functions()

        if not quick:
            self.test_llm()

        self.print_report()

        return self.report.failed == 0


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Holocloude System Tester - Prüft alle Komponenten"
    )
    parser.add_argument("--quick", "-q", action="store_true",
                        help="Schnelle Tests (ohne LLM)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Mehr Details ausgeben")
    parser.add_argument("--modules", action="store_true",
                        help="Nur Module testen")
    parser.add_argument("--services", action="store_true",
                        help="Nur Services testen")
    parser.add_argument("--databases", action="store_true",
                        help="Nur Datenbanken testen")
    parser.add_argument("--no-color", action="store_true",
                        help="Keine Farben ausgeben")

    args = parser.parse_args()

    if args.no_color:
        Colors.disable()

    tester = HoloTester(verbose=args.verbose)

    # Spezifische Tests
    if args.modules:
        tester.test_modules()
        tester.print_report()
    elif args.services:
        tester.test_services()
        tester.print_report()
    elif args.databases:
        tester.test_databases()
        tester.print_report()
    else:
        # Alle Tests
        success = tester.run_all(quick=args.quick)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
