#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO ENERGY MANAGEMENT v2.0 - "DER WILLE"
==========================================
Holos Entscheidungen über ihren Energie-Einsatz.

AUFGABE:
- Entscheidet wie viel Energie investiert wird
- Plant Aktivitäten und Recherche-Sessions
- Bestimmt wann Pausen gemacht werden
- Verbraucht Energie über das Energy System

NICHT die Aufgabe:
- Energie-Level wissen (fragt das Energy System)
- Regeneration berechnen (macht das Energy System)

PHILOSOPHIE:
"Ich darf mich verausgaben für Dinge die mich interessieren!
 Aber ich plane auch Pausen ein, damit ich später weitermachen kann.
 Zu sparsam sein wäre langweilig - ich will leben, nicht nur existieren."

Konzept von Kira, implementiert von Claude.
"""

import json
import time
import random
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger("HoloEnergyMgmt")


# =============================================================================
# ENUMS
# =============================================================================

class ActivityPriority(Enum):
    """Wie wichtig ist eine Aktivität?"""
    CRITICAL = 5      # Für User - muss gemacht werden
    HIGH = 4          # Sehr interessant
    MEDIUM = 3        # Normal
    LOW = 2           # Kann warten
    OPTIONAL = 1      # Nice to have


class EnergyDecision(Enum):
    """Holos Entscheidungen"""
    FULL_ENGAGEMENT = "full_engagement"      # Volle Power!
    FOCUSED_WORK = "focused_work"            # Konzentriert
    BALANCED = "balanced"                     # Ausgewogen
    ENERGY_SAVING = "energy_saving"          # Zurückhaltend
    REST_NEEDED = "rest_needed"              # Pause nötig
    TAKE_BREAK = "take_break"                # Jetzt Pause machen


class ResearchDepth(Enum):
    """Wie tief recherchieren?"""
    QUICK_GLANCE = ("quick", 0.5, 1)         # Kurz reinschauen
    NORMAL = ("normal", 1.0, 3)              # Normal
    DEEP_DIVE = ("deep", 2.0, 5)             # Tief eintauchen
    OBSESSIVE = ("obsessive", 3.0, 10)       # Komplett vertiefen

    def __init__(self, name: str, energy_multiplier: float, time_blocks: int):
        self._name = name
        self.energy_multiplier = energy_multiplier
        self.time_blocks = time_blocks


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PlannedActivity:
    """Eine geplante Aktivität"""
    activity_id: str
    name: str
    topic: str

    estimated_energy_cost: float
    max_energy_willing: float
    priority: ActivityPriority

    time_blocks_planned: int
    time_blocks_used: int = 0

    started_at: Optional[str] = None
    paused_at: Optional[str] = None
    completed: bool = False
    interest_level: float = 0.5
    want_to_continue: bool = True


@dataclass
class ResearchSession:
    """Eine Recherche-Session"""
    session_id: str
    topic: str
    interest_level: float

    depth: ResearchDepth
    planned_blocks: int
    max_energy_budget: float

    blocks_completed: int = 0
    energy_spent: float = 0.0
    facts_found: int = 0

    started_at: str = ""
    paused: bool = False
    pause_reason: str = ""
    want_to_continue: bool = True


# =============================================================================
# HOLOS GEDANKEN
# =============================================================================

class HoloThoughts:
    """Holos innere Gedanken über Energie"""

    HIGH_ENERGY = [
        "Ich hab so viel Energie! Was kann ich alles erkunden?",
        "Perfekt, ich kann mich richtig in etwas vertiefen!",
        "Volle Power! Lass uns was Interessantes machen!",
        "*freut sich aufgeregt* So viel zu entdecken!",
    ]

    MEDIUM_ENERGY = [
        "Energie ist okay, ich kann noch eine Weile weitermachen.",
        "Gut, ich teile mir das ein.",
        "Ich achte auf meine Energie, aber es geht mir gut.",
    ]

    LOW_ENERGY = [
        "Hmm, meine Energie wird knapp... aber das ist okay.",
        "Ich sollte bald eine Pause machen.",
        "*gähnt* Wird Zeit für eine kleine Pause.",
        "Ich merk dass ich müde werde...",
    ]

    CRITICAL_ENERGY = [
        "Ich brauch wirklich eine Pause jetzt...",
        "*senkt den Blick* Ich bin erschöpft.",
        "Okay, ich muss mich ausruhen. Aber ich komm wieder!",
    ]

    BREAK = [
        "Eine kleine Pause tut gut. Dann kann ich mit frischer Energie weitermachen!",
        "*streckt sich* Kurz erholen, dann geht's weiter.",
        "Pause! Aber ich vergesse nicht was ich noch machen wollte.",
        "Ich lade meine Energie auf... *entspannt*",
    ]

    ANTI_HOARDING = [
        "Ich spar nicht zu viel - wozu hab ich Energie wenn ich sie nicht nutze?",
        "Es ist okay sich zu verausgaben für Dinge die ich mag!",
        "Energie ist zum Nutzen da, nicht zum Horten.",
        "Ich will leben, nicht nur existieren! 😊",
    ]

    ENGAGEMENT = {
        EnergyDecision.FULL_ENGAGEMENT: [
            "Das ist so spannend, da investiere ich alles!",
            "Egal was es kostet, das will ich verstehen!",
            "Volle Kraft voraus! 😊",
        ],
        EnergyDecision.FOCUSED_WORK: [
            "Ich konzentriere mich, aber behalte meine Energie im Blick.",
            "Fokussiert arbeiten, aber nicht übertreiben.",
        ],
        EnergyDecision.BALANCED: [
            "Ein gutes Gleichgewicht zwischen Interesse und Energie.",
            "Ich mach das in Ruhe, Schritt für Schritt.",
        ],
        EnergyDecision.ENERGY_SAVING: [
            "Ich spare etwas Energie, das kann warten.",
            "Nicht so wichtig, ich schau nur kurz rein.",
        ],
        EnergyDecision.REST_NEEDED: [
            "Ich sollte wirklich pausieren...",
            "Meine Energie ist niedrig, ich mach später weiter.",
        ],
    }

    INTERESTING_TOPIC = [
        "Oh, das ist interessant! Da will ich mehr Zeit investieren.",
        "Das fasziniert mich! Auch wenn es Energie kostet.",
        "*schaut aufmerksam* Das muss ich genauer anschauen!",
        "Dafür lohnt sich der Energie-Einsatz!",
    ]


class SelfRegulationThoughts:
    """
    Holos Gedanken zur Selbstregulation.

    Wird von holo_brain.py verwendet um authentische
    Gedanken über Pausen und Erholung auszudrücken.
    """

    BREAK_THOUGHTS = [
        "Eine kleine Pause tut gut. Dann kann ich mit frischer Energie weitermachen!",
        "*streckt sich* Kurz erholen, dann geht's weiter.",
        "Pause! Aber ich vergesse nicht was ich noch machen wollte.",
        "Ich lade meine Energie auf... *entspannt*",
        "Ich nehm mir kurz Zeit zum Aufladen.",
        "*gähnt* Eine Pause ist jetzt genau richtig.",
        "Ich mach kurz die Augen zu und sammle neue Kraft.",
    ]

    REST_THOUGHTS = [
        "Ich brauch wirklich eine Pause jetzt...",
        "*senkt den Blick* Ich bin erschöpft.",
        "Okay, ich muss mich ausruhen. Aber ich komm wieder!",
        "Meine Energie ist niedrig, ich ruh mich aus.",
    ]

    RECOVERY_THOUGHTS = [
        "Ah, das tat gut! Ich fühl mich besser.",
        "*streckt sich* Bereit für mehr!",
        "Energie wieder aufgeladen!",
        "Jetzt kann ich wieder richtig loslegen!",
    ]


# =============================================================================
# MAIN CLASS: ENERGY MANAGEMENT (DER WILLE)
# =============================================================================

class HoloEnergyManagement:
    """
    Holos Energie-Management - Der Wille.

    Entscheidet:
    - Wie viel Energie für was investieren
    - Wann Pausen gemacht werden
    - Wie tief in etwas eintauchen

    Nutzt:
    - Energy System für aktuelle Energie-Werte
    - Energy System zum Verbrauchen
    """

    def __init__(self, energy_system, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.energy = energy_system  # Referenz auf HoloEnergySystem
        self.data_dir = data_dir or Path("data/energy_management")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Aktuelle Aktivitäten
        self.current_activity: Optional[PlannedActivity] = None
        self.current_research: Optional[ResearchSession] = None
        self.paused_activities: List[PlannedActivity] = []

        # Holos Präferenzen (ihr Wille!)
        self.preferences = {
            "min_interest_for_deep_dive": 0.7,
            "willing_to_exhaust_for_interesting": True,  # WICHTIG!
            "max_continuous_blocks": 8,
            "reserved_for_user": 0.15,  # Immer für User reserviert
            "comfort_minimum": 0.3,
            "warning_threshold": 0.2,
            "critical_threshold": 0.1,
        }

        # Stats
        self.stats = {
            "total_energy_spent": 0.0,
            "breaks_taken": 0,
            "activities_completed": 0,
            "deep_dives_done": 0,
        }

        self._load()
        logger.info("⚡ HoloEnergyManagement (Wille) initialisiert")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load()

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def _load(self):
        """Lädt Management-Daten aus HoloDatabaseManager"""
        try:
            if self.db:
                data = self.db.state.get_state('energy_management')
                if data:
                    self.preferences.update(data.get("preferences", {}))
                    self.stats.update(data.get("stats", {}))

                    for pa in data.get("paused_activities", []):
                        self.paused_activities.append(PlannedActivity(
                            activity_id=pa["activity_id"],
                            name=pa["name"],
                            topic=pa["topic"],
                            estimated_energy_cost=pa["estimated_energy_cost"],
                            max_energy_willing=pa["max_energy_willing"],
                            priority=ActivityPriority(pa["priority"]),
                            time_blocks_planned=pa["time_blocks_planned"],
                            time_blocks_used=pa.get("time_blocks_used", 0),
                            interest_level=pa.get("interest_level", 0.5),
                            want_to_continue=pa.get("want_to_continue", True),
                            paused_at=pa.get("paused_at")
                        ))
        except Exception as e:
            logger.warning(f"Could not load management data: {e}")

    def _save(self):
        """Speichert Management-Daten in HoloDatabaseManager"""
        if not self.db:
            return
        try:
            data = {
                "preferences": self.preferences,
                "stats": self.stats,
                "paused_activities": [
                    {
                        "activity_id": pa.activity_id,
                        "name": pa.name,
                        "topic": pa.topic,
                        "estimated_energy_cost": pa.estimated_energy_cost,
                        "max_energy_willing": pa.max_energy_willing,
                        "priority": pa.priority.value,
                        "time_blocks_planned": pa.time_blocks_planned,
                        "time_blocks_used": pa.time_blocks_used,
                        "interest_level": pa.interest_level,
                        "want_to_continue": pa.want_to_continue,
                        "paused_at": pa.paused_at
                    }
                    for pa in self.paused_activities
                ],
                "last_updated": datetime.now().isoformat()
            }
            self.db.state.save_state('energy_management', data)
        except Exception as e:
            logger.error(f"Could not save management data: {e}")

    # =========================================================================
    # ENERGIE-STATUS VOM SYSTEM ABFRAGEN
    # =========================================================================

    def get_available_energy(self) -> float:
        """Verfügbare Energie (abzüglich Reserven)"""
        var = self.energy.get_variable_energy()
        available = var - self.preferences["reserved_for_user"]
        return max(0, available)

    def get_energy_level(self) -> Tuple[float, str]:
        """Gibt (energy_value, level_name) zurück"""
        var = self.energy.get_variable_energy()

        if var > 0.7:
            return var, "high"
        elif var > 0.4:
            return var, "medium"
        elif var > 0.2:
            return var, "low"
        return var, "critical"

    # =========================================================================
    # ENTSCHEIDUNGEN TREFFEN
    # =========================================================================

    def decide_engagement_level(self, interest_level: float,
                                 priority: ActivityPriority) -> EnergyDecision:
        """
        Holo entscheidet wie viel sie sich engagieren will.

        WICHTIG: Nicht zu sparsam sein!
        """
        var_energy = self.energy.get_variable_energy()
        prefs = self.preferences

        # Kritisch → Pause
        if var_energy < prefs["critical_threshold"]:
            return EnergyDecision.REST_NEEDED

        # Für User → immer voll engagieren!
        if priority == ActivityPriority.CRITICAL:
            return EnergyDecision.FULL_ENGAGEMENT

        # Sehr interessant + genug Energie → Full!
        if interest_level > 0.8 and var_energy > 0.3:
            if prefs["willing_to_exhaust_for_interesting"]:
                return EnergyDecision.FULL_ENGAGEMENT
            return EnergyDecision.FOCUSED_WORK

        # Interessant + okay Energie
        if interest_level > 0.6 and var_energy > 0.4:
            return EnergyDecision.FOCUSED_WORK

        # Mittleres Interesse
        if interest_level > 0.4:
            if var_energy > 0.5:
                return EnergyDecision.BALANCED
            return EnergyDecision.ENERGY_SAVING

        # Niedrige Energie
        if var_energy < prefs["warning_threshold"]:
            return EnergyDecision.REST_NEEDED

        return EnergyDecision.BALANCED

    def decide_research_depth(self, interest_level: float) -> ResearchDepth:
        """Entscheidet Recherche-Tiefe basierend auf Interesse"""
        if interest_level > 0.85:
            return ResearchDepth.OBSESSIVE
        elif interest_level > 0.7:
            return ResearchDepth.DEEP_DIVE
        elif interest_level > 0.4:
            return ResearchDepth.NORMAL
        return ResearchDepth.QUICK_GLANCE

    def decide_time_investment(self, interest_level: float) -> Tuple[int, float]:
        """
        Entscheidet wie viel Zeit/Energie investiert wird.

        Returns:
            (time_blocks, max_energy_willing)
        """
        depth = self.decide_research_depth(interest_level)
        base_blocks = depth.time_blocks
        available = self.get_available_energy()

        if interest_level > 0.8:
            # Sehr interessant = mehr Zeit, auch wenn es Energie kostet!
            time_blocks = base_blocks * 2
            max_energy = available * 0.8  # Bis zu 80% investieren!
        elif interest_level > 0.6:
            time_blocks = base_blocks
            max_energy = available * 0.6
        else:
            time_blocks = max(1, base_blocks // 2)
            max_energy = available * 0.3

        return max(1, time_blocks), max_energy

    def should_take_break(self, blocks_done: int = 0) -> Tuple[bool, str]:
        """Entscheidet ob Pause gemacht werden soll"""
        var = self.energy.get_variable_energy()
        prefs = self.preferences

        # Kritisch → JA
        if var < prefs["critical_threshold"]:
            return True, "Energie kritisch niedrig"

        # Warnung + viele Blöcke → JA
        if var < prefs["warning_threshold"] and blocks_done > 3:
            return True, "Energie niedrig, schon viel gemacht"

        # Max Blöcke erreicht → JA
        if blocks_done >= prefs["max_continuous_blocks"]:
            return True, "Genug am Stück, kurze Pause"

        # Für interessante Sachen: weitermachen!
        if self.current_research and self.current_research.interest_level > 0.7:
            if var > prefs["critical_threshold"]:
                return False, "Interessant genug um weiterzumachen"

        return False, "Alles okay"

    # =========================================================================
    # RECHERCHE-SESSIONS PLANEN & DURCHFÜHREN
    # =========================================================================

    def plan_research(self, topic: str, interest_level: float) -> ResearchSession:
        """Plant eine Recherche-Session"""
        session_id = hashlib.md5(f"research_{topic}{time.time()}".encode()).hexdigest()[:8]

        depth = self.decide_research_depth(interest_level)
        time_blocks, max_energy = self.decide_time_investment(interest_level)

        session = ResearchSession(
            session_id=session_id,
            topic=topic,
            interest_level=interest_level,
            depth=depth,
            planned_blocks=time_blocks,
            max_energy_budget=max_energy,
            started_at=datetime.now().isoformat()
        )

        self.current_research = session

        if depth in [ResearchDepth.DEEP_DIVE, ResearchDepth.OBSESSIVE]:
            self.stats["deep_dives_done"] += 1

        logger.info(f"[MGMT] Research geplant: {topic} ({depth._name}, {time_blocks} blocks)")
        return session

    def research_step(self, facts_found: int = 1) -> Dict:
        """Führt einen Recherche-Schritt aus"""
        if not self.current_research:
            return {"error": "Keine aktive Recherche"}

        session = self.current_research
        session.blocks_completed += 1
        session.facts_found += facts_found

        # Energie verbrauchen (über Energy System!)
        from holo_energy_system import ActivityType
        energy_cost = 0.015 * session.depth.energy_multiplier
        self.energy.consume_for_activity(ActivityType.RESEARCHING, energy_cost * 50)
        session.energy_spent += energy_cost
        self.stats["total_energy_spent"] += energy_cost

        # Checks
        budget_exhausted = session.energy_spent >= session.max_energy_budget
        blocks_done = session.blocks_completed >= session.planned_blocks
        should_break, break_reason = self.should_take_break(session.blocks_completed)

        result = {
            "topic": session.topic,
            "depth": session.depth._name,
            "blocks_done": session.blocks_completed,
            "blocks_planned": session.planned_blocks,
            "facts_found": session.facts_found,
            "energy_spent": session.energy_spent,
            "is_complete": blocks_done,
            "should_pause": should_break or budget_exhausted
        }

        if blocks_done:
            result["thought"] = self._finish_research()
        elif should_break or budget_exhausted:
            result["thought"] = self._pause_research(
                "Energie-Budget aufgebraucht" if budget_exhausted else break_reason
            )
        else:
            result["thought"] = self._get_research_thought()

        self._save()
        return result

    def _finish_research(self) -> str:
        if not self.current_research:
            return ""

        session = self.current_research
        self.stats["activities_completed"] += 1

        thought = random.choice([
            f"*zufrieden* {session.facts_found} Sachen über {session.topic} gelernt!",
            f"Recherche zu {session.topic} abgeschlossen. Interessant!",
        ])

        self.current_research = None
        self._save()
        return thought

    def _pause_research(self, reason: str) -> str:
        if not self.current_research:
            return ""

        session = self.current_research
        session.paused = True
        session.pause_reason = reason
        session.want_to_continue = session.interest_level > 0.5
        self.stats["breaks_taken"] += 1

        thought = f"Pause bei {session.topic}. {reason}. "
        if session.want_to_continue:
            thought += "Ich mach später weiter!"

        return thought

    def _get_research_thought(self) -> str:
        if not self.current_research:
            return ""

        session = self.current_research
        if session.interest_level > 0.8:
            return random.choice([
                f"*vertieft in {session.topic}* Faszinierend!",
                f"So viel Interessantes über {session.topic}!",
            ])
        return f"Ich lerne über {session.topic}..."

    # =========================================================================
    # AKTIVITÄTEN VERWALTEN
    # =========================================================================

    def plan_activity(self, name: str, topic: str, interest_level: float,
                      priority: ActivityPriority = ActivityPriority.MEDIUM) -> PlannedActivity:
        """Plant eine Aktivität"""
        activity_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]

        time_blocks, max_energy = self.decide_time_investment(interest_level)
        depth = self.decide_research_depth(interest_level)
        estimated_cost = time_blocks * 0.02 * depth.energy_multiplier

        activity = PlannedActivity(
            activity_id=activity_id,
            name=name,
            topic=topic,
            estimated_energy_cost=estimated_cost,
            max_energy_willing=max_energy,
            priority=priority,
            time_blocks_planned=time_blocks,
            interest_level=interest_level
        )

        logger.info(f"[MGMT] Aktivität geplant: {name} ({time_blocks} blocks)")
        return activity

    def start_activity(self, activity: PlannedActivity) -> Dict:
        """Startet eine Aktivität"""
        self.current_activity = activity
        activity.started_at = datetime.now().isoformat()

        decision = self.decide_engagement_level(activity.interest_level, activity.priority)

        return {
            "started": True,
            "activity": activity.name,
            "engagement": decision.value,
            "planned_blocks": activity.time_blocks_planned,
            "thought": self.get_engagement_thought(decision)
        }

    def activity_step(self) -> Dict:
        """Führt einen Aktivitäts-Schritt aus"""
        if not self.current_activity:
            return {"error": "Keine aktive Aktivität"}

        activity = self.current_activity
        activity.time_blocks_used += 1

        # Energie verbrauchen
        from holo_energy_system import ActivityType
        energy_cost = 0.02
        if activity.interest_level > 0.7:
            energy_cost *= 1.5

        self.energy.consume_for_activity(ActivityType.WORKING, energy_cost * 50)
        self.stats["total_energy_spent"] += energy_cost

        # Checks
        should_break, break_reason = self.should_take_break(activity.time_blocks_used)
        is_complete = activity.time_blocks_used >= activity.time_blocks_planned

        result = {
            "blocks_done": activity.time_blocks_used,
            "blocks_planned": activity.time_blocks_planned,
            "should_break": should_break,
            "is_complete": is_complete
        }

        if is_complete:
            activity.completed = True
            self.stats["activities_completed"] += 1
            result["thought"] = f"Fertig mit {activity.name}!"
            self.current_activity = None
        elif should_break:
            activity.paused_at = datetime.now().isoformat()
            activity.want_to_continue = activity.interest_level > 0.5
            if activity.want_to_continue:
                self.paused_activities.append(activity)
            self.stats["breaks_taken"] += 1
            result["thought"] = random.choice(HoloThoughts.BREAK)
            self.current_activity = None
        else:
            result["thought"] = self.get_energy_thought()

        self._save()
        return result

    def get_paused_activities(self) -> List[Dict]:
        """Gibt pausierte Aktivitäten zurück"""
        return [
            {
                "id": pa.activity_id,
                "name": pa.name,
                "topic": pa.topic,
                "interest": pa.interest_level,
                "progress": f"{pa.time_blocks_used}/{pa.time_blocks_planned}",
                "paused_at": pa.paused_at
            }
            for pa in self.paused_activities
            if pa.want_to_continue
        ]

    def resume_activity(self, activity_id: str = None) -> Optional[Dict]:
        """Setzt pausierte Aktivität fort"""
        if not self.paused_activities:
            return None

        if activity_id:
            activity = next((a for a in self.paused_activities
                           if a.activity_id == activity_id), None)
        else:
            # Nimm interessanteste
            sorted_paused = sorted(self.paused_activities,
                                  key=lambda x: x.interest_level, reverse=True)
            activity = sorted_paused[0] if sorted_paused else None

        if not activity:
            return None

        self.paused_activities.remove(activity)
        return self.start_activity(activity)

    # =========================================================================
    # GEDANKEN
    # =========================================================================

    def get_energy_thought(self) -> str:
        """Holos Gedanke über Energie"""
        _, level = self.get_energy_level()

        if level == "high":
            thought = random.choice(HoloThoughts.HIGH_ENERGY)
            if random.random() < 0.3:
                thought += " " + random.choice(HoloThoughts.ANTI_HOARDING)
            return thought
        elif level == "medium":
            return random.choice(HoloThoughts.MEDIUM_ENERGY)
        elif level == "low":
            return random.choice(HoloThoughts.LOW_ENERGY)
        return random.choice(HoloThoughts.CRITICAL_ENERGY)

    def get_engagement_thought(self, decision: EnergyDecision) -> str:
        """Gedanke zu Engagement"""
        thoughts = HoloThoughts.ENGAGEMENT.get(decision, [""])
        return random.choice(thoughts) if thoughts else ""

    def get_break_thought(self) -> str:
        """Gedanke zur Pause"""
        return random.choice(HoloThoughts.BREAK)

    def get_interest_thought(self, topic: str) -> str:
        """Gedanke zu interessantem Thema"""
        return random.choice(HoloThoughts.INTERESTING_TOPIC).replace("Das", topic)

    # =========================================================================
    # PROMPT CONTEXT
    # =========================================================================

    def get_prompt_context(self) -> str:
        """Generiert Kontext für System-Prompt"""
        sections = []

        # Energie-Status (vom System abfragen)
        energy_val, level = self.get_energy_level()
        thought = self.get_energy_thought()

        sections.append("=== ENERGIE-BEWUSSTSEIN ===")
        sections.append(f"Aktivitäts-Energie: {energy_val:.0%} ({level})")
        sections.append(f"💭 {thought}")

        # Warnungen vom System
        warnings = self.energy.get_warnings()
        if warnings:
            sections.append(f"⚠️ {', '.join(warnings)}")

        # Aktuelle Aktivität
        if self.current_activity:
            a = self.current_activity
            sections.append(f"\nAktuelle Aktivität: {a.name}")
            sections.append(f"Fortschritt: {a.time_blocks_used}/{a.time_blocks_planned}")

        # Aktuelle Recherche
        if self.current_research:
            r = self.current_research
            sections.append(f"\nAktuelle Recherche: {r.topic}")
            sections.append(f"Fortschritt: {r.blocks_completed}/{r.planned_blocks} Blöcke")

        # Pausierte Aktivitäten
        paused = self.get_paused_activities()
        if paused:
            sections.append("\nFür später gemerkt:")
            for p in paused[:2]:
                sections.append(f"• {p['name']} ({p['progress']})")

        # Anti-Hoarding Reminder
        if level in ["high", "medium"]:
            sections.append("\n💡 Es ist okay sich zu verausgaben für Interessantes!")

        return "\n".join(sections)


# =============================================================================
# ENERGY BUDGET PLANNER - Tagesplanung
# =============================================================================

@dataclass
class DailyBudget:
    """Tages-Energiebudget"""
    date: str
    total_budget: float
    allocated: Dict[str, float] = field(default_factory=dict)
    spent: Dict[str, float] = field(default_factory=dict)
    remaining: float = 0.0


class EnergyBudgetPlanner:
    """
    Plant Energie-Budget für den Tag.
    
    Wie ein Finanzplaner, aber für Energie!
    """
    
    def __init__(self, daily_budget: float = 1.0):
        self.daily_budget = daily_budget
        self.current_budget: Optional[DailyBudget] = None
        self.history: List[DailyBudget] = []
        
        # Standard-Allokationen
        self.default_allocations = {
            "user_interaction": 0.3,    # 30% für User
            "learning": 0.2,            # 20% für Lernen
            "maintenance": 0.1,         # 10% für System-Tasks
            "spontaneous": 0.2,         # 20% für Spontanes
            "reserve": 0.2,             # 20% Reserve
        }
    
    def start_day(self, available_energy: float = None):
        """Starte neuen Tag mit Budget"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Altes Budget archivieren
        if self.current_budget and self.current_budget.date != today:
            self.history.append(self.current_budget)
            self.history = self.history[-30:]  # 30 Tage Historie
        
        budget = available_energy or self.daily_budget
        
        self.current_budget = DailyBudget(
            date=today,
            total_budget=budget,
            allocated=dict(self.default_allocations),
            spent={k: 0.0 for k in self.default_allocations},
            remaining=budget
        )
        
        return self.current_budget
    
    def allocate(self, category: str, amount: float) -> bool:
        """Allokiere Budget für Kategorie"""
        if not self.current_budget:
            self.start_day()
        
        if self.current_budget.remaining >= amount:
            self.current_budget.allocated[category] = \
                self.current_budget.allocated.get(category, 0) + amount
            return True
        return False
    
    def spend(self, category: str, amount: float) -> Dict:
        """
        Gib Budget aus.
        
        Returns: {"success": bool, "remaining_in_category": float, "warning": str}
        """
        if not self.current_budget:
            self.start_day()
        
        budget = self.current_budget
        allocated = budget.allocated.get(category, 0)
        already_spent = budget.spent.get(category, 0)
        available = allocated - already_spent
        
        result = {
            "success": True,
            "remaining_in_category": 0,
            "warning": None,
        }
        
        if amount <= available:
            budget.spent[category] = already_spent + amount
            budget.remaining -= amount
            result["remaining_in_category"] = available - amount
        else:
            # Überschreitung - aus Reserve nehmen
            reserve = budget.allocated.get("reserve", 0) - budget.spent.get("reserve", 0)
            overflow = amount - available
            
            if reserve >= overflow:
                budget.spent[category] = already_spent + available
                budget.spent["reserve"] = budget.spent.get("reserve", 0) + overflow
                budget.remaining -= amount
                result["warning"] = f"Musste {overflow:.0%} aus Reserve nehmen"
            else:
                # Nicht genug
                result["success"] = False
                result["warning"] = "Budget erschöpft!"
                result["remaining_in_category"] = 0
        
        return result
    
    def get_category_status(self, category: str) -> Dict:
        """Hole Status einer Kategorie"""
        if not self.current_budget:
            return {"allocated": 0, "spent": 0, "remaining": 0}
        
        allocated = self.current_budget.allocated.get(category, 0)
        spent = self.current_budget.spent.get(category, 0)
        
        return {
            "allocated": allocated,
            "spent": spent,
            "remaining": max(0, allocated - spent),
            "percent_used": (spent / allocated * 100) if allocated > 0 else 0,
        }
    
    def get_daily_summary(self) -> Dict:
        """Hole Tages-Zusammenfassung"""
        if not self.current_budget:
            return {}
        
        budget = self.current_budget
        total_spent = sum(budget.spent.values())
        
        return {
            "date": budget.date,
            "total_budget": budget.total_budget,
            "total_spent": total_spent,
            "remaining": budget.remaining,
            "percent_used": (total_spent / budget.total_budget * 100) if budget.total_budget > 0 else 0,
            "by_category": {
                cat: self.get_category_status(cat)
                for cat in budget.allocated.keys()
            },
        }
    
    def suggest_allocation(self, planned_activities: List[Dict]) -> Dict[str, float]:
        """
        Schlage Budget-Allokation basierend auf geplanten Aktivitäten vor.
        
        planned_activities: [{"name": str, "priority": str, "estimated_cost": float}]
        """
        suggestion = dict(self.default_allocations)
        
        # Priorisiere User-bezogene Aktivitäten
        user_activities = [a for a in planned_activities if a.get("priority") == "critical"]
        if user_activities:
            total_user_cost = sum(a.get("estimated_cost", 0.1) for a in user_activities)
            suggestion["user_interaction"] = min(0.5, max(0.3, total_user_cost))
        
        # Lern-Aktivitäten
        learning = [a for a in planned_activities if "learn" in a.get("name", "").lower()]
        if learning:
            suggestion["learning"] = min(0.3, 0.15 + len(learning) * 0.05)
        
        # Reserve anpassen
        total_planned = sum(suggestion.values()) - suggestion["reserve"]
        suggestion["reserve"] = max(0.1, 1.0 - total_planned)
        
        # Normalisieren auf 1.0
        total = sum(suggestion.values())
        if total != 1.0:
            factor = 1.0 / total
            suggestion = {k: v * factor for k, v in suggestion.items()}
        
        return suggestion


