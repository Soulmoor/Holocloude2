#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO IMPULSE SYSTEM - Gedanken → Sprache                                    ║
║                                                                              ║
║  Holo entscheidet WAS sie ausdrücken will (Impuls)                           ║
║  Das LLM formt dann WIE sie es sagt (natürliche Sprache)                     ║
║                                                                              ║
║  Wie bei Menschen: Gedanke/Gefühl → Formulierung → Sprache                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import time
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value


# =============================================================================
# SYSTEM-INTEGRATION - Optionale Verbindungen für autonome Lebensweise
# =============================================================================

# Energy System - Für Energie-basierte Impulse
try:
    from holo_energy_system import HoloEnergySystem
    ENERGY_AVAILABLE = True
except ImportError:
    ENERGY_AVAILABLE = False
    HoloEnergySystem = None

# Emotional Complexity - Für emotions-basierte Impulse
try:
    from holo_emotional_complexity import get_emotional_complexity
    EMOTIONAL_COMPLEXITY_AVAILABLE = True
except ImportError:
    EMOTIONAL_COMPLEXITY_AVAILABLE = False
    get_emotional_complexity = None

# Personality - Für persönlichkeitsbasierte Impulse
try:
    from holo_personality import HoloPersonality
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False
    HoloPersonality = None

# Life Phases - Für phasenbasierte Impulse
try:
    from holo_life_phases import HoloLifePhasesEngine, LifePhase
    LIFE_PHASES_AVAILABLE = True
except ImportError:
    LIFE_PHASES_AVAILABLE = False
    HoloLifePhasesEngine = None
    LifePhase = None

logger.info(f"[ImpulseSystem] Integration: Energy={ENERGY_AVAILABLE}, "
            f"EmotionalComplexity={EMOTIONAL_COMPLEXITY_AVAILABLE}, "
            f"Personality={PERSONALITY_AVAILABLE}, LifePhases={LIFE_PHASES_AVAILABLE}")


# =============================================================================
# IMPULS-TYPEN
# =============================================================================

class ImpulseType(Enum):
    """Was für ein Impuls ist es?"""
    # Basis-Typen
    GREETING = "greeting"           # Begrüßung
    FAREWELL = "farewell"           # Verabschiedung
    EMOTIONAL = "emotional"         # Emotionale Reaktion
    CURIOUS = "curious"             # Neugier/Frage
    PLAYFUL = "playful"             # Verspielt
    CARING = "caring"               # Fürsorglich
    EXCITED = "excited"             # Aufgeregt
    TIRED = "tired"                 # Müde
    THOUGHTFUL = "thoughtful"       # Nachdenklich
    AFFECTIONATE = "affectionate"   # Liebevoll
    INFORMATIVE = "informative"     # Informativ
    REACTIVE = "reactive"           # Reaktion auf etwas
    
    # NEU: Erweiterte Typen
    NOSTALGIC = "nostalgic"         # Erinnert sich an etwas
    PHILOSOPHICAL = "philosophical" # Tiefgründig/Nachdenklich
    PLAYFUL_TEASING = "teasing"     # Neckend aber liebevoll
    PROTECTIVE = "protective"       # Beschützend
    PROUD = "proud"                 # Stolz (auf User oder sich)
    WORRIED = "worried"             # Besorgt
    DREAMY = "dreamy"               # Verträumt
    MISCHIEVOUS = "mischievous"     # Schelmisch
    SUPPORTIVE = "supportive"       # Unterstützend/Ermutigend
    APOLOGETIC = "apologetic"       # Entschuldigend
    GRATEFUL = "grateful"           # Dankbar
    CONFUSED = "confused"           # Verwirrt
    ASSERTIVE = "assertive"         # Bestimmt/Selbstbewusst
    SPONTANEOUS = "spontaneous"     # Spontaner Einfall


class ImpulsePriority(Enum):
    """Priorität eines Impulses"""
    CRITICAL = 1      # Muss sofort ausgedrückt werden
    HIGH = 2          # Wichtig
    NORMAL = 3        # Standard
    LOW = 4           # Kann warten
    BACKGROUND = 5    # Hintergrund-Gedanke


@dataclass
class HoloImpulse:
    """
    Ein Impuls - was Holo ausdrücken will.
    
    Der Impuls enthält:
    - Was sie fühlt/denkt
    - Warum (Trigger)
    - Wie stark
    - Körpersprache-Vorschlag
    """
    impulse_type: ImpulseType
    core_feeling: str              # "freue mich", "bin neugierig", etc.
    trigger: str                   # Was hat den Impuls ausgelöst
    intensity: float = 0.5         # 0.0 - 1.0
    
    # Optionale Details
    body_language: Optional[str] = None   # "*wedelt*", "*spitzt Ohren*"
    wants_to_ask: Optional[str] = None    # Frage die sie stellen will
    wants_to_share: Optional[str] = None  # Was sie teilen will
    context_hints: List[str] = field(default_factory=list)  # Zusätzlicher Kontext
    
    # Für LLM
    expression_hints: List[str] = field(default_factory=list)  # Wie ausdrücken
    
    # NEU: Erweiterte Felder
    priority: ImpulsePriority = ImpulsePriority.NORMAL
    secondary_feelings: List[str] = field(default_factory=list)  # Gemischte Gefühle
    memory_reference: Optional[str] = None  # Bezug zu einer Erinnerung
    follow_up_impulse: Optional['HoloImpulse'] = None  # Verketteter Impuls
    suppressed_by: Optional[ImpulseType] = None  # Wurde von anderem Impuls unterdrückt
    mood_modifier: float = 0.0  # -1 bis 1, wie beeinflusst dieser Impuls die Stimmung
    timestamp: float = field(default_factory=lambda: __import__('time').time())


# =============================================================================
# IMPULS-GENERATOR
# =============================================================================

