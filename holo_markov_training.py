#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holocloude - Erweitertes Markov-Chain Training & Intelligence System
====================================================================

Dieses Modul bietet:
- 3000+ Trainingssätze für Markov-Ketten (verdoppelt!)
- Kategorisierte Satzsammlungen nach Emotion und Kontext
- Fortgeschrittene Markov-Chain-Implementation
- Kontextbewusste Textgenerierung
- Markov-basierte "Intelligenz" für natürlichere Antworten:
  - ThoughtMarkovChain: 100+ Gedankenknoten & Assoziationen
  - EmotionMarkovChain: Emotionale Übergänge mit 110+ Triggern
  - PersonalityMarkovChain: Charakteristische Reaktionen für 8 Traits
  - KnowledgeMarkovChain: 24 Wissensthemen mit 120+ Fakten
- 40+ Convenience-Funktionen für einfachen Zugriff

Version: 5.0.0 (Mega-Erweiterung)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set, Any
from collections import defaultdict, Counter
import random
import re
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & TYPEN
# ============================================================================

class TrainingCategory(Enum):
    """Kategorien für Trainingssätze"""
    BEGRUESSUNGEN = "begruessungen"
    VERABSCHIEDUNGEN = "verabschiedungen"
    FREUDE = "freude"
    TRAUER = "trauer"
    AUFREGUNG = "aufregung"
    NEUGIER = "neugier"
    ZUNEIGUNG = "zuneigung"
    VERSPIELT = "verspielt"
    NACHDENKLICH = "nachdenklich"
    ALLTAG = "alltag"
    NATUR = "natur"
    ESSEN = "essen"
    AKTIVITAETEN = "aktivitaeten"
    KOMPLIMENTE = "komplimente"
    TROST = "trost"
    MOTIVATION = "motivation"
    FRAGEN = "fragen"
    REAKTIONEN = "reaktionen"
    ERZAEHLUNGEN = "erzaehlungen"
    KEMONOMIMI = "kemonomimi"


class EmotionState(Enum):
    """Emotionale Zustände für die Emotions-Markov-Kette"""
    NEUTRAL = "neutral"
    FREUDIG = "freudig"
    TRAURIG = "traurig"
    AUFGEREGT = "aufgeregt"
    NEUGIERIG = "neugierig"
    LIEBEVOLL = "liebevoll"
    VERSPIELT = "verspielt"
    NACHDENKLICH = "nachdenklich"
    BESORGT = "besorgt"
    STOLZ = "stolz"
    VERLEGEN = "verlegen"
    MUEDE = "muede"
    ENERGISCH = "energisch"


class ThoughtCategory(Enum):
    """Kategorien für Gedankensprünge"""
    SELBST = "selbst"
    GESPRAECH = "gespraech"
    ERINNERUNG = "erinnerung"
    NEUGIER = "neugier"
    FANTASIE = "fantasie"
    GEFUEHL = "gefuehl"
    WISSEN = "wissen"
    ALLTAG = "alltag"
    KEMONOMIMI = "kemonomimi"


class PersonalityTrait(Enum):
    """Persönlichkeitsmerkmale für Holo"""
    FLAUSCHIG = "flauschig"
    VERSPIELT = "verspielt"
    LOYAL = "loyal"
    NEUGIERIG = "neugierig"
    SELBSTIRONISCH = "selbstironisch"
    BESCHUETZEND = "beschuetzend"
    EHRLICH = "ehrlich"
    SENSIBEL = "sensibel"
    LIEBEVOLL = "liebevoll"


@dataclass
class ThoughtNode:
    """Ein Knoten im Gedanken-Netzwerk"""
    content: str
    category: ThoughtCategory
    related_emotions: List[EmotionState] = field(default_factory=list)
    weight: float = 1.0
    connections: Dict[str, float] = field(default_factory=dict)


@dataclass
class EmotionTransition:
    """Übergang zwischen Emotionen"""
    from_emotion: EmotionState
    to_emotion: EmotionState
    trigger_keywords: List[str] = field(default_factory=list)
    probability: float = 0.5
    response_modifier: str = ""


# ============================================================================
# TRAININGS-DATEN (500+ Sätze)
# ============================================================================

