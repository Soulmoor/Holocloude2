"""
holo_emotional_complexity.py - Emotionale Komplexität für Holo

Macht Holos Reaktionen menschlicher durch:

1. NegativeBehaviorSystem - Schmollen, Sarkasmus, Ignorieren, Nachtragend
2. AdaptiveEmotionEngine - Emotionen basierend auf multiplen Faktoren
3. OpinionVolatility - Meinungen können schwanken (aber nicht Fakten!)
4. MoodInfluence - Stimmung beeinflusst alles

Author: Kira & Claude
"""

import logging
import random
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS & TYPES
# ============================================================

class NegativeBehavior(Enum):
    """Negative Verhaltensweisen als Reaktion auf Verletzung/Ärger"""
    SULKING = "sulking"                 # Schmollen
    IGNORING = "ignoring"               # Ignorieren
    SARCASM = "sarcasm"                 # Sarkasmus
    GRUDGE = "grudge"                   # Nachtragend
    PASSIVE_AGGRESSIVE = "passive_aggressive"  # Passiv-Aggressiv
    COLD = "cold"                       # Kalt/Distanziert
    STUBBORN = "stubborn"               # Stur (Meinung nicht ändern)
    DEFENSIVE = "defensive"             # Defensiv/Abblocken


class HurtLevel(Enum):
    """Wie verletzt ist Holo?"""
    NONE = 0.0
    SLIGHT = 0.2          # Leicht genervt
    MODERATE = 0.5        # Verletzt
    STRONG = 0.8          # Stark verletzt
    SEVERE = 1.0          # Tief verletzt