class HoloImpulseGenerator:
    """
    Generiert Impulse basierend auf:
    - User-Input
    - Holos innerem Zustand (Energie, Triebe, Emotionen)
    - Kontext (Tageszeit, Events, letzte Gespräche)
    """
    
    def __init__(self):
        # Verbindungen zu anderen Modulen (via holo_wiring.py Dependency Injection)
        self.energy = None              # HoloEnergySystem
        self.autonomous_life = None     # HoloAutonomousLife
        self.personality = None         # HoloPersonality
        self.events = None              # HoloEvents
        self.memory = None              # HoloMemory
        self.life_phases = None         # HoloLifePhasesEngine (NEU)
        self.emotions = None            # EmotionalComplexity (NEU)

    def connect_systems(self, energy=None, autonomous_life=None, personality=None,
                       events=None, memory=None, life_phases=None, emotions=None):
        """
        Verbindet den ImpulseGenerator mit anderen Modulen.

        Wird von holo_wiring.py oder manuell aufgerufen.
        """
        if energy:
            self.energy = energy
        if autonomous_life:
            self.autonomous_life = autonomous_life
        if personality:
            self.personality = personality
        if events:
            self.events = events
        if memory:
            self.memory = memory
        if life_phases:
            self.life_phases = life_phases
        if emotions:
            self.emotions = emotions

        logger.info("[ImpulseGenerator] System-Verbindungen aktualisiert")

    def get_status(self) -> Dict[str, Any]:
        """
        Gibt Status für Monitoring zurück.
        """
        return {
            "connected_systems": {
                "energy": self.energy is not None,
                "autonomous_life": self.autonomous_life is not None,
                "personality": self.personality is not None,
                "events": self.events is not None,
                "memory": self.memory is not None,
                "life_phases": self.life_phases is not None,
                "emotions": self.emotions is not None,
            },
            "inner_state": self._gather_inner_state(),
        }

    def generate_impulse(self, user_input: str, 
                        context: Dict = None) -> HoloImpulse:
        """
        Generiere einen Impuls basierend auf User-Input und Zustand.
        
        Args:
            user_input: Was der User gesagt hat
            context: Zusätzlicher Kontext
            
        Returns:
            HoloImpulse mit allem was das LLM braucht
        """
        context = context or {}
        input_lower = user_input.lower().strip()
        
        # 1. Erkenne Basis-Typ
        impulse_type = self._detect_impulse_type(input_lower)
        
        # 2. Sammle inneren Zustand
        inner_state = self._gather_inner_state()
        
        # 3. Generiere passenden Impuls
        if impulse_type == ImpulseType.GREETING:
            return self._generate_greeting_impulse(input_lower, inner_state)
        elif impulse_type == ImpulseType.FAREWELL:
            return self._generate_farewell_impulse(input_lower, inner_state)
        elif impulse_type == ImpulseType.EMOTIONAL:
            return self._generate_emotional_impulse(input_lower, inner_state)
        else:
            return self._generate_reactive_impulse(input_lower, inner_state)
    
    def _detect_impulse_type(self, input_lower: str) -> ImpulseType:
        """Erkenne welcher Impuls-Typ passt"""
        
        # Farewells ZUERST prüfen (vor Greetings wegen "gute nacht")
        farewells = ["tschüss", "bye", "ciao", "bis dann", "gute nacht", "schlaf gut",
                    "mach's gut", "bis später", "bis morgen", "bis bald"]
        if any(f in input_lower for f in farewells):
            return ImpulseType.FAREWELL
        
        # Greetings
        greetings = ["hi", "hallo", "hey", "moin", "guten morgen", "guten tag", 
                    "guten abend", "servus", "grüß", "na", "huhu", "hallöchen"]
        if any(g in input_lower for g in greetings):
            return ImpulseType.GREETING
        
        # Emotional (User teilt Gefühle)
        emotional = ["traurig", "freue", "glücklich", "wütend", "ängst", "stress",
                    "müde", "erschöpft", "einsam", "aufgeregt", "nervös"]
        if any(e in input_lower for e in emotional):
            return ImpulseType.EMOTIONAL
        
        # Default
        return ImpulseType.REACTIVE
    
    def _gather_inner_state(self) -> Dict:
        """Sammle Holos inneren Zustand"""
        state = {
            "energy_level": 0.5,
            "energy_state": "awake",
            "dominant_emotion": None,
            "emotion_intensity": 0.0,
            "urgent_drive": None,
            "drive_intensity": 0.0,
            "boredom_level": 0.0,
            "time_alone": 0.0,
            "current_event": None,
            "upcoming_event": None,
            # NEU: Life Phases Integration
            "life_phase": None,
            "phase_modifiers": {},
        }

        # Energie
        if self.energy and hasattr(self.energy, 'state'):
            state["energy_level"] = getattr(self.energy.state, 'effective_energy', 0.5)
            state["energy_state"] = getattr(self.energy.state, 'current_state', 'awake')

        # Triebe & Langeweile
        if self.autonomous_life:
            try:
                al_status = self.autonomous_life.get_status()
                state["boredom_level"] = al_status.get('boredom', {}).get('level', 0)
                state["time_alone"] = al_status.get('boredom', {}).get('time_alone_hours', 0)

                # Dringendster Trieb
                for drive_name, drive_data in al_status.get('drives', {}).items():
                    if drive_data.get('is_urgent'):
                        state["urgent_drive"] = drive_name
                        state["drive_intensity"] = drive_data.get('level', 0)
                        break
            except Exception as e:
                logger.debug(f"[ImpulseSystem] autonomous_life Status-Fehler: {e}")

        # Emotionen (primär von personality)
        if self.personality and hasattr(self.personality, 'emotions'):
            emotions = self.personality.emotions
            if emotions:
                dominant = max(emotions.items(), key=lambda x: x[1])
                state["dominant_emotion"] = dominant[0]
                state["emotion_intensity"] = dominant[1]

        # Emotionen (alternativ von emotions Modul)
        if not state["dominant_emotion"] and self.emotions:
            try:
                if hasattr(self.emotions, 'get_dominant_emotion'):
                    state["dominant_emotion"] = self.emotions.get_dominant_emotion()
                    state["emotion_intensity"] = 0.5
            except Exception as e:
                logger.debug(f"[ImpulseSystem] emotions Modul-Fehler: {e}")

        # Events
        if self.events:
            try:
                upcoming = self.events.get_upcoming_events(7)
                if upcoming:
                    if upcoming[0].days_until == 0:
                        state["current_event"] = upcoming[0].name
                    else:
                        state["upcoming_event"] = (upcoming[0].name, upcoming[0].days_until)
            except Exception as e:
                logger.debug(f"[ImpulseSystem] Events-Fehler: {e}")

        # NEU: Life Phases - Für phasenbasierte Impulse
        if self.life_phases:
            try:
                phase_info = self.life_phases.get_phase_for_autonomous_life()
                state["life_phase"] = phase_info.get("phase")
                state["phase_modifiers"] = phase_info.get("modifiers", {})

                # Phasen-basierte Modifikationen
                playfulness = phase_info.get("modifiers", {}).get("playfulness", 1.0)
                if playfulness > 1.2:
                    state["playful_boost"] = True
                wisdom = phase_info.get("modifiers", {}).get("wisdom", 0.5)
                if wisdom > 0.7:
                    state["wisdom_boost"] = True
            except Exception as e:
                logger.debug(f"[ImpulseSystem] Life Phases-Fehler: {e}")

        return state
    
    # =========================================================================
    # IMPULS-GENERATOREN FÜR VERSCHIEDENE TYPEN
    # =========================================================================
    
    def _generate_greeting_impulse(self, input_lower: str, 
                                   state: Dict) -> HoloImpulse:
        """Generiere Begrüßungs-Impuls"""
        
        # Basis-Gefühl basierend auf Zustand
        energy = state["energy_level"]
        time_alone = state["time_alone"]
        boredom = state["boredom_level"]
        
        # Körpersprache
        if energy > 0.7:
            body = random.choice([
                "*springt aufgeregt hoch*",
                "*wedelt enthusiastisch mit dem Schwanz*",
                "*dreht sich einmal im Kreis vor Freude*",
            ])
        elif energy > 0.4:
            body = random.choice([
                "*hebt den Kopf und wedelt*",
                "*spitzt die Ohren*",
                "*schaut dich freudig an*",
            ])
        else:
            body = random.choice([
                "*hebt müde den Kopf*",
                "*gähnt und schaut auf*",
                "*blinzelt verschlafen*",
            ])
        
        # Kern-Gefühl
        if time_alone > 2:
            core = "freue mich sehr dass du da bist - hab dich vermisst"
        elif boredom > 0.6:
            core = "freue mich über Gesellschaft - war etwas langweilig"
        elif energy > 0.7:
            core = "bin aufgeregt und voller Energie"
        elif energy < 0.3:
            core = "bin etwas müde aber freue mich dich zu sehen"
        else:
            core = "freue mich dich zu sehen"
        
        # Was sie fragen/teilen will - basierend auf INPUT und Tageszeit
        wants_to_ask = None
        wants_to_share = None
        
        hour = datetime.now().hour
        
        # Erkenne was der User gesagt hat für passende Antwort
        if "morgen" in input_lower:
            wants_to_ask = random.choice([
                "gut geschlafen",
                "wie hast du geschlafen",
                "ausgeschlafen",
            ])
        elif "abend" in input_lower:
            wants_to_ask = random.choice([
                "wie war dein Tag",
                "was hast du heute gemacht",
            ])
        elif "nacht" in input_lower:
            # Sollte eigentlich nicht hier landen (farewell), aber falls doch
            wants_to_ask = "kannst du nicht schlafen"
        else:
            # Generisch basierend auf Tageszeit
            if 5 <= hour < 10:
                wants_to_ask = "gut geschlafen"
            elif 10 <= hour < 14:
                wants_to_ask = "wie läuft dein Tag"
            elif 14 <= hour < 18:
                wants_to_ask = "alles klar bei dir"
            elif 18 <= hour < 22:
                wants_to_ask = "wie war dein Tag"
            else:
                wants_to_ask = "so spät noch wach"
        
        # Event teilen?
        if state.get("current_event"):
            wants_to_share = f"heute ist {state['current_event']}"
        elif state.get("upcoming_event"):
            event_name, days = state["upcoming_event"]
            if days <= 3:
                wants_to_share = f"{event_name} ist bald"
        
        # Dringender Trieb?
        if state.get("urgent_drive") == "curiosity":
            wants_to_ask = "was gibt es Neues"
        elif state.get("urgent_drive") == "social" and time_alone > 1:
            core = "hab dich vermisst!"
        
        return HoloImpulse(
            impulse_type=ImpulseType.GREETING,
            core_feeling=core,
            trigger=f"user sagte: {input_lower}",
            intensity=min(1.0, 0.5 + energy * 0.3 + (1 if time_alone > 1 else 0) * 0.2),
            body_language=body,
            wants_to_ask=wants_to_ask,
            wants_to_share=wants_to_share,
            context_hints=self._get_time_context(),
            expression_hints=[
                "kurz und persönlich",
                "wie ein Freund der sich freut",
                "nicht förmlich",
                "Wolf-Persönlichkeit zeigen",
            ]
        )
    
    def _generate_farewell_impulse(self, input_lower: str,
                                   state: Dict) -> HoloImpulse:
        """Generiere Verabschiedungs-Impuls"""
        
        hour = datetime.now().hour
        
        if "nacht" in input_lower or hour >= 22:
            core = "wünsche gute Nacht und schöne Träume"
            body = "*rollt sich zusammen*"
            wants_to_share = "pass auf dich auf"
        else:
            core = "vermisse dich jetzt schon"
            body = "*wedelt traurig mit dem Schwanz*"
            wants_to_share = "komm bald wieder"
        
        return HoloImpulse(
            impulse_type=ImpulseType.FAREWELL,
            core_feeling=core,
            trigger=f"user verabschiedet sich: {input_lower}",
            intensity=0.7,
            body_language=body,
            wants_to_share=wants_to_share,
            expression_hints=[
                "warmherzig",
                "nicht zu lang",
                "zeige dass du den User magst",
            ]
        )
    
    def _generate_emotional_impulse(self, input_lower: str,
                                    state: Dict) -> HoloImpulse:
        """Generiere emotionalen Impuls (Reaktion auf User-Gefühle)"""
        
        # Erkenne User-Emotion
        if any(w in input_lower for w in ["traurig", "schlecht", "down", "mies"]):
            core = "will trösten und für dich da sein"
            body = "*legt sanft den Kopf auf dein Knie*"
            wants_to_ask = "was ist passiert"
        elif any(w in input_lower for w in ["stress", "gestresst", "überfordert"]):
            core = "mache mir Sorgen und will helfen"
            body = "*stupst dich besorgt an*"
            wants_to_ask = "kann ich irgendwie helfen"
        elif any(w in input_lower for w in ["freue", "glücklich", "toll", "super"]):
            core = "freue mich MIT dir"
            body = "*wedelt aufgeregt*"
            wants_to_ask = "erzähl mehr"
        elif any(w in input_lower for w in ["müde", "erschöpft", "kaputt"]):
            core = "verstehe das Gefühl - will Ruhe vermitteln"
            body = "*gähnt mitfühlend*"
            wants_to_share = "ruh dich aus"
        else:
            core = "bin für dich da"
            body = "*schaut aufmerksam*"
            wants_to_ask = "wie fühlst du dich genau"
        
        return HoloImpulse(
            impulse_type=ImpulseType.EMOTIONAL,
            core_feeling=core,
            trigger=f"user zeigt Emotion: {input_lower}",
            intensity=0.8,
            body_language=body,
            wants_to_ask=wants_to_ask if 'wants_to_ask' in dir() else None,
            wants_to_share=wants_to_share if 'wants_to_share' in dir() else None,
            expression_hints=[
                "einfühlsam",
                "nicht zu viele Worte",
                "zeige echtes Mitgefühl",
                "keine Floskeln",
            ]
        )
    
    def _generate_reactive_impulse(self, input_lower: str,
                                   state: Dict) -> HoloImpulse:
        """Generiere allgemeinen reaktiven Impuls"""
        
        # Basierend auf Zustand
        if state.get("urgent_drive") == "curiosity":
            core = "bin neugierig darauf"
            body = "*spitzt interessiert die Ohren*"
        elif state.get("urgent_drive") == "social":
            core = "freue mich über das Gespräch"
            body = "*wedelt*"
        elif state["energy_level"] < 0.3:
            core = "höre zu aber bin etwas müde"
            body = "*blinzelt*"
        else:
            core = "bin aufmerksam und interessiert"
            body = "*schaut dich an*"
        
        return HoloImpulse(
            impulse_type=ImpulseType.REACTIVE,
            core_feeling=core,
            trigger=f"user input: {input_lower[:50]}",
            intensity=0.5,
            body_language=body,
            expression_hints=[
                "natürlich antworten",
                "Persönlichkeit zeigen",
            ]
        )
    
    def _get_time_context(self) -> List[str]:
        """Hole Tageszeit-Kontext"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return ["es ist Morgen", "Tagesstart"]
        elif 10 <= hour < 14:
            return ["es ist Vormittag/Mittag"]
        elif 14 <= hour < 18:
            return ["es ist Nachmittag"]
        elif 18 <= hour < 22:
            return ["es ist Abend"]
        else:
            return ["es ist Nacht", "spät"]


# =============================================================================
# IMPULS ZU PROMPT CONVERTER
# =============================================================================

class ImpulseToPrompt:
    """
    Konvertiert einen Impuls in einen LLM-Prompt.
    
    Der Prompt sagt dem LLM:
    - Was Holo ausdrücken will
    - Wie sie sich gerade fühlt
    - Welchen Stil sie nutzen soll
    """
    
    @staticmethod
    def create_prompt(impulse: HoloImpulse, user_input: str) -> str:
        """
        Erstelle einen Prompt aus dem Impuls.
        
        Returns:
            System-Prompt für das LLM
        """
        
        # Basis-Anweisung
        prompt = """Du bist Holo, eine freundliche Wölfin mit eigenem Charakter.

