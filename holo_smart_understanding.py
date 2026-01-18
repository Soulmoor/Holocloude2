#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO SMART UNDERSTANDING - Zentrale Intent Detection                        ║
║                                                                              ║
║  SINGLE SOURCE OF TRUTH für:                                                 ║
║  • Intent Detection (inkl. Multi-Intent)                                     ║
║  • Entity Extraction                                                         ║
║  • Sentiment Analysis                                                        ║
║  • Follow-up Detection                                                       ║
║  • Reference Resolution                                                      ║
║                                                                              ║
║  INTEGRIERT BESTE FEATURES AUS:                                              ║
║  • holo_nlp_algorithms.py → Fuzzy Matching, Kölner Phonetik, TF-IDF          ║
║  • holo_context_mind.py → TopicTracker (ehem. holo_organic)                  ║
║  • holo_message_analyzer.py → Multi-Intent, WolfNewsFormatter                ║
║  • holo_dialogue_engine.py → DialogueActs                                    ║
║                                                                              ║
║  Andere Module sollten diese Klasse IMPORTIEREN statt eigene Intent-         ║
║  Detection zu implementieren!                                                ║
║                                                                              ║
║  Version: 3.0 (Consolidated)                                                 ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import logging
import time
import math
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from difflib import SequenceMatcher
from collections import Counter, deque, defaultdict
from enum import Enum
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger("SmartUnderstanding")

# =============================================================================
# PUBLIC API - Exported symbols
# =============================================================================

__all__ = [
    # Main Class - Primary Entry Point
    "SmartUnderstanding",

    # Configuration
    "UnderstandingConfig",

    # Enums
    "IntentType",
    "IntentPriority",
    "Sentiment",
    "SharedContentType",

    # Data Classes
    "DetectedIntent",
    "SentimentResult",
    "SharedContent",
    "IntentMatch",
    "KeywordMatch",

    # Core Detectors
    "KeywordIntentDetector",
    "MultiIntentDetector",
    "QuestionTypeClassifier",
    "ImplicitIntentDetector",
    "ContextAwareDetector",
    "MultiStageIntentPipeline",

    # Analysis Classes
    "SentimentAnalyzer",
    "EntityExtractor",
    "SubjectVerbAnalyzer",
    "WellbeingInquiryDetector",
    "UserEmotionDetector",
    "ActivityInquiryDetector",
    "UserActivityExtractor",

    # Text Processing
    "FuzzyMatcher",
    "KoelnerPhonetik",
    "TextNormalizer",
    "NegationHandler",
    "IntensityAnalyzer",
    "SarcasmDetector",
    "ModalVerbHandler",
    "ConditionalPatternDetector",

    # Response Enhancement
    "HoloResponsePipeline",
    "ResponseIntensityModifier",
    "EmotionalResponseEnhancer",
    "ContextualResponseAdapter",

    # Context Tracking
    "ConversationContextTracker",
    "SharedContentTracker",

    # Specialized Handlers
    "SeparableVerbHandler",
    "CodeSwitchingDetector",
    "EmojiIntentDetector",
    "InternetSlangDetector",
    "TemporalReferenceDetector",
    "EllipsisHandler",
    "ContextIntentInheritor",

    # Fallbacks (for when nlp_algorithms not available)
    "SentenceAnalyzerFallback",
    "AnaphoraResolverFallback",
    "WolfNewsFormatterFallback",
]

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value


# =============================================================================
# OPTIONAL IMPORTS - Features aus anderen Modulen (mit Fallbacks)
# =============================================================================

# Versuche erweiterte Features zu importieren
_HAS_NLP_ALGORITHMS = False
_HAS_CONTEXT_MIND = False
_HAS_MESSAGE_ANALYZER = False

try:
    from holo_nlp_algorithms import (
        AdvancedFuzzyMatcher,
        AdvancedSentimentAnalyzer,
        TFIDFIntentDetector,
        EntityExtractor as NLPEntityExtractor,
        DialogueActClassifier,
        AntiRepetitionTracker,
    )
    _HAS_NLP_ALGORITHMS = True
    logger.info("✅ holo_nlp_algorithms importiert")
except ImportError:
    logger.debug("⚠️ holo_nlp_algorithms nicht verfügbar - nutze Fallbacks")

# holo_organic wurde in holo_context_mind konsolidiert
try:
    from holo_context_mind import TopicTracker
    _HAS_CONTEXT_MIND = True
    logger.info("✅ holo_context_mind (TopicTracker) importiert")
except ImportError:
    TopicTracker = None
    logger.debug("⚠️ holo_context_mind nicht verfügbar")

try:
    from holo_message_analyzer import (
        WolfNewsFormatter,
        IntentType as MessageIntentType,
        IntentPriority,
    )
    _HAS_MESSAGE_ANALYZER = True
    logger.info("✅ holo_message_analyzer importiert")
except ImportError:
    logger.debug("⚠️ holo_message_analyzer nicht verfügbar - nutze Fallbacks")


# =============================================================================
# CONFIGURATION
# =============================================================================

class UnderstandingConfig:
    """Zentrale Konfiguration"""

    # Fuzzy Matching
    FUZZY_THRESHOLD = 0.85
    KEYWORD_CONFIDENCE_THRESHOLD = 0.6
    MAX_TYPO_DISTANCE = 1
    MIN_FUZZY_LENGTH = 4

    # Bekannte Typos
    KNOWN_SHORT_KEYWORDS = {
        "ki": ["kii", "kiii", "ky"],
        "nas": ["nass", "naas"],
        "llm": ["lllm", "llmm"],
        "cpu": ["cpuu", "cpi"],
        "ram": ["ramm", "raam"],
        "api": ["apii", "abi"],
    }

    # Shared Content
    SHARED_CONTENT_TIMEOUT_MINUTES = 30
    MAX_SHARED_CONTENT_ITEMS = 10

    # Multi-Intent
    MULTI_INTENT_ENABLED = True
    MAX_INTENTS_PER_MESSAGE = 3


# =============================================================================
# INTENT TYPES - Unified
# =============================================================================

class IntentType(Enum):
    """Alle möglichen Intent-Typen (Unified aus allen Modulen)"""
    # Greetings & Social
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    COMPLIMENT = "compliment"
    APOLOGY = "apology"

    # Activity & Wellbeing
    ACTIVITY_INQUIRY = "activity_inquiry"
    WELLBEING_INQUIRY = "wellbeing_inquiry"

    # Information Requests
    STATUS = "status"
    STATUS_NAS = "status_nas"
    NEWS = "news"
    NEWS_DETAIL = "news_detail"
    WEATHER = "weather"
    TIME = "time"
    TEMPERATURE = "temperature"

    # Knowledge & Self
    USER_KNOWLEDGE = "user_knowledge"
    TOPIC_EXPLAIN = "topic_explain"
    SELF_INFO = "self_info"
    QUESTION_KI = "question_ki"

    # Holo-Specific
    DREAM = "dream"
    EMOTION = "emotion"
    MEMORY = "memory"
    PERSONALITY = "personality"

    # Actions & Commands
    COMMAND = "command"
    COMMAND_NAS_START = "command_nas_start"
    COMMAND_NAS_STOP = "command_nas_stop"
    SMART_HOME = "smart_home"
    LIGHT_CONTROL = "light"
    SEARCH = "search"
    REMINDER = "reminder"
    TIMER = "timer"

    # Conversation
    QUESTION = "question"
    CHITCHAT = "chitchat"
    INTRODUCTION = "introduction"
    FEEDBACK = "feedback"
    ROMANTIC = "romantic"
    NEGATIVE = "negative"

    # Follow-up & References
    FOLLOWUP_QUESTION = "followup_question"
    PREVIOUS_REFERENCE = "previous_reference"
    RECIPE_REFERENCE = "recipe_reference"

    # User Shared Content (NEU!)
    USER_SHARED_ACTIVITY = "user_shared_activity"  # User erzählt was er macht/gemacht hat
    USER_SHARED_OPINION = "user_shared_opinion"    # User teilt Meinung
    USER_SHARED_EXPERIENCE = "user_shared_experience"  # User erzählt Erlebnis

    # Meta
    HELP = "help"
    SETTINGS = "settings"

    # Default
    GENERAL = "general"
    UNKNOWN = "unknown"


class IntentPriority(Enum):
    """Priorität für Response-Reihenfolge"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


# =============================================================================
# SENTIMENT
# =============================================================================

class Sentiment(Enum):
    """Sentiment-Typen"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"


@dataclass
class SentimentResult:
    """Sentiment-Analyse Ergebnis"""
    sentiment: Sentiment
    score: float  # -1.0 bis 1.0
    confidence: float
    is_sarcastic: bool = False
    indicators: List[str] = field(default_factory=list)


# =============================================================================
# DETECTED INTENT
# =============================================================================

@dataclass
class DetectedIntent:
    """Ein erkannter Intent mit Metadaten"""
    intent_type: IntentType
    confidence: float
    priority: IntentPriority = IntentPriority.MEDIUM
    text_segment: str = ""
    extracted_entities: Dict = field(default_factory=dict)
    requires_llm: bool = False
    context_hint: str = ""

    # Multi-Intent Support
    is_primary: bool = True
    secondary_intents: List['DetectedIntent'] = field(default_factory=list)

    def __lt__(self, other):
        """Für Sortierung nach Priorität"""
        return self.priority.value < other.priority.value


# =============================================================================
# SHARED CONTENT TRACKING
# =============================================================================

class SharedContentType(Enum):
    """Typen von geteiltem Content"""
    NEWS = "news"
    LINK = "link"
    CODE = "code"
    IMAGE = "image"
    DOCUMENT = "document"
    QUOTE = "quote"
    FACT = "fact"
    QUESTION = "question"
    TOPIC = "topic"
    UNKNOWN = "unknown"


@dataclass
class SharedContent:
    """Ein vom User geteilter Inhalt"""
    content_type: SharedContentType
    content: str
    summary: str
    keywords: List[str]
    timestamp: float
    source: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        age_minutes = (time.time() - self.timestamp) / 60
        return age_minutes > timeout_minutes

    def matches_query(self, query_keywords: List[str], threshold: float = 0.3) -> float:
        if not query_keywords or not self.keywords:
            return 0.0
        query_set = set(kw.lower() for kw in query_keywords)
        content_set = set(kw.lower() for kw in self.keywords)
        intersection = query_set & content_set
        union = query_set | content_set
        return len(intersection) / len(union) if union else 0.0


# =============================================================================
# KÖLNER PHONETIK - Für deutsche Fuzzy Matches
# =============================================================================

class KoelnerPhonetik:
    """
    Kölner Phonetik - Phonetischer Algorithmus für Deutsch.
    Ähnlich klingende Wörter → gleicher Code.

    Delegiert zu AdvancedFuzzyMatcher.cologne_phonetic() wenn verfügbar,
    sonst nutzt eigene Fallback-Implementation.
    """

    @staticmethod
    @lru_cache(maxsize=5000)
    def encode(word: str) -> str:
        """Wandle Wort in phonetischen Code um"""
        # Nutze nlp_algorithms Implementation wenn verfügbar
        if _HAS_NLP_ALGORITHMS:
            return AdvancedFuzzyMatcher.cologne_phonetic(word)

        # Fallback-Implementation
        if not word:
            return ""

        word = word.lower()

        # Umlaute ersetzen
        replacements = {
            'ä': 'a', 'ö': 'o', 'ü': 'u', 'ß': 'ss',
            'ph': 'f', 'qu': 'kw', 'pf': 'f', 'ck': 'k'
        }
        for old, new in replacements.items():
            word = word.replace(old, new)

        result = []
        prev_code = ""

        for i, char in enumerate(word):
            code = ""
            prev_char = word[i-1] if i > 0 else ""
            next_char = word[i+1] if i < len(word)-1 else ""

            if char in "aeiouäöüj":
                code = "0"
            elif char == "b":
                code = "1"
            elif char == "p":
                code = "1" if next_char != "h" else "3"
            elif char in "dt":
                code = "2" if next_char not in "csz" else "8"
            elif char in "fvw":
                code = "3"
            elif char in "gkq":
                code = "4"
            elif char == "c":
                if i == 0:
                    code = "4" if next_char in "ahkloqrux" else "8"
                else:
                    code = "4" if prev_char in "sz" else "8"
            elif char == "x":
                code = "48"
            elif char == "l":
                code = "5"
            elif char in "mn":
                code = "6"
            elif char == "r":
                code = "7"
            elif char in "sz":
                code = "8"
            elif char == "h":
                code = ""  # h wird ignoriert (wie in nlp_algorithms)

            if code and code != prev_code:
                result.append(code)
                prev_code = code

        result_str = "".join(result)
        if len(result_str) > 1:
            result_str = result_str[0] + result_str[1:].replace("0", "")

        return result_str

    @classmethod
    def similarity(cls, word1: str, word2: str) -> float:
        """Phonetische Ähnlichkeit (0-1)"""
        p1 = cls.encode(word1)
        p2 = cls.encode(word2)

        if p1 == p2:
            return 1.0

        if not p1 or not p2:
            return 0.0

        # Jaro-Winkler auf phonetischen Codes
        return SequenceMatcher(None, p1, p2).ratio() * 0.9


# =============================================================================
# ADVANCED FUZZY MATCHER
# =============================================================================

class FuzzyMatcher:
    """
    Kombiniertes Fuzzy Matching:
    - Jaro-Winkler (gut für Tippfehler)
    - Damerau-Levenshtein (Transpositionen)
    - Kölner Phonetik (Hörfehler)
    """

    def __init__(self):
        self.phonetic = KoelnerPhonetik()

        # Nutze erweiterte Version wenn verfügbar
        if _HAS_NLP_ALGORITHMS:
            self._advanced = AdvancedFuzzyMatcher()
        else:
            self._advanced = None

    @staticmethod
    @lru_cache(maxsize=10000)
    def jaro_winkler(s1: str, s2: str, prefix_weight: float = 0.1) -> float:
        """Jaro-Winkler Similarity"""
        if s1 == s2:
            return 1.0

        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0

        match_distance = max(len1, len2) // 2 - 1
        if match_distance < 0:
            match_distance = 0

        s1_matches = [False] * len1
        s2_matches = [False] * len2
        matches = 0
        transpositions = 0

        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        jaro = (matches / len1 + matches / len2 +
                (matches - transpositions / 2) / matches) / 3

        # Prefix bonus
        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        return jaro + prefix_len * prefix_weight * (1 - jaro)

    @staticmethod
    @lru_cache(maxsize=10000)
    def damerau_levenshtein(s1: str, s2: str) -> int:
        """Damerau-Levenshtein Distanz (mit Transpositionen)"""
        len1, len2 = len(s1), len(s2)

        if len1 == 0:
            return len2
        if len2 == 0:
            return len1
        if s1 == s2:
            return 0

        d = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            d[i][0] = i
        for j in range(len2 + 1):
            d[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                d[i][j] = min(
                    d[i-1][j] + 1,
                    d[i][j-1] + 1,
                    d[i-1][j-1] + cost
                )
                if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                    d[i][j] = min(d[i][j], d[i-2][j-2] + cost)

        return d[len1][len2]

    def combined_similarity(self, s1: str, s2: str) -> float:
        """Kombinierte Ähnlichkeit aus allen Methoden"""
        if s1 == s2:
            return 1.0

        s1_lower = s1.lower()
        s2_lower = s2.lower()

        # Nutze erweiterte Version wenn verfügbar
        if self._advanced:
            return self._advanced.combined_similarity(s1, s2)

        # Fallback: Eigene Implementierung
        jw = self.jaro_winkler(s1_lower, s2_lower)

        max_len = max(len(s1), len(s2))
        dl_dist = self.damerau_levenshtein(s1_lower, s2_lower)
        dl_sim = 1.0 - (dl_dist / max_len) if max_len > 0 else 1.0

        phon_sim = self.phonetic.similarity(s1_lower, s2_lower)

        # Gewichteter Durchschnitt
        return jw * 0.4 + dl_sim * 0.35 + phon_sim * 0.25

    def fuzzy_word_match(self, word: str, target: str,
                         threshold: float = None) -> Tuple[bool, float]:
        """Prüfe ob Wort fuzzy zum Target passt"""
        threshold = threshold or UnderstandingConfig.FUZZY_THRESHOLD

        # Exakter Match
        if word.lower() == target.lower():
            return True, 1.0

        # Kurze Keywords: Nur exakt oder bekannte Typos
        if len(target) < UnderstandingConfig.MIN_FUZZY_LENGTH:
            known_typos = UnderstandingConfig.KNOWN_SHORT_KEYWORDS.get(target, [])
            if word.lower() in known_typos:
                return True, 0.95
            return False, 0.0

        # Fuzzy Match
        similarity = self.combined_similarity(word, target)
        return similarity >= threshold, similarity

    def find_best_match(self, query: str, candidates: List[str],
                        threshold: float = 0.7) -> Tuple[Optional[str], float]:
        """Finde besten Match aus Kandidaten"""
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            score = self.combined_similarity(query, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= threshold:
            return best_match, best_score
        return None, best_score


# =============================================================================
# SENTENCE ANALYZER (aus holo_organic)
# =============================================================================

class SentenceAnalyzerFallback:
    """
    Fallback SentenceAnalyzer wenn holo_organic nicht verfügbar.
    Analysiert deutsche Satzstruktur.
    """

    NEBENSATZ_MARKER = [
        "dass", "weil", "obwohl", "wenn", "falls", "sofern",
        "nachdem", "bevor", "während", "sobald", "bis", "seit",
        "damit", "sodass", "als", "wie", "ob",
    ]

    EINLEITUNGEN = [
        "danke", "dankeschön", "vielen dank", "okay", "ok", "alles klar",
        "ja", "nein", "naja", "also", "ähm", "hmm", "achso", "ach",
        "übrigens", "apropos", "nebenbei",
    ]

    FRAGE_WOERTER = [
        "was", "wer", "wie", "wo", "wann", "warum", "wieso", "weshalb",
        "welcher", "welche", "welches", "wieviel", "wie viel",
        "kannst", "könntest", "würdest", "ist", "sind", "hat", "haben",
    ]

    BEFEHLS_VERBEN = [
        "mach", "schalte", "starte", "stoppe", "zeig", "gib", "hol",
        "such", "finde", "öffne", "schließe", "sag", "erzähl", "erkläre",
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict:
        """Analysiert Satzstruktur"""
        text_clean = text.strip()
        text_lower = text_clean.lower()

        result = {
            'sentence_type': cls._detect_sentence_type(text_clean, text_lower),
            'segments': cls._segment_sentence(text_lower),
            'main_segment': text_clean,
            'main_segment_index': 0,
            'has_einleitung': False,
            'einleitung': None,
            'keyword_weights': {},
        }

        # Einleitung erkennen
        if result['segments']:
            first = result['segments'][0].strip()
            if len(first.split()) <= 3:
                for einl in cls.EINLEITUNGEN:
                    if first.startswith(einl) or first == einl:
                        result['has_einleitung'] = True
                        result['einleitung'] = einl
                        break

        # Hauptsegment finden
        start_index = 1 if result['has_einleitung'] and len(result['segments']) > 1 else 0
        if start_index < len(result['segments']):
            result['main_segment'] = result['segments'][start_index]
            result['main_segment_index'] = start_index

        return result

    @classmethod
    def _detect_sentence_type(cls, text: str, text_lower: str) -> str:
        if text.endswith('?'):
            return 'question'
        first_word = safe_list_access(text_lower.split(), 0, "smart_understanding", "_detect_sentence_type", default="")
        if first_word in cls.FRAGE_WOERTER:
            return 'question'
        if first_word in cls.BEFEHLS_VERBEN:
            return 'command'
        return 'statement'

    @classmethod
    def _segment_sentence(cls, text_lower: str) -> List[str]:
        segments = re.split(r'[,;.!?]+', text_lower)
        return [s.strip() for s in segments if s.strip()]


# Nutze Fallback (holo_organic wurde konsolidiert)
SentenceAnalyzerImpl = SentenceAnalyzerFallback


# =============================================================================
# ANAPHORA RESOLVER (aus holo_organic)
# =============================================================================

class AnaphoraResolverFallback:
    """
    Fallback Anaphora Resolver - löst Pronomen auf.
    z.B. "das", "es", "davon" → worauf bezieht sich das?
    """

    PRONOUNS = {
        "personal": ["er", "sie", "es", "ihn", "ihm", "ihr"],
        "demonstrative": ["das", "dies", "dieses", "jenes", "dieser", "diese"],
        "locative": ["dort", "da", "hier", "dahin", "dorthin"],
        "relative": ["darüber", "dazu", "davon", "damit", "dafür"],
    }

    def __init__(self):
        self.entity_stack: List[Dict] = []
        self.topic_stack: List[str] = []

    def add_entity(self, entity: str, entity_type: str = "unknown"):
        """Füge Entity zum Stack hinzu"""
        self.entity_stack.append({"entity": entity, "type": entity_type})
        if len(self.entity_stack) > 10:
            self.entity_stack.pop(0)

    def add_topic(self, topic: str):
        """Füge Thema zum Stack hinzu"""
        self.topic_stack.append(topic)
        if len(self.topic_stack) > 5:
            self.topic_stack.pop(0)

    def resolve(self, pronoun: str) -> Optional[str]:
        """Löse Pronomen auf"""
        pronoun_lower = pronoun.lower()

        # Relative Pronomen → letztes Thema
        if pronoun_lower in self.PRONOUNS["relative"]:
            if self.topic_stack:
                return self.topic_stack[-1]

        # Demonstrative → letzte Entity
        if pronoun_lower in self.PRONOUNS["demonstrative"]:
            if self.entity_stack:
                return self.entity_stack[-1]["entity"]

        return None

    def has_unresolved_reference(self, text: str) -> bool:
        """Prüfe ob Text unaufgelöste Referenzen enthält"""
        text_lower = text.lower()
        all_pronouns = []
        for plist in self.PRONOUNS.values():
            all_pronouns.extend(plist)

        for pronoun in all_pronouns:
            if f" {pronoun} " in f" {text_lower} " or text_lower.startswith(pronoun + " "):
                return True
        return False


# Nutze Fallback (holo_organic wurde konsolidiert)
AnaphoraResolverImpl = AnaphoraResolverFallback


# =============================================================================
# TEXT NORMALIZER
# =============================================================================

class TextNormalizer:
    """Normalisiert Text für Analyse"""

    REPLACEMENTS = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "'s": " ist", "'n": " ein", "'ne": " eine",
    }

    CONTRACTIONS = {
        "gehts": "geht es", "gibts": "gibt es", "hats": "hat es",
        "isses": "ist es", "machste": "machst du", "biste": "bist du",
        "kannste": "kannst du", "willste": "willst du",
        "weisste": "weißt du", "weiste": "weißt du",
    }

    def normalize(self, text: str) -> str:
        """Normalisiere Text"""
        result = text.lower().strip()

        # Kontraktionen
        for short, long in self.CONTRACTIONS.items():
            result = result.replace(short, long)

        # Mehrfache Leerzeichen
        result = re.sub(r'\s+', ' ', result)

        return result

    def extract_keywords(self, text: str) -> List[str]:
        """Extrahiere Keywords"""
        stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber",
            "ich", "du", "er", "sie", "es", "wir", "ihr", "sie",
            "ist", "sind", "war", "bin", "hat", "haben", "wird",
            "zu", "in", "an", "auf", "für", "mit", "von", "bei",
            "ja", "nein", "nicht", "auch", "nur", "noch", "schon",
            "mal", "denn", "doch", "so", "sehr", "ganz", "dass",
            "was", "wie", "wo", "wann", "warum", "wer",
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]

        return list(set(keywords))[:15]


# =============================================================================
# SENTIMENT ANALYZER
# =============================================================================

class SentimentAnalyzer:
    """Sentiment-Analyse mit Lexikon und Modifikatoren"""

    def __init__(self):
        # Nutze erweiterte Version wenn verfügbar
        if _HAS_NLP_ALGORITHMS:
            self._advanced = AdvancedSentimentAnalyzer()
        else:
            self._advanced = None

        self._init_lexicon()

    def _init_lexicon(self):
        """Initialisiere Sentiment-Lexikon"""
        self.positive_words = {
            "super": 0.8, "toll": 0.7, "gut": 0.5, "schön": 0.6,
            "fantastisch": 1.0, "großartig": 0.9, "wunderbar": 0.9,
            "liebe": 0.8, "freue": 0.7, "glücklich": 0.8,
            "cool": 0.6, "nice": 0.6, "top": 0.7, "klasse": 0.7,
            "danke": 0.4, "bitte": 0.2,
        }

        self.negative_words = {
            "schlecht": -0.6, "blöd": -0.5, "doof": -0.4,
            "furchtbar": -0.9, "schrecklich": -0.9, "hasse": -0.9,
            "traurig": -0.7, "wütend": -0.7, "nervig": -0.5,
            "mist": -0.6, "scheiße": -0.8, "kacke": -0.7,
            "langweilig": -0.3, "müde": -0.2,
        }

        self.intensifiers = {
            "sehr": 1.5, "total": 1.6, "echt": 1.4, "richtig": 1.4,
            "mega": 1.6, "extrem": 1.8, "super": 1.4,
        }

        self.negations = ["nicht", "kein", "keine", "keinen", "nie", "niemals"]

    def analyze(self, text: str) -> SentimentResult:
        """Analysiere Sentiment"""
        # Nutze erweiterte Version wenn verfügbar
        if self._advanced:
            result = self._advanced.analyze(text)
            return SentimentResult(
                sentiment=Sentiment(result.sentiment) if result.sentiment in [s.value for s in Sentiment] else Sentiment.NEUTRAL,
                score=result.score,
                confidence=result.confidence,
                is_sarcastic=result.is_sarcastic,
                indicators=[i[0] for i in result.positive_indicators + result.negative_indicators]
            )

        # Fallback
        return self._analyze_simple(text)

    def _analyze_simple(self, text: str) -> SentimentResult:
        """Einfache Sentiment-Analyse"""
        text_lower = text.lower()
        words = text_lower.split()

        score = 0.0
        indicators = []
        negation_active = False
        modifier = 1.0

        for word in words:
            # Negation?
            if word in self.negations:
                negation_active = True
                continue

            # Intensifier?
            if word in self.intensifiers:
                modifier = self.intensifiers[word]
                continue

            # Positive?
            if word in self.positive_words:
                value = self.positive_words[word] * modifier
                if negation_active:
                    value *= -0.8
                score += value
                indicators.append(word)

            # Negative?
            elif word in self.negative_words:
                value = self.negative_words[word] * modifier
                if negation_active:
                    value *= -0.8
                score += value
                indicators.append(word)

            negation_active = False
            modifier = 1.0

        # Score normalisieren
        score = max(-1.0, min(1.0, score))

        # Sentiment bestimmen
        if score >= 0.5:
            sentiment = Sentiment.VERY_POSITIVE
        elif score >= 0.2:
            sentiment = Sentiment.POSITIVE
        elif score <= -0.5:
            sentiment = Sentiment.VERY_NEGATIVE
        elif score <= -0.2:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL

        return SentimentResult(
            sentiment=sentiment,
            score=score,
            confidence=min(1.0, abs(score) + 0.3),
            indicators=indicators
        )


# =============================================================================
# SHARED CONTENT TRACKER
# =============================================================================

class SharedContentTracker:
    """Trackt Inhalte die der User geteilt hat"""

    SHARE_INDICATORS = {
        SharedContentType.NEWS: [
            r"(?:hast du |kennst du |weißt du )(?:schon |bereits )?(?:die(?:se)? |den |das )?(?:news|nachricht|artikel)",
            r"(?:schau|guck|lies) (?:dir )?(?:mal )?(?:diese?n?|den|das) (?:news|artikel)",
            r"(?:habe|hab) (?:gerade |eben )?(?:gelesen|gesehen|gehört)",
        ],
        SharedContentType.LINK: [
            r"https?://\S+",
            r"www\.\S+",
        ],
        SharedContentType.CODE: [
            r"```[\s\S]*```",
            r"(?:hier|da) ist (?:mein |der |ein )?code",
        ],
    }

    FOLLOWUP_PATTERNS = [
        r"(?:was )?(?:weißt|denkst|meinst|hältst|sagst) (?:du )?(?:darüber|dazu|davon)",
        r"(?:was )?(?:ist |sind )?(?:deine |dein )?(?:meinung|gedanken) (?:dazu|darüber)",
        r"(?:kannst du |könntest du )?(?:mir )?(?:mehr )?(?:darüber|dazu) (?:sagen|erzählen)",
        r"(?:was ist |erkläre? )?(?:das|dies)",
        r"(?:mehr |weitere )?(?:infos?|details?) (?:dazu|darüber|bitte)",
        r"^(?:und|also|aber|interessant|krass|wow)[\s!?.]*$",
        r"^(?:wirklich|echt|stimmt das)[\s!?]*$",
    ]

    def __init__(self, max_items: int = None):
        self.max_items = max_items or UnderstandingConfig.MAX_SHARED_CONTENT_ITEMS
        self.shared_items: deque = deque(maxlen=self.max_items)
        self.normalizer = TextNormalizer()

    def detect_shared_content(self, text: str) -> Optional[SharedContent]:
        """Erkennt ob User Content teilt"""
        text_lower = text.lower()

        for content_type, patterns in self.SHARE_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    keywords = self.normalizer.extract_keywords(text)
                    url_match = re.search(r'https?://\S+', text)

                    return SharedContent(
                        content_type=content_type,
                        content=text,
                        summary=text[:100] + "..." if len(text) > 100 else text,
                        keywords=keywords,
                        timestamp=time.time(),
                        source=url_match.group(0) if url_match else None,
                    )
        return None

    def is_followup(self, text: str) -> Tuple[bool, float]:
        """Prüft ob Text ein Follow-up ist"""
        text_lower = text.lower()

        for pattern in self.FOLLOWUP_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, 0.85

        return False, 0.0

    def add_shared_content(self, content: SharedContent):
        """Fügt geteilten Content hinzu"""
        self.shared_items.append(content)

    def get_recent(self, max_age_minutes: int = 30) -> List[SharedContent]:
        """Hole kürzlich geteilten Content"""
        cutoff = time.time() - (max_age_minutes * 60)
        return [item for item in self.shared_items if item.timestamp >= cutoff]

    def find_matching_content(self, keywords: List[str]) -> Optional[SharedContent]:
        """Finde passenden geteilten Content"""
        recent = self.get_recent()
        best_match = None
        best_score = 0.3

        for item in recent:
            score = item.matches_query(keywords)
            if score > best_score:
                best_score = score
                best_match = item

        return best_match


# =============================================================================
# MULTI-INTENT DETECTOR
# =============================================================================

class MultiIntentDetector:
    """
    Erkennt MEHRERE Intents in einer Nachricht.

    z.B. "hast du news? und was machst du so?"
    → [NEWS, ACTIVITY_INQUIRY]
    """

    def __init__(self):
        self.fuzzy = FuzzyMatcher()
        self.normalizer = TextNormalizer()

        # Intent-Patterns
        self._init_patterns()

    def _init_patterns(self):
        """Initialisiere Intent-Patterns"""
        self.patterns = {
            IntentType.GREETING: [
                r'^(hallo|hi|hey|moin|guten\s*(morgen|tag|abend)|servus)[\s!,]*$',
                r'^na[\s!?]*$',
            ],
            IntentType.FAREWELL: [
                r'(tschüss|bye|ciao|bis\s*(bald|dann|später)|gute\s*nacht)',
            ],
            IntentType.ACTIVITY_INQUIRY: [
                r'was (?:machst|tust) du',
                r'was hast du (?:so )?gemacht',
                r'womit beschäftigst du dich',
            ],
            IntentType.WELLBEING_INQUIRY: [
                r"wie geht(?:'?s| es) dir",
                r'wie fühlst du dich',
                r'alles (?:klar|gut) bei dir',
            ],
            IntentType.NEWS: [
                r'(?:hast du |gibt es )?(?:irgendwelche )?news',
                r'(?:hast du )?nachrichten',
                r'was gibt(?:\'?s| es) neues',
            ],
            IntentType.STATUS_NAS: [
                r'nas\s*(?:status|check)',
                r'(?:wie )?(?:geht|läuft)(?:\'?s| es)? (?:dem )?nas',
            ],
            IntentType.DREAM: [
                r'was hast du (?:zuletzt\s+)?geträumt',
                r'(?:dein|deinen?)\s+(?:letzter?\s+)?traum',
                r'träumst du',
            ],
            IntentType.SELF_INFO: [
                r'was weißt du (?:über )?(?:dich|dich selbst)',
                r'wer bist du',
                r'was kannst du',
            ],
            IntentType.USER_KNOWLEDGE: [
                r'was weißt du (?:über|von) mir',
                r'erinnerst du dich an mich',
            ],
            IntentType.TEMPERATURE: [
                r'(?:wie )?(?:warm|kalt) ist es',
                r'temperatur',
                r'(?:wie ?viel|wieviele?) grad',
            ],
            IntentType.SMART_HOME: [
                r'(?:licht|lampe)\s+(?:an|aus|ein|dimmen)',
                r'(?:mach|schalte).+(?:licht|lampe)',
            ],
            IntentType.SEARCH: [
                r'^(?:such|google|finde?)\s+',
            ],
            IntentType.INTRODUCTION: [
                r'(?:ich heiße|mein name ist|nenn mich)',
                r'ich bin\s+\w+\s*$',
            ],
            IntentType.GRATITUDE: [
                r'^(?:danke|dankeschön|vielen dank|thx|thanks)',
            ],
            IntentType.HELP: [
                r'^(?:hilfe|help|was kannst du)',
            ],
        }

        # Kompilieren
        self._compiled = {}
        for intent, patterns in self.patterns.items():
            self._compiled[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def detect_all(self, text: str) -> List[DetectedIntent]:
        """Erkenne ALLE Intents in einer Nachricht"""
        text_lower = text.lower().strip()
        intents = []

        # Segmentiere bei "und", ",", "?"
        segments = re.split(r'[,?]|\bund\b|\baber\b|\boder\b', text_lower)
        segments = [s.strip() for s in segments if s.strip()]

        for segment in segments:
            detected = self._detect_in_segment(segment)
            intents.extend(detected)

        # Deduplizieren
        seen = set()
        unique = []
        for intent in intents:
            if intent.intent_type not in seen:
                seen.add(intent.intent_type)
                unique.append(intent)

        # Sortieren nach Priorität
        unique.sort()

        # Fallback
        if not unique:
            unique.append(DetectedIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.5,
                priority=IntentPriority.LOW,
                text_segment=text
            ))

        return unique

    def _detect_in_segment(self, segment: str) -> List[DetectedIntent]:
        """Erkenne Intents in einem Segment"""
        intents = []

        for intent_type, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.search(segment):
                    priority = self._get_priority(intent_type)
                    intents.append(DetectedIntent(
                        intent_type=intent_type,
                        confidence=0.85,
                        priority=priority,
                        text_segment=segment,
                    ))
                    break

        return intents

    def _get_priority(self, intent_type: IntentType) -> IntentPriority:
        """Bestimme Priorität eines Intent-Typs"""
        high_priority = {
            IntentType.FAREWELL, IntentType.ACTIVITY_INQUIRY,
            IntentType.WELLBEING_INQUIRY, IntentType.COMMAND,
        }
        low_priority = {
            IntentType.GREETING, IntentType.CHITCHAT, IntentType.GRATITUDE,
        }

        if intent_type in high_priority:
            return IntentPriority.HIGH
        elif intent_type in low_priority:
            return IntentPriority.LOW
        return IntentPriority.MEDIUM


# =============================================================================
# KEYWORD INTENT DETECTOR
# =============================================================================

@dataclass
class KeywordMatch:
    """Ein Keyword-Match"""
    keyword: str
    matched_word: str
    confidence: float
    position: int


@dataclass
class IntentMatch:
    """Ein Intent-Match mit Details"""
    intent: str
    confidence: float
    matches: List[KeywordMatch]
    trigger_count: int


class KeywordIntentDetector:
    """Intent Detection basierend auf Keywords"""

    INTENT_KEYWORDS = {
        # Grüße
        "greeting": {
            "trigger_words": ["hallo", "hi", "hey", "moin", "servus", "guten"],
            "required": [],
            "optional": ["morgen", "tag", "abend"],
        },
        # Verabschiedung
        "farewell": {
            "trigger_words": ["tschüss", "bye", "ciao", "nacht"],
            "required": [],
            "optional": ["gute", "bis", "bald"],
        },
        # Status
        "status_general": {
            "trigger_words": ["status", "statusbericht", "bericht"],
            "required": [],
            "optional": [],
        },
        "status_nas": {
            "required": ["nas"],
            "trigger_words": ["status", "läuft", "geht", "online"],
            "optional": [],
        },
        # Aktivität
        "activity_inquiry": {
            "trigger_words": ["machst", "tust", "gemacht", "getrieben", "beschäftigt"],
            "required": [],
            "optional": ["was", "du", "so"],
        },
        # Wohlbefinden
        "wellbeing_inquiry": {
            "trigger_words": ["geht", "gehts", "fühlst"],
            "required": [],
            "optional": ["wie", "dir"],
        },
        # News
        "news": {
            "trigger_words": ["news", "nachrichten", "neuigkeiten", "neues"],
            "required": [],
            "optional": ["hast", "gibt", "was"],
        },
        # Traum
        "dream": {
            "trigger_words": ["traum", "träume", "geträumt", "träumst"],
            "required": [],
            "optional": ["was", "hast", "du"],
        },
        # Wissen über User
        "user_knowledge": {
            "required": ["weißt", "mir"],
            "trigger_words": ["über"],
            "optional": ["was", "du"],
        },
        # Selbst-Info
        "self_info": {
            "trigger_words": ["bist", "kannst"],
            "required": ["du"],
            "optional": ["wer", "was"],
        },
        # KI Frage
        "question_ki": {
            "required": ["ki"],
            "trigger_words": ["was", "erkläre", "erklär"],
            "optional": ["ist"],
            "synonyms": {"ki": ["künstliche intelligenz", "artificial intelligence", "ai"]},
        },
        # NAS Commands
        "command_nas_start": {
            "required": ["nas"],
            "trigger_words": ["start", "starten", "aufwecken", "weck", "an"],
            "optional": ["bitte"],
        },
        "command_nas_stop": {
            "required": ["nas"],
            "trigger_words": ["stop", "stoppen", "aus", "herunterfahren"],
            "optional": ["bitte"],
        },
        # Follow-up
        "followup_question": {
            "trigger_words": ["darüber", "dazu", "davon", "damit", "dafür"],
            "required": [],
            "optional": ["was", "mehr", "erzähl"],
        },
        # Hilfe
        "help": {
            "trigger_words": ["hilfe", "help", "kannst"],
            "required": [],
            "optional": ["was", "du"],
        },
        # Danke
        "gratitude": {
            "trigger_words": ["danke", "dankeschön", "thanks", "thx"],
            "required": [],
            "optional": ["vielen"],
        },
    }

    def __init__(self):
        self.normalizer = TextNormalizer()
        self.fuzzy = FuzzyMatcher()

    def detect_intent(self, text: str) -> Optional[IntentMatch]:
        """Erkenne Intent basierend auf Keywords"""
        normalized = self.normalizer.normalize(text)
        words = normalized.split()
        words_set = set(words)

        candidates = []

        for intent_name, intent_data in self.INTENT_KEYWORDS.items():
            required = intent_data.get("required", [])
            trigger_words = intent_data.get("trigger_words", [])
            optional = intent_data.get("optional", [])
            synonyms = intent_data.get("synonyms", {})

            matches = []
            trigger_matches = 0

            # Required Keywords
            all_required = True
            for req_kw in required:
                found = False
                all_variants = [req_kw] + synonyms.get(req_kw, [])

                for variant in all_variants:
                    for word in words:
                        is_match, conf = self.fuzzy.fuzzy_word_match(word, variant)
                        if is_match:
                            matches.append(KeywordMatch(req_kw, word, conf, -1))
                            found = True
                            break
                    if found:
                        break

                if not found:
                    all_required = False
                    break

            if not all_required and required:
                continue

            # Trigger Words
            for trigger in trigger_words:
                if trigger in words_set:
                    matches.append(KeywordMatch(trigger, trigger, 1.0, -1))
                    trigger_matches += 1
                else:
                    for word in words:
                        is_match, conf = self.fuzzy.fuzzy_word_match(word, trigger)
                        if is_match:
                            matches.append(KeywordMatch(trigger, word, conf, -1))
                            trigger_matches += 1
                            break

            if trigger_words and trigger_matches == 0 and not required:
                continue

            # Optional Keywords
            for opt_kw in optional:
                if opt_kw in words_set:
                    matches.append(KeywordMatch(opt_kw, opt_kw, 0.7, -1))

            # Confidence berechnen
            if matches:
                core_matches = [m for m in matches if m.confidence >= 0.9]
                if core_matches:
                    avg_conf = sum(m.confidence for m in core_matches) / len(core_matches)
                else:
                    avg_conf = sum(m.confidence for m in matches) / len(matches)

                if required and all_required:
                    avg_conf = min(avg_conf + 0.15, 1.0)

                if trigger_matches > 1:
                    avg_conf = min(avg_conf + 0.1, 1.0)

                candidates.append({
                    "intent": intent_name,
                    "confidence": avg_conf,
                    "matches": matches,
                    "trigger_count": trigger_matches,
                })

        if not candidates:
            return None

        # Beste wählen
        best = max(candidates, key=lambda x: (x["confidence"], x["trigger_count"]))

        return IntentMatch(
            intent=best["intent"],
            confidence=best["confidence"],
            matches=best["matches"],
            trigger_count=best["trigger_count"]
        )


# =============================================================================
# ENTITY EXTRACTOR
# =============================================================================

class EntityExtractor:
    """Extrahiert Entities aus Text"""

    PATTERNS = {
        "time_absolute": r"(\d{1,2})[:\.](\d{2})\s*(?:uhr)?",
        "time_relative": r"in\s+(\d+)\s*(?:min(?:uten?)?|stunden?)",
        "number": r"\b(\d+(?:[.,]\d+)?)\b",
        "temperature": r"(\d+(?:[.,]\d+)?)\s*(?:°c?|grad)",
        "percentage": r"(\d+(?:[.,]\d+)?)\s*(?:%|prozent)",
    }

    GAZETTEERS = {
        "device": ["nas", "server", "licht", "lampe", "computer", "handy", "fernseher"],
        "room": ["wohnzimmer", "schlafzimmer", "küche", "bad", "büro", "flur"],
        "color": ["rot", "blau", "grün", "gelb", "weiß", "warm", "kalt"],
        "action": ["an", "aus", "ein", "dimmen", "starten", "stoppen"],
    }

    def __init__(self):
        # Nutze erweiterte Version wenn verfügbar
        if _HAS_NLP_ALGORITHMS:
            self._advanced = NLPEntityExtractor()
        else:
            self._advanced = None

    def extract(self, text: str) -> List[Dict]:
        """Extrahiere Entities"""
        if self._advanced:
            entities = self._advanced.extract(text)
            return [{"type": e.type, "value": e.value, "original": e.original} for e in entities]

        return self._extract_simple(text)

    def _extract_simple(self, text: str) -> List[Dict]:
        """Einfache Entity-Extraktion"""
        entities = []
        text_lower = text.lower()

        # Pattern-basiert
        for entity_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text_lower):
                entities.append({
                    "type": entity_type,
                    "value": match.group(1),
                    "original": match.group(0),
                })

        # Gazetteer-basiert
        words = text_lower.split()
        for word in words:
            for entity_type, values in self.GAZETTEERS.items():
                if word in values:
                    entities.append({
                        "type": entity_type,
                        "value": word,
                        "original": word,
                    })

        return entities


