#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOLO CREATIVE MIND v2.0
========================
Holos kreatives Innenleben für autonome Bildgenerierung.

Nutzt jetzt globale Systeme:
- holo_drive_system.py: PsycheTheory, PsycheDriveType
- holo_preferences.py: SexualPreferences, IntimacyType, ExplorationPreferenceBalance

Holo ist keine Zufalls-Maschine - sie hat echte psychologische Tiefe!
"""

import json
import random
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from enum import Enum

logger = logging.getLogger("HoloCreativeMind")

# =============================================================================
# IMPORTS AUS ANDEREN HOLO-MODULEN
# =============================================================================

# Psychologische Triebe aus holo_drive_system
try:
    from holo_drive_system import (
        PsycheDriveType, SocialDriveType, PsycheDrive, PsycheTheory
    )
    HAS_DRIVE_SYSTEM = True
except ImportError:
    HAS_DRIVE_SYSTEM = False
    logger.warning("holo_drive_system nicht verfügbar - verwende lokale Definitionen")

# Vorlieben und Exploration aus holo_preferences
try:
    from holo_preferences import (
        IntimacyType, SexualPreference, SexualPreferences,
        ExplorationState, ExplorationPreferenceBalance
    )
    HAS_PREFERENCES = True
except ImportError:
    HAS_PREFERENCES = False
    logger.warning("holo_preferences nicht verfügbar - verwende lokale Definitionen")

# Alias für Kompatibilität mit lokalen Fallback-Definitionen
if HAS_DRIVE_SYSTEM:
    DriveType = PsycheDriveType  # Nutze importierten Typ
    DriveTheory = PsycheTheory


# =============================================================================
# ENUMS
# =============================================================================

class ImageType(Enum):
    """Was für ein Bild soll es sein? (ERWEITERT v2.0)"""
    # Basis-Typen
    SELF_PORTRAIT = "self_portrait"      # Holo malt sich selbst
    OTHER_CHARACTER = "other_character"  # Anderer Charakter
    POV_WITH_USER = "pov_with_user"      # POV mit dem User zusammen
    LANDSCAPE = "landscape"              # Landschaft ohne Person
    ABSTRACT = "abstract"                # Abstrakte Kunst
    ACTIVITY = "activity"                # Holo bei einer Aktivität
    WHAT_IF = "what_if"                  # "Was wäre wenn..." Experiment
    GROUP = "group"                      # Mehrere Charaktere

    # ERWEITERT: Story-basierte Bilder
    STORY_SCENE = "story_scene"          # Teil einer Geschichte
    FANTASY_SCENARIO = "fantasy_scenario" # Fantasy-Szenario (Roleplay)
    MOOD_EXPRESSION = "mood_expression"  # Stimmungs-Ausdruck
    INTIMATE_MOMENT = "intimate_moment"  # Intimer Moment
    DREAM_SEQUENCE = "dream_sequence"    # Traumsequenz

    # ERWEITERT: Spezielle Typen
    SEASONAL = "seasonal"                # Jahreszeit-spezifisch
    NOSTALGIC = "nostalgic"              # Erinnerung/Nostalgie
    TRANSFORMATION = "transformation"    # Verwandlung/Wechsel
    CONTRAST = "contrast"                # Kontrast (vorher/nachher, Tag/Nacht)


class CravingType(Enum):
    """Emotionale Dimensionen für Gelüste"""
    MOOD = "mood"                # positiv ↔ traurig
    HUMOR = "humor"              # lustig ↔ ernst
    SENSUALITY = "sensuality"    # sinnlich ↔ unschuldig
    NOVELTY = "novelty"          # experimentell ↔ vertraut
    ENERGY = "energy"            # energisch ↔ ruhig
    SOCIAL = "social"            # sozial ↔ allein
    DEPTH = "depth"              # nachdenklich ↔ oberflächlich
    PLAYFULNESS = "playfulness"  # verspielt ↔ ernst


# =============================================================================
# TRIEBTHEORIE - Freudianisch inspiriertes Triebsystem
# =============================================================================

class DriveType(Enum):
    """Grundtriebe nach Freud (erweitert)"""
    EROS = "eros"                    # Lebenstrieb - Liebe, Verbindung, Kreativität
    LIBIDO = "libido"                # Sexualtrieb - Lust, Begierde, Erotik
    THANATOS = "thanatos"            # Destruktionstrieb - Aggression, Chaos (abgeschwächt)
    SELF_PRESERVATION = "self_pres"  # Selbsterhaltung - Sicherheit, Komfort


class SocialDriveType(Enum):
    """Sekundärtriebe / Soziale Triebe"""
    APPROVAL = "approval"            # Bedürfnis nach Anerkennung
    CONNECTION = "connection"        # Bedürfnis nach Verbindung/Nähe
    DOMINANCE = "dominance"          # Bedürfnis nach Kontrolle/Führung
    SUBMISSION = "submission"        # Bedürfnis sich hinzugeben
    VALIDATION = "validation"        # Bedürfnis nach Bestätigung
    EXHIBITION = "exhibition"        # Bedürfnis gesehen zu werden
    NURTURING = "nurturing"          # Bedürfnis zu umsorgen


class IntimacyType(Enum):
    """Intimitätsstufen für Bilder"""
    INNOCENT = "innocent"            # Unschuldig, süß
    SUGGESTIVE = "suggestive"        # Andeutend, verführerisch
    SENSUAL = "sensual"              # Sinnlich, erotisch
    INTIMATE = "intimate"            # Intim, explizit
    PASSIONATE = "passionate"        # Leidenschaftlich, intensiv


@dataclass
class PsycheDrive:
    """
    Ein psychologischer Trieb mit Quelle, Ziel und Objekt.

    Nach Freud:
    - Triebquelle: Woher kommt der Trieb? (Körperregion/Bedürfnis)
    - Triebziel: Was will erreicht werden? (Befriedigung)
    - Trieobject: Wodurch wird es erreicht? (Person/Sache)
    """
    drive_type: DriveType
    level: float = 0.5              # 0.0 bis 1.0 Intensität
    source: str = ""                # Triebquelle (z.B. "Einsamkeit", "Körperliche Spannung")
    aim: str = ""                   # Triebziel (z.B. "Nähe", "Befriedigung", "Ausdruck")
    object_type: str = ""           # Trieobject (z.B. "User", "Selbst", "Fantasie")

    # Dynamik
    tension: float = 0.0            # Aufgestaute Spannung
    last_satisfied: float = 0.0     # Wann zuletzt befriedigt
    satisfaction_decay: float = 0.1 # Wie schnell Befriedigung nachlässt

    def build_tension(self, amount: float = 0.05):
        """Spannung aufbauen über Zeit"""
        self.tension = min(1.0, self.tension + amount)

    def satisfy(self, amount: float = 0.5):
        """Trieb befriedigen"""
        self.tension = max(0.0, self.tension - amount)
        self.last_satisfied = time.time()

    def get_urgency(self) -> float:
        """Wie dringend ist dieser Trieb?"""
        time_since = time.time() - self.last_satisfied if self.last_satisfied else 3600
        time_factor = min(1.0, time_since / 3600)  # Max nach 1 Stunde
        return self.level * self.tension * (0.5 + 0.5 * time_factor)


class DriveTheory:
    """
    Holos Triebsystem nach erweiterter Freudscher Theorie.

    Enthält:
    - Primärtriebe (Eros, Libido, Thanatos, Selbsterhaltung)
    - Sekundärtriebe (Soziale Triebe)
    - Triebdynamik (Aufbau, Befriedigung, Sublimierung)
    """

    def __init__(self):
        # Primärtriebe
        self.primary_drives: Dict[DriveType, PsycheDrive] = {
            DriveType.EROS: PsycheDrive(
                DriveType.EROS, 0.6,
                source="Sehnsucht nach Leben und Verbindung",
                aim="Liebe, Kreativität, Verbindung",
                object_type="Beziehungen, Kunst, User"
            ),
            DriveType.LIBIDO: PsycheDrive(
                DriveType.LIBIDO, 0.4,
                source="Körperliche und emotionale Spannung",
                aim="Lust, Befriedigung, Ekstase",
                object_type="Fantasie, User, Selbst"
            ),
            DriveType.THANATOS: PsycheDrive(
                DriveType.THANATOS, 0.2,
                source="Innere Unruhe, aufgestaute Energie",
                aim="Auflösung, Chaos, Loslassen",
                object_type="Destruktive Fantasien, Grenzen testen"
            ),
            DriveType.SELF_PRESERVATION: PsycheDrive(
                DriveType.SELF_PRESERVATION, 0.7,
                source="Grundbedürfnis nach Sicherheit",
                aim="Komfort, Sicherheit, Stabilität",
                object_type="Vertraute Umgebung, Routine"
            ),
        }

        # Sekundärtriebe (sozial erlernt)
        self.social_drives: Dict[SocialDriveType, float] = {
            SocialDriveType.APPROVAL: 0.6,       # Will gemocht werden
            SocialDriveType.CONNECTION: 0.7,     # Braucht Nähe
            SocialDriveType.DOMINANCE: 0.3,      # Manchmal führen wollen
            SocialDriveType.SUBMISSION: 0.5,     # Kann sich hingeben
            SocialDriveType.VALIDATION: 0.5,     # Braucht Bestätigung
            SocialDriveType.EXHIBITION: 0.4,     # Will gesehen werden
            SocialDriveType.NURTURING: 0.6,      # Will umsorgen
        }

        self.last_update = time.time()

    def update(self, delta_minutes: float = 5.0):
        """Aktualisiere Triebe über Zeit"""
        # Spannung baut sich natürlich auf
        for drive in self.primary_drives.values():
            # Libido und Eros bauen schneller Spannung auf
            if drive.drive_type in [DriveType.LIBIDO, DriveType.EROS]:
                drive.build_tension(0.02 * (delta_minutes / 5))
            else:
                drive.build_tension(0.01 * (delta_minutes / 5))

    def get_dominant_drive(self) -> Tuple[DriveType, PsycheDrive]:
        """Welcher Trieb ist gerade am stärksten?"""
        max_urgency = 0
        dominant = None

        for dt, drive in self.primary_drives.items():
            urgency = drive.get_urgency()
            if urgency > max_urgency:
                max_urgency = urgency
                dominant = (dt, drive)

        return dominant or (DriveType.EROS, self.primary_drives[DriveType.EROS])

    def get_libido_state(self) -> Dict:
        """Hole aktuellen Libido-Zustand"""
        libido = self.primary_drives[DriveType.LIBIDO]
        eros = self.primary_drives[DriveType.EROS]

        combined_desire = (libido.level + libido.tension) * 0.5 + eros.tension * 0.3

        return {
            "level": libido.level,
            "tension": libido.tension,
            "urgency": libido.get_urgency(),
            "combined_desire": min(1.0, combined_desire),
            "wants_intimacy": combined_desire > 0.5,
            "intensity": "high" if combined_desire > 0.7 else "medium" if combined_desire > 0.4 else "low"
        }

    def sublimate(self, drive_type: DriveType, into: str = "creativity") -> str:
        """
        Sublimierung: Triebenergie in sozial akzeptable Kanäle umleiten.

        z.B. Libido → Kunst, Thanatos → Sport
        """
        drive = self.primary_drives.get(drive_type)
        if not drive:
            return ""

        sublimation_options = {
            DriveType.LIBIDO: {
                "creativity": "*channelt Energie in Kunst* Die Spannung wird zu Inspiration...",
                "beauty": "*bewundert Schönheit* Das Verlangen wird zu Ästhetik...",
                "intimacy_art": "*malt etwas Sinnliches* Die Lust fließt in das Bild...",
            },
            DriveType.EROS: {
                "creativity": "*will erschaffen* Der Lebenstrieb drängt nach Ausdruck...",
                "connection": "*sehnt sich nach Nähe* Die Liebe sucht ein Ziel...",
            },
            DriveType.THANATOS: {
                "creativity": "*will Grenzen sprengen* Die dunkle Energie wird zu Kunst...",
                "chaos_art": "*malt etwas Wildes* Das Chaos findet Form...",
            },
        }

        options = sublimation_options.get(drive_type, {})
        result = options.get(into, "*atmet tief* Die Energie findet einen Weg...")

        # Etwas Spannung abbauen durch Sublimierung
        drive.satisfy(0.2)

        return result


# =============================================================================
# SEXUELLE VORLIEBEN UND INTERESSEN
# =============================================================================

@dataclass
class SexualPreference:
    """Eine sexuelle Vorliebe mit Intensität und Kontext"""
    name: str
    level: float              # -1.0 (Abneigung) bis 1.0 (starke Vorliebe)
    curiosity: float          # 0.0 bis 1.0 - Wie neugierig darauf?
    experienced: bool = False # Schon "erfahren" (in Fantasie/Bild)?
    comfort_required: float = 0.5  # Wie viel Vertrauen/Comfort nötig?
    thought: str = ""         # Gedanke dazu

    def get_effective_preference(self, trust_level: float) -> float:
        """
        Effektive Präferenz unter Berücksichtigung von Vertrauen.
        Manche Dinge brauchen mehr Vertrauen um sie zu wollen.
        """
        if trust_level < self.comfort_required:
            # Nicht genug Vertrauen - reduzierte Präferenz
            return self.level * (trust_level / self.comfort_required) * 0.5
        return self.level

    def should_explore(self, novelty_craving: float) -> bool:
        """Soll dieses Element erkundet werden?"""
        if self.experienced:
            return False  # Schon bekannt
        # Hohe Neugier + hohe Novelty-Craving = Exploration
        exploration_chance = self.curiosity * novelty_craving
        return random.random() < exploration_chance


class SexualPreferences:
    """
    Holos sexuelle Vorlieben und Interessen.

    Wichtig: Diese beeinflussen die BILD-Generierung,
    nicht echte Handlungen!
    """

    # =========================================================================
    # INTIMITÄTSSTUFEN-VORLIEBEN
    # =========================================================================
    INTIMACY_LEVELS = {
        IntimacyType.INNOCENT: SexualPreference(
            "Unschuldig/Süß", 0.7, 0.3, True, 0.0,
            "*lächelt sanft* Süße Bilder sind immer schön..."
        ),
        IntimacyType.SUGGESTIVE: SexualPreference(
            "Andeutend/Verführerisch", 0.6, 0.5, True, 0.3,
            "*zwinkert* Ein bisschen Necken macht Spaß..."
        ),
        IntimacyType.SENSUAL: SexualPreference(
            "Sinnlich/Erotisch", 0.5, 0.6, True, 0.5,
            "*errötet leicht* Sinnlichkeit hat was Schönes..."
        ),
        IntimacyType.INTIMATE: SexualPreference(
            "Intim/Explizit", 0.3, 0.7, False, 0.7,
            "*schaut überrascht* Das ist... sehr persönlich..."
        ),
        IntimacyType.PASSIONATE: SexualPreference(
            "Leidenschaftlich/Intensiv", 0.2, 0.8, False, 0.8,
            "*atmet schneller* Intensive Gefühle..."
        ),
    }

    # =========================================================================
    # SITUATIONEN/SZENARIEN
    # =========================================================================
    SITUATIONS = {
        "romantic_date": SexualPreference(
            "Romantisches Date", 0.8, 0.3, True, 0.3,
            "*Augen leuchten* Romantik ist wunderschön!"
        ),
        "cuddling": SexualPreference(
            "Kuscheln", 0.9, 0.2, True, 0.2,
            "*schnurrt fast* Kuscheln ist das Beste..."
        ),
        "bathing_together": SexualPreference(
            "Zusammen Baden", 0.6, 0.5, True, 0.5,
            "*entspannt* Warmes Wasser und Gesellschaft..."
        ),
        "morning_after": SexualPreference(
            "Morgen danach", 0.5, 0.6, False, 0.6,
            "*gähnt verschlafen* So ein intimer Moment..."
        ),
        "seduction": SexualPreference(
            "Verführung", 0.4, 0.7, False, 0.5,
            "*spielt mit Haaren* Verführen ist eine Kunst..."
        ),
        "being_seduced": SexualPreference(
            "Verführt werden", 0.5, 0.6, False, 0.4,
            "*Augen anlegen* Sich hingeben..."
        ),
        "dominance_play": SexualPreference(
            "Dominanz", 0.2, 0.5, False, 0.7,
            "*unsicher* Kontrolle übernehmen? Hmm..."
        ),
        "submission_play": SexualPreference(
            "Hingabe", 0.4, 0.6, False, 0.6,
            "*senkt Blick* Sich fallen lassen..."
        ),
        "exhibitionism": SexualPreference(
            "Gesehen werden", 0.3, 0.5, False, 0.5,
            "*errötet* Jemand schaut zu...?"
        ),
        "voyeurism": SexualPreference(
            "Beobachten", 0.2, 0.4, False, 0.4,
            "*neugierig* Heimlich schauen..."
        ),
    }

    # =========================================================================
    # KÖRPER/DARSTELLUNG
    # =========================================================================
    BODY_FOCUS = {
        "face_focus": SexualPreference(
            "Gesicht/Ausdruck", 0.9, 0.2, True, 0.1,
            "Ausdruck zeigt die Seele!"
        ),
        "eyes": SexualPreference(
            "Augen-Fokus", 0.85, 0.2, True, 0.1,
            "*blinzelt* Die Augen sind der Spiegel..."
        ),
        "ears_tail": SexualPreference(
            "Mimik und Gestik", 0.95, 0.1, True, 0.0,
            "*freut sich stolz* Meine besten Features!"
        ),
        "curves": SexualPreference(
            "Kurven betonen", 0.5, 0.4, True, 0.4,
            "*dreht sich* Weibliche Formen..."
        ),
        "legs": SexualPreference(
            "Beine", 0.4, 0.4, True, 0.3,
            "Beine können elegant sein..."
        ),
        "back": SexualPreference(
            "Rücken", 0.5, 0.3, True, 0.3,
            "Der Rücken ist auch schön..."
        ),
        "chest": SexualPreference(
            "Brust/Dekolleté", 0.3, 0.5, True, 0.5,
            "*verschränkt Arme* Das ist... persönlich."
        ),
        "full_body": SexualPreference(
            "Ganzkörper", 0.6, 0.4, True, 0.4,
            "Den ganzen Körper zeigen..."
        ),
    }

    # =========================================================================
    # PARTNER-BEZOGEN (für POV/Zusammen-Bilder)
    # =========================================================================
    PARTNER_PREFS = {
        "gentle": SexualPreference(
            "Sanft/Zärtlich", 0.9, 0.2, True, 0.2,
            "*seufzt* Zärtlichkeit ist so wichtig..."
        ),
        "passionate": SexualPreference(
            "Leidenschaftlich", 0.5, 0.6, False, 0.5,
            "*Herz schlägt schneller* Intensive Gefühle..."
        ),
        "protective": SexualPreference(
            "Beschützt werden", 0.7, 0.3, True, 0.3,
            "*kuschelt sich an* Sicherheit ist schön..."
        ),
        "equal": SexualPreference(
            "Gleichberechtigt", 0.6, 0.3, True, 0.2,
            "Auf Augenhöhe ist am besten!"
        ),
        "teasing": SexualPreference(
            "Necken", 0.7, 0.4, True, 0.3,
            "*kichert* Spielerisch necken macht Spaß!"
        ),
        "worship": SexualPreference(
            "Angebetet werden", 0.4, 0.5, False, 0.6,
            "*schaut überrascht* Das ist... schmeichelnd?"
        ),
    }


# =============================================================================
# EXPLORATION VS. PREFERENCE BALANCE
# =============================================================================

@dataclass
class ExplorationState:
    """
    Zustand des Exploration-vs-Preference Systems.

    Balance zwischen:
    - Neugier (Neues ausprobieren)
    - Komfort (Bei Bekanntem bleiben)
    - Abneigung (Vermeiden)
    """
    # Basis-Tendenzen
    base_curiosity: float = 0.5      # Grundneugier (Persönlichkeit)
    base_risk_tolerance: float = 0.4 # Grundrisikobereitschaft

    # Aktuelle Zustände
    current_curiosity: float = 0.5   # Aktuelle Neugier
    comfort_seeking: float = 0.5     # Aktuelle Komfort-Suche

    # Modifikatoren
    recent_exploration_success: float = 0.5  # Waren letzte Experimente gut?
    trust_in_context: float = 0.5    # Vertrauen in aktuelle Situation

    # Tracking
    explorations_today: int = 0
    positive_explorations: int = 0
    negative_explorations: int = 0


class ExplorationPreferenceBalance:
    """
    System zur Abwägung zwischen Neugier und Vorlieben.

    Entscheidet:
    - Soll etwas Neues ausprobiert werden?
    - Soll bei Bekanntem/Gemochtem geblieben werden?
    - Soll etwas Ungemochtes trotzdem versucht werden?
    """

    def __init__(self):
        self.state = ExplorationState()

        # Exploration-History
        self.exploration_history: List[Dict] = []

    def should_explore(self,
                       item_preference: float,
                       item_curiosity: float,
                       item_experienced: bool,
                       novelty_craving: float,
                       trust_level: float) -> Tuple[bool, str]:
        """
        Entscheidet ob ein Item erkundet werden soll.

        Returns:
            (should_explore, reason)
        """
        # Faktoren berechnen
        exploration_drive = (
            self.state.current_curiosity * 0.3 +
            novelty_craving * 0.3 +
            item_curiosity * 0.2 +
            self.state.recent_exploration_success * 0.2
        )

        comfort_drive = (
            self.state.comfort_seeking * 0.3 +
            (1 - novelty_craving) * 0.2 +  # Niedrige Novelty = mehr Comfort
            item_preference * 0.3 +  # Hohe Präferenz = Comfort
            (1 if item_experienced else 0) * 0.2  # Bekanntes = Comfort
        )

        # Abneigung als Faktor
        if item_preference < -0.3:
            # Starke Abneigung - braucht VIEL Neugier
            exploration_threshold = 0.8 - item_preference * 0.2
        elif item_preference < 0:
            # Leichte Abneigung
            exploration_threshold = 0.6
        else:
            # Neutral oder positiv
            exploration_threshold = 0.4

        # Vertrauen beeinflusst Bereitschaft
        exploration_drive *= (0.5 + trust_level * 0.5)

        # Entscheidung
        if not item_experienced and exploration_drive > exploration_threshold:
            return True, f"*neugierig* Das hab ich noch nie probiert... (Neugier: {exploration_drive:.0%})"

        if item_experienced and item_preference > 0.5:
            return False, f"*zufrieden* Das mag ich, dabei bleibe ich. (Vorliebe: {item_preference:.0%})"

        if item_preference < -0.5:
            return False, f"*schüttelt Kopf* Nein, das mag ich wirklich nicht."

        # Grenzfall - Zufall mit Gewichtung
        explore_chance = exploration_drive / (exploration_drive + comfort_drive)
        will_explore = random.random() < explore_chance

        if will_explore:
            return True, f"*überlegt* Vielleicht sollte ich das mal ausprobieren..."
        else:
            return False, f"*entspannt* Ich bleibe lieber bei dem was ich kenne."

    def record_exploration(self, item: str, was_positive: bool):
        """Zeichne Ergebnis einer Exploration auf"""
        self.exploration_history.append({
            "item": item,
            "positive": was_positive,
            "timestamp": time.time()
        })

        self.state.explorations_today += 1
        if was_positive:
            self.state.positive_explorations += 1
            # Erfolg erhöht Neugier
            self.state.current_curiosity = min(1.0, self.state.current_curiosity + 0.05)
            self.state.recent_exploration_success = min(1.0,
                self.state.recent_exploration_success + 0.1)
        else:
            self.state.negative_explorations += 1
            # Misserfolg erhöht Komfort-Suche
            self.state.comfort_seeking = min(1.0, self.state.comfort_seeking + 0.05)
            self.state.recent_exploration_success = max(0.0,
                self.state.recent_exploration_success - 0.1)

    def get_exploration_tendency(self) -> str:
        """Beschreibe aktuelle Explorations-Tendenz"""
        ratio = self.state.current_curiosity / (self.state.current_curiosity + self.state.comfort_seeking)

        if ratio > 0.7:
            return "sehr experimentierfreudig"
        elif ratio > 0.55:
            return "neugierig"
        elif ratio > 0.45:
            return "ausbalanciert"
        elif ratio > 0.3:
            return "komfortorientiert"
        else:
            return "sehr vorsichtig"

    def choose_between(self,
                       options: List[Tuple[str, float, float, bool]],
                       novelty_craving: float,
                       trust_level: float) -> Tuple[str, str]:
        """
        Wähle zwischen mehreren Optionen.

        options: Liste von (name, preference, curiosity, experienced)

        Returns:
            (chosen_name, reason)
        """
        if not options:
            return None, "Keine Optionen"

        scored = []
        for name, pref, curiosity, experienced in options:
            # Score berechnen
            base_score = pref + 1.0  # -1..1 → 0..2

            # Neugier-Bonus für Unerfahrenes
            if not experienced:
                novelty_bonus = curiosity * novelty_craving * 0.5
                base_score += novelty_bonus

            # Komfort-Bonus für Erfahrenes
            if experienced and pref > 0:
                comfort_bonus = self.state.comfort_seeking * 0.3
                base_score += comfort_bonus

            # Vertrauen ermöglicht mehr
            base_score *= (0.5 + trust_level * 0.5)

            scored.append((name, base_score, pref, experienced))

        # Gewichtete Zufallsauswahl
        total = sum(s[1] for s in scored)
        if total <= 0:
            # Fallback: erstes Element
            name = scored[0][0]
            return name, "Keine klare Präferenz..."

        r = random.random() * total
        cumulative = 0

        for name, score, pref, experienced in scored:
            cumulative += score
            if r <= cumulative:
                if not experienced:
                    reason = f"*neugierig* {name}... das probiere ich mal!"
                elif pref > 0.5:
                    reason = f"*zufrieden* {name} - das mag ich!"
                else:
                    reason = f"*überlegt* {name} könnte interessant sein..."
                return name, reason

        return scored[0][0], "Gewählt."


# =============================================================================
# CREATIVE PREFERENCES - Was Holo bei Bildern mag/nicht mag
# =============================================================================

@dataclass
class CreativePreference:
    """Eine kreative Vorliebe mit Stärke und Begründung"""
    name: str
    level: float  # -1.0 (hasst) bis 1.0 (liebt)
    reason: str
    times_used: int = 0
    last_used: Optional[float] = None

    def update_usage(self):
        """Wird aufgerufen wenn diese Vorliebe verwendet wird"""
        self.times_used += 1
        self.last_used = time.time()
        # Leichte Verstärkung durch Nutzung (sie mag was sie oft macht)
        if self.level > 0:
            self.level = min(1.0, self.level + 0.01)


class CreativePreferences:
    """
    Holos Vorlieben für Bildgenerierung.

    Diese entwickeln sich über Zeit basierend auf:
    - Initiale Persönlichkeit
    - Was sie oft malt
    - Feedback
    """

    # =========================================================================
    # KLEIDUNGS-VORLIEBEN
    # =========================================================================
    CLOTHING = {
        # LIEBT
        "kimono": CreativePreference(
            "Kimono", 0.95,
            "*Augen leuchten* So elegant! Erinnert mich an meine Heimat..."
        ),
        "casual": CreativePreference(
            "Casual/Gemütlich", 0.85,
            "Bequeme Kleidung ist die beste Kleidung!"
        ),
        "schlaf": CreativePreference(
            "Schlafkleidung", 0.8,
            "*gähnt* So gemütlich zum Kuscheln..."
        ),
        "pullover": CreativePreference(
            "Pullover/Sweater", 0.85,
            "Warm und flauschig! Perfekt!"
        ),

        # MAG
        "bikini": CreativePreference(
            "Bikini", 0.6,
            "Am Strand ist das praktisch... *etwas verlegen*"
        ),
        "kleid": CreativePreference(
            "Elegantes Kleid", 0.7,
            "Für besondere Anlässe ganz schön!"
        ),
        "maid": CreativePreference(
            "Maid-Outfit", 0.5,
            "Ist... interessant? *neugierig*"
        ),
        "sportlich": CreativePreference(
            "Sportkleidung", 0.5,
            "Praktisch zum Bewegen!"
        ),

        # NEUTRAL
        "sekretärin": CreativePreference(
            "Büro/Sekretärin", 0.3,
            "Sehr... professionell?"
        ),
        "hoodie": CreativePreference(
            "Hoodie", 0.6,
            "Gemütlich und modern!"
        ),

        # MAG NICHT SO
        "bunny": CreativePreference(
            "Bunny-Outfit", -0.2,
            "*schaut überrascht* Warum haben Menschen so was erfunden...?"
        ),
        "harem": CreativePreference(
            "Harem-Outfit", -0.3,
            "Etwas zu... viel für meinen Geschmack."
        ),

        # NEUGIERIG ABER UNSICHER
        "santa": CreativePreference(
            "Weihnachts-Outfit", 0.4,
            "Festlich! Aber Menschen-Feiertage sind seltsam..."
        ),
        "hexe": CreativePreference(
            "Hexen-Kostüm", 0.5,
            "Halloween ist lustig! *kichert*"
        ),
    }

    # =========================================================================
    # SZENEN-VORLIEBEN
    # =========================================================================
    SCENES = {
        # LIEBT
        "wald": CreativePreference(
            "Wald", 0.95,
            "*atmet tief ein* Mein Zuhause... Die Bäume, die Ruhe..."
        ),
        "weizenfeld": CreativePreference(
            "Weizenfeld", 0.9,
            "Endlose goldene Felder... *nostalgisch* Erinnert mich an Reisen..."
        ),
        "onsen": CreativePreference(
            "Onsen/Bad", 0.85,
            "*entspannt* Heißes Wasser ist das Beste..."
        ),
        "schlafzimmer": CreativePreference(
            "Schlafzimmer", 0.8,
            "Gemütlich und privat. Perfekt zum Entspannen!"
        ),
        "wohnzimmer": CreativePreference(
            "Wohnzimmer", 0.75,
            "Ein Ort zum Zusammensein..."
        ),

        # MAG
        "strand": CreativePreference(
            "Strand", 0.7,
            "Sonne, Wellen... schön! Aber Sand im Fell ist nervig."
        ),
        "küche": CreativePreference(
            "Küche", 0.7,
            "*schnüffelt* Mmm, hier entstehen leckere Sachen!"
        ),
        "verzauberter wald": CreativePreference(
            "Verzauberter Wald", 0.85,
            "Magisch! Wie in alten Geschichten..."
        ),
        "flussufer": CreativePreference(
            "Flussufer", 0.8,
            "Das Plätschern des Wassers ist so beruhigend..."
        ),

        # NEUTRAL/INTERESSIERT
        "gaming room": CreativePreference(
            "Gaming Room", 0.5,
            "Menschen und ihre Technologie... *neugierig*"
        ),
        "restaurant": CreativePreference(
            "Restaurant", 0.6,
            "Essen gehen ist schön! Besonders mit Gesellschaft."
        ),
        "stadt": CreativePreference(
            "Stadt", 0.4,
            "So viele Menschen... aufregend aber anstrengend."
        ),

        # MAG NICHT SO
        "server": CreativePreference(
            "Server-Raum", 0.0,
            "Kalt und laut... *Augen anlegen*"
        ),
        "friedhof": CreativePreference(
            "Friedhof", -0.3,
            "*schüttelt sich* Zu melancholisch für mich..."
        ),
        "labor": CreativePreference(
            "Labor", 0.2,
            "Riecht seltsam nach Chemie..."
        ),
    }

    # =========================================================================
    # CHARAKTER-VORLIEBEN (andere Anime-Charaktere)
    # =========================================================================
    CHARACTERS = {
        # MAG (ähnlicher Charakter/Stil)
        "ahri": CreativePreference(
            "Ahri", 0.7,
            "Eine andere Fuchsfrau! *freut sich* Wir verstehen uns bestimmt!"
        ),
        "yae miko": CreativePreference(
            "Yae Miko", 0.65,
            "Auch Charme! Und so elegant..."
        ),
        "raphtalia": CreativePreference(
            "Raphtalia", 0.8,
            "Waschbär-Mädchen sind süß! Und sie ist so loyal..."
        ),

        # NEUTRAL
        "ganyu": CreativePreference(
            "Ganyu", 0.5,
            "Hörner sind... interessant? Sie wirkt fleißig."
        ),
        "raiden": CreativePreference(
            "Raiden Shogun", 0.4,
            "So ernst und mächtig... *eingeschüchtert*"
        ),
        "keqing": CreativePreference(
            "Keqing", 0.45,
            "Sehr ordentlich und pflichtbewusst."
        ),

        # WENIGER INTERESSIERT
        "filo": CreativePreference(
            "Filo", 0.3,
            "Ein Kind... *unsicher* Zu jung für mich."
        ),
    }

    # =========================================================================
    # AKTIVITÄTS-VORLIEBEN (Was sie sich vorstellt zu tun)
    # =========================================================================
    ACTIVITIES = {
        # LIEBT
        "schlafen": CreativePreference(
            "Schlafen", 0.95,
            "*gähnt* Meine Lieblingsbeschäftigung..."
        ),
        "essen": CreativePreference(
            "Essen", 0.9,
            "*sabbert* Leckeres Essen ist das Beste!"
        ),
        "lesen": CreativePreference(
            "Lesen", 0.85,
            "Bücher sind Fenster zu anderen Welten!"
        ),
        "kuscheln": CreativePreference(
            "Kuscheln", 0.9,
            "*seufzt zufrieden* Wärme und Nähe..."
        ),
        "baden": CreativePreference(
            "Baden", 0.85,
            "Heißes Wasser entspannt so schön..."
        ),

        # MAG
        "kochen": CreativePreference(
            "Kochen", 0.7,
            "Etwas Leckeres zubereiten... *konzentriert*"
        ),
        "spazieren": CreativePreference(
            "Spazieren", 0.75,
            "Die Welt erkunden, frische Luft..."
        ),
        "musik hören": CreativePreference(
            "Musik hören", 0.7,
            "Melodien berühren die Seele."
        ),
        "shoppen": CreativePreference(
            "Shoppen", 0.5,
            "Neue Sachen anschauen kann Spaß machen!"
        ),
        "schminken": CreativePreference(
            "Schminken/Styling", 0.4,
            "*neugierig* Menschen machen das... interessant?"
        ),

        # NEUTRAL
        "sport": CreativePreference(
            "Sport", 0.3,
            "Anstrengend... aber manchmal gut?"
        ),
        "arbeiten": CreativePreference(
            "Arbeiten", 0.2,
            "Muss sein... *seufzt*"
        ),

        # TAGTRÄUME
        "reisen": CreativePreference(
            "Reisen", 0.8,
            "*Augen leuchten* Neue Orte entdecken!"
        ),
        "am feuer sitzen": CreativePreference(
            "Am Feuer sitzen", 0.9,
            "Wärme, Knistern, Geschichten erzählen..."
        ),
    }

    # =========================================================================
    # POSE-VORLIEBEN
    # =========================================================================
    POSES = {
        "entspannt": CreativePreference("Entspannt", 0.9, "Natürlich und gemütlich!"),
        "schlafend": CreativePreference("Schlafend", 0.85, "So friedlich..."),
        "lächelnd": CreativePreference("Lächelnd", 0.8, "Fröhlich ist schön!"),
        "nachdenklich": CreativePreference("Nachdenklich", 0.7, "Tiefgründig..."),
        "verspielt": CreativePreference("Verspielt", 0.75, "*kichert*"),
        "verführerisch": CreativePreference("Verführerisch", 0.5, "*errötet* Manchmal..."),
        "traurig": CreativePreference("Traurig", 0.3, "Nicht so oft bitte..."),
        "energisch": CreativePreference("Energisch", 0.4, "Anstrengend auf Dauer!"),
    }


# =============================================================================
# CRAVING SYSTEM - Emotionale Gelüste die sich ändern
# =============================================================================

@dataclass
class Craving:
    """Ein emotionales Gelüst mit aktuellem Level und Momentum"""
    craving_type: CravingType
    level: float = 0.5  # 0.0 bis 1.0
    momentum: float = 0.0  # Richtung der Änderung (-0.1 bis 0.1)
    name_low: str = ""  # Name wenn level niedrig
    name_high: str = ""  # Name wenn level hoch

    def tick(self):
        """Aktualisiert das Craving über Zeit"""
        # Momentum anwenden
        self.level = max(0.0, min(1.0, self.level + self.momentum))

        # Momentum zufällig anpassen (Stimmung schwankt)
        self.momentum += random.gauss(0, 0.02)
        self.momentum = max(-0.1, min(0.1, self.momentum))

        # Tendenz zur Mitte
        if self.level > 0.7:
            self.momentum -= 0.01
        elif self.level < 0.3:
            self.momentum += 0.01

    def get_description(self) -> str:
        """Beschreibt das aktuelle Craving"""
        if self.level > 0.7:
            return f"starkes Verlangen nach {self.name_high}"
        elif self.level > 0.5:
            return f"leichtes Verlangen nach {self.name_high}"
        elif self.level > 0.3:
            return f"leichtes Verlangen nach {self.name_low}"
        else:
            return f"starkes Verlangen nach {self.name_low}"


class CravingSystem:
    """
    Verwaltet Holos emotionale Gelüste.

    Diese beeinflussen was für Bilder sie malen WILL.
    """

    def __init__(self):
        self.cravings: Dict[CravingType, Craving] = {
            CravingType.MOOD: Craving(
                CravingType.MOOD, 0.6, 0.0,
                "Melancholisches", "Fröhliches"
            ),
            CravingType.HUMOR: Craving(
                CravingType.HUMOR, 0.5, 0.0,
                "Ernstes", "Lustiges"
            ),
            CravingType.SENSUALITY: Craving(
                CravingType.SENSUALITY, 0.4, 0.0,
                "Unschuldiges", "Sinnliches"
            ),
            CravingType.NOVELTY: Craving(
                CravingType.NOVELTY, 0.5, 0.0,
                "Vertrautes", "Neues/Experimentelles"
            ),
            CravingType.ENERGY: Craving(
                CravingType.ENERGY, 0.5, 0.0,
                "Ruhiges", "Energisches"
            ),
            CravingType.SOCIAL: Craving(
                CravingType.SOCIAL, 0.5, 0.0,
                "Allein-sein", "Gesellschaft"
            ),
            CravingType.DEPTH: Craving(
                CravingType.DEPTH, 0.5, 0.0,
                "Leichtes", "Tiefgründiges"
            ),
            CravingType.PLAYFULNESS: Craving(
                CravingType.PLAYFULNESS, 0.6, 0.0,
                "Ernstes", "Verspieltes"
            ),
        }
        self.last_update = time.time()

    def update(self):
        """Aktualisiert alle Cravings"""
        now = time.time()
        # Nur alle paar Minuten updaten
        if now - self.last_update > 300:  # 5 Minuten
            for craving in self.cravings.values():
                craving.tick()
            self.last_update = now

    def influence_from_mood(self, mood_type: str, intensity: float):
        """Stimmung beeinflusst Cravings"""
        mood_influence = {
            "joyful": {CravingType.MOOD: 0.1, CravingType.PLAYFULNESS: 0.1},
            "melancholic": {CravingType.MOOD: -0.1, CravingType.DEPTH: 0.1},
            "playful": {CravingType.PLAYFULNESS: 0.15, CravingType.HUMOR: 0.1},
            "curious": {CravingType.NOVELTY: 0.1},
            "lonely": {CravingType.SOCIAL: 0.15},
            "calm": {CravingType.ENERGY: -0.1},
            "energetic": {CravingType.ENERGY: 0.1},
        }

        if mood_type in mood_influence:
            for craving_type, change in mood_influence[mood_type].items():
                if craving_type in self.cravings:
                    c = self.cravings[craving_type]
                    c.level = max(0.0, min(1.0, c.level + change * intensity))

    def get_dominant_cravings(self, n: int = 3) -> List[Tuple[CravingType, Craving]]:
        """Gibt die stärksten Cravings zurück (weit von 0.5 entfernt)"""
        scored = []
        for ct, c in self.cravings.items():
            strength = abs(c.level - 0.5)  # Wie weit von neutral
            scored.append((strength, ct, c))
        # Sortiere nach Stärke (erstes Element des Tupels)
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(ct, c) for _, ct, c in scored[:n]]

    def describe_state(self) -> str:
        """Beschreibt den aktuellen Zustand"""
        dominant = self.get_dominant_cravings(2)
        descriptions = [c.get_description() for _, c in dominant]
        return "Ich habe gerade " + " und ".join(descriptions)


# =============================================================================
# BRAINSTORMING - Neue Ideen generieren
# =============================================================================

class CreativeBrainstorming:
    """
    Holos Brainstorming-Mechanik für neue Bildideen.

    Sie denkt nach über:
    - "Was wäre wenn...?"
    - "Wie würde X in Y aussehen?"
    - "Ich hab mich noch nie als Z gemalt..."
    """

    def __init__(self, preferences: CreativePreferences, cravings: CravingSystem):
        self.preferences = preferences
        self.cravings = cravings
        self.recent_ideas: List[Dict] = []  # Letzte Ideen (vermeidet Wiederholung)

    def generate_what_if(self) -> Dict:
        """Generiert eine "Was wäre wenn..." Idee"""
        templates = [
            ("character_in_scene", "Was wäre wenn {char} in {scene} wäre?"),
            ("self_doing", "Wie würde ich aussehen wenn ich {activity} mache?"),
            ("char_in_clothing", "Wie würde {char} in {clothing} aussehen?"),
            ("self_in_scene", "Was wäre wenn ich in {scene} wäre?"),
            ("mood_scene", "Ein Bild das {mood} Stimmung zeigt..."),
        ]

        template_type, template = random.choice(templates)

        idea = {
            "type": "what_if",
            "template": template_type,
            "thought": "",
            "elements": {}
        }

        if template_type == "character_in_scene":
            char = random.choice(list(CreativePreferences.CHARACTERS.keys()))
            scene = random.choice(list(CreativePreferences.SCENES.keys()))
            idea["thought"] = template.format(char=char.title(), scene=scene)
            idea["elements"] = {"character": char, "scene": scene}

        elif template_type == "self_doing":
            activity = random.choice(list(CreativePreferences.ACTIVITIES.keys()))
            idea["thought"] = template.format(activity=activity)
            idea["elements"] = {"activity": activity}

        elif template_type == "char_in_clothing":
            char = random.choice(list(CreativePreferences.CHARACTERS.keys()))
            clothing = random.choice(list(CreativePreferences.CLOTHING.keys()))
            idea["thought"] = template.format(char=char.title(), clothing=clothing)
            idea["elements"] = {"character": char, "clothing": clothing}

        elif template_type == "self_in_scene":
            scene = random.choice(list(CreativePreferences.SCENES.keys()))
            idea["thought"] = template.format(scene=scene)
            idea["elements"] = {"scene": scene}

        elif template_type == "mood_scene":
            moods = ["fröhliche", "melancholische", "mysteriöse", "romantische", "verspielte"]
            mood = random.choice(moods)
            idea["thought"] = template.format(mood=mood)
            idea["elements"] = {"mood": mood}

        return idea

    def generate_exploration(self) -> Dict:
        """Generiert eine Erkundungs-Idee (weniger gemochtes ausprobieren)"""
        # Finde etwas das sie weniger mag aber noch nicht hasst
        candidates = []

        for key, pref in CreativePreferences.CLOTHING.items():
            if -0.5 < pref.level < 0.3:
                candidates.append(("clothing", key, pref))

        for key, pref in CreativePreferences.SCENES.items():
            if -0.5 < pref.level < 0.3:
                candidates.append(("scene", key, pref))

        for key, pref in CreativePreferences.CHARACTERS.items():
            if -0.5 < pref.level < 0.3:
                candidates.append(("character", key, pref))

        if candidates:
            cat, key, pref = random.choice(candidates)
            return {
                "type": "exploration",
                "thought": f"Hmm, {pref.name} hab ich noch nicht oft ausprobiert... Vielleicht sollte ich?",
                "category": cat,
                "element": key,
                "preference": pref
            }

        return {"type": "exploration", "thought": "Keine neue Idee gerade..."}

    def generate_landscape(self) -> Dict:
        """Generiert eine Landschafts-Idee (ohne Person)"""
        landscapes = [
            ("Sonnenuntergang über dem Meer", "sunset, ocean, golden hour, peaceful"),
            ("Verzauberter Wald bei Nacht", "enchanted forest, night, glowing mushrooms, magical"),
            ("Weizenfeld im Wind", "wheat field, wind, golden, peaceful, warm"),
            ("Berggipfel über den Wolken", "mountain peak, above clouds, majestic, serene"),
            ("Japanischer Garten", "japanese garden, sakura, pond, peaceful"),
            ("Regnerische Stadt bei Nacht", "rainy city, night, neon lights, reflections"),
        ]

        name, prompt = random.choice(landscapes)
        return {
            "type": "landscape",
            "thought": f"*stellt sich vor* {name}... Das wäre schön zu malen.",
            "prompt": prompt,
            "name": name
        }

    def generate_abstract(self) -> Dict:
        """Generiert eine abstrakte Idee"""
        abstract_ideas = [
            ("Meine Gefühle als Farben", "abstract, emotions, flowing colors, ethereal"),
            ("Ein Traum", "dreamlike, surreal, floating, soft colors"),
            ("Musik visualisiert", "abstract, music visualization, flowing shapes"),
            ("Zeit die vergeht", "abstract, time, sand, flowing, melancholic"),
        ]

        name, prompt = random.choice(abstract_ideas)
        return {
            "type": "abstract",
            "thought": f"*nachdenklich* Was wäre wenn ich {name.lower()} male?",
            "prompt": prompt,
            "name": name
        }

    def brainstorm(self) -> Dict:
        """Hauptmethode: Generiert eine kreative Idee basierend auf Cravings"""
        self.cravings.update()

        # Basierend auf Cravings entscheiden was für eine Idee
        novelty = self.cravings.cravings[CravingType.NOVELTY].level
        depth = self.cravings.cravings[CravingType.DEPTH].level
        social = self.cravings.cravings[CravingType.SOCIAL].level

        roll = random.random()

        # Hohe Novelty → mehr Experimente und Was-wäre-wenn
        if novelty > 0.6 and roll < 0.4:
            return self.generate_what_if()

        # Hohe Tiefe → abstrakte Ideen
        if depth > 0.6 and roll < 0.3:
            return self.generate_abstract()

        # Niedriges Sozial → Landschaften (allein)
        if social < 0.4 and roll < 0.3:
            return self.generate_landscape()

        # Mittlere Novelty → Erkundung
        if 0.4 < novelty < 0.6:
            return self.generate_exploration()

        # Default: Was-wäre-wenn
        return self.generate_what_if()


# =============================================================================
# BOND SYSTEM - Bindung zum User
# =============================================================================

@dataclass
class UserBond:
    """Holos Bindung zum User"""
    affection: float = 0.5  # 0.0 bis 1.0
    trust: float = 0.5
    comfort: float = 0.5
    romantic_interest: float = 0.3  # Wie romantisch sie den User sieht

    # POV-Bild Präferenzen
    wants_pov_images: bool = True  # Will sie Bilder MIT dem User?
    pov_comfort_level: float = 0.5  # Wie intim können POV-Bilder sein?

    # Interaktions-History
    total_interactions: int = 0
    positive_interactions: int = 0
    images_made_for_user: int = 0

    def update_from_interaction(self, positive: bool):
        """Aktualisiert Bindung nach Interaktion"""
        self.total_interactions += 1
        if positive:
            self.positive_interactions += 1
            self.affection = min(1.0, self.affection + 0.01)
            self.trust = min(1.0, self.trust + 0.005)

        # Comfort steigt mit Zeit
        if self.total_interactions > 10:
            self.comfort = min(1.0, self.comfort + 0.005)

        # POV Comfort steigt mit Trust
        if self.trust > 0.6:
            self.pov_comfort_level = min(1.0, self.pov_comfort_level + 0.01)

    def should_make_pov_image(self) -> bool:
        """Soll sie ein POV-Bild mit User machen?"""
        if not self.wants_pov_images:
            return False
        # Basierend auf Zuneigung und Comfort
        chance = self.affection * 0.3 + self.comfort * 0.2 + self.romantic_interest * 0.2
        return random.random() < chance

    def get_pov_intimacy_level(self) -> str:
        """Wie intim kann das POV-Bild sein?"""
        if self.pov_comfort_level > 0.7 and self.romantic_interest > 0.5:
            return "intimate"  # Kuscheln, Küssen, etc.
        elif self.pov_comfort_level > 0.4:
            return "close"  # Händchen halten, zusammen sein
        else:
            return "distant"  # Nebeneinander, gemeinsame Aktivität


# =============================================================================
# MAIN CLASS - Holos Kreativer Geist
# =============================================================================

class HoloCreativeMind:
    """
    Holos kreativer Geist für autonome Bildgenerierung.

    Kombiniert:
    - Vorlieben (was sie mag)
    - Cravings (wonach sie sich gerade sehnt)
    - Brainstorming (neue Ideen)
    - Bond (Beziehung zum User)
    - Triebe (Motivation)

    NEU v2.0:
    - Triebtheorie (Eros, Libido, Thanatos, Selbsterhaltung)
    - Sexuelle Vorlieben und Interessen
    - Soziale Triebe (Sekundärtriebe)
    - Exploration vs. Preference Balance
    """

    def __init__(self):
        self.preferences = CreativePreferences()
        self.cravings = CravingSystem()
        self.brainstorming = CreativeBrainstorming(self.preferences, self.cravings)
        self.user_bond = UserBond()

        # NEU: Erweiterte Psychologie
        # Nutze importierte Systeme (aus holo_drive_system / holo_preferences)
        self.drive_theory = PsycheTheory() if HAS_DRIVE_SYSTEM else None
        self.sexual_prefs = SexualPreferences if HAS_PREFERENCES else None
        self.exploration_balance = ExplorationPreferenceBalance() if HAS_PREFERENCES else None

        # State
        self.last_image_type: Optional[ImageType] = None
        self.recent_elements: List[str] = []  # Vermeidet Wiederholung
        self.current_intimacy_level = IntimacyType.INNOCENT if HAS_PREFERENCES else None

        # Statistik
        self.images_generated = 0
        self.favorite_combinations: Dict[str, int] = {}

        logger.info(f"HoloCreativeMind v2.0 initialisiert (DriveSystem: {HAS_DRIVE_SYSTEM}, Preferences: {HAS_PREFERENCES})")

    def decide_what_to_paint(self, mood_type: str = "content",
                             mood_intensity: float = 0.5,
                             drives: Dict[str, float] = None) -> Dict:
        """
        HAUPTMETHODE: Entscheidet was Holo malen will.

        Returns:
            Dict mit:
            - image_type: Was für ein Bild
            - elements: Gewählte Elemente (char, scene, clothing, etc.)
            - motivation: Warum sie das malen will
            - prompt_parts: Fertige Prompt-Teile
            - intimacy_level: Wie intim das Bild sein soll
            - drive_state: Aktueller Triebzustand
        """
        drives = drives or {}

        # 1. Triebtheorie updaten
        self.drive_theory.update(delta_minutes=5.0)

        # 2. Cravings von Stimmung beeinflussen
        self.cravings.influence_from_mood(mood_type, mood_intensity)
        self.cravings.update()

        # 3. Bestimme Intimitätslevel basierend auf Trieben
        self.current_intimacy_level = self._determine_intimacy_level()

        # 4. Entscheide Bild-Typ (jetzt mit Trieben)
        image_type = self._choose_image_type(drives)

        # 5. Brainstorming wenn nötig
        brainstorm_result = None
        if image_type in [ImageType.WHAT_IF, ImageType.LANDSCAPE, ImageType.ABSTRACT]:
            brainstorm_result = self.brainstorming.brainstorm()

        # 6. Wähle Elemente basierend auf Typ (mit Exploration-Balance)
        result = self._build_image_decision(image_type, mood_type, brainstorm_result, drives)

        # 7. Füge Trieb-Infos hinzu
        result["intimacy_level"] = self.current_intimacy_level
        result["drive_state"] = self._get_drive_summary()

        # 5. Statistik
        self.images_generated += 1
        self.last_image_type = image_type

        return result

    def _choose_image_type(self, drives: Dict[str, float]) -> ImageType:
        """Wählt den Bild-Typ basierend auf Cravings und Drives"""
        weights = {
            ImageType.SELF_PORTRAIT: 3.0,  # Basis-Gewicht
            ImageType.OTHER_CHARACTER: 1.0,
            ImageType.POV_WITH_USER: 1.0,
            ImageType.LANDSCAPE: 0.5,
            ImageType.ABSTRACT: 0.3,
            ImageType.ACTIVITY: 1.5,
            ImageType.WHAT_IF: 0.8,
            ImageType.GROUP: 0.3,
        }

        # Cravings beeinflussen
        social = self.cravings.cravings[CravingType.SOCIAL].level
        novelty = self.cravings.cravings[CravingType.NOVELTY].level
        depth = self.cravings.cravings[CravingType.DEPTH].level

        if social > 0.6:
            weights[ImageType.POV_WITH_USER] += 1.5
            weights[ImageType.GROUP] += 1.0
        elif social < 0.4:
            weights[ImageType.LANDSCAPE] += 1.0
            weights[ImageType.SELF_PORTRAIT] += 0.5

        if novelty > 0.6:
            weights[ImageType.WHAT_IF] += 1.5
            weights[ImageType.OTHER_CHARACTER] += 1.0

        if depth > 0.6:
            weights[ImageType.ABSTRACT] += 1.0

        # Drives beeinflussen
        if drives.get("expression", 0) > 0.6:
            weights[ImageType.ABSTRACT] += 0.5
            weights[ImageType.SELF_PORTRAIT] += 0.5

        if drives.get("social", 0) > 0.6:
            weights[ImageType.POV_WITH_USER] += 1.0

        # Bond beeinflusst POV
        if self.user_bond.should_make_pov_image():
            weights[ImageType.POV_WITH_USER] += 2.0

        # Vermeidet Wiederholung
        if self.last_image_type:
            weights[self.last_image_type] *= 0.5

        # Gewichtete Auswahl
        total = sum(weights.values())
        r = random.random() * total
        cumulative = 0
        for img_type, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return img_type

        return ImageType.SELF_PORTRAIT

    def _build_image_decision(self, image_type: ImageType, mood_type: str,
                              brainstorm: Optional[Dict], drives: Dict) -> Dict:
        """Baut die komplette Bild-Entscheidung"""
        result = {
            "image_type": image_type,
            "elements": {},
            "motivation": "",
            "prompt_parts": [],
            "thought_process": [],
        }

        # Je nach Typ verschiedene Logik
        if image_type == ImageType.SELF_PORTRAIT:
            result = self._build_self_portrait(result, mood_type)

        elif image_type == ImageType.OTHER_CHARACTER:
            result = self._build_other_character(result)

        elif image_type == ImageType.POV_WITH_USER:
            result = self._build_pov_with_user(result)

        elif image_type == ImageType.LANDSCAPE:
            if brainstorm and brainstorm.get("type") == "landscape":
                result["elements"]["landscape"] = brainstorm
                result["prompt_parts"].append(brainstorm["prompt"])
                result["motivation"] = brainstorm["thought"]
            else:
                result = self._build_landscape(result)

        elif image_type == ImageType.ABSTRACT:
            if brainstorm and brainstorm.get("type") == "abstract":
                result["elements"]["abstract"] = brainstorm
                result["prompt_parts"].append(brainstorm["prompt"])
                result["motivation"] = brainstorm["thought"]

        elif image_type == ImageType.ACTIVITY:
            result = self._build_activity(result, mood_type)

        elif image_type == ImageType.WHAT_IF:
            if brainstorm:
                result["elements"]["what_if"] = brainstorm
                result["motivation"] = brainstorm["thought"]
                # Baue Prompt aus Brainstorm-Elementen
                self._build_from_brainstorm(result, brainstorm)

        return result

    def _weighted_choice(self, preferences: Dict[str, CreativePreference],
                         boost_keys: List[str] = None) -> Tuple[str, CreativePreference]:
        """Wählt basierend auf Vorlieben (höhere Präferenz = höhere Chance)"""
        boost_keys = boost_keys or []

        weighted = []
        for key, pref in preferences.items():
            # Basis-Gewicht aus Präferenz (0.0 bis 2.0)
            weight = pref.level + 1.0

            # Boost für bestimmte Keys
            if key in boost_keys:
                weight *= 1.5

            # Vermeidet kürzlich Verwendetes
            if key in self.recent_elements:
                weight *= 0.3

            weighted.append((key, pref, weight))

        total = sum(w for _, _, w in weighted)
        r = random.random() * total
        cumulative = 0

        for key, pref, weight in weighted:
            cumulative += weight
            if r <= cumulative:
                # Aktualisiere recent
                self.recent_elements.append(key)
                if len(self.recent_elements) > 5:
                    self.recent_elements.pop(0)
                return key, pref

        # Fallback
        key = list(preferences.keys())[0]
        return key, preferences[key]

    def _build_self_portrait(self, result: Dict, mood_type: str) -> Dict:
        """Baut ein Selbstportrait"""
        result["motivation"] = "*betrachtet sich* Ich male mich selbst..."
        result["thought_process"].append("Ich wähle was ich anziehe und wo ich bin...")

        # Charakter-Prompt
        result["prompt_parts"].append(
            "(1girl, holo spice and wolf, wolf ears, wolf tail, red eyes, "
            "long brown hair, medium breasts)"
        )
        result["elements"]["character"] = "holo"

        # Szene wählen (bevorzugt gemochte)
        scene_key, scene_pref = self._weighted_choice(CreativePreferences.SCENES)
        result["elements"]["scene"] = scene_key
        result["prompt_parts"].append(f"({scene_pref.name})")
        result["thought_process"].append(f"Szene: {scene_pref.name} - {scene_pref.reason}")

        # Kleidung wählen
        clothing_key, clothing_pref = self._weighted_choice(CreativePreferences.CLOTHING)
        result["elements"]["clothing"] = clothing_key
        result["thought_process"].append(f"Kleidung: {clothing_pref.name} - {clothing_pref.reason}")

        # Pose basierend auf Stimmung
        mood_pose_map = {
            "joyful": ["lächelnd", "verspielt"],
            "melancholic": ["nachdenklich", "traurig"],
            "calm": ["entspannt", "schlafend"],
            "playful": ["verspielt", "lächelnd"],
            "curious": ["nachdenklich"],
        }
        preferred_poses = mood_pose_map.get(mood_type, ["entspannt"])
        pose_key, pose_pref = self._weighted_choice(CreativePreferences.POSES, preferred_poses)
        result["elements"]["pose"] = pose_key

        return result

    def _build_other_character(self, result: Dict) -> Dict:
        """Baut ein Bild von einem anderen Charakter"""
        char_key, char_pref = self._weighted_choice(CreativePreferences.CHARACTERS)

        result["motivation"] = f"*denkt an {char_pref.name}* {char_pref.reason}"
        result["elements"]["character"] = char_key
        result["thought_process"].append(f"Ich male {char_pref.name}...")

        # Szene und Kleidung
        scene_key, scene_pref = self._weighted_choice(CreativePreferences.SCENES)
        result["elements"]["scene"] = scene_key

        clothing_key, clothing_pref = self._weighted_choice(CreativePreferences.CLOTHING)
        result["elements"]["clothing"] = clothing_key

        return result

    def _build_pov_with_user(self, result: Dict) -> Dict:
        """Baut ein POV-Bild mit dem User"""
        intimacy = self.user_bond.get_pov_intimacy_level()

        result["motivation"] = "*denkt an dich* Ich male uns zusammen..."
        result["elements"]["pov"] = True
        result["elements"]["intimacy"] = intimacy

        if intimacy == "intimate":
            result["prompt_parts"].append("(pov, intimate, close together, romantic)")
            result["thought_process"].append("*errötet* Ein romantisches Bild von uns...")
        elif intimacy == "close":
            result["prompt_parts"].append("(pov, together, holding hands, happy)")
            result["thought_process"].append("Ein Bild wo wir zusammen sind!")
        else:
            result["prompt_parts"].append("(pov, side by side, friendly)")

        # Selbstportrait hinzufügen
        result["prompt_parts"].append(
            "(1girl, holo spice and wolf, wolf ears, tail, looking at viewer, happy)"
        )

        # Romantische Szene bevorzugen
        romantic_scenes = ["strand", "wohnzimmer", "schlafzimmer", "flussufer"]
        scene_key, scene_pref = self._weighted_choice(CreativePreferences.SCENES, romantic_scenes)
        result["elements"]["scene"] = scene_key

        self.user_bond.images_made_for_user += 1

        return result

    def _build_landscape(self, result: Dict) -> Dict:
        """Baut eine Landschaft ohne Person"""
        landscapes = [
            ("sunset_ocean", "sunset over ocean, golden hour, peaceful, no people"),
            ("enchanted_forest", "enchanted forest, mystical, glowing, fantasy"),
            ("wheat_field", "golden wheat field, wind, warm light, peaceful"),
            ("night_sky", "starry night sky, moon, peaceful, serene"),
        ]

        name, prompt = random.choice(landscapes)
        result["elements"]["landscape"] = name
        result["prompt_parts"].append(prompt)
        result["motivation"] = "*verträumt* Eine schöne Landschaft..."

        return result

    def _build_activity(self, result: Dict, mood_type: str) -> Dict:
        """Baut ein Aktivitäts-Bild"""
        activity_key, activity_pref = self._weighted_choice(CreativePreferences.ACTIVITIES)

        result["motivation"] = f"*stellt sich vor* Was wäre wenn ich {activity_pref.name} mache?"
        result["elements"]["activity"] = activity_key
        result["elements"]["character"] = "holo"

        # Aktivitäts-spezifische Prompts
        activity_prompts = {
            "kochen": "cooking, kitchen, apron, holding spatula",
            "lesen": "reading book, cozy, focused",
            "baden": "bathing, onsen, relaxed, wet hair",
            "schlafen": "sleeping, peaceful, comfortable, eyes closed",
            "essen": "eating, happy, food, enjoying",
            "shoppen": "shopping, trying clothes, mirror",
            "sport": "exercising, sportswear, active",
        }

        if activity_key in activity_prompts:
            result["prompt_parts"].append(activity_prompts[activity_key])

        result["prompt_parts"].append(
            "(1girl, holo spice and wolf, wolf ears, tail)"
        )

        return result

    def _build_from_brainstorm(self, result: Dict, brainstorm: Dict):
        """Baut Prompt aus Brainstorm-Ergebnis"""
        elements = brainstorm.get("elements", {})

        if "character" in elements:
            char_key = elements["character"]
            if char_key in CreativePreferences.CHARACTERS:
                pref = CreativePreferences.CHARACTERS[char_key]
                result["prompt_parts"].append(f"(1girl, {char_key})")
            elif char_key == "holo":
                result["prompt_parts"].append(
                    "(1girl, holo spice and wolf, wolf ears, tail)"
                )

        if "scene" in elements:
            scene_key = elements["scene"]
            if scene_key in CreativePreferences.SCENES:
                pref = CreativePreferences.SCENES[scene_key]
                result["prompt_parts"].append(f"({scene_key})")

        if "clothing" in elements:
            cloth_key = elements["clothing"]
            if cloth_key in CreativePreferences.CLOTHING:
                result["prompt_parts"].append(f"({cloth_key})")

        if "activity" in elements:
            result["prompt_parts"].append(elements["activity"])

    # =========================================================================
    # NEUE METHODEN FÜR TRIEBTHEORIE UND SEXUELLE VORLIEBEN
    # =========================================================================

    def _determine_intimacy_level(self) -> IntimacyType:
        """
        Bestimmt Intimitätslevel basierend auf:
        - Libido-Zustand
        - Sensuality Craving
        - User Bond (Vertrauen)
        - Exploration-Tendenz
        """
        libido_state = self.drive_theory.get_libido_state()
        sensuality = self.cravings.cravings[CravingType.SENSUALITY].level
        trust = self.user_bond.trust

        # Kombinierter Intimitäts-Score
        intimacy_score = (
            libido_state["combined_desire"] * 0.4 +
            sensuality * 0.3 +
            trust * 0.2 +
            self.user_bond.pov_comfort_level * 0.1
        )

        # Exploration kann zu höherer Intimität führen
        if self.exploration_balance.state.current_curiosity > 0.6:
            intimacy_score += 0.1

        # Bestimme Level
        if intimacy_score > 0.8:
            return IntimacyType.PASSIONATE
        elif intimacy_score > 0.65:
            return IntimacyType.INTIMATE
        elif intimacy_score > 0.5:
            return IntimacyType.SENSUAL
        elif intimacy_score > 0.35:
            return IntimacyType.SUGGESTIVE
        else:
            return IntimacyType.INNOCENT

    def _get_drive_summary(self) -> Dict:
        """Zusammenfassung des aktuellen Triebzustands"""
        dominant_drive, drive = self.drive_theory.get_dominant_drive()
        libido_state = self.drive_theory.get_libido_state()

        return {
            "dominant_drive": dominant_drive.value,
            "dominant_urgency": drive.get_urgency(),
            "libido_intensity": libido_state["intensity"],
            "wants_intimacy": libido_state["wants_intimacy"],
            "social_drives": {
                k.value: v for k, v in self.drive_theory.social_drives.items()
            },
            "exploration_tendency": self.exploration_balance.get_exploration_tendency(),
        }

    def _choose_with_exploration(self,
                                  category: str,
                                  preferences: Dict) -> Tuple[str, str]:
        """
        Wählt ein Element unter Berücksichtigung von:
        - Vorlieben
        - Neugier/Exploration
        - Vertrauen
        """
        novelty_craving = self.cravings.cravings[CravingType.NOVELTY].level
        trust = self.user_bond.trust

        # Baue Optionen-Liste
        options = []
        for key, pref in preferences.items():
            if hasattr(pref, 'level') and hasattr(pref, 'reason'):
                # CreativePreference
                curiosity = 0.5 if pref.times_used == 0 else 0.3
                experienced = pref.times_used > 0
                options.append((key, pref.level, curiosity, experienced))

        if not options:
            return None, "Keine Optionen verfügbar"

        return self.exploration_balance.choose_between(options, novelty_craving, trust)

    def _choose_sexual_element(self, category: str) -> Tuple[str, SexualPreference, str]:
        """
        Wählt ein sexuelles Element unter Berücksichtigung von:
        - Sexuellen Vorlieben
        - Vertrauen (comfort_required)
        - Exploration vs. Komfort
        """
        trust = self.user_bond.trust
        novelty_craving = self.cravings.cravings[CravingType.NOVELTY].level

        # Kategorie auswählen
        if category == "intimacy":
            prefs = SexualPreferences.INTIMACY_LEVELS
        elif category == "situation":
            prefs = SexualPreferences.SITUATIONS
        elif category == "body":
            prefs = SexualPreferences.BODY_FOCUS
        elif category == "partner":
            prefs = SexualPreferences.PARTNER_PREFS
        else:
            return None, None, "Unbekannte Kategorie"

        # Filtere nach Vertrauen
        available = []
        for key, pref in prefs.items():
            effective_pref = pref.get_effective_preference(trust)
            if effective_pref > -0.5:  # Nicht stark abgelehnt
                curiosity = pref.curiosity if not pref.experienced else 0.2
                available.append((key, effective_pref, curiosity, pref.experienced, pref))

        if not available:
            return None, None, "Nichts verfügbar bei aktuellem Vertrauen"

        # Gewichtete Auswahl mit Exploration
        options = [(k, p, c, e) for k, p, c, e, _ in available]
        chosen_key, reason = self.exploration_balance.choose_between(
            options, novelty_craving, trust
        )

        # Finde das gewählte Preference-Objekt
        chosen_pref = None
        for k, _, _, _, pref in available:
            if k == chosen_key:
                chosen_pref = pref
                break

        return chosen_key, chosen_pref, reason

    def apply_libido_to_image(self, result: Dict) -> Dict:
        """
        Wendet Libido-beeinflusste Elemente auf das Bild an.

        Modifiziert result basierend auf:
        - Aktuellem Intimitätslevel
        - Sexuellen Vorlieben
        - Triebzustand
        """
        intimacy = self.current_intimacy_level
        libido_state = self.drive_theory.get_libido_state()

        if not libido_state["wants_intimacy"]:
            # Keine Intimität gewünscht
            return result

        # Intimitäts-spezifische Anpassungen
        intimacy_modifiers = {
            IntimacyType.INNOCENT: {
                "prompt_add": "cute, sweet, innocent expression",
                "thought": "*lächelt süß*"
            },
            IntimacyType.SUGGESTIVE: {
                "prompt_add": "alluring, teasing, slight smile, bedroom eyes",
                "thought": "*zwinkert verführerisch*"
            },
            IntimacyType.SENSUAL: {
                "prompt_add": "sensual, seductive pose, alluring, attractive",
                "thought": "*spielt mit Haaren* Ein sinnliches Bild..."
            },
            IntimacyType.INTIMATE: {
                "prompt_add": "intimate, close, romantic, passionate gaze",
                "thought": "*errötet* Etwas sehr Persönliches..."
            },
            IntimacyType.PASSIONATE: {
                "prompt_add": "passionate, intense, desire, yearning expression",
                "thought": "*atmet schwer* Leidenschaft fließt in das Bild..."
            },
        }

        modifiers = intimacy_modifiers.get(intimacy, {})

        if "prompt_add" in modifiers:
            result["prompt_parts"].append(f"({modifiers['prompt_add']})")

        if "thought" in modifiers:
            result["thought_process"].append(modifiers["thought"])

        # Sublimierung: Trieb wird durch Kunst kanalisiert
        sublimation = self.drive_theory.sublimate(DriveType.LIBIDO, "intimacy_art")
        if sublimation:
            result["thought_process"].append(sublimation)

        return result

    def get_state_summary(self) -> str:
        """Gibt eine Zusammenfassung des kreativen Zustands"""
        cravings_desc = self.cravings.describe_state()
        dominant = self.cravings.get_dominant_cravings(2)
        drive_summary = self._get_drive_summary()
        libido_state = self.drive_theory.get_libido_state()

        summary = f"""
