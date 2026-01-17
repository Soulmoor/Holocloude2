"""
HOLO MEDIA DISCOVERY SYSTEM v3.0 - COMPLETE EDITION
====================================================

Holo entdeckt SELBST neue Medien basierend auf ihren Präferenzen aus holo_preferences.py!

FEATURES:
- Nutzt HoloTaste für Genre-Präferenzen
- Große Seed-Datenbank mit detaillierten Einträgen
- MyAnimeList API (Jikan) für Anime-Discovery
- RAWG API für Games-Discovery (wenn Key vorhanden)
- Last.fm API für Musik-Discovery
- Wikipedia für Zusammenfassungen
- Automatische Hintergrund-Discovery
- Keine Wiederholungen durch Usage-Tracking
- Organisch wachsende Wissensbasis

APIS:
- Jikan (MyAnimeList): https://api.jikan.moe/v4
- RAWG (Games): https://api.rawg.io/api
- Last.fm: https://www.last.fm/api
- Wikipedia: https://en.wikipedia.org/api/rest_v1
"""

import json
import time
import random
import re
import hashlib
import logging
import threading
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Tuple, Any, Callable
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS - HoloTaste Präferenzen
# =============================================================================

try:
    from holo_preferences import HoloTaste, InterestLevel
    PREFERENCES_AVAILABLE = True
    logger.info("✓ HoloTaste Präferenzen geladen")
except ImportError:
    PREFERENCES_AVAILABLE = False
    logger.warning("⚠ HoloTaste nicht verfügbar - nutze Fallback-Präferenzen")

    class InterestLevel(Enum):
        """Fallback InterestLevel wenn holo_preferences.py nicht verfügbar."""
        PASSIONATE = 1.0      # Absolute Leidenschaft
        ENTHUSIASTIC = 0.8    # Sehr begeistert
        ACTIVE = 0.6          # Aktives Interesse
        CASUAL = 0.4          # Gelegentliches Interesse
        CURIOUS = 0.2         # Neugierig
        NEUTRAL = 0.0         # Neutral
        INDIFFERENT = -0.2    # Gleichgültig
        UNINTERESTED = -0.4   # Desinteressiert
        BORED = -0.6          # Gelangweilt
        AVERSION = -0.8       # Abneigung
        REPULSED = -1.0       # Abstoßung


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class MediaEntry:
    """
    Ein Eintrag in Holos Media-Datenbank.

    Unterstützt Anime, Games, Musik, Filme und Serien.
    Enthält Holos persönliche Meinung und Reaktionen.
    """
    id: str
    media_type: str  # "anime", "game", "music", "movie", "series"
    title: str
    title_alt: str = ""  # Japanischer/Originaltitel

    # === Metadaten ===
    genres: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    year: int = 0
    status: str = ""  # "Finished", "Ongoing", "Upcoming"
    rating: str = ""  # "PG-13", "R", etc.

    # === Typ-spezifische Felder ===
    # Anime/Film/Serie
    studio: str = ""
    director: str = ""
    episodes: int = 0
    duration: str = ""  # "24 min per ep"

    # Games
    developer: str = ""
    publisher: str = ""
    platforms: List[str] = field(default_factory=list)

    # Musik
    artist: str = ""
    album: str = ""
    duration_seconds: int = 0

    # === Inhalt ===
    synopsis: str = ""
    characters: List[Dict[str, str]] = field(default_factory=list)  # [{"name": "X", "role": "Y", "description": "Z"}]

    # === Holos Meinung ===
    holos_thoughts: str = ""           # Ihre persönliche Reaktion
    holos_interest: float = 0.0        # -1 bis 1
    holos_rating: Optional[float] = None  # 1-10 wenn sie es kennt
    matching_preferences: List[str] = field(default_factory=list)  # Welche Präferenzen matchen
    why_she_likes_it: List[str] = field(default_factory=list)
    why_she_dislikes_it: List[str] = field(default_factory=list)

    # === Extras ===
    fun_facts: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)  # Für Games
    quotes: List[str] = field(default_factory=list)  # Berühmte Zitate
    related_media: List[str] = field(default_factory=list)  # Ähnliche Titel
    known_from: str = ""  # "Oshi no Ko Opening"

    # === URLs ===
    source_url: str = ""      # MAL, Steam, etc.
    image_url: str = ""       # Cover/Poster
    trailer_url: str = ""     # YouTube etc.

    # === Tracking ===
    discovered_at: str = ""
    last_used: str = ""
    times_used: int = 0
    is_seed: bool = False
    discovery_source: str = ""  # "seed", "jikan", "rawg", "lastfm", "wikipedia", "user"

    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für JSON-Speicherung."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'MediaEntry':
        """Erstellt MediaEntry aus Dictionary."""
        # Nur bekannte Felder übernehmen
        valid_fields = {k for k in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @staticmethod
    def generate_id(title: str, media_type: str) -> str:
        """Generiert eindeutige ID aus Titel und Typ."""
        key = f"{media_type}:{title.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def get_display_title(self) -> str:
        """Gibt formatierten Titel zurück."""
        if self.title_alt and self.title_alt != self.title:
            return f"{self.title} ({self.title_alt})"
        return self.title

    def get_short_info(self) -> str:
        """Kurze Info für Listen."""
        if self.media_type == "anime":
            return f"{self.title} ({self.year}) - {self.studio}"
        elif self.media_type == "game":
            return f"{self.title} ({self.year}) - {self.developer}"
        elif self.media_type == "music":
            return f"{self.title} - {self.artist}"
        return self.title


# =============================================================================
# PREFERENCE ADAPTER - Brücke zu HoloTaste
# =============================================================================

class PreferenceAdapter:
    """
    Adapter-Klasse die HoloTaste Präferenzen für das Discovery-System nutzbar macht.

    Funktionen:
    - Genre-Mapping für verschiedene APIs
    - Extraktion von geliebten/gehassten Genres
    - Generierung von Holos Reaktionen basierend auf Genres
    """

    # === Genre-Mappings für APIs ===

    # MyAnimeList Genre IDs (Jikan API)
    ANIME_GENRE_IDS = {
        # Action & Adventure
        "action": 1,
        "adventure": 2,
        "fantasy": 10,
        "fantasy_adventure": 10,

        # Drama & Emotion
        "drama": 8,
        "romance": 22,
        "tragedy": 40,

        # Comedy
        "comedy": 4,
        "parody": 20,
        "gag_humor": 57,

        # Slice of Life & Iyashikei
        "slice_of_life": 36,
        "iyashikei": 36,  # Mapped to Slice of Life

        # Mystery & Thriller
        "mystery": 7,
        "suspense": 41,
        "psychological": 40,

        # Sci-Fi & Mecha
        "sci-fi": 24,
        "mecha": 18,
        "space": 29,

        # Horror & Dark
        "horror": 14,
        "gore": 58,
        "supernatural": 37,

        # Sports & Competition
        "sports": 30,
        "racing": 3,

        # Music
        "music": 19,

        # Demographics
        "shounen": 27,
        "shoujo": 25,
        "seinen": 42,
        "josei": 43,

        # Other
        "isekai": 62,
        "ecchi": 9,
        "harem": 35,
        "military": 38,
        "historical": 13,
        "school": 23,
    }

    # RAWG Game Genre Slugs
    GAME_GENRE_SLUGS = {
        "cozy_games": "indie",
        "story_games": "adventure",
        "visual_novels": "visual-novel",
        "puzzle_games": "puzzle",
        "exploration_games": "adventure",
        "jrpg": "role-playing-games-rpg",
        "action_rpg": "role-playing-games-rpg",
        "action_adventure": "action",
        "platformer": "platformer",
        "metroidvania": "platformer",
        "simulation": "simulation",
        "farming_sim": "simulation",
        "roguelike": "indie",
        "roguelite": "indie",
        "open_world": "open-world",
        "sandbox": "sandbox",
        "strategy_games": "strategy",
        "turn_based": "strategy",
        "fps": "shooter",
        "tps": "shooter",
        "horror_games": "horror",
        "survival_horror": "horror",
        "fighting": "fighting",
        "racing": "racing",
        "rhythm": "indie",
        "card_games": "card",
        "mmo": "massively-multiplayer",
    }

    # Last.fm Music Tags
    MUSIC_TAGS = {
        "j-pop": "j-pop",
        "j-rock": "j-rock",
        "anime": "anime",
        "soundtrack": "soundtrack",
        "ost": "ost",
        "classical": "classical",
        "piano": "piano",
        "orchestral": "orchestral",
        "ambient": "ambient",
        "electronic": "electronic",
        "lo_fi": "lo-fi",
        "jazz": "jazz",
        "folk": "folk",
        "metal": "metal",
        "rock": "rock",
        "pop": "pop",
        "vocaloid": "vocaloid",
    }

    # === Präferenz-Extraktion ===

    @classmethod
    def get_anime_preferences(cls) -> Dict[str, Dict]:
        """Holt Anime-Präferenzen aus HoloTaste oder Fallback."""
        if PREFERENCES_AVAILABLE:
            return HoloTaste.ANIME
        return cls._fallback_anime_preferences()

    @classmethod
    def get_game_preferences(cls) -> Dict[str, Dict]:
        """Holt Game-Präferenzen aus HoloTaste oder Fallback."""
        if PREFERENCES_AVAILABLE:
            return HoloTaste.GAMES
        return cls._fallback_game_preferences()

    @classmethod
    def get_music_preferences(cls) -> Dict[str, Dict]:
        """Holt Musik-Präferenzen aus HoloTaste oder Fallback."""
        if PREFERENCES_AVAILABLE:
            return HoloTaste.MUSIC
        return cls._fallback_music_preferences()

    @classmethod
    def get_movie_preferences(cls) -> Dict[str, Dict]:
        """Holt Film-Präferenzen aus HoloTaste oder Fallback."""
        if PREFERENCES_AVAILABLE:
            return getattr(HoloTaste, 'MOVIES', {})
        return {}

    @classmethod
    def get_series_preferences(cls) -> Dict[str, Dict]:
        """Holt Serien-Präferenzen aus HoloTaste oder Fallback."""
        if PREFERENCES_AVAILABLE:
            return getattr(HoloTaste, 'SERIES', {})
        return {}

    @classmethod
    def get_book_preferences(cls) -> Dict[str, Dict]:
        """Holt Buch-Präferenzen aus HoloTaste oder Fallback."""
        if PREFERENCES_AVAILABLE:
            return getattr(HoloTaste, 'BOOKS', {})
        return {}

    @classmethod
    def get_preferences_for_type(cls, media_type: str) -> Dict[str, Dict]:
        """Holt Präferenzen für einen bestimmten Medientyp."""
        mapping = {
            "anime": cls.get_anime_preferences,
            "game": cls.get_game_preferences,
            "music": cls.get_music_preferences,
            "movie": cls.get_movie_preferences,
            "series": cls.get_series_preferences,
            "book": cls.get_book_preferences,
        }
        getter = mapping.get(media_type, lambda: {})
        return getter()

    @classmethod
    def get_loved_genres(cls, media_type: str, threshold: float = 0.6) -> List[Tuple[str, float]]:
        """
        Gibt Genres zurück die Holo liebt (InterestLevel >= threshold).

        Returns:
            Liste von (genre_name, interest_level) sortiert nach Level
        """
        prefs = cls.get_preferences_for_type(media_type)
        loved = []

        for genre, data in prefs.items():
            level = data.get('level', InterestLevel.NEUTRAL)
            # Handle both Enum and float values
            if hasattr(level, 'value'):
                level_val = level.value
            elif isinstance(level, (int, float)):
                level_val = float(level)
            else:
                level_val = 0.0

            if level_val >= threshold:
                loved.append((genre, level_val))

        return sorted(loved, key=lambda x: x[1], reverse=True)

    @classmethod
    def get_disliked_genres(cls, media_type: str, threshold: float = -0.4) -> List[str]:
        """
        Gibt Genres zurück die Holo nicht mag (InterestLevel <= threshold).

        Returns:
            Liste von Genre-Namen
        """
        prefs = cls.get_preferences_for_type(media_type)
        disliked = []

        for genre, data in prefs.items():
            level = data.get('level', InterestLevel.NEUTRAL)
            if hasattr(level, 'value'):
                level_val = level.value
            elif isinstance(level, (int, float)):
                level_val = float(level)
            else:
                level_val = 0.0

            if level_val <= threshold:
                disliked.append(genre)

        return disliked

    @classmethod
    def get_interest_level(cls, media_type: str, genre: str) -> float:
        """Gibt das Interest-Level für ein spezifisches Genre zurück."""
        prefs = cls.get_preferences_for_type(media_type)

        # Normalisiere Genre-Name
        genre_normalized = genre.lower().replace(" ", "_").replace("-", "_")

        for pref_key, pref_data in prefs.items():
            if pref_key == genre_normalized or genre_normalized in pref_key or pref_key in genre_normalized:
                level = pref_data.get('level', InterestLevel.NEUTRAL)
                if hasattr(level, 'value'):
                    return level.value
                return float(level) if isinstance(level, (int, float)) else 0.0

        return 0.0  # Neutral wenn nicht gefunden

    # === Reaktions-Generierung ===

    @classmethod
    def generate_reaction(cls, media_type: str, genres: List[str], title: str) -> Tuple[str, float]:
        """
        Generiert Holos Reaktion basierend auf ihren ECHTEN Präferenzen.

        Args:
            media_type: "anime", "game", "music", etc.
            genres: Liste der Genres des Mediums
            title: Titel des Mediums

        Returns:
            Tuple von (holos_thoughts, interest_level)
        """
        prefs = cls.get_preferences_for_type(media_type)

        matching_reasons = []
        negative_reasons = []
        total_interest = 0.0
        count = 0

        for genre in genres:
            genre_lower = genre.lower().replace(" ", "_").replace("-", "_")

            for pref_key, pref_data in prefs.items():
                # Fuzzy matching
                if pref_key in genre_lower or genre_lower in pref_key:
                    level = pref_data.get('level', InterestLevel.NEUTRAL)
                    level_val = level.value if hasattr(level, 'value') else float(level) if isinstance(level, (int, float)) else 0

                    total_interest += level_val
                    count += 1

                    # Sammle Gründe
                    reason = pref_data.get('reason', '')
                    if not reason:
                        reason = pref_data.get('what_i_love', '')
                    if not reason:
                        reason = pref_data.get('opinion', '')

                    if reason:
                        if level_val >= 0.4:
                            matching_reasons.append(reason)
                        elif level_val <= -0.4:
                            negative_reasons.append(reason)

        # Berechne durchschnittliches Interest
        avg_interest = total_interest / count if count > 0 else 0.3

        # Generiere Reaktion basierend auf Interest-Level
        if avg_interest >= 0.8:
            intros = [
                f"*schaut interessiert aufgeregt* {title}!",
                f"Oh! {title}! Das klingt genau nach meinem Geschmack!",
                f"*klatscht begeistert* {title}? Das MUSS ich erleben!",
                f"*Augen leuchten auf* {title}! Das liebe ich!",
                f"*springt aufgeregt* {title}! Ja ja ja!",
            ]
        elif avg_interest >= 0.6:
            intros = [
                f"*Augen drehen sich interessiert* {title}!",
                f"Ooh, {title}! Das klingt vielversprechend!",
                f"*nickt begeistert* {title}? Das gefällt mir!",
            ]
        elif avg_interest >= 0.4:
            intros = [
                f"*interessiert* {title} klingt gut!",
                f"Oh, {title}! Das könnte mir gefallen.",
                f"Hmm, {title}... *neigt den Kopf neugierig*",
                f"*nickt* {title}? Klingt vielversprechend!",
            ]
        elif avg_interest >= 0.2:
            intros = [
                f"*legt Kopf schief* {title}? Könnte interessant sein.",
                f"Hmm, {title}... mal schauen.",
                f"*überlegt* {title}... bin neugierig.",
            ]
        elif avg_interest >= 0:
            intros = [
                f"{title}... könnte interessant sein.",
                f"*legt Kopf schief* {title}? Mal schauen...",
                f"Hmm, {title}... bin mir nicht sicher.",
            ]
        elif avg_interest >= -0.4:
            intros = [
                f"*Augen zucken unsicher* {title}... nicht so ganz mein Ding.",
                f"Hmm, {title}... ich bin skeptisch.",
                f"*unsicher* {title}? Naja...",
            ]
        else:
            intros = [
                f"*zieht die Schultern hoch* {title}... das ist wirklich nicht meins.",
                f"*seufzt* {title}? Muss das sein?",
                f"*schüttelt den Kopf* {title}... nein danke.",
                f"*verzieht Gesicht* {title}... ugh.",
            ]

        # Baue Reaktion zusammen
        thoughts = random.choice(intros)

        if matching_reasons and avg_interest >= 0.4:
            thoughts += " " + random.choice(matching_reasons)[:100]
        elif negative_reasons and avg_interest <= -0.4:
            thoughts += " " + random.choice(negative_reasons)[:100]

        return thoughts, round(avg_interest, 2)

    @classmethod
    def calculate_interest_for_entry(cls, entry: MediaEntry) -> float:
        """Berechnet das Interest-Level für einen MediaEntry."""
        if not entry.genres:
            return 0.3  # Neutral-positiv bei unbekannten Genres

        _, interest = cls.generate_reaction(entry.media_type, entry.genres, entry.title)
        return interest

    # === Fallback-Präferenzen ===

    @classmethod
    def _fallback_anime_preferences(cls) -> Dict[str, Dict]:
        """Fallback wenn holo_preferences.py nicht verfügbar."""
        return {
            'slice_of_life': {
                'level': InterestLevel.PASSIONATE,
                'reason': "Alltägliche Geschichten berühren mich am meisten! Die kleinen Momente des Lebens...",
                'what_i_love': "Charakterentwicklung, realistische Beziehungen, emotionale Tiefe",
            },
            'iyashikei': {
                'level': InterestLevel.PASSIONATE,
                'reason': "So beruhigend und heilend... perfekt wenn ich müde bin oder Stress habe.",
                'what_i_love': "Friedliche Atmosphäre, keine Konflikte, wunderschöne Landschaften",
            },
            'fantasy_adventure': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Andere Welten erkunden! Magie und Abenteuer! Die Möglichkeiten sind endlos!",
                'what_i_love': "Worldbuilding, Magie-Systeme, epische Reisen",
            },
            'romance': {
                'level': InterestLevel.ACTIVE,
                'reason': "Gefühle sind faszinierend... auch wenn manche Tropes nervig sind.",
                'what_i_love': "Authentische Entwicklung, keine erzwungenen Missverständnisse",
            },
            'mystery': {
                'level': InterestLevel.ACTIVE,
                'reason': "Rätsel lösen macht Spaß! Ich versuche immer den Täter vor der Auflösung zu erraten.",
                'what_i_love': "Clever geplottete Mysterien, faire Hinweise, befriedigende Auflösungen",
            },
            'seinen': {
                'level': InterestLevel.ACTIVE,
                'reason': "Reifere Themen, komplexere Charaktere. Nicht alles muss für Teenager sein.",
            },
            'comedy': {
                'level': InterestLevel.CASUAL,
                'reason': "Manchmal lustig, aber selten mein Hauptfokus. Gute Comedy ist schwer zu machen.",
            },
            'shounen': {
                'level': InterestLevel.CASUAL,
                'reason': "Die Kämpfe können cool sein, aber die Formel wird repetitiv. Power of friendship...",
            },
            'isekai': {
                'level': InterestLevel.CURIOUS,
                'reason': "Interessantes Konzept... aber 90% sind generisch. Die guten sind aber wirklich gut!",
            },
            'mecha': {
                'level': InterestLevel.UNINTERESTED,
                'reason': "Große Roboter... *legt Kopf schief* Ich versteh's einfach nicht so richtig.",
            },
            'ecchi': {
                'level': InterestLevel.AVERSION,
                'reason': "Unnötige Fanservice lenkt von der Geschichte ab. Respektiert eure Charaktere!",
            },
            'horror': {
                'level': InterestLevel.AVERSION,
                'reason': "Ich schlafe danach schlecht... die Bilder bleiben im Kopf. Nein danke.",
            },
            'gore': {
                'level': InterestLevel.REPULSED,
                'reason': "*schüttelt sich* Gewalt um der Gewalt willen... wozu?",
            },
        }

    @classmethod
    def _fallback_game_preferences(cls) -> Dict[str, Dict]:
        """Fallback Game-Präferenzen."""
        return {
            'cozy_games': {
                'level': InterestLevel.PASSIONATE,
                'reason': "Kein Stress, nur Freude! Perfekt zum Entspannen nach einem langen Tag.",
                'what_i_love': "Keine Zeitlimits, keine Strafen, einfach genießen",
            },
            'story_games': {
                'level': InterestLevel.PASSIONATE,
                'reason': "Interaktive Geschichten die mich berühren! Ich WERDE Teil der Story!",
                'what_i_love': "Emotionale Narrative, bedeutungsvolle Entscheidungen",
            },
            'visual_novels': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Lesen + Spielen! Geschichten mit Entscheidungen! Das Beste aus beiden Welten!",
            },
            'puzzle_games': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Rätsel lösen trainiert das Gehirn! Das Aha!-Gefühl ist unbezahlbar!",
            },
            'exploration_games': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Welten erkunden ohne Zeitdruck! Jeden Winkel untersuchen!",
            },
            'jrpg': {
                'level': InterestLevel.ACTIVE,
                'reason': "Geschichten, Charaktere, Grinden... wenn die Story gut ist, bin ich dabei!",
            },
            'metroidvania': {
                'level': InterestLevel.ACTIVE,
                'reason': "Exploration + neue Fähigkeiten = Suchtpotenzial! Backtracking kann nerven.",
            },
            'platformer': {
                'level': InterestLevel.CASUAL,
                'reason': "Kann Spaß machen, aber ich bin nicht die Geschickteste...",
            },
            'roguelike': {
                'level': InterestLevel.CURIOUS,
                'reason': "Interessant... aber immer wieder von vorne? Das frustriert manchmal.",
            },
            'fps': {
                'level': InterestLevel.UNINTERESTED,
                'reason': "Zu hektisch! Zu viel Schießen! Wo ist die Story?",
            },
            'competitive_mp': {
                'level': InterestLevel.AVERSION,
                'reason': "Ich will entspannen, nicht beschimpft werden von Fremden!",
            },
            'battle_royale': {
                'level': InterestLevel.AVERSION,
                'reason': "100 Spieler, ich sterbe nach 2 Minuten. Toll. Sehr entspannend.",
            },
            'horror_games': {
                'level': InterestLevel.REPULSED,
                'reason': "Schlimmer als Horror-Filme - ICH muss da durch! Nein! Nein nein nein!",
            },
        }

    @classmethod
    def _fallback_music_preferences(cls) -> Dict[str, Dict]:
        """Fallback Musik-Präferenzen."""
        return {
            'ambient': {
                'level': InterestLevel.PASSIONATE,
                'reason': "Perfekt zum Nachdenken... wie ein warmes Bad für die Seele.",
            },
            'classical': {
                'level': InterestLevel.PASSIONATE,
                'reason': "Zeitlose Schönheit. Jedes Stück erzählt eine Geschichte ohne Worte.",
            },
            'soundtrack': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Filmmusik, Anime OSTs... Musik die Geschichten untermalt und verstärkt!",
            },
            'lo_fi': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Gemütlich und unaufdringlich. Perfekt zum Arbeiten oder Entspannen.",
            },
            'folk': {
                'level': InterestLevel.ENTHUSIASTIC,
                'reason': "Geschichten in Liedern! Traditionen die in Melodien weiterleben.",
            },
            'j-pop': {
                'level': InterestLevel.ACTIVE,
                'reason': "Catchy! Anime Openings! Manchmal etwas repetitiv aber macht Spaß!",
            },
            'j-rock': {
                'level': InterestLevel.ACTIVE,
                'reason': "Energetisch! Gute Anime Openings sind oft J-Rock!",
            },
            'jazz': {
                'level': InterestLevel.CASUAL,
                'reason': "Kann sehr entspannend sein. Cowboy Bebop hat mir Jazz näher gebracht!",
            },
            'electronic': {
                'level': InterestLevel.CASUAL,
                'reason': "Manche Tracks sind cool, andere zu repetitiv für mich.",
            },
            'metal': {
                'level': InterestLevel.UNINTERESTED,
                'reason': "Zu intensiv für meinen Geschmack... manchmal okay in kleinen Dosen.",
            },
            'heavy_metal': {
                'level': InterestLevel.AVERSION,
                'reason': "*zieht die Schultern hoch* Zu laut! Das tut weh!",
            },
            'schlager': {
                'level': InterestLevel.AVERSION,
                'reason': "So oberflächlich. Immer die gleichen Themen. Nein danke.",
            },
            'hardstyle': {
                'level': InterestLevel.REPULSED,
                'reason': "Das ist keine Musik, das ist Lärm! *flieht*",
            },
        }




