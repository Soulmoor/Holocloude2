#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holocloude - Variable Satzstrukturen & Phrasen-Baukasten
=========================================================

Dieses Modul bietet:
- 50+ variable Satzstruktur-Templates
- Phrasen-Baukasten für natürliche Füllwörter
- Dynamische Satzkonstruktion basierend auf Kontext

Version: 1.0.0
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
    # BEGRÜSSUNGEN (10 Templates)
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

    # -------------------------------------------------------------------------
    # AUSSAGEN (15 Templates)
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

    # -------------------------------------------------------------------------
    # FRAGEN (12 Templates)
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

    # -------------------------------------------------------------------------
    # REAKTIONEN (10 Templates)
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

    # -------------------------------------------------------------------------
    # ERZÄHLUNGEN (8 Templates)
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

    # -------------------------------------------------------------------------
    # VERABSCHIEDUNGEN (5 Templates)
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

    # -------------------------------------------------------------------------
    # WÜNSCHE & AUFFORDERUNGEN (5 Templates)
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

    # -------------------------------------------------------------------------
    # ERKLÄRUNGEN (5 Templates)
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
]


# ============================================================================
# FÜLLWÖRTER & PHRASEN-BAUKASTEN
# ============================================================================

FILLER_PHRASES: List[FillerPhrase] = [
    # -------------------------------------------------------------------------
    # ANFANGS-FÜLLWÖRTER
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

    # -------------------------------------------------------------------------
    # MITTEN-FÜLLWÖRTER
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

    # -------------------------------------------------------------------------
    # END-FÜLLWÖRTER
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

    # -------------------------------------------------------------------------
    # ÜBERGANGS-FÜLLWÖRTER
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
