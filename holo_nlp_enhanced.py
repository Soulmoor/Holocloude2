#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloNLP Enhanced v1.0 - Fortgeschrittene NLP ohne LLM

VERBESSERUNGEN:
1. Word Embeddings (FastText-kompatibel, eigene leichte Variante)
2. Bessere NER mit Gazetteers (umfangreiche Namenslisten)
3. Koreference-Resolution (wer ist "er"/"sie"?)
4. Dependency Parsing (Satzstruktur-Analyse)
5. Argumentations-Erkennung
6. Ironie/Sarkasmus-Erkennung
7. Plagiatserkennung (Similarity)
8. Autor-Stil-Fingerprint

Optimiert fuer Raspberry Pi - Keine schweren ML-Bibliotheken!

Author: Kira & Claude
Version: 1.0
"""

import re
import math
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("HoloNLPEnhanced")

# =============================================================================
# PUBLIC API - Exported symbols
# =============================================================================

__all__ = [
    # Main Class
    "HoloNLPEnhanced",

    # NER
    "EnhancedNER",
    "Entity",

    # Coreference Resolution
    "CoreferenceResolver",
    "CoreferenceCluster",

    # Dependency Parsing
    "SimpleDependencyParser",
    "DependencyNode",

    # Argument Mining
    "ArgumentDetector",
    "Argument",

    # Irony Detection
    "IronyDetector",
    "IronyResult",

    # Plagiarism Detection
    "PlagiarismDetector",
    "PlagiarismMatch",

    # Author Style Analysis
    "AuthorStyleAnalyzer",
    "AuthorFingerprint",

    # Embeddings
    "LightweightEmbeddings",
]

# Safe access helpers für Strict Mode
try:
    from holo_error_tracker import safe_list_access, safe_split_access, report_error
except ImportError:
    def safe_list_access(lst, index, module, function, default=None, context=""):
        if not lst or len(lst) <= abs(index):
            return default
        return lst[index]
    def safe_split_access(text, sep, index, module, function, default="", context=""):
        parts = text.split(sep) if text else []
        if len(parts) <= abs(index):
            return default
        return parts[index]
    def report_error(e, module="", function="", context="", severity=None, fallback_value=None):
        return fallback_value


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Entity:
    """Eine erkannte Entitaet"""
    text: str
    label: str  # PERSON, ORG, LOC, DATE, MONEY, PRODUCT, EVENT
    start: int
    end: int
    confidence: float
    source: str = "gazetteer"  # gazetteer, pattern, context


@dataclass
class CoreferenceCluster:
    """Ein Koreference-Cluster (z.B. 'Maria' -> 'sie' -> 'die Forscherin')"""
    main_mention: str
    mentions: List[Tuple[str, int]]  # (text, position)
    entity_type: str  # PERSON, ORG, etc.


@dataclass
class DependencyNode:
    """Ein Knoten im Dependency-Baum"""
    word: str
    pos: str  # Part-of-Speech
    dep_rel: str  # Dependency Relation
    head_idx: int  # Index des Kopfes
    children: List[int] = field(default_factory=list)


@dataclass
class Argument:
    """Ein erkanntes Argument"""
    arg_type: str  # claim, premise, conclusion, evidence
    text: str
    confidence: float
    indicators: List[str]


@dataclass
class IronyResult:
    """Ergebnis der Ironie-Erkennung"""
    is_ironic: bool
    confidence: float
    indicators: List[str]
    irony_type: str  # situational, verbal, sarcasm


@dataclass
class PlagiarismMatch:
    """Ein Plagiat-Treffer"""
    source_text: str
    match_text: str
    similarity: float
    match_type: str  # exact, paraphrase, structural


@dataclass
class AuthorFingerprint:
    """Autor-Stil-Fingerprint"""
    avg_word_length: float
    avg_sentence_length: float
    vocabulary_richness: float
    punctuation_ratio: Dict[str, float]
    function_word_freq: Dict[str, float]
    sentence_starters: Dict[str, float]
    hapax_legomena_ratio: float  # Woerter die nur 1x vorkommen
    fingerprint_vector: List[float]


# =============================================================================
# 1. WORD EMBEDDINGS (Leichtgewichtig)
# =============================================================================

class LightweightEmbeddings:
    """
    Leichtgewichtige Word Embeddings ohne externe Bibliotheken.

    Verwendet:
    - Co-occurrence Matrix
    - PMI (Pointwise Mutual Information)
    - SVD-Approximation fuer Dimensionsreduktion

    Kann optional vortrainierte Vektoren laden.
    """

    def __init__(self, dim: int = 50, window: int = 5):
        self.dim = dim
        self.window = window
        self.word2idx: Dict[str, int] = {}
        self.idx2word: Dict[int, str] = {}
        self.vectors: Dict[str, List[float]] = {}
        self.word_counts: Counter = Counter()
        self.cooccurrence: Dict[Tuple[int, int], float] = {}

        # Lade vortrainierte deutsche Embeddings wenn vorhanden
        self._load_pretrained()

    def _load_pretrained(self):
        """Laedt vortrainierte Embeddings wenn vorhanden"""
        pretrained_path = Path("data/embeddings/german_embeddings.json")
        if pretrained_path.exists():
            try:
                with open(pretrained_path) as f:
                    data = json.load(f)
                    self.vectors = data.get("vectors", {})
                    logger.info(f"Loaded {len(self.vectors)} pretrained embeddings")
            except Exception as e:
                logger.warning(f"Could not load pretrained embeddings: {e}")

    def train_on_corpus(self, texts: List[str]):
        """Trainiert Embeddings auf einem Korpus"""
        # Tokenize und zaehle
        for text in texts:
            words = self._tokenize(text)
            self.word_counts.update(words)

            # Co-occurrence
            for i, word in enumerate(words):
                if word not in self.word2idx:
                    idx = len(self.word2idx)
                    self.word2idx[word] = idx
                    self.idx2word[idx] = word

                # Fenster
                start = max(0, i - self.window)
                end = min(len(words), i + self.window + 1)

                for j in range(start, end):
                    if i != j:
                        pair = (self.word2idx[word], self.word2idx.get(words[j], -1))
                        if pair[1] >= 0:
                            self.cooccurrence[pair] = self.cooccurrence.get(pair, 0) + 1

        # PMI berechnen und zu Vektoren umwandeln
        self._compute_pmi_vectors()

    def _compute_pmi_vectors(self):
        """Berechnet PMI-basierte Vektoren"""
        total = sum(self.word_counts.values())

        for word, idx in self.word2idx.items():
            if self.word_counts[word] < 5:  # Min frequency
                continue

            vector = [0.0] * self.dim
            p_word = self.word_counts[word] / total

            # Top co-occurrences als Features
            word_cooc = [(self.cooccurrence.get((idx, j), 0), j)
                        for j in range(min(self.dim, len(self.word2idx)))]
            word_cooc.sort(reverse=True)

            for i, (count, j) in enumerate(word_cooc[:self.dim]):
                if count > 0 and j in self.idx2word:
                    context_word = self.idx2word[j]
                    p_context = self.word_counts[context_word] / total
                    p_joint = count / total

                    # PMI
                    if p_word > 0 and p_context > 0:
                        pmi = math.log2(p_joint / (p_word * p_context) + 1e-10)
                        vector[i] = max(0, pmi)  # Positive PMI

            # Normalisieren
            norm = math.sqrt(sum(v*v for v in vector)) + 1e-10
            self.vectors[word] = [v / norm for v in vector]

    def get_vector(self, word: str) -> Optional[List[float]]:
        """Gibt den Vektor fuer ein Wort zurueck"""
        word_lower = word.lower()
        if word_lower in self.vectors:
            return self.vectors[word_lower]
        return None

    def similarity(self, word1: str, word2: str) -> float:
        """Berechnet Cosine Similarity zwischen zwei Woertern"""
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)

        if v1 is None or v2 is None:
            return 0.0

        dot = sum(a * b for a, b in zip(v1, v2))
        return dot  # Bereits normalisiert

    def most_similar(self, word: str, n: int = 10) -> List[Tuple[str, float]]:
        """Findet die aehnlichsten Woerter"""
        v = self.get_vector(word)
        if v is None:
            return []

        similarities = []
        for other_word, other_vec in self.vectors.items():
            if other_word != word.lower():
                sim = sum(a * b for a, b in zip(v, other_vec))
                similarities.append((other_word, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenisiert Text"""
        return re.findall(r'\b[a-zäöüß]+\b', text.lower())