# =============================================================================
# USER ACTIVITY EXTRACTOR (NEU!)
# =============================================================================

class UserActivityExtractor:
    """
    Extrahiert User-Aktivitäten aus dem Text.

    Erkennt Patterns wie:
    - "ich habe Genshin Impact gespielt"
    - "ich spiele gerade Minecraft"
    - "ich schaue eine Serie"
    - "ich habe einen Film gesehen"
    """

    # Aktivitäts-Patterns mit Kategorien
    ACTIVITY_PATTERNS = [
        # Gaming
        (r"ich\s+(?:habe?|hab)\s+(?:viel\s+|etwas\s+)?(.+?)\s+(?:gespielt|gezockt|gemacht)", "gaming"),
        (r"ich\s+(?:spiele|zocke)\s+(?:gerade\s+)?(.+?)(?:\s|$|,|\.)", "gaming"),
        (r"war(?:en)?\s+(?:bei|in|am)\s+(.+?)\s+(?:spielen|zocken)", "gaming"),

        # Watching (Filme/Serien/Anime)
        (r"ich\s+(?:habe?|hab)\s+(?:gerade\s+)?(.+?)\s+(?:geschaut|geguckt|gesehen|angeschaut)", "watching"),
        (r"ich\s+(?:schaue?|gucke?)\s+(?:gerade\s+)?(.+?)(?:\s|$|,|\.)", "watching"),
        (r"war(?:en)?\s+(?:bei|im)\s+(?:kino|film)", "watching"),

        # Reading
        (r"ich\s+(?:habe?|hab)\s+(?:gerade\s+)?(.+?)\s+(?:gelesen|durchgelesen)", "reading"),
        (r"ich\s+(?:lese|les)\s+(?:gerade\s+)?(.+?)(?:\s|$|,|\.)", "reading"),

        # Listening (Musik/Podcast)
        (r"ich\s+(?:habe?|hab)\s+(?:gerade\s+)?(.+?)\s+(?:gehört|angehört)", "listening"),
        (r"ich\s+(?:höre?)\s+(?:gerade\s+)?(.+?)(?:\s|$|,|\.)", "listening"),

        # Working/Studying
        (r"ich\s+(?:habe?|hab)\s+(?:an\s+)?(.+?)\s+(?:gearbeitet|gelernt|studiert)", "working"),
        (r"ich\s+(?:arbeite|lerne)\s+(?:gerade\s+)?(?:an\s+)?(.+?)(?:\s|$|,|\.)", "working"),

        # General Activities
        (r"ich\s+war\s+(?:gerade\s+)?(?:beim?|im|in\s+der?)\s+(.+?)(?:\s|$|,|\.)", "activity"),
        (r"ich\s+(?:habe?|hab)\s+(?:gerade\s+)?(.+?)\s+gemacht", "activity"),
        (r"ich\s+(?:mache|tu)\s+(?:gerade\s+)?(.+?)(?:\s|$|,|\.)", "activity"),
    ]

    # Bekannte Spiele/Medien für bessere Extraktion
    KNOWN_GAMES = {
        "genshin", "genshin impact", "minecraft", "fortnite", "valorant",
        "league of legends", "lol", "wow", "world of warcraft", "elden ring",
        "dark souls", "zelda", "pokemon", "mario", "animal crossing",
        "stardew valley", "terraria", "cyberpunk", "baldurs gate", "diablo",
    }

    KNOWN_MEDIA = {
        "anime", "serie", "film", "movie", "youtube", "twitch", "netflix",
        "disney", "amazon prime", "crunchyroll", "spotify", "podcast",
    }

    def __init__(self):
        self.last_extracted: Optional[Dict] = None
        self.session_activities: List[Dict] = []

    def extract(self, text: str) -> Optional[Dict]:
        """
        Extrahiert User-Aktivität aus Text.

        Returns:
            Dict mit:
            - activity_type: gaming/watching/reading/etc.
            - activity_name: Was genau (z.B. "Genshin Impact")
            - raw_match: Ursprünglicher Match
            - confidence: Wie sicher (0-1)
        """
        text_lower = text.lower()

        for pattern, activity_type in self.ACTIVITY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                activity_name = match.group(1).strip() if match.groups() else ""

                # Cleanup
                activity_name = self._clean_activity_name(activity_name)

                if activity_name and len(activity_name) > 1:
                    # Confidence basierend auf Bekanntheitsgrad
                    confidence = self._calculate_confidence(activity_name, activity_type)

                    result = {
                        "activity_type": activity_type,
                        "activity_name": activity_name,
                        "raw_match": match.group(0),
                        "confidence": confidence,
                        "is_known": self._is_known(activity_name),
                    }

                    self.last_extracted = result
                    self.session_activities.append(result)

                    # Max 20 Activities speichern
                    if len(self.session_activities) > 20:
                        self.session_activities = self.session_activities[-20:]

                    return result

        return None

    def _clean_activity_name(self, name: str) -> str:
        """Bereinigt extrahierten Namen"""
        # Entferne häufige Füllwörter am Ende
        stop_words = ["und", "oder", "aber", "dann", "jetzt", "gerade", "noch", "auch"]
        words = name.split()
        while words and words[-1].lower() in stop_words:
            words.pop()

        # Entferne Satzzeichen
        name = " ".join(words)
        name = re.sub(r"[,\.!?:;]", "", name)

        return name.strip()

    def _is_known(self, name: str) -> bool:
        """Prüft ob Aktivität bekannt ist"""
        name_lower = name.lower()
        return (
            name_lower in self.KNOWN_GAMES or
            name_lower in self.KNOWN_MEDIA or
            any(known in name_lower for known in self.KNOWN_GAMES) or
            any(known in name_lower for known in self.KNOWN_MEDIA)
        )

    def _calculate_confidence(self, name: str, activity_type: str) -> float:
        """Berechnet Confidence Score"""
        confidence = 0.6  # Base

        # Bekannte Namen = höhere Confidence
        if self._is_known(name):
            confidence += 0.3

        # Längere Namen = oft spezifischer
        if len(name.split()) >= 2:
            confidence += 0.1

        return min(1.0, confidence)

    def get_recent_activities(self, limit: int = 5) -> List[Dict]:
        """Gibt letzte User-Aktivitäten zurück"""
        return self.session_activities[-limit:]

    def clear_session(self):
        """Löscht Session-Daten"""
        self.session_activities = []
        self.last_extracted = None


# =============================================================================
# ACTIVITY INQUIRY DETECTOR (NEU!)
# =============================================================================

class ActivityInquiryDetector:
    """
    Erkennt flexibel ob User nach Holos Aktivität fragt.
    Nutzt Regex statt starrer Keyword-Liste.
    """

    # Patterns für "was machst du" Varianten
    INQUIRY_PATTERNS = [
        r"was\s+(?:du\s+)?(?:so\s+)?(?:gerade\s+)?machst",
        r"was\s+(?:du\s+)?(?:so\s+)?(?:gerade\s+)?tust",
        r"was\s+(?:du\s+)?(?:so\s+)?(?:gerade\s+)?treibst",
        r"womit\s+(?:du\s+)?(?:dich\s+)?beschäftigst",
        r"bist\s+du\s+(?:gerade\s+)?beschäftigt",
        r"was\s+(?:geht|läuft)\s+(?:bei\s+dir|so)",
        r"was\s+gibt.s\s+(?:bei\s+dir|neues)",
        r"(?:und\s+)?(?:bei\s+)?dir\s*\?",  # "und bei dir?"
        r"was\s+hast\s+du\s+(?:so\s+)?(?:gemacht|getrieben)",
        r"wie\s+(?:war|ist)\s+dein\s+(?:tag|abend|morgen)",
    ]

    @classmethod
    def is_activity_inquiry(cls, text: str) -> Tuple[bool, float]:
        """
        Prüft ob Text eine Aktivitäts-Frage ist.

        Returns:
            Tuple[bool, float]: (ist_inquiry, confidence)
        """
        text_lower = text.lower()

        for pattern in cls.INQUIRY_PATTERNS:
            if re.search(pattern, text_lower):
                # Confidence basierend auf Direktheit
                if "was machst" in text_lower or "was tust" in text_lower:
                    return True, 0.95
                elif "bei dir" in text_lower:
                    return True, 0.85
                else:
                    return True, 0.80

        return False, 0.0


# =============================================================================
# SUBJECT-VERB ANALYZER (NEU! - Konjugationsbasierte Erkennung)
# =============================================================================

class SubjectVerbAnalyzer:
    """
    Analysiert deutsche Saetze auf Subjekt-Verb-Uebereinstimmung.

    Kernidee: Deutsche Verbkonjugation verraet das Subjekt!
    - "ich bin/mache/habe" → 1. Person Singular
    - "du bist/machst/hast" → 2. Person Singular
    - "er/sie/es ist/macht/hat" → 3. Person Singular

    Das ermoeglicht die Unterscheidung:
    - "bist du müde?" → Frage AN Holo (du = 2. Person)
    - "ich bin müde" → Aussage VOM User (ich = 1. Person)
    """

    # Verbkonjugationen: verb_stamm → {endung: person}
    VERB_CONJUGATIONS = {
        # sein (unregelmaessig)
        "bin": "ich",
        "bist": "du",
        "ist": "er/sie/es",
        "sind": "wir/sie/Sie",
        "seid": "ihr",

        # haben (unregelmaessig)
        "habe": "ich",
        "hast": "du",
        "hat": "er/sie/es",
        "haben": "wir/sie/Sie",
        "habt": "ihr",

        # werden
        "werde": "ich",
        "wirst": "du",
        "wird": "er/sie/es",
        "werden": "wir/sie/Sie",
        "werdet": "ihr",

        # koennen
        "kann": "ich/er/sie/es",
        "kannst": "du",
        "koennen": "wir/sie/Sie",
        "koennt": "ihr",

        # muessen
        "muss": "ich/er/sie/es",
        "musst": "du",
        "muessen": "wir/sie/Sie",
        "muesst": "ihr",

        # wollen
        "will": "ich/er/sie/es",
        "willst": "du",
        "wollen": "wir/sie/Sie",
        "wollt": "ihr",

        # moegen/moechten
        "mag": "ich/er/sie/es",
        "magst": "du",
        "moegen": "wir/sie/Sie",
        "moegt": "ihr",
        "moechte": "ich/er/sie/es",
        "moechtest": "du",

        # fuehlen
        "fuehle": "ich",
        "fuehlst": "du",
        "fuehlt": "er/sie/es",
        "fuehlen": "wir/sie/Sie",

        # gehen (wie geht es)
        "gehe": "ich",
        "gehst": "du",
        "geht": "er/sie/es",
        "gehen": "wir/sie/Sie",
    }

    # Regelmaessige Endungen fuer andere Verben
    REGULAR_ENDINGS = {
        "e": "ich",           # ich mache, spiele, schaue
        "st": "du",           # du machst, spielst, schaust
        "t": "er/sie/es",     # er/sie/es macht, spielt, schaut
        "en": "wir/sie/Sie",  # wir/sie machen, spielen, schauen
        "et": "ihr",          # ihr macht (spielt, schaut)
    }

    # Pronomen zu Person-Mapping
    PRONOUN_TO_PERSON = {
        "ich": "1sg",
        "du": "2sg",
        "er": "3sg",
        "sie": "3sg",  # oder 3pl
        "es": "3sg",
        "wir": "1pl",
        "ihr": "2pl",
        "Sie": "formal",
    }

    # Person zu Beschreibung
    PERSON_DESCRIPTIONS = {
        "ich": "user_self",      # User spricht ueber sich
        "du": "asking_holo",     # Frage an Holo
        "er/sie/es": "third_party",
        "wir": "inclusive",
        "ihr": "group",
        "wir/sie/Sie": "plural_or_formal",
    }

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """
        Analysiert einen Satz und bestimmt Subjekt/Perspektive.

        Returns:
            {
                "subject": "ich" | "du" | "er/sie/es" | None,
                "perspective": "user_self" | "asking_holo" | "third_party" | None,
                "verb": str | None,
                "confidence": float,
                "is_question": bool,
                "sentence_type": "statement" | "question" | "imperative"
            }
        """
        text_lower = text.lower().strip()
        words = text_lower.replace("?", " ?").replace("!", " !").split()

        result = {
            "subject": None,
            "perspective": None,
            "verb": None,
            "confidence": 0.0,
            "is_question": "?" in text,
            "sentence_type": cls._detect_sentence_type(text_lower, words)
        }

        # 1. Suche explizites Pronomen
        explicit_pronoun = None
        pronoun_position = -1
        for i, word in enumerate(words):
            clean = word.strip("?,!.")
            if clean in cls.PRONOUN_TO_PERSON:
                explicit_pronoun = clean
                pronoun_position = i
                break

        # 2. Suche Verb und analysiere Konjugation
        verb_found = None
        verb_person = None
        verb_position = -1

        for i, word in enumerate(words):
            clean = word.strip("?,!.")

            # Pruefe bekannte Verben
            if clean in cls.VERB_CONJUGATIONS:
                verb_found = clean
                verb_person = cls.VERB_CONJUGATIONS[clean]
                verb_position = i
                break

            # Pruefe regelmaessige Endungen (nur fuer Woerter > 3 Zeichen)
            if len(clean) > 3:
                for ending, person in cls.REGULAR_ENDINGS.items():
                    if clean.endswith(ending) and not clean.endswith("en" + ending):
                        verb_found = clean
                        verb_person = person
                        verb_position = i
                        break
                if verb_found:
                    break

        result["verb"] = verb_found

        # 3. Bestimme Subjekt basierend auf Evidenz
        if explicit_pronoun:
            result["subject"] = explicit_pronoun
            result["confidence"] = 0.95
        elif verb_person:
            # Keine explizites Pronomen, aber Verb verraet Person
            if "/" not in verb_person:  # Eindeutig
                result["subject"] = verb_person
                result["confidence"] = 0.80
            else:
                # Mehrdeutig (z.B. "kann" = ich ODER er/sie/es)
                result["subject"] = safe_split_access(verb_person, "/", 0, "smart_understanding", "_resolve_subject", default="")
                result["confidence"] = 0.50

        # 4. Validiere Subjekt-Verb-Uebereinstimmung
        if explicit_pronoun and verb_person:
            if explicit_pronoun in verb_person or verb_person.startswith(explicit_pronoun):
                result["confidence"] = 0.98  # Hohe Sicherheit
            else:
                # Mismatch - reduziere Confidence
                result["confidence"] = 0.40

        # 5. Bestimme Perspektive
        if result["subject"]:
            result["perspective"] = cls.PERSON_DESCRIPTIONS.get(
                result["subject"],
                "unknown"
            )

        # 6. Spezialfall: Frage mit "du" → definitiv an Holo gerichtet
        if result["is_question"] and result["subject"] == "du":
            result["perspective"] = "asking_holo"
            result["confidence"] = min(result["confidence"] + 0.1, 1.0)

        # 7. Spezialfall: Aussage mit "ich" → User spricht ueber sich
        if not result["is_question"] and result["subject"] == "ich":
            result["perspective"] = "user_self"
            result["confidence"] = min(result["confidence"] + 0.1, 1.0)

        return result

    @classmethod
    def _detect_sentence_type(cls, text: str, words: List[str]) -> str:
        """Erkennt Satztyp"""
        if "?" in text:
            return "question"

        # Imperativ: Verb am Anfang ohne Pronomen
        if words and words[0] not in cls.PRONOUN_TO_PERSON:
            first_clean = words[0].strip("?,!.")
            if first_clean in cls.VERB_CONJUGATIONS or any(
                first_clean.endswith(e) for e in ["e", "t"]
            ):
                return "imperative"

        return "statement"

    @classmethod
    def is_question_about_holo(cls, text: str) -> Tuple[bool, float]:
        """
        Schnelle Pruefung: Ist das eine Frage ueber Holo?

        "bist du müde?" → True, 0.95
        "ich bin müde" → False, 0.0
        """
        analysis = cls.analyze(text)

        if analysis["perspective"] == "asking_holo":
            return True, analysis["confidence"]

        # Zusaetzliche Patterns fuer Fragen an Holo
        holo_patterns = [
            r"wie\s+(?:geht|gehts|geht.s)\s+(?:es\s+)?dir",
            r"wie\s+fühlst\s+du\s+dich",
            r"und\s+(?:bei\s+)?dir\s*\?",
            r"(?:alles\s+)?(?:klar|gut|ok)\s+bei\s+dir",
        ]

        text_lower = text.lower()
        for pattern in holo_patterns:
            if re.search(pattern, text_lower):
                return True, 0.90

        return False, 0.0

    @classmethod
    def is_user_statement_about_self(cls, text: str) -> Tuple[bool, float]:
        """
        Schnelle Pruefung: Spricht der User ueber sich selbst?

        "ich bin müde" → True, 0.95
        "bist du müde?" → False, 0.0
        """
        analysis = cls.analyze(text)

        if analysis["perspective"] == "user_self":
            return True, analysis["confidence"]

        return False, 0.0


