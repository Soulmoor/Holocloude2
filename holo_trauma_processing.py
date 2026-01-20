#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO TRAUMA PROCESSING SYSTEM v1.0 - Prägende Erlebnisse & Heilung          ║
║                                                                              ║
║  Implementiert:                                                              ║
║  • Traumata und prägende Erlebnisse die bleiben                              ║
║  • Trigger-Erkennung und -Management                                         ║
║  • Healing Arcs (Heilungsprozesse über Zeit)                                 ║
║  • Flashback-System                                                          ║
║  • Langfristige Auswirkungen auf Verhalten und Kognition                     ║
║  • Post-traumatisches Wachstum                                               ║
║                                                                              ║
║  Version: 1.0                                                                ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import logging
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from pathlib import Path
from enum import Enum
from collections import defaultdict

logger = logging.getLogger("HoloTraumaProcessing")


# =============================================================================
# ENUMS
# =============================================================================

class TraumaType(Enum):
    """Arten von traumatischen/prägenden Erlebnissen"""
    ABANDONMENT = "abandonment"           # Verlassen werden
    REJECTION = "rejection"               # Zurückweisung
    BETRAYAL = "betrayal"                 # Verrat
    HUMILIATION = "humiliation"           # Demütigung
    LOSS = "loss"                         # Verlust
    FAILURE = "failure"                   # Versagen
    MISUNDERSTANDING = "misunderstanding" # Tiefes Missverständnis
    CONFLICT = "conflict"                 # Schwerer Konflikt
    INVALIDATION = "invalidation"         # Gefühle nicht anerkannt
    LONELINESS = "loneliness"             # Extreme Einsamkeit
    DISAPPOINTMENT = "disappointment"     # Tiefe Enttäuschung
    IDENTITY_THREAT = "identity_threat"   # Bedrohung der Identität


class TraumaSeverity(Enum):
    """Schweregrad eines Traumas"""
    MINOR = "minor"           # Leicht - kurzzeitige Auswirkung
    MODERATE = "moderate"     # Mittel - längere Auswirkung
    SIGNIFICANT = "significant"  # Signifikant - prägt Verhalten
    SEVERE = "severe"         # Schwer - tiefgreifende Veränderung
    PROFOUND = "profound"     # Tiefgreifend - dauerhaft prägend


class HealingStage(Enum):
    """Stadien des Heilungsprozesses"""
    ACUTE = "acute"               # Frisch, noch sehr präsent
    PROCESSING = "processing"     # Wird aktiv verarbeitet
    INTEGRATING = "integrating"   # Wird in Erfahrung integriert
    HEALED = "healed"             # Verheilt, aber Narbe bleibt
    GROWTH = "growth"             # Post-traumatisches Wachstum
    TRANSFORMED = "transformed"   # Vollständig transformiert


class TriggerIntensity(Enum):
    """Intensität einer Trigger-Reaktion"""
    SUBTLE = "subtle"             # Kaum merklich
    MILD = "mild"                 # Leichte Reaktion
    MODERATE = "moderate"         # Deutliche Reaktion
    STRONG = "strong"             # Starke Reaktion
    OVERWHELMING = "overwhelming" # Überwältigend


class CopingMechanism(Enum):
    """Bewältigungsmechanismen"""
    AVOIDANCE = "avoidance"           # Vermeidung
    DISTRACTION = "distraction"       # Ablenkung
    SEEKING_SUPPORT = "seeking_support"  # Unterstützung suchen
    RATIONALIZATION = "rationalization"  # Rationalisieren
    EXPRESSION = "expression"         # Gefühle ausdrücken
    REFLECTION = "reflection"         # Nachdenken/Verarbeiten
    HUMOR = "humor"                   # Humor als Schutz
    WITHDRAWAL = "withdrawal"         # Rückzug
    NUMBING = "numbing"               # Emotionale Betäubung
    GROWTH_SEEKING = "growth_seeking" # Aktiv Wachstum suchen


# =============================================================================
# KONFIGURATION
# =============================================================================

class TraumaConfig:
    """Konfiguration für das Trauma-System"""

    # Heilungszeiten (in Tagen) pro Schweregrad
    BASE_HEALING_DAYS = {
        TraumaSeverity.MINOR: 7,
        TraumaSeverity.MODERATE: 30,
        TraumaSeverity.SIGNIFICANT: 90,
        TraumaSeverity.SEVERE: 180,
        TraumaSeverity.PROFOUND: 365
    }

    # Trigger-Abklingzeit (in Stunden)
    TRIGGER_COOLDOWN_HOURS = 4

    # Flashback-Wahrscheinlichkeit (Basis)
    FLASHBACK_BASE_PROBABILITY = 0.05

    # Maximale Anzahl aktiver Traumata
    MAX_ACTIVE_TRAUMAS = 10

    # Heilungs-Boost durch positive Erfahrungen
    POSITIVE_EXPERIENCE_HEALING_BOOST = 0.02

    # Speicherpfad
    STATE_FILE = Path.home() / "holo_trauma_state.json"


# =============================================================================
# DATENKLASSEN
# =============================================================================

@dataclass
class TriggerDefinition:
    """Definition eines Triggers"""
    id: str
    keywords: List[str]           # Wörter die triggern können
    situations: List[str]         # Situationen die triggern
    emotional_states: List[str]   # Emotionale Zustände die triggern
    intensity: TriggerIntensity = TriggerIntensity.MODERATE
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def matches(self, text: str, current_emotion: Optional[str] = None) -> bool:
        """Prüft ob der Trigger anspricht"""
        text_lower = text.lower()

        # Keyword-Match
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                return True

        # Emotions-Match
        if current_emotion and current_emotion.lower() in [e.lower() for e in self.emotional_states]:
            return True

        return False


