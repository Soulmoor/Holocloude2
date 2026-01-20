"""
HOLO UTILS - Zentrale Utility-Funktionen
=========================================

Konsolidiert haeufig verwendete Patterns um Duplikation zu vermeiden.

Enthaltene Utilities:
- Datetime-Funktionen
- JSON-Serialisierung
- String-Validierung
- Dictionary-Zugriff
- Serializable-Mixin

Verwendung:
    from holo_utils import (
        get_iso_timestamp,
        safe_json_dumps,
        validate_string,
        safe_get,
        SerializableMixin
    )
"""

import json
import re
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Type, Union
from dataclasses import asdict, is_dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# DATETIME UTILITIES
# =============================================================================

def get_iso_timestamp() -> str:
    """
    Gibt aktuellen Zeitstempel im ISO-Format zurueck.

    Ersetzt das Pattern: datetime.now().isoformat()

    Returns:
        str: ISO-formatierter Zeitstempel

    Example:
        >>> timestamp = get_iso_timestamp()
        >>> # "2026-01-20T14:30:45.123456"
    """
    return datetime.now().isoformat()


def get_timestamp_compact() -> str:
    """
    Kompaktes Zeitstempel-Format fuer Dateinamen.

    Returns:
        str: Format "YYYYMMDD_HHMMSS"
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_timestamp_readable() -> str:
    """
    Lesbares Zeitstempel-Format fuer Logs und Ausgaben.

    Returns:
        str: Format "DD.MM.YYYY HH:MM:SS"
    """
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def parse_iso_timestamp(iso_string: str) -> Optional[datetime]:
    """
    Parst einen ISO-Zeitstempel sicher.

    Args:
        iso_string: ISO-formatierter String

    Returns:
        datetime oder None bei Fehler
    """
    try:
        return datetime.fromisoformat(iso_string)
    except (ValueError, TypeError):
        return None


def time_ago(dt: datetime) -> str:
    """
    Gibt relative Zeit als lesbaren String zurueck.

    Args:
        dt: Datetime-Objekt

    Returns:
        str: z.B. "vor 5 Minuten", "vor 2 Stunden"
    """
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "gerade eben"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"vor {minutes} Minute{'n' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"vor {hours} Stunde{'n' if hours != 1 else ''}"
    else:
        days = int(seconds / 86400)
        return f"vor {days} Tag{'en' if days != 1 else ''}"


# =============================================================================
# JSON UTILITIES
# =============================================================================

def safe_json_dumps(
    obj: Any,
    indent: Optional[int] = None,
    default: Any = str,
    sort_keys: bool = False
) -> str:
    """
    Sichere JSON-Serialisierung mit UTF-8-Support.

    Ersetzt das Pattern: json.dumps(obj, ensure_ascii=False, default=str)

    Args:
        obj: Zu serialisierendes Objekt
        indent: Einrueckung (None fuer kompakt)
        default: Fallback-Funktion fuer nicht-serialisierbare Typen
        sort_keys: Schluessel sortieren

    Returns:
        str: JSON-String
    """
    try:
        return json.dumps(
            obj,
            ensure_ascii=False,
            indent=indent,
            default=default,
            sort_keys=sort_keys
        )
    except (TypeError, ValueError) as e:
        logger.warning(f"JSON serialization fallback: {e}")
        return json.dumps(str(obj), ensure_ascii=False)


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Sichere JSON-Deserialisierung.

    Args:
        json_string: JSON-String
        default: Rueckgabewert bei Fehler

    Returns:
        Deserialisiertes Objekt oder default
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def pretty_json(obj: Any) -> str:
    """
    Gibt huebsch formatierten JSON-String zurueck.

    Args:
        obj: Zu formatierendes Objekt

    Returns:
        str: Eingerueckter JSON-String
    """
    return safe_json_dumps(obj, indent=2, sort_keys=True)


# =============================================================================
# STRING VALIDATION UTILITIES
# =============================================================================

def validate_string(
    value: str,
    allowed_chars: Optional[str] = None,
    pattern: Optional[str] = None,
    max_length: int = 255,
    default: str = ""
) -> str:
    """
    Universelle String-Validierung.

    Args:
        value: Zu validierender String
        allowed_chars: Erlaubte Zeichen (None = alle)
        pattern: Regex-Pattern zum Ersetzen ungültiger Zeichen
        max_length: Maximale Laenge
        default: Rueckgabewert bei leerem Ergebnis

    Returns:
        str: Bereinigter String
    """
    if not isinstance(value, str):
        value = str(value) if value is not None else default

    value = value.strip()

    if pattern:
        value = re.sub(pattern, '', value)
    elif allowed_chars:
        allowed_set = set(allowed_chars)
        value = ''.join(c for c in value if c in allowed_set)

    value = value[:max_length].strip()

    return value if value else default


def validate_identifier(name: str, default: str = "unknown") -> str:
    """
    Validiert einen Bezeichner (nur alphanumerisch und Bindestriche).

    Ersetzt das Pattern aus holo_device_agent.py:_validate_device_name

    Args:
        name: Zu validierender Name
        default: Fallback bei leerem Ergebnis

    Returns:
        str: Gueltiger Bezeichner
    """
    # Nur alphanumerisch und Bindestriche
    cleaned = re.sub(r'[^a-zA-Z0-9\-]', '-', name.lower())
    # Mehrfache Bindestriche zusammenfassen
    cleaned = re.sub(r'-+', '-', cleaned)
    # Fuehrende/trailing Bindestriche entfernen
    cleaned = cleaned.strip('-')
    # Max 50 Zeichen
    return cleaned[:50] if cleaned else default


def validate_display_name(name: str, default: str = "Unbekannt") -> str:
    """
    Validiert einen Anzeigenamen (entfernt gefaehrliche Zeichen).

    Args:
        name: Zu validierender Name
        default: Fallback bei leerem Ergebnis

    Returns:
        str: Sicherer Anzeigename
    """
    allowed = set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789 -_'
        'äöüÄÖÜß'
    )
    cleaned = ''.join(c for c in name if c in allowed)
    return cleaned[:100].strip() if cleaned else default


def validate_enum_value(
    value: str,
    allowed_values: Set[str],
    default: str
) -> str:
    """
    Validiert einen Wert gegen eine Whitelist.

    Args:
        value: Zu validierender Wert
        allowed_values: Erlaubte Werte
        default: Fallback bei ungueltigem Wert

    Returns:
        str: Gueltiger Wert
    """
    cleaned = value.lower().strip() if isinstance(value, str) else ""
    return cleaned if cleaned in allowed_values else default


def validate_ip_or_hostname(address: str, default: str = "localhost") -> str:
    """
    Validiert eine IP-Adresse oder Hostname.

    Args:
        address: Zu validierende Adresse
        default: Fallback bei ungueltiger Adresse

    Returns:
        str: Gueltige Adresse
    """
    address = address.strip() if isinstance(address, str) else ""

    if address == 'localhost':
        return address

    # IP-Adresse Pattern
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, address):
        parts = address.split('.')
        if all(0 <= int(p) <= 255 for p in parts):
            return address

    # Hostname Pattern
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*$'
    if re.match(hostname_pattern, address) and len(address) <= 253:
        return address

    return default


# =============================================================================
# DICTIONARY UTILITIES
# =============================================================================

def safe_get(
    obj: Dict,
    *keys: str,
    default: Any = None
) -> Any:
    """
    Sicherer Zugriff auf verschachtelte Dictionary-Werte.

    Ersetzt das Pattern: obj.get('a', {}).get('b', {}).get('c', default)

    Args:
        obj: Dictionary
        *keys: Schluessel-Pfad
        default: Rueckgabewert bei Fehler

    Returns:
        Wert oder default

    Example:
        >>> data = {"a": {"b": {"c": 42}}}
        >>> safe_get(data, "a", "b", "c")  # 42
        >>> safe_get(data, "a", "x", "y", default=0)  # 0
    """
    try:
        result = obj
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            elif isinstance(result, (list, tuple)) and isinstance(key, int):
                result = result[key]
            else:
                return default
            if result is None:
                return default
        return result
    except (KeyError, TypeError, IndexError):
        return default


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merged mehrere Dictionaries (tiefes Merging).

    Args:
        *dicts: Zu mergende Dictionaries

    Returns:
        Dict: Gemergtes Dictionary
    """
    result = {}

    for d in dicts:
        if not d:
            continue
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return result


