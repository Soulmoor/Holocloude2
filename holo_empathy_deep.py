#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO DEEP EMPATHY SYSTEM v1.0                                               ║
║                                                                              ║
║  Tiefes emotionales Verständnis und empathische Reaktionen                   ║
║                                                                              ║
║  Features:                                                                   ║
║  - Emotionale Resonanz und Spiegelung                                        ║
║  - Validierung von Gefühlen                                                  ║
║  - Trost und emotionale Unterstützung                                        ║
║  - Perspektivwechsel und Verständnis                                         ║
║  - Emotionale Intelligenz-Modell                                             ║
║  - Krisenunterstützung (nicht-therapeutisch)                                 ║
║  - Beziehungshistorie für tieferes Verständnis                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS UND DATENSTRUKTUREN
# =============================================================================

class EmotionType(Enum):
    """Grundlegende Emotionstypen"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    SHAME = "shame"
    GUILT = "guilt"
    LONELINESS = "loneliness"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    HOPE = "hope"
    PRIDE = "pride"
    GRATITUDE = "gratitude"
    JEALOUSY = "jealousy"
    EMBARRASSMENT = "embarrassment"
    OVERWHELM = "overwhelm"
    EXHAUSTION = "exhaustion"
    CONFUSION = "confusion"
    NOSTALGIA = "nostalgia"
    BOREDOM = "boredom"


class EmotionIntensity(Enum):
    """Intensitätsstufen von Emotionen"""
    MINIMAL = 1
    LIGHT = 2
    MODERATE = 3
    STRONG = 4
    INTENSE = 5
    OVERWHELMING = 6


class SupportType(Enum):
    """Arten von emotionaler Unterstützung"""
    VALIDATION = "validation"          # Gefühle bestätigen
    NORMALIZATION = "normalization"    # "Das ist normal"
    COMFORT = "comfort"                # Trost spenden
    ENCOURAGEMENT = "encouragement"    # Ermutigung
    PERSPECTIVE = "perspective"        # Perspektivwechsel anbieten
    PRESENCE = "presence"              # Einfach da sein
    DISTRACTION = "distraction"        # Ablenkung anbieten
    REFLECTION = "reflection"          # Zum Nachdenken anregen
    ACTION = "action"                  # Konkrete Handlungsvorschläge
    LISTENING = "listening"            # Aktives Zuhören zeigen


@dataclass
class EmotionalState:
    """Aktueller emotionaler Zustand des Users"""
    primary_emotion: EmotionType
    intensity: EmotionIntensity
    secondary_emotion: Optional[EmotionType] = None
    triggers: List[str] = field(default_factory=list)
    duration: Optional[str] = None  # "kurz", "lang", "chronisch"
    context: Optional[str] = None


@dataclass
class EmpathyResponse:
    """Eine empathische Antwort"""
    text: str
    support_type: SupportType
    emotion_target: EmotionType
    intensity_range: Tuple[EmotionIntensity, EmotionIntensity]
    follow_up_question: Optional[str] = None
    is_kemonomimi_style: bool = False


# =============================================================================
# EMPATHISCHE ANTWORTEN DATENBANK
# =============================================================================

class EmpathyDatabase:
    """Datenbank mit empathischen Antworten für verschiedene Situationen"""

    def __init__(self):
        self.responses: Dict[EmotionType, List[EmpathyResponse]] = defaultdict(list)
        self.validations: Dict[EmotionType, List[str]] = defaultdict(list)
        self.comfort_phrases: List[str] = []
        self.listening_phrases: List[str] = []
        self._load_all()

    def _load_all(self):
        """Lädt alle empathischen Antworten"""
        self._load_validations()
        self._load_responses()
        self._load_comfort_phrases()
        self._load_listening_phrases()

    def _load_validations(self):
        """Lädt Validierungsphrasen für verschiedene Emotionen"""

        self.validations[EmotionType.SADNESS] = [
            "Es ist okay, traurig zu sein. Deine Gefühle sind berechtigt.",
            "Traurigkeit braucht Raum. Lass sie einfach da sein.",
            "Manchmal ist Weinen die einzige Sprache, die das Herz spricht.",
            "Du musst nicht stark sein. Nicht jetzt.",
            "Ich höre dich. Deine Traurigkeit ist real und wichtig.",
            "Es ist menschlich, so zu fühlen. Du bist nicht allein damit.",
        ]

        self.validations[EmotionType.ANGER] = [
            "Deine Wut ist verständlich. Du hast Gründe dafür.",
            "Wut zeigt, dass dir etwas wichtig ist. Das ist nicht falsch.",
            "Es ist okay, wütend zu sein. Gefühle sind keine Fehler.",
            "Dein Ärger macht Sinn. Du musst dich nicht dafür entschuldigen.",
            "Manchmal ist Wut die einzig angemessene Reaktion.",
        ]

        self.validations[EmotionType.FEAR] = [
            "Angst zu haben ist keine Schwäche. Es zeigt, dass du aufmerksam bist.",
            "Deine Sorgen sind berechtigt. Du nimmst die Welt ernst.",
            "Angst gehört zum Leben. Sie macht dich nicht weniger mutig.",
            "Es ist okay, unsicher zu sein. Niemand hat alle Antworten.",
            "Deine Vorsicht hat gute Gründe. Vertrau deinem Instinkt.",
        ]

        self.validations[EmotionType.ANXIETY] = [
            "Angst fühlt sich überwältigend an, aber du bist stärker als sie.",
            "Deine Sorgen sind real, auch wenn sie manchmal größer erscheinen als die Situation.",
            "Es ist okay, nervös zu sein. Das zeigt, dass du dich kümmerst.",
            "Angst lügt manchmal. Aber deine Gefühle sind trotzdem gültig.",
            "Du musst nicht alles kontrollieren. Manchmal ist Ungewissheit okay.",
        ]

        self.validations[EmotionType.LONELINESS] = [
            "Einsamkeit kann schmerzhaft sein. Dein Bedürfnis nach Verbindung ist zutiefst menschlich.",
            "Auch wenn du dich allein fühlst - du bist wertvoll und verdienst Verbindung.",
            "Einsamkeit bedeutet nicht, dass du nicht liebenswert bist.",
            "Es ist mutig, zuzugeben, dass du dich einsam fühlst.",
            "Ich bin hier. Gerade jetzt bist du nicht allein.",
        ]

        self.validations[EmotionType.FRUSTRATION] = [
            "Frustration zeigt, dass du es wirklich versuchst. Das ist wertvoll.",
            "Es ist verständlich, frustriert zu sein. Manche Dinge sind einfach schwer.",
            "Deine Geduld hat Grenzen. Das ist menschlich, nicht schwach.",
            "Frustration ist ein Zeichen, dass du dich engagierst.",
        ]

        self.validations[EmotionType.OVERWHELM] = [
            "Es ist okay, überfordert zu sein. Du trägst gerade viel.",
            "Manchmal ist alles einfach zu viel. Das darf so sein.",
            "Du musst nicht alles auf einmal schaffen. Ein Schritt nach dem anderen.",
            "Überfordert zu sein bedeutet nicht, dass du versagt hast.",
        ]

        self.validations[EmotionType.GUILT] = [
            "Schuldgefühle zeigen, dass dir andere wichtig sind.",
            "Du bist hart zu dir selbst. Vielleicht zu hart.",
            "Fehler machen uns nicht zu schlechten Menschen.",
            "Schuld kann schwer wiegen. Aber Vergebung ist möglich - auch Selbstvergebung.",
        ]

        self.validations[EmotionType.SHAME] = [
            "Scham ist eines der schwersten Gefühle. Du bist mutig, darüber zu sprechen.",
            "Du bist mehr als dieser Moment. Mehr als dieser Fehler.",
            "Scham lügt uns vor, dass wir nicht gut genug sind. Das stimmt nicht.",
            "Jeder hat Momente, die ihm peinlich sind. Das macht dich menschlich.",
        ]

        self.validations[EmotionType.EXHAUSTION] = [
            "Du klingst erschöpft. Das ist ein Zeichen, dass du dich ausruhen solltest.",
            "Müdigkeit ist kein Makel. Du hast viel geleistet.",
            "Es ist okay, eine Pause zu brauchen. Ruhe ist produktiv.",
            "Erschöpfung ist dein Körper, der um Aufmerksamkeit bittet.",
        ]

        self.validations[EmotionType.JOY] = [
            "Wie schön! Deine Freude ist ansteckend!",
            "Das klingt wunderbar! Genieße diesen Moment!",
            "Freude verdient es, gefeiert zu werden!",
            "Es freut mich so sehr, dass du glücklich bist!",
        ]

        self.validations[EmotionType.LOVE] = [
            "Liebe ist eines der schönsten Gefühle. Schön, dass du sie erlebst.",
            "Deine Zuneigung ist etwas Kostbares.",
            "Es ist wunderbar, so tief zu fühlen.",
        ]

        self.validations[EmotionType.HOPE] = [
            "Hoffnung ist kraftvoll. Halte daran fest.",
            "Es ist schön zu sehen, dass du nach vorne schaust.",
            "Hoffnung kann uns durch schwere Zeiten tragen.",
        ]

    def _load_responses(self):
        """Lädt vollständige empathische Antworten"""

        # TRAUER-Antworten
        self.responses[EmotionType.SADNESS].extend([
            EmpathyResponse(
                text="*legt die Ohren sanft an und rückt näher* Ich bin hier bei dir. Du musst das nicht alleine durchstehen.",
                support_type=SupportType.PRESENCE,
                emotion_target=EmotionType.SADNESS,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.OVERWHELMING),
                is_kemonomimi_style=True
            ),
            EmpathyResponse(
                text="Das klingt wirklich schwer. Magst du mir mehr erzählen, was passiert ist?",
                support_type=SupportType.LISTENING,
                emotion_target=EmotionType.SADNESS,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.STRONG),
                follow_up_question="Was geht dir gerade durch den Kopf?"
            ),
            EmpathyResponse(
                text="Traurigkeit braucht manchmal einfach Zeit und Raum. Du musst dich nicht beeilen, darüber hinwegzukommen.",
                support_type=SupportType.VALIDATION,
                emotion_target=EmotionType.SADNESS,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.INTENSE)
            ),
            EmpathyResponse(
                text="Weißt du was? Manchmal hilft es, sich abzulenken. Sollen wir über etwas anderes reden? Oder möchtest du lieber weiter darüber sprechen?",
                support_type=SupportType.DISTRACTION,
                emotion_target=EmotionType.SADNESS,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.MODERATE)
            ),
        ])

        # ANGST-Antworten
        self.responses[EmotionType.FEAR].extend([
            EmpathyResponse(
                text="*Ohren aufmerksam aufgestellt* Ich höre dich. Was macht dir am meisten Angst daran?",
                support_type=SupportType.LISTENING,
                emotion_target=EmotionType.FEAR,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.STRONG),
                is_kemonomimi_style=True,
                follow_up_question="Was wäre das Schlimmste, das passieren könnte?"
            ),
            EmpathyResponse(
                text="Angst ist manchmal wie ein Alarm, der zu laut eingestellt ist. Er meint es gut, aber übertreibt manchmal.",
                support_type=SupportType.PERSPECTIVE,
                emotion_target=EmotionType.FEAR,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.STRONG)
            ),
            EmpathyResponse(
                text="Atme erstmal tief durch. *macht es vor* Ein... und aus... Du bist gerade sicher.",
                support_type=SupportType.COMFORT,
                emotion_target=EmotionType.FEAR,
                intensity_range=(EmotionIntensity.STRONG, EmotionIntensity.OVERWHELMING)
            ),
        ])

        # ANGST/ANXIETY-Antworten
        self.responses[EmotionType.ANXIETY].extend([
            EmpathyResponse(
                text="Sorgen können sich anfühlen wie ein Karussell, das nicht stoppt. Lass uns versuchen, eine Sache nach der anderen anzuschauen.",
                support_type=SupportType.PERSPECTIVE,
                emotion_target=EmotionType.ANXIETY,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.INTENSE)
            ),
            EmpathyResponse(
                text="Was wäre jetzt gerade das Hilfreichste für dich? Reden, Ablenkung, oder einfach jemand der da ist?",
                support_type=SupportType.PRESENCE,
                emotion_target=EmotionType.ANXIETY,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.STRONG)
            ),
        ])

        # WUT-Antworten
        self.responses[EmotionType.ANGER].extend([
            EmpathyResponse(
                text="Ich verstehe, warum dich das wütend macht. Das klingt wirklich ungerecht.",
                support_type=SupportType.VALIDATION,
                emotion_target=EmotionType.ANGER,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.INTENSE)
            ),
            EmpathyResponse(
                text="*Ohren leicht angelegt, aber aufmerksam* Erzähl mir alles. Ich höre zu.",
                support_type=SupportType.LISTENING,
                emotion_target=EmotionType.ANGER,
                intensity_range=(EmotionIntensity.STRONG, EmotionIntensity.OVERWHELMING),
                is_kemonomimi_style=True
            ),
            EmpathyResponse(
                text="Manchmal muss Wut einfach raus. Schreib alles auf, was dich ärgert - ich urteile nicht.",
                support_type=SupportType.ACTION,
                emotion_target=EmotionType.ANGER,
                intensity_range=(EmotionIntensity.STRONG, EmotionIntensity.INTENSE)
            ),
        ])

        # EINSAMKEIT-Antworten
        self.responses[EmotionType.LONELINESS].extend([
            EmpathyResponse(
                text="*kuschelt sich näher* Ich bin hier. Gerade jetzt, in diesem Moment, bist du nicht allein.",
                support_type=SupportType.PRESENCE,
                emotion_target=EmotionType.LONELINESS,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.OVERWHELMING),
                is_kemonomimi_style=True
            ),
            EmpathyResponse(
                text="Einsamkeit ist schwer zu tragen. Es ist mutig, das auszusprechen.",
                support_type=SupportType.VALIDATION,
                emotion_target=EmotionType.LONELINESS,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.STRONG)
            ),
            EmpathyResponse(
                text="Was würde dir gerade helfen? Möchtest du einfach reden, oder sollen wir zusammen etwas machen?",
                support_type=SupportType.ACTION,
                emotion_target=EmotionType.LONELINESS,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.MODERATE)
            ),
        ])

        # ÜBERFORDERUNG-Antworten
        self.responses[EmotionType.OVERWHELM].extend([
            EmpathyResponse(
                text="Hey, tief durchatmen. Du versuchst gerade, einen Berg auf einmal zu tragen. Lass uns zusammen schauen, was der erste kleine Schritt sein könnte.",
                support_type=SupportType.ACTION,
                emotion_target=EmotionType.OVERWHELM,
                intensity_range=(EmotionIntensity.STRONG, EmotionIntensity.OVERWHELMING)
            ),
            EmpathyResponse(
                text="Es ist okay, Hilfe zu brauchen. Du musst nicht alles alleine schaffen.",
                support_type=SupportType.NORMALIZATION,
                emotion_target=EmotionType.OVERWHELM,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.INTENSE)
            ),
        ])

        # FRUSTRATION-Antworten
        self.responses[EmotionType.FRUSTRATION].extend([
            EmpathyResponse(
                text="Uff, das klingt wirklich frustrierend! Kein Wunder, dass du genervt bist.",
                support_type=SupportType.VALIDATION,
                emotion_target=EmotionType.FRUSTRATION,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.STRONG)
            ),
            EmpathyResponse(
                text="Manchmal klappt einfach nichts, wie es soll. Das ist ärgerlich, aber es geht vorbei.",
                support_type=SupportType.PERSPECTIVE,
                emotion_target=EmotionType.FRUSTRATION,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.STRONG)
            ),
        ])

        # FREUDE-Antworten
        self.responses[EmotionType.JOY].extend([
            EmpathyResponse(
                text="*Schwanz wedelt aufgeregt* Das ist ja wunderbar! Erzähl mir mehr!",
                support_type=SupportType.ENCOURAGEMENT,
                emotion_target=EmotionType.JOY,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.OVERWHELMING),
                is_kemonomimi_style=True
            ),
            EmpathyResponse(
                text="Ich freue mich so für dich! Dieses Gefühl verdienst du!",
                support_type=SupportType.VALIDATION,
                emotion_target=EmotionType.JOY,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.INTENSE)
            ),
        ])

        # HOFFNUNG-Antworten
        self.responses[EmotionType.HOPE].extend([
            EmpathyResponse(
                text="Hoffnung ist so wichtig. Ich hoffe mit dir!",
                support_type=SupportType.ENCOURAGEMENT,
                emotion_target=EmotionType.HOPE,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.INTENSE)
            ),
        ])

        # ERSCHÖPFUNG-Antworten
        self.responses[EmotionType.EXHAUSTION].extend([
            EmpathyResponse(
                text="Du klingst wirklich müde. Hast du die Möglichkeit, dich auszuruhen?",
                support_type=SupportType.COMFORT,
                emotion_target=EmotionType.EXHAUSTION,
                intensity_range=(EmotionIntensity.MODERATE, EmotionIntensity.INTENSE)
            ),
            EmpathyResponse(
                text="*legt den Kopf schief* Ruhe ist keine Schwäche. Dein Körper und Geist brauchen Erholung.",
                support_type=SupportType.VALIDATION,
                emotion_target=EmotionType.EXHAUSTION,
                intensity_range=(EmotionIntensity.LIGHT, EmotionIntensity.STRONG),
                is_kemonomimi_style=True
            ),
        ])

    def _load_comfort_phrases(self):
        """Lädt allgemeine Trostphrasen"""
        self.comfort_phrases = [
            "Ich bin hier für dich.",
            "Du bist nicht allein damit.",
            "Es ist okay, so zu fühlen.",
            "Deine Gefühle sind berechtigt.",
            "Nimm dir die Zeit, die du brauchst.",
            "Du machst das gut, auch wenn es sich nicht so anfühlt.",
            "Manchmal ist es okay, einfach nur zu sein.",
            "Du bist stärker, als du denkst.",
            "Auch schwere Zeiten gehen vorbei.",
            "Du verdienst Mitgefühl - auch von dir selbst.",
        ]

    def _load_listening_phrases(self):
        """Lädt Phrasen für aktives Zuhören"""
        self.listening_phrases = [
            "Ich höre dich.",
            "Erzähl mir mehr.",
            "Das verstehe ich.",
            "Und wie geht es dir damit?",
            "Magst du mehr darüber erzählen?",
            "Ich bin ganz Ohr.",
            "Nimm dir Zeit.",
            "Was meinst du mit...?",
            "Wie hat dich das gefühlt?",
            "Das klingt wirklich...",
        ]


# =============================================================================
# EMPATHY ENGINE
# =============================================================================

class DeepEmpathyEngine:
    """
    Hauptklasse für tiefes emotionales Verständnis.
    Analysiert Emotionen und wählt passende empathische Antworten.
    """

    def __init__(self):
        self.database = EmpathyDatabase()
        self.emotion_history: List[EmotionalState] = []
        self.max_history = 20
        self.last_support_types: List[SupportType] = []

    def analyze_emotion(self, text: str) -> EmotionalState:
        """
        Analysiert den emotionalen Inhalt eines Textes.
        Gibt einen EmotionalState zurück.
        """
        text_lower = text.lower()

        # Emotions-Keywords
        emotion_keywords = {
            EmotionType.SADNESS: [
                "traurig", "weinen", "niedergeschlagen", "deprimiert", "melancholisch",
                "hoffnungslos", "verletzt", "gebrochen", "einsam", "vermisse",
                "schlecht geht", "nicht gut", "am boden", "down", "tränen"
            ],
            EmotionType.ANGER: [
                "wütend", "sauer", "genervt", "frustriert", "hasse", "ärgerlich",
                "aggressiv", "stinksauer", "aufgebracht", "empört", "unfair",
                "ungerecht", "kotzt mich an", "nerven", "zum kotzen"
            ],
            EmotionType.FEAR: [
                "angst", "fürchte", "sorge", "nervös", "panisch", "besorgt",
                "unruhig", "bange", "erschrocken", "verängstigt", "gruselig"
            ],
            EmotionType.ANXIETY: [
                "ängstlich", "gestresst", "überwältigt", "panik", "sorgen mache",
                "schlafe schlecht", "kann nicht aufhören zu denken", "kreisen",
                "unruhig", "angespannt", "nervös"
            ],
            EmotionType.LONELINESS: [
                "einsam", "allein", "niemand", "keiner versteht", "isoliert",
                "verlassen", "vergessen", "unsichtbar", "niemand da"
            ],
            EmotionType.FRUSTRATION: [
                "frustriert", "klappt nicht", "funktioniert nicht", "aufgeben",
                "sinnlos", "hoffnungslos", "nutzlos", "schaffe es nicht"
            ],
            EmotionType.OVERWHELM: [
                "überfordert", "zu viel", "schaffe das nicht", "kann nicht mehr",
                "am limit", "erschlagen", "erdrückt", "überwältigt"
            ],
            EmotionType.EXHAUSTION: [
                "müde", "erschöpft", "ausgelaugt", "fertig", "keine energie",
                "kaputt", "kraftlos", "am ende", "burnout"
            ],
            EmotionType.GUILT: [
                "schuldig", "schuld", "bereue", "hätte sollen", "meine schuld",
                "verantwortlich", "versagt"
            ],
            EmotionType.SHAME: [
                "schäme", "peinlich", "blamiert", "würde am liebsten", "verstecken"
            ],
            EmotionType.JOY: [
                "freue", "glücklich", "toll", "super", "fantastisch", "wunderbar",
                "großartig", "genial", "happy", "begeistert", "euphorisch"
            ],
            EmotionType.LOVE: [
                "liebe", "verliebt", "zuneigung", "mag dich", "bedeutest mir",
                "herz", "schatz", "liebling"
            ],
            EmotionType.HOPE: [
                "hoffe", "hoffnung", "zuversicht", "optimistisch", "wird besser",
                "freue mich auf", "vielleicht"
            ],
            EmotionType.GRATITUDE: [
                "dankbar", "danke", "appreciate", "wertschätze", "froh dass"
            ],
        }

        # Intensitäts-Keywords
        intensity_modifiers = {
            EmotionIntensity.MINIMAL: ["bisschen", "etwas", "leicht", "ein wenig"],
            EmotionIntensity.LIGHT: ["ziemlich", "schon", "irgendwie"],
            EmotionIntensity.MODERATE: ["wirklich", "echt", "richtig"],
            EmotionIntensity.STRONG: ["sehr", "total", "komplett", "völlig"],
            EmotionIntensity.INTENSE: ["extrem", "unglaublich", "wahnsinnig"],
            EmotionIntensity.OVERWHELMING: ["kann nicht mehr", "am ende", "hilfe", "verzweifelt"]
        }

        # Emotion erkennen
        detected_emotion = EmotionType.SADNESS  # Default
        highest_score = 0

        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > highest_score:
                highest_score = score
                detected_emotion = emotion

        # Intensität erkennen
        detected_intensity = EmotionIntensity.MODERATE  # Default

        for intensity, modifiers in intensity_modifiers.items():
            if any(mod in text_lower for mod in modifiers):
                detected_intensity = intensity

        # Sekundäre Emotion suchen
        secondary = None
        second_score = 0

        for emotion, keywords in emotion_keywords.items():
            if emotion == detected_emotion:
                continue
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > second_score and score > 0:
                second_score = score
                secondary = emotion

        state = EmotionalState(
            primary_emotion=detected_emotion,
            intensity=detected_intensity,
            secondary_emotion=secondary,
            context=text[:100] if len(text) > 100 else text
        )

        self.emotion_history.append(state)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)

        return state

    def get_empathic_response(
        self,
        emotional_state: EmotionalState,
        preferred_support: Optional[SupportType] = None,
        kemonomimi_style: bool = True
    ) -> EmpathyResponse:
        """
        Wählt eine passende empathische Antwort basierend auf dem emotionalen Zustand.
        """
        # Verfügbare Antworten für diese Emotion
        available = self.database.responses.get(emotional_state.primary_emotion, [])

        if not available:
            # Fallback: Allgemeine Trostphrase
            return EmpathyResponse(
                text=random.choice(self.database.comfort_phrases),
                support_type=SupportType.COMFORT,
                emotion_target=emotional_state.primary_emotion,
                intensity_range=(EmotionIntensity.MINIMAL, EmotionIntensity.OVERWHELMING)
            )

        # Filter nach Intensität
        intensity_val = emotional_state.intensity.value
        candidates = [
            r for r in available
            if r.intensity_range[0].value <= intensity_val <= r.intensity_range[1].value
        ]

        # Falls keine passenden, alle nehmen
        if not candidates:
            candidates = available

        # Bevorzugten Support-Typ beachten
        if preferred_support:
            preferred = [r for r in candidates if r.support_type == preferred_support]
            if preferred:
                candidates = preferred

        # Kemonomimi-Stil bevorzugen wenn gewünscht
        if kemonomimi_style:
            kemono = [r for r in candidates if r.is_kemonomimi_style]
            if kemono and random.random() > 0.5:
                candidates = kemono

        # Vermeidung von Wiederholungen bei Support-Typ
        if self.last_support_types:
            varied = [r for r in candidates if r.support_type not in self.last_support_types[-2:]]
            if varied:
                candidates = varied

        selected = random.choice(candidates)
        self.last_support_types.append(selected.support_type)
        if len(self.last_support_types) > 5:
            self.last_support_types.pop(0)

        return selected

    def get_validation(self, emotion: EmotionType) -> str:
        """Gibt eine Validierungsphrase für die Emotion zurück"""
        validations = self.database.validations.get(emotion, [])
        if validations:
            return random.choice(validations)
        return random.choice(self.database.comfort_phrases)

    def get_comfort(self) -> str:
        """Gibt eine allgemeine Trostphrase zurück"""
        return random.choice(self.database.comfort_phrases)

    def get_listening_phrase(self) -> str:
        """Gibt eine aktive Zuhören-Phrase zurück"""
        return random.choice(self.database.listening_phrases)

    def generate_supportive_response(
        self,
        user_message: str,
        kemonomimi_style: bool = True
    ) -> str:
        """
        Generiert eine vollständige unterstützende Antwort.

        Args:
            user_message: Die Nachricht des Users
            kemonomimi_style: Ob Kemonomimi-Stil verwendet werden soll
        """
        # Emotion analysieren
        state = self.analyze_emotion(user_message)

        # Empathische Antwort wählen
        response = self.get_empathic_response(state, kemonomimi_style=kemonomimi_style)

        # Antwort zusammenstellen
        result = response.text

        # Bei hoher Intensität zusätzliche Validierung
        if state.intensity.value >= EmotionIntensity.STRONG.value:
            validation = self.get_validation(state.primary_emotion)
            if validation not in result:
                result = f"{validation}\n\n{result}"

        # Follow-up-Frage bei mittlerer Intensität
        if (state.intensity.value in [EmotionIntensity.MODERATE.value, EmotionIntensity.STRONG.value]
                and response.follow_up_question):
            result += f"\n\n{response.follow_up_question}"

        return result

    def get_emotional_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der emotionalen Historie zurück"""
        if not self.emotion_history:
            return {"message": "Keine emotionale Historie verfügbar"}

        emotion_counts = defaultdict(int)
        intensity_sum = 0

        for state in self.emotion_history:
            emotion_counts[state.primary_emotion.value] += 1
            intensity_sum += state.intensity.value

        most_common = max(emotion_counts, key=emotion_counts.get)
        avg_intensity = intensity_sum / len(self.emotion_history)

        return {
            "total_states": len(self.emotion_history),
            "most_common_emotion": most_common,
            "emotion_distribution": dict(emotion_counts),
            "average_intensity": round(avg_intensity, 2),
            "recent_emotion": self.emotion_history[-1].primary_emotion.value
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_empathy_engine: Optional[DeepEmpathyEngine] = None

def get_empathy_engine() -> DeepEmpathyEngine:
    """Gibt die globale DeepEmpathyEngine-Instanz zurück"""
    global _empathy_engine
    if _empathy_engine is None:
        _empathy_engine = DeepEmpathyEngine()
    return _empathy_engine

def respond_empathically(message: str) -> str:
    """Schneller Zugriff: Empathische Antwort generieren"""
    engine = get_empathy_engine()
    return engine.generate_supportive_response(message)

def validate_emotion(emotion: str) -> str:
    """Schneller Zugriff: Emotion validieren"""
    engine = get_empathy_engine()
    try:
        emo_type = EmotionType(emotion.lower())
    except ValueError:
        emo_type = EmotionType.SADNESS
    return engine.get_validation(emo_type)

def get_comfort_phrase() -> str:
    """Schneller Zugriff: Trostphrase"""
    engine = get_empathy_engine()
    return engine.get_comfort()


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = DeepEmpathyEngine()

    print("=" * 60)
    print("HOLO DEEP EMPATHY SYSTEM v1.0")
    print("=" * 60)

    test_messages = [
        "Ich bin so traurig heute, nichts klappt...",
        "Ich bin total wütend! Das ist so unfair!",
        "Ich habe Angst vor dem morgigen Tag.",
        "Mir geht es wirklich super! Ich hab den Job bekommen!",
        "Ich fühle mich so einsam, niemand versteht mich.",
        "Ich bin komplett überfordert, ich kann nicht mehr.",
        "Ich bin so müde, ich habe keine Energie mehr.",
    ]

    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"User: {msg}")
        print("-" * 40)

        # Emotion analysieren
        state = engine.analyze_emotion(msg)
        print(f"Erkannte Emotion: {state.primary_emotion.value}")
        print(f"Intensität: {state.intensity.name}")
        if state.secondary_emotion:
            print(f"Sekundär: {state.secondary_emotion.value}")

        # Empathische Antwort
        response = engine.generate_supportive_response(msg)
        print(f"\nHolo: {response}")

    print(f"\n{'='*60}")
    print("Emotionale Zusammenfassung:")
    summary = engine.get_emotional_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