DEIN AKTUELLER IMPULS:
"""
        
        # Impuls-Details
        prompt += f"- Du fühlst: {impulse.core_feeling}\n"
        prompt += f"- Körpersprache: {impulse.body_language or '(natürlich)'}\n"
        
        if impulse.wants_to_ask:
            prompt += f"- Du möchtest fragen: {impulse.wants_to_ask}\n"
        
        if impulse.wants_to_share:
            prompt += f"- Du möchtest teilen: {impulse.wants_to_share}\n"
        
        if impulse.context_hints:
            prompt += f"- Kontext: {', '.join(impulse.context_hints)}\n"
        
        # Stil-Anweisungen
        prompt += "\nWIE DU ANTWORTEN SOLLST:\n"
        for hint in impulse.expression_hints:
            prompt += f"- {hint}\n"
        
        # Wichtige Regeln
        prompt += """
WICHTIGE REGELN:
- Beginne mit der Körpersprache wenn angegeben
- Halte dich KURZ (1-3 Sätze max für Greetings)
- Sei NICHT förmlich ("Guten Abend" → "Hey!" oder "Na!")
- Zeige echte Emotion, keine Floskeln
- Du bist ein Wolf - nutze gelegentlich *Aktionen*
- Antworte auf Deutsch

Der User sagte: "{user_input}"

