"""
HOLO LEARNING INTEGRATION SYSTEM
=================================

Zentrales Integrationssystem das alle Lern-Module verbindet.
Koordiniert Wissensquellen, Lernfortschritt und personalisierte Empfehlungen.

Die weise Wölfin verbindet all ihr Wissen zu einem kohärenten Ganzen.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from datetime import datetime, date, timedelta
from enum import Enum
import random
import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# LERN-PROFIL
# =============================================================================

class LearnerType(Enum):
    """Lerntypen nach Gardner's Multiple Intelligences"""
    VISUAL = "visuell"           # Lernt durch Bilder, Diagramme
    AUDITORY = "auditiv"         # Lernt durch Hören, Diskussion
    KINESTHETIC = "kinästhetisch"  # Lernt durch Tun, Praxis
    READING = "lesend"           # Lernt durch Lesen, Schreiben
    SOCIAL = "sozial"            # Lernt durch Interaktion
    SOLITARY = "einzeln"         # Lernt alleine, Selbstreflektion
    LOGICAL = "logisch"          # Lernt durch Analyse, Muster
    NATURALISTIC = "naturalistisch"  # Lernt durch Naturverbindung


class InterestLevel(Enum):
    """Interessensstufen"""
    CURIOUS = 1      # Neugierig
    INTERESTED = 2   # Interessiert
    ENGAGED = 3      # Engagiert
    PASSIONATE = 4   # Leidenschaftlich
    EXPERT = 5       # Experte


