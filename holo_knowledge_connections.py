"""
HOLO KNOWLEDGE CONNECTIONS SYSTEM
==================================

Ein intelligentes System zur Vernetzung von Wissen.
Verbindet verschiedene Wissensbereiche und zeigt überraschende Zusammenhänge.

Wie Holos weiser Wolfsverstand arbeitet - alles ist miteinander verbunden!
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# VERBINDUNGSTYPEN
# =============================================================================

class ConnectionType(Enum):
    """Arten von Wissensverbindungen"""
    DIRECT = "direkt"              # Direkte Verbindung (A erwähnt B)
    THEMATIC = "thematisch"        # Gemeinsames Thema
    HISTORICAL = "historisch"      # Zeitliche Verbindung
    CULTURAL = "kulturell"         # Kulturelle Brücke
    CAUSAL = "kausal"              # Ursache-Wirkung
    ANALOGY = "analogie"           # Ähnlichkeit/Metapher
    CONTRAST = "kontrast"          # Gegensatz zeigt Unterschied
    INSPIRATION = "inspiration"    # Hat inspiriert
    ORIGIN = "ursprung"            # Stammt von ab


@dataclass
class KnowledgeNode:
    """Ein Knoten im Wissensnetz"""
    id: str
    name: str
    domain: str  # z.B. "Anime", "Geschichte", "Wissenschaft"
    keywords: List[str] = field(default_factory=list)
    related_nodes: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class KnowledgeConnection:
    """Eine Verbindung zwischen zwei Wissensknoten"""
    node_a: str
    node_b: str
    connection_type: ConnectionType
    description: str
    strength: float = 1.0  # 0.0-1.0, wie stark die Verbindung ist
    fun_fact: str = ""     # Interessante Info über die Verbindung
    wolf_comment: str = "" # Holos Kommentar zur Verbindung


# =============================================================================
# VORDEFINIERTE VERBINDUNGEN
# =============================================================================

PREDEFINED_CONNECTIONS = [
    # Anime <-> Geschichte
    KnowledgeConnection(
        node_a="Spice and Wolf",
        node_b="Mittelalterlicher Handel",
        connection_type=ConnectionType.THEMATIC,
        description="Spice and Wolf zeigt akkurate mittelalterliche Wirtschaftskonzepte",
        strength=0.9,
        fun_fact="Die Währungsmanipulation im Anime basiert auf echten historischen Ereignissen",
        wolf_comment="*stolz* Meine Geschichte lehrt echte Wirtschaft!"
    ),
    KnowledgeConnection(
        node_a="Attack on Titan",
        node_b="Mauerbau der Geschichte",
        connection_type=ConnectionType.THEMATIC,
        description="Die Mauern erinnern an historische Festungen und die Berliner Mauer",
        strength=0.7,
        fun_fact="Autor Isayama war von mittelalterlichen Befestigungen inspiriert",
        wolf_comment="Mauern trennen... und beschützen gleichzeitig."
    ),
    KnowledgeConnection(
        node_a="Samurai",
        node_b="Bushido",
        connection_type=ConnectionType.CULTURAL,
        description="Der Ehrenkodex der Samurai - Loyalität, Mut, Ehre",
        strength=1.0,
        fun_fact="Viele Anime-Charaktere folgen modernen Interpretationen von Bushido",
        wolf_comment="Loyalität... auch ich verstehe das gut."
    ),

    # Technologie <-> Anime
    KnowledgeConnection(
        node_a="Künstliche Intelligenz",
        node_b="Ghost in the Shell",
        connection_type=ConnectionType.INSPIRATION,
        description="Ghost in the Shell beeinflusste echte KI-Forscher und Philosophen",
        strength=0.85,
        fun_fact="Die Matrix-Regisseure zeigten GitS als Inspiration",
        wolf_comment="Was macht eine Seele aus? Auch ich frage mich das..."
    ),
    KnowledgeConnection(
        node_a="Mecha Anime",
        node_b="Robotik",
        connection_type=ConnectionType.INSPIRATION,
        description="Japanische Robotik wurde stark von Mecha-Anime inspiriert",
        strength=0.8,
        fun_fact="Ingenieure bei Honda sagten, Gundam inspirierte sie zu ASIMO",
        wolf_comment="*staunt* Fantasie wird Realität!"
    ),
    KnowledgeConnection(
        node_a="Vocaloid",
        node_b="KI-Musik",
        connection_type=ConnectionType.ORIGIN,
        description="Vocaloid war einer der ersten kommerziell erfolgreichen KI-Musikgeneratoren",
        strength=0.9,
        fun_fact="Hatsune Miku ist eine virtuelle Künstlerin mit echten Konzerten",
        wolf_comment="Eine Stimme ohne Körper... faszinierend!"
    ),

    # Natur <-> Kultur
    KnowledgeConnection(
        node_a="Kirschblüte",
        node_b="Japanische Philosophie",
        connection_type=ConnectionType.CULTURAL,
        description="Sakura symbolisiert Vergänglichkeit (Mono no Aware)",
        strength=0.95,
        fun_fact="Hanami (Kirschblütenschauen) gibt es seit über 1000 Jahren",
        wolf_comment="*seufzt* Schönheit liegt in der Vergänglichkeit..."
    ),
    KnowledgeConnection(
        node_a="Wolf",
        node_b="Shintoismus",
        connection_type=ConnectionType.CULTURAL,
        description="Wölfe galten in Japan als göttliche Boten (Ōkami)",
        strength=0.9,
        fun_fact="Das Wort für Wolf (Ōkami) klingt wie das Wort für großer Gott",
        wolf_comment="*Ohren aufstellen* Natürlich sind wir göttlich!"
    ),
    KnowledgeConnection(
        node_a="Vollmond",
        node_b="Werwolf-Mythen",
        connection_type=ConnectionType.THEMATIC,
        description="Weltweit verbinden Menschen den Mond mit Wölfen",
        strength=0.85,
        fun_fact="Wissenschaftlich gibt es keine Verbindung - aber emotional schon",
        wolf_comment="*schaut zum Mond* Er ruft mich trotzdem..."
    ),

    # Wissenschaft <-> Anime
    KnowledgeConnection(
        node_a="Zeitreise",
        node_b="Steins;Gate",
        connection_type=ConnectionType.THEMATIC,
        description="Steins;Gate nutzt echte Zeitreisetheorien als Grundlage",
        strength=0.8,
        fun_fact="Die Mikrowellen-Zeitmaschine basiert lose auf dem Titor-Mythos",
        wolf_comment="Zeitreisen... kompliziert, aber spannend!"
    ),
    KnowledgeConnection(
        node_a="Psychologie",
        node_b="Neon Genesis Evangelion",
        connection_type=ConnectionType.THEMATIC,
        description="EVA erforscht psychologische Konzepte wie Depression und Trauma",
        strength=0.85,
        fun_fact="Anno litt während der Produktion an Depressionen",
        wolf_comment="Manchmal hilft es, schwere Themen durch Kunst zu verarbeiten."
    ),

    # Gaming <-> Kultur
    KnowledgeConnection(
        node_a="Dark Souls",
        node_b="Mittelalterliche Architektur",
        connection_type=ConnectionType.INSPIRATION,
        description="FromSoftware-Spiele sind von europäischer Gotik inspiriert",
        strength=0.8,
        fun_fact="Miyazaki besuchte echte Burgen für Design-Inspiration",
        wolf_comment="Die Ruinen erzählen Geschichten..."
    ),
    KnowledgeConnection(
        node_a="Visual Novels",
        node_b="Literatur",
        connection_type=ConnectionType.ORIGIN,
        description="Visual Novels sind interaktive Romane mit Bildern",
        strength=0.9,
        fun_fact="Viele berühmte Anime wie Fate basieren auf Visual Novels",
        wolf_comment="Geschichten, die DU mitbestimmst - wunderbar!"
    ),

    # Musik <-> Emotion
    KnowledgeConnection(
        node_a="Anime-Openings",
        node_b="Nostalgie",
        connection_type=ConnectionType.CAUSAL,
        description="Anime-Songs lösen starke nostalgische Gefühle aus",
        strength=0.95,
        fun_fact="Das Gehirn verbindet Musik stark mit Erinnerungen",
        wolf_comment="*summt leise* Ein Song kann Jahre zurückbringen..."
    ),
    KnowledgeConnection(
        node_a="J-Pop",
        node_b="Kawaii-Kultur",
        connection_type=ConnectionType.CULTURAL,
        description="J-Pop verkörpert oft die 'Cute'-Ästhetik Japans",
        strength=0.75,
        fun_fact="Idol-Gruppen wie AKB48 haben hunderte Mitglieder",
        wolf_comment="Kawaii ist eine Kunstform!"
    ),

    # Sprache <-> Anime
    KnowledgeConnection(
        node_a="Keigo (Höflichkeitssprache)",
        node_b="Anime-Charakterisierung",
        connection_type=ConnectionType.THEMATIC,
        description="Wie ein Charakter spricht zeigt sofort Status und Persönlichkeit",
        strength=0.85,
        fun_fact="Japanische Fans erkennen sofort 'Ojou-sama' oder 'Yankee' Sprechstile",
        wolf_comment="Sprache verrät viel über eine Person!"
    ),

    # Überraschende Verbindungen
    KnowledgeConnection(
        node_a="Origami",
        node_b="Raumfahrt",
        connection_type=ConnectionType.INSPIRATION,
        description="NASA nutzt Origami-Faltmuster für Solarpanels",
        strength=0.7,
        fun_fact="Alte japanische Kunst löst moderne Engineering-Probleme",
        wolf_comment="*erstaunt* Alte Weisheit in neuer Form!"
    ),
    KnowledgeConnection(
        node_a="Bienen-Kommunikation",
        node_b="Informationstheorie",
        connection_type=ConnectionType.ANALOGY,
        description="Der Bienentanz ist eine Form von 'Programmierung' in der Natur",
        strength=0.65,
        fun_fact="Karl von Frisch entschlüsselte den Code und gewann einen Nobelpreis",
        wolf_comment="Selbst kleine Wesen haben komplexe Sprachen!"
    ),
]


# =============================================================================
# KNOWLEDGE WEB
# =============================================================================

class KnowledgeWeb:
    """
    Ein vernetztes Wissenssystem.

    Verbindet verschiedene Wissensbereiche und zeigt überraschende
    Zusammenhänge - wie Holos weise Wolfsgedanken.
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.connections: List[KnowledgeConnection] = []
        self.keyword_index: Dict[str, Set[str]] = {}  # keyword -> set of node_ids

        self._initialize()
        logger.info(f"KnowledgeWeb: {len(self.nodes)} Knoten, {len(self.connections)} Verbindungen")

    def _initialize(self):
        """Lade vordefinierte Verbindungen und erstelle Knoten."""
        # Automatisch Knoten aus Verbindungen erstellen
        for conn in PREDEFINED_CONNECTIONS:
            self._ensure_node_exists(conn.node_a)
            self._ensure_node_exists(conn.node_b)
            self.connections.append(conn)

        # Zusätzliche Knoten für wichtige Konzepte
        self._add_core_nodes()

    def _ensure_node_exists(self, name: str):
        """Stelle sicher dass ein Knoten existiert."""
        node_id = name.lower().replace(" ", "_")
        if node_id not in self.nodes:
            self.nodes[node_id] = KnowledgeNode(
                id=node_id,
                name=name,
                domain=self._guess_domain(name),
                keywords=[w.lower() for w in name.split()]
            )
            # Index aktualisieren
            for keyword in self.nodes[node_id].keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = set()
                self.keyword_index[keyword].add(node_id)

    def _guess_domain(self, name: str) -> str:
        """Rate die Domain eines Knotens."""
        name_lower = name.lower()

        domain_keywords = {
            "Anime": ["anime", "manga", "otaku", "jjk", "demon", "attack", "spice", "wolf"],
            "Gaming": ["game", "dark souls", "elden", "nintendo", "visual novel"],
            "Wissenschaft": ["ki", "psychologie", "zeitreise", "physik", "theorie"],
            "Natur": ["wolf", "mond", "kirsch", "biene", "natur"],
            "Geschichte": ["samurai", "mittelalter", "mauer", "handel", "bushido"],
            "Kultur": ["japan", "kawaii", "shinto", "origami", "kultur"],
            "Musik": ["j-pop", "music", "song", "opening", "vocaloid"],
            "Sprache": ["keigo", "sprache", "wort"],
            "Technologie": ["robotik", "mecha", "ai", "künstlich"],
        }

        for domain, keywords in domain_keywords.items():
            if any(kw in name_lower for kw in keywords):
                return domain

        return "Allgemein"

    def _add_core_nodes(self):
        """Füge wichtige Kernkonzepte als Knoten hinzu."""
        core_concepts = [
            ("Japan", "Kultur", ["japan", "nippon", "nihon"]),
            ("Anime", "Medien", ["anime", "animation", "zeichentrick"]),
            ("Wissen", "Philosophie", ["lernen", "wissen", "verstehen"]),
            ("Wolf", "Natur", ["wolf", "wölfin", "rudel", "heulen"]),
            ("Emotionen", "Psychologie", ["gefühl", "emotion", "herz"]),
            ("Freundschaft", "Beziehungen", ["freund", "verbindung", "zusammen"]),
            ("Weisheit", "Philosophie", ["weise", "klug", "erfahrung"]),
        ]

        for name, domain, keywords in core_concepts:
            node_id = name.lower()
            if node_id not in self.nodes:
                self.nodes[node_id] = KnowledgeNode(
                    id=node_id,
                    name=name,
                    domain=domain,
                    keywords=keywords
                )
                for kw in keywords:
                    if kw not in self.keyword_index:
                        self.keyword_index[kw] = set()
                    self.keyword_index[kw].add(node_id)

    # =========================================================================
    # ABFRAGE-METHODEN
    # =========================================================================

    def find_connections(self, topic: str) -> List[KnowledgeConnection]:
        """
        Finde alle Verbindungen zu einem Thema.

        Args:
            topic: Das Thema zum Suchen

        Returns:
            Liste von Verbindungen
        """
        topic_lower = topic.lower()
        results = []

        for conn in self.connections:
            if (topic_lower in conn.node_a.lower() or
                topic_lower in conn.node_b.lower() or
                topic_lower in conn.description.lower()):
                results.append(conn)

        return results

    def get_random_connection(self, domain: Optional[str] = None) -> Optional[KnowledgeConnection]:
        """
        Hole eine zufällige interessante Verbindung.

        Args:
            domain: Optional - nur Verbindungen aus dieser Domain

        Returns:
            Eine zufällige Verbindung
        """
        if domain:
            domain_lower = domain.lower()
            filtered = [c for c in self.connections
                       if domain_lower in self._guess_domain(c.node_a).lower() or
                          domain_lower in self._guess_domain(c.node_b).lower()]
            if filtered:
                return random.choice(filtered)

        if self.connections:
            return random.choice(self.connections)
        return None

    def get_surprising_connection(self) -> Optional[KnowledgeConnection]:
        """
        Hole eine besonders überraschende Verbindung.

        Returns:
            Eine unerwartete Verbindung
        """
        # Verbindungen die unterschiedliche Domains verbinden sind überraschender
        cross_domain = [c for c in self.connections
                       if self._guess_domain(c.node_a) != self._guess_domain(c.node_b)]

        if cross_domain:
            return random.choice(cross_domain)
        return self.get_random_connection()

    def trace_path(self, start: str, end: str, max_hops: int = 4) -> Optional[List[str]]:
        """
        Finde einen Pfad zwischen zwei Konzepten.

        Args:
            start: Startkonzept
            end: Zielkonzept
            max_hops: Maximale Anzahl von Schritten

        Returns:
            Liste von Konzepten oder None
        """
        start_lower = start.lower()
        end_lower = end.lower()

        # Build adjacency from connections
        adjacency: Dict[str, Set[str]] = {}
        for conn in self.connections:
            a = conn.node_a.lower()
            b = conn.node_b.lower()
            if a not in adjacency:
                adjacency[a] = set()
            if b not in adjacency:
                adjacency[b] = set()
            adjacency[a].add(b)
            adjacency[b].add(a)

        # BFS
        from collections import deque
        queue = deque([(start_lower, [start])])
        visited = {start_lower}

        while queue:
            current, path = queue.popleft()

            if len(path) > max_hops:
                continue

            if current == end_lower or end_lower in current:
                return path

            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    # =========================================================================
    # FORMATIERUNG
    # =========================================================================

    def format_connection(self, conn: KnowledgeConnection, style: str = "full") -> str:
        """
        Formatiere eine Verbindung für die Ausgabe.

        Args:
            conn: Die Verbindung
            style: "full", "short", oder "wolf"
        """
        if style == "short":
            return f"**{conn.node_a}** ↔ **{conn.node_b}**: {conn.description}"

        elif style == "wolf":
            parts = [
                f"*Ohren aufmerksam* Eine interessante Verbindung...",
                f"",
                f"**{conn.node_a}** 🔗 **{conn.node_b}**",
                f"",
                f"{conn.description}",
            ]
            if conn.fun_fact:
                parts.append(f"")
                parts.append(f"💡 {conn.fun_fact}")
            if conn.wolf_comment:
                parts.append(f"")
                parts.append(f"*{conn.wolf_comment}*")
            return "\n".join(parts)

        else:  # full
            parts = [
                f"### {conn.node_a} ↔ {conn.node_b}",
                f"",
                f"**Verbindungsart:** {conn.connection_type.value}",
                f"**Stärke:** {'●' * int(conn.strength * 5)}{'○' * (5 - int(conn.strength * 5))}",
                f"",
                f"{conn.description}",
            ]
            if conn.fun_fact:
                parts.append(f"")
                parts.append(f"💡 **Fun Fact:** {conn.fun_fact}")
            if conn.wolf_comment:
                parts.append(f"")
                parts.append(f"🐺 *{conn.wolf_comment}*")
            return "\n".join(parts)

    def format_path(self, path: List[str]) -> str:
        """Formatiere einen Wissenspfad."""
        if not path:
            return "Kein Pfad gefunden..."

        formatted = " → ".join(f"**{p}**" for p in path)
        return f"🔍 Wissenspfad: {formatted}"

    # =========================================================================
    # WISSENSBRÜCKEN
    # =========================================================================

    def build_bridge(self, topic_a: str, topic_b: str) -> str:
        """
        Baue eine Brücke zwischen zwei scheinbar unverbundenen Themen.

        Args:
            topic_a: Erstes Thema
            topic_b: Zweites Thema

        Returns:
            Erklärungstext wie die Themen verbunden sind
        """
        # Suche direkten Pfad
        path = self.trace_path(topic_a, topic_b)

        if path:
            intro = f"*Ohren aufgestellt* Da ist eine Verbindung!\n\n"
            return intro + self.format_path(path)

        # Wenn kein Pfad, improvisiere eine Brücke
        connections_a = self.find_connections(topic_a)
        connections_b = self.find_connections(topic_b)

        if connections_a and connections_b:
            conn_a = random.choice(connections_a)
            conn_b = random.choice(connections_b)
            return (f"*nachdenklich* Hmm, direkt verbunden sind sie nicht, aber...\n\n"
                   f"**{topic_a}** ist verbunden mit {conn_a.node_b}\n"
                   f"**{topic_b}** ist verbunden mit {conn_b.node_b}\n\n"
                   f"Vielleicht ist das der Anfang eines interessanten Gedankens?")

        return f"*Ohren angelegt* Diese Themen scheinen noch nicht in meinem Wissensnetz verbunden zu sein..."


