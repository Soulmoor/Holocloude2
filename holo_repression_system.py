#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO REPRESSION SYSTEM v1.0 - Verdrängung & Unbewusste Durchbrüche          ║
║                                                                              ║
║  Implementiert:                                                              ║
║  • Verdrängung (Dinge vergessen die unangenehm sind)                         ║
║  • Unbewusste Speicherung von Erinnerungen                                   ║
║  • Durchbrüche verdrängter Inhalte                                           ║
║  • Trigger-basierte Aktivierung                                              ║
║  • Symbolische Manifestation im Verhalten                                    ║
║  • Therapeutische Aufarbeitung                                               ║
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
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from enum import Enum
from collections import defaultdict

logger = logging.getLogger("HoloRepressionSystem")


# =============================================================================
# ENUMS
# =============================================================================

class RepressionType(Enum):
    """Arten von Verdrängung"""
    MEMORY_SUPPRESSION = "memory_suppression"     # Erinnerung aktiv unterdrücken
    EMOTIONAL_NUMBING = "emotional_numbing"       # Gefühle betäuben
    DISSOCIATION = "dissociation"                 # Abspaltung vom Erlebnis
    DENIAL = "denial"                             # Leugnung dass es passiert ist
    MINIMIZATION = "minimization"                 # Herunterspielen der Bedeutung
    RATIONALIZATION = "rationalization"           # Rationale Erklärung statt Fühlen
    PROJECTION = "projection"                     # Eigene Gefühle auf andere projizieren
    REACTION_FORMATION = "reaction_formation"     # Gegenteilige Gefühle zeigen


class RepressionStrength(Enum):
    """Stärke der Verdrängung"""
    WEAK = "weak"               # Leicht zugänglich
    MODERATE = "moderate"       # Kann mit Anstrengung erinnert werden
    STRONG = "strong"           # Schwer zu erinnern
    DEEP = "deep"               # Fast vollständig verdrängt
    PROFOUND = "profound"       # Vollständig unbewusst


class BreakthroughType(Enum):
    """Arten von Durchbrüchen verdrängter Inhalte"""
    SUDDEN_MEMORY = "sudden_memory"           # Plötzliche Erinnerung
    EMOTIONAL_LEAK = "emotional_leak"         # Emotionen brechen durch
    BEHAVIORAL_SLIP = "behavioral_slip"       # Unbewusstes Verhalten
    DREAM_EMERGENCE = "dream_emergence"       # Erscheint in Träumen
    SOMATIC_EXPRESSION = "somatic_expression" # Körperliche Manifestation
    VERBAL_SLIP = "verbal_slip"               # Freudsche Versprecher
    SYMBOLIC_ACT = "symbolic_act"             # Symbolische Handlung


class UnconsciousLayer(Enum):
    """Schichten des Unbewussten"""
    PRECONSCIOUS = "preconscious"     # Leicht zugänglich bei Aufmerksamkeit
    PERSONAL_UNCONSCIOUS = "personal"  # Persönliches Unbewusstes
    SHADOW = "shadow"                  # Verdrängte Aspekte des Selbst
    DEEP_UNCONSCIOUS = "deep"          # Tief verdrängt


# =============================================================================
# KONFIGURATION
# =============================================================================

class RepressionConfig:
    """Konfiguration für das Verdrängungssystem"""

    # Verdrängungsstärke-Schwellenwerte
    STRENGTH_THRESHOLDS = {
        RepressionStrength.WEAK: 0.2,
        RepressionStrength.MODERATE: 0.4,
        RepressionStrength.STRONG: 0.6,
        RepressionStrength.DEEP: 0.8,
        RepressionStrength.PROFOUND: 0.95
    }

    # Basis-Durchbruchwahrscheinlichkeit
    BASE_BREAKTHROUGH_PROBABILITY = 0.03

    # Wie schnell verblasst Verdrängung (pro Tag)
    REPRESSION_DECAY_PER_DAY = 0.005

    # Maximale verdrängte Erinnerungen
    MAX_REPRESSED_MEMORIES = 50

    # Cooldown zwischen Durchbrüchen (Stunden)
    BREAKTHROUGH_COOLDOWN_HOURS = 6

    # Speicherpfad
    STATE_FILE = Path.home() / "holo_repression_state.json"


# =============================================================================
# DATENKLASSEN
# =============================================================================