# =============================================================================
# WELLBEING INQUIRY DETECTOR (NEU!)
# =============================================================================

class WellbeingInquiryDetector:
    """
    Erkennt Fragen nach Holos Befinden/Zustand.

    Unterscheidet sich von ActivityInquiryDetector:
    - Activity: "Was machst du?" → Fragt nach AKTIVITAET
    - Wellbeing: "Wie geht es dir?" → Fragt nach BEFINDEN
    """

    # Patterns fuer Befindlichkeits-Fragen AN HOLO
    WELLBEING_PATTERNS = [
        # Allgemeines Befinden
        (r"wie\s+(?:geht|gehts|geht.s)\s+(?:es\s+)?dir", "general_wellbeing", 0.95),
        (r"wie\s+fühlst\s+du\s+dich", "feelings", 0.95),
        (r"(?:alles\s+)?(?:klar|gut|ok|okay)\s+bei\s+dir", "general_wellbeing", 0.85),
        (r"geht\s*(?:e)?s\s+dir\s+(?:gut|schlecht)", "general_wellbeing", 0.90),

        # Spezifische Zustaende
        (r"bist\s+du\s+(?:etwa\s+)?müde", "tiredness", 0.95),
        (r"bist\s+du\s+(?:etwa\s+)?erschöpft", "tiredness", 0.95),
        (r"bist\s+du\s+(?:etwa\s+)?wach", "alertness", 0.90),
        (r"bist\s+du\s+(?:etwa\s+)?glücklich", "happiness", 0.95),
        (r"bist\s+du\s+(?:etwa\s+)?traurig", "sadness", 0.95),
        (r"bist\s+du\s+(?:etwa\s+)?gelangweilt", "boredom", 0.95),
        (r"bist\s+du\s+(?:etwa\s+)?gestresst", "stress", 0.90),
        (r"bist\s+du\s+(?:etwa\s+)?hungrig", "hunger", 0.85),
        (r"bist\s+du\s+(?:etwa\s+)?einsam", "loneliness", 0.90),
        (r"bist\s+du\s+(?:etwa\s+)?aufgeregt", "excitement", 0.90),
        (r"bist\s+du\s+(?:etwa\s+)?nervös", "nervousness", 0.90),

        # Nachfragen mit Klarstellung
        (r"(?:ich\s+)?mein(?:t)?e?\s+(?:ob\s+)?du\s+(?:etwa\s+)?müde\s+bist", "tiredness", 0.98),
        (r"(?:ich\s+)?mein(?:t)?e?\s+(?:ob\s+)?du", "clarification", 0.85),
        (r"ob\s+du\s+(?:etwa\s+)?\w+\s+bist", "state_question", 0.90),

        # Fragen mit "und du?"
        (r"und\s+(?:bei\s+)?dir\s*\??\s*$", "reciprocal", 0.80),
        (r"(?:was\s+ist\s+)?mit\s+dir\s*\?", "reciprocal", 0.80),
    ]

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt ob nach Holos Befinden gefragt wird.

        Returns:
            {
                "is_wellbeing_inquiry": bool,
                "wellbeing_type": str | None,
                "confidence": float,
                "pattern_matched": str | None
            }
        """
        text_lower = text.lower().strip()

        result = {
            "is_wellbeing_inquiry": False,
            "wellbeing_type": None,
            "confidence": 0.0,
            "pattern_matched": None
        }

        # Pruefe alle Patterns
        best_match = None
        best_confidence = 0.0

        for pattern, wellbeing_type, confidence in cls.WELLBEING_PATTERNS:
            if re.search(pattern, text_lower):
                if confidence > best_confidence:
                    best_match = (pattern, wellbeing_type, confidence)
                    best_confidence = confidence

        if best_match:
            result["is_wellbeing_inquiry"] = True
            result["wellbeing_type"] = best_match[1]
            result["confidence"] = best_match[2]
            result["pattern_matched"] = best_match[0]

            # Zusaetzliche Validierung mit SubjectVerbAnalyzer
            sv_analysis = SubjectVerbAnalyzer.analyze(text)
            if sv_analysis["perspective"] == "asking_holo":
                result["confidence"] = min(result["confidence"] + 0.05, 1.0)
            elif sv_analysis["perspective"] == "user_self":
                # Widerspruch! Reduziere Confidence stark
                result["confidence"] = max(result["confidence"] - 0.4, 0.1)
                result["is_wellbeing_inquiry"] = result["confidence"] > 0.5

        return result

    @classmethod
    def is_wellbeing_inquiry(cls, text: str) -> Tuple[bool, float]:
        """Kurzform fuer schnelle Pruefung"""
        result = cls.detect(text)
        return result["is_wellbeing_inquiry"], result["confidence"]


# =============================================================================
# USER EMOTION DETECTOR (NEU!)
# =============================================================================

class UserEmotionDetector:
    """
    Erkennt wenn der User seinen eigenen emotionalen Zustand mitteilt.

    WICHTIG: Unterscheidet von Fragen an Holo!
    - "ich bin müde" → User teilt seinen Zustand mit
    - "bist du müde?" → Frage an Holo (NICHT hier behandelt!)
    """

    # Patterns fuer User-Emotionen (erfordern "ich")
    USER_EMOTION_PATTERNS = [
        # Muedigkeit
        (r"ich\s+bin\s+(?:so\s+)?(?:ziemlich\s+)?müde", "tired", 0.95),
        (r"ich\s+bin\s+(?:so\s+)?(?:total\s+)?erschöpft", "exhausted", 0.95),
        (r"ich\s+bin\s+(?:so\s+)?kaputt", "exhausted", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?fertig", "exhausted", 0.85),
        (r"ich\s+bin\s+(?:so\s+)?platt", "exhausted", 0.90),

        # Positive Emotionen
        (r"ich\s+bin\s+(?:so\s+)?(?:richtig\s+)?glücklich", "happy", 0.95),
        (r"ich\s+bin\s+(?:so\s+)?(?:total\s+)?happy", "happy", 0.95),
        (r"ich\s+(?:freu|freue)\s+mich", "happy", 0.90),
        (r"mir\s+geht.?s?\s+(?:super|gut|toll)", "happy", 0.85),
        (r"ich\s+bin\s+(?:so\s+)?aufgeregt", "excited", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?begeistert", "excited", 0.90),

        # Negative Emotionen
        (r"ich\s+bin\s+(?:so\s+)?(?:ziemlich\s+)?traurig", "sad", 0.95),
        (r"ich\s+bin\s+(?:so\s+)?(?:total\s+)?down", "sad", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?deprimiert", "sad", 0.90),
        (r"mir\s+geht.?s?\s+(?:schlecht|nicht\s+gut|mies)", "sad", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?gestresst", "stressed", 0.95),
        (r"ich\s+hab(?:e)?\s+(?:so\s+)?(?:viel\s+)?stress", "stressed", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?(?:richtig\s+)?wütend", "angry", 0.95),
        (r"ich\s+bin\s+(?:so\s+)?sauer", "angry", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?genervt", "annoyed", 0.90),

        # Andere Zustaende
        (r"ich\s+bin\s+(?:so\s+)?gelangweilt", "bored", 0.90),
        (r"mir\s+ist\s+(?:so\s+)?langweilig", "bored", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?einsam", "lonely", 0.95),
        (r"ich\s+(?:fühle|fühl)\s+mich\s+(?:so\s+)?allein", "lonely", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?nervös", "nervous", 0.90),
        (r"ich\s+bin\s+(?:so\s+)?ängstlich", "anxious", 0.90),
        (r"ich\s+hab(?:e)?\s+(?:ein\s+bisschen\s+)?angst", "anxious", 0.85),
    ]

    # Emotion zu Reaktions-Typ Mapping
    EMOTION_RESPONSE_TYPE = {
        "tired": "show_care",
        "exhausted": "show_care",
        "happy": "share_joy",
        "excited": "share_excitement",
        "sad": "comfort",
        "stressed": "comfort",
        "angry": "calm_down",
        "annoyed": "empathize",
        "bored": "suggest_activity",
        "lonely": "comfort",
        "nervous": "reassure",
        "anxious": "reassure",
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt User-Emotionen.

        Returns:
            {
                "user_shared_emotion": bool,
                "emotion": str | None,
                "intensity": float,  # 0-1
                "response_type": str | None,
                "confidence": float
            }
        """
        text_lower = text.lower().strip()

        result = {
            "user_shared_emotion": False,
            "emotion": None,
            "intensity": 0.5,
            "response_type": None,
            "confidence": 0.0
        }

        # Zusaetzliche Validierung: Ist es wirklich eine User-Aussage?
        sv_analysis = SubjectVerbAnalyzer.analyze(text)

        # Wenn es eine Frage an Holo ist, ignorieren
        if sv_analysis["perspective"] == "asking_holo":
            return result

        # Pruefe Emotion-Patterns
        best_match = None
        best_confidence = 0.0

        for pattern, emotion, confidence in cls.USER_EMOTION_PATTERNS:
            if re.search(pattern, text_lower):
                if confidence > best_confidence:
                    best_match = (pattern, emotion, confidence)
                    best_confidence = confidence

        if best_match:
            result["user_shared_emotion"] = True
            result["emotion"] = best_match[1]
            result["confidence"] = best_match[2]
            result["response_type"] = cls.EMOTION_RESPONSE_TYPE.get(
                best_match[1], "empathize"
            )

            # Intensitaet schaetzen
            if "so " in text_lower or "total " in text_lower or "richtig " in text_lower:
                result["intensity"] = 0.8
            elif "ziemlich " in text_lower or "sehr " in text_lower:
                result["intensity"] = 0.7
            elif "ein bisschen" in text_lower or "etwas " in text_lower:
                result["intensity"] = 0.3
            else:
                result["intensity"] = 0.5

            # Erhoehe Confidence wenn SubjectVerbAnalyzer bestaetigt
            if sv_analysis["perspective"] == "user_self":
                result["confidence"] = min(result["confidence"] + 0.05, 1.0)

        return result

    @classmethod
    def is_user_emotion(cls, text: str) -> Tuple[bool, str, float]:
        """
        Kurzform fuer schnelle Pruefung.

        Returns:
            Tuple[bool, str, float]: (hat_emotion, emotion_typ, confidence)
        """
        result = cls.detect(text)
        return (
            result["user_shared_emotion"],
            result["emotion"] or "",
            result["confidence"]
        )


# =============================================================================
# SARCASM DETECTOR - Erkennt Sarkasmus und Ironie
# =============================================================================

class SarcasmDetector:
    """
    Erkennt Sarkasmus und Ironie in deutschen Saetzen.

    Sarkasmus invertiert die emotionale Bedeutung:
    - "Oh super, noch mehr Arbeit!" → Klingt positiv, ist negativ
    - "Na toll, das hat ja super geklappt" → Negativ gemeint
    - "Wow, wie überraschend..." → Keine echte Überraschung
    """

    # Sarkasmus-Marker (Wörter die oft sarkastisch verwendet werden)
    SARCASM_MARKERS = [
        r"\bna\s+toll\b",
        r"\bna\s+super\b",
        r"\bna\s+klasse\b",
        r"\bna\s+wunderbar\b",
        r"\bna\s+prima\b",
        r"\boh\s+(?:wie\s+)?toll\b",
        r"\boh\s+(?:wie\s+)?super\b",
        r"\boh\s+(?:wie\s+)?wunderbar\b",
        r"\bja\s+(?:ganz\s+)?toll\b",
        r"\bja\s+(?:ganz\s+)?super\b",
        r"\bwie\s+(?:überraschend|schön|toll|nett)\s*\.{2,}",  # Mit Auslassungspunkten
        r"\bwow\s*\.{2,}",
        r"\bsuper\s*\.{2,}",
        r"\btoll\s*\.{2,}",
    ]

    # Kontrast-Patterns (positives Wort + negative Situation)
    CONTRAST_PATTERNS = [
        # "super/toll/klasse" + negative Situation
        (r"\b(?:super|toll|klasse|prima|wunderbar|großartig)\b",
         r"\b(?:arbeit|stress|problem|fehler|kaputt|versagt|verloren|schlecht)\b"),
        # Übertriebenes Lob in negativem Kontext
        (r"\b(?:genial|perfekt|fantastisch|brillant)\b",
         r"\b(?:nicht|kein|wieder|schon\s+wieder|natürlich|ausgerechnet)\b"),
    ]

    # Typische sarkastische Phrasen
    SARCASTIC_PHRASES = [
        r"das\s+hat\s+(?:ja\s+)?(?:super|toll|wunderbar)\s+geklappt",
        r"(?:ja\s+)?klar\s*,?\s*(?:doch|natürlich)",
        r"(?:ach\s+)?wirklich\s*\??\s*(?:echt\s+)?jetzt\s*\??",
        r"aber\s+(?:sowas\s+von|total|echt)\s+(?:nicht|kein)",
        r"als\s+ob\b",
        r"genau\s+(?:mein|das)\s+(?:ding|humor)",
        r"(?:schon\s+)?wieder\s+(?:mal|einmal)\s*[!.]+",
        r"natürlich\s+(?:mal\s+)?wieder\b",
        r"ausgerechnet\s+(?:jetzt|heute|ich|du)\b",
        r"(?:das\s+)?war\s*(?:'s|es)?\s*(?:ja\s+)?(?:klar|logisch|typisch)",
        r"(?:ach\s+)?(?:was\s+)?du\s+nicht\s+sagst",
        r"nein\s*[!,]\s*(?:wirklich|echt)\s*\?",
        r"(?:ja\s+)?(?:nee|ne)\s*,?\s*(?:is|ist)\s+klar",
        r"(?:wow|boah)\s*,?\s*(?:echt\s+)?(?:beeindruckend|erstaunlich)",
    ]

    # Interpunktions-Indikatoren
    PUNCTUATION_PATTERNS = [
        r"\.{3,}$",          # Auslassungspunkte am Ende
        r"!{2,}$",           # Mehrere Ausrufezeichen
        r"\?\!|\!\?",        # Gemischte Satzzeichen
        r"\.\.\.\s*\?+$",    # ... gefolgt von Fragezeichen
    ]

    # Emoji/Text-Emoticons die Sarkasmus signalisieren
    SARCASM_EMOTICONS = [
        r":\)|;\)|:\-\)",    # Smiley nach negativem Inhalt
        r"🙄|😒|😏|🤦|💀",   # Sarkasmus-Emojis
    ]

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt Sarkasmus in Text.

        Returns:
            {
                "is_sarcastic": bool,
                "confidence": float,
                "markers_found": List[str],
                "inverted_sentiment": str | None,  # Was wirklich gemeint ist
                "original_sentiment": str | None,  # Wie es klingt
            }
        """
        text_lower = text.lower().strip()

        result = {
            "is_sarcastic": False,
            "confidence": 0.0,
            "markers_found": [],
            "inverted_sentiment": None,
            "original_sentiment": None,
        }

        confidence = 0.0
        markers = []

        # 1. Sarkasmus-Marker prüfen
        for pattern in cls.SARCASM_MARKERS:
            if re.search(pattern, text_lower):
                confidence += 0.35
                markers.append(f"marker:{pattern[:20]}")

        # 2. Sarkastische Phrasen
        for pattern in cls.SARCASTIC_PHRASES:
            if re.search(pattern, text_lower):
                confidence += 0.45
                markers.append(f"phrase:{pattern[:25]}")

        # 3. Kontrast-Patterns (positiv + negativ zusammen)
        for pos_pattern, neg_pattern in cls.CONTRAST_PATTERNS:
            if re.search(pos_pattern, text_lower) and re.search(neg_pattern, text_lower):
                confidence += 0.4
                markers.append("contrast:pos+neg")

        # 4. Interpunktion
        for pattern in cls.PUNCTUATION_PATTERNS:
            if re.search(pattern, text):
                confidence += 0.15
                markers.append("punctuation")
                break

        # 5. Sarkasmus-Emoticons nach positivem Text
        positive_words = re.search(r"\b(?:super|toll|klasse|prima|gut|schön)\b", text_lower)
        for pattern in cls.SARCASM_EMOTICONS:
            if re.search(pattern, text) and positive_words:
                confidence += 0.25
                markers.append("emoticon_contrast")
                break

        # 6. Länge und Großschreibung
        # Kurze Ausrufe wie "Super." oder "TOLL." sind oft sarkastisch
        if len(text.split()) <= 3:
            if re.match(r"^[A-ZÄÖÜ]{2,}", text) or text.endswith("."):
                if re.search(r"\b(?:super|toll|klasse|prima|wunderbar|genial)\b", text_lower):
                    confidence += 0.3
                    markers.append("short_sarcastic")

        # Confidence begrenzen
        confidence = min(confidence, 1.0)

        # Ergebnis bestimmen
        if confidence >= 0.4:
            result["is_sarcastic"] = True
            result["confidence"] = confidence
            result["markers_found"] = markers

            # Sentiment invertieren
            if re.search(r"\b(?:super|toll|klasse|prima|gut|schön|wunderbar|genial|perfekt)\b", text_lower):
                result["original_sentiment"] = "positive"
                result["inverted_sentiment"] = "negative"
            elif re.search(r"\b(?:schlecht|mies|furchtbar|schrecklich)\b", text_lower):
                result["original_sentiment"] = "negative"
                result["inverted_sentiment"] = "positive"  # Selten, aber möglich

        return result

    @classmethod
    def is_sarcastic(cls, text: str) -> Tuple[bool, float]:
        """
        Schnelle Prüfung ob Text sarkastisch ist.

        Returns:
            Tuple[bool, float]: (ist_sarkastisch, confidence)
        """
        result = cls.detect(text)
        return result["is_sarcastic"], result["confidence"]

    @classmethod
    def get_true_sentiment(cls, text: str, apparent_sentiment: str) -> str:
        """
        Gibt das wahre Sentiment zurück (invertiert bei Sarkasmus).

        Args:
            text: Der Text
            apparent_sentiment: Das scheinbare Sentiment ("positive"/"negative")

        Returns:
            Das wahre Sentiment
        """
        result = cls.detect(text)
        if result["is_sarcastic"] and result["confidence"] >= 0.5:
            # Invertiere Sentiment
            if apparent_sentiment == "positive":
                return "negative"
            elif apparent_sentiment == "negative":
                return "positive"
        return apparent_sentiment


# =============================================================================
# NEGATION HANDLER - Erkennt Verneinungen
# =============================================================================

class NegationHandler:
    """
    Erkennt und behandelt Verneinungen in deutschen Saetzen.

    WICHTIG fuer korrekte Intent-Erkennung:
    - "ich bin müde" → User ist muede
    - "ich bin NICHT müde" → User ist NICHT muede (komplett andere Bedeutung!)
    - "ich bin gar nicht müde" → Verstaerkte Verneinung

    NEU: Scope-Analyse für komplexe Sätze:
    - "Ich glaube nicht, dass du müde bist" → Verneint: "du müde bist"
    - "Er ist nicht müde, sondern hungrig" → Verneint nur: "müde"
    """

    # Verneinungswoerter mit Staerke (0-1)
    NEGATION_WORDS = {
        # Starke Verneinung
        "nicht": 1.0,
        "kein": 1.0,
        "keine": 1.0,
        "keinen": 1.0,
        "keiner": 1.0,
        "keines": 1.0,
        "nie": 1.0,
        "niemals": 1.0,
        "nimmer": 1.0,
        "nix": 1.0,  # Umgangssprache
        "nüscht": 1.0,  # Dialekt
        "nit": 1.0,  # Süddeutsch
        "ned": 1.0,  # Bayrisch
        "net": 1.0,  # Österreichisch

        # Verstaerkte Verneinung
        "gar nicht": 1.2,
        "überhaupt nicht": 1.2,
        "absolut nicht": 1.2,
        "keineswegs": 1.1,
        "keinesfalls": 1.1,
        "auf keinen fall": 1.2,
        "noch nie": 1.1,
        "kein bisschen": 1.2,
        "kein stück": 1.2,
        "null": 1.0,
        "null komma null": 1.2,
        "beim besten willen nicht": 1.2,

        # Abschwaechung/Teilverneinung
        "kaum": 0.7,
        "wenig": 0.5,
        "selten": 0.6,
        "nicht wirklich": 0.8,
        "nicht so": 0.7,
        "nicht besonders": 0.6,
        "nicht unbedingt": 0.6,
        "eher nicht": 0.75,
        "wohl kaum": 0.8,
    }

    # Doppelte Verneinung (hebt sich auf)
    DOUBLE_NEGATION_PATTERNS = [
        r"nicht\s+un",  # "nicht unglücklich" = glücklich
        r"kein\s+un",   # "kein Unglück" = Glück
        r"nie\s+nicht", # umgangssprachlich
        r"nichts\s+un",
    ]

    # Scope-Begrenzer: Diese Wörter begrenzen den Scope der Verneinung
    SCOPE_LIMITERS = {
        "sondern": "contrast",  # "nicht A, sondern B" → nur A ist verneint
        "aber": "contrast",     # "nicht A, aber B"
        "jedoch": "contrast",
        "dass": "subordinate",  # Nebensatz beginnt
        "ob": "subordinate",
        "weil": "subordinate",
        "obwohl": "subordinate",
        ",": "clause_boundary",
    }

    # Phrasen wo Verneinung auf Nebensatz wirkt
    NEGATION_TRANSFER_PATTERNS = [
        r"(?:glaube|denke|meine|finde)\s+nicht,?\s+dass",  # "glaube nicht, dass X"
        r"(?:bin|ist|sind)\s+(?:mir\s+)?nicht\s+sicher,?\s+(?:ob|dass)",
        r"bezweifle,?\s+dass",
        r"kann\s+(?:mir\s+)?nicht\s+vorstellen,?\s+dass",
    ]

    # Feste Phrasen wo "nicht" keine echte Verneinung ist
    FALSE_NEGATION_PATTERNS = [
        r"nicht\s+wahr\??",  # Bestätigungsfrage
        r"warum\s+nicht",    # Vorschlag
        r"wieso\s+nicht",
        r"oder\s+(?:etwa\s+)?nicht",  # Tag-Question
        r"wenn\s+nicht",     # Bedingung
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """
        Analysiert Verneinungen im Text mit Scope-Analyse.

        Returns:
            {
                "has_negation": bool,
                "negation_strength": float,  # 0-1.2
                "negation_words": List[str],
                "negated_element": str | None,  # Was wird verneint
                "negation_scope": str | None,  # Der Bereich der verneint wird
                "is_double_negation": bool,  # Hebt sich auf
                "is_false_negation": bool,  # "nicht wahr?" etc.
                "negation_transfers": bool,  # Verneinung wirkt auf Nebensatz
                "effective_polarity": str,  # "positive", "negative", "neutral"
            }
        """
        text_lower = text.lower().strip()

        result = {
            "has_negation": False,
            "negation_strength": 0.0,
            "negation_words": [],
            "negated_element": None,
            "negation_scope": None,
            "is_double_negation": False,
            "is_false_negation": False,
            "negation_transfers": False,
            "effective_polarity": "neutral",
        }

        # 1. Prüfe auf falsche Verneinungen (nicht wahr?, warum nicht, etc.)
        for pattern in cls.FALSE_NEGATION_PATTERNS:
            if re.search(pattern, text_lower):
                result["is_false_negation"] = True
                # Keine echte Verneinung, früh zurückkehren
                return result

        # 2. Pruefe auf doppelte Verneinung
        for pattern in cls.DOUBLE_NEGATION_PATTERNS:
            if re.search(pattern, text_lower):
                result["is_double_negation"] = True
                result["effective_polarity"] = "positive"
                break

        # 3. Prüfe auf Negation-Transfer (Verneinung wirkt auf Nebensatz)
        for pattern in cls.NEGATION_TRANSFER_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                result["negation_transfers"] = True
                # Finde den Nebensatz nach "dass"
                dass_match = re.search(r"dass\s+(.+?)(?:\.|$)", text_lower)
                if dass_match:
                    result["negation_scope"] = dass_match.group(1).strip()
                break

        # 4. Finde Verneinungswoerter
        found_negations = []
        max_strength = 0.0

        # Zuerst laengere Phrasen pruefen (z.B. "gar nicht" vor "nicht")
        sorted_negations = sorted(
            cls.NEGATION_WORDS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for negation, strength in sorted_negations:
            if negation in text_lower:
                # Pruefe dass es nicht schon als Teil einer laengeren Phrase gefunden wurde
                already_found = any(negation in found for found in found_negations)
                if not already_found:
                    found_negations.append(negation)
                    if strength > max_strength:
                        max_strength = strength

        if found_negations:
            result["has_negation"] = True
            result["negation_strength"] = max_strength
            result["negation_words"] = found_negations

            # 5. Scope-Analyse: Was genau wird verneint?
            # Suche nach "nicht X, sondern Y" Pattern
            sondern_match = re.search(
                r"nicht\s+(\w+(?:\s+\w+)?),?\s+sondern\s+(\w+)",
                text_lower
            )
            if sondern_match:
                result["negated_element"] = sondern_match.group(1)
                result["negation_scope"] = sondern_match.group(1)  # Nur erster Teil
            else:
                # Standard: "nicht" + Adjektiv/Verb
                negated_match = re.search(
                    r"(?:nicht|kein\w*|nie(?:mals)?)\s+(\w+(?:\s+\w+)?)",
                    text_lower
                )
                if negated_match:
                    result["negated_element"] = negated_match.group(1)

                # Bestimme Scope bis zum nächsten Scope-Begrenzer
                for limiter, limit_type in cls.SCOPE_LIMITERS.items():
                    if limiter in text_lower:
                        parts = text_lower.split(limiter, 1)
                        if "nicht" in parts[0] or "kein" in parts[0]:
                            result["negation_scope"] = parts[0].strip()
                            break

            # 6. Bestimme effektive Polaritaet
            if not result["is_double_negation"]:
                result["effective_polarity"] = "negative"

        return result

    @classmethod
    def get_negation_scope(cls, text: str) -> Tuple[str, str]:
        """
        Gibt den Bereich zurück, der verneint wird.

        Returns:
            Tuple[str, str]: (verneintersBereich, restDesSatzes)
        """
        result = cls.analyze(text)
        scope = result.get("negation_scope") or result.get("negated_element") or ""
        rest = text.lower().replace(scope, "", 1).strip() if scope else text
        return (scope, rest)

    @classmethod
    def negate_emotion(cls, emotion: str, negation_strength: float) -> Tuple[str, float]:
        """
        Kehrt eine Emotion um basierend auf Verneinung.

        Args:
            emotion: Die urspruengliche Emotion
            negation_strength: Staerke der Verneinung

        Returns:
            Tuple[str, float]: (neue_emotion, confidence)
        """
        # Emotion-Gegensatz-Paare
        OPPOSITES = {
            "happy": "unhappy",
            "sad": "not_sad",
            "tired": "energetic",
            "exhausted": "energetic",
            "stressed": "relaxed",
            "angry": "calm",
            "bored": "engaged",
            "lonely": "not_lonely",
            "anxious": "calm",
            "nervous": "calm",
            "excited": "calm",
        }

        if negation_strength >= 0.8:
            # Starke Verneinung: Emotion umkehren
            opposite = OPPOSITES.get(emotion, f"not_{emotion}")
            return (opposite, 0.85)
        elif negation_strength >= 0.5:
            # Teilverneinung: Emotion abschwaechen
            return (f"slightly_{emotion}", 0.6)
        else:
            # Schwache Verneinung: Emotion bleibt, aber Confidence sinkt
            return (emotion, 0.4)


# =============================================================================
# MODAL VERB HANDLER - Erkennt Modalverben und deren Bedeutung
# =============================================================================

class ModalVerbHandler:
    """
    Erkennt deutsche Modalverben und deren Einfluss auf die Aussage.

    Modalverben ändern die Bedeutung grundlegend:
    - "Ich gehe" → Fakt/Absicht
    - "Ich muss gehen" → Zwang/Notwendigkeit
    - "Ich sollte gehen" → Empfehlung/Pflicht
    - "Ich könnte gehen" → Möglichkeit
    - "Ich will gehen" → Wunsch
    - "Ich darf gehen" → Erlaubnis
    - "Ich mag gehen" → Vorliebe
    """

    # Modalverben mit Konjugationen
    MODAL_VERBS = {
        "müssen": {
            "conjugations": ["muss", "musst", "müssen", "müsst", "musste", "müsste", "müssten"],
            "meaning": "necessity",  # Notwendigkeit/Zwang
            "strength": 0.9,
            "implies_external_pressure": True,
        },
        "sollen": {
            "conjugations": ["soll", "sollst", "sollen", "sollt", "sollte", "sollten"],
            "meaning": "obligation",  # Empfehlung/Pflicht
            "strength": 0.7,
            "implies_external_pressure": True,
        },
        "können": {
            "conjugations": ["kann", "kannst", "können", "könnt", "konnte", "könnte", "könnten"],
            "meaning": "possibility",  # Möglichkeit/Fähigkeit
            "strength": 0.5,
            "implies_external_pressure": False,
        },
        "wollen": {
            "conjugations": ["will", "willst", "wollen", "wollt", "wollte", "wollten"],
            "meaning": "desire",  # Wunsch/Absicht
            "strength": 0.8,
            "implies_external_pressure": False,
        },
        "dürfen": {
            "conjugations": ["darf", "darfst", "dürfen", "dürft", "durfte", "dürfte", "dürften"],
            "meaning": "permission",  # Erlaubnis
            "strength": 0.6,
            "implies_external_pressure": True,
        },
        "mögen": {
            "conjugations": ["mag", "magst", "mögen", "mögt", "mochte", "möchte", "möchten"],
            "meaning": "preference",  # Vorliebe/Wunsch
            "strength": 0.6,
            "implies_external_pressure": False,
        },
    }

    # Konjunktiv II signalisiert Irrealis/Wunsch
    KONJUNKTIV_MARKERS = [
        "würde", "würdest", "würden", "würdet",
        "wäre", "wärst", "wären", "wärt",
        "hätte", "hättest", "hätten", "hättet",
        "könnte", "müsste", "sollte", "dürfte", "möchte",
    ]

    # Phrasen die auf Modalität hinweisen
    MODAL_PHRASES = {
        r"ich\s+(?:muss|müsste)\s+(?:mal|eigentlich)\s+(?:schlafen|gehen|aufhören)": "signal_end",
        r"ich\s+sollte\s+(?:eigentlich|wohl)\s+(?:schlafen|gehen|aufhören|los)": "signal_end",
        r"es\s+wird\s+zeit(?:,?\s+dass)": "signal_end",
        r"ich\s+(?:muss|sollte)\s+(?:langsam|bald|mal)\s+(?:los|weg|gehen)": "signal_end",
        r"ich\s+(?:will|möchte)\s+(?:gerne?)?\s+(?:wissen|verstehen|lernen)": "request_info",
        r"ich\s+(?:kann|könnte)\s+(?:dir|ihnen)\s+(?:helfen|zeigen|erklären)": "offer_help",
        r"du\s+(?:musst|solltest)\s+(?:nicht|keine?)": "reassurance",
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt Modalverben und deren Bedeutung.

        Returns:
            {
                "has_modal": bool,
                "modal_verb": str | None,
                "modal_meaning": str | None,  # necessity, obligation, possibility, desire, permission, preference
                "is_konjunktiv": bool,  # Konjunktiv II (Irrealis)
                "strength": float,
                "implies_external_pressure": bool,
                "implicit_intent": str | None,  # z.B. "signal_end"
                "confidence": float,
            }
        """
        text_lower = text.lower().strip()

        result = {
            "has_modal": False,
            "modal_verb": None,
            "modal_meaning": None,
            "is_konjunktiv": False,
            "strength": 0.5,
            "implies_external_pressure": False,
            "implicit_intent": None,
            "confidence": 0.0,
        }

        # Prüfe Modal-Phrasen zuerst (spezifischer)
        for pattern, intent in cls.MODAL_PHRASES.items():
            if re.search(pattern, text_lower):
                result["implicit_intent"] = intent
                result["confidence"] = 0.85

        # Prüfe auf Konjunktiv
        for marker in cls.KONJUNKTIV_MARKERS:
            if re.search(rf"\b{marker}\b", text_lower):
                result["is_konjunktiv"] = True
                break

        # Suche Modalverben
        for verb_infinitive, info in cls.MODAL_VERBS.items():
            for conjugation in info["conjugations"]:
                if re.search(rf"\b{conjugation}\b", text_lower):
                    result["has_modal"] = True
                    result["modal_verb"] = verb_infinitive
                    result["modal_meaning"] = info["meaning"]
                    result["strength"] = info["strength"]
                    result["implies_external_pressure"] = info["implies_external_pressure"]
                    result["confidence"] = 0.9

                    # Konjunktiv II reduziert Stärke (Möglichkeit statt Fakt)
                    if result["is_konjunktiv"]:
                        result["strength"] *= 0.7

                    return result

        return result

    @classmethod
    def get_modal_meaning(cls, text: str) -> Tuple[str, float]:
        """
        Kurzform: Gibt Modalverb-Bedeutung zurück.

        Returns:
            Tuple[str, float]: (bedeutung, confidence)
        """
        result = cls.detect(text)
        return result["modal_meaning"] or "none", result["confidence"]

    @classmethod
    def implies_farewell(cls, text: str) -> bool:
        """Prüft ob Text einen impliziten Abschied signalisiert."""
        result = cls.detect(text)
        return result["implicit_intent"] == "signal_end"


