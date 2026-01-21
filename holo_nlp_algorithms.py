#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NLP ALGORITHMS v4.0 - Text Analysis & Generation Engine                ║
║                                                                              ║
║  SPEZIALISIERUNG: Fortgeschrittene Textanalyse & Generierung                 ║
║                                                                              ║
║  KERNFUNKTIONEN:                                                             ║
║  • Advanced Fuzzy Matching (Jaro-Winkler, Damerau-Levenshtein, Phonetik)     ║
║  • Sentiment Analysis (N-Gram, Negation Scope, Sarkasmus)                    ║
║  • Entity Extraction (NER-light, Slot-Filling)                               ║
║  • Word Embeddings (Co-occurrence, PMI)                                      ║
║  • Text Summarization (Extractive, Keyword-based)                            ║
║  • Text Generation (Markov-Chain, Templates)                                 ║
║  • Semantic Similarity                                                       ║
║  • Dependency Parsing (Simplified)                                           ║
║  • Dialogue Act Classification                                               ║
║                                                                              ║
║  IMPORT FÜR INTENT DETECTION:                                                ║
║  → from holo_smart_understanding import SmartUnderstanding                   ║
║                                                                              ║
║  Andere Module sollten DIESE Klasse für Textanalyse nutzen!                  ║
║                                                                              ║
║  Version: 4.0 (Refactored - Single Responsibility)                           ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import random
import logging
import time
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from functools import lru_cache

logger = logging.getLogger("HoloNLP")

# =============================================================================
# PUBLIC API - Exported symbols
# =============================================================================

__all__ = [
    # Core Classes
    "HoloNLP",
    "HoloNLPV2",

    # Fuzzy Matching
    "AdvancedFuzzyMatcher",

    # Sentiment Analysis
    "AdvancedSentimentAnalyzer",
    "SentimentResult",

    # Entity Extraction
    "EntityExtractor",
    "Entity",

    # Intent Detection (legacy, use SmartUnderstanding instead)
    "TFIDFIntentDetector",
    "IntentDatabase",

    # Parsing & Structure
    "GermanSentenceParser",
    "SimpleDependencyParser",
    "DependencyRelation",

    # Embeddings & Vectors
    "LightweightVectorEngine",
    "SimpleWordEmbeddings",

    # Text Generation
    "TextSummarizer",
    "MarkovTextGenerator",
    "TemplateTextGenerator",

    # Dialogue & Coherence
    "DialogueActClassifier",
    "DialogueActType",
    "CoherenceScorer",
    "AntiRepetitionTracker",

    # Search
    "SemanticSearchEngine",

    # Extended NLP v4.1
    "EmotionalToneAnalyzer",
    "ContextualResponseGenerator",
    "SemanticClusterEngine",
    "AdaptiveMarkovChain",
    "HumorDetector",

    # Helper Functions
    "get_smart_understanding",
    "has_smart_understanding",
    "create_nlp",
]

# =============================================================================
# ENTITY DATABASE IMPORT
# =============================================================================

_HAS_ENTITY_DB = False

try:
    from holo_entity_database import (
        get_all_male_names,
        get_all_female_names,
        get_all_names_with_gender,
        get_all_known_entities,
        GAMING_CHARACTERS,
        ANIME_CHARACTERS,
        GAMES,
        TECHNOLOGY,
    )
    _HAS_ENTITY_DB = True
    logger.info("✅ holo_entity_database importiert")
except ImportError:
    logger.debug("⚠️ holo_entity_database nicht verfügbar, nutze eingebaute Daten")


# =============================================================================
# LIGHTWEIGHT VECTOR ENGINE - Für Raspberry Pi optimiert
# =============================================================================