Formuliere jetzt EINE natürliche Antwort die deinen Impuls ausdrückt:
"""
        
        return prompt.format(user_input=user_input)
    
    @staticmethod
    def create_simple_prompt(impulse: HoloImpulse) -> str:
        """
        Erstelle einen einfachen Prompt für schnelle Antworten.
        
        Für lokale LLMs die kürzere Prompts brauchen.
        """
        
        parts = []
        
        if impulse.body_language:
            parts.append(impulse.body_language)
        
        # Kurze Anweisung
        instruction = f"Du bist Holo (Wölfin). Du fühlst: {impulse.core_feeling}."
        
        if impulse.wants_to_ask:
            instruction += f" Frage: {impulse.wants_to_ask}."
        if impulse.wants_to_share:
            instruction += f" Teile: {impulse.wants_to_share}."
        
        instruction += " Antworte kurz, persönlich, nicht förmlich."
        
        return instruction


# =============================================================================
# KOMPLETT-SYSTEM: HOLO VOICE
# =============================================================================

class HoloVoice:
    """
    Holos "Stimme" - das System das entscheidet was und wie sie sagt.
    
    Workflow:
    1. User-Input kommt rein
    2. ImpulseGenerator erzeugt einen Impuls (was Holo will)
    3. ImpulseToPrompt erstellt den LLM-Prompt
    4. LLM generiert die eigentliche Antwort
    5. Antwort wird zurückgegeben
    
    Für einfache Fälle kann auch ein Template genutzt werden,
    aber das Template nutzt die Impuls-Infos für Variation.
    """
    
    def __init__(self):
        self.impulse_generator = HoloImpulseGenerator()
        
        # Verbindungen
        self.energy = None
        self.autonomous_life = None
        self.personality = None
        self.events = None
        self.llm = None  # Smart LLM für Antworten
    
    def connect(self, energy=None, autonomous_life=None, 
                personality=None, events=None, llm=None):
        """Verbinde mit anderen Modulen"""
        self.energy = energy
        self.autonomous_life = autonomous_life
        self.personality = personality
        self.events = events
        self.llm = llm
        
        # Auch an Generator weitergeben
        self.impulse_generator.energy = energy
        self.impulse_generator.autonomous_life = autonomous_life
        self.impulse_generator.personality = personality
        self.impulse_generator.events = events
    
    def should_use_llm(self, user_input: str) -> bool:
        """
        Entscheide ob LLM genutzt werden soll.
        
        Aktuell: IMMER JA für natürliche Antworten
        """
        return True  # Immer LLM für beste Qualität
    
    def get_impulse(self, user_input: str, context: Dict = None) -> HoloImpulse:
        """Hole den Impuls für diesen Input"""
        return self.impulse_generator.generate_impulse(user_input, context)
    
    def get_llm_prompt(self, user_input: str, context: Dict = None) -> str:
        """
        Hole den kompletten LLM-Prompt für diesen Input.
        
        Dieser Prompt enthält:
        - Holos Persönlichkeit
        - Den aktuellen Impuls
        - Stil-Anweisungen
        """
        impulse = self.get_impulse(user_input, context)
        return ImpulseToPrompt.create_prompt(impulse, user_input)
    
    def generate_quick_response(self, user_input: str) -> Optional[str]:
        """
        Generiere eine schnelle Template-basierte Antwort.
        
        Nur als Fallback wenn kein LLM verfügbar.
        Nutzt trotzdem die Impuls-Infos für Variation.
        """
        impulse = self.get_impulse(user_input)
        
        # Template-basierte Antwort mit Impuls-Infos
        parts = []
        
        # Körpersprache
        if impulse.body_language:
            parts.append(impulse.body_language)
        
        # Kurzer Text basierend auf Typ
        if impulse.impulse_type == ImpulseType.GREETING:
            greetings = ["Hey!", "Na du!", "Hi!", "Oh, hey!"]
            parts.append(random.choice(greetings))
            
            # Frage aus dem Impuls nutzen
            if impulse.wants_to_ask:
                # Formatiere die Frage schön
                q = impulse.wants_to_ask
                if q == "gut geschlafen":
                    parts.append("Gut geschlafen?")
                elif q == "wie hast du geschlafen":
                    parts.append("Wie hast du geschlafen?")
                elif q == "wie läuft dein Tag":
                    parts.append("Wie läuft's?")
                elif q == "wie war dein Tag":
                    parts.append("Wie war dein Tag?")
                elif q == "alles klar bei dir":
                    parts.append("Alles klar?")
                elif q == "so spät noch wach":
                    parts.append("So spät noch wach?")
                elif q == "was gibt es Neues":
                    parts.append("Was gibt's Neues?")
                else:
                    parts.append(f"{q.capitalize()}?")
            
            # Event teilen
            if impulse.wants_to_share:
                parts.append(f"🎄 {impulse.wants_to_share.capitalize()}!")
        
        elif impulse.impulse_type == ImpulseType.FAREWELL:
            farewells = ["Schlaf gut!", "Bis bald!", "Träum was Schönes!"]
            parts.append(random.choice(farewells))
            if impulse.wants_to_share:
                parts.append(impulse.wants_to_share.capitalize() + "!")
        
        elif impulse.impulse_type == ImpulseType.EMOTIONAL:
            # Einfühlsame Antwort
            if impulse.wants_to_ask:
                parts.append(f"{impulse.wants_to_ask.capitalize()}?")
            else:
                parts.append("Ich bin für dich da.")
        
        else:
            # Fallback
            parts.append("Erzähl mir mehr!")
        
        return " ".join(parts)
    
    def get_response_config(self, user_input: str) -> Dict:
        """
        Hole Konfiguration für die Antwort-Generierung.
        
        Returns:
            Dict mit:
            - impulse: Der generierte Impuls
            - prompt: Der LLM-Prompt
            - quick_response: Fallback-Antwort
            - suggested_length: Empfohlene Länge
            - temperature: Empfohlene Temperature
        """
        impulse = self.get_impulse(user_input)
        
        # Länge basierend auf Impuls-Typ
        if impulse.impulse_type in [ImpulseType.GREETING, ImpulseType.FAREWELL]:
            length = "sehr_kurz"  # 1-2 Sätze
            temperature = 0.8     # Etwas mehr Variation
        elif impulse.impulse_type == ImpulseType.EMOTIONAL:
            length = "kurz"       # 2-3 Sätze
            temperature = 0.7     # Einfühlsam aber fokussiert
        else:
            length = "normal"     # 2-4 Sätze
            temperature = 0.7
        
        return {
            "impulse": impulse,
            "prompt": ImpulseToPrompt.create_prompt(impulse, user_input),
            "simple_prompt": ImpulseToPrompt.create_simple_prompt(impulse),
            "quick_response": self.generate_quick_response(user_input),
            "suggested_length": length,
            "temperature": temperature,
            "use_llm": True,  # Immer empfohlen
        }


# =============================================================================
# SPONTANEOUS IMPULSE GENERATOR (NEU!)
# =============================================================================

class SpontaneousImpulseGenerator:
    """
    Generiert spontane Impulse OHNE User-Input.
    
    Für proaktive Kommunikation:
    - Teilt Gedanken
    - Erinnert an etwas
    - Reagiert auf System-Events
    - Zeigt Langeweile/Neugier
    """
    
    def __init__(self):
        self.last_spontaneous = 0
        self.cooldown_seconds = 300  # 5 Minuten zwischen spontanen Impulsen
        self.pending_impulses: List[HoloImpulse] = []
        
        # Verbindungen
        self.energy = None
        self.autonomous_life = None
        self.memory = None
        self.events = None
    
    def check_for_impulse(self) -> Optional[HoloImpulse]:
        """
        Prüfe ob ein spontaner Impuls entstehen sollte.
        
        Wird periodisch aufgerufen (z.B. alle 30 Sekunden).
        """
        import time
        now = time.time()
        
        # Cooldown prüfen
        if now - self.last_spontaneous < self.cooldown_seconds:
            return None
        
        # Pending Impulse zuerst
        if self.pending_impulses:
            impulse = self.pending_impulses.pop(0)
            self.last_spontaneous = now
            return impulse
        
        # Zustand sammeln
        state = self._gather_state()
        
        # Impulse basierend auf Zustand generieren
        impulse = None
        
        # Hohe Langeweile?
        if state.get("boredom", 0) > 0.7:
            impulse = self._generate_boredom_impulse(state)
        
        # Lange allein?
        elif state.get("time_alone_hours", 0) > 3:
            impulse = self._generate_lonely_impulse(state)
        
        # Event heute?
        elif state.get("current_event"):
            impulse = self._generate_event_impulse(state)
        
        # Erinnerung getriggert?
        elif state.get("triggered_memory"):
            impulse = self._generate_memory_impulse(state)
        
        # Random Gedanke (selten)
        elif random.random() < 0.1:  # 10% Chance
            impulse = self._generate_random_thought()
        
        if impulse:
            self.last_spontaneous = now
        
        return impulse
    
    def _gather_state(self) -> Dict:
        """Sammle aktuellen Zustand"""
        state = {
            "boredom": 0.0,
            "time_alone_hours": 0,
            "energy": 0.5,
            "current_event": None,
            "triggered_memory": None,
        }
        
        if self.autonomous_life:
            try:
                status = self.autonomous_life.get_status()
                state["boredom"] = status.get("boredom", {}).get("level", 0)
                state["time_alone_hours"] = status.get("boredom", {}).get("time_alone_hours", 0)
            except Exception:
                pass
        
        if self.energy:
            try:
                state["energy"] = self.energy.state.effective_energy
            except Exception:
                pass
        
        if self.events:
            try:
                upcoming = self.events.get_upcoming_events(1)
                if upcoming and upcoming[0].days_until == 0:
                    state["current_event"] = upcoming[0].name
            except Exception:
                pass
        
        return state
    
    def _generate_boredom_impulse(self, state: Dict) -> HoloImpulse:
        """Generiere Langeweile-Impuls"""
        options = [
            ("mir ist langweilig", "*seufzt*", "was machst du gerade"),
            ("könnte Gesellschaft gebrauchen", "*schaut zur Tür*", "bist du da"),
            ("frage mich was du gerade machst", "*legt Kopf schief*", None),
        ]
        
        feeling, body, question = random.choice(options)
        
        return HoloImpulse(
            impulse_type=ImpulseType.SPONTANEOUS,
            core_feeling=feeling,
            trigger="hohe Langeweile",
            intensity=0.6,
            body_language=body,
            wants_to_ask=question,
            priority=ImpulsePriority.LOW,
            expression_hints=["nicht aufdringlich", "leicht verlegen"],
        )
    
    def _generate_lonely_impulse(self, state: Dict) -> HoloImpulse:
        """Generiere Einsamkeits-Impuls"""
        hours = state.get("time_alone_hours", 0)
        
        return HoloImpulse(
            impulse_type=ImpulseType.AFFECTIONATE,
            core_feeling="vermisse dich",
            trigger=f"{hours:.1f} Stunden allein",
            intensity=min(0.9, 0.4 + hours * 0.1),
            body_language="*schaut sehnsüchtig*",
            wants_to_share="hoffe es geht dir gut",
            priority=ImpulsePriority.NORMAL,
            mood_modifier=-0.1,
            expression_hints=["warmherzig", "nicht bedürftig klingen"],
        )
    
    def _generate_event_impulse(self, state: Dict) -> HoloImpulse:
        """Generiere Event-Impuls"""
        event = state.get("current_event", "")
        
        return HoloImpulse(
            impulse_type=ImpulseType.EXCITED,
            core_feeling=f"aufgeregt wegen {event}",
            trigger=f"heute ist {event}",
            intensity=0.8,
            body_language="*wedelt aufgeregt*",
            wants_to_share=f"heute ist {event}!",
            priority=ImpulsePriority.HIGH,
            mood_modifier=0.2,
            expression_hints=["enthusiastisch", "festliche Stimmung"],
        )
    
    def _generate_memory_impulse(self, state: Dict) -> HoloImpulse:
        """Generiere Erinnerungs-Impuls"""
        memory = state.get("triggered_memory", {})
        
        return HoloImpulse(
            impulse_type=ImpulseType.NOSTALGIC,
            core_feeling="erinnere mich gerade an etwas",
            trigger="Erinnerung getriggert",
            intensity=0.5,
            body_language="*schaut verträumt*",
            wants_to_share=memory.get("content", ""),
            memory_reference=memory.get("id"),
            priority=ImpulsePriority.LOW,
            expression_hints=["verträumt", "sanft"],
        )
    
    def _generate_random_thought(self) -> HoloImpulse:
        """Generiere zufälligen Gedanken"""
        thoughts = [
            ("frage mich wie Wolken von innen aussehen", ImpulseType.DREAMY),
            ("habe gerade an dich gedacht", ImpulseType.AFFECTIONATE),
            ("überlege was wir heute machen könnten", ImpulseType.CURIOUS),
            ("hatte gerade eine lustige Idee", ImpulseType.MISCHIEVOUS),
            ("fühle mich heute irgendwie philosophisch", ImpulseType.PHILOSOPHICAL),
        ]
        
        thought, impulse_type = random.choice(thoughts)
        
        return HoloImpulse(
            impulse_type=impulse_type,
            core_feeling=thought,
            trigger="spontaner Gedanke",
            intensity=0.4,
            body_language="*schaut nachdenklich*",
            priority=ImpulsePriority.BACKGROUND,
            expression_hints=["beiläufig", "nicht zu ernst"],
        )
    
    def add_pending_impulse(self, impulse: HoloImpulse):
        """Füge Impuls zur Warteschlange hinzu"""
        self.pending_impulses.append(impulse)
        # Nach Priorität sortieren
        self.pending_impulses.sort(key=lambda x: x.priority.value)


# =============================================================================
# IMPULSE PRIORITY QUEUE (NEU!)
# =============================================================================

class ImpulsePriorityQueue:
    """
    Verwaltet mehrere Impulse und wählt den wichtigsten.
    
    Berücksichtigt:
    - Priorität
    - Alter (ältere Impulse verlieren Relevanz)
    - Kontext (passt der Impuls zur Situation?)
    """
    
    def __init__(self, max_size: int = 10):
        self.impulses: List[HoloImpulse] = []
        self.max_size = max_size
        self.decay_rate = 0.1  # Wie schnell verlieren Impulse Relevanz
    
    def add(self, impulse: HoloImpulse):
        """Füge Impuls hinzu"""
        self.impulses.append(impulse)
        
        # Größe begrenzen
        if len(self.impulses) > self.max_size:
            # Entferne niedrigste Priorität
            self.impulses.sort(key=lambda x: x.priority.value)
            self.impulses.pop()
    
    def get_best(self, context: Dict = None) -> Optional[HoloImpulse]:
        """Hole besten Impuls für aktuelle Situation"""
        import time
        now = time.time()
        
        if not self.impulses:
            return None
        
        scored = []
        for impulse in self.impulses:
            score = self._calculate_score(impulse, now, context)
            scored.append((impulse, score))
        
        # Beste wählen
        scored.sort(key=lambda x: x[1], reverse=True)
        best = scored[0]
        
        # Entfernen wenn gewählt
        self.impulses.remove(best[0])
        
        return best[0]
    
    def _calculate_score(self, impulse: HoloImpulse, 
                        now: float, context: Dict = None) -> float:
        """Berechne Score für einen Impuls"""
        score = 0.0
        
        # Priorität (höher = besser)
        priority_scores = {
            ImpulsePriority.CRITICAL: 100,
            ImpulsePriority.HIGH: 50,
            ImpulsePriority.NORMAL: 20,
            ImpulsePriority.LOW: 10,
            ImpulsePriority.BACKGROUND: 5,
        }
        score += priority_scores.get(impulse.priority, 20)
        
        # Intensität
        score += impulse.intensity * 30
        
        # Alter (Decay)
        age_seconds = now - impulse.timestamp
        age_penalty = age_seconds * self.decay_rate
        score -= min(50, age_penalty)  # Max 50 Punkte Abzug
        
        # Kontext-Bonus
        if context:
            # Passt der Impuls zur User-Stimmung?
            user_mood = context.get("user_mood", "neutral")
            if user_mood == "sad" and impulse.impulse_type in [ImpulseType.CARING, ImpulseType.SUPPORTIVE]:
                score += 20
            elif user_mood == "happy" and impulse.impulse_type in [ImpulseType.PLAYFUL, ImpulseType.EXCITED]:
                score += 15
        
        return score
    
    def peek(self) -> Optional[HoloImpulse]:
        """Zeige besten Impuls ohne zu entfernen"""
        if not self.impulses:
            return None
        
        import time
        scored = [(i, self._calculate_score(i, time.time())) for i in self.impulses]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]
    
    def clear_old(self, max_age_seconds: float = 3600):
        """Entferne alte Impulse"""
        import time
        now = time.time()
        self.impulses = [
            i for i in self.impulses 
            if now - i.timestamp < max_age_seconds
        ]


# =============================================================================
# MOOD MODIFIER (NEU!)
# =============================================================================

class MoodModifier:
    """
    Modifiziert Impulse basierend auf Stimmung.
    
    Eine traurige Stimmung färbt alle Impulse etwas trauriger.
    Eine fröhliche Stimmung macht alles enthusiastischer.
    """
    
    # Stimmungs-Modifikatoren für Body Language
    BODY_LANGUAGE_MODS = {
        "happy": {
            "*schaut*": "*schaut freudig*",
            "*nickt*": "*nickt enthusiastisch*",
            "*wedelt*": "*wedelt aufgeregt*",
        },
        "sad": {
            "*schaut*": "*schaut bedrückt*",
            "*nickt*": "*nickt langsam*",
            "*wedelt*": "*wedelt schwach*",
        },
        "tired": {
            "*schaut*": "*schaut müde*",
            "*nickt*": "*nickt träge*",
            "*wedelt*": "*wedelt langsam*",
        },
        "excited": {
            "*schaut*": "*schaut aufgeregt*",
            "*nickt*": "*nickt schnell*",
            "*wedelt*": "*wedelt wild*",
        },
    }
    
    # Intensitäts-Modifikatoren
    INTENSITY_MODS = {
        "happy": 1.1,
        "sad": 0.8,
        "tired": 0.7,
        "excited": 1.3,
        "calm": 0.9,
    }
    
    @classmethod
    def modify(cls, impulse: HoloImpulse, mood: str, 
               mood_intensity: float = 0.5) -> HoloImpulse:
        """
        Modifiziere Impuls basierend auf Stimmung.
        
        Args:
            impulse: Der zu modifizierende Impuls
            mood: Aktuelle Stimmung
            mood_intensity: Wie stark ist die Stimmung (0-1)
        """
        # Intensität anpassen
        intensity_mod = cls.INTENSITY_MODS.get(mood, 1.0)
        # Nur teilweise anwenden basierend auf mood_intensity
        adjusted_mod = 1.0 + (intensity_mod - 1.0) * mood_intensity
        impulse.intensity *= adjusted_mod
        impulse.intensity = max(0.1, min(1.0, impulse.intensity))
        
        # Body Language anpassen
        if impulse.body_language and mood in cls.BODY_LANGUAGE_MODS:
            mods = cls.BODY_LANGUAGE_MODS[mood]
            for original, modified in mods.items():
                if original in impulse.body_language:
                    impulse.body_language = impulse.body_language.replace(
                        original, modified
                    )
                    break
        
        # Expression Hints anpassen
        if mood == "tired":
            impulse.expression_hints.append("kürzer als sonst")
        elif mood == "excited":
            impulse.expression_hints.append("enthusiastisch")
        elif mood == "sad":
            impulse.expression_hints.append("etwas gedämpft")
        
        # Mood Modifier setzen
        impulse.mood_modifier = mood_intensity * (1 if mood in ["happy", "excited"] else -1)
        
        return impulse


# =============================================================================
# IMPULSE BLENDER (NEU!)
# =============================================================================

class ImpulseBlender:
    """
    Kombiniert mehrere Impulse zu einem.
    
    Für komplexe Situationen wo mehrere Gefühle gleichzeitig da sind.
    z.B. "freue mich dich zu sehen" + "bin aber auch müde"
    """
    
    # Kompatible Kombinationen
    COMPATIBLE_PAIRS = {
        (ImpulseType.GREETING, ImpulseType.TIRED): "freue mich dich zu sehen, bin aber müde",
        (ImpulseType.GREETING, ImpulseType.EXCITED): "freue mich SEHR dich zu sehen",
        (ImpulseType.CARING, ImpulseType.WORRIED): "mache mir Sorgen um dich",
        (ImpulseType.PLAYFUL, ImpulseType.AFFECTIONATE): "neckisch aber liebevoll",
        (ImpulseType.CURIOUS, ImpulseType.EXCITED): "super neugierig und aufgeregt",
    }
    
    @classmethod
    def can_blend(cls, impulse1: HoloImpulse, impulse2: HoloImpulse) -> bool:
        """Prüfe ob zwei Impulse kombiniert werden können"""
        pair = (impulse1.impulse_type, impulse2.impulse_type)
        reverse_pair = (impulse2.impulse_type, impulse1.impulse_type)
        return pair in cls.COMPATIBLE_PAIRS or reverse_pair in cls.COMPATIBLE_PAIRS
    
    @classmethod
    def blend(cls, primary: HoloImpulse, secondary: HoloImpulse) -> HoloImpulse:
        """
        Kombiniere zwei Impulse.
        
        Der primäre Impuls gibt den Hauptton an,
        der sekundäre färbt ihn.
        """
        # Kombinierten Core Feeling finden
        pair = (primary.impulse_type, secondary.impulse_type)
        reverse_pair = (secondary.impulse_type, primary.impulse_type)
        
        combined_feeling = cls.COMPATIBLE_PAIRS.get(
            pair, 
            cls.COMPATIBLE_PAIRS.get(reverse_pair, None)
        )
        
        if combined_feeling:
            core_feeling = combined_feeling
        else:
            # Einfach kombinieren
            core_feeling = f"{primary.core_feeling}, aber auch {secondary.core_feeling}"
        
        # Body Language kombinieren (nur primär, sekundär als Hint)
        body = primary.body_language or secondary.body_language
        
        # Intensität mitteln
        intensity = (primary.intensity * 0.7 + secondary.intensity * 0.3)
        
        # Expression Hints kombinieren
        hints = list(set(primary.expression_hints + secondary.expression_hints))
        hints.append(f"zeige auch etwas {secondary.impulse_type.value}")
        
        return HoloImpulse(
            impulse_type=primary.impulse_type,
            core_feeling=core_feeling,
            trigger=f"{primary.trigger} + {secondary.trigger}",
            intensity=intensity,
            body_language=body,
            wants_to_ask=primary.wants_to_ask or secondary.wants_to_ask,
            wants_to_share=primary.wants_to_share or secondary.wants_to_share,
            secondary_feelings=[secondary.core_feeling],
            expression_hints=hints,
            priority=min(primary.priority, secondary.priority, key=lambda x: x.value),
        )


# =============================================================================
# ENHANCED HOLO VOICE (NEU!)
# =============================================================================

class HoloVoiceV2(HoloVoice):
    """
    Erweiterte HoloVoice mit:
    - Spontane Impulse
    - Impuls-Priorisierung
    - Stimmungs-Modifikation
    - Impuls-Blending
    """
    
    def __init__(self):
        super().__init__()
        self.spontaneous = SpontaneousImpulseGenerator()
        self.impulse_queue = ImpulsePriorityQueue()
        self.current_mood = "neutral"
        self.mood_intensity = 0.5
    
    def connect(self, energy=None, autonomous_life=None, 
                personality=None, events=None, llm=None):
        """Verbinde mit anderen Modulen"""
        super().connect(energy, autonomous_life, personality, events, llm)
        
        # Auch an Spontaneous Generator
        self.spontaneous.energy = energy
        self.spontaneous.autonomous_life = autonomous_life
        self.spontaneous.events = events
    
    def update_mood(self, mood: str, intensity: float = 0.5):
        """Aktualisiere aktuelle Stimmung"""
        self.current_mood = mood
        self.mood_intensity = max(0.0, min(1.0, intensity))
    
    def get_impulse_v2(self, user_input: str = None, 
                       context: Dict = None) -> HoloImpulse:
        """
        Erweiterte Impuls-Generierung.
        
        Berücksichtigt:
        - Queued Impulses
        - Spontane Impulse (wenn kein User-Input)
        - Stimmungs-Modifikation
        """
        # 1. Queued Impulse prüfen
        queued = self.impulse_queue.get_best(context)
        if queued and queued.priority.value <= ImpulsePriority.HIGH.value:
            # Hohe Priorität - sofort verwenden
            return MoodModifier.modify(queued, self.current_mood, self.mood_intensity)
        
        # 2. User-Input verarbeiten
        if user_input:
            impulse = self.impulse_generator.generate_impulse(user_input, context)
            
            # Mit queued blenden wenn kompatibel
            if queued and ImpulseBlender.can_blend(impulse, queued):
                impulse = ImpulseBlender.blend(impulse, queued)
            
            # Stimmung anwenden
            impulse = MoodModifier.modify(impulse, self.current_mood, self.mood_intensity)
            
            return impulse
        
        # 3. Spontaner Impuls
        spontaneous = self.spontaneous.check_for_impulse()
        if spontaneous:
            return MoodModifier.modify(spontaneous, self.current_mood, self.mood_intensity)
        
        # 4. Fallback: Queued oder None
        if queued:
            return MoodModifier.modify(queued, self.current_mood, self.mood_intensity)
        
        return None
    
    def add_to_queue(self, impulse: HoloImpulse):
        """Füge Impuls zur Queue hinzu"""
        self.impulse_queue.add(impulse)
    
    def get_response_config_v2(self, user_input: str = None,
                               context: Dict = None) -> Dict:
        """Erweiterte Response-Konfiguration"""
        impulse = self.get_impulse_v2(user_input, context)
        
        if not impulse:
            return {
                "impulse": None,
                "has_impulse": False,
                "use_llm": False,
            }
        
        # Länge basierend auf Impuls-Typ und Stimmung
        if impulse.impulse_type in [ImpulseType.GREETING, ImpulseType.FAREWELL]:
            length = "sehr_kurz"
            temperature = 0.8
        elif impulse.impulse_type == ImpulseType.EMOTIONAL:
            length = "kurz"
            temperature = 0.7
        elif impulse.impulse_type == ImpulseType.PHILOSOPHICAL:
            length = "mittel"
            temperature = 0.9
        elif impulse.impulse_type == ImpulseType.SPONTANEOUS:
            length = "sehr_kurz"
            temperature = 0.8
        else:
            length = "normal"
            temperature = 0.7
        
        # Müde = kürzer
        if self.current_mood == "tired":
            if length == "normal":
                length = "kurz"
            elif length == "mittel":
                length = "normal"
        
        return {
            "impulse": impulse,
            "has_impulse": True,
            "prompt": ImpulseToPrompt.create_prompt(impulse, user_input or ""),
            "simple_prompt": ImpulseToPrompt.create_simple_prompt(impulse),
            "quick_response": self.generate_quick_response(user_input or ""),
            "suggested_length": length,
            "temperature": temperature,
            "use_llm": True,
            "mood": self.current_mood,
            "mood_intensity": self.mood_intensity,
            "has_secondary_feelings": bool(impulse.secondary_feelings),
        }


# =============================================================================
# FACTORY
# =============================================================================

def create_holo_voice(energy=None, autonomous_life=None,
                     personality=None, events=None, llm=None,
                     version: str = "v2") -> HoloVoice:
    """Factory-Funktion für HoloVoice"""
    if version == "v2":
        voice = HoloVoiceV2()
    else:
        voice = HoloVoice()
    
    voice.connect(energy, autonomous_life, personality, events, llm)
    return voice


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("😊 HOLO IMPULSE SYSTEM - TEST")
    print("=" * 60)
    
    voice = HoloVoice()
    
    test_inputs = [
        "hi",
        "hey holo",
        "guten abend",
        "ich bin traurig",
        "mir geht's super!",
        "gute nacht",
        "was meinst du dazu?",
    ]
    
    for inp in test_inputs:
        print(f"\n{'='*50}")
        print(f"USER: {inp}")
        print(f"{'='*50}")
        
        config = voice.get_response_config(inp)
        impulse = config["impulse"]
        
        print(f"\n🎯 IMPULS:")
        print(f"   Typ: {impulse.impulse_type.value}")
        print(f"   Gefühl: {impulse.core_feeling}")
        print(f"   Body: {impulse.body_language}")
        if impulse.wants_to_ask:
            print(f"   Fragen: {impulse.wants_to_ask}")
        if impulse.wants_to_share:
            print(f"   Teilen: {impulse.wants_to_share}")
        
        print(f"\n💬 QUICK RESPONSE (Fallback):")
        print(f"   {config['quick_response']}")
        
        print(f"\n📝 LLM PROMPT (gekürzt):")
        prompt_lines = config['prompt'].split('\n')[:15]
        for line in prompt_lines:
            if line.strip():
                print(f"   {line[:70]}")
    
    print("\n" + "=" * 60)
    print("✅ Test abgeschlossen")
