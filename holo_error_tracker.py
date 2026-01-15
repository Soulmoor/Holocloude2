"""
Holocloude Error Tracking System
================================

Zentrales Error-Tracking fuer alle Module.
Sammelt Fehler und stellt sie fuer das Dashboard bereit.

Features:
- Fehler werden abgefangen aber geloggt
- Kategorisierung nach Modul und Schweregrad
- Statistiken ueber Fehleraufkommen
- Export fuer Dashboard-Anzeige
"""

import logging
import threading
import traceback
import json
import os
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Schweregrad von Fehlern."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TrackedError:
    """Ein getrackteter Fehler."""
    timestamp: str
    module: str
    function: str
    error_type: str
    message: str
    severity: str
    traceback: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    count: int = 1
    last_occurrence: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class HoloErrorTracker:
    """
    Zentraler Error-Tracker fuer Holocloude.

    Verwendung:
        tracker = HoloErrorTracker.get_instance()

        # In einem try/except Block:
        try:
            # code
        except Exception as e:
            tracker.track_error(e, "module_name", "function_name")
            # Optional: weitermachen statt crashen
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, max_errors: int = 1000, persist_path: str = None):
        self.max_errors = max_errors
        self.persist_path = persist_path or "data/error_log.json"

        # Fehler-Speicher
        self._errors: deque = deque(maxlen=max_errors)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._error_by_module: Dict[str, List[TrackedError]] = defaultdict(list)

        # Statistiken
        self._stats = {
            "total_errors": 0,
            "errors_by_severity": defaultdict(int),
            "errors_by_module": defaultdict(int),
            "errors_last_hour": 0,
            "errors_last_24h": 0,
            "most_common_errors": [],
            "last_reset": datetime.now().isoformat()
        }

        # Lock fuer Thread-Safety
        self._lock = threading.Lock()

        # Callbacks fuer Echtzeit-Benachrichtigung
        self._callbacks: List[Callable] = []

        # Lade persistierte Fehler
        self._load_persisted_errors()

        logger.info("HoloErrorTracker initialisiert")

    @classmethod
    def get_instance(cls) -> 'HoloErrorTracker':
        """Singleton-Pattern fuer globalen Zugriff."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def track_error(
        self,
        error: Exception,
        module: str = "unknown",
        function: str = "unknown",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Dict[str, Any] = None,
        log_traceback: bool = True
    ) -> TrackedError:
        """
        Trackt einen Fehler.

        Args:
            error: Die Exception
            module: Name des Moduls wo der Fehler auftrat
            function: Name der Funktion
            severity: Schweregrad
            context: Zusaetzlicher Kontext
            log_traceback: Ob Traceback gespeichert werden soll

        Returns:
            TrackedError Objekt
        """
        with self._lock:
            now = datetime.now()

            # Traceback extrahieren
            tb = ""
            if log_traceback:
                tb = traceback.format_exc()

            # Error-Key fuer Deduplizierung
            error_key = f"{module}:{function}:{type(error).__name__}:{str(error)[:100]}"

            # Pruefen ob aehnlicher Fehler bereits existiert
            existing = self._find_similar_error(error_key)

            if existing:
                # Zaehler erhoehen statt neuen Eintrag
                existing.count += 1
                existing.last_occurrence = now.isoformat()
                tracked = existing
            else:
                # Neuen Fehler erstellen
                tracked = TrackedError(
                    timestamp=now.isoformat(),
                    module=module,
                    function=function,
                    error_type=type(error).__name__,
                    message=str(error)[:500],  # Begrenzen
                    severity=severity.value,
                    traceback=tb[:2000] if tb else "",  # Begrenzen
                    context=context or {},
                    last_occurrence=now.isoformat()
                )

                self._errors.append(tracked)
                self._error_by_module[module].append(tracked)

            # Statistiken aktualisieren
            self._stats["total_errors"] += 1
            self._stats["errors_by_severity"][severity.value] += 1
            self._stats["errors_by_module"][module] += 1
            self._error_counts[error_key] += 1

            # Callbacks benachrichtigen
            for callback in self._callbacks:
                try:
                    callback(tracked)
                except Exception as cb_err:
                    # Log callback errors but don't re-track (avoid infinite loop)
                    logger.warning(f"Error tracker callback failed: {cb_err}")

            # Logging
            log_msg = f"[{module}.{function}] {type(error).__name__}: {error}"
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(log_msg)
            elif severity == ErrorSeverity.ERROR:
                logger.error(log_msg)
            elif severity == ErrorSeverity.WARNING:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

            return tracked

    def _find_similar_error(self, error_key: str) -> Optional[TrackedError]:
        """Findet einen aehnlichen Fehler in den letzten Eintraegen."""
        for error in reversed(self._errors):
            key = f"{error.module}:{error.function}:{error.error_type}:{error.message[:100]}"
            if key == error_key:
                return error
        return None

    def get_recent_errors(self, limit: int = 50, module: str = None) -> List[Dict]:
        """Gibt die letzten Fehler zurueck."""
        with self._lock:
            if module:
                errors = self._error_by_module.get(module, [])[-limit:]
            else:
                errors = list(self._errors)[-limit:]

            return [e.to_dict() for e in reversed(errors)]

    def get_errors_by_severity(self, severity: ErrorSeverity, limit: int = 50) -> List[Dict]:
        """Gibt Fehler nach Schweregrad zurueck."""
        with self._lock:
            filtered = [e for e in self._errors if e.severity == severity.value]
            return [e.to_dict() for e in filtered[-limit:]]

    def get_statistics(self) -> Dict:
        """Gibt Fehler-Statistiken zurueck."""
        with self._lock:
            # Berechne zeitbasierte Stats
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(hours=24)

            errors_last_hour = sum(
                1 for e in self._errors
                if datetime.fromisoformat(e.timestamp) > hour_ago
            )
            errors_last_24h = sum(
                1 for e in self._errors
                if datetime.fromisoformat(e.timestamp) > day_ago
            )

            # Top 5 haeufigste Fehler
            sorted_counts = sorted(
                self._error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return {
                "total_errors": self._stats["total_errors"],
                "errors_by_severity": dict(self._stats["errors_by_severity"]),
                "errors_by_module": dict(self._stats["errors_by_module"]),
                "errors_last_hour": errors_last_hour,
                "errors_last_24h": errors_last_24h,
                "most_common": [{"error": k, "count": v} for k, v in sorted_counts],
                "tracked_errors_count": len(self._errors),
                "modules_with_errors": list(self._error_by_module.keys())
            }

    def get_dashboard_data(self) -> Dict:
        """Gibt alle Daten fuer das Dashboard zurueck."""
        return {
            "statistics": self.get_statistics(),
            "recent_errors": self.get_recent_errors(limit=100),
            "critical_errors": self.get_errors_by_severity(ErrorSeverity.CRITICAL, limit=20),
            "warning_count": self._stats["errors_by_severity"].get("warning", 0),
            "error_count": self._stats["errors_by_severity"].get("error", 0),
            "critical_count": self._stats["errors_by_severity"].get("critical", 0)
        }

    def register_callback(self, callback: Callable):
        """Registriert einen Callback fuer neue Fehler."""
        self._callbacks.append(callback)

    def clear_errors(self):
        """Loescht alle getrackteten Fehler."""
        with self._lock:
            self._errors.clear()
            self._error_counts.clear()
            self._error_by_module.clear()
            self._stats = {
                "total_errors": 0,
                "errors_by_severity": defaultdict(int),
                "errors_by_module": defaultdict(int),
                "errors_last_hour": 0,
                "errors_last_24h": 0,
                "most_common_errors": [],
                "last_reset": datetime.now().isoformat()
            }
            logger.info("Error-Tracker zurueckgesetzt")

    def persist_errors(self):
        """Speichert Fehler auf Disk."""
        try:
            Path(self.persist_path).parent.mkdir(parents=True, exist_ok=True)

            data = {
                "errors": [e.to_dict() for e in self._errors],
                "stats": {
                    "total_errors": self._stats["total_errors"],
                    "errors_by_severity": dict(self._stats["errors_by_severity"]),
                    "errors_by_module": dict(self._stats["errors_by_module"]),
                    "last_reset": self._stats["last_reset"]
                },
                "saved_at": datetime.now().isoformat()
            }

            with open(self.persist_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Fehler persistiert: {self.persist_path}")
        except Exception as e:
            logger.error(f"Fehler beim Persistieren: {e}")

    def _load_persisted_errors(self):
        """Laedt persistierte Fehler."""
        try:
            if os.path.exists(self.persist_path):
                with open(self.persist_path, 'r') as f:
                    data = json.load(f)

                for error_dict in data.get("errors", [])[-100:]:  # Nur letzte 100
                    error = TrackedError(**error_dict)
                    self._errors.append(error)

                logger.info(f"Geladene Fehler: {len(self._errors)}")
        except Exception as e:
            logger.warning(f"Fehler beim Laden persistierter Errors: {e}")


# Globale Instanz
error_tracker = HoloErrorTracker.get_instance()


def get_error_tracker() -> HoloErrorTracker:
    """Helper-Funktion fuer einfachen Zugriff auf den Error-Tracker."""
    return HoloErrorTracker.get_instance()


# =============================================================================
# HELPER FUNKTIONEN
# =============================================================================

def track_exception(
    module: str = "unknown",
    function: str = "unknown",
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    reraise: bool = False
):
    """
    Decorator zum automatischen Error-Tracking.

    Verwendung:
        @track_exception("my_module", "my_function")
        def my_function():
            # code that might fail
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_tracker.track_error(
                    e,
                    module=module,
                    function=function or func.__name__,
                    severity=severity
                )
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    module: str = "unknown",
    function: str = "unknown",
    default: Any = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR
) -> Any:
    """
    Fuehrt eine Funktion sicher aus mit Error-Tracking.

    Verwendung:
        result = safe_execute(
            lambda: risky_operation(),
            module="my_module",
            function="risky_operation",
            default=[]
        )
    """
    try:
        return func()
    except Exception as e:
        error_tracker.track_error(e, module=module, function=function, severity=severity)
        return default


# =============================================================================
# STRICT MODE - Fehler laut melden statt still schlucken
# =============================================================================

class StrictModeError(Exception):
    """Fehler der im Strict Mode geworfen wird."""
    def __init__(self, original_error: Exception, module: str, function: str, context: str = ""):
        self.original_error = original_error
        self.module = module
        self.function = function
        self.context = context
        super().__init__(
            f"[STRICT MODE] {module}.{function}: {type(original_error).__name__}: {original_error}"
            + (f" (Context: {context})" if context else "")
        )


class StrictModeConfig:
    """Konfiguration fuer den Strict Mode."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.enabled = True  # Strict Mode standardmaessig AN
        self.raise_on_error = False  # Fehler werfen statt nur loggen
        self.log_level = logging.ERROR  # Logging-Level fuer Fehler
        self.notify_callbacks: List[Callable] = []  # Callbacks bei Fehlern
        self.ignored_modules: set = set()  # Module die ignoriert werden
        self.error_threshold = 0  # Wenn > 0: Nach X gleichen Fehlern deaktivieren
        self._error_counts: Dict[str, int] = defaultdict(int)

    @classmethod
    def get_instance(cls) -> 'StrictModeConfig':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def enable(self, raise_errors: bool = False):
        """Aktiviert Strict Mode."""
        self.enabled = True
        self.raise_on_error = raise_errors
        logger.warning("🔴 STRICT MODE AKTIVIERT - Fehler werden laut gemeldet!")

    def disable(self):
        """Deaktiviert Strict Mode."""
        self.enabled = False
        logger.info("Strict Mode deaktiviert")

    def ignore_module(self, module: str):
        """Ignoriert ein Modul im Strict Mode."""
        self.ignored_modules.add(module)

    def add_notify_callback(self, callback: Callable):
        """Fuegt einen Callback hinzu der bei Fehlern aufgerufen wird."""
        self.notify_callbacks.append(callback)


# Globale Instanz
strict_mode = StrictModeConfig.get_instance()


def report_error(
    error: Exception,
    module: str = "unknown",
    function: str = "unknown",
    context: str = "",
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    fallback_value: Any = None
) -> Any:
    """
    Meldet einen Fehler laut und gibt einen Fallback-Wert zurueck.

    ERSETZT stille except: pass Bloecke!

    Verwendung (VORHER - SCHLECHT):
        try:
            result = risky_operation()
        except:
            pass  # STILL!

    Verwendung (NACHHER - GUT):
        try:
            result = risky_operation()
        except Exception as e:
            result = report_error(e, "module", "function", fallback_value=[])

    Args:
        error: Die Exception
        module: Name des Moduls
        function: Name der Funktion
        context: Zusaetzlicher Kontext
        severity: Schweregrad
        fallback_value: Wert der zurueckgegeben wird

    Returns:
        fallback_value
    """
    # Error tracken
    error_tracker.track_error(
        error,
        module=module,
        function=function,
        severity=severity,
        context={"context": context} if context else None
    )

    # Strict Mode Aktionen
    if strict_mode.enabled and module not in strict_mode.ignored_modules:
        # Laut loggen
        error_msg = f"⚠️  FEHLER in {module}.{function}: {type(error).__name__}: {error}"
        if context:
            error_msg += f" | Context: {context}"

        if severity == ErrorSeverity.CRITICAL:
            logger.critical(error_msg)
        elif severity == ErrorSeverity.ERROR:
            logger.error(error_msg)
        else:
            logger.warning(error_msg)

        # Callbacks benachrichtigen
        for callback in strict_mode.notify_callbacks:
            try:
                callback(error, module, function, context)
            except Exception:
                pass  # Callback-Fehler ignorieren

        # Optional: Fehler werfen
        if strict_mode.raise_on_error:
            raise StrictModeError(error, module, function, context)

    return fallback_value


def loud_fallback(
    value: Any,
    expected_type: type,
    module: str,
    function: str,
    context: str = ""
) -> Any:
    """
    Prueft ob ein Wert den erwarteten Typ hat und meldet laut wenn nicht.

    ERSETZT stille or [] / or {} Fallbacks!

    Verwendung (VORHER - SCHLECHT):
        data = response.get("items") or []  # STILL wenn None!

    Verwendung (NACHHER - GUT):
        data = loud_fallback(response.get("items"), list, "module", "func")
    """
    if value is None or (expected_type == list and value == []) or (expected_type == dict and value == {}):
        # Melde dass wir auf Fallback zurueckgreifen
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FALLBACK in {module}.{function}: Erwartete {expected_type.__name__}, "
                f"bekam {type(value).__name__}({value})"
                + (f" | Context: {context}" if context else "")
            )
            error_tracker.track_error(
                ValueError(f"Unexpected None/empty value, expected {expected_type.__name__}"),
                module=module,
                function=function,
                severity=ErrorSeverity.WARNING,
                context={"context": context, "actual_value": str(value)[:100]}
            )

        # Gib leeren Wert des erwarteten Typs zurueck
        if expected_type == list:
            return []
        elif expected_type == dict:
            return {}
        elif expected_type == str:
            return ""
        elif expected_type == int:
            return 0
        elif expected_type == float:
            return 0.0
        elif expected_type == bool:
            return False
        else:
            return None

    return value


def safe_list_access(
    lst: list,
    index: int,
    module: str,
    function: str,
    default: Any = None,
    context: str = ""
) -> Any:
    """
    Sicherer Listen-Zugriff mit lautem Fehler wenn Index nicht existiert.

    ERSETZT unsichere [0], [-1] Zugriffe!

    Verwendung (VORHER - SCHLECHT):
        first = items[0]  # IndexError wenn leer!

    Verwendung (NACHHER - GUT):
        first = safe_list_access(items, 0, "module", "func", default=None)
    """
    if not isinstance(lst, (list, tuple)):
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FEHLER in {module}.{function}: safe_list_access erwartet Liste, "
                f"bekam {type(lst).__name__}"
            )
        return default

    if len(lst) == 0:
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FALLBACK in {module}.{function}: Liste ist leer, "
                f"kann Index [{index}] nicht zugreifen"
                + (f" | Context: {context}" if context else "")
            )
            error_tracker.track_error(
                IndexError(f"List is empty, cannot access index {index}"),
                module=module,
                function=function,
                severity=ErrorSeverity.WARNING,
                context={"context": context, "index": index}
            )
        return default

    try:
        return lst[index]
    except IndexError as e:
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FALLBACK in {module}.{function}: Index [{index}] ausserhalb der Liste "
                f"(Laenge: {len(lst)})"
                + (f" | Context: {context}" if context else "")
            )
        error_tracker.track_error(e, module=module, function=function, severity=ErrorSeverity.WARNING)
        return default


