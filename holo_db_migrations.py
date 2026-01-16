"""
Holocloude Database Migration System
=====================================

Einfaches aber robustes Migrationssystem fuer SQLite-Datenbanken.

Features:
- Automatische Schema-Versionierung
- Vorwaerts-Migrationen
- Rollback-Unterstuetzung (optional)
- Transaktionssicherheit
- Logging aller Migrationen

Verwendung:
    from holo_db_migrations import MigrationManager, Migration

    mgr = MigrationManager("path/to/db.sqlite")
    mgr.register(Migration(
        version=1,
        name="add_user_preferences",
        up="ALTER TABLE users ADD COLUMN preferences TEXT",
        down="ALTER TABLE users DROP COLUMN preferences"
    ))
    mgr.migrate()  # Fuehrt alle ausstehenden Migrationen aus
"""

import os
import sqlite3
import logging
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Union, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """
    Repraesentiert eine einzelne Datenbank-Migration.

    Attributes:
        version: Eindeutige Versionsnummer (aufsteigend)
        name: Beschreibender Name der Migration
        up: SQL oder Callable fuer Vorwaerts-Migration
        down: SQL oder Callable fuer Rueckwaerts-Migration (optional)
        checksum: Automatisch berechneter Hash des up-SQL
    """
    version: int
    name: str
    up: Union[str, Callable[[sqlite3.Connection], None]]
    down: Optional[Union[str, Callable[[sqlite3.Connection], None]]] = None
    checksum: str = field(default="", init=False)

    def __post_init__(self):
        # Berechne Checksum fuer Integritaetspruefung
        if isinstance(self.up, str):
            self.checksum = hashlib.md5(self.up.encode()).hexdigest()[:8]
        else:
            self.checksum = hashlib.md5(self.up.__name__.encode()).hexdigest()[:8]


class MigrationError(Exception):
    """Fehler waehrend der Migration."""
    pass


