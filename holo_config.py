"""
Holocloude Central Configuration Loader
=======================================

Laedt die zentrale config.json und stellt alle Konfigurationswerte bereit.
Unterstuetzt Environment-Variable Overrides fuer sensible Daten.

Verwendung:
    from holo_config import config, get_config

    # Direkter Zugriff
    host = config.network.ollama.host

    # Mit Pfad
    host = get_config("network.ollama.host")

    # Mit Default
    host = get_config("network.ollama.host", "http://localhost:11434")

Environment Variables (haben Vorrang vor config.json):
    HOLO_MQTT_PASSWORD - MQTT Passwort
    HOLO_MQTT_BROKER - MQTT Broker IP
    HOLO_HA_TOKEN - Home Assistant Token
    HOLO_HA_URL - Home Assistant API URL
    HOLO_OLLAMA_HOST - Ollama Host URL
    HOLO_NAS_IP - NAS IP Adresse
"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIG FILE LOCATION
# =============================================================================

# Suche config.json in verschiedenen Orten
CONFIG_SEARCH_PATHS = [
    Path(__file__).parent / "config.json",           # Neben diesem Modul
    Path.cwd() / "config.json",                       # Aktuelles Verzeichnis
    Path.home() / ".holocloude" / "config.json",     # Home Directory
    Path("/etc/holocloude/config.json"),              # System-weit
]


# =============================================================================
# NESTED DICT ACCESS HELPER
# =============================================================================

class ConfigDict(dict):
    """
    Dict mit Attribut-Zugriff fuer verschachtelte Konfiguration.
    Erlaubt config.network.mqtt.broker_ip statt config["network"]["mqtt"]["broker_ip"]
    """

    def __init__(self, data: dict = None):
        super().__init__(data or {})
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = ConfigDict(value)
            elif isinstance(value, list):
                self[key] = [ConfigDict(item) if isinstance(item, dict) else item
                            for item in value]

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"Config hat kein Attribut '{key}'")

    def __setattr__(self, key: str, value: Any):
        self[key] = value

    def get_nested(self, path: str, default: Any = None) -> Any:
        """
        Holt einen Wert ueber einen Pfad wie "network.mqtt.broker_ip"
        """
        keys = path.split(".")
        value = self
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list):
                try:
                    value = value[int(key)]
                except (ValueError, IndexError):
                    return default
            else:
                return default
        return value


# =============================================================================
# ENVIRONMENT VARIABLE OVERRIDES
# =============================================================================

ENV_OVERRIDES = {
    # Format: "config.path": "ENV_VAR_NAME"
    "network.mqtt.password": "HOLO_MQTT_PASSWORD",
    "network.mqtt.broker_ip": "HOLO_MQTT_BROKER",
    "network.mqtt.broker_port": "HOLO_MQTT_PORT",
    "network.home_assistant.token": "HOLO_HA_TOKEN",
    "network.home_assistant.api_url": "HOLO_HA_URL",
    "network.ollama.host": "HOLO_OLLAMA_HOST",
    "network.ollama.local_host": "HOLO_LLM_LOCAL_HOST",
    "network.ollama.remote_host": "HOLO_LLM_REMOTE_HOST",
    "network.nas.ip": "HOLO_NAS_IP",
    "network.nas.mac": "HOLO_NAS_MAC",
    "network.nas.ssh_user": "HOLO_NAS_SSH_USER",
    "storage.ram_cache_mb": "HOLO_RAM_CACHE_MB",
    "storage.sd_storage_gb": "HOLO_SD_STORAGE_GB",
    "storage.data_dir": "HOLO_DATA_DIR",
    "logging.level": "HOLO_LOG_LEVEL",
}


def apply_env_overrides(config: ConfigDict) -> ConfigDict:
    """Wendet Environment-Variable Overrides auf die Config an."""
    for config_path, env_var in ENV_OVERRIDES.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            # Pfad in Keys aufteilen
            keys = config_path.split(".")

            # Zum Parent navigieren
            parent = config
            for key in keys[:-1]:
                if key not in parent:
                    parent[key] = ConfigDict({})
                parent = parent[key]

            # Wert setzen (mit Typ-Konvertierung)
            final_key = keys[-1]
            original_value = parent.get(final_key)

            # Typ beibehalten wenn moeglich
            if isinstance(original_value, bool):
                parent[final_key] = env_value.lower() in ("true", "1", "yes")
            elif isinstance(original_value, int):
                try:
                    parent[final_key] = int(env_value)
                except ValueError:
                    parent[final_key] = env_value
            elif isinstance(original_value, float):
                try:
                    parent[final_key] = float(env_value)
                except ValueError:
                    parent[final_key] = env_value
            else:
                parent[final_key] = env_value

            logger.debug(f"Config override: {config_path} = [from {env_var}]")

    return config


# =============================================================================
# CONFIG LOADING
# =============================================================================

def find_config_file() -> Optional[Path]:
    """Findet die config.json Datei."""
    for path in CONFIG_SEARCH_PATHS:
        if path.exists():
            return path
    return None


def load_config(config_path: Path = None) -> ConfigDict:
    """
    Laedt die Konfiguration aus config.json.

    Args:
        config_path: Optionaler Pfad zur config.json

    Returns:
        ConfigDict mit allen Konfigurationswerten
    """
    # Config-Datei finden
    if config_path is None:
        config_path = find_config_file()

    if config_path is None or not config_path.exists():
        logger.warning("config.json nicht gefunden - verwende Defaults")
        return ConfigDict(get_default_config())

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        config = ConfigDict(data)
        logger.info(f"Config geladen von: {config_path}")

        # Environment Overrides anwenden
        config = apply_env_overrides(config)

        return config

    except json.JSONDecodeError as e:
        logger.error(f"config.json JSON Fehler: {e}")
        return ConfigDict(get_default_config())
    except Exception as e:
        logger.error(f"config.json Ladefehler: {e}")
        return ConfigDict(get_default_config())


def get_default_config() -> Dict:
    """Gibt Default-Konfiguration zurueck wenn config.json fehlt."""
    return {
        "network": {
            "ollama": {
                "host": "http://localhost:11434",
                "local_host": "http://localhost:11434",
                "remote_host": "http://localhost:11434"
            },
            "mqtt": {
                "broker_ip": "localhost",
                "broker_port": 1883,
                "username": "",
                "password": ""
            },
            "home_assistant": {
                "api_url": "http://localhost:8123/api",
                "token": ""
            },
            "nas": {
                "ip": "192.168.1.1",
                "mac": "",
                "ssh_user": "admin",
                "ssh_port": 22
            }
        },
        "devices": {
            "tracked_devices": {},
            "wake_detection_devices": [],
            "media_sources": [],
            "rooms": {}
        },
        "llm": {
            "local_model": "llama3.2",
            "remote_model": "llama3.2",
            "fallback_model": "llama3.2",
            "temperature": 0.7,
            "timeout_seconds": 120
        },
        "behavior": {
            "bedtime_reminder_hour": 23,
            "wake_up_hour": 7
        },
        "watchlist": {
            "news_topics": [],
            "priority_sources": []
        },
        "storage": {
            "data_dir": "data",
            "ram_cache_mb": 500,
            "sd_storage_gb": 16,
            "cleanup_enabled": False
        },
        "logging": {
            "level": "INFO"
        },
        "features": {
            "enable_voice": True,
            "enable_media_discovery": True,
            "enable_proactive_messages": True
        }
    }


# =============================================================================
# GLOBAL CONFIG INSTANCE
# =============================================================================

# Singleton Config-Instanz
_config: Optional[ConfigDict] = None


def get_config(path: str = None, default: Any = None) -> Any:
    """
    Holt einen Konfigurationswert.

    Args:
        path: Punkt-separierter Pfad (z.B. "network.mqtt.broker_ip")
              Wenn None, gibt die gesamte Config zurueck
        default: Default-Wert wenn Pfad nicht existiert

    Returns:
        Konfigurationswert oder Default

    Beispiele:
        >>> get_config("network.mqtt.broker_ip")
        "192.168.178.99"

        >>> get_config("network.mqtt.broker_port", 1883)
        1883

        >>> get_config()  # Gesamte Config
        ConfigDict({...})
    """
    global _config

    if _config is None:
        _config = load_config()

    if path is None:
        return _config

    return _config.get_nested(path, default)


def reload_config(config_path: Path = None) -> ConfigDict:
    """
    Laedt die Konfiguration neu.

    Args:
        config_path: Optionaler neuer Pfad zur config.json

    Returns:
        Neue ConfigDict Instanz
    """
    global _config
    _config = load_config(config_path)
    logger.info("Config neu geladen")
    return _config


# =============================================================================
# CONVENIENCE PROPERTIES
# =============================================================================

@property
def config() -> ConfigDict:
    """Property fuer direkten Config-Zugriff."""
    return get_config()


# Lazy-loaded config fuer Import
class _ConfigProxy:
    """Proxy-Klasse fuer lazy config loading."""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_config(), name)

    def __getitem__(self, key: str) -> Any:
        return get_config()[key]


# Globale Config-Instanz fuer einfachen Import
config = _ConfigProxy()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_config(cfg: ConfigDict = None) -> Dict[str, list]:
    """
    Validiert die Konfiguration und gibt Warnungen/Fehler zurueck.

    Returns:
        Dict mit "errors" und "warnings" Listen
    """
    if cfg is None:
        cfg = get_config()

    errors = []
    warnings = []

    # Pflichtfelder pruefen
    required_paths = [
        "network.ollama.host",
        "storage.data_dir",
    ]

    for path in required_paths:
        if not cfg.get_nested(path):
            errors.append(f"Pflichtfeld fehlt: {path}")

    # Sensible Daten warnen wenn leer
    sensitive_paths = [
        ("network.mqtt.password", "MQTT Passwort"),
        ("network.home_assistant.token", "Home Assistant Token"),
    ]

    for path, name in sensitive_paths:
        value = cfg.get_nested(path, "")
        if not value:
            warnings.append(f"{name} nicht konfiguriert ({path})")

    # IP-Adressen Format pruefen
    import re
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    ip_paths = [
        "network.mqtt.broker_ip",
        "network.nas.ip",
    ]

    for path in ip_paths:
        value = cfg.get_nested(path, "")
        if value and not ip_pattern.match(value) and value != "localhost":
            warnings.append(f"Ungueltige IP-Adresse: {path} = {value}")

    return {"errors": errors, "warnings": warnings}


# =============================================================================
# CLI SUPPORT
# =============================================================================

if __name__ == "__main__":
    import sys

    # Config laden und anzeigen
    cfg = load_config()

    if len(sys.argv) > 1:
        # Spezifischen Pfad abfragen
        path = sys.argv[1]
        value = cfg.get_nested(path)
        if value is not None:
            print(f"{path} = {value}")
        else:
            print(f"Pfad nicht gefunden: {path}")
            sys.exit(1)
    else:
        # Gesamte Config anzeigen (ohne sensible Daten)
        print("=== Holocloude Config ===")
        print(f"Config-Datei: {find_config_file()}")
        print()

        # Validierung
        result = validate_config(cfg)
        if result["errors"]:
            print("FEHLER:")
            for err in result["errors"]:
                print(f"  - {err}")
        if result["warnings"]:
            print("WARNUNGEN:")
            for warn in result["warnings"]:
                print(f"  - {warn}")

        print()
        print("Wichtige Einstellungen:")
        print(f"  Ollama Host: {cfg.get_nested('network.ollama.host')}")
        print(f"  MQTT Broker: {cfg.get_nested('network.mqtt.broker_ip')}")
        print(f"  Data Dir: {cfg.get_nested('storage.data_dir')}")
        print(f"  Log Level: {cfg.get_nested('logging.level')}")
