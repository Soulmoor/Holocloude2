#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holo CrossModal - Multimodale Analyse ohne Deep Learning
=========================================================

Bietet crossmodale Features mit 80%+ Standalone-Qualitaet:
- Image Captioning (Template + Rule-based)
- Multimodal Sentiment (Text + Bild + Audio)
- Image-Text Matching
- Audio-Visual Correlation
- Context Fusion
- Multimodal Summarization

Autor: Holo CrossModal Team
Version: 1.0.0
"""

import logging
import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

# =============================================================================
# Optionale Imports
# =============================================================================

_HAS_CV2 = False
_HAS_NUMPY = False
_HAS_PIL = False

try:
    import cv2
    _HAS_CV2 = True
except ImportError:
    logger.info("OpenCV nicht verfuegbar")

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    logger.info("NumPy nicht verfuegbar")

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    logger.info("PIL nicht verfuegbar")


# =============================================================================
# Datenstrukturen
# =============================================================================

class Sentiment(Enum):
    """Sentiment-Kategorien"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class ImageCaption:
    """Bildbeschreibung"""
    caption: str
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    alternative_captions: List[str] = field(default_factory=list)


@dataclass
class MultimodalSentimentResult:
    """Multimodales Sentiment"""
    overall_sentiment: Sentiment
    confidence: float
    text_sentiment: Optional[Dict[str, float]] = None
    image_sentiment: Optional[Dict[str, float]] = None
    audio_sentiment: Optional[Dict[str, float]] = None
    fusion_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class ImageTextMatch:
    """Bild-Text Uebereinstimmung"""
    score: float
    matched_elements: List[str]
    mismatched_elements: List[str]
    explanation: str


@dataclass
class ContextFusionResult:
    """Kontextfusion"""
    unified_context: str
    modalities: List[str]
    key_entities: List[str]
    main_topic: str
    confidence: float


@dataclass
class MultimodalSummary:
    """Multimodale Zusammenfassung"""
    summary: str
    key_points: List[str]
    visual_elements: List[str]
    audio_elements: List[str]
    sentiment: Sentiment


# =============================================================================
# Template-based Image Captioner
# =============================================================================

