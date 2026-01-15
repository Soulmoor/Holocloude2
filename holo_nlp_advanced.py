#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloNLP Advanced v1.0 - Fortgeschrittene NLP-Features

NEUE FEATURES:
1. Topic Modeling (LDA-aehnlich ohne sklearn)
2. Relation Extraction (Subject-Predicate-Object)
3. Timeline Extraction (Events + Daten)
4. Question Answering (extraktiv)
5. Text Generation (Markov Chains + Templates)
6. Aspect-based Sentiment
7. Multi-Label Classification

Optimiert fuer Raspberry Pi - Keine schweren Bibliotheken!

Author: Kira & Claude
Version: 1.0
"""

import re
import math
import random
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime

logger = logging.getLogger("HoloNLPAdvanced")

# =============================================================================
# PUBLIC API - Exported symbols
# =============================================================================

__all__ = [
    # Main Class
    "HoloNLPAdvanced",

    # Topic Modeling
    "SimpleTopicModel",
    "Topic",

    # Relation Extraction
    "RelationExtractor",
    "Relation",

    # Timeline Extraction
    "TimelineExtractor",
    "TimelineEvent",

    # Question Answering
    "ExtractiveQA",
    "QAResult",

    # Text Generation
    "SimpleTextGenerator",

    # Sentiment Analysis
    "AspectSentimentAnalyzer",
    "AspectSentiment",

    # Classification
    "MultiLabelClassifier",
    "TextClassification",
]

# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Topic:
    """Ein erkanntes Thema"""
    topic_id: int
    name: str
    keywords: List[Tuple[str, float]]  # (word, weight)
    documents: List[int]  # Document indices
    coherence: float


@dataclass
class Relation:
    """Eine extrahierte Relation"""
    subject: str
    predicate: str
    object: str
    confidence: float
    sentence: str
    relation_type: str  # "is_a", "has", "located_in", "works_for", etc.


@dataclass
class TimelineEvent:
    """Ein Event auf der Timeline"""
    event_id: str
    description: str
    date: Optional[str]
    date_normalized: Optional[datetime]
    entities: List[str]
    event_type: str  # "birth", "death", "founding", "announcement", etc.
    confidence: float


@dataclass
class QAResult:
    """Ergebnis einer Question-Answering Anfrage"""
    question: str
    answer: str
    confidence: float
    source_sentence: str
    answer_type: str  # "person", "location", "date", "number", "description"


@dataclass
class AspectSentiment:
    """Sentiment fuer einen bestimmten Aspekt"""
    aspect: str
    sentiment: str  # "positiv", "negativ", "neutral"
    score: float
    mentions: List[str]


@dataclass
class TextClassification:
    """Multi-Label Klassifikation"""
    labels: List[str]
    scores: Dict[str, float]
    primary_label: str
    confidence: float


# =============================================================================
# 1. TOPIC MODELING (LDA-aehnlich)
# =============================================================================

class SimpleTopicModel:
    """
    Einfaches Topic Modeling ohne sklearn.

    Verwendet:
    - TF-IDF fuer Feature-Extraktion
    - K-Means-aehnliches Clustering
    - PMI fuer Topic Coherence
    """

    def __init__(self, n_topics: int = 5, n_iterations: int = 20):
        self.n_topics = n_topics
        self.n_iterations = n_iterations
        self.stopwords = self._get_stopwords()
        self.topics: List[Topic] = []

    def _get_stopwords(self) -> Set[str]:
        return {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber",
            "ist", "sind", "war", "waren", "wird", "werden", "hat", "haben",
            "ich", "du", "er", "sie", "es", "wir", "ihr", "sie",
            "in", "an", "auf", "aus", "bei", "mit", "nach", "von", "zu",
            "nicht", "auch", "noch", "nur", "sehr", "so", "wie", "was",
            "kann", "muss", "soll", "will", "darf", "wenn", "dass", "ob",
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "this", "that", "these", "those", "it", "its",
        }

    def fit(self, documents: List[str]) -> List[Topic]:
        """Trainiert das Topic Model"""
        # Tokenize und TF-IDF
        doc_tokens = [self._tokenize(doc) for doc in documents]
        vocab, tfidf_matrix = self._compute_tfidf(doc_tokens)

        if not vocab:
            return []

        # Initialisiere Topics zufaellig
        n_words = len(vocab)
        topic_word_dist = [
            [random.random() for _ in range(n_words)]
            for _ in range(self.n_topics)
        ]

        # Iteratives Update (vereinfachtes LDA)
        doc_topic_dist = [[1.0 / self.n_topics] * self.n_topics for _ in documents]

        for _ in range(self.n_iterations):
            # E-Step: Update document-topic distribution
            for d, tokens in enumerate(doc_tokens):
                for t in range(self.n_topics):
                    score = 0.0
                    for token in tokens:
                        if token in vocab:
                            w_idx = vocab[token]
                            score += topic_word_dist[t][w_idx]
                    doc_topic_dist[d][t] = score + 0.1

                # Normalize
                total = sum(doc_topic_dist[d])
                if total > 0:
                    doc_topic_dist[d] = [s / total for s in doc_topic_dist[d]]

            # M-Step: Update topic-word distribution
            for t in range(self.n_topics):
                for w_idx in range(n_words):
                    word = list(vocab.keys())[list(vocab.values()).index(w_idx)]
                    score = 0.0
                    for d, tokens in enumerate(doc_tokens):
                        if word in tokens:
                            score += doc_topic_dist[d][t] * tokens.count(word)
                    topic_word_dist[t][w_idx] = score + 0.01

                # Normalize
                total = sum(topic_word_dist[t])
                if total > 0:
                    topic_word_dist[t] = [s / total for s in topic_word_dist[t]]

        # Extrahiere Topics
        idx_to_word = {v: k for k, v in vocab.items()}
        self.topics = []

        for t in range(self.n_topics):
            # Top Keywords
            word_scores = [(idx_to_word[i], topic_word_dist[t][i])
                          for i in range(n_words)]
            word_scores.sort(key=lambda x: x[1], reverse=True)
            top_keywords = word_scores[:10]

            # Documents in this topic
            topic_docs = [d for d, dist in enumerate(doc_topic_dist)
                         if dist[t] == max(dist)]

            # Topic name from top keyword
            topic_name = top_keywords[0][0] if top_keywords else f"topic_{t}"

            # Coherence
            coherence = self._compute_coherence(top_keywords, doc_tokens)

            self.topics.append(Topic(
                topic_id=t,
                name=topic_name,
                keywords=top_keywords,
                documents=topic_docs,
                coherence=coherence
            ))

        return self.topics

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zäöüß]{3,}\b', text.lower())
        return [w for w in words if w not in self.stopwords]

    def _compute_tfidf(self, doc_tokens: List[List[str]]) -> Tuple[Dict[str, int], List[List[float]]]:
        # Build vocabulary
        vocab = {}
        df = Counter()

        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                if token not in vocab:
                    vocab[token] = len(vocab)
                df[token] += 1

        if not vocab:
            return {}, []

        # Compute TF-IDF
        n_docs = len(doc_tokens)
        tfidf_matrix = []

        for tokens in doc_tokens:
            tf = Counter(tokens)
            tfidf = [0.0] * len(vocab)

            for token, count in tf.items():
                if token in vocab:
                    tf_score = count / len(tokens) if tokens else 0
                    idf_score = math.log(n_docs / (df[token] + 1))
                    tfidf[vocab[token]] = tf_score * idf_score

            tfidf_matrix.append(tfidf)

        return vocab, tfidf_matrix

    def _compute_coherence(self, keywords: List[Tuple[str, float]],
                           doc_tokens: List[List[str]]) -> float:
        """Berechnet Topic Coherence (PMI-basiert)"""
        words = [w for w, _ in keywords[:5]]

        if len(words) < 2:
            return 0.0

        # Count co-occurrences
        coherence = 0.0
        pairs = 0

        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                w1, w2 = words[i], words[j]

                count_w1 = sum(1 for tokens in doc_tokens if w1 in tokens)
                count_w2 = sum(1 for tokens in doc_tokens if w2 in tokens)
                count_both = sum(1 for tokens in doc_tokens
                                if w1 in tokens and w2 in tokens)

                if count_w1 > 0 and count_w2 > 0:
                    pmi = math.log((count_both + 1) * len(doc_tokens) /
                                  (count_w1 * count_w2 + 1))
                    coherence += pmi
                    pairs += 1

        return coherence / pairs if pairs > 0 else 0.0

    def get_document_topics(self, text: str) -> List[Tuple[int, float]]:
        """Gibt Topics fuer ein Dokument zurueck"""
        tokens = self._tokenize(text)
        scores = []

        for topic in self.topics:
            score = sum(weight for word, weight in topic.keywords
                       if word in tokens)
            scores.append((topic.topic_id, score))

        # Normalize
        total = sum(s for _, s in scores)
        if total > 0:
            scores = [(tid, s / total) for tid, s in scores]

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


# =============================================================================
# 2. RELATION EXTRACTION
# =============================================================================

class RelationExtractor:
    """
    Extrahiert Relationen (Subject-Predicate-Object) aus Text.

    Verwendet:
    - Dependency-aehnliche Patterns
    - Regelbasierte Extraktion
    """

    def __init__(self):
        self._init_patterns()

    def _init_patterns(self):
        """Initialisiert Extraktions-Patterns"""

        # Relation patterns: (regex, relation_type, subject_group, object_group)
        self.patterns = [
            # "X ist Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+ist\s+(?:ein[e]?\s+)?([A-Za-zäöüß]+)',
             "is_a", 1, 2),

            # "X ist der/die Y von Z"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+ist\s+(?:der|die|das)\s+([A-Za-zäöüß]+)\s+von\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "role_of", 1, 3),

            # "X arbeitet bei/fuer Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+arbeitet\s+(?:bei|für|fuer)\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "works_for", 1, 2),

            # "X lebt in Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+(?:lebt|wohnt)\s+in\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "lives_in", 1, 2),

            # "X wurde in Y geboren"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+wurde\s+in\s+([A-ZÄÖÜ][a-zäöüß]+)\s+geboren',
             "born_in", 1, 2),

            # "X gehoert zu Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+)\s+gehört\s+zu\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "part_of", 1, 2),

            # "X hat Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+hat\s+(?:ein[e]?\s+)?([A-Za-zäöüß]+)',
             "has", 1, 2),

            # "X gruendete Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+(?:gründete|gruendete)\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "founded", 1, 2),

            # "X kaufte Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+)\s+kaufte\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "acquired", 1, 2),

            # "X ist CEO/Chef von Y"
            (r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\s+ist\s+(?:CEO|Chef|Geschäftsfuehrer|Vorstand)\s+von\s+([A-ZÄÖÜ][a-zäöüß]+)',
             "leads", 1, 2),
        ]

        # Compile patterns
        self.compiled_patterns = [
            (re.compile(p, re.IGNORECASE), rel, sg, og)
            for p, rel, sg, og in self.patterns
        ]

        # Predicate mappings
        self.predicate_map = {
            "is_a": "ist ein(e)",
            "role_of": "ist ... von",
            "works_for": "arbeitet für",
            "lives_in": "lebt in",
            "born_in": "wurde geboren in",
            "part_of": "gehört zu",
            "has": "hat",
            "founded": "gründete",
            "acquired": "kaufte",
            "leads": "leitet",
        }

    def extract(self, text: str) -> List[Relation]:
        """Extrahiert alle Relationen aus dem Text"""
        relations = []
        sentences = re.split(r'[.!?]+', text)

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            for pattern, rel_type, subj_group, obj_group in self.compiled_patterns:
                for match in pattern.finditer(sent):
                    try:
                        subject = match.group(subj_group).strip()
                        obj = match.group(obj_group).strip()

                        if len(subject) > 1 and len(obj) > 1:
                            relations.append(Relation(
                                subject=subject,
                                predicate=self.predicate_map.get(rel_type, rel_type),
                                object=obj,
                                confidence=0.8,
                                sentence=sent,
                                relation_type=rel_type
                            ))
                    except IndexError:
                        continue

        # Deduplicate
        seen = set()
        unique_relations = []
        for rel in relations:
            key = (rel.subject.lower(), rel.relation_type, rel.object.lower())
            if key not in seen:
                seen.add(key)
                unique_relations.append(rel)

        return unique_relations

    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extrahiert als einfache Tripel"""
        relations = self.extract(text)
        return [(r.subject, r.predicate, r.object) for r in relations]