# =============================================================================
# 2. NAMED ENTITY RECOGNITION MIT GAZETTEERS
# =============================================================================

class EnhancedNER:
    """
    Verbesserte Named Entity Recognition mit:
    - Umfangreichen Gazetteers (Namenslisten)
    - Kontext-basierter Erkennung
    - Pattern Matching
    - Confidence Scoring
    """

    def __init__(self):
        self._init_gazetteers()
        self._init_patterns()
        self._init_context_clues()

    def _init_gazetteers(self):
        """Initialisiert umfangreiche Namenslisten"""

        # Deutsche Vornamen (erweitert)
        self.first_names_male = {
            "alexander", "andreas", "benjamin", "christian", "daniel", "david",
            "dennis", "dominik", "erik", "fabian", "felix", "florian", "frank",
            "hans", "jan", "jonas", "julian", "kevin", "lars", "leon", "lukas",
            "marcel", "marco", "mario", "markus", "martin", "matthias", "max",
            "michael", "moritz", "nico", "niklas", "oliver", "pascal", "patrick",
            "paul", "peter", "philipp", "rafael", "robin", "sebastian", "simon",
            "stefan", "steffen", "thomas", "tim", "tobias", "tom", "wolfgang",
            # Internationale
            "james", "john", "william", "richard", "robert", "charles", "joseph",
            "edward", "george", "henry", "albert", "arthur", "alfred", "ernest",
            "vladimir", "sergei", "dimitri", "ivan", "boris", "alexei",
            "mohammed", "ahmed", "ali", "omar", "hassan", "hussein",
            "pierre", "jean", "jacques", "françois", "louis", "marc",
        }

        self.first_names_female = {
            "alexandra", "andrea", "angelika", "anna", "barbara", "birgit",
            "brigitte", "carolin", "charlotte", "christina", "claudia", "daniela",
            "diana", "elena", "elisabeth", "emma", "eva", "franziska", "gabriele",
            "hannah", "heike", "helena", "ines", "jana", "jennifer", "jessica",
            "julia", "juliane", "karen", "karin", "katharina", "katja", "kerstin",
            "laura", "lea", "lena", "lisa", "luisa", "manuela", "maria", "marie",
            "marina", "martina", "melanie", "michelle", "mia", "michaela", "monika",
            "nadine", "natalie", "nicole", "nina", "petra", "sabine", "sandra",
            "sara", "sarah", "silke", "simone", "sophia", "stefanie", "susanne",
            "tanja", "ulrike", "ursula", "vanessa", "verena", "yvonne",
            # Internationale
            "mary", "elizabeth", "margaret", "victoria", "catherine", "anne",
            "emily", "emma", "olivia", "sophia", "isabella", "charlotte",
            "natasha", "olga", "anna", "maria", "elena", "tatiana",
        }

        self.all_first_names = self.first_names_male | self.first_names_female

        # Deutsche Nachnamen
        self.last_names = {
            "mueller", "schmidt", "schneider", "fischer", "weber", "meyer",
            "wagner", "becker", "schulz", "hoffmann", "schaefer", "koch",
            "bauer", "richter", "klein", "wolf", "schroeder", "neumann",
            "schwarz", "zimmermann", "braun", "krueger", "hofmann", "hartmann",
            "lange", "schmitt", "werner", "schmitz", "krause", "meier",
            "lehmann", "schmid", "schulze", "maier", "koehler", "herrmann",
            "koenig", "walter", "mayer", "huber", "kaiser", "fuchs",
            "peters", "lang", "scholz", "moeller", "weiss", "jung",
            "hahn", "schubert", "vogel", "friedrich", "keller", "guenther",
            "frank", "berger", "winkler", "roth", "beck", "lorenz",
            "baumann", "franke", "albrecht", "schuster", "simon", "ludwig",
            "boehm", "winter", "kraus", "martin", "schumacher", "kraemer",
            "vogt", "stein", "jaeger", "otto", "sommer", "gross",
            "seidel", "heinrich", "brandt", "haas", "schreiber", "graf",
            "schulte", "dietrich", "ziegler", "kuhn", "kuehn", "pohl",
        }

        # Staedte und Laender
        self.cities = {
            # Deutschland
            "berlin", "hamburg", "muenchen", "koeln", "frankfurt", "stuttgart",
            "duesseldorf", "dortmund", "essen", "leipzig", "bremen", "dresden",
            "hannover", "nuernberg", "duisburg", "bochum", "wuppertal", "bielefeld",
            "bonn", "muenster", "karlsruhe", "mannheim", "augsburg", "wiesbaden",
            "gelsenkirchen", "moenchengladbach", "braunschweig", "chemnitz", "kiel",
            "aachen", "halle", "magdeburg", "freiburg", "krefeld", "luebeck",
            "oberhausen", "erfurt", "mainz", "rostock", "kassel", "hagen",
            "hamm", "saarbruecken", "muelheim", "potsdam", "ludwigshafen",
            "oldenburg", "leverkusen", "osnabrueck", "solingen", "heidelberg",
            # Oesterreich
            "wien", "graz", "linz", "salzburg", "innsbruck",
            # Schweiz
            "zuerich", "genf", "basel", "bern", "lausanne",
            # International
            "london", "paris", "rom", "madrid", "barcelona", "amsterdam",
            "bruessel", "prag", "warschau", "budapest", "moskau", "peking",
            "tokio", "new york", "los angeles", "chicago", "washington",
            "san francisco", "seattle", "boston", "miami", "toronto",
            "sydney", "melbourne", "singapur", "hongkong", "shanghai",
        }

        self.countries = {
            "deutschland", "oesterreich", "schweiz", "frankreich", "italien",
            "spanien", "portugal", "niederlande", "belgien", "luxemburg",
            "grossbritannien", "england", "schottland", "irland", "polen",
            "tschechien", "slowakei", "ungarn", "rumaenien", "bulgarien",
            "griechenland", "tuerkei", "russland", "ukraine", "schweden",
            "norwegen", "finnland", "daenemark", "usa", "kanada", "mexiko",
            "brasilien", "argentinien", "china", "japan", "indien", "australien",
            "aegypten", "suedafrika", "israel", "saudi-arabien", "iran",
        }

        self.locations = self.cities | self.countries

        # Organisationen
        self.organizations = {
            # Tech
            "google", "apple", "microsoft", "amazon", "meta", "facebook",
            "twitter", "netflix", "nvidia", "intel", "amd", "samsung",
            "sony", "nintendo", "tesla", "spacex", "openai", "anthropic",
            "ibm", "oracle", "sap", "siemens", "bosch", "volkswagen",
            "bmw", "mercedes", "audi", "porsche", "daimler",
            # Medien
            "spiegel", "bild", "zeit", "faz", "sueddeutsche", "welt",
            "stern", "focus", "tagesschau", "zdf", "ard", "rtl", "pro7",
            "bbc", "cnn", "reuters", "bloomberg", "nytimes",
            # Politik/Org
            "bundestag", "bundesrat", "bundesregierung", "eu", "europaeische union",
            "nato", "uno", "un", "unesco", "who", "iwf", "weltbank",
            "cdu", "spd", "gruene", "fdp", "afd", "linke", "csu",
            # Universitaeten
            "tu", "rwth", "lmu", "fu", "hu", "kit", "eth", "mit",
            "harvard", "stanford", "oxford", "cambridge", "yale", "princeton",
        }

        # Produkte
        self.products = {
            "iphone", "ipad", "macbook", "imac", "airpods", "apple watch",
            "galaxy", "pixel", "surface", "xbox", "playstation", "switch",
            "windows", "macos", "linux", "android", "ios",
            "chatgpt", "gpt-4", "gpt-5", "claude", "gemini", "copilot",
            "alexa", "siri", "cortana", "bixby",
            "chrome", "firefox", "safari", "edge", "opera",
            "word", "excel", "powerpoint", "outlook", "teams",
        }

        # Titel und Anreden
        self.titles = {
            "dr", "dr.", "prof", "prof.", "ing", "ing.", "dipl", "dipl.",
            "mag", "mag.", "herr", "frau", "mr", "mr.", "mrs", "mrs.",
            "ms", "ms.", "sir", "lord", "lady", "graf", "baron",
            "praesident", "kanzler", "minister", "buergermeister", "ceo",
            "cto", "cfo", "coo", "direktor", "manager", "chef",
        }

    def _init_patterns(self):
        """Initialisiert Erkennungs-Patterns"""

        self.patterns = {
            "MONEY": [
                r'(\d+(?:[.,]\d+)?)\s*(euro|eur|€|dollar|usd|\$|pfund|gbp|£|chf|yen|¥)',
                r'(\d+(?:[.,]\d+)?)\s*(millionen?|milliarden?|mio\.?|mrd\.?)\s*(euro|dollar|€|\$)?',
            ],
            "PERCENT": [
                r'(\d+(?:[.,]\d+)?)\s*(%|prozent|prozentpunkte)',
            ],
            "DATE": [
                r'(\d{1,2})\.?\s*(januar|februar|maerz|april|mai|juni|juli|august|september|oktober|november|dezember)\s*(\d{4})?',
                r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})',
                r'(januar|februar|maerz|april|mai|juni|juli|august|september|oktober|november|dezember)\s+(\d{4})',
                r'(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)',
                r'(gestern|heute|morgen|vorgestern|uebermorgen)',
                r'(letzte|naechste|diese)\s+(woche|monat|jahr)',
            ],
            "TIME": [
                r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(uhr)?',
                r'(\d{1,2})\s*uhr\s*(\d{2})?',
            ],
            "EMAIL": [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            "URL": [
                r'https?://[^\s<>"{}|\\^`\[\]]+',
                r'www\.[^\s<>"{}|\\^`\[\]]+',
            ],
            "PHONE": [
                r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            ],
        }

        # Kompiliere Patterns
        self.compiled_patterns = {}
        for label, patterns in self.patterns.items():
            self.compiled_patterns[label] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def _init_context_clues(self):
        """Initialisiert Kontext-Hinweise fuer Entity-Erkennung"""

        self.person_context = {
            "sagte", "erklaerte", "meinte", "betonte", "berichtete",
            "laut", "nach", "so", "laut aussage von",
            "geschaeftsfuehrer", "vorstand", "praesident", "kanzler",
            "minister", "direktor", "chef", "leiter", "sprecher",
            "autor", "kuenstler", "wissenschaftler", "forscher",
            "geboren", "gestorben", "heiratete", "gruendete",
        }

        self.org_context = {
            "unternehmen", "firma", "konzern", "gruppe", "holding",
            "gmbh", "ag", "kg", "se", "inc", "corp", "ltd",
            "verein", "verband", "organisation", "institut", "stiftung",
            "partei", "fraktion", "regierung", "ministerium", "behoerde",
            "universitaet", "hochschule", "akademie", "schule",
            "krankenhaus", "klinik", "praxis",
            "mitarbeiter", "beschaeftigte", "angestellte",
        }

        self.location_context = {
            "in", "aus", "nach", "bei", "nahe", "unweit",
            "stadt", "gemeinde", "kreis", "land", "staat", "region",
            "hauptstadt", "metropole", "provinz", "bundesland",
            "strasse", "platz", "allee", "weg", "gasse",
            "geboren in", "lebt in", "wohnt in", "stammt aus",
        }

    def extract_entities(self, text: str) -> List[Entity]:
        """Extrahiert alle Entitaeten aus dem Text"""
        entities = []
        text_lower = text.lower()

        # 1. Pattern-basierte Extraktion (DATE, MONEY, etc.)
        entities.extend(self._extract_by_patterns(text))

        # 2. Gazetteer-basierte Extraktion (PERSON, ORG, LOC)
        entities.extend(self._extract_by_gazetteers(text))

        # 3. Kontext-basierte Extraktion
        entities.extend(self._extract_by_context(text))

        # 4. Deduplizieren und sortieren
        entities = self._deduplicate_entities(entities)

        return entities

    def _extract_by_patterns(self, text: str) -> List[Entity]:
        """Extrahiert Entities mittels Regex-Patterns"""
        entities = []

        for label, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entities.append(Entity(
                        text=match.group(0),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,
                        source="pattern"
                    ))

        return entities

    def _extract_by_gazetteers(self, text: str) -> List[Entity]:
        """Extrahiert Entities mittels Gazetteers"""
        entities = []
        words = text.split()

        i = 0
        while i < len(words):
            word = words[i]
            word_lower = word.lower().strip('.,!?;:()[]"\'')
            word_clean = re.sub(r'[^\w]', '', word_lower)

            # Check fuer Titel + Name Kombination
            if word_lower in self.titles and i + 1 < len(words):
                next_word = words[i + 1].strip('.,!?;:()[]"\'')
                next_lower = next_word.lower()

                if next_lower in self.all_first_names or next_lower in self.last_names:
                    # Sammle den vollstaendigen Namen
                    name_parts = [word, next_word]
                    j = i + 2

                    while j < len(words):
                        candidate = words[j].strip('.,!?;:()[]"\'').lower()
                        if candidate in self.last_names:
                            name_parts.append(words[j].strip('.,!?;:()[]"\''))
                            j += 1
                        else:
                            break

                    full_name = " ".join(name_parts)
                    start = text.find(full_name)
                    if start == -1:
                        start = text.lower().find(full_name.lower())

                    entities.append(Entity(
                        text=full_name,
                        label="PERSON",
                        start=start,
                        end=start + len(full_name),
                        confidence=0.95,
                        source="gazetteer"
                    ))
                    i = j
                    continue

            # Check fuer Namen (Vorname + Nachname)
            if word_clean in self.all_first_names:
                if i + 1 < len(words):
                    next_word = words[i + 1].strip('.,!?;:()[]"\'')
                    next_lower = next_word.lower()

                    if next_lower in self.last_names or (len(next_word) > 1 and next_word[0].isupper()):
                        word_stripped = word.strip('.,!?;:()[]"\'')
                        full_name = f"{word_stripped} {next_word}"
                        start = text.find(full_name)
                        if start == -1:
                            start = text.lower().find(full_name.lower())

                        entities.append(Entity(
                            text=full_name,
                            label="PERSON",
                            start=max(0, start),
                            end=max(0, start) + len(full_name),
                            confidence=0.85,
                            source="gazetteer"
                        ))
                        i += 2
                        continue

            # Check fuer Orte
            if word_clean in self.locations:
                start = text.lower().find(word_lower)
                entities.append(Entity(
                    text=word.strip('.,!?;:()[]"\''),
                    label="LOC",
                    start=start,
                    end=start + len(word_clean),
                    confidence=0.85,
                    source="gazetteer"
                ))

            # Check fuer Organisationen
            elif word_clean in self.organizations:
                start = text.lower().find(word_lower)
                entities.append(Entity(
                    text=word.strip('.,!?;:()[]"\''),
                    label="ORG",
                    start=start,
                    end=start + len(word_clean),
                    confidence=0.85,
                    source="gazetteer"
                ))

            # Check fuer Produkte
            elif word_clean in self.products:
                start = text.lower().find(word_lower)
                entities.append(Entity(
                    text=word.strip('.,!?;:()[]"\''),
                    label="PRODUCT",
                    start=start,
                    end=start + len(word_clean),
                    confidence=0.85,
                    source="gazetteer"
                ))

            i += 1

        return entities

    def _extract_by_context(self, text: str) -> List[Entity]:
        """Extrahiert Entities basierend auf Kontext"""
        entities = []
        sentences = re.split(r'[.!?]+', text)

        for sent in sentences:
            sent_lower = sent.lower()
            words = sent.split()

            # Person-Kontext (z.B. "... sagte Max Mueller")
            for i, word in enumerate(words):
                word_lower = word.lower().strip('.,!?;:()[]"\'')

                if word_lower in self.person_context:
                    # Schaue nach Grossgeschriebenem danach
                    for j in range(i + 1, min(i + 4, len(words))):
                        candidate = words[j].strip('.,!?;:()[]"\'')
                        if len(candidate) > 1 and candidate[0].isupper():
                            # Sammle alle folgenden Grossgeschriebenen
                            name_parts = [candidate]
                            k = j + 1
                            while k < min(j + 3, len(words)):
                                next_part = words[k].strip('.,!?;:()[]"\'')
                                if len(next_part) > 1 and next_part[0].isupper():
                                    name_parts.append(next_part)
                                    k += 1
                                else:
                                    break

                            full_name = " ".join(name_parts)
                            if len(full_name) > 2:
                                entities.append(Entity(
                                    text=full_name,
                                    label="PERSON",
                                    start=sent.find(full_name),
                                    end=sent.find(full_name) + len(full_name),
                                    confidence=0.75,
                                    source="context"
                                ))
                            break

        return entities

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Entfernt Duplikate und ueberlappende Entities"""
        if not entities:
            return []

        # Sortiere nach Position und Laenge
        entities.sort(key=lambda e: (e.start, -len(e.text)))

        result = []
        last_end = -1

        for entity in entities:
            if entity.start >= last_end:
                result.append(entity)
                last_end = entity.end
            elif entity.confidence > 0.9:  # Hochkonfidente ueberschreiben
                if result and result[-1].start == entity.start:
                    if entity.confidence > result[-1].confidence:
                        result[-1] = entity

        return result


# =============================================================================
# 3. KOREFERENCE-RESOLUTION
# =============================================================================

class CoreferenceResolver:
    """
    Loest Koreferenzen auf (z.B. "Maria" -> "sie" -> "die Forscherin")

    Verwendet:
    - Pronomen-Matching
    - Gender-Agreement
    - Number-Agreement
    - Recency-basiertes Linking
    """

    def __init__(self):
        self.pronouns_male = {"er", "ihm", "ihn", "sein", "seiner", "seinen", "seinem"}
        self.pronouns_female = {"sie", "ihr", "ihre", "ihrer", "ihren", "ihrem"}
        self.pronouns_neutral = {"es", "sein", "seiner", "seinem", "seinen"}
        self.pronouns_plural = {"sie", "ihnen", "ihre", "ihrer", "ihren", "ihrem"}

        self.definite_np_patterns = [
            r'der\s+(\w+)',
            r'die\s+(\w+)',
            r'das\s+(\w+)',
        ]

        # Berufsbezeichnungen mit Gender
        self.role_nouns_male = {
            "forscher", "wissenschaftler", "professor", "doktor", "arzt",
            "ingenieur", "manager", "direktor", "chef", "leiter", "sprecher",
            "autor", "kuenstler", "politiker", "praesident", "kanzler",
            "minister", "buergermeister", "richter", "anwalt", "unternehmer",
        }

        self.role_nouns_female = {
            "forscherin", "wissenschaftlerin", "professorin", "doktorin", "aerztin",
            "ingenieurin", "managerin", "direktorin", "chefin", "leiterin", "sprecherin",
            "autorin", "kuenstlerin", "politikerin", "praesidentin", "kanzlerin",
            "ministerin", "buergermeisterin", "richterin", "anwaeltin", "unternehmerin",
        }

    def resolve(self, text: str, entities: List[Entity]) -> List[CoreferenceCluster]:
        """Loest Koreferenzen im Text auf"""
        clusters = []
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Filtere PERSON-Entities
        person_entities = [e for e in entities if e.label == "PERSON"]

        for person in person_entities:
            cluster = CoreferenceCluster(
                main_mention=person.text,
                mentions=[(person.text, person.start)],
                entity_type="PERSON"
            )

            # Bestimme Gender
            first_name = safe_list_access(person.text.split(), 0, "nlp_enhanced", "resolve", default="").lower() if person.text else ""
            is_male = self._is_likely_male(first_name)
            is_female = self._is_likely_female(first_name)

            # Suche nach Koreferenzen in folgenden Saetzen
            person_pos = person.start

            for sent in sentences:
                sent_start = text.find(sent)
                if sent_start <= person_pos:
                    continue

                # Pronomen
                pronouns_to_check = set()
                if is_male:
                    pronouns_to_check = self.pronouns_male
                elif is_female:
                    pronouns_to_check = self.pronouns_female
                else:
                    pronouns_to_check = self.pronouns_male | self.pronouns_female

                words = sent.lower().split()
                for i, word in enumerate(words):
                    word_clean = re.sub(r'[^\w]', '', word)
                    if word_clean in pronouns_to_check:
                        # Position im Originaltext finden
                        word_pos = text.lower().find(word, sent_start)
                        if word_pos > person_pos:
                            cluster.mentions.append((word_clean, word_pos))

                # Definite NPs (z.B. "die Forscherin")
                role_nouns = self.role_nouns_female if is_female else self.role_nouns_male
                for role in role_nouns:
                    if role in sent.lower():
                        role_pos = text.lower().find(role, sent_start)
                        if role_pos > person_pos:
                            # Finde den vollen Ausdruck
                            for pattern in self.definite_np_patterns:
                                match = re.search(pattern + r'\s*' + role, sent, re.IGNORECASE)
                                if match:
                                    cluster.mentions.append((match.group(0), sent_start + match.start()))
                                    break

            if len(cluster.mentions) > 1:
                clusters.append(cluster)

        return clusters

    def _is_likely_male(self, name: str) -> bool:
        """Prueft ob ein Name wahrscheinlich maennlich ist"""
        name_lower = name.lower()
        # Einfache Heuristik + bekannte Namen
        male_endings = ("o", "us", "er", "an", "en", "el", "as", "is")

        # Check gegen bekannte maennliche Namen
        if hasattr(self, '_ner') and name_lower in self._ner.first_names_male:
            return True

        return name_lower.endswith(male_endings)

    def _is_likely_female(self, name: str) -> bool:
        """Prueft ob ein Name wahrscheinlich weiblich ist"""
        name_lower = name.lower()
        female_endings = ("a", "e", "ie", "in", "ine", "ette", "elle")

        # Check gegen bekannte weibliche Namen
        if hasattr(self, '_ner') and name_lower in self._ner.first_names_female:
            return True

        return name_lower.endswith(female_endings)

    def get_resolved_text(self, text: str, clusters: List[CoreferenceCluster]) -> str:
        """Gibt Text mit aufgeloesten Koreferenzen zurueck"""
        result = text

        for cluster in clusters:
            main = cluster.main_mention
            for mention, pos in cluster.mentions[1:]:  # Skip main mention
                # Ersetze Pronomen mit [Name]
                if mention.lower() in (self.pronouns_male | self.pronouns_female | self.pronouns_neutral):
                    result = result[:pos] + f"[{main}]" + result[pos + len(mention):]

        return result


# =============================================================================
# 4. DEPENDENCY PARSING (Vereinfacht)
# =============================================================================

class SimpleDependencyParser:
    """
    Vereinfachter Dependency Parser ohne ML.

    Erkennt:
    - Subjekt-Verb-Objekt Strukturen
    - Modifikatoren
    - Praepositionalphrasen
    """

    def __init__(self):
        self._init_pos_patterns()

    def _init_pos_patterns(self):
        """Initialisiert POS-Tagging Patterns"""

        self.verbs = {
            "ist", "sind", "war", "waren", "wird", "werden", "wurde", "wurden",
            "hat", "haben", "hatte", "hatten", "kann", "koennen", "konnte",
            "muss", "muessen", "musste", "soll", "sollen", "sollte",
            "macht", "machen", "machte", "geht", "gehen", "ging",
            "kommt", "kommen", "kam", "gibt", "geben", "gab",
            "sagt", "sagen", "sagte", "erklaert", "erklaeren", "erklaerte",
            "zeigt", "zeigen", "zeigte", "findet", "finden", "fand",
            "bringt", "bringen", "brachte", "nimmt", "nehmen", "nahm",
            "sieht", "sehen", "sah", "hoert", "hoeren", "hoerte",
            "schreibt", "schreiben", "schrieb", "liest", "lesen", "las",
            "arbeitet", "arbeiten", "arbeitete", "spielt", "spielen", "spielte",
            "entwickelt", "entwickeln", "entwickelte",
        }

        self.auxiliaries = {
            "ist", "sind", "war", "waren", "wird", "werden", "wurde", "wurden",
            "hat", "haben", "hatte", "hatten", "sein", "haben", "werden",
        }

        self.prepositions = {
            "in", "an", "auf", "aus", "bei", "mit", "nach", "seit", "von",
            "zu", "fuer", "durch", "gegen", "ohne", "um", "unter", "ueber",
            "vor", "hinter", "neben", "zwischen", "waehrend", "wegen", "trotz",
        }

        self.determiners = {
            "der", "die", "das", "den", "dem", "des",
            "ein", "eine", "einer", "eines", "einem", "einen",
            "kein", "keine", "keiner", "keines", "keinem", "keinen",
            "mein", "dein", "sein", "ihr", "unser", "euer",
            "dieser", "diese", "dieses", "jener", "jene", "jenes",
        }

        self.adjective_endings = ("e", "en", "er", "es", "em", "ig", "lich", "isch", "bar", "sam")

        self.conjunctions = {
            "und", "oder", "aber", "denn", "weil", "dass", "wenn", "ob",
            "als", "wie", "da", "obwohl", "waehrend", "bevor", "nachdem",
        }

    def parse(self, sentence: str) -> List[DependencyNode]:
        """Parst einen Satz und gibt Dependency-Struktur zurueck"""
        words = sentence.split()
        nodes = []

        # Einfaches POS-Tagging
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:()[]"\'')

            pos = self._get_pos(word_lower)

            nodes.append(DependencyNode(
                word=word,
                pos=pos,
                dep_rel="",
                head_idx=-1,
                children=[]
            ))

        # Dependency Relations
        self._assign_dependencies(nodes)

        return nodes

    def _get_pos(self, word: str) -> str:
        """Bestimmt Part-of-Speech fuer ein Wort"""
        word_lower = word.lower()

        if word_lower in self.verbs:
            return "VERB"
        elif word_lower in self.auxiliaries:
            return "AUX"
        elif word_lower in self.prepositions:
            return "ADP"  # Adposition
        elif word_lower in self.determiners:
            return "DET"
        elif word_lower in self.conjunctions:
            return "CONJ"
        elif word_lower.endswith(self.adjective_endings) and len(word_lower) > 4:
            return "ADJ"
        elif word[0].isupper() and len(word) > 1:
            return "PROPN"  # Proper Noun
        else:
            return "NOUN"

    def _assign_dependencies(self, nodes: List[DependencyNode]):
        """Weist Dependency-Relationen zu"""
        # Finde Hauptverb (ROOT)
        root_idx = -1
        for i, node in enumerate(nodes):
            if node.pos in ("VERB", "AUX"):
                root_idx = i
                node.dep_rel = "ROOT"
                break

        if root_idx == -1:
            return

        # Subjekt (links vom Verb, Nomen/Pronomen)
        for i in range(root_idx):
            if nodes[i].pos in ("NOUN", "PROPN"):
                nodes[i].dep_rel = "nsubj"
                nodes[i].head_idx = root_idx
                nodes[root_idx].children.append(i)
                break

        # Objekt (rechts vom Verb, Nomen)
        for i in range(root_idx + 1, len(nodes)):
            if nodes[i].pos in ("NOUN", "PROPN"):
                nodes[i].dep_rel = "obj"
                nodes[i].head_idx = root_idx
                nodes[root_idx].children.append(i)
                break

        # Determiner und Adjektive zu ihren Nomen
        for i, node in enumerate(nodes):
            if node.pos == "DET" and i + 1 < len(nodes):
                node.dep_rel = "det"
                node.head_idx = i + 1
                nodes[i + 1].children.append(i)
            elif node.pos == "ADJ" and i + 1 < len(nodes):
                node.dep_rel = "amod"
                node.head_idx = i + 1
                nodes[i + 1].children.append(i)

    def get_subject(self, nodes: List[DependencyNode]) -> Optional[str]:
        """Extrahiert das Subjekt"""
        for node in nodes:
            if node.dep_rel == "nsubj":
                return node.word
        return None

    def get_object(self, nodes: List[DependencyNode]) -> Optional[str]:
        """Extrahiert das Objekt"""
        for node in nodes:
            if node.dep_rel == "obj":
                return node.word
        return None

    def get_verb(self, nodes: List[DependencyNode]) -> Optional[str]:
        """Extrahiert das Hauptverb"""
        for node in nodes:
            if node.dep_rel == "ROOT":
                return node.word
        return None


# =============================================================================
# 5. ARGUMENTATIONS-ERKENNUNG
# =============================================================================

class ArgumentDetector:
    """
    Erkennt Argumente in Texten:
    - Claims (Behauptungen)
    - Premises (Begruendungen)
    - Conclusions (Schlussfolgerungen)
    - Evidence (Belege)
    """

    def __init__(self):
        self._init_indicators()

    def _init_indicators(self):
        """Initialisiert Argument-Indikatoren"""

        self.claim_indicators = {
            "ich glaube", "ich denke", "ich meine", "meiner meinung nach",
            "es ist klar", "offensichtlich", "zweifellos", "sicherlich",
            "man sollte", "wir muessen", "es ist wichtig", "es ist notwendig",
            "tatsache ist", "fakt ist", "die wahrheit ist",
            "ich behaupte", "ich bin ueberzeugt", "es steht fest",
        }

        self.premise_indicators = {
            "weil", "da", "denn", "aufgrund", "wegen", "durch",
            "aus diesem grund", "der grund ist", "der grund dafuer",
            "erstens", "zweitens", "drittens", "zunaechst", "dann", "schliesslich",
            "einerseits", "andererseits", "zum einen", "zum anderen",
            "angesichts", "in anbetracht", "bedenkt man",
        }

        self.conclusion_indicators = {
            "daher", "deshalb", "deswegen", "folglich", "somit", "also",
            "daraus folgt", "dies zeigt", "dies beweist", "dies bedeutet",
            "zusammenfassend", "insgesamt", "im ergebnis", "letztendlich",
            "schlussendlich", "abschliessend", "fazit", "ergo",
            "wir koennen schlussfolgern", "daraus ergibt sich",
        }

        self.evidence_indicators = {
            "studien zeigen", "forschung zeigt", "untersuchungen belegen",
            "laut", "gemaess", "nach", "zufolge",
            "statistiken zeigen", "daten belegen", "zahlen zeigen",
            "beispielsweise", "zum beispiel", "etwa", "wie",
            "experten sagen", "wissenschaftler bestaetigen",
            "es wurde nachgewiesen", "es ist bewiesen",
        }

        self.contrast_indicators = {
            "jedoch", "aber", "allerdings", "dennoch", "trotzdem",
            "obwohl", "obgleich", "wenngleich", "zwar...aber",
            "im gegensatz", "im unterschied", "andererseits",
            "kritiker sagen", "gegner argumentieren",
        }

    def detect_arguments(self, text: str) -> List[Argument]:
        """Erkennt Argumente im Text"""
        arguments = []
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for sent in sentences:
            sent_lower = sent.lower()

            # Check fuer jeden Argument-Typ
            arg_type, confidence, indicators = self._classify_sentence(sent_lower)

            if arg_type and confidence > 0.5:
                arguments.append(Argument(
                    arg_type=arg_type,
                    text=sent.strip(),
                    confidence=confidence,
                    indicators=indicators
                ))

        return arguments

    def _classify_sentence(self, sent_lower: str) -> Tuple[Optional[str], float, List[str]]:
        """Klassifiziert einen Satz als Argument-Typ"""

        found_indicators = []

        # Claims
        for indicator in self.claim_indicators:
            if indicator in sent_lower:
                found_indicators.append(indicator)
        if found_indicators:
            return "claim", min(0.6 + len(found_indicators) * 0.1, 0.95), found_indicators

        # Conclusions
        found_indicators = []
        for indicator in self.conclusion_indicators:
            if indicator in sent_lower:
                found_indicators.append(indicator)
        if found_indicators:
            return "conclusion", min(0.7 + len(found_indicators) * 0.1, 0.95), found_indicators

        # Evidence
        found_indicators = []
        for indicator in self.evidence_indicators:
            if indicator in sent_lower:
                found_indicators.append(indicator)
        if found_indicators:
            return "evidence", min(0.75 + len(found_indicators) * 0.1, 0.95), found_indicators

        # Premises
        found_indicators = []
        for indicator in self.premise_indicators:
            if indicator in sent_lower:
                found_indicators.append(indicator)
        if found_indicators:
            return "premise", min(0.65 + len(found_indicators) * 0.1, 0.95), found_indicators

        return None, 0.0, []

    def get_argument_structure(self, arguments: List[Argument]) -> Dict[str, List[str]]:
        """Gibt die Argument-Struktur zurueck"""
        structure = {
            "claims": [],
            "premises": [],
            "conclusions": [],
            "evidence": [],
        }

        for arg in arguments:
            if arg.arg_type in structure:
                structure[arg.arg_type].append(arg.text)

        return structure


# =============================================================================
# 6. IRONIE/SARKASMUS-ERKENNUNG
# =============================================================================

class IronyDetector:
    """
    Erkennt Ironie und Sarkasmus in Texten.

    Verwendet:
    - Sentiment-Kontrast (positive Woerter + negative Kontext)
    - Uebertreibungs-Marker
    - Typische ironische Phrasen
    - Interpunktion (z.B. "..." oder Emojis)
    """

    def __init__(self):
        self._init_markers()

    def _init_markers(self):
        """Initialisiert Ironie-Marker"""

        # Typische ironische Phrasen
        self.ironic_phrases = {
            "na toll", "super gemacht", "wie schoen", "ach wirklich",
            "ja klar", "na sicher", "genau mein humor", "wie unerwartet",
            "wer haette das gedacht", "welch ueberraschung", "wie originell",
            "herzlichen glueckwunsch", "bravo", "sehr hilfreich", "danke fuer nichts",
            "das ist ja mal was neues", "wie clever", "sehr witzig",
            "ja genau", "sicher doch", "klar doch", "logisch",
        }

        # Uebertreibungs-Marker
        self.hyperbole_markers = {
            "absolut", "total", "voellig", "komplett", "100%", "definitiv",
            "immer", "nie", "niemals", "alle", "niemand", "jeder",
            "bester", "schlimmster", "groesster", "kleinster",
            "unglaublich", "wahnsinnig", "irre", "verrueckt",
            "einfach", "natuerlich", "offensichtlich", "selbstverstaendlich",
        }

        # Sentiment-Woerter
        self.positive_words = {
            "toll", "super", "wunderbar", "fantastisch", "grossartig", "perfekt",
            "ausgezeichnet", "hervorragend", "brilliant", "genial", "fabelhaft",
            "schoen", "gut", "nett", "freundlich", "lieb", "suess",
        }

        self.negative_words = {
            "schlecht", "schrecklich", "furchtbar", "miserabel", "katastrophal",
            "grauenhaft", "entsetzlich", "abscheulich", "widerlich", "ekelhaft",
            "problem", "fehler", "versagen", "scheitern", "panne",
        }

        # Kontrastive Konnektoren
        self.contrast_connectors = {
            "aber", "jedoch", "allerdings", "dennoch", "trotzdem",
            "obwohl", "obgleich", "wenngleich",
        }

    def detect(self, text: str) -> IronyResult:
        """Erkennt Ironie im Text"""
        text_lower = text.lower()
        indicators = []
        confidence = 0.0
        irony_type = "verbal"

        # 1. Check fuer bekannte ironische Phrasen
        for phrase in self.ironic_phrases:
            if phrase in text_lower:
                indicators.append(f"phrase: {phrase}")
                confidence += 0.3

        # 2. Check fuer Sentiment-Kontrast
        has_positive = any(w in text_lower for w in self.positive_words)
        has_negative = any(w in text_lower for w in self.negative_words)
        has_contrast = any(c in text_lower for c in self.contrast_connectors)

        if has_positive and has_negative:
            indicators.append("sentiment_contrast")
            confidence += 0.2

        if has_contrast:
            indicators.append("contrast_connector")
            confidence += 0.1

        # 3. Uebertreibungen
        hyperbole_count = sum(1 for h in self.hyperbole_markers if h in text_lower)
        if hyperbole_count >= 2:
            indicators.append(f"hyperbole ({hyperbole_count})")
            confidence += 0.15 * min(hyperbole_count, 3)

        # 4. Interpunktion
        if "..." in text:
            indicators.append("ellipsis")
            confidence += 0.1

        if "!!" in text or "?!" in text or "??" in text:
            indicators.append("emphatic_punctuation")
            confidence += 0.15

        if text.count("!") > 2:
            indicators.append("excessive_exclamation")
            confidence += 0.1

        # 5. Anfuehrungszeichen um positive Woerter
        quoted_positive = re.findall(r'["\'](\w+)["\']', text)
        for word in quoted_positive:
            if word.lower() in self.positive_words:
                indicators.append(f"quoted_positive: {word}")
                confidence += 0.25
                irony_type = "sarcasm"

        # 6. Emojis (wenn Text Emojis enthaelt)
        emoji_pattern = re.compile(r'[:;][-]?[)D(P]|[^\x00-\x7F]')
        if emoji_pattern.search(text):
            indicators.append("emoji_present")
            confidence += 0.1

        # Bestimme Ironie-Typ
        if "sarcasm" in [safe_split_access(i, ":", 0, "nlp_enhanced", "detect_irony", default="") for i in indicators]:
            irony_type = "sarcasm"
        elif "sentiment_contrast" in indicators:
            irony_type = "situational"
        else:
            irony_type = "verbal"

        # Clamp confidence
        confidence = min(confidence, 0.95)

        return IronyResult(
            is_ironic=confidence > 0.35,
            confidence=confidence,
            indicators=indicators,
            irony_type=irony_type
        )


# =============================================================================
# 7. PLAGIATSERKENNUNG
# =============================================================================

class PlagiarismDetector:
    """
    Erkennt Plagiate durch Text-Vergleich.

    Methoden:
    - N-Gram Fingerprinting
    - Jaccard Similarity
    - Cosine Similarity
    - Longest Common Subsequence
    """

    def __init__(self, n: int = 5):
        self.n = n  # N-Gram Groesse

    def compare(self, text1: str, text2: str) -> List[PlagiarismMatch]:
        """Vergleicht zwei Texte auf Plagiat"""
        matches = []

        # 1. Exakte Uebereinstimmungen (lange Phrasen)
        exact_matches = self._find_exact_matches(text1, text2)
        matches.extend(exact_matches)

        # 2. N-Gram basierte Aehnlichkeit
        ngram_sim = self._ngram_similarity(text1, text2)

        # 3. Satz-weise Vergleich
        sentence_matches = self._compare_sentences(text1, text2)
        matches.extend(sentence_matches)

        return matches

    def _find_exact_matches(self, text1: str, text2: str, min_length: int = 30) -> List[PlagiarismMatch]:
        """Findet exakte Uebereinstimmungen"""
        matches = []

        # Sliding Window
        words1 = text1.split()
        words2 = text2.split()

        for window_size in range(min(10, len(words1)), 4, -1):
            for i in range(len(words1) - window_size + 1):
                phrase = " ".join(words1[i:i + window_size])

                if len(phrase) >= min_length and phrase.lower() in text2.lower():
                    matches.append(PlagiarismMatch(
                        source_text=phrase,
                        match_text=phrase,
                        similarity=1.0,
                        match_type="exact"
                    ))

        return matches

    def _ngram_similarity(self, text1: str, text2: str) -> float:
        """Berechnet N-Gram basierte Aehnlichkeit"""
        ngrams1 = self._get_ngrams(text1)
        ngrams2 = self._get_ngrams(text2)

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)

        return intersection / union if union > 0 else 0.0

    def _get_ngrams(self, text: str) -> Set[str]:
        """Extrahiert N-Grams aus Text"""
        words = text.lower().split()
        ngrams = set()

        for i in range(len(words) - self.n + 1):
            ngram = " ".join(words[i:i + self.n])
            ngrams.add(ngram)

        return ngrams

    def _compare_sentences(self, text1: str, text2: str) -> List[PlagiarismMatch]:
        """Vergleicht Saetze paarweise"""
        matches = []

        sentences1 = re.split(r'[.!?]+', text1)
        sentences2 = re.split(r'[.!?]+', text2)

        for sent1 in sentences1:
            sent1 = sent1.strip()
            if len(sent1) < 20:
                continue

            for sent2 in sentences2:
                sent2 = sent2.strip()
                if len(sent2) < 20:
                    continue

                sim = self._sentence_similarity(sent1, sent2)

                if sim > 0.7:
                    match_type = "exact" if sim > 0.95 else "paraphrase"
                    matches.append(PlagiarismMatch(
                        source_text=sent1,
                        match_text=sent2,
                        similarity=sim,
                        match_type=match_type
                    ))

        return matches

    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Berechnet Satz-Aehnlichkeit"""
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def get_overall_similarity(self, text1: str, text2: str) -> float:
        """Berechnet Gesamt-Aehnlichkeit"""
        ngram_sim = self._ngram_similarity(text1, text2)

        # Wort-basierte Jaccard
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        word_sim = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0

        # Gewichteter Durchschnitt
        return 0.6 * ngram_sim + 0.4 * word_sim


