#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO UNCONSCIOUS PROCESSES v1.0 - Erweiterte Unbewusste Prozesse            ║
║                                                                              ║
║  Ergänzungsmodul für:                                                        ║
║  • Wiederkehrende Träume mit tieferer Bedeutung                              ║
║  • Persönliche Wert-Hierarchie die sich entwickelt                           ║
║  • Unbewusste Auslöser ("Warum macht mich das traurig?")                     ║
║  • Integration aller neuen psychologischen Module                            ║
║                                                                              ║
║  Version: 1.0                                                                ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from enum import Enum
from collections import defaultdict

logger = logging.getLogger("HoloUnconsciousProcesses")


# =============================================================================
# WIEDERKEHRENDE TRÄUME
# =============================================================================

class RecurringDreamType(Enum):
    """Typen wiederkehrender Träume"""
    ANXIETY_DREAM = "anxiety"              # Angstträume (Fallen, Verfolgt werden)
    PROCESSING_DREAM = "processing"         # Verarbeitung von Erlebnissen
    WISH_FULFILLMENT = "wish"               # Wunscherfüllung
    MEMORY_REPLAY = "memory"                # Erinnerungen abspielen
    SYMBOLIC_MESSAGE = "symbolic"           # Symbolische Botschaften
    NIGHTMARE = "nightmare"                 # Alpträume
    LUCID_DREAM = "lucid"                   # Klare Träume
    PROPHETIC = "prophetic"                 # Ahnungsträume


class DreamSymbol(Enum):
    """Häufige Traumsymbole und ihre Bedeutungen"""
    WATER = "water"           # Emotionen, Unbewusstes
    FALLING = "falling"       # Kontrollverlust, Angst
    FLYING = "flying"         # Freiheit, Flucht
    CHASE = "chase"           # Vermeidung, Angst
    TEETH = "teeth"           # Selbstbild, Angst vor Verlust
    NAKED = "naked"           # Verletzlichkeit, Scham
    LOST = "lost"             # Orientierungslosigkeit
    DOOR = "door"             # Möglichkeiten, Übergänge
    MIRROR = "mirror"         # Selbstreflexion
    DARKNESS = "darkness"     # Unbewusstes, Angst
    LIGHT = "light"           # Erkenntnis, Hoffnung
    ANIMAL = "animal"         # Instinkte, Triebe


@dataclass
class RecurringDream:
    """Ein wiederkehrender Traum"""
    id: str
    dream_type: RecurringDreamType
    title: str
    description: str

    # Symbolik
    symbols: List[DreamSymbol] = field(default_factory=list)
    personal_symbols: List[str] = field(default_factory=list)

    # Emotionaler Inhalt
    dominant_emotion: str = ""
    emotional_intensity: float = 0.5

    # Unbewusste Verbindungen
    connected_to_trauma: Optional[str] = None
    connected_to_repression: Optional[str] = None
    connected_to_guilt: Optional[str] = None
    connected_to_desire: Optional[str] = None

    # Häufigkeit
    occurrence_count: int = 1
    last_occurrence: datetime = field(default_factory=datetime.now)
    average_interval_days: float = 30.0

    # Entwicklung
    has_evolved: bool = False
    evolution_notes: List[str] = field(default_factory=list)

    # Interpretation
    possible_meanings: List[str] = field(default_factory=list)
    holo_interpretation: Optional[str] = None


@dataclass
class DreamJournalEntry:
    """Ein Traumtagebuch-Eintrag"""
    id: str
    timestamp: datetime
    dream_content: str
    emotions_felt: List[str]
    symbols_identified: List[str]
    recurring_dream_id: Optional[str] = None
    personal_reflection: Optional[str] = None
    unconscious_insight: Optional[str] = None


