#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NLP UNIFIED v1.0 - Zentrales NLP-Modul                                 ║
║                                                                              ║
║  MERGT FUNKTIONALITÄT AUS:                                                   ║
║  • holo_nlp_algorithms.py  → TF-IDF, Fuzzy Matching, Sentiment               ║
║  • holo_nlp_enhanced.py    → Lightweight NLP, NER, Coreference               ║
║  • holo_nlp_advanced.py    → Topic Modeling, QA, Relations                   ║
║                                                                              ║
║  VERWENDUNG:                                                                 ║
║      from holo_nlp_unified import HoloNLP                                    ║
║      nlp = HoloNLP()                                                         ║
║      result = nlp.analyze("Dein Text hier")                                  ║
║                                                                              ║
║  Optimiert für Raspberry Pi - Keine schweren Bibliotheken!                   ║
║                                                                              ║
║  Version: 1.0 (Unified)                                                      ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import random
import logging
import time
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum

# Import zentrale Typen
try:
    from holo_core_types import (
        Sentiment, extract_keywords, simple_tokenize, calculate_similarity,
        STOPWORDS, STOPWORDS_DE, STOPWORDS_EN
    )
except ImportError:
    # Fallback wenn holo_core_types nicht verfügbar
    class Sentiment(Enum):
        VERY_POSITIVE = "very_positive"
        POSITIVE = "positive"
        NEUTRAL = "neutral"
        NEGATIVE = "negative"
        VERY_NEGATIVE = "very_negative"

    STOPWORDS_DE = {"der", "die", "das", "ein", "eine", "und", "oder", "ist", "sind"}
    STOPWORDS_EN = {"the", "a", "an", "is", "are", "was", "were", "be", "been"}
    STOPWORDS = STOPWORDS_DE | STOPWORDS_EN

    def extract_keywords(text: str, n: int = 10, min_length: int = 3) -> List[str]:
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text.lower())
        filtered = [w for w in words if w not in STOPWORDS and len(w) >= min_length]
        counts = Counter(filtered)
        return [word for word, _ in counts.most_common(n)]

    def simple_tokenize(text: str) -> List[str]:
        return re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text.lower())

    def calculate_similarity(text1: str, text2: str) -> float:
        words1 = set(simple_tokenize(text1)) - STOPWORDS
        words2 = set(simple_tokenize(text2)) - STOPWORDS
        if not words1 or not words2:
            return 0.0
        return len(words1 & words2) / len(words1 | words2)

logger = logging.getLogger("HoloNLPUnified")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Main Class
    "HoloNLP",

    # Fuzzy Matching
    "FuzzyMatcher",

    # Sentiment Analysis
    "SentimentAnalyzer",
    "SentimentResult",

    # Entity Extraction
    "EntityExtractor",
    "Entity",

    # TF-IDF & Vectors
    "TFIDFVectorizer",

    # Topic Modeling
    "TopicModeler",
    "Topic",

    # Relation Extraction
    "RelationExtractor",
    "Relation",

    # Question Answering
    "QuestionAnswerer",
    "QAResult",

    # Text Generation
    "TextGenerator",

    # Dialogue Acts
    "DialogueActClassifier",

    # Helpers (re-exported from core_types)
    "extract_keywords",
    "simple_tokenize",
    "calculate_similarity",
    "STOPWORDS",
]


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Entity:
    """Eine erkannte Entität"""
    text: str
    entity_type: str  # "PERSON", "LOCATION", "ORG", "DATE", "NUMBER"
    confidence: float = 0.8
    start: int = 0
    end: int = 0


@dataclass
class SentimentResult:
    """Ergebnis einer Sentiment-Analyse"""
    sentiment: Sentiment
    score: float  # -1 bis 1
    confidence: float
    positive_words: List[str] = field(default_factory=list)
    negative_words: List[str] = field(default_factory=list)