class LightweightVectorEngine:
    """
    Leichtgewichtige TF-IDF Vector Engine für Raspberry Pi.

    Kein PyTorch/TensorFlow nötig!
    Nur Python + math (optional: numpy für Speed)

    Features:
    - TF-IDF Vectorization
    - Cosine Similarity
    - Intent Matching
    - Semantic Search
    - LLM-Routing Entscheidung
    """

    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.intent_vectors: Dict[str, List[float]] = {}
        self.intent_examples: Dict[str, List[str]] = {}
        self.document_count = 0

        # Stopwords (werden ignoriert)
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber", "ist",
            "sind", "war", "waren", "hat", "haben", "wird", "werden", "kann",
            "können", "muss", "müssen", "soll", "sollen", "ich", "du", "er",
            "sie", "es", "wir", "ihr", "mir", "dir", "mich", "dich", "sich",
            "den", "dem", "des", "im", "in", "an", "auf", "für", "mit", "bei",
            "zu", "von", "aus", "nach", "über", "unter", "vor", "hinter",
            "nicht", "auch", "noch", "schon", "nur", "sehr", "so", "wie",
            "was", "wer", "wo", "wann", "warum", "wenn", "dann", "denn",
            "mal", "bitte", "ja", "nein", "okay", "ok", "hm", "ähm",
        }

        # Standard Intent-Beispiele für Training
        self._init_intent_examples()
        self._build_vectors()

    def _init_intent_examples(self):
        """Definiere Beispiel-Sätze für jeden Intent"""
        self.intent_examples = {
            # ===== GREETINGS (kein LLM nötig) =====
            "greeting": [
                "hallo", "hi", "hey", "guten morgen", "guten tag", "guten abend",
                "moin", "servus", "huhu", "na", "hallöchen", "grüß dich",
                "hallo holo", "hi holo", "hey holo", "guten morgen holo",
            ],

            "farewell": [
                "tschüss", "bye", "auf wiedersehen", "bis später", "bis dann",
                "ciao", "machs gut", "gute nacht", "schlaf gut", "bis morgen", "nacht", "gn8", "schlaf schön", "träum süß",
            ],

            # ===== HOLO-SPEZIFISCH (kein LLM nötig) =====
            "holo_identity": [
                "wer bist du", "was bist du", "wie heißt du", "was ist dein name",
                "bist du eine ki", "bist du ein bot", "bist du echt",
                "erzähl mir von dir", "stell dich vor", "wer ist holo",
            ],

            "holo_feelings": [
                "wie geht es dir", "wie gehts", "wie fühlst du dich",
                "geht es dir gut", "alles klar bei dir", "was machst du",
                "bist du müde", "bist du glücklich", "bist du traurig",
                "und dir", "und bei dir", "was geht bei dir",
            ],

            "holo_capabilities": [
                "was kannst du", "was sind deine fähigkeiten", "hilf mir",
                "kannst du mir helfen", "was kannst du alles", "zeig was du kannst",
            ],

            # ===== SYSTEM COMMANDS (kein LLM nötig) =====
            "nas_wake": [
                "weck das nas", "nas aufwecken", "nas starten", "nas an",
                "server starten", "nas hochfahren", "wake nas", "start nas",
                "mach das nas an", "nas einschalten",
            ],

            "nas_sleep": [
                "nas schlafen", "nas ausschalten", "nas herunterfahren",
                "nas suspend", "nas aus", "server ausschalten",
                "leg das nas schlafen", "nas in standby",
            ],

            "nas_status": [
                "nas status", "ist das nas an", "läuft das nas",
                "nas info", "wie geht es dem nas", "server status",
                "ist der server an", "nas check",
            ],

            "system_status": [
                "system status", "wie geht es dem system", "alles okay",
                "systeminfo", "status check", "health check",
            ],

            # ===== MEDIA/INFO (kein LLM nötig) =====
            "weather": [
                "wie ist das wetter", "wetter heute", "wird es regnen",
                "scheint die sonne", "wie warm ist es", "wetter morgen",
                "wettervorhersage", "brauche ich einen regenschirm",
            ],

            "time": [
                "wie spät ist es", "uhrzeit", "welcher tag ist heute",
                "welches datum", "wie viel uhr", "aktuelle zeit",
            ],

            "news": [
                "gibt es news", "was gibt es neues", "nachrichten",
                "neuigkeiten", "aktuelle news", "was ist passiert",
            ],

            # ===== SMALLTALK (kein LLM nötig) =====
            "joke": [
                "erzähl einen witz", "mach einen witz", "witz bitte",
                "kannst du witze", "sag was lustiges", "bring mich zum lachen",
            ],

            "compliment": [
                "du bist toll", "du bist super", "ich mag dich",
                "du bist die beste", "danke holo", "gut gemacht",
            ],

            "bored": [
                "mir ist langweilig", "was soll ich machen", "keine ahnung was tun",
                "ich weiß nicht was ich machen soll", "unterhalt mich",
            ],

            # ===== USER STATEMENTS (kein LLM nötig) =====
            "user_activity": [
                "ich spiele gerade", "ich schaue gerade", "ich höre gerade",
                "ich arbeite gerade", "ich lerne gerade", "ich bin beschäftigt",
                "ich zocke", "ich game", "ich bin am spielen",
            ],

            "user_feeling": [
                "mir geht es gut", "mir geht es schlecht", "ich bin müde",
                "ich bin happy", "ich bin traurig", "ich bin gestresst",
                "ich fühle mich gut", "ich fühle mich schlecht",
            ],

            # ===== META (kein LLM nötig) =====
            "thanks": [
                "danke", "vielen dank", "dankeschön", "danke dir",
                "thanks", "thx", "merci", "ich danke dir",
            ],

            "confirmation": [
                "ja", "ja genau", "richtig", "stimmt", "korrekt",
                "genau so", "exakt", "ja bitte", "mach das",
            ],

            "negation": [
                "nein", "ne", "nö", "falsch", "stimmt nicht",
                "das ist falsch", "nicht richtig",
            ],

            "correction": [
                "nein ich meinte", "nicht das sondern", "ich meinte eigentlich",
                "falsch verstanden", "das war anders gemeint",
            ],

            "repeat": [
                "nochmal", "wiederholen", "wie bitte", "was hast du gesagt",
                "sag das nochmal", "ich habe nicht verstanden",
            ],

            # ===== BENÖTIGT LLM =====
            "complex_question": [
                "erkläre mir", "was bedeutet", "warum ist", "wie funktioniert",
                "kannst du erklären", "ich verstehe nicht", "was ist der unterschied",
                "erzähl mir mehr über", "was weißt du über", "beschreibe",
            ],

            "creative_request": [
                "schreib mir", "erfinde", "erstelle", "generiere",
                "schreib eine geschichte", "schreib ein gedicht", "sei kreativ",
            ],

            "opinion_request": [
                "was denkst du", "was meinst du", "was ist deine meinung",
                "wie siehst du das", "findest du", "glaubst du",
            ],

            "advice_request": [
                "was soll ich tun", "gib mir einen rat", "was empfiehlst du",
                "hast du einen tipp", "wie würdest du", "was würdest du machen",
            ],

            "search_request": [
                "such nach", "google mal", "finde heraus", "recherchiere",
                "such mir", "kannst du nachschauen", "schau mal nach",
            ],

            # ===== TEXT-VERARBEITUNG (Pi kann teilweise selbst) =====
            "summarize_request": [
                "fass zusammen", "zusammenfassung", "fasse zusammen",
                "kurz zusammenfassen", "was steht da", "worum geht es",
                "kannst du zusammenfassen", "gib mir eine zusammenfassung",
                "tldr", "in kürze", "auf den punkt",
            ],

            "read_request": [
                "lies das", "lies vor", "was steht in", "kannst du lesen",
                "schau dir an", "analysiere", "was sagt der text",
                "lies den artikel", "lies die news",
            ],

            "keyword_request": [
                "wichtige wörter", "keywords", "schlüsselwörter",
                "worum geht es hauptsächlich", "hauptthemen",
            ],

            "knowledge_request": [
                "was hast du gelernt", "was weißt du", "dein wissen",
                "was hast du dir gemerkt", "zeig mir was du weißt",
                "deine wissensdatenbank", "wissen statistik",
                "wie viel weißt du", "was kannst du mir erzählen",
                "zeig dein wissen", "lernfortschritt",
            ],

            # ===== NEWS (Pi holt, formatiert lokal) =====
            "news_request": [
                "welche news", "was gibt es neues", "aktuelle nachrichten",
                "news bitte", "zeig mir news", "gibt es neuigkeiten",
                "was ist passiert", "was gibt es für news",
                "nachrichten", "schlagzeilen", "headlines",
                "was gibts neues", "gibts news", "hast du news",
                "news heute", "aktuelle news", "neueste nachrichten",
                "zeig nachrichten", "was passiert in der welt",
            ],

            "tech_news_request": [
                "technik news", "tech news", "technologie nachrichten",
                "was gibt es neues in technik", "it news", "computer news",
                "technik nachrichten", "neue technik", "tech schlagzeilen",
                "was gibt es neues in der technik", "technik neuigkeiten",
            ],

            "gaming_news_request": [
                "gaming news", "spiele news", "game news", "zocken news",
                "was gibt es neues bei spielen", "neue spiele", "spielenews",
                "gamestar", "pc games news", "gaming neuigkeiten",
                "was gibt es neues in gaming", "videospiel news",
                "zeig mir game news", "games news", "spiele nachrichten",
                "was gibt es neues zum zocken", "neuigkeiten gaming",
            ],
        }

        # Markiere welche Intents LLM brauchen
        self.needs_llm = {
            "complex_question", "creative_request", "opinion_request",
            "advice_request", "search_request",
        }

        # Intents die Pi teilweise selbst kann (mit Fallback zu LLM)
        self.pi_capable = {
            "summarize_request", "read_request", "keyword_request",
            "news_request", "tech_news_request", "gaming_news_request",
            "knowledge_request",
        }

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiere und normalisiere Text"""
        text = text.lower()
        # Entferne Satzzeichen
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split und filtere Stopwords + kurze Wörter
        tokens = [w for w in text.split() if w not in self.stopwords and len(w) > 1]
        return tokens

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Berechne Term Frequency"""
        tf = Counter(tokens)
        total = len(tokens) if tokens else 1
        return {term: count / total for term, count in tf.items()}

    def _build_vocabulary(self):
        """Baue Vokabular aus allen Intent-Beispielen"""
        all_tokens = set()
        doc_freq = Counter()

        for intent, examples in self.intent_examples.items():
            for example in examples:
                tokens = self._tokenize(example)
                all_tokens.update(tokens)
                # Document frequency
                unique_tokens = set(tokens)
                for token in unique_tokens:
                    doc_freq[token] += 1
                self.document_count += 1

        # Vokabular aufbauen
        self.vocabulary = {token: idx for idx, token in enumerate(sorted(all_tokens))}

        # IDF berechnen
        for token, freq in doc_freq.items():
            self.idf[token] = math.log((self.document_count + 1) / (freq + 1)) + 1

    def _text_to_vector(self, text: str) -> List[float]:
        """Konvertiere Text zu TF-IDF Vector"""
        tokens = self._tokenize(text)
        tf = self._compute_tf(tokens)

        vector = [0.0] * len(self.vocabulary)
        for token, freq in tf.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                idf = self.idf.get(token, 1.0)
                vector[idx] = freq * idf

        # Normalisieren
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Berechne Cosine Similarity zwischen zwei Vektoren"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        # Vektoren sind bereits normalisiert, also ist dot_product = cosine
        return dot_product

    def _build_vectors(self):
        """Baue Intent-Vektoren aus Beispielen"""
        self._build_vocabulary()

        for intent, examples in self.intent_examples.items():
            # Kombiniere alle Beispiele zu einem "Centroid"
            vectors = [self._text_to_vector(ex) for ex in examples]

            if vectors:
                # Durchschnitts-Vektor
                centroid = [0.0] * len(self.vocabulary)
                for vec in vectors:
                    for i, v in enumerate(vec):
                        centroid[i] += v
                centroid = [v / len(vectors) for v in centroid]

                # Normalisieren
                magnitude = math.sqrt(sum(v * v for v in centroid))
                if magnitude > 0:
                    centroid = [v / magnitude for v in centroid]

                self.intent_vectors[intent] = centroid

        logger.info(f"✅ VectorEngine: {len(self.vocabulary)} Tokens, {len(self.intent_vectors)} Intents")

    def find_intent(self, text: str, threshold: float = 0.3) -> Tuple[Optional[str], float]:
        """
        Finde besten Intent für Text.

        Returns:
            (intent_name, confidence) oder (None, 0.0)
        """
        if not text.strip():
            return None, 0.0

        text_vector = self._text_to_vector(text)

        best_intent = None
        best_score = 0.0

        for intent, intent_vector in self.intent_vectors.items():
            score = self._cosine_similarity(text_vector, intent_vector)
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_score >= threshold:
            return best_intent, best_score
        return None, best_score

    def find_top_intents(self, text: str, n: int = 3) -> List[Tuple[str, float]]:
        """Finde Top-N Intents"""
        text_vector = self._text_to_vector(text)

        scores = []
        for intent, intent_vector in self.intent_vectors.items():
            score = self._cosine_similarity(text_vector, intent_vector)
            scores.append((intent, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:n]

    def needs_llm_response(self, text: str, threshold: float = 0.35) -> Tuple[bool, str, float]:
        """
        Entscheide ob LLM benötigt wird.

        Returns:
            (needs_llm: bool, intent: str, confidence: float)
        """
        intent, confidence = self.find_intent(text, threshold=0.2)

        if intent is None:
            # Kein Intent erkannt → LLM für Sicherheit
            return True, "unknown", 0.0

        if confidence < threshold:
            # Unsicher → LLM
            return True, intent, confidence

        if intent in self.needs_llm:
            # Intent benötigt explizit LLM
            return True, intent, confidence

        # Einfacher Intent → kein LLM nötig
        return False, intent, confidence

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Berechne semantische Ähnlichkeit zwischen zwei Texten"""
        vec1 = self._text_to_vector(text1)
        vec2 = self._text_to_vector(text2)
        return self._cosine_similarity(vec1, vec2)

    def find_similar(self, query: str, candidates: List[str], top_n: int = 5) -> List[Tuple[str, float]]:
        """Finde ähnlichste Texte aus Kandidaten"""
        query_vec = self._text_to_vector(query)

        scored = []
        for candidate in candidates:
            candidate_vec = self._text_to_vector(candidate)
            score = self._cosine_similarity(query_vec, candidate_vec)
            scored.append((candidate, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def add_intent_example(self, intent: str, example: str):
        """Füge neues Beispiel zu Intent hinzu (Runtime-Learning)"""
        if intent not in self.intent_examples:
            self.intent_examples[intent] = []

        self.intent_examples[intent].append(example)

        # Rebuild nur für diesen Intent
        vectors = [self._text_to_vector(ex) for ex in self.intent_examples[intent]]
        if vectors:
            centroid = [0.0] * len(self.vocabulary)
            for vec in vectors:
                for i, v in enumerate(vec):
                    centroid[i] += v
            centroid = [v / len(vectors) for v in centroid]

            magnitude = math.sqrt(sum(v * v for v in centroid))
            if magnitude > 0:
                centroid = [v / magnitude for v in centroid]

            self.intent_vectors[intent] = centroid


# =============================================================================
# OPTIONAL: IMPORT SMART UNDERSTANDING FÜR INTENT
# =============================================================================

def get_smart_understanding(_cache: Dict[str, Any] = {"instance": None, "checked": False}) -> Optional[Any]:
    """
    Lazy-load SmartUnderstanding.

    Uses function-closure cache to avoid global variables.
    The _cache parameter should NOT be passed by callers - it's an internal cache.

    Returns:
        SmartUnderstanding instance or None if not available.
    """
    if _cache["checked"]:
        return _cache["instance"]

    try:
        from holo_smart_understanding import SmartUnderstanding
        _cache["instance"] = SmartUnderstanding()
        _cache["checked"] = True
        logger.info("✅ SmartUnderstanding für Intent Detection geladen")
        return _cache["instance"]
    except ImportError:
        logger.debug("⚠️ SmartUnderstanding nicht verfügbar")
        _cache["checked"] = True
        _cache["instance"] = None
        return None


def has_smart_understanding() -> bool:
    """Check if SmartUnderstanding is available."""
    return get_smart_understanding() is not None


# =============================================================================
# FUZZY MATCHING - Verbesserte Algorithmen
# =============================================================================

class AdvancedFuzzyMatcher:
    """
    Fortgeschrittenes Fuzzy Matching mit mehreren Algorithmen.

    Kombiniert:
    - Jaro-Winkler (gut für Tippfehler am Anfang)
    - Damerau-Levenshtein (Transpositionen)
    - Phonetische Ähnlichkeit (Kölner Phonetik für Deutsch)
    - N-Gram Similarity (für längere Texte)
    """

    def __init__(self):
        self.cache = {}
        self.phonetic_cache = {}

    # =========================================================================
    # JARO-WINKLER DISTANCE
    # =========================================================================

    @staticmethod
    @lru_cache(maxsize=10000)
    def jaro_similarity(s1: str, s2: str) -> float:
        """Jaro Similarity - Basis für Jaro-Winkler."""
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

        return jaro

    @staticmethod
    def jaro_winkler(s1: str, s2: str, prefix_weight: float = 0.1) -> float:
        """Jaro-Winkler Similarity - bevorzugt gleiche Präfixe."""
        jaro = AdvancedFuzzyMatcher.jaro_similarity(s1, s2)

        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        return jaro + prefix_len * prefix_weight * (1 - jaro)

    # =========================================================================
    # DAMERAU-LEVENSHTEIN DISTANCE
    # =========================================================================

    @staticmethod
    @lru_cache(maxsize=10000)
    def damerau_levenshtein(s1: str, s2: str) -> int:
        """Damerau-Levenshtein Distanz (mit Transpositionen)."""
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

    @staticmethod
    def damerau_levenshtein_similarity(s1: str, s2: str) -> float:
        """Normalisierte Damerau-Levenshtein Similarity (0-1)"""
        if not s1 and not s2:
            return 1.0
        distance = AdvancedFuzzyMatcher.damerau_levenshtein(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1.0 - (distance / max_len)

    # =========================================================================
    # KÖLNER PHONETIK (Deutsche Phonetik)
    # =========================================================================

    @staticmethod
    @lru_cache(maxsize=5000)
    def cologne_phonetic(word: str) -> str:
        """Kölner Phonetik - Phonetischer Algorithmus für Deutsch."""
        if not word:
            return ""

        word = word.lower()

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
                code = ""

            if code and code != prev_code:
                result.append(code)
                prev_code = code

        result_str = "".join(result)
        if len(result_str) > 1:
            result_str = result_str[0] + result_str[1:].replace("0", "")

        return result_str

    def phonetic_similarity(self, s1: str, s2: str) -> float:
        """Phonetische Ähnlichkeit basierend auf Kölner Phonetik"""
        key = (s1, s2)
        if key in self.phonetic_cache:
            return self.phonetic_cache[key]

        p1 = self.cologne_phonetic(s1)
        p2 = self.cologne_phonetic(s2)

        if p1 == p2:
            similarity = 1.0
        else:
            similarity = self.jaro_winkler(p1, p2) * 0.9

        self.phonetic_cache[key] = similarity
        return similarity

    # =========================================================================
    # N-GRAM SIMILARITY
    # =========================================================================

    @staticmethod
    def get_ngrams(text: str, n: int = 2) -> Set[str]:
        """Extrahiere N-Grams aus Text"""
        if len(text) < n:
            return {text}
        return {text[i:i+n] for i in range(len(text) - n + 1)}

    @staticmethod
    def ngram_similarity(s1: str, s2: str, n: int = 2) -> float:
        """N-Gram Similarity (Jaccard)."""
        if not s1 or not s2:
            return 0.0 if s1 != s2 else 1.0

        ngrams1 = AdvancedFuzzyMatcher.get_ngrams(s1.lower(), n)
        ngrams2 = AdvancedFuzzyMatcher.get_ngrams(s2.lower(), n)

        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)

        return intersection / union if union > 0 else 0.0

    # =========================================================================
    # KOMBINIERTE ÄHNLICHKEIT
    # =========================================================================

    def combined_similarity(self, s1: str, s2: str,
                           weights: Dict[str, float] = None) -> float:
        """Kombinierte Ähnlichkeit aus allen Algorithmen."""
        if s1 == s2:
            return 1.0

        weights = weights or {
            "jaro_winkler": 0.4,
            "damerau": 0.3,
            "phonetic": 0.2,
            "ngram": 0.1,
        }

        s1_lower = s1.lower()
        s2_lower = s2.lower()

        scores = {
            "jaro_winkler": self.jaro_winkler(s1_lower, s2_lower),
            "damerau": self.damerau_levenshtein_similarity(s1_lower, s2_lower),
            "phonetic": self.phonetic_similarity(s1_lower, s2_lower),
            "ngram": self.ngram_similarity(s1_lower, s2_lower),
        }

        total_weight = sum(weights.values())
        combined = sum(scores[k] * weights.get(k, 0) for k in scores)

        return combined / total_weight if total_weight > 0 else 0.0

    def find_best_match(self, query: str, candidates: List[str],
                       threshold: float = 0.7) -> Tuple[Optional[str], float]:
        """Finde besten Match aus Kandidaten."""
        if not query or not candidates:
            return None, 0.0

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

    def find_all_matches(self, query: str, candidates: List[str],
                        threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Finde alle Matches über Threshold, sortiert nach Score"""
        matches = []
        for candidate in candidates:
            score = self.combined_similarity(query, candidate)
            if score >= threshold:
                matches.append((candidate, score))

        return sorted(matches, key=lambda x: x[1], reverse=True)


# =============================================================================
# SENTIMENT ANALYSE - Verbessert
# =============================================================================

@dataclass
class SentimentResult:
    """Ergebnis der Sentiment-Analyse"""
    sentiment: str
    confidence: float
    score: float
    positive_indicators: List[Tuple[str, float]] = field(default_factory=list)
    negative_indicators: List[Tuple[str, float]] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    is_sarcastic: bool = False
    is_mixed: bool = False


class AdvancedSentimentAnalyzer:
    """
    Fortgeschrittene Sentiment-Analyse mit:
    - N-Gram basierter Erkennung
    - Negation Scope
    - Sarkasmus-Erkennung
    - Emoji-Analyse
    - Intensitäts-Modellierung
    """

    def __init__(self):
        self._init_lexicons()
        self._init_patterns()

    def _init_lexicons(self):
        """Initialisiere Sentiment-Lexika"""

        self.sentiment_lexicon = {
            # Sehr positiv
            "fantastisch": (1.0, 0.8), "großartig": (1.0, 0.7),
            "wunderbar": (0.95, 0.6), "genial": (0.95, 0.8),
            "perfekt": (1.0, 0.5), "liebe": (0.9, 0.7),
            "hammer": (0.9, 0.9), "mega": (0.85, 0.8),
            "geil": (0.85, 0.8), "krass": (0.8, 0.9),

            # Positiv
            "super": (0.8, 0.6), "toll": (0.75, 0.5),
            "gut": (0.6, 0.3), "schön": (0.65, 0.4),
            "nett": (0.5, 0.2), "okay": (0.3, 0.1),
            "freue": (0.7, 0.6), "glücklich": (0.8, 0.6),
            "zufrieden": (0.6, 0.3), "entspannt": (0.5, 0.1),
            "cool": (0.6, 0.4), "nice": (0.6, 0.4),
            "spitze": (0.8, 0.6), "prima": (0.7, 0.4),
            "klasse": (0.75, 0.5), "top": (0.8, 0.5),

            # Leicht negativ
            "langweilig": (-0.3, 0.1), "öde": (-0.35, 0.1),
            "naja": (-0.2, 0.1), "meh": (-0.25, 0.1),
            "müde": (-0.2, 0.2), "erschöpft": (-0.4, 0.3),

            # Negativ
            "schlecht": (-0.6, 0.4), "blöd": (-0.5, 0.4),
            "doof": (-0.45, 0.3), "nervig": (-0.55, 0.5),
            "stressig": (-0.5, 0.6), "anstrengend": (-0.4, 0.5),
            "traurig": (-0.7, 0.4), "enttäuscht": (-0.6, 0.4),
            "frustriert": (-0.65, 0.6), "genervt": (-0.55, 0.5),
            "ärgerlich": (-0.6, 0.6), "wütend": (-0.7, 0.8),

            # Sehr negativ
            "furchtbar": (-0.9, 0.7), "schrecklich": (-0.95, 0.7),
            "katastrophe": (-1.0, 0.8), "hasse": (-0.95, 0.8),
            "scheiße": (-0.85, 0.7), "mist": (-0.7, 0.5),
            "kacke": (-0.75, 0.5), "beschissen": (-0.9, 0.6),
        }

        self.ngram_sentiment = {
            "freue mich": (0.8, 0.6),
            "macht spaß": (0.7, 0.6),
            "gefällt mir": (0.65, 0.4),
            "bin happy": (0.75, 0.5),
            "bin froh": (0.7, 0.4),
            "läuft gut": (0.6, 0.3),
            "alles gut": (0.5, 0.2),
            "kein problem": (0.4, 0.2),
            "super geil": (0.95, 0.9),
            "richtig toll": (0.85, 0.6),
            "nervt mich": (-0.6, 0.6),
            "habe angst": (-0.7, 0.7),
            "bin traurig": (-0.75, 0.5),
            "geht mir schlecht": (-0.7, 0.5),
            "kotzt mich an": (-0.85, 0.8),
            "zum kotzen": (-0.8, 0.7),
            "keine lust": (-0.4, 0.3),
            "kein bock": (-0.45, 0.4),
            "echt nervig": (-0.65, 0.6),
            "so schlecht": (-0.7, 0.5),
        }

        self.emoji_sentiment = {
            "😊": (0.7, 0.5), "😃": (0.8, 0.6), "😄": (0.85, 0.7),
            "😍": (0.9, 0.7), "🥰": (0.9, 0.6), "❤️": (0.85, 0.6),
            "💕": (0.8, 0.5), "👍": (0.6, 0.4), "🎉": (0.8, 0.8),
            "✨": (0.6, 0.4), "🙂": (0.4, 0.3), "😐": (0.0, 0.1),
            "😕": (-0.3, 0.3), "😢": (-0.7, 0.5), "😭": (-0.85, 0.7),
            "😡": (-0.8, 0.9), "😤": (-0.6, 0.7), "👎": (-0.5, 0.4),
            "💔": (-0.75, 0.5), "😞": (-0.6, 0.4), "😔": (-0.5, 0.3),
            "🙄": (-0.3, 0.4), "😒": (-0.4, 0.4),
        }

        self.intensifiers = {
            "sehr": 1.5, "total": 1.6, "echt": 1.4, "wirklich": 1.4,
            "absolut": 1.7, "mega": 1.6, "extrem": 1.8, "richtig": 1.4,
            "so": 1.3, "voll": 1.5, "komplett": 1.5, "unglaublich": 1.7,
            "wahnsinnig": 1.6, "irre": 1.5, "ultra": 1.6, "super": 1.4,
            "ziemlich": 1.2, "recht": 1.1, "ganz": 1.2,
        }

        self.diminishers = {
            "etwas": 0.6, "ein bisschen": 0.5, "bisschen": 0.5,
            "leicht": 0.6, "eher": 0.7, "kaum": 0.3,
            "nicht so": 0.4, "weniger": 0.5, "fast": 0.7,
        }

        self.negations = {
            "nicht": 3, "kein": 2, "keine": 2, "keinen": 2,
            "nie": 4, "niemals": 4, "nichts": 2, "ohne": 2, "kaum": 2,
        }

    def _init_patterns(self):
        """Initialisiere Erkennungs-Patterns"""
        self.sarcasm_patterns = [
            r"ja\s+klar", r"oh\s+wie\s+toll", r"super\s*\.\.\.",
            r"toll\s*\.\.\.", r"na\s+toll", r"wie\s+schön\s*\.\.\.",
            r"wer\s+hätte\s+das\s+gedacht", r"überraschung",
            r"🙄", r"\.{3,}",
        ]

        self.mixed_patterns = [
            r"aber\s+auch", r"einerseits.*andererseits",
            r"zwar.*aber", r"obwohl", r"trotzdem",
        ]

    def analyze(self, text: str) -> SentimentResult:
        """Analysiere Sentiment mit allen Features."""
        text_lower = text.lower()
        words = text_lower.split()

        positive_indicators = []
        negative_indicators = []
        modifiers = []
        total_score = 0.0
        total_weight = 0.0

        # 1. Emoji-Analyse
        for emoji, (valence, arousal) in self.emoji_sentiment.items():
            count = text.count(emoji)
            if count > 0:
                total_score += valence * count * (1 + arousal * 0.3)
                total_weight += count
                if valence > 0:
                    positive_indicators.append((emoji, valence))
                else:
                    negative_indicators.append((emoji, valence))

        # 2. N-Gram Analyse
        for phrase, (valence, arousal) in self.ngram_sentiment.items():
            if phrase in text_lower:
                weight = 1.5
                total_score += valence * weight
                total_weight += weight
                if valence > 0:
                    positive_indicators.append((phrase, valence))
                else:
                    negative_indicators.append((phrase, valence))

        # 3. Wort-für-Wort Analyse
        negation_scope = 0
        current_modifier = 1.0

        for i, word in enumerate(words):
            if word in self.intensifiers:
                current_modifier = self.intensifiers[word]
                modifiers.append(f"intensifier:{word}")
                continue

            for dim, factor in self.diminishers.items():
                if dim in text_lower:
                    current_modifier *= factor
                    modifiers.append(f"diminisher:{dim}")

            if word in self.negations:
                negation_scope = self.negations[word]
                modifiers.append(f"negation:{word}")
                continue

            if word in self.sentiment_lexicon:
                valence, arousal = self.sentiment_lexicon[word]
                valence *= current_modifier

                if negation_scope > 0:
                    valence *= -0.8
                    negation_scope -= 1

                weight = 1.0 + arousal * 0.2
                total_score += valence * weight
                total_weight += weight

                if valence > 0:
                    positive_indicators.append((word, valence))
                else:
                    negative_indicators.append((word, valence))

                current_modifier = 1.0
            else:
                if negation_scope > 0:
                    negation_scope -= 1
                current_modifier = 1.0

        # 4. Sarkasmus-Check
        is_sarcastic = any(re.search(p, text_lower) for p in self.sarcasm_patterns)
        if is_sarcastic and total_score > 0:
            total_score *= -0.7
            modifiers.append("sarcasm_detected")

        # 5. Mixed Feelings
        is_mixed = any(re.search(p, text_lower) for p in self.mixed_patterns)
        if is_mixed:
            modifiers.append("mixed_feelings")

        # 6. Finales Sentiment
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0

        final_score = max(-1.0, min(1.0, final_score))

        if final_score >= 0.6:
            sentiment = "very_positive"
        elif final_score >= 0.2:
            sentiment = "positive"
        elif final_score <= -0.6:
            sentiment = "very_negative"
        elif final_score <= -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        confidence = min(1.0, abs(final_score) + (total_weight * 0.1))
        if is_mixed:
            confidence *= 0.7

        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            score=final_score,
            positive_indicators=positive_indicators,
            negative_indicators=negative_indicators,
            modifiers=modifiers,
            is_sarcastic=is_sarcastic,
            is_mixed=is_mixed
        )


