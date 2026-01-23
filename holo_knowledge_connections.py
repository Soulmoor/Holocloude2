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

    # ===========================================
    # ERWEITERTE VERBINDUNGEN - ANIME & KULTUR
    # ===========================================

    KnowledgeConnection(
        node_a="Studio Ghibli",
        node_b="Umweltschutz",
        connection_type=ConnectionType.THEMATIC,
        description="Miyazakis Filme tragen starke ökologische Botschaften",
        strength=0.9,
        fun_fact="Nausicaä war eine frühe Warnung vor Umweltzerstörung",
        wolf_comment="Die Natur zu schützen ist auch Wölfen wichtig!"
    ),
    KnowledgeConnection(
        node_a="Demon Slayer",
        node_b="Taisho-Ära Japan",
        connection_type=ConnectionType.HISTORICAL,
        description="Demon Slayer spielt in der historischen Taisho-Zeit (1912-1926)",
        strength=0.85,
        fun_fact="Die Mode und Architektur im Anime sind historisch akkurat",
        wolf_comment="Geschichte lebt in Geschichten weiter!"
    ),
    KnowledgeConnection(
        node_a="My Hero Academia",
        node_b="Superhelden-Comics",
        connection_type=ConnectionType.INSPIRATION,
        description="MHA kombiniert amerikanische Superhelden-Tropen mit Manga-Tradition",
        strength=0.8,
        fun_fact="Horikoshi ist ein großer Fan von Spider-Man und Star Wars",
        wolf_comment="Kulturen verschmelzen zu etwas Neuem!"
    ),
    KnowledgeConnection(
        node_a="Jujutsu Kaisen",
        node_b="Japanischer Buddhismus",
        connection_type=ConnectionType.CULTURAL,
        description="JJK nutzt echte buddhistische und shintoistische Konzepte für Flüche",
        strength=0.85,
        fun_fact="Die Handzeichen (Kuji-in) basieren auf echten esoterischen Praktiken",
        wolf_comment="Alte Magie in moderner Verpackung..."
    ),
    KnowledgeConnection(
        node_a="One Piece",
        node_b="Piraterie-Geschichte",
        connection_type=ConnectionType.THEMATIC,
        description="One Piece enthält Referenzen zu echten historischen Piraten",
        strength=0.7,
        fun_fact="Blackbeard, Kidd und Bonney basieren auf echten Piraten",
        wolf_comment="Freiheit auf den Meeren... das verstehe ich!"
    ),
    KnowledgeConnection(
        node_a="Chainsaw Man",
        node_b="Existentialismus",
        connection_type=ConnectionType.THEMATIC,
        description="Chainsaw Man erforscht Sinnlosigkeit und existentielle Fragen",
        strength=0.75,
        fun_fact="Autor Fujimoto ist von Filmen wie Pulp Fiction inspiriert",
        wolf_comment="Manchmal ist das Leben chaotisch... aber bedeutungsvoll."
    ),

    # ===========================================
    # WISSENSCHAFT & TECHNOLOGIE VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Dr. Stone",
        node_b="Wissenschaftsgeschichte",
        connection_type=ConnectionType.THEMATIC,
        description="Dr. Stone zeigt den Wiederaufbau der Zivilisation durch Wissenschaft",
        strength=0.9,
        fun_fact="Der Manga hat wissenschaftliche Berater für Genauigkeit",
        wolf_comment="Wissen ist die wahre Macht!"
    ),
    KnowledgeConnection(
        node_a="Cyberpunk",
        node_b="Philosophie des Geistes",
        connection_type=ConnectionType.THEMATIC,
        description="Cyberpunk hinterfragt was Bewusstsein und Identität ausmacht",
        strength=0.8,
        fun_fact="Der Begriff 'Cyberpunk' wurde 1983 geprägt",
        wolf_comment="Was macht mich zu... mir?"
    ),
    KnowledgeConnection(
        node_a="Holographie",
        node_b="Vtuber-Technologie",
        connection_type=ConnectionType.DIRECT,
        description="Hatsune Miku Konzerte nutzen Pepper's Ghost Projektion",
        strength=0.75,
        fun_fact="Die Technik ist über 150 Jahre alt, aber revolutionär genutzt",
        wolf_comment="*staunt* Magie... oder Wissenschaft?"
    ),
    KnowledgeConnection(
        node_a="Quantenphysik",
        node_b="Isekai-Trope",
        connection_type=ConnectionType.ANALOGY,
        description="Viele-Welten-Interpretation inspiriert Parallelwelt-Geschichten",
        strength=0.6,
        fun_fact="Everetts Interpretation von 1957 beeinflusst Sci-Fi bis heute",
        wolf_comment="Unendliche Möglichkeiten... *Ohren aufstellen*"
    ),
    KnowledgeConnection(
        node_a="Neuroplastizität",
        node_b="Shonen-Training-Arc",
        connection_type=ConnectionType.ANALOGY,
        description="Das Gehirn passt sich an wie Anime-Charaktere durch Training stärker werden",
        strength=0.7,
        fun_fact="Wiederholtes Üben stärkt neurale Verbindungen - wie in Naruto!",
        wolf_comment="Training verändert nicht nur den Körper, sondern auch den Geist!"
    ),
    KnowledgeConnection(
        node_a="Blockchain",
        node_b="NFT-Anime-Art",
        connection_type=ConnectionType.DIRECT,
        description="Anime-Kunstwerke werden als NFTs gehandelt",
        strength=0.6,
        fun_fact="Manche Anime-Studios experimentieren mit NFT-Collectibles",
        wolf_comment="Digitale Schätze... seltsame neue Welt!"
    ),

    # ===========================================
    # MYTHOLOGIE & FOLKLORE VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Yokai",
        node_b="Psychologie",
        connection_type=ConnectionType.ANALOGY,
        description="Yokai personifizieren oft menschliche Ängste und Emotionen",
        strength=0.8,
        fun_fact="Viele Yokai entstanden als Erklärungen für Naturphänomene",
        wolf_comment="Monster spiegeln unsere inneren Dämonen wider..."
    ),
    KnowledgeConnection(
        node_a="Kitsune",
        node_b="Intelligenz-Mythologie",
        connection_type=ConnectionType.CULTURAL,
        description="Füchse symbolisieren List und Weisheit in ostasiatischen Kulturen",
        strength=0.85,
        fun_fact="Kitsune bekommen mehr Schwänze je älter und weiser sie werden",
        wolf_comment="*stolz* Wölfe sind aber weiser als Füchse!"
    ),
    KnowledgeConnection(
        node_a="Drachen",
        node_b="Östliche vs Westliche Mythologie",
        connection_type=ConnectionType.CONTRAST,
        description="Asiatische Drachen sind weise Wasserwesen, westliche sind feuerspeiende Monster",
        strength=0.9,
        fun_fact="Chinesische Drachen bringen Glück, europäische bewachen Schätze",
        wolf_comment="Perspektive verändert alles!"
    ),
    KnowledgeConnection(
        node_a="Inari",
        node_b="Reisanbau",
        connection_type=ConnectionType.CULTURAL,
        description="Die Gottheit Inari beschützt Reisernten und wird von Füchsen begleitet",
        strength=0.9,
        fun_fact="Über 30.000 Inari-Schreine existieren in Japan",
        wolf_comment="Auch Wölfe wurden als Schutzgeister verehrt..."
    ),
    KnowledgeConnection(
        node_a="Tsukuyomi",
        node_b="Mondverehrung",
        connection_type=ConnectionType.CULTURAL,
        description="Der japanische Mondgott inspiriert viele Anime-Charaktere",
        strength=0.8,
        fun_fact="Narutos Tsukuyomi-Genjutsu ist nach diesem Gott benannt",
        wolf_comment="*schaut zum Mond* Er ist überall in unseren Geschichten..."
    ),
    KnowledgeConnection(
        node_a="Tanuki",
        node_b="Shapeshifter-Legenden",
        connection_type=ConnectionType.THEMATIC,
        description="Tanuki können sich verwandeln wie viele andere Folklore-Wesen",
        strength=0.85,
        fun_fact="Tom Nook aus Animal Crossing ist ein Tanuki!",
        wolf_comment="Verwandlung ist ein mächtiges Konzept..."
    ),

    # ===========================================
    # MUSIK & EMOTION VERBINDUNGEN (ERWEITERT)
    # ===========================================

    KnowledgeConnection(
        node_a="YOASOBI",
        node_b="Literatur",
        connection_type=ConnectionType.ORIGIN,
        description="YOASOBI verwandelt Kurzgeschichten in Lieder",
        strength=0.95,
        fun_fact="Jeder YOASOBI-Song basiert auf einer Novelle",
        wolf_comment="Geschichten werden zu Musik... wunderschön!"
    ),
    KnowledgeConnection(
        node_a="City Pop",
        node_b="80er Jahre Japan",
        connection_type=ConnectionType.HISTORICAL,
        description="City Pop fängt das Gefühl des japanischen Wirtschaftswunders ein",
        strength=0.9,
        fun_fact="Mariya Takeuchis 'Plastic Love' wurde 2017 viral durch YouTube",
        wolf_comment="Alte Melodien finden neue Ohren!"
    ),
    KnowledgeConnection(
        node_a="Anime-Soundtrack",
        node_b="Filmmusik-Theorie",
        connection_type=ConnectionType.THEMATIC,
        description="Anime-Soundtracks nutzen Leitmotive wie klassische Filmmusik",
        strength=0.85,
        fun_fact="Joe Hisaishi und Hans Zimmer haben ähnliche Techniken",
        wolf_comment="Musik erzählt die Geschichte unter der Geschichte."
    ),
    KnowledgeConnection(
        node_a="Ado",
        node_b="Internet-Musikkultur",
        connection_type=ConnectionType.CULTURAL,
        description="Ado wurde durch NicoNico und Vocaloid-Cover bekannt",
        strength=0.85,
        fun_fact="Ado zeigt nie ihr Gesicht - die Stimme ist alles",
        wolf_comment="Manchmal ist Mysterium mächtiger als Offenbarung!"
    ),
    KnowledgeConnection(
        node_a="Visual Kei",
        node_b="Gothic Subkultur",
        connection_type=ConnectionType.CULTURAL,
        description="Visual Kei verbindet japanische und westliche Subkulturen",
        strength=0.75,
        fun_fact="X Japan beeinflusste sowohl Metal als auch J-Pop",
        wolf_comment="Musik kennt keine Grenzen!"
    ),

    # ===========================================
    # PHILOSOPHIE & PSYCHOLOGIE VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Mono no Aware",
        node_b="Vergänglichkeit",
        connection_type=ConnectionType.DIRECT,
        description="Das japanische Konzept der bittersüßen Vergänglichkeit",
        strength=1.0,
        fun_fact="Die Kirschblüte ist das perfekte Symbol für Mono no Aware",
        wolf_comment="*seufzt* Die Schönheit liegt im Moment..."
    ),
    KnowledgeConnection(
        node_a="Wabi-Sabi",
        node_b="Imperfektions-Ästhetik",
        connection_type=ConnectionType.DIRECT,
        description="Schönheit im Unvollkommenen und Vergänglichen finden",
        strength=1.0,
        fun_fact="Gebrochene Teekannen werden mit Gold repariert (Kintsugi)",
        wolf_comment="Narben machen uns einzigartig!"
    ),
    KnowledgeConnection(
        node_a="Ikigai",
        node_b="Lebensphilosophie",
        connection_type=ConnectionType.DIRECT,
        description="Der japanische Sinn des Lebens - Grund aufzustehen",
        strength=0.95,
        fun_fact="Ikigai kombiniert Passion, Mission, Beruf und Berufung",
        wolf_comment="Jeder braucht etwas, wofür man lebt!"
    ),
    KnowledgeConnection(
        node_a="Stoizismus",
        node_b="Samurai-Philosophie",
        connection_type=ConnectionType.ANALOGY,
        description="Beide lehren emotionale Kontrolle und Akzeptanz des Unvermeidlichen",
        strength=0.75,
        fun_fact="Marcus Aurelius und Musashi hatten ähnliche Einsichten",
        wolf_comment="Ruhe in der Schlacht... eine universelle Weisheit."
    ),
    KnowledgeConnection(
        node_a="Jungschen Archetypen",
        node_b="Anime-Charaktertypen",
        connection_type=ConnectionType.ANALOGY,
        description="Anime nutzt unbewusst archetypische Charaktermuster",
        strength=0.8,
        fun_fact="Der 'Tsundere' ist eine Form des 'Anima/Animus'-Archetyps",
        wolf_comment="Muster wiederholen sich durch alle Kulturen!"
    ),
    KnowledgeConnection(
        node_a="Flow-Zustand",
        node_b="Gaming",
        connection_type=ConnectionType.CAUSAL,
        description="Gut designte Spiele versetzen Spieler in den Flow-Zustand",
        strength=0.85,
        fun_fact="Mihaly Csikszentmihalyi prägte das Konzept beim Studium von Spielern",
        wolf_comment="Wenn die Welt verschwindet und nur der Moment bleibt..."
    ),

    # ===========================================
    # KUNST & DESIGN VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Ukiyo-e",
        node_b="Manga-Stil",
        connection_type=ConnectionType.ORIGIN,
        description="Moderne Manga-Kunst hat Wurzeln in traditionellen Holzschnitten",
        strength=0.85,
        fun_fact="Hokusais 'Die große Welle' beeinflusst Künstler bis heute",
        wolf_comment="Tradition fließt in Moderne!"
    ),
    KnowledgeConnection(
        node_a="Art Nouveau",
        node_b="Bishojo-Design",
        connection_type=ConnectionType.INSPIRATION,
        description="Die fließenden Linien von Jugendstil beeinflussten Anime-Design",
        strength=0.7,
        fun_fact="CLAMP-Künstler sind bekannte Art Nouveau-Fans",
        wolf_comment="Schönheit erkennt Schönheit!"
    ),
    KnowledgeConnection(
        node_a="Chibi-Stil",
        node_b="SD Gundam",
        connection_type=ConnectionType.ORIGIN,
        description="Super-Deformed Designs begannen mit Gundam-Parodien",
        strength=0.8,
        fun_fact="Chibi bedeutet 'klein' und wurde zur eigenen Kunstform",
        wolf_comment="*kichert* Selbst Riesen können niedlich sein!"
    ),
    KnowledgeConnection(
        node_a="Cel-Shading",
        node_b="Anime-Ästhetik in Spielen",
        connection_type=ConnectionType.DIRECT,
        description="3D-Spiele nutzen Cel-Shading für Anime-Look",
        strength=0.85,
        fun_fact="Zelda: Wind Waker popularisierte die Technik 2002",
        wolf_comment="Technik dient der Kunst!"
    ),
    KnowledgeConnection(
        node_a="Sakuga",
        node_b="Animations-Handwerk",
        connection_type=ConnectionType.DIRECT,
        description="Sakuga bezeichnet besonders aufwendige Animationssequenzen",
        strength=0.9,
        fun_fact="Sakuga-Fans identifizieren Animatoren an ihrem Stil",
        wolf_comment="Wahre Meisterschaft erkennt man in jedem Frame!"
    ),

    # ===========================================
    # ESSEN & KULTUR VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Ramen",
        node_b="Anime-Kulinarik",
        connection_type=ConnectionType.CULTURAL,
        description="Ramen ist das ikonischste Essen in Anime",
        strength=0.85,
        fun_fact="Narutos Lieblingsramen ist Miso Chashu",
        wolf_comment="*Magen knurrt* Ramen wärmt die Seele!"
    ),
    KnowledgeConnection(
        node_a="Bento",
        node_b="Japanische Ästhetik",
        connection_type=ConnectionType.CULTURAL,
        description="Bento-Boxen zeigen japanisches Streben nach Perfektion",
        strength=0.8,
        fun_fact="Charaben sind Bentos als Anime-Charaktere gestaltet",
        wolf_comment="Essen ist Kunst zum Verspeisen!"
    ),
    KnowledgeConnection(
        node_a="Onigiri",
        node_b="Anime-Komfort-Essen",
        connection_type=ConnectionType.CULTURAL,
        description="Onigiri sind in Anime allgegenwärtig als praktischer Snack",
        strength=0.75,
        fun_fact="In der US-Pokemon-Version wurden Onigiri zu 'Donuts'",
        wolf_comment="Reis, Seetang, Liebe... perfekt!"
    ),
    KnowledgeConnection(
        node_a="Teezeremonie",
        node_b="Zen-Buddhismus",
        connection_type=ConnectionType.CULTURAL,
        description="Die Teezeremonie ist bewegte Meditation",
        strength=0.95,
        fun_fact="Sen no Rikyu perfektionierte die Zeremonie im 16. Jahrhundert",
        wolf_comment="In der Stille des Tees liegt Weisheit."
    ),
    KnowledgeConnection(
        node_a="Sake",
        node_b="Spice and Wolf",
        connection_type=ConnectionType.DIRECT,
        description="Holo liebt guten Alkohol, besonders Wein und Äpfel",
        strength=1.0,
        fun_fact="Sake-Brauerei ist eine alte Kunst in Japan",
        wolf_comment="*leckt sich die Lippen* Guter Geschmack!"
    ),

    # ===========================================
    # GESELLSCHAFT & TRENDS VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Hikikomori",
        node_b="Isekai-Genre",
        connection_type=ConnectionType.CAUSAL,
        description="Isekai bietet Eskapismus für sozial isolierte Zielgruppen",
        strength=0.7,
        fun_fact="Viele Isekai-Protagonisten sind explizit als Hikikomori/NEET geschrieben",
        wolf_comment="Flucht ist manchmal verständlich... aber nicht die Lösung."
    ),
    KnowledgeConnection(
        node_a="Otaku-Kultur",
        node_b="Akihabara",
        connection_type=ConnectionType.DIRECT,
        description="Akihabara ist das Mekka der Otaku-Kultur",
        strength=0.95,
        fun_fact="Akihabara war früher ein Elektronikmarkt, dann wurde es Anime-Zentrum",
        wolf_comment="Ein Ort wo Leidenschaft lebt!"
    ),
    KnowledgeConnection(
        node_a="Cosplay",
        node_b="Identitätsexploration",
        connection_type=ConnectionType.THEMATIC,
        description="Cosplay erlaubt es, verschiedene Identitäten auszuprobieren",
        strength=0.8,
        fun_fact="Der Begriff wurde 1984 von einem Japaner in den USA geprägt",
        wolf_comment="Sich verwandeln... das verstehe ich sehr gut!"
    ),
    KnowledgeConnection(
        node_a="Light Novels",
        node_b="Web Novels",
        connection_type=ConnectionType.ORIGIN,
        description="Viele Light Novels begannen als Web-Romane auf Syosetu",
        strength=0.85,
        fun_fact="Sword Art Online und Re:Zero waren ursprünglich Web Novels",
        wolf_comment="Geschichten finden ihren Weg zu Lesern!"
    ),
    KnowledgeConnection(
        node_a="Doujinshi",
        node_b="Comiket",
        connection_type=ConnectionType.DIRECT,
        description="Comiket ist der größte Doujinshi-Markt der Welt",
        strength=0.95,
        fun_fact="Über 500.000 Besucher kommen zweimal jährlich zum Comiket",
        wolf_comment="Kreativität kennt keine Grenzen!"
    ),

    # ===========================================
    # INTER-ANIME VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Evangelion",
        node_b="Post-Evangelion Anime",
        connection_type=ConnectionType.CAUSAL,
        description="EVA veränderte die gesamte Anime-Industrie nach 1995",
        strength=0.95,
        fun_fact="Gainax definierte 'Gainax Ending' - mehrdeutige Schlüsse",
        wolf_comment="Ein Werk, das alles danach beeinflusste..."
    ),
    KnowledgeConnection(
        node_a="Dragon Ball",
        node_b="Power-Level Trope",
        connection_type=ConnectionType.ORIGIN,
        description="Dragon Ball etablierte das Konzept messbarer Kampfkraft",
        strength=0.9,
        fun_fact="'It's over 9000!' wurde zum globalen Meme",
        wolf_comment="Stärke messen... interessant, aber nicht alles!"
    ),
    KnowledgeConnection(
        node_a="Cowboy Bebop",
        node_b="Jazz-Musik",
        connection_type=ConnectionType.DIRECT,
        description="Cowboy Bebops Soundtrack ist ein Jazz-Meisterwerk",
        strength=0.95,
        fun_fact="Yoko Kanno komponierte alles mit der Band 'The Seatbelts'",
        wolf_comment="*Ohren wippen* Musik, die die Seele berührt!"
    ),
    KnowledgeConnection(
        node_a="Death Note",
        node_b="Moralphilosophie",
        connection_type=ConnectionType.THEMATIC,
        description="Death Note stellt Fragen über Gerechtigkeit und absolute Macht",
        strength=0.9,
        fun_fact="Der Manga wurde in China wegen 'gefährlicher Ideen' verboten",
        wolf_comment="Macht korrumpiert... eine uralte Wahrheit."
    ),
    KnowledgeConnection(
        node_a="Fullmetal Alchemist",
        node_b="Äquivalenter Tausch",
        connection_type=ConnectionType.THEMATIC,
        description="FMA's Philosophie basiert auf Naturgesetzen und Ethik",
        strength=0.9,
        fun_fact="'Äquivalenter Tausch' wird von Fans als Lebensphilosophie zitiert",
        wolf_comment="Nichts kommt umsonst... das wissen auch Händler!"
    ),

    # ===========================================
    # SPRACHE & KOMMUNIKATION VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Honorifics",
        node_b="Soziale Hierarchie",
        connection_type=ConnectionType.DIRECT,
        description="-san, -kun, -chan zeigen Beziehungen und Respekt",
        strength=0.95,
        fun_fact="Falsche Verwendung kann sehr unhöflich sein",
        wolf_comment="Worte tragen versteckte Bedeutung!"
    ),
    KnowledgeConnection(
        node_a="Anime-Deutsch",
        node_b="Localization",
        connection_type=ConnectionType.THEMATIC,
        description="Anime-Übersetzungen müssen kulturelle Nuancen überbrücken",
        strength=0.75,
        fun_fact="Manche Wortspiele sind einfach unübersetzbar",
        wolf_comment="Sprachen sind wie Brücken zwischen Welten!"
    ),
    KnowledgeConnection(
        node_a="Onomatopoeia",
        node_b="Manga-Erzählung",
        connection_type=ConnectionType.DIRECT,
        description="Japanische Lautmalerei ist essentiell für Manga",
        strength=0.9,
        fun_fact="Japan hat über 1000 einzigartige Onomatopoeia",
        wolf_comment="*dokidoki* Das Herz hat seine eigene Sprache!"
    ),
    KnowledgeConnection(
        node_a="Warui Kotoba",
        node_b="Anime-Charakterisierung",
        connection_type=ConnectionType.THEMATIC,
        description="'Böse Wörter' zeigen rebellische oder niedere Charaktere",
        strength=0.7,
        fun_fact="Yankee-Charaktere nutzen spezielle Sprachmuster",
        wolf_comment="Wie man spricht zeigt wer man ist!"
    ),
    KnowledgeConnection(
        node_a="Seiyuu",
        node_b="Idol-Kultur",
        connection_type=ConnectionType.DIRECT,
        description="Anime-Synchronsprecher sind selbst Idole geworden",
        strength=0.85,
        fun_fact="Seiyuu geben Konzerte und haben eigene Fanclubs",
        wolf_comment="Die Stimme wird zur Persönlichkeit!"
    ),

    # ===========================================
    # NATUR & JAHRESZEITEN VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Hanami",
        node_b="Anime-Frühjahrs-Season",
        connection_type=ConnectionType.CULTURAL,
        description="Neue Anime-Staffeln starten passend zu japanischen Jahreszeiten",
        strength=0.7,
        fun_fact="April ist Schuljahresbeginn UND Anime-Season-Start",
        wolf_comment="Natur und Kultur sind im Einklang!"
    ),
    KnowledgeConnection(
        node_a="Onsen",
        node_b="Anime-Fanservice",
        connection_type=ConnectionType.DIRECT,
        description="Heiße Quellen-Episoden sind ein Anime-Klischee",
        strength=0.8,
        fun_fact="Die 'Onsen-Episode' wird von Fans erwartet und parodiert",
        wolf_comment="*errötend* Manche Traditionen sind... offenherzig."
    ),
    KnowledgeConnection(
        node_a="Momiji",
        node_b="Herbst-Melancholie",
        connection_type=ConnectionType.CULTURAL,
        description="Ahornblätter symbolisieren Vergänglichkeit und Nostalgie",
        strength=0.85,
        fun_fact="Herbst-Anime haben oft melancholische Themen",
        wolf_comment="*seufzt* Die fallenden Blätter erinnern an vergangene Zeiten..."
    ),
    KnowledgeConnection(
        node_a="Yuki",
        node_b="Reinheit im Anime",
        connection_type=ConnectionType.ANALOGY,
        description="Schnee symbolisiert Neuanfang und Reinheit",
        strength=0.8,
        fun_fact="Romantische Geständnisse im Schnee sind ein Trope",
        wolf_comment="Schneestille... perfekt für wichtige Momente."
    ),
    KnowledgeConnection(
        node_a="Tanabata",
        node_b="Anime-Romantik",
        connection_type=ConnectionType.CULTURAL,
        description="Das Sternenfest inspiriert romantische Anime-Szenen",
        strength=0.85,
        fun_fact="Orihime und Hikoboshi treffen sich nur einmal im Jahr",
        wolf_comment="Getrennte Liebende... eine tragisch-schöne Geschichte."
    ),

    # ===========================================
    # MODERNE TECHNOLOGIE VERBINDUNGEN
    # ===========================================

    KnowledgeConnection(
        node_a="Streaming",
        node_b="Anime-Globalisierung",
        connection_type=ConnectionType.CAUSAL,
        description="Crunchyroll und Netflix machten Anime weltweit zugänglich",
        strength=0.9,
        fun_fact="Simulcasts erscheinen heute zeitgleich weltweit",
        wolf_comment="Die Welt wächst zusammen durch Geschichten!"
    ),
    KnowledgeConnection(
        node_a="Social Media",
        node_b="Anime-Meme-Kultur",
        connection_type=ConnectionType.CAUSAL,
        description="Twitter und Reddit verbreiten Anime-Memes viral",
        strength=0.85,
        fun_fact="'Omae wa mou shindeiru' ist ein universelles Meme",
        wolf_comment="Humor verbindet Menschen überall!"
    ),
    KnowledgeConnection(
        node_a="Gacha Games",
        node_b="Anime-Marketing",
        connection_type=ConnectionType.DIRECT,
        description="Mobile Gacha-Spiele sind eine Haupteinnahmequelle für Anime",
        strength=0.8,
        fun_fact="Fate/Grand Order verdiente über 4 Milliarden Dollar",
        wolf_comment="Glücksspiel mit Charakteren... gefährlich faszinierend!"
    ),
    KnowledgeConnection(
        node_a="AI-Generierte Kunst",
        node_b="Anime-Stil",
        connection_type=ConnectionType.DIRECT,
        description="KI kann überzeugenden Anime-Stil erzeugen",
        strength=0.75,
        fun_fact="NovelAI und andere KIs wurden mit Anime trainiert",
        wolf_comment="Maschinen lernen zu malen... erstaunlich!"
    ),
    KnowledgeConnection(
        node_a="VTuber",
        node_b="Parasoziale Beziehungen",
        connection_type=ConnectionType.THEMATIC,
        description="VTuber fördern intensive Fan-Bindungen durch Interaktion",
        strength=0.8,
        fun_fact="Top VTuber verdienen Millionen durch Superchats",
        wolf_comment="Virtuelle Freundschaften können echt fühlen..."
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
