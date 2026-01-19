"""
Holo Self-Repair System - Vollständiges Auto-Repair für Holo
=============================================================

Ein umfassendes Self-Healing System das automatisch:
- Datenbanken repariert und wiederherstellt
- Konfigurationen korrigiert
- Module neu startet
- Provisorische Workarounds anwendet
- Code-Patches für bekannte Fehler einspielt

Autor: Claude (Anthropic) für Holo
Version: 1.0.0
"""

import os
import sys
import json
import time
import shutil
import sqlite3
import hashlib
import logging
import traceback
import threading
import subprocess
import importlib
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
import re
import ast
import tempfile


# ==================== ENUMS & DATA CLASSES ====================

class RepairType(Enum):
    """Typen von Reparaturen"""
    DATABASE = auto()
    CONFIG = auto()
    MODULE = auto()
    CODE_PATCH = auto()
    WORKAROUND = auto()
    FILESYSTEM = auto()
    PERMISSION = auto()
    DEPENDENCY = auto()


class RepairStatus(Enum):
    """Status einer Reparatur"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLBACK = "rollback"


class Severity(Enum):
    """Schweregrad eines Problems"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RepairAction:
    """Eine einzelne Reparatur-Aktion"""
    id: str
    repair_type: RepairType
    target: str
    description: str
    severity: Severity
    status: RepairStatus = RepairStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[str] = None
    rollback_data: Optional[Dict] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class RepairReport:
    """Bericht über durchgeführte Reparaturen"""
    total_issues: int = 0
    fixed: int = 0
    partial: int = 0
    failed: int = 0
    actions: List[RepairAction] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "total_issues": self.total_issues,
            "fixed": self.fixed,
            "partial": self.partial,
            "failed": self.failed,
            "success_rate": f"{(self.fixed/self.total_issues*100):.1f}%" if self.total_issues > 0 else "N/A",
            "duration": str(self.end_time - self.start_time) if self.end_time else "in_progress",
            "actions": [
                {
                    "id": a.id,
                    "type": a.repair_type.name,
                    "target": a.target,
                    "status": a.status.value,
                    "result": a.result
                }
                for a in self.actions
            ]
        }


# ==================== BASE REPAIRER CLASS ====================

class BaseRepairer(ABC):
    """Abstrakte Basisklasse für alle Repairer"""

    def __init__(self, project_dir: Path, logger: logging.Logger):
        self.project_dir = project_dir
        self.logger = logger
        self.backup_dir = project_dir / ".holo_backups"
        self.backup_dir.mkdir(exist_ok=True)

    @abstractmethod
    def detect_issues(self) -> List[RepairAction]:
        """Erkennt Probleme die repariert werden können"""
        pass

    @abstractmethod
    def repair(self, action: RepairAction) -> RepairAction:
        """Führt eine Reparatur durch"""
        pass

    @abstractmethod
    def rollback(self, action: RepairAction) -> bool:
        """Macht eine Reparatur rückgängig"""
        pass

    def _create_backup(self, path: Path, prefix: str = "") -> Optional[Path]:
        """Erstellt ein Backup einer Datei"""
        if not path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{prefix}_{path.name}_{timestamp}"
        backup_path = self.backup_dir / backup_name

        try:
            if path.is_file():
                shutil.copy2(path, backup_path)
            else:
                shutil.copytree(path, backup_path)
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup fehlgeschlagen für {path}: {e}")
            return None


# ==================== DATABASE REPAIRER ====================

