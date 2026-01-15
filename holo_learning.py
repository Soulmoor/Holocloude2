#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO LEARNING SYSTEM - Echtes Lernen, Echtes Wissen                         ║
║                                                                              ║
║  Holo lernt WIRKLICH:                                                        ║
║  • Liest echte News aus RSS Feeds                                           ║
║  • Extrahiert Fakten und speichert sie                                      ║
║  • Kann Wissen bei Abfrage wiedergeben                                      ║
║  • Verfolgt Interessen und lernt priorisiert                                ║
║  • Emotionale Erinnerungen an bedeutsame Momente                            ║
║  • Stimmungs-Ansteckung vom User                                            ║
║                                                                              ║
║  KEINE SIMULATION - ECHTES LERNEN!                                           ║
║                                                                              ║
║  Komponenten:                                                                ║
║  • LearningKnowledgeDB - Fakten-Speicher mit Suche                          ║
║  • FactExtractor - Extrahiert Fakten aus Text (ohne LLM)                    ║
║  • NewsFetcher - Holt News aus RSS Feeds                                    ║
║  • LearningTopicTracker - Verfolgt aktuelle Interessen                      ║
║  • LearningScheduler - Plant autonomes Lernen                               ║
║  • MoodContagion - Stimmungs-Ansteckung                                     ║
║  • EmotionalMemoryStore - Emotionale Erinnerungen                           ║
║  • RealLearningEngine - Orchestriert alles                                  ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import time
import random
import hashlib
import logging
import threading
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum
import re

logger = logging.getLogger("HoloLearning")

# Database Integration (optional)
try:
    from holo_database_system import HoloDatabaseManager
    DATABASE_AVAILABLE = True
    logger.info("[Learning] ✓ holo_database_system verfügbar")
except ImportError:
    DATABASE_AVAILABLE = False
    HoloDatabaseManager = None
    logger.debug("[Learning] holo_database_system nicht verfügbar")

# Person Opinion Integration (optional)
try:
    from holo_person_opinions import PersonInfoTrigger, get_person_opinion_manager
    PERSON_OPINIONS_AVAILABLE = True
    logger.info("[Learning] ✓ holo_person_opinions verfügbar")
except ImportError:
    PERSON_OPINIONS_AVAILABLE = False
    PersonInfoTrigger = None
    get_person_opinion_manager = None
    logger.debug("[Learning] holo_person_opinions nicht verfügbar")


# =============================================================================
# KONFIGURATION
# =============================================================================

class LearningConfig:
    """Zentrale Konfiguration für das Lern-System"""

    # === PFADE ===
    DATA_DIR = Path.home() / "holo_knowledge"
    KNOWLEDGE_DB = DATA_DIR / "knowledge.json"
    EMOTIONAL_MEMORY_DB = DATA_DIR / "emotional_memories.json"
    TOPIC_TRACKER_DB = DATA_DIR / "topic_tracker.json"
    LEARNING_LOG = DATA_DIR / "learning_log.json"

    # === LERN-ZEITEN ===
    LEARNING_INTERVAL_MINUTES = 30          # Background-Lernen
    DEEP_RESEARCH_HOURS = (3, 5)            # Tiefe Recherche nachts

    # === LIMITS ===
    MAX_FACTS_TOTAL = 10000
    MAX_FACTS_PER_TOPIC = 500
    MAX_FACTS_PER_CATEGORY = 2000
    FACTS_PER_ARTICLE = 5
    MAX_EMOTIONAL_MEMORIES = 200
    MAX_TOPIC_HISTORY = 100

    # === VERFALL ===
    FACT_DECAY_DAYS = 90                    # Nach 90 Tagen sinkt Relevanz
    FACT_DECAY_RATE = 0.01                  # 1% pro Tag
    FACT_MIN_IMPORTANCE = 0.1               # Minimum Wichtigkeit

    # === STIMMUNG ===
    MOOD_CONTAGION_RATE = 0.3               # 30% Einfluss

    # === HOLOS INTERESSEN ===
    # Diese bestimmen Lern-Priorität
    INTERESTS = {
        "anime": 0.95,          # LEIDENSCHAFT
        "manga": 0.90,
        "gaming": 0.90,
        "japan": 0.80,
        "technik": 0.70,
        "serien": 0.65,
        "filme": 0.60,
        "musik": 0.55,
        "wissenschaft": 0.50,
        "welt": 0.40,
    }

    # === NEWS FEEDS ===
    NEWS_FEEDS = {
        "anime": {
            "Anime2You": "https://www.anime2you.de/feed/",
            "Anime News Network": "https://www.animenewsnetwork.com/news/rss.xml",
            "Crunchyroll": "https://www.crunchyroll.com/newsrss",
            "MyAnimeList": "https://myanimelist.net/rss/news.xml",
        },
        "gaming": {
            "GameStar": "https://www.gamestar.de/rss/gamestar.rss",
            "PC Games": "https://www.pcgames.de/feed.cfm?menu_alias=home",
            "IGN": "https://feeds.feedburner.com/ign/games-all",
            "Eurogamer": "https://www.eurogamer.de/feed",
            "GamePro": "https://www.gamepro.de/feed.xml",
        },
        "technik": {
            "Heise": "https://www.heise.de/rss/heise-atom.xml",
            "Golem": "https://rss.golem.de/rss.php?feed=ATOM1.0",
            "ComputerBase": "https://www.computerbase.de/rss/news.xml",
            "t3n": "https://t3n.de/rss.xml",
        },
        "serien": {
            "Serienjunkies": "https://www.serienjunkies.de/news/feed/",
            "Moviepilot": "https://www.moviepilot.de/rss/news",
            "Filmstarts": "https://www.filmstarts.de/rss/news.xml",
        },
        "wissenschaft": {
            "Scinexx": "https://www.scinexx.de/feed/",
            "Spektrum": "https://www.spektrum.de/alias/rss/spektrum-de-rss-feed/996406",
            "Wissenschaft.de": "https://www.wissenschaft.de/feed/",
        },
        "welt": {
            "Tagesschau": "https://www.tagesschau.de/xml/rss2",
            "Zeit Online": "https://newsfeed.zeit.de/index",
            "Spiegel": "https://www.spiegel.de/schlagzeilen/tops/index.rss",
        },
        "musik": {
            "Musikexpress": "https://www.musikexpress.de/feed/",
            "Rolling Stone": "https://www.rollingstone.de/feed/",
        },
    }


# =============================================================================
# ENUMS
# =============================================================================

class FactCategory(Enum):
    """Kategorien von gelerntem Wissen"""
    ANIME = "anime"
    MANGA = "manga"
    GAMING = "gaming"
    TECH = "technik"
    ENTERTAINMENT = "serien"
    MOVIES = "filme"
    MUSIC = "musik"
    SCIENCE = "wissenschaft"
    NEWS = "welt"
    JAPAN = "japan"
    GENERAL = "allgemein"


class EmotionType(Enum):
    """Emotionstypen"""
    JOY = "freude"
    SADNESS = "trauer"
    CURIOSITY = "neugier"
    SURPRISE = "überraschung"
    AFFECTION = "zuneigung"
    PRIDE = "stolz"
    GRATITUDE = "dankbarkeit"
    EXCITEMENT = "aufregung"
    NOSTALGIA = "nostalgie"
    WORRY = "sorge"


class LearningPriority(Enum):
    """Lern-Prioritäten"""
    URGENT = 1          # Sofort lernen
    HIGH = 2            # Bald lernen
    NORMAL = 3          # Normal
    LOW = 4             # Wenn Zeit ist
    BACKGROUND = 5      # Im Hintergrund


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class LearnedFact:
    """Ein gelerntes Faktum"""
    fact_id: str
    content: str
    category: FactCategory
    topic: str
    keywords: List[str]

    # Quelle
    source_title: str
    source_url: str
    source_feed: str

    # Bewertung
    importance: float = 0.5
    trust_score: float = 0.7
    relevance: float = 1.0          # Sinkt mit der Zeit

    # Nutzung
    times_recalled: int = 0
    last_recalled: Optional[str] = None

    # Verknüpfungen
    related_facts: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Meta
    learned_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.learned_at:
            self.learned_at = now
        if not self.updated_at:
            self.updated_at = now
        if not self.fact_id:
            self.fact_id = hashlib.md5(
                f"{self.content[:100]}{self.source_url}".encode()
            ).hexdigest()[:12]

    def calculate_current_importance(self) -> float:
        """Berechnet aktuelle Wichtigkeit mit Zeitverfall"""
        try:
            learned = datetime.fromisoformat(self.learned_at)
            days_old = (datetime.now() - learned).days

            # Basis-Wichtigkeit
            base = self.importance

            # Zeitverfall (langsam)
            decay = max(0, 1 - (days_old * LearningConfig.FACT_DECAY_RATE))

            # Nutzungs-Bonus
            usage_bonus = min(0.3, self.times_recalled * 0.05)

            return max(
                LearningConfig.FACT_MIN_IMPORTANCE,
                base * decay + usage_bonus
            )
        except Exception:
            return self.importance


@dataclass
class LearningEmotionalMemory:
    """
    Emotionale Erinnerung für das Lernsystem.

    (Umbenannt von EmotionalMemory um Konflikte zu vermeiden)
    """
    id: str
    timestamp: str
    trigger: str
    emotion: str
    intensity: float
    valence: float
    context: str
    lasting_impact: float

    # Erweitert
    related_topics: List[str] = field(default_factory=list)
    user_involved: bool = True


# Alias für Kompatibilität
EmotionalMemory = LearningEmotionalMemory


@dataclass
class LearningTopic:
    """Ein verfolgtes Thema/Interesse (für Lernsystem)"""
    topic: str
    category: str
    interest_level: float
    first_seen: str
    last_seen: str
    mention_count: int = 1
    facts_learned: int = 0
    is_active: bool = True


@dataclass
class LearningSession:
    """Eine Lernsession"""
    session_id: str
    started_at: str
    category: str

    articles_read: int = 0
    facts_learned: int = 0
    facts_updated: int = 0
    new_topics: List[str] = field(default_factory=list)

    duration_seconds: float = 0
    finished_at: str = ""
    success: bool = True
    error_message: str = ""


# =============================================================================
# FAKTEN-EXTRAKTOR (erweitert)
# =============================================================================

