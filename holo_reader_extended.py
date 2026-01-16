#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloReader Extended v2.0 - Erweiterte Text-Analyse

FEATURES (Standalone + LLM-erweitert):
- Kapitel-Erkennung: Automatisch Kapitel/Abschnitte in Buechern erkennen
- Zitat-Extraktion: Wichtige Zitate aus Texten herausziehen
- Lesbarkeits-Index: Flesch-Reading-Ease fuer Deutsch
- Stil-Analyse: Schreibstil erkennen (formell, casual, poetisch)
- Themen-Clustering: Aehnliche Texte gruppieren
- Fragen generieren: Verstaendnisfragen zum Text erstellen (+ LLM)
- Fakten-Extraktion: Konkrete Fakten (Zahlen, Daten) extrahieren
- Vergleichs-Analyse: Zwei Texte vergleichen

HYBRID-SYSTEM:
- Funktioniert vollstaendig ohne LLM (Standalone)
- Optionale LLM-Erweiterung fuer bessere Ergebnisse
- Automatische Erkennung ob LLM verfuegbar

Author: Kira & Claude
Version: 2.0
"""

import re
import math
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum, auto

logger = logging.getLogger("HoloReaderExtended")


# =============================================================================
# ENUMS UND DATACLASSES
# =============================================================================

class WritingStyle(Enum):
    """Schreibstil-Typen"""
    FORMAL = "formell"
    CASUAL = "casual"
    POETIC = "poetisch"
    TECHNICAL = "technisch"
    JOURNALISTIC = "journalistisch"
    NARRATIVE = "narrativ"
    ACADEMIC = "akademisch"
    CONVERSATIONAL = "konversationell"


class ChapterType(Enum):
    """Kapitel-Typen"""
    NUMBERED = "nummeriert"
    NAMED = "benannt"
    SECTION = "abschnitt"
    PART = "teil"
    PROLOGUE = "prolog"
    EPILOGUE = "epilog"


@dataclass
class Chapter:
    """Ein erkanntes Kapitel"""
    chapter_id: str
    chapter_type: ChapterType
    title: str
    number: Optional[int]
    start_position: int
    end_position: int
    word_count: int
    content_preview: str  # Erste 200 Zeichen


@dataclass
class Quote:
    """Ein extrahiertes Zitat"""
    quote_id: str
    text: str
    speaker: Optional[str]
    context: str  # Text drumherum
    position: int
    importance_score: float  # 0-1
    quote_type: str  # "dialogue", "citation", "emphasis"


@dataclass
class ReadabilityResult:
    """Ergebnis der Lesbarkeits-Analyse"""
    flesch_score: float  # 0-100
    flesch_grade: str  # "sehr leicht" bis "sehr schwer"
    avg_sentence_length: float
    avg_syllables_per_word: float
    long_word_ratio: float  # Woerter > 6 Silben
    vocabulary_richness: float  # Type-Token-Ratio
    suggested_audience: str  # "Kinder", "Erwachsene", "Fachpublikum"


@dataclass
class StyleAnalysisResult:
    """Ergebnis der Stil-Analyse"""
    primary_style: WritingStyle
    style_scores: Dict[str, float]  # Score pro Stil
    formality_score: float  # 0 (casual) bis 1 (formal)
    emotionality_score: float  # 0 (sachlich) bis 1 (emotional)
    complexity_score: float  # 0 (einfach) bis 1 (komplex)
    distinctive_features: List[str]  # Auffaellige Merkmale


@dataclass
class TopicCluster:
    """Ein Themen-Cluster"""
    cluster_id: str
    main_topic: str
    keywords: List[str]
    texts: List[str]  # Text-IDs in diesem Cluster
    coherence_score: float  # 0-1


@dataclass
class GeneratedQuestion:
    """Eine generierte Verstaendnisfrage"""
    question: str
    question_type: str  # "wer", "was", "warum", "wie", "wann", "wo"
    difficulty: str  # "leicht", "mittel", "schwer"
    related_sentence: str
    expected_answer_keywords: List[str]


@dataclass
class ExtractedFact:
    """Ein extrahierter Fakt"""
    fact_id: str
    fact_type: str  # "zahl", "datum", "prozent", "name", "ort", "ereignis"
    value: str
    context: str
    confidence: float  # 0-1
    position: int


@dataclass
class TextComparisonResult:
    """Ergebnis eines Text-Vergleichs"""
    similarity_score: float  # 0-1 (Jaccard/Cosine)
    common_keywords: List[str]
    unique_to_text1: List[str]
    unique_to_text2: List[str]
    style_similarity: float  # 0-1
    topic_overlap: float  # 0-1
    sentiment_difference: float  # -2 bis +2
    summary: str


# =============================================================================
# HOLOREADER EXTENDED
# =============================================================================

class HoloReaderExtended:
    """
    Erweiterte Text-Analyse-Funktionen fuer HoloReader.

    HYBRID-SYSTEM:
    - Alle Features funktionieren standalone ohne LLM
    - Optionale LLM-Erweiterung fuer bessere Ergebnisse
    - use_llm=True aktiviert LLM wenn verfuegbar

    Features:
    - Kapitel-Erkennung
    - Zitat-Extraktion
    - Lesbarkeits-Index (Flesch fuer Deutsch)
    - Stil-Analyse
    - Themen-Clustering
    - Fragen generieren (+ LLM)
    - Fakten-Extraktion
    - Vergleichs-Analyse (+ LLM)
    """

    def __init__(self, use_llm: bool = False, llm_instance=None):
        """
        Initialisiert HoloReaderExtended.

        Args:
            use_llm: Aktiviert LLM-Erweiterung wenn verfuegbar
            llm_instance: Optionale UnifiedLLM Instanz
        """
        self._init_german_syllables()
        self._init_style_indicators()
        self._init_question_patterns()
        self._init_fact_patterns()
        self._init_stopwords()

        # Cache fuer Clustering
        self._text_vectors: Dict[str, Dict[str, float]] = {}
        self._clusters: List[TopicCluster] = []

        # LLM Integration
        self.use_llm = use_llm
        self.llm = llm_instance
        self._llm_available = False

        if use_llm:
            self._init_llm()

        logger.info(f"HoloReaderExtended initialisiert (LLM: {self._llm_available})")

    def _init_llm(self):
        """Initialisiert LLM-Verbindung"""
        if self.llm is not None:
            self._llm_available = True
            return

        try:
            from smart_llm_system import UnifiedLLM
            self.llm = UnifiedLLM()
            self._llm_available = True
            logger.info("LLM-Verbindung hergestellt")
        except Exception as e:
            logger.warning(f"LLM nicht verfuegbar: {e}")
            self._llm_available = False

    def _query_llm(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Sendet Anfrage an LLM (wenn verfuegbar)"""
        if not self._llm_available or self.llm is None:
            return None

        try:
            result = self.llm.query(
                prompt=prompt,
                system_prompt=system_prompt,
                intent="analysis"
            )
            return result.get("response")
        except Exception as e:
            logger.error(f"LLM-Anfrage fehlgeschlagen: {e}")
            return None

    # =========================================================================
    # INITIALISIERUNG
    # =========================================================================

    def _init_german_syllables(self):
        """Initialisiert Silben-Zaehlung fuer Deutsch"""
        self.vowels = set("aeiouaeoeueAEIOUAeOeUe")
        self.diphthongs = ["ei", "ai", "au", "eu", "ae", "ie", "oe", "ue"]

    def _init_style_indicators(self):
        """Initialisiert Stil-Indikatoren"""
        self.formal_indicators = {
            "daher", "folglich", "demzufolge", "infolgedessen", "mithin",
            "diesbezueglich", "hinsichtlich", "bezueglich", "gemaess",
            "entsprechend", "aufgrund", "indem", "sofern", "insofern",
            "jedoch", "dennoch", "gleichwohl", "nichtsdestotrotz"
        }

        self.casual_indicators = {
            "halt", "eben", "einfach", "irgendwie", "quasi", "sozusagen",
            "ja", "ne", "naja", "okay", "cool", "krass", "mega", "voll",
            "eigentlich", "praktisch", "total", "echt", "super"
        }

        self.poetic_indicators = {
            "gleich", "wie", "als ob", "sanft", "zart", "leuchtend",
            "schimmernd", "fluestern", "hauchen", "sehnsucht", "ewigkeit",
            "traum", "seele", "herz", "schatten", "licht", "dunkel"
        }

        self.technical_indicators = {
            "parameter", "funktion", "system", "prozess", "algorithmus",
            "variable", "methode", "implementierung", "struktur", "modul",
            "konfiguration", "instanz", "objekt", "schnittstelle"
        }

        self.academic_indicators = {
            "hypothese", "these", "analyse", "studie", "forschung",
            "ergebnis", "methodik", "theorie", "modell", "paradigma",
            "diskurs", "kontext", "implikation", "signifikant"
        }

    def _init_question_patterns(self):
        """Initialisiert Muster fuer Fragen-Generierung"""
        self.question_templates = {
            "wer": [
                "Wer {verb} {objekt}?",
                "Von wem wird {objekt} {verb}?",
                "Wer ist {subjekt}?"
            ],
            "was": [
                "Was {verb} {subjekt}?",
                "Was passiert mit {objekt}?",
                "Was bedeutet {konzept}?"
            ],
            "warum": [
                "Warum {verb} {subjekt} {objekt}?",
                "Aus welchem Grund {verb} {subjekt}?",
                "Was ist der Grund fuer {ereignis}?"
            ],
            "wie": [
                "Wie {verb} {subjekt} {objekt}?",
                "Auf welche Weise {verb} {subjekt}?",
                "Wie wird {konzept} beschrieben?"
            ],
            "wann": [
                "Wann {verb} {ereignis}?",
                "Zu welchem Zeitpunkt {verb} {subjekt}?",
                "In welchem Jahr {verb} {ereignis}?"
            ],
            "wo": [
                "Wo {verb} {ereignis}?",
                "An welchem Ort {verb} {subjekt}?",
                "Wo befindet sich {objekt}?"
            ]
        }

    def _init_fact_patterns(self):
        """Initialisiert Muster fuer Fakten-Extraktion"""
        self.fact_patterns = {
            "zahl": [
                r'\b(\d+(?:\.\d+)?)\s*(million|milliarde|tausend|prozent|%|euro|dollar|km|meter|kg|gramm|liter|jahr|jahre|monat|monate|tag|tage)\b',
                r'\b(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\b'
            ],
            "datum": [
                r'\b(\d{1,2})\.\s*(januar|februar|maerz|april|mai|juni|juli|august|september|oktober|november|dezember)\s*(\d{4})\b',
                r'\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b',
                r'\b(im\s+jahr\s+\d{4})\b',
                r'\b(\d{4})\b'  # Jahreszahlen
            ],
            "prozent": [
                r'(\d+(?:,\d+)?)\s*(?:prozent|%)',
                r'(\d+(?:,\d+)?)\s*von\s*(\d+)'
            ],
            "name": [
                r'\b([A-ZAEOEUE][a-zaeoeue]+(?:\s+[A-ZAEOEUE][a-zaeoeue]+)+)\b'
            ],
            "ort": [
                r'\b(?:in|aus|nach|bei)\s+([A-ZAEOEUE][a-zaeoeue]+(?:\s+[A-ZAEOEUE][a-zaeoeue]+)*)\b'
            ]
        }

    def _init_stopwords(self):
        """Initialisiert Stopwords"""
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "einer", "eines", "einem",
            "und", "oder", "aber", "doch", "jedoch", "sondern", "sowie",
            "ist", "sind", "war", "waren", "sein", "wird", "werden",
            "hat", "haben", "hatte", "hatten", "kann", "koennen", "konnte",
            "muss", "muessen", "musste", "soll", "sollen", "sollte",
            "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich",
            "mir", "dir", "sich", "uns", "euch", "ihm", "ihr", "ihnen",
            "den", "dem", "des", "im", "in", "an", "auf", "fuer", "mit",
            "bei", "zu", "von", "aus", "nach", "ueber", "unter", "vor",
            "nicht", "auch", "noch", "schon", "nur", "sehr", "so", "wie",
        }

    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================

    def _count_syllables(self, word: str) -> int:
        """Zaehlt Silben in einem deutschen Wort"""
        word = word.lower()
        if len(word) <= 3:
            return 1

        syllables = 0
        prev_vowel = False

        i = 0
        while i < len(word):
            # Pruefe auf Diphthonge
            if i < len(word) - 1:
                digraph = word[i:i+2]
                if digraph in self.diphthongs:
                    if not prev_vowel:
                        syllables += 1
                    prev_vowel = True
                    i += 2
                    continue

            if word[i] in self.vowels:
                if not prev_vowel:
                    syllables += 1
                prev_vowel = True
            else:
                prev_vowel = False
            i += 1

        return max(1, syllables)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiert Text in Woerter"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [w for w in text.split() if len(w) > 1]

    def _get_sentences(self, text: str) -> List[str]:
        """Extrahiert Saetze aus Text"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    def _generate_id(self, content: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _get_text_vector(self, text: str) -> Dict[str, float]:
        """Erstellt TF-Vektor fuer Text"""
        words = self._tokenize(text)
        words = [w for w in words if w not in self.stopwords]

        word_count = Counter(words)
        total = len(words)

        return {word: count / total for word, count in word_count.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Berechnet Kosinus-Aehnlichkeit"""
        common_keys = set(vec1.keys()) & set(vec2.keys())

        if not common_keys:
            return 0.0

        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    # =========================================================================
    # KAPITEL-ERKENNUNG
    # =========================================================================

    def detect_chapters(self, text: str) -> List[Chapter]:
        """
        Erkennt Kapitel und Abschnitte in einem Text.

        Sucht nach:
        - "Kapitel 1", "Kapitel I", "Chapter 1"
        - "1.", "1)", "I."
        - "Prolog", "Epilog"
        - Ueberschriften-artige Zeilen (kurz, evtl. GROSSBUCHSTABEN)
        """
        chapters = []
        lines = text.split('\n')

        # Kapitel-Muster
        patterns = {
            ChapterType.NUMBERED: [
                r'^(?:kapitel|chapter)\s+(\d+|[ivxlc]+)[\s:.-]*(.*)$',
                r'^(\d+)[\.\)]\s+(.+)$',
            ],
            ChapterType.NAMED: [
                r'^([A-ZAEOEUE][A-ZAEOEUE\s]{10,})$',  # GROSSBUCHSTABEN
            ],
            ChapterType.PROLOGUE: [
                r'^(?:prolog|einleitung|vorwort)[\s:.-]*(.*)$',
            ],
            ChapterType.EPILOGUE: [
                r'^(?:epilog|nachwort|schlusswort)[\s:.-]*(.*)$',
            ],
            ChapterType.PART: [
                r'^(?:teil|part)\s+(\d+|[ivxlc]+)[\s:.-]*(.*)$',
            ],
        }

        current_pos = 0
        chapter_starts = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                current_pos += len(line) + 1
                continue

            for chapter_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.match(pattern, line_stripped, re.IGNORECASE)
                    if match:
                        title = match.group(1) if match.lastindex >= 1 else line_stripped
                        number = None

                        # Extrahiere Nummer wenn vorhanden
                        if chapter_type in [ChapterType.NUMBERED, ChapterType.PART]:
                            try:
                                number = int(match.group(1))
                            except ValueError:
                                # Roemische Zahl
                                roman = match.group(1).upper()
                                roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
                                try:
                                    number = sum(roman_map.get(c, 0) for c in roman)
                                except Exception:
                                    pass  # Invalid roman numeral, keep number as None

                        chapter_starts.append({
                            'type': chapter_type,
                            'title': title,
                            'number': number,
                            'position': current_pos,
                            'line': i
                        })
                        break

            current_pos += len(line) + 1

        # Erstelle Chapter-Objekte mit End-Positionen
        for i, start in enumerate(chapter_starts):
            end_pos = chapter_starts[i + 1]['position'] if i < len(chapter_starts) - 1 else len(text)
            content = text[start['position']:end_pos]
            words = self._tokenize(content)

            chapter = Chapter(
                chapter_id=self._generate_id(start['title'] + str(start['position'])),
                chapter_type=start['type'],
                title=start['title'],
                number=start['number'],
                start_position=start['position'],
                end_position=end_pos,
                word_count=len(words),
                content_preview=content[:200].replace('\n', ' ')
            )
            chapters.append(chapter)

        logger.info(f"Kapitel erkannt: {len(chapters)}")
        return chapters

    # =========================================================================
    # ZITAT-EXTRAKTION
    # =========================================================================

    def extract_quotes(self, text: str, min_length: int = 10) -> List[Quote]:
        """
        Extrahiert Zitate aus einem Text.

        Erkennt:
        - Direkte Rede ("...", '...')
        - Zitate mit Anfuehrungszeichen
        - Hervorgehobene Saetze
        """
        quotes = []

        # Muster fuer verschiedene Anfuehrungszeichen
        quote_patterns = [
            (r'"([^"]+)"', "dialogue"),
            (r'"([^"]+)"', "dialogue"),
            (r'„([^"]+)"', "dialogue"),
            (r"'([^']+)'", "emphasis"),
            (r'»([^«]+)«', "citation"),
            (r'«([^»]+)»', "citation"),
        ]

        for pattern, quote_type in quote_patterns:
            for match in re.finditer(pattern, text):
                quote_text = match.group(1).strip()

                if len(quote_text) < min_length:
                    continue

                # Kontext extrahieren (50 Zeichen vor und nach)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')

                # Sprecher erkennen (fuer direkte Rede)
                speaker = None
                if quote_type == "dialogue":
                    # Suche nach "sagte X", "X sagte" etc.
                    speaker_pattern = r'(?:sagte|fragte|rief|antwortete|meinte|erklaerte)\s+([A-ZAEOEUE][a-zaeoeue]+)'
                    speaker_match = re.search(speaker_pattern, context)
                    if speaker_match:
                        speaker = speaker_match.group(1)

                # Wichtigkeit berechnen (laengere Zitate sind oft wichtiger)
                importance = min(1.0, len(quote_text) / 200)

                # Bonus fuer Zitate mit Sprecher
                if speaker:
                    importance = min(1.0, importance + 0.2)

                quote = Quote(
                    quote_id=self._generate_id(quote_text),
                    text=quote_text,
                    speaker=speaker,
                    context=context,
                    position=match.start(),
                    importance_score=round(importance, 2),
                    quote_type=quote_type
                )
                quotes.append(quote)

        # Sortiere nach Wichtigkeit
        quotes.sort(key=lambda q: q.importance_score, reverse=True)

        logger.info(f"Zitate extrahiert: {len(quotes)}")
        return quotes

    # =========================================================================
    # LESBARKEITS-INDEX (FLESCH FUER DEUTSCH)
    # =========================================================================

    def calculate_readability(self, text: str) -> ReadabilityResult:
        """
        Berechnet den Flesch-Reading-Ease fuer deutschen Text.

        Formel (Amstad): 180 - ASL - (58.5 * ASW)
        ASL = Durchschnittliche Satzlaenge
        ASW = Durchschnittliche Silben pro Wort

        Score-Interpretation:
        - 100-80: Sehr leicht (Grundschule)
        - 80-60: Leicht (Mittelstufe)
        - 60-40: Mittelschwer (Oberstufe)
        - 40-20: Schwer (Hochschule)
        - 20-0: Sehr schwer (Akademisch)
        """
        words = self._tokenize(text)
        sentences = self._get_sentences(text)

        if not words or not sentences:
            return ReadabilityResult(
                flesch_score=0.0,
                flesch_grade="nicht berechenbar",
                avg_sentence_length=0.0,
                avg_syllables_per_word=0.0,
                long_word_ratio=0.0,
                vocabulary_richness=0.0,
                suggested_audience="unbekannt"
            )

        # Durchschnittliche Satzlaenge
        asl = len(words) / len(sentences)

        # Durchschnittliche Silben pro Wort
        total_syllables = sum(self._count_syllables(w) for w in words)
        asw = total_syllables / len(words)

        # Flesch-Score (Amstad-Formel fuer Deutsch)
        flesch = 180 - asl - (58.5 * asw)
        flesch = max(0, min(100, flesch))

        # Grade bestimmen
        if flesch >= 80:
            grade = "sehr leicht"
            audience = "Kinder, Anfaenger"
        elif flesch >= 60:
            grade = "leicht"
            audience = "Schueler, breite Oeffentlichkeit"
        elif flesch >= 40:
            grade = "mittelschwer"
            audience = "Oberstufe, interessierte Laien"
        elif flesch >= 20:
            grade = "schwer"
            audience = "Studenten, Fachpublikum"
        else:
            grade = "sehr schwer"
            audience = "Akademiker, Experten"

        # Lange Woerter (>= 4 Silben)
        long_words = [w for w in words if self._count_syllables(w) >= 4]
        long_word_ratio = len(long_words) / len(words)

        # Vokabular-Reichtum (Type-Token-Ratio)
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / len(words)

        return ReadabilityResult(
            flesch_score=round(flesch, 1),
            flesch_grade=grade,
            avg_sentence_length=round(asl, 1),
            avg_syllables_per_word=round(asw, 2),
            long_word_ratio=round(long_word_ratio, 3),
            vocabulary_richness=round(vocabulary_richness, 3),
            suggested_audience=audience
        )

    # =========================================================================
    # STIL-ANALYSE
    # =========================================================================

    def analyze_style(self, text: str) -> StyleAnalysisResult:
        """
        Analysiert den Schreibstil eines Textes.

        Erkennt:
        - Formell vs. Casual
        - Poetisch
        - Technisch
        - Journalistisch
        - Akademisch
        """
        words = self._tokenize(text)
        word_set = set(words)
        sentences = self._get_sentences(text)

        if not words:
            return StyleAnalysisResult(
                primary_style=WritingStyle.CASUAL,
                style_scores={},
                formality_score=0.5,
                emotionality_score=0.5,
                complexity_score=0.5,
                distinctive_features=[]
            )

        # Style Scores berechnen
        style_scores = {}

        # Formal Score
        formal_count = len(word_set & self.formal_indicators)
        style_scores["formell"] = min(1.0, formal_count / 5)

        # Casual Score
        casual_count = len(word_set & self.casual_indicators)
        style_scores["casual"] = min(1.0, casual_count / 5)

        # Poetic Score
        poetic_count = len(word_set & self.poetic_indicators)
        style_scores["poetisch"] = min(1.0, poetic_count / 5)

        # Technical Score
        tech_count = len(word_set & self.technical_indicators)
        style_scores["technisch"] = min(1.0, tech_count / 5)

        # Academic Score
        academic_count = len(word_set & self.academic_indicators)
        style_scores["akademisch"] = min(1.0, academic_count / 5)

        # Narrative Score (Dialog-Anteil)
        dialogue_markers = text.count('"') + text.count('"') + text.count('„')
        style_scores["narrativ"] = min(1.0, dialogue_markers / 20)

        # Journalistic Score (kurze Saetze, aktive Sprache)
        avg_sent_len = len(words) / max(len(sentences), 1)
        style_scores["journalistisch"] = 1.0 - min(1.0, avg_sent_len / 25)

        # Primaeren Stil bestimmen
        max_style = max(style_scores, key=style_scores.get)
        style_map = {
            "formell": WritingStyle.FORMAL,
            "casual": WritingStyle.CASUAL,
            "poetisch": WritingStyle.POETIC,
            "technisch": WritingStyle.TECHNICAL,
            "akademisch": WritingStyle.ACADEMIC,
            "narrativ": WritingStyle.NARRATIVE,
            "journalistisch": WritingStyle.JOURNALISTIC,
        }
        primary_style = style_map.get(max_style, WritingStyle.CASUAL)

        # Formality Score (formal vs casual)
        formality = (style_scores.get("formell", 0) + style_scores.get("akademisch", 0)) / 2
        formality -= style_scores.get("casual", 0) / 2
        formality = max(0, min(1, formality + 0.5))

        # Emotionality (poetisch + narrativ)
        emotionality = (style_scores.get("poetisch", 0) + style_scores.get("narrativ", 0)) / 2

        # Complexity (akademisch + technisch + Satzlaenge)
        complexity = (style_scores.get("akademisch", 0) + style_scores.get("technisch", 0)) / 2
        complexity += min(1.0, avg_sent_len / 30) * 0.5
        complexity = min(1.0, complexity)

        # Distinctive Features
        features = []
        if style_scores.get("formell", 0) > 0.5:
            features.append("Formelle Sprache")
        if style_scores.get("casual", 0) > 0.5:
            features.append("Umgangssprachlich")
        if style_scores.get("poetisch", 0) > 0.3:
            features.append("Poetische Elemente")
        if style_scores.get("technisch", 0) > 0.4:
            features.append("Fachsprache")
        if dialogue_markers > 10:
            features.append("Viel direkte Rede")
        if avg_sent_len > 25:
            features.append("Lange Saetze")
        elif avg_sent_len < 12:
            features.append("Kurze, praeagnante Saetze")

        return StyleAnalysisResult(
            primary_style=primary_style,
            style_scores=style_scores,
            formality_score=round(formality, 2),
            emotionality_score=round(emotionality, 2),
            complexity_score=round(complexity, 2),
            distinctive_features=features
        )

    # =========================================================================
    # THEMEN-CLUSTERING
    # =========================================================================

    def add_text_for_clustering(self, text: str, text_id: str = None) -> str:
        """Fuegt Text zum Clustering-Pool hinzu"""
        if text_id is None:
            text_id = self._generate_id(text)

        self._text_vectors[text_id] = self._get_text_vector(text)
        return text_id

    def cluster_texts(self, num_clusters: int = 5) -> List[TopicCluster]:
        """
        Clustert die hinzugefuegten Texte nach Themen.

        Verwendet einfaches K-Means-artiges Clustering basierend auf
        TF-Vektoren und Kosinus-Aehnlichkeit.
        """
        if len(self._text_vectors) < 2:
            logger.warning("Nicht genug Texte fuer Clustering")
            return []

        text_ids = list(self._text_vectors.keys())
        num_clusters = min(num_clusters, len(text_ids))

        # Initialisiere Cluster mit zufaelligen Zentren
        clusters = []
        step = len(text_ids) // num_clusters

        for i in range(num_clusters):
            center_id = text_ids[i * step]
            cluster = TopicCluster(
                cluster_id=f"cluster_{i}",
                main_topic="",
                keywords=[],
                texts=[center_id],
                coherence_score=0.0
            )
            clusters.append(cluster)

        # Iteratives Zuweisen
        for _ in range(10):  # Max 10 Iterationen
            # Weise Texte zu naechstem Cluster zu
            for text_id in text_ids:
                if any(text_id in c.texts for c in clusters):
                    continue

                best_cluster = None
                best_sim = -1

                for cluster in clusters:
                    # Berechne durchschnittliche Aehnlichkeit zum Cluster
                    if cluster.texts:
                        sims = [
                            self._cosine_similarity(
                                self._text_vectors[text_id],
                                self._text_vectors[t]
                            )
                            for t in cluster.texts
                        ]
                        avg_sim = sum(sims) / len(sims)

                        if avg_sim > best_sim:
                            best_sim = avg_sim
                            best_cluster = cluster

                if best_cluster:
                    best_cluster.texts.append(text_id)

        # Berechne Keywords und Coherence fuer jeden Cluster
        for cluster in clusters:
            if not cluster.texts:
                continue

            # Kombiniere alle Woerter aus Cluster-Texten
            all_words = Counter()
            for text_id in cluster.texts:
                vec = self._text_vectors[text_id]
                for word, score in vec.items():
                    all_words[word] += score

            cluster.keywords = [w for w, _ in all_words.most_common(10)]
            cluster.main_topic = cluster.keywords[0] if cluster.keywords else "Unbekannt"

            # Coherence: durchschnittliche paarweise Aehnlichkeit
            if len(cluster.texts) > 1:
                similarities = []
                for i, t1 in enumerate(cluster.texts):
                    for t2 in cluster.texts[i+1:]:
                        sim = self._cosine_similarity(
                            self._text_vectors[t1],
                            self._text_vectors[t2]
                        )
                        similarities.append(sim)
                cluster.coherence_score = sum(similarities) / len(similarities)
            else:
                cluster.coherence_score = 1.0

        self._clusters = clusters
        logger.info(f"Texte in {len(clusters)} Cluster gruppiert")

        return clusters

    def find_similar_texts(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Findet aehnliche Texte im Pool"""
        query_vec = self._get_text_vector(text)

        similarities = []
        for text_id, vec in self._text_vectors.items():
            sim = self._cosine_similarity(query_vec, vec)
            similarities.append((text_id, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    # =========================================================================
    # FRAGEN GENERIEREN
    # =========================================================================

    def generate_questions(self, text: str, num_questions: int = 5) -> List[GeneratedQuestion]:
        """
        Generiert Verstaendnisfragen zum Text.

        Erstellt Fragen basierend auf:
        - Wer/Was/Wo/Wann/Warum/Wie-Muster
        - Wichtige Saetze im Text
        - Extrahierte Fakten
        """
        questions = []
        sentences = self._get_sentences(text)

        if not sentences:
            return []

        # Extrahiere wichtige Elemente
        facts = self.extract_facts(text)

        for sentence in sentences[:20]:  # Max 20 Saetze betrachten
            words = self._tokenize(sentence)

            if len(words) < 5:
                continue

            # Erkenne Satzstruktur fuer Fragen
            sentence_lower = sentence.lower()

            # WER-Fragen (bei Personennamen)
            names = re.findall(r'\b([A-ZAEOEUE][a-zaeoeue]+)\b', sentence)
            if names and len(names) <= 3:
                q = GeneratedQuestion(
                    question=f"Wer wird in diesem Abschnitt erwaehnt?",
                    question_type="wer",
                    difficulty="leicht",
                    related_sentence=sentence,
                    expected_answer_keywords=names[:3]
                )
                questions.append(q)

            # WAS-Fragen (bei Verben)
            verbs = ["macht", "tut", "sagt", "erklaert", "zeigt", "beschreibt"]
            for verb in verbs:
                if verb in sentence_lower:
                    q = GeneratedQuestion(
                        question=f"Was {verb} der Text ueber dieses Thema?",
                        question_type="was",
                        difficulty="mittel",
                        related_sentence=sentence,
                        expected_answer_keywords=words[:5]
                    )
                    questions.append(q)
                    break

            # WARUM-Fragen (bei Kausalitaet)
            causal = ["weil", "da", "deshalb", "daher", "aufgrund"]
            if any(c in sentence_lower for c in causal):
                q = GeneratedQuestion(
                    question="Warum passiert das laut dem Text?",
                    question_type="warum",
                    difficulty="schwer",
                    related_sentence=sentence,
                    expected_answer_keywords=words[:5]
                )
                questions.append(q)

            # WANN-Fragen (bei Zeitangaben)
            if any(f.fact_type == "datum" for f in facts):
                date_facts = [f for f in facts if f.fact_type == "datum"]
                if date_facts:
                    q = GeneratedQuestion(
                        question="Wann fand dieses Ereignis statt?",
                        question_type="wann",
                        difficulty="leicht",
                        related_sentence=date_facts[0].context,
                        expected_answer_keywords=[date_facts[0].value]
                    )
                    questions.append(q)

            # WO-Fragen (bei Ortsangaben)
            location_pattern = r'in\s+([A-ZAEOEUE][a-zaeoeue]+)'
            locations = re.findall(location_pattern, sentence)
            if locations:
                q = GeneratedQuestion(
                    question="Wo spielt sich das Geschehen ab?",
                    question_type="wo",
                    difficulty="leicht",
                    related_sentence=sentence,
                    expected_answer_keywords=locations
                )
                questions.append(q)

        # Dedupliziere und begrenze
        seen = set()
        unique_questions = []
        for q in questions:
            if q.question not in seen:
                seen.add(q.question)
                unique_questions.append(q)

        logger.info(f"Fragen generiert: {len(unique_questions[:num_questions])}")

        # LLM-Erweiterung wenn aktiviert
        if self._llm_available and self.use_llm:
            llm_questions = self._generate_questions_llm(text, num_questions)
            if llm_questions:
                # Kombiniere: LLM-Fragen zuerst, dann Standalone als Fallback
                combined = llm_questions + unique_questions
                seen_llm = set()
                final = []
                for q in combined:
                    if q.question not in seen_llm:
                        seen_llm.add(q.question)
                        final.append(q)
                return final[:num_questions]

        return unique_questions[:num_questions]

    def _generate_questions_llm(self, text: str, num_questions: int) -> List[GeneratedQuestion]:
        """Generiert Fragen mit LLM-Unterstuetzung"""
        prompt = f"""Erstelle {num_questions} Verstaendnisfragen zu diesem Text.

Text: "{text[:1500]}"

Antworte NUR in diesem Format (eine Frage pro Zeile):
FRAGE: [Die Frage]
TYP: [wer/was/wo/wann/warum/wie]
SCHWIERIGKEIT: [leicht/mittel/schwer]
---"""

        response = self._query_llm(prompt)
        if not response:
            return []

        questions = []
        current_q = {}

        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('FRAGE:'):
                if current_q.get('question'):
                    questions.append(GeneratedQuestion(
                        question=current_q.get('question', ''),
                        question_type=current_q.get('type', 'was'),
                        difficulty=current_q.get('difficulty', 'mittel'),
                        related_sentence="[LLM-generiert]",
                        expected_answer_keywords=[]
                    ))
                current_q = {'question': line.replace('FRAGE:', '').strip()}
            elif line.startswith('TYP:'):
                current_q['type'] = line.replace('TYP:', '').strip().lower()
            elif line.startswith('SCHWIERIGKEIT:'):
                current_q['difficulty'] = line.replace('SCHWIERIGKEIT:', '').strip().lower()
            elif line == '---' and current_q.get('question'):
                questions.append(GeneratedQuestion(
                    question=current_q.get('question', ''),
                    question_type=current_q.get('type', 'was'),
                    difficulty=current_q.get('difficulty', 'mittel'),
                    related_sentence="[LLM-generiert]",
                    expected_answer_keywords=[]
                ))
                current_q = {}

        # Letzte Frage hinzufuegen
        if current_q.get('question'):
            questions.append(GeneratedQuestion(
                question=current_q.get('question', ''),
                question_type=current_q.get('type', 'was'),
                difficulty=current_q.get('difficulty', 'mittel'),
                related_sentence="[LLM-generiert]",
                expected_answer_keywords=[]
            ))

        return questions

    # =========================================================================
    # FAKTEN-EXTRAKTION
    # =========================================================================

    def extract_facts(self, text: str) -> List[ExtractedFact]:
        """
        Extrahiert konkrete Fakten aus dem Text.

        Erkennt:
        - Zahlen und Mengenangaben
        - Daten und Zeitangaben
        - Prozentangaben
        - Namen und Orte
        """
        facts = []

        for fact_type, patterns in self.fact_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    value = match.group(0)

                    # Kontext extrahieren
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].replace('\n', ' ')

                    # Confidence basierend auf Kontext
                    confidence = 0.8
                    if fact_type == "zahl" and any(c in context.lower() for c in ["etwa", "ca.", "ungefaehr"]):
                        confidence = 0.6

                    fact = ExtractedFact(
                        fact_id=self._generate_id(value + str(match.start())),
                        fact_type=fact_type,
                        value=value,
                        context=context,
                        confidence=confidence,
                        position=match.start()
                    )
                    facts.append(fact)

        # Sortiere nach Position
        facts.sort(key=lambda f: f.position)

        logger.info(f"Fakten extrahiert: {len(facts)}")
        return facts

    # =========================================================================
    # VERGLEICHS-ANALYSE
    # =========================================================================

    def compare_texts(self, text1: str, text2: str) -> TextComparisonResult:
        """
        Vergleicht zwei Texte miteinander.

        Analysiert:
        - Aehnlichkeit (Jaccard, Cosine)
        - Gemeinsame Keywords
        - Einzigartige Woerter
        - Stil-Aehnlichkeit
        - Themen-Ueberlappung
        - Sentiment-Differenz
        """
        # Vektoren und Keywords
        vec1 = self._get_text_vector(text1)
        vec2 = self._get_text_vector(text2)

        words1 = set(self._tokenize(text1)) - self.stopwords
        words2 = set(self._tokenize(text2)) - self.stopwords

        # Kosinus-Aehnlichkeit
        similarity = self._cosine_similarity(vec1, vec2)

        # Keywords
        top_words1 = [w for w, _ in sorted(vec1.items(), key=lambda x: -x[1])[:20]]
        top_words2 = [w for w, _ in sorted(vec2.items(), key=lambda x: -x[1])[:20]]

        common_keywords = list(set(top_words1) & set(top_words2))
        unique_to_text1 = list(set(top_words1) - set(top_words2))[:10]
        unique_to_text2 = list(set(top_words2) - set(top_words1))[:10]

        # Stil-Analyse
        style1 = self.analyze_style(text1)
        style2 = self.analyze_style(text2)

        style_similarity = 1.0 - abs(style1.formality_score - style2.formality_score)
        style_similarity = (style_similarity + (1.0 - abs(style1.complexity_score - style2.complexity_score))) / 2

        # Themen-Ueberlappung (Jaccard)
        topic_overlap = len(words1 & words2) / max(len(words1 | words2), 1)

        # Sentiment (vereinfacht - nur basierend auf positiv/negativ Woertern)
        # TODO: Integration mit HoloReader sentiment
        sentiment_diff = style1.emotionality_score - style2.emotionality_score

        # Zusammenfassung generieren
        if similarity > 0.7:
            summary = "Die Texte sind sehr aehnlich und behandeln wahrscheinlich das gleiche Thema."
        elif similarity > 0.4:
            summary = "Die Texte haben einige Gemeinsamkeiten, unterscheiden sich aber in Details."
        else:
            summary = "Die Texte sind recht unterschiedlich und behandeln verschiedene Aspekte."

        if style_similarity < 0.5:
            summary += " Der Schreibstil unterscheidet sich deutlich."

        return TextComparisonResult(
            similarity_score=round(similarity, 3),
            common_keywords=common_keywords,
            unique_to_text1=unique_to_text1,
            unique_to_text2=unique_to_text2,
            style_similarity=round(style_similarity, 3),
            topic_overlap=round(topic_overlap, 3),
            sentiment_difference=round(sentiment_diff, 3),
            summary=summary
        )


# =============================================================================
# ALIASE FÜR RÜCKWÄRTSKOMPATIBILITÄT
# =============================================================================

# holo_brain.py erwartet diesen Namen
ExtendedReader = HoloReaderExtended


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "WritingStyle",
    "ChapterType",

    # Dataclasses
    "Chapter",
    "Quote",
    "ReadabilityResult",
    "StyleAnalysisResult",
    "TopicCluster",
    "GeneratedQuestion",
    "ExtractedFact",
    "TextComparisonResult",

    # Main class
    "HoloReaderExtended",
    "ExtendedReader",  # Alias
]


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO READER EXTENDED - Test")
    print("=" * 60)

    reader = HoloReaderExtended()

    # Test-Text
    test_text = """
    Kapitel 1: Der Anfang

    Es war ein schoener Sommertag im Jahr 2023, als Maria durch den Park spazierte.
    Die Sonne schien warm auf ihr Gesicht und die Voegel sangen froehlich in den Baeumen.
    Sie fuehlte sich gluecklich und zufrieden mit ihrem Leben.

    "Hallo Maria!", rief Thomas. "Was fuer eine Ueberraschung!"
    "Ja, es ist wirklich schoen hier", antwortete Maria laechelnd.

    Laut einer Studie von 2022 verbringen Deutsche durchschnittlich 45 Minuten pro Tag
    in Parks. Das entspricht etwa 3% ihrer wachen Zeit. Berlin hat mit 2.500 Hektar
    die groesste Parkflaeche aller deutschen Staedte.

    Kapitel 2: Die Erkenntnis

    Maria dachte nach: "Warum bin ich eigentlich so gluecklich?"
    Die Antwort war einfach - weil sie Zeit in der Natur verbrachte.
    """

    # Kapitel-Erkennung
    print("\n[1] Kapitel-Erkennung:")
    chapters = reader.detect_chapters(test_text)
    for ch in chapters:
        print(f"  - {ch.title} ({ch.word_count} Woerter)")

    # Zitat-Extraktion
    print("\n[2] Zitat-Extraktion:")
    quotes = reader.extract_quotes(test_text)
    for q in quotes[:3]:
        print(f"  - \"{q.text[:50]}...\" (Sprecher: {q.speaker})")

    # Lesbarkeit
    print("\n[3] Lesbarkeit:")
    readability = reader.calculate_readability(test_text)
    print(f"  - Flesch-Score: {readability.flesch_score} ({readability.flesch_grade})")
    print(f"  - Zielgruppe: {readability.suggested_audience}")

    # Stil-Analyse
    print("\n[4] Stil-Analyse:")
    style = reader.analyze_style(test_text)
    print(f"  - Primaerer Stil: {style.primary_style.value}")
    print(f"  - Formalitaet: {style.formality_score}")
    print(f"  - Merkmale: {', '.join(style.distinctive_features)}")

    # Fakten-Extraktion
    print("\n[5] Fakten-Extraktion:")
    facts = reader.extract_facts(test_text)
    for f in facts[:5]:
        print(f"  - [{f.fact_type}] {f.value}")

    # Fragen generieren
    print("\n[6] Generierte Fragen:")
    questions = reader.generate_questions(test_text, 3)
    for q in questions:
        print(f"  - [{q.question_type}] {q.question}")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)