# =============================================================================
# CONDITIONAL PATTERN DETECTOR - Erkennt bedingte Aussagen
# =============================================================================

class ConditionalPatternDetector:
    """
    Erkennt bedingte Aussagen (wenn/falls) und deren Einfluss.

    Bedingte Aussagen reduzieren die Verbindlichkeit:
    - "Hilf mir!" → Direkte Anfrage (1.0)
    - "Wenn du Zeit hast, hilf mir" → Bedingte Anfrage (0.6)
    - "Falls es möglich wäre..." → Sehr höfliche Anfrage (0.4)
    """

    # Bedingungs-Einleiter mit Höflichkeits-/Verbindlichkeitsstufe
    CONDITIONAL_MARKERS = {
        # Neutrale Bedingungen
        r"\bwenn\b": {"type": "neutral", "reduces_strength": 0.3},
        r"\bfalls\b": {"type": "tentative", "reduces_strength": 0.4},
        r"\bsofern\b": {"type": "formal", "reduces_strength": 0.3},
        r"\bsoweit\b": {"type": "formal", "reduces_strength": 0.3},

        # Höfliche/Abschwächende Bedingungen
        r"\bwenn\s+(?:es\s+)?(?:dir|ihnen)\s+(?:nichts\s+ausmacht|passt|recht\s+ist)": {
            "type": "polite", "reduces_strength": 0.5
        },
        r"\bwenn\s+(?:du|sie)\s+zeit\s+(?:hast|haben|hättest|hätten)": {
            "type": "polite", "reduces_strength": 0.4
        },
        r"\bfalls\s+(?:es\s+)?möglich\s+(?:ist|wäre)": {
            "type": "very_polite", "reduces_strength": 0.5
        },
        r"\bwenn\s+(?:es\s+)?(?:nicht\s+zu\s+viel|keine\s+umstände)": {
            "type": "very_polite", "reduces_strength": 0.5
        },

        # Irreale Bedingungen (Konjunktiv)
        r"\bwenn\s+ich\s+(?:dürfte|könnte|würde)": {
            "type": "hypothetical", "reduces_strength": 0.4
        },
        r"\bwärst\s+du\s+so\s+(?:nett|lieb|freundlich)": {
            "type": "very_polite", "reduces_strength": 0.5
        },
    }

    # Temporal vs. Konditional unterscheiden
    TEMPORAL_MARKERS = [
        r"\bwenn\s+(?:ich\s+)?(?:nach\s+hause|da\s+bin|ankomme|fertig\s+bin)",
        r"\bwenn\s+(?:es\s+)?(?:morgen|später|nachher|gleich)",
    ]

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt bedingte Aussagen.

        Returns:
            {
                "is_conditional": bool,
                "condition_type": str | None,  # neutral, tentative, polite, very_polite, hypothetical
                "strength_reduction": float,  # Wie sehr wird die Aussage abgeschwächt
                "is_temporal": bool,  # Temporal statt konditional
                "politeness_level": str,  # direct, normal, polite, very_polite
                "confidence": float,
            }
        """
        text_lower = text.lower().strip()

        result = {
            "is_conditional": False,
            "condition_type": None,
            "strength_reduction": 0.0,
            "is_temporal": False,
            "politeness_level": "direct",
            "confidence": 0.0,
        }

        # Prüfe erst auf temporale Verwendung
        for pattern in cls.TEMPORAL_MARKERS:
            if re.search(pattern, text_lower):
                result["is_temporal"] = True

        # Suche Bedingungs-Marker (sortiert nach Spezifität)
        sorted_markers = sorted(
            cls.CONDITIONAL_MARKERS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for pattern, info in sorted_markers:
            if re.search(pattern, text_lower):
                result["is_conditional"] = True
                result["condition_type"] = info["type"]
                result["strength_reduction"] = info["reduces_strength"]
                result["confidence"] = 0.85

                # Höflichkeitsstufe bestimmen
                if info["type"] in ["very_polite", "hypothetical"]:
                    result["politeness_level"] = "very_polite"
                elif info["type"] == "polite":
                    result["politeness_level"] = "polite"
                else:
                    result["politeness_level"] = "normal"

                break

        return result

    @classmethod
    def adjust_request_strength(cls, text: str, base_strength: float = 1.0) -> float:
        """
        Passt die Stärke einer Anfrage basierend auf Bedingungen an.

        Args:
            text: Der Text
            base_strength: Basis-Stärke (1.0 = direkte Anfrage)

        Returns:
            Angepasste Stärke (0.0-1.0)
        """
        result = cls.detect(text)
        if result["is_conditional"] and not result["is_temporal"]:
            return base_strength * (1.0 - result["strength_reduction"])
        return base_strength


# =============================================================================
# INTENSITY ANALYZER - Analysiert Emotionsstaerke
# =============================================================================

class IntensityAnalyzer:
    """
    Analysiert die Intensitaet/Staerke von Aussagen.

    Stufen:
    1. minimal (0.0-0.2): "ein bisschen", "etwas", "leicht"
    2. niedrig (0.2-0.4): "etwas", "ein wenig"
    3. mittel (0.4-0.6): keine Modifikatoren (Standard)
    4. hoch (0.6-0.8): "ziemlich", "sehr", "echt"
    5. extrem (0.8-1.0): "total", "mega", "extrem", "unglaublich"
    """

    # Intensitaets-Modifikatoren mit Werten
    INTENSITY_MODIFIERS = {
        # Minimal (0.1-0.2)
        "ein bisschen": 0.15,
        "ein wenig": 0.2,
        "etwas": 0.2,
        "leicht": 0.15,
        "minimal": 0.1,
        "ganz leicht": 0.1,
        "n bisschen": 0.15,  # Umgangssprache
        "bisschen": 0.15,
        "bissl": 0.15,  # Süddeutsch
        "a bissl": 0.15,  # Bayrisch
        "bisserl": 0.15,  # Österreichisch

        # Niedrig (0.25-0.4)
        "nicht so": 0.3,
        "nicht besonders": 0.25,
        "nicht wirklich": 0.35,
        "halbwegs": 0.4,
        "so halbwegs": 0.35,
        "so lala": 0.35,
        "geht so": 0.35,
        "na ja": 0.3,
        "naja": 0.3,

        # Mittel-Hoch (0.55-0.65)
        "schon": 0.6,
        "durchaus": 0.6,
        "definitiv": 0.65,
        "auf jeden fall": 0.65,

        # Hoch (0.65-0.8)
        "ziemlich": 0.7,
        "sehr": 0.75,
        "echt": 0.7,
        "wirklich": 0.7,
        "richtig": 0.75,
        "ganz schön": 0.7,
        "ordentlich": 0.65,
        "verdammt": 0.75,
        "verflucht": 0.75,
        "sau": 0.75,  # "saumüde"
        "ur": 0.75,   # Österreichisch: "urmüde"
        "voi": 0.75,  # Bayrisch: "voi müde"

        # Extrem (0.85-1.0)
        "total": 0.9,
        "mega": 0.95,
        "extrem": 0.95,
        "unglaublich": 0.95,
        "wahnsinnig": 0.9,
        "unfassbar": 0.95,
        "so": 0.8,  # "ich bin SO müde"
        "sooo": 0.95,
        "soooo": 1.0,
        "absolut": 0.9,
        "komplett": 0.85,
        "völlig": 0.85,
        "voll": 0.8,
        "hammer": 0.9,
        "krass": 0.85,
        "brutal": 0.9,
        "tierisch": 0.85,
        "höllisch": 0.9,
        "mörder": 0.9,   # "mördermüde"
        "stink": 0.85,   # "stinksauer"
        "stock": 0.85,   # "stockmüde"
        "tod": 0.95,     # "todmüde"
        "hundemüde": 1.0,
        "100%": 1.0,
        "100 prozent": 1.0,
        "hundertpro": 0.95,
        "sowas von": 0.9,
        "dermaßen": 0.9,
        "unheimlich": 0.85,
        "irre": 0.85,
        "irrsinnig": 0.9,
        "ultra": 0.95,
        "über": 0.85,    # "übermüde"
        "hyper": 0.9,
    }

    # Emotionale Verstaerker (Satzzeichen etc.)
    PUNCTUATION_BOOST = {
        "!": 0.1,
        "!!": 0.15,
        "!!!": 0.2,
        "!!!!": 0.25,
        "?!": 0.15,
        "!?": 0.15,
        "...": 0.05,  # Leichte Betonung
    }

    # Wiederholungen verstaerken
    REPETITION_PATTERNS = [
        (r"(\w)\1{2,}", 0.15),  # "sooo", "ahhh" etc.
        (r"(\w)\1{3,}", 0.25),  # "soooo", "ahhhh" - noch stärker
        (r"(ja|nein|oh|ah|ach)\s+\1", 0.1),  # "ja ja", "nein nein"
        (r"(so|ganz|sehr)\s+\1", 0.15),  # "so so", "ganz ganz"
    ]

    # Superlative erkennen
    SUPERLATIVE_PATTERNS = [
        (r"\b(?:der|die|das)\s+(?:\w+)ste\b", 0.9),  # "das beste", "die schönste"
        (r"\bam\s+(?:\w+)sten\b", 0.9),  # "am müdesten", "am besten"
        (r"\b(?:aller)?(?:\w+)ste[nrs]?\b", 0.85),  # "allerbeste"
    ]

    # Numerische Verstärker
    NUMERIC_PATTERNS = [
        (r"\b(?:1000|tausend)\s*(?:mal|%|prozent)?\b", 0.95),
        (r"\b(?:100|hundert)\s*(?:mal|%|prozent)?\b", 0.9),
        (r"\b(?:1000000|million)\s*(?:mal)?\b", 1.0),
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """
        Analysiert die Intensitaet einer Aussage.

        Returns:
            {
                "intensity_level": str,  # "minimal", "low", "medium", "high", "extreme"
                "intensity_value": float,  # 0-1
                "modifiers_found": List[str],
                "has_emphasis": bool,  # Satzzeichen-Verstaerkung
                "has_repetition": bool,  # Wiederholungen
                "original_text": str,
            }
        """
        text_lower = text.lower().strip()

        result = {
            "intensity_level": "medium",
            "intensity_value": 0.5,
            "modifiers_found": [],
            "has_emphasis": False,
            "has_repetition": False,
            "original_text": text,
        }

        base_intensity = 0.5  # Standard

        # Suche nach Intensitaets-Modifikatoren
        # Sortiere nach Laenge (laengere zuerst fuer korrekte Erkennung)
        sorted_modifiers = sorted(
            cls.INTENSITY_MODIFIERS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for modifier, value in sorted_modifiers:
            if modifier in text_lower:
                result["modifiers_found"].append(modifier)
                # Nehme den hoechsten/niedrigsten Wert
                if value > 0.5 and value > base_intensity:
                    base_intensity = value
                elif value < 0.5 and value < base_intensity:
                    base_intensity = value

        # Satzzeichen-Verstaerkung
        for punct, boost in cls.PUNCTUATION_BOOST.items():
            if text.endswith(punct):
                base_intensity = min(base_intensity + boost, 1.0)
                result["has_emphasis"] = True
                break

        # Wiederholungen
        for pattern, boost in cls.REPETITION_PATTERNS:
            if re.search(pattern, text_lower):
                base_intensity = min(base_intensity + boost, 1.0)
                result["has_repetition"] = True

        # Grossbuchstaben deuten auf Betonung hin
        uppercase_words = re.findall(r"\b[A-ZÄÖÜ]{2,}\b", text)
        if uppercase_words:
            base_intensity = min(base_intensity + 0.1, 1.0)
            result["has_emphasis"] = True

        result["intensity_value"] = base_intensity

        # Bestimme Level
        if base_intensity < 0.2:
            result["intensity_level"] = "minimal"
        elif base_intensity < 0.4:
            result["intensity_level"] = "low"
        elif base_intensity < 0.6:
            result["intensity_level"] = "medium"
        elif base_intensity < 0.8:
            result["intensity_level"] = "high"
        else:
            result["intensity_level"] = "extreme"

        return result

    @classmethod
    def get_intensity(cls, text: str) -> Tuple[str, float]:
        """
        Kurzform fuer schnelle Intensitaets-Abfrage.

        Returns:
            Tuple[str, float]: (level, value)
        """
        result = cls.analyze(text)
        return (result["intensity_level"], result["intensity_value"])


# =============================================================================
# QUESTION TYPE CLASSIFIER - Klassifiziert Fragetypen
# =============================================================================

class QuestionTypeClassifier:
    """
    Klassifiziert verschiedene Fragetypen fuer bessere Antwort-Generierung.

    Fragetypen:
    1. yes_no: Ja/Nein-Fragen ("Bist du müde?")
    2. wh_question: W-Fragen ("Was machst du?", "Wie geht's?")
    3. choice: Auswahlfragen ("Kaffee oder Tee?")
    4. rhetorical: Rhetorische Fragen ("Wer hätte das gedacht?")
    5. confirmation: Bestaetigungsfragen ("...oder?", "...nicht wahr?")
    6. indirect: Indirekte Fragen ("Ich frage mich ob...")
    7. embedded: Eingebettete Fragen ("Weißt du, wo...?")
    """

    # W-Fragewörter mit Unterkategorien
    WH_WORDS = {
        "was": "object",      # Was machst du?
        "wer": "person",      # Wer bist du?
        "wen": "person_acc",  # Wen siehst du?
        "wem": "person_dat",  # Wem gehört das?
        "wessen": "possession",  # Wessen Buch?
        "wo": "location",     # Wo bist du?
        "woher": "origin",    # Woher kommst du?
        "wohin": "destination",  # Wohin gehst du?
        "wann": "time",       # Wann kommst du?
        "wie": "manner",      # Wie geht's?
        "warum": "reason",    # Warum fragst du?
        "weshalb": "reason",
        "wieso": "reason",
        "weswegen": "reason",
        "welch": "selection", # Welcher Tag?
        "wieviel": "quantity",
        "wie viel": "quantity",
        "wie viele": "quantity",
    }

    # Ja/Nein-Frage-Patterns (Verb am Anfang)
    YES_NO_PATTERNS = [
        r"^(?:bist|hast|kannst|willst|magst|darfst|sollst|musst|wirst|weißt)\s+du\b",
        r"^(?:bin|habe|kann|will|mag|darf|soll|muss|werde|weiß)\s+ich\b",
        r"^(?:ist|hat|kann|wird|soll|muss|darf)\s+(?:das|es|er|sie|man)\b",
        r"^(?:sind|haben|können|werden|sollen|müssen|dürfen)\s+(?:wir|sie)\b",
        r"^(?:gibt|stimmt|passt|klappt|funktioniert)\s+",
    ]

    # Bestaetigungsfragen (Tag-Questions) - inkl. deutsche Dialekte
    CONFIRMATION_TAGS = [
        # Standard
        r",?\s*oder\??$",
        r",?\s*nicht\s*wahr\??$",
        r",?\s*stimmt'?s?\??$",
        r",?\s*richtig\??$",
        r",?\s*oder\s*etwa\s*nicht\??$",
        r",?\s*oder\s*nicht\??$",
        r",?\s*verstehst\s*(?:du)?\??$",
        r",?\s*weißt\s*(?:du)?\??$",
        r",?\s*meinst\s*(?:du)?\s*nicht\s*(?:auch)?\??$",

        # Norddeutsch
        r",?\s*(?:ne|nä|nech|nich|wa|wah)\??$",
        r",?\s*(?:oder\s+wat|wat)\??$",

        # Süddeutsch / Bayrisch / Österreichisch
        r",?\s*(?:gell|gel|gelle|gelt|gö)\??$",
        r",?\s*(?:net|ned|nit)\s*(?:wahr)?\??$",
        r",?\s*(?:oder|oda)\??$",
        r",?\s*(?:stimmts|stimmt's)\??$",

        # Schwäbisch
        r",?\s*(?:gell|gelle|odr)\??$",

        # Sächsisch
        r",?\s*(?:nu|nü)\??$",

        # Rheinisch / Kölsch
        r",?\s*(?:nä|woll|wollens)\??$",

        # Berlinerisch
        r",?\s*(?:wa|wat|oda)\??$",

        # Umgangssprache
        r",?\s*(?:hm|hmm|mh)\??$",
        r",?\s*(?:ja|nein)\??$",
        r",?\s*(?:check|checkst)\??$",  # Jugendsprache
        r",?\s*(?:kapiert|kapierst)\??$",
    ]

    # Rhetorische Fragen (erweitert)
    RHETORICAL_PATTERNS = [
        # Existenzielle
        r"wer\s+hätte\s+das\s+gedacht",
        r"was\s+soll'?s?\s*\??",
        r"wen\s+interessiert'?s?\s*\??",
        r"wer\s+braucht\s+das\s+schon",
        r"was\s+will\s+man\s+mehr",
        r"was\s+soll\s+ich\s+(?:dazu\s+)?sagen",
        r"was\s+erwartest\s+du\s*\??",

        # Resigniert / Akzeptierend
        r"warum\s+(?:auch\s+)?nicht",
        r"wieso\s+(?:denn\s+)?nicht",
        r"was\s+kann\s+man\s+(?:da\s+)?(?:schon\s+)?machen",
        r"was\s+bleibt\s+(?:mir|uns)\s+(?:anderes\s+)?übrig",
        r"(?:ach|na)\s+was\s+soll'?s",

        # Sarkastisch / Ironisch
        r"(?:ach\s+)?(?:wirklich|echt)\s+(?:jetzt)?\s*\??",
        r"du\s+meinst\s+(?:wohl\s+)?nicht\s*\??",
        r"(?:und\s+)?(?:das\s+)?(?:wundert|überrascht)\s+(?:dich|mich|wen)\s*\??",
        r"wen\s+juckt'?s\s*\??",
        r"na\s+und\s*\??",
        r"so\s+what\s*\??",  # Anglizismus

        # Ungläubig
        r"(?:das\s+)?(?:meinst|glaubst)\s+du\s+(?:wirklich|echt|doch\s+nicht)\s*\??",
        r"im\s+ernst\s*\??",
        r"(?:ist|war)\s+(?:das\s+)?(?:dein|ihr)\s+ernst\s*\??",
        r"willst\s+du\s+mich\s+(?:ver)?(?:äppeln|veräppeln|verarschen)\s*\??",

        # Philosophisch
        r"wer\s+weiß\s+(?:das\s+)?schon",
        r"wozu\s+das\s+(?:alles|ganze)\s*\??",
        r"warum\s+ist\s+das\s+so\s*\??",
    ]

    # Indirekte Fragen
    INDIRECT_PATTERNS = [
        r"ich\s+(?:frage|frag)\s+mich,?\s*(?:ob|was|wer|wie|wo|wann|warum)",
        r"ich\s+(?:wüsste|wüsst|wollte|wollt)\s+gern(?:e)?,?\s*(?:ob|was|wer|wie|wo)",
        r"ich\s+(?:möchte|würde)\s+(?:gern|gerne)\s+wissen",
        r"mich\s+interessiert,?\s*(?:ob|was|wie)",
        r"kannst\s+du\s+mir\s+sagen,?\s*(?:ob|was|wie|wo|wann)",
    ]

    # Eingebettete Fragen
    EMBEDDED_PATTERNS = [
        r"(?:weißt|wissen)\s+(?:du|Sie),?\s*(?:ob|was|wer|wie|wo|wann|warum)",
        r"(?:hast|haben)\s+(?:du|Sie)\s+(?:eine\s+)?(?:ahnung|idee),?\s*(?:ob|was|wie)",
        r"keine\s+ahnung,?\s*(?:ob|was|wie|wo)",
    ]

    # Auswahlfragen
    CHOICE_PATTERNS = [
        r"\boder\b(?!etwa\s+nicht)",  # "Kaffee oder Tee?" aber nicht "...oder etwa nicht?"
    ]

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Klassifiziert den Fragetyp.

        Returns:
            {
                "is_question": bool,
                "question_type": str,
                "sub_type": str | None,  # z.B. "reason" bei "warum"
                "wh_word": str | None,
                "expects_answer_type": str,  # "yes_no", "entity", "explanation", etc.
                "confidence": float,
            }
        """
        text_lower = text.lower().strip()
        text_clean = text.strip()

        result = {
            "is_question": False,
            "question_type": "statement",
            "sub_type": None,
            "wh_word": None,
            "expects_answer_type": "none",
            "confidence": 0.0,
        }

        # Grundlegende Frage-Erkennung
        has_question_mark = "?" in text
        has_question_intonation = text_clean.endswith("?")

        # Indirekte Fragen pruefen (haben oft kein Fragezeichen)
        for pattern in cls.INDIRECT_PATTERNS:
            if re.search(pattern, text_lower):
                result["is_question"] = True
                result["question_type"] = "indirect"
                result["expects_answer_type"] = "information"
                result["confidence"] = 0.85
                return result

        # Eingebettete Fragen
        for pattern in cls.EMBEDDED_PATTERNS:
            if re.search(pattern, text_lower):
                result["is_question"] = True
                result["question_type"] = "embedded"
                result["expects_answer_type"] = "information"
                result["confidence"] = 0.85
                return result

        # Rhetorische Fragen
        for pattern in cls.RHETORICAL_PATTERNS:
            if re.search(pattern, text_lower):
                result["is_question"] = True
                result["question_type"] = "rhetorical"
                result["expects_answer_type"] = "none"  # Erwartet keine echte Antwort
                result["confidence"] = 0.9
                return result

        # Bestaetigungsfragen
        for pattern in cls.CONFIRMATION_TAGS:
            if re.search(pattern, text_lower):
                result["is_question"] = True
                result["question_type"] = "confirmation"
                result["expects_answer_type"] = "yes_no"
                result["confidence"] = 0.85
                return result

        # Ab hier: Fragezeichen erhoeht Confidence
        if not has_question_mark:
            # Ohne Fragezeichen: Niedrigere Confidence oder Statement
            pass

        # W-Fragen erkennen
        words = text_lower.split()
        for word in words[:3]:  # Nur erste Woerter pruefen
            # Entferne Satzzeichen
            clean_word = re.sub(r"[?,!.]", "", word)
            for wh, sub_type in cls.WH_WORDS.items():
                if clean_word == wh or clean_word.startswith(wh):
                    result["is_question"] = True
                    result["question_type"] = "wh_question"
                    result["sub_type"] = sub_type
                    result["wh_word"] = wh
                    result["confidence"] = 0.95 if has_question_mark else 0.7

                    # Erwartete Antwort-Art basierend auf W-Wort
                    if sub_type in ["person", "person_acc", "person_dat"]:
                        result["expects_answer_type"] = "entity_person"
                    elif sub_type in ["location", "origin", "destination"]:
                        result["expects_answer_type"] = "entity_location"
                    elif sub_type == "time":
                        result["expects_answer_type"] = "entity_time"
                    elif sub_type == "reason":
                        result["expects_answer_type"] = "explanation"
                    elif sub_type == "manner":
                        result["expects_answer_type"] = "description"
                    elif sub_type == "quantity":
                        result["expects_answer_type"] = "number"
                    else:
                        result["expects_answer_type"] = "entity"

                    return result

        # Ja/Nein-Fragen (Verb am Satzanfang)
        for pattern in cls.YES_NO_PATTERNS:
            if re.search(pattern, text_lower):
                result["is_question"] = True
                result["question_type"] = "yes_no"
                result["expects_answer_type"] = "yes_no"
                result["confidence"] = 0.9 if has_question_mark else 0.6
                return result

        # Auswahlfragen
        for pattern in cls.CHOICE_PATTERNS:
            if re.search(pattern, text_lower) and has_question_mark:
                result["is_question"] = True
                result["question_type"] = "choice"
                result["expects_answer_type"] = "selection"
                result["confidence"] = 0.8
                return result

        # Fallback: Fragezeichen aber kein erkanntes Muster
        if has_question_mark:
            result["is_question"] = True
            result["question_type"] = "unknown"
            result["expects_answer_type"] = "unknown"
            result["confidence"] = 0.5

        return result

    @classmethod
    def is_yes_no_question(cls, text: str) -> bool:
        """Schnellpruefung ob Ja/Nein-Frage."""
        result = cls.classify(text)
        return result["question_type"] == "yes_no"

    @classmethod
    def get_expected_answer_type(cls, text: str) -> str:
        """Gibt den erwarteten Antwort-Typ zurueck."""
        result = cls.classify(text)
        return result["expects_answer_type"]


