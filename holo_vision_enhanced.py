#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloVision Enhanced v1.0 - Fortgeschrittene Bildanalyse ohne LLM

VERBESSERUNGEN:
1. Bessere Emotionserkennung (Gesichtslandmarks + Regeln)
2. Pose Estimation (Skelett-Erkennung)
3. Objekt-Tracking in Videos
4. CLIP-aehnliches Image-Text Matching
5. Verbesserte Szenen-Klassifizierung
6. Fortgeschrittene Farbanalyse
7. Gesichts-Attribute (Alter, Geschlecht, Brille)

Optimiert fuer Raspberry Pi!

Author: Kira & Claude
Version: 1.0
"""

import os
import math
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime
from enum import Enum

logger = logging.getLogger("HoloVisionEnhanced")


# =============================================================================
# OPTIONAL IMPORTS
# =============================================================================

_HAS_CV2 = False
_HAS_PIL = False
_HAS_NUMPY = False

try:
    import cv2
    _HAS_CV2 = True
except ImportError:
    cv2 = None
    logger.warning("OpenCV nicht verfuegbar")

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageStat
    _HAS_PIL = True
except ImportError:
    Image = None
    logger.warning("PIL nicht verfuegbar")

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    np = None
    logger.warning("NumPy nicht verfuegbar")


# =============================================================================
# ENUMS & DATACLASSES
# =============================================================================

class Emotion(Enum):
    """Erkennbare Emotionen"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    NEUTRAL = "neutral"


class SceneType(Enum):
    """Szenen-Typen"""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    NATURE = "nature"
    URBAN = "urban"
    PORTRAIT = "portrait"
    GROUP = "group"
    FOOD = "food"
    DOCUMENT = "document"
    ART = "art"
    NIGHT = "night"
    SPORTS = "sports"
    UNKNOWN = "unknown"


@dataclass
class FaceAnalysis:
    """Ergebnis der Gesichtsanalyse"""
    face_id: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    emotion: Emotion
    emotion_confidence: float
    emotion_scores: Dict[str, float]
    landmarks: Dict[str, Tuple[int, int]]  # Augen, Nase, Mund
    estimated_age: str  # "kind", "jugendlich", "erwachsen", "senior"
    estimated_gender: str  # "maennlich", "weiblich", "unbekannt"
    has_glasses: bool
    is_smiling: bool
    head_pose: Dict[str, float]  # yaw, pitch, roll


@dataclass
class PoseEstimation:
    """Ergebnis der Pose-Erkennung"""
    person_id: int
    keypoints: Dict[str, Tuple[int, int, float]]  # name -> (x, y, confidence)
    pose_type: str  # "stehend", "sitzend", "liegend", "sport"
    body_bbox: Tuple[int, int, int, int]
    confidence: float


@dataclass
class TrackedObject:
    """Ein verfolgtes Objekt"""
    object_id: int
    object_class: str
    positions: List[Tuple[int, int, int, int, int]]  # frame, x, y, w, h
    first_frame: int
    last_frame: int
    velocity: Tuple[float, float]  # Pixel pro Frame
    direction: str  # "links", "rechts", "oben", "unten", "statisch"


@dataclass
class ImageTextMatch:
    """Ergebnis des Image-Text Matchings"""
    query: str
    score: float
    matched_features: List[str]
    explanation: str


@dataclass
class ColorAnalysis:
    """Fortgeschrittene Farbanalyse"""
    dominant_colors: List[Tuple[Tuple[int, int, int], float]]  # (RGB, percentage)
    color_names: List[str]
    color_harmony: str  # "komplementaer", "analog", "triadisch", "monochrom"
    color_temperature: str  # "warm", "kalt", "neutral"
    saturation_level: str  # "gedaempft", "normal", "lebendig"
    brightness_distribution: Dict[str, float]  # shadows, midtones, highlights


@dataclass
class SceneAnalysis:
    """Fortgeschrittene Szenenanalyse"""
    scene_type: SceneType
    confidence: float
    scene_attributes: List[str]
    objects_detected: List[str]
    text_regions: List[Tuple[int, int, int, int]]
    faces_count: int
    is_blurry: bool
    is_noisy: bool
    composition: str  # "zentriert", "regel_der_drittel", "symmetrisch"


# =============================================================================
# 1. VERBESSERTE EMOTIONSERKENNUNG
# =============================================================================