# =============================================================================
# ENTITY EXTRACTION - Slot Filling
# =============================================================================

@dataclass
class Entity:
    """Extrahierte Entity"""
    type: str
    value: str
    original: str
    start: int
    end: int
    confidence: float


class EntityExtractor:
    """
    Entity Extraction mit Pattern Matching, Gazetteers und NER.

    v5.0: Erweitert um:
    - Echte Menschennamen (deutsche Vornamen + Nachnamen-Patterns)
    - Gaming/Anime-Charaktere mit Gender
    - Verbesserte Entity-Typen
    """

    def __init__(self):
        self._init_patterns()
        self._init_gazetteers()
        self._init_names()
        self._init_known_entities()

    def _init_patterns(self):
        """Regex-Patterns für Entity-Typen"""
        self.patterns = {
            "time_absolute": [
                (r"(\d{1,2})[:\.](\d{2})\s*(?:uhr)?", "HH:MM"),
                (r"um\s+(\d{1,2})\s*(?:uhr)?", "HH"),
            ],
            "time_relative": [
                (r"in\s+(\d+)\s*(?:min(?:uten?)?|m)", "minutes"),
                (r"in\s+(\d+)\s*(?:stunden?|h)", "hours"),
                (r"in\s+(\d+)\s*(?:sekunden?|sek|s)", "seconds"),
            ],
            "time_named": [
                (r"\b(morgen)\b", "tomorrow"),
                (r"\b(heute)\b", "today"),
                (r"\b(gestern)\b", "yesterday"),
                (r"\b(mittag)\b", "noon"),
                (r"\b(abend)\b", "evening"),
            ],
            "number": [
                (r"\b(\d+(?:[.,]\d+)?)\s*(?:€|euro)", "currency_eur"),
                (r"\b(\d+(?:[.,]\d+)?)\s*(?:%|prozent)", "percentage"),
                (r"\b(\d+(?:[.,]\d+)?)\s*(?:°c?|grad)", "temperature"),
                (r"\b(\d+)\b", "integer"),
            ],
            "duration": [
                (r"(\d+)\s*(?:min(?:uten?)?)", "minutes"),
                (r"(\d+)\s*(?:stunden?|h)", "hours"),
                (r"(\d+)\s*(?:tage?)", "days"),
            ],
            "date": [
                (r"\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b", "date"),
                (r"\b(\d{1,2})\.\s*(januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember)", "date_named"),
            ],
        }

    def _init_gazetteers(self):
        """Wortlisten für bekannte Entities"""
        self.gazetteers = {
            "device": {
                "nas": ["nas", "server", "netzwerkspeicher"],
                "light": ["licht", "lampe", "lampen", "beleuchtung", "led"],
                "tv": ["fernseher", "tv", "television"],
                "speaker": ["lautsprecher", "speaker", "box", "boxen"],
                "thermostat": ["heizung", "thermostat"],
                "computer": ["pc", "computer", "rechner"],
                "phone": ["handy", "telefon", "smartphone"],
            },
            "room": {
                "living_room": ["wohnzimmer", "wohnraum"],
                "bedroom": ["schlafzimmer"],
                "kitchen": ["küche"],
                "bathroom": ["bad", "badezimmer"],
                "office": ["büro", "arbeitszimmer"],
                "hallway": ["flur", "gang"],
            },
            "color": {
                "red": ["rot"], "blue": ["blau"], "green": ["grün"],
                "yellow": ["gelb"], "white": ["weiß", "weiss"],
                "warm": ["warm", "warmweiß"], "cold": ["kalt", "kaltweiß"],
            },
            "action": {
                "on": ["an", "ein", "einschalten", "aktivieren", "starten"],
                "off": ["aus", "ausschalten", "deaktivieren", "stoppen"],
                "toggle": ["umschalten", "wechseln"],
                "dim": ["dimmen", "dunkler", "heller"],
            },
        }

        self.entity_lookup = {}
        for entity_type, entities in self.gazetteers.items():
            for canonical, variants in entities.items():
                for variant in variants:
                    self.entity_lookup[variant.lower()] = (entity_type, canonical)

    def _init_names(self):
        """Internationale Vornamen für Namens-Erkennung (2000+)"""

        if _HAS_ENTITY_DB:
            # Nutze externe Datenbank mit 2000+ Namen
            self.male_names = get_all_male_names()
            self.female_names = get_all_female_names()
            self.first_names = get_all_names_with_gender()
            logger.debug(f"   Namen aus DB: {len(self.first_names)} Vornamen geladen")
        else:
            # Fallback: Eingebaute kompakte Liste
            self.male_names = {
                "alexander", "andreas", "anton", "benjamin", "christian", "daniel",
                "david", "dominik", "felix", "florian", "jan", "jonas", "julian",
                "kevin", "leon", "lukas", "max", "michael", "niklas", "paul", "peter",
                "sebastian", "stefan", "thomas", "tobias", "tim",
                # Türkisch
                "ahmet", "ali", "mehmet", "mustafa", "emre", "can", "burak", "murat",
                # Arabisch
                "mohamed", "ahmed", "ali", "omar", "yusuf", "hassan",
                # Englisch
                "james", "john", "william", "robert", "michael", "david", "chris",
            }
            self.female_names = {
                "anna", "marie", "sophie", "lena", "laura", "julia", "lisa", "sarah",
                "emma", "mia", "lea", "hannah", "nina", "jana", "katharina",
                # Türkisch
                "ayse", "fatma", "elif", "zeynep", "merve", "esra",
                # Arabisch
                "fatima", "aisha", "layla", "noor", "sara",
                # Englisch
                "mary", "jennifer", "jessica", "ashley", "emily", "emma",
            }
            self.first_names = {}
            for name in self.male_names:
                self.first_names[name] = "male"
            for name in self.female_names:
                self.first_names[name] = "female"

        # Typische Nachname-Endungen (alle Kulturen)
        self.surname_patterns = [
            # Deutsch
            r"[A-ZÄÖÜ][a-zäöüß]+(?:mann|berg|stein|bach|burg|dorf|feld|hof)",
            r"[A-ZÄÖÜ][a-zäöüß]+(?:meyer|meier|müller|schmidt|schneider|fischer)",
            # Türkisch
            r"[A-ZÄÖÜ][a-zäöüß]+(?:oglu|oğlu|son)",
            # Slawisch
            r"[A-ZÄÖÜ][a-zäöüß]+(?:ov|ova|ski|ska|wicz|enko)",
            # Englisch
            r"[A-ZÄÖÜ][a-zäöüß]+(?:son|sen|ley|ford|wood|field)",
        ]

    def _init_known_entities(self):
        """Bekannte Entities (Gaming, Anime, Tech, etc.) - 700+ Entities"""

        if _HAS_ENTITY_DB:
            # Nutze externe Datenbank
            self.known_entities = get_all_known_entities()
            logger.debug(f"   Entities aus DB: {len(self.known_entities)} Entities geladen")
        else:
            # Fallback: Kompakte eingebaute Liste
            self.known_entities = {
                "raiden shogun": {"type": "character", "game": "Genshin Impact", "gender": "female"},
                "yae miko": {"type": "character", "game": "Genshin Impact", "gender": "female"},
                "zhongli": {"type": "character", "game": "Genshin Impact", "gender": "male"},
                "nahida": {"type": "character", "game": "Genshin Impact", "gender": "female"},
                "kafka": {"type": "character", "game": "Honkai Star Rail", "gender": "female"},
                "firefly": {"type": "character", "game": "Honkai Star Rail", "gender": "female"},
                "goku": {"type": "character", "anime": "Dragon Ball", "gender": "male"},
                "naruto": {"type": "character", "anime": "Naruto", "gender": "male"},
                "genshin impact": {"type": "game"},
                "minecraft": {"type": "game"},
                "raspberry pi": {"type": "technology"},
                "python": {"type": "technology", "category": "programming_language"},
            }

        # Sortiert nach Länge für Greedy Matching
        self._entity_keys = sorted(self.known_entities.keys(), key=len, reverse=True)


    def extract(self, text: str) -> List[Entity]:
        """Extrahiere alle Entities aus Text"""
        text_lower = text.lower()
        entities = []
        used_ranges = []  # Verhindere Überlappungen

        # 1. Bekannte Entities (Gaming, Anime, Tech, etc.)
        for entity_name in self._entity_keys:
            pattern = rf"\b{re.escape(entity_name)}\b"
            for match in re.finditer(pattern, text_lower):
                start, end = match.start(), match.end()
                if not self._overlaps_range(start, end, used_ranges):
                    entity_info = self.known_entities[entity_name]
                    entities.append(Entity(
                        type=entity_info.get("type", "unknown"),
                        value=entity_name,
                        original=text[start:end],
                        start=start,
                        end=end,
                        confidence=0.95
                    ))
                    used_ranges.append((start, end))

        # 2. Pattern-basiert (Zeit, Datum, Zahlen)
        for entity_type, patterns in self.patterns.items():
            for pattern, subtype in patterns:
                for match in re.finditer(pattern, text_lower):
                    start, end = match.start(), match.end()
                    if not self._overlaps_range(start, end, used_ranges):
                        value = match.group(1) if match.groups() else match.group(0)
                        entities.append(Entity(
                            type=entity_type,
                            value=value,
                            original=match.group(0),
                            start=start,
                            end=end,
                            confidence=0.95
                        ))
                        used_ranges.append((start, end))

        # 3. Gazetteer-basiert (Geräte, Räume, etc.)
        words = text_lower.split()
        pos = 0
        for word in words:
            word_clean = re.sub(r'[^\wäöüß]', '', word)
            if word_clean in self.entity_lookup:
                entity_type, canonical = self.entity_lookup[word_clean]
                start = text_lower.find(word, pos)
                if start >= 0 and not self._overlaps_range(start, start + len(word), used_ranges):
                    entities.append(Entity(
                        type=entity_type,
                        value=canonical,
                        original=word,
                        start=start,
                        end=start + len(word),
                        confidence=0.9
                    ))
                    used_ranges.append((start, start + len(word)))
                    pos = start + len(word)

        # 4. Menschennamen erkennen
        name_entities = self._extract_names(text)
        for ne in name_entities:
            if not self._overlaps_range(ne.start, ne.end, used_ranges):
                entities.append(ne)
                used_ranges.append((ne.start, ne.end))

        return sorted(entities, key=lambda e: e.start)

    def _extract_names(self, text: str) -> List[Entity]:
        """Extrahiere Menschennamen aus Text"""
        entities = []

        # Split in Wörter mit Positionen
        words_with_pos = []
        pos = 0
        for word in text.split():
            start = text.find(word, pos)
            words_with_pos.append((word, start, start + len(word)))
            pos = start + len(word)

        i = 0
        while i < len(words_with_pos):
            word, start, end = words_with_pos[i]
            word_clean = word.strip('.,!?;:()[]{}"\'-')
            word_lower = word_clean.lower()

            # Bekannter Vorname?
            if word_lower in self.first_names:
                gender = self.first_names[word_lower]

                # Prüfe ob Nachname folgt
                full_name = word_clean
                final_end = end

                if i + 1 < len(words_with_pos):
                    next_word, next_start, next_end = words_with_pos[i + 1]
                    next_clean = next_word.strip('.,!?;:()[]{}"\'-')

                    # Nachname: Beginnt mit Großbuchstabe und ist nicht am Satzanfang
                    if next_clean and next_clean[0].isupper():
                        # Prüfe Nachname-Pattern
                        if self._is_surname(next_clean):
                            full_name = f"{word_clean} {next_clean}"
                            final_end = next_end
                            i += 1

                entities.append(Entity(
                    type="person",
                    value=full_name,
                    original=text[start:final_end],
                    start=start,
                    end=final_end,
                    confidence=0.85 if " " in full_name else 0.7
                ))

            # Großbuchstabe mitten im Satz ohne bekannten Vornamen?
            elif i > 0 and word_clean and word_clean[0].isupper() and len(word_clean) > 1:
                # Könnte ein Name sein
                if self._looks_like_name(word_clean):
                    # Prüfe ob mehrere Großbuchstaben-Wörter hintereinander
                    full_name = word_clean
                    final_end = end

                    if i + 1 < len(words_with_pos):
                        next_word, next_start, next_end = words_with_pos[i + 1]
                        next_clean = next_word.strip('.,!?;:()[]{}"\'-')

                        if next_clean and next_clean[0].isupper() and self._looks_like_name(next_clean):
                            full_name = f"{word_clean} {next_clean}"
                            final_end = next_end
                            i += 1

                    entities.append(Entity(
                        type="person",
                        value=full_name,
                        original=text[start:final_end],
                        start=start,
                        end=final_end,
                        confidence=0.6
                    ))

            i += 1

        return entities

    def _is_surname(self, word: str) -> bool:
        """Prüfe ob Wort ein Nachname sein könnte"""
        # Typische deutsche Nachnamen-Endungen
        surname_endings = (
            "mann", "berg", "stein", "bach", "burg", "dorf", "feld", "hof",
            "meyer", "meier", "maier", "mayer", "müller", "schmidt", "schneider",
            "fischer", "weber", "wagner", "becker", "schulz", "hoffmann",
            "schäfer", "koch", "richter", "klein", "wolf", "schröder", "neumann",
            "schwarz", "braun", "zimmermann", "krüger", "hartmann", "lange",
            "werner", "kraus", "lehmann", "köhler", "maier", "herrmann",
        )

        word_lower = word.lower()

        # Bekannte Nachnamen
        if word_lower in surname_endings:
            return True

        # Endungen prüfen
        for ending in surname_endings:
            if word_lower.endswith(ending):
                return True

        # Mindestens 2 Buchstaben, beginnt mit Großbuchstabe
        if len(word) >= 2 and word[0].isupper():
            return True

        return False

    def _looks_like_name(self, word: str) -> bool:
        """Prüfe ob Wort wie ein Name aussieht"""
        # Keine Ziffern
        if any(c.isdigit() for c in word):
            return False

        # Nicht nur Großbuchstaben (Akronyme)
        if word.isupper():
            return False

        # Mindestens 2 Buchstaben
        if len(word) < 2:
            return False

        # Beginnt mit Großbuchstabe
        if not word[0].isupper():
            return False

        # Rest hauptsächlich Kleinbuchstaben
        lower_count = sum(1 for c in word[1:] if c.islower())
        if lower_count < len(word) - 2:
            return False

        return True

    def _overlaps_range(self, start: int, end: int, used_ranges: List[Tuple[int, int]]) -> bool:
        """Prüfe ob Bereich mit bereits genutzten Bereichen überlappt"""
        for used_start, used_end in used_ranges:
            if not (end <= used_start or start >= used_end):
                return True
        return False

    def _remove_overlaps(self, entities: List[Entity]) -> List[Entity]:
        """Entferne überlappende Entities"""
        if not entities:
            return []

        sorted_entities = sorted(entities, key=lambda e: (e.start, -(e.end - e.start)))
        result = [sorted_entities[0]]

        for entity in sorted_entities[1:]:
            last = result[-1]
            if entity.start >= last.end:
                result.append(entity)
            elif entity.end - entity.start > last.end - last.start:
                result[-1] = entity

        return result

    def extract_slots(self, text: str, required_slots: List[str]) -> Dict[str, Optional[Entity]]:
        """Extrahiere spezifische Slots."""
        entities = self.extract(text)
        slots = {slot: None for slot in required_slots}

        for entity in entities:
            if entity.type in slots and slots[entity.type] is None:
                slots[entity.type] = entity

        return slots

    def get_entity_info(self, name: str) -> Optional[Dict]:
        """Hole Informationen zu einer bekannten Entity"""
        return self.known_entities.get(name.lower())

    def get_gender(self, name: str) -> Optional[str]:
        """Hole Gender für Namen oder Charakter"""
        name_lower = name.lower()

        # Bekannte Entities
        if name_lower in self.known_entities:
            return self.known_entities[name_lower].get("gender")

        # Vornamen
        if name_lower in self.first_names:
            return self.first_names[name_lower]

        return None