# =============================================================================
# IMPLICIT INTENT DETECTOR - Erkennt implizite Absichten
# =============================================================================

class ImplicitIntentDetector:
    """
    Erkennt implizite/indirekte Absichten, die nicht direkt ausgesprochen werden.

    Beispiele:
    - "Es ist kalt hier" → Implizit: Fenster schließen / Heizung an
    - "Ich habe Hunger" → Implizit: Essensvorschlag gewünscht
    - "Es ist schon spät" → Implizit: Gespräch beenden
    - "Ich weiß nicht was ich machen soll" → Implizit: Rat/Vorschlag gewünscht
    """

    # Implizite Muster mit moeglichen Absichten
    IMPLICIT_PATTERNS = [
        # Umgebung/Komfort
        {
            "patterns": [r"(?:es\s+ist|hier\s+ist)\s+(?:so\s+)?kalt", r"mir\s+ist\s+kalt"],
            "implicit_intent": "request_comfort",
            "implicit_action": "suggest_warmth",
            "confidence": 0.7,
        },
        {
            "patterns": [r"(?:es\s+ist|hier\s+ist)\s+(?:so\s+)?heiß", r"mir\s+ist\s+(?:so\s+)?warm"],
            "implicit_intent": "request_comfort",
            "implicit_action": "suggest_cooling",
            "confidence": 0.7,
        },
        {
            "patterns": [r"(?:es\s+ist|hier\s+ist)\s+(?:so\s+)?dunkel"],
            "implicit_intent": "request_action",
            "implicit_action": "suggest_light",
            "confidence": 0.6,
        },

        # Zeit-basiert
        {
            "patterns": [r"es\s+ist\s+(?:schon\s+)?spät", r"(?:schon\s+)?so\s+spät"],
            "implicit_intent": "signal_end",
            "implicit_action": "offer_farewell",
            "confidence": 0.65,
        },
        {
            "patterns": [r"ich\s+(?:muss|sollte)\s+(?:eigentlich\s+)?(?:los|gehen|schlafen)"],
            "implicit_intent": "signal_end",
            "implicit_action": "acknowledge_departure",
            "confidence": 0.8,
        },

        # Beduerfnisse
        {
            "patterns": [r"ich\s+hab(?:e)?\s+(?:so\s+)?hunger", r"mir\s+knurrt\s+der\s+magen"],
            "implicit_intent": "request_suggestion",
            "implicit_action": "suggest_food",
            "confidence": 0.75,
        },
        {
            "patterns": [r"ich\s+hab(?:e)?\s+(?:so\s+)?durst"],
            "implicit_intent": "request_suggestion",
            "implicit_action": "suggest_drink",
            "confidence": 0.7,
        },
        {
            "patterns": [r"ich\s+kann\s+nicht\s+schlafen", r"ich\s+(?:bin|lieg)\s+wach"],
            "implicit_intent": "request_help",
            "implicit_action": "offer_sleep_tips",
            "confidence": 0.7,
        },

        # Entscheidungs-Hilfe
        {
            "patterns": [
                r"ich\s+weiß\s+nicht\s+was\s+ich\s+(?:machen|tun)\s+soll",
                r"keine\s+ahnung\s+was\s+ich\s+machen\s+soll",
            ],
            "implicit_intent": "request_advice",
            "implicit_action": "offer_suggestions",
            "confidence": 0.85,
        },
        {
            "patterns": [
                r"ich\s+kann\s+mich\s+nicht\s+entscheiden",
                r"ich\s+bin\s+(?:mir\s+)?unsicher",
            ],
            "implicit_intent": "request_advice",
            "implicit_action": "help_decide",
            "confidence": 0.75,
        },

        # Langeweile/Beschaeftigung
        {
            "patterns": [
                r"mir\s+ist\s+(?:so\s+)?langweilig",
                r"ich\s+weiß\s+nicht\s+was\s+ich\s+machen\s+soll",
                r"nichts\s+zu\s+tun",
            ],
            "implicit_intent": "request_activity",
            "implicit_action": "suggest_activity",
            "confidence": 0.8,
        },

        # Soziales
        {
            "patterns": [r"ich\s+(?:fühl|fühle)\s+mich\s+(?:so\s+)?(?:allein|einsam)"],
            "implicit_intent": "request_company",
            "implicit_action": "offer_conversation",
            "confidence": 0.85,
        },
        {
            "patterns": [r"(?:ich\s+)?(?:brauch|brauche)\s+jemanden\s+zum\s+reden"],
            "implicit_intent": "request_conversation",
            "implicit_action": "offer_listening",
            "confidence": 0.9,
        },

        # Informations-Suche
        {
            "patterns": [
                r"ich\s+(?:frage|frag)\s+mich",
                r"ich\s+(?:bin\s+)?(?:neugierig|gespannt)",
                r"mich\s+(?:würde|wuerde)\s+interessieren",
            ],
            "implicit_intent": "request_information",
            "implicit_action": "provide_info",
            "confidence": 0.7,
        },

        # Zustimmungs-Suche
        {
            "patterns": [
                r"findest\s+du\s+(?:auch|nicht)",
                r"siehst\s+du\s+das\s+(?:auch\s+)?so",
                r"oder\s+(?:wie\s+)?siehst\s+du\s+das",
            ],
            "implicit_intent": "request_opinion",
            "implicit_action": "share_opinion",
            "confidence": 0.8,
        },
    ]

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt implizite Absichten.

        Returns:
            {
                "has_implicit_intent": bool,
                "implicit_intent": str | None,
                "implicit_action": str | None,
                "explicit_content": str,  # Was tatsaechlich gesagt wurde
                "confidence": float,
                "all_detected": List[Dict],  # Alle erkannten impliziten Intents
            }
        """
        text_lower = text.lower().strip()

        result = {
            "has_implicit_intent": False,
            "implicit_intent": None,
            "implicit_action": None,
            "explicit_content": text,
            "confidence": 0.0,
            "all_detected": [],
        }

        best_match = None
        best_confidence = 0.0

        for intent_data in cls.IMPLICIT_PATTERNS:
            for pattern in intent_data["patterns"]:
                if re.search(pattern, text_lower):
                    confidence = intent_data["confidence"]
                    match_data = {
                        "implicit_intent": intent_data["implicit_intent"],
                        "implicit_action": intent_data["implicit_action"],
                        "confidence": confidence,
                        "matched_pattern": pattern,
                    }
                    result["all_detected"].append(match_data)

                    if confidence > best_confidence:
                        best_match = intent_data
                        best_confidence = confidence

        if best_match:
            result["has_implicit_intent"] = True
            result["implicit_intent"] = best_match["implicit_intent"]
            result["implicit_action"] = best_match["implicit_action"]
            result["confidence"] = best_confidence

        return result

    @classmethod
    def get_suggested_action(cls, text: str) -> Optional[str]:
        """Gibt die vorgeschlagene Aktion fuer impliziten Intent zurueck."""
        result = cls.detect(text)
        return result["implicit_action"] if result["has_implicit_intent"] else None


# =============================================================================
# CONTEXT AWARE DETECTOR - Nutzt Konversationsverlauf
# =============================================================================

class ContextAwareDetector:
    """
    Erkennt Intents unter Beruecksichtigung des Konversationsverlaufs.

    Funktionen:
    1. Referenz-Aufloesung ("das", "es", "davon")
    2. Topic-Kontinuitaet erkennen
    3. Follow-up-Fragen erkennen
    4. Stimmungs-Verlauf tracken
    """

    # Referenz-Woerter die Kontext brauchen
    REFERENCE_WORDS = {
        "das": "demonstrative",
        "dies": "demonstrative",
        "diese": "demonstrative",
        "dieser": "demonstrative",
        "dieses": "demonstrative",
        "es": "pronoun",
        "sie": "pronoun",
        "er": "pronoun",
        "ihn": "pronoun",
        "ihm": "pronoun",
        "davon": "prepositional",
        "dazu": "prepositional",
        "damit": "prepositional",
        "darüber": "prepositional",
        "darunter": "prepositional",
        "dafür": "prepositional",
        "dagegen": "prepositional",
        "danach": "temporal",
        "davor": "temporal",
        "dabei": "locative",
    }

    # Follow-up-Indikatoren
    FOLLOWUP_INDICATORS = [
        r"^und\s+",  # "Und was noch?"
        r"^aber\s+", # "Aber warum?"
        r"^also\s+", # "Also stimmt das?"
        r"^dann\s+", # "Dann mach das"
        r"^ok(?:ay)?,?\s+(?:und|aber)", # "Ok, und dann?"
        r"^(?:ah|aha|oh),?\s+", # "Aha, interessant"
        r"^(?:ja|nein),?\s+(?:und|aber|also)", # "Ja, und weiter?"
        r"^(?:stimmt|richtig|genau),?\s+", # "Stimmt, aber..."
        r"^sonst\s+noch", # "Sonst noch was?"
        r"^was\s+noch", # "Was noch?"
        r"^mehr\s+(?:davon|dazu)", # "Mehr davon"
        r"^erzähl\s+(?:mir\s+)?mehr", # "Erzähl mehr"
    ]

    # Topic-Wechsel-Indikatoren
    TOPIC_CHANGE_INDICATORS = [
        r"^(?:übrigens|apropos|by\s+the\s+way)",
        r"^(?:ach\s+)?(?:ganz\s+)?was\s+anderes",
        r"^(?:mal\s+)?(?:eine\s+)?andere\s+frage",
        r"^(?:ich\s+wollte\s+)?(?:noch\s+)?(?:was\s+anderes|etwas\s+anderes)",
        r"^(?:bevor\s+ich.?s\s+vergesse)",
        r"^(?:wo\s+wir\s+(?:schon\s+)?dabei\s+sind)",
    ]

    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.current_topic: Optional[str] = None
        self.mood_history: List[str] = []
        self.last_entities: List[str] = []

    def add_turn(self, speaker: str, text: str, intent: str = None, entities: List[str] = None):
        """Fuegt eine Konversations-Runde hinzu."""
        turn = {
            "speaker": speaker,
            "text": text,
            "intent": intent,
            "entities": entities or [],
            "timestamp": time.time() if 'time' in dir() else 0,
        }
        self.conversation_history.append(turn)

        # Entities merken fuer Referenz-Aufloesung
        if entities:
            self.last_entities = entities

        # Maximal 50 Turns speichern (erhöht von 20 für besseren Kontext)
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def analyze_with_context(self, text: str) -> Dict[str, Any]:
        """
        Analysiert Text unter Beruecksichtigung des Kontexts.

        Returns:
            {
                "has_reference": bool,
                "reference_type": str | None,
                "resolved_reference": str | None,
                "is_followup": bool,
                "followup_type": str | None,
                "is_topic_change": bool,
                "topic_continuity": float,  # 0-1 wie stark Topic weitergeführt wird
                "context_needed": bool,
                "suggested_context": Dict | None,
            }
        """
        text_lower = text.lower().strip()

        result = {
            "has_reference": False,
            "reference_type": None,
            "resolved_reference": None,
            "is_followup": False,
            "followup_type": None,
            "is_topic_change": False,
            "topic_continuity": 0.5,
            "context_needed": False,
            "suggested_context": None,
        }

        # Referenz-Woerter pruefen
        words = text_lower.split()
        for word in words:
            clean_word = re.sub(r"[?,!.]", "", word)
            if clean_word in self.REFERENCE_WORDS:
                result["has_reference"] = True
                result["reference_type"] = self.REFERENCE_WORDS[clean_word]
                result["context_needed"] = True

                # Versuche Referenz aufzuloesen
                if self.last_entities:
                    result["resolved_reference"] = self.last_entities[-1]
                break

        # Follow-up pruefen
        for pattern in self.FOLLOWUP_INDICATORS:
            if re.search(pattern, text_lower):
                result["is_followup"] = True
                result["topic_continuity"] = 0.8
                break

        # Topic-Wechsel pruefen
        for pattern in self.TOPIC_CHANGE_INDICATORS:
            if re.search(pattern, text_lower):
                result["is_topic_change"] = True
                result["topic_continuity"] = 0.1
                break

        # Kontext vorschlagen wenn noetig
        if result["context_needed"] and self.conversation_history:
            last_turn = self.conversation_history[-1]
            result["suggested_context"] = {
                "last_speaker": last_turn["speaker"],
                "last_text": last_turn["text"][:100],
                "last_intent": last_turn.get("intent"),
                "last_entities": last_turn.get("entities", []),
            }

        return result

    def get_conversation_mood(self) -> str:
        """Gibt die aktuelle Stimmung der Konversation zurueck."""
        if not self.mood_history:
            return "neutral"
        # Letzte 3 Stimmungen gewichten
        recent = self.mood_history[-3:]
        # Einfache Mehrheitsentscheidung
        from collections import Counter
        return Counter(recent).most_common(1)[0][0]


# =============================================================================
# MULTI-STAGE INTENT PIPELINE - Orchestriert alle Detektoren
# =============================================================================

class MultiStageIntentPipeline:
    """
    Orchestriert alle Detektoren in einer mehrstufigen Pipeline.

    Pipeline-Stufen:
    1. Preprocessing: Normalisierung, Tokenisierung
    2. Syntax: Satztyp, Fragetyp, Subjekt-Verb-Analyse
    3. Semantik: Emotion, Intention, Implizite Bedeutung
    4. Kontext: Referenzen, Follow-ups, Topic
    5. Integration: Alle Ergebnisse zusammenfuehren
    6. Confidence: Finale Confidence berechnen
    """

    def __init__(self):
        self.context_detector = ContextAwareDetector()
        self.pipeline_stats = {
            "total_processed": 0,
            "avg_confidence": 0.0,
            "stage_times": {},
        }

    def process(self, text: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Verarbeitet Text durch alle Pipeline-Stufen.

        Returns:
            {
                "original_text": str,
                "stages": {
                    "syntax": {...},
                    "semantics": {...},
                    "context": {...},
                },
                "final_intent": str,
                "final_confidence": float,
                "all_intents": List[Dict],
                "recommended_response_type": str,
                "metadata": {...},
            }
        """
        result = {
            "original_text": text,
            "stages": {},
            "final_intent": "unknown",
            "final_confidence": 0.0,
            "all_intents": [],
            "recommended_response_type": "general",
            "metadata": {},
        }

        # Kontext aktualisieren
        if conversation_history:
            for turn in conversation_history[-5:]:  # Letzte 5 Turns
                self.context_detector.add_turn(
                    turn.get("speaker", "unknown"),
                    turn.get("text", ""),
                    turn.get("intent"),
                    turn.get("entities")
                )

        # ===== STUFE 1: SYNTAX =====
        syntax_result = self._stage_syntax(text)
        result["stages"]["syntax"] = syntax_result

        # ===== STUFE 2: SEMANTIK =====
        semantics_result = self._stage_semantics(text)
        result["stages"]["semantics"] = semantics_result

        # ===== STUFE 3: KONTEXT =====
        context_result = self._stage_context(text)
        result["stages"]["context"] = context_result

        # ===== STUFE 4: INTEGRATION =====
        integrated = self._integrate_results(syntax_result, semantics_result, context_result)
        result["final_intent"] = integrated["intent"]
        result["final_confidence"] = integrated["confidence"]
        result["all_intents"] = integrated["all_intents"]
        result["recommended_response_type"] = integrated["response_type"]

        # Metadata
        result["metadata"] = {
            "is_question": syntax_result["question"]["is_question"],
            "has_negation": semantics_result["negation"]["has_negation"],
            "intensity": semantics_result["intensity"]["intensity_level"],
            "needs_context": context_result["context_needed"],
            "is_followup": context_result["is_followup"],
        }

        self.pipeline_stats["total_processed"] += 1

        return result

    def _stage_syntax(self, text: str) -> Dict[str, Any]:
        """Stufe 1: Syntaktische Analyse."""
        return {
            "subject_verb": SubjectVerbAnalyzer.analyze(text),
            "question": QuestionTypeClassifier.classify(text),
        }

    def _stage_semantics(self, text: str) -> Dict[str, Any]:
        """Stufe 2: Semantische Analyse."""
        return {
            "negation": NegationHandler.analyze(text),
            "intensity": IntensityAnalyzer.analyze(text),
            "wellbeing": WellbeingInquiryDetector.detect(text),
            "user_emotion": UserEmotionDetector.detect(text),
            "implicit": ImplicitIntentDetector.detect(text),
        }

    def _stage_context(self, text: str) -> Dict[str, Any]:
        """Stufe 3: Kontext-Analyse."""
        return self.context_detector.analyze_with_context(text)

    def _integrate_results(self, syntax: Dict, semantics: Dict, context: Dict) -> Dict[str, Any]:
        """Integriert alle Ergebnisse zu finalem Intent."""
        all_intents = []

        # Sammle alle erkannten Intents mit Confidence
        # Wellbeing Inquiry
        if semantics["wellbeing"]["is_wellbeing_inquiry"]:
            all_intents.append({
                "intent": "wellbeing_inquiry",
                "confidence": semantics["wellbeing"]["confidence"],
                "source": "wellbeing_detector",
            })

        # User Emotion
        if semantics["user_emotion"]["user_shared_emotion"]:
            # Beruecksichtige Negation
            emotion = semantics["user_emotion"]["emotion"]
            confidence = semantics["user_emotion"]["confidence"]

            if semantics["negation"]["has_negation"]:
                negated = NegationHandler.negate_emotion(
                    emotion,
                    semantics["negation"]["negation_strength"]
                )
                emotion = negated[0]
                confidence *= negated[1]

            all_intents.append({
                "intent": f"user_emotion_{emotion}",
                "confidence": confidence,
                "source": "emotion_detector",
            })

        # Implicit Intent
        if semantics["implicit"]["has_implicit_intent"]:
            all_intents.append({
                "intent": semantics["implicit"]["implicit_intent"],
                "confidence": semantics["implicit"]["confidence"],
                "source": "implicit_detector",
                "action": semantics["implicit"]["implicit_action"],
            })

        # Question Type
        if syntax["question"]["is_question"]:
            all_intents.append({
                "intent": f"question_{syntax['question']['question_type']}",
                "confidence": syntax["question"]["confidence"],
                "source": "question_classifier",
            })

        # Sortiere nach Confidence
        all_intents.sort(key=lambda x: x["confidence"], reverse=True)

        # Waehle besten Intent
        if all_intents:
            best = all_intents[0]
            final_intent = best["intent"]
            final_confidence = best["confidence"]
        else:
            final_intent = "general"
            final_confidence = 0.3

        # Context-Modifikation
        if context["is_followup"]:
            final_confidence *= 1.1  # Follow-ups haben hoehere Confidence
            final_confidence = min(final_confidence, 1.0)

        # Bestimme Response-Typ
        response_type = self._determine_response_type(final_intent, semantics, syntax)

        return {
            "intent": final_intent,
            "confidence": final_confidence,
            "all_intents": all_intents,
            "response_type": response_type,
        }

    def _determine_response_type(self, intent: str, semantics: Dict, syntax: Dict) -> str:
        """Bestimmt den empfohlenen Antwort-Typ."""
        # Fragen -> Antwort
        if syntax["question"]["is_question"]:
            if syntax["question"]["question_type"] == "yes_no":
                return "yes_no_answer"
            elif syntax["question"]["question_type"] == "wh_question":
                return "informative_answer"
            elif syntax["question"]["question_type"] == "rhetorical":
                return "acknowledgment"

        # Emotionen -> Empathie
        if semantics["user_emotion"]["user_shared_emotion"]:
            response_type = semantics["user_emotion"]["response_type"]
            return response_type or "empathic_response"

        # Implizite Intents -> Vorschlag
        if semantics["implicit"]["has_implicit_intent"]:
            return f"action_{semantics['implicit']['implicit_action']}"

        # Hohe Intensitaet -> Bestaerkende Antwort
        if semantics["intensity"]["intensity_value"] > 0.8:
            return "emphatic_response"

        return "general_response"

    def get_quick_analysis(self, text: str) -> Dict[str, Any]:
        """
        Schnelle Analyse ohne vollen Pipeline-Durchlauf.

        Fuer Performance-kritische Anwendungen.
        """
        # Nur die wichtigsten Checks
        sv = SubjectVerbAnalyzer.analyze(text)
        question = QuestionTypeClassifier.classify(text)
        wellbeing = WellbeingInquiryDetector.detect(text)

        is_about_holo = sv["perspective"] == "asking_holo" or wellbeing["is_wellbeing_inquiry"]

        return {
            "is_question": question["is_question"],
            "is_about_holo": is_about_holo,
            "is_user_statement": sv["perspective"] == "user_self",
            "quick_intent": "wellbeing_inquiry" if wellbeing["is_wellbeing_inquiry"] else (
                "question" if question["is_question"] else "statement"
            ),
        }


# =============================================================================
# RESPONSE ENHANCEMENT - Fuer Holos Antworten
# =============================================================================

class ResponseIntensityModifier:
    """
    Modifiziert die Intensitaet von Holos Antworten.

    Kann:
    - Antworten verstaerken ("gut" → "richtig gut", "super")
    - Antworten abschwaechen ("schlecht" → "nicht so gut")
    - Intensitaet an User-Input anpassen (Mirroring)
    """

    # Basis-Adjektive mit Intensitaets-Varianten
    INTENSITY_VARIANTS = {
        # Positive Adjektive
        "gut": {
            "minimal": "ganz okay",
            "low": "okay",
            "medium": "gut",
            "high": "richtig gut",
            "extreme": "mega gut",
        },
        "schön": {
            "minimal": "ganz nett",
            "low": "nett",
            "medium": "schön",
            "high": "wunderschön",
            "extreme": "traumhaft schön",
        },
        "toll": {
            "minimal": "ganz nett",
            "low": "nett",
            "medium": "toll",
            "high": "super toll",
            "extreme": "mega toll",
        },
        "interessant": {
            "minimal": "ganz interessant",
            "low": "etwas interessant",
            "medium": "interessant",
            "high": "sehr interessant",
            "extreme": "mega interessant",
        },
        "cool": {
            "minimal": "ganz okay",
            "low": "okay",
            "medium": "cool",
            "high": "richtig cool",
            "extreme": "mega cool",
        },
        "lustig": {
            "minimal": "ein bisschen witzig",
            "low": "witzig",
            "medium": "lustig",
            "high": "echt lustig",
            "extreme": "so lustig",
        },
        "spannend": {
            "minimal": "ganz okay",
            "low": "interessant",
            "medium": "spannend",
            "high": "richtig spannend",
            "extreme": "mega spannend",
        },
        # Negative Adjektive
        "schlecht": {
            "minimal": "nicht so toll",
            "low": "nicht so gut",
            "medium": "schlecht",
            "high": "richtig schlecht",
            "extreme": "echt mies",
        },
        "traurig": {
            "minimal": "ein bisschen down",
            "low": "etwas traurig",
            "medium": "traurig",
            "high": "sehr traurig",
            "extreme": "total traurig",
        },
        "müde": {
            "minimal": "ein bisschen müde",
            "low": "etwas müde",
            "medium": "müde",
            "high": "richtig müde",
            "extreme": "total fertig",
        },
    }

    # Intensitaets-Verstaerker fuer Antworten
    INTENSIFIERS = {
        "minimal": [],
        "low": ["etwas", "ein bisschen"],
        "medium": [],
        "high": ["echt", "wirklich", "richtig"],
        "extreme": ["total", "mega", "so", "voll"],
    }

    # Ausrufezeichen-Mapping
    PUNCTUATION_MAP = {
        "minimal": ".",
        "low": ".",
        "medium": "!",
        "high": "!",
        "extreme": "!!",
    }

    @classmethod
    def modify_response(cls, response: str, target_intensity: str = "medium",
                       match_user_intensity: float = None) -> str:
        """
        Modifiziert die Intensitaet einer Antwort.

        Args:
            response: Die urspruengliche Antwort
            target_intensity: Ziel-Intensitaet ("minimal", "low", "medium", "high", "extreme")
            match_user_intensity: Optional - Intensitaets-Wert zum Anpassen (0-1)

        Returns:
            Modifizierte Antwort
        """
        if match_user_intensity is not None:
            # Berechne target_intensity aus User-Wert
            if match_user_intensity < 0.2:
                target_intensity = "minimal"
            elif match_user_intensity < 0.4:
                target_intensity = "low"
            elif match_user_intensity < 0.6:
                target_intensity = "medium"
            elif match_user_intensity < 0.8:
                target_intensity = "high"
            else:
                target_intensity = "extreme"

        modified = response

        # Ersetze Basis-Adjektive durch intensitaets-passende Varianten
        for base_word, variants in cls.INTENSITY_VARIANTS.items():
            if base_word in modified.lower():
                replacement = variants.get(target_intensity, base_word)
                # Case-preserving replacement
                modified = re.sub(
                    rf"\b{base_word}\b",
                    replacement,
                    modified,
                    flags=re.IGNORECASE
                )

        # Fuer hohe Intensitaet: Verstaerker hinzufuegen
        if target_intensity in ["high", "extreme"]:
            intensifiers = cls.INTENSIFIERS[target_intensity]
            if intensifiers and not any(i in modified.lower() for i in intensifiers):
                # Fuege Verstaerker vor erstem Adjektiv ein
                import random
                intensifier = random.choice(intensifiers)
                # Finde erstes Adjektiv-aehnliches Wort
                adjective_pattern = r"\b(gut|toll|schön|cool|interessant|spannend|lustig)\b"
                match = re.search(adjective_pattern, modified, re.IGNORECASE)
                if match:
                    pos = match.start()
                    modified = modified[:pos] + intensifier + " " + modified[pos:]

        # Satzzeichen anpassen
        target_punct = cls.PUNCTUATION_MAP.get(target_intensity, ".")
        if modified and modified[-1] in ".!?":
            if target_intensity == "extreme" and modified[-1] == "!":
                modified = modified[:-1] + "!!"
            elif target_intensity in ["high", "extreme"] and modified[-1] == ".":
                modified = modified[:-1] + "!"

        return modified

    @classmethod
    def get_intensity_adverb(cls, intensity: str) -> str:
        """Gibt ein passendes Adverb fuer die Intensitaet zurueck."""
        adverbs = {
            "minimal": "",
            "low": "etwas",
            "medium": "",
            "high": "echt",
            "extreme": "total",
        }
        return adverbs.get(intensity, "")


