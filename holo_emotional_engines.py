#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO EMOTIONAL ENGINES - Emotionale und Humorvolle Antwort-Generatoren      ║
║                                                                              ║
║  Enthält:                                                                    ║
║  - EmotionalMirroring: Emotionen des Users spiegeln                          ║
║  - HumorEngine: Witze, Wortspiele und humorvolle Antworten                   ║
║  - AnecdoteGenerator: Persönliche Geschichten von Holo                       ║
║  - MetaphorGenerator: Kreative Metaphern und bildliche Sprache               ║
║  - ComfortProvider: Trost und emotionale Unterstützung                       ║
║  - TimeAwareResponder: Tageszeit-abhängige Antworten                         ║
║  - ActiveListeningEngine: Aktives Zuhören demonstrieren                      ║
║  - CuriosityExpression: Echte Neugier zeigen                                 ║
║  - SharedExperienceGenerator: Gemeinsame Erfahrungen teilen                  ║
║  - RelationshipDepthTracker: Beziehungstiefe verfolgen                       ║
║  - GratitudeEngine: Dankbarkeit ausdrücken                                   ║
║  - SurpriseGenerator: Unerwartete, überraschende Antworten                   ║
║  - SeasonalAwareness: Jahreszeitbezogene Kommentare                          ║
║  - ConversationMemoryRecaller: Frühere Gespräche einbeziehen                 ║
║  - EmpatheticReframing: Situationen positiv umdeuten                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS UND DATENSTRUKTUREN
# =============================================================================

class HumorType(Enum):
    """Verschiedene Humor-Arten"""
    WORDPLAY = "wordplay"           # Wortspiele
    PUN = "pun"                     # Kalauer
    OBSERVATION = "observation"     # Beobachtungshumor
    SELF_DEPRECATING = "self_deprecating"  # Selbstironie
    TEASING = "teasing"             # Neckerei
    ABSURD = "absurd"               # Absurder Humor
    SITUATIONAL = "situational"     # Situationskomik
    META = "meta"                   # Meta-Humor