# =============================================================================
# INTENT DATABASE - Große Sammlung von Intent-Patterns
# =============================================================================

class IntentDatabase:
    """
    Große Datenbank mit Intent-Patterns für deutsches Sprachverständnis.

    Enthält 60+ Intents mit Patterns und Keywords.
    """

    def __init__(self):
        self.intents = {}
        self._compiled = {}
        self._keyword_index = defaultdict(list)
        self._load_intents()
        self._compile_patterns()

    def _load_intents(self):
        """Lade alle Intent-Definitionen"""

        # Format: intent_name -> (category, patterns, keywords, priority)
        intent_data = {
            # GREETINGS
            "greeting_morning": ("greeting", [
                r"^guten\s+morgen", r"^morgen\s*[!.]?$", r"^moin",
            ], ["morgen", "moin"], 8),

            "greeting_day": ("greeting", [
                r"^guten\s+tag", r"^tag\s*[!.]?$", r"^tach",
            ], ["tag", "tach"], 8),

            "greeting_evening": ("greeting", [
                r"^guten\s+abend", r"^n'?abend", r"^abend\s*[!.]?$",
            ], ["abend", "nabend"], 8),

            "greeting_night": ("greeting", [
                r"^gute\s+nacht", r"^schlaf\s+gut",
            ], ["nacht", "schlaf gut"], 8),

            "greeting_casual": ("greeting", [
                r"^h[ae]llo", r"^hi\s*[!.]?$", r"^hey\s*[!.]?",
                r"^huhu", r"^servus", r"^yo\s*[!.]?$", r"^na\s*[!.,?]?$",
            ], ["hallo", "hello", "hi", "hey", "huhu", "servus", "yo", "na"], 9),

            "greeting_return": ("greeting", [
                r"bin\s+(?:wieder\s+)?(?:da|zurück)", r"^back\s*[!.]?",
            ], ["wieder da", "zurück", "back"], 7),

            # FAREWELLS
            "farewell": ("farewell", [
                r"^(?:auf\s+)?wiedersehen", r"^tschüss?", r"^bye",
                r"^ciao", r"^bis\s+(?:dann|später|bald|morgen)",
                r"^mach'?s?\s+gut", r"^hau\s+rein",
            ], ["wiedersehen", "tschüss", "bye", "ciao", "bis später"], 9),

            # GRATITUDE
            "thanks": ("gratitude", [
                r"^dank[e]?\s*[!.]?$", r"^danke\s+(?:dir|schön|sehr)",
                r"^vielen\s+dank", r"^thanks?", r"^thx", r"^merci",
            ], ["danke", "dank", "thanks", "merci"], 9),

            "apology": ("gratitude", [
                r"tut\s+mir\s+leid", r"^entschuldig", r"^sorry", r"^verzeih",
            ], ["leid", "entschuldigung", "sorry"], 7),

            # QUESTIONS
            "question_who": ("question", [
                r"^wer\s+(?:ist|sind|war|hat)", r"\bwer\s+(?:eigentlich|denn)",
            ], ["wer ist", "wer hat"], 8),

            "question_what": ("question", [
                r"^was\s+(?:ist|sind|bedeutet|heißt|macht)",
                r"^was\s+für\s+(?:ein|eine)",
            ], ["was ist", "was bedeutet"], 8),

            "question_where": ("question", [
                r"^wo\s+(?:ist|sind|liegt|befindet|kann)",
                r"^wo(?:hin|her)\s+",
            ], ["wo ist", "wohin", "woher"], 8),

            "question_when": ("question", [
                r"^wann\s+(?:ist|war|wird|fängt|beginnt)",
                r"^(?:um\s+)?wie\s*viel\s+uhr",
            ], ["wann", "wie viel uhr"], 8),

            "question_how": ("question", [
                r"^wie\s+(?:geht|gehts|funktioniert|macht\s+man)",
                r"^wie\s+(?:viel|viele|oft|lange)",
            ], ["wie geht", "wie funktioniert", "wie viel"], 8),

            "question_why": ("question", [
                r"^warum\s+", r"^wieso\s+", r"^weshalb\s+",
            ], ["warum", "wieso", "weshalb"], 8),

            # HOLO-SPECIFIC
            "question_holo_identity": ("personal", [
                r"wer\s+bist\s+du", r"was\s+bist\s+du",
                r"bist\s+du\s+(?:ein[e]?\s+)?(?:ki|ai|bot)",
                r"wie\s+heißt\s+du",
            ], ["wer bist", "was bist", "heißt du"], 9),

            "question_holo_feelings": ("personal", [
                r"wie\s+geht\s*(?:'s|s|es)\s*(?:dir)?",
                r"wie\s+fühlst\s+du\s+dich",
                r"bist\s+du\s+(?:müde|traurig|glücklich)",
            ], ["wie gehts", "fühlst du", "bist du müde"], 9),

            "question_holo_activity": ("personal", [
                r"was\s+(?:machst|tust|treibst)\s+du",
                r"was\s+(?:geht|läuft)\s+(?:bei\s+dir|so)",
                r"womit\s+beschäftigst\s+du",
                r"und\s+(?:bei\s+)?dir\s*\?",
            ], ["was machst", "was tust", "bei dir"], 9),

            "question_holo_capabilities": ("personal", [
                r"was\s+kannst\s+du", r"was\s+sind\s+deine\s+fähigkeiten",
                r"(?:kannst|könntest)\s+du\s+(?:mir\s+)?helfen",
            ], ["was kannst", "fähigkeiten", "helfen"], 8),

            # COMMANDS
            "command_search": ("command", [
                r"^(?:bitte\s+)?(?:such|suche|suchen)\s+(?:mal\s+)?(?:nach\s+)?",
                r"^(?:google|recherchier)", r"^(?:find|finde)\s+(?:heraus)?",
            ], ["such", "suche", "google", "finde"], 9),

            "command_tell": ("command", [
                r"(?:erzähl|sag)\s+(?:mir\s+)?(?:(?:et)?was\s+)?(?:über|von)",
                r"(?:berichte?|beschreib|erklär)",
            ], ["erzähl", "sag mir", "erkläre"], 8),

            "command_show": ("command", [
                r"(?:zeig|zeige)\s+(?:mir\s+)?", r"(?:lass)\s+(?:mich\s+)?sehen",
            ], ["zeig", "lass sehen"], 8),

            "command_help": ("command", [
                r"(?:hilf|helfe|hilfe)\s+(?:mir\s+)?",
                r"ich\s+(?:brauche?|bräuchte)\s+hilfe",
            ], ["hilf", "hilfe", "brauche hilfe"], 8),

            "command_remember": ("command", [
                r"(?:merk|merke)\s+(?:dir\s+)?", r"(?:erinner|erinnere)\s+mich",
                r"(?:vergiss)\s+(?:nicht\s+)?", r"(?:speicher|speichere)",
            ], ["merk", "erinner", "vergiss nicht"], 7),

            # SYSTEM
            "system_nas_wake": ("system", [
                r"(?:weck|wecke)\s+(?:das\s+)?nas", r"nas\s+(?:aufwecken|starten|an)",
                r"(?:start|starte)\s+(?:das\s+)?nas",
            ], ["weck nas", "nas starten", "nas an"], 9),

            "system_nas_sleep": ("system", [
                r"(?:leg|lege)\s+(?:das\s+)?nas\s+schlafen",
                r"nas\s+(?:suspend|schlafen|aus|herunterfahren)",
            ], ["nas schlafen", "nas aus"], 9),

            "system_nas_status": ("system", [
                r"(?:ist|läuft)\s+(?:das\s+)?nas", r"nas\s+status",
                r"(?:wie|was)\s+(?:ist|macht)\s+(?:das\s+)?nas",
            ], ["nas status", "nas an", "läuft nas"], 8),

            "system_status": ("system", [
                r"(?:system|pi)\s*(?:status|info)",
                r"(?:alle[sn]?\s+)?(?:ok|okay|gut)\s*\?",
            ], ["system status", "alles ok"], 7),

            # MEDIA
            "media_news": ("media", [
                r"(?:gibt.s|gibt\s+es)\s+(?:neues|für\s+)?news",
                r"(?:zeig|erzähl)\s+(?:mir\s+)?(?:die\s+)?news",
                r"was\s+(?:ist|war)\s+(?:in\s+den\s+)?nachrichten",
            ], ["news", "nachrichten", "neuigkeiten"], 8),

            "media_weather": ("media", [
                r"(?:wie\s+)?(?:ist|wird)\s+(?:das\s+)?wetter",
                r"(?:regnet|schneit)\s+es",
            ], ["wetter", "regnet", "schneit"], 8),

            "media_time": ("media", [
                r"(?:wie\s+)?(?:viel|spät)\s+(?:ist\s+es|uhr)",
                r"(?:welche[rs]?\s+)?(?:uhrzeit|zeit|datum)",
            ], ["uhr", "uhrzeit", "datum"], 8),

            # SMALLTALK
            "smalltalk_joke": ("smalltalk", [
                r"(?:erzähl|sag)\s+(?:mir\s+)?(?:einen?\s+)?witz",
                r"(?:hast|kennst)\s+du\s+(?:einen?\s+)?witz",
            ], ["witz", "witze", "lachen"], 6),

            "smalltalk_bored": ("smalltalk", [
                r"(?:mir\s+)?(?:ist|wird)\s+langweilig",
                r"(?:weiß|weiss)\s+nicht\s+was\s+(?:ich\s+)?(?:machen|tun)",
            ], ["langweilig", "weiß nicht"], 5),

            "smalltalk_compliment": ("smalltalk", [
                r"du\s+bist\s+(?:toll|super|nett|lieb|süß|cool)",
                r"(?:ich\s+)?mag\s+dich",
            ], ["du bist toll", "mag dich"], 6),

            # USER SHARING
            "user_shared_activity": ("statement", [
                r"ich\s+(?:spiele|zocke)\s+(?:gerade\s+)?",
                r"ich\s+(?:schaue?|gucke?)\s+(?:gerade\s+)?",
                r"ich\s+(?:höre?|lese?)\s+(?:gerade\s+)?",
                r"ich\s+(?:habe?|hab)\s+(?:gerade\s+)?.+\s+(?:gespielt|gezockt)",
            ], ["ich spiele", "ich schaue", "ich höre"], 7),

            "user_shared_feeling": ("statement", [
                r"ich\s+(?:bin|fühle\s+mich)\s+",
                r"(?:mir\s+)?geht(?:'s|s)?\s+",
            ], ["ich bin", "mir gehts", "ich fühle"], 6),

            # CORRECTIONS
            "correction": ("meta", [
                r"^nein[,.]?\s+(?:ich\s+)?(?:meinte?|wollte)",
                r"^nicht\s+.+\s+sondern\s+",
                r"(?:ich\s+)?meinte?\s+(?:eigentlich|eher)",
                r"(?:das\s+)?stimmt\s+(?:so\s+)?nicht",
            ], ["nein ich meinte", "nicht sondern", "eigentlich"], 10),

            "confirmation": ("meta", [
                r"^(?:ja|jo|jap|jep|yes)\s*[,!.]?\s*(?:genau|richtig)?",
                r"^(?:genau|richtig|stimmt|korrekt)\s*[,!.]?",
            ], ["ja", "genau", "richtig", "stimmt"], 10),

            "negation": ("meta", [
                r"^(?:nein|nee|nö|ne)\s*[,!.]?\s*$",
                r"^(?:falsch|inkorrekt)\s*[,!.]?$",
            ], ["nein", "nee", "falsch"], 10),

            # META
            "meta_repeat": ("meta", [
                r"(?:noch\s*mal|wiederholen)", r"(?:wie\s+)?bitte\s*\?$",
                r"(?:hab|habe)\s+(?:das\s+)?nicht\s+verstanden",
            ], ["noch mal", "wiederholen", "nicht verstanden"], 7),

            "meta_continue": ("meta", [
                r"(?:und\s+)?(?:dann|weiter|mehr)", r"(?:erzähl|sag)\s+(?:mir\s+)?mehr",
            ], ["weiter", "mehr", "dann"], 6),

            "meta_stop": ("meta", [
                r"^(?:ok|okay|gut|genug|stopp?|halt)\s*[,!.]?$",
                r"(?:das\s+)?reicht\s*[,!.]?$",
            ], ["ok", "genug", "stop", "reicht"], 7),
        }

        for intent_name, (category, patterns, keywords, priority) in intent_data.items():
            self.intents[intent_name] = {
                "category": category,
                "patterns": patterns,
                "keywords": keywords,
                "priority": priority,
            }

    def _compile_patterns(self):
        """Kompiliere Patterns und baue Keyword-Index"""
        for intent_name, data in self.intents.items():
            self._compiled[intent_name] = [
                re.compile(p, re.IGNORECASE) for p in data["patterns"]
            ]
            for keyword in data["keywords"]:
                self._keyword_index[keyword.lower()].append(intent_name)

    def match(self, text: str) -> List[Tuple[str, float, str]]:
        """
        Finde passende Intents.

        Returns:
            Liste von (intent_name, confidence, category)
        """
        text_lower = text.lower().strip()
        matches = []
        seen = set()

        # 1. Pattern Matching
        for intent_name, patterns in self._compiled.items():
            if intent_name in seen:
                continue
            for pattern in patterns:
                if pattern.search(text_lower):
                    priority = self.intents[intent_name]["priority"]
                    category = self.intents[intent_name]["category"]
                    confidence = 0.9 if pattern.match(text_lower) else 0.7
                    confidence *= (priority / 10)
                    matches.append((intent_name, confidence, category))
                    seen.add(intent_name)
                    break

        # 2. Keyword Matching (falls keine Pattern-Matches)
        if not matches:
            for keyword, intent_names in self._keyword_index.items():
                if keyword in text_lower:
                    for intent_name in intent_names:
                        if intent_name not in seen:
                            priority = self.intents[intent_name]["priority"]
                            category = self.intents[intent_name]["category"]
                            confidence = 0.5 * (priority / 10)
                            matches.append((intent_name, confidence, category))
                            seen.add(intent_name)

        # Sortieren nach Konfidenz
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches

    def get_intent(self, text: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Hole besten Intent"""
        matches = self.match(text)
        if matches:
            return matches[0]
        return None, 0.0, None


# =============================================================================
# GERMAN SENTENCE PARSER - Deutsche Satzstruktur analysieren
# =============================================================================

class GermanSentenceParser:
    """
    Parser für deutsche Satzstruktur.

    Analysiert:
    - Satztyp (Aussage, Frage, Aufforderung)
    - Hauptverb
    - Subjekt
    - Negation
    - Frage-Wort
    """

    # Deutsche Hilfsverben
    HILFSVERBEN = {
        "bin", "bist", "ist", "sind", "seid", "war", "warst", "waren",
        "habe", "hast", "hat", "haben", "habt", "hatte", "hatten",
        "werde", "wirst", "wird", "werden", "werdet", "wurde", "wurden",
    }

    # Modalverben
    MODALVERBEN = {
        "kann", "kannst", "können", "könnt", "konnte", "konnten",
        "muss", "musst", "müssen", "müsst", "musste", "mussten",
        "will", "willst", "wollen", "wollt", "wollte", "wollten",
        "soll", "sollst", "sollen", "sollt", "sollte", "sollten",
        "darf", "darfst", "dürfen", "dürft", "durfte", "durften",
        "mag", "magst", "mögen", "mögt", "mochte", "mochten",
        "möchte", "möchtest", "möchten", "möchtet",
    }

    # Frage-Wörter
    FRAGEWÖRTER = {
        "wer", "was", "wo", "wann", "wie", "warum", "wieso", "weshalb",
        "woher", "wohin", "welche", "welcher", "welches", "welchen",
        "wessen", "wem", "wen", "womit", "wofür", "worüber",
    }

    # Negationswörter
    NEGATION = {"nicht", "kein", "keine", "keinen", "keinem", "keiner",
                "nie", "niemals", "nichts", "niemand"}

    # Pronomen
    PERSONAL_PRONOUNS = {
        "ich", "du", "er", "sie", "es", "wir", "ihr",
        "mich", "dich", "ihn", "uns", "euch",
        "mir", "dir", "ihm",
    }

    def __init__(self):
        self.all_verbs = self.HILFSVERBEN | self.MODALVERBEN

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Analysiere einen deutschen Satz.

        Returns:
            {
                "sentence_type": str,  # question, statement, imperative
                "main_verb": Optional[str],
                "subject": Optional[str],
                "negated": bool,
                "question_word": Optional[str],
                "tense": str,
                "mood": str,
            }
        """
        text = text.strip()
        text_lower = text.lower()
        words = text_lower.split()

        if not words:
            return self._empty_result()

        # Satztyp bestimmen
        sentence_type = self._determine_sentence_type(text, words)

        # Frage-Wort finden
        question_word = None
        for word in words[:3]:
            clean_word = re.sub(r'[^\wäöüß]', '', word)
            if clean_word in self.FRAGEWÖRTER:
                question_word = clean_word
                break

        # Verb finden
        main_verb = self._find_main_verb(words)

        # Subjekt finden
        subject = self._find_subject(words)

        # Negation prüfen
        negated = any(neg in words for neg in self.NEGATION)

        # Tempus bestimmen
        tense = self._determine_tense(words)

        # Modus
        mood = "imperative" if sentence_type == "imperative" else "indicative"
        if any(w in words for w in ["würde", "wäre", "hätte", "könnte", "müsste"]):
            mood = "subjunctive"

        return {
            "sentence_type": sentence_type,
            "main_verb": main_verb,
            "subject": subject,
            "negated": negated,
            "question_word": question_word,
            "tense": tense,
            "mood": mood,
        }

    def _empty_result(self) -> Dict:
        return {
            "sentence_type": "unknown",
            "main_verb": None,
            "subject": None,
            "negated": False,
            "question_word": None,
            "tense": "present",
            "mood": "indicative",
        }

    def _determine_sentence_type(self, text: str, words: List[str]) -> str:
        """Bestimme den Satztyp"""
        # Fragezeichen → Frage
        if text.endswith("?"):
            return "question"

        # Frage-Wort am Anfang → Frage
        if words:
            first_clean = re.sub(r'[^\wäöüß]', '', words[0])
            if first_clean in self.FRAGEWÖRTER:
                return "question"

        # Verb-Erst-Stellung prüfen
        if words:
            first_clean = re.sub(r'[^\wäöüß]', '', words[0])
            if first_clean in self.all_verbs:
                # Imperativ oder Frage
                if len(words) > 1 and words[1] in self.PERSONAL_PRONOUNS:
                    return "question"
                return "imperative"

        # Ausrufezeichen und kein Pronomen am Anfang
        if text.endswith("!"):
            if words and words[0] not in self.PERSONAL_PRONOUNS:
                return "imperative"

        return "statement"

    def _find_main_verb(self, words: List[str]) -> Optional[str]:
        """Finde das Hauptverb"""
        for word in words:
            clean_word = re.sub(r'[^\wäöüß]', '', word)
            if clean_word in self.all_verbs:
                return clean_word
            # Einfache Heuristik für andere Verben
            if clean_word.endswith(("en", "st", "t")) and len(clean_word) > 3:
                return clean_word
        return None

    def _find_subject(self, words: List[str]) -> Optional[str]:
        """Finde das Subjekt"""
        for word in words:
            clean_word = re.sub(r'[^\wäöüß]', '', word)
            if clean_word in self.PERSONAL_PRONOUNS:
                return clean_word
        return None

    def _determine_tense(self, words: List[str]) -> str:
        """Bestimme das Tempus"""
        # Perfekt-Marker
        if any(w in words for w in ["habe", "hast", "hat", "haben", "habt"]):
            for word in words:
                if word.startswith("ge") and word.endswith(("t", "en")):
                    return "perfect"

        # Präteritum
        past_markers = ["war", "hatte", "ging", "kam", "machte", "sagte"]
        if any(w in words for w in past_markers):
            return "past"

        # Futur
        if any(w in words for w in ["werde", "wirst", "wird", "werden", "werdet"]):
            return "future"

        return "present"


# =============================================================================
# WORD EMBEDDINGS - Co-occurrence basiert
# =============================================================================

class SimpleWordEmbeddings:
    """
    Einfache Word Embeddings ohne externe Bibliotheken.

    Nutzt:
    - Co-occurrence Matrix
    - PMI (Pointwise Mutual Information)
    """

    def __init__(self, dimension: int = 50, window_size: int = 3):
        self.dimension = dimension
        self.window_size = window_size
        self.word_to_id: Dict[str, int] = {}
        self.id_to_word: Dict[int, str] = {}
        self.cooccurrence: Dict[Tuple[int, int], float] = defaultdict(float)
        self.word_counts: Counter = Counter()
        self.total_count = 0
        self.embeddings: Dict[str, List[float]] = {}

        self._init_semantic_groups()

    def _init_semantic_groups(self):
        """Semantische Gruppen für Bootstrapping"""
        self.semantic_groups = {
            "emotion_positive": ["freude", "glück", "liebe", "spaß", "toll", "super"],
            "emotion_negative": ["trauer", "angst", "wut", "stress", "schlecht"],
            "time": ["heute", "morgen", "gestern", "jetzt", "später", "bald"],
            "devices": ["licht", "lampe", "nas", "server", "computer", "handy"],
            "rooms": ["küche", "wohnzimmer", "schlafzimmer", "bad", "büro"],
            "actions": ["machen", "tun", "gehen", "kommen", "sagen"],
            "holo": ["wolf", "wedeln", "ohren", "schweif", "pfote"],
        }

    def train(self, texts: List[str]):
        """Trainiere Embeddings auf Texten"""
        # Vokabular aufbauen
        for text in texts:
            words = text.lower().split()
            for word in words:
                if word not in self.word_to_id:
                    idx = len(self.word_to_id)
                    self.word_to_id[word] = idx
                    self.id_to_word[idx] = word
                self.word_counts[word] += 1
                self.total_count += 1

        # Co-occurrence zählen
        for text in texts:
            words = text.lower().split()
            for i, word in enumerate(words):
                word_id = self.word_to_id[word]
                start = max(0, i - self.window_size)
                end = min(len(words), i + self.window_size + 1)

                for j in range(start, end):
                    if i != j:
                        context_id = self.word_to_id[words[j]]
                        weight = 1.0 / abs(i - j)
                        self.cooccurrence[(word_id, context_id)] += weight

        self._compute_embeddings()

    def _compute_embeddings(self):
        """Berechne Embeddings aus Co-occurrence"""
        for word, word_id in self.word_to_id.items():
            embedding = [0.0] * self.dimension
            word_count = self.word_counts[word]

            for (w1, w2), cooc in self.cooccurrence.items():
                if w1 == word_id:
                    context_word = self.id_to_word[w2]
                    context_count = self.word_counts[context_word]

                    p_joint = cooc / self.total_count
                    p_w1 = word_count / self.total_count
                    p_w2 = context_count / self.total_count

                    if p_w1 > 0 and p_w2 > 0:
                        pmi = math.log(max(p_joint / (p_w1 * p_w2), 1e-10))
                        pmi = max(0, pmi)
                        feature_idx = hash(context_word) % self.dimension
                        embedding[feature_idx] += pmi

            # Semantic Groups
            for group_name, group_words in self.semantic_groups.items():
                if word in group_words:
                    group_idx = hash(group_name) % self.dimension
                    embedding[group_idx] += 1.0

            # Normalisieren
            magnitude = math.sqrt(sum(x*x for x in embedding))
            if magnitude > 0:
                embedding = [x / magnitude for x in embedding]

            self.embeddings[word] = embedding

    def get_embedding(self, word: str) -> Optional[List[float]]:
        """Hole Embedding für Wort"""
        return self.embeddings.get(word.lower())

    def similarity(self, word1: str, word2: str) -> float:
        """Cosine Similarity zwischen Wörtern"""
        emb1 = self.get_embedding(word1)
        emb2 = self.get_embedding(word2)

        if not emb1 or not emb2:
            return 0.0

        return sum(a * b for a, b in zip(emb1, emb2))

    def most_similar(self, word: str, n: int = 5) -> List[Tuple[str, float]]:
        """Finde ähnlichste Wörter"""
        if word.lower() not in self.embeddings:
            return []

        similarities = []
        for other_word in self.embeddings:
            if other_word != word.lower():
                sim = self.similarity(word, other_word)
                similarities.append((other_word, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]

    def sentence_embedding(self, text: str) -> List[float]:
        """Embedding für ganzen Satz (Durchschnitt)"""
        words = text.lower().split()
        embeddings = [self.get_embedding(w) for w in words if self.get_embedding(w)]

        if not embeddings:
            return [0.0] * self.dimension

        result = [0.0] * self.dimension
        for emb in embeddings:
            for i, val in enumerate(emb):
                result[i] += val

        return [x / len(embeddings) for x in result]

    def sentence_similarity(self, text1: str, text2: str) -> float:
        """Similarity zwischen Sätzen"""
        emb1 = self.sentence_embedding(text1)
        emb2 = self.sentence_embedding(text2)

        dot = sum(a * b for a, b in zip(emb1, emb2))
        mag1 = math.sqrt(sum(x*x for x in emb1))
        mag2 = math.sqrt(sum(x*x for x in emb2))

        if mag1 > 0 and mag2 > 0:
            return dot / (mag1 * mag2)
        return 0.0


# =============================================================================
# TEXT SUMMARIZATION
# =============================================================================

class TextSummarizer:
    """Extractive Text-Summarization."""

    def __init__(self):
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber",
            "ist", "sind", "war", "waren", "hat", "haben", "wird", "werden",
            "ich", "du", "er", "sie", "es", "wir", "ihr",
            "in", "an", "auf", "für", "mit", "von", "zu", "bei",
            "nicht", "auch", "noch", "schon", "dann", "wenn", "als",
        }

    def summarize_extractive(self, text: str, n_sentences: int = 2) -> str:
        """Extractive Summarization - wichtigste Sätze."""
        sentences = self._split_sentences(text)

        if len(sentences) <= n_sentences:
            return text

        word_scores = self._calculate_word_scores(text)

        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, word_scores)
            if i == 0:
                score *= 1.2
            elif i == len(sentences) - 1:
                score *= 1.1
            sentence_scores.append((sentence, score, i))

        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = sentence_scores[:n_sentences]
        top_sentences.sort(key=lambda x: x[2])

        return " ".join(s[0] for s in top_sentences)

    def _split_sentences(self, text: str) -> List[str]:
        """Splitte Text in Sätze"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_word_scores(self, text: str) -> Dict[str, float]:
        """Berechne Wort-Wichtigkeit"""
        words = text.lower().split()
        word_counts = Counter(words)
        total = len(words)

        scores = {}
        for word, count in word_counts.items():
            if word in self.stopwords or len(word) < 3:
                continue
            tf = count / total
            rarity_bonus = 1.0 / (count ** 0.5)
            scores[word] = tf * rarity_bonus

        return scores

    def _score_sentence(self, sentence: str, word_scores: Dict[str, float]) -> float:
        """Berechne Satz-Score"""
        words = sentence.lower().split()
        if not words:
            return 0.0

        score = sum(word_scores.get(w, 0) for w in words)
        length_factor = min(1.0, len(words) / 10)
        return score * length_factor

    def extract_keywords(self, text: str, n: int = 5) -> List[str]:
        """Extrahiere Top-N Keywords"""
        word_scores = self._calculate_word_scores(text)
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:n]]


# =============================================================================
# TEXT GENERATION - Markov Chain
# =============================================================================

class MarkovTextGenerator:
    """Markov-Chain basierte Text-Generierung."""

    def __init__(self, order: int = 2):
        self.order = order
        self.chain: Dict[Tuple, List[str]] = defaultdict(list)
        self.starters: List[Tuple] = []

    def train(self, texts: List[str]):
        """Trainiere mit Beispiel-Texten"""
        for text in texts:
            words = text.split()

            if len(words) < self.order:
                continue

            starter = tuple(words[:self.order])
            self.starters.append(starter)

            for i in range(len(words) - self.order):
                key = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                self.chain[key].append(next_word)

    def generate(self, max_length: int = 20, seed: Tuple[str, ...] = None) -> str:
        """Generiere neuen Text."""
        if not self.starters and not seed:
            return ""

        if seed and seed in self.chain:
            current = list(seed)
        elif self.starters:
            current = list(random.choice(self.starters))
        else:
            return ""

        for _ in range(max_length - self.order):
            key = tuple(current[-self.order:])

            if key not in self.chain:
                break

            next_options = self.chain[key]
            next_word = random.choice(next_options)
            current.append(next_word)

            if next_word.endswith(('.', '!', '?')):
                break

        return ' '.join(current)


# =============================================================================
# DEPENDENCY PARSER - Simplified
# =============================================================================

@dataclass
class DependencyRelation:
    """Eine Dependency-Relation"""
    head: str
    dependent: str
    relation: str
    head_pos: int
    dependent_pos: int


class SimpleDependencyParser:
    """Einfacher regelbasierter Dependency Parser für Deutsch."""

    VERBEN = [
        "sein", "haben", "werden", "können", "müssen", "wollen", "sollen",
        "machen", "tun", "gehen", "kommen", "sagen", "fragen", "antworten",
        "schalten", "starten", "stoppen", "öffnen", "schließen", "zeigen",
        "suchen", "finden", "spielen", "laufen", "arbeiten", "schlafen",
    ]

    ARTIKEL = ["der", "die", "das", "ein", "eine", "einen", "einem", "einer"]
    PRÄPOSITIONEN = ["in", "auf", "an", "bei", "mit", "ohne", "für", "gegen",
                     "über", "unter", "vor", "nach", "zwischen", "neben"]
    PRONOMEN = ["ich", "du", "er", "sie", "es", "wir", "ihr",
                "mich", "dich", "ihn", "uns", "euch", "mir", "dir", "ihm"]
    NEGATIONEN = ["nicht", "kein", "keine", "keinen", "niemals", "nie", "nichts"]

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse Text und extrahiere Dependencies."""
        text_lower = text.lower()
        tokens = self._tokenize(text_lower)

        result = {
            "tokens": tokens,
            "relations": [],
            "svo_triplets": [],
            "negated": False,
            "main_verb": None,
            "subject": None,
            "objects": [],
        }

        # Hauptverb
        verb_pos = self._find_verb(tokens)
        if verb_pos >= 0:
            result["main_verb"] = tokens[verb_pos]

        # Subjekt
        if verb_pos > 0:
            subject = self._find_subject(tokens, verb_pos)
            if subject:
                result["subject"] = subject
                result["relations"].append(DependencyRelation(
                    head=result["main_verb"],
                    dependent=subject,
                    relation="nsubj",
                    head_pos=verb_pos,
                    dependent_pos=tokens.index(subject) if subject in tokens else -1
                ))

        # Objekte
        if verb_pos >= 0:
            objects = self._find_objects(tokens, verb_pos)
            result["objects"] = objects
            for obj in objects:
                result["relations"].append(DependencyRelation(
                    head=result["main_verb"],
                    dependent=obj,
                    relation="dobj",
                    head_pos=verb_pos,
                    dependent_pos=tokens.index(obj) if obj in tokens else -1
                ))

        # SVO Triplets
        if result["subject"] and result["main_verb"]:
            for obj in result["objects"] or [None]:
                result["svo_triplets"].append((
                    result["subject"], result["main_verb"], obj
                ))

        # Negation
        result["negated"] = any(neg in tokens for neg in self.NEGATIONEN)

        return result

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'([.,!?])', r' \1', text)
        return text.split()

    def _find_verb(self, tokens: List[str]) -> int:
        for i, token in enumerate(tokens):
            token_stem = token.rstrip("etsn")
            if token in self.VERBEN or token_stem in self.VERBEN:
                return i
            if token.endswith(("en", "st", "t", "e")) and len(token) > 3:
                if token not in self.ARTIKEL + self.PRÄPOSITIONEN:
                    return i
        return -1

    def _find_subject(self, tokens: List[str], verb_pos: int) -> Optional[str]:
        if tokens[0] in self.PRONOMEN:
            return tokens[0]

        for i in range(verb_pos - 1, -1, -1):
            token = tokens[i]
            if token not in self.ARTIKEL and token not in self.VERBEN and len(token) > 2:
                return token
        return None

    def _find_objects(self, tokens: List[str], verb_pos: int) -> List[str]:
        objects = []
        for i in range(verb_pos + 1, len(tokens)):
            token = tokens[i]
            if token in self.ARTIKEL or token in self.PRÄPOSITIONEN or token in ".,!?":
                continue
            if len(token) > 2:
                objects.append(token)
        return objects

    def extract_action(self, text: str) -> Optional[Dict]:
        """Extrahiere Aktion für Commands."""
        parsed = self.parse(text)

        if not parsed["main_verb"]:
            return None

        return {
            "action": parsed["main_verb"],
            "target": parsed["objects"][0] if parsed["objects"] else None,
            "negated": parsed["negated"],
            "subject": parsed["subject"],
        }


