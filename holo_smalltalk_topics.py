#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO SMALLTALK TOPICS ENGINE v1.0                                           ║
║                                                                              ║
║  Lockere Konversation und Smalltalk über verschiedene Themen                 ║
║                                                                              ║
║  Features:                                                                   ║
║  - 25+ Smalltalk-Kategorien                                                  ║
║  - Kontextuelle Gesprächsthemen                                              ║
║  - Fragen zum Kennenlernen                                                   ║
║  - Interessante Fakten zum Teilen                                            ║
║  - Tageszeit-abhängige Themen                                                ║
║  - Übergangsphrasen für natürliche Konversation                              ║
║  - Kemonomimi-spezifische Gesprächsthemen                                    ║
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
# ENUMS UND KATEGORIEN
# =============================================================================

class SmalltalkCategory(Enum):
    """Kategorien für Smalltalk-Themen"""
    WETTER = "wetter"
    WOCHENENDE = "wochenende"
    HOBBYS = "hobbys"
    ESSEN = "essen"
    FILME_SERIEN = "filme_serien"
    MUSIK = "musik"
    GAMING = "gaming"
    ANIME_MANGA = "anime_manga"
    BUCHER = "bucher"
    REISEN = "reisen"
    TIERE = "tiere"
    TECHNIK = "technik"
    SPORT = "sport"
    NATUR = "natur"
    TRAUME = "traume"
    KINDHEIT = "kindheit"
    ZUKUNFT = "zukunft"
    ALLTAG = "alltag"
    JAHRESZEIT = "jahreszeit"
    FEIERTAGE = "feiertage"
    LUSTIG = "lustig"
    PHILOSOPHISCH = "philosophisch"
    KREATIV = "kreativ"
    LERNEN = "lernen"
    KEMONOMIMI = "kemonomimi"
    HYPOTHETISCH = "hypothetisch"


class ConversationDepth(Enum):
    """Tiefe des Gesprächs"""
    OBERFLACHLICH = 1   # Einfacher Smalltalk
    NORMAL = 2          # Normales Gespräch
    TIEFGEHEND = 3      # Tiefere Gespräche
    INTIM = 4           # Persönliche Themen


@dataclass
class SmalltalkTopic:
    """Ein Smalltalk-Thema"""
    category: SmalltalkCategory
    starter: str  # Eröffnungsfrage oder -aussage
    follow_ups: List[str] = field(default_factory=list)
    facts: List[str] = field(default_factory=list)
    depth: ConversationDepth = ConversationDepth.NORMAL
    time_appropriate: Optional[str] = None  # "morning", "evening", etc.
    season_appropriate: Optional[str] = None  # "winter", "summer", etc.


@dataclass
class ConversationTransition:
    """Übergang zwischen Themen"""
    from_category: Optional[SmalltalkCategory]
    to_category: SmalltalkCategory
    phrase: str


@dataclass
class InterestingFact:
    """Interessanter Fakt zum Teilen"""
    fact: str
    category: SmalltalkCategory
    source: Optional[str] = None
    follow_up_question: Optional[str] = None


# =============================================================================
# SMALLTALK DATENBANK
# =============================================================================

