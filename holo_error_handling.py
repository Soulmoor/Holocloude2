"""
Holocloude Error Handling Utilities
====================================

Zentrale Error-Handling Patterns für das gesamte Projekt.
Ersetzt bare `except:` Blöcke durch sichere Alternativen.

Verwendung:
    from holo_error_handling import safe_execute, log_exception, ErrorContext

    # Statt:
    try:
        result = risky_operation()
    except:
        pass

    # Besser:
    result = safe_execute(risky_operation, default=None, context="risky_operation")

    # Oder mit Context Manager:
    with ErrorContext("operation_name", default=None) as ctx:
        ctx.result = risky_operation()
    result = ctx.result
"""

import logging
import traceback
import functools
from typing import Any, Callable, Optional, TypeVar, Union, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')


# =============================================================================
# AUSNAHMEN DIE NICHT GEFANGEN WERDEN SOLLTEN
# =============================================================================

# Diese Exceptions sollten NIEMALS mit bare except gefangen werden
CRITICAL_EXCEPTIONS = (
    KeyboardInterrupt,  # Ctrl+C
    SystemExit,         # sys.exit()
    GeneratorExit,      # Generator cleanup
    MemoryError,        # Kein Speicher mehr
)


# =============================================================================
# SAFE EXECUTE - Ersetzt try/except/pass Pattern
# =============================================================================

def safe_execute(
    func: Callable[..., T],
    *args,
    default: T = None,
    context: str = "",
    log_level: int = logging.DEBUG,
    reraise_critical: bool = True,
    **kwargs
) -> T:
    """
    Führt eine Funktion sicher aus mit Fallback auf Default.

    Args:
        func: Die auszuführende Funktion
        *args: Argumente für die Funktion
        default: Rückgabewert bei Fehler
        context: Kontext für Logging (z.B. Funktionsname)
        log_level: Logging-Level für Fehler (DEBUG, INFO, WARNING, ERROR)
        reraise_critical: Kritische Exceptions weitergeben (KeyboardInterrupt etc.)
        **kwargs: Keyword-Argumente für die Funktion

    Returns:
        Ergebnis der Funktion oder default bei Fehler

    Beispiel:
        # Statt:
        try:
            value = int(text)
        except:
            value = 0

        # Besser:
        value = safe_execute(int, text, default=0, context="parse_int")
    """
    try:
        return func(*args, **kwargs)
    except CRITICAL_EXCEPTIONS:
        if reraise_critical:
            raise
        return default
    except Exception as e:
        if context:
            logger.log(log_level, f"[{context}] {type(e).__name__}: {e}")
        else:
            logger.log(log_level, f"{type(e).__name__}: {e}")
        return default


def safe_execute_async(
    func: Callable[..., T],
    *args,
    default: T = None,
    context: str = "",
    **kwargs
) -> T:
    """Async-Version von safe_execute."""
    import asyncio

    async def _wrapper():
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except CRITICAL_EXCEPTIONS:
            raise
        except Exception as e:
            if context:
                logger.debug(f"[{context}] {type(e).__name__}: {e}")
            return default

    return _wrapper()


# =============================================================================
# ERROR CONTEXT MANAGER
# =============================================================================

class ErrorContext:
    """
    Context Manager für sicheres Error-Handling.

    Beispiel:
        with ErrorContext("load_config", default={}) as ctx:
            ctx.result = json.load(file)
        config = ctx.result  # {} bei Fehler
    """

    def __init__(
        self,
        context: str = "",
        default: Any = None,
        log_level: int = logging.DEBUG,
        reraise_critical: bool = True
    ) -> None:
        self.context = context
        self.default = default
        self.log_level = log_level
        self.reraise_critical = reraise_critical
        self.result = default
        self.error: Optional[Exception] = None
        self.success = True

    def __enter__(self) -> 'ErrorContext':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            return True

        # Kritische Exceptions durchlassen
        if exc_type in CRITICAL_EXCEPTIONS:
            if self.reraise_critical:
                return False  # Exception weitergeben
            self.error = exc_val
            self.success = False
            self.result = self.default
            return True

        # Normale Exceptions loggen und unterdrücken
        self.error = exc_val
        self.success = False
        self.result = self.default

        if self.context:
            logger.log(self.log_level, f"[{self.context}] {exc_type.__name__}: {exc_val}")
        else:
            logger.log(self.log_level, f"{exc_type.__name__}: {exc_val}")

        return True  # Exception unterdrücken


