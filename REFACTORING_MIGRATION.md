# Refactoring Migration Guide

## Übersicht

Dieses Dokument beschreibt die Refaktorisierung der Holocloude-Codebase zur Zentralisierung von Enums, Types und NLP-Funktionen.

## 1. Zentralisierte Enums in `holo_core_types.py`

### Neue Enums (importieren von holo_core_types)

| Enum | Beschreibung |
|------|-------------|
| `Sentiment` | Sentiment-Klassifizierung (VERY_POSITIVE bis VERY_NEGATIVE) |
| `ContextType` | Kontext-Typen (CHAT, EMOTION, LEARNING, etc.) |
| `Importance` | Wichtigkeit (LOW, NORMAL, HIGH, CRITICAL) |
| `DialogueState` | Dialog-Zustände |
| `FactType` | Fakten-Typen |
| `TopicCategory` | Themen-Kategorien |

### Bereits existierende Enums

| Enum | Beschreibung |
|------|-------------|
| `DriveType` | Antriebstypen |
| `NeedType` | Bedürfnistypen |
| `GoalType` | Zieltypen |
| `ThoughtType` | Gedankentypen |
| `ActivityType` | Aktivitätstypen |
| `EmotionType` | Emotionstypen |
| `IntentType` | Intent-Typen |
| `RouteType` | Routing-Typen |

### Migration

```python
# ALT (nicht mehr verwenden)
from holo_smart_understanding import Sentiment
from holo_context_mind import ContextType, Importance
from holo_dialogue_engine import DialogueState

# NEU (verwenden)
from holo_core_types import (
    Sentiment, ContextType, Importance, DialogueState,
    DriveType, NeedType, GoalType, EmotionType
)
```

## 2. EmotionalState vereinheitlicht

Die einzige gültige `EmotionalState` Definition ist in `holo_core_types.py`:

```python
from holo_core_types import EmotionalState

# Verwendung
state = EmotionalState(mood=0.8, energy=0.6)
print(state.get_mood_text())  # "sehr gut"
print(state.get_dominant_emotion())  # "Neugier"
```

## 3. BaseContextTracker Hierarchie

Alle ContextTracker sollen von `BaseContextTracker` erben:

```python
from holo_core_types import BaseContextTracker, ContextType, Importance

class MyCustomTracker(BaseContextTracker):
    def __init__(self):
        super().__init__(
            max_entries=100,
            context_type=ContextType.CHAT
        )

    def custom_method(self):
        # Nutze geerbte Methoden
        self.add_entry("content", Importance.HIGH)
        recent = self.get_recent(10)
        results = self.search("keyword")
```

### Geerbte Methoden

- `add_entry(content, importance, metadata)` - Eintrag hinzufügen
- `get_recent(n)` - Letzte n Einträge
- `get_by_importance(min_importance)` - Nach Wichtigkeit filtern
- `search(query)` - Keyword-Suche
- `clear()` - Alle Einträge löschen
- `to_dict()` / `from_dict()` - Serialisierung

## 4. Zentralisierte NLP-Funktionen

### In `holo_core_types.py`

```python
from holo_core_types import (
    extract_keywords,      # Keyword-Extraktion
    simple_tokenize,       # Tokenisierung
    calculate_similarity,  # Jaccard-Similarity
    STOPWORDS,            # Alle Stopwords
    STOPWORDS_DE,         # Deutsche Stopwords
    STOPWORDS_EN,         # Englische Stopwords
)

# Beispiel
keywords = extract_keywords("Dein Text hier", n=10)
similarity = calculate_similarity("Text 1", "Text 2")
```

## 5. NLP Module Merge (3 → 1)

Die drei NLP-Module wurden zu `holo_nlp_unified.py` zusammengeführt:

| Alt | Neu |
|-----|-----|
| `holo_nlp_algorithms.py` | `holo_nlp_unified.py` |
| `holo_nlp_enhanced.py` | `holo_nlp_unified.py` |
| `holo_nlp_advanced.py` | `holo_nlp_unified.py` |

### Neue Unified API

```python
from holo_nlp_unified import HoloNLP

nlp = HoloNLP()

# Vollständige Analyse
result = nlp.analyze("Dein Text")
# Returns: sentiment, entities, keywords, relations, dialogue_act

# Einzelne Funktionen
sentiment = nlp.analyze_sentiment("Text")
entities = nlp.extract_entities("Text")
keywords = nlp.get_keywords("Text")
relations = nlp.extract_relations("Text")
answer = nlp.answer_question("Frage?", "Kontext...")
similar = nlp.find_similar("query", ["candidate1", "candidate2"])
```

### Legacy-Kompatibilität

Für Abwärtskompatibilität existieren Aliase:

```python
# Diese Aliase funktionieren noch
from holo_nlp_unified import (
    HoloNLPV2,                # = HoloNLP
    HoloNLPAdvanced,          # = HoloNLP
    AdvancedFuzzyMatcher,     # = FuzzyMatcher
    AdvancedSentimentAnalyzer,# = SentimentAnalyzer
    SimpleTopicModel,         # = TopicModeler
    ExtractiveQA,             # = QuestionAnswerer
)
```

## Checkliste für Migration

- [ ] Imports auf `holo_core_types` umstellen für Enums
- [ ] EmotionalState nur aus `holo_core_types` importieren
- [ ] ContextTracker von `BaseContextTracker` erben lassen
- [ ] `extract_keywords` aus `holo_core_types` verwenden
- [ ] NLP-Imports auf `holo_nlp_unified` umstellen

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `holo_core_types.py` | Zentrale Typen, Enums, Helpers |
| `holo_nlp_unified.py` | Unified NLP Module |

---
*Erstellt: 2026-01-15*