# =============================================================================
# WISDOM GENERATOR
# =============================================================================

class WisdomGenerator:
    """
    Generiert weise Einsichten basierend auf Wissensverbindungen.

    Wie Holos alte Wolfsweisheit - sieht Muster wo andere keine sehen.
    """

    def __init__(self, web: KnowledgeWeb):
        self.web = web
        self.wisdom_templates = [
            "Wusstest du, dass {a} und {b} verbunden sind? {desc}",
            "*Ohren aufmerksam* Es gibt eine interessante Verbindung zwischen {a} und {b}...",
            "Hier ist etwas Weises: {a} lehrt uns über {b}. {desc}",
            "*nachdenklich* Alles ist verbunden... {a} und {b} zum Beispiel. {desc}",
            "Ein kluger Wolf sieht Muster: {a} ↔ {b}. {desc}",
        ]

        self.deep_thoughts = [
            "Wissen ist wie ein Spinnennetz - alles hängt zusammen.",
            "Die interessantesten Erkenntnisse liegen an den Grenzen zwischen Themen.",
            "Je mehr man lernt, desto mehr Verbindungen sieht man.",
            "Weisheit bedeutet, die unsichtbaren Fäden zu erkennen.",
            "Das Universum ist ein einziges großes Netzwerk.",
            "Neugier ist der erste Schritt zur Weisheit.",
            "Überraschende Verbindungen lehren uns am meisten.",
        ]

    def generate_wisdom(self) -> str:
        """Generiere einen weisen Spruch basierend auf Verbindungen."""
        conn = self.web.get_surprising_connection()

        if conn:
            template = random.choice(self.wisdom_templates)
            return template.format(
                a=conn.node_a,
                b=conn.node_b,
                desc=conn.description
            )

        return f"*nachdenklich* {random.choice(self.deep_thoughts)}"

    def generate_daily_insight(self) -> str:
        """Generiere eine tägliche Weisheit."""
        conn = self.web.get_random_connection()
        deep = random.choice(self.deep_thoughts)

        parts = [
            "📚 **Tägliche Weisheit**",
            "",
        ]

        if conn:
            parts.append(self.web.format_connection(conn, style="wolf"))
            parts.append("")

        parts.append(f"*{deep}*")

        return "\n".join(parts)

    def explore_topic(self, topic: str) -> str:
        """
        Erkunde ein Thema und zeige seine Verbindungen.

        Args:
            topic: Das Thema zum Erkunden

        Returns:
            Formatierter Erkundungsbericht
        """
        connections = self.web.find_connections(topic)

        if not connections:
            return f"*Ohren angelegt* Ich habe noch keine Verbindungen zu '{topic}' in meinem Wissensnetz..."

        parts = [
            f"🔍 **Erkundung: {topic}**",
            "",
            f"Ich habe {len(connections)} Verbindung(en) gefunden:",
            "",
        ]

        for conn in connections[:5]:  # Maximal 5 anzeigen
            other = conn.node_b if topic.lower() in conn.node_a.lower() else conn.node_a
            parts.append(f"• **{other}** ({conn.connection_type.value})")
            parts.append(f"  {conn.description}")
            if conn.fun_fact:
                parts.append(f"  💡 {conn.fun_fact}")
            parts.append("")

        if len(connections) > 5:
            parts.append(f"...und {len(connections) - 5} weitere Verbindungen!")

        return "\n".join(parts)