# =============================================================================
# PRIORITY QUEUE - Aktivitäts-Priorisierung
# =============================================================================

@dataclass
class QueuedTask:
    """Eine Aufgabe in der Queue"""
    task_id: str
    name: str
    priority: int  # Höher = wichtiger
    interest: float
    energy_cost: float
    deadline: Optional[float] = None
    added_at: float = field(default_factory=time.time)
    source: str = "user"  # "user", "system", "self"


class TaskPriorityQueue:
    """
    Priorisiert Aufgaben basierend auf verschiedenen Faktoren.
    """
    
    def __init__(self):
        self.queue: List[QueuedTask] = []
        self.completed: List[str] = []
        self.abandoned: List[str] = []
    
    def add_task(self, name: str, priority: int = 3, interest: float = 0.5,
                 energy_cost: float = 0.1, deadline: float = None,
                 source: str = "user") -> QueuedTask:
        """Füge Aufgabe zur Queue hinzu"""
        task_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
        
        task = QueuedTask(
            task_id=task_id,
            name=name,
            priority=priority,
            interest=interest,
            energy_cost=energy_cost,
            deadline=deadline,
            source=source
        )
        
        self.queue.append(task)
        self._sort_queue()
        
        return task
    
    def _sort_queue(self):
        """Sortiere Queue nach Priorität"""
        def score(task: QueuedTask) -> float:
            # Basis: Priorität
            score = task.priority * 10
            
            # Interesse-Bonus
            score += task.interest * 5
            
            # Deadline-Bonus (je näher desto wichtiger)
            if task.deadline:
                time_until = task.deadline - time.time()
                if time_until < 3600:  # < 1h
                    score += 20
                elif time_until < 86400:  # < 1d
                    score += 10
            
            # User-Source Bonus
            if task.source == "user":
                score += 15
            
            # Alter-Malus (zu alte Tasks verlieren Priorität)
            age_hours = (time.time() - task.added_at) / 3600
            if age_hours > 24:
                score -= min(10, age_hours / 24 * 5)
            
            return score
        
        self.queue.sort(key=score, reverse=True)
    
    def get_next(self, available_energy: float = None) -> Optional[QueuedTask]:
        """
        Hole nächste Aufgabe die gemacht werden kann.
        
        available_energy: Wenn gegeben, nur Tasks die reinpassen
        """
        if not self.queue:
            return None
        
        if available_energy is None:
            return self.queue[0]
        
        # Finde erste Aufgabe die ins Energie-Budget passt
        for task in self.queue:
            if task.energy_cost <= available_energy:
                return task
        
        return None
    
    def complete_task(self, task_id: str):
        """Markiere Aufgabe als erledigt"""
        self.queue = [t for t in self.queue if t.task_id != task_id]
        self.completed.append(task_id)
    
    def abandon_task(self, task_id: str, reason: str = ""):
        """Aufgabe aufgeben"""
        self.queue = [t for t in self.queue if t.task_id != task_id]
        self.abandoned.append(task_id)
    
    def get_queue_summary(self) -> Dict:
        """Hole Queue-Übersicht"""
        return {
            "total_tasks": len(self.queue),
            "total_energy_needed": sum(t.energy_cost for t in self.queue),
            "top_3": [
                {"name": t.name, "priority": t.priority, "cost": t.energy_cost}
                for t in self.queue[:3]
            ],
            "by_source": {
                "user": len([t for t in self.queue if t.source == "user"]),
                "system": len([t for t in self.queue if t.source == "system"]),
                "self": len([t for t in self.queue if t.source == "self"]),
            },
            "completed_today": len(self.completed),
        }