# =============================================================================
# 3. TIMELINE EXTRACTION
# =============================================================================

class TimelineExtractor:
    """
    Extrahiert Events und Daten fuer eine Timeline.
    """

    def __init__(self):
        self._init_patterns()

    def _init_patterns(self):
        """Initialisiert Datums- und Event-Patterns"""

        self.month_map = {
            "januar": 1, "februar": 2, "maerz": 3, "märz": 3, "april": 4,
            "mai": 5, "juni": 6, "juli": 7, "august": 8, "september": 9,
            "oktober": 10, "november": 11, "dezember": 12,
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8, "september": 9,
            "october": 10, "november": 11, "december": 12,
        }

        self.date_patterns = [
            # "12. Januar 2023"
            (r'(\d{1,2})\.\s*(' + '|'.join(self.month_map.keys()) + r')\s*(\d{4})',
             "day_month_year"),
            # "Januar 2023"
            (r'(' + '|'.join(self.month_map.keys()) + r')\s*(\d{4})',
             "month_year"),
            # "2023"
            (r'\b(19\d{2}|20\d{2})\b', "year"),
            # "12.01.2023"
            (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', "numeric"),
        ]

        self.event_indicators = {
            "birth": ["geboren", "geburt", "kam zur welt", "born"],
            "death": ["gestorben", "starb", "tod", "verstarb", "died", "death"],
            "founding": ["gegründet", "gründung", "gruendete", "founded", "established"],
            "announcement": ["angekündigt", "vorgestellt", "präsentiert", "announced"],
            "release": ["veröffentlicht", "erschienen", "released", "launched"],
            "election": ["gewählt", "wahl", "elected"],
            "award": ["ausgezeichnet", "gewann", "erhielt", "awarded", "won"],
            "merger": ["fusioniert", "übernommen", "merged", "acquired"],
            "start": ["begann", "startete", "began", "started"],
            "end": ["endete", "beendet", "ended", "finished"],
        }

    def extract(self, text: str) -> List[TimelineEvent]:
        """Extrahiert Timeline-Events"""
        events = []
        sentences = re.split(r'[.!?]+', text)

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            # Find dates
            dates = self._find_dates(sent)

            if dates:
                # Find event type
                event_type = self._classify_event(sent)

                # Extract entities
                entities = self._extract_entities(sent)

                for date_str, date_norm in dates:
                    events.append(TimelineEvent(
                        event_id=f"evt_{hash(sent) % 10000}",
                        description=sent[:200],
                        date=date_str,
                        date_normalized=date_norm,
                        entities=entities,
                        event_type=event_type,
                        confidence=0.8 if date_norm else 0.6
                    ))

        # Sort by date
        events.sort(key=lambda e: e.date_normalized or datetime.max)

        return events

    def _find_dates(self, text: str) -> List[Tuple[str, Optional[datetime]]]:
        """Findet alle Daten im Text"""
        dates = []
        text_lower = text.lower()

        for pattern, date_type in self.date_patterns:
            for match in re.finditer(pattern, text_lower):
                date_str = match.group(0)
                date_norm = self._normalize_date(match, date_type)
                dates.append((date_str, date_norm))

        return dates

    def _normalize_date(self, match, date_type: str) -> Optional[datetime]:
        """Normalisiert ein Datum zu datetime"""
        try:
            if date_type == "day_month_year":
                day = int(match.group(1))
                month = self.month_map.get(match.group(2).lower(), 1)
                year = int(match.group(3))
                return datetime(year, month, day)

            elif date_type == "month_year":
                month = self.month_map.get(match.group(1).lower(), 1)
                year = int(match.group(2))
                return datetime(year, month, 1)

            elif date_type == "year":
                year = int(match.group(1))
                return datetime(year, 1, 1)

            elif date_type == "numeric":
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                return datetime(year, month, day)
        except (ValueError, IndexError):
            pass

        return None

    def _classify_event(self, text: str) -> str:
        """Klassifiziert den Event-Typ"""
        text_lower = text.lower()

        for event_type, indicators in self.event_indicators.items():
            if any(ind in text_lower for ind in indicators):
                return event_type

        return "general"

    def _extract_entities(self, text: str) -> List[str]:
        """Extrahiert Entitaeten aus dem Satz"""
        # Simple: Alle Grossgeschriebenen Woerter
        entities = re.findall(r'\b([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?)\b', text)
        return list(set(entities))[:5]


# =============================================================================
# 4. QUESTION ANSWERING (Extraktiv)
# =============================================================================

class ExtractiveQA:
    """
    Beantwortet Fragen durch Extraktion aus dem Text.
    """

    def __init__(self):
        self._init_question_patterns()

    def _init_question_patterns(self):
        """Initialisiert Frage-Patterns"""

        self.question_types = {
            "wer": ("person", ["ist", "war", "hat", "wird", "wurde"]),
            "was": ("thing", ["ist", "sind", "macht", "bedeutet"]),
            "wo": ("location", ["ist", "liegt", "befindet", "statt"]),
            "wann": ("date", ["ist", "war", "wurde", "findet", "beginnt"]),
            "wie viel": ("number", ["kostet", "sind", "beträgt", "dauert"]),
            "wie viele": ("number", ["gibt", "sind", "haben"]),
            "warum": ("reason", ["ist", "hat", "wurde"]),
            "welche": ("thing", ["ist", "sind", "gibt"]),
        }

    def answer(self, question: str, context: str) -> QAResult:
        """Beantwortet eine Frage basierend auf dem Kontext"""
        question_lower = question.lower()

        # Bestimme Frage-Typ
        answer_type = "description"
        for q_word, (a_type, _) in self.question_types.items():
            if question_lower.startswith(q_word):
                answer_type = a_type
                break

        # Extrahiere Keywords aus der Frage
        q_keywords = self._extract_keywords(question)

        # Finde relevante Saetze
        sentences = re.split(r'[.!?]+', context)
        scored_sentences = []

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            score = self._score_sentence(sent, q_keywords, answer_type)
            if score > 0:
                scored_sentences.append((sent, score))

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
        answer = self._extract_answer(best_sentence, question, answer_type)

        return QAResult(
            question=question,
            answer=answer,
            confidence=min(score / 5, 1.0),
            source_sentence=best_sentence,
            answer_type=answer_type
        )

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extrahiert Keywords"""
        stopwords = {"wer", "was", "wo", "wann", "wie", "warum", "welche",
                    "ist", "sind", "war", "hat", "wird", "der", "die", "das",
                    "ein", "eine", "und", "oder", "von", "zu", "in", "an"}
        words = re.findall(r'\b[a-zäöüß]{3,}\b', text.lower())
        return set(w for w in words if w not in stopwords)

    def _score_sentence(self, sentence: str, keywords: Set[str],
                        answer_type: str) -> float:
        """Bewertet einen Satz"""
        sent_lower = sentence.lower()
        score = 0.0

        # Keyword overlap
        for kw in keywords:
            if kw in sent_lower:
                score += 1.0

        # Answer type bonus
        if answer_type == "person":
            if re.search(r'[A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+', sentence):
                score += 0.5
        elif answer_type == "date":
            if re.search(r'\d{4}|\d{1,2}\.\s*\w+', sentence):
                score += 0.5
        elif answer_type == "number":
            if re.search(r'\d+', sentence):
                score += 0.5
        elif answer_type == "location":
            if any(w in sent_lower for w in ["in", "aus", "bei", "nach"]):
                score += 0.3

        return score

    def _extract_answer(self, sentence: str, question: str,
                        answer_type: str) -> str:
        """Extrahiert die Antwort aus dem Satz"""

        if answer_type == "person":
            # Find person names
            names = re.findall(r'[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+', sentence)
            if names:
                return names[0]

        elif answer_type == "date":
            # Find dates
            dates = re.findall(r'\d{1,2}\.\s*\w+\s*\d{4}|\w+\s+\d{4}|\d{4}', sentence)
            if dates:
                return dates[0]

        elif answer_type == "number":
            # Find numbers
            numbers = re.findall(r'\d+(?:[.,]\d+)?(?:\s*(?:Euro|Dollar|Prozent|%|Millionen|Milliarden))?', sentence)
            if numbers:
                return numbers[0]

        elif answer_type == "location":
            # Find location (after "in", "aus", etc.)
            loc_match = re.search(r'(?:in|aus|bei|nach)\s+([A-ZÄÖÜ][a-zäöüß]+)', sentence)
            if loc_match:
                return loc_match.group(1)

        # Fallback: return sentence (truncated)
        return sentence[:150] + "..." if len(sentence) > 150 else sentence


# =============================================================================
# 5. TEXT GENERATION
# =============================================================================

class SimpleTextGenerator:
    """
    Einfache Textgenerierung mit Markov Chains und Templates.
    """

    def __init__(self, order: int = 2):
        self.order = order
        self.transitions: Dict[Tuple, Counter] = defaultdict(Counter)
        self.starters: List[Tuple] = []
        self.templates = self._init_templates()

    def _init_templates(self) -> Dict[str, List[str]]:
        """Initialisiert Text-Templates"""
        return {
            "summary": [
                "Der Text handelt von {topic}. {key_point}",
                "Hauptsächlich geht es um {topic}. Dabei wird {key_point} erläutert.",
                "{topic} ist das zentrale Thema. {key_point}",
            ],
            "description": [
                "{subject} ist {attribute}. {detail}",
                "Bei {subject} handelt es sich um {attribute}.",
                "{subject} zeichnet sich durch {attribute} aus.",
            ],
            "comparison": [
                "Während {a} {attr_a} ist, ist {b} {attr_b}.",
                "{a} und {b} unterscheiden sich: {a} ist {attr_a}, {b} hingegen {attr_b}.",
                "Im Vergleich zu {b} ist {a} {attr_a}.",
            ],
            "question": [
                "Was bedeutet {topic} in diesem Kontext?",
                "Wie hängt {topic} mit {related} zusammen?",
                "Welche Rolle spielt {topic}?",
            ],
        }

    def train(self, texts: List[str]):
        """Trainiert den Markov-Generator"""
        for text in texts:
            words = text.split()

            if len(words) <= self.order:
                continue

            # Record starter
            self.starters.append(tuple(words[:self.order]))

            # Build transitions
            for i in range(len(words) - self.order):
                state = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                self.transitions[state][next_word] += 1

    def generate_markov(self, length: int = 50, seed: Tuple = None) -> str:
        """Generiert Text mit Markov Chain"""
        if not self.starters:
            return ""

        # Start state
        if seed and seed in self.transitions:
            current = seed
        else:
            current = random.choice(self.starters)

        result = list(current)

        for _ in range(length - self.order):
            if current not in self.transitions:
                break

            # Choose next word
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

    def generate_from_template(self, template_type: str,
                               variables: Dict[str, str]) -> str:
        """Generiert Text aus Template"""
        if template_type not in self.templates:
            return ""

        template = random.choice(self.templates[template_type])

        try:
            return template.format(**variables)
        except KeyError:
            return template

    def generate_summary(self, topic: str, key_points: List[str]) -> str:
        """Generiert eine Zusammenfassung"""
        key_point = key_points[0] if key_points else "verschiedene Aspekte werden behandelt"
        return self.generate_from_template("summary", {
            "topic": topic,
            "key_point": key_point
        })


# =============================================================================
# 6. ASPECT-BASED SENTIMENT
# =============================================================================

class AspectSentimentAnalyzer:
    """
    Analysiert Sentiment pro Aspekt.
    z.B. "Das Essen war gut, aber der Service schlecht"
    """

    def __init__(self):
        self._init_lexicons()

    def _init_lexicons(self):
        """Initialisiert Sentiment-Lexikon"""
        self.positive = {
            "gut", "super", "toll", "ausgezeichnet", "fantastisch", "wunderbar",
            "lecker", "freundlich", "schnell", "sauber", "gemütlich", "schön",
            "perfekt", "hervorragend", "empfehlenswert", "zufrieden", "top",
            "great", "good", "excellent", "amazing", "wonderful", "delicious",
        }

        self.negative = {
            "schlecht", "schrecklich", "furchtbar", "langsam", "unhöflich",
            "kalt", "teuer", "dreckig", "laut", "enttäuscht", "mangelhaft",
            "unfreundlich", "ungenießbar", "katastrophal", "nie wieder",
            "bad", "terrible", "awful", "slow", "rude", "dirty", "expensive",
        }

        self.negations = {"nicht", "kein", "keine", "nie", "niemals", "kaum"}

        # Common aspects
        self.aspects = {
            "essen": ["essen", "gericht", "speise", "portion", "geschmack", "food"],
            "service": ["service", "bedienung", "kellner", "personal", "staff"],
            "preis": ["preis", "kosten", "teuer", "günstig", "wert", "price"],
            "atmosphäre": ["atmosphäre", "ambiente", "einrichtung", "laut", "gemütlich"],
            "qualität": ["qualität", "quality", "verarbeitung"],
            "lieferung": ["lieferung", "versand", "delivery", "schnell", "pünktlich"],
        }

    def analyze(self, text: str) -> List[AspectSentiment]:
        """Analysiert Sentiment pro Aspekt"""
        results = []
        text_lower = text.lower()
        sentences = re.split(r'[.!?,;]+', text)

        for aspect_name, aspect_words in self.aspects.items():
            mentions = []
            sentiment_scores = []

            for sent in sentences:
                sent_lower = sent.lower()

                # Check if aspect is mentioned
                if any(aw in sent_lower for aw in aspect_words):
                    mentions.append(sent.strip())

                    # Calculate sentiment for this sentence
                    score = self._sentence_sentiment(sent_lower)
                    sentiment_scores.append(score)

            if mentions:
                avg_score = sum(sentiment_scores) / len(sentiment_scores)

                if avg_score > 0.2:
                    sentiment = "positiv"
                elif avg_score < -0.2:
                    sentiment = "negativ"
                else:
                    sentiment = "neutral"

                results.append(AspectSentiment(
                    aspect=aspect_name,
                    sentiment=sentiment,
                    score=avg_score,
                    mentions=mentions[:3]
                ))

        return results

    def _sentence_sentiment(self, sentence: str) -> float:
        """Berechnet Sentiment fuer einen Satz"""
        words = sentence.split()
        score = 0.0
        negation = False

        for i, word in enumerate(words):
            word_clean = re.sub(r'[^\w]', '', word)

            if word_clean in self.negations:
                negation = True
                continue

            if word_clean in self.positive:
                score += -1.0 if negation else 1.0
            elif word_clean in self.negative:
                score += 1.0 if negation else -1.0

            negation = False

        return score / max(len(words), 1)


# =============================================================================
# 7. MULTI-LABEL CLASSIFICATION
# =============================================================================

class MultiLabelClassifier:
    """
    Klassifiziert Text in mehrere Kategorien gleichzeitig.
    """

    def __init__(self):
        self._init_categories()

    def _init_categories(self):
        """Initialisiert Kategorie-Keywords"""
        self.categories = {
            "technologie": {
                "keywords": ["computer", "software", "hardware", "app", "digital",
                           "ki", "ai", "algorithmus", "daten", "internet", "cloud",
                           "smartphone", "tablet", "prozessor", "speicher"],
                "weight": 1.0
            },
            "wirtschaft": {
                "keywords": ["unternehmen", "firma", "börse", "aktie", "gewinn",
                           "umsatz", "wirtschaft", "markt", "handel", "investition",
                           "bank", "geld", "euro", "dollar", "inflation"],
                "weight": 1.0
            },
            "politik": {
                "keywords": ["regierung", "partei", "wahl", "politik", "gesetz",
                           "minister", "bundestag", "parlament", "demokratie",
                           "koalition", "opposition", "reform"],
                "weight": 1.0
            },
            "sport": {
                "keywords": ["fußball", "spiel", "mannschaft", "liga", "meister",
                           "tor", "sieg", "niederlage", "trainer", "spieler",
                           "olympia", "rekord", "turnier"],
                "weight": 1.0
            },
            "wissenschaft": {
                "keywords": ["forschung", "studie", "wissenschaft", "forscher",
                           "entdeckung", "experiment", "theorie", "labor",
                           "universität", "professor", "ergebnis"],
                "weight": 1.0
            },
            "unterhaltung": {
                "keywords": ["film", "serie", "musik", "konzert", "künstler",
                           "show", "star", "promi", "kino", "album", "streaming"],
                "weight": 1.0
            },
            "gesundheit": {
                "keywords": ["gesundheit", "krankheit", "arzt", "medizin", "therapie",
                           "patient", "krankenhaus", "symptom", "behandlung",
                           "impfung", "virus", "heilung"],
                "weight": 1.0
            },
            "umwelt": {
                "keywords": ["umwelt", "klima", "nachhaltigkeit", "energie", "solar",
                           "wind", "emission", "co2", "recycling", "natur",
                           "artenschutz", "ökologie"],
                "weight": 1.0
            },
        }

    def classify(self, text: str, threshold: float = 0.3) -> TextClassification:
        """Klassifiziert den Text"""
        text_lower = text.lower()
        words = set(re.findall(r'\b[a-zäöüß]+\b', text_lower))

        scores = {}

        for category, config in self.categories.items():
            keywords = set(config["keywords"])
            overlap = len(words & keywords)

            if overlap > 0:
                score = (overlap / len(keywords)) * config["weight"]
                scores[category] = min(score * 3, 1.0)  # Scale up

        # Normalize
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}

        # Filter by threshold
        labels = [cat for cat, score in scores.items() if score >= threshold]

        # Primary label
        primary = max(scores, key=scores.get) if scores else "allgemein"
        confidence = scores.get(primary, 0.0)

        return TextClassification(
            labels=labels if labels else ["allgemein"],
            scores=scores,
            primary_label=primary,
            confidence=confidence
        )


# =============================================================================
# UNIFIED CLASS
# =============================================================================

class HoloNLPAdvanced:
    """
    Vereinigte Klasse fuer alle fortgeschrittenen NLP-Features.
    """

    def __init__(self):
        self.topic_model = SimpleTopicModel()
        self.relation_extractor = RelationExtractor()
        self.timeline_extractor = TimelineExtractor()
        self.qa = ExtractiveQA()
        self.text_generator = SimpleTextGenerator()
        self.aspect_sentiment = AspectSentimentAnalyzer()
        self.classifier = MultiLabelClassifier()

        logger.info("HoloNLPAdvanced initialisiert")

    def analyze(self, text: str) -> Dict[str, Any]:
        """Fuehrt alle Analysen durch"""
        return {
            "relations": self.relation_extractor.extract(text),
            "timeline": self.timeline_extractor.extract(text),
            "aspect_sentiment": self.aspect_sentiment.analyze(text),
            "classification": self.classifier.classify(text),
        }

    def train_topics(self, documents: List[str]) -> List[Topic]:
        """Trainiert Topic Model"""
        return self.topic_model.fit(documents)

    def answer_question(self, question: str, context: str) -> QAResult:
        """Beantwortet eine Frage"""
        return self.qa.answer(question, context)

    def generate_text(self, template_type: str, variables: Dict) -> str:
        """Generiert Text aus Template"""
        return self.text_generator.generate_from_template(template_type, variables)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO NLP ADVANCED v1.0 TEST")
    print("=" * 70)

    nlp = HoloNLPAdvanced()

    test_text = """
    Angela Merkel wurde in Hamburg geboren und war von 2005 bis 2021
    Bundeskanzlerin von Deutschland. Sie arbeitet für die CDU.

    Im Jahr 2015 kam es zur Flüchtlingskrise. Merkel sagte: "Wir schaffen das."

    Olaf Scholz ist der neue Bundeskanzler seit Dezember 2021.
    Er lebt in Hamburg und ist Mitglied der SPD.

    Das Essen im Restaurant war sehr gut, aber der Service war langsam.
    Die Atmosphäre war gemütlich, nur etwas zu laut.
    """

    result = nlp.analyze(test_text)

    print("\nRELATIONEN:")
    for rel in result["relations"]:
        print(f"  {rel.subject} --[{rel.relation_type}]--> {rel.object}")

    print("\nTIMELINE:")
    for evt in result["timeline"]:
        print(f"  [{evt.date}] {evt.event_type}: {evt.description[:50]}...")

    print("\nASPEKT-SENTIMENT:")
    for asp in result["aspect_sentiment"]:
        print(f"  {asp.aspect}: {asp.sentiment} ({asp.score:.2f})")

    print("\nKLASSIFIKATION:")
    cls = result["classification"]
    print(f"  Labels: {cls.labels}")
    print(f"  Primary: {cls.primary_label} ({cls.confidence:.2f})")

    print("\nQUESTION ANSWERING:")
    qa_result = nlp.answer_question("Wer war Bundeskanzlerin?", test_text)
    print(f"  Q: {qa_result.question}")
    print(f"  A: {qa_result.answer} (conf: {qa_result.confidence:.2f})")

    print("\n" + "=" * 70)
    print("TEST ABGESCHLOSSEN")
