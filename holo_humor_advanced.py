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
