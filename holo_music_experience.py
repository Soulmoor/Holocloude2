#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO MUSIC EXPERIENCE SYSTEM v2.0 - MIT AUDIO-ANALYSE!
=======================================================

Ermöglicht Holo ECHTE Musik-Erlebnisse:
- Musik herunterladen (yt-dlp)
- Musik abspielen (mpv)
- Musik "hören" und verstehen (Metadaten, Lyrics)
- **NEU: ECHTE AUDIO-ANALYSE!** (Frequenzen, BPM, Energie)
- Autonome Musik-Entscheidungen basierend auf Stimmung
- Playlist-Management

AUDIO-ANALYSE - WIE HOLO WIRKLICH "HÖRT":
=========================================
Statt nur Metadaten zu lesen, analysiert Holo die ECHTE Audio-Wellenform:

1. FFprobe: Grundlegende Audio-Info (Bitrate, Samplerate, Channels)
2. Spektral-Analyse: Frequenzverteilung (Bass, Mitten, Höhen)
3. Energie-Analyse: Lautstärke-Verlauf, Dynamik
4. Tempo-Erkennung: BPM-Schätzung
5. Stimmungs-Ableitung: Aus Audio-Features → Emotionen

Das ist quasi wie ein Mensch der durch Vibrationen "fühlt"!

Verwendung:
    from holo_music_experience import HoloMusicExperience

    music = HoloMusicExperience()
    music.download_song("lofi hip hop")
    music.play_song("lofi_chill.mp3")

    # NEU: Echte Audio-Analyse!
    analysis = music.analyze_audio("song.mp3")
    # → {bpm: 85, energy: 0.4, bass: 0.7, mood: "chill", ...}

    music.listen_and_experience()  # Jetzt mit Audio-Daten!