@contextmanager
def error_context(context: str = "", default: Any = None, log_level: int = logging.DEBUG):
    """
    Funktionaler Context Manager für Error-Handling.

    Beispiel:
        with error_context("parse_json", default={}) as get_result:
            data = json.loads(text)
        # Bei Fehler: data ist nicht gesetzt, aber kein Crash
    """
    ctx = ErrorContext(context, default, log_level)
    try:
        yield ctx
    except CRITICAL_EXCEPTIONS:
        raise
    except Exception as e:
        ctx.error = e
        ctx.success = False
        if context:
            logger.log(log_level, f"[{context}] {type(e).__name__}: {e}")


# =============================================================================
# DECORATOR FÜR FUNKTIONEN
# =============================================================================

def handle_errors(
    default: Any = None,
    context: str = "",
    log_level: int = logging.DEBUG,
    reraise_critical: bool = True
):
    """
    Decorator für sicheres Error-Handling.

    Beispiel:
        @handle_errors(default=0, context="calculate")
        def risky_calculation(x, y):
            return x / y

        result = risky_calculation(10, 0)  # Gibt 0 zurück statt ZeroDivisionError
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return safe_execute(
                func, *args,
                default=default,
                context=context or func.__name__,
                log_level=log_level,
                reraise_critical=reraise_critical,
                **kwargs
            )
        return wrapper
    return decorator


def handle_errors_async(
    default: Any = None,
    context: str = "",
    log_level: int = logging.DEBUG
):
    """Async-Version des handle_errors Decorators."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except CRITICAL_EXCEPTIONS:
                raise
            except Exception as e:
                ctx = context or func.__name__
                logger.log(log_level, f"[{ctx}] {type(e).__name__}: {e}")
                return default
        return wrapper
    return decorator


# =============================================================================
# LOGGING HELPERS
# =============================================================================

def log_exception(
    e: Exception,
    context: str = "",
    level: int = logging.ERROR,
    include_traceback: bool = False
) -> None:
    """
    Loggt eine Exception mit optionalem Traceback.

    Args:
        e: Die Exception
        context: Kontext für die Fehlermeldung
        level: Logging-Level
        include_traceback: Ob Traceback geloggt werden soll
    """
    msg = f"[{context}] " if context else ""
    msg += f"{type(e).__name__}: {e}"

    if include_traceback:
        msg += f"\n{traceback.format_exc()}"

    logger.log(level, msg)


def format_exception(e: Exception, include_traceback: bool = False) -> str:
    """Formatiert eine Exception als String."""
    result = f"{type(e).__name__}: {e}"
    if include_traceback:
        result += f"\n{traceback.format_exc()}"
    return result