@dataclass
class Topic:
    """Ein erkanntes Thema"""
    topic_id: int
    name: str
    keywords: List[Tuple[str, float]]
    coherence: float = 0.0


@dataclass
class Relation:
    """Eine extrahierte Relation"""
    subject: str
    predicate: str
    object: str
    confidence: float
    relation_type: str


@dataclass
class QAResult:
    """Ergebnis einer Question-Answering Anfrage"""
    question: str
    answer: str
    confidence: float
    source_sentence: str
    answer_type: str


# =============================================================================
# 1. FUZZY MATCHING
# =============================================================================

class FuzzyMatcher:
    """
    Fortgeschrittenes Fuzzy Matching für Typos und ähnliche Wörter.

    Algorithmen:
    - Jaro-Winkler (für Namen)
    - Damerau-Levenshtein (für Typos)
    - Soundex/Kölner Phonetik (für Aussprache)
    """

    @staticmethod
    def jaro_winkler(s1: str, s2: str, winkler_prefix: float = 0.1) -> float:
        """Jaro-Winkler Similarity - gut für Namen"""
        s1, s2 = s1.lower(), s2.lower()

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

        # Winkler prefix boost
        prefix_len = 0
        for i in range(min(4, len1, len2)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        return jaro + prefix_len * winkler_prefix * (1 - jaro)

    @staticmethod
    def damerau_levenshtein(s1: str, s2: str) -> int:
        """Damerau-Levenshtein Distanz - gut für Typos"""
        s1, s2 = s1.lower(), s2.lower()
        len1, len2 = len(s1), len(s2)

        if len1 == 0:
            return len2
        if len2 == 0:
            return len1

        # Distanz-Matrix
        d = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            d[i][0] = i
        for j in range(len2 + 1):
            d[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1

                d[i][j] = min(
                    d[i - 1][j] + 1,      # Deletion
                    d[i][j - 1] + 1,      # Insertion
                    d[i - 1][j - 1] + cost  # Substitution
                )

                # Transposition
                if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                    d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)

        return d[len1][len2]

    @staticmethod
    def cologne_phonetic(word: str) -> str:
        """Kölner Phonetik - deutsch optimiert"""
        word = word.upper()

        # Ersetzungen
        replacements = [
            (r'[AEIJOUY]', '0'),
            (r'[BP]', '1'),
            (r'[DT](?![CSZ])', '2'),
            (r'[FVW]', '3'),
            (r'[GKQ]', '4'),
            (r'L', '5'),
            (r'[MN]', '6'),
            (r'R', '7'),
            (r'[CSZ]', '8'),
            (r'X', '48'),
        ]

        result = word
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)

        # Duplikate entfernen
        result = re.sub(r'(\d)\1+', r'\1', result)

        # Führende Nullen entfernen
        result = result.lstrip('0')

        return result

    def match(self, query: str, candidates: List[str],
              threshold: float = 0.7, method: str = "jaro_winkler") -> List[Tuple[str, float]]:
        """
        Finde ähnliche Kandidaten für einen Query.

        Args:
            query: Suchbegriff
            candidates: Liste möglicher Treffer
            threshold: Minimale Ähnlichkeit (0-1)
            method: "jaro_winkler", "levenshtein", oder "phonetic"

        Returns:
            Liste von (kandidat, score) sortiert nach Ähnlichkeit
        """
        results = []

        for candidate in candidates:
            if method == "jaro_winkler":
                score = self.jaro_winkler(query, candidate)
            elif method == "levenshtein":
                max_len = max(len(query), len(candidate))
                dist = self.damerau_levenshtein(query, candidate)
                score = 1 - (dist / max_len) if max_len > 0 else 1.0
            elif method == "phonetic":
                p1 = self.cologne_phonetic(query)
                p2 = self.cologne_phonetic(candidate)
                score = 1.0 if p1 == p2 else 0.0
            else:
                score = 0.0

            if score >= threshold:
                results.append((candidate, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results


# =============================================================================
# 2. SENTIMENT ANALYSIS
# =============================================================================

class SentimentAnalyzer:
    """
    Sentiment-Analyse für deutsche und englische Texte.

    Features:
    - Lexikon-basiert
    - Negation-Handling
    - Intensifier-Support
    """

    def __init__(self):
        self._init_lexicons()

    def _init_lexicons(self):
        """Initialisiert Sentiment-Lexika"""
        self.positive_words = {
            # Deutsch
            "gut", "super", "toll", "ausgezeichnet", "fantastisch", "wunderbar",
            "großartig", "perfekt", "hervorragend", "genial", "klasse", "prima",
            "freude", "glücklich", "liebe", "schön", "positiv", "freundlich",
            "nett", "hilfreich", "interessant", "spannend", "lustig", "cool",
            # English
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "awesome", "perfect", "brilliant", "love", "happy", "nice", "helpful",
        }

        self.negative_words = {
            # Deutsch
            "schlecht", "schrecklich", "furchtbar", "miserabel", "grauenhaft",
            "katastrophal", "traurig", "wütend", "ärgerlich", "enttäuscht",
            "langweilig", "nervig", "blöd", "dumm", "hass", "negativ", "böse",
            # English
            "bad", "terrible", "awful", "horrible", "worst", "hate", "angry",
            "sad", "disappointed", "boring", "annoying", "stupid",
        }

        self.negations = {
            "nicht", "kein", "keine", "keinen", "keiner", "nie", "niemals",
            "kaum", "without", "not", "no", "never", "neither",
        }

        self.intensifiers = {
            "sehr": 1.5, "extrem": 2.0, "total": 1.8, "absolut": 1.8,
            "wirklich": 1.3, "echt": 1.3, "ziemlich": 1.2, "unglaublich": 1.8,
            "very": 1.5, "extremely": 2.0, "totally": 1.8, "really": 1.3,
        }

    def analyze(self, text: str) -> SentimentResult:
        """Analysiert das Sentiment eines Textes"""
        words = simple_tokenize(text)

        score = 0.0
        positive_found = []
        negative_found = []
        negation_active = False
        intensifier = 1.0

        for i, word in enumerate(words):
            # Check for negation
            if word in self.negations:
                negation_active = True
                continue

            # Check for intensifier
            if word in self.intensifiers:
                intensifier = self.intensifiers[word]
                continue

            # Check sentiment
            word_score = 0.0
            if word in self.positive_words:
                word_score = 1.0 * intensifier
                positive_found.append(word)
            elif word in self.negative_words:
                word_score = -1.0 * intensifier
                negative_found.append(word)

            # Apply negation
            if negation_active:
                word_score *= -0.8
                negation_active = False

            score += word_score
            intensifier = 1.0

        # Normalisieren
        word_count = len(words)
        if word_count > 0:
            normalized_score = score / math.sqrt(word_count)
            normalized_score = max(-1, min(1, normalized_score))
        else:
            normalized_score = 0.0

        # Sentiment bestimmen
        sentiment = Sentiment.from_score(normalized_score) if hasattr(Sentiment, 'from_score') else (
            Sentiment.VERY_POSITIVE if normalized_score >= 0.5 else
            Sentiment.POSITIVE if normalized_score >= 0.2 else
            Sentiment.NEUTRAL if normalized_score >= -0.2 else
            Sentiment.NEGATIVE if normalized_score >= -0.5 else
            Sentiment.VERY_NEGATIVE
        )

        # Confidence basierend auf Evidenz
        evidence_count = len(positive_found) + len(negative_found)
        confidence = min(0.95, 0.5 + evidence_count * 0.1)

        return SentimentResult(
            sentiment=sentiment,
            score=normalized_score,
            confidence=confidence,
            positive_words=positive_found,
            negative_words=negative_found
        )


# =============================================================================
# 3. ENTITY EXTRACTION
# =============================================================================

class EntityExtractor:
    """
    Named Entity Recognition ohne externe Bibliotheken.

    Erkennt:
    - Personen (Namen)
    - Orte
    - Organisationen
    - Daten
    - Zahlen
    """

    def __init__(self):
        self._init_gazetteers()
        self._init_patterns()

    def _init_gazetteers(self):
        """Initialisiert bekannte Entitäten"""
        self.known_locations = {
            "berlin", "münchen", "hamburg", "köln", "frankfurt", "stuttgart",
            "düsseldorf", "leipzig", "dortmund", "essen", "bremen", "dresden",
            "deutschland", "österreich", "schweiz", "europa", "usa", "china",
            "london", "paris", "new york", "tokyo", "los angeles",
        }

        self.known_orgs = {
            "google", "apple", "microsoft", "amazon", "facebook", "meta",
            "tesla", "bmw", "mercedes", "volkswagen", "audi", "siemens",
            "sap", "bosch", "lidl", "aldi", "dhl", "lufthansa",
        }

        # Häufige deutsche Vornamen
        self.common_names = {
            "anna", "maria", "emma", "sophie", "lena", "laura", "julia",
            "max", "paul", "leon", "felix", "lukas", "jonas", "tim",
            "michael", "thomas", "andreas", "stefan", "peter", "hans",
        }

    def _init_patterns(self):
        """Initialisiert Regex-Patterns"""
        self.patterns = {
            "DATE": [
                r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',  # 01.01.2024
                r'\b\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4}\b',
                r'\b(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4}\b',
            ],
            "NUMBER": [
                r'\b\d+(?:[.,]\d+)?\s*(?:Euro|€|Dollar|\$|Prozent|%|Millionen|Milliarden)?\b',
            ],
            "EMAIL": [
                r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b',
            ],
            "URL": [
                r'\bhttps?://\S+\b',
            ],
        }

    def extract(self, text: str) -> List[Entity]:
        """Extrahiert alle Entitäten aus dem Text"""
        entities = []

        # Pattern-basierte Extraktion
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entities.append(Entity(
                        text=match.group(),
                        entity_type=entity_type,
                        confidence=0.9,
                        start=match.start(),
                        end=match.end()
                    ))

        # Gazetteer-basierte Extraktion
        words = text.split()
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?')

            if word_lower in self.known_locations:
                entities.append(Entity(
                    text=word,
                    entity_type="LOCATION",
                    confidence=0.85
                ))
            elif word_lower in self.known_orgs:
                entities.append(Entity(
                    text=word,
                    entity_type="ORG",
                    confidence=0.85
                ))

        # Heuristik für Personennamen (Großbuchstaben am Satzanfang ignorieren)
        name_pattern = r'\b([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)\b'
        for match in re.finditer(name_pattern, text):
            first, last = match.group(1), match.group(2)
            if first.lower() in self.common_names or last.lower() in self.common_names:
                entities.append(Entity(
                    text=match.group(),
                    entity_type="PERSON",
                    confidence=0.75,
                    start=match.start(),
                    end=match.end()
                ))

        return entities


# =============================================================================
# 4. TF-IDF VECTORIZER
# =============================================================================

class TFIDFVectorizer:
    """
    Leichtgewichtige TF-IDF Implementierung.

    Kein numpy/scipy nötig!
    """

    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.document_count = 0

    def fit(self, documents: List[str]):
        """Trainiert den Vectorizer auf Dokumenten"""
        doc_freq = Counter()

        for doc in documents:
            tokens = set(simple_tokenize(doc))
            tokens = tokens - STOPWORDS

            for token in tokens:
                if token not in self.vocabulary:
                    self.vocabulary[token] = len(self.vocabulary)
                doc_freq[token] += 1

            self.document_count += 1

        # IDF berechnen
        for token, freq in doc_freq.items():
            self.idf[token] = math.log((self.document_count + 1) / (freq + 1)) + 1

    def transform(self, text: str) -> Dict[str, float]:
        """Transformiert Text zu TF-IDF Vektor (als dict)"""
        tokens = simple_tokenize(text)
        tokens = [t for t in tokens if t not in STOPWORDS]

        tf = Counter(tokens)
        total = len(tokens) if tokens else 1

        vector = {}
        for token, count in tf.items():
            if token in self.vocabulary:
                tf_score = count / total
                idf_score = self.idf.get(token, 1.0)
                vector[token] = tf_score * idf_score

        return vector

    def similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Berechnet Cosine Similarity zwischen zwei Vektoren"""
        common_keys = set(vec1.keys()) & set(vec2.keys())

        if not common_keys:
            return 0.0

        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


# =============================================================================
# 5. TOPIC MODELING
# =============================================================================

class TopicModeler:
    """
    Einfaches Topic Modeling ohne sklearn.

    Verwendet TF-IDF und Co-occurrence für Topic-Extraktion.
    """

    def __init__(self, n_topics: int = 5):
        self.n_topics = n_topics
        self.topics: List[Topic] = []
        self.vectorizer = TFIDFVectorizer()

    def fit(self, documents: List[str]) -> List[Topic]:
        """Extrahiert Topics aus Dokumenten"""
        if not documents:
            return []

        self.vectorizer.fit(documents)

        # Sammle alle Keywords mit Gewichten
        all_keywords = defaultdict(float)
        for doc in documents:
            vec = self.vectorizer.transform(doc)
            for word, weight in vec.items():
                all_keywords[word] += weight

        # Sortiere nach Gewicht
        sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)

        # Teile in Topics auf
        keywords_per_topic = max(5, len(sorted_keywords) // self.n_topics)
        self.topics = []

        for i in range(self.n_topics):
            start = i * keywords_per_topic
            end = start + keywords_per_topic
            topic_keywords = sorted_keywords[start:end]

            if topic_keywords:
                self.topics.append(Topic(
                    topic_id=i,
                    name=topic_keywords[0][0] if topic_keywords else f"topic_{i}",
                    keywords=topic_keywords[:10],
                    coherence=self._compute_coherence(topic_keywords, documents)
                ))

        return self.topics

    def _compute_coherence(self, keywords: List[Tuple[str, float]],
                           documents: List[str]) -> float:
        """Berechnet Topic Coherence"""
        words = [w for w, _ in keywords[:5]]
        if len(words) < 2:
            return 0.0

        coherence = 0.0
        pairs = 0

        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                w1, w2 = words[i], words[j]
                count_both = sum(1 for doc in documents
                                 if w1 in doc.lower() and w2 in doc.lower())
                count_w1 = sum(1 for doc in documents if w1 in doc.lower())

                if count_w1 > 0:
                    coherence += math.log((count_both + 1) / (count_w1 + 1))
                    pairs += 1

        return coherence / pairs if pairs > 0 else 0.0

    def get_document_topics(self, text: str) -> List[Tuple[int, float]]:
        """Gibt Topics für ein Dokument zurück"""
        text_lower = text.lower()
        scores = []

        for topic in self.topics:
            score = sum(weight for word, weight in topic.keywords
                        if word in text_lower)
            scores.append((topic.topic_id, score))

        total = sum(s for _, s in scores)
        if total > 0:
            scores = [(tid, s / total) for tid, s in scores]

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


# =============================================================================
# 6. RELATION EXTRACTION
# =============================================================================

class RelationExtractor:
    """
    Extrahiert Relationen (Subject-Predicate-Object) aus Text.
    """

    def __init__(self):
        self._init_patterns()

    def _init_patterns(self):
        """Initialisiert Extraktions-Patterns"""
        self.patterns = [
            # "X ist Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+ist\s+(?:ein[e]?\s+)?([A-Za-zäöüß]+)',
             "is_a"),
            # "X arbeitet bei Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+arbeitet\s+(?:bei|für)\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "works_for"),
            # "X lebt in Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+(?:lebt|wohnt)\s+in\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "lives_in"),
            # "X hat Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+hat\s+(?:ein[e]?\s+)?([A-Za-zäöüß]+)',
             "has"),
        ]

        self.predicate_map = {
            "is_a": "ist",
            "works_for": "arbeitet für",
            "lives_in": "lebt in",
            "has": "hat",
        }

    def extract(self, text: str) -> List[Relation]:
        """Extrahiert alle Relationen aus dem Text"""
        relations = []
        sentences = re.split(r'[.!?]+', text)

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            for pattern, rel_type in self.patterns:
                for match in re.finditer(pattern, sent, re.IGNORECASE):
                    try:
                        subject = match.group(1).strip()
                        obj = match.group(2).strip()

                        if len(subject) > 1 and len(obj) > 1:
                            relations.append(Relation(
                                subject=subject,
                                predicate=self.predicate_map.get(rel_type, rel_type),
                                object=obj,
                                confidence=0.8,
                                relation_type=rel_type
                            ))
                    except IndexError:
                        continue

        return relations


# =============================================================================
# 7. QUESTION ANSWERING
# =============================================================================

class QuestionAnswerer:
    """
    Extraktives Question Answering.
    """

    def __init__(self):
        self.question_types = {
            "wer": "PERSON",
            "was": "THING",
            "wo": "LOCATION",
            "wann": "DATE",
            "wie viel": "NUMBER",
            "warum": "REASON",
        }

    def answer(self, question: str, context: str) -> QAResult:
        """Beantwortet eine Frage basierend auf Kontext"""
        question_lower = question.lower()

        # Bestimme Frage-Typ
        answer_type = "DESCRIPTION"
        for q_word, a_type in self.question_types.items():
            if question_lower.startswith(q_word):
                answer_type = a_type
                break

        # Extrahiere Keywords aus Frage
        q_keywords = set(extract_keywords(question))

        # Finde relevante Sätze
        sentences = re.split(r'[.!?]+', context)
        scored_sentences = []

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            sent_keywords = set(extract_keywords(sent))
            overlap = len(q_keywords & sent_keywords)

            if overlap > 0:
                scored_sentences.append((sent, overlap))

        if not scored_sentences:
            return QAResult(
                question=question,
                answer="Keine Antwort gefunden.",
                confidence=0.0,
                source_sentence="",
                answer_type=answer_type
            )

        # Beste Sentence
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        best_sentence, score = scored_sentences[0]

        # Extrahiere Antwort
        answer = self._extract_answer(best_sentence, answer_type)

        return QAResult(
            question=question,
            answer=answer,
            confidence=min(score / 5, 1.0),
            source_sentence=best_sentence,
            answer_type=answer_type
        )

    def _extract_answer(self, sentence: str, answer_type: str) -> str:
        """Extrahiert die Antwort aus dem Satz"""
        if answer_type == "PERSON":
            names = re.findall(r'[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+', sentence)
            if names:
                return names[0]
        elif answer_type == "DATE":
            dates = re.findall(r'\d{1,2}\.\s*\w+\s*\d{4}|\d{4}', sentence)
            if dates:
                return dates[0]
        elif answer_type == "NUMBER":
            numbers = re.findall(r'\d+(?:[.,]\d+)?', sentence)
            if numbers:
                return numbers[0]
        elif answer_type == "LOCATION":
            loc_match = re.search(r'(?:in|aus|bei|nach)\s+([A-ZÄÖÜ][a-zäöüß]+)', sentence)
            if loc_match:
                return loc_match.group(1)

        return sentence[:150] + "..." if len(sentence) > 150 else sentence


# =============================================================================
# 8. TEXT GENERATION
# =============================================================================

class TextGenerator:
    """
    Einfache Textgenerierung mit Markov Chains und Templates.
    """

    def __init__(self, order: int = 2):
        self.order = order
        self.transitions: Dict[Tuple, Counter] = defaultdict(Counter)
        self.starters: List[Tuple] = []

    def train(self, texts: List[str]):
        """Trainiert den Generator auf Texten"""
        for text in texts:
            words = text.split()

            if len(words) <= self.order:
                continue

            self.starters.append(tuple(words[:self.order]))

            for i in range(len(words) - self.order):
                state = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                self.transitions[state][next_word] += 1

    def generate(self, length: int = 50) -> str:
        """Generiert Text mit Markov Chain"""
        if not self.starters:
            return ""

        current = random.choice(self.starters)
        result = list(current)

        for _ in range(length - self.order):
            if current not in self.transitions:
                break

            choices = self.transitions[current]
            total = sum(choices.values())
            r = random.uniform(0, total)

            cumsum = 0
            next_word = None
            for word, count in choices.items():
                cumsum += count
                if cumsum >= r:
                    next_word = word
                    break

            if next_word is None:
                break

            result.append(next_word)
            current = tuple(result[-self.order:])

        return " ".join(result)


# =============================================================================
# 9. DIALOGUE ACT CLASSIFIER
# =============================================================================

class DialogueActClassifier:
    """
    Klassifiziert Dialogue Acts (Sprechakte).
    """

    def __init__(self):
        self._init_patterns()

    def _init_patterns(self):
        """Initialisiert Dialogue Act Patterns"""
        self.patterns = {
            "GREETING": [r'\b(hallo|hi|hey|moin|guten\s+(?:morgen|tag|abend))\b'],
            "FAREWELL": [r'\b(tschüss|bye|auf\s+wiedersehen|bis\s+(?:bald|dann|später))\b'],
            "QUESTION": [r'\?$', r'^(wer|was|wo|wann|wie|warum|wieso|weshalb)\b'],
            "CONFIRM": [r'^(ja|genau|richtig|korrekt|stimmt)\b'],
            "DENY": [r'^(nein|ne|falsch|stimmt\s+nicht)\b'],
            "THANKS": [r'\b(danke|vielen\s+dank|dankeschön)\b'],
            "REQUEST": [r'\b(kannst|könntest|würdest|bitte)\b'],
            "INFORM": [r'\b(ich\s+(?:bin|habe|war|werde))\b'],
        }

    def classify(self, text: str) -> Tuple[str, float]:
        """Klassifiziert den Dialogue Act"""
        text_lower = text.lower()

        for act, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return act, 0.8

        return "STATEMENT", 0.5


# =============================================================================
# MAIN CLASS - HoloNLP
# =============================================================================

class HoloNLP:
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  HoloNLP - Unified NLP Interface                              ║
    ║                                                               ║
    ║  Kombiniert alle NLP-Funktionen in einer Klasse:              ║
    ║  - Sentiment Analysis                                         ║
    ║  - Entity Extraction                                          ║
    ║  - Keyword Extraction                                         ║
    ║  - Topic Modeling                                             ║
    ║  - Relation Extraction                                        ║
    ║  - Question Answering                                         ║
    ║  - Fuzzy Matching                                             ║
    ║  - Dialogue Act Classification                                ║
    ╚═══════════════════════════════════════════════════════════════╝
    """

    def __init__(self):
        self.sentiment = SentimentAnalyzer()
        self.entities = EntityExtractor()
        self.fuzzy = FuzzyMatcher()
        self.vectorizer = TFIDFVectorizer()
        self.topics = TopicModeler()
        self.relations = RelationExtractor()
        self.qa = QuestionAnswerer()
        self.text_gen = TextGenerator()
        self.dialogue = DialogueActClassifier()

        logger.info("✅ HoloNLP Unified initialisiert")

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Führt vollständige NLP-Analyse durch.

        Returns:
            {
                "sentiment": SentimentResult,
                "entities": List[Entity],
                "keywords": List[str],
                "relations": List[Relation],
                "dialogue_act": (str, float),
            }
        """
        return {
            "sentiment": self.sentiment.analyze(text),
            "entities": self.entities.extract(text),
            "keywords": extract_keywords(text),
            "relations": self.relations.extract(text),
            "dialogue_act": self.dialogue.classify(text),
        }

    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Sentiment-Analyse"""
        return self.sentiment.analyze(text)

    def extract_entities(self, text: str) -> List[Entity]:
        """Entity Extraction"""
        return self.entities.extract(text)

    def get_keywords(self, text: str, n: int = 10) -> List[str]:
        """Keyword Extraction"""
        return extract_keywords(text, n)

    def extract_relations(self, text: str) -> List[Relation]:
        """Relation Extraction"""
        return self.relations.extract(text)

    def answer_question(self, question: str, context: str) -> QAResult:
        """Question Answering"""
        return self.qa.answer(question, context)

    def find_similar(self, query: str, candidates: List[str],
                     threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Fuzzy Matching"""
        return self.fuzzy.match(query, candidates, threshold)

    def train_topics(self, documents: List[str]) -> List[Topic]:
        """Topic Modeling"""
        return self.topics.fit(documents)

    def get_document_topics(self, text: str) -> List[Tuple[int, float]]:
        """Topics für ein Dokument"""
        return self.topics.get_document_topics(text)

    def classify_dialogue_act(self, text: str) -> Tuple[str, float]:
        """Dialogue Act Classification"""
        return self.dialogue.classify(text)

    def similarity(self, text1: str, text2: str) -> float:
        """Berechnet Textähnlichkeit"""
        return calculate_similarity(text1, text2)


# =============================================================================
# LEGACY COMPATIBILITY - Aliase für alte Imports
# =============================================================================

# Aliase für Kompatibilität mit holo_nlp_algorithms.py
HoloNLPV2 = HoloNLP
AdvancedFuzzyMatcher = FuzzyMatcher
AdvancedSentimentAnalyzer = SentimentAnalyzer
LightweightVectorEngine = TFIDFVectorizer

# Aliase für Kompatibilität mit holo_nlp_advanced.py
HoloNLPAdvanced = HoloNLP
SimpleTopicModel = TopicModeler
ExtractiveQA = QuestionAnswerer
SimpleTextGenerator = TextGenerator


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_nlp() -> HoloNLP:
    """Factory für HoloNLP"""
    return HoloNLP()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("🐺 HOLO NLP UNIFIED v1.0 - TEST")
    print("=" * 70)

    nlp = HoloNLP()

    test_text = """
    Angela Merkel wurde in Hamburg geboren und war von 2005 bis 2021
    Bundeskanzlerin von Deutschland. Sie arbeitet für die CDU.
    Das finde ich sehr interessant und toll!
    """

    print("\n📊 VOLLSTÄNDIGE ANALYSE:")
    result = nlp.analyze(test_text)

    print(f"\n  Sentiment: {result['sentiment'].sentiment.value}")
    print(f"  Score: {result['sentiment'].score:.2f}")
    print(f"  Confidence: {result['sentiment'].confidence:.2f}")

    print(f"\n  Entities ({len(result['entities'])}):")
    for ent in result['entities'][:5]:
        print(f"    - {ent.text} ({ent.entity_type})")

    print(f"\n  Keywords: {result['keywords'][:5]}")

    print(f"\n  Relations ({len(result['relations'])}):")
    for rel in result['relations'][:3]:
        print(f"    - {rel.subject} --[{rel.relation_type}]--> {rel.object}")

    print(f"\n  Dialogue Act: {result['dialogue_act']}")

    print("\n" + "=" * 70)
    print("✅ Test abgeschlossen!")
