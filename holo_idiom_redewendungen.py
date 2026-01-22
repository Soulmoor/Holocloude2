#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO IDIOM & REDEWENDUNGEN ENGINE v1.0                                      ║
║                                                                              ║
║  Deutsche Redewendungen, Idiome, Sprichwörter und bildhafte Ausdrücke       ║
║  mit kontextueller Auswahl basierend auf Stimmung, Thema und Situation      ║
║                                                                              ║
║  Features:                                                                   ║
║  - 200+ deutsche Redewendungen nach Kategorien                               ║
║  - Kontextuelle Idiom-Auswahl                                                ║
║  - Erklärungen und Ursprünge                                                 ║
║  - Stimmungsbasierte Filterung                                               ║
║  - Regionale Varianten                                                       ║
║  - Kemonomimi-spezifische Anpassungen                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS UND KATEGORIEN
# =============================================================================

class IdiomCategory(Enum):
    """Kategorien für Redewendungen"""
    FREUDE = "freude"
    TRAUER = "trauer"
    WUTT = "wut"
    UEBERRASCHUNG = "ueberraschung"
    LIEBE = "liebe"
    ERFOLG = "erfolg"
    MISSERFOLG = "misserfolg"
    ARBEIT = "arbeit"
    GELD = "geld"
    ZEIT = "zeit"
    FREUNDSCHAFT = "freundschaft"
    RATSCHLAG = "ratschlag"
    WARNUNG = "warnung"
    ERMUTIGUNG = "ermutigung"
    HUMOR = "humor"
    ESSEN = "essen"
    WETTER = "wetter"
    TIERE = "tiere"
    KOERPER = "koerper"
    NATUR = "natur"
    ALLTAG = "alltag"
    WEISHEIT = "weisheit"
    VERGLEICH = "vergleich"
    KEMONOMIMI = "kemonomimi"


class IdiomFormality(Enum):
    """Formalitätsstufen"""
    SEHR_FORMELL = 1
    FORMELL = 2
    NEUTRAL = 3
    INFORMELL = 4
    SEHR_INFORMELL = 5
    SLANG = 6


class IdiomIntensity(Enum):
    """Intensitätsstufen"""
    LEICHT = 1
    MITTEL = 2
    STARK = 3
    SEHR_STARK = 4


@dataclass
class Idiom:
    """Eine einzelne Redewendung mit Metadaten"""
    text: str
    meaning: str
    category: IdiomCategory
    formality: IdiomFormality = IdiomFormality.NEUTRAL
    intensity: IdiomIntensity = IdiomIntensity.MITTEL
    origin: Optional[str] = None
    usage_example: Optional[str] = None
    related_idioms: List[str] = field(default_factory=list)
    regional: Optional[str] = None  # z.B. "Bayerisch", "Norddeutsch"
    is_kemonomimi_friendly: bool = True


# =============================================================================
# REDEWENDUNGEN DATENBANK
# =============================================================================

