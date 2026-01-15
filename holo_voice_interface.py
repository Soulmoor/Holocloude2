#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO VOICE INTERFACE - STT & TTS für echte Sprachinteraktion               ║
║                                                                              ║
║  Macht Holo zur sprechenden und hörenden KI!                                 ║
║                                                                              ║
║  MODI:                                                                       ║
║  • REMOTE (empfohlen): Nutzt holo_voice_server.py auf Mini-PC                ║
║  • LOCAL: Alles auf dem Pi4 (nur für leichte Backends)                       ║
║                                                                              ║
║  STT (Speech-to-Text) Backends:                                              ║
║  • Remote Server (Whisper auf Mini-PC) ← EMPFOHLEN                           ║
║  • Whisper (lokal, beste Qualität, braucht GPU/CPU Power)                    ║
║  • Vosk (lokal, schnell, leichtgewichtig)                                    ║
║  • Google Speech Recognition (online, gratis)                                ║
║                                                                              ║
║  TTS (Text-to-Speech) Backends:                                              ║
║  • Remote Server (Edge-TTS auf Mini-PC) ← EMPFOHLEN                          ║
║  • Piper (lokal, schnell, gute deutsche Stimmen)                             ║
║  • edge-tts (Microsoft, online, sehr gute Qualität)                          ║
║  • pyttsx3 (lokal, einfach, mäßige Qualität)                                 ║
║                                                                              ║
║  Integration:                                                                 ║
║  • Energy-System (müde = langsameres Sprechen)                               ║
║  • Emotions (fröhlich = höhere Tonlage)                                      ║
║  • Kemonomimi (Wolf-Sounds hinzufügen)                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import wave
import logging
import tempfile
import threading
import subprocess
import base64
from pathlib import Path
from typing import Optional, Dict, Callable, Generator, Tuple, Any, List
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# HTTP Client
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    # Fallback mit urllib
    import urllib.request
    import urllib.error

logger = logging.getLogger("HoloVoice")


# =============================================================================
# CONFIGURATION
# =============================================================================

class VoiceConfig:
    """Konfiguration für Voice Interface"""
    
    # === REMOTE SERVER (EMPFOHLEN für Pi4) ===
    USE_REMOTE = True  # True = Mini-PC, False = Lokal
    REMOTE_HOST = "192.168.178.42"  # Mini-PC IP
    REMOTE_PORT = 5007
    REMOTE_TIMEOUT = 30  # Sekunden
    
    # Pfade
    DATA_DIR = Path("~/.holo/voice").expanduser()
    MODELS_DIR = DATA_DIR / "models"
    CACHE_DIR = DATA_DIR / "cache"
    
    # STT Settings (nur für lokalen Betrieb)
    STT_BACKEND = "vosk"     # vosk für Pi4, whisper für starke Hardware
    WHISPER_MODEL = "base"   # tiny, base, small, medium, large
    VOSK_MODEL = "vosk-model-small-de-0.15"
    
    # TTS Settings (nur für lokalen Betrieb)
    TTS_BACKEND = "edge-tts"  # edge-tts (online) oder piper (offline)
    PIPER_VOICE = "de_DE-thorsten-medium"
    EDGE_VOICE = "de-DE-ConradNeural"  # oder de-DE-KatjaNeural
    
    # Audio Settings
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    
    # Voice Modulation
    ENABLE_EMOTION_MODULATION = True
    ENABLE_ENERGY_MODULATION = True
    
    # Wolf Sounds
    WOLF_SOUNDS = {
        "happy": ["*lächelt strahlend*", "*Schweif wedelt*"],
        "tired": ["*gähnt*", "*seufzt müde*"],
        "curious": ["*Ohren spitzen sich*", "*schaut interessiert*"],
        "excited": ["*springt aufgeregt*", "*strahlt vor Freude*"],
        "sad": ["*senkt die Ohren*", "*schaut traurig*"],
    }
    
    @classmethod
    def get_remote_url(cls) -> str:
        """Gibt die Remote Server URL zurück"""
        return f"http://{cls.REMOTE_HOST}:{cls.REMOTE_PORT}"


# =============================================================================
# REMOTE VOICE CLIENT (für Pi4 → Mini-PC)
# =============================================================================