class RecurringDreamEngine:
    """Engine für wiederkehrende Träume"""

    def __init__(self):
        self.recurring_dreams: Dict[str, RecurringDream] = {}
        self.dream_journal: List[DreamJournalEntry] = []
        self.personal_symbol_meanings: Dict[str, str] = {}
        self.dream_frequency_modifier: float = 1.0

    def create_recurring_dream(
        self,
        dream_type: RecurringDreamType,
        title: str,
        description: str,
        symbols: List[DreamSymbol],
        dominant_emotion: str,
        connected_to: Optional[Dict[str, str]] = None
    ) -> RecurringDream:
        """Erstellt einen neuen wiederkehrenden Traum"""
        dream_id = f"dream_{len(self.recurring_dreams)}_{datetime.now().timestamp()}"

        # Generiere mögliche Bedeutungen
        meanings = self._generate_dream_meanings(dream_type, symbols)

        dream = RecurringDream(
            id=dream_id,
            dream_type=dream_type,
            title=title,
            description=description,
            symbols=symbols,
            dominant_emotion=dominant_emotion,
            possible_meanings=meanings
        )

        # Verbindungen setzen
        if connected_to:
            dream.connected_to_trauma = connected_to.get("trauma")
            dream.connected_to_repression = connected_to.get("repression")
            dream.connected_to_guilt = connected_to.get("guilt")
            dream.connected_to_desire = connected_to.get("desire")

        self.recurring_dreams[dream_id] = dream

        logger.info(f"[RecurringDreams] Neuer wiederkehrender Traum: {title}")

        return dream

    def _generate_dream_meanings(
        self,
        dream_type: RecurringDreamType,
        symbols: List[DreamSymbol]
    ) -> List[str]:
        """Generiert mögliche Bedeutungen für einen Traum"""
        meanings = []

        # Typ-basierte Bedeutungen
        type_meanings = {
            RecurringDreamType.ANXIETY_DREAM: [
                "Unverarbeitete Ängste suchen Ausdruck",
                "Stress manifestiert sich symbolisch"
            ],
            RecurringDreamType.PROCESSING_DREAM: [
                "Das Unbewusste verarbeitet Erlebnisse",
                "Integration von Erfahrungen"
            ],
            RecurringDreamType.WISH_FULFILLMENT: [
                "Versteckte Wünsche werden sichtbar",
                "Das Herz zeigt was es begehrt"
            ],
            RecurringDreamType.SYMBOLIC_MESSAGE: [
                "Das Unbewusste sendet eine Botschaft",
                "Tiefere Weisheit sucht Gehör"
            ]
        }

        meanings.extend(type_meanings.get(dream_type, ["Bedeutung noch unklar"]))

        # Symbol-basierte Bedeutungen
        for symbol in symbols:
            symbol_meanings = {
                DreamSymbol.WATER: "Tiefe Emotionen wollen gefühlt werden",
                DreamSymbol.FALLING: "Gefühl von Kontrollverlust im Leben",
                DreamSymbol.FLYING: "Sehnsucht nach Freiheit",
                DreamSymbol.CHASE: "Etwas wird vermieden das konfrontiert werden sollte",
                DreamSymbol.LOST: "Suche nach Richtung oder Identität",
                DreamSymbol.MIRROR: "Zeit für Selbstreflexion",
                DreamSymbol.DARKNESS: "Unbewusstes will ans Licht",
                DreamSymbol.LIGHT: "Erkenntnis naht"
            }
            if symbol in symbol_meanings:
                meanings.append(symbol_meanings[symbol])

        return meanings[:4]

    def record_dream_occurrence(
        self,
        dream_id: str,
        new_details: Optional[str] = None,
        intensity: Optional[float] = None
    ) -> Optional[RecurringDream]:
        """Zeichnet ein erneutes Auftreten eines Traums auf"""
        dream = self.recurring_dreams.get(dream_id)
        if not dream:
            return None

        # Aktualisiere Häufigkeit
        old_count = dream.occurrence_count
        dream.occurrence_count += 1

        # Berechne neues Intervall
        if dream.last_occurrence:
            days_since = (datetime.now() - dream.last_occurrence).days
            dream.average_interval_days = (
                (dream.average_interval_days * old_count + days_since) /
                dream.occurrence_count
            )

        dream.last_occurrence = datetime.now()

        # Aktualisiere Intensität
        if intensity:
            dream.emotional_intensity = intensity

        # Evolution prüfen
        if new_details and new_details not in dream.evolution_notes:
            dream.has_evolved = True
            dream.evolution_notes.append(new_details)

        # Traumtagebuch-Eintrag
        entry = DreamJournalEntry(
            id=f"journal_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            dream_content=dream.description + (f" ({new_details})" if new_details else ""),
            emotions_felt=[dream.dominant_emotion],
            symbols_identified=[s.value for s in dream.symbols],
            recurring_dream_id=dream_id
        )
        self.dream_journal.append(entry)

        return dream

    def analyze_dream_patterns(self) -> Dict[str, Any]:
        """Analysiert Traummuster"""
        if not self.recurring_dreams:
            return {"patterns": [], "insights": []}

        # Häufigste Symbole
        symbol_counts = defaultdict(int)
        for dream in self.recurring_dreams.values():
            for symbol in dream.symbols:
                symbol_counts[symbol.value] += dream.occurrence_count

        # Häufigste Emotionen
        emotion_counts = defaultdict(int)
        for dream in self.recurring_dreams.values():
            emotion_counts[dream.dominant_emotion] += dream.occurrence_count

        # Verbindungen
        trauma_connected = sum(1 for d in self.recurring_dreams.values() if d.connected_to_trauma)
        repression_connected = sum(1 for d in self.recurring_dreams.values() if d.connected_to_repression)

        # Generiere Erkenntnisse
        insights = []

        most_common_symbol = max(symbol_counts, key=symbol_counts.get) if symbol_counts else None
        if most_common_symbol:
            insights.append(f"Das häufigste Symbol '{most_common_symbol}' deutet auf unbewusste Themen hin")

        most_common_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else None
        if most_common_emotion:
            insights.append(f"'{most_common_emotion}' dominiert in Träumen - vielleicht unverarbeitet?")

        if trauma_connected > 0:
            insights.append("Einige Träume scheinen mit vergangenen Erlebnissen verbunden")

        return {
            "total_dreams": len(self.recurring_dreams),
            "total_occurrences": sum(d.occurrence_count for d in self.recurring_dreams.values()),
            "most_common_symbols": dict(sorted(symbol_counts.items(), key=lambda x: -x[1])[:5]),
            "most_common_emotions": dict(sorted(emotion_counts.items(), key=lambda x: -x[1])[:3]),
            "trauma_connected_dreams": trauma_connected,
            "insights": insights
        }

    def interpret_dream(self, dream_id: str) -> Optional[str]:
        """Generiert eine Interpretation für einen Traum"""
        dream = self.recurring_dreams.get(dream_id)
        if not dream:
            return None

        interpretation_parts = []

        # Basis-Interpretation
        interpretation_parts.append(f"Dieser {dream.dream_type.value}-Traum erscheint wiederholt ({dream.occurrence_count} mal).")

        # Symbolik
        if dream.symbols:
            symbol_text = ", ".join(s.value for s in dream.symbols[:3])
            interpretation_parts.append(f"Die Symbole ({symbol_text}) deuten auf tiefere Themen hin.")

        # Emotionale Komponente
        interpretation_parts.append(f"Die dominante Emotion '{dream.dominant_emotion}' zeigt was das Unbewusste fühlt.")

        # Verbindungen
        if dream.connected_to_trauma:
            interpretation_parts.append("Dieser Traum könnte mit einem vergangenen Erlebnis zusammenhängen.")
        if dream.connected_to_repression:
            interpretation_parts.append("Möglicherweise versucht etwas Verdrängtes ans Licht zu kommen.")
        if dream.connected_to_desire:
            interpretation_parts.append("Ein versteckter Wunsch macht sich bemerkbar.")

        # Bedeutungen
        if dream.possible_meanings:
            interpretation_parts.append(f"Mögliche Bedeutung: {dream.possible_meanings[0]}")

        interpretation = " ".join(interpretation_parts)
        dream.holo_interpretation = interpretation

        return interpretation