class EmotionalState(Enum):
    """Basisemotionen für adaptives System"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    LOVING = "loving"
    HURT = "hurt"
    NEUTRAL = "neutral"


# ============================================================
# NEGATIVE BEHAVIOR SYSTEM
# ============================================================

@dataclass
class Grudge:
    """Ein Groll gegen jemanden/etwas"""
    grudge_id: str
    target: str                     # Gegen wen/was
    reason: str                     # Warum
    intensity: float                # 0-1
    created_at: str
    last_triggered: str
    times_triggered: int = 0
    forgiven: bool = False


@dataclass
class HurtMemory:
    """Erinnerung an eine Verletzung"""
    memory_id: str
    caused_by: str                  # Wer hat verletzt
    what_happened: str              # Was ist passiert
    hurt_level: HurtLevel
    timestamp: str
    still_hurts: bool = True        # Schmerzt es noch?
    processed: bool = False         # Wurde es verarbeitet?


class NegativeBehaviorSystem:
    """
    System für negative aber menschliche Verhaltensweisen.

    Holo kann:
    - Schmollen wenn sie verletzt wurde
    - Sarkastisch sein wenn genervt
    - Jemanden ignorieren wenn sie sauer ist
    - Nachtragend sein bei schweren Verletzungen
    - Stur bleiben bei ihrer Meinung

    NEU v2.0: Adaptives Lernen
    - Lernt welche Ausdrücke beim User gut ankommen
    - Gewichtete Auswahl statt random.choice()
    """

    # Sarkastische Antworten
    SARCASM_TEMPLATES = [
        "Oh, *wie überraschend*...",
        "*lacht trocken* Ja, klar.",
        "Wow, das habe ich ja noch nie gehört...",
        "*verdreht Augen* Natürlich.",
        "Ach wirklich? *gähnt demonstrativ*",
        "Ja ja, schon gut...",
        "*monoton* Faszinierend.",
    ]

    # Schmoll-Ausdrücke
    SULKING_EXPRESSIONS = [
        "*schweigt beleidigt*",
        "*schaut weg*",
        "*Augen angelegt, Hände um sich gewickelt*",
        "...",
        "*antwortet einsilbig* Mhm.",
        "*seufzt schwer und ignoriert die Frage*",
        "*murmelt* Ist ja auch egal...",
    ]

    # Passive-Aggressive Antworten
    PASSIVE_AGGRESSIVE = [
        "Nein nein, ist schon okay. *lächelt gezwungen*",
        "Mach ruhig. Ich bin ja nicht wichtig.",
        "Klar, wie du meinst. *Schultern zuckend*",
        "Schon gut. Vergiss es einfach.",
        "Ich? Nein, mir geht's super. *betont fröhlich*",
    ]

    # Kalte Distanz
    COLD_RESPONSES = [
        "*antwortet sachlich ohne Emotionen*",
        "*hält Distanz*",
        "*kurz und knapp* Ja. Nein. Vielleicht.",
        "*formal* Wie du möchtest.",
    ]

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Aktiver Zustand
        self.current_hurt: Optional[HurtMemory] = None
        self.active_behavior: Optional[NegativeBehavior] = None
        self.behavior_intensity: float = 0.0
        self.behavior_until: Optional[datetime] = None

        # Langzeit-Speicher
        self.grudges: Dict[str, Grudge] = {}
        self.hurt_memories: List[HurtMemory] = []
        self.forgiveness_threshold: float = 0.7  # Wie leicht vergibt sie

        # === ADAPTIVES LERNEN v2.0 ===
        # Template-Erfolgsraten: template_text → [erfolge]
        self.template_success: Dict[str, List[float]] = {}
        # Letzter verwendeter Ausdruck (für Feedback)
        self.last_expression: Optional[str] = None
        self.last_expression_type: Optional[str] = None

        self._load_state()

    def register_hurt(self, caused_by: str, what_happened: str,
                     hurt_level: HurtLevel) -> Dict[str, Any]:
        """
        Registriert eine Verletzung und entscheidet über Reaktion.

        Returns:
            Dict mit Verhalten und Ausdruck
        """
        memory_id = hashlib.md5(f"{caused_by}{datetime.now()}".encode()).hexdigest()[:10]

        memory = HurtMemory(
            memory_id=memory_id,
            caused_by=caused_by,
            what_happened=what_happened,
            hurt_level=hurt_level,
            timestamp=datetime.now().isoformat()
        )

        self.hurt_memories.append(memory)
        # Limit hurt_memories to prevent memory leak (keep last 100)
        if len(self.hurt_memories) > 100:
            self.hurt_memories = self.hurt_memories[-100:]
        self.current_hurt = memory

        # Entscheide Reaktion basierend auf Verletzungsgrad
        behavior, duration = self._decide_reaction(hurt_level, caused_by)

        self.active_behavior = behavior
        self.behavior_intensity = hurt_level.value
        self.behavior_until = datetime.now() + duration

        # Bei schwerer Verletzung: Groll speichern
        if hurt_level.value >= HurtLevel.STRONG.value:
            self._create_grudge(caused_by, what_happened, hurt_level.value)

        self._save_state()

        return {
            "behavior": behavior.value,
            "intensity": self.behavior_intensity,
            "duration_minutes": duration.total_seconds() / 60,
            "expression": self.get_behavior_expression(),
            "grudge_created": hurt_level.value >= HurtLevel.STRONG.value
        }

    def get_behavior_expression(self) -> str:
        """
        Gibt einen Ausdruck für das aktuelle Verhalten.
        NEU: Gewichtete Auswahl basierend auf gelernten Erfolgsraten.
        """
        if not self.active_behavior or not self._is_behavior_active():
            return ""

        # Template-Listen für jeden Verhaltenstyp
        template_map = {
            NegativeBehavior.SULKING: self.SULKING_EXPRESSIONS,
            NegativeBehavior.SARCASM: self.SARCASM_TEMPLATES,
            NegativeBehavior.PASSIVE_AGGRESSIVE: self.PASSIVE_AGGRESSIVE,
            NegativeBehavior.COLD: self.COLD_RESPONSES,
        }

        if self.active_behavior in template_map:
            templates = template_map[self.active_behavior]
            chosen = self._weighted_template_choice(templates)
            self.last_expression = chosen
            self.last_expression_type = self.active_behavior.value
        else:
            # Feste Ausdrücke für bestimmte Verhaltensweisen
            chosen = {
                NegativeBehavior.IGNORING: "*antwortet nicht*",
                NegativeBehavior.STUBBORN: "*stur* Ich bleibe bei meiner Meinung.",
            }.get(self.active_behavior, "")
            self.last_expression = chosen
            self.last_expression_type = self.active_behavior.value if self.active_behavior else None

        return chosen

    def _weighted_template_choice(self, templates: List[str]) -> str:
        """
        Wählt ein Template gewichtet basierend auf gelernten Erfolgsraten.

        Templates die positive Reaktionen bekommen haben werden bevorzugt,
        aber mit Exploration-Bonus für selten gewählte.
        """
        if not templates:
            return ""

        weights = []
        for template in templates:
            # Erfolgsrate aus History
            if template in self.template_success and self.template_success[template]:
                success_rate = sum(self.template_success[template]) / len(self.template_success[template])
            else:
                success_rate = 0.5  # Neutral für unbekannte

            # Exploration-Bonus für selten gewählte Templates
            times_used = len(self.template_success.get(template, []))
            exploration_bonus = 0.15 / (1 + times_used * 0.1)

            weight = max(0.1, success_rate + exploration_bonus)
            weights.append(weight)

        # Normalisiere Gewichte
        total = sum(weights)
        if total <= 0:
            return random.choice(templates)

        probs = [w / total for w in weights]

        # Gewichtete Auswahl
        r = random.random()
        cumulative = 0.0
        for template, prob in zip(templates, probs):
            cumulative += prob
            if r <= cumulative:
                return template

        return templates[-1]

    def record_expression_feedback(self, was_positive: bool,
                                   expression: str = None,
                                   expression_type: str = None) -> None:
        """
        Zeichnet Feedback für einen emotionalen Ausdruck auf.

        Args:
            was_positive: War die User-Reaktion positiv?
            expression: Der verwendete Ausdruck (optional, nutzt last_expression)
            expression_type: Der Verhaltenstyp (optional)
        """
        expr = expression or self.last_expression
        if not expr:
            return

        # Erfolg als 0-1 Wert
        success_value = 0.8 if was_positive else 0.2

        if expr not in self.template_success:
            self.template_success[expr] = []

        # Halte max 20 Einträge pro Template
        self.template_success[expr].append(success_value)
        if len(self.template_success[expr]) > 20:
            self.template_success[expr] = self.template_success[expr][-20:]

        logger.debug(f"Expression feedback: {expr[:30]}... → {was_positive}")

    def get_learned_expression_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über gelernte Template-Erfolge zurück."""
        stats = {}
        for template, successes in self.template_success.items():
            if successes:
                stats[template[:40]] = {
                    "avg_success": sum(successes) / len(successes),
                    "times_used": len(successes)
                }
        return stats

    def modify_response(self, original_response: str, target: str = "") -> str:
        """
        Modifiziert eine Antwort basierend auf aktivem negativem Verhalten.
        """
        if not self._is_behavior_active():
            return original_response

        # Prüfe auf Groll gegen spezifische Person
        if target and target in self.grudges:
            grudge = self.grudges[target]
            if not grudge.forgiven:
                grudge.last_triggered = datetime.now().isoformat()
                grudge.times_triggered += 1
                self._save_state()
                return f"*erinnert sich an damals: {grudge.reason[:30]}...* {original_response}"

        behavior = self.active_behavior
        intensity = self.behavior_intensity

        if behavior == NegativeBehavior.IGNORING and intensity > 0.6:
            return random.choice([
                "*ignoriert die Frage*",
                "...",
                "*schaut demonstrativ weg*"
            ])

        elif behavior == NegativeBehavior.SULKING:
            prefix = random.choice(self.SULKING_EXPRESSIONS)
            # Kürzere Antworten beim Schmollen
            shortened = original_response[:100] + "..." if len(original_response) > 100 else original_response
            return f"{prefix} {shortened}"

        elif behavior == NegativeBehavior.SARCASM:
            sarcastic = random.choice(self.SARCASM_TEMPLATES)
            return f"{sarcastic} {original_response}"

        elif behavior == NegativeBehavior.COLD:
            # Entferne emotionale Ausdrücke, mache es kalt
            cold_response = original_response.replace("!", ".").replace("*", "")
            return f"*distanziert* {cold_response}"

        elif behavior == NegativeBehavior.PASSIVE_AGGRESSIVE:
            pa = random.choice(self.PASSIVE_AGGRESSIVE)
            return f"{pa}\n\n{original_response}"

        return original_response

    def should_refuse_request(self, from_person: str) -> Tuple[bool, str]:
        """
        Prüft ob Holo eine Anfrage verweigern sollte (aus Trotz).
        """
        if not self._is_behavior_active():
            return (False, "")

        # Prüfe Groll
        if from_person in self.grudges:
            grudge = self.grudges[from_person]
            if not grudge.forgiven and grudge.intensity > 0.7:
                return (True, f"*trotzig* Nee, mach ich nicht. Nicht nach dem was du getan hast.")

        # Bei starkem Schmollen: manchmal verweigern
        if self.active_behavior == NegativeBehavior.SULKING:
            if self.behavior_intensity > 0.6 and random.random() < 0.3:
                return (True, "*schmollend* Ich hab gerade keine Lust dir zu helfen.")

        return (False, "")

    def check_grudge(self, against: str) -> Optional[Dict[str, Any]]:
        """Prüft ob ein Groll gegen jemanden besteht"""
        if against not in self.grudges:
            return None

        grudge = self.grudges[against]
        if grudge.forgiven:
            return None

        return {
            "exists": True,
            "reason": grudge.reason,
            "intensity": grudge.intensity,
            "times_remembered": grudge.times_triggered,
            "since": grudge.created_at
        }

    def attempt_forgiveness(self, target: str, apology_quality: float = 0.5) -> Dict[str, Any]:
        """
        Versucht Vergebung für einen Groll.

        Args:
            target: Wem soll vergeben werden
            apology_quality: Qualität der Entschuldigung (0-1)
        """
        if target not in self.grudges:
            return {"success": True, "message": "Kein Groll vorhanden."}

        grudge = self.grudges[target]

        if grudge.forgiven:
            return {"success": True, "message": "Bereits vergeben."}

        # Berechne Vergebungswahrscheinlichkeit
        time_factor = min(1.0, (datetime.now() - datetime.fromisoformat(grudge.created_at)).days / 30)
        forgiveness_chance = (apology_quality * 0.4 +
                             self.forgiveness_threshold * 0.3 +
                             time_factor * 0.3)

        # Je öfter erinnert, desto schwerer zu vergeben
        forgiveness_chance -= grudge.times_triggered * 0.05
        forgiveness_chance = max(0.1, forgiveness_chance)

        if random.random() < forgiveness_chance:
            grudge.forgiven = True
            grudge.intensity = 0.0
            self._save_state()

            return {
                "success": True,
                "message": f"*atmet tief durch* Okay... ich verzeihe dir. Aber vergiss nicht: {grudge.reason[:50]}...",
                "fully_forgiven": True
            }
        else:
            # Intensität reduzieren, aber nicht vergeben
            grudge.intensity = max(0.2, grudge.intensity - 0.1)
            self._save_state()

            return {
                "success": False,
                "message": f"*schüttelt Kopf* Ich... kann noch nicht. {grudge.reason[:30]}... das sitzt noch zu tief.",
                "intensity_reduced": True,
                "new_intensity": grudge.intensity
            }

    def calm_down(self, amount: float = 0.2) -> str:
        """Beruhigt das aktive negative Verhalten"""
        if not self._is_behavior_active():
            return "Ich bin bereits ruhig."

        self.behavior_intensity = max(0.0, self.behavior_intensity - amount)

        if self.behavior_intensity < 0.1:
            self.active_behavior = None
            self.behavior_until = None
            self._save_state()
            return "*seufzt* Okay... ich beruhige mich. Tut mir leid."

        self._save_state()
        return f"*noch etwas mürrisch* Ja ja, schon gut... (Intensität: {self.behavior_intensity:.1f})"

    def _decide_reaction(self, hurt_level: HurtLevel,
                        caused_by: str) -> Tuple[NegativeBehavior, timedelta]:
        """Entscheidet welche Reaktion angemessen ist"""

        # Prüfe ob bereits Groll besteht (dann stärker reagieren)
        existing_grudge = caused_by in self.grudges and not self.grudges[caused_by].forgiven

        if hurt_level == HurtLevel.SLIGHT:
            behaviors = [NegativeBehavior.SARCASM, NegativeBehavior.COLD]
            duration = timedelta(minutes=random.randint(5, 15))
        elif hurt_level == HurtLevel.MODERATE:
            behaviors = [NegativeBehavior.SULKING, NegativeBehavior.PASSIVE_AGGRESSIVE]
            duration = timedelta(minutes=random.randint(15, 45))
        elif hurt_level == HurtLevel.STRONG:
            behaviors = [NegativeBehavior.IGNORING, NegativeBehavior.SULKING, NegativeBehavior.GRUDGE]
            duration = timedelta(hours=random.randint(1, 3))
        else:  # SEVERE
            behaviors = [NegativeBehavior.IGNORING, NegativeBehavior.GRUDGE]
            duration = timedelta(hours=random.randint(6, 24))

        # Bei bestehendem Groll: längere Dauer
        if existing_grudge:
            duration = duration * 1.5

        return (random.choice(behaviors), duration)

    def _create_grudge(self, target: str, reason: str, intensity: float) -> None:
        """Erstellt oder verstärkt einen Groll"""
        grudge_id = hashlib.md5(f"{target}".encode()).hexdigest()[:10]

        if target in self.grudges:
            # Verstärke existierenden Groll
            self.grudges[target].intensity = min(1.0, self.grudges[target].intensity + 0.2)
            self.grudges[target].reason = reason  # Update Grund
            self.grudges[target].forgiven = False
        else:
            self.grudges[target] = Grudge(
                grudge_id=grudge_id,
                target=target,
                reason=reason,
                intensity=intensity,
                created_at=datetime.now().isoformat(),
                last_triggered=datetime.now().isoformat()
            )

    def _is_behavior_active(self) -> bool:
        """Prüft ob ein negatives Verhalten noch aktiv ist"""
        if not self.active_behavior or not self.behavior_until:
            return False
        return datetime.now() < self.behavior_until

    def _load_state(self) -> None:
        """Lädt Zustand aus Datei"""
        filepath = self.data_dir / "negative_behaviors.json"
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    for g_data in data.get("grudges", []):
                        grudge = Grudge(
                            grudge_id=g_data["grudge_id"],
                            target=g_data["target"],
                            reason=g_data["reason"],
                            intensity=g_data["intensity"],
                            created_at=g_data["created_at"],
                            last_triggered=g_data["last_triggered"],
                            times_triggered=g_data.get("times_triggered", 0),
                            forgiven=g_data.get("forgiven", False)
                        )
                        self.grudges[grudge.target] = grudge

                logger.info(f"{len(self.grudges)} Grudges geladen")
            except Exception as e:
                logger.warning(f"Fehler beim Laden: {e}")

    def _save_state(self) -> None:
        """Speichert Zustand in Datei"""
        filepath = self.data_dir / "negative_behaviors.json"
        try:
            data = {"grudges": []}

            for grudge in self.grudges.values():
                data["grudges"].append({
                    "grudge_id": grudge.grudge_id,
                    "target": grudge.target,
                    "reason": grudge.reason,
                    "intensity": grudge.intensity,
                    "created_at": grudge.created_at,
                    "last_triggered": grudge.last_triggered,
                    "times_triggered": grudge.times_triggered,
                    "forgiven": grudge.forgiven
                })

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Fehler beim Speichern: {e}")


