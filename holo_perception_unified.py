#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloPerception Unified v5.0 - Integriertes Wahrnehmungssystem

INTEGRATION: Nutzt existierende Module statt Duplikation!

VERWENDETE KERN-MODULE:
- holo_perception.py -> HoloReader, HoloVision (Basis)
- holo_text_reader.py -> HoloTextReader (erweiterte Textanalyse)
- holo_nlp_algorithms.py -> LightweightVectorEngine, Sentiment, Entities

ENHANCED MODULE (80%+ Standalone-Qualitaet):
- holo_nlp_enhanced.py -> NER, Koreferenz, Ironie, Stil-Fingerprint
- holo_vision_enhanced.py -> Emotionen, Posen, Tracking, Farben
- holo_nlp_advanced.py -> Topic Modeling, Relations, Timeline, QA
- holo_vision_advanced.py -> Objects, Faces, QR, Logo, Layout
- holo_audio_enhanced.py -> Speaker, Voice Emotion, Genre, STT
- holo_crossmodal.py -> Image Captioning, Multimodal Sentiment

NEUE MODULE (nur hier integriert):
- holo_audio.py -> Audio/Musik-Analyse
- holo_video.py -> Video-Analyse
- holo_document.py -> Dokument-Parsing
- holo_media_integration.py -> Media Journal, Knowledge Graph

HYBRID-SYSTEM: Funktioniert standalone UND mit LLM-Erweiterung

Author: Kira & Claude
Version: 5.0 (Vollstaendig Integriert)
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

logger = logging.getLogger("HoloPerceptionUnified")


# =============================================================================
# KONFIGURATION
# =============================================================================

class PerceptionMode(Enum):
    """Wahrnehmungs-Modus"""
    STANDALONE = "standalone"      # Nur lokale Algorithmen
    LLM_ENHANCED = "llm_enhanced"  # Mit LLM-Unterstuetzung
    HYBRID = "hybrid"              # Standalone + LLM wenn verfuegbar
    AUTO = "auto"                  # Automatische Entscheidung


class AnalysisDepth(Enum):
    """Analyse-Tiefe"""
    QUICK = "quick"        # Schnell, nur Basis-Features
    STANDARD = "standard"  # Normal, gute Balance
    DEEP = "deep"          # Tiefgehend, alle Features
    EXHAUSTIVE = "exhaustive"  # Alles + LLM


# =============================================================================
# IMPORTS DER EXISTIERENDEN MODULE
# =============================================================================

# --- Basis-Perception (HoloReader, HoloVision) ---
_HAS_PERCEPTION = False
HoloReader = None
HoloVision = None
HoloPerception = None
TextAnalysisResult = None
ImageAnalysisResult = None

try:
    from holo_perception import (
        HoloReader,
        HoloVision,
        HoloPerception,
        TextAnalysisResult,
        ImageAnalysisResult,
        TextType,
        ImageType,
        ColorMood,
    )
    _HAS_PERCEPTION = True
    logger.info("holo_perception importiert")
except ImportError as e:
    logger.warning(f"holo_perception nicht verfuegbar: {e}")


# --- Erweiterte Textanalyse ---
_HAS_TEXT_READER = False
HoloTextReader = None

try:
    from holo_text_reader import (
        HoloTextReader,
        KeywordExtractor,
        EntityExtractor as TextEntityExtractor,
        SentimentAnalyzer,
        FactExtractor,
        TopicDetector,
        LanguageDetector,
        FactType,
        Sentiment,
        TopicCategory,
    )
    _HAS_TEXT_READER = True
    logger.info("holo_text_reader importiert")
except ImportError as e:
    logger.warning(f"holo_text_reader nicht verfuegbar: {e}")


# --- NLP Algorithmen ---
_HAS_NLP_ALGORITHMS = False
LightweightVectorEngine = None

try:
    from holo_nlp_algorithms import (
        LightweightVectorEngine,
    )
    _HAS_NLP_ALGORITHMS = True
    logger.info("holo_nlp_algorithms importiert")
except ImportError as e:
    logger.warning(f"holo_nlp_algorithms nicht verfuegbar: {e}")


# --- Neue Module (Audio, Video, Document, Media Integration) ---
_HAS_AUDIO = False
_HAS_VIDEO = False
_HAS_DOCUMENT = False
_HAS_MEDIA_INTEGRATION = False

try:
    from holo_audio import HoloAudio, AudioAnalysisResult
    _HAS_AUDIO = True
    logger.info("holo_audio importiert")
except ImportError:
    HoloAudio = None
    AudioAnalysisResult = None

try:
    from holo_video import HoloVideo, VideoAnalysisResult
    _HAS_VIDEO = True
    logger.info("holo_video importiert")
except ImportError:
    HoloVideo = None
    VideoAnalysisResult = None

try:
    from holo_document import HoloDocument, DocumentAnalysisResult
    _HAS_DOCUMENT = True
    logger.info("holo_document importiert")
except ImportError:
    HoloDocument = None
    DocumentAnalysisResult = None

try:
    from holo_media_integration import (
        MediaJournal,
        RecommendationEngine,
        EmotionalConnectionManager,
        KnowledgeGraph,
    )
    _HAS_MEDIA_INTEGRATION = True
    logger.info("holo_media_integration importiert")
except ImportError:
    MediaJournal = None
    RecommendationEngine = None
    EmotionalConnectionManager = None
    KnowledgeGraph = None


# --- Enhanced NLP (NEU - 80%+ Qualitaet) ---
_HAS_NLP_ENHANCED = False
HoloNLPEnhanced = None

try:
    from holo_nlp_enhanced import (
        HoloNLPEnhanced,
        EnhancedNER,
        CoreferenceResolver,
        ArgumentDetector,
        IronyDetector,
        PlagiarismDetector,
        AuthorStyleAnalyzer,
    )
    _HAS_NLP_ENHANCED = True
    logger.info("holo_nlp_enhanced importiert")
except ImportError as e:
    logger.warning(f"holo_nlp_enhanced nicht verfuegbar: {e}")
    EnhancedNER = None
    CoreferenceResolver = None
    ArgumentDetector = None
    IronyDetector = None
    PlagiarismDetector = None
    AuthorStyleAnalyzer = None


# --- Enhanced Vision (NEU - 80%+ Qualitaet) ---
_HAS_VISION_ENHANCED = False
HoloVisionEnhanced = None

try:
    from holo_vision_enhanced import (
        HoloVisionEnhanced,
        EnhancedEmotionDetector,
        SimplePoseEstimator,
        SimpleObjectTracker,
        SimpleImageTextMatcher,
        EnhancedSceneClassifier,
        EnhancedColorAnalyzer,
    )
    _HAS_VISION_ENHANCED = True
    logger.info("holo_vision_enhanced importiert")
except ImportError as e:
    logger.warning(f"holo_vision_enhanced nicht verfuegbar: {e}")
    EnhancedEmotionDetector = None
    SimplePoseEstimator = None
    SimpleObjectTracker = None
    SimpleImageTextMatcher = None
    EnhancedSceneClassifier = None
    EnhancedColorAnalyzer = None


# --- NLP Advanced (Topic Modeling, QA, TextGen) ---
_HAS_NLP_ADVANCED = False
HoloNLPAdvanced = None

try:
    from holo_nlp_advanced import (
        HoloNLPAdvanced,
        SimpleTopicModel,
        RelationExtractor,
        TimelineExtractor,
        ExtractiveQA,
        SimpleTextGenerator,
        AspectSentimentAnalyzer,
        MultiLabelClassifier,
    )
    _HAS_NLP_ADVANCED = True
    logger.info("holo_nlp_advanced importiert")
except ImportError as e:
    logger.warning(f"holo_nlp_advanced nicht verfuegbar: {e}")
    SimpleTopicModel = None
    RelationExtractor = None
    TimelineExtractor = None
    ExtractiveQA = None
    SimpleTextGenerator = None
    AspectSentimentAnalyzer = None
    MultiLabelClassifier = None


# --- Vision Advanced (Objects, Faces, QR, Layout) ---
_HAS_VISION_ADVANCED = False
HoloVisionAdvanced = None

try:
    from holo_vision_advanced import (
        HoloVisionAdvanced,
        SimpleObjectDetector,
        SimpleFaceRecognizer,
        QRBarcodeReader,
        LogoDetector,
        DocumentLayoutAnalyzer,
        ImageSimilarity,
        SimpleHandwritingRecognizer,
    )
    _HAS_VISION_ADVANCED = True
    logger.info("holo_vision_advanced importiert")
except ImportError as e:
    logger.warning(f"holo_vision_advanced nicht verfuegbar: {e}")
    SimpleObjectDetector = None
    SimpleFaceRecognizer = None
    QRBarcodeReader = None
    LogoDetector = None
    DocumentLayoutAnalyzer = None
    ImageSimilarity = None
    SimpleHandwritingRecognizer = None


# --- Audio Enhanced (Speaker, Emotion, Genre, STT) ---
_HAS_AUDIO_ENHANCED = False
HoloAudioEnhanced = None

try:
    from holo_audio_enhanced import (
        HoloAudioEnhanced,
        SpeakerRecognizer,
        VoiceEmotionDetector,
        MusicGenreClassifier,
        SpeechToText,
        AudioFingerprinter,
        SoundEventDetector,
    )
    _HAS_AUDIO_ENHANCED = True
    logger.info("holo_audio_enhanced importiert")
except ImportError as e:
    logger.warning(f"holo_audio_enhanced nicht verfuegbar: {e}")
    SpeakerRecognizer = None
    VoiceEmotionDetector = None
    MusicGenreClassifier = None
    SpeechToText = None
    AudioFingerprinter = None
    SoundEventDetector = None


