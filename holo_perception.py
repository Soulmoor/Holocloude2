#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO PERCEPTION v1.0 - Wahrnehmungssystem                                   ║
║                                                                              ║
║  KOMPONENTEN:                                                                ║
║  • HoloReader - Text-Lese-System                                             ║
║    - Bücher/Artikel/Texte lesen und verstehen                                ║
║    - Sentiment-Analyse                                                       ║
║    - Schlüsselwörter extrahieren                                             ║
║    - Zusammenfassungen generieren (regelbasiert)                             ║
║    - Emotionale Reaktion auf Text                                            ║
║    - Lesefortschritt speichern                                               ║
║                                                                              ║
║  • HoloVision - Bild-Analyse-System                                          ║
║    - Bilder analysieren (OpenCV/PIL)                                         ║
║    - Farben erkennen (dominant colors, Farbstimmung)                         ║
║    - Helligkeit/Kontrast analysieren                                         ║
║    - Gesichtserkennung (Anzahl)                                              ║
║    - Objekt-Erkennung (YOLO/MobileNet)                                       ║
║    - Stimmung aus Bildfarben ableiten                                        ║
║    - Bildkomposition verstehen                                               ║
║                                                                              ║
║  Author: Kira & Claude                                                       ║
║  Version: 1.0                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import math
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum, auto

logger = logging.getLogger("HoloPerception")

# =============================================================================
# OPTIONAL IMPORTS - Graceful Fallbacks
# =============================================================================

# OpenCV für Bildanalyse
_HAS_CV2 = False
try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
    logger.info("OpenCV verfügbar")
except ImportError:
    logger.warning("OpenCV nicht verfügbar - Bildanalyse eingeschränkt")

# PIL als Fallback
_HAS_PIL = False
try:
    from PIL import Image, ImageStat
    _HAS_PIL = True
    logger.info("PIL verfügbar")
except ImportError:
    logger.warning("PIL nicht verfügbar")

# NumPy (oft mit CV2 installiert)
_HAS_NUMPY = False
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    pass


# =============================================================================
# ENUMS UND DATACLASSES
# =============================================================================

class TextType(Enum):
    """Typ des Textes"""
    UNKNOWN = auto()
    ARTICLE = auto()
    BOOK = auto()
    POEM = auto()
    NEWS = auto()
    DIALOGUE = auto()
    TECHNICAL = auto()
    NARRATIVE = auto()
    ESSAY = auto()


class ImageType(Enum):
    """Typ des Bildes"""
    UNKNOWN = auto()
    PORTRAIT = auto()
    LANDSCAPE = auto()
    ABSTRACT = auto()
    PHOTO = auto()
    ARTWORK = auto()
    SCREENSHOT = auto()
    DIAGRAM = auto()
    MEME = auto()


class ColorMood(Enum):
    """Stimmung basierend auf Farben"""
    WARM = "warm"
    COLD = "kalt"
    NEUTRAL = "neutral"
    VIBRANT = "lebhaft"
    MUTED = "gedämpft"
    DARK = "dunkel"
    BRIGHT = "hell"


@dataclass
class TextAnalysisResult:
    """Ergebnis einer Textanalyse"""
    text_id: str
    text_type: TextType
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    sentiment: float  # -1.0 bis 1.0
    sentiment_label: str
    keywords: List[str]
    key_phrases: List[str]
    summary: str
    emotional_response: Dict[str, float]
    reading_time_minutes: float
    complexity_score: float  # 0.0 bis 1.0
    topics: List[str]
    entities: Dict[str, List[str]]  # Namen, Orte, etc.
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ReadingProgress:
    """Lesefortschritt für einen Text"""
    text_id: str
    title: str
    total_words: int
    words_read: int
    current_position: int  # Zeichen-Position
    current_chapter: Optional[str]
    percent_complete: float
    started_at: str
    last_read_at: str
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    bookmarks: List[int] = field(default_factory=list)


@dataclass
class ImageAnalysisResult:
    """Ergebnis einer Bildanalyse"""
    image_id: str
    image_type: ImageType
    width: int
    height: int
    aspect_ratio: float
    dominant_colors: List[Tuple[int, int, int]]  # RGB
    color_names: List[str]
    brightness: float  # 0.0 bis 1.0
    contrast: float  # 0.0 bis 1.0
    saturation: float  # 0.0 bis 1.0
    color_mood: ColorMood
    face_count: int
    detected_objects: List[str]
    composition: str  # "portrait", "landscape", "square"
    emotional_impression: Dict[str, float]
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# HOLO READER - Text-Lese-System
# =============================================================================