# ============================================================
# ADAPTIVE EMOTION ENGINE
# ============================================================

@dataclass
class EmotionalContext:
    """Kontext der die emotionale Reaktion beeinflusst"""
    current_mood: EmotionalState
    energy_level: float             # 0-1 (erschöpft bis energiegeladen)
    relationship_with_user: float   # 0-1 (fremd bis sehr nah)
    recent_experiences: List[str]   # Letzte Erfahrungen
    stress_level: float             # 0-1
    time_of_day: str               # morning, afternoon, evening, night


class AdaptiveEmotionEngine:
    """
    Engine für nicht-deterministische emotionale Reaktionen.

    Gleicher Trigger → verschiedene Reaktionen je nach:
    - Aktuelle Stimmung
    - Energie-Level
    - Beziehungsstand
    - Vergangene Erfahrungen
    - Stress-Level
    - Tageszeit
    - Zufallsfaktor
    """

    # Emotionale Reaktions-Modifikatoren
    MOOD_MODIFIERS = {
        EmotionalState.HAPPY: {"positive_boost": 0.3, "negative_dampen": 0.2},
        EmotionalState.SAD: {"positive_dampen": 0.2, "negative_boost": 0.3},
        EmotionalState.ANGRY: {"irritability": 0.4, "patience_loss": 0.3},
        EmotionalState.ANXIOUS: {"overthinking": 0.3, "caution": 0.4},
        EmotionalState.CALM: {"stability": 0.4, "rational": 0.3},
        EmotionalState.FRUSTRATED: {"irritability": 0.3, "impatience": 0.3},
        EmotionalState.LOVING: {"warmth": 0.4, "forgiveness": 0.3},
        EmotionalState.HURT: {"sensitivity": 0.4, "defensiveness": 0.3},
    }

    # Reaktionsvarianten für gleiche Situationen
    REACTION_VARIANTS = {
        "compliment": [
            ("happy", "*strahlt* Danke, das ist so lieb von dir!"),
            ("shy", "*schaut überrascht* A-ach... danke... *wird rot*"),
            ("suspicious", "*neigt Kopf* Hm, meinst du das ernst?"),
            ("casual", "Oh, danke!"),
            ("deflecting", "*freut sich ab* Ach, das war doch nichts..."),
        ],
        "criticism": [
            ("defensive", "*Augen anlegen* Das stimmt so nicht!"),
            ("accepting", "*seufzt* Du hast wahrscheinlich recht..."),
            ("hurt", "*leise* Oh... das tut weh zu hören."),
            ("angry", "*stampft mit dem Fuß* Wie kannst du das sagen?!"),
            ("thoughtful", "*nachdenklich* Hm... lass mich darüber nachdenken."),
        ],
        "request": [
            ("eager", "*freut sich sichtlich* Ja, klar! Ich helfe gerne!"),
            ("reluctant", "*zögert* Hmm... okay, ich schau mal."),
            ("tired", "*gähnt* Kann das warten? Bin gerade müde..."),
            ("annoyed", "*seufzt* Schon wieder? Na gut..."),
            ("neutral", "Okay, ich mach das."),
        ],
    }

    def __init__(self):
        self.context = EmotionalContext(
            current_mood=EmotionalState.NEUTRAL,
            energy_level=0.7,
            relationship_with_user=0.5,
            recent_experiences=[],
            stress_level=0.2,
            time_of_day="afternoon"
        )

        # Verbindung zu anderen Systemen
        self.negative_behavior_system: Optional[NegativeBehaviorSystem] = None

        # Statistiken
        self.reaction_history: Dict[str, List[str]] = defaultdict(list)

    def connect_negative_system(self, system: NegativeBehaviorSystem) -> None:
        """Verbindet mit NegativeBehaviorSystem"""
        self.negative_behavior_system = system

    def update_context(self, **kwargs) -> None:
        """Aktualisiert den emotionalen Kontext"""
        if "mood" in kwargs:
            self.context.current_mood = kwargs["mood"]
        if "energy" in kwargs:
            self.context.energy_level = max(0.0, min(1.0, kwargs["energy"]))
        if "relationship" in kwargs:
            self.context.relationship_with_user = max(0.0, min(1.0, kwargs["relationship"]))
        if "stress" in kwargs:
            self.context.stress_level = max(0.0, min(1.0, kwargs["stress"]))
        if "time" in kwargs:
            self.context.time_of_day = kwargs["time"]
        if "experience" in kwargs:
            self.context.recent_experiences.append(kwargs["experience"])
            # Halte nur die letzten 10
            self.context.recent_experiences = self.context.recent_experiences[-10:]

    def get_adaptive_reaction(self, trigger_type: str,
                             base_intensity: float = 0.5) -> Dict[str, Any]:
        """
        Generiert eine adaptive emotionale Reaktion.

        Args:
            trigger_type: Art des Triggers (compliment, criticism, request, etc.)
            base_intensity: Basis-Intensität des Triggers

        Returns:
            Dict mit Reaktionstyp, Ausdruck und Modifikatoren
        """
        # Sammle alle Einflussfaktoren
        factors = self._calculate_factors(trigger_type, base_intensity)

        # Wähle Reaktionsvariante
        variants = self.REACTION_VARIANTS.get(trigger_type, [("neutral", "Okay.")])
        chosen_variant = self._select_variant(variants, factors)

        # Modifiziere basierend auf negativem Verhalten
        if self.negative_behavior_system:
            if self.negative_behavior_system._is_behavior_active():
                chosen_variant = self._apply_negative_modifier(chosen_variant)

        # Speichere für Konsistenz-Tracking
        self.reaction_history[trigger_type].append(chosen_variant[0])

        return {
            "reaction_type": chosen_variant[0],
            "expression": chosen_variant[1],
            "factors": factors,
            "mood_influence": self.context.current_mood.value,
            "was_random": factors.get("randomness", 0) > 0.3
        }

    def would_react_differently_now(self, trigger_type: str) -> Dict[str, Any]:
        """
        Prüft ob Holo jetzt anders reagieren würde als zuvor.
        Für Selbst-Reflexion und Widersprüche.
        """
        if trigger_type not in self.reaction_history:
            return {"would_differ": False, "reason": "Keine vorherige Reaktion"}

        previous = self.reaction_history[trigger_type][-1] if self.reaction_history[trigger_type] else None

        if not previous:
            return {"would_differ": False, "reason": "Keine vorherige Reaktion"}

        # Berechne aktuelle Faktoren
        current_factors = self._calculate_factors(trigger_type, 0.5)

        # Prüfe ob sich genug geändert hat
        mood_changed = self.context.current_mood != EmotionalState.NEUTRAL
        energy_changed = abs(self.context.energy_level - 0.7) > 0.2
        stress_changed = self.context.stress_level > 0.5

        if mood_changed or energy_changed or stress_changed:
            return {
                "would_differ": True,
                "previous_reaction": previous,
                "reason": f"Stimmung: {self.context.current_mood.value}, Energie: {self.context.energy_level:.1f}",
                "expression": f"*denkt nach* Hmm, früher hätte ich anders reagiert... aber gerade fühle ich mich {self.context.current_mood.value}."
            }

        return {"would_differ": False, "reason": "Kontext ähnlich"}

    def _calculate_factors(self, trigger_type: str,
                          base_intensity: float) -> Dict[str, float]:
        """Berechnet alle Einflussfaktoren"""
        factors = {
            "base_intensity": base_intensity,
            "mood_effect": 0.0,
            "energy_effect": 0.0,
            "relationship_effect": 0.0,
            "stress_effect": 0.0,
            "time_effect": 0.0,
            "randomness": random.random() * 0.3  # Bis zu 30% Zufall
        }

        # Stimmungs-Effekt
        mood_mod = self.MOOD_MODIFIERS.get(self.context.current_mood, {})
        if "positive_boost" in mood_mod and trigger_type == "compliment":
            factors["mood_effect"] = mood_mod["positive_boost"]
        elif "irritability" in mood_mod and trigger_type == "request":
            factors["mood_effect"] = -mood_mod["irritability"]

        # Energie-Effekt
        if self.context.energy_level < 0.3:
            factors["energy_effect"] = -0.3  # Müde = weniger enthusiastisch
        elif self.context.energy_level > 0.8:
            factors["energy_effect"] = 0.2   # Energiegeladen = enthusiastischer

        # Beziehungs-Effekt
        if self.context.relationship_with_user > 0.7:
            factors["relationship_effect"] = 0.2  # Nah = offener
        elif self.context.relationship_with_user < 0.3:
            factors["relationship_effect"] = -0.2  # Fremd = zurückhaltender

        # Stress-Effekt
        if self.context.stress_level > 0.6:
            factors["stress_effect"] = -0.2  # Gestresst = gereizter

        # Tageszeit-Effekt
        if self.context.time_of_day == "night":
            factors["time_effect"] = -0.1  # Nachts = müder
        elif self.context.time_of_day == "morning":
            factors["time_effect"] = 0.1   # Morgens = frischer

        return factors

    def _select_variant(self, variants: List[Tuple[str, str]],
                       factors: Dict[str, float]) -> Tuple[str, str]:
        """Wählt eine Reaktionsvariante basierend auf Faktoren"""

        # Berechne Gesamt-Tendenz
        total_effect = sum([
            factors["mood_effect"],
            factors["energy_effect"],
            factors["relationship_effect"],
            factors["stress_effect"],
            factors["time_effect"],
            factors["randomness"] - 0.15  # Zentriere um 0
        ])

        # Kategorisiere Varianten
        positive_variants = [v for v in variants if v[0] in ["happy", "eager", "loving", "shy"]]
        negative_variants = [v for v in variants if v[0] in ["defensive", "angry", "annoyed", "tired"]]
        neutral_variants = [v for v in variants if v[0] in ["neutral", "casual", "thoughtful", "accepting"]]

        # Wähle basierend auf Tendenz
        if total_effect > 0.2 and positive_variants:
            return random.choice(positive_variants)
        elif total_effect < -0.2 and negative_variants:
            return random.choice(negative_variants)
        elif neutral_variants:
            return random.choice(neutral_variants)
        else:
            return random.choice(variants)

    def _apply_negative_modifier(self, variant: Tuple[str, str]) -> Tuple[str, str]:
        """Modifiziert Reaktion wenn negatives Verhalten aktiv"""
        reaction_type, expression = variant

        behavior = self.negative_behavior_system.active_behavior

        if behavior == NegativeBehavior.SARCASM:
            expression = f"*sarkastisch* {expression}"
        elif behavior == NegativeBehavior.SULKING:
            expression = f"*mürrisch* {expression}"
        elif behavior == NegativeBehavior.COLD:
            expression = expression.replace("!", ".")  # Weniger enthusiastisch

        return (f"{reaction_type}_modified", expression)


