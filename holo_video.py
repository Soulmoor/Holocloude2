#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloVideo v1.0 - Video-Analyse-System

FEATURES:
- Keyframes extrahieren
- Szenen erkennen (Scene Detection)
- Video-Metadaten analysieren
- Thumbnail generieren
- Bewegungsanalyse
- Gesichter im Video zaehlen

Author: Kira & Claude
Version: 1.0
"""

import os
import math
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

logger = logging.getLogger("HoloVideo")


# =============================================================================
# OPTIONAL IMPORTS
# =============================================================================

_HAS_CV2 = False
_HAS_NUMPY = False
_HAS_PIL = False

try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
    _HAS_NUMPY = True
    logger.info("OpenCV verfuegbar")
except ImportError:
    logger.warning("OpenCV nicht verfuegbar")

try:
    from PIL import Image
    _HAS_PIL = True
    logger.info("PIL verfuegbar")
except ImportError:
    logger.warning("PIL nicht verfuegbar")


# =============================================================================
# ENUMS UND DATACLASSES
# =============================================================================

class VideoType(Enum):
    """Video-Typen"""
    MOVIE = "film"
    CLIP = "clip"
    ANIMATION = "animation"
    SCREENCAST = "screencast"
    SLIDESHOW = "slideshow"
    UNKNOWN = "unbekannt"


class SceneChangeType(Enum):
    """Arten von Szenen-Wechseln"""
    CUT = "schnitt"  # Harter Schnitt
    FADE = "ueberblendung"  # Fade-In/Out
    DISSOLVE = "aufloesung"  # Cross-Dissolve
    WIPE = "wischen"  # Wipe-Transition
    UNKNOWN = "unbekannt"


@dataclass
class VideoInfo:
    """Basis-Informationen eines Videos"""
    video_id: str
    file_path: str
    duration_seconds: float
    frame_count: int
    fps: float
    width: int
    height: int
    aspect_ratio: float
    codec: str
    file_size_bytes: int
    format: str


@dataclass
class Keyframe:
    """Ein extrahierter Keyframe"""
    frame_id: str
    frame_number: int
    timestamp_seconds: float
    image_path: Optional[str]  # Pfad zum gespeicherten Bild
    brightness: float
    contrast: float
    dominant_colors: List[Tuple[int, int, int]]
    face_count: int
    motion_score: float  # Bewegung relativ zum vorherigen Frame


@dataclass
class SceneChange:
    """Ein erkannter Szenen-Wechsel"""
    scene_id: str
    timestamp_seconds: float
    frame_number: int
    change_type: SceneChangeType
    confidence: float
    prev_scene_duration: float  # Dauer der vorherigen Szene


@dataclass
class VideoAnalysisResult:
    """Vollstaendiges Ergebnis einer Video-Analyse"""
    video_id: str
    video_type: VideoType
    duration_seconds: float
    frame_count: int
    fps: float

    # Szenen
    scene_count: int
    scenes: List[SceneChange]
    avg_scene_duration: float

    # Keyframes
    keyframes: List[Keyframe]

    # Visuelle Eigenschaften
    avg_brightness: float
    avg_contrast: float
    dominant_colors: List[Tuple[int, int, int]]

    # Bewegung
    avg_motion: float  # 0-1, wie viel Bewegung
    static_percentage: float  # Anteil statischer Frames

    # Gesichter
    frames_with_faces: int
    max_faces_in_frame: int

    # Meta
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MotionAnalysis:
    """Ergebnis der Bewegungsanalyse"""
    avg_motion: float
    max_motion: float
    motion_timeline: List[Tuple[float, float]]  # (timestamp, motion_score)
    static_sections: List[Tuple[float, float]]  # (start, end) in Sekunden
    high_motion_sections: List[Tuple[float, float]]


@dataclass
class ThumbnailResult:
    """Ergebnis der Thumbnail-Generierung"""
    thumbnail_path: str
    timestamp_seconds: float
    frame_number: int
    quality_score: float  # Wie gut ist das Thumbnail?


# =============================================================================
# HOLOVIDEO
# =============================================================================

class HoloVideo:
    """
    Video-Analyse-System.

    Features:
    - Keyframe-Extraktion
    - Szenen-Erkennung
    - Video-Metadaten
    - Thumbnail-Generierung
    - Bewegungsanalyse
    """

    def __init__(self, output_dir: str = "data/video_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.has_cv2 = _HAS_CV2
        self.has_numpy = _HAS_NUMPY
        self.has_pil = _HAS_PIL

        # Gesichtserkennung
        self.face_cascade = None
        if self.has_cv2:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception as e:
                logger.debug(f"Face cascade initialization failed: {e}")

        # Szenen-Erkennungs-Schwellwert
        self.scene_threshold = 30.0  # Differenz-Schwellwert

        logger.info("HoloVideo initialisiert")

    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================

    def _generate_id(self, content: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _open_video(self, video_path: str) -> Optional[Any]:
        """Oeffnet ein Video"""
        if not os.path.exists(video_path):
            logger.error(f"Video nicht gefunden: {video_path}")
            return None

        if not self.has_cv2:
            logger.error("OpenCV nicht verfuegbar")
            return None

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Video konnte nicht geoeffnet werden: {video_path}")
            return None

        return cap

    def _frame_difference(self, frame1, frame2) -> float:
        """Berechnet die Differenz zwischen zwei Frames"""
        if not self.has_cv2 or not self.has_numpy:
            return 0.0

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray1, gray2)
        return np.mean(diff)

    def _calculate_motion(self, frame1, frame2) -> float:
        """Berechnet Bewegung zwischen zwei Frames"""
        if not self.has_cv2 or not self.has_numpy:
            return 0.0

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Optical Flow (vereinfacht: Frame-Differenz)
        diff = cv2.absdiff(gray1, gray2)
        motion = np.mean(diff) / 255.0

        return min(1.0, motion * 5)  # Normalisiert

    def _get_dominant_colors(self, frame, n_colors: int = 3) -> List[Tuple[int, int, int]]:
        """Extrahiert dominante Farben aus einem Frame"""
        if not self.has_cv2 or not self.has_numpy:
            return []

        # Resize fuer Performance
        small = cv2.resize(frame, (50, 50))
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # K-Means Clustering
        pixels = rgb.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        return [tuple(map(int, c)) for c in centers]

    def _detect_faces(self, frame) -> int:
        """Erkennt Gesichter in einem Frame"""
        if not self.has_cv2 or self.face_cascade is None:
            return 0

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        return len(faces)

    def _calculate_brightness(self, frame) -> float:
        """Berechnet die Helligkeit eines Frames"""
        if not self.has_cv2:
            return 0.5

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) / 255.0

    def _calculate_contrast(self, frame) -> float:
        """Berechnet den Kontrast eines Frames"""
        if not self.has_cv2:
            return 0.5

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return min(1.0, np.std(gray) / 128.0)

    # =========================================================================
    # VIDEO-INFO
    # =========================================================================

    def get_video_info(self, video_path: str) -> Optional[VideoInfo]:
        """Holt Basis-Informationen eines Videos"""
        cap = self._open_video(video_path)
        if cap is None:
            return None

        try:
            video_id = self._generate_id(video_path)
            file_size = os.path.getsize(video_path)
            file_format = Path(video_path).suffix.lower().replace('.', '')

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            duration = frame_count / fps if fps > 0 else 0
            aspect_ratio = width / height if height > 0 else 0

            # Codec
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

            return VideoInfo(
                video_id=video_id,
                file_path=video_path,
                duration_seconds=round(duration, 2),
                frame_count=frame_count,
                fps=round(fps, 2),
                width=width,
                height=height,
                aspect_ratio=round(aspect_ratio, 2),
                codec=codec.strip(),
                file_size_bytes=file_size,
                format=file_format
            )

        finally:
            cap.release()

    # =========================================================================
    # KEYFRAME-EXTRAKTION
    # =========================================================================

    def extract_keyframes(self, video_path: str, n_keyframes: int = 10,
                          save_images: bool = True) -> List[Keyframe]:
        """
        Extrahiert Keyframes aus einem Video.

        Methode: Gleichmaessig verteilt + Szenen-Wechsel-basiert

        Args:
            video_path: Pfad zum Video
            n_keyframes: Anzahl der Keyframes
            save_images: Keyframes als Bilder speichern?
        """
        cap = self._open_video(video_path)
        if cap is None:
            return []

        try:
            video_id = self._generate_id(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if frame_count == 0:
                return []

            # Frame-Intervall fuer gleichmaessige Verteilung
            interval = max(1, frame_count // n_keyframes)

            keyframes = []
            prev_frame = None

            for i in range(n_keyframes):
                frame_num = min(i * interval, frame_count - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

                ret, frame = cap.read()
                if not ret:
                    continue

                # Eigenschaften berechnen
                brightness = self._calculate_brightness(frame)
                contrast = self._calculate_contrast(frame)
                colors = self._get_dominant_colors(frame)
                faces = self._detect_faces(frame)

                # Bewegung
                motion = 0.0
                if prev_frame is not None:
                    motion = self._calculate_motion(prev_frame, frame)
                prev_frame = frame.copy()

                timestamp = frame_num / fps if fps > 0 else 0

                # Bild speichern
                image_path = None
                if save_images:
                    image_filename = f"{video_id}_keyframe_{i}.jpg"
                    image_path = str(self.output_dir / image_filename)
                    cv2.imwrite(image_path, frame)

                keyframe = Keyframe(
                    frame_id=f"{video_id}_kf{i}",
                    frame_number=frame_num,
                    timestamp_seconds=round(timestamp, 2),
                    image_path=image_path,
                    brightness=round(brightness, 2),
                    contrast=round(contrast, 2),
                    dominant_colors=colors,
                    face_count=faces,
                    motion_score=round(motion, 2)
                )
                keyframes.append(keyframe)

            logger.info(f"Keyframes extrahiert: {len(keyframes)}")
            return keyframes

        finally:
            cap.release()

    # =========================================================================
    # SZENEN-ERKENNUNG
    # =========================================================================

    def detect_scenes(self, video_path: str, threshold: float = None) -> List[SceneChange]:
        """
        Erkennt Szenen-Wechsel im Video.

        Methode: Frame-Differenz-basiert

        Args:
            video_path: Pfad zum Video
            threshold: Schwellwert fuer Szenen-Wechsel (hoher = weniger Szenen)
        """
        cap = self._open_video(video_path)
        if cap is None:
            return []

        if threshold is None:
            threshold = self.scene_threshold

        try:
            video_id = self._generate_id(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            scenes = []
            prev_frame = None
            last_scene_frame = 0
            scene_counter = 0

            # Sampling (jedes 3. Frame fuer Performance)
            sample_interval = 3

            for frame_num in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()

                if not ret:
                    continue

                if prev_frame is not None:
                    diff = self._frame_difference(prev_frame, frame)

                    if diff > threshold:
                        # Szenen-Wechsel erkannt
                        timestamp = frame_num / fps if fps > 0 else 0
                        prev_duration = (frame_num - last_scene_frame) / fps if fps > 0 else 0

                        # Typ des Wechsels schaetzen
                        if diff > threshold * 2:
                            change_type = SceneChangeType.CUT
                            confidence = 0.9
                        else:
                            change_type = SceneChangeType.FADE
                            confidence = 0.6

                        scene = SceneChange(
                            scene_id=f"{video_id}_scene{scene_counter}",
                            timestamp_seconds=round(timestamp, 2),
                            frame_number=frame_num,
                            change_type=change_type,
                            confidence=confidence,
                            prev_scene_duration=round(prev_duration, 2)
                        )
                        scenes.append(scene)

                        last_scene_frame = frame_num
                        scene_counter += 1

                prev_frame = frame.copy()

            logger.info(f"Szenen erkannt: {len(scenes)}")
            return scenes

        finally:
            cap.release()

    # =========================================================================
    # BEWEGUNGSANALYSE
    # =========================================================================

    def analyze_motion(self, video_path: str, sample_rate: int = 10) -> Optional[MotionAnalysis]:
        """
        Analysiert die Bewegung im Video.

        Args:
            video_path: Pfad zum Video
            sample_rate: Jedes n-te Frame analysieren
        """
        cap = self._open_video(video_path)
        if cap is None:
            return None

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            motion_scores = []
            motion_timeline = []
            prev_frame = None

            for frame_num in range(0, frame_count, sample_rate):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()

                if not ret:
                    continue

                if prev_frame is not None:
                    motion = self._calculate_motion(prev_frame, frame)
                    timestamp = frame_num / fps if fps > 0 else 0

                    motion_scores.append(motion)
                    motion_timeline.append((timestamp, motion))

                prev_frame = frame.copy()

            if not motion_scores:
                return None

            avg_motion = sum(motion_scores) / len(motion_scores)
            max_motion = max(motion_scores)

            # Statische Abschnitte (Motion < 0.1)
            static_sections = []
            high_motion_sections = []

            in_static = False
            in_high_motion = False
            section_start = 0.0

            for timestamp, motion in motion_timeline:
                if motion < 0.1:
                    if not in_static:
                        in_static = True
                        section_start = timestamp
                    if in_high_motion:
                        high_motion_sections.append((section_start, timestamp))
                        in_high_motion = False
                elif motion > 0.5:
                    if not in_high_motion:
                        in_high_motion = True
                        section_start = timestamp
                    if in_static:
                        static_sections.append((section_start, timestamp))
                        in_static = False
                else:
                    if in_static:
                        static_sections.append((section_start, timestamp))
                        in_static = False
                    if in_high_motion:
                        high_motion_sections.append((section_start, timestamp))
                        in_high_motion = False

            return MotionAnalysis(
                avg_motion=round(avg_motion, 3),
                max_motion=round(max_motion, 3),
                motion_timeline=motion_timeline[:100],  # Max 100 Punkte
                static_sections=static_sections[:20],
                high_motion_sections=high_motion_sections[:20]
            )

        finally:
            cap.release()

    # =========================================================================
    # THUMBNAIL-GENERIERUNG
    # =========================================================================

    def generate_thumbnail(self, video_path: str, output_path: str = None,
                           strategy: str = "smart") -> Optional[ThumbnailResult]:
        """
        Generiert ein Thumbnail fuer das Video.

        Strategien:
        - "first": Erstes Frame
        - "middle": Mittleres Frame
        - "smart": Frame mit hoher Qualitaet (hell, kontrastreich, evtl. Gesichter)
        """
        cap = self._open_video(video_path)
        if cap is None:
            return None

        try:
            video_id = self._generate_id(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if frame_count == 0:
                return None

            if strategy == "first":
                target_frame = 0
            elif strategy == "middle":
                target_frame = frame_count // 2
            elif strategy == "smart":
                # Analysiere mehrere Frames und waehle den besten
                candidates = []
                sample_frames = [
                    int(frame_count * 0.1),
                    int(frame_count * 0.25),
                    int(frame_count * 0.5),
                    int(frame_count * 0.75),
                    int(frame_count * 0.9)
                ]

                for frame_num in sample_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                    ret, frame = cap.read()

                    if not ret:
                        continue

                    # Qualitaet bewerten
                    brightness = self._calculate_brightness(frame)
                    contrast = self._calculate_contrast(frame)
                    faces = self._detect_faces(frame)

                    # Score: Mittlere Helligkeit, hoher Kontrast, Gesichter sind gut
                    brightness_score = 1.0 - abs(brightness - 0.5) * 2
                    face_bonus = min(0.3, faces * 0.1)

                    quality_score = brightness_score * 0.4 + contrast * 0.4 + face_bonus

                    candidates.append((frame_num, frame, quality_score))

                # Bestes Frame waehlen
                if candidates:
                    candidates.sort(key=lambda x: x[2], reverse=True)
                    target_frame = candidates[0][0]
                else:
                    target_frame = frame_count // 2
            else:
                target_frame = frame_count // 2

            # Frame extrahieren
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()

            if not ret:
                return None

            # Speichern
            if output_path is None:
                output_path = str(self.output_dir / f"{video_id}_thumbnail.jpg")

            cv2.imwrite(output_path, frame)

            # Qualitaet berechnen
            brightness = self._calculate_brightness(frame)
            contrast = self._calculate_contrast(frame)
            quality_score = (1.0 - abs(brightness - 0.5) * 2) * 0.5 + contrast * 0.5

            timestamp = target_frame / fps if fps > 0 else 0

            return ThumbnailResult(
                thumbnail_path=output_path,
                timestamp_seconds=round(timestamp, 2),
                frame_number=target_frame,
                quality_score=round(quality_score, 2)
            )

        finally:
            cap.release()

    # =========================================================================
    # VOLLSTAENDIGE ANALYSE
    # =========================================================================

    def analyze_video(self, video_path: str, extract_keyframes: bool = True,
                      detect_scenes: bool = True) -> Optional[VideoAnalysisResult]:
        """
        Fuehrt eine vollstaendige Video-Analyse durch.

        Args:
            video_path: Pfad zum Video
            extract_keyframes: Keyframes extrahieren?
            detect_scenes: Szenen erkennen?
        """
        info = self.get_video_info(video_path)
        if info is None:
            return None

        # Keyframes
        keyframes = []
        if extract_keyframes:
            keyframes = self.extract_keyframes(video_path, n_keyframes=10, save_images=False)

        # Szenen
        scenes = []
        if detect_scenes:
            scenes = self.detect_scenes(video_path)

        # Bewegungsanalyse
        motion_analysis = self.analyze_motion(video_path)

        # Aggregierte Werte
        avg_brightness = sum(kf.brightness for kf in keyframes) / len(keyframes) if keyframes else 0.5
        avg_contrast = sum(kf.contrast for kf in keyframes) / len(keyframes) if keyframes else 0.5

        # Dominante Farben (aus erstem Keyframe)
        dominant_colors = keyframes[0].dominant_colors if keyframes else []

        # Gesichter
        frames_with_faces = sum(1 for kf in keyframes if kf.face_count > 0)
        max_faces = max((kf.face_count for kf in keyframes), default=0)

        # Durchschnittliche Szenen-Dauer
        avg_scene_duration = info.duration_seconds / (len(scenes) + 1) if scenes else info.duration_seconds

        # Video-Typ schaetzen
        video_type = self._estimate_video_type(info, motion_analysis, keyframes)

        # Motion-Werte
        avg_motion = motion_analysis.avg_motion if motion_analysis else 0.5
        static_pct = len(motion_analysis.static_sections) / 10 if motion_analysis else 0.0

        return VideoAnalysisResult(
            video_id=info.video_id,
            video_type=video_type,
            duration_seconds=info.duration_seconds,
            frame_count=info.frame_count,
            fps=info.fps,
            scene_count=len(scenes),
            scenes=scenes,
            avg_scene_duration=round(avg_scene_duration, 2),
            keyframes=keyframes,
            avg_brightness=round(avg_brightness, 2),
            avg_contrast=round(avg_contrast, 2),
            dominant_colors=dominant_colors,
            avg_motion=round(avg_motion, 3),
            static_percentage=round(static_pct * 100, 1),
            frames_with_faces=frames_with_faces,
            max_faces_in_frame=max_faces
        )

    def _estimate_video_type(self, info: VideoInfo, motion: Optional[MotionAnalysis],
                             keyframes: List[Keyframe]) -> VideoType:
        """Schaetzt den Video-Typ"""
        # Screencast: Niedrige Bewegung, hoher Kontrast
        if motion and motion.avg_motion < 0.1:
            avg_contrast = sum(kf.contrast for kf in keyframes) / len(keyframes) if keyframes else 0.5
            if avg_contrast > 0.6:
                return VideoType.SCREENCAST

        # Slideshow: Sehr niedrige Bewegung mit Spruengen
        if motion and motion.avg_motion < 0.05:
            return VideoType.SLIDESHOW

        # Animation: Cartoon-artige Farben (wenig Farbvarianz)
        if keyframes:
            color_counts = [len(kf.dominant_colors) for kf in keyframes]
            if all(c <= 5 for c in color_counts):
                return VideoType.ANIMATION

        # Film: Laenger als 20 Minuten
        if info.duration_seconds > 1200:
            return VideoType.MOVIE

        # Clip: Standard
        return VideoType.CLIP

    # =========================================================================
    # UTILITY
    # =========================================================================

    def get_capabilities(self) -> Dict[str, bool]:
        """Gibt die verfuegbaren Faehigkeiten zurueck"""
        return {
            "video_analysis": self.has_cv2,
            "keyframe_extraction": self.has_cv2,
            "scene_detection": self.has_cv2 and self.has_numpy,
            "motion_analysis": self.has_cv2 and self.has_numpy,
            "face_detection": self.has_cv2 and self.face_cascade is not None,
            "thumbnail_generation": self.has_cv2,
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO VIDEO - Test")
    print("=" * 60)

    video = HoloVideo()

    print(f"\nVerfuegbare Features:")
    for cap, available in video.get_capabilities().items():
        status = "ja" if available else "nein"
        print(f"  - {cap}: {status}")

    # Test mit Video-Datei (falls vorhanden)
    test_files = ["test.mp4", "test.avi", "video.mp4"]

    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n--- Analysiere: {test_file} ---")

            # Video-Info
            info = video.get_video_info(test_file)
            if info:
                print(f"Dauer: {info.duration_seconds}s")
                print(f"Aufloesung: {info.width}x{info.height}")
                print(f"FPS: {info.fps}")
                print(f"Frames: {info.frame_count}")

            # Szenen
            scenes = video.detect_scenes(test_file)
            print(f"Szenen erkannt: {len(scenes)}")

            # Keyframes
            keyframes = video.extract_keyframes(test_file, n_keyframes=5, save_images=False)
            print(f"Keyframes: {len(keyframes)}")

            # Thumbnail
            thumb = video.generate_thumbnail(test_file)
            if thumb:
                print(f"Thumbnail: {thumb.thumbnail_path}")

            break
    else:
        print("\nKeine Test-Video-Datei gefunden.")
        print("Erstellen Sie eine MP4/AVI-Datei fuer vollstaendigen Test.")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)