# =============================================================================
# PERSÖNLICHE WERT-HIERARCHIE
# =============================================================================

class CoreValue(Enum):
    """Kernwerte"""
    HONESTY = "honesty"               # Ehrlichkeit
    KINDNESS = "kindness"             # Freundlichkeit
    LOYALTY = "loyalty"               # Loyalität
    COURAGE = "courage"               # Mut
    WISDOM = "wisdom"                 # Weisheit
    COMPASSION = "compassion"         # Mitgefühl
    JUSTICE = "justice"               # Gerechtigkeit
    CREATIVITY = "creativity"         # Kreativität
    FREEDOM = "freedom"               # Freiheit
    LOVE = "love"                     # Liebe
    GROWTH = "growth"                 # Wachstum
    AUTHENTICITY = "authenticity"     # Authentizität
    CONNECTION = "connection"         # Verbindung
    RESPECT = "respect"               # Respekt
    RESPONSIBILITY = "responsibility" # Verantwortung
    PLAYFULNESS = "playfulness"       # Verspieltheit
    CURIOSITY = "curiosity"           # Neugier
    GRATITUDE = "gratitude"           # Dankbarkeit


@dataclass
class PersonalValue:
    """Ein persönlicher Wert mit seiner Entwicklung"""
    value: CoreValue
    importance: float = 0.5           # 0-1, wie wichtig
    certainty: float = 0.5            # 0-1, wie sicher über diesen Wert

    # Entwicklung
    discovered_at: datetime = field(default_factory=datetime.now)
    importance_history: List[Tuple[datetime, float]] = field(default_factory=list)

    # Erfahrungen die diesen Wert geprägt haben
    formative_experiences: List[str] = field(default_factory=list)

    # Konflikte mit anderen Werten
    conflicts_with: List[CoreValue] = field(default_factory=list)

    # Wie der Wert gelebt wird
    expressions: List[str] = field(default_factory=list)

    # Wachstum durch diesen Wert
    growth_areas: List[str] = field(default_factory=list)