def dict_diff(old: Dict, new: Dict) -> Dict:
    """
    Findet Unterschiede zwischen zwei Dictionaries.

    Args:
        old: Altes Dictionary
        new: Neues Dictionary

    Returns:
        Dict mit 'added', 'removed', 'changed' Keys
    """
    old_keys = set(old.keys()) if old else set()
    new_keys = set(new.keys()) if new else set()

    return {
        'added': {k: new[k] for k in new_keys - old_keys},
        'removed': {k: old[k] for k in old_keys - new_keys},
        'changed': {
            k: {'old': old[k], 'new': new[k]}
            for k in old_keys & new_keys
            if old[k] != new[k]
        }
    }


# =============================================================================
# SERIALIZABLE MIXIN
# =============================================================================

class SerializableMixin:
    """
    Mixin-Klasse fuer serialisierbare Objekte.

    Bietet Standard-Implementierungen fuer to_dict() und from_dict().

    Ersetzt duplizierte to_dict()-Implementierungen in:
    - holo_problem_solver.py
    - holo_core_types.py
    - holo_live_monitor.py
    - etc.

    Usage:
        @dataclass
        class MyClass(SerializableMixin):
            name: str
            value: int

        obj = MyClass("test", 42)
        data = obj.to_dict()  # {"name": "test", "value": 42}
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Objekt zu einem Dictionary.

        Returns:
            Dict: Serialisiertes Objekt
        """
        if is_dataclass(self):
            return asdict(self)

        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (list, tuple)):
                result[key] = [
                    v.to_dict() if hasattr(v, 'to_dict') else v
                    for v in value
                ]
            else:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerializableMixin':
        """
        Erstellt ein Objekt aus einem Dictionary.

        Args:
            data: Dictionary mit Attributen

        Returns:
            Neues Objekt
        """
        if is_dataclass(cls):
            return cls(**data)

        obj = cls.__new__(cls)
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Serialisiert das Objekt zu JSON.

        Args:
            indent: Einrueckung (None fuer kompakt)

        Returns:
            str: JSON-String
        """
        return safe_json_dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_string: str) -> 'SerializableMixin':
        """
        Erstellt ein Objekt aus einem JSON-String.

        Args:
            json_string: JSON-String

        Returns:
            Neues Objekt
        """
        data = safe_json_loads(json_string, {})
        return cls.from_dict(data)


# =============================================================================
# TYPE VALIDATION
# =============================================================================

def ensure_type(value: Any, expected_type: Type, default: Any = None) -> Any:
    """
    Stellt sicher dass ein Wert den erwarteten Typ hat.

    Args:
        value: Zu pruefender Wert
        expected_type: Erwarteter Typ
        default: Fallback bei falschem Typ

    Returns:
        Wert oder default
    """
    if isinstance(value, expected_type):
        return value
    return default


def ensure_list(value: Any) -> List:
    """
    Stellt sicher dass der Wert eine Liste ist.

    Args:
        value: Beliebiger Wert

    Returns:
        Liste (wrapping wenn noetig)
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def ensure_dict(value: Any) -> Dict:
    """
    Stellt sicher dass der Wert ein Dictionary ist.

    Args:
        value: Beliebiger Wert

    Returns:
        Dictionary oder leeres Dict
    """
    if isinstance(value, dict):
        return value
    return {}


