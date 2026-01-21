#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  HOLO NLP Context Understanding v1.0                                          ║
║  Erweiterte Kontextverständnis-Engine für Holocloude                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FEATURES:                                                                    ║
║  1. Discourse Tracker - Versteht Zusammenhänge über mehrere Sätze            ║
║  2. Coreference Resolution - "Er sagte..." → Wer ist "er"?                   ║
║  3. Topic Memory - Was wurde vorher besprochen?                              ║
║  4. Context Window Management - Relevante Historie verwalten                 ║
║  5. Discourse Relations - Kausalität, Kontrast, Elaboration erkennen         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Optimiert für Raspberry Pi - Keine schweren ML-Bibliotheken!                ║
║  Author: Kira & Claude                                                        ║
║  Version: 1.0                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import math
import logging
from typing import Dict, List, Optional, Tuple, Set, Any, Deque
from dataclasses import dataclass, field
from collections import Counter, defaultdict, deque
from datetime import datetime
from enum import Enum, auto

logger = logging.getLogger("HoloNLPContextUnderstanding")

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Main Classes
    "DiscourseTracker",
    "AdvancedCoreferenceResolver",
    "TopicMemory",
    "ContextUnderstandingEngine",

    # Data Classes
    "DiscourseSegment",
    "DiscourseRelation",
    "CorefMention",
    "CorefCluster",
    "Topic",
    "TopicShift",
    "ConversationContext",

    # Enums
    "DiscourseRelationType",
    "MentionType",
    "TopicRelevance",

    # Getter Functions
    "get_context_understanding_engine",
    "get_discourse_tracker",
    "get_topic_memory",
]

# =============================================================================
# ENUMS
# =============================================================================

class DiscourseRelationType(Enum):
    """Typen von Diskursrelationen zwischen Sätzen"""
    ELABORATION = auto()      # Details hinzufügen
    CONTRAST = auto()         # Gegensatz
    CAUSE = auto()            # Ursache
    RESULT = auto()           # Folge/Ergebnis
    CONDITION = auto()        # Bedingung
    TEMPORAL = auto()         # Zeitliche Abfolge
    COMPARISON = auto()       # Vergleich
    EXAMPLE = auto()          # Beispiel
    SUMMARY = auto()          # Zusammenfassung
    CONTINUATION = auto()     # Fortführung
    EXPLANATION = auto()      # Erklärung
    BACKGROUND = auto()       # Hintergrundinformation
    CONCESSION = auto()       # Einräumung
    ATTRIBUTION = auto()      # Zuschreibung (jemand sagt/denkt)
    UNKNOWN = auto()          # Unbekannt


class MentionType(Enum):
    """Typen von Erwähnungen für Koreference"""
    PROPER_NOUN = auto()      # Eigenname: "Maria", "Berlin"
    COMMON_NOUN = auto()      # Gattungsname: "der Mann", "die Stadt"
    PRONOUN = auto()          # Pronomen: "er", "sie", "es"
    DEMONSTRATIVE = auto()    # Demonstrativ: "dieser", "jener"
    REFLEXIVE = auto()        # Reflexiv: "sich"
    POSSESSIVE = auto()       # Possessiv: "sein", "ihr"
    RELATIVE = auto()         # Relativ: "der", "die", "das" (Relativsatz)
    ZERO = auto()             # Ellipse/ausgelassen


class TopicRelevance(Enum):
    """Relevanz eines Themas"""
    MAIN = auto()             # Hauptthema
    SECONDARY = auto()        # Nebenthema
    MENTIONED = auto()        # Nur erwähnt
    BACKGROUND = auto()       # Hintergrund
    CONCLUDED = auto()        # Abgeschlossen


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DiscourseSegment:
    """Ein Segment im Diskurs (typisch ein Satz)"""
    text: str
    index: int
    tokens: List[str]
    entities: List[str]
    main_verb: Optional[str]
    subject: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    speaker: str = "user"


@dataclass
class DiscourseRelation:
    """Eine Relation zwischen zwei Diskurssegmenten"""
    source_idx: int
    target_idx: int
    relation_type: DiscourseRelationType
    confidence: float
    markers: List[str]  # Diskursmarker die erkannt wurden


@dataclass
class CorefMention:
    """Eine einzelne Erwähnung in der Koreference"""
    text: str
    mention_type: MentionType
    sentence_idx: int
    start_pos: int
    end_pos: int
    gender: Optional[str] = None  # m, f, n, pl
    number: Optional[str] = None  # sg, pl
    person: Optional[int] = None  # 1, 2, 3
    animacy: Optional[str] = None  # animate, inanimate


@dataclass
class CorefCluster:
    """Ein Cluster von koreferenten Erwähnungen"""
    cluster_id: int
    mentions: List[CorefMention]
    canonical_mention: str  # Hauptreferenz
    entity_type: str  # PERSON, ORG, LOC, THING, ABSTRACT
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Topic:
    """Ein Gesprächsthema"""
    topic_id: int
    name: str
    keywords: Set[str]
    first_mentioned: int  # Segment-Index
    last_mentioned: int
    mention_count: int
    relevance: TopicRelevance
    related_entities: List[str]
    subtopics: List[str] = field(default_factory=list)
    sentiment: float = 0.0  # -1.0 bis 1.0


@dataclass
class TopicShift:
    """Ein Themenwechsel im Gespräch"""
    from_topic: Optional[str]
    to_topic: str
    segment_idx: int
    shift_type: str  # smooth, abrupt, return
    confidence: float


