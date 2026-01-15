"""
Holo Cognitive Enhancement Module
=================================

Erweitert Holos kognitive Fähigkeiten um:
1. Proaktive Wissensnutzung - Relevantes Wissen automatisch in Antworten einbringen
2. Transfer-Learning - Von konkreten Mustern zu abstrakten Regeln generalisieren
3. Symbolisches Reasoning - Logische Schlussfolgerungen (A→B, B→C ∴ A→C)

Autor: Claude (Integration)
Datum: 2026-01-15
"""

import logging
import json
import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# 1. PROAKTIVE WISSENSNUTZUNG
# =============================================================================

class RelevanceScorer:
    """Bewertet Relevanz von Fakten für aktuelle Konversation"""

    # Schlüsselwörter die auf bestimmte Themen hinweisen
    TOPIC_INDICATORS = {
        'technik': ['computer', 'pc', 'laptop', 'cpu', 'gpu', 'ram', 'software',
                    'hardware', 'programmieren', 'code', 'app', 'internet'],
        'gaming': ['spiel', 'game', 'zocken', 'konsole', 'playstation', 'xbox',
                   'nintendo', 'steam', 'multiplayer', 'rpg'],
        'anime': ['anime', 'manga', 'japan', 'otaku', 'kawaii', 'shounen',
                  'isekai', 'crunchyroll'],
        'musik': ['musik', 'song', 'lied', 'album', 'band', 'konzert',
                  'spotify', 'playlist'],
        'wissenschaft': ['forschung', 'studie', 'wissenschaft', 'entdeckung',
                         'experiment', 'theorie'],
        'nachrichten': ['news', 'nachricht', 'aktuell', 'heute', 'gestern',
                        'politik', 'wirtschaft'],
    }

    def __init__(self):
        self.recent_topics: List[str] = []
        self.topic_weights: Dict[str, float] = defaultdict(lambda: 0.5)

    def extract_topics(self, text: str) -> List[str]:
        """Extrahiert Themen aus Text"""
        text_lower = text.lower()
        found_topics = []

        for topic, keywords in self.TOPIC_INDICATORS.items():
            if any(kw in text_lower for kw in keywords):
                found_topics.append(topic)

        # Extrahiere auch Eigennamen (Großbuchstaben am Wortanfang)
        proper_nouns = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß]+\b', text)
        found_topics.extend([n.lower() for n in proper_nouns if len(n) > 2])

        return found_topics

    def score_fact_relevance(self, fact_content: str, fact_topic: str,
                             conversation_topics: List[str]) -> float:
        """Bewertet wie relevant ein Fakt für die aktuelle Konversation ist"""
        score = 0.0

        # Direkter Topic-Match
        if fact_topic.lower() in [t.lower() for t in conversation_topics]:
            score += 0.5

        # Keyword-Overlap
        fact_words = set(fact_content.lower().split())
        for topic in conversation_topics:
            topic_keywords = self.TOPIC_INDICATORS.get(topic, [topic])
            overlap = fact_words.intersection(set(k.lower() for k in topic_keywords))
            score += len(overlap) * 0.1

        # Aktualität (neuere Fakten sind relevanter für Nachrichten)
        if 'nachrichten' in conversation_topics or 'aktuell' in conversation_topics:
            score += 0.2

        return min(1.0, score)

    def update_topic_history(self, topics: List[str]):
        """Aktualisiert die Themen-Historie"""
        self.recent_topics = (topics + self.recent_topics)[:20]

        # Erhöhe Gewicht für häufig besprochene Themen
        for topic in topics:
            self.topic_weights[topic] = min(1.0, self.topic_weights[topic] + 0.1)