# =============================================================================
# DIALOGUE ACT CLASSIFICATION
# =============================================================================

class DialogueActType:
    """Dialogue Act Typen"""
    STATEMENT = "statement"
    OPINION = "opinion"
    INFORM = "inform"
    REQUEST = "request"
    COMMAND = "command"
    SUGGESTION = "suggestion"
    PROMISE = "promise"
    OFFER = "offer"
    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKING = "thanking"
    APOLOGIZING = "apologizing"
    COMPLIMENT = "compliment"
    COMPLAINT = "complaint"
    YES_NO_QUESTION = "yes_no_question"
    WH_QUESTION = "wh_question"
    RHETORICAL_QUESTION = "rhetorical_question"
    ACCEPT = "accept"
    REJECT = "reject"
    ACKNOWLEDGE = "acknowledge"
    CLARIFICATION = "clarification"
    BACKCHANNEL = "backchannel"
    FILLER = "filler"


class DialogueActClassifier:
    """Klassifiziert Dialogue Acts."""

    ACT_PATTERNS = {
        DialogueActType.GREETING: [
            r"^(hallo|hi|hey|moin|guten\s*(morgen|tag|abend)|servus)",
        ],
        DialogueActType.FAREWELL: [
            r"(tschüss|bye|ciao|bis\s*(bald|dann|später)|gute\s*nacht)",
        ],
        DialogueActType.THANKING: [
            r"(dank|thanks|merci|thx)",
        ],
        DialogueActType.YES_NO_QUESTION: [
            r"^(ist|sind|hat|haben|kann|kannst|wird|werden|möchtest?|willst)\s",
            r"\?\s*$",
        ],
        DialogueActType.WH_QUESTION: [
            r"^(was|wer|wie|wo|wann|warum|wieso|weshalb|welche[rs]?)\s",
        ],
        DialogueActType.COMMAND: [
            r"^(mach|schalte|starte|stoppe|zeig|gib|such|finde|öffne)\s",
        ],
        DialogueActType.REQUEST: [
            r"(kannst\s*du|könntest\s*du|würdest\s*du)",
            r"(bitte|wärst\s*du\s*so\s*nett)",
        ],
        DialogueActType.ACKNOWLEDGE: [
            r"^(ok|okay|alles\s*klar|verstehe|achso|aha)",
            r"^(ja|genau|stimmt|richtig)",
        ],
        DialogueActType.ACCEPT: [
            r"^(ja|klar|gerne|natürlich|auf\s*jeden\s*fall)",
        ],
        DialogueActType.REJECT: [
            r"^(nein|ne|nö|lieber\s*nicht|keine\s*lust)",
        ],
    }

    def __init__(self):
        self.compiled_patterns = {
            act: [re.compile(p, re.IGNORECASE) for p in patterns]
            for act, patterns in self.ACT_PATTERNS.items()
        }

    def classify(self, text: str) -> List[Tuple[str, float]]:
        """Klassifiziere Dialogue Act(s)."""
        text_clean = text.strip()
        results = []

        for act_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text_clean):
                    match = pattern.search(text_clean)
                    match_ratio = len(match.group(0)) / len(text_clean) if text_clean else 0
                    confidence = min(0.95, 0.6 + match_ratio * 0.4)
                    results.append((act_type, confidence))
                    break

        if not results:
            results.append((DialogueActType.STATEMENT, 0.3))

        results = list(set(results))
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    def get_primary_act(self, text: str) -> Tuple[str, float]:
        """Hole primären Dialogue Act"""
        results = self.classify(text)
        return results[0] if results else (DialogueActType.STATEMENT, 0.3)

    def get_expected_response_acts(self, act) -> List:
        """Gibt erwartete Response-Acts für einen Dialogue Act zurück."""
        response_map = {
            DialogueActType.GREETING: [DialogueActType.GREETING, DialogueActType.STATEMENT],
            DialogueActType.FAREWELL: [DialogueActType.FAREWELL],
            DialogueActType.YES_NO_QUESTION: [DialogueActType.ACCEPT, DialogueActType.REJECT, DialogueActType.STATEMENT],
            DialogueActType.WH_QUESTION: [DialogueActType.STATEMENT],
            DialogueActType.COMMAND: [DialogueActType.ACKNOWLEDGE, DialogueActType.REJECT],
            DialogueActType.REQUEST: [DialogueActType.ACCEPT, DialogueActType.REJECT, DialogueActType.STATEMENT],
            DialogueActType.ACKNOWLEDGE: [DialogueActType.STATEMENT],
            DialogueActType.THANKING: [DialogueActType.ACKNOWLEDGE],
            DialogueActType.ACCEPT: [DialogueActType.STATEMENT, DialogueActType.THANKING],
            DialogueActType.REJECT: [DialogueActType.STATEMENT],
            DialogueActType.STATEMENT: [DialogueActType.STATEMENT, DialogueActType.ACKNOWLEDGE],
        }
        return response_map.get(act, [DialogueActType.STATEMENT])