@dataclass
class ConversationContext:
    """Gesamtkontext einer Konversation"""
    segments: List[DiscourseSegment]
    relations: List[DiscourseRelation]
    coref_clusters: List[CorefCluster]
    active_topics: List[Topic]
    topic_history: List[TopicShift]
    current_speaker: str
    conversation_length: int
    summary: str = ""


# =============================================================================
# DISCOURSE TRACKER
# =============================================================================

class DiscourseTracker:
    """
    Verfolgt und analysiert die Diskursstruktur über mehrere Sätze hinweg.
    Erkennt Diskursrelationen wie Kausalität, Kontrast, Elaboration.
    """

    def __init__(self, max_segments: int = 50):
        self.segments: Deque[DiscourseSegment] = deque(maxlen=max_segments)
        self.relations: List[DiscourseRelation] = []
        self.max_segments = max_segments

        # Diskursmarker für Deutsch
        self.discourse_markers = {
            DiscourseRelationType.CAUSE: [
                "weil", "da", "denn", "aufgrund", "wegen", "dadurch dass",
                "durch", "infolge", "angesichts", "deshalb", "daher",
                "aus diesem grund", "somit", "folglich"
            ],
            DiscourseRelationType.RESULT: [
                "deshalb", "daher", "darum", "deswegen", "folglich",
                "infolgedessen", "somit", "also", "demnach", "sodass",
                "so dass", "weshalb", "weswegen"
            ],
            DiscourseRelationType.CONTRAST: [
                "aber", "jedoch", "allerdings", "dennoch", "trotzdem",
                "obwohl", "obgleich", "wenngleich", "hingegen", "dagegen",
                "andererseits", "im gegensatz", "während", "stattdessen",
                "vielmehr", "nichtsdestotrotz", "gleichwohl"
            ],
            DiscourseRelationType.CONDITION: [
                "wenn", "falls", "sofern", "vorausgesetzt", "angenommen",
                "unter der bedingung", "im falle", "gesetzt den fall",
                "es sei denn", "nur wenn", "solange"
            ],
            DiscourseRelationType.TEMPORAL: [
                "dann", "danach", "anschließend", "später", "zuerst",
                "zunächst", "schließlich", "bevor", "nachdem", "während",
                "als", "sobald", "inzwischen", "mittlerweile", "seitdem",
                "bis", "ehe", "zuvor", "vorher", "hinterher"
            ],
            DiscourseRelationType.ELABORATION: [
                "genauer gesagt", "das heißt", "nämlich", "insbesondere",
                "vor allem", "besonders", "zum beispiel", "beispielsweise",
                "und zwar", "also", "sprich", "mit anderen worten"
            ],
            DiscourseRelationType.COMPARISON: [
                "wie", "als", "ebenso", "genauso", "ähnlich", "gleich",
                "im vergleich", "verglichen mit", "analog", "entsprechend"
            ],
            DiscourseRelationType.EXAMPLE: [
                "zum beispiel", "beispielsweise", "etwa", "so zum beispiel",
                "wie etwa", "z.b.", "bspw.", "exemplarisch"
            ],
            DiscourseRelationType.SUMMARY: [
                "zusammenfassend", "kurz gesagt", "insgesamt", "im großen und ganzen",
                "alles in allem", "letztendlich", "fazit", "abschließend",
                "zusammengefasst", "resümierend"
            ],
            DiscourseRelationType.CONTINUATION: [
                "außerdem", "zudem", "darüber hinaus", "ferner", "weiterhin",
                "überdies", "des weiteren", "zusätzlich", "auch", "und",
                "ebenso", "gleichermaßen"
            ],
            DiscourseRelationType.EXPLANATION: [
                "denn", "nämlich", "schließlich", "immerhin", "da ja",
                "erklärend", "begründet durch"
            ],
            DiscourseRelationType.CONCESSION: [
                "obwohl", "obgleich", "wenngleich", "auch wenn", "selbst wenn",
                "trotz", "trotzdem", "dennoch", "zwar...aber", "gewiss...aber"
            ],
            DiscourseRelationType.ATTRIBUTION: [
                "sagt", "sagte", "meint", "meinte", "behauptet", "erklärt",
                "laut", "nach", "zufolge", "gemäß", "wie...sagt"
            ]
        }

        # Patterns für Satzstruktur
        self.sentence_split_pattern = re.compile(r'[.!?]+\s*')
        self.token_pattern = re.compile(r'\b\w+\b', re.UNICODE)

    def add_text(self, text: str, speaker: str = "user") -> List[DiscourseSegment]:
        """Fügt Text hinzu und analysiert die Diskursstruktur"""
        sentences = self._split_sentences(text)
        new_segments = []

        for sentence in sentences:
            if not sentence.strip():
                continue

            segment = self._create_segment(sentence, speaker)
            self.segments.append(segment)
            new_segments.append(segment)

            # Relationen zum vorherigen Segment finden
            if len(self.segments) >= 2:
                relation = self._find_relation(
                    self.segments[-2],
                    self.segments[-1]
                )
                if relation:
                    self.relations.append(relation)

        return new_segments

    def _split_sentences(self, text: str) -> List[str]:
        """Teilt Text in Sätze auf"""
        # Einfache Satz-Segmentierung
        sentences = self.sentence_split_pattern.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def _create_segment(self, text: str, speaker: str) -> DiscourseSegment:
        """Erstellt ein DiscourseSegment aus einem Satz"""
        tokens = self.token_pattern.findall(text.lower())

        # Einfache Entitätserkennung (Großgeschriebene Wörter)
        entities = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß]+\b', text)

        # Einfache Verb- und Subjekterkennung
        main_verb = self._find_main_verb(tokens)
        subject = self._find_subject(text)

        return DiscourseSegment(
            text=text,
            index=len(self.segments),
            tokens=tokens,
            entities=entities,
            main_verb=main_verb,
            subject=subject,
            speaker=speaker
        )

    def _find_main_verb(self, tokens: List[str]) -> Optional[str]:
        """Findet das Hauptverb (vereinfacht)"""
        # Deutsche Verbendungen
        verb_endings = ["en", "st", "t", "e", "te", "tet", "ten"]

        for token in tokens:
            if len(token) > 3:
                for ending in verb_endings:
                    if token.endswith(ending):
                        return token
        return None

    def _find_subject(self, text: str) -> Optional[str]:
        """Findet das Subjekt (vereinfacht)"""
        # Erstes Nomen oder Pronomen vor dem Verb
        words = text.split()
        if words:
            # Vereinfacht: erstes Wort wenn großgeschrieben
            first = words[0]
            if first[0].isupper() and first.lower() not in ["und", "oder", "aber", "denn"]:
                return first
        return None

    def _find_relation(self, source: DiscourseSegment, target: DiscourseSegment) -> Optional[DiscourseRelation]:
        """Findet die Diskursrelation zwischen zwei Segmenten"""
        target_text = target.text.lower()
        best_relation = None
        best_confidence = 0.0
        found_markers = []

        for rel_type, markers in self.discourse_markers.items():
            for marker in markers:
                if marker in target_text:
                    # Prüfe Position des Markers (am Anfang = höhere Konfidenz)
                    pos_factor = 1.0 if target_text.strip().startswith(marker) else 0.7
                    confidence = 0.8 * pos_factor

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_relation = rel_type
                        found_markers = [marker]

        if best_relation:
            return DiscourseRelation(
                source_idx=source.index,
                target_idx=target.index,
                relation_type=best_relation,
                confidence=best_confidence,
                markers=found_markers
            )

        # Default: Continuation wenn kein Marker gefunden
        return DiscourseRelation(
            source_idx=source.index,
            target_idx=target.index,
            relation_type=DiscourseRelationType.CONTINUATION,
            confidence=0.5,
            markers=[]
        )

    def get_discourse_structure(self) -> Dict[str, Any]:
        """Gibt die komplette Diskursstruktur zurück"""
        return {
            "segments": [
                {
                    "index": s.index,
                    "text": s.text,
                    "speaker": s.speaker,
                    "entities": s.entities,
                    "main_verb": s.main_verb,
                    "subject": s.subject
                }
                for s in self.segments
            ],
            "relations": [
                {
                    "from": r.source_idx,
                    "to": r.target_idx,
                    "type": r.relation_type.name,
                    "confidence": r.confidence,
                    "markers": r.markers
                }
                for r in self.relations
            ],
            "segment_count": len(self.segments),
            "relation_count": len(self.relations)
        }

    def get_causal_chains(self) -> List[List[int]]:
        """Findet kausale Ketten (Ursache-Wirkungs-Zusammenhänge)"""
        causal_types = {DiscourseRelationType.CAUSE, DiscourseRelationType.RESULT}

        chains = []
        visited = set()

        for relation in self.relations:
            if relation.relation_type in causal_types and relation.source_idx not in visited:
                chain = [relation.source_idx, relation.target_idx]
                visited.add(relation.source_idx)

                # Kette erweitern
                current = relation.target_idx
                for r in self.relations:
                    if r.source_idx == current and r.relation_type in causal_types:
                        chain.append(r.target_idx)
                        current = r.target_idx
                        visited.add(r.source_idx)

                if len(chain) >= 2:
                    chains.append(chain)

        return chains

    def summarize_discourse(self) -> str:
        """Erstellt eine kurze Zusammenfassung der Diskursstruktur"""
        if not self.segments:
            return "Keine Segmente vorhanden."

        # Zähle Relationstypen
        rel_counts = Counter(r.relation_type.name for r in self.relations)

        # Finde Hauptentitäten
        all_entities = []
        for s in self.segments:
            all_entities.extend(s.entities)
        top_entities = Counter(all_entities).most_common(3)

        summary_parts = []
        summary_parts.append(f"Diskurs mit {len(self.segments)} Segmenten")

        if top_entities:
            entities_str = ", ".join(e[0] for e in top_entities)
            summary_parts.append(f"Hauptentitäten: {entities_str}")

        if rel_counts:
            top_rel = rel_counts.most_common(2)
            rel_str = ", ".join(f"{r[0]}({r[1]}x)" for r in top_rel)
            summary_parts.append(f"Häufigste Relationen: {rel_str}")

        return ". ".join(summary_parts)


