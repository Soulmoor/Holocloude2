"""
HOLO CROSS-REFERENCE ENGINE
============================

Ein fortgeschrittenes System für automatische Querverweise zwischen
verschiedenen Wissensbereichen.

Wie Holos weise Wolfsaugen - sieht Verbindungen, die anderen verborgen bleiben!
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Callable, Any
from enum import Enum
from collections import defaultdict
import random
import logging
import json
import re

logger = logging.getLogger(__name__)


# =============================================================================
# CROSS-REFERENCE TYPEN
# =============================================================================

class ReferenceType(Enum):
    """Arten von Querverweisen"""
    KEYWORD = "keyword"              # Gemeinsames Schlüsselwort
    SEMANTIC = "semantic"            # Semantische Ähnlichkeit
    TEMPORAL = "temporal"            # Zeitliche Verbindung
    CAUSAL = "causal"                # Ursache-Wirkung
    AUTHOR = "author"                # Gleicher Autor/Schöpfer
    GENRE = "genre"                  # Gleiches Genre
    THEME = "theme"                  # Gemeinsames Thema
    CHARACTER = "character"          # Charakterverbindung
    CULTURAL = "cultural"            # Kulturelle Referenz
    INTERTEXTUAL = "intertextual"    # Direkte Referenz in anderem Werk
    INVERSE = "inverse"              # Gegenteiliges Konzept
    EVOLUTION = "evolution"          # Entwicklung/Fortsetzung
    INSPIRATION = "inspiration"      # Hat inspiriert


class ConfidenceLevel(Enum):
    """Konfidenz der Querverweise"""
    DEFINITE = "sicher"       # 100% sicher
    PROBABLE = "wahrscheinlich"  # 70-99%
    POSSIBLE = "möglich"      # 40-69%
    SPECULATIVE = "spekulativ"  # 10-39%


@dataclass
class CrossReference:
    """Ein Querverweis zwischen zwei Wissensentitäten"""
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    ref_type: ReferenceType
    confidence: ConfidenceLevel
    description: str
    shared_keywords: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    wolf_insight: str = ""

    def to_dict(self) -> Dict:
        return {
            "source": self.source_name,
            "target": self.target_name,
            "type": self.ref_type.value,
            "confidence": self.confidence.value,
            "description": self.description,
            "keywords": self.shared_keywords,
            "evidence": self.evidence
        }


@dataclass
class KnowledgeEntity:
    """Eine Wissensentität für Cross-Referencing"""
    id: str
    name: str
    domain: str
    subdomain: str = ""
    keywords: Set[str] = field(default_factory=set)
    themes: Set[str] = field(default_factory=set)
    era: Optional[str] = None
    creator: Optional[str] = None
    related_works: List[str] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# KEYWORD-INDEX
# =============================================================================

class KeywordIndex:
    """
    Invertierter Index für schnelle Keyword-Suche.

    Wie Holos Geruchssinn - findet blitzschnell Verbindungen!
    """

    def __init__(self):
        self.keyword_to_entities: Dict[str, Set[str]] = defaultdict(set)
        self.entity_to_keywords: Dict[str, Set[str]] = defaultdict(set)
        self.keyword_weights: Dict[str, float] = {}

        # Stopwörter die ignoriert werden
        self.stopwords = {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber",
            "ist", "sind", "war", "waren", "wird", "werden", "hat", "haben",
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "in", "im", "auf", "mit", "von", "zu", "für", "nach", "bei"
        }

    def add_entity(self, entity_id: str, keywords: Set[str]):
        """Füge eine Entität zum Index hinzu."""
        # Filtere Stopwörter und normalisiere
        filtered = {kw.lower().strip() for kw in keywords
                   if kw.lower().strip() not in self.stopwords and len(kw) > 2}

        for keyword in filtered:
            self.keyword_to_entities[keyword].add(entity_id)
            self.entity_to_keywords[entity_id].add(keyword)

    def find_related(self, entity_id: str, min_shared: int = 1) -> List[Tuple[str, Set[str]]]:
        """
        Finde verwandte Entitäten basierend auf gemeinsamen Keywords.

        Returns:
            Liste von (entity_id, shared_keywords) Tupeln
        """
        my_keywords = self.entity_to_keywords.get(entity_id, set())
        if not my_keywords:
            return []

        # Zähle gemeinsame Keywords
        related_counts: Dict[str, Set[str]] = defaultdict(set)

        for keyword in my_keywords:
            for other_id in self.keyword_to_entities[keyword]:
                if other_id != entity_id:
                    related_counts[other_id].add(keyword)

        # Filtere nach Mindestanzahl
        results = [(eid, shared) for eid, shared in related_counts.items()
                  if len(shared) >= min_shared]

        # Sortiere nach Anzahl gemeinsamer Keywords
        results.sort(key=lambda x: len(x[1]), reverse=True)

        return results

    def search(self, query: str) -> List[Tuple[str, float]]:
        """
        Suche Entitäten nach Query.

        Returns:
            Liste von (entity_id, score) Tupeln
        """
        query_words = {w.lower().strip() for w in query.split()
                      if w.lower().strip() not in self.stopwords}

        scores: Dict[str, float] = defaultdict(float)

        for word in query_words:
            # Exakte Matches
            for entity_id in self.keyword_to_entities.get(word, []):
                scores[entity_id] += 1.0

            # Partial Matches
            for keyword in self.keyword_to_entities:
                if word in keyword or keyword in word:
                    for entity_id in self.keyword_to_entities[keyword]:
                        scores[entity_id] += 0.5

        results = [(eid, score) for eid, score in scores.items()]
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:20]


# =============================================================================
# SEMANTIC SIMILARITY ENGINE
# =============================================================================

class SemanticSimilarityEngine:
    """
    Berechnet semantische Ähnlichkeit zwischen Konzepten.

    Nutzt vordefinierte semantische Cluster und Beziehungen.
    """

    def __init__(self):
        # Semantische Cluster - Wörter die ähnliche Bedeutung haben
        self.semantic_clusters = {
            "kampf": {"krieg", "battle", "fight", "kämpfen", "action", "duell", "konflikt"},
            "liebe": {"romantik", "romance", "love", "beziehung", "herz", "gefühl"},
            "freundschaft": {"nakama", "bonds", "friendship", "zusammen", "team"},
            "tod": {"sterben", "death", "verlust", "trauer", "ende"},
            "macht": {"power", "stärke", "kraft", "herrschaft", "kontrolle"},
            "magie": {"magic", "zauber", "übernatürlich", "fantasy", "mystisch"},
            "technologie": {"tech", "cyber", "mecha", "roboter", "zukunft", "sci-fi"},
            "natur": {"wald", "tiere", "umwelt", "wild", "ökologie"},
            "musik": {"song", "melodie", "soundtrack", "opening", "ending"},
            "psychologie": {"mental", "trauma", "emotion", "gefühl", "seele"},
            "geschichte": {"history", "vergangenheit", "epoche", "historisch"},
            "philosophie": {"existenz", "sinn", "moral", "ethik", "wahrheit"},
            "comedy": {"humor", "lustig", "witzig", "lachen", "komödie"},
            "horror": {"grusel", "angst", "dunkel", "unheimlich", "creepy"},
            "mystery": {"geheimnis", "rätsel", "detektiv", "krimi", "thriller"},
            "schule": {"school", "bildung", "lehrer", "schüler", "highschool"},
            "familie": {"eltern", "kinder", "blut", "verwandte", "family"},
            "tier": {"animal", "kemono", "wolf", "katze", "hund", "beast"},
            "japan": {"nihon", "nippon", "japanisch", "tokyo", "osaka"},
            "fantasy": {"mittelalter", "schwert", "drache", "magie", "abenteuer"},
        }

        # Invertierter Index: Wort -> Cluster-Name
        self.word_to_cluster: Dict[str, str] = {}
        for cluster, words in self.semantic_clusters.items():
            for word in words:
                self.word_to_cluster[word] = cluster
            self.word_to_cluster[cluster] = cluster

    def calculate_similarity(self, keywords_a: Set[str], keywords_b: Set[str]) -> float:
        """
        Berechne semantische Ähnlichkeit zwischen zwei Keyword-Sets.

        Returns:
            Ähnlichkeitsscore zwischen 0.0 und 1.0
        """
        if not keywords_a or not keywords_b:
            return 0.0

        # Direkte Überlappung
        direct_overlap = len(keywords_a & keywords_b)

        # Semantische Cluster-Überlappung
        clusters_a = {self.word_to_cluster.get(w.lower(), None) for w in keywords_a}
        clusters_b = {self.word_to_cluster.get(w.lower(), None) for w in keywords_b}
        clusters_a.discard(None)
        clusters_b.discard(None)

        cluster_overlap = len(clusters_a & clusters_b)

        # Kombinierter Score
        max_possible = max(len(keywords_a), len(keywords_b))
        if max_possible == 0:
            return 0.0

        direct_score = direct_overlap / max_possible
        cluster_score = cluster_overlap / max(len(clusters_a), len(clusters_b), 1)

        # Gewichtete Kombination
        return min(1.0, direct_score * 0.6 + cluster_score * 0.4)

    def find_shared_themes(self, keywords_a: Set[str], keywords_b: Set[str]) -> List[str]:
        """Finde gemeinsame thematische Cluster."""
        clusters_a = {self.word_to_cluster.get(w.lower(), None) for w in keywords_a}
        clusters_b = {self.word_to_cluster.get(w.lower(), None) for w in keywords_b}
        clusters_a.discard(None)
        clusters_b.discard(None)

        return list(clusters_a & clusters_b)


# =============================================================================
# CROSS-REFERENCE ENGINE
# =============================================================================

class CrossReferenceEngine:
    """
    Die Haupt-Engine für automatische Querverweise.

    Wie Holos weiser Wolfsverstand - verbindet das scheinbar Unverbundene!
    """

    def __init__(self):
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.keyword_index = KeywordIndex()
        self.semantic_engine = SemanticSimilarityEngine()
        self.references: List[CrossReference] = []
        self.reference_cache: Dict[Tuple[str, str], CrossReference] = {}

        # Domain-Beziehungen für Cross-Domain Referenzen
        self.domain_relations = {
            ("Anime", "Manga"): ReferenceType.EVOLUTION,
            ("Anime", "Light Novel"): ReferenceType.EVOLUTION,
            ("Anime", "Gaming"): ReferenceType.GENRE,
            ("Geschichte", "Anime"): ReferenceType.INSPIRATION,
            ("Mythologie", "Anime"): ReferenceType.INSPIRATION,
            ("Musik", "Anime"): ReferenceType.THEME,
            ("Psychologie", "Anime"): ReferenceType.THEME,
            ("Technologie", "Sci-Fi"): ReferenceType.THEME,
        }

        self._initialize()
        logger.info(f"CrossReferenceEngine initialisiert mit {len(self.entities)} Entitäten")

    def _initialize(self):
        """Initialisiere mit vordefinierten Entitäten."""
        self._load_anime_entities()
        self._load_cultural_entities()
        self._load_science_entities()
        self._load_music_entities()
        self._load_mythology_entities()
        self._build_indexes()

    def _load_anime_entities(self):
        """Lade Anime-bezogene Entitäten."""
        anime_data = [
            # Format: (id, name, subdomain, keywords, themes, era, creator)
            ("spice_and_wolf", "Spice and Wolf", "Fantasy/Romance",
             {"wolf", "handel", "wirtschaft", "mittelalter", "romance", "reise", "kemonomimi"},
             {"liebe", "freundschaft", "wirtschaft", "abenteuer"}, "2008", "Isuna Hasekura"),

            ("attack_on_titan", "Attack on Titan", "Action/Dark Fantasy",
             {"titan", "mauer", "krieg", "freiheit", "militär", "mystery"},
             {"kampf", "freiheit", "opfer", "wahrheit"}, "2013", "Hajime Isayama"),

            ("demon_slayer", "Demon Slayer", "Action/Supernatural",
             {"dämon", "katana", "familie", "taisho", "breath", "action"},
             {"familie", "rache", "güte", "kampf"}, "2019", "Koyoharu Gotouge"),

            ("jujutsu_kaisen", "Jujutsu Kaisen", "Action/Supernatural",
             {"fluch", "exorzist", "curse", "tokyo", "kampf", "dark"},
             {"macht", "freundschaft", "opfer"}, "2020", "Gege Akutami"),

            ("one_piece", "One Piece", "Action/Adventure",
             {"pirat", "schatz", "abenteuer", "nakama", "meer", "freiheit"},
             {"freundschaft", "freiheit", "träume", "abenteuer"}, "1999", "Eiichiro Oda"),

            ("evangelion", "Neon Genesis Evangelion", "Mecha/Psychological",
             {"mecha", "engel", "psychologie", "apokalypse", "trauma"},
             {"existenz", "identität", "trauma", "einsamkeit"}, "1995", "Hideaki Anno"),

            ("steins_gate", "Steins;Gate", "Sci-Fi/Thriller",
             {"zeitreise", "wissenschaft", "thriller", "schicksal", "lab"},
             {"zeit", "opfer", "freundschaft", "konsequenz"}, "2011", "5pb."),

            ("death_note", "Death Note", "Psychological/Thriller",
             {"tod", "gerechtigkeit", "katz-und-maus", "notebook", "shinigami"},
             {"macht", "moral", "gerechtigkeit", "verderben"}, "2006", "Tsugumi Ohba"),

            ("fullmetal_alchemist", "Fullmetal Alchemist", "Action/Fantasy",
             {"alchemie", "brüder", "philosophen-stein", "militär", "äquivalent"},
             {"opfer", "familie", "wahrheit", "erlösung"}, "2003", "Hiromu Arakawa"),

            ("cowboy_bebop", "Cowboy Bebop", "Sci-Fi/Action",
             {"weltraum", "kopfgeldjäger", "jazz", "past", "blues"},
             {"vergangenheit", "einsamkeit", "freiheit"}, "1998", "Shinichiro Watanabe"),

            ("ghost_in_shell", "Ghost in the Shell", "Sci-Fi/Cyberpunk",
             {"cyber", "bewusstsein", "identität", "hacker", "zukunft"},
             {"identität", "technologie", "existenz"}, "1995", "Mamoru Oshii"),

            ("my_hero_academia", "My Hero Academia", "Action/Superhero",
             {"held", "quirk", "superheld", "schule", "training"},
             {"held", "wachstum", "freundschaft", "gerechtigkeit"}, "2016", "Kohei Horikoshi"),

            ("chainsaw_man", "Chainsaw Man", "Action/Horror",
             {"dämon", "kettensäge", "chaos", "existenz", "absurd"},
             {"existenz", "wünsche", "freundschaft"}, "2022", "Tatsuki Fujimoto"),

            ("spy_family", "Spy x Family", "Action/Comedy",
             {"spion", "familie", "comedy", "krieg", "geheimnis"},
             {"familie", "frieden", "liebe", "lügen"}, "2022", "Tatsuya Endo"),

            ("violet_evergarden", "Violet Evergarden", "Drama",
             {"brief", "emotion", "krieg", "heilung", "liebe"},
             {"liebe", "verständnis", "heilung", "kommunikation"}, "2018", "Kana Akatsuki"),

            ("mob_psycho", "Mob Psycho 100", "Action/Comedy",
             {"esper", "psycho", "selbstverbesserung", "comedy", "geist"},
             {"wachstum", "selbstwert", "menschlichkeit"}, "2016", "ONE"),

            ("made_in_abyss", "Made in Abyss", "Fantasy/Adventure",
             {"abyss", "artefakt", "expedition", "dunkel", "kindheit"},
             {"neugier", "opfer", "abenteuer", "dunkelheit"}, "2017", "Akihito Tsukushi"),

            ("frieren", "Frieren: Beyond Journey's End", "Fantasy/Drama",
             {"elf", "zeit", "erinnerung", "magie", "reise"},
             {"zeit", "erinnerung", "verständnis", "verlust"}, "2023", "Kanehito Yamada"),
        ]

        for data in anime_data:
            entity = KnowledgeEntity(
                id=data[0],
                name=data[1],
                domain="Anime",
                subdomain=data[2],
                keywords=set(data[3]),
                themes=set(data[4]),
                era=data[5],
                creator=data[6]
            )
            self.entities[entity.id] = entity

    def _load_cultural_entities(self):
        """Lade kulturelle Entitäten."""
        cultural_data = [
            ("bushido", "Bushido", "Philosophie",
             {"samurai", "ehre", "loyalität", "tod", "schwert", "krieger"},
             {"ehre", "loyalität", "mut", "disziplin"}, "feudal"),

            ("ikigai", "Ikigai", "Philosophie",
             {"leben", "sinn", "passion", "zweck", "japan"},
             {"sinn", "freude", "arbeit", "leben"}, "modern"),

            ("wabi_sabi", "Wabi-Sabi", "Ästhetik",
             {"unvollkommen", "vergänglich", "einfach", "natur"},
             {"schönheit", "vergänglichkeit", "akzeptanz"}, "traditionell"),

            ("mono_no_aware", "Mono no Aware", "Ästhetik",
             {"vergänglich", "traurig", "schön", "kirschblüte"},
             {"vergänglichkeit", "emotion", "empathie"}, "traditionell"),

            ("kawaii", "Kawaii-Kultur", "Popkultur",
             {"niedlich", "cute", "moe", "idol", "mode"},
             {"niedlich", "jugend", "konsum"}, "modern"),

            ("otaku", "Otaku-Kultur", "Subkultur",
             {"anime", "manga", "sammeln", "fan", "akihabara"},
             {"passion", "identität", "gemeinschaft"}, "modern"),

            ("cosplay", "Cosplay", "Subkultur",
             {"kostüm", "identität", "kreativ", "fan", "convention"},
             {"kreativität", "identität", "gemeinschaft"}, "modern"),

            ("hanami", "Hanami", "Tradition",
             {"kirschblüte", "sakura", "fest", "frühling", "natur"},
             {"natur", "vergänglichkeit", "gemeinschaft"}, "traditionell"),

            ("onsen", "Onsen-Kultur", "Tradition",
             {"bad", "entspannung", "nackt", "japan", "natur"},
             {"entspannung", "natur", "reinigung"}, "traditionell"),

            ("teezeremonie", "Teezeremonie", "Tradition",
             {"tee", "zen", "ritual", "stille", "harmonie"},
             {"harmonie", "respekt", "reinheit", "stille"}, "traditionell"),
        ]

        for data in cultural_data:
            entity = KnowledgeEntity(
                id=data[0],
                name=data[1],
                domain="Kultur",
                subdomain=data[2],
                keywords=set(data[3]),
                themes=set(data[4]),
                era=data[5]
            )
            self.entities[entity.id] = entity

    def _load_science_entities(self):
        """Lade wissenschaftliche Entitäten."""
        science_data = [
            ("ai", "Künstliche Intelligenz", "Informatik",
             {"computer", "lernen", "neural", "maschine", "algorithmus"},
             {"intelligenz", "zukunft", "ethik"}, "modern"),

            ("quantum", "Quantenphysik", "Physik",
             {"quanten", "welle", "partikel", "unschärfe", "verschränkung"},
             {"realität", "messung", "paradox"}, "modern"),

            ("psychology", "Psychologie", "Sozialwissenschaft",
             {"geist", "verhalten", "emotion", "trauma", "therapie"},
             {"verständnis", "heilung", "verhalten"}, "modern"),

            ("evolution", "Evolutionstheorie", "Biologie",
             {"darwin", "selektion", "anpassung", "art", "überleben"},
             {"veränderung", "überleben", "anpassung"}, "19. Jahrhundert"),

            ("neuroscience", "Neurowissenschaft", "Biologie",
             {"gehirn", "neuron", "bewusstsein", "plastizität"},
             {"bewusstsein", "lernen", "verhalten"}, "modern"),

            ("spacetime", "Raumzeit", "Physik",
             {"einstein", "relativität", "zeit", "raum", "gravitation"},
             {"zeit", "realität", "universum"}, "20. Jahrhundert"),
        ]

        for data in science_data:
            entity = KnowledgeEntity(
                id=data[0],
                name=data[1],
                domain="Wissenschaft",
                subdomain=data[2],
                keywords=set(data[3]),
                themes=set(data[4]),
                era=data[5]
            )
            self.entities[entity.id] = entity

    def _load_music_entities(self):
        """Lade Musik-Entitäten."""
        music_data = [
            ("jpop", "J-Pop", "Genre",
             {"japan", "idol", "catchy", "pop", "dance"},
             {"jugend", "energie", "liebe"}, "modern"),

            ("anisong", "Anime Songs", "Genre",
             {"opening", "ending", "anime", "nostalgie", "emotion"},
             {"nostalgie", "emotion", "identität"}, "modern"),

            ("vocaloid", "Vocaloid", "Technologie",
             {"miku", "synthese", "virtual", "computer", "stimme"},
             {"kreativität", "technologie", "gemeinschaft"}, "modern"),

            ("citypop", "City Pop", "Genre",
             {"80er", "funk", "disco", "nostalgie", "urban"},
             {"nostalgie", "freiheit", "romantik"}, "1980er"),

            ("visual_kei", "Visual Kei", "Subkultur",
             {"rock", "visual", "mode", "androgyn", "theatralik"},
             {"identität", "kunst", "rebellion"}, "modern"),

            ("yoasobi", "YOASOBI", "Künstler",
             {"novel", "story", "synthpop", "ikura", "ayase"},
             {"erzählung", "emotion", "literatur"}, "2019"),

            ("ado", "Ado", "Künstler",
             {"stimme", "emotion", "power", "anonym", "internet"},
             {"emotion", "rebellion", "geheimnis"}, "2020"),
        ]

        for data in music_data:
            entity = KnowledgeEntity(
                id=data[0],
                name=data[1],
                domain="Musik",
                subdomain=data[2],
                keywords=set(data[3]),
                themes=set(data[4]),
                era=data[5]
            )
            self.entities[entity.id] = entity

    def _load_mythology_entities(self):
        """Lade mythologische Entitäten."""
        mythology_data = [
            ("yokai", "Yokai", "Folklore",
             {"geist", "monster", "übernatürlich", "japan", "nacht"},
             {"angst", "erklärung", "natur"}, "traditionell"),

            ("kitsune", "Kitsune", "Folklore",
             {"fuchs", "verwandlung", "list", "magie", "schwanz"},
             {"weisheit", "täuschung", "macht"}, "traditionell"),

            ("tanuki", "Tanuki", "Folklore",
             {"verwandlung", "glück", "bauch", "sake", "natur"},
             {"glück", "täuschung", "natur"}, "traditionell"),

            ("ookami", "Ōkami (Wolf)", "Folklore",
             {"wolf", "gott", "beschützer", "berg", "shinto"},
             {"schutz", "natur", "göttlich"}, "traditionell"),

            ("inari", "Inari", "Religion",
             {"fuchs", "reis", "ernte", "handel", "schrein"},
             {"wohlstand", "fruchtbarkeit", "schutz"}, "traditionell"),

            ("dragon_east", "Östlicher Drache", "Mythologie",
             {"drache", "wasser", "wetter", "weise", "glück"},
             {"weisheit", "macht", "glück"}, "traditionell"),

            ("dragon_west", "Westlicher Drache", "Mythologie",
             {"drache", "feuer", "schatz", "held", "kampf"},
             {"gier", "macht", "gefahr"}, "traditionell"),

            ("tsukuyomi", "Tsukuyomi", "Shintoismus",
             {"mond", "nacht", "gott", "shinto", "silber"},
             {"nacht", "geheimnis", "zyklen"}, "traditionell"),
        ]

        for data in mythology_data:
            entity = KnowledgeEntity(
                id=data[0],
                name=data[1],
                domain="Mythologie",
                subdomain=data[2],
                keywords=set(data[3]),
                themes=set(data[4]),
                era=data[5]
            )
            self.entities[entity.id] = entity

    def _build_indexes(self):
        """Baue alle Indexe auf."""
        for entity_id, entity in self.entities.items():
            all_keywords = entity.keywords | entity.themes
            all_keywords.add(entity.name.lower())
            if entity.creator:
                all_keywords.add(entity.creator.lower())
            self.keyword_index.add_entity(entity_id, all_keywords)

    # =========================================================================
    # QUERVERWEIS-GENERIERUNG
    # =========================================================================

    def find_cross_references(self, entity_id: str,
                             min_confidence: ConfidenceLevel = ConfidenceLevel.POSSIBLE
                             ) -> List[CrossReference]:
        """
        Finde alle Querverweise für eine Entität.

        Args:
            entity_id: ID der Quellentität
            min_confidence: Minimale Konfidenz

        Returns:
            Liste von Querverweisen
        """
        if entity_id not in self.entities:
            return []

        source = self.entities[entity_id]
        references = []

        # 1. Keyword-basierte Referenzen
        keyword_matches = self.keyword_index.find_related(entity_id, min_shared=2)
        for target_id, shared in keyword_matches[:15]:
            ref = self._create_keyword_reference(source, self.entities[target_id], shared)
            if ref and self._confidence_meets_minimum(ref.confidence, min_confidence):
                references.append(ref)

        # 2. Thematische Referenzen
        for target_id, target in self.entities.items():
            if target_id == entity_id:
                continue

            shared_themes = source.themes & target.themes
            if len(shared_themes) >= 2:
                ref = self._create_thematic_reference(source, target, shared_themes)
                if ref and self._confidence_meets_minimum(ref.confidence, min_confidence):
                    references.append(ref)

        # 3. Gleicher Schöpfer
        if source.creator:
            for target_id, target in self.entities.items():
                if target_id != entity_id and target.creator == source.creator:
                    ref = self._create_author_reference(source, target)
                    references.append(ref)

        # 4. Cross-Domain Referenzen
        for target_id, target in self.entities.items():
            if target_id == entity_id:
                continue

            domain_pair = (source.domain, target.domain)
            if domain_pair in self.domain_relations:
                semantic_sim = self.semantic_engine.calculate_similarity(
                    source.keywords | source.themes,
                    target.keywords | target.themes
                )
                if semantic_sim > 0.3:
                    ref = self._create_cross_domain_reference(source, target, semantic_sim)
                    if ref and self._confidence_meets_minimum(ref.confidence, min_confidence):
                        references.append(ref)

        # Deduplizieren und sortieren
        seen = set()
        unique_refs = []
        for ref in references:
            key = (ref.source_id, ref.target_id, ref.ref_type.value)
            if key not in seen:
                seen.add(key)
                unique_refs.append(ref)

        # Sortiere nach Konfidenz
        confidence_order = {
            ConfidenceLevel.DEFINITE: 4,
            ConfidenceLevel.PROBABLE: 3,
            ConfidenceLevel.POSSIBLE: 2,
            ConfidenceLevel.SPECULATIVE: 1
        }
        unique_refs.sort(key=lambda r: confidence_order.get(r.confidence, 0), reverse=True)

        return unique_refs

    def _create_keyword_reference(self, source: KnowledgeEntity,
                                  target: KnowledgeEntity,
                                  shared: Set[str]) -> Optional[CrossReference]:
        """Erstelle einen Keyword-basierten Querverweis."""
        shared_list = list(shared)

        # Bestimme Konfidenz basierend auf Anzahl gemeinsamer Keywords
        if len(shared) >= 4:
            confidence = ConfidenceLevel.DEFINITE
        elif len(shared) >= 3:
            confidence = ConfidenceLevel.PROBABLE
        elif len(shared) >= 2:
            confidence = ConfidenceLevel.POSSIBLE
        else:
            return None

        return CrossReference(
            source_id=source.id,
            source_name=source.name,
            target_id=target.id,
            target_name=target.name,
            ref_type=ReferenceType.KEYWORD,
            confidence=confidence,
            description=f"Teilen die Konzepte: {', '.join(shared_list[:4])}",
            shared_keywords=shared_list,
            wolf_insight=self._generate_wolf_insight(shared_list)
        )

    def _create_thematic_reference(self, source: KnowledgeEntity,
                                   target: KnowledgeEntity,
                                   shared_themes: Set[str]) -> CrossReference:
        """Erstelle einen thematischen Querverweis."""
        themes_list = list(shared_themes)

        confidence = (ConfidenceLevel.DEFINITE if len(shared_themes) >= 3
                     else ConfidenceLevel.PROBABLE)

        return CrossReference(
            source_id=source.id,
            source_name=source.name,
            target_id=target.id,
            target_name=target.name,
            ref_type=ReferenceType.THEME,
            confidence=confidence,
            description=f"Teilen thematische Elemente: {', '.join(themes_list)}",
            shared_keywords=themes_list,
            evidence=[f"Beide behandeln das Thema '{t}'" for t in themes_list[:3]],
            wolf_insight=self._generate_theme_insight(themes_list)
        )

    def _create_author_reference(self, source: KnowledgeEntity,
                                target: KnowledgeEntity) -> CrossReference:
        """Erstelle einen Autor-basierten Querverweis."""
        return CrossReference(
            source_id=source.id,
            source_name=source.name,
            target_id=target.id,
            target_name=target.name,
            ref_type=ReferenceType.AUTHOR,
            confidence=ConfidenceLevel.DEFINITE,
            description=f"Vom selben Schöpfer: {source.creator}",
            evidence=[f"Beide wurden von {source.creator} erschaffen"],
            wolf_insight="*Ohren aufgestellt* Der gleiche Geist erschuf beides!"
        )

    def _create_cross_domain_reference(self, source: KnowledgeEntity,
                                       target: KnowledgeEntity,
                                       similarity: float) -> CrossReference:
        """Erstelle einen Cross-Domain Querverweis."""
        ref_type = self.domain_relations.get(
            (source.domain, target.domain),
            ReferenceType.SEMANTIC
        )

        if similarity > 0.6:
            confidence = ConfidenceLevel.PROBABLE
        elif similarity > 0.4:
            confidence = ConfidenceLevel.POSSIBLE
        else:
            confidence = ConfidenceLevel.SPECULATIVE

        shared_themes = self.semantic_engine.find_shared_themes(
            source.keywords | source.themes,
            target.keywords | target.themes
        )

        return CrossReference(
            source_id=source.id,
            source_name=source.name,
            target_id=target.id,
            target_name=target.name,
            ref_type=ref_type,
            confidence=confidence,
            description=f"Cross-Domain Verbindung zwischen {source.domain} und {target.domain}",
            shared_keywords=shared_themes,
            evidence=[f"Semantische Ähnlichkeit: {similarity*100:.0f}%"],
            wolf_insight=self._generate_cross_domain_insight(source.domain, target.domain)
        )

    def _confidence_meets_minimum(self, actual: ConfidenceLevel,
                                  minimum: ConfidenceLevel) -> bool:
        """Prüfe ob Konfidenz Minimum erreicht."""
        order = [ConfidenceLevel.SPECULATIVE, ConfidenceLevel.POSSIBLE,
                ConfidenceLevel.PROBABLE, ConfidenceLevel.DEFINITE]
        return order.index(actual) >= order.index(minimum)

    def _generate_wolf_insight(self, keywords: List[str]) -> str:
        """Generiere einen Wolf-Kommentar für Keywords."""
        templates = [
            "*Ohren zucken* {kw} verbindet diese Welten!",
            "*nachdenklich* Interessant... beide teilen {kw}.",
            "*Schwanz wedelt* Ich sehe die Verbindung durch {kw}!",
            "*weise blickend* {kw} - ein roter Faden zwischen den Geschichten.",
        ]
        kw = ", ".join(keywords[:2]) if keywords else "etwas Besonderes"
        return random.choice(templates).format(kw=kw)

    def _generate_theme_insight(self, themes: List[str]) -> str:
        """Generiere einen Kommentar für Themen."""
        templates = [
            "*seufzt* {theme} - ein zeitloses Thema.",
            "Beide erkunden {theme}... wie interessant!",
            "*Ohren aufmerksam* {theme} verbindet Menschen über Genres hinweg.",
        ]
        theme = themes[0] if themes else "etwas Tiefes"
        return random.choice(templates).format(theme=theme)

    def _generate_cross_domain_insight(self, domain_a: str, domain_b: str) -> str:
        """Generiere Kommentar für Cross-Domain."""
        return f"*staunend* {domain_a} und {domain_b} sprechen dieselbe Sprache!"

    # =========================================================================
    # ABFRAGE-METHODEN
    # =========================================================================

    def search_entities(self, query: str) -> List[Tuple[KnowledgeEntity, float]]:
        """Suche Entitäten nach Query."""
        results = self.keyword_index.search(query)
        return [(self.entities[eid], score) for eid, score in results if eid in self.entities]

    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """Hole eine Entität nach ID."""
        return self.entities.get(entity_id)

    def get_all_references_for_domain(self, domain: str) -> List[CrossReference]:
        """Hole alle Querverweise für eine Domain."""
        all_refs = []
        for entity_id, entity in self.entities.items():
            if entity.domain.lower() == domain.lower():
                refs = self.find_cross_references(entity_id)
                all_refs.extend(refs)
        return all_refs

    def build_reference_web(self, start_entity: str, depth: int = 2) -> Dict:
        """
        Baue ein Netz von Querverweisen ausgehend von einer Entität.

        Returns:
            Dictionary mit Knoten und Kanten
        """
        visited = set()
        nodes = {}
        edges = []

        def explore(entity_id: str, current_depth: int):
            if entity_id in visited or current_depth > depth:
                return
            visited.add(entity_id)

            entity = self.entities.get(entity_id)
            if not entity:
                return

            nodes[entity_id] = {
                "name": entity.name,
                "domain": entity.domain,
                "themes": list(entity.themes)[:3]
            }

            refs = self.find_cross_references(entity_id, ConfidenceLevel.POSSIBLE)
            for ref in refs[:5]:  # Maximal 5 pro Knoten
                edges.append({
                    "source": ref.source_id,
                    "target": ref.target_id,
                    "type": ref.ref_type.value,
                    "confidence": ref.confidence.value
                })
                explore(ref.target_id, current_depth + 1)

        explore(start_entity, 0)

        return {"nodes": nodes, "edges": edges}

    # =========================================================================
    # FORMATIERUNG
    # =========================================================================

    def format_reference(self, ref: CrossReference, style: str = "full") -> str:
        """Formatiere einen Querverweis für die Ausgabe."""
        if style == "short":
            return f"**{ref.source_name}** ↔ **{ref.target_name}** ({ref.ref_type.value})"

        elif style == "wolf":
            parts = [
                f"🔗 **{ref.source_name}** ↔ **{ref.target_name}**",
                "",
                f"*Typ:* {ref.ref_type.value}",
                f"*Sicherheit:* {ref.confidence.value}",
                "",
                ref.description,
            ]
            if ref.shared_keywords:
                parts.append(f"")
                parts.append(f"*Gemeinsam:* {', '.join(ref.shared_keywords[:4])}")
            if ref.wolf_insight:
                parts.append(f"")
                parts.append(f"🐺 {ref.wolf_insight}")
            return "\n".join(parts)

        else:  # full
            confidence_icons = {
                ConfidenceLevel.DEFINITE: "🟢",
                ConfidenceLevel.PROBABLE: "🟡",
                ConfidenceLevel.POSSIBLE: "🟠",
                ConfidenceLevel.SPECULATIVE: "🔴"
            }

            parts = [
                f"### {ref.source_name} ↔ {ref.target_name}",
                "",
                f"**Typ:** {ref.ref_type.value}",
                f"**Sicherheit:** {confidence_icons.get(ref.confidence, '')} {ref.confidence.value}",
                "",
                f"*{ref.description}*",
            ]
            if ref.shared_keywords:
                parts.append(f"")
                parts.append(f"**Schlüsselwörter:** {', '.join(ref.shared_keywords)}")
            if ref.evidence:
                parts.append(f"")
                parts.append("**Belege:**")
                for ev in ref.evidence[:3]:
                    parts.append(f"  - {ev}")
            if ref.wolf_insight:
                parts.append(f"")
                parts.append(f"🐺 *{ref.wolf_insight}*")

            return "\n".join(parts)

    def format_entity(self, entity: KnowledgeEntity) -> str:
        """Formatiere eine Entität für die Ausgabe."""
        return (f"**{entity.name}** ({entity.domain}/{entity.subdomain})\n"
               f"*Keywords:* {', '.join(list(entity.keywords)[:5])}\n"
               f"*Themen:* {', '.join(list(entity.themes)[:4])}")


# =============================================================================
# REFERENCE FINDER - VEREINFACHTE INTERFACE
# =============================================================================

class ReferenceFinder:
    """
    Vereinfachtes Interface für Querverweis-Suche.

    Wie Holos Instinkt - schnell und zuverlässig!
    """

    def __init__(self, engine: CrossReferenceEngine):
        self.engine = engine

    def find(self, query: str) -> str:
        """
        Finde Querverweise zu einem Suchbegriff.

        Returns:
            Formatierte Ergebnisstring
        """
        # Suche passende Entitäten
        matches = self.engine.search_entities(query)

        if not matches:
            return f"*Ohren angelegt* Ich finde keine Einträge zu '{query}'..."

        # Nimm beste Übereinstimmung
        best_entity, score = matches[0]

        # Finde Querverweise
        refs = self.engine.find_cross_references(best_entity.id)

        if not refs:
            return (f"**{best_entity.name}** gefunden, aber keine Querverweise...\n\n"
                   f"{self.engine.format_entity(best_entity)}")

        # Formatiere Ergebnis
        parts = [
            f"🔍 **Querverweise für: {best_entity.name}**",
            "",
            f"*{len(refs)} Verbindung(en) gefunden:*",
            ""
        ]

        for ref in refs[:7]:
            parts.append(self.engine.format_reference(ref, style="short"))
            parts.append(f"   {ref.description}")
            if ref.wolf_insight:
                parts.append(f"   🐺 {ref.wolf_insight}")
            parts.append("")

        return "\n".join(parts)

    def explore(self, entity_name: str) -> str:
        """
        Erkunde ein Thema im Detail.

        Returns:
            Detaillierte Erkundungsergebnisse
        """
        matches = self.engine.search_entities(entity_name)

        if not matches:
            return f"*traurig* '{entity_name}' ist mir unbekannt..."

        entity, _ = matches[0]
        refs = self.engine.find_cross_references(entity.id, ConfidenceLevel.POSSIBLE)

        # Gruppiere nach Typ
        by_type: Dict[ReferenceType, List[CrossReference]] = defaultdict(list)
        for ref in refs:
            by_type[ref.ref_type].append(ref)

        parts = [
            f"📖 **Tiefenanalyse: {entity.name}**",
            "",
            self.engine.format_entity(entity),
            "",
            "---",
            ""
        ]

        for ref_type, type_refs in by_type.items():
            parts.append(f"**{ref_type.value.title()} Verbindungen:**")
            for ref in type_refs[:3]:
                other = ref.target_name if ref.source_id == entity.id else ref.source_name
                parts.append(f"  • {other} - {ref.confidence.value}")
            parts.append("")

        return "\n".join(parts)

    def surprise_me(self) -> str:
        """
        Zeige eine überraschende Cross-Domain Verbindung.

        Returns:
            Eine interessante Verbindung
        """
        # Wähle zwei zufällige Entitäten aus verschiedenen Domains
        entities = list(self.engine.entities.values())
        random.shuffle(entities)

        for source in entities[:10]:
            refs = self.engine.find_cross_references(source.id, ConfidenceLevel.POSSIBLE)
            cross_domain = [r for r in refs
                          if self.engine.entities[r.target_id].domain != source.domain]

            if cross_domain:
                ref = random.choice(cross_domain)
                return (f"✨ **Überraschende Verbindung!**\n\n"
                       f"{self.engine.format_reference(ref, style='wolf')}")

        return "*seufzt* Keine überraschenden Verbindungen gefunden heute..."


# =============================================================================
# SINGLETON & FACTORY
# =============================================================================

_cross_ref_engine: Optional[CrossReferenceEngine] = None
_reference_finder: Optional[ReferenceFinder] = None


def get_cross_reference_engine() -> CrossReferenceEngine:
    """Gibt die Singleton-Instanz der CrossReferenceEngine zurück."""
    global _cross_ref_engine
    if _cross_ref_engine is None:
        _cross_ref_engine = CrossReferenceEngine()
    return _cross_ref_engine


def get_reference_finder() -> ReferenceFinder:
    """Gibt die Singleton-Instanz des ReferenceFinder zurück."""
    global _reference_finder
    if _reference_finder is None:
        _reference_finder = ReferenceFinder(get_cross_reference_engine())
    return _reference_finder


# Aliase für holo_brain.py Kompatibilität
Reference = CrossReference
create_cross_reference_engine = get_cross_reference_engine


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=== CROSS-REFERENCE ENGINE TEST ===\n")

    engine = get_cross_reference_engine()
    finder = get_reference_finder()

    print(f"Geladene Entitäten: {len(engine.entities)}")
    print()

    # Test: Suche nach Spice and Wolf
    print("[Test 1: Querverweise für 'Spice and Wolf']")
    print(finder.find("Spice and Wolf"))
    print()

    print("="*60)
    print()

    # Test: Exploration
    print("[Test 2: Tiefenanalyse 'Evangelion']")
    print(finder.explore("Evangelion"))
    print()

    print("="*60)
    print()

    # Test: Überraschung
    print("[Test 3: Überraschende Verbindung]")
    print(finder.surprise_me())
    print()

    print("="*60)
    print()

    # Test: Referenz-Web
    print("[Test 4: Referenz-Web für 'demon_slayer' (Tiefe 2)]")
    web = engine.build_reference_web("demon_slayer", depth=2)
    print(f"Knoten: {len(web['nodes'])}")
    print(f"Kanten: {len(web['edges'])}")
    for node_id, node_data in list(web['nodes'].items())[:5]:
        print(f"  - {node_data['name']} ({node_data['domain']})")
