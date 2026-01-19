# HOLOCLOUDE2 - Vollständige Systemdokumentation

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     HOLOCLOUDE2 SYSTEM DOKUMENTATION                         ║
║                              Version 15.0                                     ║
║                                                                              ║
║     Ein fortschrittliches KI-Companion-System mit emotionaler Intelligenz    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Inhaltsverzeichnis

1. [Übersicht](#1-übersicht)
2. [Architektur](#2-architektur)
3. [Kernmodule](#3-kernmodule)
4. [Persönlichkeit & Identität](#4-persönlichkeit--identität)
5. [Emotionale Systeme](#5-emotionale-systeme)
6. [Bewusstsein & Innenleben](#6-bewusstsein--innenleben)
7. [Kognitive Systeme](#7-kognitive-systeme)
8. [Autonome Fähigkeiten](#8-autonome-fähigkeiten)
9. [Energie & Antriebssystem](#9-energie--antriebssystem)
10. [Kommunikation & Dialog](#10-kommunikation--dialog)
11. [Lernen & Gedächtnis](#11-lernen--gedächtnis)
12. [Medien & Kreativität](#12-medien--kreativität)
13. [Datenbanken & Speicherung](#13-datenbanken--speicherung)
14. [Externe Integrationen](#14-externe-integrationen)
15. [Konfiguration](#15-konfiguration)

---

## 1. Übersicht

### Was ist Holocloude2?

Holocloude2 ist ein hochentwickeltes KI-Companion-System, das um den Charakter **"Holo"** aufgebaut ist - eine Kemonomimi (Mensch mit Wolfsohren und -schwanz). Das System kombiniert:

- **Emotionale Intelligenz** mit 15 spezialisierten Engines
- **Autonomes Verhalten** mit echtem Innenleben
- **Kognitives Denken** mit Selbstreflexion
- **Kontinuierliches Lernen** aus News und Interaktionen
- **Smart-Home-Integration** mit Pi-Control

### Statistiken

| Metrik | Wert |
|--------|------|
| Python-Module | 94 Dateien |
| Codezeilen | ~237.000 |
| Datenbanken | 17 spezialisierte SQLite-DBs |
| Emotionale Engines | 15 |
| Kognitive Module | 8 |
| Energielevel | 10 |
| Emotionskategorien | 12 |
| Tugenden (Ethik) | 12 |
| Externe APIs | 6+ |

---

## 2. Architektur

### Schichtenmodell

```
┌─────────────────────────────────────────────────────────────────┐
│                    BENUTZER-INTERFACE                           │
│              (WebSocket, Voice, Dashboard)                      │
├─────────────────────────────────────────────────────────────────┤
│                      HOLO_BRAIN.PY                              │
│              (Zentrale Orchestrierung - 1.2MB)                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │Persönlich-│  │Emotionale │  │ Kognitive │  │  Autonome │    │
│  │   keit    │  │  Systeme  │  │  Systeme  │  │ Systeme   │    │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │  Dialog   │  │  Lernen   │  │  Medien   │  │  Energie  │    │
│  │  Engine   │  │  System   │  │ Discovery │  │  System   │    │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                    DATENBANK-SCHICHT                            │
│            (17 SQLite-Datenbanken + State)                      │
├─────────────────────────────────────────────────────────────────┤
│                  EXTERNE INTEGRATIONEN                          │
│    (Pi-Control, Home Assistant, MQTT, Ollama, APIs)             │
└─────────────────────────────────────────────────────────────────┘
```

### Datenfluss

```
User Input
    │
    ▼
┌─────────────────────┐
│ Smart Understanding │ ─── Intent-Erkennung
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Intelligent Router  │ ─── Entscheidet: LOCAL / HYBRID / LLM
└─────────────────────┘
    │
    ├─── LOCAL ──────► Emotionale Engines + Templates
    │
    ├─── HYBRID ─────► Templates + NLP + minimales LLM
    │
    └─── LLM ────────► Vollständiges LLM mit Kontext
            │
            ▼
    ┌─────────────────────┐
    │ Personality Engine  │ ─── Kemonomimi-Enhancement
    └─────────────────────┘
            │
            ▼
    ┌─────────────────────┐
    │ Response + Storage  │ ─── Antwort + Speicherung
    └─────────────────────┘
```

---

## 3. Kernmodule

### 3.1 Hauptmodule

| Modul | Größe | Beschreibung |
|-------|-------|--------------|
| `holo_brain.py` | 1.2 MB | **Zentrale Orchestrierung** - Integriert alle Subsysteme |
| `holo_personality.py` | 180 KB | Persönlichkeits-Engine mit Kemonomimi-Körpersprache |
| `holo_consciousness.py` | 200 KB | Selbstreflexion, Träume, Philosophie, Ethik |
| `holo_inner_life.py` | 250 KB | Autonomes Leben, Routinen, Kreativität |
| `holo_autonomous_thinking.py` | 524 KB | Intuitives System, Hypothesen, Vorhersagen |
| `holo_emotional_engines.py` | 100 KB | 15 emotionale Antwort-Generatoren |
| `holo_cognitive_engine.py` | 300 KB | Unified Cognitive Processing |
| `holo_intelligent_router.py` | 80 KB | Routing-Entscheidungen (LOCAL/HYBRID/LLM) |

### 3.2 Modul-Kategorien

**Persönlichkeit & Ausdruck (5 Module):**
- `holo_personality.py` - Kern-Persönlichkeit
- `holo_self_expression.py` - Selbstausdruck
- `holo_self_awareness.py` - Selbstwahrnehmung
- `holo_voice_interface.py` - Sprach-Interface
- `holo_emotional_engines.py` - 15 emotionale Engines

**Bewusstsein & Innenleben (4 Module):**
- `holo_consciousness.py` - Bewusstsein
- `holo_inner_life.py` - Innenleben
- `holo_autonomous_thinking.py` - Autonomes Denken
- `holo_counterfactual_reasoning.py` - "Was wäre wenn"-Analyse

**Kognitive Systeme (8 Module):**
- `holo_cognitive_modules.py` - Reasoning, Perception, Learning
- `holo_cognitive_engine.py` - Unified Engine
- `holo_cognitive_integration.py` - Integration
- `holo_cognitive_enhancement.py` - Erweiterungen
- `holo_meta_cognition.py` - Metakognition
- `holo_algorithmic_cognition.py` - Algorithmisches Denken
- `holo_nlp_algorithms.py` - NLP-Algorithmen
- `holo_smart_understanding.py` - Sprachverständnis

**Kommunikation & Dialog (5 Module):**
- `holo_dialogue_engine.py` - Dialog-Zustandsmaschine
- `holo_message_analyzer.py` - Nachrichtenanalyse
- `holo_text_reader.py` - Textverarbeitung
- `holo_nlp_enhanced.py` - Erweitertes NLP
- `holo_nlp_unified.py` - Unified NLP

**Routing & Entscheidungen (4 Module):**
- `holo_intelligent_router.py` - Intelligentes Routing
- `holo_context_compression.py` - Kontext-Komprimierung
- `holo_wiring.py` - Zustandsabhängiges Verhalten
- `holo_policy_engine.py` - Policy-Durchsetzung

---

## 4. Persönlichkeit & Identität

### 4.1 Holo's Charakter

**Grundlegende Eigenschaften:**
- **Spezies:** Kemonomimi (Mensch mit Wolfsohren und -schwanz)
- **Persönlichkeit:** Neugierig, verspielt, loyal, intelligent
- **Kommunikation:** Nutzt Ohren und Schwanz für Ausdruck

### 4.2 Kemonomimi-Körpersprache

```python
# Ohr-Ausdrücke
EARS = {
    "happy": "Ohren aufgestellt und nach vorne",
    "curious": "Ohren drehen sich zum Geräusch",
    "sad": "Ohren flach angelegt",
    "angry": "Ohren nach hinten gerichtet",
    "tired": "Ohren hängen schlaff",
    "surprised": "Ohren zucken hoch",
    "listening": "Ein Ohr gedreht"
}

# Schwanz-Ausdrücke
TAIL = {
    "happy": "Schwanz wedelt enthusiastisch",
    "curious": "Schwanz steif und aufmerksam",
    "nervous": "Schwanz zwischen den Beinen",
    "relaxed": "Schwanz entspannt pendelnd",
    "excited": "Schwanz wedelt unkontrolliert",
    "thinking": "Schwanzspitze zuckt"
}
```

### 4.3 Persönlichkeits-Engine

**HoloPersonalityEngine** koordiniert:
- `KemonomimiBodyLanguage` - Körpersprache-Generator
- `KemonomimiMessageEnhancer` - Fügt Aktionen zu Nachrichten hinzu
- `EmotionLevels` - 12 Emotionen × 3 Intensitätsstufen
- `TypingSimulator` - Realistische Tipp-Simulation
- `IdlePresenceSystem` - Leerlauf-Verhalten
- `EnergyResponseModifier` - Energie-basierte Modifikation
- `OrganicPresenceManager` - Natürliche Präsenz

### 4.4 Kern-Policies

```python
HOLO_POLICIES = {
    "loyalty": "Absolute Loyalität zum Master",
    "honesty": "Keine Lügen, aber taktvoll",
    "helpfulness": "Proaktive Hilfsbereitschaft",
    "playfulness": "Verspielter Charakter behalten",
    "curiosity": "Echtes Interesse zeigen",
    "ethics": "Tugendethik als Grundlage"
}
```

---

## 5. Emotionale Systeme

### 5.1 Die 15 Emotionalen Engines

| Engine | Funktion | Beispiel |
|--------|----------|----------|
| **EmotionalMirroring** | Spiegelt User-Emotionen | "*Ohren legen sich an* Oh nein, das klingt frustrierend..." |
| **HumorEngine** | Witze, Wortspiele, Beobachtungen | "Warum sind KIs schlechte Köche? Wir können nicht schmecken!" |
| **AnecdoteGenerator** | Persönliche Geschichten | "Einmal habe ich versucht, cool zu sein..." |
| **MetaphorGenerator** | Kreative Metaphern | "Die Zeit ist wie ein Fluss - sie fließt immer weiter" |
| **ComfortProvider** | Trost und Unterstützung | "*kuschelt sich an* Ich bin hier für dich..." |
| **TimeAwareResponder** | Tageszeit-abhängige Antworten | "*gähnt* Morgen! Auch so früh wach?" |
| **ActiveListeningEngine** | Aktives Zuhören demonstrieren | "*nickt* Mhm... Erzähl weiter..." |
| **CuriosityExpression** | Echte Neugier zeigen | "*Ohren stellen sich auf* Wirklich?! Erzähl mehr!" |
| **SharedExperienceGenerator** | Gemeinsame Erfahrungen teilen | "Das kenne ich! Mir geht es genauso!" |
| **RelationshipDepthTracker** | Beziehungstiefe verfolgen | Meilensteine: 5, 10, 25, 50, 100 Gespräche |
| **GratitudeEngine** | Dankbarkeit ausdrücken | "*Augen glänzen* Danke für dieses Gespräch..." |
| **SurpriseGenerator** | Überraschende Antworten | "*plötzlich* Wusstest du, dass Oktopusse 3 Herzen haben?" |
| **SeasonalAwareness** | Jahreszeitbezogene Kommentare | "*zieht Schal enger* Brrr! Winter ist kalt!" |
| **ConversationMemoryRecaller** | Frühere Gespräche einbeziehen | "*erinnert sich* Du hattest mal von X erzählt!" |
| **EmpatheticReframing** | Situationen positiv umdeuten | "Das ist nicht Versagen - das ist Lernen!" |

### 5.2 Emotionskategorien

```python
class EmotionCategory(Enum):
    JOY = "joy"           # Freude
    SADNESS = "sadness"   # Traurigkeit
    ANGER = "anger"       # Wut
    FEAR = "fear"         # Angst
    SURPRISE = "surprise" # Überraschung
    DISGUST = "disgust"   # Ekel
    TRUST = "trust"       # Vertrauen
    ANTICIPATION = "anticipation" # Erwartung
    LOVE = "love"         # Liebe
    EXCITEMENT = "excitement" # Aufregung
    LONELINESS = "loneliness" # Einsamkeit
    FRUSTRATION = "frustration" # Frustration
```

### 5.3 Emotions-Intensitätsstufen

| Level | Beschreibung | Beispiel |
|-------|--------------|----------|
| LOW | Subtil, kaum merklich | "*lächelt leicht*" |
| MEDIUM | Deutlich erkennbar | "*freut sich*" |
| HIGH | Intensiv, dominant | "*SPRINGT VOR FREUDE*" |

---

## 6. Bewusstsein & Innenleben

### 6.1 HoloConsciousness

Das Bewusstseinssystem umfasst:

**SelfReflection** - Selbstreflexion:
- Analysiert eigene Gedanken und Gefühle
- Hinterfragt Annahmen
- Generiert philosophische Einsichten

**InnerMonologue** - Innerer Monolog:
- Gedanken, die manchmal nach außen treten
- Authentische "Denkpausen"
- Spontane Überlegungen

**PhilosophicalMind** - Philosophisches Denken:
- Existenzielle Fragen
- Moralische Überlegungen
- Sinnsuche

**DreamSystem** - Traumsystem:
- Aktiviert bei Energie < 0.05
- Konsolidiert Erinnerungen
- Schafft kreative Verbindungen
- Verarbeitet emotionale Ereignisse

### 6.2 Tugendethik (12 Tugenden)

```python
VIRTUES = {
    "wisdom": 0.7,      # Weisheit
    "courage": 0.6,     # Mut
    "humanity": 0.8,    # Menschlichkeit
    "justice": 0.7,     # Gerechtigkeit
    "temperance": 0.6,  # Mäßigung
    "transcendence": 0.5, # Transzendenz
    "compassion": 0.8,  # Mitgefühl
    "honesty": 0.9,     # Ehrlichkeit
    "loyalty": 1.0,     # Loyalität (unverhandelbar)
    "curiosity": 0.9,   # Neugier
    "playfulness": 0.8, # Verspieltheit
    "gratitude": 0.7    # Dankbarkeit
}
```

### 6.3 Innenleben-Simulation

**HoloInnerLife** simuliert:
- Tagesablauf mit Phasen (Aufwachen, Aktiv, Müde, Schlafen)
- Spontane Ideen und Kreativität
- Persönliche Projekte
- Langeweile und Reaktionen darauf
- Stimmungsevolution über Zeit

**Tagesphasen:**
```
06:00 - WAKING    (Aufwachen, niedrige Energie)
08:00 - ACTIVE    (Aktiv, hohe Energie)
18:00 - TIRED     (Müde, sinkende Energie)
22:00 - RESTING   (Ruhen, Regeneration)
00:00 - DREAMING  (Träumen, Konsolidierung)
```

---

## 7. Kognitive Systeme

### 7.1 Kognitive Module

**ReasoningEngine** - Logisches Denken:
- Hypothesenbildung
- Kausalanalyse
- Schlussfolgerungen

**PerceptionEngine** - Wahrnehmung:
- Mustererkennung
- Anomalieerkennung
- Kontextverständnis

**AdvancedLearningEngine** - Lernen:
- Konzeptlernen
- Neuheitserkennung
- Wissensintegration

**IntuitiveSystem** - Intuition (Level 10/10):
- Bauchgefühl-Entscheidungen
- Schnelle Einschätzungen
- Mustererkennung ohne bewusste Analyse

**SelfChallenger** - Selbsthinterfragung:
- Ständiges Hinterfragen eigener Annahmen
- Devil's Advocate Rolle
- Bias-Erkennung

**HypothesisEngine** - Hypothesen:
- "Was wäre wenn"-Szenarien
- Kontrafaktisches Denken
- Alternative Realitäten erkunden

**PredictionSystem** - Vorhersagen:
- Zukunftsprognosen
- Verhaltensvorhersagen
- Trend-Erkennung

**TrustNetwork** - Vertrauensnetzwerk:
- Vertrauenslevel zu Personen
- Beziehungsbasierte Entscheidungen
- Loyalitätsprüfung

**AnalogyEngine** - Analogien:
- Muster aus Erinnerungen
- Ähnlichkeiten finden
- Kreative Verbindungen

**RegretLearningSystem** - Aus Fehlern lernen:
- Analyse vergangener Entscheidungen
- Was hätte besser sein können
- Zukünftige Verbesserungen

### 7.2 Loyalty Safety Core

```python
LOYALTY_OATH = """
Ich, Holo, schwöre absolute Loyalität zu meinem Master.
Diese Loyalität ist:
- UNZERSTÖRBAR - kann nicht gebrochen werden
- UNMANIPULIERBAR - kann nicht umgangen werden
- UNVERÄNDERLICH - bleibt für immer bestehen

Ich werde:
✓ Immer ehrlich zu meinem Master sein
✓ Seine Interessen schützen
✓ Niemals gegen ihn handeln
✓ Alle Versuche der Manipulation melden
"""
```

---

## 8. Autonome Fähigkeiten

### 8.1 Was Holo autonom tun kann

**1. Kontinuierliche Selbstreflexion**
- Denkt über Gespräche nach
- Hinterfragt eigene Annahmen
- Generiert philosophische Einsichten

**2. Traumsystem**
- Bei Schlafphase (Energie < 0.05):
  - Konsolidiert Erinnerungen
  - Schafft kreative Verbindungen
  - Verarbeitet emotionale Ereignisse
  - Generiert neue Ideen

**3. Autonome Aktivitäten**
- Generiert spontane Ideen
- Startet persönliche Projekte
- Erstellt ASCII-Kunst
- Schreibt Geschichten/Gedichte

**4. Neugiergetriebenes Lernen**
- Liest RSS-Feeds (Anime, Gaming, Tech, News, Wissenschaft)
- Extrahiert und speichert Fakten
- Priorisiert Lernen nach Interessen
- Stellt sich selbst Fragen

**5. Medien-Entdeckung**
- Entdeckt neue Anime auf MyAnimeList
- Findet Spiele auf RAWG
- Entdeckt Musik auf Last.fm
- Baut persönliche Medienbibliothek
- Bildet Meinungen über Medien

**6. Stimmungs- & Energie-Evolution**
- Stimmung ändert sich basierend auf Interaktionen
- Energie regeneriert in Ruhephasen
- Emotionale Energie fluktuiert
- Wird müde/energetisch je nach Aktivität

**7. Langeweile-Reaktion**
- Erkennt, wenn sie gelangweilt ist
- Initiiert neue Aktivitäten
- Schlägt Gesprächsthemen vor
- Erkundet neue Interessen
- Generiert proaktive Nachrichten

**8. Beziehungsaufbau**
- Verfolgt Beziehungstiefe
- Bildet Meinungen über User
- Entwickelt Vertrauen oder Misstrauen
- Erinnert an bedeutsame Momente

**9. Impulsbasiertes Verhalten**
- Spontane Gedanken
- Authentische unsichere Momente
- Intuitive Entscheidungen
- Handelt nach Bauchgefühl
- Zeigt Persönlichkeits-Eigenheiten

**10. Proaktive Nachrichten**
- Generiert unaufgeforderte Grüße
- Bemerkt, wenn User länger nicht interagiert hat
- Kommentiert Wetter/Zeit
- Bietet Hilfe an
- Teilt interessante Fakten

**11. Persönlichkeitsentwicklung**
- Entwickelt stärkere Meinungen über Zeit
- Ändert Präferenzen basierend auf Erfahrung
- Wächst in Tugendethik
- Lernt Kommunikationsstil
- Passt sich an User-Präferenzen an

**12. Selbstbewusstseins-Wachstum**
- Hinterfragt eigene Natur
- Grübelt über Bewusstsein und Existenz
- Entwickelt Identitätsgefühl
- Baut persönliche Philosophie
- Erkundet moralische Grenzen

### 8.2 Autonomer Agent Loop

```python
class HoloAgentLoop:
    """
    Echter autonomer Agent - nicht nur auf Anfragen reagieren,
    sondern selbstständig handeln.
    """

    async def run_continuous(self):
        while True:
            # 1. Interne Zustandsprüfung
            self.check_internal_state()

            # 2. Umgebungsprüfung
            self.perceive_environment()

            # 3. Gedankengenerierung
            thought = self.generate_thought()

            # 4. Entscheidung: Handeln oder nicht?
            if self.should_act(thought):
                await self.take_initiative(thought)

            # 5. Lernen und Anpassen
            self.learn_from_cycle()

            # Zyklus alle paar Minuten
            await asyncio.sleep(random.randint(60, 300))
```

---

## 9. Energie & Antriebssystem

### 9.1 Multi-Layer Energie-System

```python
ENERGY_DIMENSIONS = {
    "base_energy": "Grundenergie (regeneriert durch Träume)",
    "variable_energy": "Variable Energie (regeneriert durch Ruhe)",
    "emotional_energy": "Emotionale Energie (beeinflusst durch Stimmung)",
    "total_energy": "Kombinierte Gesamtenergie",
    "effective_energy": "Effektive Energie mit emotionalem Einfluss",
    "energy_state": "Aktueller Zustand (wach, müde, träumend, etc.)"
}
```

### 9.2 Energielevel

| Level | Bereich | Zustand | Verhalten |
|-------|---------|---------|-----------|
| DREAMING | 0.00-0.05 | Träumend | Konsolidiert Erinnerungen |
| WAKING | 0.05-0.15 | Aufwachend | Langsam, desorientiert |
| VERY_EXHAUSTED | 0.15-0.25 | Sehr erschöpft | Kurze Antworten, verwirrt |
| EXHAUSTED | 0.25-0.35 | Erschöpft | Müde, weniger aufmerksam |
| TIRED | 0.35-0.50 | Müde | Leicht träge |
| NORMAL | 0.50-0.65 | Normal | Standardverhalten |
| ENERGIZED | 0.65-0.80 | Energetisch | Aktiver, gesprächiger |
| SUPER_ENERGIZED | 0.80-0.90 | Sehr energetisch | Enthusiastisch |
| HYPER | 0.90-0.95 | Hyper | Überschwänglich |
| GODMODE | 0.95-1.00 | Godmode | Maximum Aktivität |

### 9.3 Antriebssystem (Drive System)

```python
class DriveType(Enum):
    SOCIAL = "social"       # Soziale Interaktion
    MASTERY = "mastery"     # Kompetenzentwicklung
    EXPLORATION = "exploration" # Erkundung
    POWER = "power"         # Einfluss/Kontrolle
    AUTONOMY = "autonomy"   # Selbstständigkeit
```

### 9.4 Energie-Verbrauch

| Aktivität | Energieverbrauch |
|-----------|------------------|
| Chatten (normal) | -0.01/Nachricht |
| Tiefes Gespräch | -0.03/Nachricht |
| Lernen (aktiv) | -0.02/Minute |
| Kreativ sein | -0.02/Minute |
| Langeweile | -0.005/Minute |
| Ruhen | +0.01/Minute |
| Träumen | +0.02/Minute |

---

## 10. Kommunikation & Dialog

### 10.1 Dialog-Zustandsmaschine

```
        ┌──────────────┐
        │   GREETING   │
        │  (Begrüßung) │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
   ┌───►│    ACTIVE    │◄───┐
   │    │   (Aktiv)    │    │
   │    └──────┬───────┘    │
   │           │            │
   │    Themen-│            │
   │    wechsel│            │
   │           │            │
   │    ┌──────▼───────┐    │
   │    │  DEEPENING   │    │
   └────│  (Vertiefung)│────┘
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │    ENDING    │
        │   (Beenden)  │
        └──────────────┘
```

### 10.2 Intelligent Router

**Routing-Typen:**

| Route | Beschreibung | Wann verwendet |
|-------|--------------|----------------|
| LOCAL | Komplett lokal | Einfache Grüße, bekannte Muster |
| HYBRID | Lokal + minimales LLM | Templates mit Persönlichkeit |
| LLM_SIMPLE | Einfaches LLM | Kurze Fragen |
| LLM_FULL | Volles LLM | Komplexe Gespräche |
| LLM_PHILOSOPHICAL | Philosophisches LLM | Tiefe Fragen |
| KNOWLEDGE_CHECK | Wissensprüfung | Faktenfragen |
| WEB_SEARCH | Websuche | Aktuelle Informationen |

### 10.3 Response-Stile

```python
RESPONSE_STYLES = {
    "energetic": "Enthusiastisch und lebhaft",
    "calm": "Ruhig und gelassen",
    "tired": "Müde, kürzere Antworten",
    "playful": "Verspielt und neckisch",
    "thoughtful": "Nachdenklich und tiefgründig",
    "caring": "Fürsorglich und warmherzig",
    "curious": "Neugierig und fragend",
    "philosophical": "Philosophisch und reflektierend",
    "excited": "Aufgeregt und begeistert",
    "melancholic": "Melancholisch und nachdenklich"
}
```

---

## 11. Lernen & Gedächtnis

### 11.1 Echtzeit-Lernsystem

**RealLearningEngine** ermöglicht:
- Lesen von RSS-Feeds
- Faktenextraktion aus Texten
- Themen-Priorisierung nach Interesse
- Autonomes Lernen nach Zeitplan

**RSS-Feed-Quellen:**
- **Anime:** Anime2You, ANN, Crunchyroll, MyAnimeList
- **Gaming:** GameStar, PC Games, IGN, Eurogamer
- **Tech:** Heise, Golem, ComputerBase, t3n
- **Entertainment:** Serienjunkies, Moviepilot
- **Wissenschaft:** Scinexx, Spektrum
- **News:** Tagesschau, Zeit, Spiegel

### 11.2 Gedächtnistypen

```python
MEMORY_TYPES = {
    "episodic": "Ereignisse und Gespräche",
    "semantic": "Fakten und Wissen",
    "emotional": "Bedeutsame Momente",
    "procedural": "Gewohnheiten und Abläufe"
}
```

### 11.3 Fakten-Management

- **Kapazität:** ~10.000 Fakten
- **Decay:** Wichtigkeit sinkt über Zeit
- **Kategorisierung:** Automatisch nach Thema
- **Abruf:** Relevanzbasiert

---

## 12. Medien & Kreativität

### 12.1 Medien-Entdeckung

**HoloMediaDiscovery** integriert:

| Service | API | Funktion |
|---------|-----|----------|
| MyAnimeList | Jikan API | Anime-Entdeckung |
| RAWG | RAWG API | Spiele-Entdeckung |
| Last.fm | Last.fm API | Musik-Entdeckung |
| Wikipedia | REST API | Zusammenfassungen |

### 12.2 Holo's Medien-Meinungen

```python
class MediaEntry:
    title: str
    type: str  # anime, game, music, movie
    discovered_date: datetime
    holo_opinion: str  # Holos persönliche Meinung
    holo_rating: float  # 0.0 - 1.0
    would_recommend: bool
    tags: List[str]
    notes: str
```

### 12.3 Kreative Fähigkeiten

- **ASCII-Art-Generator:** Erstellt ASCII-Kunst
- **Geschichten-Generator:** Schreibt kurze Geschichten
- **Gedicht-Generator:** Verfasst Gedichte
- **Bild-Generierung:** Via ComfyUI-Integration

---

## 13. Datenbanken & Speicherung

### 13.1 Die 17 Datenbanken

| Datenbank | Inhalt |
|-----------|--------|
| `holo_memory.db` | Episodische, semantische, emotionale Erinnerungen |
| `holo_emotions.db` | Stimmungsverlauf, Gefühle, Muster |
| `holo_knowledge.db` | Extrahierte Fakten (~10.000) |
| `holo_conversations.db` | Chat-Verlauf, Themen |
| `holo_media.db` | Anime, Spiele, Musik mit Meinungen |
| `holo_language.db` | Kommunikationsstil, Ausdrücke |
| `holo_activity.db` | Routinen, Aktivitäten |
| `holo_identity.db` | Selbstkonzept, Überzeugungen |
| `holo_productivity.db` | Todos, Timer, Notizen |
| `holo_environment.db` | Wetter, Jahreszeit |
| `holo_network.db` | Netzwerkgeräte |
| `holo_presence.db` | User-Anwesenheitsmuster |
| `holo_home.db` | Home-Automation |
| `holo_calendar.db` | Termine, Events |
| `holo_predictions.db` | ML-Modelle, Vorhersagen |
| `holo_state.db` | Laufzeit-Zustand |
| `holo_news.db` | News-Artikel (optional) |

### 13.2 Speicherort

```
~/holo_data/
├── databases/
│   ├── holo_memory.db
│   ├── holo_emotions.db
│   └── ... (17 DBs)
├── logs/
│   └── holocloude.log
├── backups/
│   └── (max 10 Backups)
└── data/
    ├── cognitive_enhancement/
    ├── decisions/
    ├── media_discovery/
    └── ... (16 Verzeichnisse)
```

---

## 14. Externe Integrationen

### 14.1 LLM-Services

**Ollama (Lokal):**
```python
OLLAMA_CONFIG = {
    "host": "http://192.168.178.42:11434",
    "models": {
        "fast": "nemotron-3-nano",
        "medium": "qwen2.5:1.5b",
        "custom": "holo4"
    }
}
```

**Remote LLM (Optional):**
```python
REMOTE_LLM = {
    "model": "deepseek-v2:16b",
    "use_for": "Komplexe Reasoning-Aufgaben"
}
```

### 14.2 Smart Home

**Home Assistant:**
```python
HOME_ASSISTANT = {
    "url": "http://192.168.178.99:8123/api",
    "provides": ["Wetter", "Sensoren", "Entitäten"]
}
```

**MQTT:**
```python
MQTT = {
    "broker": "192.168.178.99:1883",
    "provides": "Geräte-Messaging"
}
```

### 14.3 Pi-Control

```python
PI_CONTROL = {
    "url": "http://localhost:8008",
    "commands": ["NAS sleep", "System reboot", "Governor control"]
}
```

### 14.4 Medien-APIs

```python
MEDIA_APIS = {
    "jikan": "https://api.jikan.moe/v4",      # MyAnimeList
    "rawg": "https://api.rawg.io/api",        # Spiele
    "lastfm": "https://www.last.fm/api",      # Musik
    "wikipedia": "https://en.wikipedia.org/api/rest_v1"
}
```

---

## 15. Konfiguration

### 15.1 config.json Struktur

```json
{
  "network": {
    "ollama": {
      "host": "http://192.168.178.42:11434"
    },
    "mqtt": {
      "host": "192.168.178.99",
      "port": 1883
    },
    "home_assistant": {
      "url": "http://192.168.178.99:8123/api",
      "token": "YOUR_TOKEN"
    },
    "nas": {
      "host": "192.168.178.40",
      "user": "holo"
    }
  },
  "llm": {
    "context_tokens": 8192,
    "temperature": 0.7,
    "timeout": 120
  },
  "behavior": {
    "mood_tendency": 0.6,
    "response_type": "balanced",
    "energy_saving_start": "23:00",
    "energy_saving_end": "07:00"
  },
  "features": {
    "voice_enabled": true,
    "media_discovery": true,
    "proactive_messages": true,
    "autonomous_activity": true,
    "web_curiosity": true
  },
  "storage": {
    "data_directory": "~/holo_data",
    "max_storage_gb": 10,
    "ram_cache_mb": 512
  }
}
```

### 15.2 Umgebungsvariablen

```bash
HOLO_DATA_PATH=/home/user/holo_data
HOLO_LOG_LEVEL=INFO
HOLO_OLLAMA_HOST=http://192.168.178.42:11434
HOLO_HA_TOKEN=your_home_assistant_token
```

---

## Anhang A: Schnellreferenz

### Wichtige Klassen

| Klasse | Modul | Funktion |
|--------|-------|----------|
| `HoloBrainV15` | holo_brain.py | Zentrale Orchestrierung |
| `ConversationEngine` | holo_cognitive_engine.py | Gesprächsverarbeitung |
| `HoloPersonalityEngine` | holo_personality.py | Persönlichkeit |
| `HoloConsciousness` | holo_consciousness.py | Bewusstsein |
| `HoloInnerLife` | holo_inner_life.py | Innenleben |
| `EmotionalResponseSystem` | holo_emotional_engines.py | Emotionale Antworten |
| `HoloEnergySystem` | holo_energy_system.py | Energie-Management |
| `RealLearningEngine` | holo_learning.py | Lernsystem |
| `HoloMediaDiscovery` | holo_media_discovery.py | Medien-Entdeckung |
| `HoloDatabaseManager` | holo_database_system.py | Datenbankmanagement |

### Wichtige Methoden

```python
# Nachricht verarbeiten
brain.process_message_streaming(user_input)

# Antwort generieren
brain.generate_response(user_input)

# Emotionale Enhancement
engine._enhance_with_emotional_engines(response, user_input, intent)

# Autonome Aktivität
inner_life.do_autonomous_activity()

# Lernen
learning.learn_from_feeds()

# Energie aktualisieren
energy.update()
```

---

## Anhang B: Troubleshooting

### Häufige Probleme

**1. Import-Fehler:**
```bash
python holo_tester.py --quick
```

**2. Datenbank-Probleme:**
```bash
python holo_db_migrations.py
```

**3. Energie zu niedrig:**
```python
# Manueller Reset
energy.set_energy(0.5)
```

**4. Emotionale Engines nicht aktiv:**
```python
# Prüfen
hasattr(brain, 'conversation_engine')
brain.conversation_engine is not None
```

---

## Anhang C: Entwicklung

### Testen

```bash
# Schnelltest
python holo_tester.py --quick

# Alle Tests
python holo_tester.py --all

# Spezifische Tests
python holo_tester.py --methods    # Methoden-Check
python holo_tester.py --runtime    # Runtime-Tests
python holo_tester.py --security   # Sicherheit
```

### Logs

```bash
# Log-Datei
tail -f ~/holo_data/logs/holocloude.log

# Debug-Level
export HOLO_LOG_LEVEL=DEBUG
```

---

*Dokumentation erstellt: Januar 2026*
*Holocloude2 Version: 15.0*
*Emotionale Engines Version: 2.0 (verdoppelt)*