class DatabaseRepairer(BaseRepairer):
    """Repariert und verwaltet Datenbanken"""

    # Bekannte Datenbank-Schemata
    KNOWN_SCHEMAS = {
        "holo_memory.db": {
            "memories": """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    importance REAL DEFAULT 0.5,
                    category TEXT,
                    tags TEXT,
                    embedding BLOB
                )
            """,
            "conversations": """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    message TEXT NOT NULL,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context TEXT
                )
            """
        },
        "holo_skills.db": {
            "skills": """
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    code TEXT,
                    version TEXT DEFAULT '1.0',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1
                )
            """,
            "skill_usage": """
                CREATE TABLE IF NOT EXISTS skill_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_id INTEGER,
                    used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 1,
                    FOREIGN KEY (skill_id) REFERENCES skills(id)
                )
            """
        },
        "holo_knowledge.db": {
            "knowledge": """
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    confidence REAL DEFAULT 0.8,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "relations": """
                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER,
                    to_id INTEGER,
                    relation_type TEXT,
                    strength REAL DEFAULT 0.5,
                    FOREIGN KEY (from_id) REFERENCES knowledge(id),
                    FOREIGN KEY (to_id) REFERENCES knowledge(id)
                )
            """
        }
    }

    def detect_issues(self) -> List[RepairAction]:
        """Erkennt Datenbank-Probleme"""
        issues = []

        # Suche nach .db Dateien
        db_files = list(self.project_dir.glob("*.db")) + \
                   list(self.project_dir.glob("data/*.db")) + \
                   list(self.project_dir.glob("databases/*.db"))

        for db_path in db_files:
            # Prüfe ob Datei korrupt ist
            if self._is_corrupt(db_path):
                issues.append(RepairAction(
                    id=f"db_corrupt_{db_path.name}",
                    repair_type=RepairType.DATABASE,
                    target=str(db_path),
                    description=f"Datenbank {db_path.name} ist korrupt",
                    severity=Severity.CRITICAL
                ))

            # Prüfe auf fehlende Tabellen
            missing = self._check_missing_tables(db_path)
            if missing:
                issues.append(RepairAction(
                    id=f"db_missing_tables_{db_path.name}",
                    repair_type=RepairType.DATABASE,
                    target=str(db_path),
                    description=f"Fehlende Tabellen in {db_path.name}: {missing}",
                    severity=Severity.HIGH
                ))

            # Prüfe auf Integritätsprobleme
            integrity = self._check_integrity(db_path)
            if integrity:
                issues.append(RepairAction(
                    id=f"db_integrity_{db_path.name}",
                    repair_type=RepairType.DATABASE,
                    target=str(db_path),
                    description=f"Integritätsprobleme in {db_path.name}: {integrity}",
                    severity=Severity.MEDIUM
                ))

        # Prüfe auf fehlende wichtige Datenbanken
        for db_name in self.KNOWN_SCHEMAS.keys():
            db_path = self.project_dir / db_name
            if not db_path.exists():
                # Auch in data/ und databases/ prüfen
                alt_paths = [
                    self.project_dir / "data" / db_name,
                    self.project_dir / "databases" / db_name
                ]
                if not any(p.exists() for p in alt_paths):
                    issues.append(RepairAction(
                        id=f"db_missing_{db_name}",
                        repair_type=RepairType.DATABASE,
                        target=str(db_path),
                        description=f"Wichtige Datenbank {db_name} fehlt",
                        severity=Severity.HIGH
                    ))

        return issues

    def repair(self, action: RepairAction) -> RepairAction:
        """Repariert ein Datenbank-Problem"""
        action.status = RepairStatus.IN_PROGRESS
        action.attempts += 1
        db_path = Path(action.target)

        try:
            if "corrupt" in action.id:
                return self._repair_corrupt(action, db_path)
            elif "missing_tables" in action.id:
                return self._repair_missing_tables(action, db_path)
            elif "integrity" in action.id:
                return self._repair_integrity(action, db_path)
            elif "missing" in action.id:
                return self._create_database(action, db_path)
            else:
                action.status = RepairStatus.FAILED
                action.result = "Unbekannter Reparaturtyp"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {str(e)}"
            self.logger.error(f"DB Repair fehlgeschlagen: {e}")

        return action

    def rollback(self, action: RepairAction) -> bool:
        """Stellt eine Datenbank aus Backup wieder her"""
        if not action.rollback_data or "backup_path" not in action.rollback_data:
            return False

        try:
            backup_path = Path(action.rollback_data["backup_path"])
            target_path = Path(action.target)

            if backup_path.exists():
                if target_path.exists():
                    target_path.unlink()
                shutil.copy2(backup_path, target_path)
                return True
        except Exception as e:
            self.logger.error(f"Rollback fehlgeschlagen: {e}")

        return False

    def _is_corrupt(self, db_path: Path) -> bool:
        """Prüft ob eine Datenbank korrupt ist"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            return result[0] != "ok"
        except:
            return True

    def _check_missing_tables(self, db_path: Path) -> List[str]:
        """Prüft auf fehlende Tabellen basierend auf bekannten Schemata"""
        if db_path.name not in self.KNOWN_SCHEMAS:
            return []

        expected_tables = set(self.KNOWN_SCHEMAS[db_path.name].keys())

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = set(row[0] for row in cursor.fetchall())
            conn.close()

            return list(expected_tables - existing_tables)
        except:
            return list(expected_tables)

    def _check_integrity(self, db_path: Path) -> Optional[str]:
        """Führt Integritätsprüfung durch"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()

            if result != "ok":
                return result
        except Exception as e:
            return str(e)

        return None

    def _repair_corrupt(self, action: RepairAction, db_path: Path) -> RepairAction:
        """Repariert eine korrupte Datenbank"""
        # Backup erstellen
        backup = self._create_backup(db_path, "corrupt")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            # Versuche Daten zu retten
            recovered_path = db_path.with_suffix('.recovered')

            # Dump und Recreate
            conn = sqlite3.connect(str(db_path))
            with open(str(recovered_path) + '.sql', 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            conn.close()

            # Neue DB erstellen
            if recovered_path.exists():
                recovered_path.unlink()

            new_conn = sqlite3.connect(str(recovered_path))
            with open(str(recovered_path) + '.sql', 'r') as f:
                new_conn.executescript(f.read())
            new_conn.close()

            # Alte ersetzen
            db_path.unlink()
            shutil.move(str(recovered_path), str(db_path))

            # Cleanup
            sql_dump = recovered_path.with_suffix('.recovered.sql')
            if sql_dump.exists():
                sql_dump.unlink()

            action.status = RepairStatus.SUCCESS
            action.result = "Datenbank erfolgreich wiederhergestellt"

        except Exception as e:
            # Plan B: Neu erstellen mit bekanntem Schema
            if db_path.name in self.KNOWN_SCHEMAS:
                action = self._create_database(action, db_path)
                action.result = f"DB neu erstellt (Datenverlust): {e}"
                action.status = RepairStatus.PARTIAL
            else:
                action.status = RepairStatus.FAILED
                action.result = f"Konnte nicht reparieren: {e}"

        return action

    def _repair_missing_tables(self, action: RepairAction, db_path: Path) -> RepairAction:
        """Erstellt fehlende Tabellen"""
        if db_path.name not in self.KNOWN_SCHEMAS:
            action.status = RepairStatus.FAILED
            action.result = "Kein Schema bekannt"
            return action

        backup = self._create_backup(db_path, "tables")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            created = []
            for table_name, create_sql in self.KNOWN_SCHEMAS[db_path.name].items():
                try:
                    cursor.execute(create_sql)
                    created.append(table_name)
                except sqlite3.OperationalError:
                    pass  # Tabelle existiert bereits

            conn.commit()
            conn.close()

            action.status = RepairStatus.SUCCESS
            action.result = f"Tabellen erstellt: {created}"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _repair_integrity(self, action: RepairAction, db_path: Path) -> RepairAction:
        """Versucht Integritätsprobleme zu beheben"""
        backup = self._create_backup(db_path, "integrity")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Versuche zu reparieren
            cursor.execute("VACUUM")
            cursor.execute("REINDEX")

            # Prüfe erneut
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]

            conn.close()

            if result == "ok":
                action.status = RepairStatus.SUCCESS
                action.result = "Integrität wiederhergestellt"
            else:
                action.status = RepairStatus.PARTIAL
                action.result = f"Teilweise repariert: {result}"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _create_database(self, action: RepairAction, db_path: Path) -> RepairAction:
        """Erstellt eine neue Datenbank mit bekanntem Schema"""
        if db_path.name not in self.KNOWN_SCHEMAS:
            action.status = RepairStatus.FAILED
            action.result = "Kein Schema bekannt für diese Datenbank"
            return action

        try:
            # Verzeichnis erstellen falls nötig
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            for table_name, create_sql in self.KNOWN_SCHEMAS[db_path.name].items():
                cursor.execute(create_sql)

            conn.commit()
            conn.close()

            action.status = RepairStatus.SUCCESS
            action.result = f"Datenbank {db_path.name} neu erstellt"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler beim Erstellen: {e}"

        return action


# ==================== CONFIG REPAIRER ====================

class ConfigRepairer(BaseRepairer):
    """Repariert und verwaltet Konfigurationsdateien"""

    # Standard-Konfigurationen
    DEFAULT_CONFIGS = {
        "holo_config.json": {
            "name": "Holo",
            "version": "2.0",
            "debug": False,
            "log_level": "INFO",
            "modules": {
                "brain": True,
                "memory": True,
                "skills": True,
                "discord": False
            },
            "paths": {
                "data": "./data",
                "logs": "./logs",
                "backups": "./.holo_backups"
            },
            "api": {
                "openai": "",
                "anthropic": ""
            }
        },
        "holo_settings.json": {
            "language": "de",
            "personality": "freundlich",
            "response_style": "ausführlich",
            "auto_learn": True,
            "memory_limit": 10000
        }
    }

    # Erforderliche Felder pro Config
    REQUIRED_FIELDS = {
        "holo_config.json": ["name", "version", "modules"],
        "holo_settings.json": ["language", "personality"]
    }

    def detect_issues(self) -> List[RepairAction]:
        """Erkennt Config-Probleme"""
        issues = []

        # Suche nach JSON und YAML Configs
        config_files = list(self.project_dir.glob("*.json")) + \
                       list(self.project_dir.glob("*.yaml")) + \
                       list(self.project_dir.glob("*.yml")) + \
                       list(self.project_dir.glob("config/*.json"))

        for config_path in config_files:
            if config_path.name.startswith('.'):
                continue

            # Prüfe auf Syntax-Fehler
            syntax_error = self._check_syntax(config_path)
            if syntax_error:
                issues.append(RepairAction(
                    id=f"config_syntax_{config_path.name}",
                    repair_type=RepairType.CONFIG,
                    target=str(config_path),
                    description=f"Syntax-Fehler in {config_path.name}: {syntax_error}",
                    severity=Severity.HIGH
                ))
                continue  # Keine weiteren Prüfungen bei Syntax-Fehlern

            # Prüfe auf fehlende Felder
            missing = self._check_required_fields(config_path)
            if missing:
                issues.append(RepairAction(
                    id=f"config_missing_{config_path.name}",
                    repair_type=RepairType.CONFIG,
                    target=str(config_path),
                    description=f"Fehlende Felder in {config_path.name}: {missing}",
                    severity=Severity.MEDIUM
                ))

            # Prüfe auf ungültige Werte
            invalid = self._check_invalid_values(config_path)
            if invalid:
                issues.append(RepairAction(
                    id=f"config_invalid_{config_path.name}",
                    repair_type=RepairType.CONFIG,
                    target=str(config_path),
                    description=f"Ungültige Werte in {config_path.name}: {invalid}",
                    severity=Severity.LOW
                ))

        # Prüfe auf fehlende wichtige Configs
        for config_name in self.DEFAULT_CONFIGS.keys():
            config_path = self.project_dir / config_name
            if not config_path.exists():
                issues.append(RepairAction(
                    id=f"config_create_{config_name}",
                    repair_type=RepairType.CONFIG,
                    target=str(config_path),
                    description=f"Wichtige Config {config_name} fehlt",
                    severity=Severity.HIGH
                ))

        return issues

    def repair(self, action: RepairAction) -> RepairAction:
        """Repariert ein Config-Problem"""
        action.status = RepairStatus.IN_PROGRESS
        action.attempts += 1
        config_path = Path(action.target)

        try:
            if "syntax" in action.id:
                return self._repair_syntax(action, config_path)
            elif "missing" in action.id and "config_missing" in action.id:
                return self._repair_missing_fields(action, config_path)
            elif "invalid" in action.id:
                return self._repair_invalid_values(action, config_path)
            elif "create" in action.id:
                return self._create_config(action, config_path)
            else:
                action.status = RepairStatus.FAILED
                action.result = "Unbekannter Reparaturtyp"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {str(e)}"

        return action

    def rollback(self, action: RepairAction) -> bool:
        """Stellt eine Config aus Backup wieder her"""
        if not action.rollback_data or "backup_path" not in action.rollback_data:
            return False

        try:
            backup_path = Path(action.rollback_data["backup_path"])
            target_path = Path(action.target)

            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
                return True
        except:
            pass

        return False

    def _check_syntax(self, config_path: Path) -> Optional[str]:
        """Prüft JSON/YAML Syntax"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if config_path.suffix == '.json':
                json.loads(content)
            elif config_path.suffix in ['.yaml', '.yml']:
                try:
                    import yaml
                    yaml.safe_load(content)
                except ImportError:
                    pass  # YAML nicht verfügbar

            return None
        except json.JSONDecodeError as e:
            return str(e)
        except Exception as e:
            return str(e)

    def _check_required_fields(self, config_path: Path) -> List[str]:
        """Prüft auf fehlende Pflichtfelder"""
        if config_path.name not in self.REQUIRED_FIELDS:
            return []

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            required = self.REQUIRED_FIELDS[config_path.name]
            missing = [f for f in required if f not in config]
            return missing
        except:
            return []

    def _check_invalid_values(self, config_path: Path) -> List[str]:
        """Prüft auf ungültige Werte"""
        invalid = []

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Typische Validierungen
            if "log_level" in config:
                if config["log_level"] not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                    invalid.append(f"log_level: {config['log_level']}")

            if "language" in config:
                if config["language"] not in ["de", "en", "es", "fr", "ja"]:
                    invalid.append(f"language: {config['language']}")

            # Prüfe auf leere Strings wo nicht erlaubt
            for key in ["name", "version"]:
                if key in config and not config[key]:
                    invalid.append(f"{key}: leer")

        except:
            pass

        return invalid

    def _repair_syntax(self, action: RepairAction, config_path: Path) -> RepairAction:
        """Repariert Syntax-Fehler in Config"""
        backup = self._create_backup(config_path, "syntax")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Häufige JSON-Fehler korrigieren
            fixed = content

            # Trailing commas entfernen
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)

            # Single quotes durch double quotes ersetzen
            fixed = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', fixed)

            # Fehlende Quotes um Keys
            fixed = re.sub(r'(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed)

            # Versuche zu parsen
            try:
                parsed = json.loads(fixed)

                # Speichern mit korrekter Formatierung
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed, f, indent=2, ensure_ascii=False)

                action.status = RepairStatus.SUCCESS
                action.result = "Syntax korrigiert"

            except json.JSONDecodeError:
                # Plan B: Mit Default ersetzen
                if config_path.name in self.DEFAULT_CONFIGS:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(self.DEFAULT_CONFIGS[config_path.name], f, indent=2)
                    action.status = RepairStatus.PARTIAL
                    action.result = "Mit Standard-Config ersetzt (Datenverlust möglich)"
                else:
                    action.status = RepairStatus.FAILED
                    action.result = "Syntax konnte nicht repariert werden"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _repair_missing_fields(self, action: RepairAction, config_path: Path) -> RepairAction:
        """Fügt fehlende Felder hinzu"""
        backup = self._create_backup(config_path, "fields")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Defaults hinzufügen
            if config_path.name in self.DEFAULT_CONFIGS:
                defaults = self.DEFAULT_CONFIGS[config_path.name]
                added = []

                for key, value in defaults.items():
                    if key not in config:
                        config[key] = value
                        added.append(key)

                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                action.status = RepairStatus.SUCCESS
                action.result = f"Felder hinzugefügt: {added}"
            else:
                action.status = RepairStatus.PARTIAL
                action.result = "Keine Standard-Werte bekannt"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _repair_invalid_values(self, action: RepairAction, config_path: Path) -> RepairAction:
        """Korrigiert ungültige Werte"""
        backup = self._create_backup(config_path, "values")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            fixed = []

            # Standard-Korrekturen
            if "log_level" in config:
                if config["log_level"] not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                    config["log_level"] = "INFO"
                    fixed.append("log_level -> INFO")

            if "language" in config:
                if config["language"] not in ["de", "en", "es", "fr", "ja"]:
                    config["language"] = "de"
                    fixed.append("language -> de")

            if fixed:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                action.status = RepairStatus.SUCCESS
                action.result = f"Korrigiert: {fixed}"
            else:
                action.status = RepairStatus.SUCCESS
                action.result = "Keine Korrekturen nötig"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _create_config(self, action: RepairAction, config_path: Path) -> RepairAction:
        """Erstellt eine neue Config mit Defaults"""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_path.name in self.DEFAULT_CONFIGS:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.DEFAULT_CONFIGS[config_path.name], f, indent=2, ensure_ascii=False)

                action.status = RepairStatus.SUCCESS
                action.result = f"Config {config_path.name} erstellt"
            else:
                # Leere Config erstellen
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)

                action.status = RepairStatus.PARTIAL
                action.result = "Leere Config erstellt (kein Schema bekannt)"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action