class FactExtractor:
    """
    Extrahiert Fakten aus Text - optimiert für Pi, ohne LLM.
    """

    # Fakten-Indikatoren (Deutsch & Englisch)
    FACT_INDICATORS = {
        "de": [
            "wurde", "wird", "ist", "sind", "hat", "haben", "erhält",
            "erscheint", "erschien", "startet", "startete", "beginnt",
            "angekündigt", "veröffentlicht", "enthüllt", "bestätigt",
            "erreicht", "übertrifft", "gewinnt", "bricht", "setzt",
            "neu", "erste", "größte", "beste", "offiziell", "exklusiv",
            "laut", "zeigt", "meldet", "berichtet", "erklärt",
            "entwickelt", "plant", "arbeitet an", "präsentiert",
        ],
        "en": [
            "is", "are", "was", "were", "has", "have", "will",
            "announced", "released", "revealed", "confirmed",
            "launches", "starts", "begins", "reaches", "wins",
            "new", "first", "biggest", "best", "official", "exclusive",
            "according to", "shows", "reports", "explains",
        ],
    }

    # Kategorie-Keywords
    CATEGORY_KEYWORDS = {
        FactCategory.ANIME: [
            "anime", "manga", "staffel", "season", "episode", "studio",
            "crunchyroll", "netflix", "funimation", "simulcast", "dub",
            "light novel", "ova", "film", "isekai", "shonen", "seinen",
            "shojo", "mecha", "slice of life", "iyashikei", "adaptation",
            "opening", "ending", "ost", "seiyuu", "synchronsprecher",
        ],
        FactCategory.GAMING: [
            "spiel", "game", "release", "dlc", "update", "patch", "mod",
            "playstation", "xbox", "nintendo", "steam", "pc", "switch",
            "ps5", "ps4", "trailer", "gameplay", "entwickler", "studio",
            "sequel", "remake", "remaster", "early access", "beta",
            "multiplayer", "singleplayer", "rpg", "fps", "mmorpg",
            "indie", "triple-a", "aaa", "esports", "speedrun",
        ],
        FactCategory.TECH: [
            "software", "hardware", "update", "version", "prozessor",
            "gpu", "cpu", "ram", "speicher", "cloud", "ki", "ai",
            "smartphone", "laptop", "server", "sicherheit", "hack",
            "android", "ios", "windows", "linux", "mac", "apple",
            "google", "microsoft", "nvidia", "amd", "intel",
            "open source", "api", "framework", "programmierung",
        ],
        FactCategory.ENTERTAINMENT: [
            "serie", "staffel", "season", "episode", "streaming",
            "netflix", "disney", "amazon", "hbo", "paramount",
            "trailer", "premiere", "finale", "schauspieler", "regisseur",
            "showrunner", "spin-off", "prequel", "sequel",
        ],
        FactCategory.SCIENCE: [
            "studie", "forschung", "wissenschaftler", "entdeckung",
            "experiment", "theorie", "nasa", "esa", "weltraum",
            "planet", "stern", "galaxie", "physik", "chemie", "biologie",
            "medizin", "klima", "umwelt", "energie", "quantenphysik",
        ],
    }

    # Erweiterte Stopwörter
    STOPWORDS = {
        # Deutsch
        "der", "die", "das", "ein", "eine", "einer", "eines", "einem",
        "und", "oder", "aber", "doch", "jedoch", "sondern", "sowie",
        "ist", "sind", "war", "waren", "wird", "werden", "wurde",
        "hat", "haben", "hatte", "hatten", "kann", "können",
        "mit", "von", "zu", "für", "auf", "an", "in", "bei", "nach",
        "aus", "um", "über", "unter", "durch", "gegen", "ohne",
        "ich", "du", "er", "sie", "es", "wir", "ihr", "sie",
        "mein", "dein", "sein", "unser", "euer", "ihr",
        "dieser", "diese", "dieses", "jener", "jene", "jenes",
        "hier", "dort", "da", "nun", "jetzt", "dann", "also",
        "auch", "noch", "schon", "nur", "sehr", "so", "wie",
        "nicht", "kein", "keine", "nichts", "niemand",
        # Englisch
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "can", "could", "should", "may", "might", "must",
        "of", "to", "in", "for", "on", "with", "at", "by", "from",
        "this", "that", "these", "those", "it", "its",
    }

    # Entitäts-Muster
    ENTITY_PATTERNS = [
        r'\b[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*\b',  # Namen
        r'\b[A-Z]{2,}\b',                                       # Abkürzungen
        r'\b\d{4}\b',                                           # Jahre
        r'\b\d+(?:\.\d+)?\s*(?:Millionen?|Milliarden?|Mio|Mrd)\b',  # Zahlen
    ]

    def __init__(self):
        self.extracted_count = 0

    def extract_facts(self, text: str, title: str = "",
                      category: FactCategory = FactCategory.GENERAL,
                      max_facts: int = 5) -> List[Dict]:
        """Extrahiert Fakten aus Text"""
        facts = []

        # Titel ist oft der wichtigste Fakt
        if title and len(title) > 15:
            title_data = self._analyze_sentence(title, category)
            title_data["is_title"] = True
            title_data["importance"] = min(1.0, title_data["importance"] + 0.3)
            facts.append(title_data)

        # Sätze analysieren
        sentences = self._split_sentences(text)
        scored = []

        for sent in sentences:
            # Längen-Filter
            if len(sent) < 25 or len(sent) > 400:
                continue

            # Duplikat-Check mit Titel
            if title and self._is_similar(sent, title):
                continue

            analysis = self._analyze_sentence(sent, category)
            if analysis["importance"] > 0.25:
                scored.append(analysis)

        # Nach Wichtigkeit sortieren
        scored.sort(key=lambda x: x["importance"], reverse=True)

        # Duplikate unter den Fakten entfernen
        seen_content = {title.lower()} if title else set()
        for item in scored:
            if len(facts) >= max_facts:
                break

            content_lower = item["content"].lower()
            if not any(self._is_similar(content_lower, seen) for seen in seen_content):
                item["is_title"] = False
                facts.append(item)
                seen_content.add(content_lower)

        self.extracted_count += len(facts)
        return facts

    def _analyze_sentence(self, sentence: str, category: FactCategory) -> Dict:
        """Analysiert einen Satz vollständig"""
        sent_lower = sentence.lower()
        score = 0.0

        # 1. Fakten-Indikatoren
        for lang_indicators in self.FACT_INDICATORS.values():
            for indicator in lang_indicators:
                if indicator in sent_lower:
                    score += 0.08

        # 2. Kategorie-Keywords
        cat_keywords = self.CATEGORY_KEYWORDS.get(category, [])
        keyword_matches = 0
        for kw in cat_keywords:
            if kw in sent_lower:
                keyword_matches += 1
                score += 0.12

        # 3. Entitäten (Namen, Zahlen, etc.)
        entities = self._extract_entities(sentence)
        score += min(0.25, len(entities) * 0.05)

        # 4. Zahlen und Daten
        if re.search(r'\b(19|20)\d{2}\b', sentence):  # Jahr
            score += 0.1
        if re.search(r'\d+\s*%', sentence):  # Prozent
            score += 0.1
        if re.search(r'\d+(?:\.\d+)?\s*(Millionen?|Milliarden?|Euro|Dollar|\$|€)', sentence):
            score += 0.15

        # 5. Längen-Bonus (mittellange Sätze sind oft informativ)
        if 40 < len(sentence) < 200:
            score += 0.1
        elif 200 <= len(sentence) < 300:
            score += 0.05

        # 6. Zitat-Malus (Zitate sind oft weniger faktisch)
        if '"' in sentence or '„' in sentence:
            score *= 0.8

        # Keywords extrahieren
        keywords = self._extract_keywords(sentence)

        # Topic erkennen
        topic = self._detect_topic(sentence, entities)

        return {
            "content": sentence.strip(),
            "keywords": keywords,
            "entities": entities,
            "topic": topic,
            "importance": min(1.0, score),
            "category_relevance": keyword_matches,
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Teilt Text in Sätze"""
        # Bereinigen
        text = re.sub(r'\s+', ' ', text)

        # Satz-Trennung (robust)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÄÖÜ])', text)

        result = []
        for sent in sentences:
            sent = sent.strip()
            if sent and len(sent) > 10:
                result.append(sent)

        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiert Keywords"""
        words = re.findall(r'\b[a-zäöüßA-ZÄÖÜ]{3,}\b', text.lower())
        words = [w for w in words if w not in self.STOPWORDS and len(w) >= 4]

        # Häufigkeit
        freq = Counter(words)

        # Top Keywords (unique, sortiert nach Häufigkeit)
        return [w for w, _ in freq.most_common(15)]

    def _extract_entities(self, text: str) -> List[str]:
        """Extrahiert benannte Entitäten"""
        entities = []

        for pattern in self.ENTITY_PATTERNS:
            matches = re.findall(pattern, text)
            entities.extend(matches)

        # Deduplizieren und filtern
        seen = set()
        result = []
        for ent in entities:
            ent_lower = ent.lower()
            if ent_lower not in seen and ent_lower not in self.STOPWORDS:
                seen.add(ent_lower)
                result.append(ent)

        return result[:10]

    def _detect_topic(self, text: str, entities: List[str]) -> str:
        """Erkennt das Hauptthema"""
        # Priorität: Erste relevante Entität
        for ent in entities:
            if len(ent) >= 3 and ent[0].isupper():
                return ent

        # Fallback: Erstes Großgeschriebenes Wort
        match = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]{3,})\b', text)
        if match:
            return match.group(1)

        return "Allgemein"

    def _is_similar(self, text1: str, text2: str, threshold: float = 0.6) -> bool:
        """Prüft Ähnlichkeit zweier Texte"""
        if isinstance(text1, str):
            text1 = text1.lower()
        if isinstance(text2, str):
            text2 = text2.lower()

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return (intersection / union) > threshold if union > 0 else False


# =============================================================================
# WISSENS-DATENBANK (erweitert)
# =============================================================================

