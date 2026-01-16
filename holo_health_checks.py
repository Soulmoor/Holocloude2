"""
Holocloude Health Check System
===============================

Umfassendes Health-Check-System fuer Produktionsumgebungen.

Endpoints:
    /health/live     - Liveness Check (Prozess laeuft)
    /health/ready    - Readiness Check (Vollstaendig initialisiert)
    /health/full     - Vollstaendiger Health Report
    /health/deps     - Dependency Status

Features:
- Kubernetes-kompatible Health Checks
- Dependency-Monitoring (Ollama, MQTT, Home Assistant, NAS)
- Konfigurierbare Timeouts und Thresholds
- Metriken-Sammlung fuer Monitoring
- Thread-safe Singleton-Pattern

Verwendung:
    from holo_health_checks import HealthChecker, health_checker

    # Singleton verwenden
    status = health_checker.check_all()

    # Oder eigene Instanz
    hc = HealthChecker(config)
    hc.check_readiness()
"""

import os
import time
import json
import socket
import logging
import threading
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health Check Status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    """Ergebnis eines einzelnen Health Checks."""
    name: str
    status: HealthStatus
    message: str = ""
    response_time_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass
class HealthReport:
    """Vollstaendiger Health Report."""
    status: HealthStatus
    checks: List[CheckResult]
    uptime_seconds: float = 0.0
    version: str = "15.1"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "timestamp": self.timestamp,
            "checks": {c.name: c.to_dict() for c in self.checks}
        }