# ==================== MODULE REPAIRER ====================

class ModuleRepairer(BaseRepairer):
    """Repariert und verwaltet Python-Module"""

    def __init__(self, project_dir: Path, logger: logging.Logger):
        super().__init__(project_dir, logger)
        self._module_states: Dict[str, Dict] = {}
        self._restart_counts: Dict[str, int] = {}

    def detect_issues(self) -> List[RepairAction]:
        """Erkennt Modul-Probleme"""
        issues = []

        # Scanne alle Python-Dateien
        py_files = list(self.project_dir.glob("*.py"))

        for py_path in py_files:
            if py_path.name.startswith('__'):
                continue

            module_name = py_path.stem

            # Prüfe auf Import-Fehler
            import_error = self._check_import(py_path)
            if import_error:
                issues.append(RepairAction(
                    id=f"module_import_{module_name}",
                    repair_type=RepairType.MODULE,
                    target=str(py_path),
                    description=f"Import-Fehler in {module_name}: {import_error}",
                    severity=Severity.HIGH
                ))

            # Prüfe auf Syntax-Fehler
            syntax_error = self._check_syntax(py_path)
            if syntax_error:
                issues.append(RepairAction(
                    id=f"module_syntax_{module_name}",
                    repair_type=RepairType.MODULE,
                    target=str(py_path),
                    description=f"Syntax-Fehler in {module_name}: {syntax_error}",
                    severity=Severity.CRITICAL
                ))

            # Prüfe auf fehlende Dependencies
            missing_deps = self._check_dependencies(py_path)
            if missing_deps:
                issues.append(RepairAction(
                    id=f"module_deps_{module_name}",
                    repair_type=RepairType.DEPENDENCY,
                    target=str(py_path),
                    description=f"Fehlende Dependencies für {module_name}: {missing_deps}",
                    severity=Severity.MEDIUM
                ))

        return issues

    def repair(self, action: RepairAction) -> RepairAction:
        """Repariert ein Modul-Problem"""
        action.status = RepairStatus.IN_PROGRESS
        action.attempts += 1
        module_path = Path(action.target)

        try:
            if "import" in action.id:
                return self._repair_import(action, module_path)
            elif "syntax" in action.id:
                return self._repair_syntax(action, module_path)
            elif "deps" in action.id:
                return self._repair_dependencies(action, module_path)
            else:
                action.status = RepairStatus.FAILED
                action.result = "Unbekannter Reparaturtyp"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {str(e)}"

        return action

    def rollback(self, action: RepairAction) -> bool:
        """Stellt ein Modul aus Backup wieder her"""
        if not action.rollback_data or "backup_path" not in action.rollback_data:
            return False

        try:
            backup_path = Path(action.rollback_data["backup_path"])
            target_path = Path(action.target)

            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
                # Modul neu laden
                self._reload_module(target_path.stem)
                return True
        except:
            pass

        return False

    def restart_module(self, module_name: str) -> bool:
        """Startet ein Modul neu"""
        try:
            if module_name in sys.modules:
                # Modul entladen
                del sys.modules[module_name]

            # Modul neu laden
            importlib.import_module(module_name)

            self._restart_counts[module_name] = self._restart_counts.get(module_name, 0) + 1
            self.logger.info(f"Modul {module_name} neugestartet (#{self._restart_counts[module_name]})")
            return True

        except Exception as e:
            self.logger.error(f"Restart von {module_name} fehlgeschlagen: {e}")
            return False

    def _reload_module(self, module_name: str) -> bool:
        """Lädt ein Modul neu"""
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                return True
            else:
                importlib.import_module(module_name)
                return True
        except:
            return False

    def _check_import(self, py_path: Path) -> Optional[str]:
        """Prüft ob ein Modul importiert werden kann"""
        try:
            spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Nicht tatsächlich ausführen, nur prüfen
                return None
        except Exception as e:
            return str(e)
        return None

    def _check_syntax(self, py_path: Path) -> Optional[str]:
        """Prüft Python-Syntax"""
        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            return None
        except SyntaxError as e:
            return f"Zeile {e.lineno}: {e.msg}"
        except Exception as e:
            return str(e)

    def _check_dependencies(self, py_path: Path) -> List[str]:
        """Prüft auf fehlende Dependencies"""
        missing = []

        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Finde Imports
            import_pattern = r'^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            imports = re.findall(import_pattern, content, re.MULTILINE)

            # Standard-Bibliotheken ignorieren
            stdlib = {
                'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 're', 'ast',
                'logging', 'threading', 'subprocess', 'shutil', 'sqlite3', 'hashlib',
                'tempfile', 'importlib', 'collections', 'functools', 'itertools',
                'typing', 'dataclasses', 'enum', 'abc', 'copy', 'random', 'math',
                'socket', 'http', 'urllib', 'asyncio', 'concurrent', 'traceback'
            }

            for imp in imports:
                if imp in stdlib:
                    continue
                if imp.startswith('holo_'):
                    continue

                try:
                    importlib.import_module(imp)
                except ImportError:
                    missing.append(imp)

        except Exception as e:
            self.logger.debug(f"Dependency check fehlgeschlagen für {py_path}: {e}")

        return missing

    def _repair_import(self, action: RepairAction, module_path: Path) -> RepairAction:
        """Repariert Import-Probleme"""
        module_name = module_path.stem

        # Versuche Cache zu löschen und neu zu laden
        try:
            # Python Cache löschen
            pycache = module_path.parent / "__pycache__"
            if pycache.exists():
                for f in pycache.glob(f"{module_name}*.pyc"):
                    f.unlink()

            # Modul aus sys.modules entfernen
            to_remove = [k for k in sys.modules.keys() if k.startswith(module_name)]
            for k in to_remove:
                del sys.modules[k]

            # Versuche erneut zu importieren
            try:
                importlib.import_module(module_name)
                action.status = RepairStatus.SUCCESS
                action.result = "Modul-Cache geleert und neu geladen"
            except ImportError as e:
                # Vielleicht fehlende Dependency
                action.status = RepairStatus.PARTIAL
                action.result = f"Cache geleert, aber Import-Fehler bleibt: {e}"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _repair_syntax(self, action: RepairAction, module_path: Path) -> RepairAction:
        """Versucht einfache Syntax-Fehler zu beheben"""
        backup = self._create_backup(module_path, "syntax")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Parse-Fehler finden
            try:
                ast.parse(''.join(lines))
                action.status = RepairStatus.SUCCESS
                action.result = "Kein Syntax-Fehler gefunden"
                return action
            except SyntaxError as e:
                error_line = e.lineno - 1 if e.lineno else 0

            # Einfache Fixes versuchen
            fixed = False

            # Fix 1: Fehlende Doppelpunkte
            if error_line < len(lines):
                line = lines[error_line]
                if re.match(r'\s*(if|elif|else|for|while|def|class|try|except|finally|with).*[^:]\s*$', line):
                    lines[error_line] = line.rstrip() + ':\n'
                    fixed = True

            # Fix 2: Nicht geschlossene Klammern
            # (vereinfacht - nur offensichtliche Fälle)

            if fixed:
                with open(module_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                # Prüfe ob es jetzt funktioniert
                try:
                    ast.parse(''.join(lines))
                    action.status = RepairStatus.SUCCESS
                    action.result = "Syntax-Fehler behoben"
                except SyntaxError:
                    action.status = RepairStatus.PARTIAL
                    action.result = "Einige Fixes angewendet, aber noch Fehler vorhanden"
            else:
                action.status = RepairStatus.FAILED
                action.result = "Syntax-Fehler zu komplex für Auto-Fix"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _repair_dependencies(self, action: RepairAction, module_path: Path) -> RepairAction:
        """Installiert fehlende Dependencies"""
        # Extrahiere fehlende Deps aus der Beschreibung
        desc = action.description
        deps_match = re.search(r'\[(.*?)\]', desc)

        if not deps_match:
            action.status = RepairStatus.FAILED
            action.result = "Keine Dependencies in Beschreibung gefunden"
            return action

        deps = [d.strip().strip("'\"") for d in deps_match.group(1).split(',')]

        installed = []
        failed = []

        for dep in deps:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', dep],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    installed.append(dep)
                else:
                    failed.append(dep)
            except Exception as e:
                failed.append(f"{dep} ({e})")

        if failed:
            if installed:
                action.status = RepairStatus.PARTIAL
                action.result = f"Installiert: {installed}, Fehlgeschlagen: {failed}"
            else:
                action.status = RepairStatus.FAILED
                action.result = f"Installation fehlgeschlagen: {failed}"
        else:
            action.status = RepairStatus.SUCCESS
            action.result = f"Dependencies installiert: {installed}"

        return action


# ==================== CODE PATCH REPAIRER ====================

class CodePatchRepairer(BaseRepairer):
    """Wendet Code-Patches für bekannte Fehler an"""

    # Bekannte Fehlermuster und ihre Fixes
    KNOWN_PATCHES = {
        "missing_self": {
            "pattern": r"def\s+(\w+)\s*\(\s*\)",  # Methode ohne self
            "check": lambda m, ctx: ctx.get("in_class", False),
            "fix": lambda m: f"def {m.group(1)}(self)",
            "description": "Fehlender self Parameter in Methode"
        },
        "none_comparison": {
            "pattern": r"(\w+)\s*==\s*None",
            "fix": lambda m: f"{m.group(1)} is None",
            "description": "Verwende 'is None' statt '== None'"
        },
        "mutable_default": {
            "pattern": r"def\s+\w+\s*\([^)]*(\w+)\s*=\s*(\[\]|\{\})",
            "fix": lambda m: m.group(0).replace(m.group(2), "None"),
            "description": "Mutable Default-Argument"
        },
        "bare_except": {
            "pattern": r"except\s*:",
            "fix": lambda m: "except Exception:",
            "description": "Bare except sollte Exception spezifizieren"
        },
        "print_statement": {
            "pattern": r"^\s*print\s+([^(\n]+)$",
            "fix": lambda m: f"print({m.group(1)})",
            "description": "Python 2 print Statement"
        }
    }

    # Provisorische Workarounds
    WORKAROUNDS = {
        "import_error": {
            "pattern": r"^from\s+(\w+)\s+import",
            "workaround": "try:\n    {original}\nexcept ImportError:\n    pass  # Provisorischer Workaround",
            "description": "Import in try/except wrappen"
        },
        "attribute_error": {
            "pattern": r"(\w+)\.(\w+)",
            "workaround": "getattr({obj}, '{attr}', None)",
            "description": "Sichere Attribut-Zugriffe"
        }
    }

    def detect_issues(self) -> List[RepairAction]:
        """Erkennt Code-Probleme die gepatcht werden können"""
        issues = []

        py_files = list(self.project_dir.glob("*.py"))

        for py_path in py_files:
            if py_path.name.startswith('__'):
                continue

            try:
                with open(py_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for patch_id, patch in self.KNOWN_PATCHES.items():
                    matches = list(re.finditer(patch["pattern"], content, re.MULTILINE))
                    if matches:
                        issues.append(RepairAction(
                            id=f"patch_{patch_id}_{py_path.stem}",
                            repair_type=RepairType.CODE_PATCH,
                            target=str(py_path),
                            description=f"{patch['description']} in {py_path.name} ({len(matches)} Stellen)",
                            severity=Severity.LOW
                        ))

            except Exception as e:
                self.logger.debug(f"Patch-Scan fehlgeschlagen für {py_path}: {e}")

        return issues

    def repair(self, action: RepairAction) -> RepairAction:
        """Wendet einen Code-Patch an"""
        action.status = RepairStatus.IN_PROGRESS
        action.attempts += 1

        # Extrahiere patch_id aus action.id
        parts = action.id.split('_')
        if len(parts) < 3:
            action.status = RepairStatus.FAILED
            action.result = "Ungültige Action ID"
            return action

        patch_id = parts[1]

        if patch_id not in self.KNOWN_PATCHES:
            action.status = RepairStatus.FAILED
            action.result = f"Unbekannter Patch: {patch_id}"
            return action

        file_path = Path(action.target)
        backup = self._create_backup(file_path, f"patch_{patch_id}")
        if backup:
            action.rollback_data = {"backup_path": str(backup)}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            patch = self.KNOWN_PATCHES[patch_id]

            # Patch anwenden
            def replace_func(m):
                return patch["fix"](m)

            new_content = re.sub(patch["pattern"], replace_func, content, flags=re.MULTILINE)

            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                # Syntax prüfen
                try:
                    ast.parse(new_content)
                    action.status = RepairStatus.SUCCESS
                    action.result = f"Patch '{patch_id}' erfolgreich angewendet"
                except SyntaxError as e:
                    # Rollback
                    if backup:
                        shutil.copy2(backup, file_path)
                    action.status = RepairStatus.FAILED
                    action.result = f"Patch verursachte Syntax-Fehler: {e}"
            else:
                action.status = RepairStatus.SUCCESS
                action.result = "Keine Änderungen nötig"

        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def rollback(self, action: RepairAction) -> bool:
        """Macht einen Patch rückgängig"""
        if not action.rollback_data or "backup_path" not in action.rollback_data:
            return False

        try:
            backup_path = Path(action.rollback_data["backup_path"])
            target_path = Path(action.target)

            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
                return True
        except:
            pass

        return False

    def apply_workaround(self, error_type: str, context: Dict) -> Optional[str]:
        """Wendet einen provisorischen Workaround an"""
        if error_type not in self.WORKAROUNDS:
            return None

        workaround = self.WORKAROUNDS[error_type]

        try:
            original = context.get("original_code", "")
            if not original:
                return None

            # Workaround generieren
            result = workaround["workaround"].format(
                original=original,
                **context
            )

            return result
        except Exception as e:
            self.logger.error(f"Workaround fehlgeschlagen: {e}")
            return None


# ==================== FILESYSTEM REPAIRER ====================

class FilesystemRepairer(BaseRepairer):
    """Repariert Dateisystem-Probleme"""

    # Erforderliche Verzeichnisse
    REQUIRED_DIRS = [
        "data",
        "logs",
        "skills",
        "modules",
        ".holo_backups"
    ]

    def detect_issues(self) -> List[RepairAction]:
        """Erkennt Dateisystem-Probleme"""
        issues = []

        # Prüfe auf fehlende Verzeichnisse
        for dir_name in self.REQUIRED_DIRS:
            dir_path = self.project_dir / dir_name
            if not dir_path.exists():
                issues.append(RepairAction(
                    id=f"fs_mkdir_{dir_name}",
                    repair_type=RepairType.FILESYSTEM,
                    target=str(dir_path),
                    description=f"Verzeichnis {dir_name} fehlt",
                    severity=Severity.MEDIUM
                ))

        # Prüfe auf Berechtigungsprobleme
        for py_file in self.project_dir.glob("*.py"):
            if not os.access(py_file, os.R_OK):
                issues.append(RepairAction(
                    id=f"fs_perm_{py_file.name}",
                    repair_type=RepairType.PERMISSION,
                    target=str(py_file),
                    description=f"Keine Leserechte für {py_file.name}",
                    severity=Severity.HIGH
                ))

        # Prüfe auf beschädigte Symlinks
        for item in self.project_dir.iterdir():
            if item.is_symlink() and not item.exists():
                issues.append(RepairAction(
                    id=f"fs_symlink_{item.name}",
                    repair_type=RepairType.FILESYSTEM,
                    target=str(item),
                    description=f"Beschädigter Symlink: {item.name}",
                    severity=Severity.LOW
                ))

        return issues

    def repair(self, action: RepairAction) -> RepairAction:
        """Repariert ein Dateisystem-Problem"""
        action.status = RepairStatus.IN_PROGRESS
        action.attempts += 1

        try:
            if "mkdir" in action.id:
                return self._create_directory(action)
            elif "perm" in action.id:
                return self._fix_permissions(action)
            elif "symlink" in action.id:
                return self._remove_broken_symlink(action)
            else:
                action.status = RepairStatus.FAILED
                action.result = "Unbekannter Reparaturtyp"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {str(e)}"

        return action

    def rollback(self, action: RepairAction) -> bool:
        """Dateisystem-Änderungen sind schwer rückgängig zu machen"""
        return False

    def _create_directory(self, action: RepairAction) -> RepairAction:
        """Erstellt ein fehlendes Verzeichnis"""
        try:
            dir_path = Path(action.target)
            dir_path.mkdir(parents=True, exist_ok=True)

            action.status = RepairStatus.SUCCESS
            action.result = f"Verzeichnis {dir_path.name} erstellt"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _fix_permissions(self, action: RepairAction) -> RepairAction:
        """Korrigiert Dateiberechtigungen"""
        try:
            file_path = Path(action.target)

            # Versuche Leserechte zu setzen
            os.chmod(file_path, 0o644)

            if os.access(file_path, os.R_OK):
                action.status = RepairStatus.SUCCESS
                action.result = "Berechtigungen korrigiert"
            else:
                action.status = RepairStatus.FAILED
                action.result = "Berechtigungen konnten nicht korrigiert werden"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action

    def _remove_broken_symlink(self, action: RepairAction) -> RepairAction:
        """Entfernt beschädigte Symlinks"""
        try:
            link_path = Path(action.target)

            if link_path.is_symlink():
                link_path.unlink()
                action.status = RepairStatus.SUCCESS
                action.result = "Beschädigter Symlink entfernt"
            else:
                action.status = RepairStatus.SUCCESS
                action.result = "Kein Symlink gefunden"
        except Exception as e:
            action.status = RepairStatus.FAILED
            action.result = f"Fehler: {e}"

        return action


# ==================== MAIN SELF-REPAIR SYSTEM ====================

class HoloSelfRepair:
    """
    Hauptklasse für das Holo Self-Repair System.
    Koordiniert alle Repairer und führt automatische Reparaturen durch.
    """

    def __init__(
        self,
        project_dir: Path = None,
        holo_brain = None,
        live_monitor = None,
        auto_repair: bool = True,
        max_auto_repairs: int = 10
    ):
        self.project_dir = project_dir or Path(__file__).parent
        self.holo_brain = holo_brain
        self.live_monitor = live_monitor
        self.auto_repair = auto_repair
        self.max_auto_repairs = max_auto_repairs

        # Logger
        self.logger = logging.getLogger("HoloSelfRepair")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Repairer initialisieren
        self.repairers: Dict[RepairType, BaseRepairer] = {
            RepairType.DATABASE: DatabaseRepairer(self.project_dir, self.logger),
            RepairType.CONFIG: ConfigRepairer(self.project_dir, self.logger),
            RepairType.MODULE: ModuleRepairer(self.project_dir, self.logger),
            RepairType.DEPENDENCY: ModuleRepairer(self.project_dir, self.logger),
            RepairType.CODE_PATCH: CodePatchRepairer(self.project_dir, self.logger),
            RepairType.WORKAROUND: CodePatchRepairer(self.project_dir, self.logger),
            RepairType.FILESYSTEM: FilesystemRepairer(self.project_dir, self.logger),
            RepairType.PERMISSION: FilesystemRepairer(self.project_dir, self.logger),
        }

        # Status
        self._running = False
        self._repair_thread: Optional[threading.Thread] = None
        self._repair_history: List[RepairReport] = []
        self._pending_actions: List[RepairAction] = []
        self._last_scan: Optional[datetime] = None

        # Statistiken
        self.stats = {
            "total_repairs": 0,
            "successful_repairs": 0,
            "failed_repairs": 0,
            "rollbacks": 0
        }

    def start(self):
        """Startet den Self-Repair Daemon"""
        if self._running:
            return

        self._running = True
        self._repair_thread = threading.Thread(target=self._repair_loop, daemon=True)
        self._repair_thread.start()
        self.logger.info("Self-Repair System gestartet")

    def stop(self):
        """Stoppt den Self-Repair Daemon"""
        self._running = False
        if self._repair_thread:
            self._repair_thread.join(timeout=5)
        self.logger.info("Self-Repair System gestoppt")

    def _repair_loop(self):
        """Hauptschleife für automatische Reparaturen"""
        while self._running:
            try:
                if self.auto_repair:
                    # Scanne alle 5 Minuten
                    if not self._last_scan or \
                       (datetime.now() - self._last_scan).seconds > 300:
                        self.scan_and_repair()
                        self._last_scan = datetime.now()

                time.sleep(30)  # Check alle 30 Sekunden

            except Exception as e:
                self.logger.error(f"Fehler in Repair-Loop: {e}")
                time.sleep(60)

    def scan_all(self) -> List[RepairAction]:
        """Scannt auf alle bekannten Probleme"""
        all_issues = []

        for repair_type, repairer in self.repairers.items():
            try:
                issues = repairer.detect_issues()
                all_issues.extend(issues)
            except Exception as e:
                self.logger.error(f"Scan fehlgeschlagen für {repair_type.name}: {e}")

        # Nach Schweregrad sortieren
        all_issues.sort(key=lambda x: x.severity.value, reverse=True)

        self._pending_actions = all_issues
        return all_issues

    def scan_and_repair(self, max_repairs: int = None) -> RepairReport:
        """Scannt und repariert automatisch"""
        max_repairs = max_repairs or self.max_auto_repairs

        report = RepairReport()
        issues = self.scan_all()
        report.total_issues = len(issues)

        repairs_done = 0

        for action in issues:
            if repairs_done >= max_repairs:
                break

            # Nur kritische und hohe Priorität automatisch reparieren
            if action.severity.value < Severity.MEDIUM.value:
                continue

            repaired = self.repair(action)
            report.actions.append(repaired)

            if repaired.status == RepairStatus.SUCCESS:
                report.fixed += 1
                repairs_done += 1
            elif repaired.status == RepairStatus.PARTIAL:
                report.partial += 1
                repairs_done += 1
            else:
                report.failed += 1

        report.end_time = datetime.now()
        self._repair_history.append(report)

        # Statistiken aktualisieren
        self.stats["total_repairs"] += repairs_done
        self.stats["successful_repairs"] += report.fixed
        self.stats["failed_repairs"] += report.failed

        self.logger.info(
            f"Scan abgeschlossen: {report.total_issues} Probleme, "
            f"{report.fixed} behoben, {report.partial} teilweise, "
            f"{report.failed} fehlgeschlagen"
        )

        return report

    def repair(self, action: RepairAction) -> RepairAction:
        """Führt eine einzelne Reparatur durch"""
        repairer = self.repairers.get(action.repair_type)

        if not repairer:
            action.status = RepairStatus.FAILED
            action.result = f"Kein Repairer für {action.repair_type.name}"
            return action

        self.logger.info(f"Repariere: {action.description}")

        while action.attempts < action.max_attempts:
            action = repairer.repair(action)

            if action.status in [RepairStatus.SUCCESS, RepairStatus.PARTIAL]:
                break

            time.sleep(1)  # Kurze Pause zwischen Versuchen

        return action

    def rollback(self, action: RepairAction) -> bool:
        """Macht eine Reparatur rückgängig"""
        repairer = self.repairers.get(action.repair_type)

        if not repairer:
            return False

        success = repairer.rollback(action)

        if success:
            self.stats["rollbacks"] += 1
            action.status = RepairStatus.ROLLBACK

        return success

    def repair_database(self, db_name: str) -> RepairAction:
        """Repariert eine spezifische Datenbank"""
        db_path = self.project_dir / db_name

        action = RepairAction(
            id=f"manual_db_{db_name}",
            repair_type=RepairType.DATABASE,
            target=str(db_path),
            description=f"Manuelle Reparatur von {db_name}",
            severity=Severity.HIGH
        )

        return self.repair(action)

    def repair_config(self, config_name: str) -> RepairAction:
        """Repariert eine spezifische Config"""
        config_path = self.project_dir / config_name

        action = RepairAction(
            id=f"manual_config_{config_name}",
            repair_type=RepairType.CONFIG,
            target=str(config_path),
            description=f"Manuelle Reparatur von {config_name}",
            severity=Severity.HIGH
        )

        return self.repair(action)

    def restart_module(self, module_name: str) -> bool:
        """Startet ein Modul neu"""
        module_repairer = self.repairers.get(RepairType.MODULE)
        if isinstance(module_repairer, ModuleRepairer):
            return module_repairer.restart_module(module_name)
        return False

    def apply_workaround(self, error_type: str, context: Dict) -> Optional[str]:
        """Wendet einen provisorischen Workaround an"""
        code_repairer = self.repairers.get(RepairType.CODE_PATCH)
        if isinstance(code_repairer, CodePatchRepairer):
            return code_repairer.apply_workaround(error_type, context)
        return None

    def get_status(self) -> Dict:
        """Gibt den aktuellen Status zurück"""
        return {
            "running": self._running,
            "auto_repair": self.auto_repair,
            "pending_issues": len(self._pending_actions),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "stats": self.stats,
            "history_count": len(self._repair_history)
        }

    def get_pending_issues(self) -> List[Dict]:
        """Gibt alle bekannten Probleme zurück"""
        return [
            {
                "id": a.id,
                "type": a.repair_type.name,
                "target": a.target,
                "description": a.description,
                "severity": a.severity.name,
                "status": a.status.value
            }
            for a in self._pending_actions
        ]

    def get_repair_history(self, limit: int = 10) -> List[Dict]:
        """Gibt die letzten Reparatur-Reports zurück"""
        return [r.to_dict() for r in self._repair_history[-limit:]]

    def generate_health_report(self) -> str:
        """Generiert einen Gesundheitsbericht"""
        issues = self.scan_all()

        report = ["=" * 50]
        report.append("HOLO SELF-REPAIR HEALTH REPORT")
        report.append(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)

        # Übersicht
        critical = len([i for i in issues if i.severity == Severity.CRITICAL])
        high = len([i for i in issues if i.severity == Severity.HIGH])
        medium = len([i for i in issues if i.severity == Severity.MEDIUM])
        low = len([i for i in issues if i.severity == Severity.LOW])

        report.append(f"\nGefundene Probleme: {len(issues)}")
        report.append(f"  - KRITISCH: {critical}")
        report.append(f"  - HOCH:     {high}")
        report.append(f"  - MITTEL:   {medium}")
        report.append(f"  - NIEDRIG:  {low}")

        # Statistiken
        report.append(f"\nReparatur-Statistiken:")
        report.append(f"  - Gesamt:         {self.stats['total_repairs']}")
        report.append(f"  - Erfolgreich:    {self.stats['successful_repairs']}")
        report.append(f"  - Fehlgeschlagen: {self.stats['failed_repairs']}")
        report.append(f"  - Rollbacks:      {self.stats['rollbacks']}")

        # Details
        if issues:
            report.append("\nProblem-Details:")
            for issue in issues[:10]:  # Max 10 anzeigen
                report.append(f"\n  [{issue.severity.name}] {issue.repair_type.name}")
                report.append(f"  Ziel: {issue.target}")
                report.append(f"  {issue.description}")

        report.append("\n" + "=" * 50)

        return "\n".join(report)

    def can_self_repair(self, error: Exception, context: Dict = None) -> Tuple[bool, str]:
        """
        Prüft ob ein Fehler automatisch repariert werden kann.
        Gibt (kann_reparieren, beschreibung) zurück.
        """
        error_type = type(error).__name__
        error_msg = str(error)
        context = context or {}

        # Datenbank-Fehler
        if "database" in error_msg.lower() or "sqlite" in error_msg.lower():
            return True, "Datenbank-Fehler kann mit DB-Recovery repariert werden"

        # Import-Fehler
        if error_type == "ImportError" or error_type == "ModuleNotFoundError":
            return True, "Import-Fehler kann durch Dependency-Installation behoben werden"

        # Config-Fehler
        if "config" in error_msg.lower() or "json" in error_msg.lower():
            return True, "Config-Fehler kann durch Reset auf Defaults behoben werden"

        # Permissions
        if "permission" in error_msg.lower() or "access" in error_msg.lower():
            return True, "Berechtigungsfehler kann durch chmod behoben werden"

        # FileNotFound
        if error_type == "FileNotFoundError":
            if "data" in error_msg or "log" in error_msg:
                return True, "Fehlende Verzeichnisse/Dateien können erstellt werden"

        # Syntax-Fehler in bekannten Mustern
        if error_type == "SyntaxError":
            return True, "Einfache Syntax-Fehler können automatisch korrigiert werden"

        return False, "Fehler kann nicht automatisch repariert werden"

    async def auto_heal(self, error: Exception, context: Dict = None) -> Tuple[bool, str]:
        """
        Versucht einen Fehler automatisch zu heilen.
        Async für Integration mit anderen Systemen.
        """
        can_repair, description = self.can_self_repair(error, context)

        if not can_repair:
            return False, description

        error_type = type(error).__name__
        error_msg = str(error)
        context = context or {}

        try:
            # Spezifische Reparaturen basierend auf Fehlertyp
            if "database" in error_msg.lower() or "sqlite" in error_msg.lower():
                # Datenbank reparieren
                issues = self.repairers[RepairType.DATABASE].detect_issues()
                for issue in issues:
                    result = self.repair(issue)
                    if result.status == RepairStatus.SUCCESS:
                        return True, f"Datenbank repariert: {result.result}"

            elif error_type in ["ImportError", "ModuleNotFoundError"]:
                # Dependencies installieren
                module_name = str(error).split("'")[1] if "'" in str(error) else ""
                if module_name:
                    action = RepairAction(
                        id=f"auto_dep_{module_name}",
                        repair_type=RepairType.DEPENDENCY,
                        target=module_name,
                        description=f"Auto-Install {module_name}",
                        severity=Severity.HIGH
                    )
                    result = self.repair(action)
                    return result.status == RepairStatus.SUCCESS, result.result or ""

            elif "config" in error_msg.lower():
                # Config reparieren
                issues = self.repairers[RepairType.CONFIG].detect_issues()
                for issue in issues:
                    result = self.repair(issue)
                    if result.status == RepairStatus.SUCCESS:
                        return True, f"Config repariert: {result.result}"

            elif error_type == "FileNotFoundError":
                # Verzeichnis/Datei erstellen
                issues = self.repairers[RepairType.FILESYSTEM].detect_issues()
                for issue in issues:
                    result = self.repair(issue)
                    if result.status == RepairStatus.SUCCESS:
                        return True, f"Dateisystem repariert: {result.result}"

            # Allgemeiner Scan und Repair
            report = self.scan_and_repair(max_repairs=5)
            if report.fixed > 0:
                return True, f"Auto-Repair: {report.fixed} Probleme behoben"

        except Exception as heal_error:
            self.logger.error(f"Auto-Heal fehlgeschlagen: {heal_error}")
            return False, f"Auto-Heal fehlgeschlagen: {heal_error}"

        return False, "Keine passende Reparatur gefunden"


# ==================== FACTORY FUNCTION ====================

def create_self_repair(
    project_dir: Path = None,
    holo_brain = None,
    live_monitor = None,
    auto_start: bool = True,
    auto_repair: bool = True
) -> HoloSelfRepair:
    """
    Factory-Funktion zum Erstellen des Self-Repair Systems.

    Args:
        project_dir: Projektverzeichnis
        holo_brain: HoloBrain-Instanz
        live_monitor: HoloLiveMonitor-Instanz
        auto_start: Automatisch starten
        auto_repair: Automatische Reparaturen aktivieren

    Returns:
        HoloSelfRepair-Instanz
    """
    repair_system = HoloSelfRepair(
        project_dir=project_dir,
        holo_brain=holo_brain,
        live_monitor=live_monitor,
        auto_repair=auto_repair
    )

    if auto_start:
        repair_system.start()

    return repair_system


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    print("=" * 60)
    print("HOLO SELF-REPAIR SYSTEM - STANDALONE TEST")
    print("=" * 60)

    # System erstellen
    repair = create_self_repair(auto_start=False, auto_repair=False)

    # Health Report
    print("\n" + repair.generate_health_report())

    # Interaktiver Modus
    print("\n" + "-" * 60)
    print("Befehle:")
    print("  scan    - Scanne auf Probleme")
    print("  repair  - Scanne und repariere automatisch")
    print("  status  - Zeige Status")
    print("  db      - Zeige Datenbank-Probleme")
    print("  config  - Zeige Config-Probleme")
    print("  quit    - Beenden")
    print("-" * 60)

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd == "quit":
                break
            elif cmd == "scan":
                issues = repair.scan_all()
                print(f"\nGefunden: {len(issues)} Probleme")
                for i in issues[:10]:
                    print(f"  [{i.severity.name}] {i.description}")
            elif cmd == "repair":
                report = repair.scan_and_repair()
                print(f"\nReparatur-Bericht:")
                print(f"  Gesamt: {report.total_issues}")
                print(f"  Behoben: {report.fixed}")
                print(f"  Teilweise: {report.partial}")
                print(f"  Fehlgeschlagen: {report.failed}")
            elif cmd == "status":
                status = repair.get_status()
                print(f"\nStatus: {json.dumps(status, indent=2)}")
            elif cmd == "db":
                db_repairer = repair.repairers[RepairType.DATABASE]
                issues = db_repairer.detect_issues()
                print(f"\nDatenbank-Probleme: {len(issues)}")
                for i in issues:
                    print(f"  - {i.description}")
            elif cmd == "config":
                cfg_repairer = repair.repairers[RepairType.CONFIG]
                issues = cfg_repairer.detect_issues()
                print(f"\nConfig-Probleme: {len(issues)}")
                for i in issues:
                    print(f"  - {i.description}")
            else:
                print("Unbekannter Befehl")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Fehler: {e}")

    print("\nSelf-Repair System beendet.")
