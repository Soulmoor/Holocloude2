"""
HOLO EVENTS - Zentrales Event-System (Observer Pattern)
=======================================================

Implementiert das Observer Pattern fuer lose gekoppelte Kommunikation
zwischen Modulen.

Features:
- Event-Registrierung und -Dispatch
- Synchrone und asynchrone Events
- Event-Filtering und Prioritaeten
- Event-History fuer Debugging
- Thread-safe Implementation

Verwendung:
    from holo_events import EventBus, Event

    # Event-Bus instanziieren (Singleton)
    bus = EventBus.get_instance()

    # Handler registrieren
    @bus.on("user:message")
    def on_message(event):
        print(f"Nachricht: {event.data['text']}")

    # Event ausloesen
    bus.emit("user:message", {"text": "Hallo!"})

Event-Namenskonvention:
    <modul>:<aktion>
    Beispiele:
    - "user:message" - Benutzer hat Nachricht gesendet
    - "emotion:changed" - Emotion hat sich geaendert
    - "energy:low" - Energie ist niedrig
    - "system:startup" - System startet
    - "llm:response" - LLM hat geantwortet
"""

import logging
import threading
import time
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from functools import wraps

logger = logging.getLogger(__name__)


# =============================================================================
# EVENT TYPES
# =============================================================================

class EventPriority(Enum):
    """Prioritaet fuer Event-Handler."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    """
    Ein Event mit Metadaten.

    Attributes:
        name: Event-Name (z.B. "user:message")
        data: Event-Daten als Dictionary
        timestamp: Zeitstempel der Erstellung
        source: Quelle des Events (optional)
        priority: Prioritaet
        id: Eindeutige Event-ID
    """
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    priority: EventPriority = EventPriority.NORMAL
    id: str = field(default_factory=lambda: f"evt_{int(time.time()*1000)}")

    def __post_init__(self):
        if isinstance(self.priority, int):
            self.priority = EventPriority(self.priority)

    def to_dict(self) -> Dict:
        """Konvertiert Event zu Dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority.value
        }


@dataclass
class EventHandler:
    """
    Registrierter Event-Handler.

    Attributes:
        callback: Die Handler-Funktion
        event_pattern: Event-Name oder Pattern (mit * fuer Wildcard)
        priority: Handler-Prioritaet
        once: True wenn Handler nach einmaliger Ausfuehrung entfernt werden soll
        filter_fn: Optionale Filter-Funktion
    """
    callback: Callable
    event_pattern: str
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False
    filter_fn: Optional[Callable[[Event], bool]] = None
    active: bool = True

    def matches(self, event_name: str) -> bool:
        """Prueft ob der Handler zum Event-Namen passt."""
        if self.event_pattern == "*":
            return True

        if "*" in self.event_pattern:
            # Wildcard-Matching
            pattern_parts = self.event_pattern.split(":")
            name_parts = event_name.split(":")

            if len(pattern_parts) != len(name_parts):
                return False

            for pattern, name in zip(pattern_parts, name_parts):
                if pattern != "*" and pattern != name:
                    return False
            return True

        return self.event_pattern == event_name


# =============================================================================
# EVENT BUS (SINGLETON)
# =============================================================================

