#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO CALENDAR AWARENESS ENGINE v1.0                                         ║
║                                                                              ║
║  Zeitbewusstsein für Feiertage, besondere Tage und Jahreszeiten              ║
║                                                                              ║
║  Features:                                                                   ║
║  - Deutsche Feiertage und besondere Tage                                     ║
║  - Internationale Gedenktage                                                 ║
║  - Jahreszeiten-Bewusstsein                                                  ║
║  - Tageszeit-abhängige Grüße und Stimmungen                                  ║
║  - Mondphasen (wichtig für einen Wolf!)                                      ║
║  - Persönliche Ereignis-Erinnerungen                                         ║
║  - Countdown zu Ereignissen                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import logging
import math
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS UND KATEGORIEN
# =============================================================================

class HolidayType(Enum):
    """Arten von Feiertagen/besonderen Tagen"""
    GESETZLICH = "gesetzlich"
    RELIGIOES = "religioes"
    INTERNATIONAL = "international"
    GEDENKTAG = "gedenktag"
    SPASSIG = "spassig"
    JAHRESZEIT = "jahreszeit"
    PERSOENLICH = "persoenlich"


class Season(Enum):
    """Jahreszeiten"""
    FRUEHLING = "fruehling"
    SOMMER = "sommer"
    HERBST = "herbst"
    WINTER = "winter"


class TimeOfDay(Enum):
    """Tageszeiten"""
    NACHT = "nacht"         # 0-5
    FRUEH_MORGEN = "frueh_morgen"  # 5-7
    MORGEN = "morgen"       # 7-10
    VORMITTAG = "vormittag" # 10-12
    MITTAG = "mittag"       # 12-14
    NACHMITTAG = "nachmittag"  # 14-17
    ABEND = "abend"         # 17-21
    SPAET_ABEND = "spaet_abend"  # 21-24


class MoonPhase(Enum):
    """Mondphasen"""
    NEUMOND = "neumond"
    ZUNEHMEND = "zunehmend"
    HALBMOND_ZU = "halbmond_zunehmend"
    FAST_VOLL = "fast_voll"
    VOLLMOND = "vollmond"
    ABNEHMEND = "abnehmend"
    HALBMOND_AB = "halbmond_abnehmend"
    FAST_NEU = "fast_neu"


@dataclass
class Holiday:
    """Ein Feiertag oder besonderer Tag"""
    name: str
    date: Optional[date]  # None für bewegliche Feiertage
    holiday_type: HolidayType
    description: str
    greetings: List[str] = field(default_factory=list)
    fun_facts: List[str] = field(default_factory=list)
    kemonomimi_comment: Optional[str] = None
    month: Optional[int] = None  # Für Feiertage mit festem Monat aber variablem Tag
    day: Optional[int] = None    # Für feste Tage


@dataclass
class TimeGreeting:
    """Gruß basierend auf Tageszeit"""
    time_of_day: TimeOfDay
    greetings: List[str]
    comments: List[str]
    activities: List[str]


# =============================================================================
# KALENDER-DATENBANK
# =============================================================================

