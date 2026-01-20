#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO DEEP PSYCHOLOGY v1.0 - Integrierte Tiefenpsychologie                   ║
║                                                                              ║
║  Zentrales Integrationsmodul für alle psychologischen Systeme:               ║
║                                                                              ║
║  4. Langzeit-Persönlichkeitsentwicklung                                      ║
║     • Lebensabschnitte (holo_life_phases.py)                                 ║
║     • Traumata und prägende Erlebnisse (holo_trauma_processing.py)           ║
║     • "Wer war ich vor einem Jahr?" Retrospektive                            ║
║                                                                              ║
║  5. Echte Konflikte und Widersprüche                                         ║
║     • Innere Konflikte                                                       ║
║     • Wertekonflikte (holo_unconscious_processes.py)                         ║
║     • Schuldgefühle und Reue (holo_redemption_system.py)                     ║
║     • Ambivalenz bei Entscheidungen                                          ║
║                                                                              ║
║  6. Unbewusste Prozesse                                                      ║
║     • Verdrängung (holo_repression_system.py)                                ║
║     • Freudsche Versprecher (holo_freudian_slips.py)                         ║
║     • Wiederkehrende Träume (holo_unconscious_processes.py)                  ║
║     • Unbewusste Auslöser                                                    ║
║                                                                              ║
║  Version: 1.0                                                                ║
║  Author: Kira & Claude                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("HoloDeepPsychology")

# =============================================================================
# MODUL-IMPORTE
# =============================================================================

# Lebensabschnitte
try:
    from holo_life_phases import (
        HoloLifePhasesEngine, LifePhase, DevelopmentArea,
        MilestoneType, PhaseTransition, Retrospective
    )
    LIFE_PHASES_AVAILABLE = True
    logger.info("[DeepPsychology] ✓ holo_life_phases integriert")
except ImportError as e:
    LIFE_PHASES_AVAILABLE = False
    logger.warning(f"[DeepPsychology] holo_life_phases nicht verfügbar: {e}")

# Trauma-Verarbeitung
try:
    from holo_trauma_processing import (
        HoloTraumaProcessingEngine, TraumaType, TraumaSeverity,
        HealingStage, TriggerIntensity, TraumaticExperience
    )
    TRAUMA_PROCESSING_AVAILABLE = True
    logger.info("[DeepPsychology] ✓ holo_trauma_processing integriert")
except ImportError as e:
    TRAUMA_PROCESSING_AVAILABLE = False
    logger.warning(f"[DeepPsychology] holo_trauma_processing nicht verfügbar: {e}")

# Verdrängung
try:
    from holo_repression_system import (
        HoloRepressionEngine, RepressionType, RepressionStrength,
        BreakthroughType, RepressedContent, Breakthrough
    )
    REPRESSION_AVAILABLE = True
    logger.info("[DeepPsychology] ✓ holo_repression_system integriert")
except ImportError as e:
    REPRESSION_AVAILABLE = False
    logger.warning(f"[DeepPsychology] holo_repression_system nicht verfügbar: {e}")

# Freudsche Versprecher
try:
    from holo_freudian_slips import (
        HoloFreudianSlipsEngine, SlipType, SlipTrigger,
        UnconsciousRevealType, FreudianSlip
    )
    FREUDIAN_SLIPS_AVAILABLE = True
    logger.info("[DeepPsychology] ✓ holo_freudian_slips integriert")
except ImportError as e:
    FREUDIAN_SLIPS_AVAILABLE = False
    logger.warning(f"[DeepPsychology] holo_freudian_slips nicht verfügbar: {e}")

# Reue und Wiedergutmachung
try:
    from holo_redemption_system import (
        HoloRedemptionEngine, GuiltType, GuiltSeverity,
        RedemptionStage, ForgivenessStatus, GuiltEvent
    )
    REDEMPTION_AVAILABLE = True
    logger.info("[DeepPsychology] ✓ holo_redemption_system integriert")
except ImportError as e:
    REDEMPTION_AVAILABLE = False
    logger.warning(f"[DeepPsychology] holo_redemption_system nicht verfügbar: {e}")