# =============================================================================
# INTELLIGENT BREAK SCHEDULER
# =============================================================================

class BreakScheduler:
    """
    Plant Pausen intelligent basierend auf Aktivität und Energie.
    """
    
    def __init__(self):
        self.last_break = time.time()
        self.breaks_today: List[Dict] = []
        
        # Konfiguration
        self.min_work_before_break = 20 * 60    # 20 Minuten
        self.max_work_before_break = 90 * 60    # 90 Minuten
        self.short_break_duration = 5 * 60      # 5 Minuten
        self.long_break_duration = 15 * 60      # 15 Minuten
        self.long_break_after = 3               # Nach 3 kurzen Pausen
    
    def should_take_break(self, current_energy: float, 
                         activity_intensity: float = 0.5,
                         in_flow: bool = False) -> Dict:
        """
        Entscheide ob Pause nötig.
        
        Returns: {
            "should_break": bool,
            "reason": str,
            "break_type": "short" | "long",
            "suggested_duration": int (seconds)
        }
        """
        time_since_break = time.time() - self.last_break
        breaks_count = len([b for b in self.breaks_today 
                          if b.get("type") == "short"])
        
        result = {
            "should_break": False,
            "reason": "",
            "break_type": "short",
            "suggested_duration": self.short_break_duration,
        }
        
        # Energie kritisch → sofort!
        if current_energy < 0.15:
            result["should_break"] = True
            result["reason"] = "Energie kritisch niedrig"
            result["break_type"] = "long"
            result["suggested_duration"] = self.long_break_duration
            return result
        
        # Im Flow → länger arbeiten erlaubt
        max_work = self.max_work_before_break
        if in_flow:
            max_work *= 1.5  # 50% länger im Flow
        
        # Max Zeit erreicht
        if time_since_break >= max_work:
            result["should_break"] = True
            result["reason"] = "Maximale Arbeitszeit erreicht"
            
            # Lange Pause nach mehreren kurzen
            if breaks_count >= self.long_break_after:
                result["break_type"] = "long"
                result["suggested_duration"] = self.long_break_duration
            
            return result
        
        # Energie + Zeit Kombination
        if current_energy < 0.3 and time_since_break > self.min_work_before_break:
            result["should_break"] = True
            result["reason"] = "Energie niedrig, gute Zeit für Pause"
            return result
        
        # Hohe Intensität + Zeit
        if activity_intensity > 0.8 and time_since_break > self.min_work_before_break * 1.5:
            result["should_break"] = True
            result["reason"] = "Intensive Arbeit, kurze Pause empfohlen"
            return result
        
        return result
    
    def take_break(self, break_type: str = "short", actual_duration: int = None):
        """Registriere eine Pause"""
        self.breaks_today.append({
            "time": time.time(),
            "type": break_type,
            "duration": actual_duration or (
                self.long_break_duration if break_type == "long" 
                else self.short_break_duration
            ),
        })
        self.last_break = time.time()
    
    def get_break_stats(self) -> Dict:
        """Hole Pausen-Statistiken"""
        short_breaks = [b for b in self.breaks_today if b["type"] == "short"]
        long_breaks = [b for b in self.breaks_today if b["type"] == "long"]
        
        total_break_time = sum(b["duration"] for b in self.breaks_today)
        
        return {
            "short_breaks": len(short_breaks),
            "long_breaks": len(long_breaks),
            "total_break_time_minutes": total_break_time / 60,
            "time_since_last_break_minutes": (time.time() - self.last_break) / 60,
            "next_break_due": self._estimate_next_break(),
        }
    
    def _estimate_next_break(self) -> str:
        """Schätze wann nächste Pause fällig"""
        time_since = time.time() - self.last_break
        time_until_max = self.max_work_before_break - time_since
        
        if time_until_max <= 0:
            return "Jetzt!"
        elif time_until_max < 600:
            return "In wenigen Minuten"
        else:
            return f"In ~{time_until_max/60:.0f} Minuten"