# =============================================================================
# RETRY DECORATOR
# =============================================================================

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    context: str = ""
):
    """
    Decorator für automatische Wiederholung bei Fehlern.

    Args:
        max_attempts: Maximale Anzahl Versuche
        delay: Initiale Verzögerung zwischen Versuchen (Sekunden)
        backoff: Multiplikator für Verzögerung (exponentielles Backoff)
        exceptions: Tuple von Exceptions die wiederholt werden sollen
        context: Kontext für Logging

    Beispiel:
        @retry(max_attempts=3, delay=1.0, context="api_call")
        def call_api():
            return requests.get(url)
    """
    import time

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            ctx = context or func.__name__
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except CRITICAL_EXCEPTIONS:
                    raise
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.warning(f"[{ctx}] Alle {max_attempts} Versuche fehlgeschlagen: {e}")
                        raise

                    logger.debug(f"[{ctx}] Versuch {attempt}/{max_attempts} fehlgeschlagen: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff

            # Sollte nie erreicht werden
            raise RuntimeError(f"[{ctx}] Retry logic error")

        return wrapper
    return decorator


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_not_none(value: Any, name: str = "value") -> Any:
    """Stellt sicher dass ein Wert nicht None ist."""
    if value is None:
        raise ValueError(f"{name} darf nicht None sein")
    return value


def validate_type(value: Any, expected_type: type, name: str = "value") -> Any:
    """Stellt sicher dass ein Wert den erwarteten Typ hat."""
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} muss {expected_type.__name__} sein, ist aber {type(value).__name__}")
    return value


def validate_range(value: Union[int, float], min_val: float = None, max_val: float = None, name: str = "value") -> Union[int, float]:
    """Stellt sicher dass ein Wert im erwarteten Bereich liegt."""
    if min_val is not None and value < min_val:
        raise ValueError(f"{name} muss >= {min_val} sein, ist aber {value}")
    if max_val is not None and value > max_val:
        raise ValueError(f"{name} muss <= {max_val} sein, ist aber {value}")
    return value


# =============================================================================
# GRACEFUL DEGRADATION PATTERN
# =============================================================================

class GracefulDegradation:
    """
    Helper für Graceful Degradation - probiert mehrere Strategien.

    Beispiel:
        gd = GracefulDegradation("get_data")
        gd.add_strategy(fetch_from_api, "API")
        gd.add_strategy(fetch_from_cache, "Cache")
        gd.add_strategy(lambda: default_data, "Default")

        result = gd.execute()  # Probiert API, dann Cache, dann Default
    """

    def __init__(self, context: str = "") -> None:
        self.context = context
        self.strategies: List[tuple] = []

    def add_strategy(self, func: Callable[[], T], name: str = "") -> 'GracefulDegradation':
        """Fügt eine Strategie hinzu."""
        self.strategies.append((func, name))
        return self

    def execute(self, default: T = None) -> T:
        """Führt Strategien der Reihe nach aus bis eine erfolgreich ist."""
        for func, name in self.strategies:
            try:
                result = func()
                if result is not None:
                    logger.debug(f"[{self.context}] Strategie '{name}' erfolgreich")
                    return result
            except CRITICAL_EXCEPTIONS:
                raise
            except Exception as e:
                logger.debug(f"[{self.context}] Strategie '{name}' fehlgeschlagen: {e}")
                continue

        logger.warning(f"[{self.context}] Alle Strategien fehlgeschlagen, nutze Default")
        return default


# =============================================================================
# QUICK REPLACEMENTS FÜR HÄUFIGE PATTERNS
# =============================================================================

def safe_int(value: Any, default: int = 0) -> int:
    """Sichere Konvertierung zu int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Sichere Konvertierung zu float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Sicherer Attribut-Zugriff."""
    try:
        if hasattr(obj, key):
            return getattr(obj, key)
        elif hasattr(obj, '__getitem__'):
            return obj[key]
        return default
    except (KeyError, IndexError, TypeError):
        return default


def safe_dict_get(d: dict, *keys, default: Any = None) -> Any:
    """Sicherer verschachtelter Dict-Zugriff."""
    try:
        result = d
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError, IndexError):
        return default


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Sicheres JSON Parsing."""
    import json
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_call(obj: Any, method: str, *args, default: Any = None, **kwargs) -> Any:
    """Sicherer Methoden-Aufruf."""
    try:
        if hasattr(obj, method):
            return getattr(obj, method)(*args, **kwargs)
        return default
    except Exception:
        return default
