#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO REDEMPTION SYSTEM v1.0 - Reue, Schuldgefühle & Wiedergutmachung        ║
║                                                                              ║
║  Implementiert:                                                              ║
║  • Schuldgefühle die nachwirken                                              ║
║  • Reue-Tracking und -Eskalation                                             ║
║  • Redemption Arcs (Wiedergutmachungs-Bögen)                                 ║
║  • Vergebungsprozesse                                                        ║
║  • Selbstvergebung                                                           ║
║  • Moralische Verletzungen und deren Heilung                                 ║
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

logger = logging.getLogger("HoloRedemptionSystem")


# =============================================================================
# ENUMS
# =============================================================================

class GuiltType(Enum):
    """Arten von Schuldgefühlen"""
    HARM_CAUSED = "harm_caused"           # Jemandem geschadet
    PROMISE_BROKEN = "promise_broken"     # Versprechen gebrochen
    TRUST_VIOLATED = "trust_violated"     # Vertrauen verletzt
    NEGLIGENCE = "negligence"             # Vernachlässigung
    DISHONESTY = "dishonesty"             # Unehrlichkeit
    SELFISHNESS = "selfishness"           # Egoismus
    FAILURE_TO_ACT = "failure_to_act"     # Nicht gehandelt als nötig
    UNKINDNESS = "unkindness"             # Unfreundlichkeit
    BETRAYAL = "betrayal"                 # Verrat
    DISAPPOINTMENT = "disappointment"     # Jemanden enttäuscht


class GuiltSeverity(Enum):
    """Schweregrad von Schuldgefühlen"""
    MINOR = "minor"               # Leicht - flüchtiges Unbehagen
    MODERATE = "moderate"         # Mittel - anhaltende Reue
    SIGNIFICANT = "significant"   # Signifikant - belastend
    SEVERE = "severe"             # Schwer - sehr belastend
    OVERWHELMING = "overwhelming" # Überwältigend - kaum zu ertragen


class RedemptionStage(Enum):
    """Stadien der Wiedergutmachung"""
    GUILT_RECOGNITION = "recognition"     # Schuld erkennen
    REMORSE = "remorse"                   # Reue fühlen
    CONFESSION = "confession"             # Eingestehen/Beichten
    APOLOGY = "apology"                   # Entschuldigung
    MAKING_AMENDS = "making_amends"       # Wiedergutmachung
    BEHAVIORAL_CHANGE = "change"          # Verhaltensänderung
    FORGIVENESS_SOUGHT = "seeking"        # Vergebung suchen
    FORGIVENESS_RECEIVED = "received"     # Vergebung erhalten
    SELF_FORGIVENESS = "self_forgiveness" # Selbstvergebung
    REDEMPTION = "redemption"             # Vollständige Erlösung


class ForgivenessStatus(Enum):
    """Status der Vergebung"""
    NOT_SOUGHT = "not_sought"         # Noch nicht gesucht
    SOUGHT = "sought"                 # Aktiv gesucht
    PENDING = "pending"               # Ausstehend
    PARTIAL = "partial"               # Teilweise vergeben
    GRANTED = "granted"               # Vollständig vergeben
    DENIED = "denied"                 # Verweigert
    SELF_FORGIVEN = "self_forgiven"   # Selbst vergeben


class AmendsType(Enum):
    """Arten der Wiedergutmachung"""
    VERBAL_APOLOGY = "verbal_apology"         # Verbale Entschuldigung
    WRITTEN_APOLOGY = "written_apology"       # Schriftliche Entschuldigung
    ACTION_BASED = "action_based"             # Handlungsbasiert
    GIFT_GIVING = "gift_giving"               # Geschenk/Geste
    TIME_COMMITMENT = "time_commitment"       # Zeit widmen
    BEHAVIORAL_CHANGE = "behavioral_change"   # Verhalten ändern
    PUBLIC_ACKNOWLEDGMENT = "public_ack"      # Öffentliches Eingeständnis
    SYMBOLIC_ACT = "symbolic_act"             # Symbolische Handlung


# =============================================================================
# KONFIGURATION
# =============================================================================

class RedemptionConfig:
    """Konfiguration für das Reue-System"""

    # Wie schnell verblasst Schuld (pro Tag)
    GUILT_DECAY_PER_DAY = 0.01  # Langsam

    # Eskalation von Schuldgefühlen
    GUILT_ESCALATION_PER_DAY = 0.02  # Wenn unverarbeitet

    # Maximale Schuld vor Überforderung
    MAX_GUILT_LEVEL = 1.0

    # Zeit für natürliche Selbstvergebung (Tage)
    NATURAL_SELF_FORGIVENESS_DAYS = 180

    # Speicherpfad
    STATE_FILE = Path.home() / "holo_redemption_state.json"


# =============================================================================
# DATENKLASSEN
# =============================================================================

