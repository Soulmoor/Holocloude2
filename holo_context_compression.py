#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO CONTEXT COMPRESSION v1.0
==============================
Intelligente Komprimierung des Chat-Verlaufs für effiziente LLM-Calls.

PROBLEM:
- 100 Nachrichten = ~10.000+ Tokens
- LLM Context Window begrenzt (8k-32k)
- Mehr Tokens = langsamer + teurer

LÖSUNG:
- Neueste Nachrichten: VOLLSTÄNDIG
- Mittlere Nachrichten: ZUSAMMENGEFASST  
- Alte Nachrichten: NUR KEY-POINTS
- Extrahierte Fakten: PERSISTENT

ARCHITEKTUR:
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT WINDOW                           │
├─────────────────────────────────────────────────────────────┤
│  [Letzte 5-10 Nachrichten]     ← Vollständig (~500 tokens) │
│  [Zusammenfassung Mitte]       ← Komprimiert (~200 tokens) │
│  [Key-Points Anfang]           ← Nur Fakten (~100 tokens)  │
│  [Extrahierte Entitäten]       ← Namen, Orte, Themen       │
├─────────────────────────────────────────────────────────────┤
│  GESAMT: ~800 Tokens statt ~10.000!                        │
└─────────────────────────────────────────────────────────────┘