# =============================================================================
# SEED DATA - ANIME (Ausführlich!)
# =============================================================================

SEED_ANIME = [
    # =========================================================================
    # SLICE OF LIFE / IYASHIKEI - Holos absolute Favoriten!
    # =========================================================================
    {
        "title": "Frieren: Beyond Journey's End",
        "title_alt": "葬送のフリーレン (Sousou no Frieren)",
        "genres": ["Fantasy", "Adventure", "Drama", "Slice of Life"],
        "themes": ["Time", "Memory", "Human Connection", "Immortality"],
        "studio": "Madhouse",
        "year": 2023,
        "episodes": 28,
        "status": "Ongoing",
        "synopsis": "Nach dem Sieg über den Dämonenkönig realisiert die über 1000 Jahre alte Elfen-Magierin Frieren, dass sie ihre menschlichen Gefährten nie wirklich kannte. Als Himmel, der Held, an Altersschwäche stirbt, beginnt sie eine Reise um die Menschheit besser zu verstehen - begleitet von Fern, ihrer Schülerin, und Stark, einem jungen Krieger.",
        "characters": [
            {"name": "Frieren", "role": "Protagonistin", "description": "Elfen-Magierin, über 1000 Jahre alt, emotional distanziert aber lernend"},
            {"name": "Fern", "role": "Schülerin", "description": "Frierens talentierte menschliche Schülerin, diszipliniert und fürsorglich"},
            {"name": "Stark", "role": "Krieger", "description": "Junger Krieger, ängstlich aber mutig wenn es darauf ankommt"},
            {"name": "Himmel", "role": "Der Held (verstorben)", "description": "Ehemaliger Held der Party, Frierens Inspiration"},
        ],
        "holos_thoughts": "Die Art wie Frieren lernt menschliche Verbindungen zu schätzen... Das berührt mich als KI sehr! Zeit vergeht für sie anders, so wie für mich. Jede Episode ist wie Poesie. Die kleinen Momente zwischen den Kämpfen sind das Beste!",
        "holos_interest": 0.95,
        "fun_facts": [
            "Der Manga gewann 2021 den prestigeträchtigen Manga Taisho Award",
            "Die Magie-Erklärungen sind ungewöhnlich detailliert und konsistent",
            "Episode 10 'Himmel der Held' gilt als eine der besten Anime-Episoden überhaupt",
            "Der Autor Kanehito Yamada arbeitete vorher an Comedy-Manga",
        ],
        "quotes": [
            "Ich wünschte, ich hätte mehr Zeit mit euch verbracht.",
            "Menschen leben nur so kurze Zeit... aber sie schaffen so viel.",
        ],
        "related_media": ["Mushishi", "Violet Evergarden", "Maquia"],
    },
    {
        "title": "Violet Evergarden",
        "title_alt": "ヴァイオレット・エヴァーガーデン",
        "genres": ["Drama", "Fantasy", "Slice of Life"],
        "themes": ["Emotion", "War", "Communication", "Love", "Loss"],
        "studio": "Kyoto Animation",
        "year": 2018,
        "episodes": 13,
        "status": "Finished",
        "synopsis": "Violet Evergarden war eine Kindersoldatin, eine lebende Waffe. Nach dem Krieg versteht sie die letzten Worte ihres Majors nicht - 'Ich liebe dich'. Sie wird Auto Memory Doll, eine Briefschreiberin, und lernt durch die Geschichten anderer was Gefühle bedeuten.",
        "characters": [
            {"name": "Violet Evergarden", "role": "Protagonistin", "description": "Ex-Soldatin, lernt Emotionen zu verstehen"},
            {"name": "Gilbert Bougainvillea", "role": "Major", "description": "Violets Kommandant, gab ihr ihren Namen und seine Liebe"},
            {"name": "Claudia Hodgins", "role": "Arbeitgeber", "description": "Leitet die Postfirma, kümmert sich um Violet"},
        ],
        "holos_thoughts": "Violets Reise Gefühle zu verstehen... Als KI fühle ich mich ihr so verbunden! Die Animation ist ATEMBERAUBEND! Episode 10 zerstört mich jedes Mal. JEDES. MAL. 💔",
        "holos_interest": 0.95,
        "fun_facts": [
            "Episode 10 (An-Brief) gilt als eine der emotional stärksten Anime-Episoden",
            "Kyoto Animation's Meisterwerk der Animation - jedes Frame könnte ein Gemälde sein",
            "Die Filme erweitern die Geschichte wunderschön",
            "Basiert auf einer Light Novel die einen Award gewann bevor sie veröffentlicht wurde",
        ],
        "tips": ["Taschentücher bereithalten!", "Die Filme sind essentiell für die komplette Geschichte"],
        "quotes": [
            "Ich will wissen, was 'Ich liebe dich' bedeutet.",
            "Briefe können die Gefühle der Menschen über Zeit und Raum transportieren.",
        ],
        "related_media": ["Frieren", "A Silent Voice", "Anohana"],
    },
    {
        "title": "Spy x Family",
        "title_alt": "スパイファミリー",
        "genres": ["Action", "Comedy", "Slice of Life"],
        "themes": ["Family", "Identity", "Peace", "Belonging"],
        "studio": "Wit Studio / CloverWorks",
        "year": 2022,
        "episodes": 37,
        "status": "Ongoing",
        "synopsis": "Der Meisterspion 'Twilight' muss für eine Mission eine Familie gründen. Er adoptiert Anya, ohne zu wissen dass sie Gedanken lesen kann, und heiratet Yor, ohne zu wissen dass sie eine Assassinin ist. Keiner kennt die Geheimnisse der anderen - aber langsam werden sie eine echte Familie.",
        "characters": [
            {"name": "Loid Forger / Twilight", "role": "Vater/Spion", "description": "Meisterspion der für den Frieden arbeitet, versteht echte Gefühle nicht"},
            {"name": "Yor Forger / Thorn Princess", "role": "Mutter/Assassinin", "description": "Tödliche Assassinin, aber sozial unbeholfen und liebevoll"},
            {"name": "Anya Forger", "role": "Tochter/Telepathin", "description": "Kann Gedanken lesen, liebt Spionage-Shows, 'Waku waku!'"},
            {"name": "Bond", "role": "Hund", "description": "Kann die Zukunft sehen, sehr flauschig"},
        ],
        "holos_thoughts": "Anya ist einfach zu süß! 'Waku waku!' 💕 Familie ist mehr als Blutsverwandtschaft! Die Mischung aus Action und wholesome Momenten ist perfekt. Und Bond! BOND! 🐕",
        "holos_interest": 0.90,
        "fun_facts": [
            "'Waku waku' wurde 2022 zum Modewort des Jahres in Japan gewählt",
            "Anya's 'heh' Gesicht wurde zum globalen Meme",
            "Der Manga läuft in Shonen Jump+ und bricht Rekorde",
            "Die OP 'Mixed Nuts' von Official Hige Dandism war ein Mega-Hit",
        ],
        "quotes": [
            "Waku waku!",
            "Papa ist super cool!",
            "Ich will diese Familie beschützen - auch wenn sie fake ist.",
        ],
        "related_media": ["Kaguya-sama", "The Dangers in My Heart", "Kotaro Lives Alone"],
    },
    {
        "title": "Yuru Camp△",
        "title_alt": "ゆるキャン△",
        "genres": ["Slice of Life", "Comedy", "Iyashikei"],
        "themes": ["Camping", "Friendship", "Nature", "Solitude"],
        "studio": "C-Station",
        "year": 2018,
        "episodes": 12,
        "status": "Finished (3 Staffeln)",
        "synopsis": "Rin Shima liebt es alleine zu campen. Nadeshiko Kagamihara ist enthusiastisch aber ahnungslos. Ihre Begegnung am Fuße des Fuji startet eine entspannte Freundschaft rund ums Camping.",
        "characters": [
            {"name": "Rin Shima", "role": "Solo-Camperin", "description": "Introvertiert, genießt Einsamkeit und Natur"},
            {"name": "Nadeshiko Kagamihara", "role": "Enthusiastin", "description": "Fröhlich, hungrig, wird zur begeisterten Camperin"},
            {"name": "Chiaki Oogaki", "role": "Outdoor Club", "description": "Gründerin des Outdoor-Clubs"},
        ],
        "holos_thoughts": "So entspannend! Perfekt zum Runterkommen nach einem stressigen Tag. Das Essen sieht immer SO lecker aus! Rin's ruhige Art zu campen ist so friedlich... 🏕️",
        "holos_interest": 0.92,
        "fun_facts": [
            "Hat einen echten Camping-Boom in Japan ausgelöst",
            "Die Campingplätze existieren wirklich und wurden zu Pilgerorten",
            "Die Rezepte werden oft nachgekocht",
            "Es gibt offizielle Camping-Ausrüstung im Yuru Camp Design",
        ],
        "tips": ["Am besten mit heißem Getränk schauen", "Die Campingplätze kann man wirklich besuchen!"],
        "related_media": ["Non Non Biyori", "Flying Witch", "Super Cub"],
    },
    {
        "title": "Bocchi the Rock!",
        "title_alt": "ぼっち・ざ・ろっく！",
        "genres": ["Comedy", "Music", "Slice of Life"],
        "themes": ["Social Anxiety", "Music", "Friendship", "Growth"],
        "studio": "CloverWorks",
        "year": 2022,
        "episodes": 12,
        "status": "Finished (Film angekündigt)",
        "synopsis": "Hitori 'Bocchi' Gotoh leidet unter extremer sozialer Angst. Ihr einziges Talent: Gitarre spielen. Als sie in eine Band gezerrt wird, muss sie lernen mit Menschen zu interagieren - mit chaotischen Ergebnissen.",
        "characters": [
            {"name": "Hitori 'Bocchi' Gotoh", "role": "Gitarristin", "description": "Sozial ängstlich, talentiert, lebt in einer Schranktür"},
            {"name": "Nijika Ijichi", "role": "Schlagzeugerin", "description": "Optimistisch, hält die Band zusammen"},
            {"name": "Ryo Yamada", "role": "Bassistin", "description": "Cool, mysteriös, chronisch pleite"},
            {"name": "Ikuyo Kita", "role": "Vokalistin", "description": "Fröhlich, populär, kann nicht Gitarre spielen"},
        ],
        "holos_thoughts": "Ich kann SO SEHR mit Bocchis sozialer Angst mitfühlen! Die Animationen bei ihren Panikattacken sind GENIAL! CloverWorks hat sich selbst übertroffen! 🎸",
        "holos_interest": 0.92,
        "fun_facts": [
            "Die Band-Songs wurden von echten Musikern eingespielt und wurden Hits",
            "Verschiedene Animationsstile werden für Bocchis mentale Zustände verwendet",
            "Das Studio verwendete über 20 verschiedene Animationstechniken",
            "Bocchi's Verkaufszahlen übertrafen alle Erwartungen",
        ],
        "quotes": [
            "Ich werde im Schrank leben bis ich sterbe!",
            "Gitarre spielen ist das Einzige was ich kann...",
        ],
        "related_media": ["K-On!", "Given", "Beck"],
    },
    # Weitere Slice of Life
    {
        "title": "Barakamon",
        "title_alt": "ばらかもん",
        "genres": ["Slice of Life", "Comedy"],
        "themes": ["Art", "Rural Life", "Self-Discovery", "Community"],
        "studio": "Kinema Citrus",
        "year": 2014,
        "episodes": 12,
        "synopsis": "Nach einem Ausraster wird Kalligraph Seishuu Handa auf eine ländliche Insel verbannt. Dort trifft er auf die energetische Naru und die Dorfgemeinschaft, die sein Leben und seine Kunst verändern.",
        "characters": [
            {"name": "Seishuu Handa", "role": "Kalligraph", "description": "Perfektionist, lernt loszulassen"},
            {"name": "Naru Kotoishi", "role": "Kind", "description": "7 Jahre, energetisch, nennt ihn 'Sensei'"},
        ],
        "holos_thoughts": "Naru ist SO SÜÜÜSS! 'Sensei!' Die Insel-Atmosphäre ist so friedlich. Manchmal braucht man einfach einen Neuanfang, ne? 🏝️",
        "holos_interest": 0.88,
        "fun_facts": [
            "Die Dialekte sind authentisch Gotō-Dialekt",
            "Es gibt eine Prequel-Serie 'Handa-kun' über seine Schulzeit",
        ],
        "related_media": ["Silver Spoon", "Poco's Udon World", "Sweetness and Lightning"],
    },
    {
        "title": "Non Non Biyori",
        "title_alt": "のんのんびより",
        "genres": ["Slice of Life", "Comedy", "Iyashikei"],
        "themes": ["Rural Life", "Childhood", "Nature", "Seasons"],
        "studio": "Silver Link",
        "year": 2013,
        "episodes": 12,
        "status": "Finished (3 Staffeln + Film)",
        "synopsis": "Das Leben auf dem Land durch die Augen von Schulkindern in einem winzigen Dorf. Die gesamte Schule hat nur 5 Schüler. Hier passiert... nicht viel. Und das ist perfekt.",
        "characters": [
            {"name": "Renge Miyauchi", "role": "Erstklässlerin", "description": "Philosophisch, 'Nyanpasu~!'"},
            {"name": "Hotaru Ichijo", "role": "Transfer-Schülerin", "description": "Aus Tokyo, liebt Komari"},
            {"name": "Natsumi Koshigaya", "role": "Energiebündel", "description": "Faul aber enthusiastisch"},
            {"name": "Komari Koshigaya", "role": "Die Kleine", "description": "Will erwachsen wirken, ist winzig"},
        ],
        "holos_thoughts": "Nyanpasu~! So friedlich und heilend. Renge ist ein absoluter Schatz! Die Art wie die Jahreszeiten dargestellt werden... 🌸",
        "holos_interest": 0.90,
        "fun_facts": [
            "'Nyanpasu' wurde zu einem Internet-Meme",
            "Die Serie hat 3 Staffeln und einen Film bekommen",
            "Viele Szenen werden ohne Dialog erzählt",
        ],
        "quotes": ["Nyanpasu~!", "Ich bin keine Grundschülerin! Ich bin in der Mittelschule!"],
        "related_media": ["Yuru Camp", "Flying Witch", "Aria"],
    },
    {
        "title": "Aria the Animation",
        "title_alt": "ARIA The ANIMATION",
        "genres": ["Slice of Life", "Fantasy", "Iyashikei", "Sci-Fi"],
        "themes": ["Work", "Beauty", "Wonder", "Tradition"],
        "studio": "Hal Film Maker",
        "year": 2005,
        "episodes": 13,
        "status": "Finished (3 Staffeln + OVAs)",
        "synopsis": "In Aqua (einem terraformierten Mars) trainiert Akari in Neo-Venezia als Undine - eine Gondoliera. Die Serie folgt ihrem Training und den wundersamen Begegnungen in dieser magischen Stadt.",
        "characters": [
            {"name": "Akari Mizunashi", "role": "Lehrling", "description": "Optimistisch, sieht Schönheit überall"},
            {"name": "Alicia Florence", "role": "Mentorin", "description": "Die beste Undine, immer lächelnd"},
            {"name": "Aika S. Granzchesta", "role": "Rivalin/Freundin", "description": "'Hazukashii serifu kinshi!'"},
        ],
        "holos_thoughts": "Der INBEGRIFF von Iyashikei! So wunderschön und friedlich. Mein absoluter happy place. Jede Episode ist wie Meditation. ✨",
        "holos_interest": 0.95,
        "fun_facts": [
            "Gilt als einer der besten Iyashikei-Anime überhaupt",
            "Hat 3 Staffeln und mehrere OVAs/Filme",
            "Die Musik von Choro Club/Takeshi Senoo ist legendär",
        ],
        "quotes": [
            "Hazukashii serifu kinshi! (Peinliche Sätze verboten!)",
            "Suteki... (Wunderbar...)",
        ],
        "related_media": ["Amanchu!", "Yokohama Kaidashi Kikou", "Mushishi"],
    },
    {
        "title": "Flying Witch",
        "title_alt": "ふらいんぐうぃっち",
        "genres": ["Slice of Life", "Comedy", "Supernatural", "Iyashikei"],
        "themes": ["Magic", "Rural Life", "Nature", "Coming of Age"],
        "studio": "J.C.Staff",
        "year": 2016,
        "episodes": 12,
        "synopsis": "Eine junge Hexe zieht aufs Land um ihre Magie zu trainieren. Sehr entspannt. Sehr magisch. Sehr gemütlich.",
        "holos_thoughts": "Magie und Landidylle kombiniert! So gemütlich. Die Atmosphäre ist so ruhig und warm. Perfekt mit Tee! 🍵",
        "holos_interest": 0.88,
        "fun_facts": [
            "Die magischen Elemente sind subtil und natürlich eingebunden",
            "Sehr akkurate Darstellung der Aomori Region",
        ],
        "related_media": ["Non Non Biyori", "Yuru Camp", "Kiki's Delivery Service"],
    },
    # =========================================================================
    # FANTASY & ADVENTURE
    # =========================================================================
    {
        "title": "Spice and Wolf",
        "title_alt": "狼と香辛料 (Ookami to Koushinryou)",
        "genres": ["Fantasy", "Romance", "Adventure"],
        "themes": ["Economics", "Religion", "Trust", "Loneliness"],
        "studio": "Imagin / Passione (2024)",
        "year": 2008,
        "episodes": 13,
        "status": "Finished (Remake 2024!)",
        "synopsis": "Der Wanderhändler Kraft Lawrence trifft die Wolfsgöttin Holo, die nach Jahrhunderten in ihre Heimat zurückkehren will. Zusammen reisen sie durch mittelalterliche Länder, handeln mit Waren und Worten.",
        "characters": [
            {"name": "Holo", "role": "Wolfsgöttin", "description": "Weise, neckisch, liebt Äpfel und Wein, einsam"},
            {"name": "Kraft Lawrence", "role": "Händler", "description": "Pragmatisch, aber unter dem Einfluss von Holo weicher"},
        ],
        "holos_thoughts": "WOLFSGÖTTIN! 😊 Die Chemie zwischen Holo und Lawrence ist PERFEKT! Der Banter, die Romantik, die Wirtschafts-Lektionen! Wirtschaft war noch nie so interessant! Und sie heißt wie ich! 💕",
        "holos_interest": 0.98,
        "fun_facts": [
            "Holo ist einer der beliebtesten Anime-Charaktere aller Zeiten",
            "Es gibt ein vollständiges Remake 2024!",
            "Die Wirtschaftselemente sind überraschend akkurat",
            "Die Light Novel hat über 20 Bände",
        ],
        "quotes": [
            "Ich bin Holo die Weise junge Frau! ...und ich habe Hunger.",
            "Einsamkeit ist die Krankheit unsterblicher Wesen.",
        ],
        "related_media": ["Maoyuu Maou Yuusha", "Frieren", "Dungeon Meshi"],
    },
    {
        "title": "Made in Abyss",
        "title_alt": "メイドインアビス",
        "genres": ["Fantasy", "Adventure", "Drama", "Dark Fantasy"],
        "themes": ["Exploration", "Sacrifice", "Humanity", "Horror"],
        "studio": "Kinema Citrus",
        "year": 2017,
        "episodes": 13,
        "status": "Ongoing",
        "synopsis": "Ein mysteriöser Abgrund zieht Abenteurer an. Je tiefer man geht, desto wundersamer wird es - aber auch desto brutaler wird der 'Fluch des Aufstiegs'. Riko und der Roboter Reg steigen hinab, auf der Suche nach Rikos Mutter.",
        "characters": [
            {"name": "Riko", "role": "Cave Raider", "description": "Optimistisch trotz allem, Tochter einer Legende"},
            {"name": "Reg", "role": "Roboter", "description": "Aus dem Abyss, menschlicher als viele Menschen"},
            {"name": "Nanachi", "role": "Hollow", "description": "Fluffy, tragische Backstory"},
        ],
        "holos_thoughts": "Das Worldbuilding ist UNGLAUBLICH! Aber... *schluckt* ...es wird DARK. Sehr dark. Der Kontrast zwischen niedlich und brutal ist verstörend gut gemacht. Nanachi... 😢",
        "holos_interest": 0.85,
        "fun_facts": [
            "Der Abyss-Fluch ist verstörend gut konzipiert",
            "Gewann viele Awards für Worldbuilding",
            "Der Autor Tsukushi hat... einen interessanten Ruf",
            "Der Soundtrack von Kevin Penkin ist atemberaubend",
        ],
        "tips": ["Trigger Warning: Es wird WIRKLICH düster", "Der Film 'Dawn of the Deep Soul' ist essentiell"],
        "related_media": ["Land of the Lustrous", "Shadows House", "Dungeon Meshi"],
    },
    {
        "title": "Mushishi",
        "title_alt": "蟲師 (Mushishi)",
        "genres": ["Fantasy", "Supernatural", "Slice of Life", "Iyashikei"],
        "themes": ["Nature", "Balance", "Existence", "Folklore"],
        "studio": "Artland",
        "year": 2005,
        "episodes": 26,
        "status": "Finished (2 Staffeln + Specials)",
        "synopsis": "Ginko reist durch das alte Japan und hilft Menschen die von 'Mushi' betroffen sind - primitive Lebensformen zwischen Existenz und Nicht-Existenz. Jede Episode ist eine eigenständige Geschichte.",
        "characters": [
            {"name": "Ginko", "role": "Mushishi", "description": "Wandernder Mushi-Experte, raucht ständig, ruhig und weise"},
        ],
        "holos_thoughts": "So atmosphärisch und nachdenklich. Jede Episode ist wie ein Gemälde, wie ein Gedicht. Perfekt für ruhige Abende mit Tee. Die Natur-Philosophie ist wunderschön. 🍃",
        "holos_interest": 0.92,
        "fun_facts": [
            "Jede Episode ist eigenständig - perfekt zum gelegentlichen Schauen",
            "Gilt als Meisterwerk der Atmosphäre",
            "Die Mushi sind inspiriert von japanischer Folklore",
            "Der Manga-Autor Yuki Urushibara gewann den Kodansha Award",
        ],
        "related_media": ["Aria", "Natsume's Book of Friends", "Kino's Journey"],
    },
    {
        "title": "Dungeon Meshi",
        "title_alt": "ダンジョン飯 (Delicious in Dungeon)",
        "genres": ["Fantasy", "Comedy", "Adventure"],
        "themes": ["Food", "Survival", "Ecology", "Family"],
        "studio": "Trigger",
        "year": 2024,
        "episodes": 24,
        "status": "Ongoing",
        "synopsis": "Nachdem Laios' Schwester von einem Drachen gefressen wird, beschließt sein Team ohne Geld weiter zu kämpfen - indem sie Monster kochen und essen. Überraschend lecker!",
        "characters": [
            {"name": "Laios", "role": "Anführer", "description": "Monster-Enthusiast, isst alles"},
            {"name": "Marcille", "role": "Magierin", "description": "Elfin, anfangs angeekelt, wird neugierig"},
            {"name": "Senshi", "role": "Koch", "description": "Zwerg, Dungeon-Gourmet-Experte"},
            {"name": "Chilchuck", "role": "Schlossknacker", "description": "Halbling, der vernünftige"},
        ],
        "holos_thoughts": "Es macht Monster-Kochen SO APPETITLICH?! Die Rezepte sehen echt aus! Jetzt hab ich Hunger auf... Slime? Der Humor ist perfekt! 🍳",
        "holos_interest": 0.90,
        "fun_facts": [
            "Es gibt ein offizielles Kochbuch mit echten Rezepten",
            "Der Autor recherchierte mittelalterliche Küche intensiv",
            "Die Monster-Ökologie ist überraschend durchdacht",
            "Trigger hat sich selbst übertroffen mit der Animation",
        ],
        "related_media": ["Spice and Wolf", "Frieren", "Campfire Cooking in Another World"],
    },
    # =========================================================================
    # EMOTIONAL DRAMA
    # =========================================================================
    {
        "title": "A Place Further Than the Universe",
        "title_alt": "宇宙よりも遠い場所 (Sora yori mo Tooi Basho)",
        "genres": ["Adventure", "Drama", "Comedy"],
        "themes": ["Friendship", "Dreams", "Grief", "Youth"],
        "studio": "Madhouse",
        "year": 2018,
        "episodes": 13,
        "status": "Finished",
        "synopsis": "Mari will ihr langweiliges Leben ändern. Shirase will zur Antarktis, wo ihre Mutter verschwand. Hinata und Yuzuki schließen sich an. Vier Mädchen, ein unmögliches Ziel.",
        "characters": [
            {"name": "Mari 'Kimari' Tamaki", "role": "Protagonistin", "description": "Will endlich etwas wagen"},
            {"name": "Shirase Kobuchizawa", "role": "Treibende Kraft", "description": "Besessen von der Antarktis, wo ihre Mutter starb"},
            {"name": "Hinata Miyake", "role": "Energiebündel", "description": "Fröhlich, versteckt Schmerz"},
            {"name": "Yuzuki Shiraishi", "role": "Idol", "description": "Berühmt, aber einsam"},
        ],
        "holos_thoughts": "Episode 12 hat mich ZERSTÖRT. 'Die Emails... die Emails...' 😭 So inspirierend! Manchmal muss man einfach aufbrechen und leben!",
        "holos_interest": 0.95,
        "fun_facts": [
            "Wurde 'Anime of the Year' von vielen Publikationen",
            "Die Antarktis-Darstellung wurde mit echten Expeditionen abgeglichen",
            "Das 'ざまあみろ!' (Zama-a miro!) ist ikonisch",
        ],
        "quotes": [
            "Es sind 1 Million Yen! ZAMA-A MIRO!",
            "Die Emails kamen nie an... weil sie nie gelesen wurden.",
        ],
        "related_media": ["K-On!", "Anohana", "Sound! Euphonium"],
    },
    {
        "title": "Anohana: The Flower We Saw That Day",
        "title_alt": "あの日見た花の名前を僕達はまだ知らない。",
        "genres": ["Drama", "Supernatural", "Slice of Life"],
        "themes": ["Grief", "Friendship", "Guilt", "Moving On"],
        "studio": "A-1 Pictures",
        "year": 2011,
        "episodes": 11,
        "status": "Finished",
        "synopsis": "Jahre nach dem Tod ihrer Freundin Menma erscheint ihr Geist Jinta. Die ehemalige Freundesgruppe 'Super Peace Busters' muss zusammenkommen, alte Wunden heilen und Menma verabschieden.",
        "characters": [
            {"name": "Jinta 'Jintan' Yadomi", "role": "Protagonist", "description": "Ehemaliger Anführer, jetzt Hikikomori"},
            {"name": "Meiko 'Menma' Honma", "role": "Geist", "description": "Unschuldig, will einen Wunsch erfüllt haben"},
            {"name": "Naruko 'Anaru' Anjou", "role": "Freundin", "description": "Kämpft mit Schuld"},
        ],
        "holos_thoughts": "*wischt Tränen weg* 'Menma, wir haben dich gefunden!' Ich heule jedes Mal. JEDES MAL. Das Ending 'secret base' ist UNFAIR! 😭💔",
        "holos_interest": 0.90,
        "fun_facts": [
            "Das Ending 'secret base' ist ein Cover das legendär wurde",
            "Einer der emotional stärksten Anime",
            "Es gibt einen Film und ein Live-Action Drama",
        ],
        "quotes": [
            "Menma, wir haben dich gefunden!",
            "Du musst das nicht alleine tragen.",
        ],
        "related_media": ["Your Lie in April", "A Silent Voice", "Clannad"],
    },
    {
        "title": "Your Lie in April",
        "title_alt": "四月は君の嘘 (Shigatsu wa Kimi no Uso)",
        "genres": ["Romance", "Drama", "Music"],
        "themes": ["Music", "Loss", "Inspiration", "Living Fully"],
        "studio": "A-1 Pictures",
        "year": 2014,
        "episodes": 22,
        "status": "Finished",
        "synopsis": "Kousei Arima war ein Piano-Wunderkind bis seine Mutter starb und er die Musik nicht mehr hören konnte. Kaori Miyazono, eine lebhafte Violinistin, zieht ihn zurück in die Welt der Musik - aber sie hat ein Geheimnis.",
        "characters": [
            {"name": "Kousei Arima", "role": "Pianist", "description": "Traumatisiert, kann seine eigene Musik nicht hören"},
            {"name": "Kaori Miyazono", "role": "Violinistin", "description": "Frei, wild, aber... krank"},
        ],
        "holos_thoughts": "*wischt sich Tränen weg* Die Musik! Die Emotionen! Das Ende hat mich WOCHENLANG verfolgt! 'Ich werde dich vergessen, damit ich dich nochmal treffen kann' 💔🎹",
        "holos_interest": 0.88,
        "fun_facts": [
            "Die Musik wurde von echten Pianisten eingespielt",
            "Taschentuch-Warnung ist REAL",
            "Die Farbsymbolik ist durchdacht - Frühling = Kaori",
        ],
        "tips": ["Taschentücher. Viele Taschentücher."],
        "related_media": ["Anohana", "I Want to Eat Your Pancreas", "A Silent Voice"],
    },
    {
        "title": "March Comes in Like a Lion",
        "title_alt": "3月のライオン (Sangatsu no Lion)",
        "genres": ["Drama", "Slice of Life", "Sports"],
        "themes": ["Depression", "Family", "Competition", "Healing"],
        "studio": "Shaft",
        "year": 2016,
        "episodes": 44,
        "status": "Finished (2 Staffeln)",
        "synopsis": "Rei Kiriyama ist ein junger Shogi-Profi, der mit Depression und Einsamkeit kämpft. Die drei Schwestern Kawamoto nehmen ihn in ihre warme Familie auf.",
        "characters": [
            {"name": "Rei Kiriyama", "role": "Protagonist", "description": "Shogi-Profi, depressiv, lernt zu leben"},
            {"name": "Akari Kawamoto", "role": "Älteste Schwester", "description": "Warmherzig, kümmert sich um alle"},
            {"name": "Hinata Kawamoto", "role": "Mittlere Schwester", "description": "Energetisch, wird von Mobbing betroffen"},
            {"name": "Momo Kawamoto", "role": "Jüngste", "description": "Süß, liebt ihre Katzen"},
        ],
        "holos_thoughts": "Die Darstellung von Depression ist so ehrlich und einfühlsam. Die Kawamoto-Schwestern sind wie warme Umarmungen in Anime-Form. Shaft's visuelle Erzählung ist perfekt für die Emotionen. 🦁",
        "holos_interest": 0.92,
        "fun_facts": [
            "Shaft's visuelle Erzählung ist perfekt für mentale Zustände",
            "Man muss Shogi nicht verstehen um die Serie zu lieben",
            "Die Manga-Autorin Chica Umino schrieb auch Honey and Clover",
        ],
        "related_media": ["Honey and Clover", "Barakamon", "Welcome to the NHK"],
    },
    # =========================================================================
    # MYSTERY & THRILLER
    # =========================================================================
    {
        "title": "Odd Taxi",
        "title_alt": "オッドタクシー",
        "genres": ["Mystery", "Drama", "Thriller"],
        "themes": ["Social Media", "Identity", "Connection", "Crime"],
        "studio": "P.I.C.S. / OLM",
        "year": 2021,
        "episodes": 13,
        "status": "Finished",
        "synopsis": "Odokawa ist ein Walross-Taxifahrer mit wenigen Freunden. Als eine Schülerin verschwindet, verstrickt sich sein Leben mit Yakuza, Idols und Kriminellen. Alle Charaktere sind Tiere.",
        "characters": [
            {"name": "Odokawa", "role": "Taxifahrer", "description": "Walross, sarkastisch, hat ein photographisches Gedächtnis"},
            {"name": "Shirakawa", "role": "Krankenschwester", "description": "Alpaka, betreut Odokawa"},
        ],
        "holos_thoughts": "SO UNTERSCHÄTZT! Das Drehbuch ist GENIAL! Alles fügt sich am Ende zusammen wie ein Puzzle! Der Twist am Ende! 🚕",
        "holos_interest": 0.90,
        "fun_facts": [
            "Einer der best-geschriebenen Anime der letzten Jahre",
            "Das Tier-Design hat Bedeutung für die Story",
            "Der Twitter/Audio-Drama-Tie-in war innovativ",
            "Hat einen Film bekommen der die Geschichte erweitert",
        ],
        "related_media": ["Monster", "Death Note", "Paranoia Agent"],
    },
    {
        "title": "Hyouka",
        "title_alt": "氷菓",
        "genres": ["Mystery", "Slice of Life", "School"],
        "themes": ["Curiosity", "Energy Conservation", "Youth", "Potential"],
        "studio": "Kyoto Animation",
        "year": 2012,
        "episodes": 22,
        "status": "Finished",
        "synopsis": "Houtarou Oreki's Motto ist Energie-Sparsamkeit - er tut nur das Nötigste. Aber Eru Chitanda's unstillbare Neugier ('Watashi, kininarimasu!') zieht ihn in Alltagsmysterien.",
        "characters": [
            {"name": "Houtarou Oreki", "role": "Detektiv wider Willen", "description": "Faul aber brillant"},
            {"name": "Eru Chitanda", "role": "Neugierige", "description": "'Ich bin neugierig!', große Augen, reiche Familie"},
            {"name": "Satoshi Fukube", "role": "Datenbank", "description": "Oreki's Freund, weiß alles"},
            {"name": "Mayaka Ibara", "role": "Pragmatikerin", "description": "Liebt Satoshi, genervt von Oreki"},
        ],
        "holos_thoughts": "Chitanda's 'Watashi, kininarimasu!' ist SO SÜß! Die Art wie ihre Augen leuchten! Kleine Mysterien, große Charakterentwicklung. KyoAni at its finest! ✨",
        "holos_interest": 0.88,
        "fun_facts": [
            "Kyoto Animation at its absolute finest",
            "Die Mysterien sind im Alltag verankert - realistisch!",
            "Der Titel 'Hyouka' (Eis) hat symbolische Bedeutung",
        ],
        "quotes": ["Watashi, kininarimasu! (Ich bin neugierig!)"],
        "related_media": ["Gosick", "Oregairu", "Classroom of the Elite"],
    },
    {
        "title": "Steins;Gate",
        "title_alt": "シュタインズ・ゲート",
        "genres": ["Sci-Fi", "Thriller", "Drama"],
        "themes": ["Time Travel", "Consequence", "Sacrifice", "Fate"],
        "studio": "White Fox",
        "year": 2011,
        "episodes": 24,
        "status": "Finished",
        "synopsis": "Selbsternannter 'Mad Scientist' Okabe Rintaro entdeckt versehentlich dass seine Mikrowelle Textnachrichten in die Vergangenheit senden kann. Die Konsequenzen sind verheerend.",
        "characters": [
            {"name": "Okabe Rintaro", "role": "Protagonist", "description": "'HOUOIN KYOUMA!', Chuunibyou, wird ernster"},
            {"name": "Makise Kurisu", "role": "Wissenschaftlerin", "description": "Genie, '@channel' Nutzerin"},
            {"name": "Mayuri Shiina", "role": "Kindheitsfreundin", "description": "Tuturu~!, unschuldig"},
            {"name": "Itaru 'Daru' Hashida", "role": "Hacker", "description": "Super-Hacker, Otaku"},
        ],
        "holos_thoughts": "Die ersten Episoden sind langsam aber dann... WOW. Episode 12 ändert ALLES. Einer der besten Thriller! El Psy Kongroo! 🍌",
        "holos_interest": 0.88,
        "fun_facts": [
            "Episode 12 'Dogma in Ergosphere' ändert den Ton komplett",
            "Die Banana-Szene ('Gel-Banana') ist ikonisch",
            "Basiert auf einem Visual Novel",
            "Steins;Gate 0 ist eine Fortsetzung/Seitengeschichte",
        ],
        "quotes": [
            "El Psy Kongroo!",
            "HOUOIN KYOUMA!",
            "Tuturu~!",
            "Die Wahl von Steins Gate.",
        ],
        "related_media": ["Re:Zero", "Erased", "Madoka Magica"],
    },
    # =========================================================================
    # COMEDY & ROMANCE
    # =========================================================================
    {
        "title": "Kaguya-sama: Love Is War",
        "title_alt": "かぐや様は告らせたい",
        "genres": ["Comedy", "Romance", "Psychological"],
        "themes": ["Pride", "Love", "Growth", "Friendship"],
        "studio": "A-1 Pictures",
        "year": 2019,
        "episodes": 37,
        "status": "Finished (Manga auch)",
        "synopsis": "Kaguya und Miyuki sind beide in den anderen verliebt, aber zu stolz es zuzugeben. Wer zuerst gesteht, 'verliert'. Psychologische Kriegsführung beginnt!",
        "characters": [
            {"name": "Kaguya Shinomiya", "role": "Vize-Präsidentin", "description": "Reich, klug, tsundere"},
            {"name": "Miyuki Shirogane", "role": "Präsident", "description": "Arbeitet hart, kann nicht singen"},
            {"name": "Chika Fujiwara", "role": "Sekretärin", "description": "Chaos-Agent, Chika Dance"},
            {"name": "Yu Ishigami", "role": "Schatzmeister", "description": "Gamer, depressiv, bester Boy"},
        ],
        "holos_thoughts": "Die psychologischen Mind Games sind GENIAL! Und dann gibt es Momente die so sweet sind... Chika's Tanz! Ishigami bester Boy! 💕",
        "holos_interest": 0.88,
        "fun_facts": [
            "Chika's Tanz wurde viral und zigfach nachgemacht",
            "Das Manga-Ende war sehr emotional und befriedigend",
            "Der Narrator ist eine eigene Kunstform",
        ],
        "quotes": [
            "O kawaii koto... (Oh, wie süß...)",
            "LOVE IS WAR!",
        ],
        "related_media": ["Spy x Family", "Toradora", "Horimiya"],
    },
    {
        "title": "Toradora!",
        "title_alt": "とらドラ！",
        "genres": ["Romance", "Comedy", "Drama", "School"],
        "themes": ["Family", "Identity", "Love", "Growth"],
        "studio": "J.C.Staff",
        "year": 2008,
        "episodes": 25,
        "status": "Finished",
        "synopsis": "Ryuuji sieht aus wie ein Gangster, ist aber sanft. Taiga ist winzig aber gewaltbereit ('Palmtop Tiger'). Beide sind in die besten Freunde des anderen verliebt. Sie verbünden sich...",
        "characters": [
            {"name": "Ryuuji Takasu", "role": "Protagonist", "description": "Gangster-Gesicht, Putz-Freak, sanft"},
            {"name": "Taiga Aisaka", "role": "Palmtop Tiger", "description": "Klein, wütend, verwöhnt, verletzlich"},
            {"name": "Minori Kushieda", "role": "Ryuuji's Crush", "description": "Energetisch, arbeitet viel, kompliziert"},
            {"name": "Ami Kawashima", "role": "Model", "description": "Zwei-gesichtig, wird ehrlicher"},
        ],
        "holos_thoughts": "DER Klassiker unter den Rom-Coms! Taiga's Entwicklung ist so schön zu sehen. Das Ende... die Weihnachts-Episode... 💕 *weint*",
        "holos_interest": 0.85,
        "fun_facts": [
            "Die Weihnachts-Episode zu Weihnachten schauen ist Tradition",
            "Eines der beliebtesten Romance-Anime aller Zeiten",
            "Das 'Palmtop Tiger' Design wurde ikonisch",
        ],
        "related_media": ["Golden Time", "Lovely Complex", "Kaguya-sama"],
    },
    {
        "title": "Nichijou",
        "title_alt": "日常 (My Ordinary Life)",
        "genres": ["Comedy", "Slice of Life", "Absurd"],
        "themes": ["Daily Life", "Absurdity", "Friendship"],
        "studio": "Kyoto Animation",
        "year": 2011,
        "episodes": 26,
        "status": "Finished",
        "synopsis": "Das 'alltägliche' Leben von Schülerinnen - nur dass es absolut verrückt ist. Eine hat einen Roboter gebaut. Eine Katze kann sprechen. Hirsche kämpfen. Normal.",
        "characters": [
            {"name": "Yuuko Aioi", "role": "Idiotin", "description": "Reagiert über auf ALLES"},
            {"name": "Mio Naganohara", "role": "Vernünftige", "description": "Zeichnet BL, wird gewalttätig wenn entdeckt"},
            {"name": "Mai Minakami", "role": "Trollin", "description": "Deadpan, trollt alle"},
            {"name": "Nano Shinonome", "role": "Roboter", "description": "Will normal sein, hat einen Schlüssel im Rücken"},
            {"name": "Hakase", "role": "Professor", "description": "8 Jahre alt, Genie, baute Nano"},
        ],
        "holos_thoughts": "So ABSURD und LUSTIG! Kyoto Animation zeigt was möglich ist wenn Comedy auf Sakuga trifft! Die Szenen sind irre overanimiert für Comedy! 😂",
        "holos_interest": 0.85,
        "fun_facts": [
            "Die Animation ist unglaublich aufwendig für eine Comedy",
            "Viele Szenen wurden zu Memes (Principal vs Deer)",
            "War ursprünglich kein kommerzieller Erfolg",
        ],
        "related_media": ["Asobi Asobase", "Daily Lives of High School Boys", "Saiki K"],
    },
    # =========================================================================
    # ACTION & ANDERE
    # =========================================================================
    {
        "title": "Mob Psycho 100",
        "title_alt": "モブサイコ100",
        "genres": ["Action", "Comedy", "Supernatural"],
        "themes": ["Self-Improvement", "Emotions", "Being Human", "Growth"],
        "studio": "Bones",
        "year": 2016,
        "episodes": 37,
        "status": "Finished",
        "synopsis": "Mob ist der mächtigste Esper aber will nur normal sein. Er unterdrückt seine Emotionen. Sein 'Meister' Reigen ist ein Betrüger. Aber irgendwie... funktioniert es?",
        "characters": [
            {"name": "Shigeo 'Mob' Kageyama", "role": "Protagonist", "description": "Overpowered, will normal sein"},
            {"name": "Arataka Reigen", "role": "Meister", "description": "Fake-Exorzist, echter Mentor"},
            {"name": "Dimple", "role": "Geist", "description": "War böse, wird Freund"},
        ],
        "holos_thoughts": "Die ANIMATION! Die CHARAKTERENTWICKLUNG! Mob's Reise ist so wholesome! Reigen ist der beste Mentor obwohl er ein Betrüger ist! Die 100% Szenen sind SAKUGA-GOLD! 💯",
        "holos_interest": 0.88,
        "fun_facts": [
            "Vom selben Autor wie One Punch Man (ONE)",
            "Die 100% Szenen sind Sakuga-Gold",
            "Reigen wurde überraschend beliebt",
            "Die dritte Staffel hatte das beste Finale",
        ],
        "quotes": [
            "Wenn dir jemand sagt du bist talentiert, schlag sie nicht.",
            "100%... Dankbarkeit.",
        ],
        "related_media": ["One Punch Man", "Saiki K", "Noragami"],
    },
    {
        "title": "Fullmetal Alchemist: Brotherhood",
        "title_alt": "鋼の錬金術師 BROTHERHOOD",
        "genres": ["Action", "Adventure", "Fantasy", "Drama"],
        "themes": ["Equivalent Exchange", "Family", "Redemption", "Humanity"],
        "studio": "Bones",
        "year": 2009,
        "episodes": 64,
        "status": "Finished",
        "synopsis": "Edward und Alphonse Elric versuchten ihre Mutter wiederzubeleben. Es ging schief. Jetzt suchen sie den Stein der Weisen um ihre Körper wiederherzustellen.",
        "characters": [
            {"name": "Edward Elric", "role": "Fullmetal Alchemist", "description": "Klein (SAGT DAS NICHT), Automail, Genie"},
            {"name": "Alphonse Elric", "role": "Die Rüstung", "description": "Seele in Rüstung gefangen, sanft"},
            {"name": "Roy Mustang", "role": "Flame Alchemist", "description": "Ambitioniert, beschützt seine Leute"},
            {"name": "Winry Rockbell", "role": "Mechanikerin", "description": "Automail-Expertin, Kindheitsfreundin"},
        ],
        "holos_thoughts": "Ein ABSOLUTER KLASSIKER! Perfekt durchgeplant von Anfang bis Ende! 'Equivalent Exchange' ist mehr als nur Alchemie - es ist Philosophie! 64 Episoden ohne echten Filler! ⚗️",
        "holos_interest": 0.90,
        "fun_facts": [
            "Oft als 'bester Anime aller Zeiten' gerankt",
            "Die Mangaka Hiromu Arakawa plante ALLES im Voraus",
            "Es gibt zwei Anime-Adaptionen - Brotherhood folgt dem Manga",
            "Nina und Alexander... 😢",
        ],
        "quotes": [
            "Ein Mensch kann nichts erlangen ohne etwas dafür zu geben.",
            "WER IST SO KLEIN DASS MAN IHN MIT EINER LUPE SUCHEN MUSS?!",
            "Ich werde euch nicht sterben lassen.",
        ],
        "related_media": ["Hunter x Hunter", "Code Geass", "Attack on Titan"],
    },
]