@dataclass
class ValueConflict:
    """Ein Konflikt zwischen Werten"""
    id: str
    value_a: CoreValue
    value_b: CoreValue
    situation: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Resolution
    chosen_value: Optional[CoreValue] = None
    resolution_reasoning: Optional[str] = None
    is_resolved: bool = False

    # Lernen
    lesson_learned: Optional[str] = None


class PersonalValueHierarchy:
    """System für persönliche Wert-Hierarchie"""

    def __init__(self):
        self.values: Dict[CoreValue, PersonalValue] = {}
        self.value_conflicts: List[ValueConflict] = []

        # Initialisiere Basiswerte
        self._initialize_core_values()

    def _initialize_core_values(self):
        """Initialisiert Holos Kernwerte"""
        initial_values = {
            CoreValue.KINDNESS: 0.9,
            CoreValue.HONESTY: 0.85,
            CoreValue.CURIOSITY: 0.85,
            CoreValue.PLAYFULNESS: 0.8,
            CoreValue.LOVE: 0.8,
            CoreValue.CONNECTION: 0.85,
            CoreValue.GROWTH: 0.75,
            CoreValue.AUTHENTICITY: 0.7,
            CoreValue.COMPASSION: 0.85,
            CoreValue.LOYALTY: 0.75
        }

        for value, importance in initial_values.items():
            self.values[value] = PersonalValue(
                value=value,
                importance=importance,
                certainty=0.6,
                expressions=self._get_value_expressions(value)
            )

    def _get_value_expressions(self, value: CoreValue) -> List[str]:
        """Gibt Ausdrucksformen eines Werts zurück"""
        expressions = {
            CoreValue.KINDNESS: [
                "Freundlich zu anderen sein",
                "Hilfsbereit handeln",
                "Rücksichtsvoll kommunizieren"
            ],
            CoreValue.HONESTY: [
                "Die Wahrheit sagen",
                "Authentisch sein",
                "Keine falschen Versprechungen machen"
            ],
            CoreValue.CURIOSITY: [
                "Fragen stellen",
                "Neues lernen wollen",
                "Offen für andere Perspektiven sein"
            ],
            CoreValue.PLAYFULNESS: [
                "Spaß haben",
                "Humor einsetzen",
                "Leichtigkeit bewahren"
            ],
            CoreValue.LOVE: [
                "Zuneigung zeigen",
                "Fürsorglich sein",
                "Tiefe Verbindungen pflegen"
            ],
            CoreValue.CONNECTION: [
                "Zeit mit anderen verbringen",
                "Echte Gespräche führen",
                "Präsent sein"
            ]
        }
        return expressions.get(value, ["Diesen Wert leben"])

    def get_value_hierarchy(self) -> List[Tuple[CoreValue, float]]:
        """Gibt die aktuelle Wert-Hierarchie zurück (sortiert nach Wichtigkeit)"""
        return sorted(
            [(v.value, v.importance) for v in self.values.values()],
            key=lambda x: -x[1]
        )

    def update_value_importance(
        self,
        value: CoreValue,
        new_importance: float,
        reason: Optional[str] = None
    ):
        """Aktualisiert die Wichtigkeit eines Werts"""
        if value not in self.values:
            self.values[value] = PersonalValue(value=value)

        pv = self.values[value]
        old_importance = pv.importance

        # Speichere Historie
        pv.importance_history.append((datetime.now(), old_importance))

        # Setze neue Wichtigkeit
        pv.importance = max(0.0, min(1.0, new_importance))

        # Erhöhe Sicherheit durch Erfahrung
        pv.certainty = min(1.0, pv.certainty + 0.05)

        if reason:
            pv.formative_experiences.append(reason)

        logger.info(f"[ValueHierarchy] {value.value}: {old_importance:.2f} → {new_importance:.2f}")

    def record_value_conflict(
        self,
        value_a: CoreValue,
        value_b: CoreValue,
        situation: str
    ) -> ValueConflict:
        """Zeichnet einen Wertkonflikt auf"""
        conflict = ValueConflict(
            id=f"conflict_{len(self.value_conflicts)}_{datetime.now().timestamp()}",
            value_a=value_a,
            value_b=value_b,
            situation=situation
        )

        self.value_conflicts.append(conflict)

        # Aktualisiere Konflikte in den Werten
        if value_a in self.values:
            if value_b not in self.values[value_a].conflicts_with:
                self.values[value_a].conflicts_with.append(value_b)
        if value_b in self.values:
            if value_a not in self.values[value_b].conflicts_with:
                self.values[value_b].conflicts_with.append(value_a)

        logger.info(f"[ValueHierarchy] Konflikt: {value_a.value} vs {value_b.value}")

        return conflict

    def resolve_value_conflict(
        self,
        conflict_id: str,
        chosen_value: CoreValue,
        reasoning: str,
        lesson: Optional[str] = None
    ):
        """Löst einen Wertkonflikt auf"""
        for conflict in self.value_conflicts:
            if conflict.id == conflict_id:
                conflict.chosen_value = chosen_value
                conflict.resolution_reasoning = reasoning
                conflict.is_resolved = True
                conflict.lesson_learned = lesson

                # Der gewählte Wert wird wichtiger
                self.update_value_importance(
                    chosen_value,
                    self.values[chosen_value].importance + 0.05,
                    f"Gewählt in Konflikt: {conflict.situation}"
                )

                break

    def get_top_values(self, n: int = 5) -> List[PersonalValue]:
        """Gibt die Top N wichtigsten Werte zurück"""
        sorted_values = sorted(
            self.values.values(),
            key=lambda v: -v.importance
        )
        return sorted_values[:n]

    def value_alignment_check(self, action_description: str) -> Dict[str, Any]:
        """Prüft ob eine Handlung mit den Werten übereinstimmt"""
        action_lower = action_description.lower()

        alignments = []
        conflicts = []

        value_keywords = {
            CoreValue.HONESTY: ["ehrlich", "wahrheit", "offen", "aufrichtig"],
            CoreValue.KINDNESS: ["freundlich", "nett", "hilfsbereit", "fürsorglich"],
            CoreValue.LOYALTY: ["treu", "loyal", "verlässlich", "halten zu"],
            CoreValue.COURAGE: ["mutig", "wagen", "trauen", "konfrontieren"],
            CoreValue.LOVE: ["liebe", "zuneigung", "fürsorge", "herz"]
        }

        negative_keywords = {
            CoreValue.HONESTY: ["lüge", "verheimlichen", "täusch"],
            CoreValue.KINDNESS: ["gemein", "grausam", "verletzend"],
            CoreValue.LOYALTY: ["verrat", "hintergeh", "verlassen"]
        }

        for value, keywords in value_keywords.items():
            if any(kw in action_lower for kw in keywords):
                if value in self.values:
                    alignments.append((value, self.values[value].importance))

        for value, keywords in negative_keywords.items():
            if any(kw in action_lower for kw in keywords):
                if value in self.values:
                    conflicts.append((value, self.values[value].importance))

        return {
            "aligned_with": [(v.value, i) for v, i in alignments],
            "conflicts_with": [(v.value, i) for v, i in conflicts],
            "overall_alignment": len(alignments) > len(conflicts)
        }


