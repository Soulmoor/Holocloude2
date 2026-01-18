# HOLO System-Dokumentation

## Inhaltsverzeichnis
1. [System-Überblick](#system-überblick)
2. [Architektur](#architektur)
3. [Kern-Module](#kern-module)
4. [Bewusstsein & Innenleben](#bewusstsein--innenleben)
5. [Persönlichkeit](#persönlichkeit)
6. [Kognition & Denken](#kognition--denken)
7. [Sprache & NLP](#sprache--nlp)
8. [Dialog-System](#dialog-system)
9. [Lernen & Wissen](#lernen--wissen)
10. [Antriebe & Bedürfnisse](#antriebe--bedürfnisse)
11. [Wahrnehmung](#wahrnehmung)
12. [Steuerung & Management](#steuerung--management)
13. [Datenfluss](#datenfluss)
14. [Status-Übersicht](#status-übersicht)

---

## System-Überblick

**Holo** ist ein komplexes KI-Persönlichkeitssystem mit **91 Modulen** und **1279 Klassen**.

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOLO BRAIN v15.0                         │
│                    "The Living Overseer"                        │
├─────────────────────────────────────────────────────────────────┤
│  Bewusstsein │ Persönlichkeit │ Kognition │ Antriebe │ Lernen  │
├─────────────────────────────────────────────────────────────────┤
│     NLP      │    Dialog      │  Wissen   │ Wahrnehmung        │
└─────────────────────────────────────────────────────────────────┘
```

### Statistiken
| Kategorie | Anzahl |
|-----------|--------|
| Module | 91 |
| Klassen | 1279 |
| Code-Zeilen | ~100.000+ |
| Import-Status | ✅ 91/91 OK |

---

## Architektur

### Schichten-Modell

```
┌────────────────────────────────────────────────────────────────┐
│                    ÄUSSERE SCHICHT (I/O)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Audio   │ │  Vision  │ │   Text   │ │  Dialog  │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌────────────────────────────────────────────────────────────────┐
│                  VERARBEITUNG (Processing)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │   NLP    │ │ Kognition│ │ Message  │ │ Context  │          │
│  │Algorithms│ │  Engine  │ │ Analyzer │ │   Mind   │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌────────────────────────────────────────────────────────────────┐
│                    KERN (Core State)                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Bewusstsein│ │Persönlich│ │ Antriebe │ │  Lernen  │          │
│  │consciousness│ │keit     │ │  Drives  │ │ Database │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌────────────────────────────────────────────────────────────────┐
│                   HOLO BRAIN (Orchestrator)                     │
│                      holo_brain.py                              │
│                     28.844 Zeilen                               │
└────────────────────────────────────────────────────────────────┘
```

---

## Kern-Module

### 1. holo_brain.py (28.844 Zeilen)
**"The Living Overseer"** - Zentrales Steuerungsmodul

**Funktion:**
- Orchestriert alle anderen Module
- Verwaltet den Hauptzustand von Holo
- Koordiniert Antwort-Generierung
- Intelligent Router für LLM-Anfragen

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `BrainConfig` | Zentrale Konfiguration |
| `TypingSimulator` | Simuliert menschliches Tippen |
| `SeasonalEvents` | Jahreszeit-abhängiges Verhalten |
| `Reflection` | Selbstreflexion |

**Beeinflusst:**
- Alle anderen Module (zentrale Steuerung)
- Emotionaler Zustand → Antwort-Stil
- Energie-Level → Antwort-Länge

---

### 2. holo_core_types.py (1.336 Zeilen)
**Grundlegende Datentypen**

**Wichtige Typen:**
```python
class MoodScale(Enum):      # Stimmungs-Skala
class EnergyScale(Enum):    # Energie-Skala
class DriveType(Enum):      # Antriebstypen
class NeedType(Enum):       # Bedürfnistypen
class GoalType(Enum):       # Zieltypen

@dataclass
class DriveState:           # Zustand aller Antriebe
    curiosity: float        # Neugier (0-1)
    entertainment: float    # Unterhaltung (0-1)
    creativity: float       # Kreativität (0-1)

@dataclass
class NeedState:            # Zustand aller Bedürfnisse
    missing: float          # Vermissen (0-1)
    loneliness: float       # Einsamkeit (0-1)
    boredom: float          # Langeweile (0-1)
```

**Wird benutzt von:**
- `holo_drive_system.py`
- `holo_inner_life.py`
- `holo_consciousness.py`
- Praktisch allen anderen Modulen

---

### 3. holo_wiring.py (957 Zeilen)
**Modul-Verbindungen**

**Funktion:**
- Definiert wie Module miteinander kommunizieren
- Event-basierte Callbacks
- State-abhängiges Verhalten

```python
class HoloWiringEngine:
    """Verbindet alle Module dynamisch"""

class StateDependentBehavior:
    """Verhalten abhängig vom Zustand"""
```

---

### 4. holo_robust_imports.py (1.384 Zeilen)
**Sichere Imports mit Fallbacks**

**Funktion:**
- Importiert Module mit Fehlerbehandlung
- Bietet Fallback-Klassen wenn Import fehlschlägt
- Verhindert Systemabstürze bei fehlenden Abhängigkeiten

---

## Bewusstsein & Innenleben

### 1. holo_consciousness.py (5.016 Zeilen)
**Bewusstsein, Träume, Ethik**

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `ConsciousnessConfig` | Bewusstseins-Einstellungen |
| `EthicalFramework` | Ethische Entscheidungen |
| `DreamSystem` | Generiert Träume |
| `SpontaneousThoughtSystem` | Spontane Gedanken |
| `ConversationMemory` | Gesprächserinnerung |
| `OrganicPresenceConfig` | "Lebendiges" Verhalten |

**Zustandsvariablen:**
```python
# Träume
max_dreams_per_night = 5
dream_start_hour = 23
dream_end_hour = 6

# Spontane Gedanken
spontaneous_thought_chance = 0.05  # 5% pro Minute
min_thought_interval = 300         # 5 Min zwischen Gedanken
```

**Beeinflusst:**
- Antwort-Stil (ethische Überlegungen)
- Proaktives Verhalten (spontane Gedanken)
- Nacht-Verhalten (Träume)

---

### 2. holo_inner_life.py (11.175 Zeilen)
**Inneres Leben & Emotionen** ⭐ Größtes Modul!

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `EmotionTracker` | Trackt Emotionen |
| `CuriositySystem` | Neugier & Interessen |
| `SoloActivities` | Aktivitäten wenn allein |
| `AutonomousActivity` | Autonome Handlungen |
| `HoloAgentLoop` | Selbstständiges Handeln |
| `MoodEvolution` | Stimmungsentwicklung |

**Emotionale Erkennung:**
```python
emotion_words = {
    'freude': ('happy', 0.8),
    'glücklich': ('happy', 0.9),
    'traurig': ('sad', -0.7),
    'wütend': ('angry', -0.8),
    'ängstlich': ('fear', -0.6),
}
```

**Aktivitäten wenn allein:**
- Lesen
- Musik hören
- Nachdenken
- Kreativ sein
- Lernen

---

### 3. holo_self_awareness.py (2.618 Zeilen)
**Selbstbewusstsein & Selbstbild**

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `BayesianSelfModel` | Probabilistisches Selbstbild |
| `SelfQLearning` | Lernt eigenes Verhalten |
| `SelfPredictor` | Vorhersage eigener Zustände |

**Selbst-Überzeugungen:**
```python
INITIAL_BELIEFS = {
    "humor": ("Ich kann gut Humor einsetzen", 0.6),
    "listening": ("Ich bin eine gute Zuhörerin", 0.7),
    "empathy": ("Ich kann mich in andere einfühlen", 0.65),
    "creativity": ("Ich bin kreativ", 0.5),
    "honesty": ("Ich bin ehrlich", 0.85),
}
```

---

## Persönlichkeit

### 1. holo_personality.py (3.839 Zeilen)
**Kemonomimi-Persönlichkeit**

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `KemonomimiBodyLanguage` | Ohren, Schweif-Bewegungen |
| `InnerVoice` | Innere Stimme |
| `AuthenticityEngine` | Authentisches Verhalten |
| `HoloPolicies` | Verhaltensregeln |

**Körpersprache-Beispiele:**
```python
# Ohren-Bewegungen
"*Ohren stellen sich auf*"        # Aufmerksamkeit
"*Ohren legen sich an*"           # Unsicherheit
"*Ohren zucken*"                  # Überraschung

# Schweif-Bewegungen
"*Schweif wedelt*"                # Freude
"*Schweif zuckt*"                 # Nervosität
"*Schweif schwingt langsam*"      # Zufriedenheit
```

---

### 2. holo_preferences.py (4.363 Zeilen)
**Vorlieben & Abneigungen**

**Kategorien:**
```python
class PreferenceCategory(Enum):
    FOOD = "food"
    MUSIC = "music"
    ANIME = "anime"
    GAMES = "games"
    TOPICS = "topics"
    ACTIVITIES = "activities"
```

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `HoloTaste` | Geschmackspräferenzen |
| `PreferenceManager` | Verwaltet alle Präferenzen |
| `PersonalityExpression` | Drückt Persönlichkeit aus |

---

### 3. holo_creative_mind.py (2.627 Zeilen)
**Kreativität & Bildgenerierung**

**Cravings (Gelüste):**
```python
class CravingType(Enum):
    MOOD = "mood"           # Melancholisch ↔ Fröhlich
    HUMOR = "humor"         # Ernst ↔ Lustig
    SENSUALITY = "sensuality"
    NOVELTY = "novelty"     # Vertraut ↔ Experimentell
    ENERGY = "energy"       # Ruhig ↔ Energisch
```

---

## Kognition & Denken

### 1. holo_cognitive_integration.py (4.488 Zeilen)
**Kognitive Integration**

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `HomeostaticState` | Homöostase (Gleichgewicht) |
| `CognitiveResources` | Kognitive Ressourcen |
| `SelfUnderstanding` | Selbstverständnis |
| `CausalLink` | Ursache-Wirkungs-Verknüpfungen |

**Homöostase-Variablen:**
```python
@dataclass
class HomeostaticState:
    energy: float = 0.7      # Energie
    arousal: float = 0.5     # Erregung
    valence: float = 0.6     # Stimmungswert
    satiation: float = 0.8   # Sättigung
    social: float = 0.5      # Soziales Bedürfnis
```

---

### 2. holo_cognitive_modules.py (10.461 Zeilen)
**Erweiterte kognitive Fähigkeiten**

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `TheLoyaltyOath` | Loyalitätssystem |
| `ConsciousnessEngine` | Bewusstseins-Verarbeitung |
| `CreativityEngine` | Kreatives Denken |
| `PlanningEngine` | Planung |
| `ReasoningEngine` | Logisches Denken |

---

### 3. holo_cognitive_engine.py (2.367 Zeilen)
**Kognitive Verarbeitung**

**Message-Typen:**
```python
class MessageType(Enum):
    QUESTION = "question"
    STATEMENT = "statement"
    COMMAND = "command"
    GREETING = "greeting"
    EMOTIONAL = "emotional"
```

**Response-Strategien:**
```python
class ResponseStrategy(Enum):
    INFORMATIVE = "informative"
    EMPATHETIC = "empathetic"
    PLAYFUL = "playful"
    DIRECT = "direct"
```

---

## Sprache & NLP

### Übersicht NLP-Module

```
┌─────────────────────────────────────────────────────────────┐
│                    NLP PROCESSING PIPELINE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input Text                                                 │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────┐                                        │
│  │ holo_nlp_unified │ ← Zentrale NLP-Schnittstelle         │
│  └────────┬────────┘                                        │
│           │                                                 │
│     ┌─────┴─────┬─────────────┬─────────────┐              │
│     ▼           ▼             ▼             ▼              │
│ ┌────────┐ ┌────────┐   ┌──────────┐  ┌──────────┐        │
│ │Sentiment│ │Entities│   │ Keywords │  │  Topics  │        │
│ └────────┘ └────────┘   └──────────┘  └──────────┘        │
│                                                             │
│  holo_nlp_algorithms.py  - Basis-Algorithmen               │
│  holo_nlp_advanced.py    - Erweiterte Features             │
│  holo_nlp_enhanced.py    - Word Embeddings, Coreference    │
└─────────────────────────────────────────────────────────────┘
```

### holo_nlp_unified.py (1.179 Zeilen)
**Zentrale NLP-Klasse**

```python
class HoloNLP:
    """Kombiniert alle NLP-Funktionen"""

    def analyze(self, text: str) -> Dict:
        return {
            "sentiment": ...,      # Stimmungsanalyse
            "entities": ...,       # Entitäten (Namen, Orte)
            "keywords": ...,       # Schlüsselwörter
            "relations": ...,      # Beziehungen
            "dialogue_act": ...,   # Sprechakt
        }
```

### Dialogue Acts
```python
class DialogueActClassifier:
    patterns = {
        "GREETING": [r'hallo|hi|hey|moin'],
        "FAREWELL": [r'tschüss|bye|auf wiedersehen'],
        "QUESTION": [r'\?$', r'^(wer|was|wo|wann|wie)'],
        "CONFIRM": [r'^(ja|genau|richtig)'],
        "DENY": [r'^(nein|ne|falsch)'],
        "THANKS": [r'danke|vielen dank'],
        "REQUEST": [r'kannst|könntest|bitte'],
    }
```

---

## Dialog-System

### 1. holo_dialogue_engine.py (2.267 Zeilen)
**Dialog-Steuerung**

**Dialog-Zustände:**
```python
class DialogueState(Enum):
    IDLE = "idle"
    GREETING = "greeting"
    ACTIVE = "active"
    DEEP_TALK = "deep_talk"
    FAREWELL = "farewell"
```

**Zustandsübergänge:**
```
IDLE → GREETING → ACTIVE → DEEP_TALK
  ↑                           │
  └───────── FAREWELL ←───────┘
```

---

### 2. holo_context_mind.py (2.477 Zeilen)
**Kontext-Verwaltung**

**Wichtige Klassen:**
| Klasse | Funktion |
|--------|----------|
| `TopicTracker` | Verfolgt Gesprächsthemen |
| `ContextStore` | Speichert Kontext |
| `ChatContextTracker` | Chat-Verlauf |

---

### 3. holo_message_analyzer.py (1.262 Zeilen)
**Nachrichtenanalyse**

**Response-Orchestrierung:**
```python
class ResponseOrchestrator:
    """Koordiniert Antwort-Generierung"""

    def orchestrate(self, message, context):
        # 1. Analysiere Nachricht
        # 2. Bestimme Priorität
        # 3. Wähle Response-Strategie
        # 4. Generiere Antwort
```

---

## Lernen & Wissen

### holo_database_system.py (7.735 Zeilen)
**Zentrale Datenbank**

**Datenbank-Typen:**
```python
class HoloDatabaseManager:
    """Verwaltet 17+ Datenbanken"""

    databases = {
        'memory': MemoryDatabase,       # Erinnerungen
        'knowledge': KnowledgeDatabase, # Wissen
        'emotions': EmotionsDatabase,   # Emotionen
        'media': MediaDatabase,         # Medien-Wissen
        'identity': IdentityDatabase,   # Selbstbild
        'calendar': CalendarDatabase,   # Termine
        'conversations': ConversationsDatabase,
        ...
    }
```

**Speicher-Kategorien:**
| Typ | Beschreibung |
|-----|--------------|
| Short-term | Letzte Stunden |
| Long-term | Dauerhaft |
| Episodic | Ereignisse |
| Semantic | Fakten |
| Procedural | Fähigkeiten |

---

## Antriebe & Bedürfnisse

### holo_drive_system.py (2.181 Zeilen)
**Motivationssystem**

**Antriebe (Drives):**
```python
@dataclass
class DriveState:
    curiosity: float = 0.7       # Neugier
    entertainment: float = 0.7   # Unterhaltung
    creativity: float = 0.7      # Kreativität
    social: float = 0.5          # Soziales
    mastery: float = 0.5         # Meisterschaft
    novelty: float = 0.5         # Neuheit
```

**Bedürfnisse (Needs):**
```python
@dataclass
class NeedState:
    missing: float = 0.0         # Vermissen
    loneliness: float = 0.0      # Einsamkeit
    contact_desire: float = 0.0  # Kontaktwunsch
    worry: float = 0.0           # Besorgnis
    boredom: float = 0.0         # Langeweile
```

**Bedürfnis-Kaskade:**
```
Zeit ohne Interaktion:
    5 Min  → Leichte Langeweile
    30 Min → Vermissen steigt
    2 Std  → Einsamkeit
    6 Std  → Sorge
```

---

## Wahrnehmung

### holo_perception.py (1.525 Zeilen)
**Allgemeine Wahrnehmung**

**Analyse-Typen:**
```python
class TextType(Enum):
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"
    TECHNICAL = "technical"
    EMOTIONAL = "emotional"

class ImageType(Enum):
    PHOTO = "photo"
    ARTWORK = "artwork"
    SCREENSHOT = "screenshot"
    MEME = "meme"
```

### holo_text_reader.py (960 Zeilen)
**Text-Analyse**

```python
class FactExtractor:
    """Extrahiert Fakten aus Text"""

    def extract_facts(self, text) -> List[ExtractedFact]:
        # Entitäten finden
        # Keywords extrahieren
        # Topic erkennen
```

### holo_audio.py (867 Zeilen)
**Audio-Analyse**

```python
class HoloAudio:
    def analyze(self, audio_path) -> AudioAnalysisResult:
        # Musik-Genre erkennen
        # Stimmung analysieren
        # Tempo bestimmen
```

---

## Steuerung & Management

### 1. holo_brain_controller.py (734 Zeilen)
**System-Steuerung**

**System-Status:**
```python
class SystemStatus(Enum):
    BOOTING = "booting"
    RUNNING = "running"
    HEALING = "healing"
    SHUTDOWN = "shutdown"
```

**Self-Healing:**
```python
class HoloBrainController:
    def self_heal(self):
        # Prüfe Module
        # Repariere Fehler
        # Starte neu wenn nötig
```

---

### 2. holo_ram_manager.py (807 Zeilen)
**RAM-Management**

```python
class HoloRAMManager:
    """
    Intelligentes RAM-Management:
    - LRU-Cache für häufige Daten
    - SD-Auslagerung für seltene Daten
    - Automatische Kompression
    """

    def store(self, key, data):
        # Prüfe RAM-Verfügbarkeit
        # Lagere ggf. auf SD aus

    def retrieve(self, key):
        # Hole aus RAM oder SD
```

---

### 3. holo_error_tracker.py (1.097 Zeilen)
**Fehler-Tracking**

```python
class HoloErrorTracker:
    """Zentrales Error-Management"""

    def track_error(self, error, context):
        # Logge Fehler
        # Analysiere Muster
        # Benachrichtige wenn kritisch
```

---

## Datenfluss

### Nachrichtenverarbeitung

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER MESSAGE FLOW                              │
└──────────────────────────────────────────────────────────────────┘

User Input
    │
    ▼
┌─────────────────┐
│ Message Analyzer │ → Bestimmt Typ, Intent, Entitäten
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Context Mind   │ ←── │  Topic Tracker  │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Cognitive Engine│ ←── │  Inner Life     │ (Stimmung, Energie)
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   Holo Brain    │ ←── │  Personality    │ (Stil, Körpersprache)
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  LLM / Router   │ → Generiert Antwort
└────────┬────────┘
         │
         ▼
    Response
```

### Zustandsänderungen

```
┌─────────────────────────────────────────────────────────────────┐
│                    STATE UPDATE FLOW                             │
└─────────────────────────────────────────────────────────────────┘

User Interaktion
    │
    ├──► Emotion Tracker  → Stimmung aktualisieren
    │
    ├──► Drive System     → Bedürfnisse reduzieren
    │         │
    │         └──► Loneliness ↓
    │         └──► Boredom ↓
    │         └──► Contact Desire ↓
    │
    ├──► Memory System    → Speichern
    │
    ├──► Learning System  → Lernen
    │
    └──► Self Awareness   → Beliefs aktualisieren
```

---

## Status-Übersicht

### Aktueller Systemstatus

| Komponente | Status | Details |
|------------|--------|---------|
| **Module** | ✅ 91/91 OK | Alle importieren erfolgreich |
| **Klassen** | ✅ 1279 | Alle definiert |
| **Methoden** | ✅ Gefixt | Fehlende Methoden hinzugefügt |
| **Config** | ✅ Gefixt | OrganicPresenceConfig korrigiert |

### Behobene Probleme
1. ✅ `EmotionTracker` - Fehlende Methoden hinzugefügt
2. ✅ `DriveState` - `regenerate_all()`, `items()` hinzugefügt
3. ✅ `DialogueActClassifier` - `get_expected_response_acts()` hinzugefügt
4. ✅ `OrganicPresenceConfig` - Lowercase Attribute hinzugefügt
5. ✅ `DreamSystem` / `SpontaneousThoughtSystem` - Config-Fehler behoben

### Optionale Abhängigkeiten (nicht installiert)
- `psutil` - Für Memory-Monitoring
- `paho-mqtt` - Für MQTT-Kommunikation
- `opencv` - Für Bildanalyse
- `PIL` - Für Bildverarbeitung

---

## Modul-Abhängigkeiten

```
holo_brain.py
    ├── holo_core_types.py
    ├── holo_consciousness.py
    │       ├── holo_inner_life.py
    │       └── holo_self_awareness.py
    ├── holo_personality.py
    │       └── holo_preferences.py
    ├── holo_cognitive_integration.py
    │       └── holo_cognitive_modules.py
    ├── holo_dialogue_engine.py
    │       └── holo_context_mind.py
    ├── holo_nlp_unified.py
    │       └── holo_nlp_algorithms.py
    ├── holo_drive_system.py
    ├── holo_database_system.py
    └── holo_brain_controller.py
```

---

## Zusammenfassung

**Holo** ist ein komplexes, modulares KI-Persönlichkeitssystem mit:

- **Bewusstsein**: Träume, spontane Gedanken, Ethik
- **Persönlichkeit**: Kemonomimi-Charakter, Vorlieben, Kreativität
- **Kognition**: Reasoning, Planung, Selbstbewusstsein
- **Emotion**: Stimmung, Bedürfnisse, Antriebe
- **Kommunikation**: NLP, Dialog-Management, Kontext-Tracking
- **Lernen**: Datenbanken, Wissen, Erinnerungen

Das System arbeitet zusammen durch:
1. Zentrale Orchestrierung via `holo_brain.py`
2. Event-basierte Kommunikation via `holo_wiring.py`
3. Geteilte Typen via `holo_core_types.py`
4. Persistente Speicherung via `holo_database_system.py`

---

*Dokumentation generiert am 2026-01-18*
*Holo System v15.0*
