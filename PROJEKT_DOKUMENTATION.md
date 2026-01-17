# HOLOCLOUDE - Vollständige Projektdokumentation

**Version:** 2.0
**Stand:** 2026-01-17
**Autor:** Holocloude Development Team

---

## Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [Systemarchitektur](#systemarchitektur)
3. [Modul-Übersicht](#modul-übersicht)
4. [Kernmodule im Detail](#kernmodule-im-detail)
5. [Datenbank-System](#datenbank-system)
6. [Konfiguration](#konfiguration)
7. [Installation & Inbetriebnahme](#installation--inbetriebnahme)
8. [API-Referenz](#api-referenz)
9. [Fehlerbehebung](#fehlerbehebung)

---

## Projektübersicht

### Was ist Holocloude?

Holocloude ist ein fortschrittliches KI-Persönlichkeitssystem, das eine virtuelle Begleiterin namens **Holo** simuliert - eine Kemonomimi-Charakter mit Wolfsohren und Schweif. Das System kombiniert:

- **Emotionale Intelligenz**: Komplexes Emotionssystem mit 6 Intensitätsstufen
- **Autonomes Denken**: Eigenständige Gedanken, Träume und Initiativen
- **Persönlichkeitsentwicklung**: Lernt aus Interaktionen und entwickelt Meinungen
- **Smart Home Integration**: Verbindung zu Home Assistant und IoT-Geräten
- **Multi-Modal**: Text, Sprache, Bilder und Videos

### Statistiken

| Metrik | Wert |
|--------|------|
| Python-Module | 94 |
| Codezeilen | ~240.000 |
| Klassen | 1.495 |
| Funktionen | 5.238 |
| Datenbanken | 17 (zentral) |

---

## Systemarchitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOLOCLOUDE SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   holo_brain    │◄──►│ holo_personality│◄──►│ holo_energy │ │
│  │  (Hauptmodul)   │    │   (Charakter)   │    │  (Energie)  │ │
│  └────────┬────────┘    └─────────────────┘    └─────────────┘ │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │holo_inner_life  │◄──►│holo_consciousness│◄──►│holo_learning│ │
│  │(Inneres Leben)  │    │  (Bewusstsein)  │    │  (Lernen)   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │holo_database    │◄──►│   holo_config   │◄──►│ smart_llm   │ │
│  │   (Speicher)    │    │ (Konfiguration) │    │  (LLM API)  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Modul-Übersicht

### Kern-Module (Essential)

| Modul | Beschreibung | Abhängigkeiten |
|-------|--------------|----------------|
| `holo_brain.py` | Haupt-Koordinator, verarbeitet Nachrichten | Alle anderen Module |
| `holo_brain_core.py` | Basis-Funktionalität des Gehirns | holo_config, holo_database |
| `holo_personality.py` | Persönlichkeit, Emotionen, Ausdrücke | holo_core_types |
| `holo_config.py` | Zentrale Konfiguration | - |
| `holo_core_types.py` | Gemeinsame Datentypen (Enums, Dataclasses) | - |

### Emotions- & Bewusstseins-Module

| Modul | Beschreibung |
|-------|--------------|
| `holo_consciousness.py` | Bewusstsein, Selbstreflexion, Träume |
| `holo_inner_life.py` | Inneres Leben, Autonomie, Beziehungen |
| `holo_emotional_complexity.py` | Komplexe Emotionen, negative Verhaltensweisen |
| `holo_energy_system.py` | Energie, Müdigkeit, Stimmung |
| `holo_preferences.py` | Vorlieben und Präferenzen |

### Lern- & Wissens-Module

| Modul | Beschreibung |
|-------|--------------|
| `holo_learning.py` | Haupt-Lernsystem |
| `holo_knowledge_influence.py` | Wissen beeinflusst Persönlichkeit |
| `holo_context_mind.py` | Kontextverständnis, Topic-Tracking |
| `holo_smart_understanding.py` | Intelligente Nachrichtenverarbeitung |
| `holo_autonomous_thinking.py` | Autonomes Denken |

### Interaktions-Module

| Modul | Beschreibung |
|-------|--------------|
| `holo_dialogue_engine.py` | Dialog-Management |
| `holo_voice_interface.py` | Spracheingabe/-ausgabe |
| `holo_speech_engine.py` | Text-to-Speech |
| `holo_perception.py` | Wahrnehmung (Lesen, Sehen) |
| `holo_perception_unified.py` | Vereinheitlichte Wahrnehmung |

### Smart Home & Geräte

| Modul | Beschreibung |
|-------|--------------|
| `holo_device_agent.py` | Geräte-Agent |
| `holo_device_receiver.py` | MQTT-Empfänger für Geräte |
| `pi_holo_interface.py` | Raspberry Pi Interface |
| `pi_control_v8_AI-extendet.py` | Erweiterte Pi-Steuerung mit KI |

### Medien-Module

| Modul | Beschreibung |
|-------|--------------|
| `holo_media_integration.py` | Medien-Integration |
| `holo_media_discovery.py` | Medien-Entdeckung |
| `holo_media_index.py` | Medien-Indexierung |
| `holo_media_knowledge.py` | Medien-Wissen (Anime, Games, etc.) |
| `holo_music_experience.py` | Musik-Erlebnis |
| `holo_video.py` | Video-Verarbeitung |

### Datenbank & Speicher

| Modul | Beschreibung |
|-------|--------------|
| `holo_database_system.py` | Zentrales Datenbank-Management |
| `holo_db_migrations.py` | Datenbank-Migrationen |
| `holo_ram_manager.py` | RAM-Verwaltung |

### Hilfs-Module

| Modul | Beschreibung |
|-------|--------------|
| `holo_error_tracker.py` | Fehler-Tracking |
| `holo_error_handling.py` | Fehlerbehandlung |
| `holo_health_checks.py` | Gesundheits-Checks |
| `holo_tester.py` | System-Tester (v7.0) |
| `holo_robust_imports.py` | Robuste Imports |

---

## Kernmodule im Detail

### holo_brain.py - Das Gehirn

Das zentrale Modul, das alle anderen koordiniert.

**Hauptklasse:** `HoloBrain`

```python
from holo_brain import HoloBrain

brain = HoloBrain()
response = brain.process_message("Hallo Holo!")
```

**Hauptfunktionen:**
- `process_message(text)` - Verarbeitet Benutzernachricht
- `process_message_streaming(text)` - Streaming-Antwort
- `_build_system_prompt()` - Erstellt System-Prompt für LLM
- `_get_integrated_context()` - Sammelt Kontext aus allen Modulen

### holo_personality.py - Die Persönlichkeit

Definiert Holos Charakter, Emotionen und Ausdrucksweise.

**Wichtige Klassen:**

```python
from holo_personality import (
    KemonomimiBodyLanguage,  # Ohren/Schweif-Bewegungen
    EmotionLevels,           # 6 Intensitätsstufen
    InitiativeMessageGenerator,  # Proaktive Nachrichten
)
```

**Emotionssystem mit 6 Stufen:**
- `minimal` (0.0-0.17) - Kaum spürbar
- `leicht` (0.17-0.33) - Leicht spürbar
- `mittel` (0.33-0.50) - Deutlich
- `stark` (0.50-0.67) - Stark
- `sehr_stark` (0.67-0.83) - Sehr stark
- `extrem` (0.83-1.0) - Überwältigend

**Ohren/Schweif-Reaktionen:**
```python
# Beispiel für verschiedene Intensitäten
KemonomimiBodyLanguage.get_ear_action("happy", 0.1)  # *Ohren heben sich leicht*
KemonomimiBodyLanguage.get_ear_action("happy", 0.9)  # *Ohren vibrieren vor Freude*
KemonomimiBodyLanguage.get_tail_action("happy", 0.5) # *Schweif wedelt*
```

### holo_inner_life.py - Das Innere Leben

Koordiniert Holos autonomes Verhalten.

**Hauptklassen:**
- `HoloAutonomy` - Selbstständigkeit
- `HoloAutonomyEngine` - Erweiterte Autonomie
- `InitiativeCoordinator` - Eigeninitiative
- `RelationshipTracker` - Beziehungs-Tracking
- `OpinionSystem` - Meinungsbildung

```python
from holo_inner_life import create_autonomy, create_autonomy_engine

# Einfache Autonomie
autonomy = create_autonomy()

# Erweiterte Autonomie mit Topic-Tracking
engine = create_autonomy_engine()
message = engine.update(energy=0.8, boredom=0.3)
```

### holo_consciousness.py - Das Bewusstsein

Selbstreflexion, Träume und tiefes Denken.

**Wichtige Klassen:**
- `ThoughtGenerator` - Gedanken-Erzeugung
- `DaydreamEngine` - Tagträume
- `PersonalGrowth` - Persönliches Wachstum

---

## Datenbank-System

### Zentrale Datenbanken (~/holo_data/)

| Datenbank | Inhalt |
|-----------|--------|
| `holo_memory.db` | Episoden, Träume, Erinnerungen |
| `holo_emotions.db` | Emotionen, Stimmungen |
| `holo_identity.db` | Persönlichkeit, Beliefs |
| `holo_language.db` | Sprachmuster, Stil |
| `holo_knowledge.db` | Fakten, Interessen |
| `holo_media.db` | Anime, Games, Musik |
| `holo_news.db` | News, Artikel |
| `holo_conversations.db` | Chat-History |
| `holo_activity.db` | Aktivitäten |
| `holo_productivity.db` | Todos, Timer |
| `holo_environment.db` | Wetter, Feiertage |
| `holo_network.db` | Geräte, NAS |
| `holo_presence.db` | User-Anwesenheit |
| `holo_home.db` | Home Assistant |
| `holo_calendar.db` | Termine |
| `holo_predictions.db` | Q-Learning, Patterns |
| `holo_state.db` | Runtime States |

### Verwendung

```python
from holo_database_system import HoloDatabaseManager

db = HoloDatabaseManager()

# Erinnerung speichern
db.memory.store_episode(
    content="User hat von seinem neuen Job erzählt",
    emotion="happy",
    importance=0.8
)

# Emotion loggen
db.emotions.log_emotion(
    category="joy",
    intensity=0.7,
    trigger="User shared good news"
)
```

### Dezentrale Speicherorte

Einige Module haben zusätzliche lokale Speicher:

| Pfad | Inhalt |
|------|--------|
| `data/` | Lokale JSON-Dateien für Module |
| `~/holo_*.json` | State-Dateien im Home-Verzeichnis |

---

## Konfiguration

### config.json

Hauptkonfigurationsdatei im Projektverzeichnis:

```json
{
  "llm": {
    "model": "gpt-4",
    "api_key": "sk-...",
    "temperature": 0.7
  },
  "storage": {
    "db_file": "holo_brain_v12.db",
    "data_dir": "~/holo_data"
  },
  "brain": {
    "personality_name": "Holo",
    "max_context_tokens": 8000
  },
  "home_assistant": {
    "url": "http://homeassistant.local:8123",
    "token": "..."
  }
}
```

### Konfiguration laden

```python
from holo_config import get_config, load_config

# Einzelnen Wert holen
model = get_config("llm.model", default="gpt-4")

# Gesamte Config laden
config = load_config()
```

---

## Installation & Inbetriebnahme

### Voraussetzungen

- Python 3.10+
- SQLite3
- Optional: CUDA für GPU-Beschleunigung

### Installation

```bash
# Repository klonen
git clone https://github.com/user/holocloude2.git
cd holocloude2

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Konfiguration erstellen
cp config.example.json config.json
# config.json mit API-Keys füllen
```

### Erster Start

```bash
# System testen
python holo_tester.py --quick

# Vollständiger Test
python holo_tester.py --all

# Holo starten
python holo_brain.py
```

### System-Test

```bash
# Schneller Import-Test
python holo_tester.py --quick

# Vollständiger Test
python holo_tester.py --all

# Einzelne Tests
python holo_tester.py --runtime      # Runtime-Tests
python holo_tester.py --integration  # Integration-Tests
python holo_tester.py --security     # Sicherheits-Audit
```

---

## API-Referenz

### HoloBrain

```python
class HoloBrain:
    def __init__(self, config_path: str = None)
    def process_message(self, text: str) -> str
    def process_message_streaming(self, text: str) -> Generator[str]
    def get_status(self) -> Dict
```

### HoloPersonality

```python
class KemonomimiBodyLanguage:
    @classmethod
    def get_ear_action(cls, mood: str, intensity: float = 0.5) -> str

    @classmethod
    def get_tail_action(cls, mood: str, intensity: float = 0.5) -> str

    @classmethod
    def get_combined_action(cls, mood: str, intensity: float = 0.5) -> str

    @classmethod
    def intensity_to_level(cls, intensity: float) -> str
```

### HoloDatabaseManager

```python
class HoloDatabaseManager:
    def __init__(self, data_dir: Path = None)

    # Sub-Manager
    memory: MemoryDatabase
    emotions: EmotionsDatabase
    knowledge: KnowledgeDatabase
    conversations: ConversationsDatabase
    media: MediaDatabase
    # ... weitere
```

---

## Fehlerbehebung

### Häufige Probleme

#### ImportError bei Modulen

```bash
# Imports testen
python holo_tester.py --quick

# Wenn Fehler: Abhängigkeiten prüfen
pip install -r requirements.txt
```

#### Datenbank-Fehler

```bash
# Datenbank-Schema prüfen
python holo_tester.py --db

# Migrationen ausführen
python holo_db_migrations.py
```

#### Konfiguration nicht gefunden

```bash
# Prüfen ob config.json existiert
ls config.json

# Beispiel kopieren
cp config.example.json config.json
```

### Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

Bei Problemen:
1. `python holo_tester.py --all` ausführen
2. Fehlerausgabe analysieren
3. Issue auf GitHub erstellen

---

## Lizenz

MIT License - Siehe LICENSE Datei

---

*Dokumentation erstellt am 2026-01-17*