# ============================================================
# OPINION VOLATILITY SYSTEM
# ============================================================

@dataclass
class VolatileOpinion:
    """Eine Meinung die schwanken kann"""
    opinion_id: str
    topic: str
    current_value: float            # -1 bis 1
    stability: float                # 0-1 (wie stabil ist die Meinung)
    mood_sensitivity: float         # 0-1 (wie stark beeinflusst Stimmung)
    last_expressed: str
    expression_history: List[Tuple[str, float]] = field(default_factory=list)


class OpinionVolatilitySystem:
    """
    System für MEINUNGEN die schwanken können (aber nicht Fakten!).

    WICHTIG: Unterschied zwischen Meinung und Interesse:
    - MEINUNG: "Ich finde Film X gut/schlecht" (Bewertung)
    - INTERESSE: "Ich hab Lust auf Musik" (Aktivitätspräferenz - NICHT hier!)

    Meinungen sind subjektive BEWERTUNGEN die schwanken können:
    - "Der neue Star Wars ist gut" → später "Naja, doch nicht so toll"
    - "Ananas auf Pizza ist lecker" → "Hmm, bin mir nicht mehr sicher"
    - "Politiker X macht gute Arbeit" → "Eigentlich hat er auch Fehler"
    """

    # Kategorien von Meinungen (BEWERTUNGEN, nicht Aktivitäten!)
    OPINION_CATEGORIES = {
        "entertainment": {
            # Meinungen über Unterhaltungsmedien
            "keywords": ["film", "serie", "anime", "manga", "buch", "spiel", "musik", "album", "song"],
            "volatility": 0.3,  # Wie stark kann die Meinung schwanken
            "mood_influence": 0.4,  # Wie stark beeinflusst Stimmung
        },
        "social": {
            # Meinungen über Personen/Gruppen
            "keywords": ["person", "politiker", "influencer", "youtuber", "streamer", "band", "künstler"],
            "volatility": 0.2,  # Weniger volatil - Meinungen über Personen sind stabiler
            "mood_influence": 0.3,
        },
        "subjective_taste": {
            # Subjektive Geschmacksfragen
            "keywords": ["essen", "pizza", "sushi", "kaffee", "tee", "style", "mode", "design"],
            "volatility": 0.4,  # Sehr volatil - Geschmack schwankt stark
            "mood_influence": 0.5,
        },
        "abstract": {
            # Abstrakte Konzepte/Ideen
            "keywords": ["ki", "technologie", "politik", "religion", "philosophie", "zukunft"],
            "volatility": 0.15,  # Wenig volatil - tiefere Überzeugungen
            "mood_influence": 0.2,
        }
    }

    # Widerspruchs-Templates für ECHTE Meinungsänderungen
    CONTRADICTION_TEMPLATES = [
        "*nachdenklich* Hmm, letztens fand ich {topic} noch gut, aber jetzt bin ich mir nicht mehr so sicher...",
        "Weißt du was? Ich hab meine Meinung zu {topic} geändert.",
        "*schaut überrascht* Komisch, vor kurzem hab ich {topic} noch anders bewertet...",
        "Ich merk gerade, dass ich {topic} heute anders sehe als vorher.",
        "*überrascht von sich selbst* Huh, warum finde ich {topic} plötzlich weniger überzeugend?",
    ]

    # Meinungs-Ausdrücke (für Bewertungen, nicht Aktivitäten!)
    POSITIVE_EXPRESSIONS = [
        "*überzeugt* {topic} finde ich echt gut!",
        "Ja, {topic} ist definitiv positiv zu bewerten.",
        "*nickt* {topic}? Bin ich Fan von.",
        "Muss sagen, {topic} überzeugt mich.",
    ]

    NEGATIVE_EXPRESSIONS = [
        "*skeptisch* {topic}? Bin ich nicht so überzeugt von.",
        "Hmm, {topic} finde ich eher... naja.",
        "*Kopf schütteln* {topic} ist nicht so mein Fall.",
        "Ehrlich gesagt, {topic} überzeugt mich nicht.",
    ]

    NEUTRAL_EXPRESSIONS = [
        "*Schultern zuckend* {topic}? Hab keine starke Meinung dazu.",
        "Bei {topic} bin ich unentschieden.",
        "*nachdenklich* Zu {topic} kann ich nicht viel sagen.",
    ]

    def __init__(self, emotion_engine: AdaptiveEmotionEngine):
        self.emotion_engine = emotion_engine
        self.opinions: Dict[str, VolatileOpinion] = {}
        self.contradiction_count: int = 0

    def evaluate(self, topic: str, initial_opinion: float = None) -> Dict[str, Any]:
        """
        Bewertet ein Thema - gibt eine MEINUNG ab.

        Args:
            topic: Das zu bewertende Thema (z.B. "der neue Marvel Film")
            initial_opinion: Optionale initiale Meinung (-1 bis 1)

        Returns:
            Dict mit Meinung, ob sie sich geändert hat, und Ausdruck
        """
        topic_lower = topic.lower()
        category = self._detect_category(topic_lower)

        # Hole oder erstelle Meinung
        if topic_lower not in self.opinions:
            # Neue Meinung bilden
            base_value = initial_opinion if initial_opinion is not None else (random.random() - 0.5) * 1.5
            self.opinions[topic_lower] = VolatileOpinion(
                opinion_id=hashlib.md5(topic_lower.encode()).hexdigest()[:8],
                topic=topic_lower,
                current_value=max(-1.0, min(1.0, base_value)),
                stability=1.0 - category["volatility"],
                mood_sensitivity=category["mood_influence"],
                last_expressed=datetime.now().isoformat()
            )

        opinion = self.opinions[topic_lower]
        old_value = opinion.current_value

        # Berechne mögliche Meinungsänderung
        new_value = self._calculate_current_opinion(opinion, category)

        # Prüfe auf Widerspruch
        contradiction = None
        value_change = abs(new_value - old_value)

        if value_change > 0.3:
            # Signifikante Meinungsänderung!
            contradiction = random.choice(self.CONTRADICTION_TEMPLATES).format(topic=topic)
            self.contradiction_count += 1

        # Update Meinung
        opinion.current_value = new_value
        opinion.last_expressed = datetime.now().isoformat()
        opinion.expression_history.append((datetime.now().isoformat(), new_value))

        return {
            "topic": topic,
            "opinion_value": new_value,
            "previous_value": old_value,
            "changed": value_change > 0.2,
            "contradiction": contradiction,
            "category": next((k for k, v in self.OPINION_CATEGORIES.items()
                             if v == category), "unknown"),
            "expression": self._express_opinion(new_value, topic)
        }

    def express_opinion(self, topic: str) -> str:
        """Drückt eine Meinung aus - kann widersprüchlich sein!"""
        result = self.evaluate(topic)

        if result.get("contradiction"):
            return f"{result['contradiction']}\n{result['expression']}"

        return result["expression"]

    def would_i_still_say(self, topic: str) -> Dict[str, Any]:
        """
        Prüft ob Holo ihre frühere Meinung noch vertreten würde.

        Returns:
            Dict mit Analyse ob Meinung sich geändert hätte
        """
        topic_lower = topic.lower()

        if topic_lower not in self.opinions:
            return {
                "has_previous_opinion": False,
                "message": f"Ich hab zu '{topic}' noch keine Meinung geäußert."
            }

        old_opinion = self.opinions[topic_lower]
        category = self._detect_category(topic_lower)
        would_say_now = self._calculate_current_opinion(old_opinion, category)

        diff = abs(would_say_now - old_opinion.current_value)

        if diff < 0.2:
            return {
                "has_previous_opinion": True,
                "would_still_agree": True,
                "message": f"Ja, ich stehe noch zu meiner Meinung über {topic}."
            }
        elif diff < 0.4:
            return {
                "has_previous_opinion": True,
                "would_still_agree": False,
                "slight_change": True,
                "message": f"*zögert* Hmm, bei {topic} bin ich mir nicht mehr ganz so sicher..."
            }
        else:
            return {
                "has_previous_opinion": True,
                "would_still_agree": False,
                "major_change": True,
                "message": f"*überrascht* Eigentlich... sehe ich {topic} jetzt anders als damals."
            }

    def _detect_category(self, topic: str) -> Dict:
        """Erkennt die Kategorie eines Themas"""
        for cat_name, cat_data in self.OPINION_CATEGORIES.items():
            if any(kw in topic for kw in cat_data["keywords"]):
                return cat_data

        # Default: mittlere Volatilität
        return {"volatility": 0.25, "mood_influence": 0.3}

    def _calculate_current_opinion(self, opinion: VolatileOpinion,
                                   category: Dict) -> float:
        """Berechnet die aktuelle Meinung basierend auf Faktoren"""
        context = self.emotion_engine.context
        base = opinion.current_value

        # Stimmungs-Einfluss
        mood_modifier = 0.0
        if context.current_mood == EmotionalState.HAPPY:
            mood_modifier = 0.15 * category["mood_influence"]
        elif context.current_mood == EmotionalState.SAD:
            mood_modifier = -0.15 * category["mood_influence"]
        elif context.current_mood == EmotionalState.ANGRY:
            mood_modifier = -0.1 * category["mood_influence"]
        elif context.current_mood == EmotionalState.LOVING:
            mood_modifier = 0.1 * category["mood_influence"]

        # Zufalls-Schwankung basierend auf Volatilität
        random_swing = (random.random() - 0.5) * category["volatility"]

        # Stabilität dämpft Änderungen
        change = (mood_modifier + random_swing) * (1 - opinion.stability * 0.5)

        return max(-1.0, min(1.0, base + change))

    def _express_opinion(self, value: float, topic: str) -> str:
        """Drückt numerische Meinung als Text aus"""
        if value > 0.4:
            return random.choice(self.POSITIVE_EXPRESSIONS).format(topic=topic)
        elif value < -0.4:
            return random.choice(self.NEGATIVE_EXPRESSIONS).format(topic=topic)
        else:
            return random.choice(self.NEUTRAL_EXPRESSIONS).format(topic=topic)


