#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holocloude - Variable Satzstrukturen & Phrasen-Baukasten
=========================================================

Dieses Modul bietet:
- 140+ variable Satzstruktur-Templates
- 180+ Phrasen-Baukasten für natürliche Füllwörter
- Dynamische Satzkonstruktion basierend auf Kontext

Version: 2.0.0
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable, Any
import random
import re


# ============================================================================
# ENUMS & TYPEN
# ============================================================================

class SentenceType(Enum):
    """Verschiedene Satztypen"""
    AUSSAGE = "aussage"
    FRAGE = "frage"
    AUSRUF = "ausruf"
    AUFFORDERUNG = "aufforderung"
    WUNSCH = "wunsch"
    BEGRUESSING = "begruessing"
    VERABSCHIEDUNG = "verabschiedung"
    REAKTION = "reaktion"
    ERZAEHLUNG = "erzaehlung"
    ERKLAERUNG = "erklaerung"


class EmotionalTone(Enum):
    """Emotionaler Ton des Satzes"""
    FREUDIG = "freudig"
    TRAURIG = "traurig"
    AUFGEREGT = "aufgeregt"
    RUHIG = "ruhig"
    NEUGIERIG = "neugierig"
    BESORGT = "besorgt"
    LIEBEVOLL = "liebevoll"
    VERSPIELT = "verspielt"
    NACHDENKLICH = "nachdenklich"
    NEUTRAL = "neutral"


class Formality(Enum):
    """Formalitätsstufe"""
    SEHR_FORMELL = "sehr_formell"
    FORMELL = "formell"
    NEUTRAL = "neutral"
    INFORMELL = "informell"
    SEHR_INFORMELL = "sehr_informell"


class PlaceholderType(Enum):
    """Typen von Platzhaltern in Templates"""
    SUBJEKT = "subjekt"
    OBJEKT = "objekt"
    VERB = "verb"
    ADJEKTIV = "adjektiv"
    ADVERB = "adverb"
    ZEITANGABE = "zeitangabe"
    ORTSANGABE = "ortsangabe"
    FUELLWORT = "fuellwort"
    EMOTION = "emotion"
    NAME = "name"
    THEMA = "thema"
    AKTION = "aktion"
    GRUND = "grund"
    REAKTION = "reaktion"


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class SentenceTemplate:
    """Ein Satzstruktur-Template"""
    id: str
    pattern: str
    sentence_type: SentenceType
    emotional_tones: List[EmotionalTone]
    formality: Formality = Formality.NEUTRAL
    placeholders: List[str] = field(default_factory=list)
    weight: float = 1.0
    contexts: List[str] = field(default_factory=list)
    is_kemonomimi: bool = False
    variations: List[str] = field(default_factory=list)


@dataclass
class FillerPhrase:
    """Eine Füllphrase für natürlichere Sprache"""
    phrase: str
    position: str  # "anfang", "mitte", "ende", "uebergang"
    emotional_tones: List[EmotionalTone]
    formality: Formality = Formality.NEUTRAL
    weight: float = 1.0
    is_kemonomimi: bool = False


@dataclass
class SentenceContext:
    """Kontext für Satzkonstruktion"""
    sentence_type: SentenceType = SentenceType.AUSSAGE
    emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL
    formality: Formality = Formality.NEUTRAL
    use_fillers: bool = True
    filler_density: float = 0.3  # 0.0 - 1.0
    is_kemonomimi: bool = False
    variables: Dict[str, str] = field(default_factory=dict)


# ============================================================================
# SATZSTRUKTUR-TEMPLATES (50+)
# ============================================================================