# --- CrossModal (Image Captioning, Multimodal Sentiment) ---
_HAS_CROSSMODAL = False
HoloCrossModal = None

try:
    from holo_crossmodal import (
        HoloCrossModal,
        TemplateImageCaptioner,
        MultimodalSentimentAnalyzer,
        ImageTextMatcher,
        ContextFusion,
        MultimodalSummarizer,
    )
    _HAS_CROSSMODAL = True
    logger.info("holo_crossmodal importiert")
except ImportError as e:
    logger.warning(f"holo_crossmodal nicht verfuegbar: {e}")
    TemplateImageCaptioner = None
    MultimodalSentimentAnalyzer = None
    ImageTextMatcher = None
    ContextFusion = None
    MultimodalSummarizer = None


# =============================================================================
# ERWEITERTE TEXT-FEATURES (Nutz existierende Module)
# =============================================================================

@dataclass
class ExtendedTextAnalysis:
    """Erweiterte Textanalyse mit allen Features"""
    # Basis (aus holo_perception)
    text_id: str = ""
    word_count: int = 0
    sentence_count: int = 0
    sentiment: float = 0.0
    sentiment_label: str = ""
    keywords: List[str] = field(default_factory=list)
    summary: str = ""

    # Erweitert (aus holo_text_reader)
    facts: List[Any] = field(default_factory=list)
    entities: List[Any] = field(default_factory=list)
    topic_category: str = ""
    language: str = "de"

    # Neue Features
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    quotes: List[str] = field(default_factory=list)
    readability_score: float = 0.0
    readability_label: str = ""
    style_analysis: Dict[str, Any] = field(default_factory=dict)
    questions: List[str] = field(default_factory=list)

    # Enhanced NLP Features (80%+ Qualitaet)
    enhanced_entities: List[Any] = field(default_factory=list)  # Bessere NER
    coreference_clusters: List[Any] = field(default_factory=list)  # Pronomen-Aufloesung
    arguments: List[Any] = field(default_factory=list)  # Argumentations-Struktur
    irony_detected: bool = False
    irony_confidence: float = 0.0
    author_fingerprint: Optional[Dict[str, Any]] = None  # Stil-Fingerprint

    # Advanced NLP Features (Topic Modeling, QA, Relations)
    topics: List[Dict[str, Any]] = field(default_factory=list)  # Topic Modeling
    relations: List[Dict[str, Any]] = field(default_factory=list)  # Relation Extraction
    timeline: List[Dict[str, Any]] = field(default_factory=list)  # Timeline Events
    aspect_sentiments: Dict[str, float] = field(default_factory=dict)  # Aspect-based Sentiment
    labels: List[str] = field(default_factory=list)  # Multi-Label Classification

    # LLM-erweitert
    llm_summary: Optional[str] = None
    llm_insights: Optional[List[str]] = None

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExtendedImageAnalysis:
    """Erweiterte Bildanalyse mit allen Features"""
    # Basis (aus holo_perception)
    image_id: str = ""
    width: int = 0
    height: int = 0
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    brightness: float = 0.0
    face_count: int = 0

    # Neue Features
    emotions: List[Dict[str, float]] = field(default_factory=list)
    ocr_text: str = ""
    scene_type: str = ""
    similar_images: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    art_style: str = ""
    is_meme: bool = False
    histogram: Dict[str, List[int]] = field(default_factory=dict)

    # Enhanced Vision Features (80%+ Qualitaet)
    face_analyses: List[Any] = field(default_factory=list)  # Detaillierte Gesichtsanalyse
    pose_estimations: List[Any] = field(default_factory=list)  # Pose-Erkennung
    color_analysis: Optional[Dict[str, Any]] = None  # Fortgeschrittene Farbanalyse
    scene_analysis: Optional[Dict[str, Any]] = None  # Fortgeschrittene Szenenanalyse
    composition: str = ""  # Bildkomposition
    color_harmony: str = ""  # Farbharmonie
    color_temperature: str = ""  # Warm/Kalt

    # Advanced Vision Features (Objects, QR, Layout)
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)  # Object Detection
    recognized_faces: List[Dict[str, Any]] = field(default_factory=list)  # Face Recognition
    qr_codes: List[Dict[str, Any]] = field(default_factory=list)  # QR/Barcode
    logos: List[Dict[str, Any]] = field(default_factory=list)  # Logo Detection
    document_layout: Optional[Dict[str, Any]] = None  # Document Layout
    image_caption: str = ""  # Generated Caption
    similar_hash: str = ""  # Perceptual Hash

    # LLM-erweitert
    llm_description: Optional[str] = None

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# LLM ENHANCER (Optional)
# =============================================================================

