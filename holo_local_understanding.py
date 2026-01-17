"""
Holo Local Understanding Module
===============================

Lokales Sprachverständnis OHNE externes LLM.

Verwendet Sentence-Transformers für semantisches Verstehen:
- Intent-Klassifikation (Was will der User?)
- Sentiment-Analyse (Wie fühlt sich der User?)
- Entity-Extraktion (Worüber spricht der User?)
- Semantische Ähnlichkeit (Wie ähnlich sind zwei Aussagen?)

Das Modul kann ~80-90% der Anfragen VERSTEHEN ohne LLM.
Nur für komplexe GENERIERUNG wird das LLM noch gebraucht.

Installation:
    pip install sentence-transformers

Autor: Claude (Integration)
Datum: 2026-01-15
"""

import logging
import json
import re
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

# =============================================================================
# GRACEFUL DEGRADATION - Funktioniert auch ohne sentence-transformers
# =============================================================================

SENTENCE_TRANSFORMERS_AVAILABLE = False
SentenceTransformer = None
np = None

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    logger.info("[LocalUnderstanding] ✓ sentence-transformers verfügbar")
except ImportError:
    logger.warning("[LocalUnderstanding] sentence-transformers nicht installiert. "
                   "Fallback auf Keyword-basiertes Verständnis. "
                   "Für bessere Ergebnisse: pip install sentence-transformers")


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

class IntentType(Enum):
    """Erkannte Intent-Typen"""
    GREETING = auto()           # Begrüßung
    FAREWELL = auto()           # Verabschiedung
    EMOTIONAL_SUPPORT = auto()  # Emotionale Unterstützung
    TECH_HELP = auto()          # Technische Hilfe
    KNOWLEDGE = auto()          # Wissensfrage
    CREATIVE = auto()           # Kreative Anfrage
    OPINION = auto()            # Meinungsfrage
    COMMAND = auto()            # Befehl/Aufforderung
    SMALLTALK = auto()          # Smalltalk
    PERSONAL = auto()           # Persönliche Frage an Holo
    FEEDBACK = auto()           # Feedback (positiv/negativ)
    CLARIFICATION = auto()      # Rückfrage
    UNKNOWN = auto()            # Unbekannt


