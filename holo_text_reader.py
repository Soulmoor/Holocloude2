#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO TEXT READER v2.0 - Intelligente Text-Analyse für Holo                 ║
║                                                                              ║
║  VERBESSERUNGEN in v2.0:                                                     ║
║  • Englische + Deutsche Fact-Patterns                                        ║
║  • Fallback Entity Recognition (ohne NLP)                                    ║
║  • Bessere Summary-Generierung                                               ║
║  • Sentiment-Analyse integriert                                              ║
║  • Verbesserte Topic Detection mit Kategorien                                ║
║  • Mehr Fact-Types (Vergleiche, Trends, Ankündigungen)                       ║
║                                                                              ║
║  Optimiert für Raspberry Pi - kein LLM nötig für Basis-Funktionen!          ║
║                                                                              ║
║  Version: 2.0                                                                ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import Counter
from enum import Enum

logger = logging.getLogger("HoloTextReader")


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class FactType(Enum):
    """Typen von extrahierten Fakten"""
    STATISTIC = "statistic"
    DATE = "date"
    DEFINITION = "definition"
    QUOTE = "quote"
    RESEARCH = "research"
    COMPARISON = "comparison"
    ANNOUNCEMENT = "announcement"
    TREND = "trend"
    LOCATION = "location"
    UNKNOWN = "unknown"