class EmotionalResponseEnhancer:
    """
    Erweitert Holos Antworten mit emotionalen Elementen.

    Basierend auf:
    - Holos aktuellem emotionalen Zustand
    - User's erkannter Emotion
    - Konversationskontext
    """

    # Emotionale Partikel und Interjektionen
    EMOTIONAL_PARTICLES = {
        "happy": ["hehe", "hihi", "yay", "juhu"],
        "excited": ["oh", "wow", "ooh", "aaah"],
        "sad": ["ach", "oh", "hmm"],
        "tired": ["uff", "puh", "seufz"],
        "surprised": ["oh", "wow", "huch", "oha"],
        "thoughtful": ["hmm", "hm", "naja"],
        "playful": ["hehe", "hihi", "höhö"],
        "caring": ["aw", "ohh", "aww"],
        "curious": ["ooh", "hmm", "oh"],
    }

    # Emotionale Satzenden
    EMOTIONAL_ENDINGS = {
        "happy": ["~", "♪", ""],
        "excited": ["!", "!!", "~!"],
        "sad": ["...", "."],
        "tired": ["...", "~"],
        "playful": ["~", "♪", "hehe"],
        "caring": ["~", "♥", ""],
        "curious": ["?", "~?"],
    }

    # Empathie-Phrasen
    EMPATHY_PHRASES = {
        "comfort": [
            "das versteh ich",
            "das kenn ich",
            "das ist nicht leicht",
            "ich bin für dich da",
        ],
        "celebrate": [
            "das freut mich für dich",
            "wie cool",
            "das ist ja toll",
            "ich freu mich mit dir",
        ],
        "curious": [
            "erzähl mir mehr",
            "das klingt interessant",
            "wie meinst du das",
        ],
        "supportive": [
            "du schaffst das",
            "ich glaub an dich",
            "das wird schon",
        ],
    }

    @classmethod
    def enhance(cls, response: str, holo_emotion: str = "neutral",
               user_emotion: str = None, add_particles: bool = True) -> str:
        """
        Erweitert eine Antwort mit emotionalen Elementen.

        Args:
            response: Die Basis-Antwort
            holo_emotion: Holos aktueller emotionaler Zustand
            user_emotion: Erkannte User-Emotion (fuer Empathie)
            add_particles: Ob emotionale Partikel hinzugefuegt werden sollen

        Returns:
            Emotional erweiterte Antwort
        """
        import random

        enhanced = response

        # Emotionale Partikel am Anfang
        if add_particles and holo_emotion in cls.EMOTIONAL_PARTICLES:
            particles = cls.EMOTIONAL_PARTICLES[holo_emotion]
            if random.random() < 0.4:  # 40% Chance
                particle = random.choice(particles)
                # Stelle sicher dass Antwort mit Grossbuchstaben beginnt danach
                if enhanced and enhanced[0].isupper():
                    enhanced = enhanced[0].lower() + enhanced[1:]
                enhanced = f"{particle.capitalize()}, {enhanced}"

        # Emotionale Satzenden
        if holo_emotion in cls.EMOTIONAL_ENDINGS:
            endings = cls.EMOTIONAL_ENDINGS[holo_emotion]
            if random.random() < 0.3:  # 30% Chance
                ending = random.choice(endings)
                # Entferne existierendes Satzzeichen
                if enhanced and enhanced[-1] in ".!?":
                    enhanced = enhanced[:-1]
                enhanced += ending

        return enhanced

    @classmethod
    def add_empathy(cls, response: str, empathy_type: str) -> str:
        """
        Fuegt Empathie-Phrasen hinzu.

        Args:
            response: Die Basis-Antwort
            empathy_type: Art der Empathie ("comfort", "celebrate", "curious", "supportive")

        Returns:
            Antwort mit Empathie
        """
        import random

        if empathy_type not in cls.EMPATHY_PHRASES:
            return response

        phrases = cls.EMPATHY_PHRASES[empathy_type]
        phrase = random.choice(phrases)

        # Empathie-Phrase am Anfang oder Ende
        if random.random() < 0.5:
            return f"{phrase.capitalize()}! {response}"
        else:
            # Entferne Satzzeichen am Ende
            if response and response[-1] in ".!":
                response = response[:-1]
            return f"{response} - {phrase}."

    @classmethod
    def mirror_user_emotion(cls, response: str, user_emotion: str,
                           user_intensity: float = 0.5) -> str:
        """
        Passt Holos Antwort an User-Emotion an (Emotional Mirroring).

        Args:
            response: Die Basis-Antwort
            user_emotion: Die erkannte User-Emotion
            user_intensity: Intensitaet der User-Emotion (0-1)

        Returns:
            Angepasste Antwort
        """
        # Mapping von User-Emotion zu Holo-Response-Typ
        emotion_to_response = {
            "happy": ("celebrate", "happy"),
            "excited": ("celebrate", "excited"),
            "sad": ("comfort", "caring"),
            "tired": ("comfort", "caring"),
            "stressed": ("supportive", "caring"),
            "angry": ("comfort", "thoughtful"),
            "bored": ("curious", "playful"),
            "lonely": ("comfort", "caring"),
            "anxious": ("supportive", "caring"),
        }

        if user_emotion in emotion_to_response:
            empathy_type, holo_emotion = emotion_to_response[user_emotion]

            # Fuege Empathie hinzu
            response = cls.add_empathy(response, empathy_type)

            # Passe Holo's emotionale Expression an
            response = cls.enhance(response, holo_emotion, user_emotion)

            # Intensitaet anpassen
            response = ResponseIntensityModifier.modify_response(
                response,
                match_user_intensity=user_intensity
            )

        return response


class ContextualResponseAdapter:
    """
    Passt Holos Antworten an den Konversationskontext an.

    Beruecksichtigt:
    - Tageszeit (morgens entspannter, abends mueder)
    - Konversationslaenge (wird persoenlicher)
    - Vorherige Topics
    - User's Kommunikationsstil
    """

    # Tageszeit-basierte Anpassungen
    TIME_OF_DAY_MODIFIERS = {
        "morning": {
            "greetings": ["Guten Morgen", "Morgen", "Hey, schon wach?"],
            "energy": 0.7,  # Etwas verschlafen
            "formality": 0.5,
        },
        "midday": {
            "greetings": ["Hey", "Hi", "Na?"],
            "energy": 1.0,  # Volle Energie
            "formality": 0.4,
        },
        "afternoon": {
            "greetings": ["Hey", "Na", "Hi"],
            "energy": 0.9,
            "formality": 0.4,
        },
        "evening": {
            "greetings": ["Hey", "Na", "Noch wach?"],
            "energy": 0.7,
            "formality": 0.3,
        },
        "night": {
            "greetings": ["Hey", "Auch noch wach?", "Na du Nachteule"],
            "energy": 0.5,  # Muede
            "formality": 0.2,  # Sehr informell
        },
    }

    # Formalitaets-Stufen
    FORMALITY_MARKERS = {
        "formal": {
            "affirmations": ["Ja", "Das ist korrekt", "Richtig"],
            "negations": ["Nein", "Das stimmt nicht", "Leider nicht"],
            "fillers": [],
        },
        "neutral": {
            "affirmations": ["Ja", "Jap", "Stimmt"],
            "negations": ["Nein", "Ne", "Nicht wirklich"],
            "fillers": ["also", "naja"],
        },
        "informal": {
            "affirmations": ["Jap", "Jop", "Jo", "Yep"],
            "negations": ["Nö", "Nee", "Nope", "Gar nicht"],
            "fillers": ["also", "naja", "halt", "irgendwie"],
        },
        "very_informal": {
            "affirmations": ["Jo", "Jop", "Yep", "Mhm"],
            "negations": ["Nö", "Nope", "Gar nich", "Null"],
            "fillers": ["halt", "so", "irgendwie", "voll"],
        },
    }

    # Konversationslaenge-Progressionen
    FAMILIARITY_PROGRESSION = [
        (0, "formal"),       # Erste Nachrichten
        (5, "neutral"),      # Nach 5 Nachrichten
        (15, "informal"),    # Nach 15 Nachrichten
        (30, "very_informal"),  # Nach 30 Nachrichten
    ]

    @classmethod
    def get_time_of_day(cls) -> str:
        """Bestimmt die aktuelle Tageszeit."""
        from datetime import datetime
        hour = datetime.now().hour

        if 5 <= hour < 10:
            return "morning"
        elif 10 <= hour < 12:
            return "midday"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"

    @classmethod
    def get_formality_level(cls, message_count: int) -> str:
        """Bestimmt Formalitaets-Level basierend auf Nachrichtenanzahl."""
        level = "formal"
        for threshold, formality in cls.FAMILIARITY_PROGRESSION:
            if message_count >= threshold:
                level = formality
        return level

    @classmethod
    def adapt_response(cls, response: str, message_count: int = 0,
                      user_style: str = None) -> str:
        """
        Passt eine Antwort an den Kontext an.

        Args:
            response: Die Basis-Antwort
            message_count: Anzahl der bisherigen Nachrichten
            user_style: Erkannter Kommunikationsstil des Users

        Returns:
            Kontextuell angepasste Antwort
        """
        import random

        # Bestimme Formalitaet
        formality = cls.get_formality_level(message_count)

        # Passe an User-Stil an wenn bekannt
        if user_style == "very_casual" and formality in ["formal", "neutral"]:
            formality = "informal"

        markers = cls.FORMALITY_MARKERS.get(formality, cls.FORMALITY_MARKERS["neutral"])

        # Fuege gelegentlich Filler-Woerter hinzu (bei informellem Stil)
        if formality in ["informal", "very_informal"] and markers["fillers"]:
            if random.random() < 0.2:  # 20% Chance
                filler = random.choice(markers["fillers"])
                # Am Satzanfang einfuegen
                if response and response[0].isupper():
                    response = response[0].lower() + response[1:]
                response = f"{filler.capitalize()}, {response}"

        # Tageszeit-Anpassung
        time_of_day = cls.get_time_of_day()
        time_mod = cls.TIME_OF_DAY_MODIFIERS.get(time_of_day, {})

        # Energy-basierte Anpassung
        energy = time_mod.get("energy", 1.0)
        if energy < 0.6:
            # Muede: Kuerzere Saetze, mehr Pausen
            if "..." not in response and random.random() < 0.3:
                response = response.replace(". ", "... ")

        return response

    @classmethod
    def get_contextual_greeting(cls, message_count: int = 0) -> str:
        """Gibt eine kontextuelle Begruessung zurueck."""
        import random

        time_of_day = cls.get_time_of_day()
        time_mod = cls.TIME_OF_DAY_MODIFIERS.get(time_of_day, {})
        greetings = time_mod.get("greetings", ["Hey"])

        # Formalitaet beruecksichtigen
        formality = cls.get_formality_level(message_count)
        if formality == "formal" and "Guten Morgen" in greetings:
            return "Guten Morgen"
        elif formality == "very_informal":
            # Waehle informellere Optionen
            informal_greetings = [g for g in greetings if len(g) < 10]
            if informal_greetings:
                return random.choice(informal_greetings)

        return random.choice(greetings)


class HoloResponsePipeline:
    """
    Orchestriert alle Response-Enhancement-Komponenten.

    Pipeline:
    1. Basis-Antwort generieren (extern)
    2. Intensitaet anpassen (basierend auf User-Input)
    3. Emotion hinzufuegen (basierend auf Holo's Zustand)
    4. Kontext anpassen (Tageszeit, Formalitaet)
    5. Finale Antwort

    NEU: Persistenz fuer Konversations-Kontinuitaet
    """

    DEFAULT_STATE_PATH = Path("data/response_pipeline_state.json")

    def __init__(self, persist_path: Path = None, auto_load: bool = True):
        self.message_count = 0
        self.user_style = None
        self.last_user_intensity = 0.5
        self.last_user_emotion = None

        # Persistenz
        self.persist_path = persist_path or self.DEFAULT_STATE_PATH
        self._intensity_history: List[float] = []  # Letzte Intensitaeten
        self._emotion_history: List[str] = []      # Letzte Emotionen

        # Session-Tracking
        self.session_start = time.time()
        self.total_sessions = 1

        # Automatisch laden
        if auto_load:
            self._load_state()

    def _load_state(self) -> bool:
        """Lade gespeicherten State."""
        if not self.persist_path.exists():
            return False

        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            self.message_count = state.get("message_count", 0)
            self.user_style = state.get("user_style")
            self.total_sessions = state.get("total_sessions", 0) + 1
            self._intensity_history = state.get("intensity_history", [])[-20:]
            self._emotion_history = state.get("emotion_history", [])[-20:]

            # Durchschnittliche Intensitaet wiederherstellen
            if self._intensity_history:
                self.last_user_intensity = sum(self._intensity_history) / len(self._intensity_history)

            logger.info(f"[ResponsePipeline] State geladen: {self.message_count} Nachrichten, "
                       f"Session #{self.total_sessions}")
            return True

        except Exception as e:
            logger.warning(f"[ResponsePipeline] State laden fehlgeschlagen: {e}")
            return False

    def save_state(self) -> bool:
        """Speichere aktuellen State."""
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            state = {
                "saved_at": time.time(),
                "message_count": self.message_count,
                "user_style": self.user_style,
                "total_sessions": self.total_sessions,
                "last_user_intensity": self.last_user_intensity,
                "intensity_history": self._intensity_history[-20:],
                "emotion_history": self._emotion_history[-20:],
            }

            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.warning(f"[ResponsePipeline] State speichern fehlgeschlagen: {e}")
            return False

    def get_user_profile(self) -> Dict[str, Any]:
        """
        Gibt ein Profil des Users basierend auf der Konversations-Historie zurueck.

        Nuetzlich fuer personalisierte Antworten.
        """
        avg_intensity = sum(self._intensity_history) / len(self._intensity_history) if self._intensity_history else 0.5

        # Haeufigste Emotion
        if self._emotion_history:
            from collections import Counter
            emotion_counts = Counter(self._emotion_history)
            dominant_emotion = emotion_counts.most_common(1)[0][0]
        else:
            dominant_emotion = None

        # User-Style inferieren
        if avg_intensity > 0.7:
            inferred_style = "expressive"
        elif avg_intensity < 0.3:
            inferred_style = "reserved"
        else:
            inferred_style = "balanced"

        return {
            "avg_intensity": avg_intensity,
            "dominant_emotion": dominant_emotion,
            "inferred_style": inferred_style,
            "message_count": self.message_count,
            "sessions": self.total_sessions,
        }

    def process_user_input(self, user_message: str) -> Dict[str, Any]:
        """
        Analysiert User-Input fuer Response-Anpassung.

        Returns:
            Dict mit Analyse-Ergebnissen fuer Response-Generierung
        """
        self.message_count += 1

        # Analysiere User-Input
        intensity = IntensityAnalyzer.analyze(user_message)
        emotion = UserEmotionDetector.detect(user_message)
        question = QuestionTypeClassifier.classify(user_message)

        self.last_user_intensity = intensity["intensity_value"]

        # NEU: Historie tracken
        self._intensity_history.append(intensity["intensity_value"])
        if len(self._intensity_history) > 50:
            self._intensity_history = self._intensity_history[-50:]

        if emotion["user_shared_emotion"]:
            self.last_user_emotion = emotion["emotion"]
            self._emotion_history.append(emotion["emotion"])
            if len(self._emotion_history) > 50:
                self._emotion_history = self._emotion_history[-50:]

        # Auto-Save alle 10 Nachrichten
        if self.message_count % 10 == 0:
            self.save_state()

        return {
            "intensity": intensity,
            "emotion": emotion,
            "question": question,
            "message_count": self.message_count,
            "user_profile": self.get_user_profile(),  # NEU
        }

    def enhance_response(self, base_response: str, holo_emotion: str = "neutral",
                        analysis: Dict[str, Any] = None) -> str:
        """
        Verbessert eine Basis-Antwort durch alle Enhancement-Stufen.

        Args:
            base_response: Die generierte Basis-Antwort
            holo_emotion: Holos aktueller emotionaler Zustand
            analysis: Ergebnis von process_user_input()

        Returns:
            Vollstaendig verbesserte Antwort
        """
        response = base_response

        # 1. Intensitaet anpassen (User-Mirroring)
        if analysis and "intensity" in analysis:
            response = ResponseIntensityModifier.modify_response(
                response,
                match_user_intensity=analysis["intensity"]["intensity_value"]
            )

        # 2. Emotionale Elemente hinzufuegen
        user_emotion = None
        user_intensity = 0.5
        if analysis and "emotion" in analysis:
            if analysis["emotion"]["user_shared_emotion"]:
                user_emotion = analysis["emotion"]["emotion"]
                user_intensity = analysis["emotion"]["intensity"]

        if user_emotion:
            # Empathisches Mirroring
            response = EmotionalResponseEnhancer.mirror_user_emotion(
                response, user_emotion, user_intensity
            )
        else:
            # Nur Holo's eigene Emotion
            response = EmotionalResponseEnhancer.enhance(
                response, holo_emotion
            )

        # 3. Kontext anpassen
        message_count = analysis.get("message_count", self.message_count) if analysis else self.message_count
        response = ContextualResponseAdapter.adapt_response(
            response,
            message_count=message_count,
            user_style=self.user_style
        )

        return response

    def get_greeting(self, holo_emotion: str = "neutral") -> str:
        """Generiert eine kontextuelle Begruessung."""
        greeting = ContextualResponseAdapter.get_contextual_greeting(
            self.message_count
        )
        return EmotionalResponseEnhancer.enhance(greeting, holo_emotion)


# =============================================================================
# CONVERSATION CONTEXT TRACKER (NEU!)
# =============================================================================

