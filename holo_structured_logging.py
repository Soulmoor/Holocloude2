"""
Holocloude Structured Logging System
=====================================

JSON-basiertes strukturiertes Logging fuer bessere Analyse und Monitoring.

Features:
- JSON-Format fuer maschinelle Verarbeitung
- Kontext-Anreicherung (request_id, user_id, etc.)
- Log-Level-basierte Ausgabe
- Rotating File Handler mit Kompression
- Optional: Text-Format fuer Entwicklung
- Kompatibel mit ELK Stack, Loki, etc.

Verwendung:
    from holo_structured_logging import setup_logging, get_logger

    setup_logging(json_format=True)
    logger = get_logger(__name__)

    logger.info("User logged in", extra={"user_id": "123", "ip": "192.168.1.1"})

    # Mit Context Manager
    with LogContext(request_id="abc-123"):
        logger.info("Processing request")
"""

import os
import sys
import json
import logging
import logging.handlers
import threading
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from pathlib import Path

# Context-Variable fuer Request-Tracking
_log_context: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})


class LogContext:
    """
    Context Manager fuer Log-Kontext.

    Verwendung:
        with LogContext(request_id="abc", user="max"):
            logger.info("Message")  # Enthaelt automatisch request_id und user
    """

    def __init__(self, **kwargs):
        self.new_context = kwargs
        self.old_context = None

    def __enter__(self):
        self.old_context = _log_context.get().copy()
        new = {**self.old_context, **self.new_context}
        _log_context.set(new)
        return self

    def __exit__(self, *args):
        _log_context.set(self.old_context)


def get_context() -> Dict[str, Any]:
    """Gibt den aktuellen Log-Kontext zurueck."""
    return _log_context.get().copy()


def set_context(**kwargs):
    """Setzt Werte im aktuellen Log-Kontext."""
    current = _log_context.get().copy()
    current.update(kwargs)
    _log_context.set(current)


def clear_context():
    """Loescht den aktuellen Log-Kontext."""
    _log_context.set({})


