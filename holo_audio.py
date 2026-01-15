#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloAudio v1.0 - Audio-Analyse-System

FEATURES:
- Musik analysieren (Tempo, Stimmung, Genre)
- Audio-Eigenschaften erkennen (Lautstaerke, Frequenz)
- Sprache erkennen (Speech-to-Text)
- Audio-Typ klassifizieren (Musik, Sprache, Geraeusch)
- Emotionale Wirkung der Musik schaetzen

Author: Kira & Claude
Version: 1.0
"""

import os
import re
import math
import wave
import struct
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

logger = logging.getLogger("HoloAudio")


# =============================================================================
# OPTIONAL IMPORTS
# =============================================================================

_HAS_LIBROSA = False
_HAS_NUMPY = False
_HAS_SCIPY = False
_HAS_SPEECH_RECOGNITION = False

try:
    import numpy as np
    _HAS_NUMPY = True
    logger.info("NumPy verfuegbar")
except ImportError:
    logger.warning("NumPy nicht verfuegbar")

try:
    import librosa
    _HAS_LIBROSA = True
    logger.info("Librosa verfuegbar")
except ImportError:
    logger.warning("Librosa nicht verfuegbar - Audio-Analyse eingeschraenkt")

try:
    from scipy import signal
    _HAS_SCIPY = True
    logger.info("SciPy verfuegbar")
except ImportError:
    logger.warning("SciPy nicht verfuegbar")

try:
    import speech_recognition as sr
    _HAS_SPEECH_RECOGNITION = True
    logger.info("Speech Recognition verfuegbar")
except ImportError:
    logger.warning("Speech Recognition nicht verfuegbar")


# =============================================================================
# ENUMS UND DATACLASSES
# =============================================================================

class AudioType(Enum):
    """Audio-Typen"""
    MUSIC = "musik"
    SPEECH = "sprache"
    AMBIENT = "ambient"
    NOISE = "geraeusch"
    SILENCE = "stille"
    MIXED = "gemischt"
    UNKNOWN = "unbekannt"


class MusicGenre(Enum):
    """Musik-Genres (vereinfacht)"""
    POP = "pop"
    ROCK = "rock"
    ELECTRONIC = "electronic"
    CLASSICAL = "klassik"
    JAZZ = "jazz"
    HIPHOP = "hiphop"
    AMBIENT = "ambient"
    METAL = "metal"
    FOLK = "folk"
    UNKNOWN = "unbekannt"


class MusicMood(Enum):
    """Stimmung der Musik"""
    HAPPY = "froehlich"
    SAD = "traurig"
    ENERGETIC = "energetisch"
    CALM = "ruhig"
    AGGRESSIVE = "aggressiv"
    ROMANTIC = "romantisch"
    MELANCHOLIC = "melancholisch"
    EPIC = "episch"
    MYSTERIOUS = "mysterioees"
    NEUTRAL = "neutral"


@dataclass
class AudioInfo:
    """Basis-Informationen einer Audio-Datei"""
    audio_id: str
    file_path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    bit_depth: int
    file_size_bytes: int
    format: str  # "wav", "mp3", etc.


@dataclass
class AudioAnalysisResult:
    """Vollstaendiges Ergebnis einer Audio-Analyse"""
    audio_id: str
    audio_type: AudioType
    duration_seconds: float

    # Musik-spezifisch
    tempo_bpm: Optional[float]
    genre: MusicGenre
    mood: MusicMood
    energy: float  # 0-1
    danceability: float  # 0-1

    # Audio-Eigenschaften
    loudness_db: float
    dynamic_range: float  # 0-1
    spectral_centroid: float  # Helligkeit
    zero_crossing_rate: float

    # Emotionale Wirkung
    emotional_impact: Dict[str, float]

    # Meta
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SpeechResult:
    """Ergebnis der Sprach-Erkennung"""
    text: str
    confidence: float
    language: str
    word_count: int
    duration_seconds: float
    speaking_rate: float  # Woerter pro Minute


@dataclass
class BeatAnalysis:
    """Ergebnis der Beat-Analyse"""
    tempo_bpm: float
    beats_per_bar: int
    beat_positions: List[float]  # Zeitpunkte in Sekunden
    is_regular: bool  # Regelmaessiger Beat?
    tempo_stability: float  # 0-1


@dataclass
class SpectralAnalysis:
    """Ergebnis der Spektral-Analyse"""
    spectral_centroid: float  # Helligkeit (Hz)
    spectral_bandwidth: float
    spectral_rolloff: float
    mfcc_features: List[float]  # 13 MFCCs
    frequency_bands: Dict[str, float]  # bass, mid, treble


# =============================================================================
# HOLOAUDIO
# =============================================================================

class HoloAudio:
    """
    Audio-Analyse-System fuer Musik und Sprache.

    Features:
    - Musik-Analyse (Tempo, Genre, Stimmung)
    - Sprach-Erkennung (Speech-to-Text)
    - Audio-Klassifikation
    - Spektral-Analyse
    - Emotionale Wirkung
    """

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.has_librosa = _HAS_LIBROSA
        self.has_numpy = _HAS_NUMPY
        self.has_scipy = _HAS_SCIPY
        self.has_speech = _HAS_SPEECH_RECOGNITION

        # Genre-Patterns (vereinfacht)
        self._init_genre_patterns()

        # Mood-Patterns
        self._init_mood_patterns()

        logger.info("HoloAudio initialisiert")

    def _init_genre_patterns(self):
        """Initialisiert Genre-Erkennungs-Patterns"""
        self.genre_patterns = {
            MusicGenre.ELECTRONIC: {
                "tempo_range": (120, 150),
                "energy_range": (0.6, 1.0),
                "spectral_centroid_range": (2000, 5000)
            },
            MusicGenre.CLASSICAL: {
                "tempo_range": (60, 120),
                "energy_range": (0.2, 0.6),
                "spectral_centroid_range": (500, 2000)
            },
            MusicGenre.ROCK: {
                "tempo_range": (100, 140),
                "energy_range": (0.5, 0.9),
                "spectral_centroid_range": (1500, 3500)
            },
            MusicGenre.HIPHOP: {
                "tempo_range": (80, 115),
                "energy_range": (0.5, 0.8),
                "spectral_centroid_range": (1000, 2500)
            },
            MusicGenre.JAZZ: {
                "tempo_range": (80, 200),
                "energy_range": (0.3, 0.7),
                "spectral_centroid_range": (1000, 3000)
            },
            MusicGenre.AMBIENT: {
                "tempo_range": (60, 100),
                "energy_range": (0.1, 0.4),
                "spectral_centroid_range": (500, 1500)
            },
        }

    def _init_mood_patterns(self):
        """Initialisiert Stimmungs-Patterns"""
        self.mood_patterns = {
            MusicMood.HAPPY: {
                "tempo_min": 100,
                "mode": "major",  # Dur
                "energy_min": 0.5
            },
            MusicMood.SAD: {
                "tempo_max": 90,
                "mode": "minor",  # Moll
                "energy_max": 0.4
            },
            MusicMood.ENERGETIC: {
                "tempo_min": 120,
                "energy_min": 0.7
            },
            MusicMood.CALM: {
                "tempo_max": 80,
                "energy_max": 0.3
            },
            MusicMood.AGGRESSIVE: {
                "tempo_min": 130,
                "energy_min": 0.8,
                "spectral_centroid_min": 3000
            },
        }

    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================

    def _generate_id(self, path: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5(path.encode()).hexdigest()[:12]

    def _load_audio(self, audio_path: str) -> Optional[Tuple[Any, int]]:
        """Laedt eine Audio-Datei"""
        if not os.path.exists(audio_path):
            logger.error(f"Audio nicht gefunden: {audio_path}")
            return None

        if self.has_librosa:
            try:
                y, sr = librosa.load(audio_path, sr=None)
                return (y, sr)
            except Exception as e:
                logger.error(f"Librosa Fehler: {e}")

        # Fallback: Nur WAV mit wave-Modul
        if audio_path.lower().endswith('.wav'):
            try:
                with wave.open(audio_path, 'rb') as wav:
                    sr = wav.getframerate()
                    frames = wav.readframes(-1)
                    if wav.getsampwidth() == 2:
                        y = list(struct.unpack(f'{len(frames)//2}h', frames))
                        if self.has_numpy:
                            y = np.array(y) / 32768.0
                        return (y, sr)
            except Exception as e:
                logger.error(f"WAV Fehler: {e}")

        return None

    def _calculate_rms(self, audio_data) -> float:
        """Berechnet RMS (Root Mean Square) Lautstaerke"""
        if self.has_numpy:
            return float(np.sqrt(np.mean(np.square(audio_data))))
        else:
            return math.sqrt(sum(x**2 for x in audio_data) / len(audio_data))

    def _calculate_zero_crossings(self, audio_data) -> float:
        """Berechnet Zero-Crossing-Rate"""
        if self.has_numpy:
            signs = np.sign(audio_data)
            crossings = np.sum(np.abs(np.diff(signs)) > 0)
            return crossings / len(audio_data)
        else:
            crossings = 0
            for i in range(1, len(audio_data)):
                if (audio_data[i] >= 0) != (audio_data[i-1] >= 0):
                    crossings += 1
            return crossings / len(audio_data)

    # =========================================================================
    # AUDIO-INFO
    # =========================================================================

    def get_audio_info(self, audio_path: str) -> Optional[AudioInfo]:
        """Holt Basis-Informationen einer Audio-Datei"""
        if not os.path.exists(audio_path):
            return None

        audio_id = self._generate_id(audio_path)
        file_size = os.path.getsize(audio_path)
        file_format = Path(audio_path).suffix.lower().replace('.', '')

        # Versuche Dauer zu ermitteln
        duration = 0.0
        sample_rate = 0
        channels = 0
        bit_depth = 0

        if self.has_librosa:
            try:
                duration = librosa.get_duration(path=audio_path)
                y, sr = librosa.load(audio_path, sr=None, duration=0.1)
                sample_rate = sr
                channels = 1 if len(y.shape) == 1 else y.shape[0]
                bit_depth = 16  # Librosa normalisiert zu float
            except Exception as e:
                logger.warning(f"Librosa Info-Fehler: {e}")

        elif audio_path.lower().endswith('.wav'):
            try:
                with wave.open(audio_path, 'rb') as wav:
                    sample_rate = wav.getframerate()
                    channels = wav.getnchannels()
                    bit_depth = wav.getsampwidth() * 8
                    frames = wav.getnframes()
                    duration = frames / sample_rate
            except Exception as e:
                logger.warning(f"WAV Info-Fehler: {e}")

        return AudioInfo(
            audio_id=audio_id,
            file_path=audio_path,
            duration_seconds=round(duration, 2),
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=bit_depth,
            file_size_bytes=file_size,
            format=file_format
        )

    # =========================================================================
    # AUDIO-TYP ERKENNUNG
    # =========================================================================

    def classify_audio_type(self, audio_path: str) -> AudioType:
        """
        Klassifiziert den Audio-Typ.

        Unterscheidet:
        - Musik
        - Sprache
        - Ambient/Geraeusche
        - Stille
        """
        audio_data = self._load_audio(audio_path)
        if not audio_data:
            return AudioType.UNKNOWN

        y, sr = audio_data

        # RMS Lautstaerke
        rms = self._calculate_rms(y)

        # Stille erkennen
        if rms < 0.01:
            return AudioType.SILENCE

        # Zero-Crossing-Rate
        zcr = self._calculate_zero_crossings(y)

        if self.has_librosa and self.has_numpy:
            # Spektral-Centroid
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            avg_centroid = np.mean(centroid)

            # Spektrale Flatness (hohe Werte = Rauschen)
            flatness = librosa.feature.spectral_flatness(y=y)
            avg_flatness = np.mean(flatness)

            # Tempo/Beats
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # Klassifizierung
            if avg_flatness > 0.5:
                return AudioType.NOISE

            if tempo > 0 and avg_centroid > 500:
                # Hat Beat und musikalische Eigenschaften
                return AudioType.MUSIC

            if zcr > 0.1 and avg_centroid > 1000:
                # Hohe Frequenzen, variable Amplitude = wahrscheinlich Sprache
                return AudioType.SPEECH

            if avg_centroid < 500 and rms < 0.1:
                return AudioType.AMBIENT

            return AudioType.MIXED

        # Fallback ohne Librosa
        if zcr > 0.15:
            return AudioType.SPEECH
        elif zcr > 0.05:
            return AudioType.MUSIC
        else:
            return AudioType.AMBIENT

    # =========================================================================
    # MUSIK-ANALYSE
    # =========================================================================

    def analyze_music(self, audio_path: str) -> Optional[AudioAnalysisResult]:
        """
        Analysiert Musik-Eigenschaften.

        Ermittelt:
        - Tempo (BPM)
        - Genre (geschaetzt)
        - Stimmung
        - Energie
        - Tanzbarkeit
        """
        audio_data = self._load_audio(audio_path)
        if not audio_data:
            return None

        y, sr = audio_data
        audio_id = self._generate_id(audio_path)
        duration = len(y) / sr

        # Audio-Typ pruefen
        audio_type = self.classify_audio_type(audio_path)

        # Basis-Werte
        rms = self._calculate_rms(y)
        zcr = self._calculate_zero_crossings(y)
        loudness_db = 20 * math.log10(max(rms, 0.0001))

        if self.has_librosa and self.has_numpy:
            # Tempo
            tempo_array, beats = librosa.beat.beat_track(y=y, sr=sr)
            tempo = float(tempo_array) if isinstance(tempo_array, (int, float)) else float(tempo_array[0]) if len(tempo_array) > 0 else 120.0

            # Spektral-Features
            centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

            # Energie (RMS-basiert, normalisiert)
            energy = min(1.0, rms * 3)

            # Tanzbarkeit (basierend auf Tempo-Stabilitaet und Beat-Staerke)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_stability = 1.0 - np.std(np.diff(beats)) / (sr / 10) if len(beats) > 1 else 0.5
            danceability = (tempo_stability + energy) / 2

            # Genre schaetzen
            genre = self._estimate_genre(tempo, energy, centroid)

            # Stimmung schaetzen
            mood = self._estimate_mood(tempo, energy, centroid)

            # Dynamic Range
            dynamic_range = np.std(librosa.feature.rms(y=y)[0])

        else:
            # Fallback-Werte
            tempo = 120.0
            centroid = 1500.0
            energy = min(1.0, rms * 3)
            danceability = 0.5
            genre = MusicGenre.UNKNOWN
            mood = MusicMood.NEUTRAL
            dynamic_range = 0.5

        # Emotionale Wirkung
        emotional_impact = self._calculate_emotional_impact(tempo, energy, mood)

        return AudioAnalysisResult(
            audio_id=audio_id,
            audio_type=audio_type,
            duration_seconds=round(duration, 2),
            tempo_bpm=round(tempo, 1),
            genre=genre,
            mood=mood,
            energy=round(energy, 2),
            danceability=round(danceability, 2),
            loudness_db=round(loudness_db, 1),
            dynamic_range=round(dynamic_range, 2),
            spectral_centroid=round(centroid, 1),
            zero_crossing_rate=round(zcr, 4),
            emotional_impact=emotional_impact
        )

    def _estimate_genre(self, tempo: float, energy: float, centroid: float) -> MusicGenre:
        """Schaetzt das Genre basierend auf Audio-Features"""
        best_genre = MusicGenre.UNKNOWN
        best_score = 0.0

        for genre, patterns in self.genre_patterns.items():
            score = 0.0

            # Tempo
            tempo_range = patterns.get("tempo_range", (0, 300))
            if tempo_range[0] <= tempo <= tempo_range[1]:
                score += 0.4

            # Energie
            energy_range = patterns.get("energy_range", (0, 1))
            if energy_range[0] <= energy <= energy_range[1]:
                score += 0.3

            # Spectral Centroid
            centroid_range = patterns.get("spectral_centroid_range", (0, 10000))
            if centroid_range[0] <= centroid <= centroid_range[1]:
                score += 0.3

            if score > best_score:
                best_score = score
                best_genre = genre

        return best_genre if best_score > 0.5 else MusicGenre.UNKNOWN

    def _estimate_mood(self, tempo: float, energy: float, centroid: float) -> MusicMood:
        """Schaetzt die Stimmung basierend auf Audio-Features"""
        # Einfache Heuristik
        if tempo > 120 and energy > 0.7:
            return MusicMood.ENERGETIC
        elif tempo < 80 and energy < 0.4:
            return MusicMood.CALM
        elif tempo > 100 and energy > 0.5:
            return MusicMood.HAPPY
        elif tempo < 90 and energy < 0.5:
            return MusicMood.SAD
        elif tempo > 130 and energy > 0.8 and centroid > 3000:
            return MusicMood.AGGRESSIVE
        elif tempo < 100 and centroid < 1500:
            return MusicMood.MELANCHOLIC
        else:
            return MusicMood.NEUTRAL

    def _calculate_emotional_impact(self, tempo: float, energy: float, mood: MusicMood) -> Dict[str, float]:
        """Berechnet die emotionale Wirkung der Musik"""
        impact = {
            "freude": 0.0,
            "trauer": 0.0,
            "energie": energy,
            "ruhe": 1.0 - energy,
            "spannung": 0.0,
            "nostalgie": 0.0
        }

        if mood == MusicMood.HAPPY:
            impact["freude"] = 0.7
        elif mood == MusicMood.SAD:
            impact["trauer"] = 0.6
            impact["nostalgie"] = 0.4
        elif mood == MusicMood.ENERGETIC:
            impact["freude"] = 0.5
            impact["spannung"] = 0.4
        elif mood == MusicMood.CALM:
            impact["ruhe"] = 0.8
        elif mood == MusicMood.MELANCHOLIC:
            impact["trauer"] = 0.4
            impact["nostalgie"] = 0.6
        elif mood == MusicMood.AGGRESSIVE:
            impact["spannung"] = 0.8

        # Tempo-Einfluss
        if tempo > 140:
            impact["spannung"] = min(1.0, impact["spannung"] + 0.3)
        elif tempo < 70:
            impact["ruhe"] = min(1.0, impact["ruhe"] + 0.2)

        return {k: round(v, 2) for k, v in impact.items()}

    # =========================================================================
    # BEAT-ANALYSE
    # =========================================================================

    def analyze_beats(self, audio_path: str) -> Optional[BeatAnalysis]:
        """
        Analysiert den Beat/Rhythmus.

        Ermittelt:
        - Tempo (BPM)
        - Beat-Positionen
        - Taktart (geschaetzt)
        - Tempo-Stabilitaet
        """
        if not self.has_librosa:
            return None

        audio_data = self._load_audio(audio_path)
        if not audio_data:
            return None

        y, sr = audio_data

        # Beat-Tracking
        tempo_array, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo_array) if isinstance(tempo_array, (int, float)) else float(tempo_array[0]) if len(tempo_array) > 0 else 0.0

        # Beat-Positionen in Sekunden
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        beat_positions = [float(t) for t in beat_times]

        # Tempo-Stabilitaet (basierend auf Beat-Intervallen)
        if len(beat_positions) > 2:
            intervals = np.diff(beat_positions)
            stability = 1.0 - min(1.0, np.std(intervals) / np.mean(intervals))
        else:
            stability = 0.0

        # Taktart schaetzen (vereinfacht: 4/4 oder 3/4)
        beats_per_bar = 4  # Standard-Annahme

        # Regelmaessigkeit
        is_regular = stability > 0.7

        return BeatAnalysis(
            tempo_bpm=round(tempo, 1),
            beats_per_bar=beats_per_bar,
            beat_positions=beat_positions[:100],  # Max 100 Beats
            is_regular=is_regular,
            tempo_stability=round(stability, 2)
        )

    # =========================================================================
    # SPEKTRAL-ANALYSE
    # =========================================================================

    def analyze_spectrum(self, audio_path: str) -> Optional[SpectralAnalysis]:
        """
        Fuehrt eine Spektral-Analyse durch.

        Ermittelt:
        - Spektrale Merkmale
        - MFCC Features
        - Frequenzband-Verteilung
        """
        if not self.has_librosa or not self.has_numpy:
            return None

        audio_data = self._load_audio(audio_path)
        if not audio_data:
            return None

        y, sr = audio_data

        # Spektrale Merkmale
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_means = np.mean(mfccs, axis=1)

        # Frequenzbaender
        # Bass: 20-250 Hz, Mid: 250-4000 Hz, Treble: 4000-20000 Hz
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)

        bass_mask = freqs < 250
        mid_mask = (freqs >= 250) & (freqs < 4000)
        treble_mask = freqs >= 4000

        bass_energy = np.mean(S[bass_mask, :]) if np.any(bass_mask) else 0.0
        mid_energy = np.mean(S[mid_mask, :]) if np.any(mid_mask) else 0.0
        treble_energy = np.mean(S[treble_mask, :]) if np.any(treble_mask) else 0.0

        total = bass_energy + mid_energy + treble_energy
        if total > 0:
            frequency_bands = {
                "bass": round(bass_energy / total, 2),
                "mid": round(mid_energy / total, 2),
                "treble": round(treble_energy / total, 2)
            }
        else:
            frequency_bands = {"bass": 0.33, "mid": 0.33, "treble": 0.33}

        return SpectralAnalysis(
            spectral_centroid=round(float(centroid), 1),
            spectral_bandwidth=round(float(bandwidth), 1),
            spectral_rolloff=round(float(rolloff), 1),
            mfcc_features=[round(float(m), 3) for m in mfcc_means],
            frequency_bands=frequency_bands
        )

    # =========================================================================
    # SPRACH-ERKENNUNG
    # =========================================================================

    def recognize_speech(self, audio_path: str, language: str = "de-DE") -> Optional[SpeechResult]:
        """
        Erkennt Sprache in einer Audio-Datei.

        Args:
            audio_path: Pfad zur Audio-Datei
            language: Sprache (z.B. "de-DE", "en-US")

        Returns:
            SpeechResult mit erkanntem Text
        """
        if not self.has_speech:
            logger.warning("Speech Recognition nicht verfuegbar")
            return None

        # Pruefe ob WAV
        if not audio_path.lower().endswith('.wav'):
            logger.warning("Speech Recognition benoetigt WAV-Format")
            return None

        try:
            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                duration = source.DURATION

            # Sprache erkennen (mit Google)
            try:
                text = recognizer.recognize_google(audio, language=language)
                confidence = 0.8  # Google gibt keine Confidence zurueck
            except sr.UnknownValueError:
                text = ""
                confidence = 0.0
            except sr.RequestError as e:
                logger.error(f"Speech Recognition API Fehler: {e}")
                return None

            words = text.split() if text else []
            speaking_rate = (len(words) / duration) * 60 if duration > 0 else 0

            return SpeechResult(
                text=text,
                confidence=confidence,
                language=language,
                word_count=len(words),
                duration_seconds=round(duration, 2),
                speaking_rate=round(speaking_rate, 1)
            )

        except Exception as e:
            logger.error(f"Speech Recognition Fehler: {e}")
            return None

    # =========================================================================
    # UTILITY-FUNKTIONEN
    # =========================================================================

    def get_capabilities(self) -> Dict[str, bool]:
        """Gibt die verfuegbaren Faehigkeiten zurueck"""
        return {
            "basic_analysis": True,
            "music_analysis": self.has_librosa,
            "beat_detection": self.has_librosa,
            "spectral_analysis": self.has_librosa and self.has_numpy,
            "speech_recognition": self.has_speech,
            "numpy_support": self.has_numpy,
            "scipy_support": self.has_scipy,
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO AUDIO - Test")
    print("=" * 60)

    audio = HoloAudio()

    print(f"\nVerfuegbare Features:")
    for cap, available in audio.get_capabilities().items():
        status = "ja" if available else "nein"
        print(f"  - {cap}: {status}")

    # Test mit Audio-Datei (falls vorhanden)
    test_files = ["test.wav", "test.mp3", "music.wav"]

    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n--- Analysiere: {test_file} ---")

            # Audio-Info
            info = audio.get_audio_info(test_file)
            if info:
                print(f"Dauer: {info.duration_seconds}s")
                print(f"Sample Rate: {info.sample_rate} Hz")

            # Typ
            audio_type = audio.classify_audio_type(test_file)
            print(f"Typ: {audio_type.value}")

            # Musik-Analyse
            if audio_type in [AudioType.MUSIC, AudioType.MIXED]:
                result = audio.analyze_music(test_file)
                if result:
                    print(f"Tempo: {result.tempo_bpm} BPM")
                    print(f"Genre: {result.genre.value}")
                    print(f"Stimmung: {result.mood.value}")
                    print(f"Energie: {result.energy}")

            break
    else:
        print("\nKeine Test-Audio-Datei gefunden.")
        print("Erstellen Sie eine WAV-Datei fuer vollstaendigen Test.")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)