Token-Ersparnis: 80-90%!
"""

import json
import re
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from pathlib import Path

logger = logging.getLogger("ContextCompression")


# =============================================================================
# CONFIGURATION
# =============================================================================

class CompressionConfig:
    """Konfiguration für Context Compression"""
    
    # Wie viele Nachrichten vollständig behalten?
    FULL_CONTEXT_MESSAGES = 6          # Letzte 6 Nachrichten = vollständig
    
    # Wie viele Nachrichten zusammenfassen?
    SUMMARY_CONTEXT_MESSAGES = 20      # Nächste 20 = zusammengefasst
    
    # Ab wann nur Key-Points?
    KEYPOINT_THRESHOLD = 26            # Alles davor = nur Key-Points
    
    # Token-Limits (ungefähr)
    MAX_FULL_TOKENS = 600              # Max für vollständige Nachrichten
    MAX_SUMMARY_TOKENS = 300           # Max für Zusammenfassung
    MAX_KEYPOINTS_TOKENS = 150         # Max für Key-Points
    MAX_ENTITIES_TOKENS = 100          # Max für extrahierte Entitäten
    
    # Wann neu komprimieren?
    RECOMPRESS_INTERVAL = 10           # Alle 10 neuen Nachrichten
    
    # Speicherung
    CACHE_FILE = Path.home() / "holo_context_cache.json"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ChatMessage:
    """Eine Chat-Nachricht"""
    role: str                          # "user" oder "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5            # 0-1, wie wichtig
    tokens_estimate: int = 0           # Geschätzte Token-Anzahl
    
    def __post_init__(self):
        if self.tokens_estimate == 0:
            # Grobe Schätzung: 1 Token ≈ 4 Zeichen (für Deutsch)
            self.tokens_estimate = len(self.content) // 3


@dataclass
class ExtractedEntity:
    """Eine extrahierte Entität (Name, Ort, Thema, etc.)"""
    entity_type: str                   # "person", "place", "topic", "fact", "preference"
    value: str
    context: str                       # Woher kommt diese Info?
    confidence: float = 0.8
    first_mentioned: str = field(default_factory=lambda: datetime.now().isoformat())
    mention_count: int = 1


@dataclass
class CompressedContext:
    """Der komprimierte Kontext für das LLM"""
    full_messages: List[Dict]          # Vollständige letzte Nachrichten
    summary: str                       # Zusammenfassung der mittleren
    key_points: List[str]              # Key-Points vom Anfang
    entities: Dict[str, List[str]]     # Extrahierte Entitäten
    total_tokens_estimate: int = 0
    compression_ratio: float = 0.0     # Wie viel gespart?
    
    def to_prompt_section(self) -> str:
        """Formatiert den Kontext für den System-Prompt"""
        sections = []
        
        # Entitäten (wichtige Fakten)
        if self.entities:
            entity_parts = []
            for etype, values in self.entities.items():
                if values:
                    entity_parts.append(f"{etype}: {', '.join(values[:5])}")
            if entity_parts:
                sections.append("=== BEKANNTE FAKTEN ===\n" + "\n".join(entity_parts))
        
        # Key-Points (früher im Gespräch)
        if self.key_points:
            sections.append("=== FRÜHER IM GESPRÄCH ===\n" + "\n".join(f"• {kp}" for kp in self.key_points[:5]))
        
        # Zusammenfassung
        if self.summary:
            sections.append(f"=== GESPRÄCHSVERLAUF ===\n{self.summary}")
        
        return "\n\n".join(sections)
    
    def get_messages_for_llm(self) -> List[Dict]:
        """Gibt die Nachrichten für den LLM-Call zurück"""
        return self.full_messages


# =============================================================================
# ENTITY EXTRACTOR - Extrahiert wichtige Informationen
# =============================================================================

class EntityExtractor:
    """
    Extrahiert wichtige Entitäten aus Nachrichten.
    Läuft lokal, kein LLM nötig!
    """
    
    # Patterns für verschiedene Entitäten
    PATTERNS = {
        "name": [
            r"ich heiße (\w+)",
            r"mein name ist (\w+)",
            r"ich bin (?:der |die )?(\w+)",
            r"nenn mich (\w+)",
        ],
        "location": [
            r"ich (?:wohne|lebe|bin) in ([\w\s]+?)(?:\.|,|$)",
            r"ich komme aus ([\w\s]+?)(?:\.|,|$)",
            r"hier in ([\w\s]+?)(?:\.|,|$)",
        ],
        "preference_positive": [
            r"ich (?:mag|liebe|finde.*gut) ([\w\s]+?)(?:\.|,|$)",
            r"(?:mein|meine) lieblings[\w]* (?:ist|sind) ([\w\s]+?)(?:\.|,|$)",
            r"ich interessiere mich für ([\w\s]+?)(?:\.|,|$)",
        ],
        "preference_negative": [
            r"ich (?:mag|hasse|finde).*nicht ([\w\s]+?)(?:\.|,|$)",
            r"ich kann ([\w\s]+?) nicht (?:leiden|ausstehen)",
        ],
        "fact": [
            r"ich (?:habe|bin|arbeite|studiere) ([\w\s]+?)(?:\.|,|$)",
            r"ich (?:muss|will|möchte|werde) ([\w\s]+?)(?:\.|,|$)",
        ],
        "topic": [
            # Topics werden aus häufigen Substantiven extrahiert
        ],
    }
    
    def __init__(self):
        self.entities: Dict[str, List[ExtractedEntity]] = {
            "names": [],
            "locations": [],
            "preferences": [],
            "facts": [],
            "topics": [],
        }
        self._compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Kompiliert die Regex-Patterns"""
        for category, patterns in self.PATTERNS.items():
            self._compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def extract_from_message(self, message: str, role: str = "user") -> List[ExtractedEntity]:
        """Extrahiert Entitäten aus einer Nachricht"""
        extracted = []
        message_lower = message.lower()
        
        # Nur User-Nachrichten für persönliche Infos
        if role == "user":
            # Namen
            for pattern in self._compiled_patterns.get("name", []):
                match = pattern.search(message_lower)
                if match:
                    name = match.group(1).strip().title()
                    if len(name) > 1:
                        extracted.append(ExtractedEntity(
                            entity_type="name",
                            value=name,
                            context=message[:50]
                        ))
            
            # Orte
            for pattern in self._compiled_patterns.get("location", []):
                match = pattern.search(message_lower)
                if match:
                    location = match.group(1).strip().title()
                    if len(location) > 2:
                        extracted.append(ExtractedEntity(
                            entity_type="location",
                            value=location,
                            context=message[:50]
                        ))
            
            # Positive Präferenzen
            for pattern in self._compiled_patterns.get("preference_positive", []):
                match = pattern.search(message_lower)
                if match:
                    pref = match.group(1).strip()
                    if len(pref) > 2:
                        extracted.append(ExtractedEntity(
                            entity_type="preference_positive",
                            value=pref,
                            context=message[:50]
                        ))
            
            # Fakten
            for pattern in self._compiled_patterns.get("fact", []):
                match = pattern.search(message_lower)
                if match:
                    fact = match.group(1).strip()
                    if len(fact) > 3:
                        extracted.append(ExtractedEntity(
                            entity_type="fact",
                            value=fact,
                            context=message[:50]
                        ))
        
        # Topics aus beiden Rollen (häufige Wörter)
        topics = self._extract_topics(message)
        for topic in topics:
            extracted.append(ExtractedEntity(
                entity_type="topic",
                value=topic,
                context=message[:30]
            ))
        
        return extracted
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extrahiert potenzielle Themen (wichtige Wörter)"""
        # Stopwords die wir ignorieren
        stopwords = {
            "ich", "du", "wir", "sie", "er", "es", "und", "oder", "aber", 
            "dass", "das", "die", "der", "den", "dem", "ein", "eine", 
            "ist", "sind", "war", "bin", "habe", "hat", "haben", "wird",
            "kann", "muss", "will", "soll", "darf", "mit", "für", "von",
            "auf", "bei", "nach", "vor", "über", "unter", "zwischen",
            "nicht", "auch", "noch", "schon", "nur", "mal", "dann",
            "wenn", "weil", "als", "wie", "was", "wer", "wo", "wann",
            "gerade", "jetzt", "heute", "morgen", "gestern", "immer",
            "vielleicht", "eigentlich", "wirklich", "sehr", "ganz",
            "holo", "bitte", "danke", "okay", "ja", "nein", "gut",
        }
        
        # Wörter extrahieren (nur Buchstaben, min 4 Zeichen)
        words = re.findall(r'\b[a-zäöüß]{4,}\b', message.lower())
        
        # Filtern
        topics = [w for w in words if w not in stopwords]
        
        # Nur die wichtigsten (erste 2)
        return topics[:2]
    
    def add_entity(self, entity: ExtractedEntity):
        """Fügt eine Entität hinzu (mit Deduplizierung)"""
        category = self._get_category(entity.entity_type)
        
        # Prüfen ob schon vorhanden
        for existing in self.entities[category]:
            if existing.value.lower() == entity.value.lower():
                existing.mention_count += 1
                return
        
        self.entities[category].append(entity)
    
    def _get_category(self, entity_type: str) -> str:
        """Mappt Entity-Typ auf Kategorie"""
        mapping = {
            "name": "names",
            "location": "locations",
            "preference_positive": "preferences",
            "preference_negative": "preferences",
            "fact": "facts",
            "topic": "topics",
        }
        return mapping.get(entity_type, "facts")
    
    def get_entities_for_prompt(self) -> Dict[str, List[str]]:
        """Gibt Entitäten formatiert für den Prompt zurück"""
        result = {}
        
        if self.entities["names"]:
            result["User-Name"] = [e.value for e in self.entities["names"][:2]]
        
        if self.entities["locations"]:
            result["Orte"] = [e.value for e in self.entities["locations"][:3]]
        
        if self.entities["preferences"]:
            result["Interessen"] = [e.value for e in self.entities["preferences"][:5]]
        
        if self.entities["facts"]:
            result["Fakten"] = [e.value for e in self.entities["facts"][:5]]
        
        # Topics: nur die häufigsten
        if self.entities["topics"]:
            topic_counts = {}
            for e in self.entities["topics"]:
                topic_counts[e.value] = topic_counts.get(e.value, 0) + 1
            
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            result["Themen"] = [t[0] for t in top_topics]
        
        return result


# =============================================================================
# MESSAGE SUMMARIZER - Fasst Nachrichten zusammen
# =============================================================================

class MessageSummarizer:
    """
    Fasst Nachrichten zusammen.
    OHNE LLM - rein algorithmisch!
    """
    
    @staticmethod
    def summarize_messages(messages: List[ChatMessage], max_length: int = 300) -> str:
        """
        Erstellt eine Zusammenfassung mehrerer Nachrichten.
        
        Args:
            messages: Liste von Nachrichten
            max_length: Maximale Länge der Zusammenfassung
            
        Returns:
            Zusammenfassung als String
        """
        if not messages:
            return ""
        
        # Wichtige Sätze extrahieren
        important_parts = []
        
        for msg in messages:
            # Ersten Satz jeder Nachricht (oft der wichtigste)
            sentences = re.split(r'[.!?]', msg.content)
            if sentences:
                first = sentences[0].strip()
                if len(first) > 10:
                    role_prefix = "User: " if msg.role == "user" else "Holo: "
                    important_parts.append(f"{role_prefix}{first[:80]}")
        
        # Zusammenfügen
        summary = " → ".join(important_parts[-6:])  # Letzte 6 Punkte
        
        # Kürzen wenn nötig
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    @staticmethod
    def extract_key_points(messages: List[ChatMessage], max_points: int = 5) -> List[str]:
        """
        Extrahiert Key-Points aus älteren Nachrichten.
        
        Returns:
            Liste von Key-Points
        """
        key_points = []
        
        # Patterns für wichtige Aussagen
        importance_patterns = [
            r"wichtig",
            r"merken",
            r"vergiss nicht",
            r"ich (?:bin|habe|arbeite|wohne)",
            r"mein(?:e)? (?:name|arbeit|hobby|lieblings)",
            r"ich (?:mag|liebe|hasse)",
            r"wir haben (?:besprochen|geredet|diskutiert)",
        ]
        
        for msg in messages:
            if msg.role == "user":
                content_lower = msg.content.lower()
                
                # Prüfen ob wichtig
                for pattern in importance_patterns:
                    if re.search(pattern, content_lower):
                        # Ersten relevanten Satz nehmen
                        sentences = re.split(r'[.!?]', msg.content)
                        for sent in sentences:
                            if re.search(pattern, sent.lower()) and len(sent.strip()) > 10:
                                key_points.append(sent.strip()[:100])
                                break
                        break
        
        # Deduplizieren und begrenzen
        unique_points = list(dict.fromkeys(key_points))
        return unique_points[:max_points]


# =============================================================================
# CONTEXT COMPRESSOR - Hauptklasse
# =============================================================================

class ContextCompressor:
    """
    Komprimiert den Chat-Kontext intelligent.
    
    Spart 80-90% Tokens bei gleichbleibender Qualität!
    """
    
    def __init__(self, db=None):
        self.db = db  # StateDatabase für zentrale Speicherung
        self.messages: deque = deque(maxlen=200)  # Rohe Nachrichten
        self.entity_extractor = EntityExtractor()
        self.summarizer = MessageSummarizer()

        self._last_compression: Optional[CompressedContext] = None
        self._messages_since_compression: int = 0

        # Cache laden
        self._load_cache()
    
    def add_message(self, role: str, content: str):
        """Fügt eine neue Nachricht hinzu"""
        msg = ChatMessage(role=role, content=content)
        self.messages.append(msg)
        
        # Entitäten extrahieren
        entities = self.entity_extractor.extract_from_message(content, role)
        for entity in entities:
            self.entity_extractor.add_entity(entity)
        
        self._messages_since_compression += 1
        
        # Periodisch speichern
        if len(self.messages) % 20 == 0:
            self._save_cache()
    
    def get_compressed_context(self, force_recompress: bool = False) -> CompressedContext:
        """
        Gibt den komprimierten Kontext zurück.
        
        Args:
            force_recompress: Erzwingt Neu-Komprimierung
            
        Returns:
            CompressedContext mit allen Teilen
        """
        # Prüfen ob Neu-Komprimierung nötig
        needs_recompress = (
            force_recompress or
            self._last_compression is None or
            self._messages_since_compression >= CompressionConfig.RECOMPRESS_INTERVAL
        )
        
        if not needs_recompress and self._last_compression:
            # Nur letzte Nachrichten aktualisieren
            self._update_recent_messages()
            return self._last_compression
        
        # Neu komprimieren
        return self._compress()
    
    def _compress(self) -> CompressedContext:
        """Führt die Komprimierung durch"""
        messages = list(self.messages)
        total_raw_tokens = sum(m.tokens_estimate for m in messages)
        
        if not messages:
            return CompressedContext(
                full_messages=[],
                summary="",
                key_points=[],
                entities={},
            )
        
        # 1. Vollständige Nachrichten (neueste)
        full_count = min(len(messages), CompressionConfig.FULL_CONTEXT_MESSAGES)
        full_messages = messages[-full_count:]
        full_messages_dict = [
            {"role": m.role, "content": m.content}
            for m in full_messages
        ]
        
        # 2. Zusammenfassung (mittlere)
        summary_start = max(0, len(messages) - full_count - CompressionConfig.SUMMARY_CONTEXT_MESSAGES)
        summary_end = len(messages) - full_count
        summary_messages = messages[summary_start:summary_end]
        summary = self.summarizer.summarize_messages(
            summary_messages,
            max_length=CompressionConfig.MAX_SUMMARY_TOKENS * 3  # ~3 Zeichen pro Token
        )
        
        # 3. Key-Points (älteste)
        old_messages = messages[:summary_start]
        key_points = self.summarizer.extract_key_points(old_messages)
        
        # 4. Entitäten
        entities = self.entity_extractor.get_entities_for_prompt()
        
        # Token-Schätzung
        full_tokens = sum(m.tokens_estimate for m in full_messages)
        summary_tokens = len(summary) // 3
        keypoint_tokens = sum(len(kp) // 3 for kp in key_points)
        entity_tokens = sum(len(str(v)) // 3 for v in entities.values())
        
        total_compressed = full_tokens + summary_tokens + keypoint_tokens + entity_tokens
        
        compression_ratio = 1 - (total_compressed / max(1, total_raw_tokens))
        
        self._last_compression = CompressedContext(
            full_messages=full_messages_dict,
            summary=summary,
            key_points=key_points,
            entities=entities,
            total_tokens_estimate=total_compressed,
            compression_ratio=compression_ratio,
        )
        
        self._messages_since_compression = 0
        
        logger.info(f"[COMPRESS] {len(messages)} msgs → ~{total_compressed} tokens "
                   f"(saved {compression_ratio:.0%})")
        
        return self._last_compression
    
    def _update_recent_messages(self):
        """Aktualisiert nur die neuesten Nachrichten im Cache"""
        if not self._last_compression:
            return
        
        messages = list(self.messages)
        full_count = min(len(messages), CompressionConfig.FULL_CONTEXT_MESSAGES)
        full_messages = messages[-full_count:]
        
        self._last_compression.full_messages = [
            {"role": m.role, "content": m.content}
            for m in full_messages
        ]
    
    def get_context_for_llm(self) -> Tuple[str, List[Dict]]:
        """
        Convenience-Methode: Gibt System-Prompt-Ergänzung und Messages zurück.
        
        Returns:
            (context_section, messages_list)
        """
        compressed = self.get_compressed_context()
        
        context_section = compressed.to_prompt_section()
        messages = compressed.get_messages_for_llm()
        
        return context_section, messages
    
    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        compressed = self.get_compressed_context()
        
        return {
            "total_messages": len(self.messages),
            "full_messages": len(compressed.full_messages),
            "has_summary": bool(compressed.summary),
            "key_points_count": len(compressed.key_points),
            "entities": {k: len(v) for k, v in compressed.entities.items()},
            "tokens_estimate": compressed.total_tokens_estimate,
            "compression_ratio": f"{compressed.compression_ratio:.0%}",
        }
    
    def _save_cache(self):
        """Speichert Entitäten und wichtige Daten"""
        try:
            cache = {
                "entities": {
                    cat: [asdict(e) for e in entities]
                    for cat, entities in self.entity_extractor.entities.items()
                },
                "last_update": datetime.now().isoformat(),
            }

            # Primär: StateDatabase verwenden
            if self.db:
                try:
                    self.db.state.save_state('context_compression', cache)
                    logger.debug("[COMPRESS] State saved to StateDatabase")
                except Exception as db_err:
                    logger.warning(f"[COMPRESS] StateDatabase save failed: {db_err}, falling back to JSON")
                    # Fallback auf JSON
                    CompressionConfig.CACHE_FILE.write_text(
                        json.dumps(cache, indent=2, ensure_ascii=False)
                    )
            else:
                # Fallback: JSON wenn keine DB verfügbar
                CompressionConfig.CACHE_FILE.write_text(
                    json.dumps(cache, indent=2, ensure_ascii=False)
                )
                logger.debug("[COMPRESS] State saved to JSON (no DB available)")
        except Exception as e:
            logger.debug(f"Could not save cache: {e}")
    
    def _load_cache(self):
        """Lädt gecachte Entitäten"""
        try:
            cache = None

            # Primär: StateDatabase verwenden
            if self.db:
                try:
                    cache = self.db.state.load_state('context_compression')
                    if cache:
                        logger.info("[COMPRESS] Loaded cached entities from StateDatabase")
                except Exception as db_err:
                    logger.warning(f"[COMPRESS] StateDatabase load failed: {db_err}, trying JSON fallback")

            # Fallback: JSON wenn DB nicht verfügbar oder leer
            if not cache and CompressionConfig.CACHE_FILE.exists():
                cache = json.loads(CompressionConfig.CACHE_FILE.read_text())
                logger.info("[COMPRESS] Loaded cached entities from JSON")

            # Cache-Daten verarbeiten
            if cache:
                for cat, entities in cache.get("entities", {}).items():
                    for e_data in entities:
                        entity = ExtractedEntity(**e_data)
                        self.entity_extractor.entities[cat].append(entity)
        except Exception as e:
            logger.debug(f"Could not load cache: {e}")
    
    def clear(self):
        """Löscht alles"""
        self.messages.clear()
        self.entity_extractor = EntityExtractor()
        self._last_compression = None
        self._messages_since_compression = 0


# =============================================================================
# INTEGRATION HELPER
# =============================================================================

class SmartContextManager:
    """
    High-Level Manager für intelligentes Context-Management.
    Integriert sich nahtlos in HoloBrain.
    """

    def __init__(self, db=None):
        self.compressor = ContextCompressor(db=db)
        self.total_tokens_saved: int = 0
    
    def add_exchange(self, user_message: str, assistant_response: str):
        """Fügt einen kompletten Austausch hinzu"""
        self.compressor.add_message("user", user_message)
        self.compressor.add_message("assistant", assistant_response)
    
    def get_context_for_prompt(self) -> str:
        """Gibt den Kontext-Teil für den System-Prompt zurück"""
        context_section, _ = self.compressor.get_context_for_llm()
        return context_section
    
    def get_messages_for_llm(self) -> List[Dict]:
        """Gibt die Messages für den LLM-Call zurück"""
        _, messages = self.compressor.get_context_for_llm()
        return messages
    
    def get_full_context(self) -> Tuple[str, List[Dict]]:
        """Gibt beides zurück"""
        return self.compressor.get_context_for_llm()
    
    def get_known_facts(self) -> Dict[str, List[str]]:
        """Gibt extrahierte Fakten über den User zurück"""
        return self.compressor.entity_extractor.get_entities_for_prompt()
    
    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        stats = self.compressor.get_stats()
        stats["total_tokens_saved_session"] = self.total_tokens_saved
        return stats


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_context_manager() -> SmartContextManager:
    """Erstellt einen SmartContextManager"""
    return SmartContextManager()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("HOLO CONTEXT COMPRESSION v1.0 - TEST")
    print("=" * 60)
    
    manager = SmartContextManager()
    
    # Simuliere ein Gespräch
    test_conversation = [
        ("user", "Hallo Holo! Ich bin Max und wohne in Berlin."),
        ("assistant", "Hallo Max! Schön dich kennenzulernen. Berlin ist eine tolle Stadt!"),
        ("user", "Ja, ich mag die Stadt sehr. Ich arbeite als Programmierer."),
        ("assistant", "Oh, Programmieren ist spannend! Was für Projekte machst du?"),
        ("user", "Ich entwickle gerade eine Smart Home Steuerung mit Python."),
        ("assistant", "Das klingt nach einem interessanten Projekt! Python eignet sich gut dafür."),
        ("user", "Ja, ich nutze auch Raspberry Pi dafür. Mein Lieblingshobby ist übrigens Musik."),
        ("assistant", "Raspberry Pi ist perfekt für Smart Home. Welche Musik hörst du gerne?"),
        ("user", "Vor allem Rock und Metal. Aber manchmal auch Jazz."),
        ("assistant", "Eine interessante Mischung! Jazz hat auch technisch anspruchsvolle Musik."),
        ("user", "Stimmt. Hey, kannst du mir bei einem Python-Problem helfen?"),
        ("assistant", "Natürlich! Was für ein Problem hast du?"),
        ("user", "Meine Async-Funktion blockiert irgendwie den Main-Thread."),
        ("assistant", "Das ist ein häufiges Problem. Verwendest du asyncio.run() korrekt?"),
    ]
    
    print("\n1️⃣ Gespräch simulieren...")
    for role, content in test_conversation:
        if role == "user":
            manager.compressor.add_message("user", content)
        else:
            manager.compressor.add_message("assistant", content)
    
    print(f"   {len(test_conversation)} Nachrichten hinzugefügt")
    
    # Komprimieren
    print("\n2️⃣ Kontext komprimieren...")
    context_section, messages = manager.get_full_context()
    
    print(f"\n   Extrahierte Fakten:")
    for key, values in manager.get_known_facts().items():
        print(f"   • {key}: {', '.join(values)}")
    
    print(f"\n   Kontext für System-Prompt:")
    print("-" * 40)
    print(context_section[:500] + "..." if len(context_section) > 500 else context_section)
    print("-" * 40)
    
    print(f"\n   Vollständige Messages für LLM: {len(messages)}")
    
    # Stats
    print("\n3️⃣ Statistiken:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