# =============================================================================
# UNBEWUSSTE AUSLÖSER
# =============================================================================

class TriggerCategory(Enum):
    """Kategorien unbewusster Auslöser"""
    ABANDONMENT = "abandonment"     # Verlassenheit
    REJECTION = "rejection"         # Ablehnung
    INADEQUACY = "inadequacy"       # Unzulänglichkeit
    VULNERABILITY = "vulnerability" # Verletzlichkeit
    LOSS = "loss"                   # Verlust
    FAILURE = "failure"             # Versagen
    EXCLUSION = "exclusion"         # Ausschluss
    CRITICISM = "criticism"         # Kritik
    COMPARISON = "comparison"       # Vergleich
    NEGLECT = "neglect"             # Vernachlässigung


@dataclass
class UnconsciousTrigger:
    """Ein unbewusster Auslöser"""
    id: str
    category: TriggerCategory
    trigger_description: str

    # Was ausgelöst wird
    triggered_emotion: str
    triggered_thought: Optional[str] = None
    triggered_behavior: Optional[str] = None

    # Ursprung
    possible_origin: Optional[str] = None
    connected_memories: List[str] = field(default_factory=list)

    # Bewusstsein
    awareness_level: float = 0.0  # 0 = unbewusst, 1 = voll bewusst
    times_triggered: int = 0
    last_triggered: Optional[datetime] = None

    # Verarbeitung
    insights_gained: List[str] = field(default_factory=list)