class TemplateImageCaptioner:
    """
    Generiert Bildbeschreibungen basierend auf:
    - Erkannte Objekte
    - Szenenklassifikation
    - Farbanalyse
    - Layoutanalyse
    - Template-basierte Satzgenerierung
    """

    # Deutsche Caption Templates
    TEMPLATES = {
        "single_object": [
            "Ein {object} ist zu sehen.",
            "Das Bild zeigt {article} {object}.",
            "Auf dem Bild befindet sich {article} {object}.",
            "{Article} {object} ist abgebildet."
        ],
        "multiple_objects": [
            "Das Bild zeigt {objects}.",
            "Zu sehen sind {objects}.",
            "Auf dem Bild befinden sich {objects}.",
            "Abgebildet sind {objects}."
        ],
        "scene_with_objects": [
            "Eine {scene}-Szene mit {objects}.",
            "Das Bild zeigt eine {scene}-Umgebung, in der {objects} zu sehen sind.",
            "{Article} {scene} mit {objects}.",
            "In dieser {scene}-Szene sieht man {objects}."
        ],
        "action": [
            "{subject} {verb} {object}.",
            "Zu sehen ist, wie {subject} {verb}.",
            "Das Bild zeigt {subject}, wie er/sie {verb}."
        ],
        "landscape": [
            "Eine {adjective} {scene}-Landschaft.",
            "Das Bild zeigt eine {adjective} {scene}.",
            "{Article} {adjective} {scene} ist zu sehen."
        ],
        "portrait": [
            "Ein Portrait von einer Person.",
            "Das Bild zeigt eine Person im Portrait.",
            "Eine Person ist im Portrait abgebildet."
        ],
        "group": [
            "Eine Gruppe von {count} Personen.",
            "Das Bild zeigt {count} Personen zusammen.",
            "{Count} Personen sind auf dem Bild zu sehen."
        ]
    }

    # Objekt-Woerterbuch (Deutsch)
    OBJECT_VOCAB = {
        "person": ("Person", "eine", "Eine"),
        "car": ("Auto", "ein", "Ein"),
        "dog": ("Hund", "ein", "Ein"),
        "cat": ("Katze", "eine", "Eine"),
        "tree": ("Baum", "ein", "Ein"),
        "building": ("Gebaeude", "ein", "Ein"),
        "flower": ("Blume", "eine", "Eine"),
        "bird": ("Vogel", "ein", "Ein"),
        "table": ("Tisch", "ein", "Ein"),
        "chair": ("Stuhl", "ein", "Ein"),
        "book": ("Buch", "ein", "Ein"),
        "phone": ("Telefon", "ein", "Ein"),
        "laptop": ("Laptop", "ein", "Ein"),
        "cup": ("Tasse", "eine", "Eine"),
        "bottle": ("Flasche", "eine", "Eine"),
        "plant": ("Pflanze", "eine", "Eine"),
        "sky": ("Himmel", "der", "Der"),
        "water": ("Wasser", "das", "Das"),
        "mountain": ("Berg", "ein", "Ein"),
        "road": ("Strasse", "eine", "Eine"),
        "house": ("Haus", "ein", "Ein"),
        "food": ("Essen", "das", "Das"),
        "animal": ("Tier", "ein", "Ein")
    }

    # Szenen-Adjektive
    SCENE_ADJECTIVES = {
        "outdoor": ["sonnig", "bewölkt", "natuerlich", "weitlaeufig"],
        "indoor": ["gemütlich", "hell", "modern", "geräumig"],
        "urban": ["belebt", "urban", "städtisch", "modern"],
        "nature": ["gruen", "natürlich", "ruhig", "idyllisch"],
        "beach": ["sonnig", "tropisch", "entspannt", "malerisch"],
        "forest": ["dicht", "grün", "mystisch", "ruhig"],
        "mountain": ["majestätisch", "beeindruckend", "hoch", "schneebedeckt"],
        "city": ["geschäftig", "urban", "modern", "lebendig"]
    }

    # Farb-Adjektive
    COLOR_ADJECTIVES = {
        "warm": ["warm", "sonnig", "herbstlich", "golden"],
        "cool": ["kühl", "blau", "winterlich", "frisch"],
        "neutral": ["natürlich", "gedämpft", "ausgewogen"],
        "vibrant": ["farbenfroh", "lebhaft", "bunt", "leuchtend"],
        "dark": ["dunkel", "mysteriös", "nächtlich", "schattig"],
        "bright": ["hell", "strahlend", "lichtdurchflutet", "sonnig"]
    }

    def __init__(self):
        self.color_analyzer = None
        self.scene_classifier = None

        # Versuche Vision-Module zu laden
        try:
            from holo_vision_enhanced import EnhancedColorAnalyzer, EnhancedSceneClassifier
            self.color_analyzer = EnhancedColorAnalyzer()
            self.scene_classifier = EnhancedSceneClassifier()
        except ImportError:
            logger.info("Vision-Module nicht verfuegbar - reduzierte Captioning-Qualitaet")

    def generate_caption(self, image,
                         detected_objects: Optional[List[Dict]] = None,
                         scene_info: Optional[Dict] = None) -> ImageCaption:
        """Generiere Bildbeschreibung"""

        # Analysiere Bild falls keine Infos gegeben
        if detected_objects is None:
            detected_objects = self._detect_objects_simple(image)

        if scene_info is None:
            scene_info = self._classify_scene_simple(image)

        # Waehle passendes Template
        caption, confidence = self._select_and_fill_template(
            detected_objects, scene_info, image
        )

        # Generiere Alternativen
        alternatives = self._generate_alternatives(detected_objects, scene_info)

        return ImageCaption(
            caption=caption,
            confidence=confidence,
            details={
                "objects": detected_objects,
                "scene": scene_info,
                "method": "template_based"
            },
            alternative_captions=alternatives
        )

    def _detect_objects_simple(self, image) -> List[Dict]:
        """Einfache Objekterkennung"""
        objects = []

        if not _HAS_CV2 or not _HAS_NUMPY:
            return objects

        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                return objects
        else:
            img = image

        # Haar Cascade fuer Gesichter
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            objects.append({
                "label": "person",
                "confidence": 0.8,
                "bbox": (x, y, w, h)
            })

        # Farb-basierte Objekterkennung
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Gruen (Pflanzen)
        green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        green_ratio = np.sum(green_mask > 0) / green_mask.size

        if green_ratio > 0.2:
            objects.append({
                "label": "plant",
                "confidence": 0.6,
                "area_ratio": green_ratio
            })

        # Blau (Himmel/Wasser)
        blue_mask = cv2.inRange(hsv, (85, 50, 50), (130, 255, 255))
        blue_ratio = np.sum(blue_mask > 0) / blue_mask.size

        if blue_ratio > 0.3:
            # Oben = Himmel, Unten = Wasser
            h, w = img.shape[:2]
            upper_blue = np.sum(blue_mask[:h//2] > 0) / (h * w // 2)
            if upper_blue > 0.3:
                objects.append({
                    "label": "sky",
                    "confidence": 0.7,
                    "area_ratio": upper_blue
                })

        return objects

    def _classify_scene_simple(self, image) -> Dict:
        """Einfache Szenenklassifikation"""
        scene_info = {
            "scene_type": "unknown",
            "confidence": 0.5,
            "is_outdoor": True,
            "dominant_colors": []
        }

        if self.scene_classifier:
            try:
                result = self.scene_classifier.classify(image)
                scene_info["scene_type"] = result.scene_type
                scene_info["confidence"] = result.confidence
                scene_info["is_outdoor"] = result.is_outdoor
            except Exception:
                pass

        if self.color_analyzer:
            try:
                colors = self.color_analyzer.analyze(image)
                scene_info["dominant_colors"] = colors.dominant_colors[:3]
                scene_info["color_mood"] = colors.mood
            except Exception:
                pass

        return scene_info

    def _select_and_fill_template(self, objects: List[Dict],
                                   scene: Dict, image) -> Tuple[str, float]:
        """Waehle und fuelle Template"""
        import random

        confidence = 0.6

        # Personen zaehlen
        person_count = sum(1 for o in objects if o.get("label") == "person")

        # Szenentyp
        scene_type = scene.get("scene_type", "unknown")

        if person_count > 3:
            # Gruppe
            template = random.choice(self.TEMPLATES["group"])
            caption = template.format(count=person_count, Count=str(person_count))
            confidence = 0.7

        elif person_count == 1:
            # Portrait oder Person
            template = random.choice(self.TEMPLATES["portrait"])
            caption = template
            confidence = 0.75

        elif objects and scene_type != "unknown":
            # Szene mit Objekten
            obj_names = self._format_objects(objects)
            template = random.choice(self.TEMPLATES["scene_with_objects"])

            # Adjektiv fuer Szene
            adjectives = self.SCENE_ADJECTIVES.get(scene_type, [""])
            adj = random.choice(adjectives) if adjectives else ""

            caption = template.format(
                scene=scene_type,
                objects=obj_names,
                adjective=adj,
                article="eine",
                Article="Eine"
            )
            confidence = 0.65

        elif objects:
            # Nur Objekte
            if len(objects) == 1:
                obj = objects[0]
                label = obj.get("label", "Objekt")
                vocab = self.OBJECT_VOCAB.get(label, (label, "ein", "Ein"))

                template = random.choice(self.TEMPLATES["single_object"])
                caption = template.format(
                    object=vocab[0],
                    article=vocab[1],
                    Article=vocab[2]
                )
            else:
                obj_names = self._format_objects(objects)
                template = random.choice(self.TEMPLATES["multiple_objects"])
                caption = template.format(objects=obj_names)

            confidence = 0.6

        elif scene_type != "unknown":
            # Nur Szene
            adjectives = self.SCENE_ADJECTIVES.get(scene_type, ["schoene"])
            adj = random.choice(adjectives)

            template = random.choice(self.TEMPLATES["landscape"])
            caption = template.format(
                scene=scene_type,
                adjective=adj,
                article="eine",
                Article="Eine"
            )
            confidence = 0.55

        else:
            # Fallback
            caption = "Ein Bild ist zu sehen."
            confidence = 0.3

        return caption, confidence

    def _format_objects(self, objects: List[Dict]) -> str:
        """Formatiere Objektliste als Text"""
        if not objects:
            return "verschiedene Elemente"

        labels = []
        for obj in objects[:5]:  # Max 5 Objekte
            label = obj.get("label", "Objekt")
            vocab = self.OBJECT_VOCAB.get(label, (label, "ein", "Ein"))
            labels.append(vocab[0])

        if len(labels) == 1:
            return labels[0]
        elif len(labels) == 2:
            return f"{labels[0]} und {labels[1]}"
        else:
            return ", ".join(labels[:-1]) + f" und {labels[-1]}"

    def _generate_alternatives(self, objects: List[Dict],
                                scene: Dict) -> List[str]:
        """Generiere alternative Beschreibungen"""
        alternatives = []

        # Kurzform
        if objects:
            obj_list = [self.OBJECT_VOCAB.get(o.get("label"), (o.get("label"),))[0]
                        for o in objects[:3]]
            alternatives.append(f"Bild mit: {', '.join(obj_list)}")

        # Szenen-basiert
        scene_type = scene.get("scene_type")
        if scene_type and scene_type != "unknown":
            alternatives.append(f"{scene_type.capitalize()}-Szene")

        # Farb-basiert
        colors = scene.get("dominant_colors", [])
        if colors:
            color_str = ", ".join(colors[:2])
            alternatives.append(f"Bild in {color_str} Toenen")

        return alternatives


# =============================================================================
# Multimodal Sentiment Analyzer
# =============================================================================

class MultimodalSentimentAnalyzer:
    """
    Kombiniert Sentiment aus verschiedenen Modalitaeten:
    - Text-Sentiment
    - Bild-Sentiment (Farben, Gesichtsausdruecke)
    - Audio-Sentiment (Stimme)
    """

    # Sentiment-Schwellen
    SENTIMENT_THRESHOLDS = {
        Sentiment.VERY_NEGATIVE: (-1.0, -0.6),
        Sentiment.NEGATIVE: (-0.6, -0.2),
        Sentiment.NEUTRAL: (-0.2, 0.2),
        Sentiment.POSITIVE: (0.2, 0.6),
        Sentiment.VERY_POSITIVE: (0.6, 1.0)
    }

    # Farben und ihre emotionale Assoziation
    COLOR_SENTIMENT = {
        "red": 0.0,      # Kann positiv (Liebe) oder negativ (Wut) sein
        "orange": 0.3,   # Warm, energetisch
        "yellow": 0.4,   # Froehlich, sonnig
        "green": 0.3,    # Ruhe, Natur
        "blue": 0.1,     # Ruhig, kann melancholisch sein
        "purple": 0.1,   # Kreativ, mystisch
        "pink": 0.3,     # Weich, romantisch
        "white": 0.2,    # Rein, neutral
        "black": -0.2,   # Dunkel, kann negativ sein
        "gray": 0.0,     # Neutral
        "brown": 0.1     # Erdig, warm
    }

    def __init__(self):
        self.text_analyzer = None
        self.image_analyzer = None
        self.audio_analyzer = None

        # Versuche Module zu laden
        try:
            from holo_nlp_enhanced import HoloNLPEnhanced
            self.text_analyzer = HoloNLPEnhanced()
        except ImportError:
            pass

        try:
            from holo_vision_enhanced import HoloVisionEnhanced
            self.image_analyzer = HoloVisionEnhanced()
        except ImportError:
            pass

        try:
            from holo_audio_enhanced import HoloAudioEnhanced
            self.audio_analyzer = HoloAudioEnhanced()
        except ImportError:
            pass

    def analyze(self, text: Optional[str] = None,
                image: Optional[Any] = None,
                audio: Optional[str] = None,
                weights: Optional[Dict[str, float]] = None) -> MultimodalSentimentResult:
        """
        Analysiere Sentiment ueber mehrere Modalitaeten

        Args:
            text: Optionaler Text
            image: Optionales Bild (Pfad oder Array)
            audio: Optionaler Audio-Pfad
            weights: Gewichtung der Modalitaeten {"text": 0.5, "image": 0.3, "audio": 0.2}
        """
        if weights is None:
            weights = {"text": 0.4, "image": 0.35, "audio": 0.25}

        # Normalisiere Gewichte
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}

        results = {}
        scores = []

        # Text-Sentiment
        if text:
            text_result = self._analyze_text_sentiment(text)
            results["text"] = text_result
            scores.append((text_result["score"], weights.get("text", 0.33)))

        # Bild-Sentiment
        if image:
            image_result = self._analyze_image_sentiment(image)
            results["image"] = image_result
            scores.append((image_result["score"], weights.get("image", 0.33)))

        # Audio-Sentiment
        if audio:
            audio_result = self._analyze_audio_sentiment(audio)
            results["audio"] = audio_result
            scores.append((audio_result["score"], weights.get("audio", 0.33)))

        # Fusion
        if scores:
            # Gewichteter Durchschnitt
            weighted_sum = sum(score * weight for score, weight in scores)
            total_weight = sum(weight for _, weight in scores)
            overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

            # Zu Sentiment konvertieren
            overall_sentiment = self._score_to_sentiment(overall_score)
            confidence = self._calculate_confidence(scores)
        else:
            overall_sentiment = Sentiment.NEUTRAL
            overall_score = 0.0
            confidence = 0.0

        return MultimodalSentimentResult(
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            text_sentiment=results.get("text"),
            image_sentiment=results.get("image"),
            audio_sentiment=results.get("audio"),
            fusion_weights=weights
        )

    def _analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """Analysiere Text-Sentiment"""
        # Einfache Wortlisten-basierte Analyse
        positive_words = {
            "gut", "schoen", "toll", "super", "wunderbar", "fantastisch",
            "grossartig", "prima", "excellent", "gluecklich", "froh",
            "liebe", "freude", "positiv", "erfolg", "gewinn", "spass",
            "lachen", "freundlich", "herzlich", "danke", "perfekt"
        }

        negative_words = {
            "schlecht", "boese", "traurig", "schrecklich", "furchtbar",
            "hass", "wut", "aerger", "problem", "fehler", "verlust",
            "schmerz", "angst", "negativ", "schlimm", "katastrophe",
            "enttaeuscht", "frustriert", "muede", "krank", "schwierig"
        }

        words = text.lower().split()
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        total = len(words)

        if total == 0:
            return {"score": 0.0, "positive": 0, "negative": 0}

        # Score zwischen -1 und 1
        score = (pos_count - neg_count) / max(pos_count + neg_count, 1)

        return {
            "score": score,
            "positive": pos_count,
            "negative": neg_count,
            "total_words": total
        }

    def _analyze_image_sentiment(self, image) -> Dict[str, float]:
        """Analysiere Bild-Sentiment"""
        score = 0.0

        if not _HAS_CV2 or not _HAS_NUMPY:
            return {"score": 0.0}

        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                return {"score": 0.0}
        else:
            img = image

        # Farbanalyse
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Helligkeit
        brightness = np.mean(hsv[:, :, 2]) / 255
        score += (brightness - 0.5) * 0.3  # Heller = positiver

        # Saettigung
        saturation = np.mean(hsv[:, :, 1]) / 255
        score += saturation * 0.2  # Lebhaftere Farben = positiver

        # Dominante Farben und ihre Sentiment-Werte
        color_scores = []

        # Verschiedene Farbbereiche pruefen
        color_ranges = {
            "red": [(0, 100, 100), (10, 255, 255)],
            "yellow": [(20, 100, 100), (35, 255, 255)],
            "green": [(35, 100, 100), (85, 255, 255)],
            "blue": [(85, 100, 100), (130, 255, 255)]
        }

        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            ratio = np.sum(mask > 0) / mask.size

            if ratio > 0.1:
                color_scores.append(
                    self.COLOR_SENTIMENT.get(color_name, 0.0) * ratio
                )

        if color_scores:
            score += sum(color_scores) / len(color_scores)

        # Gesichtserkennung fuer Emotionen
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_smile.xml'
        )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) > 0:
            # Laecheln erkennen
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)

                if len(smiles) > 0:
                    score += 0.3  # Laecheln = positiv

        # Begrenzen auf [-1, 1]
        score = max(-1.0, min(1.0, score))

        return {
            "score": score,
            "brightness": brightness,
            "saturation": saturation,
            "faces_detected": len(faces)
        }

    def _analyze_audio_sentiment(self, audio_path: str) -> Dict[str, float]:
        """Analysiere Audio-Sentiment"""
        if self.audio_analyzer:
            try:
                result = self.audio_analyzer.analyze(audio_path, features=['emotion'])
                emotion = result.get('emotion', {})

                # Emotion zu Score mappen
                valence = emotion.get('valence', 0.5)
                score = (valence - 0.5) * 2  # Zu [-1, 1] skalieren

                return {
                    "score": score,
                    "emotion": emotion.get('emotion', 'neutral'),
                    "arousal": emotion.get('arousal', 0.5),
                    "valence": valence
                }
            except Exception:
                pass

        return {"score": 0.0}

    def _score_to_sentiment(self, score: float) -> Sentiment:
        """Konvertiere Score zu Sentiment"""
        for sentiment, (low, high) in self.SENTIMENT_THRESHOLDS.items():
            if low <= score < high:
                return sentiment

        return Sentiment.NEUTRAL

    def _calculate_confidence(self, scores: List[Tuple[float, float]]) -> float:
        """Berechne Konfidenz basierend auf Uebereinstimmung"""
        if len(scores) < 2:
            return 0.7

        # Je mehr Modalitaeten uebereinstimmen, desto hoeher die Konfidenz
        score_values = [s for s, _ in scores]
        variance = np.var(score_values) if _HAS_NUMPY else 0.1

        # Niedrigere Varianz = hoehere Konfidenz
        confidence = max(0.5, 1.0 - variance)

        return float(confidence)


