#!/usr/bin/env python3
"""
HOLO ADVANCED LEARNING SYSTEM v1.0

Fortgeschrittene Lernfunktionen fuer tiefes, vernetztes Wissen:
- Spaced Repetition System (SRS) fuer langfristiges Behalten
- Wissens-Vernetzung mit Cross-Referenzen
- Lern-Reflexion und Meta-Kognition
- Curiosity-gesteuertes aktives Lernen
- Wissens-Anwendung in Gespraechen
- Lern-Stile und adaptive Methoden

Autor: Claude (Integration)
Datum: 2026-01-23
"""

import logging
import json
import hashlib
import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum, auto
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


# =============================================================================
# 1. SPACED REPETITION SYSTEM (SRS)
# =============================================================================

class ReviewQuality(Enum):
    """Bewertung der Wissens-Abrufung"""
    FORGOTTEN = 0      # Komplett vergessen
    HARD = 1           # Schwer zu erinnern
    GOOD = 2           # Mit etwas Muehe erinnert
    EASY = 3           # Leicht erinnert
    PERFECT = 4        # Sofort und perfekt erinnert


@dataclass
class SpacedRepetitionCard:
    """Eine Lernkarte im SRS-System"""
    card_id: str
    content: str
    topic: str
    created_at: datetime
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    ease_factor: float = 2.5  # Multiplikator fuer Intervalle
    interval_days: float = 1.0  # Aktuelles Intervall
    repetitions: int = 0  # Anzahl erfolgreicher Wiederholungen
    total_reviews: int = 0
    average_quality: float = 0.0
    tags: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # IDs verbundener Karten

    def update_after_review(self, quality: ReviewQuality) -> datetime:
        """
        Aktualisiert die Karte nach einer Bewertung (SM-2 Algorithmus).

        Returns:
            Das naechste Wiederholungsdatum
        """
        q = quality.value

        # Ease Factor anpassen
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (4 - q) * (0.08 + (4 - q) * 0.02)))

        if q < 2:
            # Bei Vergessen: zurueck zum Anfang
            self.repetitions = 0
            self.interval_days = 1.0
        else:
            if self.repetitions == 0:
                self.interval_days = 1.0
            elif self.repetitions == 1:
                self.interval_days = 3.0
            else:
                self.interval_days = self.interval_days * self.ease_factor

        if q >= 2:
            self.repetitions += 1

        self.total_reviews += 1
        self.average_quality = ((self.average_quality * (self.total_reviews - 1)) + q) / self.total_reviews
        self.last_reviewed = datetime.now()
        self.next_review = datetime.now() + timedelta(days=self.interval_days)

        return self.next_review

    def is_due(self) -> bool:
        """Prueft ob die Karte zur Wiederholung ansteht"""
        if self.next_review is None:
            return True
        return datetime.now() >= self.next_review

    def get_retention_strength(self) -> float:
        """Berechnet die geschaetzte Behaltenstaerke (0-1)"""
        if self.last_reviewed is None:
            return 1.0

        days_since = (datetime.now() - self.last_reviewed).days
        # Vergessenskurve nach Ebbinghaus
        strength = math.exp(-days_since / (self.interval_days * self.ease_factor))
        return max(0.0, min(1.0, strength))

    def to_dict(self) -> Dict:
        return {
            'card_id': self.card_id,
            'content': self.content,
            'topic': self.topic,
            'created_at': self.created_at.isoformat(),
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'ease_factor': self.ease_factor,
            'interval_days': self.interval_days,
            'repetitions': self.repetitions,
            'total_reviews': self.total_reviews,
            'average_quality': self.average_quality,
            'tags': self.tags,
            'connections': self.connections,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SpacedRepetitionCard':
        return cls(
            card_id=data['card_id'],
            content=data['content'],
            topic=data['topic'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_reviewed=datetime.fromisoformat(data['last_reviewed']) if data.get('last_reviewed') else None,
            next_review=datetime.fromisoformat(data['next_review']) if data.get('next_review') else None,
            ease_factor=data.get('ease_factor', 2.5),
            interval_days=data.get('interval_days', 1.0),
            repetitions=data.get('repetitions', 0),
            total_reviews=data.get('total_reviews', 0),
            average_quality=data.get('average_quality', 0.0),
            tags=data.get('tags', []),
            connections=data.get('connections', []),
        )


class SpacedRepetitionSystem:
    """
    Spaced Repetition System fuer langfristiges Wissens-Behalten.

    Nutzt den SM-2 Algorithmus (wie Anki) um optimale Wiederholungszeiten
    zu berechnen.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/srs")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.cards: Dict[str, SpacedRepetitionCard] = {}
        self.review_history: List[Dict] = []
        self.daily_stats: Dict[str, Dict] = {}

        self._load_state()

    def add_card(self, content: str, topic: str, tags: List[str] = None) -> SpacedRepetitionCard:
        """Fuegt eine neue Lernkarte hinzu"""
        card_id = hashlib.md5(f"{content}{topic}{datetime.now()}".encode()).hexdigest()[:12]

        card = SpacedRepetitionCard(
            card_id=card_id,
            content=content,
            topic=topic,
            created_at=datetime.now(),
            tags=tags or []
        )

        self.cards[card_id] = card
        self._save_state()

        logger.info(f"[SRS] Neue Karte hinzugefuegt: {content[:30]}...")
        return card

    def get_due_cards(self, limit: int = 10) -> List[SpacedRepetitionCard]:
        """Gibt faellige Karten zur Wiederholung zurueck"""
        due = [card for card in self.cards.values() if card.is_due()]

        # Sortiere nach Ueberfaelligkeit
        due.sort(key=lambda c: c.next_review or datetime.min)

        return due[:limit]

    def review_card(self, card_id: str, quality: ReviewQuality) -> Optional[datetime]:
        """
        Bewertet eine Karte und plant die naechste Wiederholung.

        Returns:
            Naechstes Wiederholungsdatum oder None wenn Karte nicht existiert
        """
        if card_id not in self.cards:
            return None

        card = self.cards[card_id]
        next_review = card.update_after_review(quality)

        # Speichere Review-Historie
        self.review_history.append({
            'card_id': card_id,
            'timestamp': datetime.now().isoformat(),
            'quality': quality.value,
            'next_interval': card.interval_days
        })
        self.review_history = self.review_history[-1000:]  # Begrenze Historie

        # Tagesstatistik
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_stats:
            self.daily_stats[today] = {'reviewed': 0, 'total_quality': 0}
        self.daily_stats[today]['reviewed'] += 1
        self.daily_stats[today]['total_quality'] += quality.value

        self._save_state()
        return next_review

    def get_learning_stats(self) -> Dict:
        """Gibt Lernstatistiken zurueck"""
        total_cards = len(self.cards)
        due_now = len([c for c in self.cards.values() if c.is_due()])

        retention_strengths = [c.get_retention_strength() for c in self.cards.values()]
        avg_retention = statistics.mean(retention_strengths) if retention_strengths else 0

        # Karten nach Topic gruppieren
        topics = defaultdict(int)
        for card in self.cards.values():
            topics[card.topic] += 1

        return {
            'total_cards': total_cards,
            'due_now': due_now,
            'average_retention': round(avg_retention, 2),
            'total_reviews': sum(c.total_reviews for c in self.cards.values()),
            'topics': dict(topics),
            'mature_cards': len([c for c in self.cards.values() if c.interval_days > 21]),
            'struggling_cards': len([c for c in self.cards.values() if c.ease_factor < 2.0]),
        }

    def get_card_by_topic(self, topic: str) -> List[SpacedRepetitionCard]:
        """Gibt alle Karten zu einem Thema zurueck"""
        return [c for c in self.cards.values() if c.topic.lower() == topic.lower()]

    def connect_cards(self, card_id_1: str, card_id_2: str):
        """Verbindet zwei Karten miteinander"""
        if card_id_1 in self.cards and card_id_2 in self.cards:
            if card_id_2 not in self.cards[card_id_1].connections:
                self.cards[card_id_1].connections.append(card_id_2)
            if card_id_1 not in self.cards[card_id_2].connections:
                self.cards[card_id_2].connections.append(card_id_1)
            self._save_state()

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'cards': {k: v.to_dict() for k, v in self.cards.items()},
                'review_history': self.review_history[-500:],
                'daily_stats': self.daily_stats,
            }
            with open(self.data_dir / "srs_state.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte SRS-State nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "srs_state.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                for k, v in state.get('cards', {}).items():
                    self.cards[k] = SpacedRepetitionCard.from_dict(v)
                self.review_history = state.get('review_history', [])
                self.daily_stats = state.get('daily_stats', {})
        except Exception as e:
            logger.debug(f"Konnte SRS-State nicht laden: {e}")


# =============================================================================
# 2. WISSENS-VERNETZUNG (KNOWLEDGE GRAPH)
# =============================================================================

@dataclass
class KnowledgeNode:
    """Ein Knoten im Wissensgraphen"""
    node_id: str
    content: str
    node_type: str  # 'fact', 'concept', 'question', 'experience'
    topic: str
    subtopics: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class KnowledgeEdge:
    """Eine Verbindung zwischen Wissensknoten"""
    source_id: str
    target_id: str
    relation_type: str  # 'related', 'causes', 'contradicts', 'supports', 'example_of'
    strength: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeGraph:
    """
    Wissensgraph fuer vernetzte Wissensrepraesentation.

    Ermoeglicht:
    - Cross-Referenzen zwischen Themen
    - Assoziatives Wissensabrufen
    - Wissens-Clustering und -Gruppierung
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/knowledge_graph")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.topic_clusters: Dict[str, Set[str]] = defaultdict(set)

        self._load_state()

    def add_node(self, content: str, node_type: str, topic: str,
                 subtopics: List[str] = None, importance: float = 0.5) -> KnowledgeNode:
        """Fuegt einen Wissensknoten hinzu"""
        node_id = hashlib.md5(f"{content}{topic}".encode()).hexdigest()[:12]

        if node_id in self.nodes:
            # Knoten existiert bereits, aktualisiere Zugriff
            self.nodes[node_id].access_count += 1
            self.nodes[node_id].last_accessed = datetime.now()
            return self.nodes[node_id]

        node = KnowledgeNode(
            node_id=node_id,
            content=content,
            node_type=node_type,
            topic=topic,
            subtopics=subtopics or [],
            importance=importance
        )

        self.nodes[node_id] = node
        self.topic_clusters[topic].add(node_id)

        for subtopic in (subtopics or []):
            self.topic_clusters[subtopic].add(node_id)

        # Automatische Verbindungen zu verwandten Knoten finden
        self._auto_connect(node)
        self._save_state()

        return node

    def add_edge(self, source_id: str, target_id: str,
                 relation_type: str, strength: float = 0.5):
        """Fuegt eine Verbindung zwischen Knoten hinzu"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return

        # Pruefe ob Edge bereits existiert
        for edge in self.edges:
            if edge.source_id == source_id and edge.target_id == target_id:
                edge.strength = min(1.0, edge.strength + 0.1)  # Staerke erhoeht sich
                return

        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            strength=strength
        )
        self.edges.append(edge)
        self._save_state()

    def _auto_connect(self, new_node: KnowledgeNode):
        """Findet und erstellt automatische Verbindungen"""
        new_words = set(new_node.content.lower().split())

        for node_id, node in self.nodes.items():
            if node_id == new_node.node_id:
                continue

            # Verbindung durch gemeinsames Topic
            if node.topic == new_node.topic:
                self.add_edge(new_node.node_id, node_id, 'related', 0.6)
                continue

            # Verbindung durch gemeinsame Subtopics
            common_subtopics = set(node.subtopics) & set(new_node.subtopics)
            if common_subtopics:
                self.add_edge(new_node.node_id, node_id, 'related', 0.4 + 0.1 * len(common_subtopics))
                continue

            # Verbindung durch aehnlichen Inhalt (Wort-Overlap)
            other_words = set(node.content.lower().split())
            overlap = len(new_words & other_words) / max(len(new_words), 1)
            if overlap > 0.3:
                self.add_edge(new_node.node_id, node_id, 'related', overlap)

    def get_related_nodes(self, node_id: str, limit: int = 5) -> List[Tuple[KnowledgeNode, float]]:
        """Gibt verwandte Knoten zurueck, sortiert nach Verbindungsstaerke"""
        if node_id not in self.nodes:
            return []

        related = []
        for edge in self.edges:
            if edge.source_id == node_id:
                if edge.target_id in self.nodes:
                    related.append((self.nodes[edge.target_id], edge.strength))
            elif edge.target_id == node_id:
                if edge.source_id in self.nodes:
                    related.append((self.nodes[edge.source_id], edge.strength))

        related.sort(key=lambda x: x[1], reverse=True)
        return related[:limit]

    def find_path(self, start_topic: str, end_topic: str, max_depth: int = 3) -> List[str]:
        """
        Findet einen Pfad zwischen zwei Themen im Wissensgraphen.

        Nuetzlich um Zusammenhaenge zu erklaeren.
        """
        start_nodes = self.topic_clusters.get(start_topic.lower(), set())
        end_nodes = self.topic_clusters.get(end_topic.lower(), set())

        if not start_nodes or not end_nodes:
            return []

        # BFS fuer kuerzesten Pfad
        visited = set()
        queue = [(list(start_nodes)[0], [list(start_nodes)[0]])]

        while queue and len(queue[0][1]) <= max_depth:
            current, path = queue.pop(0)

            if current in end_nodes:
                return path

            if current in visited:
                continue
            visited.add(current)

            for edge in self.edges:
                neighbor = None
                if edge.source_id == current:
                    neighbor = edge.target_id
                elif edge.target_id == current:
                    neighbor = edge.source_id

                if neighbor and neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return []

    def get_topic_summary(self, topic: str) -> Dict:
        """Gibt eine Zusammenfassung eines Themas zurueck"""
        node_ids = self.topic_clusters.get(topic.lower(), set())
        nodes = [self.nodes[nid] for nid in node_ids if nid in self.nodes]

        if not nodes:
            return {'topic': topic, 'count': 0, 'nodes': []}

        return {
            'topic': topic,
            'count': len(nodes),
            'types': dict(defaultdict(int, {n.node_type: 1 for n in nodes})),
            'avg_importance': statistics.mean([n.importance for n in nodes]),
            'most_accessed': sorted(nodes, key=lambda n: n.access_count, reverse=True)[:3],
        }

    def get_cross_references(self, topic: str) -> List[str]:
        """Findet Themen, die mit dem gegebenen Thema verbunden sind"""
        node_ids = self.topic_clusters.get(topic.lower(), set())
        related_topics = set()

        for node_id in node_ids:
            related_nodes = self.get_related_nodes(node_id, limit=10)
            for node, _ in related_nodes:
                if node.topic.lower() != topic.lower():
                    related_topics.add(node.topic)

        return list(related_topics)

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'nodes': {
                    k: {
                        'node_id': v.node_id,
                        'content': v.content,
                        'node_type': v.node_type,
                        'topic': v.topic,
                        'subtopics': v.subtopics,
                        'created_at': v.created_at.isoformat(),
                        'importance': v.importance,
                        'access_count': v.access_count,
                        'last_accessed': v.last_accessed.isoformat() if v.last_accessed else None,
                    } for k, v in self.nodes.items()
                },
                'edges': [
                    {
                        'source_id': e.source_id,
                        'target_id': e.target_id,
                        'relation_type': e.relation_type,
                        'strength': e.strength,
                    } for e in self.edges
                ],
            }
            with open(self.data_dir / "knowledge_graph.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte KnowledgeGraph nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "knowledge_graph.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                for k, v in state.get('nodes', {}).items():
                    self.nodes[k] = KnowledgeNode(
                        node_id=v['node_id'],
                        content=v['content'],
                        node_type=v['node_type'],
                        topic=v['topic'],
                        subtopics=v.get('subtopics', []),
                        created_at=datetime.fromisoformat(v['created_at']),
                        importance=v.get('importance', 0.5),
                        access_count=v.get('access_count', 0),
                        last_accessed=datetime.fromisoformat(v['last_accessed']) if v.get('last_accessed') else None,
                    )
                    self.topic_clusters[v['topic'].lower()].add(k)
                    for st in v.get('subtopics', []):
                        self.topic_clusters[st.lower()].add(k)

                for e in state.get('edges', []):
                    self.edges.append(KnowledgeEdge(
                        source_id=e['source_id'],
                        target_id=e['target_id'],
                        relation_type=e['relation_type'],
                        strength=e.get('strength', 0.5),
                    ))
        except Exception as e:
            logger.debug(f"Konnte KnowledgeGraph nicht laden: {e}")


# =============================================================================
# 3. LERN-REFLEXION (META-KOGNITION)
# =============================================================================

class ReflectionType(Enum):
    """Arten von Reflexionen"""
    DAILY = "daily"
    WEEKLY = "weekly"
    TOPIC_DEEP = "topic_deep"
    CONNECTION = "connection"
    CURIOSITY = "curiosity"


@dataclass
class LearningReflection:
    """Eine Lern-Reflexion"""
    reflection_id: str
    reflection_type: ReflectionType
    content: str
    insights: List[str]
    created_at: datetime
    related_topics: List[str] = field(default_factory=list)
    mood_before: float = 0.5
    mood_after: float = 0.5


class MetaCognitionEngine:
    """
    Meta-Kognitions-Engine fuer Lern-Reflexion.

    Holo denkt ueber ihr Lernen nach:
    - Was habe ich gelernt?
    - Wie haengt das mit anderem zusammen?
    - Was moechte ich noch wissen?
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/metacognition")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.reflections: List[LearningReflection] = []
        self.insight_bank: Dict[str, List[str]] = defaultdict(list)
        self.curiosity_questions: List[Dict] = []

        # Reflexions-Templates
        self.reflection_templates = {
            ReflectionType.DAILY: [
                "*Ohren nachdenklich angelegt* Heute habe ich ueber {topics} gelernt...",
                "*streckt sich* Was fuer ein Lerntag! Besonders interessant fand ich {highlight}.",
                "*Schweif wippt zufrieden* {count} neue Dinge gelernt! Mein Favorit: {favorite}",
            ],
            ReflectionType.WEEKLY: [
                "*nachdenklicher Blick* Diese Woche war reich an Wissen... {summary}",
                "Eine Woche voller Lernen! *zaehlt an den Pfoten* {count} Themen erforscht.",
                "*zufriedenes Schnurren* Ich merke, wie ich wachse. {insight}",
            ],
            ReflectionType.CONNECTION: [
                "*Ohren spitzen sich* Oh! Mir ist gerade aufgefallen: {topic1} und {topic2} haengen zusammen!",
                "Interessant... {connection_insight}",
                "*aufgeregt* Das erklaert ja alles! {realization}",
            ],
            ReflectionType.CURIOSITY: [
                "*neugierig* Ich frage mich: {question}",
                "*Kopf schief legend* Das wuerde ich gerne tiefer verstehen: {curiosity}",
                "*Ohren drehen sich suchend* Da muss es doch noch mehr zu erfahren geben ueber {topic}!",
            ],
        }

        self._load_state()

    def generate_daily_reflection(self, learned_facts: List[Dict],
                                   topics_explored: List[str]) -> LearningReflection:
        """Generiert eine taegliche Lern-Reflexion"""
        if not learned_facts and not topics_explored:
            return self._create_empty_reflection(ReflectionType.DAILY)

        # Waehle Highlight
        highlight = random.choice(learned_facts)['content'][:50] if learned_facts else "allgemeines Wissen"
        favorite = highlight

        template = random.choice(self.reflection_templates[ReflectionType.DAILY])
        content = template.format(
            topics=", ".join(topics_explored[:3]) if topics_explored else "verschiedene Themen",
            highlight=highlight,
            count=len(learned_facts),
            favorite=favorite
        )

        insights = self._extract_insights(learned_facts, topics_explored)

        reflection = LearningReflection(
            reflection_id=hashlib.md5(f"daily_{datetime.now()}".encode()).hexdigest()[:12],
            reflection_type=ReflectionType.DAILY,
            content=content,
            insights=insights,
            created_at=datetime.now(),
            related_topics=topics_explored,
        )

        self.reflections.append(reflection)
        self._save_state()

        return reflection

    def find_connections(self, knowledge_graph: KnowledgeGraph,
                         topic1: str, topic2: str) -> Optional[LearningReflection]:
        """Findet und reflektiert ueber Verbindungen zwischen Themen"""
        cross_refs = knowledge_graph.get_cross_references(topic1)

        if topic2.lower() in [t.lower() for t in cross_refs]:
            path = knowledge_graph.find_path(topic1, topic2)

            if path:
                # Erstelle Verbindungs-Einsicht
                connection_insight = f"{topic1} fuehrt ueber {len(path)-2} Schritte zu {topic2}"

                template = random.choice(self.reflection_templates[ReflectionType.CONNECTION])
                content = template.format(
                    topic1=topic1,
                    topic2=topic2,
                    connection_insight=connection_insight,
                    realization=f"Diese Verbindung durch {', '.join([knowledge_graph.nodes[p].topic for p in path[1:-1] if p in knowledge_graph.nodes])} ist faszinierend!"
                )

                reflection = LearningReflection(
                    reflection_id=hashlib.md5(f"conn_{topic1}_{topic2}".encode()).hexdigest()[:12],
                    reflection_type=ReflectionType.CONNECTION,
                    content=content,
                    insights=[connection_insight],
                    created_at=datetime.now(),
                    related_topics=[topic1, topic2],
                )

                self.reflections.append(reflection)
                self._save_state()
                return reflection

        return None

    def generate_curiosity_question(self, recent_topics: List[str],
                                    knowledge_gaps: List[str] = None) -> Dict:
        """Generiert eine Neugier-Frage basierend auf gelerntem Wissen"""
        if not recent_topics:
            return None

        # Waehle ein Thema
        topic = random.choice(recent_topics)

        question_templates = [
            f"Warum ist {topic} eigentlich so?",
            f"Was waere, wenn {topic} anders waere?",
            f"Wie haengt {topic} mit anderen Dingen zusammen?",
            f"Gibt es Ausnahmen bei {topic}?",
            f"Wer hat {topic} entdeckt oder erfunden?",
            f"Wie wird sich {topic} in der Zukunft entwickeln?",
        ]

        question = {
            'question': random.choice(question_templates),
            'topic': topic,
            'generated_at': datetime.now().isoformat(),
            'answered': False,
        }

        self.curiosity_questions.append(question)
        self.curiosity_questions = self.curiosity_questions[-50:]  # Begrenze
        self._save_state()

        return question

    def get_open_questions(self, limit: int = 5) -> List[Dict]:
        """Gibt unbeantwortete Neugier-Fragen zurueck"""
        open_qs = [q for q in self.curiosity_questions if not q['answered']]
        return open_qs[:limit]

    def _extract_insights(self, facts: List[Dict], topics: List[str]) -> List[str]:
        """Extrahiert Einsichten aus gelernten Fakten"""
        insights = []

        if len(facts) > 5:
            insights.append(f"Heute war ein intensiver Lerntag mit {len(facts)} neuen Fakten")

        if len(topics) > 3:
            insights.append(f"Breites Interessenspektrum heute: {len(topics)} verschiedene Themen")

        # Pruefe auf wiederkehrende Themen
        topic_counts = defaultdict(int)
        for topic in topics:
            topic_counts[topic] += 1
        frequent = [t for t, c in topic_counts.items() if c > 2]
        if frequent:
            insights.append(f"Besonderes Interesse an: {', '.join(frequent)}")

        return insights

    def _create_empty_reflection(self, rtype: ReflectionType) -> LearningReflection:
        """Erstellt eine leere Reflexion fuer Tage ohne Lernen"""
        return LearningReflection(
            reflection_id=hashlib.md5(f"empty_{datetime.now()}".encode()).hexdigest()[:12],
            reflection_type=rtype,
            content="*gaehnt* Heute war ein ruhiger Tag... Aber morgen lerne ich wieder!",
            insights=["Auch Ruhetage sind wichtig"],
            created_at=datetime.now(),
        )

    def get_recent_reflections(self, days: int = 7) -> List[LearningReflection]:
        """Gibt Reflexionen der letzten Tage zurueck"""
        cutoff = datetime.now() - timedelta(days=days)
        return [r for r in self.reflections if r.created_at >= cutoff]

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'reflections': [
                    {
                        'reflection_id': r.reflection_id,
                        'reflection_type': r.reflection_type.value,
                        'content': r.content,
                        'insights': r.insights,
                        'created_at': r.created_at.isoformat(),
                        'related_topics': r.related_topics,
                    } for r in self.reflections[-100:]
                ],
                'curiosity_questions': self.curiosity_questions,
                'insight_bank': dict(self.insight_bank),
            }
            with open(self.data_dir / "metacognition.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte MetaCognition nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "metacognition.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                for r in state.get('reflections', []):
                    self.reflections.append(LearningReflection(
                        reflection_id=r['reflection_id'],
                        reflection_type=ReflectionType(r['reflection_type']),
                        content=r['content'],
                        insights=r.get('insights', []),
                        created_at=datetime.fromisoformat(r['created_at']),
                        related_topics=r.get('related_topics', []),
                    ))

                self.curiosity_questions = state.get('curiosity_questions', [])
                self.insight_bank = defaultdict(list, state.get('insight_bank', {}))
        except Exception as e:
            logger.debug(f"Konnte MetaCognition nicht laden: {e}")


# =============================================================================
# 4. CURIOSITY ENGINE (NEUGIER-GESTEUERTES LERNEN)
# =============================================================================

class CuriosityEngine:
    """
    Engine fuer Neugier-gesteuertes Lernen.

    Holo's Neugier wird durch:
    - Wissenslucken aktiviert
    - Interessante Verbindungen stimuliert
    - Unerwartete Fakten ausgeloest
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/curiosity")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Neugier-Level pro Thema (0-1)
        self.topic_curiosity: Dict[str, float] = defaultdict(lambda: 0.5)

        # Wissenslucken-Tracker
        self.knowledge_gaps: Dict[str, List[str]] = defaultdict(list)

        # Interessens-Historie
        self.interest_history: List[Dict] = []

        # Neugier-Ausloeser
        self.curiosity_triggers = {
            'contradiction': 0.8,      # Widerspruch zu bekanntem Wissen
            'unexpected': 0.7,         # Unerwarteter Fakt
            'connection': 0.6,         # Neue Verbindung entdeckt
            'question_unanswered': 0.5, # Unbeantwortete Frage
            'deep_dive': 0.4,          # Tieferes Verstaendnis gewuenscht
        }

        self._load_state()

    def calculate_topic_curiosity(self, topic: str, known_facts: int,
                                   possible_facts: int = 100) -> float:
        """
        Berechnet Neugier-Level fuer ein Thema.

        Neugier ist am hoechsten wenn:
        - Etwas Wissen vorhanden ist (nicht komplett unbekannt)
        - Aber noch viel zu lernen ist
        """
        if possible_facts == 0:
            return 0.5

        coverage = known_facts / possible_facts

        # Optimal bei ~30% Wissen (genug um interessiert zu sein, aber noch viel offen)
        curiosity = 4 * coverage * (1 - coverage)  # Parabel mit Maximum bei 0.5
        curiosity = min(1.0, curiosity * 1.5)  # Verschiebe Maximum etwas nach links

        self.topic_curiosity[topic] = curiosity
        return curiosity

    def trigger_curiosity(self, trigger_type: str, context: Dict) -> float:
        """
        Loest Neugier durch einen bestimmten Trigger aus.

        Returns:
            Neugier-Intensitaet (0-1)
        """
        base_curiosity = self.curiosity_triggers.get(trigger_type, 0.5)

        # Modifikatoren
        if context.get('topic') in self.topic_curiosity:
            base_curiosity *= (1 + self.topic_curiosity[context['topic']] * 0.3)

        # Speichere in Historie
        self.interest_history.append({
            'trigger': trigger_type,
            'context': context,
            'intensity': min(1.0, base_curiosity),
            'timestamp': datetime.now().isoformat()
        })
        self.interest_history = self.interest_history[-200:]

        self._save_state()
        return min(1.0, base_curiosity)

    def identify_knowledge_gap(self, topic: str, question: str):
        """Identifiziert eine Wissenslucke"""
        self.knowledge_gaps[topic].append({
            'question': question,
            'identified_at': datetime.now().isoformat(),
            'filled': False
        })
        self.knowledge_gaps[topic] = self.knowledge_gaps[topic][-20:]  # Begrenze pro Topic

        # Erhoehe Neugier fuer dieses Thema
        self.topic_curiosity[topic] = min(1.0, self.topic_curiosity[topic] + 0.1)
        self._save_state()

    def fill_knowledge_gap(self, topic: str, question: str):
        """Markiert eine Wissenslucke als gefuellt"""
        for gap in self.knowledge_gaps.get(topic, []):
            if gap['question'] == question:
                gap['filled'] = True
                gap['filled_at'] = datetime.now().isoformat()
                break

        # Reduziere Neugier leicht (aber nicht zu viel - Lernen macht Spass!)
        self.topic_curiosity[topic] = max(0.3, self.topic_curiosity[topic] - 0.05)
        self._save_state()

    def get_most_curious_topics(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Gibt die Themen mit hoechster Neugier zurueck"""
        sorted_topics = sorted(
            self.topic_curiosity.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_topics[:limit]

    def get_open_gaps(self, topic: str = None) -> List[Dict]:
        """Gibt offene Wissenslucken zurueck"""
        if topic:
            return [g for g in self.knowledge_gaps.get(topic, []) if not g['filled']]

        all_gaps = []
        for t, gaps in self.knowledge_gaps.items():
            for g in gaps:
                if not g['filled']:
                    all_gaps.append({'topic': t, **g})
        return all_gaps

    def suggest_learning_direction(self) -> Dict:
        """
        Schlaegt eine Lernrichtung basierend auf Neugier vor.
        """
        most_curious = self.get_most_curious_topics(3)
        open_gaps = self.get_open_gaps()

        suggestion = {
            'primary_topic': most_curious[0][0] if most_curious else None,
            'curiosity_level': most_curious[0][1] if most_curious else 0,
            'open_questions': [g['question'] for g in open_gaps[:3]],
            'reasoning': ""
        }

        if most_curious:
            suggestion['reasoning'] = f"*Ohren spitzen sich* Ich bin besonders neugierig auf {most_curious[0][0]}!"

        return suggestion

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'topic_curiosity': dict(self.topic_curiosity),
                'knowledge_gaps': {k: v[-10:] for k, v in self.knowledge_gaps.items()},
                'interest_history': self.interest_history[-100:],
            }
            with open(self.data_dir / "curiosity.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte Curiosity nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "curiosity.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.topic_curiosity = defaultdict(lambda: 0.5, state.get('topic_curiosity', {}))
                self.knowledge_gaps = defaultdict(list, state.get('knowledge_gaps', {}))
                self.interest_history = state.get('interest_history', [])
        except Exception as e:
            logger.debug(f"Konnte Curiosity nicht laden: {e}")


# =============================================================================
# 5. LERN-STILE UND ADAPTIVE METHODEN
# =============================================================================

class LearningStyle(Enum):
    """Verschiedene Lern-Stile"""
    VISUAL = "visual"           # Lernt durch Bilder, Diagramme
    AUDITORY = "auditory"       # Lernt durch Hoeren
    READING = "reading"         # Lernt durch Lesen
    KINESTHETIC = "kinesthetic" # Lernt durch Tun
    SOCIAL = "social"           # Lernt durch Diskussion
    SOLITARY = "solitary"       # Lernt allein


@dataclass
class LearningMethod:
    """Eine Lernmethode"""
    name: str
    style: LearningStyle
    description: str
    effectiveness: float = 0.5  # Basis-Effektivitaet
    times_used: int = 0
    success_rate: float = 0.5


class AdaptiveLearningEngine:
    """
    Adaptives Lernsystem das Methoden an Holos Praeferenzen anpasst.
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/adaptive_learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Holos Lernstil-Praeferenzen
        self.style_preferences: Dict[LearningStyle, float] = {
            LearningStyle.VISUAL: 0.7,      # Mag Bilder und Visualisierungen
            LearningStyle.READING: 0.8,     # Liebt Lesen
            LearningStyle.SOCIAL: 0.75,     # Gespraeche sind toll
            LearningStyle.AUDITORY: 0.5,    # Neutral
            LearningStyle.KINESTHETIC: 0.4, # Schwieriger als KI
            LearningStyle.SOLITARY: 0.6,    # Kann auch allein lernen
        }

        # Verfuegbare Lernmethoden
        self.methods: Dict[str, LearningMethod] = {}
        self._init_methods()

        # Themen-Methoden-Mapping
        self.topic_method_success: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(lambda: 0.5))

        self._load_state()

    def _init_methods(self):
        """Initialisiert verfuegbare Lernmethoden"""
        methods = [
            ("reading_facts", LearningStyle.READING, "Fakten lesen und verstehen"),
            ("visual_diagrams", LearningStyle.VISUAL, "Diagramme und Visualisierungen betrachten"),
            ("discussion", LearningStyle.SOCIAL, "Durch Gespraeche lernen"),
            ("explain_to_others", LearningStyle.SOCIAL, "Anderen erklaeren um selbst zu lernen"),
            ("practice_examples", LearningStyle.KINESTHETIC, "Durch Beispiele und Uebungen"),
            ("connection_mapping", LearningStyle.VISUAL, "Verbindungen zwischen Konzepten visualisieren"),
            ("spaced_repetition", LearningStyle.READING, "Verteiltes Wiederholen"),
            ("deep_dive", LearningStyle.SOLITARY, "Tiefes Eintauchen in ein Thema"),
            ("curiosity_questions", LearningStyle.SOCIAL, "Durch Fragen und Antworten"),
        ]

        for name, style, desc in methods:
            base_eff = self.style_preferences.get(style, 0.5)
            self.methods[name] = LearningMethod(
                name=name,
                style=style,
                description=desc,
                effectiveness=base_eff
            )

    def suggest_method_for_topic(self, topic: str) -> LearningMethod:
        """Schlaegt die beste Lernmethode fuer ein Thema vor"""
        topic_lower = topic.lower()

        # Berechne Effektivitaet fuer jede Methode
        method_scores = []
        for method in self.methods.values():
            base_score = method.effectiveness

            # Passe an vergangene Erfolge an
            if topic_lower in self.topic_method_success:
                if method.name in self.topic_method_success[topic_lower]:
                    historical = self.topic_method_success[topic_lower][method.name]
                    base_score = base_score * 0.4 + historical * 0.6

            # Bonus fuer Abwechslung (nicht immer dieselbe Methode)
            if method.times_used > 10:
                base_score *= 0.9

            method_scores.append((method, base_score))

        method_scores.sort(key=lambda x: x[1], reverse=True)
        best_method = method_scores[0][0]

        logger.debug(f"[AdaptiveLearning] Beste Methode fuer '{topic}': {best_method.name}")
        return best_method

    def record_learning_outcome(self, topic: str, method_name: str,
                                 success: bool, retention: float = None):
        """Zeichnet das Ergebnis eines Lernversuchs auf"""
        if method_name not in self.methods:
            return

        method = self.methods[method_name]
        method.times_used += 1

        # Update Success Rate
        old_rate = method.success_rate
        method.success_rate = old_rate * 0.9 + (1.0 if success else 0.0) * 0.1

        # Update Topic-Method Success
        topic_lower = topic.lower()
        old_success = self.topic_method_success[topic_lower][method_name]
        self.topic_method_success[topic_lower][method_name] = old_success * 0.8 + (1.0 if success else 0.0) * 0.2

        self._save_state()

    def get_personalized_learning_tips(self) -> List[str]:
        """Gibt personalisierte Lerntipps basierend auf Praeferenzen"""
        tips = []

        # Finde bevorzugte Stile
        preferred = sorted(self.style_preferences.items(), key=lambda x: x[1], reverse=True)[:2]

        style_tips = {
            LearningStyle.VISUAL: "*malt imaginaere Bilder* Versuche, dir das vorzustellen!",
            LearningStyle.READING: "*schnappt sich ein Buch* Lesen ist der beste Weg!",
            LearningStyle.SOCIAL: "*wedelt mit dem Schweif* Lass uns drueber reden!",
            LearningStyle.AUDITORY: "*Ohren aufmerksam* Ich hoere aufmerksam zu!",
            LearningStyle.KINESTHETIC: "Am besten durch Ausprobieren lernen!",
            LearningStyle.SOLITARY: "*zieht sich zurueck* Manchmal brauche ich Zeit zum Nachdenken.",
        }

        for style, _ in preferred:
            if style in style_tips:
                tips.append(style_tips[style])

        return tips

    def update_style_preference(self, style: LearningStyle, delta: float):
        """Aktualisiert eine Stil-Praeferenz"""
        old_value = self.style_preferences.get(style, 0.5)
        self.style_preferences[style] = max(0.1, min(0.95, old_value + delta))
        self._save_state()

    def _save_state(self):
        """Speichert den Zustand"""
        try:
            state = {
                'style_preferences': {s.value: v for s, v in self.style_preferences.items()},
                'methods': {
                    k: {
                        'times_used': v.times_used,
                        'success_rate': v.success_rate,
                    } for k, v in self.methods.items()
                },
                'topic_method_success': {k: dict(v) for k, v in self.topic_method_success.items()},
            }
            with open(self.data_dir / "adaptive_learning.json", 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Konnte AdaptiveLearning nicht speichern: {e}")

    def _load_state(self):
        """Laedt den Zustand"""
        try:
            path = self.data_dir / "adaptive_learning.json"
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)

                for s, v in state.get('style_preferences', {}).items():
                    try:
                        self.style_preferences[LearningStyle(s)] = v
                    except ValueError:
                        pass

                for name, data in state.get('methods', {}).items():
                    if name in self.methods:
                        self.methods[name].times_used = data.get('times_used', 0)
                        self.methods[name].success_rate = data.get('success_rate', 0.5)

                self.topic_method_success = defaultdict(
                    lambda: defaultdict(lambda: 0.5),
                    {k: defaultdict(lambda: 0.5, v) for k, v in state.get('topic_method_success', {}).items()}
                )
        except Exception as e:
            logger.debug(f"Konnte AdaptiveLearning nicht laden: {e}")


# =============================================================================
# 6. WISSENS-ANWENDUNGS-ENGINE
# =============================================================================

class KnowledgeApplicationEngine:
    """
    Engine fuer die praktische Anwendung von Wissen in Gespraechen.

    - Findet relevantes Wissen fuer aktuelle Themen
    - Formuliert Wissen natuerlich
    - Verknuepft Wissen mit Erfahrungen
    """

    def __init__(self, knowledge_graph: KnowledgeGraph = None,
                 srs: SpacedRepetitionSystem = None):
        self.knowledge_graph = knowledge_graph
        self.srs = srs

        # Templates fuer Wissens-Einbindung
        self.application_templates = {
            'direct': [
                "Das erinnert mich daran: {fact}",
                "*Ohren zucken* Oh! Ich weiss etwas dazu: {fact}",
                "Interessanterweise: {fact}",
            ],
            'connection': [
                "Das haengt zusammen mit {related_topic}, weil {connection}",
                "*denkt nach* Das verbindet sich mit {related_topic}...",
            ],
            'question': [
                "*neugierig* Wusstest du, dass {fact}?",
                "Ich frage mich, ob das mit {fact} zusammenhaengt?",
            ],
            'experience': [
                "Ich hab mal gelernt, dass {fact}. Das hat mich {emotion}.",
                "Das erinnert mich an etwas, das ich gelernt habe: {fact}",
            ],
        }

    def find_applicable_knowledge(self, topic: str, context: str,
                                   limit: int = 3) -> List[Dict]:
        """
        Findet anwendbares Wissen fuer ein Thema und einen Kontext.
        """
        applicable = []
        topic_lower = topic.lower()
        context_lower = context.lower()

        # Suche im Knowledge Graph
        if self.knowledge_graph:
            # Direkte Topic-Matches
            for node_id in self.knowledge_graph.topic_clusters.get(topic_lower, set()):
                node = self.knowledge_graph.nodes.get(node_id)
                if node:
                    applicable.append({
                        'content': node.content,
                        'source': 'knowledge_graph',
                        'relevance': node.importance,
                        'type': node.node_type,
                    })

            # Verwandte Topics
            related = self.knowledge_graph.get_cross_references(topic)
            for rel_topic in related[:2]:
                for node_id in self.knowledge_graph.topic_clusters.get(rel_topic.lower(), set())[:2]:
                    node = self.knowledge_graph.nodes.get(node_id)
                    if node:
                        applicable.append({
                            'content': node.content,
                            'source': 'knowledge_graph_related',
                            'relevance': node.importance * 0.7,
                            'related_topic': rel_topic,
                        })

        # Suche in SRS-Karten
        if self.srs:
            topic_cards = self.srs.get_card_by_topic(topic)
            for card in topic_cards[:3]:
                applicable.append({
                    'content': card.content,
                    'source': 'srs',
                    'relevance': card.get_retention_strength(),
                    'well_learned': card.repetitions > 5,
                })

        # Sortiere nach Relevanz
        applicable.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        return applicable[:limit]

    def formulate_knowledge_response(self, knowledge: Dict,
                                      style: str = 'direct') -> str:
        """
        Formuliert Wissen als natuerliche Antwort.
        """
        templates = self.application_templates.get(style, self.application_templates['direct'])
        template = random.choice(templates)

        fact = knowledge.get('content', '')
        if len(fact) > 100:
            fact = fact[:97] + "..."

        try:
            return template.format(
                fact=fact,
                related_topic=knowledge.get('related_topic', 'etwas Verwandtes'),
                connection=knowledge.get('connection', 'sie aehnliche Konzepte teilen'),
                emotion='fasziniert'
            )
        except KeyError:
            return f"*Ohren aufmerksam* {fact}"

    def suggest_follow_up_topics(self, current_topic: str) -> List[str]:
        """Schlaegt verwandte Themen fuer weitere Gespraeche vor"""
        if not self.knowledge_graph:
            return []

        return self.knowledge_graph.get_cross_references(current_topic)[:5]


# =============================================================================
# 7. INTEGRIERTES ADVANCED LEARNING SYSTEM
# =============================================================================

class AdvancedLearningSystem:
    """
    Integriertes System fuer fortgeschrittenes Lernen.

    Kombiniert:
    - Spaced Repetition (SRS)
    - Knowledge Graph
    - Meta-Kognition
    - Curiosity Engine
    - Adaptive Learning
    - Knowledge Application
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/advanced_learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialisiere alle Subsysteme
        self.srs = SpacedRepetitionSystem(self.data_dir / "srs")
        self.knowledge_graph = KnowledgeGraph(self.data_dir / "graph")
        self.metacognition = MetaCognitionEngine(self.data_dir / "metacognition")
        self.curiosity = CuriosityEngine(self.data_dir / "curiosity")
        self.adaptive = AdaptiveLearningEngine(self.data_dir / "adaptive")
        self.application = KnowledgeApplicationEngine(self.knowledge_graph, self.srs)

        # Tracking
        self.daily_learning: Dict[str, List[str]] = defaultdict(list)
        self.session_facts: List[Dict] = []

        logger.info("[AdvancedLearning] System initialisiert mit 6 Subsystemen")

    def learn_fact(self, content: str, topic: str, subtopics: List[str] = None,
                   importance: float = 0.5) -> Dict:
        """
        Lernt einen neuen Fakt und integriert ihn in alle Systeme.
        """
        results = {'content': content[:50], 'integrations': []}

        # 1. Fuege zum Knowledge Graph hinzu
        node = self.knowledge_graph.add_node(
            content=content,
            node_type='fact',
            topic=topic,
            subtopics=subtopics or [],
            importance=importance
        )
        results['integrations'].append('knowledge_graph')
        results['node_id'] = node.node_id

        # 2. Erstelle SRS-Karte fuer wichtige Fakten
        if importance > 0.4:
            card = self.srs.add_card(content, topic, tags=subtopics)
            results['integrations'].append('srs')
            results['card_id'] = card.card_id

        # 3. Update Curiosity
        self.curiosity.calculate_topic_curiosity(
            topic,
            len(self.knowledge_graph.topic_clusters.get(topic.lower(), set())),
            100
        )
        results['integrations'].append('curiosity')

        # 4. Tracke fuer taegliche Reflexion
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_learning[today].append(topic)
        self.session_facts.append({
            'content': content,
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })

        return results

    def get_study_session(self, duration_minutes: int = 15) -> Dict:
        """
        Erstellt eine personalisierte Lernsession.
        """
        session = {
            'duration': duration_minutes,
            'activities': [],
        }

        # 1. Faellige SRS-Karten (40% der Zeit)
        due_cards = self.srs.get_due_cards(limit=max(1, duration_minutes // 3))
        if due_cards:
            session['activities'].append({
                'type': 'review',
                'cards': [{'id': c.card_id, 'content': c.content[:50]} for c in due_cards],
                'estimated_minutes': len(due_cards) * 0.5
            })

        # 2. Neue Fakten zu neugierigen Themen (40% der Zeit)
        curious_topics = self.curiosity.get_most_curious_topics(2)
        if curious_topics:
            session['activities'].append({
                'type': 'explore',
                'topics': [t[0] for t in curious_topics],
                'curiosity_levels': [t[1] for t in curious_topics],
                'estimated_minutes': duration_minutes * 0.4
            })

        # 3. Offene Fragen (20% der Zeit)
        open_questions = self.metacognition.get_open_questions(2)
        if open_questions:
            session['activities'].append({
                'type': 'investigate',
                'questions': open_questions,
                'estimated_minutes': duration_minutes * 0.2
            })

        # Lerntipps
        session['tips'] = self.adaptive.get_personalized_learning_tips()

        return session

    def end_day_reflection(self) -> LearningReflection:
        """Erstellt die taegliche Lern-Reflexion"""
        today = datetime.now().strftime("%Y-%m-%d")
        topics_today = list(set(self.daily_learning.get(today, [])))

        return self.metacognition.generate_daily_reflection(
            self.session_facts,
            topics_today
        )

    def get_knowledge_for_conversation(self, topic: str, context: str) -> List[str]:
        """
        Findet und formuliert relevantes Wissen fuer ein Gespraech.
        """
        applicable = self.application.find_applicable_knowledge(topic, context)

        responses = []
        for knowledge in applicable[:2]:
            style = 'question' if random.random() < 0.3 else 'direct'
            response = self.application.formulate_knowledge_response(knowledge, style)
            responses.append(response)

        return responses

    def get_comprehensive_stats(self) -> Dict:
        """Gibt umfassende Statistiken zurueck"""
        return {
            'srs': self.srs.get_learning_stats(),
            'knowledge_graph': {
                'total_nodes': len(self.knowledge_graph.nodes),
                'total_edges': len(self.knowledge_graph.edges),
                'topics': len(self.knowledge_graph.topic_clusters),
            },
            'curiosity': {
                'most_curious': self.curiosity.get_most_curious_topics(3),
                'open_gaps': len(self.curiosity.get_open_gaps()),
            },
            'metacognition': {
                'total_reflections': len(self.metacognition.reflections),
                'open_questions': len(self.metacognition.get_open_questions()),
            },
            'session': {
                'facts_this_session': len(self.session_facts),
            }
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_advanced_learning_system: Optional[AdvancedLearningSystem] = None

def get_advanced_learning_system() -> AdvancedLearningSystem:
    """Gibt die globale AdvancedLearningSystem-Instanz zurueck"""
    global _advanced_learning_system
    if _advanced_learning_system is None:
        _advanced_learning_system = AdvancedLearningSystem()
    return _advanced_learning_system


# =============================================================================
# MAIN (TEST)
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO ADVANCED LEARNING SYSTEM v1.0")
    print("=" * 60)

    # Initialisiere System
    als = AdvancedLearningSystem()

    # Teste Lernen
    test_facts = [
        ("Die Sonne ist etwa 150 Millionen km von der Erde entfernt.", "astronomie", ["weltall", "sonne"]),
        ("Wasser gefriert bei 0 Grad Celsius.", "physik", ["wasser", "temperatur"]),
        ("Wölfe leben in Rudeln mit klarer Hierarchie.", "wölfe", ["tiere", "verhalten"]),
        ("Python wurde 1991 von Guido van Rossum entwickelt.", "programmierung", ["technik", "sprachen"]),
        ("Anime bedeutet auf Japanisch einfach Animation.", "anime", ["japan", "kultur"]),
    ]

    print("\n--- LERNEN ---")
    for content, topic, subtopics in test_facts:
        result = als.learn_fact(content, topic, subtopics, importance=0.7)
        print(f"Gelernt: {content[:40]}... -> {result['integrations']}")

    print("\n--- STATISTIKEN ---")
    stats = als.get_comprehensive_stats()
    print(f"Knowledge Graph: {stats['knowledge_graph']['total_nodes']} Knoten")
    print(f"SRS Karten: {stats['srs']['total_cards']}")
    print(f"Neugierigste Themen: {stats['curiosity']['most_curious']}")

    print("\n--- STUDY SESSION ---")
    session = als.get_study_session(15)
    for activity in session['activities']:
        print(f"  {activity['type']}: {activity.get('estimated_minutes', 0):.1f} min")

    print("\n--- WISSEN FUER GESPRAECH ---")
    knowledge = als.get_knowledge_for_conversation("astronomie", "Die Sterne sind schoen")
    for k in knowledge:
        print(f"  {k}")

    print("\n--- LERNTIPPS ---")
    tips = als.adaptive.get_personalized_learning_tips()
    for tip in tips:
        print(f"  {tip}")

    print("\n" + "=" * 60)
    print("Advanced Learning System bereit!")