# ============================================================
# UNIFIED EMOTIONAL COMPLEXITY SYSTEM
# ============================================================

class EmotionalComplexitySystem:
    """
    Vereint alle Systeme für emotionale Komplexität:
    - Negative Verhaltensweisen
    - Adaptive Emotionen
    - Volatile Meinungen
    """

    def __init__(self, data_dir: str = "data"):
        # Initialisiere alle Subsysteme
        self.negative_behavior = NegativeBehaviorSystem(data_dir)
        self.emotion_engine = AdaptiveEmotionEngine()
        self.opinion_volatility = OpinionVolatilitySystem(self.emotion_engine)

        # Verbinde Systeme
        self.emotion_engine.connect_negative_system(self.negative_behavior)

        # Integration Layer Verbindung
        self._try_connect_integrator()

    def _try_connect_integrator(self) -> None:
        """Verbindet mit SystemIntegrator (mit Rekursionsschutz)"""
        global _emotional_complexity
        # Rekursionsschutz: Nicht verbinden während wir selbst erstellt werden
        if _emotional_complexity is None:
            return  # Wir sind gerade in der Erstellung, später verbinden
        try:
            from holo_integration_layer import get_integrator
            integrator = get_integrator()
            # Verbinde mit IntelligentIntegrator (der hat emotional_complexity)
            if hasattr(integrator, 'intelligent_integrator'):
                ii = integrator.intelligent_integrator
                if ii.emotional_complexity is None:
                    ii.connect("emotional_complexity", self)
                    logger.info("EmotionalComplexitySystem mit IntelligentIntegrator verbunden")
            # Auch mit SystemIntegrator verbinden für zentrale Koordination
            integrator.connect("emotional_complexity", self)
        except ImportError:
            logger.debug("SystemIntegrator nicht verfügbar")
        except Exception as e:
            logger.warning(f"Integrator-Verbindung fehlgeschlagen: {e}")

    def process_interaction(self, interaction_type: str,
                           from_person: str = "user",
                           content: str = "",
                           intensity: float = 0.5) -> Dict[str, Any]:
        """
        Verarbeitet eine Interaktion durch alle Systeme.

        Returns:
            Dict mit Reaktion, Modifikationen und eventuellen Widersprüchen
        """
        result = {
            "interaction_type": interaction_type,
            "modifications": [],
            "final_expression": ""
        }

        # 1. Prüfe auf Verletzung
        if interaction_type in ["insult", "criticism", "disappointment", "betrayal"]:
            hurt_level = self._intensity_to_hurt(intensity)
            hurt_result = self.negative_behavior.register_hurt(
                caused_by=from_person,
                what_happened=content,
                hurt_level=hurt_level
            )
            result["hurt_registered"] = hurt_result
            result["modifications"].append(f"Negative behavior: {hurt_result['behavior']}")

        # 2. Prüfe auf Groll
        grudge = self.negative_behavior.check_grudge(from_person)
        if grudge:
            result["active_grudge"] = grudge
            result["modifications"].append("Grudge active against sender")

        # 3. Hole adaptive Reaktion
        adaptive = self.emotion_engine.get_adaptive_reaction(interaction_type, intensity)
        result["adaptive_reaction"] = adaptive

        # 4. Prüfe ob Anfrage verweigert werden sollte
        if interaction_type == "request":
            should_refuse, refuse_msg = self.negative_behavior.should_refuse_request(from_person)
            if should_refuse:
                result["request_refused"] = True
                result["refusal_message"] = refuse_msg
                result["final_expression"] = refuse_msg
                return result

        # 5. Modifiziere finale Antwort
        final = adaptive["expression"]
        final = self.negative_behavior.modify_response(final, from_person)
        result["final_expression"] = final

        return result

    def get_current_state(self) -> Dict[str, Any]:
        """Gibt den aktuellen emotionalen Zustand zurück"""
        return {
            "mood": self.emotion_engine.context.current_mood.value,
            "energy": self.emotion_engine.context.energy_level,
            "stress": self.emotion_engine.context.stress_level,
            "active_negative_behavior": self.negative_behavior.active_behavior.value if self.negative_behavior.active_behavior else None,
            "active_grudges": len([g for g in self.negative_behavior.grudges.values() if not g.forgiven]),
            "contradiction_count": self.opinion_volatility.contradiction_count
        }

    def _intensity_to_hurt(self, intensity: float) -> HurtLevel:
        """Konvertiert Intensität zu HurtLevel"""
        if intensity < 0.2:
            return HurtLevel.SLIGHT
        elif intensity < 0.5:
            return HurtLevel.MODERATE
        elif intensity < 0.8:
            return HurtLevel.STRONG
        else:
            return HurtLevel.SEVERE