class LLMEnhancer:
    """Optionale LLM-Erweiterung fuer tiefere Analysen"""

    def __init__(self, llm_instance=None):
        self.llm = llm_instance
        self._available = llm_instance is not None

    @property
    def available(self) -> bool:
        return self._available

    def set_llm(self, llm_instance):
        """Setzt LLM-Instanz nachtraeglich"""
        self.llm = llm_instance
        self._available = llm_instance is not None

    def query(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Stellt eine Anfrage an das LLM"""
        if not self._available:
            return None

        try:
            result = self.llm.query(
                prompt=prompt,
                system_prompt=system_prompt,
                intent="analysis"
            )
            return result.get("response") if isinstance(result, dict) else str(result)
        except Exception as e:
            logger.warning(f"LLM-Anfrage fehlgeschlagen: {e}")
            return None

    def enhance_summary(self, text: str, basic_summary: str) -> Optional[str]:
        """Verbessert eine Zusammenfassung mit LLM"""
        if not self._available:
            return None

        prompt = f"""Verbessere diese Zusammenfassung und mache sie natuerlicher:

Basis-Zusammenfassung: {basic_summary}

Originaltext (Auszug): {text[:1500]}...

Erstelle eine verbesserte, fluesige Zusammenfassung in 2-3 Saetzen."""

        return self.query(prompt)

    def extract_insights(self, text: str, analysis: Dict) -> Optional[List[str]]:
        """Extrahiert tiefere Einsichten mit LLM"""
        if not self._available:
            return None

        prompt = f"""Analysiere diesen Text und extrahiere 3-5 wichtige Einsichten:

Text: {text[:2000]}...

Bisherige Analyse:
- Themen: {analysis.get('topics', [])}
- Sentiment: {analysis.get('sentiment', 'neutral')}
- Entitaeten: {analysis.get('entities', [])}

Gib konkrete, interessante Einsichten zurueck."""

        result = self.query(prompt)
        if result:
            # Parse Einsichten aus Antwort
            insights = [line.strip("- ").strip() for line in result.split("\n")
                       if line.strip() and len(line.strip()) > 10]
            return insights[:5]
        return None

    def describe_image(self, analysis: Dict) -> Optional[str]:
        """Erstellt eine natuerliche Bildbeschreibung mit LLM"""
        if not self._available:
            return None

        prompt = f"""Erstelle eine natuerliche Beschreibung fuer dieses Bild basierend auf der Analyse:

- Groesse: {analysis.get('width', 0)}x{analysis.get('height', 0)} Pixel
- Dominante Farben: {analysis.get('color_names', [])}
- Helligkeit: {analysis.get('brightness', 0.5):.1%}
- Gesichter erkannt: {analysis.get('face_count', 0)}
- Farbstimmung: {analysis.get('color_mood', 'neutral')}
- OCR-Text: {analysis.get('ocr_text', '')[:200]}

Beschreibe das Bild in 2-3 natuerlichen Saetzen."""

        return self.query(prompt)


# =============================================================================
# ERWEITERTE READER-FEATURES
# =============================================================================

class ExtendedReaderFeatures:
    """Erweiterte Text-Features die auf existierenden Modulen aufbauen"""

    def __init__(self):
        # Nutze existierende Module wenn verfuegbar
        if _HAS_TEXT_READER:
            self.keyword_extractor = KeywordExtractor()
            self.sentiment_analyzer = SentimentAnalyzer()
            self.language_detector = LanguageDetector()
        else:
            self.keyword_extractor = None
            self.sentiment_analyzer = None
            self.language_detector = None

    def detect_chapters(self, text: str) -> List[Dict[str, Any]]:
        """Erkennt Kapitel im Text"""
        chapters = []

        # Patterns fuer Kapitel
        patterns = [
            r'^(Kapitel\s+\d+[:\.\s]*.*?)$',
            r'^(Chapter\s+\d+[:\.\s]*.*?)$',
            r'^(\d+\.\s+[A-ZAEOEUE].*?)$',
            r'^(Teil\s+\d+[:\.\s]*.*?)$',
            r'^(Abschnitt\s+\d+[:\.\s]*.*?)$',
        ]

        import re
        lines = text.split('\n')
        current_pos = 0

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            for pattern in patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    chapters.append({
                        "title": match.group(1),
                        "line": i,
                        "position": current_pos,
                        "length": 0  # Wird spaeter berechnet
                    })
                    break
            current_pos += len(line) + 1

        # Berechne Laengen
        for i, chapter in enumerate(chapters):
            if i < len(chapters) - 1:
                chapter["length"] = chapters[i+1]["position"] - chapter["position"]
            else:
                chapter["length"] = len(text) - chapter["position"]

        return chapters

    def extract_quotes(self, text: str) -> List[str]:
        """Extrahiert Zitate aus dem Text"""
        import re

        quotes = []

        # Deutsche und englische Anfuehrungszeichen
        patterns = [
            r'"([^"]{10,300})"',
            r"'([^']{10,300})'",
            r'„([^"]{10,300})"',
            r'«([^»]{10,300})»',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            quotes.extend(matches)

        # Deduplizieren
        return list(dict.fromkeys(quotes))[:20]

    def calculate_readability_german(self, text: str) -> Tuple[float, str]:
        """
        Berechnet Flesch-Reading-Ease fuer Deutsch (Amstad-Formel).

        FRE_de = 180 - ASL - (58.5 * ASW)
        ASL = Average Sentence Length
        ASW = Average Syllables per Word
        """
        import re

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = re.findall(r'\b[a-zaeoeueAEOEUEss]+\b', text)

        if not sentences or not words:
            return 0.0, "unbekannt"

        # Silben zaehlen (vereinfacht fuer Deutsch)
        def count_syllables(word: str) -> int:
            word = word.lower()
            vowels = "aeiouaeoeue"
            count = 0
            prev_vowel = False

            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_vowel:
                    count += 1
                prev_vowel = is_vowel

            # Mindestens eine Silbe
            return max(1, count)

        total_syllables = sum(count_syllables(w) for w in words)

        asl = len(words) / len(sentences)  # Average Sentence Length
        asw = total_syllables / len(words)  # Average Syllables per Word

        # Amstad-Formel
        fre = 180 - asl - (58.5 * asw)
        fre = max(0, min(100, fre))  # Clamp to 0-100

        # Label
        if fre >= 70:
            label = "sehr leicht"
        elif fre >= 60:
            label = "leicht"
        elif fre >= 50:
            label = "mittel"
        elif fre >= 30:
            label = "schwer"
        else:
            label = "sehr schwer"

        return round(fre, 1), label

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """Analysiert den Schreibstil"""
        import re

        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not words or not sentences:
            return {}

        # Basis-Statistiken
        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)

        # Vokabular-Diversitaet
        unique_words = len(set(w.lower() for w in words))
        vocab_diversity = unique_words / len(words)

        # Komplexitaet
        long_words = sum(1 for w in words if len(w) > 10)
        complexity = long_words / len(words)

        # Stil-Kategorisierung
        if avg_sentence_length > 25 and complexity > 0.1:
            style = "akademisch"
        elif avg_sentence_length < 12 and vocab_diversity < 0.4:
            style = "einfach"
        elif vocab_diversity > 0.6:
            style = "kreativ"
        else:
            style = "journalistisch"

        return {
            "avg_word_length": round(avg_word_length, 1),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "vocabulary_diversity": round(vocab_diversity, 3),
            "complexity": round(complexity, 3),
            "style_category": style,
            "unique_words": unique_words,
            "total_words": len(words),
            "total_sentences": len(sentences),
        }

    def generate_questions(self, text: str, keywords: List[str] = None) -> List[str]:
        """Generiert Fragen zum Text"""
        import re

        questions = []

        # Nutze Keywords wenn vorhanden
        if keywords:
            for kw in keywords[:5]:
                questions.append(f"Was bedeutet '{kw}' in diesem Kontext?")

        # Erkenne Entitaeten und erstelle Fragen
        # Personen
        person_matches = re.findall(r'\b([A-ZAEOEUE][a-zaeoeue]+)\s+([A-ZAEOEUE][a-zaeoeue]+)\b', text)
        for first, last in person_matches[:3]:
            name = f"{first} {last}"
            questions.append(f"Welche Rolle spielt {name}?")

        # Zahlen und Statistiken
        number_matches = re.findall(r'(\d+(?:[.,]\d+)?)\s*(%|Prozent|Euro|Dollar|Millionen|Milliarden)', text)
        for num, unit in number_matches[:3]:
            questions.append(f"Was bedeutet die Zahl {num} {unit}?")

        # Allgemeine Fragen
        questions.extend([
            "Was ist die Hauptaussage des Textes?",
            "Welche Schlussfolgerungen lassen sich ziehen?",
        ])

        return list(dict.fromkeys(questions))[:10]


# =============================================================================
# ERWEITERTE VISION-FEATURES
# =============================================================================

class ExtendedVisionFeatures:
    """Erweiterte Bild-Features die auf existierenden Modulen aufbauen"""

    def __init__(self):
        self._has_cv2 = False
        self._has_pil = False
        self._has_tesseract = False

        try:
            import cv2
            import numpy as np
            self._has_cv2 = True
            self.cv2 = cv2
            self.np = np
        except ImportError:
            pass

        try:
            from PIL import Image
            self._has_pil = True
            self.Image = Image
        except ImportError:
            pass

        try:
            import pytesseract
            self._has_tesseract = True
            self.pytesseract = pytesseract
        except ImportError:
            pass

    def extract_ocr_text(self, image_path: str) -> str:
        """Extrahiert Text aus Bild via OCR"""
        if not self._has_tesseract:
            return ""

        try:
            if self._has_pil:
                img = self.Image.open(image_path)
                text = self.pytesseract.image_to_string(img, lang='deu+eng')
                return text.strip()
        except Exception as e:
            logger.warning(f"OCR fehlgeschlagen: {e}")

        return ""

    def detect_emotions_in_faces(self, image_path: str) -> List[Dict[str, float]]:
        """Erkennt Emotionen in Gesichtern (vereinfacht)"""
        if not self._has_cv2:
            return []

        try:
            img = self.cv2.imread(image_path)
            if img is None:
                return []

            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)

            # Haar Cascade fuer Gesichter
            face_cascade = self.cv2.CascadeClassifier(
                self.cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

            emotions = []
            for (x, y, w, h) in faces:
                # Vereinfachte Emotion basierend auf Gesichtsregion
                face_roi = gray[y:y+h, x:x+w]

                # Helligkeit als Proxy fuer Stimmung
                brightness = self.np.mean(face_roi) / 255.0

                # Vereinfachte Emotion-Schaetzung
                emotion = {
                    "neutral": 0.5,
                    "happy": brightness * 0.3,
                    "sad": (1 - brightness) * 0.2,
                    "region": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                }
                emotions.append(emotion)

            return emotions
        except Exception as e:
            logger.warning(f"Emotionserkennung fehlgeschlagen: {e}")
            return []

    def classify_scene(self, image_path: str) -> str:
        """Klassifiziert die Szene im Bild"""
        if not self._has_cv2:
            return "unbekannt"

        try:
            img = self.cv2.imread(image_path)
            if img is None:
                return "unbekannt"

            # Analysiere Farbverteilung
            hsv = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2HSV)

            # Durchschnittliche Saettigung und Helligkeit
            sat_mean = self.np.mean(hsv[:, :, 1])
            val_mean = self.np.mean(hsv[:, :, 2])
            hue_mean = self.np.mean(hsv[:, :, 0])

            # Gruene Toene (Natur)
            green_mask = (hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85)
            green_ratio = self.np.sum(green_mask) / green_mask.size

            # Blaue Toene (Himmel/Wasser)
            blue_mask = (hsv[:, :, 0] > 90) & (hsv[:, :, 0] < 130)
            blue_ratio = self.np.sum(blue_mask) / blue_mask.size

            # Klassifizierung
            if green_ratio > 0.3:
                return "natur"
            elif blue_ratio > 0.4:
                return "himmel_wasser"
            elif val_mean > 200:
                return "hell_indoor"
            elif val_mean < 80:
                return "dunkel_nacht"
            elif sat_mean < 50:
                return "schwarzweiss"
            else:
                return "allgemein"

        except Exception as e:
            logger.warning(f"Szenenklassifizierung fehlgeschlagen: {e}")
            return "unbekannt"

    def analyze_quality(self, image_path: str) -> float:
        """Analysiert die Bildqualitaet"""
        if not self._has_cv2:
            return 0.5

        try:
            img = self.cv2.imread(image_path)
            if img is None:
                return 0.0

            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)

            # Schaerfe (Laplacian-Varianz)
            laplacian_var = self.cv2.Laplacian(gray, self.cv2.CV_64F).var()
            sharpness = min(1.0, laplacian_var / 1000)

            # Kontrast
            contrast = gray.std() / 128.0
            contrast = min(1.0, contrast)

            # Helligkeit (nicht zu dunkel/hell)
            brightness = self.np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2

            # Gesamtscore
            quality = (sharpness * 0.4 + contrast * 0.3 + brightness_score * 0.3)
            return round(quality, 2)

        except Exception as e:
            logger.warning(f"Qualitaetsanalyse fehlgeschlagen: {e}")
            return 0.5

    def detect_art_style(self, image_path: str) -> str:
        """Erkennt den Kunststil (vereinfacht)"""
        if not self._has_cv2:
            return "unbekannt"

        try:
            img = self.cv2.imread(image_path)
            if img is None:
                return "unbekannt"

            # Analysiere Kanten und Farben
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)
            edges = self.cv2.Canny(gray, 50, 150)
            edge_density = self.np.sum(edges > 0) / edges.size

            # Farbanzahl (Quantisierung)
            img_small = self.cv2.resize(img, (100, 100))
            pixels = img_small.reshape(-1, 3)
            unique_colors = len(set(map(tuple, pixels)))

            # Stil-Klassifizierung
            if edge_density > 0.3:
                return "skizze_zeichnung"
            elif unique_colors < 50:
                return "minimalistisch"
            elif unique_colors < 500:
                return "illustration"
            elif edge_density < 0.05:
                return "abstrakt"
            else:
                return "foto_realistisch"

        except Exception as e:
            logger.warning(f"Stilerkennung fehlgeschlagen: {e}")
            return "unbekannt"

    def is_meme(self, image_path: str, ocr_text: str = None) -> bool:
        """Prueft ob das Bild ein Meme ist"""
        if not self._has_cv2:
            return False

        try:
            img = self.cv2.imread(image_path)
            if img is None:
                return False

            h, w = img.shape[:2]

            # Typische Meme-Indikatoren:
            # 1. Text im Bild (Impact-Font oben/unten)
            if ocr_text and len(ocr_text) > 10:
                # Text vorhanden
                upper_third = img[:h//3]
                lower_third = img[2*h//3:]

                # Weisse Bereiche (typisch fuer Text)
                upper_white = self.np.mean(upper_third) > 200
                lower_white = self.np.mean(lower_third) > 200

                if upper_white or lower_white:
                    return True

            # 2. Quadratisches Format (typisch fuer Social Media)
            aspect = w / h
            if 0.9 <= aspect <= 1.1:
                return True

            return False

        except Exception as e:
            logger.warning(f"Meme-Erkennung fehlgeschlagen: {e}")
            return False

    def get_histogram(self, image_path: str) -> Dict[str, List[int]]:
        """Berechnet Farbhistogramm"""
        if not self._has_cv2:
            return {}

        try:
            img = self.cv2.imread(image_path)
            if img is None:
                return {}

            histograms = {}
            colors = ('blue', 'green', 'red')

            for i, color in enumerate(colors):
                hist = self.cv2.calcHist([img], [i], None, [256], [0, 256])
                histograms[color] = hist.flatten().tolist()

            return histograms

        except Exception as e:
            logger.warning(f"Histogram-Berechnung fehlgeschlagen: {e}")
            return {}


# =============================================================================
# HOLO PERCEPTION UNIFIED - Hauptklasse
# =============================================================================

class HoloPerceptionUnified:
    """
    Vereinigtes Wahrnehmungssystem - Integriert alle Module.

    Nutzt existierende Module:
    - holo_perception (HoloReader, HoloVision)
    - holo_text_reader (erweiterte Textanalyse)
    - holo_nlp_algorithms (Vektoren, Sentiment)

    Plus neue Module:
    - Audio, Video, Document, Media Integration
    """

    def __init__(self,
                 mode: PerceptionMode = PerceptionMode.HYBRID,
                 llm_instance = None,
                 data_dir: str = "data"):

        self.mode = mode
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # LLM-Enhancer
        self.llm_enhancer = LLMEnhancer(llm_instance)

        # --- Existierende Module initialisieren ---

        # Basis-Perception
        self.reader = None
        self.vision = None
        if _HAS_PERCEPTION:
            try:
                self.reader = HoloReader(data_dir=f"{data_dir}/reading")
                self.vision = HoloVision()
            except Exception as e:
                logger.warning(f"HoloPerception init fehlgeschlagen: {e}")

        # Erweiterte Textanalyse
        self.text_reader = None
        if _HAS_TEXT_READER:
            try:
                self.text_reader = HoloTextReader()
            except Exception as e:
                logger.warning(f"HoloTextReader init fehlgeschlagen: {e}")

        # NLP-Engine
        self.vector_engine = None
        if _HAS_NLP_ALGORITHMS:
            try:
                self.vector_engine = LightweightVectorEngine()
            except Exception as e:
                logger.warning(f"LightweightVectorEngine init fehlgeschlagen: {e}")

        # --- Neue Features ---
        self.extended_reader = ExtendedReaderFeatures()
        self.extended_vision = ExtendedVisionFeatures()

        # --- Neue Module ---
        self.audio = None
        self.video = None
        self.document = None
        self.media_journal = None
        self.knowledge_graph = None
        self.recommendation_engine = None

        if _HAS_AUDIO and HoloAudio:
            try:
                self.audio = HoloAudio()
            except Exception as e:
                logger.warning(f"HoloAudio init fehlgeschlagen: {e}")

        if _HAS_VIDEO and HoloVideo:
            try:
                self.video = HoloVideo()
            except Exception as e:
                logger.warning(f"HoloVideo init fehlgeschlagen: {e}")

        if _HAS_DOCUMENT and HoloDocument:
            try:
                self.document = HoloDocument()
            except Exception as e:
                logger.warning(f"HoloDocument init fehlgeschlagen: {e}")

        if _HAS_MEDIA_INTEGRATION:
            try:
                if MediaJournal:
                    self.media_journal = MediaJournal(data_dir=f"{data_dir}/journal")
                if KnowledgeGraph:
                    self.knowledge_graph = KnowledgeGraph()
                if RecommendationEngine:
                    self.recommendation_engine = RecommendationEngine()
            except Exception as e:
                logger.warning(f"Media Integration init fehlgeschlagen: {e}")

        # --- Enhanced NLP (80%+ Qualitaet) ---
        self.nlp_enhanced = None
        if _HAS_NLP_ENHANCED and HoloNLPEnhanced:
            try:
                self.nlp_enhanced = HoloNLPEnhanced()
            except Exception as e:
                logger.warning(f"HoloNLPEnhanced init fehlgeschlagen: {e}")

        # --- Enhanced Vision (80%+ Qualitaet) ---
        self.vision_enhanced = None
        if _HAS_VISION_ENHANCED and HoloVisionEnhanced:
            try:
                self.vision_enhanced = HoloVisionEnhanced()
            except Exception as e:
                logger.warning(f"HoloVisionEnhanced init fehlgeschlagen: {e}")

        # --- NLP Advanced (Topic Modeling, QA, Relations) ---
        self.nlp_advanced = None
        if _HAS_NLP_ADVANCED and HoloNLPAdvanced:
            try:
                self.nlp_advanced = HoloNLPAdvanced()
            except Exception as e:
                logger.warning(f"HoloNLPAdvanced init fehlgeschlagen: {e}")

        # --- Vision Advanced (Objects, Faces, QR, Layout) ---
        self.vision_advanced = None
        if _HAS_VISION_ADVANCED and HoloVisionAdvanced:
            try:
                self.vision_advanced = HoloVisionAdvanced()
            except Exception as e:
                logger.warning(f"HoloVisionAdvanced init fehlgeschlagen: {e}")

        # --- Audio Enhanced (Speaker, Emotion, Genre, STT) ---
        self.audio_enhanced = None
        if _HAS_AUDIO_ENHANCED and HoloAudioEnhanced:
            try:
                self.audio_enhanced = HoloAudioEnhanced()
            except Exception as e:
                logger.warning(f"HoloAudioEnhanced init fehlgeschlagen: {e}")

        # --- CrossModal (Captioning, Multimodal Sentiment) ---
        self.crossmodal = None
        if _HAS_CROSSMODAL and HoloCrossModal:
            try:
                self.crossmodal = HoloCrossModal()
            except Exception as e:
                logger.warning(f"HoloCrossModal init fehlgeschlagen: {e}")

        logger.info(f"HoloPerceptionUnified v5.0 initialisiert (Modus: {mode.value})")
        self._log_capabilities()

    def _log_capabilities(self):
        """Loggt verfuegbare Faehigkeiten"""
        caps = self.get_capabilities()
        available = [k for k, v in caps.items() if v]
        logger.info(f"Verfuegbare Module: {', '.join(available)}")

    # =========================================================================
    # UNIFIED TEXT ANALYSIS
    # =========================================================================

    def analyze_text(self, text: str,
                     title: str = None,
                     depth: AnalysisDepth = AnalysisDepth.STANDARD) -> ExtendedTextAnalysis:
        """
        Analysiert Text mit allen verfuegbaren Modulen.

        Kombiniert:
        - holo_perception.HoloReader (Basis)
        - holo_text_reader.HoloTextReader (erweitert)
        - Neue Features (Kapitel, Zitate, Lesbarkeit)
        - Optional: LLM-Erweiterung
        """
        result = ExtendedTextAnalysis()

        # --- Basis-Analyse (holo_perception) ---
        if self.reader:
            try:
                basic = self.reader.analyze_text(text, title)
                result.text_id = basic.text_id
                result.word_count = basic.word_count
                result.sentence_count = basic.sentence_count
                result.sentiment = basic.sentiment
                result.sentiment_label = basic.sentiment_label
                result.keywords = basic.keywords
                result.summary = basic.summary
            except Exception as e:
                logger.warning(f"Basis-Textanalyse fehlgeschlagen: {e}")

        # --- Erweiterte Analyse (holo_text_reader) ---
        if self.text_reader and depth in [AnalysisDepth.STANDARD, AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            try:
                extended = self.text_reader.read(text, title=title or "")
                result.facts = extended.facts
                result.entities = extended.entities
                result.topic_category = extended.topic_category.value if hasattr(extended.topic_category, 'value') else str(extended.topic_category)
                result.language = extended.language

                # Keywords ergaenzen
                if extended.keywords:
                    existing = set(result.keywords)
                    for kw in extended.keywords:
                        if kw not in existing:
                            result.keywords.append(kw)
            except Exception as e:
                logger.warning(f"Erweiterte Textanalyse fehlgeschlagen: {e}")

        # --- Neue Features ---
        if depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            # Kapitel
            result.chapters = self.extended_reader.detect_chapters(text)

            # Zitate
            result.quotes = self.extended_reader.extract_quotes(text)

            # Lesbarkeit
            readability, label = self.extended_reader.calculate_readability_german(text)
            result.readability_score = readability
            result.readability_label = label

            # Stil
            result.style_analysis = self.extended_reader.analyze_style(text)

            # Fragen generieren
            result.questions = self.extended_reader.generate_questions(text, result.keywords)

        # --- Enhanced NLP (80%+ Qualitaet) ---
        if self.nlp_enhanced and depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            try:
                nlp_result = self.nlp_enhanced.analyze(text)

                # Bessere Entity-Erkennung
                result.enhanced_entities = nlp_result.get("entities", [])

                # Koreference-Aufloesung
                result.coreference_clusters = nlp_result.get("coreference_clusters", [])

                # Argumentations-Struktur
                result.arguments = nlp_result.get("arguments", [])

                # Ironie-Erkennung
                irony = nlp_result.get("irony")
                if irony:
                    result.irony_detected = irony.is_ironic
                    result.irony_confidence = irony.confidence

                # Autor-Stil-Fingerprint
                fingerprint = nlp_result.get("style_fingerprint")
                if fingerprint:
                    result.author_fingerprint = {
                        "avg_word_length": fingerprint.avg_word_length,
                        "avg_sentence_length": fingerprint.avg_sentence_length,
                        "vocabulary_richness": fingerprint.vocabulary_richness,
                        "hapax_ratio": fingerprint.hapax_legomena_ratio,
                    }
            except Exception as e:
                logger.warning(f"Enhanced NLP fehlgeschlagen: {e}")

        # --- NLP Advanced (Topic Modeling, QA, Relations) ---
        if self.nlp_advanced and depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            try:
                advanced_result = self.nlp_advanced.analyze(text)

                # Topic Modeling
                topics = advanced_result.get("topics", [])
                result.topics = [
                    {"name": t.name, "keywords": t.keywords, "coherence": t.coherence}
                    for t in topics
                ] if topics else []

                # Relation Extraction
                relations = advanced_result.get("relations", [])
                result.relations = [
                    {"subject": r.subject, "predicate": r.predicate, "object": r.object_}
                    for r in relations
                ] if relations else []

                # Timeline
                events = advanced_result.get("timeline", [])
                result.timeline = [
                    {"date": e.date_str, "event": e.event_text, "type": e.event_type}
                    for e in events
                ] if events else []

                # Aspect-based Sentiment
                aspects = advanced_result.get("aspect_sentiments", {})
                if aspects:
                    result.aspect_sentiments = aspects

                # Multi-Label Classification
                labels = advanced_result.get("labels", [])
                if labels:
                    result.labels = labels

            except Exception as e:
                logger.warning(f"NLP Advanced fehlgeschlagen: {e}")

        # --- LLM-Erweiterung ---
        if depth == AnalysisDepth.EXHAUSTIVE and self.llm_enhancer.available:
            if self.mode in [PerceptionMode.LLM_ENHANCED, PerceptionMode.HYBRID, PerceptionMode.AUTO]:
                # Verbesserte Zusammenfassung
                result.llm_summary = self.llm_enhancer.enhance_summary(text, result.summary)

                # Tiefere Einsichten
                analysis_dict = {
                    "topics": result.keywords[:5],
                    "sentiment": result.sentiment_label,
                    "entities": [str(e) for e in result.entities[:5]] if result.entities else []
                }
                result.llm_insights = self.llm_enhancer.extract_insights(text, analysis_dict)

        return result

    # =========================================================================
    # UNIFIED IMAGE ANALYSIS
    # =========================================================================

    def analyze_image(self, image_path: str,
                      depth: AnalysisDepth = AnalysisDepth.STANDARD) -> ExtendedImageAnalysis:
        """
        Analysiert Bild mit allen verfuegbaren Modulen.

        Kombiniert:
        - holo_perception.HoloVision (Basis)
        - Neue Features (OCR, Emotionen, Szene, Qualitaet)
        - Optional: LLM-Beschreibung
        """
        result = ExtendedImageAnalysis()

        if not os.path.exists(image_path):
            logger.error(f"Bild nicht gefunden: {image_path}")
            return result

        # --- Basis-Analyse (holo_perception) ---
        if self.vision:
            try:
                basic = self.vision.analyze_image(image_path)
                if basic:
                    result.image_id = basic.image_id
                    result.width = basic.width
                    result.height = basic.height
                    result.dominant_colors = basic.dominant_colors
                    result.brightness = basic.brightness
                    result.face_count = basic.face_count
            except Exception as e:
                logger.warning(f"Basis-Bildanalyse fehlgeschlagen: {e}")

        # --- Erweiterte Features ---
        if depth in [AnalysisDepth.STANDARD, AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            # OCR
            result.ocr_text = self.extended_vision.extract_ocr_text(image_path)

            # Szene
            result.scene_type = self.extended_vision.classify_scene(image_path)

            # Qualitaet
            result.quality_score = self.extended_vision.analyze_quality(image_path)

        if depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            # Emotionen
            result.emotions = self.extended_vision.detect_emotions_in_faces(image_path)

            # Kunststil
            result.art_style = self.extended_vision.detect_art_style(image_path)

            # Meme-Erkennung
            result.is_meme = self.extended_vision.is_meme(image_path, result.ocr_text)

            # Histogram
            result.histogram = self.extended_vision.get_histogram(image_path)

        # --- Enhanced Vision (80%+ Qualitaet) ---
        if self.vision_enhanced and depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            try:
                vision_result = self.vision_enhanced.analyze_image(image_path)

                # Detaillierte Gesichtsanalyse
                faces = vision_result.get("faces", [])
                if faces:
                    result.face_analyses = [
                        {
                            "emotion": f.emotion.value if hasattr(f, 'emotion') else str(f.emotion),
                            "emotion_confidence": f.emotion_confidence,
                            "is_smiling": f.is_smiling,
                            "estimated_age": f.estimated_age,
                            "estimated_gender": f.estimated_gender,
                            "has_glasses": f.has_glasses,
                            "head_pose": f.head_pose,
                        }
                        for f in faces
                    ]

                # Fortgeschrittene Farbanalyse
                colors = vision_result.get("colors")
                if colors:
                    result.color_analysis = {
                        "dominant_colors": colors.dominant_colors,
                        "color_names": colors.color_names,
                        "color_harmony": colors.color_harmony,
                        "brightness_distribution": colors.brightness_distribution,
                    }
                    result.color_harmony = colors.color_harmony
                    result.color_temperature = colors.color_temperature

                # Fortgeschrittene Szenenanalyse
                scene = vision_result.get("scene")
                if scene:
                    result.scene_analysis = {
                        "scene_type": scene.scene_type.value if hasattr(scene.scene_type, 'value') else str(scene.scene_type),
                        "confidence": scene.confidence,
                        "attributes": scene.scene_attributes,
                        "is_blurry": scene.is_blurry,
                        "is_noisy": scene.is_noisy,
                    }
                    result.composition = scene.composition

            except Exception as e:
                logger.warning(f"Enhanced Vision fehlgeschlagen: {e}")

        # --- Vision Advanced (Objects, Faces, QR, Layout) ---
        if self.vision_advanced and depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            try:
                advanced_result = self.vision_advanced.analyze(
                    image_path,
                    features=['objects', 'faces', 'codes', 'logos', 'layout']
                )

                # Object Detection
                objects = advanced_result.get('objects', [])
                result.detected_objects = objects

                # Face Recognition
                faces = advanced_result.get('faces', [])
                result.recognized_faces = faces

                # QR/Barcode
                codes = advanced_result.get('codes', [])
                result.qr_codes = codes

                # Logo Detection
                logos = advanced_result.get('logos', [])
                result.logos = logos

                # Document Layout
                layout = advanced_result.get('layout')
                if layout:
                    result.document_layout = layout

                # Image Hash
                similarity = self.vision_advanced.image_similarity
                fp = similarity.compute_hash(image_path)
                if fp:
                    result.similar_hash = fp

            except Exception as e:
                logger.warning(f"Vision Advanced fehlgeschlagen: {e}")

        # --- CrossModal (Image Captioning) ---
        if self.crossmodal and depth in [AnalysisDepth.DEEP, AnalysisDepth.EXHAUSTIVE]:
            try:
                caption_result = self.crossmodal.generate_caption(
                    image_path,
                    objects=result.detected_objects if result.detected_objects else None
                )
                result.image_caption = caption_result.get('caption', '')
            except Exception as e:
                logger.warning(f"CrossModal Captioning fehlgeschlagen: {e}")

        # --- LLM-Beschreibung ---
        if depth == AnalysisDepth.EXHAUSTIVE and self.llm_enhancer.available:
            if self.mode in [PerceptionMode.LLM_ENHANCED, PerceptionMode.HYBRID, PerceptionMode.AUTO]:
                analysis_dict = {
                    "width": result.width,
                    "height": result.height,
                    "color_names": [str(c) for c in result.dominant_colors[:3]],
                    "brightness": result.brightness,
                    "face_count": result.face_count,
                    "color_mood": result.scene_type,
                    "ocr_text": result.ocr_text,
                }
                result.llm_description = self.llm_enhancer.describe_image(analysis_dict)

        return result

    # =========================================================================
    # NEUE MEDIEN-ANALYSE (Audio, Video, Document)
    # =========================================================================

    def analyze_audio(self, audio_path: str) -> Optional[Any]:
        """Analysiert Audio/Musik-Datei"""
        if not self.audio:
            logger.warning("HoloAudio nicht verfuegbar")
            return None

        try:
            return self.audio.analyze(audio_path)
        except Exception as e:
            logger.error(f"Audio-Analyse fehlgeschlagen: {e}")
            return None

    def analyze_video(self, video_path: str) -> Optional[Any]:
        """Analysiert Video-Datei"""
        if not self.video:
            logger.warning("HoloVideo nicht verfuegbar")
            return None

        try:
            return self.video.analyze(video_path)
        except Exception as e:
            logger.error(f"Video-Analyse fehlgeschlagen: {e}")
            return None

    def analyze_document(self, doc_path: str) -> Optional[Any]:
        """Analysiert Dokument (PDF, DOCX, MD)"""
        if not self.document:
            logger.warning("HoloDocument nicht verfuegbar")
            return None

        try:
            return self.document.parse(doc_path)
        except Exception as e:
            logger.error(f"Dokument-Analyse fehlgeschlagen: {e}")
            return None

    # =========================================================================
    # ENHANCED AUDIO ANALYSIS
    # =========================================================================

    def analyze_audio_enhanced(self, audio_path: str,
                                features: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Erweiterte Audio-Analyse mit 80%+ Standalone-Qualitaet.

        Features: transcription, emotion, genre, events, segments, fingerprint
        """
        if not self.audio_enhanced:
            logger.warning("HoloAudioEnhanced nicht verfuegbar")
            return None

        try:
            return self.audio_enhanced.analyze(audio_path, features)
        except Exception as e:
            logger.error(f"Enhanced Audio-Analyse fehlgeschlagen: {e}")
            return None

    def identify_speaker(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """Identifiziere Sprecher in Audio"""
        if not self.audio_enhanced:
            return None
        return self.audio_enhanced.identify_speaker(audio_path)

    def register_speaker(self, audio_path: str, speaker_id: str,
                         name: str = None) -> bool:
        """Registriere neuen Sprecher"""
        if not self.audio_enhanced:
            return False
        return self.audio_enhanced.register_speaker(audio_path, speaker_id, name)

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transkribiere Audio zu Text"""
        if not self.audio_enhanced:
            return None
        result = self.audio_enhanced.analyze(audio_path, features=['transcription'])
        return result.get('transcription', {}).get('text', '')

    # =========================================================================
    # CROSSMODAL ANALYSIS
    # =========================================================================

    def analyze_multimodal(self, text: str = None,
                           image = None,
                           audio: str = None,
                           features: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Crossmodale Analyse (Text + Bild + Audio).

        Features: caption, sentiment, match, fusion
        """
        if not self.crossmodal:
            logger.warning("HoloCrossModal nicht verfuegbar")
            return None

        try:
            return self.crossmodal.analyze(text, image, audio, features)
        except Exception as e:
            logger.error(f"Crossmodal-Analyse fehlgeschlagen: {e}")
            return None

    def get_multimodal_sentiment(self, text: str = None,
                                  image = None,
                                  audio: str = None) -> Optional[Dict[str, Any]]:
        """Analysiere Sentiment ueber mehrere Modalitaeten"""
        if not self.crossmodal:
            return None
        return self.crossmodal.analyze_multimodal_sentiment(text, image, audio)

    def generate_image_caption(self, image) -> Optional[str]:
        """Generiere Bildbeschreibung"""
        if not self.crossmodal:
            return None
        result = self.crossmodal.generate_caption(image)
        return result.get('caption', '')

    def create_multimodal_summary(self, text: str = None,
                                   images: List = None,
                                   audio_transcriptions: List[str] = None) -> Optional[Dict[str, Any]]:
        """Erstelle multimodale Zusammenfassung"""
        if not self.crossmodal:
            return None
        return self.crossmodal.create_summary(text, images, audio_transcriptions)

    # =========================================================================
    # NLP ADVANCED FEATURES
    # =========================================================================

    def extract_topics(self, text: str, n_topics: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Extrahiere Themen aus Text"""
        if not self.nlp_advanced:
            return None
        result = self.nlp_advanced.analyze(text)
        return result.get('topics', [])

    def extract_relations(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Extrahiere Relationen (Subject-Predicate-Object)"""
        if not self.nlp_advanced:
            return None
        result = self.nlp_advanced.analyze(text)
        return result.get('relations', [])

    def extract_timeline(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Extrahiere Zeitlinie mit Events"""
        if not self.nlp_advanced:
            return None
        result = self.nlp_advanced.analyze(text)
        return result.get('timeline', [])

    def answer_question(self, text: str, question: str) -> Optional[str]:
        """Beantworte Frage basierend auf Text"""
        if not self.nlp_advanced:
            return None
        return self.nlp_advanced.qa.answer(text, question)

    def generate_text(self, prompt: str, max_length: int = 100) -> Optional[str]:
        """Generiere Text basierend auf Prompt"""
        if not self.nlp_advanced:
            return None
        return self.nlp_advanced.text_generator.generate(prompt, max_length)

    # =========================================================================
    # VISION ADVANCED FEATURES
    # =========================================================================

    def detect_objects(self, image) -> Optional[List[Dict[str, Any]]]:
        """Erkenne Objekte im Bild"""
        if not self.vision_advanced:
            return None
        result = self.vision_advanced.analyze(image, features=['objects'])
        return result.get('objects', [])

    def read_qr_codes(self, image) -> Optional[List[Dict[str, Any]]]:
        """Lese QR-Codes und Barcodes"""
        if not self.vision_advanced:
            return None
        result = self.vision_advanced.analyze(image, features=['codes'])
        return result.get('codes', [])

    def detect_logos(self, image) -> Optional[List[Dict[str, Any]]]:
        """Erkenne Logos im Bild"""
        if not self.vision_advanced:
            return None
        result = self.vision_advanced.analyze(image, features=['logos'])
        return result.get('logos', [])

    def analyze_document_layout(self, image) -> Optional[Dict[str, Any]]:
        """Analysiere Dokumentlayout"""
        if not self.vision_advanced:
            return None
        result = self.vision_advanced.analyze(image, features=['layout'])
        return result.get('layout')

    def compare_images(self, image1, image2) -> Optional[Dict[str, Any]]:
        """Vergleiche zwei Bilder"""
        if not self.vision_advanced:
            return None
        return self.vision_advanced.compare_images(image1, image2)

    def register_face(self, image, name: str) -> bool:
        """Registriere Gesicht fuer Erkennung"""
        if not self.vision_advanced:
            return False
        return self.vision_advanced.register_face(name, image)

    # =========================================================================
    # MEDIA INTEGRATION
    # =========================================================================

    def add_to_journal(self, media_type: str, analysis: Any,
                       emotion: str = None, note: str = None) -> bool:
        """Fuegt Media-Analyse zum Tagebuch hinzu"""
        if not self.media_journal:
            return False

        try:
            self.media_journal.add_entry(
                media_type=media_type,
                analysis=analysis,
                emotion=emotion,
                note=note
            )
            return True
        except Exception as e:
            logger.error(f"Journal-Eintrag fehlgeschlagen: {e}")
            return False

    def add_to_knowledge_graph(self, subject: str, predicate: str, obj: str,
                               confidence: float = 1.0) -> bool:
        """Fuegt Wissen zum Knowledge Graph hinzu"""
        if not self.knowledge_graph:
            return False

        try:
            self.knowledge_graph.add_relation(subject, predicate, obj, confidence)
            return True
        except Exception as e:
            logger.error(f"Knowledge Graph Eintrag fehlgeschlagen: {e}")
            return False

    def get_recommendations(self, context: Dict = None) -> List[Any]:
        """Holt Empfehlungen basierend auf Kontext"""
        if not self.recommendation_engine:
            return []

        try:
            return self.recommendation_engine.get_recommendations(context or {})
        except Exception as e:
            logger.error(f"Empfehlungen fehlgeschlagen: {e}")
            return []

    # =========================================================================
    # CAPABILITIES & UTILITIES
    # =========================================================================

    def get_capabilities(self) -> Dict[str, bool]:
        """Gibt verfuegbare Faehigkeiten zurueck"""
        return {
            # Basis
            "text_analysis": self.reader is not None,
            "image_analysis": self.vision is not None,
            "extended_text": self.text_reader is not None,
            "vector_engine": self.vector_engine is not None,

            # Neue Features
            "chapter_detection": True,
            "quote_extraction": True,
            "readability_german": True,
            "style_analysis": True,
            "ocr": self.extended_vision._has_tesseract,
            "emotion_detection": self.extended_vision._has_cv2,
            "scene_classification": self.extended_vision._has_cv2,
            "quality_analysis": self.extended_vision._has_cv2,

            # Enhanced NLP (80%+ Qualitaet)
            "enhanced_ner": self.nlp_enhanced is not None,
            "coreference_resolution": self.nlp_enhanced is not None,
            "argument_detection": self.nlp_enhanced is not None,
            "irony_detection": self.nlp_enhanced is not None,
            "plagiarism_detection": self.nlp_enhanced is not None,
            "author_fingerprint": self.nlp_enhanced is not None,

            # Enhanced Vision (80%+ Qualitaet)
            "enhanced_emotion": self.vision_enhanced is not None,
            "pose_estimation": self.vision_enhanced is not None,
            "object_tracking": self.vision_enhanced is not None,
            "image_text_matching": self.vision_enhanced is not None,
            "enhanced_scene": self.vision_enhanced is not None,
            "color_harmony": self.vision_enhanced is not None,

            # NLP Advanced
            "topic_modeling": self.nlp_advanced is not None,
            "relation_extraction": self.nlp_advanced is not None,
            "timeline_extraction": self.nlp_advanced is not None,
            "question_answering": self.nlp_advanced is not None,
            "text_generation": self.nlp_advanced is not None,
            "aspect_sentiment": self.nlp_advanced is not None,
            "multi_label_classification": self.nlp_advanced is not None,

            # Vision Advanced
            "object_detection": self.vision_advanced is not None,
            "face_recognition": self.vision_advanced is not None,
            "qr_barcode_reader": self.vision_advanced is not None,
            "logo_detection": self.vision_advanced is not None,
            "document_layout": self.vision_advanced is not None,
            "image_similarity": self.vision_advanced is not None,
            "handwriting_recognition": self.vision_advanced is not None,

            # Audio Enhanced
            "speaker_recognition": self.audio_enhanced is not None,
            "voice_emotion": self.audio_enhanced is not None,
            "music_genre": self.audio_enhanced is not None,
            "speech_to_text": self.audio_enhanced is not None,
            "audio_fingerprint": self.audio_enhanced is not None,
            "sound_events": self.audio_enhanced is not None,

            # CrossModal
            "image_captioning": self.crossmodal is not None,
            "multimodal_sentiment": self.crossmodal is not None,
            "image_text_matching_cm": self.crossmodal is not None,
            "context_fusion": self.crossmodal is not None,
            "multimodal_summary": self.crossmodal is not None,

            # Neue Module
            "audio_analysis": self.audio is not None,
            "video_analysis": self.video is not None,
            "document_parsing": self.document is not None,
            "media_journal": self.media_journal is not None,
            "knowledge_graph": self.knowledge_graph is not None,
            "recommendations": self.recommendation_engine is not None,

            # LLM
            "llm_enhancement": self.llm_enhancer.available,
        }

    def set_llm(self, llm_instance):
        """Setzt LLM-Instanz nachtraeglich"""
        self.llm_enhancer.set_llm(llm_instance)
        logger.info(f"LLM gesetzt: {llm_instance is not None}")

    def set_mode(self, mode: PerceptionMode):
        """Aendert den Wahrnehmungs-Modus"""
        self.mode = mode
        logger.info(f"Modus geaendert: {mode.value}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# =============================================================================
# ADVANCED PERCEPTION: Attention Mechanism
# =============================================================================

class AttentionMechanism:
    """
    Attention-basierte Wahrnehmung - fokussiert auf relevante Inhalte.

    Lernt was für den User wichtig ist und gewichtet Analyse entsprechend.
    """

    def __init__(self):
        # Attention-Weights pro Content-Typ
        self.content_weights: Dict[str, float] = {
            "sentiment": 0.8,
            "entities": 0.7,
            "keywords": 0.7,
            "emotion": 0.9,
            "facts": 0.6,
            "style": 0.5,
            "structure": 0.4,
        }

        # Kontext-basierte Modifikatoren
        self.context_modifiers: Dict[str, Dict[str, float]] = {
            "emotional_conversation": {"emotion": 1.5, "sentiment": 1.3, "facts": 0.5},
            "technical_discussion": {"facts": 1.5, "keywords": 1.3, "emotion": 0.5},
            "casual_chat": {"sentiment": 1.2, "style": 1.2, "structure": 0.3},
            "question_answering": {"facts": 1.5, "entities": 1.3, "keywords": 1.2},
        }

        # Gelernte User-Präferenzen
        self.user_preferences: Dict[str, float] = {}

        # Attention History für Lernen
        self.attention_history: List[Dict] = []

        logger.info("👁️ AttentionMechanism initialisiert")

    def compute_attention(self, context: Dict = None) -> Dict[str, float]:
        """Berechnet Attention-Weights basierend auf Kontext"""
        weights = dict(self.content_weights)

        # Kontext-Modifikatoren anwenden
        if context:
            context_type = context.get("conversation_type", "casual_chat")
            modifiers = self.context_modifiers.get(context_type, {})

            for feature, modifier in modifiers.items():
                if feature in weights:
                    weights[feature] *= modifier

            # User-Mood berücksichtigen
            user_mood = context.get("user_mood", 0)
            if isinstance(user_mood, (int, float)):
                if user_mood < -0.3:  # Negativ
                    weights["emotion"] *= 1.3
                    weights["sentiment"] *= 1.2

        # User-Präferenzen anwenden
        for feature, pref in self.user_preferences.items():
            if feature in weights:
                weights[feature] *= (0.5 + pref)  # 0.5x to 1.5x

        # Normalisieren
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return weights

    def focus_analysis(self, analysis_result: Dict, context: Dict = None) -> Dict:
        """Filtert Analyse-Ergebnis basierend auf Attention"""
        weights = self.compute_attention(context)

        focused = {
            "weights_applied": weights,
            "priority_features": [],
            "filtered_result": {},
        }

        # Features nach Gewicht sortieren
        sorted_features = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        focused["priority_features"] = [f[0] for f in sorted_features[:5]]

        # Relevante Features extrahieren
        for feature, weight in sorted_features:
            if weight > 0.1 and feature in analysis_result:
                focused["filtered_result"][feature] = analysis_result[feature]

        return focused

    def learn_preference(self, feature: str, was_useful: bool, feedback_strength: float = 0.5):
        """Lernt User-Präferenzen aus Feedback"""
        current = self.user_preferences.get(feature, 0.5)

        if was_useful:
            new_pref = current + (1 - current) * 0.1 * feedback_strength
        else:
            new_pref = current - current * 0.1 * feedback_strength

        self.user_preferences[feature] = max(0.1, min(1.0, new_pref))

        # History speichern
        self.attention_history.append({
            "timestamp": datetime.now().isoformat(),
            "feature": feature,
            "was_useful": was_useful,
            "new_preference": self.user_preferences[feature],
        })

    def get_stats(self) -> Dict:
        return {
            "learned_preferences": dict(self.user_preferences),
            "history_size": len(self.attention_history),
        }


# =============================================================================
# ADVANCED PERCEPTION: Perception Learner
# =============================================================================

class PerceptionLearner:
    """
    Lernt was für den User bei der Wahrnehmung wichtig ist.

    Basiert auf:
    - Welche Analyse-Ergebnisse der User nutzt
    - Feedback auf Zusammenfassungen
    - Implizite Signale (Nachfragen, Reaktionen)
    """

    def __init__(self):
        # Feature-Relevanz pro Kategorie
        self.feature_relevance: Dict[str, Dict[str, float]] = {}

        # Kategorie-Tracking
        self.category_interactions: Dict[str, int] = {}

        # Feedback-History
        self.feedback_history: List[Dict] = []

        logger.info("📚 PerceptionLearner initialisiert")

    def record_usage(self, category: str, features_used: List[str],
                     features_ignored: List[str]):
        """Zeichnet auf welche Features genutzt wurden"""
        if category not in self.feature_relevance:
            self.feature_relevance[category] = {}

        # Used features werden wichtiger
        for feature in features_used:
            current = self.feature_relevance[category].get(feature, 0.5)
            self.feature_relevance[category][feature] = min(1.0, current + 0.1)

        # Ignored features werden unwichtiger
        for feature in features_ignored:
            current = self.feature_relevance[category].get(feature, 0.5)
            self.feature_relevance[category][feature] = max(0.1, current - 0.05)

        self.category_interactions[category] = self.category_interactions.get(category, 0) + 1

    def record_feedback(self, category: str, feature: str,
                        feedback: str, value: float = 0.0):
        """Zeichnet explizites Feedback auf"""
        self.feedback_history.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "feature": feature,
            "feedback": feedback,
            "value": value,
        })

        # Relevanz anpassen
        if category not in self.feature_relevance:
            self.feature_relevance[category] = {}

        current = self.feature_relevance[category].get(feature, 0.5)
        adjustment = value * 0.2  # -1 to +1 -> -0.2 to +0.2
        self.feature_relevance[category][feature] = max(0.1, min(1.0, current + adjustment))

    def get_recommended_features(self, category: str, limit: int = 5) -> List[str]:
        """Gibt empfohlene Features für eine Kategorie zurück"""
        relevance = self.feature_relevance.get(category, {})
        if not relevance:
            return ["sentiment", "keywords", "entities", "emotion", "summary"]

        sorted_features = sorted(relevance.items(), key=lambda x: x[1], reverse=True)
        return [f[0] for f in sorted_features[:limit]]

    def should_include_feature(self, category: str, feature: str) -> bool:
        """Prüft ob ein Feature für diese Kategorie relevant ist"""
        relevance = self.feature_relevance.get(category, {}).get(feature, 0.5)
        return relevance > 0.3

    def get_stats(self) -> Dict:
        return {
            "categories_learned": len(self.feature_relevance),
            "total_interactions": sum(self.category_interactions.values()),
            "feedback_count": len(self.feedback_history),
        }


# =============================================================================
# ADVANCED PERCEPTION: Perceptual Continuity
# =============================================================================

class PerceptualContinuity:
    """
    Trackt wie sich Wahrnehmung über Zeit entwickelt.

    Ermöglicht:
    - Erkennen von Veränderungen
    - Kontinuität über Turns hinweg
    - Vorhersage von Wahrnehmungs-Trajektorien
    """

    def __init__(self, memory_size: int = 100):
        self.memory_size = memory_size

        # Perception-Memory: item_id -> [perceptions over time]
        self.perception_memory: Dict[str, List[Dict]] = {}

        # Session-Perceptions (aktuelle Konversation)
        self.session_perceptions: List[Dict] = []

        # Deltas zwischen Wahrnehmungen
        self.perception_deltas: List[Dict] = []

        logger.info("🔄 PerceptualContinuity initialisiert")

    def add_perception(self, item_id: str, perception: Dict,
                       item_type: str = "text"):
        """Fügt neue Wahrnehmung hinzu"""
        timestamp = datetime.now().isoformat()

        entry = {
            "timestamp": timestamp,
            "item_type": item_type,
            "perception": perception,
        }

        # Zum Item-Memory hinzufügen
        if item_id not in self.perception_memory:
            self.perception_memory[item_id] = []

        old_perceptions = self.perception_memory[item_id]
        self.perception_memory[item_id].append(entry)

        # Memory begrenzen
        if len(self.perception_memory[item_id]) > 20:
            self.perception_memory[item_id] = self.perception_memory[item_id][-20:]

        # Delta berechnen wenn vorherige Wahrnehmung existiert
        if old_perceptions:
            delta = self._compute_delta(old_perceptions[-1]["perception"], perception)
            self.perception_deltas.append({
                "item_id": item_id,
                "timestamp": timestamp,
                "delta": delta,
            })

        # Session-Memory
        self.session_perceptions.append(entry)
        if len(self.session_perceptions) > self.memory_size:
            self.session_perceptions = self.session_perceptions[-self.memory_size:]

    def _compute_delta(self, old: Dict, new: Dict) -> Dict:
        """Berechnet Unterschied zwischen zwei Wahrnehmungen"""
        delta = {
            "changed_features": [],
            "sentiment_change": 0.0,
            "overall_change": 0.0,
        }

        # Sentiment-Änderung
        old_sent = old.get("sentiment", 0)
        new_sent = new.get("sentiment", 0)
        delta["sentiment_change"] = new_sent - old_sent

        # Feature-Änderungen zählen
        changes = 0
        for key in set(list(old.keys()) + list(new.keys())):
            if old.get(key) != new.get(key):
                delta["changed_features"].append(key)
                changes += 1

        delta["overall_change"] = changes / max(1, len(set(list(old.keys()) + list(new.keys()))))

        return delta

    def get_perception_history(self, item_id: str) -> List[Dict]:
        """Gibt Wahrnehmungs-Historie für ein Item zurück"""
        return self.perception_memory.get(item_id, [])

    def detect_significant_change(self, item_id: str, threshold: float = 0.3) -> Optional[Dict]:
        """Erkennt signifikante Wahrnehmungs-Änderungen"""
        history = self.perception_memory.get(item_id, [])
        if len(history) < 2:
            return None

        # Letzte Änderung prüfen
        old = history[-2]["perception"]
        new = history[-1]["perception"]
        delta = self._compute_delta(old, new)

        if delta["overall_change"] >= threshold:
            return {
                "item_id": item_id,
                "change_detected": True,
                "delta": delta,
                "previous": old,
                "current": new,
            }

        return None

    def get_session_summary(self) -> Dict:
        """Gibt Zusammenfassung der Session-Wahrnehmungen"""
        if not self.session_perceptions:
            return {"count": 0}

        sentiments = []
        for p in self.session_perceptions:
            sent = p["perception"].get("sentiment", 0)
            if sent:
                sentiments.append(sent)

        return {
            "count": len(self.session_perceptions),
            "avg_sentiment": sum(sentiments) / max(1, len(sentiments)),
            "sentiment_trend": "rising" if len(sentiments) > 1 and sentiments[-1] > sentiments[0] else "falling",
            "types": list(set(p["item_type"] for p in self.session_perceptions)),
        }

    def get_stats(self) -> Dict:
        return {
            "items_tracked": len(self.perception_memory),
            "session_perceptions": len(self.session_perceptions),
            "deltas_recorded": len(self.perception_deltas),
        }


# =============================================================================
# ADVANCED PERCEPTION: Salience Predictor
# =============================================================================

class SaliencePredictor:
    """
    Sagt vorher was für den User wichtig sein wird.

    Ermöglicht proaktive Analyse der relevanten Aspekte.
    """

    def __init__(self):
        # Gelernte Salience-Patterns
        self.salience_patterns: Dict[str, Dict[str, float]] = {
            "default": {"emotion": 0.8, "sentiment": 0.7, "entities": 0.6},
        }

        # Kontext-zu-Salience Mapping
        self.context_salience: Dict[str, List[str]] = {
            "anime": ["characters", "emotion", "story"],
            "gaming": ["gameplay", "graphics", "story"],
            "tech": ["features", "specs", "comparison"],
            "personal": ["emotion", "sentiment", "empathy"],
        }

        # Prediction History
        self.predictions: List[Dict] = []
        self.prediction_accuracy: List[float] = []

        logger.info("🎯 SaliencePredictor initialisiert")

    def predict_salience(self, context: Dict, content_preview: str = "") -> Dict:
        """Sagt vorher welche Aspekte salient sein werden"""
        prediction = {
            "high_salience": [],
            "medium_salience": [],
            "low_salience": [],
            "confidence": 0.5,
        }

        # Kontext-basierte Vorhersage
        topic = context.get("topic", "").lower()
        user_interest = context.get("user_interest", "default")

        # Pattern matching
        for category, features in self.context_salience.items():
            if category in topic or category in user_interest:
                prediction["high_salience"].extend(features)
                prediction["confidence"] += 0.1

        # Content-basierte Hinweise
        if content_preview:
            if "?" in content_preview:
                prediction["high_salience"].append("answer_quality")
            if any(word in content_preview.lower() for word in ["gefühl", "fühle", "traurig", "freue"]):
                prediction["high_salience"].append("emotion")
                prediction["confidence"] += 0.1

        # Default wenn nichts gefunden
        if not prediction["high_salience"]:
            prediction["high_salience"] = ["sentiment", "keywords", "summary"]

        # Confidence begrenzen
        prediction["confidence"] = min(0.95, prediction["confidence"])

        # Speichern
        self.predictions.append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "prediction": prediction,
        })

        return prediction

    def record_accuracy(self, prediction: Dict, actual_salience: List[str]):
        """Zeichnet auf wie genau die Vorhersage war"""
        predicted = set(prediction.get("high_salience", []))
        actual = set(actual_salience)

        if not predicted:
            accuracy = 0.0
        else:
            overlap = len(predicted & actual)
            accuracy = overlap / len(predicted)

        self.prediction_accuracy.append(accuracy)

        # Nur letzte 100
        if len(self.prediction_accuracy) > 100:
            self.prediction_accuracy = self.prediction_accuracy[-100:]

    def get_recommended_analysis(self, context: Dict) -> List[str]:
        """Gibt empfohlene Analyse-Features basierend auf Vorhersage"""
        prediction = self.predict_salience(context)
        return prediction["high_salience"] + prediction["medium_salience"]

    def get_stats(self) -> Dict:
        avg_accuracy = sum(self.prediction_accuracy) / max(1, len(self.prediction_accuracy))
        return {
            "total_predictions": len(self.predictions),
            "avg_accuracy": avg_accuracy,
            "patterns_count": len(self.salience_patterns),
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_perception(mode: str = "hybrid", llm=None) -> HoloPerceptionUnified:
    """Erstellt eine HoloPerceptionUnified-Instanz"""
    mode_map = {
        "standalone": PerceptionMode.STANDALONE,
        "llm": PerceptionMode.LLM_ENHANCED,
        "hybrid": PerceptionMode.HYBRID,
        "auto": PerceptionMode.AUTO,
    }
    return HoloPerceptionUnified(
        mode=mode_map.get(mode, PerceptionMode.HYBRID),
        llm_instance=llm
    )


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO PERCEPTION UNIFIED v5.0 TEST")
    print("Vollstaendig integriertes System mit 80%+ Standalone-Qualitaet!")
    print("=" * 70)

    perception = HoloPerceptionUnified(mode=PerceptionMode.STANDALONE)

    # Capabilities
    print("\nVerfuegbare Faehigkeiten:")
    caps = perception.get_capabilities()
    for cap, available in sorted(caps.items()):
        status = "+" if available else "-"
        print(f"  [{status}] {cap}")

    # Text-Analyse Test
    print("\n" + "-" * 50)
    print("TEXT-ANALYSE TEST")
    print("-" * 50)

    test_text = """
    Kapitel 1: Die Entdeckung

    Es war ein regnerischer Novembertag, als Dr. Maria Schmidt eine
    bahnbrechende Entdeckung machte. "Das ist unglaublich!", rief sie
    begeistert. Die Forscherin hatte nach 15 Jahren Arbeit endlich den
    Durchbruch geschafft.

    Das neue Verfahren koennte die Energieproduktion revolutionieren.
    Experten schaetzen das Einsparpotential auf 40% bis 2030.
    Die Universitaet Berlin plant bereits weitere Studien.

    Kapitel 2: Die Reaktionen

    Die wissenschaftliche Gemeinschaft reagierte begeistert.
    Professor Hans Mueller von der TU Muenchen erklaerte:
    "Dies ist ein Meilenstein fuer die Forschung."
    """

    print("\nAnalysiere Text (DEEP)...")
    result = perception.analyze_text(test_text, title="Die Entdeckung", depth=AnalysisDepth.DEEP)

    print(f"\nWoerter: {result.word_count}")
    print(f"Saetze: {result.sentence_count}")
    print(f"Sentiment: {result.sentiment:.2f} ({result.sentiment_label})")
    print(f"Sprache: {result.language}")
    print(f"Kategorie: {result.topic_category}")
    print(f"Lesbarkeit: {result.readability_score} ({result.readability_label})")

    print(f"\nKeywords: {', '.join(result.keywords[:8])}")

    print(f"\nKapitel erkannt: {len(result.chapters)}")
    for ch in result.chapters:
        print(f"  - {ch['title']}")

    print(f"\nZitate: {len(result.quotes)}")
    for q in result.quotes[:3]:
        print(f'  "{q[:50]}..."')

    print(f"\nStil-Analyse:")
    for key, val in result.style_analysis.items():
        print(f"  {key}: {val}")

    print(f"\nGenerierte Fragen:")
    for q in result.questions[:5]:
        print(f"  - {q}")

    print(f"\nFakten: {len(result.facts)}")

    print(f"\nZusammenfassung: {result.summary}")

    print("\n" + "=" * 70)
    print("TEST ABGESCHLOSSEN")
    print("=" * 70)