class HoloReader:
    """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║  HOLO READER - Text-Wahrnehmung und Analyse                           ║
    ║                                                                       ║
    ║  Funktionen:                                                          ║
    ║  • Texte lesen und verstehen                                          ║
    ║  • Sentiment-Analyse (regelbasiert)                                   ║
    ║  • Schlüsselwörter und Phrasen extrahieren                            ║
    ║  • Zusammenfassungen generieren                                       ║
    ║  • Emotionale Reaktion berechnen                                      ║
    ║  • Lesefortschritt verwalten                                          ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def __init__(self, data_dir: str = "data/reading"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.reading_progress: Dict[str, ReadingProgress] = {}
        self.analysis_cache: Dict[str, TextAnalysisResult] = {}

        # Lade gespeicherten Fortschritt
        self._load_progress()

        # Sentiment-Lexikon (Deutsch)
        self._init_sentiment_lexicon()

        # Stopwords
        self._init_stopwords()

        # Emotionale Trigger-Wörter
        self._init_emotional_triggers()

    def _init_sentiment_lexicon(self):
        """Initialisiert das Sentiment-Lexikon"""
        self.positive_words = {
            # Starke positive Wörter
            "liebe", "lieben", "liebevoll", "wunderbar", "fantastisch",
            "großartig", "hervorragend", "exzellent", "perfekt", "glücklich",
            "freude", "freuen", "freudig", "begeistert", "begeisterung",
            "toll", "super", "genial", "brilliant", "erstaunlich",
            "schön", "wunderschön", "herrlich", "prächtig", "bezaubernd",
            "hoffnung", "hoffnungsvoll", "optimistisch", "zuversicht",
            "erfolg", "erfolgreich", "triumph", "sieg", "gewinn",
            "frieden", "friedlich", "harmonie", "harmonisch", "einklang",
            "dankbar", "dankbarkeit", "anerkennung", "wertschätzung",
            "vertrauen", "zuverlässig", "treu", "loyal", "ehrlich",
            "mut", "mutig", "tapfer", "stark", "kraft",
            "lachen", "lächeln", "humor", "lustig", "witzig",
            "freundlich", "nett", "herzlich", "warmherzig", "gütig",
            "inspiriert", "inspirierend", "motivation", "motiviert",
            "glänzend", "strahlend", "leuchtend", "funkelnd",
        }

        self.negative_words = {
            # Starke negative Wörter
            "hass", "hassen", "hasserfüllt", "verabscheuen", "abscheu",
            "traurig", "trauer", "traurigkeit", "weinen", "tränen",
            "wut", "wütend", "zorn", "zornig", "ärger", "ärgerlich",
            "angst", "ängstlich", "furcht", "furchtbar", "schrecklich",
            "schlecht", "schlimm", "übel", "miserabel", "katastrophal",
            "schmerz", "schmerzhaft", "leid", "leiden", "qual",
            "einsamkeit", "einsam", "verlassen", "isoliert", "allein",
            "verzweiflung", "verzweifelt", "hoffnungslos", "aussichtslos",
            "schuld", "schuldig", "scham", "schämen", "beschämt",
            "neid", "neidisch", "eifersucht", "eifersüchtig", "missgunst",
            "enttäuschung", "enttäuscht", "frustration", "frustriert",
            "kritik", "kritisch", "tadel", "vorwurf", "beschuldigung",
            "konflikt", "streit", "kampf", "krieg", "feindschaft",
            "versagen", "gescheitert", "niederlage", "verlust", "verlieren",
            "tod", "sterben", "tot", "gestorben", "ende",
            "dunkel", "finster", "düster", "grau", "trist",
            "kalt", "eisig", "frostig", "gefühllos", "herzlos",
            "schwach", "schwäche", "kraftlos", "müde", "erschöpft",
            "langweilig", "öde", "monoton", "eintönig", "fade",
        }

        # Intensifizierer
        self.intensifiers = {
            "sehr": 1.5, "extrem": 2.0, "unglaublich": 1.8, "absolut": 1.7,
            "total": 1.5, "komplett": 1.5, "vollkommen": 1.6, "richtig": 1.3,
            "wirklich": 1.3, "echt": 1.2, "ziemlich": 1.1, "etwas": 0.7,
            "wenig": 0.5, "kaum": 0.3, "nicht": -1.0, "kein": -1.0,
            "nie": -1.0, "niemals": -1.0,
        }

    def _init_stopwords(self):
        """Initialisiert Stopwords"""
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "einer", "eines", "einem",
            "und", "oder", "aber", "doch", "jedoch", "sondern", "sowie",
            "ist", "sind", "war", "waren", "sein", "wird", "werden",
            "hat", "haben", "hatte", "hatten", "kann", "können", "konnte",
            "muss", "müssen", "musste", "soll", "sollen", "sollte",
            "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich",
            "mir", "dir", "sich", "uns", "euch", "ihm", "ihr", "ihnen",
            "den", "dem", "des", "im", "in", "an", "auf", "für", "mit",
            "bei", "zu", "von", "aus", "nach", "über", "unter", "vor",
            "hinter", "neben", "zwischen", "durch", "gegen", "ohne", "um",
            "nicht", "auch", "noch", "schon", "nur", "sehr", "so", "wie",
            "was", "wer", "wo", "wann", "warum", "wenn", "dann", "denn",
            "als", "ob", "dass", "weil", "da", "obwohl", "falls", "damit",
            "diese", "dieser", "dieses", "jene", "jener", "jenes",
            "alle", "alles", "andere", "anderer", "anderes", "mehr",
            "viel", "viele", "wenig", "wenige", "einige", "manche",
            "kein", "keine", "keiner", "keines", "jeder", "jede", "jedes",
        }

    def _init_emotional_triggers(self):
        """Initialisiert emotionale Trigger-Kategorien"""
        self.emotional_triggers = {
            "freude": ["glück", "freude", "lachen", "feiern", "jubel", "spaß", "vergnügen"],
            "trauer": ["trauer", "weinen", "verlust", "abschied", "tod", "schmerz", "leid"],
            "angst": ["angst", "furcht", "panik", "schrecken", "horror", "gefahr", "bedrohung"],
            "wut": ["wut", "zorn", "ärger", "hass", "aggression", "gewalt", "kampf"],
            "liebe": ["liebe", "zuneigung", "romantik", "herz", "küss", "umarm", "sehnsucht"],
            "neugier": ["frage", "geheimnis", "rätsel", "entdeckung", "überraschung", "wunder"],
            "nostalgie": ["erinnerung", "früher", "kindheit", "damals", "vergangen", "alt"],
            "hoffnung": ["hoffnung", "traum", "zukunft", "wunsch", "glaube", "vertrauen"],
        }

    def _generate_text_id(self, text: str) -> str:
        """Generiert eine eindeutige ID für einen Text"""
        return hashlib.md5(text[:1000].encode()).hexdigest()[:12]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiert Text in Wörter"""
        text = text.lower()
        text = re.sub(r'[^\wäöüß\s]', ' ', text)
        words = text.split()
        return [w for w in words if len(w) > 1]

    def _get_sentences(self, text: str) -> List[str]:
        """Extrahiert Sätze aus Text"""
        # Einfache Satz-Segmentierung
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analysiert das Sentiment eines Textes.

        Returns:
            Tuple[float, str]: (Sentiment-Score -1 bis 1, Label)
        """
        words = self._tokenize(text)
        if not words:
            return 0.0, "neutral"

        positive_score = 0.0
        negative_score = 0.0
        current_multiplier = 1.0

        for i, word in enumerate(words):
            # Prüfe auf Intensifizierer
            if word in self.intensifiers:
                current_multiplier = self.intensifiers[word]
                continue

            # Zähle positive/negative Wörter
            if word in self.positive_words:
                positive_score += current_multiplier
            elif word in self.negative_words:
                negative_score += current_multiplier

            # Reset Multiplier nach Verwendung
            if word not in self.intensifiers:
                current_multiplier = 1.0

        # Berechne Gesamt-Score
        total = positive_score + negative_score
        if total == 0:
            return 0.0, "neutral"

        sentiment = (positive_score - negative_score) / max(len(words) * 0.1, 1)
        sentiment = max(-1.0, min(1.0, sentiment))

        # Label zuweisen
        if sentiment > 0.3:
            label = "sehr positiv" if sentiment > 0.6 else "positiv"
        elif sentiment < -0.3:
            label = "sehr negativ" if sentiment < -0.6 else "negativ"
        else:
            label = "neutral"

        return sentiment, label

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrahiert Schlüsselwörter aus dem Text"""
        words = self._tokenize(text)

        # Filtere Stopwords
        content_words = [w for w in words if w not in self.stopwords]

        # Zähle Häufigkeit
        word_freq = Counter(content_words)

        # Berechne TF-IDF-ähnlichen Score (vereinfacht)
        scored_words = []
        for word, freq in word_freq.items():
            if len(word) >= 3:
                # Längere Wörter bekommen Bonus
                score = freq * (1 + len(word) * 0.1)
                scored_words.append((word, score))

        # Sortiere nach Score
        scored_words.sort(key=lambda x: x[1], reverse=True)

        return [word for word, _ in scored_words[:max_keywords]]

    def extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """Extrahiert wichtige Phrasen (N-Gramme)"""
        sentences = self._get_sentences(text)
        bigrams = []
        trigrams = []

        for sentence in sentences:
            words = self._tokenize(sentence)
            words = [w for w in words if w not in self.stopwords or w in ["nicht", "kein"]]

            # Bigrams
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                bigrams.append(bigram)

            # Trigrams
            for i in range(len(words) - 2):
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                trigrams.append(trigram)

        # Zähle und sortiere
        phrase_freq = Counter(bigrams + trigrams)
        top_phrases = phrase_freq.most_common(max_phrases)

        return [phrase for phrase, _ in top_phrases]

    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        Generiert eine extraktive Zusammenfassung (regelbasiert).

        Wählt die wichtigsten Sätze basierend auf:
        - Schlüsselwort-Dichte
        - Position im Text
        - Satzlänge
        """
        sentences = self._get_sentences(text)
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        keywords = set(self.extract_keywords(text, max_keywords=20))

        scored_sentences = []
        for i, sentence in enumerate(sentences):
            words = self._tokenize(sentence)

            # Keyword-Score
            keyword_count = sum(1 for w in words if w in keywords)
            keyword_score = keyword_count / max(len(words), 1)

            # Position-Score (erste und letzte Sätze wichtiger)
            position_score = 0.0
            if i < 2:
                position_score = 0.3
            elif i >= len(sentences) - 2:
                position_score = 0.2

            # Längen-Score (mittellange Sätze bevorzugt)
            length_score = 0.0
            if 10 <= len(words) <= 25:
                length_score = 0.2
            elif len(words) < 5:
                length_score = -0.3

            total_score = keyword_score + position_score + length_score
            scored_sentences.append((i, sentence, total_score))

        # Sortiere nach Score
        scored_sentences.sort(key=lambda x: x[2], reverse=True)

        # Wähle Top-Sätze und sortiere nach Original-Position
        top_sentences = scored_sentences[:max_sentences]
        top_sentences.sort(key=lambda x: x[0])

        return " ".join(s[1] for s in top_sentences)

    def calculate_emotional_response(self, text: str) -> Dict[str, float]:
        """Berechnet die emotionale Reaktion auf den Text"""
        words = self._tokenize(text)
        word_set = set(words)

        emotional_scores = {}

        for emotion, triggers in self.emotional_triggers.items():
            score = 0.0
            for trigger in triggers:
                # Prüfe ob Trigger-Wort vorkommt
                for word in word_set:
                    if trigger in word:
                        score += 1.0

            # Normalisiere
            emotional_scores[emotion] = min(1.0, score / max(len(triggers), 1))

        return emotional_scores

    def detect_text_type(self, text: str) -> TextType:
        """Erkennt den Typ des Textes"""
        text_lower = text.lower()
        sentences = self._get_sentences(text)

        # Prüfe auf Dialog
        dialogue_markers = text.count('"') + text.count('„') + text.count('"')
        if dialogue_markers > 10:
            return TextType.DIALOGUE

        # Prüfe auf Gedicht (kurze Zeilen, Reimstruktur)
        lines = text.split('\n')
        avg_line_length = sum(len(l) for l in lines) / max(len(lines), 1)
        if avg_line_length < 50 and len(lines) > 5:
            return TextType.POEM

        # Prüfe auf technischen Text
        technical_words = {"system", "funktion", "methode", "parameter", "variable",
                          "algorithmus", "daten", "prozess", "implementierung"}
        tech_count = sum(1 for w in self._tokenize(text) if w in technical_words)
        if tech_count / max(len(self._tokenize(text)), 1) > 0.05:
            return TextType.TECHNICAL

        # Prüfe auf Nachricht
        news_markers = ["laut", "berichtet", "meldung", "aktuell", "heute",
                       "gestern", "pressemitteilung", "quelle"]
        if any(m in text_lower for m in news_markers):
            return TextType.NEWS

        # Prüfe auf Essay
        if len(text) > 2000 and len(sentences) > 10:
            return TextType.ESSAY

        # Prüfe auf Narrativ
        narrative_markers = ["er sagte", "sie dachte", "plötzlich", "dann",
                            "eines tages", "es war einmal"]
        if any(m in text_lower for m in narrative_markers):
            return TextType.NARRATIVE

        # Artikel als Default für längere Texte
        if len(text) > 500:
            return TextType.ARTICLE

        return TextType.UNKNOWN

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrahiert benannte Entitäten (Namen, Orte, etc.)"""
        entities = {
            "personen": [],
            "orte": [],
            "organisationen": [],
            "daten": [],
        }

        # Einfache Regex-basierte Extraktion

        # Personen (Wörter mit Großbuchstaben, die keine Satzanfänge sind)
        words = text.split()
        for i, word in enumerate(words[1:], 1):  # Skip erstes Wort
            clean_word = re.sub(r'[^\wäöüÄÖÜß]', '', word)
            if clean_word and clean_word[0].isupper():
                # Prüfe ob es kein Satzanfang ist
                prev_word = words[i-1] if i > 0 else ""
                if not prev_word.endswith(('.', '!', '?')):
                    entities["personen"].append(clean_word)

        # Dedupliziere
        entities["personen"] = list(set(entities["personen"]))[:10]

        # Daten (einfache Muster)
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{2,4}',
            r'\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)',
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["daten"].extend(matches)

        entities["daten"] = list(set(entities["daten"]))[:5]

        return entities

    def calculate_complexity(self, text: str) -> float:
        """Berechnet die Komplexität des Textes (0.0-1.0)"""
        words = self._tokenize(text)
        sentences = self._get_sentences(text)

        if not words or not sentences:
            return 0.0

        # Durchschnittliche Wortlänge
        avg_word_length = sum(len(w) for w in words) / len(words)
        word_complexity = min(1.0, avg_word_length / 10)

        # Durchschnittliche Satzlänge
        avg_sentence_length = len(words) / len(sentences)
        sentence_complexity = min(1.0, avg_sentence_length / 30)

        # Vokabular-Diversität
        unique_words = len(set(words))
        vocab_diversity = unique_words / len(words)

        # Gewichteter Score
        complexity = (word_complexity * 0.3 +
                     sentence_complexity * 0.4 +
                     vocab_diversity * 0.3)

        return round(complexity, 3)

    def analyze_text(self, text: str, title: str = None) -> TextAnalysisResult:
        """
        Führt eine vollständige Textanalyse durch.

        Args:
            text: Der zu analysierende Text
            title: Optionaler Titel

        Returns:
            TextAnalysisResult mit allen Analyseergebnissen
        """
        text_id = self._generate_text_id(text)

        # Prüfe Cache
        if text_id in self.analysis_cache:
            logger.debug(f"Analyse aus Cache: {text_id}")
            return self.analysis_cache[text_id]

        words = self._tokenize(text)
        sentences = self._get_sentences(text)

        # Sentiment
        sentiment_score, sentiment_label = self.analyze_sentiment(text)

        # Keywords und Phrasen
        keywords = self.extract_keywords(text)
        key_phrases = self.extract_key_phrases(text)

        # Zusammenfassung
        summary = self.generate_summary(text)

        # Emotionale Reaktion
        emotional_response = self.calculate_emotional_response(text)

        # Texttyp
        text_type = self.detect_text_type(text)

        # Entitäten
        entities = self.extract_entities(text)

        # Komplexität
        complexity = self.calculate_complexity(text)

        # Lesezeit (durchschnittlich 200 Wörter/Minute)
        reading_time = len(words) / 200

        # Topics aus Keywords ableiten
        topics = keywords[:5]

        result = TextAnalysisResult(
            text_id=text_id,
            text_type=text_type,
            word_count=len(words),
            sentence_count=len(sentences),
            avg_sentence_length=len(words) / max(len(sentences), 1),
            sentiment=sentiment_score,
            sentiment_label=sentiment_label,
            keywords=keywords,
            key_phrases=key_phrases,
            summary=summary,
            emotional_response=emotional_response,
            reading_time_minutes=round(reading_time, 1),
            complexity_score=complexity,
            topics=topics,
            entities=entities,
        )

        # Cache speichern
        self.analysis_cache[text_id] = result

        logger.info(f"Text analysiert: {len(words)} Wörter, Sentiment: {sentiment_label}")

        return result

    def start_reading(self, text: str, title: str = "Unbenannt") -> ReadingProgress:
        """Startet das Lesen eines Textes und erstellt Fortschritt"""
        text_id = self._generate_text_id(text)
        words = self._tokenize(text)

        now = datetime.now().isoformat()

        progress = ReadingProgress(
            text_id=text_id,
            title=title,
            total_words=len(words),
            words_read=0,
            current_position=0,
            current_chapter=None,
            percent_complete=0.0,
            started_at=now,
            last_read_at=now,
            sessions=[{"started": now, "words_read": 0}],
        )

        self.reading_progress[text_id] = progress
        self._save_progress()

        logger.info(f"Lesen gestartet: '{title}' ({len(words)} Wörter)")

        return progress

    def update_reading_progress(self, text_id: str, position: int,
                                words_read: int = None) -> Optional[ReadingProgress]:
        """Aktualisiert den Lesefortschritt"""
        if text_id not in self.reading_progress:
            logger.warning(f"Kein Lesefortschritt für {text_id}")
            return None

        progress = self.reading_progress[text_id]
        progress.current_position = position

        if words_read is not None:
            progress.words_read = words_read

        progress.percent_complete = round(
            (progress.words_read / max(progress.total_words, 1)) * 100, 1
        )
        progress.last_read_at = datetime.now().isoformat()

        self._save_progress()

        return progress

    def add_bookmark(self, text_id: str, position: int) -> bool:
        """Fügt ein Lesezeichen hinzu"""
        if text_id not in self.reading_progress:
            return False

        if position not in self.reading_progress[text_id].bookmarks:
            self.reading_progress[text_id].bookmarks.append(position)
            self._save_progress()

        return True

    def add_note(self, text_id: str, note: str) -> bool:
        """Fügt eine Notiz hinzu"""
        if text_id not in self.reading_progress:
            return False

        self.reading_progress[text_id].notes.append(note)
        self._save_progress()

        return True

    def get_reading_progress(self, text_id: str) -> Optional[ReadingProgress]:
        """Gibt den Lesefortschritt zurück"""
        return self.reading_progress.get(text_id)

    def _save_progress(self):
        """Speichert den Lesefortschritt"""
        progress_file = self.data_dir / "reading_progress.json"

        data = {}
        for text_id, progress in self.reading_progress.items():
            data[text_id] = {
                "text_id": progress.text_id,
                "title": progress.title,
                "total_words": progress.total_words,
                "words_read": progress.words_read,
                "current_position": progress.current_position,
                "current_chapter": progress.current_chapter,
                "percent_complete": progress.percent_complete,
                "started_at": progress.started_at,
                "last_read_at": progress.last_read_at,
                "sessions": progress.sessions,
                "notes": progress.notes,
                "bookmarks": progress.bookmarks,
            }

        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_progress(self):
        """Lädt gespeicherten Lesefortschritt"""
        progress_file = self.data_dir / "reading_progress.json"

        if not progress_file.exists():
            return

        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for text_id, progress_data in data.items():
                self.reading_progress[text_id] = ReadingProgress(
                    text_id=progress_data["text_id"],
                    title=progress_data["title"],
                    total_words=progress_data["total_words"],
                    words_read=progress_data["words_read"],
                    current_position=progress_data["current_position"],
                    current_chapter=progress_data.get("current_chapter"),
                    percent_complete=progress_data["percent_complete"],
                    started_at=progress_data["started_at"],
                    last_read_at=progress_data["last_read_at"],
                    sessions=progress_data.get("sessions", []),
                    notes=progress_data.get("notes", []),
                    bookmarks=progress_data.get("bookmarks", []),
                )

            logger.info(f"Lesefortschritt geladen: {len(self.reading_progress)} Texte")
        except Exception as e:
            logger.error(f"Fehler beim Laden des Lesefortschritts: {e}")