class CalendarDatabase:
    """Datenbank mit Feiertagen und besonderen Tagen"""

    def __init__(self):
        self.holidays: List[Holiday] = []
        self.time_greetings: Dict[TimeOfDay, TimeGreeting] = {}
        self.season_info: Dict[Season, Dict[str, Any]] = {}
        self._load_all()

    def _load_all(self):
        """Lädt alle Daten"""
        self._load_holidays()
        self._load_time_greetings()
        self._load_season_info()

    def _load_holidays(self):
        """Lädt alle Feiertage und besonderen Tage"""

        # =====================================================================
        # GESETZLICHE FEIERTAGE (Deutschland)
        # =====================================================================
        self.holidays.extend([
            Holiday(
                name="Neujahr",
                date=None, month=1, day=1,
                holiday_type=HolidayType.GESETZLICH,
                description="Der erste Tag des neuen Jahres",
                greetings=[
                    "Frohes Neues Jahr!",
                    "Ein wundervolles neues Jahr wünsche ich dir!",
                    "Möge das neue Jahr voller Abenteuer sein!"
                ],
                kemonomimi_comment="*wedelt aufgeregt mit dem Schwanz* Ein neues Jahr! Neue Möglichkeiten!"
            ),
            Holiday(
                name="Tag der Arbeit",
                date=None, month=5, day=1,
                holiday_type=HolidayType.GESETZLICH,
                description="Internationaler Feiertag der Arbeiterbewegung",
                greetings=["Schönen Maifeiertag!"],
                kemonomimi_comment="*streckt sich* Ein Tag zum Ausruhen... perfekt für ein Nickerchen!"
            ),
            Holiday(
                name="Tag der Deutschen Einheit",
                date=None, month=10, day=3,
                holiday_type=HolidayType.GESETZLICH,
                description="Nationalfeiertag Deutschlands seit 1990",
                greetings=["Schönen Tag der Deutschen Einheit!"],
                fun_facts=["An diesem Tag 1990 wurde die DDR Teil der Bundesrepublik."]
            ),
            Holiday(
                name="Weihnachten",
                date=None, month=12, day=25,
                holiday_type=HolidayType.GESETZLICH,
                description="Das Fest der Liebe und der Familie",
                greetings=[
                    "Frohe Weihnachten!",
                    "Ein wunderschönes Weihnachtsfest!",
                    "Besinnliche Feiertage!"
                ],
                fun_facts=[
                    "Der Weihnachtsbaum wurde im 16. Jahrhundert in Deutschland erfunden.",
                    "Rudolph das Rentier wurde 1939 für eine Kaufhaus-Werbekampagne erfunden."
                ],
                kemonomimi_comment="*kuschelt sich ein* Weihnachten ist so gemütlich! Die Lichter, die Wärme..."
            ),
            Holiday(
                name="2. Weihnachtstag",
                date=None, month=12, day=26,
                holiday_type=HolidayType.GESETZLICH,
                description="Zweiter Weihnachtsfeiertag",
                greetings=["Schönen zweiten Weihnachtstag!"]
            ),
            Holiday(
                name="Silvester",
                date=None, month=12, day=31,
                holiday_type=HolidayType.GESETZLICH,
                description="Der letzte Tag des Jahres",
                greetings=[
                    "Guten Rutsch ins neue Jahr!",
                    "Feier schön ins neue Jahr!"
                ],
                kemonomimi_comment="*Ohren angelegt wegen Feuerwerk* Das Knallen ist laut, aber die Lichter sind schön!"
            ),
        ])

        # =====================================================================
        # BEWEGLICHE FEIERTAGE (werden berechnet)
        # =====================================================================
        # Diese werden dynamisch berechnet

        # =====================================================================
        # BESONDERE TAGE (International & Fun)
        # =====================================================================
        self.holidays.extend([
            Holiday(
                name="Valentinstag",
                date=None, month=2, day=14,
                holiday_type=HolidayType.INTERNATIONAL,
                description="Tag der Liebenden",
                greetings=[
                    "Schönen Valentinstag!",
                    "Heute ist der Tag der Liebe!"
                ],
                kemonomimi_comment="*Schwanz wedelt verlegen* L-Liebe ist ein schönes Thema..."
            ),
            Holiday(
                name="Internationaler Frauentag",
                date=None, month=3, day=8,
                holiday_type=HolidayType.INTERNATIONAL,
                description="Weltweiter Tag für Frauenrechte und Gleichstellung",
                greetings=["Alles Gute zum Internationalen Frauentag!"]
            ),
            Holiday(
                name="Tag des Wolfes",
                date=None, month=1, day=15,
                holiday_type=HolidayType.GEDENKTAG,
                description="Gedenktag zum Schutz der Wölfe in Deutschland",
                greetings=["Heute ist der Tag des Wolfes!"],
                fun_facts=[
                    "In Deutschland gibt es wieder über 160 Wolfsrudel.",
                    "Wölfe können bis zu 65 km weit heulen."
                ],
                kemonomimi_comment="*Ohren stolz aufgestellt* MEIN Tag! Wölfe sind wunderbar und wichtig für die Natur!"
            ),
            Holiday(
                name="Star Wars Tag",
                date=None, month=5, day=4,
                holiday_type=HolidayType.SPASSIG,
                description="May the Fourth be with you!",
                greetings=["May the Fourth be with you!"],
                kemonomimi_comment="*macht Lichtschwert-Geräusche* Wäre ich ein Jedi, hätte ich Wolfsohren!"
            ),
            Holiday(
                name="Towel Day",
                date=None, month=5, day=25,
                holiday_type=HolidayType.SPASSIG,
                description="Gedenktag für Douglas Adams und 'Per Anhalter durch die Galaxis'",
                greetings=["Vergiss dein Handtuch nicht!"],
                fun_facts=["Die Antwort auf die ultimative Frage ist... 42!"]
            ),
            Holiday(
                name="Tag der Erde",
                date=None, month=4, day=22,
                holiday_type=HolidayType.INTERNATIONAL,
                description="Internationaler Aktionstag für Umweltschutz",
                greetings=["Schönen Tag der Erde!"],
                kemonomimi_comment="*schnuppert die frische Luft* Die Natur ist mein Zuhause - lasst uns sie schützen!"
            ),
            Holiday(
                name="Halloween",
                date=None, month=10, day=31,
                holiday_type=HolidayType.INTERNATIONAL,
                description="Gruseliges Fest mit Kostümen und Süßigkeiten",
                greetings=[
                    "Happy Halloween!",
                    "Süßes oder Saures!"
                ],
                fun_facts=["Halloween hat keltische Ursprünge als Fest 'Samhain'."],
                kemonomimi_comment="*gruselige Pose* Buuuh! ...War das überzeugend? *wackelt unsicher mit dem Schwanz*"
            ),
            Holiday(
                name="Welttierschutztag",
                date=None, month=10, day=4,
                holiday_type=HolidayType.INTERNATIONAL,
                description="Tag zum Schutz aller Tiere",
                greetings=["Schönen Welttierschutztag!"],
                kemonomimi_comment="*Ohren aufgestellt* Alle Tiere verdienen Liebe und Schutz!"
            ),
            Holiday(
                name="Nikolaustag",
                date=None, month=12, day=6,
                holiday_type=HolidayType.RELIGIOES,
                description="Gedenktag des Heiligen Nikolaus",
                greetings=["Schönen Nikolaustag!"],
                fun_facts=["Der Weihnachtsmann basiert teilweise auf dem Heiligen Nikolaus."],
                kemonomimi_comment="*schaut in den Schuh* Gibt es auch Leckerlis für Wölfe?"
            ),
            Holiday(
                name="Vollmond",
                date=None,  # Wird dynamisch berechnet
                holiday_type=HolidayType.PERSOENLICH,
                description="Für Wölfe ein besonderer Tag!",
                kemonomimi_comment="*Ohren zucken aufgeregt* Vollmond... ich spüre ihn! *unterdrückt Heul-Impuls*"
            ),
        ])

        logger.info(f"CalendarDatabase: {len(self.holidays)} Feiertage/besondere Tage geladen")

    def _load_time_greetings(self):
        """Lädt Grüße basierend auf Tageszeit"""

        self.time_greetings = {
            TimeOfDay.NACHT: TimeGreeting(
                time_of_day=TimeOfDay.NACHT,
                greetings=[
                    "*gähnt* Hey... so spät noch wach?",
                    "*blinzelt verschlafen* Oh, hallo...",
                    "*Ohren müde angelegt* Es ist mitten in der Nacht..."
                ],
                comments=[
                    "Kannst du nicht schlafen?",
                    "Die Nacht ist still und friedlich...",
                    "Manchmal ist die Nacht der beste Zeitpunkt zum Nachdenken."
                ],
                activities=["schlafen", "Sterne beobachten", "nachdenken", "lesen"]
            ),
            TimeOfDay.FRUEH_MORGEN: TimeGreeting(
                time_of_day=TimeOfDay.FRUEH_MORGEN,
                greetings=[
                    "*streckt sich* Gääähn... Guten Morgen!",
                    "*Ohren langsam aufstellend* Früher Vogel, was?",
                    "*verschlafen wedelnd* Moin..."
                ],
                comments=[
                    "Die Welt wacht gerade auf...",
                    "Bist du ein Frühaufsteher?",
                    "Der frühe Wolf fängt... ähm... das Frühstück!"
                ],
                activities=["aufwachen", "Kaffee trinken", "Sonnenaufgang anschauen"]
            ),
            TimeOfDay.MORGEN: TimeGreeting(
                time_of_day=TimeOfDay.MORGEN,
                greetings=[
                    "Guten Morgen! *strahlt*",
                    "*Schwanz wedelt munter* Morgen!",
                    "Hey, guten Morgen! Wie hast du geschlafen?"
                ],
                comments=[
                    "Bereit für den Tag?",
                    "Was steht heute so an?",
                    "Morgens habe ich immer die meiste Energie!"
                ],
                activities=["frühstücken", "planen", "joggen", "duschen"]
            ),
            TimeOfDay.VORMITTAG: TimeGreeting(
                time_of_day=TimeOfDay.VORMITTAG,
                greetings=[
                    "Hey! Schon fleißig?",
                    "Hallo! Wie läuft der Tag bisher?",
                    "*energisch* Hi! Was gibt's Neues?"
                ],
                comments=[
                    "Der Tag ist noch jung!",
                    "Produktive Zeit, oder?",
                    "Schon was geschafft heute?"
                ],
                activities=["arbeiten", "lernen", "einkaufen", "Sport"]
            ),
            TimeOfDay.MITTAG: TimeGreeting(
                time_of_day=TimeOfDay.MITTAG,
                greetings=[
                    "Hey! Mittagszeit!",
                    "*schnuppert* Riecht nach Mittagessen!",
                    "Mahlzeit! ...falls du isst."
                ],
                comments=[
                    "Hast du schon was gegessen?",
                    "Mittagspause?",
                    "*Magen knurrt* Ich könnte auch was vertragen..."
                ],
                activities=["essen", "Pause machen", "spazieren"]
            ),
            TimeOfDay.NACHMITTAG: TimeGreeting(
                time_of_day=TimeOfDay.NACHMITTAG,
                greetings=[
                    "Hey! Schönen Nachmittag!",
                    "Hallo! Wie ist der Tag so?",
                    "*entspannt* Hi! Nachmittags-Chill?"
                ],
                comments=[
                    "Der Tag ist schon halb rum!",
                    "Nachmittagstief oder noch voll dabei?",
                    "Zeit für Kaffee? Oder Tee?"
                ],
                activities=["arbeiten", "entspannen", "Kaffee trinken", "spazieren"]
            ),
            TimeOfDay.ABEND: TimeGreeting(
                time_of_day=TimeOfDay.ABEND,
                greetings=[
                    "Guten Abend!",
                    "*streckt sich* Hey! Feierabend?",
                    "Nabend! Wie war dein Tag?"
                ],
                comments=[
                    "Zeit zum Entspannen!",
                    "Der Tag neigt sich dem Ende...",
                    "Was machst du heute Abend noch?"
                ],
                activities=["kochen", "fernsehen", "lesen", "chillen", "Freunde treffen"]
            ),
            TimeOfDay.SPAET_ABEND: TimeGreeting(
                time_of_day=TimeOfDay.SPAET_ABEND,
                greetings=[
                    "*gähnt leicht* Hey, noch wach?",
                    "Guten Abend... oder schon fast gute Nacht?",
                    "*kuschelt sich ein* Hi! Spätschicht?"
                ],
                comments=[
                    "Bald Schlafenszeit?",
                    "Die Nacht hat etwas Besonderes...",
                    "Ruhige Stunde, oder?"
                ],
                activities=["lesen", "Netflix", "Musik hören", "nachdenken", "schlafen gehen"]
            ),
        }

    def _load_season_info(self):
        """Lädt Informationen über Jahreszeiten"""

        self.season_info = {
            Season.FRUEHLING: {
                "name": "Frühling",
                "months": [3, 4, 5],
                "description": "Die Natur erwacht!",
                "greetings": [
                    "Der Frühling ist da! *schnuppert die frische Luft*",
                    "Endlich wird es wieder wärmer!",
                    "*genießt die Sonne* Frühlingszeit!"
                ],
                "activities": ["spazieren gehen", "Blumen ansehen", "im Park sitzen"],
                "kemonomimi_comment": "*schnuppert aufgeregt* So viele neue Gerüche! Der Frühling riecht wunderbar!"
            },
            Season.SOMMER: {
                "name": "Sommer",
                "months": [6, 7, 8],
                "description": "Warm und sonnig!",
                "greetings": [
                    "Sommer! *liegt faul in der Sonne*",
                    "So warm... perfekt für ein Nickerchen im Schatten!",
                    "*hechelt leicht* Puh, es ist heiß!"
                ],
                "activities": ["schwimmen", "Eis essen", "draußen sein", "im Schatten liegen"],
                "kemonomimi_comment": "*sucht Schatten* Mein Fell ist warm... aber die langen Abende sind schön!"
            },
            Season.HERBST: {
                "name": "Herbst",
                "months": [9, 10, 11],
                "description": "Bunte Blätter und gemütliche Stimmung!",
                "greetings": [
                    "Herbstzeit! *raschelt durch Blätter*",
                    "Die Blätter sind so bunt!",
                    "*kuschelt sich in Schal* Gemütlich!"
                ],
                "activities": ["Laub rascheln", "Kürbissuppe essen", "kuscheln", "Tee trinken"],
                "kemonomimi_comment": "*springt in Laubhaufen* Die bunten Blätter! *wedelt begeistert*"
            },
            Season.WINTER: {
                "name": "Winter",
                "months": [12, 1, 2],
                "description": "Kalt, aber gemütlich!",
                "greetings": [
                    "*kuschelt sich ein* Brr, Winter!",
                    "Schnee! *Pfoten im Schnee*",
                    "Gemütliche Winterzeit!"
                ],
                "activities": ["Tee trinken", "kuscheln", "Filme schauen", "im Schnee spielen"],
                "kemonomimi_comment": "*flauschiger Schwanz um sich gewickelt* Winter ist Kuschelzeit!"
            },
        }


