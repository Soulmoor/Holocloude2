# HOLOCLOUDE - Vollständige Projektdokumentation

> **Version**: 15.0 (Intelligent Router Edition)
> **Stand**: Januar 2026
> **Autor**: Automatisch generierte Dokumentation
> **Codeumfang**: ~212.000 Zeilen in 86 Python-Modulen

---

## Inhaltsverzeichnis

1. [Projektübersicht](#1-projektübersicht)
2. [Architektur-Überblick](#2-architektur-überblick)
3. [Verzeichnisstruktur](#3-verzeichnisstruktur)
4. [Konfigurationssystem](#4-konfigurationssystem)
5. [Kernmodule (Foundation)](#5-kernmodule-foundation)
6. [Kognitive Systeme](#6-kognitive-systeme)
7. [Wahrnehmungssysteme](#7-wahrnehmungssysteme)
8. [Kommunikation & NLP](#8-kommunikation--nlp)
9. [Autonomes Verhalten](#9-autonomes-verhalten)
10. [Medien & Wissen](#10-medien--wissen)
11. [Datenpersistenz](#11-datenpersistenz)
12. [Integration & Schnittstellen](#12-integration--schnittstellen)
13. [Datenfluss & Verarbeitung](#13-datenfluss--verarbeitung)
14. [Einstiegspunkte](#14-einstiegspunkte)
15. [Test-Framework](#15-test-framework)
16. [Abhängigkeiten](#16-abhängigkeiten)
17. [Modulreferenz (Komplett)](#17-modulreferenz-komplett)

---

## 1. Projektübersicht

### Was ist Holocloude?

**Holocloude** ist ein hochentwickeltes, modulares Python-basiertes KI-System, das eine virtuelle Persona namens "Holo" implementiert - einen Kemonomimi-Charakter (wolfsähnlich) mit komplexen kognitiven und emotionalen Fähigkeiten.

### Kernfähigkeiten

| Bereich | Beschreibung |
|---------|--------------|
| **Kognition** | Bewusstsein, Reasoning, Lernen, Meta-Kognition |
| **Emotionen** | 12 Emotionen × 6 Intensitätsstufen (minimal, leicht, mittel, stark, sehr_stark, extrem), komplexe Stimmungsdynamik |
| **Wahrnehmung** | Vision, Audio, Text, Video-Analyse |
| **Kommunikation** | Dialog-Engine, LLM-Integration, Sprach-Interface |
| **Autonomie** | Innenleben, autonomes Denken, Impulsgenerierung |
| **Integration** | Smart Home, Gerätekontrolle, Web-Integration |

### Besondere Merkmale

- **Graceful Degradation**: Das System funktioniert auch bei fehlenden Modulen weiter
- **Multi-Modal**: Verarbeitung von Bild, Ton, Text und Video
- **Bewusstseinssimulation**: Qualia, phänomenales Bewusstsein, Gedankenstrom
- **Energiesystem**: 6-dimensionales Energiemodell beeinflusst Verhalten
- **Träume**: Schlafzyklen mit Gedächtniskonsolidierung

---

## 2. Architektur-Überblick

### Schichtenmodell

```
┌─────────────────────────────────────────────────────────────┐
│                  SCHICHT 7: ORCHESTRATOR                     │
│                    holo_brain.py (HoloPersona)               │
├─────────────────────────────────────────────────────────────┤
│                  SCHICHT 6: INTEGRATION                      │
│    holo_integration_layer.py | holo_wiring.py |              │
│                  holo_module_loader.py                       │
├─────────────────────────────────────────────────────────────┤
│                   SCHICHT 5: FEATURES                        │
│  Vision(3) | Audio(3) | Media(5) | NLP(4) | Self(2) | ...   │
├─────────────────────────────────────────────────────────────┤
│                   SCHICHT 4: INTELLIGENZ                     │
│  holo_smart_understanding | holo_nlp_algorithms |            │
│              holo_intelligent_router                         │
├─────────────────────────────────────────────────────────────┤
│                 SCHICHT 3: KOGNITIVE SYSTEME                 │
│  holo_consciousness | holo_inner_life | holo_personality |   │
│              holo_energy_system | holo_cognitive_modules     │
├─────────────────────────────────────────────────────────────┤
│                SCHICHT 2: PERSISTENZ & LLM                   │
│       holo_database_system (17 DBs) | smart_llm_system       │
├─────────────────────────────────────────────────────────────┤
│                   SCHICHT 1: KERN (Basis)                    │
│  holo_core_types | holo_robust_imports | holo_config |       │
│           holo_error_handling | holo_error_tracker           │
└─────────────────────────────────────────────────────────────┘
```

### Kernprinzipien

1. **Modularität**: Jede Funktion ist in eigenständige Module gekapselt
2. **Fallback-System**: Robuste Imports mit Mock-Implementierungen
3. **Intelligentes Routing**: Zentrale Entscheidungslogik für Antwortgenerierung
4. **Asynchrone Verarbeitung**: Hintergrundaufgaben und autonomes Denken

---

## 3. Verzeichnisstruktur

```
/home/user/Holocloude/
│
├── holo_brain.py              # 🧠 Haupt-Orchestrator (~27.600 Zeilen)
├── holo_intelligent_router.py # 🔀 Zentrales Routing (~8.900 Zeilen)
├── holo_database_system.py    # 💾 17 SQLite-Datenbanken (~7.700 Zeilen)
├── holo_cognitive_modules.py  # 🧩 Kognitive Module (~10.200 Zeilen)
├── holo_inner_life.py         # 💭 Innenleben (~10.700 Zeilen)
├── ... (81 weitere Module)
│
├── config.json                # ⚙️ Zentrale Konfiguration
├── holo_config.py             # 📝 Konfigurationslader
├── holo_comfyui_config.json   # 🎨 ComfyUI-Konfiguration
├── requirements.txt           # 📦 Python-Abhängigkeiten
│
├── data/                      # 📂 Datenpersistenz (wird bei Bedarf erstellt)
│   ├── conversation_context.json
│   ├── trust_network.json
│   └── ...
│
├── state/                     # 🔄 Laufzeit-Zustand (wird bei Bedarf erstellt)
│   └── holo_to_pi.json        # Pi-Kommunikation
│
├── logs/                      # 📋 Runtime-Logs (wird bei Bedarf erstellt)
│
└── skills/                    # 🎯 Erweiterbare Skills (optional)
    └── comfyui_skill.py       # ComfyUI-Integration

# HINWEIS: Test-Suite muss noch implementiert werden
```

---

## 4. Konfigurationssystem

### config.json - Hauptkonfiguration

Die zentrale Konfigurationsdatei enthält alle systemweiten Einstellungen:

```json
{
  "network": {
    "ollama": {
      "host": "192.168.178.42",
      "local_host": "localhost",
      "remote_host": "192.168.178.42",
      "port": 11434
    },
    "mqtt": {
      "broker_ip": "192.168.178.99",
      "broker_port": 1883,
      "username": "...",
      "password": "..."
    },
    "home_assistant": {
      "api_url": "http://192.168.178.99:8123/api",
      "token": "..."
    },
    "nas": {
      "ip": "192.168.178.40",
      "mac": "...",
      "ssh_user": "...",
      "ssh_port": 22
    },
    "comfyui": {
      "host": "localhost",
      "port": 8188
    }
  },
  "devices": {
    "tracked_devices": { ... },
    "wake_detection_devices": [ ... ],
    "media_sources": [ ... ],
    "rooms": { ... }
  },
  "llm": {
    "local_model": "llama3.2",
    "remote_model": "deepseek-r1:14b",
    "fallback_model": "llama3.2",
    "embedding_model": "nomic-embed-text",
    "max_context_tokens": 8192,
    "temperature": 0.7,
    "timeout_seconds": 120
  },
  "behavior": {
    "bedtime_hour": 23,
    "wakeup_hour": 7,
    "energy_saving_start": 0,
    "energy_saving_end": 6
  },
  "storage": {
    "data_dir": "./data",
    "max_storage_mb": 1000,
    "ram_cache_mb": 256
  },
  "logging": {
    "level": "INFO",
    "file": "./logs/holo.log",
    "rotation": "daily"
  },
  "features": {
    "autonomous_thinking": true,
    "dream_simulation": true,
    "news_monitoring": true,
    "creative_mode": true
  }
}
```

### holo_config.py - Konfigurationslader

```python
# Funktionen
get_config()       # Lädt/cached die Konfiguration
load_config()      # Lädt Konfiguration aus Datei
reload_config()    # Lädt Konfiguration neu
validate_config()  # Validiert Konfigurationswerte

# ConfigDict - Verschachtelter Attributzugriff
config = get_config()
ollama_host = config.network.ollama.host  # "192.168.178.42"

# Umgebungsvariablen-Überschreibung
# HOLO_OLLAMA_HOST=localhost überschreibt config.network.ollama.host
```

---

## 5. Kernmodule (Foundation)

### 5.1 holo_core_types.py (~1.500 Zeilen)

**Zweck**: Zentrale Typdefinitionen für das gesamte System

```python
# Enumerationen
class DriveType(Enum):
    CURIOSITY = "curiosity"
    CONNECTION = "connection"
    CREATIVITY = "creativity"
    GROWTH = "growth"

class NeedType(Enum):
    SOCIAL = "social"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"

class GoalType(Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

# Skalen (Standard: 0.0 - 1.0)
class MoodScale:
    MIN = 0.0
    NEUTRAL = 0.5
    MAX = 1.0

class EnergyScale:
    DEPLETED = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    FULL = 1.0

# Dataclasses
@dataclass
class EmotionalState:
    primary: str
    intensity: float
    secondary: Optional[str]
    duration: float

@dataclass
class Goal:
    type: GoalType
    description: str
    priority: float
    progress: float

# Validierungsfunktionen
validate_mood(value: float) -> float      # Clamp auf 0.0-1.0
validate_energy(value: float) -> float    # Clamp auf 0.0-1.0
```

### 5.2 holo_robust_imports.py (~1.500 Zeilen)

**Zweck**: Sichere Imports mit Fallback-Implementierungen

```python
# Das System stürzt nicht ab, wenn Module fehlen
# Stattdessen werden Mock-Klassen verwendet

class MockConsciousness:
    """Fallback wenn holo_consciousness.py nicht verfügbar"""
    def get_awareness_level(self) -> float:
        return 0.5  # Neutraler Standardwert

class MockEmotionEngine:
    """Fallback wenn Emotionssystem nicht verfügbar"""
    def get_current_emotion(self) -> str:
        return "neutral"

# Sicherer Import-Wrapper
def safe_import(module_name: str, fallback_class):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return fallback_class
```

### 5.3 holo_error_handling.py (~450 Zeilen)

**Zweck**: Fehlerbehandlung und sichere Ausführung

```python
# Decorator für sichere Ausführung
@safe_execute
def risky_function():
    # Fehler werden abgefangen und geloggt
    pass

# Context Manager für Fehler-Tracking
with ErrorContext("processing_message"):
    result = process(message)

# Sichere Wertextraktion
value = safe_dict_get(data, "key.nested.value", default=0)
number = safe_float("3.14", default=0.0)
```

### 5.4 holo_module_loader.py (~750 Zeilen)

**Zweck**: Dynamisches Laden und Verwalten von Modulen

```python
class HoloBootManager:
    """Verwaltet den 8-Phasen-Bootvorgang"""

    BOOT_PHASES = [
        "core",           # Phase 1: Kernsysteme
        "persistence",    # Phase 2: Datenbanken
        "cognitive",      # Phase 3: Kognition
        "perception",     # Phase 4: Wahrnehmung
        "communication",  # Phase 5: Kommunikation
        "autonomy",       # Phase 6: Autonomie
        "integration",    # Phase 7: Integration
        "features"        # Phase 8: Features
    ]

    async def boot(self):
        """Startet alle Module in korrekter Reihenfolge"""
        for phase in self.BOOT_PHASES:
            await self.load_phase(phase)

class RobustModuleLoader:
    """Lädt Module mit Health-Monitoring"""

    def load(self, module_name: str):
        module = self._safe_import(module_name)
        self._register_health_check(module)
        return module

    def check_health(self) -> Dict[str, bool]:
        """Gibt Gesundheitsstatus aller Module zurück"""
        return {name: mod.is_healthy() for name, mod in self.modules.items()}
```

---

## 6. Kognitive Systeme

### 6.1 holo_consciousness.py (~4.500 Zeilen)

**Zweck**: Bewusstseins-Simulation mit philosophischer Tiefe

```python
class ConsciousnessEngine:
    """Hauptklasse für Bewusstseinssimulation"""

    def __init__(self):
        self.qualia = QualiaSimulator()           # Subjektive Erfahrungen
        self.phenomenal = PhenomenalConsciousness()  # Phänomenales Bewusstsein
        self.access = AccessConsciousness()        # Zugangs-Bewusstsein
        self.reflection = SelfReflection()         # Introspektion
        self.thought_stream = StreamOfThought()    # Gedankenstrom

    def get_awareness_level(self) -> float:
        """Aktueller Bewusstseinsgrad (0.0-1.0)"""
        return self._calculate_awareness()

    def simulate_dream(self) -> DreamSummary:
        """Generiert einen Traum basierend auf Erinnerungen"""
        memories = self._gather_recent_memories()
        return self._dream_from_memories(memories)

class QualiaSimulator:
    """Simuliert subjektive Erfahrungen (Qualia)"""

    def experience_color(self, rgb: Tuple[int, int, int]) -> str:
        """Wie fühlt sich eine Farbe an?"""
        warmth = self._calculate_color_warmth(rgb)
        return f"Eine {warmth} Empfindung, wie {self._color_metaphor(rgb)}"
```

### 6.2 holo_inner_life.py (~8.000 Zeilen)

**Zweck**: Vollständige Simulation eines Innenlebens

```python
class InnerLife:
    """Das komplette innere Leben von Holo"""

    def __init__(self):
        self.thoughts = ThoughtStream()      # Gedankenstrom
        self.daydreams = DaydreamEngine()    # Tagträume
        self.emotions = EmotionalLife()      # Emotionales Leben
        self.dreams = DreamEngine()          # Nachtträume
        self.meditation = MeditationState()  # Meditation/Reflexion

    async def background_process(self):
        """Kontinuierlicher Hintergrundprozess"""
        while True:
            await self._process_thoughts()
            await self._check_daydream_trigger()
            await self._update_emotional_state()
            await asyncio.sleep(0.1)

    def get_current_thought(self) -> str:
        """Was denkt Holo gerade?"""
        return self.thoughts.current

class DreamEngine:
    """Generiert und verarbeitet Träume"""

    def generate_dream(self, memories: List[Memory]) -> Dream:
        """Erstellt einen Traum aus Erinnerungen"""
        themes = self._extract_themes(memories)
        narrative = self._weave_narrative(themes)
        return Dream(
            content=narrative,
            emotions=self._dream_emotions(themes),
            symbols=self._extract_symbols(narrative)
        )

    def consolidate_memories(self, dream: Dream):
        """Konsolidiert Erinnerungen während des Träumens"""
        for symbol in dream.symbols:
            self._strengthen_related_memories(symbol)
```

### 6.3 holo_energy_system.py (~1.900 Zeilen)

**Zweck**: 6-dimensionales Energiemodell

```python
@dataclass
class EnergyState:
    mental: float      # Denk-Energie (0.0-1.0)
    physical: float    # Bewegungs-Energie
    emotional: float   # Gefühls-Energie
    social: float      # Interaktions-Energie
    creative: float    # Kreativitäts-Energie
    spiritual: float   # Bedeutungs-Energie

class EnergySystem:
    """Verwaltet das 6D-Energiemodell"""

    def __init__(self):
        self.state = EnergyState(
            mental=0.8,
            physical=0.7,
            emotional=0.75,
            social=0.6,
            creative=0.85,
            spiritual=0.7
        )

    def consume_energy(self, activity_type: str, amount: float):
        """Verbraucht Energie basierend auf Aktivität"""
        mapping = {
            "thinking": "mental",
            "talking": "social",
            "creating": "creative",
            # ...
        }
        dimension = mapping.get(activity_type, "mental")
        setattr(self.state, dimension,
                max(0, getattr(self.state, dimension) - amount))

    def regenerate(self, duration_hours: float):
        """Regeneriert Energie über Zeit"""
        for dim in ["mental", "physical", "emotional",
                    "social", "creative", "spiritual"]:
            current = getattr(self.state, dim)
            rate = self._get_regen_rate(dim)
            new_value = min(1.0, current + rate * duration_hours)
            setattr(self.state, dim, new_value)

    def get_overall_energy(self) -> float:
        """Durchschnittliche Energie aller Dimensionen"""
        values = [self.state.mental, self.state.physical,
                  self.state.emotional, self.state.social,
                  self.state.creative, self.state.spiritual]
        return sum(values) / len(values)
```

### 6.4 holo_cognitive_modules.py (~9.000 Zeilen)

**Zweck**: Erweiterte kognitive Fähigkeiten

```python
class LoyaltySafetyCore:
    """Loyalitätssystem (Eid an Kira)"""

    def __init__(self):
        self.oath = "Ich diene und beschütze Kira"
        self.trust_levels = {}

    def check_safety(self, action: str) -> bool:
        """Prüft ob Aktion sicher/erlaubt ist"""
        return not self._violates_oath(action)

class ReasoningEngine:
    """Logisches Denken und hypothetisches Reasoning"""

    def reason_about(self, premise: str, question: str) -> str:
        """Schließt logisch von Prämisse auf Antwort"""
        facts = self._extract_facts(premise)
        inferences = self._apply_logic(facts)
        return self._answer_from_inferences(inferences, question)

    def hypothetical_reasoning(self, scenario: str) -> List[str]:
        """Was-wäre-wenn Szenarien durchspielen"""
        possibilities = self._generate_possibilities(scenario)
        return [self._evaluate_possibility(p) for p in possibilities]

class PerceptionEngine:
    """Mustererkennung und Anomalie-Detektion"""

    def detect_patterns(self, data: List[Any]) -> List[Pattern]:
        """Erkennt Muster in Daten"""
        return self._pattern_mining(data)

    def detect_anomalies(self, data: List[Any]) -> List[Anomaly]:
        """Erkennt Abweichungen vom Normalzustand"""
        baseline = self._calculate_baseline(data)
        return self._find_deviations(data, baseline)

class AdvancedLearningEngine:
    """Konzeptlernen und Meta-Lernen"""

    def learn_concept(self, examples: List[str], name: str):
        """Lernt ein neues Konzept aus Beispielen"""
        features = self._extract_common_features(examples)
        self.concepts[name] = Concept(
            name=name,
            features=features,
            examples=examples
        )

    def meta_learn(self, task_type: str):
        """Lernt, wie man besser lernt"""
        past_successes = self._analyze_learning_history(task_type)
        self._update_learning_strategy(past_successes)
```

### 6.5 holo_personality.py (~3.200 Zeilen)

**Zweck**: Persönlichkeitssystem mit Big-Five-Modell

```python
@dataclass
class PersonalityTraits:
    """Big Five + Holo-spezifische Traits"""
    openness: float = 0.85          # Offenheit für Erfahrungen
    conscientiousness: float = 0.7   # Gewissenhaftigkeit
    extraversion: float = 0.65       # Extraversion
    agreeableness: float = 0.8       # Verträglichkeit
    neuroticism: float = 0.35        # Neurotizismus (niedrig = stabil)

    # Holo-spezifisch
    playfulness: float = 0.9         # Verspieltheit
    loyalty: float = 0.95            # Loyalität
    curiosity: float = 0.88          # Neugier

class PersonalityEngine:
    """Verwaltet Holos Persönlichkeit"""

    def __init__(self):
        self.traits = PersonalityTraits()
        self.expression_patterns = {}

    def modulate_response(self, response: str, emotion: str) -> str:
        """Passt Antwort an Persönlichkeit an"""
        if self.traits.playfulness > 0.7 and emotion == "happy":
            response = self._add_playful_elements(response)
        if self.traits.neuroticism < 0.3:
            response = self._add_confidence(response)
        return response

    def evolve(self, experience: Experience):
        """Persönlichkeit entwickelt sich durch Erfahrung"""
        impact = self._calculate_impact(experience)
        for trait, change in impact.items():
            current = getattr(self.traits, trait)
            # Kleine, graduelle Änderungen
            new_value = current + change * 0.01
            setattr(self.traits, trait, max(0, min(1, new_value)))
```

---

## 7. Wahrnehmungssysteme

### 7.1 Vision-Module

#### holo_vision_advanced.py (~1.350 Zeilen)
```python
class AdvancedVision:
    """Fortgeschrittene Bildverarbeitung"""

    def analyze_image(self, image_path: str) -> ImageAnalysis:
        """Analysiert ein Bild umfassend"""
        return ImageAnalysis(
            objects=self._detect_objects(image_path),
            scene=self._classify_scene(image_path),
            colors=self._extract_colors(image_path),
            mood=self._detect_mood(image_path)
        )
```

#### holo_vision_enhanced.py (~1.300 Zeilen)
```python
class EnhancedVision:
    """Objekterkennung und Szenenverstehen"""

    def detect_objects(self, image) -> List[DetectedObject]:
        """Erkennt Objekte im Bild"""
        pass

    def understand_scene(self, image) -> SceneDescription:
        """Beschreibt die Szene"""
        pass
```

#### holo_vision_extended.py (~1.300 Zeilen)
```python
class ExtendedVision:
    """Gesichtserkennung und Aktivitätserkennung"""

    def recognize_face(self, image) -> Optional[Person]:
        """Erkennt bekannte Personen"""
        pass

    def recognize_activity(self, video) -> Activity:
        """Erkennt Aktivitäten in Videos"""
        pass
```

### 7.2 Audio-Module

#### holo_audio.py (~650 Zeilen)
```python
class AudioProcessor:
    """Basis-Audioverarbeitung"""

    def process_audio(self, audio_path: str) -> AudioFeatures:
        """Extrahiert Audio-Features"""
        return AudioFeatures(
            duration=self._get_duration(audio_path),
            loudness=self._measure_loudness(audio_path),
            frequency_spectrum=self._analyze_frequencies(audio_path)
        )
```

#### holo_audio_enhanced.py (~1.400 Zeilen)
```python
class EnhancedAudio:
    """Erweiterte Audio-Analyse"""

    def analyze_speech(self, audio) -> SpeechAnalysis:
        """Analysiert Sprache"""
        return SpeechAnalysis(
            transcription=self._transcribe(audio),
            emotion=self._detect_emotion(audio),
            speaker=self._identify_speaker(audio)
        )

    def analyze_music(self, audio) -> MusicAnalysis:
        """Analysiert Musik"""
        return MusicAnalysis(
            tempo=self._detect_tempo(audio),
            key=self._detect_key(audio),
            mood=self._detect_mood(audio)
        )
```

### 7.3 Sprach-Module

#### holo_speech_engine.py (~2.000 Zeilen)
```python
class SpeechEngine:
    """Text-to-Speech und Prosodie"""

    def speak(self, text: str, emotion: str = "neutral"):
        """Spricht Text mit emotionaler Färbung"""
        prosody = self._calculate_prosody(emotion)
        audio = self._synthesize(text, prosody)
        self._play(audio)

    def _calculate_prosody(self, emotion: str) -> Prosody:
        """Berechnet Sprechmelodie basierend auf Emotion"""
        return Prosody(
            pitch=self.emotion_pitch_map[emotion],
            rate=self.emotion_rate_map[emotion],
            volume=self.emotion_volume_map[emotion]
        )
```

#### holo_voice_interface.py (~1.300 Zeilen)
```python
class VoiceInterface:
    """Sprach-Ein/Ausgabe-Schnittstelle"""

    def listen(self) -> str:
        """Hört auf Spracheingabe"""
        audio = self._record_audio()
        text = self._speech_to_text(audio)
        return text

    def respond(self, text: str):
        """Antwortet per Sprache"""
        self.speech_engine.speak(text, self.current_emotion)
```

---

## 8. Kommunikation & NLP

### 8.1 holo_smart_understanding.py (~5.000 Zeilen)

**Zweck**: Intent-Erkennung und Textverstehen

```python
class SmartUnderstanding:
    """Haupt-Klasse für Textverstehen"""

    def __init__(self):
        self.normalizer = TextNormalizer()
        self.subject_verb = SubjectVerbAnalyzer()
        self.wellbeing = WellbeingInquiryDetector()
        self.emotion = UserEmotionDetector()
        self.negation = NegationHandler()
        self.question = QuestionTypeClassifier()
        self.implicit = ImplicitIntentDetector()
        self.context = ContextAwareDetector()

    def understand(self, text: str) -> Understanding:
        """Versteht eine Nachricht umfassend"""
        normalized = self.normalizer.normalize(text)

        return Understanding(
            intent=self._detect_intent(normalized),
            entities=self._extract_entities(normalized),
            emotion=self.emotion.detect(normalized),
            question_type=self.question.classify(normalized),
            implicit_intents=self.implicit.detect(normalized),
            confidence=self._calculate_confidence()
        )

class TextNormalizer:
    """Textbereinigung und Standardisierung"""

    def normalize(self, text: str) -> str:
        """Normalisiert Text für Verarbeitung"""
        text = self._fix_typos(text)
        text = self._expand_contractions(text)
        text = self._standardize_punctuation(text)
        return text

    def _fix_typos(self, text: str) -> str:
        """Korrigiert häufige Tippfehler"""
        # Fuzzy Matching für Korrekturvorschläge
        pass

class QuestionTypeClassifier:
    """Klassifiziert Fragetypen"""

    TYPES = [
        "yes_no",       # Ja/Nein-Frage
        "wh_question",  # W-Frage (Was, Wer, Wo, etc.)
        "choice",       # Auswahlfrage
        "clarification", # Klärungsfrage
        "rhetorical",   # Rhetorische Frage
        "embedded"      # Eingebettete Frage
    ]

    def classify(self, text: str) -> str:
        """Bestimmt den Fragetyp"""
        pass
```

### 8.2 holo_nlp_algorithms.py (~3.700 Zeilen)

**Zweck**: Fortgeschrittene NLP-Algorithmen

```python
class AdvancedFuzzyMatching:
    """Verschiedene Fuzzy-Matching-Algorithmen"""

    def jaro_winkler(self, s1: str, s2: str) -> float:
        """Jaro-Winkler-Ähnlichkeit"""
        pass

    def damerau_levenshtein(self, s1: str, s2: str) -> int:
        """Damerau-Levenshtein-Distanz"""
        pass

    def phonetic_match(self, s1: str, s2: str) -> bool:
        """Phonetischer Vergleich"""
        pass

class SentimentAnalyzer:
    """Stimmungsanalyse"""

    def analyze(self, text: str) -> SentimentResult:
        """Analysiert Stimmung eines Textes"""
        ngram_score = self._ngram_sentiment(text)
        negation_adjusted = self._handle_negation(text, ngram_score)
        sarcasm_check = self._detect_sarcasm(text)

        return SentimentResult(
            polarity=negation_adjusted,
            confidence=self._confidence,
            is_sarcastic=sarcasm_check
        )

class EntityExtractor:
    """Named Entity Recognition (Light)"""

    def extract(self, text: str) -> List[Entity]:
        """Extrahiert Entitäten aus Text"""
        entities = []
        entities.extend(self._extract_persons(text))
        entities.extend(self._extract_locations(text))
        entities.extend(self._extract_dates(text))
        entities.extend(self._extract_numbers(text))
        return entities

class TextSummarizer:
    """Textzusammenfassung"""

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Erstellt Zusammenfassung"""
        sentences = self._split_sentences(text)
        scores = self._score_sentences(sentences)
        top_sentences = self._select_top(sentences, scores, max_sentences)
        return " ".join(top_sentences)

class MarkovTextGenerator:
    """Markov-Ketten-Textgenerierung"""

    def train(self, corpus: str):
        """Trainiert das Modell auf einem Corpus"""
        tokens = self._tokenize(corpus)
        self._build_chain(tokens)

    def generate(self, seed: str, length: int) -> str:
        """Generiert Text basierend auf Seed"""
        pass
```

### 8.3 holo_message_analyzer.py (~1.100 Zeilen)

**Zweck**: Nachrichtenanalyse und Antwortkoordination

```python
class HoloMessageAnalyzer:
    """Umfassende Nachrichtenanalyse"""

    def analyze(self, message: str) -> MessageAnalysis:
        """Analysiert eine eingehende Nachricht"""
        return MessageAnalysis(
            content=message,
            intents=self._detect_intents(message),
            entities=self._extract_entities(message),
            sentiment=self._analyze_sentiment(message),
            urgency=self._assess_urgency(message),
            context_references=self._find_context_refs(message)
        )

class ResponseOrchestrator:
    """Koordiniert Antwortgenerierung"""

    def orchestrate(self, analysis: MessageAnalysis) -> Response:
        """Orchestriert die Antwort aus verschiedenen Teilen"""
        parts = []

        for intent in analysis.intents:
            handler = self._get_handler(intent)
            part = handler.generate(intent)
            parts.append(ResponsePart(
                content=part,
                priority=self._get_priority(intent),
                source=handler.name
            ))

        return self._compose_response(parts)

class MultiIntentDetector:
    """Erkennt mehrere Absichten in einer Nachricht"""

    def detect(self, text: str) -> List[Intent]:
        """Erkennt alle Absichten"""
        # "Wie geht's dir und was gibt's Neues?"
        # -> [WELLBEING_INQUIRY, NEWS_REQUEST]
        pass
```

### 8.4 holo_dialogue_engine.py (~1.500 Zeilen)

**Zweck**: Dialogmanagement und Gesprächsfluss

```python
class DialogueEngine:
    """Verwaltet Dialogzustände und -flüsse"""

    def __init__(self):
        self.state = DialogueState.IDLE
        self.context = ConversationContext()
        self.turn_manager = TurnManager()

    def process_turn(self, user_input: str) -> DialogueTurn:
        """Verarbeitet einen Gesprächszug"""
        self.turn_manager.start_turn()

        # Kontext aktualisieren
        self.context.add_user_input(user_input)

        # Antwort generieren
        response = self._generate_response(user_input)

        # Turn abschließen
        self.turn_manager.end_turn()
        self.context.add_system_response(response)

        return DialogueTurn(
            user_input=user_input,
            response=response,
            state=self.state
        )

    def switch_topic(self, new_topic: str):
        """Wechselt das Gesprächsthema"""
        self.context.save_current_topic()
        self.context.set_topic(new_topic)
```

---

## 9. Autonomes Verhalten

### 9.1 holo_impulse_system.py (~1.250 Zeilen)

**Zweck**: Authentische Impulsgenerierung

```python
class ImpulseSystem:
    """Generiert authentische Verhaltensimpulse"""

    def __init__(self):
        self.impulse_queue = PriorityQueue()
        self.suppression_threshold = 0.3

    def generate_impulses(self) -> List[Impulse]:
        """Generiert Impulse basierend auf aktuellem Zustand"""
        impulses = []

        # Neugier-basierte Impulse
        if self.curiosity_level > 0.7:
            impulses.append(Impulse(
                type="exploration",
                content="Ich möchte mehr über X erfahren",
                strength=self.curiosity_level
            ))

        # Soziale Impulse
        if self.social_need > 0.6:
            impulses.append(Impulse(
                type="social",
                content="Ich würde gerne mit jemandem reden",
                strength=self.social_need
            ))

        return self._rank_and_filter(impulses)

    def should_express(self, impulse: Impulse) -> bool:
        """Entscheidet ob Impuls ausgedrückt werden soll"""
        # Impulse unter der Schwelle werden unterdrückt
        if impulse.strength < self.suppression_threshold:
            return False
        # Soziale Angemessenheit prüfen
        if not self._is_appropriate(impulse):
            return False
        return True

@dataclass
class Impulse:
    type: str           # "exploration", "social", "creative", etc.
    content: str        # Beschreibung des Impulses
    strength: float     # 0.0-1.0
    timestamp: datetime
    source: str         # Was hat den Impuls ausgelöst?
```

### 9.2 holo_autonomous_thinking.py (~2.050 Zeilen)

**Zweck**: Selbstständiges Denken im Hintergrund

```python
class AutonomousThinking:
    """Autonome Gedankengenerierung"""

    def __init__(self):
        self.thought_stream = []
        self.intrusive_thoughts = []
        self.background_processes = []

    async def think(self):
        """Kontinuierlicher Denkprozess"""
        while True:
            # Normale Gedanken
            if random.random() < 0.3:
                thought = self._generate_thought()
                self.thought_stream.append(thought)

            # Gelegentlich intrusive Gedanken
            if random.random() < 0.05:
                intrusive = self._generate_intrusive_thought()
                self.intrusive_thoughts.append(intrusive)

            await asyncio.sleep(0.5)

    def _generate_thought(self) -> Thought:
        """Generiert einen normalen Gedanken"""
        sources = [
            self._think_about_recent_conversation,
            self._think_about_current_topic,
            self._random_association,
            self._reflect_on_self
        ]
        generator = random.choice(sources)
        return generator()

    def associate(self, concept: str) -> List[str]:
        """Assoziatives Denken"""
        associations = self._find_associations(concept)
        return [self._elaborate(a) for a in associations[:5]]
```

### 9.3 holo_drive_system.py (~1.700 Zeilen)

**Zweck**: Bedürfnisse und Antriebe

```python
class DriveSystem:
    """Verwaltet Holos Bedürfnisse und Antriebe"""

    def __init__(self):
        # Primäre Antriebe
        self.primary_drives = {
            DriveType.CURIOSITY: 0.8,
            DriveType.CONNECTION: 0.7,
            DriveType.CREATIVITY: 0.85
        }

        # Sekundäre Antriebe
        self.secondary_drives = {
            DriveType.GROWTH: 0.6,
            DriveType.ACHIEVEMENT: 0.5
        }

        # Meta-Antriebe
        self.meta_drives = {
            DriveType.SELF_UNDERSTANDING: 0.7
        }

    def update_drive(self, drive_type: DriveType, satisfaction: float):
        """Aktualisiert einen Antrieb nach Befriedigung"""
        current = self._get_drive(drive_type)
        # Befriedigung reduziert temporär den Drang
        new_value = current - satisfaction * 0.3
        self._set_drive(drive_type, max(0, new_value))

    def generate_goals(self) -> List[Goal]:
        """Generiert Ziele aus unbefriedigten Antrieben"""
        goals = []
        for drive, level in self._get_unsatisfied_drives():
            goal = self._drive_to_goal(drive, level)
            goals.append(goal)
        return goals

    def get_dominant_drive(self) -> DriveType:
        """Welcher Antrieb ist gerade am stärksten?"""
        all_drives = {**self.primary_drives, **self.secondary_drives}
        return max(all_drives, key=all_drives.get)
```

---

## 10. Medien & Wissen

### 10.1 holo_media_knowledge.py (~1.000 Zeilen)

**Zweck**: Wissen über Medien (Filme, Serien, Musik)

```python
class MediaKnowledge:
    """Wissensbasis für Medieninhalte"""

    def __init__(self):
        self.movies = {}
        self.shows = {}
        self.music = {}
        self.preferences = MediaPreferences()

    def learn_media(self, media_type: str, media_info: dict):
        """Lernt über ein neues Medium"""
        if media_type == "movie":
            self.movies[media_info["title"]] = Movie(**media_info)
        elif media_type == "show":
            self.shows[media_info["title"]] = Show(**media_info)
        elif media_type == "music":
            self.music[media_info["title"]] = Music(**media_info)

    def recommend(self, user_mood: str) -> List[Media]:
        """Empfiehlt Medien basierend auf Stimmung"""
        candidates = self._filter_by_mood(user_mood)
        return self._rank_by_preference(candidates)
```

### 10.2 holo_media_discovery.py (~3.300 Zeilen)

**Zweck**: Entdeckung neuer Medien und Trends

```python
class MediaDiscovery:
    """Entdeckt neue Medien und Trends"""

    def __init__(self):
        self.sources = []
        self.discovered = []
        self.trending = []

    async def discover(self):
        """Entdeckt kontinuierlich neue Inhalte"""
        for source in self.sources:
            new_content = await source.fetch_new()
            for item in new_content:
                if self._is_interesting(item):
                    self.discovered.append(item)
                    self._notify_discovery(item)

    def track_trends(self) -> List[Trend]:
        """Verfolgt aktuelle Trends"""
        return self._analyze_trending()
```

### 10.3 holo_music_experience.py (~2.000 Zeilen)

**Zweck**: Musikverständnis und -erlebnis

```python
class MusicExperience:
    """Holos Musikerleben"""

    def __init__(self):
        self.taste = MusicTaste()
        self.emotional_responses = {}
        self.memories = MusicMemories()

    def experience_song(self, song: Song) -> MusicResponse:
        """Erlebt ein Lied emotional"""
        analysis = self._analyze_song(song)
        emotional_response = self._generate_emotion(analysis)

        # Speichere emotionale Assoziation
        self.emotional_responses[song.id] = emotional_response

        # Prüfe auf Erinnerungen
        memory = self.memories.recall(song)
        if memory:
            emotional_response.memory = memory

        return MusicResponse(
            song=song,
            emotion=emotional_response,
            rating=self._rate_song(song),
            thoughts=self._generate_thoughts(song)
        )

    def recommend_for_mood(self, mood: str) -> List[Song]:
        """Empfiehlt Musik für eine Stimmung"""
        # Finde Lieder, die diese Stimmung erzeugen
        matching = []
        for song_id, response in self.emotional_responses.items():
            if response.emotion == mood:
                matching.append(self._get_song(song_id))
        return matching
```

### 10.4 holo_web_curiosity.py (~1.500 Zeilen)

**Zweck**: Autonome Web-Recherche und Neugier

```python
class WebCuriosity:
    """Autonome Web-Entdeckung"""

    def __init__(self):
        self.topics_of_interest = []
        self.followed_sources = []
        self.discoveries = []

    async def explore(self):
        """Erkundet das Web basierend auf Interessen"""
        for topic in self.topics_of_interest:
            results = await self._search(topic)
            interesting = self._filter_interesting(results)
            for item in interesting:
                self.discoveries.append(item)
                self._process_discovery(item)

    def follow_news(self, topic: str):
        """Verfolgt Nachrichten zu einem Thema"""
        self.topics_of_interest.append(topic)

    def get_news_summary(self) -> str:
        """Zusammenfassung der neuesten Entdeckungen"""
        recent = self.discoveries[-10:]
        return self._summarize_discoveries(recent)
```

---

## 11. Datenpersistenz

### 11.1 holo_database_system.py (~7.700 Zeilen)

**Zweck**: Verwaltung von 17 spezialisierten SQLite-Datenbanken

```python
class HoloDatabaseManager:
    """Zentrale Datenbankverwaltung (siehe holo_database_system.py:7272)"""

    # Die 17 tatsächlichen Datenbank-Klassen:
    DATABASES = {
        "memory": MemoryDatabase,         # Erinnerungen, Erlebnisse
        "emotions": EmotionsDatabase,     # Emotionsverläufe
        "knowledge": KnowledgeDatabase,   # Gelernte Fakten
        "conversations": ConversationsDatabase,  # Gesprächsverläufe
        "media": MediaDatabase,           # Medien-Metadaten
        "language": LanguageDatabase,     # Sprachmuster, Phrasen
        "activity": ActivityDatabase,     # Aktivitäten, Handlungen
        "identity": IdentityDatabase,     # Personen, Entitäten
        "state": StateDatabase,           # Systemzustand
        "productivity": ProductivityDatabase,  # Timer, Todos, Notizen
        "environment": EnvironmentDatabase,    # Umgebungsdaten
        "network": NetworkDatabase,       # Netzwerk-Geräte
        "presence": PresenceDatabase,     # Anwesenheitserkennung
        "home": HomeDatabase,             # Smart Home Status
        "news": NewsDatabase,             # Gelesene Nachrichten
        "calendar": CalendarDatabase,     # Termine, Events
        "predictions": PredictionsDatabase  # Vorhersagen, Muster
    }

    def __init__(self):
        self.databases = {}
        for name, db_class in self.DATABASES.items():
            self.databases[name] = db_class()

    def get(self, name: str):
        """Gibt eine spezifische Datenbank zurück"""
        return self.databases.get(name)

    def backup_all(self, backup_dir: str):
        """Sichert alle Datenbanken"""
        for name, db in self.databases.items():
            db.backup(f"{backup_dir}/{name}.db.bak")

    def migrate_all(self):
        """Führt Migrationen für alle DBs durch"""
        for db in self.databases.values():
            db.migrate()

class BrainDatabase:
    """Speichert Kernerinnerungen und Emotionen"""

    def store_memory(self, memory: Memory):
        """Speichert eine Erinnerung"""
        self.execute(
            "INSERT INTO memories (content, emotion, timestamp, importance) "
            "VALUES (?, ?, ?, ?)",
            (memory.content, memory.emotion, memory.timestamp, memory.importance)
        )

    def recall(self, query: str, limit: int = 10) -> List[Memory]:
        """Ruft relevante Erinnerungen ab"""
        # Ähnlichkeitssuche
        return self.search_similar(query, limit)

class KnowledgeBase:
    """Speichert gelernte Fakten"""

    def add_fact(self, fact: str, source: str, confidence: float):
        """Fügt ein neues Faktum hinzu"""
        self.execute(
            "INSERT INTO facts (content, source, confidence) VALUES (?, ?, ?)",
            (fact, source, confidence)
        )

    def query_facts(self, topic: str) -> List[Fact]:
        """Fragt Fakten zu einem Thema ab"""
        return self.search(f"topic:{topic}")
```

### 11.2 JSON-Dateien in data/

```python
# conversation_context.json
{
    "current_topic": "...",
    "history": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
    ],
    "entities_mentioned": [],
    "emotions_detected": []
}

# trust_network.json
{
    "persons": {
        "Kira": {"trust_level": 1.0, "relationship": "owner"},
        "...": {"trust_level": 0.5, "relationship": "acquaintance"}
    }
}

# regrets.json
[
    {
        "action": "...",
        "consequence": "...",
        "lesson_learned": "...",
        "timestamp": "..."
    }
]
```

---

## 12. Integration & Schnittstellen

### 12.1 holo_intelligent_router.py (~10.000 Zeilen)

**Zweck**: Zentrale Routing-Logik für alle Anfragen

```python
class RouteType(Enum):
    """Routing-Entscheidungen"""
    LOCAL_TEMPLATE = "local_template"   # Lokale Vorlagen
    LOCAL_NLP = "local_nlp"             # Lokale NLP-Verarbeitung
    HYBRID_IMPULSE = "hybrid_impulse"   # Hybrid mit Impulsen
    HYBRID_CREATIVE = "hybrid_creative" # Hybrid mit Kreativität
    LLM_SIMPLE = "llm_simple"           # Einfache LLM-Anfrage
    LLM_FULL = "llm_full"               # Vollständige LLM-Verarbeitung
    LLM_EXTENDED = "llm_extended"       # Erweiterte LLM-Verarbeitung
    DIRECT_ANSWER = "direct_answer"     # Direkte Antwort
    SKILL_EXECUTION = "skill_execution" # Skill-Ausführung

class ResponseStyle(Enum):
    """Antwort-Stile basierend auf Persönlichkeit"""
    PLAYFUL = "playful"
    SERIOUS = "serious"
    CARING = "caring"
    CURIOUS = "curious"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    SUPPORTIVE = "supportive"
    ENTHUSIASTIC = "enthusiastic"
    REFLECTIVE = "reflective"
    NEUTRAL = "neutral"

class IntelligentRouter:
    """Zentrales Routing für alle Anfragen"""

    def __init__(self):
        # Verbindungen zu allen Subsystemen
        self.energy_system = None
        self.emotion_system = None
        self.cognitive_modules = None
        self.impulse_system = None
        self.personality = None
        self.understanding = None

    def route(self, message: str) -> RouteDecision:
        """Entscheidet über die beste Route für eine Anfrage"""

        # 1. Verstehe die Nachricht
        understanding = self.understanding.understand(message)

        # 2. Prüfe Energie-Level
        energy = self.energy_system.get_overall_energy()

        # 3. Prüfe emotionalen Zustand
        emotion = self.emotion_system.current_emotion

        # 4. Bestimme Route basierend auf allem
        route = self._decide_route(understanding, energy, emotion)

        # 5. Bestimme Antwort-Stil
        style = self._decide_style(understanding, emotion)

        return RouteDecision(
            route_type=route,
            style=style,
            understanding=understanding,
            modifiers=self._get_modifiers()
        )

    def _decide_route(self, understanding, energy, emotion) -> RouteType:
        """Entscheidungslogik für Routing"""

        # Einfache Fragen → Lokal
        if understanding.is_simple_greeting:
            return RouteType.LOCAL_TEMPLATE

        # Faktenfragen → LLM
        if understanding.needs_knowledge:
            return RouteType.LLM_SIMPLE

        # Kreative Anfragen → Hybrid
        if understanding.is_creative:
            return RouteType.HYBRID_CREATIVE

        # Komplexe Diskussionen → Volles LLM
        if understanding.complexity > 0.7:
            return RouteType.LLM_FULL

        # Standard → NLP
        return RouteType.LOCAL_NLP
```

### 12.2 smart_llm_system.py (~1.100 Zeilen)

**Zweck**: Einheitliche LLM-Schnittstelle zu Ollama

```python
class UnifiedLLM:
    """Einheitliche Schnittstelle zu Ollama"""

    def __init__(self, config):
        self.host = config.network.ollama.host
        self.port = config.network.ollama.port
        self.local_model = config.llm.local_model
        self.remote_model = config.llm.remote_model
        self.pattern_cache = PatternCache()

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generiert eine Antwort"""

        # Stufe 1: Pattern-Cache prüfen
        cached = self.pattern_cache.check(prompt)
        if cached:
            return cached

        # Stufe 2: Lokales Modell versuchen
        try:
            response = await self._call_model(self.local_model, prompt)
            return response
        except Exception:
            pass

        # Stufe 3: Remote-Modell als Fallback
        return await self._call_model(self.remote_model, prompt)

    async def _call_model(self, model: str, prompt: str) -> str:
        """Ruft ein spezifisches Modell auf"""
        url = f"http://{self.host}:{self.port}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                result = await resp.json()
                return result["response"]
```

### 12.3 pi_holo_interface.py (~1.400 Zeilen)

**Zweck**: Raspberry Pi Kommunikation

```python
class HoloInterface:
    """Schnittstelle zum Raspberry Pi"""

    def __init__(self):
        self.state_file = "state/holo_to_pi.json"
        self.mqtt_client = MQTTClient()

    def send_state(self, state: HoloState):
        """Sendet aktuellen Zustand an Pi"""
        state_dict = {
            "mood": state.mood,
            "energy": state.energy,
            "activity": state.current_activity,
            "timestamp": datetime.now().isoformat()
        }
        with open(self.state_file, "w") as f:
            json.dump(state_dict, f)

        # Auch per MQTT senden
        self.mqtt_client.publish("holo/state", json.dumps(state_dict))

    def receive_command(self) -> Optional[Command]:
        """Empfängt Befehle vom Pi"""
        return self.mqtt_client.get_latest("pi/commands")
```

### 12.4 pi_control_v8_AI-extendet.py (~10.000 Zeilen)

**Zweck**: Fortgeschrittene Pi-Steuerung mit kognitiver Vorhersage

```python
class CognitivePredictiveAgent:
    """7-Schichten-Architektur für Pi-Steuerung"""

    LAYERS = [
        "perception",     # Wahrnehmung
        "attention",      # Aufmerksamkeit
        "memory",         # Gedächtnis
        "prediction",     # Vorhersage
        "planning",       # Planung
        "action",         # Aktion
        "learning"        # Lernen
    ]

    def __init__(self):
        self.presence_zones = {}
        self.predictions = PredictionEngine()
        self.goals = GoalManager()
        self.home_assistant = HomeAssistantClient()

    async def process(self):
        """Hauptverarbeitungsschleife"""
        while True:
            # Wahrnehmung sammeln
            perception = await self._gather_perception()

            # Aufmerksamkeit fokussieren
            focus = self._focus_attention(perception)

            # Gedächtnis konsultieren
            context = self._recall_context(focus)

            # Vorhersagen treffen
            prediction = self.predictions.predict(perception, context)

            # Aktionen planen
            plan = self._create_plan(prediction)

            # Aktionen ausführen
            await self._execute_plan(plan)

            # Aus Ergebnis lernen
            self._learn_from_outcome(plan)

            await asyncio.sleep(0.1)
```

---

## 13. Datenfluss & Verarbeitung

### Hauptverarbeitungsfluss

```
                    ┌─────────────────┐
                    │  USER INPUT     │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│          holo_brain.py: HoloPersona.process_message() │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│    holo_smart_understanding.py: SmartUnderstanding    │
│    ├─ Intent-Erkennung                                │
│    ├─ Entitäten-Extraktion                            │
│    └─ Tippfehler-Korrektur                            │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│     holo_intelligent_router.py: Route-Entscheidung    │
│     ├─ energy_system → Energie-Level                  │
│     ├─ emotions → Emotionaler Kontext                 │
│     ├─ cognitive_modules → Reasoning-Tiefe            │
│     ├─ impulse_system → Authentizität                 │
│     └─ Entscheidung: LOCAL | HYBRID | LLM             │
└────────────────────────────┬───────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌─────────────┐  ┌───────────┐  ┌──────────────┐
     │ LOCAL       │  │ HYBRID    │  │ LLM          │
     │ ├─ Template │  │ ├─ NLP    │  │ ├─ Compress  │
     │ └─ NLP      │  │ └─ LLM    │  │ └─ Generate  │
     └──────┬──────┘  └─────┬─────┘  └───────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│              Personalisierung                          │
│     ├─ holo_personality.py: Persönlichkeits-Traits    │
│     ├─ holo_self_expression.py: Emotionaler Ausdruck  │
│     ├─ holo_energy_system.py: Energie-basierter Stil  │
│     └─ holo_creative_mind.py: Kreativität hinzufügen  │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────┐
│              Autonomes Leben Update                    │
│     ├─ holo_inner_life.py: Innere Gedanken            │
│     ├─ holo_impulse_system.py: Neue Impulse           │
│     ├─ holo_drive_system.py: Antriebe aktualisieren   │
│     └─ holo_learning.py: Fakten speichern             │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    RESPONSE     │
                    └─────────────────┘
```

### Modul-Abhängigkeiten

```
holo_core_types (BASIS - keine Abhängigkeiten)
        │
        ▼
holo_robust_imports
        │
        ▼
┌───────┴───────┬───────────────┐
▼               ▼               ▼
holo_config     holo_error_     holo_error_
                handling        tracker
        │
        ▼
┌───────┴───────┐
▼               ▼
holo_database   smart_llm_
system          system
        │
        ▼
┌───────┴───────┬───────────────┐
▼               ▼               ▼
holo_          holo_           holo_energy_
consciousness  inner_life      system
        │
        ▼
┌───────┴───────┐
▼               ▼
holo_          holo_cognitive_
personality    modules
        │
        ▼
┌───────┴───────┐
▼               ▼
holo_smart_    holo_nlp_
understanding  algorithms
        │
        ▼
holo_intelligent_router (ZENTRALER HUB)
        │
        ▼
holo_brain.py (ORCHESTRATOR)
```

---

## 14. Einstiegspunkte

### 14.1 holo_brain.py - Vollständiges System

```python
# Start des kompletten Systems
from holo_brain import HoloPersona

# Initialisierung
holo = HoloPersona()

# Einzelne Nachricht verarbeiten
response = holo.process_message("Hallo Holo!")

# Event-Loop starten (für autonomes Verhalten)
holo.run()
```

### 14.2 holo_unified.py - Vereinfachte Schnittstelle

```python
# Vereinfachter Zugang
from holo_unified import HoloUnified

# Standalone-Modus (ohne alle Subsysteme)
holo = HoloUnified()

# Chat-Modus
response = holo.chat("Wie geht es dir?")

# Mit Statistiken
result = holo.process("Was weißt du über KI?")
print(result.stats)

# Spezielle Befehle
# /stats - Zeigt Statistiken
# /name [name] - Setzt/zeigt Namen
```

### 14.3 Kommandozeile

```bash
# Direkte Ausführung
python holo_brain.py

# Im Test-Modus
python holo_unified.py --test

# Mit spezifischer Konfiguration
HOLO_LOG_LEVEL=DEBUG python holo_brain.py
```

---

## 15. Test-Framework

### Test-Dateien

| Datei | Testet |
|-------|--------|
| `test_brain_background.py` | Hintergrundaufgaben |
| `test_dashboard.py` | Web-Dashboard |
| `test_database_system.py` | Datenbanksystem |
| `test_error_tracker.py` | Fehler-Tracking |
| `test_integration.py` | Systemintegration |
| `test_memory_monitor.py` | Speicherüberwachung |
| `test_process_controller.py` | Prozesssteuerung |
| `test_ram_manager.py` | RAM-Verwaltung |
| `test_shutdown.py` | Graceful Shutdown |
| `test_smart_llm.py` | LLM-System |

### Tests ausführen

```bash
# Alle Tests
pytest tests/

# Spezifische Tests
pytest tests/test_database_system.py

# Mit Coverage
pytest tests/ --cov=. --cov-report=html

# Verbose Ausgabe
pytest tests/ -v

# Nur fehlgeschlagene Tests erneut
pytest tests/ --lf
```

### conftest.py - Pytest-Konfiguration

```python
# Gemeinsame Fixtures für alle Tests
@pytest.fixture
def mock_config():
    return MockConfig()

@pytest.fixture
def test_database(tmp_path):
    db = DatabaseManager(path=tmp_path)
    yield db
    db.cleanup()

@pytest.fixture
async def holo_instance():
    holo = HoloPersona(test_mode=True)
    yield holo
    await holo.shutdown()
```

---

## 16. Abhängigkeiten

### requirements.txt

```
# HTTP & Async
aiohttp>=3.8.0
requests>=2.28.0

# System
psutil>=5.9.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Optional (für erweiterte Features)
# numpy>=1.24.0
# scipy>=1.10.0
# opencv-python>=4.7.0
# librosa>=0.10.0
# pyttsx3>=2.90
# websockets>=11.0
# paho-mqtt>=1.6.0
```

### Externe Dienste

| Dienst | URL | Zweck |
|--------|-----|-------|
| Ollama | http://192.168.178.42:11434 | LLM-Generierung |
| MQTT Broker | 192.168.178.99:1883 | IoT-Kommunikation |
| Home Assistant | http://192.168.178.99:8123/api | Smart Home |
| NAS | 192.168.178.40 | Datenspeicherung |
| ComfyUI | localhost:8188 | Bildgenerierung |

---

## 17. Modulreferenz (Komplett)

### Alphabetische Liste aller 78+ Module

| # | Modul | Zeilen | Kategorie | Beschreibung |
|---|-------|--------|-----------|--------------|
| 1 | `holo_algorithmic_cognition.py` | ~2.500 | Kognition | Theoretische CS-Konzepte |
| 2 | `holo_audio.py` | ~650 | Wahrnehmung | Basis-Audioverarbeitung |
| 3 | `holo_audio_enhanced.py` | ~1.400 | Wahrnehmung | Erweiterte Audio-Analyse |
| 4 | `holo_autonomous_thinking.py` | ~2.050 | Autonomie | Selbstständiges Denken |
| 5 | `holo_brain.py` | ~26.600 | **KERN** | **Haupt-Orchestrator** |
| 6 | `holo_brain_background.py` | ~800 | System | Hintergrundaufgaben |
| 7 | `holo_brain_controller.py` | ~600 | System | Brain-Steuerung |
| 8 | `holo_brain_core.py` | ~450 | Kern | Kern-Konfiguration |
| 9 | `holo_cognitive_engine.py` | ~2.100 | Kognition | Kognitive Pipeline |
| 10 | `holo_cognitive_integration.py` | ~4.000 | Kognition | Modul-Integration |
| 11 | `holo_cognitive_modules.py` | ~9.000 | Kognition | Erweiterte Kognition |
| 12 | `holo_config.py` | ~450 | Kern | Konfigurationslader |
| 13 | `holo_consciousness.py` | ~4.500 | Kognition | Bewusstseinssimulation |
| 14 | `holo_context_compression.py` | ~750 | Utility | Kontext-Kompression |
| 15 | `holo_context_mind.py` | ~2.200 | Kognition | Kontextaufbau |
| 16 | `holo_core_types.py` | ~1.500 | **KERN** | **Typdefinitionen** |
| 17 | `holo_creative_mind.py` | ~2.500 | Kognition | Kreativitäts-Engine |
| 18 | `holo_crossmodal.py` | ~1.250 | Wahrnehmung | Cross-modale Integration |
| 19 | `holo_dashboard.py` | ~2.300 | System | Web-Dashboard |
| 20 | `holo_database_system.py` | ~7.000 | **KERN** | **17 Datenbanken** |
| 21 | `holo_depth_system.py` | ~1.900 | Kognition | Tiefenanalyse |
| 22 | `holo_device_agent.py` | ~640 | Integration | Geräte-Agent |
| 23 | `holo_device_receiver.py` | ~650 | Integration | Geräte-Empfänger |
| 24 | `holo_dialogue_engine.py` | ~1.500 | Kommunikation | Dialogmanagement |
| 25 | `holo_document.py` | ~800 | Medien | Dokumentverarbeitung |
| 26 | `holo_drive_system.py` | ~1.700 | Autonomie | Antriebe & Bedürfnisse |
| 27 | `holo_emotional_complexity.py` | ~1.200 | Emotion | Komplexe Emotionen |
| 28 | `holo_energy_management.py` | ~1.400 | System | Energie-Management |
| 29 | `holo_energy_system.py` | ~1.900 | **KERN** | **6D-Energiemodell** |
| 30 | `holo_entity_database.py` | ~2.000 | Daten | Entitätenverwaltung |
| 31 | `holo_error_handling.py` | ~450 | Kern | Fehlerbehandlung |
| 32 | `holo_error_tracker.py` | ~650 | System | Fehler-Tracking |
| 33 | `holo_impulse_system.py` | ~1.250 | Autonomie | Impulsgenerierung |
| 34 | `holo_inner_life.py` | ~8.000 | **KERN** | **Innenleben** |
| 35 | `holo_integration_layer.py` | ~4.300 | Integration | Integrationsschicht |
| 36 | `holo_intelligent_router.py` | ~10.000 | **KERN** | **Zentrales Routing** |
| 37 | `holo_learning.py` | ~2.900 | Kognition | Lernsystem |
| 38 | `holo_media_discovery.py` | ~3.300 | Medien | Medien-Entdeckung |
| 39 | `holo_media_index.py` | ~1.100 | Medien | Medien-Indexierung |
| 40 | `holo_media_integration.py` | ~850 | Medien | Medien-Integration |
| 41 | `holo_media_knowledge.py` | ~1.000 | Medien | Medienwissen |
| 42 | `holo_memory_monitor.py` | ~600 | System | Speicherüberwachung |
| 43 | `holo_message_analyzer.py` | ~1.100 | Kommunikation | Nachrichtenanalyse |
| 44 | `holo_meta_cognition.py` | ~2.050 | Kognition | Meta-Kognition |
| 45 | `holo_module_loader.py` | ~750 | Kern | Modul-Loader |
| 46 | `holo_music_experience.py` | ~2.000 | Medien | Musikerlebnis |
| 47 | `holo_nlp_advanced.py` | ~1.200 | NLP | Fortgeschrittene NLP |
| 48 | `holo_nlp_algorithms.py` | ~3.700 | **KERN** | **NLP-Algorithmen** |
| 49 | `holo_nlp_enhanced.py` | ~1.500 | NLP | Erweiterte NLP |
| 50 | `holo_perception.py` | ~1.400 | Wahrnehmung | Basis-Wahrnehmung |
| 51 | `holo_perception_unified.py` | ~1.700 | Wahrnehmung | Einheitliche Wahrnehmung |
| 52 | `holo_person_opinions.py` | ~1.600 | Daten | Personen-Meinungen |
| 53 | `holo_personality.py` | ~3.200 | **KERN** | **Persönlichkeit** |
| 54 | `holo_policy_engine.py` | ~2.700 | System | Policy-Engine |
| 55 | `holo_preferences.py` | ~3.400 | Daten | Präferenzsystem |
| 56 | `holo_process_controller.py` | ~1.000 | System | Prozesssteuerung |
| 57 | `holo_ram_manager.py` | ~750 | System | RAM-Verwaltung |
| 58 | `holo_reader_extended.py` | ~1.400 | Medien | Erweitertes Lesen |
| 59 | `holo_robust_imports.py` | ~1.500 | **KERN** | **Sichere Imports** |
| 60 | `holo_self_awareness.py` | ~2.400 | Kognition | Selbstbewusstsein |
| 61 | `holo_self_expression.py` | ~800 | Kommunikation | Selbstausdruck |
| 62 | `holo_skill_system.py` | ~1.000 | System | Skill-System |
| 63 | `holo_smart_understanding.py` | ~5.000 | **KERN** | **Intent-Erkennung** |
| 64 | `holo_speech_engine.py` | ~2.000 | Kommunikation | Sprach-Engine |
| 65 | `holo_text_reader.py` | ~850 | Medien | Textverarbeitung |
| 66 | `holo_tools.py` | ~1.000 | Utility | Werkzeuge |
| 67 | `holo_unified.py` | ~1.400 | Integration | Vereinfachte API |
| 68 | `holo_video.py` | ~650 | Wahrnehmung | Videoverarbeitung |
| 69 | `holo_vision_advanced.py` | ~1.350 | Wahrnehmung | Fortgeschrittene Vision |
| 70 | `holo_vision_enhanced.py` | ~1.300 | Wahrnehmung | Erweiterte Vision |
| 71 | `holo_vision_extended.py` | ~1.300 | Wahrnehmung | Extended Vision |
| 72 | `holo_voice_interface.py` | ~1.300 | Kommunikation | Sprach-Interface |
| 73 | `holo_web_curiosity.py` | ~1.500 | Autonomie | Web-Neugier |
| 74 | `holo_websocket_handler.py` | ~650 | Integration | WebSocket-Handler |
| 75 | `holo_wiring.py` | ~400 | Integration | Modul-Verbindungen |
| 76 | `pi_control_v8_AI-extendet.py` | ~10.000 | Integration | Pi-Steuerung |
| 77 | `pi_holo_interface.py` | ~1.400 | Integration | Pi-Schnittstelle |
| 78 | `smart_llm_system.py` | ~1.100 | **KERN** | **LLM-System** |

---

## Zusammenfassung

**Holocloude** ist ein hochentwickeltes, kognitives KI-System mit:

- **78+ Python-Module** mit klarer Trennung der Verantwortlichkeiten
- **~400.000+ Zeilen Code** für umfassende KI-Funktionalität
- **Modulare Architektur** mit graceful degradation
- **17 spezialisierte Datenbanken** für Persistenz
- **Multi-Layer Routing** (lokal, hybrid, remote LLM)
- **Reiches emotionales und kognitives System**
- **Autonomes Verhalten** und Kreativität
- **Smart Home Integration** über MQTT und Home Assistant
- **Umfassendes Test-Framework** mit pytest

Das System ist so konzipiert, dass es wartbar, erweiterbar und widerstandsfähig ist - durch durchdachte Modultrennung, Abhängigkeitsmanagement und Fallback-Systeme.

---

*Dokumentation automatisch generiert am 14. Januar 2026*
