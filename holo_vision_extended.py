#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloVision Extended v1.0 - Erweiterte Bild-Analyse

NEUE FEATURES:
- Emotions-Erkennung: Gesichtsausdruecke analysieren (gluecklich, traurig)
- Text-in-Bild (OCR): Text aus Screenshots/Fotos lesen
- Szenen-Klassifikation: Strand, Wald, Stadt, Innenraum erkennen
- Aehnliche Bilder: Bilder nach Aehnlichkeit gruppieren
- Bild-Qualitaet: Schaerfe, Rauschen, Belichtung bewerten
- Kunst-Stil: Impressionismus, Anime, Foto-realistisch erkennen
- Meme-Erkennung: Bekannte Meme-Templates identifizieren
- Histogramm-Analyse: Detaillierte Farbverteilung

Author: Kira & Claude
Version: 1.0
"""

import os
import re
import math
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

logger = logging.getLogger("HoloVisionExtended")


# =============================================================================
# OPTIONAL IMPORTS
# =============================================================================

_HAS_CV2 = False
_HAS_PIL = False
_HAS_NUMPY = False
_HAS_PYTESSERACT = False

try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
    _HAS_NUMPY = True
    logger.info("OpenCV verfuegbar")
except ImportError:
    logger.warning("OpenCV nicht verfuegbar")

try:
    from PIL import Image, ImageStat, ImageFilter
    _HAS_PIL = True
    logger.info("PIL verfuegbar")
except ImportError:
    logger.warning("PIL nicht verfuegbar")

try:
    import pytesseract
    _HAS_PYTESSERACT = True
    logger.info("Tesseract OCR verfuegbar")
except ImportError:
    logger.warning("Tesseract OCR nicht verfuegbar")


# =============================================================================
# ENUMS UND DATACLASSES
# =============================================================================

class FacialEmotion(Enum):
    """Erkannte Gesichtsgefuehle"""
    HAPPY = "gluecklich"
    SAD = "traurig"
    ANGRY = "wuetend"
    SURPRISED = "ueberrascht"
    NEUTRAL = "neutral"
    FEARFUL = "aengstlich"
    DISGUSTED = "angewidert"
    UNKNOWN = "unbekannt"


class SceneType(Enum):
    """Szenen-Typen"""
    BEACH = "strand"
    FOREST = "wald"
    CITY = "stadt"
    INDOOR = "innenraum"
    MOUNTAIN = "berge"
    WATER = "wasser"
    FIELD = "feld"
    NIGHT = "nacht"
    SUNSET = "sonnenuntergang"
    SNOW = "schnee"
    DESERT = "wueste"
    UNKNOWN = "unbekannt"


class ArtStyle(Enum):
    """Kunst-Stile"""
    PHOTO_REALISTIC = "fotorealistisch"
    ANIME = "anime"
    CARTOON = "cartoon"
    IMPRESSIONIST = "impressionismus"
    ABSTRACT = "abstrakt"
    PIXEL_ART = "pixel_art"
    WATERCOLOR = "aquarell"
    SKETCH = "skizze"
    OIL_PAINTING = "oelgemaelde"
    DIGITAL_ART = "digital_art"
    UNKNOWN = "unbekannt"


class MemeTemplate(Enum):
    """Bekannte Meme-Templates"""
    DRAKE = "drake"
    DISTRACTED_BOYFRIEND = "distracted_boyfriend"
    EXPANDING_BRAIN = "expanding_brain"
    TWO_BUTTONS = "two_buttons"
    CHANGE_MY_MIND = "change_my_mind"
    WOMAN_YELLING_CAT = "woman_yelling_cat"
    SURPRISED_PIKACHU = "surprised_pikachu"
    STONKS = "stonks"
    UNKNOWN = "unbekannt"


@dataclass
class EmotionAnalysisResult:
    """Ergebnis der Emotions-Erkennung"""
    face_count: int
    emotions: List[Dict[str, Any]]  # Pro Gesicht: emotion, confidence, position
    dominant_emotion: FacialEmotion
    average_happiness: float  # 0-1
    has_smile: bool


@dataclass
class OCRResult:
    """Ergebnis der Text-Erkennung"""
    text: str
    confidence: float  # 0-1
    language: str
    word_count: int
    bounding_boxes: List[Dict[str, Any]]  # Pro Wort: text, x, y, w, h
    has_text: bool


@dataclass
class SceneClassificationResult:
    """Ergebnis der Szenen-Klassifikation"""
    primary_scene: SceneType
    scene_scores: Dict[str, float]  # Score pro Szene
    is_outdoor: bool
    is_natural: bool
    time_of_day: str  # "tag", "nacht", "daemmerung"
    weather_guess: str  # "sonnig", "bewoelkt", "regnerisch"


@dataclass
class ImageSimilarityResult:
    """Ergebnis des Bild-Vergleichs"""
    hash_value: str  # Perceptual Hash
    similar_images: List[Tuple[str, float]]  # (image_id, similarity)
    is_duplicate: bool


@dataclass
class ImageQualityResult:
    """Ergebnis der Qualitaets-Analyse"""
    overall_quality: float  # 0-1
    sharpness: float  # 0-1
    noise_level: float  # 0-1 (0=kein Rauschen)
    exposure: str  # "unterbelichtet", "normal", "ueberbelichtet"
    brightness_uniformity: float  # 0-1
    contrast_quality: float  # 0-1
    is_blurry: bool
    suggestions: List[str]


@dataclass
class ArtStyleResult:
    """Ergebnis der Kunst-Stil-Erkennung"""
    primary_style: ArtStyle
    style_scores: Dict[str, float]
    is_photo: bool
    is_illustration: bool
    is_digital: bool
    color_palette: str  # "warm", "kalt", "neutral", "bunt"


@dataclass
class MemeDetectionResult:
    """Ergebnis der Meme-Erkennung"""
    is_meme: bool
    template: MemeTemplate
    confidence: float
    text_regions: List[str]  # Gefundene Text-Bereiche


@dataclass
class HistogramAnalysis:
    """Ergebnis der Histogramm-Analyse"""
    red_histogram: List[int]  # 256 Bins
    green_histogram: List[int]
    blue_histogram: List[int]
    luminance_histogram: List[int]
    dominant_channel: str  # "rot", "gruen", "blau"
    dynamic_range: float  # 0-1
    is_high_contrast: bool
    is_low_key: bool
    is_high_key: bool
    color_balance: str  # "warm", "kalt", "neutral"


# =============================================================================
# HOLOVISION EXTENDED
# =============================================================================

class HoloVisionExtended:
    """
    Erweiterte Bild-Analyse-Funktionen fuer HoloVision.

    Features:
    - Emotions-Erkennung
    - Text-in-Bild (OCR)
    - Szenen-Klassifikation
    - Aehnliche Bilder
    - Bild-Qualitaet
    - Kunst-Stil
    - Meme-Erkennung
    - Histogramm-Analyse
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.has_cv2 = _HAS_CV2
        self.has_pil = _HAS_PIL
        self.has_ocr = _HAS_PYTESSERACT

        # Gesichtserkennung
        self.face_cascade = None
        self.smile_cascade = None
        if self.has_cv2:
            self._init_cascades()

        # Image Hash Cache
        self._image_hashes: Dict[str, str] = {}

        # Scene Detection Keywords
        self._init_scene_colors()

        # Art Style Patterns
        self._init_art_patterns()

        # Meme Templates
        self._init_meme_patterns()

        logger.info("HoloVisionExtended initialisiert")

    def _init_cascades(self):
        """Initialisiert Haar Cascades"""
        try:
            cascade_path = cv2.data.haarcascades
            self.face_cascade = cv2.CascadeClassifier(
                cascade_path + 'haarcascade_frontalface_default.xml'
            )
            self.smile_cascade = cv2.CascadeClassifier(
                cascade_path + 'haarcascade_smile.xml'
            )
            logger.info("Haar Cascades geladen")
        except Exception as e:
            logger.warning(f"Cascades nicht verfuegbar: {e}")

    def _init_scene_colors(self):
        """Initialisiert Farb-Patterns fuer Szenen-Erkennung"""
        self.scene_colors = {
            SceneType.BEACH: {
                "dominant": [(194, 178, 128), (135, 206, 235)],  # Sand, Himmel
                "keywords": ["blau", "beige", "hellblau"]
            },
            SceneType.FOREST: {
                "dominant": [(34, 139, 34), (85, 107, 47)],  # Gruen-Toene
                "keywords": ["gruen", "dunkelgruen", "braun"]
            },
            SceneType.CITY: {
                "dominant": [(128, 128, 128), (169, 169, 169)],  # Grau-Toene
                "keywords": ["grau", "schwarz", "weiss"]
            },
            SceneType.INDOOR: {
                "dominant": [(245, 245, 220), (210, 180, 140)],  # Beige, Tan
                "keywords": ["beige", "braun", "weiss"]
            },
            SceneType.MOUNTAIN: {
                "dominant": [(128, 128, 128), (255, 255, 255)],  # Grau, Schnee
                "keywords": ["grau", "weiss", "blau"]
            },
            SceneType.SUNSET: {
                "dominant": [(255, 140, 0), (255, 69, 0)],  # Orange-Toene
                "keywords": ["orange", "rot", "gelb"]
            },
            SceneType.NIGHT: {
                "dominant": [(25, 25, 112), (0, 0, 0)],  # Dunkel
                "keywords": ["schwarz", "dunkelblau", "dunkel"]
            },
            SceneType.SNOW: {
                "dominant": [(255, 250, 250), (240, 248, 255)],  # Weiss
                "keywords": ["weiss", "hellblau", "grau"]
            },
        }

    def _init_art_patterns(self):
        """Initialisiert Kunst-Stil-Patterns"""
        self.art_patterns = {
            ArtStyle.ANIME: {
                "edge_density": (0.1, 0.3),
                "color_count": (5, 30),
                "saturation": (0.5, 1.0)
            },
            ArtStyle.CARTOON: {
                "edge_density": (0.15, 0.4),
                "color_count": (3, 20),
                "saturation": (0.6, 1.0)
            },
            ArtStyle.PHOTO_REALISTIC: {
                "edge_density": (0.05, 0.15),
                "color_count": (100, 10000),
                "saturation": (0.2, 0.6)
            },
            ArtStyle.PIXEL_ART: {
                "edge_density": (0.3, 0.8),
                "color_count": (2, 32),
                "saturation": (0.4, 1.0)
            },
            ArtStyle.SKETCH: {
                "edge_density": (0.2, 0.5),
                "color_count": (2, 10),
                "saturation": (0.0, 0.2)
            },
        }

    def _init_meme_patterns(self):
        """Initialisiert Meme-Template-Patterns"""
        self.meme_aspect_ratios = {
            MemeTemplate.DRAKE: (1.0, 1.2),
            MemeTemplate.DISTRACTED_BOYFRIEND: (1.3, 1.6),
            MemeTemplate.EXPANDING_BRAIN: (0.4, 0.6),
            MemeTemplate.TWO_BUTTONS: (0.8, 1.0),
            MemeTemplate.CHANGE_MY_MIND: (1.5, 1.8),
        }

    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================

    def _load_image(self, image_path: str) -> Optional[Tuple[str, Any]]:
        """Laedt ein Bild"""
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
                logger.error(f"PIL Fehler: {e}")

        return None

    def _calculate_perceptual_hash(self, image_path: str, hash_size: int = 8) -> str:
        """Berechnet den perceptuellen Hash eines Bildes"""
        img_data = self._load_image(image_path)
        if not img_data:
            return ""

        img_type, img = img_data

        if img_type == "cv2":
            # Resize und Graustufen
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (hash_size + 1, hash_size))

            # Differenz-Hash
            diff = resized[:, 1:] > resized[:, :-1]
            hash_value = sum([2**i for i, v in enumerate(diff.flatten()) if v])
            return format(hash_value, '016x')

        elif img_type == "pil":
            gray = img.convert('L')
            resized = gray.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
            pixels = list(resized.getdata())

            # Differenz-Hash
            hash_bits = []
            for row in range(hash_size):
                for col in range(hash_size):
                    idx = row * (hash_size + 1) + col
                    hash_bits.append(pixels[idx] > pixels[idx + 1])

            hash_value = sum([2**i for i, v in enumerate(hash_bits) if v])
            return format(hash_value, '016x')

        return ""

    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        """Berechnet Hamming-Distanz zwischen zwei Hashes"""
        if len(hash1) != len(hash2):
            return -1

        try:
            val1 = int(hash1, 16)
            val2 = int(hash2, 16)
            xor = val1 ^ val2
            return bin(xor).count('1')
        except (ValueError, TypeError):
            return -1  # Invalid hash format

    def _get_color_histogram(self, image_path: str) -> Dict[str, List[int]]:
        """Berechnet RGB-Histogramme"""
        img_data = self._load_image(image_path)
        if not img_data:
            return {}

        img_type, img = img_data

        if img_type == "cv2":
            histograms = {}
            colors = {'blue': 0, 'green': 1, 'red': 2}

            for color_name, channel in colors.items():
                hist = cv2.calcHist([img], [channel], None, [256], [0, 256])
                histograms[color_name] = [int(h[0]) for h in hist]

            # Luminanz
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            histograms['luminance'] = [int(h[0]) for h in hist]

            return histograms

        elif img_type == "pil":
            histograms = {}

            # RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')

            r, g, b = img.split()
            histograms['red'] = list(r.histogram())
            histograms['green'] = list(g.histogram())
            histograms['blue'] = list(b.histogram())

            # Luminanz
            gray = img.convert('L')
            histograms['luminance'] = list(gray.histogram())

            return histograms

        return {}

    # =========================================================================
    # EMOTIONS-ERKENNUNG
    # =========================================================================

    def analyze_emotions(self, image_path: str) -> EmotionAnalysisResult:
        """
        Analysiert Gesichtsausdruecke in einem Bild.

        Erkennt:
        - Gluecklich/Traurig/Neutral/etc.
        - Laecheln
        - Emotionale Staerke
        """
        if not self.has_cv2 or self.face_cascade is None:
            return EmotionAnalysisResult(
                face_count=0,
                emotions=[],
                dominant_emotion=FacialEmotion.UNKNOWN,
                average_happiness=0.0,
                has_smile=False
            )

        img_data = self._load_image(image_path)
        if not img_data or img_data[0] != "cv2":
            return EmotionAnalysisResult(
                face_count=0, emotions=[], dominant_emotion=FacialEmotion.UNKNOWN,
                average_happiness=0.0, has_smile=False
            )

        img = img_data[1]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Gesichter erkennen
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        emotions = []
        total_happiness = 0.0
        has_smile = False

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]

            # Laecheln erkennen
            smiles = []
            if self.smile_cascade is not None:
                smiles = self.smile_cascade.detectMultiScale(
                    face_roi, scaleFactor=1.7, minNeighbors=22, minSize=(25, 25)
                )

            smile_detected = len(smiles) > 0
            has_smile = has_smile or smile_detected

            # Einfache Emotions-Schaetzung basierend auf Helligkeit und Laecheln
            brightness = face_roi.mean() / 255.0

            if smile_detected:
                emotion = FacialEmotion.HAPPY
                happiness = 0.7 + brightness * 0.3
            elif brightness < 0.3:
                emotion = FacialEmotion.SAD
                happiness = 0.2
            else:
                emotion = FacialEmotion.NEUTRAL
                happiness = 0.5

            total_happiness += happiness

            emotions.append({
                "emotion": emotion.value,
                "confidence": 0.6,
                "position": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
                "has_smile": smile_detected
            })

        # Dominante Emotion bestimmen
        if emotions:
            emotion_counts = Counter(e["emotion"] for e in emotions)
            dominant = emotion_counts.most_common(1)[0][0]
            dominant_emotion = FacialEmotion(dominant)
            avg_happiness = total_happiness / len(emotions)
        else:
            dominant_emotion = FacialEmotion.UNKNOWN
            avg_happiness = 0.0

        return EmotionAnalysisResult(
            face_count=len(faces),
            emotions=emotions,
            dominant_emotion=dominant_emotion,
            average_happiness=round(avg_happiness, 2),
            has_smile=has_smile
        )

    # =========================================================================
    # TEXT-IN-BILD (OCR)
    # =========================================================================

    def extract_text(self, image_path: str, language: str = "deu") -> OCRResult:
        """
        Extrahiert Text aus einem Bild mittels OCR.

        Unterstuetzt: Deutsch, Englisch, weitere Sprachen je nach
        Tesseract-Installation.
        """
        if not self.has_ocr:
            return OCRResult(
                text="", confidence=0.0, language=language,
                word_count=0, bounding_boxes=[], has_text=False
            )

        img_data = self._load_image(image_path)
        if not img_data:
            return OCRResult(
                text="", confidence=0.0, language=language,
                word_count=0, bounding_boxes=[], has_text=False
            )

        img_type, img = img_data

        # Konvertiere zu PIL wenn noetig
        if img_type == "cv2":
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img_rgb)

        try:
            # OCR durchfuehren
            custom_config = f'--oem 3 --psm 3 -l {language}'
            text = pytesseract.image_to_string(img, config=custom_config)

            # Detaillierte Daten
            data = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)

            # Bounding Boxes und Confidence extrahieren
            bounding_boxes = []
            confidences = []

            for i, word in enumerate(data['text']):
                if word.strip():
                    conf = int(data['conf'][i])
                    if conf > 0:
                        confidences.append(conf)
                        bounding_boxes.append({
                            "text": word,
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "w": data['width'][i],
                            "h": data['height'][i],
                            "confidence": conf
                        })

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            words = text.split()

            return OCRResult(
                text=text.strip(),
                confidence=round(avg_confidence / 100, 2),
                language=language,
                word_count=len(words),
                bounding_boxes=bounding_boxes,
                has_text=len(words) > 0
            )

        except Exception as e:
            logger.error(f"OCR Fehler: {e}")
            return OCRResult(
                text="", confidence=0.0, language=language,
                word_count=0, bounding_boxes=[], has_text=False
            )

    # =========================================================================
    # SZENEN-KLASSIFIKATION
    # =========================================================================

    def classify_scene(self, image_path: str) -> SceneClassificationResult:
        """
        Klassifiziert die Szene in einem Bild.

        Erkennt:
        - Strand, Wald, Stadt, Innenraum, etc.
        - Indoor/Outdoor
        - Tageszeit
        - Wetter
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return SceneClassificationResult(
                primary_scene=SceneType.UNKNOWN,
                scene_scores={},
                is_outdoor=False,
                is_natural=False,
                time_of_day="unbekannt",
                weather_guess="unbekannt"
            )

        img_type, img = img_data

        # Analysiere Farbverteilung
        histograms = self._get_color_histogram(image_path)

        # Durchschnittliche Farben berechnen
        if img_type == "cv2":
            avg_color = img.mean(axis=(0, 1))  # BGR
            avg_b, avg_g, avg_r = avg_color
            brightness = (avg_r + avg_g + avg_b) / (3 * 255)

            # Oberer und unterer Bereich analysieren
            h, w = img.shape[:2]
            top_half = img[:h//3, :, :]
            bottom_half = img[2*h//3:, :, :]

            top_brightness = top_half.mean() / 255
            bottom_brightness = bottom_half.mean() / 255

            # Dominant Color
            dominant_b = int(np.median(img[:, :, 0]))
            dominant_g = int(np.median(img[:, :, 1]))
            dominant_r = int(np.median(img[:, :, 2]))

        else:
            # PIL
            stat = ImageStat.Stat(img.convert('RGB'))
            avg_r, avg_g, avg_b = stat.mean
            brightness = (avg_r + avg_g + avg_b) / (3 * 255)
            top_brightness = brightness
            bottom_brightness = brightness
            dominant_r, dominant_g, dominant_b = int(avg_r), int(avg_g), int(avg_b)

        # Scene Scores berechnen
        scene_scores = {}

        # Strand: viel Blau oben, Beige/Braun unten
        if top_brightness > 0.6 and avg_b > avg_g:
            scene_scores["strand"] = 0.6

        # Wald: viel Gruen
        green_ratio = avg_g / max(avg_r + avg_b, 1)
        if green_ratio > 0.4:
            scene_scores["wald"] = min(1.0, green_ratio)

        # Stadt: viel Grau
        gray_variance = abs(avg_r - avg_g) + abs(avg_g - avg_b)
        if gray_variance < 30:
            scene_scores["stadt"] = 0.5

        # Nacht: sehr dunkel
        if brightness < 0.2:
            scene_scores["nacht"] = 1.0 - brightness

        # Sonnenuntergang: Orange/Rot dominant
        if avg_r > avg_g > avg_b and avg_r > 150:
            scene_scores["sonnenuntergang"] = min(1.0, avg_r / 255)

        # Schnee: sehr hell und wenig Saettigung
        if brightness > 0.8:
            scene_scores["schnee"] = brightness

        # Indoor (neutral, mittlere Helligkeit)
        if 0.3 < brightness < 0.7 and gray_variance < 50:
            scene_scores["innenraum"] = 0.5

        # Primaere Szene bestimmen
        if scene_scores:
            primary = max(scene_scores, key=scene_scores.get)
            scene_map = {
                "strand": SceneType.BEACH,
                "wald": SceneType.FOREST,
                "stadt": SceneType.CITY,
                "innenraum": SceneType.INDOOR,
                "nacht": SceneType.NIGHT,
                "sonnenuntergang": SceneType.SUNSET,
                "schnee": SceneType.SNOW,
            }
            primary_scene = scene_map.get(primary, SceneType.UNKNOWN)
        else:
            primary_scene = SceneType.UNKNOWN

        # Is Outdoor
        outdoor_scenes = {SceneType.BEACH, SceneType.FOREST, SceneType.CITY,
                         SceneType.MOUNTAIN, SceneType.NIGHT, SceneType.SUNSET}
        is_outdoor = primary_scene in outdoor_scenes

        # Is Natural
        natural_scenes = {SceneType.BEACH, SceneType.FOREST, SceneType.MOUNTAIN,
                         SceneType.FIELD, SceneType.WATER}
        is_natural = primary_scene in natural_scenes or scene_scores.get("wald", 0) > 0.3

        # Time of Day
        if brightness < 0.2:
            time_of_day = "nacht"
        elif brightness < 0.4:
            time_of_day = "daemmerung"
        else:
            time_of_day = "tag"

        # Weather Guess
        if primary_scene == SceneType.SNOW:
            weather = "schnee"
        elif brightness > 0.7:
            weather = "sonnig"
        elif brightness < 0.4 and primary_scene != SceneType.NIGHT:
            weather = "bewoelkt"
        else:
            weather = "unbekannt"

        return SceneClassificationResult(
            primary_scene=primary_scene,
            scene_scores=scene_scores,
            is_outdoor=is_outdoor,
            is_natural=is_natural,
            time_of_day=time_of_day,
            weather_guess=weather
        )

    # =========================================================================
    # AEHNLICHE BILDER
    # =========================================================================

    def add_image_for_similarity(self, image_path: str, image_id: str = None) -> str:
        """Fuegt ein Bild zum Aehnlichkeits-Pool hinzu"""
        if image_id is None:
            image_id = hashlib.md5(image_path.encode()).hexdigest()[:12]

        hash_value = self._calculate_perceptual_hash(image_path)
        if hash_value:
            self._image_hashes[image_id] = hash_value

        return image_id

    def find_similar_images(self, image_path: str, threshold: float = 0.8) -> ImageSimilarityResult:
        """
        Findet aehnliche Bilder im Pool.

        Args:
            image_path: Pfad zum Bild
            threshold: Mindest-Aehnlichkeit (0-1)

        Returns:
            Liste aehnlicher Bilder mit Aehnlichkeits-Score
        """
        query_hash = self._calculate_perceptual_hash(image_path)
        if not query_hash:
            return ImageSimilarityResult(
                hash_value="",
                similar_images=[],
                is_duplicate=False
            )

        similar = []
        is_duplicate = False

        for image_id, stored_hash in self._image_hashes.items():
            distance = self._hamming_distance(query_hash, stored_hash)
            if distance >= 0:
                # Aehnlichkeit = 1 - (Distanz / max_distanz)
                similarity = 1.0 - (distance / 64)  # 64 bits

                if similarity >= threshold:
                    similar.append((image_id, similarity))

                    if similarity > 0.95:
                        is_duplicate = True

        # Sortiere nach Aehnlichkeit
        similar.sort(key=lambda x: x[1], reverse=True)

        return ImageSimilarityResult(
            hash_value=query_hash,
            similar_images=similar,
            is_duplicate=is_duplicate
        )

    # =========================================================================
    # BILD-QUALITAET
    # =========================================================================

    def analyze_quality(self, image_path: str) -> ImageQualityResult:
        """
        Analysiert die technische Qualitaet eines Bildes.

        Prueft:
        - Schaerfe
        - Rauschen
        - Belichtung
        - Kontrast
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return ImageQualityResult(
                overall_quality=0.0, sharpness=0.0, noise_level=0.0,
                exposure="unbekannt", brightness_uniformity=0.0,
                contrast_quality=0.0, is_blurry=True, suggestions=[]
            )

        img_type, img = img_data
        suggestions = []

        if img_type == "cv2":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Schaerfe (Laplacian Varianz)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            sharpness_normalized = min(1.0, sharpness / 500)

            is_blurry = sharpness < 100
            if is_blurry:
                suggestions.append("Bild ist unscharf - Stabilisierung oder hoeherer ISO empfohlen")

            # Rauschen (Standard-Abweichung in glatten Bereichen)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = np.std(gray.astype(float) - blur.astype(float))
            noise_level = min(1.0, noise / 30)

            if noise_level > 0.5:
                suggestions.append("Hohes Bildrauschen - ISO senken oder bessere Beleuchtung")

            # Belichtung
            mean_brightness = gray.mean() / 255

            if mean_brightness < 0.25:
                exposure = "unterbelichtet"
                suggestions.append("Bild ist unterbelichtet - laengere Belichtung oder hoeherer ISO")
            elif mean_brightness > 0.75:
                exposure = "ueberbelichtet"
                suggestions.append("Bild ist ueberbelichtet - kuerzere Belichtung oder niedrigerer ISO")
            else:
                exposure = "normal"

            # Helligkeits-Uniformitaet
            h, w = gray.shape
            regions = [
                gray[:h//3, :w//3].mean(),
                gray[:h//3, 2*w//3:].mean(),
                gray[2*h//3:, :w//3].mean(),
                gray[2*h//3:, 2*w//3:].mean(),
            ]
            uniformity = 1.0 - (max(regions) - min(regions)) / 255
            brightness_uniformity = uniformity

            # Kontrast
            contrast = gray.std() / 128
            contrast_quality = min(1.0, contrast)

            if contrast < 0.3:
                suggestions.append("Niedriger Kontrast - Kontrastanpassung empfohlen")

        else:
            # PIL Fallback
            gray = img.convert('L')
            stat = ImageStat.Stat(gray)

            sharpness_normalized = 0.5
            noise_level = 0.3
            mean_brightness = stat.mean[0] / 255

            if mean_brightness < 0.25:
                exposure = "unterbelichtet"
            elif mean_brightness > 0.75:
                exposure = "ueberbelichtet"
            else:
                exposure = "normal"

            brightness_uniformity = 0.7
            contrast_quality = stat.stddev[0] / 128
            is_blurry = False

        # Gesamtqualitaet
        overall = (
            sharpness_normalized * 0.3 +
            (1 - noise_level) * 0.2 +
            contrast_quality * 0.2 +
            brightness_uniformity * 0.15 +
            (0.5 if exposure == "normal" else 0.2) * 0.15
        )

        return ImageQualityResult(
            overall_quality=round(overall, 2),
            sharpness=round(sharpness_normalized, 2),
            noise_level=round(noise_level, 2),
            exposure=exposure,
            brightness_uniformity=round(brightness_uniformity, 2),
            contrast_quality=round(contrast_quality, 2),
            is_blurry=is_blurry,
            suggestions=suggestions
        )

    # =========================================================================
    # KUNST-STIL
    # =========================================================================

    def detect_art_style(self, image_path: str) -> ArtStyleResult:
        """
        Erkennt den Kunst-Stil eines Bildes.

        Unterscheidet:
        - Fotorealistisch
        - Anime/Cartoon
        - Impressionismus
        - Pixel Art
        - Skizze
        """
        img_data = self._load_image(image_path)
        if not img_data:
            return ArtStyleResult(
                primary_style=ArtStyle.UNKNOWN,
                style_scores={},
                is_photo=False,
                is_illustration=False,
                is_digital=False,
                color_palette="neutral"
            )

        img_type, img = img_data
        style_scores = {}

        if img_type == "cv2":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Edge Density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = edges.sum() / (edges.shape[0] * edges.shape[1] * 255)

            # Color Count (unique colors)
            img_small = cv2.resize(img, (100, 100))
            unique_colors = len(set(tuple(p) for p in img_small.reshape(-1, 3)))

            # Saturation
            saturation = hsv[:, :, 1].mean() / 255

            # Klassifizierung
            if unique_colors < 50 and edge_density > 0.1:
                style_scores["anime"] = 0.7
                style_scores["cartoon"] = 0.5
            elif unique_colors < 32 and edge_density > 0.3:
                style_scores["pixel_art"] = 0.8
            elif saturation < 0.15:
                style_scores["skizze"] = 0.7
            elif unique_colors > 1000 and edge_density < 0.15:
                style_scores["fotorealistisch"] = 0.8
            else:
                style_scores["digital_art"] = 0.5

        else:
            # PIL Fallback
            style_scores["unbekannt"] = 0.5

        # Primaeren Stil bestimmen
        if style_scores:
            primary = max(style_scores, key=style_scores.get)
            style_map = {
                "anime": ArtStyle.ANIME,
                "cartoon": ArtStyle.CARTOON,
                "pixel_art": ArtStyle.PIXEL_ART,
                "skizze": ArtStyle.SKETCH,
                "fotorealistisch": ArtStyle.PHOTO_REALISTIC,
                "digital_art": ArtStyle.DIGITAL_ART,
            }
            primary_style = style_map.get(primary, ArtStyle.UNKNOWN)
        else:
            primary_style = ArtStyle.UNKNOWN

        is_photo = primary_style == ArtStyle.PHOTO_REALISTIC
        is_illustration = primary_style in {ArtStyle.ANIME, ArtStyle.CARTOON,
                                             ArtStyle.SKETCH, ArtStyle.PIXEL_ART}
        is_digital = primary_style in {ArtStyle.DIGITAL_ART, ArtStyle.PIXEL_ART}

        # Color Palette
        if img_type == "cv2":
            avg_b, avg_g, avg_r = img.mean(axis=(0, 1))
            if avg_r > avg_b + 30:
                color_palette = "warm"
            elif avg_b > avg_r + 30:
                color_palette = "kalt"
            elif hsv[:, :, 1].mean() > 150:
                color_palette = "bunt"
            else:
                color_palette = "neutral"
        else:
            color_palette = "neutral"

        return ArtStyleResult(
            primary_style=primary_style,
            style_scores=style_scores,
            is_photo=is_photo,
            is_illustration=is_illustration,
            is_digital=is_digital,
            color_palette=color_palette
        )

    # =========================================================================
    # MEME-ERKENNUNG
    # =========================================================================

    def detect_meme(self, image_path: str) -> MemeDetectionResult:
        """
        Erkennt ob ein Bild ein Meme ist und welches Template.

        Prueft:
        - Text-Regionen
        - Typische Meme-Layouts
        - Bekannte Templates (per Aspect Ratio + Struktur)
        """
        # OCR fuer Text
        ocr_result = self.extract_text(image_path, "deu+eng")

        # Ist es ueberhaupt ein Meme? (Hat es Text?)
        has_text = ocr_result.has_text

        img_data = self._load_image(image_path)
        if not img_data:
            return MemeDetectionResult(
                is_meme=False,
                template=MemeTemplate.UNKNOWN,
                confidence=0.0,
                text_regions=[]
            )

        img_type, img = img_data

        # Aspect Ratio
        if img_type == "cv2":
            h, w = img.shape[:2]
        else:
            w, h = img.size

        aspect = w / h

        # Template-Erkennung basierend auf Aspect Ratio
        template = MemeTemplate.UNKNOWN
        confidence = 0.0

        for meme_template, (min_ratio, max_ratio) in self.meme_aspect_ratios.items():
            if min_ratio <= aspect <= max_ratio:
                template = meme_template
                confidence = 0.5
                break

        # Meme-Kriterien
        is_meme = has_text and (
            len(ocr_result.text) < 500 and  # Memes haben kurzen Text
            (aspect > 0.5 and aspect < 2.0)  # Typische Meme-Formate
        )

        if is_meme:
            confidence = max(confidence, 0.6)

        # Text-Regionen extrahieren
        text_regions = []
        if ocr_result.bounding_boxes:
            for box in ocr_result.bounding_boxes:
                text_regions.append(box["text"])

        return MemeDetectionResult(
            is_meme=is_meme,
            template=template,
            confidence=confidence,
            text_regions=text_regions[:10]  # Max 10
        )

    # =========================================================================
    # HISTOGRAMM-ANALYSE
    # =========================================================================

    def analyze_histogram(self, image_path: str) -> HistogramAnalysis:
        """
        Fuehrt eine detaillierte Histogramm-Analyse durch.

        Analysiert:
        - RGB-Verteilung
        - Luminanz
        - Dynamikumfang
        - High/Low Key
        """
        histograms = self._get_color_histogram(image_path)

        if not histograms:
            return HistogramAnalysis(
                red_histogram=[], green_histogram=[], blue_histogram=[],
                luminance_histogram=[], dominant_channel="unbekannt",
                dynamic_range=0.0, is_high_contrast=False,
                is_low_key=False, is_high_key=False, color_balance="neutral"
            )

        # Histogramme
        red_hist = histograms.get('red', [0] * 256)
        green_hist = histograms.get('green', [0] * 256)
        blue_hist = histograms.get('blue', [0] * 256)
        lum_hist = histograms.get('luminance', [0] * 256)

        # Dominanter Kanal
        red_sum = sum(red_hist)
        green_sum = sum(green_hist)
        blue_sum = sum(blue_hist)

        if red_sum > green_sum and red_sum > blue_sum:
            dominant_channel = "rot"
        elif green_sum > red_sum and green_sum > blue_sum:
            dominant_channel = "gruen"
        else:
            dominant_channel = "blau"

        # Dynamikumfang
        lum_nonzero = [i for i, v in enumerate(lum_hist) if v > 0]
        if lum_nonzero:
            dynamic_range = (max(lum_nonzero) - min(lum_nonzero)) / 255
        else:
            dynamic_range = 0.0

        # High/Low Contrast
        is_high_contrast = dynamic_range > 0.7

        # High/Low Key
        lum_mean = sum(i * v for i, v in enumerate(lum_hist)) / max(sum(lum_hist), 1)
        is_low_key = lum_mean < 85  # Dunkel
        is_high_key = lum_mean > 170  # Hell

        # Color Balance
        avg_red = sum(i * v for i, v in enumerate(red_hist)) / max(red_sum, 1)
        avg_blue = sum(i * v for i, v in enumerate(blue_hist)) / max(blue_sum, 1)

        if avg_red > avg_blue + 30:
            color_balance = "warm"
        elif avg_blue > avg_red + 30:
            color_balance = "kalt"
        else:
            color_balance = "neutral"

        return HistogramAnalysis(
            red_histogram=red_hist,
            green_histogram=green_hist,
            blue_histogram=blue_hist,
            luminance_histogram=lum_hist,
            dominant_channel=dominant_channel,
            dynamic_range=round(dynamic_range, 2),
            is_high_contrast=is_high_contrast,
            is_low_key=is_low_key,
            is_high_key=is_high_key,
            color_balance=color_balance
        )


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO VISION EXTENDED - Test")
    print("=" * 60)

    vision = HoloVisionExtended()

    print(f"\nVerfuegbare Features:")
    print(f"  - OpenCV: {'ja' if _HAS_CV2 else 'nein'}")
    print(f"  - PIL: {'ja' if _HAS_PIL else 'nein'}")
    print(f"  - Tesseract OCR: {'ja' if _HAS_PYTESSERACT else 'nein'}")

    # Test mit existierendem Bild (falls vorhanden)
    test_image = "test_image.jpg"

    if os.path.exists(test_image):
        print(f"\n[1] Emotions-Analyse:")
        emotions = vision.analyze_emotions(test_image)
        print(f"  - Gesichter: {emotions.face_count}")
        print(f"  - Dominante Emotion: {emotions.dominant_emotion.value}")

        print(f"\n[2] OCR:")
        ocr = vision.extract_text(test_image)
        print(f"  - Text gefunden: {ocr.has_text}")
        if ocr.text:
            print(f"  - Text: {ocr.text[:100]}...")

        print(f"\n[3] Szenen-Klassifikation:")
        scene = vision.classify_scene(test_image)
        print(f"  - Szene: {scene.primary_scene.value}")
        print(f"  - Outdoor: {scene.is_outdoor}")
        print(f"  - Tageszeit: {scene.time_of_day}")

        print(f"\n[4] Bild-Qualitaet:")
        quality = vision.analyze_quality(test_image)
        print(f"  - Gesamt: {quality.overall_quality}")
        print(f"  - Schaerfe: {quality.sharpness}")
        print(f"  - Belichtung: {quality.exposure}")

        print(f"\n[5] Kunst-Stil:")
        style = vision.detect_art_style(test_image)
        print(f"  - Stil: {style.primary_style.value}")
        print(f"  - Ist Foto: {style.is_photo}")

        print(f"\n[6] Meme-Erkennung:")
        meme = vision.detect_meme(test_image)
        print(f"  - Ist Meme: {meme.is_meme}")
        print(f"  - Template: {meme.template.value}")

        print(f"\n[7] Histogramm:")
        hist = vision.analyze_histogram(test_image)
        print(f"  - Dominanter Kanal: {hist.dominant_channel}")
        print(f"  - Dynamikumfang: {hist.dynamic_range}")
        print(f"  - High Key: {hist.is_high_key}")
    else:
        print(f"\nKein Test-Bild gefunden ({test_image})")
        print("Erstellen Sie ein Test-Bild fuer vollstaendigen Test.")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)