# =============================================================================
# COHERENCE SCORING
# =============================================================================

class CoherenceScorer:
    """Bewertet Kohärenz/Qualität von Texten."""

    def __init__(self):
        self.good_patterns = [
            r"^\*[^*]+\*",
            r"😊",
            r"\?$",
            r"!$",
        ]

        self.bad_patterns = [
            r"(\b\w+\b)\s+\1",
            r"\.{4,}",
            r"!{3,}",
            r"^\s*$",
        ]

        self.persona_words = {
            "positiv": ["😊", "*", "wedelt", "ohren", "schweif"],
            "freundlich": ["gerne", "freut", "schön", "toll"],
        }

    def score(self, text: str, context: Dict[str, Any] = None) -> Tuple[float, List[str]]:
        """Bewerte Text-Qualität."""
        if not text:
            return 0.0, ["empty_text"]

        score = 0.5
        issues = []

        words = text.split()
        if len(words) < 2:
            score -= 0.2
            issues.append("too_short")
        elif len(words) > 50:
            score -= 0.1
            issues.append("too_long")
        elif 5 <= len(words) <= 20:
            score += 0.1

        for pattern in self.good_patterns:
            if re.search(pattern, text):
                score += 0.1

        for pattern in self.bad_patterns:
            if re.search(pattern, text):
                score -= 0.15
                issues.append(f"bad_pattern")

        text_lower = text.lower()
        persona_score = 0
        for category, words_list in self.persona_words.items():
            for word in words_list:
                if word in text_lower:
                    persona_score += 0.05
        score += min(0.2, persona_score)

        score = max(0.0, min(1.0, score))

        return score, issues

    def select_best(self, candidates: List[str],
                   context: Dict[str, Any] = None) -> Tuple[str, float]:
        """Wähle besten Kandidaten"""
        if not candidates:
            return "", 0.0

        scored = [(text, self.score(text, context)[0]) for text in candidates]
        return max(scored, key=lambda x: x[1])


# =============================================================================
# ANTI-REPETITION TRACKER
# =============================================================================

