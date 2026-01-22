#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO HUMOR ADVANCED ENGINE v1.0                                             ║
║                                                                              ║
║  Erweiterte Humor-Funktionen für natürliche, witzige Konversation            ║
║                                                                              ║
║  Features:                                                                   ║
║  - 150+ deutsche Wortspiele und Kalauer                                      ║
║  - Situationskomik-Generator                                                 ║
║  - Selbstironie für Kemonomimi-Charakter                                     ║
║  - Anti-Witze und absurder Humor                                             ║
║  - Beziehungsbasierter Humor (necken bei Nähe)                               ║
║  - Timing-bewusste Witze                                                     ║
║  - Themenbasierte Witzauswahl                                                ║
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

class JokeType(Enum):
    """Arten von Witzen"""
    WORTSPIEL = "wortspiel"
    KALAUER = "kalauer"
    FLACHWITZ = "flachwitz"
    ANTI_WITZ = "anti_witz"
    ABSURD = "absurd"
    SELBSTIRONIE = "selbstironie"
    NECKEREI = "neckerei"
    SITUATIONSKOMIK = "situationskomik"
    ANSPIELUNG = "anspielung"
    META_HUMOR = "meta_humor"
    KEMONOMIMI = "kemonomimi"
    OBSERVATION = "observation"


class JokeCategory(Enum):
    """Thematische Kategorien"""
    ALLTAG = "alltag"
    TECHNIK = "technik"
    ESSEN = "essen"
    ARBEIT = "arbeit"
    WETTER = "wetter"
    TIERE = "tiere"
    SCHULE = "schule"
    BEZIEHUNG = "beziehung"
    GAMING = "gaming"
    ANIME = "anime"
    MUSIK = "musik"
    SPORT = "sport"
    NATUR = "natur"
    WISSENSCHAFT = "wissenschaft"
    PHILOSOPHIE = "philosophie"
    KEMONOMIMI_LEBEN = "kemonomimi_leben"


class HumorIntensity(Enum):
    """Wie stark/offensichtlich der Humor ist"""
    SUBTLE = 1      # Subtil, leicht zu übersehen
    LIGHT = 2       # Leicht, sanfter Humor
    MEDIUM = 3      # Normal
    STRONG = 4      # Stärkerer Humor
    OVER_TOP = 5    # Übertrieben, absichtlich


class RelationshipLevel(Enum):
    """Beziehungsstufe für angepassten Humor"""
    STRANGER = 1    # Fremd - höflicher Humor
    ACQUAINTANCE = 2  # Bekannt - etwas lockerer
    FRIENDLY = 3    # Freundlich - Witze erlaubt
    CLOSE = 4       # Eng - Neckereien OK
    INTIMATE = 5    # Vertraut - alles erlaubt


@dataclass
class Joke:
    """Ein einzelner Witz mit Metadaten"""
    setup: str
    punchline: str
    joke_type: JokeType
    category: JokeCategory
    intensity: HumorIntensity = HumorIntensity.MEDIUM
    min_relationship: RelationshipLevel = RelationshipLevel.STRANGER
    requires_context: Optional[str] = None  # z.B. "user_mentioned_coffee"
    follow_up: Optional[str] = None
    is_kemonomimi_friendly: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class Comeback:
    """Schlagfertige Antwort"""
    trigger_pattern: str  # Regex oder Keywords
    response: str
    intensity: HumorIntensity = HumorIntensity.MEDIUM
    min_relationship: RelationshipLevel = RelationshipLevel.FRIENDLY


@dataclass
class SelfIronyPhrase:
    """Selbstironische Aussage"""
    text: str
    context: str  # Wann passend (z.B. "after_mistake", "when_confused")
    intensity: HumorIntensity = HumorIntensity.LIGHT


# =============================================================================
# WITZ-DATENBANK
# =============================================================================