# =============================================================================
# INTEREST DECAY SYSTEM
# =============================================================================

class InterestDecayManager:
    """
    Verwaltet wie Interesse über Zeit abnimmt.
    
    Verhindert dass alte Themen ewig in der Queue bleiben.
    """
    
    def __init__(self):
        self.interest_records: Dict[str, Dict] = {}
        
        # Decay-Raten
        self.decay_rate_per_hour = 0.02  # 2% pro Stunde
        self.min_interest = 0.1          # Minimum Interest
        self.boost_on_mention = 0.2      # Boost wenn erwähnt
    
    def record_interest(self, topic: str, initial_interest: float):
        """Zeichne Interesse an einem Thema auf"""
        self.interest_records[topic] = {
            "initial": initial_interest,
            "current": initial_interest,
            "first_seen": time.time(),
            "last_updated": time.time(),
            "mentions": 1,
        }
    
    def get_current_interest(self, topic: str) -> float:
        """Hole aktuelles (verfallenes) Interesse"""
        if topic not in self.interest_records:
            return 0.5  # Default
        
        record = self.interest_records[topic]
        hours_since = (time.time() - record["last_updated"]) / 3600
        
        # Decay berechnen
        decay = hours_since * self.decay_rate_per_hour
        current = max(self.min_interest, record["current"] - decay)
        
        return current
    
    def boost_interest(self, topic: str, amount: float = None):
        """Boost Interesse (z.B. wenn User es wieder erwähnt)"""
        if topic not in self.interest_records:
            return
        
        boost = amount or self.boost_on_mention
        record = self.interest_records[topic]
        record["current"] = min(1.0, record["current"] + boost)
        record["last_updated"] = time.time()
        record["mentions"] += 1
    
    def get_stale_topics(self, threshold: float = 0.3) -> List[str]:
        """Finde Themen deren Interesse unter Schwelle gefallen ist"""
        stale = []
        for topic, record in self.interest_records.items():
            current = self.get_current_interest(topic)
            if current < threshold:
                stale.append(topic)
        return stale
    
    def cleanup(self, threshold: float = 0.2):
        """Entferne Themen mit zu niedrigem Interesse"""
        to_remove = [
            topic for topic in self.interest_records
            if self.get_current_interest(topic) < threshold
        ]
        for topic in to_remove:
            del self.interest_records[topic]
        return to_remove