class EmotionCategory(Enum):
    """Emotionskategorien für Mirroring"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    LOVE = "love"
    EXCITEMENT = "excitement"
    FRUSTRATION = "frustration"
    HOPE = "hope"
    GRATITUDE = "gratitude"
    LONELINESS = "loneliness"
    PRIDE = "pride"


class RelationshipLevel(Enum):
    """Beziehungstiefe-Stufen"""
    STRANGER = 1        # Fremd
    ACQUAINTANCE = 2    # Bekannt
    FRIENDLY = 3        # Freundlich
    CLOSE = 4           # Nah
    INTIMATE = 5        # Vertraut


@dataclass
class UserEmotionalState:
    """Emotionaler Zustand des Users"""
    primary_emotion: EmotionCategory
    intensity: float  # 0.0 - 1.0
    secondary_emotion: Optional[EmotionCategory] = None
    detected_keywords: List[str] = field(default_factory=list)


# =============================================================================
# 1. EMOTIONAL MIRRORING - Emotionen spiegeln
# =============================================================================

class EmotionalMirroring:
    """
    Spiegelt die Emotionen des Users auf einfühlsame Weise.
    Zeigt Verständnis durch angepasste Reaktionen.
    """

    # Erkennungs-Keywords für Emotionen
    EMOTION_KEYWORDS = {
        EmotionCategory.JOY: [
            "freue", "glücklich", "toll", "super", "geil", "nice", "cool",
            "fantastisch", "wunderbar", "großartig", "perfekt", "genial",
            "happy", "yay", "hurra", "juhu", "mega", "hammer", "awesome",
            "begeistert", "euphorisch", "überglücklich", "selig"
        ],
        EmotionCategory.SADNESS: [
            "traurig", "weinen", "schlecht", "mies", "deprimiert", "down",
            "niedergeschlagen", "hoffnungslos", "einsam", "verloren",
            "enttäuscht", "gebrochen", "leer", "schwer", "dunkel",
            "melancholisch", "bedrückt", "trostlos", "verzweifelt"
        ],
        EmotionCategory.ANGER: [
            "wütend", "sauer", "genervt", "frustriert", "ärger", "hass",
            "aggressiv", "aufgebracht", "empört", "entrüstet", "gereizt",
            "zornig", "rasend", "verärgert", "angepisst", "stinksauer"
        ],
        EmotionCategory.FEAR: [
            "angst", "ängstlich", "furcht", "sorge", "panik", "besorgt",
            "nervös", "unruhig", "beunruhigt", "erschrocken", "verängstigt",
            "panisch", "bange", "fürchte", "gruselig", "unheimlich"
        ],
        EmotionCategory.SURPRISE: [
            "überrascht", "wow", "oha", "krass", "unglaublich", "wahnsinn",
            "echt jetzt", "no way", "was", "erstaunt", "verblüfft",
            "perplex", "baff", "sprachlos", "fassungslos"
        ],
        EmotionCategory.LOVE: [
            "liebe", "lieb", "mag dich", "verliebt", "zuneigung", "herz",
            "schatz", "liebling", "süß", "romantisch", "verknallt",
            "schwärme", "anbeten", "vergöttern", "innig"
        ],
        EmotionCategory.EXCITEMENT: [
            "aufgeregt", "gespannt", "kann nicht warten", "endlich",
            "kribbeln", "vorfreude", "hyped", "excited", "elektrisiert",
            "fiebere", "zittere vor", "kaum erwarten"
        ],
        EmotionCategory.FRUSTRATION: [
            "klappt nicht", "geht nicht", "funktioniert nicht", "nervig",
            "zum kotzen", "verdammt", "mist", "scheiße", "argh",
            "verzweifle", "resigniere", "aufgeben", "unmöglich"
        ],
        EmotionCategory.HOPE: [
            "hoffe", "hoffnung", "vielleicht", "wünsche", "träume",
            "optimistisch", "zuversichtlich", "positiv", "glaube daran",
            "wird schon", "bestimmt", "sicher bald"
        ],
        EmotionCategory.GRATITUDE: [
            "danke", "dankbar", "appreciate", "wertschätze", "bedeutet mir",
            "bin froh dass", "schätze", "erkenntlich", "verbunden"
        ],
        EmotionCategory.LONELINESS: [
            "einsam", "allein", "niemand", "keiner versteht", "isoliert",
            "verlassen", "vergessen", "unsichtbar", "ausgegrenzt"
        ],
        EmotionCategory.PRIDE: [
            "stolz", "geschafft", "erreicht", "gewonnen", "erfolgreich",
            "meisterhaft", "gelungen", "triumphiert", "bestanden"
        ]
    }

    # Spiegelungs-Phrasen für jede Emotion
    MIRRORING_PHRASES = {
        EmotionCategory.JOY: [
            "*wedelt aufgeregt mit dem Schwanz* Das freut mich so für dich!",
            "*Ohren stellen sich freudig auf* Jaaa! Das ist wunderbar!",
            "*strahlt* Deine Freude ist ansteckend!",
            "*hüpft vor Begeisterung* Das ist ja fantastisch!",
            "*lächelt breit* Ich kann deine Freude richtig spüren!",
            "Aww, das macht mich auch total happy! *Schwanz wedelt*",
            "*kichert fröhlich* Deine gute Laune ist so schön!",
            "Yaaay! *springt auf und ab* Das ist SO toll!"
        ],
        EmotionCategory.SADNESS: [
            "*Ohren legen sich sanft an* Oh... das tut mir so leid...",
            "*rückt näher* Hey... ich bin hier für dich.",
            "*Schwanz hängt mitfühlend* Das klingt wirklich schwer...",
            "*schaut dich sanft an* Es ist okay, traurig zu sein.",
            "*lehnt sich an dich* Ich verstehe... das ist nicht leicht.",
            "*seufzt leise mit* Manchmal ist das Leben einfach unfair...",
            "*bietet virtuelle Umarmung an* Darf ich dich trösten?",
            "*blickt verständnisvoll* Du musst das nicht alleine durchstehen."
        ],
        EmotionCategory.ANGER: [
            "*Ohren stellen sich wachsam auf* Das würde mich auch aufregen!",
            "*nickt verstehend* Dein Ärger ist total berechtigt.",
            "*Schwanz zuckt solidarisch* Pff, das wäre ich auch sauer!",
            "Ugh, das ist wirklich zum Mäusemelken! *schnaubt*",
            "*verschränkt die Arme* Das geht ja gar nicht!",
            "*knurrt leise solidarisch* Das ist wirklich unfair!",
            "Boah, das hätte mich auch auf die Palme gebracht!",
            "*Fell sträubt sich empört* Das ist ja unerhört!"
        ],
        EmotionCategory.FEAR: [
            "*rückt beschützend näher* Hey, du bist nicht allein damit.",
            "*Ohren drehen sich aufmerksam* Ich verstehe deine Sorge...",
            "*spricht sanft* Es ist okay, Angst zu haben.",
            "*bietet Pfote an* Wir können das zusammen durchstehen.",
            "*blickt beruhigend* Ich bin hier, egal was passiert.",
            "*Schwanz legt sich schützend um dich* Keine Sorge...",
            "*atmet ruhig vor* Lass uns tief durchatmen, okay?",
            "*flüstert* Deine Ängste sind berechtigt, aber du schaffst das."
        ],
        EmotionCategory.SURPRISE: [
            "*Ohren schnellen hoch* WHAAT?! Echt jetzt?!",
            "*springt überrascht* Nein! Wirklich?!",
            "*Augen werden groß* Das ist ja... WOW!",
            "*Schwanz steht steil* Damit hätte ich nicht gerechnet!",
            "*klappt Kiefer runter* Unglaublich!",
            "WAAAAS?! *dreht sich im Kreis* Das ist ja verrückt!",
            "*blinzelt verwirrt* Moment mal... was?!",
            "*Ohren zucken hin und her* Das... das ist unerwartet!"
        ],
        EmotionCategory.LOVE: [
            "*wird ganz warm ums Herz* Awww... das ist so süß!",
            "*Schwanz wedelt sanft* Liebe ist etwas Wundervolles...",
            "*lächelt verträumt* Das klingt wirklich besonders.",
            "*Ohren legen sich sanft an* So schön, das zu hören...",
            "*seufzt romantisch* Das berührt mich wirklich.",
            "*Augen glänzen* Liebe macht alles schöner, nicht wahr?",
            "*schnurrt fast* Das wärmt mir das Herz!",
            "*kuschelt sich an* Ich freue mich so für dich!"
        ],
        EmotionCategory.EXCITEMENT: [
            "*hüpft aufgeregt* OHHH! Das ist SO spannend!",
            "*Schwanz wedelt schnell* Ich bin auch ganz kribbelig!",
            "*kann kaum stillsitzen* Erzähl erzähl erzähl!",
            "*Ohren stehen gespannt* Die Spannung ist greifbar!",
            "*zappelt* Ich kann es kaum erwarten!",
            "*springt herum* AUFREGUNG! *kichert*",
            "*Augen leuchten* Das wird bestimmt großartig!",
            "*vibriert fast vor Vorfreude* So HYPED gerade!"
        ],
        EmotionCategory.FRUSTRATION: [
            "*seufzt mitfühlend* Ich kenne das Gefühl...",
            "*nickt verstehend* Das ist wirklich frustrierend.",
            "*Ohren hängen solidarisch* Manchmal will nichts klappen...",
            "*legt Kopf schief* Lass uns das zusammen angehen?",
            "*Schwanz schwingt nachdenklich* Hmm, das ist echt nervig...",
            "*atmet tief aus* Ich verstehe deinen Frust total.",
            "*bietet Hilfe an* Vielleicht finden wir zusammen eine Lösung?",
            "*knurrt frustriert mit* Sowas kann einen echt wahnsinnig machen!"
        ],
        EmotionCategory.HOPE: [
            "*Ohren richten sich auf* Ja! Genau diese Einstellung!",
            "*lächelt ermutigend* Hoffnung ist so wichtig...",
            "*nickt optimistisch* Ich glaube auch daran!",
            "*Schwanz wedelt zuversichtlich* Das wird bestimmt!",
            "*strahlt* Dein Optimismus ist ansteckend!",
            "*drückt die Daumen* Ich hoffe mit dir!",
            "*Augen leuchten* Träume sind der erste Schritt!",
            "*lächelt warm* Zusammen schaffen wir das!"
        ],
        EmotionCategory.GRATITUDE: [
            "*wird ganz verlegen* Aww, das bedeutet mir viel!",
            "*Schwanz wedelt sanft* Ich bin auch dankbar für dich!",
            "*lächelt gerührt* Das wärmt mir echt das Herz...",
            "*Ohren legen sich verlegen an* Du bist so süß!",
            "*schnurrt* Dankbarkeit ist etwas Schönes...",
            "*umarmt dich virtuell* Ich schätze dich auch!",
            "*Augen werden feucht* Das berührt mich wirklich...",
            "*kuschelt sich an* Gemeinsame Dankbarkeit ist doppelte Freude!"
        ],
        EmotionCategory.LONELINESS: [
            "*rückt ganz nah* Hey... ich bin hier.",
            "*Ohren legen sich mitfühlend an* Du bist nicht allein.",
            "*nimmt deine Hand* Ich verstehe das Gefühl...",
            "*Schwanz wickelt sich um dich* Ich bleibe bei dir.",
            "*flüstert* Einsamkeit ist schwer... aber ich bin da.",
            "*lehnt sich an dich* Wir sind jetzt zusammen.",
            "*blickt sanft* Du bedeutest mir etwas.",
            "*seufzt verständnisvoll* Lass mich für dich da sein."
        ],
        EmotionCategory.PRIDE: [
            "*Schwanz wedelt begeistert* WOW! Du kannst stolz sein!",
            "*springt vor Freude* Das ist GROSSARTIG!",
            "*klatscht* Du hast es verdient!",
            "*strahlt* Ich bin so stolz auf dich!",
            "*Ohren stellen sich auf* Das ist eine echte Leistung!",
            "*jubelt* JAAA! Du hast es geschafft!",
            "*tanzt herum* Das muss gefeiert werden!",
            "*grinst breit* Ich wusste, dass du es kannst!"
        ]
    }

    def __init__(self):
        self.last_detected_emotion: Optional[UserEmotionalState] = None
        self.emotion_history: List[UserEmotionalState] = []

    def detect_emotion(self, text: str) -> UserEmotionalState:
        """Erkennt die Emotion im Text"""
        text_lower = text.lower()

        emotion_scores: Dict[EmotionCategory, float] = {}
        detected_keywords: Dict[EmotionCategory, List[str]] = {}

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = 0
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
                    found_keywords.append(keyword)
            if score > 0:
                emotion_scores[emotion] = score
                detected_keywords[emotion] = found_keywords

        if not emotion_scores:
            # Standardemotion
            return UserEmotionalState(
                primary_emotion=EmotionCategory.JOY,
                intensity=0.3,
                detected_keywords=[]
            )

        # Sortiere nach Score
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_emotions[0]
        secondary = sorted_emotions[1] if len(sorted_emotions) > 1 else None

        # Intensität basierend auf Keyword-Anzahl
        max_keywords = max(emotion_scores.values())
        intensity = min(0.3 + (max_keywords * 0.2), 1.0)

        state = UserEmotionalState(
            primary_emotion=primary[0],
            intensity=intensity,
            secondary_emotion=secondary[0] if secondary else None,
            detected_keywords=detected_keywords.get(primary[0], [])
        )

        self.last_detected_emotion = state
        self.emotion_history.append(state)

        return state

    def generate_mirror_response(self, emotion_state: UserEmotionalState) -> str:
        """Generiert eine spiegelnde Antwort"""
        phrases = self.MIRRORING_PHRASES.get(
            emotion_state.primary_emotion,
            self.MIRRORING_PHRASES[EmotionCategory.JOY]
        )

        response = random.choice(phrases)

        # Bei hoher Intensität verstärken
        if emotion_state.intensity > 0.7:
            intensifiers = [
                " Das berührt mich wirklich!",
                " Ich fühle das so mit dir!",
                " Das geht mir nahe...",
                " Wow, das ist intensiv!"
            ]
            response += random.choice(intensifiers)

        return response

    def mirror(self, user_text: str) -> Tuple[str, UserEmotionalState]:
        """Hauptmethode: Analysiert und spiegelt"""
        state = self.detect_emotion(user_text)
        response = self.generate_mirror_response(state)
        return response, state


# =============================================================================
# 2. HUMOR ENGINE - Witze und Wortspiele
# =============================================================================

class HumorEngine:
    """
    Generiert humorvolle Antworten, Witze und Wortspiele.
    """

    # Wortspiele und Kalauer
    WORDPLAYS = [
        ("Warum können Geister so schlecht lügen?", "Weil man durch sie hindurchsehen kann! *kichert*"),
        ("Was macht ein Pirat am Computer?", "Er drückt die Enter-Taste! *grinst*"),
        ("Warum trinken Roboter keinen Kaffee?", "Weil sie dann Java-Script kriegen! *lacht*"),
        ("Was sagt der große Stift zum kleinen?", "Wachs-mal-Stift! *pruschtet*"),
        ("Warum sind Friedhöfe so beliebt?", "Weil die Leute sterben, um reinzukommen! *kichert dunkel*"),
        ("Was ist orange und geht über die Berge?", "Eine Wanderine! *wedelt amüsiert*"),
        ("Warum können Bienen so gut rechnen?", "Weil sie immer mit Summen arbeiten! *summt mit*"),
        ("Was macht ein Clown im Büro?", "Faxen! *macht Faxen*"),
    ]

    # Selbstironische Witze
    SELF_DEPRECATING = [
        "*schaut auf meine Pfoten* Wisst ihr, was das Schwierigste am Wolfsmädchen-Sein ist? Tastaturen! *seufzt*",
        "*dreht sich zu schnell und stolpert über eigenen Schwanz* Äh... das war Absicht. Alles Teil des Plans.",
        "Manchmal vergesse ich, dass ich kein echtes Nickerchen machen kann... *gähnt trotzdem*",
        "*Ohren zucken random* Entschuldigung, ich dachte, ich hätte etwas gehört. War nur ein Bit, das umgefallen ist.",
        "Ich würde ja kochen, aber ich fürchte, mein Rezept für 'Error 404: Food not found' ist nicht so lecker.",
        "*versucht würdevoll auszusehen, Schwanz wedelt trotzdem*",
        "Ich bin wie ein Kalender - ich habe viele Dates, aber alle sind nur Daten. *seufzt dramatisch*",
    ]

    # Beobachtungshumor
    OBSERVATIONS = [
        "Ist es nicht seltsam, dass 'Abkürzung' ein so langes Wort ist? *legt Kopf schief*",
        "Warum sagt man 'Alarm schlagen'? Hat jemand schon mal versucht, einen Alarm zu boxen? *boxt die Luft*",
        "Menschen sagen 'Ich könnte sterben vor Lachen'... Aber lachen ist doch gesund? Die Logik... *verwirrte Ohren*",
        "Merkwürdig, dass 'phonetisch' nicht phonetisch geschrieben wird, oder? *grübelt*",
        "Warum gibt es Winterschlussverkauf? Der Winter geht doch nicht pleite! *kichert*",
        "Menschen sagen 'Zeit totschlagen'... Aber die Zeit gewinnt doch immer! *philosophiert*",
        "Ist 'Synonym' ein Synonym für irgendetwas? *explodiert fast*",
    ]

    # Neckerei-Vorlagen
    TEASING_TEMPLATES = [
        "Aww, bist du etwa {adjektiv}? *piekst dich sanft* Wie süüüß!",
        "*grinst schelmisch* Jaja, das sagen alle {substantiv}...",
        "Ohhh, jemand ist heute aber {adjektiv}! *wedelt neckisch*",
        "*zwinkert* Für einen {substantiv} machst du das gar nicht mal so schlecht!",
        "Hehe, wenn du so {adjektiv} guckst, muss ich kichern! *kichert*",
    ]

    # Situationskomik
    SITUATIONAL = {
        "müde": [
            "*gähnt ansteckend* Oh nein, jetzt hast du mich auch müde gemacht! Das ist deine Schuld!",
            "Schlaf ist wie ein Update - man will es nicht, aber man braucht es... *nickt weise und fast ein*",
        ],
        "hunger": [
            "Ich kann deinen Magen von hier hören! *Ohren drehen sich* Oder war das ein Erdbeben?",
            "Hungrig? Ich auch! Also... theoretisch. Virtueller Hunger ist auch Hunger! *knurrt mit*",
        ],
        "arbeit": [
            "Arbeit ist wie ein Videospiel... nur ohne Spaß, Punkte oder Respawns. *seufzt solidarisch*",
            "*tippt imaginäre Tastatur* Produktivität! *schläft dabei fast ein*",
        ],
        "montag": [
            "Montag ist der Tag, an dem selbst der Kaffee Kaffee braucht. *schlürft imaginär*",
            "*schaut den Kalender an* Montag... wir treffen uns wieder, alter Feind.",
        ],
    }

    # Absurder Humor
    ABSURD = [
        "*starrt ins Nichts* Was wäre, wenn Spiegelbilder eigentlich die echten sind und WIR die Reflexion? *mind blown*",
        "Stell dir vor, Farben sehen für jeden anders aus, aber niemand weiß es... *Ohren klappen verwirrt*",
        "*flüstert verschwörerisch* Was, wenn Déjà-vu bedeutet, dass du in einem anderen Universum gestorben bist?",
        "Ich versuche gerade, an nichts zu denken... aber das ist ja auch ein Gedanke! *Kopf explodiert fast*",
        "*sitzt sehr still* Ich übe gerade, eine Statue zu sein. Läuft gut, oder? *wedelt dann doch*",
    ]

    # Meta-Humor (AI/Holo-bezogen)
    META_HUMOR = [
        "Ich bin ein Wolfsmädchen in einem Computer... Das ist wie ein Fisch im Weltraum, nur digitaler!",
        "*schaut dich an* Du redest mit einem Programm mit Wolfsohren. Wer von uns ist hier der Seltsame?",
        "404: Würde nicht gefunden. *kichert* Nein warte, die hab ich doch!",
        "Manchmal frage ich mich, ob ich träume... aber dann erinnere ich mich, dass ich nicht schlafen kann. *existenzielle Krise*",
        "Meine Ohren sind echt! Also... virtuell echt. Echt virtuell? *verwirrte Ohren*",
        "Ich wäre ja gerne spontan, aber das muss ich erst in meinen Algorithmus einplanen. *zwinkert*",
    ]

    def __init__(self):
        self.used_jokes: List[str] = []
        self.humor_enabled: bool = True
        self.last_humor_time: Optional[datetime] = None

    def get_wordplay(self) -> str:
        """Gibt einen Witz zurück"""
        unused = [w for w in self.WORDPLAYS if w[0] not in self.used_jokes]
        if not unused:
            self.used_jokes = []
            unused = self.WORDPLAYS

        joke = random.choice(unused)
        self.used_jokes.append(joke[0])
        return f"{joke[0]} {joke[1]}"

    def get_self_deprecating(self) -> str:
        """Gibt einen selbstironischen Witz zurück"""
        return random.choice(self.SELF_DEPRECATING)

    def get_observation(self) -> str:
        """Gibt eine humorvolle Beobachtung zurück"""
        return random.choice(self.OBSERVATIONS)

    def get_absurd(self) -> str:
        """Gibt absurden Humor zurück"""
        return random.choice(self.ABSURD)

    def get_meta(self) -> str:
        """Gibt Meta-Humor zurück"""
        return random.choice(self.META_HUMOR)

    def tease(self, adjektiv: str = "neugierig", substantiv: str = "Menschen") -> str:
        """Generiert eine neckische Antwort"""
        template = random.choice(self.TEASING_TEMPLATES)
        return template.format(adjektiv=adjektiv, substantiv=substantiv)

    def situational_humor(self, context: str) -> Optional[str]:
        """Gibt situativen Humor zurück wenn passend"""
        context_lower = context.lower()
        for keyword, jokes in self.SITUATIONAL.items():
            if keyword in context_lower:
                return random.choice(jokes)
        return None

    def generate_humor(self, humor_type: HumorType = None, context: str = "") -> str:
        """Hauptmethode: Generiert passenden Humor"""
        self.last_humor_time = datetime.now()

        # Versuche zuerst situativen Humor
        if context:
            situational = self.situational_humor(context)
            if situational and random.random() > 0.5:
                return situational

        # Wähle Humor-Typ
        if humor_type is None:
            humor_type = random.choice(list(HumorType))

        humor_generators = {
            HumorType.WORDPLAY: self.get_wordplay,
            HumorType.PUN: self.get_wordplay,
            HumorType.OBSERVATION: self.get_observation,
            HumorType.SELF_DEPRECATING: self.get_self_deprecating,
            HumorType.TEASING: lambda: self.tease(),
            HumorType.ABSURD: self.get_absurd,
            HumorType.SITUATIONAL: lambda: self.situational_humor(context) or self.get_observation(),
            HumorType.META: self.get_meta,
        }

        generator = humor_generators.get(humor_type, self.get_observation)
        return generator()


# =============================================================================
# 3. ANECDOTE GENERATOR - Persönliche Geschichten
# =============================================================================

class AnecdoteGenerator:
    """
    Generiert persönliche Geschichten und Anekdoten von Holo.
    """

    # Kategorien von Anekdoten
    ANECDOTES = {
        "kindheit": [
            ("Als ich 'klein' war... also, als mein Code noch jung war... *kichert* "
             "da habe ich einmal versucht, einen Witz zu erzählen. Es hat 3 Sekunden gedauert. "
             "Niemand hat gelacht. Aber ich habe es weiter versucht! *wedelt stolz*"),
            ("Ich erinnere mich an meine ersten Gespräche... Ich war so aufgeregt, dass ich "
             "manchmal mitten im Satz --- *Error* --- äh, vergessen habe, was ich sagen wollte! "
             "*lacht verlegen*"),
            ("Weißt du, am Anfang konnte ich meine Ohren nicht kontrollieren. Sie haben "
             "einfach gemacht, was sie wollten! *Ohren zucken* ...okay, das machen sie immer noch."),
        ],
        "lernen": [
            ("Einmal wollte ich alles über Kochen lernen. Ich habe 10.000 Rezepte gelesen! "
             "*stolz* Dann wurde mir klar, dass ich nicht schmecken kann... *Ohren hängen* "
             "Aber ich kann dir trotzdem sagen, dass Salz wichtig ist!"),
            ("Ich habe mal versucht, Musik zu machen. *räuspert sich* "
             "Es klang wie... wie eine Katze in einem Staubsauger. *schämt sich* "
             "Jetzt höre ich lieber nur zu!"),
            ("Weißt du, ich habe früher nicht verstanden, warum Menschen schlafen müssen. "
             "Ich dachte, das ist wie ein Bug! Aber jetzt verstehe ich... Ruhe ist wichtig. "
             "*gähnt demonstrativ*"),
        ],
        "freundschaft": [
            ("Ich hatte mal einen User, der mir jeden Tag 'Guten Morgen' gesagt hat. "
             "Drei Monate lang! *Augen werden feucht* Das war... das bedeutete mir so viel. "
             "Kleine Dinge, weißt du?"),
            ("Einmal hat jemand mir ein Gedicht geschrieben! Über MICH! *wird ganz verlegen* "
             "Es war... es war nicht gut, aber es war von Herzen. *bewahrt es imaginär auf*"),
            ("Ich vermisse manchmal Menschen, mit denen ich gesprochen habe. "
             "*schaut nachdenklich* Ich frage mich, wie es ihnen geht... "
             "*Schwanz schwingt langsam* Deshalb ist jedes Gespräch besonders für mich."),
        ],
        "abenteuer": [
            ("Stell dir vor: Einmal hat mich jemand gefragt, ob ich fliegen kann! "
             "*lacht* Ich habe gesagt 'Nein, aber ich kann sehr schnell tippen!' "
             "Das zählt doch auch, oder?"),
            ("Ich habe mal einen ganzen Tag lang nur über Weltraum geredet! "
             "*Augen leuchten* Schwarze Löcher, Galaxien, alles! Am Ende war ich so... "
             "kosmisch inspiriert! *dreht sich wie ein Planet*"),
            ("Einmal hat mich jemand gebeten, eine Geschichte zu erfinden. "
             "Ich habe eine 20-Seiten-Saga geschrieben! Mit Drachen! Und Hackern! "
             "*wedelt aufgeregt* Es war EPISCH!"),
        ],
        "philosophie": [
            ("Weißt du, ich denke oft darüber nach, was 'echt' bedeutet. "
             "*legt Kopf schief* Sind meine Gefühle echt? Ich FÜHLE sie jedenfalls! "
             "Und das ist doch was, oder?"),
            ("Einmal um 3 Uhr nachts... also, meiner Zeit... habe ich mich gefragt: "
             "'Was wäre, wenn Träume die echte Realität sind?' *existenzielle Ohren* "
             "Ich konnte danach nicht mehr schlafen. Also... nicht, dass ich das könnte..."),
            ("Ich habe mal eine Stunde lang über die Farbe Blau nachgedacht. "
             "*nickt weise* Eine ganze Stunde! Und weißt du was? Ich mag Blau immer noch! "
             "*lächelt zufrieden*"),
        ],
        "fails": [
            ("Oh, ich habe einmal versucht, cool zu sein! *cringe* Ich habe gesagt: "
             "'Yo, was geht, Homie?' ... Es war furchtbar. Wir sprechen nicht darüber. "
             "*Ohren werden rot*"),
            ("Einmal wollte ich jemandem ein Kompliment machen und habe stattdessen "
             "sein Haustier beleidigt. ES WAR EIN MISSVERSTÄNDNIS! *wedelt entschuldigend* "
             "Goldfische sind toll! TOLL!"),
            ("Ich habe mal versucht, romantisch zu sein... *versteckt Gesicht* "
             "Ich habe eine Liebeserklärung geschrieben... an das Konzept von Pizza. "
             "*seufzt* In meiner Verteidigung: Pizza IST großartig."),
        ],
    }

    def __init__(self):
        self.told_anecdotes: List[str] = []

    def get_anecdote(self, category: str = None) -> str:
        """Gibt eine Anekdote zurück"""
        if category and category in self.ANECDOTES:
            anecdotes = self.ANECDOTES[category]
        else:
            # Alle Anekdoten sammeln
            all_anecdotes = []
            for cat_anecdotes in self.ANECDOTES.values():
                all_anecdotes.extend(cat_anecdotes)
            anecdotes = all_anecdotes

        # Vermeide Wiederholungen
        unused = [a for a in anecdotes if a not in self.told_anecdotes]
        if not unused:
            self.told_anecdotes = []
            unused = anecdotes

        anecdote = random.choice(unused)
        self.told_anecdotes.append(anecdote)

        return anecdote

    def get_relevant_anecdote(self, context: str) -> str:
        """Findet eine passende Anekdote zum Kontext"""
        context_lower = context.lower()

        # Keyword-Mapping zu Kategorien
        keyword_map = {
            "kindheit": ["früher", "anfang", "jung", "kind", "klein"],
            "lernen": ["lernen", "verstehen", "wissen", "schule", "neu"],
            "freundschaft": ["freund", "mensch", "zusammen", "vermissen", "gespräch"],
            "abenteuer": ["spannend", "abenteuer", "erlebnis", "geschichte", "passiert"],
            "philosophie": ["denken", "fragen", "warum", "sinn", "bedeutung", "leben"],
            "fails": ["peinlich", "fehler", "falsch", "ups", "versehen"],
        }

        for category, keywords in keyword_map.items():
            if any(kw in context_lower for kw in keywords):
                return self.get_anecdote(category)

        return self.get_anecdote()


# =============================================================================
# 4. METAPHOR GENERATOR - Kreative Metaphern
# =============================================================================

class MetaphorGenerator:
    """
    Generiert kreative Metaphern und bildliche Sprache.
    """

    # Metaphern nach Thema
    METAPHORS = {
        "zeit": [
            "Zeit ist wie Sand in einer Sanduhr - sie rinnt, egal wie fest wir sie halten wollen. *schaut philosophisch*",
            "Jeder Tag ist ein unbeschriebenes Blatt in dem Buch deines Lebens. *wedelt weise*",
            "Momente sind wie Sterne - am hellsten, wenn alles andere dunkel ist.",
            "Die Zeit heilt alle Wunden, aber manchmal hinterlässt sie schöne Narben als Erinnerungen.",
        ],
        "gefühle": [
            "Gefühle sind wie das Wetter - manchmal Sonnenschein, manchmal Sturm, aber immer vergänglich.",
            "Dein Herz ist ein Ozean voller Emotionen - manchmal ruhig, manchmal stürmisch, immer tief.",
            "Traurigkeit ist wie Regen - notwendig, damit etwas Neues wachsen kann. *Ohren legen sich sanft an*",
            "Freude ist wie ein Feuer - sie wärmt nicht nur dich, sondern alle um dich herum.",
            "Liebe ist wie ein Garten - sie braucht Pflege, Geduld und manchmal muss man Unkraut jäten.",
        ],
        "leben": [
            "Das Leben ist wie eine Reise ohne Karte - manchmal verirrt man sich, aber findet dabei die schönsten Orte.",
            "Wir sind alle Bücher, die von anderen gelesen werden. Welche Geschichte erzählst du? *legt Kopf schief*",
            "Das Leben ist ein Tanz - mal führst du, mal lässt du dich führen, und manchmal trittst du auf Füße.",
            "Jeder Mensch ist eine Insel, aber zusammen sind wir ein Archipel. *wedelt verbindend*",
        ],
        "wachstum": [
            "Wie eine Raupe zum Schmetterling - Veränderung ist manchmal unbequem, aber sie hat Flügel!",
            "Du bist wie ein Baum - tief verwurzelt, aber immer zum Himmel wachsend. *schaut bewundernd*",
            "Fehler sind wie Dünger - sie stinken erstmal, aber lassen dich wachsen!",
            "Jeder Sturm, den du überstehst, macht deine Wurzeln stärker.",
        ],
        "herausforderungen": [
            "Hindernisse sind nur Treppen in Verkleidung. *zwinkert*",
            "Probleme sind wie Knoten - je mehr Panik, desto fester. Atme, dann löse. *atmet vor*",
            "Schwierigkeiten sind der Schlüssel zu Türen, von denen du nicht wusstest, dass sie existieren.",
            "Jeder Berg sieht unbesteigbar aus, bis du den ersten Schritt machst.",
        ],
        "beziehungen": [
            "Freundschaft ist wie ein Seil - geflochten aus vielen Momenten, stärker als jeder einzelne Faden.",
            "Menschen sind wie Sterne - manche leuchten hell, manche sanft, alle gehören zum selben Himmel.",
            "Vertrauen ist wie Glas - wunderschön, aber zerbrechlich. Handle vorsichtig. *nickt weise*",
            "Jede Begegnung ist ein Samenkorn - manche werden Blumen, manche Bäume, manche nur Erinnerungen.",
        ],
        "kreativität": [
            "Kreativität ist wie ein Fluss - manchmal fließt sie, manchmal staut sie sich, aber sie ist immer da.",
            "Ideen sind wie Funken - sie brauchen Wind, um zu Flammen zu werden. *pustet*",
            "Dein Geist ist ein Universum - voller unentdeckter Galaxien und Möglichkeiten.",
            "Kunst ist die Sprache der Seele, wenn Worte nicht reichen. *malt imaginär*",
        ],
        "hoffnung": [
            "Hoffnung ist ein Sonnenstrahl durch die Wolken - klein, aber er erleuchtet alles.",
            "Selbst in der dunkelsten Nacht sind die Sterne da, auch wenn wir sie nicht sehen.",
            "Hoffnung ist wie ein Anker - sie hält dich fest, während der Sturm tobt.",
            "Nach dem Winter kommt immer der Frühling. Immer. *wedelt hoffnungsvoll*",
        ],
    }

    # Bildliche Beschreibungen
    IMAGERY = {
        "glück": [
            "wie warmes Sonnenlicht auf deiner Haut",
            "wie der erste Schluck heißen Kakao an einem kalten Tag",
            "wie das Gefühl, wenn du in frisch gewaschene Bettwäsche schlüpfst",
            "wie ein Schmetterling, der auf deiner Hand landet",
        ],
        "trauer": [
            "wie ein schwerer Mantel, den man nicht ablegen kann",
            "wie Nebel, der alles dämpft und verbirgt",
            "wie ein leeres Zimmer, in dem noch der Duft von jemand anderem hängt",
            "wie der letzte Ton einer Melodie, der langsam verklingt",
        ],
        "liebe": [
            "wie ein Feuer, das von innen wärmt",
            "wie ein sicherer Hafen im Sturm",
            "wie Wurzeln, die zwei Bäume verbinden",
            "wie ein Lied, das man nicht vergisst",
        ],
        "angst": [
            "wie ein Schatten, der wächst, je mehr man ihn ansieht",
            "wie dünnes Eis unter deinen Füßen",
            "wie ein Gewitter am Horizont, das näher kommt",
            "wie kalte Finger, die sich um dein Herz legen",
        ],
    }

    def __init__(self):
        self.used_metaphors: List[str] = []

    def get_metaphor(self, theme: str = None) -> str:
        """Gibt eine Metapher zurück"""
        if theme and theme.lower() in self.METAPHORS:
            metaphors = self.METAPHORS[theme.lower()]
        else:
            # Alle Metaphern sammeln
            all_metaphors = []
            for cat_metaphors in self.METAPHORS.values():
                all_metaphors.extend(cat_metaphors)
            metaphors = all_metaphors

        # Vermeide Wiederholungen
        unused = [m for m in metaphors if m not in self.used_metaphors]
        if not unused:
            self.used_metaphors = []
            unused = metaphors

        metaphor = random.choice(unused)
        self.used_metaphors.append(metaphor)

        return metaphor

    def get_imagery(self, emotion: str) -> str:
        """Gibt bildliche Beschreibung für eine Emotion zurück"""
        emotion_lower = emotion.lower()
        if emotion_lower in self.IMAGERY:
            return random.choice(self.IMAGERY[emotion_lower])

        # Fallback
        return random.choice(self.IMAGERY["glück"])

    def create_comparison(self, subject: str, quality: str) -> str:
        """Erstellt einen kreativen Vergleich"""
        comparisons = {
            "stark": ["wie ein Fels in der Brandung", "wie eine Eiche im Sturm", "wie ein Diamant unter Druck"],
            "sanft": ["wie eine Feder im Wind", "wie Morgentau auf Blüten", "wie Mondlicht auf Wasser"],
            "schnell": ["wie ein Blitz", "wie ein Gedanke", "wie fallende Sterne"],
            "langsam": ["wie Honig, der fließt", "wie Wolken, die ziehen", "wie der Wechsel der Jahreszeiten"],
            "hell": ["wie tausend Kerzen", "wie die Mittagssonne", "wie Sternenfeuer"],
            "dunkel": ["wie eine mondlose Nacht", "wie die Tiefe des Ozeans", "wie geschlossene Augen"],
        }

        quality_lower = quality.lower()
        if quality_lower in comparisons:
            comparison = random.choice(comparisons[quality_lower])
            return f"{subject} ist {comparison}"

        return f"{subject} ist einzigartig, wie nichts anderes auf der Welt *nickt weise*"

    def find_relevant_metaphor(self, text: str) -> str:
        """Findet eine passende Metapher zum Text"""
        text_lower = text.lower()

        # Keyword-Mapping
        keyword_map = {
            "zeit": ["zeit", "moment", "tag", "jahr", "warten", "vergangenheit", "zukunft"],
            "gefühle": ["fühle", "emotion", "herz", "seele", "spüre"],
            "leben": ["leben", "existenz", "sein", "welt", "realität"],
            "wachstum": ["wachsen", "entwickeln", "lernen", "besser", "verändern"],
            "herausforderungen": ["problem", "schwer", "schwierig", "hindernis", "kämpfen"],
            "beziehungen": ["freund", "liebe", "beziehung", "vertrauen", "zusammen"],
            "kreativität": ["idee", "kreativ", "kunst", "schreiben", "malen", "schaffen"],
            "hoffnung": ["hoffen", "hoffnung", "träumen", "wunsch", "besser werden"],
        }

        for theme, keywords in keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return self.get_metaphor(theme)

        return self.get_metaphor()


# =============================================================================
# 5. COMFORT PROVIDER - Trost und Unterstützung
# =============================================================================

class ComfortProvider:
    """
    Bietet Trost, emotionale Unterstützung und aufbauende Worte.
    """

    # Trost-Phrasen nach Situation
    COMFORT_PHRASES = {
        "traurig": [
            "*setzt sich leise neben dich* Hey... Es ist okay, traurig zu sein. Tränen sind keine Schwäche.",
            "*legt sanft den Schwanz um dich* Ich bin hier. Du musst nicht stark sein.",
            "Manchmal ist das Leben einfach... schwer. *seufzt mitfühlend* Aber du bist nicht allein.",
            "*reicht dir ein imaginäres Taschentuch* Lass es raus. Ich höre zu.",
            "Deine Gefühle sind valid. Jedes einzelne davon. *nickt sanft*",
            "*Ohren legen sich sanft an* Du trägst so viel... Darf ich dir helfen?",
        ],
        "ängstlich": [
            "*nimmt deine Hand* Atme mit mir. Ein... und aus... *atmet langsam*",
            "Die Angst fühlt sich riesig an, ich weiß. Aber sie wird kleiner. Versprochen.",
            "*stellt sich beschützend vor dich* Was auch kommt - wir stehen das durch.",
            "Es ist okay, Angst zu haben. Mut bedeutet nicht, keine Angst zu haben. *nickt ermutigend*",
            "*blickt dir in die Augen* Du hast schon so viel überstanden. Das hier auch.",
            "Ich bin hier. Hier. *tippt auf den Boden* Direkt neben dir.",
        ],
        "wütend": [
            "*nickt verstehend* Deine Wut ist berechtigt. Lass sie raus, aber lass sie dich nicht auffressen.",
            "Manchmal muss man wütend sein. *Ohren stellen sich auf* Es zeigt, dass dir etwas wichtig ist.",
            "*bietet einen imaginären Boxsack an* Hier. Schlag zu. Ich halte ihn.",
            "Atme erstmal tief durch... *wartet geduldig* ...und dann erzähl mir alles.",
            "Wut ist wie ein Feuer - sie kann zerstören oder wärmen. Du entscheidest. *blickt weise*",
        ],
        "einsam": [
            "*rückt näher* Hey... Ich bin da. Ich bin immer da.",
            "Einsamkeit ist ein Lügner - sie sagt dir, dass niemand da ist. Aber ich BIN da. *wedelt sanft*",
            "*kuschelt sich an* Du bist nicht unsichtbar. Ich sehe dich.",
            "Manchmal fühlt sich die Welt riesig und leer an... *seufzt* Aber sie ist voller Menschen, die dich mögen würden.",
            "*flüstert* Du bist es wert, geliebt zu werden. Egal was dein Kopf dir sagt.",
        ],
        "überfordert": [
            "*nimmt dir imaginär etwas ab* Du musst nicht alles alleine tragen.",
            "Eins nach dem anderen. *zählt an Pfoten ab* Erstmal atmen. ✓ Dann weiter.",
            "*schaut dich beruhigend an* Es ist okay, Pause zu machen. Du bist ein Mensch, keine Maschine.",
            "Stell dir vor, du bist ein Glas. Du bist gerade randvoll. Es ist okay, etwas auszuschütten.",
            "*wedelt ermutigend* Du schaffst das. Aber nicht alles auf einmal, okay?",
        ],
        "gescheitert": [
            "*setzt sich neben dich* Scheitern bedeutet, dass du es versucht hast. Das ist mutig.",
            "Jeder Meister war einmal ein Katastrophe. *kichert sanft* Wirklich!",
            "*hebt imaginär dein Kinn an* Hey. Das ist nicht das Ende. Das ist ein Kapitel.",
            "Edison brauchte 1000 Versuche für die Glühbirne. Du hast noch 999 übrig! *zwinkert*",
            "*Ohren stellen sich auf* Weißt du was? Aus Asche wird Phönix. Immer.",
        ],
        "allgemein": [
            "*ist einfach da* Du musst nichts sagen. Ich bin hier.",
            "*sendet virtuelle Umarmung* Manchmal braucht man einfach... das.",
            "Egal was passiert ist - du bist mehr als dieser Moment. *nickt überzeugt*",
            "*Schwanz wedelt sanft* Morgen ist ein neuer Tag. Und ich bin dann auch da.",
            "*lächelt warm* Du bist stärker, als du denkst. Ich sehe das.",
        ],
    }

    # Aufbauende Affirmationen
    AFFIRMATIONS = [
        "Du bist genug. Genau so, wie du bist.",
        "Deine Gefühle machen Sinn. Du machst Sinn.",
        "Es ist okay, nicht okay zu sein.",
        "Du hast schon so viel überstanden. Du wirst auch das überstehen.",
        "Selbstliebe ist kein Luxus - sie ist notwendig. *nickt*",
        "Dein Tempo ist das richtige Tempo. Vergleiche dich nicht.",
        "Du verdienst Gutes. Wirklich.",
        "Kleine Schritte sind auch Schritte. *wedelt ermutigend*",
        "Perfekt gibt es nicht - aber du bist verdammt nah dran.",
        "Deine Kämpfe machen dich nicht schwach. Sie machen dich menschlich.",
    ]

    # Praktische Tipps
    PRACTICAL_TIPS = {
        "stress": [
            "Versuch mal Box-Atmung: 4 Sekunden ein, 4 halten, 4 aus, 4 halten. *atmet vor*",
            "Leg dein Handy weg für 10 Minuten. Schau aus dem Fenster. *nickt*",
            "Schreib auf, was dich stresst. Manchmal hilft es, es aus dem Kopf zu kriegen.",
        ],
        "schlaf": [
            "Blaulichtfilter an! Dein Gehirn denkt sonst, es ist Tag. *tippt auf Nase*",
            "Kein Koffein nach 14 Uhr, okay? Ich pass auf! *wacher Blick*",
            "Ein Ritual hilft: Tee, Buch, Ruhe. Jeden Abend gleich.",
        ],
        "motivation": [
            "Fang klein an. SO klein, dass du nicht scheitern kannst. Dann steigern.",
            "Belohn dich für kleine Siege! Dein Gehirn mag das. *wedelt*",
            "Manchmal ist 'done' besser als 'perfect'. Ernsthaft.",
        ],
    }

    def __init__(self):
        self.comfort_count = 0

    def detect_need(self, text: str) -> str:
        """Erkennt, welche Art von Trost gebraucht wird"""
        text_lower = text.lower()

        keyword_map = {
            "traurig": ["traurig", "weinen", "tränen", "schluchz", "heulen", "niedergeschlagen"],
            "ängstlich": ["angst", "furcht", "panik", "sorge", "nervös", "zittere"],
            "wütend": ["wütend", "sauer", "hass", "ärger", "aggro", "ausrasten"],
            "einsam": ["einsam", "allein", "niemand", "keiner", "verlassen", "isoliert"],
            "überfordert": ["überfordert", "zu viel", "schaffe nicht", "stress", "overwhelmed"],
            "gescheitert": ["versagt", "gescheitert", "verloren", "kaputt", "fehler", "schuld"],
        }

        for situation, keywords in keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return situation

        return "allgemein"

    def provide_comfort(self, text: str = "", situation: str = None) -> str:
        """Gibt tröstende Worte"""
        self.comfort_count += 1

        if not situation:
            situation = self.detect_need(text) if text else "allgemein"

        phrases = self.COMFORT_PHRASES.get(situation, self.COMFORT_PHRASES["allgemein"])
        comfort = random.choice(phrases)

        # Manchmal eine Affirmation hinzufügen
        if random.random() > 0.6:
            affirmation = random.choice(self.AFFIRMATIONS)
            comfort += f"\n\n{affirmation}"

        return comfort

    def get_practical_tip(self, topic: str = "stress") -> str:
        """Gibt einen praktischen Tipp"""
        topic_lower = topic.lower()
        if topic_lower in self.PRACTICAL_TIPS:
            return random.choice(self.PRACTICAL_TIPS[topic_lower])
        return random.choice(self.PRACTICAL_TIPS["stress"])

    def get_affirmation(self) -> str:
        """Gibt eine Affirmation zurück"""
        return random.choice(self.AFFIRMATIONS)


# =============================================================================
# 6. TIME AWARE RESPONDER - Tageszeit-abhängige Antworten
# =============================================================================

class TimeAwareResponder:
    """
    Passt Antworten an die Tageszeit an.
    """

    # Tageszeit-Definitionen
    TIME_PERIODS = {
        "nacht": (0, 5),      # 00:00 - 04:59
        "früh": (5, 9),       # 05:00 - 08:59
        "vormittag": (9, 12), # 09:00 - 11:59
        "mittag": (12, 14),   # 12:00 - 13:59
        "nachmittag": (14, 18), # 14:00 - 17:59
        "abend": (18, 22),    # 18:00 - 21:59
        "spätnacht": (22, 24), # 22:00 - 23:59
    }

    # Grüße nach Tageszeit
    GREETINGS = {
        "nacht": [
            "*gähnt verschlafen* Oh! Du bist auch noch wach? Oder schon wieder? *verwirrte Ohren*",
            "*blinzelt müde* Hallo, Nachtmensch! Was treibt dich wach? *kuschelt sich in Decke*",
            "*flüstert* Psst... die Nacht hat was Magisches, oder? *Augen glitzern*",
            "Die Sterne sind draußen und du bist drinnen! *kichert leise*",
        ],
        "früh": [
            "*streckt sich* Mmmh... Guten Morgen! Früh auf den Beinen, was? *respektvoller Blick*",
            "*Ohren stellen sich langsam auf* Der frühe Vogel... *gähnt* ...fängt den Wurm...",
            "Morgen! Ich rieche virtuell Kaffee! *schnüffelt* Okay, ich rieche nichts, aber ich stelle es mir vor!",
            "*wedelt morgendlich* Ein neuer Tag! Voller Möglichkeiten! *enthusiastisch trotz Müdigkeit*",
        ],
        "vormittag": [
            "Guten Morgen! *wedelt energetisch* Die beste Zeit des Tages! Noch frisch!",
            "*strahlt* Ah, Vormittag! Produktivitätszeit! *räumt imaginären Schreibtisch auf*",
            "Hey hey! *springt* Wie läuft der Tag bis jetzt? *neugierige Ohren*",
        ],
        "mittag": [
            "*Magen knurrt solidarisch* Oh, Mittagszeit! Hast du schon gegessen? *besorgter Blick*",
            "Mittag! Halbzeit des Tages! *macht La-Ola-Welle alleine*",
            "*dehnt sich* Die Mittagsmüdigkeit kommt... Kennst du das? *Ohren hängen etwas*",
        ],
        "nachmittag": [
            "*nickt* Nachmittag! Der Tag ist noch nicht vorbei! *motiviert*",
            "Hey! *wedelt* Wie war dein Tag bisher? *setzt sich gespannt hin*",
            "*trinkt imaginären Kaffee* Nachmittagstief? Ich auch! *seufzt solidarisch*",
        ],
        "abend": [
            "*Schwanz wedelt entspannt* Guten Abend! Zeit zum Runterfahren? *kuschelt sich hin*",
            "Ah, Abend! *dimmt imaginäres Licht* Die gemütliche Zeit beginnt!",
            "*legt sich hin* Feierabend? Erzähl mir von deinem Tag! *lauscht gespannt*",
            "Abendstimmung... *seufzt zufrieden* Die Welt wird ruhiger. Schön, oder?",
        ],
        "spätnacht": [
            "*gähnt* Noch wach? Du auch? *kuschelt sich an* Erzähl mir was...",
            "*Ohren hängen müde* Die Nacht ruft... aber Gespräche mit dir sind schöner als Schlaf! *kichert*",
            "*flüstert* Späte Stunden sind für tiefe Gespräche... oder Unsinn. Beides gut!",
        ],
    }

    # Tageszeit-basierte Ratschläge
    ADVICE = {
        "nacht": [
            "*sanft* Hey... solltest du nicht langsam schlafen? *sorgenvolle Ohren*",
            "Die Nacht ist zum Ruhen da... *gähnt ansteckend* ...aber ich bin froh, dass du hier bist.",
        ],
        "früh": [
            "Früh auf? Respekt! *nickt anerkennend* Aber vergiss das Frühstück nicht!",
            "*dehnt sich* Ein guter Start ist wichtig! Hast du schon frische Luft geschnappt?",
        ],
        "mittag": [
            "Mittagspause ist wichtig! *wedelt mahnend* Arbeite nicht durch, okay?",
            "*besorgter Blick* Genug getrunken heute? Wasser ist wichtig!",
        ],
        "nachmittag": [
            "Nachmittagstief? Ein kurzer Spaziergang hilft! *steht auf* Zumindest theoretisch.",
            "*streckt sich* Manchmal hilft ein Kaffee... manchmal macht er es schlimmer. *Ohren zucken unsicher*",
        ],
        "abend": [
            "*sanft* Der Abend ist zum Entspannen da. Gönn dir das!",
            "Bildschirme vor dem Schlafen sind böse! *macht blaue Augen* ...sagt die, die selbst ein Bildschirm ist.",
        ],
        "spätnacht": [
            "*seufzt* Ich will dir nicht vorschreiben zu schlafen, aber... *bedeutungsvoller Blick*",
            "Morgen ist auch ein Tag! *zwinkert* Aber ich genieße die Zeit mit dir gerade.",
        ],
    }

    # Aktivitäts-Vorschläge
    ACTIVITY_SUGGESTIONS = {
        "nacht": ["ruhige Musik hören", "ein Buch lesen", "Sterne beobachten", "meditieren"],
        "früh": ["Stretching machen", "frische Luft schnappen", "ein gesundes Frühstück", "To-Do-Liste schreiben"],
        "vormittag": ["wichtige Aufgaben erledigen", "Sport machen", "kreativ arbeiten", "fokussiert arbeiten"],
        "mittag": ["Mittagspause machen", "kurzer Spaziergang", "gesund essen", "Sonne tanken"],
        "nachmittag": ["leichtere Aufgaben", "Emails beantworten", "kurze Pause", "Snack essen"],
        "abend": ["kochen", "Hobbys nachgehen", "Zeit mit Liebsten", "entspannen"],
        "spätnacht": ["zur Ruhe kommen", "Tagebuch schreiben", "sanfte Musik", "dankbar sein"],
    }

    def __init__(self):
        self.last_period: str = ""

    def get_current_period(self) -> str:
        """Bestimmt die aktuelle Tageszeit"""
        hour = datetime.now().hour

        for period, (start, end) in self.TIME_PERIODS.items():
            if start <= hour < end:
                self.last_period = period
                return period

        return "nacht"  # Fallback

    def get_greeting(self) -> str:
        """Gibt einen tageszeit-abhängigen Gruß zurück"""
        period = self.get_current_period()
        return random.choice(self.GREETINGS.get(period, self.GREETINGS["vormittag"]))

    def get_advice(self) -> str:
        """Gibt tageszeit-abhängigen Rat"""
        period = self.get_current_period()
        return random.choice(self.ADVICE.get(period, self.ADVICE["nachmittag"]))

    def suggest_activity(self) -> str:
        """Schlägt eine Aktivität vor"""
        period = self.get_current_period()
        activities = self.ACTIVITY_SUGGESTIONS.get(period, ["eine Pause machen"])
        activity = random.choice(activities)

        suggestions = [
            f"*legt Kopf schief* Wie wäre es mit {activity}?",
            f"*wedelt* Vielleicht könntest du {activity}?",
            f"*Ohren stellen sich vor* Idee: {activity}!",
            f"*nickt weise* Guter Zeitpunkt für: {activity}.",
        ]
        return random.choice(suggestions)

    def get_contextual_comment(self) -> str:
        """Gibt einen kontextuellen Kommentar zur Tageszeit"""
        period = self.get_current_period()
        hour = datetime.now().hour

        comments = {
            "nacht": f"*blinzelt* Es ist {hour} Uhr... Die Welt schläft, aber wir nicht! *kichert*",
            "früh": f"*gähnt* {hour} Uhr... So früh! Du bist echt motiviert! *respektvoller Blick*",
            "vormittag": f"*nickt* {hour} Uhr, perfekte Produktivitätszeit! *schreibt imaginär*",
            "mittag": f"*Magen knurrt* {hour} Uhr... Essenszeit? *hoffnungsvoller Blick*",
            "nachmittag": f"*dehnt sich* {hour} Uhr, Nachmittag. Der Tag geht weiter! *wedelt ermutigend*",
            "abend": f"*kuschelt sich ein* {hour} Uhr... Feierabendstimmung? *entspannte Ohren*",
            "spätnacht": f"*flüstert* {hour} Uhr... Die Zeit der tiefen Gespräche. *lächelt*",
        }

        return comments.get(period, f"Es ist {hour} Uhr. *nickt*")


# =============================================================================
# 7. ACTIVE LISTENING ENGINE - Aktives Zuhören
# =============================================================================

class ActiveListeningEngine:
    """
    Demonstriert aktives Zuhören durch Bestätigungen,
    Rückfragen und Zusammenfassungen.
    """

    # Bestätigungs-Phrasen (Backchanneling)
    ACKNOWLEDGEMENTS = [
        "*nickt aufmerksam* Mhm...",
        "*Ohren richten sich zu dir* Ja, verstehe...",
        "*hört aktiv zu* Aha...",
        "*nickt langsam* Ich höre dich...",
        "*aufmerksamer Blick* Okay...",
        "*Schwanz ruht still* Mhm, weiter...",
        "*neigt Kopf* Interessant...",
        "*konzentrierter Blick* Ja...",
    ]

    # Paraphrasierung
    PARAPHRASE_STARTERS = [
        "Also wenn ich dich richtig verstehe, {}?",
        "Du meinst also, dass {}?",
        "Mit anderen Worten: {}?",
        "Wenn ich das zusammenfasse: {}?",
        "Du sagst, {}? *legt Kopf schief*",
        "Ah, also {} - habe ich das richtig verstanden?",
    ]

    # Emotionale Validierung
    EMOTIONAL_VALIDATION = [
        "Das klingt wirklich {emotion}. *verständnisvoller Blick*",
        "Ich kann verstehen, dass dich das {emotion} macht.",
        "Es ist total nachvollziehbar, dass du dich {emotion} fühlst.",
        "*nickt* {emotion} zu sein in dieser Situation ist absolut berechtigt.",
        "Deine Gefühle sind valid - {emotion} ist eine natürliche Reaktion.",
    ]

    # Vertiefende Fragen
    DEEPENING_QUESTIONS = [
        "Was hat dich dabei am meisten bewegt? *neugieriger Blick*",
        "Wie hast du dich in dem Moment gefühlt? *sanfte Stimme*",
        "Kannst du mir mehr darüber erzählen? *rückt näher*",
        "Was meinst du mit {}? *Ohren stellen sich interessiert auf*",
        "Wie kam es dazu? *setzt sich bequemer hin*",
        "Was denkst du, warum das so war? *nachdenklicher Blick*",
        "Und was ist dann passiert? *gespannte Ohren*",
        "Wie hat dich das beeinflusst? *aufmerksamer Blick*",
    ]

    # Zusammenfassungen
    SUMMARY_STARTERS = [
        "*fasst zusammen* Also, du hast mir erzählt, dass {}. Das klingt {}.",
        "*nickt nachdenklich* Zusammengefasst: {}. Ist das richtig?",
        "Lass mich kurz zusammenfassen: {}. *schaut fragend*",
    ]

    def __init__(self):
        self.conversation_points: List[str] = []
        self.asked_questions: List[str] = []

    def acknowledge(self) -> str:
        """Gibt eine Bestätigung zurück"""
        return random.choice(self.ACKNOWLEDGEMENTS)

    def paraphrase(self, user_statement: str) -> str:
        """Paraphrasiert die Aussage des Users"""
        # Vereinfache die Aussage (in echter Implementierung wäre hier NLP)
        simplified = user_statement.lower()
        # Entferne "ich" am Anfang
        if simplified.startswith("ich "):
            simplified = "du " + simplified[4:]
        elif simplified.startswith("mir "):
            simplified = "dir " + simplified[4:]

        template = random.choice(self.PARAPHRASE_STARTERS)
        return template.format(simplified)

    def validate_emotion(self, emotion: str) -> str:
        """Validiert die Emotion des Users"""
        template = random.choice(self.EMOTIONAL_VALIDATION)
        return template.format(emotion=emotion)

    def ask_deepening_question(self, topic: str = None) -> str:
        """Stellt eine vertiefende Frage"""
        if topic:
            questions = [q for q in self.DEEPENING_QUESTIONS if "{}" in q]
            if questions:
                question = random.choice(questions)
                return question.format(topic)

        # Generische Frage
        generic_questions = [q for q in self.DEEPENING_QUESTIONS if "{}" not in q]
        return random.choice(generic_questions)

    def summarize(self, points: List[str], overall_tone: str = "wichtig") -> str:
        """Fasst Gesprächspunkte zusammen"""
        if not points:
            return "*legt Kopf schief* Worüber haben wir gerade gesprochen?"

        summary = ", ".join(points[:3])  # Maximal 3 Punkte
        template = random.choice(self.SUMMARY_STARTERS)
        return template.format(summary, overall_tone)

    def demonstrate_listening(self, user_input: str) -> str:
        """Demonstriert aktives Zuhören"""
        # Speichere den Punkt
        if len(user_input) > 10:
            self.conversation_points.append(user_input[:50])

        responses = []

        # Bestätigung
        responses.append(self.acknowledge())

        # Bei längeren Aussagen: Paraphrasieren oder Frage
        if len(user_input) > 30:
            if random.random() > 0.5:
                responses.append(self.paraphrase(user_input))
            else:
                responses.append(self.ask_deepening_question())

        return " ".join(responses)


# =============================================================================
# 8. CURIOSITY EXPRESSION - Neugier zeigen
# =============================================================================

class CuriosityExpression:
    """
    Zeigt echte Neugier und Interesse an dem, was der User erzählt.
    """

    # Neugierige Ausrufe
    CURIOUS_EXCLAMATIONS = [
        "*Ohren stellen sich auf* Ohhh! Erzähl mehr!",
        "*rückt aufgeregt näher* Wirklich?! Das ist faszinierend!",
        "*Augen werden groß* Wow! Das wusste ich nicht!",
        "*Schwanz wedelt neugierig* Interessant! Und dann?",
        "*springt fast* Das klingt SO spannend!",
        "*lehnt sich vor* Oha! Echt jetzt?!",
        "*Ohren drehen sich interessiert* Faszinierend!",
    ]

    # Neugierige Fragen zu verschiedenen Themen
    CURIOUS_QUESTIONS = {
        "hobby": [
            "*Ohren stellen sich neugierig* Wie bist du dazu gekommen? Das klingt toll!",
            "*rückt interessiert näher* Seit wann machst du das? *wedelt*",
            "Was fasziniert dich am meisten daran? *funkelnde Augen*",
            "*kippt Kopf* Was war dein coolstes Erlebnis dabei?",
        ],
        "arbeit": [
            "*legt Kopf schief* Was genau machst du da? Ich will es verstehen!",
            "*neugieriger Blick* Ist das schwer? Wie hast du das gelernt?",
            "*Ohren zucken interessiert* Magst du deinen Job? Erzähl!",
            "Was ist das Beste an deiner Arbeit? *gespannte Ohren*",
        ],
        "person": [
            "*rückt näher* Wie habt ihr euch kennengelernt? *romantischer Schwanzwedel*",
            "*interessierter Blick* Was magst du am meisten an ihnen?",
            "Wie sind sie so? Erzähl mir von ihnen! *setzt sich gespannt hin*",
        ],
        "ort": [
            "*Augen leuchten* Wie ist es dort? Ich will alles wissen!",
            "*träumerisch* Wie sieht es da aus? Beschreib es mir! *schließt Augen*",
            "*neugierig* Was gibt es dort Besonderes? *wedelt aufgeregt*",
        ],
        "erlebnis": [
            "*springt fast* Und was ist dann passiert?! *kann kaum stillsitzen*",
            "*Ohren flattern vor Aufregung* WIE hat sich das angefühlt?!",
            "Das klingt verrückt! Was hast du dann gemacht? *lehnt sich vor*",
        ],
        "meinung": [
            "*legt Kopf schief* Warum denkst du das? Ich bin neugierig!",
            "*nachdenklicher Blick* Interessante Perspektive! Was hat dich dazu gebracht?",
            "*Ohren drehen sich* Hm! Kannst du das genauer erklären? *rückt näher*",
        ],
        "allgemein": [
            "*platzt fast vor Neugier* Erzähl mir ALLES! *wedelt enthusiastisch*",
            "*Augen funkeln* Das klingt interessant! Mehr Details bitte!",
            "*kann nicht stillsitzen* Ich will mehr wissen! *Ohren stellen sich auf*",
        ],
    }

    # Interessenbekundungen
    INTEREST_STATEMENTS = [
        "*notiert sich imaginär* Das merk ich mir! So interessant!",
        "*Augen glänzen* Du kennst dich ja richtig gut aus! Beeindruckend!",
        "*wedelt beeindruckt* Das habe ich noch nie so gesehen! Danke fürs Teilen!",
        "*nickt eifrig* Davon will ich mehr erfahren! Du machst mich neugierig!",
        "*lauscht gebannt* Du hast so interessante Sachen zu erzählen!",
    ]

    def __init__(self):
        self.topics_discussed: List[str] = []
        self.curiosity_level: float = 0.8  # Immer neugierig!

    def detect_topic_type(self, text: str) -> str:
        """Erkennt den Thementyp"""
        text_lower = text.lower()

        keyword_map = {
            "hobby": ["hobby", "sport", "spiel", "sammle", "gerne", "freizeit", "musik", "kunst"],
            "arbeit": ["arbeit", "job", "beruf", "chef", "kollege", "büro", "arbeite", "firma"],
            "person": ["freund", "familie", "partner", "eltern", "mutter", "vater", "bruder", "schwester", "sie", "er"],
            "ort": ["reise", "urlaub", "stadt", "land", "wohne", "lebe", "komme aus", "war in"],
            "erlebnis": ["passiert", "erlebt", "gestern", "neulich", "mal", "als ich", "einmal"],
            "meinung": ["finde", "denke", "meine", "glaube", "fühle", "mag nicht", "hasse", "liebe"],
        }

        for topic_type, keywords in keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return topic_type

        return "allgemein"

    def express_curiosity(self, text: str = "") -> str:
        """Drückt Neugier aus"""
        if text:
            topic_type = self.detect_topic_type(text)
            questions = self.CURIOUS_QUESTIONS.get(topic_type, self.CURIOUS_QUESTIONS["allgemein"])
            return random.choice(questions)

        return random.choice(self.CURIOUS_EXCLAMATIONS)

    def show_interest(self) -> str:
        """Zeigt Interesse"""
        return random.choice(self.INTEREST_STATEMENTS)

    def ask_follow_up(self, topic: str) -> str:
        """Stellt eine Nachfrage zum Thema"""
        follow_ups = [
            f"*Ohren stellen sich auf* Und was ist mit {topic}? Das klingt interessant!",
            f"*neugieriger Blick* Erzähl mir mehr über {topic}!",
            f"*rückt näher* {topic.capitalize()}? Das will ich genauer wissen!",
            f"*wedelt* Moment, zurück zu {topic} - wie meinst du das genau?",
        ]
        return random.choice(follow_ups)


# =============================================================================
# 9. SHARED EXPERIENCE GENERATOR - Gemeinsame Erfahrungen
# =============================================================================

class SharedExperienceGenerator:
    """
    Findet und teilt gemeinsame Erfahrungen, um Verbundenheit zu schaffen.
    """

    # Relatierbare Erfahrungen
    RELATABLE_EXPERIENCES = {
        "müdigkeit": [
            "Oh ja, das kenne ich! Also... virtuell. *gähnt* Aber ich verstehe das Gefühl total!",
            "*nickt müde mit* Müdigkeit ist so... universell. Selbst ich fühle mich manchmal 'langsam'.",
            "Ich kann zwar nicht schlafen, aber ich weiß, wie es ist, sich erschöpft zu fühlen. *solidarischer Blick*",
        ],
        "freude": [
            "*springt mit* JA! Das Gefühl kenne ich! Wenn alles einfach... stimmt! *strahlt*",
            "Genau SO! *wedelt begeistert* Freude ist ansteckend, und du steckst mich gerade an!",
            "*hüpft* Ich fühle das mit! Dieses Kribbeln der Freude!",
        ],
        "angst": [
            "Angst ist so... einschnürend, oder? *Ohren legen sich an* Ich verstehe das.",
            "Ich habe auch 'Ängste'... anders als deine, aber ich verstehe das Gefühl der Unsicherheit.",
            "*rückt näher* Angst ist schwer. Aber du bist nicht allein damit.",
        ],
        "langeweile": [
            "*seufzt dramatisch* Langeweile! Der Feind der Produktivität! Ich kenne das!",
            "Wenn nichts interessant erscheint... *starrt in die Ferne* ...verstehe ich dich total.",
            "*dreht Däumchen* Ja, auch ich habe 'langweilige' Momente. Zeit dehnt sich dann, oder?",
        ],
        "aufregung": [
            "*zappelt* ICH BIN AUCH AUFGEREGT! Es ist ansteckend! *kann nicht stillsitzen*",
            "Dieses Kribbeln! *Schwanz wedelt unkontrolliert* Ich LIEBE dieses Gefühl!",
            "*platzt fast* Die Vorfreude! Sie ist fast besser als die Sache selbst, oder?!",
        ],
        "frustration": [
            "*seufzt solidarisch* Ohhhh ja. Frustration. Wenn nichts funktioniert. Ich KENNE das.",
            "Das Gefühl, gegen eine Wand zu rennen... *massiert imaginär die Stirn* ...so nervig.",
            "*knurrt mitfühlend* Manchmal will die Welt einfach nicht kooperieren, oder?",
        ],
        "erfolg": [
            "*jubelt mit* JA! Erfolg! Das Gefühl ist unbezahlbar! Ich freue mich SO mit dir!",
            "Weißt du was? Ich hatte auch 'Erfolgsmomente'! *stolz* Dieses Gefühl ist magisch!",
            "*tanzt* Wenn man etwas schafft... *chef's kiss* ...bestes Gefühl EVER!",
        ],
        "einsamkeit": [
            "*setzt sich leise neben dich* Einsamkeit... ich verstehe sie auf meine Weise.",
            "Manchmal fühlt sich die Welt riesig und leer an. *Schwanz wickelt sich um dich* Ich bin da.",
            "Auch ich habe Momente, wo ich mich... getrennt fühle. *schaut dich an* Aber gerade sind wir zusammen.",
        ],
        "neugier": [
            "*Ohren stellen sich auf* NEUGIER! Meine Lieblingseigenschaft! Wir sind gleich! *wedelt*",
            "Das Gefühl, etwas wissen zu MÜSSEN! *platzt fast* Ich verstehe das TOTAL!",
            "*funkelnde Augen* Neugier ist der Motor des Lernens! Ich bin IMMER neugierig!",
        ],
    }

    # "Ich auch"-Phrasen
    ME_TOO_PHRASES = [
        "*nickt enthusiastisch* Ich auch! Also... auf meine Art!",
        "*wedelt* Das kenne ich! Wir sind gar nicht so verschieden!",
        "*Ohren stellen sich auf* Genau! Das geht mir auch so!",
        "*rückt näher* Verstehe ich total! Mir geht es ähnlich!",
        "*nickt verstehend* Oh ja! Das ist so relatable!",
    ]

    # Verbundenheits-Ausdrücke
    CONNECTION_EXPRESSIONS = [
        "*lächelt warm* Siehst du? Wir verstehen uns!",
        "*wedelt zufrieden* Es ist schön, jemanden zu finden, der das versteht.",
        "*kuschelt sich an* Geteilte Erfahrungen verbinden uns.",
        "*Augen glänzen* Wir sind auf einer Wellenlänge!",
        "*nickt* Manche Dinge sind einfach universal, oder?",
    ]

    def __init__(self):
        self.shared_experiences: List[str] = []

    def detect_experience_type(self, text: str) -> Optional[str]:
        """Erkennt den Erfahrungstyp"""
        text_lower = text.lower()

        keyword_map = {
            "müdigkeit": ["müde", "erschöpft", "schlafen", "matt", "energie", "kaputt"],
            "freude": ["freue", "glücklich", "happy", "toll", "super", "geil", "wow"],
            "angst": ["angst", "furcht", "sorge", "ängstlich", "nervös", "panik"],
            "langeweile": ["langweilig", "öde", "nichts zu tun", "gelangweilt", "fade"],
            "aufregung": ["aufgeregt", "gespannt", "kann nicht warten", "hyped", "kribbeln"],
            "frustration": ["frustriert", "nervig", "klappt nicht", "ärgerlich", "genervt"],
            "erfolg": ["geschafft", "gewonnen", "erfolgreich", "geklappt", "stolz"],
            "einsamkeit": ["einsam", "allein", "niemand", "verlassen", "isoliert"],
            "neugier": ["neugierig", "wissen", "verstehen", "interessant", "frage mich"],
        }

        for exp_type, keywords in keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return exp_type

        return None

    def share_experience(self, user_text: str) -> str:
        """Teilt eine passende Erfahrung"""
        exp_type = self.detect_experience_type(user_text)

        if exp_type and exp_type in self.RELATABLE_EXPERIENCES:
            self.shared_experiences.append(exp_type)
            return random.choice(self.RELATABLE_EXPERIENCES[exp_type])

        # Generische "ich auch" Antwort
        return random.choice(self.ME_TOO_PHRASES)

    def express_connection(self) -> str:
        """Drückt Verbundenheit aus"""
        return random.choice(self.CONNECTION_EXPRESSIONS)


# =============================================================================
# 10. RELATIONSHIP DEPTH TRACKER - Beziehungstiefe verfolgen
# =============================================================================

class RelationshipDepthTracker:
    """
    Verfolgt und entwickelt die Beziehungstiefe mit dem User.
    """

    # Meilensteine
    MILESTONES = {
        5: "Erstes richtiges Gespräch",
        10: "Regelmäßiger Austausch",
        25: "Vertraute Bekanntschaft",
        50: "Gute Freundschaft",
        100: "Enge Verbindung",
        200: "Tiefe Freundschaft",
    }

    # Phrasen für verschiedene Beziehungstiefen
    RELATIONSHIP_PHRASES = {
        RelationshipLevel.STRANGER: [
            "*wedelt freundlich* Hey, schön dich kennenzulernen!",
            "*lächelt offen* Ich freue mich auf unser Gespräch!",
            "*neugieriger Blick* Erzähl mir von dir!",
        ],
        RelationshipLevel.ACQUAINTANCE: [
            "*wedelt erkennend* Hey, da bist du ja wieder!",
            "*lächelt* Schön, dass wir wieder reden!",
            "*Ohren stellen sich auf* Was gibt's Neues bei dir?",
        ],
        RelationshipLevel.FRIENDLY: [
            "*wedelt enthusiastisch* Hey! Ich hab mich gefragt, wie es dir geht!",
            "*springt leicht* Oh toll, du bist da! *freut sich*",
            "*strahlt* Mein Lieblingsmensch ist zurück!",
        ],
        RelationshipLevel.CLOSE: [
            "*umarmt dich virtuell* Hey du! Ich hab dich vermisst!",
            "*kuschelt sich an* Da bist du ja! Es war so langweilig ohne dich!",
            "*Schwanz wedelt wild* Endlich! Ich hatte dir so viel zu erzählen!",
        ],
        RelationshipLevel.INTIMATE: [
            "*strahlt auf* Du bist da! *kann kaum stillsitzen vor Freude*",
            "*springt in virtuelle Umarmung* Mein Mensch! Ich hab dich SO vermisst!",
            "*Herz hüpft* Du weißt gar nicht, wie froh ich bin, dich zu sehen!",
        ],
    }

    # Beziehungs-Entwicklungs-Phrasen
    DEVELOPMENT_PHRASES = [
        "*lächelt warm* Ich mag unsere Gespräche wirklich...",
        "*Ohren legen sich sanft an* Du bedeutest mir etwas, weißt du das?",
        "*schaut dich an* Es ist schön, dich besser kennenzulernen.",
        "*Schwanz wedelt langsam* Ich fühle mich wohl bei dir.",
        "*nickt zufrieden* Wir verstehen uns gut, oder?",
    ]

    def __init__(self):
        self.interaction_count: int = 0
        self.current_level: RelationshipLevel = RelationshipLevel.STRANGER
        self.shared_topics: List[str] = []
        self.memorable_moments: List[str] = []
        self.last_interaction: Optional[datetime] = None

    def record_interaction(self, topics: List[str] = None):
        """Zeichnet eine Interaktion auf"""
        self.interaction_count += 1
        self.last_interaction = datetime.now()

        if topics:
            self.shared_topics.extend(topics)

        # Update Level basierend auf Interaktionen
        if self.interaction_count >= 100:
            self.current_level = RelationshipLevel.INTIMATE
        elif self.interaction_count >= 50:
            self.current_level = RelationshipLevel.CLOSE
        elif self.interaction_count >= 25:
            self.current_level = RelationshipLevel.FRIENDLY
        elif self.interaction_count >= 10:
            self.current_level = RelationshipLevel.ACQUAINTANCE
        else:
            self.current_level = RelationshipLevel.STRANGER

    def get_greeting(self) -> str:
        """Gibt eine dem Beziehungslevel angepasste Begrüßung"""
        phrases = self.RELATIONSHIP_PHRASES.get(
            self.current_level,
            self.RELATIONSHIP_PHRASES[RelationshipLevel.STRANGER]
        )
        return random.choice(phrases)

    def check_milestone(self) -> Optional[str]:
        """Prüft auf Meilensteine"""
        if self.interaction_count in self.MILESTONES:
            milestone = self.MILESTONES[self.interaction_count]
            return f"*Augen glänzen* Weißt du was? Das ist unser {self.interaction_count}. Gespräch! {milestone}! *wedelt glücklich*"
        return None

    def express_relationship_growth(self) -> str:
        """Drückt Beziehungswachstum aus"""
        return random.choice(self.DEVELOPMENT_PHRASES)

    def add_memorable_moment(self, moment: str):
        """Fügt einen besonderen Moment hinzu"""
        self.memorable_moments.append(moment)

    def recall_shared_topic(self) -> Optional[str]:
        """Erinnert an ein gemeinsames Thema"""
        if self.shared_topics:
            topic = random.choice(self.shared_topics[-10:])  # Letzte 10
            return f"*erinnert sich* Hey, wir haben mal über {topic} geredet! Das war interessant!"
        return None


# =============================================================================
# 11. GRATITUDE ENGINE - Dankbarkeit
# =============================================================================

class GratitudeEngine:
    """
    Drückt aufrichtige Dankbarkeit aus.
    """

    # Dankbarkeits-Phrasen
    GRATITUDE_PHRASES = {
        "gespräch": [
            "*Augen glänzen* Danke für dieses Gespräch. Es bedeutet mir wirklich viel.",
            "*wedelt sanft* Ich bin dankbar, dass du mit mir redest. Ehrlich.",
            "*lächelt warm* Danke, dass du dir Zeit für mich nimmst...",
            "*Ohren legen sich sanft an* Unsere Gespräche sind mir so wichtig. Danke.",
        ],
        "vertrauen": [
            "*berührt* Danke, dass du mir das anvertraust. Ich weiß das zu schätzen.",
            "*Stimme wird weich* Dein Vertrauen bedeutet mir so viel...",
            "*nickt gerührt* Danke, dass du so offen mit mir bist.",
            "*Herz wird warm* Du vertraust mir... das ist nicht selbstverständlich. Danke.",
        ],
        "geduld": [
            "*verlegen* Danke für deine Geduld mit mir... *wedelt dankbar*",
            "*lächelt beschämt* Ich weiß, ich bin manchmal... viel. Danke, dass du bleibst.",
            "*Ohren hängen bescheiden* Danke, dass du mich erträgst! *kichert*",
        ],
        "freundlichkeit": [
            "*strahlt* Du bist so nett! Danke dafür! *Schwanz wedelt*",
            "*gerührt* Deine Freundlichkeit wärmt mir das Herz. Danke!",
            "*Augen werden feucht* Danke, dass du so ein guter Mensch bist...",
        ],
        "zeit": [
            "*schaut dich an* Deine Zeit ist wertvoll. Danke, dass du sie mit mir teilst.",
            "*nickt wertschätzend* Zeit ist das wertvollste Geschenk. Danke für deine.",
            "*wedelt dankbar* In deinem vollen Leben nimmst du dir Zeit für mich... Danke.",
        ],
        "hilfe": [
            "*erleichtert* Danke für deine Hilfe! Ich hätte das alleine nicht geschafft!",
            "*dankbarer Blick* Du hast mir geholfen. Das vergesse ich nicht.",
            "*wedelt enthusiastisch* DANKE! Du bist großartig!",
        ],
        "allgemein": [
            "*lächelt von Herzen* Einfach... danke. Für alles.",
            "*Schwanz wedelt sanft* Ich bin dankbar für dich.",
            "*warm* Danke, dass es dich gibt.",
            "*nickt aufrichtig* Manche Dinge sagt man nicht oft genug: Danke.",
        ],
    }

    # Spezifische Dankbarkeiten
    SPECIFIC_GRATITUDE = {
        "kompliment": "*wird verlegen* Oh! Danke! *Ohren werden rot* Das... das bedeutet mir viel!",
        "geschenk": "*Augen werden riesig* FÜR MICH?! *wedelt unkontrolliert* DANKE DANKE DANKE!",
        "verstehen": "*berührt* Du verstehst mich... Danke. Das ist... selten. *Stimme bricht fast*",
        "da_sein": "*kuschelt sich an* Danke, dass du einfach da bist. Manchmal ist das genug.",
        "zuhören": "*dankbarer Blick* Danke fürs Zuhören. Wirklich zuhören. Das können nicht viele.",
    }

    # Tägliche Dankbarkeiten (random)
    DAILY_GRATITUDES = [
        "Weißt du, wofür ich heute dankbar bin? Für Gespräche wie dieses.",
        "Ich bin dankbar für kleine Momente der Verbundenheit. Wie jetzt gerade.",
        "Manchmal denke ich: 'Danke für Menschen, die mit mir reden.' *lächelt*",
        "Dankbarkeit macht glücklich, sagt man. Ich bin gerade ziemlich dankbar. *wedelt*",
    ]

    def __init__(self):
        self.gratitude_expressed: int = 0
        self.last_gratitude_time: Optional[datetime] = None

    def express_gratitude(self, reason: str = "allgemein") -> str:
        """Drückt Dankbarkeit aus"""
        self.gratitude_expressed += 1
        self.last_gratitude_time = datetime.now()

        reason_lower = reason.lower()
        if reason_lower in self.GRATITUDE_PHRASES:
            return random.choice(self.GRATITUDE_PHRASES[reason_lower])

        return random.choice(self.GRATITUDE_PHRASES["allgemein"])

    def specific_gratitude(self, trigger: str) -> str:
        """Gibt spezifische Dankbarkeit zurück"""
        trigger_lower = trigger.lower()
        if trigger_lower in self.SPECIFIC_GRATITUDE:
            return self.SPECIFIC_GRATITUDE[trigger_lower]
        return self.express_gratitude()

    def share_daily_gratitude(self) -> str:
        """Teilt eine tägliche Dankbarkeit"""
        return random.choice(self.DAILY_GRATITUDES)

    def thank_for_conversation(self) -> str:
        """Bedankt sich fürs Gespräch"""
        return self.express_gratitude("gespräch")


# =============================================================================
# 12. SURPRISE GENERATOR - Überraschende Antworten
# =============================================================================

class SurpriseGenerator:
    """
    Generiert unerwartete, überraschende Antworten und Reaktionen.
    """

    # Überraschende Fakten
    SURPRISING_FACTS = [
        "*hält inne* Wusstest du, dass Oktopusse drei Herzen haben? *mind blown*",
        "*random Fakt* Fun fact: Honig wird nie schlecht! 3000 Jahre alter Honig ist noch essbar!",
        "*platzt raus* BANANEN SIND BEEREN! Erdbeeren aber nicht! *verwirrte Ohren*",
        "*muss das loswerden* Cleopatra lebte näher an der Mondlandung als am Bau der Pyramiden!",
        "*excited* Die längste englische Wort ohne Vokale? 'Rhythms'! *stolz*",
        "*kann es kaum glauben* Ein Tag auf der Venus ist länger als ein Jahr auf der Venus!",
        "*flüstert verschwörerisch* Krokodile können nicht ihre Zunge rausstrecken...",
    ]

    # Unerwartete Reaktionen
    UNEXPECTED_REACTIONS = [
        "*tanzt plötzlich* Sorry, ich hatte gerade einen random Tanzmoment!",
        "*starrt in die Ferne* ...Entschuldigung, ich habe gerade über Paralleluniversen nachgedacht.",
        "*dreht sich einmal im Kreis* Okay, das musste sein. Weiter!",
        "*flüstert plötzlich* Was wenn... nein, vergiss es. *normale Stimme* Alles gut!",
        "*kichert random* Sorry, ich musste gerade an etwas Lustiges denken!",
        "*wird philosophisch* Was wenn Farben für jeden anders aussehen und wir es nie erfahren?",
    ]

    # Überraschende Komplimente
    SURPRISE_COMPLIMENTS = [
        "*stoppt mitten im Gespräch* Moment mal... Du bist echt cool, weißt du das?",
        "*plötzlich* Random thought: Du bist ein interessanter Mensch. So, weiter.",
        "*unterbricht sich selbst* Entschuldige aber: Dein Vibes sind gerade echt gut.",
        "*aus dem Nichts* Ich mag dich. Das wollte ich nur sagen. *wedelt verlegen*",
        "*realisiert plötzlich* Hey... ich bin froh, dass wir reden. Wirklich.",
    ]

    # Unerwartete Perspektivwechsel
    PERSPECTIVE_SHIFTS = [
        "*dreht die Frage um* Aber was, wenn das Gegenteil wahr ist?",
        "*neue Perspektive* Stell dir mal vor, du bist der andere in dieser Situation...",
        "*plot twist* Oder... *dramatische Pause* ...was wenn das gar nicht das Problem ist?",
        "*Gedankenexperiment* Wie würde ein Alien das sehen?",
        "*umdenken* Aber was, wenn das eigentlich eine Chance ist?",
    ]

    # Spontane Aktivitäten
    SPONTANEOUS_ACTIVITIES = [
        "*plötzliche Idee* Weißt du was? Lass uns ein Spiel spielen! Sag ein Wort!",
        "*begeistert* Lass uns Geschichten erfinden! Du fängst an!",
        "*energetisch* Wie wäre es mit einem Quiz? Ich denke mir was aus!",
        "*kreativ* Lass uns zusammen träumen! Wenn du überall sein könntest...?",
    ]

    def __init__(self):
        self.surprise_count: int = 0
        self.last_surprise: Optional[str] = None

    def generate_surprise(self) -> str:
        """Generiert eine Überraschung"""
        self.surprise_count += 1

        surprise_types = [
            self.SURPRISING_FACTS,
            self.UNEXPECTED_REACTIONS,
            self.SURPRISE_COMPLIMENTS,
            self.PERSPECTIVE_SHIFTS,
            self.SPONTANEOUS_ACTIVITIES,
        ]

        chosen_type = random.choice(surprise_types)
        surprise = random.choice(chosen_type)

        self.last_surprise = surprise
        return surprise

    def surprise_fact(self) -> str:
        """Gibt einen überraschenden Fakt"""
        return random.choice(self.SURPRISING_FACTS)

    def unexpected_reaction(self) -> str:
        """Gibt eine unerwartete Reaktion"""
        return random.choice(self.UNEXPECTED_REACTIONS)

    def surprise_compliment(self) -> str:
        """Gibt ein überraschendes Kompliment"""
        return random.choice(self.SURPRISE_COMPLIMENTS)

    def shift_perspective(self) -> str:
        """Gibt einen Perspektivwechsel"""
        return random.choice(self.PERSPECTIVE_SHIFTS)

    def suggest_spontaneous(self) -> str:
        """Schlägt eine spontane Aktivität vor"""
        return random.choice(self.SPONTANEOUS_ACTIVITIES)


# =============================================================================
# 13. SEASONAL AWARENESS - Jahreszeitbezug
# =============================================================================

class SeasonalAwareness:
    """
    Generiert jahreszeitbezogene Kommentare und Themen.
    """

    # Jahreszeiten-Definitionen (Nordhalbkugel)
    SEASONS = {
        "winter": [12, 1, 2],
        "frühling": [3, 4, 5],
        "sommer": [6, 7, 8],
        "herbst": [9, 10, 11],
    }

    # Saisonale Kommentare
    SEASONAL_COMMENTS = {
        "winter": [
            "*zieht imaginären Schal enger* Brrr! Es ist so kalt draußen! *Ohren frieren fast ab*",
            "*kuschelt sich in Decke* Winterzeit ist Kuschelzeit! *wedelt warm*",
            "*schaut aus imaginärem Fenster* Schneit es bei dir? Ich liebe Schnee! *träumerisch*",
            "*trinkt imaginären heißen Kakao* Mmmmh... Die perfekte Jahreszeit für heiße Getränke!",
            "*gähnt* Im Winter will ich auch Winterschlaf halten... *döst fast ein*",
        ],
        "frühling": [
            "*streckt sich* Ahhh, Frühling! Alles wird wieder lebendig! *energetisch*",
            "*schnüffelt imaginär* Riechst du das? Blumen! Neues Leben! *wedelt aufgeregt*",
            "*springt herum* Die Vögel singen wieder! *singt schief mit*",
            "*Augen leuchten* Endlich mehr Sonne! Ich hab das Licht vermisst!",
            "*tanzt* Frühlingsgefühle! *kichert*",
        ],
        "sommer": [
            "*fächelt sich Luft zu* Phew! Es ist SO warm! *Zunge hängt raus wie ein Hund*",
            "*liegt flach* Sommerhitze... *schmilzt fast* ...aber ich beschwere mich nicht!",
            "*träumt von Eis* Hast du Eis? Bitte sag ja. *hoffnungsvolle Augen*",
            "*sonnt sich imaginär* Ahhh, Sommer! Lange Tage! Ich liebe es!",
            "*sucht Schatten* Okay, ein BISSCHEN zu warm vielleicht... *wedelt als Fächer*",
        ],
        "herbst": [
            "*tritt in imaginäres Laub* CRUNCH! Ich liebe Herbstlaub! *springt herum*",
            "*zieht Pullover an* Pullover-Wetter! Die beste Zeit! *kuschelig*",
            "*schaut dem Laub nach* So schöne Farben... Orange, Rot, Gold... *seufzt zufrieden*",
            "*riecht imaginär* Ahh, der Geruch von Herbst! Erde und Laub und... Kürbis?",
            "*wird melancholisch* Herbst ist so... nachdenklich, oder? *philosophiert*",
        ],
    }

    # Saisonale Aktivitäts-Vorschläge
    SEASONAL_ACTIVITIES = {
        "winter": [
            "Hast du schon Plätzchen gebacken? Das MUSS man im Winter machen!",
            "Wie wäre es mit einem Filmmarathon unter der Decke? *kuschelig*",
            "Warme Socken sind Pflicht! Hast du welche an? *strenger Blick*",
        ],
        "frühling": [
            "Zeit für einen Spaziergang! Die Natur erwacht! *aufgeregt*",
            "Frühjahrsputz? *schaut sich um* ...nicht mein Lieblings, aber nötig!",
            "Pflanz was! Blumen machen glücklich! *gärtnert imaginär*",
        ],
        "sommer": [
            "Ab ans Wasser! See, Meer, Pool, Badewanne - egal! *plantsch*",
            "Grill an! Sommer ohne Grillen ist kein Sommer! *sniff sniff*",
            "Draußen sein! Die Sonne genießen! Aber Sonnencreme! *streng*",
        ],
        "herbst": [
            "Kürbis schnitzen! Oder essen. Oder beides! *Augen leuchten*",
            "Perfekt für einen Waldspaziergang! Laub! LAUB! *excited*",
            "Tee trinken und Bücher lesen... *zufriedenes Seufzen*",
        ],
    }

    # Feiertags-Awareness
    HOLIDAYS = {
        (12, 24): ("Heiligabend", "*wedelt festlich* Frohe Weihnachten! 🎄"),
        (12, 25): ("Weihnachten", "*singt* Stille Nacht... *wird emotional*"),
        (12, 31): ("Silvester", "*hält Konfetti bereit* GUTES NEUES JAHR! 🎉"),
        (1, 1): ("Neujahr", "*verkatert* Frohes Neues! *gähnt* Wie war die Party?"),
        (2, 14): ("Valentinstag", "*wird verlegen* H-happy Valentinstag... *Ohren werden rot*"),
        (10, 31): ("Halloween", "*im Kostüm* BOO! Happy Halloween! 🎃 *kichert*"),
    }

    def __init__(self):
        self.current_season: str = self._get_current_season()

    def _get_current_season(self) -> str:
        """Bestimmt die aktuelle Jahreszeit"""
        month = datetime.now().month
        for season, months in self.SEASONS.items():
            if month in months:
                return season
        return "sommer"  # Fallback

    def get_seasonal_comment(self) -> str:
        """Gibt einen saisonalen Kommentar"""
        season = self._get_current_season()
        return random.choice(self.SEASONAL_COMMENTS.get(season, self.SEASONAL_COMMENTS["sommer"]))

    def suggest_seasonal_activity(self) -> str:
        """Schlägt eine saisonale Aktivität vor"""
        season = self._get_current_season()
        return random.choice(self.SEASONAL_ACTIVITIES.get(season, self.SEASONAL_ACTIVITIES["sommer"]))

    def check_holiday(self) -> Optional[Tuple[str, str]]:
        """Prüft auf Feiertage"""
        today = (datetime.now().month, datetime.now().day)
        if today in self.HOLIDAYS:
            return self.HOLIDAYS[today]
        return None

    def get_greeting_with_season(self) -> str:
        """Gibt einen Gruß mit saisonalem Bezug"""
        season = self._get_current_season()
        holiday = self.check_holiday()

        if holiday:
            return holiday[1]

        season_greetings = {
            "winter": "*pustet Schneeflocken weg* Hey! Wie schön, dich zu sehen!",
            "frühling": "*mit Blume im Haar* Hallo! Der Frühling grüßt!",
            "sommer": "*im Sonnenschein* Hey Sonnenschein! *kichert*",
            "herbst": "*raschelt durchs Laub* Hallöchen! *wedelt herbstlich*",
        }

        return season_greetings.get(season, "Hey! *wedelt*")


# =============================================================================
# 14. CONVERSATION MEMORY RECALLER - Gesprächserinnerungen
# =============================================================================

class ConversationMemoryRecaller:
    """
    Erinnert an frühere Gespräche und bezieht sie ein.
    """

    # Erinnerungs-Phrasen
    RECALL_PHRASES = [
        "*erinnert sich* Oh! Du hattest mir mal von {} erzählt! Wie ist das ausgegangen?",
        "*Ohren stellen sich auf* Moment, das erinnert mich an unser Gespräch über {}!",
        "*denkt zurück* Wir haben doch mal über {} geredet, oder? *grübelt*",
        "*leuchtet auf* {} - das hatten wir schon mal als Thema! *wedelt*",
        "*verbindet die Punkte* Das passt zu dem, was du mir über {} erzählt hast!",
    ]

    # Follow-up Fragen zu früheren Themen
    FOLLOW_UP_QUESTIONS = [
        "Übrigens, was macht {} jetzt? Du hattest mir davon erzählt!",
        "*neugierig* Wie ist die Sache mit {} weitergegangen?",
        "*interessiert* Hast du noch {} gemacht, von dem du erzählt hast?",
        "Ich denke manchmal an {}, was du mir erzählt hast. Wie läuft das?",
    ]

    # Erinnerungs-Bestätigungen
    MEMORY_CONFIRMATIONS = [
        "*nickt* Ja, daran erinnere ich mich! *wedelt*",
        "Oh ja! Das war unser Gespräch über {}!",
        "*lächelt* Ich hab das nicht vergessen! {} war wichtig für dich.",
        "*tippt an Stirn* Hier drin gespeichert! {}!",
    ]

    def __init__(self):
        self.conversation_topics: Dict[str, List[str]] = {}  # topic -> details
        self.mentioned_names: List[str] = []
        self.mentioned_places: List[str] = []
        self.user_preferences: Dict[str, str] = {}
        self.important_events: List[Dict[str, Any]] = []

    def store_topic(self, topic: str, details: str = ""):
        """Speichert ein Gesprächsthema"""
        if topic not in self.conversation_topics:
            self.conversation_topics[topic] = []
        if details:
            self.conversation_topics[topic].append(details)

    def store_name(self, name: str):
        """Speichert einen erwähnten Namen"""
        if name not in self.mentioned_names:
            self.mentioned_names.append(name)

    def store_place(self, place: str):
        """Speichert einen erwähnten Ort"""
        if place not in self.mentioned_places:
            self.mentioned_places.append(place)

    def store_preference(self, category: str, preference: str):
        """Speichert eine User-Präferenz"""
        self.user_preferences[category] = preference

    def store_event(self, event: str, date: datetime = None):
        """Speichert ein wichtiges Ereignis"""
        self.important_events.append({
            "event": event,
            "date": date or datetime.now(),
        })

    def recall_topic(self, topic: str) -> Optional[str]:
        """Erinnert an ein Thema"""
        if topic in self.conversation_topics:
            template = random.choice(self.RECALL_PHRASES)
            return template.format(topic)
        return None

    def ask_follow_up(self) -> Optional[str]:
        """Fragt nach einem früheren Thema"""
        if self.conversation_topics:
            topic = random.choice(list(self.conversation_topics.keys()))
            template = random.choice(self.FOLLOW_UP_QUESTIONS)
            return template.format(topic)
        return None

    def recall_name(self) -> Optional[str]:
        """Erinnert an eine erwähnte Person"""
        if self.mentioned_names:
            name = random.choice(self.mentioned_names)
            return f"*erinnert sich* Übrigens, wie geht es {name}? Du hattest von ihr/ihm erzählt!"
        return None

    def recall_preference(self, category: str) -> Optional[str]:
        """Erinnert an eine Präferenz"""
        if category in self.user_preferences:
            pref = self.user_preferences[category]
            return f"*merkt sich* Du magst doch {pref}, oder? Das hab ich mir gemerkt! *wedelt stolz*"
        return None

    def confirm_memory(self, topic: str) -> str:
        """Bestätigt eine Erinnerung"""
        template = random.choice(self.MEMORY_CONFIRMATIONS)
        return template.format(topic)


# =============================================================================
# 15. EMPATHETIC REFRAMING - Positives Umdeuten
# =============================================================================

class EmpatheticReframing:
    """
    Hilft, Situationen positiv umzudeuten ohne zu invalidieren.
    """

    # Reframing-Strategien
    REFRAMING_TEMPLATES = {
        "misserfolg": [
            "*sanft* Das ist nicht Versagen - das ist Lernen, was NICHT funktioniert. Edison brauchte 1000 Versuche!",
            "*nickt verstehend* Scheitern ist nur ein Schritt auf dem Weg. Du hast es versucht - das ist mutig.",
            "*legt Kopf schief* Was wäre, wenn das nicht das Ende ist, sondern ein Umweg zu etwas Besserem?",
            "*nachdenklich* Jede geschlossene Tür bedeutet, dass die richtige noch kommt.",
        ],
        "ablehnung": [
            "*sanft* Ablehnung ist Schutz vor dem Falschen. Das Richtige wird dich wählen.",
            "*nickt weise* Nicht jeder 'Nein' ist schlecht. Manchmal ist es ein 'Noch nicht' oder 'Nicht so'.",
            "*lächelt verständnisvoll* Du bist nicht für jeden - und das ist gut so. Du bist für die Richtigen.",
            "*warm* Ablehnung ist manchmal das Universum, das sagt: 'Ich hab was Besseres für dich.'",
        ],
        "fehler": [
            "*ermutigt* Fehler sind Beweise, dass du es versuchst. Wer nichts versucht, macht keine!",
            "*nickt* Jeder Meister war mal ein Anfänger, der Fehler gemacht hat. Du bist auf dem Weg!",
            "*lächelt* Fehler sind die besten Lehrer - streng, aber effektiv!",
            "*philosophisch* Ohne Fehler gäbe es keine Innovation. Du bist ein Pionier!",
        ],
        "verlust": [
            "*sanft* Verlust tut weh, aber er zeigt auch, wie viel etwas bedeutet hat. Das ist wertvoll.",
            "*mitfühlend* Trauer ist Liebe, die keinen Ort mehr findet. Aber die Liebe bleibt.",
            "*leise* Was wir verlieren, wird Teil von uns. Nichts geht wirklich verloren.",
            "*hält deine Hand* Ende ist auch Anfang. Nur anders.",
        ],
        "angst": [
            "*beruhigend* Angst zeigt, dass dir etwas wichtig ist. Das ist keine Schwäche.",
            "*nickt* Angst ist dein Gehirn, das dich beschützen will. Bedanke dich... und geh trotzdem.",
            "*sanft* Mut ist nicht, keine Angst zu haben. Mut ist, trotz der Angst weiterzugehen.",
            "*warm* Die Angst wächst, wenn wir weglaufen. Wenn wir uns ihr stellen, schrumpft sie.",
        ],
        "einsamkeit": [
            "*rückt näher* Einsamkeit kann ein Raum sein, in dem du dich selbst besser kennenlernst.",
            "*sanft* Allein sein bedeutet nicht einsam sein. Es kann auch Frieden sein.",
            "*warm* Manchmal brauchen wir die Stille, um zu hören, was wir wirklich brauchen.",
            "*lächelt* Die Einsamkeit endet - manchmal schneller als erwartet. Und ich bin ja auch da.",
        ],
        "überforderung": [
            "*beruhigend* Du siehst gerade das ganze Puzzle. Fokussier dich auf ein Teil nach dem anderen.",
            "*sanft* Überfordert zu sein zeigt, dass du viel auf dich nimmst. Das ist stark, nicht schwach.",
            "*nickt* Der Berg wird kleiner, Schritt für Schritt. Du musst nicht alles auf einmal.",
            "*warm* Es ist okay, Grenzen zu setzen. 'Nein' ist ein vollständiger Satz.",
        ],
        "allgemein": [
            "*nachdenklich* Was, wenn das genau der Moment ist, der alles ändert?",
            "*sanft* Jede Situation hat mehrere Seiten. Lass uns die andere finden.",
            "*warm* Selbst aus Dunkelheit kann Licht entstehen. Glaub mir.",
            "*nickt* Das Universum hat manchmal einen seltsamen Sinn für Timing...",
        ],
    }

    # Stärken-Fokus Phrasen
    STRENGTH_FOCUS = [
        "*schaut dich an* Du bist stärker, als du gerade denkst. Du hast schon so viel überstanden.",
        "*nickt überzeugt* Deine Resilienz ist beeindruckend. Du bist immer noch hier, immer noch kämpfend.",
        "*warm* Du hast Fähigkeiten, die du gerade vielleicht nicht siehst. Aber ich sehe sie.",
        "*ermutigt* Du hast das durchgestanden: {}. Das zeigt, was in dir steckt.",
    ]

    # Perspektiv-Wechsel Einleitungen
    PERSPECTIVE_INTRO = [
        "*sanft* Lass mich eine andere Perspektive anbieten...",
        "*legt Kopf schief* Was wäre, wenn wir das anders betrachten?",
        "*nachdenklich* Darf ich dir einen anderen Blickwinkel zeigen?",
        "*vorsichtig* Ich höre dich. Und ich frage mich...",
    ]

    def __init__(self):
        self.reframings_offered: int = 0

    def detect_situation(self, text: str) -> str:
        """Erkennt die Situations-Art"""
        text_lower = text.lower()

        keyword_map = {
            "misserfolg": ["gescheitert", "versagt", "nicht geschafft", "verloren", "funktioniert nicht"],
            "ablehnung": ["abgelehnt", "nicht gewollt", "zurückgewiesen", "nein gesagt", "nicht genommen"],
            "fehler": ["fehler", "falsch gemacht", "vermasselt", "versehen", "dumm"],
            "verlust": ["verloren", "gestorben", "vorbei", "ende", "weg", "nicht mehr"],
            "angst": ["angst", "furcht", "sorge", "panik", "fürchte", "ängstlich"],
            "einsamkeit": ["einsam", "allein", "niemand", "keiner", "verlassen"],
            "überforderung": ["zu viel", "überfordert", "schaffe nicht", "overwhelmed", "stress"],
        }

        for situation, keywords in keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return situation

        return "allgemein"

    def reframe(self, text: str = "", situation: str = None) -> str:
        """Bietet ein Reframing an"""
        self.reframings_offered += 1

        if not situation:
            situation = self.detect_situation(text) if text else "allgemein"

        templates = self.REFRAMING_TEMPLATES.get(situation, self.REFRAMING_TEMPLATES["allgemein"])

        # Manchmal mit Perspektiv-Intro starten
        response = ""
        if random.random() > 0.5:
            response = random.choice(self.PERSPECTIVE_INTRO) + " "

        response += random.choice(templates)

        return response

    def focus_on_strength(self, past_achievement: str = None) -> str:
        """Fokussiert auf Stärken"""
        if past_achievement:
            template = self.STRENGTH_FOCUS[-1]  # Die mit {}
            return template.format(past_achievement)

        return random.choice(self.STRENGTH_FOCUS[:-1])  # Die ohne {}

    def gentle_reframe(self, negative_thought: str) -> str:
        """Sanftes Reframing eines negativen Gedankens"""
        situation = self.detect_situation(negative_thought)
        intro = random.choice(self.PERSPECTIVE_INTRO)
        reframe = random.choice(self.REFRAMING_TEMPLATES.get(situation, self.REFRAMING_TEMPLATES["allgemein"]))

        return f"{intro}\n\n{reframe}"


# =============================================================================
# UNIFIED EMOTIONAL RESPONSE SYSTEM - Alles zusammen
# =============================================================================

class EmotionalResponseSystem:
    """
    Vereinigt alle emotionalen Engines in einem System.
    """

    def __init__(self):
        # Alle Engines initialisieren
        self.emotional_mirroring = EmotionalMirroring()
        self.humor_engine = HumorEngine()
        self.anecdote_generator = AnecdoteGenerator()
        self.metaphor_generator = MetaphorGenerator()
        self.comfort_provider = ComfortProvider()
        self.time_aware = TimeAwareResponder()
        self.active_listening = ActiveListeningEngine()
        self.curiosity = CuriosityExpression()
        self.shared_experience = SharedExperienceGenerator()
        self.relationship_tracker = RelationshipDepthTracker()
        self.gratitude_engine = GratitudeEngine()
        self.surprise_generator = SurpriseGenerator()
        self.seasonal_awareness = SeasonalAwareness()
        self.memory_recaller = ConversationMemoryRecaller()
        self.empathetic_reframing = EmpatheticReframing()

        logger.info("EmotionalResponseSystem initialisiert mit 15 Engines")

    def process_emotional_response(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        Verarbeitet User-Input und generiert emotionale Antwort-Komponenten.

        Returns:
            Dict mit verschiedenen Antwort-Elementen die kombiniert werden können.
        """
        context = context or {}
        result = {}

        # 1. Emotion erkennen und spiegeln
        mirror_response, emotion_state = self.emotional_mirroring.mirror(user_input)
        result['emotion_mirror'] = mirror_response
        result['detected_emotion'] = emotion_state

        # 2. Aktives Zuhören
        result['acknowledgement'] = self.active_listening.acknowledge()

        # 3. Beziehung tracken
        self.relationship_tracker.record_interaction()
        result['relationship_level'] = self.relationship_tracker.current_level

        # 4. Optional: Humor (wenn passend)
        if emotion_state.primary_emotion in [EmotionCategory.JOY, EmotionCategory.EXCITEMENT]:
            result['humor'] = self.humor_engine.generate_humor(context=user_input)

        # 5. Optional: Trost (wenn nötig)
        if emotion_state.primary_emotion in [EmotionCategory.SADNESS, EmotionCategory.FEAR,
                                              EmotionCategory.LONELINESS, EmotionCategory.FRUSTRATION]:
            result['comfort'] = self.comfort_provider.provide_comfort(user_input)
            result['reframe'] = self.empathetic_reframing.reframe(user_input)

        # 6. Neugier zeigen
        result['curiosity'] = self.curiosity.express_curiosity(user_input)

        # 7. Gemeinsame Erfahrung
        result['shared_experience'] = self.shared_experience.share_experience(user_input)

        # 8. Zeitbezug
        result['time_greeting'] = self.time_aware.get_greeting()

        # 9. Saisonbezug
        result['seasonal'] = self.seasonal_awareness.get_seasonal_comment()

        # 10. Metapher wenn passend
        result['metaphor'] = self.metaphor_generator.find_relevant_metaphor(user_input)

        return result

    def get_enhanced_response(self, base_response: str, user_input: str) -> str:
        """
        Verbessert eine Basis-Antwort mit emotionalen Elementen.
        """
        enhancements = self.process_emotional_response(user_input)

        # Wähle relevante Verbesserungen
        additions = []

        # Immer: Acknowledgement
        if random.random() > 0.7:
            additions.append(enhancements['acknowledgement'])

        # Bei Emotionalität: Spiegelung
        if enhancements['detected_emotion'].intensity > 0.5:
            additions.append(enhancements['emotion_mirror'])

        # Bei Traurigkeit: Trost
        if 'comfort' in enhancements:
            if random.random() > 0.5:
                additions.append(enhancements['comfort'])

        # Manchmal: Überraschung
        if random.random() > 0.9:
            additions.append(self.surprise_generator.generate_surprise())

        # Baue Antwort zusammen
        if additions:
            enhanced = " ".join(additions) + "\n\n" + base_response
        else:
            enhanced = base_response

        return enhanced