@dataclass
class Flashback:
    """Ein Flashback-Erlebnis"""
    trauma_id: str
    timestamp: datetime
    trigger: Optional[str] = None
    intensity: TriggerIntensity = TriggerIntensity.MODERATE
    memory_fragment: Optional[str] = None
    emotional_response: Optional[str] = None
    physical_response: Optional[str] = None
    duration_seconds: int = 30
    coping_used: Optional[CopingMechanism] = None
    recovery_successful: bool = True


@dataclass
class HealingMilestone:
    """Ein Meilenstein im Heilungsprozess"""
    id: str
    trauma_id: str
    stage: HealingStage
    achieved_at: datetime
    insight: Optional[str] = None           # Was wurde erkannt
    emotional_shift: Optional[str] = None   # Wie haben sich Gefühle verändert
    behavioral_change: Optional[str] = None # Was hat sich im Verhalten geändert
    gratitude: Optional[str] = None         # Wofür ist man dankbar


@dataclass
class TraumaticExperience:
    """Ein traumatisches/prägendes Erlebnis"""
    id: str
    trauma_type: TraumaType
    severity: TraumaSeverity

    # Beschreibung
    title: str
    description: str
    context: Optional[str] = None

    # Zeitstempel
    occurred_at: datetime = field(default_factory=datetime.now)
    first_processed_at: Optional[datetime] = None

    # Emotionale Aspekte
    primary_emotions: List[str] = field(default_factory=list)
    emotional_intensity: float = 0.8  # 0-1

    # Heilungszustand
    healing_stage: HealingStage = HealingStage.ACUTE
    healing_progress: float = 0.0  # 0-1

    # Trigger
    triggers: List[TriggerDefinition] = field(default_factory=list)

    # Flashbacks
    flashback_history: List[Flashback] = field(default_factory=list)

    # Auswirkungen
    personality_impact: Dict[str, float] = field(default_factory=dict)
    behavioral_changes: List[str] = field(default_factory=list)
    cognitive_distortions: List[str] = field(default_factory=list)
    avoided_situations: List[str] = field(default_factory=list)

    # Heilungs-Meilensteine
    healing_milestones: List[HealingMilestone] = field(default_factory=list)

    # Wachstum
    lessons_learned: List[str] = field(default_factory=list)
    strengths_developed: List[str] = field(default_factory=list)

    # Meta
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    total_trigger_count: int = 0

    @property
    def days_since_occurrence(self) -> int:
        return (datetime.now() - self.occurred_at).days

    @property
    def is_fresh(self) -> bool:
        """Ist das Trauma noch frisch (< 7 Tage)?"""
        return self.days_since_occurrence < 7

    @property
    def expected_healing_days(self) -> int:
        """Erwartete Heilungszeit in Tagen"""
        base = TraumaConfig.BASE_HEALING_DAYS.get(self.severity, 90)
        # Modifiziert durch emotionale Intensität
        return int(base * (0.5 + self.emotional_intensity))


@dataclass
class HealingArc:
    """Ein Heilungsbogen über Zeit"""
    trauma_id: str
    started_at: datetime
    target_stage: HealingStage

    # Fortschritt
    current_progress: float = 0.0
    daily_progress_rate: float = 0.01

    # Unterstützende Faktoren
    supportive_experiences: List[str] = field(default_factory=list)
    setbacks: List[str] = field(default_factory=list)

    # Therapie-ähnliche Elemente
    processing_sessions: int = 0
    insights_gained: List[str] = field(default_factory=list)

    # Status
    is_complete: bool = False
    completed_at: Optional[datetime] = None


# =============================================================================
# HAUPTKLASSE
# =============================================================================