class LearningKnowledgeDB:
    """
    Holos Wissensdatenbank - Wrapper um HoloDatabaseManager.knowledge.

    Nutzt zentrale Datenbank statt eigener JSON-Speicherung.

    (Umbenannt von KnowledgeDatabase um Konflikte mit
     holo_database_system.KnowledgeDatabase zu vermeiden)
    """

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        """
        Args:
            db_path: DEPRECATED - wird ignoriert
            db: HoloDatabaseManager Instanz
        """
        self.db = db
        self._cache: Dict[str, LearnedFact] = {}

        # Statistiken (lokal gecached)
        self.total_searches = 0
        self.total_recalls = 0

        if db:
            logger.info("[LearningKnowledgeDB] 💾 Mit HoloDatabaseManager initialisiert")
        else:
            logger.warning("[LearningKnowledgeDB] ⚠️ Keine Database - eingeschränkt")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet Database nachträglich"""
        self.db = db
        logger.info("[LearningKnowledgeDB] 💾 Database verbunden")

    def _to_learned_fact(self, db_fact: dict) -> LearnedFact:
        """Konvertiert DB-Fakt zu LearnedFact"""
        try:
            return LearnedFact(
                fact_id=db_fact.get('id', ''),
                content=db_fact.get('value', ''),
                category=FactCategory(db_fact.get('category', 'allgemein')),
                topic=db_fact.get('key', ''),
                keywords=[],
                source_title=db_fact.get('source', ''),
                source_url='',
                source_feed='',
                importance=db_fact.get('confidence', 0.5),
                trust_score=db_fact.get('source_quality', 0.7),
                relevance=1.0,
                times_recalled=db_fact.get('times_confirmed', 0),
                last_recalled=db_fact.get('last_confirmed', ''),
                related_facts=[],
                tags=[],
                learned_at=db_fact.get('first_learned', ''),
                updated_at=db_fact.get('last_confirmed', ''),
            )
        except Exception:
            return None

    def add_fact(self, fact: LearnedFact) -> Tuple[bool, str]:
        """Fügt Fakt über HoloDatabaseManager hinzu"""
        if not self.db:
            self._cache[fact.fact_id] = fact
            return True, "cached_only"

        try:
            # Kategorie-Mapping
            cat_map = {
                'technik': 'technology',
                'politik': 'world_events',
                'wirtschaft': 'finance',
                'wissenschaft': 'science',
                'kultur': 'entertainment',
                'sport': 'entertainment',
            }
            db_cat = cat_map.get(fact.category.value, 'general')

            self.db.knowledge.store_fact(
                category=db_cat,
                key=fact.topic or fact.content[:50],
                value=fact.content,
                confidence=fact.importance,
                source=fact.source_title,
                source_quality=fact.trust_score,
            )
            self._cache[fact.fact_id] = fact
            return True, "added"
        except Exception as e:
            logger.debug(f"Fakt speichern: {e}")
            self._cache[fact.fact_id] = fact
            return True, "cached_only"

    def search(self, query: str, category: FactCategory = None,
               limit: int = 10, min_importance: float = 0.0) -> List[LearnedFact]:
        """Durchsucht Wissensdatenbank via HoloDatabaseManager"""
        self.total_searches += 1
        results = []

        if self.db:
            try:
                # Suche in DB
                db_results = self.db.knowledge.search_facts(query, limit=limit * 2)
                for r in db_results:
                    fact = self._to_learned_fact(r)
                    if fact and fact.importance >= min_importance:
                        results.append(fact)
            except Exception as e:
                logger.debug(f"DB-Suche: {e}")

        # Fallback auf Cache
        if not results:
            query_lower = query.lower()
            for fact in self._cache.values():
                if query_lower in fact.content.lower():
                    if fact.importance >= min_importance:
                        results.append(fact)

        # Sortieren und limitieren
        results.sort(key=lambda f: f.importance, reverse=True)
        return results[:limit]

    def get_by_category(self, category: FactCategory, limit: int = 20) -> List[LearnedFact]:
        """Holt Fakten einer Kategorie"""
        if not self.db:
            return [f for f in self._cache.values() if f.category == category][:limit]

        try:
            cat_map = {'technik': 'technology', 'politik': 'world_events'}
            db_cat = cat_map.get(category.value, category.value)
            db_facts = self.db.knowledge.get_facts_by_category(db_cat)
            return [self._to_learned_fact(f) for f in db_facts[:limit] if f]
        except Exception:
            return []

    def get_by_topic(self, topic: str, limit: int = 20) -> List[LearnedFact]:
        """Holt Fakten zu einem Topic"""
        return self.search(topic, limit=limit)

    def get_recent(self, category: FactCategory = None, limit: int = 10) -> List[LearnedFact]:
        """Holt neueste Fakten"""
        if category:
            return self.get_by_category(category, limit)
        return self.search("", limit=limit)

    def get_most_recalled(self, limit: int = 10) -> List[LearnedFact]:
        """Holt am häufigsten abgerufene Fakten"""
        facts = list(self._cache.values())
        facts.sort(key=lambda f: f.times_recalled, reverse=True)
        return facts[:limit]

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        return {
            "total_facts": len(self._cache),
            "total_searches": self.total_searches,
            "total_recalls": self.total_recalls,
            "db_connected": self.db is not None,
        }


# =============================================================================
# NEWS FETCHER (erweitert)
# =============================================================================

class NewsFetcher:
    """Holt echte News aus RSS Feeds"""

    def __init__(self):
        self.feeds = LearningConfig.NEWS_FEEDS
        self.timeout = 15
        self.user_agent = "Mozilla/5.0 (Holo Learning System)"

        # Tracking
        self.fetch_stats: Dict[str, Dict] = {}
        self.last_fetch: Dict[str, float] = {}

    def fetch_category(self, category: str, max_articles: int = 15) -> List[Dict]:
        """Holt News einer Kategorie"""
        if category not in self.feeds:
            logger.warning(f"Unbekannte Kategorie: {category}")
            return []

        articles = []
        feeds = self.feeds[category]

        for source, url in feeds.items():
            try:
                articles.extend(self._fetch_feed(source, url, category))
            except Exception as e:
                logger.debug(f"Feed {source} fehlgeschlagen: {e}")
                self._update_stats(source, success=False, error=str(e))

        self.last_fetch[category] = time.time()

        # Nach Datum sortieren (neueste zuerst) und limitieren
        articles.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return articles[:max_articles]

    def _fetch_feed(self, source: str, url: str, category: str) -> List[Dict]:
        """Holt einen einzelnen Feed"""
        try:
            import feedparser
        except ImportError:
            logger.error("feedparser nicht installiert!")
            return []

        req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
        response = urllib.request.urlopen(req, timeout=self.timeout)
        feed = feedparser.parse(response.read())

        articles = []
        for entry in feed.entries[:10]:
            # Timestamp extrahieren
            timestamp = 0
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    from time import mktime
                    timestamp = mktime(entry.published_parsed)
                except Exception:
                    pass

            articles.append({
                "title": entry.get("title", "").strip(),
                "summary": self._clean_html(entry.get("summary", ""))[:800],
                "link": entry.get("link", ""),
                "source": source,
                "category": category,
                "timestamp": timestamp,
                "published": entry.get("published", ""),
            })

        self._update_stats(source, success=True, count=len(articles))
        return articles

    def _clean_html(self, html: str) -> str:
        """Entfernt HTML-Tags und bereinigt Text"""
        # HTML-Tags entfernen
        text = re.sub(r'<[^>]+>', '', html)
        # Mehrfache Leerzeichen
        text = re.sub(r'\s+', ' ', text)
        # Entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        return text.strip()

    def _update_stats(self, source: str, success: bool, count: int = 0, error: str = ""):
        """Aktualisiert Fetch-Statistiken"""
        if source not in self.fetch_stats:
            self.fetch_stats[source] = {
                "success_count": 0,
                "fail_count": 0,
                "total_articles": 0,
                "last_error": "",
            }

        stats = self.fetch_stats[source]
        if success:
            stats["success_count"] += 1
            stats["total_articles"] += count
        else:
            stats["fail_count"] += 1
            stats["last_error"] = error

    def fetch_by_interest(self, max_per_category: int = 10) -> Dict[str, List[Dict]]:
        """Holt News basierend auf Holos Interessen"""
        all_news = {}

        # Kategorien nach Interesse sortieren
        sorted_cats = sorted(
            LearningConfig.INTERESTS.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for category, interest in sorted_cats:
            if category in self.feeds:
                # Mehr Artikel für höheres Interesse
                count = int(max_per_category * interest)
                all_news[category] = self.fetch_category(category, max(3, count))

        return all_news

    def get_stats(self) -> Dict:
        """Gibt Fetch-Statistiken zurück"""
        return {
            "feeds": self.fetch_stats,
            "last_fetch": self.last_fetch,
            "available_categories": list(self.feeds.keys()),
        }


# =============================================================================
# LEARNING TOPIC TRACKER (Wrapper um HoloDatabaseManager.knowledge)
# =============================================================================

class LearningTopicTracker:
    """
    Verfolgt Themen und Interessen über Zeit.

    Nutzt HoloDatabaseManager.knowledge für Persistenz.
    Kein eigenes JSON mehr - alles zentral in der Datenbank!

    NEU v2.0: Adaptives Interesse-Learning
    - Lernt welche Themen beim User gut ankommen
    - Passt Interessen basierend auf User-Reaktionen an
    - Erkennt neue Interessengebiete automatisch
    """

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        """
        Args:
            db_path: DEPRECATED - wird ignoriert, nur für Kompatibilität
            db: HoloDatabaseManager Instanz (empfohlen)
        """
        self.db = db
        self._cache: Dict[str, LearningTopic] = {}  # Lokaler Cache

        # === ADAPTIVES LERNEN v2.0 ===
        # User-Reaktions-Tracking pro Topic/Kategorie
        self.topic_reactions: Dict[str, List[float]] = {}  # topic → [reaktionen]
        self.category_reactions: Dict[str, List[float]] = {}  # category → [reaktionen]
        # Lernrate für Interesse-Updates
        self.interest_learning_rate: float = 0.05
        # Adaptive Basis-Interessen (überschreiben LearningConfig.INTERESTS)
        self.adaptive_base_interests: Dict[str, float] = {}
        # Letztes besprochenes Topic für Feedback
        self.last_discussed_topic: Optional[str] = None
        self.last_discussed_category: Optional[str] = None

        if db:
            self._load_from_db()
            logger.info("[LearningTopicTracker] 💾 Mit Database initialisiert")
        else:
            logger.warning("[LearningTopicTracker] ⚠️ Keine Database - Funktionalität eingeschränkt")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet Database nachträglich"""
        self.db = db
        self._load_from_db()
        logger.info("[LearningTopicTracker] 💾 Database verbunden")

    def _load_from_db(self):
        """Lädt Topics aus Database in Cache"""
        if not self.db:
            return

        try:
            topics = self.db.knowledge.get_tracked_topics(min_interest=0.0, limit=500)
            for t in topics:
                key = t.get('topic', '').lower()
                if key:
                    self._cache[key] = LearningTopic(
                        topic=t.get('topic', ''),
                        category=t.get('category', 'allgemein'),
                        interest_level=t.get('interest_level', 0.5),
                        first_seen=t.get('first_tracked', ''),
                        last_seen=t.get('last_discussed', ''),
                        mention_count=t.get('times_discussed', 1),
                        facts_learned=0,  # Aus related_facts parsen wenn nötig
                        is_active=t.get('interest_level', 0) > 0.1,
                    )
        except Exception as e:
            logger.debug(f"Topics aus DB laden: {e}")

    def track_topic(self, topic: str, category: str = "allgemein",
                    from_learning: bool = False) -> LearningTopic:
        """Verfolgt ein neues oder existierendes Topic"""
        topic_key = topic.lower()
        now = datetime.now().isoformat()

        # Cache aktualisieren
        if topic_key in self._cache:
            tracked = self._cache[topic_key]
            tracked.last_seen = now
            tracked.mention_count += 1
            if from_learning:
                tracked.facts_learned += 1
            tracked.interest_level = min(1.0, tracked.interest_level + 0.02)
        else:
            base_interest = LearningConfig.INTERESTS.get(category, 0.5)
            tracked = LearningTopic(
                topic=topic,
                category=category,
                interest_level=base_interest,
                first_seen=now,
                last_seen=now,
                mention_count=1,
                facts_learned=1 if from_learning else 0,
            )
            self._cache[topic_key] = tracked

        # In Database speichern
        if self.db:
            try:
                self.db.knowledge.track_topic(
                    topic=topic,
                    interest_level=tracked.interest_level,
                    related_facts=f"category:{category},facts:{tracked.facts_learned}",
                    curiosity_questions=""
                )
            except Exception as e:
                logger.debug(f"Topic DB sync: {e}")

        return tracked

    def get_active_topics(self, limit: int = 20) -> List[LearningTopic]:
        """Holt aktive Topics sortiert nach Interesse"""
        # Erst aus DB aktualisieren
        if self.db:
            try:
                db_topics = self.db.knowledge.get_tracked_topics(min_interest=0.1, limit=limit)
                for t in db_topics:
                    key = t.get('topic', '').lower()
                    if key and key not in self._cache:
                        self._cache[key] = LearningTopic(
                            topic=t.get('topic', ''),
                            category='allgemein',
                            interest_level=t.get('interest_level', 0.5),
                            first_seen=t.get('first_tracked', ''),
                            last_seen=t.get('last_discussed', ''),
                            mention_count=t.get('times_discussed', 1),
                            facts_learned=0,
                            is_active=True,
                        )
            except Exception:
                pass

        active = [t for t in self._cache.values() if t.is_active]
        active.sort(key=lambda t: (t.interest_level, t.mention_count), reverse=True)
        return active[:limit]

    def get_topics_for_category(self, category: str) -> List[LearningTopic]:
        """Holt Topics einer Kategorie"""
        return [t for t in self._cache.values() if t.category == category and t.is_active]

    def decay_inactive(self, days_threshold: int = 14):
        """Reduziert Interesse für lange nicht gesehene Topics"""
        now = datetime.now()

        for tracked in self._cache.values():
            try:
                last = datetime.fromisoformat(tracked.last_seen)
                days_inactive = (now - last).days

                if days_inactive > days_threshold:
                    decay = 0.02 * (days_inactive - days_threshold)
                    tracked.interest_level = max(0.1, tracked.interest_level - decay)

                    if tracked.interest_level < 0.15:
                        tracked.is_active = False

                    # Update in DB
                    if self.db:
                        try:
                            self.db.knowledge.track_topic(
                                topic=tracked.topic,
                                interest_level=tracked.interest_level
                            )
                        except Exception:
                            pass
            except Exception:
                pass

    # === ADAPTIVES LERNEN v2.0 ===

    def record_topic_discussion(self, topic: str, category: str = "allgemein") -> None:
        """
        Zeichnet auf, dass ein Topic besprochen wurde.

        Sollte aufgerufen werden, wenn Holo über ein Topic spricht,
        damit späteres Feedback zugeordnet werden kann.
        """
        self.last_discussed_topic = topic.lower()
        self.last_discussed_category = category.lower()

        # Track auch normal
        self.track_topic(topic, category)

    def observe_user_reaction(self, reaction_score: float,
                              topic: str = None,
                              category: str = None) -> None:
        """
        Beobachtet User-Reaktion auf ein Topic und lernt daraus.

        Args:
            reaction_score: User-Reaktion von -1 (negativ) bis +1 (positiv)
            topic: Optionales Topic (sonst last_discussed)
            category: Optionale Kategorie (sonst last_discussed)
        """
        topic = (topic or self.last_discussed_topic or "").lower()
        category = (category or self.last_discussed_category or "allgemein").lower()

        if not topic and not category:
            return

        # Topic-Reaktion speichern
        if topic:
            if topic not in self.topic_reactions:
                self.topic_reactions[topic] = []
            self.topic_reactions[topic].append(reaction_score)

            # Nur letzte 50 Reaktionen behalten
            if len(self.topic_reactions[topic]) > 50:
                self.topic_reactions[topic] = self.topic_reactions[topic][-50:]

            # Interesse sofort leicht anpassen
            if topic in self._cache:
                adjustment = reaction_score * self.interest_learning_rate
                self._cache[topic].interest_level = max(0.1, min(1.0,
                    self._cache[topic].interest_level + adjustment))

        # Kategorie-Reaktion speichern
        if category:
            if category not in self.category_reactions:
                self.category_reactions[category] = []
            self.category_reactions[category].append(reaction_score)

            if len(self.category_reactions[category]) > 100:
                self.category_reactions[category] = self.category_reactions[category][-100:]

    def adapt_base_interests(self) -> Dict[str, float]:
        """
        Passt die Basis-Interessen basierend auf gelernten Reaktionen an.

        Returns:
            Dict mit alten und neuen Basis-Interessen
        """
        old_interests = LearningConfig.INTERESTS.copy()

        for category, reactions in self.category_reactions.items():
            if len(reactions) < 5:
                continue  # Nicht genug Daten

            avg_reaction = sum(reactions) / len(reactions)
            current_base = LearningConfig.INTERESTS.get(category, 0.5)

            # Anpassung basierend auf Reaktionen
            if avg_reaction > 0.2:
                # Positive Reaktionen → Interesse erhöhen
                new_interest = min(1.0, current_base + avg_reaction * 0.1)
            elif avg_reaction < -0.2:
                # Negative Reaktionen → Interesse senken
                new_interest = max(0.1, current_base + avg_reaction * 0.1)
            else:
                new_interest = current_base

            self.adaptive_base_interests[category] = new_interest

        return {
            "original_interests": old_interests,
            "adapted_interests": self.adaptive_base_interests,
            "category_reactions": {
                k: sum(v) / len(v) if v else 0.0
                for k, v in self.category_reactions.items()
            }
        }

    def get_effective_interest(self, category: str) -> float:
        """
        Gibt das effektive Interesse für eine Kategorie zurück.

        Kombiniert statische und gelernte Interessen.
        """
        base = LearningConfig.INTERESTS.get(category.lower(), 0.5)
        adapted = self.adaptive_base_interests.get(category.lower())

        if adapted is not None:
            # Mische statisch und adaptiv (60% adaptiv wenn vorhanden)
            return 0.4 * base + 0.6 * adapted

        return base

    def get_topic_insights(self, topic: str) -> Dict[str, Any]:
        """
        Gibt Einblicke in gelernte Topic-Präferenzen.
        """
        topic_key = topic.lower()
        insights = {
            "topic": topic,
            "tracked": topic_key in self._cache,
            "reactions": None,
            "interest_level": None,
        }

        if topic_key in self._cache:
            cached = self._cache[topic_key]
            insights["interest_level"] = cached.interest_level
            insights["mention_count"] = cached.mention_count

        if topic_key in self.topic_reactions:
            reactions = self.topic_reactions[topic_key]
            insights["reactions"] = {
                "count": len(reactions),
                "avg": sum(reactions) / len(reactions) if reactions else 0.0,
                "recent": sum(reactions[-10:]) / len(reactions[-10:]) if len(reactions) >= 10 else None,
            }

        return insights

    def get_learning_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über adaptives Lernen zurück."""
        return {
            "topics_with_reactions": len(self.topic_reactions),
            "categories_with_reactions": len(self.category_reactions),
            "adapted_interests": self.adaptive_base_interests.copy(),
            "learning_rate": self.interest_learning_rate,
            "top_reacted_topics": sorted(
                [(t, sum(r) / len(r)) for t, r in self.topic_reactions.items() if r],
                key=lambda x: x[1],
                reverse=True
            )[:10],
        }

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        return {
            "total_topics": len(self.topics),
            "active_topics": sum(1 for t in self.topics.values() if t.is_active),
            "by_category": Counter(t.category for t in self.topics.values()),
            "top_interests": [
                {"topic": t.topic, "interest": t.interest_level, "mentions": t.mention_count}
                for t in self.get_active_topics(10)
            ],
        }


# =============================================================================
# MOOD CONTAGION (verbessert)
# =============================================================================

class MoodContagion:
    """
    Stimmungs-Ansteckung: Holo wird von User-Stimmung beeinflusst.
    """

    # Erweiterte Stimmungs-Indikatoren
    MOOD_INDICATORS = {
        'happy': {
            'keywords': [
                'freue', 'freut', 'froh', 'glücklich', 'toll', 'super', 'großartig',
                'fantastisch', 'genial', 'perfekt', 'wunderbar', 'herrlich',
                'hurra', 'juhu', 'yeah', 'yay', 'nice', 'geil', 'hammer',
                '😊', '😄', '😁', '🎉', '❤️', '💕', ':)', ':-)', 'haha', 'hihi', 'lol',
            ],
            'valence': 0.8,
            'arousal': 0.6,
        },
        'excited': {
            'keywords': [
                'wow', 'krass', 'wahnsinn', 'unglaublich', 'aufgeregt', 'gespannt',
                'kann kaum erwarten', 'hyped', 'omg', 'mega', 'extrem',
                '🤩', '😍', '🔥', '⚡', '!!!', 'wooo',
            ],
            'valence': 0.9,
            'arousal': 0.9,
        },
        'sad': {
            'keywords': [
                'traurig', 'schade', 'leider', 'schlecht', 'mist', 'doof',
                'enttäuscht', 'deprimiert', 'einsam', 'allein', 'verloren',
                'hoffnungslos', 'niedergeschlagen', 'down',
                '😢', '😞', '😔', '😭', ':(', ':-(', 'seufz',
            ],
            'valence': -0.7,
            'arousal': 0.3,
        },
        'angry': {
            'keywords': [
                'wütend', 'ärger', 'ärgert', 'nervig', 'nervt', 'kotzt', 'hass',
                'blöd', 'dumm', 'idiot', 'scheiße', 'mist', 'verdammt',
                'unfair', 'ungerecht', 'frustriert', 'genervt',
                '😤', '😠', '😡', '🤬', 'grr', 'argh',
            ],
            'valence': -0.8,
            'arousal': 0.8,
        },
        'curious': {
            'keywords': [
                'interessant', 'spannend', 'neugierig', 'frage mich', 'faszinierend',
                'wie', 'warum', 'was ist', 'erzähl', 'erkläre', 'wissen',
                '🤔', '🧐', 'hmm', 'hm', 'interessant',
            ],
            'valence': 0.4,
            'arousal': 0.5,
        },
        'tired': {
            'keywords': [
                'müde', 'erschöpft', 'fertig', 'kaputt', 'schlapp', 'platt',
                'ausgelaugt', 'energie los', 'schlafen', 'bett',
                '😴', '🥱', 'gähn', 'zzz',
            ],
            'valence': -0.2,
            'arousal': 0.1,
        },
        'loving': {
            'keywords': [
                'liebe', 'lieb', 'vermisse', 'mag dich', 'süß', 'kuschel',
                'knuddel', 'umarmung', 'danke', 'dankbar', 'schön dass',
                '❤️', '💕', '💖', '🥰', '😘', '<3',
            ],
            'valence': 0.9,
            'arousal': 0.4,
        },
        'anxious': {
            'keywords': [
                'angst', 'sorge', 'sorgen', 'besorgt', 'ängstlich', 'nervös',
                'unsicher', 'stress', 'panik', 'überwältigt',
                '😰', '😨', '😧', '😱',
            ],
            'valence': -0.5,
            'arousal': 0.7,
        },
    }

    def __init__(self, contagion_rate: float = None, db: 'HoloDatabaseManager' = None):
        self.contagion_rate = contagion_rate or LearningConfig.MOOD_CONTAGION_RATE
        self.user_mood_history: List[Dict] = []
        self.current_influence = 0.0
        self.db = db  # NEU: Database Connection
        self._last_holo_mood = 0.5  # Für Tracking

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet Database nachträglich"""
        self.db = db
        logger.info("[MoodContagion] 💾 Database verbunden")

    def detect_user_mood(self, message: str) -> Dict:
        """Erkennt User-Stimmung aus Nachricht"""
        msg_lower = message.lower()

        detected = 'neutral'
        highest = 0
        valence = 0.0
        arousal = 0.5

        # Alle Stimmungen prüfen
        mood_scores = {}
        for mood, data in self.MOOD_INDICATORS.items():
            count = sum(1 for kw in data['keywords'] if kw in msg_lower)
            if count > 0:
                mood_scores[mood] = count

        # Beste Stimmung wählen
        if mood_scores:
            detected = max(mood_scores, key=mood_scores.get)
            highest = mood_scores[detected]
            valence = self.MOOD_INDICATORS[detected]['valence']
            arousal = self.MOOD_INDICATORS[detected]['arousal']

        # Confidence berechnen
        confidence = min(1.0, highest * 0.25) if highest > 0 else 0.2

        result = {
            'mood': detected,
            'valence': valence,
            'arousal': arousal,
            'confidence': confidence,
            'all_detected': mood_scores,
            'timestamp': datetime.now().isoformat(),
        }

        # History speichern
        self.user_mood_history.append(result)
        self.user_mood_history = self.user_mood_history[-30:]

        return result

    def calculate_mood_influence(self, user_mood: Dict, current_holo_mood: float) -> float:
        """Berechnet Einfluss auf Holos Stimmung"""
        user_valence = user_mood.get('valence', 0)
        confidence = user_mood.get('confidence', 0.3)

        # Valence von -1/+1 auf 0-1 umrechnen
        user_normalized = (user_valence + 1) / 2

        # Einfluss gewichtet nach Confidence
        influence = self.contagion_rate * confidence
        self.current_influence = influence

        # Neue Stimmung
        new_mood = current_holo_mood * (1 - influence) + user_normalized * influence
        new_mood = max(0.0, min(1.0, new_mood))

        # NEU: In Database loggen wenn signifikante Änderung
        if self.db and abs(new_mood - self._last_holo_mood) > 0.05:
            try:
                self.db.emotions.log_mood_contagion(
                    detected_user_mood=user_mood.get('mood', 'neutral'),
                    user_mood_intensity=confidence,
                    holo_mood_before=self._last_holo_mood,
                    holo_mood_after=new_mood,
                    context=f"valence={user_valence:.2f}, arousal={user_mood.get('arousal', 0.5):.2f}"
                )
            except Exception as e:
                logger.debug(f"Mood contagion log failed: {e}")

        self._last_holo_mood = new_mood
        return new_mood

    def get_mood_trend(self) -> Dict:
        """Analysiert Stimmungstrend"""
        if len(self.user_mood_history) < 3:
            return {"trend": "unknown", "message": "Zu wenig Daten"}

        recent = self.user_mood_history[-10:]
        avg_valence = sum(m['valence'] for m in recent) / len(recent)
        avg_arousal = sum(m['arousal'] for m in recent) / len(recent)

        # Trend bestimmen
        if avg_valence > 0.3:
            trend = "positive"
            message = "Der User scheint gute Laune zu haben!"
        elif avg_valence < -0.3:
            trend = "negative"
            message = "Der User scheint nicht so gut drauf zu sein..."
        else:
            trend = "neutral"
            message = "Die Stimmung ist ausgeglichen."

        # Mood-Verteilung
        mood_counts = Counter(m['mood'] for m in recent)

        return {
            "trend": trend,
            "message": message,
            "avg_valence": avg_valence,
            "avg_arousal": avg_arousal,
            "mood_distribution": dict(mood_counts),
            "data_points": len(recent),
        }

    def get_response_modifier(self, user_mood: Dict) -> Dict:
        """Gibt Modifikatoren für Holos Antwort"""
        mood = user_mood.get('mood', 'neutral')

        modifiers = {
            'happy': {
                'energy': 1.2,
                'playfulness': 1.3,
                'empathy_focus': 0.8,
            },
            'excited': {
                'energy': 1.4,
                'playfulness': 1.5,
                'empathy_focus': 0.7,
            },
            'sad': {
                'energy': 0.7,
                'playfulness': 0.5,
                'empathy_focus': 1.5,
            },
            'angry': {
                'energy': 0.8,
                'playfulness': 0.3,
                'empathy_focus': 1.3,
            },
            'tired': {
                'energy': 0.6,
                'playfulness': 0.6,
                'empathy_focus': 1.2,
            },
            'loving': {
                'energy': 1.0,
                'playfulness': 1.1,
                'empathy_focus': 1.4,
            },
        }

        return modifiers.get(mood, {
            'energy': 1.0,
            'playfulness': 1.0,
            'empathy_focus': 1.0,
        })