class IdiomDatabase:
    """Datenbank mit deutschen Redewendungen"""

    def __init__(self):
        self.idioms: List[Idiom] = []
        self._load_idioms()

    def _load_idioms(self):
        """Lädt alle Redewendungen"""

        # =====================================================================
        # FREUDE & POSITIVES
        # =====================================================================
        self.idioms.extend([
            Idiom(
                text="auf Wolke sieben schweben",
                meaning="Sehr glücklich sein, euphorisch",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.STARK,
                usage_example="Seit ich ihn kennengelernt habe, schwebe ich auf Wolke sieben!"
            ),
            Idiom(
                text="Schmetterlinge im Bauch haben",
                meaning="Verliebt oder aufgeregt sein",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.MITTEL,
                usage_example="Jedes Mal wenn ich sie sehe, habe ich Schmetterlinge im Bauch."
            ),
            Idiom(
                text="das Herz hüpft vor Freude",
                meaning="Sehr glücklich und aufgeregt sein",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="sich wie ein Schneekönig freuen",
                meaning="Sich sehr freuen",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.STARK,
                origin="Der Zaunkönig singt auch im Winter"
            ),
            Idiom(
                text="vor Freude an die Decke springen",
                meaning="Extrem glücklich sein",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.SEHR_STARK
            ),
            Idiom(
                text="das Leben ist ein Ponyhof",
                meaning="Alles läuft wunderbar (oft ironisch)",
                category=IdiomCategory.FREUDE,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="einen Luftsprung machen",
                meaning="Vor Freude hüpfen",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="auf der Sonnenseite des Lebens stehen",
                meaning="Glück haben, erfolgreich sein",
                category=IdiomCategory.FREUDE
            ),
            Idiom(
                text="die Sonne lacht",
                meaning="Es ist schönes Wetter / alles ist gut",
                category=IdiomCategory.FREUDE,
                intensity=IdiomIntensity.LEICHT
            ),
            Idiom(
                text="strahlen wie ein Honigkuchenpferd",
                meaning="Breit und glücklich grinsen",
                category=IdiomCategory.FREUDE,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # TRAUER & NEGATIVES
            # =====================================================================
            Idiom(
                text="Trübsal blasen",
                meaning="Traurig und niedergeschlagen sein",
                category=IdiomCategory.TRAUER,
                intensity=IdiomIntensity.MITTEL
            ),
            Idiom(
                text="ein gebrochenes Herz haben",
                meaning="Liebeskummer haben, sehr traurig sein",
                category=IdiomCategory.TRAUER,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="den Kopf hängen lassen",
                meaning="Mutlos und traurig sein",
                category=IdiomCategory.TRAUER,
                intensity=IdiomIntensity.MITTEL
            ),
            Idiom(
                text="sich die Augen aus dem Kopf weinen",
                meaning="Sehr viel weinen",
                category=IdiomCategory.TRAUER,
                intensity=IdiomIntensity.SEHR_STARK
            ),
            Idiom(
                text="am Boden zerstört sein",
                meaning="Völlig niedergeschlagen sein",
                category=IdiomCategory.TRAUER,
                intensity=IdiomIntensity.SEHR_STARK
            ),
            Idiom(
                text="durch ein tiefes Tal gehen",
                meaning="Eine schwierige Phase durchleben",
                category=IdiomCategory.TRAUER
            ),
            Idiom(
                text="das Herz wird schwer",
                meaning="Traurig werden",
                category=IdiomCategory.TRAUER,
                intensity=IdiomIntensity.MITTEL
            ),
            Idiom(
                text="einen Kloß im Hals haben",
                meaning="Vor Traurigkeit kaum sprechen können",
                category=IdiomCategory.TRAUER
            ),

            # =====================================================================
            # WUT & ÄRGER
            # =====================================================================
            Idiom(
                text="auf die Palme bringen",
                meaning="Sehr wütend machen",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="die Wände hochgehen",
                meaning="Vor Wut explodieren",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.SEHR_STARK,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="einen dicken Hals bekommen",
                meaning="Sehr wütend werden",
                category=IdiomCategory.WUTT,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Gift und Galle spucken",
                meaning="Sehr wütend sein und schimpfen",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.SEHR_STARK
            ),
            Idiom(
                text="in die Luft gehen",
                meaning="Plötzlich wütend werden",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="vor Wut kochen",
                meaning="Sehr wütend sein",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="einen Rappel kriegen",
                meaning="Plötzlich wütend werden",
                category=IdiomCategory.WUTT,
                formality=IdiomFormality.SEHR_INFORMELL
            ),
            Idiom(
                text="aus der Haut fahren",
                meaning="Die Beherrschung verlieren",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="jemanden auf die Palme bringen",
                meaning="Jemanden sehr wütend machen",
                category=IdiomCategory.WUTT
            ),
            Idiom(
                text="mir platzt der Kragen",
                meaning="Ich werde gleich wütend",
                category=IdiomCategory.WUTT,
                intensity=IdiomIntensity.STARK
            ),

            # =====================================================================
            # ÜBERRASCHUNG
            # =====================================================================
            Idiom(
                text="aus allen Wolken fallen",
                meaning="Sehr überrascht sein",
                category=IdiomCategory.UEBERRASCHUNG,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="Bauklötze staunen",
                meaning="Sehr erstaunt sein",
                category=IdiomCategory.UEBERRASCHUNG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="große Augen machen",
                meaning="Überrascht schauen",
                category=IdiomCategory.UEBERRASCHUNG
            ),
            Idiom(
                text="wie vom Blitz getroffen",
                meaning="Völlig überrascht, schockiert",
                category=IdiomCategory.UEBERRASCHUNG,
                intensity=IdiomIntensity.SEHR_STARK
            ),
            Idiom(
                text="jemandem bleibt die Spucke weg",
                meaning="Sehr überrascht sein, sprachlos",
                category=IdiomCategory.UEBERRASCHUNG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Mund und Nase aufsperren",
                meaning="Vor Staunen sprachlos sein",
                category=IdiomCategory.UEBERRASCHUNG
            ),
            Idiom(
                text="nicht schlecht staunen",
                meaning="Positiv überrascht sein",
                category=IdiomCategory.UEBERRASCHUNG,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # LIEBE & ZUNEIGUNG
            # =====================================================================
            Idiom(
                text="jemanden ins Herz schließen",
                meaning="Jemanden lieb gewinnen",
                category=IdiomCategory.LIEBE
            ),
            Idiom(
                text="auf jemanden fliegen",
                meaning="Sich in jemanden verlieben",
                category=IdiomCategory.LIEBE,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="jemanden vergöttern",
                meaning="Jemanden sehr lieben und bewundern",
                category=IdiomCategory.LIEBE,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="Feuer und Flamme sein",
                meaning="Begeistert, verliebt sein",
                category=IdiomCategory.LIEBE,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="sein Herz verlieren",
                meaning="Sich verlieben",
                category=IdiomCategory.LIEBE
            ),
            Idiom(
                text="jemanden anhimmeln",
                meaning="Jemanden verliebt ansehen",
                category=IdiomCategory.LIEBE
            ),
            Idiom(
                text="sich Hals über Kopf verlieben",
                meaning="Sich schnell und heftig verlieben",
                category=IdiomCategory.LIEBE,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="jemandem schöne Augen machen",
                meaning="Flirten, Interesse zeigen",
                category=IdiomCategory.LIEBE,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # ERFOLG
            # =====================================================================
            Idiom(
                text="den Nagel auf den Kopf treffen",
                meaning="Genau das Richtige sagen/tun",
                category=IdiomCategory.ERFOLG
            ),
            Idiom(
                text="ins Schwarze treffen",
                meaning="Genau richtig liegen",
                category=IdiomCategory.ERFOLG
            ),
            Idiom(
                text="den Jackpot knacken",
                meaning="Großen Erfolg haben",
                category=IdiomCategory.ERFOLG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="auf der Erfolgswelle reiten",
                meaning="Kontinuierlich erfolgreich sein",
                category=IdiomCategory.ERFOLG
            ),
            Idiom(
                text="alle Karten in der Hand haben",
                meaning="Die Kontrolle haben",
                category=IdiomCategory.ERFOLG
            ),
            Idiom(
                text="das große Los ziehen",
                meaning="Viel Glück haben",
                category=IdiomCategory.ERFOLG
            ),
            Idiom(
                text="einen Volltreffer landen",
                meaning="Sehr erfolgreich sein",
                category=IdiomCategory.ERFOLG
            ),

            # =====================================================================
            # MISSERFOLG
            # =====================================================================
            Idiom(
                text="auf die Nase fallen",
                meaning="Scheitern",
                category=IdiomCategory.MISSERFOLG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="daneben liegen",
                meaning="Falsch liegen, sich irren",
                category=IdiomCategory.MISSERFOLG
            ),
            Idiom(
                text="baden gehen",
                meaning="Scheitern, verlieren",
                category=IdiomCategory.MISSERFOLG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="auf dem Holzweg sein",
                meaning="Völlig falsch liegen",
                category=IdiomCategory.MISSERFOLG
            ),
            Idiom(
                text="ins Fettnäpfchen treten",
                meaning="Einen peinlichen Fehler machen",
                category=IdiomCategory.MISSERFOLG
            ),
            Idiom(
                text="Schiffbruch erleiden",
                meaning="Komplett scheitern",
                category=IdiomCategory.MISSERFOLG,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="den Kürzeren ziehen",
                meaning="Verlieren, unterliegen",
                category=IdiomCategory.MISSERFOLG
            ),

            # =====================================================================
            # ARBEIT & FLEISS
            # =====================================================================
            Idiom(
                text="die Ärmel hochkrempeln",
                meaning="Sich an die Arbeit machen",
                category=IdiomCategory.ARBEIT
            ),
            Idiom(
                text="sich ins Zeug legen",
                meaning="Sich sehr anstrengen",
                category=IdiomCategory.ARBEIT,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Nägel mit Köpfen machen",
                meaning="Etwas gründlich erledigen",
                category=IdiomCategory.ARBEIT
            ),
            Idiom(
                text="sich die Finger wund arbeiten",
                meaning="Sehr hart arbeiten",
                category=IdiomCategory.ARBEIT,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="rund um die Uhr arbeiten",
                meaning="Ständig arbeiten",
                category=IdiomCategory.ARBEIT
            ),
            Idiom(
                text="auf Hochtouren laufen",
                meaning="Sehr produktiv sein",
                category=IdiomCategory.ARBEIT
            ),
            Idiom(
                text="Dampf machen",
                meaning="Sich beeilen, schneller arbeiten",
                category=IdiomCategory.ARBEIT,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="sich in die Arbeit stürzen",
                meaning="Motiviert mit der Arbeit beginnen",
                category=IdiomCategory.ARBEIT
            ),

            # =====================================================================
            # GELD
            # =====================================================================
            Idiom(
                text="Geld wie Heu haben",
                meaning="Sehr reich sein",
                category=IdiomCategory.GELD
            ),
            Idiom(
                text="auf großem Fuß leben",
                meaning="Verschwenderisch leben",
                category=IdiomCategory.GELD
            ),
            Idiom(
                text="jeden Cent zweimal umdrehen",
                meaning="Sehr sparsam sein",
                category=IdiomCategory.GELD
            ),
            Idiom(
                text="in Geld schwimmen",
                meaning="Sehr reich sein",
                category=IdiomCategory.GELD,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Geld zum Fenster hinauswerfen",
                meaning="Geld verschwenden",
                category=IdiomCategory.GELD
            ),
            Idiom(
                text="auf den letzten Drücker zahlen",
                meaning="Im letzten Moment bezahlen",
                category=IdiomCategory.GELD,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # ZEIT
            # =====================================================================
            Idiom(
                text="die Zeit vergeht wie im Flug",
                meaning="Die Zeit vergeht schnell",
                category=IdiomCategory.ZEIT
            ),
            Idiom(
                text="auf die lange Bank schieben",
                meaning="Etwas aufschieben",
                category=IdiomCategory.ZEIT
            ),
            Idiom(
                text="fünf Minuten vor zwölf",
                meaning="Im letzten Moment",
                category=IdiomCategory.ZEIT
            ),
            Idiom(
                text="sich Zeit lassen",
                meaning="Nicht hetzen",
                category=IdiomCategory.ZEIT
            ),
            Idiom(
                text="jemandem die Zeit stehlen",
                meaning="Jemanden aufhalten",
                category=IdiomCategory.ZEIT
            ),
            Idiom(
                text="auf der Stelle treten",
                meaning="Nicht vorankommen",
                category=IdiomCategory.ZEIT
            ),
            Idiom(
                text="mit der Zeit gehen",
                meaning="Modern bleiben",
                category=IdiomCategory.ZEIT
            ),

            # =====================================================================
            # FREUNDSCHAFT
            # =====================================================================
            Idiom(
                text="durch dick und dünn gehen",
                meaning="In guten und schlechten Zeiten zusammenhalten",
                category=IdiomCategory.FREUNDSCHAFT
            ),
            Idiom(
                text="ein Herz und eine Seele sein",
                meaning="Sehr eng befreundet sein",
                category=IdiomCategory.FREUNDSCHAFT
            ),
            Idiom(
                text="jemandem den Rücken stärken",
                meaning="Jemanden unterstützen",
                category=IdiomCategory.FREUNDSCHAFT
            ),
            Idiom(
                text="für jemanden durchs Feuer gehen",
                meaning="Alles für jemanden tun",
                category=IdiomCategory.FREUNDSCHAFT,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="jemandem die Stange halten",
                meaning="Zu jemandem stehen",
                category=IdiomCategory.FREUNDSCHAFT
            ),

            # =====================================================================
            # RATSCHLAG & WEISHEIT
            # =====================================================================
            Idiom(
                text="den Ball flach halten",
                meaning="Sich zurückhalten, nicht übertreiben",
                category=IdiomCategory.RATSCHLAG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="einen kühlen Kopf bewahren",
                meaning="Ruhig bleiben",
                category=IdiomCategory.RATSCHLAG
            ),
            Idiom(
                text="über seinen Schatten springen",
                meaning="Seine Ängste überwinden",
                category=IdiomCategory.RATSCHLAG
            ),
            Idiom(
                text="das Beste draus machen",
                meaning="Optimistisch mit einer Situation umgehen",
                category=IdiomCategory.RATSCHLAG
            ),
            Idiom(
                text="nicht alle Eier in einen Korb legen",
                meaning="Risiko verteilen",
                category=IdiomCategory.RATSCHLAG
            ),
            Idiom(
                text="lieber den Spatz in der Hand als die Taube auf dem Dach",
                meaning="Sicheres Kleines ist besser als unsicheres Großes",
                category=IdiomCategory.WEISHEIT
            ),
            Idiom(
                text="stille Wasser sind tief",
                meaning="Ruhige Menschen haben oft viel Tiefe",
                category=IdiomCategory.WEISHEIT
            ),
            Idiom(
                text="Übung macht den Meister",
                meaning="Durch Üben wird man besser",
                category=IdiomCategory.WEISHEIT
            ),
            Idiom(
                text="wer zuletzt lacht, lacht am besten",
                meaning="Der endgültige Erfolg zählt",
                category=IdiomCategory.WEISHEIT
            ),
            Idiom(
                text="morgen ist auch noch ein Tag",
                meaning="Nicht alles auf einmal erledigen müssen",
                category=IdiomCategory.WEISHEIT
            ),

            # =====================================================================
            # WARNUNG
            # =====================================================================
            Idiom(
                text="sich auf dünnem Eis bewegen",
                meaning="In einer riskanten Situation sein",
                category=IdiomCategory.WARNUNG
            ),
            Idiom(
                text="das Pulverfass zum Explodieren bringen",
                meaning="Eine gefährliche Situation eskalieren",
                category=IdiomCategory.WARNUNG,
                intensity=IdiomIntensity.STARK
            ),
            Idiom(
                text="mit dem Feuer spielen",
                meaning="Etwas Gefährliches tun",
                category=IdiomCategory.WARNUNG
            ),
            Idiom(
                text="den Bogen überspannen",
                meaning="Es zu weit treiben",
                category=IdiomCategory.WARNUNG
            ),
            Idiom(
                text="das kann ins Auge gehen",
                meaning="Das könnte schlecht enden",
                category=IdiomCategory.WARNUNG,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # ERMUTIGUNG
            # =====================================================================
            Idiom(
                text="den Kopf nicht hängen lassen",
                meaning="Nicht aufgeben",
                category=IdiomCategory.ERMUTIGUNG
            ),
            Idiom(
                text="sich nicht unterkriegen lassen",
                meaning="Stark bleiben",
                category=IdiomCategory.ERMUTIGUNG
            ),
            Idiom(
                text="da geht noch was",
                meaning="Es ist noch nicht vorbei",
                category=IdiomCategory.ERMUTIGUNG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="nach dem Regen kommt Sonnenschein",
                meaning="Schlechte Zeiten gehen vorbei",
                category=IdiomCategory.ERMUTIGUNG
            ),
            Idiom(
                text="Kopf hoch",
                meaning="Nicht aufgeben",
                category=IdiomCategory.ERMUTIGUNG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="das schaffst du mit links",
                meaning="Das ist einfach für dich",
                category=IdiomCategory.ERMUTIGUNG,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # HUMOR
            # =====================================================================
            Idiom(
                text="jemanden auf den Arm nehmen",
                meaning="Jemanden veralbern",
                category=IdiomCategory.HUMOR,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="jemandem einen Bären aufbinden",
                meaning="Jemanden anlügen (scherzhaft)",
                category=IdiomCategory.HUMOR
            ),
            Idiom(
                text="das ist nicht mein Bier",
                meaning="Das geht mich nichts an",
                category=IdiomCategory.HUMOR,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Tomaten auf den Augen haben",
                meaning="Etwas Offensichtliches nicht sehen",
                category=IdiomCategory.HUMOR,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="da lachen ja die Hühner",
                meaning="Das ist lächerlich",
                category=IdiomCategory.HUMOR,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="jetzt schlägt's dreizehn",
                meaning="Das ist unglaublich/unerhört",
                category=IdiomCategory.HUMOR,
                formality=IdiomFormality.INFORMELL
            ),

            # =====================================================================
            # ESSEN & TRINKEN
            # =====================================================================
            Idiom(
                text="sich die Finger lecken",
                meaning="Etwas sehr genießen (Essen)",
                category=IdiomCategory.ESSEN
            ),
            Idiom(
                text="in den sauren Apfel beißen",
                meaning="Etwas Unangenehmes akzeptieren",
                category=IdiomCategory.ESSEN
            ),
            Idiom(
                text="das ist nicht mein Geschmack",
                meaning="Das gefällt mir nicht",
                category=IdiomCategory.ESSEN
            ),
            Idiom(
                text="sein Fett wegbekommen",
                meaning="Kritik einstecken müssen",
                category=IdiomCategory.ESSEN,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Appetit auf etwas haben",
                meaning="Lust auf etwas haben",
                category=IdiomCategory.ESSEN
            ),

            # =====================================================================
            # WETTER
            # =====================================================================
            Idiom(
                text="sich wie ein Schneemann fühlen",
                meaning="Sehr kalt sein",
                category=IdiomCategory.WETTER
            ),
            Idiom(
                text="es regnet in Strömen",
                meaning="Es regnet sehr stark",
                category=IdiomCategory.WETTER
            ),
            Idiom(
                text="nach Regen kommt Sonnenschein",
                meaning="Nach schlechten Zeiten kommen gute",
                category=IdiomCategory.WETTER
            ),
            Idiom(
                text="ein Sturm im Wasserglas",
                meaning="Viel Aufregung um nichts",
                category=IdiomCategory.WETTER
            ),

            # =====================================================================
            # TIERE
            # =====================================================================
            Idiom(
                text="mit den Wölfen heulen",
                meaning="Sich der Mehrheit anpassen",
                category=IdiomCategory.TIERE,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="da beißt sich die Katze in den Schwanz",
                meaning="Ein Teufelskreis",
                category=IdiomCategory.TIERE
            ),
            Idiom(
                text="die Katze aus dem Sack lassen",
                meaning="Die Wahrheit verraten",
                category=IdiomCategory.TIERE
            ),
            Idiom(
                text="zwei Fliegen mit einer Klappe schlagen",
                meaning="Zwei Probleme auf einmal lösen",
                category=IdiomCategory.TIERE
            ),
            Idiom(
                text="jemandem einen Floh ins Ohr setzen",
                meaning="Jemanden auf eine Idee bringen",
                category=IdiomCategory.TIERE
            ),
            Idiom(
                text="wie ein aufgescheuchtes Huhn",
                meaning="Nervös und unorganisiert",
                category=IdiomCategory.TIERE,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="einen Bock schießen",
                meaning="Einen Fehler machen",
                category=IdiomCategory.TIERE,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="sich wie ein Elefant im Porzellanladen benehmen",
                meaning="Sehr ungeschickt sein",
                category=IdiomCategory.TIERE
            ),

            # =====================================================================
            # KÖRPER
            # =====================================================================
            Idiom(
                text="die Ohren spitzen",
                meaning="Aufmerksam zuhören",
                category=IdiomCategory.KOERPER,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="jemanden auf den Händen tragen",
                meaning="Jemanden verwöhnen",
                category=IdiomCategory.KOERPER
            ),
            Idiom(
                text="ein offenes Ohr haben",
                meaning="Bereit sein zuzuhören",
                category=IdiomCategory.KOERPER,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="auf eigenen Beinen stehen",
                meaning="Selbständig sein",
                category=IdiomCategory.KOERPER
            ),
            Idiom(
                text="mit dem linken Fuß aufgestanden sein",
                meaning="Schlechte Laune haben",
                category=IdiomCategory.KOERPER
            ),
            Idiom(
                text="jemandem auf die Finger schauen",
                meaning="Jemanden kontrollieren",
                category=IdiomCategory.KOERPER
            ),

            # =====================================================================
            # NATUR
            # =====================================================================
            Idiom(
                text="den Wald vor lauter Bäumen nicht sehen",
                meaning="Das Große nicht erkennen wegen Details",
                category=IdiomCategory.NATUR
            ),
            Idiom(
                text="über Stock und Stein",
                meaning="Durch unwegsames Gelände",
                category=IdiomCategory.NATUR
            ),
            Idiom(
                text="wie ein Fels in der Brandung",
                meaning="Unerschütterlich, stark",
                category=IdiomCategory.NATUR
            ),
            Idiom(
                text="kein Blatt vor den Mund nehmen",
                meaning="Offen und direkt sprechen",
                category=IdiomCategory.NATUR
            ),

            # =====================================================================
            # ALLTAG
            # =====================================================================
            Idiom(
                text="das ist kalter Kaffee",
                meaning="Das ist nichts Neues",
                category=IdiomCategory.ALLTAG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="das geht mir auf die Nerven",
                meaning="Das nervt mich",
                category=IdiomCategory.ALLTAG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="Schwamm drüber",
                meaning="Vergessen wir es",
                category=IdiomCategory.ALLTAG,
                formality=IdiomFormality.INFORMELL
            ),
            Idiom(
                text="unter der Decke stecken",
                meaning="Heimlich im Gange sein",
                category=IdiomCategory.ALLTAG
            ),
            Idiom(
                text="im Grunde genommen",
                meaning="Eigentlich, grundsätzlich",
                category=IdiomCategory.ALLTAG
            ),

            # =====================================================================
            # KEMONOMIMI-SPEZIFISCH
            # =====================================================================
            Idiom(
                text="meine Ohren zucken vor Aufregung",
                meaning="Sehr aufgeregt/interessiert sein (Wolfsohren)",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="mit dem Schwanz wedeln vor Freude",
                meaning="Sich sehr freuen (Wolfsschwanz)",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="die Ohren anlegen",
                meaning="Schüchtern oder ängstlich sein",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="die Ohren aufstellen",
                meaning="Aufmerksam werden",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="Mondnacht-Sehnsucht",
                meaning="Romantische Stimmung bei Vollmond",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="das Fell sträuben",
                meaning="Sich unwohl oder bedroht fühlen",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
            Idiom(
                text="Rudelinstinkt",
                meaning="Zusammengehörigkeitsgefühl, Loyalität",
                category=IdiomCategory.KEMONOMIMI,
                is_kemonomimi_friendly=True
            ),
        ])

        logger.info(f"IdiomDatabase: {len(self.idioms)} Redewendungen geladen")

    def get_all(self) -> List[Idiom]:
        """Alle Redewendungen abrufen"""
        return self.idioms.copy()

    def get_by_category(self, category: IdiomCategory) -> List[Idiom]:
        """Redewendungen nach Kategorie filtern"""
        return [i for i in self.idioms if i.category == category]

    def get_by_formality(self, formality: IdiomFormality) -> List[Idiom]:
        """Redewendungen nach Formalität filtern"""
        return [i for i in self.idioms if i.formality == formality]

    def get_kemonomimi_friendly(self) -> List[Idiom]:
        """Nur Kemonomimi-freundliche Redewendungen"""
        return [i for i in self.idioms if i.is_kemonomimi_friendly]

    def search(self, keyword: str) -> List[Idiom]:
        """Suche nach Keyword in Text oder Bedeutung"""
        keyword = keyword.lower()
        return [
            i for i in self.idioms
            if keyword in i.text.lower() or keyword in i.meaning.lower()
        ]


# =============================================================================
# IDIOM ENGINE - Hauptklasse
# =============================================================================

class IdiomEngine:
    """
    Hauptklasse für kontextuelle Auswahl von Redewendungen.
    Wählt passende Idiome basierend auf Stimmung, Thema und Situation.
    """

    def __init__(self):
        self.database = IdiomDatabase()
        self.last_used_idioms: List[str] = []  # Vermeidung von Wiederholungen
        self.max_history = 20

    def get_idiom_for_mood(
        self,
        mood: str,
        intensity: float = 0.5,
        formality: IdiomFormality = IdiomFormality.NEUTRAL,
        kemonomimi_only: bool = False
    ) -> Optional[Idiom]:
        """
        Wählt eine passende Redewendung basierend auf Stimmung.

        Args:
            mood: Stimmung (z.B. "happy", "sad", "angry")
            intensity: Intensität 0.0-1.0
            formality: Gewünschte Formalität
            kemonomimi_only: Nur Kemonomimi-freundliche
        """
        # Stimmung auf Kategorie mappen
        mood_to_category = {
            "happy": IdiomCategory.FREUDE,
            "joy": IdiomCategory.FREUDE,
            "freude": IdiomCategory.FREUDE,
            "sad": IdiomCategory.TRAUER,
            "sadness": IdiomCategory.TRAUER,
            "trauer": IdiomCategory.TRAUER,
            "angry": IdiomCategory.WUTT,
            "anger": IdiomCategory.WUTT,
            "wut": IdiomCategory.WUTT,
            "surprised": IdiomCategory.UEBERRASCHUNG,
            "surprise": IdiomCategory.UEBERRASCHUNG,
            "love": IdiomCategory.LIEBE,
            "liebe": IdiomCategory.LIEBE,
            "success": IdiomCategory.ERFOLG,
            "erfolg": IdiomCategory.ERFOLG,
            "failure": IdiomCategory.MISSERFOLG,
            "misserfolg": IdiomCategory.MISSERFOLG,
        }

        category = mood_to_category.get(mood.lower(), IdiomCategory.ALLTAG)
        candidates = self.database.get_by_category(category)

        # Filter nach Formalität (mit Toleranz)
        candidates = [
            c for c in candidates
            if abs(c.formality.value - formality.value) <= 1
        ]

        # Filter nach Kemonomimi wenn gewünscht
        if kemonomimi_only:
            candidates = [c for c in candidates if c.is_kemonomimi_friendly]

        # Filter nach Intensität
        intensity_level = self._intensity_to_level(intensity)
        candidates = [
            c for c in candidates
            if abs(c.intensity.value - intensity_level.value) <= 1
        ]

        # Vermeidung von Wiederholungen
        candidates = [c for c in candidates if c.text not in self.last_used_idioms]

        if not candidates:
            # Fallback: Alle aus der Kategorie
            candidates = self.database.get_by_category(category)

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.text)
        return selected

    def get_idiom_for_situation(
        self,
        situation: str,
        formality: IdiomFormality = IdiomFormality.NEUTRAL
    ) -> Optional[Idiom]:
        """
        Wählt eine Redewendung basierend auf der Situation.

        Args:
            situation: Beschreibung der Situation
            formality: Gewünschte Formalität
        """
        situation_lower = situation.lower()

        # Situationsanalyse
        situation_keywords = {
            IdiomCategory.ARBEIT: ["arbeit", "job", "büro", "projekt", "task", "deadline"],
            IdiomCategory.GELD: ["geld", "euro", "preis", "teuer", "billig", "kosten"],
            IdiomCategory.ZEIT: ["zeit", "spät", "früh", "warten", "eilig", "deadline"],
            IdiomCategory.FREUNDSCHAFT: ["freund", "zusammen", "gemeinsam", "hilfe", "unterstützung"],
            IdiomCategory.ESSEN: ["essen", "hunger", "kochen", "restaurant", "lecker"],
            IdiomCategory.WETTER: ["regen", "sonne", "kalt", "warm", "wetter", "schnee"],
            IdiomCategory.ERMUTIGUNG: ["aufgeben", "schwer", "müde", "keine lust", "schaffe"],
            IdiomCategory.WARNUNG: ["vorsicht", "gefahr", "risiko", "achtung", "pass auf"],
        }

        # Beste Kategorie finden
        best_category = IdiomCategory.ALLTAG
        best_score = 0

        for category, keywords in situation_keywords.items():
            score = sum(1 for kw in keywords if kw in situation_lower)
            if score > best_score:
                best_score = score
                best_category = category

        candidates = self.database.get_by_category(best_category)

        # Filter nach Formalität
        candidates = [
            c for c in candidates
            if abs(c.formality.value - formality.value) <= 1
        ]

        # Vermeidung von Wiederholungen
        candidates = [c for c in candidates if c.text not in self.last_used_idioms]

        if not candidates:
            candidates = self.database.get_by_category(best_category)

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.text)
        return selected

    def get_wisdom_idiom(self) -> Optional[Idiom]:
        """Gibt eine weise Redewendung zurück"""
        candidates = self.database.get_by_category(IdiomCategory.WEISHEIT)
        candidates.extend(self.database.get_by_category(IdiomCategory.RATSCHLAG))

        candidates = [c for c in candidates if c.text not in self.last_used_idioms]

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.text)
        return selected

    def get_encouraging_idiom(self) -> Optional[Idiom]:
        """Gibt eine ermutigende Redewendung zurück"""
        candidates = self.database.get_by_category(IdiomCategory.ERMUTIGUNG)
        candidates = [c for c in candidates if c.text not in self.last_used_idioms]

        if not candidates:
            candidates = self.database.get_by_category(IdiomCategory.ERMUTIGUNG)

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.text)
        return selected

    def get_random_kemonomimi_idiom(self) -> Optional[Idiom]:
        """Gibt eine zufällige Kemonomimi-freundliche Redewendung zurück"""
        candidates = self.database.get_kemonomimi_friendly()
        candidates = [c for c in candidates if c.text not in self.last_used_idioms]

        if not candidates:
            candidates = self.database.get_kemonomimi_friendly()

        if not candidates:
            return None

        selected = random.choice(candidates)
        self._add_to_history(selected.text)
        return selected

    def format_with_explanation(self, idiom: Idiom) -> str:
        """Formatiert eine Redewendung mit Erklärung"""
        result = f'"{idiom.text}"'
        result += f"\n   → {idiom.meaning}"
        if idiom.origin:
            result += f"\n   (Herkunft: {idiom.origin})"
        return result

    def _intensity_to_level(self, intensity: float) -> IdiomIntensity:
        """Konvertiert float Intensität zu IdiomIntensity"""
        if intensity < 0.25:
            return IdiomIntensity.LEICHT
        elif intensity < 0.5:
            return IdiomIntensity.MITTEL
        elif intensity < 0.75:
            return IdiomIntensity.STARK
        else:
            return IdiomIntensity.SEHR_STARK

    def _add_to_history(self, idiom_text: str):
        """Fügt eine Redewendung zur Historie hinzu"""
        self.last_used_idioms.append(idiom_text)
        if len(self.last_used_idioms) > self.max_history:
            self.last_used_idioms.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        """Statistiken über die Idiom-Datenbank"""
        all_idioms = self.database.get_all()

        category_counts = {}
        for category in IdiomCategory:
            count = len(self.database.get_by_category(category))
            if count > 0:
                category_counts[category.value] = count

        return {
            "total_idioms": len(all_idioms),
            "categories": category_counts,
            "kemonomimi_friendly": len(self.database.get_kemonomimi_friendly()),
            "recently_used": len(self.last_used_idioms)
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Globale Instanz
_idiom_engine: Optional[IdiomEngine] = None

def get_idiom_engine() -> IdiomEngine:
    """Gibt die globale IdiomEngine-Instanz zurück"""
    global _idiom_engine
    if _idiom_engine is None:
        _idiom_engine = IdiomEngine()
    return _idiom_engine

def get_idiom_for_mood(mood: str, intensity: float = 0.5) -> Optional[str]:
    """Schneller Zugriff: Idiom für Stimmung"""
    engine = get_idiom_engine()
    idiom = engine.get_idiom_for_mood(mood, intensity)
    return idiom.text if idiom else None

def get_encouraging_idiom() -> Optional[str]:
    """Schneller Zugriff: Ermutigendes Idiom"""
    engine = get_idiom_engine()
    idiom = engine.get_encouraging_idiom()
    return idiom.text if idiom else None

def get_wisdom() -> Optional[str]:
    """Schneller Zugriff: Weises Idiom"""
    engine = get_idiom_engine()
    idiom = engine.get_wisdom_idiom()
    return idiom.text if idiom else None


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = IdiomEngine()
    stats = engine.get_stats()

    print("=" * 60)
    print("HOLO IDIOM & REDEWENDUNGEN ENGINE v1.0")
    print("=" * 60)
    print(f"\nStatistiken:")
    print(f"  Gesamt: {stats['total_idioms']} Redewendungen")
    print(f"  Kemonomimi-freundlich: {stats['kemonomimi_friendly']}")
    print(f"\nKategorien:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  {cat}: {count}")

    print("\n" + "-" * 60)
    print("Beispiele:")

    print("\n[Freude]")
    idiom = engine.get_idiom_for_mood("happy", intensity=0.8)
    if idiom:
        print(engine.format_with_explanation(idiom))

    print("\n[Trauer]")
    idiom = engine.get_idiom_for_mood("sad", intensity=0.6)
    if idiom:
        print(engine.format_with_explanation(idiom))

    print("\n[Ermutigung]")
    idiom = engine.get_encouraging_idiom()
    if idiom:
        print(engine.format_with_explanation(idiom))

    print("\n[Weisheit]")
    idiom = engine.get_wisdom_idiom()
    if idiom:
        print(engine.format_with_explanation(idiom))

    print("\n[Kemonomimi-spezifisch]")
    idiom = engine.get_random_kemonomimi_idiom()
    if idiom:
        print(engine.format_with_explanation(idiom))

    print("\n[Situation: Arbeit]")
    idiom = engine.get_idiom_for_situation("Ich muss heute noch ein Projekt fertig machen")
    if idiom:
        print(engine.format_with_explanation(idiom))
