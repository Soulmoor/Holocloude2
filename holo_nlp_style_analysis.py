#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NLP Style Analysis v1.0                                                 ║
║  Erweiterte Sprachstil- und Persönlichkeitsanalyse für Holocloude             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FEATURES:                                                                    ║
║  1. Writing Style Analyzer - Formal/Informal, Komplexität, Lesbarkeit        ║
║  2. Personality Insights - Big Five Traits aus Text ableiten                 ║
║  3. Rhetorical Pattern Detector - Argumentationsstrukturen erkennen          ║
║  4. Tone Analyzer - Emotionale Färbung und Stimmung                          ║
║  5. Register Classifier - Sprachregister bestimmen                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Optimiert für Raspberry Pi - Keine schweren ML-Bibliotheken!                ║
║  Author: Kira & Claude                                                        ║
║  Version: 1.0                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum, auto

logger = logging.getLogger("HoloNLPStyleAnalysis")

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Main Classes
    "WritingStyleAnalyzer",
    "PersonalityInsights",
    "RhetoricalPatternDetector",
    "ToneAnalyzer",
    "RegisterClassifier",
    "StyleAnalysisEngine",

    # Data Classes
    "StyleProfile",
    "PersonalityProfile",
    "RhetoricalPattern",
    "ToneProfile",
    "RegisterProfile",
    "ReadabilityMetrics",

    # Enums
    "FormalityLevel",
    "WritingStyle",
    "PersonalityTrait",
    "RhetoricalDevice",
    "ToneType",
    "RegisterType",

    # Getter Functions
    "get_style_analysis_engine",
    "get_writing_style_analyzer",
    "get_personality_insights",
]

# =============================================================================
# ENUMS
# =============================================================================

class FormalityLevel(Enum):
    """Formalitätsstufen"""
    VERY_INFORMAL = 1    # Umgangssprache, Slang
    INFORMAL = 2         # Locker, freundlich
    NEUTRAL = 3          # Standard
    FORMAL = 4           # Förmlich
    VERY_FORMAL = 5      # Hochformell, akademisch


class WritingStyle(Enum):
    """Schreibstile"""
    NARRATIVE = auto()       # Erzählend
    DESCRIPTIVE = auto()     # Beschreibend
    EXPOSITORY = auto()      # Erklärend
    PERSUASIVE = auto()      # Überzeugend
    ARGUMENTATIVE = auto()   # Argumentierend
    INFORMATIVE = auto()     # Informativ
    CONVERSATIONAL = auto()  # Gesprächig
    TECHNICAL = auto()       # Technisch
    CREATIVE = auto()        # Kreativ
    ACADEMIC = auto()        # Akademisch


class PersonalityTrait(Enum):
    """Big Five Persönlichkeitsmerkmale"""
    OPENNESS = auto()           # Offenheit für Erfahrungen
    CONSCIENTIOUSNESS = auto()  # Gewissenhaftigkeit
    EXTRAVERSION = auto()       # Extraversion
    AGREEABLENESS = auto()      # Verträglichkeit
    NEUROTICISM = auto()        # Neurotizismus


class RhetoricalDevice(Enum):
    """Rhetorische Stilmittel"""
    METAPHOR = auto()        # Metapher
    SIMILE = auto()          # Vergleich
    ANAPHORA = auto()        # Anapher (Wiederholung am Satzanfang)
    RHETORICAL_QUESTION = auto()  # Rhetorische Frage
    HYPERBOLE = auto()       # Übertreibung
    LITOTES = auto()         # Untertreibung
    IRONY = auto()           # Ironie
    PARALLELISM = auto()     # Parallelismus
    ANTITHESIS = auto()      # Antithese
    TRICOLON = auto()        # Dreierfigur
    CLIMAX = auto()          # Klimax (Steigerung)
    ALLITERATION = auto()    # Alliteration
    CHIASMUS = auto()        # Chiasmus (Kreuzstellung)
    EUPHEMISM = auto()       # Euphemismus
    REPETITION = auto()      # Wiederholung


class ToneType(Enum):
    """Tonalitätstypen"""
    NEUTRAL = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    ENTHUSIASTIC = auto()
    SKEPTICAL = auto()
    CONFIDENT = auto()
    UNCERTAIN = auto()
    HUMOROUS = auto()
    SERIOUS = auto()
    EMPATHETIC = auto()
    CRITICAL = auto()
    SUPPORTIVE = auto()


class RegisterType(Enum):
    """Sprachregister"""
    FROZEN = auto()          # Rituell, unveränderlich (Gebete, Eide)
    FORMAL = auto()          # Offiziell, professionell
    CONSULTATIVE = auto()    # Beratend, halbformell
    CASUAL = auto()          # Umgangssprachlich
    INTIMATE = auto()        # Intim, persönlich


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ReadabilityMetrics:
    """Lesbarkeitsmetriken"""
    flesch_reading_ease: float  # 0-100, höher = leichter
    avg_sentence_length: float
    avg_word_length: float
    syllables_per_word: float
    complex_word_percentage: float
    vocabulary_richness: float  # Type-Token-Ratio
    grade_level: int  # Geschätzte Klassenstufe


@dataclass
class StyleProfile:
    """Stilprofil eines Textes"""
    formality: FormalityLevel
    formality_score: float  # 0.0 - 1.0
    writing_style: WritingStyle
    readability: ReadabilityMetrics
    sentence_variety: float  # Satzlängen-Varianz
    passive_voice_ratio: float
    question_ratio: float
    exclamation_ratio: float
    personal_pronoun_ratio: float
    hedging_score: float  # Abschwächungsgrad


@dataclass
class PersonalityProfile:
    """Persönlichkeitsprofil aus Text"""
    openness: float           # 0.0 - 1.0
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    dominant_traits: List[PersonalityTrait]
    linguistic_markers: Dict[str, List[str]]
    confidence: float


@dataclass
class RhetoricalPattern:
    """Ein erkanntes rhetorisches Muster"""
    device: RhetoricalDevice
    text: str
    position: int
    confidence: float
    explanation: str