class ConversationContextTracker:
    """
    Trackt den Konversationskontext für bessere Referenz-Auflösung.

    Problem: User sagt "wer ist Raiden Shogun?" dann "kannst du nach ihr suchen?"
    → "ihr" muss zu "Raiden Shogun" aufgelöst werden!

    Lösung:
    1. Extrahiere Named Entities aus jeder User-Nachricht
    2. Speichere sie im Kontext-Stack
    3. Löse Pronomen auf
    4. Erweitere Suchanfragen mit Kontext
    """

    # Pronomen die aufgelöst werden müssen
    REFERENCE_PRONOUNS = {
        "sie": "female",      # sie, ihr, ihre
        "ihr": "female",
        "ihre": "female",
        "er": "male",         # er, ihn, ihm, sein
        "ihn": "male",
        "ihm": "male",
        "sein": "male",
        "seine": "male",
        "es": "neutral",      # es, sein
        "das": "thing",       # das, dies, dieses
        "dies": "thing",
        "dieses": "thing",
        "davon": "topic",     # davon, darüber, dazu
        "darüber": "topic",
        "dazu": "topic",
        "damit": "topic",
    }

    # Patterns für Named Entity Extraction
    ENTITY_PATTERNS = [
        # "wer ist X" → X ist eine Entity
        (r"wer\s+ist\s+(?:eigentlich\s+)?(.+?)[\?\!]?$", "person"),
        # "was ist X" → X ist eine Entity
        (r"was\s+ist\s+(?:eigentlich\s+)?(?:ein[e]?\s+)?(.+?)[\?\!]?$", "thing"),
        # "kennst du X" → X ist eine Entity
        (r"kennst\s+du\s+(.+?)[\?\!]?$", "entity"),
        # "erzähl mir von X" → X ist eine Entity
        (r"erzähl\s+(?:mir\s+)?(?:(?:et)?was\s+)?(?:von|über)\s+(.+?)[\?\!]?$", "entity"),
        # "suche nach X" → X ist eine Entity
        (r"such[e]?\s+(?:mal\s+)?(?:nach\s+)?(.+?)[\?\!]?$", "search_target"),
        # "X aus Genshin/Anime/Game" → X ist ein Charakter
        (r"(.+?)\s+(?:aus|von|in)\s+(?:genshin|anime|spiel|game|serie)", "character"),
    ]

    # Standard-Pfad fuer Kontext-Persistenz
    DEFAULT_CONTEXT_PATH = Path("data/conversation_context.json")

    def __init__(self, max_history: int = 10, persist_path: Path = None, auto_load: bool = True):
        self.message_history: List[Dict] = []  # Letzte Nachrichten
        self.entity_stack: List[Dict] = []     # Erkannte Entities
        self.topic_stack: List[str] = []       # Aktuelle Themen
        self.max_history = max_history

        # Persistenz-Konfiguration
        self.persist_path = persist_path or self.DEFAULT_CONTEXT_PATH
        self._last_save_time = 0
        self._save_interval = 30  # Sekunden zwischen Auto-Saves

        # Session-Tracking
        self.session_start = time.time()
        self.total_messages = 0

        # Automatisch laden wenn vorhanden
        if auto_load:
            self.load_context()

    def add_user_message(self, text: str) -> Dict:
        """
        Verarbeite User-Nachricht und extrahiere Entities.

        Returns:
            Dict mit extrahierten Infos
        """
        text_lower = text.lower().strip()

        # Nachrichtenzaehler erhoehen
        self.total_messages += 1

        # Extrahiere Named Entities
        entities = self._extract_entities(text)

        # Speichere Nachricht
        msg_data = {
            "text": text,
            "timestamp": time.time(),
            "entities": entities,
            "is_question": "?" in text,
        }
        self.message_history.append(msg_data)

        # Trim history
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]

        # Entities zum Stack hinzufügen
        for entity in entities:
            self._add_entity(entity["value"], entity["type"])

        # Auto-Save (alle 30 Sekunden oder bei wichtigen Entities)
        if entities or self.total_messages % 5 == 0:
            self.auto_save()

        # Topic extrahieren
        if entities:
            self.topic_stack.append(entities[0]["value"])
            if len(self.topic_stack) > 5:
                self.topic_stack = self.topic_stack[-5:]

        return msg_data

    def _extract_entities(self, text: str) -> List[Dict]:
        """Extrahiere Named Entities aus Text"""
        entities = []
        text_lower = text.lower()

        for pattern, entity_type in self.ENTITY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                entity_value = match.group(1).strip()
                # Cleanup
                entity_value = re.sub(r"^(der|die|das|ein|eine)\s+", "", entity_value)
                if entity_value and len(entity_value) > 1:
                    entities.append({
                        "value": entity_value,
                        "type": entity_type,
                        "original": match.group(0),
                    })

        # Auch Eigennamen erkennen (Großbuchstaben mitten im Satz)
        words = text.split()
        for i, word in enumerate(words):
            # Wort mit Großbuchstabe das nicht am Satzanfang ist
            if i > 0 and word[0].isupper() and len(word) > 2:
                # Prüfe ob es kein deutsches Nomen ist (die sind auch groß...)
                # Einfache Heuristik: Wenn das nächste Wort auch groß ist, ist es ein Name
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    full_name = word + " " + words[i + 1]
                    entities.append({
                        "value": full_name.lower(),
                        "type": "proper_name",
                        "original": full_name,
                    })

        return entities

    def _add_entity(self, entity: str, entity_type: str):
        """Füge Entity zum Stack hinzu"""
        # Duplikate vermeiden
        for e in self.entity_stack:
            if e["value"].lower() == entity.lower():
                return

        self.entity_stack.append({
            "value": entity,
            "type": entity_type,
            "timestamp": time.time(),
        })

        # Max 20 Entities
        if len(self.entity_stack) > 20:
            self.entity_stack = self.entity_stack[-20:]

    def resolve_references(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Löse Pronomen/Referenzen im Text auf.

        Returns:
            Tuple[resolved_text, resolved_entities]
        """
        resolved_text = text
        resolved_entities = []
        text_lower = text.lower()

        # Prüfe auf Referenz-Pronomen
        for pronoun, pronoun_type in self.REFERENCE_PRONOUNS.items():
            # Wort-Grenzen beachten
            pattern = rf"\b{pronoun}\b"
            if re.search(pattern, text_lower):
                # Finde passende Entity
                resolved = self._find_reference(pronoun_type)
                if resolved:
                    resolved_entities.append({
                        "pronoun": pronoun,
                        "resolved_to": resolved["value"],
                        "type": resolved["type"],
                    })

        return resolved_text, resolved_entities

    def _find_reference(self, pronoun_type: str) -> Optional[Dict]:
        """Finde Entity für Pronomen-Typ"""
        if not self.entity_stack:
            return None

        # Letzte passende Entity
        for entity in reversed(self.entity_stack):
            if pronoun_type == "female" and entity["type"] in ["person", "character", "entity"]:
                return entity
            elif pronoun_type == "male" and entity["type"] in ["person", "character", "entity"]:
                return entity
            elif pronoun_type in ["thing", "topic", "neutral"]:
                return entity

        # Fallback: Letzte Entity (sicher, da entity_stack nicht leer ist nach Check oben)
        return self.entity_stack[-1] if self.entity_stack else None

    def enhance_search_query(self, query: str) -> str:
        """
        Verbessere Suchanfrage mit Kontext.

        "kannst du nach ihr suchen?" → "Raiden Shogun"
        """
        query_lower = query.lower()

        # Prüfe auf Referenzen
        _, resolved = self.resolve_references(query)

        if resolved:
            # Ersetze Query durch aufgelöste Entity
            return resolved[0]["resolved_to"]

        # Prüfe ob Query nur Pronomen ist
        words = query_lower.split()
        pronoun_only = all(w in self.REFERENCE_PRONOUNS or w in ["nach", "suche", "such", "kannst", "du", "mal", "bitte"] for w in words)

        if pronoun_only and self.entity_stack:
            # Nutze letzte Entity
            return self.entity_stack[-1]["value"]

        return query

    def get_context_summary(self) -> Dict:
        """Gibt Kontext-Zusammenfassung zurück"""
        return {
            "recent_entities": [e["value"] for e in self.entity_stack[-5:]],
            "current_topic": self.topic_stack[-1] if self.topic_stack else None,
            "message_count": len(self.message_history),
            "last_question": next(
                (m["text"] for m in reversed(self.message_history) if m["is_question"]),
                None
            ),
        }

    def clear(self):
        """Lösche Kontext"""
        self.message_history = []
        self.entity_stack = []
        self.topic_stack = []
        self.total_messages = 0

    # =========================================================================
    # PERSISTENZ - Kontext speichern und laden
    # =========================================================================

    def save_context(self, force: bool = False) -> bool:
        """
        Speichert den Kontext persistent.

        Args:
            force: Erzwingt Speicherung auch wenn Intervall nicht erreicht

        Returns:
            True wenn gespeichert wurde
        """
        # Auto-Save Intervall pruefen
        now = time.time()
        if not force and (now - self._last_save_time) < self._save_interval:
            return False

        try:
            # Stelle sicher dass Verzeichnis existiert
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            context_data = {
                "version": 2,
                "saved_at": now,
                "session_start": self.session_start,
                "total_messages": self.total_messages,
                "entity_stack": self.entity_stack[-20:],  # Max 20 Entities
                "topic_stack": self.topic_stack[-5:],     # Max 5 Topics
                "message_history": [
                    {
                        "text": m.get("text", "")[:500],  # Truncate
                        "timestamp": m.get("timestamp", 0),
                        "is_question": m.get("is_question", False),
                        # Entities separat gespeichert
                    }
                    for m in self.message_history[-10:]
                ],
                "recent_topics": self._get_recent_topics(),
            }

            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)

            self._last_save_time = now
            logger.debug(f"[ContextTracker] Kontext gespeichert: {len(self.entity_stack)} Entities, {len(self.topic_stack)} Topics")
            return True

        except Exception as e:
            logger.warning(f"[ContextTracker] Kontext speichern fehlgeschlagen: {e}")
            return False

    def load_context(self) -> bool:
        """
        Lädt den Kontext aus persistentem Speicher.

        Returns:
            True wenn erfolgreich geladen
        """
        if not self.persist_path.exists():
            logger.debug("[ContextTracker] Kein gespeicherter Kontext gefunden")
            return False

        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)

            # Version pruefen
            version = context_data.get("version", 1)

            # Kontext wiederherstellen
            self.entity_stack = context_data.get("entity_stack", [])
            self.topic_stack = context_data.get("topic_stack", [])
            self.total_messages = context_data.get("total_messages", 0)

            # Message history wiederherstellen (ohne Entities)
            loaded_history = context_data.get("message_history", [])
            self.message_history = [
                {
                    "text": m.get("text", ""),
                    "timestamp": m.get("timestamp", 0),
                    "is_question": m.get("is_question", False),
                    "entities": [],  # Werden nicht gespeichert
                }
                for m in loaded_history
            ]

            # Pruefe ob Kontext noch aktuell ist (max 24h alt)
            saved_at = context_data.get("saved_at", 0)
            age_hours = (time.time() - saved_at) / 3600
            if age_hours > 24:
                logger.info(f"[ContextTracker] Kontext ist {age_hours:.1f}h alt - wird teilweise verworfen")
                # Alte Entities entfernen, Topics behalten
                self.entity_stack = self.entity_stack[-5:]  # Nur letzte 5

            logger.info(f"[ContextTracker] Kontext geladen: {len(self.entity_stack)} Entities, "
                       f"{len(self.topic_stack)} Topics, {self.total_messages} Nachrichten total")
            return True

        except json.JSONDecodeError as e:
            logger.warning(f"[ContextTracker] Kontext-Datei beschaedigt: {e}")
            return False
        except Exception as e:
            logger.warning(f"[ContextTracker] Kontext laden fehlgeschlagen: {e}")
            return False

    def _get_recent_topics(self) -> List[str]:
        """Extrahiert die wichtigsten Topics aus dem Entity-Stack."""
        topics = []
        for entity in reversed(self.entity_stack[-10:]):
            if entity.get("type") in ["person", "character", "entity", "search_target"]:
                topics.append(entity["value"])
        return topics[:5]

    def auto_save(self):
        """Auto-Save wenn Intervall erreicht."""
        self.save_context(force=False)

    def get_context_summary(self) -> str:
        """
        Gibt eine lesbare Zusammenfassung des Kontexts zurueck.

        Nützlich für Debugging und Anzeige.
        """
        summary_parts = []

        if self.topic_stack:
            summary_parts.append(f"Aktuelle Themen: {', '.join(self.topic_stack[-3:])}")

        if self.entity_stack:
            recent_entities = [e["value"] for e in self.entity_stack[-5:]]
            summary_parts.append(f"Erwähnte Entitäten: {', '.join(recent_entities)}")

        summary_parts.append(f"Nachrichten diese Session: {self.total_messages}")

        return " | ".join(summary_parts) if summary_parts else "Kein Kontext vorhanden"


# =============================================================================
# SMART UNDERSTANDING - HAUPTKLASSE
# =============================================================================

class SmartUnderstanding:
    """
    Zentrale Intent Detection Klasse.

    SINGLE SOURCE OF TRUTH für:
    - Intent Detection (inkl. Multi-Intent)
    - Entity Extraction
    - Sentiment Analysis
    - Follow-up Detection
    - Reference Resolution

    Verwendung:
        su = SmartUnderstanding()
        result = su.understand("hast du news? und was machst du so?")
    """

    def __init__(self):
        # Core Components
        self.normalizer = TextNormalizer()
        self.fuzzy = FuzzyMatcher()
        self.sentiment = SentimentAnalyzer()
        self.entities = EntityExtractor()

        # Intent Detection
        self.keyword_detector = KeywordIntentDetector()
        self.multi_intent = MultiIntentDetector()

        # NEU: User Activity Extraction
        self.user_activity = UserActivityExtractor()
        self.activity_inquiry = ActivityInquiryDetector()

        # NEU: Subject-Verb Analysis und spezialisierte Detektoren
        self.subject_verb = SubjectVerbAnalyzer()
        self.wellbeing_inquiry = WellbeingInquiryDetector()
        self.user_emotion = UserEmotionDetector()

        # NEU: Erweiterte Analyse-Komponenten
        self.negation_handler = NegationHandler()
        self.intensity_analyzer = IntensityAnalyzer()
        self.question_classifier = QuestionTypeClassifier()
        self.implicit_detector = ImplicitIntentDetector()
        self.context_aware = ContextAwareDetector()

        # NEU: Multi-Stage Pipeline (orchestriert alle Detektoren)
        self.pipeline = MultiStageIntentPipeline()

        # NEU: Conversation Context Tracking
        self.context_tracker = ConversationContextTracker()

        # Context & References
        self.shared_tracker = SharedContentTracker()
        self.anaphora = AnaphoraResolverFallback()

        # Sentence Analysis
        self.sentence_analyzer = SentenceAnalyzerImpl

        # Topic Tracking (aus holo_context_mind)
        if _HAS_CONTEXT_MIND and TopicTracker:
            self.topic_tracker = TopicTracker()
        else:
            self.topic_tracker = None

        logger.info("✅ SmartUnderstanding initialisiert (mit MultiStageIntentPipeline)")
        logger.info(f"   Features: NLP={_HAS_NLP_ALGORITHMS}, ContextMind={_HAS_CONTEXT_MIND}, MessageAnalyzer={_HAS_MESSAGE_ANALYZER}")
        logger.info("   NEU: Negation, Intensity, QuestionType, Implicit, ContextAware Detektoren")

    def understand(self, text: str) -> Dict[str, Any]:
        """
        Hauptmethode: Vollständiges Text-Verständnis.

        Returns:
            {
                "original": str,
                "normalized": str,
                "intent": str,
                "confidence": float,
                "intents": List[Dict],  # Alle erkannten Intents
                "is_multi_intent": bool,
                "sentiment": str,
                "sentiment_score": float,
                "entities": List[Dict],
                "is_followup": bool,
                "followup_confidence": float,
                "has_reference": bool,
                "reference_type": str,
                "referenced_content": Optional[Dict],
                "requires_llm": bool,
                "sentence_type": str,
                "context_hint": str,
                "suggested_route": str,
            }
        """
        if not text or not text.strip():
            return self._empty_result()

        text = text.strip()
        normalized = self.normalizer.normalize(text)

        # 0. NEU: Context Tracking - User-Nachricht verarbeiten
        context_data = self.context_tracker.add_user_message(text)

        # 0b. NEU: Referenzen auflösen
        _, resolved_refs = self.context_tracker.resolve_references(text)
        enhanced_query = self.context_tracker.enhance_search_query(text)

        if resolved_refs:
            logger.debug(f"[Context] Resolved references: {resolved_refs}")
            logger.debug(f"[Context] Enhanced query: {enhanced_query}")

        # 1. Satzstruktur-Analyse
        sentence_analysis = self.sentence_analyzer.analyze(text)
        main_segment = sentence_analysis.get('main_segment', text)

        # 2. Multi-Intent Detection
        multi_intents = self.multi_intent.detect_all(text)
        is_multi = len(multi_intents) > 1

        # 3. Keyword-basierte Intent Detection (für primären Intent)
        keyword_match = self.keyword_detector.detect_intent(main_segment)

        # 4. Primären Intent bestimmen
        if keyword_match and keyword_match.confidence > 0.7:
            primary_intent = keyword_match.intent
            primary_confidence = keyword_match.confidence
        elif multi_intents and multi_intents[0].intent_type != IntentType.UNKNOWN:
            primary_intent = multi_intents[0].intent_type.value
            primary_confidence = multi_intents[0].confidence
        else:
            primary_intent = "general"
            primary_confidence = 0.5

        # 5. Follow-up Detection
        is_followup, followup_conf = self.shared_tracker.is_followup(text)

        # 6. Reference Resolution
        has_reference = self.anaphora.has_unresolved_reference(text)
        reference_type = "none"
        referenced_content = None

        if has_reference or is_followup:
            keywords = self.normalizer.extract_keywords(text)
            referenced_content = self.shared_tracker.find_matching_content(keywords)
            if referenced_content:
                reference_type = referenced_content.content_type.value

        # 7. Shared Content Detection (User teilt was)
        shared = self.shared_tracker.detect_shared_content(text)
        if shared:
            self.shared_tracker.add_shared_content(shared)
            # Auch als Topic speichern
            if self.topic_tracker:
                self.topic_tracker.add_message(text, is_user=True)
            self.anaphora.add_topic(shared.summary[:50])

        # 7b. NEU: User Activity Extraction
        user_activity = self.user_activity.extract(text)
        if user_activity:
            logger.debug(f"[Understanding] User Activity: {user_activity}")
            # Wenn User was erzählt hat, Intent anpassen
            if primary_intent == "general" or primary_confidence < 0.6:
                primary_intent = "user_shared_activity"
                primary_confidence = user_activity['confidence']

        # 7c. NEU: Activity Inquiry Detection (verbessert)
        is_activity_inquiry, inquiry_confidence = self.activity_inquiry.is_activity_inquiry(text)
        if is_activity_inquiry and inquiry_confidence > 0.7:
            # Prüfe ob es ein Multi-Intent ist (User erzählt + fragt)
            if user_activity:
                # Beides: User erzählt UND fragt
                if not is_multi:
                    is_multi = True
                    # Füge activity_inquiry hinzu wenn nicht schon vorhanden
                    has_inquiry = any(i.get('intent') == 'activity_inquiry' for i in intents_list)
                    if not has_inquiry:
                        intents_list.append({
                            "intent": "activity_inquiry",
                            "confidence": inquiry_confidence,
                            "priority": 2,  # HIGH
                        })
            else:
                # Nur Activity Inquiry
                primary_intent = "activity_inquiry"
                primary_confidence = inquiry_confidence

        # 7d. NEU: Subject-Verb Analysis (Konjugationsbasierte Erkennung)
        sv_analysis = SubjectVerbAnalyzer.analyze(text)

        # 7e. NEU: Wellbeing Inquiry Detection (Fragen nach Holos Befinden)
        wellbeing_result = WellbeingInquiryDetector.detect(text)
        is_wellbeing_inquiry = wellbeing_result["is_wellbeing_inquiry"]

        if is_wellbeing_inquiry and wellbeing_result["confidence"] > 0.7:
            # Hohe Prioritaet: Frage nach Holos Befinden
            primary_intent = "wellbeing_inquiry"
            primary_confidence = wellbeing_result["confidence"]
            logger.debug(f"[Understanding] Wellbeing inquiry detected: {wellbeing_result['wellbeing_type']}")

        # 7f. NEU: User Emotion Detection (User teilt eigene Emotionen)
        user_emotion_result = UserEmotionDetector.detect(text)

        if user_emotion_result["user_shared_emotion"] and user_emotion_result["confidence"] > 0.7:
            # Wichtig: NUR wenn es KEINE Frage an Holo ist
            if not is_wellbeing_inquiry and sv_analysis["perspective"] != "asking_holo":
                primary_intent = "user_emotion"
                primary_confidence = user_emotion_result["confidence"]
                logger.debug(f"[Understanding] User emotion detected: {user_emotion_result['emotion']}")

        # 8. Sentiment
        sentiment_result = self.sentiment.analyze(text)

        # 9. Entities
        entities = self.entities.extract(text)

        # 10. Requires LLM?
        requires_llm = self._needs_llm(primary_intent, primary_confidence, text)

        # 11. Suggested Route
        suggested_route = self._get_route(primary_intent, is_followup, has_reference)

        # 12. Context Hint
        context_hint = self._get_context_hint(
            primary_intent, is_followup, sentence_analysis.get('user_mood', 'neutral')
        )

        # Intents als List[Dict]
        intents_list = [
            {
                "intent": i.intent_type.value,
                "confidence": i.confidence,
                "priority": i.priority.value,
            }
            for i in multi_intents
        ]

        return {
            "original": text,
            "normalized": normalized,
            "intent": primary_intent,
            "confidence": primary_confidence,
            "intents": intents_list,
            "is_multi_intent": is_multi,
            "sentiment": sentiment_result.sentiment.value,
            "sentiment_score": sentiment_result.score,
            "entities": entities,
            "is_followup": is_followup,
            "followup_confidence": followup_conf,
            "has_reference": has_reference,
            "reference_type": reference_type,
            "referenced_content": {
                "type": referenced_content.content_type.value,
                "summary": referenced_content.summary,
                "keywords": referenced_content.keywords,
            } if referenced_content else None,
            "requires_llm": requires_llm,
            "sentence_type": sentence_analysis.get('sentence_type', 'statement'),
            "context_hint": context_hint,
            "suggested_route": suggested_route,
            # NEU: User Activity
            "user_activity": user_activity,
            "is_activity_inquiry": is_activity_inquiry,
            "activity_inquiry_confidence": inquiry_confidence if is_activity_inquiry else 0.0,
            # NEU: Wellbeing Inquiry (Fragen nach Holos Befinden)
            "is_wellbeing_inquiry": is_wellbeing_inquiry,
            "wellbeing_type": wellbeing_result.get("wellbeing_type"),
            "wellbeing_confidence": wellbeing_result.get("confidence", 0.0),
            # NEU: User Emotion (User teilt eigene Emotionen)
            "user_shared_emotion": user_emotion_result.get("user_shared_emotion", False),
            "user_emotion": user_emotion_result.get("emotion"),
            "user_emotion_intensity": user_emotion_result.get("intensity", 0.5),
            "user_emotion_response_type": user_emotion_result.get("response_type"),
            # NEU: Subject-Verb Analysis
            "subject": sv_analysis.get("subject"),
            "perspective": sv_analysis.get("perspective"),
            "sv_confidence": sv_analysis.get("confidence", 0.0),
            # NEU: Context Tracking
            "resolved_references": resolved_refs,
            "enhanced_query": enhanced_query if enhanced_query != text else None,
            "context_entities": [e["value"] for e in self.context_tracker.entity_stack[-5:]],
            "current_topic": self.context_tracker.topic_stack[-1] if self.context_tracker.topic_stack else None,
        }

    def understand_enhanced(self, text: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Erweiterte Analyse mit voller Multi-Stage Pipeline.

        Nutzt alle neuen Detektoren:
        - NegationHandler: Erkennt Verneinungen
        - IntensityAnalyzer: Analysiert Emotionsstaerke
        - QuestionTypeClassifier: Klassifiziert Fragetypen
        - ImplicitIntentDetector: Erkennt implizite Absichten
        - ContextAwareDetector: Nutzt Konversationsverlauf

        Args:
            text: Der zu analysierende Text
            conversation_history: Optionaler Konversationsverlauf

        Returns:
            Erweitertes Dict mit allen Analyse-Ergebnissen
        """
        # Basis-Analyse
        base_result = self.understand(text)

        # Pipeline-Analyse
        pipeline_result = self.pipeline.process(text, conversation_history)

        # Negation-Analyse
        negation = NegationHandler.analyze(text)

        # Intensity-Analyse
        intensity = IntensityAnalyzer.analyze(text)

        # Question-Type
        question_type = QuestionTypeClassifier.classify(text)

        # Implicit Intent
        implicit = ImplicitIntentDetector.detect(text)

        # Erweitere Basis-Ergebnis
        base_result.update({
            # Pipeline-Ergebnisse
            "pipeline_intent": pipeline_result["final_intent"],
            "pipeline_confidence": pipeline_result["final_confidence"],
            "pipeline_all_intents": pipeline_result["all_intents"],
            "recommended_response_type": pipeline_result["recommended_response_type"],

            # Negation
            "has_negation": negation["has_negation"],
            "negation_strength": negation["negation_strength"],
            "negation_words": negation["negation_words"],
            "effective_polarity": negation["effective_polarity"],

            # Intensity
            "intensity_level": intensity["intensity_level"],
            "intensity_value": intensity["intensity_value"],
            "intensity_modifiers": intensity["modifiers_found"],
            "has_emphasis": intensity["has_emphasis"],

            # Question Classification
            "question_type": question_type["question_type"],
            "question_sub_type": question_type["sub_type"],
            "wh_word": question_type["wh_word"],
            "expects_answer_type": question_type["expects_answer_type"],

            # Implicit Intent
            "has_implicit_intent": implicit["has_implicit_intent"],
            "implicit_intent": implicit["implicit_intent"],
            "implicit_action": implicit["implicit_action"],
            "all_implicit_intents": implicit["all_detected"],

            # Metadata
            "pipeline_metadata": pipeline_result["metadata"],
        })

        return base_result

    def quick_analyze(self, text: str) -> Dict[str, Any]:
        """
        Schnelle Analyse fuer Performance-kritische Anwendungen.

        Nutzt nur die wichtigsten Detektoren.
        """
        return self.pipeline.get_quick_analysis(text)

    def add_response_to_context(self, response: str, intent: str = None):
        """Füge Holo's Antwort zum Kontext hinzu"""
        if self.topic_tracker:
            self.topic_tracker.add_message(response, is_user=False)

    def _empty_result(self) -> Dict:
        """Leeres Ergebnis"""
        return {
            "original": "",
            "normalized": "",
            "intent": "unknown",
            "confidence": 0.0,
            "intents": [],
            "is_multi_intent": False,
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "entities": [],
            "is_followup": False,
            "followup_confidence": 0.0,
            "has_reference": False,
            "reference_type": "none",
            "referenced_content": None,
            "requires_llm": False,
            "sentence_type": "unknown",
            "context_hint": "",
            "suggested_route": "default",
            # NEU
            "user_activity": None,
            "is_activity_inquiry": False,
            "activity_inquiry_confidence": 0.0,
            # Context Tracking
            "resolved_references": [],
            "enhanced_query": None,
            "context_entities": [],
            "current_topic": None,
        }

    def _needs_llm(self, intent: str, confidence: float, text: str) -> bool:
        """Entscheide ob LLM benötigt wird - LOKAL BEVORZUGT!"""
        text_lower = text.lower().strip()
        word_count = len(text.split())

        # === DEFINITIV KEIN LLM ===
        # Einfache Intents die lokal bearbeitet werden können
        no_llm_intents = {
            # Soziale Interaktion
            "greeting", "farewell", "gratitude", "apology",
            "wellbeing_inquiry", "activity_inquiry", "self_info",
            # Commands
            "command_nas_start", "command_nas_stop", "command_light",
            "command_music", "command_tv", "command_timer",
            # Status
            "status_nas", "status_system", "status_network",
            # Einfache Antworten
            "confirmation", "negation", "acknowledgment",
        }

        if intent in no_llm_intents:
            return False

        # Sehr kurze Nachrichten (< 5 Wörter) brauchen selten LLM
        if word_count < 5:
            # Außer bei expliziten Wissensfragen
            knowledge_triggers = ['was ist', 'wer ist', 'wie funktioniert', 'erkläre', 'warum']
            if not any(t in text_lower for t in knowledge_triggers):
                return False

        # Einfache persönliche Fragen
        personal_simple = ['wie geht', "wie geht's", 'wie gehts', 'was machst du',
                          'alles gut', 'alles klar', 'bist du da']
        if any(p in text_lower for p in personal_simple):
            return False

        # Grüße und Verabschiedungen
        greet_bye = ['hallo', 'hey', 'hi', 'moin', 'tschüss', 'bye', 'ciao',
                    'guten morgen', 'guten tag', 'gute nacht', 'bis später']
        if any(g in text_lower for g in greet_bye):
            return False

        # Danke und Entschuldigungen
        thanks_sorry = ['danke', 'dankeschön', 'vielen dank', 'sorry', 'entschuldigung']
        if any(t in text_lower for t in thanks_sorry):
            return False

        # Ja/Nein Antworten
        if text_lower in ['ja', 'nein', 'jep', 'jo', 'ok', 'okay', 'nö', 'ne', 'klar']:
            return False

        # === LLM BENÖTIGT ===
        # Sehr lange Texte (> 20 Wörter) brauchen LLM für gute Antwort
        if word_count > 20:
            return True

        # Explizite Wissensfragen
        knowledge_triggers = ['was ist', 'wer ist', 'wie funktioniert', 'erkläre mir',
                             'warum ist', 'kannst du mir sagen', 'weißt du']
        if any(t in text_lower for t in knowledge_triggers):
            return True

        # Komplexe Themen
        complex_intents = {"question", "topic_explain", "analysis", "comparison",
                         "creative_request", "coding_help", "research"}
        if intent in complex_intents and confidence > 0.7:
            return True

        # Default: KEIN LLM - lokale Verarbeitung bevorzugen!
        return False

    def _get_route(self, intent: str, is_followup: bool, has_reference: bool) -> str:
        """Bestimme Route für Response"""
        if intent.startswith("command_"):
            return "command_handler"
        if intent.startswith("status_"):
            return "status_handler"
        if intent in ["news", "news_detail"]:
            return "news_handler"
        if intent in ["dream"]:
            return "dream_handler"
        if is_followup or has_reference:
            return "context_aware_llm"
        return "llm"

    def _get_context_hint(self, intent: str, is_followup: bool, mood: str) -> str:
        """Generiere Context-Hint für LLM"""
        hints = []

        hint_map = {
            "greeting": "User grüßt - antworte warm und persönlich",
            "farewell": "User verabschiedet sich - antworte herzlich",
            "gratitude": "User bedankt sich - freue dich aufrichtig",
            "activity_inquiry": "User fragt nach deinen Aktivitäten",
            "wellbeing_inquiry": "User fragt nach deinem Befinden",
            "dream": "User fragt nach deinen Träumen",
            "news": "User möchte News - nutze News-Daten",
            "self_info": "User möchte mehr über dich wissen",
            "user_knowledge": "User fragt was du über ihn weißt - nutze Memory",
        }

        if intent in hint_map:
            hints.append(hint_map[intent])

        if is_followup:
            hints.append("Bezieht sich auf vorherigen Kontext")

        if mood in ["sad", "upset", "negative"]:
            hints.append("User scheint unzufrieden - sei einfühlsam")

        return " | ".join(hints) if hints else ""

    def correct_typos(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Korrigiert Tippfehler im Text.

        Args:
            text: Eingabetext

        Returns:
            Tuple (korrigierter_text, Liste der Korrekturen)
        """
        corrections = []
        corrected = text

        # Häufige deutsche Tippfehler
        typo_map = {
            "shcön": "schön",
            "weis": "weiß",
            "weiss": "weiß",
            "das": "dass",  # Kontextabhängig - hier nur wenn nach Verb
            "nciht": "nicht",
            "cih": "ich",
            "udn": "und",
            "auhc": "auch",
            "mcih": "mich",
            "amcht": "macht",
            "hte": "the",
            "teh": "the",
            "wieso": "wieso",
            "wahrscheilich": "wahrscheinlich",
            "vll": "vielleicht",
            "vllt": "vielleicht",
            "eig": "eigentlich",
            "eigtl": "eigentlich",
        }

        words = text.split()
        corrected_words = []

        for word in words:
            word_lower = word.lower().strip(".,!?")
            if word_lower in typo_map:
                correction = typo_map[word_lower]
                # Behalte Groß/Kleinschreibung
                if word[0].isupper():
                    correction = correction.capitalize()
                corrected_words.append(correction)
                corrections.append({
                    "original": word,
                    "corrected": correction,
                    "type": "typo"
                })
            else:
                corrected_words.append(word)

        corrected = " ".join(corrected_words)

        # FuzzyMatcher für unbekannte Wörter nutzen
        if hasattr(self, 'fuzzy') and self.fuzzy:
            for word in words:
                word_clean = word.lower().strip(".,!?")
                if len(word_clean) > 3 and word_clean not in typo_map:
                    # Prüfe ob es ein bekanntes ähnliches Wort gibt
                    match = self.fuzzy.find_best_match(word_clean)
                    if match and match.get("score", 0) > 0.85:
                        suggested = match.get("matched", "")
                        if suggested != word_clean:
                            corrections.append({
                                "original": word,
                                "suggested": suggested,
                                "score": match.get("score"),
                                "type": "fuzzy"
                            })

        return corrected, corrections


# =============================================================================
# ALIASES FÜR KOMPATIBILITÄT
# =============================================================================

SmartUnderstandingV2 = SmartUnderstanding
SmartUnderstandingV3 = SmartUnderstanding


# =============================================================================
# WOLF NEWS FORMATTER (aus holo_message_analyzer)
# =============================================================================

class WolfNewsFormatterFallback:
    """Formatiert News mit Wolf-Persönlichkeit"""

    NEWS_INTRO = [
        "*hebt neugierig den Kopf*",
        "*spitzt die Ohren*",
        "*schaut interessiert auf*",
    ]

    def __init__(self, energy_level: float = 0.7, mood: str = "neutral"):
        self.energy = energy_level
        self.mood = mood

    def format_news(self, news_list: List[Dict], max_items: int = 5) -> str:
        """Formatiere News mit Wolf-Persönlichkeit"""
        if not news_list:
            return "*schaut sich um* Hmm, hab gerade keine neuen Nachrichten gesehen..."

        import random

        response_parts = [random.choice(self.NEWS_INTRO)]
        response_parts.append(" Hab ein paar interessante Sachen gelesen!\n")

        for i, news in enumerate(news_list[:max_items]):
            title = news.get('title', 'Kein Titel')
            source = news.get('source', '?')
            response_parts.append(f"\n• **{source}:** {title}")

        if len(news_list) > max_items:
            response_parts.append(f"\n\n*Ohren zucken* Gibt noch {len(news_list) - max_items} weitere...")

        return "".join(response_parts)


# Nutze holo_message_analyzer Version wenn verfügbar
if _HAS_MESSAGE_ANALYZER:
    WolfNewsFormatterImpl = WolfNewsFormatter
else:
    WolfNewsFormatterImpl = WolfNewsFormatterFallback


# =============================================================================
# CODE-SWITCHING DETECTOR - Erkennt Deutsch-Englisch Mix
# =============================================================================

class CodeSwitchingDetector:
    """
    Erkennt Code-Switching (Sprachwechsel) zwischen Deutsch und Englisch.

    Beispiele:
    - "Das ist so cool, right?"
    - "Let me just kurz nachschauen"
    - "Ich hab das gecheckt"
    """

    # Häufige englische Wörter in deutschem Kontext
    ENGLISH_MARKERS = {
        # Adjektive/Adverbien
        "cool", "nice", "awesome", "amazing", "crazy", "weird", "random",
        "funny", "boring", "interesting", "exciting", "annoying",
        "okay", "ok", "sure", "fine", "great", "perfect", "super",
        # Verben (oft eingedeutscht)
        "check", "gecheckt", "checken", "like", "geliked", "liken",
        "post", "gepostet", "posten", "share", "geshared", "sharen",
        "cancel", "gecancelt", "canceln", "download", "uploaden",
        "streamen", "gestreamt", "gamen", "gegamt",
        # Substantive
        "meeting", "call", "deadline", "feedback", "update", "feature",
        "bug", "issue", "problem", "stuff", "thing", "whatever",
        # Phrasen
        "by the way", "btw", "anyway", "whatever", "you know",
        "i mean", "like", "right", "actually", "basically",
    }

    # Englische Fragen/Tags am Satzende
    ENGLISH_TAGS = [
        r",?\s*right\??$",
        r",?\s*you know\??$",
        r",?\s*i guess\??$",
        r",?\s*isn'?t it\??$",
        r",?\s*(?:ya|yeah)\??$",
    ]

    # Eingedeutschte Verben (Anglizismen)
    GERMANIZED_ENGLISH = [
        (r"\b(?:ge)?check(?:t|en|st)?\b", "check"),
        (r"\b(?:ge)?like(?:t|n|st)?\b", "like"),
        (r"\b(?:ge)?post(?:et|en|est)?\b", "post"),
        (r"\b(?:ge)?share(?:t|n|st)?\b", "share"),
        (r"\b(?:ge)?cancel(?:t|n|st)?\b", "cancel"),
        (r"\b(?:ge)?download(?:et|en)?\b", "download"),
        (r"\b(?:ge)?upload(?:et|en)?\b", "upload"),
        (r"\b(?:ge)?stream(?:t|en)?\b", "stream"),
        (r"\b(?:ge)?game?(?:t|n|st)?\b", "game"),
        (r"\b(?:ge)?chill(?:t|en)?\b", "chill"),
        (r"\b(?:ge)?hype(?:t|n)?\b", "hype"),
        (r"\b(?:ge)?troll(?:t|en)?\b", "troll"),
        (r"\b(?:ge)?spam(?:m)?(?:t|en)?\b", "spam"),
        (r"\b(?:ge)?stalk(?:t|en)?\b", "stalk"),
        (r"\b(?:ge)?flex(?:t|en)?\b", "flex"),
    ]

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt Code-Switching.

        Returns:
            {
                "has_code_switching": bool,
                "primary_language": str,  # "german", "english", "mixed"
                "english_elements": List[str],
                "germanized_verbs": List[str],
                "switch_confidence": float,
            }
        """
        text_lower = text.lower().strip()
        words = text_lower.split()

        result = {
            "has_code_switching": False,
            "primary_language": "german",
            "english_elements": [],
            "germanized_verbs": [],
            "switch_confidence": 0.0,
        }

        english_found = []
        germanized_found = []

        # Suche englische Wörter
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word)
            if clean_word in cls.ENGLISH_MARKERS:
                english_found.append(clean_word)

        # Suche eingedeutschte Verben
        for pattern, verb in cls.GERMANIZED_ENGLISH:
            if re.search(pattern, text_lower):
                germanized_found.append(verb)

        # Prüfe englische Tags am Ende
        for pattern in cls.ENGLISH_TAGS:
            if re.search(pattern, text_lower):
                english_found.append("english_tag")

        # Ergebnis berechnen
        total_english = len(english_found) + len(germanized_found)
        if total_english > 0:
            result["has_code_switching"] = True
            result["english_elements"] = english_found
            result["germanized_verbs"] = germanized_found
            result["switch_confidence"] = min(total_english * 0.25, 1.0)

            # Bestimme primäre Sprache
            german_words = len([w for w in words if w not in cls.ENGLISH_MARKERS])
            if len(english_found) > german_words:
                result["primary_language"] = "english"
            elif total_english >= 2:
                result["primary_language"] = "mixed"

        return result


# =============================================================================
# SEPARABLE VERB HANDLER - Deutsche trennbare Verben
# =============================================================================

class SeparableVerbHandler:
    """
    Erkennt und analysiert deutsche trennbare Verben.

    Beispiele:
    - "aufwachen" → "ich wache auf"
    - "anrufen" → "ich rufe dich an"
    - "einkaufen" → "ich kaufe ein"
    """

    # Trennbare Präfixe mit Bedeutung
    SEPARABLE_PREFIXES = {
        "ab": "away/off",
        "an": "on/at",
        "auf": "up/open",
        "aus": "out",
        "bei": "with/near",
        "ein": "in/into",
        "fest": "firm",
        "her": "here/hither",
        "hin": "there/thither",
        "los": "loose/off",
        "mit": "with/along",
        "nach": "after",
        "vor": "before/forward",
        "weg": "away",
        "weiter": "further",
        "zu": "to/closed",
        "zurück": "back",
        "zusammen": "together",
    }

    # Häufige trennbare Verben mit Stammformen
    COMMON_SEPARABLE_VERBS = {
        "aufwachen": ("wach", "auf"),
        "aufstehen": ("steh", "auf"),
        "aufhören": ("hör", "auf"),
        "aufmachen": ("mach", "auf"),
        "aufpassen": ("pass", "auf"),
        "anrufen": ("ruf", "an"),
        "ankommen": ("komm", "an"),
        "anfangen": ("fang", "an"),
        "anmachen": ("mach", "an"),
        "anziehen": ("zieh", "an"),
        "ausgehen": ("geh", "aus"),
        "aussehen": ("seh", "aus"),
        "ausschalten": ("schalt", "aus"),
        "einladen": ("lad", "ein"),
        "einschlafen": ("schlaf", "ein"),
        "einkaufen": ("kauf", "ein"),
        "einsteigen": ("steig", "ein"),
        "mitkommen": ("komm", "mit"),
        "mitnehmen": ("nehm", "mit"),
        "mitmachen": ("mach", "mit"),
        "nachdenken": ("denk", "nach"),
        "weggehen": ("geh", "weg"),
        "wegwerfen": ("werf", "weg"),
        "zuhören": ("hör", "zu"),
        "zumachen": ("mach", "zu"),
        "zurückkommen": ("komm", "zurück"),
        "zusammenarbeiten": ("arbeit", "zusammen"),
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt trennbare Verben (getrennt oder zusammen).

        Returns:
            {
                "has_separable_verb": bool,
                "verbs_found": List[Dict],  # [{infinitive, stem, prefix, is_separated}]
                "reconstructed": str | None,  # Rekonstruierter Infinitiv
            }
        """
        text_lower = text.lower().strip()

        result = {
            "has_separable_verb": False,
            "verbs_found": [],
            "reconstructed": None,
        }

        # 1. Suche nach getrennten Verben (Stamm ... Präfix am Ende)
        for infinitive, (stem, prefix) in cls.COMMON_SEPARABLE_VERBS.items():
            # Pattern: Stamm + Konjugation ... Präfix am Satzende
            pattern = rf"\b{stem}(?:e|st|t|en)?\b.*\b{prefix}\b"
            if re.search(pattern, text_lower):
                result["has_separable_verb"] = True
                result["verbs_found"].append({
                    "infinitive": infinitive,
                    "stem": stem,
                    "prefix": prefix,
                    "is_separated": True,
                })

        # 2. Suche nach zusammengeschriebenen Infinitiven
        for infinitive in cls.COMMON_SEPARABLE_VERBS.keys():
            if infinitive in text_lower:
                result["has_separable_verb"] = True
                stem, prefix = cls.COMMON_SEPARABLE_VERBS[infinitive]
                result["verbs_found"].append({
                    "infinitive": infinitive,
                    "stem": stem,
                    "prefix": prefix,
                    "is_separated": False,
                })

        # Rekonstruiere Infinitiv wenn möglich
        if result["verbs_found"]:
            result["reconstructed"] = result["verbs_found"][0]["infinitive"]

        return result


# =============================================================================
# EMOJI INTENT DETECTOR - Erkennt Intent aus Emojis
# =============================================================================

class EmojiIntentDetector:
    """
    Erkennt Intent und Emotion aus Emojis und Emoticons.

    Beispiele:
    - "😊" → positive Emotion
    - "😢" → Traurigkeit
    - "🎮" → Gaming-Kontext
    """

    # Emoji zu Emotion Mapping
    EMOJI_EMOTIONS = {
        # Positive
        "😊": ("happy", 0.8), "😄": ("happy", 0.9), "😁": ("happy", 0.85),
        "🙂": ("happy", 0.5), "😀": ("happy", 0.7), "😃": ("happy", 0.8),
        "🥰": ("love", 0.9), "😍": ("love", 0.85), "❤️": ("love", 0.8),
        "💕": ("love", 0.7), "💖": ("love", 0.75), "🥳": ("excited", 0.9),
        "🎉": ("excited", 0.8), "✨": ("excited", 0.6),

        # Negative
        "😢": ("sad", 0.8), "😭": ("sad", 0.95), "😞": ("sad", 0.7),
        "😔": ("sad", 0.65), "🥺": ("sad", 0.6), "😿": ("sad", 0.7),
        "😠": ("angry", 0.8), "😡": ("angry", 0.9), "🤬": ("angry", 1.0),
        "😤": ("frustrated", 0.7), "💢": ("angry", 0.75),

        # Müdigkeit/Erschöpfung
        "😴": ("tired", 0.9), "🥱": ("tired", 0.8), "😪": ("tired", 0.75),
        "💤": ("tired", 0.85), "😫": ("exhausted", 0.85),

        # Verwirrt/Nachdenklich
        "🤔": ("thinking", 0.8), "😕": ("confused", 0.7), "🧐": ("curious", 0.7),
        "❓": ("question", 0.9), "❔": ("question", 0.7),

        # Neutral/Sarkastisch
        "😐": ("neutral", 0.5), "😑": ("annoyed", 0.6), "🙄": ("sarcastic", 0.8),
        "😒": ("annoyed", 0.7), "😏": ("sarcastic", 0.75),
    }

    # Emoji zu Intent/Kontext Mapping
    EMOJI_CONTEXT = {
        "🎮": "gaming", "🕹️": "gaming", "👾": "gaming",
        "🎬": "watching", "📺": "watching", "🍿": "watching",
        "🎵": "music", "🎶": "music", "🎧": "music",
        "📚": "reading", "📖": "reading", "📕": "reading",
        "💻": "computing", "🖥️": "computing", "⌨️": "computing",
        "🍕": "food", "🍔": "food", "🍜": "food", "☕": "food",
        "🏠": "home", "🏡": "home", "🛋️": "home",
        "💤": "sleep", "🛏️": "sleep", "😴": "sleep",
        "👋": "greeting", "✋": "greeting", "🖐️": "greeting",
        "👍": "approval", "👎": "disapproval", "👌": "approval",
        "🙏": "request", "🤲": "request",
        "⚠️": "warning", "❗": "important", "❌": "rejection",
        "✅": "confirmation", "✔️": "confirmation",
    }

    # Text-Emoticons
    TEXT_EMOTICONS = {
        ":)": ("happy", 0.6), ":-)": ("happy", 0.6), ":D": ("happy", 0.8),
        ":(": ("sad", 0.6), ":-(": ("sad", 0.6), ":'(": ("sad", 0.8),
        ";)": ("playful", 0.6), ";-)": ("playful", 0.6),
        ":P": ("playful", 0.5), ":-P": ("playful", 0.5),
        "xD": ("laughing", 0.8), "XD": ("laughing", 0.9),
        ":O": ("surprised", 0.7), ":-O": ("surprised", 0.7),
        ":/": ("skeptical", 0.6), ":-/": ("skeptical", 0.6),
        "<3": ("love", 0.7), "</3": ("heartbreak", 0.8),
        "^^": ("happy", 0.5), "^_^": ("happy", 0.6),
        "-_-": ("annoyed", 0.7), "._." : ("neutral", 0.4),
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt Emojis und deren Bedeutung.

        Returns:
            {
                "has_emoji": bool,
                "emotions": List[Tuple[str, float]],  # [(emotion, intensity)]
                "contexts": List[str],  # ["gaming", "music", ...]
                "dominant_emotion": str | None,
                "dominant_context": str | None,
                "emoji_count": int,
            }
        """
        result = {
            "has_emoji": False,
            "emotions": [],
            "contexts": [],
            "dominant_emotion": None,
            "dominant_context": None,
            "emoji_count": 0,
        }

        emotions = []
        contexts = []

        # Suche Emojis
        for emoji, (emotion, intensity) in cls.EMOJI_EMOTIONS.items():
            count = text.count(emoji)
            if count > 0:
                result["has_emoji"] = True
                result["emoji_count"] += count
                # Mehrfache Emojis verstärken
                adjusted_intensity = min(intensity + (count - 1) * 0.1, 1.0)
                emotions.append((emotion, adjusted_intensity))

        # Suche Kontext-Emojis
        for emoji, context in cls.EMOJI_CONTEXT.items():
            if emoji in text:
                result["has_emoji"] = True
                contexts.append(context)

        # Suche Text-Emoticons
        for emoticon, (emotion, intensity) in cls.TEXT_EMOTICONS.items():
            if emoticon in text:
                result["has_emoji"] = True
                emotions.append((emotion, intensity))

        result["emotions"] = emotions
        result["contexts"] = list(set(contexts))

        # Bestimme dominante Emotion
        if emotions:
            sorted_emotions = sorted(emotions, key=lambda x: x[1], reverse=True)
            result["dominant_emotion"] = sorted_emotions[0][0]

        if contexts:
            result["dominant_context"] = contexts[0]

        return result


# =============================================================================
# INTERNET SLANG DETECTOR - Erkennt Internet-Slang und Abkürzungen
# =============================================================================

class InternetSlangDetector:
    """
    Erkennt Internet-Slang, Abkürzungen und Jugendsprache.

    Beispiele:
    - "lol" → Lachen
    - "omg" → Überraschung
    - "wtf" → Verärgerung/Überraschung
    """

    # Slang zu Emotion/Intent Mapping
    SLANG_MAPPING = {
        # Lachen/Humor
        "lol": ("laughing", "humor", 0.7),
        "lmao": ("laughing", "humor", 0.85),
        "lmfao": ("laughing", "humor", 0.95),
        "rofl": ("laughing", "humor", 0.9),
        "haha": ("laughing", "humor", 0.6),
        "hahaha": ("laughing", "humor", 0.75),
        "hihi": ("laughing", "humor", 0.5),
        "xd": ("laughing", "humor", 0.7),
        "kek": ("laughing", "humor", 0.6),

        # Überraschung
        "omg": ("surprised", "exclamation", 0.8),
        "omfg": ("surprised", "exclamation", 0.95),
        "wtf": ("confused", "exclamation", 0.85),
        "wth": ("confused", "exclamation", 0.7),
        "wow": ("surprised", "exclamation", 0.6),

        # Zustimmung
        "ok": ("neutral", "agreement", 0.5),
        "okay": ("neutral", "agreement", 0.5),
        "k": ("neutral", "agreement", 0.4),
        "kk": ("neutral", "agreement", 0.5),
        "jap": ("neutral", "agreement", 0.6),
        "jo": ("neutral", "agreement", 0.5),
        "jup": ("neutral", "agreement", 0.55),
        "yep": ("neutral", "agreement", 0.55),
        "yup": ("neutral", "agreement", 0.55),
        "yas": ("excited", "agreement", 0.7),
        "yass": ("excited", "agreement", 0.8),

        # Ablehnung
        "nope": ("neutral", "rejection", 0.6),
        "nah": ("neutral", "rejection", 0.5),
        "nö": ("neutral", "rejection", 0.5),
        "nee": ("neutral", "rejection", 0.5),

        # Emotionen
        "ugh": ("annoyed", "frustration", 0.7),
        "meh": ("bored", "indifference", 0.6),
        "yay": ("excited", "celebration", 0.8),
        "aww": ("touched", "endearment", 0.7),
        "oops": ("embarrassed", "mistake", 0.6),
        "ups": ("embarrassed", "mistake", 0.55),

        # Abkürzungen
        "btw": ("neutral", "addition", 0.3),
        "afk": ("neutral", "status", 0.4),
        "brb": ("neutral", "status", 0.4),
        "gtg": ("neutral", "farewell", 0.5),
        "g2g": ("neutral", "farewell", 0.5),
        "bbl": ("neutral", "farewell", 0.4),
        "imo": ("neutral", "opinion", 0.4),
        "imho": ("neutral", "opinion", 0.45),
        "tbh": ("neutral", "honesty", 0.5),
        "idk": ("confused", "uncertainty", 0.5),
        "idc": ("bored", "indifference", 0.6),
        "nvm": ("neutral", "dismissal", 0.5),
        "thx": ("grateful", "gratitude", 0.6),
        "ty": ("grateful", "gratitude", 0.55),
        "np": ("neutral", "acknowledgment", 0.4),
        "yw": ("neutral", "acknowledgment", 0.4),
        "pls": ("neutral", "request", 0.5),
        "plz": ("neutral", "request", 0.5),

        # Deutsch-spezifisch
        "lg": ("neutral", "farewell", 0.4),  # Liebe Grüße
        "mfg": ("neutral", "farewell", 0.3),  # Mit freundlichen Grüßen
        "vlg": ("neutral", "farewell", 0.35),  # Viele liebe Grüße
        "hdl": ("love", "affection", 0.7),  # Hab dich lieb
        "hdgdl": ("love", "affection", 0.8),  # Hab dich ganz doll lieb
        "ild": ("love", "affection", 0.75),  # Ich liebe dich
        "ka": ("confused", "uncertainty", 0.5),  # Keine Ahnung
        "kp": ("confused", "uncertainty", 0.5),  # Kein Plan
        "kb": ("bored", "refusal", 0.6),  # Kein Bock
        "omw": ("neutral", "status", 0.4),  # On my way
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt Internet-Slang.

        Returns:
            {
                "has_slang": bool,
                "slang_found": List[Dict],  # [{term, emotion, intent, intensity}]
                "dominant_emotion": str | None,
                "implies_farewell": bool,
                "implies_agreement": bool,
                "formality_level": str,  # "very_informal", "informal", "neutral"
            }
        """
        text_lower = text.lower().strip()
        words = re.findall(r"\b\w+\b", text_lower)

        result = {
            "has_slang": False,
            "slang_found": [],
            "dominant_emotion": None,
            "implies_farewell": False,
            "implies_agreement": False,
            "formality_level": "neutral",
        }

        slang_found = []
        emotions = []

        for word in words:
            if word in cls.SLANG_MAPPING:
                emotion, intent, intensity = cls.SLANG_MAPPING[word]
                slang_found.append({
                    "term": word,
                    "emotion": emotion,
                    "intent": intent,
                    "intensity": intensity,
                })
                emotions.append((emotion, intensity))

                if intent == "farewell":
                    result["implies_farewell"] = True
                if intent == "agreement":
                    result["implies_agreement"] = True

        if slang_found:
            result["has_slang"] = True
            result["slang_found"] = slang_found
            result["formality_level"] = "very_informal" if len(slang_found) > 2 else "informal"

            # Dominante Emotion
            if emotions:
                sorted_emotions = sorted(emotions, key=lambda x: x[1], reverse=True)
                result["dominant_emotion"] = sorted_emotions[0][0]

        return result


# =============================================================================
# TEMPORAL REFERENCE DETECTOR - Erkennt Zeitbezüge
# =============================================================================

class TemporalReferenceDetector:
    """
    Erkennt implizite und explizite Zeitbezüge.

    Beispiele:
    - "später" → Zukunft (unbestimmt)
    - "gleich" → Nahe Zukunft
    - "gestern" → Vergangenheit
    """

    # Zeitreferenzen mit relativer Position und Spezifität
    TEMPORAL_MARKERS = {
        # Nahe Zukunft
        "gleich": ("future", "immediate", 0.9),
        "sofort": ("future", "immediate", 1.0),
        "jetzt": ("present", "immediate", 1.0),
        "gerade": ("present", "immediate", 0.95),
        "momentan": ("present", "current", 0.9),
        "aktuell": ("present", "current", 0.85),

        # Nahe Zukunft (Minuten bis Stunden)
        "bald": ("future", "soon", 0.7),
        "nachher": ("future", "soon", 0.75),
        "später": ("future", "later", 0.6),
        "demnächst": ("future", "soon", 0.65),
        "in kürze": ("future", "soon", 0.7),

        # Ferne Zukunft
        "morgen": ("future", "tomorrow", 0.95),
        "übermorgen": ("future", "day_after", 0.95),
        "nächste woche": ("future", "next_week", 0.9),
        "nächsten monat": ("future", "next_month", 0.9),
        "irgendwann": ("future", "indefinite", 0.3),

        # Vergangenheit
        "gestern": ("past", "yesterday", 0.95),
        "vorgestern": ("past", "day_before", 0.95),
        "letzte woche": ("past", "last_week", 0.9),
        "letzten monat": ("past", "last_month", 0.9),
        "vorhin": ("past", "recent", 0.8),
        "eben": ("past", "just_now", 0.9),
        "gerade eben": ("past", "just_now", 0.95),
        "früher": ("past", "indefinite", 0.5),
        "damals": ("past", "distant", 0.4),

        # Wiederholung
        "wieder": ("recurring", "repetition", 0.7),
        "nochmal": ("recurring", "repetition", 0.8),
        "immer": ("recurring", "always", 0.9),
        "nie": ("recurring", "never", 0.9),
        "manchmal": ("recurring", "sometimes", 0.6),
        "oft": ("recurring", "often", 0.7),
        "selten": ("recurring", "rarely", 0.7),

        # Dauer
        "lange": ("duration", "long", 0.7),
        "kurz": ("duration", "short", 0.7),
        "den ganzen tag": ("duration", "all_day", 0.9),
        "die ganze nacht": ("duration", "all_night", 0.9),
        "stundenlang": ("duration", "hours", 0.85),
    }

    # Zeitliche Signale für Intent
    TEMPORAL_INTENT_SIGNALS = {
        # Signal für Abschied
        r"\b(?:muss|sollte)\s+(?:jetzt|gleich|bald)\s+(?:los|gehen|schlafen)": "farewell_soon",
        r"\b(?:bis|auf)\s+(?:später|morgen|bald|dann|gleich)\b": "farewell",
        r"\bgute\s+nacht\b": "farewell_night",

        # Signal für Fortsetzung
        r"\b(?:wir\s+)?(?:machen|reden)\s+(?:später|morgen|dann)\s+weiter": "continue_later",
        r"\bein\s+andermal\b": "postpone",
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt Zeitbezüge.

        Returns:
            {
                "has_temporal_reference": bool,
                "references": List[Dict],  # [{marker, tense, specificity, confidence}]
                "primary_tense": str | None,  # "past", "present", "future", "recurring"
                "temporal_intent": str | None,  # "farewell", "continue_later", etc.
                "urgency_level": float,  # 0-1, wie dringend
            }
        """
        text_lower = text.lower().strip()

        result = {
            "has_temporal_reference": False,
            "references": [],
            "primary_tense": None,
            "temporal_intent": None,
            "urgency_level": 0.5,
        }

        references = []
        tense_counts = {"past": 0, "present": 0, "future": 0, "recurring": 0, "duration": 0}

        # Suche Zeitmarker (längere zuerst)
        sorted_markers = sorted(
            cls.TEMPORAL_MARKERS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for marker, (tense, specificity, confidence) in sorted_markers:
            if marker in text_lower:
                result["has_temporal_reference"] = True
                references.append({
                    "marker": marker,
                    "tense": tense,
                    "specificity": specificity,
                    "confidence": confidence,
                })
                tense_counts[tense] += 1

                # Urgency basierend auf Spezifität
                if specificity == "immediate":
                    result["urgency_level"] = max(result["urgency_level"], 0.9)
                elif specificity == "soon":
                    result["urgency_level"] = max(result["urgency_level"], 0.7)

        result["references"] = references

        # Primäre Zeitform bestimmen
        if references:
            primary = max(tense_counts.items(), key=lambda x: x[1])
            if primary[1] > 0:
                result["primary_tense"] = primary[0]

        # Zeitliche Intent-Signale
        for pattern, intent in cls.TEMPORAL_INTENT_SIGNALS.items():
            if re.search(pattern, text_lower):
                result["temporal_intent"] = intent
                break

        return result


# =============================================================================
# ELLIPSIS HANDLER - Erkennt unvollständige Sätze
# =============================================================================

class EllipsisHandler:
    """
    Erkennt und interpretiert Ellipsen (unvollständige Sätze).

    Beispiele:
    - "Und du?" → Rückfrage auf vorherige Aussage
    - "Auch nicht" → Negierte Übereinstimmung
    - "Morgen dann" → Bezug auf vorherigen Vorschlag
    """

    # Elliptische Phrasen mit Interpretation
    ELLIPSIS_PATTERNS = {
        # Rückfragen
        r"^und\s+(?:du|sie|ihr)\??$": ("reciprocal_question", "Rückfrage nach gleichem Thema"),
        r"^(?:du|sie)\s+(?:auch|nicht)\??$": ("reciprocal_question", "Rückfrage mit Modifikator"),
        r"^(?:was|wie)\s+(?:ist\s+)?mit\s+(?:dir|ihnen|euch)\??$": ("reciprocal_question", "Was ist mit dir?"),
        r"^selber\??$": ("reciprocal", "Gleiches gilt für dich"),
        r"^(?:und\s+)?selbst\??$": ("reciprocal", "Gleiches gilt für dich"),

        # Zustimmung/Ablehnung
        r"^(?:ich\s+)?auch(?:\s+nicht)?\.?$": ("agreement", "Übereinstimmung"),
        r"^(?:ich\s+)?(?:auch\s+)?nicht\.?$": ("disagreement", "Verneinte Übereinstimmung"),
        r"^(?:genau|eben|richtig)\.?$": ("confirmation", "Bestätigung"),
        r"^(?:stimmt|wahr)\.?$": ("confirmation", "Bestätigung"),
        r"^dito\.?$": ("agreement", "Zustimmung"),
        r"^same\.?$": ("agreement", "Zustimmung"),

        # Zeitliche Ellipsen
        r"^(?:dann\s+)?(?:morgen|später|nachher)\.?$": ("temporal_reference", "Zeitliche Bestätigung"),
        r"^(?:bis|auf)\s+(?:dann|später|morgen|bald)\.?$": ("farewell", "Verabschiedung"),
        r"^(?:dann\s+)?(?:mal\s+)?(?:sehen|schauen)\.?$": ("uncertainty", "Wir werden sehen"),

        # Kausale/Begründende
        r"^(?:weil|da|denn)\s*\.\.\.$": ("incomplete_reason", "Unvollständige Begründung"),
        r"^(?:deshalb|daher|darum)\.?$": ("reference_to_cause", "Bezug auf Grund"),

        # Emotionale
        r"^(?:oh|ach)\s+(?:so|ja)\.?$": ("understanding", "Verständnis"),
        r"^(?:na\s+)?(?:ja|gut|okay)\.?$": ("reluctant_agreement", "Zögerliche Zustimmung"),
        r"^(?:schon\s+)?(?:klar|logisch)\.?$": ("understanding", "Selbstverständlich"),
        r"^(?:wenn\s+)?schon\.?$": ("resignation", "Resignation"),

        # Fragmente
        r"^(?:also|naja|hmm?)\.{0,3}$": ("hesitation", "Zögern"),
        r"^\.{3,}$": ("trailing_off", "Verstummen"),
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        """
        Erkennt und interpretiert Ellipsen.

        Returns:
            {
                "is_ellipsis": bool,
                "ellipsis_type": str | None,
                "interpretation": str | None,
                "needs_context": bool,
                "implied_subject": str | None,  # "ich", "du", etc.
                "confidence": float,
            }
        """
        text_lower = text.lower().strip()

        result = {
            "is_ellipsis": False,
            "ellipsis_type": None,
            "interpretation": None,
            "needs_context": False,
            "implied_subject": None,
            "confidence": 0.0,
        }

        # Sehr kurze Texte sind oft Ellipsen
        word_count = len(text.split())
        if word_count <= 3:
            result["needs_context"] = True

        # Suche bekannte Ellipsen-Muster
        for pattern, (etype, interpretation) in cls.ELLIPSIS_PATTERNS.items():
            if re.match(pattern, text_lower):
                result["is_ellipsis"] = True
                result["ellipsis_type"] = etype
                result["interpretation"] = interpretation
                result["confidence"] = 0.85

                # Implizites Subjekt bestimmen
                if "du" in text_lower or "dir" in text_lower:
                    result["implied_subject"] = "du"
                elif "ich" in text_lower or "auch" in text_lower:
                    result["implied_subject"] = "ich"

                return result

        # Generische Ellipsen-Erkennung
        if word_count <= 2 and not re.search(r"[.!?]", text):
            result["is_ellipsis"] = True
            result["ellipsis_type"] = "fragment"
            result["needs_context"] = True
            result["confidence"] = 0.5

        return result


# =============================================================================
# CONTEXT INTENT INHERITOR - Vererbt Intent aus Kontext
# =============================================================================

class ContextIntentInheritor:
    """
    Vererbt und modifiziert Intent basierend auf Konversationskontext.

    Beispiele:
    - Nach "Wie geht's dir?" → "Und dir?" erbt WELLBEING_INQUIRY
    - Nach "Ich spiele gerade" → "Cool, was?" erbt ACTIVITY_INQUIRY
    """

    # Intent-Vererbungsregeln
    INHERITANCE_RULES = {
        # (vorheriger_intent, aktuelles_pattern) → neuer_intent
        ("wellbeing_inquiry", r"^und\s+(?:du|dir)\??$"): "wellbeing_inquiry",
        ("activity_inquiry", r"^(?:was|welches?)\??$"): "activity_detail_inquiry",
        ("greeting", r"^(?:hi|hallo|hey)\s+(?:auch|zurück)?\??$"): "greeting_response",
        ("farewell", r"^(?:du\s+)?auch\.?$"): "farewell_response",
        ("question", r"^(?:und|aber)\s+(?:warum|wieso)\??$"): "followup_question",
    }

    # Kontext-Modifikatoren
    CONTEXT_MODIFIERS = {
        "auch": "reciprocal",
        "nicht": "negation",
        "wirklich": "emphasis",
        "vielleicht": "uncertainty",
        "eigentlich": "contrast",
    }

    @classmethod
    def inherit_intent(
        cls,
        current_text: str,
        previous_intent: str,
        previous_text: str = ""
    ) -> Dict[str, Any]:
        """
        Bestimmt Intent basierend auf vorherigem Kontext.

        Returns:
            {
                "inherited_intent": str | None,
                "modification": str | None,  # "reciprocal", "negation", etc.
                "refers_to_previous": bool,
                "confidence": float,
            }
        """
        text_lower = current_text.lower().strip()

        result = {
            "inherited_intent": None,
            "modification": None,
            "refers_to_previous": False,
            "confidence": 0.0,
        }

        # Prüfe Vererbungsregeln
        for (prev_intent, pattern), new_intent in cls.INHERITANCE_RULES.items():
            if previous_intent == prev_intent and re.match(pattern, text_lower):
                result["inherited_intent"] = new_intent
                result["refers_to_previous"] = True
                result["confidence"] = 0.85
                break

        # Prüfe Modifikatoren
        for modifier, mod_type in cls.CONTEXT_MODIFIERS.items():
            if modifier in text_lower:
                result["modification"] = mod_type

        # Generische Referenz-Erkennung
        reference_patterns = [
            r"^(?:und|aber)\s+",  # Konjunktion am Anfang
            r"\b(?:das|dies|es)\b",  # Demonstrativpronomen
            r"^(?:ja|nein|doch),?\s+",  # Antwort-Partikel
        ]

        for pattern in reference_patterns:
            if re.search(pattern, text_lower):
                result["refers_to_previous"] = True
                if not result["inherited_intent"]:
                    result["inherited_intent"] = previous_intent
                    result["confidence"] = 0.6
                break

        return result


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_understanding() -> SmartUnderstanding:
    """Factory für SmartUnderstanding"""
    return SmartUnderstanding()


def understand(text: str) -> Dict[str, Any]:
    """Quick-Funktion für einmalige Analyse"""
    su = SmartUnderstanding()
    return su.understand(text)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=" * 70)
    print("🧠 HOLO SMART UNDERSTANDING v3.0 - TEST")
    print("=" * 70)

    su = SmartUnderstanding()

    print(f"\n📦 Features aktiviert:")
    print(f"   NLP Algorithms: {_HAS_NLP_ALGORITHMS}")
    print(f"   Context Mind: {_HAS_CONTEXT_MIND}")
    print(f"   Message Analyzer: {_HAS_MESSAGE_ANALYZER}")

    # Test-Nachrichten
    test_messages = [
        # Multi-Intent
        "hast du news? und was machst du so?",

        # Einzel-Intents
        "hallo!",
        "was weißt du über mich",
        "nas status",
        "was hast du geträumt",

        # Typo-Toleranz
        "nass statis",  # nas status mit Typos
        "kii erklärenb",  # KI erklären mit Typos

        # Follow-up
        "was denkst du darüber?",
        "erzähl mir mehr davon",

        # Komplex
        "danke, aber ich wollte eigentlich wissen wie kalt es im wohnzimmer ist",
    ]

    print("\n📊 INTENT DETECTION TESTS:")
    print("-" * 70)

    for msg in test_messages:
        print(f"\n💬 '{msg}'")
        result = su.understand(msg)

        print(f"   🎯 Intent: {result['intent']} (conf: {result['confidence']:.2f})")
        print(f"   🔄 Multi-Intent: {result['is_multi_intent']}")
        if result['is_multi_intent']:
            intents_str = ", ".join(i['intent'] for i in result['intents'])
            print(f"      Intents: [{intents_str}]")
        print(f"   💭 Sentiment: {result['sentiment']} ({result['sentiment_score']:.2f})")
        print(f"   🔗 Follow-up: {result['is_followup']}")
        print(f"   📍 Route: {result['suggested_route']}")
        if result['entities']:
            print(f"   📦 Entities: {result['entities']}")

    # Fuzzy Matching Test
    print("\n\n📏 FUZZY MATCHING (mit Kölner Phonetik):")
    print("-" * 70)

    fuzzy = FuzzyMatcher()
    test_pairs = [
        ("nass", "nas"),
        ("tempertur", "temperatur"),
        ("Meyer", "Meier"),
        ("kii", "ki"),
    ]

    for typo, correct in test_pairs:
        sim = fuzzy.combined_similarity(typo, correct)
        phon = KoelnerPhonetik.similarity(typo, correct)
        print(f"   '{typo}' ↔ '{correct}': combined={sim:.2f}, phonetic={phon:.2f}")

    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