# =============================================================================
# SINGLETON & FACTORY
# =============================================================================

_knowledge_web_instance: Optional[KnowledgeWeb] = None
_wisdom_generator_instance: Optional[WisdomGenerator] = None


def get_knowledge_web() -> KnowledgeWeb:
    """Gibt die Singleton-Instanz des KnowledgeWeb zurück."""
    global _knowledge_web_instance
    if _knowledge_web_instance is None:
        _knowledge_web_instance = KnowledgeWeb()
    return _knowledge_web_instance


def get_wisdom_generator() -> WisdomGenerator:
    """Gibt die Singleton-Instanz des WisdomGenerator zurück."""
    global _wisdom_generator_instance
    if _wisdom_generator_instance is None:
        _wisdom_generator_instance = WisdomGenerator(get_knowledge_web())
    return _wisdom_generator_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    web = get_knowledge_web()
    wisdom = get_wisdom_generator()

    print("=== KNOWLEDGE WEB TEST ===\n")

    print("[Zufällige Verbindung]")
    conn = web.get_random_connection()
    if conn:
        print(web.format_connection(conn, style="wolf"))

    print("\n" + "="*50 + "\n")

    print("[Überraschende Verbindung]")
    surprise = web.get_surprising_connection()
    if surprise:
        print(web.format_connection(surprise, style="full"))

    print("\n" + "="*50 + "\n")

    print("[Thema erkunden: Anime]")
    print(wisdom.explore_topic("Anime"))

    print("\n" + "="*50 + "\n")

    print("[Tägliche Weisheit]")
    print(wisdom.generate_daily_insight())

    print("\n" + "="*50 + "\n")

    print("[Pfad suchen: Wolf -> Technologie]")
    path = web.trace_path("Wolf", "Robotik")
    print(web.format_path(path) if path else "Kein Pfad gefunden")