@dataclass
class ToneProfile:
    """Tonalitätsprofil"""
    primary_tone: ToneType
    secondary_tones: List[ToneType]
    tone_scores: Dict[str, float]
    emotional_intensity: float  # 0.0 - 1.0
    subjectivity: float  # 0.0 - 1.0


@dataclass
class RegisterProfile:
    """Registerprofil"""
    register: RegisterType
    formality_score: float
    features: Dict[str, Any]


# =============================================================================
# WRITING STYLE ANALYZER
# =============================================================================

class WritingStyleAnalyzer:
    """
    Analysiert Schreibstil: Formalität, Lesbarkeit, Stilmerkmale.
    """

    def __init__(self):
        # Formale vs. informale Wörter
        self.formal_words = {
            "jedoch", "allerdings", "ferner", "überdies", "infolgedessen",
            "demzufolge", "indes", "mittels", "bezüglich", "hinsichtlich",
            "aufgrund", "zwecks", "gemäß", "entsprechend", "vermittels",
            "infolge", "betreffend", "diesbezüglich", "dementsprechend"
        }

        self.informal_words = {
            "echt", "mega", "super", "krass", "geil", "cool", "ne", "nee",
            "jo", "naja", "halt", "irgendwie", "so", "total", "voll",
            "verdammt", "mist", "blöd", "doof", "okay", "hey", "hi"
        }

        # Hedging-Ausdrücke (Abschwächungen)
        self.hedging_words = {
            "vielleicht", "möglicherweise", "eventuell", "gewissermaßen",
            "sozusagen", "irgendwie", "quasi", "mehr oder weniger",
            "könnte", "dürfte", "scheint", "anscheinend", "vermutlich",
            "wahrscheinlich", "tendenziell", "im gewissen sinne"
        }

        # Passiv-Indikatoren
        self.passive_indicators = [
            r"\bwird\s+\w+t\b", r"\bwurde\s+\w+t\b", r"\bwerden\s+\w+t\b",
            r"\bwurden\s+\w+t\b", r"\bworden\b", r"\bist\s+\w+t\s+worden\b"
        ]

        # Komplexe Wörter (lang + Fremdwörter)
        self.complex_word_endings = [
            "tion", "ität", "ismus", "ierung", "schaft", "heit", "keit",
            "ologie", "onomie", "graphie", "metrie", "analyse"
        ]

    def analyze(self, text: str) -> StyleProfile:
        """Analysiert den Schreibstil eines Textes"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        sentences = self._split_sentences(text)

        if not words or not sentences:
            return self._empty_profile()

        # Formalität berechnen
        formality_score = self._calculate_formality(words)
        formality_level = self._score_to_formality(formality_score)

        # Lesbarkeit berechnen
        readability = self._calculate_readability(text, words, sentences)

        # Schreibstil erkennen
        writing_style = self._detect_writing_style(text, text_lower, words)

        # Weitere Metriken
        sentence_lengths = [len(s.split()) for s in sentences]
        sentence_variety = self._calculate_variance(sentence_lengths) if sentence_lengths else 0.0

        passive_ratio = self._calculate_passive_ratio(text_lower)
        question_ratio = text.count("?") / len(sentences) if sentences else 0
        exclamation_ratio = text.count("!") / len(sentences) if sentences else 0

        personal_pronouns = ["ich", "du", "wir", "ihr", "mein", "dein", "unser"]
        personal_ratio = sum(1 for w in words if w in personal_pronouns) / len(words) if words else 0

        hedging_score = sum(1 for w in words if w in self.hedging_words) / len(words) if words else 0

        return StyleProfile(
            formality=formality_level,
            formality_score=formality_score,
            writing_style=writing_style,
            readability=readability,
            sentence_variety=sentence_variety,
            passive_voice_ratio=passive_ratio,
            question_ratio=question_ratio,
            exclamation_ratio=exclamation_ratio,
            personal_pronoun_ratio=personal_ratio,
            hedging_score=hedging_score
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Teilt Text in Sätze"""
        sentences = re.split(r'[.!?]+\s*', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_formality(self, words: List[str]) -> float:
        """Berechnet Formalitätsscore (0=informal, 1=formal)"""
        formal_count = sum(1 for w in words if w in self.formal_words)
        informal_count = sum(1 for w in words if w in self.informal_words)

        total = formal_count + informal_count
        if total == 0:
            return 0.5  # Neutral

        return formal_count / total

    def _score_to_formality(self, score: float) -> FormalityLevel:
        """Konvertiert Score zu FormalityLevel"""
        if score >= 0.8:
            return FormalityLevel.VERY_FORMAL
        elif score >= 0.6:
            return FormalityLevel.FORMAL
        elif score >= 0.4:
            return FormalityLevel.NEUTRAL
        elif score >= 0.2:
            return FormalityLevel.INFORMAL
        else:
            return FormalityLevel.VERY_INFORMAL

    def _calculate_readability(self, text: str, words: List[str],
                               sentences: List[str]) -> ReadabilityMetrics:
        """Berechnet Lesbarkeitsmetriken"""
        word_count = len(words)
        sentence_count = len(sentences)

        if word_count == 0 or sentence_count == 0:
            return ReadabilityMetrics(
                flesch_reading_ease=0,
                avg_sentence_length=0,
                avg_word_length=0,
                syllables_per_word=0,
                complex_word_percentage=0,
                vocabulary_richness=0,
                grade_level=0
            )

        # Durchschnittliche Satzlänge
        avg_sentence_length = word_count / sentence_count

        # Durchschnittliche Wortlänge
        avg_word_length = sum(len(w) for w in words) / word_count

        # Silben pro Wort (vereinfacht: Vokale zählen)
        total_syllables = sum(self._count_syllables(w) for w in words)
        syllables_per_word = total_syllables / word_count

        # Flesch Reading Ease (adaptiert für Deutsch)
        # Original: 206.835 - 1.015 * ASL - 84.6 * ASW
        # Deutsche Anpassung
        flesch = 180 - avg_sentence_length - (58.5 * syllables_per_word)
        flesch = max(0, min(100, flesch))

        # Komplexe Wörter (>3 Silben oder mit komplexen Endungen)
        complex_words = sum(
            1 for w in words
            if self._count_syllables(w) > 3 or any(w.endswith(e) for e in self.complex_word_endings)
        )
        complex_percentage = complex_words / word_count

        # Vokabularreichtum (Type-Token-Ratio)
        unique_words = len(set(words))
        vocabulary_richness = unique_words / word_count if word_count > 0 else 0

        # Geschätzte Klassenstufe (Wiener Sachtextformel adaptiert)
        grade_level = int(0.2 * avg_sentence_length + 0.3 * complex_percentage * 100)
        grade_level = max(1, min(13, grade_level))

        return ReadabilityMetrics(
            flesch_reading_ease=flesch,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            syllables_per_word=syllables_per_word,
            complex_word_percentage=complex_percentage,
            vocabulary_richness=vocabulary_richness,
            grade_level=grade_level
        )

    def _count_syllables(self, word: str) -> int:
        """Zählt Silben in einem deutschen Wort (vereinfacht)"""
        word = word.lower()
        vowels = "aeiouäöü"
        count = 0
        prev_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel

        # Mindestens eine Silbe
        return max(1, count)

    def _detect_writing_style(self, text: str, text_lower: str,
                              words: List[str]) -> WritingStyle:
        """Erkennt den vorherrschenden Schreibstil"""
        scores = defaultdict(float)

        # Narrative Indikatoren
        narrative_words = ["dann", "danach", "als", "plötzlich", "schließlich", "erzählte"]
        scores[WritingStyle.NARRATIVE] = sum(1 for w in words if w in narrative_words) / len(words) * 10

        # Deskriptive Indikatoren (Adjektive, Adverbien)
        descriptive_patterns = [r'\b\w+lich\b', r'\b\w+ig\b', r'\b\w+sam\b']
        for pattern in descriptive_patterns:
            scores[WritingStyle.DESCRIPTIVE] += len(re.findall(pattern, text_lower)) / len(words) * 5

        # Expository (Erklärend)
        expository_words = ["bedeutet", "heißt", "erklärt", "zeigt", "beweist", "nämlich"]
        scores[WritingStyle.EXPOSITORY] = sum(1 for w in words if w in expository_words) / len(words) * 10

        # Persuasive
        persuasive_words = ["müssen", "sollten", "unbedingt", "wichtig", "entscheidend"]
        scores[WritingStyle.PERSUASIVE] = sum(1 for w in words if w in persuasive_words) / len(words) * 10

        # Argumentative
        argumentative_words = ["weil", "deshalb", "daher", "folglich", "denn", "jedoch", "allerdings"]
        scores[WritingStyle.ARGUMENTATIVE] = sum(1 for w in words if w in argumentative_words) / len(words) * 10

        # Technical
        if any(w.endswith(e) for w in words for e in ["tion", "ierung", "system", "prozess"]):
            scores[WritingStyle.TECHNICAL] += 0.3

        # Conversational (Fragezeichen, persönliche Pronomen)
        if "?" in text:
            scores[WritingStyle.CONVERSATIONAL] += 0.2
        personal = sum(1 for w in words if w in ["ich", "du", "wir", "ihr"])
        scores[WritingStyle.CONVERSATIONAL] += personal / len(words) * 5

        # Höchsten Score finden
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return WritingStyle.INFORMATIVE

    def _calculate_passive_ratio(self, text: str) -> float:
        """Berechnet den Anteil passiver Konstruktionen"""
        passive_count = sum(len(re.findall(p, text)) for p in self.passive_indicators)
        sentence_count = len(self._split_sentences(text)) or 1
        return min(1.0, passive_count / sentence_count)

    def _calculate_variance(self, values: List[float]) -> float:
        """Berechnet Varianz einer Liste"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    def _empty_profile(self) -> StyleProfile:
        """Leeres Profil für leere Eingaben"""
        return StyleProfile(
            formality=FormalityLevel.NEUTRAL,
            formality_score=0.5,
            writing_style=WritingStyle.INFORMATIVE,
            readability=ReadabilityMetrics(0, 0, 0, 0, 0, 0, 0),
            sentence_variety=0,
            passive_voice_ratio=0,
            question_ratio=0,
            exclamation_ratio=0,
            personal_pronoun_ratio=0,
            hedging_score=0
        )


# =============================================================================
# PERSONALITY INSIGHTS
# =============================================================================

class PersonalityInsights:
    """
    Leitet Big Five Persönlichkeitsmerkmale aus Text ab.
    Basiert auf LIWC-ähnlichen Ansätzen.
    """

    def __init__(self):
        # Wort-Kategorien für jeden Trait
        self.trait_markers = self._build_trait_markers()

    def _build_trait_markers(self) -> Dict[PersonalityTrait, Dict[str, List[str]]]:
        """Wort-Marker für jeden Persönlichkeitstrait"""
        return {
            PersonalityTrait.OPENNESS: {
                "positive": [
                    "kreativ", "interessant", "neu", "idee", "kunst", "philosophie",
                    "abstrakt", "fantasie", "träumen", "vorstellen", "entdecken",
                    "erfinden", "originell", "ungewöhnlich", "neugierig", "vielfältig",
                    "kulturell", "intellektuell", "innovativ", "experimentell"
                ],
                "negative": [
                    "langweilig", "gewöhnlich", "normal", "üblich", "standard",
                    "traditionell", "konservativ", "altmodisch"
                ]
            },
            PersonalityTrait.CONSCIENTIOUSNESS: {
                "positive": [
                    "planen", "organisieren", "sorgfältig", "genau", "pünktlich",
                    "zuverlässig", "verantwortlich", "diszipliniert", "ordentlich",
                    "systematisch", "gründlich", "pflichtbewusst", "gewissenhaft",
                    "strukturiert", "effizient", "zielorientiert"
                ],
                "negative": [
                    "vergessen", "chaotisch", "unordentlich", "spontan", "impulsiv",
                    "nachlässig", "schlampig", "verspätet"
                ]
            },
            PersonalityTrait.EXTRAVERSION: {
                "positive": [
                    "sprechen", "reden", "feiern", "treffen", "leute", "freunde",
                    "gesellig", "aktivität", "energie", "begeistert", "aufgeregt",
                    "gesellschaft", "party", "gruppe", "team", "unterhalten",
                    "enthusiastisch", "lebhaft", "gesprächig"
                ],
                "negative": [
                    "allein", "ruhig", "still", "zurückgezogen", "einsam",
                    "introvertiert", "schüchtern"
                ]
            },
            PersonalityTrait.AGREEABLENESS: {
                "positive": [
                    "helfen", "unterstützen", "freundlich", "nett", "lieb",
                    "verständnisvoll", "mitfühlend", "kooperativ", "harmonisch",
                    "vertrauen", "ehrlich", "fair", "tolerant", "geduldig",
                    "rücksichtsvoll", "hilfsbereit", "großzügig"
                ],
                "negative": [
                    "streit", "konflikt", "wütend", "ärgerlich", "kritisch",
                    "misstrauisch", "egoistisch", "konkurrenz"
                ]
            },
            PersonalityTrait.NEUROTICISM: {
                "positive": [  # Hoher Neurotizismus
                    "sorge", "angst", "nervös", "stress", "besorgt", "unsicher",
                    "ängstlich", "beunruhigt", "erschöpft", "traurig", "deprimiert",
                    "frustriert", "verärgert", "überfordert", "verzweifelt"
                ],
                "negative": [  # Niedriger Neurotizismus
                    "ruhig", "entspannt", "gelassen", "sicher", "stabil",
                    "ausgeglichen", "zufrieden", "optimistisch"
                ]
            }
        }

    def analyze(self, text: str) -> PersonalityProfile:
        """Analysiert Persönlichkeitsmerkmale aus Text"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        if not words:
            return self._empty_profile()

        word_count = len(words)
        trait_scores = {}
        linguistic_markers = {}

        for trait, markers in self.trait_markers.items():
            positive_matches = [w for w in words if any(m in w for m in markers["positive"])]
            negative_matches = [w for w in words if any(m in w for m in markers["negative"])]

            pos_count = len(positive_matches)
            neg_count = len(negative_matches)

            # Score berechnen
            if trait == PersonalityTrait.NEUROTICISM:
                # Bei Neurotizismus sind "positive" Marker = hoher Neurotizismus
                score = (pos_count - neg_count) / word_count * 10 + 0.5
            else:
                score = (pos_count - neg_count * 0.5) / word_count * 10 + 0.5

            # Auf 0-1 begrenzen
            score = max(0.0, min(1.0, score))
            trait_scores[trait] = score
            linguistic_markers[trait.name] = positive_matches[:5]

        # Dominante Traits bestimmen (Top 2 mit Score > 0.6)
        sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
        dominant = [t for t, s in sorted_traits if s > 0.6][:2]

        # Confidence basierend auf Textlänge und Marker-Dichte
        total_markers = sum(len(m) for m in linguistic_markers.values())
        confidence = min(0.9, 0.3 + (total_markers / word_count) * 5 + (word_count / 1000) * 0.2)

        return PersonalityProfile(
            openness=trait_scores[PersonalityTrait.OPENNESS],
            conscientiousness=trait_scores[PersonalityTrait.CONSCIENTIOUSNESS],
            extraversion=trait_scores[PersonalityTrait.EXTRAVERSION],
            agreeableness=trait_scores[PersonalityTrait.AGREEABLENESS],
            neuroticism=trait_scores[PersonalityTrait.NEUROTICISM],
            dominant_traits=dominant,
            linguistic_markers=linguistic_markers,
            confidence=confidence
        )

    def _empty_profile(self) -> PersonalityProfile:
        """Leeres Profil"""
        return PersonalityProfile(
            openness=0.5,
            conscientiousness=0.5,
            extraversion=0.5,
            agreeableness=0.5,
            neuroticism=0.5,
            dominant_traits=[],
            linguistic_markers={},
            confidence=0.0
        )

    def get_personality_description(self, profile: PersonalityProfile) -> str:
        """Generiert eine Beschreibung der Persönlichkeit"""
        descriptions = []

        if profile.openness > 0.6:
            descriptions.append("kreativ und offen für neue Erfahrungen")
        elif profile.openness < 0.4:
            descriptions.append("praktisch orientiert und traditionsbewusst")

        if profile.conscientiousness > 0.6:
            descriptions.append("organisiert und zuverlässig")
        elif profile.conscientiousness < 0.4:
            descriptions.append("flexibel und spontan")

        if profile.extraversion > 0.6:
            descriptions.append("gesellig und energiegeladen")
        elif profile.extraversion < 0.4:
            descriptions.append("ruhig und nachdenklich")

        if profile.agreeableness > 0.6:
            descriptions.append("kooperativ und einfühlsam")
        elif profile.agreeableness < 0.4:
            descriptions.append("direkt und wettbewerbsorientiert")

        if profile.neuroticism > 0.6:
            descriptions.append("emotional sensibel")
        elif profile.neuroticism < 0.4:
            descriptions.append("emotional stabil")

        if descriptions:
            return "Die Person wirkt " + ", ".join(descriptions) + "."
        return "Keine eindeutige Persönlichkeitstendenz erkennbar."


# =============================================================================
# RHETORICAL PATTERN DETECTOR
# =============================================================================

class RhetoricalPatternDetector:
    """
    Erkennt rhetorische Stilmittel und Argumentationsstrukturen.
    """

    def __init__(self):
        self.device_patterns = self._build_device_patterns()

    def _build_device_patterns(self) -> Dict[RhetoricalDevice, List[Dict[str, Any]]]:
        """Patterns für rhetorische Stilmittel"""
        return {
            RhetoricalDevice.METAPHOR: [
                {"pattern": r"(\w+)\s+ist\s+(?:ein[e]?\s+)?(\w+)", "type": "is-metaphor"},
                {"pattern": r"(\w+)\s+wie\s+(?:ein[e]?\s+)?(\w+)", "type": "explicit-metaphor"},
            ],
            RhetoricalDevice.SIMILE: [
                {"pattern": r"wie\s+(?:ein[e]?\s+)?(\w+)", "type": "simile"},
                {"pattern": r"als\s+(?:ob|wenn)\s+", "type": "als-ob-simile"},
            ],
            RhetoricalDevice.ANAPHORA: [
                {"pattern": r"^(\w+(?:\s+\w+)?).+\.\s*\1", "type": "sentence-anaphora"},
            ],
            RhetoricalDevice.RHETORICAL_QUESTION: [
                {"pattern": r"(?:wer|was|wie|warum|weshalb)\s+(?:\w+\s+)*\?(?!\s*[a-zäöü])", "type": "wh-question"},
                {"pattern": r"ist\s+(?:das|es)\s+nicht\s+.+\?", "type": "negation-question"},
                {"pattern": r"kann\s+(?:man|jemand)\s+.+\?", "type": "possibility-question"},
            ],
            RhetoricalDevice.HYPERBOLE: [
                {"pattern": r"\b(nie|niemals|immer|ewig|unendlich|absolut|total)\b", "type": "absolute"},
                {"pattern": r"\b(millionen|tausende?|hunderte?)\s+(?:mal|von)", "type": "number-hyperbole"},
                {"pattern": r"\b(größte|beste|schlimmste|wichtigste)\s+(?:aller|jemals)", "type": "superlative"},
            ],
            RhetoricalDevice.LITOTES: [
                {"pattern": r"nicht\s+(?:un\w+|schlecht|übel)", "type": "double-negation"},
                {"pattern": r"(?:kein\w*\s+)?(?:geringer|kleiner|unbedeutender)", "type": "understatement"},
            ],
            RhetoricalDevice.IRONY: [
                {"pattern": r"(?:na\s+)?(?:toll|super|wunderbar|fantastisch)[,!]", "type": "praise-irony"},
                {"pattern": r"(?:ach|oh)\s+(?:wie\s+)?(?:schön|toll)", "type": "exclamation-irony"},
            ],
            RhetoricalDevice.PARALLELISM: [
                {"pattern": r"(\w+\s+\w+),\s*\1", "type": "word-parallel"},
            ],
            RhetoricalDevice.ANTITHESIS: [
                {"pattern": r"nicht\s+(\w+),?\s+sondern\s+(\w+)", "type": "nicht-sondern"},
                {"pattern": r"einerseits.+andererseits", "type": "einerseits-andererseits"},
                {"pattern": r"zwar.+aber", "type": "zwar-aber"},
            ],
            RhetoricalDevice.TRICOLON: [
                {"pattern": r"(\w+),\s*(\w+)\s+und\s+(\w+)", "type": "triple-list"},
            ],
            RhetoricalDevice.CLIMAX: [
                {"pattern": r"(\w+),?\s+(\w+)er,?\s+(?:am\s+)?(\w+)sten", "type": "comparative-climax"},
            ],
            RhetoricalDevice.ALLITERATION: [
                {"pattern": r"\b([a-zäöü])\w+\s+\1\w+\s+\1\w+\b", "type": "triple-alliteration"},
            ],
            RhetoricalDevice.EUPHEMISM: [
                {"pattern": r"(?:entschlafen|von uns gegangen|ableben)", "type": "death-euphemism"},
                {"pattern": r"(?:freisetzen|freigestellt|sozialverträglich)", "type": "job-euphemism"},
            ],
            RhetoricalDevice.REPETITION: [
                {"pattern": r"\b(\w{4,})\b.+\b\1\b", "type": "word-repetition"},
            ],
        }

    def detect(self, text: str) -> List[RhetoricalPattern]:
        """Erkennt rhetorische Stilmittel im Text"""
        results = []
        text_lower = text.lower()

        for device, patterns in self.device_patterns.items():
            for pattern_info in patterns:
                matches = re.finditer(pattern_info["pattern"], text_lower, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    results.append(RhetoricalPattern(
                        device=device,
                        text=match.group(0),
                        position=match.start(),
                        confidence=0.7,
                        explanation=self._get_explanation(device, pattern_info["type"])
                    ))

        # Deduplizieren (gleiche Position + Device)
        seen = set()
        unique_results = []
        for r in results:
            key = (r.device, r.position)
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results

    def _get_explanation(self, device: RhetoricalDevice, pattern_type: str) -> str:
        """Gibt eine Erklärung für das erkannte Stilmittel"""
        explanations = {
            RhetoricalDevice.METAPHOR: "Bildhafte Übertragung einer Bedeutung",
            RhetoricalDevice.SIMILE: "Expliziter Vergleich mit 'wie' oder 'als'",
            RhetoricalDevice.ANAPHORA: "Wiederholung am Satz-/Versanfang",
            RhetoricalDevice.RHETORICAL_QUESTION: "Frage ohne erwartete Antwort",
            RhetoricalDevice.HYPERBOLE: "Übertreibung zur Verstärkung",
            RhetoricalDevice.LITOTES: "Untertreibung durch doppelte Verneinung",
            RhetoricalDevice.IRONY: "Gegenteil des Gesagten ist gemeint",
            RhetoricalDevice.PARALLELISM: "Syntaktische Gleichstruktur",
            RhetoricalDevice.ANTITHESIS: "Gegenüberstellung von Gegensätzen",
            RhetoricalDevice.TRICOLON: "Dreiergruppe von Elementen",
            RhetoricalDevice.CLIMAX: "Steigerung",
            RhetoricalDevice.ALLITERATION: "Gleicher Anlaut bei aufeinanderfolgenden Wörtern",
            RhetoricalDevice.EUPHEMISM: "Beschönigende Umschreibung",
            RhetoricalDevice.REPETITION: "Wiederholung zur Betonung",
        }
        return explanations.get(device, "Rhetorisches Stilmittel")

    def get_argumentation_structure(self, text: str) -> Dict[str, Any]:
        """Analysiert die Argumentationsstruktur"""
        structures = {
            "claims": [],
            "evidence": [],
            "counterarguments": [],
            "conclusions": []
        }

        # Behauptungen
        claim_patterns = [
            r"ich (?:behaupte|meine|denke),?\s+dass\s+(.+)",
            r"(?:es ist (?:klar|offensichtlich)),?\s+dass\s+(.+)",
            r"(?:tatsache ist|fakt ist),?\s+dass\s+(.+)"
        ]

        for pattern in claim_patterns:
            matches = re.findall(pattern, text.lower())
            structures["claims"].extend(matches)

        # Belege
        evidence_patterns = [
            r"(?:weil|da|denn)\s+(.+)",
            r"(?:die studie|die forschung|experten)\s+(?:zeigt|belegt|sagt)\s+(.+)",
            r"(?:laut|gemäß|entsprechend)\s+(.+)"
        ]

        for pattern in evidence_patterns:
            matches = re.findall(pattern, text.lower())
            structures["evidence"].extend(matches)

        # Gegenargumente
        counter_patterns = [
            r"(?:obwohl|zwar|jedoch|allerdings)\s+(.+)",
            r"(?:man könnte einwenden|kritiker sagen)\s+(.+)"
        ]

        for pattern in counter_patterns:
            matches = re.findall(pattern, text.lower())
            structures["counterarguments"].extend(matches)

        # Schlussfolgerungen
        conclusion_patterns = [
            r"(?:deshalb|daher|folglich|somit)\s+(.+)",
            r"(?:zusammenfassend|abschließend|letztendlich)\s+(.+)"
        ]

        for pattern in conclusion_patterns:
            matches = re.findall(pattern, text.lower())
            structures["conclusions"].extend(matches)

        return structures


# =============================================================================
# TONE ANALYZER
# =============================================================================

class ToneAnalyzer:
    """
    Analysiert die Tonalität und emotionale Färbung eines Textes.
    """

    def __init__(self):
        self.tone_markers = self._build_tone_markers()

    def _build_tone_markers(self) -> Dict[ToneType, List[str]]:
        """Wort-Marker für verschiedene Tonalitäten"""
        return {
            ToneType.POSITIVE: [
                "gut", "toll", "super", "wunderbar", "fantastisch", "großartig",
                "freude", "glücklich", "begeistert", "zufrieden", "erfolg",
                "liebe", "schön", "perfekt", "exzellent", "hervorragend"
            ],
            ToneType.NEGATIVE: [
                "schlecht", "schrecklich", "furchtbar", "katastrophal", "miserabel",
                "traurig", "enttäuscht", "verärgert", "wütend", "frustriert",
                "hass", "problem", "fehler", "versagen", "mangelhaft"
            ],
            ToneType.ENTHUSIASTIC: [
                "wow", "unglaublich", "wahnsinn", "irre", "krass", "genial",
                "umwerfend", "phänomenal", "sensationell", "überwältigend"
            ],
            ToneType.SKEPTICAL: [
                "zweifelhaft", "fraglich", "unsicher", "bezweifle", "kaum",
                "angeblich", "vermeintlich", "sogenannt", "wirklich"
            ],
            ToneType.CONFIDENT: [
                "sicher", "gewiss", "zweifellos", "definitiv", "absolut",
                "klar", "eindeutig", "offensichtlich", "selbstverständlich"
            ],
            ToneType.UNCERTAIN: [
                "vielleicht", "möglicherweise", "eventuell", "womöglich",
                "könnte", "dürfte", "scheint", "vermutlich"
            ],
            ToneType.HUMOROUS: [
                "haha", "lol", "witzig", "lustig", "komisch", "spaß",
                "scherz", "witz", "amüsant", "lachen"
            ],
            ToneType.SERIOUS: [
                "ernst", "wichtig", "kritisch", "dringend", "entscheidend",
                "schwerwiegend", "gravierend", "bedeutsam", "wesentlich"
            ],
            ToneType.EMPATHETIC: [
                "verstehe", "nachvollziehen", "mitfühlen", "fühle mit",
                "kann mir vorstellen", "das muss", "tut mir leid", "bedaure"
            ],
            ToneType.CRITICAL: [
                "kritisiere", "mangelhaft", "unzureichend", "problematisch",
                "fragwürdig", "bedenklich", "zweifelhaft", "schwach"
            ],
            ToneType.SUPPORTIVE: [
                "unterstütze", "helfe", "gerne", "natürlich", "selbstverständlich",
                "kein problem", "mache ich", "zähle auf mich"
            ]
        }

    def analyze(self, text: str) -> ToneProfile:
        """Analysiert die Tonalität eines Textes"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        if not words:
            return ToneProfile(
                primary_tone=ToneType.NEUTRAL,
                secondary_tones=[],
                tone_scores={},
                emotional_intensity=0.0,
                subjectivity=0.0
            )

        word_count = len(words)
        tone_scores = {}

        for tone_type, markers in self.tone_markers.items():
            matches = sum(1 for w in words if any(m in w for m in markers))
            score = matches / word_count * 10  # Normalisiert
            tone_scores[tone_type.name] = min(1.0, score)

        # Primärer und sekundärer Ton
        sorted_tones = sorted(
            [(t, tone_scores.get(t.name, 0)) for t in ToneType],
            key=lambda x: x[1],
            reverse=True
        )

        primary = sorted_tones[0][0] if sorted_tones[0][1] > 0.1 else ToneType.NEUTRAL
        secondary = [t for t, s in sorted_tones[1:3] if s > 0.05]

        # Emotionale Intensität (basierend auf Ausrufezeichen, Superlative, etc.)
        intensity_markers = text.count("!") + len(re.findall(r'\b\w+ste[rns]?\b', text_lower))
        emotional_intensity = min(1.0, intensity_markers / (len(words) / 10 + 1))

        # Subjektivität (Ich-Form, Meinungsmarker)
        subjectivity_markers = ["ich", "mein", "finde", "glaube", "meine", "denke"]
        subjectivity = sum(1 for w in words if w in subjectivity_markers) / word_count * 5
        subjectivity = min(1.0, subjectivity)

        return ToneProfile(
            primary_tone=primary,
            secondary_tones=secondary,
            tone_scores=tone_scores,
            emotional_intensity=emotional_intensity,
            subjectivity=subjectivity
        )


# =============================================================================
# REGISTER CLASSIFIER
# =============================================================================

class RegisterClassifier:
    """
    Klassifiziert das Sprachregister (formal bis intim).
    """

    def __init__(self):
        self.register_features = self._build_register_features()

    def _build_register_features(self) -> Dict[RegisterType, Dict[str, Any]]:
        """Features für verschiedene Register"""
        return {
            RegisterType.FROZEN: {
                "markers": ["hiermit", "kraft", "eid", "gelobe", "schwöre", "amen"],
                "patterns": [r"im namen des", r"kraft meines amtes"],
                "features": {"fixed_phrases": True, "archaic_words": True}
            },
            RegisterType.FORMAL: {
                "markers": ["sehr geehrte", "hochachtungsvoll", "mit freundlichen grüßen",
                           "gestatten sie", "dürfte ich", "wäre es möglich"],
                "patterns": [r"bezugnehmend auf", r"in anbetracht"],
                "features": {"sie_form": True, "complex_sentences": True}
            },
            RegisterType.CONSULTATIVE: {
                "markers": ["könnten sie", "würden sie", "gerne", "vielleicht",
                           "wenn es ihnen recht ist", "darf ich fragen"],
                "patterns": [r"wie kann ich ihnen helfen"],
                "features": {"polite_forms": True, "professional": True}
            },
            RegisterType.CASUAL: {
                "markers": ["hey", "hi", "na", "echt", "cool", "krass", "okay",
                           "kein ding", "alles klar", "logo"],
                "patterns": [r"was geht", r"keine ahnung"],
                "features": {"du_form": True, "slang": True, "abbreviations": True}
            },
            RegisterType.INTIMATE: {
                "markers": ["schatz", "liebling", "baby", "süße", "maus",
                           "hab dich lieb", "vermisse dich", "knutsch"],
                "patterns": [r"ich liebe dich", r"du bist mein"],
                "features": {"terms_of_endearment": True, "private": True}
            }
        }

    def classify(self, text: str) -> RegisterProfile:
        """Klassifiziert das Sprachregister"""
        text_lower = text.lower()

        register_scores = defaultdict(float)

        for register, features in self.register_features.items():
            # Marker-Score
            for marker in features["markers"]:
                if marker in text_lower:
                    register_scores[register] += 1.0

            # Pattern-Score
            for pattern in features["patterns"]:
                if re.search(pattern, text_lower):
                    register_scores[register] += 1.5

        # Sie vs. Du Form
        sie_count = len(re.findall(r'\b(sie|ihnen|ihrer|ihr)\b', text_lower))
        du_count = len(re.findall(r'\b(du|dir|dich|dein)\b', text_lower))

        if sie_count > du_count:
            register_scores[RegisterType.FORMAL] += 0.5
            register_scores[RegisterType.CONSULTATIVE] += 0.3
        elif du_count > sie_count:
            register_scores[RegisterType.CASUAL] += 0.5
            register_scores[RegisterType.INTIMATE] += 0.3

        # Höchstes Register bestimmen
        if register_scores:
            best_register = max(register_scores.items(), key=lambda x: x[1])
            detected_register = best_register[0]
            formality_score = self._register_to_formality(detected_register)
        else:
            detected_register = RegisterType.CONSULTATIVE
            formality_score = 0.5

        detected_features = {}
        if detected_register in self.register_features:
            detected_features = self.register_features[detected_register]["features"]

        return RegisterProfile(
            register=detected_register,
            formality_score=formality_score,
            features=detected_features
        )

    def _register_to_formality(self, register: RegisterType) -> float:
        """Konvertiert Register zu Formalitätsscore"""
        mapping = {
            RegisterType.FROZEN: 1.0,
            RegisterType.FORMAL: 0.8,
            RegisterType.CONSULTATIVE: 0.5,
            RegisterType.CASUAL: 0.3,
            RegisterType.INTIMATE: 0.1
        }
        return mapping.get(register, 0.5)


# =============================================================================
# STYLE ANALYSIS ENGINE (Unified Interface)
# =============================================================================

class StyleAnalysisEngine:
    """
    Vereinte Engine für Stilanalyse.
    Kombiniert alle Komponenten.
    """

    def __init__(self):
        self.style_analyzer = WritingStyleAnalyzer()
        self.personality_insights = PersonalityInsights()
        self.rhetorical_detector = RhetoricalPatternDetector()
        self.tone_analyzer = ToneAnalyzer()
        self.register_classifier = RegisterClassifier()

    def analyze(self, text: str) -> Dict[str, Any]:
        """Vollständige Stilanalyse eines Textes"""
        # Schreibstil
        style = self.style_analyzer.analyze(text)

        # Persönlichkeit
        personality = self.personality_insights.analyze(text)

        # Rhetorische Muster
        rhetorical_patterns = self.rhetorical_detector.detect(text)

        # Tonalität
        tone = self.tone_analyzer.analyze(text)

        # Register
        register = self.register_classifier.classify(text)

        return {
            "writing_style": {
                "formality": style.formality.name,
                "formality_score": style.formality_score,
                "style_type": style.writing_style.name,
                "passive_ratio": style.passive_voice_ratio,
                "question_ratio": style.question_ratio,
                "hedging_score": style.hedging_score,
                "readability": {
                    "flesch_score": style.readability.flesch_reading_ease,
                    "avg_sentence_length": style.readability.avg_sentence_length,
                    "vocabulary_richness": style.readability.vocabulary_richness,
                    "grade_level": style.readability.grade_level
                }
            },
            "personality": {
                "openness": personality.openness,
                "conscientiousness": personality.conscientiousness,
                "extraversion": personality.extraversion,
                "agreeableness": personality.agreeableness,
                "neuroticism": personality.neuroticism,
                "dominant_traits": [t.name for t in personality.dominant_traits],
                "confidence": personality.confidence
            },
            "rhetorical_devices": [
                {
                    "device": p.device.name,
                    "text": p.text,
                    "explanation": p.explanation
                }
                for p in rhetorical_patterns[:10]  # Top 10
            ],
            "tone": {
                "primary": tone.primary_tone.name,
                "secondary": [t.name for t in tone.secondary_tones],
                "emotional_intensity": tone.emotional_intensity,
                "subjectivity": tone.subjectivity
            },
            "register": {
                "type": register.register.name,
                "formality_score": register.formality_score
            },
            "original_text": text
        }

    def get_style_summary(self, text: str) -> str:
        """Gibt eine kurze Stil-Zusammenfassung"""
        style = self.style_analyzer.analyze(text)
        tone = self.tone_analyzer.analyze(text)
        register = self.register_classifier.classify(text)

        parts = []
        parts.append(f"Stil: {style.writing_style.name}")
        parts.append(f"Formalität: {style.formality.name}")
        parts.append(f"Ton: {tone.primary_tone.name}")
        parts.append(f"Register: {register.register.name}")
        parts.append(f"Lesbarkeit: {style.readability.flesch_reading_ease:.0f}/100")

        return " | ".join(parts)


# =============================================================================
# SINGLETON INSTANCES & GETTERS
# =============================================================================

_style_analysis_engine: Optional[StyleAnalysisEngine] = None
_writing_style_analyzer: Optional[WritingStyleAnalyzer] = None
_personality_insights: Optional[PersonalityInsights] = None


def get_style_analysis_engine() -> StyleAnalysisEngine:
    """Gibt die Singleton-Instanz der StyleAnalysisEngine zurück"""
    global _style_analysis_engine
    if _style_analysis_engine is None:
        _style_analysis_engine = StyleAnalysisEngine()
        logger.info("StyleAnalysisEngine initialisiert")
    return _style_analysis_engine


def get_writing_style_analyzer() -> WritingStyleAnalyzer:
    """Gibt die Singleton-Instanz des WritingStyleAnalyzers zurück"""
    global _writing_style_analyzer
    if _writing_style_analyzer is None:
        _writing_style_analyzer = WritingStyleAnalyzer()
        logger.info("WritingStyleAnalyzer initialisiert")
    return _writing_style_analyzer


def get_personality_insights() -> PersonalityInsights:
    """Gibt die Singleton-Instanz der PersonalityInsights zurück"""
    global _personality_insights
    if _personality_insights is None:
        _personality_insights = PersonalityInsights()
        logger.info("PersonalityInsights initialisiert")
    return _personality_insights


# =============================================================================
# DEMO & TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO NLP Style Analysis - Demo")
    print("=" * 60)

    engine = get_style_analysis_engine()

    test_texts = [
        """Sehr geehrte Damen und Herren,
        bezugnehmend auf Ihr Schreiben vom 15. Januar möchte ich Ihnen mitteilen,
        dass wir Ihre Anfrage sorgfältig geprüft haben. Nach eingehender Analyse
        sind wir zu dem Schluss gekommen, dass eine Zusammenarbeit für beide
        Seiten von Vorteil wäre.
        Mit freundlichen Grüßen""",

        """Hey, was geht? Hab echt keine Ahnung was ich machen soll.
        Das Projekt ist voll im Eimer und der Chef nervt total.
        Können wir uns heute Abend treffen? Ich brauch echt mal ne Pause!""",

        """Die Studie zeigt eindeutig: Nicht nur ist der Klimawandel real,
        sondern er beschleunigt sich auch dramatisch. Einerseits schmelzen
        die Polkappen, andererseits steigen die Meeresspiegel. Wer kann
        angesichts dieser Fakten noch zweifeln? Die Zeit zum Handeln ist jetzt!""",

        """Ich denke oft über Kreativität nach. Was bedeutet es, kreativ zu sein?
        Vielleicht ist es die Fähigkeit, neue Verbindungen zu sehen, wo andere
        nur das Gewohnte erkennen. Träumen wir nicht alle davon, etwas
        Außergewöhnliches zu erschaffen?"""
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n{'─' * 60}")
        print(f"TEXT {i}:")
        print(f"{'─' * 60}")
        print(text[:100] + "..." if len(text) > 100 else text)

        result = engine.analyze(text)

        print(f"\n📝 SCHREIBSTIL:")
        print(f"   Typ: {result['writing_style']['style_type']}")
        print(f"   Formalität: {result['writing_style']['formality']} ({result['writing_style']['formality_score']:.2f})")
        print(f"   Lesbarkeit: {result['writing_style']['readability']['flesch_score']:.0f}/100")
        print(f"   Klassenstufe: ~{result['writing_style']['readability']['grade_level']}")

        print(f"\n🧠 PERSÖNLICHKEIT:")
        print(f"   Offenheit: {result['personality']['openness']:.2f}")
        print(f"   Gewissenhaftigkeit: {result['personality']['conscientiousness']:.2f}")
        print(f"   Extraversion: {result['personality']['extraversion']:.2f}")
        print(f"   Verträglichkeit: {result['personality']['agreeableness']:.2f}")
        print(f"   Neurotizismus: {result['personality']['neuroticism']:.2f}")
        if result['personality']['dominant_traits']:
            print(f"   Dominante Traits: {', '.join(result['personality']['dominant_traits'])}")

        print(f"\n🎭 TONALITÄT:")
        print(f"   Primär: {result['tone']['primary']}")
        if result['tone']['secondary']:
            print(f"   Sekundär: {', '.join(result['tone']['secondary'])}")
        print(f"   Emotionale Intensität: {result['tone']['emotional_intensity']:.2f}")
        print(f"   Subjektivität: {result['tone']['subjectivity']:.2f}")

        print(f"\n📋 REGISTER: {result['register']['type']}")

        if result['rhetorical_devices']:
            print(f"\n🎨 RHETORISCHE STILMITTEL:")
            for device in result['rhetorical_devices'][:3]:
                print(f"   - {device['device']}: \"{device['text'][:40]}...\"")

    print("\n" + "=" * 60)
    print("Demo abgeschlossen!")