# =============================================================================
# 8. AUTOR-STIL-FINGERPRINT
# =============================================================================

class AuthorStyleAnalyzer:
    """
    Erstellt einen Stil-Fingerprint fuer Autoren.

    Features:
    - Wort- und Satzlaenge
    - Vokabular-Reichhaltigkeit
    - Interpunktion
    - Funktionswoerter-Frequenz
    - Satzanfaenge
    - Hapax Legomena
    """

    def __init__(self):
        self.function_words = {
            "der", "die", "das", "und", "oder", "aber", "ist", "sind",
            "hat", "haben", "wird", "werden", "kann", "koennen",
            "ich", "du", "er", "sie", "es", "wir", "ihr",
            "in", "an", "auf", "aus", "bei", "mit", "nach", "von", "zu",
            "nicht", "auch", "noch", "nur", "sehr", "so", "dann", "doch",
        }

    def create_fingerprint(self, text: str) -> AuthorFingerprint:
        """Erstellt einen Stil-Fingerprint"""
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not words or not sentences:
            return AuthorFingerprint(
                avg_word_length=0, avg_sentence_length=0,
                vocabulary_richness=0, punctuation_ratio={},
                function_word_freq={}, sentence_starters={},
                hapax_legomena_ratio=0, fingerprint_vector=[]
            )

        # Basis-Metriken
        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)

        # Vokabular-Reichhaltigkeit (Type-Token-Ratio)
        unique_words = set(w.lower() for w in words)
        vocabulary_richness = len(unique_words) / len(words)

        # Interpunktion
        punctuation_counts = Counter(c for c in text if c in '.,!?;:-()[]"\'')
        total_punct = sum(punctuation_counts.values()) or 1
        punctuation_ratio = {p: count / total_punct for p, count in punctuation_counts.items()}

        # Funktionswoerter
        word_counts = Counter(w.lower() for w in words)
        total_words = len(words)
        function_word_freq = {
            fw: word_counts.get(fw, 0) / total_words
            for fw in self.function_words
        }

        # Satzanfaenge
        sentence_starters = Counter()
        for sent in sentences:
            sent_words = sent.split()
            if sent_words:
                starter = sent_words[0].lower()
                sentence_starters[starter] += 1

        total_sentences = len(sentences)
        sentence_starter_freq = {
            w: count / total_sentences
            for w, count in sentence_starters.most_common(20)
        }

        # Hapax Legomena (Woerter die nur 1x vorkommen)
        hapax = sum(1 for w, c in word_counts.items() if c == 1)
        hapax_ratio = hapax / len(unique_words) if unique_words else 0

        # Fingerprint-Vektor (fuer Vergleiche)
        vector = [
            avg_word_length / 10,
            avg_sentence_length / 50,
            vocabulary_richness,
            hapax_ratio,
            punctuation_ratio.get(',', 0),
            punctuation_ratio.get('.', 0),
            punctuation_ratio.get('!', 0),
            punctuation_ratio.get('?', 0),
        ]

        # Fuege Top Funktionswoerter hinzu
        for fw in ["und", "der", "die", "ist", "in", "nicht", "ich", "das"]:
            vector.append(function_word_freq.get(fw, 0))

        return AuthorFingerprint(
            avg_word_length=avg_word_length,
            avg_sentence_length=avg_sentence_length,
            vocabulary_richness=vocabulary_richness,
            punctuation_ratio=punctuation_ratio,
            function_word_freq=function_word_freq,
            sentence_starters=sentence_starter_freq,
            hapax_legomena_ratio=hapax_ratio,
            fingerprint_vector=vector
        )

    def compare_fingerprints(self, fp1: AuthorFingerprint, fp2: AuthorFingerprint) -> float:
        """Vergleicht zwei Fingerprints (Cosine Similarity)"""
        v1 = fp1.fingerprint_vector
        v2 = fp2.fingerprint_vector

        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)

    def is_same_author(self, fp1: AuthorFingerprint, fp2: AuthorFingerprint, threshold: float = 0.85) -> Tuple[bool, float]:
        """Prueft ob zwei Texte vom selben Autor stammen"""
        similarity = self.compare_fingerprints(fp1, fp2)
        return similarity >= threshold, similarity