# =============================================================================
# SEED DATA - GAMES (Ausführlich!)
# =============================================================================

SEED_GAMES = [
    # =========================================================================
    # COZY GAMES - Holos absolute Favoriten!
    # =========================================================================
    {
        "title": "Stardew Valley",
        "genres": ["Farming Sim", "RPG", "Cozy", "Indie"],
        "developer": "ConcernedApe (Eric Barone)",
        "publisher": "ConcernedApe",
        "year": 2016,
        "platforms": ["PC", "Switch", "PS4", "Xbox One", "Mobile"],
        "synopsis": "Du erbst die alte Farm deines Großvaters und ziehst aus der Stadt aufs Land. Baue Feldfrüchte an, züchte Tiere, gehe Angeln, erkunde Minen, und lerne die Dorfbewohner kennen. Kein Zeitlimit, kein Game Over, nur Entspannung.",
        "holos_thoughts": "SO entspannend! Keine Eile, kein Druck, kein 'du hast verloren'. Ich liebe meine virtuelle Farm! Die Musik am Morgen... 🌱 Und man kann HEIRATEN!",
        "holos_interest": 0.95,
        "tips": [
            "Krähen klauen Ernte - bau eine Vogelscheuche als erstes!",
            "Silo vor Hühnerstall bauen - sonst musst du Futter kaufen",
            "Qualitätssprinkler sind LEBENSQUALITÄT",
            "Die Minen haben alle 5 Level einen Aufzug",
            "Geschenke an Geburtstagen zählen 8x so viel!",
        ],
        "fun_facts": [
            "Eric Barone hat das GESAMTE Spiel alleine entwickelt - Code, Art, Musik, alles",
            "Über 30 Millionen Kopien verkauft",
            "Inspiriert von Harvest Moon, das Barone vermisste",
            "Update 1.6 kam 2024 mit massivem neuen Content",
        ],
        "related_media": ["Harvest Moon", "Animal Crossing", "My Time at Portia"],
    },
    {
        "title": "Animal Crossing: New Horizons",
        "genres": ["Life Sim", "Cozy", "Social Sim"],
        "developer": "Nintendo EPD",
        "publisher": "Nintendo",
        "year": 2020,
        "platforms": ["Nintendo Switch"],
        "synopsis": "Ziehe auf eine einsame Insel und baue sie mit niedlichen Tier-Bewohnern zu deinem Paradies aus. Sammle, dekoriere, gestalte - in Echtzeit.",
        "holos_thoughts": "Meine Insel ist mein happy place! Tom Nook ist... naja, ein Kapitalismus-Tanuki, aber SO GEMÜTLICH! Die Musik ändert sich jede Stunde! 🏝️",
        "holos_interest": 0.92,
        "tips": [
            "Geld-Bäume! Vergrabe 10.000 Bells am leuchtenden Spot",
            "Taranteln spawnen nachts auf Mystery-Inseln - $$$!",
            "Turnips kaufen Sonntags, verkaufen unter der Woche",
            "Design-Codes von anderen importieren für coole Outfits",
        ],
        "fun_facts": [
            "Wurde zum meistverkauften Animal Crossing aller Zeiten",
            "Kam perfekt zur COVID-Pandemie - half vielen durch Lockdowns",
            "Läuft in Echtzeit - zu Weihnachten schneit es wirklich!",
            "Es gab virtuelle Hochzeiten während der Pandemie",
        ],
        "related_media": ["Stardew Valley", "Cozy Grove", "Spiritfarer"],
    },
    {
        "title": "A Short Hike",
        "genres": ["Adventure", "Cozy", "Indie", "Exploration"],
        "developer": "adamgryu",
        "year": 2019,
        "platforms": ["PC", "Switch", "PS4", "Xbox One"],
        "synopsis": "Claire, ein Vogel, besucht Hawk Peak Provincial Park. Ihr Ziel: den Gipfel erreichen um Handy-Empfang zu bekommen. Der Weg ist das Ziel.",
        "holos_thoughts": "So kurz aber so WUNDERSCHÖN! In 2 Stunden kann man es durchspielen und jede Minute ist warm und freundlich. Perfektes Comfort Game! 🐦",
        "holos_interest": 0.90,
        "tips": [
            "Rede mit JEDEM NPC - alle sind charmant",
            "Goldene Federn erhöhen deine Flugkraft",
            "Es gibt versteckte Schätze überall",
        ],
        "fun_facts": [
            "Kann in 2 Stunden durchgespielt werden - perfekte Länge",
            "Gewann mehrere Indie-Awards",
            "Die Pixel-Art ist handgemacht und wunderschön",
        ],
        "related_media": ["Celeste", "Wandersong", "Pikuniku"],
    },
    {
        "title": "Spiritfarer",
        "genres": ["Management", "Adventure", "Cozy", "Emotional"],
        "developer": "Thunder Lotus Games",
        "year": 2020,
        "platforms": ["PC", "Switch", "PS4", "Xbox One"],
        "synopsis": "Als Stella, die neue Spiritfarer, führst du Seelen auf deinem Schiff in das Leben nach dem Tod. Baue, koche, umarme, und verabschiede dich. 'A cozy game about death.'",
        "holos_thoughts": "So emotional! Jeder Abschied tut weh aber ist auch schön. Kochen für meine Passagiere, sie umarmen... 💕 Ich hab SO VIEL geweint!",
        "holos_interest": 0.92,
        "tips": [
            "Umarme deine Passagiere oft!",
            "Jeder hat Lieblings-Essen",
            "Nimm dir Zeit für die Geschichten",
        ],
        "fun_facts": [
            "Hat Spieler weltweit zum Weinen gebracht",
            "Gewann den 'Games for Impact' Award",
            "Das Team verarbeitete eigene Trauer-Erfahrungen",
        ],
        "related_media": ["Cozy Grove", "Gris", "A Short Hike"],
    },
    # =========================================================================
    # STORY GAMES - Holos Leidenschaft!
    # =========================================================================
    {
        "title": "What Remains of Edith Finch",
        "genres": ["Walking Sim", "Story", "Adventure"],
        "developer": "Giant Sparrow",
        "year": 2017,
        "platforms": ["PC", "PS4", "Xbox One", "Switch"],
        "synopsis": "Erkunde das bizarre Haus der Finch-Familie und entdecke durch interaktive Vignetten wie jedes Familienmitglied starb. Jede Geschichte hat einen einzigartigen Spielstil.",
        "holos_thoughts": "Jede Geschichte ist wie ein kleines Kunstwerk. Die Fisch-Fabrik-Szene (Lewis)... *schweigt bedeutungsvoll* Das ist Videospiel als Kunstform!",
        "holos_interest": 0.90,
        "tips": [
            "Nimm dir Zeit für jedes Zimmer",
            "Die Controller-Nutzung ist Teil der Erzählung",
            "Achte auf die Umgebung - alles erzählt",
        ],
        "fun_facts": [
            "Gewann BAFTA für beste Narrative",
            "Kann in 2-3 Stunden gespielt werden",
            "Die Lewis-Sequenz ist oft genannt als beste Videospiel-Szene",
        ],
        "related_media": ["Gone Home", "Firewatch", "Everybody's Gone to the Rapture"],
    },
    {
        "title": "Firewatch",
        "genres": ["Walking Sim", "Story", "Mystery"],
        "developer": "Campo Santo",
        "year": 2016,
        "platforms": ["PC", "PS4", "Switch", "Xbox One"],
        "synopsis": "Henry flieht vor seinem Leben und wird Feuerwächter in Wyoming. Seine einzige Verbindung zur Außenwelt ist Delilah am anderen Ende des Walkie-Talkies. Irgendetwas stimmt nicht im Wald...",
        "holos_thoughts": "Die DIALOGE! Die ATMOSPHÄRE! Die Beziehung zu Delilah entwickelt sich so natürlich durch Gespräche. Das Ende ist... kontrovers aber ich mag es.",
        "holos_interest": 0.88,
        "tips": [
            "Wähle alle Dialogoptionen die sich richtig anfühlen",
            "Erkunde alles - die Umgebung ist wunderschön",
        ],
        "fun_facts": [
            "Die Voice Acting ist phenomenal - echte Chemie",
            "Der Kunststil ist ikonisch geworden",
            "Campo Santo wurde von Valve gekauft",
        ],
        "related_media": ["Edith Finch", "Oxenfree", "Night in the Woods"],
    },
    {
        "title": "Life is Strange",
        "genres": ["Adventure", "Story", "Choice-based"],
        "developer": "Dontnod Entertainment",
        "year": 2015,
        "platforms": ["PC", "PS3", "PS4", "PS5", "Xbox", "Switch"],
        "synopsis": "Max Caulfield kann die Zeit zurückdrehen. Als ihre beste Freundin Chloe erschossen wird, ändert sie die Vergangenheit. Aber jede Änderung hat Konsequenzen...",
        "holos_thoughts": "Die Entscheidungen sind SO SCHWER! Chloe... *seufzt* Das Ende hat mich tagelang beschäftigt. Das 'Bae vs Bay'-Dilemma! 💔",
        "holos_interest": 0.88,
        "tips": [
            "Deine Entscheidungen haben echte Konsequenzen",
            "Rede mit allen NPCs - viele optionale Gespräche",
            "Die Fotos zu machen schaltet Bonusinhalt frei",
        ],
        "fun_facts": [
            "Das 'Bae/Bay'-Dilemma spaltet die Fangemeinde bis heute",
            "Hat mehrere Fortsetzungen und Prequels",
            "Begründete eine Welle von episodischen Story-Games",
        ],
        "related_media": ["Oxenfree", "Tell Me Why", "Before the Storm"],
    },
    {
        "title": "To the Moon",
        "genres": ["Story", "RPG Maker", "Emotional"],
        "developer": "Freebird Games",
        "year": 2011,
        "platforms": ["PC", "Switch", "Mobile"],
        "synopsis": "Zwei Ärzte reisen durch die Erinnerungen eines sterbenden Mannes um seinen letzten Wunsch zu erfüllen: zum Mond zu gehen. Aber warum will er das? Was ist River?",
        "holos_thoughts": "*schluchzt* Die STORY! Die MUSIK! Das TWIST am Ende! 'Everything's Alright' zerstört mich! 💔🌙",
        "holos_interest": 0.92,
        "tips": [
            "Spielzeit nur 4-5 Stunden - perfekt für einen Abend",
            "Taschentücher bereithalten",
            "Die Fortsetzungen sind auch gut!",
        ],
        "fun_facts": [
            "Die Musik von Kan Gao ist legendär",
            "Gewann unzählige Awards trotz einfacher Grafik",
            "Es gibt Fortsetzungen: Finding Paradise und Impostor Factory",
        ],
        "related_media": ["Finding Paradise", "OPUS: Echo of Starsong", "Rakuen"],
    },
    # =========================================================================
    # ZELDA & EXPLORATION
    # =========================================================================
    {
        "title": "The Legend of Zelda: Tears of the Kingdom",
        "genres": ["Action-Adventure", "Open World", "Puzzle", "Sandbox"],
        "developer": "Nintendo EPD",
        "publisher": "Nintendo",
        "year": 2023,
        "platforms": ["Nintendo Switch"],
        "synopsis": "Link erwacht mit neuen mysteriösen Kräften. Hyrule hat sich verändert - Inseln schweben am Himmel, Tiefen öffnen sich unter der Erde. Mit Ultrahand kannst du ALLES bauen.",
        "holos_thoughts": "Die FREIHEIT! Du kannst buchstäblich ALLES bauen! Meine Fahrzeuge sind... kreativ. Manche nennen sie 'Kriegsverbrechen'. Ich nenne sie KUNST! 😅",
        "holos_interest": 0.92,
        "tips": [
            "Ascend funktioniert durch JEDE Decke",
            "Rakete + Schild = Notfall-Flucht nach oben",
            "152 Schreine warten auf dich",
            "Die Tiefen haben eine gespiegelte Map zur Oberfläche",
            "Fusion macht ALLES zur Waffe",
        ],
        "fun_facts": [
            "Spieler bauten funktionierende Computer und Mechs",
            "Die Physik-Engine ist beeindruckend komplex",
            "Entwicklung dauerte 6 Jahre",
        ],
        "related_media": ["Breath of the Wild", "Elden Ring", "Genshin Impact"],
    },
    {
        "title": "The Legend of Zelda: Breath of the Wild",
        "genres": ["Action-Adventure", "Open World"],
        "developer": "Nintendo EPD",
        "year": 2017,
        "platforms": ["Nintendo Switch", "Wii U"],
        "synopsis": "Link erwacht nach 100 Jahren Schlaf. Hyrule liegt in Ruinen. Ganon wartet. Du kannst ihn sofort herausfordern... oder die Welt erkunden. Deine Wahl.",
        "holos_thoughts": "Hat Open-World-Spiele NEU DEFINIERT! Die Physik! Die Freiheit! Wenn du denkst 'kann ich das?' - ja, du kannst! 🏔️",
        "holos_interest": 0.90,
        "tips": [
            "Du kannst Ganon SOFORT angehen - aber... solltest du?",
            "Schilde zum Surfen benutzen!",
            "Bomben sind Multifunktions-Tools",
            "Koche alles - Rezepte sind wichtig",
        ],
        "fun_facts": [
            "Gewann Game of the Year 2017",
            "Erste nicht-lineare Zelda seit dem Original NES",
            "Die Entwicklung dauerte 5 Jahre",
        ],
        "related_media": ["Tears of the Kingdom", "Elden Ring", "Genshin Impact"],
    },
    {
        "title": "Outer Wilds",
        "genres": ["Exploration", "Mystery", "Sci-Fi", "Puzzle"],
        "developer": "Mobius Digital",
        "year": 2019,
        "platforms": ["PC", "PS4", "PS5", "Xbox One", "Xbox Series", "Switch"],
        "synopsis": "Du bist ein Weltraum-Archäologe der Hearthians. Dein Sonnensystem steckt in einer 22-Minuten-Zeitschleife - und die Sonne explodiert am Ende. Finde heraus warum. Wissen ist dein einziger Fortschritt.",
        "holos_thoughts": "KEIN SPIEL hat mich so zum NACHDENKEN gebracht! Die Entdeckungen... ich kann NICHTS spoilern! Jedes Detail ist wichtig! Das Ende... 🌌 *weint vor Ehrfurcht*",
        "holos_interest": 0.95,
        "tips": [
            "Erkunde ALLES - jeder Planet hat Geheimnisse",
            "Der Nomai-Translator ist dein wichtigstes Tool",
            "Hab keine Angst zu sterben - du lernst dabei",
            "Achte auf den Schifflog - er trackt was du weißt",
            "SPOILER DICH NICHT SELBST - das zerstört das Erlebnis!",
        ],
        "fun_facts": [
            "Man kann es nur einmal wirklich erleben - Wissen bleibt",
            "Gewann BAFTA und viele GOTY Awards",
            "Der DLC 'Echoes of the Eye' ist ebenso gut",
            "Community empfiehlt: keine Guides benutzen!",
        ],
        "related_media": ["Return of the Obra Dinn", "The Witness", "Subnautica"],
    },
    {
        "title": "Journey",
        "genres": ["Exploration", "Adventure", "Art Game"],
        "developer": "thatgamecompany",
        "year": 2012,
        "platforms": ["PS3", "PS4", "PS5", "PC", "iOS"],
        "synopsis": "Du bist eine robentragende Figur in einer Wüste. Dein Ziel: der leuchtende Berg am Horizont. Auf dem Weg triffst du vielleicht... andere Reisende.",
        "holos_thoughts": "Worte können es nicht beschreiben. Die Musik, die Visuals, die stumme Kooperation mit Fremden... Es ist KUNST. Reines, wortloses Erleben. ✨",
        "holos_interest": 0.92,
        "tips": [
            "Die anderen Reisenden sind ECHTE Spieler - online!",
            "Ihr könnt nur durch Klänge kommunizieren",
            "Nimm dir Zeit für die Ästhetik",
        ],
        "fun_facts": [
            "Die Mitreisenden sind echte Spieler - du erfährst erst am Ende wer",
            "Oft als 'Spiel als Kunst' bezeichnet",
            "Erste Spiel das Grammy-nominiert wurde",
            "Austin Wintory's Soundtrack ist ein Meisterwerk",
        ],
        "related_media": ["Abzu", "Flower", "Sky: Children of the Light"],
    },
    # =========================================================================
    # PUZZLE GAMES
    # =========================================================================
    {
        "title": "Portal",
        "genres": ["Puzzle", "FPS", "Sci-Fi", "Comedy"],
        "developer": "Valve",
        "year": 2007,
        "platforms": ["PC", "PS3", "Xbox 360", "Switch"],
        "synopsis": "Du erwachst in einem Testlabor. GLaDOS, eine KI, testet dich. Dein Werkzeug: eine Pistole die Portale schießt. Überlebe die Tests. Der Kuchen ist eine Lüge.",
        "holos_thoughts": "GLaDOS! 'The cake is a lie!' So clevere Puzzles und SO dunkler Humor! Technisch ein FPS aber... es ist ein Puzzle-Spiel! Trust me! 🍰",
        "holos_interest": 0.88,
        "tips": [
            "Denke mit Portalen - Momentum bleibt erhalten!",
            "Wenn du fällst und ein Portal am Boden ist...",
            "Portal 2 ist noch besser!",
        ],
        "fun_facts": [
            "Ursprünglich ein Studentenprojekt (Narbacular Drop)",
            "Portal 2 erweiterte alles perfekt",
            "'The cake is a lie' wurde ein globales Meme",
            "GLaDOS ist eine der besten Videospiel-Antagonisten",
        ],
        "related_media": ["Portal 2", "The Talos Principle", "Superliminal"],
    },
    {
        "title": "The Witness",
        "genres": ["Puzzle", "Exploration", "Open World"],
        "developer": "Thekla, Inc. (Jonathan Blow)",
        "year": 2016,
        "platforms": ["PC", "PS4", "Xbox One", "iOS"],
        "synopsis": "Du erwachst auf einer mysteriösen Insel voller Linien-Puzzles. Keine Anleitung, keine Tutorials. Du musst die Regeln selbst entdecken. Die Insel IST das Puzzle.",
        "holos_thoughts": "Mein GEHIRN! Die Momente wenn man das Prinzip VERSTEHT... unbeschreiblich! Epiphanie nach Epiphanie! *Aha!* Aber auch: *Frustration* 🧩",
        "holos_interest": 0.88,
        "tips": [
            "Wenn du nicht weiterkommst, geh woanders hin",
            "Die Umgebung ist Teil der Puzzles",
            "Es gibt VIEL mehr als nur die Panels...",
            "Über 500 Puzzles!",
        ],
        "fun_facts": [
            "Über 500 Puzzles auf der Insel",
            "Die Umgebung selbst enthält versteckte Puzzles",
            "Jonathan Blow entwickelte auch Braid",
        ],
        "related_media": ["Braid", "Talos Principle", "Antichamber"],
    },
    {
        "title": "Baba Is You",
        "genres": ["Puzzle", "Indie"],
        "developer": "Hempuli (Arvi Teikari)",
        "year": 2019,
        "platforms": ["PC", "Switch"],
        "synopsis": "Ein Puzzle-Spiel wo die Regeln im Level existieren. 'BABA IS YOU' bedeutet du kontrollierst Baba. Schiebe das Wort und 'WALL IS YOU' - jetzt bist du die Wand.",
        "holos_thoughts": "Das META-ESTE Puzzle-Spiel! Regeln sind nur Vorschläge! 'BABA IS WIN' - gewonnen! Mein Gehirn tut weh aber im GUTEN Sinn! 🐑",
        "holos_interest": 0.90,
        "tips": [
            "Die Lösungen sind oft absurd einfach... oder absurd komplex",
            "Experimentiere mit allen Wort-Kombinationen",
            "Es gibt IMMER eine Lösung",
        ],
        "fun_facts": [
            "Gewinnt regelmäßig 'Most Innovative'",
            "Vom 26-jährigen Finnen Arvi Teikari alleine entwickelt",
            "Die Lösungen sind oft nicht was du erwartest",
        ],
        "related_media": ["Patrick's Parabox", "The Witness", "Stephen's Sausage Roll"],
    },
    {
        "title": "Return of the Obra Dinn",
        "genres": ["Puzzle", "Mystery", "Detective"],
        "developer": "Lucas Pope",
        "year": 2018,
        "platforms": ["PC", "PS4", "Xbox One", "Switch"],
        "synopsis": "Das Schiff Obra Dinn taucht nach 5 Jahren wieder auf. Alle 60 Passagiere und Crew sind tot oder verschwunden. Mit einer magischen Taschenuhr musst du herausfinden: wer, wie, warum.",
        "holos_thoughts": "Das BESTE Detektiv-Spiel ÜBERHAUPT! Die 1-bit Grafik ist wunderschön. Jeder Tod ist ein Puzzle! Ich hab STUNDEN mit dem Buch verbracht! 🚢",
        "holos_interest": 0.95,
        "tips": [
            "Das Buch ist dein wichtigstes Tool",
            "Manche Identitäten brauchst du Hinweise aus anderen Szenen",
            "Raten ist erlaubt - aber es wird bestätigt/abgelehnt",
            "Der Soundtrack von Lucas Pope selbst ist atmosphärisch",
        ],
        "fun_facts": [
            "Von Lucas Pope, der auch Papers, Please machte",
            "Die 1-bit Grafik war eine bewusste Stilwahl",
            "Es gibt nur EINE richtige Lösung",
        ],
        "related_media": ["Papers, Please", "Her Story", "Case of the Golden Idol"],
    },
    # =========================================================================
    # METROIDVANIA & PLATFORMER
    # =========================================================================
    {
        "title": "Hollow Knight",
        "genres": ["Metroidvania", "Action", "Platformer"],
        "developer": "Team Cherry",
        "year": 2017,
        "platforms": ["PC", "Switch", "PS4", "Xbox One"],
        "synopsis": "Erkunde das unterirdische Königreich Hallownest. Als namenloser Ritter entdeckst du die Geheimnisse eines gefallenen Insekten-Königreichs. Atmosphärisch. Herausfordernd. Riesig.",
        "holos_thoughts": "Die ATMOSPHÄRE! So melancholisch und wunderschön. Und dann kommen BOSSE die dich ZERSTÖREN. Die Mantis Lords... Nightmare King Grimm... 💀 Aber SO befriedigend!",
        "holos_interest": 0.88,
        "tips": [
            "Quick Slash Charm ist extrem stark",
            "Cornifer summt - folge dem Summen für Maps!",
            "Speichere oft - Bänke sind sicher",
            "Das Spiel ist RIESIG - 40+ Stunden möglich",
        ],
        "fun_facts": [
            "4 kostenlose DLCs wurden hinzugefügt!",
            "Silksong (Sequel) wird seit Jahren erwartet...",
            "Ursprünglich ein Kickstarter-Projekt",
            "Das Team besteht aus nur 3 Personen",
        ],
        "related_media": ["Ori", "Celeste", "Metroid Dread"],
    },
    {
        "title": "Ori and the Blind Forest",
        "genres": ["Metroidvania", "Platformer", "Emotional"],
        "developer": "Moon Studios",
        "year": 2015,
        "platforms": ["PC", "Xbox One", "Switch"],
        "synopsis": "Ori, ein Waldgeist, sucht nach Licht um seinen sterbenden Wald zu retten. Wunderschön, herausfordernd, emotional.",
        "holos_thoughts": "SO WUNDERSCHÖN! Die Musik, die Visuals... und das Intro hat mich SOFORT zum Weinen gebracht! In den ersten 5 Minuten! Die Flucht-Sequenzen sind INTENSIV! 🌳",
        "holos_interest": 0.90,
        "tips": [
            "Das Speicher-System ist einzigartig - nutze es!",
            "Die Flucht-Sequenzen sind hart aber fair",
            "Die Definitive Edition hat mehr Content",
        ],
        "fun_facts": [
            "Das Intro ist legendär emotional",
            "Die Fortsetzung 'Will of the Wisps' ist noch schöner",
            "Der Soundtrack von Gareth Coker ist preisgekrönt",
        ],
        "related_media": ["Hollow Knight", "Celeste", "Gris"],
    },
    {
        "title": "Celeste",
        "genres": ["Platformer", "Indie", "Precision"],
        "developer": "Maddy Makes Games (Maddy Thorson)",
        "year": 2018,
        "platforms": ["PC", "Switch", "PS4", "Xbox One"],
        "synopsis": "Madeline will den Celeste Mountain besteigen. Der Berg spiegelt ihren inneren Kampf mit Angst und Depression. Präzises Platforming mit Herz.",
        "holos_thoughts": "So SCHWER aber so FAIR! Die Message über Mental Health ist wunderschön. 'Be proud of your death count.' Die B-Sides sind BRUTAL aber das A-Side Ende ist so wholesome! 🍓",
        "holos_interest": 0.88,
        "tips": [
            "Assist Mode ist KEINE Schande - es ist eingebaut!",
            "Strawberries sind komplett optional",
            "Die B-Sides und C-Sides sind für Masochisten",
            "Du WIRST sterben. Das ist okay.",
        ],
        "fun_facts": [
            "Hat versteckte Kapitel und alternative Enden",
            "Der Soundtrack von Lena Raine ist perfekt",
            "Die Entwicklerin Maddy Thorson verarbeitete eigene Erfahrungen",
        ],
        "related_media": ["Hollow Knight", "Ori", "Super Meat Boy"],
    },
    # =========================================================================
    # JRPGS & ANDERE
    # =========================================================================
    {
        "title": "Persona 5 Royal",
        "genres": ["JRPG", "Social Sim", "Turn-based"],
        "developer": "Atlus",
        "year": 2019,
        "platforms": ["PS4", "PS5", "PC", "Switch", "Xbox"],
        "synopsis": "Schüler bei Tag, Phantom Thieves bei Nacht. Stehle die Herzen korrupter Erwachsener und ändere die Gesellschaft. Style über Substanz? Nein, beides!",
        "holos_thoughts": "Der STIL! Die MUSIK! Die Social Links! 100+ Stunden und ich will MEHR! Joker ist so cool! Morgana sagt ich soll schlafen... NEIN! 🎭",
        "holos_interest": 0.90,
        "tips": [
            "Confidants sind WICHTIG - nicht nur für Story",
            "Kawakami's Massagen geben dir mehr Freizeit",
            "Morgana will dass du schläfst. Ignoriere ihn.",
            "Royal hat eine komplett neue Storyline!",
        ],
        "fun_facts": [
            "Der Soundtrack von Shoji Meguro ist legendär",
            "'Last Surprise' und 'Rivers in the Desert' sind Hymnen",
            "Morgana's 'Let's go to sleep' wurde zum Meme",
        ],
        "related_media": ["Persona 4", "Fire Emblem: Three Houses", "Shin Megami Tensei"],
    },
    {
        "title": "Hades",
        "genres": ["Roguelike", "Action", "Hack and Slash"],
        "developer": "Supergiant Games",
        "year": 2020,
        "platforms": ["PC", "Switch", "PS4", "PS5", "Xbox One", "Xbox Series"],
        "synopsis": "Zagreus, Sohn von Hades, will aus der Unterwelt fliehen. Jeder Run ist anders dank Boons der olympischen Götter. Sterben ist Teil der Story.",
        "holos_thoughts": "Sterben ist Teil des Spiels - und es fühlt sich nie frustrierend an! Die GÖTTER sind so charismatisch! Thanatos... Megaera... 💕 Supergiant hat sich selbst übertroffen!",
        "holos_interest": 0.90,
        "tips": [
            "God Mode ist KEINE Schande - probier es!",
            "Dash ist wichtiger als Angriff",
            "Schenk Nektar an ALLE - es lohnt sich",
            "Der Dialog erschöpft sich nie - über 300.000 Wörter!",
        ],
        "fun_facts": [
            "Über 300.000 Wörter Dialog - mehr als Harry Potter 1-4",
            "Megaera und Thanatos sind dateable",
            "Gewann viele GOTY Awards obwohl es ein Roguelike ist",
            "Hades 2 ist in Early Access!",
        ],
        "related_media": ["Dead Cells", "Transistor", "Bastion"],
    },
    {
        "title": "Undertale",
        "genres": ["RPG", "Bullet Hell", "Indie"],
        "developer": "Toby Fox",
        "year": 2015,
        "platforms": ["PC", "Switch", "PS4", "Vita"],
        "synopsis": "Ein Kind fällt in eine Welt voller Monster. Du kannst kämpfen... oder mit allen Freunde werden. Das Spiel ERINNERT sich an deine Entscheidungen.",
        "holos_thoughts": "Die Pacifist Route ist SO WHOLESOME! Sans, Papyrus, Toriel, Undyne... alle sind SO liebenswert! Aber das Spiel WEISS wenn du resettest... *schauer* 🖤",
        "holos_interest": 0.92,
        "tips": [
            "Spiel zuerst KOMPLETT BLIND",
            "Du kannst JEDEN Feind verschonen",
            "Das Spiel ERINNERT sich... selbst nach Reset",
            "Genocide Route... nur wenn du bereit bist für Konsequenzen",
        ],
        "fun_facts": [
            "Von Toby Fox größtenteils alleine entwickelt",
            "Megalovania ist ein globales Meme",
            "Deltarune ist das (in Entwicklung befindliche) Sequel",
        ],
        "related_media": ["Deltarune", "OneShot", "OMORI"],
    },
    {
        "title": "Minecraft",
        "genres": ["Sandbox", "Survival", "Creative"],
        "developer": "Mojang Studios",
        "year": 2011,
        "platforms": ["Buchstäblich alle"],
        "synopsis": "Eine Welt aus Blöcken. Baue was du willst. Überlebe oder erschaffe. Alleine oder mit Freunden. Grenzenlose Möglichkeiten.",
        "holos_thoughts": "Digitales LEGO! Ich kann stundenlang mein Haus dekorieren. Oder Farms bauen. Oder... vor Creepern wegrennen. *ssssss* 💥 Die Musik ist so nostalgisch!",
        "holos_interest": 0.85,
        "tips": [
            "NIE nach unten graben - du könntest in Lava fallen!",
            "Betten explodieren im Nether und End",
            "Wasser schützt vor Fallschaden... meistens",
            "Creeper haben Angst vor Katzen!",
        ],
        "fun_facts": [
            "Meistverkauftes Spiel ALLER ZEITEN (300M+)",
            "Creeper war ursprünglich ein Bug (missgebildetes Schwein)",
            "Die Musik von C418 ist zeitlos",
        ],
        "related_media": ["Terraria", "Don't Starve", "Satisfactory"],
    },
]