def safe_dict_access(
    d: dict,
    *keys,
    module: str,
    function: str,
    default: Any = None,
    context: str = ""
) -> Any:
    """
    Sicherer verschachtelter Dict-Zugriff mit lautem Fehler.

    Verwendung:
        value = safe_dict_access(data, "user", "name", module="mod", function="fn")
    """
    if not isinstance(d, dict):
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FEHLER in {module}.{function}: safe_dict_access erwartet Dict, "
                f"bekam {type(d).__name__}"
            )
        return default

    try:
        result = d
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError) as e:
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FALLBACK in {module}.{function}: Key-Pfad {keys} nicht gefunden in Dict"
                + (f" | Context: {context}" if context else "")
            )
            error_tracker.track_error(e, module=module, function=function, severity=ErrorSeverity.WARNING)
        return default


def safe_json_parse(
    text: str,
    module: str,
    function: str,
    default: Any = None,
    context: str = ""
) -> Any:
    """
    Sicheres JSON-Parsing mit lautem Fehler.

    ERSETZT ungesicherte json.loads() Aufrufe!
    """
    if not text:
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FALLBACK in {module}.{function}: JSON-Text ist leer"
                + (f" | Context: {context}" if context else "")
            )
        return default

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  JSON-FEHLER in {module}.{function}: {e}"
                + (f" | Context: {context}" if context else "")
                + f" | Text (gekuerzt): {text[:100]}..."
            )
        error_tracker.track_error(e, module=module, function=function, severity=ErrorSeverity.WARNING)
        return default