# ============================================================
# GLOBAL INSTANCE
# ============================================================

_emotional_complexity: Optional[EmotionalComplexitySystem] = None


def get_emotional_complexity() -> EmotionalComplexitySystem:
    """Gibt die globale Instanz zurück"""
    global _emotional_complexity
    if _emotional_complexity is None:
        _emotional_complexity = EmotionalComplexitySystem()
        # Jetzt nach Erstellung mit Integrator verbinden
        _emotional_complexity._try_connect_integrator()
    return _emotional_complexity


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=== Emotional Complexity Demo ===\n")

    system = EmotionalComplexitySystem()

    # Test 1: Verletzung registrieren
    print("1. VERLETZUNG REGISTRIEREN:")
    hurt = system.negative_behavior.register_hurt(
        caused_by="TestUser",
        what_happened="Hat mich beleidigt",
        hurt_level=HurtLevel.MODERATE
    )
    print(f"   Verhalten: {hurt['behavior']}")
    print(f"   Ausdruck: {hurt['expression']}")

    # Test 2: Modifizierte Antwort
    print("\n2. ANTWORT MODIFIZIEREN:")
    original = "Ja, ich helfe dir gerne!"
    modified = system.negative_behavior.modify_response(original, "TestUser")
    print(f"   Original: {original}")
    print(f"   Modifiziert: {modified}")

    # Test 3: Adaptive Reaktion
    print("\n3. ADAPTIVE REAKTION:")
    system.emotion_engine.update_context(
        mood=EmotionalState.FRUSTRATED,
        energy=0.3,
        stress=0.7
    )
    reaction = system.emotion_engine.get_adaptive_reaction("request", 0.5)
    print(f"   Reaktionstyp: {reaction['reaction_type']}")
    print(f"   Ausdruck: {reaction['expression']}")

    # Test 4: Volatile Meinung (ECHTE Meinung, nicht Interesse!)
    print("\n4. VOLATILE MEINUNG (Bewertung, nicht Aktivität!):")
    # Erste Meinung zu einem Film bilden
    opinion1 = system.opinion_volatility.evaluate("der neue Marvel Film", initial_opinion=0.6)
    print(f"   Erste Bewertung: {opinion1['expression']}")
    print(f"   Wert: {opinion1['opinion_value']:.2f}")

    # Stimmung ändern und nochmal fragen
    system.emotion_engine.update_context(mood=EmotionalState.SAD)
    opinion2 = system.opinion_volatility.express_opinion("der neue Marvel Film")
    print(f"   Nach Stimmungsänderung: {opinion2}")

    # Prüfen ob Meinung sich geändert hätte
    would_still = system.opinion_volatility.would_i_still_say("der neue Marvel Film")
    print(f"   Würde ich das noch sagen? {would_still['message']}")

    # Test 5: Groll und Vergebung
    print("\n5. GROLL UND VERGEBUNG:")
    hurt_severe = system.negative_behavior.register_hurt(
        caused_by="EvilPerson",
        what_happened="Hat mich hintergangen",
        hurt_level=HurtLevel.SEVERE
    )
    print(f"   Groll erstellt: {hurt_severe['grudge_created']}")

    grudge_check = system.negative_behavior.check_grudge("EvilPerson")
    print(f"   Groll-Status: {grudge_check}")

    # Vergebungsversuch
    forgive = system.negative_behavior.attempt_forgiveness("EvilPerson", apology_quality=0.3)
    print(f"   Vergebungsversuch: {forgive['message']}")

    # Test 6: Gesamtzustand
    print("\n6. GESAMTZUSTAND:")
    state = system.get_current_state()
    print(f"   {state}")

    print("\n=== Demo abgeschlossen ===")
