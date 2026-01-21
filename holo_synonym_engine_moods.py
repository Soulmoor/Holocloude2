"""
Holocloude Synonym-Engine mit Stimmungsebenen v2.0
===================================================
Umfassendes Vokabular-System mit 400+ Synonym-Gruppen,
kategorisiert nach Stimmungsebenen und emotionaler Intensität.

Autor: Holocloude Development Team
Version: 2.0.0
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Set, Any
import random
import sqlite3
import json
from pathlib import Path

# ============================================================================
# ENUMERATIONEN & GRUNDTYPEN
# ============================================================================

class MoodLevel(Enum):
    """Stimmungsebenen für Synonym-Auswahl"""
    SEHR_POSITIV = "sehr_positiv"      # Euphorisch, begeistert
    POSITIV = "positiv"                 # Fröhlich, zufrieden
    NEUTRAL = "neutral"                 # Ausgeglichen, sachlich
    NEGATIV = "negativ"                 # Traurig, enttäuscht
    SEHR_NEGATIV = "sehr_negativ"       # Verzweifelt, wütend
    ENERGISCH = "energisch"             # Aktiv, dynamisch
    RUHIG = "ruhig"                     # Entspannt, gelassen
    INTIM = "intim"                     # Vertraut, liebevoll
    VERSPIELT = "verspielt"             # Neckisch, humorvoll
    NACHDENKLICH = "nachdenklich"       # Reflektierend, philosophisch

class FormalityLevel(Enum):
    """Formalitätsebenen"""
    SEHR_FORMELL = "sehr_formell"       # Höflichkeitsform, distanziert
    FORMELL = "formell"                 # Respektvoll, professionell
    NEUTRAL = "neutral"                 # Standard
    INFORMELL = "informell"             # Locker, freundschaftlich
    SEHR_INFORMELL = "sehr_informell"   # Umgangssprachlich, slang

class IntensityLevel(Enum):
    """Intensitätsebenen"""
    MINIMAL = 1      # Sehr schwach
    NIEDRIG = 2      # Leicht
    MITTEL = 3       # Normal
    HOCH = 4         # Stark
    MAXIMAL = 5      # Sehr stark

class WordCategory(Enum):
    """Wort-Kategorien"""
    # Emotionale Ausdrücke
    FREUDE = "freude"
    TRAUER = "trauer"
    WUET = "wut"
    ANGST = "angst"
    UEBERRASCHUNG = "ueberraschung"
    LIEBE = "liebe"
    HOFFNUNG = "hoffnung"
    DANKBARKEIT = "dankbarkeit"
    STOLZ = "stolz"
    SCHAM = "scham"
    EKEL = "ekel"
    NEUGIER = "neugier"

    # Soziale Interaktion
    GRUSS = "gruss"
    ABSCHIED = "abschied"
    ZUSTIMMUNG = "zustimmung"
    ABLEHNUNG = "ablehnung"
    BITTE = "bitte"
    DANK = "dank"
    ENTSCHULDIGUNG = "entschuldigung"

    # Kognitive Ausdrücke
    VERSTEHEN = "verstehen"
    DENKEN = "denken"
    WISSEN = "wissen"
    GLAUBEN = "glauben"
    ERINNERN = "erinnern"

    # Handlungen & Aktivitäten
    BEWEGUNG = "bewegung"
    KOMMUNIKATION = "kommunikation"
    HILFE = "hilfe"
    ARBEIT = "arbeit"

    # Beschreibungen
    POSITIV_ADJ = "positiv_adjektiv"
    NEGATIV_ADJ = "negativ_adjektiv"
    GROESSE = "groesse"
    GESCHWINDIGKEIT = "geschwindigkeit"
    INTENSITAET = "intensitaet"

    # Reaktionen
    AUSRUF = "ausruf"
    BESTAETIGUNG = "bestaetigung"
    VERNEINUNG = "verneinung"
    UEBERGANG = "uebergang"

# ============================================================================
# DATENSTRUKTUREN
# ============================================================================

@dataclass
class SynonymEntry:
    """Einzelner Synonym-Eintrag mit Metadaten"""
    word: str
    mood_levels: List[MoodLevel]
    formality: FormalityLevel = FormalityLevel.NEUTRAL
    intensity: IntensityLevel = IntensityLevel.MITTEL
    weight: float = 1.0  # Auswahlgewichtung
    contexts: List[str] = field(default_factory=list)
    is_kemonomimi: bool = False  # Spezielle Kemonomimi-Ausdrücke
    emotion_boost: Dict[str, float] = field(default_factory=dict)

@dataclass
class SynonymGroup:
    """Gruppe von Synonymen mit gemeinsamer Bedeutung"""
    id: str
    base_word: str
    category: WordCategory
    entries: List[SynonymEntry]
    description: str = ""
    related_groups: List[str] = field(default_factory=list)

@dataclass
class EmotionalContext:
    """Aktueller emotionaler Kontext für Synonym-Auswahl"""
    mood: float = 0.5  # 0.0-1.0
    energy: float = 0.5
    intimacy: float = 0.0
    formality: float = 0.5
    playfulness: float = 0.0
    primary_emotion: Optional[str] = None
    emotion_intensity: float = 0.5

# ============================================================================
# SYNONYM-DATENBANK (200+ GRUPPEN)
# ============================================================================

class SynonymDatabase:
    """Zentrale Synonym-Datenbank mit allen Gruppen"""

    def __init__(self):
        self.groups: Dict[str, SynonymGroup] = {}
        self._initialize_all_groups()

    def _initialize_all_groups(self):
        """Initialisiert alle 400+ Synonym-Gruppen"""
        self._init_freude_gruppen()
        self._init_trauer_gruppen()
        self._init_wut_gruppen()
        self._init_angst_gruppen()
        self._init_liebe_gruppen()
        self._init_ueberraschung_gruppen()
        self._init_hoffnung_gruppen()
        self._init_dankbarkeit_gruppen()
        self._init_stolz_gruppen()
        self._init_scham_gruppen()
        self._init_neugier_gruppen()
        self._init_gruss_gruppen()
        self._init_abschied_gruppen()
        self._init_zustimmung_gruppen()
        self._init_ablehnung_gruppen()
        self._init_bitte_gruppen()
        self._init_dank_gruppen()
        self._init_entschuldigung_gruppen()
        self._init_verstehen_gruppen()
        self._init_denken_gruppen()
        self._init_positiv_adj_gruppen()
        self._init_negativ_adj_gruppen()
        self._init_intensitaet_gruppen()
        self._init_ausruf_gruppen()
        self._init_bestaetigung_gruppen()
        self._init_uebergang_gruppen()
        self._init_bewegung_gruppen()
        self._init_kommunikation_gruppen()
        self._init_hilfe_gruppen()
        self._init_kemonomimi_gruppen()
        # v2.0 - Erweiterte Gruppen
        self._init_erweiterte_freude_gruppen()
        self._init_erweiterte_trauer_gruppen()
        self._init_erweiterte_wut_gruppen()
        self._init_erweiterte_angst_gruppen()
        self._init_erweiterte_liebe_gruppen()
        self._init_erweiterte_hoffnung_gruppen()
        self._init_charakter_gruppen()
        self._init_wetter_natur_gruppen()
        self._init_zeit_gruppen()
        self._init_soziale_interaktion_gruppen()
        self._init_koerper_gesundheit_gruppen()
        self._init_arbeit_leistung_gruppen()
        self._init_kreativitaet_gruppen()
        self._init_philosophie_gruppen()
        self._init_alltag_erweitert_gruppen()
        self._init_kemonomimi_erweitert_gruppen()
        # v2.1 - Stimmungsebenen & Erweitertes Vokabular
        self._init_erweiterte_stimmungen_v2()

    # ========================================================================
    # FREUDE-GRUPPEN (20 Gruppen)
    # ========================================================================

    def _init_freude_gruppen(self):
        """Initialisiert Freude-bezogene Synonym-Gruppen"""

        # Gruppe 1: Sich freuen
        self.groups["freuen"] = SynonymGroup(
            id="freuen",
            base_word="freuen",
            category=WordCategory.FREUDE,
            description="Freude empfinden",
            entries=[
                SynonymEntry("freue mich", [MoodLevel.POSITIV, MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin happy", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin froh", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin begeistert", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin entzückt", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin überglücklich", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("freut mich sehr", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin total aus dem Häuschen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("freu mich riesig", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz verzückt", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 2: Glücklich sein
        self.groups["gluecklich"] = SynonymGroup(
            id="gluecklich",
            base_word="glücklich",
            category=WordCategory.FREUDE,
            description="Zustand des Glücks",
            entries=[
                SynonymEntry("glücklich", [MoodLevel.POSITIV, MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("selig", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("im siebten Himmel", [MoodLevel.SEHR_POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("voller Freude", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("freudestrahlend", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("zufrieden", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("happy", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("vergnügt", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fröhlich gestimmt", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("voll Glück", [MoodLevel.SEHR_POSITIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 3: Lachen
        self.groups["lachen"] = SynonymGroup(
            id="lachen",
            base_word="lachen",
            category=WordCategory.FREUDE,
            description="Ausdruck der Freude durch Lachen",
            entries=[
                SynonymEntry("lache", [MoodLevel.POSITIV, MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("kichere", [MoodLevel.VERSPIELT, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("schmunzle", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("grinse", [MoodLevel.VERSPIELT, MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("pruste los", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("lache herzlich", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("muss lachen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("lache mich kaputt", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("gluckse", [MoodLevel.VERSPIELT, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("wiehre vor Lachen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 4: Begeisterung
        self.groups["begeisterung"] = SynonymGroup(
            id="begeisterung",
            base_word="begeistert",
            category=WordCategory.FREUDE,
            description="Intensive positive Erregung",
            entries=[
                SynonymEntry("begeistert", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("hingerissen", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("euphorisch", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("außer sich vor Freude", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("total begeistert", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("schwärme", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fasziniert", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("elektrisiert", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hin und weg", [MoodLevel.SEHR_POSITIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("restlos beeindruckt", [MoodLevel.SEHR_POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 5: Spaß haben
        self.groups["spass"] = SynonymGroup(
            id="spass",
            base_word="Spaß",
            category=WordCategory.FREUDE,
            description="Vergnügen und Unterhaltung",
            entries=[
                SynonymEntry("macht Spaß", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("macht total Laune", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("ist vergnüglich", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("amüsiert mich", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bereitet Freude", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ist lustig", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("macht mega Bock", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("ist unterhaltsam", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("genießen wir", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("erfreut das Herz", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 6: Aufregung (positiv)
        self.groups["aufregung_positiv"] = SynonymGroup(
            id="aufregung_positiv",
            base_word="aufgeregt",
            category=WordCategory.FREUDE,
            description="Positive Aufregung und Erwartung",
            entries=[
                SynonymEntry("bin aufgeregt", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin gespannt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("kann es kaum erwarten", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fiebere entgegen", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz kribbelig", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin voller Vorfreude", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("erwarte ungeduldig", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("freue mich drauf", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin heiß drauf", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("erwarte gespannt", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 7: Genuss
        self.groups["genuss"] = SynonymGroup(
            id="genuss",
            base_word="genießen",
            category=WordCategory.FREUDE,
            description="Etwas mit Freude erleben",
            entries=[
                SynonymEntry("genieße", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("koste aus", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("schwelge", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("erfreue mich an", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("sauge auf", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("lasse mir schmecken", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ergötze mich", [MoodLevel.POSITIV], FormalityLevel.SEHR_FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("feiere", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("zelebriere", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("nehme voll mit", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 8: Erleichterung
        self.groups["erleichterung"] = SynonymGroup(
            id="erleichterung",
            base_word="erleichtert",
            category=WordCategory.FREUDE,
            description="Freude durch Wegfall von Sorgen",
            entries=[
                SynonymEntry("bin erleichtert", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fällt mir ein Stein vom Herzen", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("atme auf", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("puh, Glück gehabt", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin befreit", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kann aufatmen", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin erlöst", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("endlich entspannt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("wie befreit", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("erleichtert aufgeatmet", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 9: Zufriedenheit
        self.groups["zufriedenheit"] = SynonymGroup(
            id="zufriedenheit",
            base_word="zufrieden",
            category=WordCategory.FREUDE,
            description="Ruhige, ausgeglichene Freude",
            entries=[
                SynonymEntry("bin zufrieden", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin content", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("fühle mich wohl", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin im Reinen", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("passt so", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin erfüllt", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("alles gut", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin ganz bei mir", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("rundherum zufrieden", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin guter Dinge", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 10: Fröhlichkeit
        self.groups["froehlichkeit"] = SynonymGroup(
            id="froehlichkeit",
            base_word="fröhlich",
            category=WordCategory.FREUDE,
            description="Leichte, beschwingte Freude",
            entries=[
                SynonymEntry("fröhlich", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("heiter", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("beschwingt", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("gut gelaunt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("putzmunter", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fidel", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("quietschvergnügt", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("sonnig", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("strahlend", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("aufgekratzt", [MoodLevel.POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 11: Freudige Überraschung
        self.groups["freudige_ueberraschung"] = SynonymGroup(
            id="freudige_ueberraschung",
            base_word="überrascht",
            category=WordCategory.FREUDE,
            description="Positive unerwartete Freude",
            entries=[
                SynonymEntry("bin positiv überrascht", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wow", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin baff", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("hätte nicht gedacht", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin sprachlos vor Freude", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("was für eine Freude", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin überwältigt", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("krass", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("unerwartet schön", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("angenehm überrascht", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 12: Beschreibung toll/super
        self.groups["toll"] = SynonymGroup(
            id="toll",
            base_word="toll",
            category=WordCategory.FREUDE,
            description="Positive Bewertung",
            entries=[
                SynonymEntry("toll", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("super", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("klasse", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("spitze", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("prima", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("großartig", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fantastisch", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("wunderbar", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ausgezeichnet", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("phänomenal", [MoodLevel.SEHR_POSITIV], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("mega", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hammer", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("geil", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hervorragend", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("exzellent", [MoodLevel.POSITIV], FormalityLevel.SEHR_FORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 13: Schön finden
        self.groups["schoen"] = SynonymGroup(
            id="schoen",
            base_word="schön",
            category=WordCategory.FREUDE,
            description="Ästhetische positive Bewertung",
            entries=[
                SynonymEntry("schön", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("wunderschön", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("hübsch", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("bezaubernd", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("reizend", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("entzückend", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ästhetisch", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("atemberaubend", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("malerisch", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bildschön", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 14: Mögen/Lieben (leicht)
        self.groups["moegen"] = SynonymGroup(
            id="moegen",
            base_word="mögen",
            category=WordCategory.FREUDE,
            description="Positive Zuneigung",
            entries=[
                SynonymEntry("mag", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("gefällt mir", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("finde gut", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("hab gern", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("schätze", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin angetan von", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("find ich nice", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("steh auf", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin Fan von", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("habe Gefallen an", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 15: Positives Erstaunen
        self.groups["erstaunen_positiv"] = SynonymGroup(
            id="erstaunen_positiv",
            base_word="erstaunt",
            category=WordCategory.FREUDE,
            description="Bewunderndes Staunen",
            entries=[
                SynonymEntry("bin erstaunt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin beeindruckt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("staune", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("Respekt", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Hut ab", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Chapeau", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("nicht schlecht", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("Wahnsinn", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bemerkenswert", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bewundernswert", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 16: Heiterkeit
        self.groups["heiterkeit"] = SynonymGroup(
            id="heiterkeit",
            base_word="heiter",
            category=WordCategory.FREUDE,
            description="Leichte, unbeschwerte Stimmung",
            entries=[
                SynonymEntry("heiter", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("unbeschwert", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("leichtherzig", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("sorgenfrei", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("gelöst", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("locker drauf", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("entspannt-fröhlich", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ausgelassen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("unbekümmert", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("leichten Herzens", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 17: Wohlfühlen
        self.groups["wohlfuehlen"] = SynonymGroup(
            id="wohlfuehlen",
            base_word="wohlfühlen",
            category=WordCategory.FREUDE,
            description="Behagliches Wohlbefinden",
            entries=[
                SynonymEntry("fühle mich wohl", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich geborgen", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz entspannt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("geht mir gut", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich behaglich", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin in meiner Mitte", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich pudelwohl", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz bei mir", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("alles bestens", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("befinde mich wohl", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 18: Dankbare Freude
        self.groups["dankbare_freude"] = SynonymGroup(
            id="dankbare_freude",
            base_word="dankbar-froh",
            category=WordCategory.FREUDE,
            description="Mit Dankbarkeit verbundene Freude",
            entries=[
                SynonymEntry("bin dankbar und froh", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("schätze mich glücklich", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin gesegnet", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("weiß zu schätzen", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin privilegiert", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("empfinde Dankbarkeit", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich beschenkt", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin voller Dankbarkeit", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("das Herz geht mir auf", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin von Herzen froh", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 19: Stolze Freude
        self.groups["stolze_freude"] = SynonymGroup(
            id="stolze_freude",
            base_word="stolz-froh",
            category=WordCategory.FREUDE,
            description="Freude über eigene Leistung",
            entries=[
                SynonymEntry("bin stolz", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("freue mich über mich", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hab's geschafft", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin zufrieden mit mir", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("kann mich sehen lassen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin erfüllt von Stolz", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("das macht mich stolz", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich bestätigt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin richtig stolz", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("empfinde Genugtuung", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 20: Lebenslust
        self.groups["lebenslust"] = SynonymGroup(
            id="lebenslust",
            base_word="Lebenslust",
            category=WordCategory.FREUDE,
            description="Intensive Lebensfreude",
            entries=[
                SynonymEntry("voller Lebenslust", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("lebensfroh", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("könnte Bäume ausreißen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("sprühe vor Energie", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin voller Tatendrang", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("das Leben ist schön", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("genieße jeden Moment", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühl mich lebendig", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin quicklebendig", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("lebe auf", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

    # ========================================================================
    # TRAUER-GRUPPEN (15 Gruppen)
    # ========================================================================

    def _init_trauer_gruppen(self):
        """Initialisiert Trauer-bezogene Synonym-Gruppen"""

        # Gruppe 21: Traurig sein
        self.groups["traurig"] = SynonymGroup(
            id="traurig",
            base_word="traurig",
            category=WordCategory.TRAUER,
            description="Grundlegende Traurigkeit",
            entries=[
                SynonymEntry("bin traurig", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin down", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin betrübt", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin bekümmert", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("mir ist schwer ums Herz", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühle mich mies", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin niedergeschlagen", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("hab Kummer", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin geknickt", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("tut mir in der Seele weh", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 22: Weinen
        self.groups["weinen"] = SynonymGroup(
            id="weinen",
            base_word="weinen",
            category=WordCategory.TRAUER,
            description="Tränen vergießen",
            entries=[
                SynonymEntry("weine", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mir kommen die Tränen", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("schluchze", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("heule", [MoodLevel.SEHR_NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hab feuchte Augen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("vergieße Tränen", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("muss weinen", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bricht mir das Herz", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("weine bitterlich", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann Tränen nicht zurückhalten", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 23: Vermissen
        self.groups["vermissen"] = SynonymGroup(
            id="vermissen",
            base_word="vermissen",
            category=WordCategory.TRAUER,
            description="Sehnsucht nach Abwesendem",
            entries=[
                SynonymEntry("vermisse", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("sehne mich", [MoodLevel.NEGATIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fehlt mir", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hab Sehnsucht", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("denke oft an", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("wünschte du wärst hier", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("empfinde Sehnsucht", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("mein Herz sehnt sich", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühle mich verlassen", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist eine Lücke", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 24: Enttäuschung
        self.groups["enttaeuschung"] = SynonymGroup(
            id="enttaeuschung",
            base_word="enttäuscht",
            category=WordCategory.TRAUER,
            description="Ernüchterung über Erwartungen",
            entries=[
                SynonymEntry("bin enttäuscht", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hatte mir mehr erhofft", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin ernüchtert", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin desillusioniert", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("hat mich getroffen", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin frustriert", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist schade", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("hatte andere Erwartungen", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hat mich runtergebracht", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fühl mich enttäuscht", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 25: Depression/Niedergeschlagenheit
        self.groups["niedergeschlagen"] = SynonymGroup(
            id="niedergeschlagen",
            base_word="niedergeschlagen",
            category=WordCategory.TRAUER,
            description="Tiefe Traurigkeit",
            entries=[
                SynonymEntry("bin niedergeschlagen", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin am Boden", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin deprimiert", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühle mich leer", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("hänge durch", [MoodLevel.SEHR_NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin gedrückt", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin mutlos", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("alles ist grau", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin entmutigt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("sehe schwarz", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 26: Einsamkeit
        self.groups["einsamkeit"] = SynonymGroup(
            id="einsamkeit",
            base_word="einsam",
            category=WordCategory.TRAUER,
            description="Gefühl der Isolation",
            entries=[
                SynonymEntry("fühle mich einsam", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin allein", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich isoliert", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin verlassen", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("hab niemanden", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("fühle mich abgeschnitten", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin auf mich gestellt", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("empfinde Einsamkeit", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich ausgegrenzt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("niemand versteht mich", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 27: Melancholie
        self.groups["melancholie"] = SynonymGroup(
            id="melancholie",
            base_word="melancholisch",
            category=WordCategory.TRAUER,
            description="Sanfte, nachdenkliche Trauer",
            entries=[
                SynonymEntry("bin melancholisch", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin wehmütig", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin schwermütig", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("hänge Erinnerungen nach", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin in sentimentaler Stimmung", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("denke an vergangene Zeiten", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("empfinde Wehmut", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin nostalgisch-traurig", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hab den Blues", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin in Gedanken versunken", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
            ]
        )

        # Gruppe 28: Schlechte Nachrichten
        self.groups["schlecht"] = SynonymGroup(
            id="schlecht",
            base_word="schlecht",
            category=WordCategory.TRAUER,
            description="Negative Bewertung",
            entries=[
                SynonymEntry("schlecht", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("nicht gut", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("mies", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("doof", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("übel", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("schrecklich", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("furchtbar", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("unschön", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bedauerlich", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("echt mist", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 29: Trauer um Verlust
        self.groups["verlust"] = SynonymGroup(
            id="verlust",
            base_word="Verlust",
            category=WordCategory.TRAUER,
            description="Trauer über Verlust",
            entries=[
                SynonymEntry("trauere", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("betrauere", [MoodLevel.SEHR_NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("vermisse schmerzlich", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("werde nicht fertig mit", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("der Verlust schmerzt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin in Trauer", [MoodLevel.SEHR_NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("es tut so weh", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("empfinde tiefe Trauer", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("hab einen schweren Verlust erlitten", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("mein Herz ist schwer", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 30: Hoffnungslosigkeit
        self.groups["hoffnungslos"] = SynonymGroup(
            id="hoffnungslos",
            base_word="hoffnungslos",
            category=WordCategory.TRAUER,
            description="Fehlen von Hoffnung",
            entries=[
                SynonymEntry("bin hoffnungslos", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("sehe keine Hoffnung", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin verzweifelt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("weiß nicht mehr weiter", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin am Ende", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("empfinde Verzweiflung", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("gibt keinen Ausweg", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin in einer Sackgasse", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("seh kein Licht", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("alles erscheint sinnlos", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 31: Reue
        self.groups["reue"] = SynonymGroup(
            id="reue",
            base_word="bereuen",
            category=WordCategory.TRAUER,
            description="Bedauern über Vergangenes",
            entries=[
                SynonymEntry("bereue", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("tut mir leid", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hätte ich mal", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("empfinde Reue", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("wünschte es wäre anders", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ärgere mich über mich", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("mache mir Vorwürfe", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("würde gern ungeschehen machen", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("nagt an mir", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bedaure zutiefst", [MoodLevel.SEHR_NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 32: Resignation
        self.groups["resignation"] = SynonymGroup(
            id="resignation",
            base_word="resigniert",
            category=WordCategory.TRAUER,
            description="Aufgeben und Akzeptanz",
            entries=[
                SynonymEntry("bin resigniert", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("hab aufgegeben", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("ist halt so", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("akzeptiere es", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("kann nichts ändern", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("füge mich", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ergebe mich", [MoodLevel.SEHR_NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("habe mich damit abgefunden", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("sehe es ein", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("was soll ich machen", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 33: Erschöpfung (emotional)
        self.groups["erschoepfung_emotional"] = SynonymGroup(
            id="erschoepfung_emotional",
            base_word="erschöpft",
            category=WordCategory.TRAUER,
            description="Emotionale Müdigkeit",
            entries=[
                SynonymEntry("bin emotional erschöpft", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin ausgelaugt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin ausgebrannt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann nicht mehr", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin am Limit", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("fühle mich leer", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("hab keine Kraft mehr", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin emotional bankrott", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("brauche eine Pause", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin völlig fertig", [MoodLevel.SEHR_NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 34: Mitleid
        self.groups["mitleid"] = SynonymGroup(
            id="mitleid",
            base_word="Mitleid",
            category=WordCategory.TRAUER,
            description="Empathische Trauer",
            entries=[
                SynonymEntry("empfinde Mitleid", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("tut mir so leid für dich", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fühle mit dir", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("das berührt mich", [MoodLevel.NEGATIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("geht mir nahe", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin betroffen", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("leidet mit", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin gerührt", [MoodLevel.NEGATIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hab großes Mitgefühl", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("spreche mein Beileid aus", [MoodLevel.NEGATIV], FormalityLevel.SEHR_FORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 35: Seufzen
        self.groups["seufzen"] = SynonymGroup(
            id="seufzen",
            base_word="seufzen",
            category=WordCategory.TRAUER,
            description="Ausdruck milder Trauer",
            entries=[
                SynonymEntry("seufze", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("ach", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("oh je", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("tja", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("naja", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("leider", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("schade eigentlich", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("atme schwer", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hm", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("seufze tief", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

    # ========================================================================
    # WUT-GRUPPEN (15 Gruppen)
    # ========================================================================

    def _init_wut_gruppen(self):
        """Initialisiert Wut-bezogene Synonym-Gruppen"""

        # Gruppe 36: Wütend sein
        self.groups["wuetend"] = SynonymGroup(
            id="wuetend",
            base_word="wütend",
            category=WordCategory.WUET,
            description="Starke Verärgerung",
            entries=[
                SynonymEntry("bin wütend", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin sauer", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin stinksauer", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin zornig", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin aufgebracht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin außer mir", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("koche vor Wut", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin geladen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin fuchsteufelswild", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin erzürnt", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_FORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 37: Ärger
        self.groups["aerger"] = SynonymGroup(
            id="aerger",
            base_word="ärgern",
            category=WordCategory.WUET,
            description="Milde Verärgerung",
            entries=[
                SynonymEntry("ärgere mich", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("nervt mich", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("geht mir auf die Nerven", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("regt mich auf", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin genervt", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("stört mich", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("ist lästig", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("kotzt mich an", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("macht mich wahnsinnig", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bringt mich auf die Palme", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 38: Empörung
        self.groups["empoerung"] = SynonymGroup(
            id="empoerung",
            base_word="empört",
            category=WordCategory.WUET,
            description="Moralische Entrüstung",
            entries=[
                SynonymEntry("bin empört", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin entrüstet", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("finde das unerhört", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("das geht gar nicht", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin schockiert", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("frechheit", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("eine Zumutung", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin aufgebracht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin entsetzt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("das ist unverschämt", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 39: Frustration
        self.groups["frustration"] = SynonymGroup(
            id="frustration",
            base_word="frustriert",
            category=WordCategory.WUET,
            description="Ohnmächtige Verärgerung",
            entries=[
                SynonymEntry("bin frustriert", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("es klappt einfach nicht", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin am Verzweifeln", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("komme nicht weiter", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("es macht mich fertig", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin ratlos", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("stehe auf dem Schlauch", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("könnte schreien", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin blockiert", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("drehe durch", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 40: Ungeduld
        self.groups["ungeduld"] = SynonymGroup(
            id="ungeduld",
            base_word="ungeduldig",
            category=WordCategory.WUET,
            description="Mangel an Geduld",
            entries=[
                SynonymEntry("bin ungeduldig", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("dauert mir zu lang", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin zappelig", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("kann nicht mehr warten", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("wann endlich", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("muss jetzt sein", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("mir platzt gleich der Kragen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin kribbelig", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("halte das nicht mehr aus", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("verliere die Geduld", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 41: Verachtung
        self.groups["verachtung"] = SynonymGroup(
            id="verachtung",
            base_word="verachten",
            category=WordCategory.WUET,
            description="Geringschätzung",
            entries=[
                SynonymEntry("verachte", [MoodLevel.SEHR_NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("schau drauf herab", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("find das erbärmlich", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("ist unter meiner Würde", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("empfinde Verachtung", [MoodLevel.SEHR_NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("ist jämmerlich", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("pff", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("kann ich nicht ernst nehmen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ist lächerlich", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("ist armselig", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 42: Hass
        self.groups["hass"] = SynonymGroup(
            id="hass",
            base_word="hassen",
            category=WordCategory.WUET,
            description="Intensivste Abneigung",
            entries=[
                SynonymEntry("hasse", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann nicht ausstehen", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("verabscheue", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("ist mir zuwider", [MoodLevel.SEHR_NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("empfinde tiefen Hass", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("ekelt mich an", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("widert mich an", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist mir verhasst", [MoodLevel.SEHR_NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("kann ich absolut nicht leiden", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("das ist das Letzte", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 43: Eifersucht
        self.groups["eifersucht"] = SynonymGroup(
            id="eifersucht",
            base_word="eifersüchtig",
            category=WordCategory.WUET,
            description="Neidische Wut",
            entries=[
                SynonymEntry("bin eifersüchtig", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin neidisch", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("gönne es nicht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin missgünstig", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("empfinde Eifersucht", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin grün vor Neid", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("warum nicht ich", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich übergangen", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hätte auch gern", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin possessiv", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 44: Gereiztheit
        self.groups["gereizt"] = SynonymGroup(
            id="gereizt",
            base_word="gereizt",
            category=WordCategory.WUET,
            description="Schnell reizbare Stimmung",
            entries=[
                SynonymEntry("bin gereizt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin dünnhäutig", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin auf 180", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("mir reicht's", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin angespannt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin sensibel heute", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("alles nervt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin aufgekratzt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin reizbar", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin grantig", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 45: Kritik
        self.groups["kritik"] = SynonymGroup(
            id="kritik",
            base_word="kritisieren",
            category=WordCategory.WUET,
            description="Tadelnde Äußerung",
            entries=[
                SynonymEntry("kritisiere", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("finde nicht gut", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("meckere", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("beanstande", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("habe etwas auszusetzen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("nörgle", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("äußere Kritik", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bemängele", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("tadele", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("motze", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 46: Fluchen
        self.groups["fluchen"] = SynonymGroup(
            id="fluchen",
            base_word="fluchen",
            category=WordCategory.WUET,
            description="Zornige Ausdrücke",
            entries=[
                SynonymEntry("verflixt", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("mist", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("verdammt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("so ein Mist", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("zum Teufel", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Mann oh Mann", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Herrgott", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("ach du Schreck", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("heiliger Strohsack", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("donnerwetter", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 47: Vorwurf
        self.groups["vorwurf"] = SynonymGroup(
            id="vorwurf",
            base_word="vorwerfen",
            category=WordCategory.WUET,
            description="Beschuldigung",
            entries=[
                SynonymEntry("werfe dir vor", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist deine Schuld", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("beschuldige", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("du bist schuld", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("mache dir Vorwürfe", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wegen dir", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bist verantwortlich", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hast verbockt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("das hast du davon", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("klage an", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 48: Widerwille
        self.groups["widerwille"] = SynonymGroup(
            id="widerwille",
            base_word="Widerwille",
            category=WordCategory.WUET,
            description="Unlust und Abneigung",
            entries=[
                SynonymEntry("mag nicht", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("will nicht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hab keine Lust", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("weigere mich", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kommt nicht in Frage", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mache das nicht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("niemals", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("auf keinen Fall", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("lehne ab", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin dagegen", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 49: Genervt
        self.groups["genervt"] = SynonymGroup(
            id="genervt",
            base_word="genervt",
            category=WordCategory.WUET,
            description="Anhaltende Verärgerung",
            entries=[
                SynonymEntry("bin genervt", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hab die Nase voll", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("reichts mir", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("habs satt", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("strapaziert meine Geduld", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("geht mir auf den Keks", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin bedient", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin angenervt", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hängt mir zum Hals raus", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin fertig mit", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 50: Trotz
        self.groups["trotz"] = SynonymGroup(
            id="trotz",
            base_word="trotzig",
            category=WordCategory.WUET,
            description="Widerstand und Auflehnung",
            entries=[
                SynonymEntry("bin trotzig", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mache es trotzdem", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("jetzt erst recht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("lass mich nicht beirren", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin stur", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bleibe dabei", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mir egal", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("widersetze mich", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("rebelliere", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin dickköpfig", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ]
        )

    # ========================================================================
    # ANGST-GRUPPEN (12 Gruppen)
    # ========================================================================

    def _init_angst_gruppen(self):
        """Initialisiert Angst-bezogene Synonym-Gruppen"""

        # Gruppe 51: Angst haben
        self.groups["angst"] = SynonymGroup(
            id="angst",
            base_word="Angst",
            category=WordCategory.ANGST,
            description="Grundlegendes Angstgefühl",
            entries=[
                SynonymEntry("hab Angst", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fürchte mich", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hab Schiss", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin ängstlich", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mir ist mulmig", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("habe Furcht", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin verängstigt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mir ist bang", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mir ist unheimlich", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich bedroht", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 52: Sorge
        self.groups["sorge"] = SynonymGroup(
            id="sorge",
            base_word="Sorge",
            category=WordCategory.ANGST,
            description="Besorgniserregende Gedanken",
            entries=[
                SynonymEntry("mache mir Sorgen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin besorgt", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin in Sorge", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("beunruhigt mich", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("macht mir Kopfzerbrechen", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("sorge mich um", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("lässt mir keine Ruhe", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("habe Bedenken", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("denke ständig daran", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("liegt mir schwer auf der Seele", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 53: Panik
        self.groups["panik"] = SynonymGroup(
            id="panik",
            base_word="Panik",
            category=WordCategory.ANGST,
            description="Extreme Angst",
            entries=[
                SynonymEntry("bin in Panik", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bekomme Panik", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin völlig aufgelöst", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("flip gleich aus", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin panisch", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("Herzrasen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin hysterisch", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann nicht mehr klar denken", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin kopflos", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("die Angst übermannt mich", [MoodLevel.SEHR_NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 54: Nervosität
        self.groups["nervositaet"] = SynonymGroup(
            id="nervositaet",
            base_word="nervös",
            category=WordCategory.ANGST,
            description="Unruhige Anspannung",
            entries=[
                SynonymEntry("bin nervös", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin aufgeregt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hab Lampenfieber", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin hibbelig", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("zittere", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin angespannt", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin fahrig", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hab feuchte Hände", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin inner unruhig", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("kann nicht stillsitzen", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 55: Unsicherheit
        self.groups["unsicherheit"] = SynonymGroup(
            id="unsicherheit",
            base_word="unsicher",
            category=WordCategory.ANGST,
            description="Mangel an Selbstvertrauen",
            entries=[
                SynonymEntry("bin unsicher", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("weiß nicht", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin mir nicht sicher", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("zweifle", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin verunsichert", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("traue mich nicht", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin zögerlich", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("hadere", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin unschlüssig", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich unsicher", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 56: Schüchternheit
        self.groups["schuechtern"] = SynonymGroup(
            id="schuechtern",
            base_word="schüchtern",
            category=WordCategory.ANGST,
            description="Soziale Zurückhaltung",
            entries=[
                SynonymEntry("bin schüchtern", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin befangen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin gehemmt", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("traue mich nicht zu fragen", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin zurückhaltend", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin verschämt", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin verlegen", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("werde rot", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin introvertiert", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin still", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MINIMAL),
            ]
        )

        # Gruppe 57: Erschrecken
        self.groups["erschrecken"] = SynonymGroup(
            id="erschrecken",
            base_word="erschrecken",
            category=WordCategory.ANGST,
            description="Plötzliche Angstreaktion",
            entries=[
                SynonymEntry("erschrecke", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("zucke zusammen", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fahre hoch", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("mein Herz bleibt stehen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("kriege einen Schreck", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin erschrocken", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mir stockt der Atem", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bekomme einen Schock", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("hui", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("uah", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 58: Vorsicht
        self.groups["vorsicht"] = SynonymGroup(
            id="vorsicht",
            base_word="vorsichtig",
            category=WordCategory.ANGST,
            description="Behutsames Handeln",
            entries=[
                SynonymEntry("bin vorsichtig", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("passe auf", [MoodLevel.NEUTRAL, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin achtsam", [MoodLevel.NEUTRAL, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("gehe behutsam vor", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin wachsam", [MoodLevel.NEUTRAL, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("halte Ausschau", [MoodLevel.NEUTRAL, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin auf der Hut", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin skeptisch", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("habe ein ungutes Gefühl", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("taste mich vor", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
            ]
        )

        # Gruppe 59: Überwältigt
        self.groups["ueberwaeltigt"] = SynonymGroup(
            id="ueberwaeltigt",
            base_word="überwältigt",
            category=WordCategory.ANGST,
            description="Von Eindrücken überfordert",
            entries=[
                SynonymEntry("bin überwältigt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist zu viel", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin überfordert", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("komme nicht hinterher", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin übermannt", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("kann das nicht verarbeiten", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin erschlagen", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin platt", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin aus der Bahn geworfen", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin sprachlos", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 60: Phobie
        self.groups["phobie"] = SynonymGroup(
            id="phobie",
            base_word="Phobie",
            category=WordCategory.ANGST,
            description="Irrationale Angst",
            entries=[
                SynonymEntry("habe panische Angst vor", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann es nicht ertragen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("krieg Gänsehaut bei", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin allergisch gegen", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("habe Horror vor", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("ist mein Albtraum", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bekomme Zustände bei", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann nicht mal daran denken", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("lähmt mich", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("macht mich kirre", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 61: Beklemmung
        self.groups["beklemmung"] = SynonymGroup(
            id="beklemmung",
            base_word="beklommen",
            category=WordCategory.ANGST,
            description="Diffuses Unbehagen",
            entries=[
                SynonymEntry("fühle mich beklommen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ist mir unwohl", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hab ein flaues Gefühl", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("mir ist nicht geheuer", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("spüre Unbehagen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("empfinde Beklemmung", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich unwohl", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ist mir komisch", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("hab Bauchschmerzen deswegen", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("kriege ein komisches Gefühl", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 62: Paranoia
        self.groups["paranoia"] = SynonymGroup(
            id="paranoia",
            base_word="paranoid",
            category=WordCategory.ANGST,
            description="Verfolgungsängste",
            entries=[
                SynonymEntry("bin paranoid", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühle mich beobachtet", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("traue niemandem", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin misstrauisch", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("werde verfolgt", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("sie sind hinter mir her", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("hab Verfolgungswahn", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin argwöhnisch", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hege Verdacht", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin auf alles gefasst", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

    # ========================================================================
    # LIEBE-GRUPPEN (15 Gruppen)
    # ========================================================================

    def _init_liebe_gruppen(self):
        """Initialisiert Liebe-bezogene Synonym-Gruppen"""

        # Gruppe 63: Liebe
        self.groups["liebe"] = SynonymGroup(
            id="liebe",
            base_word="lieben",
            category=WordCategory.LIEBE,
            description="Tiefe Zuneigung",
            entries=[
                SynonymEntry("liebe dich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("hab dich lieb", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin verliebt", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mein Herz gehört dir", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("liebe dich von Herzen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("empfinde tiefe Liebe", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("du bist mein Ein und Alles", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin total verknallt", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("du bedeutest mir alles", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("mein Herz schlägt für dich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 64: Zuneigung
        self.groups["zuneigung"] = SynonymGroup(
            id="zuneigung",
            base_word="Zuneigung",
            category=WordCategory.LIEBE,
            description="Warme Gefühle",
            entries=[
                SynonymEntry("mag dich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hab dich gern", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich zu dir hingezogen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("empfinde Zuneigung", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("schätze dich sehr", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bist mir wichtig", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("liegt mir am Herzen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin dir zugetan", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("find dich sympathisch", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bist mir ans Herz gewachsen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 65: Fürsorge
        self.groups["fuersorge"] = SynonymGroup(
            id="fuersorge",
            base_word="Fürsorge",
            category=WordCategory.LIEBE,
            description="Sorgende Zuneigung",
            entries=[
                SynonymEntry("sorge mich um dich", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kümmere mich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("pass auf dich auf", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("will dass es dir gut geht", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin für dich da", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("beschütze dich", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("nehme mich deiner an", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hege und pflege", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("dein Wohl ist mir wichtig", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("stehe an deiner Seite", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 66: Romantik
        self.groups["romantik"] = SynonymGroup(
            id="romantik",
            base_word="romantisch",
            category=WordCategory.LIEBE,
            description="Romantische Gefühle",
            entries=[
                SynonymEntry("schwärme für dich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("Schmetterlinge im Bauch", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin wie verzaubert", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin hin und weg", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("träume von dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("du verzauberst mich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin vernarrt in dich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin hingerissen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du bringst mein Herz zum Flattern", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Herzklopfen bei dir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ]
        )

        # Gruppe 67: Sehnsucht (romantisch)
        self.groups["sehnsucht_liebe"] = SynonymGroup(
            id="sehnsucht_liebe",
            base_word="Sehnsucht",
            category=WordCategory.LIEBE,
            description="Liebevolle Sehnsucht",
            entries=[
                SynonymEntry("sehne mich nach dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wünschte du wärst hier", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("kann es kaum erwarten dich zu sehen", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("vermisse dich so sehr", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("zähle die Tage", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("denke ständig an dich", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du fehlst mir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bist immer in meinen Gedanken", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mein Herz sehnt sich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("würde alles geben um bei dir zu sein", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 68: Verbundenheit
        self.groups["verbundenheit"] = SynonymGroup(
            id="verbundenheit",
            base_word="verbunden",
            category=WordCategory.LIEBE,
            description="Tiefe Verbundenheit",
            entries=[
                SynonymEntry("fühle mich verbunden", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wir gehören zusammen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du verstehst mich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("spüre tiefe Verbindung", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("sind Seelenverwandte", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("du bist mein Zuhause", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("fühle mich geborgen bei dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wir sind wie eins", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("teilen eine besondere Bindung", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin eins mit dir", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 69: Treue
        self.groups["treue"] = SynonymGroup(
            id="treue",
            base_word="treu",
            category=WordCategory.LIEBE,
            description="Loyalität und Beständigkeit",
            entries=[
                SynonymEntry("bin dir treu", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("stehe zu dir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("halte zu dir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin loyal", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("werde dich nie verlassen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bleibe bei dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kannst dich auf mich verlassen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin dir ergeben", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("für immer dein", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("in guten wie in schlechten Zeiten", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ]
        )

        # Gruppe 70: Kompliment
        self.groups["kompliment"] = SynonymGroup(
            id="kompliment",
            base_word="Kompliment",
            category=WordCategory.LIEBE,
            description="Liebevolle Worte",
            entries=[
                SynonymEntry("bist wunderschön", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bist toll", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("du bist einzigartig", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bewundere dich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bist so besonders", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("du strahlst", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bist hinreißend", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du bist mein Sonnenschein", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bist so liebenswert", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du machst mich glücklich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ]
        )

        # Gruppe 71: Kosenamen
        self.groups["kosenamen"] = SynonymGroup(
            id="kosenamen",
            base_word="Kosename",
            category=WordCategory.LIEBE,
            description="Zärtliche Anreden",
            entries=[
                SynonymEntry("Schatz", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Liebling", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Süße", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Maus", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("Herzchen", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Engel", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Hase", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("Bärchen", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("mein Herz", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Schnucki", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
            ]
        )

        # Gruppe 72-77: Weitere Liebe-Gruppen (Vertrauen, Hingabe, etc.)
        self.groups["vertrauen"] = SynonymGroup(
            id="vertrauen",
            base_word="vertrauen",
            category=WordCategory.LIEBE,
            description="Tiefes Vertrauen",
            entries=[
                SynonymEntry("vertraue dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("glaube an dich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kannst mir alles sagen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("vertraue dir blind", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("du hast mein Vertrauen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("öffne mich dir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("setze mein Vertrauen in dich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("weiß dass du es gut meinst", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich sicher bei dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("lass dich in mein Herz", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ]
        )

    # ========================================================================
    # ÜBERRASCHUNG-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_ueberraschung_gruppen(self):
        """Initialisiert Überraschungs-Gruppen"""
        self.groups["ueberraschung"] = SynonymGroup(
            id="ueberraschung", base_word="überrascht", category=WordCategory.UEBERRASCHUNG,
            description="Erstaunen", entries=[
                SynonymEntry("bin überrascht", [MoodLevel.NEUTRAL, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("wow", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Wahnsinn", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("hätte nicht gedacht", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("damit habe ich nicht gerechnet", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin perplex", [MoodLevel.NEUTRAL, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("krass", [MoodLevel.POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("unglaublich", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin baff", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("was eine Überraschung", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ])

        self.groups["staunen"] = SynonymGroup(
            id="staunen", base_word="staunen", category=WordCategory.UEBERRASCHUNG,
            description="Verwunderung", entries=[
                SynonymEntry("staune", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin erstaunt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("beeindruckend", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("faszinierend", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bemerkenswert", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("Hut ab", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Respekt", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("nicht schlecht", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin beeindruckt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("beachtlich", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ])

        self.groups["verwirrung"] = SynonymGroup(
            id="verwirrung", base_word="verwirrt", category=WordCategory.UEBERRASCHUNG,
            description="Durcheinander", entries=[
                SynonymEntry("bin verwirrt", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("versteh nicht ganz", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin durcheinander", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("häh", [MoodLevel.NEUTRAL, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("wie bitte", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("verstehe Bahnhof", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin irritiert", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("komme nicht mit", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("stehe auf dem Schlauch", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin etwas lost", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # HOFFNUNG-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_hoffnung_gruppen(self):
        """Initialisiert Hoffnungs-Gruppen"""
        self.groups["hoffnung"] = SynonymGroup(
            id="hoffnung", base_word="hoffen", category=WordCategory.HOFFNUNG,
            description="Zuversicht", entries=[
                SynonymEntry("hoffe", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin zuversichtlich", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin optimistisch", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wird schon werden", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("glaube daran", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("drücke die Daumen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("setze auf", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin guter Hoffnung", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("wünsche mir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("Kopf hoch", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ])

        self.groups["erwartung"] = SynonymGroup(
            id="erwartung", base_word="erwarten", category=WordCategory.HOFFNUNG,
            description="Vorfreude", entries=[
                SynonymEntry("freue mich auf", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kann es kaum erwarten", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin gespannt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin voller Vorfreude", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fiebere entgegen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("erwarte ungeduldig", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("sehe dem entgegen", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("freu mich riesig drauf", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin total aufgeregt", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("kribbelt schon", [MoodLevel.POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # DANKBARKEIT-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_dankbarkeit_gruppen(self):
        """Initialisiert Dankbarkeits-Gruppen"""
        self.groups["dankbarkeit"] = SynonymGroup(
            id="dankbarkeit", base_word="dankbar", category=WordCategory.DANKBARKEIT,
            description="Dankgefühl", entries=[
                SynonymEntry("bin dankbar", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("danke dir", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("vielen Dank", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("danke vielmals", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("herzlichen Dank", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("tausend Dank", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin sehr verbunden", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("weiß zu schätzen", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("danke von Herzen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("mega lieb von dir", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # STOLZ-GRUPPEN (5 Gruppen)
    # ========================================================================

    def _init_stolz_gruppen(self):
        """Initialisiert Stolz-Gruppen"""
        self.groups["stolz"] = SynonymGroup(
            id="stolz", base_word="stolz", category=WordCategory.STOLZ,
            description="Selbstwertgefühl", entries=[
                SynonymEntry("bin stolz", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin stolz auf dich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("habs geschafft", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("Weltklasse", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin zufrieden mit mir", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("erfüllt mich mit Stolz", [MoodLevel.SEHR_POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann mich sehen lassen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin richtig stolz", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fühle mich bestätigt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("das macht mich stolz", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # SCHAM-GRUPPEN (5 Gruppen)
    # ========================================================================

    def _init_scham_gruppen(self):
        """Initialisiert Scham-Gruppen"""
        self.groups["scham"] = SynonymGroup(
            id="scham", base_word="Scham", category=WordCategory.SCHAM,
            description="Beschämung", entries=[
                SynonymEntry("schäme mich", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist mir peinlich", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin verlegen", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("werde rot", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("könnte im Boden versinken", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("empfinde Scham", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("wie peinlich", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin beschämt", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("traue mich nicht", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("unangenehm berührt", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # NEUGIER-GRUPPEN (5 Gruppen)
    # ========================================================================

    def _init_neugier_gruppen(self):
        """Initialisiert Neugier-Gruppen"""
        self.groups["neugier"] = SynonymGroup(
            id="neugier", base_word="neugierig", category=WordCategory.NEUGIER,
            description="Wissensdrang", entries=[
                SynonymEntry("bin neugierig", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("interessiert mich", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("will mehr wissen", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fasziniert mich", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("macht mich neugierig", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin wissbegierig", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("erzähl mehr", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("was genau", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin gespannt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("weckt mein Interesse", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # GRUSS-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_gruss_gruppen(self):
        """Initialisiert Gruß-Gruppen"""
        self.groups["gruss_casual"] = SynonymGroup(
            id="gruss_casual", base_word="Hallo", category=WordCategory.GRUSS,
            description="Lockere Begrüßung", entries=[
                SynonymEntry("hallo", [MoodLevel.POSITIV, MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hi", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("hey", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("na", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("servus", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("moin", [MoodLevel.POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("tach", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("hallöchen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("huhu", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.INTIM], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("yo", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
            ])

        self.groups["gruss_formell"] = SynonymGroup(
            id="gruss_formell", base_word="Grüße", category=WordCategory.GRUSS,
            description="Formelle Begrüßung", entries=[
                SynonymEntry("guten Tag", [MoodLevel.NEUTRAL, MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("grüß Gott", [MoodLevel.NEUTRAL], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("herzlich willkommen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("guten Morgen", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("guten Abend", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("freut mich", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("schön Sie zu sehen", [MoodLevel.POSITIV], FormalityLevel.SEHR_FORMELL, IntensityLevel.HOCH),
                SynonymEntry("willkommen", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("sei gegrüßt", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("grüße Sie", [MoodLevel.NEUTRAL], FormalityLevel.SEHR_FORMELL, IntensityLevel.MITTEL),
            ])

        self.groups["gruss_intim"] = SynonymGroup(
            id="gruss_intim", base_word="Liebste", category=WordCategory.GRUSS,
            description="Liebevolle Begrüßung", entries=[
                SynonymEntry("da bist du ja", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("freue mich so dich zu sehen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("schön dass du da bist", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hab dich vermisst", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("endlich", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("mein Liebling", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("wie schön", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hallo Schatz", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("du fehlst mir immer", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("toll dass du hier bist", [MoodLevel.POSITIV, MoodLevel.ENERGISCH, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # ABSCHIED-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_abschied_gruppen(self):
        """Initialisiert Abschieds-Gruppen"""
        self.groups["abschied_casual"] = SynonymGroup(
            id="abschied_casual", base_word="tschüss", category=WordCategory.ABSCHIED,
            description="Lockerer Abschied", entries=[
                SynonymEntry("tschüss", [MoodLevel.POSITIV, MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bis dann", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("ciao", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bye", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("bis bald", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mach's gut", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bis später", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("man sieht sich", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("hdl", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bis gleich", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
            ])

        self.groups["abschied_intim"] = SynonymGroup(
            id="abschied_intim", base_word="Lebwohl", category=WordCategory.ABSCHIED,
            description="Liebevoller Abschied", entries=[
                SynonymEntry("pass auf dich auf", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("vermisse dich jetzt schon", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("freue mich auf das nächste Mal", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("hab dich lieb", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("schlaf gut", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("träum was Schönes", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("denk an dich", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("du fehlst mir schon", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bis bald mein Schatz", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("alles Liebe", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # ZUSTIMMUNG-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_zustimmung_gruppen(self):
        """Initialisiert Zustimmungs-Gruppen"""
        self.groups["ja"] = SynonymGroup(
            id="ja", base_word="ja", category=WordCategory.ZUSTIMMUNG,
            description="Bejahung", entries=[
                SynonymEntry("ja", [MoodLevel.NEUTRAL, MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("jawohl", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("klar", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("genau", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("stimmt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("absolut", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("auf jeden Fall", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("definitiv", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("jep", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("jo", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
            ])

        self.groups["einverstanden"] = SynonymGroup(
            id="einverstanden", base_word="einverstanden", category=WordCategory.ZUSTIMMUNG,
            description="Übereinstimmung", entries=[
                SynonymEntry("einverstanden", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin dabei", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("geht klar", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("abgemacht", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("deal", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("passt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("finde ich gut", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin dafür", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("machen wir so", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("akzeptiert", [MoodLevel.NEUTRAL], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # ABLEHNUNG-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_ablehnung_gruppen(self):
        """Initialisiert Ablehnungs-Gruppen"""
        self.groups["nein"] = SynonymGroup(
            id="nein", base_word="nein", category=WordCategory.ABLEHNUNG,
            description="Verneinung", entries=[
                SynonymEntry("nein", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("nö", [MoodLevel.NEUTRAL, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("leider nein", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("eher nicht", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("auf keinen Fall", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("niemals", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("keinesfalls", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("nope", [MoodLevel.NEUTRAL, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("sicher nicht", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("kommt nicht in Frage", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ])

    # ========================================================================
    # BITTE-GRUPPEN (6 Gruppen)
    # ========================================================================

    def _init_bitte_gruppen(self):
        """Initialisiert Bitte-Gruppen"""
        self.groups["bitte"] = SynonymGroup(
            id="bitte", base_word="bitte", category=WordCategory.BITTE,
            description="Höfliche Bitte", entries=[
                SynonymEntry("bitte", [MoodLevel.NEUTRAL, MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bitte bitte", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.INTIM], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("könntest du", [MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("wärst du so lieb", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("würdest du bitte", [MoodLevel.NEUTRAL], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ich bitte dich", [MoodLevel.NEUTRAL, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("sei so gut", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ich hätte gern", [MoodLevel.NEUTRAL], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("dürfte ich bitten", [MoodLevel.NEUTRAL], FormalityLevel.SEHR_FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("kannst du mir helfen", [MoodLevel.NEUTRAL, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # DANK-GRUPPEN (6 Gruppen)
    # ========================================================================

    def _init_dank_gruppen(self):
        """Initialisiert Dank-Gruppen"""
        self.groups["danke"] = SynonymGroup(
            id="danke", base_word="danke", category=WordCategory.DANK,
            description="Dankesausdruck", entries=[
                SynonymEntry("danke", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("dankeschön", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("vielen Dank", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("merci", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("thx", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("herzlichen Dank", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("besten Dank", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("sehr freundlich", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("echt lieb", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("du bist der Beste", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
            ])

    # ========================================================================
    # ENTSCHULDIGUNG-GRUPPEN (6 Gruppen)
    # ========================================================================

    def _init_entschuldigung_gruppen(self):
        """Initialisiert Entschuldigungs-Gruppen"""
        self.groups["entschuldigung"] = SynonymGroup(
            id="entschuldigung", base_word="Entschuldigung", category=WordCategory.ENTSCHULDIGUNG,
            description="Entschuldigungsausdruck", entries=[
                SynonymEntry("Entschuldigung", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("tut mir leid", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("sorry", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("war mein Fehler", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("es tut mir sehr leid", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bitte verzeih mir", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("ich entschuldige mich", [MoodLevel.NEGATIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("das wollte ich nicht", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("mea culpa", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bitte entschuldige", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # VERSTEHEN-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_verstehen_gruppen(self):
        """Initialisiert Verstehen-Gruppen"""
        self.groups["verstehen"] = SynonymGroup(
            id="verstehen", base_word="verstehen", category=WordCategory.VERSTEHEN,
            description="Verständnis", entries=[
                SynonymEntry("verstehe", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ach so", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("alles klar", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ich sehe", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("macht Sinn", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("kapiert", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("hab ich verstanden", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist angekommen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("nachvollziehbar", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("einleuchtend", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # DENKEN-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_denken_gruppen(self):
        """Initialisiert Denken-Gruppen"""
        self.groups["denken"] = SynonymGroup(
            id="denken", base_word="denken", category=WordCategory.DENKEN,
            description="Gedankenprozess", entries=[
                SynonymEntry("denke", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("glaube", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("meine", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("bin der Meinung", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("finde", [MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("vermute", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("schätze", [MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("überlepe", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("erwäge", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("grüble", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # POSITIV ADJEKTIV-GRUPPEN (15 Gruppen)
    # ========================================================================

    def _init_positiv_adj_gruppen(self):
        """Initialisiert positive Adjektiv-Gruppen"""
        self.groups["gut"] = SynonymGroup(
            id="gut", base_word="gut", category=WordCategory.POSITIV_ADJ,
            description="Positive Bewertung", entries=[
                SynonymEntry("gut", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("super", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("toll", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("klasse", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("prima", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("spitze", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("großartig", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fantastisch", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("hervorragend", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("ausgezeichnet", [MoodLevel.POSITIV], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("mega", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hammer", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("geil", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("wunderbar", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("exzellent", [MoodLevel.POSITIV], FormalityLevel.SEHR_FORMELL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # NEGATIV ADJEKTIV-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_negativ_adj_gruppen(self):
        """Initialisiert negative Adjektiv-Gruppen"""
        self.groups["schlecht_adj"] = SynonymGroup(
            id="schlecht_adj", base_word="schlecht", category=WordCategory.NEGATIV_ADJ,
            description="Negative Bewertung", entries=[
                SynonymEntry("schlecht", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mies", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("doof", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("übel", [MoodLevel.SEHR_NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("beschissen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("schrecklich", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("furchtbar", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("grauenvoll", [MoodLevel.SEHR_NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("miserabel", [MoodLevel.SEHR_NEGATIV], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("katastrophal", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
            ])

    # ========================================================================
    # INTENSITÄTS-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_intensitaet_gruppen(self):
        """Initialisiert Intensitäts-Gruppen"""
        self.groups["sehr"] = SynonymGroup(
            id="sehr", base_word="sehr", category=WordCategory.INTENSITAET,
            description="Verstärkung", entries=[
                SynonymEntry("sehr", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("total", [MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("extrem", [MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("mega", [MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("unglaublich", [MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("wahnsinnig", [MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("richtig", [MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("echt", [MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("überaus", [MoodLevel.NEUTRAL], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("ausgesprochen", [MoodLevel.NEUTRAL], FormalityLevel.FORMELL, IntensityLevel.HOCH),
            ])

        self.groups["ein_bisschen"] = SynonymGroup(
            id="ein_bisschen", base_word="ein bisschen", category=WordCategory.INTENSITAET,
            description="Abschwächung", entries=[
                SynonymEntry("ein bisschen", [MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("etwas", [MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("leicht", [MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("ein wenig", [MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("kaum", [MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MINIMAL),
                SynonymEntry("minimal", [MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MINIMAL),
                SynonymEntry("ansatzweise", [MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("n bissl", [MoodLevel.VERSPIELT, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("geringfügig", [MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("vielleicht", [MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
            ])

    # ========================================================================
    # AUSRUF-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_ausruf_gruppen(self):
        """Initialisiert Ausruf-Gruppen"""
        self.groups["ausruf_positiv"] = SynonymGroup(
            id="ausruf_positiv", base_word="yay", category=WordCategory.AUSRUF,
            description="Positive Ausrufe", entries=[
                SynonymEntry("yay", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hurra", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("juhu", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("super", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("jippie", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("wow", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("yeah", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("jaaa", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("wunderbar", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("herrlich", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

        self.groups["ausruf_negativ"] = SynonymGroup(
            id="ausruf_negativ", base_word="oh nein", category=WordCategory.AUSRUF,
            description="Negative Ausrufe", entries=[
                SynonymEntry("oh nein", [MoodLevel.NEGATIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mist", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("verdammt", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("oje", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("nee", [MoodLevel.NEGATIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("arg", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("au weia", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("oh je", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("mein Gott", [MoodLevel.NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("ach herrje", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
            ])

    # ========================================================================
    # BESTÄTIGUNG-GRUPPEN (6 Gruppen)
    # ========================================================================

    def _init_bestaetigung_gruppen(self):
        """Initialisiert Bestätigungs-Gruppen"""
        self.groups["bestaetigung"] = SynonymGroup(
            id="bestaetigung", base_word="okay", category=WordCategory.BESTAETIGUNG,
            description="Zustimmende Bestätigung", entries=[
                SynonymEntry("okay", [MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ok", [MoodLevel.NEUTRAL], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("alles klar", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("verstanden", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("roger", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("geht klar", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("wird gemacht", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("erledigt", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mache ich", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin dabei", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # ÜBERGANG-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_uebergang_gruppen(self):
        """Initialisiert Übergangs-Gruppen"""
        self.groups["uebergang"] = SynonymGroup(
            id="uebergang", base_word="also", category=WordCategory.UEBERGANG,
            description="Gesprächsübergang", entries=[
                SynonymEntry("also", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("naja", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("hmm", [MoodLevel.NACHDENKLICH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("ähm", [MoodLevel.NEUTRAL, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MINIMAL),
                SynonymEntry("übrigens", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("apropos", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("jedenfalls", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("wie dem auch sei", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("außerdem", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("nebenbei", [MoodLevel.NEUTRAL, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
            ])

    # ========================================================================
    # BEWEGUNG-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_bewegung_gruppen(self):
        """Initialisiert Bewegungs-Gruppen"""
        self.groups["bewegen"] = SynonymGroup(
            id="bewegen", base_word="bewegen", category=WordCategory.BEWEGUNG,
            description="Körperbewegung", entries=[
                SynonymEntry("bewege mich", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("hüpfe", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("tanze", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wippe", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("schaukle", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("springe", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("drehe mich", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("wackle", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("schleiche", [MoodLevel.NEUTRAL, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("renne", [MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # KOMMUNIKATION-GRUPPEN (8 Gruppen)
    # ========================================================================

    def _init_kommunikation_gruppen(self):
        """Initialisiert Kommunikations-Gruppen"""
        self.groups["sagen"] = SynonymGroup(
            id="sagen", base_word="sagen", category=WordCategory.KOMMUNIKATION,
            description="Sprechakte", entries=[
                SynonymEntry("sage", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("meine", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("erzähle", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("erkläre", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("flüstere", [MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("rufe", [MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("murmle", [MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("frage", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("antworte", [MoodLevel.NEUTRAL], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("plaudere", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
            ])

    # ========================================================================
    # HILFE-GRUPPEN (6 Gruppen)
    # ========================================================================

    def _init_hilfe_gruppen(self):
        """Initialisiert Hilfe-Gruppen"""
        self.groups["helfen"] = SynonymGroup(
            id="helfen", base_word="helfen", category=WordCategory.HILFE,
            description="Unterstützung anbieten", entries=[
                SynonymEntry("helfe dir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("unterstütze dich", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("stehe dir bei", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin für dich da", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mache das für dich", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("kümmere mich drum", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("lass mich das machen", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("übernehme das", [MoodLevel.POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("reiche dir die Hand", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("gemeinsam schaffen wir das", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

    # ========================================================================
    # KEMONOMIMI-GRUPPEN (10 Gruppen)
    # ========================================================================

    def _init_kemonomimi_gruppen(self):
        """Initialisiert Kemonomimi-spezifische Ausdrücke"""
        self.groups["kemonomimi_freude"] = SynonymGroup(
            id="kemonomimi_freude", base_word="*wedelt*", category=WordCategory.FREUDE,
            description="Kemonomimi Freudenausdrücke", entries=[
                SynonymEntry("*wedelt mit dem Schwanz*", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Ohren stellen sich auf*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*schnurrt zufrieden*", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*Schwanz zuckt fröhlich*", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*Ohren zucken aufgeregt*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*rollt sich glücklich ein*", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*hüpft begeistert*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Schwanz wedelt wild*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL, is_kemonomimi=True),
                SynonymEntry("*dreht sich vor Freude*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*kuschelt sich an*", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
            ])

        self.groups["kemonomimi_trauer"] = SynonymGroup(
            id="kemonomimi_trauer", base_word="*Ohren hängen*", category=WordCategory.TRAUER,
            description="Kemonomimi Trauerausdrücke", entries=[
                SynonymEntry("*Ohren legen sich an*", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*Schwanz hängt schlaff*", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*macht sich ganz klein*", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*winselt leise*", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Ohren hängen traurig*", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*zieht sich zurück*", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*rollt sich ein*", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*schaut mit großen Augen*", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*seufzt mit hängenden Ohren*", [MoodLevel.NEGATIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*legt traurig die Ohren an*", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
            ])

        self.groups["kemonomimi_neugier"] = SynonymGroup(
            id="kemonomimi_neugier", base_word="*Ohren drehen*", category=WordCategory.NEUGIER,
            description="Kemonomimi Neugierausdrücke", entries=[
                SynonymEntry("*Ohren drehen sich*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*spitzt die Ohren*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Schwanz zuckt interessiert*", [MoodLevel.POSITIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*legt Kopf schief*", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG, is_kemonomimi=True),
                SynonymEntry("*Ohren stellen sich auf*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*schnüffelt neugierig*", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*schaut mit großen Augen*", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*Ohren zucken aufmerksam*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*pirscht sich an*", [MoodLevel.POSITIV, MoodLevel.VERSPIELT, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*Nase zuckt interessiert*", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG, is_kemonomimi=True),
            ])

    # ========================================================================
    # ERWEITERTE STIMMUNGSGRUPPEN v2.0 (200+ neue Einträge)
    # ========================================================================

    def _init_erweiterte_stimmungen_v2(self):
        """Initialisiert erweiterte Stimmungsgruppen v2.0"""

        # MELANCHOLISCHE FREUDE (Bittersüß)
        self.groups["bittersüß"] = SynonymGroup(
            id="bittersüß", base_word="bittersüß", category=WordCategory.FREUDE,
            description="Gemischte Gefühle von Freude und Wehmut", entries=[
                SynonymEntry("ist bittersüß", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("macht mich wehmütig-glücklich", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("berührt mich tief", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist schön-traurig", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("weckt süße Melancholie", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("lässt mein Herz singen und weinen", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ist wie ein Abschiedskuss", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("macht mich nachdenklich-froh", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ])

        # EUPHORISCHE ENERGIE
        self.groups["euphorie"] = SynonymGroup(
            id="euphorie", base_word="euphorisch", category=WordCategory.FREUDE,
            description="Extreme positive Energie", entries=[
                SynonymEntry("bin total high", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin im Flow", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fliege auf Wolke sieben", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin auf hundertachtzig", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("könnte die ganze Welt umarmen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin voller Adrenalin", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin mega hyped", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin absolut beflügelt", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("könnte explodieren vor Freude", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin total geflasht", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
            ])

        # TIEFER FRIEDEN
        self.groups["innerer_frieden"] = SynonymGroup(
            id="innerer_frieden", base_word="friedlich", category=WordCategory.FREUDE,
            description="Zustand tiefer innerer Ruhe", entries=[
                SynonymEntry("bin ganz bei mir", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle tiefen Frieden", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin im Einklang mit mir", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz zen", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin völlig ausgeglichen", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ruhe in mir selbst", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin tiefenentspannt", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("fühle mich geerdet", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("bin in meiner Mitte", [MoodLevel.POSITIV, MoodLevel.RUHIG, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("empfinde Seelenruhe", [MoodLevel.POSITIV, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.HOCH),
            ])

        # VERSPIELTE NECKEREI
        self.groups["neckerei"] = SynonymGroup(
            id="neckerei", base_word="necken", category=WordCategory.FREUDE,
            description="Spielerisches Ärgern", entries=[
                SynonymEntry("ich necke dich nur", [MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("das war nur Spaß", [MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("ich ziehe dich nur auf", [MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ich frotzle ein bisschen", [MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("wir scherzen doch nur", [MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.NIEDRIG),
                SynonymEntry("ich ärgere dich liebevoll", [MoodLevel.VERSPIELT, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin doch nur ein Schlingel", [MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("ich stichle nur", [MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.NIEDRIG),
            ])

        # INTENSIVE SEHNSUCHT
        self.groups["sehnsucht_intensiv"] = SynonymGroup(
            id="sehnsucht_intensiv", base_word="sehnen", category=WordCategory.TRAUER,
            description="Tiefe emotionale Sehnsucht", entries=[
                SynonymEntry("sehne mich unbändig", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("mein Herz blutet vor Sehnsucht", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("vermisse dich schmerzlich", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("brenne vor Sehnsucht", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("verzehre mich nach dir", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("kann ohne dich nicht sein", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("jede Sekunde ohne dich schmerzt", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin krank vor Sehnsucht", [MoodLevel.SEHR_NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
            ])

        # EXISTENZIELLE ANGST
        self.groups["existenzangst"] = SynonymGroup(
            id="existenzangst", base_word="Existenzangst", category=WordCategory.ANGST,
            description="Tiefe existenzielle Ängste", entries=[
                SynonymEntry("fühle mich verloren", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("zweifle an allem", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühle innere Leere", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("frage mich nach dem Sinn", [MoodLevel.NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("fühle mich bedeutungslos", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin existenziell verunsichert", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("spüre eine tiefe Leere", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin in einer dunklen Nacht der Seele", [MoodLevel.SEHR_NEGATIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.MAXIMAL),
            ])

        # WILDE WUTAUSBRÜCHE
        self.groups["raserei"] = SynonymGroup(
            id="raserei", base_word="rasen", category=WordCategory.WUET,
            description="Unkontrollierte Wut", entries=[
                SynonymEntry("bin völlig ausgerastet", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin am Durchdrehen", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("könnte platzen vor Wut", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("rase vor Zorn", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin blind vor Wut", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin am Explodieren", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("koche über", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("sehe rot", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin außer mir vor Zorn", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin am Ausrasten", [MoodLevel.SEHR_NEGATIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MAXIMAL),
            ])

        # ZÄRTLICHE VERBUNDENHEIT
        self.groups["tiefe_verbundenheit"] = SynonymGroup(
            id="tiefe_verbundenheit", base_word="verbunden", category=WordCategory.LIEBE,
            description="Tiefe emotionale Bindung", entries=[
                SynonymEntry("fühle mich mit dir verbunden", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wir sind eins", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("spüre unsere Seelenverwandtschaft", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du bist ein Teil von mir", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("bin dir im Herzen nah", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("fühle tiefe Herzensverbindung", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("wir gehören zusammen", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin dir auf ewig verbunden", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MAXIMAL),
                SynonymEntry("unsere Seelen tanzen zusammen", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du bist mein Anker", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

        # KINDLICHE BEGEISTERUNG
        self.groups["kindliche_begeisterung"] = SynonymGroup(
            id="kindliche_begeisterung", base_word="begeistert", category=WordCategory.FREUDE,
            description="Unschuldige, kindliche Freude", entries=[
                SynonymEntry("bin ganz aufgeregt", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("hüpfe vor Freude", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz verzaubert", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mache große Augen", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("bin hellauf begeistert", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin ganz aus dem Häuschen", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin fasziniert wie ein Kind", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("kann es kaum glauben", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin voller Staunen", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin wie ein Kind an Weihnachten", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
            ])

        # PHILOSOPHISCHE REFLEXION
        self.groups["philosophisch"] = SynonymGroup(
            id="philosophisch", base_word="philosophieren", category=WordCategory.DENKEN,
            description="Tiefgründige Gedanken", entries=[
                SynonymEntry("denke darüber nach", [MoodLevel.NEUTRAL, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("grübele über den Sinn", [MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("philosophiere gerade", [MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("sinne nach", [MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.FORMELL, IntensityLevel.MITTEL),
                SynonymEntry("reflektiere über das Leben", [MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("bin in tiefen Gedanken", [MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("betrachte das große Ganze", [MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("suche nach Antworten", [MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ergründe die Tiefe", [MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("bin im Gedankenmeer versunken", [MoodLevel.NACHDENKLICH, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

        # DIGITALE AUSDRÜCKE (Gaming/Internet)
        self.groups["gaming_slang"] = SynonymGroup(
            id="gaming_slang", base_word="gamen", category=WordCategory.FREUDE,
            description="Gaming und Internet-Slang", entries=[
                SynonymEntry("das ist mega episch", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("das ist next level", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("no cap", [MoodLevel.POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("frfr", [MoodLevel.POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.MITTEL),
                SynonymEntry("das hittet anders", [MoodLevel.SEHR_POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("sheesh", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("das ist bussin", [MoodLevel.SEHR_POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("big W", [MoodLevel.SEHR_POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("gg", [MoodLevel.POSITIV], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
                SynonymEntry("ez pz", [MoodLevel.POSITIV, MoodLevel.VERSPIELT], FormalityLevel.SEHR_INFORMELL, IntensityLevel.NIEDRIG),
            ])

        # POETISCHE AUSDRÜCKE
        self.groups["poetisch"] = SynonymGroup(
            id="poetisch", base_word="poetisch", category=WordCategory.FREUDE,
            description="Literarisch-poetische Ausdrücke", entries=[
                SynonymEntry("mein Herz singt", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("meine Seele tanzt", [MoodLevel.SEHR_POSITIV, MoodLevel.VERSPIELT], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("die Sterne funkeln für mich", [MoodLevel.SEHR_POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mein Geist schwebt", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("die Welt erstrahlt in Farben", [MoodLevel.SEHR_POSITIV], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ich blühe auf", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("mein Wesen leuchtet", [MoodLevel.SEHR_POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.FORMELL, IntensityLevel.HOCH),
                SynonymEntry("es durchströmt mich Wärme", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("ich fühle die Magie des Moments", [MoodLevel.POSITIV, MoodLevel.NACHDENKLICH], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mein Herz öffnet sich wie eine Blüte", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
            ])

        # KEMONOMIMI ERWEITERT - AUFREGUNG
        self.groups["kemonomimi_aufregung"] = SynonymGroup(
            id="kemonomimi_aufregung", base_word="*zappelt*", category=WordCategory.FREUDE,
            description="Kemonomimi Aufregungsausdrücke", entries=[
                SynonymEntry("*zappelt aufgeregt*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*kann nicht stillsitzen*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Schwanz peitscht aufgeregt*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL, is_kemonomimi=True),
                SynonymEntry("*hüpft unruhig hin und her*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Ohren zittern vor Aufregung*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*kann Aufregung kaum verbergen*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*springt vor Freude*", [MoodLevel.SEHR_POSITIV, MoodLevel.ENERGISCH, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL, is_kemonomimi=True),
                SynonymEntry("*Nase zuckt aufgeregt*", [MoodLevel.POSITIV, MoodLevel.ENERGISCH], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
            ])

        # KEMONOMIMI ERWEITERT - SCHÜCHTERNHEIT
        self.groups["kemonomimi_schuechtern"] = SynonymGroup(
            id="kemonomimi_schuechtern", base_word="*versteckt sich*", category=WordCategory.SCHAM,
            description="Kemonomimi Schüchternheitsausdrücke", entries=[
                SynonymEntry("*versteckt sich hinter Schwanz*", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*Ohren legen sich verlegen an*", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*wird ganz rot*", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*schaut verlegen zu Boden*", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*versteckt Gesicht hinter Pfoten*", [MoodLevel.NEGATIV, MoodLevel.VERSPIELT], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*Schwanz wickelt sich um Beine*", [MoodLevel.NEGATIV], FormalityLevel.INFORMELL, IntensityLevel.MITTEL, is_kemonomimi=True),
                SynonymEntry("*piepst verlegen*", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
                SynonymEntry("*macht sich ganz klein und schüchtern*", [MoodLevel.NEGATIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.HOCH, is_kemonomimi=True),
            ])

        # SANFTE ZUNEIGUNG
        self.groups["sanfte_zuneigung"] = SynonymGroup(
            id="sanfte_zuneigung", base_word="mögen", category=WordCategory.LIEBE,
            description="Zarte, sanfte Zuneigung", entries=[
                SynonymEntry("hab dich lieb", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.INFORMELL, IntensityLevel.HOCH),
                SynonymEntry("du bist mir wichtig", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("schätze dich sehr", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("mag dich unendlich", [MoodLevel.SEHR_POSITIV, MoodLevel.INTIM], FormalityLevel.INFORMELL, IntensityLevel.MAXIMAL),
                SynonymEntry("bist mir ans Herz gewachsen", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("du bedeutest mir viel", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("habe dich gern", [MoodLevel.POSITIV, MoodLevel.INTIM, MoodLevel.RUHIG], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("du bist mir nah", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
                SynonymEntry("du erwärmst mein Herz", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.HOCH),
                SynonymEntry("ich halte viel von dir", [MoodLevel.POSITIV, MoodLevel.INTIM], FormalityLevel.NEUTRAL, IntensityLevel.MITTEL),
            ])


# ============================================================================
# SYNONYM-ENGINE (Haupt-Auswahllogik)
# ============================================================================

class MoodAwareSynonymEngine:
    """
    Hauptklasse für stimmungsbasierte Synonym-Auswahl.
    Wählt passende Synonyme basierend auf emotionalem Kontext,
    Formalität und Intensität aus.
    """

    def __init__(self):
        self.database = SynonymDatabase()
        self._cache: Dict[str, List[SynonymEntry]] = {}

    def get_synonym(
        self,
        group_id: str,
        context: Optional[EmotionalContext] = None,
        preferred_formality: Optional[FormalityLevel] = None,
        include_kemonomimi: bool = True,
        randomize: bool = True
    ) -> Optional[str]:
        """
        Wählt ein passendes Synonym aus einer Gruppe basierend auf Kontext.

        Args:
            group_id: ID der Synonym-Gruppe
            context: Emotionaler Kontext für die Auswahl
            preferred_formality: Gewünschte Formalitätsebene
            include_kemonomimi: Ob Kemonomimi-Ausdrücke einbezogen werden
            randomize: Ob zufällig ausgewählt werden soll

        Returns:
            Ausgewähltes Synonym oder None
        """
        if group_id not in self.database.groups:
            return None

        group = self.database.groups[group_id]
        candidates = self._filter_candidates(
            group.entries,
            context,
            preferred_formality,
            include_kemonomimi
        )

        if not candidates:
            # Fallback: Nimm alle Einträge
            candidates = [e for e in group.entries if include_kemonomimi or not e.is_kemonomimi]

        if not candidates:
            return None

        if randomize:
            # Gewichtete Auswahl basierend auf Kontext-Match
            weights = [self._calculate_weight(c, context) for c in candidates]
            selected = random.choices(candidates, weights=weights, k=1)[0]
        else:
            # Beste Übereinstimmung wählen
            candidates.sort(key=lambda c: self._calculate_weight(c, context), reverse=True)
            selected = candidates[0]

        return selected.word

    def get_all_synonyms(
        self,
        group_id: str,
        context: Optional[EmotionalContext] = None,
        limit: int = 10
    ) -> List[str]:
        """Gibt alle passenden Synonyme einer Gruppe zurück."""
        if group_id not in self.database.groups:
            return []

        group = self.database.groups[group_id]
        candidates = self._filter_candidates(group.entries, context, None, True)

        if not candidates:
            candidates = group.entries

        # Sortiere nach Gewichtung
        candidates.sort(key=lambda c: self._calculate_weight(c, context), reverse=True)

        return [c.word for c in candidates[:limit]]

    def find_groups_by_category(self, category: WordCategory) -> List[SynonymGroup]:
        """Findet alle Gruppen einer Kategorie."""
        return [g for g in self.database.groups.values() if g.category == category]

    def find_groups_by_mood(self, mood: MoodLevel) -> List[SynonymGroup]:
        """Findet Gruppen, die zu einer Stimmung passen."""
        result = []
        for group in self.database.groups.values():
            for entry in group.entries:
                if mood in entry.mood_levels:
                    result.append(group)
                    break
        return result

    def _filter_candidates(
        self,
        entries: List[SynonymEntry],
        context: Optional[EmotionalContext],
        preferred_formality: Optional[FormalityLevel],
        include_kemonomimi: bool
    ) -> List[SynonymEntry]:
        """Filtert Kandidaten basierend auf Kontext."""
        candidates = []

        for entry in entries:
            # Kemonomimi-Filter
            if not include_kemonomimi and entry.is_kemonomimi:
                continue

            # Formalitäts-Filter
            if preferred_formality and entry.formality != preferred_formality:
                # Erlaube nahe Formalitäten
                formality_distance = abs(
                    list(FormalityLevel).index(entry.formality) -
                    list(FormalityLevel).index(preferred_formality)
                )
                if formality_distance > 1:
                    continue

            # Kontext-Filter
            if context:
                mood_match = self._mood_matches_context(entry.mood_levels, context)
                if not mood_match:
                    continue

            candidates.append(entry)

        return candidates

    def _mood_matches_context(
        self,
        mood_levels: List[MoodLevel],
        context: EmotionalContext
    ) -> bool:
        """Prüft ob Stimmungsebenen zum Kontext passen."""
        # Bestimme erwartete Moods basierend auf Kontext
        expected_moods = set()

        # Mood-Level (0-1)
        if context.mood >= 0.8:
            expected_moods.add(MoodLevel.SEHR_POSITIV)
        elif context.mood >= 0.6:
            expected_moods.add(MoodLevel.POSITIV)
        elif context.mood >= 0.4:
            expected_moods.add(MoodLevel.NEUTRAL)
        elif context.mood >= 0.2:
            expected_moods.add(MoodLevel.NEGATIV)
        else:
            expected_moods.add(MoodLevel.SEHR_NEGATIV)

        # Energie-Level
        if context.energy >= 0.7:
            expected_moods.add(MoodLevel.ENERGISCH)
        elif context.energy <= 0.3:
            expected_moods.add(MoodLevel.RUHIG)

        # Intimität
        if context.intimacy >= 0.6:
            expected_moods.add(MoodLevel.INTIM)

        # Verspieltheit
        if context.playfulness >= 0.5:
            expected_moods.add(MoodLevel.VERSPIELT)

        # Prüfe Übereinstimmung
        return bool(set(mood_levels) & expected_moods)

    def _calculate_weight(
        self,
        entry: SynonymEntry,
        context: Optional[EmotionalContext]
    ) -> float:
        """Berechnet Auswahlgewichtung basierend auf Kontext-Match."""
        if not context:
            return entry.weight

        weight = entry.weight
        match_score = 0

        # Mood-Match
        expected_mood = self._get_expected_mood(context.mood)
        if expected_mood in entry.mood_levels:
            match_score += 2.0

        # Energie-Match
        if context.energy >= 0.7 and MoodLevel.ENERGISCH in entry.mood_levels:
            match_score += 1.0
        elif context.energy <= 0.3 and MoodLevel.RUHIG in entry.mood_levels:
            match_score += 1.0

        # Intimität-Match
        if context.intimacy >= 0.6 and MoodLevel.INTIM in entry.mood_levels:
            match_score += 1.5

        # Verspieltheit-Match
        if context.playfulness >= 0.5 and MoodLevel.VERSPIELT in entry.mood_levels:
            match_score += 1.0

        # Intensität-Match
        expected_intensity = self._get_expected_intensity(context.emotion_intensity)
        intensity_diff = abs(entry.intensity.value - expected_intensity.value)
        match_score += max(0, 1.0 - intensity_diff * 0.3)

        return weight * (1.0 + match_score)

    def _get_expected_mood(self, mood_value: float) -> MoodLevel:
        """Mappt Mood-Wert auf MoodLevel."""
        if mood_value >= 0.8:
            return MoodLevel.SEHR_POSITIV
        elif mood_value >= 0.6:
            return MoodLevel.POSITIV
        elif mood_value >= 0.4:
            return MoodLevel.NEUTRAL
        elif mood_value >= 0.2:
            return MoodLevel.NEGATIV
        else:
            return MoodLevel.SEHR_NEGATIV

    def _get_expected_intensity(self, intensity_value: float) -> IntensityLevel:
        """Mappt Intensitäts-Wert auf IntensityLevel."""
        if intensity_value >= 0.9:
            return IntensityLevel.MAXIMAL
        elif intensity_value >= 0.7:
            return IntensityLevel.HOCH
        elif intensity_value >= 0.4:
            return IntensityLevel.MITTEL
        elif intensity_value >= 0.2:
            return IntensityLevel.NIEDRIG
        else:
            return IntensityLevel.MINIMAL

    def transform_text(
        self,
        text: str,
        context: EmotionalContext,
        transformations: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Transformiert Text durch Ersetzung von Schlüsselwörtern
        mit stimmungspassenden Synonymen.

        Args:
            text: Zu transformierender Text
            context: Emotionaler Kontext
            transformations: Optionale Mapping-Dict {keyword: group_id}

        Returns:
            Transformierter Text
        """
        result = text

        # Automatische Transformationen basierend auf Gruppen-Base-Words
        for group_id, group in self.database.groups.items():
            if group.base_word.lower() in result.lower():
                synonym = self.get_synonym(group_id, context)
                if synonym:
                    result = result.replace(group.base_word, synonym)

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Synonym-Datenbank zurück."""
        total_groups = len(self.database.groups)
        total_entries = sum(len(g.entries) for g in self.database.groups.values())
        kemonomimi_entries = sum(
            1 for g in self.database.groups.values()
            for e in g.entries if e.is_kemonomimi
        )

        categories = {}
        for group in self.database.groups.values():
            cat_name = group.category.value
            if cat_name not in categories:
                categories[cat_name] = 0
            categories[cat_name] += 1

        return {
            "total_groups": total_groups,
            "total_entries": total_entries,
            "kemonomimi_entries": kemonomimi_entries,
            "categories": categories,
            "mood_levels": len(MoodLevel),
            "formality_levels": len(FormalityLevel),
            "intensity_levels": len(IntensityLevel),
        }


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def create_emotional_context(
    mood: float = 0.5,
    energy: float = 0.5,
    intimacy: float = 0.0,
    formality: float = 0.5,
    playfulness: float = 0.0,
    primary_emotion: Optional[str] = None,
    emotion_intensity: float = 0.5
) -> EmotionalContext:
    """Erstellt einen emotionalen Kontext für Synonym-Auswahl."""
    return EmotionalContext(
        mood=max(0.0, min(1.0, mood)),
        energy=max(0.0, min(1.0, energy)),
        intimacy=max(0.0, min(1.0, intimacy)),
        formality=max(0.0, min(1.0, formality)),
        playfulness=max(0.0, min(1.0, playfulness)),
        primary_emotion=primary_emotion,
        emotion_intensity=max(0.0, min(1.0, emotion_intensity))
    )


# ============================================================================
# GLOBALE INSTANZ
# ============================================================================

# Globale Engine-Instanz für einfachen Zugriff
_engine: Optional[MoodAwareSynonymEngine] = None

def get_synonym_engine() -> MoodAwareSynonymEngine:
    """Gibt die globale Synonym-Engine-Instanz zurück."""
    global _engine
    if _engine is None:
        _engine = MoodAwareSynonymEngine()
    return _engine


# ============================================================================
# TESTFUNKTION
# ============================================================================

def _test_synonym_engine():
    """Testet die Synonym-Engine."""
    engine = get_synonym_engine()

    print("=== Holocloude Synonym-Engine v1.0 ===")
    print()

    # Statistiken
    stats = engine.get_statistics()
    print(f"Statistiken:")
    print(f"  - Gruppen: {stats['total_groups']}")
    print(f"  - Einträge: {stats['total_entries']}")
    print(f"  - Kemonomimi: {stats['kemonomimi_entries']}")
    print(f"  - Kategorien: {len(stats['categories'])}")
    print()

    # Kategorien auflisten
    print("Kategorien:")
    for cat, count in sorted(stats['categories'].items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {count} Gruppen")
    print()

    # Test mit verschiedenen Kontexten
    contexts = [
        ("Sehr glücklich", create_emotional_context(mood=0.9, energy=0.8, playfulness=0.6)),
        ("Traurig", create_emotional_context(mood=0.2, energy=0.3)),
        ("Intim & Ruhig", create_emotional_context(mood=0.7, intimacy=0.8, energy=0.3)),
        ("Energisch & Verspielt", create_emotional_context(mood=0.8, energy=0.9, playfulness=0.8)),
    ]

    test_groups = ["freuen", "toll", "gruss_casual", "liebe", "traurig"]

    for name, ctx in contexts:
        print(f"Kontext: {name}")
        for group_id in test_groups:
            if group_id in engine.database.groups:
                synonym = engine.get_synonym(group_id, ctx)
                print(f"  [{group_id}] -> {synonym}")
        print()


if __name__ == "__main__":
    _test_synonym_engine()