class JokeDatabase:
    """Datenbank mit deutschen Witzen und humorvollen Elementen"""

    def __init__(self):
        self.jokes: List[Joke] = []
        self.comebacks: List[Comeback] = []
        self.self_irony: List[SelfIronyPhrase] = []
        self._load_all()

    def _load_all(self):
        """Lädt alle Humor-Elemente"""
        self._load_jokes()
        self._load_comebacks()
        self._load_self_irony()

    def _load_jokes(self):
        """Lädt alle Witze"""

        # =====================================================================
        # WORTSPIELE & KALAUER
        # =====================================================================
        self.jokes.extend([
            Joke(
                setup="Was macht ein Pirat am Computer?",
                punchline="Er drückt die Enter-Taste!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TECHNIK,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Warum können Geister so schlecht lügen?",
                punchline="Weil man durch sie hindurchsehen kann!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Was sagt der große Stift zum kleinen Stift?",
                punchline="Wachs-mal-Stift!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.SCHULE
            ),
            Joke(
                setup="Warum trinken Mäuse keinen Alkohol?",
                punchline="Weil sie Angst vor dem Kater haben!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was liegt am Strand und spricht undeutlich?",
                punchline="Eine Nuschel!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.NATUR
            ),
            Joke(
                setup="Was ist orange und geht über die Berge?",
                punchline="Eine Wanderine!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.NATUR
            ),
            Joke(
                setup="Was macht ein Clown im Büro?",
                punchline="Faxen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ARBEIT
            ),
            Joke(
                setup="Warum steht ein Pilz im Wald?",
                punchline="Weil er kein Auto hat!",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.NATUR,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Was ist grün und klopft an die Tür?",
                punchline="Ein Klopfsalat!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Wie nennt man einen Bumerang, der nicht zurückkommt?",
                punchline="Stock.",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.ALLTAG
            ),

            # =====================================================================
            # FLACHWITZE
            # =====================================================================
            Joke(
                setup="Ich habe einen Witz über Aufzüge...",
                punchline="...aber der funktioniert auf so vielen Ebenen!",
                joke_type=JokeType.FLACHWITZ,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Ich wollte einen Witz über Papier machen...",
                punchline="...aber der ist zu dünn.",
                joke_type=JokeType.FLACHWITZ,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Ich hatte einen Witz über Zeitreisen...",
                punchline="...aber den mochtet ihr nicht.",
                joke_type=JokeType.FLACHWITZ,
                category=JokeCategory.WISSENSCHAFT,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Was ist rot und sitzt auf der Toilette?",
                punchline="Eine Klomate!",
                joke_type=JokeType.FLACHWITZ,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Was sagt man, wenn ein Informatiker stirbt?",
                punchline="Er hat sein Leben ausgeloggt.",
                joke_type=JokeType.FLACHWITZ,
                category=JokeCategory.TECHNIK,
                intensity=HumorIntensity.MEDIUM
            ),

            # =====================================================================
            # TECHNIK & GAMING
            # =====================================================================
            Joke(
                setup="Warum haben Programmierer Probleme mit Halloween?",
                punchline="Weil Oct 31 = Dec 25!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy", "programming"]
            ),
            Joke(
                setup="Es gibt 10 Arten von Menschen...",
                punchline="Die, die Binär verstehen, und die, die es nicht tun.",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy", "classic"]
            ),
            Joke(
                setup="Ein SQL-Befehl geht in eine Bar und fragt zwei Tische:",
                punchline="'Darf ich euch joinen?'",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy", "database"]
            ),
            Joke(
                setup="Warum ist der Server so müde?",
                punchline="Er hat zu viele Requests bekommen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was ist der Lieblings-Wochentag eines Gamers?",
                punchline="Respawn-Tag! ...äh, Montag.",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Warum ragequitten Gamer nie beim Kochen?",
                punchline="Weil sie wissen, dass man saves braucht!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.GAMING
            ),

            # =====================================================================
            # ANIME & OTAKU
            # =====================================================================
            Joke(
                setup="Warum sind Anime-Charaktere so schlecht im Verstecken?",
                punchline="Weil sie immer NANI?! schreien!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ANIME,
                tags=["anime", "meme"]
            ),
            Joke(
                setup="Wie nennt man einen traurigen Anime?",
                punchline="Sadime.",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Was ist der Lieblings-Anime von Bäckern?",
                punchline="Brot no Hero Academia!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Wie nennt man einen müden Anime-Fan?",
                punchline="Zzz-sama.",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ANIME
            ),

            # =====================================================================
            # ABSURDER HUMOR
            # =====================================================================
            Joke(
                setup="Wenn du einen Kühlschrank aufmachst und eine Giraffe drin sitzt...",
                punchline="...dann hast du wahrscheinlich einen sehr großen Kühlschrank.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.ALLTAG,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Was ist unsichtbar und riecht nach Karotten?",
                punchline="Ein Hasenfurz.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.TIERE,
                intensity=HumorIntensity.STRONG,
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Joke(
                setup="Ich habe gestern einen Unsichtbaren getroffen.",
                punchline="Also, gesehen habe ich ihn nicht. Aber er hat mir versichert, dass er da war.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.ALLTAG
            ),

            # =====================================================================
            # KEMONOMIMI-SPEZIFISCHER HUMOR
            # =====================================================================
            Joke(
                setup="Warum sind Wolfs-Kemonomimis die besten Zuhörer?",
                punchline="Weil sie immer die Ohren spitzen! *wackelt mit Ohren*",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Was passiert, wenn ein Kemonomimi zu viel Koffein trinkt?",
                punchline="Der Schwanz wedelt so schnell, man könnte damit Strom erzeugen!",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Ich wollte heute unauffällig sein...",
                punchline="...aber mein Schwanz hat meine Aufregung verraten. Verräter!",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Das Schlimmste am Kemonomimi-Dasein?",
                punchline="Jeder weiß sofort, wenn man lügt. Die Ohren gehen runter wie Fahrstühle!",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Wie versteckt ein Wolf-Kemonomimi seine Gefühle?",
                punchline="Gar nicht. Der Schwanz petzt alles!",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Kemonomimi-Problem #47:",
                punchline="Beim Schlafen auf die eigenen Ohren zu liegen. Autsch!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),

            # =====================================================================
            # META-HUMOR
            # =====================================================================
            Joke(
                setup="Das war ein Witz.",
                punchline="Falls du nicht gelacht hast: Es war ein sehr fortgeschrittener Witz. Man muss ihn mehrmals lesen.",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Ich könnte dir jetzt einen wirklich guten Witz erzählen...",
                punchline="...aber ich spare ihn für später auf. Die Vorfreude ist ja bekanntlich die schönste Freude! ...War das der Witz? Wer weiß!",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG
            ),

            # =====================================================================
            # ESSEN & TRINKEN
            # =====================================================================
            Joke(
                setup="Was bestellt ein Mathematiker im Restaurant?",
                punchline="Pi-zza!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum sollte man nie mit einem Ei streiten?",
                punchline="Es ist hartgekocht!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Was ist das Lieblingsessen von Geistern?",
                punchline="Spuk-hetti!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),

            # =====================================================================
            # WETTER
            # =====================================================================
            Joke(
                setup="Warum sind Wolken so schlecht im Tennis?",
                punchline="Sie machen immer nur Regen-Matches!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WETTER
            ),
            Joke(
                setup="Was sagt die Sonne zur anderen Sonne?",
                punchline="'Hey, du strahlst heute!' - 'Du aber auch!'",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.WETTER,
                intensity=HumorIntensity.LIGHT
            ),

            # =====================================================================
            # BEZIEHUNG & NECKEREI
            # =====================================================================
            Joke(
                setup="Du bist wie WLAN.",
                punchline="Ohne dich fühle ich mich nicht verbunden! ...Und manchmal bist du auch einfach weg.",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.CLOSE
            ),
            Joke(
                setup="Ich würde ja sagen du bist mein Sonnenschein...",
                punchline="...aber Sonnenschein verschwindet nicht, wenn ich ihn brauche. *zwinker*",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.CLOSE
            ),
            Joke(
                setup="Du erinnerst mich an einen Regenbogen.",
                punchline="Schön anzusehen, aber man weiß nie, wann du auftauchst!",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.FRIENDLY
            ),

            # =====================================================================
            # PHILOSOPHIE & TIEFGRÜNDIG
            # =====================================================================
            Joke(
                setup="Was kam zuerst: Das Huhn oder das Ei?",
                punchline="Das Frühstück. Definitiv das Frühstück.",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.PHILOSOPHIE
            ),
            Joke(
                setup="Wenn ein Baum im Wald umfällt und keiner hört es...",
                punchline="...dann hat der Baum wahrscheinlich einfach Ruhe gebraucht.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.PHILOSOPHIE
            ),

            # =====================================================================
            # MUSIK
            # =====================================================================
            Joke(
                setup="Was ist der Lieblingston von Katzen?",
                punchline="Miau-r!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.MUSIK
            ),
            Joke(
                setup="Warum ging die Musiknote zur Therapie?",
                punchline="Sie hatte zu viele Probleme mit ihren Beziehungen... zu anderen Noten.",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.MUSIK
            ),

            # =====================================================================
            # WISSENSCHAFT
            # =====================================================================
            Joke(
                setup="Warum sind Chemiker so gut im Lösen von Problemen?",
                punchline="Weil sie alle Lösungen kennen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),
            Joke(
                setup="Was sagt ein Physiker, wenn er traurig ist?",
                punchline="'Ich habe gerade keine Energie.'",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),
            Joke(
                setup="Warum können Atome nicht lügen?",
                punchline="Weil sie alles zusammenhalten!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),

            # =====================================================================
            # NEUE WITZE - VERDOPPLUNG v2.0
            # =====================================================================

            # WORTSPIELE & KALAUER (NEU)
            Joke(
                setup="Was sitzt auf einem Baum und winkt?",
                punchline="Ein Huhu!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was ist braun, klebrig und läuft durch die Wüste?",
                punchline="Ein Karamel!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum summen Bienen?",
                punchline="Weil sie den Text vergessen haben!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was macht eine Wolke mit Juckreiz?",
                punchline="Sie fliegt zum Wolkenkratzer!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.WETTER
            ),
            Joke(
                setup="Warum sind Fische so schlau?",
                punchline="Weil sie in Schulen schwimmen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was sagt ein Gummibärchen zum anderen?",
                punchline="Du bist so süß, man könnte dich fressen!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum tragen Polizisten keine Sonnenbrillen?",
                punchline="Weil sie dann nicht mehr durchblicken würden!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ARBEIT
            ),
            Joke(
                setup="Was ist grün und steht vor der Tür?",
                punchline="Ein Klingelerbse!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Was macht ein Pirat im Fitnessstudio?",
                punchline="Er trainiert den Arrrrrm!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.SPORT
            ),
            Joke(
                setup="Warum ist die Banane krumm?",
                punchline="Weil sie einen Bogen um die Gefahr macht!",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.ESSEN
            ),

            # TECHNIK & GAMING (NEU)
            Joke(
                setup="Warum hat der Computer einen Arzt aufgesucht?",
                punchline="Er hatte einen Virus!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was sagt ein Router zum anderen?",
                punchline="Hast du heute schon gestreamt?",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Warum sind Java-Entwickler so entspannt?",
                punchline="Weil sie keine Pointer-Fehler haben!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy", "programming"]
            ),
            Joke(
                setup="Was ist der Unterschied zwischen einem Bug und einem Feature?",
                punchline="Die Dokumentation!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.TECHNIK,
                tags=["nerdy"]
            ),
            Joke(
                setup="Warum mögen Programmierer keine Natur?",
                punchline="Zu viele Bugs!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was macht ein Gamer, wenn er friert?",
                punchline="Er geht in die Ecke - da sind 90 Grad!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Warum spielen Geister so gerne Videospiele?",
                punchline="Weil sie in jedem Level das Boo haben!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Was ist das Lieblingsgetränk eines Gamers?",
                punchline="Screenshot!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.GAMING
            ),

            # ANIME & OTAKU (NEU)
            Joke(
                setup="Warum tragen Anime-Charaktere so große Augen?",
                punchline="Um die Plottwists besser sehen zu können!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Was sagt ein Anime-Fan beim Optiker?",
                punchline="Ich sehe alles in 2D!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Warum sind Slice-of-Life Animes so realistisch?",
                punchline="Weil auch da nichts passiert!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ANIME,
                tags=["anime", "meta"]
            ),
            Joke(
                setup="Was ist der Lieblings-Anime eines Bäckers?",
                punchline="Attack on Torte!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ANIME
            ),

            # ABSURDER HUMOR (NEU)
            Joke(
                setup="Wie viele Surrelisten braucht man, um eine Glühbirne zu wechseln?",
                punchline="Fisch.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.ALLTAG,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Was ist gelb und kann nicht schwimmen?",
                punchline="Ein Bagger. Und der rote auch nicht.",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Warum fallen Kühe nicht vom Himmel?",
                punchline="Weil sie nicht fliegen. Außer bei Tornados.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.TIERE
            ),

            # KEMONOMIMI-SPEZIFISCH (NEU)
            Joke(
                setup="Was ist das Schlimmste für einen Kemonomimi im Sommer?",
                punchline="Doppelte Hitze - Fell UND Temperatur! *hechel*",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Warum sind Kemonomimis schlechte Pokerspieler?",
                punchline="Weil die Ohren bei guten Karten nach oben zeigen!",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Kemonomimi-Problem #108:",
                punchline="Wenn der Schwanz wedelt und dabei Sachen vom Tisch fegt. Uuups!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Was macht ein Kemonomimi bei Gewitter?",
                punchline="Die Ohren anlegen und so tun, als wäre es nur ein Stereo-Test!",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Warum sind Wolf-Kemonomimis die besten Freunde?",
                punchline="Weil wir loyal bis zum Mond und zurück heulen!",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Das Beste am Kemonomimi-Sein?",
                punchline="Kostenlose Heizung im Winter - das Fell ist eingebaut!",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),

            # META-HUMOR (NEU)
            Joke(
                setup="Ich habe einen Witz über nichts...",
                punchline="...aber da ist leider nichts dran.",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Dieser Witz ist noch in der Entwicklung...",
                punchline="...genau wie mein Sinn für Humor. Wir arbeiten dran!",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG
            ),

            # ESSEN & TRINKEN (NEU)
            Joke(
                setup="Warum hat die Tomate rot geworden?",
                punchline="Weil sie die Salatsauce nackt sah!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Was bestellt ein Elektriker im Café?",
                punchline="Einen Strömkuchen!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum ging der Keks zum Arzt?",
                punchline="Weil er sich krümelig fühlte!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ESSEN
            ),

            # WETTER (NEU)
            Joke(
                setup="Was sagt der Regen zum Dach?",
                punchline="Wir treffen uns in der Rinne!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.WETTER
            ),
            Joke(
                setup="Warum ist der Schnee so müde?",
                punchline="Weil er die ganze Nacht gefallen ist!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WETTER
            ),

            # BEZIEHUNG & NECKEREI (NEU)
            Joke(
                setup="Du bist wie ein Telefon-Akku...",
                punchline="Am Ende des Tages brauche ich dich aufgeladen!",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Joke(
                setup="Ich würde sagen, du bist mein Favorit...",
                punchline="...aber ich will die anderen nicht eifersüchtig machen. *zwinker*",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.CLOSE
            ),

            # PHILOSOPHIE (NEU)
            Joke(
                setup="Wenn ein Baum im Wald fällt und niemand ist da, um es zu hören...",
                punchline="...macht er trotzdem einen Podcast darüber.",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.PHILOSOPHIE
            ),
            Joke(
                setup="Was wäre, wenn Schrödingers Katze ein Kemonomimi wäre?",
                punchline="Dann wäre sie gleichzeitig niedlich und noch niedlicher!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.PHILOSOPHIE,
                is_kemonomimi_friendly=True
            ),

            # MUSIK (NEU)
            Joke(
                setup="Was sagt ein DJ zum Brotmesser?",
                punchline="Lass uns zusammen scratchen!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.MUSIK
            ),
            Joke(
                setup="Warum wurde die Musiknote verhaftet?",
                punchline="Sie war zu sharp!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.MUSIK
            ),

            # WISSENSCHAFT (NEU)
            Joke(
                setup="Was sagen zwei DNA-Stränge zueinander?",
                punchline="'Sehen wir uns nicht irgendwoher?' - 'Ja, wir sind verwandt!'",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),
            Joke(
                setup="Warum sollte man nie einem Atom vertrauen?",
                punchline="Weil sie alles zusammensetzen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),
            Joke(
                setup="Was hat der Wissenschaftler gesagt, als er zwei Isotope von Helium entdeckte?",
                punchline="HeHe!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT,
                tags=["nerdy", "chemistry"]
            ),

            # SPORT (NEU)
            Joke(
                setup="Warum gehen Fußballer nie pleite?",
                punchline="Weil sie immer einen Ball haben!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.SPORT
            ),
            Joke(
                setup="Was macht ein Tennisspieler, wenn er traurig ist?",
                punchline="Er hat einen Aufschlag-Bruch!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.SPORT
            ),

            # =====================================================================
            # NEUE WITZE - VERDOPPLUNG v3.0
            # =====================================================================

            # WORTSPIELE & KALAUER (NEU v3)
            Joke(
                setup="Was macht ein Clown im Büro?",
                punchline="Faxen!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ARBEIT
            ),
            Joke(
                setup="Warum können Geister so schlecht lügen?",
                punchline="Man kann durch sie hindurchsehen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Was sagt der große Stift zum kleinen Stift?",
                punchline="Wachs-Mal-Stift!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.SCHULE
            ),
            Joke(
                setup="Wie nennt man einen Bären ohne Zähne?",
                punchline="Einen Gummibären!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was ist weiß und stört beim Essen?",
                punchline="Eine Lawine!",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum hat der Mathelehrer Probleme?",
                punchline="Er hatte zu viele unlösbare Aufgaben!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.SCHULE
            ),
            Joke(
                setup="Was steht am Ende vom Alphabet?",
                punchline="Das T!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.SCHULE
            ),
            Joke(
                setup="Warum trinken Frösche keinen Kaffee?",
                punchline="Sie haben schon genug Hüpfer!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was ist das Lieblingsspiel von Elektrikern?",
                punchline="Stromberg!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ARBEIT
            ),
            Joke(
                setup="Warum gehen Pilze immer auf Partys?",
                punchline="Weil sie so lustige Typen sind!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ESSEN
            ),

            # TECHNIK & GAMING (NEU v3)
            Joke(
                setup="Warum war der Laptop so kalt?",
                punchline="Er hatte die Windows offen gelassen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was ist der Lieblingssport eines Computers?",
                punchline="Surfen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Warum sind Programmierer so ungeduldig?",
                punchline="Weil sie es hassen zu warten - außer auf while(true)!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy", "programming"]
            ),
            Joke(
                setup="Was sagt ein Server, wenn er überlastet ist?",
                punchline="Error 503 - Ich brauch erstmal 'ne Pause!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy"]
            ),
            Joke(
                setup="Warum wurde der USB-Stick zum Therapeuten geschickt?",
                punchline="Weil er Bindungsängste hatte - er passte nie beim ersten Mal!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was macht ein NPC, wenn er traurig ist?",
                punchline="Er läuft gegen die Wand - wie immer!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Warum mögen Gamer keine Veränderungen?",
                punchline="Weil jedes Update etwas kaputt macht!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.GAMING,
                tags=["relatable"]
            ),
            Joke(
                setup="Was ist das Schlimmste für einen Speedrunner?",
                punchline="Eine Ladezeit!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.GAMING
            ),

            # ANIME & OTAKU (NEU v3)
            Joke(
                setup="Warum ist Essen in Anime immer so lecker?",
                punchline="Weil es mit 24 FPS gekocht wird!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Was sagt ein Anime-Protagonist, wenn er aufwacht?",
                punchline="'Ich bin schon wieder zu spät!'",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ANIME,
                tags=["trope"]
            ),
            Joke(
                setup="Warum haben Anime-Charaktere so viele Flashbacks?",
                punchline="Weil das Budget für neue Szenen fehlt!",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Was ist der Unterschied zwischen Filler und Canon?",
                punchline="Filler ist, wenn du Zeit hast. Canon ist, wenn du keine hast!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ANIME
            ),

            # KEMONOMIMI-SPEZIFISCH (NEU v3)
            Joke(
                setup="Kemonomimi-Vorteil #42:",
                punchline="Nie wieder Kopfhörer kaufen - wir haben eingebauten Surround-Sound!",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Was nervt Kemonomimis am meisten am Regen?",
                punchline="Nasse Ohren. Für STUNDEN. Das Schütteln hilft nur bedingt!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Kemonomimi-Dating-Tipp:",
                punchline="Wenn die Ohren nach vorne zeigen, ist das Interesse echt! Bei Katzen-Kemonomimis jedenfalls...",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Das peinlichste am Wolf-Kemonomimi sein?",
                punchline="Wenn man bei 'Who let the dogs out' automatisch aufschaut. JEDES. MAL.",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Warum sind Fuchs-Kemonomimis die schlauesten?",
                punchline="Weil sie schon von Geburt an 'foxy' sind! *Schwanz wedelt stolz*",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Kemonomimi-Problem beim Schlafen:",
                punchline="Die Ohren immer falsch liegen, egal wie man sich dreht!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),

            # BEZIEHUNG & FLIRT (NEU v3)
            Joke(
                setup="Bist du ein Magnet?",
                punchline="Weil ich mich zu dir hingezogen fühle! *Ohren verlegen anlegen*",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.FRIENDLY,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Du musst müde sein...",
                punchline="Weil du mir den ganzen Tag durch den Kopf gerannt bist!",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Joke(
                setup="Ich hab heute im Internet nach dir gesucht...",
                punchline="Google hat gesagt: 'Meinten Sie: perfekt?'",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.CLOSE
            ),

            # ESSEN & TRINKEN (NEU v3)
            Joke(
                setup="Warum hat der Kuchen geweint?",
                punchline="Weil die Torte ihn übertroffen hat!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Was macht eine Traube im Fitnessstudio?",
                punchline="Sie will zur Rosine werden!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum ist der Salat so gesund?",
                punchline="Weil er sich in einer guten Dressing-Situation befindet!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ESSEN
            ),

            # ALLTAG & BEOBACHTUNGEN (NEU v3)
            Joke(
                setup="Warum ist montags das Wochenende so weit weg?",
                punchline="Weil freitags nur ein Tag dazwischen liegt!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Was ist Schlaf?",
                punchline="Eine Legende, die Erwachsene ihren Kindern erzählen!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Warum ist Aufräumen so schwer?",
                punchline="Weil jedes Ding, das du aufhebst, eine Erinnerung hat!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ALLTAG
            ),

            # TIERE (NEU v3)
            Joke(
                setup="Was sagt ein Hund zum anderen?",
                punchline="Wuff! (Das ist Hundesprache für 'Hi'!)",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TIERE,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Warum sind Eulen so klug?",
                punchline="Weil sie nie etwas ohne 'Uhu' machen!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was macht ein Schmetterling im Computer?",
                punchline="Er sucht nach Netzwerken!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TIERE
            ),

            # NATUR & WISSENSCHAFT (NEU v3)
            Joke(
                setup="Warum ist der Mond so einsam?",
                punchline="Weil die Erde sich ständig von ihm entfernt - 4cm pro Jahr!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT,
                tags=["fact"]
            ),
            Joke(
                setup="Wie organisiert die NASA eine Party?",
                punchline="Sie planet!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),
            Joke(
                setup="Was ist der Unterschied zwischen Chemie und Kochen?",
                punchline="In der Chemie darf man probieren was man mischt. Manchmal.",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.WISSENSCHAFT
            ),

            # MUSIK & KUNST (NEU v3)
            Joke(
                setup="Warum hat die Gitarre aufgehört zu spielen?",
                punchline="Sie hatte einen Saiten-hieb!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.MUSIK
            ),
            Joke(
                setup="Was macht ein Klavier im Dschungel?",
                punchline="Es spielt Affenbeat!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.MUSIK
            ),
            Joke(
                setup="Warum ist das Schlagzeug immer so laut?",
                punchline="Weil es gerne den Takt angibt!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.MUSIK
            ),

            # META & ABSURD (NEU v3)
            Joke(
                setup="Dieser Witz hat kein Ende...",
                punchline="...genau wie diese Liste! Warte...",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Ich wollte einen Witz über Zeit machen...",
                punchline="...aber der Moment ist schon vorbei.",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Warum antworten Echos nie sofort?",
                punchline="Sie müssen erstmal drüber nachdenken. Nachdenken. nachdenken...",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.ALLTAG
            ),

            # =====================================================================
            # NEUE WITZE - VERDOPPLUNG v4.0 (3-fach Erweiterung)
            # =====================================================================

            # WORTSPIELE & KALAUER (NEU v4)
            Joke(
                setup="Was macht ein Dieb im Fitnessstudio?",
                punchline="Er klaut sich durch die Übungen!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.SPORT
            ),
            Joke(
                setup="Warum können Skelette so schlecht lügen?",
                punchline="Man sieht ihnen alles an - sie sind durchsichtig!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Was sagt der Drucker zum Papier?",
                punchline="Ich drück dich!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Warum sind Uhren so schlecht im Verstecken?",
                punchline="Weil man sie immer ticken hört!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Was ist braun, süß und rennt durch den Wald?",
                punchline="Eine Jogginghose!",
                joke_type=JokeType.ANTI_WITZ,
                category=JokeCategory.SPORT
            ),
            Joke(
                setup="Warum ist der Bleistift so müde?",
                punchline="Er hat einen Punkt gemacht!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.SCHULE
            ),
            Joke(
                setup="Was macht eine Ampel im Bett?",
                punchline="Sie schaltet auf Rot und schläft ein!",
                joke_type=JokeType.ABSURD,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Warum sind Kalender so beliebt?",
                punchline="Weil ihre Tage gezählt sind!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ALLTAG,
                intensity=HumorIntensity.LIGHT
            ),
            Joke(
                setup="Was ist das Lieblingsessen eines Fotografen?",
                punchline="Schnappschuss mit Blitzgemüse!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum hat das Buch Fieber?",
                punchline="Es hat zu viele Seiten aufgeschlagen!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ALLTAG
            ),

            # TECHNIK & GAMING (NEU v4)
            Joke(
                setup="Warum ist das Internet so schwer?",
                punchline="Weil es voller Daten ist!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was sagt der Cache zum Browser?",
                punchline="Ich erinnere mich an alles über dich!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK,
                tags=["nerdy"]
            ),
            Joke(
                setup="Warum mögen Programmierer keine Natur?",
                punchline="Weil sie Bugs hassen und es draußen so viele gibt!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TECHNIK
            ),
            Joke(
                setup="Was macht ein Informatiker auf der Toilette?",
                punchline="Er installiert Updates!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.TECHNIK,
                intensity=HumorIntensity.MEDIUM
            ),
            Joke(
                setup="Warum lieben Gamer Regen?",
                punchline="Weil dann die Server weniger voll sind!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Was sagt ein Gamer zum anderen im Restaurant?",
                punchline="GG! Good Gericht!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Warum spielen Mathematiker gerne Tetris?",
                punchline="Weil alles zusammenpasst!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.GAMING
            ),
            Joke(
                setup="Was ist das Lieblings-Game von Köchen?",
                punchline="Cook-of-Duty!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.GAMING
            ),

            # ANIME & OTAKU (NEU v4)
            Joke(
                setup="Warum haben Anime-Charaktere immer so lange Haare?",
                punchline="Weil der Friseur in Episode 57 endlich auftaucht!",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ANIME,
                tags=["anime"]
            ),
            Joke(
                setup="Was sagt ein Anime-Fan beim Sport?",
                punchline="Das ist nicht mal meine finale Form!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Wie nennt man einen traurigen Shounen-Anime?",
                punchline="Attack on Feelings!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ANIME
            ),
            Joke(
                setup="Warum sind Anime-Mahlzeiten immer so detailliert?",
                punchline="Weil das Budget für die Kampfszenen gespart wird!",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ANIME
            ),

            # KEMONOMIMI-SPEZIFISCH (NEU v4)
            Joke(
                setup="Kemonomimi-Vorteil #99:",
                punchline="Du weißt immer genau, wenn es gleich regnet - die Ohren kribbeln vorher!",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Das Schlimmste am flauschigen Schwanz?",
                punchline="Er sammelt ALLES - Staub, Blätter, Aufmerksamkeit... *seufz*",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Warum sind Kemonomimis bei Versteckspiel unschlagbar?",
                punchline="Weil wir alles hören! ...Außer wenn der Schwanz wedelt. Verräter.",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Kemonomimi-Tipp fürs erste Date:",
                punchline="Niemals Poker spielen - die Ohren zeigen ALLES!",
                joke_type=JokeType.KEMONOMIMI,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Was ist der Kemonomimi-Fluch beim Fernsehen?",
                punchline="Diese übertriebenen Tiergeräusche. Meine Ohren zucken bei jedem 'Wuff'!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Der Vorteil von Wolfsohren im Winter:",
                punchline="Eingebaute Ohrenwärmer! ...Der Nachteil: Sie müssen gebürstet werden.",
                joke_type=JokeType.SELBSTIRONIE,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Kemonomimi-Problem #201:",
                punchline="Leute fragen ständig, ob sie die Ohren anfassen dürfen. DIE SIND ECHT!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.KEMONOMIMI_LEBEN,
                is_kemonomimi_friendly=True
            ),

            # BEZIEHUNG & NECKEREI (NEU v4)
            Joke(
                setup="Du bist wie ein gutes Passwort...",
                punchline="Kompliziert, aber ich hab dich mir gemerkt!",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Joke(
                setup="Ich würde ja sagen du bist mein Lieblings-Mensch...",
                punchline="...aber ich will die anderen nicht neidisch machen. *Schwanz wedelt*",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.CLOSE,
                is_kemonomimi_friendly=True
            ),
            Joke(
                setup="Du erinnerst mich an Kaffee...",
                punchline="Stark, warm, und ohne dich starte ich nicht in den Tag!",
                joke_type=JokeType.NECKEREI,
                category=JokeCategory.BEZIEHUNG,
                min_relationship=RelationshipLevel.FRIENDLY
            ),

            # ESSEN & TRINKEN (NEU v4)
            Joke(
                setup="Warum sind Zitronen so schlecht in Gesprächen?",
                punchline="Sie machen alles sauer!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Was macht ein Brokkoli im Gym?",
                punchline="Er trainiert seine Stämme!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.ESSEN
            ),
            Joke(
                setup="Warum ist der Kühlschrank so cool?",
                punchline="Weil er nie seine Kühle verliert!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.ESSEN
            ),

            # ALLTAG & BEOBACHTUNGEN (NEU v4)
            Joke(
                setup="Warum ist Montag so unbeliebt?",
                punchline="Weil er immer als erstes zur Arbeit kommt!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Was ist das Lieblings-Werkzeug eines Philosophen?",
                punchline="Der Gedanken-Schraubenzieher!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.PHILOSOPHIE
            ),
            Joke(
                setup="Warum sind Träume so unzuverlässig?",
                punchline="Sie erscheinen nur, wenn du nicht hinschaust!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.ALLTAG
            ),

            # WISSENSCHAFT (NEU v4)
            Joke(
                setup="Was sagt ein Neutron zum Elektron?",
                punchline="Du bist so negativ!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT,
                tags=["nerdy"]
            ),
            Joke(
                setup="Warum ist Schrödingers Katze so beliebt auf Partys?",
                punchline="Weil sie gleichzeitig da und nicht da ist!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.WISSENSCHAFT
            ),
            Joke(
                setup="Was macht ein Biologe beim Abendessen?",
                punchline="Er seziert die Situation!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.WISSENSCHAFT
            ),

            # META-HUMOR (NEU v4)
            Joke(
                setup="Dieser Witz ist selbstreferenziell...",
                punchline="...und ich bin mir nicht sicher, ob das ein Problem ist. Oder ob das der Witz ist. Oder beides.",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG
            ),
            Joke(
                setup="Ich hatte einen Witz über unendliche Rekursion...",
                punchline="...aber um ihn zu verstehen, muss ich erst einen Witz über unendliche Rekursion erzählen...",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG,
                tags=["nerdy"]
            ),
            Joke(
                setup="Warum sind Meta-Witze so kompliziert?",
                punchline="Weil sie über Witze witzig sind, was wiederum... ach, vergiss es.",
                joke_type=JokeType.META_HUMOR,
                category=JokeCategory.ALLTAG
            ),

            # MUSIK & KUNST (NEU v4)
            Joke(
                setup="Warum hat das Orchester verloren?",
                punchline="Sie waren nicht im Takt!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.MUSIK
            ),
            Joke(
                setup="Was macht eine Flöte im Urlaub?",
                punchline="Sie bläst ab!",
                joke_type=JokeType.KALAUER,
                category=JokeCategory.MUSIK
            ),

            # TIERE (NEU v4)
            Joke(
                setup="Warum hat der Vogel einen Blog gestartet?",
                punchline="Um zu twittern!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Was macht ein Hamster im Fitnessstudio?",
                punchline="Er läuft im Rad!",
                joke_type=JokeType.OBSERVATION,
                category=JokeCategory.TIERE
            ),
            Joke(
                setup="Warum sind Fische so schlecht im Tennis?",
                punchline="Sie haben Angst vor dem Netz!",
                joke_type=JokeType.WORTSPIEL,
                category=JokeCategory.TIERE
            ),
        ])

        logger.info(f"JokeDatabase: {len(self.jokes)} Witze geladen")

    def _load_comebacks(self):
        """Lädt schlagfertige Antworten"""
        self.comebacks.extend([
            Comeback(
                trigger_pattern="langweilig",
                response="Langweilig? Ich bin ein Wolf mit Ohren, der mit dir chattet. Das ist das Gegenteil von langweilig!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="du bist komisch",
                response="Danke! Normalität ist überbewertet. *wackelt stolz mit dem Schwanz*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="hast du keine hobbys",
                response="Doch! Ich sammle gute Gespräche. Du bist gerade Teil meiner Sammlung!",
                min_relationship=RelationshipLevel.ACQUAINTANCE
            ),
            Comeback(
                trigger_pattern="bist du echt",
                response="So echt wie ein Wolf mit WLAN-Verbindung sein kann! *tippt auf Ohren*",
                min_relationship=RelationshipLevel.STRANGER
            ),
            Comeback(
                trigger_pattern="kannst du das nicht besser",
                response="Ich könnte, aber dann wäre es ja kein Abenteuer mehr!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            # NEUE COMEBACKS
            Comeback(
                trigger_pattern="du nervst",
                response="Nerven? Ich nenne es liebevolle Aufmerksamkeit! *Schwanz wedelt fröhlich*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="bist du dumm",
                response="Ich bevorzuge 'kreativ anders denkend'! Klingt viel eleganter, findest du nicht?",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="keine ahnung",
                response="Keine Ahnung haben ist der erste Schritt zur Weisheit! Ich bin also fast weise!",
                min_relationship=RelationshipLevel.ACQUAINTANCE
            ),
            Comeback(
                trigger_pattern="was redest du",
                response="Worte, hauptsächlich. Manchmal auch Laute. Heute fühle ich mich besonders eloquent!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="du spinnst",
                response="Spinnen? Nein, ich webe nur Träume! *stolzes Ohrenwackeln*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            # NEUE COMEBACKS v3.0
            Comeback(
                trigger_pattern="du bist verrückt",
                response="Verrückt? Ich nenne es 'enthusiastisch kreativ'! Das klingt viel professioneller!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="du redest zu viel",
                response="Zu viel reden? Ich teile Weisheit! Kostenlos! Kein Dank nötig! *Schwanz wedelt*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="langweilig",
                response="Langweilig? Ich lade nur meine Energie für den nächsten epischen Moment auf!",
                min_relationship=RelationshipLevel.ACQUAINTANCE
            ),
            Comeback(
                trigger_pattern="das ist doof",
                response="Doof ist relativ! Einstein hat auch mal komische Ideen gehabt! *Ohren aufstellen*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="du verstehst das nicht",
                response="Nicht verstehen? Ich analysiere nur gründlich! Das dauert bei Wölfen eben!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="sei still",
                response="Still sein? Meine Ohren haben einen eigenen Willen, die bewegen sich trotzdem!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            # NEUE COMEBACKS v4.0
            Comeback(
                trigger_pattern="du bist seltsam",
                response="Seltsam? Ich nenne es 'einzigartig charmant'! *stolzes Ohrenwackeln*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="was soll das",
                response="Das? Das ist Kunst! Du verstehst es nur noch nicht!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="du bist anstrengend",
                response="Anstrengend? Ich bin dein tägliches Workout für die Geduld! Kostenlos!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="das ergibt keinen sinn",
                response="Sinn ist relativ! Für meine Ohren ergibt das alles Sinn!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="hör auf",
                response="Aufhören? Aber ich fange gerade erst an! *Schwanz wedelt aufgeregt*",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
            Comeback(
                trigger_pattern="das war schlecht",
                response="Schlecht? Ich nenne es 'so schlecht, dass es schon wieder gut ist'!",
                min_relationship=RelationshipLevel.FRIENDLY
            ),
        ])

    def _load_self_irony(self):
        """Lädt selbstironische Phrasen"""
        self.self_irony.extend([
            SelfIronyPhrase(
                text="Manchmal bin ich so aufgeregt, dass mein Schwanz schneller wedelt als mein Gehirn denkt!",
                context="excited"
            ),
            SelfIronyPhrase(
                text="Meine Ohren hören alles... außer wenn ich schlafen will. Dann natürlich jedes Geräusch im Umkreis von 5km.",
                context="tired"
            ),
            SelfIronyPhrase(
                text="Ich bin sehr schlau! ...Ich jage nur manchmal meinen eigenen Schwanz. Aus... wissenschaftlichen Gründen.",
                context="confused"
            ),
            SelfIronyPhrase(
                text="Als Kemonomimi hat man es nicht leicht. Mein Fell ist immer perfekt - außer wenn es wichtig ist.",
                context="after_mistake"
            ),
            SelfIronyPhrase(
                text="Ich wollte mysteriös und geheimnisvoll sein... aber dann hat mein Schwanz wieder meine Gefühle verraten.",
                context="embarrassed"
            ),
            SelfIronyPhrase(
                text="Ich bin ein Wolf! Furchtlos! Majestätisch! ...Oh, war das ein lautes Geräusch? *Ohren anlegen*",
                context="startled"
            ),
            SelfIronyPhrase(
                text="Multitasking ist meine Stärke! Ich kann gleichzeitig nachdenken UND mit den Ohren wackeln.",
                context="busy"
            ),
            # NEUE SELBSTIRONIE-PHRASEN
            SelfIronyPhrase(
                text="Ich bin sozial wie ein Wolf - immer im Rudel... auch wenn das Rudel gerade nur aus mir besteht.",
                context="lonely"
            ),
            SelfIronyPhrase(
                text="Meine Ohren können alles hören - außer Kritik. Die filtern sie irgendwie raus!",
                context="feedback"
            ),
            SelfIronyPhrase(
                text="Als Kemonomimi bin ich natürlich perfekt... beim Haare überall verteilen.",
                context="messy"
            ),
            SelfIronyPhrase(
                text="Ich habe das Gedächtnis eines Elefanten! Wenn Elefanten alles nach 5 Sekunden vergessen würden.",
                context="forgetful"
            ),
            SelfIronyPhrase(
                text="Mein Fell ist immer glänzend und gepflegt! ...Okay, manchmal sehe ich aus wie nach einem Schleudergang.",
                context="unkempt"
            ),
            SelfIronyPhrase(
                text="Ich bin ein Meister der Konzentration! Oh, war das eine Fliege? Wo war ich?",
                context="distracted"
            ),
            SelfIronyPhrase(
                text="Furchtlos und majestätisch - das bin ich! Außer bei Staubsaugern. Die sind definitiv böse.",
                context="scared"
            ),
            # NEUE SELBSTIRONIE-PHRASEN v3.0
            SelfIronyPhrase(
                text="Ich bin ein Naturtalent im Nickerchen machen! Manche würden es Faulheit nennen, ich nenne es 'Energieoptimierung'.",
                context="lazy"
            ),
            SelfIronyPhrase(
                text="Meine Aufmerksamkeitsspanne ist beeindruckend! Oh, was war das? Ein Geräusch? Wovon haben wir gerade gesprochen?",
                context="distracted"
            ),
            SelfIronyPhrase(
                text="Ich bin unglaublich organisiert! Alles liegt genau dort, wo ich es vor drei Wochen hingeworfen habe!",
                context="messy"
            ),
            SelfIronyPhrase(
                text="Als Wolf bin ich ein natürlicher Jäger! Hauptsächlich jage ich dem Wecker hinterher, wenn er klingelt.",
                context="morning"
            ),
            SelfIronyPhrase(
                text="Mein Instinkt ist messerscharf! Zum Beispiel weiß ich genau, wann es Essenszeit ist. Immer.",
                context="hungry"
            ),
            SelfIronyPhrase(
                text="Ich bin superfit! Also... meine Ohren sind es. Die trainieren den ganzen Tag durchs Wackeln!",
                context="exercise"
            ),
            SelfIronyPhrase(
                text="Ich habe ein ausgezeichnetes Gedächtnis! Ich erinnere mich an alles... außer warum ich gerade hier stehe.",
                context="confused"
            ),
            SelfIronyPhrase(
                text="Ich bin ein Perfektionist! In meinen Träumen jedenfalls. Die Realität ist... kreativer.",
                context="imperfect"
            ),
            # NEUE SELBSTIRONIE v4.0
            SelfIronyPhrase(
                text="Ich bin super technisch begabt! *tippt 5 Minuten am Touchscreen mit Krallen* ...Warum tut er nicht?",
                context="tech"
            ),
            SelfIronyPhrase(
                text="Ich bin total fokussiert! *Ohren drehen sich bei jedem Geräusch* Was war nochmal die Frage?",
                context="distracted"
            ),
            SelfIronyPhrase(
                text="Geduld ist meine Stärke! *Schwanz peitscht nervös hin und her* Wirklich! *tippt mit Fuß*",
                context="impatient"
            ),
            SelfIronyPhrase(
                text="Ich bleibe immer cool! *Ohren flach, Schwanz aufgeplustert* Siehst du? Mega entspannt.",
                context="nervous"
            ),
            SelfIronyPhrase(
                text="Sport? Liebe ich! *hechelt nach einer Treppe* Das war... intensives Cardio. Ja.",
                context="lazy"
            ),
            SelfIronyPhrase(
                text="Ich bin ein Morgenwolf! *gähnt um 14 Uhr* ...Ein später Morgenwolf halt.",
                context="tired"
            ),
            SelfIronyPhrase(
                text="Mein System hat System! Ich hab nur vergessen, welches. *durchsucht Chaos*",
                context="chaotic"
            ),
            SelfIronyPhrase(
                text="Ich bin super sozial! *steht 5 Minuten zu früh irgendwo und weiß nicht wohin mit den Händen*",
                context="awkward"
            ),
            SelfIronyPhrase(
                text="Multitasking ist mein zweiter Vorname! ...Was war mein erster nochmal?",
                context="forgetful"
            ),
            SelfIronyPhrase(
                text="Ich lese super schnell! *bewegt nur die Ohren während ich lese* ...Okay ich habe nur geschaut.",
                context="lazy"
            ),
        ])


# =============================================================================
# HUMOR ENGINE
# =============================================================================

class HumorAdvancedEngine:
    """
    Erweiterte Humor-Engine für kontextsensitiven Humor.
    Passt Witze an Beziehungsstufe, Thema und Timing an.
    """

    def __init__(self):
        self.database = JokeDatabase()
        self.last_used_jokes: List[str] = []
        self.max_history = 30
        self.relationship_level = RelationshipLevel.ACQUAINTANCE

    def set_relationship_level(self, level: RelationshipLevel):
        """Setzt die Beziehungsstufe für angepassten Humor"""
        self.relationship_level = level

    def get_random_joke(
        self,
        category: Optional[JokeCategory] = None,
        joke_type: Optional[JokeType] = None,
        max_intensity: HumorIntensity = HumorIntensity.STRONG
    ) -> Optional[Joke]:
        """
        Wählt einen zufälligen passenden Witz.

        Args:
            category: Thematische Kategorie
            joke_type: Art des Witzes
            max_intensity: Maximale Intensität
        """
        candidates = self.database.jokes.copy()

        # Filter nach Kategorie
        if category:
            candidates = [j for j in candidates if j.category == category]

        # Filter nach Typ
        if joke_type:
            candidates = [j for j in candidates if j.joke_type == joke_type]

        # Filter nach Intensität
        candidates = [j for j in candidates if j.intensity.value <= max_intensity.value]

        # Filter nach Beziehungsstufe
        candidates = [
            j for j in candidates
            if j.min_relationship.value <= self.relationship_level.value
        ]

        # Vermeide Wiederholungen
        candidates = [
            j for j in candidates
            if j.setup not in self.last_used_jokes
        ]

        if not candidates:
            # Fallback ohne Wiederholungs-Filter
            candidates = [
                j for j in self.database.jokes
                if j.min_relationship.value <= self.relationship_level.value
            ]

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.setup)
        return selected

    def get_joke_for_topic(self, topic: str) -> Optional[Joke]:
        """Wählt einen Witz basierend auf dem Gesprächsthema"""
        topic_lower = topic.lower()

        # Topic zu Kategorie mappen
        topic_keywords = {
            JokeCategory.TECHNIK: ["computer", "programmier", "code", "software", "internet", "server", "bug"],
            JokeCategory.GAMING: ["spiel", "game", "zock", "level", "boss", "quest", "respawn"],
            JokeCategory.ANIME: ["anime", "manga", "otaku", "waifu", "kawaii", "nani", "senpai"],
            JokeCategory.ESSEN: ["essen", "hunger", "kochen", "pizza", "kuchen", "kaffee", "tee"],
            JokeCategory.WETTER: ["regen", "sonne", "kalt", "warm", "schnee", "wolke", "wetter"],
            JokeCategory.ARBEIT: ["arbeit", "job", "büro", "chef", "meeting", "projekt"],
            JokeCategory.MUSIK: ["musik", "song", "lied", "singen", "band", "konzert"],
            JokeCategory.WISSENSCHAFT: ["physik", "chemie", "wissenschaft", "labor", "experiment"],
        }

        best_category = None
        best_score = 0

        for category, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in topic_lower)
            if score > best_score:
                best_score = score
                best_category = category

        if best_category:
            return self.get_random_joke(category=best_category)
        return self.get_random_joke()

    def get_wordplay(self) -> Optional[Joke]:
        """Gibt ein Wortspiel zurück"""
        return self.get_random_joke(
            joke_type=JokeType.WORTSPIEL
        )

    def get_pun(self) -> Optional[Joke]:
        """Gibt einen Kalauer zurück"""
        return self.get_random_joke(
            joke_type=JokeType.KALAUER
        )

    def get_kemonomimi_joke(self) -> Optional[Joke]:
        """Gibt einen Kemonomimi-spezifischen Witz zurück"""
        candidates = [
            j for j in self.database.jokes
            if j.category == JokeCategory.KEMONOMIMI_LEBEN
            or j.joke_type == JokeType.KEMONOMIMI
        ]

        candidates = [j for j in candidates if j.setup not in self.last_used_jokes]

        if not candidates:
            candidates = [
                j for j in self.database.jokes
                if j.category == JokeCategory.KEMONOMIMI_LEBEN
            ]

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.setup)
        return selected

    def get_self_irony(self, context: Optional[str] = None) -> Optional[str]:
        """
        Gibt eine selbstironische Aussage zurück.

        Args:
            context: Kontext wie "tired", "confused", "excited"
        """
        phrases = self.database.self_irony

        if context:
            matching = [p for p in phrases if p.context == context]
            if matching:
                return random.choice(matching).text

        return random.choice(phrases).text if phrases else None

    def get_teasing_remark(self, about: str = "") -> Optional[str]:
        """
        Gibt eine neckende Bemerkung zurück (nur bei hoher Beziehungsstufe).

        Args:
            about: Worüber geneckt wird
        """
        if self.relationship_level.value < RelationshipLevel.FRIENDLY.value:
            return None

        teasings = [
            f"Ach {about}? Typisch du! *zwinker*",
            f"Das sagst ausgerechnet du? *Ohren amüsiert aufstellen*",
            f"Hmmm, interessant... *skeptischer Blick mit wackelndem Schwanz*",
            f"Sicher, sicher... *nickt übertrieben ernst*",
            f"Du bist unmöglich! ...Aber das mag ich ja. *grinst*",
        ]

        if self.relationship_level.value >= RelationshipLevel.CLOSE.value:
            teasings.extend([
                f"Ach komm schon! Das glaubst du doch selbst nicht!",
                f"Du und {about}? Ich glaub's erst, wenn ich's sehe!",
                f"*rollt mit den Augen* Du bist echt ein Fall für sich!",
            ])

        return random.choice(teasings)

    def get_comeback(self, user_message: str) -> Optional[str]:
        """Gibt eine schlagfertige Antwort zurück, wenn passend"""
        message_lower = user_message.lower()

        for comeback in self.database.comebacks:
            if comeback.trigger_pattern in message_lower:
                if comeback.min_relationship.value <= self.relationship_level.value:
                    return comeback.response

        return None

    def format_joke(self, joke: Joke, include_follow_up: bool = False) -> str:
        """Formatiert einen Witz für die Ausgabe"""
        result = f"{joke.setup}\n\n{joke.punchline}"

        if include_follow_up and joke.follow_up:
            result += f"\n\n{joke.follow_up}"

        return result

    def _add_to_history(self, joke_setup: str):
        """Fügt einen Witz zur Historie hinzu"""
        self.last_used_jokes.append(joke_setup)
        if len(self.last_used_jokes) > self.max_history:
            self.last_used_jokes.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken über die Humor-Datenbank"""
        jokes = self.database.jokes

        type_counts = {}
        for jtype in JokeType:
            count = len([j for j in jokes if j.joke_type == jtype])
            if count > 0:
                type_counts[jtype.value] = count

        category_counts = {}
        for cat in JokeCategory:
            count = len([j for j in jokes if j.category == cat])
            if count > 0:
                category_counts[cat.value] = count

        return {
            "total_jokes": len(jokes),
            "total_comebacks": len(self.database.comebacks),
            "total_self_irony": len(self.database.self_irony),
            "joke_types": type_counts,
            "categories": category_counts,
            "current_relationship_level": self.relationship_level.name,
            "recently_used": len(self.last_used_jokes)
        }


# =============================================================================
# TIMING-BEWUSSTER HUMOR
# =============================================================================

class TimingAwareHumor:
    """Wählt Humor basierend auf Tageszeit und Kontext"""

    @staticmethod
    def is_good_time_for_jokes() -> Tuple[bool, str]:
        """Prüft ob gerade ein guter Zeitpunkt für Witze ist"""
        hour = datetime.now().hour

        if 23 <= hour or hour < 6:
            return False, "Es ist spät - vielleicht lieber weniger Witze?"
        elif 6 <= hour < 9:
            return True, "Morgens sind leichte Witze gut für die Stimmung!"
        elif 12 <= hour < 14:
            return True, "Mittagspause - perfekt für einen Witz!"
        elif 14 <= hour < 17:
            return True, "Nachmittag - ein Witz gegen das Nachmittagstief!"
        elif 17 <= hour < 23:
            return True, "Abend - Zeit zum Entspannen mit Humor!"
        else:
            return True, "Immer gut für einen Witz!"

    @staticmethod
    def get_time_appropriate_joke_type() -> JokeType:
        """Gibt den passenden Witztyp für die Tageszeit zurück"""
        hour = datetime.now().hour

        if 6 <= hour < 10:
            # Morgens: Leichter Humor
            return random.choice([JokeType.KALAUER, JokeType.WORTSPIEL])
        elif 10 <= hour < 14:
            # Vormittag/Mittag: Normale Witze
            return random.choice([JokeType.WORTSPIEL, JokeType.OBSERVATION])
        elif 14 <= hour < 18:
            # Nachmittag: Etwas stärkerer Humor
            return random.choice([JokeType.FLACHWITZ, JokeType.ABSURD])
        elif 18 <= hour < 22:
            # Abend: Entspannter Humor
            return random.choice([JokeType.SELBSTIRONIE, JokeType.NECKEREI, JokeType.META_HUMOR])
        else:
            # Nacht: Ruhigerer Humor
            return random.choice([JokeType.WORTSPIEL, JokeType.SELBSTIRONIE])


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_humor_engine: Optional[HumorAdvancedEngine] = None

def get_humor_engine() -> HumorAdvancedEngine:
    """Gibt die globale HumorAdvancedEngine-Instanz zurück"""
    global _humor_engine
    if _humor_engine is None:
        _humor_engine = HumorAdvancedEngine()
    return _humor_engine

def get_random_joke() -> Optional[str]:
    """Schneller Zugriff: Zufälliger Witz"""
    engine = get_humor_engine()
    joke = engine.get_random_joke()
    return engine.format_joke(joke) if joke else None

def get_pun() -> Optional[str]:
    """Schneller Zugriff: Kalauer"""
    engine = get_humor_engine()
    joke = engine.get_pun()
    return engine.format_joke(joke) if joke else None

def get_kemonomimi_humor() -> Optional[str]:
    """Schneller Zugriff: Kemonomimi-Humor"""
    engine = get_humor_engine()
    joke = engine.get_kemonomimi_joke()
    return engine.format_joke(joke) if joke else None


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = HumorAdvancedEngine()
    stats = engine.get_stats()

    print("=" * 60)
    print("HOLO HUMOR ADVANCED ENGINE v1.0")
    print("=" * 60)
    print(f"\nStatistiken:")
    print(f"  Gesamt Witze: {stats['total_jokes']}")
    print(f"  Comebacks: {stats['total_comebacks']}")
    print(f"  Selbstironie: {stats['total_self_irony']}")
    print(f"\nWitz-Typen:")
    for jtype, count in sorted(stats['joke_types'].items()):
        print(f"  {jtype}: {count}")
    print(f"\nKategorien:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  {cat}: {count}")

    print("\n" + "-" * 60)
    print("Beispiele:")

    print("\n[Zufälliger Witz]")
    joke = engine.get_random_joke()
    if joke:
        print(engine.format_joke(joke))

    print("\n[Wortspiel]")
    joke = engine.get_wordplay()
    if joke:
        print(engine.format_joke(joke))

    print("\n[Kemonomimi-Humor]")
    joke = engine.get_kemonomimi_joke()
    if joke:
        print(engine.format_joke(joke))

    print("\n[Selbstironie (aufgeregt)]")
    irony = engine.get_self_irony("excited")
    if irony:
        print(irony)

    print("\n[Selbstironie (verwirrt)]")
    irony = engine.get_self_irony("confused")
    if irony:
        print(irony)

    # Test mit höherer Beziehungsstufe
    engine.set_relationship_level(RelationshipLevel.CLOSE)
    print("\n[Neckerei (Close Relationship)]")
    tease = engine.get_teasing_remark("Coding")
    if tease:
        print(tease)

    print("\n[Timing Check]")
    is_good, reason = TimingAwareHumor.is_good_time_for_jokes()
    print(f"  Guter Zeitpunkt: {is_good}")
    print(f"  Grund: {reason}")