class ProactiveKnowledgeInjector:
    """
    Injiziert relevantes Wissen automatisch in den LLM-Kontext.

    VORHER: Wissen wurde nur bei expliziten Fragen genutzt
    NACHHER: Relevantes Wissen wird automatisch eingebracht

    Verbindet BEIDE Wissenssysteme:
    - web_curiosity.facts_db (WebFactsDB)
    - learning_system.knowledge_db (KnowledgeDB)
    """

    def __init__(self, web_curiosity=None, learning_system=None):
        self.web_curiosity = web_curiosity
        self.learning_system = learning_system  # NEU: holo_learning.py System
        self.relevance_scorer = RelevanceScorer()
        self.injection_history: List[str] = []  # Verhindert Wiederholungen
        self.max_facts_per_response = 5  # Erhöht von 3 auf 5
        self.min_relevance_threshold = 0.25  # Gesenkt für mehr Treffer

    def connect_web_curiosity(self, web_curiosity):
        """Verbindet mit dem WebCuriosity-System"""
        self.web_curiosity = web_curiosity
        logger.debug("[KnowledgeInjector] WebCuriosity verbunden")

    def connect_learning_system(self, learning_system):
        """Verbindet mit dem Learning-System (holo_learning.py)"""
        self.learning_system = learning_system
        logger.debug("[KnowledgeInjector] LearningSystem verbunden")

    def get_relevant_facts_for_context(self, user_message: str,
                                        conversation_history: List[str] = None
                                        ) -> List[Dict[str, Any]]:
        """
        Findet relevante Fakten für den aktuellen Konversationskontext.

        Durchsucht BEIDE Wissenssysteme:
        1. web_curiosity.facts_db (verifizierte Web-Fakten)
        2. learning_system.knowledge_db (gelernte Fakten aus RSS etc.)

        Returns:
            Liste von relevanten Fakten mit Relevanz-Score
        """
        scored_facts = []

        # Extrahiere Themen aus aktueller Nachricht und Historie
        topics = self.relevance_scorer.extract_topics(user_message)

        if conversation_history:
            for msg in conversation_history[-3:]:  # Letzte 3 Nachrichten
                topics.extend(self.relevance_scorer.extract_topics(msg))

        topics = list(set(topics))  # Deduplizieren

        # Auch die User-Nachricht selbst als Suchbegriff nutzen
        search_terms = topics + [user_message[:100]] if user_message else topics

        if not search_terms:
            return []

        # === QUELLE 1: WebCuriosity Facts ===
        if self.web_curiosity:
            try:
                # Methode 1: Verifizierte Fakten
                if hasattr(self.web_curiosity, 'facts_db'):
                    all_facts = self.web_curiosity.facts_db.get_verified_facts()
                    for fact in all_facts:
                        relevance = self.relevance_scorer.score_fact_relevance(
                            fact.content, fact.topic, topics
                        )
                        if relevance >= self.min_relevance_threshold:
                            fact_hash = hashlib.md5(fact.content.encode()).hexdigest()[:8]
                            if fact_hash not in self.injection_history[-20:]:
                                scored_facts.append({
                                    'content': fact.content,
                                    'topic': fact.topic,
                                    'trust_score': fact.trust_score,
                                    'relevance': relevance,
                                    'source': 'web_curiosity',
                                    'hash': fact_hash
                                })

                # Methode 2: Direkte Suche
                if hasattr(self.web_curiosity, 'facts_db') and hasattr(self.web_curiosity.facts_db, 'search_facts'):
                    for term in search_terms[:3]:
                        search_results = self.web_curiosity.facts_db.search_facts(term)
                        for fact in search_results[:5]:
                            fact_hash = hashlib.md5(fact.content.encode()).hexdigest()[:8]
                            if fact_hash not in self.injection_history[-20:]:
                                if not any(f['hash'] == fact_hash for f in scored_facts):
                                    scored_facts.append({
                                        'content': fact.content,
                                        'topic': getattr(fact, 'topic', 'allgemein'),
                                        'trust_score': getattr(fact, 'trust_score', 0.5),
                                        'relevance': 0.5,  # Suchergebnis = mittlere Relevanz
                                        'source': 'web_search',
                                        'hash': fact_hash
                                    })
            except Exception as e:
                logger.debug(f"WebCuriosity Fakten-Abruf: {e}")

        # === QUELLE 2: Learning System (holo_learning.py) ===
        if self.learning_system:
            try:
                # Methode 1: knowledge_db.search()
                if hasattr(self.learning_system, 'knowledge_db'):
                    kb = self.learning_system.knowledge_db
                    for term in search_terms[:3]:
                        results = kb.search(term, limit=5)
                        for fact in results:
                            fact_hash = hashlib.md5(fact.content.encode()).hexdigest()[:8]
                            if fact_hash not in self.injection_history[-20:]:
                                if not any(f['hash'] == fact_hash for f in scored_facts):
                                    scored_facts.append({
                                        'content': fact.content,
                                        'topic': getattr(fact, 'category', 'gelernt').value if hasattr(getattr(fact, 'category', None), 'value') else 'gelernt',
                                        'trust_score': getattr(fact, 'importance', 0.5),
                                        'relevance': getattr(fact, 'importance', 0.5),
                                        'source': 'learning_system',
                                        'hash': fact_hash
                                    })

                # Methode 2: Direkte Suche via search_knowledge()
                if hasattr(self.learning_system, 'search_knowledge'):
                    for term in search_terms[:2]:
                        results = self.learning_system.search_knowledge(term, limit=3)
                        for fact in results:
                            content = fact.get('content', '') or fact.get('fact', '') or str(fact)
                            if content:
                                fact_hash = hashlib.md5(content.encode()).hexdigest()[:8]
                                if fact_hash not in self.injection_history[-20:]:
                                    if not any(f['hash'] == fact_hash for f in scored_facts):
                                        scored_facts.append({
                                            'content': content,
                                            'topic': fact.get('topic', 'gelernt'),
                                            'trust_score': fact.get('importance', 0.5),
                                            'relevance': 0.4,
                                            'source': 'learning_search',
                                            'hash': fact_hash
                                        })
            except Exception as e:
                logger.debug(f"LearningSystem Fakten-Abruf: {e}")

        # Sortiere nach Relevanz und Trust
        scored_facts.sort(key=lambda x: (x['relevance'] * 0.6 + x['trust_score'] * 0.4),
                          reverse=True)

        return scored_facts[:self.max_facts_per_response]

    def format_facts_for_prompt(self, facts: List[Dict]) -> str:
        """Formatiert Fakten für den System-Prompt"""
        if not facts:
            return ""

        lines = ["\n=== RELEVANTES WISSEN (automatisch erkannt) ==="]
        for fact in facts:
            trust_indicator = "✓" if fact['trust_score'] >= 0.7 else "?"
            lines.append(f"• [{trust_indicator}] {fact['content']}")
            # Merke als verwendet
            self.injection_history.append(fact['hash'])

        lines.append("(Du kannst dieses Wissen nutzen wenn es zur Frage passt)")

        # Begrenze Historie
        self.injection_history = self.injection_history[-50:]

        return "\n".join(lines)

    def get_enhanced_prompt_context(self, user_message: str,
                                     conversation_history: List[str] = None,
                                     existing_context: str = "") -> str:
        """
        Erweitert den bestehenden Prompt-Kontext mit relevantem Wissen.

        Args:
            user_message: Die aktuelle User-Nachricht
            conversation_history: Bisherige Nachrichten
            existing_context: Bereits vorhandener Kontext

        Returns:
            Erweiterter Kontext-String
        """
        relevant_facts = self.get_relevant_facts_for_context(
            user_message, conversation_history
        )

        facts_context = self.format_facts_for_prompt(relevant_facts)

        if facts_context:
            return existing_context + "\n" + facts_context
        return existing_context