# =============================================================================
# LOGGING HELPER (Ersetzt print() in Test-Funktionen)
# =============================================================================

class TestLogger:
    """
    Logger fuer Test-Funktionen als Ersatz fuer print().

    Kann zu echtem Logging umschalten oder stdout verwenden.

    Usage:
        tlog = TestLogger("MyTest")
        tlog.header("Test startet")
        tlog.info("Schritt 1 erfolgreich")
        tlog.success("Test bestanden!")
    """

    def __init__(self, name: str, use_print: bool = True):
        """
        Args:
            name: Name des Tests
            use_print: True fuer print(), False fuer logger
        """
        self.name = name
        self.use_print = use_print
        self._logger = logging.getLogger(name)

    def _output(self, message: str, level: str = "INFO"):
        if self.use_print:
            print(message)
        else:
            getattr(self._logger, level.lower(), self._logger.info)(message)

    def header(self, title: str):
        """Zeigt eine Header-Zeile."""
        self._output("=" * 60)
        self._output(f"  {title}")
        self._output("=" * 60)

    def section(self, title: str):
        """Zeigt eine Sections-Ueberschrift."""
        self._output(f"\n--- {title} ---")

    def info(self, message: str):
        """Zeigt eine Info-Nachricht."""
        self._output(f"  {message}")

    def success(self, message: str):
        """Zeigt eine Erfolgs-Nachricht."""
        self._output(f"  [OK] {message}")

    def warning(self, message: str):
        """Zeigt eine Warnung."""
        self._output(f"  [!] {message}", "WARNING")

    def error(self, message: str):
        """Zeigt einen Fehler."""
        self._output(f"  [ERROR] {message}", "ERROR")

    def result(self, label: str, value: Any):
        """Zeigt ein Ergebnis mit Label."""
        self._output(f"  {label}: {value}")

    def footer(self, message: str = "Test abgeschlossen"):
        """Zeigt eine Footer-Zeile."""
        self._output("\n" + "=" * 60)
        self._output(f"  {message}")
        self._output("=" * 60)


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

__all__ = [
    # Datetime
    'get_iso_timestamp',
    'get_timestamp_compact',
    'get_timestamp_readable',
    'parse_iso_timestamp',
    'time_ago',

    # JSON
    'safe_json_dumps',
    'safe_json_loads',
    'pretty_json',

    # String Validation
    'validate_string',
    'validate_identifier',
    'validate_display_name',
    'validate_enum_value',
    'validate_ip_or_hostname',

    # Dict Utilities
    'safe_get',
    'merge_dicts',
    'dict_diff',

    # Type Utilities
    'ensure_type',
    'ensure_list',
    'ensure_dict',

    # Classes
    'SerializableMixin',
    'TestLogger',
]