class HealthChecker:
    """
    Zentraler Health Checker fuer Holocloude.

    Prueft:
    - Liveness: Prozess reagiert
    - Readiness: Alle Komponenten initialisiert
    - Dependencies: Externe Services erreichbar
    """

    # Singleton
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config: Dict = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, config: Dict = None):
        if self._initialized:
            return

        self.config = config or {}
        self.start_time = datetime.now()
        self._ready = False
        self._ready_components: Dict[str, bool] = {}
        self._last_checks: Dict[str, CheckResult] = {}
        self._check_history: List[Dict] = []
        self._max_history = 100

        # Konfigurierbare Timeouts (in Sekunden)
        self.timeouts = {
            "ollama": self.config.get("health_timeout_ollama", 5),
            "mqtt": self.config.get("health_timeout_mqtt", 3),
            "home_assistant": self.config.get("health_timeout_ha", 5),
            "nas": self.config.get("health_timeout_nas", 3),
            "database": self.config.get("health_timeout_db", 2),
        }

        # Thresholds
        self.thresholds = {
            "memory_warning_mb": self.config.get("memory_warning_mb", 500),
            "memory_critical_mb": self.config.get("memory_critical_mb", 800),
            "disk_warning_percent": self.config.get("disk_warning_percent", 80),
            "disk_critical_percent": self.config.get("disk_critical_percent", 95),
        }

        self._initialized = True
        logger.info("HealthChecker initialisiert")

    @property
    def uptime(self) -> timedelta:
        """Gibt die Uptime zurueck."""
        return datetime.now() - self.start_time

    def mark_ready(self, component: str, ready: bool = True):
        """Markiert eine Komponente als ready/not ready."""
        self._ready_components[component] = ready
        logger.debug(f"Component {component} marked as {'ready' if ready else 'not ready'}")

    def is_ready(self) -> bool:
        """Prueft ob alle Komponenten ready sind."""
        required = {"brain", "database", "config"}
        ready_set = {k for k, v in self._ready_components.items() if v}
        return required.issubset(ready_set)

    # =========================================================================
    # LIVENESS CHECK
    # =========================================================================

    def check_liveness(self) -> CheckResult:
        """
        Liveness Check - Prozess laeuft und reagiert.

        Kubernetes: livenessProbe
        Wenn dieser Check fehlschlaegt, sollte der Container neu gestartet werden.
        """
        start = time.time()
        try:
            # Einfacher Check: Koennen wir Zeit messen?
            _ = datetime.now()

            # Memory Check
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
            except ImportError:
                memory_mb = 0

            response_time = (time.time() - start) * 1000

            return CheckResult(
                name="liveness",
                status=HealthStatus.HEALTHY,
                message="Process alive",
                response_time_ms=response_time,
                details={
                    "pid": os.getpid(),
                    "memory_mb": round(memory_mb, 2),
                    "uptime_seconds": self.uptime.total_seconds()
                }
            )

        except Exception as e:
            return CheckResult(
                name="liveness",
                status=HealthStatus.UNHEALTHY,
                message=f"Liveness check failed: {e}",
                response_time_ms=(time.time() - start) * 1000
            )

    # =========================================================================
    # READINESS CHECK
    # =========================================================================

    def check_readiness(self) -> CheckResult:
        """
        Readiness Check - Anwendung ist bereit, Traffic zu empfangen.

        Kubernetes: readinessProbe
        Wenn dieser Check fehlschlaegt, wird kein Traffic geroutet.
        """
        start = time.time()

        missing = []
        ready_components = []

        # Pruefe erforderliche Komponenten
        required = {
            "brain": "HoloPersona initialisiert",
            "database": "Datenbank-Verbindung",
            "config": "Konfiguration geladen"
        }

        for comp, desc in required.items():
            if self._ready_components.get(comp, False):
                ready_components.append(comp)
            else:
                missing.append(f"{comp} ({desc})")

        response_time = (time.time() - start) * 1000

        if missing:
            return CheckResult(
                name="readiness",
                status=HealthStatus.UNHEALTHY,
                message=f"Not ready: {', '.join(missing)}",
                response_time_ms=response_time,
                details={
                    "ready_components": ready_components,
                    "missing_components": missing
                }
            )

        return CheckResult(
            name="readiness",
            status=HealthStatus.HEALTHY,
            message="Application ready",
            response_time_ms=response_time,
            details={
                "ready_components": ready_components,
                "initialization_time_s": self.uptime.total_seconds()
            }
        )

    # =========================================================================
    # DEPENDENCY CHECKS
    # =========================================================================

    def _check_tcp_connection(self, host: str, port: int, timeout: float) -> tuple:
        """Prueft TCP-Verbindung zu einem Host."""
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            response_time = (time.time() - start) * 1000
            return result == 0, response_time
        except Exception as e:
            return False, (time.time() - start) * 1000

    def _check_http_endpoint(self, url: str, timeout: float) -> tuple:
        """Prueft HTTP-Endpoint."""
        start = time.time()
        try:
            import urllib.request
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
                response_time = (time.time() - start) * 1000
                return status == 200, response_time, status
        except Exception as e:
            return False, (time.time() - start) * 1000, str(e)

    def check_ollama(self) -> CheckResult:
        """Prueft Ollama LLM Service."""
        host = self.config.get("ollama", {}).get("host", "192.168.178.42")
        port = self.config.get("ollama", {}).get("port", 11434)
        timeout = self.timeouts["ollama"]

        # Erst TCP Check
        reachable, response_time = self._check_tcp_connection(host, port, timeout)

        if not reachable:
            return CheckResult(
                name="ollama",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to {host}:{port}",
                response_time_ms=response_time,
                details={"host": host, "port": port}
            )

        # Dann HTTP API Check
        url = f"http://{host}:{port}/api/tags"
        success, http_time, status = self._check_http_endpoint(url, timeout)

        if success:
            return CheckResult(
                name="ollama",
                status=HealthStatus.HEALTHY,
                message="Ollama API responding",
                response_time_ms=http_time,
                details={"host": host, "port": port, "api_status": status}
            )
        else:
            return CheckResult(
                name="ollama",
                status=HealthStatus.DEGRADED,
                message=f"Ollama reachable but API error: {status}",
                response_time_ms=http_time,
                details={"host": host, "port": port, "error": str(status)}
            )

    def check_mqtt(self) -> CheckResult:
        """Prueft MQTT Broker."""
        host = self.config.get("mqtt", {}).get("broker", "192.168.178.99")
        port = self.config.get("mqtt", {}).get("port", 1883)
        timeout = self.timeouts["mqtt"]

        reachable, response_time = self._check_tcp_connection(host, port, timeout)

        status = HealthStatus.HEALTHY if reachable else HealthStatus.UNHEALTHY
        message = "MQTT broker reachable" if reachable else f"Cannot connect to {host}:{port}"

        return CheckResult(
            name="mqtt",
            status=status,
            message=message,
            response_time_ms=response_time,
            details={"host": host, "port": port}
        )

    def check_home_assistant(self) -> CheckResult:
        """Prueft Home Assistant API."""
        ha_config = self.config.get("home_assistant", {})
        url = ha_config.get("url", "http://192.168.178.99:8123")
        timeout = self.timeouts["home_assistant"]

        # API Check
        api_url = f"{url}/api/"
        success, response_time, status = self._check_http_endpoint(api_url, timeout)

        if success:
            return CheckResult(
                name="home_assistant",
                status=HealthStatus.HEALTHY,
                message="Home Assistant API responding",
                response_time_ms=response_time,
                details={"url": url}
            )
        else:
            return CheckResult(
                name="home_assistant",
                status=HealthStatus.UNHEALTHY,
                message=f"Home Assistant not reachable: {status}",
                response_time_ms=response_time,
                details={"url": url, "error": str(status)}
            )

    def check_nas(self) -> CheckResult:
        """Prueft NAS-Verbindung (SSH)."""
        host = self.config.get("nas", {}).get("ip", "192.168.178.40")
        port = 22  # SSH
        timeout = self.timeouts["nas"]

        reachable, response_time = self._check_tcp_connection(host, port, timeout)

        status = HealthStatus.HEALTHY if reachable else HealthStatus.DEGRADED
        message = "NAS SSH reachable" if reachable else f"NAS not reachable at {host}"

        return CheckResult(
            name="nas",
            status=status,
            message=message,
            response_time_ms=response_time,
            details={"host": host, "port": port}
        )

    def check_database(self) -> CheckResult:
        """Prueft Datenbank-Verbindung."""
        start = time.time()
        data_dir = self.config.get("data_dir", "data")
        db_path = os.path.join(data_dir, "holo_brain_v12.db")

        try:
            if not os.path.exists(db_path):
                # Kein Fehler wenn DB noch nicht existiert
                return CheckResult(
                    name="database",
                    status=HealthStatus.DEGRADED,
                    message="Database file not found (may be first run)",
                    response_time_ms=(time.time() - start) * 1000,
                    details={"path": db_path, "exists": False}
                )

            # Verbindung testen
            conn = sqlite3.connect(db_path, timeout=self.timeouts["database"])
            cursor = conn.execute("SELECT 1")
            cursor.fetchone()
            conn.close()

            response_time = (time.time() - start) * 1000

            # Dateigroesse pruefen
            size_mb = os.path.getsize(db_path) / 1024 / 1024

            return CheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection OK",
                response_time_ms=response_time,
                details={
                    "path": db_path,
                    "size_mb": round(size_mb, 2)
                }
            )

        except Exception as e:
            return CheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {e}",
                response_time_ms=(time.time() - start) * 1000,
                details={"path": db_path, "error": str(e)}
            )

    def check_disk_space(self) -> CheckResult:
        """Prueft verfuegbaren Festplattenplatz."""
        start = time.time()
        data_dir = self.config.get("data_dir", "data")

        try:
            import shutil
            total, used, free = shutil.disk_usage(data_dir)

            used_percent = (used / total) * 100
            free_gb = free / (1024 ** 3)

            if used_percent >= self.thresholds["disk_critical_percent"]:
                status = HealthStatus.UNHEALTHY
                message = f"Critical: {used_percent:.1f}% disk used"
            elif used_percent >= self.thresholds["disk_warning_percent"]:
                status = HealthStatus.DEGRADED
                message = f"Warning: {used_percent:.1f}% disk used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk OK: {free_gb:.1f}GB free"

            return CheckResult(
                name="disk_space",
                status=status,
                message=message,
                response_time_ms=(time.time() - start) * 1000,
                details={
                    "total_gb": round(total / (1024 ** 3), 2),
                    "used_gb": round(used / (1024 ** 3), 2),
                    "free_gb": round(free_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
            )

        except Exception as e:
            return CheckResult(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check disk: {e}",
                response_time_ms=(time.time() - start) * 1000
            )

    def check_memory(self) -> CheckResult:
        """Prueft Speicherverbrauch."""
        start = time.time()

        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_percent = process.memory_percent()

            if memory_mb >= self.thresholds["memory_critical_mb"]:
                status = HealthStatus.UNHEALTHY
                message = f"Critical: {memory_mb:.0f}MB RAM used"
            elif memory_mb >= self.thresholds["memory_warning_mb"]:
                status = HealthStatus.DEGRADED
                message = f"Warning: {memory_mb:.0f}MB RAM used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory OK: {memory_mb:.0f}MB"

            return CheckResult(
                name="memory",
                status=status,
                message=message,
                response_time_ms=(time.time() - start) * 1000,
                details={
                    "rss_mb": round(memory_mb, 2),
                    "percent": round(memory_percent, 2)
                }
            )

        except ImportError:
            return CheckResult(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message="psutil not available",
                response_time_ms=(time.time() - start) * 1000
            )

    # =========================================================================
    # AGGREGIERTE CHECKS
    # =========================================================================

    def check_dependencies(self) -> List[CheckResult]:
        """Prueft alle externen Abhaengigkeiten."""
        checks = [
            self.check_ollama(),
            self.check_mqtt(),
            self.check_home_assistant(),
            self.check_nas(),
            self.check_database(),
        ]

        # Cache results
        for check in checks:
            self._last_checks[check.name] = check

        return checks

    def check_resources(self) -> List[CheckResult]:
        """Prueft System-Ressourcen."""
        return [
            self.check_disk_space(),
            self.check_memory(),
        ]

    def check_all(self) -> HealthReport:
        """Fuehrt alle Health Checks durch und gibt Report zurueck."""
        all_checks = [
            self.check_liveness(),
            self.check_readiness(),
            *self.check_dependencies(),
            *self.check_resources(),
        ]

        # Bestimme Gesamt-Status
        statuses = [c.status for c in all_checks]

        if HealthStatus.UNHEALTHY in statuses:
            overall = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall = HealthStatus.DEGRADED
        elif HealthStatus.UNKNOWN in statuses:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        report = HealthReport(
            status=overall,
            checks=all_checks,
            uptime_seconds=self.uptime.total_seconds()
        )

        # Historie speichern
        self._add_to_history(report)

        return report

    def _add_to_history(self, report: HealthReport):
        """Fuegt Report zur Historie hinzu."""
        entry = {
            "timestamp": report.timestamp,
            "status": report.status.value,
            "checks": {c.name: c.status.value for c in report.checks}
        }
        self._check_history.append(entry)

        # Alte Eintraege entfernen
        if len(self._check_history) > self._max_history:
            self._check_history = self._check_history[-self._max_history:]

    def get_history(self) -> List[Dict]:
        """Gibt die Check-Historie zurueck."""
        return self._check_history.copy()


# =============================================================================
# HTTP HANDLER INTEGRATION
# =============================================================================

def create_health_endpoints(health_checker: HealthChecker) -> Dict[str, Callable]:
    """
    Erstellt HTTP-Endpoint-Handler fuer Health Checks.

    Verwendung mit http.server:
        endpoints = create_health_endpoints(health_checker)

        if path == "/health/live":
            return endpoints["live"]()
    """

    def live_handler() -> tuple:
        """GET /health/live"""
        result = health_checker.check_liveness()
        status_code = 200 if result.status == HealthStatus.HEALTHY else 503
        return status_code, result.to_dict()

    def ready_handler() -> tuple:
        """GET /health/ready"""
        result = health_checker.check_readiness()
        status_code = 200 if result.status == HealthStatus.HEALTHY else 503
        return status_code, result.to_dict()

    def full_handler() -> tuple:
        """GET /health/full"""
        report = health_checker.check_all()
        status_code = 200 if report.status == HealthStatus.HEALTHY else 503
        return status_code, report.to_dict()

    def deps_handler() -> tuple:
        """GET /health/deps"""
        checks = health_checker.check_dependencies()
        all_healthy = all(c.status == HealthStatus.HEALTHY for c in checks)
        status_code = 200 if all_healthy else 503
        return status_code, {c.name: c.to_dict() for c in checks}

    return {
        "live": live_handler,
        "ready": ready_handler,
        "full": full_handler,
        "deps": deps_handler,
    }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Globale Instanz (wird bei erstem Import erstellt)
health_checker: Optional[HealthChecker] = None


def init_health_checker(config: Dict = None) -> HealthChecker:
    """Initialisiert den globalen Health Checker."""
    global health_checker
    health_checker = HealthChecker(config)
    return health_checker


def get_health_checker() -> HealthChecker:
    """Gibt den globalen Health Checker zurueck."""
    global health_checker
    if health_checker is None:
        health_checker = HealthChecker()
    return health_checker


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(description="Holocloude Health Check")
    parser.add_argument("check", nargs="?", default="all",
                        choices=["all", "live", "ready", "deps", "resources"],
                        help="Welcher Check ausgefuehrt werden soll")
    parser.add_argument("--json", action="store_true",
                        help="Output als JSON")

    args = parser.parse_args()

    # Lade Config wenn vorhanden
    config = {}
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.load(f)

    hc = HealthChecker(config)

    # Markiere Basis-Komponenten als ready fuer Test
    hc.mark_ready("config", True)

    if args.check == "all":
        report = hc.check_all()
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"HEALTH STATUS: {report.status.value.upper()}")
            print(f"Uptime: {report.uptime_seconds:.0f}s")
            print(f"{'='*50}\n")
            for check in report.checks:
                icon = "✓" if check.status == HealthStatus.HEALTHY else "✗" if check.status == HealthStatus.UNHEALTHY else "⚠"
                print(f"  {icon} {check.name}: {check.message} ({check.response_time_ms:.1f}ms)")
            print()

    elif args.check == "live":
        result = hc.check_liveness()
        print(json.dumps(result.to_dict(), indent=2) if args.json else f"{result.status.value}: {result.message}")

    elif args.check == "ready":
        result = hc.check_readiness()
        print(json.dumps(result.to_dict(), indent=2) if args.json else f"{result.status.value}: {result.message}")

    elif args.check == "deps":
        results = hc.check_dependencies()
        if args.json:
            print(json.dumps({r.name: r.to_dict() for r in results}, indent=2))
        else:
            for r in results:
                icon = "✓" if r.status == HealthStatus.HEALTHY else "✗"
                print(f"  {icon} {r.name}: {r.message}")

    elif args.check == "resources":
        results = hc.check_resources()
        if args.json:
            print(json.dumps({r.name: r.to_dict() for r in results}, indent=2))
        else:
            for r in results:
                icon = "✓" if r.status == HealthStatus.HEALTHY else "⚠"
                print(f"  {icon} {r.name}: {r.message}")
