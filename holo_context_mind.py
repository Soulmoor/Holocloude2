#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO CONTEXT MIND - Universelles Kontext & Memory System                    ║
║                                                                              ║
║  Ein modulares System das ALLES verwaltet was Holo "weiß":                   ║
║                                                                              ║
║  📍 CONTEXT STORES (Was Holo sich merkt):                                    ║
║     • Chat Context      → Gesprächsverlauf, Themen, User-Aussagen           ║
║     • Learning Context  → Was Holo gelernt hat, neue Fakten                 ║
║     • World Context     → Wetter, News, Events, Externe Welt                ║
║     • Task Context      → Aktuelle Aufgaben, Projekte                       ║
║                                                                              ║
║  🔍 CONTEXT RECALL (Relevanten Kontext abrufen):                            ║
║     • Keyword-basiert                                                        ║
║     • Zeitbasiert (recent, today, this_week)                                ║
║     • Relevanz-Score                                                         ║
║     • Cross-Context Suche                                                    ║
║                                                                              ║
║  🧠 SELF REFLECTION (Über sich selbst nachdenken):                          ║
║     • Was habe ich gelernt?                                                  ║
║     • Wie habe ich mich gefühlt?                                            ║
║     • Was war wichtig?                                                       ║
║     • Muster erkennen                                                        ║
║                                                                              ║
║  NOTE: EmotionalContextTracker wurde nach holo_inner_life.py verschoben     ║
║  NOTE: Selbstreflexion (Deep) wurde nach holo_consciousness.py verschoben   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import math
import random
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)

# =============================================================================
# TIEFENPSYCHOLOGIE-INTEGRATION - Für psychologisch reichere Kontextverarbeitung
# =============================================================================

# Deep Psychology Engine
try:
    from holo_deep_psychology import (
        HoloDeepPsychologyEngine,
        load_or_create_engine as load_deep_psychology,
    )
    DEEP_PSYCHOLOGY_AVAILABLE = True
except ImportError:
    DEEP_PSYCHOLOGY_AVAILABLE = False
    HoloDeepPsychologyEngine = None
    load_deep_psychology = None

# Trauma-Trigger für Kontexterkennung
try:
    from holo_trauma_processing import (
        HoloTraumaProcessingEngine,
        TriggerIntensity,
    )
    TRAUMA_TRIGGERS_AVAILABLE = True
except ImportError:
    TRAUMA_TRIGGERS_AVAILABLE = False
    HoloTraumaProcessingEngine = None
    TriggerIntensity = None

# Unbewusste Trigger
try:
    from holo_unconscious_processes import UnconsciousTriggerSystem
    UNCONSCIOUS_TRIGGERS_AVAILABLE = True
except ImportError:
    UNCONSCIOUS_TRIGGERS_AVAILABLE = False
    UnconsciousTriggerSystem = None


# =============================================================================
# SMART UNDERSTANDING (aus holo_organic.py)
# =============================================================================

_HAS_SMART_UNDERSTANDING = False
_smart_understanding = None

def get_smart_understanding():
    """Lazy-load SmartUnderstanding für Intent Detection"""
    global _HAS_SMART_UNDERSTANDING, _smart_understanding

    if _smart_understanding is not None:
        return _smart_understanding

    try:
        from holo_smart_understanding import SmartUnderstanding
        _smart_understanding = SmartUnderstanding()
        _HAS_SMART_UNDERSTANDING = True
        logger.info("✅ SmartUnderstanding für Intent Detection geladen")
        return _smart_understanding
    except ImportError:
        logger.debug("⚠️ SmartUnderstanding nicht verfügbar - nutze Fallback")
        _HAS_SMART_UNDERSTANDING = False
        return None


# =============================================================================
# IMPORT: EmotionalContextTracker (aus holo_inner_life)
# =============================================================================

try:
    from holo_inner_life import EmotionalContextTracker
    EMOTIONAL_TRACKER_AVAILABLE = True
except ImportError:
    EMOTIONAL_TRACKER_AVAILABLE = False
    # Versuche Enhanced Version aus Integration Layer
    try:
        from holo_integration_layer import EnhancedEmotionalContextTracker as EmotionalContextTracker
        EMOTIONAL_TRACKER_AVAILABLE = True
        logger.info("✅ Using EnhancedEmotionalContextTracker from integration layer")
    except ImportError:
        pass

# Person Opinion Integration
PERSON_OPINIONS_AVAILABLE = False
_person_opinion_manager = None

try:
    from holo_person_opinions import get_person_opinion_manager, PersonInfoTrigger
    PERSON_OPINIONS_AVAILABLE = True
    logger.info("✅ PersonOpinionManager verfügbar")
except ImportError:
    logger.debug("PersonOpinionManager nicht verfügbar")

def get_person_opinions():
    """Lazy-load PersonOpinionManager"""
    global _person_opinion_manager
    if _person_opinion_manager is None and PERSON_OPINIONS_AVAILABLE:
        _person_opinion_manager = get_person_opinion_manager()
    return _person_opinion_manager


# Fallback EmotionalContextTracker if not available
if not EMOTIONAL_TRACKER_AVAILABLE:
    # Fallback: Verbesserte Stub-Klasse (nicht mehr leer!)
    class EmotionalContextTracker:
        """Fallback mit echten Implementierungen"""
        def __init__(self):
            self.user_emotions = []
            self.holo_emotions = []
            self.current_mood = "neutral"
            self.mood_intensity = 0.5
            self.triggers = []
            self.mood_history = []

        def add_user_emotion(self, emotion: str, intensity: float = 0.5,
                             trigger: str = "", context: dict = None):
            """Füge User-Emotion hinzu"""
            self.user_emotions.append({
                "emotion": emotion,
                "intensity": intensity,
                "trigger": trigger,
                "timestamp": time.time(),
                "context": context or {},
            })
            if len(self.user_emotions) > 100:
                self.user_emotions = self.user_emotions[-100:]

        def add_holo_emotion(self, emotion: str, intensity: float = 0.5,
                             reason: str = ""):
            """Füge Holo-Emotion hinzu"""
            self.holo_emotions.append({
                "emotion": emotion,
                "intensity": intensity,
                "reason": reason,
                "timestamp": time.time(),
            })
            if intensity > 0.5:
                self.current_mood = emotion
                self.mood_intensity = intensity
                self.mood_history.append((emotion, intensity, time.time()))
            if len(self.holo_emotions) > 100:
                self.holo_emotions = self.holo_emotions[-100:]

        def get_user_mood_trend(self, hours=24):
            """Analysiere User-Mood-Trend"""
            cutoff = time.time() - (hours * 3600)
            recent = [e for e in self.user_emotions if e["timestamp"] >= cutoff]
            if not recent:
                return "unknown"
            positive = {"happy", "excited", "grateful", "content", "joyful"}
            negative = {"sad", "angry", "frustrated", "anxious", "stressed"}
            pos_count = sum(1 for e in recent if e["emotion"].lower() in positive)
            neg_count = sum(1 for e in recent if e["emotion"].lower() in negative)
            if pos_count > neg_count * 2:
                return "positive"
            elif neg_count > pos_count * 2:
                return "negative"
            return "neutral"

        def get_dominant_emotion(self, recent_only=True):
            """Hole dominante Emotion"""
            emotions = self.holo_emotions[-10:] if recent_only else self.holo_emotions
            if not emotions:
                return None
            from collections import defaultdict
            scores = defaultdict(float)
            now = time.time()
            for e in emotions:
                age = (now - e["timestamp"]) / 3600
                weight = 1.0 / (1 + age)
                scores[e["emotion"]] += e["intensity"] * weight
            return max(scores, key=scores.get) if scores else None

        # === FEHLENDE METHODEN (für Cross-Module Kompatibilität) ===

        def detect_emotion_from_text(self, text: str) -> tuple:
            """Erkennt Emotion aus Text"""
            text_lower = text.lower()
            positive = ["freude", "glücklich", "super", "toll", "danke", "liebe", "schön"]
            negative = ["traurig", "wütend", "frustriert", "ärger", "schlecht", "stress"]

            for word in positive:
                if word in text_lower:
                    return ("happy", 0.7, 0.8)
            for word in negative:
                if word in text_lower:
                    return ("sad", -0.5, 0.7)

            return ("neutral", 0.0, 0.5)

        def add_emotion(self, emotion: str, valence: float, is_user: bool = True, confidence: float = 0.5):
            """Fügt Emotion hinzu"""
            if is_user:
                self.add_user_emotion(emotion, abs(valence))
            else:
                self.add_holo_emotion(emotion, abs(valence))

        def get_current_mood(self) -> tuple:
            """Gibt aktuelle Stimmung zurück"""
            return (self.current_mood, self.mood_intensity)

        def get_trend(self) -> str:
            """Gibt Mood-Trend zurück"""
            if len(self.mood_history) < 2:
                return "stable"
            recent = self.mood_history[-5:]
            avg_intensity = sum(m[1] for m in recent) / len(recent)
            if avg_intensity > 0.6:
                return "positive"
            elif avg_intensity < 0.4:
                return "negative"
            return "stable"

        def needs_support(self) -> bool:
            """Prüft ob User emotionale Unterstützung braucht"""
            recent = self.user_emotions[-5:] if self.user_emotions else []
            if not recent:
                return False
            negative = {"sad", "angry", "frustrated", "anxious", "stressed", "depressed"}
            neg_count = sum(1 for e in recent if e.get("emotion", "").lower() in negative)
            return neg_count >= 2


# =============================================================================
# IMPORT: EmotionTracker (Alias für MoodEvolution aus holo_inner_life)
# =============================================================================

try:
    from holo_inner_life import EmotionTracker
    EMOTION_TRACKER_AVAILABLE = True