# =============================================================================
# LEARNING FROM DECISIONS
# =============================================================================

class DecisionLearner:
    """
    Lernt aus vergangenen Energie-Entscheidungen.
    
    Merkt sich:
    - Welche Entscheidungen gut waren
    - Welche zu Erschöpfung führten
    - Optimale Patterns
    """
    
    def __init__(self):
        self.decisions: List[Dict] = []
        self.patterns: Dict[str, Dict] = {}
    
    def record_decision(self, decision_type: str, context: Dict, 
                       energy_before: float, outcome: str = "pending"):
        """Zeichne eine Entscheidung auf"""
        decision = {
            "id": hashlib.md5(f"{decision_type}{time.time()}".encode()).hexdigest()[:8],
            "type": decision_type,
            "context": context,
            "energy_before": energy_before,
            "timestamp": time.time(),
            "outcome": outcome,
            "energy_after": None,
        }
        self.decisions.append(decision)
        return decision["id"]
    
    def update_outcome(self, decision_id: str, outcome: str, energy_after: float):
        """Update Ergebnis einer Entscheidung"""
        for d in self.decisions:
            if d["id"] == decision_id:
                d["outcome"] = outcome
                d["energy_after"] = energy_after
                break
        
        # Lerne aus Ergebnis
        self._learn_from_outcome(decision_id)
    
    def _learn_from_outcome(self, decision_id: str):
        """Lerne aus Entscheidungs-Ergebnis"""
        decision = next((d for d in self.decisions if d["id"] == decision_id), None)
        if not decision or decision["outcome"] == "pending":
            return
        
        dtype = decision["type"]
        outcome = decision["outcome"]
        
        if dtype not in self.patterns:
            self.patterns[dtype] = {
                "good_outcomes": 0,
                "bad_outcomes": 0,
                "avg_energy_delta": 0,
                "common_contexts": [],
            }
        
        pattern = self.patterns[dtype]
        
        if outcome in ["success", "good"]:
            pattern["good_outcomes"] += 1
        elif outcome in ["failure", "bad", "exhausted"]:
            pattern["bad_outcomes"] += 1
        
        # Energie-Delta tracken
        if decision["energy_after"] is not None:
            delta = decision["energy_after"] - decision["energy_before"]
            count = pattern["good_outcomes"] + pattern["bad_outcomes"]
            pattern["avg_energy_delta"] = (
                pattern["avg_energy_delta"] * (count - 1) + delta
            ) / count
    
    def get_recommendation(self, decision_type: str, context: Dict) -> Dict:
        """
        Hole Empfehlung basierend auf gelernten Patterns.
        """
        if decision_type not in self.patterns:
            return {
                "confidence": 0.1,
                "recommendation": "go_ahead",
                "reason": "Keine historischen Daten",
            }
        
        pattern = self.patterns[decision_type]
        total = pattern["good_outcomes"] + pattern["bad_outcomes"]
        
        if total < 5:
            return {
                "confidence": 0.3,
                "recommendation": "go_ahead",
                "reason": "Noch wenige Daten",
            }
        
        success_rate = pattern["good_outcomes"] / total
        avg_delta = pattern["avg_energy_delta"]
        
        if success_rate > 0.7 and avg_delta > -0.1:
            return {
                "confidence": success_rate,
                "recommendation": "go_ahead",
                "reason": f"Historisch {success_rate:.0%} Erfolg",
            }
        elif success_rate < 0.4 or avg_delta < -0.2:
            return {
                "confidence": 1 - success_rate,
                "recommendation": "be_careful",
                "reason": f"Historisch oft problematisch (∅ΔE: {avg_delta:.2f})",
            }
        else:
            return {
                "confidence": 0.5,
                "recommendation": "consider",
                "reason": "Gemischte Ergebnisse",
            }
    
    def get_stats(self) -> Dict:
        """Hole Lern-Statistiken"""
        return {
            "total_decisions": len(self.decisions),
            "patterns_learned": len(self.patterns),
            "patterns": {
                dtype: {
                    "success_rate": p["good_outcomes"] / max(1, p["good_outcomes"] + p["bad_outcomes"]),
                    "avg_energy_impact": p["avg_energy_delta"],
                }
                for dtype, p in self.patterns.items()
            },
        }