# =============================================================================
# USER STATE TRACKER - Erkennt User-Zustand für angepasste Reaktionen
# =============================================================================

class UserState(Enum):
    """Erkannter User-Zustand"""
    ENERGETIC = "energetic"      # Aktiv, schreibt viel
    NORMAL = "normal"            # Normales Gespräch
    TIRED = "tired"              # Müde, kurze Antworten
    STRESSED = "stressed"        # Gestresst, hektisch
    SAD = "sad"                  # Traurig, braucht Trost
    HAPPY = "happy"              # Gut drauf
    BUSY = "busy"                # Beschäftigt, wenig Zeit
    AWAY = "away"                # Nicht da / AFK
    SLEEPING = "sleeping"        # Schläft wahrscheinlich


class HoloReaction(Enum):
    """Wie Holo reagieren sollte"""
    BE_ENERGETIC = "be_energetic"        # Enthusiastisch sein
    BE_CALM = "be_calm"                  # Ruhig und entspannt
    BE_SUPPORTIVE = "be_supportive"      # Tröstend, unterstützend
    BE_BRIEF = "be_brief"                # Kurz halten
    LEAVE_ALONE = "leave_alone"          # In Ruhe lassen
    CHEER_UP = "cheer_up"                # Aufmuntern
    MATCH_ENERGY = "match_energy"        # Energie anpassen
    ASK_IF_OK = "ask_if_ok"              # Nachfragen ob alles ok


@dataclass
class UserStateAnalysis:
    """Analyse des User-Zustands"""
    state: UserState
    confidence: float
    energy_level: float          # 0-1 (müde - energetisch)
    engagement_level: float      # 0-1 (abwesend - voll dabei)
    emotional_valence: float     # -1 bis +1 (negativ - positiv)
    recommended_reaction: HoloReaction
    reasoning: str
    should_reduce_messages: bool
    suggested_tone: str