class RemoteVoiceClient:
    """
    Client für Remote Voice Server auf Mini-PC.
    
    Sendet Audio zum Server und bekommt Text/Audio zurück.
    Ideal für Pi4 mit wenig RAM.
    """
    
    def __init__(self, host: str = None, port: int = None, timeout: int = None):
        self.host = host or VoiceConfig.REMOTE_HOST
        self.port = port or VoiceConfig.REMOTE_PORT
        self.timeout = timeout or VoiceConfig.REMOTE_TIMEOUT
        self.base_url = f"http://{self.host}:{self.port}"
        self._available = None
        
    def _request(self, method: str, endpoint: str, 
                 data: Dict = None, json_data: Dict = None) -> Optional[Dict]:
        """Macht HTTP Request zum Server"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if REQUESTS_AVAILABLE:
                if method == "GET":
                    resp = requests.get(url, timeout=self.timeout)
                else:
                    if json_data:
                        resp = requests.post(url, json=json_data, timeout=self.timeout)
                    else:
                        resp = requests.post(url, data=data, timeout=self.timeout)
                
                if resp.status_code == 200:
                    return resp.json()
                else:
                    logger.error(f"[Remote] HTTP {resp.status_code}: {resp.text}")
                    return None
            else:
                # Fallback mit urllib
                if method == "GET":
                    req = urllib.request.Request(url)
                else:
                    body = json.dumps(json_data).encode('utf-8') if json_data else data
                    req = urllib.request.Request(url, data=body)
                    req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode('utf-8'))
                    
        except Exception as e:
            logger.error(f"[Remote] Request Fehler: {e}")
            return None
    
    def is_available(self) -> bool:
        """Prüft ob Server erreichbar"""
        if self._available is not None:
            return self._available
        
        try:
            result = self._request("GET", "/health")
            self._available = result is not None and result.get("status") == "ok"
        except Exception as e:
            logger.debug(f"[VoiceInterface] is_available health check failed: {type(e).__name__}: {e}")
            self._available = False
        
        return self._available
    
    def get_status(self) -> Dict:
        """Holt Server-Status"""
        result = self._request("GET", "/status")
        return result or {"error": "Server nicht erreichbar"}
    
    def get_voices(self) -> List[Dict]:
        """Holt verfügbare TTS Stimmen"""
        result = self._request("GET", "/voices")
        if result:
            return result.get("voices", [])
        return []
    
    def transcribe(self, audio_data: bytes) -> str:
        """
        Transkribiert Audio über Remote Server.
        
        Args:
            audio_data: WAV Audio als Bytes
            
        Returns:
            Transkribierter Text
        """
        # Audio als base64 senden
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        result = self._request("POST", "/stt", json_data={"audio": audio_b64})
        
        if result and result.get("success"):
            return result.get("text", "")
        else:
            logger.error(f"[Remote] STT Fehler: {result}")
            return ""
    
    def synthesize(self, text: str, voice: str = None,
                   rate: float = 1.0, pitch: float = 1.0) -> Optional[bytes]:
        """
        Synthetisiert Text zu Audio über Remote Server.
        
        Args:
            text: Zu sprechender Text
            voice: TTS Stimme (optional)
            rate: Sprechgeschwindigkeit
            pitch: Tonhöhe
            
        Returns:
            Audio-Daten als Bytes (MP3 oder WAV)
        """
        result = self._request("POST", "/tts", json_data={
            "text": text,
            "voice": voice,
            "rate": rate,
            "pitch": pitch
        })
        
        if result and result.get("success"):
            audio_b64 = result.get("audio", "")
            if audio_b64:
                return base64.b64decode(audio_b64)
        
        logger.error(f"[Remote] TTS Fehler: {result}")
        return None


# =============================================================================
# STT BACKENDS
# =============================================================================

class STTBackend(ABC):
    """Abstrakte Basis für STT Backends"""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Transkribiert Audio zu Text"""
        pass
    
    @abstractmethod
    def transcribe_file(self, filepath: str) -> str:
        """Transkribiert Audio-Datei zu Text"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Prüft ob Backend verfügbar"""
        pass


class WhisperSTT(STTBackend):
    """
    OpenAI Whisper für STT - Beste Qualität!
    
    Installation:
        pip install openai-whisper
        # oder für schnellere Version:
        pip install faster-whisper
    """
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self._use_faster = False
        
    def _load_model(self):
        if self.model is not None:
            return
            
        # Versuche faster-whisper zuerst
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(self.model_name, device="auto")
            self._use_faster = True
            logger.info(f"[STT] faster-whisper '{self.model_name}' geladen")
        except ImportError:
            try:
                import whisper
                self.model = whisper.load_model(self.model_name)
                self._use_faster = False
                logger.info(f"[STT] whisper '{self.model_name}' geladen")
            except ImportError:
                logger.error("[STT] Whisper nicht installiert!")
                raise
    
    def transcribe(self, audio_data: bytes) -> str:
        """Transkribiert Audio-Bytes"""
        # Speichere temporär
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            return self.transcribe_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def transcribe_file(self, filepath: str) -> str:
        """Transkribiert Audio-Datei"""
        self._load_model()
        
        if self._use_faster:
            segments, _ = self.model.transcribe(filepath, language="de")
            return " ".join([seg.text for seg in segments]).strip()
        else:
            result = self.model.transcribe(filepath, language="de")
            return result["text"].strip()
    
    def is_available(self) -> bool:
        try:
            import whisper
            return True
        except ImportError:
            try:
                from faster_whisper import WhisperModel
                return True
            except ImportError:
                return False


