#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO TOOLS v2.0 - Werkzeuge für Holo Brain
===========================================

Nutzt das zentrale HoloDatabaseManager System!

Tools:
- Timer & Wecker (mit Background-Thread)
- Notizen & Erinnerungen
- Einkaufsliste
- Todo-Liste
- Rechner
- Wetter-Übersetzer

WICHTIG: Benötigt holo_database_system.py!

Author: Kira & Claude
"""

import threading
import time
import re
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("HoloTools")

# Type hint für HoloDatabaseManager (vermeidet zirkuläre Imports)
if TYPE_CHECKING:
    from holo_database_system import HoloDatabaseManager, ProductivityDatabase

# WeatherTranslator aus holo_personality importieren
try:
    from holo_personality import WeatherTranslator
except ImportError:
    class WeatherTranslator:
        """Fallback - echte Version in holo_personality.py"""
        TRANSLATIONS = {"clear": "klar", "sunny": "sonnig", "cloudy": "bewölkt"}
        @classmethod
        def translate(cls, text: str) -> str:
            return cls.TRANSLATIONS.get(text.lower().strip(), text) if text else text


# =============================================================================
# TIMER SYSTEM
# =============================================================================

@dataclass
class Timer:
    """Ein einzelner Timer"""
    id: str
    name: str
    duration_seconds: int
    created_at: datetime
    ends_at: datetime
    message: str = ""
    triggered: bool = False

    @property
    def remaining_seconds(self) -> int:
        if self.triggered:
            return 0
        remaining = (self.ends_at - datetime.now()).total_seconds()
        return max(0, int(remaining))

    @property
    def is_expired(self) -> bool:
        return datetime.now() >= self.ends_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "message": self.message,
            "triggered": self.triggered,
            "remaining_seconds": self.remaining_seconds
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Timer':
        """Erstellt Timer aus Dict (z.B. aus DB)"""
        return cls(
            id=data['id'],
            name=data.get('name', 'Timer'),
            duration_seconds=data.get('duration_seconds', 0),
            created_at=datetime.fromisoformat(data['started_at']) if isinstance(data.get('started_at'), str) else data.get('created_at', datetime.now()),
            ends_at=datetime.fromisoformat(data['ends_at']) if isinstance(data.get('ends_at'), str) else datetime.now(),
            message=data.get('message', ''),
            triggered=bool(data.get('completed', False) or data.get('triggered', False))
        )


class TimerManager:
    """
    Verwaltet Timer mit Background-Thread.

    Nutzt ProductivityDatabase für Persistenz!
    """

    def __init__(self, db: 'ProductivityDatabase', notification_callback: Callable = None):
        self.db = db
        self.notification_callback = notification_callback

        # In-Memory Cache für aktive Timer
        self.timers: Dict[str, Timer] = {}
        self._lock = threading.Lock()
        self._running = True

        # Timer aus DB laden
        self._load_timers()

        # Background-Thread starten
        self._start_checker()

        logger.info(f"⏰ TimerManager initialisiert ({len(self.timers)} aktive Timer)")

    def _load_timers(self):
        """Lädt aktive Timer aus DB in Memory-Cache"""
        try:
            active = self.db.get_active_timers()
            for row in active:
                timer = Timer.from_dict(row)
                if not timer.is_expired:
                    self.timers[timer.id] = timer
        except Exception as e:
            logger.error(f"⏰ Timer laden fehlgeschlagen: {e}")

    def _start_checker(self):
        """Startet Background-Thread für Timer-Prüfung"""
        def check_loop():
            while self._running:
                self._check_timers()
                time.sleep(1)  # Jede Sekunde prüfen

        thread = threading.Thread(target=check_loop, daemon=True, name="TimerChecker")
        thread.start()

    def _check_timers(self):
        """Prüft ob Timer abgelaufen sind"""
        with self._lock:
            expired = []

            for timer_id, timer in list(self.timers.items()):
                if timer.is_expired and not timer.triggered:
                    timer.triggered = True
                    # In DB als completed markieren
                    try:
                        self.db.mark_timer_completed(timer_id)
                    except Exception as e:
                        logger.error(f"⏰ DB update failed: {e}")
                    expired.append(timer)

            # Notifications senden (außerhalb des Locks für bessere Performance)
            for timer in expired:
                self._trigger_notification(timer)
                if timer.id in self.timers:
                    del self.timers[timer.id]

    def _trigger_notification(self, timer: Timer):
        """
        Sendet Benachrichtigung wenn Timer abläuft.

        THREAD-SAFE: Wird vom Background-Thread aufgerufen!
        """
        message = timer.message or f"Timer '{timer.name}' ist abgelaufen!"
        logger.info(f"⏰ TIMER EXPIRED: {timer.name} - {message}")

        if self.notification_callback:
            try:
                logger.info(f"⏰ Calling notification_callback for timer '{timer.name}'")
                self.notification_callback(
                    title=f"⏰ Timer: {timer.name}",
                    message=message,
                    timer=timer
                )
                logger.info(f"⏰ notification_callback completed successfully")
            except Exception as e:
                logger.error(f"⏰ Notification callback error: {e}", exc_info=True)
        else:
            logger.warning(f"⏰ No notification_callback set for timer '{timer.name}'")

    def create_timer(self, duration_seconds: int, name: str = None, message: str = None) -> Timer:
        """Erstellt einen neuen Timer"""
        # In DB erstellen
        timer_data = self.db.create_timer(
            duration_seconds=duration_seconds,
            name=name,
            message=message
        )

        # Timer-Objekt erstellen
        timer = Timer(
            id=timer_data['id'],
            name=timer_data['name'],
            duration_seconds=duration_seconds,
            created_at=datetime.fromisoformat(timer_data['started_at']),
            ends_at=datetime.fromisoformat(timer_data['ends_at']),
            message=message or ""
        )

        # In Memory-Cache
        with self._lock:
            self.timers[timer.id] = timer

        logger.info(f"⏰ Timer erstellt: {timer.name} ({duration_seconds}s)")
        return timer

    def cancel_timer(self, timer_id: str) -> bool:
        """Löscht einen Timer"""
        with self._lock:
            if timer_id in self.timers:
                del self.timers[timer_id]
            self.db.cancel_timer(timer_id)
            return True
        return False

    def get_active_timers(self) -> List[Timer]:
        """Gibt alle aktiven Timer zurück"""
        with self._lock:
            return list(self.timers.values())

    def parse_duration(self, text: str) -> Optional[int]:
        """Parst Zeitangaben aus Text"""
        text = text.lower()
        total_seconds = 0

        patterns = [
            (r'(\d+)\s*(?:stunde|stunden|std|h)', 3600),
            (r'(\d+)\s*(?:minute|minuten|min|m)', 60),
            (r'(\d+)\s*(?:sekunde|sekunden|sek|s)', 1),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                total_seconds += int(match.group(1)) * multiplier

        return total_seconds if total_seconds > 0 else None

    def stop(self):
        """Stoppt den Background-Thread"""
        self._running = False


# =============================================================================
# NOTIZEN SYSTEM (Wrapper für ProductivityDatabase)
# =============================================================================

@dataclass
class Note:
    """Eine Notiz"""
    id: str
    content: str
    created_at: datetime
    category: str = "allgemein"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "category": self.category,
            "tags": self.tags
        }


class NotesManager:
    """Wrapper für ProductivityDatabase.notes Funktionen"""

    def __init__(self, db: 'ProductivityDatabase'):
        self.db = db
        logger.info("📝 NotesManager initialisiert")

    def add_note(self, content: str, category: str = "allgemein", tags: List[str] = None) -> Note:
        """Fügt eine neue Notiz hinzu"""
        note_id = self.db.add_note(content, category=category)

        return Note(
            id=note_id,
            content=content,
            created_at=datetime.now(),
            category=category,
            tags=tags or []
        )

    def get_notes(self, limit: int = 10, category: str = None) -> List[Note]:
        """Holt Notizen"""
        if category:
            rows = self.db.fetchall('''
                SELECT * FROM notes WHERE category = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (category, limit))
        else:
            rows = self.db.fetchall('''
                SELECT * FROM notes ORDER BY created_at DESC LIMIT ?
            ''', (limit,))

        return [Note(
            id=r['id'],
            content=r['content'],
            created_at=datetime.fromisoformat(r['created_at']) if r['created_at'] else datetime.now(),
            category=r.get('category', 'allgemein'),
            tags=[]
        ) for r in rows]

    def search_notes(self, query: str) -> List[Note]:
        """Sucht in Notizen"""
        rows = self.db.search_notes(query)
        return [Note(
            id=r['id'],
            content=r['content'],
            created_at=datetime.fromisoformat(r['created_at']) if r['created_at'] else datetime.now(),
            category=r.get('category', 'allgemein'),
            tags=[]
        ) for r in rows]

    def delete_note(self, note_id: str) -> bool:
        """Löscht eine Notiz"""
        self.db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        return True


# =============================================================================
# EINKAUFSLISTE (Wrapper für ProductivityDatabase)
# =============================================================================

@dataclass
class ShoppingItem:
    """Ein Einkaufslisteneintrag"""
    id: str
    item: str
    quantity: str = ""
    checked: bool = False
    added_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "item": self.item,
            "quantity": self.quantity,
            "checked": self.checked,
            "added_at": self.added_at.isoformat()
        }


class ShoppingListManager:
    """Wrapper für ProductivityDatabase.shopping Funktionen"""

    def __init__(self, db: 'ProductivityDatabase'):
        self.db = db
        logger.info("🛒 ShoppingListManager initialisiert")

    def add_item(self, item: str, quantity: str = "") -> ShoppingItem:
        """Fügt Item zur Liste hinzu"""
        item_id = self.db.add_shopping_item(item, quantity)

        return ShoppingItem(
            id=item_id,
            item=item,
            quantity=quantity,
            added_at=datetime.now()
        )

    def get_list(self) -> List[ShoppingItem]:
        """Holt Einkaufsliste"""
        rows = self.db.get_shopping_list()
        return [ShoppingItem(
            id=r['id'],
            item=r['item'],
            quantity=r.get('quantity', ''),
            checked=bool(r.get('purchased', 0)),
            added_at=datetime.fromisoformat(r['added_at']) if r.get('added_at') else datetime.now()
        ) for r in rows]

    def check_item(self, item_id: str) -> bool:
        """Markiert Item als gekauft"""
        self.db.execute(
            'UPDATE shopping_items SET purchased = 1 WHERE id = ?',
            (item_id,)
        )
        return True

    def uncheck_item(self, item_id: str) -> bool:
        """Markiert Item als nicht gekauft"""
        self.db.execute(
            'UPDATE shopping_items SET purchased = 0 WHERE id = ?',
            (item_id,)
        )
        return True

    def remove_item(self, item_id: str) -> bool:
        """Entfernt Item"""
        self.db.execute('DELETE FROM shopping_items WHERE id = ?', (item_id,))
        return True

    def clear_checked(self):
        """Entfernt alle gekauften Items"""
        self.db.execute('DELETE FROM shopping_items WHERE purchased = 1')


# =============================================================================
# TODO SYSTEM (Wrapper für ProductivityDatabase)
# =============================================================================

class TodoPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TodoItem:
    """Eine Aufgabe"""
    id: str
    task: str
    priority: TodoPriority = TodoPriority.NORMAL
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task": self.task,
            "priority": self.priority.value,
            "priority_name": self.priority.name,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }


class TodoManager:
    """Wrapper für ProductivityDatabase.todos Funktionen"""

    def __init__(self, db: 'ProductivityDatabase'):
        self.db = db
        logger.info("✅ TodoManager initialisiert")

    def add_todo(self, task: str, priority: TodoPriority = TodoPriority.NORMAL,
                 due_date: datetime = None) -> TodoItem:
        """Fügt eine neue Aufgabe hinzu"""
        todo_id = self.db.add_todo(
            title=task,
            priority=priority.value,
            due_date=due_date.isoformat() if due_date else None
        )

        return TodoItem(
            id=todo_id,
            task=task,
            priority=priority,
            due_date=due_date,
            created_at=datetime.now()
        )

    def get_todos(self, include_completed: bool = False) -> List[TodoItem]:
        """Holt Todos"""
        if include_completed:
            rows = self.db.fetchall('''
                SELECT * FROM todos ORDER BY priority DESC, due_date ASC
            ''')
        else:
            rows = self.db.get_open_todos()

        return [TodoItem(
            id=r['id'],
            task=r['title'],
            priority=TodoPriority(r.get('priority', 2)),
            due_date=datetime.fromisoformat(r['due_date']) if r.get('due_date') else None,
            completed=bool(r.get('completed', 0)),
            created_at=datetime.fromisoformat(r['created_at']) if r.get('created_at') else datetime.now()
        ) for r in rows]

    def complete_todo(self, todo_id: str) -> bool:
        """Markiert Todo als erledigt"""
        self.db.complete_todo(todo_id)
        return True

    def delete_todo(self, todo_id: str) -> bool:
        """Löscht Todo"""
        self.db.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        return True


# =============================================================================
# RECHNER (SICHERE IMPLEMENTIERUNG - KEIN eval()!)
# =============================================================================

import ast
import operator

class SafeMathEvaluator(ast.NodeVisitor):
    """
    Sicherer mathematischer Ausdruck-Evaluator.
    Verwendet AST statt eval() um Code-Injection zu verhindern.
    """

    # Erlaubte Operatoren
    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self._operators.get(type(node.op))
        if op is None:
            raise ValueError(f"Nicht erlaubter Operator: {type(node.op).__name__}")
        return op(left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = self._operators.get(type(node.op))
        if op is None:
            raise ValueError(f"Nicht erlaubter Operator: {type(node.op).__name__}")
        return op(operand)

    def visit_Num(self, node):
        # Python < 3.8
        return node.n

    def visit_Constant(self, node):
        # Python >= 3.8
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Nicht erlaubter Wert: {node.value}")

    def visit_Expression(self, node):
        return self.visit(node.body)

    def generic_visit(self, node):
        raise ValueError(f"Nicht erlaubter Ausdruck: {type(node).__name__}")


class Calculator:
    """Einfacher Rechner für mathematische Ausdrücke (SICHER - ohne eval!)"""

    @staticmethod
    def calculate(expression: str) -> Optional[float]:
        """Berechnet einen mathematischen Ausdruck sicher ohne eval()"""
        try:
            expression = expression.lower()
            expression = expression.replace('x', '*').replace('×', '*')
            expression = expression.replace('÷', '/').replace(':', '/')
            expression = expression.replace('^', '**')
            expression = expression.replace(',', '.')

            expression = re.sub(r'(\d+)\s*%\s*von\s*(\d+)', r'(\1/100)*\2', expression)
            expression = re.sub(r'(\d+)\s*%', r'(\1/100)', expression)

            # Nur erlaubte Zeichen
            allowed = set('0123456789.+-*/() ')
            if not all(c in allowed for c in expression.replace('**', '')):
                return None

            # Sichere Auswertung via AST
            tree = ast.parse(expression, mode='eval')
            evaluator = SafeMathEvaluator()
            result = evaluator.visit(tree)

            return round(result, 10)

        except Exception:
            return None

    @staticmethod
    def format_result(result: float) -> str:
        """Formatiert das Ergebnis schön"""
        if result == int(result):
            return str(int(result))
        return f"{result:.4f}".rstrip('0').rstrip('.')


# =============================================================================
# HOLO TOOLS - HAUPTKLASSE
# =============================================================================

class HoloTools:
    """
    Zentrale Tool-Sammlung für Holo.

    NUTZT HoloDatabaseManager für alle Persistenz!

    Usage:
        from holo_database_system import HoloDatabaseManager
        from holo_tools import HoloTools

        db = HoloDatabaseManager()
        tools = HoloTools(db, notification_callback=my_callback)
    """

    def __init__(self, db_manager: 'HoloDatabaseManager', notification_callback: Callable = None):
        """
        Initialisiert HoloTools mit dem zentralen DB-Manager.

        Args:
            db_manager: HoloDatabaseManager Instanz
            notification_callback: Callback für Timer-Benachrichtigungen
        """
        self.db = db_manager
        self.notification_callback = notification_callback

        # Alle Manager nutzen db.productivity!
        self.timer = TimerManager(
            self.db.productivity,
            notification_callback=self._on_timer_expired
        )
        self.notes = NotesManager(self.db.productivity)
        self.shopping = ShoppingListManager(self.db.productivity)
        self.todos = TodoManager(self.db.productivity)
        self.calculator = Calculator()
        self.weather_translator = WeatherTranslator()

        # Pending notifications (für proaktive Nachrichten)
        self.pending_notifications: List[Dict] = []

        logger.info(f"🛠️ HoloTools v2.0 initialisiert (zentrale DB)")

    def _on_timer_expired(self, title: str, message: str, timer: Timer):
        """
        Callback wenn Timer abläuft.

        THREAD-SAFE: Wird vom TimerManager Background-Thread aufgerufen!
        """
        logger.info(f"🔔 HoloTools._on_timer_expired: {title} - {message}")

        notification = {
            "type": "timer",
            "tool": "timer",
            "title": title,
            "message": message,
            "timer": timer.to_dict() if timer else {},
            "timestamp": datetime.now().isoformat()
        }
        self.pending_notifications.append(notification)

        # Weiterleiten an externen Callback (HoloPersona)
        if self.notification_callback:
            try:
                logger.info(f"🔔 Calling external notification_callback...")
                self.notification_callback(notification)
                logger.info(f"🔔 External callback completed")
            except Exception as e:
                logger.error(f"🔔 External callback error: {e}", exc_info=True)

    def get_pending_notification(self) -> Optional[Dict]:
        """Holt und entfernt die nächste Benachrichtigung"""
        if self.pending_notifications:
            return self.pending_notifications.pop(0)
        return None

    def get_status(self) -> Dict:
        """Gibt Status aller Tools zurück"""
        return {
            "active_timers": len(self.timer.get_active_timers()),
            "open_todos": len(self.todos.get_todos()),
            "shopping_items": len(self.shopping.get_list()),
            "notes_count": len(self.notes.get_notes(limit=100)),
            "pending_notifications": len(self.pending_notifications)
        }

    def process_command(self, text: str) -> Optional[Dict]:
        """
        Verarbeitet Tool-Befehle aus natürlicher Sprache.

        Returns:
            Dict mit Ergebnis oder None wenn kein Tool-Befehl
        """
        text_lower = text.lower().strip()

        # === TIMER ===
        if any(word in text_lower for word in ["timer", "wecker", "erinner", "in ... minuten"]):
            return self._handle_timer_command(text)

        # === NOTIZEN ===
        if any(word in text_lower for word in ["merk dir", "notiz", "notiere", "speicher"]):
            return self._handle_note_command(text)

        # === EINKAUFSLISTE ===
        if any(word in text_lower for word in ["einkauf", "kaufen", "kauf ", "einkaufsliste", "shopping", "brauch", "brauchen", "auf die liste", "hole ", "hol "]):
            return self._handle_shopping_command(text)

        # === TODO ===
        if any(word in text_lower for word in ["todo", "aufgabe", "muss noch", "zu tun"]):
            return self._handle_todo_command(text)

        # === RECHNER ===
        if any(word in text_lower for word in ["rechne", "berechne", "was ist", "prozent"]):
            result = self._handle_calculator(text)
            if result:
                return result

        return None

    def _handle_timer_command(self, text: str) -> Optional[Dict]:
        """Verarbeitet Timer-Befehle"""
        text_lower = text.lower()

        # Timer auflisten
        if any(word in text_lower for word in ["welche timer", "aktive timer", "timer liste", "läuft"]):
            timers = self.timer.get_active_timers()
            if not timers:
                return {
                    "type": "tool_response",
                    "tool": "timer",
                    "action": "list",
                    "response": "⏰ Du hast keine aktiven Timer."
                }

            lines = ["⏰ **Aktive Timer:**"]
            for t in timers:
                mins = t.remaining_seconds // 60
                secs = t.remaining_seconds % 60
                lines.append(f"  • {t.name}: noch {mins}:{secs:02d}")

            return {
                "type": "tool_response",
                "tool": "timer",
                "action": "list",
                "response": "\n".join(lines)
            }

        # Timer erstellen
        duration = self.timer.parse_duration(text)
        if duration:
            name_match = re.search(r'(?:für|namens?|:)\s*["\']?([^"\']+)["\']?', text)
            name = name_match.group(1).strip() if name_match else None

            timer = self.timer.create_timer(duration, name=name)
            mins = duration // 60
            secs = duration % 60

            time_str = f"{mins} Minuten" if mins else f"{secs} Sekunden"
            if mins and secs:
                time_str = f"{mins} Minuten und {secs} Sekunden"

            return {
                "type": "tool_response",
                "tool": "timer",
                "action": "create",
                "timer": timer.to_dict(),
                "response": f"⏰ Timer '{timer.name}' für {time_str} gestartet! Ich sage dir Bescheid wenn er abläuft."
            }

        return None

    def _handle_note_command(self, text: str) -> Optional[Dict]:
        """Verarbeitet Notiz-Befehle"""
        text_lower = text.lower()

        # Notizen anzeigen
        if any(word in text_lower for word in ["zeig notiz", "meine notiz", "was hast du"]):
            notes = self.notes.get_notes(limit=5)
            if not notes:
                return {
                    "type": "tool_response",
                    "tool": "notes",
                    "action": "list",
                    "response": "📝 Du hast noch keine Notizen."
                }

            lines = ["📝 **Deine Notizen:**"]
            for n in notes:
                preview = n.content[:50] + "..." if len(n.content) > 50 else n.content
                lines.append(f"  • {preview}")

            return {
                "type": "tool_response",
                "tool": "notes",
                "action": "list",
                "response": "\n".join(lines)
            }

        # Notiz speichern
        match = re.search(r'(?:merk dir|notiz|notiere|speicher)[:\s]+(.+)', text, re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            note = self.notes.add_note(content)

            return {
                "type": "tool_response",
                "tool": "notes",
                "action": "add",
                "note": note.to_dict(),
                "response": f"📝 Notiert: \"{content}\""
            }

        return None

    def _handle_shopping_command(self, text: str) -> Optional[Dict]:
        """Verarbeitet Einkaufslisten-Befehle"""
        text_lower = text.lower()

        # Liste anzeigen
        if any(word in text_lower for word in ["einkaufsliste", "was muss ich", "was brauche ich", "zeig einkauf"]):
            items = self.shopping.get_list()
            if not items:
                return {
                    "type": "tool_response",
                    "tool": "shopping",
                    "action": "list",
                    "response": "🛒 Die Einkaufsliste ist leer!"
                }

            lines = ["🛒 **Einkaufsliste:**"]
            for item in items:
                qty = f" ({item.quantity})" if item.quantity else ""
                check = "✓" if item.checked else "○"
                lines.append(f"  {check} {item.item}{qty}")

            return {
                "type": "tool_response",
                "tool": "shopping",
                "action": "list",
                "response": "\n".join(lines)
            }

        # Item hinzufügen
        patterns = [
            r'(?:kauf|kaufe|hole|hol|brauch|brauche|auf die liste)[:\s]+(.+)',
            r'(?:füg|füge).+(?:einkauf|liste).+hinzu[:\s]+(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                item_text = match.group(1).strip()
                items = [i.strip() for i in re.split(r'[,;und&]+', item_text) if i.strip()]

                added = []
                for item in items:
                    entry = self.shopping.add_item(item)
                    added.append(entry.item)

                return {
                    "type": "tool_response",
                    "tool": "shopping",
                    "action": "add",
                    "response": f"🛒 Auf die Liste: {', '.join(added)}"
                }

        return None

    def _handle_todo_command(self, text: str) -> Optional[Dict]:
        """Verarbeitet Todo-Befehle"""
        text_lower = text.lower()

        # Todos anzeigen
        if any(word in text_lower for word in ["zeig todo", "meine aufgaben", "was muss ich", "to-do liste"]):
            todos = self.todos.get_todos()
            if not todos:
                return {
                    "type": "tool_response",
                    "tool": "todos",
                    "action": "list",
                    "response": "✅ Keine offenen Aufgaben!"
                }

            lines = ["✅ **Deine Aufgaben:**"]
            priority_emoji = {1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴"}
            for t in todos:
                emoji = priority_emoji.get(t.priority.value, "⚪")
                lines.append(f"  {emoji} {t.task}")

            return {
                "type": "tool_response",
                "tool": "todos",
                "action": "list",
                "response": "\n".join(lines)
            }

        # Todo hinzufügen
        match = re.search(r'(?:todo|aufgabe|muss noch)[:\s]+(.+)', text, re.IGNORECASE)
        if match:
            task = match.group(1).strip()
            priority = TodoPriority.NORMAL

            if any(word in text_lower for word in ["wichtig", "dringend", "urgent"]):
                priority = TodoPriority.HIGH
            elif any(word in text_lower for word in ["später", "irgendwann"]):
                priority = TodoPriority.LOW

            todo = self.todos.add_todo(task, priority)

            return {
                "type": "tool_response",
                "tool": "todos",
                "action": "add",
                "todo": todo.to_dict(),
                "response": f"✅ Aufgabe hinzugefügt: \"{task}\""
            }

        return None

    def _handle_calculator(self, text: str) -> Optional[Dict]:
        """Verarbeitet Rechenaufgaben"""
        patterns = [
            r'(?:rechne|berechne|was ist|wie viel ist)[:\s]*(.+)',
            r'(\d+[\s]*[+\-*/x×÷^][\s]*\d+(?:[\s]*[+\-*/x×÷^][\s]*\d+)*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expression = match.group(1).strip()
                expression = expression.rstrip('?=')

                result = self.calculator.calculate(expression)
                if result is not None:
                    formatted = self.calculator.format_result(result)
                    return {
                        "type": "tool_response",
                        "tool": "calculator",
                        "expression": expression,
                        "result": result,
                        "response": f"🔢 {expression} = **{formatted}**"
                    }

        return None

    def stop(self):
        """Stoppt alle Background-Threads"""
        self.timer.stop()


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HOLO TOOLS v2.0 TEST")
    print("=" * 60)

    # Test mit HoloDatabaseManager
    try:
        from holo_database_system import HoloDatabaseManager

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            db = HoloDatabaseManager(Path(tmpdir))

            def test_callback(notification):
                print(f"🔔 NOTIFICATION: {notification}")

            tools = HoloTools(db, notification_callback=test_callback)

            # Timer Test
            print("\n⏰ Timer Test...")
            timer = tools.timer.create_timer(3, name="Test Timer")
            print(f"   Created: {timer.name}")
            print(f"   Active: {len(tools.timer.get_active_timers())}")

            # Notes Test
            print("\n📝 Notes Test...")
            note = tools.notes.add_note("Test Notiz")
            print(f"   Added: {note.id}")

            # Shopping Test
            print("\n🛒 Shopping Test...")
            item = tools.shopping.add_item("Milch")
            print(f"   Added: {item.item}")

            # Todos Test
            print("\n✅ Todos Test...")
            todo = tools.todos.add_todo("Test Task")
            print(f"   Added: {todo.task}")

            # Calculator Test
            print("\n🔢 Calculator Test...")
            result = tools.calculator.calculate("2 + 2 * 3")
            print(f"   2 + 2 * 3 = {result}")

            # Status
            print("\n📊 Status:")
            print(f"   {tools.get_status()}")

            # Wait for timer
            print("\n⏰ Waiting for timer...")
            time.sleep(4)

            tools.stop()
            db.close_all()

            print("\n✅ All tests passed!")

    except ImportError:
        print("❌ holo_database_system.py not found!")
        print("   This module requires HoloDatabaseManager.")