class JSONFormatter(logging.Formatter):
    """
    Formatiert Log-Records als JSON.

    Ausgabe-Format:
    {
        "timestamp": "2026-01-16T12:00:00.000Z",
        "level": "INFO",
        "logger": "holo_brain",
        "message": "Processing message",
        "context": {"request_id": "abc"},
        "extra": {"user_id": "123"},
        "location": {"file": "holo_brain.py", "line": 42, "function": "process"}
    }
    """

    def __init__(
        self,
        include_location: bool = True,
        include_exception: bool = True,
        timestamp_format: str = "iso"
    ):
        super().__init__()
        self.include_location = include_location
        self.include_exception = include_exception
        self.timestamp_format = timestamp_format

    def format(self, record: logging.LogRecord) -> str:
        # Basis-Felder
        log_entry = {
            "timestamp": self._format_timestamp(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Kontext aus ContextVar
        context = get_context()
        if context:
            log_entry["context"] = context

        # Extra-Felder aus record (ausser Standard-Felder)
        extra = self._extract_extra(record)
        if extra:
            log_entry["extra"] = extra

        # Location-Info
        if self.include_location:
            log_entry["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Exception-Info
        if self.include_exception and record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self._format_traceback(record.exc_info),
            }

        # Thread/Process Info (optional, nuetzlich fuer Debugging)
        log_entry["thread"] = record.threadName
        log_entry["process"] = record.process

        return json.dumps(log_entry, ensure_ascii=False, default=str)

    def _format_timestamp(self, record: logging.LogRecord) -> str:
        dt = datetime.fromtimestamp(record.created)
        if self.timestamp_format == "iso":
            return dt.isoformat() + "Z"
        elif self.timestamp_format == "unix":
            return str(record.created)
        else:
            return dt.strftime(self.timestamp_format)

    def _extract_extra(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extrahiert Extra-Felder aus dem Log-Record."""
        # Standard-Felder die wir ignorieren
        standard_fields = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "pathname", "process", "processName", "relativeCreated",
            "stack_info", "exc_info", "exc_text", "thread", "threadName",
            "message", "asctime"
        }

        extra = {}
        for key, value in record.__dict__.items():
            if key not in standard_fields and not key.startswith("_"):
                extra[key] = value

        return extra

    def _format_traceback(self, exc_info) -> Optional[str]:
        """Formatiert Exception-Traceback."""
        if exc_info and exc_info[2]:
            return "".join(traceback.format_exception(*exc_info))
        return None


class PrettyFormatter(logging.Formatter):
    """
    Huebsche Text-Formatierung fuer Entwicklung.

    Format: [TIMESTAMP] LEVEL logger - message {extra}
    """

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        # Timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Level mit Farbe
        level = record.levelname
        if self.use_colors:
            color = self.COLORS.get(level, "")
            level = f"{color}{level:8}{self.RESET}"
        else:
            level = f"{level:8}"

        # Logger-Name (gekuerzt)
        logger_name = record.name
        if len(logger_name) > 20:
            logger_name = "..." + logger_name[-17:]

        # Message
        message = record.getMessage()

        # Extra-Felder
        extra = self._extract_extra(record)
        context = get_context()
        all_extra = {**context, **extra}

        extra_str = ""
        if all_extra:
            extra_str = " " + " ".join(f"{k}={v}" for k, v in all_extra.items())

        # Basis-Zeile
        line = f"[{timestamp}] {level} {logger_name:20} - {message}{extra_str}"

        # Exception
        if record.exc_info:
            line += "\n" + "".join(traceback.format_exception(*record.exc_info))

        return line

    def _extract_extra(self, record: logging.LogRecord) -> Dict[str, Any]:
        standard_fields = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "pathname", "process", "processName", "relativeCreated",
            "stack_info", "exc_info", "exc_text", "thread", "threadName",
            "message", "asctime"
        }
        return {
            k: v for k, v in record.__dict__.items()
            if k not in standard_fields and not k.startswith("_")
        }


class StructuredLogger(logging.Logger):
    """
    Erweiterter Logger mit Structured-Logging-Support.

    Erlaubt einfaches Hinzufuegen von Extra-Feldern:
        logger.info("Message", user_id="123", action="login")
    """

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        # kwargs werden als extra-Felder behandelt
        if kwargs:
            if extra is None:
                extra = {}
            extra.update(kwargs)

        super()._log(level, msg, args, exc_info, extra, stack_info)


# Registriere unseren Logger-Typ
logging.setLoggerClass(StructuredLogger)


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console: bool = True,
    include_location: bool = True
) -> logging.Logger:
    """
    Konfiguriert das Logging-System.

    Args:
        level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: True fuer JSON, False fuer Pretty-Print
        log_file: Pfad zur Log-Datei (optional)
        max_bytes: Max. Dateigroesse vor Rotation
        backup_count: Anzahl der Backup-Dateien
        console: Ausgabe auf Console
        include_location: File/Line/Function in JSON inkludieren

    Returns:
        Root-Logger
    """
    # Root-Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Alte Handler entfernen
    root_logger.handlers.clear()

    # Formatter waehlen
    if json_format:
        formatter = JSONFormatter(include_location=include_location)
    else:
        formatter = PrettyFormatter(use_colors=True)

    # Console Handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File Handler
    if log_file:
        # Verzeichnis erstellen falls noetig
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        # Datei immer als JSON fuer maschinelle Verarbeitung
        file_handler.setFormatter(JSONFormatter(include_location=include_location))
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> StructuredLogger:
    """
    Gibt einen konfigurierten Logger zurueck.

    Args:
        name: Logger-Name (typischerweise __name__)

    Returns:
        StructuredLogger-Instanz
    """
    return logging.getLogger(name)


# =============================================================================
# CONVENIENCE FUNKTIONEN
# =============================================================================

def log_request(logger: logging.Logger, method: str, path: str, **kwargs):
    """Loggt einen HTTP-Request."""
    logger.info(
        f"{method} {path}",
        extra={"event": "http_request", "method": method, "path": path, **kwargs}
    )


def log_response(logger: logging.Logger, method: str, path: str, status: int, duration_ms: float, **kwargs):
    """Loggt eine HTTP-Response."""
    logger.info(
        f"{method} {path} -> {status} ({duration_ms:.1f}ms)",
        extra={"event": "http_response", "method": method, "path": path,
               "status": status, "duration_ms": duration_ms, **kwargs}
    )


def log_error(logger: logging.Logger, message: str, error: Exception, **kwargs):
    """Loggt einen Fehler mit Exception-Details."""
    logger.error(
        message,
        exc_info=error,
        extra={"event": "error", "error_type": type(error).__name__, **kwargs}
    )


def log_metric(logger: logging.Logger, metric_name: str, value: float, **tags):
    """Loggt eine Metrik."""
    logger.info(
        f"metric:{metric_name}={value}",
        extra={"event": "metric", "metric_name": metric_name, "value": value, **tags}
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Holocloude Structured Logging Demo")
    parser.add_argument("--json", action="store_true", help="JSON-Format verwenden")
    parser.add_argument("--file", help="Log-Datei")
    parser.add_argument("--level", default="DEBUG", help="Log-Level")

    args = parser.parse_args()

    # Setup
    setup_logging(
        level=args.level,
        json_format=args.json,
        log_file=args.file
    )

    logger = get_logger("demo")

    # Demo-Logs
    logger.debug("Debug message")
    logger.info("Info message", user_id="123", action="demo")

    with LogContext(request_id="req-abc-123", session="sess-xyz"):
        logger.info("Message with context")
        logger.warning("Warning with context", extra_field="value")

    try:
        raise ValueError("Demo error")
    except Exception as e:
        log_error(logger, "Something went wrong", e, component="demo")

    log_metric(logger, "response_time", 42.5, endpoint="/api/test")
    log_request(logger, "GET", "/api/health")
    log_response(logger, "GET", "/api/health", 200, 15.3)

    print("\n--- Demo complete ---")