class EnhancedEmotionDetector:
    """
    Verbesserte Emotionserkennung mit:
    - Haar Cascades fuer Gesichtserkennung
    - Landmark-basierte Emotionsanalyse
    - Regelbasierte Klassifizierung
    """

    def __init__(self):
        self._init_cascades()
        self._init_emotion_rules()

    def _init_cascades(self):
        """Initialisiert Haar Cascades"""
        self.face_cascade = None
        self.eye_cascade = None
        self.smile_cascade = None

        if _HAS_CV2:
            cascade_path = cv2.data.haarcascades

            try:
                self.face_cascade = cv2.CascadeClassifier(
                    cascade_path + 'haarcascade_frontalface_default.xml'
                )
                self.eye_cascade = cv2.CascadeClassifier(
                    cascade_path + 'haarcascade_eye.xml'
                )
                self.smile_cascade = cv2.CascadeClassifier(
                    cascade_path + 'haarcascade_smile.xml'
                )
            except Exception as e:
                logger.warning(f"Cascades nicht geladen: {e}")

    def _init_emotion_rules(self):
        """Initialisiert Emotions-Regeln basierend auf Gesichtsgeometrie"""

        # Verhältnisse für verschiedene Emotionen
        self.emotion_rules = {
            Emotion.HAPPY: {
                "mouth_width_ratio": (0.4, 0.7),  # Breiter Mund
                "mouth_curve": "up",  # Nach oben gebogen
                "eye_openness": (0.3, 0.7),  # Normal bis weit
                "eyebrow_position": "neutral",
            },
            Emotion.SAD: {
                "mouth_width_ratio": (0.2, 0.4),  # Schmaler Mund
                "mouth_curve": "down",  # Nach unten
                "eye_openness": (0.2, 0.5),  # Halb geschlossen
                "eyebrow_position": "inner_raised",
            },
            Emotion.ANGRY: {
                "mouth_width_ratio": (0.3, 0.5),
                "mouth_curve": "straight",
                "eye_openness": (0.4, 0.6),
                "eyebrow_position": "lowered",
            },
            Emotion.SURPRISED: {
                "mouth_width_ratio": (0.3, 0.5),
                "mouth_curve": "open",
                "eye_openness": (0.6, 1.0),  # Weit offen
                "eyebrow_position": "raised",
            },
            Emotion.FEARFUL: {
                "mouth_width_ratio": (0.3, 0.5),
                "mouth_curve": "open",
                "eye_openness": (0.6, 0.9),
                "eyebrow_position": "raised",
            },
            Emotion.NEUTRAL: {
                "mouth_width_ratio": (0.3, 0.5),
                "mouth_curve": "straight",
                "eye_openness": (0.3, 0.6),
                "eyebrow_position": "neutral",
            },
        }

    def analyze_face(self, image, face_bbox: Tuple[int, int, int, int]) -> FaceAnalysis:
        """Analysiert ein einzelnes Gesicht"""
        if not _HAS_CV2 or not _HAS_NUMPY:
            return self._empty_face_analysis(0, face_bbox)

        x, y, w, h = face_bbox
        face_roi = image[y:y+h, x:x+w]

        if face_roi.size == 0:
            return self._empty_face_analysis(0, face_bbox)

        # Grayscale fuer Analyse
        if len(face_roi.shape) == 3:
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_roi

        # Landmarks erkennen
        landmarks = self._detect_landmarks(gray, w, h)

        # Emotionen analysieren
        emotion, confidence, scores = self._analyze_emotion(gray, landmarks, w, h)

        # Laecheln erkennen
        is_smiling = self._detect_smile(gray)

        # Attribute schaetzen
        estimated_age = self._estimate_age(gray, landmarks)
        estimated_gender = self._estimate_gender(gray, landmarks)
        has_glasses = self._detect_glasses(gray, landmarks)

        # Kopfpose schaetzen
        head_pose = self._estimate_head_pose(landmarks, w, h)

        return FaceAnalysis(
            face_id=hash(face_bbox) % 10000,
            bbox=face_bbox,
            emotion=emotion,
            emotion_confidence=confidence,
            emotion_scores=scores,
            landmarks=landmarks,
            estimated_age=estimated_age,
            estimated_gender=estimated_gender,
            has_glasses=has_glasses,
            is_smiling=is_smiling,
            head_pose=head_pose
        )

    def _detect_landmarks(self, gray, w: int, h: int) -> Dict[str, Tuple[int, int]]:
        """Erkennt Gesichtslandmarks"""
        landmarks = {}

        if self.eye_cascade is None:
            return landmarks

        # Augen erkennen
        eyes = self.eye_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20)
        )

        if len(eyes) >= 2:
            # Sortiere nach X-Position
            eyes = sorted(eyes, key=lambda e: e[0])
            left_eye = eyes[0]
            right_eye = eyes[1]

            landmarks["left_eye"] = (
                left_eye[0] + left_eye[2] // 2,
                left_eye[1] + left_eye[3] // 2
            )
            landmarks["right_eye"] = (
                right_eye[0] + right_eye[2] // 2,
                right_eye[1] + right_eye[3] // 2
            )
        elif len(eyes) == 1:
            eye = eyes[0]
            landmarks["left_eye"] = (eye[0] + eye[2] // 2, eye[1] + eye[3] // 2)

        # Nase (Mitte des Gesichts)
        landmarks["nose"] = (w // 2, int(h * 0.55))

        # Mund (unteres Drittel)
        landmarks["mouth_center"] = (w // 2, int(h * 0.75))
        landmarks["mouth_left"] = (int(w * 0.3), int(h * 0.75))
        landmarks["mouth_right"] = (int(w * 0.7), int(h * 0.75))

        return landmarks

    def _analyze_emotion(self, gray, landmarks: Dict, w: int, h: int) -> Tuple[Emotion, float, Dict[str, float]]:
        """Analysiert Emotion basierend auf Landmarks und Bildregionen"""
        scores = {e.value: 0.0 for e in Emotion}

        # Basis-Score fuer neutral
        scores["neutral"] = 0.3

        # Analysiere Mundregion
        mouth_y = int(h * 0.65)
        mouth_roi = gray[mouth_y:h, :]

        if mouth_roi.size > 0:
            # Helligkeit in Mundregion (Laecheln = mehr Kontrast)
            mouth_std = np.std(mouth_roi)
            mouth_mean = np.mean(mouth_roi)

            # Laecheln-Erkennung (hoher Kontrast = Zaehne sichtbar)
            if self.smile_cascade is not None:
                smiles = self.smile_cascade.detectMultiScale(
                    mouth_roi, scaleFactor=1.5, minNeighbors=15, minSize=(25, 25)
                )
                if len(smiles) > 0:
                    scores["happy"] += 0.5

            # Dunkle Mundregion = offener Mund
            if mouth_mean < 80:
                scores["surprised"] += 0.3
                scores["fearful"] += 0.2

        # Analysiere Augenregion
        eye_y = int(h * 0.25)
        eye_h = int(h * 0.25)
        eye_roi = gray[eye_y:eye_y + eye_h, :]

        if eye_roi.size > 0:
            eye_mean = np.mean(eye_roi)
            eye_std = np.std(eye_roi)

            # Weit offene Augen (mehr Weiss = mehr Helligkeit)
            if eye_mean > 120:
                scores["surprised"] += 0.25
                scores["fearful"] += 0.15

            # Zusammengekniffene Augen
            if eye_std < 30:
                scores["angry"] += 0.2
                scores["sad"] += 0.15

        # Analysiere Augenbrauen-Region
        brow_roi = gray[0:int(h * 0.3), :]
        if brow_roi.size > 0:
            brow_gradient = np.gradient(np.mean(brow_roi, axis=1))

            # Stark fallender Gradient = gerunzelte Stirn
            if len(brow_gradient) > 0 and np.min(brow_gradient) < -2:
                scores["angry"] += 0.3
                scores["sad"] += 0.2

        # Gesamt-Helligkeit
        overall_brightness = np.mean(gray)
        if overall_brightness < 100:
            scores["sad"] += 0.1
        elif overall_brightness > 150:
            scores["happy"] += 0.1

        # Normalisieren
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        # Beste Emotion
        best_emotion = max(scores, key=scores.get)
        confidence = scores[best_emotion]

        return Emotion(best_emotion), confidence, scores

    def _detect_smile(self, gray) -> bool:
        """Erkennt ein Laecheln"""
        if self.smile_cascade is None:
            return False

        # Untere Gesichtshaelfte
        h = gray.shape[0]
        lower_face = gray[h // 2:, :]

        smiles = self.smile_cascade.detectMultiScale(
            lower_face, scaleFactor=1.5, minNeighbors=20, minSize=(25, 25)
        )

        return len(smiles) > 0

    def _estimate_age(self, gray, landmarks: Dict) -> str:
        """Schaetzt Altersgruppe"""
        # Vereinfachte Heuristik basierend auf Gesichtsmerkmalen
        h, w = gray.shape

        # Stirn-Falten (oberes Viertel)
        forehead = gray[:h // 4, w // 4:3 * w // 4]
        forehead_texture = np.std(forehead) if forehead.size > 0 else 0

        # Augenringe (unter den Augen)
        if "left_eye" in landmarks:
            eye_y = landmarks["left_eye"][1]
            under_eye = gray[eye_y:eye_y + h // 8, :]
            under_eye_darkness = 255 - np.mean(under_eye) if under_eye.size > 0 else 0
        else:
            under_eye_darkness = 0

        # Heuristiken
        if forehead_texture > 40 and under_eye_darkness > 50:
            return "senior"
        elif forehead_texture > 25:
            return "erwachsen"
        elif w < 100:  # Kleines Gesicht = wahrscheinlich Kind
            return "kind"
        else:
            return "jugendlich"

    def _estimate_gender(self, gray, landmarks: Dict) -> str:
        """Schaetzt Geschlecht (sehr vereinfacht)"""
        h, w = gray.shape

        # Gesichtsform-Analyse
        # Breiteres Gesicht = eher maennlich
        # Schmaleres = eher weiblich

        # Kiefer-Bereich analysieren
        jaw_region = gray[2 * h // 3:, :]
        if jaw_region.size == 0:
            return "unbekannt"

        # Kantenstaerke im Kieferbereich
        edges = cv2.Canny(jaw_region, 50, 150)
        jaw_edge_ratio = np.sum(edges > 0) / edges.size

        # Staerkere Kanten = ausgepraegter Kiefer = eher maennlich
        if jaw_edge_ratio > 0.15:
            return "maennlich"
        elif jaw_edge_ratio < 0.08:
            return "weiblich"
        else:
            return "unbekannt"

    def _detect_glasses(self, gray, landmarks: Dict) -> bool:
        """Erkennt Brillen"""
        if "left_eye" not in landmarks:
            return False

        h, w = gray.shape

        # Augenbereich
        eye_y = landmarks.get("left_eye", (0, h // 3))[1]
        eye_region = gray[max(0, eye_y - h // 8):min(h, eye_y + h // 8), :]

        if eye_region.size == 0:
            return False

        # Brillenrahmen erzeugen starke horizontale Kanten
        edges = cv2.Canny(eye_region, 30, 100)
        horizontal_edges = np.sum(edges, axis=0)

        # Peaks in horizontalen Kanten = Brillenrahmen
        if len(horizontal_edges) > 0:
            edge_variance = np.var(horizontal_edges)
            return edge_variance > 1000

        return False

    def _estimate_head_pose(self, landmarks: Dict, w: int, h: int) -> Dict[str, float]:
        """Schaetzt Kopfpose"""
        pose = {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

        if "left_eye" in landmarks and "right_eye" in landmarks:
            left = landmarks["left_eye"]
            right = landmarks["right_eye"]

            # Yaw (links/rechts Drehung)
            eye_center_x = (left[0] + right[0]) / 2
            yaw = (eye_center_x - w / 2) / (w / 2) * 45
            pose["yaw"] = yaw

            # Roll (Kopfneigung)
            dy = right[1] - left[1]
            dx = right[0] - left[0]
            roll = math.degrees(math.atan2(dy, dx))
            pose["roll"] = roll

        if "nose" in landmarks:
            nose_y = landmarks["nose"][1]
            # Pitch (hoch/runter)
            pitch = (nose_y - h * 0.5) / (h * 0.5) * 30
            pose["pitch"] = pitch

        return pose

    def _empty_face_analysis(self, face_id: int, bbox: Tuple) -> FaceAnalysis:
        """Gibt leere Analyse zurueck"""
        return FaceAnalysis(
            face_id=face_id,
            bbox=bbox,
            emotion=Emotion.NEUTRAL,
            emotion_confidence=0.0,
            emotion_scores={e.value: 0.0 for e in Emotion},
            landmarks={},
            estimated_age="unbekannt",
            estimated_gender="unbekannt",
            has_glasses=False,
            is_smiling=False,
            head_pose={"yaw": 0.0, "pitch": 0.0, "roll": 0.0}
        )


# =============================================================================
# 2. POSE ESTIMATION
# =============================================================================

class SimplePoseEstimator:
    """
    Vereinfachte Pose-Erkennung ohne Deep Learning.

    Verwendet:
    - Konturdetektion
    - Blob-Analyse
    - Geometrische Heuristiken
    """

    def __init__(self):
        self.keypoint_names = [
            "head", "neck", "left_shoulder", "right_shoulder",
            "left_elbow", "right_elbow", "left_wrist", "right_wrist",
            "left_hip", "right_hip", "left_knee", "right_knee",
            "left_ankle", "right_ankle"
        ]

    def estimate_pose(self, image, person_bbox: Tuple[int, int, int, int]) -> PoseEstimation:
        """Schaetzt Pose einer Person"""
        if not _HAS_CV2 or not _HAS_NUMPY:
            return self._empty_pose(0, person_bbox)

        x, y, w, h = person_bbox
        person_roi = image[y:y+h, x:x+w]

        if person_roi.size == 0:
            return self._empty_pose(0, person_bbox)

        # Zu Grayscale
        if len(person_roi.shape) == 3:
            gray = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = person_roi

        # Keypoints schaetzen
        keypoints = self._estimate_keypoints(gray, w, h)

        # Pose-Typ bestimmen
        pose_type = self._classify_pose(keypoints, h)

        # Confidence basierend auf gefundenen Keypoints
        confidence = len([k for k in keypoints.values() if k[2] > 0.3]) / len(self.keypoint_names)

        return PoseEstimation(
            person_id=hash(person_bbox) % 10000,
            keypoints=keypoints,
            pose_type=pose_type,
            body_bbox=person_bbox,
            confidence=confidence
        )

    def _estimate_keypoints(self, gray, w: int, h: int) -> Dict[str, Tuple[int, int, float]]:
        """Schaetzt Keypoints basierend auf Bildanalyse"""
        keypoints = {}

        # Kopf (oberes Viertel, Mitte)
        keypoints["head"] = (w // 2, h // 8, 0.8)

        # Nacken
        keypoints["neck"] = (w // 2, h // 5, 0.7)

        # Schultern (horizontale Linie unter Kopf)
        shoulder_y = int(h * 0.25)
        keypoints["left_shoulder"] = (int(w * 0.25), shoulder_y, 0.6)
        keypoints["right_shoulder"] = (int(w * 0.75), shoulder_y, 0.6)

        # Ellbogen (Mitte des Oberkörpers)
        elbow_y = int(h * 0.4)
        keypoints["left_elbow"] = (int(w * 0.15), elbow_y, 0.5)
        keypoints["right_elbow"] = (int(w * 0.85), elbow_y, 0.5)

        # Handgelenke
        wrist_y = int(h * 0.55)
        keypoints["left_wrist"] = (int(w * 0.1), wrist_y, 0.4)
        keypoints["right_wrist"] = (int(w * 0.9), wrist_y, 0.4)

        # Hueften
        hip_y = int(h * 0.5)
        keypoints["left_hip"] = (int(w * 0.35), hip_y, 0.6)
        keypoints["right_hip"] = (int(w * 0.65), hip_y, 0.6)

        # Knie
        knee_y = int(h * 0.7)
        keypoints["left_knee"] = (int(w * 0.35), knee_y, 0.5)
        keypoints["right_knee"] = (int(w * 0.65), knee_y, 0.5)

        # Knoechel
        ankle_y = int(h * 0.9)
        keypoints["left_ankle"] = (int(w * 0.35), ankle_y, 0.4)
        keypoints["right_ankle"] = (int(w * 0.65), ankle_y, 0.4)

        # Verfeinere mit Kantendetekcion
        edges = cv2.Canny(gray, 50, 150)
        keypoints = self._refine_keypoints(keypoints, edges, w, h)

        return keypoints

    def _refine_keypoints(self, keypoints: Dict, edges, w: int, h: int) -> Dict:
        """Verfeinert Keypoints basierend auf Kanten"""
        refined = keypoints.copy()

        for name, (kp_x, kp_y, conf) in keypoints.items():
            # Suche staerkste Kante in der Naehe
            search_radius = max(10, w // 10)

            x_min = max(0, kp_x - search_radius)
            x_max = min(w, kp_x + search_radius)
            y_min = max(0, kp_y - search_radius)
            y_max = min(h, kp_y + search_radius)

            region = edges[y_min:y_max, x_min:x_max]

            if region.size > 0 and np.max(region) > 0:
                # Finde staerksten Kantenpunkt
                local_max = np.unravel_index(np.argmax(region), region.shape)
                new_y = y_min + local_max[0]
                new_x = x_min + local_max[1]

                # Erhoehe Confidence wenn Kante gefunden
                refined[name] = (new_x, new_y, min(conf + 0.2, 0.95))

        return refined

    def _classify_pose(self, keypoints: Dict, h: int) -> str:
        """Klassifiziert die Pose"""

        # Berechne vertikale Verteilung
        head_y = keypoints.get("head", (0, 0, 0))[1]
        hip_y = keypoints.get("left_hip", (0, h // 2, 0))[1]
        ankle_y = keypoints.get("left_ankle", (0, h, 0))[1]

        torso_length = hip_y - head_y
        leg_length = ankle_y - hip_y

        if torso_length <= 0 or leg_length <= 0:
            return "unbekannt"

        ratio = leg_length / torso_length

        # Heuristiken
        if ratio < 0.8:
            return "sitzend"
        elif ratio > 1.5:
            return "stehend"
        elif head_y > h * 0.4:
            return "liegend"
        else:
            return "stehend"

    def _empty_pose(self, person_id: int, bbox: Tuple) -> PoseEstimation:
        """Gibt leere Pose zurueck"""
        return PoseEstimation(
            person_id=person_id,
            keypoints={name: (0, 0, 0.0) for name in self.keypoint_names},
            pose_type="unbekannt",
            body_bbox=bbox,
            confidence=0.0
        )


# =============================================================================
# 3. OBJEKT-TRACKING
# =============================================================================

class SimpleObjectTracker:
    """
    Einfaches Objekt-Tracking fuer Videos.

    Verwendet:
    - Frame-Differencing
    - Contour Tracking
    - Centroid-basiertes Matching
    """

    def __init__(self, max_disappeared: int = 10):
        self.max_disappeared = max_disappeared
        self.next_object_id = 0
        self.objects: Dict[int, TrackedObject] = {}
        self.disappeared: Dict[int, int] = {}

    def update(self, frame_num: int, detections: List[Tuple[int, int, int, int, str]]) -> Dict[int, TrackedObject]:
        """
        Aktualisiert Tracking mit neuen Detektionen.

        detections: Liste von (x, y, w, h, class_name)
        """
        if not detections:
            # Erhoehe disappeared counter
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self._deregister(obj_id)
            return self.objects

        # Berechne Zentren der neuen Detektionen
        input_centroids = []
        for (x, y, w, h, cls) in detections:
            cx = x + w // 2
            cy = y + h // 2
            input_centroids.append((cx, cy, x, y, w, h, cls))

        # Wenn keine Objekte getrackt werden, registriere alle
        if not self.objects:
            for centroid in input_centroids:
                self._register(frame_num, centroid)
        else:
            # Match existierende Objekte mit neuen Detektionen
            self._match_and_update(frame_num, input_centroids)

        return self.objects

    def _register(self, frame_num: int, centroid_data: Tuple):
        """Registriert neues Objekt"""
        cx, cy, x, y, w, h, cls = centroid_data

        obj = TrackedObject(
            object_id=self.next_object_id,
            object_class=cls,
            positions=[(frame_num, x, y, w, h)],
            first_frame=frame_num,
            last_frame=frame_num,
            velocity=(0.0, 0.0),
            direction="statisch"
        )

        self.objects[self.next_object_id] = obj
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def _deregister(self, obj_id: int):
        """Entfernt Objekt aus Tracking"""
        del self.objects[obj_id]
        del self.disappeared[obj_id]

    def _match_and_update(self, frame_num: int, input_centroids: List[Tuple]):
        """Matched existierende Objekte mit neuen Detektionen"""
        object_ids = list(self.objects.keys())
        object_centroids = []

        for obj_id in object_ids:
            obj = self.objects[obj_id]
            last_pos = obj.positions[-1]
            cx = last_pos[1] + last_pos[3] // 2
            cy = last_pos[2] + last_pos[4] // 2
            object_centroids.append((cx, cy))

        # Berechne Distanzen
        used_rows = set()
        used_cols = set()

        for i, (ocx, ocy) in enumerate(object_centroids):
            min_dist = float('inf')
            min_j = -1

            for j, (cx, cy, x, y, w, h, cls) in enumerate(input_centroids):
                if j in used_cols:
                    continue

                dist = math.sqrt((ocx - cx) ** 2 + (ocy - cy) ** 2)

                if dist < min_dist:
                    min_dist = dist
                    min_j = j

            # Threshold fuer Matching (max 100 Pixel)
            if min_j >= 0 and min_dist < 100:
                obj_id = object_ids[i]
                cx, cy, x, y, w, h, cls = input_centroids[min_j]

                # Update Objekt
                self.objects[obj_id].positions.append((frame_num, x, y, w, h))
                self.objects[obj_id].last_frame = frame_num

                # Berechne Velocity
                if len(self.objects[obj_id].positions) >= 2:
                    prev = self.objects[obj_id].positions[-2]
                    vx = (x - prev[1])
                    vy = (y - prev[2])
                    self.objects[obj_id].velocity = (vx, vy)

                    # Bestimme Richtung
                    self.objects[obj_id].direction = self._get_direction(vx, vy)

                self.disappeared[obj_id] = 0
                used_rows.add(i)
                used_cols.add(min_j)

        # Nicht gematchte existierende Objekte
        for i in range(len(object_ids)):
            if i not in used_rows:
                obj_id = object_ids[i]
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self._deregister(obj_id)

        # Nicht gematchte neue Detektionen
        for j in range(len(input_centroids)):
            if j not in used_cols:
                self._register(frame_num, input_centroids[j])

    def _get_direction(self, vx: float, vy: float) -> str:
        """Bestimmt Bewegungsrichtung"""
        if abs(vx) < 2 and abs(vy) < 2:
            return "statisch"
        elif abs(vx) > abs(vy):
            return "rechts" if vx > 0 else "links"
        else:
            return "unten" if vy > 0 else "oben"

    def detect_moving_objects(self, prev_frame, curr_frame) -> List[Tuple[int, int, int, int]]:
        """Erkennt bewegte Objekte zwischen zwei Frames"""
        if not _HAS_CV2 or not _HAS_NUMPY:
            return []

        # Frame Differencing
        if len(prev_frame.shape) == 3:
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        else:
            prev_gray = prev_frame
            curr_gray = curr_frame

        # Differenz
        diff = cv2.absdiff(prev_gray, curr_gray)

        # Threshold
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # Morphologie
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Konturen finden
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Bounding Boxes
        bboxes = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Min area
                x, y, w, h = cv2.boundingRect(contour)
                bboxes.append((x, y, w, h))

        return bboxes


# =============================================================================
# 4. IMAGE-TEXT MATCHING (CLIP-aehnlich)
# =============================================================================

class SimpleImageTextMatcher:
    """
    Einfaches Image-Text Matching ohne CLIP.

    Verwendet:
    - Farb-Keywords
    - Objekt-Keywords
    - Szenen-Keywords
    - Text im Bild (OCR)
    """

    def __init__(self):
        self._init_keywords()

    def _init_keywords(self):
        """Initialisiert Keyword-Mappings"""

        self.color_keywords = {
            "rot": [(150, 0, 0), (255, 100, 100)],
            "gruen": [(0, 150, 0), (100, 255, 100)],
            "blau": [(0, 0, 150), (100, 100, 255)],
            "gelb": [(200, 200, 0), (255, 255, 100)],
            "orange": [(200, 100, 0), (255, 180, 50)],
            "pink": [(200, 0, 100), (255, 150, 200)],
            "lila": [(100, 0, 150), (200, 100, 255)],
            "braun": [(100, 60, 20), (180, 120, 80)],
            "schwarz": [(0, 0, 0), (50, 50, 50)],
            "weiss": [(200, 200, 200), (255, 255, 255)],
            "grau": [(80, 80, 80), (180, 180, 180)],
        }

        self.scene_keywords = {
            "himmel": ["blau", "wolken", "hell", "oben"],
            "natur": ["gruen", "baum", "gras", "wald", "pflanze"],
            "strand": ["sand", "meer", "wasser", "blau", "gelb"],
            "stadt": ["gebaeude", "strasse", "grau", "urban"],
            "nacht": ["dunkel", "schwarz", "lichter", "sterne"],
            "innen": ["zimmer", "moebel", "wand", "boden"],
            "essen": ["teller", "gericht", "bunt", "warm"],
            "portrait": ["gesicht", "person", "mensch"],
            "tier": ["hund", "katze", "vogel", "tier"],
            "kunst": ["gemaelde", "bild", "rahmen", "farbe"],
        }

        self.attribute_keywords = {
            "hell": "brightness > 0.6",
            "dunkel": "brightness < 0.4",
            "bunt": "saturation > 0.5",
            "gedaempft": "saturation < 0.3",
            "warm": "temperature == warm",
            "kalt": "temperature == cold",
            "scharf": "sharpness > 0.7",
            "unscharf": "sharpness < 0.3",
        }

    def match(self, image_features: Dict[str, Any], query: str) -> ImageTextMatch:
        """Matched eine Text-Anfrage gegen Bild-Features"""
        query_lower = query.lower()
        score = 0.0
        matched_features = []
        explanations = []

        # Farb-Matching
        for color, _ in self.color_keywords.items():
            if color in query_lower:
                color_names = image_features.get("color_names", [])
                if color in [c.lower() for c in color_names]:
                    score += 0.3
                    matched_features.append(f"color:{color}")
                    explanations.append(f"Farbe '{color}' im Bild gefunden")

        # Szenen-Matching
        scene_type = image_features.get("scene_type", "").lower()
        for scene, keywords in self.scene_keywords.items():
            if scene in query_lower:
                if scene_type == scene or any(kw in scene_type for kw in keywords):
                    score += 0.3
                    matched_features.append(f"scene:{scene}")
                    explanations.append(f"Szene '{scene}' erkannt")

        # Attribut-Matching
        brightness = image_features.get("brightness", 0.5)
        saturation = image_features.get("saturation", 0.5)

        if "hell" in query_lower and brightness > 0.6:
            score += 0.2
            matched_features.append("attr:hell")
        if "dunkel" in query_lower and brightness < 0.4:
            score += 0.2
            matched_features.append("attr:dunkel")
        if "bunt" in query_lower and saturation > 0.5:
            score += 0.2
            matched_features.append("attr:bunt")

        # Person-Matching
        faces = image_features.get("faces_count", 0)
        if any(w in query_lower for w in ["person", "mensch", "gesicht", "leute"]):
            if faces > 0:
                score += 0.3
                matched_features.append(f"faces:{faces}")
                explanations.append(f"{faces} Gesicht(er) gefunden")

        # Text-im-Bild Matching
        ocr_text = image_features.get("ocr_text", "").lower()
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 3 and word in ocr_text:
                score += 0.25
                matched_features.append(f"ocr:{word}")
                explanations.append(f"Text '{word}' im Bild gefunden")

        # Normalisieren
        score = min(score, 1.0)

        return ImageTextMatch(
            query=query,
            score=score,
            matched_features=matched_features,
            explanation=" | ".join(explanations) if explanations else "Keine Uebereinstimmung"
        )


# =============================================================================
# 5. FORTGESCHRITTENE SZENEN-KLASSIFIZIERUNG
# =============================================================================

class EnhancedSceneClassifier:
    """
    Verbesserte Szenen-Klassifizierung.

    Verwendet:
    - Farbverteilung
    - Kantenanalyse
    - Gesichtserkennung
    - Textur-Analyse
    - Kompositions-Analyse
    """

    def __init__(self):
        self._init_scene_features()

    def _init_scene_features(self):
        """Initialisiert Szenen-Features"""

        self.scene_profiles = {
            SceneType.NATURE: {
                "green_ratio": (0.2, 1.0),
                "blue_ratio": (0.1, 0.5),
                "edge_density": (0.05, 0.3),
                "faces": (0, 2),
            },
            SceneType.URBAN: {
                "gray_ratio": (0.2, 0.8),
                "edge_density": (0.2, 0.6),
                "line_ratio": (0.1, 0.5),
            },
            SceneType.PORTRAIT: {
                "faces": (1, 5),
                "face_area_ratio": (0.1, 0.7),
                "center_focus": True,
            },
            SceneType.FOOD: {
                "warm_ratio": (0.3, 0.8),
                "saturation": (0.4, 0.9),
                "center_focus": True,
            },
            SceneType.NIGHT: {
                "brightness": (0.0, 0.3),
                "contrast": (0.4, 1.0),
            },
            SceneType.DOCUMENT: {
                "white_ratio": (0.5, 1.0),
                "text_ratio": (0.1, 0.8),
                "edge_density": (0.1, 0.4),
            },
        }

    def classify(self, image) -> SceneAnalysis:
        """Klassifiziert die Szene im Bild"""
        if not _HAS_CV2 or not _HAS_NUMPY:
            return self._empty_scene_analysis()

        h, w = image.shape[:2]

        # Features extrahieren
        features = self._extract_features(image)

        # Szene klassifizieren
        scene_type, confidence = self._match_scene(features)

        # Attribute bestimmen
        attributes = self._get_attributes(features)

        # Komposition analysieren
        composition = self._analyze_composition(image, features)

        # Qualitaet pruefen
        is_blurry = features.get("sharpness", 0.5) < 0.3
        is_noisy = features.get("noise", 0.0) > 0.5

        return SceneAnalysis(
            scene_type=scene_type,
            confidence=confidence,
            scene_attributes=attributes,
            objects_detected=features.get("objects", []),
            text_regions=features.get("text_regions", []),
            faces_count=features.get("faces_count", 0),
            is_blurry=is_blurry,
            is_noisy=is_noisy,
            composition=composition
        )

    def _extract_features(self, image) -> Dict[str, Any]:
        """Extrahiert Bild-Features"""
        features = {}

        h, w = image.shape[:2]

        # Zu HSV konvertieren
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Farbverhaeltnisse
        # Gruen
        green_mask = (hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85) & (hsv[:, :, 1] > 50)
        features["green_ratio"] = np.sum(green_mask) / green_mask.size

        # Blau
        blue_mask = (hsv[:, :, 0] > 90) & (hsv[:, :, 0] < 130) & (hsv[:, :, 1] > 50)
        features["blue_ratio"] = np.sum(blue_mask) / blue_mask.size

        # Grau
        gray_mask = hsv[:, :, 1] < 30
        features["gray_ratio"] = np.sum(gray_mask) / gray_mask.size

        # Weiss
        white_mask = (hsv[:, :, 2] > 200) & (hsv[:, :, 1] < 30)
        features["white_ratio"] = np.sum(white_mask) / white_mask.size

        # Warm (rot/orange/gelb)
        warm_mask = (hsv[:, :, 0] < 30) | (hsv[:, :, 0] > 150)
        features["warm_ratio"] = np.sum(warm_mask & (hsv[:, :, 1] > 50)) / warm_mask.size

        # Helligkeit
        features["brightness"] = np.mean(hsv[:, :, 2]) / 255.0

        # Saettigung
        features["saturation"] = np.mean(hsv[:, :, 1]) / 255.0

        # Kanten
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        features["edge_density"] = np.sum(edges > 0) / edges.size

        # Linien (Hough)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=10)
        features["line_ratio"] = len(lines) / (h * w / 10000) if lines is not None else 0

        # Schaerfe
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        features["sharpness"] = min(1.0, laplacian_var / 500)

        # Rauschen
        noise = np.std(cv2.blur(gray, (3, 3)) - gray)
        features["noise"] = min(1.0, noise / 50)

        # Gesichter
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        features["faces_count"] = len(faces)

        if len(faces) > 0:
            total_face_area = sum(fw * fh for (_, _, fw, fh) in faces)
            features["face_area_ratio"] = total_face_area / (h * w)
        else:
            features["face_area_ratio"] = 0

        # Kontrast
        features["contrast"] = gray.std() / 128.0

        return features

    def _match_scene(self, features: Dict) -> Tuple[SceneType, float]:
        """Matched Features gegen Szenen-Profile"""
        scores = {}

        for scene_type, profile in self.scene_profiles.items():
            score = 0.0
            checks = 0

            for feature, constraint in profile.items():
                if feature not in features:
                    continue

                value = features[feature]
                checks += 1

                if isinstance(constraint, tuple):
                    min_val, max_val = constraint
                    if min_val <= value <= max_val:
                        # Score basierend auf wie gut der Wert passt
                        mid = (min_val + max_val) / 2
                        distance = abs(value - mid) / (max_val - min_val)
                        score += 1.0 - distance
                elif isinstance(constraint, bool):
                    if constraint == bool(value):
                        score += 1.0

            if checks > 0:
                scores[scene_type] = score / checks

        # Spezielle Regeln
        if features.get("faces_count", 0) >= 1 and features.get("face_area_ratio", 0) > 0.1:
            scores[SceneType.PORTRAIT] = scores.get(SceneType.PORTRAIT, 0) + 0.3

        if features.get("brightness", 0.5) < 0.3:
            scores[SceneType.NIGHT] = scores.get(SceneType.NIGHT, 0) + 0.3

        if features.get("white_ratio", 0) > 0.5 and features.get("edge_density", 0) < 0.2:
            scores[SceneType.DOCUMENT] = scores.get(SceneType.DOCUMENT, 0) + 0.3

        # Beste Szene
        if scores:
            best_scene = max(scores, key=scores.get)
            confidence = min(scores[best_scene], 1.0)
            return best_scene, confidence

        return SceneType.UNKNOWN, 0.0

    def _get_attributes(self, features: Dict) -> List[str]:
        """Bestimmt Szenen-Attribute"""
        attributes = []

        if features.get("brightness", 0.5) > 0.7:
            attributes.append("hell")
        elif features.get("brightness", 0.5) < 0.3:
            attributes.append("dunkel")

        if features.get("saturation", 0.5) > 0.6:
            attributes.append("farbenfroh")
        elif features.get("saturation", 0.5) < 0.2:
            attributes.append("gedaempft")

        if features.get("green_ratio", 0) > 0.3:
            attributes.append("gruene_vegetation")

        if features.get("blue_ratio", 0) > 0.3:
            attributes.append("himmel_oder_wasser")

        if features.get("faces_count", 0) > 0:
            attributes.append(f"{features['faces_count']}_gesichter")

        if features.get("sharpness", 0.5) > 0.7:
            attributes.append("scharf")
        elif features.get("sharpness", 0.5) < 0.3:
            attributes.append("unscharf")

        return attributes

    def _analyze_composition(self, image, features: Dict) -> str:
        """Analysiert Bildkomposition"""
        h, w = image.shape[:2]

        # Finde Fokus-Bereich (hoechste Kanten-Dichte)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Teile in 3x3 Grid
        grid = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                y1, y2 = i * h // 3, (i + 1) * h // 3
                x1, x2 = j * w // 3, (j + 1) * w // 3
                grid[i, j] = np.sum(edges[y1:y2, x1:x2])

        # Finde Maximum
        max_pos = np.unravel_index(np.argmax(grid), grid.shape)

        # Kompositionstyp bestimmen
        if max_pos == (1, 1):
            return "zentriert"
        elif max_pos in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            return "regel_der_drittel"
        else:
            # Pruefe Symmetrie
            left_half = np.sum(edges[:, :w // 2])
            right_half = np.sum(edges[:, w // 2:])
            symmetry = 1 - abs(left_half - right_half) / max(left_half, right_half, 1)

            if symmetry > 0.8:
                return "symmetrisch"
            else:
                return "asymmetrisch"

    def _empty_scene_analysis(self) -> SceneAnalysis:
        """Gibt leere Analyse zurueck"""
        return SceneAnalysis(
            scene_type=SceneType.UNKNOWN,
            confidence=0.0,
            scene_attributes=[],
            objects_detected=[],
            text_regions=[],
            faces_count=0,
            is_blurry=False,
            is_noisy=False,
            composition="unbekannt"
        )


# =============================================================================
# 6. FORTGESCHRITTENE FARBANALYSE
# =============================================================================

class EnhancedColorAnalyzer:
    """
    Fortgeschrittene Farbanalyse.

    Features:
    - K-Means Clustering fuer dominante Farben
    - Farbharmonie-Erkennung
    - Farbtemperatur
    - Farbstimmung
    """

    def __init__(self):
        self.color_names = {
            "rot": (255, 0, 0),
            "gruen": (0, 255, 0),
            "blau": (0, 0, 255),
            "gelb": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "lila": (128, 0, 128),
            "braun": (139, 69, 19),
            "schwarz": (0, 0, 0),
            "weiss": (255, 255, 255),
            "grau": (128, 128, 128),
            "beige": (245, 245, 220),
            "tuerkis": (64, 224, 208),
        }

    def analyze(self, image, n_colors: int = 5) -> ColorAnalysis:
        """Analysiert Farben im Bild"""
        if not _HAS_CV2 or not _HAS_NUMPY:
            return self._empty_color_analysis()

        # Resize fuer Performance
        small = cv2.resize(image, (100, 100))
        pixels = small.reshape(-1, 3)

        # K-Means fuer dominante Farben (vereinfacht)
        dominant = self._find_dominant_colors(pixels, n_colors)

        # Farbnamen zuordnen
        color_names = [self._get_color_name(c[0]) for c in dominant]

        # Farbharmonie
        harmony = self._analyze_harmony(dominant)

        # Temperatur
        temperature = self._analyze_temperature(pixels)

        # Saettigung
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        avg_saturation = np.mean(hsv[:, :, 1]) / 255.0

        if avg_saturation > 0.6:
            saturation_level = "lebendig"
        elif avg_saturation < 0.3:
            saturation_level = "gedaempft"
        else:
            saturation_level = "normal"

        # Helligkeitsverteilung
        brightness = hsv[:, :, 2].flatten()
        brightness_dist = {
            "shadows": np.sum(brightness < 85) / len(brightness),
            "midtones": np.sum((brightness >= 85) & (brightness < 170)) / len(brightness),
            "highlights": np.sum(brightness >= 170) / len(brightness),
        }

        return ColorAnalysis(
            dominant_colors=dominant,
            color_names=color_names,
            color_harmony=harmony,
            color_temperature=temperature,
            saturation_level=saturation_level,
            brightness_distribution=brightness_dist
        )

    def _find_dominant_colors(self, pixels, n: int) -> List[Tuple[Tuple[int, int, int], float]]:
        """Findet dominante Farben (vereinfachtes K-Means)"""
        # Quantisiere zu weniger Farben
        quantized = (pixels // 32) * 32

        # Zaehle eindeutige Farben
        colors, counts = np.unique(quantized, axis=0, return_counts=True)

        # Sortiere nach Haeufigkeit
        sorted_idx = np.argsort(counts)[::-1]

        result = []
        total = len(pixels)

        for i in sorted_idx[:n]:
            color = tuple(int(c) for c in colors[i])
            percentage = counts[i] / total
            result.append((color, percentage))

        return result

    def _get_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Findet den naechsten Farbnamen"""
        min_dist = float('inf')
        closest_name = "unbekannt"

        for name, ref_color in self.color_names.items():
            dist = sum((a - b) ** 2 for a, b in zip(rgb, ref_color))
            if dist < min_dist:
                min_dist = dist
                closest_name = name

        return closest_name

    def _analyze_harmony(self, colors: List[Tuple[Tuple[int, int, int], float]]) -> str:
        """Analysiert Farbharmonie"""
        if len(colors) < 2:
            return "monochrom"

        # Konvertiere zu HSV
        hues = []
        for (b, g, r), _ in colors:
            # RGB zu Hue
            rgb = np.array([[[b, g, r]]], dtype=np.uint8)
            hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
            hues.append(hsv[0, 0, 0])

        # Analysiere Hue-Verteilung
        if len(hues) >= 2:
            hue_diff = abs(hues[0] - hues[1])

            if hue_diff < 30 or hue_diff > 150:
                if all(abs(h - hues[0]) < 30 for h in hues):
                    return "monochrom"

            if 75 < hue_diff < 105:  # ~90 Grad
                return "analog"

            if 150 < hue_diff < 180 or hue_diff > 150:  # ~180 Grad
                return "komplementaer"

            if 110 < hue_diff < 130:  # ~120 Grad
                return "triadisch"

        return "vielfaeltig"

    def _analyze_temperature(self, pixels) -> str:
        """Analysiert Farbtemperatur"""
        # Durchschnittliche RGB-Werte
        avg_b = np.mean(pixels[:, 0])
        avg_g = np.mean(pixels[:, 1])
        avg_r = np.mean(pixels[:, 2])

        # Warm = mehr Rot/Gelb, Kalt = mehr Blau
        warm_score = (avg_r + avg_g / 2) / 255
        cold_score = (avg_b + avg_g / 2) / 255

        if warm_score > cold_score + 0.1:
            return "warm"
        elif cold_score > warm_score + 0.1:
            return "kalt"
        else:
            return "neutral"

    def _empty_color_analysis(self) -> ColorAnalysis:
        """Gibt leere Analyse zurueck"""
        return ColorAnalysis(
            dominant_colors=[],
            color_names=[],
            color_harmony="unbekannt",
            color_temperature="neutral",
            saturation_level="normal",
            brightness_distribution={"shadows": 0.33, "midtones": 0.34, "highlights": 0.33}
        )


# =============================================================================
# UNIFIED ENHANCED VISION CLASS
# =============================================================================

class HoloVisionEnhanced:
    """
    Vereinigte Klasse fuer alle erweiterten Vision-Features.
    """

    def __init__(self):
        self.emotion_detector = EnhancedEmotionDetector()
        self.pose_estimator = SimplePoseEstimator()
        self.object_tracker = SimpleObjectTracker()
        self.image_text_matcher = SimpleImageTextMatcher()
        self.scene_classifier = EnhancedSceneClassifier()
        self.color_analyzer = EnhancedColorAnalyzer()

        logger.info("HoloVisionEnhanced initialisiert")

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Fuehrt vollstaendige Bildanalyse durch"""
        if not _HAS_CV2:
            return {"error": "OpenCV nicht verfuegbar"}

        image = cv2.imread(image_path)
        if image is None:
            return {"error": f"Bild nicht gefunden: {image_path}"}

        # Szenen-Analyse
        scene = self.scene_classifier.classify(image)

        # Farb-Analyse
        colors = self.color_analyzer.analyze(image)

        # Gesichts-Analyse
        faces = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        detected_faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in detected_faces:
            face_analysis = self.emotion_detector.analyze_face(image, (x, y, w, h))
            faces.append(face_analysis)

        return {
            "scene": scene,
            "colors": colors,
            "faces": faces,
            "dimensions": {"width": image.shape[1], "height": image.shape[0]},
        }

    def match_text(self, image_path: str, query: str) -> ImageTextMatch:
        """Matched Text-Query gegen Bild"""
        if not _HAS_CV2:
            return ImageTextMatch(query, 0.0, [], "OpenCV nicht verfuegbar")

        image = cv2.imread(image_path)
        if image is None:
            return ImageTextMatch(query, 0.0, [], "Bild nicht gefunden")

        # Features extrahieren
        scene = self.scene_classifier.classify(image)
        colors = self.color_analyzer.analyze(image)

        features = {
            "scene_type": scene.scene_type.value,
            "color_names": colors.color_names,
            "brightness": colors.brightness_distribution.get("highlights", 0),
            "saturation": 0.5,  # Vereinfacht
            "faces_count": scene.faces_count,
            "ocr_text": "",  # Optional: OCR hinzufuegen
        }

        return self.image_text_matcher.match(features, query)

    def analyze_video_frame(self, frame, frame_num: int, prev_frame=None) -> Dict[str, Any]:
        """Analysiert einen Video-Frame"""
        result = {
            "frame_num": frame_num,
            "tracked_objects": {},
        }

        if prev_frame is not None:
            # Bewegungserkennung
            moving = self.object_tracker.detect_moving_objects(prev_frame, frame)
            detections = [(x, y, w, h, "bewegung") for (x, y, w, h) in moving]

            # Update Tracker
            tracked = self.object_tracker.update(frame_num, detections)
            result["tracked_objects"] = {
                obj_id: {
                    "class": obj.object_class,
                    "direction": obj.direction,
                    "velocity": obj.velocity,
                }
                for obj_id, obj in tracked.items()
            }

        return result


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO VISION ENHANCED v1.0 TEST")
    print("=" * 70)

    vision = HoloVisionEnhanced()

    print(f"\nOpenCV verfuegbar: {_HAS_CV2}")
    print(f"NumPy verfuegbar: {_HAS_NUMPY}")
    print(f"PIL verfuegbar: {_HAS_PIL}")

    # Test Image-Text Matching
    print("\n" + "-" * 50)
    print("IMAGE-TEXT MATCHING TEST")
    print("-" * 50)

    test_features = {
        "scene_type": "nature",
        "color_names": ["gruen", "blau", "weiss"],
        "brightness": 0.7,
        "saturation": 0.6,
        "faces_count": 0,
        "ocr_text": "",
    }

    queries = [
        "gruene natur",
        "blauer himmel",
        "person im bild",
        "helles bild",
        "buntes foto"
    ]

    for query in queries:
        match = vision.image_text_matcher.match(test_features, query)
        print(f"  '{query}': Score={match.score:.2f}, Features={match.matched_features}")

    print("\n" + "=" * 70)
    print("TEST ABGESCHLOSSEN")
    print("=" * 70)
