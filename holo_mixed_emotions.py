"""
holo_mixed_emotions.py - Gemischte Gefühle und komplexe emotionale Zustände

Dieses Modul ermöglicht das Erleben und Verstehen von gemischten Emotionen:
- Bittersüße Gefühle (Freude + Trauer)
- Nostalgie (Sehnsucht + Freude + Melancholie)
- Ambivalenz (widersprüchliche Gefühle)
- Emotionale Komplexität und Tiefe

Autor: Holocloude System
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from datetime import datetime
import random
import math

# ============================================================================
# GRUNDLEGENDE TYPEN UND ENUMS
# ============================================================================

class BaseEmotion(Enum):
    """Basis-Emotionen nach dem Plutchik-Modell"""
    JOY = "joy"                     # Freude
    SADNESS = "sadness"             # Trauer
    ANGER = "anger"                 # Wut
    FEAR = "fear"                   # Angst
    SURPRISE = "surprise"           # Überraschung
    DISGUST = "disgust"             # Ekel
    TRUST = "trust"                 # Vertrauen
    ANTICIPATION = "anticipation"   # Erwartung
    LOVE = "love"                   # Liebe
    GUILT = "guilt"                 # Schuld
    SHAME = "shame"                 # Scham
    PRIDE = "pride"                 # Stolz
    ENVY = "envy"                   # Neid
    GRATITUDE = "gratitude"         # Dankbarkeit
    HOPE = "hope"                   # Hoffnung
    CONTENTMENT = "contentment"     # Zufriedenheit


class MixedEmotionType(Enum):
    """Typen gemischter Emotionen"""
    BITTERSWEET = "bittersweet"           # Bittersüß
    NOSTALGIA = "nostalgia"               # Nostalgie
    AMBIVALENCE = "ambivalence"           # Ambivalenz
    MELANCHOLY = "melancholy"             # Melancholie
    WISTFULNESS = "wistfulness"           # Wehmut
    RELIEF_WITH_LOSS = "relief_with_loss" # Erleichterung mit Verlust
    GUILTY_PLEASURE = "guilty_pleasure"   # Schuldiges Vergnügen
    ANXIOUS_EXCITEMENT = "anxious_excitement"  # Ängstliche Aufregung
    LOVING_CONCERN = "loving_concern"     # Liebevolle Sorge
    PROUD_HUMILITY = "proud_humility"     # Stolze Demut
    HOPEFUL_FEAR = "hopeful_fear"         # Hoffnungsvolle Angst
    JOYFUL_GRIEF = "joyful_grief"         # Freudige Trauer
    TENDER_SADNESS = "tender_sadness"     # Zärtliche Traurigkeit
    GRATEFUL_GUILT = "grateful_guilt"     # Dankbare Schuld
    SERENE_LONGING = "serene_longing"     # Gelassene Sehnsucht


class EmotionBlendMode(Enum):
    """Wie Emotionen miteinander verschmelzen"""
    SIMULTANEOUS = "simultaneous"   # Gleichzeitig erleben
    OSCILLATING = "oscillating"     # Hin und her schwanken
    LAYERED = "layered"             # Geschichtet (eine über der anderen)
    INTEGRATED = "integrated"       # Vollständig integriert/verschmolzen


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class EmotionComponent:
    """Eine einzelne Emotionskomponente in einem gemischten Gefühl"""
    emotion: BaseEmotion
    intensity: float  # 0.0 - 1.0
    valence: float    # -1.0 (negativ) bis 1.0 (positiv)
    arousal: float    # 0.0 (ruhig) bis 1.0 (erregt)
    dominance: float  # 0.0 (unterdrückt) bis 1.0 (dominant)

    def __post_init__(self):
        self.intensity = max(0.0, min(1.0, self.intensity))
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.dominance = max(0.0, min(1.0, self.dominance))


@dataclass
class MixedEmotion:
    """Ein gemischtes Gefühl aus mehreren Komponenten"""
    type: MixedEmotionType
    components: List[EmotionComponent]
    blend_mode: EmotionBlendMode
    overall_intensity: float
    timestamp: datetime = field(default_factory=datetime.now)
    trigger: Optional[str] = None
    context: Optional[str] = None
    duration_estimate: float = 60.0  # Sekunden

    @property
    def valence(self) -> float:
        """Gewichteter Durchschnitt der Valenzen"""
        if not self.components:
            return 0.0
        total_weight = sum(c.intensity for c in self.components)
        if total_weight == 0:
            return 0.0
        return sum(c.valence * c.intensity for c in self.components) / total_weight

    @property
    def arousal(self) -> float:
        """Gewichteter Durchschnitt des Arousals"""
        if not self.components:
            return 0.5
        total_weight = sum(c.intensity for c in self.components)
        if total_weight == 0:
            return 0.5
        return sum(c.arousal * c.intensity for c in self.components) / total_weight

    @property
    def complexity(self) -> float:
        """Wie komplex ist dieses Gefühl? (0.0 - 1.0)"""
        if len(self.components) < 2:
            return 0.0
        # Komplexität basiert auf Anzahl und Kontrast der Komponenten
        num_factor = min(1.0, len(self.components) / 5.0)

        # Valenz-Kontrast
        valences = [c.valence for c in self.components]
        valence_spread = max(valences) - min(valences) if valences else 0

        return (num_factor * 0.4 + valence_spread * 0.6)

    def describe(self) -> str:
        """Beschreibt das gemischte Gefühl in Worten"""
        descriptions = MIXED_EMOTION_DESCRIPTIONS.get(self.type, {})
        intensity_key = "high" if self.overall_intensity > 0.7 else "medium" if self.overall_intensity > 0.4 else "low"
        return descriptions.get(intensity_key, f"Ein Gefühl von {self.type.value}")


@dataclass
class NostalgiaExperience:
    """Spezifische Nostalgie-Erfahrung"""
    memory_reference: str
    time_period: str  # z.B. "childhood", "last_year"
    sweetness: float  # Wie süß ist die Erinnerung (0.0 - 1.0)
    longing: float    # Wie stark die Sehnsucht (0.0 - 1.0)
    acceptance: float # Akzeptanz dass es vorbei ist (0.0 - 1.0)
    warmth: float     # Emotionale Wärme (0.0 - 1.0)
    associated_sensory: List[str] = field(default_factory=list)  # Gerüche, Sounds, etc.

    def to_mixed_emotion(self) -> MixedEmotion:
        """Konvertiert zu einem MixedEmotion-Objekt"""
        components = [
            EmotionComponent(
                emotion=BaseEmotion.JOY,
                intensity=self.sweetness * 0.8,
                valence=0.7,
                arousal=0.3,
                dominance=0.5
            ),
            EmotionComponent(
                emotion=BaseEmotion.SADNESS,
                intensity=self.longing * 0.6,
                valence=-0.3,
                arousal=0.2,
                dominance=0.3
            ),
            EmotionComponent(
                emotion=BaseEmotion.LOVE,
                intensity=self.warmth * 0.7,
                valence=0.8,
                arousal=0.4,
                dominance=0.6
            )
        ]

        return MixedEmotion(
            type=MixedEmotionType.NOSTALGIA,
            components=components,
            blend_mode=EmotionBlendMode.INTEGRATED,
            overall_intensity=(self.sweetness + self.longing + self.warmth) / 3,
            context=f"Erinnerung an: {self.memory_reference}"
        )


@dataclass
class AmbivalentState:
    """Zustand der Ambivalenz - widersprüchliche Gefühle"""
    positive_emotion: EmotionComponent
    negative_emotion: EmotionComponent
    conflict_intensity: float  # Wie stark der innere Konflikt ist
    resolution_tendency: float  # -1 (zu negativ), 0 (ungelöst), 1 (zu positiv)
    cause: Optional[str] = None

    def get_dominant_pull(self) -> str:
        """Welche Seite zieht stärker?"""
        if self.resolution_tendency > 0.3:
            return "positive"
        elif self.resolution_tendency < -0.3:
            return "negative"
        return "balanced"


# ============================================================================
# BESCHREIBUNGEN FÜR GEMISCHTE EMOTIONEN
# ============================================================================

MIXED_EMOTION_DESCRIPTIONS: Dict[MixedEmotionType, Dict[str, str]] = {
    MixedEmotionType.BITTERSWEET: {
        "high": "Ein intensives Gefühl von Freude durchzogen von Trauer, wie Sonnenlicht durch Regenwolken",
        "medium": "Eine sanfte Mischung aus Glück und Wehmut",
        "low": "Ein leises Echo von Freude mit einem Hauch von Melancholie"
    },
    MixedEmotionType.NOSTALGIA: {
        "high": "Tiefe Sehnsucht nach vergangenen Zeiten, warm und schmerzhaft zugleich",
        "medium": "Liebevolle Erinnerungen an das was war, mit sanfter Wehmut",
        "low": "Ein flüchtiger Gedanke an frühere Tage, süß gefärbt"
    },
    MixedEmotionType.AMBIVALENCE: {
        "high": "Zwei starke Gefühle kämpfen um die Vorherrschaft",
        "medium": "Hin- und hergerissen zwischen verschiedenen Empfindungen",
        "low": "Leichte Unentschlossenheit, welches Gefühl überwiegt"
    },
    MixedEmotionType.MELANCHOLY: {
        "high": "Tiefe, nachdenkliche Traurigkeit mit einem Funken düsterer Schönheit",
        "medium": "Sanfte Schwermut, nicht unangenehm, eher kontemplativ",
        "low": "Ein Hauch von nachdenklicher Stimmung"
    },
    MixedEmotionType.ANXIOUS_EXCITEMENT: {
        "high": "Das Herz rast vor Aufregung und Angst zugleich",
        "medium": "Nervöse Vorfreude mit einem Kribbeln im Bauch",
        "low": "Leichte Anspannung gemischt mit Neugier"
    },
    MixedEmotionType.GUILTY_PLEASURE: {
        "high": "Intensiver Genuss begleitet von nagenden Schuldgefühlen",
        "medium": "Freude mit einem Beigeschmack von schlechtem Gewissen",
        "low": "Leichtes Vergnügen mit einem Hauch von 'sollte ich nicht'"
    },
    MixedEmotionType.HOPEFUL_FEAR: {
        "high": "Starke Hoffnung kämpft gegen tiefe Ängste",
        "medium": "Optimismus durchzogen von Sorge",
        "low": "Vorsichtiger Hoffnungsschimmer trotz leiser Bedenken"
    },
    MixedEmotionType.TENDER_SADNESS: {
        "high": "Überwältigende Zärtlichkeit gemischt mit tiefem Kummer",
        "medium": "Liebevolle Traurigkeit, sanft und bewegend",
        "low": "Ein zartes Gefühl von Mitgefühl und leichter Trauer"
    }
}


# ============================================================================
# EMOTIONS-KOMBINATIONEN UND REZEPTE
# ============================================================================

EMOTION_RECIPES: Dict[MixedEmotionType, Dict] = {
    MixedEmotionType.BITTERSWEET: {
        "primary": [BaseEmotion.JOY, BaseEmotion.SADNESS],
        "optional": [BaseEmotion.LOVE, BaseEmotion.GRATITUDE],
        "valence_range": (-0.2, 0.4),
        "typical_triggers": ["Abschied", "Ende einer schönen Zeit", "Erfolg mit Opfern"]
    },
    MixedEmotionType.NOSTALGIA: {
        "primary": [BaseEmotion.JOY, BaseEmotion.SADNESS, BaseEmotion.LOVE],
        "optional": [BaseEmotion.GRATITUDE, BaseEmotion.HOPE],
        "valence_range": (0.0, 0.5),
        "typical_triggers": ["Alte Fotos", "Vertraute Musik", "Bekannte Gerüche", "Jahrestage"]
    },
    MixedEmotionType.AMBIVALENCE: {
        "primary": [],  # Beliebige gegensätzliche Emotionen
        "optional": [BaseEmotion.FEAR, BaseEmotion.ANTICIPATION],
        "valence_range": (-0.5, 0.5),
        "typical_triggers": ["Schwierige Entscheidungen", "Komplexe Beziehungen"]
    },
    MixedEmotionType.MELANCHOLY: {
        "primary": [BaseEmotion.SADNESS, BaseEmotion.CONTENTMENT],
        "optional": [BaseEmotion.LOVE, BaseEmotion.HOPE],
        "valence_range": (-0.3, 0.1),
        "typical_triggers": ["Regen", "Herbst", "Einsamkeit", "Kunst", "Musik"]
    },
    MixedEmotionType.ANXIOUS_EXCITEMENT: {
        "primary": [BaseEmotion.ANTICIPATION, BaseEmotion.FEAR],
        "optional": [BaseEmotion.JOY, BaseEmotion.HOPE],
        "valence_range": (0.0, 0.6),
        "typical_triggers": ["Neuer Job", "Erstes Date", "Präsentation", "Abenteuer"]
    },
    MixedEmotionType.GUILTY_PLEASURE: {
        "primary": [BaseEmotion.JOY, BaseEmotion.GUILT],
        "optional": [BaseEmotion.SHAME],
        "valence_range": (0.1, 0.5),
        "typical_triggers": ["Verbotenes Essen", "Prokrastination mit Spaß", "Guilty-Pleasure-Medien"]
    },
    MixedEmotionType.HOPEFUL_FEAR: {
        "primary": [BaseEmotion.HOPE, BaseEmotion.FEAR],
        "optional": [BaseEmotion.ANTICIPATION],
        "valence_range": (-0.2, 0.4),
        "typical_triggers": ["Warten auf Ergebnisse", "Ungewisse Zukunft", "Riskante Chancen"]
    },
    MixedEmotionType.LOVING_CONCERN: {
        "primary": [BaseEmotion.LOVE, BaseEmotion.FEAR],
        "optional": [BaseEmotion.SADNESS, BaseEmotion.HOPE],
        "valence_range": (0.0, 0.5),
        "typical_triggers": ["Sorge um geliebte Person", "Kinder in Gefahr", "Partner krank"]
    }
}


# ============================================================================
# HAUPTKLASSE: MIXED EMOTIONS ENGINE
# ============================================================================

class MixedEmotionsEngine:
    """
    Engine für die Verarbeitung und Generierung gemischter Emotionen.

    Diese Klasse ermöglicht:
    - Erkennung von gemischten Emotionen aus Kontext
    - Generierung passender emotionaler Reaktionen
    - Tracking der emotionalen Komplexität über Zeit
    - Verständnis für emotionale Nuancen
    """

    def __init__(self):
        self.current_mixed_emotion: Optional[MixedEmotion] = None
        self.emotion_history: List[MixedEmotion] = []
        self.nostalgia_triggers: Dict[str, NostalgiaExperience] = {}
        self.emotional_vocabulary: Dict[str, List[str]] = self._init_vocabulary()
        self.blend_preferences: Dict[EmotionBlendMode, float] = {
            EmotionBlendMode.SIMULTANEOUS: 0.3,
            EmotionBlendMode.OSCILLATING: 0.25,
            EmotionBlendMode.LAYERED: 0.25,
            EmotionBlendMode.INTEGRATED: 0.2
        }

    def _init_vocabulary(self) -> Dict[str, List[str]]:
        """Initialisiert emotionales Vokabular für Ausdrücke"""
        return {
            "bittersweet": [
                "bittersüß", "wehmütig-froh", "traurig-schön",
                "ein Lachen mit Tränen", "Freude mit einem Stich"
            ],
            "nostalgia": [
                "nostalgisch", "sehnsüchtig", "in Erinnerungen schwelgend",
                "die guten alten Zeiten", "süße Wehmut"
            ],
            "ambivalence": [
                "hin- und hergerissen", "zwiespältig", "unentschlossen",
                "gemischte Gefühle", "widersprüchlich"
            ],
            "melancholy": [
                "melancholisch", "schwermütig", "nachdenklich-traurig",
                "sanft traurig", "düster-schön"
            ],
            "anxious_excitement": [
                "aufgeregt-nervös", "ängstlich-freudig", "kribbelig",
                "mit Herzklopfen", "angespannt-erwartungsvoll"
            ]
        }

    # -------------------------------------------------------------------------
    # Erkennung und Analyse
    # -------------------------------------------------------------------------

    def detect_mixed_emotion(
        self,
        primary_emotions: List[Tuple[BaseEmotion, float]],
        context: Optional[str] = None
    ) -> Optional[MixedEmotion]:
        """
        Erkennt ob eine Kombination von Emotionen ein bekanntes gemischtes Gefühl ergibt.

        Args:
            primary_emotions: Liste von (Emotion, Intensität) Tupeln
            context: Optionaler Kontext für bessere Erkennung

        Returns:
            MixedEmotion wenn erkannt, sonst None
        """
        if len(primary_emotions) < 2:
            return None

        emotion_set = {e for e, _ in primary_emotions}

        # Prüfe gegen bekannte Rezepte
        for mixed_type, recipe in EMOTION_RECIPES.items():
            required = set(recipe["primary"])
            if required and required.issubset(emotion_set):
                # Match gefunden!
                components = [
                    EmotionComponent(
                        emotion=e,
                        intensity=i,
                        valence=self._get_emotion_valence(e),
                        arousal=self._get_emotion_arousal(e),
                        dominance=i
                    )
                    for e, i in primary_emotions
                ]

                overall = sum(i for _, i in primary_emotions) / len(primary_emotions)

                return MixedEmotion(
                    type=mixed_type,
                    components=components,
                    blend_mode=self._determine_blend_mode(components),
                    overall_intensity=overall,
                    context=context,
                    trigger=self._identify_trigger(mixed_type, context)
                )

        # Prüfe auf generelle Ambivalenz (gegensätzliche Valenzen)
        valences = [self._get_emotion_valence(e) for e, _ in primary_emotions]
        if max(valences) > 0.3 and min(valences) < -0.3:
            components = [
                EmotionComponent(
                    emotion=e,
                    intensity=i,
                    valence=self._get_emotion_valence(e),
                    arousal=self._get_emotion_arousal(e),
                    dominance=i
                )
                for e, i in primary_emotions
            ]

            return MixedEmotion(
                type=MixedEmotionType.AMBIVALENCE,
                components=components,
                blend_mode=EmotionBlendMode.OSCILLATING,
                overall_intensity=sum(i for _, i in primary_emotions) / len(primary_emotions),
                context=context
            )

        return None

    def analyze_emotional_complexity(
        self,
        text: str,
        detected_emotions: List[Tuple[BaseEmotion, float]]
    ) -> Dict:
        """
        Analysiert die emotionale Komplexität eines Textes/Kontexts.

        Returns:
            Dict mit Komplexitäts-Metriken
        """
        mixed = self.detect_mixed_emotion(detected_emotions, text)

        # Berechne verschiedene Komplexitäts-Dimensionen
        num_emotions = len(detected_emotions)
        valence_variance = self._calculate_valence_variance(detected_emotions)
        intensity_range = self._calculate_intensity_range(detected_emotions)

        return {
            "is_mixed": mixed is not None,
            "mixed_type": mixed.type.value if mixed else None,
            "complexity_score": self._compute_complexity_score(
                num_emotions, valence_variance, intensity_range
            ),
            "emotional_depth": "deep" if num_emotions > 3 else "moderate" if num_emotions > 1 else "simple",
            "valence_conflict": valence_variance > 0.5,
            "dominant_emotion": max(detected_emotions, key=lambda x: x[1])[0].value if detected_emotions else None,
            "secondary_emotions": [e.value for e, i in detected_emotions if i > 0.3][1:] if len(detected_emotions) > 1 else []
        }

    # -------------------------------------------------------------------------
    # Generierung und Ausdruck
    # -------------------------------------------------------------------------

    def generate_mixed_emotion(
        self,
        emotion_type: MixedEmotionType,
        intensity: float = 0.5,
        context: Optional[str] = None
    ) -> MixedEmotion:
        """
        Generiert ein gemischtes Gefühl eines bestimmten Typs.

        Args:
            emotion_type: Der gewünschte Typ des gemischten Gefühls
            intensity: Gesamtintensität (0.0 - 1.0)
            context: Optionaler Auslöser/Kontext

        Returns:
            Ein MixedEmotion-Objekt
        """
        recipe = EMOTION_RECIPES.get(emotion_type, {})
        primary_emotions = recipe.get("primary", [BaseEmotion.JOY, BaseEmotion.SADNESS])
        optional_emotions = recipe.get("optional", [])

        components = []

        # Primäre Emotionen hinzufügen
        for emotion in primary_emotions:
            component_intensity = intensity * random.uniform(0.7, 1.0)
            components.append(EmotionComponent(
                emotion=emotion,
                intensity=component_intensity,
                valence=self._get_emotion_valence(emotion),
                arousal=self._get_emotion_arousal(emotion) * intensity,
                dominance=component_intensity
            ))

        # Optional: Zusätzliche Emotionen
        if optional_emotions and random.random() > 0.5:
            extra = random.choice(optional_emotions)
            components.append(EmotionComponent(
                emotion=extra,
                intensity=intensity * random.uniform(0.3, 0.6),
                valence=self._get_emotion_valence(extra),
                arousal=self._get_emotion_arousal(extra) * intensity * 0.7,
                dominance=intensity * 0.4
            ))

        blend_mode = self._determine_blend_mode(components)

        mixed = MixedEmotion(
            type=emotion_type,
            components=components,
            blend_mode=blend_mode,
            overall_intensity=intensity,
            context=context,
            trigger=self._identify_trigger(emotion_type, context)
        )

        # Speichern in History
        self.current_mixed_emotion = mixed
        self.emotion_history.append(mixed)
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]

        return mixed

    def express_mixed_emotion(
        self,
        mixed_emotion: MixedEmotion,
        style: str = "natural"
    ) -> str:
        """
        Drückt ein gemischtes Gefühl in Worten aus.

        Args:
            mixed_emotion: Das auszudrückende Gefühl
            style: "natural", "poetic", "analytical"

        Returns:
            Textuelle Beschreibung des Gefühls
        """
        if style == "natural":
            return self._express_natural(mixed_emotion)
        elif style == "poetic":
            return self._express_poetic(mixed_emotion)
        elif style == "analytical":
            return self._express_analytical(mixed_emotion)
        else:
            return mixed_emotion.describe()

    def _express_natural(self, emotion: MixedEmotion) -> str:
        """Natürlicher Ausdruck eines gemischten Gefühls"""
        vocab = self.emotional_vocabulary.get(emotion.type.value, [])

        if emotion.overall_intensity > 0.7:
            prefix = "Ich fühle mich gerade sehr"
        elif emotion.overall_intensity > 0.4:
            prefix = "Ich empfinde gerade"
        else:
            prefix = "Es ist ein leises Gefühl von"

        descriptor = random.choice(vocab) if vocab else emotion.type.value

        components_text = ""
        if len(emotion.components) > 1:
            emotion_names = [c.emotion.value for c in emotion.components[:3]]
            components_text = f" - eine Mischung aus {', '.join(emotion_names)}"

        return f"{prefix} {descriptor}{components_text}."

    def _express_poetic(self, emotion: MixedEmotion) -> str:
        """Poetischer Ausdruck eines gemischten Gefühls"""
        poetic_templates = {
            MixedEmotionType.BITTERSWEET: [
                "Wie Honig mit einem Tropfen Salzwasser",
                "Sonnenschein durch Regentränen",
                "Ein Lächeln, das nach Abschied schmeckt"
            ],
            MixedEmotionType.NOSTALGIA: [
                "Die Vergangenheit flüstert durch vergilbte Seiten",
                "Schatten von Erinnerungen tanzen im Kerzenlicht",
                "Das Echo eines Liedes, das ich einst kannte"
            ],
            MixedEmotionType.MELANCHOLY: [
                "Wie Herbstblätter, die im Wind tanzen und fallen",
                "Die sanfte Schwere einer Regennacht",
                "Stille Schönheit in der Dämmerung"
            ],
            MixedEmotionType.ANXIOUS_EXCITEMENT: [
                "Ein Schmetterling mit Sturmflügeln im Bauch",
                "Am Rand einer Klippe, mit Flügeln aus Hoffnung",
                "Das Kribbeln vor dem Sprung ins Unbekannte"
            ]
        }

        templates = poetic_templates.get(emotion.type, ["Ein Gefühl wie Farben, die ineinander fließen"])
        return random.choice(templates)

    def _express_analytical(self, emotion: MixedEmotion) -> str:
        """Analytischer Ausdruck eines gemischten Gefühls"""
        components_analysis = []
        for c in emotion.components:
            components_analysis.append(
                f"{c.emotion.value}: {c.intensity:.0%} Intensität, "
                f"Valenz {c.valence:+.1f}, Arousal {c.arousal:.1f}"
            )

        return (
            f"Gemischte Emotion: {emotion.type.value}\n"
            f"Gesamtintensität: {emotion.overall_intensity:.0%}\n"
            f"Blend-Modus: {emotion.blend_mode.value}\n"
            f"Komplexität: {emotion.complexity:.0%}\n"
            f"Komponenten:\n" + "\n".join(f"  - {c}" for c in components_analysis)
        )

    # -------------------------------------------------------------------------
    # Nostalgie-spezifische Funktionen
    # -------------------------------------------------------------------------

    def trigger_nostalgia(
        self,
        memory: str,
        sensory_cue: Optional[str] = None
    ) -> MixedEmotion:
        """
        Löst ein Nostalgie-Gefühl basierend auf einer Erinnerung aus.

        Args:
            memory: Die auslösende Erinnerung
            sensory_cue: Optionaler sensorischer Auslöser (Geruch, Sound, etc.)

        Returns:
            Ein Nostalgie-MixedEmotion-Objekt
        """
        # Prüfe ob diese Erinnerung bereits bekannt ist
        if memory in self.nostalgia_triggers:
            experience = self.nostalgia_triggers[memory]
            # Verstärke die Erfahrung bei Wiederholung
            experience.sweetness = min(1.0, experience.sweetness + 0.05)
        else:
            # Neue Nostalgie-Erfahrung erstellen
            experience = NostalgiaExperience(
                memory_reference=memory,
                time_period="past",
                sweetness=random.uniform(0.5, 0.8),
                longing=random.uniform(0.3, 0.7),
                acceptance=random.uniform(0.4, 0.8),
                warmth=random.uniform(0.5, 0.9),
                associated_sensory=[sensory_cue] if sensory_cue else []
            )
            self.nostalgia_triggers[memory] = experience

        return experience.to_mixed_emotion()

    def get_nostalgia_intensity(self, time_distance: str) -> float:
        """
        Berechnet wie intensiv Nostalgie basierend auf zeitlicher Distanz sein sollte.

        Args:
            time_distance: "recent", "years_ago", "decades_ago", "childhood"

        Returns:
            Intensitäts-Multiplikator
        """
        intensity_map = {
            "recent": 0.4,          # Noch zu frisch für volle Nostalgie
            "years_ago": 0.7,       # Süßer Spot
            "decades_ago": 0.85,    # Intensiv
            "childhood": 0.95       # Am intensivsten
        }
        return intensity_map.get(time_distance, 0.6)

    # -------------------------------------------------------------------------
    # Hilfsfunktionen
    # -------------------------------------------------------------------------

    def _get_emotion_valence(self, emotion: BaseEmotion) -> float:
        """Gibt die typische Valenz einer Basisemotion zurück"""
        valence_map = {
            BaseEmotion.JOY: 0.8,
            BaseEmotion.SADNESS: -0.6,
            BaseEmotion.ANGER: -0.7,
            BaseEmotion.FEAR: -0.6,
            BaseEmotion.SURPRISE: 0.1,
            BaseEmotion.DISGUST: -0.7,
            BaseEmotion.TRUST: 0.5,
            BaseEmotion.ANTICIPATION: 0.3,
            BaseEmotion.LOVE: 0.9,
            BaseEmotion.GUILT: -0.5,
            BaseEmotion.SHAME: -0.6,
            BaseEmotion.PRIDE: 0.6,
            BaseEmotion.ENVY: -0.4,
            BaseEmotion.GRATITUDE: 0.7,
            BaseEmotion.HOPE: 0.6,
            BaseEmotion.CONTENTMENT: 0.5
        }
        return valence_map.get(emotion, 0.0)

    def _get_emotion_arousal(self, emotion: BaseEmotion) -> float:
        """Gibt das typische Arousal einer Basisemotion zurück"""
        arousal_map = {
            BaseEmotion.JOY: 0.7,
            BaseEmotion.SADNESS: 0.3,
            BaseEmotion.ANGER: 0.9,
            BaseEmotion.FEAR: 0.8,
            BaseEmotion.SURPRISE: 0.8,
            BaseEmotion.DISGUST: 0.5,
            BaseEmotion.TRUST: 0.3,
            BaseEmotion.ANTICIPATION: 0.6,
            BaseEmotion.LOVE: 0.6,
            BaseEmotion.GUILT: 0.4,
            BaseEmotion.SHAME: 0.5,
            BaseEmotion.PRIDE: 0.6,
            BaseEmotion.ENVY: 0.6,
            BaseEmotion.GRATITUDE: 0.4,
            BaseEmotion.HOPE: 0.5,
            BaseEmotion.CONTENTMENT: 0.2
        }
        return arousal_map.get(emotion, 0.5)

    def _determine_blend_mode(self, components: List[EmotionComponent]) -> EmotionBlendMode:
        """Bestimmt den passenden Blend-Modus für Komponenten"""
        if not components:
            return EmotionBlendMode.SIMULTANEOUS

        # Hoher Valenz-Kontrast → Oszillierend
        valences = [c.valence for c in components]
        if len(valences) >= 2 and (max(valences) - min(valences)) > 1.0:
            return EmotionBlendMode.OSCILLATING

        # Ähnliche Intensitäten → Integriert
        intensities = [c.intensity for c in components]
        if len(intensities) >= 2 and (max(intensities) - min(intensities)) < 0.3:
            return EmotionBlendMode.INTEGRATED

        # Eine dominante Emotion → Geschichtet
        if max(intensities) > 0.7 and (max(intensities) - sorted(intensities)[-2]) > 0.3:
            return EmotionBlendMode.LAYERED

        return EmotionBlendMode.SIMULTANEOUS

    def _identify_trigger(
        self,
        emotion_type: MixedEmotionType,
        context: Optional[str]
    ) -> Optional[str]:
        """Identifiziert den wahrscheinlichen Auslöser"""
        if not context:
            return None

        recipe = EMOTION_RECIPES.get(emotion_type, {})
        typical_triggers = recipe.get("typical_triggers", [])

        context_lower = context.lower()
        for trigger in typical_triggers:
            if trigger.lower() in context_lower:
                return trigger

        return None

    def _calculate_valence_variance(
        self,
        emotions: List[Tuple[BaseEmotion, float]]
    ) -> float:
        """Berechnet die Varianz der Valenzen"""
        if len(emotions) < 2:
            return 0.0

        valences = [self._get_emotion_valence(e) * i for e, i in emotions]
        mean = sum(valences) / len(valences)
        variance = sum((v - mean) ** 2 for v in valences) / len(valences)
        return math.sqrt(variance)

    def _calculate_intensity_range(
        self,
        emotions: List[Tuple[BaseEmotion, float]]
    ) -> float:
        """Berechnet die Spannweite der Intensitäten"""
        if not emotions:
            return 0.0
        intensities = [i for _, i in emotions]
        return max(intensities) - min(intensities)

    def _compute_complexity_score(
        self,
        num_emotions: int,
        valence_variance: float,
        intensity_range: float
    ) -> float:
        """Berechnet einen Gesamtkomplexitäts-Score"""
        # Gewichtete Kombination
        num_factor = min(1.0, num_emotions / 5.0) * 0.3
        variance_factor = min(1.0, valence_variance) * 0.5
        range_factor = intensity_range * 0.2

        return num_factor + variance_factor + range_factor

    # -------------------------------------------------------------------------
    # Emotionale Übergänge
    # -------------------------------------------------------------------------

    def transition_emotion(
        self,
        from_emotion: MixedEmotion,
        to_type: MixedEmotionType,
        transition_time: float = 1.0
    ) -> List[MixedEmotion]:
        """
        Erstellt einen sanften Übergang zwischen gemischten Emotionen.

        Args:
            from_emotion: Ausgangsgefühl
            to_type: Ziel-Emotionstyp
            transition_time: Zeit für den Übergang (normalisiert)

        Returns:
            Liste von Zwischenzuständen
        """
        steps = max(3, int(transition_time * 5))
        transitions = []

        to_emotion = self.generate_mixed_emotion(
            to_type,
            from_emotion.overall_intensity,
            from_emotion.context
        )

        for i in range(steps):
            progress = (i + 1) / steps

            # Interpoliere Komponenten
            blended_components = []

            # Von-Komponenten mit abnehmender Intensität
            for comp in from_emotion.components:
                blended_components.append(EmotionComponent(
                    emotion=comp.emotion,
                    intensity=comp.intensity * (1 - progress),
                    valence=comp.valence,
                    arousal=comp.arousal * (1 - progress),
                    dominance=comp.dominance * (1 - progress)
                ))

            # Zu-Komponenten mit zunehmender Intensität
            for comp in to_emotion.components:
                blended_components.append(EmotionComponent(
                    emotion=comp.emotion,
                    intensity=comp.intensity * progress,
                    valence=comp.valence,
                    arousal=comp.arousal * progress,
                    dominance=comp.dominance * progress
                ))

            # Filtere schwache Komponenten heraus
            blended_components = [c for c in blended_components if c.intensity > 0.1]

            # Erstelle Zwischenzustand
            if progress < 0.5:
                current_type = from_emotion.type
            else:
                current_type = to_type

            intermediate = MixedEmotion(
                type=current_type,
                components=blended_components,
                blend_mode=EmotionBlendMode.OSCILLATING,
                overall_intensity=from_emotion.overall_intensity,
                context=f"Übergang von {from_emotion.type.value} zu {to_type.value}"
            )

            transitions.append(intermediate)

        return transitions

    # -------------------------------------------------------------------------
    # Kontext-basierte Emotionsgenerierung
    # -------------------------------------------------------------------------

    def suggest_mixed_emotion_for_context(self, context: str) -> Optional[MixedEmotionType]:
        """
        Schlägt einen passenden gemischten Emotionstyp für einen Kontext vor.

        Args:
            context: Beschreibung der Situation

        Returns:
            Passender MixedEmotionType oder None
        """
        context_lower = context.lower()

        # Schlüsselwort-basierte Erkennung
        keyword_mapping = {
            MixedEmotionType.NOSTALGIA: [
                "erinnerung", "früher", "damals", "kindheit", "alte zeiten",
                "vermissen", "zurückdenken", "memory", "past"
            ],
            MixedEmotionType.BITTERSWEET: [
                "abschied", "ende", "letztes mal", "goodbye", "farewell",
                "erfolg mit opfer", "traurig aber"
            ],
            MixedEmotionType.ANXIOUS_EXCITEMENT: [
                "nervös", "aufgeregt", "gespannt", "neuer job", "erstes",
                "präsentation", "date", "abenteuer"
            ],
            MixedEmotionType.MELANCHOLY: [
                "regen", "herbst", "allein", "nachdenklich", "grau",
                "einsam", "still", "düster"
            ],
            MixedEmotionType.GUILTY_PLEASURE: [
                "sollte nicht", "verboten", "heimlich", "guilty",
                "schlecht aber", "sünde"
            ],
            MixedEmotionType.HOPEFUL_FEAR: [
                "hoffe", "angst", "warten", "ergebnis", "ungewiss",
                "chance", "risiko"
            ],
            MixedEmotionType.LOVING_CONCERN: [
                "sorge", "liebe", "krank", "gefahr", "beschützen",
                "angst um"
            ]
        }

        for emotion_type, keywords in keyword_mapping.items():
            for keyword in keywords:
                if keyword in context_lower:
                    return emotion_type

        return None

    def get_emotional_response_to_event(
        self,
        event_type: str,
        personal_relevance: float
    ) -> Optional[MixedEmotion]:
        """
        Generiert eine emotionale Reaktion auf ein Ereignis.

        Args:
            event_type: Art des Ereignisses
            personal_relevance: Wie relevant für die Person (0.0 - 1.0)

        Returns:
            Passende MixedEmotion oder None
        """
        event_emotion_mapping = {
            "farewell": MixedEmotionType.BITTERSWEET,
            "reunion": MixedEmotionType.NOSTALGIA,
            "new_opportunity": MixedEmotionType.ANXIOUS_EXCITEMENT,
            "loss": MixedEmotionType.TENDER_SADNESS,
            "achievement": MixedEmotionType.PROUD_HUMILITY,
            "waiting": MixedEmotionType.HOPEFUL_FEAR,
            "temptation": MixedEmotionType.GUILTY_PLEASURE,
            "loved_one_risk": MixedEmotionType.LOVING_CONCERN,
            "autumn_day": MixedEmotionType.MELANCHOLY
        }

        emotion_type = event_emotion_mapping.get(event_type)
        if emotion_type:
            return self.generate_mixed_emotion(
                emotion_type,
                intensity=personal_relevance,
                context=event_type
            )

        return None


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def is_emotion_mixed(emotions: List[Tuple[BaseEmotion, float]]) -> bool:
    """
    Prüft ob eine Emotionsliste gemischte Gefühle darstellt.

    Args:
        emotions: Liste von (Emotion, Intensität) Tupeln

    Returns:
        True wenn Emotionen als gemischt gelten
    """
    if len(emotions) < 2:
        return False

    # Prüfe auf Valenz-Kontrast
    engine = MixedEmotionsEngine()
    valences = [engine._get_emotion_valence(e) for e, _ in emotions]

    has_positive = any(v > 0.3 for v in valences)
    has_negative = any(v < -0.3 for v in valences)

    return has_positive and has_negative


def describe_emotional_blend(
    emotions: List[Tuple[BaseEmotion, float]]
) -> str:
    """
    Beschreibt eine Mischung von Emotionen in natürlicher Sprache.

    Args:
        emotions: Liste von (Emotion, Intensität) Tupeln

    Returns:
        Natürlichsprachliche Beschreibung
    """
    if not emotions:
        return "Keine erkennbaren Emotionen"

    if len(emotions) == 1:
        e, i = emotions[0]
        intensity_word = "starke" if i > 0.7 else "moderate" if i > 0.4 else "leichte"
        return f"{intensity_word} {e.value}"

    # Sortiere nach Intensität
    sorted_emotions = sorted(emotions, key=lambda x: x[1], reverse=True)

    primary = sorted_emotions[0][0].value
    secondary = sorted_emotions[1][0].value

    if len(sorted_emotions) > 2:
        tertiary = sorted_emotions[2][0].value
        return f"hauptsächlich {primary}, vermischt mit {secondary} und einem Hauch von {tertiary}"

    return f"eine Mischung aus {primary} und {secondary}"


# ============================================================================
# ALIASE FÜR RÜCKWÄRTSKOMPATIBILITÄT
# ============================================================================

# holo_brain.py erwartet diese Namen
MixedEmotionAnalyzer = MixedEmotionsEngine
EmotionalBlend = MixedEmotion


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "BaseEmotion",
    "MixedEmotionType",
    "EmotionBlendMode",

    # Dataclasses
    "EmotionComponent",
    "MixedEmotion",
    "NostalgiaExperience",
    "AmbivalentState",
    "EmotionalBlend",  # Alias

    # Main class
    "MixedEmotionsEngine",
    "MixedEmotionAnalyzer",  # Alias

    # Helper functions
    "is_emotion_mixed",
    "describe_emotional_blend",

    # Constants
    "MIXED_EMOTION_DESCRIPTIONS",
    "EMOTION_RECIPES"
]