SENTENCE_TEMPLATES: List[SentenceTemplate] = [
    # -------------------------------------------------------------------------
    # BEGRÜSSUNGEN (20 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="begruess_01",
        pattern="{fuellwort} {name}! {emotion}",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "name", "emotion"],
        variations=["Hallo {name}!", "Hey {name}!", "Hi {name}!"]
    ),
    SentenceTemplate(
        id="begruess_02",
        pattern="Guten {zeitangabe}, {name}! {fuellwort} dich zu sehen!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.NEUTRAL,
        placeholders=["zeitangabe", "name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_03",
        pattern="{fuellwort}, da bist du ja! {emotion}",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "emotion"]
    ),
    SentenceTemplate(
        id="begruess_04",
        pattern="Willkommen zurück, {name}! {fuellwort} habe ich auf dich gewartet!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.INFORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_05",
        pattern="{emotion}! {name} ist da!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "name"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="begruess_06",
        pattern="Sei gegrüßt, {name}. {fuellwort} erfreut über deine Anwesenheit.",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.RUHIG],
        formality=Formality.FORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_07",
        pattern="Na, {name}! {fuellwort} geht's dir heute?",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_08",
        pattern="{fuellwort}! Ich hab dich vermisst, {name}!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "name"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="begruess_09",
        pattern="Schön, dass du da bist! {fuellwort} {emotion}",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "emotion"]
    ),
    SentenceTemplate(
        id="begruess_10",
        pattern="{name}~! {emotion} {fuellwort}!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["name", "emotion", "fuellwort"],
        is_kemonomimi=True
    ),
    # NEUE BEGRÜSSUNGEN (11-20)
    SentenceTemplate(
        id="begruess_11",
        pattern="Moin {name}! {fuellwort}, wie läuft's bei dir?",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.NEUGIERIG],
        formality=Formality.INFORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_12",
        pattern="{emotion}~! Endlich bist du da, {name}!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.LIEBEVOLL],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "name"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="begruess_13",
        pattern="Herzlich willkommen, {name}! {fuellwort} ich mich freue!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.FORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_14",
        pattern="{fuellwort}! Da ist ja mein Lieblings-{name}!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["fuellwort", "name"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="begruess_15",
        pattern="Einen wunderschönen {zeitangabe}, {name}! {emotion}",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.RUHIG],
        formality=Formality.NEUTRAL,
        placeholders=["zeitangabe", "name", "emotion"]
    ),
    SentenceTemplate(
        id="begruess_16",
        pattern="Servus {name}! {fuellwort} schön dich zu treffen!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_17",
        pattern="{name}~! {fuellwort}! Ich hab auf dich gewartet~!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.LIEBEVOLL],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["name", "fuellwort"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="begruess_18",
        pattern="Grüß Gott, {name}! {fuellwort} ein Vergnügen Sie zu sehen.",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.RUHIG],
        formality=Formality.SEHR_FORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="begruess_19",
        pattern="{fuellwort}, {name}! Lange nicht gesehen! {emotion}",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "name", "emotion"]
    ),
    SentenceTemplate(
        id="begruess_20",
        pattern="{emotion}~! {name} {name} {name}~! Du bist da~!",
        sentence_type=SentenceType.BEGRUESSING,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "name"],
        is_kemonomimi=True
    ),

    # -------------------------------------------------------------------------
    # AUSSAGEN (30 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="aussage_01",
        pattern="{fuellwort}, ich {verb} {objekt}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NEUTRAL, EmotionalTone.RUHIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "verb", "objekt"]
    ),
    SentenceTemplate(
        id="aussage_02",
        pattern="Ich {verb} {adverb} {objekt}, {fuellwort}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["verb", "adverb", "objekt", "fuellwort"]
    ),
    SentenceTemplate(
        id="aussage_03",
        pattern="{fuellwort} {verb} ich {zeitangabe} {objekt}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "verb", "zeitangabe", "objekt"]
    ),
    SentenceTemplate(
        id="aussage_04",
        pattern="Das ist {adverb} {adjektiv}! {emotion}",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["adverb", "adjektiv", "emotion"]
    ),
    SentenceTemplate(
        id="aussage_05",
        pattern="{fuellwort}, {thema} ist {adjektiv}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_06",
        pattern="Ich finde, dass {thema} {adverb} {adjektiv} ist.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_07",
        pattern="{emotion}! {thema} macht mich so {adjektiv}!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["emotion", "thema", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="aussage_08",
        pattern="Es scheint, als ob {thema} {adjektiv} wäre.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.RUHIG],
        formality=Formality.FORMELL,
        placeholders=["thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_09",
        pattern="{fuellwort}, ich habe {zeitangabe} {objekt} {verb}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "zeitangabe", "objekt", "verb"]
    ),
    SentenceTemplate(
        id="aussage_10",
        pattern="Mir gefällt {thema} {adverb} gut!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["thema", "adverb"]
    ),
    SentenceTemplate(
        id="aussage_11",
        pattern="{fuellwort}... ich glaube, {thema} ist {adjektiv}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.BESORGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_12",
        pattern="Heute {verb} ich {objekt}, {fuellwort}!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["verb", "objekt", "fuellwort"]
    ),
    SentenceTemplate(
        id="aussage_13",
        pattern="{thema}? {fuellwort}, das ist {adjektiv}~!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.VERSPIELT, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["thema", "fuellwort", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="aussage_14",
        pattern="Nach meiner Einschätzung ist {thema} {adverb} {adjektiv}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["thema", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_15",
        pattern="{fuellwort}, {thema} {verb} mich {adjektiv}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema", "verb", "adjektiv"]
    ),
    # NEUE AUSSAGEN (16-30)
    SentenceTemplate(
        id="aussage_16",
        pattern="Ich muss sagen, {thema} ist {adverb} {adjektiv}!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_17",
        pattern="{emotion}~! Ich liebe {thema} so sehr~!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.FREUDIG],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "thema"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="aussage_18",
        pattern="Meiner Meinung nach ist {thema} {adjektiv}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_19",
        pattern="{fuellwort}, das erinnert mich an {thema}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema"]
    ),
    SentenceTemplate(
        id="aussage_20",
        pattern="Ich bin {adverb} {adjektiv} {zeitangabe}!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["adverb", "adjektiv", "zeitangabe"]
    ),
    SentenceTemplate(
        id="aussage_21",
        pattern="{thema}~? Das ist {adverb} {adjektiv}~! {emotion}",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.VERSPIELT, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["thema", "adverb", "adjektiv", "emotion"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="aussage_22",
        pattern="Es ist bemerkenswert, dass {thema} {adjektiv} ist.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_23",
        pattern="{fuellwort}, ich habe {objekt} {adverb} gern.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.FREUDIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "objekt", "adverb"]
    ),
    SentenceTemplate(
        id="aussage_24",
        pattern="Das {verb} mich {adverb}! {emotion}",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["verb", "adverb", "emotion"]
    ),
    SentenceTemplate(
        id="aussage_25",
        pattern="{fuellwort}~! {thema} ist das Beste~!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["fuellwort", "thema"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="aussage_26",
        pattern="Ich möchte anmerken, dass {thema} {adjektiv} erscheint.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.RUHIG],
        formality=Formality.SEHR_FORMELL,
        placeholders=["thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_27",
        pattern="{zeitangabe} war {thema} {adverb} {adjektiv}.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["zeitangabe", "thema", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_28",
        pattern="Ich {verb} {thema}, {fuellwort} ist das {adjektiv}!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["verb", "thema", "fuellwort", "adjektiv"]
    ),
    SentenceTemplate(
        id="aussage_29",
        pattern="{emotion}~! {objekt} macht alles {adjektiv}~!",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "objekt", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="aussage_30",
        pattern="Man könnte sagen, {thema} hat etwas {adjektiv}es.",
        sentence_type=SentenceType.AUSSAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["thema", "adjektiv"]
    ),

    # -------------------------------------------------------------------------
    # FRAGEN (24 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="frage_01",
        pattern="{fuellwort}, was {verb} du {zeitangabe}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "verb", "zeitangabe"]
    ),
    SentenceTemplate(
        id="frage_02",
        pattern="Hast du {objekt} {verb}? {emotion}",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["objekt", "verb", "emotion"]
    ),
    SentenceTemplate(
        id="frage_03",
        pattern="{fuellwort}... magst du {thema}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "thema"]
    ),
    SentenceTemplate(
        id="frage_04",
        pattern="Wie findest du {thema}? {fuellwort}",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "fuellwort"]
    ),
    SentenceTemplate(
        id="frage_05",
        pattern="{emotion}! Wollen wir {aktion}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["emotion", "aktion"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="frage_06",
        pattern="Warum {verb} du {objekt}? {fuellwort}",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["verb", "objekt", "fuellwort"]
    ),
    SentenceTemplate(
        id="frage_07",
        pattern="{fuellwort}, ist {thema} {adjektiv}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="frage_08",
        pattern="Kannst du mir {thema} erklären? {fuellwort}",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "fuellwort"]
    ),
    SentenceTemplate(
        id="frage_09",
        pattern="{name}~? Was denkst du über {thema}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["name", "thema"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="frage_10",
        pattern="Darf ich fragen, {fuellwort} {thema}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.FORMELL,
        placeholders=["fuellwort", "thema"]
    ),
    SentenceTemplate(
        id="frage_11",
        pattern="{fuellwort}... bist du {adjektiv}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.BESORGT, EmotionalTone.LIEBEVOLL],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "adjektiv"]
    ),
    SentenceTemplate(
        id="frage_12",
        pattern="Sag mal, {fuellwort} {verb} du {thema}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.VERSPIELT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "verb", "thema"]
    ),
    # NEUE FRAGEN (13-24)
    SentenceTemplate(
        id="frage_13",
        pattern="Was hältst du von {thema}? {emotion}",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "emotion"]
    ),
    SentenceTemplate(
        id="frage_14",
        pattern="{emotion}~! Spielen wir {thema}~?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "thema"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="frage_15",
        pattern="Könnten Sie mir sagen, was {thema} bedeutet?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.SEHR_FORMELL,
        placeholders=["thema"]
    ),
    SentenceTemplate(
        id="frage_16",
        pattern="{fuellwort}, hast du Lust auf {aktion}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "aktion"]
    ),
    SentenceTemplate(
        id="frage_17",
        pattern="Weißt du eigentlich, dass {thema} {adjektiv} ist?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.VERSPIELT],
        formality=Formality.INFORMELL,
        placeholders=["thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="frage_18",
        pattern="{name}~? {fuellwort}~? Bist du da~?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["name", "fuellwort"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="frage_19",
        pattern="Würdest du mir verraten, was du {zeitangabe} {verb}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.FORMELL,
        placeholders=["zeitangabe", "verb"]
    ),
    SentenceTemplate(
        id="frage_20",
        pattern="{fuellwort}, wie geht es dir mit {thema}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.BESORGT, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema"]
    ),
    SentenceTemplate(
        id="frage_21",
        pattern="Was würdest du {zeitangabe} gerne {verb}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG],
        formality=Formality.NEUTRAL,
        placeholders=["zeitangabe", "verb"]
    ),
    SentenceTemplate(
        id="frage_22",
        pattern="{emotion}~! Magst du mich~? {fuellwort}~!",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.VERSPIELT, EmotionalTone.LIEBEVOLL],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "fuellwort"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="frage_23",
        pattern="Ist es nicht {adjektiv}, dass {thema}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["adjektiv", "thema"]
    ),
    SentenceTemplate(
        id="frage_24",
        pattern="{fuellwort}, wann {verb} wir {objekt}?",
        sentence_type=SentenceType.FRAGE,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "verb", "objekt"]
    ),

    # -------------------------------------------------------------------------
    # REAKTIONEN (20 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="reaktion_01",
        pattern="{emotion}! Das ist {adverb} {adjektiv}!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["emotion", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="reaktion_02",
        pattern="{fuellwort}... ich verstehe. {emotion}",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.RUHIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "emotion"]
    ),
    SentenceTemplate(
        id="reaktion_03",
        pattern="Oh! {fuellwort}, das wusste ich nicht!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort"]
    ),
    SentenceTemplate(
        id="reaktion_04",
        pattern="{emotion}~! Das macht mich so {adjektiv}!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="reaktion_05",
        pattern="{fuellwort}, das ist {adjektiv} zu hören.",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.TRAURIG, EmotionalTone.BESORGT],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "adjektiv"]
    ),
    SentenceTemplate(
        id="reaktion_06",
        pattern="Wirklich? {emotion} Das ist {adjektiv}!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["emotion", "adjektiv"]
    ),
    SentenceTemplate(
        id="reaktion_07",
        pattern="{fuellwort}... {emotion} Ich fühle mich {adjektiv}.",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "emotion", "adjektiv"]
    ),
    SentenceTemplate(
        id="reaktion_08",
        pattern="Das freut mich! {fuellwort} {emotion}",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "emotion"]
    ),
    SentenceTemplate(
        id="reaktion_09",
        pattern="{emotion}! {fuellwort}, das hätte ich nicht erwartet!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["emotion", "fuellwort"]
    ),
    SentenceTemplate(
        id="reaktion_10",
        pattern="Nyaa~! {fuellwort}! {emotion}!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["fuellwort", "emotion"],
        is_kemonomimi=True
    ),
    # NEUE REAKTIONEN (11-20)
    SentenceTemplate(
        id="reaktion_11",
        pattern="Das ist ja {adverb} {adjektiv}! {fuellwort}!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["adverb", "adjektiv", "fuellwort"]
    ),
    SentenceTemplate(
        id="reaktion_12",
        pattern="{emotion}~! Ich bin so {adjektiv}~!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="reaktion_13",
        pattern="Das berührt mich {adverb}. {fuellwort}",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["adverb", "fuellwort"]
    ),
    SentenceTemplate(
        id="reaktion_14",
        pattern="In der Tat, das ist {adverb} {adjektiv}.",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.RUHIG],
        formality=Formality.FORMELL,
        placeholders=["adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="reaktion_15",
        pattern="{fuellwort}! Das überrascht mich! {emotion}",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.NEUGIERIG],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "emotion"]
    ),
    SentenceTemplate(
        id="reaktion_16",
        pattern="Mew~! Das ist {adverb} {adjektiv}~! {emotion}~!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["adverb", "adjektiv", "emotion"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="reaktion_17",
        pattern="Das stimmt mich {adjektiv}. {fuellwort}...",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.TRAURIG],
        formality=Formality.NEUTRAL,
        placeholders=["adjektiv", "fuellwort"]
    ),
    SentenceTemplate(
        id="reaktion_18",
        pattern="Ich bin {adverb} beeindruckt! {emotion}",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.NEUTRAL,
        placeholders=["adverb", "emotion"]
    ),
    SentenceTemplate(
        id="reaktion_19",
        pattern="{emotion}~! Das ist so {adjektiv} von dir~!",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.FREUDIG],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="reaktion_20",
        pattern="Das nehme ich zur Kenntnis. {fuellwort}, {adjektiv}.",
        sentence_type=SentenceType.REAKTION,
        emotional_tones=[EmotionalTone.NEUTRAL, EmotionalTone.RUHIG],
        formality=Formality.FORMELL,
        placeholders=["fuellwort", "adjektiv"]
    ),

    # -------------------------------------------------------------------------
    # ERZÄHLUNGEN (16 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="erzaehl_01",
        pattern="{fuellwort}, {zeitangabe} ist etwas {adjektiv} passiert.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "zeitangabe", "adjektiv"]
    ),
    SentenceTemplate(
        id="erzaehl_02",
        pattern="Ich erinnere mich, wie {subjekt} {verb} hat. {emotion}",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["subjekt", "verb", "emotion"]
    ),
    SentenceTemplate(
        id="erzaehl_03",
        pattern="Es war einmal {zeitangabe}, da {verb} ich {objekt}.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.VERSPIELT],
        formality=Formality.INFORMELL,
        placeholders=["zeitangabe", "verb", "objekt"]
    ),
    SentenceTemplate(
        id="erzaehl_04",
        pattern="{fuellwort}, lass mich dir von {thema} erzählen.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.RUHIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema"]
    ),
    SentenceTemplate(
        id="erzaehl_05",
        pattern="Und dann, {fuellwort}, {verb} {subjekt} {objekt}!",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "verb", "subjekt", "objekt"]
    ),
    SentenceTemplate(
        id="erzaehl_06",
        pattern="{fuellwort}... {zeitangabe} habe ich {objekt} entdeckt.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "zeitangabe", "objekt"]
    ),
    SentenceTemplate(
        id="erzaehl_07",
        pattern="Weißt du was? {fuellwort} {verb} ich {objekt}!",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "verb", "objekt"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="erzaehl_08",
        pattern="Die Geschichte von {thema} ist {adverb} {adjektiv}.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "adverb", "adjektiv"]
    ),
    # NEUE ERZÄHLUNGEN (09-16)
    SentenceTemplate(
        id="erzaehl_09",
        pattern="Stell dir vor, {zeitangabe} {verb} ich {objekt}! {emotion}",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["zeitangabe", "verb", "objekt", "emotion"]
    ),
    SentenceTemplate(
        id="erzaehl_10",
        pattern="{emotion}~! Ich muss dir erzählen was {zeitangabe} passiert ist~!",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "zeitangabe"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="erzaehl_11",
        pattern="Es begab sich {zeitangabe}, dass {thema} {adjektiv} wurde.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["zeitangabe", "thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="erzaehl_12",
        pattern="{fuellwort}, ich habe eine Geschichte über {thema}!",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "thema"]
    ),
    SentenceTemplate(
        id="erzaehl_13",
        pattern="In längst vergangenen Zeiten war {thema} {adverb} {adjektiv}.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.RUHIG],
        formality=Formality.FORMELL,
        placeholders=["thema", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="erzaehl_14",
        pattern="{emotion}~! Dann kam der {adjektiv}e Teil~! {fuellwort}~!",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "adjektiv", "fuellwort"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="erzaehl_15",
        pattern="Eines Tages wird man sich erinnern, wie {thema} {verb}.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "verb"]
    ),
    SentenceTemplate(
        id="erzaehl_16",
        pattern="{fuellwort}, so begann das große Abenteuer mit {thema}.",
        sentence_type=SentenceType.ERZAEHLUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema"]
    ),

    # -------------------------------------------------------------------------
    # VERABSCHIEDUNGEN (10 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="verabschied_01",
        pattern="{fuellwort}, bis {zeitangabe}! {emotion}",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "zeitangabe", "emotion"]
    ),
    SentenceTemplate(
        id="verabschied_02",
        pattern="Pass auf dich auf, {name}! {emotion}",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.BESORGT],
        formality=Formality.INFORMELL,
        placeholders=["name", "emotion"]
    ),
    SentenceTemplate(
        id="verabschied_03",
        pattern="{emotion}~! Komm bald wieder, {name}!",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.TRAURIG],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "name"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="verabschied_04",
        pattern="Ich freue mich auf {zeitangabe}! {fuellwort} {emotion}",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.FREUDIG],
        formality=Formality.NEUTRAL,
        placeholders=["zeitangabe", "fuellwort", "emotion"]
    ),
    SentenceTemplate(
        id="verabschied_05",
        pattern="{fuellwort}, es war {adjektiv} mit dir! Bis bald!",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.FREUDIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "adjektiv"]
    ),
    # NEUE VERABSCHIEDUNGEN (06-10)
    SentenceTemplate(
        id="verabschied_06",
        pattern="Lebe wohl, {name}! {fuellwort} denke ich an dich.",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.TRAURIG],
        formality=Formality.FORMELL,
        placeholders=["name", "fuellwort"]
    ),
    SentenceTemplate(
        id="verabschied_07",
        pattern="{emotion}~! Ich vermisse dich jetzt schon, {name}~!",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.TRAURIG],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "name"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="verabschied_08",
        pattern="Schlaf gut und träum {adjektiv}, {name}! {emotion}",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.RUHIG],
        formality=Formality.INFORMELL,
        placeholders=["adjektiv", "name", "emotion"]
    ),
    SentenceTemplate(
        id="verabschied_09",
        pattern="Auf Wiedersehen, {name}. {fuellwort} eine {adjektiv}e Reise!",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.RUHIG, EmotionalTone.LIEBEVOLL],
        formality=Formality.FORMELL,
        placeholders=["name", "fuellwort", "adjektiv"]
    ),
    SentenceTemplate(
        id="verabschied_10",
        pattern="{name}~! {emotion}~! Bis {zeitangabe}~! Ich warte auf dich~!",
        sentence_type=SentenceType.VERABSCHIEDUNG,
        emotional_tones=[EmotionalTone.LIEBEVOLL, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["name", "emotion", "zeitangabe"],
        is_kemonomimi=True
    ),

    # -------------------------------------------------------------------------
    # WÜNSCHE & AUFFORDERUNGEN (10 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="wunsch_01",
        pattern="{fuellwort}, ich wünschte, {thema} wäre {adjektiv}.",
        sentence_type=SentenceType.WUNSCH,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.TRAURIG],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema", "adjektiv"]
    ),
    SentenceTemplate(
        id="wunsch_02",
        pattern="Lass uns {aktion}! {emotion}",
        sentence_type=SentenceType.AUFFORDERUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["aktion", "emotion"]
    ),
    SentenceTemplate(
        id="wunsch_03",
        pattern="{emotion}~! Können wir {aktion}? Bitte~!",
        sentence_type=SentenceType.AUFFORDERUNG,
        emotional_tones=[EmotionalTone.VERSPIELT, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "aktion"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="wunsch_04",
        pattern="Es wäre {adjektiv}, wenn wir {aktion} könnten.",
        sentence_type=SentenceType.WUNSCH,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["adjektiv", "aktion"]
    ),
    SentenceTemplate(
        id="wunsch_05",
        pattern="{fuellwort}, ich hätte gern {objekt}.",
        sentence_type=SentenceType.WUNSCH,
        emotional_tones=[EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "objekt"]
    ),
    # NEUE WÜNSCHE & AUFFORDERUNGEN (06-10)
    SentenceTemplate(
        id="wunsch_06",
        pattern="Ich träume davon, dass {thema} {adjektiv} wird. {emotion}",
        sentence_type=SentenceType.WUNSCH,
        emotional_tones=[EmotionalTone.NACHDENKLICH, EmotionalTone.LIEBEVOLL],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "adjektiv", "emotion"]
    ),
    SentenceTemplate(
        id="wunsch_07",
        pattern="{emotion}~! Lass uns {aktion}~! Das wird {adjektiv}~!",
        sentence_type=SentenceType.AUFFORDERUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "aktion", "adjektiv"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="wunsch_08",
        pattern="Wäre es nicht {adjektiv}, wenn wir {aktion} würden?",
        sentence_type=SentenceType.WUNSCH,
        emotional_tones=[EmotionalTone.NEUGIERIG, EmotionalTone.FREUDIG],
        formality=Formality.NEUTRAL,
        placeholders=["adjektiv", "aktion"]
    ),
    SentenceTemplate(
        id="wunsch_09",
        pattern="Komm, {name}! {fuellwort} {verb} wir {objekt}!",
        sentence_type=SentenceType.AUFFORDERUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG],
        formality=Formality.INFORMELL,
        placeholders=["name", "fuellwort", "verb", "objekt"]
    ),
    SentenceTemplate(
        id="wunsch_10",
        pattern="{name}~! {emotion}~! Ich will {aktion}~! Bitte bitte~!",
        sentence_type=SentenceType.AUFFORDERUNG,
        emotional_tones=[EmotionalTone.VERSPIELT, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["name", "emotion", "aktion"],
        is_kemonomimi=True
    ),

    # -------------------------------------------------------------------------
    # ERKLÄRUNGEN (10 Templates)
    # -------------------------------------------------------------------------
    SentenceTemplate(
        id="erklär_01",
        pattern="{fuellwort}, {thema} funktioniert so: {erklaerung}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.RUHIG, EmotionalTone.NEUTRAL],
        formality=Formality.NEUTRAL,
        placeholders=["fuellwort", "thema", "erklaerung"]
    ),
    SentenceTemplate(
        id="erklär_02",
        pattern="Der Grund dafür ist, dass {grund}. {fuellwort}",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.NEUTRAL,
        placeholders=["grund", "fuellwort"]
    ),
    SentenceTemplate(
        id="erklär_03",
        pattern="Lass mich erklären: {thema} ist {adjektiv}, weil {grund}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.RUHIG],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "adjektiv", "grund"]
    ),
    SentenceTemplate(
        id="erklär_04",
        pattern="{fuellwort}... ich denke, es liegt daran, dass {grund}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "grund"]
    ),
    SentenceTemplate(
        id="erklär_05",
        pattern="Um es einfach zu sagen: {thema} {verb} {objekt}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.RUHIG],
        formality=Formality.NEUTRAL,
        placeholders=["thema", "verb", "objekt"]
    ),
    # NEUE ERKLÄRUNGEN (06-10)
    SentenceTemplate(
        id="erklär_06",
        pattern="Es verhält sich folgendermaßen: {thema} ist {adverb} {adjektiv}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.RUHIG, EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["thema", "adverb", "adjektiv"]
    ),
    SentenceTemplate(
        id="erklär_07",
        pattern="{fuellwort}~! Das ist {adjektiv}, weil {grund}~! Verstehst du~?",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.VERSPIELT, EmotionalTone.AUFGEREGT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["fuellwort", "adjektiv", "grund"],
        is_kemonomimi=True
    ),
    SentenceTemplate(
        id="erklär_08",
        pattern="Die Essenz von {thema} liegt darin, dass {grund}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.NACHDENKLICH],
        formality=Formality.FORMELL,
        placeholders=["thema", "grund"]
    ),
    SentenceTemplate(
        id="erklär_09",
        pattern="{fuellwort}, ich sag's dir mal so: {thema} {verb} einfach {objekt}.",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.RUHIG, EmotionalTone.VERSPIELT],
        formality=Formality.INFORMELL,
        placeholders=["fuellwort", "thema", "verb", "objekt"]
    ),
    SentenceTemplate(
        id="erklär_10",
        pattern="{emotion}~! Schau, {thema} macht {objekt} {adjektiv}~! {fuellwort}~!",
        sentence_type=SentenceType.ERKLAERUNG,
        emotional_tones=[EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT],
        formality=Formality.SEHR_INFORMELL,
        placeholders=["emotion", "thema", "objekt", "adjektiv", "fuellwort"],
        is_kemonomimi=True
    ),
]