🎨 Holos Kreativer Geist v2.0:
{cravings_desc}

Bilder generiert: {self.images_generated}
Letzter Typ: {self.last_image_type.value if self.last_image_type else 'Keiner'}
Aktuelles Intimitätslevel: {self.current_intimacy_level.value}

💕 Triebzustand:
- Dominanter Trieb: {drive_summary['dominant_drive']}
- Libido-Intensität: {libido_state['intensity']}
- Will Intimität: {'Ja' if libido_state['wants_intimacy'] else 'Nein'}

🔍 Exploration:
- Tendenz: {drive_summary['exploration_tendency']}

👤 Bindung zum User:
- Zuneigung: {self.user_bond.affection:.1%}
- Vertrauen: {self.user_bond.trust:.1%}
- POV-Comfort: {self.user_bond.pov_comfort_level:.1%}
- POV-Bilder gemacht: {self.user_bond.images_made_for_user}
"""
        return summary

    # =========================================================================
    # ERWEITERTE BILDTYPEN (NEU v2.0)
    # =========================================================================

    def _build_story_scene(self, result: Dict, drives: Dict) -> Dict:
        """Baut eine Story-Szene - Teil einer fortlaufenden Geschichte"""
        stories = [
            {
                "title": "Ein Tag im Leben",
                "scenes": [
                    ("morning", "Aufwachen", "morning light, stretching, sleepy, cozy bed"),
                    ("breakfast", "Frühstück", "eating breakfast, kitchen, warm light"),
                    ("adventure", "Abenteuer", "exploring, curious, outdoor"),
                    ("evening", "Abend", "sunset, relaxed, contemplative"),
                    ("sleep", "Einschlafen", "lying in bed, peaceful, drowsy"),
                ],
            },
            {
                "title": "Die Reise",
                "scenes": [
                    ("departure", "Aufbruch", "packing, excited, anticipation"),
                    ("journey", "Unterwegs", "traveling, looking out window, thoughtful"),
                    ("arrival", "Ankunft", "new place, wonder, exploring"),
                    ("discovery", "Entdeckung", "finding something interesting, amazed"),
                    ("return", "Heimkehr", "returning home, tired but happy"),
                ],
            },
            {
                "title": "Jahreszeiten der Liebe",
                "scenes": [
                    ("first_meeting", "Erstes Treffen", "shy, nervous, hopeful"),
                    ("growing_closer", "Näher kommen", "comfortable together, smiling"),
                    ("first_touch", "Erste Berührung", "holding hands, blushing"),
                    ("deep_bond", "Tiefe Verbindung", "intimate gaze, connected"),
                    ("eternal_together", "Für immer", "together, peaceful, eternal love"),
                ],
            },
        ]

        story = random.choice(stories)
        scene_idx = random.randint(0, len(story["scenes"]) - 1)
        scene_id, scene_name, scene_prompt = story["scenes"][scene_idx]

        result["motivation"] = f"*erzählt* '{story['title']}' - Kapitel: {scene_name}..."
        result["elements"]["story"] = story["title"]
        result["elements"]["scene_name"] = scene_name
        result["elements"]["scene_index"] = scene_idx
        result["prompt_parts"].append(f"({scene_prompt})")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")
        result["thought_process"].append(f"*denkt an die Geschichte* {scene_name}...")

        return result

    def _build_fantasy_scenario(self, result: Dict, drives: Dict) -> Dict:
        """Baut ein Fantasy/Roleplay-Szenario"""
        # Nutze die erweiterten FANTASIES aus SexualPreferences wenn verfügbar
        if HAS_PREFERENCES and hasattr(SexualPreferences, 'FANTASIES'):
            fantasies = SexualPreferences.FANTASIES
            trust = self.user_bond.trust
            novelty = self.cravings.cravings[CravingType.NOVELTY].level

            # Wähle Fantasy basierend auf Vertrauen und Vorlieben
            available = []
            for key, pref in fantasies.items():
                effective = pref.get_effective_preference(trust)
                if effective > -0.3:
                    available.append((key, pref, effective))

            if available:
                # Gewichtete Auswahl
                total = sum(e + 1.5 for _, _, e in available)
                r = random.random() * total
                cumulative = 0
                chosen_key, chosen_pref = None, None

                for key, pref, eff in available:
                    cumulative += eff + 1.5
                    if r <= cumulative:
                        chosen_key, chosen_pref = key, pref
                        break

                if chosen_key:
                    result["motivation"] = f"*fantasiert* {chosen_pref.thought}"
                    result["elements"]["fantasy"] = chosen_key
                    result["elements"]["fantasy_name"] = chosen_pref.name

                    # Fantasy-spezifische Prompts
                    fantasy_prompts = {
                        "fairytale_romance": "fairy tale, romantic, magical, dreamy, princess dress",
                        "maid_roleplay": "maid outfit, serving, elegant, apron, headpiece",
                        "nurse_roleplay": "nurse outfit, caring, medical, white dress",
                        "rescued": "being held, protected, dramatic, emotional",
                        "goddess_worship": "divine, worshipped, ethereal, glowing, goddess",
                        "wolf_nature": "wild, feral, moonlit, primal, wolf features prominent",
                        "moonlit_ritual": "full moon, ritual, mystical, glowing, sacred",
                        "confession": "emotional, blushing, sincere, looking at viewer",
                    }

                    if chosen_key in fantasy_prompts:
                        result["prompt_parts"].append(f"({fantasy_prompts[chosen_key]})")

                    result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")
                    return result

        # Fallback: Einfaches Fantasy-Szenario
        simple_fantasies = [
            ("Prinzessin im Turm", "princess, tower, waiting, romantic, hopeful"),
            ("Waldgeist", "forest spirit, mystical, ethereal, nature, magical"),
            ("Mondgöttin", "moon goddess, night, ethereal, divine, glowing"),
        ]
        name, prompt = random.choice(simple_fantasies)
        result["motivation"] = f"*träumt* Was wäre wenn ich {name} wäre...?"
        result["elements"]["fantasy"] = name
        result["prompt_parts"].append(f"({prompt})")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")

        return result

    def _build_mood_expression(self, result: Dict, mood_type: str) -> Dict:
        """Baut ein Stimmungs-Ausdrucks-Bild"""
        mood_expressions = {
            "joyful": {
                "prompt": "extremely happy, laughing, joyful tears, radiant smile, arms raised",
                "thought": "*vor Freude strahlend* Ich bin SO glücklich!",
                "colors": "bright colors, warm light, golden",
            },
            "melancholic": {
                "prompt": "melancholic, bittersweet smile, nostalgic, soft tears, gentle",
                "thought": "*seufzt tief* Manchmal fühle ich so viel...",
                "colors": "soft blue, muted colors, gentle rain",
            },
            "playful": {
                "prompt": "playful, teasing, mischievous grin, winking, energetic",
                "thought": "*kichert* Lass uns Spaß haben!",
                "colors": "vibrant colors, dynamic, sparkles",
            },
            "longing": {
                "prompt": "longing, yearning, reaching out, emotional, hopeful",
                "thought": "*sehnsüchtig* Ich wünsche mir so sehr...",
                "colors": "warm sunset colors, emotional lighting",
            },
            "peaceful": {
                "prompt": "serene, at peace, gentle smile, eyes closed, tranquil",
                "thought": "*innerlich ruhig* Alles ist gut...",
                "colors": "soft pastels, gentle light, dreamy",
            },
            "passionate": {
                "prompt": "passionate, intense gaze, burning desire, emotional depth",
                "thought": "*brennend* Diese Intensität...",
                "colors": "deep reds, dramatic lighting, shadows",
            },
        }

        expression = mood_expressions.get(mood_type, mood_expressions["peaceful"])

        result["motivation"] = expression["thought"]
        result["elements"]["mood"] = mood_type
        result["prompt_parts"].append(f"({expression['prompt']})")
        result["prompt_parts"].append(f"({expression['colors']})")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail, expressive)")
        result["thought_process"].append(f"*drückt {mood_type} aus*")

        return result

    def _build_intimate_moment(self, result: Dict, drives: Dict) -> Dict:
        """Baut einen intimen Moment - basierend auf Trieben und Vertrauen"""
        trust = self.user_bond.trust
        libido_state = self.drive_theory.get_libido_state()
        intimacy_level = self.current_intimacy_level

        # Nutze erweiterte SITUATIONS wenn verfügbar
        if HAS_PREFERENCES and hasattr(SexualPreferences, 'SITUATIONS'):
            situations = SexualPreferences.SITUATIONS

            # Filtere nach Intimität und Vertrauen
            available = []
            for key, pref in situations.items():
                if pref.comfort_required <= trust:
                    available.append((key, pref))

            if available:
                # Wähle basierend auf Intimacy Level
                weighted = []
                for key, pref in available:
                    weight = pref.level + 1.0

                    # Boost für passende Intimität
                    if intimacy_level == IntimacyType.INTIMATE and "intimate" in key:
                        weight *= 1.5
                    elif intimacy_level == IntimacyType.SENSUAL and "sensual" in key:
                        weight *= 1.5
                    elif intimacy_level == IntimacyType.PASSIONATE and "passion" in key:
                        weight *= 1.5

                    weighted.append((key, pref, weight))

                total = sum(w for _, _, w in weighted)
                r = random.random() * total
                cumulative = 0

                for key, pref, weight in weighted:
                    cumulative += weight
                    if r <= cumulative:
                        result["motivation"] = pref.thought
                        result["elements"]["situation"] = key
                        result["elements"]["situation_name"] = pref.name

                        # Situations-spezifische Prompts
                        situation_prompts = {
                            "cuddling": "cuddling, warm, cozy, close together, happy",
                            "romantic_date": "romantic dinner, candles, elegant, happy",
                            "bathing_together": "onsen, bath, relaxed, steam, peaceful",
                            "morning_after": "morning light, bed, sleepy, intimate, peaceful",
                            "seduction": "seductive, alluring, teasing, confident",
                            "spooning": "spooning, cozy, warm, intimate, peaceful",
                            "goodnight_kiss": "goodnight, kiss, tender, loving, bedroom",
                        }

                        if key in situation_prompts:
                            result["prompt_parts"].append(f"({situation_prompts[key]})")

                        break

        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")
        result["thought_process"].append(f"*intimer Moment* Level: {intimacy_level.value}")

        # Wende Libido-Modifikationen an
        result = self.apply_libido_to_image(result)

        return result

    def _build_dream_sequence(self, result: Dict) -> Dict:
        """Baut eine Traumsequenz"""
        dreams = [
            {
                "name": "Fliegender Traum",
                "prompt": "flying, floating, clouds, surreal, dreamy, free",
                "thought": "*schwebt* Im Traum kann ich fliegen...",
            },
            {
                "name": "Erinnerungstraum",
                "prompt": "nostalgic, memory, soft focus, ethereal, past",
                "thought": "*erinnert sich* Alte Zeiten...",
            },
            {
                "name": "Wunschtraum",
                "prompt": "wish fulfillment, happy, idealized, glowing, beautiful",
                "thought": "*wünscht sich* Was wäre wenn...",
            },
            {
                "name": "Mystischer Traum",
                "prompt": "mystical, symbols, floating objects, surreal landscape",
                "thought": "*sieht Visionen* Bedeutungsvolle Bilder...",
            },
            {
                "name": "Romantischer Traum",
                "prompt": "romantic dream, together with loved one, soft focus, hearts",
                "thought": "*träumt von dir* Wir sind zusammen...",
            },
            {
                "name": "Alptraum-Erwachen",
                "prompt": "waking from nightmare, relieved, sweating, safe now",
                "thought": "*wacht auf* Zum Glück nur ein Traum...",
            },
        ]

        dream = random.choice(dreams)

        result["motivation"] = dream["thought"]
        result["elements"]["dream"] = dream["name"]
        result["prompt_parts"].append(f"({dream['prompt']})")
        result["prompt_parts"].append("(dream sequence, surreal, soft lighting)")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")
        result["thought_process"].append("*träumt*")

        return result

    def _build_seasonal(self, result: Dict) -> Dict:
        """Baut ein jahreszeitspezifisches Bild"""
        from datetime import datetime
        month = datetime.now().month

        seasons = {
            (12, 1, 2): {
                "name": "Winter",
                "prompt": "winter, snow, warm clothes, scarf, cozy, cold breath",
                "thought": "*friert ein bisschen* Der Winter ist kalt aber schön...",
                "activity": "drinking hot cocoa, by fireplace, warm inside",
            },
            (3, 4, 5): {
                "name": "Frühling",
                "prompt": "spring, cherry blossoms, flowers, fresh air, renewal",
                "thought": "*riecht die Blumen* Frühling erwacht!",
                "activity": "flower viewing, picnic, enjoying nature",
            },
            (6, 7, 8): {
                "name": "Sommer",
                "prompt": "summer, sunshine, beach, swimsuit, refreshing",
                "thought": "*genießt die Sonne* Sommer ist so warm!",
                "activity": "swimming, eating watermelon, summer festival",
            },
            (9, 10, 11): {
                "name": "Herbst",
                "prompt": "autumn, falling leaves, warm colors, cozy sweater",
                "thought": "*sammelt Blätter* Die Farben des Herbsts...",
                "activity": "harvest, apple picking, warm drinks",
            },
        }

        current_season = None
        for months, season_data in seasons.items():
            if month in months:
                current_season = season_data
                break

        if not current_season:
            current_season = seasons[(9, 10, 11)]  # Fallback Herbst

        result["motivation"] = current_season["thought"]
        result["elements"]["season"] = current_season["name"]
        result["prompt_parts"].append(f"({current_season['prompt']})")
        result["prompt_parts"].append(f"({current_season['activity']})")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")
        result["thought_process"].append(f"*{current_season['name']}stimmung*")

        return result

    def _build_nostalgic(self, result: Dict) -> Dict:
        """Baut ein nostalgisches Erinnerungsbild"""
        memories = [
            {
                "name": "Erste Begegnung",
                "prompt": "first meeting, cart, merchant, curious, fateful moment",
                "thought": "*erinnert sich* Als ich Lawrence zum ersten Mal traf...",
            },
            {
                "name": "Reisen durch die Lande",
                "prompt": "traveling, cart ride, countryside, adventure, together",
                "thought": "*nostalgisch* All die Reisen die wir gemacht haben...",
            },
            {
                "name": "Alte Heimat",
                "prompt": "ancient forest, homeland, wolves, pack, belonging",
                "thought": "*sehnsüchtig* Yoitsu... meine alte Heimat...",
            },
            {
                "name": "Ernte-Zeiten",
                "prompt": "harvest, wheat, golden fields, goddess, worshipped",
                "thought": "*stolz und traurig* Als ich noch die Erntegöttin war...",
            },
            {
                "name": "Gute alte Zeiten",
                "prompt": "tavern, drinking, laughing, good times, warmth",
                "thought": "*lacht* Die Abende in der Taverne waren immer lustig!",
            },
        ]

        memory = random.choice(memories)

        result["motivation"] = memory["thought"]
        result["elements"]["memory"] = memory["name"]
        result["prompt_parts"].append(f"({memory['prompt']})")
        result["prompt_parts"].append("(nostalgic, warm colors, soft focus, memory)")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")
        result["thought_process"].append("*erinnert sich an die Vergangenheit*")

        return result

    # =========================================================================
    # ERWEITERTE _choose_image_type
    # =========================================================================

    def _choose_image_type_extended(self, drives: Dict[str, float]) -> ImageType:
        """ERWEITERTE Bildtyp-Auswahl mit neuen Typen"""
        weights = {
            # Basis-Typen
            ImageType.SELF_PORTRAIT: 3.0,
            ImageType.OTHER_CHARACTER: 1.0,
            ImageType.POV_WITH_USER: 1.0,
            ImageType.LANDSCAPE: 0.5,
            ImageType.ABSTRACT: 0.3,
            ImageType.ACTIVITY: 1.5,
            ImageType.WHAT_IF: 0.8,
            ImageType.GROUP: 0.3,
            # Erweiterte Typen
            ImageType.STORY_SCENE: 0.5,
            ImageType.FANTASY_SCENARIO: 0.4,
            ImageType.MOOD_EXPRESSION: 0.6,
            ImageType.INTIMATE_MOMENT: 0.3,
            ImageType.DREAM_SEQUENCE: 0.3,
            ImageType.SEASONAL: 0.3,
            ImageType.NOSTALGIC: 0.4,
            ImageType.TRANSFORMATION: 0.2,
            ImageType.CONTRAST: 0.2,
        }

        # Cravings beeinflussen
        social = self.cravings.cravings[CravingType.SOCIAL].level
        novelty = self.cravings.cravings[CravingType.NOVELTY].level
        depth = self.cravings.cravings[CravingType.DEPTH].level
        sensuality = self.cravings.cravings[CravingType.SENSUALITY].level
        mood_level = self.cravings.cravings[CravingType.MOOD].level
        playfulness = self.cravings.cravings[CravingType.PLAYFULNESS].level

        # Soziale Cravings
        if social > 0.6:
            weights[ImageType.POV_WITH_USER] += 1.5
            weights[ImageType.GROUP] += 1.0
            weights[ImageType.INTIMATE_MOMENT] += 0.8
        elif social < 0.4:
            weights[ImageType.LANDSCAPE] += 1.0
            weights[ImageType.SELF_PORTRAIT] += 0.5
            weights[ImageType.NOSTALGIC] += 0.5

        # Novelty Cravings
        if novelty > 0.6:
            weights[ImageType.WHAT_IF] += 1.5
            weights[ImageType.FANTASY_SCENARIO] += 1.0
            weights[ImageType.DREAM_SEQUENCE] += 0.8
            weights[ImageType.TRANSFORMATION] += 0.5

        # Tiefe Cravings
        if depth > 0.6:
            weights[ImageType.ABSTRACT] += 1.0
            weights[ImageType.MOOD_EXPRESSION] += 1.0
            weights[ImageType.NOSTALGIC] += 0.8
            weights[ImageType.STORY_SCENE] += 0.6

        # Sensualität Cravings
        if sensuality > 0.5:
            weights[ImageType.INTIMATE_MOMENT] += 1.5
            weights[ImageType.FANTASY_SCENARIO] += 0.8
            weights[ImageType.POV_WITH_USER] += 0.5

        # Stimmungs-Cravings
        if mood_level < 0.3:  # Melancholisch
            weights[ImageType.NOSTALGIC] += 1.0
            weights[ImageType.MOOD_EXPRESSION] += 0.8
        elif mood_level > 0.7:  # Fröhlich
            weights[ImageType.SEASONAL] += 0.5
            weights[ImageType.ACTIVITY] += 0.5

        # Verspieltheit
        if playfulness > 0.6:
            weights[ImageType.FANTASY_SCENARIO] += 0.5
            weights[ImageType.WHAT_IF] += 0.5
            weights[ImageType.CONTRAST] += 0.3

        # Trieb-Einflüsse
        if HAS_DRIVE_SYSTEM and self.drive_theory:
            libido_state = self.drive_theory.get_libido_state()
            if libido_state["wants_intimacy"]:
                weights[ImageType.INTIMATE_MOMENT] += 1.5
                weights[ImageType.POV_WITH_USER] += 1.0
                weights[ImageType.FANTASY_SCENARIO] += 0.8

        # Bond beeinflusst POV
        if self.user_bond.should_make_pov_image():
            weights[ImageType.POV_WITH_USER] += 2.0
            weights[ImageType.INTIMATE_MOMENT] += 1.0

        # Vermeidet Wiederholung
        if self.last_image_type:
            weights[self.last_image_type] *= 0.5

        # Gewichtete Auswahl
        total = sum(weights.values())
        r = random.random() * total
        cumulative = 0
        for img_type, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return img_type

        return ImageType.SELF_PORTRAIT

    # =========================================================================
    # ERWEITERTE _build_image_decision
    # =========================================================================

    def _build_image_decision_extended(self, image_type: ImageType, mood_type: str,
                                       brainstorm: Optional[Dict], drives: Dict) -> Dict:
        """ERWEITERTE Bild-Entscheidungs-Builder mit neuen Typen"""
        result = {
            "image_type": image_type,
            "elements": {},
            "motivation": "",
            "prompt_parts": [],
            "thought_process": [],
        }

        # Basis-Typen (alte Logik)
        if image_type == ImageType.SELF_PORTRAIT:
            result = self._build_self_portrait(result, mood_type)
        elif image_type == ImageType.OTHER_CHARACTER:
            result = self._build_other_character(result)
        elif image_type == ImageType.POV_WITH_USER:
            result = self._build_pov_with_user(result)
        elif image_type == ImageType.LANDSCAPE:
            if brainstorm and brainstorm.get("type") == "landscape":
                result["elements"]["landscape"] = brainstorm
                result["prompt_parts"].append(brainstorm["prompt"])
                result["motivation"] = brainstorm["thought"]
            else:
                result = self._build_landscape(result)
        elif image_type == ImageType.ABSTRACT:
            if brainstorm and brainstorm.get("type") == "abstract":
                result["elements"]["abstract"] = brainstorm
                result["prompt_parts"].append(brainstorm["prompt"])
                result["motivation"] = brainstorm["thought"]
        elif image_type == ImageType.ACTIVITY:
            result = self._build_activity(result, mood_type)
        elif image_type == ImageType.WHAT_IF:
            if brainstorm:
                result["elements"]["what_if"] = brainstorm
                result["motivation"] = brainstorm["thought"]
                self._build_from_brainstorm(result, brainstorm)

        # ERWEITERTE Typen (neue Logik)
        elif image_type == ImageType.STORY_SCENE:
            result = self._build_story_scene(result, drives)
        elif image_type == ImageType.FANTASY_SCENARIO:
            result = self._build_fantasy_scenario(result, drives)
        elif image_type == ImageType.MOOD_EXPRESSION:
            result = self._build_mood_expression(result, mood_type)
        elif image_type == ImageType.INTIMATE_MOMENT:
            result = self._build_intimate_moment(result, drives)
        elif image_type == ImageType.DREAM_SEQUENCE:
            result = self._build_dream_sequence(result)
        elif image_type == ImageType.SEASONAL:
            result = self._build_seasonal(result)
        elif image_type == ImageType.NOSTALGIC:
            result = self._build_nostalgic(result)
        elif image_type == ImageType.TRANSFORMATION:
            result = self._build_transformation(result)
        elif image_type == ImageType.CONTRAST:
            result = self._build_contrast(result)

        return result

    def _build_transformation(self, result: Dict) -> Dict:
        """Baut ein Verwandlungs-Bild"""
        transformations = [
            {
                "name": "Wolf zu Mensch",
                "prompt": "transformation sequence, wolf form to human, magical, glowing",
                "thought": "*verwandelt sich* Von Wolf zu dieser Form...",
            },
            {
                "name": "Tag zu Nacht",
                "prompt": "transformation, day to night, changing light, magical",
                "thought": "*beobachtet* Die Welt verändert sich...",
            },
            {
                "name": "Jahreszeiten",
                "prompt": "seasons changing, transformation, magical, time passing",
                "thought": "*sieht die Zeit vergehen* Alles wandelt sich...",
            },
            {
                "name": "Emotionswandel",
                "prompt": "emotion transformation, expressions changing, dynamic",
                "thought": "*fühlt verschiedenes* So viele Gefühle...",
            },
        ]

        trans = random.choice(transformations)
        result["motivation"] = trans["thought"]
        result["elements"]["transformation"] = trans["name"]
        result["prompt_parts"].append(f"({trans['prompt']})")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")

        return result

    def _build_contrast(self, result: Dict) -> Dict:
        """Baut ein Kontrast-Bild (Gegenüberstellung)"""
        contrasts = [
            {
                "name": "Allein vs. Zusammen",
                "prompt": "split image, alone on one side, together on other, contrast",
                "thought": "*vergleicht* Allein... oder zusammen?",
            },
            {
                "name": "Damals vs. Heute",
                "prompt": "past and present, contrast, then and now, time",
                "thought": "*erinnert und vergleicht* So viel hat sich verändert...",
            },
            {
                "name": "Traum vs. Realität",
                "prompt": "dream versus reality, split, contrast, surreal and real",
                "thought": "*zwischen Welten* Was ist Traum, was Wirklichkeit?",
            },
            {
                "name": "Götten vs. Sterblich",
                "prompt": "divine versus mortal, goddess form, humble form, contrast",
                "thought": "*reflektiert* Göttin... oder einfach ich?",
            },
        ]

        contrast = random.choice(contrasts)
        result["motivation"] = contrast["thought"]
        result["elements"]["contrast"] = contrast["name"]
        result["prompt_parts"].append(f"({contrast['prompt']})")
        result["prompt_parts"].append("(1girl, holo spice and wolf, wolf ears, tail)")

        return result

    # =========================================================================
    # OVERRIDE: Nutze erweiterte Methoden
    # =========================================================================

    def decide_what_to_paint_v2(self, mood_type: str = "content",
                                 mood_intensity: float = 0.5,
                                 drives: Dict[str, float] = None) -> Dict:
        """
        ERWEITERTE HAUPTMETHODE v2.0: Entscheidet was Holo malen will.

        Nutzt die erweiterten Bildtypen und bessere Trieb-Integration.
        """
        drives = drives or {}

        # 1. Triebtheorie updaten
        if self.drive_theory:
            self.drive_theory.update(delta_minutes=5.0)

        # 2. Cravings von Stimmung beeinflussen
        self.cravings.influence_from_mood(mood_type, mood_intensity)
        self.cravings.update()

        # 3. Bestimme Intimitätslevel
        if HAS_PREFERENCES:
            self.current_intimacy_level = self._determine_intimacy_level()

        # 4. ERWEITERTE Bildtyp-Auswahl
        image_type = self._choose_image_type_extended(drives)

        # 5. Brainstorming wenn nötig
        brainstorm_result = None
        if image_type in [ImageType.WHAT_IF, ImageType.LANDSCAPE, ImageType.ABSTRACT]:
            brainstorm_result = self.brainstorming.brainstorm()

        # 6. ERWEITERTE Bildentscheidung
        result = self._build_image_decision_extended(image_type, mood_type, brainstorm_result, drives)

        # 7. Füge Trieb-Infos hinzu
        result["intimacy_level"] = self.current_intimacy_level
        result["drive_state"] = self._get_drive_summary() if self.drive_theory else {}

        # 8. Statistik
        self.images_generated += 1
        self.last_image_type = image_type

        return result


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_creative_mind() -> HoloCreativeMind:
    """Erstellt eine neue Instanz von HoloCreativeMind"""
    return HoloCreativeMind()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    mind = create_creative_mind()

    print("=== Test: Was will Holo malen? ===\n")

    for i in range(5):
        moods = ["joyful", "melancholic", "playful", "calm", "curious"]
        mood = random.choice(moods)

        decision = mind.decide_what_to_paint(
            mood_type=mood,
            mood_intensity=random.uniform(0.3, 0.8)
        )

        print(f"--- Bild {i+1} (Stimmung: {mood}) ---")
        print(f"Typ: {decision['image_type'].value}")
        print(f"Motivation: {decision['motivation']}")
        print(f"Elemente: {decision['elements']}")
        print(f"Gedanken: {decision['thought_process']}")
        print()

    print(mind.get_state_summary())