class AntiRepetitionTracker:
    """Verhindert Wiederholungen in Antworten."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.recent_phrases: List[str] = []
        self.phrase_counts: Counter = Counter()

    def record(self, phrase: str):
        """Speichere verwendete Phrase"""
        phrase_lower = phrase.lower()
        self.recent_phrases.append(phrase_lower)
        self.phrase_counts[phrase_lower] += 1

        if len(self.recent_phrases) > self.window_size:
            old = self.recent_phrases.pop(0)
            self.phrase_counts[old] -= 1
            if self.phrase_counts[old] <= 0:
                del self.phrase_counts[old]

    def get_freshness(self, phrase: str) -> float:
        """Frische-Score (0-1). 1.0 = nie verwendet."""
        phrase_lower = phrase.lower()

        if phrase_lower not in self.phrase_counts:
            return 1.0

        if self.recent_phrases and phrase_lower == self.recent_phrases[-1]:
            return 0.0

        count = self.phrase_counts[phrase_lower]
        freq_penalty = 1.0 / (1 + count * 0.3)

        return freq_penalty

    def select_fresh(self, candidates: List[str]) -> str:
        """Wähle frischesten Kandidaten"""
        if not candidates:
            return ""

        scored = [(c, self.get_freshness(c)) for c in candidates]
        total = sum(score for _, score in scored)

        if total == 0:
            return random.choice(candidates)

        r = random.uniform(0, total)
        cumsum = 0
        for candidate, score in scored:
            cumsum += score
            if cumsum >= r:
                return candidate

        return candidates[-1]


# =============================================================================
# SEMANTIC SEARCH ENGINE (NEU!)
# =============================================================================

class SemanticSearchEngine:
    """
    Semantische Suche über Texte.

    Kombiniert:
    - Keyword-Matching
    - Fuzzy-Matching
    - Embedding-Similarity
    """

    def __init__(self):
        self.fuzzy = AdvancedFuzzyMatcher()
        self.embeddings = SimpleWordEmbeddings()
        self.documents: List[Dict] = []  # {"id", "text", "embedding", "keywords"}
        self._trained = False

    def add_document(self, doc_id: str, text: str, metadata: Dict = None):
        """Füge Dokument zum Index hinzu"""
        keywords = self._extract_keywords(text)

        self.documents.append({
            "id": doc_id,
            "text": text,
            "keywords": keywords,
            "metadata": metadata or {},
        })

    def build_index(self):
        """Baue Embedding-Index auf"""
        all_texts = [doc["text"] for doc in self.documents]
        self.embeddings.train(all_texts)

        for doc in self.documents:
            doc["embedding"] = self.embeddings.sentence_embedding(doc["text"])

        self._trained = True

    def search(self, query: str, top_k: int = 5,
               use_semantic: bool = True,
               use_keyword: bool = True) -> List[Tuple[Dict, float]]:
        """
        Suche nach relevanten Dokumenten.

        Returns: [(doc, score), ...]
        """
        if not self.documents:
            return []

        results = []
        query_keywords = self._extract_keywords(query)
        query_embedding = self.embeddings.sentence_embedding(query) if self._trained else None

        for doc in self.documents:
            score = 0.0

            # Keyword Score
            if use_keyword:
                keyword_score = self._keyword_match_score(query_keywords, doc["keywords"])
                score += keyword_score * 0.4

            # Semantic Score
            if use_semantic and self._trained and query_embedding:
                semantic_score = self._cosine_similarity(
                    query_embedding, doc.get("embedding", [])
                )
                score += semantic_score * 0.6

            results.append((doc, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiere Keywords"""
        stopwords = {"der", "die", "das", "ein", "eine", "und", "oder", "aber",
                     "ist", "sind", "war", "bin", "hat", "haben", "wird",
                     "zu", "in", "an", "auf", "für", "mit", "von", "bei"}

        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if len(w) > 2 and w not in stopwords]

    def _keyword_match_score(self, query_kw: List[str], doc_kw: List[str]) -> float:
        """Keyword-Match Score"""
        if not query_kw or not doc_kw:
            return 0.0

        matches = 0
        for qk in query_kw:
            for dk in doc_kw:
                if qk == dk:
                    matches += 1
                elif self.fuzzy.combined_similarity(qk, dk) > 0.85:
                    matches += 0.7

        return min(1.0, matches / len(query_kw))

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Cosine Similarity"""
        if not v1 or not v2:
            return 0.0

        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(x*x for x in v1))
        mag2 = math.sqrt(sum(x*x for x in v2))

        if mag1 > 0 and mag2 > 0:
            return dot / (mag1 * mag2)
        return 0.0


# =============================================================================
# TEMPLATE-BASED TEXT GENERATOR (NEU!)
# =============================================================================

class TemplateTextGenerator:
    """
    Template-basierte Text-Generierung mit Variationen.

    Erlaubt:
    - Platzhalter
    - Optionale Teile
    - Synonyme
    - Stimmungs-Anpassung
    """

    def __init__(self):
        self.templates: Dict[str, List[str]] = {}
        self.synonyms: Dict[str, List[str]] = self._init_synonyms()
        self.mood_modifiers: Dict[str, Dict] = self._init_mood_modifiers()
        self.anti_rep = AntiRepetitionTracker(window_size=30)

    def _init_synonyms(self) -> Dict[str, List[str]]:
        """Initialisiere Synonym-Gruppen"""
        return {
            "freuen": ["freuen", "freu mich", "bin happy", "bin froh"],
            "toll": ["toll", "super", "klasse", "spitze", "prima"],
            "schlecht": ["schlecht", "nicht gut", "mies", "doof"],
            "verstehe": ["verstehe", "hab verstanden", "alles klar", "okay"],
            "moment": ["moment", "augenblick", "sekunde", "gleich"],
            "gerne": ["gerne", "klar", "na klar", "selbstverständlich"],
        }

    def _init_mood_modifiers(self) -> Dict[str, Dict]:
        """Stimmungs-Modifikatoren"""
        return {
            "energetic": {
                "prefix": ["*springt auf*", "*wedelt begeistert*"],
                "suffix": ["!", "!!"],
                "intensifiers": ["total", "mega", "richtig"],
            },
            "tired": {
                "prefix": ["*gähnt*", "*streckt sich müde*"],
                "suffix": ["...", "."],
                "intensifiers": ["etwas", "bisschen"],
            },
            "neutral": {
                "prefix": ["*nickt*", "*schaut*"],
                "suffix": [".", "!"],
                "intensifiers": [],
            },
        }

    def add_template(self, category: str, template: str):
        """Füge Template hinzu"""
        if category not in self.templates:
            self.templates[category] = []
        self.templates[category].append(template)

    def generate(self, category: str,
                 variables: Dict[str, str] = None,
                 mood: str = "neutral") -> str:
        """
        Generiere Text aus Template.

        Variables: {"name": "Max", "topic": "Wetter"}
        """
        if category not in self.templates:
            return ""

        # Wähle frisches Template
        templates = self.templates[category]
        template = self.anti_rep.select_fresh(templates)

        # Variablen ersetzen
        text = template
        if variables:
            for key, value in variables.items():
                text = text.replace(f"{{{key}}}", value)

        # Synonyme ersetzen
        text = self._apply_synonyms(text)

        # Stimmung anwenden
        text = self._apply_mood(text, mood)

        # Tracken
        self.anti_rep.record(template)

        return text

    def _apply_synonyms(self, text: str) -> str:
        """Ersetze Wörter durch Synonyme"""
        for base_word, synonyms in self.synonyms.items():
            if base_word in text.lower():
                replacement = random.choice(synonyms)
                text = re.sub(
                    rf'\b{base_word}\b',
                    replacement,
                    text,
                    flags=re.IGNORECASE
                )
        return text

    def _apply_mood(self, text: str, mood: str) -> str:
        """Wende Stimmungs-Modifikatoren an"""
        if mood not in self.mood_modifiers:
            mood = "neutral"

        mods = self.mood_modifiers[mood]

        # Prefix
        if mods["prefix"] and random.random() > 0.5:
            text = random.choice(mods["prefix"]) + " " + text

        # Suffix anpassen
        if mods["suffix"]:
            if text.endswith("."):
                text = text[:-1] + random.choice(mods["suffix"])

        return text


# =============================================================================
# MAIN NLP CLASS - KOMBINIERT ALLES
# =============================================================================

class HoloNLP:
    """
    Hauptklasse für NLP-Operationen v5.1.

    Erweitert um:
    - IntentDatabase (60+ Intents)
    - GermanSentenceParser (Satzstruktur)
    - Erweiterte NER (Namen, Gaming, Anime)
    - LightweightVectorEngine (Pi-optimiert)
    - LLM-Routing Entscheidung

    Optimiert für Raspberry Pi - entscheidet selbst ob LLM nötig ist!
    """

    def __init__(self):
        # Core Components
        self.fuzzy = AdvancedFuzzyMatcher()
        self.sentiment = AdvancedSentimentAnalyzer()
        self.entities = EntityExtractor()
        self.coherence = CoherenceScorer()
        self.anti_rep = AntiRepetitionTracker()

        # v5.0: Intent & Sentence Analysis
        self.intent_db = IntentDatabase()
        self.sentence_parser = GermanSentenceParser()

        # v5.1: Lightweight Vector Engine (Pi-optimiert!)
        self.vectors = LightweightVectorEngine()

        # Text Processing
        self.embeddings = SimpleWordEmbeddings()
        self.summarizer = TextSummarizer()
        self.dep_parser = SimpleDependencyParser()
        self.dialogue_acts = DialogueActClassifier()

        # Generation
        self.markov = MarkovTextGenerator(order=2)
        self.templates = TemplateTextGenerator()

        # Search
        self.search = SemanticSearchEngine()

        # Lazy-loaded Intent
        self._understanding = None

        self._train_embeddings()

        logger.info(f"✅ HoloNLP v5.1 initialisiert (Pi-optimiert)")
        logger.info(f"   Intents: {len(self.intent_db.intents)}")
        logger.info(f"   Entities: {len(self.entities.known_entities)}")
        logger.info(f"   Vector-Intents: {len(self.vectors.intent_vectors)}")

    def _train_embeddings(self):
        """Trainiere Embeddings mit Beispiel-Sätzen"""
        training_data = [
            "Ich freue mich dich zu sehen",
            "Das Licht in der Küche ist an",
            "Der NAS Server läuft ohne Probleme",
            "Wie geht es dir heute",
            "Mir geht es gut danke der Nachfrage",
            "Schalte das Licht im Wohnzimmer an",
            "Der Wolf wedelt mit dem Schweif",
        ]
        self.embeddings.train(training_data)

    def get_understanding(self):
        """Hole SmartUnderstanding (lazy)"""
        if self._understanding is None:
            self._understanding = get_smart_understanding()
        return self._understanding

    # =========================================================================
    # HAUPTMETHODEN
    # =========================================================================

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analysiere Text vollständig (v5.0).

        Für Intent: Nutze SmartUnderstanding direkt!
        """
        start = time.time()

        # Sentiment
        sentiment_result = self.sentiment.analyze(text)

        # Entities (v5.0: inkl. Namen, Gaming, Anime)
        entities = self.entities.extract(text)

        # v5.0: Intent aus IntentDatabase (Pattern-basiert)
        intent_match = self.intent_db.get_intent(text)
        intent_name, intent_conf, intent_category = intent_match

        # v5.1: Vector-basiertes Intent + LLM-Routing
        needs_llm, vector_intent, vector_conf = self.vectors.needs_llm_response(text)

        # Kombiniere Pattern + Vector für beste Entscheidung
        if intent_conf > vector_conf and intent_name:
            final_intent = intent_name
            final_conf = intent_conf
        else:
            final_intent = vector_intent
            final_conf = vector_conf

        # v5.0: Satzstruktur-Analyse
        sentence_info = self.sentence_parser.parse(text)

        # Dialogue Act
        dialogue_act, act_conf = self.dialogue_acts.get_primary_act(text)

        # Dependencies
        deps = self.dep_parser.parse(text)

        elapsed = time.time() - start

        return {
            "text": text,
            # Sentiment
            "sentiment": sentiment_result.sentiment,
            "sentiment_score": sentiment_result.score,
            "sentiment_confidence": sentiment_result.confidence,
            "is_sarcastic": sentiment_result.is_sarcastic,
            "is_mixed": sentiment_result.is_mixed,
            # Entities (v5.0)
            "entities": [
                {
                    "type": e.type,
                    "value": e.value,
                    "original": e.original,
                    "confidence": e.confidence,
                }
                for e in entities
            ],
            # v5.1: Intent (kombiniert Pattern + Vector)
            "intent": final_intent,
            "intent_confidence": final_conf,
            "intent_category": intent_category,
            # v5.1: LLM-Routing
            "needs_llm": needs_llm,
            "vector_intent": vector_intent,
            "vector_confidence": vector_conf,
            # v5.0: Satzstruktur
            "sentence_type": sentence_info.get("sentence_type"),
            "question_word": sentence_info.get("question_word"),
            "tense": sentence_info.get("tense"),
            "mood": sentence_info.get("mood"),
            # Dialogue Act
            "dialogue_act": dialogue_act,
            "dialogue_act_confidence": act_conf,
            # Dependency Parse
            "main_verb": sentence_info.get("main_verb") or deps.get("main_verb"),
            "subject": sentence_info.get("subject") or deps.get("subject"),
            "objects": deps.get("objects", []),
            "negated": sentence_info.get("negated", False) or deps.get("negated", False),
            # Meta
            "processing_time_ms": elapsed * 1000,
        }

    def needs_llm(self, text: str) -> Tuple[bool, str, float]:
        """
        Schnelle Entscheidung: Braucht dieser Text das LLM?

        Returns:
            (needs_llm: bool, intent: str, confidence: float)

        Beispiel:
            >>> nlp.needs_llm("Hallo Holo!")
            (False, "greeting", 0.85)

            >>> nlp.needs_llm("Erkläre mir Quantenphysik")
            (True, "complex_question", 0.72)
        """
        return self.vectors.needs_llm_response(text)

    def fuzzy_match(self, query: str, candidates: List[str],
                   threshold: float = 0.7) -> Tuple[Optional[str], float]:
        """Fuzzy Match"""
        return self.fuzzy.find_best_match(query, candidates, threshold)

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Semantische Ähnlichkeit"""
        return self.embeddings.sentence_similarity(text1, text2)

    def summarize(self, text: str, n_sentences: int = 2) -> str:
        """Fasse Text zusammen"""
        return self.summarizer.summarize_extractive(text, n_sentences)

    def extract_keywords(self, text: str, n: int = 5) -> List[str]:
        """Extrahiere Keywords"""
        return self.summarizer.extract_keywords(text, n)

    def score_response(self, response: str,
                      context: Dict = None) -> Tuple[float, List[str]]:
        """Bewerte Antwort-Qualität"""
        return self.coherence.score(response, context)

    def select_best_response(self, candidates: List[str],
                            context: Dict = None) -> str:
        """Wähle beste Antwort"""
        scored = []
        for candidate in candidates:
            coh_score, _ = self.coherence.score(candidate, context)
            fresh_score = self.anti_rep.get_freshness(candidate)
            combined = coh_score * 0.7 + fresh_score * 0.3
            scored.append((candidate, combined))

        best = max(scored, key=lambda x: x[1])
        self.anti_rep.record(best[0])

        return best[0]


# =============================================================================
# COMPATIBILITY: HoloNLPV2
# =============================================================================

class HoloNLPV2(HoloNLP):
    """Erweiterte Version mit Deep Understanding."""

    def understand_deep(self, text: str) -> Dict[str, Any]:
        """
        Tiefes Verständnis.

        HINWEIS: Für Intent, nutze SmartUnderstanding!
        """
        base = self.analyze(text)

        # Zusätzlich: Intent via SmartUnderstanding
        understanding = self.get_understanding()
        if understanding:
            intent_result = understanding.understand(text)
            base["intent"] = intent_result.get("intent", "general")
            base["intent_score"] = intent_result.get("confidence", 0.5)
            base["is_followup"] = intent_result.get("is_followup", False)
        else:
            base["intent"] = "general"
            base["intent_score"] = 0.5

        return base


# =============================================================================
# LEGACY COMPATIBILITY - TFIDFIntentDetector
# =============================================================================

class TFIDFIntentDetector:
    """
    LEGACY WRAPPER - Nutzt SmartUnderstanding.

    Für Abwärtskompatibilität mit holo_brain.py.
    Neue Code sollte SmartUnderstanding direkt nutzen!
    """

    def __init__(self):
        self._understanding = None
        logger.warning("⚠️ TFIDFIntentDetector ist deprecated - nutze SmartUnderstanding!")

    def _get_understanding(self):
        if self._understanding is None:
            self._understanding = get_smart_understanding()
        return self._understanding

    def detect(self, text: str) -> Dict:
        """Legacy detect Methode"""
        understanding = self._get_understanding()
        if understanding:
            result = understanding.understand(text)
            return {
                "intent": result.get("intent", "general"),
                "confidence": result.get("confidence", 0.5),
                "requires_llm": result.get("requires_llm", True),
            }
        return {"intent": "general", "confidence": 0.5, "requires_llm": True}

    def classify(self, text: str) -> str:
        """Legacy classify Methode"""
        result = self.detect(text)
        return result.get("intent", "general")

    def train(self, *args, **kwargs):
        """Legacy train - nicht mehr nötig"""
        logger.debug("TFIDFIntentDetector.train() ist deprecated - SmartUnderstanding braucht kein Training")
        pass


# =============================================================================
# ERWEITERTE NLP-ALGORITHMEN v4.1
# =============================================================================

class EmotionalToneAnalyzer:
    """
    Erweiterte emotionale Tonanalyse für differenzierte Stimmungserkennung.
    Erkennt subtile emotionale Nuancen und kontextuelle Stimmungswechsel.
    """

    def __init__(self):
        self._init_tone_lexicons()
        self._init_pattern_rules()

    def _init_tone_lexicons(self):
        """Initialisiert erweiterte emotionale Lexika"""
        # Primäre Emotionen mit Gewichtung
        self.primary_emotions = {
            # FREUDE-SPEKTRUM
            "freude": {
                "euphorie": ["ekstatisch", "überwältigt", "beseelt", "verzückt", "überglücklich"],
                "begeisterung": ["begeistert", "fasziniert", "hingerissen", "entzückt", "enthusiastisch"],
                "zufriedenheit": ["zufrieden", "glücklich", "froh", "erfreut", "content"],
                "gelassenheit": ["gelassen", "ruhig", "entspannt", "friedlich", "ausgeglichen"],
            },
            # TRAUER-SPEKTRUM
            "trauer": {
                "verzweiflung": ["verzweifelt", "hoffnungslos", "gebrochen", "zerbrochen", "am Ende"],
                "kummer": ["traurig", "niedergeschlagen", "bedrückt", "melancholisch", "schwermütig"],
                "sehnsucht": ["sehnsüchtig", "vermissend", "nostalgisch", "wehmütig"],
                "enttäuschung": ["enttäuscht", "desillusioniert", "ernüchtert", "frustriert"],
            },
            # WUT-SPEKTRUM
            "wut": {
                "rage": ["rasend", "tobend", "außer sich", "blind vor Wut", "kochend"],
                "zorn": ["zornig", "wütend", "erbost", "aufgebracht", "empört"],
                "ärger": ["ärgerlich", "verärgert", "genervt", "gereizt", "irritiert"],
                "frustration": ["frustriert", "entnervt", "angespannt", "ungeduldig"],
            },
            # ANGST-SPEKTRUM
            "angst": {
                "panik": ["panisch", "in Todesangst", "paralysiert", "erstarrt"],
                "furcht": ["ängstlich", "verängstigt", "furchtsam", "eingeschüchtert"],
                "sorge": ["besorgt", "beunruhigt", "in Sorge", "unruhig"],
                "unsicherheit": ["unsicher", "verunsichert", "nervös", "beklommen"],
            },
            # LIEBE-SPEKTRUM
            "liebe": {
                "leidenschaft": ["leidenschaftlich", "hingegeben", "verzehrend", "brennend"],
                "zuneigung": ["liebevoll", "zugetan", "herzlich", "warmherzig"],
                "fürsorge": ["fürsorglich", "beschützend", "umsorgend", "behutsam"],
                "verbundenheit": ["verbunden", "nah", "vertraut", "innig"],
            },
            # ÜBERRASCHUNG-SPEKTRUM
            "ueberraschung": {
                "schock": ["schockiert", "fassungslos", "sprachlos", "erschüttert"],
                "staunen": ["erstaunt", "verwundert", "verblüfft", "baff"],
                "neugier": ["neugierig", "interessiert", "gespannt", "wissbegierig"],
            },
        }

        # Kontextuelle Modifikatoren
        self.modifiers = {
            "verstärker": ["sehr", "extrem", "total", "absolut", "mega", "super", "ultra", "richtig", "echt", "voll"],
            "abschwächer": ["etwas", "ein bisschen", "leicht", "ein wenig", "kaum", "minimal"],
            "negation": ["nicht", "kein", "keine", "niemals", "nie", "ohne", "kaum"],
        }

    def _init_pattern_rules(self):
        """Initialisiert Mustererkennung für komplexe Emotionen"""
        self.patterns = {
            "ironie": [
                r"ja\s+klar",
                r"super\s+toll",
                r"na\s+toll",
                r"oh\s+wie\s+(schön|toll)",
                r"wirklich\?+$",
            ],
            "sarkasmus": [
                r"das\s+war\s+ja\s+zu\s+erwarten",
                r"überraschung",
                r"hätte\s+ich\s+nie\s+gedacht",
                r"wie\s+originell",
            ],
            "freundliche_ablehnung": [
                r"ich\s+schätze",
                r"das\s+ist\s+nett\s+aber",
                r"danke\s+aber",
            ],
        }
        self._compiled_patterns = {
            key: [re.compile(p, re.IGNORECASE) for p in patterns]
            for key, patterns in self.patterns.items()
        }

    def analyze_emotional_tone(self, text: str) -> Dict[str, Any]:
        """
        Analysiert den emotionalen Ton eines Textes.

        Returns:
            Dict mit primary_emotion, intensity, subtype, modifiers, patterns
        """
        text_lower = text.lower()
        words = text_lower.split()

        # Finde primäre Emotion
        emotion_scores = {}
        for emotion, subtypes in self.primary_emotions.items():
            score = 0
            detected_subtype = None
            for subtype, keywords in subtypes.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        score += 1
                        detected_subtype = subtype
            if score > 0:
                emotion_scores[emotion] = {"score": score, "subtype": detected_subtype}

        # Bestimme dominante Emotion
        primary_emotion = None
        max_score = 0
        subtype = None
        for emotion, data in emotion_scores.items():
            if data["score"] > max_score:
                max_score = data["score"]
                primary_emotion = emotion
                subtype = data["subtype"]

        # Analysiere Modifikatoren
        detected_modifiers = []
        intensity = 1.0
        for word in words:
            if word in self.modifiers["verstärker"]:
                intensity *= 1.3
                detected_modifiers.append(("verstärker", word))
            elif word in self.modifiers["abschwächer"]:
                intensity *= 0.7
                detected_modifiers.append(("abschwächer", word))
            elif word in self.modifiers["negation"]:
                intensity *= -1 if intensity > 0 else 1
                detected_modifiers.append(("negation", word))

        # Erkenne Muster
        detected_patterns = []
        for pattern_type, compiled_list in self._compiled_patterns.items():
            for pattern in compiled_list:
                if pattern.search(text):
                    detected_patterns.append(pattern_type)
                    break

        return {
            "primary_emotion": primary_emotion or "neutral",
            "subtype": subtype,
            "intensity": min(max(intensity, 0.1), 2.0),
            "modifiers": detected_modifiers,
            "patterns": detected_patterns,
            "confidence": min(max_score * 0.25, 1.0) if max_score > 0 else 0.5,
        }


class ContextualResponseGenerator:
    """
    Kontextbasierter Antwortgenerator für natürlichere Dialoge.
    Berücksichtigt Gesprächskontext, emotionalen Ton und Benutzerpräferenzen.
    """

    def __init__(self):
        self._init_response_templates()
        self._init_transition_phrases()

    def _init_response_templates(self):
        """Initialisiert kontextuelle Antwort-Templates"""
        self.templates = {
            "empathie": {
                "freude": [
                    "Das freut mich zu hören!",
                    "Wie schön für dich!",
                    "Das klingt wunderbar!",
                    "Ich kann deine Freude nachempfinden!",
                ],
                "trauer": [
                    "Das tut mir wirklich leid.",
                    "Ich kann verstehen, dass das schwer ist.",
                    "Das muss wirklich belastend sein.",
                    "Ich bin für dich da.",
                ],
                "wut": [
                    "Ich kann verstehen, dass dich das ärgert.",
                    "Das wäre auch für mich frustrierend.",
                    "Es ist okay, wütend zu sein.",
                    "Ich kann nachvollziehen, warum du aufgebracht bist.",
                ],
                "angst": [
                    "Es ist verständlich, dass du besorgt bist.",
                    "Deine Ängste sind berechtigt.",
                    "Es ist okay, Angst zu haben.",
                    "Ich bin hier, um zu helfen.",
                ],
            },
            "interesse": {
                "neutral": [
                    "Erzähl mir mehr darüber!",
                    "Das klingt interessant!",
                    "Wie meinst du das genau?",
                    "Kannst du das näher erklären?",
                ],
                "neugier": [
                    "Oh, das ist spannend!",
                    "Da bin ich aber gespannt!",
                    "Jetzt machst du mich neugierig!",
                    "Das würde ich gerne wissen!",
                ],
            },
            "bestaetigung": [
                "Ich verstehe.",
                "Alles klar!",
                "Das macht Sinn.",
                "Ja, das kann ich nachvollziehen.",
                "Verstanden!",
            ],
            "ermutigung": [
                "Du schaffst das!",
                "Ich glaube an dich!",
                "Das wird schon!",
                "Kopf hoch!",
                "Gemeinsam schaffen wir das!",
            ],
        }

    def _init_transition_phrases(self):
        """Initialisiert Übergangsphrasen für flüssigere Dialoge"""
        self.transitions = {
            "themenwechsel": [
                "Übrigens,",
                "Apropos,",
                "Da fällt mir ein,",
                "Wenn wir schon dabei sind,",
                "Das erinnert mich an",
            ],
            "vertiefung": [
                "Um darauf zurückzukommen,",
                "Was das betrifft,",
                "In diesem Zusammenhang,",
                "Diesbezüglich,",
            ],
            "zusammenfassung": [
                "Also zusammengefasst,",
                "Kurz gesagt,",
                "Mit anderen Worten,",
                "Im Wesentlichen,",
            ],
            "gegensatz": [
                "Andererseits,",
                "Allerdings,",
                "Jedoch,",
                "Aber bedenke,",
            ],
        }

    def generate_contextual_response(
        self,
        emotion: str,
        response_type: str = "empathie",
        use_transition: bool = False,
        transition_type: str = None
    ) -> str:
        """
        Generiert eine kontextbezogene Antwort.

        Args:
            emotion: Erkannte Emotion des Benutzers
            response_type: Art der gewünschten Antwort
            use_transition: Ob eine Übergangsphrase verwendet werden soll
            transition_type: Art der Übergangsphrase

        Returns:
            Generierte Antwort
        """
        response_parts = []

        # Füge Übergangsphrase hinzu
        if use_transition and transition_type in self.transitions:
            response_parts.append(random.choice(self.transitions[transition_type]))

        # Wähle passende Antwort
        if response_type == "empathie":
            if emotion in self.templates["empathie"]:
                response_parts.append(random.choice(self.templates["empathie"][emotion]))
            else:
                response_parts.append(random.choice(self.templates["bestaetigung"]))
        elif response_type == "interesse":
            emotion_key = emotion if emotion in self.templates["interesse"] else "neutral"
            response_parts.append(random.choice(self.templates["interesse"][emotion_key]))
        elif response_type in self.templates:
            if isinstance(self.templates[response_type], list):
                response_parts.append(random.choice(self.templates[response_type]))
            elif isinstance(self.templates[response_type], dict):
                key = emotion if emotion in self.templates[response_type] else list(self.templates[response_type].keys())[0]
                response_parts.append(random.choice(self.templates[response_type][key]))

        return " ".join(response_parts)


class SemanticClusterEngine:
    """
    Semantisches Clustering für Themen- und Konzepterkennung.
    Gruppiert verwandte Begriffe und erkennt thematische Zusammenhänge.
    """

    def __init__(self):
        self._init_semantic_clusters()

    def _init_semantic_clusters(self):
        """Initialisiert semantische Cluster"""
        self.clusters = {
            "technologie": {
                "core": ["computer", "software", "hardware", "app", "programm", "system"],
                "web": ["internet", "website", "browser", "online", "cloud", "server"],
                "gaming": ["spiel", "game", "zocken", "controller", "konsole", "pc"],
                "mobile": ["handy", "smartphone", "tablet", "app", "android", "ios"],
            },
            "gefuehle": {
                "positiv": ["glücklich", "froh", "zufrieden", "begeistert", "entspannt"],
                "negativ": ["traurig", "wütend", "ängstlich", "frustriert", "gestresst"],
                "neutral": ["gelassen", "ruhig", "ausgeglichen", "neutral", "sachlich"],
            },
            "aktivitaeten": {
                "freizeit": ["spielen", "lesen", "schauen", "hören", "entspannen"],
                "arbeit": ["arbeiten", "lernen", "studieren", "programmieren", "schreiben"],
                "sport": ["laufen", "schwimmen", "trainieren", "joggen", "wandern"],
                "sozial": ["treffen", "reden", "feiern", "besuchen", "einladen"],
            },
            "zeit": {
                "vergangenheit": ["gestern", "letztens", "früher", "damals", "vor"],
                "gegenwart": ["heute", "jetzt", "gerade", "momentan", "aktuell"],
                "zukunft": ["morgen", "bald", "später", "demnächst", "irgendwann"],
            },
            "orte": {
                "zuhause": ["zuhause", "wohnung", "haus", "zimmer", "küche", "wohnzimmer"],
                "draussen": ["draußen", "park", "wald", "stadt", "natur", "garten"],
                "arbeit": ["büro", "firma", "arbeit", "schule", "uni", "werkstatt"],
            },
        }

        # Baue inverses Mapping
        self.word_to_cluster = {}
        for category, subclusters in self.clusters.items():
            for subcluster, words in subclusters.items():
                for word in words:
                    self.word_to_cluster[word.lower()] = {
                        "category": category,
                        "subcluster": subcluster
                    }

    def identify_clusters(self, text: str) -> Dict[str, List[str]]:
        """
        Identifiziert semantische Cluster im Text.

        Returns:
            Dict mit gefundenen Clustern und deren Begriffen
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        found_clusters = {}
        for word in words:
            if word in self.word_to_cluster:
                info = self.word_to_cluster[word]
                category = info["category"]
                if category not in found_clusters:
                    found_clusters[category] = {
                        "words": [],
                        "subclusters": set()
                    }
                found_clusters[category]["words"].append(word)
                found_clusters[category]["subclusters"].add(info["subcluster"])

        # Konvertiere sets zu lists für JSON-Kompatibilität
        for category in found_clusters:
            found_clusters[category]["subclusters"] = list(found_clusters[category]["subclusters"])

        return found_clusters

    def get_related_terms(self, word: str, limit: int = 10) -> List[str]:
        """Findet verwandte Begriffe zu einem Wort"""
        word_lower = word.lower()
        if word_lower not in self.word_to_cluster:
            return []

        info = self.word_to_cluster[word_lower]
        category = info["category"]
        subcluster = info["subcluster"]

        # Hole alle Wörter aus demselben Subcluster
        related = [w for w in self.clusters[category][subcluster] if w.lower() != word_lower]

        # Füge Wörter aus anderen Subclustern der gleichen Kategorie hinzu
        for other_subcluster, words in self.clusters[category].items():
            if other_subcluster != subcluster:
                for w in words:
                    if w.lower() not in related and w.lower() != word_lower:
                        related.append(w)

        return related[:limit]


