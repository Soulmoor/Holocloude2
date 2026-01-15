#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloMedia Integration v1.0 - Medien-Integration und Wissensmanagement

FEATURES:
- Medien-Tagebuch: Was Holo gelesen/gesehen hat speichern
- Empfehlungen: "Das koennte dir gefallen" basierend auf Analyse
- Emotionale Verbindung: Gelesenes mit Holos Stimmung verknuepfen
- Wissens-Graph: Verbindungen zwischen Texten/Bildern erstellen

Author: Kira & Claude
Version: 1.0
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path

logger = logging.getLogger("HoloMediaIntegration")


# =============================================================================
# ENUMS UND DATACLASSES
# =============================================================================

class MediaType(Enum):
    """Medien-Typen"""
    TEXT = "text"
    BOOK = "buch"
    ARTICLE = "artikel"
    IMAGE = "bild"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "dokument"
    WEBSITE = "website"


class EmotionalTag(Enum):
    """Emotionale Tags fuer Medien"""
    INSPIRING = "inspirierend"
    COMFORTING = "troestlich"
    EXCITING = "aufregend"
    THOUGHT_PROVOKING = "nachdenklich"
    NOSTALGIC = "nostalgisch"
    RELAXING = "entspannend"
    MOTIVATING = "motivierend"
    DISTURBING = "verstoerend"
    EDUCATIONAL = "lehrreich"
    FUN = "lustig"


class RelationType(Enum):
    """Beziehungstypen im Wissens-Graph"""
    SIMILAR_TOPIC = "aehnliches_thema"
    SAME_AUTHOR = "gleicher_autor"
    REFERENCES = "referenziert"
    CONTRADICTS = "widerspricht"
    EXTENDS = "erweitert"
    INSPIRED_BY = "inspiriert_von"
    RELATED_MOOD = "aehnliche_stimmung"
    SAME_GENRE = "gleiches_genre"
    SEQUEL = "fortsetzung"
    PREQUEL = "vorgeschichte"


@dataclass
class JournalEntry:
    """Ein Eintrag im Medien-Tagebuch"""
    entry_id: str
    media_type: MediaType
    title: str
    source: Optional[str]  # URL, Dateipfad, etc.

    # Zeitstempel
    consumed_at: str
    duration_minutes: Optional[float]  # Wie lange konsumiert

    # Holos Zustand waehrend des Konsums
    mood_before: float  # 0-1
    mood_after: float  # 0-1
    energy_before: float  # 0-1
    energy_after: float  # 0-1

    # Bewertung und Reaktion
    rating: float  # 0-5 Sterne
    emotional_tags: List[EmotionalTag]
    keywords: List[str]
    notes: str  # Holos Notizen

    # Analyse-Ergebnisse (optional)
    sentiment: Optional[float]
    complexity: Optional[float]
    topics: List[str]

    # Meta
    revisit_count: int = 0
    last_revisited: Optional[str] = None


@dataclass
class EmotionalConnection:
    """Emotionale Verbindung zu einem Medium"""
    connection_id: str
    media_id: str  # Referenz zum JournalEntry
    media_title: str

    # Emotionale Staerke
    bond_strength: float  # 0-1, wie stark die Verbindung

    # Assoziationen
    positive_memories: List[str]
    negative_memories: List[str]
    associated_feelings: Dict[str, float]  # Emotion -> Staerke

    # Zeitlich
    first_exposure: str
    last_exposure: str
    exposure_count: int

    # Trigger
    trigger_words: List[str]  # Woerter die an dieses Medium erinnern
    trigger_topics: List[str]


@dataclass
class KnowledgeNode:
    """Ein Knoten im Wissens-Graph"""
    node_id: str
    node_type: str  # "media", "topic", "person", "concept"
    name: str
    description: str
    attributes: Dict[str, Any]

    # Beziehungen
    relations: List[Dict[str, Any]]  # {target_id, relation_type, strength}

    # Meta
    created_at: str
    confidence: float  # 0-1


@dataclass
class Recommendation:
    """Eine Empfehlung"""
    rec_id: str
    media_type: MediaType
    title: str
    reason: str  # Warum empfohlen
    confidence: float  # 0-1
    based_on: List[str]  # IDs der Basis-Medien
    predicted_rating: float  # Geschaetzte Bewertung 0-5
    keywords: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# MEDIEN-TAGEBUCH
