#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      HOLO SKILL SYSTEM v1.0                                  ║
║              Dynamisches Skill Discovery & Execution für Holo                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                    ║
║  • Automatische Skill-Erkennung aus skills/ Ordner                           ║
║  • Intelligente Skill-Auswahl basierend auf User-Anfrage                     ║
║  • Skill-Learning (welche Skills funktionieren gut)                          ║
║  • Nahtlose Integration mit pi_control SkillManager                          ║
║  • Persistente Skill-Metadaten in HoloDatabaseManager                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import importlib.util
import hashlib
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

# Logging
logger = logging.getLogger("holo.skills")

# ============================================================================
# SKILL RESULT (falls nicht von pi_control importiert)
# ============================================================================

@dataclass
class HoloSkillResult:
    """Ergebnis einer Skill-Ausführung"""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    skill_name: str = ""
    execution_time: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "metadata": self.metadata,
            "skill_name": self.skill_name,
            "execution_time": self.execution_time
        }


# ============================================================================
# SKILL INFO (Metadaten über einen Skill)
# ============================================================================

@dataclass
class SkillInfo:
    """Informationen über einen Skill für Holo's Verständnis"""
    name: str
    description: str
    keywords: List[str]
    capabilities: List[str]
    examples: List[str]
    category: str
    enabled: bool
    holo_compatible: bool
    success_rate: float = 0.0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    learned_patterns: List[str] = field(default_factory=list)

    def matches_request(self, request: str) -> float:
        """Berechnet wie gut dieser Skill zur Anfrage passt"""
        if not self.keywords:
            return 0.0

        request_lower = request.lower()
        matches = sum(1 for kw in self.keywords if kw.lower() in request_lower)

        if matches == 0:
            # Prüfe gelernte Patterns
            for pattern in self.learned_patterns:
                if pattern.lower() in request_lower:
                    return 0.5

            return 0.0

        confidence = min(0.3 + (matches * 0.2), 0.95)
        return confidence

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "capabilities": self.capabilities,
            "examples": self.examples,
            "category": self.category,
            "enabled": self.enabled,
            "holo_compatible": self.holo_compatible,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "learned_patterns": self.learned_patterns
        }


# ============================================================================
# HOLO SKILL BRIDGE - Verbindung zu pi_control oder lokal
# ============================================================================

# ============================================================================
# SKILL WATCHER - Automatische Erkennung von Änderungen
# ============================================================================