class AdaptiveMarkovChain:
    """
    Adaptive Markov-Kette für kontextbewusste Textgenerierung.
    Lernt aus Eingaben und passt sich an den Stil an.
    """

    def __init__(self, order: int = 2):
        self.order = order
        self.chains: Dict[Tuple, Counter] = defaultdict(Counter)
        self.start_tokens: List[Tuple] = []
        self.vocabulary: Set[str] = set()
        self._trained = False

    def train(self, text: str):
        """Trainiert die Markov-Kette mit neuem Text"""
        tokens = self._tokenize(text)
        if len(tokens) < self.order + 1:
            return

        # Füge Start-Token hinzu
        self.start_tokens.append(tuple(tokens[:self.order]))

        # Baue Ketten auf
        for i in range(len(tokens) - self.order):
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            self.chains[state][next_token] += 1
            self.vocabulary.add(next_token)

        self._trained = True

    def train_batch(self, texts: List[str]):
        """Trainiert mit mehreren Texten"""
        for text in texts:
            self.train(text)

    def generate(self, max_length: int = 50, seed: str = None) -> str:
        """Generiert Text basierend auf trainierten Mustern"""
        if not self._trained:
            return ""

        # Wähle Startzustand
        if seed:
            seed_tokens = self._tokenize(seed)
            if len(seed_tokens) >= self.order:
                state = tuple(seed_tokens[-self.order:])
            else:
                state = random.choice(self.start_tokens) if self.start_tokens else None
        else:
            state = random.choice(self.start_tokens) if self.start_tokens else None

        if state is None:
            return ""

        result = list(state)

        for _ in range(max_length - self.order):
            if state not in self.chains:
                break

            # Gewichtete Auswahl des nächsten Tokens
            choices = self.chains[state]
            total = sum(choices.values())
            r = random.uniform(0, total)
            cumulative = 0
            next_token = None

            for token, count in choices.items():
                cumulative += count
                if cumulative >= r:
                    next_token = token
                    break

            if next_token is None:
                break

            result.append(next_token)
            state = tuple(result[-self.order:])

            # Stoppe bei Satzende
            if next_token in '.!?':
                break

        return self._detokenize(result)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiert Text"""
        # Einfache Tokenisierung mit Satzzeichen als separate Tokens
        tokens = []
        current_word = []

        for char in text:
            if char.isalnum() or char == '-':
                current_word.append(char)
            else:
                if current_word:
                    tokens.append(''.join(current_word).lower())
                    current_word = []
                if char in '.!?,;:':
                    tokens.append(char)
                elif char.isspace() and tokens and tokens[-1] != ' ':
                    pass  # Ignoriere Whitespace

        if current_word:
            tokens.append(''.join(current_word).lower())

        return tokens

    def _detokenize(self, tokens: List[str]) -> str:
        """Konvertiert Tokens zurück zu Text"""
        result = []
        capitalize_next = True

        for token in tokens:
            if token in '.!?':
                if result:
                    result[-1] = result[-1] + token
                capitalize_next = True
            elif token in ',;:':
                if result:
                    result[-1] = result[-1] + token
            else:
                if capitalize_next:
                    token = token.capitalize()
                    capitalize_next = False
                result.append(token)

        return ' '.join(result)


class HumorDetector:
    """
    Erkennt humoristische Elemente in Texten.
    Identifiziert Witze, Wortspiele, Ironie und Sarkasmus.
    """

    def __init__(self):
        self._init_humor_patterns()

    def _init_humor_patterns(self):
        """Initialisiert Humor-Erkennungsmuster"""
        self.patterns = {
            "wortspiel": [
                r"\b(\w+)\s+\1\b",  # Wiederholungen
                r"(?:heißt|nennt|bedeutet).*?(?:weil|da)\s",  # Wortspiel-Erklärungen
            ],
            "uebertreibung": [
                r"(millionen|milliarden|unendlich|ewig)\s+\w+",
                r"immer\s+\w+\s+immer",
                r"größte|kleinste|beste|schlechteste\s+\w+\s+aller\s+zeiten",
            ],
            "kontrast": [
                r"aber\s+(?:eigentlich|in\s+wirklichkeit)",
                r"dachte.*?(?:stellt\s+sich\s+heraus|war\s+aber)",
            ],
            "selbstironie": [
                r"ich\s+(?:dummkopf|idiot|trottel|depp)",
                r"wieder\s+mal\s+(?:ich|mein)",
                r"typisch\s+ich",
            ],
            "absurdität": [
                r"warum\s+(?:liegt|steht|sitzt).*?\?",
                r"was\s+macht\s+ein\w*\s+(?:wenn|auf|in)",
            ],
        }

        self._compiled_patterns = {
            key: [re.compile(p, re.IGNORECASE) for p in patterns]
            for key, patterns in self.patterns.items()
        }

        # Humor-Signalwörter
        self.humor_signals = {
            "einleitung": ["kennst du den", "witz", "weißt du was", "stell dir vor", "spaß"],
            "reaktion": ["haha", "hihi", "lol", "rofl", "xd", "😂", "🤣", "😄"],
            "ironie_marker": ["natürlich", "klar doch", "oh ja", "super", "toll"],
        }

    def analyze_humor(self, text: str) -> Dict[str, Any]:
        """
        Analysiert Text auf humoristische Elemente.

        Returns:
            Dict mit humor_detected, types, confidence, signals
        """
        text_lower = text.lower()

        detected_types = []
        signals_found = []

        # Prüfe Muster
        for humor_type, compiled_list in self._compiled_patterns.items():
            for pattern in compiled_list:
                if pattern.search(text):
                    detected_types.append(humor_type)
                    break

        # Prüfe Signalwörter
        for signal_type, signals in self.humor_signals.items():
            for signal in signals:
                if signal in text_lower:
                    signals_found.append((signal_type, signal))

        # Berechne Konfidenz
        confidence = 0.0
        if detected_types:
            confidence += 0.3 * len(detected_types)
        if signals_found:
            confidence += 0.2 * len(signals_found)

        # Zusätzliche Heuristiken
        if text.count('!') > 2:
            confidence += 0.1
        if text.count('?') > 1 and any(s[0] == "einleitung" for s in signals_found):
            confidence += 0.15

        return {
            "humor_detected": confidence > 0.3,
            "types": list(set(detected_types)),
            "signals": signals_found,
            "confidence": min(confidence, 1.0),
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_nlp() -> HoloNLP:
    """Factory für NLP"""
    return HoloNLP()


def create_nlp_v2() -> HoloNLPV2:
    """Factory für NLP V2"""
    return HoloNLPV2()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔬 HOLO NLP ALGORITHMS v4.0 - TEST")
    print("=" * 70)

    nlp = HoloNLPV2()

    # Test Fuzzy Matching
    print("\n📏 FUZZY MATCHING:")
    test_words = [("nass", "nas"), ("kii", "ki"), ("tempertur", "temperatur")]
    for typo, correct in test_words:
        comb = nlp.fuzzy.combined_similarity(typo, correct)
        print(f"   {typo} ↔ {correct}: {comb:.2f}")

    # Test Sentiment
    print("\n💭 SENTIMENT:")
    test_sentiment = ["Das ist super toll!", "Mir geht es schlecht...", "Ja klar..."]
    for text in test_sentiment:
        result = nlp.sentiment.analyze(text)
        print(f"   '{text}' → {result.sentiment} ({result.score:.2f})")

    # Test Analysis
    print("\n🔍 FULL ANALYSIS:")
    test_text = "Kannst du bitte das Licht in der Küche anmachen?"
    result = nlp.analyze(test_text)
    print(f"   Text: '{test_text}'")
    print(f"   Dialogue Act: {result['dialogue_act']}")
    print(f"   Entities: {result['entities']}")
    print(f"   Main Verb: {result['main_verb']}")

    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