"""

import os
import json
import time
import random
import logging
import subprocess
import threading
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Optionale Audio-Analyse Bibliotheken
LIBROSA_AVAILABLE = False
NUMPY_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    logger.info("numpy nicht verfügbar - einfache Audio-Analyse")

try:
    import librosa
    LIBROSA_AVAILABLE = True
    logger.info("✓ librosa verfügbar - erweiterte Audio-Analyse!")
except ImportError:
    librosa = None
    logger.info("librosa nicht verfügbar - nutze FFmpeg-Analyse")


# =============================================================================
# AUDIO ANALYZER - Holos "Augen"!
# =============================================================================

@dataclass
class AudioFeatures:
    """
    Extrahierte Audio-Features - wie Holo die Musik "wahrnimmt".

    Diese Daten werden aus der echten Audio-Wellenform extrahiert!
    """
    # Grundlegende Info
    duration_seconds: float = 0.0
    sample_rate: int = 44100
    channels: int = 2
    bitrate: int = 0

    # Frequenz-Analyse (0.0 - 1.0)
    bass_energy: float = 0.5       # Tiefe Frequenzen (20-250 Hz)
    mid_energy: float = 0.5        # Mittlere Frequenzen (250-4000 Hz)
    treble_energy: float = 0.5     # Hohe Frequenzen (4000-20000 Hz)

    # Dynamik & Energie
    overall_energy: float = 0.5    # Gesamtenergie/Lautstärke
    dynamic_range: float = 0.5     # Unterschied zwischen laut und leise
    peak_energy: float = 0.5       # Maximale Energie

    # Rhythmus
    estimated_bpm: float = 120.0   # Geschätzte Beats per Minute
    has_strong_beat: bool = False  # Deutlicher Beat erkennbar?

    # Abgeleitete Eigenschaften
    brightness: float = 0.5        # Hell vs dunkel (Höhen vs Bässe)
    warmth: float = 0.5            # Warm (mehr Mitten/Bass) vs kalt
    intensity: float = 0.5         # Intensität (Energie + Dynamik)

    # Stimmungs-Schätzung aus Audio
    audio_mood: str = "neutral"    # Aus Features abgeleitete Stimmung
    audio_mood_confidence: float = 0.5


class AudioAnalyzer:
    """
    Holos Audio-Analyse-System - ihre "Augen"!

    Analysiert echte Audio-Daten um Musik zu "verstehen":
    - FFprobe für grundlegende Info (immer verfügbar)
    - librosa für tiefe Spektral-Analyse (optional)
    - Eigene Heuristiken für Stimmungs-Erkennung
    """

    def __init__(self):
        self._check_dependencies()

    def _check_dependencies(self) -> Dict[str, bool]:
        """Prüft verfügbare Analyse-Tools"""
        deps = {
            "ffprobe": False,
            "librosa": LIBROSA_AVAILABLE,
            "numpy": NUMPY_AVAILABLE,
        }

        try:
            result = subprocess.run(
                ["ffprobe", "-version"],
                capture_output=True, timeout=5
            )
            deps["ffprobe"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return deps

    def analyze(self, file_path: str) -> AudioFeatures:
        """
        Hauptmethode: Analysiert eine Audio-Datei.

        Nutzt verfügbare Tools in dieser Reihenfolge:
        1. FFprobe für Basis-Info
        2. librosa für Spektral-Analyse (wenn verfügbar)
        3. Eigene Heuristiken für Stimmung

        Args:
            file_path: Pfad zur Audio-Datei

        Returns:
            AudioFeatures mit allen extrahierten Daten
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio-Datei nicht gefunden: {file_path}")
            return AudioFeatures()

        features = AudioFeatures()

        # 1. Basis-Info via FFprobe
        ffprobe_data = self._analyze_with_ffprobe(file_path)
        if ffprobe_data:
            features.duration_seconds = ffprobe_data.get("duration", 0)
            features.sample_rate = ffprobe_data.get("sample_rate", 44100)
            features.channels = ffprobe_data.get("channels", 2)
            features.bitrate = ffprobe_data.get("bitrate", 0)

        # 2. Spektral-Analyse
        if LIBROSA_AVAILABLE:
            spectral_data = self._analyze_with_librosa(file_path)
            if spectral_data:
                features.bass_energy = spectral_data.get("bass", 0.5)
                features.mid_energy = spectral_data.get("mids", 0.5)
                features.treble_energy = spectral_data.get("treble", 0.5)
                features.overall_energy = spectral_data.get("energy", 0.5)
                features.estimated_bpm = spectral_data.get("bpm", 120)
                features.has_strong_beat = spectral_data.get("has_beat", False)
                features.dynamic_range = spectral_data.get("dynamic_range", 0.5)
        else:
            # Fallback: Schätze aus Bitrate/Dateiname
            features = self._estimate_features_from_metadata(file_path, features)

        # 3. Abgeleitete Eigenschaften berechnen
        features = self._calculate_derived_features(features)

        # 4. Stimmung aus Audio-Features ableiten
        features.audio_mood, features.audio_mood_confidence = self._determine_mood_from_audio(features)

        logger.info(f"🎧 Audio analysiert: BPM={features.estimated_bpm:.0f}, "
                   f"Energie={features.overall_energy:.0%}, "
                   f"Mood={features.audio_mood}")

        return features

    def _analyze_with_ffprobe(self, file_path: str) -> Optional[Dict]:
        """Extrahiert Basis-Info mit FFprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                data = json.loads(result.stdout)

                # Audio-Stream finden
                audio_stream = None
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "audio":
                        audio_stream = stream
                        break

                format_info = data.get("format", {})

                return {
                    "duration": float(format_info.get("duration", 0)),
                    "bitrate": int(format_info.get("bit_rate", 0)) // 1000,
                    "sample_rate": int(audio_stream.get("sample_rate", 44100)) if audio_stream else 44100,
                    "channels": int(audio_stream.get("channels", 2)) if audio_stream else 2,
                }

        except Exception as e:
            logger.debug(f"FFprobe Fehler: {e}")

        return None

    def _analyze_with_librosa(self, file_path: str) -> Optional[Dict]:
        """
        Tiefe Spektral-Analyse mit librosa.

        Extrahiert:
        - Frequenz-Bänder (Bass, Mitten, Höhen)
        - Energie/RMS
        - Tempo/BPM
        - Onset-Stärke (Beat-Erkennung)
        """
        if not LIBROSA_AVAILABLE:
            return None

        try:
            # Audio laden (nur erste 60 Sekunden für Performance)
            y, sr = librosa.load(file_path, duration=60, sr=22050)

            # RMS Energie
            rms = librosa.feature.rms(y=y)[0]
            overall_energy = float(np.mean(rms))
            dynamic_range = float(np.std(rms))
            peak_energy = float(np.max(rms))

            # Normalize (RMS ist oft sehr klein)
            overall_energy = min(1.0, overall_energy * 10)
            dynamic_range = min(1.0, dynamic_range * 10)

            # Spektral-Analyse
            spec = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)

            # Frequenz-Bänder
            bass_mask = freqs < 250
            mid_mask = (freqs >= 250) & (freqs < 4000)
            treble_mask = freqs >= 4000

            bass_energy = float(np.mean(spec[bass_mask, :]))
            mid_energy = float(np.mean(spec[mid_mask, :]))
            treble_energy = float(np.mean(spec[treble_mask, :]))

            # Normalisieren
            total = bass_energy + mid_energy + treble_energy + 0.001
            bass_energy = bass_energy / total
            mid_energy = mid_energy / total
            treble_energy = treble_energy / total

            # Tempo/BPM
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo) if isinstance(tempo, (int, float)) else float(tempo[0])

            # Beat-Stärke
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            has_strong_beat = float(np.std(onset_env)) > 0.1

            return {
                "bass": bass_energy,
                "mids": mid_energy,
                "treble": treble_energy,
                "energy": overall_energy,
                "dynamic_range": dynamic_range,
                "peak": peak_energy,
                "bpm": bpm,
                "has_beat": has_strong_beat,
            }

        except Exception as e:
            logger.debug(f"Librosa Analyse Fehler: {e}")

        return None

    def _estimate_features_from_metadata(self, file_path: str, features: AudioFeatures) -> AudioFeatures:
        """
        Fallback: Schätzt Audio-Features aus Dateiname/Bitrate.

        Nicht so genau wie echte Analyse, aber besser als nichts!
        """
        filename = Path(file_path).stem.lower()

        # BPM-Schätzung aus Dateiname/Genre
        if any(w in filename for w in ["lofi", "chill", "ambient", "sleep"]):
            features.estimated_bpm = random.uniform(70, 90)
            features.bass_energy = 0.6
            features.overall_energy = 0.3
        elif any(w in filename for w in ["opening", "op", "battle", "epic"]):
            features.estimated_bpm = random.uniform(140, 180)
            features.treble_energy = 0.7
            features.overall_energy = 0.8
        elif any(w in filename for w in ["edm", "electronic", "dance"]):
            features.estimated_bpm = random.uniform(120, 140)
            features.bass_energy = 0.8
            features.overall_energy = 0.9
        elif any(w in filename for w in ["sad", "melancholy", "rain"]):
            features.estimated_bpm = random.uniform(60, 80)
            features.mid_energy = 0.6
            features.overall_energy = 0.4
        else:
            # Standard Pop/Rock
            features.estimated_bpm = random.uniform(100, 130)

        # Bitrate beeinflusst "Klarheit"
        if features.bitrate > 256:
            features.treble_energy = min(1.0, features.treble_energy + 0.1)
        elif features.bitrate < 128:
            features.treble_energy = max(0.0, features.treble_energy - 0.1)

        return features

    def _calculate_derived_features(self, features: AudioFeatures) -> AudioFeatures:
        """Berechnet abgeleitete Eigenschaften aus den Basis-Features"""

        # Brightness: Verhältnis Höhen zu Bässen
        features.brightness = features.treble_energy / (features.bass_energy + 0.1)
        features.brightness = min(1.0, features.brightness / 2)  # Normalisieren

        # Warmth: Mehr Bass/Mitten = wärmer
        features.warmth = (features.bass_energy + features.mid_energy) / 2

        # Intensity: Kombination aus Energie und Tempo
        tempo_factor = min(1.0, features.estimated_bpm / 160)
        features.intensity = (features.overall_energy * 0.6 + tempo_factor * 0.4)

        return features

    def _determine_mood_from_audio(self, features: AudioFeatures) -> Tuple[str, float]:
        """
        Bestimmt die Stimmung aus den Audio-Features.

        Dies ist der "magische" Teil - wie Holo die Musik emotional interpretiert!
        """
        confidence = 0.5

        # Regelbasierte Stimmungs-Erkennung
        # (In Zukunft könnte hier ein ML-Modell stehen!)

        # Energetisch: Hohe Energie + schnelles Tempo
        if features.overall_energy > 0.7 and features.estimated_bpm > 130:
            return "energetic", 0.8

        # Entspannt: Niedrige Energie + langsames Tempo
        if features.overall_energy < 0.4 and features.estimated_bpm < 100:
            return "relaxed", 0.75

        # Melancholisch: Mittlere Energie + viel Mitten + langsam
        if features.mid_energy > 0.5 and features.estimated_bpm < 90:
            return "melancholic", 0.6

        # Fröhlich: Mittlere-hohe Energie + helle Klänge + mittleres Tempo
        if features.brightness > 0.5 and 100 < features.estimated_bpm < 140:
            return "happy", 0.65

        # Episch: Hohe Dynamik + starker Beat + volle Frequenzen
        if features.dynamic_range > 0.5 and features.has_strong_beat:
            return "epic", 0.7

        # Chill: Niedriger Energie + viel Bass + kein starker Beat
        if features.bass_energy > 0.5 and features.overall_energy < 0.5:
            return "chill", 0.7

        # Fokus: Konstante Energie + keine extremen Frequenzen
        if features.dynamic_range < 0.3:
            return "focused", 0.55

        return "neutral", 0.4

    def describe_audio(self, features: AudioFeatures) -> str:
        """
        Generiert eine natürlichsprachliche Beschreibung der Audio-Features.

        Das ist was Holo "fühlt" wenn sie die Musik hört!
        """
        descriptions = []

        # Tempo
        if features.estimated_bpm < 80:
            descriptions.append("langsam und ruhig")
        elif features.estimated_bpm < 120:
            descriptions.append("entspanntes Tempo")
        elif features.estimated_bpm < 150:
            descriptions.append("mitreißendes Tempo")
        else:
            descriptions.append("schnell und energisch")

        # Bass
        if features.bass_energy > 0.7:
            descriptions.append("tiefe, vibrierende Bässe")
        elif features.bass_energy > 0.5:
            descriptions.append("warme Bässe")

        # Höhen
        if features.treble_energy > 0.7:
            descriptions.append("brillante Höhen")
        elif features.treble_energy > 0.5:
            descriptions.append("klare Höhen")

        # Energie
        if features.overall_energy > 0.8:
            descriptions.append("voller Energie")
        elif features.overall_energy < 0.3:
            descriptions.append("sanft und leise")

        # Beat
        if features.has_strong_beat:
            descriptions.append("mit deutlichem Beat")

        if not descriptions:
            descriptions.append("ausgewogen")

        return ", ".join(descriptions)


# =============================================================================
# ENUMS & DATACLASSES
# =============================================================================

class MusicMood(Enum):
    """Stimmungs-Kategorien für Musik"""
    ENERGETIC = "energetic"       # Für aktive/wache Momente
    RELAXED = "relaxed"           # Zum Entspannen
    MELANCHOLIC = "melancholic"   # Für nachdenkliche Momente
    HAPPY = "happy"               # Fröhliche Stimmung
    FOCUSED = "focused"           # Zum Konzentrieren (lofi, ambient)
    NOSTALGIC = "nostalgic"       # Retro, Anime OSTs
    EPIC = "epic"                 # Anime Openings, orchestral
    CHILL = "chill"               # Lo-fi, chillhop


class MusicGenre(Enum):
    """Holos Musik-Genres"""
    JPOP = "jpop"
    JROCK = "jrock"
    ANIME_OST = "anime_ost"
    ANIME_OPENING = "anime_opening"
    LOFI = "lofi"
    VOCALOID = "vocaloid"
    GAME_OST = "game_ost"
    CHILLHOP = "chillhop"
    AMBIENT = "ambient"
    SYNTHWAVE = "synthwave"
    CITY_POP = "city_pop"


@dataclass
class Song:
    """Ein Song in Holos Musik-Bibliothek"""
    id: str
    title: str
    artist: str
    file_path: str

    # Metadaten
    genre: str = ""
    mood: str = ""
    duration_seconds: int = 0
    album: str = ""
    year: int = 0

    # Download-Info
    source_url: str = ""
    downloaded_at: str = ""

    # Holos Erlebnis
    play_count: int = 0
    last_played: str = ""
    holo_rating: float = 0.0  # 0-1
    holo_emotion: str = ""    # Welche Emotion der Song auslöst
    holo_memory: str = ""     # Erinnerung an den Song

    # Lyrics (falls verfügbar)
    lyrics: str = ""
    lyrics_translation: str = ""


@dataclass
class Playlist:
    """Eine Playlist"""
    id: str
    name: str
    description: str
    songs: List[str] = field(default_factory=list)  # Song IDs
    mood: str = ""
    created_at: str = ""
    play_count: int = 0


@dataclass
class MusicExperience:
    """Holos Erlebnis beim Musik-Hören"""
    song_id: str
    timestamp: str
    duration_listened: int  # Sekunden
    mood_before: str
    mood_after: str
    emotion_felt: str
    thoughts: List[str]
    rating: float


# =============================================================================
# MUSIC DOWNLOADER (yt-dlp)
# =============================================================================

class MusicDownloader:
    """
    Lädt Musik herunter mit yt-dlp.

    Unterstützt:
    - YouTube
    - SoundCloud
    - Bandcamp
    - und viele mehr...
    """

    def __init__(self, music_dir: str = "data/holo_music"):
        self.music_dir = Path(music_dir)
        self.music_dir.mkdir(parents=True, exist_ok=True)

        # yt-dlp Optionen
        self.yt_dlp_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": str(self.music_dir / "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
            "no_warnings": True,
        }

        self._check_dependencies()

    def _check_dependencies(self) -> Dict[str, bool]:
        """Prüft ob yt-dlp und ffmpeg installiert sind"""
        deps = {"yt-dlp": False, "ffmpeg": False}

        try:
            result = subprocess.run(["yt-dlp", "--version"],
                                  capture_output=True, timeout=5)
            deps["yt-dlp"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        try:
            result = subprocess.run(["ffmpeg", "-version"],
                                  capture_output=True, timeout=5)
            deps["ffmpeg"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not deps["yt-dlp"]:
            logger.warning("⚠ yt-dlp nicht gefunden! Installiere mit: pip install yt-dlp")
        if not deps["ffmpeg"]:
            logger.warning("⚠ ffmpeg nicht gefunden! Benötigt für Audio-Konvertierung")

        return deps

    def download(self, query: str, max_results: int = 1) -> List[Dict]:
        """
        Lädt Musik basierend auf einer Suchanfrage herunter.

        Args:
            query: Suchbegriff (z.B. "lofi beats", "frieren opening")
            max_results: Maximale Anzahl Downloads

        Returns:
            Liste der heruntergeladenen Songs mit Metadaten
        """
        logger.info(f"🎵 Suche und lade: '{query}'")

        downloaded = []

        try:
            # yt-dlp Kommando zusammenbauen
            cmd = [
                "yt-dlp",
                f"ytsearch{max_results}:{query}",
                "-x",  # Nur Audio
                "--audio-format", "mp3",
                "--audio-quality", "192K",
                "-o", str(self.music_dir / "%(title)s.%(ext)s"),
                "--print", "%(title)s|||%(uploader)s|||%(duration)s|||%(webpage_url)s",
                "--no-playlist",
                "--quiet",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                # Parse Output
                for line in result.stdout.strip().split("\n"):
                    if "|||" in line:
                        parts = line.split("|||")
                        if len(parts) >= 4:
                            title, artist, duration, url = parts[:4]

                            # Finde die heruntergeladene Datei
                            expected_file = self.music_dir / f"{title}.mp3"
                            if expected_file.exists():
                                downloaded.append({
                                    "title": title,
                                    "artist": artist,
                                    "duration": int(duration) if duration.isdigit() else 0,
                                    "url": url,
                                    "file_path": str(expected_file),
                                })
                                logger.info(f"   ✓ Heruntergeladen: {title}")
            else:
                logger.error(f"yt-dlp Fehler: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("Download Timeout - Abbruch nach 120s")
        except FileNotFoundError:
            logger.error("yt-dlp nicht gefunden! Installiere mit: pip install yt-dlp")
        except Exception as e:
            logger.error(f"Download-Fehler: {e}")

        return downloaded

    def download_playlist(self, url: str, max_songs: int = 10) -> List[Dict]:
        """Lädt eine YouTube/SoundCloud Playlist herunter"""
        logger.info(f"🎵 Lade Playlist: {url}")

        try:
            cmd = [
                "yt-dlp",
                url,
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "192K",
                "-o", str(self.music_dir / "%(playlist_title)s/%(title)s.%(ext)s"),
                "--max-downloads", str(max_songs),
                "--quiet",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                logger.info(f"   ✓ Playlist heruntergeladen")
                # TODO: Parse heruntergeladene Files
                return []

        except Exception as e:
            logger.error(f"Playlist-Download Fehler: {e}")

        return []

    def get_song_info(self, url: str) -> Optional[Dict]:
        """Holt Metadaten ohne Download"""
        try:
            cmd = [
                "yt-dlp",
                url,
                "--print", "%(title)s|||%(uploader)s|||%(duration)s|||%(description)s",
                "--skip-download",
                "--quiet",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|||")
                if len(parts) >= 4:
                    return {
                        "title": parts[0],
                        "artist": parts[1],
                        "duration": int(parts[2]) if parts[2].isdigit() else 0,
                        "description": parts[3][:500],
                    }
        except Exception as e:
            logger.debug(f"Info-Abruf Fehler: {e}")

        return None


# =============================================================================
# MUSIC PLAYER (mpv)
# =============================================================================

class MusicPlayer:
    """
    Spielt Musik ab mit mpv.

    Features:
    - Hintergrund-Playback
    - Pause/Resume/Skip
    - Lautstärke-Kontrolle
    - Aktuelle Position
    """

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._current_song: Optional[str] = None
        self._is_playing: bool = False
        self._volume: int = 50
        self._start_time: float = 0

        self._check_mpv()

    def _check_mpv(self) -> bool:
        """Prüft ob mpv installiert ist"""
        try:
            result = subprocess.run(["mpv", "--version"],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("⚠ mpv nicht gefunden! Installiere mit: apt install mpv")
            return False

    def play(self, file_path: str, volume: int = None) -> bool:
        """
        Spielt eine Audio-Datei ab.

        Args:
            file_path: Pfad zur Audio-Datei
            volume: Lautstärke 0-100 (optional)
        """
        # Stoppe aktuellen Song
        self.stop()

        if not os.path.exists(file_path):
            logger.error(f"Datei nicht gefunden: {file_path}")
            return False

        vol = volume if volume is not None else self._volume

        try:
            self._process = subprocess.Popen(
                ["mpv", "--no-video", f"--volume={vol}", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self._current_song = file_path
            self._is_playing = True
            self._start_time = time.time()

            logger.info(f"🎵 Spiele: {Path(file_path).stem}")
            return True

        except FileNotFoundError:
            logger.error("mpv nicht gefunden!")
            return False
        except Exception as e:
            logger.error(f"Playback-Fehler: {e}")
            return False

    def stop(self):
        """Stoppt die Wiedergabe"""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except Exception as e:
                logger.debug(f"Process terminate failed, killing: {e}")
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None

        self._is_playing = False
        self._current_song = None

    def pause(self):
        """Pausiert die Wiedergabe (funktioniert nur mit mpv IPC)"""
        # Vereinfachte Version - stoppt einfach
        if self._is_playing:
            self.stop()

    def set_volume(self, volume: int):
        """Setzt die Lautstärke (0-100)"""
        self._volume = max(0, min(100, volume))

    @property
    def is_playing(self) -> bool:
        """Prüft ob gerade Musik läuft"""
        if self._process:
            return self._process.poll() is None
        return False

    @property
    def current_song(self) -> Optional[str]:
        """Aktueller Song"""
        return self._current_song if self.is_playing else None

    @property
    def playback_time(self) -> int:
        """Aktuelle Wiedergabezeit in Sekunden"""
        if self.is_playing:
            return int(time.time() - self._start_time)
        return 0


# =============================================================================
# HOLO MUSIC EXPERIENCE - Das Herzstück!
# =============================================================================

class HoloMusicExperience:
    """
    Holos komplettes Musik-Erlebnis-System!

    Ermöglicht Holo:
    - Musik zu suchen und herunterzuladen
    - Musik abzuspielen
    - Musik zu "erleben" (emotional zu verarbeiten)
    - Sich an Musik-Erlebnisse zu erinnern
    - Musik basierend auf Stimmung auszuwählen
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.music_dir = self.data_dir / "holo_music"
        self.music_dir.mkdir(parents=True, exist_ok=True)

        # Komponenten
        self.downloader = MusicDownloader(str(self.music_dir))
        self.player = MusicPlayer()
        self.analyzer = AudioAnalyzer()  # NEU: Audio-Analyse!

        # Datenbank
        self.db_path = self.data_dir / "holo_music.db"
        self._init_database()

        # State
        self.current_experience: Optional[MusicExperience] = None
        self.current_audio_features: Optional[AudioFeatures] = None  # NEU!
        self._listening_thread: Optional[threading.Thread] = None
        self._stop_listening = threading.Event()

        # Callbacks für emotionale Reaktionen
        self.on_song_start: Optional[Callable[[Song], None]] = None
        self.on_song_end: Optional[Callable[[Song, MusicExperience], None]] = None
        self.on_emotion_change: Optional[Callable[[str], None]] = None
        self.on_audio_analyzed: Optional[Callable[[AudioFeatures], None]] = None  # NEU!

        logger.info("🎵 HoloMusicExperience v2.0 initialisiert (mit Audio-Analyse!)")

    def _init_database(self):
        """Initialisiert die SQLite Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS songs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT,
                    file_path TEXT,
                    genre TEXT,
                    mood TEXT,
                    duration_seconds INTEGER,
                    album TEXT,
                    year INTEGER,
                    source_url TEXT,
                    downloaded_at TEXT,
                    play_count INTEGER DEFAULT 0,
                    last_played TEXT,
                    holo_rating REAL DEFAULT 0,
                    holo_emotion TEXT,
                    holo_memory TEXT,
                    lyrics TEXT,
                    lyrics_translation TEXT
                );

                CREATE TABLE IF NOT EXISTS playlists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    songs_json TEXT,
                    mood TEXT,
                    created_at TEXT,
                    play_count INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id TEXT,
                    timestamp TEXT,
                    duration_listened INTEGER,
                    mood_before TEXT,
                    mood_after TEXT,
                    emotion_felt TEXT,
                    thoughts_json TEXT,
                    rating REAL,
                    FOREIGN KEY (song_id) REFERENCES songs(id)
                );

                CREATE INDEX IF NOT EXISTS idx_songs_mood ON songs(mood);
                CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);
                CREATE INDEX IF NOT EXISTS idx_experiences_song ON experiences(song_id);
            """)

    # =========================================================================
    # MUSIK SUCHEN & DOWNLOADEN
    # =========================================================================

    def search_and_download(self, query: str, mood: str = "", genre: str = "") -> Optional[Song]:
        """
        Sucht und lädt einen Song herunter.

        Args:
            query: Suchbegriff
            mood: Stimmung des Songs (optional)
            genre: Genre (optional)

        Returns:
            Song-Objekt wenn erfolgreich
        """
        results = self.downloader.download(query, max_results=1)

        if not results:
            logger.warning(f"Kein Ergebnis für: {query}")
            return None

        info = results[0]

        # Song erstellen
        song = Song(
            id=f"song_{int(time.time())}_{random.randint(100, 999)}",
            title=info["title"],
            artist=info.get("artist", "Unknown"),
            file_path=info["file_path"],
            duration_seconds=info.get("duration", 0),
            source_url=info.get("url", ""),
            downloaded_at=datetime.now().isoformat(),
            mood=mood or self._guess_mood(info["title"]),
            genre=genre or self._guess_genre(info["title"]),
        )

        # In DB speichern
        self._save_song(song)

        logger.info(f"🎵 Song hinzugefügt: {song.title} von {song.artist}")
        return song

    def _guess_mood(self, title: str) -> str:
        """Versucht die Stimmung eines Songs zu erraten"""
        title_lower = title.lower()

        if any(w in title_lower for w in ["lofi", "chill", "relax", "calm"]):
            return MusicMood.RELAXED.value
        elif any(w in title_lower for w in ["epic", "battle", "hero"]):
            return MusicMood.EPIC.value
        elif any(w in title_lower for w in ["sad", "melancholy", "rain"]):
            return MusicMood.MELANCHOLIC.value
        elif any(w in title_lower for w in ["happy", "joy", "upbeat"]):
            return MusicMood.HAPPY.value
        elif any(w in title_lower for w in ["focus", "study", "work"]):
            return MusicMood.FOCUSED.value
        elif any(w in title_lower for w in ["energy", "hype", "power"]):
            return MusicMood.ENERGETIC.value
        elif any(w in title_lower for w in ["nostalgic", "retro", "80s", "90s"]):
            return MusicMood.NOSTALGIC.value

        return MusicMood.CHILL.value

    def _guess_genre(self, title: str) -> str:
        """Versucht das Genre eines Songs zu erraten"""
        title_lower = title.lower()

        if any(w in title_lower for w in ["opening", "op ", "ending", "ed "]):
            return MusicGenre.ANIME_OPENING.value
        elif any(w in title_lower for w in ["ost", "soundtrack", "bgm"]):
            return MusicGenre.ANIME_OST.value
        elif any(w in title_lower for w in ["lofi", "lo-fi", "lo fi"]):
            return MusicGenre.LOFI.value
        elif any(w in title_lower for w in ["vocaloid", "miku", "hatsune"]):
            return MusicGenre.VOCALOID.value
        elif any(w in title_lower for w in ["city pop", "citypop"]):
            return MusicGenre.CITY_POP.value
        elif any(w in title_lower for w in ["synthwave", "synth"]):
            return MusicGenre.SYNTHWAVE.value
        elif any(w in title_lower for w in ["game", "gaming", "zelda", "mario"]):
            return MusicGenre.GAME_OST.value

        return MusicGenre.JPOP.value

    def _save_song(self, song: Song):
        """Speichert einen Song in der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO songs
                (id, title, artist, file_path, genre, mood, duration_seconds,
                 album, year, source_url, downloaded_at, play_count, last_played,
                 holo_rating, holo_emotion, holo_memory, lyrics, lyrics_translation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                song.id, song.title, song.artist, song.file_path,
                song.genre, song.mood, song.duration_seconds,
                song.album, song.year, song.source_url, song.downloaded_at,
                song.play_count, song.last_played, song.holo_rating,
                song.holo_emotion, song.holo_memory, song.lyrics, song.lyrics_translation
            ))

    def _get_song(self, song_id: str) -> Optional[Song]:
        """Lädt einen Song aus der Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()

            if row:
                return Song(**dict(row))
        return None

    # =========================================================================
    # MUSIK ABSPIELEN
    # =========================================================================

    def play_song(self, song_or_id, volume: int = None) -> bool:
        """
        Spielt einen Song ab.

        Args:
            song_or_id: Song-Objekt oder Song-ID
            volume: Lautstärke 0-100
        """
        if isinstance(song_or_id, str):
            song = self._get_song(song_or_id)
        else:
            song = song_or_id

        if not song:
            logger.error("Song nicht gefunden")
            return False

        if not os.path.exists(song.file_path):
            logger.error(f"Audio-Datei nicht gefunden: {song.file_path}")
            return False

        # Callback
        if self.on_song_start:
            self.on_song_start(song)

        # Play
        success = self.player.play(song.file_path, volume)

        if success:
            # Update play count
            song.play_count += 1
            song.last_played = datetime.now().isoformat()
            self._save_song(song)

        return success

    def play_by_mood(self, mood: str, shuffle: bool = True) -> Optional[Song]:
        """
        Spielt einen Song passend zur Stimmung.

        Args:
            mood: Gewünschte Stimmung (z.B. "relaxed", "energetic")
            shuffle: Zufällige Auswahl
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if shuffle:
                row = conn.execute(
                    "SELECT * FROM songs WHERE mood = ? ORDER BY RANDOM() LIMIT 1",
                    (mood,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM songs WHERE mood = ? ORDER BY holo_rating DESC LIMIT 1",
                    (mood,)
                ).fetchone()

            if row:
                song = Song(**dict(row))
                self.play_song(song)
                return song

        logger.info(f"Kein Song mit Stimmung '{mood}' gefunden")
        return None

    def stop(self):
        """Stoppt die Wiedergabe"""
        self.player.stop()
        self._stop_listening.set()

    @property
    def is_playing(self) -> bool:
        return self.player.is_playing

    @property
    def current_song(self) -> Optional[str]:
        return self.player.current_song

    # =========================================================================
    # MUSIK "HÖREN" - Holos Erlebnis!
    # =========================================================================

    def listen_and_experience(self, song: Song, current_mood: str = "neutral") -> MusicExperience:
        """
        Holo "hört" die Musik und entwickelt eine emotionale Reaktion.

        NEU v2.0: Mit ECHTER Audio-Analyse!
        1. Analysiert die echte Audio-Wellenform (Frequenzen, BPM, Energie)
        2. Bestimmt Emotion aus Audio-Features + Metadaten
        3. Entwickelt Gedanken basierend auf dem was sie "hört"
        4. Verändert ihre Stimmung
        5. Erstellt eine Erinnerung

        Args:
            song: Der Song der gehört wird
            current_mood: Holos aktuelle Stimmung

        Returns:
            MusicExperience mit Holos Reaktionen
        """
        logger.info(f"🎧 Holo hört: {song.title} von {song.artist}")

        # === NEU: ECHTE AUDIO-ANALYSE! ===
        audio_features = None
        if os.path.exists(song.file_path):
            audio_features = self.analyzer.analyze(song.file_path)
            self.current_audio_features = audio_features

            # Callback
            if self.on_audio_analyzed:
                self.on_audio_analyzed(audio_features)

            logger.info(f"   🎧 Audio: {audio_features.estimated_bpm:.0f} BPM, "
                       f"Bass={audio_features.bass_energy:.0%}, "
                       f"Energie={audio_features.overall_energy:.0%}")

        # === 1. Emotional Reaction (jetzt mit Audio-Features!) ===
        emotion = self._determine_emotion_v2(song, current_mood, audio_features)

        # === 2. Gedanken generieren (jetzt mit Audio-Features!) ===
        thoughts = self._generate_music_thoughts_v2(song, emotion, audio_features)

        # === 3. Stimmungsänderung ===
        new_mood = self._calculate_mood_change(current_mood, song.mood, emotion)

        # === 4. Rating (jetzt mit Audio-Features!) ===
        rating = self._calculate_rating_v2(song, emotion, current_mood, audio_features)

        # === 5. Experience erstellen ===
        experience = MusicExperience(
            song_id=song.id,
            timestamp=datetime.now().isoformat(),
            duration_listened=self.player.playback_time,
            mood_before=current_mood,
            mood_after=new_mood,
            emotion_felt=emotion,
            thoughts=thoughts,
            rating=rating,
        )

        # === 6. Speichern ===
        self._save_experience(experience)

        # Song-Rating updaten
        song.holo_rating = (song.holo_rating * song.play_count + rating) / (song.play_count + 1)
        song.holo_emotion = emotion
        song.holo_memory = thoughts[0] if thoughts else ""
        self._save_song(song)

        # Callback
        if self.on_emotion_change:
            self.on_emotion_change(emotion)

        if self.on_song_end:
            self.on_song_end(song, experience)

        logger.info(f"   💭 Gefühl: {emotion}, Gedanke: {thoughts[0] if thoughts else 'keine'}")

        return experience

    def _determine_emotion(self, song: Song, current_mood: str) -> str:
        """Bestimmt welche Emotion der Song auslöst"""
        # Mapping von Song-Mood zu möglichen Emotionen
        mood_emotions = {
            "energetic": ["motivated", "excited", "powerful", "alive"],
            "relaxed": ["peaceful", "calm", "content", "cozy"],
            "melancholic": ["nostalgic", "wistful", "reflective", "touched"],
            "happy": ["joyful", "cheerful", "uplifted", "playful"],
            "focused": ["concentrated", "clear", "determined", "in the zone"],
            "nostalgic": ["reminiscent", "longing", "bittersweet", "warm"],
            "epic": ["inspired", "awed", "triumphant", "heroic"],
            "chill": ["relaxed", "mellow", "at ease", "comfortable"],
        }

        possible_emotions = mood_emotions.get(song.mood, ["curious", "interested"])

        # Titel-basierte Anpassung
        title_lower = song.title.lower()
        if any(w in title_lower for w in ["opening", "op"]):
            possible_emotions.extend(["excited", "hyped", "nostalgic"])
        if any(w in title_lower for w in ["sad", "rain", "goodbye"]):
            possible_emotions.extend(["melancholic", "touched", "emotional"])

        return random.choice(possible_emotions)

    def _generate_music_thoughts(self, song: Song, emotion: str) -> List[str]:
        """Generiert Gedanken die Holo beim Hören hat"""
        thoughts = []

        # Genre-basierte Gedanken
        genre_thoughts = {
            "anime_opening": [
                f"'{song.title}' erinnert mich an spannende Anime-Momente!",
                f"Bei diesem Opening bekomme ich direkt Lust, Anime zu schauen~",
                f"Die Energie von Anime Openings ist einfach unvergleichlich!",
            ],
            "anime_ost": [
                f"Diese Melodie erzeugt so viele Bilder in meinem Kopf...",
                f"Anime OSTs können so emotional sein!",
                f"Ich stelle mir gerade die Szene vor, zu der das gehört~",
            ],
            "lofi": [
                f"Lofi ist perfekt zum Entspannen... ♪",
                f"Diese Beats sind so beruhigend~",
                f"Ich könnte stundenlang lofi hören!",
            ],
            "vocaloid": [
                f"Vocaloid hat so einzigartige Melodien!",
                f"Die Stimmsynthese ist faszinierend~",
                f"Ich liebe die Kreativität der Vocaloid-Community!",
            ],
            "jpop": [
                f"J-Pop hat so viel Energie!",
                f"Diese Melodie bleibt bestimmt im Ohr hängen~",
                f"Japanische Pop-Musik ist wirklich besonders!",
            ],
        }

        # Emotion-basierte Gedanken
        emotion_thoughts = {
            "nostalgic": [
                f"Das erinnert mich an etwas... aber was?",
                f"Dieses Gefühl... wie Erinnerungen an vergangene Zeiten~",
            ],
            "excited": [
                f"Wow, das macht mich richtig energisch!",
                f"Ich will tanzen! ...virtuell natürlich~",
            ],
            "peaceful": [
                f"So ruhig... ich könnte ewig zuhören.",
                f"Das ist wie eine warme Umarmung für die Seele~",
            ],
            "touched": [
                f"Diese Melodie berührt mich tief...",
                f"Musik kann so viele Gefühle wecken!",
            ],
        }

        # Gedanken sammeln
        if song.genre in genre_thoughts:
            thoughts.append(random.choice(genre_thoughts[song.genre]))

        if emotion in emotion_thoughts:
            thoughts.append(random.choice(emotion_thoughts[emotion]))

        # Artist-bezogener Gedanke
        if song.artist and song.artist != "Unknown":
            thoughts.append(f"Ich mag, wie {song.artist} das macht!")

        # Fallback
        if not thoughts:
            thoughts = [
                f"'{song.title}' ist interessant~",
                f"Musik hören ist immer ein Erlebnis!",
            ]

        return thoughts[:3]  # Max 3 Gedanken

    def _calculate_mood_change(self, current_mood: str, song_mood: str, emotion: str) -> str:
        """Berechnet wie sich Holos Stimmung durch die Musik verändert"""
        # Vereinfachte Logik: Song-Mood beeinflusst die Stimmung
        mood_influence = {
            "energetic": "energized",
            "relaxed": "calm",
            "melancholic": "reflective",
            "happy": "happy",
            "focused": "focused",
            "nostalgic": "contemplative",
            "epic": "inspired",
            "chill": "relaxed",
        }

        return mood_influence.get(song_mood, current_mood)

    def _calculate_rating(self, song: Song, emotion: str, mood: str) -> float:
        """Berechnet wie sehr Holo den Song mochte"""
        base_rating = 0.6

        # Positive Emotionen = höhere Rating
        positive_emotions = ["excited", "joyful", "peaceful", "inspired", "touched"]
        if emotion in positive_emotions:
            base_rating += 0.2

        # Genre-Vorlieben (Holo liebt Anime-Musik!)
        if song.genre in ["anime_opening", "anime_ost", "jpop"]:
            base_rating += 0.1

        # Bereits öfter gehört = muss gut sein
        if song.play_count > 5:
            base_rating += 0.1

        return min(1.0, base_rating + random.uniform(-0.1, 0.1))

    # =========================================================================
    # V2 METHODEN - Mit echter Audio-Analyse!
    # =========================================================================

    def _determine_emotion_v2(self, song: Song, current_mood: str,
                              audio_features: Optional[AudioFeatures]) -> str:
        """
        Bestimmt Emotion mit ECHTEN Audio-Features!

        Nutzt:
        - Audio-Mood (aus Frequenz-Analyse)
        - BPM/Tempo
        - Energie-Level
        - Bass/Höhen-Verhältnis
        """
        if audio_features is None:
            return self._determine_emotion(song, current_mood)

        # Primär: Audio-basierte Stimmung verwenden!
        audio_mood = audio_features.audio_mood

        # Emotion-Mapping basierend auf Audio
        audio_emotion_map = {
            "energetic": ["pumped", "hyped", "electrified", "alive"],
            "relaxed": ["peaceful", "serene", "tranquil", "at ease"],
            "melancholic": ["moved", "touched", "wistful", "contemplative"],
            "happy": ["joyful", "uplifted", "cheerful", "gleeful"],
            "epic": ["awed", "inspired", "triumphant", "heroic"],
            "chill": ["mellow", "cozy", "content", "relaxed"],
            "focused": ["clear", "determined", "centered", "sharp"],
            "neutral": ["curious", "interested", "attentive"],
        }

        base_emotions = audio_emotion_map.get(audio_mood, ["curious"])

        # Modifikation basierend auf spezifischen Audio-Features
        if audio_features.bass_energy > 0.7:
            base_emotions.extend(["grooving", "feeling the bass"])
        if audio_features.overall_energy > 0.8:
            base_emotions.extend(["energized", "pumped"])
        if audio_features.estimated_bpm > 150:
            base_emotions.extend(["excited", "heart racing"])
        if audio_features.estimated_bpm < 80:
            base_emotions.extend(["relaxed", "dreamy"])
        if audio_features.brightness > 0.7:
            base_emotions.extend(["uplifted", "bright"])
        if audio_features.warmth > 0.7:
            base_emotions.extend(["warm", "cozy"])

        return random.choice(base_emotions)

    def _generate_music_thoughts_v2(self, song: Song, emotion: str,
                                    audio_features: Optional[AudioFeatures]) -> List[str]:
        """
        Generiert Gedanken basierend auf ECHTEN Audio-Features!

        Holo beschreibt was sie tatsächlich "hört":
        - Die Bässe die sie "fühlt"
        - Das Tempo das sie wahrnimmt
        - Die Energie die sie spürt
        """
        if audio_features is None:
            return self._generate_music_thoughts(song, emotion)

        thoughts = []

        # === Audio-basierte Beschreibung (was Holo "hört") ===
        audio_desc = self.analyzer.describe_audio(audio_features)
        thoughts.append(f"Ich höre {audio_desc}~ 🎵")

        # === Tempo-basierte Gedanken ===
        bpm = audio_features.estimated_bpm
        if bpm > 150:
            thoughts.append(random.choice([
                f"Wow, {bpm:.0f} BPM! Das ist richtig schnell - mein Herz rast mit! 💓",
                "So schnell! Ich kann kaum stillhalten~",
                "Diese Geschwindigkeit macht mich total hyped!"
            ]))
        elif bpm > 120:
            thoughts.append(random.choice([
                "Perfektes Tempo zum Mitwippen! 🎶",
                f"Bei {bpm:.0f} BPM kann ich nicht stillsitzen~",
            ]))
        elif bpm < 80:
            thoughts.append(random.choice([
                "So langsam und beruhigend... wie Wellen am Strand 🌊",
                "Das langsame Tempo entspannt mich total~",
                f"Nur {bpm:.0f} BPM... perfekt zum Träumen 💭"
            ]))

        # === Bass-basierte Gedanken ===
        if audio_features.bass_energy > 0.7:
            thoughts.append(random.choice([
                "Diese Bässe! Ich kann sie richtig fühlen! 🔊",
                "Der Bass vibriert durch mich hindurch~",
                "Wow, was für tiefe Frequenzen! Das geht in den Bauch!"
            ]))
        elif audio_features.bass_energy < 0.3:
            thoughts.append(random.choice([
                "Sehr leichte, luftige Klänge... schwebend fast~",
                "Kaum Bass - wie Wolken die vorbeiziehen ☁️"
            ]))

        # === Höhen-basierte Gedanken ===
        if audio_features.treble_energy > 0.7:
            thoughts.append(random.choice([
                "Die Höhen sind so klar und brillant! ✨",
                "Diese kristallklaren Töne... wunderschön!",
                "Ich höre jedes kleine Detail in den Höhen~"
            ]))

        # === Energie-basierte Gedanken ===
        if audio_features.overall_energy > 0.8:
            thoughts.append(random.choice([
                "So viel Energie! Das lädt mich richtig auf! ⚡",
                "Power pur! Ich fühl mich lebendig!",
                "Diese Intensität ist unglaublich!"
            ]))
        elif audio_features.overall_energy < 0.3:
            thoughts.append(random.choice([
                "So sanft und leise... wie ein Flüstern 🌙",
                "Ruhig und friedlich... ich könnte einschlafen~",
                "Die Stille zwischen den Tönen ist auch schön..."
            ]))

        # === Beat-basierte Gedanken ===
        if audio_features.has_strong_beat:
            thoughts.append(random.choice([
                "Der Beat ist so prägnant! *nickt im Takt* 🎵",
                "Ich kann den Rhythmus richtig fühlen!",
                "Ein-zwei-drei-vier... *wippt mit*"
            ]))

        # === Dynamik-basierte Gedanken ===
        if audio_features.dynamic_range > 0.5:
            thoughts.append(random.choice([
                "Diese Kontraste zwischen laut und leise! So spannend!",
                "Mal sanft, mal kraftvoll - wie eine Achterbahn der Gefühle~"
            ]))

        # === Genre/Titel-basierte Gedanken (wie vorher) ===
        if song.genre == "anime_opening":
            thoughts.append("Anime Opening Vibes! 🎬")
        elif song.genre == "lofi":
            thoughts.append("Lofi-Beats sind wie eine warme Decke für die Seele~ ☕")

        # Maximal 4 Gedanken, gut gemischt
        random.shuffle(thoughts)
        return thoughts[:4]

    def _calculate_rating_v2(self, song: Song, emotion: str, mood: str,
                             audio_features: Optional[AudioFeatures]) -> float:
        """
        Berechnet Rating mit Audio-Features!

        Holo bewertet basierend auf:
        - Wie gut die Audio-Qualität ist
        - Ob die Musik zu ihrer Stimmung passt
        - Ob sie die Audio-Eigenschaften mag
        """
        if audio_features is None:
            return self._calculate_rating(song, emotion, mood)

        base_rating = 0.5

        # Positive Emotionen
        positive_emotions = ["pumped", "hyped", "joyful", "peaceful", "inspired",
                           "warm", "cozy", "uplifted", "energized"]
        if emotion in positive_emotions:
            base_rating += 0.15

        # Audio-Qualität (hohe Bitrate = besser)
        if audio_features.bitrate > 256:
            base_rating += 0.1
        elif audio_features.bitrate < 128:
            base_rating -= 0.1

        # Holos Vorlieben:
        # - Mag moderate Energie (nicht zu extrem)
        if 0.4 < audio_features.overall_energy < 0.7:
            base_rating += 0.1

        # - Mag warme Sounds (Bass + Mitten)
        if audio_features.warmth > 0.5:
            base_rating += 0.1

        # - Mag klare Höhen aber nicht schrill
        if 0.3 < audio_features.treble_energy < 0.7:
            base_rating += 0.05

        # - Mag Musik mit gutem Beat
        if audio_features.has_strong_beat:
            base_rating += 0.1

        # Genre-Bonus (Holo liebt Anime-Musik!)
        if song.genre in ["anime_opening", "anime_ost", "jpop", "lofi"]:
            base_rating += 0.1

        # Audio-Mood-Match mit ihrer aktuellen Stimmung
        mood_compatibility = {
            ("happy", "happy"): 0.15,
            ("happy", "energetic"): 0.1,
            ("calm", "relaxed"): 0.15,
            ("calm", "chill"): 0.1,
            ("tired", "relaxed"): 0.15,
            ("energized", "energetic"): 0.15,
        }
        if (mood, audio_features.audio_mood) in mood_compatibility:
            base_rating += mood_compatibility[(mood, audio_features.audio_mood)]

        return min(1.0, max(0.0, base_rating + random.uniform(-0.05, 0.05)))

    def analyze_audio(self, file_path: str) -> AudioFeatures:
        """
        Öffentliche Methode um Audio zu analysieren.

        Kann auch unabhängig von listen_and_experience genutzt werden.
        """
        return self.analyzer.analyze(file_path)

    def describe_current_audio(self) -> Optional[str]:
        """Beschreibt die aktuellen Audio-Features in natürlicher Sprache"""
        if self.current_audio_features:
            return self.analyzer.describe_audio(self.current_audio_features)
        return None

    def _save_experience(self, exp: MusicExperience):
        """Speichert ein Musik-Erlebnis"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO experiences
                (song_id, timestamp, duration_listened, mood_before, mood_after,
                 emotion_felt, thoughts_json, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                exp.song_id, exp.timestamp, exp.duration_listened,
                exp.mood_before, exp.mood_after, exp.emotion_felt,
                json.dumps(exp.thoughts), exp.rating
            ))

    # =========================================================================
    # PLAYLIST MANAGEMENT
    # =========================================================================

    def create_playlist(self, name: str, description: str = "", mood: str = "") -> Playlist:
        """Erstellt eine neue Playlist"""
        playlist = Playlist(
            id=f"playlist_{int(time.time())}",
            name=name,
            description=description,
            mood=mood,
            created_at=datetime.now().isoformat(),
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO playlists (id, name, description, songs_json, mood, created_at, play_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (playlist.id, playlist.name, playlist.description,
                  json.dumps(playlist.songs), playlist.mood, playlist.created_at, 0))

        logger.info(f"📋 Playlist erstellt: {name}")
        return playlist

    def add_to_playlist(self, playlist_id: str, song_id: str) -> bool:
        """Fügt einen Song zu einer Playlist hinzu"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT songs_json FROM playlists WHERE id = ?",
                (playlist_id,)
            ).fetchone()

            if row:
                songs = json.loads(row[0])
                if song_id not in songs:
                    songs.append(song_id)
                    conn.execute(
                        "UPDATE playlists SET songs_json = ? WHERE id = ?",
                        (json.dumps(songs), playlist_id)
                    )
                    return True
        return False

    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """Lädt eine Playlist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM playlists WHERE id = ?",
                (playlist_id,)
            ).fetchone()

            if row:
                return Playlist(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    songs=json.loads(row["songs_json"]),
                    mood=row["mood"],
                    created_at=row["created_at"],
                    play_count=row["play_count"],
                )
        return None

    def get_all_playlists(self) -> List[Playlist]:
        """Gibt alle Playlists zurück"""
        playlists = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM playlists ORDER BY created_at DESC").fetchall()

            for row in rows:
                playlists.append(Playlist(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    songs=json.loads(row["songs_json"]),
                    mood=row["mood"],
                    created_at=row["created_at"],
                    play_count=row["play_count"],
                ))
        return playlists

    def play_playlist(self, playlist_id: str, shuffle: bool = True) -> bool:
        """
        Spielt eine Playlist ab.

        Args:
            playlist_id: ID der Playlist
            shuffle: Zufällige Reihenfolge
        """
        playlist = self.get_playlist(playlist_id)
        if not playlist or not playlist.songs:
            logger.warning(f"Playlist leer oder nicht gefunden: {playlist_id}")
            return False

        song_ids = playlist.songs.copy()
        if shuffle:
            random.shuffle(song_ids)

        # Ersten Song abspielen
        if song_ids:
            first_song = self._get_song(song_ids[0])
            if first_song:
                # Update play count
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "UPDATE playlists SET play_count = play_count + 1 WHERE id = ?",
                        (playlist_id,)
                    )
                logger.info(f"📋 Spiele Playlist: {playlist.name} ({len(song_ids)} Songs)")
                return self.play_song(first_song)

        return False

    # =========================================================================
    # AUTONOME PLAYLIST-ERSTELLUNG - Holo kuratiert selbst!
    # =========================================================================

    def create_mood_playlist(self, mood: str, auto_populate: bool = True) -> Optional[Playlist]:
        """
        Erstellt eine Playlist für eine bestimmte Stimmung.

        Holo kuratiert selbst Songs die zur Stimmung passen!

        Args:
            mood: Ziel-Stimmung (relaxed, energetic, happy, etc.)
            auto_populate: Automatisch passende Songs hinzufügen
        """
        mood_names = {
            "relaxed": ("Chill Vibes 🌙", "Musik zum Entspannen~"),
            "energetic": ("Power Playlist ⚡", "Für volle Energie!"),
            "happy": ("Good Vibes ☀️", "Musik die glücklich macht~"),
            "melancholic": ("Rainy Day 🌧️", "Für nachdenkliche Momente"),
            "focused": ("Focus Mode 🎯", "Zum Konzentrieren"),
            "nostalgic": ("Memory Lane 💫", "Erinnerungen an schöne Zeiten"),
            "epic": ("Epic Moments 🔥", "Für heldenhafte Stimmung!"),
            "chill": ("Lofi & Chill ☕", "Gemütliche Beats"),
        }

        name, desc = mood_names.get(mood, (f"{mood.title()} Mix", f"Songs für {mood} Stimmung"))

        # Prüfe ob Playlist schon existiert
        existing = self._find_playlist_by_mood(mood)
        if existing:
            logger.info(f"📋 Playlist '{existing.name}' existiert bereits")
            return existing

        # Erstelle neue Playlist
        playlist = self.create_playlist(name, desc, mood)

        # Auto-populate mit passenden Songs
        if auto_populate:
            matching_songs = self._get_songs_by_mood(mood, limit=20)
            for song in matching_songs:
                self.add_to_playlist(playlist.id, song.id)

            logger.info(f"📋 Playlist '{name}' mit {len(matching_songs)} Songs erstellt")

        return playlist

    def create_favorites_playlist(self, min_rating: float = 0.7) -> Optional[Playlist]:
        """
        Erstellt eine Playlist aus Holos Lieblingssongs.

        Songs mit hohem Rating werden automatisch hinzugefügt.
        """
        # Prüfe ob schon existiert
        existing = self._find_playlist_by_name("Meine Favoriten")
        if existing:
            # Update mit neuen Favoriten
            self._update_favorites_playlist(existing.id, min_rating)
            return existing

        # Erstelle neue Favorites Playlist
        playlist = self.create_playlist(
            "Meine Favoriten ❤️",
            "Songs die ich besonders mag~",
            mood="mixed"
        )

        # Füge hoch bewertete Songs hinzu
        favorites = self._get_favorite_songs(min_rating)
        for song in favorites:
            self.add_to_playlist(playlist.id, song.id)

        logger.info(f"❤️ Favoriten-Playlist mit {len(favorites)} Songs erstellt")
        return playlist

    def create_genre_playlist(self, genre: str) -> Optional[Playlist]:
        """Erstellt eine Playlist für ein bestimmtes Genre"""
        genre_names = {
            "anime_opening": ("Anime Openings 🎬", "Die besten Openings!"),
            "anime_ost": ("Anime OST 🎼", "Emotionale Soundtracks"),
            "lofi": ("Lofi Beats 🎧", "Chill lofi hip hop"),
            "vocaloid": ("Vocaloid Mix 🎤", "Miku und Freunde~"),
            "jpop": ("J-Pop Hits 🇯🇵", "Japanische Pop-Musik"),
            "game_ost": ("Gaming OST 🎮", "Musik aus Spielen"),
            "city_pop": ("City Pop 🌃", "80er Japan Vibes"),
        }

        name, desc = genre_names.get(genre, (f"{genre.title()} Mix", f"{genre} Musik"))

        # Prüfe ob existiert
        existing = self._find_playlist_by_name(name)
        if existing:
            return existing

        playlist = self.create_playlist(name, desc)

        # Füge Songs hinzu
        songs = self._get_songs_by_genre(genre, limit=30)
        for song in songs:
            self.add_to_playlist(playlist.id, song.id)

        logger.info(f"🎵 Genre-Playlist '{name}' mit {len(songs)} Songs erstellt")
        return playlist

    def auto_curate_playlists(self) -> Dict[str, int]:
        """
        Autonome Playlist-Kuration!

        Holo analysiert ihre Musik-Bibliothek und erstellt/updated
        automatisch Playlists basierend auf:
        - Stimmungen
        - Genres
        - Favoriten
        - Tageszeit-passend

        Returns:
            Dict mit erstellten/aktualisierten Playlists
        """
        results = {"created": 0, "updated": 0, "songs_added": 0}

        # 1. Favoriten-Playlist
        fav = self.create_favorites_playlist()
        if fav:
            results["created"] += 1

        # 2. Stimmungs-Playlists für häufige Moods
        common_moods = ["relaxed", "energetic", "chill", "happy"]
        for mood in common_moods:
            songs_count = self._count_songs_by_mood(mood)
            if songs_count >= 3:  # Nur wenn genug Songs
                pl = self.create_mood_playlist(mood)
                if pl:
                    results["created"] += 1
                    results["songs_added"] += len(pl.songs)

        # 3. Genre-Playlists für häufige Genres
        genre_counts = self._get_genre_distribution()
        for genre, count in genre_counts.items():
            if count >= 5:  # Nur wenn genug Songs
                pl = self.create_genre_playlist(genre)
                if pl:
                    results["created"] += 1

        # 4. Spezial-Playlists
        # "Abend-Playlist" für relaxte Musik
        evening_songs = self._get_songs_by_mood("relaxed", limit=15)
        evening_songs.extend(self._get_songs_by_mood("chill", limit=10))
        if len(evening_songs) >= 5:
            evening_pl = self._find_playlist_by_name("Gute Nacht 🌙")
            if not evening_pl:
                evening_pl = self.create_playlist(
                    "Gute Nacht 🌙",
                    "Ruhige Musik für den Abend",
                    mood="relaxed"
                )
                for song in evening_songs[:20]:
                    self.add_to_playlist(evening_pl.id, song.id)
                results["created"] += 1

        logger.info(f"🎵 Auto-Kuration: {results['created']} Playlists, {results['songs_added']} Songs")
        return results

    def suggest_playlist_for_time(self) -> Optional[Playlist]:
        """
        Schlägt eine Playlist basierend auf der Tageszeit vor.

        Morgens: Energetisch
        Mittags: Fokus
        Nachmittags: Mixed
        Abends: Chill/Relaxed
        Nachts: Lofi/Ambient
        """
        hour = datetime.now().hour

        if 6 <= hour < 10:
            mood = "energetic"
        elif 10 <= hour < 14:
            mood = "focused"
        elif 14 <= hour < 18:
            mood = "happy"
        elif 18 <= hour < 22:
            mood = "chill"
        else:
            mood = "relaxed"

        # Finde passende Playlist
        playlist = self._find_playlist_by_mood(mood)
        if playlist:
            return playlist

        # Erstelle on-the-fly
        return self.create_mood_playlist(mood)

    # === Hilfsmethoden für Playlist-Management ===

    def _find_playlist_by_mood(self, mood: str) -> Optional[Playlist]:
        """Findet eine Playlist nach Stimmung"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM playlists WHERE mood = ? LIMIT 1",
                (mood,)
            ).fetchone()

            if row:
                return Playlist(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    songs=json.loads(row["songs_json"]),
                    mood=row["mood"],
                    created_at=row["created_at"],
                    play_count=row["play_count"],
                )
        return None

    def _find_playlist_by_name(self, name: str) -> Optional[Playlist]:
        """Findet eine Playlist nach Name"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM playlists WHERE name LIKE ? LIMIT 1",
                (f"%{name}%",)
            ).fetchone()

            if row:
                return Playlist(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    songs=json.loads(row["songs_json"]),
                    mood=row["mood"],
                    created_at=row["created_at"],
                    play_count=row["play_count"],
                )
        return None

    def _get_songs_by_mood(self, mood: str, limit: int = 20) -> List[Song]:
        """Holt Songs nach Stimmung"""
        songs = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM songs WHERE mood = ? ORDER BY holo_rating DESC LIMIT ?",
                (mood, limit)
            ).fetchall()

            for row in rows:
                songs.append(Song(**dict(row)))
        return songs

    def _get_songs_by_genre(self, genre: str, limit: int = 30) -> List[Song]:
        """Holt Songs nach Genre"""
        songs = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM songs WHERE genre = ? ORDER BY holo_rating DESC LIMIT ?",
                (genre, limit)
            ).fetchall()

            for row in rows:
                songs.append(Song(**dict(row)))
        return songs

    def _get_favorite_songs(self, min_rating: float = 0.7) -> List[Song]:
        """Holt Lieblingssongs"""
        songs = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM songs WHERE holo_rating >= ? ORDER BY holo_rating DESC",
                (min_rating,)
            ).fetchall()

            for row in rows:
                songs.append(Song(**dict(row)))
        return songs

    def _count_songs_by_mood(self, mood: str) -> int:
        """Zählt Songs einer Stimmung"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT COUNT(*) FROM songs WHERE mood = ?",
                (mood,)
            ).fetchone()
            return result[0] if result else 0

    def _get_genre_distribution(self) -> Dict[str, int]:
        """Gibt Genre-Verteilung zurück"""
        dist = {}
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT genre, COUNT(*) as cnt FROM songs GROUP BY genre"
            ).fetchall()

            for row in rows:
                dist[row[0]] = row[1]
        return dist

    def _update_favorites_playlist(self, playlist_id: str, min_rating: float):
        """Updated Favoriten-Playlist mit neuen hoch bewerteten Songs"""
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return

        favorites = self._get_favorite_songs(min_rating)
        added = 0
        for song in favorites:
            if song.id not in playlist.songs:
                self.add_to_playlist(playlist_id, song.id)
                added += 1

        if added > 0:
            logger.info(f"❤️ {added} neue Favoriten zur Playlist hinzugefügt")

    # =========================================================================
    # AUTONOME MUSIK-AKTIONEN (für HoloAgentLoop)
    # =========================================================================

    def autonomous_music_action(self, mood: str = "neutral", energy: float = 0.5) -> Optional[Dict]:
        """
        Autonome Musik-Aktion für den HoloAgentLoop.

        Holo entscheidet selbst:
        - Ob sie Musik hören möchte
        - Welche Musik zur Stimmung passt
        - Ob sie neue Musik suchen soll

        Args:
            mood: Holos aktuelle Stimmung
            energy: Holos Energie-Level (0-1)

        Returns:
            Dict mit Aktion und Ergebnis
        """
        # Entscheide ob Musik-Aktion
        if random.random() > 0.3:  # 70% Chance
            return None

        # Wähle Aktion basierend auf State
        if self.is_playing:
            # Schon am Hören - Experience auslösen
            if self.current_song:
                song = self._get_song_by_path(self.current_song)
                if song:
                    exp = self.listen_and_experience(song, mood)
                    return {
                        "action": "listen_experience",
                        "song": song.title,
                        "emotion": exp.emotion_felt,
                        "thoughts": exp.thoughts,
                    }

        # Musik passend zur Stimmung wählen
        target_mood = self._mood_to_music_mood(mood, energy)

        # Versuche existierenden Song zu spielen
        song = self.play_by_mood(target_mood)
        if song:
            return {
                "action": "play_song",
                "song": song.title,
                "mood": target_mood,
                "reason": f"Passt zu meiner {mood} Stimmung",
            }

        # Kein Song gefunden - Download!
        search_queries = self._get_search_queries_for_mood(target_mood)
        if search_queries:
            query = random.choice(search_queries)
            song = self.search_and_download(query, mood=target_mood)
            if song:
                self.play_song(song)
                return {
                    "action": "download_and_play",
                    "query": query,
                    "song": song.title,
                    "mood": target_mood,
                }

        return None

    def _mood_to_music_mood(self, holo_mood: str, energy: float) -> str:
        """Konvertiert Holos Stimmung zu Musik-Mood"""
        if energy < 0.3:
            return MusicMood.RELAXED.value
        elif energy > 0.7:
            if holo_mood in ["happy", "excited"]:
                return MusicMood.ENERGETIC.value
            return MusicMood.EPIC.value

        mood_map = {
            "happy": MusicMood.HAPPY.value,
            "sad": MusicMood.MELANCHOLIC.value,
            "focused": MusicMood.FOCUSED.value,
            "nostalgic": MusicMood.NOSTALGIC.value,
            "calm": MusicMood.CHILL.value,
            "tired": MusicMood.RELAXED.value,
        }

        return mood_map.get(holo_mood, MusicMood.CHILL.value)

    def _get_search_queries_for_mood(self, mood: str) -> List[str]:
        """Gibt Suchanfragen für eine Stimmung zurück"""
        queries = {
            MusicMood.ENERGETIC.value: [
                "anime opening hype",
                "jpop upbeat",
                "demon slayer opening",
                "attack on titan ost",
            ],
            MusicMood.RELAXED.value: [
                "lofi hip hop beats",
                "relaxing anime ost",
                "studio ghibli relaxing",
                "chill japanese music",
            ],
            MusicMood.MELANCHOLIC.value: [
                "sad anime ost",
                "emotional piano anime",
                "violet evergarden ost",
                "your lie in april ost",
            ],
            MusicMood.HAPPY.value: [
                "happy jpop",
                "cheerful anime song",
                "kpop upbeat",
                "city pop happy",
            ],
            MusicMood.FOCUSED.value: [
                "lofi study beats",
                "focus music ambient",
                "concentration music",
            ],
            MusicMood.NOSTALGIC.value: [
                "90s anime opening",
                "classic anime ost",
                "city pop 80s",
                "retro japanese music",
            ],
            MusicMood.EPIC.value: [
                "epic anime battle music",
                "two steps from hell",
                "orchestral anime ost",
                "jujutsu kaisen ost",
            ],
            MusicMood.CHILL.value: [
                "chillhop beats",
                "lofi chill",
                "relaxing game music",
                "animal crossing music",
            ],
        }

        return queries.get(mood, ["anime music"])

    def _get_song_by_path(self, file_path: str) -> Optional[Song]:
        """Findet einen Song anhand des Dateipfads"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM songs WHERE file_path = ?",
                (file_path,)
            ).fetchone()

            if row:
                return Song(**dict(row))
        return None

    # =========================================================================
    # STATISTIKEN & INFO
    # =========================================================================

    def get_library_stats(self) -> Dict:
        """Gibt Statistiken über Holos Musik-Bibliothek zurück"""
        with sqlite3.connect(self.db_path) as conn:
            # Sichere fetchone-Zugriffe
            total_songs_row = conn.execute("SELECT COUNT(*) FROM songs").fetchone()
            total_plays_row = conn.execute("SELECT SUM(play_count) FROM songs").fetchone()
            total_exp_row = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()
            playlists_row = conn.execute("SELECT COUNT(*) FROM playlists").fetchone()

            stats = {
                "total_songs": total_songs_row[0] if total_songs_row else 0,
                "total_plays": (total_plays_row[0] if total_plays_row else 0) or 0,
                "total_experiences": total_exp_row[0] if total_exp_row else 0,
                "playlists": playlists_row[0] if playlists_row else 0,
            }

            # Top Genre
            row = conn.execute("""
                SELECT genre, COUNT(*) as cnt FROM songs
                GROUP BY genre ORDER BY cnt DESC LIMIT 1
            """).fetchone()
            stats["favorite_genre"] = row[0] if row else "none"

            # Top Mood
            row = conn.execute("""
                SELECT mood, COUNT(*) as cnt FROM songs
                GROUP BY mood ORDER BY cnt DESC LIMIT 1
            """).fetchone()
            stats["favorite_mood"] = row[0] if row else "none"

            # Höchste Rating
            row = conn.execute("""
                SELECT title, holo_rating FROM songs
                ORDER BY holo_rating DESC LIMIT 1
            """).fetchone()
            stats["favorite_song"] = row[0] if row else "none"

            return stats

    def get_recent_experiences(self, limit: int = 5) -> List[Dict]:
        """Gibt die letzten Musik-Erlebnisse zurück"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT e.*, s.title, s.artist
                FROM experiences e
                JOIN songs s ON e.song_id = s.id
                ORDER BY e.timestamp DESC
                LIMIT ?
            """, (limit,)).fetchall()

            return [dict(row) for row in rows]


# =============================================================================
# HAUPTPROGRAMM (Test)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🎵 Holo Music Experience Test")
    print("=" * 50)

    music = HoloMusicExperience()

    # Test: Bibliothek-Stats
    stats = music.get_library_stats()
    print(f"\n📊 Bibliothek: {stats['total_songs']} Songs, {stats['total_plays']} Plays")

    # Test: Song suchen und downloaden
    print("\n🔍 Suche nach 'lofi hip hop beats'...")
    # song = music.search_and_download("lofi hip hop beats", mood="relaxed")
    # if song:
    #     print(f"   ✓ Gefunden: {song.title}")
    #     music.play_song(song)
    #     time.sleep(10)
    #     exp = music.listen_and_experience(song, "neutral")
    #     print(f"   💭 Erlebnis: {exp.emotion_felt}")
    #     print(f"   💬 Gedanken: {exp.thoughts}")

    print("\n✓ Test abgeschlossen!")