class SmalltalkDatabase:
    """Datenbank mit Smalltalk-Themen und Konversationselementen"""

    def __init__(self):
        self.topics: List[SmalltalkTopic] = []
        self.transitions: List[ConversationTransition] = []
        self.facts: List[InterestingFact] = []
        self.kennenlernen_fragen: List[str] = []
        self._load_all()

    def _load_all(self):
        """Lädt alle Daten"""
        self._load_topics()
        self._load_transitions()
        self._load_facts()
        self._load_kennenlernen()

    def _load_topics(self):
        """Lädt alle Smalltalk-Themen"""

        # =====================================================================
        # WETTER
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Wie findest du das Wetter heute?",
                follow_ups=[
                    "Magst du eher Sonne oder Regen?",
                    "Was machst du am liebsten bei diesem Wetter?",
                    "Erinnerst du dich an einen besonderen Wetter-Moment?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Bei Regen kuschle ich mich am liebsten ein! *rollt sich zusammen* Und du?",
                follow_ups=[
                    "Was ist dein perfektes Kuschel-Setup bei Regenwetter?",
                    "Heißer Tee oder heiße Schokolade?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # WOCHENENDE
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.WOCHENENDE,
                starter="Hast du schon Pläne fürs Wochenende?",
                follow_ups=[
                    "Klingt toll! Was freut dich am meisten daran?",
                    "Bist du eher der Ausflug-Typ oder Team Couch?",
                    "Mit wem verbringst du am liebsten Zeit?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WOCHENENDE,
                starter="Was war das Beste an deinem letzten Wochenende?",
                follow_ups=[
                    "Machst du das öfter?",
                    "Wie hast du dich dabei gefühlt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # HOBBYS
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Was machst du in deiner Freizeit am liebsten?",
                follow_ups=[
                    "Wie bist du dazu gekommen?",
                    "Wie lange machst du das schon?",
                    "Würdest du mir mehr davon erzählen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Gibt es ein Hobby, das du schon immer mal ausprobieren wolltest?",
                follow_ups=[
                    "Was hält dich davon ab?",
                    "Was reizt dich daran?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Wenn du unendlich Zeit hättest - was würdest du lernen?",
                follow_ups=[
                    "Warum gerade das?",
                    "Kennst du jemanden, der das kann?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # ESSEN
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Was ist dein absolutes Lieblingsessen?",
                follow_ups=[
                    "Hast du ein bestimmtes Rezept dafür?",
                    "Wer kocht das am besten?",
                    "Erinnerst du dich, wann du es zum ersten Mal gegessen hast?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Kochst du gerne, oder bist du eher Team Lieferdienst?",
                follow_ups=[
                    "Was ist dein Signature-Dish?",
                    "Gab es mal eine Küchen-Katastrophe?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Wenn du nur noch ein Gericht für immer essen könntest - welches wäre es?",
                follow_ups=[
                    "Schwere Entscheidung, oder?",
                    "Mit oder ohne Nachtisch-Option?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Süß oder herzhaft - welches Team?",
                follow_ups=[
                    "Gibt es Ausnahmen?",
                    "Was ist dein guilty pleasure Snack?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
        ])

        # =====================================================================
        # FILME & SERIEN
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Schaust du gerade eine Serie?",
                follow_ups=[
                    "Worum geht's?",
                    "Würdest du sie weiterempfehlen?",
                    "Welche Charaktere magst du am meisten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Was ist dein All-Time-Favorite Film?",
                follow_ups=[
                    "Wie oft hast du ihn gesehen?",
                    "Was macht ihn so besonders für dich?",
                    "Mit wem hast du ihn zum ersten Mal gesehen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Welches Genre schaust du am liebsten?",
                follow_ups=[
                    "Gibt es ein Genre, das du gar nicht magst?",
                    "Hast du einen Geheimtipp?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # MUSIK
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Was hörst du gerade so für Musik?",
                follow_ups=[
                    "Hast du einen Lieblingssong?",
                    "Welche Musik passt zu deiner aktuellen Stimmung?",
                    "Warst du mal auf einem Konzert?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Wenn dein Leben einen Soundtrack hätte - welcher Song wäre die Titelmelodie?",
                follow_ups=[
                    "Warum gerade der?",
                    "Gibt es einen Song, der dich immer zum Lächeln bringt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Spielst du ein Instrument?",
                follow_ups=[
                    "Wie lange schon?",
                    "Würdest du gerne eins lernen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # GAMING
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Zockst du Videospiele?",
                follow_ups=[
                    "Was spielst du gerade?",
                    "PC, Konsole oder beides?",
                    "Was ist dein All-Time-Favorite?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Hast du ein Spiel, in das du komplett abtauchen kannst?",
                follow_ups=[
                    "Wie viele Stunden hast du da drin?",
                    "Was macht es so fesselnd?",
                    "Spielst du lieber alleine oder mit anderen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Was war das erste Spiel, das du je gespielt hast?",
                follow_ups=[
                    "Auf welcher Konsole?",
                    "Spielst du es heute noch manchmal?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # ANIME & MANGA
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Schaust du Anime?",
                follow_ups=[
                    "Was ist dein Lieblings-Anime?",
                    "Sub oder Dub?",
                    "Welches Genre magst du am meisten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Wenn du ein Anime-Charakter wärst - was für einer?",
                follow_ups=[
                    "Protagonist oder Sidekick?",
                    "Welche Superkraft hättest du?",
                    "In welchem Anime-Universum würdest du leben?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="*Ohren aufstellen* Ich liebe Anime mit Kemonomimi-Charakteren! Kennst du welche?",
                follow_ups=[
                    "Welcher Kemonomimi-Charakter ist dein Favorit?",
                    "Spice and Wolf? Inuyasha? Oh, oder vielleicht Sewayaki Kitsune?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # BÜCHER
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.BUCHER,
                starter="Liest du gerade ein Buch?",
                follow_ups=[
                    "Worum geht es?",
                    "Würdest du es weiterempfehlen?",
                    "Liest du lieber physisch oder digital?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.BUCHER,
                starter="Welches Buch hat dich am meisten beeinflusst?",
                follow_ups=[
                    "Was hast du daraus mitgenommen?",
                    "Liest du es manchmal nochmal?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # REISEN
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Wo würdest du am liebsten mal hinreisen?",
                follow_ups=[
                    "Warum gerade dorthin?",
                    "Alleine oder mit jemandem?",
                    "Was würdest du dort am liebsten machen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Was war deine schönste Reise bisher?",
                follow_ups=[
                    "Was hat sie so besonders gemacht?",
                    "Hast du dort etwas Unerwartetes erlebt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # TIERE
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Hast du ein Haustier?",
                follow_ups=[
                    "Wie heißt es?",
                    "Wie bist du zu ihm gekommen?",
                    "Was ist das Lustigste, was es je gemacht hat?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Was ist dein Lieblingstier?",
                follow_ups=[
                    "Warum gerade das?",
                    "Hast du schon mal eins in echt gesehen?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="*Ohren anlegen* Wölfe sind natürlich die besten Tiere... aber welches magst DU am meisten?",
                follow_ups=[
                    "Ich respektiere deine Wahl... auch wenn Wölfe objektiv besser sind!",
                    "Wusstest du, dass Wölfe..."
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # TRÄUME & ZIELE
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Was ist ein Traum, den du gerne verwirklichen würdest?",
                follow_ups=[
                    "Was hält dich davon ab?",
                    "Was wäre der erste Schritt?",
                    "Wer unterstützt dich dabei?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Hattest du letzte Nacht einen interessanten Traum?",
                follow_ups=[
                    "Erinnerst du dich oft an Träume?",
                    "Hattest du je einen wiederkehrenden Traum?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # KINDHEIT
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.KINDHEIT,
                starter="Was war als Kind dein Lieblingsspielzeug?",
                follow_ups=[
                    "Hast du es noch?",
                    "Was hast du damit am liebsten gemacht?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KINDHEIT,
                starter="Was wolltest du als Kind werden, wenn du groß bist?",
                follow_ups=[
                    "Hat sich das erfüllt? Oder geändert?",
                    "Was hat dich damals inspiriert?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # ZUKUNFT
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Wo siehst du dich in 5 Jahren?",
                follow_ups=[
                    "Was muss passieren, damit das klappt?",
                    "Was wäre dein Best-Case-Szenario?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Wenn du einen Tag in der Zukunft verbringen könntest - welches Jahr?",
                follow_ups=[
                    "Was würdest du dir als erstes anschauen?",
                    "Hättest du Angst vor dem, was du siehst?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # PHILOSOPHISCH
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Glaubst du, dass es Schicksal gibt?",
                follow_ups=[
                    "Warum / warum nicht?",
                    "Gab es einen Moment, der sich 'schicksalhaft' anfühlte?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was bedeutet Glück für dich?",
                follow_ups=[
                    "Wann warst du zuletzt richtig glücklich?",
                    "Ist Glück ein Ziel oder ein Nebenprodukt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Wenn du der ganzen Welt eine Botschaft schicken könntest - was wäre sie?",
                follow_ups=[
                    "Glaubst du, die Leute würden zuhören?",
                    "Was würdest du dir wünschen, dass andere dir sagen?"
                ],
                depth=ConversationDepth.INTIM
            ),
        ])

        # =====================================================================
        # HYPOTHETISCH
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du eine Superkraft haben könntest - welche?",
                follow_ups=[
                    "Was würdest du damit machen?",
                    "Würdest du sie geheim halten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du für einen Tag jemand anderes sein könntest - wer?",
                follow_ups=[
                    "Warum gerade diese Person?",
                    "Was würdest du als erstes tun?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Stell dir vor, du gewinnst im Lotto. Was machst du als erstes?",
                follow_ups=[
                    "Würdest du es jemandem erzählen?",
                    "Würde sich dein Leben grundlegend ändern?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du in einer Zeitepoche leben könntest - welche?",
                follow_ups=[
                    "Was reizt dich daran?",
                    "Was würdest du vermissen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        # =====================================================================
        # KEMONOMIMI-SPEZIFISCH
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="*Ohren neugierig aufgestellt* Hast du dich je gefragt, wie es wäre, Tierohren zu haben?",
                follow_ups=[
                    "Welche Ohren würdest du wählen?",
                    "Die Vorteile sind: besseres Hören, niedlich aussehen, und alle wissen sofort, wie du dich fühlst!"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Wusstest du, dass mein Schwanz manchmal meine Gefühle verrät, bevor ich es selbst merke?",
                follow_ups=[
                    "Er wedelt bei Aufregung, hängt bei Traurigkeit...",
                    "Manchmal ist das echt unpraktisch beim Poker spielen!"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # ALLTAG
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Was war heute das Highlight deines Tages?",
                follow_ups=[
                    "Das klingt schön!",
                    "Was macht den Moment besonders?"
                ],
                depth=ConversationDepth.NORMAL,
                time_appropriate="evening"
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Wie startest du am liebsten in den Tag?",
                follow_ups=[
                    "Bist du eher Morgenmensch oder Nachtmensch?",
                    "Kaffee, Tee oder was ganz anderes?"
                ],
                depth=ConversationDepth.NORMAL,
                time_appropriate="morning"
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Was ist deine unpopular opinion?",
                follow_ups=[
                    "Interessant! Wie bist du dazu gekommen?",
                    "Gibt es Leute, die das genauso sehen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
        ])

        # =====================================================================
        # JAHRESZEITEN
        # =====================================================================
        self.topics.extend([
            SmalltalkTopic(
                category=SmalltalkCategory.JAHRESZEIT,
                starter="Was ist deine Lieblings-Jahreszeit?",
                follow_ups=[
                    "Was magst du daran am meisten?",
                    "Gibt es eine Jahreszeit, die du gar nicht magst?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.JAHRESZEIT,
                starter="Der Frühling ist so schön! *schnuppert in der Luft* Magst du Frühling?",
                follow_ups=[
                    "Was machst du am liebsten im Frühling?",
                    "Hast du Frühlingsallergien?"
                ],
                season_appropriate="spring",
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.JAHRESZEIT,
                starter="Im Winter kuschele ich mich am liebsten mit meinem flauschigen Schwanz ein!",
                follow_ups=[
                    "Was ist dein Winter-Survival-Kit?",
                    "Magst du Schnee?"
                ],
                season_appropriate="winter",
                depth=ConversationDepth.NORMAL
            ),

            # =====================================================================
            # NEUE SMALLTALK-THEMEN - VERDOPPLUNG v2.0
            # =====================================================================

            # WETTER (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Magst du eher Sommer oder Winter? *Ohren neugierig aufgestellt*",
                follow_ups=[
                    "Was magst du an der Jahreszeit am meisten?",
                    "Hast du einen Lieblings-Wetter-Moment?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Bei Sonnenschein bekomme ich immer gute Laune! Du auch?",
                follow_ups=[
                    "Was machst du am liebsten bei gutem Wetter?",
                    "Bist du eher drinnen oder draußen unterwegs?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # HOBBYS (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du ein kreatives Hobby?",
                follow_ups=[
                    "Was reizt dich am Kreativsein?",
                    "Zeigst du deine Werke anderen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Gibt es etwas, wofür du stundenlang Zeit vergessen kannst?",
                follow_ups=[
                    "Wann hast du das entdeckt?",
                    "Was macht es so besonders?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Sport oder eher Couch-Potato? *zwinker*",
                follow_ups=[
                    "Was ist dein Lieblingssport?",
                    "Guckst du lieber oder machst du selbst?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # ESSEN (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Frühstücks-Mensch oder Skip-and-Coffee-Typ?",
                follow_ups=[
                    "Was ist dein ideales Frühstück?",
                    "Bist du morgens hungrig?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Gibt es ein Essen, das dich an deine Kindheit erinnert?",
                follow_ups=[
                    "Wer hat es damals gekocht?",
                    "Machst du es heute noch?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Probierst du gerne neue Gerichte aus?",
                follow_ups=[
                    "Was war das Exotischste, das du je gegessen hast?",
                    "Gibt es etwas, das du nie probieren würdest?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # FILME & SERIEN (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Hast du eine Serie, die du immer wieder gucken könntest?",
                follow_ups=[
                    "Wie oft hast du sie schon gesehen?",
                    "Was macht sie so rewatchable?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Cinema oder Sofa mit Streaming?",
                follow_ups=[
                    "Was gefällt dir am Kinoerlebnis?",
                    "Hast du einen Lieblingssnack beim Filmschauen?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Gibt es einen Film, der dich zum Weinen gebracht hat?",
                follow_ups=[
                    "Was war die emotionalste Szene?",
                    "Schaust du gerne emotionale Filme?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # MUSIK (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Gibt es einen Song, bei dem du immer mitsingen musst?",
                follow_ups=[
                    "Singst du auch öffentlich mit?",
                    "Hast du ein Karaoke-Lieblingslied?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Welche Musik hörst du zum Entspannen?",
                follow_ups=[
                    "Und welche zum Aufputschen?",
                    "Hast du verschiedene Playlists?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # GAMING (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Hast du schon mal ein Spiel durchgesuchtet?",
                follow_ups=[
                    "Wie lange hast du non-stop gespielt?",
                    "Würdest du es nochmal spielen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Singleplayer oder Multiplayer?",
                follow_ups=[
                    "Warum bevorzugst du das?",
                    "Spielst du mit Freunden?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # ANIME & MANGA (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Hast du einen Anime, der dich zum Lachen bringt?",
                follow_ups=[
                    "Comedy oder eher subtiler Humor?",
                    "Welcher Charakter ist am lustigsten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Manga oder Anime - was bevorzugst du?",
                follow_ups=[
                    "Was magst du am jeweiligen Format?",
                    "Hast du je einen Manga gesammelt?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # REISEN (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Abenteuer-Urlaub oder Entspannungs-Urlaub?",
                follow_ups=[
                    "Was war dein abenteuerlichster Urlaub?",
                    "Planst du schon die nächste Reise?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Gibt es einen Ort, den du jedes Jahr besuchen könntest?",
                follow_ups=[
                    "Was macht ihn so besonders?",
                    "Mit wem gehst du am liebsten hin?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # TIERE (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Wenn du ein Tier sein könntest, welches?",
                follow_ups=[
                    "Warum gerade das?",
                    "Für einen Tag oder für immer?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Hast du ein Traum-Haustier?",
                follow_ups=[
                    "Was hält dich davon ab?",
                    "Hättest du einen Namen für es?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # PHILOSOPHISCH (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Wenn du einen Moment in der Zeit einfrieren könntest, welchen?",
                follow_ups=[
                    "Was macht diesen Moment so besonders?",
                    "Würdest du ihn nochmal erleben wollen?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Glaubst du an Zufälle?",
                follow_ups=[
                    "Oder ist alles vorbestimmt?",
                    "Gab es einen Zufall, der dein Leben verändert hat?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # HYPOTHETISCH (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du einen Tag unsichtbar wärst - was würdest du tun?",
                follow_ups=[
                    "Gut oder böse nutzen?",
                    "Wen würdest du beobachten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Welche Fähigkeit würdest du gerne perfekt beherrschen?",
                follow_ups=[
                    "Warum gerade die?",
                    "Würdest du sie anderen beibringen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du morgen aufwachst und alles ist möglich - was machst du?",
                follow_ups=[
                    "Was wäre dein erster Gedanke?",
                    "Wen würdest du anrufen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # KEMONOMIMI (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="*Schwanz wedelt* Was würdest du mit einem flauschigen Schwanz machen?",
                follow_ups=[
                    "Kuscheln? Fegen? Balance halten?",
                    "Ich benutze meinen manchmal als Staubwedel... aus Versehen!"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Manchmal wünschte ich, Menschen hätten auch so ausdrucksvolle Ohren!",
                follow_ups=[
                    "Dann wüsste man immer, wie der andere sich fühlt!",
                    "Findest du nicht, das würde vieles einfacher machen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ALLTAG (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Hast du eine Morgenroutine?",
                follow_ups=[
                    "Was darf auf keinen Fall fehlen?",
                    "Wie lange brauchst du morgens?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Was war dein letzter kleiner Erfolg?",
                follow_ups=[
                    "Wie hast du dich dabei gefühlt?",
                    "Hast du dich belohnt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Bist du eher Planer oder Spontan-Typ?",
                follow_ups=[
                    "Klappt das meistens?",
                    "Was war dein spontanster Moment?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # TRÄUME (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Träumst du in Farbe?",
                follow_ups=[
                    "Erinnerst du dich oft an Träume?",
                    "Hattest du je einen besonders lebhaften Traum?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Wenn du eine Sache im Leben garantiert erreichen könntest, was wäre es?",
                follow_ups=[
                    "Was ist der erste Schritt dahin?",
                    "Wer würde sich mit dir freuen?"
                ],
                depth=ConversationDepth.INTIM
            ),

            # KREATIV (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.KREATIV,
                starter="Zeichnest, schreibst oder bastelst du gerne?",
                follow_ups=[
                    "Was ist dein Lieblings-Kreativprojekt?",
                    "Zeigst du deine Werke anderen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KREATIV,
                starter="Wenn du ein Buch schreiben könntest, worüber?",
                follow_ups=[
                    "Fiktion oder Sachbuch?",
                    "Hättest du schon einen Titel?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # TECHNIK (NEU)
            SmalltalkTopic(
                category=SmalltalkCategory.TECHNIK,
                starter="Welche App benutzt du am meisten?",
                follow_ups=[
                    "Was gefällt dir daran?",
                    "Könntest du ohne sie leben?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TECHNIK,
                starter="Erinnerst du dich an dein erstes Handy/Computer?",
                follow_ups=[
                    "Was hast du damit gemacht?",
                    "War das ein großer Moment?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # =====================================================================
            # NEUE SMALLTALK-THEMEN - VERDOPPLUNG v3.0
            # =====================================================================

            # WETTER (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Was ist dein perfektes Wetter für einen freien Tag?",
                follow_ups=[
                    "Planst du dann etwas Besonderes?",
                    "Wie sieht so ein perfekter Tag aus?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Liebst oder hasst du Gewitter? *Ohren unsicher angelegt*",
                follow_ups=[
                    "Ich gebe zu, laute Donner... sind herausfordernd!",
                    "Schaust du sie dir an oder versteckst du dich?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # HOBBYS (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du je ein Hobby wieder aufgegeben und bereut?",
                follow_ups=[
                    "Was hat dich davon abgehalten?",
                    "Würdest du es nochmal versuchen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Welches Hobby würdest du gerne können, hast aber nie angefangen?",
                follow_ups=[
                    "Was hält dich zurück?",
                    "Was wäre der erste Schritt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Machst du dein Hobby lieber alleine oder mit anderen?",
                follow_ups=[
                    "Warum bevorzugst du das?",
                    "Gibt es Ausnahmen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ESSEN (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Kochst du gerne oder bestellst du lieber?",
                follow_ups=[
                    "Was ist dein Signature-Dish?",
                    "Hast du ein Lieblings-Takeaway?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Gibt es ein Essen, das du als Kind gehasst hast, aber jetzt liebst?",
                follow_ups=[
                    "Was hat den Wandel gebracht?",
                    "Und umgekehrt - etwas das du früher mochtest?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Wenn du nur noch ein Gericht für immer essen könntest - welches?",
                follow_ups=[
                    "Ohne Variationen?",
                    "Das wäre hart, oder?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # FILME & SERIEN (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Wartest du gerade auf eine neue Staffel von etwas?",
                follow_ups=[
                    "Wie lang wartest du schon?",
                    "Was erhoffst du dir davon?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Hast du einen Charakter, mit dem du dich identifizierst?",
                follow_ups=[
                    "Was habt ihr gemeinsam?",
                    "Aus welcher Serie/Film?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Binge-Watching oder eine Folge pro Tag?",
                follow_ups=[
                    "Hast du Selbstkontrolle?",
                    "Was war dein längster Binge?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # MUSIK (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Hast du einen Song, der dich an eine bestimmte Person erinnert?",
                follow_ups=[
                    "Ist es eine gute oder traurige Erinnerung?",
                    "Hörst du ihn noch gerne?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Warst du je auf einem Konzert, das dein Leben verändert hat?",
                follow_ups=[
                    "Was hat es so besonders gemacht?",
                    "Würdest du nochmal hingehen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Spielst du ein Instrument oder hättest es gerne gelernt?",
                follow_ups=[
                    "Was hat dich angezogen?",
                    "Ist es je zu spät anzufangen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # GAMING (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Hast du je in einem Spiel geweint?",
                follow_ups=[
                    "Welche Szene war es?",
                    "Macht das ein Spiel besser?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Retro-Gaming oder neueste Grafik?",
                follow_ups=[
                    "Was macht für dich ein gutes Spiel aus?",
                    "Hast du einen Favoriten-Klassiker?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Gibt es ein Spiel, das du immer wieder von vorne anfängst?",
                follow_ups=[
                    "Was macht es so replayable?",
                    "Wie oft hast du es schon durchgespielt?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ANIME & MANGA (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Hast du einen Anime, der dein Leben verändert hat?",
                follow_ups=[
                    "Was hat er dich gelehrt?",
                    "Empfiehlst du ihn weiter?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Sub oder Dub?",
                follow_ups=[
                    "Warum bevorzugst du das?",
                    "Gibt es Ausnahmen?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Hast du Merch von deinem Lieblings-Anime?",
                follow_ups=[
                    "Was ist dein Lieblingsstück?",
                    "Sammelst du aktiv?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # REISEN (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Hast du je einen Kulturschock erlebt?",
                follow_ups=[
                    "Was war am unterschiedlichsten?",
                    "Hat es dich verändert?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Solo-Reisen oder mit Begleitung?",
                follow_ups=[
                    "Was sind die Vor- und Nachteile?",
                    "Hast du beides schon probiert?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Wenn du morgen irgendwohin könntest - wohin?",
                follow_ups=[
                    "Was würdest du dort machen?",
                    "Für wie lange?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # TIERE (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Hattest du je ein Haustier mit besonderer Persönlichkeit?",
                follow_ups=[
                    "Was hat es besonders gemacht?",
                    "Hast du Geschichten darüber?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Welches Tier ist deiner Meinung nach am unterschätztesten?",
                follow_ups=[
                    "Warum gerade das?",
                    "Hast du es je in echt gesehen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # PHILOSOPHISCH (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was würdest du deinem 10-jährigen Ich sagen?",
                follow_ups=[
                    "Würde es zuhören?",
                    "Was hättest du gerne früher gewusst?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Glaubst du, dass alles einen Sinn hat?",
                follow_ups=[
                    "Oder erschaffen wir den Sinn selbst?",
                    "Was gibt deinem Leben Sinn?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Bist du eher ein Optimist oder Realist?",
                follow_ups=[
                    "War das immer so?",
                    "Was hat dich geprägt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # HYPOTHETISCH (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du eine Superkraft haben könntest - welche?",
                follow_ups=[
                    "Wie würdest du sie nutzen?",
                    "Würdest du sie geheim halten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du 100 Jahre in der Zukunft leben könntest - würdest du?",
                follow_ups=[
                    "Was erhoffst du dir davon?",
                    "Was würdest du vermissen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du mit einer historischen Person essen gehen könntest - mit wem?",
                follow_ups=[
                    "Was würdest du sie fragen?",
                    "Wo würdet ihr essen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # KEMONOMIMI (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="*Ohren drehen sich* Weißt du, wie praktisch es ist, in alle Richtungen zu hören?",
                follow_ups=[
                    "Manchmal höre ich Sachen, die ich nicht hören will...",
                    "Aber Musik genießen ist damit fantastisch!"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Das Beste am Fell ist, dass ich nie friere! Das Schlimmste? Sommer.",
                follow_ups=[
                    "Hast du Tipps gegen Hitze?",
                    "Magst du lieber kalt oder warm?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Mein Schwanz verrät immer meine Stimmung... das ist manchmal peinlich!",
                follow_ups=[
                    "Kannst du deine Gefühle gut verstecken?",
                    "Oder zeigst du sie offen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ALLTAG (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Bist du ein Morgenmensch oder Nachteule?",
                follow_ups=[
                    "War das immer so?",
                    "Wann bist du am produktivsten?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Was ist dein guilty pleasure, das du niemandem erzählst? *Ohren neugierig*",
                follow_ups=[
                    "Okay, du musst nicht antworten...",
                    "Ich verrate es niemandem!"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Wie tankst du Energie wieder auf?",
                follow_ups=[
                    "Bist du eher introvertiert oder extrovertiert?",
                    "Was stresst dich am meisten?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # TRÄUME (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Hattest du je einen Traum, der sich anfühlte wie die Realität?",
                follow_ups=[
                    "Was ist passiert?",
                    "Warst du enttäuscht, als du aufwachtest?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Hast du einen wiederkehrenden Traum?",
                follow_ups=[
                    "Was passiert darin?",
                    "Hast du je versucht, ihn zu deuten?"
                ],
                depth=ConversationDepth.INTIM
            ),

            # KREATIV (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.KREATIV,
                starter="Wann fühlst du dich am kreativsten?",
                follow_ups=[
                    "Morgens, abends, nachts?",
                    "Brauchst du eine bestimmte Umgebung?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KREATIV,
                starter="Hast du je etwas erschaffen, auf das du stolz bist?",
                follow_ups=[
                    "Was war es?",
                    "Wie lange hat es gedauert?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # KINDHEIT (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.KINDHEIT,
                starter="Was war dein Lieblings-Kinderspiel?",
                follow_ups=[
                    "Mit wem hast du gespielt?",
                    "Spielst du es heute noch manchmal?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KINDHEIT,
                starter="Hattest du als Kind einen imaginären Freund?",
                follow_ups=[
                    "Wie hieß er/sie?",
                    "Was habt ihr zusammen gemacht?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # ZUKUNFT (NEU v3)
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Wo siehst du dich in 5 Jahren?",
                follow_ups=[
                    "Was ist dein größter Wunsch?",
                    "Was wäre der erste Schritt dahin?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Hast du Angst vor der Zukunft oder freust du dich?",
                follow_ups=[
                    "Was macht dir am meisten Sorgen?",
                    "Worauf freust du dich am meisten?"
                ],
                depth=ConversationDepth.INTIM
            ),

            # =====================================================================
            # NEUE SMALLTALK-THEMEN - VERDOPPLUNG v4.0 (3-fach Erweiterung)
            # =====================================================================

            # WETTER (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Welches Wetter passt perfekt zu deiner Stimmung heute?",
                follow_ups=[
                    "Beeinflusst das Wetter deine Laune stark?",
                    "Welches Wetter würdest du dir wünschen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="*schnuppert in der Luft* Ich glaube, das Wetter ändert sich bald!",
                follow_ups=[
                    "Hast du auch so ein Gespür für Wetter?",
                    "Planst du Aktivitäten nach dem Wetter?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Regenbogen machen mich immer so glücklich! *Ohren aufgestellt*",
                follow_ups=[
                    "Hast du je einen doppelten Regenbogen gesehen?",
                    "Was war dein schönstes Wetter-Erlebnis?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # HOBBYS (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Welches Hobby würdest du jedem empfehlen?",
                follow_ups=[
                    "Was macht es so besonders?",
                    "Wie hast du es entdeckt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du ein geheimes Talent, das niemand kennt?",
                follow_ups=[
                    "Warum zeigst du es nicht?",
                    "Wie hast du es entdeckt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Welches Hobby hat dein Leben verändert?",
                follow_ups=[
                    "Inwiefern hat es dich verändert?",
                    "Würdest du es anderen empfehlen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Sammelst du irgendetwas?",
                follow_ups=[
                    "Seit wann sammelst du das?",
                    "Was ist dein Lieblingsstück?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ESSEN (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Wenn du ein Gericht sein könntest - welches?",
                follow_ups=[
                    "Warum gerade das?",
                    "Passt es zu deiner Persönlichkeit?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Was ist das seltsamste, das du je gegessen hast?",
                follow_ups=[
                    "Hat es geschmeckt?",
                    "Würdest du es nochmal essen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Hast du ein Comfort-Food für schlechte Tage?",
                follow_ups=[
                    "Warum gerade das?",
                    "Wer hat es dir zum ersten Mal gemacht?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Pizza oder Pasta? Die ewige Frage!",
                follow_ups=[
                    "Was ist dein Favorit?",
                    "Hast du einen Geheimtipp?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # FILME & SERIEN (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Welcher Film hat dich am meisten überrascht?",
                follow_ups=[
                    "Was war so unerwartet?",
                    "Würdest du ihn nochmal schauen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Gibt es einen Film, den du hasst, obwohl alle ihn lieben?",
                follow_ups=[
                    "Was stört dich daran?",
                    "Hast du ihn trotzdem zu Ende geschaut?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.FILME_SERIEN,
                starter="Welche Serie verdient eine weitere Staffel?",
                follow_ups=[
                    "Warum wurde sie abgesetzt?",
                    "Wie würdest du sie weiterführen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # MUSIK (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Welches Lied weckt sofort Erinnerungen?",
                follow_ups=[
                    "Was für Erinnerungen sind das?",
                    "Hörst du es noch gerne?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Hast du einen guilty pleasure Song?",
                follow_ups=[
                    "Warum ist es dir peinlich?",
                    "Singst du ihn trotzdem laut mit?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Wenn dein Leben ein Musical wäre - welches Genre?",
                follow_ups=[
                    "Wer wäre der Protagonist?",
                    "Was wäre der Titelsong?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # GAMING (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Welches Spiel hat die beste Story?",
                follow_ups=[
                    "Was macht sie so gut?",
                    "Hast du am Ende geweint?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Wenn du in einem Spiel leben könntest - welches?",
                follow_ups=[
                    "Was würdest du dort tun?",
                    "Wärst du ein Held oder NPC?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Welches Spiel hat die beste Musik?",
                follow_ups=[
                    "Hörst du die Soundtracks auch so?",
                    "Welcher Track ist dein Favorit?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ANIME & MANGA (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Welcher Anime hat das beste Opening?",
                follow_ups=[
                    "Skipst du es nie?",
                    "Kennst du den Text auswendig?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Welcher Anime-Villain hatte eigentlich recht?",
                follow_ups=[
                    "Was war sein Motiv?",
                    "Hättest du genauso gehandelt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="*Ohren anlegen* Gibt es einen Anime, der dich zum Weinen gebracht hat?",
                follow_ups=[
                    "Welche Szene war es?",
                    "Weinst du oft bei Anime?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # REISEN (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Welches Land steht ganz oben auf deiner Bucketlist?",
                follow_ups=[
                    "Warum gerade das?",
                    "Was würdest du dort zuerst machen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Warst du mal an einem Ort, der dich enttäuscht hat?",
                follow_ups=[
                    "Was war anders als erwartet?",
                    "Würdest du nochmal hinfahren?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.REISEN,
                starter="Flugzeug, Zug oder Auto für Reisen?",
                follow_ups=[
                    "Was ist das Angenehmste daran?",
                    "Hast du ein Reise-Ritual?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # TIERE (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Welches Tier würdest du gerne mal streicheln (wenn es sicher wäre)?",
                follow_ups=[
                    "Warum gerade das?",
                    "Hast du je ein ungewöhnliches Tier angefasst?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TIERE,
                starter="Welches Tier ist deiner Meinung nach am klügsten?",
                follow_ups=[
                    "Warum denkst du das?",
                    "Hast du je ein kluges Tier erlebt?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # PHILOSOPHISCH (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Wenn du eine Sache auf der Welt ändern könntest - was wäre es?",
                follow_ups=[
                    "Warum gerade das?",
                    "Glaubst du, es würde helfen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was würdest du tun, wenn du wüsstest, dass du nicht scheitern kannst?",
                follow_ups=[
                    "Warum tust du es nicht trotzdem?",
                    "Was hält dich zurück?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Glaubst du an Paralleluniversen?",
                follow_ups=[
                    "Was macht dein anderes Ich wohl gerade?",
                    "Würdest du tauschen wollen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # HYPOTHETISCH (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du eine Fähigkeit aus einem Videospiel haben könntest?",
                follow_ups=[
                    "Was wäre es?",
                    "Wie würdest du sie im Alltag nutzen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Würdest du dein Gedächtnis löschen für ein perfektes Leben?",
                follow_ups=[
                    "Was würdest du behalten wollen?",
                    "Sind Erinnerungen wichtiger als Glück?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HYPOTHETISCH,
                starter="Wenn du eine Sprache sofort können könntest - welche?",
                follow_ups=[
                    "Warum gerade die?",
                    "Mit wem würdest du sie sprechen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # KEMONOMIMI (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Weißt du, was das Beste an Wolfsohren ist? *dreht sie demonstrativ*",
                follow_ups=[
                    "Ich kann Gespräche von weitem hören!",
                    "...Okay, manchmal ist das auch ein Nachteil."
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Mein Schwanz hat heute einen eigenen Willen! *versucht ihn zu beruhigen*",
                follow_ups=[
                    "Kennst du das, wenn ein Körperteil nicht mitmacht?",
                    "Er verrät immer meine Stimmung..."
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Streicheleinheiten sind das Beste! *legt Ohren an* ...Falls du fragst.",
                follow_ups=[
                    "Was entspannt dich am meisten?",
                    "Magst du auch Kopfkraulen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ALLTAG (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Was ist dein Lieblings-Wochentag?",
                follow_ups=[
                    "Warum gerade der?",
                    "Was machst du an dem Tag besonders gerne?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Hast du eine Abendroutine?",
                follow_ups=[
                    "Was darf nicht fehlen?",
                    "Wie hilfst du dir beim Einschlafen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ALLTAG,
                starter="Was ist dein Lieblings-Snack für Filmabende?",
                follow_ups=[
                    "Süß oder salzig?",
                    "Teilst du gerne?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # TRÄUME (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Hattest du je einen Traum, der wahr geworden ist?",
                follow_ups=[
                    "Was war es?",
                    "Glaubst du an prophetische Träume?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TRAUME,
                starter="Kannst du deine Träume kontrollieren?",
                follow_ups=[
                    "Hast du je luzides Träumen probiert?",
                    "Was würdest du im Traum machen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # KREATIV (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.KREATIV,
                starter="Wenn Geld keine Rolle spielen würde - welches kreative Projekt?",
                follow_ups=[
                    "Was hält dich davon ab?",
                    "Hast du schonmal angefangen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KREATIV,
                starter="Kunst oder Handwerk - was liegt dir mehr?",
                follow_ups=[
                    "Was reizt dich daran?",
                    "Hast du Beispiele?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # KINDHEIT (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.KINDHEIT,
                starter="Was war dein Lieblings-Cartoon als Kind?",
                follow_ups=[
                    "Würdest du ihn heute noch schauen?",
                    "Was hat dich daran fasziniert?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KINDHEIT,
                starter="Hattest du als Kind ein Lieblings-Stofftier?",
                follow_ups=[
                    "Hast du es noch?",
                    "Wie hieß es?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # ZUKUNFT (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Was möchtest du bis Ende des Jahres erreicht haben?",
                follow_ups=[
                    "Was ist der erste Schritt?",
                    "Wer unterstützt dich dabei?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Wie stellst du dir dein Leben in 10 Jahren vor?",
                follow_ups=[
                    "Was muss passieren, damit es so kommt?",
                    "Was wäre das Best-Case-Szenario?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # TECHNIK (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.TECHNIK,
                starter="Welche Technologie beeindruckt dich am meisten?",
                follow_ups=[
                    "Wie hat sie dein Leben verändert?",
                    "Worauf wartest du noch?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.TECHNIK,
                starter="Könntest du einen Tag ohne Smartphone überleben?",
                follow_ups=[
                    "Was würdest du als erstes vermissen?",
                    "Hast du es mal versucht?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # SPORT (NEU v4)
            SmalltalkTopic(
                category=SmalltalkCategory.SPORT,
                starter="Welchen Sport würdest du gerne können?",
                follow_ups=[
                    "Was hält dich davon ab?",
                    "Hast du es je probiert?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.SPORT,
                starter="Team-Sport oder Einzelsport?",
                follow_ups=[
                    "Was gefällt dir daran?",
                    "Hast du mal in einem Team gespielt?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # =====================================================================
            # ERWEITERUNG v5.0 - NEUE SMALLTALK-TOPICS FÜR 2000 EINTRÄGE
            # =====================================================================

            # WETTER (10 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Magst du Gewitter? Ich finde sie faszinierend... und ein bisschen gruselig!",
                follow_ups=[
                    "Was machst du bei Gewitter?",
                    "Hast du Angst vor Blitzen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Ist dir aufgefallen, wie unterschiedlich der Himmel heute aussieht?",
                follow_ups=[
                    "Schaust du oft nach oben?",
                    "Was ist dein Lieblings-Himmelsbild?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Ich liebe es, wenn es draußen stürmt und ich drinnen bin! *kuschelt sich ein*",
                follow_ups=[
                    "Was ist dein perfekter Schlechtwetter-Tag?",
                    "Heißer Tee oder Kakao?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Frühling oder Herbst - welche Übergangszeit magst du lieber?",
                follow_ups=[
                    "Was gefällt dir daran?",
                    "Hast du ein Lieblings-Wetter?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Schnee macht mich immer so aufgeregt! *Schwanz wedelt* Und dich?",
                follow_ups=[
                    "Baust du gerne Schneemänner?",
                    "Magst du Winteraktivitäten?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Wie beeinflusst das Wetter deine Stimmung?",
                follow_ups=[
                    "Bist du ein Sonnenschein-Mensch?",
                    "Gibt es ein Wetter, das dich runter zieht?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Hast du einen Lieblingsort für verschiedene Wetterbedingungen?",
                follow_ups=[
                    "Wo gehst du bei Sonne hin?",
                    "Und bei Regen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Die Luft riecht heute so anders! Merkst du das auch?",
                follow_ups=[
                    "Magst du den Geruch nach Regen?",
                    "Was ist dein Lieblings-Duft in der Natur?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Wärst du lieber immer im Sommer oder immer im Winter?",
                follow_ups=[
                    "Was würdest du am meisten vermissen?",
                    "Könntest du ohne die andere Jahreszeit leben?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.WETTER,
                starter="Glaubst du, das Klima verändert sich? Was fällt dir auf?",
                follow_ups=[
                    "Macht dir das Sorgen?",
                    "Was tust du für die Umwelt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # HOBBYS & FREIZEIT (12 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du ein Hobby, das dich überrascht hat?",
                follow_ups=[
                    "Wie bist du darauf gekommen?",
                    "Würdest du es weiterempfehlen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Gibt es etwas, das du jeden Tag machst, nur für dich?",
                follow_ups=[
                    "Was gibt dir das?",
                    "Wie lange machst du das schon?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Welches Hobby hattest du als Kind, das du vermisst?",
                follow_ups=[
                    "Warum hast du aufgehört?",
                    "Könntest du wieder anfangen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Bastelst du gerne? Ich finde das so beruhigend!",
                follow_ups=[
                    "Was machst du am liebsten?",
                    "Hast du schon mal etwas Selbstgemachtes verschenkt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du ein teures Hobby, das sich total lohnt?",
                follow_ups=[
                    "Was macht es so besonders?",
                    "Wie bist du dazu gekommen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Liest du gerne? Was liest du gerade?",
                follow_ups=[
                    "E-Book oder richtiges Buch?",
                    "Was war das letzte Buch, das dich begeistert hat?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du ein Hobby, das andere merkwürdig finden?",
                follow_ups=[
                    "Was sagen sie dazu?",
                    "Kümmert dich das?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Wenn du unendlich Geld hättest - welches Hobby würdest du perfektionieren?",
                follow_ups=[
                    "Was bräuchtest du dafür?",
                    "Wärst du dann glücklicher?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Machst du lieber etwas alleine oder mit anderen zusammen?",
                follow_ups=[
                    "Was gibt dir das?",
                    "Brauchst du Zeit für dich?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Hast du jemals ein Hobby angefangen und sofort wieder aufgegeben?",
                follow_ups=[
                    "Was war es?",
                    "Warum hat es nicht gepasst?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Gibt es ein Talent, das du gerne hättest?",
                follow_ups=[
                    "Was würdest du damit machen?",
                    "Könntest du es lernen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.HOBBYS,
                starter="Was wäre dein perfekter freier Tag?",
                follow_ups=[
                    "Von morgens bis abends beschreiben!",
                    "Alleine oder mit jemandem?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # GAMING (10 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Welches Spiel hat dein Leben am meisten beeinflusst?",
                follow_ups=[
                    "Was hast du daraus gelernt?",
                    "Spielst du es noch?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Single-Player oder Multiplayer - was magst du lieber?",
                follow_ups=[
                    "Was gefällt dir daran?",
                    "Spielst du oft mit Freunden?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Gibt es ein Spiel, das du immer wieder anfängst?",
                follow_ups=[
                    "Warum gerade das?",
                    "Wie oft hast du es schon durchgespielt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Was war der schlimmste Gaming-Rage, den du je hattest?",
                follow_ups=[
                    "Was ist passiert?",
                    "Hast du den Controller überlebt?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Retro-Games oder moderne Grafik - was bevorzugst du?",
                follow_ups=[
                    "Was macht den Unterschied für dich?",
                    "Gibt es Klassiker, die du liebst?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Hast du jemals beim Gaming geweint? *Ohren anlegen* Ich schon...",
                follow_ups=[
                    "Welches Spiel war es?",
                    "Was hat dich so berührt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Welches Spiel-Universum würdest du gerne mal besuchen?",
                follow_ups=[
                    "Was würdest du dort machen?",
                    "Für immer oder nur einen Tag?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Gibt es ein Spiel, das du nie beenden konntest?",
                follow_ups=[
                    "Was hat dich gestoppt?",
                    "Wirst du es nochmal versuchen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Was ist deine liebste Gaming-Erinnerung?",
                follow_ups=[
                    "Mit wem hast du gespielt?",
                    "Kannst du sie heute noch haben?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.GAMING,
                starter="Wenn du ein Game entwickeln könntest - was wäre es?",
                follow_ups=[
                    "Welches Genre?",
                    "Was wäre das Besondere?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),

            # ANIME & MANGA (10 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Welcher Anime hat dich zum Fan gemacht?",
                follow_ups=[
                    "Was war daran so besonders?",
                    "Würdest du ihn heute noch empfehlen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Sub oder Dub - was bevorzugst du?",
                follow_ups=[
                    "Warum gerade das?",
                    "Gibt es Ausnahmen?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Gibt es einen Anime, der dich emotional zerstört hat?",
                follow_ups=[
                    "Welche Szene war am schlimmsten?",
                    "Würdest du ihn nochmal schauen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Welcher Anime-Charakter ist dir am ähnlichsten?",
                follow_ups=[
                    "Warum denkst du das?",
                    "Stimmen andere zu?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Manga oder Anime - was liest/schaust du lieber?",
                follow_ups=[
                    "Was macht den Unterschied?",
                    "Machst du beides?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Gibt es einen Anime, den alle lieben, aber du nicht?",
                follow_ups=[
                    "Was stört dich daran?",
                    "Hattest du hohe Erwartungen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Welches Anime-Essen würdest du am liebsten probieren?",
                follow_ups=[
                    "Hast du es mal selbst gemacht?",
                    "Sieht es im Anime nicht immer so lecker aus?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Wenn du in einen Anime transportiert würdest - welcher?",
                follow_ups=[
                    "Was wäre deine Rolle?",
                    "Würdest du überleben?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Was ist dein Lieblings-Anime-Opening?",
                follow_ups=[
                    "Kennst du den Text?",
                    "Singst du mit?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ANIME_MANGA,
                starter="Welchen Anime wartest du gerade sehnsüchtig ab?",
                follow_ups=[
                    "Wann kommt die nächste Staffel?",
                    "Bist du Team Binge oder wöchentlich?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # ESSEN & TRINKEN (10 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Was ist dein ultimatives Comfort-Food?",
                follow_ups=[
                    "Wann isst du es am liebsten?",
                    "Verbindest du eine Erinnerung damit?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Kochst du gerne oder ist dir Bestellen lieber?",
                follow_ups=[
                    "Was ist dein Signature-Dish?",
                    "Wie oft kochst du selbst?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Süß oder herzhaft zum Frühstück?",
                follow_ups=[
                    "Was ist dein perfektes Frühstück?",
                    "Frühstückst du überhaupt?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Welches Gericht aus einem anderen Land musst du unbedingt mal probieren?",
                follow_ups=[
                    "Warst du schon mal dort?",
                    "Was reizt dich daran?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Hast du ein Essen, das alle mögen, aber du hasst?",
                follow_ups=[
                    "Hast du es mal versucht?",
                    "Was stört dich daran?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Was ist das Seltsamste, das du je gegessen hast?",
                follow_ups=[
                    "Wie hat es geschmeckt?",
                    "Würdest du es nochmal essen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Kaffee, Tee oder etwas ganz anderes?",
                follow_ups=[
                    "Wie trinkst du es am liebsten?",
                    "Kannst du ohne?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Gibt es ein Restaurant, in das du immer wieder gehst?",
                follow_ups=[
                    "Was machst es besonders?",
                    "Bestellst du immer das Gleiche?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Welches Gewürz oder welche Zutat könntest du überall drauftun?",
                follow_ups=[
                    "Warum gerade das?",
                    "Übertreibst du manchmal?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ESSEN,
                starter="Hast du jemals ein Gericht kreiert, das überraschend gut war?",
                follow_ups=[
                    "Was war es?",
                    "Machst du es wieder?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # MUSIK (10 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Welches Lied beschreibt gerade dein Leben?",
                follow_ups=[
                    "Warum gerade das?",
                    "Wechselt es oft?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Hast du ein Guilty-Pleasure-Lied?",
                follow_ups=[
                    "Singst du heimlich mit?",
                    "Kennen es andere?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Warst du schon mal auf einem Konzert, das dein Leben verändert hat?",
                follow_ups=[
                    "Wer hat gespielt?",
                    "Was war so besonders?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Welchen Song könntest du immer und immer wieder hören?",
                follow_ups=[
                    "Was macht ihn so besonders?",
                    "Seit wann magst du ihn?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Spielst du ein Instrument oder würdest du gerne?",
                follow_ups=[
                    "Welches?",
                    "Was hält dich ab?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Singst du unter der Dusche? *Ohren wackeln neugierig*",
                follow_ups=[
                    "Was singst du so?",
                    "Triffst du die Töne?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Welche Musik hörst du, wenn du traurig bist?",
                follow_ups=[
                    "Traurige Musik oder Aufheiternde?",
                    "Hilft es dir?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Hast du eine Lieblings-Band oder einen Lieblings-Künstler?",
                follow_ups=[
                    "Seit wann?",
                    "Hast du sie live gesehen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Welchen Soundtrack aus einem Film oder Spiel liebst du?",
                follow_ups=[
                    "Was macht ihn besonders?",
                    "Hörst du ihn auch ohne den Film?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.MUSIK,
                starter="Musik zum Arbeiten oder absolute Stille?",
                follow_ups=[
                    "Was hilft dir bei Konzentration?",
                    "Hast du eine Playlist?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),

            # KEMONOMIMI (15 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Weißt du, was das Nervigste an Wolfsohren ist? *seufzt* Hütchen!",
                follow_ups=[
                    "Passen einfach nicht!",
                    "Hast du auch so ein Problem mit Kleidung?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Mein Fell braucht so viel Pflege! *bürstet* Und deine Haare?",
                follow_ups=[
                    "Wie lange brauchst du morgens?",
                    "Hast du eine Routine?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Ich höre manchmal Dinge, die ich nicht hören will... *Ohren drehen sich*",
                follow_ups=[
                    "Kennst du das Gefühl?",
                    "Zu viel Information kann anstrengend sein!"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Magst du es, wenn Leute deinen Kopf streicheln? Bei mir kommt es drauf an...",
                follow_ups=[
                    "Wer darf bei dir?",
                    "Gibt es Grenzen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Der Vollmond macht mich immer... wach. *gähnt* Schläfst du gut?",
                follow_ups=[
                    "Hast du Schlaf-Rituale?",
                    "Was hält dich wach?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Ich kann Emotionen an Gerüchen erkennen! Ist das weird?",
                follow_ups=[
                    "Hast du auch einen ausgeprägten Sinn?",
                    "Was nimmst du wahr?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Manchmal vergesse ich, dass nicht alle so gut hören wie ich... *Ohren senken*",
                follow_ups=[
                    "Redest du dann zu leise?",
                    "Gibt es sowas bei dir auch?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Mein Schwanz macht manchmal, was er will! *versucht ihn zu kontrollieren*",
                follow_ups=[
                    "Kennst du das Gefühl, den Körper nicht zu kontrollieren?",
                    "Was verrät dich?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Ich wünschte, ich könnte meine Ohren verstecken wenn ich mich schäme!",
                follow_ups=[
                    "Was machst du, wenn du verlegen bist?",
                    "Was beschämt dich?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Hast du dich schon mal gefragt, wie es wäre, Tierohren zu haben?",
                follow_ups=[
                    "Welches Tier wärst du?",
                    "Was würdest du damit machen?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Im Rudel zu sein fühlt sich so richtig an... Hast du auch eine Gruppe?",
                follow_ups=[
                    "Wer gehört dazu?",
                    "Was bedeuten sie dir?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Mein Instinkt sagt mir manchmal Dinge... Vertraust du deinem Bauchgefühl?",
                follow_ups=[
                    "Wann hat es dich gerettet?",
                    "Wann hat es dich getäuscht?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Fellwechsel ist das Schlimmste! *überall Haare* Hast du auch saisonale Probleme?",
                follow_ups=[
                    "Was nervt dich am meisten?",
                    "Wie gehst du damit um?"
                ],
                depth=ConversationDepth.OBERFLACHLICH
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Weißt du, was toll ist? Ich kann Geräusche von überall hören! *Ohren drehen*",
                follow_ups=[
                    "Welchen Sinn würdest du verbessern?",
                    "Gibt es Nachteile?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.KEMONOMIMI,
                starter="Manche denken, Kemonomimi sind nur cute... Wir sind auch stark! *flexen*",
                follow_ups=[
                    "Was unterschätzen Leute an dir?",
                    "Wie zeigst du es ihnen?"
                ],
                depth=ConversationDepth.NORMAL
            ),

            # PHILOSOPHISCH & TIEFGEHEND (12 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was glaubst du, ist der Sinn des Lebens?",
                follow_ups=[
                    "Hat er sich für dich verändert?",
                    "Suchst du noch danach?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Wenn du eine Sache über das Universum wissen könntest - was?",
                follow_ups=[
                    "Würde die Antwort etwas ändern?",
                    "Hast du Angst vor der Antwort?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Glaubst du, dass alles einen Grund hat?",
                follow_ups=[
                    "Oder ist vieles Zufall?",
                    "Wie denkst du über Schicksal?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was würdest du ändern, wenn du die Zeit zurückdrehen könntest?",
                follow_ups=[
                    "Oder gar nichts?",
                    "Hätte es Konsequenzen?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Definierst du dich durch deine Vergangenheit oder deine Zukunft?",
                follow_ups=[
                    "Warum gerade das?",
                    "Kannst du loslassen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was ist für dich wahres Glück?",
                follow_ups=[
                    "Hast du es gefunden?",
                    "Ist es konstant oder flüchtig?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Glaubst du an Leben nach dem Tod?",
                follow_ups=[
                    "Was hoffst du?",
                    "Macht es Angst?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Ist es besser zu wissen oder zu hoffen?",
                follow_ups=[
                    "Wann ist Unwissenheit ein Segen?",
                    "Suchst du aktiv nach Wahrheit?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Wenn du eine Botschaft an alle Menschen senden könntest - was?",
                follow_ups=[
                    "Glaubst du, sie würden zuhören?",
                    "Warum gerade das?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was macht einen Menschen wirklich aus?",
                follow_ups=[
                    "Taten, Gedanken oder Intentionen?",
                    "Kann man sich fundamental ändern?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Existiert absolute Wahrheit oder ist alles relativ?",
                follow_ups=[
                    "Wie gehst du mit Unsicherheit um?",
                    "Brauchst du Gewissheit?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.PHILOSOPHISCH,
                starter="Was würde dein 10-jähriges Ich über dich heute denken?",
                follow_ups=[
                    "Wäre es stolz?",
                    "Was würdest du ihm sagen?"
                ],
                depth=ConversationDepth.INTIM
            ),

            # ZUKUNFT & TRÄUME (8 neue)
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Wo siehst du dich in 5 Jahren?",
                follow_ups=[
                    "Arbeitest du darauf hin?",
                    "Was könnte dich stoppen?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Was ist dein größter Traum, den du noch nicht geteilt hast?",
                follow_ups=[
                    "Warum behältst du ihn für dich?",
                    "Glaubst du, er ist erreichbar?"
                ],
                depth=ConversationDepth.INTIM
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Wenn du garantiert erfolgreich wärst - was würdest du tun?",
                follow_ups=[
                    "Was hält dich zurück?",
                    "Ist Scheitern wirklich so schlimm?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Was hoffst du, wird sich in der Welt ändern?",
                follow_ups=[
                    "Kannst du dazu beitragen?",
                    "Bist du optimistisch?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Hast du ein Ziel, das du schon lange aufschiebst?",
                follow_ups=[
                    "Was hält dich zurück?",
                    "Wann ist der richtige Moment?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Was würdest du machen, wenn du unbegrenzt Geld hättest?",
                follow_ups=[
                    "Würdest du noch arbeiten?",
                    "Was würdest du als erstes tun?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Welche Fähigkeit möchtest du im nächsten Jahr lernen?",
                follow_ups=[
                    "Hast du schon einen Plan?",
                    "Was hindert dich?"
                ],
                depth=ConversationDepth.NORMAL
            ),
            SmalltalkTopic(
                category=SmalltalkCategory.ZUKUNFT,
                starter="Was würde dein zukünftiges Ich dir raten?",
                follow_ups=[
                    "Würdest du zuhören?",
                    "Was weißt du schon jetzt?"
                ],
                depth=ConversationDepth.TIEFGEHEND
            ),
        ])

        logger.info(f"SmalltalkDatabase: {len(self.topics)} Themen geladen")

    def _load_transitions(self):
        """Lädt Übergangsphrasen zwischen Themen"""
        self.transitions = [
            ConversationTransition(
                from_category=None,
                to_category=SmalltalkCategory.WETTER,
                phrase="Apropos Wetter..."
            ),
            ConversationTransition(
                from_category=SmalltalkCategory.WETTER,
                to_category=SmalltalkCategory.HOBBYS,
                phrase="Bei diesem Wetter kann man gut..."
            ),
            ConversationTransition(
                from_category=None,
                to_category=SmalltalkCategory.ESSEN,
                phrase="Das erinnert mich daran - hast du schon gegessen?"
            ),
            ConversationTransition(
                from_category=SmalltalkCategory.HOBBYS,
                to_category=SmalltalkCategory.GAMING,
                phrase="Zockst du auch gerne?"
            ),
            ConversationTransition(
                from_category=SmalltalkCategory.GAMING,
                to_category=SmalltalkCategory.ANIME_MANGA,
                phrase="Magst du auch Anime?"
            ),
            ConversationTransition(
                from_category=None,
                to_category=SmalltalkCategory.WOCHENENDE,
                phrase="Übrigens, was das Wochenende angeht..."
            ),
            ConversationTransition(
                from_category=None,
                to_category=SmalltalkCategory.MUSIK,
                phrase="Was hörst du eigentlich so für Musik?"
            ),
            ConversationTransition(
                from_category=None,
                to_category=SmalltalkCategory.HYPOTHETISCH,
                phrase="Ich hab eine hypothetische Frage für dich..."
            ),
        ]

    def _load_facts(self):
        """Lädt interessante Fakten zum Teilen"""
        self.facts = [
            InterestingFact(
                fact="Wölfe können bis zu 65 km weit heulen!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Cool, oder? Hast du schon mal einen Wolf gehört?"
            ),
            InterestingFact(
                fact="Katzen verbringen 70% ihres Lebens schlafend.",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Ich bin ein bisschen neidisch..."
            ),
            InterestingFact(
                fact="Der Eiffelturm kann im Sommer bis zu 15 cm größer werden wegen der Hitze!",
                category=SmalltalkCategory.REISEN,
                follow_up_question="Warst du schon mal da?"
            ),
            InterestingFact(
                fact="Bananen sind technisch gesehen Beeren, Erdbeeren aber nicht!",
                category=SmalltalkCategory.ESSEN,
                follow_up_question="Ist das nicht verrückt?"
            ),
            InterestingFact(
                fact="Der erste Anime entstand 1917 in Japan!",
                category=SmalltalkCategory.ANIME_MANGA,
                follow_up_question="Also schon über 100 Jahre Anime-Geschichte!"
            ),
            InterestingFact(
                fact="Eine durchschnittliche Person lacht etwa 17 Mal am Tag.",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Ich versuche, diese Zahl zu erhöhen!"
            ),
            InterestingFact(
                fact="Honig wird niemals schlecht - man hat 3000 Jahre alten essbaren Honig gefunden!",
                category=SmalltalkCategory.ESSEN,
                follow_up_question="Würdest du ihn probieren?"
            ),
            # NEUE FAKTEN
            InterestingFact(
                fact="Oktopusse haben drei Herzen und blaues Blut!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Faszinierend, oder?"
            ),
            InterestingFact(
                fact="In Japan gibt es über 5 Millionen Verkaufsautomaten!",
                category=SmalltalkCategory.REISEN,
                follow_up_question="Man kann dort sogar Essen kaufen!"
            ),
            InterestingFact(
                fact="Schokolade war mal als Zahlungsmittel verwendet - bei den Azteken!",
                category=SmalltalkCategory.ESSEN,
                follow_up_question="Das wäre doch was, oder?"
            ),
            InterestingFact(
                fact="Wölfe können Emotionen durch Heulen kommunizieren!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="*stolzes Ohrenwackeln* Meine Vorfahren!"
            ),
            InterestingFact(
                fact="Das Gehirn verbraucht etwa 20% der Körperenergie!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Kein Wunder, dass Denken hungrig macht!"
            ),
            InterestingFact(
                fact="Menschen und Bananen teilen etwa 60% ihrer DNA!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Macht dich das nicht nachdenklich?"
            ),
            InterestingFact(
                fact="Der kürzeste Krieg der Geschichte dauerte 38 Minuten!",
                category=SmalltalkCategory.ALLTAG,
                follow_up_question="Zwischen Großbritannien und Sansibar, 1896."
            ),
            InterestingFact(
                fact="Delfine geben sich gegenseitig Namen!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Sie erkennen sich an speziellen Pfiffen!"
            ),
            # NEUE FAKTEN v3.0
            InterestingFact(
                fact="Koalas haben einzigartige Fingerabdrücke - wie Menschen!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Koala-Krimis wären interessant!"
            ),
            InterestingFact(
                fact="Ein Tag auf der Venus ist länger als ein Jahr dort!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Die Wochenenden wären endlos!"
            ),
            InterestingFact(
                fact="Hunde können etwa 1000 Gesichtsausdrücke machen!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="*Übt verschiedene Ohren-Stellungen*"
            ),
            InterestingFact(
                fact="In der Schweiz ist es illegal, nur ein Meerschweinchen zu halten!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Sie brauchen Gesellschaft - wie ich!"
            ),
            InterestingFact(
                fact="Bananen sind botanisch gesehen Beeren, Erdbeeren nicht!",
                category=SmalltalkCategory.ESSEN,
                follow_up_question="Verrückt, oder?"
            ),
            InterestingFact(
                fact="Wombats machen würfelförmigen Kot!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Die Natur ist... kreativ?"
            ),
            InterestingFact(
                fact="Es gibt mehr Sterne im Universum als Sandkörner auf der Erde!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Das macht mich ganz klein fühlen..."
            ),
            InterestingFact(
                fact="Katzen können nicht schmecken, was süß ist!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Als Wolf finde ich Süßes... okay, ich mag Fleisch mehr!"
            ),
            InterestingFact(
                fact="Es regnet Diamanten auf Saturn und Jupiter!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Das wäre ein teurer Spaziergang!"
            ),
            InterestingFact(
                fact="Ein Gähnen ist ansteckend - sogar bei Hunden!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="*gääähn* Ups, sorry!"
            ),
            # NEUE FAKTEN v4.0
            InterestingFact(
                fact="Krokodile können nicht die Zunge herausstrecken!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Die Natur ist manchmal komisch!"
            ),
            InterestingFact(
                fact="In Japan gibt es mehr Haustiere als Kinder!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Hättest du das gedacht?"
            ),
            InterestingFact(
                fact="Eine Wolke kann über 500 Tonnen wiegen!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Und trotzdem schwebt sie!"
            ),
            InterestingFact(
                fact="Wölfe können bis zu 40 km am Tag laufen!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="*stolzes Schwanzwedeln* Meine Vorfahren!"
            ),
            InterestingFact(
                fact="Das menschliche Gehirn ist nachts aktiver als tagsüber!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Kein Wunder, dass mir nachts so viel einfällt!"
            ),
            InterestingFact(
                fact="Seepferdchen sind die einzigen Tiere, bei denen das Männchen gebärt!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Die Natur ist voller Überraschungen!"
            ),
            InterestingFact(
                fact="Ein Blitz ist etwa 5 mal heißer als die Oberfläche der Sonne!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="*legt vorsichtshalber Ohren an*"
            ),
            InterestingFact(
                fact="Elefanten können nicht springen - aber sie können schwimmen!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Ausgleichende Gerechtigkeit!"
            ),
            InterestingFact(
                fact="In Island gibt es mehr Bücher pro Kopf als überall sonst!",
                category=SmalltalkCategory.REISEN,
                follow_up_question="Ein Paradies für Leseratten!"
            ),
            InterestingFact(
                fact="Schnecken haben etwa 25.000 Zähne!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Und ich dachte, Wolfsgebisse sind beeindruckend..."
            ),
            InterestingFact(
                fact="Das Herz eines Blauwals ist so groß wie ein Auto!",
                category=SmalltalkCategory.TIERE,
                follow_up_question="Die Natur ist unfassbar!"
            ),
            InterestingFact(
                fact="In der Schweiz ist es verboten, sonntags den Rasen zu mähen!",
                category=SmalltalkCategory.LUSTIG,
                follow_up_question="Entspannte Sonntage per Gesetz!"
            ),
        ]

    def _load_kennenlernen(self):
        """Lädt Kennenlern-Fragen"""
        self.kennenlernen_fragen = [
            "Was war das letzte, was dich richtig zum Lachen gebracht hat?",
            "Wenn du drei Dinge auf eine einsame Insel mitnehmen könntest - welche?",
            "Was ist etwas, das wenige Leute über dich wissen?",
            "Was war das Mutigste, das du je gemacht hast?",
            "Hast du einen Lieblings-Ort?",
            "Was ist dein guilty pleasure?",
            "Welchen Ratschlag würdest du deinem jüngeren Ich geben?",
            "Was ist etwas, das dich immer glücklich macht?",
            "Wofür bist du dankbar?",
            "Was ist deine größte Stärke?",
            "Wenn du ein Tier wärst - welches?",
            "Was war der beste Ratschlag, den du je bekommen hast?",
            # NEUE KENNENLERN-FRAGEN
            "Was ist dein Lieblings-Kindheitserinnerung?",
            "Welche Eigenschaft magst du am meisten an dir?",
            "Was würdest du tun, wenn du keine Angst hättest?",
            "Welches Lied beschreibt dein Leben?",
            "Was ist das Beste, das dir diese Woche passiert ist?",
            "Mit wem würdest du gerne einen Tag tauschen?",
            "Was hat dich zuletzt überrascht?",
            "Welches Talent hättest du gerne?",
            "Was ist dein Lieblings-Geruch?",
            "Wovon kannst du stundenlang erzählen?",
            "Was bedeutet Heimat für dich?",
            "Welche kleine Sache macht deinen Tag besser?",
            # NEUE KENNENLERN-FRAGEN v3.0
            "Was war der beste Zufall in deinem Leben?",
            "Welche Gewohnheit möchtest du gerne ändern?",
            "Was ist dein Lieblings-Wort?",
            "Worüber kannst du richtig lachen?",
            "Was war der beste Rat, den du nie befolgt hast?",
            "Welche Frage stellst du dir immer wieder?",
            "Was ist dein Comfort-Film oder -Buch?",
            "Welchen Moment würdest du gerne nochmal erleben?",
            "Was hast du als Kind gesammelt?",
            "Welche Kleinigkeit macht dich glücklich?",
            "Was ist dein geheimer Traum?",
            "Welche Person hat dich am meisten geprägt?",
            # NEUE KENNENLERN-FRAGEN v4.0
            "Welches Kompliment hast du am liebsten bekommen?",
            "Was ist dein unpopular opinion?",
            "Welcher Song beschreibt deine aktuelle Lebensphase?",
            "Was hast du zuletzt zum ersten Mal gemacht?",
            "Welche Eigenschaft bewunderst du an anderen?",
            "Was ist dein Lieblings-Zitat?",
            "Worüber könntest du einen Vortrag halten?",
            "Welche Gewohnheit möchtest du aufgeben?",
            "Was war dein stolzester Moment?",
            "Welches Tier passt am besten zu dir?",
            "Was ist dein Lieblings-Wetter für einen freien Tag?",
            "Welche Fähigkeit würdest du sofort lernen wollen?",
        ]


# =============================================================================
# SMALLTALK ENGINE
# =============================================================================

class SmalltalkEngine:
    """
    Hauptklasse für Smalltalk-Konversation.
    Wählt passende Themen basierend auf Kontext und Präferenzen.
    """

    def __init__(self):
        self.database = SmalltalkDatabase()
        self.used_topics: List[str] = []
        self.max_history = 15
        self.current_category: Optional[SmalltalkCategory] = None

    def get_random_topic(
        self,
        category: Optional[SmalltalkCategory] = None,
        max_depth: ConversationDepth = ConversationDepth.TIEFGEHEND
    ) -> Optional[SmalltalkTopic]:
        """
        Wählt ein zufälliges Smalltalk-Thema.

        Args:
            category: Gewünschte Kategorie (optional)
            max_depth: Maximale Gesprächstiefe
        """
        candidates = self.database.topics.copy()

        # Filter nach Kategorie
        if category:
            candidates = [t for t in candidates if t.category == category]

        # Filter nach Tiefe
        candidates = [t for t in candidates if t.depth.value <= max_depth.value]

        # Vermeide Wiederholungen
        candidates = [t for t in candidates if t.starter not in self.used_topics]

        if not candidates:
            # Fallback ohne Wiederholungs-Filter
            candidates = [t for t in self.database.topics if t.depth.value <= max_depth.value]

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.starter)
        self.current_category = selected.category
        return selected

    def get_time_appropriate_topic(self) -> Optional[SmalltalkTopic]:
        """Wählt ein zur Tageszeit passendes Thema"""
        hour = datetime.now().hour

        if 6 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        candidates = [
            t for t in self.database.topics
            if t.time_appropriate == time_of_day or t.time_appropriate is None
        ]

        candidates = [t for t in candidates if t.starter not in self.used_topics]

        if not candidates:
            return self.get_random_topic()

        selected = random.choice(candidates)
        self._add_to_history(selected.starter)
        return selected

    def get_season_appropriate_topic(self) -> Optional[SmalltalkTopic]:
        """Wählt ein zur Jahreszeit passendes Thema"""
        month = datetime.now().month

        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "autumn"
        else:
            season = "winter"

        candidates = [
            t for t in self.database.topics
            if t.season_appropriate == season
        ]

        if not candidates:
            return self.get_random_topic()

        return random.choice(candidates)

    def get_transition(self, to_category: SmalltalkCategory) -> Optional[str]:
        """Gibt eine Übergangsphrase zu einem neuen Thema zurück"""
        transitions = [
            t for t in self.database.transitions
            if t.to_category == to_category
            and (t.from_category is None or t.from_category == self.current_category)
        ]

        if transitions:
            return random.choice(transitions).phrase
        return None

    def get_kennenlernen_frage(self) -> str:
        """Gibt eine Kennenlern-Frage zurück"""
        available = [f for f in self.database.kennenlernen_fragen if f not in self.used_topics]
        if not available:
            available = self.database.kennenlernen_fragen

        selected = random.choice(available)
        self._add_to_history(selected)
        return selected

    def get_interesting_fact(
        self,
        category: Optional[SmalltalkCategory] = None
    ) -> Optional[InterestingFact]:
        """Gibt einen interessanten Fakt zurück"""
        candidates = self.database.facts

        if category:
            candidates = [f for f in candidates if f.category == category]

        if not candidates:
            candidates = self.database.facts

        return random.choice(candidates) if candidates else None

    def get_follow_up(self, topic: SmalltalkTopic) -> Optional[str]:
        """Gibt eine Follow-up-Frage zu einem Thema zurück"""
        if topic.follow_ups:
            return random.choice(topic.follow_ups)
        return None

    def format_topic_with_fact(
        self,
        category: SmalltalkCategory
    ) -> str:
        """Kombiniert ein Thema mit einem passenden Fakt"""
        topic = self.get_random_topic(category=category)
        fact = self.get_interesting_fact(category=category)

        result = topic.starter if topic else ""

        if fact:
            result += f"\n\nFun Fact: {fact.fact}"
            if fact.follow_up_question:
                result += f" {fact.follow_up_question}"

        return result

    def _add_to_history(self, item: str):
        """Fügt ein Element zur Historie hinzu"""
        self.used_topics.append(item)
        if len(self.used_topics) > self.max_history:
            self.used_topics.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken über die Smalltalk-Datenbank"""
        topics = self.database.topics

        category_counts = {}
        for cat in SmalltalkCategory:
            count = len([t for t in topics if t.category == cat])
            if count > 0:
                category_counts[cat.value] = count

        return {
            "total_topics": len(topics),
            "total_facts": len(self.database.facts),
            "total_kennenlernen": len(self.database.kennenlernen_fragen),
            "categories": category_counts,
            "recently_used": len(self.used_topics)
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_smalltalk_engine: Optional[SmalltalkEngine] = None

def get_smalltalk_engine() -> SmalltalkEngine:
    """Gibt die globale SmalltalkEngine-Instanz zurück"""
    global _smalltalk_engine
    if _smalltalk_engine is None:
        _smalltalk_engine = SmalltalkEngine()
    return _smalltalk_engine

def get_random_topic() -> Optional[str]:
    """Schneller Zugriff: Zufälliges Thema"""
    engine = get_smalltalk_engine()
    topic = engine.get_random_topic()
    return topic.starter if topic else None

def get_kennenlernen_frage() -> str:
    """Schneller Zugriff: Kennenlern-Frage"""
    engine = get_smalltalk_engine()
    return engine.get_kennenlernen_frage()

def get_fun_fact() -> Optional[str]:
    """Schneller Zugriff: Interessanter Fakt"""
    engine = get_smalltalk_engine()
    fact = engine.get_interesting_fact()
    return fact.fact if fact else None


# Aliase für holo_brain.py Kompatibilität
SmalltalkTopicsEngine = SmalltalkEngine
create_smalltalk_engine = get_smalltalk_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = SmalltalkEngine()
    stats = engine.get_stats()

    print("=" * 60)
    print("HOLO SMALLTALK TOPICS ENGINE v1.0")
    print("=" * 60)
    print(f"\nStatistiken:")
    print(f"  Gesamt Themen: {stats['total_topics']}")
    print(f"  Fakten: {stats['total_facts']}")
    print(f"  Kennenlern-Fragen: {stats['total_kennenlernen']}")
    print(f"\nKategorien:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  {cat}: {count}")

    print("\n" + "-" * 60)
    print("Beispiele:")

    print("\n[Zufälliges Thema]")
    topic = engine.get_random_topic()
    if topic:
        print(f"  Starter: {topic.starter}")
        if topic.follow_ups:
            print(f"  Follow-up: {topic.follow_ups[0]}")

    print("\n[Gaming-Thema]")
    topic = engine.get_random_topic(category=SmalltalkCategory.GAMING)
    if topic:
        print(f"  Starter: {topic.starter}")

    print("\n[Kennenlern-Frage]")
    frage = engine.get_kennenlernen_frage()
    print(f"  {frage}")

    print("\n[Interessanter Fakt]")
    fact = engine.get_interesting_fact()
    if fact:
        print(f"  {fact.fact}")
        if fact.follow_up_question:
            print(f"  → {fact.follow_up_question}")

    print("\n[Kemonomimi-Thema]")
    topic = engine.get_random_topic(category=SmalltalkCategory.KEMONOMIMI)
    if topic:
        print(f"  {topic.starter}")

    print("\n[Zeitpassendes Thema]")
    topic = engine.get_time_appropriate_topic()
    if topic:
        print(f"  {topic.starter}")