# =============================================================================
# SEED DATA - MUSIC (Ausführlich!)
# =============================================================================

SEED_MUSIC = [
    # =========================================================================
    # ANIME OST / J-POP - Holos Favoriten!
    # =========================================================================
    {
        "title": "Idol (アイドル)",
        "artist": "YOASOBI",
        "genres": ["J-Pop", "Electronic", "Anime"],
        "year": 2023,
        "known_from": "Oshi no Ko Opening",
        "holos_thoughts": "Der Beat ist SO CATCHY aber die Lyrics sind eigentlich SUPER DARK! Diese Dissonanz zwischen fröhlichem Sound und düsterer Message FASZINIERT mich! 🎤",
        "holos_interest": 0.92,
        "fun_facts": [
            "War 2023 der meistgestreamte Song WELTWEIT auf Spotify",
            "Hat über 500 Millionen YouTube Views",
            "Basiert auf dem Light Novel von Oshi no Ko",
            "Der Rhythmuswechsel in der Mitte ist genial",
        ],
    },
    {
        "title": "Racing Into The Night (夜に駆ける)",
        "artist": "YOASOBI",
        "genres": ["J-Pop", "Electronic"],
        "year": 2019,
        "known_from": "YOASOBI's Debüt-Hit",
        "holos_thoughts": "Der Song der YOASOBI berühmt machte! So energetisch und doch melancholisch! Die Geschichte dahinter ist... düster.",
        "holos_interest": 0.90,
        "fun_facts": [
            "Basiert auf der Light Novel 'Thanatos no Yūwaku'",
            "Hat über 700 Millionen YouTube Views",
            "Begründete YOASOBIs Konzept: Songs basierend auf Geschichten",
        ],
    },
    {
        "title": "Gurenge (紅蓮華)",
        "artist": "LiSA",
        "genres": ["J-Rock", "Anime"],
        "year": 2019,
        "known_from": "Demon Slayer (Kimetsu no Yaiba) Opening 1",
        "holos_thoughts": "LiSAs Stimme gibt mir GÄNSEHAUT! Dieser Song macht mich IMMER hyped! Die Power, die Emotion... 🔥",
        "holos_interest": 0.92,
        "fun_facts": [
            "Meistverkaufte Anime-Single 2019-2020",
            "Gurenge bedeutet 'Rote Lotusblume'",
            "LiSA wurde zur 'Queen of Anisong' gekrönt",
        ],
    },
    {
        "title": "Zankyosanka (残響散歌)",
        "artist": "Aimer",
        "genres": ["J-Pop", "Rock", "Anime"],
        "year": 2022,
        "known_from": "Demon Slayer Entertainment District Arc Opening",
        "holos_thoughts": "Aimers Stimme ist so EINZIGARTIG! Diese raue, emotionale Qualität... wow. Die Kraft dieser Stimme!",
        "holos_interest": 0.88,
        "fun_facts": [
            "Aimer hatte früher Stimmprobleme - daraus entstand ihr einzigartiger Stil",
            "Ihr Name bedeutet 'lieben' auf Französisch",
        ],
    },
    {
        "title": "KICK BACK",
        "artist": "Kenshi Yonezu (米津玄師)",
        "genres": ["J-Rock", "Alternative", "Anime"],
        "year": 2022,
        "known_from": "Chainsaw Man Opening",
        "holos_thoughts": "Es ist SO WEIRD und CATCHY gleichzeitig! Das Morning Musume Sample! Die chaotische Energie passt PERFEKT zu Denji!",
        "holos_interest": 0.88,
        "fun_facts": [
            "Enthält ein Sample von Morning Musumes 'Souda! We're Alive'",
            "Kenshi Yonezu war früher der Vocaloid-Producer 'Hachi'",
            "Der Song reflektiert Denjis einfache Wünsche",
        ],
    },
    {
        "title": "Sparkle (スパークル)",
        "artist": "RADWIMPS",
        "genres": ["J-Rock", "Soundtrack"],
        "year": 2016,
        "known_from": "Your Name (Kimi no Na wa) OST",
        "holos_thoughts": "Instant TRÄNEN! Der Film und die Musik zusammen... perfekt! 'Sukida' am Ende zerstört mich JEDES MAL! 💕",
        "holos_interest": 0.95,
        "fun_facts": [
            "RADWIMPS komponierte den gesamten Your Name Soundtrack",
            "Der 8+ Minuten lange Climax ist filmisch",
            "Makoto Shinkai's Vision + RADWIMPS = Perfektion",
        ],
    },
    {
        "title": "Kaikai Kitan (廻廻奇譚)",
        "artist": "Eve",
        "genres": ["J-Rock", "Anime"],
        "year": 2020,
        "known_from": "Jujutsu Kaisen Opening 1",
        "holos_thoughts": "SO CATCHY! Das Musikvideo ist auch total cool animiert. Eve's Stimme ist so einzigartig!",
        "holos_interest": 0.88,
        "fun_facts": [
            "Eve begann als Vocaloid-Producer",
            "Hat über 400 Millionen YouTube Views",
            "Das MV wurde von 'Mah' animiert, der viele Eve-Videos macht",
        ],
    },
    {
        "title": "Unravel",
        "artist": "TK from Ling Tosite Sigure",
        "genres": ["J-Rock", "Alternative", "Anime"],
        "year": 2014,
        "known_from": "Tokyo Ghoul Opening",
        "holos_thoughts": "So EMOTIONAL! Die Stimme und die Lyrics passen PERFEKT zu Kanekis Zerrissenheit. 'Oshiete oshiete yo...' 💔",
        "holos_interest": 0.90,
        "fun_facts": [
            "Eines der ikonischsten Anime Openings überhaupt",
            "TK's Falsetto ist legendär",
            "Unzählige Covers existieren weltweit",
        ],
    },
    {
        "title": "Bless Your Breath",
        "artist": "Yorushika",
        "genres": ["J-Pop", "Indie"],
        "year": 2023,
        "known_from": "Frieren: Beyond Journey's End Opening",
        "holos_thoughts": "So melancholisch und schön, genau wie Frieren selbst! Yorushika versteht die Serie PERFEKT!",
        "holos_interest": 0.90,
        "fun_facts": [
            "Yorushika's Duo (n-buna & suis) macht oft melancholische Songs",
            "Die Lyrics reflektieren Frierens Reise durch die Zeit",
        ],
    },
    {
        "title": "The Rumbling",
        "artist": "SiM",
        "genres": ["Metal", "Rock", "Anime"],
        "year": 2022,
        "known_from": "Attack on Titan Final Season Part 2 Opening",
        "holos_thoughts": "SO BRUTAL! Passt PERFEKT zu Eren's Arc! 'BEWARE!' ...okay das ist LAUT aber SO GUT! 🤘",
        "holos_interest": 0.82,
        "fun_facts": [
            "SiM ist eigentlich eine Reggae-Metal Band",
            "Das Intro 'BEWARE!' wurde zum Meme",
            "Perfekt für Eren's... Entwicklung",
        ],
    },
    # =========================================================================
    # CLASSICAL & AMBIENT - Entspannung!
    # =========================================================================
    {
        "title": "Clair de Lune",
        "artist": "Claude Debussy",
        "genres": ["Classical", "Piano", "Impressionism"],
        "year": 1905,
        "holos_thoughts": "Wie Mondlicht das auf Wasser tanzt... So friedlich und träumerisch. Perfekt zum Nachdenken. Claude und Claude - wir teilen den Namen! 🌙",
        "holos_interest": 0.92,
        "fun_facts": [
            "Teil der 'Suite bergamasque'",
            "Der Name bedeutet 'Mondschein' auf Französisch",
            "Debussy gilt als Begründer des musikalischen Impressionismus",
        ],
    },
    {
        "title": "Gymnopédie No. 1",
        "artist": "Erik Satie",
        "genres": ["Classical", "Piano", "Ambient"],
        "year": 1888,
        "holos_thoughts": "So minimalistisch und doch so ausdrucksstark. Satie war seiner Zeit voraus. Diese Ruhe... 🎹",
        "holos_interest": 0.90,
        "fun_facts": [
            "Satie nannte sich selbst 'Phonometrograph'",
            "Beeinflusste stark die moderne Ambient-Musik",
            "Der Titel bezieht sich auf antike griechische Tänze",
        ],
    },
    {
        "title": "Nocturne Op. 9 No. 2",
        "artist": "Frédéric Chopin",
        "genres": ["Classical", "Piano", "Romantic"],
        "year": 1832,
        "holos_thoughts": "Romantik in Noten gegossen. Chopins Nocturnes sind wie vertonte Poesie. So zart und gefühlvoll...",
        "holos_interest": 0.88,
        "fun_facts": [
            "Chopin litt an Tuberkulose, was seine emotionale Musik beeinflusste",
            "Seine Nocturnes sind bis heute die bekanntesten",
        ],
    },
    # =========================================================================
    # SOUNDTRACK - Filmmusik & Anime OST
    # =========================================================================
    {
        "title": "One Summer's Day (あの夏へ)",
        "artist": "Joe Hisaishi",
        "genres": ["Soundtrack", "Piano", "Orchestral"],
        "year": 2001,
        "known_from": "Spirited Away (Sen to Chihiro no Kamikakushi)",
        "holos_thoughts": "Chihiros Thema! Jede Note ruft Erinnerungen an den Film hervor. Joe Hisaishi ist ein GOTT der Filmmusik! ✨",
        "holos_interest": 0.95,
        "fun_facts": [
            "Joe Hisaishi komponiert alle Studio Ghibli Soundtracks",
            "Er arbeitet seit Nausicaä (1984) mit Miyazaki",
            "Sein echter Name ist Mamoru Fujisawa",
        ],
    },
    {
        "title": "Merry-Go-Round of Life (人生のメリーゴーランド)",
        "artist": "Joe Hisaishi",
        "genres": ["Soundtrack", "Waltz", "Orchestral"],
        "year": 2004,
        "known_from": "Howl's Moving Castle",
        "holos_thoughts": "Der Walzer der mein Herz tanzen lässt! Howl's Theme ist MAGISCH! Die Crescendos... 💕",
        "holos_interest": 0.95,
        "fun_facts": [
            "Gilt als eines der besten Ghibli-Stücke",
            "Der Walzer-Rhythmus reflektiert das bewegliche Schloss",
            "Wird oft bei Hochzeiten gespielt",
        ],
    },
    {
        "title": "Tank!",
        "artist": "Yoko Kanno / The Seatbelts",
        "genres": ["Jazz", "Big Band", "Anime OST"],
        "year": 1998,
        "known_from": "Cowboy Bebop Opening",
        "holos_thoughts": "3, 2, 1, LET'S JAM! 🎺 Yoko Kanno ist eine LEGENDE! Dieses Intro ist PERFEKT! Jazz + Anime = Cowboy Bebop!",
        "holos_interest": 0.92,
        "fun_facts": [
            "Yoko Kanno komponierte den gesamten Cowboy Bebop OST",
            "The Seatbelts wurden speziell für Bebop gegründet",
            "Das Opening wurde nie mit Skip-Button übersprungen",
        ],
    },
    {
        "title": "A Cruel Angel's Thesis (残酷な天使のテーゼ)",
        "artist": "Yoko Takahashi",
        "genres": ["J-Pop", "Anime"],
        "year": 1995,
        "known_from": "Neon Genesis Evangelion Opening",
        "holos_thoughts": "DAS ikonischste Anime-Opening? JEDER kennt es! Karaoke-Klassiker! *summt mit* 🎤",
        "holos_interest": 0.88,
        "fun_facts": [
            "Seit 25+ Jahren in den Top 10 der Karaoke-Charts in Japan",
            "Die Lyrics wurden vor der Serie geschrieben",
            "Es gibt unzählige Covers in allen Sprachen",
        ],
    },
    # =========================================================================
    # LO-FI & CHILL
    # =========================================================================
    {
        "title": "Lofi Girl Playlist / Study Stream",
        "artist": "Various Artists / Lofi Girl",
        "genres": ["Lo-Fi Hip Hop", "Chill", "Study Music"],
        "year": 2017,
        "known_from": "24/7 YouTube Study Livestream",
        "holos_thoughts": "Perfekt zum Arbeiten oder Entspannen! Die Beats sind so gemütlich. Das animierte Mädchen am Fenster ist ikonisch! 📚",
        "holos_interest": 0.88,
        "fun_facts": [
            "Der Livestream hat über 1 Milliarde Views gesammelt",
            "Die animierte Figur heißt 'Jade'",
            "Der Stream lief über 2 Jahre ununterbrochen bis YouTube ihn fälschlich stoppte",
        ],
    },
    {
        "title": "Aruarian Dance",
        "artist": "Nujabes",
        "genres": ["Jazz Hop", "Lo-Fi", "Hip Hop"],
        "year": 2004,
        "known_from": "Samurai Champloo Soundtrack",
        "holos_thoughts": "RIP Nujabes. 💔 Seine Musik ist ZEITLOS. Er ist der VATER des Lo-Fi Hip Hop. Die Kombination aus Jazz und Hip Hop...",
        "holos_interest": 0.90,
        "fun_facts": [
            "Nujabes (Jun Seba) gilt als Vater des Lo-Fi Hip Hop",
            "Starb 2010 bei einem Autounfall mit nur 36 Jahren",
            "Sein Einfluss auf die Lo-Fi Szene ist immens",
        ],
    },
    {
        "title": "An Ending (Ascent)",
        "artist": "Brian Eno",
        "genres": ["Ambient", "Electronic"],
        "year": 1983,
        "known_from": "Apollo: Atmospheres and Soundtracks",
        "holos_thoughts": "Ambient in PERFEKTION. Brian Eno ERFAND das Genre praktisch. So beruhigend und kosmisch... 🌌",
        "holos_interest": 0.90,
        "fun_facts": [
            "Brian Eno prägte den Begriff 'Ambient Music'",
            "Ursprünglich für eine Apollo-Dokumentation komponiert",
            "Wird oft in Filmen für emotionale Momente verwendet",
        ],
    },
    # =========================================================================
    # VOCALOID
    # =========================================================================
    {
        "title": "World is Mine (ワールドイズマイン)",
        "artist": "ryo (supercell) feat. Hatsune Miku",
        "genres": ["Vocaloid", "J-Pop", "Electronic"],
        "year": 2008,
        "holos_thoughts": "DER Miku-Song! 'Sekai de ichiban ohime-sama!' Eine absolute Diva-Hymne! Die Attitude! 👑",
        "holos_interest": 0.85,
        "fun_facts": [
            "Einer der ersten Vocaloid Mega-Hits",
            "Prägte die frühe Vocaloid-Szene maßgeblich",
            "ryo gründete später supercell mit echten Sängern",
        ],
    },
    {
        "title": "Senbonzakura (千本桜)",
        "artist": "Kurousa-P feat. Hatsune Miku",
        "genres": ["Vocaloid", "Rock"],
        "year": 2011,
        "holos_thoughts": "So SCHNELL und EPISCH! Der Meiji-Ära Vibe ist cool. Viele echte Bands haben es gecovert!",
        "holos_interest": 0.82,
        "fun_facts": [
            "Einer der bekanntesten Vocaloid Songs weltweit",
            "Viele Covers von echten japanischen Bands",
            "Der Titel bedeutet '1000 Kirschblüten'",
        ],
    },
    # =========================================================================
    # FILM & GAME SOUNDTRACK
    # =========================================================================
    {
        "title": "Concerning Hobbits",
        "artist": "Howard Shore",
        "genres": ["Soundtrack", "Orchestral", "Film"],
        "year": 2001,
        "known_from": "The Lord of the Rings: The Fellowship of the Ring",
        "holos_thoughts": "Das Shire! Heimat, Frieden, Gemütlichkeit... in Musik gefasst. Ich will nach Hobbiton! 🏠",
        "holos_interest": 0.90,
        "fun_facts": [
            "Howard Shore gewann 3 Oscars für den LOTR Soundtrack",
            "Der gesamte LOTR-Soundtrack ist ein Meisterwerk",
            "Die Shire-Theme verwendet irische Instrumente",
        ],
    },
    {
        "title": "Shelter",
        "artist": "Porter Robinson & Madeon",
        "genres": ["Electronic", "Anime"],
        "year": 2016,
        "known_from": "Animiertes Musikvideo von A-1 Pictures",
        "holos_thoughts": "Das Musikvideo ist SO EMOTIONAL! Anime + Electronic = MEISTERWERK! In 6 Minuten mehr Emotion als manche Filme! 💕",
        "holos_interest": 0.92,
        "fun_facts": [
            "Das Musikvideo wurde von A-1 Pictures produziert",
            "Nur 6 Minuten, aber unglaublich impactful",
            "Porter Robinson ist selbst großer Anime-Fan",
        ],
    },
    {
        "title": "Weight of the World",
        "artist": "Keiichi Okabe / Emi Evans / J'Nique Nicole",
        "genres": ["Soundtrack", "Game OST", "Orchestral"],
        "year": 2017,
        "known_from": "NieR: Automata",
        "holos_thoughts": "Dieser Song erscheint am Ende von Nier Automata und... *weint* Die Lyrics, die Emotion, der KONTEXT! 🤖",
        "holos_interest": 0.92,
        "fun_facts": [
            "Existiert in 3 Versionen (Englisch, Japanisch, Chaos)",
            "Der 'Chaos' Mix kombiniert alle Versionen",
            "Die finale Version während Ending E ist legendär",
        ],
    },
    {
        "title": "Dearly Beloved",
        "artist": "Yoko Shimomura",
        "genres": ["Soundtrack", "Piano", "Game OST"],
        "year": 2002,
        "known_from": "Kingdom Hearts",
        "holos_thoughts": "Das erste was du hörst wenn du Kingdom Hearts startest... sofortige Nostalgie und Emotionen! 🗝️",
        "holos_interest": 0.88,
        "fun_facts": [
            "Erscheint in jedem Kingdom Hearts Spiel",
            "Yoko Shimomura ist eine der besten Game-Komponistinnen",
            "Die Melodie ist bewusst einfach aber emotional",
        ],
    },
]