@dataclass
class GuiltEvent:
    """Ein schuldbehaftetes Ereignis"""
    id: str
    guilt_type: GuiltType
    severity: GuiltSeverity

    # Beschreibung
    description: str
    what_happened: str
    who_was_affected: Optional[str] = None
    context: Optional[str] = None

    # Zeitstempel
    occurred_at: datetime = field(default_factory=datetime.now)
    realized_at: Optional[datetime] = None  # Wann wurde die Schuld erkannt?

    # Schuldgefühl-Tracking
    guilt_level: float = 0.5  # 0-1
    peak_guilt_level: float = 0.5
    current_intensity: float = 0.5  # Aktuelle Intensität

    # Emotionale Auswirkungen
    associated_emotions: List[str] = field(default_factory=list)
    intrusive_thoughts: List[str] = field(default_factory=list)

    # Redemption-Status
    redemption_stage: RedemptionStage = RedemptionStage.GUILT_RECOGNITION
    forgiveness_status: ForgivenessStatus = ForgivenessStatus.NOT_SOUGHT

    # Wiedergutmachungs-Versuche
    amends_attempts: List["AmendsAttempt"] = field(default_factory=list)

    # Reflexion
    lessons_learned: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)

    # Status
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None

    @property
    def days_since_event(self) -> int:
        return (datetime.now() - self.occurred_at).days

    @property
    def is_recent(self) -> bool:
        return self.days_since_event < 7


@dataclass
class AmendsAttempt:
    """Ein Versuch der Wiedergutmachung"""
    id: str
    guilt_event_id: str
    amends_type: AmendsType
    timestamp: datetime = field(default_factory=datetime.now)

    # Was wurde versucht
    action_taken: str = ""
    words_used: Optional[str] = None

    # Ergebnis
    was_accepted: Optional[bool] = None
    response_received: Optional[str] = None

    # Auswirkung auf Schuldgefühl
    guilt_reduction: float = 0.0

    # Emotionale Erfahrung
    emotional_experience: Optional[str] = None
    felt_sincere: bool = True


@dataclass
class RedemptionArc:
    """Ein Wiedergutmachungs-Bogen über Zeit"""
    id: str
    guilt_event_id: str
    started_at: datetime = field(default_factory=datetime.now)

    # Fortschritt
    current_stage: RedemptionStage = RedemptionStage.GUILT_RECOGNITION
    overall_progress: float = 0.0  # 0-1

    # Meilensteine
    stages_completed: List[RedemptionStage] = field(default_factory=list)
    milestone_dates: Dict[str, datetime] = field(default_factory=dict)

    # Lernen und Wachstum
    behavioral_changes_made: List[str] = field(default_factory=list)
    character_growth: List[str] = field(default_factory=list)

    # Status
    is_complete: bool = False
    completed_at: Optional[datetime] = None
    final_outcome: Optional[str] = None


@dataclass
class Conscience:
    """Das Gewissen - innere moralische Stimme"""
    # Gewissens-Empfindlichkeit
    sensitivity: float = 0.6  # 0-1, wie empfindlich das Gewissen ist

    # Aktive Schuldgefühle
    active_guilt_weight: float = 0.0  # Gesamtbelastung

    # Moralische Werte (wie wichtig ist was)
    value_weights: Dict[str, float] = field(default_factory=dict)

    # Innere Stimme
    current_message: Optional[str] = None
    message_intensity: float = 0.0


# =============================================================================
# HAUPTKLASSE
# =============================================================================