class MigrationManager:
    """
    Verwaltet Datenbank-Migrationen fuer eine SQLite-Datenbank.

    Beispiel:
        mgr = MigrationManager("holocloude.db")
        mgr.register(Migration(1, "initial", "CREATE TABLE ..."))
        mgr.register(Migration(2, "add_index", "CREATE INDEX ..."))
        mgr.migrate()
    """

    SCHEMA_TABLE = "_schema_migrations"

    def __init__(self, db_path: str):
        """
        Initialisiert den MigrationManager.

        Args:
            db_path: Pfad zur SQLite-Datenbank
        """
        self.db_path = db_path
        self.migrations: Dict[int, Migration] = {}
        self._ensure_schema_table()

    def _get_connection(self) -> sqlite3.Connection:
        """Erstellt eine neue Datenbankverbindung."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema_table(self):
        """Erstellt die Schema-Migrations-Tabelle falls nicht vorhanden."""
        # Pruefe ob DB-Datei existiert
        if not os.path.exists(self.db_path):
            # Erstelle Verzeichnis falls noetig
            os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)

        with self._get_connection() as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.SCHEMA_TABLE} (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TEXT NOT NULL,
                    execution_time_ms INTEGER,
                    success INTEGER DEFAULT 1
                )
            """)
            conn.commit()

    def register(self, migration: Migration) -> "MigrationManager":
        """
        Registriert eine neue Migration.

        Args:
            migration: Die zu registrierende Migration

        Returns:
            Self fuer Method-Chaining
        """
        if migration.version in self.migrations:
            raise MigrationError(
                f"Migration Version {migration.version} bereits registriert"
            )
        self.migrations[migration.version] = migration
        return self

    def register_many(self, migrations: List[Migration]) -> "MigrationManager":
        """Registriert mehrere Migrationen auf einmal."""
        for m in migrations:
            self.register(m)
        return self

    def get_current_version(self) -> int:
        """Gibt die aktuelle Schema-Version zurueck."""
        with self._get_connection() as conn:
            result = conn.execute(f"""
                SELECT MAX(version) as version
                FROM {self.SCHEMA_TABLE}
                WHERE success = 1
            """).fetchone()
            return result["version"] or 0

    def get_pending_migrations(self) -> List[Migration]:
        """Gibt alle ausstehenden Migrationen zurueck."""
        current = self.get_current_version()
        pending = [
            m for v, m in sorted(self.migrations.items())
            if v > current
        ]
        return pending

    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Gibt alle angewandten Migrationen zurueck."""
        with self._get_connection() as conn:
            rows = conn.execute(f"""
                SELECT version, name, checksum, applied_at, execution_time_ms, success
                FROM {self.SCHEMA_TABLE}
                ORDER BY version
            """).fetchall()
            return [dict(row) for row in rows]

    def _execute_migration(self, conn: sqlite3.Connection, migration: Migration):
        """Fuehrt eine einzelne Migration aus."""
        if isinstance(migration.up, str):
            # SQL-String ausfuehren (kann mehrere Statements enthalten)
            conn.executescript(migration.up)
        else:
            # Callable ausfuehren
            migration.up(conn)

    def _execute_rollback(self, conn: sqlite3.Connection, migration: Migration):
        """Fuehrt Rollback einer Migration aus."""
        if migration.down is None:
            raise MigrationError(
                f"Migration {migration.version} ({migration.name}) hat kein Rollback definiert"
            )

        if isinstance(migration.down, str):
            conn.executescript(migration.down)
        else:
            migration.down(conn)

    def migrate(self, target_version: Optional[int] = None) -> int:
        """
        Fuehrt alle ausstehenden Migrationen aus.

        Args:
            target_version: Optionale Zielversion (None = neueste)

        Returns:
            Anzahl der ausgefuehrten Migrationen
        """
        pending = self.get_pending_migrations()

        if target_version is not None:
            pending = [m for m in pending if m.version <= target_version]

        if not pending:
            logger.info(f"[{self.db_path}] Keine ausstehenden Migrationen")
            return 0

        logger.info(
            f"[{self.db_path}] {len(pending)} Migration(en) ausstehend: "
            f"{', '.join(m.name for m in pending)}"
        )

        executed = 0
        for migration in pending:
            start_time = datetime.now()

            try:
                with self._get_connection() as conn:
                    logger.info(
                        f"[{self.db_path}] Migration {migration.version}: "
                        f"{migration.name} wird ausgefuehrt..."
                    )

                    # Migration ausfuehren
                    self._execute_migration(conn, migration)

                    # Erfolg protokollieren
                    execution_time = int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    )
                    conn.execute(f"""
                        INSERT INTO {self.SCHEMA_TABLE}
                        (version, name, checksum, applied_at, execution_time_ms, success)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (
                        migration.version,
                        migration.name,
                        migration.checksum,
                        datetime.now().isoformat(),
                        execution_time
                    ))
                    conn.commit()

                    logger.info(
                        f"[{self.db_path}] Migration {migration.version}: "
                        f"{migration.name} erfolgreich ({execution_time}ms)"
                    )
                    executed += 1

            except Exception as e:
                logger.error(
                    f"[{self.db_path}] Migration {migration.version} fehlgeschlagen: {e}"
                )
                raise MigrationError(
                    f"Migration {migration.version} ({migration.name}) fehlgeschlagen: {e}"
                ) from e

        return executed

    def rollback(self, steps: int = 1) -> int:
        """
        Macht die letzten N Migrationen rueckgaengig.

        Args:
            steps: Anzahl der Migrationen zum Zurueckrollen

        Returns:
            Anzahl der zurueckgerollten Migrationen
        """
        applied = self.get_applied_migrations()
        if not applied:
            logger.info(f"[{self.db_path}] Keine Migrationen zum Zurueckrollen")
            return 0

        # Letzte N erfolgreiche Migrationen
        to_rollback = [
            a for a in reversed(applied)
            if a["success"]
        ][:steps]

        rolled_back = 0
        for record in to_rollback:
            version = record["version"]

            if version not in self.migrations:
                raise MigrationError(
                    f"Migration {version} nicht registriert - Rollback nicht moeglich"
                )

            migration = self.migrations[version]

            try:
                with self._get_connection() as conn:
                    logger.info(
                        f"[{self.db_path}] Rollback Migration {version}: {migration.name}"
                    )

                    self._execute_rollback(conn, migration)

                    # Eintrag entfernen
                    conn.execute(f"""
                        DELETE FROM {self.SCHEMA_TABLE} WHERE version = ?
                    """, (version,))
                    conn.commit()

                    logger.info(
                        f"[{self.db_path}] Rollback {version} erfolgreich"
                    )
                    rolled_back += 1

            except Exception as e:
                logger.error(
                    f"[{self.db_path}] Rollback {version} fehlgeschlagen: {e}"
                )
                raise MigrationError(
                    f"Rollback {version} fehlgeschlagen: {e}"
                ) from e

        return rolled_back

    def verify_integrity(self) -> bool:
        """
        Prueft die Integritaet der angewandten Migrationen.

        Returns:
            True wenn alle Checksums uebereinstimmen
        """
        applied = self.get_applied_migrations()

        for record in applied:
            version = record["version"]
            if version not in self.migrations:
                logger.warning(
                    f"[{self.db_path}] Migration {version} angewandt aber nicht registriert"
                )
                continue

            migration = self.migrations[version]
            if migration.checksum != record["checksum"]:
                logger.error(
                    f"[{self.db_path}] Migration {version} Checksum stimmt nicht ueberein! "
                    f"Erwartet: {migration.checksum}, Gefunden: {record['checksum']}"
                )
                return False

        return True

    def status(self) -> Dict[str, Any]:
        """Gibt den aktuellen Migrationsstatus zurueck."""
        return {
            "database": self.db_path,
            "current_version": self.get_current_version(),
            "latest_version": max(self.migrations.keys()) if self.migrations else 0,
            "pending_count": len(self.get_pending_migrations()),
            "applied_count": len(self.get_applied_migrations()),
            "integrity_ok": self.verify_integrity()
        }