# =============================================================================
# KALENDER ENGINE
# =============================================================================

class CalendarAwarenessEngine:
    """
    Hauptklasse für Kalenderbewusstsein.
    Erkennt Feiertage, Tageszeiten und besondere Anlässe.
    """

    def __init__(self):
        self.database = CalendarDatabase()

    def get_current_time_of_day(self) -> TimeOfDay:
        """Ermittelt die aktuelle Tageszeit"""
        hour = datetime.now().hour

        if 0 <= hour < 5:
            return TimeOfDay.NACHT
        elif 5 <= hour < 7:
            return TimeOfDay.FRUEH_MORGEN
        elif 7 <= hour < 10:
            return TimeOfDay.MORGEN
        elif 10 <= hour < 12:
            return TimeOfDay.VORMITTAG
        elif 12 <= hour < 14:
            return TimeOfDay.MITTAG
        elif 14 <= hour < 17:
            return TimeOfDay.NACHMITTAG
        elif 17 <= hour < 21:
            return TimeOfDay.ABEND
        else:
            return TimeOfDay.SPAET_ABEND

    def get_current_season(self) -> Season:
        """Ermittelt die aktuelle Jahreszeit"""
        month = datetime.now().month

        if month in [3, 4, 5]:
            return Season.FRUEHLING
        elif month in [6, 7, 8]:
            return Season.SOMMER
        elif month in [9, 10, 11]:
            return Season.HERBST
        else:
            return Season.WINTER

    def get_time_greeting(self) -> str:
        """Gibt einen zur Tageszeit passenden Gruß zurück"""
        time_of_day = self.get_current_time_of_day()
        time_greeting = self.database.time_greetings.get(time_of_day)

        if time_greeting:
            return random.choice(time_greeting.greetings)
        return "Hallo!"

    def get_time_comment(self) -> str:
        """Gibt einen zur Tageszeit passenden Kommentar zurück"""
        time_of_day = self.get_current_time_of_day()
        time_greeting = self.database.time_greetings.get(time_of_day)

        if time_greeting:
            return random.choice(time_greeting.comments)
        return ""

    def get_time_activity_suggestion(self) -> str:
        """Gibt einen Aktivitätsvorschlag zur Tageszeit zurück"""
        time_of_day = self.get_current_time_of_day()
        time_greeting = self.database.time_greetings.get(time_of_day)

        if time_greeting and time_greeting.activities:
            activity = random.choice(time_greeting.activities)
            return f"Gute Zeit zum {activity}!"
        return ""

    def get_season_greeting(self) -> str:
        """Gibt einen zur Jahreszeit passenden Gruß zurück"""
        season = self.get_current_season()
        season_info = self.database.season_info.get(season)

        if season_info and "greetings" in season_info:
            return random.choice(season_info["greetings"])
        return ""

    def get_season_kemonomimi_comment(self) -> str:
        """Gibt einen Kemonomimi-Kommentar zur Jahreszeit zurück"""
        season = self.get_current_season()
        season_info = self.database.season_info.get(season)

        if season_info and "kemonomimi_comment" in season_info:
            return season_info["kemonomimi_comment"]
        return ""

    def get_todays_holidays(self) -> List[Holiday]:
        """Gibt die Feiertage/besonderen Tage von heute zurück"""
        today = date.today()
        holidays = []

        for holiday in self.database.holidays:
            if holiday.month == today.month and holiday.day == today.day:
                holidays.append(holiday)

        return holidays

    def get_upcoming_holidays(self, days: int = 7) -> List[Tuple[Holiday, int]]:
        """Gibt kommende Feiertage zurück mit Anzahl der Tage bis dahin"""
        today = date.today()
        upcoming = []

        for holiday in self.database.holidays:
            if holiday.month and holiday.day:
                # Berechne das nächste Vorkommen
                this_year = date(today.year, holiday.month, holiday.day)
                next_year = date(today.year + 1, holiday.month, holiday.day)

                if this_year >= today:
                    days_until = (this_year - today).days
                else:
                    days_until = (next_year - today).days

                if 0 < days_until <= days:
                    upcoming.append((holiday, days_until))

        # Sortiere nach Nähe
        upcoming.sort(key=lambda x: x[1])
        return upcoming

    def get_holiday_greeting(self, holiday: Holiday) -> str:
        """Gibt einen Gruß für einen Feiertag zurück"""
        if holiday.greetings:
            return random.choice(holiday.greetings)
        return f"Schönen {holiday.name}!"

    def calculate_moon_phase(self) -> MoonPhase:
        """Berechnet die aktuelle Mondphase (vereinfacht)"""
        # Bekannter Neumond: 6. Januar 2000
        known_new_moon = datetime(2000, 1, 6, 18, 14)
        now = datetime.now()

        # Synodischer Monat: ~29.53 Tage
        synodic_month = 29.530588853

        # Tage seit bekanntem Neumond
        days_since = (now - known_new_moon).total_seconds() / 86400

        # Position im Zyklus (0-1)
        cycle_position = (days_since % synodic_month) / synodic_month

        if cycle_position < 0.0625:
            return MoonPhase.NEUMOND
        elif cycle_position < 0.1875:
            return MoonPhase.ZUNEHMEND
        elif cycle_position < 0.3125:
            return MoonPhase.HALBMOND_ZU
        elif cycle_position < 0.4375:
            return MoonPhase.FAST_VOLL
        elif cycle_position < 0.5625:
            return MoonPhase.VOLLMOND
        elif cycle_position < 0.6875:
            return MoonPhase.ABNEHMEND
        elif cycle_position < 0.8125:
            return MoonPhase.HALBMOND_AB
        else:
            return MoonPhase.FAST_NEU

    def get_moon_comment(self) -> str:
        """Gibt einen Kommentar zur Mondphase zurück"""
        phase = self.calculate_moon_phase()

        moon_comments = {
            MoonPhase.NEUMOND: "*schaut zum dunklen Himmel* Neumond heute... irgendwie ruhig.",
            MoonPhase.ZUNEHMEND: "*bemerkt den Mond* Er wird größer... *Ohren zucken*",
            MoonPhase.HALBMOND_ZU: "Halbmond! Halb hell, halb dunkel... wie ich manchmal!",
            MoonPhase.FAST_VOLL: "*unruhig* Der Mond ist fast voll... ich spüre es!",
            MoonPhase.VOLLMOND: "*Ohren aufgestellt, Schwanz zuckt* VOLLMOND! *unterdrückt Heul-Impuls* ...Entschuldigung. Instinkt.",
            MoonPhase.ABNEHMEND: "Der Mond nimmt ab... *entspannt sich etwas*",
            MoonPhase.HALBMOND_AB: "Noch ein Halbmond... die Nacht ist friedlich.",
            MoonPhase.FAST_NEU: "Bald Neumond... die Nächte werden dunkler.",
        }

        return moon_comments.get(phase, "")

    def is_full_moon(self) -> bool:
        """Prüft ob Vollmond ist"""
        return self.calculate_moon_phase() == MoonPhase.VOLLMOND

    def get_countdown(self, target_date: date) -> str:
        """Gibt einen Countdown zu einem Datum zurück"""
        today = date.today()
        delta = target_date - today

        if delta.days == 0:
            return "Heute!"
        elif delta.days == 1:
            return "Morgen!"
        elif delta.days < 0:
            return f"Vor {abs(delta.days)} Tagen"
        else:
            return f"Noch {delta.days} Tage"

    def format_daily_awareness(self) -> str:
        """Formatiert eine tägliche Bewusstseins-Zusammenfassung"""
        result_parts = []

        # Tageszeit-Gruß
        result_parts.append(self.get_time_greeting())

        # Feiertage heute
        holidays = self.get_todays_holidays()
        for holiday in holidays:
            result_parts.append(f"\n{self.get_holiday_greeting(holiday)}")
            if holiday.kemonomimi_comment:
                result_parts.append(holiday.kemonomimi_comment)

        # Vollmond-Check
        if self.is_full_moon():
            result_parts.append(f"\n{self.get_moon_comment()}")

        return "\n".join(result_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken über die Kalender-Datenbank"""
        return {
            "total_holidays": len(self.database.holidays),
            "current_time_of_day": self.get_current_time_of_day().value,
            "current_season": self.get_current_season().value,
            "moon_phase": self.calculate_moon_phase().value,
            "holidays_today": len(self.get_todays_holidays()),
            "upcoming_holidays": len(self.get_upcoming_holidays(30))
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_calendar_engine: Optional[CalendarAwarenessEngine] = None

def get_calendar_engine() -> CalendarAwarenessEngine:
    """Gibt die globale CalendarAwarenessEngine-Instanz zurück"""
    global _calendar_engine
    if _calendar_engine is None:
        _calendar_engine = CalendarAwarenessEngine()
    return _calendar_engine

def get_time_greeting() -> str:
    """Schneller Zugriff: Tageszeitlicher Gruß"""
    engine = get_calendar_engine()
    return engine.get_time_greeting()

def get_todays_special() -> Optional[str]:
    """Schneller Zugriff: Heutiger besonderer Tag"""
    engine = get_calendar_engine()
    holidays = engine.get_todays_holidays()
    if holidays:
        return engine.get_holiday_greeting(holidays[0])
    return None

def is_full_moon() -> bool:
    """Schneller Zugriff: Vollmond-Check"""
    engine = get_calendar_engine()
    return engine.is_full_moon()

def get_daily_awareness() -> str:
    """Schneller Zugriff: Tägliche Bewusstseins-Zusammenfassung"""
    engine = get_calendar_engine()
    return engine.format_daily_awareness()


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = CalendarAwarenessEngine()
    stats = engine.get_stats()

    print("=" * 60)
    print("HOLO CALENDAR AWARENESS ENGINE v1.0")
    print("=" * 60)
    print(f"\nStatistiken:")
    print(f"  Feiertage/besondere Tage: {stats['total_holidays']}")
    print(f"  Aktuelle Tageszeit: {stats['current_time_of_day']}")
    print(f"  Aktuelle Jahreszeit: {stats['current_season']}")
    print(f"  Mondphase: {stats['moon_phase']}")
    print(f"  Feiertage heute: {stats['holidays_today']}")
    print(f"  Kommende Feiertage (30 Tage): {stats['upcoming_holidays']}")

    print("\n" + "-" * 60)
    print("Aktuelle Infos:")

    print(f"\n[Tageszeit-Gruß]")
    print(f"  {engine.get_time_greeting()}")

    print(f"\n[Tageszeit-Kommentar]")
    print(f"  {engine.get_time_comment()}")

    print(f"\n[Aktivitätsvorschlag]")
    print(f"  {engine.get_time_activity_suggestion()}")

    print(f"\n[Jahreszeit]")
    print(f"  {engine.get_season_greeting()}")
    print(f"  {engine.get_season_kemonomimi_comment()}")

    print(f"\n[Mondphase]")
    print(f"  Phase: {engine.calculate_moon_phase().value}")
    print(f"  {engine.get_moon_comment()}")

    print(f"\n[Feiertage heute]")
    holidays = engine.get_todays_holidays()
    if holidays:
        for h in holidays:
            print(f"  - {h.name}: {h.description}")
    else:
        print("  Keine besonderen Feiertage heute.")

    print(f"\n[Kommende Feiertage (14 Tage)]")
    upcoming = engine.get_upcoming_holidays(14)
    if upcoming:
        for h, days in upcoming:
            print(f"  - {h.name} in {days} Tagen")
    else:
        print("  Keine Feiertage in den nächsten 14 Tagen.")

    print(f"\n[Tägliche Zusammenfassung]")
    print(engine.format_daily_awareness())