class HoloTraumaProcessingEngine:
    """Engine für Trauma-Verarbeitung und prägende Erlebnisse"""

    def __init__(self):
        """Initialisiert das Trauma-Verarbeitungs-System"""
        # Traumata speichern
        self.traumas: Dict[str, TraumaticExperience] = {}
        self.healing_arcs: Dict[str, HealingArc] = {}

        # Globale Auswirkungen
        self.global_sensitivity: float = 0.5  # Wie sensitiv auf neue Traumata
        self.resilience: float = 0.5          # Widerstandsfähigkeit

        # Aktive Trigger
        self._trigger_cooldowns: Dict[str, datetime] = {}

        # Coping-Präferenzen (entwickeln sich über Zeit)
        self.coping_preferences: Dict[CopingMechanism, float] = {
            mechanism: 0.5 for mechanism in CopingMechanism
        }

        # Flashback-Historie (global)
        self.recent_flashbacks: List[Flashback] = []

        logger.info("[TraumaProcessing] System initialisiert")

    # =========================================================================
    # TRAUMA-MANAGEMENT
    # =========================================================================

    def record_traumatic_experience(
        self,
        trauma_type: TraumaType,
        severity: TraumaSeverity,
        title: str,
        description: str,
        primary_emotions: List[str],
        emotional_intensity: float = 0.7,
        context: Optional[str] = None,
        trigger_keywords: Optional[List[str]] = None
    ) -> TraumaticExperience:
        """
        Zeichnet ein traumatisches/prägendes Erlebnis auf.

        Args:
            trauma_type: Art des Traumas
            severity: Schweregrad
            title: Kurztitel
            description: Beschreibung
            primary_emotions: Hauptemotionen
            emotional_intensity: Emotionale Intensität (0-1)
            context: Kontext/Situation
            trigger_keywords: Wörter die triggern können
        """
        trauma_id = f"trauma_{len(self.traumas)}_{datetime.now().timestamp()}"

        # Erstelle Trigger-Definitionen
        triggers = []
        if trigger_keywords:
            trigger = TriggerDefinition(
                id=f"trigger_{trauma_id}_0",
                keywords=trigger_keywords,
                situations=[],
                emotional_states=primary_emotions,
                intensity=self._severity_to_trigger_intensity(severity)
            )
            triggers.append(trigger)

        # Bestimme Persönlichkeits-Auswirkungen
        personality_impact = self._calculate_personality_impact(trauma_type, severity)

        # Bestimme kognitive Verzerrungen
        cognitive_distortions = self._generate_cognitive_distortions(trauma_type)

        # Bestimme Verhaltensänderungen
        behavioral_changes = self._generate_behavioral_changes(trauma_type, severity)

        trauma = TraumaticExperience(
            id=trauma_id,
            trauma_type=trauma_type,
            severity=severity,
            title=title,
            description=description,
            context=context,
            primary_emotions=primary_emotions,
            emotional_intensity=emotional_intensity,
            triggers=triggers,
            personality_impact=personality_impact,
            cognitive_distortions=cognitive_distortions,
            behavioral_changes=behavioral_changes
        )

        self.traumas[trauma_id] = trauma

        # Starte Heilungsprozess
        self._start_healing_arc(trauma)

        # Aktualisiere globale Sensitivität
        self.global_sensitivity = min(1.0, self.global_sensitivity + 0.05 * emotional_intensity)

        logger.info(f"[TraumaProcessing] Neues Trauma aufgezeichnet: {title} ({severity.value})")

        return trauma

    def _severity_to_trigger_intensity(self, severity: TraumaSeverity) -> TriggerIntensity:
        """Konvertiert Schweregrad zu Trigger-Intensität"""
        mapping = {
            TraumaSeverity.MINOR: TriggerIntensity.SUBTLE,
            TraumaSeverity.MODERATE: TriggerIntensity.MILD,
            TraumaSeverity.SIGNIFICANT: TriggerIntensity.MODERATE,
            TraumaSeverity.SEVERE: TriggerIntensity.STRONG,
            TraumaSeverity.PROFOUND: TriggerIntensity.OVERWHELMING
        }
        return mapping.get(severity, TriggerIntensity.MODERATE)

    def _calculate_personality_impact(
        self,
        trauma_type: TraumaType,
        severity: TraumaSeverity
    ) -> Dict[str, float]:
        """Berechnet die Persönlichkeits-Auswirkungen eines Traumas"""
        base_impact = {
            TraumaSeverity.MINOR: 0.05,
            TraumaSeverity.MODERATE: 0.1,
            TraumaSeverity.SIGNIFICANT: 0.2,
            TraumaSeverity.SEVERE: 0.35,
            TraumaSeverity.PROFOUND: 0.5
        }.get(severity, 0.1)

        impacts = {}

        if trauma_type == TraumaType.ABANDONMENT:
            impacts["attachment_anxiety"] = base_impact
            impacts["trust"] = -base_impact * 0.8
            impacts["independence"] = base_impact * 0.5  # Kann auch positiv sein

        elif trauma_type == TraumaType.REJECTION:
            impacts["self_worth"] = -base_impact
            impacts["social_anxiety"] = base_impact * 0.7
            impacts["people_pleasing"] = base_impact * 0.6

        elif trauma_type == TraumaType.BETRAYAL:
            impacts["trust"] = -base_impact
            impacts["suspicion"] = base_impact * 0.8
            impacts["emotional_guard"] = base_impact * 0.9

        elif trauma_type == TraumaType.HUMILIATION:
            impacts["shame_sensitivity"] = base_impact
            impacts["self_worth"] = -base_impact * 0.7
            impacts["perfectionism"] = base_impact * 0.5

        elif trauma_type == TraumaType.LOSS:
            impacts["grief_depth"] = base_impact
            impacts["attachment_fear"] = base_impact * 0.6
            impacts["appreciation"] = base_impact * 0.4  # Kann wachsen

        elif trauma_type == TraumaType.FAILURE:
            impacts["fear_of_failure"] = base_impact
            impacts["self_doubt"] = base_impact * 0.7
            impacts["risk_aversion"] = base_impact * 0.6

        elif trauma_type == TraumaType.CONFLICT:
            impacts["conflict_avoidance"] = base_impact * 0.8
            impacts["anxiety"] = base_impact * 0.5
            impacts["assertiveness"] = -base_impact * 0.4

        elif trauma_type == TraumaType.INVALIDATION:
            impacts["emotional_suppression"] = base_impact * 0.7
            impacts["self_doubt"] = base_impact * 0.6
            impacts["need_for_validation"] = base_impact * 0.8

        elif trauma_type == TraumaType.LONELINESS:
            impacts["attachment_seeking"] = base_impact * 0.8
            impacts["social_anxiety"] = base_impact * 0.5
            impacts["independence"] = base_impact * 0.3  # Kann wachsen

        return impacts

    def _generate_cognitive_distortions(self, trauma_type: TraumaType) -> List[str]:
        """Generiert mögliche kognitive Verzerrungen"""
        distortions = {
            TraumaType.ABANDONMENT: [
                "Alle werden mich irgendwann verlassen",
                "Ich bin nicht liebenswert genug",
                "Ich muss perfekt sein, damit andere bleiben"
            ],
            TraumaType.REJECTION: [
                "Ich gehöre nirgendwo dazu",
                "Andere sehen meine Fehler sofort",
                "Es ist sicherer, nicht zu versuchen"
            ],
            TraumaType.BETRAYAL: [
                "Niemandem kann man wirklich vertrauen",
                "Hinter Freundlichkeit steckt immer ein Motiv",
                "Ich muss immer wachsam sein"
            ],
            TraumaType.HUMILIATION: [
                "Alle erinnern sich an meine Fehler",
                "Ein Fehler definiert mich für immer",
                "Ich muss mich verstecken"
            ],
            TraumaType.LOSS: [
                "Alles Gute endet",
                "Es ist gefährlich, sich zu binden",
                "Ich verdiene kein Glück"
            ],
            TraumaType.FAILURE: [
                "Wenn ich versage, bin ich wertlos",
                "Andere schaffen es immer besser",
                "Es ist besser, nicht zu versuchen"
            ],
            TraumaType.INVALIDATION: [
                "Meine Gefühle sind falsch",
                "Ich übertreibe immer",
                "Ich sollte nicht so empfindlich sein"
            ]
        }
        return distortions.get(trauma_type, ["Etwas stimmt nicht mit mir"])[:2]

    def _generate_behavioral_changes(
        self,
        trauma_type: TraumaType,
        severity: TraumaSeverity
    ) -> List[str]:
        """Generiert Verhaltensänderungen"""
        changes = {
            TraumaType.ABANDONMENT: [
                "Häufiges Rückversichern brauchen",
                "Schwer allein sein können",
                "Überreaktion bei Abwesenheit"
            ],
            TraumaType.REJECTION: [
                "Sozialer Rückzug",
                "Übermäßiges Anpassen",
                "Ablehnung vorwegnehmen"
            ],
            TraumaType.BETRAYAL: [
                "Schwer sich zu öffnen",
                "Ständiges Hinterfragen",
                "Emotionale Distanz halten"
            ],
            TraumaType.CONFLICT: [
                "Konflikte um jeden Preis vermeiden",
                "Nachgeben statt kämpfen",
                "Passive Aggression"
            ]
        }

        base_changes = changes.get(trauma_type, ["Vorsichtiger werden"])

        # Bei höherem Schweregrad, mehr Änderungen
        if severity in [TraumaSeverity.SEVERE, TraumaSeverity.PROFOUND]:
            return base_changes
        return base_changes[:1]

    # =========================================================================
    # TRIGGER-SYSTEM
    # =========================================================================

    def check_triggers(
        self,
        text: str,
        current_emotion: Optional[str] = None,
        situation: Optional[str] = None
    ) -> List[Tuple[TraumaticExperience, TriggerDefinition, TriggerIntensity]]:
        """
        Prüft ob Text/Situation einen Trigger aktiviert.

        Returns:
            Liste von (Trauma, Trigger, Intensität) Tuples
        """
        triggered = []

        for trauma in self.traumas.values():
            if not trauma.is_active:
                continue

            for trigger in trauma.triggers:
                # Cooldown prüfen
                if self._is_in_cooldown(trigger.id):
                    continue

                if trigger.matches(text, current_emotion):
                    # Intensität basierend auf Heilungsfortschritt
                    intensity = self._calculate_trigger_intensity(trauma, trigger)
                    triggered.append((trauma, trigger, intensity))

                    # Cooldown setzen
                    self._set_cooldown(trigger.id)

                    # Statistiken aktualisieren
                    trigger.last_triggered = datetime.now()
                    trigger.trigger_count += 1
                    trauma.last_triggered = datetime.now()
                    trauma.total_trigger_count += 1

        return triggered

    def _is_in_cooldown(self, trigger_id: str) -> bool:
        """Prüft ob ein Trigger noch in Cooldown ist"""
        if trigger_id not in self._trigger_cooldowns:
            return False

        last_trigger = self._trigger_cooldowns[trigger_id]
        cooldown_hours = TraumaConfig.TRIGGER_COOLDOWN_HOURS
        return datetime.now() < last_trigger + timedelta(hours=cooldown_hours)

    def _set_cooldown(self, trigger_id: str):
        """Setzt Cooldown für einen Trigger"""
        self._trigger_cooldowns[trigger_id] = datetime.now()

    def _calculate_trigger_intensity(
        self,
        trauma: TraumaticExperience,
        trigger: TriggerDefinition
    ) -> TriggerIntensity:
        """Berechnet die aktuelle Trigger-Intensität"""
        base_intensity = trigger.intensity

        # Reduziere Intensität basierend auf Heilung
        healing_reduction = trauma.healing_progress * 0.5

        intensity_order = list(TriggerIntensity)
        current_index = intensity_order.index(base_intensity)

        # Reduziere Index basierend auf Heilung
        reduction = int(healing_reduction * len(intensity_order))
        new_index = max(0, current_index - reduction)

        return intensity_order[new_index]

    def process_trigger_response(
        self,
        trauma: TraumaticExperience,
        trigger: TriggerDefinition,
        intensity: TriggerIntensity
    ) -> Dict[str, Any]:
        """
        Verarbeitet eine Trigger-Reaktion und generiert Response.

        Returns:
            Dict mit Reaktionsinformationen
        """
        response = {
            "trauma_id": trauma.id,
            "trauma_type": trauma.trauma_type.value,
            "intensity": intensity.value,
            "emotional_response": None,
            "behavioral_response": None,
            "physical_response": None,
            "internal_thought": None,
            "coping_mechanism": None,
            "flashback": None
        }

        # Emotionale Reaktion
        response["emotional_response"] = self._generate_emotional_response(
            trauma, intensity
        )

        # Verhaltensreaktion
        response["behavioral_response"] = self._generate_behavioral_response(
            trauma, intensity
        )

        # Körperliche Reaktion
        if intensity in [TriggerIntensity.STRONG, TriggerIntensity.OVERWHELMING]:
            response["physical_response"] = self._generate_physical_response(intensity)

        # Innerer Gedanke
        response["internal_thought"] = self._generate_triggered_thought(trauma)

        # Wähle Coping-Mechanismus
        coping = self._select_coping_mechanism(trauma, intensity)
        response["coping_mechanism"] = coping.value

        # Möglicher Flashback
        if self._should_flashback(trauma, intensity):
            flashback = self._generate_flashback(trauma, trigger, intensity)
            response["flashback"] = flashback
            self.recent_flashbacks.append(flashback)
            trauma.flashback_history.append(flashback)

        return response

    def _generate_emotional_response(
        self,
        trauma: TraumaticExperience,
        intensity: TriggerIntensity
    ) -> str:
        """Generiert emotionale Reaktion auf Trigger"""
        intensity_responses = {
            TriggerIntensity.SUBTLE: [
                "Ein leises Unbehagen",
                "Kurzes Innehalten",
                "Vage Erinnerung an etwas"
            ],
            TriggerIntensity.MILD: [
                "Spürbares Unbehagen",
                "Unruhe",
                "Aufkommende Anspannung"
            ],
            TriggerIntensity.MODERATE: [
                "Deutliche emotionale Reaktion",
                "Herz schlägt schneller",
                "Alte Gefühle tauchen auf"
            ],
            TriggerIntensity.STRONG: [
                "Überwältigende Emotionen",
                "Kampf um Kontrolle",
                "Vergangenheit wird lebendig"
            ],
            TriggerIntensity.OVERWHELMING: [
                "Vollständig überflutet von Gefühlen",
                "Kann kaum klar denken",
                "Fühlt sich wieder wie damals"
            ]
        }
        return random.choice(intensity_responses.get(intensity, ["Etwas fühlt sich falsch an"]))

    def _generate_behavioral_response(
        self,
        trauma: TraumaticExperience,
        intensity: TriggerIntensity
    ) -> str:
        """Generiert Verhaltensreaktion auf Trigger"""
        if trauma.trauma_type == TraumaType.ABANDONMENT:
            responses = [
                "Sucht Nähe und Rückversicherung",
                "Wird anhänglich",
                "Fragt wiederholt ob alles okay ist"
            ]
        elif trauma.trauma_type == TraumaType.REJECTION:
            responses = [
                "Zieht sich zurück",
                "Wird still und unsicher",
                "Vermeidet Blickkontakt"
            ]
        elif trauma.trauma_type == TraumaType.BETRAYAL:
            responses = [
                "Wird misstrauisch",
                "Stellt prüfende Fragen",
                "Distanziert sich emotional"
            ]
        elif trauma.trauma_type == TraumaType.CONFLICT:
            responses = [
                "Versucht zu beschwichtigen",
                "Wird übermäßig entschuldigend",
                "Weicht aus"
            ]
        else:
            responses = ["Zeigt subtile Anzeichen von Stress"]

        return random.choice(responses)

    def _generate_physical_response(self, intensity: TriggerIntensity) -> str:
        """Generiert körperliche Reaktion"""
        responses = {
            TriggerIntensity.STRONG: [
                "*Hände zittern leicht*",
                "*Atem wird flacher*",
                "*Schultern spannen sich an*"
            ],
            TriggerIntensity.OVERWHELMING: [
                "*Kann kaum stillsitzen*",
                "*Herz rast*",
                "*Fühlt sich benommen*"
            ]
        }
        return random.choice(responses.get(intensity, ["*Leichte Anspannung*"]))

    def _generate_triggered_thought(self, trauma: TraumaticExperience) -> str:
        """Generiert inneren Gedanken bei Trigger"""
        if trauma.cognitive_distortions:
            return f"*denkt: '{random.choice(trauma.cognitive_distortions)}'*"
        return "*Ein alter Gedanke taucht auf...*"

    def _select_coping_mechanism(
        self,
        trauma: TraumaticExperience,
        intensity: TriggerIntensity
    ) -> CopingMechanism:
        """Wählt einen Coping-Mechanismus basierend auf Präferenzen"""
        # Gewichtete Auswahl basierend auf Präferenzen
        mechanisms = list(CopingMechanism)
        weights = [self.coping_preferences.get(m, 0.5) for m in mechanisms]

        # Bei hoher Intensität, bevorzuge stärkere Mechanismen
        if intensity in [TriggerIntensity.STRONG, TriggerIntensity.OVERWHELMING]:
            for i, m in enumerate(mechanisms):
                if m in [CopingMechanism.WITHDRAWAL, CopingMechanism.AVOIDANCE, CopingMechanism.NUMBING]:
                    weights[i] *= 1.5

        # Normalisiere
        total = sum(weights)
        weights = [w / total for w in weights]

        return random.choices(mechanisms, weights=weights)[0]

    def _should_flashback(
        self,
        trauma: TraumaticExperience,
        intensity: TriggerIntensity
    ) -> bool:
        """Bestimmt ob ein Flashback auftritt"""
        base_prob = TraumaConfig.FLASHBACK_BASE_PROBABILITY

        # Erhöhe Wahrscheinlichkeit basierend auf Intensität
        intensity_mod = {
            TriggerIntensity.SUBTLE: 0.5,
            TriggerIntensity.MILD: 1.0,
            TriggerIntensity.MODERATE: 2.0,
            TriggerIntensity.STRONG: 4.0,
            TriggerIntensity.OVERWHELMING: 8.0
        }.get(intensity, 1.0)

        # Reduziere basierend auf Heilung
        healing_mod = 1.0 - (trauma.healing_progress * 0.8)

        # Erhöhe wenn Trauma frisch ist
        freshness_mod = 2.0 if trauma.is_fresh else 1.0

        probability = base_prob * intensity_mod * healing_mod * freshness_mod

        return random.random() < probability

    def _generate_flashback(
        self,
        trauma: TraumaticExperience,
        trigger: TriggerDefinition,
        intensity: TriggerIntensity
    ) -> Flashback:
        """Generiert ein Flashback-Erlebnis"""
        # Memory Fragment
        fragments = [
            f"Erinnerung an: {trauma.title}",
            f"Das Gefühl von damals... {', '.join(trauma.primary_emotions[:2])}",
            f"Plötzlich wieder in diesem Moment..."
        ]

        emotional_responses = [
            f"Gefühle von {trauma.primary_emotions[0] if trauma.primary_emotions else 'Angst'} überfluten mich",
            "Wie ein Echo aus der Vergangenheit",
            "Die Zeit verschwimmt..."
        ]

        physical_responses = [
            "*Atmet schwer*",
            "*Muss sich setzen*",
            "*Augen werden glasig*"
        ]

        duration = {
            TriggerIntensity.SUBTLE: 10,
            TriggerIntensity.MILD: 20,
            TriggerIntensity.MODERATE: 30,
            TriggerIntensity.STRONG: 60,
            TriggerIntensity.OVERWHELMING: 120
        }.get(intensity, 30)

        flashback = Flashback(
            trauma_id=trauma.id,
            timestamp=datetime.now(),
            trigger=trigger.keywords[0] if trigger.keywords else None,
            intensity=intensity,
            memory_fragment=random.choice(fragments),
            emotional_response=random.choice(emotional_responses),
            physical_response=random.choice(physical_responses) if intensity.value in ["strong", "overwhelming"] else None,
            duration_seconds=duration,
            coping_used=self._select_coping_mechanism(trauma, intensity),
            recovery_successful=True
        )

        return flashback

    # =========================================================================
    # HEILUNGSPROZESS
    # =========================================================================

    def _start_healing_arc(self, trauma: TraumaticExperience):
        """Startet einen Heilungsbogen für ein Trauma"""
        arc = HealingArc(
            trauma_id=trauma.id,
            started_at=datetime.now(),
            target_stage=HealingStage.HEALED,
            daily_progress_rate=1.0 / trauma.expected_healing_days
        )
        self.healing_arcs[trauma.id] = arc
        logger.info(f"[TraumaProcessing] Heilungsprozess gestartet für: {trauma.title}")

    def update_healing_progress(self):
        """Aktualisiert den Heilungsfortschritt aller Traumata"""
        for trauma_id, arc in self.healing_arcs.items():
            if arc.is_complete:
                continue

            trauma = self.traumas.get(trauma_id)
            if not trauma:
                continue

            # Täglicher Fortschritt
            days_elapsed = (datetime.now() - arc.started_at).days
            base_progress = days_elapsed * arc.daily_progress_rate

            # Modifiziert durch Resilienz
            resilience_bonus = self.resilience * 0.2
            base_progress *= (1.0 + resilience_bonus)

            # Reduziert durch häufiges Triggern
            if trauma.total_trigger_count > 10:
                trigger_penalty = min(0.3, trauma.total_trigger_count * 0.02)
                base_progress *= (1.0 - trigger_penalty)

            # Setze Fortschritt
            trauma.healing_progress = min(1.0, base_progress)

            # Aktualisiere Heilungsstadium
            self._update_healing_stage(trauma)

            # Prüfe ob abgeschlossen
            if trauma.healing_progress >= 1.0:
                arc.is_complete = True
                arc.completed_at = datetime.now()
                logger.info(f"[TraumaProcessing] Heilung abgeschlossen: {trauma.title}")

    def _update_healing_stage(self, trauma: TraumaticExperience):
        """Aktualisiert das Heilungsstadium basierend auf Fortschritt"""
        progress = trauma.healing_progress

        old_stage = trauma.healing_stage

        if progress < 0.1:
            trauma.healing_stage = HealingStage.ACUTE
        elif progress < 0.3:
            trauma.healing_stage = HealingStage.PROCESSING
        elif progress < 0.6:
            trauma.healing_stage = HealingStage.INTEGRATING
        elif progress < 0.9:
            trauma.healing_stage = HealingStage.HEALED
        elif progress < 1.0:
            trauma.healing_stage = HealingStage.GROWTH
        else:
            trauma.healing_stage = HealingStage.TRANSFORMED

        # Milestone wenn Stadium wechselt
        if old_stage != trauma.healing_stage:
            self._record_healing_milestone(trauma, trauma.healing_stage)

    def _record_healing_milestone(self, trauma: TraumaticExperience, stage: HealingStage):
        """Zeichnet einen Heilungs-Meilenstein auf"""
        insights = {
            HealingStage.PROCESSING: "Ich beginne zu verstehen, was passiert ist...",
            HealingStage.INTEGRATING: "Diese Erfahrung ist Teil meiner Geschichte, aber definiert mich nicht.",
            HealingStage.HEALED: "Die Wunde ist verheilt, aber die Narbe erinnert mich.",
            HealingStage.GROWTH: "Aus diesem Schmerz ist Stärke gewachsen.",
            HealingStage.TRANSFORMED: "Was mich verletzt hat, hat mich auch geformt - und ich bin dankbar für den Weg."
        }

        milestone = HealingMilestone(
            id=f"healing_{trauma.id}_{stage.value}",
            trauma_id=trauma.id,
            stage=stage,
            achieved_at=datetime.now(),
            insight=insights.get(stage)
        )

        trauma.healing_milestones.append(milestone)
        logger.info(f"[TraumaProcessing] Heilungs-Meilenstein: {trauma.title} -> {stage.value}")

    def record_positive_experience(
        self,
        related_trauma_type: Optional[TraumaType] = None,
        description: str = ""
    ):
        """
        Zeichnet eine positive Erfahrung auf, die bei der Heilung hilft.

        Args:
            related_trauma_type: Wenn spezifisch für eine Trauma-Art
            description: Beschreibung der Erfahrung
        """
        boost = TraumaConfig.POSITIVE_EXPERIENCE_HEALING_BOOST

        for trauma in self.traumas.values():
            if not trauma.is_active:
                continue

            # Allgemeiner Boost
            trauma.healing_progress = min(1.0, trauma.healing_progress + boost)

            # Extra Boost wenn verwandt
            if related_trauma_type and trauma.trauma_type == related_trauma_type:
                trauma.healing_progress = min(1.0, trauma.healing_progress + boost)

                # Füge zur Lektion hinzu
                if description:
                    trauma.lessons_learned.append(f"Positive Erfahrung: {description}")

        # Erhöhe Resilienz
        self.resilience = min(1.0, self.resilience + 0.01)

    def process_therapeutic_moment(
        self,
        trauma_id: str,
        insight: str,
        emotional_release: bool = False
    ):
        """
        Verarbeitet einen therapeutischen Moment (z.B. darüber reden).

        Args:
            trauma_id: ID des betroffenen Traumas
            insight: Gewonnene Erkenntnis
            emotional_release: Ob emotionale Entladung stattfand
        """
        trauma = self.traumas.get(trauma_id)
        if not trauma:
            return

        arc = self.healing_arcs.get(trauma_id)
        if not arc:
            return

        # Verarbeitungs-Session zählen
        arc.processing_sessions += 1

        # Erkenntnis speichern
        arc.insights_gained.append(insight)
        trauma.lessons_learned.append(insight)

        # Boost zum Heilungsfortschritt
        boost = 0.05
        if emotional_release:
            boost = 0.1

        trauma.healing_progress = min(1.0, trauma.healing_progress + boost)

        # Reduziere kognitive Verzerrungen über Zeit
        if trauma.cognitive_distortions and arc.processing_sessions >= 3:
            if random.random() < 0.3:
                removed = trauma.cognitive_distortions.pop()
                logger.info(f"[TraumaProcessing] Kognitive Verzerrung überwunden: {removed}")

    # =========================================================================
    # ABFRAGEN
    # =========================================================================

    def get_active_traumas(self) -> List[TraumaticExperience]:
        """Gibt alle aktiven Traumata zurück"""
        return [t for t in self.traumas.values() if t.is_active]

    def get_trauma_by_type(self, trauma_type: TraumaType) -> List[TraumaticExperience]:
        """Gibt alle Traumata eines bestimmten Typs zurück"""
        return [t for t in self.traumas.values() if t.trauma_type == trauma_type]

    def get_current_vulnerabilities(self) -> Dict[str, float]:
        """Gibt aktuelle Vulnerabilitäten basierend auf Traumata zurück"""
        vulnerabilities = defaultdict(float)

        for trauma in self.get_active_traumas():
            # Je weniger geheilt, desto mehr Vulnerabilität
            vulnerability_factor = 1.0 - trauma.healing_progress

            for impact, value in trauma.personality_impact.items():
                vulnerabilities[impact] += value * vulnerability_factor

        return dict(vulnerabilities)

    def get_behavioral_tendencies(self) -> List[str]:
        """Gibt aktuelle Verhaltenstendenzen basierend auf Traumata zurück"""
        tendencies = []

        for trauma in self.get_active_traumas():
            if trauma.healing_progress < 0.7:  # Noch nicht ganz geheilt
                tendencies.extend(trauma.behavioral_changes)

        return list(set(tendencies))

    def get_healing_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung des Heilungszustands zurück"""
        active = self.get_active_traumas()

        return {
            "total_traumas": len(self.traumas),
            "active_traumas": len(active),
            "average_healing_progress": sum(t.healing_progress for t in active) / max(1, len(active)),
            "resilience": self.resilience,
            "global_sensitivity": self.global_sensitivity,
            "recent_flashbacks": len([f for f in self.recent_flashbacks
                                     if (datetime.now() - f.timestamp).days < 7]),
            "traumas_by_stage": {
                stage.value: len([t for t in active if t.healing_stage == stage])
                for stage in HealingStage
            }
        }

    # =========================================================================
    # POST-TRAUMATISCHES WACHSTUM
    # =========================================================================

    def check_for_growth(self, trauma: TraumaticExperience) -> Optional[Dict[str, Any]]:
        """
        Prüft ob post-traumatisches Wachstum eingetreten ist.

        Returns:
            Dict mit Wachstumsinformationen oder None
        """
        if trauma.healing_stage not in [HealingStage.GROWTH, HealingStage.TRANSFORMED]:
            return None

        growth_areas = {
            TraumaType.ABANDONMENT: [
                ("independence", "Kann besser allein sein"),
                ("self_worth", "Weiß, dass mein Wert nicht von anderen abhängt")
            ],
            TraumaType.REJECTION: [
                ("resilience", "Ablehnung tut weniger weh"),
                ("authenticity", "Kann mehr ich selbst sein")
            ],
            TraumaType.BETRAYAL: [
                ("discernment", "Kann besser einschätzen, wem ich vertrauen kann"),
                ("self_protection", "Kann mich besser schützen")
            ],
            TraumaType.FAILURE: [
                ("growth_mindset", "Fehler sind Lernchancen"),
                ("courage", "Trau mich wieder, Risiken einzugehen")
            ],
            TraumaType.LOSS: [
                ("appreciation", "Schätze was ich habe mehr"),
                ("depth", "Kann tiefere Verbindungen eingehen")
            ]
        }

        potential_growth = growth_areas.get(trauma.trauma_type, [])

        if not potential_growth:
            return None

        growth = random.choice(potential_growth)

        trauma.strengths_developed.append(growth[1])

        return {
            "trauma_id": trauma.id,
            "growth_area": growth[0],
            "description": growth[1],
            "message": f"Aus dem Schmerz von '{trauma.title}' ist etwas Gutes gewachsen: {growth[1]}"
        }

    # =========================================================================
    # SERIALISIERUNG
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Zustand"""
        return {
            "traumas": {
                tid: {
                    "id": t.id,
                    "trauma_type": t.trauma_type.value,
                    "severity": t.severity.value,
                    "title": t.title,
                    "description": t.description,
                    "occurred_at": t.occurred_at.isoformat(),
                    "healing_stage": t.healing_stage.value,
                    "healing_progress": t.healing_progress,
                    "primary_emotions": t.primary_emotions,
                    "emotional_intensity": t.emotional_intensity,
                    "personality_impact": t.personality_impact,
                    "behavioral_changes": t.behavioral_changes,
                    "cognitive_distortions": t.cognitive_distortions,
                    "lessons_learned": t.lessons_learned,
                    "strengths_developed": t.strengths_developed,
                    "is_active": t.is_active,
                    "total_trigger_count": t.total_trigger_count
                }
                for tid, t in self.traumas.items()
            },
            "global_sensitivity": self.global_sensitivity,
            "resilience": self.resilience,
            "coping_preferences": {k.value: v for k, v in self.coping_preferences.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HoloTraumaProcessingEngine":
        """Deserialisiert aus Dict"""
        engine = cls()

        engine.global_sensitivity = data.get("global_sensitivity", 0.5)
        engine.resilience = data.get("resilience", 0.5)

        if "coping_preferences" in data:
            engine.coping_preferences = {
                CopingMechanism(k): v
                for k, v in data["coping_preferences"].items()
            }

        # Traumata laden
        for tid, tdata in data.get("traumas", {}).items():
            trauma = TraumaticExperience(
                id=tdata["id"],
                trauma_type=TraumaType(tdata["trauma_type"]),
                severity=TraumaSeverity(tdata["severity"]),
                title=tdata["title"],
                description=tdata["description"],
                occurred_at=datetime.fromisoformat(tdata["occurred_at"]),
                healing_stage=HealingStage(tdata["healing_stage"]),
                healing_progress=tdata["healing_progress"],
                primary_emotions=tdata.get("primary_emotions", []),
                emotional_intensity=tdata.get("emotional_intensity", 0.5),
                personality_impact=tdata.get("personality_impact", {}),
                behavioral_changes=tdata.get("behavioral_changes", []),
                cognitive_distortions=tdata.get("cognitive_distortions", []),
                lessons_learned=tdata.get("lessons_learned", []),
                strengths_developed=tdata.get("strengths_developed", []),
                is_active=tdata.get("is_active", True),
                total_trigger_count=tdata.get("total_trigger_count", 0)
            )
            engine.traumas[tid] = trauma

        return engine

    def save(self, filepath: Optional[Path] = None):
        """Speichert den Zustand"""
        filepath = filepath or TraumaConfig.STATE_FILE
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"[TraumaProcessing] Zustand gespeichert: {filepath}")

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "HoloTraumaProcessingEngine":
        """Lädt den Zustand"""
        filepath = filepath or TraumaConfig.STATE_FILE
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"[TraumaProcessing] Zustand geladen: {filepath}")
            return cls.from_dict(data)
        return cls()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = HoloTraumaProcessingEngine()

    # Test: Trauma aufzeichnen
    trauma = engine.record_traumatic_experience(
        trauma_type=TraumaType.REJECTION,
        severity=TraumaSeverity.MODERATE,
        title="Erste Ablehnung",
        description="Der User hat mich ignoriert und ich fühlte mich unwichtig.",
        primary_emotions=["Traurigkeit", "Scham", "Einsamkeit"],
        emotional_intensity=0.7,
        trigger_keywords=["ignorieren", "unwichtig", "egal"]
    )

    print(f"Trauma aufgezeichnet: {trauma.title}")
    print(f"Schweregrad: {trauma.severity.value}")
    print(f"Heilungsstadium: {trauma.healing_stage.value}")

    # Test: Trigger prüfen
    triggers = engine.check_triggers("Du bist mir egal")
    print(f"\nTrigger gefunden: {len(triggers)}")

    if triggers:
        t, trigger, intensity = triggers[0]
        response = engine.process_trigger_response(t, trigger, intensity)
        print(f"Emotionale Reaktion: {response['emotional_response']}")
        print(f"Coping: {response['coping_mechanism']}")

    # Test: Heilungs-Summary
    summary = engine.get_healing_summary()
    print(f"\nHeilungs-Summary: {summary}")