except ImportError:
    EMOTION_TRACKER_AVAILABLE = False
    # Fallback: Verbesserte Stub-Klasse (nicht mehr leer!)
    class EmotionTracker:
        """Fallback mit echten Implementierungen"""
        def __init__(self):
            self.current_mood = "neutral"
            self.mood_intensity = 0.5
            self.mood_history = []
            self.triggers = []
            self.decay_rate = 0.1  # Pro Stunde
            self.last_decay = time.time()

        def update_mood(self, mood: str, intensity: float = 0.5,
                        reason: str = ""):
            """Update aktuelles Mood"""
            old_mood = self.current_mood
            self.current_mood = mood
            self.mood_intensity = max(0.0, min(1.0, intensity))
            self.mood_history.append({
                "mood": mood,
                "intensity": intensity,
                "old_mood": old_mood,
                "reason": reason,
                "timestamp": time.time(),
            })
            if len(self.mood_history) > 100:
                self.mood_history = self.mood_history[-100:]

        def add_trigger(self, trigger_type: str, source: str = "",
                        effect: str = "", magnitude: float = 0.5):
            """Füge Trigger hinzu"""
            self.triggers.append({
                "type": trigger_type,
                "source": source,
                "effect": effect,
                "magnitude": magnitude,
                "timestamp": time.time(),
            })
            if len(self.triggers) > 50:
                self.triggers = self.triggers[-50:]

        def get_mood(self):
            """Hole aktuelles Mood"""
            return self.current_mood

        def get_mood_with_intensity(self):
            """Hole Mood mit Intensität"""
            return self.current_mood, self.mood_intensity

        def decay(self):
            """Mood-Decay über Zeit"""
            now = time.time()
            hours_passed = (now - self.last_decay) / 3600
            if hours_passed < 0.1:
                return
            decay_amount = self.decay_rate * hours_passed
            self.mood_intensity = max(0.1, self.mood_intensity - decay_amount)
            if self.mood_intensity < 0.2 and self.current_mood != "neutral":
                self.current_mood = "neutral"
            self.last_decay = now

        def get_trend(self):
            """Analysiere Mood-Trend"""
            if len(self.mood_history) < 3:
                return "stable"
            recent = self.mood_history[-5:]
            intensities = [m["intensity"] for m in recent]
            if len(intensities) < 2:
                return "stable"
            avg_first = sum(intensities[:len(intensities)//2]) / (len(intensities)//2)
            avg_last = sum(intensities[len(intensities)//2:]) / (len(intensities) - len(intensities)//2)
            if avg_last > avg_first + 0.1:
                return "improving"
            elif avg_last < avg_first - 0.1:
                return "declining"
            return "stable"

        def needs_support(self):
            """Prüfe ob emotionale Unterstützung nötig"""
            negative_moods = {"sad", "anxious", "stressed", "frustrated", "lonely"}
            return self.current_mood.lower() in negative_moods and self.mood_intensity > 0.5

        def detect_emotion_from_text(self, text: str):
            """Einfache Emotion-Detection aus Text"""
            text_lower = text.lower()
            emotion_keywords = {
                "happy": ["freue", "glücklich", "toll", "super", "nice", "cool", "yay"],
                "sad": ["traurig", "schlecht", "mies", "down", "depri"],
                "excited": ["aufgeregt", "gespannt", "kann nicht warten"],
                "anxious": ["angst", "nervös", "sorge", "stress"],
                "angry": ["wütend", "sauer", "genervt", "nervig"],
                "grateful": ["danke", "dankbar", "appreciate"],
                "love": ["liebe", "love", "mag dich", "❤"],
            }
            for emotion, keywords in emotion_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    return emotion, 0.7, 0.8  # emotion, valence, confidence
            return "neutral", 0.5, 0.5

        def add_emotion(self, emotion: str, valence: float = 0.5,
                        is_user: bool = True, confidence: float = 0.5):
            """Kompatibilitäts-Methode"""
            self.update_mood(emotion, confidence)

        def get_current_mood(self):
            """Kompatibilitäts-Methode"""
            return self.current_mood, self.mood_intensity


# =============================================================================
# IMPORTS für EnhancedOrganicSystem (aus holo_consciousness + holo_personality)
# =============================================================================

try:
    from holo_consciousness import ConversationMemory, SpontaneousThoughts
    CONSCIOUSNESS_ORGANIC_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_ORGANIC_AVAILABLE = False
    # Fallback: Minimale Stub-Klassen
    class ConversationMemory:
        """Fallback - echte Version in holo_consciousness.py"""
        def __init__(self): self.messages = []
        def add_message(self, *args, **kwargs): pass
        def evaluate_and_store(self, *args, **kwargs): pass
        def recall(self, *args, **kwargs): return []
    class SpontaneousThoughts:
        """Fallback - echte Version in holo_consciousness.py"""
        def __init__(self): pass
        def generate_thought(self, *args, **kwargs): return None

try:
    from holo_personality import NaturalFlow, QuirkSystem, PersonalityExpression
    PERSONALITY_ORGANIC_AVAILABLE = True
except ImportError:
    PERSONALITY_ORGANIC_AVAILABLE = False
    # Fallback: Minimale Stub-Klassen
    class NaturalFlow:
        """Fallback - echte Version in holo_personality.py"""
        def __init__(self): pass
        def enhance_with_flow(self, text, *args, **kwargs): return text
    class QuirkSystem:
        """Fallback - echte Version in holo_personality.py"""
        def __init__(self): pass
        def should_quirk(self): return False
        def apply_quirk(self, text): return text
    class PersonalityExpression:
        """Fallback - echte Version in holo_personality.py"""
        def __init__(self): pass
        def enhance_response(self, text, *args, **kwargs): return text


# =============================================================================
# CONTEXT TYPES - Importiert aus holo_core_types (zentrale Definition)
# =============================================================================

from holo_core_types import ContextType, Importance


# =============================================================================
# CONTEXT ENTRY
# =============================================================================

@dataclass
class ContextEntry:
    """Ein einzelner Kontext-Eintrag"""
    id: str
    context_type: ContextType
    content: str

    # Metadaten
    timestamp: float = field(default_factory=time.time)
    importance: Importance = Importance.NORMAL
    keywords: List[str] = field(default_factory=list)

    # Verknüpfungen
    related_ids: List[str] = field(default_factory=list)
    source: str = ""  # Woher kommt die Info?

    # Für Suche
    embedding: Optional[List[float]] = None  # Für späteres Embedding

    # Decay
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    decay_rate: float = 0.1  # Wie schnell vergessen?

    def to_dict(self) -> Dict:
        """Konvertiere zu Dict für Speicherung"""
        return {
            "id": self.id,
            "context_type": self.context_type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "importance": self.importance.value,
            "keywords": self.keywords,
            "related_ids": self.related_ids,
            "source": self.source,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "decay_rate": self.decay_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ContextEntry':
        """Erstelle aus Dict"""
        return cls(
            id=data["id"],
            context_type=ContextType(data["context_type"]),
            content=data["content"],
            timestamp=data.get("timestamp", time.time()),
            importance=Importance(data.get("importance", 2)),
            keywords=data.get("keywords", []),
            related_ids=data.get("related_ids", []),
            source=data.get("source", ""),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", time.time()),
            decay_rate=data.get("decay_rate", 0.1),
        )

    def get_relevance_score(self, query_keywords: List[str] = None) -> float:
        """Berechne Relevanz-Score"""
        score = 0.0

        # Basis: Wichtigkeit
        score += self.importance.value * 0.2

        # Aktualität (neuere = relevanter)
        age_hours = (time.time() - self.timestamp) / 3600
        recency_score = max(0, 1 - (age_hours / 168))  # 1 Woche = 0
        score += recency_score * 0.3

        # Zugriffs-Häufigkeit
        access_score = min(1.0, self.access_count / 10)
        score += access_score * 0.2

        # Keyword-Match
        if query_keywords:
            matches = sum(1 for k in query_keywords if k in self.keywords)
            if self.keywords:
                keyword_score = matches / len(query_keywords) if query_keywords else 0
                score += keyword_score * 0.3

        return min(1.0, score)


# =============================================================================
# CONTEXT STORE
# =============================================================================

class ContextStore:
    """
    Speicher für einen Kontext-Typ.

    Verwaltet Einträge, Suche, Decay.
    """

    def __init__(self, context_type: ContextType, max_entries: int = 1000):
        self.context_type = context_type
        self.max_entries = max_entries
        self.entries: Dict[str, ContextEntry] = {}
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)  # keyword → entry_ids

    def add(self, content: str,
            keywords: List[str] = None,
            importance: Importance = Importance.NORMAL,
            source: str = "",
            related_ids: List[str] = None) -> ContextEntry:
        """Füge neuen Eintrag hinzu"""

        # ID generieren
        entry_id = self._generate_id(content)

        # Keywords extrahieren wenn nicht gegeben
        if keywords is None:
            keywords = self._extract_keywords(content)

        entry = ContextEntry(
            id=entry_id,
            context_type=self.context_type,
            content=content,
            keywords=keywords,
            importance=importance,
            source=source,
            related_ids=related_ids or [],
        )

        # Speichern
        self.entries[entry_id] = entry

        # Keyword-Index aktualisieren
        for kw in keywords:
            self.keyword_index[kw.lower()].add(entry_id)

        # Cleanup wenn zu voll
        if len(self.entries) > self.max_entries:
            self._cleanup_old_entries()

        return entry

    def get(self, entry_id: str) -> Optional[ContextEntry]:
        """Hole Eintrag und aktualisiere Zugriff"""
        entry = self.entries.get(entry_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = time.time()
        return entry

    def search(self, query: str = None,
               keywords: List[str] = None,
               time_range: Tuple[float, float] = None,
               min_importance: Importance = None,
               limit: int = 10) -> List[ContextEntry]:
        """
        Suche nach Einträgen.

        Args:
            query: Freitext-Suche
            keywords: Keyword-Filter
            time_range: (start, end) Timestamps
            min_importance: Mindest-Wichtigkeit
            limit: Max Ergebnisse
        """
        results = []

        # Keywords aus Query extrahieren
        if query and not keywords:
            keywords = self._extract_keywords(query)

        # Kandidaten sammeln
        if keywords:
            candidate_ids = set()
            for kw in keywords:
                candidate_ids.update(self.keyword_index.get(kw.lower(), set()))
            candidates = [self.entries[eid] for eid in candidate_ids if eid in self.entries]
        else:
            candidates = list(self.entries.values())

        # Filtern
        for entry in candidates:
            # Zeit-Filter
            if time_range:
                if not (time_range[0] <= entry.timestamp <= time_range[1]):
                    continue

            # Wichtigkeits-Filter
            if min_importance and entry.importance.value < min_importance.value:
                continue

            # Relevanz berechnen
            entry._relevance = entry.get_relevance_score(keywords)
            results.append(entry)

        # Sortieren nach Relevanz
        results.sort(key=lambda e: e._relevance, reverse=True)

        # Zugriff aktualisieren
        for entry in results[:limit]:
            entry.access_count += 1
            entry.last_accessed = time.time()

        return results[:limit]

    def get_recent(self, hours: int = 24, limit: int = 20) -> List[ContextEntry]:
        """Hole kürzliche Einträge"""
        cutoff = time.time() - (hours * 3600)
        recent = [e for e in self.entries.values() if e.timestamp >= cutoff]
        recent.sort(key=lambda e: e.timestamp, reverse=True)
        return recent[:limit]

    def get_important(self, min_level: Importance = Importance.HIGH,
                     limit: int = 10) -> List[ContextEntry]:
        """Hole wichtige Einträge"""
        important = [
            e for e in self.entries.values()
            if e.importance.value >= min_level.value
        ]
        important.sort(key=lambda e: (e.importance.value, e.timestamp), reverse=True)
        return important[:limit]

    def update(self, entry_id: str, **kwargs) -> bool:
        """Aktualisiere einen Eintrag"""
        entry = self.entries.get(entry_id)
        if not entry:
            return False

        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        # Keywords neu indexieren wenn geändert
        if "keywords" in kwargs:
            # Alte entfernen
            for kw_set in self.keyword_index.values():
                kw_set.discard(entry_id)
            # Neue hinzufügen
            for kw in entry.keywords:
                self.keyword_index[kw.lower()].add(entry_id)

        return True

    def delete(self, entry_id: str) -> bool:
        """Lösche einen Eintrag"""
        if entry_id not in self.entries:
            return False

        entry = self.entries[entry_id]

        # Aus Index entfernen
        for kw in entry.keywords:
            self.keyword_index[kw.lower()].discard(entry_id)

        del self.entries[entry_id]
        return True

    def _generate_id(self, content: str) -> str:
        """Generiere eindeutige ID"""
        data = f"{content}{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiere Keywords aus Text"""
        # Stopwords
        stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber",
            "ich", "du", "er", "sie", "es", "wir", "ihr", "sie",
            "ist", "sind", "war", "bin", "hat", "haben", "wird",
            "zu", "in", "an", "auf", "für", "mit", "von", "bei",
            "ja", "nein", "nicht", "auch", "nur", "noch", "schon",
            "mal", "denn", "doch", "so", "sehr", "ganz", "dass",
        }

        # Wörter extrahieren
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]

        return list(set(keywords))[:10]  # Max 10 Keywords

    def _cleanup_old_entries(self):
        """Entferne alte/unwichtige Einträge"""
        if len(self.entries) <= self.max_entries:
            return

        # Score berechnen (niedrig = kann weg)
        scored = []
        for entry in self.entries.values():
            # Wichtige behalten
            if entry.importance.value >= Importance.HIGH.value:
                continue

            score = entry.get_relevance_score()
            scored.append((entry.id, score))

        # Niedrigste Scores löschen
        scored.sort(key=lambda x: x[1])
        to_delete = len(self.entries) - self.max_entries + 100  # Puffer

        for entry_id, _ in scored[:to_delete]:
            self.delete(entry_id)

    def to_dict(self) -> Dict:
        """Exportiere für Speicherung"""
        return {
            "context_type": self.context_type.value,
            "entries": [e.to_dict() for e in self.entries.values()],
        }

    def from_dict(self, data: Dict):
        """Importiere aus Speicherung"""
        for entry_data in data.get("entries", []):
            entry = ContextEntry.from_dict(entry_data)
            self.entries[entry.id] = entry
            for kw in entry.keywords:
                self.keyword_index[kw.lower()].add(entry.id)


# =============================================================================
# TOPIC TRACKER (MERGED aus autonomy_engine.py + organic.py)
# =============================================================================

@dataclass
class TrackedTopic:
    """Ein Thema das Holo verfolgt"""
    topic: str
    first_mentioned: float = field(default_factory=time.time)
    last_mentioned: float = field(default_factory=time.time)
    mention_count: int = 1
    user_sentiment: str = "neutral"    # positive, negative, neutral
    needs_followup: bool = False
    followup_sent: bool = False
    context: str = ""                  # Kontext warum wichtig
    category: str = "general"          # Themen-Kategorie
    introduced_by: str = "user"        # user oder holo

    def should_followup(self, followup_delay_hours: int = 24) -> bool:
        """Sollte nachgefragt werden?"""
        if self.followup_sent:
            return False
        if not self.needs_followup:
            return False

        hours_since = (time.time() - self.last_mentioned) / 3600
        return hours_since >= followup_delay_hours

    def get_score(self, now: float = None) -> float:
        """Berechne Relevanz-Score"""
        now = now or time.time()
        recency = 1.0 / (1 + (now - self.last_mentioned) / 3600)
        frequency = math.log(1 + self.mention_count)
        followup_boost = 2.0 if self.needs_followup and not self.followup_sent else 1.0
        return recency * frequency * followup_boost


class TopicTracker:
    """
    Verfolgt Gesprächsthemen über Zeit.

    MERGED Features aus:
    - autonomy_engine.py: Follow-up Tracking, Importance Triggers
    - organic.py: Kategorisierung, Decay, Scoring, History

    Features:
    - Themen-Erkennung aus Text
    - Themen-Kategorisierung
    - Wichtigkeits-Trigger für Follow-ups
    - Themen-Decay (alte verlieren Relevanz)
    - Scoring-System
    """

    # Themen-Kategorien (aus organic.py)
    TOPIC_CATEGORIES = {
        "technical": ["computer", "software", "hardware", "code", "programmieren",
                      "server", "nas", "netzwerk", "api", "datenbank", "python",
                      "javascript", "raspberry", "linux", "docker"],
        "personal": ["gefühl", "emotion", "freude", "traurig", "müde", "stress",
                     "liebe", "freund", "familie", "beziehung", "leben"],
        "work": ["arbeit", "job", "projekt", "meeting", "chef", "kollege",
                 "deadline", "aufgabe", "büro", "karriere"],
        "hobbies": ["spiel", "musik", "film", "buch", "sport", "kochen",
                    "reisen", "hobby", "kreativ", "gaming", "anime"],
        "holo": ["holo", "wolf", "traum", "energie", "stimmung", "wedeln",
                 "ohren", "schweif"],
        "home": ["licht", "lampe", "temperatur", "heizung", "wohnzimmer",
                 "küche", "schlafzimmer", "smart", "home"],
        "meta": ["verstehen", "erklär", "hilfe", "kannst", "funktion", "wie"],
    }

    # Stopwords die keine Themen sind (aus organic.py)
    STOPWORDS = {
        "der", "die", "das", "ein", "eine", "und", "oder", "aber",
        "ich", "du", "er", "sie", "es", "wir", "ihr",
        "ist", "sind", "war", "bin", "hat", "haben", "wird",
        "zu", "in", "an", "auf", "für", "mit", "von", "bei",
        "nicht", "auch", "noch", "schon", "dann", "wenn", "als",
        "dass", "weil", "obwohl", "damit", "also", "denn",
        "mal", "nur", "sehr", "ganz", "etwa", "vielleicht",
    }

    # Trigger-Wörter für wichtige Themen / Follow-ups (aus autonomy_engine.py)
    IMPORTANCE_TRIGGERS = {
        "high": [
            "wichtig", "dringend", "problem", "sorge", "stress",
            "krank", "arzt", "termin", "prüfung", "bewerbung",
            "projekt", "deadline", "interview", "date",
        ],
        "emotional": [
            "traurig", "glücklich", "aufgeregt", "nervös", "ängstlich",
            "wütend", "frustriert", "enttäuscht", "stolz", "verliebt",
        ],
        "future": [
            "morgen", "nächste woche", "bald", "später", "vorhaben",
            "plane", "will", "werde", "möchte",
        ],
    }

    def __init__(self, max_topics: int = 30, followup_delay_hours: int = 24,
                 decay_hours: float = 24.0):
        self.max_topics = max_topics
        self.followup_delay_hours = followup_delay_hours
        self.decay_hours = decay_hours
        self.topics: Dict[str, TrackedTopic] = {}
        self.current_focus: Optional[str] = None
        self.topic_history: List[Tuple[str, float]] = []

    def add_message(self, text: str, is_user: bool = True) -> List[str]:
        """
        Extrahiere und tracke Themen aus Nachricht automatisch.

        Returns: Liste neuer Themen
        """
        now = time.time()

        # Wörter extrahieren (nur bedeutsame)
        words = text.lower().split()
        significant_words = [
            w for w in words
            if len(w) > 3 and w.isalpha() and w not in self.STOPWORDS
        ]

        new_topics = []
        for word in significant_words:
            category = self._categorize(word)
            needs_followup = self._check_importance(word)

            if word in self.topics:
                self.topics[word].last_mentioned = now
                self.topics[word].mention_count += 1
            else:
                self.topics[word] = TrackedTopic(
                    topic=word,
                    category=category,
                    introduced_by="user" if is_user else "holo",
                    needs_followup=needs_followup,
                )
                new_topics.append(word)

        # Fokus aktualisieren
        if significant_words:
            self.current_focus = significant_words[-1]
            self.topic_history.append((self.current_focus, now))

        # Cleanup
        self._cleanup()

        return new_topics

    def _categorize(self, word: str) -> str:
        """Kategorisiere ein Thema"""
        word_lower = word.lower()
        for category, keywords in self.TOPIC_CATEGORIES.items():
            if any(kw in word_lower or word_lower in kw for kw in keywords):
                return category
        return "general"

    def _check_importance(self, word: str) -> bool:
        """Prüfe ob Wort wichtig ist (Follow-up nötig)"""
        word_lower = word.lower()
        for triggers in self.IMPORTANCE_TRIGGERS.values():
            if any(t in word_lower or word_lower in t for t in triggers):
                return True
        return False

    def extract_topics(self, message: str, sentiment: str = "neutral") -> List[Tuple[str, str, str]]:
        """
        Extrahiere wichtige Themen aus Nachricht (für Follow-ups).

        Returns: List von (trigger, context, category)
        """
        message_lower = message.lower()
        extracted = []

        for category, triggers in self.IMPORTANCE_TRIGGERS.items():
            for trigger in triggers:
                if trigger in message_lower:
                    idx = message_lower.find(trigger)
                    start = max(0, idx - 20)
                    end = min(len(message), idx + len(trigger) + 20)
                    context = message[start:end].strip()
                    extracted.append((trigger, context, category))

        return extracted

    def track(self, topic: str, context: str = "",
              sentiment: str = "neutral", needs_followup: bool = False,
              category: str = None):
        """Tracke ein spezifisches Thema manuell"""
        if topic in self.topics:
            self.topics[topic].last_mentioned = time.time()
            self.topics[topic].mention_count += 1
            if sentiment != "neutral":
                self.topics[topic].user_sentiment = sentiment
            if needs_followup:
                self.topics[topic].needs_followup = True
        else:
            self.topics[topic] = TrackedTopic(
                topic=topic,
                user_sentiment=sentiment,
                needs_followup=needs_followup,
                context=context,
                category=category or self._categorize(topic),
            )

        if len(self.topics) > self.max_topics:
            self._cleanup()

    def get_top_topics(self, n: int = 5, category: str = None) -> List[str]:
        """Hole die wichtigsten Themen nach Score"""
        now = time.time()

        filtered = self.topics
        if category:
            filtered = {k: v for k, v in filtered.items() if v.category == category}

        scored = [(topic, data.get_score(now)) for topic, data in filtered.items()]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [t[0] for t in scored[:n]]

    def get_followup_topics(self) -> List[TrackedTopic]:
        """Hole Themen die Followup brauchen"""
        return [
            t for t in self.topics.values()
            if t.should_followup(self.followup_delay_hours)
        ]

    def mark_followup_sent(self, topic: str):
        """Markiere Followup als gesendet"""
        if topic in self.topics:
            self.topics[topic].followup_sent = True

    def get_recent_topics(self, hours: int = 24) -> List[TrackedTopic]:
        """Hole kürzlich erwähnte Themen"""
        cutoff = time.time() - (hours * 3600)
        return [t for t in self.topics.values() if t.last_mentioned >= cutoff]

    def get_category_distribution(self) -> Dict[str, int]:
        """Hole Verteilung der Themen-Kategorien"""
        categories = [v.category for v in self.topics.values()]
        return dict(Counter(categories))

    def is_new_topic(self, word: str) -> bool:
        """Prüfe ob ein Thema neu ist"""
        return word.lower() not in self.topics

    def get_topic_continuity(self, new_topics: List[str]) -> float:
        """Wie sehr hängen neue Topics mit aktuellen zusammen?"""
        if not self.topics or not new_topics:
            return 0.0

        current = set(self.topics.keys())
        new_set = set(t.lower() for t in new_topics)

        # Direkte Überlappung
        overlap = len(current & new_set)

        # Kategorie-Überlappung
        current_cats = set(v.category for v in self.topics.values())
        new_cats = set(self._categorize(t) for t in new_topics)
        cat_overlap = len(current_cats & new_cats)

        return min(1.0, (overlap * 0.5 + cat_overlap * 0.3) / max(len(new_topics), 1))

    def get_conversation_theme(self) -> Optional[str]:
        """Ermittle das übergreifende Gesprächsthema"""
        if not self.topics:
            return None

        cat_dist = self.get_category_distribution()
        if cat_dist:
            return max(cat_dist, key=cat_dist.get)
        return None

    def suggest_topic_callback(self) -> Optional[str]:
        """Schlage ein Thema für Rückbezug vor"""
        now = time.time()

        candidates = []
        for topic, data in self.topics.items():
            if data.mention_count >= 2:
                age = now - data.last_mentioned
                if age > 300:  # Mehr als 5 Minuten her
                    candidates.append((topic, data.mention_count))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        return None

    def _topic_score(self, topic_data: TrackedTopic, now: float = None) -> float:
        """Berechne Relevanz-Score für ein Thema"""
        now = now or time.time()
        recency = 1.0 / (1 + (now - topic_data.last_mentioned) / 3600)
        frequency = math.log(1 + topic_data.mention_count)
        followup_boost = 2.0 if topic_data.needs_followup and not topic_data.followup_sent else 1.0
        return recency * frequency * followup_boost

    def _cleanup(self):
        """Entferne alte unwichtige Themen"""
        now = time.time()
        scored = []
        for topic, data in self.topics.items():
            age_hours = (now - data.last_mentioned) / 3600
            score = data.mention_count / (1 + age_hours * 0.1)
            if data.needs_followup and not data.followup_sent:
                score *= 2
            scored.append((topic, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        keep = [t[0] for t in scored[:self.max_topics]]

        self.topics = {k: v for k, v in self.topics.items() if k in keep}

    # Alias für Kompatibilität mit autonomy_engine.py
    def _cleanup_old_topics(self):
        """Alias für _cleanup - Kompatibilität mit autonomy_engine.py"""
        return self._cleanup()


# =============================================================================
# CHAT CONTEXT TRACKER
# =============================================================================

class ChatContextTracker:
    """
    Spezieller Tracker für Gesprächskontext.

    Merkt sich:
    - Aktuelle Themen
    - User-Aussagen
    - Fragen & Antworten
    - Gesprächsfluss
    """

    def __init__(self):
        self.current_topics: List[str] = []
        self.topic_history: List[Dict] = []
        self.unanswered_questions: List[Dict] = []
        self.user_statements: List[Dict] = []
        self.conversation_summary: str = ""
        self.turn_count: int = 0

    def add_turn(self, role: str, content: str,
                 topics: List[str] = None,
                 is_question: bool = False,
                 question_answered: bool = False):
        """Füge eine Gesprächsrunde hinzu"""
        self.turn_count += 1

        # Topics aktualisieren
        if topics:
            for topic in topics:
                if topic not in self.current_topics:
                    self.current_topics.append(topic)

            # Topic-History
            self.topic_history.append({
                "turn": self.turn_count,
                "topics": topics,
                "timestamp": time.time(),
            })

        # Fragen tracken
        if is_question and role == "user":
            self.unanswered_questions.append({
                "turn": self.turn_count,
                "content": content,
                "timestamp": time.time(),
            })

        # Frage beantwortet?
        if question_answered and self.unanswered_questions:
            self.unanswered_questions.pop(0)

        # User-Aussagen speichern
        if role == "user" and not is_question:
            self.user_statements.append({
                "turn": self.turn_count,
                "content": content,
                "timestamp": time.time(),
            })

        # Alte Topics entfernen (älter als 10 Turns)
        if len(self.current_topics) > 5:
            self.current_topics = self.current_topics[-5:]

    def get_context_summary(self) -> str:
        """Generiere Kontext-Zusammenfassung"""
        parts = []

        if self.current_topics:
            parts.append(f"Aktuelle Themen: {', '.join(self.current_topics)}")

        if self.unanswered_questions:
            questions = [q["content"][:50] for q in self.unanswered_questions[-3:]]
            parts.append(f"Offene Fragen: {'; '.join(questions)}")

        if self.user_statements:
            recent = self.user_statements[-3:]
            statements = [s["content"][:50] for s in recent]
            parts.append(f"User erwähnte: {'; '.join(statements)}")

        return " | ".join(parts) if parts else "Kein besonderer Kontext."

    def has_open_questions(self) -> bool:
        """Gibt es unbeantwortete Fragen?"""
        return len(self.unanswered_questions) > 0

    def get_topic_continuity(self, new_topics: List[str]) -> float:
        """Wie sehr hängen neue Topics mit aktuellen zusammen?"""
        if not self.current_topics or not new_topics:
            return 0.0

        matches = sum(1 for t in new_topics if t in self.current_topics)
        return matches / len(new_topics)


# =============================================================================
# EMOTIONAL CONTEXT TRACKER - VERSCHOBEN nach holo_inner_life.py
# =============================================================================
# EmotionalContextTracker wurde nach holo_inner_life.py verschoben.
# Import von dort:
#   from holo_inner_life import EmotionalContextTracker
# =============================================================================


# =============================================================================
# SELF REFLECTION ENGINE - VERSCHOBEN nach holo_consciousness.py
# =============================================================================
# SelfReflectionEngine wurde in SelfReflection (holo_consciousness.py) integriert.
# Für Rückwärtskompatibilität existiert dieser Wrapper.
#
# NEU: from holo_consciousness import SelfReflection
#      sr = SelfReflection()
#      sr.set_context_mind(context_mind)  # Für datenbasierte Reflexion
# =============================================================================

class SelfReflectionEngine:
    """
    DEPRECATED: Verwende SelfReflection aus holo_consciousness.py

    Dieser Wrapper existiert nur für Rückwärtskompatibilität.
    Die Funktionalität wurde nach holo_consciousness.py verschoben.
    """

    def __init__(self, context_mind: 'HoloContextMind'):
        self.context_mind = context_mind
        self.reflections: List[Dict] = []

        # Versuche echte SelfReflection zu nutzen
        try:
            from holo_consciousness import SelfReflection
            self._real_reflection = SelfReflection()
            self._real_reflection.set_context_mind(context_mind)
        except ImportError:
            self._real_reflection = None

    def reflect_on_conversation(self) -> Dict:
        """Reflektiere über das aktuelle Gespräch"""
        if self._real_reflection:
            # Nutze die neue Version mit Chat-Daten
            chat = self.context_mind.chat_tracker
            summary = {
                "topics": chat.current_topics if hasattr(chat, 'current_topics') else [],
                "has_open_questions": chat.has_open_questions() if hasattr(chat, 'has_open_questions') else False,
            }
            return self._real_reflection.reflect_on_conversation(summary)

        # Fallback
        return {"timestamp": time.time(), "type": "conversation", "insights": []}

    def reflect_on_learning(self) -> Dict:
        """Reflektiere über Gelerntes"""
        if self._real_reflection:
            return self._real_reflection.reflect_on_learning()
        return {"timestamp": time.time(), "type": "learning", "insights": []}

    def reflect_on_emotions(self) -> Dict:
        """Reflektiere über emotionalen Verlauf"""
        if self._real_reflection:
            return self._real_reflection.reflect_on_emotions_data()
        return {"timestamp": time.time(), "type": "emotional", "insights": []}

    def generate_daily_summary(self) -> str:
        """Generiere Tages-Zusammenfassung"""
        if self._real_reflection:
            return self._real_reflection.generate_daily_summary()
        return "Keine Zusammenfassung verfügbar."

    def ask_self(self, question: str) -> str:
        """Frage über sich selbst beantworten"""
        if self._real_reflection:
            return self._real_reflection.ask_self(question)
        return "Darüber muss ich nachdenken..."


# =============================================================================
# DISCOURSE MANAGEMENT (aus holo_organic.py)
# =============================================================================

@dataclass
class DiscourseUnit:
    """Eine Einheit im Gesprächsverlauf"""
    user_message: str
    holo_response: str
    intent: str
    timestamp: float = field(default_factory=time.time)
    topic: str = None
    emotion: str = None
    resolved: bool = True


class DiscourseManager:
    """
    Verwaltet den Gesprächsfluss.

    Features:
    - Trackt Frage-Antwort-Paare
    - Erkennt offene Fäden
    - Ermöglicht Rückbezüge
    - Misst Gesprächstiefe
    - Erkennt Themenwechsel
    """

    def __init__(self, max_history: int = 50):
        self.history: List[DiscourseUnit] = []
        self.max_history = max_history
        self.open_threads: List[str] = []
        self.depth = 0
        self.topic_changes: List[Tuple[str, str, float]] = []

    def add_exchange(self, user_msg: str, holo_response: str,
                     intent: str, topic: str = None, emotion: str = None):
        """Füge einen Austausch hinzu"""
        if topic and self.history:
            last_topic = self._get_last_topic()
            if last_topic and last_topic != topic:
                self.topic_changes.append((last_topic, topic, time.time()))

        unit = DiscourseUnit(
            user_message=user_msg,
            holo_response=holo_response,
            intent=intent,
            topic=topic,
            emotion=emotion,
            resolved=self._is_resolved(intent, holo_response)
        )

        self.history.append(unit)

        if not unit.resolved:
            self.open_threads.append(user_msg[:50])

        self._update_depth()

        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def _get_last_topic(self) -> Optional[str]:
        """Hole letztes Thema"""
        for unit in reversed(self.history):
            if unit.topic:
                return unit.topic
        return None

    def _is_resolved(self, intent: str, response: str) -> bool:
        """Prüfe ob Anfrage beantwortet wurde"""
        # All indicators must be lowercase for comparison with response.lower()
        unresolved_indicators = ["weiß nicht", "später", "mal sehen", "keine ahnung", "ich weiß es nicht"]
        return not any(ind in response.lower() for ind in unresolved_indicators)

    def _update_depth(self):
        """Aktualisiere Gesprächstiefe"""
        if len(self.history) < 2:
            self.depth = 1
            return

        last_topic = self.history[-1].topic
        same_topic_count = 0
        for unit in reversed(self.history):
            if unit.topic == last_topic:
                same_topic_count += 1
            else:
                break

        self.depth = min(5, same_topic_count)

    def get_open_threads(self) -> List[str]:
        """Hole offene Gesprächsfäden"""
        return self.open_threads[-5:]

    def get_recent_topics(self, n: int = 5) -> List[str]:
        """Hole letzte Themen"""
        topics = []
        for unit in reversed(self.history):
            if unit.topic and unit.topic not in topics:
                topics.append(unit.topic)
                if len(topics) >= n:
                    break
        return topics

    def resolve_thread(self, topic: str):
        """Markiere Faden als abgeschlossen"""
        if topic in self.open_threads:
            self.open_threads.remove(topic)
            self.depth = max(0, self.depth - 1)

    def get_context_for_response(self) -> Dict:
        """Hole Kontext für Antwort-Generierung"""
        recent = self.history[-5:] if self.history else []

        return {
            "depth": self.depth,
            "open_threads": self.open_threads,
            "recent_topics": [u.topic for u in recent if u.topic],
            "recent_emotions": [u.emotion for u in recent if u.emotion],
            "last_intent": recent[-1].intent if recent else None,
            "exchange_count": len(self.history),
        }

    def get_conversation_summary(self) -> Dict:
        """Zusammenfassung des Gesprächs"""
        return {
            "total_exchanges": len(self.history),
            "depth": self.depth,
            "open_threads": len(self.open_threads),
            "topic_changes": len(self.topic_changes),
            "recent_topics": self.get_recent_topics(3),
        }

    def should_summarize(self) -> bool:
        """Prüfe ob eine Zusammenfassung sinnvoll wäre"""
        return len(self.history) > 10 and len(self.history) % 10 == 0


class AnaphoraResolver:
    """
    Löst Pronomen und Referenzen auf.

    z.B. "er", "sie", "es", "das", "dort" → worauf bezieht sich das?
    """

    PRONOUNS = {
        "personal_male": ["er", "ihn", "ihm", "seiner"],
        "personal_female": ["sie", "ihr", "ihrer"],
        "personal_neutral": ["es"],
        "demonstrative": ["das", "dies", "dieses", "jenes", "dieser", "diese"],
        "relative": ["der", "die", "welcher", "welche", "welches"],
        "locative": ["dort", "da", "hier", "dahin", "dorthin"],
        "temporal": ["dann", "damals", "danach", "vorher", "dabei"],
        "topic": ["darüber", "davon", "dazu", "damit", "dafür", "dagegen"],
    }

    ALL_PRONOUNS = set()
    for group in PRONOUNS.values():
        ALL_PRONOUNS.update(group)

    def __init__(self):
        self.entity_stack: List[Dict] = []
        self.location_stack: List[str] = []
        self.topic_stack: List[str] = []
        self.time_stack: List[str] = []

    def add_entity(self, entity: str, entity_type: str, gender: str = "neutral"):
        """Füge Entity zum Stack hinzu"""
        self.entity_stack.append({
            "entity": entity,
            "type": entity_type,
            "gender": gender,
            "timestamp": time.time(),
        })

        if len(self.entity_stack) > 10:
            self.entity_stack.pop(0)

    def add_location(self, location: str):
        """Füge Ort hinzu"""
        self.location_stack.append(location)
        if len(self.location_stack) > 5:
            self.location_stack.pop(0)

    def add_topic(self, topic: str):
        """Füge Thema hinzu"""
        self.topic_stack.append(topic)
        if len(self.topic_stack) > 5:
            self.topic_stack.pop(0)

    def resolve(self, text: str) -> str:
        """Löse Pronomen im Text auf"""
        words = text.lower().split()
        resolved = text

        for word in words:
            if word in self.ALL_PRONOUNS:
                replacement = self._find_referent(word)
                if replacement and replacement != word:
                    resolved = resolved.replace(f" {word} ", f" {replacement} ", 1)

        return resolved

    def _find_referent(self, pronoun: str) -> Optional[str]:
        """Finde Bezug für Pronomen"""
        if pronoun in self.PRONOUNS["personal_male"]:
            return self._find_entity_by_gender("male")
        elif pronoun in self.PRONOUNS["personal_female"]:
            return self._find_entity_by_gender("female")
        elif pronoun in self.PRONOUNS["locative"]:
            return self.location_stack[-1] if self.location_stack else None
        elif pronoun in self.PRONOUNS["topic"]:
            return self.topic_stack[-1] if self.topic_stack else None
        elif pronoun in self.PRONOUNS["demonstrative"]:
            return self.entity_stack[-1]["entity"] if self.entity_stack else None
        return None

    def _find_entity_by_gender(self, gender: str) -> Optional[str]:
        """Finde Entity nach Geschlecht"""
        for entity in reversed(self.entity_stack):
            if entity["gender"] == gender:
                return entity["entity"]
        return self.entity_stack[-1]["entity"] if self.entity_stack else None

    def has_unresolved_reference(self, text: str) -> bool:
        """Prüfe ob Text ungelöste Referenzen hat"""
        words = set(text.lower().split())
        return bool(words & self.ALL_PRONOUNS)

    def has_reference(self, text: str) -> bool:
        """Alias für has_unresolved_reference"""
        return self.has_unresolved_reference(text)

    def resolve_in_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Löse alle Pronomen im Text auf.

        Returns: (text_with_annotations, resolutions)
        """
        words = text.split()
        resolutions = {}
        resolved_words = []

        for word in words:
            word_clean = word.lower().strip(".,!?")
            resolution = self.resolve(word_clean) if word_clean in self.ALL_PRONOUNS else None

            if resolution:
                resolutions[word_clean] = resolution
                resolved_words.append(f"{word}[→{resolution}]")
            else:
                resolved_words.append(word)

        return " ".join(resolved_words), resolutions

    def get_reference_context(self) -> Dict:
        """Hole Referenz-Kontext"""
        return {
            "last_entity": self.entity_stack[-1]["entity"] if self.entity_stack else None,
            "last_location": self.location_stack[-1] if self.location_stack else None,
            "last_topic": self.topic_stack[-1] if self.topic_stack else None,
            "entities": [e["entity"] for e in self.entity_stack[-3:]],
        }


class IntentDetector:
    """Erkennt die Intention hinter einer Nachricht"""

    INTENT_PATTERNS = {
        "question": ["?", "was ", "wie ", "wo ", "wer ", "wann ", "warum ", "wieso "],
        "command": ["mach ", "tu ", "zeig ", "hilf ", "erkläre ", "finde "],
        "statement": ["ich ", "mein ", "mir ", "wir "],
        "greeting": ["hallo", "hi ", "hey ", "guten ", "morgen", "abend"],
        "farewell": ["tschüss", "bye", "bis ", "gute nacht", "ciao"],
        "gratitude": ["danke", "thanks", "dankeschön", "vielen dank"],
        "emotional": ["liebe", "hasse", "traurig", "glücklich", "wütend"],
    }

    def __init__(self):
        self._understanding = None

    def _get_understanding(self):
        """
        Hole SmartUnderstanding (lazy loading).

        Hinweis: SmartUnderstanding ist eine optionale externe Abhängigkeit.
        Wenn nicht verfügbar, wird None zurückgegeben.
        """
        if self._understanding is None:
            # Nutze die lokale get_smart_understanding() Funktion (oben definiert)
            self._understanding = get_smart_understanding()
        return self._understanding

    @classmethod
    def detect(cls, text: str) -> str:
        """Erkenne Intent"""
        text_lower = text.lower()

        for intent, patterns in cls.INTENT_PATTERNS.items():
            if any(p in text_lower for p in patterns):
                return intent

        return "statement"

    @classmethod
    def detect_intent(cls, text: str) -> Dict:
        """Erkenne Intent mit Details (Alias für detect mit mehr Infos)"""
        intent = cls.detect(text)
        return {
            "intent": intent,
            "confidence": 0.8 if intent != "statement" else 0.5,
            "requires_llm": True,
        }


class SmartIntentDetector(IntentDetector):
    """Erweiterte Intent-Erkennung mit Kontext"""

    def __init__(self):
        self.conversation_context: List[str] = []
        self.last_intent: str = "statement"

    def detect_with_context(self, text: str) -> Tuple[str, float]:
        """Erkenne Intent mit Konfidenz"""
        base_intent = self.detect(text)
        confidence = 0.7

        # Kontext berücksichtigen
        if self.last_intent == "question" and len(text) < 20:
            # Kurze Antwort auf Frage
            base_intent = "answer"
            confidence = 0.8

        if base_intent == "question" and "?" in text:
            confidence = 0.95

        self.last_intent = base_intent
        self.conversation_context.append(base_intent)

        if len(self.conversation_context) > 10:
            self.conversation_context.pop(0)

        return base_intent, confidence


# =============================================================================
# CALLBACK SYSTEM (aus holo_organic.py)
# =============================================================================

class CallbackSystem:
    """
    Ermöglicht Rückbezüge auf frühere Gespräche.

    Features:
    - Themen-Callbacks
    - Erinnerungs-Callbacks
    - Beziehungs-Aufbau
    """

    CALLBACK_TEMPLATES = [
        "Das erinnert mich an unser Gespräch über {topic}!",
        "Weißt du noch, als wir über {topic} gesprochen haben?",
        "Apropos... du hattest doch mal {topic} erwähnt!",
        "Das passt ja zu dem was du über {topic} gesagt hast!",
    ]

    CALLBACK_CHANCE = 0.1

    def __init__(self):
        self.topics: List[str] = []
        self.callbacks_made: List[str] = []

    def add_topic(self, topic: str):
        """Füge Thema für späteren Callback hinzu"""
        if topic and topic not in self.topics:
            self.topics.append(topic)
            if len(self.topics) > 30:
                self.topics.pop(0)

    def should_callback(self) -> bool:
        """Prüfe ob Callback gemacht werden soll"""
        if not self.topics:
            return False
        return random.random() < self.CALLBACK_CHANCE

    def get_callback(self) -> Optional[str]:
        """Hole Callback"""
        if not self.should_callback():
            return None

        # Topic wählen das länger nicht erwähnt wurde
        available = [t for t in self.topics if t not in self.callbacks_made[-5:]]
        if not available:
            return None

        topic = random.choice(available)
        template = random.choice(self.CALLBACK_TEMPLATES)

        callback = template.replace("{topic}", topic)
        self.callbacks_made.append(topic)

        return callback


# =============================================================================
# CONVERSATION CONTEXT (aus holo_organic.py)
# =============================================================================

@dataclass
class ConversationContext:
    """Kontext der aktuellen Unterhaltung"""
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    message_count: int = 0
    topics: List[str] = field(default_factory=list)
    emotional_arc: List[str] = field(default_factory=list)
    depth_level: int = 0
    humor_used: int = 0
    intimacy_level: float = 0.0
    last_intent: Optional[str] = None
    user_name: Optional[str] = None

    def add_message(self, content: str, is_user: bool = True):
        """Füge Nachricht zum Kontext hinzu"""
        self.message_count += 1

        # Themen extrahieren
        words = content.lower().split()
        for word in words:
            if len(word) > 5 and word.isalpha():
                if word not in self.topics:
                    self.topics.append(word)
                    if len(self.topics) > 10:
                        self.topics.pop(0)

    def get_summary(self) -> str:
        """Hole Kontext-Zusammenfassung"""
        parts = [f"Messages: {self.message_count}"]

        if self.topics:
            parts.append(f"Topics: {', '.join(self.topics[:5])}")

        if self.depth_level > 0:
            parts.append(f"Depth: {self.depth_level}")

        if self.user_name:
            parts.append(f"User: {self.user_name}")

        return " | ".join(parts)



# =============================================================================
# ENHANCED ORGANIC SYSTEM (aus holo_organic.py) - Kombiniert alle organischen Features
# =============================================================================

class EnhancedOrganicSystem:
    """
    Kombiniert alle organischen Features.

    Vereint:
    - Topic Tracking
    - Emotion Tracking
    - Discourse Management
    - Anaphora Resolution
    - Conversation Memory
    - Spontaneous Thoughts
    - Personality Expression
    - Natural Flow
    - Quirks & Callbacks

    WICHTIG: Nutzt SmartUnderstanding für Intent Detection!
    """

    def __init__(self):
        # Core Tracking
        self.topic_tracker = TopicTracker()
        self.emotion_tracker = EmotionTracker()
        self.discourse = DiscourseManager()
        self.anaphora = AnaphoraResolver()
        self.memory = ConversationMemory()

        # Personality & Flow
        self.thoughts = SpontaneousThoughts()
        self.personality = PersonalityExpression()
        self.flow = NaturalFlow()
        self.quirks = QuirkSystem()
        self.callbacks = CallbackSystem()

        # Context
        self.context = ConversationContext()

        # Smart Understanding (lazy-loaded)
        self._understanding = None

    def _get_understanding(self):
        """Hole SmartUnderstanding (lazy)"""
        if self._understanding is None:
            self._understanding = get_smart_understanding()
        return self._understanding

    def process_message(self, text: str, is_user: bool = True,
                       energy: float = 0.5) -> Dict:
        """
        Verarbeite eine Nachricht vollständig.

        Returns umfassendes Analyse-Dictionary.
        """
        # 1. Intent Detection via SmartUnderstanding
        understanding = self._get_understanding()
        if understanding:
            analysis = understanding.understand(text)
            intent = analysis.get("intent", "general")
            intent_confidence = analysis.get("confidence", 0.5)
            requires_llm = analysis.get("requires_llm", True)
            entities = analysis.get("entities", [])
            is_followup = analysis.get("is_followup", False)
        else:
            intent = "general"
            intent_confidence = 0.5
            requires_llm = True
            entities = []
            is_followup = False

        # 2. Emotion Detection
        emotion, valence, emotion_conf = self.emotion_tracker.detect_emotion_from_text(text)
        self.emotion_tracker.add_emotion(emotion, valence, is_user, emotion_conf)

        # 3. Topic Tracking
        new_topics = self.topic_tracker.add_message(text, is_user)
        current_topic = self.topic_tracker.current_focus

        # 4. Context Update
        self.context.add_message(text, is_user)

        # 5. Anaphora - Entities hinzufügen
        for entity in entities:
            if entity.get("type") == "device":
                self.anaphora.add_entity(entity["value"], "device", "neutral")
            elif entity.get("type") == "room":
                self.anaphora.add_location(entity["value"])

        if current_topic:
            self.anaphora.add_topic(current_topic)

        # 6. Reference Resolution
        has_reference = self.anaphora.has_reference(text)
        reference_context = self.anaphora.get_reference_context() if has_reference else {}

        # 6.5 Person Opinion Processing - analysiere Text auf Personen-Erwähnungen
        person_mentions = []
        if is_user and PERSON_OPINIONS_AVAILABLE:
            try:
                opinion_manager = get_person_opinions()
                if opinion_manager:
                    # Suche nach Personen-Namen im Text
                    trigger = PersonInfoTrigger(opinion_manager)
                    person_results = trigger.process_text(text, source="conversation")
                    for result in person_results:
                        person_mentions.append({
                            "name": result.get("person"),
                            "opinion_change": result.get("opinion_change", {}),
                            "traits": result.get("trait_changes", [])
                        })
            except Exception as e:
                logger.debug(f"Person-Opinion-Trigger Fehler: {e}")

        # 7. Memory
        memory_event = None
        if is_user:
            memory_event = self.memory.evaluate_and_store(text, {"intent": intent})

        # 8. Callbacks
        if is_user and current_topic:
            self.callbacks.add_topic(current_topic)

        # 9. Get Current State
        current_mood, mood_valence = self.emotion_tracker.get_current_mood()
        discourse_ctx = self.discourse.get_context_for_response()

        # 10. Spontaneous Thought?
        thought = None
        if not is_user:
            thought = self.thoughts.generate_thought(
                context={"needs_support": self.emotion_tracker.needs_support()},
                topic_tracker=self.topic_tracker,
                memory=self.memory
            )

        # 11. Compile Result
        return {
            # Intent (from SmartUnderstanding)
            "intent": intent,
            "intent_confidence": intent_confidence,
            "requires_llm": requires_llm,
            "is_followup": is_followup,

            # Entities
            "entities": entities,
            "has_reference": has_reference,
            "reference_context": reference_context,

            # Emotion
            "detected_emotion": emotion,
            "emotion_valence": valence,
            "emotion_confidence": emotion_conf,
            "current_mood": current_mood,
            "mood_valence": mood_valence,
            "mood_trend": self.emotion_tracker.get_trend(),
            "needs_support": self.emotion_tracker.needs_support(),

            # Topics
            "current_topic": current_topic,
            "new_topics": new_topics,
            "top_topics": self.topic_tracker.get_top_topics(3),
            "conversation_theme": self.topic_tracker.get_conversation_theme(),

            # Discourse
            "discourse_depth": discourse_ctx["depth"],
            "open_threads": discourse_ctx["open_threads"],
            "exchange_count": self.context.message_count,

            # Memory
            "memory_stored": memory_event is not None,
            "relevant_memories": [m.content for m in self.memory.recall(text, n=2)],

            # Personality
            "spontaneous_thought": thought,
            "add_quirk": self.quirks.should_quirk(),
            "callback": self.callbacks.get_callback() if not is_user else None,

            # Context
            "context_summary": self.context.get_summary(),

            # Person Opinions
            "person_mentions": person_mentions,
        }

    def add_response(self, user_msg: str, holo_response: str, intent: str,
                    topic: str = None):
        """Füge Holo's Antwort zum Tracking hinzu"""
        self.discourse.add_exchange(
            user_msg=user_msg,
            holo_response=holo_response,
            intent=intent,
            topic=topic or self.topic_tracker.current_focus,
        )

        self.topic_tracker.add_message(holo_response, is_user=False)

    def enhance_response(self, response: str, energy: float = 0.5,
                        analysis: Dict = None) -> str:
        """Verbessere Antwort mit organischen Features"""
        result = response

        # Mood/Energy context
        mood = analysis.get("current_mood", "neutral") if analysis else "neutral"
        context_type = None

        if analysis:
            if analysis.get("needs_support"):
                context_type = "concerned"
            elif analysis.get("intent") == "greeting":
                context_type = "greeting"

        # Personality
        result = self.personality.enhance_response(result, energy, mood, context_type)

        # Natural Flow
        flow_context = {
            "should_acknowledge": analysis.get("is_followup", False) if analysis else False,
            "should_engage": random.random() < 0.2,
        }
        result = self.flow.enhance_with_flow(result, flow_context)

        # Quirk?
        if self.quirks.should_quirk() and "*" not in result[:30]:
            quirk = self.quirks.get_quirk()
            if not result.startswith("*"):
                result = f"{quirk} {result}"

        # Spontaner Gedanke?
        if analysis and analysis.get("spontaneous_thought"):
            result = f"{result}\n\n{analysis['spontaneous_thought']}"

        # Callback?
        if analysis and analysis.get("callback"):
            result = f"{result}\n\n{analysis['callback']}"

        return result

    def get_llm_hints(self, analysis: Dict, energy: float = 0.5) -> str:
        """Generiere Hints für LLM basierend auf Analyse"""
        hints = []

        # Emotionaler Kontext
        if analysis.get("needs_support"):
            hints.append("User braucht emotionale Unterstützung - sei einfühlsam")
        elif analysis.get("mood_valence", 0) > 0.5:
            hints.append("User ist gut gelaunt - sei enthusiastisch")

        # Trend
        trend = analysis.get("mood_trend", "stable")
        if trend == "declining":
            hints.append("Stimmung sinkt - sei besonders freundlich")

        # Discourse
        if analysis.get("discourse_depth", 0) > 3:
            hints.append("Tiefes Gespräch - bleib beim Thema")

        if analysis.get("open_threads"):
            hints.append(f"Offene Themen: {', '.join(analysis['open_threads'][:2])}")

        # Energie
        if energy < 0.3:
            hints.append("Du bist müde - antworte kürzer")
        elif energy > 0.7:
            hints.append("Du hast viel Energie - sei enthusiastisch")

        # Memories
        if analysis.get("relevant_memories"):
            hints.append("Es gibt relevante Erinnerungen")

        return " | ".join(hints) if hints else ""


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_organic_system() -> EnhancedOrganicSystem:
    """Factory für EnhancedOrganicSystem"""
    return EnhancedOrganicSystem()


def create_topic_tracker() -> TopicTracker:
    """Factory für TopicTracker"""
    return TopicTracker()


def create_emotion_tracker() -> EmotionTracker:
    """Factory für EmotionTracker"""
    return EmotionTracker()


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================


# =============================================================================
# HOLO CONTEXT MIND - HAUPTKLASSE
# =============================================================================

class HoloContextMind:
    """
    Holos universelles Kontext-System.

    Verwaltet alle Context-Stores und bietet:
    - Kontext hinzufügen
    - Kontext abrufen (Recall)
    - Cross-Context Suche
    - Selbstreflexion
    - Persistenz
    """

    def __init__(self, storage_path: str = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.storage_path = Path(storage_path) if storage_path else None

        # Context Stores
        self.stores: Dict[ContextType, ContextStore] = {}
        for ct in ContextType:
            self.stores[ct] = ContextStore(ct)

        # Spezielle Tracker
        self.chat_tracker = ChatContextTracker()
        self.emotion_tracker = EmotionalContextTracker()

        # Self Reflection
        self.reflection = SelfReflectionEngine(self)

        # NEU: Meta-Cognition für Systembeobachtung
        self.meta_observer = None       # HoloMetaObserver (wird von außen gesetzt)
        self.presence_awareness = None  # HoloPresenceAwareness

        # NEU: Integration Layer für System-Verbindungen
        self.system_integrator = None   # SystemIntegrator aus holo_integration_layer
        self._try_connect_integrator()

        # Working Memory (aktueller Kontext)
        self.working_memory: List[ContextEntry] = []
        self.working_memory_max = 10

        # Lade wenn vorhanden
        if self.db:
            self.load()
        elif self.storage_path and self.storage_path.exists():
            self.load()

    def _try_connect_integrator(self):
        """Versuche Verbindung zum SystemIntegrator herzustellen"""
        try:
            from holo_integration_layer import get_integrator, connect_to_integrator
            self.system_integrator = get_integrator()
            connect_to_integrator("context_mind", self)
            logger.info("✅ HoloContextMind mit SystemIntegrator verbunden")
        except ImportError:
            logger.debug("SystemIntegrator nicht verfügbar")
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self.load()

    # =========================================================================
    # KONTEXT HINZUFÜGEN
    # =========================================================================

    def add(self, context_type: ContextType, content: str,
            keywords: List[str] = None,
            importance: Importance = Importance.NORMAL,
            source: str = "",
            related_ids: List[str] = None) -> ContextEntry:
        """Füge Kontext hinzu"""
        store = self.stores[context_type]
        entry = store.add(content, keywords, importance, source, related_ids)

        # Wichtiges ins Working Memory
        if importance.value >= Importance.HIGH.value:
            self._add_to_working_memory(entry)

        # Meta-Observer informieren bei wichtigem Kontext
        if self.meta_observer and importance.value >= Importance.HIGH.value:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.LEARNING,
                    component="context_mind",
                    action="add_important_context",
                    context={
                        "type": context_type.value,
                        "keywords": keywords[:3] if keywords else [],
                        "importance": importance.value
                    },
                    outcome=f"Kontext gespeichert: {content[:50]}...",
                    success=True
                )
            except Exception:
                pass

        return entry

    def add_chat(self, role: str, content: str,
                 topics: List[str] = None,
                 is_question: bool = False) -> ContextEntry:
        """Füge Chat-Nachricht hinzu"""
        # In Chat-Store
        entry = self.add(
            ContextType.CHAT,
            f"[{role}] {content}",
            keywords=topics,
            source=role,
        )

        # Chat-Tracker aktualisieren
        self.chat_tracker.add_turn(role, content, topics, is_question)

        return entry

    def add_learning(self, content: str,
                    source: str = "conversation",
                    importance: Importance = Importance.NORMAL) -> ContextEntry:
        """Füge Gelerntes hinzu"""
        return self.add(
            ContextType.LEARNING,
            content,
            importance=importance,
            source=source,
        )

    def add_world(self, category: str, content: str,
                  importance: Importance = Importance.NORMAL) -> ContextEntry:
        """Füge Welt-Info hinzu (Wetter, News, Events)"""
        return self.add(
            ContextType.WORLD,
            f"[{category}] {content}",
            keywords=[category],
            importance=importance,
            source=category,
        )

    def add_user_info(self, content: str,
                     importance: Importance = Importance.HIGH) -> ContextEntry:
        """Füge User-Info hinzu"""
        return self.add(
            ContextType.USER,
            content,
            importance=importance,
            source="observation",
        )

    def add_thought(self, content: str) -> ContextEntry:
        """Füge Gedankengang hinzu"""
        return self.add(
            ContextType.THOUGHT,
            content,
            source="internal",
        )

    def add_emotion(self, who: str, emotion: str, intensity: float,
                   trigger: str = ""):
        """Füge emotionalen Kontext hinzu"""
        # In Store
        self.add(
            ContextType.EMOTION,
            f"[{who}] {emotion} ({intensity:.0%}) - {trigger}",
            keywords=[emotion, who],
            importance=Importance.NORMAL if intensity < 0.7 else Importance.HIGH,
        )

        # In Tracker
        if who == "user":
            self.emotion_tracker.add_user_emotion(emotion, intensity, trigger)
        else:
            self.emotion_tracker.add_holo_emotion(emotion, intensity)

    # =========================================================================
    # KONTEXT ABRUFEN (RECALL)
    # =========================================================================

    def recall(self, query: str = None,
               context_types: List[ContextType] = None,
               keywords: List[str] = None,
               time_range: Tuple[float, float] = None,
               min_importance: Importance = None,
               limit: int = 10) -> List[ContextEntry]:
        """
        Rufe relevanten Kontext ab.

        Args:
            query: Freitext-Suche
            context_types: Welche Stores durchsuchen? (None = alle)
            keywords: Keyword-Filter
            time_range: Zeitraum
            min_importance: Mindest-Wichtigkeit
            limit: Max Ergebnisse
        """
        results = []

        types_to_search = context_types or list(ContextType)

        for ct in types_to_search:
            store = self.stores[ct]
            store_results = store.search(
                query=query,
                keywords=keywords,
                time_range=time_range,
                min_importance=min_importance,
                limit=limit,
            )
            results.extend(store_results)

        # Nach Relevanz sortieren
        results.sort(key=lambda e: e._relevance if hasattr(e, '_relevance') else 0,
                    reverse=True)

        return results[:limit]

    def recall_recent(self, hours: int = 24,
                     context_types: List[ContextType] = None,
                     limit: int = 20) -> List[ContextEntry]:
        """Rufe kürzlichen Kontext ab"""
        results = []

        types_to_search = context_types or list(ContextType)

        for ct in types_to_search:
            store = self.stores[ct]
            results.extend(store.get_recent(hours, limit))

        # Nach Zeit sortieren
        results.sort(key=lambda e: e.timestamp, reverse=True)

        return results[:limit]

    def recall_important(self, min_level: Importance = Importance.HIGH,
                        context_types: List[ContextType] = None,
                        limit: int = 10) -> List[ContextEntry]:
        """Rufe wichtigen Kontext ab"""
        results = []

        types_to_search = context_types or list(ContextType)

        for ct in types_to_search:
            store = self.stores[ct]
            results.extend(store.get_important(min_level, limit))

        results.sort(key=lambda e: e.importance.value, reverse=True)

        return results[:limit]

    def cross_search(self, query: str, limit: int = 10) -> List[ContextEntry]:
        """Suche über alle Kontexte"""
        return self.recall(query=query, limit=limit)

    # =========================================================================
    # WORKING MEMORY
    # =========================================================================

    def _add_to_working_memory(self, entry: ContextEntry):
        """Füge zum Arbeitsgedächtnis hinzu"""
        self.working_memory.append(entry)

        if len(self.working_memory) > self.working_memory_max:
            self.working_memory.pop(0)

    def get_working_memory(self) -> List[ContextEntry]:
        """Hole aktuelles Arbeitsgedächtnis"""
        return self.working_memory.copy()

    def get_current_context_summary(self) -> str:
        """Generiere Zusammenfassung des aktuellen Kontexts"""
        parts = []

        # Chat-Kontext
        chat_summary = self.chat_tracker.get_context_summary()
        if chat_summary != "Kein besonderer Kontext.":
            parts.append(f"💬 {chat_summary}")

        # Emotionaler Kontext
        user_mood = self.emotion_tracker.get_user_mood_trend(2)
        if user_mood != "unknown":
            parts.append(f"💭 User-Stimmung: {user_mood}")

        # Wichtiges aus Working Memory
        if self.working_memory:
            important = [e.content[:30] for e in self.working_memory[-3:]]
            parts.append(f"📍 Wichtig: {', '.join(important)}")

        return "\n".join(parts) if parts else "Kein besonderer Kontext aktiv."

    # =========================================================================
    # KONTEXT FÜR LLM/SPEECH ENGINE
    # =========================================================================

    def get_context_for_response(self, user_input: str,
                                 analysis: Any = None) -> Dict:
        """
        Generiere relevanten Kontext für Antwort-Generierung.

        Returns:
            Dict mit relevantem Kontext für LLM oder Speech Engine
        """
        context = {
            "chat_summary": self.chat_tracker.get_context_summary(),
            "current_topics": self.chat_tracker.current_topics,
            "user_mood": self.emotion_tracker.get_user_mood_trend(2),
            "open_questions": self.chat_tracker.has_open_questions(),
            "relevant_memories": [],
            "relevant_knowledge": [],
            "user_info": [],
        }

        # Relevante Erinnerungen suchen
        memories = self.recall(
            query=user_input,
            context_types=[ContextType.CHAT, ContextType.USER],
            limit=5,
        )
        context["relevant_memories"] = [
            {"content": m.content, "relevance": getattr(m, '_relevance', 0)}
            for m in memories
        ]

        # Relevantes Wissen
        knowledge = self.recall(
            query=user_input,
            context_types=[ContextType.LEARNING, ContextType.WORLD],
            limit=3,
        )
        context["relevant_knowledge"] = [k.content for k in knowledge]

        # User-Infos
        user_info = self.stores[ContextType.USER].get_important(limit=5)
        context["user_info"] = [u.content for u in user_info]

        return context

    # =========================================================================
    # PERSISTENZ
    # =========================================================================

    def save(self):
        """Speichere alles in HoloDatabaseManager"""
        if not self.db:
            return

        try:
            data = {
                "stores": {ct.value: store.to_dict() for ct, store in self.stores.items()},
                "working_memory": [e.to_dict() for e in self.working_memory],
                "timestamp": time.time(),
            }
            self.db.state.save_state('context_mind', data)
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")

    def load(self):
        """Lade alles aus HoloDatabaseManager"""
        if not self.db:
            return

        try:
            data = self.db.state.get_state('context_mind')
            if not data:
                return

            for ct_value, store_data in data.get("stores", {}).items():
                ct = ContextType(ct_value)
                self.stores[ct].from_dict(store_data)

            for entry_data in data.get("working_memory", []):
                entry = ContextEntry.from_dict(entry_data)
                self.working_memory.append(entry)

            logger.info("Context Mind geladen aus DB")
        except Exception as e:
            logger.error(f"Fehler beim Laden: {e}")

    # =========================================================================
    # STATISTIKEN
    # =========================================================================

    def get_stats(self) -> Dict:
        """Hole Statistiken"""
        stats = {
            "total_entries": 0,
            "by_type": {},
            "working_memory_size": len(self.working_memory),
            "current_topics": self.chat_tracker.current_topics,
        }

        for ct, store in self.stores.items():
            count = len(store.entries)
            stats["total_entries"] += count
            stats["by_type"][ct.value] = count

        return stats


# =============================================================================
# FACTORY
# =============================================================================

def create_context_mind(storage_path: str = None, db: 'HoloDatabaseManager' = None) -> HoloContextMind:
    """Factory für Context Mind

    Args:
        storage_path: Pfad für JSON-Speicherung (Legacy)
        db: HoloDatabaseManager für Persistenz
    """
    return HoloContextMind(storage_path=storage_path, db=db)


# =============================================================================
# KOMPATIBILITÄTS-ALIASE (aus holo_organic.py)
# =============================================================================

class OrganicConfig:
    """Konfiguration für organische Features (Konstanten aus holo_organic.py)"""
    # Topic Tracking
    TOPIC_DECAY_HOURS = 24
    MIN_TOPIC_LENGTH = 3
    MAX_TOPICS = 20

    # Emotion
    EMOTION_DECAY_RATE = 0.1

    # Discourse
    MAX_DISCOURSE_DEPTH = 5

    # Memory
    MAX_MEMORIES = 100
    MEMORY_IMPORTANCE_THRESHOLD = 0.5

    # Spontaneous Thoughts
    THOUGHT_CHANCE = 0.15
    THOUGHT_COOLDOWN = 120

    # Personality
    QUIRK_CHANCE = 0.15
    CALLBACK_CHANCE = 0.1


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 HOLO CONTEXT MIND - TEST")
    print("=" * 70)

    # Erstellen
    mind = HoloContextMind()

    # Chat simulieren
    print("\n📍 Chat simulieren...")
    mind.add_chat("user", "Hi Holo!", topics=["greeting"])
    mind.add_chat("assistant", "*wedelt* Hey! Wie geht's?")
    mind.add_chat("user", "Mir geht es heute nicht so gut, ich bin etwas traurig",
                  topics=["emotion"])
    mind.add_emotion("user", "sad", 0.6, "unbekannt")
    mind.add_chat("assistant", "*stupst an* Was ist passiert?")
    mind.add_chat("user", "Stress auf der Arbeit mit dem Projekt", topics=["work", "stress"])

    # Wissen hinzufügen
    print("📚 Wissen hinzufügen...")
    mind.add_learning("User arbeitet an einem stressigen Projekt", source="conversation")
    mind.add_user_info("User hat manchmal Stress auf der Arbeit")
    mind.add_world("weather", "Es ist bewölkt und 8°C")

    # Recall testen
    print("\n🔍 RECALL TEST:")
    print("\n--- Suche: 'stress' ---")
    results = mind.recall("stress", limit=5)
    for r in results:
        print(f"  [{r.context_type.value}] {r.content[:50]}... (relevance: {r._relevance:.2f})")

    print("\n--- Kürzliche Einträge ---")
    recent = mind.recall_recent(hours=1, limit=5)
    for r in recent:
        print(f"  [{r.context_type.value}] {r.content[:50]}...")

    # Kontext-Summary
    print("\n📊 KONTEXT SUMMARY:")
    print(mind.get_current_context_summary())

    # Kontext für Antwort
    print("\n🎯 KONTEXT FÜR ANTWORT auf 'was kann ich dagegen tun?':")
    ctx = mind.get_context_for_response("was kann ich dagegen tun?")
    print(f"  Topics: {ctx['current_topics']}")
    print(f"  User Mood: {ctx['user_mood']}")
    print(f"  Memories: {len(ctx['relevant_memories'])}")

    # Selbstreflexion
    print("\n💭 SELBSTREFLEXION:")
    summary = mind.reflection.generate_daily_summary()
    print(summary)

    # Stats
    print("\n📈 STATISTIKEN:")
    stats = mind.get_stats()
    print(f"  Total Entries: {stats['total_entries']}")
    for ct, count in stats["by_type"].items():
        if count > 0:
            print(f"    {ct}: {count}")

    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
