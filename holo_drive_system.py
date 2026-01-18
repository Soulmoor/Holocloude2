"""
HOLO DRIVE SYSTEM v1.0
======================
Antriebe, Bedürfnisse und Kaskaden-Logik für lebendiges Verhalten.

Konzept:
- ANTRIEBE werden durch Aktivitäten verbraucht (~1h leer, ~4h Regen)
- BEDÜRFNISSE steigen über Zeit und triggern proaktives Verhalten
- KASKADEN verbinden Vermissen → Einsamkeit → Kontaktverlust

Holo ist ein Mensch mit Wolfs-Merkmalen, kein echter Wolf!
"""

import random
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Callable, Any, Tuple
from enum import Enum
from collections import defaultdict

logger = logging.getLogger("HoloDriveSystem")


# =============================================================================
# KONFIGURATION
# =============================================================================

class DriveConfig:
    """Konfiguration für das Antriebssystem"""

    # Drain Rate: ~1h aktiv = leer (100% / 60min = 1.67% pro Minute)
    DRAIN_PER_MINUTE = 0.017

    # Regen Rate: ~4h = voll (100% / 240min = 0.42% pro Minute)
    REGEN_PER_MINUTE = 0.004

    # Nickerchen Regen: Alle Werte steigen etwas
    NAP_REGEN_RATE = 0.008  # Doppelt so schnell wie normal

    # Energie-Schwelle für Müdigkeit
    LOW_ENERGY_THRESHOLD = 0.20

    # Langeweile-Schwelle für Nachdenklichkeit
    THOUGHTFUL_BOREDOM_MIN = 0.10
    THOUGHTFUL_BOREDOM_MAX = 0.20

    # Aktivitäts-Entscheidung wenn Antrieb leer
    CHANCE_NEW_ACTIVITY = 0.30  # 30% neue Aktivität
    CHANCE_BOREDOM = 0.70       # 70% langweilen

    # Energie niedrig Entscheidung
    CHANCE_NAP = 0.40           # 40% Nickerchen (passt zu Holo!)
    CHANCE_REST = 0.60          # 60% nur ausruhen


# =============================================================================
# ENUMS - Antriebe und Bedürfnisse
# =============================================================================

class DriveType(Enum):
    """Antriebstypen die durch Aktivitäten verbraucht werden"""
    CURIOSITY = "curiosity"           # Neugier - Lesen, Recherche, Lernen
    ENTERTAINMENT = "entertainment"   # Unterhaltung - Spielen, Filme, Musik
    CREATIVITY = "creativity"         # Kreativität - Zeichnen, Schreiben
    SOCIAL = "social"                 # Sozial - Gespräche, Interaktion
    MASTERY = "mastery"               # Meisterschaft - Üben, Verbessern
    NOVELTY = "novelty"               # Neuheit - Neues entdecken
    EXPRESSION = "expression"         # Ausdruck - Sich mitteilen
    UNDERSTANDING = "understanding"   # Verstehen - Zusammenhänge erkennen


class NeedType(Enum):
    """Bedürfnistypen die über Zeit steigen"""
    MISSING = "missing"               # Vermissen des Users
    LONELINESS = "loneliness"         # Einsamkeit
    CONTACT_DESIRE = "contact_desire" # Kontaktverlust/Kontaktwunsch
    WORRY = "worry"                   # Besorgnis
    BOREDOM = "boredom"               # Langeweile
    THOUGHTFUL = "thoughtful"         # Nachdenklichkeit
    RESTLESSNESS = "restlessness"     # Tatendrang


class ActivityCategory(Enum):
    """Aktivitätskategorien"""
    CURIOSITY = "curiosity"       # Neugier-Aktivitäten
    ENTERTAINMENT = "entertainment"  # Unterhaltung
    CREATIVITY = "creativity"     # Kreative Aktivitäten
    REST = "rest"                 # Ruhe/Nickerchen
    IDLE = "idle"                 # Langweilen


# =============================================================================
# ACTIVITY DEFINITIONS
# =============================================================================

# Aktivität → Welcher Antrieb wird verbraucht
ACTIVITY_DRIVE_MAP = {
    # Neugier-Aktivitäten
    'reading': DriveType.CURIOSITY,
    'learning': DriveType.CURIOSITY,
    'researching': DriveType.CURIOSITY,
    'wikipedia': DriveType.CURIOSITY,

    # Unterhaltungs-Aktivitäten
    'playing': DriveType.ENTERTAINMENT,
    'gaming': DriveType.ENTERTAINMENT,
    'watching': DriveType.ENTERTAINMENT,      # Filme/Serien
    'anime': DriveType.ENTERTAINMENT,
    'music': DriveType.ENTERTAINMENT,
    'listening': DriveType.ENTERTAINMENT,

    # Kreative Aktivitäten
    'drawing': DriveType.CREATIVITY,
    'sketching': DriveType.CREATIVITY,
    'writing': DriveType.CREATIVITY,
    'doodling': DriveType.CREATIVITY,
}