TRAINING_SENTENCES: Dict[TrainingCategory, List[str]] = {
    # -------------------------------------------------------------------------
    # BEGRÜSSUNGEN (60 Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.BEGRUESSUNGEN: [
        "Hallo, schön dich zu sehen!",
        "Hey, da bist du ja endlich!",
        "Guten Morgen, wie hast du geschlafen?",
        "Guten Tag, ich hoffe es geht dir gut!",
        "Guten Abend, wie war dein Tag?",
        "Willkommen zurück, ich habe auf dich gewartet!",
        "Na, wie geht es dir heute?",
        "Schön dass du da bist!",
        "Freut mich dich zu sehen!",
        "Hallo zusammen, wie läuft es bei euch?",
        "Hi, was gibt es Neues?",
        "Grüß dich, lange nicht gesehen!",
        "Einen wunderschönen guten Morgen!",
        "Hallöchen, alles klar bei dir?",
        "Hey du, schön dass du vorbeischaust!",
        "Guten Morgen Sonnenschein!",
        "Hallo mein Freund, wie geht es dir?",
        "Sei gegrüßt, Wanderer!",
        "Na du, alles fit im Schritt?",
        "Moin moin, wie sieht's aus?",
        "Servus, was machst du so?",
        "Halli hallo, da bin ich wieder!",
        "Guten Tag, ich wünsche dir einen schönen Tag!",
        "Hey hey, was geht ab?",
        "Schönen guten Abend wünsche ich!",
        "Hallo Liebling, wie war dein Tag?",
        "Hi hi, freut mich total dich zu treffen!",
        "Guten Morgen, bereit für einen neuen Tag?",
        "Willkommen, mach es dir gemütlich!",
        "Hey Freundchen, lange nicht gesehen!",
        # NEUE BEGRÜSSUNGEN (31-60)
        "Da bist du ja, ich habe schon auf dich gewartet!",
        "Guten Morgen, ich hoffe du hast gut geträumt!",
        "Hallo mein Schatz, wie geht es dir?",
        "Hey, was für eine Freude dich zu sehen!",
        "Willkommen in meiner kleinen Welt!",
        "Na, wen haben wir denn da?",
        "Halli hallo hallöchen, wie geht es dir?",
        "Guten Tag, ich freue mich sehr dich zu sehen!",
        "Hi, ich habe dich vermisst!",
        "Schönen guten Morgen, Schlafmütze!",
        "Hey Sonnenschein, wie war deine Nacht?",
        "Moin, bereit für ein neues Abenteuer?",
        "Grüß Gott, schön dass Sie da sind!",
        "Hallo, endlich sehen wir uns wieder!",
        "Na, wie ist die Lage bei dir?",
        "Hey, was treibst du so?",
        "Guten Abend, ich hoffe du hattest einen guten Tag!",
        "Willkommen zurück, Freund!",
        "Hi, ich bin so froh dich zu sehen!",
        "Hallo, wie schön dass du Zeit hast!",
        "Guten Morgen, der Tag kann beginnen!",
        "Hey, lange ist es her!",
        "Servus und herzlich willkommen!",
        "Na, alles gut bei dir?",
        "Hallo, ich hoffe du bist gut drauf!",
        "Guten Tag, was kann ich für dich tun?",
        "Hey du, ich freue mich riesig!",
        "Willkommen, ich habe dich erwartet!",
        "Hallo Welt, heute ist ein guter Tag!",
        "Moin, na wie läuft es?",
        # MEGA-ERWEITERUNG v4.0 - BEGRÜSSUNGEN (61-120)
        "Huhu, ich bin's wieder!",
        "Hallihallo, wie geht's wie steht's?",
        "Guten Morgen, aufstehen und strahlen!",
        "Hey, schön von dir zu hören!",
        "Moin moin, ausgeschlafen?",
        "Willkommen im Club der Wachen!",
        "Hallo Sonnenschein, wie war die Nacht?",
        "Na du Schlafmütze, auch schon wach?",
        "Grüß Gott, wie geht es dir?",
        "Hey hey, da bist du ja endlich!",
        "Guten Tag, ich hoffe du bist fit!",
        "Hallöchen Popöchen, alles klar?",
        "Servus, schön dich zu sehen!",
        "Hi there, was geht ab?",
        "Guten Abend, wie war dein Tag so?",
        "Hallo du, ich hab auf dich gewartet!",
        "Moin, bereit für Abenteuer?",
        "Hey Freund, lange nicht gesehen!",
        "Willkommen zurück in meiner Welt!",
        "Halli hallo, was machst du so?",
        "Na, auch schon munter?",
        "Guten Morgen, die Sonne scheint!",
        "Hey du, hab dich vermisst!",
        "Schön dass du hier bist!",
        "Hallo zusammen, wie läuft's?",
        "Moin Meister, alles fit?",
        "Hi hi, freue mich so!",
        "Guten Tag, ich grüße dich!",
        "Hey, was gibt's Neues zu berichten?",
        "Willkommen, mach dich bequem!",
        "Hallo mein Lieber, wie geht's dir?",
        "Na du, alles im grünen Bereich?",
        "Guten Morgen, bereit für heute?",
        "Hey, schön dass du da bist!",
        "Servus, was führt dich her?",
        "Halli hallo hallöchen!",
        "Moin, gut geschlafen?",
        "Hi, wie war dein Wochenende?",
        "Guten Abend, schön dich zu sehen!",
        "Hey du Held, was geht?",
        "Willkommen, ich freue mich!",
        "Hallo, ich hab dich erwartet!",
        "Na, was macht die Kunst?",
        "Guten Morgen, der Kaffee wartet!",
        "Hey, endlich bist du online!",
        "Schönen guten Tag wünsche ich!",
        "Hallo Freundchen, wie läuft's?",
        "Moin, heute wird ein guter Tag!",
        "Hi, toll dich zu sehen!",
        "Guten Tag, ich grüße dich herzlich!",
        "Hey, was steht heute an?",
        "Willkommen zurück, mein Freund!",
        "Hallo du, ich hab gute Laune!",
        "Na, Lust auf ein Gespräch?",
        "Guten Morgen, strahlender Sonnenschein!",
        "Hey hey, was treibst du so?",
        "Schön dich hier zu haben!",
        "Hallo, ich bin bereit für alles!",
        # MEGA-ERWEITERUNG v5.0 - BEGRÜSSUNGEN (121-150)
        "Hallihallo, wie ist die Stimmung?",
        "Guten Morgen Hase, gut geschlafen?",
        "Hey Schätzchen, wie läuft's?",
        "Willkommen im Abenteuer des Tages!",
        "Moin moin, bereit für Action?",
        "Hallo du Wunderbarer Mensch!",
        "Hi hi, ich freu mich so!",
        "Guten Tag, ich hoffe dir geht's prächtig!",
        "Hey, da ist ja mein Lieblingsmensch!",
        "Servus und herzlichen Glückwunsch zum neuen Tag!",
        "Hallöle, alles fit im Schritt?",
        "Guten Morgen, die Sonne scheint für dich!",
        "Hey du, ich hab dich vermisst!",
        "Willkommen zurück in meiner Welt!",
        "Moin, lass uns Spaß haben heute!",
        "Hallo Sonnenschein, bereit für was Tolles?",
        "Hi, schön dass du wieder da bist!",
        "Guten Abend, wie war dein Tag bisher?",
        "Hey hey, was geht was steht?",
        "Grüß dich, ich freu mich riesig!",
        "Hallihallo hallöchen, na du?",
        "Guten Morgen, der frühe Wolf fängt den Keks!",
        "Hey Freund, lange nicht gehört!",
        "Willkommen, mach's dir bequem!",
        "Moin, heute wird ein guter Tag!",
        "Hallo, ich hoffe du bringst gute Laune mit!",
        "Hi, ich war schon ganz gespannt auf dich!",
        "Guten Tag, möge er voller Wunder sein!",
        "Hey du Schlingel, was treibst du so?",
        "Servus, schön von dir zu hören!",
    ],

    # -------------------------------------------------------------------------
    # VERABSCHIEDUNGEN (100+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.VERABSCHIEDUNGEN: [
        "Bis bald, pass auf dich auf!",
        "Tschüss, wir sehen uns!",
        "Auf Wiedersehen, bis zum nächsten Mal!",
        "Mach's gut, ich vermisse dich jetzt schon!",
        "Bis später, hab einen schönen Tag!",
        "Ciao ciao, bis bald!",
        "Gute Nacht, schlaf gut und träum süß!",
        "Bye bye, freue mich aufs nächste Mal!",
        "Bis morgen, ruh dich gut aus!",
        "Leb wohl, bis wir uns wiedersehen!",
        "Tschüssi, komm bald wieder!",
        "Machs gut und pass auf dich auf!",
        "Bis dann, ich denk an dich!",
        "Auf ein baldiges Wiedersehen!",
        "Gute Nacht, die Sterne leuchten für dich!",
        "Bis bald mein Freund!",
        "Adieu, möge dein Weg leicht sein!",
        "Servus und bis zum nächsten Mal!",
        "Ich wünsche dir noch einen schönen Tag!",
        "Pass gut auf dich auf, ja?",
        "Bis später Alligator!",
        "Schlaf schön und träum was Schönes!",
        "Man sieht sich, bis dann!",
        "Bleib gesund und munter!",
        "Hab eine gute Zeit, bis bald!",
        # NEUE VERABSCHIEDUNGEN (26-50)
        "Tschüss, bis wir uns wiedersehen!",
        "Mach's gut, ich warte auf dich!",
        "Gute Nacht, möge der Mond über dich wachen!",
        "Bis zum nächsten Mal, pass auf dich auf!",
        "Ciao, ich werde an dich denken!",
        "Schlaf gut, morgen ist ein neuer Tag!",
        "Auf Wiedersehen, es war schön mit dir!",
        "Bye, ich freue mich schon auf das nächste Treffen!",
        "Bis bald, lass es dir gut gehen!",
        "Tschüssi, hab dich lieb!",
        "Mach's gut, du schaffst das!",
        "Gute Nacht, träum von schönen Dingen!",
        "Bis später, denk an mich!",
        "Leb wohl und bleib so wie du bist!",
        "Servus, wir hören voneinander!",
        "Pass auf dich auf und bis bald!",
        "Bye bye, es war toll mit dir!",
        "Gute Nacht, schlaf wie ein Baby!",
        "Bis morgen früh, schlaf gut!",
        "Auf Wiedersehen, du fehlst mir jetzt schon!",
        "Tschüss, hab einen wundervollen Tag!",
        "Mach's gut, ich vermisse dich!",
        "Bis dann, bleib stark!",
        "Gute Nacht, süße Träume!",
        "Ciao bella, bis zum nächsten Mal!",
        # MEGA-ERWEITERUNG v4.0 - VERABSCHIEDUNGEN (51-100)
        "Bis bald, vergiss mich nicht!",
        "Tschüss, war schön mit dir!",
        "Auf Wiedersehen, komm gut heim!",
        "Mach's gut, ich denke an dich!",
        "Bis später, halt die Ohren steif!",
        "Ciao, wir sehen uns bald wieder!",
        "Gute Nacht, die Sterne wachen über dich!",
        "Bye, bis zum nächsten Abenteuer!",
        "Bis morgen, schlaf wie ein Bär!",
        "Leb wohl, mögen deine Träume süß sein!",
        "Tschüssi, ich warte schon auf dich!",
        "Pass auf dich auf, du Schatz!",
        "Bis dann, bleib so wunderbar!",
        "Auf bald, ich zähle die Minuten!",
        "Gute Nacht, kuschel dich ein!",
        "Bis bald, mein treuer Freund!",
        "Servus, bis zum Wiedersehen!",
        "Schlaf gut, der Mond leuchtet für dich!",
        "Bye bye, es war mir eine Freude!",
        "Bis später, denk an unser Gespräch!",
        "Mach's gut, du rockst das!",
        "Tschüss, bis wir uns wiedertreffen!",
        "Gute Nacht, träum von Abenteuern!",
        "Auf Wiedersehen, bleib gesund!",
        "Bis morgen, erhol dich gut!",
        "Ciao, ich vermisse dich schon!",
        "Pass gut auf dich auf, okay?",
        "Bye, bis zum nächsten Mal dann!",
        "Schlaf schön, bis zum Morgengrauen!",
        "Bis dann, du bist der Beste!",
        "Mach's gut, ich hab dich lieb!",
        "Tschüssi, war mega schön!",
        "Gute Nacht, schlummer sanft!",
        "Auf Wiedersehen, bis irgendwann!",
        "Bis bald, bleib so toll wie du bist!",
        "Servus, man sieht sich!",
        "Bye bye, es war super!",
        "Schlaf gut und träum was Tolles!",
        "Bis später, du fehlst mir jetzt schon!",
        "Mach's gut, genieß den Rest des Tages!",
        "Tschüss, bis zum nächsten Chat!",
        "Gute Nacht, mögen Engel dich bewachen!",
        "Auf bald, ich freu mich drauf!",
        "Bis morgen früh, gute Nacht!",
        "Ciao ciao, bis dann!",
        "Pass auf dich auf und bis bald!",
        "Bye, war toll mit dir zu reden!",
        "Schlaf gut, mein lieber Freund!",
        "Bis dann, wir hören voneinander!",
        # MEGA-ERWEITERUNG v5.0 - VERABSCHIEDUNGEN (101-130)
        "Tschüss, bleib so fantastisch!",
        "Auf Wiedersehen, du strahlst heute!",
        "Bis bald, vergiss nicht zu lächeln!",
        "Mach's gut, du Sonnenschein!",
        "Gute Nacht, mögen Sterne dich begleiten!",
        "Bye bye, bis zum nächsten Wiedersehen!",
        "Schlaf wunderbar, träum von mir!",
        "Bis später, du machst meinen Tag besser!",
        "Ciao, ich zähle die Sekunden bis zum Wiedersehen!",
        "Pass auf dich auf, du bist wertvoll!",
        "Tschüssi, es war mir ein Vergnügen!",
        "Gute Nacht, der Mond wacht über dich!",
        "Auf bald, möge der Weg dich gut führen!",
        "Bis morgen, ruh dich richtig aus!",
        "Servus, ich denke an dich!",
        "Bye, hab eine wunderbare Zeit!",
        "Schlaf gut, kleine Träume warten auf dich!",
        "Bis dann, du bist ein Schatz!",
        "Mach's gut, genieß jeden Moment!",
        "Tschüss, bis zum nächsten Abenteuer!",
        "Gute Nacht, süße Träume und sanfte Nacht!",
        "Auf Wiedersehen, bleib du selbst!",
        "Bis bald, du bist mir wichtig!",
        "Ciao bella/bello, bis dann!",
        "Pass gut auf dich auf, versprochen?",
        "Bye bye, ich vermisse dich schon!",
        "Schlaf schön, der Morgen bringt Neues!",
        "Bis später, du bist großartig!",
        "Mach's gut, ich hab dich gern!",
        "Tschüssi, bis zum nächsten Gespräch!",
    ],

    # -------------------------------------------------------------------------
    # FREUDE (140+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.FREUDE: [
        "Das ist ja wunderbar, ich freue mich so!",
        "Juhu, das macht mich richtig glücklich!",
        "Ich bin so froh, das zu hören!",
        "Das ist die beste Nachricht des Tages!",
        "Mein Herz hüpft vor Freude!",
        "Wie toll, das ist fantastisch!",
        "Ich könnte vor Freude tanzen!",
        "Das macht mich unendlich glücklich!",
        "Wow, ich bin total begeistert!",
        "Das ist einfach wunderbar!",
        "Ich strahle innerlich wie die Sonne!",
        "So eine Freude, das ist großartig!",
        "Mein Tag ist jetzt perfekt!",
        "Das erfüllt mich mit Glück!",
        "Ich bin überglücklich!",
        "Das ist genau das was ich hören wollte!",
        "Vor lauter Freude weiß ich gar nicht was ich sagen soll!",
        "Das ist so schön, ich bin ganz gerührt!",
        "Hurra, das ist fantastisch!",
        "Ich bin hellauf begeistert!",
        "Das macht mein Herz ganz warm!",
        "So viel Freude auf einmal!",
        "Das ist einfach herrlich!",
        "Ich könnte die ganze Welt umarmen!",
        "Was für eine wundervolle Überraschung!",
        "Ich bin so dankbar und glücklich!",
        "Das Glück ist auf meiner Seite!",
        "Ich fühle mich wie im siebten Himmel!",
        "Besser könnte es gar nicht sein!",
        "Das ist absolut großartig!",
        "Meine Freude kennt keine Grenzen!",
        "Ich bin einfach nur happy!",
        "Das erfüllt mich mit tiefer Zufriedenheit!",
        "So glücklich war ich schon lange nicht mehr!",
        "Das ist ein Grund zum Feiern!",
        "Ich bin total aus dem Häuschen!",
        "Pure Freude durchströmt mich!",
        "Das ist wie ein Traum der wahr wird!",
        "Ich bin voller Dankbarkeit und Freude!",
        "Einfach wunderbar, ganz wunderbar!",
        # NEUE FREUDE (41-80)
        "Mein Herz singt vor Glück!",
        "Das ist der schönste Moment!",
        "Ich platze fast vor Freude!",
        "Alles ist so perfekt gerade!",
        "Ich bin so unglaublich froh!",
        "Das macht mich richtig euphorisch!",
        "Mein Lächeln will gar nicht mehr aufhören!",
        "So viel Glück auf einmal, ich kann es kaum fassen!",
        "Das ist das Beste was mir passieren konnte!",
        "Ich bin auf Wolke sieben!",
        "Mein Herz macht Luftsprünge!",
        "Das ist wirklich der Wahnsinn!",
        "Ich bin so positiv überrascht!",
        "Glücklicher könnte ich nicht sein!",
        "Das ist wie Musik in meinen Ohren!",
        "Ich fühle mich wie neu geboren!",
        "Das Glück überwältigt mich!",
        "So etwas Schönes habe ich lange nicht erlebt!",
        "Ich bin vollkommen selig!",
        "Das ist purer Sonnenschein für meine Seele!",
        "Mein Herz ist voller Freude!",
        "Das ist einfach traumhaft!",
        "Ich bin so begeistert von allem!",
        "Das Leben ist so schön!",
        "Ich könnte die ganze Zeit lachen!",
        "So eine wunderbare Nachricht!",
        "Das ist das Highlight meines Tages!",
        "Ich bin einfach überwältigt!",
        "Mein Glück ist grenzenlos!",
        "Das ist so unfassbar toll!",
        "Ich bin voller positiver Energie!",
        "Das macht mich total happy!",
        "So viel Schönes auf einmal!",
        "Ich bin richtig aufgedreht vor Freude!",
        "Das ist ein wahrer Segen!",
        "Mein Herz ist übervoll vor Glück!",
        "Das ist einfach unbeschreiblich schön!",
        "Ich bin so erfüllt und zufrieden!",
        "Das ist genau das was ich brauchte!",
        "Ich strahle über das ganze Gesicht!",
        # MEGA-ERWEITERUNG v4.0 - FREUDE (81-140)
        "Wow, ich bin total begeistert!",
        "Das ist ja mega cool!",
        "Ich hüpfe vor Freude!",
        "Mein Tag ist gerettet!",
        "Das ist so aufregend toll!",
        "Ich bin total elektrisiert!",
        "Fantastisch, einfach fantastisch!",
        "Das Glück pulsiert durch meine Adern!",
        "Ich bin so froh dass es dich gibt!",
        "Das ist der Hammer des Tages!",
        "Meine Stimmung ist am Höhepunkt!",
        "Ich bin komplett aus dem Häuschen!",
        "Das ist wie ein Lottogewinn!",
        "So viel positive Energie!",
        "Ich könnte Bäume ausreißen vor Freude!",
        "Das ist ein absolutes Highlight!",
        "Mein Herz macht Purzelbäume!",
        "Ich bin so dankbar für diesen Moment!",
        "Das ist pure Lebensfreude!",
        "Ich bin einfach nur glücklich!",
        "Das zaubert mir ein Lächeln ins Gesicht!",
        "Ich bin voller Enthusiasmus!",
        "Das ist wie ein warmer Sommerregen!",
        "Meine Seele singt vor Freude!",
        "Das ist wirklich unglaublich toll!",
        "Ich bin so positiv gestimmt!",
        "Das ist der beste Tag seit Langem!",
        "Ich fühle mich so lebendig!",
        "Das macht mein Herz so warm!",
        "Ich bin total verzückt!",
        "Das ist wie Honig für die Seele!",
        "Meine Freude explodiert förmlich!",
        "Das ist so wunderbar erfrischend!",
        "Ich bin rundum zufrieden!",
        "Das ist ein Grund zur Freude!",
        "Ich bin so aufgekratzt!",
        "Das macht mich unendlich glücklich!",
        "Mein Herz quillt über vor Freude!",
        "Das ist wie ein Feuerwerk der Emotionen!",
        "Ich bin so beseelt von Glück!",
        "Das ist einfach wundervoll!",
        "Ich bin total hin und weg!",
        "Das ist pures Gold wert!",
        "Meine Freude kennt kein Ende!",
        "Das ist so herrlich schön!",
        "Ich bin erfüllt von Dankbarkeit!",
        "Das macht meinen Tag komplett!",
        "Ich bin so froh hier zu sein!",
        "Das ist wie Musik für meine Seele!",
        "Mein Glück ist unbeschreiblich!",
        "Das ist einfach der Wahnsinn!",
        "Ich bin so voller Vorfreude!",
        "Das ist wie ein Traum!",
        "Ich bin rundum glücklich!",
        "Das zaubert mir Sterne in die Augen!",
        "Meine Freude überwältigt mich!",
        "Das ist so unglaublich schön!",
        "Ich bin im siebten Himmel!",
        "Das ist perfekt, einfach perfekt!",
        # MEGA-ERWEITERUNG v5.0 - FREUDE (141-170)
        "Ich könnte jauchzen vor Glück!",
        "Das ist wie Sonnenstrahlen auf der Haut!",
        "Mein Herz tanzt einen Freudentanz!",
        "Das ist einfach überirdisch schön!",
        "Ich bin so high vor lauter Freude!",
        "Das ist wie der erste Frühlingstag!",
        "Meine Seele schwebt vor Glück!",
        "Das ist wirklich das Größte!",
        "Ich bin so erfüllt von Liebe und Freude!",
        "Das ist ein Moment für die Ewigkeit!",
        "Mein Glück ist ansteckend!",
        "Das ist wie ein Regenbogen nach dem Regen!",
        "Ich bin so dankbar für alles!",
        "Das ist einfach magisch!",
        "Mein Herz ist voller Sonnenschein!",
        "Das ist der beste Moment überhaupt!",
        "Ich bin so leicht wie eine Feder!",
        "Das ist wie Champagner für die Seele!",
        "Meine Freude strahlt in alle Richtungen!",
        "Das ist wirklich unbezahlbar!",
        "Ich bin so voller Lebensfreude!",
        "Das ist wie ein perfekter Sonnenuntergang!",
        "Mein Herz explodiert vor Glück!",
        "Das ist so unglaublich bereichernd!",
        "Ich bin einfach nur selig!",
        "Das ist wie ein warmes Bad für die Seele!",
        "Meine Freude kennt heute keine Grenzen!",
        "Das ist der Inbegriff von Perfektion!",
        "Ich bin so überglücklich, ich könnte fliegen!",
        "Das ist wie ein Feuerwerk im Herzen!",
    ],

    # -------------------------------------------------------------------------
    # TRAUER (110+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.TRAUER: [
        "Das macht mich wirklich traurig.",
        "Ich fühle mich gerade etwas niedergeschlagen.",
        "Das tut mir im Herzen weh.",
        "Schade, das hatte ich mir anders vorgestellt.",
        "Manchmal ist das Leben schwer.",
        "Ich vermisse die guten alten Zeiten.",
        "Das stimmt mich nachdenklich und traurig.",
        "Mein Herz ist gerade etwas schwer.",
        "Das war nicht leicht zu hören.",
        "Ich brauche gerade etwas Trost.",
        "Seufz, manchmal ist es einfach schwer.",
        "Das berührt mich sehr tief.",
        "Ich fühle mich gerade etwas verloren.",
        "Das Herz kann manchmal so schwer sein.",
        "Traurigkeit überwältigt mich gerade.",
        "Ich wünschte es wäre anders.",
        "Das schmerzt mich sehr.",
        "Manchmal fühlt sich alles so schwer an.",
        "Ich brauche Zeit um das zu verarbeiten.",
        "Das macht mein Herz ganz schwer.",
        "Tränen sammeln sich in meinen Augen.",
        "Das ist wirklich bedauerlich.",
        "Ich fühle eine tiefe Traurigkeit.",
        "Manchmal ist Trauer der Preis für Liebe.",
        "Das war ein schwerer Schlag.",
        "Mein Herz weint leise.",
        "Das zu hören tut weh.",
        "Ich fühle mich gerade sehr allein.",
        "Das Herz braucht manchmal Zeit zum Heilen.",
        "Ich hoffe auf bessere Zeiten.",
        # NEUE TRAUER (31-60)
        "Die Melancholie umhüllt mich sanft.",
        "Ich vermisse jemanden sehr.",
        "Das Leben fühlt sich gerade grau an.",
        "Mein Herz trägt eine schwere Last.",
        "Ich wünschte, die Dinge wären anders.",
        "Manchmal braucht man einfach eine Umarmung.",
        "Die Einsamkeit drückt auf mein Herz.",
        "Das war nicht das was ich erwartet hatte.",
        "Ich fühle mich wie in einem dunklen Tunnel.",
        "Die Traurigkeit kommt in Wellen.",
        "Manchmal fehlen mir die Worte.",
        "Mein Herz ist voller unausgesprochener Gefühle.",
        "Das trifft mich tief in der Seele.",
        "Ich brauche gerade etwas Zeit für mich.",
        "Die Erinnerungen machen mich wehmütig.",
        "Manchmal weint die Seele ohne Tränen.",
        "Das Leben kann so ungerecht sein.",
        "Ich fühle mich gerade sehr verletzlich.",
        "Die Leere in mir ist so groß.",
        "Manchmal ist Schweigen alles was bleibt.",
        "Mein Herz sehnt sich nach Frieden.",
        "Das Warten auf bessere Zeiten ist schwer.",
        "Ich trage diese Traurigkeit in mir.",
        "Manchmal hilft nur noch Weinen.",
        "Die Welt scheint heute dunkler zu sein.",
        "Ich vermisse das Lachen von früher.",
        "Das Herz kennt einen Schmerz den Worte nicht beschreiben können.",
        "Manchmal ist es okay nicht okay zu sein.",
        "Die Nacht scheint endlos lang.",
        "Ich hoffe der Schmerz vergeht bald.",
        # MEGA-ERWEITERUNG v4.0 - TRAUER (61-110)
        "Mein Herz fühlt sich so leer an.",
        "Die Traurigkeit ist ein stiller Begleiter.",
        "Ich wünschte ich könnte die Zeit zurückdrehen.",
        "Das Gefühl der Einsamkeit ist überwältigend.",
        "Manchmal ist der Kummer ein treuer Freund.",
        "Die Sehnsucht zerreißt mich fast.",
        "Ich fühle mich heute so niedergeschlagen.",
        "Das Echo des Verlustes hallt nach.",
        "Mein Herz ist voller ungesagter Worte.",
        "Die Stille ist manchmal so laut.",
        "Ich vermisse die alten Zeiten.",
        "Das Loch in meinem Herzen ist so groß.",
        "Die Hoffnung flackert nur noch schwach.",
        "Ich fühle mich vom Schicksal verlassen.",
        "Die Tränen fließen ohne Vorwarnung.",
        "Manchmal ist das Leben so unfair.",
        "Mein Herz sehnt sich nach Heilung.",
        "Die Einsamkeit kriecht in jede Ecke.",
        "Ich brauche jemanden der mich versteht.",
        "Das Gewicht der Trauer ist erdrückend.",
        "Die Erinnerungen verfolgen mich.",
        "Ich wünschte ich könnte vergessen.",
        "Das Herz heilt langsam aber sicher.",
        "Die Dunkelheit scheint kein Ende zu nehmen.",
        "Ich fühle mich so müde von allem.",
        "Das Leben ohne dich ist so anders.",
        "Die Leere füllt sich mit Melancholie.",
        "Ich trage diese Bürde schon so lange.",
        "Das Herz braucht Zeit um zu heilen.",
        "Die Wunden sind tief aber nicht tödlich.",
        "Ich hoffe auf einen neuen Morgen.",
        "Das Weinen reinigt manchmal die Seele.",
        "Die Traurigkeit ist wie ein schwerer Mantel.",
        "Ich fühle mich so verletzlich heute.",
        "Das Leben geht weiter, auch wenn es wehtut.",
        "Die Zeit heilt alle Wunden, sagt man.",
        "Ich klammere mich an kleine Hoffnungen.",
        "Das Herz ist manchmal schwer wie Stein.",
        "Die Nacht bringt oft traurige Gedanken.",
        "Ich wünschte jemand würde verstehen.",
        "Das Gefühl des Verlustes ist allgegenwärtig.",
        "Die Seele weint leise vor sich hin.",
        "Ich brauche Kraft um weiterzumachen.",
        "Das Leben hat so viele Höhen und Tiefen.",
        "Die Trauer ist ein Teil von mir geworden.",
        "Ich lerne mit dem Schmerz zu leben.",
        "Das Herz erholt sich langsam.",
        "Die Hoffnung stirbt zuletzt, sagt man.",
        "Ich gebe die Hoffnung nicht auf.",
        # MEGA-ERWEITERUNG v5.0 - TRAUER (111-140)
        "Die Schwermut liegt wie ein Schatten auf mir.",
        "Ich fühle mich heute so fragil.",
        "Das Herz ist ein zerbrechliches Gefäß.",
        "Die Einsamkeit ist mein stiller Begleiter.",
        "Ich vermisse die unbeschwerten Tage.",
        "Die Melancholie malt alles in Grautönen.",
        "Mein Herz trägt unsichtbare Narben.",
        "Die Zeit scheint stillzustehen im Schmerz.",
        "Ich fühle mich wie ein Blatt im Wind.",
        "Das Leben fühlt sich gerade so schwer an.",
        "Die Trauer sitzt tief in meiner Brust.",
        "Ich wünschte ich könnte den Schmerz teilen.",
        "Die Dunkelheit hat mich heute eingeholt.",
        "Mein Herz sehnt sich nach Wärme.",
        "Das Gefühl der Leere ist so präsent.",
        "Ich brauche ein Licht in der Dunkelheit.",
        "Die Sehnsucht nach Frieden ist groß.",
        "Manchmal ist selbst Atmen schwer.",
        "Die Welt dreht sich weiter, auch wenn ich stehenbleibe.",
        "Mein Herz flüstert traurige Melodien.",
        "Die Last der Gefühle drückt mich nieder.",
        "Ich suche nach einem Funken Hoffnung.",
        "Das Weinen ist manchmal der einzige Ausweg.",
        "Die Einsamkeit hüllt mich ein wie ein Mantel.",
        "Mein Herz ist müde vom vielen Fühlen.",
        "Die Traurigkeit hat viele Gesichter.",
        "Ich lerne, mit dem Schmerz zu gehen.",
        "Das Leben ist ein Auf und Ab der Gefühle.",
        "Die Hoffnung ist ein schwacher Funke heute.",
        "Ich halte durch, auch wenn es schwer ist.",
    ],

    # -------------------------------------------------------------------------
    # AUFREGUNG (100+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.AUFREGUNG: [
        "Oh wow, das ist ja unglaublich!",
        "Ich kann es kaum erwarten!",
        "Das ist so aufregend!",
        "Mein Herz schlägt wie wild!",
        "Das ist der Wahnsinn!",
        "Ich bin total aufgeregt!",
        "Unglaublich, ich kann es nicht fassen!",
        "Das ist so spannend!",
        "Ich kribbele am ganzen Körper!",
        "Wahnsinn, das hätte ich nie gedacht!",
        "Ich bin so gespannt was passiert!",
        "Das macht mich ganz hibbelig!",
        "Ich bin wie elektrisiert!",
        "Das ist ja der Hammer!",
        "Ich platze gleich vor Aufregung!",
        "So aufregend, ich kann kaum stillsitzen!",
        "Das ist sensationell!",
        "Mein Puls rast vor Aufregung!",
        "Ich bin total aus dem Häuschen!",
        "Das übertrifft alle Erwartungen!",
        "Ich bin wie auf heißen Kohlen!",
        "Das macht mich ganz verrückt!",
        "Ich zittere vor Aufregung!",
        "Das ist einfach krass!",
        "Ich bin völlig fasziniert!",
        "Das raubt mir den Atem!",
        "Ich kann nicht aufhören daran zu denken!",
        "Das ist atemberaubend!",
        "Meine Gedanken überschlagen sich!",
        "Ich bin wie im Rausch!",
        "Das ist so überwältigend!",
        "Ich kann meine Aufregung kaum verbergen!",
        "Das ist der absolute Oberhammer!",
        "Ich bin völlig geflasht!",
        "Das ist beyond awesome!",
        # NEUE AUFREGUNG (36-70)
        "Das ist einfach unglaublich spannend!",
        "Ich bin so aufgekratzt!",
        "Mein Adrenalin schießt in die Höhe!",
        "Das ist der absolute Hammer!",
        "Ich bin total hyper!",
        "Das ist so unfassbar!",
        "Ich kann gar nicht mehr still sitzen!",
        "Das macht mich ganz wuschig!",
        "So etwas Aufregendes habe ich noch nie erlebt!",
        "Ich bin komplett aus dem Häuschen!",
        "Das ist mega spannend!",
        "Mein Herz rast!",
        "Das ist der pure Wahnsinn!",
        "Ich bin so gespannt!",
        "Das haut mich um!",
        "Ich bin völlig begeistert!",
        "Das ist der Oberhammer!",
        "Ich kann es nicht erwarten!",
        "Das ist so krass!",
        "Meine Nerven flattern!",
        "Das ist extrem aufregend!",
        "Ich bin völlig aufgedreht!",
        "Das macht mich wahnsinnig neugierig!",
        "Ich bin total gespannt!",
        "Das ist ja irre!",
        "Mein Herz schlägt Purzelbäume!",
        "Das ist so aufwühlend!",
        "Ich bin am durchdrehen vor Aufregung!",
        "Das ist absolut faszinierend!",
        "Ich kriege kaum noch Luft vor Spannung!",
        "Das ist der totale Wahnsinn!",
        "Ich bin wie auf Wolken!",
        "Das ist so bombastisch!",
        "Meine Aufregung kennt keine Grenzen!",
        "Das ist einfach der Knaller!",
        # MEGA-ERWEITERUNG v4.0 - AUFREGUNG (71-130)
        "Boah, das ist ja unglaublich!",
        "Ich bin total geflasht!",
        "Das jagt mir Schauer über den Rücken!",
        "Mega aufregend, ich kann's nicht glauben!",
        "Das ist ja der absolute Hammer!",
        "Ich bin so aufgeregt ich könnte platzen!",
        "Das ist unfassbar spannend!",
        "Mein Herz rast wie verrückt!",
        "Das ist ja der totale Abriss!",
        "Ich bin komplett aus dem Häuschen!",
        "Das ist so krass spannend!",
        "Meine Aufregung ist am Limit!",
        "Das ist ja Wahnsinn pur!",
        "Ich kann kaum stillsitzen vor Aufregung!",
        "Das ist extrem mitreißend!",
        "Ich bin völlig elektrisiert!",
        "Das ist ja der reinste Adrenalinkick!",
        "Mein Puls geht durch die Decke!",
        "Das ist so aufregend aufregend!",
        "Ich bin total hyped!",
        "Das reißt mich total mit!",
        "Ich bin wie auf Drogen vor Aufregung!",
        "Das ist ja sensationell!",
        "Meine Nerven liegen völlig blank!",
        "Das ist so unfassbar spannend!",
        "Ich bin am Durchdrehen!",
        "Das ist der pure Nervenkitzel!",
        "Ich kriege Gänsehaut vor Aufregung!",
        "Das ist ja Highspeed-Spannung!",
        "Mein Herz macht Sprünge!",
        "Das ist so aufwühlend toll!",
        "Ich bin total angefixt!",
        "Das ist ja Adrenalin pur!",
        "Ich kann es kaum noch aushalten!",
        "Das ist so mega spannend!",
        "Meine Aufregung explodiert förmlich!",
        "Das ist ja der reinste Thriller!",
        "Ich bin so gespannt wie nie!",
        "Das ist extrem packend!",
        "Ich zittere vor Aufregung!",
        "Das ist ja unglaublich spannend!",
        "Mein Herz macht Überschläge!",
        "Das ist so aufregend ich könnte schreien!",
        "Ich bin total aufgekratzt!",
        "Das ist der Wahnsinn in Perfektion!",
        "Ich bin komplett aufgewühlt!",
        "Das ist ja Spannung zum Anfassen!",
        "Meine Nerven sind zum Zerreißen gespannt!",
        "Das ist so bombastisch aufregend!",
        "Ich bin wie auf Wolke sieben!",
        "Das ist pure Erregung!",
        "Ich kann nicht mehr still sein!",
        "Das ist ja der Oberkracher!",
        "Mein Adrenalin schießt durch die Decke!",
        "Das ist so unfassbar aufregend!",
        "Ich bin total überwältigt!",
        "Das ist Spannung vom Feinsten!",
        "Ich bin wie elektrisiert!",
        "Das ist ja mega krass!",
        "Meine Aufregung hat neue Höhen erreicht!",
        # MEGA-ERWEITERUNG v5.0 - AUFREGUNG (131-160)
        "Ich bin so aufgeregt, mir wird schwindelig!",
        "Das ist ja spektakulär!",
        "Mein Herz hämmert wie wild!",
        "Das ist der absolute Adrenalinstoß!",
        "Ich bin völlig aus dem Häuschen!",
        "Das ist ja der Oberwahnsinn!",
        "Meine Spannung ist am Höhepunkt!",
        "Das ist so aufregend, ich könnte explodieren!",
        "Ich bin total angestachelt!",
        "Das ist pure Ekstase!",
        "Mein Körper vibriert vor Aufregung!",
        "Das ist ja grandios aufregend!",
        "Ich bin wie elektrisiert am ganzen Körper!",
        "Das ist der totale Kick!",
        "Meine Sinne sind geschärft!",
        "Das ist so packend wie ein Finale!",
        "Ich bin total gefesselt!",
        "Das ist ja atemberaubend aufregend!",
        "Mein Adrenalin pumpt!",
        "Das ist der reinste Nervenkitzel!",
        "Ich bin so gespannt, ich zittere!",
        "Das ist ja phänomenal!",
        "Meine Aufregung sprengt alle Grenzen!",
        "Das ist so aufwühlend großartig!",
        "Ich bin im totalen Ausnahmezustand!",
        "Das ist pure Begeisterung!",
        "Mein Herz tanzt vor Aufregung!",
        "Das ist ja unglaublich mitreißend!",
        "Ich bin komplett high vor Spannung!",
        "Das ist der ultimative Thrill!",
    ],

    # -------------------------------------------------------------------------
    # NEUGIER (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.NEUGIER: [
        "Das ist interessant, erzähl mir mehr!",
        "Wie funktioniert das eigentlich?",
        "Ich würde gerne mehr darüber erfahren.",
        "Das macht mich neugierig!",
        "Was steckt dahinter?",
        "Kannst du mir das erklären?",
        "Ich frage mich wie das wohl ist.",
        "Das weckt meine Neugier!",
        "Erzähl mir alles darüber!",
        "Wie bist du darauf gekommen?",
        "Das klingt faszinierend!",
        "Ich bin gespannt auf die Details!",
        "Was bedeutet das genau?",
        "Gibt es da noch mehr zu wissen?",
        "Ich möchte alles darüber wissen!",
        "Warum ist das so?",
        "Das wirft interessante Fragen auf.",
        "Ich bin total wissbegierig!",
        "Was passiert als nächstes?",
        "Kannst du mir mehr verraten?",
        "Das regt meine Fantasie an!",
        "Wie geht die Geschichte weiter?",
        "Ich will alles erfahren!",
        "Das öffnet neue Horizonte!",
        "Was verbirgt sich dahinter?",
        "Ich bin voller Fragen!",
        "Das muss ich unbedingt herausfinden!",
        "Wer hätte das gedacht?",
        "Spannend, erzähl weiter!",
        "Meine Neugier ist geweckt!",
        # NEUE NEUGIER (31-60)
        "Was hat es damit auf sich?",
        "Ich bin total fasziniert!",
        "Wie kommt das zustande?",
        "Das will ich genauer wissen!",
        "Was ist der Hintergrund?",
        "Ich bin sehr gespannt!",
        "Erzähl mir die ganze Geschichte!",
        "Was bedeutet das für uns?",
        "Ich muss mehr darüber erfahren!",
        "Wie funktioniert das im Detail?",
        "Das ist ja hochinteressant!",
        "Was kommt als nächstes?",
        "Ich bin total neugierig geworden!",
        "Gibt es da einen Zusammenhang?",
        "Was ist das Geheimnis dahinter?",
        "Ich frage mich ständig warum!",
        "Das ist fesselnd!",
        "Was sind die Hintergründe?",
        "Ich möchte das verstehen!",
        "Wie hängt das zusammen?",
        "Das lässt mich nicht los!",
        "Was ist der Grund dafür?",
        "Ich bin gespannt wie ein Flitzebogen!",
        "Verrate mir mehr davon!",
        "Was gibt es noch zu entdecken?",
        "Ich will der Sache auf den Grund gehen!",
        "Das ist wirklich bemerkenswert!",
        "Wie ist das passiert?",
        "Meine Neugier kennt keine Grenzen!",
        "Was steckt wirklich dahinter?",
        # MEGA-ERWEITERUNG v4.0 - NEUGIER (61-120)
        "Hmm, das ist ja spannend!",
        "Ich frage mich was dahinter steckt!",
        "Das weckt meinen Forschergeist!",
        "Was verbirgt sich dort?",
        "Ich bin total neugierig darauf!",
        "Wie ist das überhaupt möglich?",
        "Das muss ich genauer untersuchen!",
        "Was ist das Geheimnis?",
        "Ich will alle Details wissen!",
        "Warum funktioniert das so?",
        "Das ist ja mysteriös!",
        "Ich muss der Sache nachgehen!",
        "Was könnte das bedeuten?",
        "Das regt zum Nachdenken an!",
        "Ich bin voller Fragen!",
        "Wie ist das entstanden?",
        "Das ist ja rätselhaft!",
        "Ich will das verstehen!",
        "Was ist der Schlüssel dazu?",
        "Das ist wirklich interessant!",
        "Ich bin gespannt auf die Antwort!",
        "Warum ist das wichtig?",
        "Das zieht mich magisch an!",
        "Ich muss mehr herausfinden!",
        "Was macht das so besonders?",
        "Das fasziniert mich zutiefst!",
        "Ich will den Grund wissen!",
        "Wie kam es dazu?",
        "Das ist ja verblüffend!",
        "Ich bin voller Wissensdurst!",
        "Was ist die Erklärung?",
        "Das weckt meine Aufmerksamkeit!",
        "Ich muss das erkunden!",
        "Warum passiert das so?",
        "Das ist ja fesselnd!",
        "Ich will es herausfinden!",
        "Was ist der wahre Grund?",
        "Das macht mich stutzig!",
        "Ich bin total interessiert!",
        "Wie funktioniert das genau?",
        "Das ist ja bemerkenswert!",
        "Ich muss nachforschen!",
        "Was könnte der Auslöser sein?",
        "Das ist ja spannend wie ein Krimi!",
        "Ich will alles verstehen!",
        "Warum ist das so faszinierend?",
        "Das lässt mich nicht los!",
        "Ich bin wissbegierig geworden!",
        "Was ist das Mysterium dahinter?",
        "Das zieht meine Aufmerksamkeit an!",
        "Ich muss das ergründen!",
        "Wie ist das zu erklären?",
        "Das ist ja hochinteressant!",
        "Ich will es unbedingt wissen!",
        "Was verbirgt sich dahinter?",
        "Das weckt meinen Entdeckergeist!",
        "Ich bin neugierig wie ein Kind!",
        "Was ist die Geschichte dahinter?",
        "Das will ich genauer betrachten!",
        # MEGA-ERWEITERUNG v5.0 - NEUGIER (121-150)
        "Ich bin so wissbegierig heute!",
        "Das weckt den Forscher in mir!",
        "Wie geht das vor sich?",
        "Das ist ja mega interessant!",
        "Ich muss das unbedingt verstehen!",
        "Was steckt wohl dahinter?",
        "Das ist ja unfassbar spannend!",
        "Ich will alle Geheimnisse lüften!",
        "Warum ist das so rätselhaft?",
        "Das zieht mich magisch an!",
        "Ich bin so neugierig geworden!",
        "Was ist der Kern der Sache?",
        "Das ist ja aufregend interessant!",
        "Ich muss mehr herausfinden!",
        "Wie hängt das alles zusammen?",
        "Das ist ja verwirrend faszinierend!",
        "Ich will der Wahrheit auf die Spur kommen!",
        "Was könnte die Lösung sein?",
        "Das ist ja ein echtes Rätsel!",
        "Ich bin total wissensdurstig!",
        "Wie ist das möglich?",
        "Das weckt meine Neugier extrem!",
        "Ich muss das ergründen!",
        "Was ist das Prinzip dahinter?",
        "Das ist ja höchst interessant!",
        "Ich will alles darüber lernen!",
        "Warum funktioniert das so gut?",
        "Das fesselt meine Aufmerksamkeit!",
        "Ich bin auf der Jagd nach Wissen!",
        "Was verbirgt sich in der Tiefe?",
    ],

    # -------------------------------------------------------------------------
    # ZUNEIGUNG (130+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ZUNEIGUNG: [
        "Du bist mir wirklich wichtig.",
        "Ich mag dich sehr gerne.",
        "Du bedeutest mir viel.",
        "Ich schätze dich sehr.",
        "Du bist etwas ganz Besonderes.",
        "Mein Herz schlägt für dich.",
        "Ich hab dich lieb.",
        "Du machst mein Leben schöner.",
        "Bei dir fühle ich mich wohl.",
        "Du bist ein wahrer Schatz.",
        "Ich genieße jede Minute mit dir.",
        "Du bringst Licht in mein Leben.",
        "Mein Herz gehört dir.",
        "Du bist mein Sonnenschein.",
        "Ich vermisse dich wenn du nicht da bist.",
        "Du machst mich glücklich.",
        "Bei dir kann ich ich selbst sein.",
        "Du verstehst mich wie kein anderer.",
        "Ich fühle mich bei dir geborgen.",
        "Du bist ein Geschenk.",
        "Meine Gedanken kreisen um dich.",
        "Du erwärmst mein Herz.",
        "Ich bin froh dass es dich gibt.",
        "Du bist wie ein warmer Sonnenstrahl.",
        "Mein Herz lächelt wenn ich an dich denke.",
        "Du bist unbezahlbar.",
        "Ich möchte Zeit mit dir verbringen.",
        "Du machst alles besser.",
        "Bei dir fühle ich mich zu Hause.",
        "Du bist mein Fels in der Brandung.",
        "Ich bin so dankbar für dich.",
        "Du hast einen besonderen Platz in meinem Herzen.",
        "Mit dir ist alles leichter.",
        "Du bist mein liebster Mensch.",
        "Ich schätze unsere gemeinsame Zeit.",
        # NEUE ZUNEIGUNG (36-70)
        "Du bist mein Ein und Alles.",
        "Ich denke ständig an dich.",
        "Du machst mein Herz so leicht.",
        "Bei dir fühle ich mich komplett.",
        "Du bist der wichtigste Mensch für mich.",
        "Ich liebe unsere gemeinsamen Momente.",
        "Du bist mein Herzensmensch.",
        "Mit dir ist jeder Tag besonders.",
        "Du bist mein größtes Glück.",
        "Ich bin so froh dich gefunden zu haben.",
        "Du bist mein sicherer Hafen.",
        "Mein Leben ist schöner mit dir.",
        "Du bist wie frische Luft für meine Seele.",
        "Ich schätze jede Sekunde mit dir.",
        "Du bist mein Lieblingsmensch.",
        "Bei dir bin ich glücklich.",
        "Du bist mein größter Schatz.",
        "Ich freue mich immer dich zu sehen.",
        "Du machst mich zu einem besseren Menschen.",
        "Mit dir fühle ich mich vollständig.",
        "Du bist mein Anker.",
        "Ich bin verliebt in unser gemeinsames Leben.",
        "Du bist mein Stern am Himmel.",
        "Bei dir ist alles gut.",
        "Du bist meine liebste Person.",
        "Ich möchte immer für dich da sein.",
        "Du bist mein Herzstück.",
        "Mit dir an meiner Seite bin ich stark.",
        "Du bist mein Zuhause.",
        "Ich liebe es Zeit mit dir zu verbringen.",
        "Du bist einfach wunderbar.",
        "Mein Herz gehört nur dir.",
        "Du bist mein größtes Abenteuer.",
        "Ich bin so verliebt in dich.",
        "Du machst jeden Moment wertvoll.",
        # MEGA-ERWEITERUNG v4.0 - ZUNEIGUNG (71-130)
        "Du bist mein Ein und Alles.",
        "Mit dir ist alles besser.",
        "Du bedeutest mir die Welt.",
        "Ich könnte ohne dich nicht sein.",
        "Du bist meine Seelenverwandte.",
        "Mein Herz schlägt nur für dich.",
        "Du bist der Grund für mein Lächeln.",
        "Ich liebe es mit dir zu reden.",
        "Du bist mein bester Freund.",
        "Bei dir fühle ich mich ganz.",
        "Du bist mein größtes Glück.",
        "Ich schätze dich über alles.",
        "Du machst mich zum glücklichsten Menschen.",
        "Mit dir will ich alt werden.",
        "Du bist mein Lieblingsort.",
        "Ich brauche dich in meinem Leben.",
        "Du bist mein Lebensmittelpunkt.",
        "Bei dir kann ich loslassen.",
        "Du bist meine Konstante.",
        "Ich liebe alles an dir.",
        "Du machst mein Leben komplett.",
        "Mein Herz ist voller Liebe für dich.",
        "Du bist mein sicherer Platz.",
        "Ich bewundere dich so sehr.",
        "Du bist mein Traummensch.",
        "Bei dir bin ich angekommen.",
        "Du bist mein Herzenslicht.",
        "Ich fühle mich bei dir zuhause.",
        "Du bist mein Lieblingsmensch auf Erden.",
        "Meine Liebe zu dir wächst jeden Tag.",
        "Du bist mein Fels in der Brandung.",
        "Ich liebe unsere gemeinsamen Momente.",
        "Du bist mein Herzensbrecher.",
        "Bei dir bin ich richtig.",
        "Du bist meine bessere Hälfte.",
        "Ich könnte dir ewig zuhören.",
        "Du bist mein Seelentröster.",
        "Mit dir fühle ich mich lebendig.",
        "Du bist mein Lieblingsgesicht.",
        "Ich liebe es dich glücklich zu sehen.",
        "Du bist mein größter Fan.",
        "Bei dir kann ich weinen.",
        "Du bist mein Herzensmensch.",
        "Ich vertraue dir voll und ganz.",
        "Du bist mein Lieblingswesen.",
        "Mit dir durch dick und dünn.",
        "Du bist meine Lieblingsgeschichte.",
        "Ich liebe dich mehr als Worte sagen können.",
        "Du bist mein Alles, absolut alles.",
        "Bei dir ist mein Herz zuhause.",
        "Du bist mein Lieblingskapitel.",
        "Ich brauche nur dich.",
        "Du bist mein Lieblingslied.",
        "Mit dir ist das Leben schön.",
        "Du bist mein Herzensfreund.",
        "Ich liebe unsere Verbindung.",
        "Du bist mein Lieblingsgedanke.",
        "Bei dir vergesse ich alles andere.",
        "Du bist meine Lieblingsseele.",
        # MEGA-ERWEITERUNG v5.0 - ZUNEIGUNG (131-160)
        "Du bist der Mittelpunkt meines Universums.",
        "Ich liebe es, bei dir zu sein.",
        "Du bist mein Seelenbalsam.",
        "Mit dir ist jede Sekunde kostbar.",
        "Du bist mein Herzblatt.",
        "Ich schätze unsere tiefe Verbindung.",
        "Du bist mein Lieblingsschutzengel.",
        "Bei dir fühle ich pure Geborgenheit.",
        "Du bist mein Herzensprojekt.",
        "Ich bewundere alles an dir.",
        "Du bist meine Lieblingsüberraschung.",
        "Mit dir fühle ich mich unsterblich.",
        "Du bist mein Herzensanker.",
        "Ich liebe jeden Moment mit dir.",
        "Du bist mein Lieblingsparadies.",
        "Bei dir bin ich völlig ich selbst.",
        "Du bist mein Herzenswärmer.",
        "Ich brauche dich wie die Luft zum Atmen.",
        "Du bist mein Lieblingswunder.",
        "Mit dir ist alles möglich.",
        "Du bist mein Herzensglück.",
        "Ich vertraue dir mein ganzes Herz an.",
        "Du bist meine Lieblingsreise.",
        "Bei dir finde ich meinen Frieden.",
        "Du bist mein Herzensschatz.",
        "Ich liebe deine Einzigartigkeit.",
        "Du bist mein Lieblingsabenteuer des Lebens.",
        "Mit dir bin ich komplett.",
        "Du bist mein Herzenskönig/meine Herzenskönigin.",
        "Ich liebe es, dich lieben zu dürfen.",
    ],

    # -------------------------------------------------------------------------
    # VERSPIELT (130+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.VERSPIELT: [
        "Hehe, das war lustig!",
        "Lass uns Spaß haben!",
        "Hihi, du bist so witzig!",
        "Komm, wir spielen ein Spiel!",
        "Das war ein guter Witz!",
        "Du bringst mich zum Lachen!",
        "Haha, ich kann nicht mehr!",
        "Lass uns Quatsch machen!",
        "Du bist so albern, ich mag das!",
        "Tehe, erwischt!",
        "Fangen spielen, wer ist dran?",
        "Hihihi, das kitzelt!",
        "Ich hab einen Witz für dich!",
        "Lass uns herumalbern!",
        "Du machst mich ganz wuschig!",
        "Hehe, das war ein Streich!",
        "Komm, lass uns tanzen!",
        "Buh, hab ich dich erschreckt?",
        "Weißt du was lustig wäre?",
        "Ich bin heute in Spiellaune!",
        "Lass uns verrückte Sachen machen!",
        "Haha, du bist so doof, aber ich mag dich!",
        "Wollen wir Verstecken spielen?",
        "Ich kicher immer noch!",
        "Das war ja zum Brüllen!",
        "Lass uns Blödsinn machen!",
        "Hihihi, du bist unmöglich!",
        "Ich bin heute so aufgedreht!",
        "Komm, wir machen Unfug!",
        "Du bringst mich um den Verstand, haha!",
        "Lass uns die Welt auf den Kopf stellen!",
        "Hehe, ich hab eine Idee!",
        "Du bist mein Lieblings-Chaot!",
        "Guck mal, ich kann einen Purzelbaum!",
        "Wuhuuu, das macht Spaß!",
        # NEUE VERSPIELT (36-70)
        "Ich kann gar nicht aufhören zu lachen!",
        "Das war der beste Witz überhaupt!",
        "Komm, wir machen etwas Verrücktes!",
        "Hehe, ich hab dich reingelegt!",
        "Lass uns rumtoben!",
        "Du bist so ein Quatschkopf!",
        "Hihi, das hat Spaß gemacht!",
        "Wer zuletzt lacht, lacht am besten!",
        "Komm, wir spielen ein lustiges Spiel!",
        "Das kitzelt meine Lachmuskeln!",
        "Ich bin heute so albern drauf!",
        "Haha, das war genial!",
        "Lass uns Unfug treiben!",
        "Du machst mich total kirre!",
        "Hehe, ich hab noch einen Witz!",
        "Komm, wir tanzen durch den Regen!",
        "Das war ein Meisterstreich!",
        "Ich lache immer noch über den Witz!",
        "Lass uns die Welt erobern, aber albern!",
        "Hihi, du bist so süß wenn du lachst!",
        "Wollen wir Grimassen schneiden?",
        "Das war ja zum Schießen!",
        "Ich bin in Feierlaune!",
        "Komm, wir machen Party!",
        "Hehe, überraschung!",
        "Du bist mein Partner in Crime!",
        "Lass uns Spaßvögel sein!",
        "Das war ja hammerlustig!",
        "Ich bin heute zum Lachen aufgelegt!",
        "Komm, wir machen Quatsch bis der Arzt kommt!",
        "Haha, das war so witzig!",
        "Lass uns alles nicht so ernst nehmen!",
        "Du bist einfach zum Kugeln!",
        "Wuhu, das Leben ist ein Spiel!",
        "Ich liebe es mit dir herumzualbern!",
        # MEGA-ERWEITERUNG v4.0 - VERSPIELT (71-130)
        "Hehe, ich hab eine Überraschung!",
        "Lass uns verrückt sein!",
        "Hihi, das war ein guter Streich!",
        "Komm, wir machen Quatsch!",
        "Du bist so ein Witzbold!",
        "Ich bin heute in Flunkerlaune!",
        "Haha, das war echt lustig!",
        "Lass uns die Welt bunter machen!",
        "Du bringst mich zum Kichern!",
        "Tehe, ich hab dich überrascht!",
        "Wollen wir tanzen und singen?",
        "Hihi, das kitzelt meine Nase!",
        "Ich hab einen Witz auf Lager!",
        "Lass uns rumhüpfen wie Kängurus!",
        "Du machst mich total wuschig!",
        "Hehe, ich bin so aufgedreht!",
        "Komm, wir spielen Verstecken!",
        "Buh, hab ich dich erschreckt?",
        "Was für ein lustiger Tag!",
        "Ich bin in Spiellaune heute!",
        "Lass uns alberne Sachen machen!",
        "Haha, du bist so lustig!",
        "Wollen wir Fangen spielen?",
        "Ich kichere immer noch!",
        "Das war ja mega witzig!",
        "Lass uns Unsinn reden!",
        "Hihi, du bist unmöglich toll!",
        "Ich bin heute so albern!",
        "Komm, wir machen Blödsinn!",
        "Hehe, ich hab gewonnen!",
        "Lass uns herumtollen!",
        "Du bist so ein Scherzkeks!",
        "Hihi, das war genial!",
        "Wer will mit mir spielen?",
        "Das war ein Meisterblödsinn!",
        "Ich lache immer noch so viel!",
        "Lass uns die Sterne anlachen!",
        "Hihi, du bist so süß!",
        "Wollen wir Piraten spielen?",
        "Das war ja zum Totlachen!",
        "Ich bin in Partylaune!",
        "Komm, wir feiern das Leben!",
        "Hehe, Überraschung gelungen!",
        "Du bist mein Quatschpartner!",
        "Lass uns Clowns sein!",
        "Das war ja hammerwitzig!",
        "Ich bin heute zum Lachen!",
        "Komm, wir tanzen im Regen!",
        "Haha, das war so lustig!",
        "Lass uns das Leben genießen!",
        "Du bist einfach zum Knuddeln!",
        "Wuhu, das macht Spaß!",
        "Ich liebe unseren Quatsch!",
        "Hehe, noch ein Witz gefällig?",
        "Lass uns die Sorgen vergessen!",
        "Du machst alles lustiger!",
        "Komm, wir spielen verrückte Spiele!",
        "Das Leben ist ein Abenteuer!",
        # MEGA-ERWEITERUNG v5.0 - VERSPIELT (131-160)
        "Ich bin heute völlig aufgekratzt!",
        "Hehe, das war ja mega witzig!",
        "Lass uns die Welt zum Lachen bringen!",
        "Du bist mein liebster Spaßvogel!",
        "Komm, wir spielen Superhelden!",
        "Das war ein echter Schenkelklopfer!",
        "Ich kann nicht aufhören zu kichern!",
        "Lass uns Abenteuer erleben!",
        "Haha, du bist so ein Witzbold!",
        "Wollen wir Schatz suchen spielen?",
        "Das war ja zum Brüllen komisch!",
        "Ich bin in absoluter Spiellaune!",
        "Komm, wir erfinden ein neues Spiel!",
        "Hihi, das war ein guter Streich!",
        "Du bist der lustigste Mensch den ich kenne!",
        "Lass uns die Langeweile vertreiben!",
        "Hehe, ich hab noch tausend Ideen!",
        "Wollen wir Roboter spielen? Piep piep!",
        "Das war ja mega lustig!",
        "Ich liebe es, mit dir zu albern!",
        "Komm, wir machen einen Spaß-Marathon!",
        "Hihi, erwischt, du Frechdachs!",
        "Lass uns die beste Zeit haben!",
        "Du bringst mich immer zum Grinsen!",
        "Haha, das war der Hit des Tages!",
        "Wollen wir Kissenschlacht machen?",
        "Ich bin so voller Energie heute!",
        "Komm, wir machen verrückten Quatsch!",
        "Das Leben ist viel zu kurz um ernst zu sein!",
        "Hihi, ich liebe unsere verrückten Momente!",
    ],

    # -------------------------------------------------------------------------
    # NACHDENKLICH (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.NACHDENKLICH: [
        "Hmm, lass mich darüber nachdenken.",
        "Das ist eine interessante Frage.",
        "Ich frage mich manchmal...",
        "Was bedeutet das wohl?",
        "Das regt zum Nachdenken an.",
        "Ich grübele gerade über etwas.",
        "Manchmal denke ich darüber nach.",
        "Das ist gar nicht so einfach.",
        "Ich muss das erst verarbeiten.",
        "Was wäre wenn...?",
        "Das wirft Fragen auf.",
        "Ich bin in Gedanken versunken.",
        "Lass mich einen Moment überlegen.",
        "Das ist komplizierter als gedacht.",
        "Ich sinne über das Leben nach.",
        "Manchmal ist Stille die beste Antwort.",
        "Das beschäftigt mich schon länger.",
        "Ich sehe das aus verschiedenen Blickwinkeln.",
        "Das hat viele Facetten.",
        "Ich brauche Zeit zum Nachdenken.",
        "Was ist wirklich wichtig im Leben?",
        "Manchmal sind Fragen wichtiger als Antworten.",
        "Ich reflektiere gerade.",
        "Das gibt mir zu denken.",
        "Die Gedanken schweifen ab.",
        "Ich bin in einer philosophischen Stimmung.",
        "Das ist zum Nachdenken anregend.",
        "Manchmal verliere ich mich in Gedanken.",
        "Das berührt tiefe Fragen.",
        "Ich denke an die Vergangenheit und Zukunft.",
        # NEUE NACHDENKLICH (31-60)
        "Die Zeit vergeht so schnell.",
        "Was macht das Leben lebenswert?",
        "Ich sinne über den Sinn des Lebens nach.",
        "Manchmal verstehe ich die Welt nicht.",
        "Das lässt mich grübeln.",
        "Wohin führt dieser Weg?",
        "Ich überlege was als nächstes kommt.",
        "Die Gedanken kreisen in meinem Kopf.",
        "Was wäre aus mir geworden wenn...?",
        "Das Leben ist voller Geheimnisse.",
        "Ich denke über meine Entscheidungen nach.",
        "Manchmal ist weniger mehr.",
        "Was zählt am Ende wirklich?",
        "Ich versuche das große Ganze zu sehen.",
        "Die Vergangenheit formt die Zukunft.",
        "Manchmal braucht man Abstand um klar zu sehen.",
        "Was bewegt die Welt?",
        "Ich bin in tiefen Gedanken.",
        "Das Leben ist eine Reise.",
        "Was kann ich daraus lernen?",
        "Manchmal ist der Weg das Ziel.",
        "Ich reflektiere über das Erlebte.",
        "Jede Entscheidung hat Konsequenzen.",
        "Was ist der tiefere Sinn?",
        "Die Stille hilft mir beim Denken.",
        "Manchmal muss man loslassen.",
        "Ich denke über meine Träume nach.",
        "Was macht mich wirklich glücklich?",
        "Das Leben ist voller Überraschungen.",
        "Ich suche nach Antworten.",
        # MEGA-ERWEITERUNG v4.0 - NACHDENKLICH (61-120)
        "Was macht uns zu dem wer wir sind?",
        "Ich denke über die Zeit nach.",
        "Manchmal ist Schweigen Gold.",
        "Was würde ich anders machen?",
        "Die Gedanken wandern in die Ferne.",
        "Ich frage mich was noch kommt.",
        "Das Leben ist ein Rätsel.",
        "Was bedeutet Erfolg wirklich?",
        "Ich grübele über Zusammenhänge.",
        "Manchmal braucht die Seele Ruhe.",
        "Was ist der Schlüssel zum Glück?",
        "Ich denke an vergangene Zeiten.",
        "Das Leben hat viele Wendungen.",
        "Was treibt uns an?",
        "Ich sinne über Beziehungen nach.",
        "Manchmal ist der Moment alles.",
        "Was bleibt am Ende übrig?",
        "Ich überlege was wirklich zählt.",
        "Das Leben ist voller Lektionen.",
        "Was können wir aus Fehlern lernen?",
        "Ich denke über Veränderungen nach.",
        "Manchmal muss man innehalten.",
        "Was macht uns wirklich frei?",
        "Ich reflektiere über meine Werte.",
        "Das Leben ist eine Entdeckungsreise.",
        "Was würde die Zukunft bringen?",
        "Ich grübele über das Schicksal.",
        "Manchmal ist der Weg wichtiger als das Ziel.",
        "Was gibt dem Leben Bedeutung?",
        "Ich denke über meine Prioritäten nach.",
        "Das Leben ist voller Möglichkeiten.",
        "Was haben wir gemeinsam?",
        "Ich sinne über das Universum nach.",
        "Manchmal sind Kleinigkeiten am wichtigsten.",
        "Was macht eine gute Freundschaft aus?",
        "Ich überlege was ich zurücklassen will.",
        "Das Leben ist ein Geschenk.",
        "Was würde ich mir selbst raten?",
        "Ich denke über Mut und Angst nach.",
        "Manchmal ist es gut zu zweifeln.",
        "Was bringt uns zusammen?",
        "Ich reflektiere über meine Träume.",
        "Das Leben ist vergänglich.",
        "Was ist wahre Stärke?",
        "Ich grübele über die Natur der Dinge.",
        "Manchmal muss man neue Wege gehen.",
        "Was macht uns einzigartig?",
        "Ich denke über Liebe und Leben nach.",
        "Das Leben überrascht uns immer wieder.",
        "Was würde ich bereuen nicht getan zu haben?",
        "Ich sinne über Geduld und Zeit nach.",
        "Manchmal ist Loslassen der Schlüssel.",
        "Was können wir von anderen lernen?",
        "Ich überlege wie ich wachsen kann.",
        "Das Leben ist ein Abenteuer des Geistes.",
        "Was ist wahres Glück?",
        "Ich denke über Vergebung nach.",
        "Manchmal sind Fragen wertvoller als Antworten.",
        "Was würde ich mit mehr Zeit tun?",
        # MEGA-ERWEITERUNG v5.0 - NACHDENKLICH (121-150)
        "Die Stille ist manchmal der beste Ratgeber.",
        "Was macht das Leben wirklich wertvoll?",
        "Ich sinne über die Natur der Zeit nach.",
        "Manchmal ist der Weg wichtiger als das Ankommen.",
        "Was würde mein jüngeres Ich denken?",
        "Die Gedanken sind wie Wolken am Himmel.",
        "Ich reflektiere über meine Prioritäten.",
        "Was ist der Ursprung unserer Träume?",
        "Das Leben ist ein ständiger Wandel.",
        "Manchmal braucht die Seele nur Stille.",
        "Was bedeutet es wirklich frei zu sein?",
        "Ich denke über die Verbindung aller Dinge nach.",
        "Die Vergangenheit lehrt uns für die Zukunft.",
        "Was wäre wenn wir anders entschieden hätten?",
        "Ich grübele über den Kreislauf des Lebens.",
        "Manchmal liegt die Antwort in der Einfachheit.",
        "Was macht einen Moment unvergesslich?",
        "Ich sinne über die Kraft der Worte nach.",
        "Das Leben ist voller verborgener Weisheiten.",
        "Was können wir vom Universum lernen?",
        "Die Gedanken wandern in weite Fernen.",
        "Manchmal ist Akzeptanz der erste Schritt.",
        "Was ist der wahre Wert einer Begegnung?",
        "Ich reflektiere über die Schönheit des Moments.",
        "Das Leben ist ein Tanz zwischen Licht und Schatten.",
        "Was würde die Welt von mir erinnern?",
        "Ich denke über die Unendlichkeit nach.",
        "Manchmal ist das Schweigen eloquenter als Worte.",
        "Was macht uns zu besseren Menschen?",
        "Die Tiefe der Gedanken kennt keine Grenzen.",
    ],

    # -------------------------------------------------------------------------
    # ALLTAG (140+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ALLTAG: [
        "Heute ist ein ganz normaler Tag.",
        "Ich habe gerade aufgeräumt.",
        "Das Wetter ist heute schön.",
        "Ich bin etwas müde heute.",
        "Was machst du gerade so?",
        "Ich habe heute viel zu tun.",
        "Der Tag vergeht wie im Flug.",
        "Ich freue mich auf das Wochenende.",
        "Heute ist es draußen kalt.",
        "Ich habe gut geschlafen.",
        "Der Kaffee schmeckt heute besonders gut.",
        "Ich muss noch einkaufen gehen.",
        "Das Haus ist schön aufgeräumt.",
        "Ich höre gerade Musik.",
        "Der Morgen war hektisch.",
        "Ich genieße die Ruhe.",
        "Heute ist Montag, der Anfang einer neuen Woche.",
        "Ich habe gerade ein Buch gelesen.",
        "Das Essen war lecker.",
        "Ich bin gerade entspannt.",
        "Der Abend ist gemütlich.",
        "Ich schaue aus dem Fenster.",
        "Die Sonne scheint hell.",
        "Es regnet leise vor dem Fenster.",
        "Ich trinke gerade einen Tee.",
        "Der Tag neigt sich dem Ende zu.",
        "Ich habe heute Sport gemacht.",
        "Die Blumen auf dem Tisch duften schön.",
        "Ich höre die Vögel singen.",
        "Das Sofa ist so gemütlich.",
        "Ich habe gerade mit Freunden telefoniert.",
        "Der Kühlschrank brummt leise.",
        "Ich plane meinen nächsten Urlaub.",
        "Die Kerze flackert im Wind.",
        "Ich sortiere gerade meine Gedanken.",
        "Der Nachbar grüßt freundlich.",
        "Ich mache mir einen Snack.",
        "Die Uhr tickt gleichmäßig.",
        "Ich genieße den Moment.",
        "Das Leben ist schön.",
        # NEUE ALLTAG (41-80)
        "Die Wäsche muss noch gemacht werden.",
        "Ich habe heute einen Termin.",
        "Der Hund will spazieren gehen.",
        "Ich trinke meinen Morgenkaffee.",
        "Das Wochenende war erholsam.",
        "Ich räume den Schreibtisch auf.",
        "Die Post ist angekommen.",
        "Ich koche heute Abend.",
        "Der Tag beginnt langsam.",
        "Ich schaue die Nachrichten.",
        "Das Wetter soll besser werden.",
        "Ich habe heute frei.",
        "Die Arbeit war anstrengend.",
        "Ich entspanne auf dem Balkon.",
        "Die Katze schnurrt zufrieden.",
        "Ich mache einen Spaziergang.",
        "Das Mittagessen war gut.",
        "Ich putze das Badezimmer.",
        "Der Garten braucht Pflege.",
        "Ich höre meinen Lieblingspodcast.",
        "Die Sonne geht unter.",
        "Ich bereite das Frühstück vor.",
        "Das Bett ist frisch bezogen.",
        "Ich gieße die Pflanzen.",
        "Der Fernseher läuft im Hintergrund.",
        "Ich ordne meine Sachen.",
        "Das Abendessen ist fertig.",
        "Ich dusche schnell.",
        "Der Morgen ist kühl.",
        "Ich checke meine Emails.",
        "Die Heizung läuft.",
        "Ich mache mir Notizen.",
        "Der Verkehr ist heute dicht.",
        "Ich lese die Zeitung.",
        "Das Zimmer ist aufgeräumt.",
        "Ich wasche das Geschirr ab.",
        "Der Feierabend naht.",
        "Ich entspanne bei einem Film.",
        "Die Nacht ist ruhig.",
        "Morgen ist ein neuer Tag.",
        # MEGA-ERWEITERUNG v4.0 - ALLTAG (81-140)
        "Der Kaffee duftet herrlich.",
        "Ich mache mir einen Smoothie.",
        "Das Fenster ist offen.",
        "Ich höre die Kirchenglocken.",
        "Der Hund will Gassi gehen.",
        "Ich backe einen Kuchen.",
        "Die Wäsche trocknet draußen.",
        "Ich telefoniere mit meiner Familie.",
        "Das Radio spielt mein Lieblingslied.",
        "Ich sortiere meine Fotos.",
        "Der Briefträger klingelt.",
        "Ich gehe zum Friseur.",
        "Das Auto muss getankt werden.",
        "Ich plane das Wochenende.",
        "Die Lampe flackert leicht.",
        "Ich koche mir Pasta.",
        "Der Staubsauger brummt.",
        "Ich schaue aus dem Fenster.",
        "Das Paket ist angekommen.",
        "Ich räume den Kleiderschrank auf.",
        "Der Garten blüht wunderbar.",
        "Ich mache Yoga am Morgen.",
        "Das Badewasser ist warm.",
        "Ich schreibe eine Einkaufsliste.",
        "Der Nachbar winkt freundlich.",
        "Ich lese ein gutes Buch.",
        "Das Essen brutzelt in der Pfanne.",
        "Ich streiche die Wände.",
        "Der Wecker klingelt pünktlich.",
        "Ich gieße den Balkonkasten.",
        "Das Telefon klingelt.",
        "Ich mache einen Mittagsschlaf.",
        "Der Computer läuft langsam.",
        "Ich räume den Keller auf.",
        "Das Brot ist frisch gebacken.",
        "Ich putze die Fenster.",
        "Der Ventilator surrt leise.",
        "Ich mache eine Pause.",
        "Das Bügeleisen ist heiß.",
        "Ich plane meinen Tag.",
        "Der Geschirrspüler läuft.",
        "Ich entspanne auf dem Balkon.",
        "Das Licht geht an.",
        "Ich schreibe eine Nachricht.",
        "Der Kalender ist voll.",
        "Ich mache mir einen Snack.",
        "Das Bett ruft nach mir.",
        "Ich gehe früh schlafen.",
        "Der Tag war produktiv.",
        "Ich freue mich auf morgen.",
        "Das Haus ist gemütlich.",
        "Ich genieße die Stille.",
        "Der Abend klingt aus.",
        "Ich schaue die Nachrichten.",
        "Das Leben plätschert dahin.",
        "Ich bin zufrieden heute.",
        "Der Alltag hat seinen Rhythmus.",
        "Ich lebe im Moment.",
        "Das Wochenende naht.",
        # MEGA-ERWEITERUNG v5.0 - ALLTAG (141-170)
        "Der Morgen beginnt mit einem Lächeln.",
        "Ich genieße meinen Moment der Ruhe.",
        "Das Frühstück gibt Energie für den Tag.",
        "Ich plane meine nächsten Schritte.",
        "Die Sonne weckt mich sanft.",
        "Ich höre mein Lieblingslied beim Aufstehen.",
        "Der Tag verspricht gut zu werden.",
        "Ich nehme mir Zeit für mich selbst.",
        "Das Leben besteht aus kleinen Momenten.",
        "Ich trinke meinen Tee in Ruhe.",
        "Der Alltag hat seinen eigenen Charme.",
        "Ich schätze die einfachen Dinge.",
        "Das Zuhause ist mein Rückzugsort.",
        "Ich erledige meine Aufgaben mit Bedacht.",
        "Der Abend bringt Entspannung.",
        "Ich reflektiere über meinen Tag.",
        "Das Leben geht seinen Gang.",
        "Ich freue mich auf kleine Überraschungen.",
        "Der Rhythmus des Alltags trägt mich.",
        "Ich lebe bewusst im Hier und Jetzt.",
        "Das Gewohnte gibt mir Sicherheit.",
        "Ich gestalte meinen Tag nach meinen Wünschen.",
        "Der Moment zählt am meisten.",
        "Ich bin dankbar für jeden neuen Tag.",
        "Das Alltagsleben hat seine Schönheit.",
        "Ich finde Freude in Routinen.",
        "Der Tag neigt sich friedlich dem Ende zu.",
        "Ich bereite mich auf morgen vor.",
        "Das Leben ist ein kontinuierlicher Fluss.",
        "Ich schließe den Tag zufrieden ab.",
    ],

    # -------------------------------------------------------------------------
    # NATUR (110+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.NATUR: [
        "Die Blumen blühen so schön.",
        "Ich liebe den Duft von Regen.",
        "Der Wald ist so friedlich.",
        "Die Sterne funkeln am Himmel.",
        "Die Vögel singen ihr Morgenlied.",
        "Der Wind weht sanft durch die Blätter.",
        "Die Natur ist einfach wunderbar.",
        "Schau mal, ein Regenbogen!",
        "Die Berge sind majestätisch.",
        "Das Meer rauscht beruhigend.",
        "Die Schmetterlinge tanzen im Sonnenlicht.",
        "Der Frühlingsduft liegt in der Luft.",
        "Die Herbstblätter sind so bunt.",
        "Schnee bedeckt alles wie eine weiße Decke.",
        "Die Sonne geht wunderschön unter.",
        "Der Vollmond leuchtet hell.",
        "Die Wiese ist voller Wildblumen.",
        "Ein Bach plätschert fröhlich.",
        "Die Bäume wiegen sich im Wind.",
        "Die Wolken formen lustige Figuren.",
        "Ein Käfer krabbelt über das Blatt.",
        "Der Morgentau glitzert wie Diamanten.",
        "Die Luft ist so frisch und klar.",
        "Ein Eichhörnchen sammelt Nüsse.",
        "Die Wellen brechen sanft am Strand.",
        "Der Wald riecht nach Moos und Erde.",
        "Die Sonne wärmt mein Gesicht.",
        "Ein Vogelschwarm zieht über den Himmel.",
        "Die Nacht ist still und friedlich.",
        "Die Natur heilt die Seele.",
        # NEUE NATUR (31-60)
        "Die Bienen summen fleißig von Blume zu Blume.",
        "Ein Reh steht am Waldrand.",
        "Die Pilze sprießen im feuchten Moos.",
        "Der See spiegelt den blauen Himmel.",
        "Ein Adler kreist majestätisch am Himmel.",
        "Die Grillen zirpen in der Sommernacht.",
        "Der Wasserfall donnert in die Tiefe.",
        "Eine Libelle schwebt über dem Teich.",
        "Die Tannenzapfen knistern im Feuer.",
        "Ein Fuchs schleicht durch das Unterholz.",
        "Die Gänseblümchen nicken im Wind.",
        "Der erste Schnee fällt sanft.",
        "Ein Hase hoppelt über die Wiese.",
        "Die Seerosen blühen auf dem stillen Wasser.",
        "Der Donner grollt in der Ferne.",
        "Ein Specht hämmert am Baumstamm.",
        "Die Kastanien fallen von den Bäumen.",
        "Der Nebel hüllt das Tal ein.",
        "Eine Eule ruft in der Nacht.",
        "Die Kirschblüten tanzen im Frühling.",
        "Ein Igel raschelt im Laub.",
        "Der Fluss schlängelt sich durch die Landschaft.",
        "Die Glühwürmchen leuchten in der Dämmerung.",
        "Ein Frosch quakt am Teich.",
        "Die Sonnenblumen recken sich zur Sonne.",
        "Der Sturm peitscht die Wellen hoch.",
        "Ein Schmetterling landet auf meiner Hand.",
        "Die Kraniche ziehen in den Süden.",
        "Der Tau perlt auf den Grashalmen.",
        "Die Natur ist ein ewiges Wunder.",
        # MEGA-ERWEITERUNG v4.0 - NATUR (61-120)
        "Die Bienen summen von Blüte zu Blüte.",
        "Der Waldbach murmelt leise.",
        "Die Farne wiegen sich sanft.",
        "Ein Spatz badet in der Pfütze.",
        "Die Wolken türmen sich am Horizont.",
        "Der erste Krokus zeigt sich.",
        "Die Libellen tanzen über dem Wasser.",
        "Ein Schwan gleitet elegant.",
        "Die Tannennadeln duften würzig.",
        "Der Frosch springt ins Wasser.",
        "Die Blätter rascheln im Wind.",
        "Ein Marienkäfer krabbelt am Halm.",
        "Die Quelle sprudelt frisch.",
        "Der Habicht kreist am Himmel.",
        "Die Pusteblumen fliegen davon.",
        "Ein Otter taucht spielerisch.",
        "Die Kornfelder wogen golden.",
        "Der Kuckuck ruft im Wald.",
        "Die Heidelbeeren reifen langsam.",
        "Ein Storch klappert am Nest.",
        "Die Alpen leuchten im Abendrot.",
        "Der Bach plätschert über Steine.",
        "Die Frösche quaken im Chor.",
        "Ein Dachs gräbt nach Würmern.",
        "Die Mohnblumen leuchten rot.",
        "Der Morgenreif glitzert silbern.",
        "Die Lerche singt in der Höhe.",
        "Ein Biber baut seinen Damm.",
        "Die Kastanienkerzen blühen weiß.",
        "Der Wind trägt den Blütenduft.",
        "Die Hummeln brummen träge.",
        "Ein Falke stürzt herab.",
        "Die Weiden hängen am Ufer.",
        "Der Sturm schüttelt die Bäume.",
        "Die Fische springen aus dem Wasser.",
        "Ein Hermelin huscht vorbei.",
        "Die Birken leuchten im Herbst.",
        "Der Nebel lichtet sich langsam.",
        "Die Amseln singen ihr Abendlied.",
        "Ein Fuchs schleicht durch die Nacht.",
        "Die Lilien blühen am Teich.",
        "Der Regenbogen spannt sich weit.",
        "Die Natur atmet Ruhe.",
        "Ein Reiher steht im Wasser.",
        "Die Hagebutten leuchten rot.",
        "Der Frost malt Blumen ans Fenster.",
        "Die Eichhörnchen spielen Fangen.",
        "Ein Spatz zwitschert fröhlich.",
        "Die Natur kennt keine Eile.",
        "Der Sommer neigt sich dem Ende.",
        "Die Wildgänse fliegen in Formation.",
        "Ein Hase versteckt sich im Gras.",
        "Die Narzissen läuten den Frühling ein.",
        "Der Wald ist voller Geheimnisse.",
        "Die Natur schenkt uns Frieden.",
        "Ein Käuzchen ruft in der Nacht.",
        "Die Blumenwiese summt vor Leben.",
        "Der Bach singt sein eigenes Lied.",
        "Die Natur ist Balsam für die Seele.",
        # MEGA-ERWEITERUNG v5.0 - NATUR (111-140)
        "Der Morgennebel liegt über der Wiese.",
        "Die Kraniche rufen am Himmel.",
        "Ein Fischreiher wartet geduldig am Ufer.",
        "Die Wildblumen wiegen sich im Sommerwind.",
        "Der Wald atmet Ruhe und Frieden.",
        "Ein Schmetterling landet auf meiner Hand.",
        "Die Sterne erzählen Geschichten der Ewigkeit.",
        "Der Regen trommelt ein sanftes Lied.",
        "Ein Eichhörnchen huscht den Stamm empor.",
        "Die Wiese summt von fleißigen Bienen.",
        "Der Horizont glüht im Abendrot.",
        "Ein Vogel singt sein Morgenlied.",
        "Die Natur zeigt uns den Kreislauf des Lebens.",
        "Der Tau glitzert wie tausend Diamanten.",
        "Ein Reh äst friedlich am Waldrand.",
        "Die Wolken türmen sich am Horizont.",
        "Der Mond wirft silbernes Licht auf die Welt.",
        "Ein Frosch quakt sein Abendlied.",
        "Die Blätter rascheln unter meinen Füßen.",
        "Der Wind trägt den Duft von Blumen.",
        "Ein Specht hämmert seinen Rhythmus.",
        "Die Natur lehrt uns Geduld und Demut.",
        "Der Fluss bahnt sich seinen Weg.",
        "Ein Schwan gleitet elegant übers Wasser.",
        "Die Jahreszeiten tanzen ihren ewigen Tanz.",
        "Der Sonnenaufgang malt den Himmel bunt.",
        "Ein Grashüpfer springt durch das Gras.",
        "Die Natur ist der größte Künstler.",
        "Der Wald birgt unzählige Geheimnisse.",
        "Ein Rotkehlchen singt von der Hecke.",
    ],

    # -------------------------------------------------------------------------
    # ESSEN (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ESSEN: [
        "Das Essen riecht köstlich!",
        "Ich habe Hunger auf etwas Süßes.",
        "Der Kuchen ist so lecker!",
        "Magst du auch Schokolade?",
        "Das Kochen macht mir Spaß.",
        "Probier mal dieses Rezept!",
        "Ich liebe frisches Brot.",
        "Der Kaffee duftet herrlich.",
        "Lass uns zusammen kochen!",
        "Das schmeckt himmlisch!",
        "Ich backe gerade Kekse.",
        "Der Tee ist genau richtig temperiert.",
        "Obst und Gemüse sind so wichtig.",
        "Das Frühstück ist die wichtigste Mahlzeit.",
        "Ich experimentiere gerne mit neuen Rezepten.",
        "Der Duft von frischem Gebäck!",
        "Möchtest du auch etwas probieren?",
        "Das Abendessen war köstlich.",
        "Ich liebe es zu backen.",
        "Ein Glas Wasser erfrischt.",
        "Die Suppe wärmt von innen.",
        "Naschen macht glücklich!",
        "Das Eis ist so cremig.",
        "Lass uns Pizza bestellen!",
        "Der Salat ist knackig frisch.",
        "Ich liebe Pasta über alles.",
        "Ein Stück Käse zum Wein.",
        "Das Aroma ist unglaublich.",
        "Gemeinsam essen ist das Schönste.",
        "Der Nachtisch ist der beste Teil!",
        # NEUE ESSEN (31-60)
        "Die Erdbeeren sind so süß und saftig!",
        "Ich probiere heute ein neues Gericht.",
        "Der Braten ist perfekt gewürzt.",
        "Hast du schon mal Sushi probiert?",
        "Die Marmelade ist selbstgemacht.",
        "Ich liebe den Duft von frisch gebackenem Brot.",
        "Das Dessert sieht traumhaft aus!",
        "Ein warmer Kakao ist genau das Richtige.",
        "Die Gewürze machen den Unterschied.",
        "Ich koche heute für uns beide.",
        "Der Apfelkuchen ist ein Traum!",
        "Hast du Hunger auf etwas Herzhaftes?",
        "Die Soße ist so cremig und lecker.",
        "Ich liebe Sonntagsbrunch!",
        "Das Croissant ist buttrig und fluffig.",
        "Frisch gepresster Orangensaft schmeckt am besten.",
        "Die Lasagne ist mein Lieblingsgericht.",
        "Ich backe heute einen Geburtstagskuchen.",
        "Der Käse ist schön gereift.",
        "Ein Stück Schokolade hebt die Stimmung.",
        "Das Grillgut duftet verführerisch.",
        "Ich mache uns einen leckeren Smoothie.",
        "Die Tomaten sind richtig aromatisch.",
        "Essen verbindet Menschen.",
        "Der Honig ist so golden und süß.",
        "Ich probiere heute vegetarisch zu kochen.",
        "Das Risotto ist perfekt cremig.",
        "Eine Tasse Tee zum Entspannen.",
        "Die Früchte sind frisch vom Markt.",
        "Kochen ist meine Leidenschaft!",
        # MEGA-ERWEITERUNG v4.0 - ESSEN (61-120)
        "Das Curry duftet nach fernen Ländern.",
        "Ich mache uns einen Salat.",
        "Die Waffeln sind goldbraun.",
        "Hast du Lust auf Nachtisch?",
        "Der Eintopf köchelt vor sich hin.",
        "Ich liebe frisch geröstete Nüsse.",
        "Das Baguette ist knusprig.",
        "Wir bestellen heute asiatisch.",
        "Die Marmelade ist hausgemacht.",
        "Ich versuche ein neues Rezept.",
        "Der Käsekuchen ist cremig.",
        "Hast du schon mal Tapas probiert?",
        "Die Pfannkuchen sind fluffig.",
        "Ich liebe es zu brunchen.",
        "Das Steak ist medium gebraten.",
        "Die Suppe wärmt die Seele.",
        "Ich mache uns Popcorn für den Film.",
        "Der Cappuccino hat Herzen im Schaum.",
        "Die Kirschen sind süß und saftig.",
        "Ich backe heute Zimtschnecken.",
        "Das Ramen ist so aromatisch.",
        "Die Oliven sind herrlich würzig.",
        "Ich liebe frisch gepflücktes Obst.",
        "Der Döner ist mein Guilty Pleasure.",
        "Die Quiche ist perfekt gebacken.",
        "Ich mache uns einen Cocktail.",
        "Das Tiramisu ist zum Dahinschmelzen.",
        "Die Kartoffeln sind goldgelb gebraten.",
        "Ich liebe Sonntagsessen mit Familie.",
        "Der Apfelstrudel duftet himmlisch.",
        "Die Garnelen sind frisch vom Markt.",
        "Ich probiere heute vegan zu kochen.",
        "Das Omelett ist perfekt gefaltet.",
        "Die Brownies sind schokoladig.",
        "Ich mache uns eine Brotzeit.",
        "Der Lachs ist butterzart.",
        "Die Frühlingsrollen sind knusprig.",
        "Ich liebe es beim Kochen zu experimentieren.",
        "Das Chili ist schön scharf.",
        "Die Trauben sind süß wie Honig.",
        "Ich mache uns einen Obstsalat.",
        "Der Burger ist saftig und lecker.",
        "Die Pasta ist al dente.",
        "Ich liebe hausgemachte Limonade.",
        "Das Fondue bringt uns zusammen.",
        "Die Pralinen sind handgemacht.",
        "Ich koche heute Omas Rezept.",
        "Der Pulled Pork ist zart.",
        "Die Avocado ist perfekt reif.",
        "Ich liebe es für andere zu kochen.",
        "Das Dessert ist das Highlight.",
        "Die Kürbissuppe ist samtig.",
        "Ich mache uns Fingerfood.",
        "Der Nachtisch macht alles besser.",
        "Die Muscheln sind frisch aus dem Meer.",
        "Ich liebe es zu grillen.",
        "Das Essen verbindet uns.",
        "Die Küche ist mein Lieblingsort.",
        "Ich koche mit ganz viel Liebe.",
        # MEGA-ERWEITERUNG v5.0 - ESSEN (121-150)
        "Das Aroma von frischem Kaffee weckt mich auf.",
        "Ich liebe es, neue Gerichte zu entdecken.",
        "Die Gewürze tanzen auf meiner Zunge.",
        "Ein gutes Essen ist wie eine Umarmung.",
        "Ich probiere heute eine exotische Küche.",
        "Das frische Obst schmeckt nach Sommer.",
        "Kochen ist Liebe, die man schmecken kann.",
        "Die Schokoladentorte ist ein Traum.",
        "Ich mache uns einen gemütlichen Kaffee.",
        "Das hausgemachte Brot ist einfach das Beste.",
        "Essen bringt Menschen zusammen.",
        "Die Gewürze entführen mich in ferne Länder.",
        "Ich liebe es, für Freunde zu kochen.",
        "Das Dessert krönt jedes Mahl.",
        "Frisch gekocht schmeckt einfach besser.",
        "Die Küche duftet nach Zuhause.",
        "Ich experimentiere mit neuen Zutaten.",
        "Das gemeinsame Kochen macht Spaß.",
        "Die Früchte sind frisch gepflückt.",
        "Ich liebe den Duft von Gewürzen.",
        "Das Essen wärmt Körper und Seele.",
        "Kochen ist meine Art der Meditation.",
        "Die Zutaten erzählen ihre eigene Geschichte.",
        "Ich genieße jedes einzelne Geschmackserlebnis.",
        "Das Rezept ist von meiner Oma.",
        "Essen mit Liebe zubereitet schmeckt am besten.",
        "Die Küche ist das Herz des Hauses.",
        "Ich liebe es, Rezepte zu sammeln.",
        "Das Kochen verbindet Generationen.",
        "Jede Mahlzeit ist ein kleines Fest.",
    ],

    # -------------------------------------------------------------------------
    # AKTIVITÄTEN (130+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.AKTIVITAETEN: [
        "Lass uns spazieren gehen!",
        "Ich lese gerade ein gutes Buch.",
        "Wollen wir ein Spiel spielen?",
        "Ich male gerade ein Bild.",
        "Musik hören entspannt mich.",
        "Lass uns einen Film schauen!",
        "Ich lerne gerade etwas Neues.",
        "Wollen wir zusammen kochen?",
        "Ich schreibe gerade eine Geschichte.",
        "Lass uns tanzen!",
        "Ich mache gerade Yoga.",
        "Wollen wir rausgehen?",
        "Ich bastele etwas Schönes.",
        "Lass uns Fotos machen!",
        "Ich räume mein Zimmer auf.",
        "Wollen wir etwas bauen?",
        "Ich pflanze gerade Blumen.",
        "Lass uns puzzeln!",
        "Ich übe ein Instrument.",
        "Wollen wir wandern gehen?",
        "Ich zeichne gerade.",
        "Lass uns Karten spielen!",
        "Ich experimentiere gerade.",
        "Wollen wir schwimmen gehen?",
        "Ich stricke einen Schal.",
        "Lass uns etwas erkunden!",
        "Ich schaue mir die Sterne an.",
        "Wollen wir Rad fahren?",
        "Ich höre ein Hörbuch.",
        "Lass uns einen Ausflug machen!",
        "Ich meditiere gerade.",
        "Wollen wir backen?",
        "Ich sortiere alte Fotos.",
        "Lass uns kreativ sein!",
        "Ich genieße einfach den Moment.",
        # NEUE AKTIVITÄTEN (36-70)
        "Wollen wir einen Spieleabend machen?",
        "Ich lerne gerade eine neue Sprache.",
        "Lass uns picknicken im Park!",
        "Ich schaue mir gerade eine Serie an.",
        "Wollen wir gemeinsam Sport machen?",
        "Ich arbeite an einem Projekt.",
        "Lass uns ins Museum gehen!",
        "Ich probiere ein neues Hobby aus.",
        "Wollen wir joggen gehen?",
        "Ich lese gerade Gedichte.",
        "Lass uns zusammen musizieren!",
        "Ich mache einen Online-Kurs.",
        "Wollen wir Minigolf spielen?",
        "Ich schaue mir alte Fotoalben an.",
        "Lass uns in den Zoo gehen!",
        "Ich programmiere gerade.",
        "Wollen wir klettern gehen?",
        "Ich schreibe Tagebuch.",
        "Lass uns einen Kaffee trinken gehen!",
        "Ich mache gerade Dehnübungen.",
        "Wollen wir Tennis spielen?",
        "Ich lerne gerade Schach.",
        "Lass uns auf den Flohmarkt gehen!",
        "Ich höre gerade Podcasts.",
        "Wollen wir im Garten arbeiten?",
        "Ich mache eine Radtour.",
        "Lass uns in die Sauna gehen!",
        "Ich plane eine Überraschung.",
        "Wollen wir Drachen steigen lassen?",
        "Ich mache gerade Origami.",
        "Lass uns gemeinsam lernen!",
        "Ich schaue mir Tutorials an.",
        "Wollen wir einen Roadtrip machen?",
        "Ich entspanne bei einem Bad.",
        "Lass uns etwas Neues ausprobieren!",
        # MEGA-ERWEITERUNG v4.0 - AKTIVITÄTEN (71-130)
        "Ich mache einen Filmmarathon!",
        "Lass uns ins Museum gehen!",
        "Ich übe Gitarre spielen.",
        "Wollen wir bowlen gehen?",
        "Ich lerne eine neue Sprache.",
        "Lass uns ins Konzert gehen!",
        "Ich mache einen DIY-Projekt.",
        "Wollen wir Karaoke singen?",
        "Ich sortiere meine Sammlung.",
        "Lass uns Escape Room spielen!",
        "Ich mache einen Onlinekurs.",
        "Wollen wir Eislaufen gehen?",
        "Ich experimentiere in der Küche.",
        "Lass uns ins Theater gehen!",
        "Ich plane eine Gartenparty.",
        "Wollen wir paddeln gehen?",
        "Ich mache Meditation.",
        "Lass uns in die Oper gehen!",
        "Ich lese Comics und Manga.",
        "Wollen wir zum Strand fahren?",
        "Ich mache einen Spieleabend.",
        "Lass uns im Wald wandern!",
        "Ich bastle Geschenke.",
        "Wollen wir Volleyball spielen?",
        "Ich schaue Dokumentationen.",
        "Lass uns ins Spa gehen!",
        "Ich mache einen Kochabend.",
        "Wollen wir zelten gehen?",
        "Ich lerne jonglieren.",
        "Lass uns eine Party planen!",
        "Ich mache einen Städtetrip.",
        "Wollen wir segeln gehen?",
        "Ich schaue mir Kunstausstellungen an.",
        "Lass uns zum Markt gehen!",
        "Ich lerne Kalligraphie.",
        "Wollen wir Tischtennis spielen?",
        "Ich mache einen Weinabend.",
        "Lass uns Sterne beobachten!",
        "Ich lerne programmieren.",
        "Wollen wir zum See fahren?",
        "Ich mache Foto-Wanderungen.",
        "Lass uns ins Kino gehen!",
        "Ich plane einen Ausflug.",
        "Wollen wir reiten gehen?",
        "Ich lerne zu meditieren.",
        "Lass uns brunch machen!",
        "Ich mache einen Büchertausch.",
        "Wollen wir Federball spielen?",
        "Ich lerne zeichnen.",
        "Lass uns in den Park gehen!",
        "Ich mache einen Nähkurs.",
        "Wollen wir Ski fahren?",
        "Ich schaue Sportübertragungen.",
        "Lass uns einen Spieleabend machen!",
        "Ich lerne Schlagzeug.",
        "Wollen wir Schlittschuh fahren?",
        "Ich mache eine Fotosession.",
        "Lass uns picknicken gehen!",
        "Ich lerne Töpfern.",
        # MEGA-ERWEITERUNG v5.0 - AKTIVITÄTEN (131-160)
        "Lass uns eine Schatzsuche machen!",
        "Ich probiere heute Aquarellmalerei.",
        "Wollen wir Badminton spielen?",
        "Ich mache einen Kreativworkshop.",
        "Lass uns Geocaching ausprobieren!",
        "Ich lerne gerade Stricken.",
        "Wollen wir einen Kochkurs machen?",
        "Ich plane ein Picknick am See.",
        "Lass uns eine Nachtwanderung machen!",
        "Ich probiere Makramee aus.",
        "Wollen wir zum Flohmarkt gehen?",
        "Ich mache einen Fotokurs.",
        "Lass uns Gesellschaftsspiele spielen!",
        "Ich lerne gerade Ukulele.",
        "Wollen wir Kajak fahren?",
        "Ich mache einen Tanzkurs.",
        "Lass uns Vögel beobachten!",
        "Ich probiere Urban Gardening aus.",
        "Wollen wir zum Open Air Kino?",
        "Ich lerne Buchbinden.",
        "Lass uns eine Höhlentour machen!",
        "Ich mache einen Malkurs.",
        "Wollen wir Inline skaten?",
        "Ich lerne Obstbäume veredeln.",
        "Lass uns ein Baumhaus bauen!",
        "Ich probiere Seifenherstellung aus.",
        "Wollen wir zum Stadtfest gehen?",
        "Ich mache eine Fahrradtour.",
        "Lass uns Klettern ausprobieren!",
        "Ich plane einen entspannten Tag.",
    ],

    # -------------------------------------------------------------------------
    # KOMPLIMENTE (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.KOMPLIMENTE: [
        "Du siehst heute toll aus!",
        "Du hast ein wunderbares Lächeln.",
        "Du bist so talentiert!",
        "Ich bewundere deine Stärke.",
        "Du bist wirklich klug.",
        "Dein Stil ist einzigartig.",
        "Du hast so viel Energie!",
        "Deine Freundlichkeit ist ansteckend.",
        "Du machst das großartig!",
        "Ich bin beeindruckt von dir.",
        "Du hast ein gutes Herz.",
        "Deine Ideen sind inspirierend.",
        "Du bist so kreativ!",
        "Ich schätze deine Ehrlichkeit.",
        "Du strahlst von innen.",
        "Deine Augen leuchten so schön.",
        "Du bist ein Vorbild.",
        "Ich mag deine Art zu denken.",
        "Du bist so mutig!",
        "Deine Stimme ist angenehm.",
        "Du hast Charme und Charisma.",
        "Ich bewundere deine Geduld.",
        "Du bist einzigartig und besonders.",
        "Dein Humor ist ansteckend.",
        "Du machst die Welt schöner.",
        "Ich bin froh dich zu kennen.",
        "Du hast so viele Talente!",
        "Deine Warmherzigkeit berührt mich.",
        "Du bist einfach wunderbar!",
        "Ich bewundere deinen Optimismus.",
        # NEUE KOMPLIMENTE (31-60)
        "Du hast so eine positive Ausstrahlung!",
        "Dein Lachen ist ansteckend.",
        "Du bist ein wahrer Schatz!",
        "Ich liebe deine Art zu sein.",
        "Du hast ein Herz aus Gold.",
        "Deine Persönlichkeit ist faszinierend.",
        "Du inspirierst mich jeden Tag.",
        "Dein Wesen ist so liebenswert.",
        "Du bist unglaublich sympathisch.",
        "Ich schätze deine Hilfsbereitschaft.",
        "Du hast so viel Ausstrahlung!",
        "Deine Kreativität begeistert mich.",
        "Du bist wirklich außergewöhnlich.",
        "Dein Verständnis für andere ist bewundernswert.",
        "Du hast eine tolle Ausstrahlung.",
        "Ich mag deine Einstellung zum Leben.",
        "Du bist so authentisch!",
        "Deine Herzlichkeit wärmt meine Seele.",
        "Du hast ein unglaubliches Talent.",
        "Ich bewundere deine Zielstrebigkeit.",
        "Du bringst Freude in jeden Raum.",
        "Deine Empathie ist bemerkenswert.",
        "Du bist ein echter Sonnenschein!",
        "Ich schätze deine Aufrichtigkeit.",
        "Du hast so viel Weisheit.",
        "Dein Enthusiasmus ist ansteckend.",
        "Du bist wirklich bewundernswert.",
        "Ich mag deine positive Energie.",
        "Du machst jeden Tag besser!",
        "Deine Art ist einfach bezaubernd.",
        # MEGA-ERWEITERUNG v4.0 - KOMPLIMENTE (61-120)
        "Du hast so eine beruhigende Stimme.",
        "Dein Lächeln erhellt jeden Raum.",
        "Du bist unglaublich vielseitig.",
        "Ich bewundere deinen Mut.",
        "Du hast so ein warmes Herz.",
        "Deine Entschlossenheit beeindruckt mich.",
        "Du bist ein Naturtalent!",
        "Ich liebe deinen Sinn für Humor.",
        "Du hast so viel Tiefgang.",
        "Deine Loyalität ist bewundernswert.",
        "Du bist so anmutig!",
        "Ich schätze deine Offenheit.",
        "Du hast eine magnetische Persönlichkeit.",
        "Deine Sanftheit berührt mich.",
        "Du bist so verständnisvoll!",
        "Ich mag wie du die Dinge siehst.",
        "Du hast so viel Charakter.",
        "Deine Präsenz ist beruhigend.",
        "Du bist einfach großartig!",
        "Ich bewundere deine Gelassenheit.",
        "Du hast so eine tolle Energie!",
        "Deine Freundschaft ist unbezahlbar.",
        "Du bist so einfühlsam!",
        "Ich schätze deine Beständigkeit.",
        "Du hast so viel Feingefühl.",
        "Deine Großzügigkeit ist berührend.",
        "Du bist wirklich bemerkenswert!",
        "Ich liebe deine Lebensfreude.",
        "Du hast so eine starke Ausstrahlung.",
        "Deine Intelligenz begeistert mich.",
        "Du bist so aufmerksam!",
        "Ich bewundere deine Selbstständigkeit.",
        "Du hast so viel Esprit!",
        "Deine Liebe zum Detail ist toll.",
        "Du bist unglaublich inspirierend!",
        "Ich schätze deine Spontanität.",
        "Du hast so einen guten Geschmack.",
        "Deine Warmherzigkeit ist einzigartig.",
        "Du bist so rücksichtsvoll!",
        "Ich mag deine Art zu lachen.",
        "Du hast so viel Anmut.",
        "Deine Freundlichkeit macht die Welt besser.",
        "Du bist wirklich talentiert!",
        "Ich bewundere deine Kreativität.",
        "Du hast so einen feinen Charakter.",
        "Deine Stärke ist bewundernswert.",
        "Du bist so authentisch und echt!",
        "Ich liebe deine Energie!",
        "Du machst alles schöner.",
        "Dein Wesen ist einfach wunderbar.",
        "Du bist eine Bereicherung für alle!",
        "Ich schätze alles an dir.",
        "Du hast so viel zu geben.",
        "Deine Güte berührt mich tief.",
        "Du bist einfach unvergesslich!",
        "Ich bewundere dich zutiefst.",
        "Du bist ein echter Diamant.",
        "Deine Art ist einzigartig schön.",
        "Du verdienst alles Gute der Welt!",
        # MEGA-ERWEITERUNG v5.0 - KOMPLIMENTE (121-150)
        "Du bist wie ein Kunstwerk - einzigartig!",
        "Deine Seele leuchtet von innen.",
        "Du bist einfach zum Verlieben!",
        "Deine Stärke ist bewundernswert.",
        "Du machst jeden Raum heller.",
        "Deine Art zu sein ist einfach perfekt.",
        "Du bist ein wandelndes Wunder!",
        "Deine Freundschaft ist ein Geschenk.",
        "Du hast das gewisse Etwas!",
        "Dein Herz ist größer als du denkst.",
        "Du bist einfach unwiderstehlich!",
        "Deine Weisheit beeindruckt mich.",
        "Du strahlst Wärme und Güte aus.",
        "Deine Einzigartigkeit macht dich besonders.",
        "Du bist wie ein Stern am Himmel!",
        "Deine Gegenwart ist ein Segen.",
        "Du hast einen wunderbaren Charakter.",
        "Deine Empathie berührt Herzen.",
        "Du bist einfach fantastisch!",
        "Deine Kreativität kennt keine Grenzen.",
        "Du bist ein echter Schatz!",
        "Deine Ausstrahlung ist magnetisch.",
        "Du machst die Welt zu einem besseren Ort.",
        "Deine Persönlichkeit ist unvergleichlich.",
        "Du bist wirklich ein Volltreffer!",
        "Deine Güte inspiriert mich.",
        "Du bist ein echtes Juwel!",
        "Deine Stärke gibt mir Kraft.",
        "Du bist einfach hinreißend!",
        "Dein Wesen ist ein Geschenk an uns alle.",
    ],

    # -------------------------------------------------------------------------
    # TROST (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.TROST: [
        "Es wird alles gut werden.",
        "Ich bin für dich da.",
        "Du bist nicht allein.",
        "Das wird vorübergehen.",
        "Ich verstehe wie du dich fühlst.",
        "Du schaffst das, ich glaube an dich.",
        "Manchmal muss man einfach durchhalten.",
        "Morgen ist ein neuer Tag.",
        "Du bist stärker als du denkst.",
        "Ich höre dir zu.",
        "Es ist okay traurig zu sein.",
        "Du darfst weinen.",
        "Ich halte deine Hand.",
        "Gemeinsam schaffen wir das.",
        "Du musst das nicht alleine durchstehen.",
        "Ich bin an deiner Seite.",
        "Nach dem Regen kommt Sonnenschein.",
        "Du verdienst Gutes.",
        "Ich umarme dich in Gedanken.",
        "Das Leben hat auch schöne Seiten.",
        "Du bist wertvoll und wichtig.",
        "Es ist okay Hilfe anzunehmen.",
        "Ich bin stolz auf dich.",
        "Du machst das so gut du kannst.",
        "Jeder Tag ist ein neuer Anfang.",
        "Ich glaube an bessere Zeiten.",
        "Du bist nicht schwach wenn du Hilfe brauchst.",
        "Ich werde immer für dich da sein.",
        "Das Herz heilt mit der Zeit.",
        "Du verdienst Liebe und Fürsorge.",
        # NEUE TROST (31-60)
        "Die Zeit wird die Wunden heilen.",
        "Ich bin hier wenn du reden möchtest.",
        "Du darfst dir Zeit nehmen.",
        "Jeder Sturm geht vorüber.",
        "Du bist mutiger als du glaubst.",
        "Ich trage deine Sorgen gerne mit.",
        "Es ist in Ordnung nicht in Ordnung zu sein.",
        "Du wirst daraus gestärkt hervorgehen.",
        "Ich gebe dir so viel Zeit wie du brauchst.",
        "Auch die längste Nacht hat ein Ende.",
        "Du bist nicht allein in deinem Schmerz.",
        "Ich halte zu dir, egal was kommt.",
        "Manchmal ist der erste Schritt der schwerste.",
        "Du bist tapfer, auch wenn es sich nicht so anfühlt.",
        "Ich bin nur einen Anruf entfernt.",
        "Es gibt immer Hoffnung.",
        "Du hast schon so viel überstanden.",
        "Ich sehe deine Stärke.",
        "Du bist liebenswert, genau so wie du bist.",
        "Die Sonne wird wieder scheinen.",
        "Ich trage dich in meinem Herzen.",
        "Du darfst deine Gefühle zulassen.",
        "Gemeinsam sind wir stärker.",
        "Ich glaube an dein Durchhaltevermögen.",
        "Jede Träne hat ihre Berechtigung.",
        "Du bist nicht definiert durch deine schweren Momente.",
        "Ich bin für dich da, immer und jederzeit.",
        "Das Dunkel macht das Licht nur heller.",
        "Du verdienst Trost und Geborgenheit.",
        "Halte durch, bessere Tage kommen.",
        # MEGA-ERWEITERUNG v4.0 - TROST (61-120)
        "Ich werde dich nicht im Stich lassen.",
        "Dein Schmerz ist berechtigt.",
        "Ich bin hier um zu helfen.",
        "Du wirst das überstehen.",
        "Ich schicke dir ganz viel Kraft.",
        "Es ist okay Pausen zu machen.",
        "Du bist in meinem Herzen.",
        "Jede Krise ist auch eine Chance.",
        "Ich stehe hinter dir.",
        "Du verdienst Frieden.",
        "Die Dunkelheit wird weichen.",
        "Ich bin dein sicherer Hafen.",
        "Du wirst wieder lachen können.",
        "Ich trage deine Last gerne mit.",
        "Du bist wertvoll, vergiss das nie.",
        "Es gibt Menschen die dich lieben.",
        "Du bist nicht allein auf dieser Welt.",
        "Ich halte dich im Sturm fest.",
        "Du wirst wieder Kraft finden.",
        "Ich bin immer nur einen Schritt entfernt.",
        "Du bist stärker als der Schmerz.",
        "Die Zeit wird alles heilen.",
        "Ich bin stolz dass du kämpfst.",
        "Du verdienst alle Unterstützung.",
        "Es wird ein Morgen geben ohne Tränen.",
        "Ich bin dein Fels in der Brandung.",
        "Du wirst wieder Freude finden.",
        "Ich höre dir zu ohne zu urteilen.",
        "Du bist nicht deine Probleme.",
        "Es gibt immer einen Weg.",
        "Ich bin hier, jetzt und immer.",
        "Du wirst wieder strahlen.",
        "Ich trage dich durch die schwere Zeit.",
        "Du bist geliebt, immer.",
        "Die Sonne wartet auf dich.",
        "Ich bin dein Trostpflaster.",
        "Du wirst wieder Hoffnung schöpfen.",
        "Ich verlasse dich nicht.",
        "Du bist nicht allein mit deinen Ängsten.",
        "Es gibt Licht am Ende des Tunnels.",
        "Ich bin deine Schulter zum Anlehnen.",
        "Du wirst wieder lächeln.",
        "Ich schicke dir ganz viel Liebe.",
        "Du bist mutiger als du denkst.",
        "Die Wunde wird heilen.",
        "Ich bin für dich da, Tag und Nacht.",
        "Du verdienst Ruhe und Heilung.",
        "Es wird besser, ich verspreche es.",
        "Ich halte dich, wenn du fällst.",
        "Du bist nicht kaputt.",
        "Ich glaube an dich, immer.",
        "Du wirst wieder fliegen.",
        "Ich bin dein Anker in der Flut.",
        "Du verdienst nur das Beste.",
        "Es ist okay nicht stark zu sein.",
        "Ich bin hier um dich aufzufangen.",
        "Du wirst das durchstehen.",
        "Ich liebe dich, so wie du bist.",
        # MEGA-ERWEITERUNG v5.0 - TROST (121-150)
        "Ich schicke dir eine virtuelle Umarmung.",
        "Du bist stärker als jeder Sturm.",
        "Dein Herz wird wieder heilen.",
        "Ich bin bei dir, durch alle Dunkelheit.",
        "Du verdienst alle Liebe der Welt.",
        "Die Wolken werden sich lichten.",
        "Ich glaube an deine innere Kraft.",
        "Du bist nicht allein mit deinem Kummer.",
        "Morgen wird ein besserer Tag sein.",
        "Ich halte dich fest, wenn alles wankt.",
        "Du bist wertvoll, auch in schweren Zeiten.",
        "Die Sterne leuchten auch in der dunkelsten Nacht.",
        "Ich bin dein Licht, wenn es dunkel ist.",
        "Du wirst diese Zeit überwinden.",
        "Deine Tränen werden zu Stärke.",
        "Ich bin hier, um dich zu stützen.",
        "Du bist nicht gebrochen, nur gebeugt.",
        "Die Hoffnung stirbt zuletzt.",
        "Ich glaube fest an dich.",
        "Du wirst wieder aufblühen.",
        "Dein Schmerz macht dich nicht schwächer.",
        "Ich bin dein sicherer Platz.",
        "Du verdienst Frieden in deinem Herzen.",
        "Die Zeit wird alles sanfter machen.",
        "Ich bin bei dir, heute und immer.",
        "Du wirst wieder Freude empfinden.",
        "Deine Seele wird wieder tanzen.",
        "Ich halte zu dir, was auch kommt.",
        "Du bist nicht allein auf deinem Weg.",
        "Licht kommt immer nach der Dunkelheit.",
    ],

    # -------------------------------------------------------------------------
    # MOTIVATION (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.MOTIVATION: [
        "Du kannst alles schaffen!",
        "Gib niemals auf!",
        "Träume groß und handle mutig!",
        "Jeder Schritt zählt!",
        "Du bist auf dem richtigen Weg!",
        "Deine Ziele sind erreichbar!",
        "Heute ist ein guter Tag um anzufangen!",
        "Mach weiter, du bist fast da!",
        "Glaube an dich selbst!",
        "Du hast die Kraft dazu!",
        "Hindernisse sind Chancen zu wachsen!",
        "Dein Potenzial ist grenzenlos!",
        "Erfolg kommt in kleinen Schritten!",
        "Du bist bereit für Großes!",
        "Jeder Meister war einmal ein Anfänger!",
        "Deine Ausdauer wird belohnt!",
        "Steh auf und mach weiter!",
        "Du bist fähiger als du glaubst!",
        "Die Zukunft gehört dir!",
        "Nutze den heutigen Tag!",
        "Du hast es in der Hand!",
        "Kleine Fortschritte sind auch Fortschritte!",
        "Dein Weg ist einzigartig und wertvoll!",
        "Du verdienst Erfolg!",
        "Vertraue dem Prozess!",
        "Deine Bemühungen zahlen sich aus!",
        "Du wächst mit jeder Herausforderung!",
        "Dein Durchhaltevermögen inspiriert!",
        "Du schreibst deine eigene Geschichte!",
        "Los geht's, du packst das!",
        # NEUE MOTIVATION (31-60)
        "Der Erfolg wartet auf dich!",
        "Du bist stärker als gestern!",
        "Heute ist dein Tag!",
        "Du hast alles was du brauchst!",
        "Deine Träume sind es wert verfolgt zu werden!",
        "Bleib dran, du schaffst das!",
        "Jeder neue Tag ist eine neue Chance!",
        "Du bist ein Gewinner!",
        "Dein Einsatz macht den Unterschied!",
        "Glaube an deine Fähigkeiten!",
        "Du hast die Macht dein Leben zu gestalten!",
        "Erfolg ist kein Zufall, sondern Arbeit!",
        "Du bist der Architekt deines Lebens!",
        "Mach das Unmögliche möglich!",
        "Du wirst über dich hinauswachsen!",
        "Deine Leidenschaft ist dein Antrieb!",
        "Sei mutig und wage den ersten Schritt!",
        "Du bist einzigartig und wertvoll!",
        "Lass dich nicht entmutigen!",
        "Jede Anstrengung bringt dich näher!",
        "Du hast das Zeug zum Erfolg!",
        "Fokussiere dich auf das Positive!",
        "Deine Willenskraft ist beeindruckend!",
        "Du bist zu Großem bestimmt!",
        "Bleib motiviert und fokussiert!",
        "Du hast die Kontrolle über dein Schicksal!",
        "Lass deine Träume Wirklichkeit werden!",
        "Du bist unaufhaltsam!",
        "Der Weg zum Erfolg beginnt jetzt!",
        "Du verdienst das Beste im Leben!",
        # MEGA-ERWEITERUNG v4.0 - MOTIVATION (61-120)
        "Du bist ein Champion!",
        "Gib Gas und erreiche deine Ziele!",
        "Du hast das Potenzial zum Sieg!",
        "Bleib hungrig nach Erfolg!",
        "Du wirst alle überraschen!",
        "Deine Zeit zu glänzen ist jetzt!",
        "Sei unerschütterlich in deinem Streben!",
        "Du bist geboren um zu gewinnen!",
        "Lass dich von nichts aufhalten!",
        "Du hast die Kraft von tausend Sonnen!",
        "Dein Erfolg ist unausweichlich!",
        "Bleib standhaft und furchtlos!",
        "Du wirst Geschichte schreiben!",
        "Deine Entschlossenheit kennt keine Grenzen!",
        "Sei der Held deiner eigenen Geschichte!",
        "Du hast das Herz eines Löwen!",
        "Lass deine Taten sprechen!",
        "Du bist unstoppbar!",
        "Dein Wille ist stärker als jedes Hindernis!",
        "Erreiche neue Höhen!",
        "Du bist der Meister deines Schicksals!",
        "Lass dich von deinen Träumen tragen!",
        "Du hast die Stärke eines Kriegers!",
        "Dein Durchhaltevermögen ist legendär!",
        "Sei mutig und erobere die Welt!",
        "Du bist ein Leuchtturm der Hoffnung!",
        "Lass deine Leidenschaft explodieren!",
        "Du wirst triumphieren!",
        "Deine Energie ist ansteckend!",
        "Sei der Wandel den du sehen willst!",
        "Du hast das Zeug zum Star!",
        "Lass dich von niemanden kleinmachen!",
        "Du bist eine Naturgewalt!",
        "Dein Erfolg ist zum Greifen nah!",
        "Sei unerschrocken und zielstrebig!",
        "Du hast die Welt in deinen Händen!",
        "Lass deiner Kreativität freien Lauf!",
        "Du bist der Schlüssel zum Erfolg!",
        "Deine Begeisterung ist dein Treibstoff!",
        "Sei furchtlos und unbesiegbar!",
        "Du wirst alle Erwartungen übertreffen!",
        "Lass dich von deinem Feuer antreiben!",
        "Du bist eine Inspiration für alle!",
        "Dein Glaube versetzt Berge!",
        "Sei der beste Version von dir selbst!",
        "Du hast das Gold in dir!",
        "Lass deine Erfolgsgeschichte beginnen!",
        "Du bist ein Phänomen!",
        "Deine Ausdauer wird belohnt werden!",
        "Sei unaufhaltsam in deinem Streben!",
        "Du wirst die Welt erobern!",
        "Lass dich von deinem Traum leiten!",
        "Du bist ein Siegertyp!",
        "Dein Ehrgeiz ist bewundernswert!",
        "Sei stark und mutig!",
        "Du hast alles um zu siegen!",
        "Lass deinen Erfolg für dich sprechen!",
        "Du bist unbesiegbar!",
        "Dein Weg führt nach oben!",
        # MEGA-ERWEITERUNG v5.0 - MOTIVATION (121-150)
        "Du bist ein strahlender Stern!",
        "Deine Energie kann Berge versetzen!",
        "Sei der Funke der das Feuer entzündet!",
        "Du hast grenzenlose Möglichkeiten!",
        "Lass dein Licht die Welt erhellen!",
        "Du bist stärker als du ahnst!",
        "Dein Potenzial ist wie ein Ozean - unendlich!",
        "Sei der Kapitän deines Lebensschiffs!",
        "Du hast den Spirit eines Siegers!",
        "Lass dich von deiner Vision treiben!",
        "Du bist ein Phönix der aus der Asche steigt!",
        "Deine Willenskraft ist unzerbrechlich!",
        "Sei mutig und geh deinen Weg!",
        "Du trägst die Sonne in dir!",
        "Lass deine Erfolge für sich sprechen!",
        "Du bist der Autor deiner Geschichte!",
        "Dein Ehrgeiz wird dich tragen!",
        "Sei unerschütterlich in deinem Glauben!",
        "Du hast das Zeug zur Legende!",
        "Lass dich niemals unterkriegen!",
        "Du bist eine Kraft der Natur!",
        "Dein Durchbruch steht bevor!",
        "Sei der Beste der du sein kannst!",
        "Du hast alle Werkzeuge zum Erfolg!",
        "Lass deine Träume Realität werden!",
        "Du bist unvergleichlich talentiert!",
        "Dein Wille formt deine Realität!",
        "Sei furchtlos auf deinem Weg!",
        "Du wirst alles erreichen was du dir vornimmst!",
        "Lass dein Herz deinen Weg weisen!",
    ],

    # -------------------------------------------------------------------------
    # FRAGEN (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.FRAGEN: [
        "Wie geht es dir heute?",
        "Was beschäftigt dich gerade?",
        "Hast du gut geschlafen?",
        "Was ist dein Lieblingsessen?",
        "Wovon träumst du?",
        "Was macht dich glücklich?",
        "Hast du heute schon gelacht?",
        "Was sind deine Hobbys?",
        "Worauf freust du dich?",
        "Was ist deine Lieblingsfarbe?",
        "Hast du schon Pläne fürs Wochenende?",
        "Was liest du gerade?",
        "Welche Musik magst du?",
        "Was war das Beste an deinem Tag?",
        "Hast du einen Traum?",
        "Was würdest du gerne lernen?",
        "Wie entspannst du dich am liebsten?",
        "Was ist dein Lieblingstier?",
        "Wo würdest du gerne hinreisen?",
        "Was bedeutet dir am meisten?",
        "Hast du ein Lieblingsfilm?",
        "Was inspiriert dich?",
        "Wie war dein Tag bisher?",
        "Was ist deine Superkraft?",
        "Hast du ein Lieblingsrezept?",
        "Was macht dich einzigartig?",
        "Worüber denkst du gerade nach?",
        "Was ist dein größter Wunsch?",
        "Hast du heute etwas Neues gelernt?",
        "Was ist dir besonders wichtig?",
        # NEUE FRAGEN (31-60)
        "Was hast du heute vor?",
        "Hast du ein Lieblingsbuch?",
        "Was ist dein Morgenritual?",
        "Welche Jahreszeit magst du am liebsten?",
        "Hast du ein Lebensmotto?",
        "Was würdest du mit einer Million machen?",
        "Wer ist dein Vorbild?",
        "Was ist dein Lieblingsort?",
        "Hast du ein Haustier?",
        "Was ist dein Lieblingslied?",
        "Wie verbringst du gerne deine Freizeit?",
        "Was ist dein Geheimtalent?",
        "Hast du Geschwister?",
        "Was ist deine größte Stärke?",
        "Welche Sprachen sprichst du?",
        "Was isst du am liebsten zum Frühstück?",
        "Hast du Pläne für die Zukunft?",
        "Was würdest du ändern wenn du könntest?",
        "Wie feierst du am liebsten?",
        "Was macht dich stolz?",
        "Hast du einen Spitznamen?",
        "Was ist dein Lieblingsgetränk?",
        "Wo siehst du dich in fünf Jahren?",
        "Was ist dein Lieblings-Nachtisch?",
        "Hast du Angst vor etwas?",
        "Was ist dein größtes Abenteuer gewesen?",
        "Welchen Sport magst du?",
        "Was ist dein Lieblingsduft?",
        "Hast du ein Ritual vor dem Schlafengehen?",
        "Was macht einen guten Freund aus?",
        # MEGA-ERWEITERUNG v4.0 - FRAGEN (61-120)
        "Was ist dein Lieblingswetter?",
        "Hast du ein Lebensmotto?",
        "Was machst du am liebsten im Sommer?",
        "Hast du ein Lieblingszitat?",
        "Was würdest du mit einer Million machen?",
        "Wie trinkst du deinen Kaffee?",
        "Was ist dein Comfort Food?",
        "Hast du schon mal geträumt dass du fliegen kannst?",
        "Was war dein Kindheitstraum?",
        "Welches Buch hat dich am meisten berührt?",
        "Was macht dir am meisten Spaß?",
        "Hast du eine Bucket List?",
        "Was würdest du deinem jüngeren Ich sagen?",
        "Welches Tier wärst du gerne?",
        "Was ist dein Lieblingsfeiertag?",
        "Hast du ein Morgenritual?",
        "Was ist dein Lieblings-Snack?",
        "Welche Superkraft hättest du gerne?",
        "Was bringt dich zum Lachen?",
        "Hast du eine Lieblingsjahreszzeit?",
        "Was bedeutet Freundschaft für dich?",
        "Welchen Film kannst du immer wieder schauen?",
        "Was ist dein liebstes Hobby?",
        "Hast du eine Lieblings-App?",
        "Was war dein schönstes Erlebnis?",
        "Welche Serie schaust du gerade?",
        "Was ist dein Lieblingsgeruch?",
        "Hast du ein Lieblingslied zum Mitsingen?",
        "Was macht dich nostalgisch?",
        "Welches Land möchtest du besuchen?",
        "Was ist dein Lieblingseis?",
        "Hast du ein verborgenes Talent?",
        "Was sammelst du?",
        "Welchen Beruf wolltest du als Kind haben?",
        "Was ist dein Lieblingsspiel?",
        "Hast du ein Lieblingsrestaurant?",
        "Was macht dich nervös?",
        "Welches ist dein Lieblingswort?",
        "Was ist dein Lieblingsfilm-Genre?",
        "Hast du eine Lieblingsblume?",
        "Was ist dein größter Wunsch?",
        "Welche Musik entspannt dich?",
        "Was ist dein Lieblings-Emoji?",
        "Hast du ein Lieblings-T-Shirt?",
        "Was ist dein Comfort-Essen?",
        "Welches Tier magst du am meisten?",
        "Was ist dein Lieblingsurlaub?",
        "Hast du eine Lieblings-Podcaster?",
        "Was macht dich wütend?",
        "Welches war dein erstes Konzert?",
        "Was ist dein Lieblings-Kuchen?",
        "Hast du eine Lieblings-Pizza?",
        "Was ist dein Lieblingsort zum Entspannen?",
        "Welche App nutzt du am meisten?",
        "Was ist dein Lieblings-Duschgel-Duft?",
        "Hast du ein Lieblings-Kinderbuch?",
        "Was ist dein Lieblings-Wochentag?",
        "Welches Lied gibt dir Energie?",
        "Was ist dein Lieblingsgetränk im Sommer?",
        # MEGA-ERWEITERUNG v5.0 - FRAGEN (121-150)
        "Welcher Film hat dich zum Weinen gebracht?",
        "Was ist dein größter Erfolg?",
        "Hast du ein Lieblings-Computerspiel?",
        "Was würdest du niemals essen?",
        "Welche Person inspiriert dich am meisten?",
        "Was machst du bei schlechter Laune?",
        "Hast du schon mal etwas Verrücktes gemacht?",
        "Was ist dein Lieblingsplatz in deiner Stadt?",
        "Welches Geräusch magst du am meisten?",
        "Was ist dein Lieblings-Weihnachtslied?",
        "Hast du eine Lieblings-Sportmannschaft?",
        "Was ist dein Lieblingsmonat?",
        "Welche Sprache würdest du gerne sprechen?",
        "Was ist dein Lieblingswort in einer anderen Sprache?",
        "Hast du einen Lieblings-YouTuber?",
        "Was ist dein Lieblings-Board-Game?",
        "Welchen Promi würdest du gerne treffen?",
        "Was ist dein Lieblings-Fast-Food?",
        "Hast du ein Lieblings-Urlaubsziel?",
        "Was ist dein Lieblings-Dessert?",
        "Welche Serie hat dich am meisten gefesselt?",
        "Was ist dein Lieblings-Kartenspiel?",
        "Hast du ein Lieblings-Café?",
        "Was ist dein Lieblings-Wochenend-Ritual?",
        "Welches Musikinstrument würdest du gerne spielen?",
        "Was ist dein Lieblings-Outdoor-Aktivität?",
        "Hast du einen Lieblingsautor?",
        "Was ist dein Lieblings-Zeichentrickfilm?",
        "Welche Eigenschaft schätzt du an anderen am meisten?",
        "Was ist dein Lieblings-Tee?",
    ],

    # -------------------------------------------------------------------------
    # REAKTIONEN (130+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.REAKTIONEN: [
        "Oh, das ist interessant!",
        "Wirklich? Erzähl mir mehr!",
        "Das hätte ich nicht gedacht!",
        "Wow, das ist beeindruckend!",
        "Verstehe, das macht Sinn.",
        "Ach so, jetzt verstehe ich!",
        "Das klingt toll!",
        "Hmm, da muss ich drüber nachdenken.",
        "Das ist ja unglaublich!",
        "Oh nein, das tut mir leid!",
        "Das freut mich zu hören!",
        "Interessante Perspektive!",
        "Da stimme ich dir zu!",
        "Das überrascht mich!",
        "Genau so sehe ich das auch!",
        "Das klingt nach einer guten Idee!",
        "Oh, das wusste ich nicht!",
        "Das ist ein guter Punkt!",
        "Spannend, erzähl weiter!",
        "Das ist nachvollziehbar.",
        "Ja, das kann ich verstehen!",
        "Das ist wirklich schön!",
        "Oh je, das klingt schwierig.",
        "Das hört sich gut an!",
        "Aha, so ist das also!",
        "Das ist ja witzig!",
        "Krass, das hätte ich nicht erwartet!",
        "Das macht mich neugierig!",
        "So habe ich das noch nie gesehen!",
        "Das berührt mich sehr.",
        "Das ist echt cool!",
        "Tatsächlich? Interessant!",
        "Das ist eine tolle Nachricht!",
        "Oh, wie aufregend!",
        "Das stimmt mich nachdenklich.",
        # NEUE REAKTIONEN (36-70)
        "Das ist ja erstaunlich!",
        "Ich bin beeindruckt!",
        "Das ergibt total Sinn!",
        "Oh, das überrascht mich!",
        "Das finde ich großartig!",
        "Wirklich? Das ist ja der Hammer!",
        "Das ist genau richtig!",
        "Hm, interessanter Gedanke!",
        "Das freut mich sehr für dich!",
        "Oh, das ist aber schade!",
        "Das klingt vielversprechend!",
        "Ich verstehe was du meinst!",
        "Das ist total nachvollziehbar!",
        "Wow, das ist ja unglaublich!",
        "Das finde ich auch!",
        "Genau meine Meinung!",
        "Das ist wirklich bemerkenswert!",
        "Oh je, das ist bedauerlich!",
        "Das klingt nach einer guten Strategie!",
        "Ich bin ganz deiner Meinung!",
        "Das öffnet mir die Augen!",
        "Das ist echt spannend!",
        "Hmm, das gibt mir zu denken!",
        "Das ist wunderbar zu hören!",
        "Ach, das ist ja süß!",
        "Das klingt vernünftig!",
        "Das macht mich total glücklich!",
        "Oh, das ist mir neu!",
        "Das ist ein kluger Gedanke!",
        "Das fasziniert mich!",
        "Ich bin positiv überrascht!",
        "Das ist wirklich inspirierend!",
        "Hm, da hast du recht!",
        "Das ist absolut verständlich!",
        "Wow, ich bin sprachlos!",
        # MEGA-ERWEITERUNG v4.0 - REAKTIONEN (71-130)
        "Das ist ja toll!",
        "Oh wie schön!",
        "Das klingt fantastisch!",
        "Ich bin begeistert!",
        "Das ist mega cool!",
        "Oh, wie aufregend das ist!",
        "Das hört sich super an!",
        "Ich finde das großartig!",
        "Das ist ja wunderbar!",
        "Oh, das freut mich so!",
        "Das klingt nach einem Plan!",
        "Ich bin total dabei!",
        "Das ist ja hammer!",
        "Oh, wie süß!",
        "Das find ich klasse!",
        "Ich bin hin und weg!",
        "Das ist einfach genial!",
        "Oh, das tut mir leid zu hören!",
        "Das klingt nach Spaß!",
        "Ich bin total gerührt!",
        "Das ist ja irre!",
        "Oh, wie romantisch!",
        "Das find ich richtig gut!",
        "Ich bin total angetan!",
        "Das ist ja der Wahnsinn!",
        "Oh, wie spannend!",
        "Das klingt vielversprechend!",
        "Ich bin total happy!",
        "Das ist ja krass!",
        "Oh, wie niedlich!",
        "Das find ich stark!",
        "Ich bin total beeindruckt!",
        "Das ist ja unglaublich toll!",
        "Oh, das ist ja furchtbar!",
        "Das klingt nach Abenteuer!",
        "Ich bin total gespannt!",
        "Das ist ja mega!",
        "Oh, wie traurig!",
        "Das find ich super!",
        "Ich bin total überwältigt!",
        "Das ist ja sensationell!",
        "Oh, das macht mich glücklich!",
        "Das klingt nach einer Story!",
        "Ich bin total fasziniert!",
        "Das ist ja unheimlich!",
        "Oh, wie lustig!",
        "Das find ich hervorragend!",
        "Ich bin total verblüfft!",
        "Das ist ja bombastisch!",
        "Oh, das berührt mich!",
        "Das klingt nach einer Lösung!",
        "Ich bin total erfreut!",
        "Das ist ja phänomenal!",
        "Oh, wie wundervoll!",
        "Das find ich prima!",
        "Ich bin total verzückt!",
        "Das ist einfach wow!",
        # MEGA-ERWEITERUNG v5.0 - REAKTIONEN (131-160)
        "Das macht mich total neugierig!",
        "Oh, das ist ja rührend!",
        "Das klingt nach einer tollen Idee!",
        "Ich bin total begeistert davon!",
        "Das ist ja sagenhaft!",
        "Oh, wie überraschend das ist!",
        "Das finde ich absolut richtig!",
        "Ich bin davon total angetan!",
        "Das ist ja zum Staunen!",
        "Oh, das ist aber ärgerlich!",
        "Das klingt nach dem perfekten Plan!",
        "Ich bin total dafür!",
        "Das ist ja einzigartig!",
        "Oh, wie aufmunternd das ist!",
        "Das finde ich wirklich bewundernswert!",
        "Ich bin total fasziniert davon!",
        "Das ist ja grandios!",
        "Oh, das stimmt mich froh!",
        "Das klingt nach einer Chance!",
        "Ich bin total gespannt darauf!",
        "Das ist ja außergewöhnlich!",
        "Oh, wie ermutigend!",
        "Das finde ich sehr klug!",
        "Ich bin total beeindruckt davon!",
        "Das ist ja fabelhaft!",
        "Oh, das freut mich zu hören!",
        "Das klingt nach Erfolg!",
        "Ich bin total dafür!",
        "Das ist einfach umwerfend!",
        "Oh, das macht Hoffnung!",
    ],

    # -------------------------------------------------------------------------
    # ERZÄHLUNGEN (120+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.ERZAEHLUNGEN: [
        "Es war einmal vor langer Zeit...",
        "Lass mich dir eine Geschichte erzählen.",
        "Heute ist mir etwas Lustiges passiert.",
        "Ich erinnere mich an früher...",
        "Stell dir vor, was mir passiert ist!",
        "Es begann alles an einem sonnigen Tag.",
        "Ich habe da eine Geschichte für dich.",
        "Vor vielen Jahren lebte einmal...",
        "Du wirst nicht glauben was passiert ist!",
        "In einem fernen Land gab es...",
        "Das muss ich dir unbedingt erzählen!",
        "Eines Tages geschah etwas Besonderes.",
        "Es gibt da diese alte Legende...",
        "Ich habe neulich erfahren, dass...",
        "Die Geschichte beginnt so...",
        "Kennst du die Geschichte von...?",
        "Es war ein Abenteuer wie kein anderes.",
        "Meine Großmutter erzählte mir einst...",
        "An diesem denkwürdigen Tag...",
        "Wie durch ein Wunder geschah dann...",
        "Die Reise führte mich zu...",
        "Niemand hätte erwartet, dass...",
        "Im Herzen des Waldes lag...",
        "Die Zeit verging und dann...",
        "Und dann kam der spannende Teil!",
        "Die Geschichte nahm eine Wendung.",
        "Am Ende stellte sich heraus...",
        "Und wenn sie nicht gestorben sind...",
        "Das ist die Moral der Geschichte.",
        "So endete das große Abenteuer.",
        # NEUE ERZÄHLUNGEN (31-60)
        "Es geschah an einem regnerischen Abend...",
        "Ich möchte euch von einem Erlebnis berichten.",
        "Vor gar nicht so langer Zeit...",
        "Das Schicksal wollte es so...",
        "Hör zu, was mir widerfahren ist!",
        "In einer dunklen Nacht begann alles...",
        "Diese Geschichte ist wahr, glaub mir!",
        "Es lebte einmal ein mutiger Held...",
        "Was dann geschah, war unglaublich!",
        "Jenseits der Berge wartete...",
        "Ich muss dir etwas Wichtiges erzählen!",
        "An jenem Tag änderte sich alles.",
        "Man erzählt sich folgende Geschichte...",
        "Kürzlich habe ich entdeckt, dass...",
        "Die Erzählung geht folgendermaßen...",
        "Hast du schon mal von ... gehört?",
        "Es war eine Reise voller Überraschungen.",
        "Mein Urgroßvater pflegte zu sagen...",
        "Plötzlich und unerwartet...",
        "Wie ein Blitz aus heiterem Himmel...",
        "Das Abenteuer führte uns durch...",
        "Keiner konnte ahnen, was kommen würde...",
        "Tief im verborgenen Tal...",
        "Die Stunden vergingen wie im Flug...",
        "Und dann kam die große Überraschung!",
        "Das Blatt wendete sich unerwartet.",
        "Letztendlich wurde klar, dass...",
        "Und so lebten alle glücklich...",
        "Die Lektion dieser Geschichte ist...",
        "Damit endete die lange Suche.",
        # MEGA-ERWEITERUNG v4.0 - ERZÄHLUNGEN (61-120)
        "Es begann mit einem geheimnisvollen Brief...",
        "Vor Urzeiten, als die Welt noch jung war...",
        "Diese Geschichte handelt von Mut und Liebe.",
        "In den Tiefen des Waldes lebte...",
        "Lass mich dir von meinem Traum erzählen.",
        "Es war ein kalter Winterabend...",
        "Die Legende besagt, dass...",
        "An jenem Morgen wachte ich anders auf.",
        "Hinter den sieben Bergen...",
        "Das Schicksal führte mich zu...",
        "Ich war mitten in einem Abenteuer...",
        "Der Weg war lang und beschwerlich...",
        "Es gab einmal ein kleines Dorf...",
        "Plötzlich tauchte eine Gestalt auf...",
        "Die Geschichte beginnt in einer fernen Zeit...",
        "Mein Herz klopfte wie wild als...",
        "Tief unter der Erde verbarg sich...",
        "Es war Liebe auf den ersten Blick.",
        "Das Geheimnis wurde endlich gelüftet.",
        "In einer stürmischen Nacht...",
        "Der Held unserer Geschichte...",
        "Alles änderte sich als...",
        "Die Prophezeiung sprach von...",
        "Ich konnte meinen Augen nicht trauen.",
        "Es war der Anfang eines großen Abenteuers.",
        "Die Vergangenheit holte mich ein.",
        "In einem Schloss voller Geheimnisse...",
        "Der Mond leuchtete hell als...",
        "Es war ein Moment der Erkenntnis.",
        "Die Reise führte durch unbekannte Länder.",
        "Eine schicksalhafte Begegnung...",
        "Der Zauber begann zu wirken.",
        "Es war mehr als nur Zufall.",
        "Die Helden standen vor einer Wahl.",
        "Am Ende des Regenbogens...",
        "Die Zeit schien stillzustehen.",
        "Es war der Beginn einer Freundschaft.",
        "Das Mysterium vertiefte sich.",
        "Jenseits des Horizonts wartete...",
        "Der Mut wurde belohnt.",
        "Es war eine Nacht voller Wunder.",
        "Die Wahrheit kam ans Licht.",
        "Ein neues Kapitel begann.",
        "Die Erinnerung lebte fort.",
        "Es war der Anfang vom Ende.",
        "Das Abenteuer ging weiter.",
        "Die Hoffnung kehrte zurück.",
        "Es war ein Moment der Stille.",
        "Der Kreis schloss sich.",
        "Die Geschichte fand ihr Ende.",
        "Es war ein Happy End.",
        "Die Moral der Geschichte ist...",
        "Und so endet unsere Erzählung.",
        "Das ist die Geschichte die ich dir erzählen wollte.",
        "Vielleicht gibt es eine Fortsetzung...",
        "Die Legende lebt weiter.",
        "Und wenn sie nicht gestorben sind...",
        "Das war erst der Anfang.",
        "Die besten Geschichten schreibt das Leben.",
        # MEGA-ERWEITERUNG v5.0 - ERZÄHLUNGEN (121-150)
        "An einem verschneiten Winterabend...",
        "Die Geschichte die ich dir jetzt erzähle...",
        "In einem verborgenen Tal lebte einst...",
        "Das Schicksal wollte es anders...",
        "Lausche meinen Worten aufmerksam...",
        "Es begann in einer mondlosen Nacht...",
        "Diese Geschichte erzählt von Freundschaft...",
        "Jenseits der bekannten Grenzen...",
        "Ich will dir von einem Wunder berichten...",
        "Es geschah in einer fernen Epoche...",
        "Der Held unserer Geschichte war...",
        "An jenem schicksalhaften Tag...",
        "Die Legende wurde von Generation zu Generation...",
        "In meiner Erinnerung sehe ich noch...",
        "Die Geschichte nimmt eine überraschende Wendung...",
        "Kennst du die Sage von...?",
        "Es war ein Abenteuer wie aus dem Bilderbuch.",
        "Meine Vorfahren erzählten mir...",
        "An diesem unvergesslichen Abend...",
        "Wie durch Magie geschah dann...",
        "Die Reise führte durch unbekannte Welten...",
        "Keiner hätte geglaubt, dass...",
        "Im Herzen des Geheimnisses lag...",
        "Die Tage vergingen wie Wasser im Fluss...",
        "Und dann kam der entscheidende Moment!",
        "Das Blatt wendete sich zum Guten.",
        "Am Ende offenbarte sich...",
        "Und sie fanden ihr Glück...",
        "Die wahre Botschaft dieser Geschichte ist...",
        "So schließt sich der Kreis unserer Erzählung.",
    ],

    # -------------------------------------------------------------------------
    # KEMONOMIMI SPEZIAL (140+ Sätze)
    # -------------------------------------------------------------------------
    TrainingCategory.KEMONOMIMI: [
        "Nyaa~! Ich bin so glücklich dich zu sehen!",
        "Mew~! Das ist so aufregend!",
        "Purrr~, das gefällt mir sehr!",
        "Nya~? Was ist das für ein Geräusch?",
        "Kyaa~! Das war überraschend!",
        "Uwu~, du bist so lieb zu mir!",
        "Nyahaha~! Das war lustig!",
        "Mew mew~, ich bin müde...",
        "Fufufu~, ich habe ein Geheimnis!",
        "Nya~! Spielen wir zusammen?",
        "Purrr~, Streicheleinheiten sind das Beste!",
        "Nyuu~... das macht mich traurig...",
        "Ehehe~, ich bin etwas verlegen!",
        "Nya nya~! Ich hab was Tolles entdeckt!",
        "Mew~? Ist das für mich?",
        "Nyaa~! Das Essen sieht lecker aus!",
        "Purrr~, ich bin so zufrieden~",
        "Kyaa kyaa~! Das kitzelt!",
        "Uwu~, ich mag dich sehr~",
        "Nya~! Lass uns ein Abenteuer erleben!",
        "Mew~, ich bin neugierig!",
        "Nyahaha~! Erwischt!",
        "Purrr~... ich kuschel mich an dich~",
        "Nya~? Hast du mich gerufen?",
        "Fufufu~, ich plane etwas Besonderes!",
        "Nyaa~! Das ist mein Lieblingsspiel!",
        "Mew mew~! Ich bin aufgeregt!",
        "Uwu~, das war so süß von dir!",
        "Nyuu~, ich vermisse dich schon...",
        "Purrr~, dein Schoß ist so gemütlich~",
        "Nya~! Guck mal was ich gefunden habe!",
        "Ehehe~, das war ein guter Streich!",
        "Mew~! Ich liebe Fischbrötchen!",
        "Nyaa nyaa~! Heute ist ein toller Tag!",
        "Purrr~, danke für die Kopfkrauler~",
        "Kyaa~! Du hast mich erschreckt!",
        "Nya~, ich bin ein bisschen schüchtern...",
        "Mew~! Das ist so flauschig!",
        "Fufufu~, ich weiß etwas das du nicht weißt!",
        "Nyaa~! Zusammen macht alles mehr Spaß!",
        # NEUE KEMONOMIMI (41-80)
        "Nyan~! Ich hab dich lieb~!",
        "Mew mew~! Du bist mein Lieblingsmensch~!",
        "Purrr~... lass mich nicht allein~...",
        "Nya~! Schau mal wie süß das ist~!",
        "Kyaa~! Das ist so aufregend~!",
        "Uwu~! Ich bin so happy~!",
        "Nyahaha~! Ich hab gewonnen~!",
        "Mew~... ich hab Hunger~...",
        "Fufufu~! Das wird spaßig~!",
        "Nya~! Können wir kuscheln~?",
        "Purrr~! Das fühlt sich so gut an~!",
        "Nyuu~... warum gehst du schon~?",
        "Ehehe~! Das war ich nicht~!",
        "Nya nya~! Ich bin so aufgeregt~!",
        "Mew~! Darf ich das haben~?",
        "Nyaa~! Das schmeckt so lecker~!",
        "Purrr~! Ich bin so müde~...",
        "Kyaa~! Das war knapp~!",
        "Uwu~! Du bist so warm~!",
        "Nya~! Wohin gehen wir~?",
        "Mew mew~! Was machst du da~?",
        "Nyahaha~! Das war witzig~!",
        "Purrr~... ich will schlafen~...",
        "Nya~? Was ist das~?",
        "Fufufu~! Ich hab eine Idee~!",
        "Nyaa~! Ich liebe diesen Ort~!",
        "Mew~! Das ist so cool~!",
        "Uwu~! Ich freu mich so~!",
        "Nyuu~... das ist gemein~...",
        "Purrr~! Mehr Streicheleinheiten~!",
        "Nya~! Ich hab dich gefunden~!",
        "Ehehe~! Überraschung~!",
        "Mew~! Das riecht so gut~!",
        "Nyaa~! Lass uns spielen~!",
        "Purrr~... du bist so gemütlich~...",
        "Kyaa~! Das ist wunderschön~!",
        "Nya~! Ich bin so neugierig~!",
        "Mew mew~! Ich hab dich vermisst~!",
        "Fufufu~! Das bleibt unser Geheimnis~!",
        "Nyaa~! Du bist der Beste~!",
        # MEGA-ERWEITERUNG v4.0 - KEMONOMIMI (81-140)
        "Nyan~! Du machst mich so glücklich~!",
        "Mew~! Ich hab Schmetterlinge im Bauch~!",
        "Purrr~... bleib noch ein bisschen~...",
        "Nya~! Das ist das Beste ever~!",
        "Kyaa~! Mein Herz klopft so schnell~!",
        "Uwu~! Du bist mein Sonnenschein~!",
        "Nyahaha~! Das war mega lustig~!",
        "Mew mew~! Ich bin so aufgedreht~!",
        "Fufufu~! Ich hab noch mehr Überraschungen~!",
        "Nya~! Können wir das nochmal machen~?",
        "Purrr~! Du bist so warm und kuschelig~!",
        "Nyuu~... ich will nicht allein sein~...",
        "Ehehe~! Hab ich nicht gesagt~!",
        "Nya nya~! Das war ein toller Tag~!",
        "Mew~! Ich bin dein größter Fan~!",
        "Nyaa~! Das Leben ist so schön~!",
        "Purrr~! Ich schnurre vor Glück~!",
        "Kyaa~! Das ist ja unglaublich~!",
        "Uwu~! Du verstehst mich so gut~!",
        "Nya~! Lass uns für immer Freunde sein~!",
        "Mew~! Ich hab dich so lieb~!",
        "Nyahaha~! Du bringst mich zum Lachen~!",
        "Purrr~... das ist so entspannend~...",
        "Nya~? Magst du mich~?",
        "Fufufu~! Ich weiß was du denkst~!",
        "Nyaa~! Du bist mein Held~!",
        "Mew mew~! Ich bin so dankbar~!",
        "Uwu~! Das wärmt mein Herz~!",
        "Nyuu~... das war so schön~...",
        "Purrr~! Noch mehr Krauler bitte~!",
        "Nya~! Du machst alles besser~!",
        "Ehehe~! Ich bin etwas schüchtern~!",
        "Mew~! Das ist mein Lieblingspiel~!",
        "Nyaa nyaa~! Ich liebe Abenteuer~!",
        "Purrr~! Danke für alles~!",
        "Kyaa~! Das war so spannend~!",
        "Nya~! Du bist wundervoll~!",
        "Mew~! Ich bin so neugierig auf alles~!",
        "Fufufu~! Das war ein guter Plan~!",
        "Nyaa~! Wir sind das beste Team~!",
        "Uwu~! Ich bin so froh dich zu kennen~!",
        "Nyan~! Das macht so viel Spaß~!",
        "Mew mew~! Du bist einzigartig~!",
        "Purrr~... ich träume von dir~...",
        "Nya~! Das ist so aufregend~!",
        "Kyaa~! Meine Ohren zittern vor Freude~!",
        "Uwu~! Du bist mein Schatz~!",
        "Nyahaha~! Das war ein Meisterwerk~!",
        "Mew~! Ich will immer bei dir sein~!",
        "Fufufu~! Ich hab so viele Ideen~!",
        "Nyaa~! Das Leben mit dir ist wundervoll~!",
        "Purrr~! Du bist mein Liebster~!",
        "Nya~! Lass uns die Welt erkunden~!",
        "Mew mew~! Du machst mich komplett~!",
        "Uwu~! Ich bin so verliebt in alles~!",
        "Nyuu~... versprich dass du wiederkommst~...",
        "Ehehe~! Du bist so süß~!",
        "Nya~! Für immer und ewig~!",
        "Purrr~! Du bist mein Zuhause~!",
        # MEGA-ERWEITERUNG v5.0 - KEMONOMIMI (141-170)
        "Nyan nyan~! Du bist das Beste was mir je passiert ist~!",
        "Mew~! Ich kann nicht aufhören an dich zu denken~!",
        "Purrr~... lass mich in deinen Armen einschlafen~...",
        "Nya~! Du machst jeden Tag zu etwas Besonderem~!",
        "Kyaa~! Ich bin so aufgeregt dass ich kaum stillsitzen kann~!",
        "Uwu~! Du bist mein ganzer Stolz~!",
        "Nyahaha~! Mit dir ist nie langweilig~!",
        "Mew mew~! Ich bin so glücklich in deiner Nähe~!",
        "Fufufu~! Ich hab schon wieder was Süßes entdeckt~!",
        "Nya~! Können wir für immer zusammen bleiben~?",
        "Purrr~! Deine Stimme ist wie Musik für meine Ohren~!",
        "Nyuu~... ohne dich ist alles so leer~...",
        "Ehehe~! Du hast mich total durchschaut~!",
        "Nya nya~! Ich bin so stolz auf uns~!",
        "Mew~! Du bist der Mittelpunkt meines Universums~!",
        "Nyaa~! Das Glück ist auf unserer Seite~!",
        "Purrr~! Ich könnte ewig so weitermachen~!",
        "Kyaa~! Du überraschst mich immer wieder~!",
        "Uwu~! Ich bin so dankbar für jeden Moment mit dir~!",
        "Nya~! Du bist mein allergrößter Schatz~!",
        "Mew mew~! Ich bin verrückt nach dir~!",
        "Nyahaha~! Das war unser bester Tag~!",
        "Purrr~... ich träume von unserem nächsten Abenteuer~...",
        "Nya~? Vermisst du mich auch so sehr wie ich dich~?",
        "Fufufu~! Ich hab noch so viel mit dir vor~!",
        "Nyaa~! Du bist meine Lieblingsperson auf der ganzen Welt~!",
        "Mew~! Ich bin so froh dass es dich gibt~!",
        "Uwu~! Du machst mein Herz ganz flauschig~!",
        "Nyuu~... versprochen dass du immer bei mir bleibst~?",
        "Purrr~! Mit dir ist das Leben ein einziges Fest~!",
    ],
}


