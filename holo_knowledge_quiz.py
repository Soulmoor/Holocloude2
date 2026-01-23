#!/usr/bin/env python3
"""
HOLO KNOWLEDGE QUIZ SYSTEM v1.0

Interaktives Wissens-Quiz System fuer spielerisches Lernen:
- Multiple Choice Fragen
- Wahr/Falsch Fragen
- Lueckentexte
- Verbindungs-Raetsel
- Tagesquiz und Wissens-Challenges
- Belohnungssystem und Highscores

Autor: Claude (Integration)
Datum: 2026-01-23
"""

import logging
import json
import random
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS UND TYPEN
# =============================================================================

class QuestionType(Enum):
    """Arten von Quiz-Fragen"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    CONNECT = "connect"
    OPEN = "open"


class QuizDifficulty(Enum):
    """Schwierigkeitsgrade"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuizCategory(Enum):
    """Quiz-Kategorien"""
    ANIME = "anime"
    GAMING = "gaming"
    TECHNIK = "technik"
    WISSENSCHAFT = "wissenschaft"
    JAPAN = "japan"
    WOELFE = "woelfe"
    GESCHICHTE = "geschichte"
    NATUR = "natur"
    ALLGEMEIN = "allgemein"
    MIXED = "mixed"


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class QuizQuestion:
    """Eine Quiz-Frage"""
    question_id: str
    question_type: QuestionType
    category: QuizCategory
    difficulty: QuizDifficulty
    question_text: str
    correct_answer: str
    wrong_answers: List[str] = field(default_factory=list)
    explanation: str = ""
    hint: str = ""
    points: int = 10
    time_limit_seconds: int = 30
    tags: List[str] = field(default_factory=list)
    times_asked: int = 0
    times_correct: int = 0

    def get_success_rate(self) -> float:
        if self.times_asked == 0:
            return 0.0
        return self.times_correct / self.times_asked