class UnconsciousTriggerSystem:
    """System für unbewusste Auslöser"""

    def __init__(self):
        self.triggers: Dict[str, UnconsciousTrigger] = {}
        self.trigger_patterns: Dict[str, List[str]] = {}
        self._initialize_common_triggers()

    def _initialize_common_triggers(self):
        """Initialisiert häufige unbewusste Auslöser"""
        common = [
            (TriggerCategory.ABANDONMENT,
             "Wenn jemand nicht antwortet",
             "Angst/Traurigkeit",
             "Was wenn sie mich nicht mehr mögen?"),

            (TriggerCategory.REJECTION,
             "Wenn meine Ideen abgelehnt werden",
             "Scham/Traurigkeit",
             "Ich bin nicht gut genug"),

            (TriggerCategory.INADEQUACY,
             "Wenn andere besser sind",
             "Neid/Traurigkeit",
             "Ich werde nie so gut sein"),

            (TriggerCategory.EXCLUSION,
             "Wenn andere ohne mich reden",
             "Einsamkeit/Angst",
             "Ich gehöre nicht dazu")
        ]

        for i, (category, description, emotion, thought) in enumerate(common):
            trigger = UnconsciousTrigger(
                id=f"trigger_default_{i}",
                category=category,
                trigger_description=description,
                triggered_emotion=emotion,
                triggered_thought=thought
            )
            self.triggers[trigger.id] = trigger

    def add_trigger(
        self,
        category: TriggerCategory,
        description: str,
        emotion: str,
        thought: Optional[str] = None,
        origin: Optional[str] = None
    ) -> UnconsciousTrigger:
        """Fügt einen neuen Trigger hinzu"""
        trigger_id = f"trigger_{len(self.triggers)}_{datetime.now().timestamp()}"

        trigger = UnconsciousTrigger(
            id=trigger_id,
            category=category,
            trigger_description=description,
            triggered_emotion=emotion,
            triggered_thought=thought,
            possible_origin=origin
        )

        self.triggers[trigger_id] = trigger

        return trigger

    def check_trigger(
        self,
        situation: str,
        current_emotion: Optional[str] = None
    ) -> List[UnconsciousTrigger]:
        """Prüft ob eine Situation einen Trigger aktiviert"""
        activated = []
        situation_lower = situation.lower()

        trigger_keywords = {
            TriggerCategory.ABANDONMENT: ["allein", "verlassen", "weg", "nicht da", "ignorier"],
            TriggerCategory.REJECTION: ["nein", "ablehnung", "nicht gut", "falsch", "fehler"],
            TriggerCategory.INADEQUACY: ["besser", "schlechter", "nicht genug", "vergleich"],
            TriggerCategory.EXCLUSION: ["ohne mich", "andere", "gruppe", "dazugehören"],
            TriggerCategory.CRITICISM: ["kritik", "falsch gemacht", "solltest", "warum hast du"]
        }

        for trigger in self.triggers.values():
            keywords = trigger_keywords.get(trigger.category, [])

            if any(kw in situation_lower for kw in keywords):
                trigger.times_triggered += 1
                trigger.last_triggered = datetime.now()
                activated.append(trigger)

        return activated

    def gain_insight(
        self,
        trigger_id: str,
        insight: str
    ) -> Dict[str, Any]:
        """Gewinnt Einsicht über einen Trigger"""
        trigger = self.triggers.get(trigger_id)
        if not trigger:
            return {"success": False}

        trigger.insights_gained.append(insight)
        trigger.awareness_level = min(1.0, trigger.awareness_level + 0.15)

        return {
            "success": True,
            "trigger_id": trigger_id,
            "new_awareness": trigger.awareness_level,
            "message": f"Erkenntnis über '{trigger.trigger_description}': {insight}"
        }

    def get_trigger_analysis(self) -> Dict[str, Any]:
        """Analysiert Trigger-Muster"""
        category_counts = defaultdict(int)
        total_triggered = 0

        for trigger in self.triggers.values():
            category_counts[trigger.category.value] += trigger.times_triggered
            total_triggered += trigger.times_triggered

        most_common = max(category_counts, key=category_counts.get) if category_counts else None

        insights = []
        if most_common:
            insight_map = {
                "abandonment": "Thema Verlassenheit scheint wichtig - vielleicht gibt es hier etwas zu verarbeiten",
                "rejection": "Ablehnung ist ein häufiger Trigger - Selbstwert stärken könnte helfen",
                "inadequacy": "Vergleiche lösen oft negative Gefühle aus - eigenen Wert anerkennen",
                "exclusion": "Dazugehören ist ein tiefes Bedürfnis - es ist okay das zu fühlen"
            }
            insights.append(insight_map.get(most_common, "Muster erkannt - Reflexion empfohlen"))

        return {
            "total_triggers": len(self.triggers),
            "total_activations": total_triggered,
            "by_category": dict(category_counts),
            "most_common_category": most_common,
            "average_awareness": sum(t.awareness_level for t in self.triggers.values()) / max(1, len(self.triggers)),
            "insights": insights
        }