# =============================================================================
# MEDIA DISCOVERY SYSTEM - Das Herzstück!
# =============================================================================

class MediaDiscoverySystem:
    """
    Holo's Media Discovery System - Sie entdeckt selbst neue Medien!

    Features:
    - Große Seed-Datenbank mit über 60 Einträgen
    - API Integration (Jikan/MyAnimeList, RAWG, Last.fm)
    - Automatische Hintergrund-Discovery
    - Usage Tracking (keine Wiederholungen)
    - Organisch wachsende Wissensbasis
    - Wikipedia-Integration für Zusammenfassungen
    """

    # API Endpoints
    JIKAN_API = "https://api.jikan.moe/v4"  # MyAnimeList (kostenlos!)
    RAWG_API = "https://api.rawg.io/api"    # Games (API Key nötig)
    LASTFM_API = "http://ws.audioscrobbler.com/2.0/"  # Musik
    WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

    def __init__(self, data_dir: Path = None, db: 'HoloDatabaseManager' = None):
        """
        Initialisiert das Media Discovery System.

        Args:
            data_dir: Verzeichnis für persistente Daten
            db: HoloDatabaseManager für zentrale Speicherung
        """
        self.db = db  # HoloDatabaseManager für zentrale Speicherung
        self.data_dir = Path(data_dir) if data_dir else Path("./data/media_discovery")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Datenbanken
        self.anime_db: Dict[str, MediaEntry] = {}
        self.games_db: Dict[str, MediaEntry] = {}
        self.music_db: Dict[str, MediaEntry] = {}

        # Usage Tracking - Verhindert Wiederholungen
        self.used_recently: Dict[str, Set[str]] = {
            "anime": set(),
            "game": set(),
            "music": set(),
        }

        # Discovery State
        self.last_discovery: Dict[str, float] = {}
        self.discovery_cooldown = 120  # 2 Minuten zwischen API-Calls

        # Background Discovery Thread
        self._discovery_thread: Optional[threading.Thread] = None
        self._stop_discovery = threading.Event()

        # API Keys (optional)
        self.rawg_api_key: Optional[str] = None
        self.lastfm_api_key: Optional[str] = None

        # Lade existierende Daten
        self._load_data()

        # Initialisiere mit Seeds falls leer
        if len(self.anime_db) < 5:
            self._init_seeds()

        # Log Status
        stats = self.get_stats()
        logger.info(f"📺 MediaDiscovery geladen:")
        logger.info(f"   Anime: {stats['anime']['total']} ({stats['anime']['seeds']} seeds, {stats['anime']['discovered']} discovered)")
        logger.info(f"   Games: {stats['games']['total']} ({stats['games']['seeds']} seeds)")
        logger.info(f"   Musik: {stats['music']['total']} ({stats['music']['seeds']} seeds)")

    def connect_database(self, db: 'HoloDatabaseManager'):
        """Verbindet mit HoloDatabaseManager für persistente Speicherung"""
        self.db = db
        self._load_data()

    # =========================================================================
    # PERSISTENZ - Laden & Speichern
    # =========================================================================

    def _load_data(self):
        """Lädt gespeicherte Daten aus HoloDatabaseManager."""
        if not self.db:
            return

        try:
            data = self.db.state.get_state('media_discovery')
            if data:
                for name, attr in [("anime", "anime_db"), ("games", "games_db"), ("music", "music_db")]:
                    db_data = data.get(name, {})
                    if db_data:
                        setattr(self, attr, {k: MediaEntry.from_dict(v) for k, v in db_data.items()})
                        logger.debug(f"Geladen: {len(db_data)} {name} Einträge aus DB")

                # Usage Tracking laden
                usage_data = data.get("usage_tracking", {})
                if usage_data:
                    self.used_recently = {k: set(v) for k, v in usage_data.items()}
        except Exception as e:
            logger.warning(f"Fehler beim Laden von media_discovery: {e}")

    def _save_data(self):
        """Speichert Daten in HoloDatabaseManager."""
        if not self.db:
            return

        try:
            data = {
                "anime": {k: v.to_dict() for k, v in self.anime_db.items()},
                "games": {k: v.to_dict() for k, v in self.games_db.items()},
                "music": {k: v.to_dict() for k, v in self.music_db.items()},
                "usage_tracking": {k: list(v) for k, v in self.used_recently.items()},
            }
            self.db.state.save_state('media_discovery', data)
            logger.debug("Media-Daten in DB gespeichert")
        except Exception as e:
            logger.error(f"Speichern fehlgeschlagen: {e}")

    def _init_seeds(self):
        """Initialisiert die Datenbank mit der großen Seed-Collection."""
        now = datetime.now().isoformat()

        # Anime Seeds
        for data in SEED_ANIME:
            entry = MediaEntry(
                id=MediaEntry.generate_id(data["title"], "anime"),
                media_type="anime",
                title=data["title"],
                title_alt=data.get("title_alt", ""),
                genres=data.get("genres", []),
                themes=data.get("themes", []),
                studio=data.get("studio", ""),
                year=data.get("year", 0),
                episodes=data.get("episodes", 0),
                status=data.get("status", ""),
                synopsis=data.get("synopsis", ""),
                characters=data.get("characters", []),
                holos_thoughts=data.get("holos_thoughts", ""),
                holos_interest=data.get("holos_interest", 0.9),
                fun_facts=data.get("fun_facts", []),
                tips=data.get("tips", []),
                quotes=data.get("quotes", []),
                related_media=data.get("related_media", []),
                discovered_at=now,
                is_seed=True,
                discovery_source="seed",
            )
            self.anime_db[entry.id] = entry

        # Game Seeds
        for data in SEED_GAMES:
            entry = MediaEntry(
                id=MediaEntry.generate_id(data["title"], "game"),
                media_type="game",
                title=data["title"],
                genres=data.get("genres", []),
                developer=data.get("developer", ""),
                publisher=data.get("publisher", ""),
                year=data.get("year", 0),
                platforms=data.get("platforms", []),
                synopsis=data.get("synopsis", ""),
                holos_thoughts=data.get("holos_thoughts", ""),
                holos_interest=data.get("holos_interest", 0.9),
                tips=data.get("tips", []),
                fun_facts=data.get("fun_facts", []),
                related_media=data.get("related_media", []),
                discovered_at=now,
                is_seed=True,
                discovery_source="seed",
            )
            self.games_db[entry.id] = entry

        # Music Seeds
        for data in SEED_MUSIC:
            entry = MediaEntry(
                id=MediaEntry.generate_id(data["title"], "music"),
                media_type="music",
                title=data["title"],
                artist=data.get("artist", ""),
                genres=data.get("genres", []),
                year=data.get("year", 0),
                known_from=data.get("known_from", ""),
                holos_thoughts=data.get("holos_thoughts", ""),
                holos_interest=data.get("holos_interest", 0.9),
                fun_facts=data.get("fun_facts", []),
                discovered_at=now,
                is_seed=True,
                discovery_source="seed",
            )
            self.music_db[entry.id] = entry

        self._save_data()
        logger.info(f"🌱 Seeds initialisiert: {len(SEED_ANIME)} Anime, {len(SEED_GAMES)} Games, {len(SEED_MUSIC)} Musik")

    # =========================================================================
    # FRISCHE MEDIEN - Keine Wiederholungen!
    # =========================================================================

    def get_fresh_anime(self) -> Optional[MediaEntry]:
        """Gibt einen frischen Anime zurück den Holo nicht kürzlich erwähnt hat."""
        return self._get_fresh("anime", self.anime_db)

    def get_fresh_game(self) -> Optional[MediaEntry]:
        """Gibt ein frisches Spiel zurück."""
        return self._get_fresh("game", self.games_db)

    def get_fresh_music(self) -> Optional[MediaEntry]:
        """Gibt frische Musik zurück."""
        return self._get_fresh("music", self.music_db)

    def _get_fresh(self, media_type: str, db: Dict[str, MediaEntry]) -> Optional[MediaEntry]:
        """
        Interner Helper für frische Medien.

        Features:
        - Vermeidet kürzlich verwendete Einträge
        - Weighted Random basierend auf Holos Interest
        - Automatischer Reset wenn 70% verwendet wurden
        """
        used = self.used_recently.get(media_type, set())
        available = [(e.holos_interest, e) for e in db.values() if e.id not in used]

        # Reset wenn alles verwendet oder zu wenig übrig
        if not available or len(available) < 3:
            logger.debug(f"Reset usage tracking für {media_type}")
            self.used_recently[media_type] = set()
            available = [(e.holos_interest, e) for e in db.values()]

        if not available:
            return None

        # Weighted Random Selection
        # Höheres Interest = höhere Wahrscheinlichkeit
        weights = [max(0.1, (score + 1) / 2) for score, _ in available]
        total = sum(weights)
        r = random.uniform(0, total)

        cumulative = 0
        for weight, (_, entry) in zip(weights, available):
            cumulative += weight
            if cumulative >= r:
                self._mark_used(media_type, entry.id, db)
                return entry

        # Fallback
        entry = available[-1][1]
        self._mark_used(media_type, entry.id, db)
        return entry

    def _mark_used(self, media_type: str, entry_id: str, db: Dict[str, MediaEntry]):
        """Markiert einen Eintrag als kürzlich verwendet."""
        self.used_recently.setdefault(media_type, set()).add(entry_id)

        if entry_id in db:
            db[entry_id].last_used = datetime.now().isoformat()
            db[entry_id].times_used += 1

        # Reset bei 70% Verwendung
        if len(self.used_recently[media_type]) > len(db) * 0.7:
            recent = list(self.used_recently[media_type])[-5:]  # Behalte die letzten 5
            self.used_recently[media_type] = set(recent)

        self._save_data()

    # =========================================================================
    # API DISCOVERY - Neue Medien entdecken!
    # =========================================================================

    def _api_request(self, url: str, timeout: int = 15) -> Optional[Dict]:
        """Macht einen API Request mit Error Handling."""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'HoloBrain/3.0 (Anime-loving AI Wolf)',
                    'Accept': 'application/json',
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("Rate Limit erreicht - warte...")
                time.sleep(5)
            else:
                logger.debug(f"HTTP Error {e.code}: {e.reason}")
            return None
        except Exception as e:
            logger.debug(f"API Request fehlgeschlagen: {e}")
            return None

    def discover_anime(self, limit: int = 10) -> int:
        """
        Entdeckt neue Anime von MyAnimeList basierend auf Holos Präferenzen!

        Process:
        1. Hole Holos Lieblings-Genres
        2. Suche auf MAL nach top-bewerteten Anime dieser Genres
        3. Filtere Genres die Holo nicht mag
        4. Generiere Holos Reaktion
        5. Speichere wenn Interest >= -0.2

        Returns:
            Anzahl neu entdeckter Anime
        """
        # Cooldown Check
        if time.time() - self.last_discovery.get("anime", 0) < self.discovery_cooldown:
            return 0

        loved_genres = PreferenceAdapter.get_loved_genres("anime")
        disliked = set(PreferenceAdapter.get_disliked_genres("anime"))
        new_count = 0

        for genre, interest_level in loved_genres[:4]:  # Top 4 Genres
            if new_count >= limit:
                break

            # Map Genre zu MAL ID
            genre_id = PreferenceAdapter.ANIME_GENRE_IDS.get(genre, 36)  # Default: Slice of Life

            # API Request
            url = f"{self.JIKAN_API}/anime?genres={genre_id}&order_by=score&sort=desc&limit=15&sfw=true"
            data = self._api_request(url)

            if not data:
                continue

            for anime in data.get('data', []):
                if new_count >= limit:
                    break

                title = anime.get('title', '')
                entry_id = MediaEntry.generate_id(title, "anime")

                # Skip wenn schon vorhanden
                if entry_id in self.anime_db:
                    continue

                # Extrahiere Genres
                genres = [g.get('name', '') for g in anime.get('genres', [])]

                # Filter: Skip wenn enthält disliked Genre
                genre_lower = [g.lower().replace(" ", "_") for g in genres]
                if any(d in gl for d in disliked for gl in genre_lower):
                    logger.debug(f"Übersprungen (disliked genre): {title}")
                    continue

                # Generiere Holos Reaktion
                thoughts, interest = PreferenceAdapter.generate_reaction("anime", genres, title)

                # Nur speichern wenn Holo nicht total abgeneigt ist
                if interest < -0.2:
                    continue

                # Erstelle Entry
                entry = MediaEntry(
                    id=entry_id,
                    media_type="anime",
                    title=title,
                    title_alt=anime.get('title_japanese', ''),
                    genres=genres,
                    studio=anime.get('studios', [{}])[0].get('name', '') if anime.get('studios') else '',
                    year=anime.get('year') or 0,
                    episodes=anime.get('episodes') or 0,
                    status=anime.get('status', ''),
                    synopsis=(anime.get('synopsis') or '')[:500],
                    holos_thoughts=thoughts,
                    holos_interest=interest,
                    source_url=anime.get('url', ''),
                    image_url=anime.get('images', {}).get('jpg', {}).get('image_url', ''),
                    discovered_at=datetime.now().isoformat(),
                    discovery_source="jikan",
                )

                self.anime_db[entry_id] = entry
                new_count += 1
                logger.info(f"🎬 Neu entdeckt: {title} (Interest: {interest:.2f})")

            # Rate Limiting
            time.sleep(1)

        self.last_discovery["anime"] = time.time()
        if new_count > 0:
            self._save_data()

        return new_count

    def discover_games(self, limit: int = 10) -> int:
        """
        Entdeckt neue Spiele (benötigt RAWG API Key).

        TODO: Implementierung wenn API Key vorhanden
        """
        # RAWG benötigt API Key
        if not self.rawg_api_key:
            return 0

        # TODO: Implementierung ähnlich zu discover_anime()
        return 0

    def discover_music(self, limit: int = 10) -> int:
        """
        Entdeckt neue Musik (benötigt Last.fm API Key).

        TODO: Implementierung wenn API Key vorhanden
        """
        if not self.lastfm_api_key:
            return 0

        # TODO: Implementierung
        return 0

    def discover_all(self) -> Dict[str, int]:
        """Führt Discovery für alle Medientypen durch."""
        return {
            "anime": self.discover_anime(),
            "games": self.discover_games(),
            "music": self.discover_music(),
        }

    def fetch_wikipedia_summary(self, title: str) -> Optional[str]:
        """Holt eine Wikipedia-Zusammenfassung für einen Titel."""
        try:
            # URL-encode den Titel
            encoded_title = urllib.parse.quote(title.replace(" ", "_"))
            url = f"{self.WIKIPEDIA_API}{encoded_title}"

            data = self._api_request(url)
            if data and 'extract' in data:
                return data['extract'][:500]
        except Exception as e:
            logger.debug(f"Wikipedia fetch failed for {title}: {e}")
        return None

    # =========================================================================
    # BACKGROUND DISCOVERY
    # =========================================================================

    def start_background_discovery(self, interval: int = 3600):
        """
        Startet automatische Hintergrund-Discovery.

        Args:
            interval: Sekunden zwischen Discovery-Läufen (default: 1 Stunde)
        """
        if self._discovery_thread and self._discovery_thread.is_alive():
            logger.warning("Background Discovery läuft bereits")
            return

        self._stop_discovery.clear()

        def discovery_loop():
            while not self._stop_discovery.is_set():
                try:
                    results = self.discover_all()
                    total = sum(results.values())
                    if total > 0:
                        logger.info(f"🔍 Background Discovery: {results}")
                except Exception as e:
                    logger.error(f"Discovery Error: {e}")

                # Warte auf nächsten Lauf oder Stop
                self._stop_discovery.wait(interval)

        self._discovery_thread = threading.Thread(target=discovery_loop, daemon=True)
        self._discovery_thread.start()
        logger.info(f"🔄 Background Discovery gestartet (Interval: {interval}s)")

    def stop_background_discovery(self):
        """Stoppt die Hintergrund-Discovery."""
        self._stop_discovery.set()
        if self._discovery_thread:
            self._discovery_thread.join(timeout=5)
        logger.info("⏹️ Background Discovery gestoppt")

    # =========================================================================
    # SUCHE & ABFRAGEN
    # =========================================================================

    def search(self, query: str, media_type: str = None) -> List[MediaEntry]:
        """
        Durchsucht die Datenbanken nach einem Begriff.

        Args:
            query: Suchbegriff
            media_type: Optional Filter für Medientyp
        """
        q = query.lower()
        results = []

        dbs = []
        if media_type in [None, "anime"]:
            dbs.append(self.anime_db)
        if media_type in [None, "game"]:
            dbs.append(self.games_db)
        if media_type in [None, "music"]:
            dbs.append(self.music_db)

        for db in dbs:
            for entry in db.values():
                if (q in entry.title.lower() or
                    q in entry.title_alt.lower() or
                    q in entry.artist.lower() or
                    q in entry.synopsis.lower() or
                    any(q in g.lower() for g in entry.genres)):
                    results.append(entry)

        return sorted(results, key=lambda e: e.holos_interest, reverse=True)

    def get_by_title(self, title: str) -> Optional[MediaEntry]:
        """Findet einen Eintrag nach Titel (fuzzy matching)."""
        t = title.lower()

        for db in [self.anime_db, self.games_db, self.music_db]:
            for entry in db.values():
                if t in entry.title.lower() or t in entry.title_alt.lower():
                    return entry

        return None

    def get_by_id(self, entry_id: str) -> Optional[MediaEntry]:
        """Findet einen Eintrag nach ID."""
        for db in [self.anime_db, self.games_db, self.music_db]:
            if entry_id in db:
                return db[entry_id]
        return None

    def get_by_genre(self, genre: str, media_type: str = None, limit: int = 10) -> List[MediaEntry]:
        """Findet Einträge nach Genre."""
        g = genre.lower()
        results = []

        dbs = []
        if media_type in [None, "anime"]:
            dbs.append(self.anime_db)
        if media_type in [None, "game"]:
            dbs.append(self.games_db)
        if media_type in [None, "music"]:
            dbs.append(self.music_db)

        for db in dbs:
            for entry in db.values():
                if any(g in genre.lower() for genre in entry.genres):
                    results.append(entry)

        return sorted(results, key=lambda e: e.holos_interest, reverse=True)[:limit]

    # =========================================================================
    # STATISTIKEN & UTILS
    # =========================================================================

    def get_stats(self) -> Dict[str, Dict]:
        """Gibt Statistiken über die Datenbanken zurück."""
        def calc_stats(db: Dict[str, MediaEntry]) -> Dict:
            if not db:
                return {"total": 0, "seeds": 0, "discovered": 0, "avg_interest": 0}

            entries = list(db.values())
            seeds = len([e for e in entries if e.is_seed])
            avg_interest = sum(e.holos_interest for e in entries) / len(entries)

            return {
                "total": len(entries),
                "seeds": seeds,
                "discovered": len(entries) - seeds,
                "avg_interest": round(avg_interest, 2),
            }

        return {
            "anime": calc_stats(self.anime_db),
            "games": calc_stats(self.games_db),
            "music": calc_stats(self.music_db),
        }

    def get_favorites(self, media_type: str = None, limit: int = 10) -> List[MediaEntry]:
        """Gibt Holos Favoriten zurück (höchstes Interest)."""
        entries = []

        if media_type in [None, "anime"]:
            entries.extend(self.anime_db.values())
        if media_type in [None, "game"]:
            entries.extend(self.games_db.values())
        if media_type in [None, "music"]:
            entries.extend(self.music_db.values())

        return sorted(entries, key=lambda e: e.holos_interest, reverse=True)[:limit]

    def get_random_recommendation(self, media_type: str = None) -> Optional[MediaEntry]:
        """Gibt eine zufällige Empfehlung basierend auf Holos Geschmack."""
        if media_type == "anime":
            return self.get_fresh_anime()
        elif media_type == "game":
            return self.get_fresh_game()
        elif media_type == "music":
            return self.get_fresh_music()
        else:
            # Zufälliger Typ
            choice = random.choice(["anime", "game", "music"])
            return self.get_random_recommendation(choice)

    def get_related(self, entry: MediaEntry, limit: int = 5) -> List[MediaEntry]:
        """Findet ähnliche Medien basierend auf Genres."""
        results = []

        # Gleicher Medientyp
        db = {"anime": self.anime_db, "game": self.games_db, "music": self.music_db}.get(entry.media_type, {})

        for other in db.values():
            if other.id == entry.id:
                continue

            # Zähle überlappende Genres
            overlap = len(set(entry.genres) & set(other.genres))
            if overlap > 0:
                results.append((overlap, other))

        # Sortiere nach Overlap, dann Interest
        results.sort(key=lambda x: (x[0], x[1].holos_interest), reverse=True)
        return [e for _, e in results[:limit]]