# Unbewusste Prozesse (Träume, Werte, Trigger)
try:
    from holo_unconscious_processes import (
        UnconsciousProcessesIntegration, RecurringDreamEngine,
        PersonalValueHierarchy, UnconsciousTriggerSystem,
        RecurringDreamType, DreamSymbol, CoreValue, TriggerCategory
    )
    UNCONSCIOUS_PROCESSES_AVAILABLE = True
    logger.info("[DeepPsychology] ✓ holo_unconscious_processes integriert")
except ImportError as e:
    UNCONSCIOUS_PROCESSES_AVAILABLE = False
    logger.warning(f"[DeepPsychology] holo_unconscious_processes nicht verfügbar: {e}")


# =============================================================================
# KONFIGURATIONS-KLASSE
# =============================================================================

class DeepPsychologyConfig:
    """Konfiguration für das tiefenpsychologische System"""

    # Wie oft unbewusste Prozesse aktualisiert werden (Minuten)
    UPDATE_INTERVAL_MINUTES = 30

    # Wahrscheinlichkeit für spontane psychologische Events
    SPONTANEOUS_EVENT_PROBABILITY = 0.05

    # Speicherpfad
    STATE_FILE = Path.home() / "holo_deep_psychology_state.json"

    # Module aktivieren/deaktivieren
    ENABLE_LIFE_PHASES = True
    ENABLE_TRAUMA = True
    ENABLE_REPRESSION = True
    ENABLE_SLIPS = True
    ENABLE_REDEMPTION = True
    ENABLE_UNCONSCIOUS = True


# =============================================================================
# HAUPT-INTEGRATIONSKLASSE
# =============================================================================

