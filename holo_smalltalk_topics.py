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