class EventBus:
    """
    Zentraler Event-Bus (Observer Pattern).

    Singleton-Pattern fuer globalen Zugriff.

    Beispiel:
        bus = EventBus.get_instance()

        # Handler registrieren
        bus.subscribe("user:*", my_handler)

        # Event senden
        bus.emit("user:message", {"text": "Hallo"})

        # Oder mit Decorator
        @bus.on("emotion:changed")
        def handle_emotion(event):
            print(f"Emotion: {event.data['emotion']}")
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._handlers: List[EventHandler] = []
        self._handlers_lock = threading.RLock()

        # Event-History fuer Debugging
        self._history: List[Event] = []
        self._history_max_size = 1000
        self._history_enabled = True

        # Async-Queue fuer Background-Events
        self._async_queue: List[Event] = []
        self._async_thread: Optional[threading.Thread] = None
        self._running = False

        # Statistiken
        self._stats = {
            "events_emitted": 0,
            "handlers_called": 0,
            "errors": 0
        }

        logger.debug("EventBus initialisiert")

    @classmethod
    def get_instance(cls) -> 'EventBus':
        """Gibt die Singleton-Instanz zurueck."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Setzt die Singleton-Instanz zurueck (fuer Tests)."""
        with cls._lock:
            cls._instance = None

    # -------------------------------------------------------------------------
    # HANDLER REGISTRATION
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event_pattern: str,
        callback: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        filter_fn: Optional[Callable[[Event], bool]] = None
    ) -> EventHandler:
        """
        Registriert einen Event-Handler.

        Args:
            event_pattern: Event-Name oder Pattern (z.B. "user:*")
            callback: Handler-Funktion (nimmt Event als Parameter)
            priority: Handler-Prioritaet
            once: True fuer einmalige Ausfuehrung
            filter_fn: Optionale Filter-Funktion

        Returns:
            EventHandler: Der registrierte Handler (zum Unsubscribe)
        """
        handler = EventHandler(
            callback=callback,
            event_pattern=event_pattern,
            priority=priority,
            once=once,
            filter_fn=filter_fn
        )

        with self._handlers_lock:
            self._handlers.append(handler)
            # Nach Prioritaet sortieren (hoechste zuerst)
            self._handlers.sort(key=lambda h: h.priority.value, reverse=True)

        logger.debug(f"Handler registriert: {event_pattern}")
        return handler

    def unsubscribe(self, handler: EventHandler) -> bool:
        """
        Entfernt einen Handler.

        Args:
            handler: Der zu entfernende Handler

        Returns:
            bool: True wenn erfolgreich entfernt
        """
        with self._handlers_lock:
            if handler in self._handlers:
                self._handlers.remove(handler)
                return True
        return False

    def unsubscribe_all(self, event_pattern: str):
        """Entfernt alle Handler fuer ein Pattern."""
        with self._handlers_lock:
            self._handlers = [
                h for h in self._handlers
                if h.event_pattern != event_pattern
            ]

    def on(
        self,
        event_pattern: str,
        priority: EventPriority = EventPriority.NORMAL
    ) -> Callable:
        """
        Decorator zum Registrieren eines Handlers.

        Usage:
            @bus.on("user:message")
            def handle_message(event):
                print(event.data)
        """
        def decorator(func: Callable) -> Callable:
            self.subscribe(event_pattern, func, priority)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return decorator

    def once(self, event_pattern: str) -> Callable:
        """
        Decorator fuer einmalige Handler.

        Usage:
            @bus.once("system:ready")
            def on_ready(event):
                print("System ist bereit!")
        """
        def decorator(func: Callable) -> Callable:
            self.subscribe(event_pattern, func, once=True)
            return func
        return decorator

    # -------------------------------------------------------------------------
    # EVENT EMISSION
    # -------------------------------------------------------------------------

    def emit(
        self,
        event_name: str,
        data: Optional[Dict] = None,
        source: str = "",
        priority: EventPriority = EventPriority.NORMAL
    ) -> Event:
        """
        Loest ein Event aus.

        Args:
            event_name: Name des Events
            data: Event-Daten
            source: Quelle des Events
            priority: Event-Prioritaet

        Returns:
            Event: Das erstellte Event
        """
        event = Event(
            name=event_name,
            data=data or {},
            source=source,
            priority=priority
        )

        self._dispatch(event)
        return event

    def emit_async(
        self,
        event_name: str,
        data: Optional[Dict] = None,
        source: str = ""
    ):
        """
        Loest ein Event asynchron aus (im Background-Thread).

        Nuetzlich fuer nicht-blockierende Events.
        """
        event = Event(name=event_name, data=data or {}, source=source)
        self._async_queue.append(event)

        # Background-Thread starten wenn noetig
        if not self._running:
            self._start_async_processor()

    def _dispatch(self, event: Event):
        """Verteilt ein Event an alle passenden Handler."""
        self._stats["events_emitted"] += 1

        # Zur History hinzufuegen
        if self._history_enabled:
            self._history.append(event)
            if len(self._history) > self._history_max_size:
                self._history = self._history[-self._history_max_size:]

        # Handler aufrufen
        handlers_to_remove = []

        with self._handlers_lock:
            handlers = list(self._handlers)  # Kopie fuer Iteration

        for handler in handlers:
            if not handler.active:
                continue

            if not handler.matches(event.name):
                continue

            # Filter pruefen
            if handler.filter_fn:
                try:
                    if not handler.filter_fn(event):
                        continue
                except Exception as e:
                    logger.warning(f"Filter-Fehler: {e}")
                    continue

            # Handler ausfuehren
            try:
                handler.callback(event)
                self._stats["handlers_called"] += 1
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Handler-Fehler bei {event.name}: {e}")

            # Once-Handler markieren
            if handler.once:
                handlers_to_remove.append(handler)

        # Once-Handler entfernen
        for handler in handlers_to_remove:
            self.unsubscribe(handler)

    def _start_async_processor(self):
        """Startet den Background-Thread fuer async Events."""
        self._running = True
        self._async_thread = threading.Thread(
            target=self._async_loop,
            daemon=True,
            name="EventBus-Async"
        )
        self._async_thread.start()

    def _async_loop(self):
        """Background-Loop fuer async Events."""
        while self._running:
            if self._async_queue:
                event = self._async_queue.pop(0)
                self._dispatch(event)
            else:
                time.sleep(0.01)

    def stop(self):
        """Stoppt den Background-Thread."""
        self._running = False
        if self._async_thread:
            self._async_thread.join(timeout=1)

    # -------------------------------------------------------------------------
    # QUERIES & DEBUGGING
    # -------------------------------------------------------------------------

    def get_handlers(self, event_pattern: str = "*") -> List[EventHandler]:
        """Gibt alle Handler fuer ein Pattern zurueck."""
        with self._handlers_lock:
            if event_pattern == "*":
                return list(self._handlers)
            return [h for h in self._handlers if h.matches(event_pattern)]

    def get_history(
        self,
        event_pattern: str = "*",
        limit: int = 100
    ) -> List[Event]:
        """
        Gibt Event-History zurueck.

        Args:
            event_pattern: Filter-Pattern
            limit: Maximale Anzahl

        Returns:
            Liste der letzten Events
        """
        if event_pattern == "*":
            return self._history[-limit:]

        filtered = [
            e for e in self._history
            if EventHandler(lambda x: None, event_pattern).matches(e.name)
        ]
        return filtered[-limit:]

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurueck."""
        return {
            **self._stats,
            "handlers_registered": len(self._handlers),
            "history_size": len(self._history)
        }

    def clear_history(self):
        """Loescht die Event-History."""
        self._history.clear()

    def enable_history(self, enabled: bool = True):
        """Aktiviert/deaktiviert History-Recording."""
        self._history_enabled = enabled


# =============================================================================
# VORDEFINIERTE EVENTS
# =============================================================================

class HoloEvents:
    """
    Vordefinierte Event-Namen fuer Holocloude.

    Verwendung:
        bus.emit(HoloEvents.USER_MESSAGE, {"text": "Hallo"})
    """

    # System Events
    SYSTEM_STARTUP = "system:startup"
    SYSTEM_SHUTDOWN = "system:shutdown"
    SYSTEM_ERROR = "system:error"
    SYSTEM_WARNING = "system:warning"

    # User Events
    USER_MESSAGE = "user:message"
    USER_REACTION = "user:reaction"
    USER_PRESENCE = "user:presence"
    USER_AWAY = "user:away"

    # Emotion Events
    EMOTION_CHANGED = "emotion:changed"
    EMOTION_INTENSITY = "emotion:intensity"
    MOOD_SHIFT = "mood:shift"

    # Energy Events
    ENERGY_CHANGED = "energy:changed"
    ENERGY_LOW = "energy:low"
    ENERGY_CRITICAL = "energy:critical"
    ENERGY_RESTORED = "energy:restored"

    # LLM Events
    LLM_REQUEST = "llm:request"
    LLM_RESPONSE = "llm:response"
    LLM_ERROR = "llm:error"
    LLM_TIMEOUT = "llm:timeout"

    # Memory Events
    MEMORY_STORED = "memory:stored"
    MEMORY_RECALLED = "memory:recalled"
    MEMORY_FORGOTTEN = "memory:forgotten"

    # Personality Events
    PERSONALITY_TRAIT_CHANGED = "personality:trait_changed"
    PERSONALITY_MOOD_CHANGED = "personality:mood_changed"

    # Activity Events
    ACTIVITY_STARTED = "activity:started"
    ACTIVITY_COMPLETED = "activity:completed"
    ACTIVITY_FAILED = "activity:failed"

    # Device Events
    DEVICE_ONLINE = "device:online"
    DEVICE_OFFLINE = "device:offline"
    DEVICE_STATUS = "device:status"

    # Background Process Events
    PROCESS_STARTED = "process:started"
    PROCESS_STOPPED = "process:stopped"
    PROCESS_ERROR = "process:error"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_event_bus() -> EventBus:
    """Shortcut fuer EventBus.get_instance()."""
    return EventBus.get_instance()


def emit(
    event_name: str,
    data: Optional[Dict] = None,
    source: str = ""
) -> Event:
    """
    Shortcut zum Emittieren eines Events.

    Usage:
        from holo_events import emit
        emit("user:message", {"text": "Hallo"})
    """
    return EventBus.get_instance().emit(event_name, data, source)


def on(event_pattern: str) -> Callable:
    """
    Shortcut-Decorator fuer Event-Handler.

    Usage:
        from holo_events import on

        @on("user:message")
        def handle_message(event):
            print(event.data)
    """
    return EventBus.get_instance().on(event_pattern)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'Event',
    'EventHandler',
    'EventPriority',
    'EventBus',
    'HoloEvents',
    'get_event_bus',
    'emit',
    'on',
]