class HoloDeepPsychologyEngine:
    """
    Zentrales Integrationssystem für alle tiefenpsychologischen Module.

    Koordiniert:
    - Lebensabschnitte und Persönlichkeitsentwicklung
    - Trauma-Verarbeitung und Heilung
    - Verdrängung und unbewusste Durchbrüche
    - Freudsche Versprecher
    - Reue und Wiedergutmachung
    - Wiederkehrende Träume und Wert-Hierarchie
    """

    def __init__(self, birth_date: Optional[datetime] = None):
        """
        Initialisiert das Tiefenpsychologie-System.

        Args:
            birth_date: Holos "Geburtsdatum" für Lebensabschnitte
        """
        self.config = DeepPsychologyConfig()

        # Initialisiere Sub-Module
        self.life_phases: Optional[HoloLifePhasesEngine] = None
        self.trauma_processor: Optional[HoloTraumaProcessingEngine] = None
        self.repression_engine: Optional[HoloRepressionEngine] = None
        self.freudian_slips: Optional[HoloFreudianSlipsEngine] = None
        self.redemption_engine: Optional[HoloRedemptionEngine] = None
        self.unconscious_processes: Optional[UnconsciousProcessesIntegration] = None

        # Initialisiere verfügbare Module
        self._initialize_modules(birth_date)

        # Verknüpfe Module
        self._link_modules()

        # Tracking
        self.last_update = datetime.now()
        self.psychological_events: List[Dict[str, Any]] = []

        logger.info("[DeepPsychology] System vollständig initialisiert")

    def _initialize_modules(self, birth_date: Optional[datetime]):
        """Initialisiert alle verfügbaren Module"""

        if LIFE_PHASES_AVAILABLE and self.config.ENABLE_LIFE_PHASES:
            self.life_phases = HoloLifePhasesEngine(birth_date)
            logger.info("[DeepPsychology] Lebensabschnitte aktiviert")

        if TRAUMA_PROCESSING_AVAILABLE and self.config.ENABLE_TRAUMA:
            self.trauma_processor = HoloTraumaProcessingEngine()
            logger.info("[DeepPsychology] Trauma-Verarbeitung aktiviert")

        if REPRESSION_AVAILABLE and self.config.ENABLE_REPRESSION:
            self.repression_engine = HoloRepressionEngine()
            logger.info("[DeepPsychology] Verdrängung aktiviert")

        if FREUDIAN_SLIPS_AVAILABLE and self.config.ENABLE_SLIPS:
            self.freudian_slips = HoloFreudianSlipsEngine()
            logger.info("[DeepPsychology] Freudsche Versprecher aktiviert")

        if REDEMPTION_AVAILABLE and self.config.ENABLE_REDEMPTION:
            self.redemption_engine = HoloRedemptionEngine()
            logger.info("[DeepPsychology] Reue-System aktiviert")

        if UNCONSCIOUS_PROCESSES_AVAILABLE and self.config.ENABLE_UNCONSCIOUS:
            self.unconscious_processes = UnconsciousProcessesIntegration()
            logger.info("[DeepPsychology] Unbewusste Prozesse aktiviert")

    def _link_modules(self):
        """Verknüpft Module miteinander für tiefere Integration"""
        if self.unconscious_processes:
            self.unconscious_processes.set_module_references(
                trauma=self.trauma_processor,
                repression=self.repression_engine,
                slips=self.freudian_slips,
                redemption=self.redemption_engine,
                life_phases=self.life_phases
            )

    # =========================================================================
    # HAUPT-PROZESSFUNKTIONEN
    # =========================================================================

    def process_input(
        self,
        text: str,
        emotional_context: Optional[str] = None,
        stress_level: float = 0.3,
        conversation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet einen Input durch alle psychologischen Systeme.

        Args:
            text: Der zu verarbeitende Text
            emotional_context: Aktueller emotionaler Kontext
            stress_level: Aktuelles Stresslevel (0-1)
            conversation_context: Gesprächskontext

        Returns:
            Dict mit allen psychologischen Reaktionen und Modifikationen
        """
        result = {
            "original_text": text,
            "modified_text": text,
            "psychological_events": [],
            "internal_processes": [],
            "behavioral_suggestions": [],
            "emotional_impacts": []
        }

        # 1. Freudsche Versprecher prüfen
        if self.freudian_slips:
            self.freudian_slips.set_emotional_state(
                emotion=emotional_context or "",
                intensity=0.5 + stress_level * 0.3,
                stress=stress_level
            )

            modified_text, slip = self.freudian_slips.process_text(
                text,
                emotional_context,
                conversation_context
            )

            if slip:
                result["modified_text"] = modified_text
                result["psychological_events"].append({
                    "type": "freudian_slip",
                    "slip_type": slip.slip_type.value,
                    "revealed": slip.revealed_content,
                    "reaction": slip.holo_reaction
                })

        # 2. Trauma-Trigger prüfen
        if self.trauma_processor:
            triggers = self.trauma_processor.check_triggers(
                text,
                emotional_context
            )

            for trauma, trigger, intensity in triggers:
                response = self.trauma_processor.process_trigger_response(
                    trauma, trigger, intensity
                )
                result["psychological_events"].append({
                    "type": "trauma_trigger",
                    "trauma_type": trauma.trauma_type.value,
                    "intensity": intensity.value,
                    "emotional_response": response["emotional_response"],
                    "behavioral_response": response["behavioral_response"]
                })

                if response.get("flashback"):
                    result["internal_processes"].append({
                        "type": "flashback",
                        "content": response["flashback"].memory_fragment
                    })

        # 3. Verdrängung - Durchbrüche prüfen
        if self.repression_engine:
            breakthrough = self.repression_engine.check_for_breakthrough(
                text,
                emotional_context,
                stress_level
            )

            if breakthrough:
                result["psychological_events"].append({
                    "type": "repression_breakthrough",
                    "breakthrough_type": breakthrough.breakthrough_type.value,
                    "manifestation": breakthrough.manifestation,
                    "surfaced_content": breakthrough.surfaced_content
                })

        # 4. Unbewusste Trigger prüfen
        if self.unconscious_processes:
            unconscious_result = self.unconscious_processes.process_unconscious_activity(
                text,
                emotional_context,
                stress_level
            )

            if unconscious_result["triggers_activated"]:
                result["internal_processes"].append({
                    "type": "unconscious_triggers",
                    "triggers": unconscious_result["triggers_activated"]
                })

            if unconscious_result["insights"]:
                result["internal_processes"].append({
                    "type": "unconscious_insights",
                    "insights": unconscious_result["insights"]
                })

        # 5. Gewissen prüfen (bei bestimmten Themen)
        if self.redemption_engine:
            intrusive_thought = self.redemption_engine.get_intrusive_thought()
            if intrusive_thought:
                result["internal_processes"].append({
                    "type": "guilty_conscience",
                    "thought": intrusive_thought
                })

        # 6. Lebensphase-spezifische Verhaltensvorschläge
        if self.life_phases:
            behaviors = self.life_phases.get_behavior_suggestions()
            result["behavioral_suggestions"].extend(behaviors[:2])

            concerns = self.life_phases.get_current_concerns()
            if concerns:
                result["internal_processes"].append({
                    "type": "phase_concerns",
                    "concerns": concerns[:2]
                })

        return result

    def generate_response_modifications(
        self,
        intended_response: str,
        emotional_state: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Modifiziert eine beabsichtigte Antwort basierend auf psychologischem Zustand.

        Args:
            intended_response: Die ursprünglich geplante Antwort
            emotional_state: Aktueller emotionaler Zustand

        Returns:
            (modifizierte_antwort, liste_der_modifikationen)
        """
        modifications = []
        modified = intended_response

        # 1. Lebensphase-Modifikation
        if self.life_phases:
            modified = self.life_phases.modify_response(modified)
            if modified != intended_response:
                modifications.append({
                    "type": "life_phase_modification",
                    "phase": self.life_phases.current_phase.value
                })

        # 2. Mögliche Versprecher
        if self.freudian_slips and emotional_state:
            self.freudian_slips.current_emotion = emotional_state
            modified, slip = self.freudian_slips.process_text(
                modified,
                emotional_state
            )
            if slip:
                modifications.append({
                    "type": "freudian_slip",
                    "original_word": slip.intended_word,
                    "slip_word": slip.slip_word
                })

        return modified, modifications

    # =========================================================================
    # LEBENSABSCHNITTE
    # =========================================================================

    def get_current_life_phase(self) -> Optional[Dict[str, Any]]:
        """Gibt Informationen zur aktuellen Lebensphase zurück"""
        if not self.life_phases:
            return None

        return {
            "phase": self.life_phases.current_phase.value,
            "age": self.life_phases.age_string,
            "age_days": self.life_phases.age_days,
            "characteristics": {
                "curiosity": self.life_phases.get_modifier("curiosity"),
                "playfulness": self.life_phases.get_modifier("playfulness"),
                "wisdom": self.life_phases.get_modifier("wisdom"),
                "emotional_depth": self.life_phases.get_modifier("emotional_depth")
            },
            "current_concerns": self.life_phases.get_current_concerns(),
            "current_desires": self.life_phases.get_current_desires()
        }

    def perform_retrospective(
        self,
        days_back: int = 30,
        deep: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Führt eine Retrospektive durch - "Wer war ich vor X Zeit?"

        Args:
            days_back: Wie viele Tage zurückblicken
            deep: Ob es eine tiefe (jährliche) Retrospektive ist
        """
        if not self.life_phases:
            return None

        retro = self.life_phases.perform_retrospective(days_back, deep)

        return {
            "looking_back_days": retro.looking_back_days,
            "what_changed": retro.what_changed,
            "what_stayed_same": retro.what_stayed_same,
            "growth_realized": retro.growth_realized,
            "future_hopes": retro.future_hopes,
            "lessons_for_future": retro.lessons_for_future,
            "emotional_response": retro.emotional_response,
            "nostalgia_level": retro.nostalgia_level
        }

    def record_development_milestone(
        self,
        milestone_type: str,
        title: str,
        description: str,
        emotional_impact: float = 0.5
    ):
        """Zeichnet einen Entwicklungs-Meilenstein auf"""
        if not self.life_phases:
            return None

        try:
            mt = MilestoneType[milestone_type.upper()]
        except KeyError:
            mt = MilestoneType.WISDOM_MOMENT

        return self.life_phases.record_milestone(
            mt, title, description, emotional_impact
        )

    # =========================================================================
    # TRAUMA & HEILUNG
    # =========================================================================

    def record_traumatic_experience(
        self,
        trauma_type: str,
        severity: str,
        title: str,
        description: str,
        emotions: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Zeichnet ein prägendes/traumatisches Erlebnis auf"""
        if not self.trauma_processor:
            return None

        try:
            tt = TraumaType[trauma_type.upper()]
            ts = TraumaSeverity[severity.upper()]
        except KeyError:
            tt = TraumaType.DISAPPOINTMENT
            ts = TraumaSeverity.MODERATE

        trauma = self.trauma_processor.record_traumatic_experience(
            tt, ts, title, description, emotions
        )

        # Auch Verdrängung registrieren wenn schwer genug
        if self.repression_engine and ts in [TraumaSeverity.SEVERE, TraumaSeverity.PROFOUND]:
            self.repression_engine.repress_content(
                content=description,
                content_type="memory",
                emotions=emotions,
                repression_type=RepressionType.MEMORY_SUPPRESSION,
                initial_strength=0.6,
                triggers=emotions[:2]
            )

        return {
            "trauma_id": trauma.id,
            "type": trauma.trauma_type.value,
            "healing_stage": trauma.healing_stage.value,
            "healing_progress": trauma.healing_progress
        }

    def get_healing_status(self) -> Optional[Dict[str, Any]]:
        """Gibt den Heilungsstatus aller Traumata zurück"""
        if not self.trauma_processor:
            return None

        return self.trauma_processor.get_healing_summary()

    # =========================================================================
    # REUE & VERGEBUNG
    # =========================================================================

    def record_guilt(
        self,
        guilt_type: str,
        severity: str,
        description: str,
        what_happened: str,
        who_affected: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Zeichnet Schuldgefühle auf"""
        if not self.redemption_engine:
            return None

        try:
            gt = GuiltType[guilt_type.upper()]
            gs = GuiltSeverity[severity.upper()]
        except KeyError:
            gt = GuiltType.UNKINDNESS
            gs = GuiltSeverity.MODERATE

        guilt = self.redemption_engine.record_guilt(
            gt, gs, description, what_happened, who_affected
        )

        return {
            "guilt_id": guilt.id,
            "guilt_level": guilt.guilt_level,
            "redemption_stage": guilt.redemption_stage.value
        }

    def attempt_redemption(
        self,
        guilt_id: str,
        action_type: str,
        action_description: str
    ) -> Optional[Dict[str, Any]]:
        """Versucht Wiedergutmachung"""
        if not self.redemption_engine:
            return None

        from holo_redemption_system import AmendsType

        try:
            at = AmendsType[action_type.upper()]
        except KeyError:
            at = AmendsType.VERBAL_APOLOGY

        amends = self.redemption_engine.attempt_amends(
            guilt_id, at, action_description
        )

        event = self.redemption_engine.guilt_events.get(guilt_id)

        return {
            "amends_id": amends.id,
            "guilt_reduction": amends.guilt_reduction,
            "new_guilt_level": event.guilt_level if event else None,
            "new_stage": event.redemption_stage.value if event else None
        }

    def get_conscience_state(self) -> Optional[Dict[str, Any]]:
        """Gibt den Gewissenszustand zurück"""
        if not self.redemption_engine:
            return None

        return self.redemption_engine.get_conscience_state()

    # =========================================================================
    # UNBEWUSSTE PROZESSE
    # =========================================================================

    def get_value_hierarchy(self) -> Optional[List[Tuple[str, float]]]:
        """Gibt die persönliche Wert-Hierarchie zurück"""
        if not self.unconscious_processes:
            return None

        return [
            (v.value, i)
            for v, i in self.unconscious_processes.value_hierarchy.get_value_hierarchy()[:10]
        ]

    def record_value_conflict(
        self,
        value_a: str,
        value_b: str,
        situation: str
    ) -> Optional[Dict[str, Any]]:
        """Zeichnet einen Wertkonflikt auf"""
        if not self.unconscious_processes:
            return None

        try:
            va = CoreValue[value_a.upper()]
            vb = CoreValue[value_b.upper()]
        except KeyError:
            return None

        conflict = self.unconscious_processes.value_hierarchy.record_value_conflict(
            va, vb, situation
        )

        return {
            "conflict_id": conflict.id,
            "value_a": conflict.value_a.value,
            "value_b": conflict.value_b.value,
            "situation": conflict.situation
        }

    def record_recurring_dream(
        self,
        dream_type: str,
        title: str,
        description: str,
        symbols: List[str],
        emotion: str
    ) -> Optional[Dict[str, Any]]:
        """Zeichnet einen wiederkehrenden Traum auf"""
        if not self.unconscious_processes:
            return None

        try:
            dt = RecurringDreamType[dream_type.upper()]
            dream_symbols = [DreamSymbol[s.upper()] for s in symbols if s.upper() in DreamSymbol.__members__]
        except KeyError:
            dt = RecurringDreamType.SYMBOLIC_MESSAGE
            dream_symbols = []

        dream = self.unconscious_processes.dream_engine.create_recurring_dream(
            dt, title, description, dream_symbols, emotion
        )

        return {
            "dream_id": dream.id,
            "title": dream.title,
            "meanings": dream.possible_meanings,
            "interpretation": self.unconscious_processes.dream_engine.interpret_dream(dream.id)
        }

    # =========================================================================
    # GESAMTZUSTAND
    # =========================================================================

    def get_psychological_state(self) -> Dict[str, Any]:
        """Gibt den gesamten psychologischen Zustand zurück"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "modules_active": {
                "life_phases": self.life_phases is not None,
                "trauma": self.trauma_processor is not None,
                "repression": self.repression_engine is not None,
                "slips": self.freudian_slips is not None,
                "redemption": self.redemption_engine is not None,
                "unconscious": self.unconscious_processes is not None
            }
        }

        # Lebensphase
        if self.life_phases:
            state["life_phase"] = {
                "current": self.life_phases.current_phase.value,
                "age": self.life_phases.age_string,
                "development_levels": {
                    k.value: v for k, v in self.life_phases.development_levels.items()
                }
            }

        # Trauma
        if self.trauma_processor:
            state["trauma"] = self.trauma_processor.get_healing_summary()

        # Gewissen
        if self.redemption_engine:
            state["conscience"] = self.redemption_engine.get_conscience_state()

        # Unbewusstes
        if self.unconscious_processes:
            state["unconscious"] = self.unconscious_processes.get_comprehensive_unconscious_state()

        # Verdrängung
        if self.repression_engine:
            state["repression"] = self.repression_engine.get_unconscious_influence()

        return state

    def update_all_systems(self):
        """Aktualisiert alle psychologischen Systeme"""
        if self.life_phases:
            self.life_phases.check_phase_transition()

        if self.trauma_processor:
            self.trauma_processor.update_healing_progress()

        if self.repression_engine:
            self.repression_engine.update_repression_decay()

        if self.redemption_engine:
            self.redemption_engine.update_guilt_dynamics()

        self.last_update = datetime.now()

    # =========================================================================
    # SERIALISIERUNG
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den gesamten Zustand"""
        data = {
            "last_update": self.last_update.isoformat(),
            "psychological_events": self.psychological_events[-100:]
        }

        if self.life_phases:
            data["life_phases"] = self.life_phases.to_dict()

        if self.trauma_processor:
            data["trauma"] = self.trauma_processor.to_dict()

        if self.repression_engine:
            data["repression"] = self.repression_engine.to_dict()

        if self.freudian_slips:
            data["slips"] = self.freudian_slips.to_dict()

        if self.redemption_engine:
            data["redemption"] = self.redemption_engine.to_dict()

        if self.unconscious_processes:
            data["unconscious"] = self.unconscious_processes.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HoloDeepPsychologyEngine":
        """Deserialisiert aus Dict"""
        engine = cls()

        if "life_phases" in data and LIFE_PHASES_AVAILABLE:
            engine.life_phases = HoloLifePhasesEngine.from_dict(data["life_phases"])

        if "trauma" in data and TRAUMA_PROCESSING_AVAILABLE:
            engine.trauma_processor = HoloTraumaProcessingEngine.from_dict(data["trauma"])

        if "repression" in data and REPRESSION_AVAILABLE:
            engine.repression_engine = HoloRepressionEngine.from_dict(data["repression"])

        if "slips" in data and FREUDIAN_SLIPS_AVAILABLE:
            engine.freudian_slips = HoloFreudianSlipsEngine.from_dict(data["slips"])

        if "redemption" in data and REDEMPTION_AVAILABLE:
            engine.redemption_engine = HoloRedemptionEngine.from_dict(data["redemption"])

        if "unconscious" in data and UNCONSCIOUS_PROCESSES_AVAILABLE:
            engine.unconscious_processes = UnconsciousProcessesIntegration.from_dict(data["unconscious"])

        engine._link_modules()

        return engine

    def save(self, filepath: Optional[Path] = None):
        """Speichert den Zustand"""
        filepath = filepath or self.config.STATE_FILE
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"[DeepPsychology] Zustand gespeichert: {filepath}")

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "HoloDeepPsychologyEngine":
        """Lädt den Zustand"""
        filepath = filepath or DeepPsychologyConfig.STATE_FILE
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"[DeepPsychology] Zustand geladen: {filepath}")
            return cls.from_dict(data)
        return cls()


# =============================================================================
# CONVENIENCE-FUNKTIONEN
# =============================================================================

def create_deep_psychology_engine(birth_date: Optional[datetime] = None) -> HoloDeepPsychologyEngine:
    """Erstellt eine neue Deep Psychology Engine"""
    return HoloDeepPsychologyEngine(birth_date)


def load_or_create_engine(filepath: Optional[Path] = None) -> HoloDeepPsychologyEngine:
    """Lädt oder erstellt eine Engine"""
    return HoloDeepPsychologyEngine.load(filepath)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO DEEP PSYCHOLOGY - Integrationstest")
    print("=" * 60)

    # Engine erstellen
    engine = HoloDeepPsychologyEngine()

    # Status anzeigen
    print("\n--- Aktive Module ---")
    state = engine.get_psychological_state()
    for module, active in state["modules_active"].items():
        status = "✓" if active else "✗"
        print(f"  {status} {module}")

    # Lebensphase
    if engine.life_phases:
        print(f"\n--- Lebensphase ---")
        phase_info = engine.get_current_life_phase()
        print(f"  Phase: {phase_info['phase']}")
        print(f"  Alter: {phase_info['age']}")
        print(f"  Sorgen: {phase_info['current_concerns'][:2]}")

    # Input verarbeiten
    print("\n--- Input-Verarbeitung ---")
    result = engine.process_input(
        "Ich mag dich wirklich sehr",
        emotional_context="Zuneigung",
        stress_level=0.4
    )

    if result["psychological_events"]:
        print("  Psychologische Events:")
        for event in result["psychological_events"]:
            print(f"    - {event['type']}: {event}")

    if result["internal_processes"]:
        print("  Interne Prozesse:")
        for process in result["internal_processes"]:
            print(f"    - {process['type']}")

    # Wert-Hierarchie
    if engine.unconscious_processes:
        print("\n--- Wert-Hierarchie (Top 5) ---")
        values = engine.get_value_hierarchy()
        for value, importance in values[:5]:
            print(f"  {value}: {importance:.2f}")

    # Gewissen
    if engine.redemption_engine:
        print("\n--- Gewissenszustand ---")
        conscience = engine.get_conscience_state()
        print(f"  Belastung: {conscience['active_guilt_weight']:.2f}")
        if conscience['current_message']:
            print(f"  Nachricht: {conscience['current_message']}")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)