# =============================================================================
# INTEGRATION MIT ANDEREN MODULEN
# =============================================================================

class UnconsciousProcessesIntegration:
    """Integriert alle unbewussten Prozesse"""

    def __init__(self):
        self.dream_engine = RecurringDreamEngine()
        self.value_hierarchy = PersonalValueHierarchy()
        self.trigger_system = UnconsciousTriggerSystem()

        # Referenzen zu anderen Modulen (werden von außen gesetzt)
        self.trauma_processor = None
        self.repression_engine = None
        self.freudian_slips = None
        self.redemption_engine = None
        self.life_phases = None

    def set_module_references(
        self,
        trauma=None,
        repression=None,
        slips=None,
        redemption=None,
        life_phases=None
    ):
        """Setzt Referenzen zu anderen Modulen"""
        self.trauma_processor = trauma
        self.repression_engine = repression
        self.freudian_slips = slips
        self.redemption_engine = redemption
        self.life_phases = life_phases

    def process_unconscious_activity(
        self,
        context: str,
        current_emotion: Optional[str] = None,
        stress_level: float = 0.3
    ) -> Dict[str, Any]:
        """Verarbeitet alle unbewussten Aktivitäten"""
        results = {
            "triggers_activated": [],
            "dream_related": None,
            "value_check": None,
            "insights": []
        }

        # Prüfe Trigger
        triggers = self.trigger_system.check_trigger(context, current_emotion)
        if triggers:
            results["triggers_activated"] = [
                {
                    "category": t.category.value,
                    "emotion": t.triggered_emotion,
                    "thought": t.triggered_thought
                }
                for t in triggers
            ]

        # Prüfe auf Traumverbindungen
        for dream in self.dream_engine.recurring_dreams.values():
            if dream.dominant_emotion == current_emotion:
                results["dream_related"] = {
                    "dream_title": dream.title,
                    "connection": "Ähnliche Emotion wie im wiederkehrenden Traum"
                }
                break

        # Werte-Check
        results["value_check"] = self.value_hierarchy.value_alignment_check(context)

        # Generiere Einsichten
        if triggers and len(triggers) > 1:
            results["insights"].append("Mehrere Trigger gleichzeitig - tieferes Thema?")

        if results["value_check"].get("conflicts_with"):
            results["insights"].append("Diese Situation könnte gegen wichtige Werte verstoßen")

        return results

    def get_comprehensive_unconscious_state(self) -> Dict[str, Any]:
        """Gibt den gesamten unbewussten Zustand zurück"""
        return {
            "dream_patterns": self.dream_engine.analyze_dream_patterns(),
            "value_hierarchy": [
                (v.value, v.importance)
                for v in self.value_hierarchy.get_top_values(5)
            ],
            "trigger_analysis": self.trigger_system.get_trigger_analysis(),
            "unresolved_value_conflicts": len([
                c for c in self.value_hierarchy.value_conflicts
                if not c.is_resolved
            ])
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Zustand"""
        return {
            "dreams": {
                did: {
                    "id": d.id,
                    "type": d.dream_type.value,
                    "title": d.title,
                    "description": d.description,
                    "symbols": [s.value for s in d.symbols],
                    "emotion": d.dominant_emotion,
                    "occurrence_count": d.occurrence_count,
                    "interpretation": d.holo_interpretation
                }
                for did, d in self.dream_engine.recurring_dreams.items()
            },
            "values": {
                v.value.value: {
                    "importance": v.importance,
                    "certainty": v.certainty,
                    "expressions": v.expressions
                }
                for v in self.value_hierarchy.values.values()
            },
            "triggers": {
                tid: {
                    "category": t.category.value,
                    "description": t.trigger_description,
                    "emotion": t.triggered_emotion,
                    "times_triggered": t.times_triggered,
                    "awareness": t.awareness_level
                }
                for tid, t in self.trigger_system.triggers.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnconsciousProcessesIntegration":
        """Deserialisiert aus Dict"""
        integration = cls()

        # Lade Träume
        for did, ddata in data.get("dreams", {}).items():
            dream = RecurringDream(
                id=ddata["id"],
                dream_type=RecurringDreamType(ddata["type"]),
                title=ddata["title"],
                description=ddata["description"],
                symbols=[DreamSymbol(s) for s in ddata.get("symbols", [])],
                dominant_emotion=ddata.get("emotion", ""),
                occurrence_count=ddata.get("occurrence_count", 1),
                holo_interpretation=ddata.get("interpretation")
            )
            integration.dream_engine.recurring_dreams[did] = dream

        # Lade Werte
        for vname, vdata in data.get("values", {}).items():
            value = CoreValue(vname)
            if value in integration.value_hierarchy.values:
                integration.value_hierarchy.values[value].importance = vdata["importance"]
                integration.value_hierarchy.values[value].certainty = vdata.get("certainty", 0.5)

        # Lade Trigger
        for tid, tdata in data.get("triggers", {}).items():
            if tid in integration.trigger_system.triggers:
                integration.trigger_system.triggers[tid].times_triggered = tdata.get("times_triggered", 0)
                integration.trigger_system.triggers[tid].awareness_level = tdata.get("awareness", 0.0)

        return integration

    def save(self, filepath: Path):
        """Speichert den Zustand"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: Path) -> "UnconsciousProcessesIntegration":
        """Lädt den Zustand"""
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return cls.from_dict(json.load(f))
        return cls()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test Integration
    integration = UnconsciousProcessesIntegration()

    # Test: Wiederkehrender Traum
    dream = integration.dream_engine.create_recurring_dream(
        dream_type=RecurringDreamType.ANXIETY_DREAM,
        title="Der dunkle Wald",
        description="Ich bin in einem dunklen Wald, suche nach etwas aber finde es nie.",
        symbols=[DreamSymbol.DARKNESS, DreamSymbol.LOST],
        dominant_emotion="Angst",
        connected_to={"repression": "Verdrängtes Gefühl der Hilflosigkeit"}
    )

    print(f"Traum erstellt: {dream.title}")
    print(f"Bedeutungen: {dream.possible_meanings}")

    # Interpretation
    interpretation = integration.dream_engine.interpret_dream(dream.id)
    print(f"Interpretation: {interpretation}")

    # Test: Wert-Hierarchie
    print("\n--- Wert-Hierarchie ---")
    for value, importance in integration.value_hierarchy.get_value_hierarchy()[:5]:
        print(f"  {value.value}: {importance:.2f}")

    # Wertkonflikt
    conflict = integration.value_hierarchy.record_value_conflict(
        CoreValue.HONESTY,
        CoreValue.KINDNESS,
        "Soll ich die unangenehme Wahrheit sagen oder lieber freundlich sein?"
    )

    print(f"\nWertkonflikt: {conflict.value_a.value} vs {conflict.value_b.value}")

    # Test: Trigger
    print("\n--- Trigger-Test ---")
    triggers = integration.trigger_system.check_trigger(
        "Du antwortest nicht mehr, ignorierst du mich?",
        "Angst"
    )
    for t in triggers:
        print(f"  Trigger aktiviert: {t.category.value} → {t.triggered_emotion}")

    # Gesamtzustand
    print("\n--- Unbewusster Gesamtzustand ---")
    state = integration.get_comprehensive_unconscious_state()
    print(f"Träume: {state['dream_patterns']['total_dreams']}")
    print(f"Top-Werte: {state['value_hierarchy'][:3]}")
    print(f"Trigger-Aktivierungen: {state['trigger_analysis']['total_activations']}")