# =============================================================================
# ADVANCED COREFERENCE RESOLVER
# =============================================================================

class AdvancedCoreferenceResolver:
    """
    Erweiterte Koreference-Resolution für Deutsch.
    Löst Pronomen wie "er", "sie", "es" zu ihren Referenten auf.
    """

    def __init__(self):
        self.clusters: List[CorefCluster] = []
        self.mention_cache: Dict[str, CorefMention] = {}
        self.next_cluster_id = 0

        # Pronomen-Kategorien für Deutsch
        self.pronouns = {
            # Personalpronomen
            "er": {"gender": "m", "number": "sg", "person": 3, "animacy": "animate"},
            "sie": {"gender": "f", "number": "sg", "person": 3, "animacy": "animate"},  # oder pl
            "es": {"gender": "n", "number": "sg", "person": 3, "animacy": "inanimate"},
            "ihn": {"gender": "m", "number": "sg", "person": 3, "animacy": "animate"},
            "ihm": {"gender": "m", "number": "sg", "person": 3, "animacy": "animate"},
            "ihr": {"gender": "f", "number": "sg", "person": 3, "animacy": "animate"},
            "ihnen": {"gender": None, "number": "pl", "person": 3, "animacy": "animate"},

            # Demonstrativpronomen
            "dieser": {"gender": "m", "number": "sg", "person": 3, "animacy": None},
            "diese": {"gender": "f", "number": "sg", "person": 3, "animacy": None},
            "dieses": {"gender": "n", "number": "sg", "person": 3, "animacy": None},
            "jener": {"gender": "m", "number": "sg", "person": 3, "animacy": None},
            "jene": {"gender": "f", "number": "sg", "person": 3, "animacy": None},
            "jenes": {"gender": "n", "number": "sg", "person": 3, "animacy": None},

            # Possessivpronomen
            "sein": {"gender": "m", "number": "sg", "person": 3, "animacy": "animate"},
            "seine": {"gender": "m", "number": "sg", "person": 3, "animacy": "animate"},
            "seiner": {"gender": "m", "number": "sg", "person": 3, "animacy": "animate"},
            "ihr": {"gender": "f", "number": "sg", "person": 3, "animacy": "animate"},
            "ihre": {"gender": "f", "number": "sg", "person": 3, "animacy": "animate"},

            # Reflexivpronomen
            "sich": {"gender": None, "number": None, "person": 3, "animacy": None},
        }

        # Gender-Hinweise für deutsche Nomen
        self.gender_hints = {
            # Männliche Endungen/Wörter
            "m": ["er", "or", "ist", "ant", "ent", "ling", "mann", "vater", "bruder",
                  "sohn", "onkel", "herr", "könig", "arzt", "lehrer", "professor"],
            # Weibliche Endungen/Wörter
            "f": ["in", "ung", "heit", "keit", "schaft", "tion", "tät", "frau", "mutter",
                  "schwester", "tochter", "tante", "dame", "königin", "ärztin", "lehrerin"],
            # Neutrale Endungen/Wörter
            "n": ["chen", "lein", "ment", "um", "ma", "kind", "mädchen", "buch",
                  "haus", "auto", "fenster", "unternehmen"]
        }

        # Bekannte Namen mit Gender
        self.name_genders = {
            # Männliche Namen
            "peter": "m", "hans": "m", "michael": "m", "thomas": "m", "andreas": "m",
            "stefan": "m", "christian": "m", "martin": "m", "markus": "m", "daniel": "m",
            "alexander": "m", "matthias": "m", "tobias": "m", "sebastian": "m", "jan": "m",
            "max": "m", "felix": "m", "paul": "m", "leon": "m", "lukas": "m",
            # Weibliche Namen
            "maria": "f", "anna": "f", "julia": "f", "sarah": "f", "lisa": "f",
            "laura": "f", "sandra": "f", "sabine": "f", "petra": "f", "nicole": "f",
            "claudia": "f", "stefanie": "f", "melanie": "f", "katharina": "f", "christina": "f",
            "sophie": "f", "emma": "f", "mia": "f", "hannah": "f", "lena": "f",
        }

    def resolve(self, segments: List[DiscourseSegment]) -> List[CorefCluster]:
        """Hauptmethode zur Koreference-Resolution"""
        self.clusters = []
        self.next_cluster_id = 0

        # Schritt 1: Alle Mentions extrahieren
        all_mentions = []
        for segment in segments:
            mentions = self._extract_mentions(segment)
            all_mentions.extend(mentions)

        # Schritt 2: Cluster bilden
        for mention in all_mentions:
            self._assign_to_cluster(mention, all_mentions)

        return self.clusters

    def _extract_mentions(self, segment: DiscourseSegment) -> List[CorefMention]:
        """Extrahiert alle Mentions aus einem Segment"""
        mentions = []
        text = segment.text
        text_lower = text.lower()

        # 1. Pronomen finden
        for pronoun, attrs in self.pronouns.items():
            for match in re.finditer(rf'\b{pronoun}\b', text_lower):
                mention = CorefMention(
                    text=pronoun,
                    mention_type=MentionType.PRONOUN,
                    sentence_idx=segment.index,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    gender=attrs["gender"],
                    number=attrs["number"],
                    person=attrs["person"],
                    animacy=attrs["animacy"]
                )
                mentions.append(mention)

        # 2. Eigennamen finden (Großgeschriebene Wörter)
        for match in re.finditer(r'\b([A-ZÄÖÜ][a-zäöüß]+)\b', text):
            name = match.group(1)
            name_lower = name.lower()

            # Gender bestimmen
            gender = self.name_genders.get(name_lower)
            if not gender:
                gender = self._guess_gender(name)

            mention = CorefMention(
                text=name,
                mention_type=MentionType.PROPER_NOUN,
                sentence_idx=segment.index,
                start_pos=match.start(),
                end_pos=match.end(),
                gender=gender,
                number="sg",
                person=3,
                animacy="animate" if gender in ["m", "f"] else None
            )
            mentions.append(mention)

        # 3. Definite NPs finden ("der Mann", "die Frau", etc.)
        definite_patterns = [
            (r'\b(der|die|das)\s+(\w+)\b', {"der": "m", "die": "f", "das": "n"}),
        ]

        for pattern, gender_map in definite_patterns:
            for match in re.finditer(pattern, text_lower):
                article = match.group(1)
                noun = match.group(2)
                full_text = match.group(0)

                mention = CorefMention(
                    text=full_text,
                    mention_type=MentionType.COMMON_NOUN,
                    sentence_idx=segment.index,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    gender=gender_map.get(article),
                    number="sg",
                    person=3,
                    animacy=self._guess_animacy(noun)
                )
                mentions.append(mention)

        return mentions

    def _guess_gender(self, word: str) -> Optional[str]:
        """Errät das Geschlecht eines Wortes anhand von Endungen"""
        word_lower = word.lower()

        for gender, endings in self.gender_hints.items():
            for ending in endings:
                if word_lower.endswith(ending) or word_lower == ending:
                    return gender

        return None

    def _guess_animacy(self, word: str) -> Optional[str]:
        """Errät ob ein Wort belebt oder unbelebt ist"""
        word_lower = word.lower()

        animate_words = ["mann", "frau", "kind", "mensch", "person", "leute",
                        "tier", "hund", "katze", "vogel"]
        inanimate_words = ["ding", "sache", "objekt", "haus", "auto", "buch",
                          "tisch", "stuhl", "fenster", "tür"]

        for w in animate_words:
            if w in word_lower:
                return "animate"

        for w in inanimate_words:
            if w in word_lower:
                return "inanimate"

        return None

    def _assign_to_cluster(self, mention: CorefMention, all_mentions: List[CorefMention]) -> None:
        """Weist eine Mention einem Cluster zu"""
        # Suche passenden Cluster
        best_cluster = None
        best_score = 0.0

        for cluster in self.clusters:
            score = self._compute_compatibility(mention, cluster)
            if score > best_score and score > 0.5:
                best_score = score
                best_cluster = cluster

        if best_cluster:
            best_cluster.mentions.append(mention)
        else:
            # Nur für Nicht-Pronomen neuen Cluster erstellen
            if mention.mention_type != MentionType.PRONOUN:
                new_cluster = CorefCluster(
                    cluster_id=self.next_cluster_id,
                    mentions=[mention],
                    canonical_mention=mention.text,
                    entity_type=self._determine_entity_type(mention)
                )
                self.clusters.append(new_cluster)
                self.next_cluster_id += 1
            else:
                # Pronomen ohne Antezedent: zu letztem passenden Cluster
                for cluster in reversed(self.clusters):
                    if self._compute_compatibility(mention, cluster) > 0.3:
                        cluster.mentions.append(mention)
                        break

    def _compute_compatibility(self, mention: CorefMention, cluster: CorefCluster) -> float:
        """Berechnet Kompatibilität zwischen Mention und Cluster"""
        score = 0.0

        # Canonical Mention vergleichen
        canonical = cluster.mentions[0] if cluster.mentions else None
        if not canonical:
            return 0.0

        # Gender-Match
        if mention.gender and canonical.gender:
            if mention.gender == canonical.gender:
                score += 0.4
            else:
                return 0.0  # Gender-Mismatch = keine Koreference

        # Number-Match
        if mention.number and canonical.number:
            if mention.number == canonical.number:
                score += 0.3
            else:
                return 0.0  # Number-Mismatch = keine Koreference

        # Animacy-Match
        if mention.animacy and canonical.animacy:
            if mention.animacy == canonical.animacy:
                score += 0.2

        # Distanz-Penalty
        distance = abs(mention.sentence_idx - canonical.sentence_idx)
        distance_penalty = max(0, 1.0 - distance * 0.1)
        score *= distance_penalty

        return score

    def _determine_entity_type(self, mention: CorefMention) -> str:
        """Bestimmt den Entity-Typ"""
        if mention.animacy == "animate":
            if mention.gender in ["m", "f"]:
                return "PERSON"
            return "ANIMATE"
        elif mention.animacy == "inanimate":
            return "THING"

        # Nach Mention-Typ
        if mention.mention_type == MentionType.PROPER_NOUN:
            return "ENTITY"

        return "UNKNOWN"

    def get_resolved_text(self, text: str, segments: List[DiscourseSegment]) -> str:
        """Gibt Text mit aufgelösten Pronomen zurück"""
        result = text

        # Für jedes Pronomen im Text
        for cluster in self.clusters:
            for mention in cluster.mentions:
                if mention.mention_type == MentionType.PRONOUN:
                    # Ersetze Pronomen durch [Pronomen→Referent]
                    pattern = rf'\b{re.escape(mention.text)}\b'
                    replacement = f"[{mention.text}→{cluster.canonical_mention}]"
                    result = re.sub(pattern, replacement, result, count=1)

        return result

    def get_entity_mentions(self, entity: str) -> List[CorefMention]:
        """Findet alle Mentions einer bestimmten Entität"""
        for cluster in self.clusters:
            if cluster.canonical_mention.lower() == entity.lower():
                return cluster.mentions
        return []