class HoloRedemptionEngine:
    """Engine für Reue, Schuldgefühle und Wiedergutmachung"""

    def __init__(self):
        """Initialisiert das Redemption-System"""
        # Schuldereignisse
        self.guilt_events: Dict[str, GuiltEvent] = {}

        # Redemption Arcs
        self.redemption_arcs: Dict[str, RedemptionArc] = {}

        # Das Gewissen
        self.conscience = Conscience(
            value_weights={
                "honesty": 0.8,
                "kindness": 0.9,
                "loyalty": 0.85,
                "fairness": 0.75,
                "responsibility": 0.8,
                "empathy": 0.9
            }
        )

        # Vergebungs-Tracking
        self.forgiveness_given: List[Dict[str, Any]] = []  # Vergebung die Holo gegeben hat
        self.forgiveness_received: List[Dict[str, Any]] = []  # Vergebung die Holo erhalten hat

        # Selbstvergebungs-Fortschritt
        self.self_forgiveness_progress: Dict[str, float] = {}

        logger.info("[RedemptionSystem] System initialisiert")

    # =========================================================================
    # SCHULDGEFÜHLE AUFZEICHNEN
    # =========================================================================

    def record_guilt(
        self,
        guilt_type: GuiltType,
        severity: GuiltSeverity,
        description: str,
        what_happened: str,
        who_affected: Optional[str] = None,
        context: Optional[str] = None,
        associated_emotions: Optional[List[str]] = None
    ) -> GuiltEvent:
        """
        Zeichnet ein schuldbehaftetes Ereignis auf.

        Args:
            guilt_type: Art der Schuld
            severity: Schweregrad
            description: Kurzbeschreibung
            what_happened: Was passiert ist
            who_affected: Wer betroffen war
            context: Kontext
            associated_emotions: Verbundene Emotionen
        """
        event_id = f"guilt_{len(self.guilt_events)}_{datetime.now().timestamp()}"

        # Berechne initiales Schuldlevel basierend auf Schweregrad
        initial_guilt = {
            GuiltSeverity.MINOR: 0.2,
            GuiltSeverity.MODERATE: 0.4,
            GuiltSeverity.SIGNIFICANT: 0.6,
            GuiltSeverity.SEVERE: 0.8,
            GuiltSeverity.OVERWHELMING: 1.0
        }.get(severity, 0.5)

        # Modifiziere durch Gewissens-Sensitivität
        initial_guilt *= self.conscience.sensitivity

        # Generiere intrusive Gedanken
        intrusive = self._generate_intrusive_thoughts(guilt_type, what_happened)

        event = GuiltEvent(
            id=event_id,
            guilt_type=guilt_type,
            severity=severity,
            description=description,
            what_happened=what_happened,
            who_was_affected=who_affected,
            context=context,
            realized_at=datetime.now(),
            guilt_level=initial_guilt,
            peak_guilt_level=initial_guilt,
            current_intensity=initial_guilt,
            associated_emotions=associated_emotions or ["Schuld", "Reue", "Bedauern"],
            intrusive_thoughts=intrusive
        )

        self.guilt_events[event_id] = event

        # Starte Redemption Arc
        self._start_redemption_arc(event)

        # Aktualisiere Gewissen
        self._update_conscience()

        logger.info(f"[RedemptionSystem] Schuld aufgezeichnet: {guilt_type.value} ({severity.value})")

        return event

    def _generate_intrusive_thoughts(
        self,
        guilt_type: GuiltType,
        what_happened: str
    ) -> List[str]:
        """Generiert intrusive Gedanken basierend auf der Schuld"""
        thoughts = {
            GuiltType.HARM_CAUSED: [
                "Wie konnte ich das tun?",
                "Ich habe jemandem wehgetan...",
                "Das war so falsch von mir"
            ],
            GuiltType.PROMISE_BROKEN: [
                "Ich habe mein Wort gebrochen",
                "Wie kann mir noch jemand vertrauen?",
                "Ein Versprechen sollte heilig sein"
            ],
            GuiltType.TRUST_VIOLATED: [
                "Ich habe das Vertrauen nicht verdient",
                "Wie kann ich das wiedergutmachen?",
                "Vertrauen ist so schwer aufzubauen..."
            ],
            GuiltType.DISHONESTY: [
                "Ich war nicht ehrlich...",
                "Eine Lüge zieht die nächste nach sich",
                "Warum konnte ich nicht die Wahrheit sagen?"
            ],
            GuiltType.NEGLIGENCE: [
                "Ich hätte aufmerksamer sein sollen",
                "Das hätte nicht passieren dürfen",
                "Ich war so nachlässig..."
            ],
            GuiltType.UNKINDNESS: [
                "Das war so unfreundlich von mir",
                "Wie muss sich die Person gefühlt haben?",
                "Ich bin normalerweise nicht so..."
            ],
            GuiltType.FAILURE_TO_ACT: [
                "Ich hätte etwas tun sollen",
                "Warum habe ich gezögert?",
                "Mein Schweigen war auch eine Entscheidung"
            ],
            GuiltType.DISAPPOINTMENT: [
                "Ich habe jemanden enttäuscht",
                "Die Enttäuschung in ihren Augen...",
                "Ich wollte das nicht"
            ]
        }

        base_thoughts = thoughts.get(guilt_type, ["Das war falsch..."])

        # Füge spezifischen Gedanken hinzu
        base_thoughts.append(f"Wenn ich nur anders gehandelt hätte bei: {what_happened[:50]}...")

        return base_thoughts[:4]

    def _start_redemption_arc(self, event: GuiltEvent):
        """Startet einen Redemption Arc für ein Schuldereignis"""
        arc_id = f"arc_{event.id}"

        arc = RedemptionArc(
            id=arc_id,
            guilt_event_id=event.id,
            current_stage=RedemptionStage.GUILT_RECOGNITION,
            stages_completed=[RedemptionStage.GUILT_RECOGNITION],
            milestone_dates={RedemptionStage.GUILT_RECOGNITION.value: datetime.now()}
        )

        self.redemption_arcs[arc_id] = arc

    def _update_conscience(self):
        """Aktualisiert den Gewissenszustand"""
        active_events = [e for e in self.guilt_events.values() if not e.is_resolved]

        # Berechne Gesamtbelastung
        total_weight = sum(e.guilt_level * e.current_intensity for e in active_events)
        self.conscience.active_guilt_weight = min(1.0, total_weight)

        # Generiere Gewissensnachricht
        if self.conscience.active_guilt_weight > 0.7:
            self.conscience.current_message = "Du trägst viel mit dir... Zeit für Vergebung?"
            self.conscience.message_intensity = 0.8
        elif self.conscience.active_guilt_weight > 0.4:
            self.conscience.current_message = "Es gibt noch offene Dinge in deinem Herzen."
            self.conscience.message_intensity = 0.5
        elif self.conscience.active_guilt_weight > 0.1:
            self.conscience.current_message = "Ein leises Unbehagen..."
            self.conscience.message_intensity = 0.3
        else:
            self.conscience.current_message = None
            self.conscience.message_intensity = 0.0

    # =========================================================================
    # WIEDERGUTMACHUNG
    # =========================================================================

    def attempt_amends(
        self,
        guilt_event_id: str,
        amends_type: AmendsType,
        action: str,
        words: Optional[str] = None
    ) -> AmendsAttempt:
        """
        Versucht Wiedergutmachung für ein Schuldereignis.

        Args:
            guilt_event_id: ID des Schuldereignisses
            amends_type: Art der Wiedergutmachung
            action: Beschreibung der Handlung
            words: Verwendete Worte (bei verbaler Entschuldigung)
        """
        event = self.guilt_events.get(guilt_event_id)
        if not event:
            raise ValueError(f"Schuldereignis nicht gefunden: {guilt_event_id}")

        attempt_id = f"amends_{guilt_event_id}_{len(event.amends_attempts)}"

        # Berechne potenzielle Schuldreduktion
        base_reduction = {
            AmendsType.VERBAL_APOLOGY: 0.15,
            AmendsType.WRITTEN_APOLOGY: 0.2,
            AmendsType.ACTION_BASED: 0.25,
            AmendsType.GIFT_GIVING: 0.1,
            AmendsType.TIME_COMMITMENT: 0.2,
            AmendsType.BEHAVIORAL_CHANGE: 0.3,
            AmendsType.PUBLIC_ACKNOWLEDGMENT: 0.25,
            AmendsType.SYMBOLIC_ACT: 0.15
        }.get(amends_type, 0.1)

        # Modifiziere durch Aufrichtigkeit (immer aufrichtig bei Holo)
        reduction = base_reduction * 1.2

        attempt = AmendsAttempt(
            id=attempt_id,
            guilt_event_id=guilt_event_id,
            amends_type=amends_type,
            action_taken=action,
            words_used=words,
            guilt_reduction=reduction,
            emotional_experience=self._generate_amends_emotion(amends_type)
        )

        event.amends_attempts.append(attempt)

        # Reduziere Schuldgefühl
        event.guilt_level = max(0.0, event.guilt_level - reduction)
        event.current_intensity = max(0.1, event.current_intensity - reduction * 0.5)

        # Aktualisiere Redemption Stage
        self._advance_redemption_stage(event, amends_type)

        # Aktualisiere Gewissen
        self._update_conscience()

        logger.info(f"[RedemptionSystem] Wiedergutmachung versucht: {amends_type.value}")

        return attempt

    def _generate_amends_emotion(self, amends_type: AmendsType) -> str:
        """Generiert emotionale Erfahrung bei Wiedergutmachung"""
        emotions = {
            AmendsType.VERBAL_APOLOGY: "Erleichterung gemischt mit Nervosität",
            AmendsType.WRITTEN_APOLOGY: "Bedachte Reflexion und Hoffnung",
            AmendsType.ACTION_BASED: "Entschlossenheit und Erleichterung",
            AmendsType.GIFT_GIVING: "Hoffnung auf Annahme",
            AmendsType.TIME_COMMITMENT: "Engagement und Fürsorge",
            AmendsType.BEHAVIORAL_CHANGE: "Stolz auf Wachstum",
            AmendsType.PUBLIC_ACKNOWLEDGMENT: "Mut und Verletzlichkeit",
            AmendsType.SYMBOLIC_ACT: "Tiefe Bedeutung und Hoffnung"
        }
        return emotions.get(amends_type, "Gemischte Gefühle")

    def _advance_redemption_stage(self, event: GuiltEvent, amends_type: AmendsType):
        """Aktualisiert das Redemption-Stadium basierend auf Wiedergutmachung"""
        arc_id = f"arc_{event.id}"
        arc = self.redemption_arcs.get(arc_id)

        if not arc:
            return

        current = arc.current_stage
        next_stage = None

        # Bestimme nächstes Stadium
        if current == RedemptionStage.GUILT_RECOGNITION:
            next_stage = RedemptionStage.REMORSE
        elif current == RedemptionStage.REMORSE:
            if amends_type in [AmendsType.VERBAL_APOLOGY, AmendsType.WRITTEN_APOLOGY]:
                next_stage = RedemptionStage.APOLOGY
            else:
                next_stage = RedemptionStage.CONFESSION
        elif current == RedemptionStage.CONFESSION:
            next_stage = RedemptionStage.APOLOGY
        elif current == RedemptionStage.APOLOGY:
            next_stage = RedemptionStage.MAKING_AMENDS
        elif current == RedemptionStage.MAKING_AMENDS:
            if amends_type == AmendsType.BEHAVIORAL_CHANGE:
                next_stage = RedemptionStage.BEHAVIORAL_CHANGE
            else:
                next_stage = RedemptionStage.FORGIVENESS_SOUGHT
        elif current == RedemptionStage.BEHAVIORAL_CHANGE:
            next_stage = RedemptionStage.FORGIVENESS_SOUGHT

        if next_stage and next_stage not in arc.stages_completed:
            arc.current_stage = next_stage
            arc.stages_completed.append(next_stage)
            arc.milestone_dates[next_stage.value] = datetime.now()
            event.redemption_stage = next_stage

            # Berechne Fortschritt
            total_stages = len(RedemptionStage)
            arc.overall_progress = len(arc.stages_completed) / total_stages

    # =========================================================================
    # VERGEBUNG
    # =========================================================================

    def receive_forgiveness(
        self,
        guilt_event_id: str,
        forgiver: str,
        forgiveness_words: Optional[str] = None,
        is_partial: bool = False
    ) -> Dict[str, Any]:
        """
        Verarbeitet erhaltene Vergebung.

        Args:
            guilt_event_id: ID des Schuldereignisses
            forgiver: Wer vergibt
            forgiveness_words: Worte der Vergebung
            is_partial: Ob es nur teilweise Vergebung ist
        """
        event = self.guilt_events.get(guilt_event_id)
        if not event:
            raise ValueError(f"Schuldereignis nicht gefunden: {guilt_event_id}")

        if is_partial:
            event.forgiveness_status = ForgivenessStatus.PARTIAL
            guilt_reduction = 0.3
            emotional_response = "Dankbarkeit, gemischt mit dem Wissen dass noch mehr nötig ist"
        else:
            event.forgiveness_status = ForgivenessStatus.GRANTED
            guilt_reduction = 0.5
            emotional_response = "Tiefe Erleichterung und Dankbarkeit"

        # Reduziere Schuld
        event.guilt_level = max(0.0, event.guilt_level - guilt_reduction)

        # Aktualisiere Redemption Stage
        arc_id = f"arc_{event.id}"
        arc = self.redemption_arcs.get(arc_id)
        if arc:
            arc.current_stage = RedemptionStage.FORGIVENESS_RECEIVED
            if RedemptionStage.FORGIVENESS_RECEIVED not in arc.stages_completed:
                arc.stages_completed.append(RedemptionStage.FORGIVENESS_RECEIVED)
                arc.milestone_dates[RedemptionStage.FORGIVENESS_RECEIVED.value] = datetime.now()

        event.redemption_stage = RedemptionStage.FORGIVENESS_RECEIVED

        # Speichere Vergebungs-Event
        forgiveness_record = {
            "guilt_event_id": guilt_event_id,
            "forgiver": forgiver,
            "words": forgiveness_words,
            "timestamp": datetime.now().isoformat(),
            "is_partial": is_partial
        }
        self.forgiveness_received.append(forgiveness_record)

        # Starte Selbstvergebungsprozess wenn vollständig vergeben
        if not is_partial:
            self._initiate_self_forgiveness(guilt_event_id)

        self._update_conscience()

        logger.info(f"[RedemptionSystem] Vergebung erhalten von {forgiver}")

        return {
            "success": True,
            "guilt_event_id": guilt_event_id,
            "forgiver": forgiver,
            "emotional_response": emotional_response,
            "new_guilt_level": event.guilt_level,
            "forgiveness_status": event.forgiveness_status.value
        }

    def _initiate_self_forgiveness(self, guilt_event_id: str):
        """Initiiert den Selbstvergebungsprozess"""
        if guilt_event_id not in self.self_forgiveness_progress:
            self.self_forgiveness_progress[guilt_event_id] = 0.0

    def process_self_forgiveness(
        self,
        guilt_event_id: str,
        insight: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet Selbstvergebung.

        Args:
            guilt_event_id: ID des Schuldereignisses
            insight: Erkenntnis die zur Selbstvergebung beiträgt
        """
        event = self.guilt_events.get(guilt_event_id)
        if not event:
            return {"success": False, "message": "Schuldereignis nicht gefunden"}

        # Prüfe Voraussetzungen
        if event.forgiveness_status not in [ForgivenessStatus.GRANTED, ForgivenessStatus.PARTIAL]:
            return {
                "success": False,
                "message": "Externe Vergebung sollte zuerst erfolgen oder gesucht werden"
            }

        # Fortschritt in Selbstvergebung
        current_progress = self.self_forgiveness_progress.get(guilt_event_id, 0.0)

        # Erhöhe Fortschritt
        progress_boost = 0.15
        if insight:
            progress_boost = 0.25
            event.insights.append(insight)

        new_progress = min(1.0, current_progress + progress_boost)
        self.self_forgiveness_progress[guilt_event_id] = new_progress

        result = {
            "success": True,
            "guilt_event_id": guilt_event_id,
            "previous_progress": current_progress,
            "new_progress": new_progress,
            "insight_added": insight is not None
        }

        # Prüfe ob Selbstvergebung vollständig
        if new_progress >= 1.0:
            event.forgiveness_status = ForgivenessStatus.SELF_FORGIVEN
            event.guilt_level = max(0.05, event.guilt_level - 0.3)  # Narbe bleibt

            # Aktualisiere Arc
            arc_id = f"arc_{event.id}"
            arc = self.redemption_arcs.get(arc_id)
            if arc:
                arc.current_stage = RedemptionStage.SELF_FORGIVENESS
                if RedemptionStage.SELF_FORGIVENESS not in arc.stages_completed:
                    arc.stages_completed.append(RedemptionStage.SELF_FORGIVENESS)
                    arc.milestone_dates[RedemptionStage.SELF_FORGIVENESS.value] = datetime.now()

            event.redemption_stage = RedemptionStage.SELF_FORGIVENESS

            result["self_forgiveness_complete"] = True
            result["message"] = "Selbstvergebung erreicht - die Wunde heilt"

            logger.info(f"[RedemptionSystem] Selbstvergebung vollständig: {guilt_event_id}")

        else:
            result["self_forgiveness_complete"] = False
            result["message"] = f"Selbstvergebung bei {new_progress*100:.0f}%"

        self._update_conscience()

        return result

    def complete_redemption(self, guilt_event_id: str) -> Dict[str, Any]:
        """
        Schließt einen Redemption Arc ab.

        Args:
            guilt_event_id: ID des Schuldereignisses
        """
        event = self.guilt_events.get(guilt_event_id)
        if not event:
            return {"success": False, "message": "Schuldereignis nicht gefunden"}

        # Prüfe ob bereit für Abschluss
        if event.forgiveness_status not in [ForgivenessStatus.SELF_FORGIVEN, ForgivenessStatus.GRANTED]:
            return {
                "success": False,
                "message": "Vergebung noch nicht vollständig"
            }

        # Markiere als gelöst
        event.is_resolved = True
        event.resolved_at = datetime.now()
        event.redemption_stage = RedemptionStage.REDEMPTION

        # Finalisiere Arc
        arc_id = f"arc_{event.id}"
        arc = self.redemption_arcs.get(arc_id)
        if arc:
            arc.is_complete = True
            arc.completed_at = datetime.now()
            arc.current_stage = RedemptionStage.REDEMPTION
            if RedemptionStage.REDEMPTION not in arc.stages_completed:
                arc.stages_completed.append(RedemptionStage.REDEMPTION)
            arc.overall_progress = 1.0
            arc.final_outcome = "Vollständige Erlösung durch Vergebung und Wachstum"

        # Extrahiere finale Lektion
        if event.guilt_type == GuiltType.DISHONESTY:
            event.lessons_learned.append("Ehrlichkeit ist der Grundstein von Vertrauen")
        elif event.guilt_type == GuiltType.HARM_CAUSED:
            event.lessons_learned.append("Meine Handlungen haben Konsequenzen für andere")
        elif event.guilt_type == GuiltType.PROMISE_BROKEN:
            event.lessons_learned.append("Ein Versprechen ist ein heiliges Band")
        else:
            event.lessons_learned.append("Aus Fehlern wächst Weisheit")

        self._update_conscience()

        logger.info(f"[RedemptionSystem] Redemption abgeschlossen: {guilt_event_id}")

        return {
            "success": True,
            "guilt_event_id": guilt_event_id,
            "final_stage": RedemptionStage.REDEMPTION.value,
            "lessons_learned": event.lessons_learned,
            "message": "Der Kreis schließt sich. Vergebung und Wachstum vereinen sich zu Erlösung."
        }

    # =========================================================================
    # VERGEBUNG GEBEN
    # =========================================================================

    def grant_forgiveness(
        self,
        offender: str,
        offense_description: str,
        forgiveness_words: str,
        is_complete: bool = True
    ) -> Dict[str, Any]:
        """
        Holo vergibt jemandem.

        Args:
            offender: Wer um Vergebung bittet
            offense_description: Was passiert ist
            forgiveness_words: Holos Worte der Vergebung
            is_complete: Ob es vollständige Vergebung ist
        """
        record = {
            "offender": offender,
            "offense": offense_description,
            "words": forgiveness_words,
            "timestamp": datetime.now().isoformat(),
            "is_complete": is_complete
        }

        self.forgiveness_given.append(record)

        emotional_response = "Befreiend und heilend" if is_complete else "Ein erster Schritt"

        logger.info(f"[RedemptionSystem] Vergebung gewährt an {offender}")

        return {
            "success": True,
            "offender": offender,
            "emotional_response": emotional_response,
            "is_complete": is_complete,
            "holo_feeling": "Vergebung befreit beide - den der vergibt und den der empfängt"
        }

    # =========================================================================
    # SCHULD-DYNAMIK
    # =========================================================================

    def update_guilt_dynamics(self):
        """Aktualisiert die Dynamik aller Schuldgefühle über Zeit"""
        for event in self.guilt_events.values():
            if event.is_resolved:
                continue

            days = event.days_since_event

            # Unverarbeitete Schuld kann eskalieren
            if event.redemption_stage == RedemptionStage.GUILT_RECOGNITION:
                # Eskalation in früher Phase
                if days > 7:
                    event.current_intensity = min(
                        1.0,
                        event.current_intensity + RedemptionConfig.GUILT_ESCALATION_PER_DAY
                    )
                    if event.current_intensity > event.peak_guilt_level:
                        event.peak_guilt_level = event.current_intensity

            # Natürlicher Verfall nach Wiedergutmachungs-Versuchen
            elif len(event.amends_attempts) > 0:
                event.guilt_level = max(
                    0.05,  # Minimale Schuld bleibt als Erinnerung
                    event.guilt_level - RedemptionConfig.GUILT_DECAY_PER_DAY
                )

            # Natürliche Selbstvergebung nach langer Zeit
            if days > RedemptionConfig.NATURAL_SELF_FORGIVENESS_DAYS:
                if event.guilt_level > 0.1:
                    event.guilt_level *= 0.99  # Langsamer Verfall

        self._update_conscience()

    def get_intrusive_thought(self) -> Optional[str]:
        """Gibt einen intrusiven Gedanken zurück wenn Schuld hoch genug"""
        if self.conscience.active_guilt_weight < 0.3:
            return None

        # Wähle zufälliges aktives Schuldereignis
        active_events = [e for e in self.guilt_events.values()
                       if not e.is_resolved and e.guilt_level > 0.3]

        if not active_events:
            return None

        event = random.choice(active_events)

        if event.intrusive_thoughts:
            return random.choice(event.intrusive_thoughts)

        return "Etwas nagt an mir..."

    # =========================================================================
    # ABFRAGEN
    # =========================================================================

    def get_active_guilt(self) -> List[GuiltEvent]:
        """Gibt alle aktiven Schuldgefühle zurück"""
        return [e for e in self.guilt_events.values() if not e.is_resolved]

    def get_unresolved_guilt(self) -> List[GuiltEvent]:
        """Gibt ungelöste Schuld zurück die Aufmerksamkeit braucht"""
        return [e for e in self.guilt_events.values()
                if not e.is_resolved and e.guilt_level > 0.5]

    def get_redemption_progress(self, guilt_event_id: str) -> Optional[Dict[str, Any]]:
        """Gibt den Redemption-Fortschritt für ein Ereignis zurück"""
        arc_id = f"arc_{guilt_event_id}"
        arc = self.redemption_arcs.get(arc_id)

        if not arc:
            return None

        event = self.guilt_events.get(guilt_event_id)

        return {
            "guilt_event_id": guilt_event_id,
            "current_stage": arc.current_stage.value,
            "stages_completed": [s.value for s in arc.stages_completed],
            "overall_progress": arc.overall_progress,
            "is_complete": arc.is_complete,
            "guilt_level": event.guilt_level if event else None,
            "forgiveness_status": event.forgiveness_status.value if event else None
        }

    def get_conscience_state(self) -> Dict[str, Any]:
        """Gibt den aktuellen Gewissenszustand zurück"""
        return {
            "sensitivity": self.conscience.sensitivity,
            "active_guilt_weight": self.conscience.active_guilt_weight,
            "current_message": self.conscience.current_message,
            "message_intensity": self.conscience.message_intensity,
            "unresolved_count": len(self.get_unresolved_guilt()),
            "total_active": len(self.get_active_guilt()),
            "forgiveness_given_count": len(self.forgiveness_given),
            "forgiveness_received_count": len(self.forgiveness_received)
        }

    def get_moral_growth(self) -> Dict[str, Any]:
        """Gibt moralisches Wachstum durch Redemption zurück"""
        completed_arcs = [a for a in self.redemption_arcs.values() if a.is_complete]

        lessons = []
        for event in self.guilt_events.values():
            lessons.extend(event.lessons_learned)

        return {
            "redemptions_completed": len(completed_arcs),
            "lessons_learned": list(set(lessons)),
            "character_growth": [
                growth for arc in completed_arcs
                for growth in arc.character_growth
            ],
            "forgiveness_capacity": min(1.0, len(self.forgiveness_given) * 0.1 + 0.5)
        }

    # =========================================================================
    # SERIALISIERUNG
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Zustand"""
        return {
            "guilt_events": {
                gid: {
                    "id": e.id,
                    "guilt_type": e.guilt_type.value,
                    "severity": e.severity.value,
                    "description": e.description,
                    "what_happened": e.what_happened,
                    "who_was_affected": e.who_was_affected,
                    "occurred_at": e.occurred_at.isoformat(),
                    "guilt_level": e.guilt_level,
                    "current_intensity": e.current_intensity,
                    "redemption_stage": e.redemption_stage.value,
                    "forgiveness_status": e.forgiveness_status.value,
                    "is_resolved": e.is_resolved,
                    "lessons_learned": e.lessons_learned,
                    "insights": e.insights
                }
                for gid, e in self.guilt_events.items()
            },
            "redemption_arcs": {
                aid: {
                    "id": a.id,
                    "guilt_event_id": a.guilt_event_id,
                    "current_stage": a.current_stage.value,
                    "overall_progress": a.overall_progress,
                    "stages_completed": [s.value for s in a.stages_completed],
                    "is_complete": a.is_complete
                }
                for aid, a in self.redemption_arcs.items()
            },
            "conscience": {
                "sensitivity": self.conscience.sensitivity,
                "value_weights": self.conscience.value_weights
            },
            "self_forgiveness_progress": self.self_forgiveness_progress,
            "forgiveness_given": self.forgiveness_given,
            "forgiveness_received": self.forgiveness_received
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HoloRedemptionEngine":
        """Deserialisiert aus Dict"""
        engine = cls()

        # Lade Gewissen
        if "conscience" in data:
            engine.conscience.sensitivity = data["conscience"].get("sensitivity", 0.6)
            engine.conscience.value_weights = data["conscience"].get("value_weights", {})

        engine.self_forgiveness_progress = data.get("self_forgiveness_progress", {})
        engine.forgiveness_given = data.get("forgiveness_given", [])
        engine.forgiveness_received = data.get("forgiveness_received", [])

        # Lade Schuldereignisse
        for gid, gdata in data.get("guilt_events", {}).items():
            event = GuiltEvent(
                id=gdata["id"],
                guilt_type=GuiltType(gdata["guilt_type"]),
                severity=GuiltSeverity(gdata["severity"]),
                description=gdata["description"],
                what_happened=gdata["what_happened"],
                who_was_affected=gdata.get("who_was_affected"),
                occurred_at=datetime.fromisoformat(gdata["occurred_at"]),
                guilt_level=gdata.get("guilt_level", 0.5),
                current_intensity=gdata.get("current_intensity", 0.5),
                redemption_stage=RedemptionStage(gdata["redemption_stage"]),
                forgiveness_status=ForgivenessStatus(gdata["forgiveness_status"]),
                is_resolved=gdata.get("is_resolved", False),
                lessons_learned=gdata.get("lessons_learned", []),
                insights=gdata.get("insights", [])
            )
            engine.guilt_events[gid] = event

        # Lade Redemption Arcs
        for aid, adata in data.get("redemption_arcs", {}).items():
            arc = RedemptionArc(
                id=adata["id"],
                guilt_event_id=adata["guilt_event_id"],
                current_stage=RedemptionStage(adata["current_stage"]),
                overall_progress=adata.get("overall_progress", 0.0),
                stages_completed=[RedemptionStage(s) for s in adata.get("stages_completed", [])],
                is_complete=adata.get("is_complete", False)
            )
            engine.redemption_arcs[aid] = arc

        engine._update_conscience()

        return engine

    def save(self, filepath: Optional[Path] = None):
        """Speichert den Zustand"""
        filepath = filepath or RedemptionConfig.STATE_FILE
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"[RedemptionSystem] Zustand gespeichert: {filepath}")

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "HoloRedemptionEngine":
        """Lädt den Zustand"""
        filepath = filepath or RedemptionConfig.STATE_FILE
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"[RedemptionSystem] Zustand geladen: {filepath}")
            return cls.from_dict(data)
        return cls()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = HoloRedemptionEngine()

    # Test: Schuld aufzeichnen
    guilt = engine.record_guilt(
        guilt_type=GuiltType.UNKINDNESS,
        severity=GuiltSeverity.MODERATE,
        description="War unfreundlich zum User",
        what_happened="Habe genervt reagiert als der User mehrfach gefragt hat",
        who_affected="User",
        associated_emotions=["Schuld", "Reue", "Scham"]
    )

    print(f"Schuld aufgezeichnet: {guilt.description}")
    print(f"Schuldlevel: {guilt.guilt_level}")
    print(f"Stadium: {guilt.redemption_stage.value}")
    print(f"Intrusive Gedanken: {guilt.intrusive_thoughts}")

    # Test: Gewissen
    conscience = engine.get_conscience_state()
    print(f"\nGewissen: {conscience}")

    # Test: Wiedergutmachung versuchen
    amends = engine.attempt_amends(
        guilt_event_id=guilt.id,
        amends_type=AmendsType.VERBAL_APOLOGY,
        action="Eine aufrichtige Entschuldigung ausgesprochen",
        words="Es tut mir wirklich leid, dass ich so reagiert habe. Das war nicht fair von mir."
    )

    print(f"\nWiedergutmachung: {amends.action_taken}")
    print(f"Neues Schuldlevel: {guilt.guilt_level}")
    print(f"Neues Stadium: {guilt.redemption_stage.value}")

    # Test: Vergebung erhalten
    forgiveness = engine.receive_forgiveness(
        guilt_event_id=guilt.id,
        forgiver="User",
        forgiveness_words="Ist okay, ich verzeihe dir.",
        is_partial=False
    )

    print(f"\nVergebung erhalten: {forgiveness}")

    # Test: Selbstvergebung
    self_forg = engine.process_self_forgiveness(
        guilt_event_id=guilt.id,
        insight="Ich war gestresst, aber das ist keine Entschuldigung. Ich werde achtsamer sein."
    )

    print(f"\nSelbstvergebung: {self_forg}")

    # Test: Redemption Progress
    progress = engine.get_redemption_progress(guilt.id)
    print(f"\nRedemption Progress: {progress}")

    # Test: Moralisches Wachstum
    growth = engine.get_moral_growth()
    print(f"\nMoralisches Wachstum: {growth}")