def safe_split_access(
    text: str,
    separator: str,
    index: int,
    module: str,
    function: str,
    default: str = "",
    context: str = ""
) -> str:
    """
    Sicherer split()[index] Zugriff mit lautem Fehler.

    ERSETZT unsichere text.split("x")[n] Aufrufe!
    """
    if not isinstance(text, str):
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FEHLER in {module}.{function}: safe_split_access erwartet String, "
                f"bekam {type(text).__name__}"
            )
        return default

    parts = text.split(separator)

    if len(parts) <= abs(index):
        if strict_mode.enabled and module not in strict_mode.ignored_modules:
            logger.warning(
                f"⚠️  FALLBACK in {module}.{function}: split('{separator}') ergab nur "
                f"{len(parts)} Teile, Index [{index}] nicht verfuegbar"
                + (f" | Context: {context}" if context else "")
                + f" | Text: {text[:50]}..."
            )
            error_tracker.track_error(
                IndexError(f"Split result has only {len(parts)} parts, cannot access [{index}]"),
                module=module,
                function=function,
                severity=ErrorSeverity.WARNING
            )
        return default

    return parts[index]


# =============================================================================
# ASYNC VERSIONEN
# =============================================================================

async def async_report_error(
    error: Exception,
    module: str = "unknown",
    function: str = "unknown",
    context: str = "",
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    fallback_value: Any = None
) -> Any:
    """Async-Version von report_error."""
    return report_error(error, module, function, context, severity, fallback_value)


# =============================================================================
# DECORATOR FUER STRICT MODE
# =============================================================================

def strict_mode_handler(
    module: str = "unknown",
    function: str = None,
    fallback: Any = None
):
    """
    Decorator der Fehler im Strict Mode laut meldet.

    Verwendung:
        @strict_mode_handler("my_module", fallback=[])
        def my_function():
            return risky_operation()
    """
    def decorator(func):
        import functools
        import asyncio

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return report_error(
                    e,
                    module=module,
                    function=function or func.__name__,
                    fallback_value=fallback
                )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                return report_error(
                    e,
                    module=module,
                    function=function or func.__name__,
                    fallback_value=fallback
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