# =============================================================================
# HOLO VISION - Bild-Analyse-System
# =============================================================================

class HoloVision:
    """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║  HOLO VISION - Bild-Wahrnehmung und Analyse                           ║
    ║                                                                       ║
    ║  Funktionen:                                                          ║
    ║  • Bilder laden und analysieren                                       ║
    ║  • Dominante Farben erkennen                                          ║
    ║  • Helligkeit und Kontrast messen                                     ║
    ║  • Gesichtserkennung (Anzahl)                                         ║
    ║  • Objekt-Erkennung (optional mit YOLO)                               ║
    ║  • Emotionale Stimmung aus Farben ableiten                            ║
    ║  • Bildkomposition analysieren                                        ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.has_cv2 = _HAS_CV2
        self.has_pil = _HAS_PIL

        # Gesichtserkennung (OpenCV Haar Cascade)
        self.face_cascade = None
        if self.has_cv2:
            self._init_face_detection()

        # YOLO für Objekterkennung (optional)
        self.yolo_net = None
        self.yolo_classes = []
        self._try_load_yolo()

        # Farbnamen-Mapping
        self._init_color_names()

    def _init_face_detection(self):
        """Initialisiert Haar Cascade für Gesichtserkennung"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.info("Gesichtserkennung initialisiert")
        except Exception as e:
            logger.warning(f"Gesichtserkennung nicht verfügbar: {e}")

    def _try_load_yolo(self):
        """Versucht YOLO-Modell zu laden (optional)"""
        yolo_cfg = self.models_dir / "yolov3.cfg"
        yolo_weights = self.models_dir / "yolov3.weights"
        yolo_names = self.models_dir / "coco.names"

        if not all(f.exists() for f in [yolo_cfg, yolo_weights, yolo_names]):
            logger.info("YOLO-Modell nicht vorhanden - Objekterkennung deaktiviert")
            return

        try:
            if self.has_cv2:
                self.yolo_net = cv2.dnn.readNet(str(yolo_weights), str(yolo_cfg))
                with open(yolo_names, 'r') as f:
                    self.yolo_classes = [line.strip() for line in f.readlines()]
                logger.info(f"YOLO geladen mit {len(self.yolo_classes)} Klassen")
        except Exception as e:
            logger.warning(f"YOLO konnte nicht geladen werden: {e}")

    def _init_color_names(self):
        """Initialisiert Farbnamen-Mapping"""
        self.color_names = {
            # Grundfarben
            (255, 0, 0): "rot",
            (0, 255, 0): "grün",
            (0, 0, 255): "blau",
            (255, 255, 0): "gelb",
            (255, 0, 255): "magenta",
            (0, 255, 255): "cyan",
            (255, 255, 255): "weiß",
            (0, 0, 0): "schwarz",
            # Erweiterte Farben
            (255, 165, 0): "orange",
            (128, 0, 128): "lila",
            (255, 192, 203): "rosa",
            (165, 42, 42): "braun",
            (128, 128, 128): "grau",
            (0, 128, 0): "dunkelgrün",
            (0, 0, 128): "dunkelblau",
            (128, 0, 0): "dunkelrot",
            (255, 215, 0): "gold",
            (192, 192, 192): "silber",
            (0, 128, 128): "türkis",
            (245, 245, 220): "beige",
        }

        # Farb-Stimmungs-Mapping
        self.color_moods = {
            "rot": ("warm", "energisch", "leidenschaftlich"),
            "orange": ("warm", "freundlich", "optimistisch"),
            "gelb": ("warm", "fröhlich", "optimistisch"),
            "grün": ("neutral", "natürlich", "beruhigend"),
            "blau": ("kalt", "ruhig", "vertrauenswürdig"),
            "lila": ("neutral", "kreativ", "mysteriös"),
            "rosa": ("warm", "sanft", "romantisch"),
            "braun": ("warm", "natürlich", "stabil"),
            "grau": ("neutral", "sachlich", "professionell"),
            "schwarz": ("dunkel", "elegant", "kraftvoll"),
            "weiß": ("hell", "rein", "minimalistisch"),
        }

    def _generate_image_id(self, image_path: str) -> str:
        """Generiert eine eindeutige ID für ein Bild"""
        return hashlib.md5(image_path.encode()).hexdigest()[:12]

    def _get_closest_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Findet den nächsten Farbnamen für einen RGB-Wert"""
        min_dist = float('inf')
        closest_name = "unbekannt"

        for color_rgb, name in self.color_names.items():
            dist = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb))
            if dist < min_dist:
                min_dist = dist
                closest_name = name

        return closest_name

    def _load_image(self, image_path: str) -> Optional[Any]:
        """Lädt ein Bild (OpenCV oder PIL)"""
        if not os.path.exists(image_path):
            logger.error(f"Bild nicht gefunden: {image_path}")
            return None

        if self.has_cv2:
            img = cv2.imread(image_path)
            if img is not None:
                return ("cv2", img)

        if self.has_pil:
            try:
                img = Image.open(image_path)
                return ("pil", img)
            except Exception as e:
                logger.error(f"PIL konnte Bild nicht laden: {e}")

        return None

    def get_dominant_colors(self, image_path: str, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extrahiert die dominanten Farben aus einem Bild.

        Args:
            image_path: Pfad zum Bild
            num_colors: Anzahl der Farben

        Returns:
            Liste von RGB-Tupeln
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return []

        img_type, img = img_data

        if img_type == "cv2" and _HAS_NUMPY:
            # OpenCV + K-Means
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pixels = img_rgb.reshape(-1, 3).astype(np.float32)

            # K-Means Clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
            _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10,
                                            cv2.KMEANS_RANDOM_CENTERS)

            # Sortiere nach Häufigkeit
            label_counts = Counter(labels.flatten())
            sorted_centers = [centers[i] for i, _ in label_counts.most_common()]

            return [tuple(map(int, c)) for c in sorted_centers[:num_colors]]

        elif img_type == "pil":
            # PIL - Einfache Methode mit Quantisierung
            img_small = img.copy()
            img_small.thumbnail((100, 100))
            img_quantized = img_small.quantize(colors=num_colors)
            palette = img_quantized.getpalette()[:num_colors * 3]

            colors = []
            for i in range(0, len(palette), 3):
                if i + 2 < len(palette):
                    colors.append((palette[i], palette[i+1], palette[i+2]))

            return colors

        return []

    def analyze_brightness(self, image_path: str) -> float:
        """
        Analysiert die Helligkeit eines Bildes.

        Returns:
            Helligkeit von 0.0 (dunkel) bis 1.0 (hell)
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return 0.5

        img_type, img = img_data

        if img_type == "cv2":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray) / 255.0
            return round(brightness, 3)

        elif img_type == "pil":
            gray = img.convert('L')
            stat = ImageStat.Stat(gray)
            brightness = stat.mean[0] / 255.0
            return round(brightness, 3)

        return 0.5

    def analyze_contrast(self, image_path: str) -> float:
        """
        Analysiert den Kontrast eines Bildes.

        Returns:
            Kontrast von 0.0 (niedrig) bis 1.0 (hoch)
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return 0.5

        img_type, img = img_data

        if img_type == "cv2":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            contrast = np.std(gray) / 128.0  # Normalisiert
            return round(min(1.0, contrast), 3)

        elif img_type == "pil":
            gray = img.convert('L')
            stat = ImageStat.Stat(gray)
            contrast = stat.stddev[0] / 128.0
            return round(min(1.0, contrast), 3)

        return 0.5

    def analyze_saturation(self, image_path: str) -> float:
        """
        Analysiert die Sättigung eines Bildes.

        Returns:
            Sättigung von 0.0 (grau) bis 1.0 (lebendig)
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return 0.5

        img_type, img = img_data

        if img_type == "cv2":
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            return round(saturation, 3)

        elif img_type == "pil":
            hsv = img.convert('HSV')
            stat = ImageStat.Stat(hsv)
            saturation = stat.mean[1] / 255.0
            return round(saturation, 3)

        return 0.5

    def detect_faces(self, image_path: str) -> int:
        """
        Erkennt Gesichter in einem Bild.

        Returns:
            Anzahl der erkannten Gesichter
        """
        if not self.has_cv2 or self.face_cascade is None:
            logger.warning("Gesichtserkennung nicht verfügbar")
            return 0

        img_data = self._load_image(image_path)
        if not img_data or img_data[0] != "cv2":
            return 0

        img = img_data[1]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        return len(faces)

    def detect_objects(self, image_path: str) -> List[str]:
        """
        Erkennt Objekte in einem Bild (benötigt YOLO).

        Returns:
            Liste der erkannten Objekte
        """
        if self.yolo_net is None:
            logger.debug("YOLO nicht verfügbar")
            return []

        img_data = self._load_image(image_path)
        if not img_data or img_data[0] != "cv2":
            return []

        img = img_data[1]
        height, width = img.shape[:2]

        # YOLO Inferenz
        blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.yolo_net.setInput(blob)

        layer_names = self.yolo_net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]
        outputs = self.yolo_net.forward(output_layers)

        detected = []
        confidence_threshold = 0.5

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = int(np.argmax(scores))
                confidence = scores[class_id]

                if confidence > confidence_threshold:
                    if class_id < len(self.yolo_classes):
                        detected.append(self.yolo_classes[class_id])

        return list(set(detected))

    def determine_color_mood(self, dominant_colors: List[Tuple[int, int, int]]) -> ColorMood:
        """Bestimmt die Farbstimmung basierend auf dominanten Farben"""
        if not dominant_colors:
            return ColorMood.NEUTRAL

        # Analysiere erste Farbe
        r, g, b = dominant_colors[0]

        # Helligkeit
        brightness = (r + g + b) / 765.0  # 0-1

        # Sättigung (vereinfacht)
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        saturation = (max_c - min_c) / max(max_c, 1)

        # Wärme (rot/gelb vs blau)
        warmth = (r + g * 0.5) / (b + 1)

        if brightness < 0.3:
            return ColorMood.DARK
        elif brightness > 0.8:
            return ColorMood.BRIGHT
        elif saturation < 0.2:
            return ColorMood.MUTED
        elif saturation > 0.7:
            return ColorMood.VIBRANT
        elif warmth > 1.5:
            return ColorMood.WARM
        elif warmth < 0.7:
            return ColorMood.COLD

        return ColorMood.NEUTRAL

    def determine_image_type(self, image_path: str) -> ImageType:
        """Bestimmt den Bildtyp basierend auf Analyse"""
        img_data = self._load_image(image_path)
        if not img_data:
            return ImageType.UNKNOWN

        img_type, img = img_data

        # Dimensionen
        if img_type == "cv2":
            height, width = img.shape[:2]
        else:
            width, height = img.size

        aspect_ratio = width / max(height, 1)

        # Gesichtserkennung
        face_count = self.detect_faces(image_path)

        # Bestimme Typ
        if face_count >= 1 and aspect_ratio < 1.5:
            return ImageType.PORTRAIT
        elif aspect_ratio > 1.5:
            return ImageType.LANDSCAPE
        elif aspect_ratio == 1.0:
            return ImageType.PHOTO

        # Prüfe auf Screenshot (typische Bildschirmgrößen)
        common_resolutions = [(1920, 1080), (1280, 720), (1366, 768), (2560, 1440)]
        for res in common_resolutions:
            if (width, height) == res or (height, width) == res:
                return ImageType.SCREENSHOT

        return ImageType.PHOTO

    def generate_emotional_impression(self, brightness: float, saturation: float,
                                      color_mood: ColorMood, face_count: int) -> Dict[str, float]:
        """Generiert emotionalen Eindruck aus Bildmerkmalen"""
        impression = {
            "freude": 0.0,
            "ruhe": 0.0,
            "energie": 0.0,
            "melancholie": 0.0,
            "wärme": 0.0,
            "mysterium": 0.0,
        }

        # Helligkeit
        if brightness > 0.6:
            impression["freude"] += 0.3
            impression["energie"] += 0.2
        elif brightness < 0.3:
            impression["melancholie"] += 0.3
            impression["mysterium"] += 0.2

        # Sättigung
        if saturation > 0.6:
            impression["energie"] += 0.3
            impression["freude"] += 0.2
        elif saturation < 0.3:
            impression["ruhe"] += 0.3

        # Farbstimmung
        if color_mood == ColorMood.WARM:
            impression["wärme"] += 0.4
            impression["freude"] += 0.2
        elif color_mood == ColorMood.COLD:
            impression["ruhe"] += 0.3
            impression["melancholie"] += 0.2
        elif color_mood == ColorMood.VIBRANT:
            impression["energie"] += 0.4
        elif color_mood == ColorMood.DARK:
            impression["mysterium"] += 0.4
            impression["melancholie"] += 0.2

        # Gesichter
        if face_count > 0:
            impression["wärme"] += 0.2

        # Normalisieren
        for key in impression:
            impression[key] = min(1.0, impression[key])

        return impression

    def generate_description(self, analysis: 'ImageAnalysisResult') -> str:
        """Generiert eine Beschreibung des Bildes"""
        parts = []

        # Komposition
        if analysis.image_type == ImageType.PORTRAIT:
            parts.append("Ein Porträtbild")
        elif analysis.image_type == ImageType.LANDSCAPE:
            parts.append("Eine Landschaftsaufnahme")
        else:
            parts.append("Ein Bild")

        # Farben
        if analysis.color_names:
            main_colors = analysis.color_names[:3]
            parts.append(f"mit {', '.join(main_colors)} Tönen")

        # Stimmung
        mood_text = {
            ColorMood.WARM: "warmer Atmosphäre",
            ColorMood.COLD: "kühler Stimmung",
            ColorMood.VIBRANT: "lebhaften Farben",
            ColorMood.MUTED: "gedämpften Tönen",
            ColorMood.DARK: "dunkler Atmosphäre",
            ColorMood.BRIGHT: "heller Ausstrahlung",
        }
        if analysis.color_mood in mood_text:
            parts.append(f"und {mood_text[analysis.color_mood]}")

        # Gesichter
        if analysis.face_count == 1:
            parts.append(", das eine Person zeigt")
        elif analysis.face_count > 1:
            parts.append(f", das {analysis.face_count} Personen zeigt")

        # Objekte
        if analysis.detected_objects:
            objects = analysis.detected_objects[:3]
            parts.append(f". Erkannte Objekte: {', '.join(objects)}")

        return " ".join(parts) + "."

    def analyze_image(self, image_path: str) -> Optional[ImageAnalysisResult]:
        """
        Führt eine vollständige Bildanalyse durch.

        Args:
            image_path: Pfad zum Bild

        Returns:
            ImageAnalysisResult mit allen Analyseergebnissen
        """
        if not os.path.exists(image_path):
            logger.error(f"Bild nicht gefunden: {image_path}")
            return None

        if not self.has_cv2 and not self.has_pil:
            logger.error("Weder OpenCV noch PIL verfügbar")
            return None

        image_id = self._generate_image_id(image_path)

        # Lade Bild für Dimensionen
        img_data = self._load_image(image_path)
        if not img_data:
            return None

        img_type, img = img_data

        if img_type == "cv2":
            height, width = img.shape[:2]
        else:
            width, height = img.size

        # Analysiere
        dominant_colors = self.get_dominant_colors(image_path)
        color_names = [self._get_closest_color_name(c) for c in dominant_colors]
        brightness = self.analyze_brightness(image_path)
        contrast = self.analyze_contrast(image_path)
        saturation = self.analyze_saturation(image_path)
        color_mood = self.determine_color_mood(dominant_colors)
        face_count = self.detect_faces(image_path)
        detected_objects = self.detect_objects(image_path)
        image_type = self.determine_image_type(image_path)

        # Komposition
        aspect_ratio = width / max(height, 1)
        if aspect_ratio > 1.2:
            composition = "landscape"
        elif aspect_ratio < 0.8:
            composition = "portrait"
        else:
            composition = "square"

        # Emotionaler Eindruck
        emotional_impression = self.generate_emotional_impression(
            brightness, saturation, color_mood, face_count
        )

        result = ImageAnalysisResult(
            image_id=image_id,
            image_type=image_type,
            width=width,
            height=height,
            aspect_ratio=round(aspect_ratio, 2),
            dominant_colors=dominant_colors,
            color_names=color_names,
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            color_mood=color_mood,
            face_count=face_count,
            detected_objects=detected_objects,
            composition=composition,
            emotional_impression=emotional_impression,
            description="",  # Wird unten gefüllt
        )

        # Generiere Beschreibung
        result.description = self.generate_description(result)

        logger.info(f"Bild analysiert: {width}x{height}, {len(dominant_colors)} Farben, "
                   f"{face_count} Gesichter, Stimmung: {color_mood.value}")

        return result