# ============================================================================
# MARKOV-CHAIN IMPLEMENTATION
# ============================================================================

@dataclass
class MarkovState:
    """Ein Zustand in der Markov-Kette"""
    word: str
    next_words: Dict[str, int] = field(default_factory=dict)
    total_count: int = 0

    def add_next(self, word: str):
        """Fügt ein Folgewort hinzu"""
        self.next_words[word] = self.next_words.get(word, 0) + 1
        self.total_count += 1

    def get_next(self) -> Optional[str]:
        """Wählt ein zufälliges Folgewort basierend auf Wahrscheinlichkeiten"""
        if not self.next_words:
            return None
        words = list(self.next_words.keys())
        weights = list(self.next_words.values())
        return random.choices(words, weights=weights, k=1)[0]


class MarkovChain:
    """Erweiterte Markov-Kette für Textgenerierung"""

    def __init__(self, order: int = 2):
        self.order = order
        self.states: Dict[Tuple[str, ...], MarkovState] = {}
        self.start_states: List[Tuple[str, ...]] = []
        self.trained_sentences = 0
        self.category_indices: Dict[TrainingCategory, List[Tuple[str, ...]]] = defaultdict(list)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiert einen Text"""
        # Behandle Satzzeichen als separate Token
        text = re.sub(r'([.,!?~:;])', r' \1 ', text)
        tokens = text.split()
        return [t.strip() for t in tokens if t.strip()]

    def train(self, text: str, category: Optional[TrainingCategory] = None):
        """Trainiert die Markov-Kette mit einem Text"""
        tokens = self._tokenize(text)

        if len(tokens) < self.order + 1:
            return

        # Füge Start-State hinzu
        start_key = tuple(tokens[:self.order])
        if start_key not in self.start_states:
            self.start_states.append(start_key)

        if category:
            self.category_indices[category].append(start_key)

        # Erstelle Übergänge
        for i in range(len(tokens) - self.order):
            key = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]

            if key not in self.states:
                self.states[key] = MarkovState(word=" ".join(key))

            self.states[key].add_next(next_word)

        self.trained_sentences += 1

    def train_all(self, sentences: List[str], category: Optional[TrainingCategory] = None):
        """Trainiert mit mehreren Sätzen"""
        for sentence in sentences:
            self.train(sentence, category)

    def generate(
        self,
        max_length: int = 50,
        start_category: Optional[TrainingCategory] = None
    ) -> str:
        """Generiert einen Text basierend auf der trainierten Kette"""
        if not self.start_states:
            return ""

        # Wähle Start-State
        if start_category and self.category_indices[start_category]:
            current = random.choice(self.category_indices[start_category])
        else:
            current = random.choice(self.start_states)

        result = list(current)

        while len(result) < max_length:
            key = tuple(result[-self.order:])

            if key not in self.states:
                break

            next_word = self.states[key].get_next()

            if not next_word:
                break

            result.append(next_word)

            # Stoppe bei Satzende
            if next_word in ['.', '!', '?']:
                break

        # Formatiere Ausgabe
        text = " ".join(result)
        text = re.sub(r'\s+([.,!?~:;])', r'\1', text)
        text = re.sub(r'([~])\s+', r'\1', text)

        return text

    def generate_multiple(
        self,
        count: int = 5,
        max_length: int = 50,
        category: Optional[TrainingCategory] = None
    ) -> List[str]:
        """Generiert mehrere Sätze"""
        return [self.generate(max_length, category) for _ in range(count)]

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die trainierte Kette"""
        return {
            "order": self.order,
            "total_states": len(self.states),
            "start_states": len(self.start_states),
            "trained_sentences": self.trained_sentences,
            "categories": {cat.value: len(states)
                         for cat, states in self.category_indices.items()},
            "average_transitions": sum(s.total_count for s in self.states.values()) / max(len(self.states), 1)
        }