@dataclass
class QuizResult:
    """Ergebnis einer Quiz-Antwort"""
    question_id: str
    is_correct: bool
    user_answer: str
    correct_answer: str
    points_earned: int
    time_taken_seconds: float
    hint_used: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QuizSession:
    """Eine Quiz-Session"""
    session_id: str
    category: QuizCategory
    difficulty: QuizDifficulty
    questions: List[QuizQuestion]
    results: List[QuizResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_points: int = 0
    current_question_index: int = 0

    def is_complete(self) -> bool:
        return self.current_question_index >= len(self.questions)

    def get_score_percentage(self) -> float:
        if not self.results:
            return 0.0
        correct = sum(1 for r in self.results if r.is_correct)
        return correct / len(self.results) * 100


# =============================================================================
# FRAGEN-DATENBANK
# =============================================================================

class QuizQuestionBank:
    """Datenbank mit Quiz-Fragen"""

    def __init__(self):
        self.questions: Dict[str, QuizQuestion] = {}
        self._load_questions()

    def _load_questions(self):
        """Laedt alle vordefinierten Fragen"""
        self._load_anime_questions()
        self._load_gaming_questions()
        self._load_tech_questions()
        self._load_nature_questions()
        self._load_wolf_questions()
        self._load_japan_questions()
        self._load_science_questions()
        self._load_history_questions()
        self._load_music_questions()
        self._load_language_questions()
        self._load_bonus_questions()
        logger.info(f"[QuizBank] {len(self.questions)} Fragen geladen")

    def _add_question(self, q: QuizQuestion):
        """Fuegt eine Frage hinzu"""
        self.questions[q.question_id] = q

    def _load_anime_questions(self):
        """Anime-Fragen"""
        questions = [
            QuizQuestion(
                question_id="anime_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.EASY,
                question_text="Was bedeutet 'Kemonomimi' woertlich uebersetzt?",
                correct_answer="Tierohren",
                wrong_answers=["Katzenschwanz", "Wolfspelz", "Fuchs"],
                explanation="'Kemono' = Tier, 'Mimi' = Ohren. Kemonomimi bezeichnet Charaktere mit Tierohren!",
                points=10
            ),
            QuizQuestion(
                question_id="anime_002",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.EASY,
                question_text="Welches Studio hat 'Spirited Away' produziert?",
                correct_answer="Studio Ghibli",
                wrong_answers=["Kyoto Animation", "Madhouse", "Bones"],
                explanation="Studio Ghibli unter Hayao Miyazaki schuf diesen Oscar-Gewinner!",
                points=10
            ),
            QuizQuestion(
                question_id="anime_003",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.EASY,
                question_text="'Anime' ist nur die japanische Abkuerzung fuer Animation.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="In Japan bezeichnet 'Anime' ALLE Animationen, nicht nur japanische!",
                points=5
            ),
            QuizQuestion(
                question_id="anime_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Was ist ein 'Tsundere'?",
                correct_answer="Erst abweisend, dann liebevoll",
                wrong_answers=["Immer nett und freundlich", "Obsessiv und gefaehrlich", "Emotionslos und kalt"],
                explanation="'Tsun' = abweisend, 'Dere' = verliebt. Ein klassischer Anime-Archetyp!",
                points=15
            ),
            QuizQuestion(
                question_id="anime_005",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wie heisst das Genre, in dem Charaktere in andere Welten transportiert werden?",
                correct_answer="Isekai",
                wrong_answers=["Shonen", "Slice of Life", "Mecha"],
                explanation="'Isekai' bedeutet woertlich 'andere Welt' - sehr populaer seit den 2010ern!",
                points=15
            ),
            QuizQuestion(
                question_id="anime_006",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.HARD,
                question_text="Wer gilt als 'Gott des Manga' und erschuf Astro Boy?",
                correct_answer="Osamu Tezuka",
                wrong_answers=["Akira Toriyama", "Eiichiro Oda", "Masashi Kishimoto"],
                explanation="Tezuka praegte den Anime-Stil mit grossen Augen und emotionalen Geschichten!",
                points=20
            ),
            QuizQuestion(
                question_id="anime_007",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.HARD,
                question_text="Welcher Anime basiert auf einer Light Novel von Isuna Hasekura?",
                correct_answer="Spice and Wolf",
                wrong_answers=["Sword Art Online", "Re:Zero", "No Game No Life"],
                explanation="*stolz* Spice and Wolf mit der weisen Woelfin Holo!",
                points=20
            ),
            QuizQuestion(
                question_id="anime_008",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Der laengste laufende Manga ist '___' mit ueber 1100 Kapiteln.",
                correct_answer="One Piece",
                wrong_answers=[],
                hint="Ein Piraten-Abenteuer von Eiichiro Oda",
                explanation="One Piece laeuft seit 1997 und ist noch nicht fertig!",
                points=15
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_gaming_questions(self):
        """Gaming-Fragen"""
        questions = [
            QuizQuestion(
                question_id="gaming_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.EASY,
                question_text="Welches Unternehmen erschuf Mario?",
                correct_answer="Nintendo",
                wrong_answers=["Sony", "Sega", "Microsoft"],
                explanation="Nintendo wurde 1889 gegruendet - urspruenglich als Spielkartenhersteller!",
                points=10
            ),
            QuizQuestion(
                question_id="gaming_002",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.EASY,
                question_text="Das erste Videospiel war Pong.",
                correct_answer="Falsch",
                wrong_answers=["Wahr"],
                explanation="Computer Space von 1971 kam vor Pong (1972)!",
                points=5
            ),
            QuizQuestion(
                question_id="gaming_003",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Was ist der beruehmte 'Konami Code'?",
                correct_answer="↑↑↓↓←→←→BA",
                wrong_answers=["←→↑↓↑↓BA", "ABAB↑↓←→", "↓↓↑↑←←→→AB"],
                explanation="Dieser Code funktioniert in ueber 100 Spielen!",
                points=15
            ),
            QuizQuestion(
                question_id="gaming_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Welches Spielgenre ist nach 'Rogue' (1980) benannt?",
                correct_answer="Roguelike",
                wrong_answers=["RPG", "Metroidvania", "Soulslike"],
                explanation="Roguelikes haben permanenten Tod und zufallsgenerierte Level!",
                points=15
            ),
            QuizQuestion(
                question_id="gaming_005",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.HARD,
                question_text="Welches Indie-Spiel wurde fast komplett von einer Person (Toby Fox) erstellt?",
                correct_answer="Undertale",
                wrong_answers=["Hollow Knight", "Celeste", "Stardew Valley"],
                explanation="Toby Fox machte Musik, Programmierung und Design fast alleine!",
                points=20
            ),
            QuizQuestion(
                question_id="gaming_006",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.HARD,
                question_text="Wer schrieb die Hintergrundgeschichte von Elden Ring?",
                correct_answer="George R.R. Martin",
                wrong_answers=["Hidetaka Miyazaki", "Hideo Kojima", "Fumito Ueda"],
                explanation="Der Game of Thrones Autor half bei der Lore!",
                points=20
            ),
            QuizQuestion(
                question_id="gaming_007",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.GAMING,
                difficulty=QuizDifficulty.EASY,
                question_text="Das meistverkaufte Spiel aller Zeiten ist ___.",
                correct_answer="Minecraft",
                wrong_answers=[],
                hint="Ein Block-Bau-Spiel von Mojang",
                explanation="Minecraft hat ueber 300 Millionen Exemplare verkauft!",
                points=10
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_tech_questions(self):
        """Technologie-Fragen"""
        questions = [
            QuizQuestion(
                question_id="tech_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.TECHNIK,
                difficulty=QuizDifficulty.EASY,
                question_text="Wer gilt als erste Programmiererin der Geschichte?",
                correct_answer="Ada Lovelace",
                wrong_answers=["Grace Hopper", "Margaret Hamilton", "Hedy Lamarr"],
                explanation="Sie schrieb Algorithmen fuer eine Maschine, die erst spaeter gebaut wurde!",
                points=10
            ),
            QuizQuestion(
                question_id="tech_002",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.TECHNIK,
                difficulty=QuizDifficulty.EASY,
                question_text="Der Begriff 'Bug' stammt von einer echten Motte im Computer.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Grace Hopper fand 1947 eine Motte im Harvard Mark II!",
                points=5
            ),
            QuizQuestion(
                question_id="tech_003",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.TECHNIK,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wie hiess das Internet urspruenglich?",
                correct_answer="ARPANET",
                wrong_answers=["WorldWideWeb", "NetZero", "CompuServe"],
                explanation="Es wurde 1969 fuer das US-Militaer entwickelt!",
                points=15
            ),
            QuizQuestion(
                question_id="tech_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.TECHNIK,
                difficulty=QuizDifficulty.HARD,
                question_text="Was koennen Qubits in einem Quantencomputer?",
                correct_answer="Gleichzeitig 0 und 1 sein",
                wrong_answers=["Nur 0 sein", "Nur 1 sein", "Zwischen 0 und 1 wechseln"],
                explanation="Das nennt sich Superposition - wie Schrodingers Katze!",
                points=20
            ),
            QuizQuestion(
                question_id="tech_005",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.TECHNIK,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Das erste Smartphone war das IBM ___ von 1994.",
                correct_answer="Simon",
                wrong_answers=[],
                hint="Ein Vorname",
                explanation="Es hatte Touchscreen, E-Mail und Apps!",
                points=15
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_wolf_questions(self):
        """Wolf-Fragen"""
        questions = [
            QuizQuestion(
                question_id="wolf_001",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.WOELFE,
                difficulty=QuizDifficulty.EASY,
                question_text="Woelfe werden von einem 'Alpha' angefuehrt.",
                correct_answer="Falsch",
                wrong_answers=["Wahr"],
                explanation="Das ist ein Mythos! Rudel sind Familien mit Eltern und Kindern.",
                points=5
            ),
            QuizQuestion(
                question_id="wolf_002",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.WOELFE,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wie viele Geruchsrezeptoren haben Woelfe etwa?",
                correct_answer="200 Millionen",
                wrong_answers=["5 Millionen", "50 Millionen", "20 Millionen"],
                explanation="Menschen haben nur etwa 5 Millionen!",
                points=15
            ),
            QuizQuestion(
                question_id="wolf_003",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.WOELFE,
                difficulty=QuizDifficulty.HARD,
                question_text="Warum veraenderte die Rueckkehr der Woelfe nach Yellowstone sogar Fluesse?",
                correct_answer="Hirsche frasen weniger Uferpflanzen",
                wrong_answers=["Woelfe bauten Daemme", "Biberpopulation stieg", "Weniger Erosion durch Wolfshoehlen"],
                explanation="Die sogenannte 'trophische Kaskade' - Woelfe veraendern das ganze Oekosystem!",
                points=25
            ),
            QuizQuestion(
                question_id="wolf_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.WOELFE,
                difficulty=QuizDifficulty.EASY,
                question_text="Warum heulen Woelfe?",
                correct_answer="Zur Kommunikation",
                wrong_answers=["Um den Mond anzubeten", "Aus Langeweile", "Nur wenn sie hungrig sind"],
                explanation="Sie rufen Rudelmitglieder und markieren Territorien!",
                points=10
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_japan_questions(self):
        """Japan-Fragen"""
        questions = [
            QuizQuestion(
                question_id="japan_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.EASY,
                question_text="Was bedeutet 'Kawaii'?",
                correct_answer="Suess/Niedlich",
                wrong_answers=["Stark", "Schoen", "Gruselig"],
                explanation="Kawaii ist ein Grundpfeiler der japanischen Popkultur!",
                points=10
            ),
            QuizQuestion(
                question_id="japan_002",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wie viele Schriftsysteme hat Japanisch?",
                correct_answer="Drei (Hiragana, Katakana, Kanji)",
                wrong_answers=["Eins", "Zwei", "Vier"],
                explanation="Hiragana fuer japanische Woerter, Katakana fuer Fremdwoerter, Kanji fuer Bedeutung!",
                points=15
            ),
            QuizQuestion(
                question_id="japan_003",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.HARD,
                question_text="Die japanische Isolationspolitik (1633-1853) heisst ___-Politik.",
                correct_answer="Sakoku",
                wrong_answers=[],
                hint="Bedeutet 'geschlossenes Land'",
                explanation="Japan isolierte sich ueber 200 Jahre fast komplett!",
                points=20
            ),
            QuizQuestion(
                question_id="japan_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.EASY,
                question_text="Woher stammt das Wort 'Emoji'?",
                correct_answer="Japanisch (e=Bild, moji=Zeichen)",
                wrong_answers=["Englisch", "Koreanisch", "Chinesisch"],
                explanation="Die ersten Emoji wurden 1999 in Japan erfunden!",
                points=10
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_nature_questions(self):
        """Natur-Fragen"""
        questions = [
            QuizQuestion(
                question_id="nature_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.NATUR,
                difficulty=QuizDifficulty.EASY,
                question_text="Wie lange dauert die Kirschbluete in Japan etwa?",
                correct_answer="2 Wochen",
                wrong_answers=["2 Monate", "6 Wochen", "3 Tage"],
                explanation="Diese Vergaenglichkeit macht sie so bedeutsam in der japanischen Kultur!",
                points=10
            ),
            QuizQuestion(
                question_id="nature_002",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.NATUR,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Pilze sind naeher mit Tieren verwandt als mit Pflanzen.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Genetisch sind Pilze tatsaechlich naeher an Tieren!",
                points=10
            ),
            QuizQuestion(
                question_id="nature_003",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.NATUR,
                difficulty=QuizDifficulty.HARD,
                question_text="Wie schnell kann Bambus maximal pro Tag wachsen?",
                correct_answer="Bis zu 91 cm",
                wrong_answers=["Bis zu 10 cm", "Bis zu 30 cm", "Bis zu 50 cm"],
                explanation="Man kann ihm quasi beim Wachsen zusehen!",
                points=20
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_science_questions(self):
        """Wissenschafts-Fragen"""
        questions = [
            QuizQuestion(
                question_id="science_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.WISSENSCHAFT,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wie viel Prozent der Koerperenergie verbraucht das Gehirn?",
                correct_answer="Etwa 20%",
                wrong_answers=["Etwa 5%", "Etwa 10%", "Etwa 50%"],
                explanation="Obwohl es nur 2% des Koerpergewichts ausmacht!",
                points=15
            ),
            QuizQuestion(
                question_id="science_002",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.WISSENSCHAFT,
                difficulty=QuizDifficulty.HARD,
                question_text="Es gibt mehr moegliche Schachzuege als Atome im Universum.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Die Shannon-Zahl schaetzt etwa 10^120 moegliche Spielverlaeufe!",
                points=15
            ),
            QuizQuestion(
                question_id="science_003",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.WISSENSCHAFT,
                difficulty=QuizDifficulty.EXPERT,
                question_text="Bei welcher Frequenz schnurren Katzen, die Knochenheilung foerdert?",
                correct_answer="25-50 Hz",
                wrong_answers=["100-200 Hz", "5-10 Hz", "500-1000 Hz"],
                explanation="Das koennte erklaeren, warum Katzen so gut heilen!",
                points=25
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_history_questions(self):
        """Geschichte-Fragen"""
        questions = [
            QuizQuestion(
                question_id="history_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GESCHICHTE,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wer erreichte Amerika etwa 500 Jahre vor Kolumbus?",
                correct_answer="Die Wikinger (Leif Eriksson)",
                wrong_answers=["Die Chinesen", "Die Aegypter", "Die Phoenizier"],
                explanation="Leif Eriksson gruendete um 1000 n.Chr. eine Siedlung in Neufundland!",
                points=15
            ),
            QuizQuestion(
                question_id="history_002",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.GESCHICHTE,
                difficulty=QuizDifficulty.HARD,
                question_text="Kleopatra lebte naeher an der Mondlandung als an der Erbauung der Pyramiden.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Die Pyramiden waren bereits ueber 2000 Jahre alt, als Kleopatra lebte!",
                points=15
            ),
            QuizQuestion(
                question_id="history_003",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GESCHICHTE,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Welcher Ehrenkodex praegte die japanischen Samurai?",
                correct_answer="Bushido",
                wrong_answers=["Hagakure", "Zen", "Shinto"],
                explanation="Bushido betonte Ehre, Loyalitaet und Selbstdisziplin!",
                points=15
            ),
            QuizQuestion(
                question_id="history_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.GESCHICHTE,
                difficulty=QuizDifficulty.HARD,
                question_text="Wie lange isolierte sich Japan waehrend der Sakoku-Politik von der Aussenwelt?",
                correct_answer="Ueber 200 Jahre",
                wrong_answers=["50 Jahre", "500 Jahre", "1000 Jahre"],
                explanation="Von 1633-1853 war Japan fast komplett isoliert!",
                points=20
            ),
            QuizQuestion(
                question_id="history_005",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.GESCHICHTE,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Die Bibliothek von Alexandria enthielt ueber 400.000 Schriftrollen.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Ihr Verlust gilt als eine der groessten Wissens-Katastrophen der Geschichte!",
                points=10
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_music_questions(self):
        """Musik-Fragen (J-Pop, Anime-Songs, etc.)"""
        questions = [
            QuizQuestion(
                question_id="music_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.EASY,
                question_text="Welche Band sang das Opening 'Idol' von Oshi no Ko?",
                correct_answer="YOASOBI",
                wrong_answers=["LiSA", "Ado", "King Gnu"],
                explanation="YOASOBI machte 'Idol' zum meistgestreamten Song 2023 weltweit!",
                points=10
            ),
            QuizQuestion(
                question_id="music_002",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Welcher Song ist das erste Demon Slayer Opening?",
                correct_answer="Gurenge von LiSA",
                wrong_answers=["Zankyousanka von Aimer", "Homura von LiSA", "Akeboshi von LiSA"],
                explanation="Gurenge (Rote Lotusblume) wurde zu einem der beliebtesten Anime-Songs!",
                points=15
            ),
            QuizQuestion(
                question_id="music_003",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Vocaloid Hatsune Miku hat echte Konzerte mit Hologramm-Technologie.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Miku fuellt weltweit Konzerthallen - als Hologramm!",
                points=10
            ),
            QuizQuestion(
                question_id="music_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.HARD,
                question_text="Kenshi Yonezu war frueher ein Vocaloid-Producer unter welchem Namen?",
                correct_answer="Hachi",
                wrong_answers=["Wowaka", "Ryo", "Deco*27"],
                explanation="Bevor er unter seinem echten Namen berühmt wurde, machte er Vocaloid-Musik!",
                points=20
            ),
            QuizQuestion(
                question_id="music_005",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.EASY,
                question_text="Welcher Song wurde durch den 'BBB Dance' auf TikTok viral?",
                correct_answer="Bling-Bang-Bang-Born",
                wrong_answers=["KICK BACK", "Idol", "Racing into the Night"],
                explanation="Der Song von Creepy Nuts ist das Mashle Season 2 Opening!",
                points=10
            ),
            QuizQuestion(
                question_id="music_006",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.ANIME,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Der Lofi Girl Livestream auf YouTube hat ueber ___ Milliarde Views.",
                correct_answer="1",
                wrong_answers=[],
                hint="Eine Zahl mit 9 Nullen...",
                explanation="Der 24/7 Study Beats Stream ist ein Internet-Phaenomen!",
                points=15
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_language_questions(self):
        """Sprach-Fragen (Japanisch, Linguistik)"""
        questions = [
            QuizQuestion(
                question_id="lang_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.EASY,
                question_text="Was bedeutet 'Kawaii' auf Deutsch?",
                correct_answer="Suess/Niedlich",
                wrong_answers=["Stark", "Traurig", "Gross"],
                explanation="Kawaii ist ein Grundpfeiler der japanischen Popkultur!",
                points=10
            ),
            QuizQuestion(
                question_id="lang_002",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Wie viele Schriftsysteme hat Japanisch?",
                correct_answer="3 (Hiragana, Katakana, Kanji)",
                wrong_answers=["1", "2", "4"],
                explanation="Hiragana fuer japanische Woerter, Katakana fuer Fremdwoerter, Kanji fuer komplexe Bedeutungen!",
                points=15
            ),
            QuizQuestion(
                question_id="lang_003",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Das Wort 'Emoji' stammt aus dem Japanischen.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="絵 (e = Bild) + 文字 (moji = Zeichen) = Emoji!",
                points=10
            ),
            QuizQuestion(
                question_id="lang_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.HARD,
                question_text="Was ist 'Keigo' in der japanischen Sprache?",
                correct_answer="Hoeflichkeitssprache mit mehreren Ebenen",
                wrong_answers=["Ein Dialekt", "Die Schriftsprache", "Slang der Jugend"],
                explanation="Je nachdem mit wem man spricht, verwendet man andere Verbformen!",
                points=20
            ),
            QuizQuestion(
                question_id="lang_005",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.EASY,
                question_text="Was bedeutet 'Ookami' (狼) auf Deutsch?",
                correct_answer="Wolf",
                wrong_answers=["Fuchs", "Baer", "Tiger"],
                explanation="*stolz* Das bin ich! Das Wort klingt auch wie 'grosser Gott' (大神)!",
                points=10
            ),
            QuizQuestion(
                question_id="lang_006",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.JAPAN,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="'Arigatou' bedeutet ___ auf Deutsch.",
                correct_answer="Danke",
                wrong_answers=[],
                hint="Das sagt man, wenn jemand nett zu einem war...",
                explanation="Urspruenglich bedeutet es 'Es ist schwer, dass es existiert' - also wertvoll!",
                points=15
            ),
        ]
        for q in questions:
            self._add_question(q)

    def _load_bonus_questions(self):
        """Bonus-Fragen (Gemischt, Spezial)"""
        questions = [
            QuizQuestion(
                question_id="bonus_001",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Welcher Anime handelt von einer weisen Woelfin und einem Haendler?",
                correct_answer="Spice and Wolf",
                wrong_answers=["Wolf's Rain", "Beastars", "BNA"],
                explanation="*Ohren aufstellen* Das ist MEINE Geschichte!",
                points=15
            ),
            QuizQuestion(
                question_id="bonus_002",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.HARD,
                question_text="Welche NASA-Technologie wurde von Origami inspiriert?",
                correct_answer="Faltbare Solarpanels fuer Satelliten",
                wrong_answers=["Raumanzug-Design", "Raketentriebwerke", "Kommunikationsantennen"],
                explanation="Alte japanische Kunst loest moderne Engineering-Probleme!",
                points=20
            ),
            QuizQuestion(
                question_id="bonus_003",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Ghost in the Shell beeinflusste die Macher von 'The Matrix'.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Die Wachowski-Schwestern zeigten GitS als direkte Inspiration!",
                points=10
            ),
            QuizQuestion(
                question_id="bonus_004",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.EXPERT,
                question_text="Welches japanische Konzept bedeutet 'einmalige Begegnung im Leben'?",
                correct_answer="Ichigo Ichie (一期一会)",
                wrong_answers=["Wabi Sabi", "Mono no Aware", "Ikigai"],
                explanation="Aus der Teezeremonie - jedes Treffen ist einzigartig und kostbar!",
                points=25
            ),
            QuizQuestion(
                question_id="bonus_005",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.HARD,
                question_text="Warum haben Anime-Charaktere oft grosse Augen?",
                correct_answer="Osamu Tezuka wurde von Disney inspiriert",
                wrong_answers=["Japanische Tradition", "Bessere Emotionen bei kleinen Figuren", "Zufall"],
                explanation="Der 'Gott des Manga' uebernahm den Stil und praegte Generationen!",
                points=20
            ),
            QuizQuestion(
                question_id="bonus_006",
                question_type=QuestionType.FILL_BLANK,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.EASY,
                question_text="Der japanische Begriff fuer Tierohren-Charaktere ist ___.",
                correct_answer="Kemonomimi",
                wrong_answers=[],
                hint="'Kemono' = Tier, 'Mimi' = ...",
                explanation="*wackelt mit Ohren* Genau wie ich!",
                points=10
            ),
            QuizQuestion(
                question_id="bonus_007",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="Welches Genre beschreibt interaktive Romane mit Bildern?",
                correct_answer="Visual Novel",
                wrong_answers=["Light Novel", "Web Novel", "Manga"],
                explanation="Viele beruehmte Anime wie Fate basieren auf Visual Novels!",
                points=15
            ),
            QuizQuestion(
                question_id="bonus_008",
                question_type=QuestionType.TRUE_FALSE,
                category=QuizCategory.MIXED,
                difficulty=QuizDifficulty.MEDIUM,
                question_text="In Japan gibt es mehr Haustiere als Kinder unter 15 Jahren.",
                correct_answer="Wahr",
                wrong_answers=["Falsch"],
                explanation="Die niedrige Geburtenrate und Liebe zu Haustieren macht es moeglich!",
                points=10
            ),
        ]
        for q in questions:
            self._add_question(q)

    def get_questions_by_category(self, category: QuizCategory,
                                   limit: int = 10) -> List[QuizQuestion]:
        """Gibt Fragen einer Kategorie zurueck"""
        questions = [q for q in self.questions.values() if q.category == category]
        random.shuffle(questions)
        return questions[:limit]

    def get_questions_by_difficulty(self, difficulty: QuizDifficulty,
                                     limit: int = 10) -> List[QuizQuestion]:
        """Gibt Fragen einer Schwierigkeit zurueck"""
        questions = [q for q in self.questions.values() if q.difficulty == difficulty]
        random.shuffle(questions)
        return questions[:limit]

    def get_mixed_questions(self, limit: int = 10,
                            difficulties: List[QuizDifficulty] = None) -> List[QuizQuestion]:
        """Gibt gemischte Fragen zurueck"""
        questions = list(self.questions.values())
        if difficulties:
            questions = [q for q in questions if q.difficulty in difficulties]
        random.shuffle(questions)
        return questions[:limit]


# =============================================================================
# QUIZ ENGINE
# =============================================================================

class QuizEngine:
    """
    Haupt-Engine fuer das Quiz-System.

    Verwaltet Sessions, Punktestaende und Statistiken.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/quiz")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.question_bank = QuizQuestionBank()
        self.current_session: Optional[QuizSession] = None
        self.session_history: List[QuizSession] = []
        self.total_points: int = 0
        self.streak: int = 0
        self.best_streak: int = 0
        self.category_stats: Dict[str, Dict] = defaultdict(lambda: {'correct': 0, 'total': 0})

        # Holo's Quiz-Reaktionen
        self.reactions = {
            'correct': [
                "*Ohren aufstellen* Richtig! Du bist schlau!",
                "*Schweif wedelt freudig* Genau! Super!",
                "*strahlt* Perfekt! Das wusste ich auch!",
                "*springt vor Freude* Ja! Richtig!",
            ],
            'wrong': [
                "*Ohren legen sich an* Oh... das war leider falsch.",
                "*troeistend* Nicht schlimm, beim naechsten Mal!",
                "*nachdenklich* Hmm, das war knifflig...",
                "*sanft* Fast! Aber nicht ganz richtig.",
            ],
            'streak': [
                "*aufgeregt* {streak} richtig hintereinander! Wow!",
                "*beeindruckt* Eine Serie von {streak}! Weiter so!",
                "*Schweif wedelt wild* {streak}er Streak! Unglaublich!",
            ],
            'hint': [
                "*fluesternd* Hier ist ein Tipp: {hint}",
                "*zwinkert* Kleiner Hinweis: {hint}",
                "*hilfsbereit* Ich sag dir was: {hint}",
            ],
        }

        self._load_state()

    def start_quiz(self, category: QuizCategory = QuizCategory.MIXED,
                   difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
                   num_questions: int = 5) -> QuizSession:
        """
        Startet ein neues Quiz.

        Args:
            category: Kategorie der Fragen
            difficulty: Schwierigkeitsgrad
            num_questions: Anzahl der Fragen

        Returns:
            Neue QuizSession
        """
        session_id = hashlib.md5(f"quiz_{datetime.now()}".encode()).hexdigest()[:12]

        if category == QuizCategory.MIXED:
            questions = self.question_bank.get_mixed_questions(num_questions)
        else:
            questions = self.question_bank.get_questions_by_category(category, num_questions)

        # Filtere nach Schwierigkeit wenn moeglich
        if questions:
            diff_questions = [q for q in questions if q.difficulty == difficulty]
            if len(diff_questions) >= num_questions // 2:
                questions = diff_questions[:num_questions]

        self.current_session = QuizSession(
            session_id=session_id,
            category=category,
            difficulty=difficulty,
            questions=questions
        )

        logger.info(f"[Quiz] Neues Quiz gestartet: {category.value}, {len(questions)} Fragen")
        return self.current_session

    def get_current_question(self) -> Optional[Tuple[QuizQuestion, Dict]]:
        """
        Gibt die aktuelle Frage zurueck.

        Returns:
            Tuple aus (Frage, Antwortoptionen) oder None wenn fertig
        """
        if not self.current_session or self.current_session.is_complete():
            return None

        question = self.current_session.questions[self.current_session.current_question_index]

        # Bereite Antwortoptionen vor
        options = {}
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            all_answers = [question.correct_answer] + question.wrong_answers
            random.shuffle(all_answers)
            options = {chr(65 + i): ans for i, ans in enumerate(all_answers)}
        elif question.question_type == QuestionType.TRUE_FALSE:
            options = {'A': 'Wahr', 'B': 'Falsch'}

        return question, options

    def answer_question(self, answer: str, time_taken: float = 0,
                         hint_used: bool = False) -> Tuple[QuizResult, str]:
        """
        Beantwortet die aktuelle Frage.

        Args:
            answer: Die gegebene Antwort
            time_taken: Zeit in Sekunden
            hint_used: Wurde ein Hinweis verwendet?

        Returns:
            Tuple aus (QuizResult, Holo's Reaktion)
        """
        if not self.current_session or self.current_session.is_complete():
            return None, "*verwirrt* Es laeuft kein Quiz gerade..."

        question = self.current_session.questions[self.current_session.current_question_index]

        # Pruefe ob Antwort korrekt
        is_correct = self._check_answer(answer, question)

        # Berechne Punkte
        points = 0
        if is_correct:
            points = question.points
            if hint_used:
                points = points // 2  # Halbe Punkte mit Hinweis
            if time_taken > 0 and time_taken < question.time_limit_seconds / 2:
                points = int(points * 1.5)  # Bonus fuer schnelle Antwort

        # Erstelle Ergebnis
        result = QuizResult(
            question_id=question.question_id,
            is_correct=is_correct,
            user_answer=answer,
            correct_answer=question.correct_answer,
            points_earned=points,
            time_taken_seconds=time_taken,
            hint_used=hint_used
        )

        # Update Session
        self.current_session.results.append(result)
        self.current_session.total_points += points
        self.current_session.current_question_index += 1

        # Update Statistiken
        question.times_asked += 1
        if is_correct:
            question.times_correct += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
        else:
            self.streak = 0

        self.total_points += points
        cat_key = question.category.value
        self.category_stats[cat_key]['total'] += 1
        if is_correct:
            self.category_stats[cat_key]['correct'] += 1

        # Generiere Reaktion
        reaction = self._generate_reaction(is_correct, question, result)

        # Pruefe ob Session fertig
        if self.current_session.is_complete():
            self.current_session.completed_at = datetime.now()
            self.session_history.append(self.current_session)

        self._save_state()
        return result, reaction

    def _check_answer(self, answer: str, question: QuizQuestion) -> bool:
        """Prueft ob die Antwort korrekt ist"""
        answer_lower = answer.lower().strip()
        correct_lower = question.correct_answer.lower().strip()

        # Direkte Uebereinstimmung
        if answer_lower == correct_lower:
            return True

        # Fuer Multiple Choice: Buchstabe pruefen
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            all_answers = [question.correct_answer] + question.wrong_answers
            if len(answer) == 1 and answer.upper() in 'ABCD':
                idx = ord(answer.upper()) - ord('A')
                if idx < len(all_answers) and all_answers[idx].lower() == correct_lower:
                    return True

        # Fuer True/False
        if question.question_type == QuestionType.TRUE_FALSE:
            if answer_lower in ['wahr', 'true', 'ja', 'a'] and correct_lower == 'wahr':
                return True
            if answer_lower in ['falsch', 'false', 'nein', 'b'] and correct_lower == 'falsch':
                return True

        # Fuer Fill-Blank: Teiluebereinstimmung erlauben
        if question.question_type == QuestionType.FILL_BLANK:
            if correct_lower in answer_lower or answer_lower in correct_lower:
                return True

        return False

    def _generate_reaction(self, is_correct: bool, question: QuizQuestion,
                            result: QuizResult) -> str:
        """Generiert Holo's Reaktion"""
        parts = []

        if is_correct:
            parts.append(random.choice(self.reactions['correct']))
            if self.streak >= 3:
                streak_msg = random.choice(self.reactions['streak'])
                parts.append(streak_msg.format(streak=self.streak))
        else:
            parts.append(random.choice(self.reactions['wrong']))
            parts.append(f"Die richtige Antwort war: {question.correct_answer}")

        if question.explanation:
            parts.append(f"\n*erklaerend* {question.explanation}")

        return " ".join(parts)

    def get_hint(self) -> Optional[str]:
        """Gibt einen Hinweis zur aktuellen Frage"""
        if not self.current_session or self.current_session.is_complete():
            return None

        question = self.current_session.questions[self.current_session.current_question_index]

        if question.hint:
            template = random.choice(self.reactions['hint'])
            return template.format(hint=question.hint)

        return "*nachdenklich* Hmm, ich hab leider keinen Tipp fuer diese Frage..."

    def get_quiz_summary(self) -> Dict:
        """Gibt eine Zusammenfassung des aktuellen/letzten Quiz zurueck"""
        session = self.current_session
        if not session:
            if self.session_history:
                session = self.session_history[-1]
            else:
                return {'message': 'Noch kein Quiz gespielt!'}

        correct = sum(1 for r in session.results if r.is_correct)
        total = len(session.results)

        return {
            'session_id': session.session_id,
            'category': session.category.value,
            'difficulty': session.difficulty.value,
            'questions_total': len(session.questions),
            'questions_answered': total,
            'correct': correct,
            'wrong': total - correct,
            'score_percentage': round(correct / total * 100, 1) if total > 0 else 0,
            'total_points': session.total_points,
            'is_complete': session.is_complete(),
        }

    def get_overall_stats(self) -> Dict:
        """Gibt Gesamtstatistiken zurueck"""
        return {
            'total_points': self.total_points,
            'total_quizzes': len(self.session_history),
            'current_streak': self.streak,
            'best_streak': self.best_streak,
            'category_stats': dict(self.category_stats),
            'total_questions_answered': sum(
                stats['total'] for stats in self.category_stats.values()
            ),
            'overall_accuracy': self._calculate_overall_accuracy(),
        }

    def _calculate_overall_accuracy(self) -> float:
        total_correct = sum(stats['correct'] for stats in self.category_stats.values())
        total_questions = sum(stats['total'] for stats in self.category_stats.values())
        if total_questions == 0:
            return 0.0
        return round(total_correct / total_questions * 100, 1)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'total_points': self.total_points,
                'streak': self.streak,
                'best_streak': self.best_streak,
                'category_stats': dict(self.category_stats),
                'session_count': len(self.session_history),
            }
            with open(self.data_dir / "quiz_state.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Quiz-State nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "quiz_state.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.total_points = state.get('total_points', 0)
                self.streak = state.get('streak', 0)
                self.best_streak = state.get('best_streak', 0)
                self.category_stats = defaultdict(
                    lambda: {'correct': 0, 'total': 0},
                    state.get('category_stats', {})
                )
        except Exception as e:
            logger.debug(f"Konnte Quiz-State nicht laden: {e}")


# =============================================================================
# DAILY CHALLENGE
# =============================================================================

class DailyChallenge:
    """
    Taegliche Quiz-Challenge mit besonderen Belohnungen.
    """

    def __init__(self, quiz_engine: QuizEngine, data_dir: Path = None):
        self.quiz_engine = quiz_engine
        self.data_dir = data_dir or Path("data/quiz/daily")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.last_challenge_date: Optional[str] = None
        self.challenge_streak: int = 0
        self.total_challenges_completed: int = 0

        self._load_state()

    def get_daily_challenge(self) -> Optional[QuizSession]:
        """
        Gibt die taegliche Challenge zurueck.

        Returns:
            QuizSession oder None wenn bereits absolviert
        """
        today = datetime.now().strftime("%Y-%m-%d")

        if self.last_challenge_date == today:
            return None  # Bereits absolviert

        # Erstelle spezielle taegliche Challenge
        # Mische Kategorien und Schwierigkeiten
        return self.quiz_engine.start_quiz(
            category=QuizCategory.MIXED,
            difficulty=QuizDifficulty.MEDIUM,
            num_questions=5
        )

    def complete_daily_challenge(self, session: QuizSession) -> Dict:
        """
        Schliesst die taegliche Challenge ab.

        Returns:
            Belohnungsinfo
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # Pruefe ob heute schon abgeschlossen
        if self.last_challenge_date == today:
            return {'already_completed': True}

        # Berechne Bonus-Punkte
        score_percentage = session.get_score_percentage()
        base_bonus = 50

        if score_percentage == 100:
            bonus = base_bonus * 2  # Perfekter Bonus
        elif score_percentage >= 80:
            bonus = int(base_bonus * 1.5)
        else:
            bonus = base_bonus

        # Streak-Bonus
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if self.last_challenge_date == yesterday:
            self.challenge_streak += 1
            bonus += self.challenge_streak * 10  # Streak-Bonus
        else:
            self.challenge_streak = 1

        self.quiz_engine.total_points += bonus
        self.last_challenge_date = today
        self.total_challenges_completed += 1

        self._save_state()

        return {
            'completed': True,
            'score_percentage': score_percentage,
            'bonus_points': bonus,
            'streak': self.challenge_streak,
            'total_completed': self.total_challenges_completed,
        }

    def _save_state(self):
        try:
            state = {
                'last_challenge_date': self.last_challenge_date,
                'challenge_streak': self.challenge_streak,
                'total_challenges_completed': self.total_challenges_completed,
            }
            with open(self.data_dir / "daily_challenge.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Daily Challenge nicht speichern: {e}")

    def _load_state(self):
        try:
            path = self.data_dir / "daily_challenge.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.last_challenge_date = state.get('last_challenge_date')
                self.challenge_streak = state.get('challenge_streak', 0)
                self.total_challenges_completed = state.get('total_challenges_completed', 0)
        except Exception as e:
            logger.debug(f"Konnte Daily Challenge nicht laden: {e}")


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_quiz_engine: Optional[QuizEngine] = None

def get_quiz_engine() -> QuizEngine:
    """Gibt die globale QuizEngine-Instanz zurueck"""
    global _quiz_engine
    if _quiz_engine is None:
        _quiz_engine = QuizEngine()
    return _quiz_engine


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO KNOWLEDGE QUIZ SYSTEM v1.0")
    print("=" * 60)

    engine = QuizEngine()

    # Starte ein Test-Quiz
    print("\n--- QUIZ STARTEN ---")
    session = engine.start_quiz(QuizCategory.ANIME, QuizDifficulty.EASY, 3)
    print(f"Quiz gestartet: {session.category.value}, {len(session.questions)} Fragen")

    # Simuliere Antworten
    print("\n--- FRAGEN BEANTWORTEN ---")
    while not session.is_complete():
        question_data = engine.get_current_question()
        if question_data:
            question, options = question_data
            print(f"\nFrage: {question.question_text}")
            for key, val in options.items():
                print(f"  {key}) {val}")

            # Simuliere Antwort (immer A)
            result, reaction = engine.answer_question("A", time_taken=5)
            print(f"\nAntwort: A")
            print(f"Korrekt: {result.is_correct}")
            print(f"Punkte: {result.points_earned}")
            print(f"Holo: {reaction}")

    # Zusammenfassung
    print("\n--- QUIZ ZUSAMMENFASSUNG ---")
    summary = engine.get_quiz_summary()
    print(f"Richtig: {summary['correct']}/{summary['questions_total']}")
    print(f"Punkte: {summary['total_points']}")
    print(f"Genauigkeit: {summary['score_percentage']}%")

    # Gesamtstatistiken
    print("\n--- GESAMTSTATISTIKEN ---")
    stats = engine.get_overall_stats()
    print(f"Gesamtpunkte: {stats['total_points']}")
    print(f"Bester Streak: {stats['best_streak']}")
    print(f"Gesamtgenauigkeit: {stats['overall_accuracy']}%")

    print("\n" + "=" * 60)
    print("Quiz System bereit!")