class VoskSTT(STTBackend):
    """
    Vosk für STT - Schnell und leichtgewichtig!
    
    Installation:
        pip install vosk
        # Model herunterladen von https://alphacephei.com/vosk/models
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or str(VoiceConfig.MODELS_DIR / VoiceConfig.VOSK_MODEL)
        self.model = None
        self.recognizer = None
        
    def _load_model(self):
        if self.model is not None:
            return
            
        try:
            from vosk import Model, KaldiRecognizer
            
            if not os.path.exists(self.model_path):
                logger.error(f"[STT] Vosk-Model nicht gefunden: {self.model_path}")
                raise FileNotFoundError(f"Vosk model nicht gefunden: {self.model_path}")
            
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, VoiceConfig.SAMPLE_RATE)
            logger.info(f"[STT] Vosk Model geladen: {self.model_path}")
        except ImportError:
            logger.error("[STT] Vosk nicht installiert!")
            raise
    
    def transcribe(self, audio_data: bytes) -> str:
        """Transkribiert Audio-Bytes"""
        self._load_model()
        
        self.recognizer.AcceptWaveform(audio_data)
        result = json.loads(self.recognizer.FinalResult())
        return result.get("text", "").strip()
    
    def transcribe_file(self, filepath: str) -> str:
        """Transkribiert Audio-Datei"""
        self._load_model()
        
        with wave.open(filepath, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                self.recognizer.AcceptWaveform(data)
        
        result = json.loads(self.recognizer.FinalResult())
        return result.get("text", "").strip()
    
    def is_available(self) -> bool:
        try:
            from vosk import Model
            return os.path.exists(self.model_path)
        except ImportError:
            return False


class GoogleSTT(STTBackend):
    """
    Google Speech Recognition - Online, gratis!
    
    Installation:
        pip install SpeechRecognition
    """
    
    def __init__(self):
        self.recognizer = None
        
    def _init_recognizer(self):
        if self.recognizer is not None:
            return
            
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            logger.info("[STT] Google Speech Recognition bereit")
        except ImportError:
            logger.error("[STT] SpeechRecognition nicht installiert!")
            raise
    
    def transcribe(self, audio_data: bytes) -> str:
        """Transkribiert Audio-Bytes"""
        # Speichere temporär
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            return self.transcribe_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def transcribe_file(self, filepath: str) -> str:
        """Transkribiert Audio-Datei"""
        self._init_recognizer()
        import speech_recognition as sr
        
        with sr.AudioFile(filepath) as source:
            audio = self.recognizer.record(source)
        
        try:
            return self.recognizer.recognize_google(audio, language="de-DE")
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logger.error(f"[STT] Google API Fehler: {e}")
            return ""
    
    def is_available(self) -> bool:
        try:
            import speech_recognition
            return True
        except ImportError:
            return False


# =============================================================================
# TTS BACKENDS
# =============================================================================

class TTSBackend(ABC):
    """Abstrakte Basis für TTS Backends"""
    
    @abstractmethod
    def speak(self, text: str, output_file: str = None) -> Optional[str]:
        """
        Spricht Text.
        
        Args:
            text: Zu sprechender Text
            output_file: Optional - speichert als Datei statt abzuspielen
            
        Returns:
            Pfad zur Audio-Datei wenn output_file, sonst None
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Prüft ob Backend verfügbar"""
        pass
    
    def set_voice_params(self, rate: float = 1.0, pitch: float = 1.0, volume: float = 1.0):
        """Setzt Sprachparameter (wenn unterstützt)"""
        pass


class PiperTTS(TTSBackend):
    """
    Piper TTS - Schnell, lokal, gute Qualität!
    
    Installation:
        pip install piper-tts
        # oder Binary von https://github.com/rhasspy/piper/releases
        
    Stimmen:
        https://huggingface.co/rhasspy/piper-voices
        Empfohlen für Deutsch: de_DE-thorsten-medium
    """
    
    def __init__(self, voice: str = None):
        self.voice = voice or VoiceConfig.PIPER_VOICE
        self.model_path = VoiceConfig.MODELS_DIR / f"{self.voice}.onnx"
        self.config_path = VoiceConfig.MODELS_DIR / f"{self.voice}.onnx.json"
        self._rate = 1.0
        
    def speak(self, text: str, output_file: str = None) -> Optional[str]:
        """Spricht Text mit Piper"""
        
        output = output_file or tempfile.mktemp(suffix=".wav")
        
        # Versuche Python-API
        try:
            from piper import PiperVoice
            
            voice = PiperVoice.load(str(self.model_path), str(self.config_path))
            
            with wave.open(output, 'wb') as wav_file:
                voice.synthesize(text, wav_file)
            
            if not output_file:
                self._play_audio(output)
                os.unlink(output)
                return None
            return output
            
        except ImportError:
            pass
        
        # Fallback: CLI
        try:
            cmd = [
                "piper",
                "--model", str(self.model_path),
                "--output_file", output
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate(input=text.encode('utf-8'))
            
            if not output_file:
                self._play_audio(output)
                os.unlink(output)
                return None
            return output
            
        except FileNotFoundError:
            logger.error("[TTS] Piper nicht gefunden!")
            return None
    
    def _play_audio(self, filepath: str):
        """Spielt Audio-Datei ab"""
        try:
            # Linux: aplay
            subprocess.run(["aplay", filepath], check=True, capture_output=True)
        except FileNotFoundError:
            try:
                # Alternative: ffplay
                subprocess.run(["ffplay", "-nodisp", "-autoexit", filepath], 
                             check=True, capture_output=True)
            except FileNotFoundError:
                logger.warning("[TTS] Kein Audio-Player gefunden (aplay, ffplay)")
    
    def set_voice_params(self, rate: float = 1.0, pitch: float = 1.0, volume: float = 1.0):
        self._rate = rate
    
    def is_available(self) -> bool:
        # Prüfe Python-API
        try:
            from piper import PiperVoice
            return self.model_path.exists()
        except ImportError:
            pass
        
        # Prüfe CLI
        try:
            result = subprocess.run(["piper", "--help"], capture_output=True)
            return result.returncode == 0 and self.model_path.exists()
        except FileNotFoundError:
            return False


class EdgeTTS(TTSBackend):
    """
    Microsoft Edge TTS - Online, sehr gute Qualität!
    
    Installation:
        pip install edge-tts
        
    Stimmen:
        de-DE-ConradNeural (männlich)
        de-DE-KatjaNeural (weiblich)
    """
    
    def __init__(self, voice: str = None):
        self.voice = voice or VoiceConfig.EDGE_VOICE
        self._rate = "+0%"
        self._pitch = "+0Hz"
        self._volume = "+0%"
        
    def speak(self, text: str, output_file: str = None) -> Optional[str]:
        """Spricht Text mit Edge TTS"""
        import asyncio
        
        output = output_file or tempfile.mktemp(suffix=".mp3")
        
        async def _synthesize():
            try:
                import edge_tts
                
                communicate = edge_tts.Communicate(
                    text, 
                    self.voice,
                    rate=self._rate,
                    pitch=self._pitch,
                    volume=self._volume
                )
                await communicate.save(output)
                return True
            except Exception as e:
                logger.error(f"[TTS] Edge-TTS Fehler: {e}")
                return False
        
        # Async ausführen
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(_synthesize())
        
        if not success:
            return None
        
        if not output_file:
            self._play_audio(output)
            os.unlink(output)
            return None
        return output
    
    def _play_audio(self, filepath: str):
        """Spielt Audio-Datei ab"""
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", filepath], 
                         check=True, capture_output=True)
        except FileNotFoundError:
            try:
                subprocess.run(["mpv", "--no-video", filepath], 
                             check=True, capture_output=True)
            except FileNotFoundError:
                logger.warning("[TTS] Kein Audio-Player gefunden")
    
    def set_voice_params(self, rate: float = 1.0, pitch: float = 1.0, volume: float = 1.0):
        # Konvertiere zu Edge-TTS Format
        rate_percent = int((rate - 1.0) * 100)
        self._rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
        
        pitch_hz = int((pitch - 1.0) * 50)
        self._pitch = f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"
        
        vol_percent = int((volume - 1.0) * 100)
        self._volume = f"+{vol_percent}%" if vol_percent >= 0 else f"{vol_percent}%"
    
    def is_available(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False


class Pyttsx3TTS(TTSBackend):
    """
    pyttsx3 - Einfach, lokal, aber mäßige Qualität
    
    Installation:
        pip install pyttsx3
        # Linux braucht: sudo apt install espeak
    """
    
    def __init__(self):
        self.engine = None
        self._rate = 150
        self._volume = 1.0
        
    def _init_engine(self):
        if self.engine is not None:
            return
            
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # Deutsche Stimme suchen
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'german' in voice.name.lower() or 'de' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            
            self.engine.setProperty('rate', self._rate)
            self.engine.setProperty('volume', self._volume)
            logger.info("[TTS] pyttsx3 bereit")
        except Exception as e:
            logger.error(f"[TTS] pyttsx3 Fehler: {e}")
            raise
    
    def speak(self, text: str, output_file: str = None) -> Optional[str]:
        """Spricht Text mit pyttsx3"""
        self._init_engine()
        
        if output_file:
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            return output_file
        else:
            self.engine.say(text)
            self.engine.runAndWait()
            return None
    
    def set_voice_params(self, rate: float = 1.0, pitch: float = 1.0, volume: float = 1.0):
        self._rate = int(150 * rate)
        self._volume = volume
        if self.engine:
            self.engine.setProperty('rate', self._rate)
            self.engine.setProperty('volume', self._volume)
    
    def is_available(self) -> bool:
        try:
            import pyttsx3
            return True
        except ImportError:
            return False


# =============================================================================
# HOLO VOICE INTERFACE - Hauptklasse
# =============================================================================

@dataclass
class VoiceState:
    """Aktueller Zustand der Stimme"""
    is_speaking: bool = False
    is_listening: bool = False
    last_transcript: str = ""
    last_speech: str = ""
    emotion: str = "neutral"
    energy: float = 0.5


class HoloVoiceInterface:
    """
    Holos Sprach-Interface - Hören und Sprechen!
    
    Features:
    - REMOTE MODUS: Nutzt Mini-PC für STT/TTS (empfohlen für Pi4)
    - LOCAL MODUS: Alles lokal (für starke Hardware)
    - Automatische Backend-Auswahl
    - Energy-basierte Sprachmodulation
    - Emotions-basierte Tonhöhe
    - Wolf-Sounds Integration
    - Streaming-Support für lange Texte
    """
    
    def __init__(self, 
                 stt_backend: str = None,
                 tts_backend: str = None,
                 energy_system=None,
                 emotions=None,
                 use_remote: bool = None,
                 remote_host: str = None,
                 remote_port: int = None):
        """
        Args:
            stt_backend: "whisper", "vosk", "google", "remote" oder None für Auto
            tts_backend: "piper", "edge-tts", "pyttsx3", "remote" oder None für Auto
            energy_system: HoloEnergySystem für Modulation
            emotions: EmotionalCore für Modulation
            use_remote: True = Mini-PC nutzen, False = lokal, None = Auto
            remote_host: IP des Voice Servers
            remote_port: Port des Voice Servers
        """
        self.energy_system = energy_system
        self.emotions = emotions
        self.state = VoiceState()
        
        # Remote-Konfiguration
        if use_remote is None:
            use_remote = VoiceConfig.USE_REMOTE
        self.use_remote = use_remote
        
        if remote_host:
            VoiceConfig.REMOTE_HOST = remote_host
        if remote_port:
            VoiceConfig.REMOTE_PORT = remote_port
        
        # Remote Client (wenn aktiviert)
        self.remote_client: Optional[RemoteVoiceClient] = None
        if self.use_remote:
            self.remote_client = RemoteVoiceClient()
            if self.remote_client.is_available():
                logger.info(f"🌐 Remote Voice Server verfügbar: {VoiceConfig.get_remote_url()}")
            else:
                logger.warning("⚠️ Remote Voice Server nicht erreichbar, Fallback auf lokal")
                self.use_remote = False
                self.remote_client = None
        
        # Verzeichnisse erstellen (auch für lokalen Fallback)
        VoiceConfig.DATA_DIR.mkdir(parents=True, exist_ok=True)
        VoiceConfig.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        VoiceConfig.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Lokale Backends (nur wenn nicht remote oder als Fallback)
        self.stt: Optional[STTBackend] = None
        self.tts: Optional[TTSBackend] = None
        
        if not self.use_remote:
            self.stt = self._init_stt(stt_backend)
            self.tts = self._init_tts(tts_backend)
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        self.on_listen_start: Optional[Callable] = None
        self.on_listen_end: Optional[Callable] = None
        self.on_transcript: Optional[Callable[[str], None]] = None
        
        # Status-Log
        if self.use_remote:
            logger.info(f"🎤 HoloVoiceInterface initialisiert - REMOTE MODE ({VoiceConfig.get_remote_url()})")
        else:
            logger.info(f"🎤 HoloVoiceInterface initialisiert - LOCAL MODE - STT: {type(self.stt).__name__ if self.stt else 'None'}, TTS: {type(self.tts).__name__ if self.tts else 'None'}")
    
    def _init_stt(self, backend: str = None) -> Optional[STTBackend]:
        """Initialisiert STT Backend"""
        
        backends = {
            "whisper": WhisperSTT,
            "vosk": VoskSTT,
            "google": GoogleSTT,
        }
        
        if backend:
            if backend in backends:
                stt = backends[backend]()
                if stt.is_available():
                    return stt
                logger.warning(f"[STT] {backend} nicht verfügbar")
        
        # Auto-Auswahl: Vosk > Whisper > Google (Vosk ist leichter für Pi4)
        priority = ["vosk", "whisper", "google"]
        for name in priority:
            try:
                stt = backends[name]()
                if stt.is_available():
                    logger.info(f"[STT] Auto-gewählt: {name}")
                    return stt
            except Exception as e:
                logger.debug(f"[STT] {name} nicht verfügbar: {e}")
        
        logger.warning("[STT] Kein Backend verfügbar!")
        return None
    
    def _init_tts(self, backend: str = None) -> Optional[TTSBackend]:
        """Initialisiert TTS Backend"""
        
        backends = {
            "piper": PiperTTS,
            "edge-tts": EdgeTTS,
            "pyttsx3": Pyttsx3TTS,
        }
        
        if backend:
            if backend in backends:
                tts = backends[backend]()
                if tts.is_available():
                    return tts
                logger.warning(f"[TTS] {backend} nicht verfügbar")
        
        # Auto-Auswahl: Piper > Edge-TTS > pyttsx3
        for name, cls in backends.items():
            try:
                tts = cls()
                if tts.is_available():
                    logger.info(f"[TTS] Auto-gewählt: {name}")
                    return tts
            except Exception as e:
                logger.debug(f"[TTS] {name} nicht verfügbar: {e}")
        
        logger.warning("[TTS] Kein Backend verfügbar!")
        return None
    
    # =========================================================================
    # SPRECHEN (TTS)
    # =========================================================================
    
    def speak(self, text: str, add_wolf_sounds: bool = True) -> bool:
        """
        Spricht Text mit Holo-Stimme.
        
        Args:
            text: Zu sprechender Text
            add_wolf_sounds: Wolf-Sounds basierend auf Emotion hinzufügen
            
        Returns:
            True wenn erfolgreich
        """
        if self.state.is_speaking:
            logger.warning("[TTS] Spricht bereits!")
            return False
        
        self.state.is_speaking = True
        if self.on_speech_start:
            self.on_speech_start()
        
        try:
            # Modulation berechnen
            rate, pitch, volume = self._get_voice_modulation()
            
            # Wolf-Sound hinzufügen
            if add_wolf_sounds:
                text = self._add_wolf_sound(text)
            
            # Text bereinigen für TTS
            text = self._clean_text_for_tts(text)
            
            # === REMOTE MODUS ===
            if self.use_remote and self.remote_client:
                audio_data = self.remote_client.synthesize(text, rate=rate, pitch=pitch)
                if audio_data:
                    self._play_audio_data(audio_data)
                    self.state.last_speech = text
                    return True
                else:
                    logger.error("[TTS] Remote-Synthese fehlgeschlagen")
                    return False
            
            # === LOCAL MODUS ===
            if not self.tts:
                logger.warning("[TTS] Kein Backend verfügbar")
                return False
            
            self.tts.set_voice_params(rate, pitch, volume)
            self.tts.speak(text)
            self.state.last_speech = text
            
            return True
            
        except Exception as e:
            logger.error(f"[TTS] Fehler: {e}")
            return False
            
        finally:
            self.state.is_speaking = False
            if self.on_speech_end:
                self.on_speech_end()
    
    def _play_audio_data(self, audio_data: bytes):
        """Spielt Audio-Daten ab (für Remote-Modus)"""
        # Speichere temporär und spiele ab
        suffix = ".mp3"  # Remote Server liefert meist MP3
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            # Versuche verschiedene Player
            players = [
                ["mpv", "--no-video", temp_path],
                ["ffplay", "-nodisp", "-autoexit", temp_path],
                ["aplay", temp_path],  # Nur für WAV
                ["mplayer", "-really-quiet", temp_path],
            ]
            
            for cmd in players:
                try:
                    subprocess.run(cmd, check=True, capture_output=True, timeout=60)
                    return
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            
            logger.warning("[TTS] Kein Audio-Player gefunden")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def speak_to_file(self, text: str, filepath: str, add_wolf_sounds: bool = False) -> Optional[str]:
        """
        Spricht Text und speichert als Audio-Datei.
        
        Args:
            text: Zu sprechender Text
            filepath: Ziel-Pfad
            add_wolf_sounds: Wolf-Sounds hinzufügen
            
        Returns:
            Pfad zur Audio-Datei oder None bei Fehler
        """
        if not self.tts:
            return None
        
        # Modulation anwenden
        rate, pitch, volume = self._get_voice_modulation()
        self.tts.set_voice_params(rate, pitch, volume)
        
        # Wolf-Sound hinzufügen
        if add_wolf_sounds:
            text = self._add_wolf_sound(text)
        
        # Text bereinigen
        text = self._clean_text_for_tts(text)
        
        return self.tts.speak(text, output_file=filepath)
    
    def speak_streaming(self, text_generator: Generator[str, None, None]) -> Generator[str, None, None]:
        """
        Spricht Text-Stream (für lange Antworten).
        
        Args:
            text_generator: Generator der Text-Chunks liefert
            
        Yields:
            Gesprochene Text-Chunks
        """
        buffer = ""
        sentence_ends = ".!?:;"
        
        for chunk in text_generator:
            buffer += chunk
            yield chunk
            
            # Prüfe ob Satz komplett
            for end_char in sentence_ends:
                if end_char in buffer:
                    idx = buffer.rfind(end_char) + 1
                    sentence = buffer[:idx].strip()
                    buffer = buffer[idx:].strip()
                    
                    if sentence:
                        self.speak(sentence, add_wolf_sounds=False)
                    break
        
        # Rest sprechen
        if buffer.strip():
            self.speak(buffer.strip(), add_wolf_sounds=False)
    
    def _get_voice_modulation(self) -> Tuple[float, float, float]:
        """
        Berechnet Sprachmodulation basierend auf Energy und Emotion.
        
        Returns:
            (rate, pitch, volume)
        """
        rate = 1.0
        pitch = 1.0
        volume = 1.0
        
        # Energy-basiert
        if VoiceConfig.ENABLE_ENERGY_MODULATION and self.energy_system:
            try:
                status = self.energy_system.get_status()
                energy = status.get('total_energy', 0.5)

                # Müde = langsamer, leiser
                if energy < 0.3:
                    rate = 0.85
                    volume = 0.8
                # Energiegeladen = schneller
                elif energy > 0.7:
                    rate = 1.1
                    volume = 1.0

                self.state.energy = energy
            except Exception as e:
                logger.debug(f"Energy modulation failed: {e}")
        
        # Emotions-basiert
        if VoiceConfig.ENABLE_EMOTION_MODULATION and self.emotions:
            try:
                mood = self.emotions.get_dominant_mood()
                emotion = self.emotions.get_dominant_emotion() if hasattr(self.emotions, 'get_dominant_emotion') else "neutral"

                # Fröhlich = höhere Tonlage
                if emotion in ["happy", "excited", "joy"]:
                    pitch = 1.1
                    rate *= 1.05
                # Traurig = tiefere Tonlage
                elif emotion in ["sad", "melancholy"]:
                    pitch = 0.95
                    rate *= 0.95
                # Aufgeregt = schneller
                elif emotion == "excited":
                    rate *= 1.15

                self.state.emotion = emotion
            except Exception as e:
                logger.debug(f"Emotion modulation failed: {e}")
        
        return rate, pitch, volume
    
    def _add_wolf_sound(self, text: str) -> str:
        """Fügt Wolf-Sound basierend auf Emotion hinzu"""
        emotion = self.state.emotion
        
        sounds = VoiceConfig.WOLF_SOUNDS.get(emotion, [])
        if not sounds:
            sounds = VoiceConfig.WOLF_SOUNDS.get("happy", [])
        
        # 30% Chance für Wolf-Sound
        if sounds and hash(text) % 10 < 3:
            sound = sounds[hash(text) % len(sounds)]
            # Am Anfang oder Ende einfügen
            if hash(text) % 2 == 0:
                return f"{sound} {text}"
            else:
                return f"{text} {sound}"
        
        return text
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Bereinigt Text für TTS (entfernt Emojis, Markdown, etc.)"""
        import re
        
        # Entferne Emojis
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        
        # Entferne Markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)       # Italic (aber behalte *Aktionen*)
        text = re.sub(r'`(.+?)`', r'\1', text)         # Code
        text = re.sub(r'#+\s*', '', text)              # Headers
        
        # Ersetze spezielle Zeichen
        text = text.replace('→', 'nach')
        text = text.replace('←', 'von')
        text = text.replace('↔', 'zwischen')
        
        # Entferne URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Normalisiere Whitespace
        text = ' '.join(text.split())
        
        return text
    
    # =========================================================================
    # HÖREN (STT)
    # =========================================================================
    
    def listen(self, timeout: float = 5.0) -> Optional[str]:
        """
        Hört auf Sprache und transkribiert.
        
        Args:
            timeout: Maximale Wartezeit in Sekunden
            
        Returns:
            Transkribierter Text oder None
        """
        if self.state.is_listening:
            logger.warning("[STT] Hört bereits zu!")
            return None
        
        self.state.is_listening = True
        if self.on_listen_start:
            self.on_listen_start()
        
        try:
            # Aufnahme starten (immer lokal auf Pi4)
            audio_data = self._record_audio(timeout)
            if not audio_data:
                return None
            
            # === REMOTE MODUS ===
            if self.use_remote and self.remote_client:
                transcript = self.remote_client.transcribe(audio_data)
                self.state.last_transcript = transcript
                
                if self.on_transcript:
                    self.on_transcript(transcript)
                
                return transcript
            
            # === LOCAL MODUS ===
            if not self.stt:
                logger.warning("[STT] Kein Backend verfügbar")
                return None
            
            transcript = self.stt.transcribe(audio_data)
            self.state.last_transcript = transcript
            
            if self.on_transcript:
                self.on_transcript(transcript)
            
            return transcript
            
        except Exception as e:
            logger.error(f"[STT] Fehler: {e}")
            return None
            
        finally:
            self.state.is_listening = False
            if self.on_listen_end:
                self.on_listen_end()
    
    def listen_continuous(self, callback: Callable[[str], None], stop_event: threading.Event = None):
        """
        Kontinuierliches Zuhören mit Callback.
        
        Args:
            callback: Wird mit jedem Transkript aufgerufen
            stop_event: Event zum Stoppen
        """
        if stop_event is None:
            stop_event = threading.Event()
        
        while not stop_event.is_set():
            transcript = self.listen(timeout=3.0)
            if transcript:
                callback(transcript)
    
    def transcribe_file(self, filepath: str) -> Optional[str]:
        """
        Transkribiert Audio-Datei.
        
        Args:
            filepath: Pfad zur Audio-Datei
            
        Returns:
            Transkribierter Text oder None
        """
        if not self.stt:
            return None
        
        return self.stt.transcribe_file(filepath)
    
    def _record_audio(self, duration: float) -> Optional[bytes]:
        """
        Nimmt Audio auf.
        
        Args:
            duration: Aufnahmedauer in Sekunden
            
        Returns:
            Audio-Daten als Bytes
        """
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=VoiceConfig.CHANNELS,
                rate=VoiceConfig.SAMPLE_RATE,
                input=True,
                frames_per_buffer=VoiceConfig.CHUNK_SIZE
            )
            
            frames = []
            num_chunks = int(VoiceConfig.SAMPLE_RATE / VoiceConfig.CHUNK_SIZE * duration)
            
            for _ in range(num_chunks):
                data = stream.read(VoiceConfig.CHUNK_SIZE)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Als WAV speichern
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wf = wave.open(f.name, 'wb')
                wf.setnchannels(VoiceConfig.CHANNELS)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(VoiceConfig.SAMPLE_RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                with open(f.name, 'rb') as audio_file:
                    return audio_file.read()
                    
        except ImportError:
            logger.error("[STT] pyaudio nicht installiert!")
            return None
        except Exception as e:
            logger.error(f"[STT] Aufnahme-Fehler: {e}")
            return None
    
    # =========================================================================
    # STATUS & INTEGRATION
    # =========================================================================
    
    def get_status(self) -> Dict:
        """Gibt aktuellen Status zurück"""
        if self.use_remote and self.remote_client:
            remote_status = self.remote_client.get_status()
            return {
                "mode": "remote",
                "remote_url": VoiceConfig.get_remote_url(),
                "remote_available": self.remote_client.is_available(),
                "stt_backend": remote_status.get("stt", {}).get("backend", "unknown"),
                "tts_backend": remote_status.get("tts", {}).get("backend", "unknown"),
                "stt_available": True,
                "tts_available": True,
                "is_speaking": self.state.is_speaking,
                "is_listening": self.state.is_listening,
                "last_transcript": self.state.last_transcript,
                "emotion": self.state.emotion,
                "energy": self.state.energy,
            }
        else:
            return {
                "mode": "local",
                "stt_backend": type(self.stt).__name__ if self.stt else None,
                "tts_backend": type(self.tts).__name__ if self.tts else None,
                "stt_available": self.stt is not None,
                "tts_available": self.tts is not None,
                "is_speaking": self.state.is_speaking,
                "is_listening": self.state.is_listening,
                "last_transcript": self.state.last_transcript,
                "emotion": self.state.emotion,
                "energy": self.state.energy,
            }
    
    def get_voices(self) -> List[Dict]:
        """Gibt verfügbare TTS Stimmen zurück"""
        if self.use_remote and self.remote_client:
            return self.remote_client.get_voices()
        return []
    
    def connect(self, energy_system=None, emotions=None):
        """Verbindet mit Holo-Systemen"""
        if energy_system:
            self.energy_system = energy_system
        if emotions:
            self.emotions = emotions


# =============================================================================
# FACTORY & CONVENIENCE
# =============================================================================

def create_voice_interface(
    stt_backend: str = None,
    tts_backend: str = None,
    energy_system=None,
    emotions=None,
    use_remote: bool = None,
    remote_host: str = None,
    remote_port: int = None
) -> HoloVoiceInterface:
    """
    Factory für HoloVoiceInterface.
    
    Args:
        stt_backend: "whisper", "vosk", "google" oder None für Auto
        tts_backend: "piper", "edge-tts", "pyttsx3" oder None für Auto
        energy_system: HoloEnergySystem
        emotions: EmotionalCore
        use_remote: True = Mini-PC nutzen, False = lokal
        remote_host: IP des Voice Servers
        remote_port: Port des Voice Servers
    """
    return HoloVoiceInterface(
        stt_backend=stt_backend,
        tts_backend=tts_backend,
        energy_system=energy_system,
        emotions=emotions,
        use_remote=use_remote,
        remote_host=remote_host,
        remote_port=remote_port
    )


def check_voice_dependencies() -> Dict[str, bool]:
    """Prüft welche Voice-Dependencies verfügbar sind"""
    deps = {}
    
    # STT
    try:
        import whisper
        deps["whisper"] = True
    except ImportError:
        try:
            from faster_whisper import WhisperModel
            deps["faster_whisper"] = True
        except ImportError:
            deps["whisper"] = False
    
    try:
        from vosk import Model
        deps["vosk"] = True
    except ImportError:
        deps["vosk"] = False
    
    try:
        import speech_recognition
        deps["speech_recognition"] = True
    except ImportError:
        deps["speech_recognition"] = False
    
    # TTS
    try:
        from piper import PiperVoice
        deps["piper"] = True
    except ImportError:
        deps["piper"] = False
    
    try:
        import edge_tts
        deps["edge_tts"] = True
    except ImportError:
        deps["edge_tts"] = False
    
    try:
        import pyttsx3
        deps["pyttsx3"] = True
    except ImportError:
        deps["pyttsx3"] = False
    
    # Audio
    try:
        import pyaudio
        deps["pyaudio"] = True
    except ImportError:
        deps["pyaudio"] = False
    
    return deps


def download_voice_models():
    """Hilfsfunktion zum Herunterladen der Voice-Models"""
    print("=" * 60)
    print("HOLO VOICE - Model Download")
    print("=" * 60)
    
    # Piper Voice
    print("\n📥 Piper Voice (Deutsch):")
    print("  1. Gehe zu: https://huggingface.co/rhasspy/piper-voices")
    print("  2. Suche: de_DE-thorsten-medium")
    print("  3. Lade .onnx und .onnx.json herunter")
    print(f"  4. Speichere in: {VoiceConfig.MODELS_DIR}")
    
    # Vosk Model
    print("\n📥 Vosk Model (Deutsch):")
    print("  1. Gehe zu: https://alphacephei.com/vosk/models")
    print("  2. Lade 'vosk-model-small-de-0.15' herunter")
    print("  3. Entpacke nach: {VoiceConfig.MODELS_DIR}")
    
    # Whisper
    print("\n📥 Whisper:")
    print("  pip install openai-whisper")
    print("  # oder für schnellere Version:")
    print("  pip install faster-whisper")
    print("  # Models werden automatisch heruntergeladen")
    
    print("\n" + "=" * 60)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Holo Voice Interface Test")
    parser.add_argument('--local', action='store_true', help='Lokalen Modus erzwingen')
    parser.add_argument('--remote', action='store_true', help='Remote Modus erzwingen')
    parser.add_argument('--host', default=None, help='Remote Server Host')
    parser.add_argument('--port', type=int, default=None, help='Remote Server Port')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("🎤 HOLO VOICE INTERFACE - TEST")
    print("=" * 60)
    
    # Modus bestimmen
    use_remote = None
    if args.local:
        use_remote = False
    elif args.remote:
        use_remote = True
    
    # Dependencies prüfen
    print("\n📦 Lokale Dependencies:")
    deps = check_voice_dependencies()
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {name}")
    
    # Remote prüfen
    print(f"\n🌐 Remote Server ({VoiceConfig.get_remote_url()}):")
    test_client = RemoteVoiceClient(
        host=args.host or VoiceConfig.REMOTE_HOST,
        port=args.port or VoiceConfig.REMOTE_PORT
    )
    if test_client.is_available():
        print("  ✅ Erreichbar")
        remote_status = test_client.get_status()
        print(f"  STT: {remote_status.get('stt', {}).get('backend', '?')} ({remote_status.get('stt', {}).get('model', '?')})")
        print(f"  TTS: {remote_status.get('tts', {}).get('backend', '?')} ({remote_status.get('tts', {}).get('voice', '?')})")
    else:
        print("  ❌ Nicht erreichbar")
    
    # Voice Interface erstellen
    print("\n🐺 Erstelle Voice Interface...")
    voice = create_voice_interface(
        use_remote=use_remote,
        remote_host=args.host,
        remote_port=args.port
    )
    
    status = voice.get_status()
    print(f"\nModus: {status.get('mode', 'unknown').upper()}")
    print(f"STT: {status.get('stt_backend', 'N/A')}")
    print(f"TTS: {status.get('tts_backend', 'N/A')}")
    
    # Test TTS
    can_speak = (voice.use_remote and voice.remote_client) or voice.tts
    if can_speak:
        if input("\n🔊 TTS testen? (j/n): ").lower() == 'j':
            print("Spreche...")
            voice.speak("Hallo! Ich bin Holo, deine Wolfs-Freundin!")
    else:
        print("\n⚠️ TTS nicht verfügbar")
    
    # Test STT
    can_listen = (voice.use_remote and voice.remote_client) or voice.stt
    if can_listen:
        if input("\n🎤 STT testen? (j/n): ").lower() == 'j':
            print("Sprich jetzt (5 Sekunden)...")
            transcript = voice.listen(timeout=5.0)
            print(f"Verstanden: {transcript}")
    else:
        print("\n⚠️ STT nicht verfügbar")
    
    print("\n✅ Test abgeschlossen!")