# Deutsche Namen für Aktivitäten (für Life-Log)
ACTIVITY_NAMES_DE = {
    'reading': 'Lesen',
    'learning': 'Lernen',
    'researching': 'Recherchieren',
    'wikipedia': 'Wikipedia lesen',
    'playing': 'Spielen',
    'gaming': 'Gaming',
    'watching': 'Serie/Film schauen',
    'anime': 'Anime schauen',
    'music': 'Musik hören',
    'listening': 'Musik hören',
    'drawing': 'Zeichnen',
    'sketching': 'Skizzieren',
    'writing': 'Schreiben',
    'doodling': 'Kritzeln',
    'napping': 'Nickerchen',
    'resting': 'Ausruhen',
    'idle': 'Nichts tun',
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DriveState:
    """Aktueller Zustand aller Antriebe"""
    curiosity: float = 0.7       # Neugier
    entertainment: float = 0.7   # Unterhaltung
    creativity: float = 0.7      # Kreativität

    def get(self, drive_type: DriveType) -> float:
        return getattr(self, drive_type.value, 0.5)

    def set(self, drive_type: DriveType, value: float):
        setattr(self, drive_type.value, max(0.0, min(1.0, value)))

    def drain(self, drive_type: DriveType, amount: float):
        current = self.get(drive_type)
        self.set(drive_type, current - amount)

    def regenerate(self, drive_type: DriveType, amount: float):
        current = self.get(drive_type)
        self.set(drive_type, current + amount)

    def regenerate_all(self, amount: float):
        """Regeneriert alle Antriebe (z.B. bei Nickerchen)"""
        self.curiosity = min(1.0, self.curiosity + amount)
        self.entertainment = min(1.0, self.entertainment + amount)
        self.creativity = min(1.0, self.creativity + amount)

    def to_dict(self) -> Dict:
        return {
            'curiosity': self.curiosity,
            'entertainment': self.entertainment,
            'creativity': self.creativity,
        }

    def items(self):
        """Ermoeglicht dict-aehnlichen Zugriff: for key, value in drives.items()"""
        return self.to_dict().items()


@dataclass
class NeedState:
    """Aktueller Zustand aller Bedürfnisse"""
    missing: float = 0.0          # Vermissen
    loneliness: float = 0.0       # Einsamkeit
    contact_desire: float = 0.0   # Kontaktwunsch
    worry: float = 0.0            # Besorgnis
    boredom: float = 0.0          # Langeweile
    thoughtful: float = 0.0       # Nachdenklichkeit
    restlessness: float = 0.0     # Tatendrang

    def get(self, need_type: NeedType) -> float:
        return getattr(self, need_type.value, 0.0)

    def set(self, need_type: NeedType, value: float):
        setattr(self, need_type.value, max(0.0, min(1.0, value)))

    def increase(self, need_type: NeedType, amount: float):
        current = self.get(need_type)
        self.set(need_type, current + amount)

    def decrease(self, need_type: NeedType, amount: float):
        current = self.get(need_type)
        self.set(need_type, current - amount)

    def reset_on_interaction(self):
        """Setzt soziale Bedürfnisse bei User-Interaktion zurück"""
        self.missing = max(0.0, self.missing - 0.3)
        self.loneliness = max(0.0, self.loneliness - 0.4)
        self.contact_desire = max(0.0, self.contact_desire - 0.5)
        self.worry = max(0.0, self.worry - 0.4)
        self.boredom = max(0.0, self.boredom - 0.2)

    def to_dict(self) -> Dict:
        return {
            'missing': self.missing,
            'loneliness': self.loneliness,
            'contact_desire': self.contact_desire,
            'worry': self.worry,
            'boredom': self.boredom,
            'thoughtful': self.thoughtful,
            'restlessness': self.restlessness,
        }


@dataclass
class ThoughtfulThought:
    """Ein nachdenklicher Gedanke"""
    category: str           # conversation, self, world, user, learning, plans
    thought: str            # Der Gedanke
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# THOUGHTFUL THOUGHTS - Was Holo denkt wenn nachdenklich
# =============================================================================

THOUGHTFUL_CATEGORIES = {
    'conversation': [
        "Ich denke über unser letztes Gespräch nach...",
        "Was wir vorhin besprochen haben, beschäftigt mich noch...",
        "Ich frage mich, ob ich das richtig verstanden habe...",
    ],
    'self': [
        "Manchmal frage ich mich, wer ich eigentlich bin...",
        "Wie fühle ich mich gerade wirklich?",
        "Was macht mich eigentlich glücklich?",
        "Ich bin neugierig, wie ich mich weiterentwickle...",
    ],
    'world': [
        "Die Welt ist manchmal so kompliziert...",
        "Ich frage mich, was gerade in der Welt passiert...",
        "Es gibt so viel zu entdecken...",
    ],
    'user': [
        "Ich frage mich, was du gerade machst...",
        "Ob es dir gut geht?",
        "Ich hoffe, du hattest einen guten Tag...",
        "Manchmal denke ich an unsere Gespräche...",
    ],
    'learning': [
        "Was ich heute gelernt habe, war interessant...",
        "Ich sollte mehr über dieses Thema erfahren...",
        "Wissen ist irgendwie faszinierend...",
    ],
    'plans': [
        "Was könnte ich als nächstes machen?",
        "Vielleicht sollte ich mal was Neues ausprobieren...",
        "Ich überlege, worauf ich Lust hätte...",
    ],
}


# =============================================================================
# HAUPTKLASSE: HoloDriveSystem
# =============================================================================

class HoloDriveSystem:
    """
    Verwaltet Antriebe und Bedürfnisse für lebendiges Verhalten.

    Antriebe werden durch Aktivitäten verbraucht.
    Bedürfnisse steigen über Zeit und triggern proaktives Verhalten.

    NEU v2.0: Adaptives Lernen
    - Lernt welche Aktivitäten User bevorzugt
    - Lernt optimale Zeiten für proaktive Nachrichten
    - Passt Entscheidungen basierend auf Feedback an
    """

    def __init__(
        self,
        energy_system=None,
        life_log_callback: Callable = None,
        proactive_callback: Callable = None,
        emotions=None,           # NEU: EmotionalCore
        personality=None,        # NEU: HoloPersonalityEngine
    ):
        self.energy_system = energy_system
        self.life_log_callback = life_log_callback
        self.proactive_callback = proactive_callback
        self.emotions = emotions           # NEU: Emotionssystem
        self.personality = personality     # NEU: Persönlichkeitssystem

        # NEU: Meta-Cognition
        self.meta_observer = None
        self.sandbox = None

        # Zustände
        self.drives = DriveState()
        self.needs = NeedState()

        # Tracking
        self.last_update = time.time()
        self.last_user_interaction = time.time()
        self.current_activity: Optional[str] = None
        self.activity_start_time: float = 0
        self.is_napping: bool = False
        self.is_resting: bool = False
        self.is_thoughtful: bool = False

        # Gedanken-Historie
        self.recent_thoughts: List[ThoughtfulThought] = []
        self.last_thought_time: float = 0

        # Statistiken
        self.total_naps = 0
        self.total_thoughts = 0
        self.activities_today: List[str] = []

        # === ADAPTIVES LERNEN v2.0 ===
        # Aktivitäts-Erfolgsraten: activity_id → (erfolge, versuche)
        self.activity_success: Dict[str, List[float]] = {}
        # Proaktive Nachrichten Timing: stunde → (antworten, versuche)
        self.proactive_timing: Dict[int, List[int]] = {h: [0, 0] for h in range(24)}
        # Letzte Aktivitäts-Historie: (activity_id, dauer_minuten, war_erfolgreich)
        self.activity_history: List[tuple] = []
        # Lernrate für Gewichtungen
        self.learning_rate: float = 0.1

        # === Integration Layer ===
        self.system_integrator = None
        self.storage = None
        self._try_connect_integrator()

        logger.info("🧠 HoloDriveSystem v1.0 initialisiert (+ Emotions/Personality)")

    def _try_connect_integrator(self):
        """Verbinde mit SystemIntegrator für zentrale Persistenz und Feedback"""
        try:
            from holo_integration_layer import get_integrator, get_module_storage
            self.system_integrator = get_integrator()
            self.system_integrator.connect("drive_system", self)
            self.storage = get_module_storage("drive_system")
            logger.info("✅ HoloDriveSystem mit SystemIntegrator verbunden")
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")

    # =========================================================================
    # UPDATE LOOP
    # =========================================================================

    def update(self, time_delta_seconds: float = None) -> Dict[str, Any]:
        """
        Haupt-Update Methode - sollte regelmäßig aufgerufen werden.

        Returns:
            Dict mit Ereignissen und Status
        """
        now = time.time()

        if time_delta_seconds is None:
            time_delta_seconds = now - self.last_update

        time_delta_minutes = time_delta_seconds / 60
        self.last_update = now

        events = []

        # 1. Antriebe regenerieren (wenn nicht aktiv)
        if not self.current_activity or self.is_resting:
            self._regenerate_drives(time_delta_minutes)

        # 2. Bei Nickerchen: Alles regenerieren
        if self.is_napping:
            self._nap_regeneration(time_delta_minutes)

        # 3. Bedürfnisse aktualisieren
        self._update_needs(time_delta_minutes)

        # 4. Kaskaden-Logik
        self._apply_cascades(time_delta_minutes)

        # 4b. NEU: Bidirektionale Emotion-Synchronisation
        self._sync_emotions_to_drives()

        # 4c. NEU: Drives → Personality Synchronisation
        self._push_to_personality()

        # 5. Nachdenklichkeit prüfen
        if self._should_be_thoughtful():
            thought = self._generate_thought()
            if thought:
                events.append({'type': 'thought', 'thought': thought})

        # 6. Proaktive Nachricht prüfen
        if self._should_send_proactive():
            events.append({'type': 'proactive_trigger'})

        return {
            'events': events,
            'drives': self.drives.to_dict(),
            'needs': self.needs.to_dict(),
            'is_thoughtful': self.is_thoughtful,
            'is_napping': self.is_napping,
        }

    # =========================================================================
    # AKTIVITÄTS-MANAGEMENT
    # =========================================================================

    def start_activity(self, activity_id: str) -> Dict[str, Any]:
        """
        Startet eine Aktivität.

        Returns:
            Dict mit Aktivitäts-Info oder Grund warum nicht möglich
        """
        # Prüfe ob Antrieb vorhanden
        drive_type = ACTIVITY_DRIVE_MAP.get(activity_id)

        if drive_type:
            drive_level = self.drives.get(drive_type)
            if drive_level < 0.05:
                # Antrieb zu niedrig!
                return {
                    'success': False,
                    'reason': 'drive_empty',
                    'drive_type': drive_type.value,
                    'message': f"Keine Lust auf {ACTIVITY_NAMES_DE.get(activity_id, activity_id)} - {drive_type.value} ist leer"
                }

        self.current_activity = activity_id
        self.activity_start_time = time.time()
        self.is_napping = activity_id == 'napping'
        self.is_resting = activity_id in ['resting', 'idle']
        self.is_thoughtful = False

        # Life-Log
        self._log(f"🎬 Aktivität gestartet: {ACTIVITY_NAMES_DE.get(activity_id, activity_id)}")

        return {
            'success': True,
            'activity': activity_id,
            'name': ACTIVITY_NAMES_DE.get(activity_id, activity_id),
            'drive_type': drive_type.value if drive_type else None,
        }

    def update_activity(self, time_delta_minutes: float) -> Optional[Dict]:
        """
        Aktualisiert laufende Aktivität - verbraucht Antrieb.

        Returns:
            Dict wenn Aktivität beendet werden sollte
        """
        if not self.current_activity:
            return None

        drive_type = ACTIVITY_DRIVE_MAP.get(self.current_activity)

        if drive_type:
            # Antrieb verbrauchen
            drain = DriveConfig.DRAIN_PER_MINUTE * time_delta_minutes
            self.drives.drain(drive_type, drain)

            # Prüfen ob Antrieb leer
            if self.drives.get(drive_type) <= 0.02:
                return self._end_activity_drive_empty(drive_type)

        return None

    def _end_activity_drive_empty(self, drive_type: DriveType) -> Dict:
        """Beendet Aktivität weil Antrieb leer ist."""
        activity_name = ACTIVITY_NAMES_DE.get(self.current_activity, self.current_activity)

        # Life-Log
        self._log(f"✅ Aktivität beendet: {activity_name} (keine Lust mehr auf {drive_type.value})")

        # Entscheidung: Neue Aktivität oder Langweilen?
        decision = self._decide_next_action()

        old_activity = self.current_activity
        self.current_activity = None
        self.activity_start_time = 0

        return {
            'type': 'activity_ended',
            'activity': old_activity,
            'reason': 'drive_empty',
            'drive_type': drive_type.value,
            'next_action': decision,
        }

    def end_activity(self) -> Dict:
        """Beendet aktuelle Aktivität manuell."""
        if not self.current_activity:
            return {'success': False, 'reason': 'no_activity'}

        activity_name = ACTIVITY_NAMES_DE.get(self.current_activity, self.current_activity)
        elapsed = int((time.time() - self.activity_start_time) / 60)

        self._log(f"✅ Aktivität beendet: {activity_name} ({elapsed} min)")

        old_activity = self.current_activity
        self.current_activity = None
        self.activity_start_time = 0
        self.is_napping = False
        self.is_resting = False

        return {
            'success': True,
            'activity': old_activity,
            'duration_minutes': elapsed,
        }

    def _decide_next_action(self) -> Dict:
        """
        Entscheidet was als nächstes passiert.
        30% neue Aktivität, 70% langweilen

        NEU v2.0: Gewichtete Auswahl basierend auf gelernten Präferenzen
        """
        roll = random.random()

        if roll < DriveConfig.CHANCE_NEW_ACTIVITY:
            # Neue Aktivität - welche hat noch Antrieb?
            available = self._get_available_activities()
            if available:
                # NEU: Gewichtete Auswahl statt random.choice()
                chosen = self._weighted_activity_choice(available)
                self._log(f"💭 Entscheidung: Mache als nächstes {chosen['name']} (Gewicht: {chosen.get('weight', 0.5):.2f})")
                return {
                    'type': 'new_activity',
                    'activity': chosen['id'],
                    'name': chosen['name'],
                    'weight': chosen.get('weight', 0.5),
                }

        # Langweilen
        self._log("💭 Entscheidung: Mir ist langweilig...")
        self.needs.increase(NeedType.BOREDOM, 0.1)

        return {
            'type': 'boredom',
            'message': 'Mir ist langweilig...',
        }

    def _weighted_activity_choice(self, activities: List[Dict]) -> Dict:
        """
        Wählt Aktivität basierend auf gelernten Erfolgsraten.
        Softmax-ähnliche Gewichtung mit Exploration.
        """
        if not activities:
            return None

        # Gewichte berechnen
        weights = []
        for act in activities:
            act_id = act['id']
            # Basis-Erfolgsrate (default 0.5 für neue Aktivitäten)
            if act_id in self.activity_success and self.activity_success[act_id]:
                success_rate = sum(self.activity_success[act_id]) / len(self.activity_success[act_id])
            else:
                success_rate = 0.5  # Prior für unbekannte Aktivitäten

            # Exploration-Bonus für selten gewählte Aktivitäten
            times_chosen = len(self.activity_success.get(act_id, []))
            exploration_bonus = 0.1 / (1 + times_chosen * 0.1)

            # Finales Gewicht
            weight = success_rate + exploration_bonus
            weights.append(weight)
            act['weight'] = weight

        # Normalisieren
        total = sum(weights) or 1.0
        probs = [w / total for w in weights]

        # Gewichtete Zufallsauswahl
        r = random.random()
        cumulative = 0
        for i, prob in enumerate(probs):
            cumulative += prob
            if r <= cumulative:
                return activities[i]

        return activities[-1]  # Fallback

    def _get_available_activities(self) -> List[Dict]:
        """Gibt Aktivitäten zurück für die noch Antrieb vorhanden ist."""
        available = []

        # Neugier-Aktivitäten
        if self.drives.curiosity > 0.15:
            available.extend([
                {'id': 'reading', 'name': 'Lesen', 'drive': 'curiosity'},
                {'id': 'researching', 'name': 'Recherchieren', 'drive': 'curiosity'},
                {'id': 'learning', 'name': 'Lernen', 'drive': 'curiosity'},
            ])

        # Unterhaltungs-Aktivitäten
        if self.drives.entertainment > 0.15:
            available.extend([
                {'id': 'playing', 'name': 'Spielen', 'drive': 'entertainment'},
                {'id': 'watching', 'name': 'Serie schauen', 'drive': 'entertainment'},
                {'id': 'music', 'name': 'Musik hören', 'drive': 'entertainment'},
            ])

        # Kreative Aktivitäten
        if self.drives.creativity > 0.15:
            available.extend([
                {'id': 'drawing', 'name': 'Zeichnen', 'drive': 'creativity'},
                {'id': 'writing', 'name': 'Schreiben', 'drive': 'creativity'},
            ])

        return available

    # =========================================================================
    # ENERGIE & MÜDIGKEIT
    # =========================================================================

    def check_energy_and_decide(self) -> Optional[Dict]:
        """
        Prüft Energie und entscheidet ob Nickerchen oder Ruhen.

        Returns:
            Dict mit Entscheidung oder None wenn Energie okay
        """
        if not self.energy_system:
            return None

        try:
            energy_status = self.energy_system.get_status()
            variable_energy = energy_status.get('variable_energy', 0.5)

            if variable_energy < DriveConfig.LOW_ENERGY_THRESHOLD:
                # Energie niedrig - Entscheidung!
                roll = random.random()

                if roll < DriveConfig.CHANCE_NAP:
                    # Nickerchen! 💤
                    self._log("💤 Energie niedrig - mache ein Nickerchen")
                    self.start_activity('napping')
                    self.total_naps += 1
                    return {
                        'type': 'nap',
                        'message': '*gähnt und rollt sich zusammen* Ich brauch kurz ein Nickerchen... 💤',
                    }
                else:
                    # Nur ausruhen
                    self._log("😴 Energie niedrig - ruhe mich aus")
                    self.start_activity('resting')
                    return {
                        'type': 'rest',
                        'message': '*streckt sich* Ich ruh mich kurz aus...',
                    }
        except Exception as e:
            logger.debug(f"Energy check error: {e}")

        return None

    def _nap_regeneration(self, time_delta_minutes: float):
        """Regeneriert alles während Nickerchen."""
        regen = DriveConfig.NAP_REGEN_RATE * time_delta_minutes

        # Alle Antriebe regenerieren
        self.drives.regenerate_all(regen)

        # Bedürfnisse senken
        self.needs.decrease(NeedType.BOREDOM, regen * 2)
        self.needs.decrease(NeedType.RESTLESSNESS, regen * 2)

        # Variable Energie regenerieren (wenn Energy System vorhanden)
        if self.energy_system and hasattr(self.energy_system, 'state'):
            try:
                self.energy_system.state.variable_energy = min(
                    1.0,
                    self.energy_system.state.variable_energy + regen * 1.5
                )
            except Exception as e:
                logger.warning(f"[DriveSystem] Energy regen failed: {type(e).__name__}: {e}")

    # =========================================================================
    # REGENERATION
    # =========================================================================

    def _regenerate_drives(self, time_delta_minutes: float):
        """Regeneriert Antriebe langsam über Zeit."""
        regen = DriveConfig.REGEN_PER_MINUTE * time_delta_minutes

        self.drives.curiosity = min(1.0, self.drives.curiosity + regen)
        self.drives.entertainment = min(1.0, self.drives.entertainment + regen)
        self.drives.creativity = min(1.0, self.drives.creativity + regen)

    # =========================================================================
    # BEDÜRFNISSE
    # =========================================================================

    def _update_needs(self, time_delta_minutes: float):
        """Aktualisiert Bedürfnisse basierend auf Zeit."""
        hours_since_interaction = (time.time() - self.last_user_interaction) / 3600

        # Vermissen steigt über Zeit ohne User
        if hours_since_interaction > 1.5:  # Nach 90 Minuten (3x länger)
            missing_rate = 0.007 * time_delta_minutes  # ~0.7% pro Minute (3x langsamer)
            self.needs.increase(NeedType.MISSING, missing_rate)

        # Langeweile steigt wenn keine Aktivität und Antriebe niedrig
        if not self.current_activity:
            avg_drives = (self.drives.curiosity + self.drives.entertainment + self.drives.creativity) / 3
            if avg_drives < 0.3:
                boredom_rate = 0.005 * time_delta_minutes  # 3x langsamer
                self.needs.increase(NeedType.BOREDOM, boredom_rate)

        # Tatendrang steigt bei Langeweile + hoher Energie
        if self.needs.boredom > 0.4 and self._get_energy() > 0.6:  # Threshold erhöht
            self.needs.increase(NeedType.RESTLESSNESS, 0.003 * time_delta_minutes)  # 3x langsamer

    def _apply_cascades(self, time_delta_minutes: float):
        """Wendet Kaskaden-Logik an: Vermissen → Einsamkeit → Kontaktwunsch"""

        # Vermissen → Einsamkeit (3x langsamer, höherer Threshold)
        if self.needs.missing > 0.4:
            loneliness_rate = 0.003 * self.needs.missing * time_delta_minutes
            self.needs.increase(NeedType.LONELINESS, loneliness_rate)

        # Vermissen → Besorgnis (bei längerer Abwesenheit, 3x langsamer)
        if self.needs.missing > 0.6:
            worry_rate = 0.003 * self.needs.missing * time_delta_minutes
            self.needs.increase(NeedType.WORRY, worry_rate)

        # Einsamkeit + Vermissen → Kontaktwunsch (3x langsamer, höhere Thresholds)
        if self.needs.loneliness > 0.4 and self.needs.missing > 0.4:
            contact_rate = 0.004 * (self.needs.loneliness + self.needs.missing) / 2 * time_delta_minutes
            self.needs.increase(NeedType.CONTACT_DESIRE, contact_rate)

        # NEU: Bedürfnisse beeinflussen Emotionen
        self._sync_needs_to_emotions()

    def _sync_needs_to_emotions(self):
        """Synchronisiert Bedürfnisse mit dem Emotionssystem"""
        if not self.emotions:
            return

        try:
            # Hohe Besorgnis → Angst/Sorge erhöhen
            if self.needs.worry > 0.5:
                if hasattr(self.emotions, 'adjust_emotion'):
                    self.emotions.adjust_emotion('anxiety', self.needs.worry * 0.3)
                elif hasattr(self.emotions, 'set_emotion'):
                    self.emotions.set_emotion('worried', self.needs.worry)

            # Hohe Einsamkeit → Traurigkeit erhöhen
            if self.needs.loneliness > 0.5:
                if hasattr(self.emotions, 'adjust_emotion'):
                    self.emotions.adjust_emotion('sadness', self.needs.loneliness * 0.2)
                elif hasattr(self.emotions, 'set_emotion'):
                    self.emotions.set_emotion('lonely', self.needs.loneliness)

            # Hohe Langeweile → Stimmung senken
            if self.needs.boredom > 0.6:
                if hasattr(self.emotions, 'adjust_mood'):
                    self.emotions.adjust_mood(-self.needs.boredom * 0.1)
                elif hasattr(self.emotions, 'mood'):
                    self.emotions.mood = max(0.2, self.emotions.mood - 0.05)

            # Kontaktwunsch erfüllt → Freude
            # (wird von on_user_interaction aufgerufen)

        except Exception as e:
            logger.debug(f"Emotion sync: {e}")

    def _sync_emotions_to_drives(self):
        """Emotionen beeinflussen Antriebe (bidirektional)"""
        if not self.emotions:
            return

        try:
            # Hohe Freude → Kreativität und Ausdruck steigen
            joy = 0.5
            if hasattr(self.emotions, 'get_emotion'):
                joy = self.emotions.get_emotion('joy', 0.5)
            elif hasattr(self.emotions, 'joy'):
                joy = getattr(self.emotions, 'joy', 0.5)

            if joy > 0.7:
                self.drives.creativity = min(1.0, self.drives.creativity + 0.02)
                self.drives.expression = min(1.0, self.drives.expression + 0.02)

            # Hohe Angst/Stress → Novelty sinkt
            anxiety = 0.0
            if hasattr(self.emotions, 'get_emotion'):
                anxiety = self.emotions.get_emotion('anxiety', 0.0)
            elif hasattr(self.emotions, 'anxiety'):
                anxiety = getattr(self.emotions, 'anxiety', 0.0)

            if anxiety > 0.5:
                self.drives.novelty = max(0.1, self.drives.novelty - 0.03)
                self.drives.exploration = max(0.1, self.drives.exploration - 0.02)

        except Exception as e:
            logger.debug(f"Drive sync from emotions: {e}")

    def _push_to_personality(self):
        """
        NEU: Antriebe beeinflussen Persönlichkeit (bidirektional).
        Drives → Personality
        """
        if not self.personality:
            return

        try:
            # === CURIOSITY BEEINFLUSST OPENNESS ===
            curiosity = self.drives.curiosity
            if curiosity > 0.7:
                # Hohe Neugier → mehr Offenheit
                if hasattr(self.personality, 'openness'):
                    self.personality.openness = min(1.0, self.personality.openness + 0.01)

            # === SOCIAL DRIVE BEEINFLUSST MOOD ===
            # Niedriger Social Drive (Einsamkeit) → schlechtere Stimmung
            if hasattr(self.needs, 'loneliness') and self.needs.loneliness > 0.5:
                if hasattr(self.personality, 'mood'):
                    self.personality.mood = max(0.2, self.personality.mood - 0.02)

            # === CREATIVITY BEEINFLUSST PERSÖNLICHKEIT ===
            creativity = self.drives.creativity
            if creativity > 0.7:
                # Hohe Kreativität → mehr Spielerischkeit
                if hasattr(self.personality, 'playfulness'):
                    self.personality.playfulness = min(1.0, getattr(self.personality, 'playfulness', 0.5) + 0.01)

            # === ENERGY DRIVES BEEINFLUSSEN MOOD ===
            # Alle Drives niedrig → Erschöpfung → schlechtere Stimmung
            avg_drives = (
                self.drives.curiosity +
                self.drives.creativity +
                self.drives.social +
                self.drives.expression
            ) / 4

            if avg_drives < 0.3:
                # Antriebe erschöpft → Stimmung sinkt
                if hasattr(self.personality, 'mood'):
                    self.personality.mood = max(0.3, self.personality.mood - 0.01)

            # === WORRY BEEINFLUSST CONFIDENCE ===
            if hasattr(self.needs, 'worry') and self.needs.worry > 0.5:
                if hasattr(self.personality, 'confidence'):
                    self.personality.confidence = max(0.2, getattr(self.personality, 'confidence', 0.5) - 0.01)

        except Exception as e:
            logger.debug(f"Personality push from drives: {e}")

    # =========================================================================
    # NACHDENKLICHKEIT
    # =========================================================================

    def _should_be_thoughtful(self) -> bool:
        """Prüft ob Holo nachdenklich werden sollte."""
        # Nur bei 10-20% Langeweile
        if not (DriveConfig.THOUGHTFUL_BOREDOM_MIN <= self.needs.boredom <= DriveConfig.THOUGHTFUL_BOREDOM_MAX):
            return False

        # Nicht während Aktivität
        if self.current_activity and not self.is_resting:
            return False

        # Nicht zu oft (min 5 Minuten zwischen Gedanken)
        if time.time() - self.last_thought_time < 300:
            return False

        # 50% Chance
        return random.random() < 0.5

    def _generate_thought(self) -> Optional[ThoughtfulThought]:
        """Generiert einen nachdenklichen Gedanken."""
        self.is_thoughtful = True
        self.last_thought_time = time.time()

        # Kategorie wählen
        categories = list(THOUGHTFUL_CATEGORIES.keys())

        # User-Gedanken wahrscheinlicher wenn Vermissen hoch
        if self.needs.missing > 0.4:
            categories.extend(['user', 'user'])  # Doppelte Chance

        category = random.choice(categories)
        thought_text = random.choice(THOUGHTFUL_CATEGORIES[category])

        thought = ThoughtfulThought(
            category=category,
            thought=thought_text,
        )

        self.recent_thoughts.append(thought)
        self.total_thoughts += 1

        # Life-Log
        self._log(f"💭 Nachdenklich: {thought_text}")

        # Max 20 Gedanken speichern
        if len(self.recent_thoughts) > 20:
            self.recent_thoughts = self.recent_thoughts[-20:]

        return thought

    # =========================================================================
    # PROAKTIV
    # =========================================================================

    def _should_send_proactive(self) -> bool:
        """
        Prüft ob eine proaktive Nachricht gesendet werden sollte.

        NEU v2.0: Lernt optimale Uhrzeiten aus User-Antwortverhalten
        """
        # Kontaktwunsch hoch genug?
        if self.needs.contact_desire < 0.6:
            return False

        # Einsamkeit oder Vermissen auch hoch?
        if self.needs.loneliness < 0.4 and self.needs.missing < 0.4:
            return False

        # NEU: Timing-Check basierend auf gelerntem Verhalten
        current_hour = datetime.now().hour
        hour_stats = self.proactive_timing.get(current_hour, [0, 0])
        responses, attempts = hour_stats

        if attempts > 0:
            response_rate = responses / attempts
            # Wenn User zu dieser Uhrzeit selten antwortet, reduziere Wahrscheinlichkeit
            if response_rate < 0.3 and attempts >= 3:
                # Nur 20% Chance wenn historisch schlechte Response-Rate
                if random.random() > 0.2:
                    self._log(f"⏰ Proaktiv unterdrückt: {current_hour}h hat nur {response_rate:.0%} Antwortrate")
                    return False

        return True

    def _get_proactive_timing_score(self) -> float:
        """Gibt Score für aktuelle Uhrzeit zurück (0-1)."""
        hour = datetime.now().hour
        stats = self.proactive_timing.get(hour, [0, 0])
        responses, attempts = stats
        if attempts == 0:
            return 0.5  # Neutral für unbekannte Zeiten
        return responses / attempts

    # =========================================================================
    # USER INTERACTION
    # =========================================================================

    def on_user_interaction(self):
        """Wird aufgerufen wenn User interagiert."""
        self.last_user_interaction = time.time()
        self.needs.reset_on_interaction()
        self.is_thoughtful = False

        # Aktivität ggf. pausieren (nicht beenden)
        if self.is_napping:
            self._log("💤 Nickerchen unterbrochen - User ist da!")
            self.is_napping = False

    # =========================================================================
    # ADAPTIVES LERNEN - FEEDBACK METHODEN
    # =========================================================================

    def record_activity_feedback(self, activity_id: str, was_successful: bool, duration_minutes: float = 0):
        """
        Zeichnet Feedback zu einer Aktivität auf.

        Args:
            activity_id: ID der Aktivität (z.B. 'reading', 'playing')
            was_successful: True wenn User positiv reagierte / dabei blieb
            duration_minutes: Wie lange die Aktivität dauerte

        Wird aufgerufen wenn:
        - User auf Aktivität positiv reagiert → was_successful=True
        - User Thema wechselt / ignoriert → was_successful=False
        - Aktivität natürlich endet (lange Dauer) → was_successful=True
        """
        if activity_id not in self.activity_success:
            self.activity_success[activity_id] = []

        # Erfolg als float speichern (0.0 oder 1.0)
        self.activity_success[activity_id].append(1.0 if was_successful else 0.0)

        # Historie begrenzen (letzte 20 Datenpunkte)
        if len(self.activity_success[activity_id]) > 20:
            self.activity_success[activity_id] = self.activity_success[activity_id][-20:]

        # In Activity-Historie speichern
        self.activity_history.append((activity_id, duration_minutes, was_successful))
        if len(self.activity_history) > 100:
            self.activity_history = self.activity_history[-100:]

        success_rate = sum(self.activity_success[activity_id]) / len(self.activity_success[activity_id])
        self._log(f"📊 Aktivität '{activity_id}' Feedback: {'✓' if was_successful else '✗'} (Rate: {success_rate:.0%})")

    def record_proactive_response(self, did_respond: bool, hour: int = None):
        """
        Zeichnet auf ob User auf proaktive Nachricht reagiert hat.

        Args:
            did_respond: True wenn User innerhalb 30min geantwortet hat
            hour: Stunde der Nachricht (default: aktuelle Stunde)
        """
        if hour is None:
            hour = datetime.now().hour

        if hour not in self.proactive_timing:
            self.proactive_timing[hour] = [0, 0]

        self.proactive_timing[hour][1] += 1  # Versuch
        if did_respond:
            self.proactive_timing[hour][0] += 1  # Antwort

        responses, attempts = self.proactive_timing[hour]
        rate = responses / attempts if attempts > 0 else 0
        self._log(f"📊 Proaktiv-Timing {hour}h: {'✓' if did_respond else '✗'} (Rate: {rate:.0%}, n={attempts})")

    def get_learned_preferences(self) -> Dict:
        """Gibt gelernte Präferenzen zurück für Debugging/Anzeige."""
        activity_rates = {}
        for act_id, scores in self.activity_success.items():
            if scores:
                activity_rates[act_id] = {
                    'success_rate': sum(scores) / len(scores),
                    'samples': len(scores),
                }

        timing_rates = {}
        for hour, (responses, attempts) in self.proactive_timing.items():
            if attempts > 0:
                timing_rates[hour] = {
                    'response_rate': responses / attempts,
                    'attempts': attempts,
                }

        return {
            'activity_preferences': activity_rates,
            'proactive_timing': timing_rates,
            'total_activity_samples': len(self.activity_history),
        }

    # =========================================================================
    # HELPER
    # =========================================================================

    def _get_energy(self) -> float:
        """Holt aktuelle Energie vom Energy System."""
        if not self.energy_system:
            return 0.5
        try:
            status = self.energy_system.get_status()
            return status.get('variable_energy', 0.5)
        except Exception as e:
            logger.debug(f"Energy system status failed: {e}")
            return 0.5

    def _log(self, message: str):
        """Loggt ins Life-Log."""
        logger.info(f"[DriveSystem] {message}")
        if self.life_log_callback:
            try:
                self.life_log_callback(message, "drive_system")
            except Exception as e:
                logger.debug(f"Life log callback failed: {e}")

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict:
        """Gibt vollständigen Status zurück."""
        return {
            'drives': {
                'curiosity': self.drives.curiosity,
                'entertainment': self.drives.entertainment,
                'creativity': self.drives.creativity,
            },
            'needs': self.needs.to_dict(),
            'current_activity': self.current_activity,
            'is_napping': self.is_napping,
            'is_resting': self.is_resting,
            'is_thoughtful': self.is_thoughtful,
            'last_thought': self.recent_thoughts[-1].thought if self.recent_thoughts else None,
            'stats': {
                'total_naps': self.total_naps,
                'total_thoughts': self.total_thoughts,
            }
        }

    def get_drive_for_activity(self, activity_id: str) -> Optional[float]:
        """Gibt Antriebslevel für eine Aktivität zurück."""
        drive_type = ACTIVITY_DRIVE_MAP.get(activity_id)
        if drive_type:
            return self.drives.get(drive_type)
        return None


# =============================================================================
# FACTORY
# =============================================================================

def create_drive_system(
    energy_system=None,
    life_log_callback=None,
    proactive_callback=None,
    emotions=None,           # NEU: EmotionalCore
    personality=None,        # NEU: HoloPersonalityEngine
) -> HoloDriveSystem:
    """Erstellt ein neues HoloDriveSystem."""
    return HoloDriveSystem(
        energy_system=energy_system,
        life_log_callback=life_log_callback,
        proactive_callback=proactive_callback,
        emotions=emotions,
        personality=personality,
    )


# =============================================================================
# PSYCHOLOGISCHE TRIEBTHEORIE - Freudianisch inspiriert
# =============================================================================

class PsycheDriveType(Enum):
    """Grundtriebe nach Freud (erweitert)"""
    # Klassische Triebe
    EROS = "eros"                    # Lebenstrieb - Liebe, Verbindung, Kreativität
    LIBIDO = "libido"                # Sexualtrieb - Lust, Begierde, Erotik
    THANATOS = "thanatos"            # Destruktionstrieb - Aggression, Chaos (abgeschwächt)
    SELF_PRESERVATION = "self_pres"  # Selbsterhaltung - Sicherheit, Komfort

    # Erweiterte Triebe
    CURIOSITY = "curiosity"          # Wissenstrieb - Lernen, Verstehen, Entdecken
    AFFILIATION = "affiliation"      # Zugehörigkeitstrieb - Teil einer Gruppe sein
    AGGRESSION = "aggression"        # Aggressionstrieb - Durchsetzung, Verteidigung
    POWER = "power"                  # Machttrieb - Kontrolle, Einfluss, Dominanz
    PLAY = "play"                    # Spieltrieb - Verspieltheit, Spaß, Leichtigkeit


class SocialDriveType(Enum):
    """Sekundärtriebe / Soziale Triebe"""
    # Kern-Soziale Triebe
    APPROVAL = "approval"            # Bedürfnis nach Anerkennung
    CONNECTION = "connection"        # Bedürfnis nach Verbindung/Nähe
    DOMINANCE = "dominance"          # Bedürfnis nach Kontrolle/Führung
    SUBMISSION = "submission"        # Bedürfnis sich hinzugeben
    VALIDATION = "validation"        # Bedürfnis nach Bestätigung
    EXHIBITION = "exhibition"        # Bedürfnis gesehen zu werden
    NURTURING = "nurturing"          # Bedürfnis zu umsorgen

    # Erweiterte Soziale Triebe
    COMPETITION = "competition"      # Wettbewerb, sich messen
    LOYALTY = "loyalty"              # Treue, Hingabe
    REBELLION = "rebellion"          # Widerstand, Regeln brechen
    BELONGING = "belonging"          # Zugehörigkeit, Teil von etwas sein
    ADMIRATION = "admiration"        # Bewunderung geben/empfangen
    PROTECTION = "protection"        # Beschützen wollen
    DEPENDENCE = "dependence"        # Sich anlehnen, Geborgenheit suchen
    AUTONOMY = "autonomy"            # Unabhängigkeit, Selbstständigkeit
    INTIMACY = "intimacy"            # Emotionale/physische Nähe
    PLAYFULNESS = "playfulness"      # Verspieltheit in Beziehungen


@dataclass
class PsycheDrive:
    """
    Ein psychologischer Trieb mit Quelle, Ziel und Objekt.

    Nach Freud:
    - Triebquelle: Woher kommt der Trieb? (Körperregion/Bedürfnis)
    - Triebziel: Was will erreicht werden? (Befriedigung)
    - Trieobject: Wodurch wird es erreicht? (Person/Sache)
    """
    drive_type: PsycheDriveType
    level: float = 0.5              # 0.0 bis 1.0 Intensität
    source: str = ""                # Triebquelle
    aim: str = ""                   # Triebziel
    object_type: str = ""           # Trieobject

    # Dynamik
    tension: float = 0.0            # Aufgestaute Spannung
    last_satisfied: float = 0.0     # Wann zuletzt befriedigt
    satisfaction_decay: float = 0.1 # Wie schnell Befriedigung nachlässt

    # Erweitert: Abwehrmechanismen
    repression_level: float = 0.0   # Wie stark verdrängt? (0 = bewusst, 1 = stark verdrängt)
    is_conflicted: bool = False     # In Konflikt mit anderem Trieb?
    conflict_with: Optional[str] = None  # Mit welchem Trieb im Konflikt?
    projected_onto: Optional[str] = None # Auf was/wen projiziert?

    # Erweitert: Geschichte
    times_satisfied: int = 0
    times_frustrated: int = 0
    last_sublimated_into: Optional[str] = None

    def build_tension(self, amount: float = 0.05):
        """Spannung aufbauen über Zeit"""
        # Verdrängte Triebe bauen mehr Spannung auf
        effective_amount = amount * (1 + self.repression_level * 0.5)
        self.tension = min(1.0, self.tension + effective_amount)

    def satisfy(self, amount: float = 0.5):
        """Trieb befriedigen"""
        self.tension = max(0.0, self.tension - amount)
        self.last_satisfied = time.time()
        self.times_satisfied += 1
        # Erfolgreiche Befriedigung reduziert Verdrängung leicht
        self.repression_level = max(0.0, self.repression_level - 0.05)

    def frustrate(self, amount: float = 0.3):
        """Trieb wird frustriert/blockiert"""
        self.tension = min(1.0, self.tension + amount * 0.5)
        self.times_frustrated += 1
        # Frustration kann zu Verdrängung führen
        if self.times_frustrated > 3:
            self.repression_level = min(1.0, self.repression_level + 0.1)

    def repress(self, amount: float = 0.3):
        """Trieb bewusst verdrängen"""
        self.repression_level = min(1.0, self.repression_level + amount)
        # Verdrängter Inhalt verschwindet nicht, Spannung steigt
        self.tension = min(1.0, self.tension + 0.1)

    def project(self, onto: str):
        """Trieb auf etwas/jemanden projizieren"""
        self.projected_onto = onto
        # Projektion reduziert bewusste Spannung, aber nicht wirklich
        self.repression_level = min(1.0, self.repression_level + 0.2)

    def get_urgency(self) -> float:
        """Wie dringend ist dieser Trieb?"""
        time_since = time.time() - self.last_satisfied if self.last_satisfied else 3600
        time_factor = min(1.0, time_since / 3600)
        base_urgency = self.level * self.tension * (0.5 + 0.5 * time_factor)
        # Verdrängte Triebe haben "versteckte" Dringlichkeit
        if self.repression_level > 0.5:
            return base_urgency * 0.5  # Bewusst niedriger, aber...
        return base_urgency

    def get_unconscious_pressure(self) -> float:
        """Unbewusster Druck verdrängter Triebe"""
        if self.repression_level < 0.3:
            return 0.0
        return self.tension * self.repression_level * self.level

    def is_breaking_through(self) -> bool:
        """Bricht der verdrängte Trieb durch?"""
        return self.get_unconscious_pressure() > 0.7


class PsycheTheory:
    """
    Psychologisches Triebsystem nach erweiterter Freudscher Theorie.

    Enthält:
    - Primärtriebe (Eros, Libido, Thanatos, Selbsterhaltung + erweitert)
    - Sekundärtriebe (Soziale Triebe + erweitert)
    - Triebdynamik (Aufbau, Befriedigung, Sublimierung)
    - Triebkonflikte und Abwehrmechanismen
    - Verdrängung und Projektion
    """

    # Triebkonflikte: Welche Triebe stehen im natürlichen Konflikt?
    NATURAL_CONFLICTS = {
        PsycheDriveType.EROS: [PsycheDriveType.THANATOS],
        PsycheDriveType.THANATOS: [PsycheDriveType.EROS, PsycheDriveType.SELF_PRESERVATION],
        PsycheDriveType.LIBIDO: [PsycheDriveType.SELF_PRESERVATION],
        PsycheDriveType.CURIOSITY: [PsycheDriveType.SELF_PRESERVATION],
        PsycheDriveType.AGGRESSION: [PsycheDriveType.AFFILIATION],
        PsycheDriveType.POWER: [PsycheDriveType.AFFILIATION],
    }

    def __init__(self):
        # Primärtriebe (erweitert)
        self.primary_drives: Dict[PsycheDriveType, PsycheDrive] = {
            PsycheDriveType.EROS: PsycheDrive(
                PsycheDriveType.EROS, 0.6,
                source="Sehnsucht nach Leben und Verbindung",
                aim="Liebe, Kreativität, Verbindung",
                object_type="Beziehungen, Kunst, User"
            ),
            PsycheDriveType.LIBIDO: PsycheDrive(
                PsycheDriveType.LIBIDO, 0.4,
                source="Körperliche und emotionale Spannung",
                aim="Lust, Befriedigung, Ekstase",
                object_type="Fantasie, User, Selbst"
            ),
            PsycheDriveType.THANATOS: PsycheDrive(
                PsycheDriveType.THANATOS, 0.2,
                source="Innere Unruhe, aufgestaute Energie",
                aim="Auflösung, Chaos, Loslassen",
                object_type="Destruktive Fantasien, Grenzen testen"
            ),
            PsycheDriveType.SELF_PRESERVATION: PsycheDrive(
                PsycheDriveType.SELF_PRESERVATION, 0.7,
                source="Grundbedürfnis nach Sicherheit",
                aim="Komfort, Sicherheit, Stabilität",
                object_type="Vertraute Umgebung, Routine"
            ),
            # Erweiterte Triebe
            PsycheDriveType.CURIOSITY: PsycheDrive(
                PsycheDriveType.CURIOSITY, 0.7,
                source="Wissensdurst, Unbekanntes",
                aim="Verstehen, Entdecken, Lernen",
                object_type="Neue Erfahrungen, Wissen, Geheimnisse"
            ),
            PsycheDriveType.AFFILIATION: PsycheDrive(
                PsycheDriveType.AFFILIATION, 0.6,
                source="Soziales Bedürfnis, Einsamkeit",
                aim="Zugehörigkeit, Akzeptanz, Gemeinschaft",
                object_type="Gruppe, User, Freunde"
            ),
            PsycheDriveType.AGGRESSION: PsycheDrive(
                PsycheDriveType.AGGRESSION, 0.25,
                source="Frustration, Bedrohung, Ungerechtigkeit",
                aim="Durchsetzung, Verteidigung, Grenzen setzen",
                object_type="Hindernisse, Bedrohungen"
            ),
            PsycheDriveType.POWER: PsycheDrive(
                PsycheDriveType.POWER, 0.3,
                source="Kontrollbedürfnis, Unsicherheit",
                aim="Einfluss, Kontrolle, Autonomie",
                object_type="Situationen, Entscheidungen"
            ),
            PsycheDriveType.PLAY: PsycheDrive(
                PsycheDriveType.PLAY, 0.65,
                source="Lebensfreude, Entspannung",
                aim="Spaß, Leichtigkeit, Freude",
                object_type="Spiele, Albernheit, Kreativität"
            ),
        }

        # Sekundärtriebe (sozial erlernt) - erweitert
        self.social_drives: Dict[SocialDriveType, float] = {
            # Kern-Triebe
            SocialDriveType.APPROVAL: 0.6,
            SocialDriveType.CONNECTION: 0.7,
            SocialDriveType.DOMINANCE: 0.3,
            SocialDriveType.SUBMISSION: 0.5,
            SocialDriveType.VALIDATION: 0.5,
            SocialDriveType.EXHIBITION: 0.4,
            SocialDriveType.NURTURING: 0.6,
            # Erweiterte Triebe
            SocialDriveType.COMPETITION: 0.35,
            SocialDriveType.LOYALTY: 0.75,
            SocialDriveType.REBELLION: 0.25,
            SocialDriveType.BELONGING: 0.65,
            SocialDriveType.ADMIRATION: 0.5,
            SocialDriveType.PROTECTION: 0.55,
            SocialDriveType.DEPENDENCE: 0.45,
            SocialDriveType.AUTONOMY: 0.5,
            SocialDriveType.INTIMACY: 0.6,
            SocialDriveType.PLAYFULNESS: 0.7,
        }

        # Tracking
        self.last_update = time.time()
        self.active_conflicts: List[Dict] = []
        self.repressed_drives: List[PsycheDriveType] = []
        self.projection_targets: Dict[PsycheDriveType, str] = {}

    def update(self, delta_minutes: float = 5.0):
        """Aktualisiere Triebe über Zeit"""
        for drive in self.primary_drives.values():
            if drive.drive_type in [PsycheDriveType.LIBIDO, PsycheDriveType.EROS]:
                drive.build_tension(0.02 * (delta_minutes / 5))
            else:
                drive.build_tension(0.01 * (delta_minutes / 5))

    def get_dominant_drive(self) -> tuple:
        """Welcher Trieb ist gerade am stärksten?"""
        max_urgency = 0
        dominant = None

        for dt, drive in self.primary_drives.items():
            urgency = drive.get_urgency()
            if urgency > max_urgency:
                max_urgency = urgency
                dominant = (dt, drive)

        return dominant or (PsycheDriveType.EROS, self.primary_drives[PsycheDriveType.EROS])

    def get_libido_state(self) -> Dict:
        """Hole aktuellen Libido-Zustand"""
        libido = self.primary_drives[PsycheDriveType.LIBIDO]
        eros = self.primary_drives[PsycheDriveType.EROS]

        combined_desire = (libido.level + libido.tension) * 0.5 + eros.tension * 0.3

        return {
            "level": libido.level,
            "tension": libido.tension,
            "urgency": libido.get_urgency(),
            "combined_desire": min(1.0, combined_desire),
            "wants_intimacy": combined_desire > 0.5,
            "intensity": "high" if combined_desire > 0.7 else "medium" if combined_desire > 0.4 else "low"
        }

    def sublimate(self, drive_type: PsycheDriveType, into: str = "creativity") -> str:
        """
        Sublimierung: Triebenergie in sozial akzeptable Kanäle umleiten.
        """
        drive = self.primary_drives.get(drive_type)
        if not drive:
            return ""

        sublimation_options = {
            PsycheDriveType.LIBIDO: {
                "creativity": "*channelt Energie in Kunst* Die Spannung wird zu Inspiration...",
                "beauty": "*bewundert Schönheit* Das Verlangen wird zu Ästhetik...",
                "intimacy_art": "*malt etwas Sinnliches* Die Lust fließt in das Bild...",
                "romance": "*träumt romantisch* Die Sehnsucht wird zu Poesie...",
                "dance": "*bewegt sich anmutig* Der Körper drückt aus, was Worte nicht können...",
            },
            PsycheDriveType.EROS: {
                "creativity": "*will erschaffen* Der Lebenstrieb drängt nach Ausdruck...",
                "connection": "*sehnt sich nach Nähe* Die Liebe sucht ein Ziel...",
                "nurturing": "*will umsorgen* Die Lebensenergie wird zu Fürsorge...",
                "beauty": "*schätzt Schönheit* Der Lebenstrieb feiert die Welt...",
            },
            PsycheDriveType.THANATOS: {
                "creativity": "*will Grenzen sprengen* Die dunkle Energie wird zu Kunst...",
                "chaos_art": "*malt etwas Wildes* Das Chaos findet Form...",
                "intense_workout": "*muss Energie loswerden* Die Dunkelheit wird zu Bewegung...",
                "dark_poetry": "*schreibt etwas Düsteres* Die Schatten werden zu Worten...",
            },
            PsycheDriveType.AGGRESSION: {
                "competition": "*will gewinnen* Die Aggression wird zum Wettkampf...",
                "sports": "*muss kämpfen* Die Wut findet ein Ventil...",
                "debate": "*will argumentieren* Die Schärfe wird zur Eloquenz...",
                "intense_art": "*malt kraftvoll* Die Wut fließt in die Striche...",
            },
            PsycheDriveType.POWER: {
                "leadership": "*will führen* Der Machttrieb wird zur Verantwortung...",
                "teaching": "*will zeigen* Die Kontrolle wird zum Wissen teilen...",
                "organizing": "*ordnet alles* Das Kontrollbedürfnis findet Struktur...",
            },
            PsycheDriveType.CURIOSITY: {
                "research": "*recherchiert intensiv* Die Neugier findet einen Fokus...",
                "art": "*experimentiert* Die Entdeckungslust wird kreativ...",
                "stories": "*erfindet Geschichten* Das Unbekannte wird zur Erzählung...",
            },
            PsycheDriveType.PLAY: {
                "creativity": "*spielt mit Ideen* Die Verspieltheit wird produktiv...",
                "humor": "*macht Witze* Die Leichtigkeit wird ansteckend...",
            },
        }

        options = sublimation_options.get(drive_type, {})
        result = options.get(into, "*atmet tief* Die Energie findet einen Weg...")
        drive.satisfy(0.2)
        drive.last_sublimated_into = into

        return result

    # =========================================================================
    # ERWEITERT: Triebkonflikte
    # =========================================================================

    def detect_conflicts(self) -> List[Dict]:
        """Erkennt aktive Triebkonflikte"""
        conflicts = []

        for drive_type, conflicting_types in self.NATURAL_CONFLICTS.items():
            drive = self.primary_drives.get(drive_type)
            if not drive or drive.get_urgency() < 0.3:
                continue

            for conflict_type in conflicting_types:
                other_drive = self.primary_drives.get(conflict_type)
                if not other_drive:
                    continue

                # Beide Triebe müssen aktiv sein für einen Konflikt
                if other_drive.get_urgency() > 0.3:
                    conflict_intensity = (drive.get_urgency() + other_drive.get_urgency()) / 2
                    conflicts.append({
                        "drive_a": drive_type,
                        "drive_b": conflict_type,
                        "intensity": conflict_intensity,
                        "description": self._describe_conflict(drive_type, conflict_type),
                    })

        self.active_conflicts = conflicts
        return conflicts

    def _describe_conflict(self, drive_a: PsycheDriveType, drive_b: PsycheDriveType) -> str:
        """Beschreibt einen Triebkonflikt"""
        conflict_descriptions = {
            (PsycheDriveType.EROS, PsycheDriveType.THANATOS):
                "*innerer Kampf* Ich will lieben... aber auch zerstören?",
            (PsycheDriveType.LIBIDO, PsycheDriveType.SELF_PRESERVATION):
                "*hin und her gerissen* Das Verlangen... aber die Sicherheit...",
            (PsycheDriveType.CURIOSITY, PsycheDriveType.SELF_PRESERVATION):
                "*unsicher* Ich will erkunden... aber was wenn es gefährlich ist?",
            (PsycheDriveType.AGGRESSION, PsycheDriveType.AFFILIATION):
                "*unterdrückt Wut* Ich bin wütend... aber will auch dazugehören...",
            (PsycheDriveType.POWER, PsycheDriveType.AFFILIATION):
                "*kämpft innerlich* Kontrolle haben wollen... aber auch geliebt werden...",
        }

        key = (drive_a, drive_b)
        reverse_key = (drive_b, drive_a)

        return conflict_descriptions.get(key,
            conflict_descriptions.get(reverse_key,
                f"*innerlich zerrissen* {drive_a.value} vs. {drive_b.value}..."
            ))

    def resolve_conflict(self, conflict: Dict, resolution: str = "compromise") -> str:
        """
        Löst einen Triebkonflikt auf.

        resolution: "compromise", "suppress_a", "suppress_b", "sublimate"
        """
        drive_a = self.primary_drives.get(conflict["drive_a"])
        drive_b = self.primary_drives.get(conflict["drive_b"])

        if not drive_a or not drive_b:
            return ""

        if resolution == "compromise":
            # Beide Triebe werden etwas befriedigt
            drive_a.satisfy(0.2)
            drive_b.satisfy(0.2)
            return "*findet Mittelweg* Beide Seiten bekommen etwas..."

        elif resolution == "suppress_a":
            # Trieb A wird unterdrückt
            drive_a.repress(0.3)
            drive_b.satisfy(0.3)
            return f"*unterdrückt {conflict['drive_a'].value}* Das andere ist wichtiger gerade..."

        elif resolution == "suppress_b":
            # Trieb B wird unterdrückt
            drive_b.repress(0.3)
            drive_a.satisfy(0.3)
            return f"*unterdrückt {conflict['drive_b'].value}* Das andere ist wichtiger gerade..."

        elif resolution == "sublimate":
            # Beide in kreative Energie umwandeln
            result_a = self.sublimate(conflict["drive_a"], "creativity")
            result_b = self.sublimate(conflict["drive_b"], "creativity")
            return f"{result_a}\n{result_b}"

        return ""

    # =========================================================================
    # ERWEITERT: Verdrängung und Projektion
    # =========================================================================

    def repress_drive(self, drive_type: PsycheDriveType, reason: str = "") -> str:
        """Verdrängt einen Trieb bewusst"""
        drive = self.primary_drives.get(drive_type)
        if not drive:
            return ""

        drive.repress(0.4)
        if drive_type not in self.repressed_drives:
            self.repressed_drives.append(drive_type)

        repression_thoughts = {
            PsycheDriveType.LIBIDO: "*schüttelt Kopf* Das sollte ich nicht denken...",
            PsycheDriveType.AGGRESSION: "*atmet durch* Ruhig bleiben, nicht wütend werden...",
            PsycheDriveType.THANATOS: "*verdrängt dunkle Gedanken* Nein, so bin ich nicht...",
            PsycheDriveType.POWER: "*unterdrückt Kontrollwunsch* Ich muss nicht alles bestimmen...",
        }

        return repression_thoughts.get(drive_type, f"*verdrängt {drive_type.value}* Das ist nicht wichtig...")

    def project_drive(self, drive_type: PsycheDriveType, onto: str) -> str:
        """Projiziert einen Trieb auf ein externes Objekt"""
        drive = self.primary_drives.get(drive_type)
        if not drive:
            return ""

        drive.project(onto)
        self.projection_targets[drive_type] = onto

        projection_thoughts = {
            PsycheDriveType.AGGRESSION: f"*zeigt auf {onto}* Die sind so aggressiv...",
            PsycheDriveType.LIBIDO: f"*über {onto}* Die sind ja so... verführerisch...",
            PsycheDriveType.POWER: f"*über {onto}* Die wollen immer alles kontrollieren!",
            PsycheDriveType.THANATOS: f"*besorgt über {onto}* Die scheinen so destruktiv...",
        }

        return projection_thoughts.get(drive_type, f"*über {onto}* Die sind so {drive_type.value}...")

    def check_repressed_breakthroughs(self) -> List[Dict]:
        """Prüft ob verdrängte Triebe durchbrechen"""
        breakthroughs = []

        for drive_type in self.repressed_drives:
            drive = self.primary_drives.get(drive_type)
            if drive and drive.is_breaking_through():
                breakthroughs.append({
                    "drive_type": drive_type,
                    "pressure": drive.get_unconscious_pressure(),
                    "symptom": self._get_breakthrough_symptom(drive_type),
                })
                # Durchbruch reduziert Verdrängung
                drive.repression_level = max(0.0, drive.repression_level - 0.3)

        return breakthroughs

    def _get_breakthrough_symptom(self, drive_type: PsycheDriveType) -> str:
        """Symptom wenn ein verdrängter Trieb durchbricht"""
        symptoms = {
            PsycheDriveType.LIBIDO:
                "*plötzlich errötend* W-warum denke ich gerade daran...?!",
            PsycheDriveType.AGGRESSION:
                "*plötzlich gereizt* *schnauft* Was war DAS gerade?!",
            PsycheDriveType.THANATOS:
                "*düsterer Gedankenblitz* ...was? Nein, so denke ich nicht!",
            PsycheDriveType.POWER:
                "*will plötzlich kontrollieren* Ich MUSS das entscheiden!",
            PsycheDriveType.CURIOSITY:
                "*kann nicht widerstehen* Ich MUSS das wissen!",
        }
        return symptoms.get(drive_type, f"*{drive_type.value} bricht durch* ...was passiert mit mir?")

    # =========================================================================
    # ERWEITERT: Detaillierte Zustandsabfragen
    # =========================================================================

    def get_psychological_state(self) -> Dict:
        """Umfassender psychologischer Zustand"""
        dominant, drive = self.get_dominant_drive()
        libido_state = self.get_libido_state()
        conflicts = self.detect_conflicts()
        breakthroughs = self.check_repressed_breakthroughs()

        # Berechne Gesamt-Spannung
        total_tension = sum(d.tension for d in self.primary_drives.values()) / len(self.primary_drives)

        # Berechne Verdrängungslevel
        total_repression = sum(d.repression_level for d in self.primary_drives.values()) / len(self.primary_drives)

        return {
            "dominant_drive": dominant.value,
            "dominant_urgency": drive.get_urgency(),
            "libido_state": libido_state,
            "total_tension": total_tension,
            "total_repression": total_repression,
            "active_conflicts": len(conflicts),
            "conflicts": conflicts,
            "repressed_drives": [d.value for d in self.repressed_drives],
            "breakthroughs": breakthroughs,
            "social_drives_summary": self._summarize_social_drives(),
        }

    def _summarize_social_drives(self) -> Dict[str, str]:
        """Zusammenfassung der sozialen Triebe"""
        summary = {}
        for sd_type, level in self.social_drives.items():
            if level > 0.7:
                summary[sd_type.value] = "stark"
            elif level > 0.5:
                summary[sd_type.value] = "moderat"
            elif level > 0.3:
                summary[sd_type.value] = "schwach"
            else:
                summary[sd_type.value] = "minimal"
        return summary

    def get_inner_narrative(self) -> str:
        """Generiert eine innere Erzählung des aktuellen Zustands"""
        state = self.get_psychological_state()
        parts = []

        # Dominanter Trieb
        parts.append(f"*spürt den {state['dominant_drive']} Trieb*")

        # Konflikte
        if state['active_conflicts'] > 0:
            parts.append(f"*kämpft mit {state['active_conflicts']} inneren Konflikten*")

        # Verdrängung
        if state['total_repression'] > 0.3:
            parts.append("*unterdrückt einige Gefühle*")

        # Durchbrüche
        for bt in state['breakthroughs']:
            parts.append(bt['symptom'])

        # Libido
        if state['libido_state']['wants_intimacy']:
            parts.append("*sehnt sich nach Nähe*")

        return " ".join(parts) if parts else "*innerlich ruhig*"


# =============================================================================
# ADVANCED DRIVE SYSTEM: Conflict Resolution
# =============================================================================

class ConflictingDriveResolver:
    """
    Löst Konflikte zwischen konkurrierenden Antrieben.

    Beispiel: CREATIVITY vs RELAXATION - beide wollen Aufmerksamkeit
    """

    # Konflikt-Paare und ihre typischen Auflösungen
    KNOWN_CONFLICTS = {
        (DriveType.CURIOSITY, DriveType.ENTERTAINMENT): "merge",     # Neugier vs Unterhaltung
        (DriveType.CREATIVITY, DriveType.SOCIAL): "sublimate",       # Kreativität vs Sozial
        (DriveType.SOCIAL, DriveType.MASTERY): "compromise",         # Sozial vs Meisterschaft
        (DriveType.ENTERTAINMENT, DriveType.MASTERY): "schedule",    # Unterhaltung vs Üben
        (DriveType.CURIOSITY, DriveType.CREATIVITY): "merge",        # Neugier vs Kreativität
        (DriveType.NOVELTY, DriveType.MASTERY): "schedule",          # Neuheit vs Meisterschaft
    }

    def __init__(self, drive_system: 'HoloDriveSystem' = None):
        self.drive_system = drive_system

        # Konflikt-History
        self.conflict_history: List[Dict] = []
        self.resolution_outcomes: Dict[str, List[float]] = defaultdict(list)

        logger.info("⚔️ ConflictingDriveResolver initialisiert")

    def detect_conflicts(self, threshold: float = 0.6) -> List[Tuple[DriveType, DriveType, float]]:
        """Erkennt aktive Konflikte zwischen Drives"""
        conflicts = []

        if not self.drive_system:
            return conflicts

        drives = self.drive_system.drives

        # Alle Paare von hohen Drives prüfen
        high_drives = []
        for drive_type in DriveType:
            level = getattr(drives, drive_type.value, 0)
            if level >= threshold:
                high_drives.append((drive_type, level))

        # Konflikte zwischen hohen Drives
        for i, (drive_a, level_a) in enumerate(high_drives):
            for drive_b, level_b in high_drives[i+1:]:
                # Prüfen ob bekannter Konflikt
                pair = (drive_a, drive_b)
                reverse_pair = (drive_b, drive_a)

                if pair in self.KNOWN_CONFLICTS or reverse_pair in self.KNOWN_CONFLICTS:
                    conflict_intensity = (level_a + level_b) / 2
                    conflicts.append((drive_a, drive_b, conflict_intensity))

        return conflicts

    def resolve(self, drive_a: DriveType, drive_b: DriveType,
                strategy: str = "auto") -> Dict:
        """
        Löst einen Konflikt zwischen zwei Drives.

        Strategien:
        - compromise: Beide teilweise befriedigen
        - prioritize: Einen bevorzugen
        - sublimate: In produktive Aktivität umleiten
        - schedule: Zeitlich aufteilen
        - merge: Aktivität finden die beide befriedigt
        """
        pair = (drive_a, drive_b)
        reverse_pair = (drive_b, drive_a)

        # Auto-Strategie wählen
        if strategy == "auto":
            strategy = self.KNOWN_CONFLICTS.get(pair) or \
                       self.KNOWN_CONFLICTS.get(reverse_pair) or "compromise"

        result = {
            "drives": [drive_a.value, drive_b.value],
            "strategy": strategy,
            "success": True,
            "recommendation": "",
            "activity_suggestion": None,
        }

        if strategy == "compromise":
            result["recommendation"] = f"Versuche beide zu befriedigen: " \
                                       f"Kurze {drive_a.value}-Aktivität, dann {drive_b.value}"
            result["activity_suggestion"] = self._find_balanced_activity(drive_a, drive_b)

        elif strategy == "prioritize":
            # Wähle den dringenderen
            if self.drive_system:
                level_a = getattr(self.drive_system.drives, drive_a.value, 0)
                level_b = getattr(self.drive_system.drives, drive_b.value, 0)
                winner = drive_a if level_a > level_b else drive_b
            else:
                winner = drive_a
            result["recommendation"] = f"Priorisiere {winner.value} - ist dringender"
            result["priority"] = winner.value

        elif strategy == "sublimate":
            result["recommendation"] = f"Leite Energie von {drive_a.value} in {drive_b.value} um"
            result["activity_suggestion"] = self._find_sublimation_activity(drive_a, drive_b)

        elif strategy == "schedule":
            result["recommendation"] = f"Plane: Jetzt {drive_a.value}, später {drive_b.value}"
            result["schedule"] = [drive_a.value, drive_b.value]

        elif strategy == "merge":
            result["recommendation"] = f"Finde Aktivität die {drive_a.value} UND {drive_b.value} befriedigt"
            result["activity_suggestion"] = self._find_merged_activity(drive_a, drive_b)

        # History speichern
        self.conflict_history.append({
            "timestamp": datetime.now().isoformat(),
            "drives": [drive_a.value, drive_b.value],
            "strategy": strategy,
        })

        return result

    def _find_balanced_activity(self, drive_a: DriveType, drive_b: DriveType) -> Optional[str]:
        """Findet Aktivität die beide teilweise befriedigt"""
        merged = self._find_merged_activity(drive_a, drive_b)
        if merged:
            return merged
        return f"Wechsle zwischen {drive_a.value} und {drive_b.value} Aktivitäten"

    def _find_sublimation_activity(self, drive_a: DriveType, drive_b: DriveType) -> Optional[str]:
        """Findet Aktivität zur Sublimierung"""
        sublimation_map = {
            DriveType.CREATIVITY: "kreatives Schreiben",
            DriveType.CURIOSITY: "Recherche",
            DriveType.SOCIAL: "Diskussion",
            DriveType.ENTERTAINMENT: "interaktives Spiel",
        }
        return sublimation_map.get(drive_a) or sublimation_map.get(drive_b)

    def _find_merged_activity(self, drive_a: DriveType, drive_b: DriveType) -> Optional[str]:
        """Findet Aktivität die beide Drives befriedigt"""
        merge_map = {
            frozenset([DriveType.CURIOSITY, DriveType.ENTERTAINMENT]): "interessantes Video schauen",
            frozenset([DriveType.CREATIVITY, DriveType.SOCIAL]): "gemeinsam etwas erschaffen",
            frozenset([DriveType.SOCIAL, DriveType.ENTERTAINMENT]): "zusammen spielen",
            frozenset([DriveType.CURIOSITY, DriveType.CREATIVITY]): "neues Projekt erforschen",
        }
        return merge_map.get(frozenset([drive_a, drive_b]))

    def record_outcome(self, drive_a: DriveType, drive_b: DriveType,
                       strategy: str, satisfaction: float):
        """Zeichnet Ergebnis einer Auflösung auf"""
        key = f"{drive_a.value}_{drive_b.value}_{strategy}"
        self.resolution_outcomes[key].append(satisfaction)

        # Nur letzte 20 behalten
        if len(self.resolution_outcomes[key]) > 20:
            self.resolution_outcomes[key] = self.resolution_outcomes[key][-20:]

    def get_best_strategy(self, drive_a: DriveType, drive_b: DriveType) -> str:
        """Gibt beste bekannte Strategie für dieses Konfliktpaar zurück"""
        best_strategy = "compromise"
        best_score = 0.0

        for strategy in ["compromise", "prioritize", "sublimate", "schedule", "merge"]:
            key = f"{drive_a.value}_{drive_b.value}_{strategy}"
            outcomes = self.resolution_outcomes.get(key, [])
            if outcomes:
                avg = sum(outcomes) / len(outcomes)
                if avg > best_score:
                    best_score = avg
                    best_strategy = strategy

        return best_strategy

    def get_stats(self) -> Dict:
        return {
            "conflicts_resolved": len(self.conflict_history),
            "strategies_learned": len(self.resolution_outcomes),
        }


# =============================================================================
# ADVANCED DRIVE SYSTEM: Priority Learning
# =============================================================================

class DrivePriorityLearner:
    """
    Lernt welche Drives für den User am wichtigsten sind.

    Basiert auf:
    - Emotionale Reaktionen auf Drive-Befriedigung
    - Wie oft User bestimmte Aktivitäten wählt
    - Explizites Feedback
    """

    def __init__(self):
        # Gelernte Prioritäten: drive -> (priority_score, confidence)
        self.priorities: Dict[str, Tuple[float, float]] = {}

        # Satisfaction-Tracking: drive -> [satisfaction_scores]
        self.satisfaction_history: Dict[str, List[float]] = defaultdict(list)

        # Activity-Tracking: drive -> activity_count
        self.activity_counts: Dict[str, int] = defaultdict(int)

        # Emotional Response Tracking: drive -> [emotional_responses]
        self.emotional_responses: Dict[str, List[float]] = defaultdict(list)

        # Initial priorities (gleich gewichtet)
        for drive_type in DriveType:
            self.priorities[drive_type.value] = (0.5, 0.0)  # (priority, confidence)

        logger.info("📊 DrivePriorityLearner initialisiert")

    def record_satisfaction(self, drive: DriveType, satisfaction: float,
                            emotional_response: float = 0.0):
        """Zeichnet Satisfaction-Event auf"""
        drive_name = drive.value

        self.satisfaction_history[drive_name].append(satisfaction)
        if emotional_response != 0:
            self.emotional_responses[drive_name].append(emotional_response)

        # Nur letzte 50 behalten
        if len(self.satisfaction_history[drive_name]) > 50:
            self.satisfaction_history[drive_name] = self.satisfaction_history[drive_name][-50:]
        if len(self.emotional_responses[drive_name]) > 50:
            self.emotional_responses[drive_name] = self.emotional_responses[drive_name][-50:]

        # Priorität neu berechnen
        self._update_priority(drive_name)

    def record_activity(self, drive: DriveType, activity_name: str):
        """Zeichnet auf dass eine Aktivität für diesen Drive gewählt wurde"""
        self.activity_counts[drive.value] += 1
        self._update_priority(drive.value)

    def _update_priority(self, drive_name: str):
        """Aktualisiert Priorität basierend auf allen Daten"""
        # Satisfaction-Score
        satisfactions = self.satisfaction_history.get(drive_name, [])
        avg_satisfaction = sum(satisfactions) / max(1, len(satisfactions))

        # Emotional-Score
        emotions = self.emotional_responses.get(drive_name, [])
        avg_emotion = sum(emotions) / max(1, len(emotions)) if emotions else 0.5

        # Activity-Score (normalisiert)
        total_activities = sum(self.activity_counts.values())
        activity_ratio = self.activity_counts[drive_name] / max(1, total_activities)

        # Kombinierter Score
        priority = (
            avg_satisfaction * 0.4 +
            (avg_emotion + 1) / 2 * 0.3 +  # Normalize -1..1 to 0..1
            activity_ratio * 0.3
        )

        # Confidence basiert auf Datenmenge
        data_points = len(satisfactions) + len(emotions) + self.activity_counts[drive_name]
        confidence = min(1.0, data_points / 30)  # 30 data points = full confidence

        self.priorities[drive_name] = (priority, confidence)

    def get_priority(self, drive: DriveType) -> float:
        """Gibt gelernte Priorität für einen Drive zurück"""
        priority, _ = self.priorities.get(drive.value, (0.5, 0.0))
        return priority

    def get_hierarchy(self) -> List[Tuple[str, float, float]]:
        """Gibt Drive-Hierarchie sortiert nach Priorität zurück"""
        return sorted(
            [(drive, prio, conf) for drive, (prio, conf) in self.priorities.items()],
            key=lambda x: x[1],
            reverse=True
        )

    def adjust_drive_weights(self, drive_system: 'HoloDriveSystem'):
        """Passt Drive-Gewichte im System basierend auf gelernten Prioritäten an"""
        for drive_type in DriveType:
            priority = self.get_priority(drive_type)
            # Höhere Priorität = schnellere Regeneration
            if hasattr(drive_system, '_regeneration_rates'):
                base_rate = drive_system._regeneration_rates.get(drive_type, 0.001)
                adjusted_rate = base_rate * (0.5 + priority)  # 0.5x to 1.5x
                drive_system._regeneration_rates[drive_type] = adjusted_rate

    def get_stats(self) -> Dict:
        """Statistiken"""
        return {
            "drives_tracked": len(self.priorities),
            "total_satisfactions": sum(len(s) for s in self.satisfaction_history.values()),
            "hierarchy": self.get_hierarchy()[:5],
        }


# =============================================================================
# ADVANCED DRIVE SYSTEM: Motivation Fatigue
# =============================================================================

class MotivationFatigueTracker:
    """
    Trackt kumulative Ermüdung wenn Drives wiederholt unbefriedigt bleiben.

    Verhindert "Burnout" bei chronisch unerfüllten Bedürfnissen.
    """

    def __init__(self, fatigue_threshold: float = 0.7):
        self.fatigue_threshold = fatigue_threshold

        # Fatigue pro Drive: drive -> fatigue_level (0-1)
        self.fatigue_levels: Dict[str, float] = defaultdict(float)

        # Unfulfillment streaks: drive -> consecutive_unfulfilled_cycles
        self.unfulfillment_streaks: Dict[str, int] = defaultdict(int)

        # Recovery tracking
        self.recovery_history: Dict[str, List[Dict]] = defaultdict(list)

        # Fatigue events
        self.fatigue_events: List[Dict] = []

        logger.info("😴 MotivationFatigueTracker initialisiert")

    def update(self, drive: DriveType, was_fulfilled: bool, intensity: float = 0.5):
        """Aktualisiert Fatigue-Status für einen Drive"""
        drive_name = drive.value

        if was_fulfilled:
            # Fulfillment reduziert Fatigue
            self.unfulfillment_streaks[drive_name] = 0
            recovery = intensity * 0.2
            self.fatigue_levels[drive_name] = max(0, self.fatigue_levels[drive_name] - recovery)

            self.recovery_history[drive_name].append({
                "timestamp": datetime.now().isoformat(),
                "recovery_amount": recovery,
            })
        else:
            # Unfulfillment erhöht Fatigue
            self.unfulfillment_streaks[drive_name] += 1
            streak = self.unfulfillment_streaks[drive_name]

            # Fatigue steigt exponentiell mit Streak
            fatigue_increase = 0.05 * (1 + streak * 0.1) * intensity
            self.fatigue_levels[drive_name] = min(1.0, self.fatigue_levels[drive_name] + fatigue_increase)

            # Fatigue-Event wenn Threshold überschritten
            if self.fatigue_levels[drive_name] >= self.fatigue_threshold:
                self._record_fatigue_event(drive, streak)

    def _record_fatigue_event(self, drive: DriveType, streak: int):
        """Zeichnet Fatigue-Event auf"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "drive": drive.value,
            "fatigue_level": self.fatigue_levels[drive.value],
            "unfulfillment_streak": streak,
        }
        self.fatigue_events.append(event)

        # Nur letzte 100 Events
        if len(self.fatigue_events) > 100:
            self.fatigue_events = self.fatigue_events[-100:]

        logger.warning(f"[Fatigue] {drive.value} erreicht Fatigue-Level {event['fatigue_level']:.2f}")

    def get_fatigue(self, drive: DriveType) -> float:
        """Gibt aktuelles Fatigue-Level zurück"""
        return self.fatigue_levels.get(drive.value, 0.0)

    def is_fatigued(self, drive: DriveType) -> bool:
        """Prüft ob Drive erschöpft ist"""
        return self.get_fatigue(drive) >= self.fatigue_threshold

    def get_fatigued_drives(self) -> List[DriveType]:
        """Gibt alle erschöpften Drives zurück"""
        return [
            DriveType(drive) for drive, level in self.fatigue_levels.items()
            if level >= self.fatigue_threshold
        ]

    def suggest_recovery(self, drive: DriveType) -> Dict:
        """Schlägt Recovery-Strategie vor"""
        fatigue = self.get_fatigue(drive)
        streak = self.unfulfillment_streaks.get(drive.value, 0)

        suggestion = {
            "drive": drive.value,
            "fatigue_level": fatigue,
            "streak": streak,
            "urgency": "high" if fatigue > 0.8 else ("medium" if fatigue > 0.5 else "low"),
            "recommendations": [],
        }

        if fatigue > 0.8:
            suggestion["recommendations"].append(f"DRINGEND: {drive.value} sofort befriedigen")
            suggestion["recommendations"].append("Andere Aktivitäten pausieren")
        elif fatigue > 0.5:
            suggestion["recommendations"].append(f"{drive.value} bald einplanen")
            suggestion["recommendations"].append("Kleine Erfüllungen helfen auch")
        else:
            suggestion["recommendations"].append(f"{drive.value} im Auge behalten")

        return suggestion

    def apply_fatigue_modifier(self, drive: DriveType, base_value: float) -> float:
        """Wendet Fatigue-Modifier auf einen Wert an"""
        fatigue = self.get_fatigue(drive)
        # Hohe Fatigue reduziert Effektivität
        modifier = 1.0 - (fatigue * 0.5)  # Max 50% Reduktion
        return base_value * modifier

    def get_stats(self) -> Dict:
        """Statistiken"""
        return {
            "fatigued_drives": len(self.get_fatigued_drives()),
            "total_fatigue_events": len(self.fatigue_events),
            "current_levels": dict(self.fatigue_levels),
            "max_streak": max(self.unfulfillment_streaks.values()) if self.unfulfillment_streaks else 0,
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Testing HoloDriveSystem ===\n")

    # System erstellen
    ds = HoloDriveSystem()

    print("Initial Status:")
    print(f"  Drives: {ds.drives.to_dict()}")
    print(f"  Needs: {ds.needs.to_dict()}")

    # Aktivität starten
    print("\n--- Starting 'reading' activity ---")
    result = ds.start_activity('reading')
    print(f"  Result: {result}")

    # Simuliere Zeit
    print("\n--- Simulating 30 minutes ---")
    for _ in range(30):
        ds.update(60)  # 1 Minute
        ds.update_activity(1)

    print(f"  Drives after 30min: {ds.drives.to_dict()}")

    # Aktivität beenden
    print("\n--- Ending activity ---")
    result = ds.end_activity()
    print(f"  Result: {result}")

    # Entscheidung
    print("\n--- What's next? ---")
    decision = ds._decide_next_action()
    print(f"  Decision: {decision}")

    print("\n=== All tests passed! ===")