# =============================================================================
# STANDARD-MIGRATIONEN FUER HOLOCLOUDE
# =============================================================================

def get_holocloude_migrations() -> List[Migration]:
    """
    Gibt die Standard-Migrationen fuer Holocloude zurueck.

    Diese Liste sollte erweitert werden, wenn Schema-Aenderungen noetig sind.
    Neue Migrationen immer am Ende mit hoeherer Versionsnummer hinzufuegen!
    """
    return [
        # Migration 1: Basis-Indizes fuer Performance
        Migration(
            version=1,
            name="add_performance_indexes",
            up="""
                -- Indizes fuer haeufig abgefragte Spalten
                CREATE INDEX IF NOT EXISTS idx_episodes_timestamp
                    ON episodes(timestamp);
                CREATE INDEX IF NOT EXISTS idx_emotions_timestamp
                    ON emotional_states(timestamp);
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
                    ON conversations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_knowledge_category
                    ON knowledge_facts(category);
            """,
            down="""
                DROP INDEX IF EXISTS idx_episodes_timestamp;
                DROP INDEX IF EXISTS idx_emotions_timestamp;
                DROP INDEX IF EXISTS idx_conversations_timestamp;
                DROP INDEX IF EXISTS idx_knowledge_category;
            """
        ),

        # Migration 2: Schema-Metadaten Tabelle
        Migration(
            version=2,
            name="add_schema_metadata",
            up="""
                CREATE TABLE IF NOT EXISTS _schema_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                );
                INSERT OR REPLACE INTO _schema_metadata (key, value, updated_at)
                VALUES ('schema_version', '15.1', datetime('now'));
                INSERT OR REPLACE INTO _schema_metadata (key, value, updated_at)
                VALUES ('created_at', datetime('now'), datetime('now'));
            """,
            down="DROP TABLE IF EXISTS _schema_metadata;"
        ),

        # Migration 3: Audit-Log Tabelle
        Migration(
            version=3,
            name="add_audit_log",
            up="""
                CREATE TABLE IF NOT EXISTS _audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    table_name TEXT,
                    record_id TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    user_context TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON _audit_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_table ON _audit_log(table_name);
            """,
            down="DROP TABLE IF EXISTS _audit_log;"
        ),

        # Migration 4: Health-Check Tabelle
        Migration(
            version=4,
            name="add_health_tracking",
            up="""
                CREATE TABLE IF NOT EXISTS _health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    check_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time_ms INTEGER,
                    details TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_health_timestamp ON _health_checks(timestamp);
            """,
            down="DROP TABLE IF EXISTS _health_checks;"
        ),
    ]


def run_all_migrations(data_dir: str = "data") -> Dict[str, Any]:
    """
    Fuehrt alle Migrationen fuer alle Holocloude-Datenbanken aus.

    Args:
        data_dir: Verzeichnis mit den Datenbanken

    Returns:
        Status-Dict mit Ergebnissen pro Datenbank
    """
    results = {}
    migrations = get_holocloude_migrations()

    # Finde alle .db Dateien
    db_files = list(Path(data_dir).glob("*.db"))

    if not db_files:
        logger.info(f"Keine Datenbanken in {data_dir} gefunden")
        return {"status": "no_databases"}

    for db_path in db_files:
        db_name = db_path.name
        try:
            mgr = MigrationManager(str(db_path))
            mgr.register_many(migrations)

            executed = mgr.migrate()
            status = mgr.status()

            results[db_name] = {
                "status": "ok",
                "executed": executed,
                **status
            }

        except Exception as e:
            logger.error(f"Migration fuer {db_name} fehlgeschlagen: {e}")
            results[db_name] = {
                "status": "error",
                "error": str(e)
            }

    return results


# =============================================================================
# CLI-INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    parser = argparse.ArgumentParser(description="Holocloude DB Migration Tool")
    parser.add_argument("command", choices=["migrate", "status", "rollback"],
                        help="Auszufuehrender Befehl")
    parser.add_argument("--db", help="Spezifische Datenbank (optional)")
    parser.add_argument("--data-dir", default="data", help="Datenverzeichnis")
    parser.add_argument("--steps", type=int, default=1,
                        help="Anzahl Rollback-Schritte")

    args = parser.parse_args()

    if args.command == "migrate":
        results = run_all_migrations(args.data_dir)
        print("\n=== Migration Results ===")
        for db, status in results.items():
            print(f"{db}: {status}")

    elif args.command == "status":
        migrations = get_holocloude_migrations()
        for db_path in Path(args.data_dir).glob("*.db"):
            mgr = MigrationManager(str(db_path))
            mgr.register_many(migrations)
            print(f"\n{db_path.name}:")
            print(f"  {mgr.status()}")

    elif args.command == "rollback":
        if not args.db:
            print("--db erforderlich fuer Rollback")
        else:
            mgr = MigrationManager(args.db)
            mgr.register_many(get_holocloude_migrations())
            rolled = mgr.rollback(args.steps)
            print(f"Rolled back {rolled} migration(s)")