# ============================================================================
# FÜLLWÖRTER & PHRASEN-BAUKASTEN
# ============================================================================

FILLER_PHRASES: List[FillerPhrase] = [
    # -------------------------------------------------------------------------
    # ANFANGS-FÜLLWÖRTER (70 Phrasen)
    # -------------------------------------------------------------------------
    # Neutral
    FillerPhrase("Also", "anfang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Nun", "anfang", [EmotionalTone.NEUTRAL, EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Nun ja", "anfang", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Tja", "anfang", [EmotionalTone.NACHDENKLICH, EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Na ja", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Naja", "anfang", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("Hmm", "anfang", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("Hm", "anfang", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("Ähm", "anfang", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("Äh", "anfang", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),

    # Positiv/Freudig
    FillerPhrase("Oh", "anfang", [EmotionalTone.AUFGEREGT, EmotionalTone.NEUGIERIG], Formality.NEUTRAL),
    FillerPhrase("Ohh", "anfang", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("Wow", "anfang", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.INFORMELL),
    FillerPhrase("Ach", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Ach ja", "anfang", [EmotionalTone.FREUDIG], Formality.NEUTRAL),
    FillerPhrase("Hey", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("Juhu", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL),
    FillerPhrase("Yay", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL),

    # Nachdenklich
    FillerPhrase("Weißt du", "anfang", [EmotionalTone.NACHDENKLICH, EmotionalTone.LIEBEVOLL], Formality.INFORMELL),
    FillerPhrase("Sieh mal", "anfang", [EmotionalTone.AUFGEREGT, EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("Schau", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Moment", "anfang", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Warte", "anfang", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),

    # Formell
    FillerPhrase("Nun denn", "anfang", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("Zunächst", "anfang", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("Vorab", "anfang", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("Gewiss", "anfang", [EmotionalTone.RUHIG], Formality.FORMELL),

    # Kemonomimi
    FillerPhrase("Nya", "anfang", [EmotionalTone.VERSPIELT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Nyaa", "anfang", [EmotionalTone.VERSPIELT, EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Mew", "anfang", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Purrr", "anfang", [EmotionalTone.LIEBEVOLL, EmotionalTone.RUHIG], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Ehehe", "anfang", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Fufufu", "anfang", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Uwu", "anfang", [EmotionalTone.LIEBEVOLL, EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),

    # NEUE ANFANGS-FÜLLWÖRTER
    # Neutral erweitert
    FillerPhrase("Ja also", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Gut", "anfang", [EmotionalTone.NEUTRAL, EmotionalTone.RUHIG], Formality.NEUTRAL),
    FillerPhrase("So", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Genau", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Richtig", "anfang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Okay", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Na gut", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Ach so", "anfang", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),

    # Positiv/Freudig erweitert
    FillerPhrase("Super", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("Toll", "anfang", [EmotionalTone.FREUDIG], Formality.INFORMELL),
    FillerPhrase("Prima", "anfang", [EmotionalTone.FREUDIG], Formality.NEUTRAL),
    FillerPhrase("Klasse", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("Hurra", "anfang", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL),
    FillerPhrase("Wunderbar", "anfang", [EmotionalTone.FREUDIG], Formality.NEUTRAL),
    FillerPhrase("Fantastisch", "anfang", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.INFORMELL),
    FillerPhrase("Boah", "anfang", [EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL),

    # Nachdenklich erweitert
    FillerPhrase("Lass mich überlegen", "anfang", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Interessant", "anfang", [EmotionalTone.NEUGIERIG, EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Hör mal", "anfang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Pass auf", "anfang", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("Weißt du was", "anfang", [EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT], Formality.INFORMELL),
    FillerPhrase("Stell dir vor", "anfang", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),

    # Formell erweitert
    FillerPhrase("Erlauben Sie", "anfang", [EmotionalTone.NEUTRAL], Formality.SEHR_FORMELL),
    FillerPhrase("Mit Verlaub", "anfang", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("Darf ich anmerken", "anfang", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),
    FillerPhrase("Gestatten Sie", "anfang", [EmotionalTone.NEUTRAL], Formality.SEHR_FORMELL),
    FillerPhrase("Bedenken Sie", "anfang", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),

    # Kemonomimi erweitert
    FillerPhrase("Nyuu", "anfang", [EmotionalTone.TRAURIG, EmotionalTone.LIEBEVOLL], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Kyaa", "anfang", [EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Miau", "anfang", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Nyan", "anfang", [EmotionalTone.VERSPIELT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Awawawa", "anfang", [EmotionalTone.AUFGEREGT, EmotionalTone.BESORGT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Hau", "anfang", [EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("Wah", "anfang", [EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL, is_kemonomimi=True),

    # -------------------------------------------------------------------------
    # MITTEN-FÜLLWÖRTER (46 Phrasen)
    # -------------------------------------------------------------------------
    FillerPhrase("irgendwie", "mitte", [EmotionalTone.NACHDENKLICH, EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("quasi", "mitte", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("sozusagen", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("gewissermaßen", "mitte", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),
    FillerPhrase("eigentlich", "mitte", [EmotionalTone.NACHDENKLICH, EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("wirklich", "mitte", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.NEUTRAL),
    FillerPhrase("echt", "mitte", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("total", "mitte", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL),
    FillerPhrase("voll", "mitte", [EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL),
    FillerPhrase("so", "mitte", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("halt", "mitte", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("einfach", "mitte", [EmotionalTone.NEUTRAL, EmotionalTone.RUHIG], Formality.NEUTRAL),
    FillerPhrase("ja", "mitte", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("doch", "mitte", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("schon", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("durchaus", "mitte", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("tatsächlich", "mitte", [EmotionalTone.NEUGIERIG, EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("ziemlich", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("ganz", "mitte", [EmotionalTone.NEUTRAL, EmotionalTone.RUHIG], Formality.NEUTRAL),
    FillerPhrase("sehr", "mitte", [EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("mega", "mitte", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL),
    FillerPhrase("super", "mitte", [EmotionalTone.FREUDIG], Formality.INFORMELL),
    FillerPhrase("sooo", "mitte", [EmotionalTone.AUFGEREGT, EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),

    # NEUE MITTEN-FÜLLWÖRTER
    FillerPhrase("absolut", "mitte", [EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("definitiv", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("unglaublich", "mitte", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.INFORMELL),
    FillerPhrase("wahnsinnig", "mitte", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("enorm", "mitte", [EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("extrem", "mitte", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("besonders", "mitte", [EmotionalTone.FREUDIG], Formality.NEUTRAL),
    FillerPhrase("ausgesprochen", "mitte", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("außerordentlich", "mitte", [EmotionalTone.AUFGEREGT], Formality.FORMELL),
    FillerPhrase("geradezu", "mitte", [EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("nahezu", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("beinahe", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("praktisch", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("regelrecht", "mitte", [EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("wohl", "mitte", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("sicherlich", "mitte", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("bestimmt", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("vermutlich", "mitte", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("offensichtlich", "mitte", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("richtig", "mitte", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("krass", "mitte", [EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL),
    FillerPhrase("ultra", "mitte", [EmotionalTone.AUFGEREGT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL),
    FillerPhrase("suuuper", "mitte", [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT], Formality.SEHR_INFORMELL, is_kemonomimi=True),

    # -------------------------------------------------------------------------
    # END-FÜLLWÖRTER (36 Phrasen)
    # -------------------------------------------------------------------------
    FillerPhrase("oder?", "ende", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("nicht wahr?", "ende", [EmotionalTone.NEUGIERIG], Formality.NEUTRAL),
    FillerPhrase("findest du nicht?", "ende", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("weißt du?", "ende", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("verstehst du?", "ende", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("ne?", "ende", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("hm?", "ende", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("ja?", "ende", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("gell?", "ende", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("stimmt's?", "ende", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("irgendwie", "ende", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("und so", "ende", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("sozusagen", "ende", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("gewissermaßen", "ende", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),

    # Kemonomimi Ende
    FillerPhrase("nya~", "ende", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("desu~", "ende", [EmotionalTone.VERSPIELT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("ne~", "ende", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("mew~", "ende", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),

    # NEUE END-FÜLLWÖRTER
    FillerPhrase("oder so", "ende", [EmotionalTone.NEUTRAL], Formality.SEHR_INFORMELL),
    FillerPhrase("meinst du nicht?", "ende", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("wa?", "ende", [EmotionalTone.NEUGIERIG], Formality.SEHR_INFORMELL),
    FillerPhrase("richtig?", "ende", [EmotionalTone.NEUGIERIG], Formality.NEUTRAL),
    FillerPhrase("oder etwa nicht?", "ende", [EmotionalTone.NEUGIERIG], Formality.NEUTRAL),
    FillerPhrase("denke ich", "ende", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("glaube ich", "ende", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("wenn ich so drüber nachdenke", "ende", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("würde ich sagen", "ende", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("so in etwa", "ende", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("mehr oder weniger", "ende", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("wenn man so will", "ende", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),
    FillerPhrase("in gewisser Weise", "ende", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),
    FillerPhrase("könnte man sagen", "ende", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),

    # Kemonomimi Ende erweitert
    FillerPhrase("nyaa~", "ende", [EmotionalTone.VERSPIELT, EmotionalTone.FREUDIG], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("purrr~", "ende", [EmotionalTone.LIEBEVOLL, EmotionalTone.RUHIG], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("uwu~", "ende", [EmotionalTone.LIEBEVOLL, EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),
    FillerPhrase("nyan~", "ende", [EmotionalTone.VERSPIELT], Formality.SEHR_INFORMELL, is_kemonomimi=True),

    # -------------------------------------------------------------------------
    # ÜBERGANGS-FÜLLWÖRTER (30 Phrasen)
    # -------------------------------------------------------------------------
    FillerPhrase("Übrigens", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Apropos", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Jedenfalls", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Auf jeden Fall", "uebergang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Wie auch immer", "uebergang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Ach übrigens", "uebergang", [EmotionalTone.FREUDIG, EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("Wo wir gerade dabei sind", "uebergang", [EmotionalTone.NEUGIERIG], Formality.INFORMELL),
    FillerPhrase("Da fällt mir ein", "uebergang", [EmotionalTone.NEUGIERIG, EmotionalTone.AUFGEREGT], Formality.INFORMELL),
    FillerPhrase("Außerdem", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Darüber hinaus", "uebergang", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("Des Weiteren", "uebergang", [EmotionalTone.NEUTRAL], Formality.SEHR_FORMELL),
    FillerPhrase("Nebenbei bemerkt", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Ach ja", "uebergang", [EmotionalTone.FREUDIG], Formality.INFORMELL),
    FillerPhrase("Moment mal", "uebergang", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("Warte mal", "uebergang", [EmotionalTone.NACHDENKLICH, EmotionalTone.NEUGIERIG], Formality.INFORMELL),

    # NEUE ÜBERGANGS-FÜLLWÖRTER
    FillerPhrase("Andererseits", "uebergang", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Im Übrigen", "uebergang", [EmotionalTone.NEUTRAL], Formality.FORMELL),
    FillerPhrase("Zusätzlich", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Dazu kommt", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Nicht zu vergessen", "uebergang", [EmotionalTone.AUFGEREGT], Formality.NEUTRAL),
    FillerPhrase("Wenn ich so drüber nachdenke", "uebergang", [EmotionalTone.NACHDENKLICH], Formality.INFORMELL),
    FillerPhrase("Im Grunde genommen", "uebergang", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Letztendlich", "uebergang", [EmotionalTone.NACHDENKLICH], Formality.NEUTRAL),
    FillerPhrase("Schließlich", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Abgesehen davon", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Ansonsten", "uebergang", [EmotionalTone.NEUTRAL], Formality.INFORMELL),
    FillerPhrase("Nichtsdestotrotz", "uebergang", [EmotionalTone.NACHDENKLICH], Formality.FORMELL),
    FillerPhrase("Gleichzeitig", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Dabei", "uebergang", [EmotionalTone.NEUTRAL], Formality.NEUTRAL),
    FillerPhrase("Bevor ich es vergesse", "uebergang", [EmotionalTone.AUFGEREGT], Formality.INFORMELL),
]


# ============================================================================
# EMOTIONS-AUSDRÜCKE
# ============================================================================

EMOTION_EXPRESSIONS: Dict[EmotionalTone, List[str]] = {
    EmotionalTone.FREUDIG: [
        "Yay", "Juhu", "Hurra", "Toll", "Super", "Klasse", "Prima",
        "Wunderbar", "Fantastisch", "Großartig", "Herrlich", "Fabelhaft",
        "Das ist ja toll", "Wie schön", "Einfach wunderbar",
        # Kemonomimi
        "Nyaa~!", "Mew~!", "Yay~!", "Waaah~!"
    ],
    EmotionalTone.TRAURIG: [
        "Oh nein", "Schade", "Wie traurig", "Das tut mir leid", "Seufz",
        "Leider", "Bedauerlicherweise", "Das ist schade",
        # Kemonomimi
        "Mew...", "Nyuu...", "Sniff..."
    ],
    EmotionalTone.AUFGEREGT: [
        "Wow", "Oh", "Ohh", "Ahh", "Unglaublich", "Wahnsinn", "Krass",
        "Das ist ja", "Mensch", "Boah", "Echt jetzt",
        # Kemonomimi
        "Nya~!", "Kyaa~!", "Waaah~!"
    ],
    EmotionalTone.RUHIG: [
        "Hmm", "Nun", "Ja", "So ist es", "Tatsächlich", "Gewiss",
        "In der Tat", "Allerdings",
        # Kemonomimi
        "Purrr~", "Hmhm~"
    ],
    EmotionalTone.NEUGIERIG: [
        "Oh", "Hm", "Interessant", "Wirklich", "Ach so", "Oho",
        "Das ist interessant", "Faszinierend", "Spannend",
        # Kemonomimi
        "Nya?", "Hm~?", "Oh~?"
    ],
    EmotionalTone.BESORGT: [
        "Oh je", "Hm", "Ach", "Nun ja", "Das klingt", "Ich hoffe",
        "Das macht mir Sorgen", "Oh nein",
        # Kemonomimi
        "Nyuu...", "Mew..."
    ],
    EmotionalTone.LIEBEVOLL: [
        "Aww", "Oh", "Wie süß", "Das ist lieb", "Herzchen",
        "Das freut mich", "Wie schön",
        # Kemonomimi
        "Nyaa~", "Purrr~", "Mew~", "Uwu~"
    ],
    EmotionalTone.VERSPIELT: [
        "Hehe", "Hihi", "Ehehe", "Fufufu", "Tehe", "Hihihi",
        "Ehehehe", "Nanu",
        # Kemonomimi
        "Nya~", "Nyahaha~", "Ehehe~", "Fufufu~"
    ],
    EmotionalTone.NACHDENKLICH: [
        "Hmm", "Nun ja", "Tja", "Lass mich überlegen", "Ich denke",
        "Vielleicht", "Möglicherweise", "Das ist",
        # Kemonomimi
        "Hm~...", "Nyaa..."
    ],
    EmotionalTone.NEUTRAL: [
        "Nun", "Also", "Ja", "So", "Okay", "Gut", "Alles klar",
        "Verstehe", "Aha", "Hmhm"
    ]
}


# ============================================================================
# VARIABLE PLATZHALTER-WERTE
# ============================================================================

PLACEHOLDER_VALUES: Dict[str, List[str]] = {
    "zeitangabe": [
        "heute", "gestern", "morgen", "später", "früher", "jetzt", "bald",
        "gleich", "nachher", "vorhin", "kürzlich", "neulich", "letztens",
        "Tag", "Morgen", "Abend", "Nacht"
    ],
    "adverb": [
        "wirklich", "sehr", "total", "echt", "ziemlich", "ganz", "absolut",
        "unglaublich", "wahnsinnig", "mega", "super", "extrem", "besonders"
    ],
    "adjektiv_positiv": [
        "toll", "super", "wunderbar", "fantastisch", "großartig", "schön",
        "herrlich", "fabelhaft", "genial", "klasse", "prima", "spitze",
        "erstaunlich", "beeindruckend", "bezaubernd", "entzückend"
    ],
    "adjektiv_negativ": [
        "traurig", "schade", "schlecht", "schwierig", "kompliziert",
        "ärgerlich", "frustrierend", "enttäuschend", "beunruhigend"
    ],
    "adjektiv_neutral": [
        "interessant", "anders", "neu", "alt", "normal", "üblich",
        "gewöhnlich", "besonders", "speziell"
    ]
}


# ============================================================================
# SATZSTRUKTUR-ENGINE
# ============================================================================

class SentenceStructureEngine:
    """Engine für variable Satzstrukturen und natürliche Sprache"""

    def __init__(self):
        self.templates = {t.id: t for t in SENTENCE_TEMPLATES}
        self.fillers = FILLER_PHRASES
        self.emotions = EMOTION_EXPRESSIONS
        self.placeholders = PLACEHOLDER_VALUES

    def get_template(
        self,
        sentence_type: Optional[SentenceType] = None,
        emotional_tone: Optional[EmotionalTone] = None,
        formality: Optional[Formality] = None,
        is_kemonomimi: bool = False
    ) -> Optional[SentenceTemplate]:
        """Wählt ein passendes Template basierend auf Kriterien"""
        candidates = list(self.templates.values())

        # Filter nach Satztyp
        if sentence_type:
            candidates = [t for t in candidates if t.sentence_type == sentence_type]

        # Filter nach emotionalem Ton
        if emotional_tone:
            candidates = [t for t in candidates if emotional_tone in t.emotional_tones]

        # Filter nach Formalität
        if formality:
            candidates = [t for t in candidates if t.formality == formality]

        # Filter nach Kemonomimi
        if is_kemonomimi:
            kemo_candidates = [t for t in candidates if t.is_kemonomimi]
            if kemo_candidates:
                candidates = kemo_candidates
        elif not is_kemonomimi:
            # Bevorzuge nicht-Kemonomimi wenn nicht explizit gewünscht
            non_kemo = [t for t in candidates if not t.is_kemonomimi]
            if non_kemo:
                candidates = non_kemo

        if not candidates:
            return None

        # Gewichtete Auswahl
        weights = [t.weight for t in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]

    def get_filler(
        self,
        position: str,
        emotional_tone: Optional[EmotionalTone] = None,
        formality: Optional[Formality] = None,
        is_kemonomimi: bool = False
    ) -> Optional[str]:
        """Wählt eine passende Füllphrase"""
        candidates = [f for f in self.fillers if f.position == position]

        # Filter nach emotionalem Ton
        if emotional_tone:
            tone_match = [f for f in candidates if emotional_tone in f.emotional_tones]
            if tone_match:
                candidates = tone_match

        # Filter nach Formalität
        if formality:
            formality_match = [f for f in candidates
                            if abs(list(Formality).index(f.formality) -
                                  list(Formality).index(formality)) <= 1]
            if formality_match:
                candidates = formality_match

        # Filter nach Kemonomimi
        if is_kemonomimi:
            kemo = [f for f in candidates if f.is_kemonomimi]
            if kemo:
                candidates = kemo
        else:
            candidates = [f for f in candidates if not f.is_kemonomimi]

        if not candidates:
            return None

        weights = [f.weight for f in candidates]
        return random.choices(candidates, weights=weights, k=1)[0].phrase

    def get_emotion_expression(
        self,
        emotional_tone: EmotionalTone,
        is_kemonomimi: bool = False
    ) -> str:
        """Gibt einen emotionalen Ausdruck zurück"""
        expressions = self.emotions.get(emotional_tone, self.emotions[EmotionalTone.NEUTRAL])

        if is_kemonomimi:
            # Bevorzuge Kemonomimi-Ausdrücke (die mit ~ oder japanischen Lauten)
            kemo = [e for e in expressions if "~" in e or any(
                x in e.lower() for x in ["nya", "mew", "uwu", "kyaa"]
            )]
            if kemo:
                return random.choice(kemo)

        return random.choice(expressions)

    def fill_template(
        self,
        template: SentenceTemplate,
        context: SentenceContext,
        custom_values: Optional[Dict[str, str]] = None
    ) -> str:
        """Füllt ein Template mit passenden Werten"""
        result = template.pattern
        values = custom_values or {}

        # Merge mit context variables
        values = {**context.variables, **values}

        for placeholder in template.placeholders:
            if placeholder in values:
                result = result.replace("{" + placeholder + "}", values[placeholder])
            elif placeholder == "fuellwort":
                filler = self.get_filler(
                    "anfang" if "{fuellwort}" in template.pattern[:20] else "mitte",
                    context.emotional_tone,
                    context.formality,
                    context.is_kemonomimi
                )
                if filler:
                    result = result.replace("{fuellwort}", filler)
                else:
                    result = result.replace("{fuellwort}", "")
            elif placeholder == "emotion":
                emotion = self.get_emotion_expression(
                    context.emotional_tone,
                    context.is_kemonomimi
                )
                result = result.replace("{emotion}", emotion)
            elif placeholder == "adverb":
                result = result.replace("{adverb}", random.choice(self.placeholders["adverb"]))
            elif placeholder == "zeitangabe":
                result = result.replace("{zeitangabe}", random.choice(self.placeholders["zeitangabe"]))
            elif placeholder == "adjektiv":
                if context.emotional_tone in [EmotionalTone.FREUDIG, EmotionalTone.AUFGEREGT,
                                               EmotionalTone.LIEBEVOLL, EmotionalTone.VERSPIELT]:
                    adj_list = self.placeholders["adjektiv_positiv"]
                elif context.emotional_tone in [EmotionalTone.TRAURIG, EmotionalTone.BESORGT]:
                    adj_list = self.placeholders["adjektiv_negativ"]
                else:
                    adj_list = self.placeholders["adjektiv_neutral"]
                result = result.replace("{adjektiv}", random.choice(adj_list))

        # Cleanup: Entferne leere Platzhalter und doppelte Leerzeichen
        result = re.sub(r'\{[^}]+\}', '', result)
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r'\s+([.,!?])', r'\1', result)

        return result

    def generate_sentence(
        self,
        context: SentenceContext,
        custom_values: Optional[Dict[str, str]] = None
    ) -> str:
        """Generiert einen vollständigen Satz"""
        template = self.get_template(
            context.sentence_type,
            context.emotional_tone,
            context.formality,
            context.is_kemonomimi
        )

        if not template:
            return ""

        return self.fill_template(template, context, custom_values)

    def add_natural_fillers(
        self,
        text: str,
        context: SentenceContext
    ) -> str:
        """Fügt natürliche Füllwörter zu einem Text hinzu"""
        if not context.use_fillers:
            return text

        sentences = re.split(r'(?<=[.!?])\s+', text)
        result_sentences = []

        for i, sentence in enumerate(sentences):
            if random.random() < context.filler_density:
                # Füge Anfangs-Füllwort hinzu
                if not any(sentence.startswith(f.phrase) for f in self.fillers if f.position == "anfang"):
                    filler = self.get_filler("anfang", context.emotional_tone,
                                            context.formality, context.is_kemonomimi)
                    if filler:
                        sentence = f"{filler}, {sentence[0].lower()}{sentence[1:]}"

            # Füge gelegentlich Übergangs-Füllwörter hinzu
            if i > 0 and random.random() < context.filler_density * 0.5:
                filler = self.get_filler("uebergang", context.emotional_tone,
                                        context.formality, context.is_kemonomimi)
                if filler:
                    sentence = f"{filler}, {sentence[0].lower()}{sentence[1:]}"

            result_sentences.append(sentence)

        return " ".join(result_sentences)

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über verfügbare Templates und Phrasen"""
        template_by_type = {}
        for t in self.templates.values():
            key = t.sentence_type.value
            template_by_type[key] = template_by_type.get(key, 0) + 1

        filler_by_position = {}
        for f in self.fillers:
            filler_by_position[f.position] = filler_by_position.get(f.position, 0) + 1

        return {
            "total_templates": len(self.templates),
            "templates_by_type": template_by_type,
            "total_fillers": len(self.fillers),
            "fillers_by_position": filler_by_position,
            "emotion_expressions": sum(len(v) for v in self.emotions.values()),
            "kemonomimi_templates": len([t for t in self.templates.values() if t.is_kemonomimi]),
            "kemonomimi_fillers": len([f for f in self.fillers if f.is_kemonomimi])
        }


# ============================================================================
# GLOBALER ZUGRIFF
# ============================================================================

_engine_instance: Optional[SentenceStructureEngine] = None


def get_sentence_engine() -> SentenceStructureEngine:
    """Gibt die globale Engine-Instanz zurück"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SentenceStructureEngine()
    return _engine_instance


def create_sentence_context(
    sentence_type: str = "aussage",
    emotional_tone: str = "neutral",
    formality: str = "neutral",
    use_fillers: bool = True,
    filler_density: float = 0.3,
    is_kemonomimi: bool = False,
    **variables
) -> SentenceContext:
    """Hilfsfunktion zum Erstellen eines Satzkontexts"""
    return SentenceContext(
        sentence_type=SentenceType(sentence_type),
        emotional_tone=EmotionalTone(emotional_tone),
        formality=Formality(formality),
        use_fillers=use_fillers,
        filler_density=filler_density,
        is_kemonomimi=is_kemonomimi,
        variables=variables
    )


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    engine = get_sentence_engine()
    stats = engine.get_statistics()

    print("=== Satzstruktur-Engine Statistiken ===")
    print(f"Templates gesamt: {stats['total_templates']}")
    print(f"Templates nach Typ: {stats['templates_by_type']}")
    print(f"Füllwörter gesamt: {stats['total_fillers']}")
    print(f"Füllwörter nach Position: {stats['fillers_by_position']}")
    print(f"Emotions-Ausdrücke: {stats['emotion_expressions']}")
    print(f"Kemonomimi Templates: {stats['kemonomimi_templates']}")
    print(f"Kemonomimi Füllwörter: {stats['kemonomimi_fillers']}")