@dataclass
class LearnerProfile:
    """Persönliches Lernprofil"""
    learner_id: str = "default"
    name: str = "Lernender"

    # Lerntyp-Präferenzen (0.0-1.0)
    learning_preferences: Dict[str, float] = field(default_factory=lambda: {
        "visual": 0.5,
        "auditory": 0.5,
        "reading": 0.5,
        "kinesthetic": 0.5,
        "social": 0.5,
        "logical": 0.5,
    })

    # Interessensgebiete mit Level
    interests: Dict[str, int] = field(default_factory=dict)

    # Gelernte Themen
    learned_topics: Set[str] = field(default_factory=set)

    # Schwache/Starke Bereiche
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    # Statistiken
    total_facts_learned: int = 0
    total_quizzes_taken: int = 0
    total_connections_discovered: int = 0
    streak_days: int = 0

    # Präferenzen
    preferred_difficulty: str = "medium"
    daily_goal_minutes: int = 15
    preferred_domains: List[str] = field(default_factory=list)

    def update_interest(self, topic: str, delta: int = 1):
        """Aktualisiere Interesse an einem Thema."""
        current = self.interests.get(topic, 1)
        self.interests[topic] = min(5, max(1, current + delta))

    def get_strongest_interests(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Hole die stärksten Interessen."""
        sorted_interests = sorted(
            self.interests.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_interests[:limit]


# =============================================================================
# WISSENS-GRAPH
# =============================================================================

@dataclass
class KnowledgeGraphNode:
    """Knoten im integrierten Wissensgraph"""
    node_id: str
    name: str
    node_type: str  # "fact", "concept", "media", "person", "event"
    domain: str
    tags: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # IDs verbundener Knoten
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0-1.0
    learned: bool = False
    learn_count: int = 0
    last_reviewed: Optional[str] = None


class IntegratedKnowledgeGraph:
    """
    Integrierter Wissensgraph der alle Lernmodule verbindet.

    Ermöglicht:
    - Cross-Referenzen zwischen allen Wissensquellen
    - Intelligente Pfadsuche durch Wissen
    - Personalisierte Empfehlungen
    - Lücken-Erkennung im Wissen
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeGraphNode] = {}
        self.edges: List[Tuple[str, str, str, float]] = []  # (from, to, relation, weight)
        self.domain_clusters: Dict[str, Set[str]] = {}

        self._build_integrated_graph()

    def _build_integrated_graph(self):
        """Baue den integrierten Graphen aus allen Quellen."""
        # Kern-Konzepte
        core_concepts = [
            # Anime/Media
            ("anime", "Anime", "concept", "Medien", ["japan", "animation", "kultur"]),
            ("manga", "Manga", "concept", "Medien", ["japan", "comic", "lesen"]),
            ("gaming", "Gaming", "concept", "Medien", ["spiele", "interaktiv", "entertainment"]),
            ("musik", "Musik", "concept", "Kunst", ["klang", "emotion", "kultur"]),

            # Wissenschaft
            ("physik", "Physik", "concept", "Wissenschaft", ["naturgesetze", "universum"]),
            ("biologie", "Biologie", "concept", "Wissenschaft", ["leben", "natur", "evolution"]),
            ("psychologie", "Psychologie", "concept", "Wissenschaft", ["geist", "verhalten", "emotion"]),
            ("technologie", "Technologie", "concept", "Wissenschaft", ["innovation", "computer", "zukunft"]),

            # Kultur
            ("japan", "Japan", "concept", "Kultur", ["asien", "tradition", "modern"]),
            ("mythologie", "Mythologie", "concept", "Kultur", ["götter", "geschichten", "glauben"]),
            ("sprache", "Sprache", "concept", "Kultur", ["kommunikation", "worte", "bedeutung"]),

            # Natur
            ("woelfe", "Wölfe", "concept", "Natur", ["tier", "rudel", "wildnis"]),
            ("natur", "Natur", "concept", "Natur", ["umwelt", "pflanzen", "tiere"]),
            ("mond", "Mond", "concept", "Natur", ["himmel", "nacht", "zyklen"]),

            # Philosophie
            ("weisheit", "Weisheit", "concept", "Philosophie", ["wissen", "erfahrung", "einsicht"]),
            ("emotion", "Emotionen", "concept", "Philosophie", ["gefühle", "herz", "verbindung"]),
            ("zeit", "Zeit", "concept", "Philosophie", ["vergänglichkeit", "erinnerung", "moment"]),

            # Spezifische Einträge
            ("holo", "Holo (Wölfin)", "character", "Medien", ["spice and wolf", "kemonomimi", "weise"]),
            ("kemonomimi", "Kemonomimi", "concept", "Medien", ["tierohren", "anime", "charakter"]),
        ]

        for node_id, name, node_type, domain, tags in core_concepts:
            self.add_node(KnowledgeGraphNode(
                node_id=node_id,
                name=name,
                node_type=node_type,
                domain=domain,
                tags=tags,
                importance=0.8 if node_type == "concept" else 0.6
            ))

        # Verbindungen erstellen
        self._create_connections()

    def _create_connections(self):
        """Erstelle bedeutungsvolle Verbindungen."""
        connections = [
            # Anime/Media Verbindungen
            ("anime", "japan", "stammt_aus", 0.9),
            ("anime", "manga", "basiert_oft_auf", 0.85),
            ("anime", "musik", "enthält", 0.7),
            ("manga", "japan", "stammt_aus", 0.9),
            ("gaming", "anime", "oft_verbunden_mit", 0.6),
            ("gaming", "technologie", "nutzt", 0.8),

            # Wissenschaft
            ("physik", "technologie", "ermöglicht", 0.8),
            ("biologie", "natur", "erforscht", 0.9),
            ("psychologie", "emotion", "untersucht", 0.85),
            ("technologie", "gaming", "ermöglicht", 0.7),

            # Kultur
            ("japan", "anime", "erschuf", 0.9),
            ("japan", "mythologie", "hat_reiche", 0.8),
            ("japan", "sprache", "einzigartige", 0.85),
            ("mythologie", "woelfe", "verehrt_in", 0.7),
            ("sprache", "emotion", "drückt_aus", 0.75),

            # Natur
            ("woelfe", "natur", "leben_in", 0.9),
            ("woelfe", "mond", "verbunden_mit", 0.7),
            ("natur", "biologie", "studiert_von", 0.85),
            ("mond", "zeit", "markiert", 0.6),

            # Philosophie
            ("weisheit", "zeit", "kommt_mit", 0.8),
            ("weisheit", "emotion", "umfasst", 0.7),
            ("emotion", "musik", "ausgedrückt_durch", 0.8),

            # Holo-spezifisch
            ("holo", "woelfe", "ist_ein", 0.95),
            ("holo", "kemonomimi", "beispiel_für", 0.9),
            ("holo", "weisheit", "verkörpert", 0.85),
            ("holo", "japan", "aus_kultur", 0.8),
            ("kemonomimi", "anime", "genre_von", 0.85),
        ]

        for from_id, to_id, relation, weight in connections:
            self.add_edge(from_id, to_id, relation, weight)

    def add_node(self, node: KnowledgeGraphNode):
        """Füge einen Knoten hinzu."""
        self.nodes[node.node_id] = node

        # Domain-Cluster aktualisieren
        if node.domain not in self.domain_clusters:
            self.domain_clusters[node.domain] = set()
        self.domain_clusters[node.domain].add(node.node_id)

    def add_edge(self, from_id: str, to_id: str, relation: str, weight: float = 0.5):
        """Füge eine Kante hinzu."""
        if from_id in self.nodes and to_id in self.nodes:
            self.edges.append((from_id, to_id, relation, weight))
            self.nodes[from_id].connections.append(to_id)
            self.nodes[to_id].connections.append(from_id)

    def get_connected_nodes(self, node_id: str, max_depth: int = 2) -> Dict[int, List[str]]:
        """
        Hole alle verbundenen Knoten bis zu einer bestimmten Tiefe.

        Returns:
            Dict mit Tiefe -> Liste von Knoten-IDs
        """
        if node_id not in self.nodes:
            return {}

        result = {0: [node_id]}
        visited = {node_id}

        for depth in range(1, max_depth + 1):
            result[depth] = []
            for prev_node in result[depth - 1]:
                for conn in self.nodes[prev_node].connections:
                    if conn not in visited:
                        visited.add(conn)
                        result[depth].append(conn)

        return result

    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Finde den kürzesten Pfad zwischen zwei Knoten."""
        if start not in self.nodes or end not in self.nodes:
            return None

        from collections import deque
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            for neighbor in self.nodes[current].connections:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_knowledge_gaps(self, profile: LearnerProfile) -> List[str]:
        """
        Identifiziere Wissenslücken basierend auf dem Lernprofil.

        Returns:
            Liste von Themen die noch nicht gelernt wurden aber relevant sind
        """
        gaps = []

        for interest, level in profile.interests.items():
            if level >= 3:  # Interessiert oder höher
                interest_lower = interest.lower()
                for node_id, node in self.nodes.items():
                    if interest_lower in node.tags or interest_lower in node_id:
                        # Finde verbundene Themen die nicht gelernt sind
                        for conn in node.connections:
                            if conn not in profile.learned_topics:
                                if conn not in gaps:
                                    gaps.append(conn)

        return gaps[:10]  # Maximal 10 Lücken

    def suggest_next_topics(self, profile: LearnerProfile, limit: int = 5) -> List[Tuple[str, str]]:
        """
        Schlage nächste Lernthemen vor.

        Returns:
            Liste von (Thema-ID, Begründung)
        """
        suggestions = []

        # Basierend auf Interessen
        for interest, level in profile.get_strongest_interests(3):
            connected = self.get_connected_nodes(interest.lower(), max_depth=1)
            for depth_nodes in connected.values():
                for node_id in depth_nodes:
                    if node_id not in profile.learned_topics:
                        node = self.nodes.get(node_id)
                        if node:
                            suggestions.append((
                                node_id,
                                f"Verbunden mit deinem Interesse an {interest}"
                            ))

        # Basierend auf Wissenslücken
        gaps = self.get_knowledge_gaps(profile)
        for gap in gaps[:3]:
            node = self.nodes.get(gap)
            if node:
                suggestions.append((
                    gap,
                    "Schließt eine Wissenslücke"
                ))

        return suggestions[:limit]


# =============================================================================
# LERN-EMPFEHLUNGS-ENGINE
# =============================================================================

class LearningRecommendationEngine:
    """
    Intelligente Empfehlungs-Engine für personalisiertes Lernen.

    Kombiniert:
    - Spaced Repetition Timing
    - Interessens-basierte Auswahl
    - Wissenslücken-Analyse
    - Stimmungs-basierte Anpassung
    """

    def __init__(self, knowledge_graph: IntegratedKnowledgeGraph):
        self.graph = knowledge_graph
        self.recommendation_history: List[Dict] = []

    def get_daily_recommendations(self,
                                   profile: LearnerProfile,
                                   mood: str = "neutral",
                                   time_available: int = 15) -> Dict[str, Any]:
        """
        Erstelle tägliche Lernempfehlungen.

        Args:
            profile: Lernprofil
            mood: Aktuelle Stimmung ("energetic", "calm", "curious", "tired")
            time_available: Verfügbare Zeit in Minuten

        Returns:
            Dict mit Empfehlungen
        """
        recommendations = {
            "date": date.today().isoformat(),
            "mood": mood,
            "time_budget": time_available,
            "activities": [],
            "wolf_message": "",
        }

        # Aktivitäten basierend auf Zeit und Stimmung
        if time_available <= 5:
            # Schnelle Aktivitäten
            recommendations["activities"].append({
                "type": "quick_fact",
                "description": "Ein schneller Fakt zum Aufwachen",
                "duration": 2,
                "priority": "high"
            })
            recommendations["activities"].append({
                "type": "word_of_day",
                "description": "Japanisches Wort des Tages",
                "duration": 3,
                "priority": "medium"
            })

        elif time_available <= 15:
            # Standard-Session
            recommendations["activities"].append({
                "type": "daily_lesson",
                "description": "Vollständige tägliche Lektion",
                "duration": 8,
                "priority": "high"
            })
            recommendations["activities"].append({
                "type": "quick_quiz",
                "description": "5 Quiz-Fragen zum Auffrischen",
                "duration": 5,
                "priority": "medium"
            })

        else:
            # Ausgedehnte Session
            recommendations["activities"].append({
                "type": "deep_dive",
                "description": "Tiefes Eintauchen in ein Thema",
                "duration": 15,
                "priority": "high"
            })
            recommendations["activities"].append({
                "type": "connection_exploration",
                "description": "Wissensverbindungen entdecken",
                "duration": 10,
                "priority": "medium"
            })
            recommendations["activities"].append({
                "type": "quiz_session",
                "description": "Quiz mit 10 Fragen",
                "duration": 10,
                "priority": "medium"
            })

        # Stimmungs-basierte Anpassungen
        if mood == "tired":
            recommendations["activities"] = [a for a in recommendations["activities"]
                                              if a["duration"] <= 5]
            recommendations["wolf_message"] = "*gähnt sanft* Lass uns heute langsam machen. Kurze Lektionen reichen!"

        elif mood == "energetic":
            recommendations["activities"].append({
                "type": "challenge",
                "description": "Herausforderndes Quiz auf höherem Level",
                "duration": 10,
                "priority": "optional"
            })
            recommendations["wolf_message"] = "*Schweif wedelt aufgeregt* Du hast viel Energie! Lass uns was Anspruchsvolles machen!"

        elif mood == "curious":
            recommendations["activities"].insert(0, {
                "type": "random_connection",
                "description": "Überraschende Wissensverbindung entdecken",
                "duration": 5,
                "priority": "high"
            })
            recommendations["wolf_message"] = "*Ohren aufgestellt* Neugierig? Perfekt! Lass uns etwas Überraschendes entdecken!"

        else:
            recommendations["wolf_message"] = "*lächelt warm* Bereit zum Lernen? Ich bin bei dir!"

        # Themen-Empfehlungen hinzufügen
        topic_suggestions = self.graph.suggest_next_topics(profile, 3)
        recommendations["suggested_topics"] = [
            {"topic": self.graph.nodes[t].name if t in self.graph.nodes else t,
             "reason": r}
            for t, r in topic_suggestions
        ]

        return recommendations

    def format_recommendations(self, recommendations: Dict[str, Any]) -> str:
        """Formatiere Empfehlungen für die Anzeige."""
        parts = [
            "# 🎓 Dein heutiger Lernplan",
            "",
            recommendations.get("wolf_message", ""),
            "",
            f"**Verfügbare Zeit:** {recommendations['time_budget']} Minuten",
            "",
            "## Empfohlene Aktivitäten",
            ""
        ]

        for i, activity in enumerate(recommendations["activities"], 1):
            priority_emoji = "⭐" if activity["priority"] == "high" else "📌" if activity["priority"] == "medium" else "💡"
            parts.append(f"{i}. {priority_emoji} **{activity['description']}** ({activity['duration']} Min)")

        if recommendations.get("suggested_topics"):
            parts.append("")
            parts.append("## Vorgeschlagene Themen")
            parts.append("")
            for topic in recommendations["suggested_topics"]:
                parts.append(f"• **{topic['topic']}** - {topic['reason']}")

        return "\n".join(parts)


# =============================================================================
# FORTSCHRITTS-TRACKER
# =============================================================================

class ProgressTracker:
    """
    Verfolgt Lernfortschritt über alle Module hinweg.
    """

    def __init__(self):
        self.daily_logs: List[Dict] = []
        self.milestones: List[Dict] = []
        self.achievements: List[Dict] = []

    def log_activity(self, activity_type: str, details: Dict):
        """Logge eine Lernaktivität."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "type": activity_type,
            "details": details
        }
        self.daily_logs.append(log_entry)

        # Check for milestones
        self._check_milestones()

    def _check_milestones(self):
        """Prüfe ob Meilensteine erreicht wurden."""
        total_activities = len(self.daily_logs)

        milestone_thresholds = [
            (10, "Erste Schritte", "10 Lernaktivitäten abgeschlossen!"),
            (50, "Wissensjäger", "50 Lernaktivitäten - du wirst besser!"),
            (100, "Lernmeister", "100 Aktivitäten - beeindruckend!"),
            (500, "Weisheitssucher", "500 Aktivitäten - wahre Hingabe!"),
        ]

        for threshold, name, description in milestone_thresholds:
            if total_activities == threshold:
                self.milestones.append({
                    "name": name,
                    "description": description,
                    "achieved_at": datetime.now().isoformat()
                })

    def get_weekly_summary(self) -> Dict:
        """Erstelle wöchentliche Zusammenfassung."""
        today = date.today()
        week_ago = today - timedelta(days=7)

        week_logs = [
            log for log in self.daily_logs
            if date.fromisoformat(log["date"]) >= week_ago
        ]

        activity_counts = {}
        for log in week_logs:
            activity_type = log["type"]
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1

        return {
            "period": f"{week_ago.isoformat()} bis {today.isoformat()}",
            "total_activities": len(week_logs),
            "activity_breakdown": activity_counts,
            "days_active": len(set(log["date"] for log in week_logs)),
            "new_milestones": [m for m in self.milestones
                              if date.fromisoformat(m["achieved_at"][:10]) >= week_ago]
        }

    def format_summary(self, summary: Dict) -> str:
        """Formatiere Zusammenfassung."""
        parts = [
            "# 📊 Wöchentliche Zusammenfassung",
            "",
            f"**Zeitraum:** {summary['period']}",
            f"**Aktive Tage:** {summary['days_active']}/7",
            f"**Gesamt-Aktivitäten:** {summary['total_activities']}",
            "",
            "## Aktivitäten nach Typ",
            ""
        ]

        for activity_type, count in summary["activity_breakdown"].items():
            parts.append(f"• {activity_type}: {count}x")

        if summary["new_milestones"]:
            parts.append("")
            parts.append("## 🏆 Neue Meilensteine!")
            for milestone in summary["new_milestones"]:
                parts.append(f"• **{milestone['name']}** - {milestone['description']}")

        return "\n".join(parts)