# =============================================================================

class MediaJournal:
    """
    Medien-Tagebuch - Was Holo gelesen/gesehen/gehoert hat.

    Speichert Medienkonsum mit emotionalem Kontext.
    """

    def __init__(self, data_dir: str = "data/journal"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.entries: Dict[str, JournalEntry] = {}
        self._load()

        logger.info("MediaJournal initialisiert")

    def _generate_id(self, content: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5((content + datetime.now().isoformat()).encode()).hexdigest()[:12]

    def _load(self):
        """Laedt gespeicherte Eintraege"""
        journal_file = self.data_dir / "journal.json"

        if not journal_file.exists():
            return

        try:
            with open(journal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for entry_id, entry_data in data.items():
                entry_data['media_type'] = MediaType(entry_data['media_type'])
                entry_data['emotional_tags'] = [
                    EmotionalTag(t) for t in entry_data.get('emotional_tags', [])
                ]
                self.entries[entry_id] = JournalEntry(**entry_data)

            logger.info(f"Journal geladen: {len(self.entries)} Eintraege")
        except Exception as e:
            logger.error(f"Journal laden fehlgeschlagen: {e}")

    def _save(self):
        """Speichert alle Eintraege"""
        journal_file = self.data_dir / "journal.json"

        data = {}
        for entry_id, entry in self.entries.items():
            entry_dict = asdict(entry)
            entry_dict['media_type'] = entry.media_type.value
            entry_dict['emotional_tags'] = [t.value for t in entry.emotional_tags]
            data[entry_id] = entry_dict

        with open(journal_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_entry(self, media_type: MediaType, title: str,
                  mood_before: float = 0.5, mood_after: float = 0.5,
                  energy_before: float = 0.5, energy_after: float = 0.5,
                  rating: float = 3.0, emotional_tags: List[EmotionalTag] = None,
                  keywords: List[str] = None, notes: str = "",
                  source: str = None, duration_minutes: float = None,
                  sentiment: float = None, complexity: float = None,
                  topics: List[str] = None) -> JournalEntry:
        """
        Fuegt einen neuen Tagebuch-Eintrag hinzu.

        Args:
            media_type: Art des Mediums
            title: Titel
            mood_before/after: Stimmung vor/nach dem Konsum
            energy_before/after: Energie vor/nach dem Konsum
            rating: Bewertung 0-5
            emotional_tags: Emotionale Tags
            keywords: Schluesselwoerter
            notes: Holos Notizen
            ...
        """
        entry_id = self._generate_id(title)

        entry = JournalEntry(
            entry_id=entry_id,
            media_type=media_type,
            title=title,
            source=source,
            consumed_at=datetime.now().isoformat(),
            duration_minutes=duration_minutes,
            mood_before=mood_before,
            mood_after=mood_after,
            energy_before=energy_before,
            energy_after=energy_after,
            rating=rating,
            emotional_tags=emotional_tags or [],
            keywords=keywords or [],
            notes=notes,
            sentiment=sentiment,
            complexity=complexity,
            topics=topics or []
        )

        self.entries[entry_id] = entry
        self._save()

        logger.info(f"Journal-Eintrag hinzugefuegt: {title}")
        return entry

    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Holt einen Eintrag"""
        return self.entries.get(entry_id)

    def get_entries_by_type(self, media_type: MediaType) -> List[JournalEntry]:
        """Holt alle Eintraege eines Typs"""
        return [e for e in self.entries.values() if e.media_type == media_type]

    def get_recent_entries(self, days: int = 7) -> List[JournalEntry]:
        """Holt die letzten Eintraege"""
        cutoff = datetime.now() - timedelta(days=days)
        entries = []

        for entry in self.entries.values():
            entry_date = datetime.fromisoformat(entry.consumed_at)
            if entry_date > cutoff:
                entries.append(entry)

        return sorted(entries, key=lambda e: e.consumed_at, reverse=True)

    def get_favorites(self, min_rating: float = 4.0) -> List[JournalEntry]:
        """Holt Favoriten (hoch bewertete Eintraege)"""
        return sorted(
            [e for e in self.entries.values() if e.rating >= min_rating],
            key=lambda e: e.rating,
            reverse=True
        )

    def get_mood_boosters(self) -> List[JournalEntry]:
        """Holt Medien, die Holos Stimmung verbessert haben"""
        return [
            e for e in self.entries.values()
            if e.mood_after > e.mood_before + 0.1
        ]

    def search_by_keywords(self, keywords: List[str]) -> List[JournalEntry]:
        """Sucht nach Eintraegen mit bestimmten Keywords"""
        results = []
        keywords_lower = [k.lower() for k in keywords]

        for entry in self.entries.values():
            entry_keywords = [k.lower() for k in entry.keywords]
            if any(k in entry_keywords for k in keywords_lower):
                results.append(entry)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken ueber das Journal zurueck"""
        if not self.entries:
            return {"total": 0}

        entries = list(self.entries.values())

        type_counts = Counter(e.media_type.value for e in entries)
        avg_rating = sum(e.rating for e in entries) / len(entries)
        avg_mood_change = sum(e.mood_after - e.mood_before for e in entries) / len(entries)

        return {
            "total": len(entries),
            "by_type": dict(type_counts),
            "avg_rating": round(avg_rating, 2),
            "avg_mood_change": round(avg_mood_change, 3),
            "favorites_count": len(self.get_favorites()),
            "mood_boosters_count": len(self.get_mood_boosters())
        }


# =============================================================================
# EMOTIONALE VERBINDUNGEN
# =============================================================================

class EmotionalConnectionManager:
    """
    Verwaltet emotionale Verbindungen zu Medien.

    Trackt wie stark Holo mit bestimmten Medien verbunden ist.
    """

    def __init__(self, data_dir: str = "data/connections"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.connections: Dict[str, EmotionalConnection] = {}
        self._load()

        logger.info("EmotionalConnectionManager initialisiert")

    def _generate_id(self, content: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _load(self):
        """Laedt gespeicherte Verbindungen"""
        conn_file = self.data_dir / "connections.json"

        if not conn_file.exists():
            return

        try:
            with open(conn_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for conn_id, conn_data in data.items():
                self.connections[conn_id] = EmotionalConnection(**conn_data)

            logger.info(f"Verbindungen geladen: {len(self.connections)}")
        except Exception as e:
            logger.error(f"Verbindungen laden fehlgeschlagen: {e}")

    def _save(self):
        """Speichert alle Verbindungen"""
        conn_file = self.data_dir / "connections.json"

        data = {cid: asdict(conn) for cid, conn in self.connections.items()}

        with open(conn_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_connection(self, media_id: str, media_title: str,
                          initial_strength: float = 0.5) -> EmotionalConnection:
        """Erstellt eine neue emotionale Verbindung"""
        conn_id = self._generate_id(media_id)
        now = datetime.now().isoformat()

        connection = EmotionalConnection(
            connection_id=conn_id,
            media_id=media_id,
            media_title=media_title,
            bond_strength=initial_strength,
            positive_memories=[],
            negative_memories=[],
            associated_feelings={},
            first_exposure=now,
            last_exposure=now,
            exposure_count=1,
            trigger_words=[],
            trigger_topics=[]
        )

        self.connections[conn_id] = connection
        self._save()

        return connection

    def strengthen_bond(self, conn_id: str, amount: float = 0.1,
                        memory: str = None, positive: bool = True):
        """Verstaerkt eine emotionale Verbindung"""
        if conn_id not in self.connections:
            return

        conn = self.connections[conn_id]
        conn.bond_strength = min(1.0, conn.bond_strength + amount)
        conn.last_exposure = datetime.now().isoformat()
        conn.exposure_count += 1

        if memory:
            if positive:
                conn.positive_memories.append(memory)
                conn.positive_memories = conn.positive_memories[-10:]  # Max 10
            else:
                conn.negative_memories.append(memory)
                conn.negative_memories = conn.negative_memories[-10:]

        self._save()

    def weaken_bond(self, conn_id: str, amount: float = 0.1):
        """Schwaecht eine emotionale Verbindung"""
        if conn_id not in self.connections:
            return

        conn = self.connections[conn_id]
        conn.bond_strength = max(0.0, conn.bond_strength - amount)
        self._save()

    def add_feeling(self, conn_id: str, feeling: str, strength: float):
        """Fuegt ein assoziiertes Gefuehl hinzu"""
        if conn_id not in self.connections:
            return

        conn = self.connections[conn_id]
        conn.associated_feelings[feeling] = min(1.0, strength)
        self._save()

    def add_trigger(self, conn_id: str, trigger_word: str = None,
                    trigger_topic: str = None):
        """Fuegt einen Trigger hinzu"""
        if conn_id not in self.connections:
            return

        conn = self.connections[conn_id]

        if trigger_word and trigger_word not in conn.trigger_words:
            conn.trigger_words.append(trigger_word)
            conn.trigger_words = conn.trigger_words[-20:]  # Max 20

        if trigger_topic and trigger_topic not in conn.trigger_topics:
            conn.trigger_topics.append(trigger_topic)
            conn.trigger_topics = conn.trigger_topics[-10:]

        self._save()

    def find_by_trigger(self, text: str) -> List[EmotionalConnection]:
        """Findet Verbindungen die durch Text getriggert werden"""
        text_lower = text.lower()
        triggered = []

        for conn in self.connections.values():
            for trigger in conn.trigger_words:
                if trigger.lower() in text_lower:
                    triggered.append(conn)
                    break

        return sorted(triggered, key=lambda c: c.bond_strength, reverse=True)

    def get_strongest_connections(self, n: int = 10) -> List[EmotionalConnection]:
        """Holt die staerksten emotionalen Verbindungen"""
        return sorted(
            self.connections.values(),
            key=lambda c: c.bond_strength,
            reverse=True
        )[:n]


# =============================================================================
# WISSENS-GRAPH
# =============================================================================

class KnowledgeGraph:
    """
    Wissens-Graph - Verbindungen zwischen Medien und Konzepten.

    Baut ein Netz aus Beziehungen zwischen konsumierten Medien auf.
    """

    def __init__(self, data_dir: str = "data/knowledge"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[Dict[str, Any]] = []
        self._load()

        logger.info("KnowledgeGraph initialisiert")

    def _generate_id(self, content: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _load(self):
        """Laedt den Graph"""
        nodes_file = self.data_dir / "nodes.json"
        edges_file = self.data_dir / "edges.json"

        if nodes_file.exists():
            try:
                with open(nodes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for node_id, node_data in data.items():
                    self.nodes[node_id] = KnowledgeNode(**node_data)
            except Exception as e:
                logger.error(f"Nodes laden fehlgeschlagen: {e}")

        if edges_file.exists():
            try:
                with open(edges_file, 'r', encoding='utf-8') as f:
                    self.edges = json.load(f)
            except Exception as e:
                logger.error(f"Edges laden fehlgeschlagen: {e}")

        logger.info(f"Graph geladen: {len(self.nodes)} Knoten, {len(self.edges)} Kanten")

    def _save(self):
        """Speichert den Graph"""
        nodes_file = self.data_dir / "nodes.json"
        edges_file = self.data_dir / "edges.json"

        nodes_data = {nid: asdict(node) for nid, node in self.nodes.items()}

        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump(nodes_data, f, ensure_ascii=False, indent=2)

        with open(edges_file, 'w', encoding='utf-8') as f:
            json.dump(self.edges, f, ensure_ascii=False, indent=2)

    def add_node(self, node_type: str, name: str, description: str = "",
                 attributes: Dict[str, Any] = None,
                 confidence: float = 0.8) -> KnowledgeNode:
        """Fuegt einen Knoten hinzu"""
        node_id = self._generate_id(f"{node_type}_{name}")

        if node_id in self.nodes:
            return self.nodes[node_id]

        node = KnowledgeNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            description=description,
            attributes=attributes or {},
            relations=[],
            created_at=datetime.now().isoformat(),
            confidence=confidence
        )

        self.nodes[node_id] = node
        self._save()

        logger.info(f"Knoten hinzugefuegt: {name}")
        return node

    def add_edge(self, source_id: str, target_id: str,
                 relation_type: RelationType, strength: float = 0.5) -> bool:
        """Fuegt eine Kante hinzu"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return False

        # Pruefe ob Kante bereits existiert
        for edge in self.edges:
            if (edge['source'] == source_id and
                edge['target'] == target_id and
                edge['relation'] == relation_type.value):
                # Update Staerke
                edge['strength'] = max(edge['strength'], strength)
                self._save()
                return True

        edge = {
            "source": source_id,
            "target": target_id,
            "relation": relation_type.value,
            "strength": strength,
            "created_at": datetime.now().isoformat()
        }

        self.edges.append(edge)

        # Auch in Node Relations speichern
        self.nodes[source_id].relations.append({
            "target": target_id,
            "relation": relation_type.value,
            "strength": strength
        })

        self._save()
        return True

    def find_related(self, node_id: str, relation_type: RelationType = None,
                     min_strength: float = 0.0) -> List[Tuple[KnowledgeNode, float]]:
        """Findet verwandte Knoten"""
        related = []

        for edge in self.edges:
            if edge['source'] == node_id:
                if relation_type and edge['relation'] != relation_type.value:
                    continue
                if edge['strength'] < min_strength:
                    continue

                target_node = self.nodes.get(edge['target'])
                if target_node:
                    related.append((target_node, edge['strength']))

            elif edge['target'] == node_id:
                if relation_type and edge['relation'] != relation_type.value:
                    continue
                if edge['strength'] < min_strength:
                    continue

                source_node = self.nodes.get(edge['source'])
                if source_node:
                    related.append((source_node, edge['strength']))

        return sorted(related, key=lambda x: x[1], reverse=True)

    def find_path(self, source_id: str, target_id: str,
                  max_depth: int = 5) -> Optional[List[str]]:
        """Findet einen Pfad zwischen zwei Knoten (BFS)"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        visited = set()
        queue = [(source_id, [source_id])]

        while queue:
            current, path = queue.pop(0)

            if current == target_id:
                return path

            if current in visited or len(path) > max_depth:
                continue

            visited.add(current)

            for edge in self.edges:
                next_node = None
                if edge['source'] == current:
                    next_node = edge['target']
                elif edge['target'] == current:
                    next_node = edge['source']

                if next_node and next_node not in visited:
                    queue.append((next_node, path + [next_node]))

        return None

    def get_node_by_name(self, name: str) -> Optional[KnowledgeNode]:
        """Findet einen Knoten nach Namen"""
        name_lower = name.lower()
        for node in self.nodes.values():
            if node.name.lower() == name_lower:
                return node
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Graph-Statistiken zurueck"""
        type_counts = Counter(n.node_type for n in self.nodes.values())
        relation_counts = Counter(e['relation'] for e in self.edges)

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(type_counts),
            "relation_types": dict(relation_counts),
            "avg_relations_per_node": len(self.edges) / max(len(self.nodes), 1)
        }


# =============================================================================
# EMPFEHLUNGS-SYSTEM
# =============================================================================

class RecommendationEngine:
    """
    Empfehlungs-System - Schlaegt Medien vor basierend auf Praeferenzen.
    """

    def __init__(self, journal: MediaJournal, graph: KnowledgeGraph):
        self.journal = journal
        self.graph = graph
        self.recommendations: List[Recommendation] = []

        logger.info("RecommendationEngine initialisiert")

    def _generate_id(self, content: str) -> str:
        """Generiert eindeutige ID"""
        return hashlib.md5((content + datetime.now().isoformat()).encode()).hexdigest()[:12]

    def generate_recommendations(self, n: int = 5) -> List[Recommendation]:
        """
        Generiert Empfehlungen basierend auf:
        - Favoriten
        - Stimmungsverbesserern
        - Aehnlichen Themen im Wissens-Graph
        """
        recommendations = []

        # Basis: Favoriten und deren Keywords
        favorites = self.journal.get_favorites(min_rating=4.0)
        all_keywords = []
        all_topics = []

        for fav in favorites:
            all_keywords.extend(fav.keywords)
            all_topics.extend(fav.topics)

        keyword_counts = Counter(all_keywords)
        topic_counts = Counter(all_topics)

        # Top Keywords/Topics fuer Empfehlungen
        top_keywords = [k for k, _ in keyword_counts.most_common(10)]
        top_topics = [t for t, _ in topic_counts.most_common(5)]

        # Empfehlung basierend auf Keywords
        if top_keywords:
            rec = Recommendation(
                rec_id=self._generate_id("keywords"),
                media_type=MediaType.TEXT,
                title=f"Mehr ueber: {', '.join(top_keywords[:3])}",
                reason=f"Basierend auf deinen Lieblingsthemen: {', '.join(top_keywords[:3])}",
                confidence=0.7,
                based_on=[f.entry_id for f in favorites[:3]],
                predicted_rating=4.0,
                keywords=top_keywords[:5]
            )
            recommendations.append(rec)

        # Empfehlung basierend auf Stimmungsverbesserern
        mood_boosters = self.journal.get_mood_boosters()
        if mood_boosters:
            booster_keywords = []
            for mb in mood_boosters[:5]:
                booster_keywords.extend(mb.keywords)

            if booster_keywords:
                rec = Recommendation(
                    rec_id=self._generate_id("mood"),
                    media_type=mood_boosters[0].media_type,
                    title="Stimmungsaufheller gesucht?",
                    reason="Dieses Medium hat deine Stimmung verbessert",
                    confidence=0.8,
                    based_on=[mb.entry_id for mb in mood_boosters[:3]],
                    predicted_rating=4.5,
                    keywords=list(set(booster_keywords))[:5]
                )
                recommendations.append(rec)

        # Empfehlung basierend auf Wissens-Graph
        for topic in top_topics[:3]:
            topic_node = self.graph.get_node_by_name(topic)
            if topic_node:
                related = self.graph.find_related(topic_node.node_id,
                                                   RelationType.SIMILAR_TOPIC)
                for rel_node, strength in related[:2]:
                    rec = Recommendation(
                        rec_id=self._generate_id(rel_node.name),
                        media_type=MediaType.TEXT,
                        title=f"Erkunde: {rel_node.name}",
                        reason=f"Verwandt mit {topic}",
                        confidence=strength,
                        based_on=[topic_node.node_id],
                        predicted_rating=3.5 + strength,
                        keywords=[topic, rel_node.name]
                    )
                    recommendations.append(rec)

        # Sortiere nach Confidence
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        self.recommendations = recommendations[:n]

        return self.recommendations

    def get_recommendation_for_mood(self, current_mood: float) -> Optional[Recommendation]:
        """Empfiehlt basierend auf aktueller Stimmung"""
        if current_mood < 0.4:
            # Niedrige Stimmung -> Stimmungsaufheller
            mood_boosters = self.journal.get_mood_boosters()
            if mood_boosters:
                best = mood_boosters[0]
                return Recommendation(
                    rec_id=self._generate_id("mood_boost"),
                    media_type=best.media_type,
                    title=f"Aufmunterung: {best.title}",
                    reason="Hat dir frueher geholfen, dich besser zu fuehlen",
                    confidence=0.9,
                    based_on=[best.entry_id],
                    predicted_rating=best.rating,
                    keywords=best.keywords
                )

        elif current_mood > 0.7:
            # Gute Stimmung -> Etwas Herausforderndes
            complex_entries = [
                e for e in self.journal.entries.values()
                if e.complexity and e.complexity > 0.6
            ]
            if complex_entries:
                best = max(complex_entries, key=lambda e: e.rating)
                return Recommendation(
                    rec_id=self._generate_id("challenge"),
                    media_type=best.media_type,
                    title=f"Herausforderung: {best.title}",
                    reason="Du bist gerade in guter Stimmung fuer etwas Anspruchsvolles",
                    confidence=0.7,
                    based_on=[best.entry_id],
                    predicted_rating=best.rating,
                    keywords=best.keywords
                )

        return None


# =============================================================================
# UNIFIED MEDIA INTEGRATION
# =============================================================================

class HoloMediaIntegration:
    """
    Vereinigte Schnittstelle fuer alle Medien-Integration-Features.
    """

    def __init__(self, data_dir: str = "data/media"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Komponenten
        self.journal = MediaJournal(str(self.data_dir / "journal"))
        self.connections = EmotionalConnectionManager(str(self.data_dir / "connections"))
        self.graph = KnowledgeGraph(str(self.data_dir / "knowledge"))
        self.recommendations = RecommendationEngine(self.journal, self.graph)

        logger.info("HoloMediaIntegration initialisiert")

    def log_media_consumption(self, media_type: MediaType, title: str,
                              mood_before: float, mood_after: float,
                              rating: float, keywords: List[str] = None,
                              notes: str = "", topics: List[str] = None,
                              **kwargs) -> JournalEntry:
        """
        Protokolliert Medienkonsum und aktualisiert alle Systeme.
        """
        # Journal-Eintrag
        entry = self.journal.add_entry(
            media_type=media_type,
            title=title,
            mood_before=mood_before,
            mood_after=mood_after,
            rating=rating,
            keywords=keywords or [],
            notes=notes,
            topics=topics or [],
            **kwargs
        )

        # Emotionale Verbindung erstellen/staerken
        conn_id = hashlib.md5(entry.entry_id.encode()).hexdigest()[:12]
        if conn_id not in self.connections.connections:
            self.connections.create_connection(
                entry.entry_id,
                title,
                initial_strength=rating / 5.0
            )
        else:
            self.connections.strengthen_bond(
                conn_id,
                amount=0.1,
                memory=notes if notes else None,
                positive=mood_after > mood_before
            )

        # Knoten im Wissens-Graph
        media_node = self.graph.add_node(
            node_type="media",
            name=title,
            description=notes,
            attributes={
                "type": media_type.value,
                "rating": rating,
                "keywords": keywords or []
            }
        )

        # Topic-Knoten und Verbindungen
        for topic in (topics or []):
            topic_node = self.graph.add_node(
                node_type="topic",
                name=topic
            )
            self.graph.add_edge(
                media_node.node_id,
                topic_node.node_id,
                RelationType.SIMILAR_TOPIC,
                strength=0.7
            )

        return entry

    def get_recommendations(self, n: int = 5) -> List[Recommendation]:
        """Holt Empfehlungen"""
        return self.recommendations.generate_recommendations(n)

    def find_emotional_triggers(self, text: str) -> List[EmotionalConnection]:
        """Findet emotionale Trigger im Text"""
        return self.connections.find_by_trigger(text)

    def get_related_media(self, title: str) -> List[Tuple[str, float]]:
        """Findet verwandte Medien"""
        node = self.graph.get_node_by_name(title)
        if not node:
            return []

        related = self.graph.find_related(node.node_id)
        return [(n.name, s) for n, s in related if n.node_type == "media"]

    def get_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung aller Systeme zurueck"""
        return {
            "journal": self.journal.get_statistics(),
            "connections": {
                "total": len(self.connections.connections),
                "strongest": [
                    {"title": c.media_title, "strength": c.bond_strength}
                    for c in self.connections.get_strongest_connections(5)
                ]
            },
            "graph": self.graph.get_statistics()
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("HOLO MEDIA INTEGRATION - Test")
    print("=" * 60)

    integration = HoloMediaIntegration(data_dir="data/test_media")

    # Test: Medienkonsum protokollieren
    print("\n[1] Protokolliere Medienkonsum...")

    entry1 = integration.log_media_consumption(
        media_type=MediaType.BOOK,
        title="Der kleine Prinz",
        mood_before=0.5,
        mood_after=0.8,
        rating=5.0,
        keywords=["freundschaft", "liebe", "philosophie"],
        notes="Wunderschoenes Buch ueber das Wesentliche im Leben",
        topics=["philosophie", "kinderbuch", "klassiker"]
    )
    print(f"  - Eintrag erstellt: {entry1.title}")

    entry2 = integration.log_media_consumption(
        media_type=MediaType.ARTICLE,
        title="KI und Bewusstsein",
        mood_before=0.6,
        mood_after=0.7,
        rating=4.0,
        keywords=["ki", "bewusstsein", "philosophie"],
        notes="Interessante Perspektiven auf KI-Bewusstsein",
        topics=["philosophie", "technologie", "ki"]
    )
    print(f"  - Eintrag erstellt: {entry2.title}")

    # Test: Empfehlungen
    print("\n[2] Generiere Empfehlungen...")
    recs = integration.get_recommendations(3)
    for rec in recs:
        print(f"  - {rec.title} (Confidence: {rec.confidence})")

    # Test: Zusammenfassung
    print("\n[3] Zusammenfassung:")
    summary = integration.get_summary()
    print(f"  - Journal-Eintraege: {summary['journal']['total']}")
    print(f"  - Graph-Knoten: {summary['graph']['total_nodes']}")
    print(f"  - Graph-Kanten: {summary['graph']['total_edges']}")

    # Test: Verwandte Medien
    print("\n[4] Verwandte Medien zu 'Der kleine Prinz':")
    related = integration.get_related_media("Der kleine Prinz")
    for title, strength in related:
        print(f"  - {title} (Staerke: {strength})")

    print("\n" + "=" * 60)
    print("Test abgeschlossen!")
    print("=" * 60)