# =============================================================================
# TOPIC MEMORY
# =============================================================================

class TopicMemory:
    """
    Verwaltet Gesprächsthemen und deren Verlauf.
    Erkennt Themenwechsel und behält Kontext.
    """

    def __init__(self, max_topics: int = 20):
        self.topics: Dict[int, Topic] = {}
        self.active_topics: List[int] = []  # Topic IDs
        self.topic_history: List[TopicShift] = []
        self.next_topic_id = 0
        self.max_topics = max_topics

        # Stopwörter für Themenerkennung
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber", "ist", "sind",
            "war", "waren", "hat", "haben", "wird", "werden", "kann", "können",
            "muss", "müssen", "soll", "sollen", "ich", "du", "er", "sie", "es",
            "wir", "ihr", "sie", "mein", "dein", "sein", "ihr", "unser", "euer",
            "nicht", "kein", "keine", "auch", "noch", "schon", "nur", "sehr",
            "mehr", "viel", "wenig", "alle", "jeder", "dieser", "jener", "welcher"
        }

        # Themenmarker
        self.topic_intro_patterns = [
            r"(?:sprechen|reden|erzählen)\s+(?:wir\s+)?(?:über|von)\s+(.+)",
            r"(?:was|wie)\s+(?:ist|sind)\s+(?:mit\s+)?(.+)",
            r"(?:zum\s+thema|bezüglich|hinsichtlich)\s+(.+)",
            r"(?:es\s+geht\s+um)\s+(.+)",
        ]

    def process_segment(self, segment: DiscourseSegment) -> Optional[TopicShift]:
        """Verarbeitet ein Segment und aktualisiert Themen"""
        # Keywords extrahieren
        keywords = self._extract_keywords(segment)

        if not keywords:
            return None

        # Prüfe ob existierendes Thema
        matched_topic = self._find_matching_topic(keywords)

        if matched_topic:
            # Existierendes Thema aktualisieren
            self._update_topic(matched_topic, segment, keywords)
            return None
        else:
            # Neues Thema erstellen
            return self._create_new_topic(segment, keywords)

    def _extract_keywords(self, segment: DiscourseSegment) -> Set[str]:
        """Extrahiert Schlüsselwörter aus einem Segment"""
        keywords = set()

        # Entities sind immer Keywords
        keywords.update(e.lower() for e in segment.entities)

        # Tokens filtern
        for token in segment.tokens:
            if token not in self.stopwords and len(token) > 2:
                keywords.add(token)

        return keywords

    def _find_matching_topic(self, keywords: Set[str]) -> Optional[int]:
        """Findet ein passendes existierendes Thema"""
        best_match = None
        best_score = 0.0

        for topic_id, topic in self.topics.items():
            if topic.relevance == TopicRelevance.CONCLUDED:
                continue

            # Jaccard-Ähnlichkeit
            intersection = len(keywords & topic.keywords)
            union = len(keywords | topic.keywords)

            if union > 0:
                score = intersection / union
                if score > best_score and score > 0.2:
                    best_score = score
                    best_match = topic_id

        return best_match

    def _update_topic(self, topic_id: int, segment: DiscourseSegment, keywords: Set[str]) -> None:
        """Aktualisiert ein existierendes Thema"""
        topic = self.topics[topic_id]
        topic.keywords.update(keywords)
        topic.last_mentioned = segment.index
        topic.mention_count += 1
        topic.related_entities.extend(segment.entities)

        # Relevanz aktualisieren
        if topic.mention_count >= 3:
            topic.relevance = TopicRelevance.MAIN

        # An den Anfang der aktiven Themen setzen
        if topic_id in self.active_topics:
            self.active_topics.remove(topic_id)
        self.active_topics.insert(0, topic_id)

    def _create_new_topic(self, segment: DiscourseSegment, keywords: Set[str]) -> TopicShift:
        """Erstellt ein neues Thema"""
        # Themenname bestimmen
        topic_name = self._determine_topic_name(segment, keywords)

        new_topic = Topic(
            topic_id=self.next_topic_id,
            name=topic_name,
            keywords=keywords,
            first_mentioned=segment.index,
            last_mentioned=segment.index,
            mention_count=1,
            relevance=TopicRelevance.MENTIONED,
            related_entities=list(segment.entities)
        )

        self.topics[self.next_topic_id] = new_topic

        # Vorheriges Hauptthema
        previous_topic = None
        if self.active_topics:
            prev_id = self.active_topics[0]
            previous_topic = self.topics[prev_id].name

        # Shift-Typ bestimmen
        shift_type = self._determine_shift_type(previous_topic, topic_name, segment)

        shift = TopicShift(
            from_topic=previous_topic,
            to_topic=topic_name,
            segment_idx=segment.index,
            shift_type=shift_type,
            confidence=0.7
        )

        self.topic_history.append(shift)
        self.active_topics.insert(0, self.next_topic_id)
        self.next_topic_id += 1

        # Alte Themen bereinigen
        self._cleanup_old_topics()

        return shift

    def _determine_topic_name(self, segment: DiscourseSegment, keywords: Set[str]) -> str:
        """Bestimmt einen Namen für das Thema"""
        # Priorität: Entity > Längstes Keyword > Erstes Keyword
        if segment.entities:
            return segment.entities[0]

        if keywords:
            longest = max(keywords, key=len)
            return longest.capitalize()

        return "Unbekannt"

    def _determine_shift_type(self, from_topic: Optional[str], to_topic: str,
                              segment: DiscourseSegment) -> str:
        """Bestimmt den Typ des Themenwechsels"""
        if not from_topic:
            return "initial"

        # Prüfe auf Rückkehr zu früherem Thema
        for topic in self.topics.values():
            if topic.name.lower() == to_topic.lower() and topic.mention_count > 1:
                return "return"

        # Prüfe auf Diskursmarker für sanften Übergang
        soft_transitions = ["übrigens", "apropos", "dazu", "außerdem", "was...betrifft"]
        text_lower = segment.text.lower()

        for marker in soft_transitions:
            if marker in text_lower:
                return "smooth"

        # Default: abrupter Wechsel
        return "abrupt"

    def _cleanup_old_topics(self) -> None:
        """Bereinigt alte Themen wenn Limit erreicht"""
        if len(self.topics) > self.max_topics:
            # Älteste, wenig erwähnte Themen entfernen
            topics_by_relevance = sorted(
                self.topics.items(),
                key=lambda x: (x[1].mention_count, x[1].last_mentioned)
            )

            to_remove = topics_by_relevance[0][0]
            del self.topics[to_remove]
            if to_remove in self.active_topics:
                self.active_topics.remove(to_remove)

    def get_current_topic(self) -> Optional[Topic]:
        """Gibt das aktuelle Hauptthema zurück"""
        if self.active_topics:
            return self.topics.get(self.active_topics[0])
        return None

    def get_topic_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung aller Themen zurück"""
        return {
            "active_topics": [
                {
                    "name": self.topics[tid].name,
                    "relevance": self.topics[tid].relevance.name,
                    "mentions": self.topics[tid].mention_count,
                    "keywords": list(self.topics[tid].keywords)[:5]
                }
                for tid in self.active_topics
                if tid in self.topics
            ],
            "topic_shifts": len(self.topic_history),
            "total_topics": len(self.topics)
        }

    def search_topic_history(self, query: str) -> List[Topic]:
        """Sucht in der Themenhistorie"""
        query_lower = query.lower()
        results = []

        for topic in self.topics.values():
            if query_lower in topic.name.lower():
                results.append(topic)
                continue

            for keyword in topic.keywords:
                if query_lower in keyword:
                    results.append(topic)
                    break

        return results

    def get_related_topics(self, topic_id: int) -> List[Topic]:
        """Findet verwandte Themen"""
        if topic_id not in self.topics:
            return []

        base_topic = self.topics[topic_id]
        related = []

        for tid, topic in self.topics.items():
            if tid == topic_id:
                continue

            # Keyword-Überlappung
            overlap = len(base_topic.keywords & topic.keywords)
            if overlap >= 2:
                related.append(topic)

        return related


# =============================================================================
# CONTEXT UNDERSTANDING ENGINE (Unified Interface)
# =============================================================================

class ContextUnderstandingEngine:
    """
    Vereinte Engine für Kontextverständnis.
    Kombiniert Discourse Tracking, Coreference Resolution und Topic Memory.
    """

    def __init__(self, max_segments: int = 50, max_topics: int = 20):
        self.discourse_tracker = DiscourseTracker(max_segments=max_segments)
        self.coref_resolver = AdvancedCoreferenceResolver()
        self.topic_memory = TopicMemory(max_topics=max_topics)

        self.processed_count = 0
        self.last_context: Optional[ConversationContext] = None

    def process(self, text: str, speaker: str = "user") -> ConversationContext:
        """Hauptmethode: Verarbeitet Text und gibt vollständigen Kontext zurück"""
        # 1. Diskurs tracken
        new_segments = self.discourse_tracker.add_text(text, speaker)

        # 2. Koreference auflösen
        all_segments = list(self.discourse_tracker.segments)
        coref_clusters = self.coref_resolver.resolve(all_segments)

        # 3. Themen verarbeiten
        topic_shifts = []
        for segment in new_segments:
            shift = self.topic_memory.process_segment(segment)
            if shift:
                topic_shifts.append(shift)

        # Kontext erstellen
        self.last_context = ConversationContext(
            segments=all_segments,
            relations=self.discourse_tracker.relations.copy(),
            coref_clusters=coref_clusters,
            active_topics=[
                self.topic_memory.topics[tid]
                for tid in self.topic_memory.active_topics
                if tid in self.topic_memory.topics
            ],
            topic_history=self.topic_memory.topic_history.copy(),
            current_speaker=speaker,
            conversation_length=len(all_segments),
            summary=self._generate_summary()
        )

        self.processed_count += 1

        return self.last_context

    def _generate_summary(self) -> str:
        """Generiert eine Zusammenfassung des aktuellen Kontexts"""
        parts = []

        # Diskurs-Info
        parts.append(self.discourse_tracker.summarize_discourse())

        # Themen-Info
        current_topic = self.topic_memory.get_current_topic()
        if current_topic:
            parts.append(f"Aktuelles Thema: {current_topic.name}")

        # Koreference-Info
        if self.coref_resolver.clusters:
            entity_names = [c.canonical_mention for c in self.coref_resolver.clusters[:3]]
            parts.append(f"Erwähnte Entitäten: {', '.join(entity_names)}")

        return " | ".join(parts)

    def resolve_reference(self, pronoun: str) -> Optional[str]:
        """Löst ein Pronomen zu seinem Referenten auf"""
        pronoun_lower = pronoun.lower()

        for cluster in self.coref_resolver.clusters:
            for mention in cluster.mentions:
                if mention.text.lower() == pronoun_lower:
                    return cluster.canonical_mention

        return None

    def get_discourse_context(self, num_segments: int = 5) -> List[Dict[str, Any]]:
        """Gibt die letzten N Diskurssegmente mit Relationen zurück"""
        segments = list(self.discourse_tracker.segments)[-num_segments:]
        result = []

        for segment in segments:
            # Relation zu diesem Segment finden
            relation_to = None
            for rel in self.discourse_tracker.relations:
                if rel.target_idx == segment.index:
                    relation_to = {
                        "type": rel.relation_type.name,
                        "from": rel.source_idx,
                        "confidence": rel.confidence
                    }
                    break

            result.append({
                "index": segment.index,
                "text": segment.text,
                "speaker": segment.speaker,
                "relation": relation_to,
                "entities": segment.entities
            })

        return result

    def get_topic_context(self) -> Dict[str, Any]:
        """Gibt den Themenkontext zurück"""
        return self.topic_memory.get_topic_summary()

    def get_entity_history(self, entity: str) -> List[Dict[str, Any]]:
        """Gibt die Historie einer Entität zurück"""
        history = []

        # Aus Koreference-Clustern
        mentions = self.coref_resolver.get_entity_mentions(entity)
        for mention in mentions:
            segment = None
            for s in self.discourse_tracker.segments:
                if s.index == mention.sentence_idx:
                    segment = s
                    break

            if segment:
                history.append({
                    "mention": mention.text,
                    "type": mention.mention_type.name,
                    "segment_text": segment.text,
                    "segment_idx": segment.index
                })

        return history

    def reset(self) -> None:
        """Setzt den Kontext zurück"""
        self.discourse_tracker = DiscourseTracker(
            max_segments=self.discourse_tracker.max_segments
        )
        self.coref_resolver = AdvancedCoreferenceResolver()
        self.topic_memory = TopicMemory(max_topics=self.topic_memory.max_topics)
        self.processed_count = 0
        self.last_context = None


# =============================================================================
# SINGLETON INSTANCES & GETTERS
# =============================================================================

_context_engine: Optional[ContextUnderstandingEngine] = None
_discourse_tracker: Optional[DiscourseTracker] = None
_topic_memory: Optional[TopicMemory] = None


def get_context_understanding_engine() -> ContextUnderstandingEngine:
    """Gibt die Singleton-Instanz der ContextUnderstandingEngine zurück"""
    global _context_engine
    if _context_engine is None:
        _context_engine = ContextUnderstandingEngine()
        logger.info("ContextUnderstandingEngine initialisiert")
    return _context_engine


def get_discourse_tracker() -> DiscourseTracker:
    """Gibt die Singleton-Instanz des DiscourseTrackers zurück"""
    global _discourse_tracker
    if _discourse_tracker is None:
        _discourse_tracker = DiscourseTracker()
        logger.info("DiscourseTracker initialisiert")
    return _discourse_tracker


def get_topic_memory() -> TopicMemory:
    """Gibt die Singleton-Instanz der TopicMemory zurück"""
    global _topic_memory
    if _topic_memory is None:
        _topic_memory = TopicMemory()
        logger.info("TopicMemory initialisiert")
    return _topic_memory


# =============================================================================
# DEMO & TEST
# =============================================================================

if __name__ == "__main__":
    # Logging konfigurieren
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO NLP Context Understanding - Demo")
    print("=" * 60)

    # Engine initialisieren
    engine = get_context_understanding_engine()

    # Beispiel-Konversation
    texts = [
        "Maria arbeitet bei der Firma Schmidt. Sie ist Ingenieurin.",
        "Ihr Chef heißt Thomas. Er leitet das Entwicklungsteam.",
        "Weil das Projekt wichtig ist, arbeiten sie oft am Wochenende.",
        "Trotzdem sind alle motiviert. Das Team hat viel erreicht.",
        "Übrigens, das Wetter ist heute schön.",
        "Aber zurück zum Projekt: Der Abgabetermin naht."
    ]

    print("\n--- Verarbeite Konversation ---\n")

    for text in texts:
        print(f"INPUT: {text}")
        context = engine.process(text)
        print(f"  Segmente: {context.conversation_length}")
        print(f"  Aktive Themen: {[t.name for t in context.active_topics[:3]]}")
        print()

    print("\n--- Diskursstruktur ---")
    discourse = engine.discourse_tracker.get_discourse_structure()
    for rel in discourse["relations"][-3:]:
        print(f"  {rel['from']} → {rel['to']}: {rel['type']} ({rel['confidence']:.2f})")

    print("\n--- Koreference-Cluster ---")
    for cluster in engine.coref_resolver.clusters[:3]:
        mentions = [m.text for m in cluster.mentions]
        print(f"  [{cluster.canonical_mention}]: {mentions}")

    print("\n--- Referenz-Auflösung ---")
    pronouns = ["sie", "er", "ihr"]
    for p in pronouns:
        resolved = engine.resolve_reference(p)
        print(f"  '{p}' → {resolved or '?'}")

    print("\n--- Kontext-Zusammenfassung ---")
    print(f"  {context.summary}")

    print("\n" + "=" * 60)
    print("Demo abgeschlossen!")