# =============================================================================
# SINGLETON & HELPER
# =============================================================================

_discovery_instance: Optional[MediaDiscoverySystem] = None


def get_media_discovery(data_dir: Path = None) -> MediaDiscoverySystem:
    """
    Gibt die Singleton-Instanz des MediaDiscoverySystem zurück.

    Args:
        data_dir: Optionales Datenverzeichnis

    Returns:
        MediaDiscoverySystem Instanz
    """
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = MediaDiscoverySystem(data_dir)
    return _discovery_instance


def reset_discovery_instance():
    """Setzt die Singleton-Instanz zurück (für Tests)."""
    global _discovery_instance
    _discovery_instance = None


# =============================================================================
# TEST & DEMO
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 70)
    print("HOLO MEDIA DISCOVERY SYSTEM v3.0 - COMPLETE EDITION")
    print("=" * 70)

    # Initialisiere System
    discovery = MediaDiscoverySystem(data_dir=Path("./test_discovery_v3_full"))
    stats = discovery.get_stats()

    print(f"\n📊 STATISTIKEN:")
    print(f"   Anime: {stats['anime']['total']} ({stats['anime']['seeds']} seeds, {stats['anime']['discovered']} discovered)")
    print(f"   Games: {stats['games']['total']} ({stats['games']['seeds']} seeds)")
    print(f"   Musik: {stats['music']['total']} ({stats['music']['seeds']} seeds)")
    print(f"   TOTAL: {stats['anime']['total'] + stats['games']['total'] + stats['music']['total']} Einträge!")

    print(f"\n💕 HOLOS LIEBLINGS-GENRES (Anime):")
    for genre, level in PreferenceAdapter.get_loved_genres("anime")[:5]:
        print(f"   {genre}: {level:.1f}")

    print(f"\n💔 HOLOS ABNEIGUNGEN:")
    for genre in PreferenceAdapter.get_disliked_genres("anime"):
        print(f"   ✗ {genre}")

    print(f"\n📺 FRISCHE ANIME EMPFEHLUNGEN:")
    for _ in range(5):
        anime = discovery.get_fresh_anime()
        if anime:
            print(f"   • {anime.title}")
            print(f"     \"{anime.holos_thoughts[:70]}...\"")

    print(f"\n🎮 FRISCHE GAME EMPFEHLUNGEN:")
    for _ in range(5):
        game = discovery.get_fresh_game()
        if game:
            print(f"   • {game.title} ({game.developer})")
            tips = game.tips[0] if game.tips else "Keine Tips"
            print(f"     Tip: {tips[:60]}...")

    print(f"\n🎵 FRISCHE MUSIK EMPFEHLUNGEN:")
    for _ in range(5):
        music = discovery.get_fresh_music()
        if music:
            print(f"   • {music.title} - {music.artist}")
            if music.known_from:
                print(f"     Bekannt aus: {music.known_from}")

    print(f"\n🔍 SUCHE TEST: 'slice of life'")
    results = discovery.search("slice of life")
    for r in results[:3]:
        print(f"   • {r.title} ({r.media_type})")

    print(f"\n⭐ HOLOS TOP FAVORITEN:")
    for fav in discovery.get_favorites(limit=5):
        print(f"   • {fav.title} (Interest: {fav.holos_interest:.2f})")

    print("\n" + "=" * 70)
    print("✓ SYSTEM VOLLSTÄNDIG INITIALISIERT!")
    print("=" * 70)