class Sentiment(Enum):
    """Sentiment-Kategorien"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class TopicCategory(Enum):
    """Themen-Kategorien"""
    TECH = "tech"
    SCIENCE = "science"
    POLITICS = "politics"
    ECONOMY = "economy"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    GAMING = "gaming"
    HEALTH = "health"
    ENVIRONMENT = "environment"
    GENERAL = "general"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ExtractedFact:
    """Ein aus Text extrahierter Fakt"""
    content: str
    topic: str
    entities: List[str]
    related_topics: List[str]
    confidence: float
    source_sentence: str
    keywords: List[str]
    fact_type: FactType = FactType.UNKNOWN


@dataclass
class ExtractedEntity:
    """Eine erkannte Entität"""
    value: str
    entity_type: str
    confidence: float
    context: str = ""


@dataclass
class TextAnalysisResult:
    """Ergebnis einer Text-Analyse"""
    source: str
    title: str
    word_count: int
    sentence_count: int
    main_topics: List[str]
    topic_category: TopicCategory
    entities: List[ExtractedEntity]
    facts: List[ExtractedFact]
    keywords: List[str]
    summary: str
    key_sentences: List[str]
    sentiment: Sentiment
    sentiment_score: float
    reading_time_seconds: float
    needs_llm_for_deep_analysis: bool
    language: str = "de"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# =============================================================================
# KEYWORD EXTRACTOR
# =============================================================================

class KeywordExtractor:
    """TF-basierte Keyword-Extraktion, Pi-optimiert"""

    STOPWORDS_DE = {
        "der", "die", "das", "ein", "eine", "einer", "eines", "einem", "einen",
        "und", "oder", "aber", "doch", "jedoch", "sondern", "sowie",
        "ist", "sind", "war", "waren", "wird", "werden", "wurde", "wurden",
        "hat", "haben", "hatte", "hatten", "kann", "können", "konnte", "konnten",
        "muss", "müssen", "musste", "mussten", "soll", "sollen", "sollte", "sollten",
        "ich", "du", "er", "sie", "es", "wir", "ihr",
        "mich", "dich", "sich", "uns", "euch", "mir", "dir", "ihm",
        "mein", "dein", "sein", "unser", "euer",
        "in", "an", "auf", "aus", "bei", "mit", "nach", "über", "unter",
        "vor", "hinter", "neben", "zwischen", "durch", "für", "gegen", "ohne",
        "um", "von", "zu", "bis", "seit", "während", "wegen", "trotz",
        "dass", "ob", "wenn", "weil", "obwohl", "als", "wie", "wo", "was",
        "wer", "wann", "warum", "weshalb", "wieso", "welche", "welcher", "welches",
        "nicht", "auch", "noch", "schon", "nur", "sehr", "so", "dann", "denn",
        "hier", "dort", "da", "nun", "jetzt", "heute", "gestern", "morgen",
        "immer", "nie", "oft", "manchmal", "vielleicht", "etwa", "ungefähr",
        "mehr", "weniger", "viel", "wenig", "alle", "keine", "jede", "jeder",
        "diese", "dieser", "dieses", "jene", "jener", "jenes",
    }

    STOPWORDS_EN = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "between", "under", "again", "further", "then", "once",
        "and", "but", "or", "nor", "so", "yet", "both", "either", "neither",
        "not", "only", "own", "same", "than", "too", "very",
        "this", "that", "these", "those", "i", "me", "my", "myself",
        "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
        "he", "him", "his", "himself", "she", "her", "hers", "herself",
        "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom", "when", "where", "why", "how",
        "all", "each", "every", "any", "some", "no", "most", "other",
        "such", "just", "also", "now", "here", "there", "about", "over",
    }

    def __init__(self):
        self.stopwords = self.STOPWORDS_DE | self.STOPWORDS_EN

    def extract(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """Extrahiert Keywords mit Scores"""
        tokens = self._tokenize(text)
        if not tokens:
            return []

        tf = Counter(tokens)
        total = len(tokens)

        scores = {}
        for word, count in tf.items():
            if word in self.stopwords or len(word) < 3:
                continue
            tf_score = count / total
            length_bonus = min(len(word) / 10, 1.0)
            caps_bonus = 0.2 if word[0].isupper() else 0
            scores[word] = tf_score * (1 + length_bonus + caps_bonus)

        sorted_keywords = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text.lower())
        return words


# =============================================================================
# ENTITY EXTRACTOR (ohne NLP!)
# =============================================================================

class EntityExtractor:
    """Pattern-basierte Entity-Extraktion, Pi-optimiert"""

    PATTERNS = {
        "PERSON": [
            r'\b([A-ZÄÖÜ][a-zäöüß]+)\s+([A-ZÄÖÜ][a-zäöüß]+)(?:\s+(?:sagte|erklärte|meinte|betonte))',
            r'(?:CEO|Chef|Direktor|Minister|Präsident|Dr\.|Prof\.)\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)',
        ],
        "ORG": [
            r'\b((?:[A-ZÄÖÜ][a-zäöüß]*\s*){1,3}(?:GmbH|AG|Inc|Corp|Ltd|SE|KG))\b',
            r'\b(Google|Apple|Microsoft|Amazon|Meta|Facebook|Twitter|Tesla|OpenAI|Anthropic|Netflix|Nvidia|Intel|AMD|Samsung|Sony|Nintendo)\b',
            r'\b(CDU|SPD|Grüne|FDP|AfD|Linke|CSU|EU|NATO|UN|WHO|FIFA|UEFA)\b',
        ],
        "LOCATION": [
            r'\b(Berlin|München|Hamburg|Frankfurt|Köln|Stuttgart|Düsseldorf|Wien|Zürich|Bern)\b',
            r'\b(Deutschland|Österreich|Schweiz|USA|China|Japan|Russland|Frankreich|England|Italien|Spanien)\b',
            r'\b(New York|London|Paris|Tokyo|Beijing|Shanghai|Los Angeles|San Francisco|Silicon Valley)\b',
        ],
        "PRODUCT": [
            r'\b(iPhone|iPad|MacBook|Android|Windows|Linux|ChatGPT|GPT-\d|Claude|Gemini)\b',
            r'\b(PlayStation|Xbox|Switch|Steam|Unity|Unreal)\b',
        ],
        "MONEY": [
            r'(\d+(?:[.,]\d+)?\s*(?:Euro|EUR|€|Dollar|USD|\$|Millionen|Milliarden|Mio|Mrd))',
            r'(\d+(?:[.,]\d+)?\s*(?:million|billion|trillion)\s*(?:dollars?|euros?))',
        ],
        "DATE": [
            r'\b(\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4})\b',
            r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
        ],
    }

    def __init__(self):
        self.compiled_patterns = {}
        for entity_type, patterns in self.PATTERNS.items():
            self.compiled_patterns[entity_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def extract(self, text: str) -> List[ExtractedEntity]:
        """Extrahiert Entities aus Text"""
        entities = []
        seen = set()

        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    value = None
                    for group in match.groups():
                        if group:
                            value = group.strip()
                            break

                    if not value or len(value) < 2:
                        continue

                    value_lower = value.lower()
                    if value_lower in seen:
                        continue
                    seen.add(value_lower)

                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]

                    confidence = 0.7
                    if entity_type == "MONEY":
                        confidence = 0.9
                    elif entity_type == "ORG":
                        confidence = 0.85

                    entities.append(ExtractedEntity(
                        value=value,
                        entity_type=entity_type,
                        confidence=confidence,
                        context=context
                    ))

        return entities


# =============================================================================
# SENTIMENT ANALYZER
# =============================================================================

class SentimentAnalyzer:
    """Lexikon-basierte Sentiment-Analyse, Pi-optimiert"""

    POSITIVE_WORDS = {
        "gut", "super", "toll", "großartig", "ausgezeichnet", "fantastisch",
        "wunderbar", "hervorragend", "positiv", "erfolgreich", "gewinn",
        "freude", "glück", "liebe", "schön", "besser", "beste", "neu",
        "innovativ", "fortschritt", "wachstum", "steigt", "gewinnt",
        "durchbruch", "revolution", "zukunft", "hoffnung", "optimistisch",
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "awesome", "brilliant", "success", "win", "winner", "positive",
        "growth", "breakthrough", "innovation", "revolutionary", "future",
        "hope", "happy", "love", "best", "better", "improve", "improved",
    }

    NEGATIVE_WORDS = {
        "schlecht", "schrecklich", "furchtbar", "negativ", "verlust",
        "problem", "krise", "gefahr", "risiko", "warnung", "fehler",
        "absturz", "einbruch", "rückgang", "sinkt", "fällt", "verliert",
        "skandal", "kritik", "streit", "konflikt", "krieg", "tod",
        "angst", "sorge", "bedrohung", "schaden", "katastrophe",
        "bad", "terrible", "horrible", "awful", "negative", "loss",
        "problem", "crisis", "danger", "risk", "warning", "error",
        "crash", "decline", "fall", "drop", "scandal", "criticism",
        "conflict", "war", "death", "fear", "threat", "damage",
        "disaster", "fail", "failure", "worst", "worse",
    }

    INTENSIFIERS = {
        "sehr", "extrem", "absolut", "total", "komplett", "völlig",
        "unglaublich", "wahnsinnig", "enorm", "massiv",
        "very", "extremely", "absolutely", "totally", "completely",
        "incredibly", "highly", "deeply", "strongly",
    }

    NEGATIONS = {
        "nicht", "kein", "keine", "keiner", "nie", "niemals", "nichts",
        "not", "no", "never", "none", "neither", "nobody", "nothing",
    }

    def analyze(self, text: str) -> Tuple[Sentiment, float]:
        """Analysiert Sentiment, gibt (Sentiment, score) zurück"""
        words = text.lower().split()
        if not words:
            return Sentiment.NEUTRAL, 0.0

        pos_count = 0
        neg_count = 0
        negation_active = 0

        for i, word in enumerate(words):
            if word in self.NEGATIONS:
                negation_active = 3
                continue

            intensity = 1.5 if i > 0 and words[i-1] in self.INTENSIFIERS else 1.0

            if word in self.POSITIVE_WORDS:
                if negation_active > 0:
                    neg_count += intensity
                else:
                    pos_count += intensity
            elif word in self.NEGATIVE_WORDS:
                if negation_active > 0:
                    pos_count += intensity
                else:
                    neg_count += intensity

            if negation_active > 0:
                negation_active -= 1

        total = pos_count + neg_count
        if total == 0:
            return Sentiment.NEUTRAL, 0.0

        score = (pos_count - neg_count) / total

        if score >= 0.5:
            return Sentiment.VERY_POSITIVE, score
        elif score >= 0.15:
            return Sentiment.POSITIVE, score
        elif score <= -0.5:
            return Sentiment.VERY_NEGATIVE, score
        elif score <= -0.15:
            return Sentiment.NEGATIVE, score
        return Sentiment.NEUTRAL, score


# =============================================================================
# SENTENCE RANKER
# =============================================================================

class SentenceRanker:
    """Extractive Summarization, Pi-optimiert"""

    def __init__(self, keyword_extractor: KeywordExtractor = None):
        self.keywords = keyword_extractor or KeywordExtractor()

    def rank_sentences(self, text: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Rankt Sätze nach Wichtigkeit"""
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        doc_keywords = set(kw for kw, _ in self.keywords.extract(text, top_n=20))

        scored = []
        for i, sent in enumerate(sentences):
            score = self._score_sentence(sent, doc_keywords, i, len(sentences))
            if score > 0:
                scored.append((sent, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 30]

    def _score_sentence(self, sentence: str, doc_keywords: set,
                        position: int, total: int) -> float:
        score = 0.0
        sent_lower = sentence.lower()
        sent_words = set(sent_lower.split())

        keyword_overlap = len(sent_words & doc_keywords) / max(len(doc_keywords), 1)
        score += keyword_overlap * 2.0

        if position == 0:
            score += 1.0
        elif position == 1:
            score += 0.5
        elif position >= total - 2:
            score += 0.3

        word_count = len(sentence.split())
        if 10 <= word_count <= 30:
            score += 0.5

        if re.search(r'\d+', sentence):
            score += 0.4

        if re.search(r'["„"]|sagte|erklärte|said|according', sent_lower):
            score += 0.3

        signal_words = ["wichtig", "bedeutend", "neu", "erstmals",
                       "important", "significant", "new", "first", "major"]
        if any(sw in sent_lower for sw in signal_words):
            score += 0.5

        return score


# =============================================================================
# FACT EXTRACTOR v2.0
# =============================================================================

class FactExtractor:
    """Pattern-basierte Fakt-Extraktion, DE + EN, Pi-optimiert"""

    FACT_PATTERNS = [
        # Statistiken
        (r'(\d+(?:[.,]\d+)?)\s*(?:prozent|%|percent)', FactType.STATISTIC),
        (r'(\d+(?:[.,]\d+)?)\s*(?:millionen?|milliarden?|million|billion|euro|dollar)', FactType.STATISTIC),

        # Daten
        (r'(?:im\s+jahr|seit|ab|in|since|from)\s+(\d{4})', FactType.DATE),

        # Definitionen
        (r'(?:ist|sind|is|are|means|bezeichnet)\s+(?:ein[e]?|der|die|das|a|an|the)\s+', FactType.DEFINITION),

        # Zitate
        (r'(?:sagte|erklärte|betonte|said|stated|announced)\s+', FactType.QUOTE),
        (r'(?:laut|nach|according to|per)\s+', FactType.QUOTE),

        # Forschung
        (r'(?:forscher|wissenschaftler|researchers?|scientists?|studien?|study)\s+', FactType.RESEARCH),

        # Vergleiche
        (r'(?:mehr|weniger|more|less|größer|kleiner|better|worse)\s+(?:als|than)\s+', FactType.COMPARISON),

        # Trends
        (r'(?:steigt|sinkt|wächst|rises?|falls?|grows?|increases?|decreases?)\s+', FactType.TREND),

        # Ankündigungen
        (r'(?:neu[e]?|new|erstmals|first|veröffentlicht|released|launched)\s+', FactType.ANNOUNCEMENT),
    ]

    def __init__(self, keyword_extractor: KeywordExtractor = None):
        self.keywords = keyword_extractor or KeywordExtractor()
        self.compiled_patterns = [
            (re.compile(p, re.IGNORECASE), ftype) for p, ftype in self.FACT_PATTERNS
        ]

    def extract_facts(self, text: str,
                      entities: List[ExtractedEntity] = None) -> List[ExtractedFact]:
        """Extrahiert Fakten aus Text"""
        facts = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        doc_keywords = [kw for kw, _ in self.keywords.extract(text, top_n=15)]

        for sent in sentences:
            if len(sent) < 25:
                continue

            fact_type = FactType.UNKNOWN
            confidence = 0.5

            for pattern, ftype in self.compiled_patterns:
                if pattern.search(sent):
                    fact_type = ftype
                    type_conf = {
                        FactType.STATISTIC: 0.8,
                        FactType.RESEARCH: 0.75,
                        FactType.QUOTE: 0.7,
                        FactType.DATE: 0.85,
                        FactType.TREND: 0.7,
                        FactType.ANNOUNCEMENT: 0.75,
                    }
                    confidence = type_conf.get(ftype, 0.6)
                    break

            has_numbers = bool(re.search(r'\d+', sent))
            has_proper_nouns = bool(re.findall(r'\b[A-ZÄÖÜ][a-zäöüß]{2,}\b', sent))

            if fact_type != FactType.UNKNOWN or (has_numbers and has_proper_nouns):
                sent_entities = []
                if entities:
                    for ent in entities:
                        if ent.value.lower() in sent.lower():
                            sent_entities.append(ent.value)

                sent_keywords = [kw for kw in doc_keywords if kw.lower() in sent.lower()]

                main_topic = ""
                if sent_entities:
                    main_topic = sent_entities[0]
                elif sent_keywords:
                    main_topic = sent_keywords[0]

                if has_numbers:
                    confidence = min(confidence + 0.1, 0.95)

                facts.append(ExtractedFact(
                    content=sent.strip(),
                    topic=main_topic,
                    entities=sent_entities,
                    related_topics=sent_keywords[1:4] if len(sent_keywords) > 1 else [],
                    confidence=confidence,
                    source_sentence=sent,
                    keywords=sent_keywords,
                    fact_type=fact_type
                ))

        facts.sort(key=lambda f: f.confidence, reverse=True)
        return facts

    def _extract_entities(self, text: str) -> List[str]:
        """Extrahiert Entitäten aus Text (vereinfacht)"""
        entities = []
        # Finde Wörter die groß geschrieben sind (Namen, Orte, etc.)
        words = text.split()
        for word in words:
            clean = word.strip(".,!?:;\"'()")
            if clean and clean[0].isupper() and len(clean) > 2:
                if clean.lower() not in {"ich", "der", "die", "das", "ein", "eine", "und", "oder"}:
                    entities.append(clean)
        return list(set(entities))[:10]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiert Keywords aus Text"""
        if self.keywords:
            return self.keywords.extract(text)
        # Fallback: einfache Wort-Extraktion
        words = text.lower().split()
        stopwords = {"der", "die", "das", "ein", "eine", "und", "oder", "ist", "sind", "hat", "haben"}
        keywords = [w.strip(".,!?") for w in words if len(w) > 3 and w not in stopwords]
        return list(set(keywords))[:10]

    def _detect_topic(self, text: str) -> str:
        """Erkennt das Hauptthema des Textes"""
        keywords = self._extract_keywords(text)
        if keywords:
            return keywords[0]
        return "allgemein"


# =============================================================================
# TOPIC DETECTOR v2.0
# =============================================================================

class TopicDetector:
    """Topic Detection mit Kategorisierung, Pi-optimiert"""

    CATEGORY_KEYWORDS = {
        TopicCategory.TECH: {
            "computer", "software", "hardware", "app", "internet", "digital",
            "ki", "ai", "algorithmus", "daten", "cloud", "server", "smartphone",
            "tech", "technology", "processor", "chip", "nvidia", "intel", "amd",
            "google", "apple", "microsoft", "amazon", "meta", "facebook",
            "openai", "chatgpt", "claude", "gemini", "llm", "machine learning",
        },
        TopicCategory.GAMING: {
            "spiel", "game", "gaming", "gamer", "playstation", "xbox", "nintendo",
            "switch", "steam", "konsole", "esports", "fortnite", "minecraft",
        },
        TopicCategory.SCIENCE: {
            "wissenschaft", "science", "forschung", "research", "studie",
            "forscher", "scientist", "labor", "experiment", "entdeckung",
            "physik", "chemie", "biologie", "medizin", "weltraum", "nasa",
        },
        TopicCategory.POLITICS: {
            "politik", "politics", "regierung", "government", "minister",
            "präsident", "president", "kanzler", "bundestag", "parlament",
            "wahl", "election", "partei", "gesetz", "reform",
        },
        TopicCategory.ECONOMY: {
            "wirtschaft", "economy", "börse", "stock", "aktie", "markt",
            "unternehmen", "company", "umsatz", "gewinn", "verlust",
            "investition", "investment", "bank", "euro", "dollar", "inflation",
        },
        TopicCategory.SPORTS: {
            "sport", "fußball", "football", "soccer", "basketball", "tennis",
            "rennen", "meisterschaft", "liga", "league", "tor", "goal",
        },
        TopicCategory.ENTERTAINMENT: {
            "film", "movie", "kino", "serie", "netflix", "streaming",
            "musik", "music", "konzert", "album", "künstler", "hollywood",
        },
        TopicCategory.HEALTH: {
            "gesundheit", "health", "medizin", "arzt", "krankenhaus",
            "krankheit", "therapie", "impfung", "virus", "corona", "covid",
        },
        TopicCategory.ENVIRONMENT: {
            "umwelt", "environment", "klima", "climate", "nachhaltigkeit",
            "energie", "solar", "erneuerbar", "emission", "co2",
        },
    }

    def __init__(self):
        self.all_category_keywords = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                self.all_category_keywords[kw.lower()] = category

    def detect_topics(self, text: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Erkennt Hauptthemen"""
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', text_lower)
        word_freq = Counter(words)

        topics = {}
        for word, count in word_freq.items():
            if len(word) >= 4 and count >= 2:
                score = count * (1 + len(word) / 20)
                topics[word] = score

        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics[:top_n]

    def detect_category(self, text: str) -> Tuple[TopicCategory, float]:
        """Bestimmt die Kategorie des Textes"""
        text_lower = text.lower()
        category_scores = Counter()

        for kw, category in self.all_category_keywords.items():
            if kw in text_lower:
                count = text_lower.count(kw)
                category_scores[category] += count

        if not category_scores:
            return TopicCategory.GENERAL, 0.3

        best_category, best_score = category_scores.most_common(1)[0]
        total = sum(category_scores.values())
        confidence = min(best_score / total if total > 0 else 0, 0.95)

        if best_score < 3:
            confidence = max(confidence, 0.4)

        return best_category, confidence


# =============================================================================
# LANGUAGE DETECTOR
# =============================================================================

class LanguageDetector:
    """Einfache Spracherkennung"""

    GERMAN_MARKERS = {"der", "die", "das", "und", "ist", "sind", "wird", "haben", "für", "mit", "auf", "bei"}
    ENGLISH_MARKERS = {"the", "and", "is", "are", "will", "have", "for", "with", "this", "that", "from"}

    def detect(self, text: str) -> str:
        """Erkennt Sprache: 'de', 'en', oder 'unknown'"""
        words = set(text.lower().split())
        de_count = len(words & self.GERMAN_MARKERS)
        en_count = len(words & self.ENGLISH_MARKERS)

        if de_count > en_count:
            return "de"
        elif en_count > de_count:
            return "en"
        elif any(c in text.lower() for c in "äöüß"):
            return "de"
        return "unknown"


# =============================================================================
# HOLO TEXT READER v2.0 (Hauptklasse)
# =============================================================================

class HoloTextReader:
    """
    HoloTextReader v2.0 - Intelligente Text-Analyse

    Verbessert mit:
    - DE + EN Pattern-Erkennung
    - Fallback Entity Recognition
    - Sentiment-Analyse
    - Kategorisierung

    Optimiert für Raspberry Pi!
    """

    def __init__(self, nlp=None, web_curiosity=None):
        self.nlp = nlp
        self.web_curiosity = web_curiosity

        self.keyword_extractor = KeywordExtractor()
        self.entity_extractor = EntityExtractor()
        self.sentence_ranker = SentenceRanker(self.keyword_extractor)
        self.fact_extractor = FactExtractor(self.keyword_extractor)
        self.topic_detector = TopicDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.language_detector = LanguageDetector()

        logger.info("✅ HoloTextReader v2.0 initialisiert")

    def read(self, text: str, source: str = "unknown",
             title: str = "") -> TextAnalysisResult:
        """Liest und analysiert Text vollständig"""
        import time
        start = time.time()

        word_count = len(text.split())
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentence_count = len(sentences)

        language = self.language_detector.detect(text)
        topics = self.topic_detector.detect_topics(text)
        main_topics = [t for t, _ in topics]
        topic_category, _ = self.topic_detector.detect_category(text)
        keywords = [kw for kw, _ in self.keyword_extractor.extract(text, top_n=15)]

        entities = self.entity_extractor.extract(text)

        if self.nlp:
            try:
                analysis = self.nlp.analyze(text[:2000])
                for ent in analysis.get("entities", []):
                    if not any(e.value.lower() == ent.get("value", "").lower() for e in entities):
                        entities.append(ExtractedEntity(
                            value=ent.get("value", ""),
                            entity_type=ent.get("type", "UNKNOWN"),
                            confidence=0.8
                        ))
            except Exception as e:
                logger.debug(f"Smart understanding entity extraction failed: {e}")

        facts = self.fact_extractor.extract_facts(text, entities)
        key_sentences = [s for s, _ in self.sentence_ranker.rank_sentences(text, top_n=3)]
        summary = self._generate_summary(title, main_topics, key_sentences, facts, topic_category)
        sentiment, sentiment_score = self.sentiment_analyzer.analyze(text)
        needs_llm = self._check_needs_llm(text, facts, topics)

        elapsed = time.time() - start

        return TextAnalysisResult(
            source=source,
            title=title,
            word_count=word_count,
            sentence_count=sentence_count,
            main_topics=main_topics,
            topic_category=topic_category,
            entities=entities,
            facts=facts,
            keywords=keywords,
            summary=summary,
            key_sentences=key_sentences,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            reading_time_seconds=elapsed,
            needs_llm_for_deep_analysis=needs_llm,
            language=language
        )

    def read_and_learn(self, text: str, source_url: str = "",
                       title: str = "") -> Dict[str, Any]:
        """Liest und lernt Fakten"""
        analysis = self.read(text, source=source_url, title=title)
        learned_facts = []

        if self.web_curiosity and analysis.facts:
            for fact in analysis.facts[:5]:
                try:
                    self.web_curiosity.learn_fact(
                        content=fact.content,
                        topic=fact.topic or (analysis.main_topics[0] if analysis.main_topics else "allgemein"),
                        source_url=source_url,
                        related_topics=fact.related_topics
                    )
                    learned_facts.append({
                        "fact": fact.content[:100],
                        "topic": fact.topic,
                        "confidence": fact.confidence,
                        "type": fact.fact_type.value
                    })
                except Exception as e:
                    logger.debug(f"Fact learning failed: {e}")

        return {
            "analysis": analysis,
            "learned_facts": learned_facts,
            "facts_count": len(learned_facts),
            "category": analysis.topic_category.value,
            "sentiment": analysis.sentiment.value,
        }

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        return self.read(text).summary

    def extract_topics(self, text: str) -> List[Tuple[str, float]]:
        return self.topic_detector.detect_topics(text, top_n=5)

    def extract_keywords(self, text: str, n: int = 10) -> List[str]:
        return [kw for kw, _ in self.keyword_extractor.extract(text, top_n=n)]

    def extract_entities(self, text: str) -> List[Dict]:
        entities = self.entity_extractor.extract(text)
        return [{"value": e.value, "type": e.entity_type, "confidence": e.confidence} for e in entities]

    def analyze_sentiment(self, text: str) -> Dict:
        sentiment, score = self.sentiment_analyzer.analyze(text)
        return {"sentiment": sentiment.value, "score": score}

    def _generate_summary(self, title: str, topics: List[str],
                          key_sentences: List[str],
                          facts: List[ExtractedFact],
                          category: TopicCategory) -> str:
        """Generiert Zusammenfassung"""
        parts = []

        if title:
            parts.append(f"'{title}'")

        category_names = {
            TopicCategory.TECH: "Technologie",
            TopicCategory.GAMING: "Gaming",
            TopicCategory.SCIENCE: "Wissenschaft",
            TopicCategory.POLITICS: "Politik",
            TopicCategory.ECONOMY: "Wirtschaft",
            TopicCategory.SPORTS: "Sport",
            TopicCategory.ENTERTAINMENT: "Unterhaltung",
            TopicCategory.HEALTH: "Gesundheit",
            TopicCategory.ENVIRONMENT: "Umwelt",
            TopicCategory.GENERAL: "Allgemein",
        }
        cat_name = category_names.get(category, "Allgemein")

        if topics:
            topic_str = ", ".join(topics[:3])
            parts.append(f"[{cat_name}] {topic_str}")
        else:
            parts.append(f"[{cat_name}]")

        if key_sentences:
            first_sent = key_sentences[0]
            if len(first_sent) > 150:
                first_sent = first_sent[:147] + "..."
            parts.append(first_sent)

        if facts:
            high_conf = [f for f in facts if f.confidence >= 0.7]
            parts.append(f"({len(high_conf) if high_conf else len(facts)} Fakten)")

        return " - ".join(parts) if parts else "Keine Zusammenfassung möglich."

    def _check_needs_llm(self, text: str, facts: List[ExtractedFact],
                         topics: List[Tuple[str, float]]) -> bool:
        if len(text) < 500:
            return False
        if len(facts) >= 3:
            return False
        if topics and topics[0][1] > 2.0:
            return False
        return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_summarize(text: str, n: int = 3) -> str:
    return HoloTextReader().summarize(text, n)

def quick_keywords(text: str, n: int = 10) -> List[str]:
    return HoloTextReader().extract_keywords(text, n)

def quick_topics(text: str) -> List[Tuple[str, float]]:
    return HoloTextReader().extract_topics(text)

def quick_entities(text: str) -> List[Dict]:
    return HoloTextReader().extract_entities(text)

def quick_sentiment(text: str) -> Dict:
    return HoloTextReader().analyze_sentiment(text)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import time

    print("=" * 70)
    print("🔍 HOLO TEXT READER v2.0 TEST")
    print("=" * 70)

    test_text = """
    OpenAI hat gestern sein neues KI-Modell GPT-5 vorgestellt. CEO Sam Altman
    erklärte auf der Pressekonferenz in San Francisco: "Das ist unser bisher
    fortschrittlichstes Modell." Die neue Version soll 50% schneller sein als
    der Vorgänger und verbraucht dabei 30% weniger Energie.

    Forscher der Stanford University haben bereits erste Tests durchgeführt.
    Die Studie zeigt, dass GPT-5 in 85% der Fälle bessere Ergebnisse liefert.
    Microsoft investiert weitere 10 Milliarden Dollar in OpenAI.
    """

    reader = HoloTextReader()

    print("\n📰 Analysiere Text...")
    start = time.time()
    result = reader.read(test_text, title="OpenAI stellt GPT-5 vor")
    elapsed = time.time() - start

    print(f"\n⏱  Zeit: {elapsed*1000:.1f}ms")
    print(f"🔤 Sprache: {result.language}")
    print(f"📊 Kategorie: {result.topic_category.value}")
    print(f"😊 Sentiment: {result.sentiment.value} ({result.sentiment_score:.2f})")
    print(f"\n📌 Topics: {', '.join(result.main_topics[:5])}")
    print(f"🔑 Keywords: {', '.join(result.keywords[:8])}")

    print(f"\n👤 Entities ({len(result.entities)}):")
    for ent in result.entities[:5]:
        print(f"   • {ent.value} [{ent.entity_type}]")

    print(f"\n📋 Fakten ({len(result.facts)}):")
    for fact in result.facts[:3]:
        print(f"   [{fact.fact_type.value}] {fact.content[:60]}...")

    print(f"\n📝 Summary: {result.summary}")
    print(f"\n🤖 Braucht LLM: {result.needs_llm_for_deep_analysis}")

    print("\n" + "=" * 70)
    print("✅ TEST ABGESCHLOSSEN")