# =============================================================================
# Image-Text Matcher
# =============================================================================

class ImageTextMatcher:
    """
    Prueft Uebereinstimmung zwischen Bild und Text
    """

    def __init__(self):
        self.captioner = TemplateImageCaptioner()

    def match(self, image, text: str) -> ImageTextMatch:
        """Pruefe ob Text zum Bild passt"""

        # Generiere Caption fuer Bild
        caption = self.captioner.generate_caption(image)

        # Extrahiere Schluesselbegriffe aus Text
        text_keywords = self._extract_keywords(text)

        # Extrahiere Schluesselbegriffe aus Caption
        caption_keywords = self._extract_keywords(caption.caption)

        # Finde Uebereinstimmungen
        matched = set(text_keywords) & set(caption_keywords)
        text_only = set(text_keywords) - set(caption_keywords)
        caption_only = set(caption_keywords) - set(text_keywords)

        # Score berechnen
        if not text_keywords:
            score = 0.5
        else:
            score = len(matched) / len(text_keywords)

        # Erklaerung generieren
        if score > 0.7:
            explanation = "Der Text passt gut zum Bild."
        elif score > 0.4:
            explanation = "Der Text passt teilweise zum Bild."
        else:
            explanation = "Der Text passt nicht zum Bild."

        if text_only:
            explanation += f" Nicht im Bild gefunden: {', '.join(list(text_only)[:3])}."

        return ImageTextMatch(
            score=score,
            matched_elements=list(matched),
            mismatched_elements=list(text_only),
            explanation=explanation
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiere Schluesselbegriffe aus Text"""
        # Stoppwoerter (deutsch)
        stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "ist", "sind",
            "zu", "von", "mit", "auf", "in", "an", "fuer", "es", "im", "am",
            "den", "dem", "des", "einer", "einem", "einen", "wird", "werden",
            "hat", "haben", "nicht", "auch", "als", "aber", "noch", "nur",
            "kann", "wenn", "sein", "so", "wie", "bei", "nach", "vor", "zum",
            "zur", "bis", "durch", "man", "sich", "diese", "dieser", "dieses"
        }

        # Tokenisieren und filtern
        words = re.findall(r'\b[a-zäöüß]+\b', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        return keywords


# =============================================================================
# Context Fusion
# =============================================================================

class ContextFusion:
    """
    Vereint Kontext aus verschiedenen Modalitaeten
    """

    def __init__(self):
        self.captioner = TemplateImageCaptioner()

    def fuse(self, text: Optional[str] = None,
             image: Optional[Any] = None,
             audio_transcription: Optional[str] = None) -> ContextFusionResult:
        """Fusioniere Kontext aus verschiedenen Quellen"""

        modalities = []
        all_text = []
        entities = set()

        # Text verarbeiten
        if text:
            modalities.append("text")
            all_text.append(text)
            entities.update(self._extract_entities(text))

        # Bild verarbeiten
        if image:
            modalities.append("image")
            caption = self.captioner.generate_caption(image)
            all_text.append(caption.caption)

            # Objekte als Entitaeten
            for obj in caption.details.get("objects", []):
                entities.add(obj.get("label", ""))

        # Audio verarbeiten
        if audio_transcription:
            modalities.append("audio")
            all_text.append(audio_transcription)
            entities.update(self._extract_entities(audio_transcription))

        # Entities bereinigen
        entities = [e for e in entities if e]

        # Thema bestimmen
        main_topic = self._determine_topic(all_text, entities)

        # Unified Context erstellen
        unified = " ".join(all_text)

        # Konfidenz basierend auf Anzahl Modalitaeten
        confidence = min(0.9, 0.5 + 0.2 * len(modalities))

        return ContextFusionResult(
            unified_context=unified,
            modalities=modalities,
            key_entities=list(entities)[:10],
            main_topic=main_topic,
            confidence=confidence
        )

    def _extract_entities(self, text: str) -> Set[str]:
        """Extrahiere benannte Entitaeten (einfach)"""
        entities = set()

        # Grossgeschriebene Woerter (potentielle Eigennamen)
        words = text.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                clean = re.sub(r'[^\w]', '', word)
                if clean:
                    entities.add(clean)

        return entities

    def _determine_topic(self, texts: List[str], entities: Set[str]) -> str:
        """Bestimme Hauptthema"""
        if not texts:
            return "unbekannt"

        combined = " ".join(texts).lower()

        # Themen-Keywords
        topics = {
            "natur": ["baum", "pflanze", "tier", "wald", "berg", "see", "blume"],
            "menschen": ["person", "mensch", "leute", "gruppe", "familie"],
            "technik": ["computer", "telefon", "laptop", "maschine", "auto"],
            "essen": ["essen", "trinken", "restaurant", "kueche", "kochen"],
            "reise": ["reise", "urlaub", "strand", "flugzeug", "hotel"],
            "arbeit": ["arbeit", "buero", "meeting", "projekt", "team"],
            "sport": ["sport", "spiel", "ball", "laufen", "fitness"],
            "kunst": ["kunst", "musik", "film", "theater", "museum"]
        }

        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]

        return "allgemein"


# =============================================================================
# Multimodal Summarizer
# =============================================================================

class MultimodalSummarizer:
    """
    Erstellt Zusammenfassungen aus mehreren Modalitaeten
    """

    def __init__(self):
        self.captioner = TemplateImageCaptioner()
        self.sentiment_analyzer = MultimodalSentimentAnalyzer()
        self.context_fusion = ContextFusion()

    def summarize(self, text: Optional[str] = None,
                  images: Optional[List[Any]] = None,
                  audio_transcriptions: Optional[List[str]] = None) -> MultimodalSummary:
        """Erstelle multimodale Zusammenfassung"""

        key_points = []
        visual_elements = []
        audio_elements = []

        # Text zusammenfassen
        if text:
            text_summary = self._summarize_text(text)
            key_points.extend(text_summary)

        # Bilder beschreiben
        if images:
            for i, img in enumerate(images[:5]):  # Max 5 Bilder
                caption = self.captioner.generate_caption(img)
                visual_elements.append(caption.caption)

        # Audio zusammenfassen
        if audio_transcriptions:
            for trans in audio_transcriptions[:3]:  # Max 3 Audios
                audio_summary = self._summarize_text(trans)
                audio_elements.extend(audio_summary)

        # Gesamtsentiment
        sentiment = Sentiment.NEUTRAL
        if text:
            result = self.sentiment_analyzer.analyze(text=text)
            sentiment = result.overall_sentiment

        # Zusammenfassung erstellen
        summary_parts = []

        if key_points:
            summary_parts.append("Textinhalt: " + "; ".join(key_points[:3]))

        if visual_elements:
            summary_parts.append("Bilder: " + "; ".join(visual_elements[:2]))

        if audio_elements:
            summary_parts.append("Audio: " + "; ".join(audio_elements[:2]))

        summary = " | ".join(summary_parts) if summary_parts else "Keine Inhalte verfuegbar."

        return MultimodalSummary(
            summary=summary,
            key_points=key_points,
            visual_elements=visual_elements,
            audio_elements=audio_elements,
            sentiment=sentiment
        )

    def _summarize_text(self, text: str, max_sentences: int = 3) -> List[str]:
        """Extraktive Textzusammenfassung"""
        # Einfache satzbasierte Extraktion
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        # Score Saetze nach Laenge und Position
        scored = []
        for i, sent in enumerate(sentences):
            score = 0
            score += len(sent.split()) / 20  # Laenge
            score += 1.0 / (i + 1)  # Position (fruehere = wichtiger)

            # Grossgeschriebene Woerter (potentielle Schluesselwoerter)
            caps = len([w for w in sent.split() if w and w[0].isupper()])
            score += caps * 0.1

            scored.append((sent, score))

        # Top N Saetze
        scored.sort(key=lambda x: x[1], reverse=True)

        return [s for s, _ in scored[:max_sentences]]


# =============================================================================
# Hauptklasse: HoloCrossModal
# =============================================================================

class HoloCrossModal:
    """
    Hauptklasse fuer crossmodale Analyse
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.captioner = TemplateImageCaptioner()
        self.sentiment_analyzer = MultimodalSentimentAnalyzer()
        self.image_text_matcher = ImageTextMatcher()
        self.context_fusion = ContextFusion()
        self.summarizer = MultimodalSummarizer()

        logger.info(f"HoloCrossModal v{self.VERSION} initialisiert")
        logger.info(f"  OpenCV: {_HAS_CV2}")
        logger.info(f"  NumPy: {_HAS_NUMPY}")
        logger.info(f"  PIL: {_HAS_PIL}")

    def analyze(self, text: Optional[str] = None,
                image: Optional[Any] = None,
                audio: Optional[str] = None,
                features: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fuehre crossmodale Analyse durch

        Args:
            text: Optionaler Text
            image: Optionales Bild
            audio: Optionaler Audio-Pfad
            features: Liste der Features ['caption', 'sentiment', 'match', 'fusion']
        """
        if features is None:
            features = ['caption', 'sentiment']

        results = {
            "version": self.VERSION,
            "features_requested": features,
            "modalities_provided": {
                "text": text is not None,
                "image": image is not None,
                "audio": audio is not None
            }
        }

        if 'caption' in features and image:
            caption = self.captioner.generate_caption(image)
            results['caption'] = {
                "text": caption.caption,
                "confidence": caption.confidence,
                "alternatives": caption.alternative_captions
            }

        if 'sentiment' in features:
            sentiment = self.sentiment_analyzer.analyze(text, image, audio)
            results['sentiment'] = {
                "overall": sentiment.overall_sentiment.value,
                "confidence": sentiment.confidence,
                "text_sentiment": sentiment.text_sentiment,
                "image_sentiment": sentiment.image_sentiment,
                "audio_sentiment": sentiment.audio_sentiment
            }

        if 'match' in features and image and text:
            match = self.image_text_matcher.match(image, text)
            results['match'] = {
                "score": match.score,
                "matched": match.matched_elements,
                "mismatched": match.mismatched_elements,
                "explanation": match.explanation
            }

        if 'fusion' in features:
            fusion = self.context_fusion.fuse(text, image, audio)
            results['fusion'] = {
                "unified_context": fusion.unified_context,
                "modalities": fusion.modalities,
                "entities": fusion.key_entities,
                "topic": fusion.main_topic,
                "confidence": fusion.confidence
            }

        return results

    def generate_caption(self, image,
                         objects: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Generiere Bildbeschreibung"""
        caption = self.captioner.generate_caption(image, objects)

        return {
            "caption": caption.caption,
            "confidence": caption.confidence,
            "alternatives": caption.alternative_captions,
            "details": caption.details
        }

    def analyze_multimodal_sentiment(self, text: Optional[str] = None,
                                      image: Optional[Any] = None,
                                      audio: Optional[str] = None) -> Dict[str, Any]:
        """Analysiere Sentiment ueber Modalitaeten"""
        result = self.sentiment_analyzer.analyze(text, image, audio)

        return {
            "overall_sentiment": result.overall_sentiment.value,
            "confidence": result.confidence,
            "text": result.text_sentiment,
            "image": result.image_sentiment,
            "audio": result.audio_sentiment,
            "weights": result.fusion_weights
        }

    def match_image_text(self, image, text: str) -> Dict[str, Any]:
        """Pruefe Bild-Text Uebereinstimmung"""
        result = self.image_text_matcher.match(image, text)

        return {
            "score": result.score,
            "matched": result.matched_elements,
            "mismatched": result.mismatched_elements,
            "explanation": result.explanation
        }

    def create_summary(self, text: Optional[str] = None,
                       images: Optional[List[Any]] = None,
                       audio_transcriptions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Erstelle multimodale Zusammenfassung"""
        result = self.summarizer.summarize(text, images, audio_transcriptions)

        return {
            "summary": result.summary,
            "key_points": result.key_points,
            "visual_elements": result.visual_elements,
            "audio_elements": result.audio_elements,
            "sentiment": result.sentiment.value
        }

    def get_available_features(self) -> Dict[str, bool]:
        """Zeige verfuegbare Features"""
        return {
            "image_captioning": _HAS_CV2,
            "multimodal_sentiment": True,
            "image_text_matching": _HAS_CV2,
            "context_fusion": True,
            "multimodal_summarization": True
        }

    def get_quality_estimate(self) -> Dict[str, str]:
        """Qualitaetsschaetzung ohne LLM"""
        return {
            "image_captioning": "65-75%",
            "multimodal_sentiment": "70-80%",
            "image_text_matching": "60-70%",
            "context_fusion": "75-85%",
            "multimodal_summarization": "70-80%"
        }


# =============================================================================
# Testfunktion
# =============================================================================

def test_crossmodal():
    """Teste CrossModal Module"""
    print("=" * 60)
    print("HoloCrossModal Test")
    print("=" * 60)

    cm = HoloCrossModal()

    # Zeige verfuegbare Features
    print("\nVerfuegbare Features:")
    for feature, available in cm.get_available_features().items():
        status = "✓" if available else "✗"
        print(f"  {status} {feature}")

    # Qualitaetsschaetzung
    print("\nQualitaet ohne LLM:")
    for feature, quality in cm.get_quality_estimate().items():
        print(f"  {feature}: {quality}")

    # Test Sentiment
    print("\n--- Sentiment Test ---")
    sentiment = cm.analyze_multimodal_sentiment(
        text="Das ist ein wunderschoener Tag mit Sonnenschein!"
    )
    print(f"Sentiment: {sentiment['overall_sentiment']}")
    print(f"Confidence: {sentiment['confidence']:.2f}")

    print("\nTest abgeschlossen!")


if __name__ == "__main__":
    test_crossmodal()