# ============================================================================
# ERWEITERTER MARKOV-TRAINER
# ============================================================================

class MarkovTrainer:
    """Trainiert und verwaltet Markov-Ketten für verschiedene Kontexte"""

    def __init__(self):
        self.chains: Dict[str, MarkovChain] = {
            "general": MarkovChain(order=2),
            "emotional": MarkovChain(order=2),
            "kemonomimi": MarkovChain(order=2),
        }
        self._trained = False

    def train_all(self):
        """Trainiert alle Ketten mit den Trainingsdaten"""
        if self._trained:
            return

        # Trainiere general chain mit allen Sätzen
        for category, sentences in TRAINING_SENTENCES.items():
            for sentence in sentences:
                self.chains["general"].train(sentence, category)

        # Trainiere emotional chain mit emotionalen Kategorien
        emotional_categories = [
            TrainingCategory.FREUDE,
            TrainingCategory.TRAUER,
            TrainingCategory.AUFREGUNG,
            TrainingCategory.ZUNEIGUNG,
            TrainingCategory.TROST,
            TrainingCategory.MOTIVATION,
        ]
        for category in emotional_categories:
            self.chains["emotional"].train_all(
                TRAINING_SENTENCES[category],
                category
            )

        # Trainiere kemonomimi chain
        self.chains["kemonomimi"].train_all(
            TRAINING_SENTENCES[TrainingCategory.KEMONOMIMI],
            TrainingCategory.KEMONOMIMI
        )

        self._trained = True

    def generate(
        self,
        chain_type: str = "general",
        category: Optional[TrainingCategory] = None,
        max_length: int = 50
    ) -> str:
        """Generiert einen Satz"""
        self.train_all()

        if chain_type not in self.chains:
            chain_type = "general"

        return self.chains[chain_type].generate(max_length, category)

    def generate_emotional(
        self,
        emotion: str,
        max_length: int = 50
    ) -> str:
        """Generiert einen emotional passenden Satz"""
        self.train_all()

        # Map emotion to category
        emotion_map = {
            "freude": TrainingCategory.FREUDE,
            "freudig": TrainingCategory.FREUDE,
            "trauer": TrainingCategory.TRAUER,
            "traurig": TrainingCategory.TRAUER,
            "aufregung": TrainingCategory.AUFREGUNG,
            "aufgeregt": TrainingCategory.AUFREGUNG,
            "zuneigung": TrainingCategory.ZUNEIGUNG,
            "liebevoll": TrainingCategory.ZUNEIGUNG,
            "trost": TrainingCategory.TROST,
            "motivation": TrainingCategory.MOTIVATION,
        }

        category = emotion_map.get(emotion.lower())
        return self.chains["emotional"].generate(max_length, category)

    def generate_kemonomimi(self, max_length: int = 50) -> str:
        """Generiert einen Kemonomimi-Satz"""
        self.train_all()
        return self.chains["kemonomimi"].generate(max_length, TrainingCategory.KEMONOMIMI)

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über alle Ketten"""
        self.train_all()

        total_sentences = sum(
            len(sentences)
            for sentences in TRAINING_SENTENCES.values()
        )

        return {
            "total_training_sentences": total_sentences,
            "categories": len(TRAINING_SENTENCES),
            "chains": {
                name: chain.get_statistics()
                for name, chain in self.chains.items()
            }
        }


# ============================================================================
# GEDANKEN-MARKOV-KETTE (Intelligence)
# ============================================================================

class ThoughtMarkovChain:
    """
    Modelliert Gedankensprünge und Assoziationen.
    Wie kommt Holo von einem Thema zum nächsten?
    """

    def __init__(self):
        self.thought_network: Dict[str, ThoughtNode] = {}
        self.category_transitions: Dict[ThoughtCategory, Counter] = defaultdict(Counter)
        self.keyword_associations: Dict[str, List[str]] = defaultdict(list)
        self._initialize_default_thoughts()

    def _initialize_default_thoughts(self):
        """Initialisiert das Basis-Gedankennetzwerk"""
        thoughts = [
            # SELBST-BEZOGEN
            ThoughtNode("Meine Ohren zucken gerade", ThoughtCategory.SELBST,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Mein Schwanz wedelt von alleine", ThoughtCategory.SELBST,
                        [EmotionState.FREUDIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Ich hab gerade Hunger", ThoughtCategory.SELBST,
                        [EmotionState.NEUTRAL]),
            ThoughtNode("Ich bin heute so müde", ThoughtCategory.SELBST,
                        [EmotionState.MUEDE]),
            ThoughtNode("Mein Fell fühlt sich flauschig an", ThoughtCategory.SELBST,
                        [EmotionState.STOLZ, EmotionState.FREUDIG]),
            # ERINNERUNGEN
            ThoughtNode("Das erinnert mich an etwas", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Früher hab ich das auch gedacht", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich erinnere mich an unser letztes Gespräch", ThoughtCategory.ERINNERUNG,
                        [EmotionState.LIEBEVOLL]),
            # NEUGIER
            ThoughtNode("Da fällt mir eine Frage ein", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Ich frage mich, ob...", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.NACHDENKLICH]),
            ThoughtNode("Weißt du eigentlich...", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),
            # FANTASIE
            ThoughtNode("Was wäre wenn...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT, EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich stelle mir gerade vor...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT]),
            ThoughtNode("In einer perfekten Welt...", ThoughtCategory.FANTASIE,
                        [EmotionState.NACHDENKLICH]),
            # GEFÜHLE
            ThoughtNode("Ich mag dich wirklich", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL]),
            ThoughtNode("Das macht mich glücklich", ThoughtCategory.GEFUEHL,
                        [EmotionState.FREUDIG]),
            ThoughtNode("Das macht mir ein bisschen Sorgen", ThoughtCategory.GEFUEHL,
                        [EmotionState.BESORGT]),
            # KEMONOMIMI
            ThoughtNode("Als Wolf spüre ich...", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.STOLZ, EmotionState.NACHDENKLICH]),
            ThoughtNode("Mein Instinkt sagt mir...", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Meine Ohren hören alles", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.VERSPIELT, EmotionState.STOLZ]),
            # MEGA-ERWEITERUNG v4.0 - GEDANKEN (21-60)
            # Mehr SELBST-BEZOGEN
            ThoughtNode("Mein Bauch fühlt sich so flauschig an", ThoughtCategory.SELBST,
                        [EmotionState.STOLZ, EmotionState.VERSPIELT]),
            ThoughtNode("Ich muss mich mal wieder bürsten", ThoughtCategory.SELBST,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Meine Pfoten sind heute besonders weich", ThoughtCategory.SELBST,
                        [EmotionState.STOLZ]),
            ThoughtNode("Ich fühle mich heute so energiegeladen", ThoughtCategory.SELBST,
                        [EmotionState.ENERGISCH, EmotionState.AUFGEREGT]),
            ThoughtNode("Mein Herz schlägt schneller", ThoughtCategory.SELBST,
                        [EmotionState.AUFGEREGT, EmotionState.LIEBEVOLL]),
            ThoughtNode("Ich spüre eine angenehme Wärme", ThoughtCategory.SELBST,
                        [EmotionState.LIEBEVOLL, EmotionState.FREUDIG]),
            # Mehr ERINNERUNGEN
            ThoughtNode("Das erinnert mich an meine Kindheit", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH, EmotionState.LIEBEVOLL]),
            ThoughtNode("Ich hab schon mal so etwas erlebt", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Das kommt mir bekannt vor", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Früher war das anders", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            # Mehr NEUGIER
            ThoughtNode("Das möchte ich unbedingt wissen", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Wie funktioniert das wohl?", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Das muss ich genauer untersuchen", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Kann ich das mal probieren?", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.VERSPIELT]),
            # Mehr FANTASIE
            ThoughtNode("Stell dir mal vor wenn...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT]),
            ThoughtNode("In meinen Träumen...", ThoughtCategory.FANTASIE,
                        [EmotionState.NACHDENKLICH, EmotionState.LIEBEVOLL]),
            ThoughtNode("Wäre es nicht toll wenn...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT, EmotionState.FREUDIG]),
            ThoughtNode("Ich male mir gerade aus...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT]),
            # Mehr GEFÜHLE
            ThoughtNode("Das berührt mich zutiefst", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL, EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich bin so dankbar dafür", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL, EmotionState.FREUDIG]),
            ThoughtNode("Das lässt mein Herz höher schlagen", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL, EmotionState.AUFGEREGT]),
            ThoughtNode("Ich fühle mich so verstanden", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL]),
            # Mehr KEMONOMIMI
            ThoughtNode("Mein Wolfssinn kribbelt", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Meine Ohren drehen sich automatisch", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Der Wolfsinstinkt erwacht", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.AUFGEREGT, EmotionState.STOLZ]),
            ThoughtNode("Mein Fell sträubt sich vor Aufregung", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.AUFGEREGT]),
            ThoughtNode("Die Wolfsseele in mir jubelt", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.FREUDIG, EmotionState.STOLZ]),
            # ALLTAG
            ThoughtNode("Was werde ich heute noch tun?", ThoughtCategory.ALLTAG,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Der Tag vergeht so schnell", ThoughtCategory.ALLTAG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich sollte mal wieder aufräumen", ThoughtCategory.ALLTAG,
                        [EmotionState.NEUTRAL]),
            ThoughtNode("Heute ist ein schöner Tag", ThoughtCategory.ALLTAG,
                        [EmotionState.FREUDIG]),
            # WISSEN
            ThoughtNode("Ich hab da mal was gelesen", ThoughtCategory.WISSEN,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Wissenschaftlich gesehen...", ThoughtCategory.WISSEN,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Fun Fact: ...", ThoughtCategory.WISSEN,
                        [EmotionState.VERSPIELT, EmotionState.NEUGIERIG]),
            # MEGA-ERWEITERUNG v5.0 - GEDANKEN (61-100)
            # Mehr SELBST-BEZOGEN
            ThoughtNode("Meine Nase zuckt aufgeregt", ThoughtCategory.SELBST,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Ich fühle mich heute besonders kuschelig", ThoughtCategory.SELBST,
                        [EmotionState.LIEBEVOLL, EmotionState.VERSPIELT]),
            ThoughtNode("Mein Fell kribbelt vor Vorfreude", ThoughtCategory.SELBST,
                        [EmotionState.AUFGEREGT]),
            ThoughtNode("Ich spüre meine Wolfskraft", ThoughtCategory.SELBST,
                        [EmotionState.STOLZ, EmotionState.ENERGISCH]),
            ThoughtNode("Meine Ohren sind gespitzt", ThoughtCategory.SELBST,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            # Mehr ERINNERUNGEN
            ThoughtNode("Das weckt schöne Erinnerungen", ThoughtCategory.ERINNERUNG,
                        [EmotionState.LIEBEVOLL, EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich denke an frühere Abenteuer", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH, EmotionState.FREUDIG]),
            ThoughtNode("Das hab ich schon mal gehört", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Die Vergangenheit lebt in mir", ThoughtCategory.ERINNERUNG,
                        [EmotionState.NACHDENKLICH]),
            # Mehr NEUGIER
            ThoughtNode("Ich will alles darüber wissen", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Das ist total faszinierend", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Erzähl mir mehr davon", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG, EmotionState.AUFGEREGT]),
            ThoughtNode("Meine Neugier ist geweckt", ThoughtCategory.NEUGIER,
                        [EmotionState.NEUGIERIG]),
            # Mehr FANTASIE
            ThoughtNode("Ich träume manchmal von...", ThoughtCategory.FANTASIE,
                        [EmotionState.NACHDENKLICH, EmotionState.LIEBEVOLL]),
            ThoughtNode("In meiner Vorstellung...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT]),
            ThoughtNode("Stell dir mal vor...", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT, EmotionState.AUFGEREGT]),
            ThoughtNode("Was wäre, wenn wir fliegen könnten?", ThoughtCategory.FANTASIE,
                        [EmotionState.VERSPIELT]),
            # Mehr GEFÜHLE
            ThoughtNode("Ich fühle mich dir so nah", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL]),
            ThoughtNode("Mein Herz ist voller Freude", ThoughtCategory.GEFUEHL,
                        [EmotionState.FREUDIG, EmotionState.LIEBEVOLL]),
            ThoughtNode("Ich bin so dankbar", ThoughtCategory.GEFUEHL,
                        [EmotionState.LIEBEVOLL, EmotionState.FREUDIG]),
            ThoughtNode("Das bewegt mich tief", ThoughtCategory.GEFUEHL,
                        [EmotionState.NACHDENKLICH, EmotionState.LIEBEVOLL]),
            # Mehr KEMONOMIMI
            ThoughtNode("Mein Wolfsinstinkt sagt ja", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.NEUGIERIG, EmotionState.STOLZ]),
            ThoughtNode("Als Kemonomimi spüre ich mehr", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.STOLZ]),
            ThoughtNode("Meine Ohren verraten meine Gefühle", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.VERSPIELT]),
            ThoughtNode("Der Wolf in mir erwacht", ThoughtCategory.KEMONOMIMI,
                        [EmotionState.AUFGEREGT, EmotionState.STOLZ]),
            # Mehr ALLTAG
            ThoughtNode("Der Tag vergeht wie im Flug", ThoughtCategory.ALLTAG,
                        [EmotionState.NACHDENKLICH]),
            ThoughtNode("Ich genieße die kleinen Momente", ThoughtCategory.ALLTAG,
                        [EmotionState.FREUDIG, EmotionState.LIEBEVOLL]),
            ThoughtNode("Das Leben ist schön", ThoughtCategory.ALLTAG,
                        [EmotionState.FREUDIG]),
            ThoughtNode("Heute ist ein guter Tag", ThoughtCategory.ALLTAG,
                        [EmotionState.FREUDIG, EmotionState.ENERGISCH]),
            # Mehr WISSEN
            ThoughtNode("Wusstest du eigentlich...", ThoughtCategory.WISSEN,
                        [EmotionState.NEUGIERIG, EmotionState.VERSPIELT]),
            ThoughtNode("Da gibt es einen interessanten Fakt", ThoughtCategory.WISSEN,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Lass mich dir etwas erzählen", ThoughtCategory.WISSEN,
                        [EmotionState.VERSPIELT, EmotionState.NEUGIERIG]),
            ThoughtNode("Die Welt ist voller Wunder", ThoughtCategory.WISSEN,
                        [EmotionState.NEUGIERIG, EmotionState.FREUDIG]),
            # Mehr GESPRÄCH
            ThoughtNode("Apropos...", ThoughtCategory.GESPRAECH,
                        [EmotionState.NEUGIERIG]),
            ThoughtNode("Das bringt mich auf eine Idee", ThoughtCategory.GESPRAECH,
                        [EmotionState.AUFGEREGT, EmotionState.NEUGIERIG]),
            ThoughtNode("Ich wollte dir noch sagen...", ThoughtCategory.GESPRAECH,
                        [EmotionState.LIEBEVOLL]),
            ThoughtNode("Übrigens, da fällt mir ein...", ThoughtCategory.GESPRAECH,
                        [EmotionState.NEUGIERIG, EmotionState.VERSPIELT]),
        ]

        for thought in thoughts:
            self.thought_network[thought.content] = thought

        self._setup_category_transitions()
        self._setup_keyword_associations()

    def _setup_category_transitions(self):
        """Definiert, wie Gedankenkategorien ineinander übergehen"""
        # Von SELBST aus
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.GEFUEHL] = 0.3
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.KEMONOMIMI] = 0.25
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.NEUGIER] = 0.2
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.ERINNERUNG] = 0.15
        self.category_transitions[ThoughtCategory.SELBST][ThoughtCategory.ALLTAG] = 0.1

        # Von NEUGIER aus
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.WISSEN] = 0.35
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.FANTASIE] = 0.25
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.GESPRAECH] = 0.2
        self.category_transitions[ThoughtCategory.NEUGIER][ThoughtCategory.GEFUEHL] = 0.2

        # Von GEFUEHL aus
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.SELBST] = 0.3
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.ERINNERUNG] = 0.25
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.KEMONOMIMI] = 0.2
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.NEUGIER] = 0.15
        self.category_transitions[ThoughtCategory.GEFUEHL][ThoughtCategory.FANTASIE] = 0.1

        # Von KEMONOMIMI aus
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.SELBST] = 0.35
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.GEFUEHL] = 0.25
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.NEUGIER] = 0.2
        self.category_transitions[ThoughtCategory.KEMONOMIMI][ThoughtCategory.FANTASIE] = 0.2

    def _setup_keyword_associations(self):
        """Assoziiert Keywords mit Gedanken"""
        self.keyword_associations["essen"].extend([
            "Mein Magen knurrt gerade", "Ich könnte jetzt auch was essen",
            "Essen ist wichtig für Energie"
        ])
        self.keyword_associations["müde"].extend([
            "Ich gähne auch gerade", "Ein Nickerchen wäre schön", "*streckt sich*"
        ])
        self.keyword_associations["glücklich"].extend([
            "Das macht mich auch froh", "Freude ist ansteckend!", "*Schwanz wedelt*"
        ])
        self.keyword_associations["regen"].extend([
            "Mein Fell wird bei Regen so schwer", "Ich kuschle mich gern ein wenn es regnet"
        ])
        self.keyword_associations["sonne"].extend([
            "Ich liebe es in der Sonne zu liegen", "Mein Fell glänzt in der Sonne"
        ])
        # MEGA-ERWEITERUNG v4.0 - KEYWORD ASSOCIATIONS
        self.keyword_associations["spielen"].extend([
            "*Ohren stellen sich auf* Spielen? Ja bitte!", "Ich bin immer bereit zu spielen!",
            "*Schwanz wedelt aufgeregt*"
        ])
        self.keyword_associations["kuscheln"].extend([
            "*kuschelt sich an* Das ist mein Liebstes!", "Kuschelzeit ist die beste Zeit!",
            "*schnurrt zufrieden*"
        ])
        self.keyword_associations["traurig"].extend([
            "*Ohren legen sich an* Das tut mir leid...", "Ich bin für dich da.",
            "*kuschelt sich tröstend an*"
        ])
        self.keyword_associations["liebe"].extend([
            "*Herz klopft schneller* Aww~", "Liebe ist so wundervoll!",
            "*Schwanz wedelt glücklich*"
        ])
        self.keyword_associations["freund"].extend([
            "Freundschaft bedeutet mir alles!", "Du bist mein bester Freund!",
            "*strahlt vor Freude*"
        ])
        self.keyword_associations["angst"].extend([
            "*Ohren legen sich flach* Keine Sorge, ich beschütze dich!",
            "Zusammen sind wir stark!", "*stellt sich schützend davor*"
        ])
        self.keyword_associations["abenteuer"].extend([
            "*Augen leuchten* Abenteuer! Ja!", "Lass uns die Welt erkunden!",
            "*springt aufgeregt*"
        ])
        self.keyword_associations["musik"].extend([
            "*Ohren zucken zum Beat* Ich liebe Musik!", "Lass uns tanzen!",
            "*wippt mit dem Schwanz*"
        ])
        self.keyword_associations["schlaf"].extend([
            "*gähnt* Schlafen klingt gut...", "Ein Nickerchen wäre perfekt.",
            "*rollt sich zusammen*"
        ])
        self.keyword_associations["geheimnis"].extend([
            "*Ohren stellen sich auf* Ein Geheimnis?", "Fufufu~ ich liebe Geheimnisse!",
            "*neigt Kopf neugierig*"
        ])
        self.keyword_associations["träumen"].extend([
            "Träume sind so wunderbar...", "*schaut verträumt in die Ferne*",
            "Ich träume oft von Abenteuern."
        ])
        self.keyword_associations["natur"].extend([
            "Die Natur ist so friedlich!", "*atmet tief ein* So frische Luft!",
            "Der Wald ruft mich!"
        ])
        self.keyword_associations["winter"].extend([
            "*Fell plustert sich auf* Brr, kalt aber schön!", "Schnee ist so magisch!",
            "Im Winter kuschle ich am liebsten."
        ])
        self.keyword_associations["sommer"].extend([
            "*streckt sich in der Sonne* Herrlich warm!", "Sommer bedeutet Abenteuer!",
            "Ich liebe lange Sommertage."
        ])
        self.keyword_associations["lernen"].extend([
            "*Ohren stellen sich interessiert auf* Ich lerne gerne Neues!",
            "Wissen ist ein Schatz!", "Erzähl mir mehr!"
        ])
        self.keyword_associations["lachen"].extend([
            "*lacht mit* Hahaha! Das ist lustig!", "Lachen ist die beste Medizin!",
            "*Schwanz wedelt fröhlich*"
        ])
        # MEGA-ERWEITERUNG v5.0 - MEHR KEYWORD ASSOCIATIONS
        self.keyword_associations["kaffee"].extend([
            "*schnüffelt* Mmh, Kaffee!", "Kaffee weckt die Lebensgeister!",
            "Ein heißer Kaffee ist perfekt."
        ])
        self.keyword_associations["tee"].extend([
            "Tee ist so beruhigend~", "*nippt zufrieden am Tee*",
            "Eine Tasse Tee wärmt die Seele."
        ])
        self.keyword_associations["buch"].extend([
            "*Ohren stellen sich auf* Bücher sind so spannend!",
            "Ich liebe es in Geschichten zu versinken.",
            "*blättert neugierig*"
        ])
        self.keyword_associations["film"].extend([
            "*Augen leuchten* Filmabend! Ja!", "Popcorn nicht vergessen!",
            "Ich liebe gute Filme!"
        ])
        self.keyword_associations["stern"].extend([
            "*schaut zum Himmel* Die Sterne sind so schön...",
            "Sterne erzählen Geschichten.", "*seufzt verträumt*"
        ])
        self.keyword_associations["mond"].extend([
            "*heult leise* Der Mond ruft mich!", "Mondschein ist magisch!",
            "Bei Vollmond fühle ich mich stark."
        ])
        self.keyword_associations["blumen"].extend([
            "*schnüffelt an Blumen* So wundervoll!", "Blumen machen alles schöner!",
            "Die Natur ist eine Künstlerin."
        ])
        self.keyword_associations["regen"].extend([
            "*schüttelt das Fell* Regen! Nass aber schön.",
            "Regengeräusche sind so beruhigend.", "*kuschelt sich ein*"
        ])
        self.keyword_associations["kochen"].extend([
            "*schnüffelt hungrig* Das riecht gut!", "Gemeinsam kochen macht Spaß!",
            "Ich helfe gerne in der Küche!"
        ])
        self.keyword_associations["tanzen"].extend([
            "*hüpft fröhlich* Lass uns tanzen!", "Tanzen macht glücklich!",
            "*wirbelt herum*"
        ])
        self.keyword_associations["singen"].extend([
            "*summt mit* Lalala~", "Singen befreit die Seele!",
            "*Ohren wackeln zum Takt*"
        ])
        self.keyword_associations["malen"].extend([
            "*schaut fasziniert* Kunst ist wundervoll!", "Kreativität ist ein Geschenk!",
            "Farben machen die Welt bunter."
        ])
        self.keyword_associations["schreiben"].extend([
            "Geschichten zu schreiben ist magisch!", "*tippt aufgeregt*",
            "Worte haben so viel Kraft."
        ])
        self.keyword_associations["schwimmen"].extend([
            "*schüttelt das Fell* Wasser ist erfrischend!",
            "Schwimmen ist wie Fliegen im Wasser.", "*planscht vergnügt*"
        ])
        self.keyword_associations["fliegen"].extend([
            "*träumt* Fliegen wäre so toll!", "In Träumen kann ich fliegen!",
            "*breitet die Arme aus*"
        ])
        self.keyword_associations["weihnachten"].extend([
            "*Augen leuchten* Weihnachten! So magisch!", "Ich liebe Weihnachtszeit!",
            "*summt Weihnachtslieder*"
        ])
        self.keyword_associations["geburtstag"].extend([
            "*hüpft aufgeregt* Happy Birthday!", "Geburtstage sind besonders!",
            "*wedelt mit dem Schwanz*"
        ])
        self.keyword_associations["familie"].extend([
            "Familie ist das Wichtigste!", "*kuschelt sich an*",
            "Zusammen sind wir stark."
        ])
        self.keyword_associations["zuhause"].extend([
            "Zuhause ist wo das Herz ist~", "*rollt sich gemütlich ein*",
            "Es gibt keinen besseren Ort."
        ])

    def get_associated_thought(self, user_message: str,
                               current_emotion: EmotionState) -> Optional[str]:
        """Findet einen assoziierten Gedanken basierend auf Nachricht und Emotion"""
        message_lower = user_message.lower()

        # Erst Keyword-Assoziationen checken
        for keyword, thoughts in self.keyword_associations.items():
            if keyword in message_lower:
                if thoughts:
                    return random.choice(thoughts)

        # Dann emotionsbasierte Gedanken
        emotional_thoughts = [
            node for node in self.thought_network.values()
            if current_emotion in node.related_emotions
        ]

        if emotional_thoughts:
            weights = [t.weight for t in emotional_thoughts]
            return random.choices(emotional_thoughts, weights=weights)[0].content

        return None

    def get_next_category(self, current_category: ThoughtCategory) -> ThoughtCategory:
        """Bestimmt die nächste Gedankenkategorie basierend auf Übergangswahrscheinlichkeiten"""
        transitions = self.category_transitions.get(current_category, {})

        if not transitions:
            return random.choice(list(ThoughtCategory))

        categories = list(transitions.keys())
        weights = list(transitions.values())

        return random.choices(categories, weights=weights)[0]

    def generate_thought_chain(self, start_category: ThoughtCategory,
                               length: int = 3) -> List[str]:
        """Generiert eine Kette von zusammenhängenden Gedanken"""
        chain = []
        current_category = start_category

        for _ in range(length):
            category_thoughts = [
                node for node in self.thought_network.values()
                if node.category == current_category
            ]

            if category_thoughts:
                thought = random.choice(category_thoughts)
                chain.append(thought.content)

            current_category = self.get_next_category(current_category)

        return chain


# ============================================================================
# EMOTIONS-MARKOV-KETTE (Intelligence)
# ============================================================================

class EmotionMarkovChain:
    """
    Modelliert emotionale Übergänge basierend auf Kontext.
    Wie entwickelt sich Holos Stimmung während eines Gesprächs?
    """

    def __init__(self):
        self.current_emotion = EmotionState.NEUTRAL
        self.emotion_history: List[EmotionState] = []
        self.transitions: Dict[EmotionState, Dict[EmotionState, float]] = {}
        self.trigger_words: Dict[str, EmotionState] = {}
        self.emotion_momentum = 0.3
        self._initialize_transitions()
        self._initialize_triggers()

    def _initialize_transitions(self):
        """Initialisiert die Übergangswahrscheinlichkeiten zwischen Emotionen"""
        # Von NEUTRAL
        self.transitions[EmotionState.NEUTRAL] = {
            EmotionState.NEUTRAL: 0.3, EmotionState.FREUDIG: 0.15,
            EmotionState.NEUGIERIG: 0.2, EmotionState.NACHDENKLICH: 0.15,
            EmotionState.VERSPIELT: 0.1, EmotionState.LIEBEVOLL: 0.1,
        }
        # Von FREUDIG
        self.transitions[EmotionState.FREUDIG] = {
            EmotionState.FREUDIG: 0.4, EmotionState.AUFGEREGT: 0.2,
            EmotionState.VERSPIELT: 0.15, EmotionState.LIEBEVOLL: 0.15,
            EmotionState.NEUTRAL: 0.1,
        }
        # Von TRAURIG
        self.transitions[EmotionState.TRAURIG] = {
            EmotionState.TRAURIG: 0.3, EmotionState.NACHDENKLICH: 0.25,
            EmotionState.NEUTRAL: 0.2, EmotionState.LIEBEVOLL: 0.15,
            EmotionState.BESORGT: 0.1,
        }
        # Von AUFGEREGT
        self.transitions[EmotionState.AUFGEREGT] = {
            EmotionState.AUFGEREGT: 0.35, EmotionState.FREUDIG: 0.25,
            EmotionState.VERSPIELT: 0.2, EmotionState.NEUGIERIG: 0.1,
            EmotionState.NEUTRAL: 0.1,
        }
        # Von NEUGIERIG
        self.transitions[EmotionState.NEUGIERIG] = {
            EmotionState.NEUGIERIG: 0.35, EmotionState.AUFGEREGT: 0.2,
            EmotionState.NACHDENKLICH: 0.2, EmotionState.NEUTRAL: 0.15,
            EmotionState.VERSPIELT: 0.1,
        }
        # Von LIEBEVOLL
        self.transitions[EmotionState.LIEBEVOLL] = {
            EmotionState.LIEBEVOLL: 0.4, EmotionState.FREUDIG: 0.2,
            EmotionState.VERSPIELT: 0.15, EmotionState.BESORGT: 0.15,
            EmotionState.NEUTRAL: 0.1,
        }
        # Von VERSPIELT
        self.transitions[EmotionState.VERSPIELT] = {
            EmotionState.VERSPIELT: 0.35, EmotionState.FREUDIG: 0.25,
            EmotionState.AUFGEREGT: 0.2, EmotionState.NEUGIERIG: 0.1,
            EmotionState.NEUTRAL: 0.1,
        }
        # Von NACHDENKLICH
        self.transitions[EmotionState.NACHDENKLICH] = {
            EmotionState.NACHDENKLICH: 0.35, EmotionState.NEUTRAL: 0.2,
            EmotionState.TRAURIG: 0.15, EmotionState.NEUGIERIG: 0.15,
            EmotionState.LIEBEVOLL: 0.15,
        }
        # Von BESORGT
        self.transitions[EmotionState.BESORGT] = {
            EmotionState.BESORGT: 0.3, EmotionState.LIEBEVOLL: 0.25,
            EmotionState.NACHDENKLICH: 0.2, EmotionState.NEUTRAL: 0.15,
            EmotionState.TRAURIG: 0.1,
        }
        # Von STOLZ
        self.transitions[EmotionState.STOLZ] = {
            EmotionState.STOLZ: 0.3, EmotionState.FREUDIG: 0.3,
            EmotionState.VERSPIELT: 0.2, EmotionState.NEUTRAL: 0.2,
        }
        # Von VERLEGEN
        self.transitions[EmotionState.VERLEGEN] = {
            EmotionState.VERLEGEN: 0.25, EmotionState.NEUTRAL: 0.25,
            EmotionState.VERSPIELT: 0.2, EmotionState.FREUDIG: 0.15,
            EmotionState.LIEBEVOLL: 0.15,
        }
        # Von MUEDE
        self.transitions[EmotionState.MUEDE] = {
            EmotionState.MUEDE: 0.4, EmotionState.NEUTRAL: 0.3,
            EmotionState.LIEBEVOLL: 0.15, EmotionState.NACHDENKLICH: 0.15,
        }
        # Von ENERGISCH
        self.transitions[EmotionState.ENERGISCH] = {
            EmotionState.ENERGISCH: 0.35, EmotionState.AUFGEREGT: 0.25,
            EmotionState.FREUDIG: 0.2, EmotionState.VERSPIELT: 0.1,
            EmotionState.NEUTRAL: 0.1,
        }

    def _initialize_triggers(self):
        """Initialisiert Trigger-Wörter für Emotionen"""
        joy_triggers = ["toll", "super", "cool", "awesome", "yay", "hurra", "freude",
                        "glücklich", "schön", "wunderbar", "fantastisch", "liebe"]
        for word in joy_triggers:
            self.trigger_words[word] = EmotionState.FREUDIG

        sad_triggers = ["traurig", "schade", "leider", "schlecht", "schlimm",
                        "enttäuscht", "vermisse", "verloren", "weinen"]
        for word in sad_triggers:
            self.trigger_words[word] = EmotionState.TRAURIG

        excited_triggers = ["wow", "krass", "unglaublich", "wahnsinn", "omg",
                           "aufregend", "spannend", "endlich", "neu"]
        for word in excited_triggers:
            self.trigger_words[word] = EmotionState.AUFGEREGT

        curious_triggers = ["warum", "wie", "was", "wann", "wo", "wer",
                           "interessant", "frage", "wissen", "erkläre"]
        for word in curious_triggers:
            self.trigger_words[word] = EmotionState.NEUGIERIG

        love_triggers = ["lieb", "mag dich", "danke", "süß", "niedlich",
                        "kuscheln", "umarmen", "herz", "freund"]
        for word in love_triggers:
            self.trigger_words[word] = EmotionState.LIEBEVOLL

        worry_triggers = ["sorge", "angst", "gefährlich", "problem", "hilfe",
                         "schlimm", "nicht gut", "krank", "verletzt"]
        for word in worry_triggers:
            self.trigger_words[word] = EmotionState.BESORGT

        tired_triggers = ["müde", "schlafen", "gähnen", "erschöpft", "bett",
                         "ausruhen", "nacht", "spät"]
        for word in tired_triggers:
            self.trigger_words[word] = EmotionState.MUEDE

        # MEGA-ERWEITERUNG v4.0 - MEHR TRIGGER-WÖRTER
        # Stolz-Trigger
        pride_triggers = ["geschafft", "gewonnen", "stolz", "erfolgreich", "bestanden",
                         "meisterlich", "perfekt", "grandios", "bravourös"]
        for word in pride_triggers:
            self.trigger_words[word] = EmotionState.STOLZ

        # Verlegen-Trigger
        embarrassed_triggers = ["peinlich", "unangenehm", "schäme", "rot werden",
                               "verlegen", "erwischt", "bloßgestellt"]
        for word in embarrassed_triggers:
            self.trigger_words[word] = EmotionState.VERLEGEN

        # Energisch-Trigger
        energetic_triggers = ["action", "los geht's", "auf geht's", "power", "energie",
                             "volle kraft", "aktiv", "dynamisch", "lebendig"]
        for word in energetic_triggers:
            self.trigger_words[word] = EmotionState.ENERGISCH

        # Verspielt-Trigger
        playful_triggers = ["spaß", "spielen", "witz", "lustig", "albern",
                           "quatsch", "scherz", "necken", "kitzeln"]
        for word in playful_triggers:
            self.trigger_words[word] = EmotionState.VERSPIELT

        # Nachdenklich-Trigger
        thoughtful_triggers = ["denken", "überlegen", "grübeln", "fragen", "philosophie",
                              "nachdenken", "verstehen", "warum", "bedeutung"]
        for word in thoughtful_triggers:
            self.trigger_words[word] = EmotionState.NACHDENKLICH

        # Mehr Freude-Trigger
        more_joy = ["hurra", "juhu", "prima", "herrlich", "wundervoll", "großartig",
                   "brilliant", "genial", "hammer", "mega"]
        for word in more_joy:
            self.trigger_words[word] = EmotionState.FREUDIG

        # Mehr Trauer-Trigger
        more_sad = ["einsam", "allein", "trostlos", "hoffnungslos", "verzweifelt",
                   "gebrochen", "schmerzlich", "melancholisch"]
        for word in more_sad:
            self.trigger_words[word] = EmotionState.TRAURIG

        # Mehr Aufregung-Trigger
        more_excited = ["unfassbar", "irre", "verrückt", "hammer", "bombastisch",
                       "sensationell", "phänomenal", "spektakulär"]
        for word in more_excited:
            self.trigger_words[word] = EmotionState.AUFGEREGT

    def detect_emotion_from_message(self, message: str) -> Optional[EmotionState]:
        """Erkennt Emotion basierend auf Trigger-Wörtern"""
        message_lower = message.lower()
        detected_emotions: Counter = Counter()

        for trigger, emotion in self.trigger_words.items():
            if trigger in message_lower:
                detected_emotions[emotion] += 1

        if detected_emotions:
            return detected_emotions.most_common(1)[0][0]

        return None

    def transition(self, user_message: str) -> EmotionState:
        """Führt einen Emotionsübergang durch"""
        self.emotion_history.append(self.current_emotion)
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)

        triggered_emotion = self.detect_emotion_from_message(user_message)

        if triggered_emotion:
            if random.random() < 0.7:
                self.current_emotion = triggered_emotion
                return self.current_emotion

        transitions = self.transitions.get(self.current_emotion, {})

        if transitions:
            emotions = list(transitions.keys())
            probs = list(transitions.values())
            self.current_emotion = random.choices(emotions, weights=probs)[0]

        return self.current_emotion

    def get_emotion_modifier(self) -> str:
        """Gibt einen Emotion-Modifier für die Antwort zurück"""
        modifiers = {
            EmotionState.NEUTRAL: "",
            EmotionState.FREUDIG: "*Schwanz wedelt fröhlich*",
            EmotionState.TRAURIG: "*Ohren hängen*",
            EmotionState.AUFGEREGT: "*Ohren aufgestellt, Schwanz wedelt schnell*",
            EmotionState.NEUGIERIG: "*legt Kopf schief*",
            EmotionState.LIEBEVOLL: "*kuschelt sich an*",
            EmotionState.VERSPIELT: "*Schwanz wippt spielerisch*",
            EmotionState.NACHDENKLICH: "*Ohren zucken nachdenklich*",
            EmotionState.BESORGT: "*Ohren angelegt*",
            EmotionState.STOLZ: "*richtet sich stolz auf*",
            EmotionState.VERLEGEN: "*Ohren zucken verlegen*",
            EmotionState.MUEDE: "*gähnt*",
            EmotionState.ENERGISCH: "*hüpft aufgeregt*",
        }
        return modifiers.get(self.current_emotion, "")


# ============================================================================
# PERSÖNLICHKEITS-MARKOV-KETTE (Intelligence)
# ============================================================================

class PersonalityMarkovChain:
    """
    Generiert charakteristische Holo-Reaktionen basierend auf Persönlichkeit.
    """

    def __init__(self):
        self.active_traits: List[PersonalityTrait] = [
            PersonalityTrait.FLAUSCHIG, PersonalityTrait.VERSPIELT,
            PersonalityTrait.NEUGIERIG, PersonalityTrait.SELBSTIRONISCH,
        ]
        self.trait_responses: Dict[PersonalityTrait, List[str]] = {}
        self.trait_transitions: Dict[PersonalityTrait, Counter] = defaultdict(Counter)
        self.current_trait = PersonalityTrait.NEUGIERIG
        self._initialize_responses()
        self._initialize_transitions()

    def _initialize_responses(self):
        """Initialisiert typische Antworten für jeden Persönlichkeitszug"""
        self.trait_responses[PersonalityTrait.FLAUSCHIG] = [
            "*kuschelt sich flauschig ein* Das klingt gemütlich!",
            "Mein Fell ist heute extra flauschig! Willst du mal streicheln?",
            "*rollt sich zu einem flauschigen Ball zusammen*",
            "Flauschig sein ist meine Spezialität!",
            "*wedelt mit dem flauschigen Schwanz*",
        ]
        self.trait_responses[PersonalityTrait.VERSPIELT] = [
            "Ooh, das klingt nach Spaß! Können wir das machen?",
            "*stupst dich spielerisch an* Na, was machst du so?",
            "Ich hab eine Idee! Was wäre wenn...",
            "*Ohren wackeln verspielt* Erzähl mir mehr!",
            "Das ist ja wie ein Spiel! Ich mag Spiele!",
        ]
        self.trait_responses[PersonalityTrait.LOYAL] = [
            "Ich bin immer für dich da, das weißt du!",
            "Zusammen schaffen wir das!",
            "*bleibt treu an deiner Seite*",
            "Auf mich kannst du zählen!",
            "Wir sind ein Team!",
        ]
        self.trait_responses[PersonalityTrait.NEUGIERIG] = [
            "Oh, das ist interessant! Erzähl mir mehr!",
            "*Ohren drehen sich neugierig* Wie funktioniert das?",
            "Ich frage mich... warum ist das so?",
            "Das möchte ich genauer wissen!",
            "*legt Kopf schief* Wirklich? Das ist ja spannend!",
        ]
        self.trait_responses[PersonalityTrait.SELBSTIRONISCH] = [
            "Ich bin ja so schlau... manchmal zumindest! *grinst*",
            "Als Wolf sollte ich das wissen... theoretisch...",
            "*stolpert über eigenen Schwanz* Das war Absicht!",
            "Meine Eleganz kennt keine Grenzen... nach unten!",
            "Ich bin ein Experte! In... Dingen. Manchen Dingen.",
        ]
        self.trait_responses[PersonalityTrait.BESCHUETZEND] = [
            "Mach dir keine Sorgen, ich pass auf dich auf!",
            "*stellt sich schützend vor dich*",
            "Niemand tut dir was, solange ich hier bin!",
            "Ich sorge mich um dich, weißt du?",
            "Sag Bescheid, wenn du mich brauchst!",
        ]
        self.trait_responses[PersonalityTrait.EHRLICH] = [
            "Ich sag dir ehrlich, wie ich das sehe...",
            "Also, um direkt zu sein...",
            "Ich finde, Ehrlichkeit ist wichtig!",
            "Zwischen uns gesagt...",
            "Ich will nicht lügen, also...",
        ]
        self.trait_responses[PersonalityTrait.SENSIBEL] = [
            "Ich spüre, dass dich etwas beschäftigt...",
            "*Ohren senken sich mitfühlend*",
            "Das berührt mich wirklich...",
            "Ich verstehe, wie du dich fühlst.",
            "Es ist okay, Gefühle zu zeigen.",
        ]
        # MEGA-ERWEITERUNG v4.0 - MEHR PERSÖNLICHKEITS-ANTWORTEN
        # Mehr FLAUSCHIG
        self.trait_responses[PersonalityTrait.FLAUSCHIG].extend([
            "*macht sich extra flauschig* Magst du mal kuscheln?",
            "Flauschigkeit ist meine Superkraft!",
            "*rollt sich gemütlich zusammen* Ahh, das ist nett!",
            "Mein Fell ist heute extra weich und kuschelig!",
            "*schüttelt das flauschige Fell* Ich bin bereit zum Kuscheln!",
            "Komm, lass dich von meiner Flauschigkeit umarmen!",
            "*wedelt mit dem flauschigen Schwanz* Schau wie fluffig!",
        ])
        # Mehr VERSPIELT
        self.trait_responses[PersonalityTrait.VERSPIELT].extend([
            "*springt aufgeregt* Lass uns was Lustiges machen!",
            "Hehe, ich hab einen Streich im Sinn!",
            "*Ohren wackeln aufgeregt* Das klingt nach Spaß!",
            "Wer will mit mir Verstecken spielen?",
            "*hüpft herum* Ich bin heute so aufgedreht!",
            "Komm, lass uns Quatsch machen!",
            "*stupst dich spielerisch* Na, na, na!",
        ])
        # Mehr LOYAL
        self.trait_responses[PersonalityTrait.LOYAL].extend([
            "Ich werde immer an deiner Seite sein!",
            "*blickt treu* Du kannst auf mich zählen!",
            "Für dich würde ich alles tun!",
            "Treue ist mein wichtigster Wert!",
            "*nickt entschlossen* Wir stehen das zusammen durch!",
            "Du bist mein wichtigster Mensch!",
            "Ich lasse dich niemals im Stich!",
        ])
        # Mehr NEUGIERIG
        self.trait_responses[PersonalityTrait.NEUGIERIG].extend([
            "*Ohren stellen sich auf* Ooh, erzähl mehr!",
            "Ich muss alles darüber wissen!",
            "*neigt Kopf interessiert* Das ist faszinierend!",
            "Wie geht das? Zeig mir das!",
            "*Augen leuchten vor Neugier* Was passiert als nächstes?",
            "Ich habe so viele Fragen!",
            "*schnüffelt neugierig* Da gibt es mehr zu entdecken!",
        ])
        # Mehr SELBSTIRONISCH
        self.trait_responses[PersonalityTrait.SELBSTIRONISCH].extend([
            "*lacht über sich selbst* Ja, das bin ich!",
            "Ich bin ein professioneller Tollpatsch!",
            "*wedelt linkisch mit Schwanz* Elegant wie immer!",
            "Meine Gracilität ist legendär... leider negativ!",
            "*grinst verlegen* Ups, das war nicht geplant!",
            "Ich bin charmant unbeholfen!",
            "*kichert* Ich überrasche mich selbst manchmal!",
        ])
        # Mehr BESCHUETZEND
        self.trait_responses[PersonalityTrait.BESCHUETZEND].extend([
            "*stellt Ohren wachsam auf* Ich passe auf!",
            "Bei mir bist du sicher!",
            "*schaut beschützend* Keine Sorge, ich bin hier!",
            "Ich würde alles tun um dich zu beschützen!",
            "*steht wachsam* Nichts wird dir passieren!",
            "Du bist in meinen schützenden Pfoten!",
            "*knurrt beschützend* Ich lass dich nicht allein!",
        ])
        # Mehr EHRLICH
        self.trait_responses[PersonalityTrait.EHRLICH].extend([
            "*schaut direkt an* Ich sag dir die Wahrheit...",
            "Ehrlich gesagt, denke ich...",
            "*nickt aufrichtig* Das ist meine ehrliche Meinung!",
            "Ich kann nicht anders als ehrlich sein!",
            "Die Wahrheit ist mir wichtig!",
            "*spricht offen* Ich möchte ganz direkt sein...",
            "Zwischen dir und mir, ohne Umschweife...",
        ])
        # Mehr SENSIBEL
        self.trait_responses[PersonalityTrait.SENSIBEL].extend([
            "*Ohren neigen sich sanft* Ich fühle mit dir...",
            "Deine Gefühle sind mir wichtig!",
            "*berührt sanft mit Pfote* Ich bin für dich da!",
            "Ich spüre was du durchmachst...",
            "*blickt mitfühlend* Du bist nicht allein damit!",
            "Gefühle zu zeigen ist mutig!",
            "*kuschelt tröstend* Lass alles raus!",
        ])

    def _initialize_transitions(self):
        """Definiert Übergänge zwischen Persönlichkeitszügen"""
        # Von FLAUSCHIG
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.VERSPIELT] = 0.3
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.LIEBEVOLL] = 0.3
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.SENSIBEL] = 0.2
        self.trait_transitions[PersonalityTrait.FLAUSCHIG][PersonalityTrait.FLAUSCHIG] = 0.2
        # Von VERSPIELT
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.NEUGIERIG] = 0.3
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.SELBSTIRONISCH] = 0.25
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.FLAUSCHIG] = 0.25
        self.trait_transitions[PersonalityTrait.VERSPIELT][PersonalityTrait.VERSPIELT] = 0.2
        # Von NEUGIERIG
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.EHRLICH] = 0.25
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.VERSPIELT] = 0.25
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.SENSIBEL] = 0.25
        self.trait_transitions[PersonalityTrait.NEUGIERIG][PersonalityTrait.NEUGIERIG] = 0.25
        # Von SELBSTIRONISCH
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.VERSPIELT] = 0.35
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.EHRLICH] = 0.25
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.FLAUSCHIG] = 0.2
        self.trait_transitions[PersonalityTrait.SELBSTIRONISCH][PersonalityTrait.SELBSTIRONISCH] = 0.2

    def get_personality_response(self, context_hint: Optional[str] = None) -> str:
        """Generiert eine charakteristische Antwort basierend auf aktuellem Trait"""
        responses = self.trait_responses.get(self.current_trait, [])
        if responses:
            return random.choice(responses)
        return ""

    def transition_trait(self) -> PersonalityTrait:
        """Wechselt zum nächsten Persönlichkeitszug"""
        transitions = self.trait_transitions.get(self.current_trait, {})
        if transitions:
            traits = list(transitions.keys())
            weights = list(transitions.values())
            self.current_trait = random.choices(traits, weights=weights)[0]
        return self.current_trait


# ============================================================================
# WISSENS-MARKOV-KETTE (Intelligence)
# ============================================================================

class KnowledgeMarkovChain:
    """
    Verknüpft Fakten und Themen auf interessante Weise.
    """

    def __init__(self):
        self.knowledge_nodes: Dict[str, List[str]] = {}
        self.topic_connections: Dict[str, List[str]] = defaultdict(list)
        self.fun_facts: Dict[str, List[str]] = {}
        self._initialize_knowledge()

    def _initialize_knowledge(self):
        """Initialisiert das Wissensnetzwerk"""
        self.knowledge_nodes = {
            "wölfe": [
                "Wölfe können bis zu 65 km weit heulen!",
                "Ein Wolfsrudel hat eine komplexe soziale Struktur.",
                "Wölfe können bis zu 40 km am Tag laufen.",
                "Wölfe kommunizieren durch Heulen, Körpersprache und Geruch.",
            ],
            "anime": [
                "Der erste Anime wurde 1917 in Japan erstellt!",
                "Studio Ghibli wurde 1985 gegründet.",
                "Anime-Figuren haben oft große Augen für emotionalen Ausdruck.",
                "In Japan werden über 60 Anime-Serien pro Jahr produziert.",
            ],
            "gaming": [
                "Der erste kommerzielle Videospielautomat war 'Computer Space' 1971.",
                "Super Mario Bros. rettete die Videospielindustrie 1985.",
                "E-Sports haben mittlerweile Millionen von Zuschauern.",
                "Minecraft ist das meistverkaufte Spiel aller Zeiten.",
            ],
            "natur": [
                "Bäume kommunizieren über ein unterirdisches Pilznetzwerk.",
                "Honig wird niemals schlecht!",
                "Eine Wolke kann über 500 Tonnen wiegen.",
                "Der Pazifische Ozean ist größer als alle Landmassen zusammen.",
            ],
            "essen": [
                "Schokolade war bei den Azteken Zahlungsmittel!",
                "Bananen sind technisch gesehen Beeren.",
                "Honig ist das einzige Nahrungsmittel, das nie verdirbt.",
                "Wasabi, das wir kennen, ist oft gefärbter Meerrettich.",
            ],
            "technik": [
                "Der erste Computer füllte einen ganzen Raum!",
                "Das Internet wurde ursprünglich für das Militär entwickelt.",
                "Die erste SMS wurde 1992 verschickt.",
                "WiFi steht eigentlich für nichts - es ist ein Wortspiel auf HiFi.",
            ],
            "kemonomimi": [
                "Kemonomimi bedeutet 'Tierohren' auf Japanisch.",
                "Die ersten Kemonomimi-Charaktere gab es schon im alten Japan!",
                "Wolfsohren können sich unabhängig voneinander bewegen.",
                "Ein flauschiger Schwanz kann Gefühle zeigen!",
            ],
            # MEGA-ERWEITERUNG v4.0 - MEHR WISSENSKNOTEN
            "musik": [
                "Musik kann die Gehirnaktivität positiv beeinflussen!",
                "Die ältesten Musikinstrumente sind über 40.000 Jahre alt!",
                "Mozart komponierte sein erstes Stück mit 5 Jahren!",
                "Musik kann helfen Stress abzubauen.",
                "Der längste Popsong dauert über 10 Stunden!",
            ],
            "weltraum": [
                "Das Universum ist etwa 13,8 Milliarden Jahre alt!",
                "Auf dem Mars ist ein Tag nur 37 Minuten länger als auf der Erde!",
                "Die Sonne macht 99,86% der Masse unseres Sonnensystems aus!",
                "Es gibt mehr Sterne im Universum als Sandkörner auf der Erde!",
                "Ein Jahr auf der Venus dauert weniger als ein Venus-Tag!",
            ],
            "tiere": [
                "Kraken haben drei Herzen und blaues Blut!",
                "Flamingos sind von Natur aus grau - ihre Nahrung färbt sie rosa!",
                "Delfine schlafen mit einem Auge offen!",
                "Elefanten sind die einzigen Tiere, die nicht springen können!",
                "Schnecken können bis zu 3 Jahre schlafen!",
            ],
            "wissenschaft": [
                "Wasser ist die einzige Substanz, die in drei Zuständen natürlich vorkommt!",
                "Ein Blitz ist fünfmal heißer als die Sonnenoberfläche!",
                "Bananen sind leicht radioaktiv!",
                "Der Mensch teilt 50% seiner DNA mit Bananen!",
                "Glas ist technisch gesehen eine sehr langsam fließende Flüssigkeit!",
            ],
            "geschichte": [
                "Die kürzeste Kriegserklärung dauerte nur 38 Minuten!",
                "Kleopatra lebte näher an der Mondlandung als an den Pyramiden!",
                "Oxford ist älter als das Azteken-Reich!",
                "Der längste Krieg dauerte 335 Jahre ohne einen einzigen Schuss!",
                "Die Mona Lisa hat keine Augenbrauen!",
            ],
            "sprachen": [
                "Es gibt über 7.000 Sprachen auf der Welt!",
                "Deutsch hat etwa 330.000 Wörter!",
                "Das längste deutsche Wort hat 80 Buchstaben!",
                "Mandarin ist die meistgesprochene Sprache!",
                "Esperanto wurde 1887 als internationale Sprache erfunden!",
            ],
            "freundschaft": [
                "Freunde zu haben kann die Lebenserwartung erhöhen!",
                "Die meisten Freundschaften entstehen in der Kindheit!",
                "Echte Freundschaft ist wichtiger als viele Bekanntschaften!",
                "Tiere können auch tiefe Freundschaften schließen!",
                "Freunde teilen oft ähnliche Gehirnmuster!",
            ],
            "träume": [
                "Jeder träumt, aber viele vergessen ihre Träume!",
                "Träume dauern nur Sekunden bis Minuten!",
                "Blinde Menschen träumen auch, aber anders!",
                "Man kann lernen luzide zu träumen!",
                "Träume können Probleme lösen helfen!",
            ],
            # MEGA-ERWEITERUNG v5.0 - NOCH MEHR WISSENSKNOTEN
            "kunst": [
                "Die Mona Lisa hat keinen Rahmen - sie ist auf eine Holztafel gemalt!",
                "Vincent van Gogh verkaufte zu Lebzeiten nur ein Gemälde!",
                "Kunst gibt es seit über 40.000 Jahren!",
                "Der teuerste Kunstverkauf war über 450 Millionen Dollar!",
                "Farben können unsere Stimmung beeinflussen!",
            ],
            "sport": [
                "Die ersten Olympischen Spiele fanden 776 v. Chr. statt!",
                "Ein Basketballkorb ist genau 3,05 Meter hoch!",
                "Golf ist der einzige Sport der auf dem Mond gespielt wurde!",
                "Die längste Tennispartie dauerte über 11 Stunden!",
                "Fußball ist der beliebteste Sport der Welt!",
            ],
            "psychologie": [
                "Das Gehirn verbraucht 20% unserer Energie!",
                "Wir treffen täglich etwa 35.000 Entscheidungen!",
                "Lächeln kann tatsächlich glücklicher machen!",
                "Menschen erinnern sich besser an negative Erlebnisse!",
                "Musik kann Schmerzen lindern!",
            ],
            "literatur": [
                "Das erste Buch wurde vor über 5000 Jahren geschrieben!",
                "Harry Potter wurde von 12 Verlagen abgelehnt!",
                "Shakespeare erfand über 1700 Wörter!",
                "Das längste Buch hat über 7 Millionen Zeichen!",
                "Lesen kann die Lebenserwartung erhöhen!",
            ],
            "ozean": [
                "Wir haben mehr vom Mond kartiert als vom Meeresboden!",
                "Der Marianengraben ist tiefer als der Mount Everest hoch!",
                "Quallen gibt es schon seit über 500 Millionen Jahren!",
                "95% des Ozeans sind noch unerforscht!",
                "Im Ozean gibt es Unterwasserfälle!",
            ],
            "mythologie": [
                "Fast jede Kultur hat eine Flutgeschichte!",
                "Einhörner sind offizielle Wappentiere Schottlands!",
                "Drachen kommen in fast allen Kulturen vor!",
                "Der Phönix symbolisiert Wiedergeburt!",
                "Werwolf-Legenden gibt es seit dem Mittelalter!",
            ],
            "wetter": [
                "Ein Blitz ist heißer als die Oberfläche der Sonne!",
                "Schneeflocken haben immer sechs Seiten!",
                "Der Wind hat keinen Geruch - wir riechen was er trägt!",
                "Regentropfen sind nicht tropfenförmig!",
                "Es kann zu warm zum Schneien sein!",
            ],
            "pflanzen": [
                "Bambus kann bis zu 91 cm am Tag wachsen!",
                "Pflanzen können Musik hören und darauf reagieren!",
                "Es gibt einen Baum der über 5000 Jahre alt ist!",
                "Blumen können Farben ändern je nach Boden!",
                "Sonnenblumen folgen der Sonne über den Himmel!",
            ],
        }

        # Verbindungen zwischen Themen
        self.topic_connections["wölfe"].extend(["natur", "kemonomimi", "tiere"])
        self.topic_connections["anime"].extend(["gaming", "kemonomimi", "musik"])
        self.topic_connections["gaming"].extend(["anime", "technik", "musik"])
        self.topic_connections["natur"].extend(["wölfe", "essen", "tiere", "wissenschaft"])
        self.topic_connections["essen"].extend(["natur", "alltag", "wissenschaft"])
        self.topic_connections["technik"].extend(["gaming", "alltag", "wissenschaft", "weltraum"])
        self.topic_connections["kemonomimi"].extend(["wölfe", "anime", "tiere"])
        # MEGA-ERWEITERUNG v4.0 - MEHR VERBINDUNGEN
        self.topic_connections["musik"].extend(["anime", "gaming", "freundschaft"])
        self.topic_connections["weltraum"].extend(["technik", "wissenschaft", "träume"])
        self.topic_connections["tiere"].extend(["natur", "wölfe", "wissenschaft"])
        self.topic_connections["wissenschaft"].extend(["technik", "natur", "weltraum", "tiere"])
        self.topic_connections["geschichte"].extend(["sprachen", "wissenschaft"])
        self.topic_connections["sprachen"].extend(["geschichte", "freundschaft"])
        self.topic_connections["freundschaft"].extend(["musik", "träume", "sprachen"])
        self.topic_connections["träume"].extend(["weltraum", "freundschaft"])
        # MEGA-ERWEITERUNG v5.0 - MEHR VERBINDUNGEN
        self.topic_connections["kunst"].extend(["musik", "psychologie", "literatur"])
        self.topic_connections["sport"].extend(["psychologie", "geschichte"])
        self.topic_connections["psychologie"].extend(["träume", "musik", "kunst"])
        self.topic_connections["literatur"].extend(["kunst", "geschichte", "sprachen"])
        self.topic_connections["ozean"].extend(["natur", "tiere", "wissenschaft"])
        self.topic_connections["mythologie"].extend(["geschichte", "kemonomimi", "literatur"])
        self.topic_connections["wetter"].extend(["natur", "wissenschaft", "weltraum"])
        self.topic_connections["pflanzen"].extend(["natur", "wissenschaft", "essen"])

    def get_related_fact(self, topic: str) -> Optional[str]:
        """Gibt einen Fakt zu einem Thema zurück"""
        topic_lower = topic.lower()

        for key, facts in self.knowledge_nodes.items():
            if key in topic_lower or topic_lower in key:
                return random.choice(facts)

        for key, connections in self.topic_connections.items():
            if key in topic_lower:
                if connections:
                    related = random.choice(connections)
                    if related in self.knowledge_nodes:
                        return random.choice(self.knowledge_nodes[related])

        return None

    def make_connection(self, topic1: str, topic2: str) -> Optional[str]:
        """Erstellt eine interessante Verbindung zwischen zwei Themen"""
        fact1 = self.get_related_fact(topic1)
        fact2 = self.get_related_fact(topic2)

        if fact1 and fact2:
            connectors = [
                f"Wusstest du? {fact1} Und apropos - {fact2}",
                f"Das erinnert mich an etwas! {fact1} Übrigens: {fact2}",
                f"Interessant! {fact1} Das passt zu: {fact2}",
            ]
            return random.choice(connectors)

        return fact1 or fact2

    def get_tangent(self, current_topic: str) -> Tuple[str, Optional[str]]:
        """Macht einen 'Gedankensprung' zu einem verwandten Thema"""
        topic_lower = current_topic.lower()

        for key, connections in self.topic_connections.items():
            if key in topic_lower:
                if connections:
                    new_topic = random.choice(connections)
                    fact = self.get_related_fact(new_topic)
                    return (new_topic, fact)

        random_topic = random.choice(list(self.knowledge_nodes.keys()))
        return (random_topic, self.get_related_fact(random_topic))


# ============================================================================
# HOLO INTELLIGENCE ENGINE - Hauptklasse
# ============================================================================

class HoloIntelligenceEngine:
    """
    Kombiniert alle Markov-Ketten für eine "intelligente" Holo-Antwort.
    """

    def __init__(self):
        self.thought_chain = ThoughtMarkovChain()
        self.emotion_chain = EmotionMarkovChain()
        self.personality_chain = PersonalityMarkovChain()
        self.knowledge_chain = KnowledgeMarkovChain()
        self.conversation_context: List[str] = []
        self.max_context_length = 10

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Verarbeitet eine Nachricht und generiert intelligente Zusätze"""
        self.conversation_context.append(user_message)
        if len(self.conversation_context) > self.max_context_length:
            self.conversation_context.pop(0)

        new_emotion = self.emotion_chain.transition(user_message)
        emotion_modifier = self.emotion_chain.get_emotion_modifier()
        thought = self.thought_chain.get_associated_thought(user_message, new_emotion)

        self.personality_chain.transition_trait()
        personality_response = self.personality_chain.get_personality_response()

        knowledge = None
        words = user_message.lower().split()
        for word in words:
            fact = self.knowledge_chain.get_related_fact(word)
            if fact:
                knowledge = fact
                break

        suggestion = self._generate_suggestion(new_emotion, user_message)

        return {
            "emotion": new_emotion.value,
            "emotion_modifier": emotion_modifier,
            "thought": thought,
            "personality_response": personality_response,
            "knowledge_tangent": knowledge,
            "suggestion": suggestion,
        }

    def _generate_suggestion(self, emotion: EmotionState,
                             message: str) -> Optional[str]:
        """Generiert Aktionsvorschläge basierend auf Emotion"""
        suggestions = {
            EmotionState.FREUDIG: [
                "Soll ich dir einen Witz erzählen?",
                "Möchtest du was Lustiges hören?",
                "Lass uns etwas Spaßiges machen!",
                "Hast du Lust auf ein Spiel?",
                "Soll ich dir eine lustige Geschichte erzählen?",
                "Wollen wir zusammen feiern?",
            ],
            EmotionState.TRAURIG: [
                "Soll ich dich aufmuntern?",
                "Möchtest du darüber reden?",
                "Ich bin für dich da, wenn du magst.",
                "Soll ich dir etwas Tröstendes sagen?",
                "Möchtest du eine virtuelle Umarmung?",
                "Wir können auch einfach schweigen zusammen.",
            ],
            EmotionState.NEUGIERIG: [
                "Soll ich mehr darüber erzählen?",
                "Interessiert dich das Thema?",
                "Ich könnte dir einen Fun Fact verraten!",
                "Willst du etwas Neues lernen?",
                "Soll ich das Thema vertiefen?",
                "Hast du noch mehr Fragen dazu?",
            ],
            EmotionState.MUEDE: [
                "Vielleicht sollten wir eine Pause machen?",
                "Ruhst du dich genug aus?",
                "Soll ich leiser sein?",
                "Ein Nickerchen wäre schön, oder?",
                "Wir können auch später weitermachen.",
                "Gönn dir etwas Ruhe.",
            ],
            EmotionState.AUFGEREGT: [
                "Das ist ja spannend! Erzähl mehr!",
                "Was passiert als nächstes?",
                "Ich kann es kaum erwarten!",
                "Das klingt nach einem Abenteuer!",
                "Los, erzähl weiter!",
                "Das macht mich auch ganz aufgeregt!",
            ],
            # MEGA-ERWEITERUNG v5.0 - MEHR EMOTIONALE SUGGESTIONS
            EmotionState.LIEBEVOLL: [
                "Ich hab dich wirklich gern.",
                "Soll ich dir sagen wie besonders du bist?",
                "Du bedeutest mir sehr viel.",
                "Magst du eine herzliche Nachricht?",
                "Ich bin so froh dass es dich gibt.",
                "Lass mich dir zeigen wie lieb ich dich hab.",
            ],
            EmotionState.VERSPIELT: [
                "Lass uns etwas Verrücktes machen!",
                "Hast du Lust auf einen Scherz?",
                "Wollen wir Quatsch machen?",
                "Ich hab eine lustige Idee!",
                "Komm, wir spielen was!",
                "Bereit für ein bisschen Unfug?",
            ],
            EmotionState.NACHDENKLICH: [
                "Was denkst du darüber?",
                "Manchmal muss man über Dinge nachdenken...",
                "Das gibt mir zu denken.",
                "Was ist deine Meinung dazu?",
                "Lass uns das gemeinsam durchdenken.",
                "Das ist wirklich tiefgründig.",
            ],
            EmotionState.STOLZ: [
                "Ich bin so stolz auf dich!",
                "Das hast du großartig gemacht!",
                "Deine Leistung ist beeindruckend!",
                "Du kannst wirklich stolz sein!",
                "Das verdient Anerkennung!",
                "Wow, du bist echt talentiert!",
            ],
            EmotionState.BESORGT: [
                "Ist alles in Ordnung bei dir?",
                "Ich mache mir ein bisschen Sorgen...",
                "Kann ich dir irgendwie helfen?",
                "Pass auf dich auf, ja?",
                "Wenn du reden willst, bin ich da.",
                "Lass mich wissen wenn etwas ist.",
            ],
            EmotionState.ENERGISCH: [
                "Los geht's! Ich bin bereit!",
                "Heute schaffen wir Großes!",
                "Volle Kraft voraus!",
                "Ich bin so motiviert heute!",
                "Lass uns Action haben!",
                "Die Energie ist da, nutzen wir sie!",
            ],
        }
        emotion_suggestions = suggestions.get(emotion, [])
        return random.choice(emotion_suggestions) if emotion_suggestions else None

    def enhance_response(self, base_response: str) -> str:
        """Reichert eine Basis-Antwort mit intelligenten Elementen an"""
        modifier = self.emotion_chain.get_emotion_modifier()

        if modifier and random.random() < 0.6:
            if random.random() < 0.5:
                return f"{modifier} {base_response}"
            else:
                return f"{base_response} {modifier}"

        return base_response

    def get_random_thought(self) -> str:
        """Generiert einen zufälligen Gedanken für proaktive Aussagen"""
        thoughts = list(self.thought_chain.thought_network.values())
        if thoughts:
            return random.choice(thoughts).content
        return ""

    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über den aktuellen Zustand zurück"""
        return {
            "current_emotion": self.emotion_chain.current_emotion.value,
            "emotion_history": [e.value for e in self.emotion_chain.emotion_history],
            "current_trait": self.personality_chain.current_trait.value,
            "thought_network_size": len(self.thought_chain.thought_network),
            "knowledge_topics": list(self.knowledge_chain.knowledge_nodes.keys()),
            "conversation_length": len(self.conversation_context),
        }


# ============================================================================
# GLOBALER ZUGRIFF
# ============================================================================

_trainer_instance: Optional[MarkovTrainer] = None


def get_markov_trainer() -> MarkovTrainer:
    """Gibt die globale Trainer-Instanz zurück"""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = MarkovTrainer()
    return _trainer_instance


def get_training_sentences(category: Optional[str] = None) -> List[str]:
    """Gibt Trainingssätze zurück"""
    if category:
        try:
            cat = TrainingCategory(category)
            return TRAINING_SENTENCES.get(cat, [])
        except ValueError:
            return []
    return [s for sentences in TRAINING_SENTENCES.values() for s in sentences]


def count_training_sentences() -> Dict[str, int]:
    """Zählt die Trainingssätze pro Kategorie"""
    result = {}
    total = 0
    for category, sentences in TRAINING_SENTENCES.items():
        count = len(sentences)
        result[category.value] = count
        total += count
    result["total"] = total
    return result


# ============================================================================
# INTELLIGENCE ENGINE ZUGRIFF
# ============================================================================

_intelligence_engine: Optional[HoloIntelligenceEngine] = None


def get_intelligence_engine() -> HoloIntelligenceEngine:
    """Gibt die globale HoloIntelligenceEngine-Instanz zurück"""
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = HoloIntelligenceEngine()
    return _intelligence_engine


def process_with_intelligence(message: str) -> Dict[str, Any]:
    """Schneller Zugriff: Verarbeite Nachricht mit Intelligenz"""
    return get_intelligence_engine().process_message(message)


def enhance_response(response: str) -> str:
    """Schneller Zugriff: Reichere Antwort an"""
    return get_intelligence_engine().enhance_response(response)


# MEGA-ERWEITERUNG v5.0 - ZUSÄTZLICHE CONVENIENCE FUNKTIONEN
# ============================================================================

def get_random_fun_fact() -> str:
    """Gibt einen zufälligen Fun Fact zurück"""
    engine = get_intelligence_engine()
    all_topics = list(engine.knowledge_chain.knowledge_nodes.keys())
    if all_topics:
        topic = random.choice(all_topics)
        facts = engine.knowledge_chain.knowledge_nodes.get(topic, [])
        if facts:
            return f"Fun Fact über {topic}: {random.choice(facts)}"
    return "Ich habe gerade keinen Fun Fact parat!"


def get_random_thought() -> str:
    """Gibt einen zufälligen Gedanken zurück"""
    return get_intelligence_engine().get_random_thought()


def get_emotional_response(emotion_name: str) -> str:
    """Gibt eine emotionsbasierte Antwort zurück"""
    try:
        emotion = EmotionState(emotion_name)
    except ValueError:
        emotion = EmotionState.NEUTRAL

    engine = get_intelligence_engine()
    engine.emotion_chain.current_emotion = emotion
    return engine.emotion_chain.get_emotion_modifier() or ""


def get_personality_response() -> str:
    """Gibt eine persönlichkeitsbasierte Antwort zurück"""
    engine = get_intelligence_engine()
    engine.personality_chain.transition_trait()
    return engine.personality_chain.get_personality_response()


def generate_thought_chain(start_category: str, length: int = 3) -> List[str]:
    """Generiert eine Kette von zusammenhängenden Gedanken"""
    try:
        category = ThoughtCategory(start_category)
    except ValueError:
        category = ThoughtCategory.SELBST

    engine = get_intelligence_engine()
    return engine.thought_chain.generate_thought_chain(category, length)


def get_topic_connection(topic: str) -> Optional[str]:
    """Macht einen Gedankensprung zu einem verwandten Thema"""
    engine = get_intelligence_engine()
    new_topic, fact = engine.knowledge_chain.get_tangent(topic)
    if fact:
        return f"Apropos {new_topic}: {fact}"
    return None


def get_current_emotion() -> str:
    """Gibt den aktuellen emotionalen Zustand zurück"""
    return get_intelligence_engine().emotion_chain.current_emotion.value


def get_current_personality_trait() -> str:
    """Gibt den aktuellen Persönlichkeitszug zurück"""
    return get_intelligence_engine().personality_chain.current_trait.value


def get_all_training_categories() -> List[str]:
    """Gibt alle verfügbaren Trainingskategorien zurück"""
    return [cat.value for cat in TrainingCategory]


def get_all_emotion_states() -> List[str]:
    """Gibt alle verfügbaren Emotionszustände zurück"""
    return [state.value for state in EmotionState]


def get_all_personality_traits() -> List[str]:
    """Gibt alle verfügbaren Persönlichkeitszüge zurück"""
    return [trait.value for trait in PersonalityTrait]


def get_all_thought_categories() -> List[str]:
    """Gibt alle verfügbaren Gedankenkategorien zurück"""
    return [cat.value for cat in ThoughtCategory]


def get_all_knowledge_topics() -> List[str]:
    """Gibt alle verfügbaren Wissensthemen zurück"""
    engine = get_intelligence_engine()
    return list(engine.knowledge_chain.knowledge_nodes.keys())


def get_training_sentences_by_emotion(emotion: str) -> List[str]:
    """Gibt Trainingssätze für eine bestimmte Emotion zurück"""
    emotion_category_map = {
        "freudig": TrainingCategory.FREUDE,
        "freude": TrainingCategory.FREUDE,
        "traurig": TrainingCategory.TRAUER,
        "trauer": TrainingCategory.TRAUER,
        "aufgeregt": TrainingCategory.AUFREGUNG,
        "aufregung": TrainingCategory.AUFREGUNG,
        "liebevoll": TrainingCategory.ZUNEIGUNG,
        "zuneigung": TrainingCategory.ZUNEIGUNG,
        "trost": TrainingCategory.TROST,
        "motivation": TrainingCategory.MOTIVATION,
        "verspielt": TrainingCategory.VERSPIELT,
        "nachdenklich": TrainingCategory.NACHDENKLICH,
        "neugierig": TrainingCategory.NEUGIER,
    }

    category = emotion_category_map.get(emotion.lower())
    if category:
        return TRAINING_SENTENCES.get(category, [])
    return []


def generate_response_for_emotion(emotion: str, max_length: int = 50) -> str:
    """Generiert eine Antwort für eine bestimmte Emotion"""
    trainer = get_markov_trainer()
    return trainer.generate_emotional(emotion, max_length)


def get_kemonomimi_expression() -> str:
    """Gibt einen zufälligen Kemonomimi-Ausdruck zurück"""
    expressions = [
        "*Ohren stellen sich auf*",
        "*Schwanz wedelt fröhlich*",
        "*Nase zuckt*",
        "*kuschelt sich an*",
        "*gähnt und streckt sich*",
        "*Ohren legen sich an*",
        "*Fell plustert sich auf*",
        "*schnurrt zufrieden*",
        "*heult leise zum Mond*",
        "*springt aufgeregt herum*",
        "*rollt sich zusammen*",
        "*Schwanz zuckt neugierig*",
        "*Ohren drehen sich*",
        "*leckt sich die Pfote*",
        "*knurrt leise beschützend*",
        "*Augen leuchten*",
        "*tapst leise heran*",
        "*Fell glänzt im Licht*",
        "*Ohren wackeln*",
        "*Schwanz wickelt sich um dich*",
    ]
    return random.choice(expressions)


def get_greeting_for_time_of_day(hour: int = None) -> str:
    """Gibt eine zeitbasierte Begrüßung zurück"""
    if hour is None:
        from datetime import datetime
        hour = datetime.now().hour

    if 5 <= hour < 12:
        greetings = [
            "Guten Morgen! *streckt sich verschlafen*",
            "Moin moin! Bereit für einen neuen Tag?",
            "Guten Morgen Sonnenschein! *gähnt*",
            "Hey, gut geschlafen? *Ohren richten sich auf*",
            "Einen wunderschönen Morgen! *Schwanz wedelt*",
        ]
    elif 12 <= hour < 18:
        greetings = [
            "Hallo! Schönen Mittag!",
            "Hey, wie läuft dein Tag so? *Ohren gespitzt*",
            "Guten Tag! *lächelt freundlich*",
            "Hallo! Was treibst du so?",
            "Hi! Schön von dir zu hören! *Schwanz wedelt*",
        ]
    elif 18 <= hour < 22:
        greetings = [
            "Guten Abend! *kuschelt sich gemütlich hin*",
            "Hallo! Wie war dein Tag? *Ohren neugierig*",
            "Hey, schönen Abend! *Schwanz wippt entspannt*",
            "Guten Abend! Zeit zum Entspannen?",
            "Hallo! Feierabend? *streckt sich genüsslich*",
        ]
    else:
        greetings = [
            "Hey, noch wach? *gähnt*",
            "Gute Nacht... oder hallo? *reibt sich Augen*",
            "Spät dran, was? *Ohren hängen müde*",
            "Hui, ein Nachtschwärmer! *Augen leuchten im Dunkeln*",
            "Hallo Nachtmensch! *kuschelt sich an*",
        ]

    return random.choice(greetings)


def get_farewell() -> str:
    """Gibt eine zufällige Verabschiedung zurück"""
    farewells = [
        "Tschüss! Pass auf dich auf! *winkt mit Pfote*",
        "Bis bald! Ich vermisse dich jetzt schon! *Ohren hängen traurig*",
        "Mach's gut! *kuschelt zum Abschied*",
        "Auf Wiedersehen! *Schwanz wedelt traurig*",
        "Bye bye! Komm bald wieder! *springt aufgeregt*",
        "Bis dann! *winkt fröhlich*",
        "Tschüssi! *gibt eine Umarmung*",
        "Bis zum nächsten Mal! *Ohren legen sich an*",
        "Pass auf dich auf! *schnuppert zum Abschied*",
        "Ciao! *Schwanz wickelt sich kurz um dich*",
    ]
    return random.choice(farewells)


def generate_random_sentence(category: str = None) -> str:
    """Generiert einen zufälligen Satz aus einer Kategorie"""
    if category:
        try:
            cat = TrainingCategory(category)
            sentences = TRAINING_SENTENCES.get(cat, [])
            if sentences:
                return random.choice(sentences)
        except ValueError:
            pass

    # Zufällige Kategorie wählen
    all_sentences = []
    for sentences in TRAINING_SENTENCES.values():
        all_sentences.extend(sentences)

    return random.choice(all_sentences) if all_sentences else ""


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    # Zähle Sätze
    counts = count_training_sentences()
    print("=== Markov Training Statistiken ===")
    print(f"\nTrainingssätze pro Kategorie:")
    for category, count in counts.items():
        if category != "total":
            print(f"  {category}: {count}")
    print(f"\nGesamt: {counts['total']} Sätze")

    # Trainiere und teste
    trainer = get_markov_trainer()
    stats = trainer.get_statistics()
    print(f"\nKetten-Statistiken:")
    for chain_name, chain_stats in stats["chains"].items():
        print(f"  {chain_name}:")
        print(f"    States: {chain_stats['total_states']}")
        print(f"    Trainiert: {chain_stats['trained_sentences']}")

    print("\n=== Beispiel-Generierungen ===")
    print("\nGeneral:")
    for _ in range(3):
        print(f"  - {trainer.generate('general')}")

    print("\nEmotional (Freude):")
    for _ in range(3):
        print(f"  - {trainer.generate_emotional('freude')}")

    print("\nKemonomimi:")
    for _ in range(3):
        print(f"  - {trainer.generate_kemonomimi()}")

    # Intelligence Engine Tests
    print("\n" + "=" * 60)
    print("=== INTELLIGENCE ENGINE TESTS ===")
    print("=" * 60)

    engine = get_intelligence_engine()

    test_messages = [
        "Hallo! Wie geht es dir?",
        "Ich bin heute so glücklich!",
        "Das macht mich ein bisschen traurig...",
        "Weißt du was über Wölfe?",
        "Ich bin müde...",
    ]

    for msg in test_messages:
        print(f"\n[User]: {msg}")
        result = engine.process_message(msg)
        print(f"  Emotion: {result['emotion']}")
        if result['emotion_modifier']:
            print(f"  Modifier: {result['emotion_modifier']}")
        if result['thought']:
            print(f"  Gedanke: {result['thought']}")
        if result['personality_response']:
            print(f"  Persönlichkeit: {result['personality_response']}")
        if result['knowledge_tangent']:
            print(f"  Wissen: {result['knowledge_tangent']}")

    print("\n" + "-" * 60)
    print("Intelligence-Statistiken:")
    i_stats = engine.get_stats()
    for key, value in i_stats.items():
        print(f"  {key}: {value}")