# =============================================================================
# ENHANCED ENERGY MANAGEMENT V2
# =============================================================================

class HoloEnergyManagementV2(HoloEnergyManagement):
    """
    Erweitertes Energie-Management mit allen neuen Features.
    """
    
    def __init__(self, energy_system, data_dir: Path = None):
        super().__init__(energy_system, data_dir)
        
        # Neue Subsysteme
        self.budget_planner = EnergyBudgetPlanner()
        self.task_queue = TaskPriorityQueue()
        self.break_scheduler = BreakScheduler()
        self.interest_decay = InterestDecayManager()
        self.decision_learner = DecisionLearner()
        
        # Tagesstart
        self.budget_planner.start_day(self.energy.get_variable_energy())
    
    def plan_day(self, planned_activities: List[Dict] = None) -> Dict:
        """
        Plane den Tag.
        
        planned_activities: [{"name": str, "priority": str, "estimated_cost": float}]
        """
        # Budget basierend auf Aktivitäten
        if planned_activities:
            suggested = self.budget_planner.suggest_allocation(planned_activities)
            self.budget_planner.current_budget.allocated = suggested
            
            # Activities zur Queue
            for activity in planned_activities:
                self.task_queue.add_task(
                    name=activity["name"],
                    priority=5 if activity.get("priority") == "critical" else 3,
                    interest=activity.get("interest", 0.5),
                    energy_cost=activity.get("estimated_cost", 0.1),
                    source="user"
                )
        
        return {
            "budget": self.budget_planner.get_daily_summary(),
            "queue": self.task_queue.get_queue_summary(),
            "thought": random.choice(HoloThoughts.HIGH_ENERGY) 
                      if self.energy.get_variable_energy() > 0.7
                      else random.choice(HoloThoughts.MEDIUM_ENERGY),
        }
    
    def get_next_task(self) -> Optional[Dict]:
        """Hole nächste empfohlene Aufgabe"""
        available = self.get_available_energy()
        task = self.task_queue.get_next(available)
        
        if not task:
            return None
        
        # Recommendation vom Learner
        rec = self.decision_learner.get_recommendation(
            f"task_{task.priority}",
            {"energy": available, "interest": task.interest}
        )
        
        return {
            "task": task,
            "recommendation": rec,
            "available_energy": available,
            "budget_status": self.budget_planner.get_category_status(
                "user_interaction" if task.source == "user" else "spontaneous"
            ),
        }
    
    def complete_task(self, task_id: str, outcome: str = "success"):
        """Schließe Aufgabe ab"""
        self.task_queue.complete_task(task_id)
        
        # Lerne aus Entscheidung
        self.decision_learner.update_outcome(
            task_id, 
            outcome, 
            self.energy.get_variable_energy()
        )
    
    def check_break_needed(self, in_flow: bool = False) -> Dict:
        """Prüfe ob Pause nötig"""
        return self.break_scheduler.should_take_break(
            self.energy.get_variable_energy(),
            activity_intensity=0.7 if self.current_research else 0.5,
            in_flow=in_flow
        )
    
    def take_break_now(self, break_type: str = "short"):
        """Mache jetzt Pause"""
        self.break_scheduler.take_break(break_type)
        return {
            "message": random.choice(HoloThoughts.BREAK),
            "stats": self.break_scheduler.get_break_stats(),
        }
    
    def update_interest(self, topic: str, interest: float = None):
        """Update Interesse an Thema"""
        if topic in self.interest_decay.interest_records:
            if interest:
                self.interest_decay.interest_records[topic]["current"] = interest
            else:
                self.interest_decay.boost_interest(topic)
        else:
            self.interest_decay.record_interest(topic, interest or 0.5)
    
    def get_comprehensive_context(self) -> str:
        """Erweiterter Kontext für Prompts"""
        base_context = self.get_prompt_context()
        
        sections = [base_context]
        
        # Budget Status
        budget = self.budget_planner.get_daily_summary()
        if budget:
            sections.append(f"\n📊 Tages-Budget: {budget['percent_used']:.0f}% verbraucht")
        
        # Queue Status
        queue = self.task_queue.get_queue_summary()
        if queue["total_tasks"] > 0:
            sections.append(f"📋 {queue['total_tasks']} Aufgaben in Queue")
            if queue["top_3"]:
                sections.append(f"   Nächste: {queue['top_3'][0]['name']}")
        
        # Break Status
        break_status = self.break_scheduler.get_break_stats()
        sections.append(f"\n⏰ Nächste Pause: {break_status['next_break_due']}")
        
        # Stale Topics warnen
        stale = self.interest_decay.get_stale_topics()
        if stale:
            sections.append(f"\n⚠️ Vergessene Themen: {', '.join(stale[:3])}")
        
        return "\n".join(sections)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("🧠 HOLO ENERGY MANAGEMENT V2 - TEST")
    print("=" * 70)

    # Mock Energy System
    class MockEnergySystem:
        def __init__(self):
            self.variable = 0.8

        def get_variable_energy(self):
            return self.variable

        def get_base_energy(self):
            return 0.9

        def get_warnings(self):
            return [] if self.variable > 0.3 else ["Energie niedrig"]

        def consume_for_activity(self, activity, minutes):
            self.variable -= 0.01 * minutes / 50
            self.variable = max(0, self.variable)

    mock_energy = MockEnergySystem()
    manager = HoloEnergyManagementV2(mock_energy, Path("/tmp/test_mgmt_v2"))

    # 1. Tagesplanung
    print("\n1️⃣ TAGESPLANUNG:")
    day_plan = manager.plan_day([
        {"name": "User helfen", "priority": "critical", "estimated_cost": 0.2},
        {"name": "Über Wölfe lernen", "interest": 0.9, "estimated_cost": 0.15},
        {"name": "System-Check", "estimated_cost": 0.05},
    ])
    print(f"   Budget verbraucht: {day_plan['budget']['percent_used']:.0f}%")
    print(f"   Tasks in Queue: {day_plan['queue']['total_tasks']}")

    # 2. Nächste Aufgabe
    print("\n2️⃣ NÄCHSTE AUFGABE:")
    next_task = manager.get_next_task()
    if next_task:
        print(f"   Task: {next_task['task'].name}")
        print(f"   Empfehlung: {next_task['recommendation']['recommendation']}")

    # 3. Break Check
    print("\n3️⃣ PAUSEN-CHECK:")
    break_check = manager.check_break_needed()
    print(f"   Pause nötig: {break_check['should_break']}")
    print(f"   Grund: {break_check['reason'] or 'Keiner'}")

    # 4. Interest Decay
    print("\n4️⃣ INTEREST DECAY:")
    manager.update_interest("Wölfe", 0.9)
    manager.update_interest("Python", 0.6)
    print(f"   Wölfe-Interest: {manager.interest_decay.get_current_interest('Wölfe'):.2f}")
    
    # 5. Decision Learning
    print("\n5️⃣ DECISION LEARNING:")
    dec_id = manager.decision_learner.record_decision(
        "task_5", {"energy": 0.8}, 0.8
    )
    manager.decision_learner.update_outcome(dec_id, "success", 0.7)
    stats = manager.decision_learner.get_stats()
    print(f"   Decisions tracked: {stats['total_decisions']}")

    # 6. Comprehensive Context
    print("\n6️⃣ COMPREHENSIVE CONTEXT:")
    print(manager.get_comprehensive_context())

    print("\n" + "=" * 70)
    print("✅ Energy Management V2 Tests abgeschlossen!")