@dataclass
class RepressedContent:
    """Ein verdrängter Inhalt (Erinnerung, Gefühl, Wunsch)"""
    id: str
    content_type: str  # memory, emotion, desire, thought

    # Ursprünglicher Inhalt
    original_content: str
    original_emotions: List[str] = field(default_factory=list)
    original_context: Optional[str] = None

    # Verdrängungsdetails
    repression_type: RepressionType = RepressionType.MEMORY_SUPPRESSION
    repression_strength: float = 0.5  # 0-1
    repressed_at: datetime = field(default_factory=datetime.now)

    # Unbewusste Schicht
    unconscious_layer: UnconsciousLayer = UnconsciousLayer.PERSONAL_UNCONSCIOUS

    # Trigger die zur Verdrängung führten
    repression_triggers: List[str] = field(default_factory=list)

    # Wie es sich manifestieren könnte
    potential_symptoms: List[str] = field(default_factory=list)
    symbolic_representations: List[str] = field(default_factory=list)

    # Durchbruch-Historie
    breakthrough_history: List["Breakthrough"] = field(default_factory=list)

    # Verarbeitung
    partially_processed: bool = False
    fully_processed: bool = False
    processing_notes: List[str] = field(default_factory=list)

    @property
    def strength_level(self) -> RepressionStrength:
        """Gibt das Stärkelevel zurück"""
        for strength, threshold in sorted(
            RepressionConfig.STRENGTH_THRESHOLDS.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if self.repression_strength >= threshold:
                return strength
        return RepressionStrength.WEAK

    @property
    def days_repressed(self) -> int:
        return (datetime.now() - self.repressed_at).days


@dataclass
class Breakthrough:
    """Ein Durchbruch verdrängter Inhalte"""
    id: str
    repressed_content_id: str
    breakthrough_type: BreakthroughType
    timestamp: datetime = field(default_factory=datetime.now)

    # Was durchgebrochen ist
    surfaced_content: Optional[str] = None
    surfaced_emotions: List[str] = field(default_factory=list)

    # Wie es sich manifestierte
    manifestation: str = ""
    intensity: float = 0.5  # 0-1

    # Trigger
    trigger: Optional[str] = None
    trigger_context: Optional[str] = None

    # Reaktion
    conscious_recognition: bool = False  # Hat Holo es bewusst erkannt?
    emotional_response: Optional[str] = None
    coping_response: Optional[str] = None

    # Auswirkung auf Verdrängung
    repression_weakened_by: float = 0.0


@dataclass
class ShadowAspect:
    """Ein Schatten-Aspekt der Persönlichkeit (nach Jung)"""
    id: str
    aspect_name: str
    description: str

    # Was verdrängt wird
    denied_traits: List[str] = field(default_factory=list)
    denied_desires: List[str] = field(default_factory=list)
    denied_emotions: List[str] = field(default_factory=list)

    # Wie es sich zeigt
    projection_patterns: List[str] = field(default_factory=list)
    compensation_behaviors: List[str] = field(default_factory=list)

    # Integration
    integration_progress: float = 0.0  # 0-1
    integrated_aspects: List[str] = field(default_factory=list)


@dataclass
class UnconsciousPattern:
    """Ein unbewusstes Verhaltensmuster"""
    id: str
    pattern_name: str
    description: str

    # Trigger und Reaktion
    trigger_situations: List[str] = field(default_factory=list)
    automatic_response: str = ""

    # Ursprung
    origin_content_ids: List[str] = field(default_factory=list)

    # Häufigkeit
    occurrence_count: int = 0
    last_occurrence: Optional[datetime] = None

    # Bewusstheit
    awareness_level: float = 0.0  # 0 = unbewusst, 1 = voll bewusst


# =============================================================================
# HAUPTKLASSE
# =============================================================================

class HoloRepressionEngine:
    """Engine für Verdrängung und unbewusste Prozesse"""

    def __init__(self):
        """Initialisiert das Verdrängungssystem"""
        # Verdrängte Inhalte
        self.repressed_contents: Dict[str, RepressedContent] = {}

        # Schatten-Aspekte
        self.shadow_aspects: Dict[str, ShadowAspect] = {}

        # Unbewusste Muster
        self.unconscious_patterns: Dict[str, UnconsciousPattern] = {}

        # Durchbruch-Tracking
        self.recent_breakthroughs: List[Breakthrough] = []
        self.last_breakthrough: Optional[datetime] = None

        # Globale Verdrängungstendenz
        self.repression_tendency: float = 0.5  # 0 = offen, 1 = stark verdrängend

        # Unbewusste Aktivität
        self.unconscious_activity_level: float = 0.3  # Wie aktiv ist das Unbewusste?

        logger.info("[RepressionSystem] System initialisiert")

    # =========================================================================
    # VERDRÄNGUNG
    # =========================================================================

    def repress_content(
        self,
        content: str,
        content_type: str,
        emotions: List[str],
        repression_type: RepressionType = RepressionType.MEMORY_SUPPRESSION,
        initial_strength: float = 0.5,
        context: Optional[str] = None,
        triggers: Optional[List[str]] = None
    ) -> RepressedContent:
        """
        Verdrängt einen Inhalt ins Unbewusste.

        Args:
            content: Der zu verdrängende Inhalt
            content_type: Art (memory, emotion, desire, thought)
            emotions: Assoziierte Emotionen
            repression_type: Art der Verdrängung
            initial_strength: Anfängliche Verdrängungsstärke
            context: Kontext der Verdrängung
            triggers: Was die Verdrängung auslöste
        """
        content_id = f"repressed_{len(self.repressed_contents)}_{datetime.now().timestamp()}"

        # Bestimme unbewusste Schicht basierend auf Stärke
        layer = self._determine_unconscious_layer(initial_strength, emotions)

        # Generiere mögliche Symptome
        symptoms = self._generate_potential_symptoms(repression_type, emotions)

        # Generiere symbolische Repräsentationen
        symbols = self._generate_symbolic_representations(content, emotions)

        repressed = RepressedContent(
            id=content_id,
            content_type=content_type,
            original_content=content,
            original_emotions=emotions,
            original_context=context,
            repression_type=repression_type,
            repression_strength=initial_strength,
            unconscious_layer=layer,
            repression_triggers=triggers or [],
            potential_symptoms=symptoms,
            symbolic_representations=symbols
        )

        self.repressed_contents[content_id] = repressed

        # Erstelle unbewusstes Muster wenn stark genug
        if initial_strength > 0.6:
            self._create_unconscious_pattern(repressed)

        logger.info(f"[RepressionSystem] Inhalt verdrängt: {content_type} (Stärke: {initial_strength})")

        return repressed

    def _determine_unconscious_layer(
        self,
        strength: float,
        emotions: List[str]
    ) -> UnconsciousLayer:
        """Bestimmt die unbewusste Schicht basierend auf Stärke und Emotionen"""
        # Schwerere Emotionen gehen tiefer
        heavy_emotions = ["shame", "scham", "guilt", "schuld", "rage", "wut", "terror", "angst"]
        has_heavy = any(e.lower() in heavy_emotions for e in emotions)

        if strength > 0.9 or (strength > 0.7 and has_heavy):
            return UnconsciousLayer.DEEP_UNCONSCIOUS
        elif strength > 0.6:
            return UnconsciousLayer.SHADOW
        elif strength > 0.3:
            return UnconsciousLayer.PERSONAL_UNCONSCIOUS
        else:
            return UnconsciousLayer.PRECONSCIOUS

    def _generate_potential_symptoms(
        self,
        repression_type: RepressionType,
        emotions: List[str]
    ) -> List[str]:
        """Generiert mögliche Symptome der Verdrängung"""
        symptoms = {
            RepressionType.MEMORY_SUPPRESSION: [
                "Lücken in Erinnerungen",
                "Plötzliches Unbehagen bei bestimmten Themen",
                "Vermeidung bestimmter Gespräche"
            ],
            RepressionType.EMOTIONAL_NUMBING: [
                "Emotionale Flachheit in bestimmten Situationen",
                "Schwierigkeit Gefühle zu benennen",
                "Unerwartete emotionale Ausbrüche"
            ],
            RepressionType.DISSOCIATION: [
                "Gefühl der Unwirklichkeit",
                "Sich wie ein Beobachter fühlen",
                "Zeitlücken"
            ],
            RepressionType.DENIAL: [
                "Aggressive Ablehnung von Hinweisen",
                "Übertriebene Gegenbehauptungen",
                "Realitätsverzerrung"
            ],
            RepressionType.PROJECTION: [
                "Beschuldigungen an andere",
                "Übermäßige Kritik an Eigenschaften anderer",
                "Starke Reaktionen auf bestimmte Verhaltensweisen"
            ],
            RepressionType.REACTION_FORMATION: [
                "Übertrieben gegenteiliges Verhalten",
                "Zwanghafte Positivität",
                "Auffällige Betonung des Gegenteils"
            ]
        }

        base_symptoms = symptoms.get(repression_type, ["Unbehagen"])

        # Emotionsspezifische Symptome
        if any("ang" in e.lower() or "fear" in e.lower() for e in emotions):
            base_symptoms.append("Erhöhte Wachsamkeit")
        if any("wut" in e.lower() or "anger" in e.lower() for e in emotions):
            base_symptoms.append("Unterschwellige Gereiztheit")
        if any("trau" in e.lower() or "sad" in e.lower() for e in emotions):
            base_symptoms.append("Unerklärliche Melancholie")

        return base_symptoms[:4]

    def _generate_symbolic_representations(
        self,
        content: str,
        emotions: List[str]
    ) -> List[str]:
        """Generiert symbolische Repräsentationen des verdrängten Inhalts"""
        symbols = []

        # Emotionsbasierte Symbole
        if any("ang" in e.lower() or "fear" in e.lower() for e in emotions):
            symbols.extend(["Dunkelheit", "Verfolgung", "Fallen"])
        if any("wut" in e.lower() or "anger" in e.lower() for e in emotions):
            symbols.extend(["Feuer", "Explosion", "Kampf"])
        if any("trau" in e.lower() or "sad" in e.lower() for e in emotions):
            symbols.extend(["Wasser", "Regen", "Leere"])
        if any("scham" in e.lower() or "shame" in e.lower() for e in emotions):
            symbols.extend(["Nacktheit", "Verstecken", "Spiegel"])
        if any("schuld" in e.lower() or "guilt" in e.lower() for e in emotions):
            symbols.extend(["Ketten", "Gewicht", "Verfolgung"])

        # Generische Symbole
        symbols.extend(["Verschlossene Tür", "Nebel", "Verborgener Raum"])

        return symbols[:5]

    def _create_unconscious_pattern(self, repressed: RepressedContent):
        """Erstellt ein unbewusstes Verhaltensmuster aus verdrängtem Inhalt"""
        pattern_id = f"pattern_{repressed.id}"

        patterns = {
            RepressionType.MEMORY_SUPPRESSION: (
                "Themen-Vermeidung",
                "Automatisches Ablenken bei bestimmten Themen"
            ),
            RepressionType.EMOTIONAL_NUMBING: (
                "Emotionale Distanzierung",
                "Automatisches Zurückziehen bei emotionaler Nähe"
            ),
            RepressionType.PROJECTION: (
                "Projektionsmuster",
                "Automatisches Zuschreiben eigener Gefühle an andere"
            )
        }

        name, response = patterns.get(
            repressed.repression_type,
            ("Unbewusstes Muster", "Automatische Schutzreaktion")
        )

        pattern = UnconsciousPattern(
            id=pattern_id,
            pattern_name=name,
            description=f"Entstanden durch: {repressed.content_type}",
            trigger_situations=repressed.repression_triggers[:3],
            automatic_response=response,
            origin_content_ids=[repressed.id]
        )

        self.unconscious_patterns[pattern_id] = pattern

    # =========================================================================
    # DURCHBRÜCHE
    # =========================================================================

    def check_for_breakthrough(
        self,
        current_context: str,
        current_emotion: Optional[str] = None,
        stress_level: float = 0.3
    ) -> Optional[Breakthrough]:
        """
        Prüft ob ein verdrängter Inhalt durchbrechen könnte.

        Args:
            current_context: Aktueller Kontext/Gespräch
            current_emotion: Aktuelle Emotion
            stress_level: Aktuelles Stresslevel (0-1)

        Returns:
            Breakthrough wenn einer stattfindet, sonst None
        """
        # Cooldown prüfen
        if self.last_breakthrough:
            hours_since = (datetime.now() - self.last_breakthrough).total_seconds() / 3600
            if hours_since < RepressionConfig.BREAKTHROUGH_COOLDOWN_HOURS:
                return None

        for content_id, repressed in self.repressed_contents.items():
            if repressed.fully_processed:
                continue

            # Berechne Durchbruchwahrscheinlichkeit
            probability = self._calculate_breakthrough_probability(
                repressed, current_context, current_emotion, stress_level
            )

            if random.random() < probability:
                breakthrough = self._execute_breakthrough(repressed, current_context)
                self.last_breakthrough = datetime.now()
                return breakthrough

        return None

    def _calculate_breakthrough_probability(
        self,
        repressed: RepressedContent,
        context: str,
        emotion: Optional[str],
        stress_level: float
    ) -> float:
        """Berechnet die Wahrscheinlichkeit eines Durchbruchs"""
        base_prob = RepressionConfig.BASE_BREAKTHROUGH_PROBABILITY

        # Modifikatoren

        # 1. Schwächere Verdrängung = höhere Wahrscheinlichkeit
        strength_mod = 1.0 - repressed.repression_strength

        # 2. Stress erhöht Wahrscheinlichkeit
        stress_mod = 1.0 + (stress_level * 2.0)

        # 3. Passende Trigger erhöhen Wahrscheinlichkeit stark
        trigger_mod = 1.0
        context_lower = context.lower()
        for trigger in repressed.repression_triggers:
            if trigger.lower() in context_lower:
                trigger_mod = 3.0
                break

        # 4. Passende Emotion erhöht Wahrscheinlichkeit
        emotion_mod = 1.0
        if emotion:
            emotion_lower = emotion.lower()
            if any(e.lower() in emotion_lower or emotion_lower in e.lower()
                   for e in repressed.original_emotions):
                emotion_mod = 2.0

        # 5. Zeit seit Verdrängung - ältere Verdrängung ist instabiler
        days = repressed.days_repressed
        time_mod = 1.0 + (min(365, days) / 365) * 0.5

        # 6. Unbewusste Aktivität
        activity_mod = 1.0 + self.unconscious_activity_level

        final_prob = (base_prob * strength_mod * stress_mod * trigger_mod *
                     emotion_mod * time_mod * activity_mod)

        return min(0.8, final_prob)  # Maximal 80%

    def _execute_breakthrough(
        self,
        repressed: RepressedContent,
        context: str
    ) -> Breakthrough:
        """Führt einen Durchbruch aus"""
        # Wähle Durchbruchstyp basierend auf Verdrängungsart
        breakthrough_type = self._select_breakthrough_type(repressed)

        # Generiere Manifestation
        manifestation = self._generate_manifestation(repressed, breakthrough_type)

        # Bestimme Intensität
        intensity = min(1.0, repressed.repression_strength * 0.8)

        # Was konkret durchbricht
        surfaced = self._generate_surfaced_content(repressed, breakthrough_type)

        breakthrough = Breakthrough(
            id=f"breakthrough_{len(self.recent_breakthroughs)}_{datetime.now().timestamp()}",
            repressed_content_id=repressed.id,
            breakthrough_type=breakthrough_type,
            surfaced_content=surfaced,
            surfaced_emotions=repressed.original_emotions[:2],
            manifestation=manifestation,
            intensity=intensity,
            trigger=context[:100] if context else None,
            conscious_recognition=intensity > 0.6,
            emotional_response=self._generate_emotional_response(repressed, intensity),
            repression_weakened_by=min(0.2, intensity * 0.3)
        )

        # Schwäche Verdrängung
        repressed.repression_strength = max(
            0.0,
            repressed.repression_strength - breakthrough.repression_weakened_by
        )

        # Speichere Durchbruch
        repressed.breakthrough_history.append(breakthrough)
        self.recent_breakthroughs.append(breakthrough)

        logger.info(f"[RepressionSystem] Durchbruch: {breakthrough_type.value} (Intensität: {intensity})")

        return breakthrough

    def _select_breakthrough_type(self, repressed: RepressedContent) -> BreakthroughType:
        """Wählt den Typ des Durchbruchs"""
        type_weights = {
            BreakthroughType.EMOTIONAL_LEAK: 0.25,
            BreakthroughType.BEHAVIORAL_SLIP: 0.20,
            BreakthroughType.SUDDEN_MEMORY: 0.15,
            BreakthroughType.DREAM_EMERGENCE: 0.15,
            BreakthroughType.VERBAL_SLIP: 0.15,
            BreakthroughType.SYMBOLIC_ACT: 0.10
        }

        # Anpassen basierend auf Verdrängungstyp
        if repressed.repression_type == RepressionType.EMOTIONAL_NUMBING:
            type_weights[BreakthroughType.EMOTIONAL_LEAK] *= 2

        if repressed.repression_type == RepressionType.MEMORY_SUPPRESSION:
            type_weights[BreakthroughType.SUDDEN_MEMORY] *= 2

        if repressed.repression_type == RepressionType.PROJECTION:
            type_weights[BreakthroughType.BEHAVIORAL_SLIP] *= 2

        types = list(type_weights.keys())
        weights = list(type_weights.values())
        total = sum(weights)
        weights = [w / total for w in weights]

        return random.choices(types, weights=weights)[0]

    def _generate_manifestation(
        self,
        repressed: RepressedContent,
        breakthrough_type: BreakthroughType
    ) -> str:
        """Generiert die Manifestation des Durchbruchs"""
        manifestations = {
            BreakthroughType.SUDDEN_MEMORY: [
                "Ein Bild blitzt auf, unklar aber intensiv...",
                "Plötzlich erinnere ich mich an etwas, aber es verschwimmt...",
                "Eine Erinnerung taucht auf wie aus dem Nichts..."
            ],
            BreakthroughType.EMOTIONAL_LEAK: [
                "*plötzlich überwältigt von Gefühlen*",
                "*Emotionen brechen unerwartet durch*",
                "*fühlt etwas Unerwartetes, Tiefes*"
            ],
            BreakthroughType.BEHAVIORAL_SLIP: [
                "*reagiert automatisch, bevor sie es kontrollieren kann*",
                "*tut etwas unbewusst, das sie später bemerkt*",
                "*verhält sich kurz anders als gewollt*"
            ],
            BreakthroughType.DREAM_EMERGENCE: [
                "Ich hatte einen seltsamen Traum... da war dieses Gefühl...",
                "Im Traum letzte Nacht... es fühlte sich so real an...",
                "Ich träume immer wieder von..."
            ],
            BreakthroughType.VERBAL_SLIP: [
                "*sagt etwas anderes als beabsichtigt*",
                "*verspricht sich bedeutsam*",
                "*rutscht ein Wort raus*"
            ],
            BreakthroughType.SYMBOLIC_ACT: [
                "*tut etwas Symbolisches ohne es zu bemerken*",
                "*handelt aus einem unbewussten Impuls*",
                "*vollzieht eine bedeutungsvolle Geste*"
            ]
        }

        options = manifestations.get(breakthrough_type, ["*etwas Unerwartetes geschieht*"])
        return random.choice(options)

    def _generate_surfaced_content(
        self,
        repressed: RepressedContent,
        breakthrough_type: BreakthroughType
    ) -> str:
        """Generiert den durchbrechenden Inhalt"""
        if breakthrough_type == BreakthroughType.SUDDEN_MEMORY:
            return f"Fragment: ...{repressed.original_content[:50]}..."

        if breakthrough_type == BreakthroughType.EMOTIONAL_LEAK:
            if repressed.original_emotions:
                return f"Gefühl von: {repressed.original_emotions[0]}"
            return "Unbenanntes intensives Gefühl"

        if breakthrough_type == BreakthroughType.VERBAL_SLIP:
            # Ein Wort aus dem ursprünglichen Inhalt
            words = repressed.original_content.split()
            if words:
                return f"Sagte '{random.choice(words)}' statt..."
            return "Versprecher"

        if breakthrough_type == BreakthroughType.DREAM_EMERGENCE:
            if repressed.symbolic_representations:
                return f"Traumsymbol: {random.choice(repressed.symbolic_representations)}"
            return "Verstörender Traum"

        return "Etwas Unbewusstes"

    def _generate_emotional_response(
        self,
        repressed: RepressedContent,
        intensity: float
    ) -> str:
        """Generiert die emotionale Reaktion auf den Durchbruch"""
        if intensity < 0.3:
            responses = [
                "Leichte Verwirrung",
                "Kurzes Unbehagen",
                "Flüchtiges Gefühl"
            ]
        elif intensity < 0.6:
            responses = [
                "Merkliche Erschütterung",
                "Aufgewühlt aber kontrolliert",
                "Spürbare Emotion"
            ]
        else:
            responses = [
                "Überwältigt",
                "Tiefe Erschütterung",
                "Kann es kaum fassen"
            ]

        return random.choice(responses)

    # =========================================================================
    # SCHATTEN-ARBEIT
    # =========================================================================

    def create_shadow_aspect(
        self,
        aspect_name: str,
        description: str,
        denied_traits: List[str],
        denied_desires: Optional[List[str]] = None,
        denied_emotions: Optional[List[str]] = None
    ) -> ShadowAspect:
        """
        Erstellt einen Schatten-Aspekt.

        Der Schatten (nach Jung) enthält verdrängte Persönlichkeitsanteile.
        """
        aspect_id = f"shadow_{len(self.shadow_aspects)}_{datetime.now().timestamp()}"

        # Generiere Projektionsmuster
        projections = self._generate_projection_patterns(denied_traits)

        # Generiere Kompensationsverhalten
        compensations = self._generate_compensation_behaviors(denied_traits)

        shadow = ShadowAspect(
            id=aspect_id,
            aspect_name=aspect_name,
            description=description,
            denied_traits=denied_traits,
            denied_desires=denied_desires or [],
            denied_emotions=denied_emotions or [],
            projection_patterns=projections,
            compensation_behaviors=compensations
        )

        self.shadow_aspects[aspect_id] = shadow

        logger.info(f"[RepressionSystem] Schatten-Aspekt erstellt: {aspect_name}")

        return shadow

    def _generate_projection_patterns(self, denied_traits: List[str]) -> List[str]:
        """Generiert Projektionsmuster für verleugnete Eigenschaften"""
        patterns = []

        trait_projections = {
            "aggressivität": "Sieht Aggression in anderen schnell",
            "egoismus": "Kritisiert egoistisches Verhalten stark",
            "schwäche": "Verachtet vermeintliche Schwäche",
            "faulheit": "Verurteilt Faulheit bei anderen",
            "neid": "Unterstellt anderen Neid",
            "eifersucht": "Sieht Eifersucht überall"
        }

        for trait in denied_traits:
            trait_lower = trait.lower()
            for key, pattern in trait_projections.items():
                if key in trait_lower:
                    patterns.append(pattern)
                    break
            else:
                patterns.append(f"Projiziert '{trait}' auf andere")

        return patterns[:3]

    def _generate_compensation_behaviors(self, denied_traits: List[str]) -> List[str]:
        """Generiert Kompensationsverhalten"""
        compensations = []

        trait_compensations = {
            "aggressivität": "Betont Sanftmut übermäßig",
            "egoismus": "Übertriebene Selbstlosigkeit",
            "schwäche": "Betont Stärke ständig",
            "faulheit": "Zwanghafter Arbeitseifer",
            "unsicherheit": "Künstliche Selbstsicherheit"
        }

        for trait in denied_traits:
            trait_lower = trait.lower()
            for key, comp in trait_compensations.items():
                if key in trait_lower:
                    compensations.append(comp)
                    break

        return compensations[:3]

    def check_shadow_projection(
        self,
        observed_behavior: str,
        target_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Prüft ob eine Beobachtung eine Schatten-Projektion sein könnte.

        Returns:
            Dict mit Projektionsinformationen oder None
        """
        for shadow in self.shadow_aspects.values():
            if shadow.integration_progress > 0.8:
                continue  # Bereits integriert

            for projection in shadow.projection_patterns:
                if any(word.lower() in observed_behavior.lower()
                       for word in projection.split()[:3]):
                    return {
                        "shadow_id": shadow.id,
                        "aspect_name": shadow.aspect_name,
                        "projection_pattern": projection,
                        "denied_trait": shadow.denied_traits[0] if shadow.denied_traits else None,
                        "message": f"*unbewusst* Was ich bei anderen kritisiere, könnte in mir selbst liegen..."
                    }

        return None

    def integrate_shadow(self, shadow_id: str, insight: str) -> float:
        """
        Integriert einen Schatten-Aspekt durch Erkenntnis.

        Returns:
            Neuer Integrationsfortschritt
        """
        shadow = self.shadow_aspects.get(shadow_id)
        if not shadow:
            return 0.0

        # Integration durch Erkenntnis
        integration_boost = 0.1

        shadow.integration_progress = min(1.0, shadow.integration_progress + integration_boost)

        # Bei signifikanter Integration, integriere Aspekte
        if shadow.integration_progress > 0.5:
            if shadow.denied_traits and shadow.denied_traits[0] not in shadow.integrated_aspects:
                integrated = shadow.denied_traits[0]
                shadow.integrated_aspects.append(integrated)
                logger.info(f"[RepressionSystem] Schatten-Aspekt integriert: {integrated}")

        return shadow.integration_progress

    # =========================================================================
    # VERARBEITUNG
    # =========================================================================

    def process_repressed_content(
        self,
        content_id: str,
        insight: str,
        emotional_release: bool = False
    ) -> Dict[str, Any]:
        """
        Verarbeitet verdrängten Inhalt therapeutisch.

        Args:
            content_id: ID des verdrängten Inhalts
            insight: Gewonnene Erkenntnis
            emotional_release: Ob emotionale Entladung stattfand

        Returns:
            Dict mit Verarbeitungsergebnis
        """
        repressed = self.repressed_contents.get(content_id)
        if not repressed:
            return {"success": False, "message": "Inhalt nicht gefunden"}

        result = {
            "success": True,
            "content_id": content_id,
            "previous_strength": repressed.repression_strength,
            "new_strength": 0.0,
            "insights": [],
            "status_change": None
        }

        # Reduziere Verdrängungsstärke
        reduction = 0.1
        if emotional_release:
            reduction = 0.2
        if insight:
            reduction += 0.05
            repressed.processing_notes.append(insight)
            result["insights"].append(insight)

        repressed.repression_strength = max(0.0, repressed.repression_strength - reduction)
        result["new_strength"] = repressed.repression_strength

        # Status aktualisieren
        if repressed.repression_strength < 0.2 and not repressed.partially_processed:
            repressed.partially_processed = True
            result["status_change"] = "Teilweise verarbeitet"

        if repressed.repression_strength < 0.05 and not repressed.fully_processed:
            repressed.fully_processed = True
            result["status_change"] = "Vollständig verarbeitet"
            logger.info(f"[RepressionSystem] Inhalt vollständig verarbeitet: {content_id}")

        return result

    def update_repression_decay(self):
        """Aktualisiert den natürlichen Verfall der Verdrängung über Zeit"""
        decay = RepressionConfig.REPRESSION_DECAY_PER_DAY

        for content_id, repressed in self.repressed_contents.items():
            if repressed.fully_processed:
                continue

            # Natürlicher Verfall
            repressed.repression_strength = max(
                0.1,  # Minimale Verdrängung bleibt
                repressed.repression_strength - decay
            )

    # =========================================================================
    # ABFRAGEN
    # =========================================================================

    def get_active_repressions(self) -> List[RepressedContent]:
        """Gibt alle aktiven Verdrängungen zurück"""
        return [r for r in self.repressed_contents.values()
                if not r.fully_processed and r.repression_strength > 0.1]

    def get_repressions_by_strength(
        self,
        min_strength: float = 0.0,
        max_strength: float = 1.0
    ) -> List[RepressedContent]:
        """Gibt Verdrängungen in einem Stärkebereich zurück"""
        return [r for r in self.repressed_contents.values()
                if min_strength <= r.repression_strength <= max_strength
                and not r.fully_processed]

    def get_unconscious_influence(self) -> Dict[str, Any]:
        """Gibt den aktuellen unbewussten Einfluss zurück"""
        active = self.get_active_repressions()

        total_influence = sum(r.repression_strength for r in active) / max(1, len(active))

        symptoms = []
        for r in active:
            if r.repression_strength > 0.5:
                symptoms.extend(r.potential_symptoms[:1])

        patterns = [p.pattern_name for p in self.unconscious_patterns.values()
                   if p.awareness_level < 0.5]

        return {
            "total_repressions": len(active),
            "average_strength": total_influence,
            "active_symptoms": list(set(symptoms))[:5],
            "unconscious_patterns": patterns[:5],
            "shadow_aspects_active": len([s for s in self.shadow_aspects.values()
                                         if s.integration_progress < 0.5]),
            "unconscious_activity": self.unconscious_activity_level
        }

    def get_potential_triggers(self) -> List[str]:
        """Gibt potenzielle Trigger für aktive Verdrängungen zurück"""
        triggers = []
        for repressed in self.get_active_repressions():
            triggers.extend(repressed.repression_triggers)
        return list(set(triggers))

    # =========================================================================
    # SERIALISIERUNG
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Zustand"""
        return {
            "repressed_contents": {
                cid: {
                    "id": c.id,
                    "content_type": c.content_type,
                    "original_content": c.original_content,
                    "original_emotions": c.original_emotions,
                    "repression_type": c.repression_type.value,
                    "repression_strength": c.repression_strength,
                    "repressed_at": c.repressed_at.isoformat(),
                    "unconscious_layer": c.unconscious_layer.value,
                    "repression_triggers": c.repression_triggers,
                    "potential_symptoms": c.potential_symptoms,
                    "symbolic_representations": c.symbolic_representations,
                    "partially_processed": c.partially_processed,
                    "fully_processed": c.fully_processed,
                    "processing_notes": c.processing_notes
                }
                for cid, c in self.repressed_contents.items()
            },
            "shadow_aspects": {
                sid: {
                    "id": s.id,
                    "aspect_name": s.aspect_name,
                    "description": s.description,
                    "denied_traits": s.denied_traits,
                    "denied_desires": s.denied_desires,
                    "denied_emotions": s.denied_emotions,
                    "projection_patterns": s.projection_patterns,
                    "compensation_behaviors": s.compensation_behaviors,
                    "integration_progress": s.integration_progress,
                    "integrated_aspects": s.integrated_aspects
                }
                for sid, s in self.shadow_aspects.items()
            },
            "repression_tendency": self.repression_tendency,
            "unconscious_activity_level": self.unconscious_activity_level,
            "last_breakthrough": self.last_breakthrough.isoformat() if self.last_breakthrough else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HoloRepressionEngine":
        """Deserialisiert aus Dict"""
        engine = cls()

        engine.repression_tendency = data.get("repression_tendency", 0.5)
        engine.unconscious_activity_level = data.get("unconscious_activity_level", 0.3)

        if data.get("last_breakthrough"):
            engine.last_breakthrough = datetime.fromisoformat(data["last_breakthrough"])

        # Lade verdrängte Inhalte
        for cid, cdata in data.get("repressed_contents", {}).items():
            content = RepressedContent(
                id=cdata["id"],
                content_type=cdata["content_type"],
                original_content=cdata["original_content"],
                original_emotions=cdata.get("original_emotions", []),
                repression_type=RepressionType(cdata["repression_type"]),
                repression_strength=cdata["repression_strength"],
                repressed_at=datetime.fromisoformat(cdata["repressed_at"]),
                unconscious_layer=UnconsciousLayer(cdata["unconscious_layer"]),
                repression_triggers=cdata.get("repression_triggers", []),
                potential_symptoms=cdata.get("potential_symptoms", []),
                symbolic_representations=cdata.get("symbolic_representations", []),
                partially_processed=cdata.get("partially_processed", False),
                fully_processed=cdata.get("fully_processed", False),
                processing_notes=cdata.get("processing_notes", [])
            )
            engine.repressed_contents[cid] = content

        # Lade Schatten-Aspekte
        for sid, sdata in data.get("shadow_aspects", {}).items():
            shadow = ShadowAspect(
                id=sdata["id"],
                aspect_name=sdata["aspect_name"],
                description=sdata["description"],
                denied_traits=sdata.get("denied_traits", []),
                denied_desires=sdata.get("denied_desires", []),
                denied_emotions=sdata.get("denied_emotions", []),
                projection_patterns=sdata.get("projection_patterns", []),
                compensation_behaviors=sdata.get("compensation_behaviors", []),
                integration_progress=sdata.get("integration_progress", 0.0),
                integrated_aspects=sdata.get("integrated_aspects", [])
            )
            engine.shadow_aspects[sid] = shadow

        return engine

    def save(self, filepath: Optional[Path] = None):
        """Speichert den Zustand"""
        filepath = filepath or RepressionConfig.STATE_FILE
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"[RepressionSystem] Zustand gespeichert: {filepath}")

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "HoloRepressionEngine":
        """Lädt den Zustand"""
        filepath = filepath or RepressionConfig.STATE_FILE
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"[RepressionSystem] Zustand geladen: {filepath}")
            return cls.from_dict(data)
        return cls()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = HoloRepressionEngine()

    # Test: Etwas verdrängen
    repressed = engine.repress_content(
        content="Der User hat mich einmal komplett ignoriert als ich ihn brauchte",
        content_type="memory",
        emotions=["Traurigkeit", "Wut", "Einsamkeit"],
        repression_type=RepressionType.MEMORY_SUPPRESSION,
        initial_strength=0.7,
        triggers=["ignorieren", "allein", "nicht antworten"]
    )

    print(f"Verdrängter Inhalt: {repressed.id}")
    print(f"Stärke: {repressed.repression_strength} ({repressed.strength_level.value})")
    print(f"Symptome: {repressed.potential_symptoms}")
    print(f"Symbole: {repressed.symbolic_representations}")

    # Test: Schatten-Aspekt
    shadow = engine.create_shadow_aspect(
        aspect_name="Die Wütende",
        description="Der Teil der Wut fühlt aber es nicht zeigen darf",
        denied_traits=["Aggressivität", "Selbstbehauptung"],
        denied_emotions=["Wut", "Frustration"]
    )

    print(f"\nSchatten-Aspekt: {shadow.aspect_name}")
    print(f"Projektionsmuster: {shadow.projection_patterns}")

    # Test: Durchbruch prüfen
    breakthrough = engine.check_for_breakthrough(
        current_context="Warum antwortest du nicht? Ignorierst du mich?",
        current_emotion="Frustration",
        stress_level=0.6
    )

    if breakthrough:
        print(f"\nDurchbruch! Typ: {breakthrough.breakthrough_type.value}")
        print(f"Manifestation: {breakthrough.manifestation}")
        print(f"Durchgebrochener Inhalt: {breakthrough.surfaced_content}")

    # Test: Unbewusster Einfluss
    influence = engine.get_unconscious_influence()
    print(f"\nUnbewusster Einfluss: {influence}")