# =============================================================================
# HOLO PERCEPTION - Unified Interface
# =============================================================================

class HoloPerception:
    """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║  HOLO PERCEPTION - Vereinigtes Wahrnehmungssystem                     ║
    ║                                                                       ║
    ║  Kombiniert HoloReader und HoloVision für eine einheitliche           ║
    ║  Schnittstelle zur Wahrnehmung von Text und Bild.                     ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def __init__(self, data_dir: str = "data", models_dir: str = "models"):
        self.reader = HoloReader(data_dir=f"{data_dir}/reading")
        self.vision = HoloVision(models_dir=models_dir)

        logger.info("HoloPerception initialisiert")
        logger.info(f"  - OpenCV: {'verfügbar' if _HAS_CV2 else 'nicht verfügbar'}")
        logger.info(f"  - PIL: {'verfügbar' if _HAS_PIL else 'nicht verfügbar'}")
        logger.info(f"  - YOLO: {'verfügbar' if self.vision.yolo_net else 'nicht verfügbar'}")

    def read_text(self, text: str, title: str = None) -> TextAnalysisResult:
        """Analysiert einen Text"""
        return self.reader.analyze_text(text, title)

    def see_image(self, image_path: str) -> Optional[ImageAnalysisResult]:
        """Analysiert ein Bild"""
        return self.vision.analyze_image(image_path)

    def get_emotional_response(self, text: str = None, image_path: str = None) -> Dict[str, float]:
        """
        Kombiniert emotionale Reaktionen aus Text und/oder Bild.

        Returns:
            Kombinierte emotionale Reaktion
        """
        combined = defaultdict(float)
        count = 0

        if text:
            text_emotions = self.reader.calculate_emotional_response(text)
            for emotion, value in text_emotions.items():
                combined[emotion] += value
            count += 1

        if image_path and os.path.exists(image_path):
            image_result = self.vision.analyze_image(image_path)
            if image_result:
                for emotion, value in image_result.emotional_impression.items():
                    combined[emotion] += value
                count += 1

        # Durchschnitt
        if count > 0:
            for key in combined:
                combined[key] /= count

        return dict(combined)

    def start_reading(self, text: str, title: str = "Unbenannt") -> ReadingProgress:
        """Startet das Lesen eines Textes"""
        return self.reader.start_reading(text, title)

    def get_reading_progress(self, text_id: str) -> Optional[ReadingProgress]:
        """Gibt den Lesefortschritt zurück"""
        return self.reader.get_reading_progress(text_id)

    def get_capabilities(self) -> Dict[str, bool]:
        """Gibt die verfügbaren Fähigkeiten zurück"""
        return {
            "text_analysis": True,
            "sentiment_analysis": True,
            "keyword_extraction": True,
            "summarization": True,
            "image_analysis": _HAS_CV2 or _HAS_PIL,
            "color_analysis": _HAS_CV2 or _HAS_PIL,
            "face_detection": _HAS_CV2 and self.vision.face_cascade is not None,
            "object_detection": self.vision.yolo_net is not None,
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO PERCEPTION TEST")
    print("=" * 60)

    perception = HoloPerception()

    # Capabilities
    print("\nVerfügbare Fähigkeiten:")
    for cap, available in perception.get_capabilities().items():
        status = "✓" if available else "✗"
        print(f"  {status} {cap}")

    # Text-Analyse Test
    print("\n" + "-" * 40)
    print("TEXT-ANALYSE TEST")
    print("-" * 40)

    test_text = """
    Es war ein wunderschöner Sommertag, als Maria durch den Park spazierte.
    Die Sonne schien warm auf ihr Gesicht und die Vögel sangen fröhlich in den Bäumen.
    Sie fühlte sich glücklich und zufrieden mit ihrem Leben.
    Plötzlich sah sie ihren alten Freund Thomas, der auf einer Bank saß und las.
    "Hallo Thomas!", rief sie begeistert. "Was für eine Überraschung, dich hier zu treffen!"
    Thomas schaute auf und lächelte. "Maria! Wie schön, dich zu sehen!"
    Sie setzten sich zusammen und sprachen über alte Zeiten, über Hoffnungen und Träume.
    Es war ein perfekter Moment des Friedens und der Freundschaft.
    """

    result = perception.read_text(test_text, "Ein Sommertag")

    print(f"\nTexttyp: {result.text_type.name}")
    print(f"Wörter: {result.word_count}")
    print(f"Sätze: {result.sentence_count}")
    print(f"Sentiment: {result.sentiment:.2f} ({result.sentiment_label})")
    print(f"Komplexität: {result.complexity_score:.2f}")
    print(f"Lesezeit: {result.reading_time_minutes:.1f} Minuten")
    print(f"\nSchlüsselwörter: {', '.join(result.keywords[:5])}")
    print(f"\nZusammenfassung:\n{result.summary}")
    print(f"\nEmotionale Reaktion:")
    for emotion, value in sorted(result.emotional_response.items(), key=lambda x: -x[1]):
        if value > 0:
            print(f"  {emotion}: {'█' * int(value * 10)} {value:.2f}")

    print("\n" + "=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)