# =============================================================================
# 2. TRANSFER-LEARNING (Pattern Abstraction)
# =============================================================================

class AbstractionLevel(Enum):
    """Abstraktionsstufen für Muster"""
    CONCRETE = auto()      # Konkretes Beispiel: "mag kurze Antworten"
    CATEGORY = auto()      # Kategorie: "mag Effizienz"
    PRINCIPLE = auto()     # Prinzip: "bevorzugt Direktheit"
    META = auto()          # Meta: "ist ein praktisch denkender Mensch"


@dataclass
class AbstractPattern:
    """Ein abstrahiertes Muster"""
    id: str
    level: AbstractionLevel
    description: str
    source_patterns: List[str]  # IDs der konkreten Muster
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)
    applications: int = 0  # Wie oft wurde es angewandt?

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'level': self.level.name,
            'description': self.description,
            'source_patterns': self.source_patterns,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'applications': self.applications
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AbstractPattern':
        return cls(
            id=data['id'],
            level=AbstractionLevel[data['level']],
            description=data['description'],
            source_patterns=data['source_patterns'],
            confidence=data['confidence'],
            created_at=datetime.fromisoformat(data['created_at']),
            applications=data.get('applications', 0)
        )


class PatternAbstractor:
    """
    Abstrahiert von konkreten Mustern zu allgemeinen Prinzipien.

    Beispiel:
    - Konkret: "User mag kurze Antworten"
    - Konkret: "User mag schnelle Reaktionen"
    - Konkret: "User überspringt lange Erklärungen"
    → Abstrakt: "User bevorzugt Effizienz"
    → Meta: "User ist ein praktisch orientierter Mensch"
    """

    # Abstraktions-Regeln: Welche konkreten Muster zu welcher Abstraktion führen
    ABSTRACTION_RULES = {
        'effizienz': {
            'keywords': ['kurz', 'schnell', 'direkt', 'knapp', 'prägnant',
                         'überspringt', 'keine lange', 'sofort'],
            'category': 'Effizienz-Präferenz',
            'principle': 'bevorzugt Direktheit und Zeitersparnis',
            'meta': 'praktisch orientierte Person'
        },
        'tiefe': {
            'keywords': ['detail', 'erklär', 'warum', 'hintergrund', 'verstehen',
                         'genau', 'ausführlich', 'komplex'],
            'category': 'Tiefe-Präferenz',
            'principle': 'schätzt tiefes Verständnis',
            'meta': 'wissbegierige, analytische Person'
        },
        'kreativität': {
            'keywords': ['kreativ', 'idee', 'neu', 'anders', 'interessant',
                         'ungewöhnlich', 'fantasie', 'kunst'],
            'category': 'Kreativitäts-Präferenz',
            'principle': 'schätzt originelle Ansätze',
            'meta': 'kreativ denkende Person'
        },
        'struktur': {
            'keywords': ['ordnung', 'liste', 'plan', 'schritt', 'systematisch',
                         'organisiert', 'klar', 'übersicht'],
            'category': 'Struktur-Präferenz',
            'principle': 'bevorzugt klare Organisation',
            'meta': 'strukturiert denkende Person'
        },
        'emotion': {
            'keywords': ['fühl', 'emotion', 'herz', 'empathie', 'verständnis',
                         'einfühlsam', 'warm', 'persönlich'],
            'category': 'Emotions-Präferenz',
            'principle': 'schätzt emotionale Verbindung',
            'meta': 'emotional intelligente Person'
        },
        'humor': {
            'keywords': ['lustig', 'witz', 'spaß', 'lach', 'humor', 'ironisch',
                         'locker', 'entspannt'],
            'category': 'Humor-Präferenz',
            'principle': 'schätzt Leichtigkeit und Witz',
            'meta': 'humorvolle Person'
        }
    }

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/patterns")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.concrete_patterns: Dict[str, Dict] = {}  # ID -> Pattern-Data
        self.abstract_patterns: Dict[str, AbstractPattern] = {}
        self.pattern_links: Dict[str, List[str]] = defaultdict(list)  # concrete -> abstract

        self._load_state()

    def add_concrete_pattern(self, pattern_id: str, description: str,
                              category: str = None, strength: float = 0.5):
        """Fügt ein konkretes Muster hinzu"""
        self.concrete_patterns[pattern_id] = {
            'description': description,
            'category': category,
            'strength': strength,
            'created_at': datetime.now().isoformat()
        }

        # Versuche sofort zu abstrahieren
        self._try_abstraction(pattern_id, description)
        self._save_state()

    def _try_abstraction(self, pattern_id: str, description: str):
        """Versucht ein konkretes Muster zu abstrahieren"""
        desc_lower = description.lower()

        for abstract_key, rules in self.ABSTRACTION_RULES.items():
            # Prüfe ob Keywords matchen
            matching_keywords = [kw for kw in rules['keywords'] if kw in desc_lower]

            if len(matching_keywords) >= 1:
                # Erstelle oder update abstrakte Muster
                self._create_or_update_abstraction(
                    abstract_key, rules, pattern_id, len(matching_keywords)
                )

    def _create_or_update_abstraction(self, key: str, rules: Dict,
                                       source_pattern: str, match_strength: int):
        """Erstellt oder aktualisiert ein abstraktes Muster"""
        # Category-Level Abstraktion
        cat_id = f"cat_{key}"
        if cat_id not in self.abstract_patterns:
            self.abstract_patterns[cat_id] = AbstractPattern(
                id=cat_id,
                level=AbstractionLevel.CATEGORY,
                description=rules['category'],
                source_patterns=[source_pattern],
                confidence=0.3 + (match_strength * 0.1)
            )
        else:
            pattern = self.abstract_patterns[cat_id]
            if source_pattern not in pattern.source_patterns:
                pattern.source_patterns.append(source_pattern)
                pattern.confidence = min(0.95, pattern.confidence + 0.1)

        self.pattern_links[source_pattern].append(cat_id)

        # Principle-Level (braucht mindestens 2 konkrete Muster)
        cat_pattern = self.abstract_patterns[cat_id]
        if len(cat_pattern.source_patterns) >= 2:
            prin_id = f"prin_{key}"
            if prin_id not in self.abstract_patterns:
                self.abstract_patterns[prin_id] = AbstractPattern(
                    id=prin_id,
                    level=AbstractionLevel.PRINCIPLE,
                    description=f"User {rules['principle']}",
                    source_patterns=[cat_id],
                    confidence=0.5
                )
            else:
                self.abstract_patterns[prin_id].confidence = min(
                    0.95, self.abstract_patterns[prin_id].confidence + 0.05
                )

        # Meta-Level (braucht mindestens 3 konkrete Muster)
        if len(cat_pattern.source_patterns) >= 3:
            meta_id = f"meta_{key}"
            if meta_id not in self.abstract_patterns:
                self.abstract_patterns[meta_id] = AbstractPattern(
                    id=meta_id,
                    level=AbstractionLevel.META,
                    description=f"User ist eine {rules['meta']}",
                    source_patterns=[f"prin_{key}"],
                    confidence=0.4
                )
            else:
                self.abstract_patterns[meta_id].confidence = min(
                    0.95, self.abstract_patterns[meta_id].confidence + 0.03
                )

    def get_abstractions_for_prompt(self) -> str:
        """Formatiert abstrakte Muster für den System-Prompt"""
        if not self.abstract_patterns:
            return ""

        # Sortiere nach Confidence und Level
        sorted_patterns = sorted(
            self.abstract_patterns.values(),
            key=lambda p: (p.level.value, p.confidence),
            reverse=True
        )

        lines = ["\n=== USER-MUSTER (abstrahiert) ==="]

        # Nur die besten pro Level zeigen
        shown_levels = set()
        for pattern in sorted_patterns:
            if pattern.confidence < 0.4:
                continue
            if pattern.level in shown_levels:
                continue

            level_emoji = {
                AbstractionLevel.META: "🎯",
                AbstractionLevel.PRINCIPLE: "📐",
                AbstractionLevel.CATEGORY: "📁"
            }.get(pattern.level, "•")

            lines.append(f"{level_emoji} {pattern.description} (Konfidenz: {pattern.confidence:.0%})")
            shown_levels.add(pattern.level)

        if len(lines) == 1:
            return ""

        return "\n".join(lines)

    def record_pattern_application(self, pattern_id: str, success: bool):
        """Zeichnet auf wenn ein abstraktes Muster angewandt wurde"""
        if pattern_id in self.abstract_patterns:
            pattern = self.abstract_patterns[pattern_id]
            pattern.applications += 1
            if success:
                pattern.confidence = min(0.98, pattern.confidence + 0.02)
            else:
                pattern.confidence = max(0.1, pattern.confidence - 0.05)
            self._save_state()

    def _save_state(self):
        """Speichert den aktuellen Zustand"""
        try:
            state = {
                'concrete_patterns': self.concrete_patterns,
                'abstract_patterns': {
                    k: v.to_dict() for k, v in self.abstract_patterns.items()
                },
                'pattern_links': dict(self.pattern_links)
            }
            with open(self.data_dir / "patterns.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Patterns nicht speichern: {e}")

    def _load_state(self):
        """Lädt den gespeicherten Zustand"""
        try:
            path = self.data_dir / "patterns.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.concrete_patterns = state.get('concrete_patterns', {})
                self.abstract_patterns = {
                    k: AbstractPattern.from_dict(v)
                    for k, v in state.get('abstract_patterns', {}).items()
                }
                self.pattern_links = defaultdict(list, state.get('pattern_links', {}))
        except Exception as e:
            logger.debug(f"Konnte Patterns nicht laden: {e}")