class SkillWatcher:
    """
    Überwacht den Skills-Ordner auf Änderungen.
    Nutzt Hash-Vergleich um neue/geänderte/gelöschte Skills zu erkennen.
    """

    def __init__(self, skills_dir: Path, on_change_callback: Callable = None,
                 check_interval: float = 30.0):
        """
        Args:
            skills_dir: Pfad zum skills/ Ordner
            on_change_callback: Wird aufgerufen wenn Änderungen erkannt werden
            check_interval: Prüf-Intervall in Sekunden (default: 30s)
        """
        self.skills_dir = skills_dir
        self.on_change = on_change_callback
        self.check_interval = check_interval

        # Hash-State
        self._file_hashes: Dict[str, str] = {}
        self._folder_hash: str = ""

        # Thread-Control
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Initial hash berechnen
        self._update_hashes()

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Berechnet MD5-Hash einer Datei"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _calculate_folder_hash(self) -> str:
        """
        Berechnet einen kombinierten Hash des gesamten Ordners.
        Berücksichtigt: Dateinamen, Größen, Änderungszeiten
        """
        if not self.skills_dir.exists():
            return ""

        hash_input = []
        for file_path in sorted(self.skills_dir.glob("*.py")):
            if file_path.name.startswith("__"):
                continue
            try:
                stat = file_path.stat()
                hash_input.append(f"{file_path.name}:{stat.st_size}:{stat.st_mtime}")
            except Exception:
                continue

        combined = "|".join(hash_input)
        return hashlib.md5(combined.encode()).hexdigest()

    def _update_hashes(self) -> Dict[str, str]:
        """Aktualisiert alle Hashes und gibt die alten zurück"""
        old_hashes = self._file_hashes.copy()
        self._file_hashes = {}

        if self.skills_dir.exists():
            for file_path in self.skills_dir.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                self._file_hashes[file_path.name] = self._calculate_file_hash(file_path)

        self._folder_hash = self._calculate_folder_hash()
        return old_hashes

    def check_for_changes(self) -> Dict[str, List[str]]:
        """
        Prüft auf Änderungen im Skills-Ordner.

        Returns:
            Dict mit {"added": [...], "modified": [...], "removed": [...]}
        """
        old_hashes = self._file_hashes.copy()
        old_folder_hash = self._folder_hash

        self._update_hashes()

        # Schneller Check: Hat sich der Ordner-Hash geändert?
        if self._folder_hash == old_folder_hash:
            return {"added": [], "modified": [], "removed": []}

        # Detaillierte Änderungen ermitteln
        changes = {
            "added": [],
            "modified": [],
            "removed": []
        }

        current_files = set(self._file_hashes.keys())
        old_files = set(old_hashes.keys())

        # Neue Dateien
        changes["added"] = list(current_files - old_files)

        # Gelöschte Dateien
        changes["removed"] = list(old_files - current_files)

        # Geänderte Dateien
        for filename in current_files & old_files:
            if self._file_hashes[filename] != old_hashes.get(filename):
                changes["modified"].append(filename)

        return changes

    def has_changes(self) -> bool:
        """Schneller Check ob Änderungen vorliegen"""
        new_folder_hash = self._calculate_folder_hash()
        return new_folder_hash != self._folder_hash

    def start_watching(self):
        """Startet den Watcher-Thread"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info(f"👁️ SkillWatcher gestartet (Intervall: {self.check_interval}s)")

    def stop_watching(self):
        """Stoppt den Watcher-Thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("👁️ SkillWatcher gestoppt")

    def _watch_loop(self):
        """Hauptschleife des Watchers"""
        while self._running:
            try:
                changes = self.check_for_changes()

                if any(changes.values()):
                    logger.info(f"🔄 Skill-Änderungen erkannt: "
                               f"+{len(changes['added'])} "
                               f"~{len(changes['modified'])} "
                               f"-{len(changes['removed'])}")

                    if self.on_change:
                        try:
                            self.on_change(changes)
                        except Exception as e:
                            logger.error(f"Fehler im Change-Callback: {e}")

            except Exception as e:
                logger.error(f"SkillWatcher Fehler: {e}")

            time.sleep(self.check_interval)

    def get_status(self) -> Dict:
        """Gibt den Status des Watchers zurück"""
        return {
            "running": self._running,
            "skills_dir": str(self.skills_dir),
            "tracked_files": len(self._file_hashes),
            "folder_hash": self._folder_hash[:8] + "...",
            "check_interval": self.check_interval
        }