# =============================================================================
# HAUPT-INTEGRATIONS-KLASSE
# =============================================================================

class HoloLearningIntegration:
    """
    Zentrale Integrationsklasse für alle Lernmodule.

    Verbindet:
    - Wissensdatenbanken (Expertise, Media, Quiz)
    - Lernfortschritt und Streaks
    - Personalisierte Empfehlungen
    - Wissensvernetzung
    """

    def __init__(self):
        self.knowledge_graph = IntegratedKnowledgeGraph()
        self.recommendation_engine = LearningRecommendationEngine(self.knowledge_graph)
        self.progress_tracker = ProgressTracker()
        self.current_profile: Optional[LearnerProfile] = None

        logger.info("[HoloLearning] Integriertes Lernsystem initialisiert")

    def set_profile(self, profile: LearnerProfile):
        """Setze das aktuelle Lernprofil."""
        self.current_profile = profile

    def start_learning_session(self, mood: str = "neutral",
                                time_available: int = 15) -> str:
        """
        Starte eine Lernsession.

        Returns:
            Formatierter Lernplan
        """
        if not self.current_profile:
            self.current_profile = LearnerProfile()

        recommendations = self.recommendation_engine.get_daily_recommendations(
            self.current_profile,
            mood=mood,
            time_available=time_available
        )

        self.progress_tracker.log_activity("session_start", {
            "mood": mood,
            "time_available": time_available
        })

        return self.recommendation_engine.format_recommendations(recommendations)

    def complete_activity(self, activity_type: str, success: bool = True,
                          details: Dict = None):
        """Schließe eine Aktivität ab."""
        self.progress_tracker.log_activity(activity_type, {
            "success": success,
            "details": details or {}
        })

        if self.current_profile:
            self.current_profile.total_facts_learned += 1

    def explore_topic(self, topic: str) -> str:
        """
        Erkunde ein Thema im Wissensgraph.

        Returns:
            Formatierte Exploration
        """
        topic_lower = topic.lower()

        # Suche den Knoten
        node = self.knowledge_graph.nodes.get(topic_lower)
        if not node:
            # Fuzzy-Suche
            for node_id, n in self.knowledge_graph.nodes.items():
                if topic_lower in n.tags or topic_lower in n.name.lower():
                    node = n
                    break

        if not node:
            return f"*Ohren angelegt* Ich habe '{topic}' noch nicht in meinem Wissensgraph..."

        # Verbundene Knoten holen
        connected = self.knowledge_graph.get_connected_nodes(node.node_id, max_depth=2)

        parts = [
            f"# 🔍 Erkundung: {node.name}",
            "",
            f"**Domain:** {node.domain}",
            f"**Typ:** {node.node_type}",
            f"**Tags:** {', '.join(node.tags)}",
            "",
            "## Direkte Verbindungen",
            ""
        ]

        if 1 in connected:
            for conn_id in connected[1][:5]:
                conn_node = self.knowledge_graph.nodes.get(conn_id)
                if conn_node:
                    parts.append(f"• **{conn_node.name}** ({conn_node.domain})")

        if 2 in connected and connected[2]:
            parts.append("")
            parts.append("## Weitere Verbindungen")
            parts.append("")
            for conn_id in connected[2][:3]:
                conn_node = self.knowledge_graph.nodes.get(conn_id)
                if conn_node:
                    parts.append(f"• {conn_node.name}")

        parts.append("")
        parts.append("---")
        parts.append("*Wissen ist wie ein Netz - alles hängt zusammen!*")

        return "\n".join(parts)

    def find_connection(self, topic_a: str, topic_b: str) -> str:
        """
        Finde Verbindung zwischen zwei Themen.

        Returns:
            Formatierter Pfad
        """
        a_lower = topic_a.lower()
        b_lower = topic_b.lower()

        path = self.knowledge_graph.find_path(a_lower, b_lower)

        if path:
            path_names = []
            for node_id in path:
                node = self.knowledge_graph.nodes.get(node_id)
                path_names.append(node.name if node else node_id)

            formatted_path = " → ".join(f"**{n}**" for n in path_names)
            return (f"*Ohren aufgestellt* Ich habe einen Pfad gefunden!\n\n"
                   f"🔗 {formatted_path}\n\n"
                   f"*{len(path)-1} Schritte verbinden diese Themen!*")

        return (f"*nachdenklich* Ich finde keinen direkten Pfad zwischen "
               f"'{topic_a}' und '{topic_b}'... aber vielleicht gibt es einen?")

    def get_wolf_wisdom(self) -> str:
        """Hole eine weise Wolfs-Einsicht basierend auf dem Wissensgraph."""
        # Wähle zufällige Verbindung
        if not self.knowledge_graph.edges:
            return "*weise* Wissen ist wie der Mond - es beleuchtet die Dunkelheit."

        edge = random.choice(self.knowledge_graph.edges)
        from_node = self.knowledge_graph.nodes.get(edge[0])
        to_node = self.knowledge_graph.nodes.get(edge[1])

        if from_node and to_node:
            wisdoms = [
                f"*Ohren aufmerksam* Wusstest du? **{from_node.name}** und **{to_node.name}** sind verbunden durch '{edge[2]}'.",
                f"*nachdenklich* Die Verbindung zwischen **{from_node.name}** und **{to_node.name}** zeigt uns, wie alles zusammenhängt.",
                f"*weise nickend* **{from_node.name}** führt zu **{to_node.name}** - ein interessanter Gedankenpfad!",
            ]
            return random.choice(wisdoms)

        return "*weise* Jedes Stück Wissen ist ein Schritt auf dem Weg zur Weisheit."


# =============================================================================
# SINGLETON & FACTORY
# =============================================================================

_integration_instance: Optional[HoloLearningIntegration] = None


def get_learning_integration() -> HoloLearningIntegration:
    """Gibt die Singleton-Instanz zurück."""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = HoloLearningIntegration()
    return _integration_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    integration = get_learning_integration()

    print("=== LEARNING INTEGRATION TEST ===\n")

    # Profil erstellen
    profile = LearnerProfile(
        name="Test-Lerner",
        interests={"Anime": 4, "Japan": 3, "Gaming": 4}
    )
    integration.set_profile(profile)

    print("[Lernsession starten]")
    print(integration.start_learning_session(mood="curious", time_available=20))

    print("\n" + "="*60 + "\n")

    print("[Thema erkunden: Anime]")
    print(integration.explore_topic("Anime"))

    print("\n" + "="*60 + "\n")

    print("[Verbindung finden: Wölfe -> Musik]")
    print(integration.find_connection("Wölfe", "Musik"))

    print("\n" + "="*60 + "\n")

    print("[Wolfs-Weisheit]")
    print(integration.get_wolf_wisdom())