# =============================================================================
# 3. SYMBOLISCHES REASONING
# =============================================================================

@dataclass
class SymbolicRule:
    """Eine symbolische Regel: A → B"""
    antecedent: str  # A (Bedingung)
    consequent: str  # B (Folgerung)
    confidence: float  # Wie sicher ist die Regel?
    source: str  # Woher stammt die Regel?
    created_at: datetime = field(default_factory=datetime.now)
    applications: int = 0
    successes: int = 0

    @property
    def success_rate(self) -> float:
        if self.applications == 0:
            return 0.5
        return self.successes / self.applications

    def to_dict(self) -> Dict:
        return {
            'antecedent': self.antecedent,
            'consequent': self.consequent,
            'confidence': self.confidence,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'applications': self.applications,
            'successes': self.successes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SymbolicRule':
        return cls(
            antecedent=data['antecedent'],
            consequent=data['consequent'],
            confidence=data['confidence'],
            source=data['source'],
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            applications=data.get('applications', 0),
            successes=data.get('successes', 0)
        )


@dataclass
class Inference:
    """Eine abgeleitete Schlussfolgerung"""
    conclusion: str
    reasoning_chain: List[Tuple[str, str]]  # [(A, B), (B, C), ...]
    confidence: float
    inference_type: str  # 'direct', 'transitive', 'abductive'


class SymbolicReasoner:
    """
    Symbolisches Reasoning-System.

    Kann:
    - Regeln lernen aus Beobachtungen
    - Transitive Schlüsse ziehen (A→B, B→C ∴ A→C)
    - Abduktives Reasoning (B ist wahr, A→B, also vielleicht A)

    Beispiel:
    - Regel 1: "User fragt nach PC" → "User interessiert sich für Technik"
    - Regel 2: "User interessiert sich für Technik" → "Könnte Gaming-News mögen"
    - Schluss: "User fragt nach PC" → "Könnte Gaming-News mögen"
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/reasoning")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.rules: Dict[str, SymbolicRule] = {}  # ID -> Rule
        self.rule_index: Dict[str, List[str]] = defaultdict(list)  # antecedent -> rule_ids
        self.reverse_index: Dict[str, List[str]] = defaultdict(list)  # consequent -> rule_ids

        self._init_base_rules()
        self._load_state()

    def _init_base_rules(self):
        """Initialisiert Basis-Regeln"""
        base_rules = [
            # Technik-Kette
            ("fragt_nach_pc", "interesse_technik", 0.8, "base"),
            ("interesse_technik", "mag_tech_news", 0.6, "base"),
            ("interesse_technik", "versteht_fachbegriffe", 0.7, "base"),

            # Gaming-Kette
            ("fragt_nach_spielen", "interesse_gaming", 0.9, "base"),
            ("interesse_gaming", "mag_gaming_news", 0.7, "base"),
            ("interesse_gaming", "kennt_gaming_begriffe", 0.6, "base"),

            # Emotionale Kette
            ("teilt_probleme", "sucht_unterstützung", 0.8, "base"),
            ("sucht_unterstützung", "braucht_empathie", 0.7, "base"),
            ("braucht_empathie", "kurze_ratschläge_vermeiden", 0.6, "base"),

            # Lern-Kette
            ("stellt_warum_fragen", "will_verstehen", 0.85, "base"),
            ("will_verstehen", "mag_erklärungen", 0.8, "base"),
            ("mag_erklärungen", "geduld_für_details", 0.7, "base"),

            # Effizienz-Kette
            ("sagt_zu_lang", "bevorzugt_kürze", 0.9, "base"),
            ("bevorzugt_kürze", "effizienz_wichtig", 0.8, "base"),
            ("effizienz_wichtig", "keine_umschweife", 0.75, "base"),
        ]

        for ante, cons, conf, source in base_rules:
            self.add_rule(ante, cons, conf, source)

    def add_rule(self, antecedent: str, consequent: str,
                  confidence: float, source: str) -> str:
        """Fügt eine neue Regel hinzu"""
        rule_id = f"{antecedent}_to_{consequent}"

        if rule_id in self.rules:
            # Update existierende Regel
            self.rules[rule_id].confidence = max(
                self.rules[rule_id].confidence,
                confidence
            )
        else:
            rule = SymbolicRule(
                antecedent=antecedent,
                consequent=consequent,
                confidence=confidence,
                source=source
            )
            self.rules[rule_id] = rule
            self.rule_index[antecedent].append(rule_id)
            self.reverse_index[consequent].append(rule_id)

        self._save_state()
        return rule_id

    def learn_rule_from_observation(self, observation: str, outcome: str,
                                     confidence: float = 0.5):
        """Lernt eine neue Regel aus einer Beobachtung"""
        # Normalisiere
        observation_key = self._normalize_to_key(observation)
        outcome_key = self._normalize_to_key(outcome)

        self.add_rule(observation_key, outcome_key, confidence, "learned")
        logger.info(f"[SymbolicReasoner] Neue Regel gelernt: {observation_key} → {outcome_key}")

    def _normalize_to_key(self, text: str) -> str:
        """Normalisiert Text zu einem Schlüssel"""
        # Entferne Sonderzeichen, lowercase, ersetze Leerzeichen
        key = re.sub(r'[^a-zäöüß0-9\s]', '', text.lower())
        key = '_'.join(key.split())
        return key[:50]  # Begrenze Länge

    def infer_direct(self, antecedent: str) -> List[Inference]:
        """Direkte Schlussfolgerung: Was folgt aus A?"""
        results = []
        ant_key = self._normalize_to_key(antecedent)

        for rule_id in self.rule_index.get(ant_key, []):
            rule = self.rules[rule_id]
            results.append(Inference(
                conclusion=rule.consequent,
                reasoning_chain=[(rule.antecedent, rule.consequent)],
                confidence=rule.confidence,
                inference_type='direct'
            ))

        return results

    def infer_transitive(self, antecedent: str, max_depth: int = 3) -> List[Inference]:
        """
        Transitive Schlussfolgerung: A→B, B→C ∴ A→C

        Args:
            antecedent: Startpunkt
            max_depth: Maximale Kettenlänge

        Returns:
            Liste von Schlussfolgerungen mit Reasoning-Chain
        """
        results = []
        ant_key = self._normalize_to_key(antecedent)

        # BFS durch den Regelgraphen
        visited = {ant_key}
        queue = [(ant_key, [], 1.0, 0)]  # (current, chain, confidence, depth)

        while queue:
            current, chain, conf, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            for rule_id in self.rule_index.get(current, []):
                rule = self.rules[rule_id]
                next_node = rule.consequent

                if next_node in visited:
                    continue

                visited.add(next_node)
                new_chain = chain + [(rule.antecedent, rule.consequent)]
                new_conf = conf * rule.confidence

                # Füge als Ergebnis hinzu wenn Konfidenz hoch genug
                if new_conf >= 0.2:
                    results.append(Inference(
                        conclusion=next_node,
                        reasoning_chain=new_chain,
                        confidence=new_conf,
                        inference_type='transitive' if len(new_chain) > 1 else 'direct'
                    ))

                # Weiter suchen
                queue.append((next_node, new_chain, new_conf, depth + 1))

        return sorted(results, key=lambda x: x.confidence, reverse=True)

    def infer_abductive(self, consequent: str) -> List[Inference]:
        """
        Abduktives Reasoning: B ist wahr, A→B existiert, also vielleicht A

        Beispiel: User mag Gaming-News → vielleicht interessiert er sich für Gaming
        """
        results = []
        cons_key = self._normalize_to_key(consequent)

        for rule_id in self.reverse_index.get(cons_key, []):
            rule = self.rules[rule_id]
            # Abduktion ist unsicherer als Deduktion
            abductive_conf = rule.confidence * 0.6

            results.append(Inference(
                conclusion=f"möglicherweise: {rule.antecedent}",
                reasoning_chain=[(rule.consequent, rule.antecedent)],
                confidence=abductive_conf,
                inference_type='abductive'
            ))

        return results

    def reason_about(self, statement: str) -> Dict[str, Any]:
        """
        Führt vollständiges Reasoning über eine Aussage durch.

        Returns:
            Dict mit direkten, transitiven und abduktiven Schlüssen
        """
        return {
            'direct': self.infer_direct(statement),
            'transitive': self.infer_transitive(statement),
            'abductive': self.infer_abductive(statement),
            'statement': statement
        }

    def get_reasoning_for_prompt(self, context_statements: List[str]) -> str:
        """
        Generiert Reasoning-Kontext für den System-Prompt.

        Args:
            context_statements: Aktuelle Kontext-Aussagen (z.B. User-Interessen)

        Returns:
            Formatierter String für den Prompt
        """
        if not context_statements:
            return ""

        all_inferences = []

        for statement in context_statements[:5]:  # Max 5 Statements
            inferences = self.infer_transitive(statement, max_depth=2)
            all_inferences.extend(inferences[:3])  # Max 3 pro Statement

        if not all_inferences:
            return ""

        # Dedupliziere und sortiere
        seen = set()
        unique_inferences = []
        for inf in sorted(all_inferences, key=lambda x: x.confidence, reverse=True):
            if inf.conclusion not in seen and inf.confidence >= 0.3:
                seen.add(inf.conclusion)
                unique_inferences.append(inf)

        if not unique_inferences:
            return ""

        lines = ["\n=== LOGISCHE SCHLÜSSE ==="]
        for inf in unique_inferences[:5]:
            chain_str = " → ".join([f"{a}" for a, b in inf.reasoning_chain] + [inf.conclusion])
            lines.append(f"• {chain_str} ({inf.confidence:.0%})")

        return "\n".join(lines)

    def record_inference_outcome(self, inference: Inference, success: bool):
        """Zeichnet auf ob eine Schlussfolgerung erfolgreich war"""
        # Update alle Regeln in der Kette
        for ante, cons in inference.reasoning_chain:
            rule_id = f"{ante}_to_{cons}"
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                rule.applications += 1
                if success:
                    rule.successes += 1
                    rule.confidence = min(0.95, rule.confidence + 0.02)
                else:
                    rule.confidence = max(0.1, rule.confidence - 0.05)

        self._save_state()

    def _save_state(self):
        """Speichert Regeln"""
        try:
            state = {
                'rules': {k: v.to_dict() for k, v in self.rules.items()}
            }
            with open(self.data_dir / "rules.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Regeln nicht speichern: {e}")

    def _load_state(self):
        """Lädt Regeln"""
        try:
            path = self.data_dir / "rules.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                for rule_id, rule_data in state.get('rules', {}).items():
                    rule = SymbolicRule.from_dict(rule_data)
                    self.rules[rule_id] = rule
                    self.rule_index[rule.antecedent].append(rule_id)
                    self.reverse_index[rule.consequent].append(rule_id)
        except Exception as e:
            logger.debug(f"Konnte Regeln nicht laden: {e}")


# =============================================================================
# 4. INTEGRIERTES COGNITIVE ENHANCEMENT SYSTEM
# =============================================================================

class CognitiveEnhancementSystem:
    """
    Integriert alle kognitiven Erweiterungen in ein System.

    Verwendung:
        ces = CognitiveEnhancementSystem()
        ces.connect_modules(web_curiosity=holo.web_curiosity)

        # Bei jeder Nachricht:
        enhanced_context = ces.enhance_context(
            user_message="Ich brauche einen neuen PC",
            conversation_history=[...],
            existing_context="..."
        )
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/cognitive_enhancement")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Sub-Systeme initialisieren
        self.knowledge_injector = ProactiveKnowledgeInjector()
        self.pattern_abstractor = PatternAbstractor(self.data_dir / "patterns")
        self.symbolic_reasoner = SymbolicReasoner(self.data_dir / "reasoning")

        logger.info("[CognitiveEnhancement] System initialisiert")

    def connect_modules(self, web_curiosity=None, preferences=None, learning_system=None):
        """
        Verbindet mit anderen Holo-Modulen.

        Args:
            web_curiosity: HoloWebCuriosity für verifizierte Web-Fakten
            preferences: HoloPreferences für User-Präferenzen
            learning_system: HoloLearningSystem für gelernte Fakten (RSS etc.)
        """
        # Verbinde WebCuriosity (web_facts_db)
        if web_curiosity:
            self.knowledge_injector.connect_web_curiosity(web_curiosity)
            logger.info("[CognitiveEnhancement] WebCuriosity verbunden")

        # Verbinde Learning System (knowledge_db)
        if learning_system:
            self.knowledge_injector.connect_learning_system(learning_system)
            logger.info("[CognitiveEnhancement] LearningSystem verbunden")

        # Importiere existierende Präferenzen als Patterns
        if preferences and hasattr(preferences, 'preferences'):
            pattern_count = 0
            for item, pref in preferences.preferences.items():
                if hasattr(pref, 'strength') and abs(pref.strength) > 0.3:
                    desc = f"{'mag' if pref.strength > 0 else 'mag nicht'} {item}"
                    self.pattern_abstractor.add_concrete_pattern(
                        pattern_id=f"pref_{item}",
                        description=desc,
                        category=getattr(pref, 'category', 'general'),
                        strength=abs(pref.strength)
                    )
                    pattern_count += 1
            if pattern_count > 0:
                logger.info(f"[CognitiveEnhancement] {pattern_count} Präferenzen als Patterns importiert")

    def enhance_context(self, user_message: str,
                        conversation_history: List[str] = None,
                        existing_context: str = "",
                        user_interests: List[str] = None) -> str:
        """
        Erweitert den Kontext mit allen kognitiven Erweiterungen.

        Args:
            user_message: Aktuelle User-Nachricht
            conversation_history: Bisherige Nachrichten
            existing_context: Bereits vorhandener Kontext
            user_interests: Bekannte User-Interessen für Reasoning

        Returns:
            Erweiterter Kontext-String
        """
        enhanced = existing_context

        # 1. Proaktive Wissensnutzung
        knowledge_context = self.knowledge_injector.get_enhanced_prompt_context(
            user_message, conversation_history, ""
        )
        if knowledge_context:
            enhanced += knowledge_context

        # 2. Abstrahierte Muster
        pattern_context = self.pattern_abstractor.get_abstractions_for_prompt()
        if pattern_context:
            enhanced += pattern_context

        # 3. Symbolisches Reasoning
        if user_interests:
            reasoning_context = self.symbolic_reasoner.get_reasoning_for_prompt(
                user_interests
            )
            if reasoning_context:
                enhanced += reasoning_context

        return enhanced

    def learn_from_interaction(self, user_message: str, holo_response: str,
                               was_successful: bool = True):
        """
        Lernt aus einer Interaktion.

        Args:
            user_message: Was der User sagte
            holo_response: Was Holo antwortete
            was_successful: War die Interaktion erfolgreich?
        """
        # Extrahiere Muster aus der Interaktion
        if "zu lang" in user_message.lower() or "kürzer" in user_message.lower():
            self.pattern_abstractor.add_concrete_pattern(
                f"feedback_{datetime.now().timestamp()}",
                "User bevorzugt kürzere Antworten",
                "dialog_preference",
                0.7
            )
            self.symbolic_reasoner.learn_rule_from_observation(
                "sagt_zu_lang", "bevorzugt_kürze", 0.9
            )

        if "mehr detail" in user_message.lower() or "erklär" in user_message.lower():
            self.pattern_abstractor.add_concrete_pattern(
                f"feedback_{datetime.now().timestamp()}",
                "User möchte mehr Details",
                "dialog_preference",
                0.7
            )
            self.symbolic_reasoner.learn_rule_from_observation(
                "fragt_nach_details", "will_verstehen", 0.85
            )

    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über das System zurück"""
        return {
            'concrete_patterns': len(self.pattern_abstractor.concrete_patterns),
            'abstract_patterns': len(self.pattern_abstractor.abstract_patterns),
            'symbolic_rules': len(self.symbolic_reasoner.rules),
            'knowledge_injections': len(self.knowledge_injector.injection_history)
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_cognitive_enhancement(data_dir: Path = None) -> CognitiveEnhancementSystem:
    """Factory-Funktion für CognitiveEnhancementSystem"""
    return CognitiveEnhancementSystem(data_dir)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test das System
    ces = CognitiveEnhancementSystem()

    # Test Symbolic Reasoning
    print("\n=== SYMBOLIC REASONING TEST ===")
    results = ces.symbolic_reasoner.reason_about("fragt nach pc")
    print(f"Direkte Schlüsse: {[i.conclusion for i in results['direct']]}")
    print(f"Transitive Schlüsse: {[(i.conclusion, i.confidence) for i in results['transitive'][:3]]}")

    # Test Pattern Abstraction
    print("\n=== PATTERN ABSTRACTION TEST ===")
    ces.pattern_abstractor.add_concrete_pattern("test1", "User mag kurze Antworten", "dialog")
    ces.pattern_abstractor.add_concrete_pattern("test2", "User überspringt lange Texte", "dialog")
    ces.pattern_abstractor.add_concrete_pattern("test3", "User will schnelle Antworten", "dialog")
    print(ces.pattern_abstractor.get_abstractions_for_prompt())

    # Test Context Enhancement
    print("\n=== CONTEXT ENHANCEMENT TEST ===")
    enhanced = ces.enhance_context(
        "Ich brauche einen neuen Gaming-PC",
        user_interests=["interesse_gaming", "interesse_technik"]
    )
    print(enhanced)

    print("\n=== STATS ===")
    print(ces.get_stats())