class HoloSkillBridge:
    """
    Brücke zwischen Holo und dem Skill-System.
    Kann entweder direkt auf SkillManager zugreifen (wenn lokal)
    oder über API (wenn pi_control remote läuft).
    """

    def __init__(self, skill_manager=None, skills_directory: Path = None,
                 database_manager=None, auto_watch: bool = True,
                 watch_interval: float = 30.0):
        """
        Args:
            skill_manager: Direkte Referenz auf pi_control SkillManager (optional)
            skills_directory: Pfad zum skills/ Ordner
            database_manager: HoloDatabaseManager für Persistenz
            auto_watch: Automatisch auf Änderungen überwachen (default: True)
            watch_interval: Prüf-Intervall in Sekunden (default: 30s)
        """
        self.skill_manager = skill_manager
        self.skills_dir = skills_directory or Path(__file__).parent / "skills"
        self.db = database_manager

        # Lokaler Cache der Skill-Infos
        self._skill_cache: Dict[str, SkillInfo] = {}
        self._last_discovery = None

        # Skill Learning Data
        self._skill_usage: Dict[str, Dict] = {}

        # Skill Watcher für automatische Erkennung
        self._watcher = SkillWatcher(
            skills_dir=self.skills_dir,
            on_change_callback=self._on_skills_changed,
            check_interval=watch_interval
        )

        # Auto-Watch starten
        if auto_watch:
            self._watcher.start_watching()

        logger.info(f"🔧 HoloSkillBridge initialisiert (skills_dir: {self.skills_dir})")

    def set_skill_manager(self, skill_manager):
        """Setzt den SkillManager (für späte Initialisierung)"""
        self.skill_manager = skill_manager
        logger.info("🔗 SkillManager verbunden")

    def set_database(self, db):
        """Setzt die Datenbank für Persistenz"""
        self.db = db
        self._load_skill_learning_data()

    def _on_skills_changed(self, changes: Dict[str, List[str]]):
        """
        Wird vom SkillWatcher aufgerufen wenn Änderungen erkannt werden.

        Args:
            changes: {"added": [...], "modified": [...], "removed": [...]}
        """
        added = changes.get("added", [])
        modified = changes.get("modified", [])
        removed = changes.get("removed", [])

        # Gelöschte Skills aus Cache entfernen
        for filename in removed:
            skill_name = filename.replace(".py", "")
            if skill_name in self._skill_cache:
                del self._skill_cache[skill_name]
                logger.info(f"🗑️ Skill entfernt: {skill_name}")

        # Neue und geänderte Skills neu laden
        if added or modified:
            # Für geänderte Skills: Erst aus Cache entfernen
            for filename in modified:
                skill_name = filename.replace(".py", "")
                if skill_name in self._skill_cache:
                    del self._skill_cache[skill_name]

            # Discovery erneut ausführen (lädt nur neue/geänderte)
            self.discover_skills(force_refresh=True)

            for filename in added:
                skill_name = filename.replace(".py", "")
                if skill_name in self._skill_cache:
                    skill = self._skill_cache[skill_name]
                    logger.info(f"✨ Neuer Skill: {skill_name} - {skill.description[:50]}...")

            for filename in modified:
                skill_name = filename.replace(".py", "")
                if skill_name in self._skill_cache:
                    logger.info(f"🔄 Skill aktualisiert: {skill_name}")

    def stop_watching(self):
        """Stoppt den Skill-Watcher"""
        if self._watcher:
            self._watcher.stop_watching()

    def get_watcher_status(self) -> Dict:
        """Gibt den Status des Watchers zurück"""
        if self._watcher:
            return self._watcher.get_status()
        return {"running": False}

    # ========== SKILL DISCOVERY ==========

    def discover_skills(self, force_refresh: bool = False) -> List[SkillInfo]:
        """
        Entdeckt alle verfügbaren Skills.
        Kombiniert SkillManager-Skills mit lokalen Skills.
        """
        if not force_refresh and self._skill_cache:
            return list(self._skill_cache.values())

        discovered = []

        # 1. Skills vom SkillManager (wenn verbunden)
        if self.skill_manager:
            try:
                for skill_data in self.skill_manager.get_all_holo_skills():
                    info = self._skill_data_to_info(skill_data)
                    discovered.append(info)
                    self._skill_cache[info.name] = info
            except Exception as e:
                logger.error(f"Fehler beim Laden von SkillManager Skills: {e}")

        # 2. Lokale Skills aus Ordner (falls nicht schon vom SkillManager geladen)
        if self.skills_dir.exists():
            for skill_file in self.skills_dir.glob("*.py"):
                if skill_file.name.startswith("__"):
                    continue

                skill_name = skill_file.stem
                if skill_name not in self._skill_cache:
                    info = self._scan_skill_file(skill_file)
                    if info:
                        discovered.append(info)
                        self._skill_cache[info.name] = info

        # 3. Learning Data anwenden
        self._apply_learning_data()

        self._last_discovery = datetime.now()
        logger.info(f"🔍 {len(discovered)} Skills entdeckt")

        return discovered

    def _skill_data_to_info(self, data: Dict) -> SkillInfo:
        """Konvertiert SkillManager Daten zu SkillInfo"""
        return SkillInfo(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
            capabilities=data.get("capabilities", []),
            examples=data.get("examples", []),
            category=data.get("category", "general"),
            enabled=data.get("enabled", True),
            holo_compatible=data.get("holo_compatible", False),
            success_rate=data.get("success_rate", 0.0)
        )

    def _scan_skill_file(self, file_path: Path) -> Optional[SkillInfo]:
        """Scannt eine Skill-Datei nach Metadaten"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Suche nach Klassen-Attributen
            description = self._extract_class_attr(content, "description")
            keywords = self._extract_class_list(content, "keywords")
            capabilities = self._extract_class_list(content, "capabilities")
            examples = self._extract_class_list(content, "examples")
            category = self._extract_class_attr(content, "category") or "general"

            return SkillInfo(
                name=file_path.stem,
                description=description or f"Skill: {file_path.stem}",
                keywords=keywords,
                capabilities=capabilities,
                examples=examples,
                category=category,
                enabled=True,
                holo_compatible=bool(description and keywords)
            )
        except Exception as e:
            logger.warning(f"Konnte {file_path} nicht scannen: {e}")
            return None

    def _extract_class_attr(self, content: str, attr: str) -> Optional[str]:
        """Extrahiert ein String-Attribut aus dem Datei-Inhalt"""
        # Pattern: attribute = "value" oder attribute: str = "value"
        patterns = [
            rf'{attr}\s*[=:]\s*["\']([^"\']+)["\']',
            rf'{attr}\s*:\s*str\s*=\s*["\']([^"\']+)["\']'
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None

    def _extract_class_list(self, content: str, attr: str) -> List[str]:
        """Extrahiert ein Listen-Attribut aus dem Datei-Inhalt"""
        # Pattern: attribute = ["a", "b", "c"]
        pattern = rf'{attr}\s*[=:]\s*\[([^\]]+)\]'
        match = re.search(pattern, content)
        if match:
            list_content = match.group(1)
            # Extrahiere Strings aus der Liste
            items = re.findall(r'["\']([^"\']+)["\']', list_content)
            return items
        return []

    # ========== SKILL SELECTION ==========

    def find_best_skill(self, request: str) -> Tuple[Optional[SkillInfo], float]:
        """
        Findet den besten Skill für eine Anfrage.

        Returns:
            (SkillInfo, confidence) oder (None, 0)
        """
        if not self._skill_cache:
            self.discover_skills()

        best_skill = None
        best_confidence = 0.0

        for skill in self._skill_cache.values():
            if not skill.enabled or not skill.holo_compatible:
                continue

            confidence = skill.matches_request(request)

            # Bonus für erfolgreiche Skills
            if skill.success_rate > 80:
                confidence *= 1.1
            elif skill.success_rate < 30 and skill.usage_count > 5:
                confidence *= 0.8

            if confidence > best_confidence:
                best_confidence = confidence
                best_skill = skill

        return (best_skill, min(best_confidence, 1.0))

    def find_matching_skills(self, request: str,
                              min_confidence: float = 0.3) -> List[Tuple[SkillInfo, float]]:
        """
        Findet alle Skills die zur Anfrage passen könnten.

        Returns:
            Liste von (SkillInfo, confidence) sortiert nach Confidence
        """
        if not self._skill_cache:
            self.discover_skills()

        matches = []
        for skill in self._skill_cache.values():
            if not skill.enabled:
                continue

            confidence = skill.matches_request(request)
            if confidence >= min_confidence:
                matches.append((skill, confidence))

        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def get_skills_by_category(self, category: str) -> List[SkillInfo]:
        """Gibt alle Skills einer Kategorie zurück"""
        return [s for s in self._skill_cache.values()
                if s.category == category and s.enabled]

    def get_skills_by_capability(self, capability: str) -> List[SkillInfo]:
        """Findet Skills nach Fähigkeit"""
        return [s for s in self._skill_cache.values()
                if capability in s.capabilities and s.enabled]

    # ========== SKILL EXECUTION ==========

    async def execute_skill(self, skill_name: str, intent: str,
                            params: Dict = None) -> HoloSkillResult:
        """
        Führt einen Skill aus.

        Args:
            skill_name: Name des Skills
            intent: Was der User will
            params: Extrahierte Parameter

        Returns:
            HoloSkillResult
        """
        start_time = datetime.now()

        # Prüfe ob Skill existiert
        if skill_name not in self._skill_cache:
            return HoloSkillResult(
                success=False,
                error=f"Skill '{skill_name}' nicht gefunden",
                skill_name=skill_name
            )

        skill_info = self._skill_cache[skill_name]

        # Führe über SkillManager aus (wenn verfügbar)
        if self.skill_manager:
            try:
                result = await self.skill_manager.execute_skill(skill_name, intent, params)

                execution_time = (datetime.now() - start_time).total_seconds()

                # Tracking
                self._track_execution(skill_name, result.success, intent)

                return HoloSkillResult(
                    success=result.success,
                    data=result.data,
                    message=result.message,
                    error=result.error,
                    metadata=result.metadata,
                    skill_name=skill_name,
                    execution_time=execution_time
                )
            except Exception as e:
                self._track_execution(skill_name, False, intent)
                return HoloSkillResult(
                    success=False,
                    error=str(e),
                    skill_name=skill_name
                )
        else:
            return HoloSkillResult(
                success=False,
                error="Kein SkillManager verbunden - kann Skill nicht ausführen",
                skill_name=skill_name
            )

    async def execute_best_match(self, request: str, params: Dict = None,
                                  min_confidence: float = 0.4) -> HoloSkillResult:
        """
        Findet und führt den besten Skill aus.

        Returns:
            HoloSkillResult (mit success=False wenn kein Skill passt)
        """
        skill, confidence = self.find_best_skill(request)

        if skill is None or confidence < min_confidence:
            return HoloSkillResult(
                success=False,
                message=f"Kein passender Skill gefunden (min_confidence: {min_confidence})",
                metadata={"confidence": confidence}
            )

        logger.info(f"🎯 Führe Skill '{skill.name}' aus (confidence: {confidence:.2f})")
        return await self.execute_skill(skill.name, request, params)

    # ========== SKILL LEARNING ==========

    def _track_execution(self, skill_name: str, success: bool, request: str):
        """Trackt Skill-Ausführungen für Lernzwecke"""
        if skill_name not in self._skill_usage:
            self._skill_usage[skill_name] = {
                "executions": 0,
                "successes": 0,
                "requests": []
            }

        usage = self._skill_usage[skill_name]
        usage["executions"] += 1
        if success:
            usage["successes"] += 1

        # Speichere erfolgreiche Requests als Patterns
        if success and request not in usage["requests"]:
            usage["requests"].append(request)
            # Max 50 Patterns pro Skill
            if len(usage["requests"]) > 50:
                usage["requests"] = usage["requests"][-50:]

        # Update Cache
        if skill_name in self._skill_cache:
            skill = self._skill_cache[skill_name]
            skill.usage_count = usage["executions"]
            skill.success_rate = (usage["successes"] / usage["executions"]) * 100
            skill.last_used = datetime.now()
            skill.learned_patterns = usage["requests"][:10]  # Top 10

        # Persistieren
        self._save_skill_learning_data()

    def _apply_learning_data(self):
        """Wendet gespeicherte Learning Data auf Cache an"""
        for skill_name, usage in self._skill_usage.items():
            if skill_name in self._skill_cache:
                skill = self._skill_cache[skill_name]
                skill.usage_count = usage.get("executions", 0)
                if usage.get("executions", 0) > 0:
                    skill.success_rate = (usage.get("successes", 0) /
                                          usage["executions"]) * 100
                skill.learned_patterns = usage.get("requests", [])[:10]

    def _save_skill_learning_data(self):
        """Speichert Learning Data in der Datenbank"""
        if self.db:
            try:
                self.db.save_state("skill_learning", "usage_data", self._skill_usage)
            except Exception as e:
                logger.error(f"Fehler beim Speichern von Skill Learning Data: {e}")

    def _load_skill_learning_data(self):
        """Lädt Learning Data aus der Datenbank"""
        if self.db:
            try:
                data = self.db.load_state("skill_learning", "usage_data")
                if data:
                    self._skill_usage = data
                    logger.info(f"📚 Skill Learning Data geladen ({len(data)} Skills)")
            except Exception as e:
                logger.warning(f"Konnte Skill Learning Data nicht laden: {e}")

    def learn_pattern(self, skill_name: str, pattern: str):
        """Fügt ein neues Pattern für einen Skill hinzu"""
        if skill_name in self._skill_cache:
            skill = self._skill_cache[skill_name]
            if pattern not in skill.learned_patterns:
                skill.learned_patterns.append(pattern)

            # Auch in Usage speichern
            if skill_name not in self._skill_usage:
                self._skill_usage[skill_name] = {"requests": [], "executions": 0, "successes": 0}

            if pattern not in self._skill_usage[skill_name]["requests"]:
                self._skill_usage[skill_name]["requests"].append(pattern)

            self._save_skill_learning_data()

    # ========== HOLO INTEGRATION ==========

    def get_skill_summary_for_holo(self) -> str:
        """
        Erstellt eine Zusammenfassung aller Skills für Holo's Verständnis.
        Kann in den System-Prompt eingefügt werden.
        """
        if not self._skill_cache:
            self.discover_skills()

        compatible = [s for s in self._skill_cache.values()
                      if s.holo_compatible and s.enabled]

        if not compatible:
            return "Keine Skills verfügbar."

        lines = ["Verfügbare Fähigkeiten:"]

        # Gruppiere nach Kategorie
        by_category = {}
        for skill in compatible:
            cat = skill.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(skill)

        for category, skills in by_category.items():
            lines.append(f"\n[{category.upper()}]")
            for skill in skills:
                keywords_str = ", ".join(skill.keywords[:5])
                lines.append(f"• {skill.name}: {skill.description}")
                if keywords_str:
                    lines.append(f"  Trigger: {keywords_str}")

        return "\n".join(lines)

    def can_i_do(self, request: str) -> Tuple[bool, str, float]:
        """
        Holo fragt: "Kann ich das?"

        Returns:
            (kann_ich, skill_name, confidence)
        """
        skill, confidence = self.find_best_skill(request)

        if skill and confidence >= 0.4:
            return (True, skill.name, confidence)
        return (False, "", confidence)

    def what_can_i_do(self, category: str = None) -> List[str]:
        """
        Holo fragt: "Was kann ich alles?"

        Returns:
            Liste von Fähigkeits-Beschreibungen
        """
        if not self._skill_cache:
            self.discover_skills()

        skills = self._skill_cache.values()
        if category:
            skills = [s for s in skills if s.category == category]

        return [f"{s.name}: {s.description}"
                for s in skills
                if s.enabled and s.holo_compatible]


# ============================================================================
# HOLO SKILL SELECTOR - Intelligente Skill-Auswahl mit NLP
# ============================================================================

class HoloSkillSelector:
    """
    Intelligente Skill-Auswahl basierend auf User-Intent.
    Nutzt NLP und Kontext für bessere Entscheidungen.
    """

    def __init__(self, skill_bridge: HoloSkillBridge):
        self.bridge = skill_bridge
        self._intent_patterns = {}
        self._load_intent_patterns()

    def _load_intent_patterns(self):
        """Lädt Intent-Patterns für bessere Erkennung"""
        self._intent_patterns = {
            "create_image": [
                r"(mal|zeichne|erstell|generier).*bild",
                r"(bild|kunst|art).*erstellen",
                r"visualisier",
                r"(zeig|mach).*bild\s+von"
            ],
            "play_music": [
                r"(spiel|play).*musik",
                r"(musik|song|lied).*abspielen",
                r"lass.*laufen"
            ],
            "search_web": [
                r"such.*nach",
                r"find.*im\s+(web|internet|netz)",
                r"google",
                r"recherchier"
            ],
            "get_weather": [
                r"wetter",
                r"temperatur",
                r"regnet.*es",
                r"wie.*draußen"
            ],
            "control_home": [
                r"(licht|lampe).*(an|aus|dimm)",
                r"heizung",
                r"(mach|schalte).*(an|aus)"
            ]
        }

    def detect_intent(self, request: str) -> Tuple[Optional[str], float]:
        """
        Erkennt den Intent einer Anfrage.

        Returns:
            (intent_name, confidence) oder (None, 0)
        """
        request_lower = request.lower()

        for intent, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    return (intent, 0.8)

        return (None, 0.0)

    async def select_and_execute(self, request: str,
                                  context: Dict = None) -> HoloSkillResult:
        """
        Wählt den besten Skill basierend auf Intent und Kontext aus.

        Args:
            request: User-Anfrage
            context: Kontext (Stimmung, vorherige Anfragen, etc.)

        Returns:
            HoloSkillResult
        """
        # 1. Intent erkennen
        intent, intent_confidence = self.detect_intent(request)

        # 2. Skill finden (kombiniere Intent und Keyword-Matching)
        skill, skill_confidence = self.bridge.find_best_skill(request)

        if skill is None:
            return HoloSkillResult(
                success=False,
                message="Ich habe dafür leider keinen passenden Skill.",
                metadata={"intent": intent, "confidence": skill_confidence}
            )

        # 3. Entscheide ob wir ausführen
        final_confidence = max(intent_confidence, skill_confidence)

        if final_confidence < 0.4:
            return HoloSkillResult(
                success=False,
                message=f"Ich bin mir nicht sicher ob ich das kann... "
                        f"(Skill: {skill.name}, Confidence: {final_confidence:.0%})",
                metadata={"skill": skill.name, "confidence": final_confidence}
            )

        # 4. Ausführen
        logger.info(f"🎯 SkillSelector: {skill.name} (intent={intent}, conf={final_confidence:.2f})")
        return await self.bridge.execute_skill(skill.name, request)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_holo_skill_system(skill_manager=None,
                              skills_dir: Path = None,
                              database_manager=None,
                              auto_watch: bool = True,
                              watch_interval: float = 30.0) -> Tuple[HoloSkillBridge, HoloSkillSelector]:
    """
    Erstellt das komplette Holo Skill System.

    Args:
        skill_manager: pi_control SkillManager (optional)
        skills_dir: Pfad zum skills/ Ordner
        database_manager: HoloDatabaseManager für Persistenz
        auto_watch: Automatisch auf Änderungen überwachen (default: True)
        watch_interval: Prüf-Intervall in Sekunden (default: 30s)

    Returns:
        (HoloSkillBridge, HoloSkillSelector)
    """
    bridge = HoloSkillBridge(
        skill_manager=skill_manager,
        skills_directory=skills_dir,
        database_manager=database_manager,
        auto_watch=auto_watch,
        watch_interval=watch_interval
    )

    selector = HoloSkillSelector(bridge)

    return (bridge, selector)