class UserStateTracker:
    """
    Trackt User-Zustand über Zeit und gibt Empfehlungen für Holos Verhalten.

    Analysiert:
    - Nachrichtenlänge (kurze Antworten = müde/busy)
    - Antwort-Geschwindigkeit (langsam = busy/away)
    - Stimmungs-Keywords (müde, gestresst, happy)
    - Tageszeit-Muster (nachts = müde)
    - Engagement-Level (wie viel schreibt User?)
    """

    # Keywords für verschiedene Zustände
    STATE_INDICATORS = {
        UserState.TIRED: {
            'keywords': ['müde', 'tired', 'erschöpft', 'kaputt', 'fertig', 'schlapp',
                        'gähn', 'pennen', 'schlafen', 'bett', 'todmüde', 'hundemüde',
                        'k.o.', 'ko', 'platt', 'am ende', 'keine energie',
                        # NEU: Mehr English + Variationen
                        'exhausted', 'drained', 'worn out', 'sleepy', 'drowsy',
                        'dead tired', 'knackered', 'wiped out', 'burned out'],
            'weight': 1.0
        },
        UserState.STRESSED: {
            'keywords': ['stress', 'gestresst', 'hektisch', 'viel zu tun', 'keine zeit',
                        'deadlines', 'druck', 'überfordert', 'zu viel', 'chaos',
                        'wahnsinn', 'kopf raucht', 'nerven', 'anstrengend',
                        # NEU: English
                        'overwhelmed', 'anxious', 'pressure', 'hectic'],
            'weight': 1.0
        },
        UserState.SAD: {
            'keywords': ['traurig', 'sad', 'down', 'schlecht drauf', 'mies', 'depri',
                        'niedergeschlagen', 'bedrückt', 'einsam', 'allein', 'weinen',
                        'heulen', 'schlimm', 'furchtbar', 'hoffnungslos',
                        # NEU: English
                        'depressed', 'upset', 'lonely', 'heartbroken', 'miserable'],
            'weight': 1.2  # Höher gewichtet - wichtig zu erkennen
        },
        UserState.HAPPY: {
            # GEÄNDERT: "super" entfernt (zu viele false positives wie "supermüde")
            'keywords': ['happy', 'glücklich', 'freude', 'toll', 'geil', 'nice',
                        'awesome', 'yay', 'juhu', 'freu', 'beste', 'perfekt', 'großartig',
                        'fantastisch', 'wunderbar', 'genial',
                        # NEU: English + mehr
                        'excited', 'thrilled', 'amazing', 'wonderful', 'great day'],
            'weight': 0.8
        },
        UserState.BUSY: {
            'keywords': ['busy', 'beschäftigt', 'arbeiten', 'meeting', 'termin', 'muss weg',
                        'kurz', 'gleich', 'später', 'keine zeit', 'bin dran', 'moment'],
            'weight': 0.9
        },
        UserState.ENERGETIC: {
            'keywords': ['energiegeladen', 'motiviert', 'pumped', 'ready', 'bereit',
                        'los gehts', "let's go", 'hyped', 'aufgeregt', 'gespannt',
                        # NEU: hellwach, wach, fit, energie
                        'hellwach', 'wach', 'fit', 'voller energie', 'power',
                        'energized', 'fired up', 'on fire', 'unstoppable'],
            'weight': 0.8
        },
    }

    # Empfohlene Reaktionen pro Zustand
    REACTION_MAP = {
        UserState.TIRED: HoloReaction.BE_CALM,
        UserState.STRESSED: HoloReaction.BE_SUPPORTIVE,
        UserState.SAD: HoloReaction.CHEER_UP,
        UserState.HAPPY: HoloReaction.MATCH_ENERGY,
        UserState.BUSY: HoloReaction.BE_BRIEF,
        UserState.ENERGETIC: HoloReaction.BE_ENERGETIC,
        UserState.AWAY: HoloReaction.LEAVE_ALONE,
        UserState.SLEEPING: HoloReaction.LEAVE_ALONE,
        UserState.NORMAL: HoloReaction.MATCH_ENERGY,
    }

    # Tone-Empfehlungen
    TONE_MAP = {
        UserState.TIRED: "sanft, ruhig, nicht zu viel Text",
        UserState.STRESSED: "beruhigend, unterstützend, verständnisvoll",
        UserState.SAD: "einfühlsam, tröstend, liebevoll",
        UserState.HAPPY: "fröhlich, enthusiastisch, verspielt",
        UserState.BUSY: "kurz, auf den Punkt, hilfreich",
        UserState.ENERGETIC: "energetisch, begeistert, aktiv",
        UserState.AWAY: "keine Nachricht senden",
        UserState.SLEEPING: "keine Nachricht senden",
        UserState.NORMAL: "natürlich, freundlich, ausgewogen",
    }

    def __init__(self):
        self.message_history: List[Dict] = []
        self.state_history: List[UserStateAnalysis] = []
        self.last_message_time: float = time.time()
        self.last_response_times: List[float] = []  # Sekunden zwischen Nachrichten
        self.current_state: UserState = UserState.NORMAL
        self.state_confidence: float = 0.5

    # Negations und Ausnahmen
    NEGATION_WORDS = ['nicht', 'kein', 'keine', 'keinen', 'nie', 'niemals', 'kaum', 'wenig', 'ohne']
    QUESTION_ABOUT_AI = ['bist du', 'hast du', 'fühlst du', 'geht es dir', 'und du', 'wie geht\'s dir']
    PAST_INDICATORS = ['gestern', 'vorhin', 'letzte', 'letzten', 'früher', 'war ich', 'hatte ich', 'ging es mir']
    THIRD_PERSON = ['er ist', 'sie ist', 'er hat', 'sie hat', 'mein freund', 'meine freundin', 'kollege', 'chef']

    # NEU: Hypothetische/Konditionale Phrasen
    HYPOTHETICAL_INDICATORS = ['wenn ich', 'falls ich', 'wäre ich', 'würde ich', 'hätte ich',
                               'angenommen', 'stell dir vor', 'theoretisch', 'könnte sein']

    # NEU: Selbst-Fragen (User fragt sich selbst)
    SELF_QUESTION_INDICATORS = ['bin ich', 'war ich', 'werde ich', 'sollte ich', 'muss ich']

    # NEU: Zitate/Erzählung
    QUOTE_INDICATORS = ['sagte', 'meinte', 'hat gesagt', 'erzählt', 'schrieb', 'geschrieben']

    # NEU: Sarkasmus-Indikatoren (spezifischer - nur mit Kontext!)
    # GEÄNDERT: "total" entfernt (zu viele false positives wie "total erschöpft")
    SARCASM_INDICATORS = ['ja klar', 'na klar', 'ach ja', 'genau...', 'super...',
                          'toll...', '...nicht', 'wow...', 'great...', 'amazing...',
                          'oh wie toll', 'na super', 'ja genau', 'ach wirklich']

    # NEU: Emoji-Mapping zu Zuständen
    EMOJI_STATE_MAP = {
        # Tired
        '😴': UserState.TIRED, '🥱': UserState.TIRED, '😪': UserState.TIRED,
        '💤': UserState.TIRED, '🛌': UserState.TIRED,
        # Sad
        '😢': UserState.SAD, '😭': UserState.SAD, '😞': UserState.SAD,
        '😔': UserState.SAD, '🥺': UserState.SAD, '💔': UserState.SAD,
        # Stressed
        '😰': UserState.STRESSED, '😫': UserState.STRESSED, '🤯': UserState.STRESSED,
        '😤': UserState.STRESSED, '😩': UserState.STRESSED,
        # Happy
        '😊': UserState.HAPPY, '😄': UserState.HAPPY, '🥳': UserState.HAPPY,
        '🎉': UserState.HAPPY, '😁': UserState.HAPPY, '❤️': UserState.HAPPY,
        '💕': UserState.HAPPY, '🥰': UserState.HAPPY, '😍': UserState.HAPPY,
        # Energetic
        '🔥': UserState.ENERGETIC, '💪': UserState.ENERGETIC, '⚡': UserState.ENERGETIC,
        '🚀': UserState.ENERGETIC, '✨': UserState.ENERGETIC,
    }

    def _normalize_stretched_text(self, text: str) -> str:
        """
        Normalisiert gestreckte Vokale/Buchstaben.

        "müüüde" → "müde"
        "soooo" → "so"
        "haaappy" → "happy"
        """
        import re
        # Ersetze 3+ gleiche Zeichen durch 1
        normalized = re.sub(r'(.)\1{2,}', r'\1', text)
        return normalized

    def _check_negation(self, text: str, keyword: str) -> bool:
        """
        Prüft ob ein Keyword negiert wird.

        "ich bin nicht müde" → True (negiert)
        "ich bin müde" → False (nicht negiert)
        "nicht nicht müde" → False (doppelte Negation = positiv)
        """
        # Finde Position des Keywords
        pos = text.find(keyword)
        if pos == -1:
            return False

        # Prüfe die 30 Zeichen vor dem Keyword auf Negation
        before_text = text[max(0, pos-30):pos]
        negation_count = 0
        for neg in self.NEGATION_WORDS:
            negation_count += before_text.count(neg)

        # Doppelte Negation = nicht negiert
        return negation_count % 2 == 1

    def _is_hypothetical(self, text: str) -> bool:
        """
        Prüft ob der Text hypothetisch/konditional ist.

        "wenn ich müde wäre" → True
        "ich bin müde" → False
        """
        text_lower = text.lower()
        for phrase in self.HYPOTHETICAL_INDICATORS:
            if phrase in text_lower:
                return True
        return False

    def _is_self_question(self, text: str, keyword: str) -> bool:
        """
        Prüft ob User sich selbst etwas fragt (rhetorical).

        "bin ich müde?" → True
        "ich bin müde" → False
        """
        text_lower = text.lower()

        # Hat der Text ein Fragezeichen?
        if '?' not in text:
            return False

        # Prüft ob eine Selbst-Frage vor dem Keyword steht
        for phrase in self.SELF_QUESTION_INDICATORS:
            if phrase in text_lower:
                # Phrase muss VOR dem Keyword sein
                phrase_pos = text_lower.find(phrase)
                keyword_pos = text_lower.find(keyword)
                if phrase_pos < keyword_pos:
                    return True
        return False

    def _is_quote_or_narration(self, text: str) -> bool:
        """
        Prüft ob der Text ein Zitat oder Erzählung ist.

        "er sagte ich bin müde" → True
        "ich bin müde" → False
        """
        text_lower = text.lower()
        for phrase in self.QUOTE_INDICATORS:
            if phrase in text_lower:
                return True
        return False

    def _has_sarcasm_indicators(self, text: str) -> bool:
        """
        Prüft auf Sarkasmus-Indikatoren.

        "ja klar bin ich total happy..." → True
        "ich bin happy" → False
        """
        text_lower = text.lower()
        for indicator in self.SARCASM_INDICATORS:
            if indicator in text_lower:
                return True
        # Viele Punkte am Ende oft sarkastisch
        if text.strip().endswith('...') or text.strip().endswith('..'):
            return True
        return False

    def _detect_emojis(self, text: str) -> Dict[UserState, float]:
        """
        Erkennt Emojis und mappt sie zu Zuständen.

        Returns dict mit State → Score
        """
        emoji_states = {}
        for emoji, state in self.EMOJI_STATE_MAP.items():
            count = text.count(emoji)
            if count > 0:
                # Mehr Emojis = stärkeres Signal
                emoji_states[state] = emoji_states.get(state, 0) + (0.5 * count)
        return emoji_states

    def _is_about_user(self, text: str) -> bool:
        """
        Prüft ob der Text wirklich über den User spricht.

        "bist du müde?" → False (fragt nach AI)
        "ich bin müde" → True (über User)
        """
        text_lower = text.lower()

        # Frage über AI?
        for phrase in self.QUESTION_ABOUT_AI:
            if phrase in text_lower:
                return False

        # Vergangenheit?
        for phrase in self.PAST_INDICATORS:
            if phrase in text_lower:
                return False  # Reduziere Gewicht, aber nicht komplett ignorieren

        # Dritte Person?
        for phrase in self.THIRD_PERSON:
            if phrase in text_lower:
                return False

        return True

    def _get_context_modifier(self, text: str) -> float:
        """
        Gibt einen Modifier basierend auf Kontext zurück.

        1.0 = definitiv über User (ich bin, mir geht's)
        0.5 = unklar
        0.0 = definitiv nicht über User
        """
        text_lower = text.lower()

        # NEU: Hypothetisch → nicht real
        if self._is_hypothetical(text_lower):
            return 0.1

        # NEU: Zitat/Erzählung → nicht über User
        if self._is_quote_or_narration(text_lower):
            return 0.1

        # Starke Indikatoren für User
        user_indicators = ['ich bin', 'mir geht', 'ich fühl', 'ich hab', 'mich', 'mir ist', 'bei mir']
        for phrase in user_indicators:
            if phrase in text_lower:
                # NEU: Aber nicht wenn es eine Selbst-Frage ist
                # "bin ich müde?" vs "ich bin müde"
                if '?' in text and any(sq in text_lower for sq in self.SELF_QUESTION_INDICATORS):
                    return 0.3  # Unsicher, könnte rhetorisch sein
                return 1.0

        # Frage über AI
        for phrase in self.QUESTION_ABOUT_AI:
            if phrase in text_lower:
                return 0.0

        # Vergangenheit - reduzierter Wert
        for phrase in self.PAST_INDICATORS:
            if phrase in text_lower:
                return 0.3

        # Dritte Person
        for phrase in self.THIRD_PERSON:
            if phrase in text_lower:
                return 0.0

        return 0.7  # Default: wahrscheinlich über User

    def analyze_message(self, message: str, response_time_seconds: float = None) -> UserStateAnalysis:
        """
        Analysiert eine User-Nachricht und gibt Zustandsanalyse zurück.

        Args:
            message: Die User-Nachricht
            response_time_seconds: Zeit seit letzter Interaktion (optional)

        Returns:
            UserStateAnalysis mit Empfehlungen
        """
        now = time.time()
        msg_lower = message.lower().strip()
        # NEU: Normalisiere gestreckte Buchstaben (müüüde → müde)
        msg_normalized = self._normalize_stretched_text(msg_lower)

        # Response-Zeit tracken
        if response_time_seconds:
            self.last_response_times.append(response_time_seconds)
            self.last_response_times = self.last_response_times[-20:]

        # === KONTEXT-CHECK: Ist es überhaupt über den User? ===
        context_modifier = self._get_context_modifier(msg_lower)

        # === FAKTOR 1: Keyword-Analyse (mit Negations-Check!) ===
        detected_states = {}
        for state, data in self.STATE_INDICATORS.items():
            score = 0
            for keyword in data['keywords']:
                # Prüfe sowohl original als auch normalisiert
                if keyword in msg_lower or keyword in msg_normalized:
                    # Negations-Check!
                    if self._check_negation(msg_lower, keyword):
                        # Negiert = Gegenteil könnte wahr sein
                        # "nicht müde" → eher energetisch
                        if state == UserState.TIRED:
                            detected_states[UserState.ENERGETIC] = detected_states.get(UserState.ENERGETIC, 0) + 0.3
                        elif state == UserState.SAD:
                            detected_states[UserState.HAPPY] = detected_states.get(UserState.HAPPY, 0) + 0.3
                        elif state == UserState.STRESSED:
                            detected_states[UserState.NORMAL] = detected_states.get(UserState.NORMAL, 0) + 0.3
                        continue  # Überspringe das negierte Keyword

                    # Nicht negiert - normales Scoring mit Kontext-Modifier
                    score += data['weight'] * context_modifier

            if score > 0:
                detected_states[state] = score

        # === FAKTOR 2: Nachrichtenlänge ===
        msg_length = len(message)
        length_factor = {
            'very_short': msg_length < 10,      # "ok", "ja", "mhm"
            'short': msg_length < 30,           # Kurze Antwort
            'medium': msg_length < 100,         # Normal
            'long': msg_length >= 100,          # Ausführlich
        }

        # Kurze Nachrichten → wahrscheinlich müde/busy
        if length_factor['very_short']:
            detected_states[UserState.TIRED] = detected_states.get(UserState.TIRED, 0) + 0.3
            detected_states[UserState.BUSY] = detected_states.get(UserState.BUSY, 0) + 0.3
        elif length_factor['long']:
            detected_states[UserState.ENERGETIC] = detected_states.get(UserState.ENERGETIC, 0) + 0.3

        # === FAKTOR 3: Tageszeit ===
        hour = datetime.now().hour
        if 23 <= hour or hour < 6:
            detected_states[UserState.TIRED] = detected_states.get(UserState.TIRED, 0) + 0.5
        elif 6 <= hour < 9:
            # Morgens - könnte müde sein
            detected_states[UserState.TIRED] = detected_states.get(UserState.TIRED, 0) + 0.2

        # === FAKTOR 4: Response-Zeit Pattern ===
        if self.last_response_times:
            avg_response = sum(self.last_response_times[-5:]) / len(self.last_response_times[-5:])
            if avg_response > 600:  # >10 min durchschnittlich
                detected_states[UserState.BUSY] = detected_states.get(UserState.BUSY, 0) + 0.4
            elif avg_response > 1800:  # >30 min
                detected_states[UserState.AWAY] = detected_states.get(UserState.AWAY, 0) + 0.6

        # === FAKTOR 5: Emoji-Erkennung (NEU!) ===
        emoji_states = self._detect_emojis(message)
        for state, score in emoji_states.items():
            detected_states[state] = detected_states.get(state, 0) + score

        # === FAKTOR 6: Sarkasmus-Check (NEU!) ===
        is_sarcastic = self._has_sarcasm_indicators(message)
        if is_sarcastic:
            # Bei Sarkasmus: Positive Keywords weniger vertrauen
            # "ja klar bin ich total happy..." → wahrscheinlich NICHT happy
            if UserState.HAPPY in detected_states:
                detected_states[UserState.HAPPY] *= 0.3
            if UserState.ENERGETIC in detected_states:
                detected_states[UserState.ENERGETIC] *= 0.5
            # Könnte eher gestresst oder genervt sein
            detected_states[UserState.STRESSED] = detected_states.get(UserState.STRESSED, 0) + 0.3

        # === FAKTOR 7: Mixed Signals Handling (NEU!) ===
        # Wenn sowohl positiv als auch negativ erkannt, reduziere Confidence
        positive_states = {UserState.HAPPY, UserState.ENERGETIC}
        negative_states = {UserState.TIRED, UserState.SAD, UserState.STRESSED}
        has_positive = any(s in detected_states for s in positive_states)
        has_negative = any(s in detected_states for s in negative_states)
        mixed_signals = has_positive and has_negative

        # === ENTSCHEIDUNG ===
        if detected_states:
            best_state = max(detected_states, key=detected_states.get)
            confidence = min(1.0, detected_states[best_state] / 2)
            # Mixed signals = weniger Confidence
            if mixed_signals:
                confidence *= 0.6
            # Sarkasmus = weniger Confidence
            if is_sarcastic:
                confidence *= 0.7
        else:
            best_state = UserState.NORMAL
            confidence = 0.5

        # Energy Level berechnen
        energy_level = 0.5
        if best_state == UserState.TIRED:
            energy_level = 0.2
        elif best_state == UserState.STRESSED:
            energy_level = 0.4
        elif best_state == UserState.ENERGETIC:
            energy_level = 0.9
        elif best_state == UserState.HAPPY:
            energy_level = 0.8
        elif best_state == UserState.SAD:
            energy_level = 0.3

        # Engagement Level
        engagement = 0.5
        if length_factor['very_short']:
            engagement = 0.2
        elif length_factor['short']:
            engagement = 0.4
        elif length_factor['long']:
            engagement = 0.9

        # Emotional Valence
        valence = 0.0
        if best_state == UserState.HAPPY:
            valence = 0.8
        elif best_state == UserState.ENERGETIC:
            valence = 0.6
        elif best_state == UserState.SAD:
            valence = -0.7
        elif best_state == UserState.STRESSED:
            valence = -0.4
        elif best_state == UserState.TIRED:
            valence = -0.2

        # Reaktion bestimmen
        reaction = self.REACTION_MAP.get(best_state, HoloReaction.MATCH_ENERGY)
        tone = self.TONE_MAP.get(best_state, "natürlich, freundlich")

        # Soll Holo weniger schreiben?
        reduce_messages = best_state in [UserState.TIRED, UserState.BUSY, UserState.AWAY,
                                          UserState.SLEEPING, UserState.STRESSED]

        # Reasoning
        reasons = []
        if detected_states:
            for state, score in sorted(detected_states.items(), key=lambda x: -x[1])[:2]:
                reasons.append(f"{state.value}: {score:.1f}")
        if length_factor['very_short']:
            reasons.append("sehr kurze Nachricht")
        if hour >= 23 or hour < 6:
            reasons.append("späte Stunde")
        # NEU: Zusätzliche Reasoning-Infos
        if emoji_states:
            reasons.append(f"Emojis erkannt")
        if is_sarcastic:
            reasons.append("⚠️ möglicherweise sarkastisch")
        if mixed_signals:
            reasons.append("⚠️ widersprüchliche Signale")

        analysis = UserStateAnalysis(
            state=best_state,
            confidence=confidence,
            energy_level=energy_level,
            engagement_level=engagement,
            emotional_valence=valence,
            recommended_reaction=reaction,
            reasoning=", ".join(reasons) if reasons else "normale Interaktion",
            should_reduce_messages=reduce_messages,
            suggested_tone=tone
        )

        # State speichern
        self.current_state = best_state
        self.state_confidence = confidence
        self.state_history.append(analysis)
        self.state_history = self.state_history[-50:]
        self.message_history.append({
            'message': message[:100],
            'state': best_state.value,
            'timestamp': now
        })
        self.message_history = self.message_history[-30:]
        self.last_message_time = now

        return analysis

    def get_current_state(self) -> UserStateAnalysis:
        """Gibt aktuelle State-Analyse zurück"""
        if self.state_history:
            return self.state_history[-1]
        return UserStateAnalysis(
            state=UserState.NORMAL,
            confidence=0.3,
            energy_level=0.5,
            engagement_level=0.5,
            emotional_valence=0.0,
            recommended_reaction=HoloReaction.MATCH_ENERGY,
            reasoning="keine Daten",
            should_reduce_messages=False,
            suggested_tone="natürlich, freundlich"
        )

    def get_state_trend(self, last_n: int = 5) -> Dict:
        """Analysiert Trend über letzte N Nachrichten"""
        if len(self.state_history) < 2:
            return {"trend": "unknown", "dominant_state": "normal"}

        recent = self.state_history[-last_n:]
        state_counts = {}
        for analysis in recent:
            state_counts[analysis.state] = state_counts.get(analysis.state, 0) + 1

        dominant = max(state_counts, key=state_counts.get)
        avg_energy = sum(a.energy_level for a in recent) / len(recent)
        avg_engagement = sum(a.engagement_level for a in recent) / len(recent)

        # Trend bestimmen
        if len(recent) >= 3:
            first_half_energy = sum(a.energy_level for a in recent[:len(recent)//2]) / (len(recent)//2)
            second_half_energy = sum(a.energy_level for a in recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
            if second_half_energy < first_half_energy - 0.1:
                trend = "declining"  # User wird müder
            elif second_half_energy > first_half_energy + 0.1:
                trend = "improving"  # User wird wacher
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return {
            "trend": trend,
            "dominant_state": dominant.value,
            "avg_energy": avg_energy,
            "avg_engagement": avg_engagement,
            "recommendation": self.REACTION_MAP.get(dominant, HoloReaction.MATCH_ENERGY).value,
        }

    def should_holo_be_proactive(self) -> Tuple[bool, str]:
        """
        Prüft ob Holo proaktiv sein sollte basierend auf User-Zustand.

        Returns:
            (should_be_proactive, reason)
        """
        state = self.get_current_state()

        if state.state == UserState.SLEEPING:
            return False, "User schläft wahrscheinlich"

        if state.state == UserState.AWAY:
            return False, "User ist nicht da"

        if state.state == UserState.TIRED and state.confidence > 0.6:
            return False, "User ist müde - in Ruhe lassen"

        if state.state == UserState.BUSY and state.confidence > 0.5:
            return False, "User ist beschäftigt"

        if state.state == UserState.STRESSED:
            # Bei Stress: Nur supportive Messages
            return True, "User ist gestresst - nur unterstützende Nachrichten"

        if state.state == UserState.SAD:
            # Bei Traurigkeit: Aufmuntern!
            return True, "User ist traurig - aufmuntern"

        return True, "normale Interaktion"

    def get_proactive_urgency_modifier(self) -> float:
        """
        Gibt einen Modifier für proaktive Urgency zurück.

        -1.0 = nicht proaktiv sein
        0.0 = normal
        +0.5 = mehr proaktiv (z.B. bei Traurigkeit aufmuntern)
        """
        state = self.get_current_state()

        modifiers = {
            UserState.SLEEPING: -1.0,
            UserState.AWAY: -0.8,
            UserState.TIRED: -0.5,
            UserState.BUSY: -0.4,
            UserState.STRESSED: -0.2,  # Weniger, aber supportive
            UserState.SAD: 0.3,        # Mehr! Aufmuntern
            UserState.NORMAL: 0.0,
            UserState.HAPPY: 0.1,
            UserState.ENERGETIC: 0.2,
        }

        base_modifier = modifiers.get(state.state, 0.0)

        # Confidence gewichten
        return base_modifier * state.confidence


# =============================================================================
# EMOTIONAL MEMORY STORE (erweitert)
# =============================================================================

class EmotionalMemoryStore:
    """
    Speichert emotionale Erinnerungen - Wrapper um HoloDatabaseManager.emotions.
    """

    def __init__(self, db_path: Path = None, db: 'HoloDatabaseManager' = None):
        """
        Args:
            db_path: DEPRECATED - wird ignoriert
            db: HoloDatabaseManager Instanz
        """
        self.db = db
        self._cache: List[EmotionalMemory] = []

        if db:
            logger.info("[EmotionalMemoryStore] 💾 Mit HoloDatabaseManager initialisiert")
        else:
            logger.warning("[EmotionalMemoryStore] ⚠️ Keine Database - eingeschränkt")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet Database nachträglich"""
        self.db = db
        logger.info("[EmotionalMemoryStore] 💾 Database verbunden")

    def add_memory(self, trigger: str, emotion: str, intensity: float,
                   valence: float, context: str = "",
                   related_topics: List[str] = None,
                   user_involved: bool = True) -> EmotionalMemory:
        """Fügt emotionale Erinnerung hinzu"""
        memory = EmotionalMemory(
            id=f"emo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}",
            timestamp=datetime.now().isoformat(),
            trigger=trigger[:300],
            emotion=emotion,
            intensity=min(1.0, max(0.0, intensity)),
            valence=min(1.0, max(-1.0, valence)),
            context=context[:300],
            lasting_impact=intensity * 0.8,
            related_topics=related_topics or [],
            user_involved=user_involved,
        )

        # Cache aktualisieren
        self._cache.append(memory)
        if len(self._cache) > LearningConfig.MAX_EMOTIONAL_MEMORIES:
            self._cache.sort(key=lambda m: m.lasting_impact, reverse=True)
            self._cache = self._cache[:LearningConfig.MAX_EMOTIONAL_MEMORIES]

        # In DB speichern
        if self.db:
            try:
                self.db.emotions.log_emotion(
                    emotion=emotion,
                    intensity=intensity,
                    valence=valence,
                    trigger=trigger,
                    context=context,
                )
            except Exception as e:
                logger.debug(f"Emotion DB: {e}")

        return memory

    def find_similar(self, trigger: str, emotion: str = None) -> List[EmotionalMemory]:
        """Findet ähnliche Erinnerungen"""
        trigger_words = set(trigger.lower().split())
        results = []

        for mem in self._cache:
            if emotion and mem.emotion != emotion:
                continue
            mem_words = set(mem.trigger.lower().split())
            common = len(trigger_words & mem_words)
            if common >= 2:
                results.append((mem, common))

        results.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in results[:5]]

    def find_by_emotion(self, emotion: str, limit: int = 10) -> List[EmotionalMemory]:
        """Findet Erinnerungen einer Emotion"""
        matching = [m for m in self._cache if m.emotion == emotion]
        matching.sort(key=lambda m: m.lasting_impact, reverse=True)
        return matching[:limit]

    def get_strongest(self, limit: int = 10) -> List[EmotionalMemory]:
        """Gibt stärkste Erinnerungen zurück"""
        return sorted(self._cache, key=lambda m: m.lasting_impact, reverse=True)[:limit]

    def get_recent(self, limit: int = 10) -> List[EmotionalMemory]:
        """Gibt neueste Erinnerungen zurück"""
        return sorted(self._cache, key=lambda m: m.timestamp, reverse=True)[:limit]

    def decay_memories(self):
        """Lässt Erinnerungen mit der Zeit verblassen"""
        now = datetime.now()
        for mem in self._cache:
            try:
                mem_time = datetime.fromisoformat(mem.timestamp)
                days_old = (now - mem_time).days
                decay = 0.005 * days_old
                mem.lasting_impact = max(0.1, mem.lasting_impact - decay)
            except Exception:
                pass

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        emotion_counts = Counter(m.emotion for m in self._cache)
        avg_intensity = sum(m.intensity for m in self._cache) / len(self._cache) if self._cache else 0
        avg_valence = sum(m.valence for m in self._cache) / len(self._cache) if self._cache else 0

        return {
            "total": len(self._cache),
            "by_emotion": dict(emotion_counts),
            "avg_intensity": avg_intensity,
            "avg_valence": avg_valence,
            "db_connected": self.db is not None,
        }


# =============================================================================
# LEARNING SCHEDULER
# =============================================================================

class LearningScheduler:
    """
    Plant und steuert autonomes Lernen.
    """

    def __init__(self, learning_callback: Callable = None):
        self.learning_callback = learning_callback
        self.schedule: Dict[str, float] = {}  # category -> next_learn_time
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    def should_learn_now(self, category: str = None) -> Tuple[bool, str]:
        """Prüft ob jetzt gelernt werden soll"""
        now = datetime.now()
        current_time = time.time()

        # Nacht-Modus (tiefes Lernen)
        hour = now.hour
        is_night = LearningConfig.DEEP_RESEARCH_HOURS[0] <= hour < LearningConfig.DEEP_RESEARCH_HOURS[1]

        if category:
            # Spezifische Kategorie
            last_learn = self.schedule.get(category, 0)
            interval = LearningConfig.LEARNING_INTERVAL_MINUTES * 60

            if is_night:
                interval *= 0.5  # Schneller lernen nachts

            if current_time - last_learn >= interval:
                return True, "interval_reached"
            return False, "too_soon"

        # Allgemein: Irgendeine Kategorie fällig?
        for cat, last in self.schedule.items():
            interval = LearningConfig.LEARNING_INTERVAL_MINUTES * 60
            if current_time - last >= interval:
                return True, f"category_{cat}_due"

        # Noch nie gelernt?
        if not self.schedule:
            return True, "first_time"

        return False, "all_up_to_date"

    def mark_learned(self, category: str):
        """Markiert Kategorie als gelernt"""
        self.schedule[category] = time.time()

    def get_next_category(self) -> Optional[str]:
        """Gibt die nächste zu lernende Kategorie zurück"""
        if not self.schedule:
            # Erste Kategorie nach Interesse
            return max(LearningConfig.INTERESTS.items(), key=lambda x: x[1])[0]

        # Älteste Kategorie
        current = time.time()
        oldest_cat = None
        oldest_time = current

        for cat in LearningConfig.INTERESTS.keys():
            last = self.schedule.get(cat, 0)
            if last < oldest_time:
                oldest_time = last
                oldest_cat = cat

        return oldest_cat

    def get_schedule_info(self) -> Dict:
        """Gibt Schedule-Informationen zurück"""
        current = time.time()

        schedule_info = {}
        for cat in LearningConfig.INTERESTS.keys():
            last = self.schedule.get(cat, 0)
            next_due = last + (LearningConfig.LEARNING_INTERVAL_MINUTES * 60)

            schedule_info[cat] = {
                "last_learned": datetime.fromtimestamp(last).isoformat() if last else "never",
                "next_due": datetime.fromtimestamp(next_due).isoformat() if last else "now",
                "is_due": current >= next_due,
                "interest": LearningConfig.INTERESTS.get(cat, 0.5),
            }

        return schedule_info


# =============================================================================
# REAL LEARNING ENGINE (Haupt-Orchestrator)
# =============================================================================

class RealLearningEngine:
    """
    Das echte Lernsystem - orchestriert alles.
    Nutzt HoloDatabaseManager für zentrale Datenspeicherung.
    """

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.data_dir = data_dir or LearningConfig.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = db

        # Komponenten - alle mit DB verbunden
        self.knowledge = LearningKnowledgeDB(db=db)
        self.extractor = FactExtractor()
        self.fetcher = NewsFetcher()
        self.topic_tracker = LearningTopicTracker(db=db)
        self.scheduler = LearningScheduler()

        # Session-Tracking
        self.sessions: List[LearningSession] = []
        self.current_session: Optional[LearningSession] = None

        # Person Opinion Integration
        self.person_trigger = None
        if PERSON_OPINIONS_AVAILABLE:
            try:
                self.person_trigger = PersonInfoTrigger(get_person_opinion_manager())
                logger.info("🧠 PersonInfoTrigger aktiviert - Meinungen werden aus News gebildet")
            except Exception as e:
                logger.warning(f"PersonInfoTrigger konnte nicht initialisiert werden: {e}")

        logger.info(f"🧠 RealLearningEngine initialisiert (DB: {db is not None})")

    def learn(self, category: str = None, max_articles: int = 15) -> Dict:
        """
        Haupt-Lernfunktion - liest News und extrahiert Wissen.
        """
        session = LearningSession(
            session_id=f"learn_{int(time.time())}",
            started_at=datetime.now().isoformat(),
            category=category or "all",
        )
        self.current_session = session

        start_time = time.time()
        facts_learned = 0
        facts_updated = 0
        new_topics = set()
        errors = []

        try:
            # Kategorien bestimmen
            if category:
                categories = [(category, LearningConfig.INTERESTS.get(category, 0.5))]
            else:
                # Nach Interesse sortieren
                categories = sorted(
                    LearningConfig.INTERESTS.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]  # Top 5

            # News holen und lernen
            for cat, interest in categories:
                if cat not in LearningConfig.NEWS_FEEDS:
                    continue

                try:
                    articles = self.fetcher.fetch_category(cat, max_articles=int(max_articles * interest))
                    cat_enum = self._to_category(cat)

                    for article in articles:
                        session.articles_read += 1

                        # Text zusammenbauen
                        text = f"{article['title']}. {article['summary']}"

                        # Fakten extrahieren
                        extracted = self.extractor.extract_facts(
                            text=text,
                            title=article['title'],
                            category=cat_enum,
                            max_facts=LearningConfig.FACTS_PER_ARTICLE,
                        )

                        # Fakten speichern
                        for fact_data in extracted:
                            topic = fact_data.get("topic", self._detect_topic(fact_data["content"]))

                            fact = LearnedFact(
                                fact_id="",
                                content=fact_data["content"],
                                category=cat_enum,
                                topic=topic,
                                keywords=fact_data["keywords"],
                                source_title=article["title"],
                                source_url=article["link"],
                                source_feed=article["source"],
                                importance=fact_data["importance"] * interest,
                                tags=fact_data.get("entities", []),
                            )

                            is_new, status = self.knowledge.add_fact(fact)

                            if is_new:
                                facts_learned += 1
                                new_topics.add(topic)
                                # Topic tracken
                                self.topic_tracker.track_topic(topic, cat, from_learning=True)
                            elif status == "updated":
                                facts_updated += 1

                        # Person Opinion Trigger - analysiert Artikel auf Personen
                        if self.person_trigger:
                            try:
                                person_results = self.person_trigger.process_text(
                                    text, source=f"news:{cat}"
                                )
                                if person_results:
                                    session.person_opinions_updated = getattr(
                                        session, 'person_opinions_updated', 0
                                    ) + len(person_results)
                            except Exception as e:
                                logger.debug(f"Person-Trigger Fehler: {e}")

                    # Scheduler aktualisieren
                    self.scheduler.mark_learned(cat)

                except Exception as e:
                    errors.append(f"{cat}: {str(e)}")
                    logger.warning(f"Fehler beim Lernen von {cat}: {e}")

        except Exception as e:
            session.success = False
            session.error_message = str(e)
            errors.append(str(e))

        # Session abschließen
        session.facts_learned = facts_learned
        session.facts_updated = facts_updated
        session.new_topics = list(new_topics)
        session.duration_seconds = time.time() - start_time
        session.finished_at = datetime.now().isoformat()
        session.success = len(errors) == 0

        self.sessions.append(session)
        self.current_session = None

        logger.info(f"📚 Lernsession: {facts_learned} neu, {facts_updated} aktualisiert, "
                   f"{session.articles_read} Artikel in {session.duration_seconds:.1f}s")

        return {
            "success": session.success,
            "facts_learned": facts_learned,
            "facts_updated": facts_updated,
            "articles_read": session.articles_read,
            "new_topics": list(new_topics),
            "person_opinions_updated": getattr(session, 'person_opinions_updated', 0),
            "duration_seconds": session.duration_seconds,
            "errors": errors,
        }

    def learn_topic(self, topic: str) -> Dict:
        """Lernt gezielt über ein spezifisches Thema"""
        # Existierendes Wissen prüfen
        existing = self.knowledge.search(topic, limit=20)

        # In allen Kategorien nach dem Topic suchen
        results = {
            "topic": topic,
            "existing_facts": len(existing),
            "new_facts": 0,
            "sources_checked": [],
        }

        # Relevante Kategorien finden
        topic_lower = topic.lower()
        relevant_cats = []

        for cat, keywords in FactExtractor.CATEGORY_KEYWORDS.items():
            if any(kw in topic_lower for kw in keywords):
                cat_name = cat.value
                if cat_name in LearningConfig.NEWS_FEEDS:
                    relevant_cats.append(cat_name)

        # Wenn keine spezifische Kategorie, alle durchsuchen
        if not relevant_cats:
            relevant_cats = list(LearningConfig.NEWS_FEEDS.keys())[:3]

        # News holen und nach Topic filtern
        for cat in relevant_cats:
            articles = self.fetcher.fetch_category(cat, max_articles=10)
            results["sources_checked"].append(cat)

            for article in articles:
                # Prüfen ob Topic erwähnt wird
                text = f"{article['title']} {article['summary']}".lower()
                if topic_lower not in text:
                    continue

                # Fakten extrahieren
                cat_enum = self._to_category(cat)
                extracted = self.extractor.extract_facts(
                    text=f"{article['title']}. {article['summary']}",
                    title=article['title'],
                    category=cat_enum,
                )

                for fact_data in extracted:
                    fact = LearnedFact(
                        fact_id="",
                        content=fact_data["content"],
                        category=cat_enum,
                        topic=topic,
                        keywords=fact_data["keywords"] + [topic_lower],
                        source_title=article["title"],
                        source_url=article["link"],
                        source_feed=article["source"],
                        importance=fact_data["importance"] + 0.1,
                    )

                    is_new, _ = self.knowledge.add_fact(fact)
                    if is_new:
                        results["new_facts"] += 1

        # Topic tracken
        self.topic_tracker.track_topic(topic, "recherche", from_learning=True)

        return results

    def what_do_i_know(self, query: str, category: str = None) -> Dict:
        """Beantwortet 'Was weißt du über X?'"""
        cat_enum = self._to_category(category) if category else None
        facts = self.knowledge.search(query, category=cat_enum, limit=15)

        if not facts:
            return {
                "found": False,
                "query": query,
                "facts_count": 0,
                "message": f"Über '{query}' weiß ich noch nichts.",
                "facts": [],
                "suggestion": f"Soll ich nach '{query}' recherchieren?",
            }

        # Nach Kategorie gruppieren
        by_category = defaultdict(list)
        for f in facts:
            by_category[f.category.value].append(f)

        return {
            "found": True,
            "query": query,
            "facts_count": len(facts),
            "facts": facts,
            "by_category": dict(by_category),
            "sources": list(set(f.source_feed for f in facts)),
            "topics": list(set(f.topic for f in facts)),
        }

    def express_knowledge(self, query: str) -> str:
        """Drückt Wissen natürlich aus (für Chat)"""
        result = self.what_do_i_know(query)

        if not result["found"]:
            responses = [
                f"*legt Kopf schief* Hmm, über '{query}' weiß ich noch nichts. Soll ich mal nachschauen?",
                f"*Ohren zucken* '{query}'? Da muss ich passen... Soll ich recherchieren?",
                f"*kratzt sich am Ohr* Darüber hab ich noch nichts gelesen. Interesse?",
            ]
            return random.choice(responses)

        facts = result["facts"]

        # Ein Fakt
        if len(facts) == 1:
            intros = [
                "*Ohren spitzen sich* Ich hab da was gehört:",
                "*nickt wissend* Dazu weiß ich:",
                "*Schweif wedelt* Oh ja, darüber hab ich gelesen:",
            ]
            return f"{random.choice(intros)} {facts[0].content}"

        # Mehrere Fakten
        intros = [
            f"*wedelt* Über {query} weiß ich einiges!",
            f"*Ohren stellen sich auf* Oh, {query}! Da hab ich was!",
            f"*setzt sich aufrecht hin* {query}? Lass mich erzählen!",
        ]
        response = f"{random.choice(intros)}\n\n"

        for fact in facts[:4]:
            response += f"• {fact.content}\n"

        if len(facts) > 4:
            response += f"\n...und noch {len(facts) - 4} weitere Dinge! 📚"

        return response

    def express_recent_learning(self) -> str:
        """Erzählt was Holo kürzlich gelernt hat"""
        recent = self.knowledge.get_recent(limit=8)

        if not recent:
            return "*gähnt* Ich hab heute noch nichts gelesen..."

        # Nach Kategorie gruppieren
        by_cat = defaultdict(list)
        for fact in recent:
            by_cat[fact.category.value].append(fact)

        cat_emoji = {
            "anime": "🎌",
            "manga": "📖",
            "gaming": "🎮",
            "technik": "💻",
            "serien": "🎬",
            "filme": "🎥",
            "musik": "🎵",
            "wissenschaft": "🔬",
            "welt": "📰",
        }

        intros = [
            "*Schweif wedelt aufgeregt* Ich hab gerade einiges gelernt!",
            "*streckt sich* Uff, viel zu lesen heute! Hier die Highlights:",
            "*Ohren zucken begeistert* Oh oh oh, ich muss dir was erzählen!",
        ]
        response = f"{random.choice(intros)}\n\n"

        for cat, facts in by_cat.items():
            emoji = cat_emoji.get(cat, "📌")
            name = cat.title()
            response += f"**{emoji} {name}:**\n"
            for fact in facts[:2]:
                short = fact.content[:100] + "..." if len(fact.content) > 100 else fact.content
                response += f"• {short}\n"
            response += "\n"

        return response

    def _to_category(self, cat: str) -> FactCategory:
        """Konvertiert String zu FactCategory"""
        mapping = {
            "anime": FactCategory.ANIME,
            "manga": FactCategory.MANGA,
            "gaming": FactCategory.GAMING,
            "games": FactCategory.GAMING,
            "technik": FactCategory.TECH,
            "tech": FactCategory.TECH,
            "serien": FactCategory.ENTERTAINMENT,
            "entertainment": FactCategory.ENTERTAINMENT,
            "filme": FactCategory.MOVIES,
            "movies": FactCategory.MOVIES,
            "musik": FactCategory.MUSIC,
            "music": FactCategory.MUSIC,
            "wissenschaft": FactCategory.SCIENCE,
            "science": FactCategory.SCIENCE,
            "welt": FactCategory.NEWS,
            "news": FactCategory.NEWS,
            "japan": FactCategory.JAPAN,
        }
        return mapping.get(cat.lower() if cat else "", FactCategory.GENERAL)

    def _detect_topic(self, text: str) -> str:
        """Erkennt Hauptthema"""
        match = re.search(r'\b([A-ZÄÖÜ][a-zäöüß]{3,})\b', text)
        return match.group(1) if match else "Allgemein"

    def get_stats(self) -> Dict:
        """Gibt umfassende Statistiken zurück"""
        return {
            "knowledge": self.knowledge.get_stats(),
            "topics": self.topic_tracker.get_stats(),
            "fetcher": self.fetcher.get_stats(),
            "sessions": {
                "total": len(self.sessions),
                "recent": [
                    {
                        "category": s.category,
                        "facts_learned": s.facts_learned,
                        "duration": s.duration_seconds,
                        "success": s.success,
                    }
                    for s in self.sessions[-5:]
                ],
            },
            "schedule": self.scheduler.get_schedule_info(),
        }


# =============================================================================
# HAUPT-KLASSE: HOLO LEARNING SYSTEM
# =============================================================================

class HoloLearningSystem:
    """
    Vereintes Lernsystem - orchestriert alle Komponenten.

    Komponenten:
    - learning: RealLearningEngine (echtes Lernen)
    - mood: MoodContagion (Stimmungs-Ansteckung)
    - emotional_memory: EmotionalMemoryStore (emotionale Erinnerungen)

    NEU in v2.0:
    - HoloDatabaseManager Integration für persistente Speicherung
    - Automatisches Logging von Learning Sessions
    - Synchronisation von Topics mit Database
    """

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.data_dir = data_dir or LearningConfig.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # NEU: Database Connection
        self.db = db

        # Haupt-Komponenten (alle mit db verbunden)
        self.learning = RealLearningEngine(self.data_dir, db=db)
        self.mood = MoodContagion(db=db)
        self.emotional_memory = EmotionalMemoryStore(db=db)

        # Shortcuts
        self.knowledge = self.learning.knowledge
        self.topic_tracker = self.learning.topic_tracker

        # NEU: Database an Subkomponenten weitergeben
        if db:
            self.topic_tracker.connect_database(db)
            logger.info("[Learning] 💾 Database verbunden")

        # NEU: Meta-Cognition für Selbstreflexion
        self.meta_observer = None  # HoloMetaObserver (wird von außen gesetzt)
        self.sandbox = None        # HoloSandbox für Entscheidungen

        logger.info("🧠 HoloLearningSystem v2.0 initialisiert")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet Database nachträglich an alle Komponenten"""
        self.db = db
        self.mood.connect_database(db)
        self.topic_tracker.connect_database(db)
        logger.info("[Learning] 💾 Database nachträglich verbunden")

    # =========================================================================
    # WISSEN & LERNEN
    # =========================================================================

    def learn(self, category: str = None) -> Dict:
        """Lerne aus News"""
        start_time = time.time()
        result = self.learning.learn(category)
        duration = (time.time() - start_time) / 60  # In Minuten

        # NEU: Learning Session loggen
        if self.db and result.get("facts_added", 0) > 0:
            try:
                self.db.knowledge.log_learning_session(
                    topic=category or "allgemein",
                    session_type="news_reading",
                    duration_minutes=duration,
                    facts_learned=result.get("facts_added", 0),
                    sources=result.get("source", "RSS Feeds"),
                    quality_rating=0.7 if result.get("facts_added", 0) > 0 else 0.3,
                    key_insights=result.get("sample_facts", [""])[:1][0] if result.get("sample_facts") else ""
                )
            except Exception as e:
                logger.debug(f"Learning session log failed: {e}")

        # Meta-Observer informieren
        if self.meta_observer:
            try:
                from holo_meta_cognition import ObservationType
                self.meta_observer.observe(
                    ObservationType.LEARNING,
                    component="learning_system",
                    action="learn_from_news",
                    context={"category": category or "allgemein"},
                    outcome=f"Gelernt: {result.get('facts_added', 0)} Fakten",
                    success=result.get("facts_added", 0) > 0,
                    duration_ms=duration * 60000
                )
            except Exception as e:
                logger.warning(f"[Learning] meta_observer.observe failed: {type(e).__name__}: {e}")

        return result

    def learn_topic(self, topic: str) -> Dict:
        """Lerne gezielt über ein Thema"""
        start_time = time.time()
        result = self.learning.learn_topic(topic)
        duration = (time.time() - start_time) / 60

        # NEU: Learning Session loggen
        if self.db:
            try:
                self.db.knowledge.log_learning_session(
                    topic=topic,
                    session_type="topic_exploration",
                    duration_minutes=duration,
                    facts_learned=result.get("facts_added", 0),
                    sources="Topic Research",
                    quality_rating=0.8 if result.get("facts_added", 0) > 0 else 0.4
                )
            except Exception as e:
                logger.debug(f"Topic learning session log failed: {e}")

        return result

    def what_do_i_know(self, query: str, category: str = None) -> Dict:
        """Was weiß ich über X?"""
        return self.learning.what_do_i_know(query, category)

    def express_knowledge(self, query: str) -> str:
        """Drücke Wissen natürlich aus"""
        return self.learning.express_knowledge(query)

    def express_recent_learning(self) -> str:
        """Was habe ich kürzlich gelernt?"""
        return self.learning.express_recent_learning()

    def search_knowledge(self, query: str, limit: int = 10) -> List[LearnedFact]:
        """Durchsuche Wissensdatenbank"""
        return self.knowledge.search(query, limit=limit)

    def get_recent_knowledge(self, category: str = None, limit: int = 10) -> List[LearnedFact]:
        """Neuestes Wissen"""
        cat_enum = self.learning._to_category(category) if category else None
        return self.knowledge.get_recent(cat_enum, limit)

    def get_knowledge_about(self, category: str, limit: int = 20) -> List[LearnedFact]:
        """Wissen einer Kategorie"""
        cat_enum = self.learning._to_category(category)
        return self.knowledge.get_by_category(cat_enum, limit)

    # =========================================================================
    # STIMMUNG
    # =========================================================================

    def detect_mood(self, message: str) -> Dict:
        """Erkenne User-Stimmung"""
        return self.mood.detect_user_mood(message)

    def get_mood_influence(self, user_mood: Dict, current: float) -> float:
        """Berechne Stimmungs-Einfluss auf Holo"""
        return self.mood.calculate_mood_influence(user_mood, current)

    def get_mood_trend(self) -> Dict:
        """Stimmungstrend des Users"""
        return self.mood.get_mood_trend()

    def get_response_modifier(self, user_mood: Dict) -> Dict:
        """Modifikatoren für Holos Antwort"""
        return self.mood.get_response_modifier(user_mood)

    # =========================================================================
    # EMOTIONALE ERINNERUNGEN
    # =========================================================================

    def remember_emotion(self, trigger: str, emotion: str,
                         intensity: float, valence: float,
                         context: str = "", related_topics: List[str] = None) -> EmotionalMemory:
        """Speichere emotionale Erinnerung"""
        return self.emotional_memory.add_memory(
            trigger, emotion, intensity, valence, context, related_topics
        )

    def find_similar_emotion(self, trigger: str, emotion: str = None) -> List[EmotionalMemory]:
        """Finde ähnliche emotionale Erinnerungen"""
        return self.emotional_memory.find_similar(trigger, emotion)

    def get_emotions_by_type(self, emotion: str, limit: int = 10) -> List[EmotionalMemory]:
        """Erinnerungen einer Emotion"""
        return self.emotional_memory.find_by_emotion(emotion, limit)

    def get_strongest_emotions(self, limit: int = 10) -> List[EmotionalMemory]:
        """Stärkste emotionale Erinnerungen"""
        return self.emotional_memory.get_strongest(limit)

    # =========================================================================
    # TOPICS & INTERESSEN
    # =========================================================================

    def track_topic(self, topic: str, category: str = "allgemein") -> LearningTopic:
        """Verfolge ein Topic"""
        return self.topic_tracker.track_topic(topic, category)

    def get_active_topics(self, limit: int = 20) -> List[LearningTopic]:
        """Aktive Topics"""
        return self.topic_tracker.get_active_topics(limit)

    def get_topic_interests(self) -> List[Dict]:
        """Holos aktuelle Interessen"""
        topics = self.topic_tracker.get_active_topics(15)
        return [
            {"topic": t.topic, "interest": t.interest_level, "category": t.category}
            for t in topics
        ]

    # =========================================================================
    # STATISTIKEN
    # =========================================================================

    def get_stats(self) -> Dict:
        """Umfassende Statistiken"""
        return {
            "learning": self.learning.get_stats(),
            "emotional_memories": self.emotional_memory.get_stats(),
            "mood": self.mood.get_mood_trend(),
        }

    def get_knowledge_stats(self) -> Dict:
        """Wissens-Statistiken"""
        return self.knowledge.get_stats()

    # =========================================================================
    # WARTUNG
    # =========================================================================

    def maintenance(self):
        """Führt Wartungsarbeiten durch"""
        # Emotionale Erinnerungen verblassen lassen
        self.emotional_memory.decay_memories()

        # Inaktive Topics markieren
        self.topic_tracker.decay_inactive()

        logger.info("🔧 Wartung durchgeführt")


# =============================================================================
# FACTORY FUNCTION (Kompatibilität mit holo_brain.py)
# =============================================================================

def create_learning_components(memory=None, llm=None) -> Dict[str, Any]:
    """
    Factory für Lern-Komponenten (Dict mit allen Subsystemen).
    Kompatibel mit holo_brain.py Legacy-Code.

    HINWEIS: Für neue Nutzung create_learning_system() verwenden!
    """
    system = HoloLearningSystem()

    return {
        # Haupt-System
        'learning_system': system,

        # Komponenten
        'real_learning': system.learning,
        'knowledge_db': system.knowledge,
        'topic_tracker': system.topic_tracker,

        # Legacy-Namen (Kompatibilität)
        'mood_contagion': system.mood,
        'emotional_memory_store': system.emotional_memory,
        'daily_learning': system.learning,
    }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_learning_system(data_dir: Path = None,
                          db: 'HoloDatabaseManager' = None) -> HoloLearningSystem:
    """
    Factory-Funktion für HoloLearningSystem.

    Args:
        data_dir: Verzeichnis für JSON-Daten (Legacy)
        db: HoloDatabaseManager für persistente Speicherung

    Returns:
        Konfiguriertes HoloLearningSystem
    """
    return HoloLearningSystem(data_dir=data_dir, db=db)


def create_learning_system_with_db(data_dir: Path = None) -> HoloLearningSystem:
    """
    Erstellt HoloLearningSystem mit eigener Database.

    Args:
        data_dir: Verzeichnis für Datenbanken

    Returns:
        HoloLearningSystem mit verbundener Database
    """
    if DATABASE_AVAILABLE:
        db = HoloDatabaseManager(data_dir)
        return HoloLearningSystem(data_dir=data_dir, db=db)
    else:
        logger.warning("[Learning] Database nicht verfügbar, nutze JSON Storage")
        return HoloLearningSystem(data_dir=data_dir)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=" * 70)
    print("🧠 HOLO LEARNING SYSTEM - TEST")
    print("=" * 70)

    system = HoloLearningSystem()

    # Test-Fakten hinzufügen
    print("\n📥 Füge Test-Fakten hinzu...")

    test_facts = [
        LearnedFact(
            fact_id="test1",
            content="Frieren: Beyond Journey's End erhält zweite Staffel in 2025",
            category=FactCategory.ANIME,
            topic="Frieren",
            keywords=["frieren", "staffel", "anime", "2025"],
            source_title="Frieren News",
            source_url="https://test.de/1",
            source_feed="Anime2You",
            importance=0.9,
        ),
        LearnedFact(
            fact_id="test2",
            content="Nintendo Switch 2 wird offiziell für März 2025 erwartet",
            category=FactCategory.GAMING,
            topic="Nintendo",
            keywords=["nintendo", "switch", "konsole", "2025"],
            source_title="Nintendo News",
            source_url="https://test.de/2",
            source_feed="GameStar",
            importance=0.85,
        ),
        LearnedFact(
            fact_id="test3",
            content="Steam erreicht neuen Rekord mit 35 Millionen gleichzeitigen Nutzern",
            category=FactCategory.GAMING,
            topic="Steam",
            keywords=["steam", "rekord", "nutzer", "millionen"],
            source_title="Steam Rekord",
            source_url="https://test.de/3",
            source_feed="PC Games",
            importance=0.75,
        ),
        LearnedFact(
            fact_id="test4",
            content="OpenAI stellt GPT-5 mit verbessertem Reasoning vor",
            category=FactCategory.TECH,
            topic="GPT-5",
            keywords=["openai", "gpt5", "ki", "reasoning"],
            source_title="GPT-5 Release",
            source_url="https://test.de/4",
            source_feed="Heise",
            importance=0.8,
        ),
    ]

    for fact in test_facts:
        system.knowledge.add_fact(fact)

    print(f"✓ {len(test_facts)} Fakten hinzugefügt")

    # Wissen abrufen
    print("\n🔍 WISSEN ABRUFEN:")
    print("-" * 50)

    for query in ["Anime", "Nintendo", "Steam", "KI", "Wetter"]:
        result = system.what_do_i_know(query)
        status = "✓" if result["found"] else "✗"
        print(f"   {status} '{query}': {result['facts_count']} Fakten")

    # Natürliche Antworten
    print("\n💬 NATÜRLICHE ANTWORTEN:")
    print("-" * 50)
    print(system.express_knowledge("Anime"))
    print()
    print(system.express_knowledge("Wetter"))

    # Stimmung
    print("\n😊 STIMMUNGS-ERKENNUNG:")
    print("-" * 50)

    test_messages = [
        "Das ist ja fantastisch! Ich freue mich so! 😊",
        "Mir geht es heute nicht so gut...",
        "WOW! Das ist ja unglaublich! 🔥",
    ]

    for msg in test_messages:
        mood = system.detect_mood(msg)
        print(f"   '{msg[:40]}...' → {mood['mood']} ({mood['valence']:+.1f})")

    # Emotionale Erinnerung
    print("\n❤️ EMOTIONALE ERINNERUNG:")
    print("-" * 50)

    mem = system.remember_emotion(
        trigger="User hat sich für die Hilfe bedankt",
        emotion="freude",
        intensity=0.8,
        valence=0.9,
        context="Technische Hilfe bei Python-Problem"
    )
    print(f"   Gespeichert: {mem.trigger} ({mem.emotion})")

    # Stats
    print("\n📊 STATISTIKEN:")
    print("-" * 50)
    stats = system.get_stats()
    print(f"   Fakten: {stats['learning']['knowledge']['total_facts']}")
    print(f"   Topics: {stats['learning']['topics']['total_topics']}")
    print(f"   Emotionale Erinnerungen: {stats['emotional_memories']['total']}")

    print("\n" + "=" * 70)
    print("✅ TEST ERFOLGREICH!")
    print("=" * 70)