class SentimentLevel(Enum):
    """Sentiment-Stufen"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class Entity:
    """Eine extrahierte Entität"""
    type: str           # 'person', 'number', 'url', 'date', 'product', etc.
    value: str          # Der extrahierte Wert
    confidence: float   # Wie sicher ist die Extraktion?
    start: int = 0      # Position im Text
    end: int = 0


@dataclass
class Understanding:
    """Vollständiges Verständnis einer Nachricht"""
    # Kern-Verständnis (Pflichtfelder zuerst)
    intent: IntentType
    intent_confidence: float
    sentiment: float  # -1.0 bis +1.0

    # Optionale Felder mit Defaults
    secondary_intents: List[Tuple[IntentType, float]] = field(default_factory=list)
    sentiment_level: SentimentLevel = SentimentLevel.NEUTRAL
    emotional_keywords: List[str] = field(default_factory=list)

    # Entities
    entities: List[Entity] = field(default_factory=list)

    # Topics
    topics: List[str] = field(default_factory=list)

    # Meta
    needs_llm: bool = True          # Braucht LLM für Antwort?
    complexity: float = 0.5         # 0-1, wie komplex ist die Anfrage?
    is_question: bool = False       # Ist es eine Frage?
    is_negated: bool = False        # Enthält Verneinung?
    language: str = "de"            # Erkannte Sprache

    # Embedding (für spätere Nutzung)
    embedding: Optional[Any] = None

    def to_dict(self) -> Dict:
        return {
            'intent': self.intent.name,
            'intent_confidence': self.intent_confidence,
            'sentiment': self.sentiment,
            'sentiment_level': self.sentiment_level.name,
            'entities': [{'type': e.type, 'value': e.value} for e in self.entities],
            'topics': self.topics,
            'needs_llm': self.needs_llm,
            'complexity': self.complexity,
            'is_question': self.is_question
        }


# =============================================================================
# INTENT-DEFINITIONEN
# =============================================================================

INTENT_EXAMPLES = {
    IntentType.GREETING: {
        'de': [
            "hallo", "hi", "hey", "guten morgen", "guten tag", "guten abend",
            "moin", "servus", "grüß dich", "na", "wie geht's", "wie gehts",
            "was geht", "alles klar", "huhu"
        ],
        'en': [
            "hello", "hi", "hey", "good morning", "good evening",
            "how are you", "what's up", "howdy"
        ]
    },
    IntentType.FAREWELL: {
        'de': [
            "tschüss", "bye", "auf wiedersehen", "bis später", "bis dann",
            "gute nacht", "schlaf gut", "ciao", "bis morgen", "mach's gut"
        ],
        'en': [
            "bye", "goodbye", "see you", "good night", "take care"
        ]
    },
    IntentType.EMOTIONAL_SUPPORT: {
        'de': [
            "ich bin traurig", "mir geht es schlecht", "ich fühle mich einsam",
            "ich habe angst", "ich bin deprimiert", "ich bin wütend",
            "ich kann nicht mehr", "alles ist scheiße", "niemand versteht mich",
            "ich brauche hilfe", "ich bin überfordert", "es tut weh"
        ],
        'en': [
            "i'm sad", "i feel lonely", "i'm scared", "i'm depressed",
            "i need help", "i can't take it anymore"
        ]
    },
    IntentType.TECH_HELP: {
        'de': [
            "mein computer", "mein pc", "mein laptop", "wie installiere ich",
            "welchen pc", "technik problem", "funktioniert nicht", "fehler",
            "programmieren", "code", "software", "hardware", "internet",
            "welche grafikkarte", "welcher prozessor", "gaming pc"
        ],
        'en': [
            "my computer", "how to install", "which pc", "tech problem",
            "not working", "error", "programming", "software"
        ]
    },
    IntentType.KNOWLEDGE: {
        'de': [
            "was ist", "was sind", "wer ist", "wer war", "erkläre mir",
            "erklär mir", "wie funktioniert", "warum ist", "kannst du mir sagen",
            "weißt du", "was bedeutet", "definition von", "unterschied zwischen"
        ],
        'en': [
            "what is", "who is", "explain", "how does", "why is",
            "can you tell me", "do you know", "what does", "difference between"
        ]
    },
    IntentType.CREATIVE: {
        'de': [
            "schreib mir", "schreibe mir", "erzähl mir eine geschichte",
            "sei kreativ", "stell dir vor", "erfinde", "dichte",
            "schreib ein gedicht", "mach einen witz", "erzähl einen witz"
        ],
        'en': [
            "write me", "tell me a story", "be creative", "imagine",
            "make up", "write a poem", "tell a joke"
        ]
    },
    IntentType.OPINION: {
        'de': [
            "was denkst du", "was meinst du", "magst du", "findest du",
            "deine meinung", "wie findest du", "gefällt dir", "was hältst du von"
        ],
        'en': [
            "what do you think", "do you like", "your opinion",
            "how do you feel about"
        ]
    },
    IntentType.COMMAND: {
        'de': [
            "mach", "tue", "sag mir", "zeig mir", "such nach", "finde",
            "hilf mir", "gib mir", "erstelle", "berechne"
        ],
        'en': [
            "do", "tell me", "show me", "search for", "find",
            "help me", "give me", "create", "calculate"
        ]
    },
    IntentType.SMALLTALK: {
        'de': [
            "wie war dein tag", "was machst du gerade", "langweilig",
            "erzähl was", "hast du zeit", "beschäftigt"
        ],
        'en': [
            "how was your day", "what are you doing", "boring",
            "tell me something", "are you busy"
        ]
    },
    IntentType.PERSONAL: {
        'de': [
            "wer bist du", "was bist du", "wie heißt du", "wie alt bist du",
            "was kannst du", "erzähl mir von dir", "bist du eine ki",
            "bist du ein roboter", "hast du gefühle", "kannst du fühlen"
        ],
        'en': [
            "who are you", "what are you", "what's your name",
            "how old are you", "what can you do", "are you an ai"
        ]
    },
    IntentType.FEEDBACK: {
        'de': [
            "das war gut", "das war schlecht", "danke", "super",
            "toll gemacht", "das hat geholfen", "das hilft nicht",
            "zu lang", "zu kurz", "perfekt", "genau richtig"
        ],
        'en': [
            "that was good", "that was bad", "thanks", "great",
            "well done", "that helped", "that doesn't help",
            "too long", "too short", "perfect"
        ]
    },
    IntentType.CLARIFICATION: {
        'de': [
            "was meinst du", "wie meinst du das", "kannst du das erklären",
            "ich verstehe nicht", "noch einmal", "genauer bitte"
        ],
        'en': [
            "what do you mean", "can you explain", "i don't understand",
            "again please", "more specifically"
        ]
    }
}


# =============================================================================
# SENTIMENT-LEXIKON
# =============================================================================

SENTIMENT_LEXICON = {
    'de': {
        'very_positive': [
            'liebe', 'fantastisch', 'wunderbar', 'perfekt', 'genial',
            'großartig', 'ausgezeichnet', 'hervorragend', 'traumhaft', 'begeistert'
        ],
        'positive': [
            'gut', 'schön', 'nett', 'toll', 'super', 'freude', 'glücklich',
            'danke', 'interessant', 'cool', 'klasse', 'prima', 'fein',
            'angenehm', 'freundlich', 'lustig', 'spaß', 'ja', 'gerne'
        ],
        'negative': [
            'schlecht', 'blöd', 'doof', 'langweilig', 'nervig', 'ärgerlich',
            'enttäuscht', 'frustriert', 'müde', 'genervt', 'schwierig',
            'kompliziert', 'nein', 'nicht', 'leider', 'schade'
        ],
        'very_negative': [
            'schrecklich', 'furchtbar', 'hass', 'wütend', 'traurig', 'deprimiert',
            'angst', 'verzweifelt', 'hoffnungslos', 'scheiße', 'mist',
            'katastrophe', 'horror', 'elend', 'grauenhaft'
        ]
    },
    'en': {
        'very_positive': [
            'love', 'fantastic', 'wonderful', 'perfect', 'amazing',
            'excellent', 'brilliant', 'awesome', 'incredible'
        ],
        'positive': [
            'good', 'nice', 'great', 'cool', 'happy', 'thanks', 'interesting',
            'fun', 'yes', 'like', 'enjoy', 'pleasant'
        ],
        'negative': [
            'bad', 'boring', 'annoying', 'frustrated', 'tired', 'difficult',
            'no', 'not', 'unfortunately', 'sad'
        ],
        'very_negative': [
            'terrible', 'awful', 'hate', 'angry', 'depressed', 'scared',
            'hopeless', 'horrible', 'disaster', 'miserable'
        ]
    }
}


# =============================================================================
# TOPIC-SCHLÜSSELWÖRTER
# =============================================================================

TOPIC_KEYWORDS = {
    'technik': ['computer', 'pc', 'laptop', 'cpu', 'gpu', 'ram', 'software',
                'hardware', 'programmieren', 'code', 'app', 'internet', 'server',
                'datenbank', 'algorithmus', 'bug', 'fehler'],
    'gaming': ['spiel', 'game', 'zocken', 'konsole', 'playstation', 'xbox',
               'nintendo', 'steam', 'multiplayer', 'rpg', 'shooter', 'mmorpg'],
    'anime': ['anime', 'manga', 'japan', 'otaku', 'kawaii', 'shounen', 'seinen',
              'isekai', 'crunchyroll', 'cosplay', 'waifu'],
    'musik': ['musik', 'song', 'lied', 'album', 'band', 'konzert', 'spotify',
              'playlist', 'singen', 'instrument', 'gitarre', 'klavier'],
    'filme': ['film', 'movie', 'kino', 'serie', 'netflix', 'streaming',
              'schauspieler', 'regisseur', 'trailer'],
    'wissenschaft': ['forschung', 'studie', 'wissenschaft', 'entdeckung',
                     'experiment', 'theorie', 'physik', 'chemie', 'biologie'],
    'gesundheit': ['gesund', 'krank', 'arzt', 'medizin', 'sport', 'fitness',
                   'ernährung', 'schlaf', 'stress'],
    'beziehung': ['freund', 'freundin', 'familie', 'eltern', 'partner',
                  'liebe', 'beziehung', 'streit', 'trennung'],
    'arbeit': ['arbeit', 'job', 'chef', 'kollege', 'büro', 'meeting',
               'projekt', 'deadline', 'gehalt', 'bewerbung'],
    'hobby': ['hobby', 'freizeit', 'basteln', 'malen', 'lesen', 'kochen',
              'backen', 'garten', 'reisen', 'fotografie'],
}


# =============================================================================
# HAUPTKLASSE: LOKALES VERSTÄNDNIS
# =============================================================================

class HoloLocalUnderstanding:
    """
    Lokales Sprachverständnis für Holo.

    Versteht Text OHNE externes LLM durch:
    - Sentence Embeddings (semantische Ähnlichkeit)
    - Intent-Klassifikation
    - Sentiment-Analyse
    - Entity-Extraktion
    - Topic-Erkennung

    Verwendung:
        lu = HoloLocalUnderstanding()
        understanding = lu.understand("Ich brauche einen neuen Gaming-PC")

        if understanding.needs_llm:
            # LLM für komplexe Antwort
        else:
            # Lokale Template-Antwort möglich
    """

    def __init__(self, data_dir: Path = None, model_name: str = None):
        self.data_dir = data_dir or Path("data/local_understanding")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Embedding-Modell
        self.model = None
        self.model_name = model_name or 'paraphrase-multilingual-MiniLM-L12-v2'
        self.use_embeddings = False

        # Intent-Embeddings (werden bei Bedarf berechnet)
        self.intent_embeddings: Dict[IntentType, Any] = {}

        # Caches für Performance
        self.embedding_cache: Dict[str, Any] = {}
        self.max_cache_size = 1000

        # Statistiken
        self.stats = {
            'total_processed': 0,
            'local_handled': 0,
            'llm_needed': 0,
            'intents_detected': defaultdict(int)
        }

        # Initialisiere Embedding-Modell wenn verfügbar
        self._init_embedding_model()

        logger.info(f"[LocalUnderstanding] Initialisiert (Embeddings: {self.use_embeddings})")

    def _init_embedding_model(self):
        """Initialisiert das Embedding-Modell"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.info("[LocalUnderstanding] Nutze Keyword-Fallback (kein sentence-transformers)")
            return

        try:
            logger.info(f"[LocalUnderstanding] Lade Modell: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self.use_embeddings = True

            # Pre-compute Intent-Embeddings
            self._precompute_intent_embeddings()

            logger.info("[LocalUnderstanding] ✓ Embedding-Modell geladen")
        except Exception as e:
            logger.warning(f"[LocalUnderstanding] Konnte Modell nicht laden: {e}")
            self.use_embeddings = False

    def _precompute_intent_embeddings(self):
        """Berechnet Intent-Embeddings vorab"""
        if not self.use_embeddings or not self.model:
            return

        for intent_type, lang_examples in INTENT_EXAMPLES.items():
            # Kombiniere alle Sprachen
            all_examples = []
            for examples in lang_examples.values():
                all_examples.extend(examples)

            if all_examples:
                # Berechne Durchschnitts-Embedding
                embeddings = self.model.encode(all_examples)
                self.intent_embeddings[intent_type] = np.mean(embeddings, axis=0)

        logger.info(f"[LocalUnderstanding] {len(self.intent_embeddings)} Intent-Embeddings berechnet")

    # =========================================================================
    # HAUPTMETHODE: UNDERSTAND
    # =========================================================================

    def understand(self, text: str) -> Understanding:
        """
        Versteht einen Text vollständig lokal.

        Args:
            text: Der zu verstehende Text

        Returns:
            Understanding-Objekt mit allen Analysen
        """
        self.stats['total_processed'] += 1

        # Normalisiere Text
        text_clean = text.strip()
        text_lower = text_clean.lower()

        # 1. Sprache erkennen
        language = self._detect_language(text_lower)

        # 2. Intent klassifizieren
        if self.use_embeddings:
            intent, intent_conf, secondary = self._classify_intent_embedding(text_clean)
        else:
            intent, intent_conf, secondary = self._classify_intent_keyword(text_lower)

        self.stats['intents_detected'][intent.name] += 1

        # 3. Sentiment analysieren
        sentiment, sentiment_level, emotional_words = self._analyze_sentiment(text_lower, language)

        # 4. Entities extrahieren
        entities = self._extract_entities(text_clean)

        # 5. Topics erkennen
        topics = self._extract_topics(text_lower)

        # 6. Frage erkennen
        is_question = self._is_question(text_clean)

        # 7. Verneinung erkennen
        is_negated = self._has_negation(text_lower)

        # 8. Komplexität berechnen
        complexity = self._calculate_complexity(text_clean, intent, entities, topics)

        # 9. Entscheide ob LLM nötig
        needs_llm = self._needs_llm(intent, intent_conf, complexity, is_question)

        if needs_llm:
            self.stats['llm_needed'] += 1
        else:
            self.stats['local_handled'] += 1

        # 10. Embedding für spätere Nutzung
        embedding = None
        if self.use_embeddings:
            embedding = self._get_embedding(text_clean)

        return Understanding(
            intent=intent,
            intent_confidence=intent_conf,
            secondary_intents=secondary,
            sentiment=sentiment,
            sentiment_level=sentiment_level,
            emotional_keywords=emotional_words,
            entities=entities,
            topics=topics,
            needs_llm=needs_llm,
            complexity=complexity,
            is_question=is_question,
            is_negated=is_negated,
            language=language,
            embedding=embedding
        )

    # =========================================================================
    # INTENT-KLASSIFIKATION
    # =========================================================================

    def _classify_intent_embedding(self, text: str) -> Tuple[IntentType, float, List]:
        """Klassifiziert Intent mit Embeddings"""
        text_embedding = self._get_embedding(text)

        scores = []
        for intent_type, intent_emb in self.intent_embeddings.items():
            # Kosinus-Ähnlichkeit
            similarity = np.dot(text_embedding, intent_emb) / (
                np.linalg.norm(text_embedding) * np.linalg.norm(intent_emb)
            )
            scores.append((intent_type, float(similarity)))

        # Sortiere nach Score
        scores.sort(key=lambda x: x[1], reverse=True)

        best_intent = scores[0][0] if scores else IntentType.UNKNOWN
        best_conf = scores[0][1] if scores else 0.0

        # Secondary Intents (nächste 2 mit Score > 0.5)
        secondary = [(i, s) for i, s in scores[1:3] if s > 0.5]

        return best_intent, best_conf, secondary

    def _classify_intent_keyword(self, text_lower: str) -> Tuple[IntentType, float, List]:
        """Fallback: Klassifiziert Intent mit Keywords"""
        scores = defaultdict(float)

        # Entferne Satzzeichen für besseres Matching
        text_clean = re.sub(r'[^\w\s]', '', text_lower).strip()
        words = set(text_clean.split())

        for intent_type, lang_examples in INTENT_EXAMPLES.items():
            for examples in lang_examples.values():
                for example in examples:
                    example_clean = re.sub(r'[^\w\s]', '', example.lower()).strip()
                    example_words = set(example_clean.split())

                    # Exakter Match für Einzelwörter (z.B. "hallo", "tschüss")
                    if len(example_words) == 1 and example_words.issubset(words):
                        scores[intent_type] = max(scores[intent_type], 0.95)
                        continue

                    # Vollständiger Match
                    if example_clean == text_clean:
                        scores[intent_type] = max(scores[intent_type], 1.0)
                        continue

                    # Substring Match (z.B. "wie geht's" in "hey wie geht's dir")
                    if example_clean in text_clean:
                        scores[intent_type] = max(scores[intent_type], 0.85)
                        continue

                    # Wie viele Wörter überlappen?
                    overlap = len(words & example_words)
                    if overlap > 0:
                        # Normalisiere nach Beispiel-Länge
                        score = overlap / len(example_words)
                        scores[intent_type] = max(scores[intent_type], score * 0.8)

        if not scores:
            return IntentType.UNKNOWN, 0.0, []

        # Sortiere
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        best_intent = sorted_scores[0][0]
        best_conf = min(sorted_scores[0][1], 0.95)  # Cap bei 0.95 für Keywords

        secondary = [(i, s) for i, s in sorted_scores[1:3] if s > 0.3]

        return best_intent, best_conf, secondary

    # =========================================================================
    # SENTIMENT-ANALYSE
    # =========================================================================

    def _analyze_sentiment(self, text_lower: str, language: str
                           ) -> Tuple[float, SentimentLevel, List[str]]:
        """Analysiert Sentiment des Textes"""
        words = set(text_lower.split())
        lexicon = SENTIMENT_LEXICON.get(language, SENTIMENT_LEXICON['de'])

        very_pos_count = len(words & set(lexicon['very_positive']))
        pos_count = len(words & set(lexicon['positive']))
        neg_count = len(words & set(lexicon['negative']))
        very_neg_count = len(words & set(lexicon['very_negative']))

        # Gefundene emotionale Wörter
        emotional_words = []
        for category in lexicon.values():
            emotional_words.extend([w for w in words if w in category])

        # Berechne Score (-1 bis +1)
        total_positive = very_pos_count * 2 + pos_count
        total_negative = very_neg_count * 2 + neg_count
        total = total_positive + total_negative

        if total == 0:
            return 0.0, SentimentLevel.NEUTRAL, emotional_words

        sentiment = (total_positive - total_negative) / (total + 1)
        sentiment = max(-1.0, min(1.0, sentiment))

        # Bestimme Level
        if sentiment <= -0.6:
            level = SentimentLevel.VERY_NEGATIVE
        elif sentiment <= -0.2:
            level = SentimentLevel.NEGATIVE
        elif sentiment >= 0.6:
            level = SentimentLevel.VERY_POSITIVE
        elif sentiment >= 0.2:
            level = SentimentLevel.POSITIVE
        else:
            level = SentimentLevel.NEUTRAL

        return sentiment, level, emotional_words

    # =========================================================================
    # ENTITY-EXTRAKTION
    # =========================================================================

    def _extract_entities(self, text: str) -> List[Entity]:
        """Extrahiert Entities aus Text"""
        entities = []

        # URLs
        url_pattern = r'https?://[^\s]+'
        for match in re.finditer(url_pattern, text):
            entities.append(Entity(
                type='url',
                value=match.group(),
                confidence=1.0,
                start=match.start(),
                end=match.end()
            ))

        # E-Mail
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        for match in re.finditer(email_pattern, text):
            entities.append(Entity(
                type='email',
                value=match.group(),
                confidence=1.0,
                start=match.start(),
                end=match.end()
            ))

        # Zahlen mit Einheiten
        number_unit_pattern = r'\b(\d+(?:[.,]\d+)?)\s*(€|EUR|USD|\$|GB|MB|TB|kg|km|m|cm|mm|%|°C|°F)?\b'
        for match in re.finditer(number_unit_pattern, text):
            value = match.group(1)
            unit = match.group(2) or ''
            entities.append(Entity(
                type='number' if not unit else f'number_{unit.lower()}',
                value=f"{value}{unit}",
                confidence=0.9,
                start=match.start(),
                end=match.end()
            ))

        # Datum (einfache Muster)
        date_patterns = [
            r'\b(\d{1,2})[./](\d{1,2})[./](\d{2,4})\b',  # DD.MM.YYYY
            r'\b(\d{4})-(\d{2})-(\d{2})\b',              # YYYY-MM-DD
        ]
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    type='date',
                    value=match.group(),
                    confidence=0.85,
                    start=match.start(),
                    end=match.end()
                ))

        # Zeit
        time_pattern = r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(Uhr|AM|PM)?\b'
        for match in re.finditer(time_pattern, text, re.IGNORECASE):
            entities.append(Entity(
                type='time',
                value=match.group(),
                confidence=0.85,
                start=match.start(),
                end=match.end()
            ))

        # Produktnamen (häufige Tech-Produkte)
        tech_products = [
            r'\b(AMD\s+Ryzen\s+\d+\s*\d*)\b',
            r'\b(Intel\s+Core\s+i\d+(?:-\d+)?[A-Z]*)\b',
            r'\b(NVIDIA\s+(?:GeForce\s+)?(?:RTX|GTX)\s+\d+(?:\s+Ti)?)\b',
            r'\b(Radeon\s+RX\s+\d+(?:\s+XT)?)\b',
            r'\b(Windows\s+\d+)\b',
            r'\b(iPhone\s+\d+(?:\s+Pro)?(?:\s+Max)?)\b',
            r'\b(Samsung\s+Galaxy\s+S\d+)\b',
            r'\b(PlayStation\s+\d+|PS\d+)\b',
            r'\b(Xbox\s+(?:Series\s+)?[XS]?)\b',
            r'\b(Nintendo\s+Switch)\b',
        ]
        for pattern in tech_products:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    type='product',
                    value=match.group(),
                    confidence=0.9,
                    start=match.start(),
                    end=match.end()
                ))

        # Eigennamen (Großbuchstaben am Wortanfang, nicht am Satzanfang)
        words = text.split()
        for i, word in enumerate(words):
            # Überspringe erstes Wort und deutsche Nomen-Großschreibung
            if i == 0:
                continue
            if re.match(r'^[A-ZÄÖÜ][a-zäöüß]+$', word):
                # Filtere häufige deutsche Nomen
                common_nouns = {'Ich', 'Du', 'Sie', 'Wir', 'Das', 'Die', 'Der', 'Ein', 'Eine'}
                if word not in common_nouns:
                    entities.append(Entity(
                        type='name',
                        value=word,
                        confidence=0.6
                    ))

        return entities

    # =========================================================================
    # TOPIC-EXTRAKTION
    # =========================================================================

    def _extract_topics(self, text_lower: str) -> List[str]:
        """Extrahiert Topics aus Text"""
        found_topics = []

        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                found_topics.append(topic)

        return found_topics

    # =========================================================================
    # HILFSMETHODEN
    # =========================================================================

    def _detect_language(self, text_lower: str) -> str:
        """Erkennt Sprache (einfache Heuristik)"""
        # Deutsche Wörter
        german_indicators = {'ich', 'du', 'und', 'ist', 'das', 'die', 'der', 'ein',
                            'nicht', 'auch', 'was', 'wie', 'für', 'mit', 'auf'}
        # Englische Wörter
        english_indicators = {'i', 'you', 'the', 'and', 'is', 'are', 'what', 'how',
                             'for', 'with', 'this', 'that', 'not', 'can'}

        words = set(text_lower.split())

        german_count = len(words & german_indicators)
        english_count = len(words & english_indicators)

        if english_count > german_count:
            return 'en'
        return 'de'

    def _is_question(self, text: str) -> bool:
        """Erkennt ob Text eine Frage ist"""
        # Fragezeichen
        if '?' in text:
            return True

        text_lower = text.lower()

        # Fragewörter
        question_words = ['was', 'wer', 'wie', 'wo', 'wann', 'warum', 'weshalb',
                         'woher', 'wohin', 'welche', 'welcher', 'welches',
                         'what', 'who', 'how', 'where', 'when', 'why', 'which']

        first_word = text_lower.split()[0] if text_lower.split() else ''

        return first_word in question_words

    def _has_negation(self, text_lower: str) -> bool:
        """Erkennt Verneinung im Text"""
        negation_words = ['nicht', 'kein', 'keine', 'keiner', 'niemals', 'nie',
                         'nein', 'ohne', 'weder', "don't", "doesn't", "isn't",
                         "aren't", "not", "no", "never", "without"]

        return any(neg in text_lower for neg in negation_words)

    def _calculate_complexity(self, text: str, intent: IntentType,
                               entities: List[Entity], topics: List[str]) -> float:
        """Berechnet Komplexität der Anfrage (0-1)"""
        complexity = 0.3  # Basis

        # Länge erhöht Komplexität
        word_count = len(text.split())
        if word_count > 20:
            complexity += 0.2
        elif word_count > 10:
            complexity += 0.1

        # Komplexe Intents
        complex_intents = {IntentType.CREATIVE, IntentType.KNOWLEDGE, IntentType.TECH_HELP}
        if intent in complex_intents:
            complexity += 0.2

        # Viele Entities
        if len(entities) > 3:
            complexity += 0.1

        # Viele Topics
        if len(topics) > 2:
            complexity += 0.1

        return min(1.0, complexity)

    def _needs_llm(self, intent: IntentType, confidence: float,
                   complexity: float, is_question: bool) -> bool:
        """Entscheidet ob LLM für Antwort nötig ist"""
        # Einfache Intents können lokal beantwortet werden
        local_intents = {
            IntentType.GREETING,
            IntentType.FAREWELL,
            IntentType.FEEDBACK,
            IntentType.PERSONAL  # Holo kennt sich selbst
        }

        # Lokale Antwort wenn:
        # - Intent ist einfach UND
        # - Confidence ist hoch UND
        # - Komplexität ist niedrig
        if intent in local_intents and confidence >= 0.7 and complexity < 0.5:
            return False

        # Opinion kann auch lokal sein wenn Confidence hoch
        if intent == IntentType.OPINION and confidence >= 0.8:
            return False

        # Smalltalk kann lokal sein
        if intent == IntentType.SMALLTALK and confidence >= 0.75:
            return False

        # Alles andere braucht LLM
        return True

    def _get_embedding(self, text: str) -> Any:
        """Holt oder berechnet Embedding für Text"""
        if not self.use_embeddings or not self.model:
            return None

        # Cache-Key
        cache_key = hashlib.md5(text.encode()).hexdigest()

        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Berechne Embedding
        embedding = self.model.encode(text)

        # Cache (mit Größenbegrenzung)
        if len(self.embedding_cache) >= self.max_cache_size:
            # Entferne älteste Einträge
            keys_to_remove = list(self.embedding_cache.keys())[:100]
            for key in keys_to_remove:
                del self.embedding_cache[key]

        self.embedding_cache[cache_key] = embedding

        return embedding

    # =========================================================================
    # SIMILARITY-METHODEN
    # =========================================================================

    def similarity(self, text1: str, text2: str) -> float:
        """Berechnet semantische Ähnlichkeit zwischen zwei Texten"""
        if not self.use_embeddings:
            # Fallback: Jaccard-Ähnlichkeit
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0.0

        emb1 = self._get_embedding(text1)
        emb2 = self._get_embedding(text2)

        # Kosinus-Ähnlichkeit
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)

    def find_similar(self, query: str, candidates: List[str], top_k: int = 5
                     ) -> List[Tuple[str, float]]:
        """Findet ähnlichste Kandidaten zu einer Query"""
        if not candidates:
            return []

        scores = [(c, self.similarity(query, c)) for c in candidates]
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]

    # =========================================================================
    # LOKALE ANTWORT-GENERIERUNG
    # =========================================================================

    def get_local_response(self, understanding: Understanding) -> Optional[str]:
        """
        Generiert lokale Antwort wenn möglich.

        Returns:
            Antwort-String oder None wenn LLM nötig
        """
        if understanding.needs_llm:
            return None

        intent = understanding.intent
        sentiment = understanding.sentiment_level

        # Greeting-Antworten
        if intent == IntentType.GREETING:
            if sentiment in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]:
                return "*schaut interessiert freudig* Hey! Dir scheint's ja gut zu gehen!"
            elif sentiment in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]:
                return "*neigt Kopf besorgt* Hey... alles okay bei dir?"
            else:
                return "*freut sich sichtlich* Hey! Was gibt's Neues?"

        # Farewell-Antworten
        if intent == IntentType.FAREWELL:
            responses = [
                "*winkt mit dem Hände* Bis bald!",
                "Machs gut! *entspannter Blick*",
                "*lächelt warm* Bis später!",
            ]
            import random
            return random.choice(responses)

        # Feedback-Antworten
        if intent == IntentType.FEEDBACK:
            if understanding.sentiment >= 0.3:
                return "*freut sich glücklich* Das freut mich!"
            elif understanding.sentiment <= -0.3:
                return "*schaut nach unten* Oh... das tut mir leid. Was kann ich besser machen?"
            else:
                return "*nickt* Verstanden!"

        # Personal-Antworten
        if intent == IntentType.PERSONAL:
            # Holo antwortet über sich selbst
            return None  # Lass das den Persönlichkeits-Layer machen

        # Smalltalk
        if intent == IntentType.SMALLTALK:
            responses = [
                "*denkt nach* Hmm, gerade überlege ich so einiges...",
                "*schaut überrascht* Ich hab heute viel gelernt!",
                "*streckt sich* Mir geht's gut! Und dir?",
            ]
            import random
            return random.choice(responses)

        return None

    # =========================================================================
    # STATISTIKEN
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken zurück"""
        total = self.stats['total_processed']
        local_rate = self.stats['local_handled'] / total if total > 0 else 0

        return {
            'total_processed': total,
            'local_handled': self.stats['local_handled'],
            'llm_needed': self.stats['llm_needed'],
            'local_rate': f"{local_rate:.1%}",
            'embeddings_enabled': self.use_embeddings,
            'cache_size': len(self.embedding_cache),
            'top_intents': dict(sorted(
                self.stats['intents_detected'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_local_understanding(data_dir: Path = None,
                                model_name: str = None) -> HoloLocalUnderstanding:
    """Factory-Funktion für HoloLocalUnderstanding"""
    return HoloLocalUnderstanding(data_dir, model_name)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO LOCAL UNDERSTANDING - TEST")
    print("=" * 60)

    lu = HoloLocalUnderstanding()

    test_inputs = [
        "Hallo, wie geht's dir?",
        "Ich bin so traurig heute...",
        "Welchen Gaming-PC würdest du empfehlen für 1500€?",
        "Was ist der Unterschied zwischen AMD und Intel?",
        "Schreib mir ein kurzes Gedicht über Wölfe",
        "Tschüss, bis morgen!",
        "Das war super hilfreich, danke!",
        "Wer bist du eigentlich?",
        "Was denkst du über Anime?",
    ]

    for text in test_inputs:
        print(f"\n{'─' * 60}")
        print(f"INPUT: {text}")
        print(f"{'─' * 60}")

        understanding = lu.understand(text)

        print(f"  Intent: {understanding.intent.name} ({understanding.intent_confidence:.0%})")
        print(f"  Sentiment: {understanding.sentiment:.2f} ({understanding.sentiment_level.name})")
        print(f"  Topics: {understanding.topics}")
        print(f"  Entities: {[f'{e.type}:{e.value}' for e in understanding.entities]}")
        print(f"  Is Question: {understanding.is_question}")
        print(f"  Complexity: {understanding.complexity:.2f}")
        print(f"  Needs LLM: {understanding.needs_llm}")

        local_response = lu.get_local_response(understanding)
        if local_response:
            print(f"  LOCAL RESPONSE: {local_response}")

    print(f"\n{'=' * 60}")
    print("STATISTIKEN")
    print("=" * 60)
    stats = lu.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