# =============================================================================
# UNIFIED ENHANCED NLP CLASS
# =============================================================================

class HoloNLPEnhanced:
    """
    Vereinigte Klasse fuer alle erweiterten NLP-Features.
    """

    def __init__(self):
        self.embeddings = LightweightEmbeddings()
        self.ner = EnhancedNER()
        self.coref = CoreferenceResolver()
        self.dep_parser = SimpleDependencyParser()
        self.argument_detector = ArgumentDetector()
        self.irony_detector = IronyDetector()
        self.plagiarism_detector = PlagiarismDetector()
        self.style_analyzer = AuthorStyleAnalyzer()

        logger.info("HoloNLPEnhanced initialisiert")

    def analyze(self, text: str) -> Dict[str, Any]:
        """Fuehrt vollstaendige NLP-Analyse durch"""

        # Entities
        entities = self.ner.extract_entities(text)

        # Koreferenzen
        coref_clusters = self.coref.resolve(text, entities)

        # Argumente
        arguments = self.argument_detector.detect_arguments(text)

        # Ironie
        irony = self.irony_detector.detect(text)

        # Stil-Fingerprint
        fingerprint = self.style_analyzer.create_fingerprint(text)

        return {
            "entities": entities,
            "coreference_clusters": coref_clusters,
            "arguments": arguments,
            "irony": irony,
            "style_fingerprint": fingerprint,
        }

    def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """Vergleicht zwei Texte"""

        # Plagiat-Check
        plagiarism_matches = self.plagiarism_detector.compare(text1, text2)
        overall_similarity = self.plagiarism_detector.get_overall_similarity(text1, text2)

        # Stil-Vergleich
        fp1 = self.style_analyzer.create_fingerprint(text1)
        fp2 = self.style_analyzer.create_fingerprint(text2)
        same_author, style_similarity = self.style_analyzer.is_same_author(fp1, fp2)

        return {
            "plagiarism_matches": plagiarism_matches,
            "overall_similarity": overall_similarity,
            "style_similarity": style_similarity,
            "likely_same_author": same_author,
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("HOLO NLP ENHANCED v1.0 TEST")
    print("=" * 70)

    nlp = HoloNLPEnhanced()

    test_text = """
    Dr. Maria Schmidt, Professorin an der TU Muenchen, hat gestern eine
    bahnbrechende Entdeckung veroeffentlicht. Sie erklaerte auf der
    Pressekonferenz in Berlin: "Das ist ein Durchbruch fuer die Wissenschaft."

    Die Forscherin arbeitet seit 15 Jahren an diesem Projekt. Studien zeigen,
    dass das neue Verfahren 40% effizienter ist. Daher koennen wir schlussfolgern,
    dass dies die Industrie revolutionieren wird.

    Na toll, jetzt muessen wir alle unsere Systeme umstellen. Wie unerwartet.
    """

    print("\n" + "-" * 50)
    print("ANALYSE")
    print("-" * 50)

    result = nlp.analyze(test_text)

    print(f"\nEntities ({len(result['entities'])}):")
    for e in result['entities'][:10]:
        print(f"  [{e.label}] {e.text} (conf: {e.confidence:.2f})")

    print(f"\nKoreferenzen ({len(result['coreference_clusters'])}):")
    for cluster in result['coreference_clusters']:
        mentions = [m[0] for m in cluster.mentions]
        print(f"  {cluster.main_mention}: {mentions}")

    print(f"\nArgumente ({len(result['arguments'])}):")
    for arg in result['arguments']:
        print(f"  [{arg.arg_type}] {arg.text[:60]}...")

    print(f"\nIronie:")
    irony = result['irony']
    print(f"  Ironisch: {irony.is_ironic} (conf: {irony.confidence:.2f})")
    print(f"  Typ: {irony.irony_type}")
    print(f"  Indikatoren: {irony.indicators}")

    print(f"\nStil-Fingerprint:")
    fp = result['style_fingerprint']
    print(f"  Avg Wortlaenge: {fp.avg_word_length:.1f}")
    print(f"  Avg Satzlaenge: {fp.avg_sentence_length:.1f}")
    print(f"  Vokabular-Reichhaltigkeit: {fp.vocabulary_richness:.3f}")
    print(f"  Hapax Ratio: {fp.hapax_legomena_ratio:.3f}")

    print("\n" + "=" * 70)
    print("TEST ABGESCHLOSSEN")
    print("=" * 70)
